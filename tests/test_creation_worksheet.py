"""The Creation Worksheet: opened from the sheet while In
Creation, one row per step with its mark, free movement between steps, a
step's buttons, and Move to In Play."""

from __future__ import annotations

import pytest
from support import screen_lines, strip_markup, wait_until
from textual.widgets import Button, OptionList, Select, Static, Tree

from ars_magica_manager import storage
from ars_magica_manager import worksheet as ws
from ars_magica_manager.commands import Act
from ars_magica_manager.models import (
    Character,
    Covenant,
    Laboratory,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import creation as rules
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import (
    ConfirmScreen,
    SelectableList,
    WorkspaceScreen,
)
from ars_magica_manager.tui.screens.creation_worksheet import CreationWorksheetScreen
from ars_magica_manager.tui.screens.steps import ChooseScreen


def _saga(character_type: str = "magus") -> Saga:
    return Saga(
        id="test_saga",
        name="Saga",
        covenants=[Covenant(id="cov1", saga_id="test_saga", name="Keep")],
        characters=[
            Character(
                id="c1",
                name="Leandro",
                type=character_type,  # type: ignore[arg-type]
                covenant_id="cov1",
                in_creation=True,
            )
        ],
        laboratories=[Laboratory(id="lab1", covenant_id="cov1", name="Tower")],
    )


@pytest.fixture
def concept_checks(monkeypatch):
    """Concept: one passing check and one broken must; Characteristics:
    advice only."""

    def concept(saga, record):
        return [
            rules.Check("concept", "Has a name", "pass", record.name, "test"),
            rules.Check("concept", "Has a House", "warn", "none", "test"),
        ]

    def characteristics(saga, record):
        return [rules.Check("characteristics", "Balanced", "advice", "1 over", "t")]

    for step in rules.CHARACTER_CHECKS:
        monkeypatch.setitem(rules.CHARACTER_CHECKS, step, [])
    monkeypatch.setitem(rules.CHARACTER_CHECKS, "concept", [concept])
    monkeypatch.setitem(rules.CHARACTER_CHECKS, "characteristics", [characteristics])


async def _open_worksheet(pilot, app) -> CreationWorksheetScreen:
    await pilot.press("enter")
    assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
    workspace = app.screen
    tree = workspace.query_one("#nav-tree", Tree)

    def node():
        stack = [tree.root]
        while stack:
            n = stack.pop()
            if n.data is not None and n.data[1:] == ("c1",):
                return n
            stack.extend(n.children)
        return None

    assert await wait_until(pilot, lambda: node() is not None)
    tree.select_node(node())
    assert await wait_until(pilot, lambda: workspace._character_sheet_view is not None)
    button = workspace.query_one("#btn-worksheet", Button)
    assert button.display
    button.press()
    assert await wait_until(
        pilot, lambda: isinstance(app.screen, CreationWorksheetScreen)
    )
    await pilot.pause()
    return app.screen


def _text(screen, selector: str) -> str:
    return str(screen.query_one(selector, Static).render())


def _steps(screen) -> list[str]:
    options = screen.query_one("#ws-steps", OptionList)
    return [
        strip_markup(str(options.get_option_at_index(i).prompt))
        for i in range(options.option_count)
    ]


async def test_steps_follow_the_character_type(concept_checks):
    storage.save_saga(_saga("companion"))
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open_worksheet(pilot, app)
        steps = _steps(screen)
        assert [s.split(" ", 1)[1] for s in steps] == [
            "Concept",
            "Virtues and Flaws",
            "Characteristics",
            "Early Childhood",
            "Later Life",
            "Equipment",
            "Finishing Touches",
        ]
        # Each step's mark: broken must, none, advice, none...
        assert [s.split(" ", 1)[0] for s in steps][:3] == ["✘", "○", "☞"]
        assert "0 of 2 steps pass" in _text(screen, "#ws-progress")
        assert "1 warning, 1 advice" in _text(screen, "#ws-progress")
        region = screen.query_one("#ws-dialog").region
        assert region.right <= 120 and region.bottom <= 45


async def test_moving_between_steps_shows_each_steps_checks(concept_checks):
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open_worksheet(pilot, app)
        assert "Has a House: none" in _text(screen, "#ws-checks")
        await pilot.press("down", "down")
        assert await wait_until(pilot, lambda: screen.step == "characteristics")
        assert "Balanced: 1 over" in _text(screen, "#ws-checks")
        await pilot.press("up", "up")  # and back again
        assert await wait_until(pilot, lambda: screen.step == "concept")


async def test_a_steps_button_runs_its_action_and_the_checks_rerun(monkeypatch):
    calls = []

    def rename(record):
        calls.append(record.name)
        record.name = "Renamed"

    monkeypatch.setitem(
        ws.PANELS,
        ("character", "concept"),
        ws.Panel(
            budget=lambda saga, record: f"Name: {record.name}",
            actions=lambda saga, record: [
                ws.Action("Rename", lambda: Act(lambda: rename(record)))
            ],
        ),
    )
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open_worksheet(pilot, app)
        assert _text(screen, "#ws-budget") == "Name: Leandro"
        await _press_button(pilot, screen, "Rename")
        assert await wait_until(pilot, lambda: calls == ["Leandro"])
        assert storage.load_saga("test_saga").characters[0].name == "Renamed"
        await screen._refresh()
        assert _text(screen, "#ws-budget") == "Name: Renamed"


async def test_move_to_in_play_reviews_then_changes_the_mode(concept_checks):
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open_worksheet(pilot, app)
        workspace = app.screen_stack[-2]
        steps = screen.query_one("#ws-steps", OptionList)
        steps.highlighted = steps.option_count - 1
        assert await wait_until(pilot, lambda: bool(screen.query("#ws-play")))
        screen.query_one("#ws-play", Button).press()
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert "1 warning, 1 advice" in message and "Has a House" in message
        await pilot.press("y")
        assert await wait_until(pilot, lambda: app.screen is workspace)
        assert not storage.load_saga("test_saga").characters[0].in_creation
        assert not workspace.query_one("#btn-worksheet", Button).display


async def test_strict_rules_keep_the_worksheet_open(concept_checks):
    saga = _saga()
    saga.rule_options["strict_creation"] = True
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open_worksheet(pilot, app)
        screen._move_to_play()
        await pilot.pause()
        assert app.screen is screen
        assert storage.load_saga("test_saga").characters[0].in_creation


# -- the step panels --


def _button(screen, label: str) -> Button:
    return next(b for b in screen.query("#ws-actions Button") if str(b.label) == label)


async def _press_button(pilot, screen, label: str) -> None:
    """Press a step's button, once the step's buttons are (re)built."""

    def ready() -> bool:
        return any(str(b.label) == label for b in screen.query("#ws-actions Button"))

    assert await wait_until(pilot, ready), label
    _button(screen, label).press()


async def test_concept_adds_a_magus_virtues_and_opens_the_sheets_dialogs():
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open_worksheet(pilot, app)
        assert "Type:  magus" in _text(screen, "#ws-budget")
        await _press_button(pilot, screen, "Add The Gift and Hermetic Magus")
        assert await wait_until(
            pilot,
            lambda: (
                [
                    vf.vf_id
                    for vf in storage.load_saga("test_saga").characters[0].virtues_flaws
                ]
                == ["vf_the_gift", "vf_hermetic_magus"]
            ),
        )
        await screen._refresh()
        assert "A magus has The Gift: taken" in _text(screen, "#ws-checks")
        labels = [str(b.label) for b in screen.query("#ws-actions Button")]
        assert "Add The Gift and Hermetic Magus" not in labels
        await _press_button(pilot, screen, "Edit House")
        # The dialog is the current screen before it has composed: wait for
        # its title, not just for the screen to change.
        assert await wait_until(
            pilot,
            lambda: app.screen is not screen and app.screen.query("#fields-title"),
        )
        assert "Hermetic Background" in str(
            app.screen.query_one("#fields-title").render()
        )
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is screen)


