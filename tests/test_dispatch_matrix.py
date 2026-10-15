"""Golden test of WorkspaceScreen's key dispatch.

For every section (Collapsible) and tab of every kind of sheet, focus it,
press each section-dispatched key (a, e, d, More and Filter) and record what happens: whether the
binding is enabled, and which dialog opens (with its title) or which
notice appears. The result is compared with tests/golden/dispatch_matrix.json,
so a refactor of the dispatch/routing code that changes any of it fails
here. After an intended change, regenerate the file with

    UPDATE_GOLDEN=1 uv run pytest -p no:xdist tests/test_dispatch_matrix.py

(serially: each kind rewrites its own entry in the one file) and review
the diff.
"""

import asyncio
import json
import os
from pathlib import Path

import pytest
from rich.text import Text
from support import NODES, build_all_tabs, everything_saga, wait_until
from textual.widgets import Collapsible, TabbedContent, TabPane, Tree

from ars_magica_manager import storage
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import ConfirmScreen, FieldsDialog, WorkspaceScreen
from ars_magica_manager.tui.screens.prompts import MenuScreen
from ars_magica_manager.tui.screens.widgets import first_stop, section_stop

GOLDEN = Path(__file__).parent / "golden" / "dispatch_matrix.json"

#: The keys whose action depends on the active section (see
#: WorkspaceScreen.check_action). The action names bound to each key, for
#: check_action: a key is enabled where any of them is.
KEYS: dict[str, tuple[str, ...]] = {
    "a": ("add",),
    "e": ("edit",),
    "d": ("delete",),
    "m": ("more",),
    "slash": ("filter",),
}

_SHEET_VIEW_ATTR = {
    "covenant": "_covenant_sheet_view",
    "character": "_character_sheet_view",
    "laboratory": "_laboratory_sheet_view",
    "familiar": "_familiar_sheet_view",
    "saga_content": "_saga_content_view",
    "sketch_covenant": "_covenant_sheet_view",
    "tribunal": "_tribunal_sheet_view",
    "theban_tribunal": "_tribunal_sheet_view",
    "normandy_tribunal": "_tribunal_sheet_view",
    "region": "_region_sheet_view",
    "neighbour": "_neighbour_sheet_view",
    "town": "_neighbour_sheet_view",
    "church": "_neighbour_sheet_view",
    "university": "_neighbour_sheet_view",
    "faction": "_neighbour_sheet_view",
    "threat": "_neighbour_sheet_view",
    "place": "_neighbour_sheet_view",
    "seasons": "_seasons_view",
}


#: Dialogs recorded without being shown: their title is known before they
#: mount, and building them is most of this test's time. Every other screen
#: (pickers, menus) is shown, as a user would see it.
_SPIED = (FieldsDialog, ConfirmScreen)


def _title(screen) -> str:
    """The text of a dialog's first Label/Static whose id mentions "title";
    for the More menu, what it offers."""
    if isinstance(screen, FieldsDialog):
        return Text.from_markup(screen.title_text).plain.strip()
    if isinstance(screen, ConfirmScreen):
        return ""
    if isinstance(screen, MenuScreen):
        return ", ".join(label for _, _, label in screen.items)
    for widget in screen.query("Label, Static"):
        if widget.id and "title" in widget.id:
            return str(widget.render()).strip()
    return ""


async def _back_to_workspace(pilot, app, workspace) -> None:
    for _ in range(6):
        if app.screen is workspace:
            return
        await pilot.press("escape")
        await pilot.pause()
    assert app.screen is workspace, f"stuck on {type(app.screen).__name__}"


def _label(target) -> str:
    """A target's name in the golden file (a tab built on first visit is
    still a TabPane there)."""
    kind = "TabPane" if isinstance(target, TabPane) else type(target).__name__
    return f"{kind}#{target.id}"


async def _focus_target(pilot, app, view, target) -> None:
    """Make `target` (a Collapsible or TabPane of `view`) the active section
    the way a user would: show its tab, then focus the section (its list,
    or its title if it has none) or the tab's own list."""
    app.screen.set_focus(None)
    await pilot.pause()
    pane = (
        target
        if isinstance(target, TabPane)
        else next((a for a in target.ancestors if isinstance(a, TabPane)), None)
    )
    if pane is not None:
        view.query_one(TabbedContent).active = pane.id
        await pilot.pause()
    if isinstance(target, Collapsible):
        section_stop(target).focus()
        await wait_until(pilot, lambda: app.screen._active_section() == target.id)
    else:
        stop = first_stop(target)
        if stop is None:
            app.screen.set_focus(None)
        else:
            stop.focus()
        await pilot.pause()


def _spy_on_dialogs(app, spied: list) -> None:
    """Record, instead of showing, each _SPIED dialog the app is asked to
    push: what opens is the outcome, and every dialog is cancelled anyway."""
    push_screen = app.push_screen

    def record(screen, *args, **kwargs):
        if not isinstance(screen, _SPIED):
            return push_screen(screen, *args, **kwargs)
        spied.append(screen)
        done = asyncio.get_running_loop().create_future()
        if not kwargs.get("wait_for_dismiss"):
            done.set_result(None)
        return done  # waiting for a dismissal: never comes, like a cancel

    app.push_screen = record


