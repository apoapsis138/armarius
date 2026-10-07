"""Adding, editing and removing Virtues, Flaws and Abilities on characters and laboratories."""

import re

from screen_helpers import (
    _ability_labels,
    _character_vf_labels,
    _choose_in_list,
    _choose_lab_row,
    _confirm,
    _is_form,
    _lab_characteristics_text,
    _lab_rows,
    _open_lab_section,
    _open_section,
    _saga_with_bare_character,
    _saga_with_bare_laboratory,
    _sample_saga_with_covenant,
    _select,
    _select_character,
    _select_covenant,
    _select_laboratory,
    _select_vf_picker_entry,
    _wait_for_picker_ready,
)
from support import menu, picker_rows, strip_markup, wait_until
from textual.widgets import Input, Select, Static

from ars_magica_manager import storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import Laboratory, VirtueFlawInstance
from ars_magica_manager.screens import (
    AbilityPickerScreen,
    ConfirmScreen,
    FieldsDialog,
    LabVirtueFlawPickerScreen,
    VirtueFlawPickerScreen,
    WorkspaceScreen,
)


async def test_add_virtue_flaw_without_parameters_to_character():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf-virtues")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, VirtueFlawPickerScreen)

        await _select_vf_picker_entry(pilot, app, "vf_common_sense")

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Common Sense" in _character_vf_labels(app.screen._character_sheet_view)

    saga = storage.load_saga("test_saga")
    character = saga.characters[0]
    assert len(character.virtues_flaws) == 1
    assert character.virtues_flaws[0].vf_id == "vf_common_sense"


async def test_add_virtue_flaw_with_parameters_to_character():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf-virtues")

        await pilot.press("a")
        await pilot.pause()

        await _select_vf_picker_entry(pilot, app, "vf_affinity_with_art")
        assert isinstance(app.screen, FieldsDialog)

        # An {art} is picked from the fifteen Arts.
        app.screen.query_one("#fld-art", Select).value = "creo"
        await pilot.click("#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Affinity with Creo" in _character_vf_labels(
            app.screen._character_sheet_view
        )

    saga = storage.load_saga("test_saga")
    character = saga.characters[0]
    assert len(character.virtues_flaws) == 1
    assert character.virtues_flaws[0].vf_id == "vf_affinity_with_art"
    assert character.virtues_flaws[0].params == {"art": "creo"}


async def test_cancelling_param_screen_returns_to_picker_without_adding():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf-virtues")

        await pilot.press("a")
        await pilot.pause()
        await _wait_for_picker_ready(pilot, app)
        picker = app.screen
        app.screen.query_one("#picker-search", Input).value = "affinity with {art}"
        await wait_until(pilot, lambda: len(picker_rows(picker)) == 1)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)

        await pilot.press("escape")
        await pilot.pause()

        assert isinstance(app.screen, VirtueFlawPickerScreen)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].virtues_flaws == []


async def test_virtue_flaw_picker_excludes_held_entries_unless_repeatable():
    saga = _saga_with_bare_character()
    saga.characters[0].virtues_flaws += [
        VirtueFlawInstance(vf_id="vf_affinity_with_art", params={"art": "creo"}),
        VirtueFlawInstance(vf_id="vf_adept_laboratory_student"),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf-virtues")

        await pilot.press("a")
        await pilot.pause()
        await _wait_for_picker_ready(pilot, app)

        item_ids = app.screen.shown_ids()
        assert "vf-vf_adept_laboratory_student" not in item_ids
        # Affinity with Art may be taken twice, for two different Arts.
        assert "vf-vf_affinity_with_art" in item_ids


async def test_virtue_flaw_picker_search_filters_by_typed_text():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf-virtues")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, VirtueFlawPickerScreen)

        picker = app.screen
        await _wait_for_picker_ready(pilot, app)
        assert len(picker_rows(picker)) > 100  # the catalog's Virtues
        search = app.screen.query_one("#picker-search", Input)

        # Nothing matches: a single "(no matches...)" row.
        search.value = "xyzzy nonexistent"
        await wait_until(pilot, lambda: len(picker_rows(picker)) == 1)
        assert picker_rows(picker)[0][0] is None

        # The name's match first, then the Virtues whose summary mentions it.
        search.value = "common sense"
        await wait_until(pilot, lambda: 1 < len(picker_rows(picker)) < 10)
        item_ids = picker.shown_ids()
        assert item_ids[0] == "vf-vf_common_sense"
        assert len(item_ids) > 1

        # Enter in the search box takes the top match.
        await search.action_submit()
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        assert "Common Sense" in _character_vf_labels(app.screen._character_sheet_view)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].virtues_flaws[0].vf_id == "vf_common_sense"


