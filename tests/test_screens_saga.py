"""The saga picker, themes, creating a saga and its records, and the workspace tree."""

from screen_helpers import (
    _ability_labels,
    _character_vf_labels,
    _find_node,
    _is_form,
    _known_spell_labels,
    _open_workspace,
    _plain,
    _saga_with_empty_covenant,
    _sample_saga_with_covenant,
    _select,
    _select_character,
    _select_covenant,
)
from support import click_when_shown, close_worksheet, menu
from textual.widgets import Button, Collapsible, Input, ListView, Select, Static, Tree

from ars_magica_manager import settings, storage
from ars_magica_manager.models import Saga
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import SagaPickerScreen, ThemeBar, WorkspaceScreen


async def test_picker_shows_placeholder_with_no_sagas():
    app = ArsMagicaManagerApp()
    async with app.run_test():
        assert isinstance(app.screen, SagaPickerScreen)
        list_view = app.screen.query_one("#saga-list", ListView)
        assert len(list_view.children) == 1


async def test_theme_bar_shows_active_theme():
    app = ArsMagicaManagerApp()
    async with app.run_test():
        theme_bar = app.screen.query_one("#theme-bar", ThemeBar)
        assert str(theme_bar.render()) == "Theme: Scriptorum"


async def test_switching_theme_updates_theme_bar_and_persists():
    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        app.theme = "scriptorum-dark"
        await pilot.pause()

        theme_bar = app.screen.query_one("#theme-bar", ThemeBar)
        assert str(theme_bar.render()) == "Theme: Scriptorum Dark"

    assert settings.load_settings() == {"theme": "scriptorum-dark"}


async def test_saving_the_theme_keeps_the_other_settings():
    # Every theme change (including the one on launch) rewrote the
    # settings file with the theme alone.
    settings.save_settings({"theme": "scriptorum", "other": 1})

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        app.theme = "scriptorum-dark"
        await pilot.pause()

    assert settings.load_settings() == {"theme": "scriptorum-dark", "other": 1}


async def test_saved_theme_is_restored_on_next_launch():
    settings.save_settings({"theme": "scriptorum-dark"})

    app = ArsMagicaManagerApp()
    async with app.run_test():
        assert app.theme == "scriptorum-dark"