async def test_virtues_and_flaws_step_opens_the_picker_on_each_side():
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open_worksheet(pilot, app)
        await pilot.press("down")
        assert await wait_until(pilot, lambda: screen.step == "virtues_flaws")
        assert "Virtue points: 0 (allowed 0)" in _text(screen, "#ws-budget")
        assert "Remove one" not in [
            str(b.label) for b in screen.query("#ws-actions Button")
        ]
        await _press_button(pilot, screen, "Add a Flaw")
        picker = await _wait_for(pilot, app, ChooseScreen)
        assert picker.picker_title == "Add a Flaw"
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is screen)


async def test_characteristics_step_fills_a_grog_from_a_grogs_array():
    saga = _saga("grog")
    saga.books_in_play = ["Grogs"]
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open_worksheet(pilot, app)
        await pilot.press("down", "down")
        assert await wait_until(pilot, lambda: screen.step == "characteristics")
        assert "Points:        0 of 7" in _text(screen, "#ws-budget")
        await _press_button(pilot, screen, "Fill from a Grogs array")
        picker = await _wait_for(pilot, app, ChooseScreen)
        picker.dismiss(0)
        assert await wait_until(
            pilot,
            lambda: (
                storage.load_saga("test_saga")
                .characters[0]
                .characteristics.intelligence
                == 2
            ),
        )
        c = storage.load_saga("test_saga").characters[0].characteristics
        assert (c.dexterity, c.quickness) == (-1, -3)
        assert await wait_until(pilot, lambda: app.screen is screen)
        assert "Points:        7 of 7" in _text(screen, "#ws-budget")


