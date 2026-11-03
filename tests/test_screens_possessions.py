"""The covenant's Possessions tab."""

from screen_helpers import (
    _fill,
    _focus_section,
    _plain_title,
    _saga_with_bare_laboratory,
    _save_dialog,
    _select_covenant,
    _show_tab,
    _wait_for_screen,
    _wait_until_active,
)
from support import wait_until
from textual.widgets import Button, Collapsible, Input, Select, Static

from ars_magica_manager import possessions as pos
from ars_magica_manager import storage
from ars_magica_manager.models import Possession
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import (
    ConfirmScreen,
    FieldsDialog,
    SelectableList,
    WorkspaceScreen,
)


async def _show_possessions_tab(pilot, app) -> None:
    await _show_tab(pilot, app, "tab-cov-possessions")


async def _open_pos_section(pilot, app, kind: str) -> None:
    """Focus a Possessions section (so its a / e / d keys apply)."""
    await _show_possessions_tab(pilot, app)
    view = app.screen._covenant_sheet_view
    section_id = f"section-pos-{kind}"
    collapsible = view.query_one(f"#{section_id}", Collapsible)
    await _focus_section(pilot, app, collapsible, section_id)


async def _select_pos_row(pilot, app, kind: str, row: int) -> None:
    await _show_possessions_tab(pilot, app)
    rows = app.screen._covenant_sheet_view.query_one(
        f"#pos-{kind}-list", SelectableList
    )
    rows.focus()
    await pilot.pause()
    rows.highlighted = row
    await wait_until(pilot, lambda: app.focused is rows and rows.highlighted == row)
    await _wait_until_active(pilot, app, f"section-pos-{kind}")
    await pilot.pause()  # the panel follows the highlighted row


def _pos_labels(app, kind: str) -> list[str]:
    return [label for _, label in app.screen._covenant_sheet_view._pos_rows(kind)]


def _pos_records(kind: str | None = None) -> list[Possession]:
    cov = storage.load_saga("test_saga").covenants[0]
    return [r for r in cov.possessions if kind is None or r.kind == kind]


def _pos_panel(app) -> str:
    return str(app.screen._covenant_sheet_view.query_one("#pos-panel", Static).render())


async def test_possessions_tab_has_its_eight_sections_and_lists_the_labs_as_sanctums():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _show_possessions_tab(pilot, app)
        view = app.screen._covenant_sheet_view
        sections = [
            view.query_one(f"#section-pos-{kind}", Collapsible)
            for kind in pos.KIND_TITLES
        ]
        assert [_plain_title(x) for x in sections] == [
            "Ships (0)",
            "Properties and Land (0)",
            "Sanctums (1)",
            "Weapons (0)",
            "Armor (0)",
            "Vis Sources (0)",
            "Raw Vis Stores (0)",
            "Items (0)",
        ]
        assert all(not section.collapsed for section in sections)
        # The laboratory is a sanctum without anyone adding it, Quality/Upkeep
        # read live from its Lab Characteristics.
        assert _pos_labels(app, "sanctum") == [
            "Test Lab            Leandro               0       0"
        ]
        assert "Select a possession" in _pos_panel(app)


async def test_a_laboratory_sanctum_edits_only_covenant_side_fields_and_cannot_be_deleted():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_pos_row(pilot, app, "sanctum", 0)
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        for key in ("name", "owner", "location", "build_points", "quality", "upkeep"):
            assert not app.screen.query(f"#fld-{key}"), key  # from the laboratory
        assert (
            app.screen.query_one("#fld-usage", Select).value == "Standard (2 Seasons)"
        )  # the default
        _fill(
            app,
            usage="Heavy (3+ Seasons)",
            description="Busy *all* year.",
        )
        await _save_dialog(pilot, app)
        assert _pos_labels(app, "sanctum") == [
            "Test Lab            Leandro               0       0"
        ]

        await _select_pos_row(pilot, app, "sanctum", 0)
        panel = _pos_panel(app)
        for expected in (
            "Usage: Heavy (3+ Seasons)",
            "Build Points: 0",
            "Busy all year.",
        ):
            assert expected in panel, expected

        # A laboratory of the covenant can't be deleted from here.
        await pilot.press("d")
        await _wait_for_screen(pilot, app, WorkspaceScreen)
        assert isinstance(app.screen, WorkspaceScreen)  # no confirmation
        assert len(_pos_labels(app, "sanctum")) == 1

    [record] = _pos_records("sanctum")
    assert record.lab_id == "lab1" and record.usage == "Heavy (3+ Seasons)"


async def test_manual_sanctums_have_every_field_and_can_be_deleted():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_pos_section(pilot, app, "sanctum")
        await pilot.press("a")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert (
            app.screen.query_one("#fld-usage", Select).value == "Standard (2 Seasons)"
        )
        # Nobody owns it yet: free for visitors to use (the Usage says how hard).
        assert app.screen.query_one("#fld-owner", Input).value == "Free"
        _fill(
            app,
            name="Hidden Study",
            owner="Corvinus",
            location="Under the stairs",
            quality=2,
            upkeep=5,
            build_points=15,
        )
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(_pos_labels(app, "sanctum")) == 2)
        assert _pos_labels(app, "sanctum")[1] == (
            "Hidden Study        Corvinus              2       5"
        )
        await _select_pos_row(pilot, app, "sanctum", 1)
        assert "Build Points: 15" in _pos_panel(app)

        await pilot.press("d")
        await _wait_for_screen(pilot, app, ConfirmScreen)
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await wait_until(pilot, lambda: len(_pos_labels(app, "sanctum")) == 1)

    assert _pos_records("sanctum") == []


