"""Lists that share a details panel have one choice between them: choosing
a row in one unchooses the others (Virtues/Flaws, Boons/Hooks, and each of
the covenant's Inhabitants, Possessions and Economics tabs)."""

import pytest
from support import NODES, build_all_tabs, everything_saga, first_vf, wait_until
from textual.widgets import Tree

from ars_magica_manager import storage
from ars_magica_manager.models import (
    INHABITANT_KINDS,
    POSSESSION_KINDS,
    VirtueFlawInstance,
)
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import SelectableList, WorkspaceScreen

GROUPS: dict[str, list[list[str]]] = {
    "character": [["vf-virtues-list", "vf-flaws-list"]],
    "familiar": [["fam-vf-virtues-list", "fam-vf-flaws-list"]],
    "covenant": [
        ["cov-boons-list", "cov-hooks-list"],
        [f"inh-{kind}-list" for kind in INHABITANT_KINDS],
        [f"pos-{kind}-list" for kind in POSSESSION_KINDS],
        ["eco-income-list", "eco-expenditure-list", "eco-savings-list"],
    ],
}


def _choose_first(rows: SelectableList) -> bool:
    """Choose the list's first real row, as arrow keys would; False if it
    has none."""
    for position, option in enumerate(rows.options):
        if option.id is not None:
            rows.highlighted = position
            return True
    return False


@pytest.mark.parametrize(
    ("node", "group"),
    [(node, i) for node, groups in GROUPS.items() for i in range(len(groups))],
)
async def test_choosing_in_one_list_unchooses_its_group(node, group):
    saga = everything_saga()
    # The fixture's familiar has a Virtue only: give it a Flaw too.
    saga.familiars[0].virtues_flaws.append(VirtueFlawInstance(first_vf("Flaw")))
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await pilot.press("enter")
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
        assert await wait_until(
            pilot, lambda: workspace._current_sheet_view() is not None
        )
        view = workspace._current_sheet_view()
        await build_all_tabs(pilot, view)
        lists = [view.query_one(f"#{i}", SelectableList) for i in GROUPS[node][group]]
        populated = [rows for rows in lists if any(o.id for o in rows.options)]
        assert len(populated) >= 2  # the fixture fills at least two of them
        chosen: SelectableList | None = None
        for rows in populated:
            assert _choose_first(rows)
            assert await wait_until(
                pilot, lambda rows=rows: rows.selected_data_index is not None
            )
            await pilot.pause()
            if chosen is not None:
                assert chosen.selected_data_index is None, (chosen.id, rows.id)
            others = [
                r.id
                for r in lists
                if r is not rows and r.selected_data_index is not None
            ]
            assert others == []
            chosen = rows