async def test_create_saga_flow_saves_and_returns_to_picker():
    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await pilot.press("n")
        await pilot.pause()
        assert _is_form(app.screen, "Create a New Saga")

        form = app.screen
        form.query_one("#fld-name", Input).value = "Dammerstein"
        form.query_one("#fld-storyguide", Input).value = "Alex"
        form.query_one("#fld-year", Input).value = "1220"

        await click_when_shown(pilot, "#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, SagaPickerScreen)

    assert storage.list_sagas() == ["dammerstein"]
    saga = storage.load_saga("dammerstein")
    assert saga.name == "Dammerstein"
    assert saga.storyguide == "Alex"
    assert saga.current_year == 1220
    assert saga.current_season == "Spring"
    assert saga.description == ""


async def test_selecting_a_saga_opens_the_workspace():
    storage.save_saga(
        Saga(id="test_saga", name="Test Saga", storyguide="Alex", current_year=1220)
    )

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        list_view = app.screen.query_one("#saga-list", ListView)
        assert list_view.index == 0

        await pilot.press("enter")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert app.screen.saga.id == "test_saga"
        assert app.screen.selected_kind == "saga"


async def test_workspace_tree_has_no_covenants_for_a_fresh_saga():
    storage.save_saga(Saga(id="test_saga", name="Test Saga", storyguide="Alex"))

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_workspace(pilot)

        tree = app.screen.query_one("#nav-tree", Tree)
        # No covenants: an empty Region and Bestiary, Conflicts, the Seasons,
        # Saga Content, and the storyguide's Armarium and Custodia.
        assert [n.data for n in tree.root.children] == [
            ("region",),
            ("bestiary",),
            ("conflicts",),
            ("seasons",),
            ("saga_content",),
            ("armarium",),
            ("custodia",),
        ]


async def test_create_covenant_flow_saves_covenant():
    storage.save_saga(Saga(id="test_saga", name="Test Saga", storyguide="Alex"))

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_workspace(pilot)

        await menu(pilot, app, "n", "New Covenant")
        await pilot.pause()
        assert _is_form(app.screen, "Create a New Covenant")

        app.screen.query_one("#fld-name", Input).value = "Fengheld"
        app.screen.query_one("#fld-notes", Input).value = "A border covenant"

        await click_when_shown(pilot, "#btn-save")
        await pilot.pause()
        await close_worksheet(pilot, app)

        assert isinstance(app.screen, WorkspaceScreen)
        assert app.screen.selected_covenant is not None
        assert app.screen.selected_covenant.name == "Fengheld"
        tree = app.screen.query_one("#nav-tree", Tree)
        # The new covenant, the Region, the Bestiary, Conflicts, then Seasons,
        # Saga Content and the two stores.
        assert [n.data[0] for n in tree.root.children] == [
            "covenant",
            "region",
            "bestiary",
            "conflicts",
            "seasons",
            "saga_content",
            "armarium",
            "custodia",
        ]

    saga = storage.load_saga("test_saga")
    assert len(saga.covenants) == 1
    covenant = saga.covenants[0]
    assert covenant.name == "Fengheld"
    assert covenant.notes == "A border covenant"
    assert covenant.id == "fengheld"


async def test_create_character_at_saga_level_is_unassigned_and_selectable():
    storage.save_saga(Saga(id="test_saga", name="Test Saga", storyguide="Alex"))

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_workspace(pilot)
        assert app.screen.selected_kind == "saga"

        await menu(pilot, app, "n", "New Character")
        await pilot.pause()
        assert _is_form(app.screen, "Create a New Character")
        # No covenant is selected, so the dialog defaults to none.
        assert app.screen.query_one("#fld-covenant_id", Select).value == Select.NULL
        app.screen.query_one("#fld-name", Input).value = "Wandering Grog"
        app.screen.query_one("#fld-type", Select).value = "grog"
        await click_when_shown(pilot, "#btn-save")
        await pilot.pause()
        await close_worksheet(pilot, app)

        # Listed under the saga, and selectable from the tree.
        tree = app.screen.query_one("#nav-tree", Tree)
        assert _find_node(tree, ("character_group", None)) is not None
        await _select(pilot, app, ("character", "wandering_grog"))
        assert app.screen.selected_character.name == "Wandering Grog"
        assert app.screen.selected_covenant is None

    assert storage.load_saga("test_saga").characters[0].covenant_id is None


async def test_edit_saga_saves_name_storyguide_and_description():
    storage.save_saga(Saga(id="test_saga", name="Test Saga", storyguide="Alex"))

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_workspace(pilot)
        assert app.screen.selected_kind == "saga"

        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Saga")
        dialog = app.screen
        dialog.query_one("#fld-name", Input).value = "Dammerstein [Solo]"
        dialog.query_one("#fld-storyguide", Input).value = "Robin"
        dialog.query_one("#fld-description", Input).value = "A one-magus saga."
        dialog.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

        # Header and tree pick up the rename, brackets escaped.
        assert app.screen.sub_title.startswith(r"Dammerstein \[Solo]")
        tree = app.screen.query_one("#nav-tree", Tree)
        assert str(tree.root.label) == "Dammerstein [Solo]"  # brackets survive, literal
        # The saga detail panel too (re-shown after saving).
        panel = app.screen.query_one("#detail-pane").query_one(Static)
        assert "Dammerstein [Solo]" in str(panel.render())

    saga = storage.load_saga("test_saga")
    assert (saga.name, saga.storyguide, saga.description) == (
        "Dammerstein [Solo]",
        "Robin",
        "A one-magus saga.",
    )


async def test_create_character_defaults_to_current_covenant():
    storage.save_saga(_saga_with_empty_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)

        await menu(pilot, app, "n", "New Character")
        await pilot.pause()
        assert _is_form(app.screen, "Create a New Character")

        app.screen.query_one("#fld-name", Input).value = "Leandro"

        await click_when_shown(pilot, "#btn-save")
        await pilot.pause()
        await close_worksheet(pilot, app)

        assert isinstance(app.screen, WorkspaceScreen)
        assert app.screen.selected_character is not None
        assert app.screen.selected_character.name == "Leandro"

    saga = storage.load_saga("test_saga")
    assert len(saga.characters) == 1
    character = saga.characters[0]
    assert character.name == "Leandro"
    assert character.type == "magus"
    assert character.covenant_id == "cov1"


async def test_selecting_covenant_shows_summary_and_tree_children():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)

        assert app.screen.selected_covenant.id == "cov1"
        view = app.screen._covenant_sheet_view
        assert view is not None
        assert view.query_one("#section-cov-info", Collapsible).title == (
            "Test Covenant"
        )
        assert "A nice place" in view._description_text()
        assert view._pos_rows("vis_store") == [
            (0, "Ignem Vis           Ignem          5")
        ]

        tree = app.screen.query_one("#nav-tree", Tree)
        assert _find_node(tree, ("character_group", "cov1")) is not None
        assert _find_node(tree, ("laboratory_group", "cov1")) is not None
        # No Library node: a covenant's library lives on its sheet's Library tab.
        assert _find_node(tree, ("library", "cov1")) is None
        assert _find_node(tree, ("character", "char1")) is not None
        assert _find_node(tree, ("laboratory", "lab1")) is not None


async def test_selecting_character_shows_sheet_fields():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)

        view = app.screen._character_sheet_view
        # Leandro has no player: the storyguide sees him marked known (👁).
        assert view.query_one("#section-char-info", Collapsible).title == "Leandro 👁"
        assert "Test Covenant" in view._info_right_text()
        assert "Leandro's Sanctum" in view._info_right_text()
        assert "Int: +3" in view._characteristics_text()
        labels = _ability_labels(view)
        assert "Magic Theory (Lab Totals) 5 75/105" in labels
        assert "Academic" in [  # the first header also names the columns
            _plain(label).removesuffix(" Score XP")
            for index, label in view._ability_rows()
            if index is None
        ]
        assert "Affinity with Creo" in _character_vf_labels(view)
        creo_row = view._art_row_label("Creo")
        assert "Creo (Cr)" in creo_row and "10" in creo_row and "55" in creo_row
        assert "Ball of Abysmal Flame" in _known_spell_labels(view)
