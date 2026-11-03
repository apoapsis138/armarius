"""How the workspace is driven from the keyboard and the mouse: one Tab stop per
section, a click that focuses before it collapses, the tab numbers, Esc stepping out, a
/ e / d everywhere, the More and New menus, / to filter, and what the footer and the row
above it say."""

from screen_helpers import _show_tab
from support import NODES, everything_saga, menu, screen_lines, wait_until
from textual.widgets import Button, Collapsible, Input, TabbedContent, Tree
from textual.widgets._collapsible import CollapsibleTitle

from ars_magica_manager import storage
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import (
    ConfirmScreen,
    FieldsDialog,
    SagaPickerScreen,
    SelectableList,
    VirtueFlawPickerScreen,
    WorkspaceScreen,
)
from ars_magica_manager.tui.screens.prompts import MenuScreen
from ars_magica_manager.tui.screens.steps import ChooseScreen
from ars_magica_manager.tui.screens.widgets import (
    SheetSection,
    section_of,
)


def _node(tree: Tree, data: tuple):
    stack = [tree.root]
    while stack:
        node = stack.pop()
        if node.data == data:
            return node
        stack.extend(node.children)
    return None


async def _open(pilot, app, kind: str) -> WorkspaceScreen:
    """Open the workspace on everything_saga()'s `kind` node, the way Enter
    on the tree does."""
    await pilot.press("enter")
    assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
    workspace = app.screen
    tree = workspace.query_one("#nav-tree", Tree)
    assert await wait_until(pilot, lambda: _node(tree, NODES[kind]) is not None)
    node = _node(tree, NODES[kind])
    tree.move_cursor(node)
    tree.select_node(node)
    assert await wait_until(pilot, lambda: workspace.selected_kind == kind)
    view = workspace._current_sheet_view()
    if kind in ("character", "covenant", "laboratory", "familiar", "saga_content"):
        assert await wait_until(pilot, lambda: workspace._current_sheet_view())
        view = workspace._current_sheet_view()
        assert await wait_until(pilot, lambda: view.initial_tab_seen)
    await pilot.pause()
    return workspace


def _footer(app) -> str:
    return screen_lines(app)[-1]


def _where(app) -> str:
    return screen_lines(app)[-2]


# -- The focus model ------------------------------------------


async def test_tab_stops_once_per_section_and_never_on_a_button():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app, "character")
        first = app.focused
        stops = []
        for _ in range(30):
            await pilot.press("tab")
            await pilot.pause()
            stops.append(app.focused)
            if app.focused is first:
                break
        assert stops[-1] is first, "Tab never came back round"
        assert not any(isinstance(stop, Button) for stop in stops)
        sections = [
            section.id if (section := section_of(stop)) is not None else stop.id
            for stop in stops
        ]
        # One stop each: the top panel's two sections, the Description tab's
        # nine, and the tree. (It was 19 stops before.)
        assert sections == [
            "section-char-characteristics",
            "section-hermetic-background",
            "section-char-biographical",
            "section-personality-traits",
            "section-reputations",
            "section-connections",
            "section-aging",
            "section-char-constant-effects",
            "section-char-health",
            "nav-tree",
            "section-char-info",
        ]
        assert workspace._active_section() == "section-char-info"


async def test_a_list_section_takes_focus_in_its_list_with_a_row_chosen():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app, "character")
        view = workspace._current_sheet_view()
        traits = view.query_one("#personality-traits-list", SelectableList)
        assert traits.selected_data_index is None  # until it takes focus
        for _ in range(4):
            await pilot.press("tab")
        assert await wait_until(pilot, lambda: app.focused is traits)
        assert await wait_until(pilot, lambda: traits.selected_data_index == 0)
        # A section with no list is focused at its title.
        await pilot.press("shift+tab")
        assert await wait_until(
            pilot, lambda: isinstance(app.focused, CollapsibleTitle)
        )
        assert workspace._active_section() == "section-char-biographical"


async def test_a_click_focuses_a_section_and_a_second_click_collapses_it():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app, "character")
        view = workspace._current_sheet_view()
        section = view.query_one("#section-personality-traits", SheetSection)
        title = section.query_one(CollapsibleTitle)
        traits = view.query_one("#personality-traits-list", SelectableList)
        assert workspace._active_section() == "section-char-info"

        # Not the focused section: the click only focuses it, in its list.
        await pilot.click(title)
        await pilot.pause()
        assert not section.collapsed
        assert await wait_until(pilot, lambda: app.focused is traits)
        assert workspace._active_section() == "section-personality-traits"

        # Now it is: the next click on its title collapses it...
        await pilot.click(title)
        assert await wait_until(pilot, lambda: section.collapsed)
        assert workspace._active_section() == "section-personality-traits"
        assert traits.selected_data_index is None  # no row out of sight

        # ...and the one after opens it again, back in the list.
        await pilot.click(title)
        assert await wait_until(pilot, lambda: not section.collapsed)
        assert await wait_until(pilot, lambda: app.focused is traits)