async def test_lab_virtue_flaw_picker_search_filters_by_typed_text():
    saga = _saga_with_bare_character()
    saga.laboratories.append(
        Laboratory(id="lab1", covenant_id="cov1", name="Test Lab", owner_id="char1")
    )
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)
        await _select(pilot, app, ("laboratory", "lab1"))
        await _open_lab_section(pilot, app, "section-lab-vf-virtues")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, LabVirtueFlawPickerScreen)

        picker = app.screen
        await _wait_for_picker_ready(pilot, app)
        assert len(picker.shown_ids()) > 30  # the full 128-entry lab catalog

        app.screen.query_one("#picker-search", Input).value = "superior construction"
        await wait_until(pilot, lambda: len(picker_rows(picker)) == 1)

        item_ids = picker.shown_ids()
        assert item_ids == ["labvf-labvf_superior_construction"]


async def test_ability_picker_search_filters_by_typed_text():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "tab-abilities")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, AbilityPickerScreen)

        picker = app.screen
        await _wait_for_picker_ready(pilot, app)
        assert len(picker.shown_ids()) > 30  # the full 78-entry catalog

        app.screen.query_one("#picker-search", Input).value = "athletics"
        await wait_until(pilot, lambda: len(picker_rows(picker)) == 1)

        item_ids = picker.shown_ids()
        assert item_ids == ["ability-ab_athletics"]


async def test_picker_down_key_moves_focus_from_search_to_list():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "tab-abilities")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, AbilityPickerScreen)

        search = app.screen.query_one("#picker-search", Input)
        assert app.focused is search  # search box is focused on open

        await pilot.press("down")
        await pilot.pause()

        assert app.focused is app.screen.query_one("#ability-picker-list")


async def test_add_virtue_flaw_to_laboratory_uses_lab_picker():
    saga = _saga_with_bare_character()
    saga.laboratories.append(
        Laboratory(id="lab1", covenant_id="cov1", name="Test Lab", owner_id="char1")
    )
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)
        await _select(pilot, app, ("laboratory", "lab1"))
        await _open_lab_section(pilot, app, "section-lab-vf-virtues")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, LabVirtueFlawPickerScreen)

        await _wait_for_picker_ready(pilot, app)
        await _choose_in_list(
            pilot, app, "lab-vf-picker-list", "labvf-labvf_superior_construction"
        )

        assert isinstance(app.screen, WorkspaceScreen)
        view = app.screen._laboratory_sheet_view
        assert _lab_rows(view, "lab-vf-virtues-list") == [
            "Superior Construction (Free)"
        ]
        # The Characteristics above follow straight away (Safety +1).
        assert re.search(
            r"Safety:\s+\+0 \[\$text-success\]\+1\[/\] = \[\$text-success\]\+1\[/\]",
            _lab_characteristics_text(view),
        )

    saga = storage.load_saga("test_saga")
    lab = saga.laboratories[0]
    assert len(lab.virtues_flaws) == 1
    assert lab.virtues_flaws[0].vf_id == "labvf_superior_construction"


async def test_create_laboratory_flow_saves_laboratory():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)

        await menu(pilot, app, "n", "New Laboratory")
        await pilot.pause()
        assert _is_form(app.screen, "Create a New Laboratory")

        app.screen.query_one("#fld-name", Input).value = "The Alchemical Tower"
        app.screen.query_one("#fld-size", Input).value = "1"

        await pilot.click("#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert app.screen.selected_laboratory is not None
        assert app.screen.selected_laboratory.name == "The Alchemical Tower"

    saga = storage.load_saga("test_saga")
    assert len(saga.laboratories) == 1
    lab = saga.laboratories[0]
    assert lab.name == "The Alchemical Tower"
    assert lab.covenant_id == "cov1"
    assert lab.characteristics.size == 1
    assert lab.owner_id is None


async def test_add_ability_with_parameters_to_character():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    # 120x45, the smallest size the app targets: at 80x24 the picker's
    # buttons cover the Craft row.
    async with app.run_test(size=(120, 45)) as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "tab-abilities")

        await pilot.press("a")
        await pilot.pause()

        await _wait_for_picker_ready(pilot, app)
        await _choose_in_list(pilot, app, "ability-picker-list", "ability-ab_craft")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)

        app.screen.query_one("#fld-craft", Input).value = "Blacksmith"
        await pilot.click("#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, FieldsDialog)
        assert app.screen.title_text == "Craft: Blacksmith"

        app.screen.query_one("#fld-xp", Input).value = "15"

        await pilot.click("#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    character = saga.characters[0]
    assert len(character.abilities) == 1
    assert character.abilities[0].name == "Craft: Blacksmith"
    assert character.abilities[0].category == "General"
    assert character.abilities[0].level == 2


async def test_cancelling_ability_details_returns_to_picker_without_adding():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "tab-abilities")

        await pilot.press("a")
        await pilot.pause()

        await _wait_for_picker_ready(pilot, app)
        await _choose_in_list(pilot, app, "ability-picker-list", "ability-ab_athletics")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)

        await pilot.press("escape")
        await pilot.pause()

        assert isinstance(app.screen, AbilityPickerScreen)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].abilities == []