async def test_childhood_step_sets_the_native_language_and_a_sample_childhood():
    from textual.widgets import Input

    from ars_magica_manager.tui.screens.fields import FieldsDialog

    storage.save_saga(_saga("companion"))
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open_worksheet(pilot, app)
        screen.query_one("#ws-steps", OptionList).highlighted = 3
        assert await wait_until(pilot, lambda: screen.step == "childhood")
        await _press_button(pilot, screen, "Native Language")
        dialog = await _wait_for(pilot, app, FieldsDialog)
        dialog.query_one("#fld-language", Input).value = "German"
        dialog.query_one("#btn-save", Button).press()
        assert await wait_until(
            pilot,
            lambda: bool(storage.load_saga("test_saga").characters[0].creation_xp),
        )
        assert await wait_until(pilot, lambda: app.screen is screen)
        await _press_button(pilot, screen, "Use a sample childhood")
        picker = await _choose(pilot, app, "Traveling")
        dialog = await _wait_for(pilot, app, FieldsDialog)
        for key, value in (
            ("area", "Rhine"),
            ("second_area", "Alps"),
            ("language", "French"),
        ):
            dialog.query_one(f"#fld-{key}", Input).value = value
        dialog.query_one("#btn-save", Button).press()
        assert await wait_until(
            pilot,
            lambda: (
                sum(
                    x.xp
                    for x in storage.load_saga("test_saga").characters[0].creation_xp
                )
                == 120
            ),
        )
        character = storage.load_saga("test_saga").characters[0]
        assert {a.name for a in character.abilities} >= {
            "Living Language: German",
            "Area Lore: Alps",
            "Living Language: French",
        }
        assert picker is not None
        await screen._refresh()
        assert "Other childhood xp: 45 of 45" in _text(screen, "#ws-budget")


async def _wait_for(pilot, app, cls):
    assert await wait_until(pilot, lambda: isinstance(app.screen, cls))
    await pilot.pause()
    return app.screen


async def _choose(pilot, app, text: str) -> ChooseScreen:
    """Choose the first entry of the list on show whose label has `text`
    (by its label: keys can outrun the list filling up under load)."""
    picker = await _wait_for(pilot, app, ChooseScreen)
    picker.dismiss(
        next(i for i, c in enumerate(picker._all()) if text in strip_markup(c.label))
    )
    return picker