async def test_a_click_in_a_sections_body_focuses_it():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app, "character")
        view = workspace._current_sheet_view()
        section = view.query_one("#section-char-biographical", Collapsible)
        await pilot.click(section, offset=(8, 4))  # its text, not its title
        assert await wait_until(
            pilot, lambda: workspace._active_section() == "section-char-biographical"
        )
        assert not section.collapsed


async def test_a_click_on_a_sheet_button_leaves_focus_on_its_section():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app, "character")
        view = workspace._current_sheet_view()
        button = view.query_one("#btn-char-characteristics-edit", Button)
        await pilot.click(button)
        # The button still does its job...
        assert await wait_until(pilot, lambda: app.screen is not workspace)
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is workspace)
        # ...but focus went to its section, not the button, so Tab carries
        # on from there.
        assert not isinstance(app.focused, Button)
        assert workspace._active_section() == "section-char-characteristics"
        await pilot.press("tab")
        assert await wait_until(
            pilot,
            lambda: workspace._active_section() == "section-hermetic-background",
        )


async def test_c_collapses_the_focused_section_and_enter_does_not():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app, "character")
        view = workspace._current_sheet_view()
        for _ in range(3):
            await pilot.press("tab")
        assert await wait_until(
            pilot, lambda: workspace._active_section() == "section-char-biographical"
        )
        section = view.query_one("#section-char-biographical", Collapsible)
        await pilot.press("enter")
        await pilot.pause()
        assert not section.collapsed
        await pilot.press("c")
        assert await wait_until(pilot, lambda: section.collapsed)
        await pilot.press("c")
        assert await wait_until(pilot, lambda: not section.collapsed)
        # The top panel can't be collapsed: c isn't offered there.
        await pilot.press("shift+tab", "shift+tab", "shift+tab")
        await pilot.pause()
        assert workspace._active_section() == "section-char-info"
        assert not workspace.check_action("toggle_section", ())


async def test_the_tabs_are_numbered_and_a_number_opens_its_tab():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app, "character")
        view = workspace._current_sheet_view()
        tabbed = view.query_one(TabbedContent)
        strip = next(line for line in screen_lines(app) if "1 Description" in line)
        assert "2 Abilities  3 Virtues & Flaws  4 Religion  5 Hermetic Magic" in strip
        assert "6 Research  7 Rune Magic" in strip

        await pilot.press("3")
        assert await wait_until(pilot, lambda: tabbed.active == "tab-vf")
        # ...and moves into it: its first section, on its first row.
        virtues = view.query_one("#vf-virtues-list", SelectableList)
        assert await wait_until(pilot, lambda: app.focused is virtues)
        assert await wait_until(pilot, lambda: virtues.selected_data_index is not None)
        assert workspace._active_section() == "section-vf-virtues"

        # The number of the open tab moves focus back to its start.
        await pilot.press("tab")
        assert await wait_until(
            pilot, lambda: workspace._active_section() == "section-vf-flaws"
        )
        await pilot.press("3")
        assert await wait_until(pilot, lambda: app.focused is virtues)
        # The tenth tab, Planning, is opened by 0; the eleventh and twelfth
        # (Diary, Secrets) have no number, and a number past the last tab
        # does nothing.
        assert view.tab_ids[9] == "tab-planning" and len(view.tab_ids) == 12
        assert not workspace.check_action("show_tab", (13,))
        await pilot.press("0")
        assert await wait_until(pilot, lambda: tabbed.active == "tab-planning")


async def test_escape_steps_out_from_the_sheet_to_the_tree_to_the_saga_picker():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app, "character")
        tree = workspace.query_one("#nav-tree", Tree)
        assert app.focused is not tree  # Enter moved into the sheet
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.focused is tree)
        assert app.screen is workspace
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: isinstance(app.screen, SagaPickerScreen))


async def test_a_list_tab_moves_into_its_list():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app, "saga_content")
        books = workspace.query_one("#content-books-list", SelectableList)
        assert await wait_until(pilot, lambda: app.focused is books)
        await _show_tab(pilot, workspace.app, "tab-content-spells")
        spells = workspace.query_one("#spell-list", SelectableList)
        assert await wait_until(pilot, lambda: app.focused is spells)
        assert await wait_until(pilot, lambda: spells.selected_data_index is not None)


# -- A / e / d everywhere --------------------------------------


