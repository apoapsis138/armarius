"""Performance guards (CLAUDE.md "Performance rules").

Counts, not timings: timings flake under a parallel run. Each guard is a
budget on work that made the app sluggish before.
"""

import pytest
from support import NODES, everything_saga, wait_until
from test_sheet_text import SHEETS, _open_node, _settle
from textual.widgets import TabbedContent, TabPane
from textual.widgets._footer import FooterKey

from ars_magica_manager import storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import DiaryEntry
from ars_magica_manager.screens.sheets import LazyTabPane
from ars_magica_manager.screens.widgets import SelectableList, SplitFooter

#: Footer rebuilds allowed per action (a tab switch, a focus move, an arrow
#: key). A tab switch once rebuilt it 4-6 times.
FOOTER_REBUILDS_PER_ACTION = 1


def _footer(app) -> SplitFooter:
    return app.screen.query_one(SplitFooter)


def _check_footer_current(app, action: str) -> None:
    """The Footer shows exactly the keys the screen has now (a skipped
    rebuild must never leave it stale)."""
    shown = {
        binding.action: enabled
        for binding, enabled in (
            (b, e) for (_, b, e, _) in app.screen.active_bindings.values()
        )
        if binding.show
    }
    in_footer = {
        key.action: not key.disabled
        for key in app.screen.query(FooterKey)
        if key.action != "command_palette"  # ^p, always shown on the right
    }
    assert in_footer == shown, f"stale Footer after {action}"


def _check_rebuilds(app, before: int, action: str) -> None:
    rebuilds = _footer(app).rebuilds - before
    assert rebuilds <= FOOTER_REBUILDS_PER_ACTION, (
        f"{action}: the Footer was rebuilt {rebuilds} times"
    )
    _check_footer_current(app, action)


@pytest.mark.parametrize("node", sorted(SHEETS))
async def test_footer_is_rebuilt_at_most_once_per_action(node):
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open_node(pilot, app, node)
        view = workspace._current_sheet_view()
        assert view is not None
        _check_footer_current(app, "opening the sheet")

        tabbed = view.query_one(TabbedContent)
        panes = list(tabbed.query(TabPane))
        for pane in panes[1:] + panes[:1]:
            before = _footer(app).rebuilds
            tabbed.active = pane.id or ""
            assert await wait_until(pilot, lambda pane=pane: tabbed.active == pane.id)
            await _settle(pilot)
            _check_rebuilds(app, before, f"switching to {pane.id}")

            for title in list(pane.query("CollapsibleTitle"))[:3]:
                before = _footer(app).rebuilds
                title.focus()
                await _settle(pilot)
                _check_rebuilds(app, before, f"focusing a section on {pane.id}")

            lists = [lst for lst in pane.query(SelectableList) if lst.option_count >= 2]
            if lists:
                lists[0].focus()
                await _settle(pilot)
                for _ in range(2):
                    before = _footer(app).rebuilds
                    await pilot.press("down")
                    await _settle(pilot)
                    _check_rebuilds(app, before, f"arrowing down {lists[0].id}")


#: Widgets mounted when each sheet opens (everything_saga). Before
#: Tabs were once all built up front: character 149, covenant 195,
#: familiar 83, laboratory 101. Raise a budget only deliberately.
SHEET_OPEN_WIDGET_BUDGET = {
    "character": 90,
    "covenant": 65,
    "familiar": 65,
    "laboratory": 50,
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
