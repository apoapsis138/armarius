"""A familiar's sheet: binding, its details, health and traits."""

import asyncio

from screen_helpers import (
    _choose_in_list,
    _fill,
    _find_node,
    _is_form,
    _open_familiar_section,
    _open_workspace,
    _plain,
    _saga_with_bare_character,
    _saga_with_familiar,
    _sample_saga_with_covenant,
    _save_dialog,
    _select,
    _select_character,
    _select_familiar,
    _wait_for_picker_ready,
    _wait_for_screen,
)
from support import build_all_tabs, menu, wait_until
from textual.widgets import Button, Checkbox, Input, Select, Static, Tree

from ars_magica_manager import familiars as fam
from ars_magica_manager import storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import VirtueFlawInstance
from ars_magica_manager.screens import (
    AbilityPickerScreen,
    ConfirmScreen,
    FieldsDialog,
    SelectableList,
    VirtueFlawPickerScreen,
    WorkspaceScreen,
)
from ars_magica_manager.screens.widgets import DetailsPanel


def _fam_ability_labels(view) -> str:
    """Same idea as _ability_labels(), for a FamiliarSheetView."""
    return " | ".join(
        _plain(label)
        for index, label in fam.ability_rows(view.familiar)
        if index is not None
    )


async def test_binding_a_familiar_nests_it_under_its_magus_and_grants_shared_traits():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_character(pilot, app)
        assert isinstance(app.screen, WorkspaceScreen)

        await menu(pilot, app, "n", "Bind Familiar")
        await pilot.pause()
        assert _is_form(app.screen, "Bind a New Familiar")
        # A magus was already selected: it's preselected as the default.
        assert app.screen.query_one("#fld-character_id", Select).value == "char1"

        app.screen.query_one("#fld-name", Input).value = "Ashwing"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)
        assert app.screen.selected_kind == "familiar"

        # The magus's tree node is now expandable, with the Familiar nested
        # as its one child leaf.
        tree = app.screen.query_one("#nav-tree", Tree)
        magus_node = _find_node(tree, ("character", "char1"))
        familiar_id = next(f.id for f in app.screen.saga.familiars)
        assert [c.data for c in magus_node.children] == [("familiar", familiar_id)]

    saga = storage.load_saga("test_saga")
    [familiar] = saga.familiars
    magus = saga.characters[0]
    assert (familiar.character_id, familiar.name) == ("char1", "Ashwing")
    # True Friend and Loyal (Partner) +3 granted to both partners.
    assert {vf.vf_id for vf in familiar.virtues_flaws} == {"vf_true_friend"}
    assert {vf.vf_id for vf in magus.virtues_flaws} == {"vf_true_friend"}
    assert [(t.name, t.score) for t in familiar.personality_traits] == [
        ("Loyal (Partner)", 3)
    ]
    assert [(t.name, t.score) for t in magus.personality_traits] == [
        ("Loyal (Partner)", 3)
    ]


async def test_bind_familiar_only_defaults_to_the_magus_on_show():
    # After showing a magus, then a laboratory or Saga Content, the dialog
    # still preselected that magus.
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_character(pilot, app)
        # A laboratory or Saga Content doesn't offer Bind Familiar at all.
        for node in (("laboratory", "lab1"), ("saga_content",)):
            await _select(pilot, app, node)
            assert app.screen.check_action("create_familiar", ()) is False
        for node in (("covenant", "cov1"), ("saga",)):
            await _select(pilot, app, node)
            await menu(pilot, app, "n", "Bind Familiar")
            assert await wait_until(
                pilot, lambda: _is_form(app.screen, "Bind a New Familiar")
            )
            value = app.screen.query_one("#fld-character_id", Select).value
            assert value is Select.NULL, (node, value)
            await pilot.press("escape")
            await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))


async def test_records_are_created_where_they_belong():
    # N/c/l/f are offered on the saga and beside their own kind.
    storage.save_saga(_sample_saga_with_covenant())
    expected = {
        ("saga",): {"n", "c", "l", "f"},
        ("covenant", "cov1"): {"c", "l", "f"},
        ("character", "char1"): {"c", "f"},
        ("laboratory", "lab1"): {"l"},
        ("saga_content",): set(),
    }
    keys = {
        "n": "create_covenant",
        "c": "create_character",
        "l": "create_laboratory",
        "f": "create_familiar",
    }
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _open_workspace(pilot)
        for node, offered in expected.items():
            await _select(pilot, app, node)
            enabled = {k for k, a in keys.items() if app.screen.check_action(a, ())}
            assert enabled == offered, node