async def test_virtues_and_flaws_use_a_e_and_d_like_any_other_list():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app, "character")
        await _show_tab(pilot, workspace.app, "tab-vf")
        assert workspace._active_section() == "section-vf-virtues"
        footer = _footer(app)
        assert footer.lstrip().startswith("a Add  e Edit  d Delete")
        assert workspace.check_action("edit", ())  # e changes what one names

        await pilot.press("a")
        assert await wait_until(
            pilot, lambda: isinstance(app.screen, VirtueFlawPickerScreen)
        )
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is workspace)

        before = len(workspace.selected_character.virtues_flaws)
        await pilot.press("d")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        assert await wait_until(pilot, lambda: app.screen is workspace)
        assert len(storage.load_saga("test_saga").characters[0].virtues_flaws) == (
            before - 1
        )


async def test_the_keys_that_were_retired_do_nothing():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app, "character")
        await _show_tab(pilot, workspace.app, "tab-vf")
        for key in ("A", "v", "V", "ctrl+d", "r", "i", "u", "s", "x", "I", "T", "F"):
            await pilot.press(key)
            await pilot.pause()
            assert app.screen is workspace, key
        footer = _footer(app)
        for word in ("Remove", "Virtue/Flaw", "New Covenant", "Export", "Import"):
            assert word not in footer


async def test_d_deletes_the_record_from_its_tree_node_or_its_top_panel():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app, "character")
        # On the top panel that names the record.
        assert workspace._active_section() == "section-char-info"
        assert "d Delete Leandro" in _footer(app)
        await pilot.press("d")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        message = str(app.screen.query_one("#confirm-message").render())
        assert message.startswith("Delete Leandro?")
        await pilot.press("n")
        assert await wait_until(pilot, lambda: app.screen is workspace)

        # In one of its sections d is about that section (here, nothing).
        await pilot.press("tab")
        await pilot.pause()
        assert workspace._active_section() == "section-char-characteristics"
        assert not workspace.check_action("delete", ())

        # On its tree node.
        await pilot.press("escape")
        await pilot.pause()
        assert "d Delete Leandro" in _footer(app)
        await pilot.press("delete")  # the unlisted second key for d
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        assert await wait_until(pilot, lambda: app.screen is workspace)
    saved = storage.load_saga("test_saga")
    assert "Leandro" not in [c.name for c in saved.characters]


async def test_d_deletes_the_highlighted_saga_on_the_saga_picker():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await pilot.pause()
        assert "d Delete Saga" in _footer(app)
        await pilot.press("A")  # the old key
        await pilot.pause()
        assert isinstance(app.screen, SagaPickerScreen)
        await pilot.press("d")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        assert await wait_until(pilot, lambda: storage.list_sagas() == [])


# -- More, New and / -------------------------------------------


async def test_new_offers_what_can_be_made_here_and_a_letter_picks_it():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app, "saga")
        assert [item.label for item in workspace._new_items()] == [
            "New Covenant",
            "New Character",
            "New Laboratory",
            "New Tribunal",
            "New Neighbour",
            "New Creature",
        ]  # no Bind Familiar: the only magus has one
        assert "n New " in _footer(app)
        await pilot.press("n")
        assert await wait_until(pilot, lambda: isinstance(app.screen, MenuScreen))
        await pilot.press("l")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        assert app.screen.title_text == "Create a New Laboratory"
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is workspace)

        # Enter picks the highlighted item; Escape closes the menu.
        await pilot.press("n")
        assert await wait_until(pilot, lambda: isinstance(app.screen, MenuScreen))
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        assert app.screen.title_text == "Create a New Covenant"
        await pilot.press("escape")
        await pilot.press("n")
        assert await wait_until(pilot, lambda: isinstance(app.screen, MenuScreen))
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is workspace)


async def test_new_runs_directly_when_only_one_thing_can_be_made():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app, "laboratory")
        assert "n New Laboratory" in _footer(app)
        await pilot.press("n")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        assert app.screen.title_text == "Create a New Laboratory"
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is workspace)
        # The old keys are gone (l is free; c collapses a section).
        await pilot.press("l")
        await pilot.pause()
        assert app.screen is workspace


async def test_more_on_the_saga_offers_import_export_and_set_date():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app, "saga")
        assert [item.label for item in workspace._more_items()] == [
            "Import",
            "Export Saga",
            "Export Pack",
            "Host for Players",
            "Set Date",
        ]
        assert "m More" in _footer(app)
        await menu(pilot, app, "m", "Set Date")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        assert app.screen.title_text == "Set the Saga's Date"
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is workspace)
        await menu(pilot, app, "m", "Import")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ChooseScreen))
        assert app.screen.help_id == "import-data"


