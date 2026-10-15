"""Characterization snapshot of what every sheet shows.

For each tree node of the one-of-everything saga (support.everything_saga),
show every tab of its detail pane at two terminal sizes, check its details
panel, and record the pane's rendered text. The result is compared with
tests/golden/sheet_text/<node>-<W>x<H>.txt, so a refactor of the sheet
views (compose, refresh, CSS, shared widgets) that changes what is on
screen fails here. Each sheet is then refreshed section by section and
must still show exactly the same text. After an intended change,
regenerate the files with

    UPDATE_GOLDEN=1 uv run pytest tests/test_sheet_text.py

and review the diff.
"""

import difflib
import os
from collections.abc import Callable
from dataclasses import fields, is_dataclass
from pathlib import Path

import pytest
from support import NODES, everything_saga, screen_lines, wait_until
from textual.widgets import TabbedContent, TabPane, Tree

from ars_magica_manager import storage
from ars_magica_manager.models import Saga
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import WorkspaceScreen
from ars_magica_manager.tui.screens.widgets import (
    DETAILS_PANEL_MAX_HEIGHT,
    DETAILS_PANEL_MIN_HEIGHT,
    DetailsPanel,
)

GOLDEN_DIR = Path(__file__).parent / "golden" / "sheet_text"

SIZES = [(140, 70), (120, 45)]

#: The nodes that show a sheet view (the others show a list or a summary).
SHEETS = {
    "covenant",
    "character",
    "laboratory",
    "familiar",
    "sketch_covenant",
    "tribunal",
    "theban_tribunal",
    "normandy_tribunal",
    "region",
    "neighbour",
    "town",
    "church",
    "university",
    "faction",
}


async def _settle(pilot) -> None:
    await pilot.pause()
    await pilot.wait_for_scheduled_animations()
    await pilot.pause()


def _pane_text(app, workspace) -> list[str]:
    """The detail pane's rendered lines (right-trimmed). The active tab's
    underline is drawn as plain rule: its half-cell ends move with an
    animation whose end state isn't reliably reached under load."""
    region = workspace._detail_pane().region
    return [
        line[region.x : region.right].rstrip().translate(_UNDERLINE)
        for line in screen_lines(app)[region.y : region.bottom]
    ]


_UNDERLINE = str.maketrans({"╸": "━", "╺": "━"})


def _check_details_panel(app, pane, tab: TabPane | None, where: str) -> None:
    """One details panel per tab (or list), at the bottom of its tab below
    the part that scrolls. It fits its text, so with nothing chosen (focus
    is kept out of the sheet) it is the minimum, one line of hint plus its
    padding."""
    panels = list((tab or pane).query(DetailsPanel))
    assert len(panels) <= 1, where
    # A list outside a sheet (books, spells) takes focus and chooses a row;
    # a sheet's sections don't (see _open_node).
    chosen = app.focused is not None and pane in app.focused.ancestors
    for panel in panels:
        if chosen:
            height = panel.region.height
            assert DETAILS_PANEL_MIN_HEIGHT <= height, where
            assert height <= DETAILS_PANEL_MAX_HEIGHT, where
        else:
            assert panel.region.height == DETAILS_PANEL_MIN_HEIGHT, where
        assert panel.region.bottom == panel.parent.region.bottom, where
        assert panel is panel.parent.children[-1], where


async def _all_tabs(pilot, app, workspace, check_panels: bool = False) -> list[str]:
    """Every tab's text, each under a "===== <tab id>" line; with
    `check_panels`, each tab's details panel is checked on the way."""
    pane = workspace._detail_pane()
    tabbed = next(iter(pane.query(TabbedContent)), None)
    if tabbed is None:
        await _settle(pilot)
        if check_panels:
            _check_details_panel(app, pane, None, "(no tabs)")
        return ["===== (no tabs)", *_pane_text(app, workspace)]
    lines: list[str] = []
    for tab in tabbed.query(TabPane):
        app.screen.set_focus(None)
        tabbed.active = tab.id
        await wait_until(pilot, lambda tab=tab: tabbed.active == tab.id)
        await _settle(pilot)
        if check_panels:
            _check_details_panel(app, pane, tab, tab.id)
        lines += [f"===== {tab.id}", *_pane_text(app, workspace)]
    return lines