async def test_later_life_step_offers_virtue_xp_and_free_scores():
    from ars_magica_manager.models import VirtueFlawInstance
    from ars_magica_manager.tui.screens.fields import FieldsDialog

    saga = _saga("companion")
    companion = saga.characters[0]
    companion.background.year_born = 1195
    companion.virtues_flaws = [
        VirtueFlawInstance("vf_warrior"),
        VirtueFlawInstance("vf_second_sight"),
    ]
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open_worksheet(pilot, app)
        screen.query_one("#ws-steps", OptionList).highlighted = 4
        assert await wait_until(pilot, lambda: screen.step == "later_life")
        assert "20 years at 15 xp = 300 xp" in _text(screen, "#ws-budget")
        await _press_button(pilot, screen, "Record free Virtue scores")
        assert await wait_until(
            pilot,
            lambda: (
                [
                    (x.step, x.target)
                    for x in storage.load_saga("test_saga").characters[0].creation_xp
                ]
                == [("free", "Second Sight")]
            ),
        )
        await screen._refresh()
        await _press_button(pilot, screen, "Spend Warrior xp")
        dialog = await _wait_for(pilot, app, FieldsDialog)
        assert dialog.title_text == "Spend Warrior xp"
        [target] = [f for f in dialog.fields if f.key == "target"]
        offered = {value for _, value in target.options}
        assert "Single Weapon" in offered and "Brawl" not in offered
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is screen)


def _rows(screen) -> list[str]:
    """The step list's rows as plain text (headings included)."""
    listing = screen.query_one("#ws-list", SelectableList)
    return [
        strip_markup(str(listing.get_option_at_index(i).prompt)).strip()
        for i in range(listing.option_count)
    ]


async def _choose_row(pilot, screen, text: str) -> None:
    """Focus the step's list and choose the first row containing `text`."""
    assert await wait_until(pilot, lambda: any(text in r for r in _rows(screen))), text
    listing = screen.query_one("#ws-list", SelectableList)
    listing.focus()
    index = next(
        i
        for i, row in enumerate(screen._rows)
        if not row.heading and text in strip_markup(row.label)
    )
    assert listing.select_data_index(index)
    await pilot.pause()


async def test_later_life_takes_and_drops_a_training_package():
    saga = _saga("grog")
    saga.characters[0].background.year_born = 1195
    saga.books_in_play = ["Grogs"]
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open_worksheet(pilot, app)
        screen.query_one("#ws-steps", OptionList).highlighted = 4
        assert await wait_until(pilot, lambda: screen.step == "later_life")
        await _press_button(pilot, screen, "Take a training package")
        # Animal Trainer, 5 years (listed before 3): no blanks.
        await _choose(pilot, app, "Animal Trainer")
        assert await wait_until(
            pilot,
            lambda: len(storage.load_saga("test_saga").characters[0].creation_xp) == 3,
        )
        saved = storage.load_saga("test_saga").characters[0]
        assert {(x.target, x.xp) for x in saved.creation_xp} == {
            ("Animal Handling", 30),
            ("Profession: Animal Trainer", 30),
            ("Ride", 15),
        }
        await screen._refresh()
        assert "Training package: Animal Trainer (5 years)" in _rows(screen)
        assert "20 years: 5 in training packages, 15 years at 15 xp = 225 xp" in _text(
            screen, "#ws-budget"
        )
        # d on any of the package's rows drops the whole package.
        await _choose_row(pilot, screen, "Ride")
        await pilot.press("d")
        await _wait_for(pilot, app, ConfirmScreen)
        await pilot.press("y")
        assert await wait_until(
            pilot,
            lambda: storage.load_saga("test_saga").characters[0].creation_xp == [],
        )


