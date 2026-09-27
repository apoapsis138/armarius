"""Characterization snapshot of what every sheet shows.

For each tree node of the one-of-everything saga (support.everything_saga),
show every tab of its detail pane at two terminal sizes and record the
pane's rendered text. The result is compared with
tests/golden/sheet_text/<node>-<W>x<H>.txt, so a refactor of the sheet
views (compose, refresh, CSS, shared widgets) that changes what is on
screen fails here. Each sheet is then refreshed section by section and
must still show exactly the same text. After an intended change,
regenerate the files with

    UPDATE_GOLDEN=1 uv run pytest tests/test_sheet_text.py

and review the diff.
"""

import os
from pathlib import Path

import pytest
from support import NODES, everything_saga, wait_until
from textual.widgets import TabbedContent, TabPane, Tree

from ars_magica_manager import storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.screens import WorkspaceScreen

GOLDEN_DIR = Path(__file__).parent / "golden" / "sheet_text"

SIZES = [(140, 70), (80, 24)]


async def _settle(pilot) -> None:
    await pilot.pause()
    await pilot.wait_for_scheduled_animations()
    await pilot.pause()


def _pane_text(app, workspace) -> list[str]:
    """The detail pane's rendered lines (right-trimmed)."""
    region = workspace._detail_pane().region
    strips = app.screen._compositor.render_strips()
    return [
        strip.text[region.x : region.right].rstrip()
        for strip in strips[region.y : region.bottom]
    ]


async def _all_tabs(pilot, app, workspace) -> list[str]:
    """Every tab's text, each under a "===== <tab id>" line."""
    pane = workspace._detail_pane()
    tabbed = next(iter(pane.query(TabbedContent)), None)
    if tabbed is None:
        await _settle(pilot)
        return ["===== (no tabs)", *_pane_text(app, workspace)]
    lines: list[str] = []
    for tab in tabbed.query(TabPane):
        app.screen.set_focus(None)
        tabbed.active = tab.id
        await wait_until(pilot, lambda tab=tab: tabbed.active == tab.id)
        await _settle(pilot)
        lines += [f"===== {tab.id}", *_pane_text(app, workspace)]
    return lines


async def _snapshot(node: str, size: tuple[int, int]) -> tuple[str, str | None]:
    """The node's text as first shown, and (for a sheet) after refreshing
    every section and tab id."""
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=size) as pilot:
        await pilot.press("enter")  # picker -> workspace
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        workspace = app.screen
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
        assert await wait_until(pilot, lambda: workspace.selected_kind == node)
        view = workspace._current_sheet_view()
        if view is not None:
            assert await wait_until(pilot, lambda: view.initial_tab_seen)
        await _settle(pilot)
        shown = "\n".join(await _all_tabs(pilot, app, workspace)) + "\n"
        if view is None:
            return shown, None
        for widget in view.query("Collapsible, TabPane"):
            if widget.id:
                view.refresh_section(widget.id)
        await _settle(pilot)
        refreshed = "\n".join(await _all_tabs(pilot, app, workspace)) + "\n"
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