async def test_overlapping_detail_swaps_leave_one_sheet():
    # Two detail-pane swaps in flight at once (seen after binding a
    # familiar) interleaved their remove/mount steps.
    saga = _saga_with_familiar()
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_familiar(pilot, app)
        workspace = app.screen
        familiar = workspace.saga.familiars[0]
        await asyncio.gather(
            workspace._show_familiar_detail(familiar),
            workspace._show_saga_detail(),
        )
        await pilot.pause()
        children = list(workspace._detail_pane().children)
        assert [type(c).__name__ for c in children] == ["Static"], children


async def test_create_familiar_is_disabled_once_every_magus_has_one():
    storage.save_saga(_saga_with_familiar())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_character(pilot, app)
        assert app.screen.check_action("create_familiar", ()) is False
        # New doesn't offer it.
        assert [item.label for item in app.screen._new_items()] == ["New Character"]


async def test_editing_familiar_info_updates_the_top_panel_and_tree():
    storage.save_saga(_saga_with_familiar())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_familiar(pilot, app)
        assert app.screen._active_section() == "section-fam-info"

        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Familiar")
        app.screen.query_one("#fld-name", Input).value = "Nightwing"
        app.screen.query_one("#fld-species", Input).value = "Raven"
        app.screen.query_one("#fld-magic_might", Input).value = "8"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        view = app.screen._familiar_sheet_view
        text = str(view.query_one("#fam-info-content", Static).render())
        assert "Species / Description: Raven" in text
        assert "Magic Might Score: 8" in text

        tree = app.screen.query_one("#nav-tree", Tree)
        magus_node = _find_node(tree, ("character", "char1"))
        assert "Nightwing" in str(magus_node.children[0].label)

    [familiar] = storage.load_saga("test_saga").familiars
    assert (familiar.name, familiar.species, familiar.magic_might) == (
        "Nightwing",
        "Raven",
        8,
    )


async def test_editing_familiar_binding_shows_cord_costs_and_saves():
    storage.save_saga(_saga_with_familiar())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_familiar(pilot, app)
        await _open_familiar_section(pilot, app, "section-fam-binding")
        assert app.screen._active_section() == "section-fam-binding"

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        cord = app.screen.query_one("#fld-golden_cord", Select)
        assert ("+3 (30 pts)", "3") in [
            (str(prompt), value) for prompt, value in cord._options
        ]
        cord.value = "3"
        app.screen.query_one("#fld-binding_lab_total", Input).value = "45"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        view = app.screen._familiar_sheet_view
        text = str(view.query_one("#fam-binding-content", Static).render())
        assert "Golden Cord: +3 (30 pts)" in text
        assert "Initial Binding Lab Total: 45" in text

    [familiar] = storage.load_saga("test_saga").familiars
    assert (familiar.golden_cord, familiar.binding_lab_total) == (3, 45)


async def test_editing_familiar_wounds_and_fatigue_updates_the_health_panel():
    storage.save_saga(_saga_with_familiar())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_familiar(pilot, app)
        await _open_familiar_section(pilot, app, "section-fam-health")
        assert app.screen._active_section() == "section-fam-health"

        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Wounds")
        app.screen.query_one("#fld-light", Input).value = "2"
        app.screen.query_one("#fld-incapacitated", Checkbox).value = True
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        view = app.screen._familiar_sheet_view
        wounds_text = str(view.query_one("#fam-wounds-content", Static).render())
        assert "Light Wounds:  2" in wounds_text
        assert "Incapacitated: yes" in wounds_text

        await pilot.click("#btn-fam-health-fatigue-edit")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Fatigue Level")
        app.screen.query_one("#fld-level", Select).value = "weary"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        fatigue_text = str(view.query_one("#fam-fatigue-content", Static).render())
        assert "Fatigue Level: Weary" in fatigue_text

    [familiar] = storage.load_saga("test_saga").familiars
    assert (familiar.wounds.light, familiar.wounds.incapacitated) == (2, True)
    assert familiar.fatigue_level == "weary"


async def test_familiar_natural_weapons_use_generic_add_edit_remove():
    storage.save_saga(_saga_with_familiar())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_familiar(pilot, app)
        await _open_familiar_section(pilot, app, "section-fam-natural-weapons")
        assert app.screen.check_action("add", ()) is True

        await pilot.press("a")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        _fill(app, name="Bite", weapon_attack=5)
        await _save_dialog(pilot, app)

        [familiar] = storage.load_saga("test_saga").familiars
        assert len(familiar.natural_weapons) == 1
        assert familiar.natural_weapons[0].name == "Bite"
        assert familiar.natural_weapons[0].weapon_attack == 5

        view = app.screen._familiar_sheet_view
        list_widget = view.query_one("#fam-natural-weapons-list", SelectableList)
        assert any("Bite" in str(o.prompt) for o in list_widget.options)

        await pilot.press("d")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    assert storage.load_saga("test_saga").familiars[0].natural_weapons == []