async def test_apprenticeship_step_learns_a_spell_with_its_lab_total():

    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open_worksheet(pilot, app)
        screen.query_one("#ws-steps", OptionList).highlighted = 5
        assert await wait_until(pilot, lambda: screen.step == "apprenticeship")
        assert "Apprenticeship: 240 xp" in _text(screen, "#ws-budget")
        await _press_button(pilot, screen, "Learn a spell")
        picker = await _wait_for(pilot, app, ChooseScreen)
        details = str(picker.query_one("#picker-details-text", Static).render())
        assert "Lab Total for it (aura 3)" in details
        picker.dismiss(
            next(
                i
                for i, c in enumerate(picker._all())
                if c.value == "spell_wizard_s_sidestep"
            )
        )
        assert await wait_until(
            pilot,
            lambda: (
                [
                    k.spell_id
                    for k in storage.load_saga("test_saga").characters[0].spells_known
                ]
                == ["spell_wizard_s_sidestep"]
            ),
        )
        await screen._refresh()
        row = next(r for r in _rows(screen) if "Wizard's Sidestep" in r)
        assert "ReIm 10" in row and "level  10" in row and "Lab Total 3" in row
        assert "Wizard's Sidestep at most the Lab Total: level 10, Lab Total 3" in (
            _text(screen, "#ws-checks")
        )
        # The chosen spell's details show below the list; d forgets it.
        await _choose_row(pilot, screen, "Wizard's Sidestep")
        details = _text(screen, "#ws-details")
        assert "Learned at level: 10" in details and "Range: Personal" in details
        await pilot.press("d")
        await _wait_for(pilot, app, ConfirmScreen)
        await pilot.press("y")
        assert await wait_until(
            pilot,
            lambda: storage.load_saga("test_saga").characters[0].spells_known == [],
        )


async def test_xp_list_spends_changes_and_takes_back_in_pool_xp():
    """With an Affinity, 10 pool xp gains 15; changing it to 4 gains 6, and
    taking it back leaves the Art at 0: never by lowering the total."""
    from textual.widgets import Input

    from ars_magica_manager.models import VirtueFlawInstance
    from ars_magica_manager.tui.screens.fields import FieldsDialog

    saga = _saga()
    saga.characters[0].virtues_flaws = [
        VirtueFlawInstance("vf_affinity_with_art", {"art": "creo"})
    ]
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open_worksheet(pilot, app)
        screen.query_one("#ws-steps", OptionList).highlighted = 5
        assert await wait_until(pilot, lambda: screen.step == "apprenticeship")
        await pilot.press("a")
        dialog = await _wait_for(pilot, app, FieldsDialog)
        dialog.query_one("#fld-target", Select).value = "Creo"
        dialog.query_one("#fld-xp", Input).value = "10"
        assert await wait_until(
            pilot,
            lambda: (
                "Creo: gains 15 xp (Affinity x1.5)"
                in strip_markup(str(dialog.query_one("#fields-live", Static).render()))
            ),
        )
        live = strip_markup(str(dialog.query_one("#fields-live", Static).render()))
        assert "Score 5 · Score 6 at 21 xp (4 more pool xp)" in live
        dialog.query_one("#btn-save", Button).press()

        def creo() -> int:
            arts = storage.load_saga("test_saga").characters[0].arts
            return arts["creo"].xp if "creo" in arts else 0

        assert await wait_until(pilot, lambda: creo() == 15)
        assert await wait_until(pilot, lambda: app.screen is screen)
        await screen._refresh()
        row = next(r for r in _rows(screen) if r.startswith("○ Creo"))
        assert row.split()[2:5] == ["10", "15", "5"]
        await _choose_row(pilot, screen, "Creo")
        assert "Affinity: pool xp spent on it gains half again" in _text(
            screen, "#ws-details"
        )
        await pilot.press("e")
        dialog = await _wait_for(pilot, app, FieldsDialog)
        assert dialog.query_one("#fld-xp", Input).value == "10"
        dialog.query_one("#fld-xp", Input).value = "4"
        dialog.query_one("#btn-save", Button).press()
        assert await wait_until(pilot, lambda: creo() == 6)
        assert await wait_until(pilot, lambda: app.screen is screen)
        await pilot.press("d")
        confirm = await _wait_for(pilot, app, ConfirmScreen)
        message = str(confirm.query_one("#confirm-message", Static).render())
        assert "Take back the 4 xp spent on Creo? (6 xp comes off it)" in message
        await pilot.press("y")
        assert await wait_until(pilot, lambda: creo() == 0)


