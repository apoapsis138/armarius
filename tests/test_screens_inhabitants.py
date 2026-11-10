"""The covenant's Inhabitants tab."""

import re

from screen_helpers import (
    _cov_view,
    _fill,
    _inh_labels,
    _open_inh_section,
    _plain_title,
    _saga_with_people,
    _save_dialog,
    _select_covenant,
    _show_inhabitants_tab,
    _wait_for_screen,
    _wait_until_active,
)
from support import choose, menu, strip_markup, wait_until
from textual.widgets import Button, Collapsible, Input, Select, Static

from ars_magica_manager import inhabitants as inh
from ars_magica_manager import storage
from ars_magica_manager.models import Inhabitant, VirtueFlawInstance
from ars_magica_manager.rules import covenfolk
from ars_magica_manager.rules.xp import ability_xp
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import (
    ConfirmScreen,
    FieldsDialog,
    RemovalPickerScreen,
    SelectableList,
    WorkspaceScreen,
)
from ars_magica_manager.tui.screens.steps import ChooseScreen


async def _select_inh_row(pilot, app, kind: str, row: int) -> None:
    await _show_inhabitants_tab(pilot, app)
    view = app.screen._covenant_sheet_view
    rows = view.query_one(f"#inh-{kind}-list", SelectableList)
    rows.focus()
    await pilot.pause()
    rows.highlighted = row
    await wait_until(pilot, lambda: app.focused is rows and rows.highlighted == row)
    await _wait_until_active(pilot, app, f"section-inh-{kind}")
    await pilot.pause()  # the panel follows the highlighted row


def _records(kind: str | None = None) -> list[Inhabitant]:
    cov = storage.load_saga("test_saga").covenants[0]
    return [r for r in cov.inhabitants if kind is None or r.kind == kind]


def _inh_title(app, kind: str) -> str:
    return _plain_title(_cov_view(app).query_one(f"#section-inh-{kind}", Collapsible))


async def test_inhabitants_tab_has_all_its_sections_with_headcount_titles():
    saga = _saga_with_people()
    cov = saga.covenants[0]
    cov.boons_hooks = [VirtueFlawInstance(vf_id="covbh_boon_free_autocracy")]
    cov.inhabitants = [
        Inhabitant(id="t1", kind="turb", name="Guard", quantity=3),
        Inhabitant(id="i1", kind="inhabitant", name="Marta and Simon", quantity=2),
        Inhabitant(id="i2", kind="inhabitant", name="Jakob"),
    ]
    cov.population.other_people = 4
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _show_inhabitants_tab(pilot, app)
        view = _cov_view(app)

        ids = [
            "section-inh-loyalty",
            "section-inh-population",
            "section-inh-misc",
            *(f"section-inh-{k}" for k in inh.INHABITANT_KINDS),
        ]
        sections = [view.query_one(f"#{i}", Collapsible) for i in ids]
        assert all(not section.collapsed for section in sections)
        assert [_plain_title(x) for x in sections[:3]] == [
            "Loyalty",
            "Inhabitants",
            "Miscellaneous",
        ]
        # Titles carry the headcount: quantities added up, not rows.
        assert [_plain_title(x) for x in sections[3:]] == [
            "Magi (1)",
            "Companions (1)",
            "Specialists (0)",
            "Craftspeople (0)",
            "Turb (3)",
            "Other Covenfolk (3)",
            "Horses (0)",
            "Hounds (0)",
            "Livestock (0)",
        ]
        text = str(view.query_one("#inh-population-content", Static).render())
        assert re.search(r"Total Inhabitants:\s+12\b", text)  # 4+1+1+3+3
        left = str(view.query_one("#inh-loyalty-left", Static).render())
        assert "Autocracy" in left  # the governance follows the Boon
        assert "Select an inhabitant" in str(
            view.query_one("#inh-panel", Static).render()
        )


