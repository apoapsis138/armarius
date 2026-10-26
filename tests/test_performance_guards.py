"""Performance guards (CLAUDE.md "Performance rules").

Counts, not timings: timings flake under a parallel run. Each guard is a
budget on work that made the app sluggish before. The guard on Footer
rebuilds runs in test_sheet_text, on the same walk through every sheet.
"""

import pytest
from support import NODES, everything_saga, wait_until
from test_sheet_text import SHEETS, _open_node, _settle
from textual.widgets import TabbedContent

from ars_magica_manager import storage
from ars_magica_manager.models import DiaryEntry
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens.sheets import LazyTabPane
from ars_magica_manager.tui.screens.widgets import SelectableList

#: Widgets mounted when each sheet opens (everything_saga). Before
#: Tabs were once all built up front: character 149, covenant 195,
#: familiar 83, laboratory 101. Raise a budget only deliberately.
SHEET_OPEN_WIDGET_BUDGET = {
    "character": 91,  # the Agents tab adds its (unbuilt) pane
    # The Manors and Charter panes (the town charter's sections moved off
    # Attributes onto the Charter tab, unbuilt on opening).
    "covenant": 67,
    "familiar": 65,
    "laboratory": 50,
    # Its Overview tab's Connections section: 2; its Charter tab's
    # (unbuilt) pane: 2.
    "sketch_covenant": 54,
    # Each Tribunal's Secrets tab adds its (unbuilt) pane and its tab: 2.
    "tribunal": 42,
    "theban_tribunal": 42,
    "normandy_tribunal": 44,  # one tab more: History
    "transylvania_tribunal": 42,
    "hibernia_tribunal": 42,
    "region": 50,
    "neighbour": 44,  # a lord's Fief tab lists his sieges too; his Manors tab adds 2
    "town": 40,
    "church": 40,
    "university": 40,
    "faction": 40,
    "threat": 40,
    "place": 40,
    "seasons": 40,
    "bestiary": 30,
    "creature": 50,
}


@pytest.mark.parametrize("node", sorted(SHEETS))
async def test_opening_a_sheet_mounts_only_its_first_tab(node):
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open_node(pilot, app, node)
        view = workspace._current_sheet_view()
        assert view is not None
        mounted = len(list(view.walk_children()))
        assert mounted <= SHEET_OPEN_WIDGET_BUDGET[node], (
            f"opening the {node} sheet mounts {mounted} widgets"
        )
        tabbed = view.query_one(TabbedContent)
        built = [p.id for p in tabbed.query(LazyTabPane) if p.built]
        assert built == [view.INITIAL_TAB]


async def test_a_tab_built_after_a_change_shows_the_change():
    """A tab isn't built until it's shown, so a change made before then
    (its refresh does nothing yet) must show once it is."""
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open_node(pilot, app, "laboratory")
        view = workspace._current_sheet_view()
        assert view is not None
        view.laboratory.diary.append(DiaryEntry(1221, "Winter", "Hidden change"))
        workspace._commit("tab-lab-diary")
        await _settle(pilot)

        tabbed = view.query_one(TabbedContent)
        tabbed.active = "tab-lab-diary"
        assert await wait_until(pilot, lambda: view.query("#lab-diary-list"))
        rows = view.query_one("#lab-diary-list", SelectableList)._rows
        assert any("Hidden change" in label for _, label in rows)


def test_the_guard_covers_every_sheet():
    assert SHEETS <= set(NODES)
    assert SHEETS == set(SHEET_OPEN_WIDGET_BUDGET)