async def test_spending_on_an_ability_sets_its_specialty():
    from textual.widgets import Input

    from ars_magica_manager.tui.screens.fields import FieldsDialog

    storage.save_saga(_saga("companion"))
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open_worksheet(pilot, app)
        screen.query_one("#ws-steps", OptionList).highlighted = 3
        assert await wait_until(pilot, lambda: screen.step == "childhood")
        await pilot.press("a")
        dialog = await _wait_for(pilot, app, FieldsDialog)
        dialog.query_one("#fld-target", Select).value = "Brawl"
        dialog.query_one("#fld-xp", Input).value = "15"
        assert await wait_until(
            pilot, lambda: dialog.query_one("#fld-specialty", Input).display
        )
        dialog.query_one("#fld-specialty", Input).value = "dodging"
        dialog.query_one("#btn-save", Button).press()

        def brawl():
            character = storage.load_saga("test_saga").characters[0]
            return next((a for a in character.abilities if a.name == "Brawl"), None)

        assert await wait_until(pilot, lambda: brawl() is not None)
        ability = brawl()
        assert ability is not None
        assert (ability.xp, ability.specialty) == (15, "dodging")


async def test_virtues_and_flaws_list_shows_the_rules_and_d_removes_one():
    from ars_magica_manager.models import VirtueFlawInstance

    saga = _saga("companion")
    saga.characters[0].virtues_flaws = [
        VirtueFlawInstance("vf_warrior"),
        VirtueFlawInstance("vf_blind"),
    ]
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open_worksheet(pilot, app)
        await pilot.press("down")
        assert await wait_until(pilot, lambda: screen.step == "virtues_flaws")
        rows = _rows(screen)
        assert rows[0] == "Virtues" and "Flaws" in rows
        await _choose_row(pilot, screen, "Warrior")
        details = _text(screen, "#ws-details")
        assert "Rules:" in details and "Martial Abilities" in details
        await pilot.press("d")
        await _wait_for(pilot, app, ConfirmScreen)
        await pilot.press("y")
        assert await wait_until(
            pilot,
            lambda: (
                [
                    vf.vf_id
                    for vf in storage.load_saga("test_saga").characters[0].virtues_flaws
                ]
                == ["vf_blind"]
            ),
        )


async def test_a_new_record_opens_its_worksheet():
    from textual.widgets import Input

    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        workspace = app.screen
        workspace.action_create_covenant()
        assert await wait_until(pilot, lambda: bool(app.screen.query("#fld-name")))
        app.screen.query_one("#fld-name", Input).value = "Durenmar"
        app.screen.query_one("#btn-save", Button).press()
        assert await wait_until(
            pilot, lambda: isinstance(app.screen, CreationWorksheetScreen)
        )
        assert app.screen.record.name == "Durenmar"
        assert "Baseline" in _steps(app.screen)[0]


async def test_gauntlet_step_rolls_pre_play_aging_after_asking():
    saga = _saga()
    saga.characters[0].background.year_born = 1180  # 40
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open_worksheet(pilot, app)
        screen.query_one("#ws-steps", OptionList).highlighted = 6
        assert await wait_until(pilot, lambda: screen.step == "gauntlet")
        assert "Gauntlet at 25: 15 years past it" in _text(screen, "#ws-budget")
        assert "Pre-play aging: 5 roll(s) to make" in _text(screen, "#ws-budget")
        await _press_button(pilot, screen, "Roll pre-play aging")
        await _wait_for(pilot, app, ConfirmScreen)
        await pilot.press("y")
        assert await wait_until(
            pilot,
            lambda: (
                storage.load_saga("test_saga").characters[0].creation_conditions.aged_to
                == 39
            ),
        )
        diary = storage.load_saga("test_saga").characters[0].diary
        assert len(diary) == 5
        assert await wait_until(
            pilot, lambda: "Pre-play aging rolled: done" in _text(screen, "#ws-checks")
        )