async def test_magi_and_companions_are_listed_from_sheets_and_choosing_fills_the_panel():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        assert _inh_labels(app, "magus") == [
            "Corvinus            Bonisagus             1195  The Gift"
        ]
        assert _inh_labels(app, "companion") == [
            "Alys                                                   Unknown"
        ]

        await _select_inh_row(pilot, app, "magus", 0)
        panel = _cov_view(app).query_one("#inh-panel", Static)
        text = str(panel.render())
        assert "House: Bonisagus" in text and "Year Born: 1195 (age 25)" in text
        assert "From the character sheet of Corvinus." in text

        # One selection across all the lists.
        await _select_inh_row(pilot, app, "companion", 0)
        assert _cov_view(app).selected_inhabitant("magus") is None
        assert "Name: Alys" in str(panel.render())


async def test_editing_a_listed_magus_only_changes_covenant_side_fields():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_inh_row(pilot, app, "magus", 0)
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        # Name/house/year come from the sheet: shown, not editable.
        assert not app.screen.query("#fld-name")
        assert not app.screen.query("#fld-house")
        # Gift too: read straight from the sheet's Virtues, not editable here.
        assert not app.screen.query("#fld-gift")
        _fill(app, description="Trusted **completely**.")
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        assert _inh_labels(app, "magus")[0].startswith("Corvinus            Bonisagus")

    [record] = _records("magus")
    assert record.character_id == "mag1" and record.description.startswith("Trusted")
    assert not record.departed