async def test_remove_ability_from_character():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "tab-abilities")
        assert "Magic Theory" in _ability_labels(app.screen._character_sheet_view)

        await pilot.press("d")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Magic Theory" not in _ability_labels(app.screen._character_sheet_view)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].abilities == []


async def test_remove_virtue_flaw_from_character():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf-virtues")
        assert "Affinity with Creo" in _character_vf_labels(
            app.screen._character_sheet_view
        )

        await pilot.press("d")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Affinity with Creo" not in _character_vf_labels(
            app.screen._character_sheet_view
        )

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].virtues_flaws == []


async def test_remove_virtue_flaw_from_laboratory():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)
        await _select(pilot, app, ("laboratory", "lab1"))
        await _open_lab_section(pilot, app, "section-lab-vf-virtues")
        view = app.screen._laboratory_sheet_view
        assert "Superior Construction" in _lab_rows(view, "lab-vf-virtues-list")[0]

        # Nothing chosen: pick which one first.
        await pilot.press("d")
        await pilot.pause()
        await _confirm(pilot, app, "n")  # No keeps it
        assert "Superior Construction" in _lab_rows(view, "lab-vf-virtues-list")[0]

        # The chosen row: straight to the confirmation.
        await _choose_lab_row(pilot, view, "lab-vf-virtues-list", 0)
        await pilot.press("d")
        await _confirm(pilot, app, "y")
        assert _lab_rows(view, "lab-vf-virtues-list") == []

    saga = storage.load_saga("test_saga")
    assert saga.laboratories[0].virtues_flaws == []


async def test_lab_vf_tab_warns_and_fills_the_details_panel():
    saga = _saga_with_bare_laboratory()
    saga.laboratories[0].virtues_flaws = [
        VirtueFlawInstance(vf_id="labvf_greater_feature"),
        VirtueFlawInstance(vf_id="labvf_lesser_focus"),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_laboratory(pilot, app)
        await _open_lab_section(pilot, app, "section-lab-vf-flaws")
        view = app.screen._laboratory_sheet_view

        # 3 - 1 = 2 points in a Size 0 lab: over capacity by 2.
        warnings = view.query_one("#lab-vf-warnings", Static)
        assert warnings.display
        assert strip_markup(str(warnings.content)) == (
            "✘ Over capacity by 2 (Virtues less Flaws may total Size + Refinement = 0)."
        )
        # Virtues and Flaws side by side.
        virtues = view.query_one("#section-lab-vf-virtues").region
        flaws = view.query_one("#section-lab-vf-flaws").region
        assert virtues.right <= flaws.x and virtues.y == flaws.y

        await _choose_lab_row(pilot, view, "lab-vf-flaws-list", 1)
        panel = strip_markup(str(view.query_one("#lab-vf-info", Static).content))
        assert panel.startswith("Name: Lesser Focus\nCategory: Structure\n")
        assert "Characteristics: General Quality -1" in panel

        # Deleting the chosen Flaw (after confirming) leaves the lab further
        # over capacity; removing the Feature clears the warning.
        await pilot.press("d")
        await _confirm(pilot, app, "y")
        assert "Over capacity by 3" in str(warnings.content)
        await _choose_lab_row(pilot, view, "lab-vf-virtues-list", 0)
        await pilot.press("d")
        await _confirm(pilot, app, "y")
        assert not warnings.display


async def test_remove_with_nothing_to_remove_stays_on_same_screen():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "tab-abilities")

        await pilot.press("d")
        await pilot.pause()

        # Nothing to remove -- stays on the workspace, no picker opened.
        assert isinstance(app.screen, WorkspaceScreen)


async def test_cancelling_the_delete_confirmation_keeps_the_item():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf-virtues")

        await pilot.press("d")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)

        await pilot.press("escape")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Affinity with Creo" in _character_vf_labels(
            app.screen._character_sheet_view
        )

    saga = storage.load_saga("test_saga")
    assert len(saga.characters[0].virtues_flaws) == 1