async def test_finishing_touches_takes_a_grogs_aging_from_the_grogs_aging_chart():
    from ars_magica_manager.tui.screens.fields import FieldsDialog

    saga = _saga("grog")
    saga.characters[0].background.year_born = 1175  # 45
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open_worksheet(pilot, app)
        steps = screen.query_one("#ws-steps", OptionList)
        steps.highlighted = steps.option_count - 1
        assert await wait_until(pilot, lambda: screen.step == "finish")
        await _press_button(pilot, screen, "Use the Grogs Aging Chart")
        dialog = await _wait_for(pilot, app, FieldsDialog)
        dialog.query_one("#fld-kind", Select).value = "harsh"
        assert await wait_until(
            pilot,
            lambda: (
                "Total: 6 Aging Point(s)" in strip_markup(_text(dialog, "#fields-live"))
            ),
        )
        dialog.query_one("#btn-save", Button).press()

        def saved():
            return storage.load_saga("test_saga").characters[0]

        assert await wait_until(
            pilot, lambda: saved().creation_conditions.aged_to == 44
        )
        grog = saved()
        assert grog.creation_conditions.aging_chart == "harsh"
        assert grog.creation_conditions.aging_chart_cap == 1
        assert grog.aging.decrepitude_points == 6
        assert len(grog.diary) == 1
        assert await wait_until(pilot, lambda: app.screen is screen)
        assert await wait_until(
            pilot,
            lambda: (
                "the Grogs Aging Chart, harsh aging (Ability cap 1 higher)"
                in _text(screen, "#ws-budget")
            ),
        )
        assert await wait_until(
            pilot, lambda: "Pre-play aging rolled: done" in _text(screen, "#ws-checks")
        )
        assert await wait_until(
            pilot,
            lambda: (
                not any(
                    str(b.label) == "Use the Grogs Aging Chart"
                    for b in screen.query("#ws-actions Button")
                )
            ),
        )


async def test_finishing_touches_reviews_every_step_and_adds_a_trait():
    from ars_magica_manager.tui.screens.fields import FieldsDialog

    storage.save_saga(_saga("grog"))
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open_worksheet(pilot, app)
        steps = screen.query_one("#ws-steps", OptionList)
        steps.highlighted = steps.option_count - 1
        assert await wait_until(pilot, lambda: screen.step == "finish")
        budget = _text(screen, "#ws-budget")
        assert "Review:" in budget and "Concept: 1 warning" in budget
        await _press_button(pilot, screen, "Add a Personality Trait")
        await _wait_for(pilot, app, FieldsDialog)
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is screen)


async def test_concept_adds_the_house_virtue_asking_which_when_there_is_a_choice():
    saga = _saga()
    saga.characters[0].hermetic.house = "house_flambeau"
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open_worksheet(pilot, app)
        assert "Puissant Perdo or Puissant Ignem." in _text(screen, "#ws-budget")
        await _press_button(pilot, screen, "Add the House Virtue")
        await _choose(pilot, app, "Puissant Ignem")
        assert await wait_until(
            pilot,
            lambda: (
                [
                    (vf.vf_id, vf.params)
                    for vf in storage.load_saga("test_saga").characters[0].virtues_flaws
                ]
                == [("vf_puissant_art", {"art": "ignem"})]
            ),
        )


async def test_a_hedge_wizard_chooses_a_tradition_and_trains():
    saga = _saga("companion")
    saga.traditions = ["trad_vitkir"]
    vitki = saga.characters[0]
    vitki.virtues_flaws = [VirtueFlawInstance("vf_the_gift")]
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open_worksheet(pilot, app)
        assert "Tradition Training" not in " ".join(_steps(screen))
        await _press_button(pilot, screen, "Choose tradition")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ChooseScreen))
        await pilot.press("enter")
        assert await wait_until(
            pilot, lambda: "Tradition Training" in " ".join(_steps(screen))
        )
        assert "Vitkir" in _text(screen, "#ws-budget")
        steps = screen.query_one("#ws-steps", OptionList)
        steps.highlighted = [s.key for s in screen.steps].index("training")
        assert await wait_until(pilot, lambda: screen.step == "training")
        assert await wait_until(pilot, lambda: "290 xp" in _text(screen, "#ws-budget"))
        await _press_button(pilot, screen, "Open the Arts")
        assert await wait_until(
            pilot, lambda: "Opening: done" in _text(screen, "#ws-budget")
        )
        lines = "\n".join(screen_lines(app))
        assert "Rune Magic at least 1" in lines