async def test_removing_a_listed_magus_keeps_them_in_the_covenant_but_stops_counting_them():
    saga = _saga_with_people()
    # Already edited once, so a covenant-side record exists to be marked.
    saga.covenants[0].inhabitants = [
        Inhabitant(id="m", kind="magus", character_id="mag1", description="Trusted.")
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_inh_row(pilot, app, "magus", 0)
        await pilot.press("d")
        await _wait_for_screen(pilot, app, ConfirmScreen)
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert "Remove Corvinus from the Magi list?" in message
        assert "stay in the covenant on their character sheet" in message
        await pilot.press("n")
        await pilot.pause()
        assert len(_inh_labels(app, "magus")) == 1  # No keeps them

        await pilot.press("d")
        await _wait_for_screen(pilot, app, ConfirmScreen)
        await pilot.press("y")
        await wait_until(pilot, lambda: not _inh_labels(app, "magus"))
        assert _inh_title(app, "magus") == "Magi (0)"
        text = str(_cov_view(app).query_one("#inh-population-content", Static).render())
        assert re.search(r"Total Inhabitants:\s+1\b", text)  # only Alys now

    saved = storage.load_saga("test_saga")
    assert next(c for c in saved.characters if c.id == "mag1").covenant_id == "cov1"
    [record] = _records("magus")
    assert record.departed
    assert record.description == "Trusted." and record.character_id == "mag1"
    assert covenfolk.entries_for_kind(saved, saved.covenants[0], "magus") == []


async def test_removing_a_listed_companion_with_no_record_creates_one():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_inh_row(pilot, app, "companion", 0)
        await pilot.press("d")
        await _wait_for_screen(pilot, app, ConfirmScreen)
        await pilot.press("y")
        await wait_until(pilot, lambda: not _inh_labels(app, "companion"))
        assert _inh_title(app, "companion") == "Companions (0)"
        # The magus is untouched.
        assert len(_inh_labels(app, "magus")) == 1

    [record] = _records("companion")
    assert record.departed and record.character_id == "comp1"


async def test_restoring_a_departed_magus_makes_them_count_again():
    saga = _saga_with_people()
    saga.covenants[0].inhabitants = [
        Inhabitant(
            id="m",
            kind="magus",
            character_id="mag1",
            description="Trusted.",
            departed=True,
        )
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        assert _inh_labels(app, "magus") == []  # departed: not listed
        await _open_inh_section(pilot, app, "section-inh-magus")
        workspace = app.screen
        await menu(pilot, app, "m", "Restore")
        # The departed aren't rows of the list: it asks which one.
        assert isinstance(app.screen, RemovalPickerScreen)  # only one entry
        await pilot.press("enter")
        await wait_until(pilot, lambda: app.screen is workspace)
        await wait_until(pilot, lambda: len(_inh_labels(app, "magus")) == 1)
        assert _inh_labels(app, "magus")[0].startswith("Corvinus")

    [record] = _records("magus")
    assert not record.departed
    assert record.description == "Trusted."  # covenant-side extras kept


def _offered_people(app) -> list[str]:
    """The labels the Add chooser lists, markup removed."""
    return [strip_markup(c.label) for c in app.screen._all()]


async def test_specialist_from_an_unassigned_grog_prefills_and_marks_it_assigned():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-specialist")

        await pilot.press("a")
        await _wait_for_screen(pilot, app, ChooseScreen)
        labels = _offered_people(app)
        # New person first, then only THIS covenant's unassigned grogs.
        assert labels[0].startswith("(New person")
        assert [l.split("  ")[0] for l in labels[1:]] == ["Old Thomae", "Dieter"]

        await choose(pilot, app, "Old Thomae")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        assert app.screen.query_one("#fld-name", Input).value == "Old Thomae"
        assert app.screen.query_one("#fld-year_born", Input).value == "1193"
        _fill(app, responsibility="Teaches Latin", role="Teacher")
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(_inh_labels(app, "specialist")) == 1)
        assert _inh_labels(app, "specialist") == [
            "Old Thomae          Teaches Latin     Teacher             1193"
        ]

        # Now assigned, so he's no longer offered.
        await pilot.press("a")
        await _wait_for_screen(pilot, app, ChooseScreen)
        labels = _offered_people(app)
        assert [l.split("  ")[0] for l in labels[1:]] == ["Dieter"]

    [record] = _records("specialist")
    assert (record.character_id, record.role) == ("grog1", "Teacher")


async def test_a_brand_new_grog_type_person_needs_a_name_but_year_born_may_stay_unknown():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-specialist")
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("enter")  # "(New person...)"
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)

        await _save_dialog(pilot, app)
        assert isinstance(app.screen, FieldsDialog)  # refused: no name
        assert "Name is required" in str(app.screen.query_one("#fields-error").render())
        _fill(app, name="Visiting Steward", role="Steward")
        await _save_dialog(pilot, app)  # no year: fine
        await wait_until(pilot, lambda: len(_inh_labels(app, "specialist")) == 1)
        assert _inh_labels(app, "specialist") == [
            "Visiting Steward                      Steward          Unknown"
        ]

    [record] = _records("specialist")
    assert record.character_id is None and record.year_born is None


async def test_a_grog_without_a_year_born_is_assigned_with_it_unknown():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-turb")
        await pilot.press("a")
        await choose(pilot, app, "Dieter")  # no year on his sheet
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert app.screen.query_one("#fld-name", Input).value == "Dieter"
        assert app.screen.query_one("#fld-year_born", Input).value == ""
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(_inh_labels(app, "turb")) == 1)
        assert _inh_labels(app, "turb")[0].endswith("Unknown")