async def test_more_on_a_record_offers_export_and_its_mode():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app, "character")
        assert [item.label for item in workspace._more_items()] == [
            "Traditions",
            "Disputatio",
            "Cast a Power",
            "Export",
            "Interests",
            "Update from a File",
            "In Creation / In Play",
            "Demote",
            "Go To",
            # The Byzantine customs, with every book in play.
            "Hermetic Letter",
            "Invoke a Broken Oath",
            "Make Greek Fire",
            "A Mother's Curse",
            # A Gifted character, with Apprentices in play.
            "Turbulence",
            "A Scholar's Career",
            "An Offer to Faerie",
            # The saints, the mystic paths and God's aid are More in the
            # Religion tab's Faith section, not on the record.
            # A certamen duel, for a magus with a rival magus in the saga.
            "Certamen",
        ]
        await menu(pilot, app, "m", "In Creation / In Play")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        message = str(app.screen.query_one("#confirm-message").render())
        assert "back to In Creation" in message
        await pilot.press("y")
        assert await wait_until(pilot, lambda: app.screen is workspace)
        assert storage.load_saga("test_saga").characters[0].in_creation
        # In Creation, More offers the Creation Worksheet too.
        assert "Creation Worksheet" in [item.label for item in workspace._more_items()]

        # Away from the top panel, More is about the section instead.
        await pilot.press("tab")
        await pilot.pause()
        assert not workspace.check_action("more", ())
        assert "m " not in _footer(app).split("n New")[0]


async def test_more_reaches_what_only_a_button_did():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app, "character")
        view = workspace._current_sheet_view()
        view.query_one("#section-char-health", Collapsible).focus_section()
        assert await wait_until(
            pilot, lambda: workspace._active_section() == "section-char-health"
        )
        # Several things to do: More's menu, whose letters run them.
        assert await wait_until(pilot, lambda: "m More" in _footer(app))
        await pilot.press("m")
        assert await wait_until(pilot, lambda: isinstance(app.screen, MenuScreen))
        await pilot.press("f")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        assert "Fatigue" in app.screen.title_text
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is workspace)

        # One thing to do: the footer names it and m runs it.
        view.query_one("#section-hermetic-background", Collapsible).focus_section()
        assert await wait_until(pilot, lambda: "m Lab Texts Read" in _footer(app))


async def test_slash_moves_to_the_spell_search():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app, "saga_content")
        await _show_tab(pilot, workspace.app, "tab-content-spells")
        assert await wait_until(pilot, lambda: "/ Filter" in _footer(app))
        await pilot.press("slash")
        search = workspace.query_one("#spell-search", Input)
        assert await wait_until(pilot, lambda: app.focused is search)
        # Nothing to filter on a sheet with no filtered list.
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app, "character")
        assert not workspace.check_action("filter", ())
        assert "Filter" not in _footer(app)


# -- The footer and the row above it ---------------------------


async def test_the_footer_keeps_focused_actions_left_and_global_ones_right():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app, "character")
        footer = _footer(app)
        left, right = footer.split("▏", 1)
        assert left.split() == ["e", "Edit", "d", "Delete", "Leandro", "m", "More"]
        assert right.split("▏")[0].split() == [
            "n",
            "New",
            "Character",
            "t",
            "Advance",
            "Season",
            "?",
            "Help",
            "esc",
            "Back",
            "q",
            "Quit",
        ]
        # The right side stays put as focus moves; the left follows it.
        await _show_tab(pilot, workspace.app, "tab-vf")
        moved = _footer(app)
        assert moved.split("▏", 1)[1] == footer.split("▏", 1)[1]
        assert moved.split("▏", 1)[0].split() == [
            "a",
            "Add",
            "e",
            "Edit",
            "d",
            "Delete",
            # The Virtues & Flaws section's one rare action.
            "m",
            "Gain",
            "or",
            "Lose",
            "in",
            "Play",
        ]
        # It fits the smallest size the app is checked at.
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await _open(pilot, app, "character")
        footer = _footer(app)
        assert "q Quit" in footer and "palette" in footer


async def test_the_row_above_the_footer_says_where_focus_is():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app, "character")
        # The record's own panel: just the record. The theme sits at the
        # row's right end.
        assert _where(app).split("Theme:")[0].strip() == "Leandro"
        assert _where(app).rstrip().endswith("Theme: Scriptorum")

        await _show_tab(pilot, workspace.app, "tab-vf")
        view = workspace._current_sheet_view()
        virtues = view.query_one("#vf-virtues-list", SelectableList)
        assert await wait_until(pilot, lambda: virtues.chosen_text in _where(app))
        where = _where(app).split("Theme:")[0].strip()
        assert where == (
            f"Leandro  ›  Virtues & Flaws  ›  Virtues  ›  {virtues.chosen_text}"
        )

        # The other list, then the tree: the row follows.
        await pilot.press("tab")
        assert await wait_until(pilot, lambda: "›  Flaws  ›" in _where(app))
        await pilot.press("escape")
        assert await wait_until(
            pilot, lambda: _where(app).split("Theme:")[0].strip() == "Leandro"
        )