async def test_weapons_armor_and_items_need_a_name_and_a_quantity_defaulting_to_one():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        for kind, name in (
            ("weapon", "Crossbows"),
            ("armor", "Mail Hauberks"),
            ("item", "The Weeping Lens"),
        ):
            await _open_pos_section(pilot, app, kind)
            await pilot.press("a")
            await _wait_for_screen(pilot, app, FieldsDialog)
            assert app.screen.query_one("#fld-quantity", Input).value == "1"  # default
            await _save_dialog(pilot, app)
            assert "Name is required" in str(
                app.screen.query_one("#fields-error").render()
            )
            _fill(app, name=name, quantity=0)
            await _save_dialog(pilot, app)
            assert "at least 1" in str(app.screen.query_one("#fields-error").render())
            _fill(app, quantity=3, description="Well **kept**.")
            await _save_dialog(pilot, app)
            await wait_until(pilot, lambda kind=kind: len(_pos_labels(app, kind)) == 1)
            # Weapons and armor carry a Type and Quality (their points); items don't.
            expected = {
                # Weapons get four extra trailing combat-figure columns
                # (Init/Attack/Defense/Damage), defaulting to +0,
                # and Load; armor its Protection and Load;
                # items neither.
                "weapon": (
                    "Crossbows           Weapon or shield    Standard"
                    "        3   +0   +0   +0   +0    0"
                ),
                "armor": (
                    "Mail Hauberks       Partial armor       Standard        3   +0    0"
                ),
                "item": "The Weeping Lens        3",
            }[kind]
            assert _pos_labels(app, kind) == [expected]

        await _select_pos_row(pilot, app, "item", 0)
        panel = _pos_panel(app)
        assert "Quantity: 3" in panel and "Well kept." in panel
        assert "Points" not in panel

        await _select_pos_row(pilot, app, "weapon", 0)
        panel = _pos_panel(app)
        for expected in (
            "Type: Weapon or shield",
            "Quality: Standard",
            "Quantity: 3",
            "Points: 12 (4 each",
            "Init: +0",
            "Attack: +0",
            "Defense: +0",
            "Damage: +0",
            "Load: 0",
        ):
            assert expected in panel, expected


async def test_weapon_combat_figures_are_typed_in_and_shown_on_the_row_and_panel():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_pos_section(pilot, app, "weapon")
        await pilot.press("a")
        await pilot.pause()
        _fill(
            app,
            name="Longsword",
            weapon_init=2,
            weapon_attack=5,
            weapon_defense=3,
            weapon_damage=7,
        )
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(_pos_labels(app, "weapon")) == 1)

        assert _pos_labels(app, "weapon")[0].endswith("   +2   +5   +3   +7    0")

        await _select_pos_row(pilot, app, "weapon", 0)
        panel = _pos_panel(app)
        for expected in ("Init: +2", "Attack: +5", "Defense: +3", "Damage: +7"):
            assert expected in panel, expected
        # Typed in, not chosen from the book.
        assert "Weapon:" not in panel

        # Armor doesn't get these fields at all.
        await _open_pos_section(pilot, app, "armor")
        await pilot.press("a")
        await pilot.pause()
        assert not app.screen.query("#fld-weapon_init")

    [record] = _pos_records("weapon")
    assert (
        record.weapon_init,
        record.weapon_attack,
        record.weapon_defense,
        record.weapon_damage,
    ) == (2, 5, 3, 7)


async def test_one_selection_across_the_possession_lists():
    saga = _saga_with_bare_laboratory()
    saga.covenants[0].possessions = [
        Possession(id="a", kind="weapon", name="Crossbows"),
        Possession(id="b", kind="armor", name="Mail"),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_pos_row(pilot, app, "weapon", 0)
        assert "Name: Crossbows" in _pos_panel(app)
        await _select_pos_row(pilot, app, "armor", 0)
        view = app.screen._covenant_sheet_view
        assert view.selected_possession("weapon") is None  # the other list let go
        assert "Name: Mail" in _pos_panel(app)


async def test_possession_forms_fit_a_small_terminal_and_hug_content_on_a_tall_one():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await _select_covenant(pilot, app)
        await _open_pos_section(pilot, app, "vis_source")  # the busiest form
        await pilot.press("a")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        for button in app.screen.query(Button):
            assert button.region.height > 0 and button.region.bottom <= 45, button.id

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_pos_section(pilot, app, "weapon")
        await pilot.press("a")
        await pilot.pause()
        # The weapon form: its fields, Description, the book line and buttons
        # -- not the whole 70 rows.
        # (Made and Carried took it from 34 rows to 38.)
        assert app.screen.query_one("#fields-dialog").region.height < 40