async def test_other_covenfolk_requires_a_covenant_role_and_suppresses_it_when_redundant():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-inhabitant")
        await pilot.press("a")
        await _wait_for_screen(pilot, app, ChooseScreen)  # a GROG_KINDS section
        await choose(pilot, app, "(New person")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)

        _fill(app, name="Old Marta", responsibility="Nursemaid")
        await _save_dialog(pilot, app)
        assert isinstance(app.screen, FieldsDialog)  # refused: no Covenant Role
        assert "Covenant Role is required" in str(
            app.screen.query_one("#fields-error").render()
        )
        options = [
            v
            for _, v in app.screen.query_one("#fld-role", Select)._options
            if isinstance(v, str)
        ]
        assert options == ["Laborer", "Servant", "Teamster", "Dependent"]
        _fill(app, role="Dependent", year_born=1180)
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(_inh_labels(app, "inhabitant")) == 1)
        assert _inh_labels(app, "inhabitant") == [
            "Old Marta           Dependent         1        1180"
        ]

        await _select_inh_row(pilot, app, "inhabitant", 0)
        panel = _cov_view(app).query_one("#inh-panel", Static)
        text = str(panel.render())
        assert "Covenant Role: Dependent" in text
        assert "Responsibility: Nursemaid" in text

    [record] = _records("inhabitant")
    assert (record.name, record.role, record.year_born) == (
        "Old Marta",
        "Dependent",
        1180,
    )


async def test_craftsperson_links_one_of_the_grogs_abilities_and_stores_craft_fields():
    saga = _saga_with_people()
    saga.characters[2].abilities[1].xp = ability_xp(4)  # Old Thomae's Brawl
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-craftsperson")
        await pilot.press("a")
        await choose(pilot, app, "Old Thomae")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)

        ability = app.screen.query_one("#fld-linked_ability", Select)
        assert isinstance(ability, Select)  # a dropdown of the grog's Abilities
        assert [value for _, value in ability._options if isinstance(value, str)] == [
            "Athletics",
            "Brawl",
        ]
        assert app.screen.query_one("#fld-field_of_work", Select).value == "None"
        _fill(
            app,
            responsibility="Blacksmithing",
            skill_value=7,
            field_of_work="Books",
            rare=True,
            linked_ability="Brawl",
        )
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(_inh_labels(app, "craftsperson")) == 1)
        # Tied to the sheet's Brawl (Level 4): that wins over the typed 7.
        assert _inh_labels(app, "craftsperson") == [
            "Old Thomae          Blacksmithing           4    1        1193"
        ]

        # Editing again shows the score as read-only, taken from the Ability.
        await _select_inh_row(pilot, app, "craftsperson", 0)
        await pilot.press("e")
        await pilot.pause()
        assert not app.screen.query("#fld-skill_value")
        info = " ".join(
            str(s.render()) for s in app.screen.query(".fd-value").results(Static)
        )
        assert "4 (Level of Brawl)" in info
        await pilot.press("escape")

    [record] = _records("craftsperson")
    assert (record.field_of_work, record.rare, record.linked_ability) == (
        "Books",
        True,
        "Brawl",
    )
    # The typed number is kept as the fallback if the link is ever cleared.
    assert (record.skill_value, record.character_id) == (7, "grog1")


async def test_forms_and_the_remove_confirmation_fit_an_80_by_24_terminal():
    saga = _saga_with_people()
    saga.characters[2].abilities[1].xp = ability_xp(4)
    saga.covenants[0].inhabitants = [
        Inhabitant(
            id="c",
            kind="craftsperson",
            name="Old Thomae",
            character_id="grog1",
            linked_ability="Brawl",
        )
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await _select_covenant(pilot, app)
        await _select_inh_row(pilot, app, "craftsperson", 0)
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        region = app.screen.query_one("#fields-dialog").region
        assert region.right <= 120 and region.bottom <= 45  # right border on screen
        await pilot.press("escape")
        await pilot.pause()

        await _select_inh_row(pilot, app, "magus", 0)
        await pilot.press("d")
        await pilot.pause()
        region = app.screen.query_one("#confirm-dialog").region
        assert region.right <= 120 and region.bottom <= 45


async def test_craftsperson_score_is_typed_when_there_is_no_sheet_ability():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-craftsperson")
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("enter")  # (New person): no sheet at all
        await pilot.pause()
        _fill(app, name="Travelling Smith", responsibility="Smith", skill_value=6)
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(_inh_labels(app, "craftsperson")) == 1)
        assert _inh_labels(app, "craftsperson")[0] == (
            "Travelling Smith    Smith                   6    1     Unknown"
        )

        await _select_inh_row(pilot, app, "craftsperson", 0)
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert app.screen.query_one("#fld-skill_value", Input).value == "6"  # editable