async def test_familiar_abilities_use_generic_add_edit_remove():
    storage.save_saga(_saga_with_familiar())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_familiar(pilot, app)
        await _open_familiar_section(pilot, app, "tab-fam-abilities")
        assert app.screen.check_action("add", ()) is True

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, AbilityPickerScreen)
        await _wait_for_picker_ready(pilot, app)
        await _choose_in_list(pilot, app, "ability-picker-list", "ability-ab_athletics")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        app.screen.query_one("#fld-xp", Input).value = "30"
        app.screen.query_one("#fld-specialty", Input).value = "Running"
        await pilot.click("#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        view = app.screen._familiar_sheet_view
        assert "Athletics (Running) 3 30/50" in _fam_ability_labels(view)

        [familiar] = storage.load_saga("test_saga").familiars
        assert len(familiar.abilities) == 1
        assert familiar.abilities[0].name == "Athletics"
        assert familiar.abilities[0].level == 3
        assert familiar.abilities[0].specialty == "Running"

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        app.screen.query_one("#fld-xp", Input).value = "50"
        await pilot.click("#btn-save")
        await pilot.pause()
        assert "Athletics (Running) 4 50/75" in _fam_ability_labels(view)

        await pilot.press("d")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    assert storage.load_saga("test_saga").familiars[0].abilities == []


async def test_familiar_virtues_flaws_add_via_a_and_delete_via_d():
    storage.save_saga(_saga_with_familiar())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_familiar(pilot, app)
        await _open_familiar_section(pilot, app, "section-fam-vf-virtues")
        assert app.screen.check_action("add_virtue_flaw", ()) is True

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, VirtueFlawPickerScreen)
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    saga.familiars[0].virtues_flaws.append(VirtueFlawInstance(vf_id="vf_true_friend"))
    storage.save_saga(saga)

    app2 = ArsMagicaManagerApp()
    async with app2.run_test(size=(140, 70)) as pilot:
        await _select_familiar(pilot, app2)
        await _open_familiar_section(pilot, app2, "section-fam-vf-virtues")
        assert app2.screen.check_action("remove_virtue_flaw", ()) is True
        await pilot.press("d")
        await pilot.pause()
        await wait_until(pilot, lambda: isinstance(app2.screen, ConfirmScreen))
        await pilot.press("y")
        await wait_until(pilot, lambda: isinstance(app2.screen, WorkspaceScreen))

    assert storage.load_saga("test_saga").familiars[0].virtues_flaws == []


async def test_removing_a_familiar_virtue_flaw_uses_the_chosen_row_and_confirms():
    # Familiar V&F removal ignored the chosen row and never asked.
    saga = _saga_with_familiar()
    saga.familiars[0].virtues_flaws = [
        VirtueFlawInstance(vf_id="vf_true_friend"),
        VirtueFlawInstance(vf_id="vf_true_friend"),
        VirtueFlawInstance(vf_id="vf_puissant_ability", params={"ability": "Brawl"}),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_familiar(pilot, app)
        await _open_familiar_section(pilot, app, "section-fam-vf-virtues")
        rows = app.screen._familiar_sheet_view.query_one(
            "#fam-vf-virtues-list", SelectableList
        )
        rows.focus()
        await pilot.pause()
        position = next(i for i, (index, _) in enumerate(rows._rows) if index == 2)
        rows.highlighted = position
        assert await wait_until(pilot, lambda: rows._marked == position)

        await pilot.press("d")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert "Puissant" in message, message
        await pilot.press("n")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        assert len(storage.load_saga("test_saga").familiars[0].virtues_flaws) == 3

        await pilot.press("d")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))

    assert [
        vf.vf_id for vf in storage.load_saga("test_saga").familiars[0].virtues_flaws
    ] == [
        "vf_true_friend",
        "vf_true_friend",
    ]


async def test_familiar_details_panels_are_shaded_like_every_other_sheet():
    # The familiar sheet's details panels had no shaded panel style.
    # (each is a DetailsPanel docked at the bottom of its tab.)
    storage.save_saga(_saga_with_familiar())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_familiar(pilot, app)
        await build_all_tabs(pilot, app.screen._current_sheet_view())
        view = app.screen._familiar_sheet_view
        for panel_id in (
            "fam-vf-info",
            "fam-natural-weapons-info",
            "fam-ability-info",
            "fam-bond-powers-info",
        ):
            panel = view.query_one(f"#{panel_id}", Static).parent
            assert isinstance(panel, DetailsPanel), panel_id
            assert panel.styles.background.a > 0, panel_id