async def _open_node(pilot, app, node: str) -> WorkspaceScreen:
    """From the saga picker, open `node` in the workspace and let it
    settle."""
    await pilot.press("enter")  # picker -> workspace
    assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
    workspace = app.screen
    # What a sheet shows, not where focus is: opening a sheet or a tab moves
    # focus into a section or list, which chooses a row, fills the details
    # panel and can scroll. Keep focus out of the sheet while it is walked.
    workspace._focus_first_section = lambda *, initial=False: None
    tree = workspace.query_one(Tree)

    def find_node():
        stack = [tree.root]
        while stack:
            candidate = stack.pop()
            if candidate.data == NODES[node]:
                return candidate
            stack.extend(candidate.children)
        return None

    assert await wait_until(pilot, lambda: find_node() is not None)
    tree.select_node(find_node())
    assert await wait_until(pilot, lambda: workspace.selected_kind == NODES[node][0])
    # selected_kind changes before the sheet is mounted and recorded.
    if node in SHEETS:
        assert await wait_until(
            pilot, lambda: workspace._current_sheet_view() is not None
        )
    view = workspace._current_sheet_view()
    if view is not None:
        assert await wait_until(pilot, lambda: view.initial_tab_seen)
    await _settle(pilot)
    return workspace


async def _snapshot(
    node: str,
    size: tuple[int, int],
    saga: Saga | None = None,
    change: Callable[[Saga], None] | None = None,
) -> tuple[str, str | None]:
    """The node's text as first shown, and (for a sheet) after `change`
    (if any) is made to the open saga and every section and tab id is
    refreshed. The saga shown is `saga`, by default everything_saga(), whose
    details panels are checked as it is first shown."""
    storage.save_saga(saga if saga is not None else everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=size) as pilot:
        workspace = await _open_node(pilot, app, node)
        view = workspace._current_sheet_view()
        shown = "\n".join(await _all_tabs(pilot, app, workspace, saga is None)) + "\n"
        if view is None:
            return shown, None
        if change is not None:
            change(workspace.saga)
        for widget in view.query("Collapsible, TabPane"):
            if widget.id:
                view.refresh_section(widget.id)
        await _settle(pilot)
        refreshed = "\n".join(await _all_tabs(pilot, app, workspace)) + "\n"
        assert view is workspace._current_sheet_view()  # not re-mounted
        return shown, refreshed


@pytest.mark.parametrize(
    ("node", "size"), [(node, size) for node in NODES for size in SIZES]
)
async def test_sheet_text(node, size):
    golden = GOLDEN_DIR / f"{node}-{size[0]}x{size[1]}.txt"
    shown, refreshed = await _snapshot(node, size)
    if os.environ.get("UPDATE_GOLDEN"):
        golden.parent.mkdir(parents=True, exist_ok=True)
        golden.write_text(shown, encoding="utf-8")
    assert shown == golden.read_text(encoding="utf-8")
    if refreshed is not None:
        assert refreshed == shown


_RECORD_LISTS = ("covenants", "characters", "laboratories", "familiars")


def _emptied(value):
    """`value` with its lists and dicts emptied (recursing into nested
    records), or `value` itself if it has nothing to empty."""
    if isinstance(value, (list, dict)):
        return type(value)()
    if is_dataclass(value) and not isinstance(value, type):
        for f in fields(value):
            setattr(value, f.name, _emptied(getattr(value, f.name)))
    return value


def _sparse_saga() -> Saga:
    """everything_saga() with the same records (same ids) but every list on
    them empty and every name changed."""
    saga = everything_saga()
    for attr in _RECORD_LISTS:
        for record in getattr(saga, attr):
            for f in fields(record):
                setattr(record, f.name, _emptied(getattr(record, f.name)))
            record.name = "Someone"
    return saga


def _fill(saga: Saga) -> None:
    """Make the records of `saga` (as loaded from _sparse_saga()) hold
    everything_saga()'s data again, in place, as edits through dialogs
    would."""
    full = everything_saga()
    for attr in _RECORD_LISTS:
        by_id = {record.id: record for record in getattr(full, attr)}
        for record in getattr(saga, attr):
            source = by_id[record.id]
            for f in fields(record):
                setattr(record, f.name, getattr(source, f.name))


@pytest.mark.parametrize("node", sorted(SHEETS))
async def test_refresh_shows_changed_data(node):
    """A sheet opened on nearly empty records, then refreshed section by
    section after the records get their full data, shows exactly what a
    sheet composed on the full data shows -- so every widget that shows
    record data is refreshed by some section. Which widgets refresh doesn't
    depend on the terminal size, so one size does."""
    size = SIZES[0]
    golden = GOLDEN_DIR / f"{node}-{size[0]}x{size[1]}.txt"
    _, refreshed = await _snapshot(node, size, _sparse_saga(), _fill)
    assert refreshed is not None
    expected = golden.read_text(encoding="utf-8")
    assert refreshed == expected, _diff(expected, refreshed)


def _diff(expected: str, actual: str | None) -> str:
    return "\n".join(
        difflib.unified_diff(
            expected.splitlines(), (actual or "").splitlines(), lineterm="", n=1
        )
    )