async def test_quantity_drives_the_headcounts_and_must_be_at_least_one():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-turb")
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("enter")  # new person
        await pilot.pause()
        _fill(
            app, name="Guards", year_born=1200, responsibility="Gatehouse", quantity=0
        )
        await _save_dialog(pilot, app)
        assert isinstance(app.screen, FieldsDialog)  # quantity 0 refused
        assert "at least 1" in str(app.screen.query_one("#fields-error").render())
        _fill(app, quantity=3)
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: _inh_title(app, "turb") == "Turb (3)")

        text = str(_cov_view(app).query_one("#inh-population-content", Static).render())
        assert re.search(r"Total Inhabitants:\s+5\b", text)  # magus + companion + 3


async def test_horses_and_livestock_take_a_blank_year_and_a_quantity():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        # Qty, Size, Carnivore (blank), Points, Year Arrived.
        for kind, name, size, shown in (
            ("horse", "Grey Mare", 3, ["4", "+3", "4", "Unknown"]),
            ("livestock", "Sheep", 0, ["4", "+0", "1/2", "Unknown"]),
        ):
            await _open_inh_section(pilot, app, f"section-inh-{kind}")
            await pilot.press("a")
            await _wait_for_screen(pilot, app, FieldsDialog)
            assert isinstance(app.screen, FieldsDialog)  # no picker for animals
            _fill(app, name=name, size=size, quantity=4)
            await _save_dialog(pilot, app)
            await wait_until(pilot, lambda kind=kind: len(_inh_labels(app, kind)) == 1)
            [label] = _inh_labels(app, kind)
            assert label.startswith(name)
            assert label[len(name) :].split() == shown
        assert _inh_title(app, "horse") == "Horses (4)"


async def test_deleting_an_assigned_grog_returns_it_to_the_available_list():
    saga = _saga_with_people()
    saga.covenants[0].inhabitants = [
        Inhabitant(id="a", kind="specialist", name="Old Thomae", character_id="grog1")
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_inh_row(pilot, app, "specialist", 0)
        await pilot.press("d")
        await _wait_for_screen(pilot, app, ConfirmScreen)
        await pilot.press("y")
        await wait_until(pilot, lambda: not _inh_labels(app, "specialist"))
        cov = app.screen.selected_covenant
        assert "Old Thomae" in [
            g.name for g in inh.available_grogs(app.screen.saga, cov)
        ]


async def test_loyalty_governance_is_typed_unless_a_governance_boon_provides_it():
    saga = _saga_with_people()
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-loyalty")
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        assert app.screen.query_one("#fld-equipment", Select).value == "Standard"
        assert app.screen.query_one("#fld-money", Select).value == "Standard salary"
        # The four totals are calculated, not typed.
        for key in ("base_points", "current_points", "prevailing_score"):
            assert not app.screen.query(f"#fld-{key}")
        _fill(
            app,
            governance="Guild of Mercers",
            equipment="Anything they need",
            money="Lavish salary",
            familiarity=1,
        )
        await _save_dialog(pilot, app)
        await wait_until(
            pilot,
            lambda: (
                "Guild of Mercers"
                in str(_cov_view(app).query_one("#inh-loyalty-left", Static).render())
            ),
        )
        left = str(_cov_view(app).query_one("#inh-loyalty-left", Static).render())
        right = str(_cov_view(app).query_one("#inh-loyalty-right", Static).render())
        assert "Guild of Mercers" in left
        # 1 magus, The Gift (-30); +20 Equipment, +20 Money, +1 Familiarity -> 11.
        assert re.search(r"Base Loyalty Points:\s+-30", left)
        assert re.search(r"Total modifiers:\s+41", left)
        assert re.search(r"Current Loyalty Points:\s+11", left)
        assert re.search(r"Prevailing Loyalty Score:\s+1\b", left)
        assert "Anything they need  (+20)" in right and "Lavish salary  (+20)" in right

    loyalty = storage.load_saga("test_saga").covenants[0].loyalty
    assert loyalty.governance == "Guild of Mercers"
    assert (loyalty.equipment, loyalty.money) == ("Anything they need", "Lavish salary")

    # With a governance Boon the type isn't typed in: the field becomes info.
    saga = storage.load_saga("test_saga")
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_free_council")
    ]
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-loyalty")
        await pilot.press("e")
        await pilot.pause()
        assert not app.screen.query("#fld-governance")
        await pilot.press("escape")
        await pilot.pause()
        left = str(_cov_view(app).query_one("#inh-loyalty-left", Static).render())
        assert "Council" in left and "Guild of Mercers" not in left