async def _record_keys(
    pilot, app, workspace, notices: list[str], spied: list
) -> dict[str, str]:
    outcomes: dict[str, str] = {}
    for key, actions in KEYS.items():
        if not any(workspace.check_action(action, ()) for action in actions):
            outcomes[key] = "(disabled)"
            continue
        notices.clear()
        spied.clear()
        await pilot.press(key)
        await pilot.pause()
        await wait_until(
            pilot,
            lambda: app.screen is not workspace or notices or spied,
            timeout=1.0,
        )
        if spied and app.screen is workspace:
            title = _title(spied[0])
            outcomes[key] = type(spied[0]).__name__ + (f": {title}" if title else "")
        elif app.screen is not workspace:
            screen = app.screen
            title = _title(screen)
            outcomes[key] = type(screen).__name__ + (f": {title}" if title else "")
            await _back_to_workspace(pilot, app, workspace)
        elif notices:
            outcomes[key] = f"notice: {notices[0]}"
        else:
            outcomes[key] = "(nothing)"
    return outcomes


async def _matrix_for(
    kind: str, shard: int | None = None, shards: int = 1
) -> tuple[dict[str, dict], list[str]]:
    """The recorded outcomes for `kind` -- only every `shards`-th target,
    starting at `shard`, unless `shard` is None -- plus the labels of all
    of the sheet's targets."""
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    notices: list[str] = []
    spied: list = []
    async with app.run_test(size=(140, 70)) as pilot:
        await pilot.press("enter")  # picker -> workspace
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        workspace = app.screen
        original_notify = app.notify

        def record(message, *args, **kwargs):
            notices.append(str(message))
            return original_notify(message, *args, **kwargs)

        app.notify = record  # type: ignore[method-assign]
        _spy_on_dialogs(app, spied)

        tree = workspace.query_one("#nav-tree", Tree)

        def find_node():
            stack = [tree.root]
            while stack:
                candidate = stack.pop()
                if candidate.data == NODES[kind]:
                    return candidate
                stack.extend(candidate.children)
            return None

        # The tree is built as the workspace mounts: wait for the node.
        assert await wait_until(pilot, lambda: find_node() is not None)
        node = find_node()
        tree.select_node(node)
        await pilot.pause()

        attr = _SHEET_VIEW_ATTR.get(kind)
        if attr is None:  # no sheet: the node itself decides the section
            record = {
                "active": workspace._active_section(),
                "keys": await _record_keys(pilot, app, workspace, notices, spied),
            }
            return {"(node)": record}, ["(node)"]

        assert await wait_until(pilot, lambda: getattr(workspace, attr) is not None)
        view = getattr(workspace, attr)
        await build_all_tabs(pilot, view)
        # Every section, and every tab without sections. (Switching to a tab
        # that has sections focuses its first one -- that section's own
        # entry covers it, and which focus lands last would be a race.)
        targets = [
            w
            for w in view.query("Collapsible, TabPane")
            if w.id and not (isinstance(w, TabPane) and w.query(Collapsible))
        ]
        labels = [_label(t) for t in targets]
        if shard is not None:
            targets = targets[shard::shards]
        result: dict[str, dict] = {}
        for target in targets:
            await _focus_target(pilot, app, view, target)
            result[_label(target)] = {
                "active": workspace._active_section(),
                "keys": await _record_keys(pilot, app, workspace, notices, spied),
            }
        return result, labels


def _golden() -> dict:
    if not GOLDEN.exists():
        return {}
    return json.loads(GOLDEN.read_text(encoding="utf-8"))


#: Each sheet's targets are split across this many tests, so that parallel
#: workers share the long ones. Targets are independent: every dialog a key
#: opens is cancelled, so nothing in the saga changes.
SHARDS: dict[str, int] = {"covenant": 6, "character": 4, "familiar": 3, "laboratory": 2}


@pytest.mark.parametrize(
    ("kind", "shard"),
    [(kind, shard) for kind in NODES for shard in range(SHARDS.get(kind, 1))],
)
async def test_dispatch_matrix(kind, shard):
    shards = SHARDS.get(kind, 1)
    if os.environ.get("UPDATE_GOLDEN"):
        if shard:
            pytest.skip("regenerating: shard 0 records the whole sheet")
        matrix, _ = await _matrix_for(kind)
        golden = _golden() | {kind: matrix}
        GOLDEN.parent.mkdir(exist_ok=True)
        GOLDEN.write_text(
            json.dumps(golden, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        return
    matrix, labels = await _matrix_for(kind, shard, shards)
    expected = _golden()[kind]
    assert labels == list(expected)  # same sections and tabs, in the same order
    assert matrix == {label: expected[label] for label in labels[shard::shards]}