async def test_population_and_miscellaneous_fields_are_editable_and_total_is_calculated():
    saga = _saga_with_people()
    saga.covenants[0].inhabitants = [
        Inhabitant(
            id="s", kind="inhabitant", name="Servants", role="Servant", quantity=3
        )
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        view = _cov_view(app)

        await _open_inh_section(pilot, app, "section-inh-population")
        await pilot.press("e")
        await pilot.pause()
        assert not app.screen.query("#fld-total")  # calculated: not an input
        # Teamsters/Servants/Laborers and their two "Needed" minimums are all
        # calculated now, from the Other Covenfolk list -- nothing to type.
        for key in ("teamsters", "teamsters_needed", "servants", "servants_needed"):
            assert not app.screen.query(f"#fld-{key}")
        assert not app.screen.query("#fld-laborers")
        _fill(app, other_people=6)
        await _save_dialog(pilot, app)
        await wait_until(
            pilot,
            lambda: re.search(
                r"Total Inhabitants:\s+11\b",
                str(view.query_one("#inh-population-content", Static).render()),
            ),
        )
        text = str(view.query_one("#inh-population-content", Static).render())
        minimum = covenfolk.minimum_servants(view.saga, view.covenant)
        assert f"3 / {minimum}" in text  # 3 servants already on the list
        assert re.search(
            r"Total Inhabitants:\s+11\b", text
        )  # 6 other + magus + companion + 3 servants

        await _open_inh_section(pilot, app, "section-inh-misc")
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        _fill(app, aging_magi=1, magic_laborers=2, magic_turbula=5)
        await _save_dialog(pilot, app)
        await wait_until(
            pilot,
            lambda: "5" in str(view.query_one("#inh-misc-right", Static).render()),
        )

    pop = storage.load_saga("test_saga").covenants[0].population
    assert pop.other_people == 6
    assert (pop.aging_magi, pop.magic_laborers, pop.magic_turbula) == (1, 2, 5)


async def test_inhabitant_dialogs_fit_a_small_terminal_and_hug_content_on_a_tall_one():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await _select_covenant(pilot, app)
        # The busiest form: a craftsperson (many fields + a description).
        await _open_inh_section(pilot, app, "section-inh-craftsperson")
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("down")
        await pilot.press("enter")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        for button in app.screen.query(Button):
            assert button.region.height > 0 and button.region.bottom <= 45, button.id
        await pilot.press("escape")
        await pilot.pause()

        # ...and the biggest summary form: Loyalty.
        await _open_inh_section(pilot, app, "section-inh-loyalty")
        await pilot.press("e")
        await pilot.pause()
        for button in app.screen.query(Button):
            assert button.region.height > 0 and button.region.bottom <= 45, button.id

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-horse")
        await pilot.press("a")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        # well short of the 70 rows (its title is ruled)
        assert app.screen.query_one("#fields-dialog").region.height < 34
