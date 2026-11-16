"""The workspace's settled signal: a view shown from the tree settles once
its first focus has landed (CONTRIBUTING.md "Settled and closed")."""

from __future__ import annotations

from support import NODES, everything_saga, settled, wait_until
from textual.message import Message
from textual.widgets import Tree

from ars_magica_manager import storage
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import WorkspaceScreen
from ars_magica_manager.tui.screens.workspace.base import WorkspaceBase


def _node(tree: Tree, data: tuple):
    pending = [tree.root]
    while pending:
        node = pending.pop()
        if node.data == data:
            return node
        pending.extend(node.children)
    return None


async def test_a_view_settles_once_its_first_focus_has_landed() -> None:
    storage.save_saga(everything_saga())
    announced: list[Message] = []

    def hook(message: Message) -> None:
        if isinstance(message, WorkspaceBase.DetailSettled):
            announced.append(message)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60), message_hook=hook) as pilot:
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        workspace = app.screen
        assert isinstance(workspace, WorkspaceScreen)
        tree = workspace.query_one(Tree)
        for kind in ("custodia", "covenant"):  # a store, then a tabbed sheet
            data = NODES[kind]
            assert await wait_until(pilot, lambda data=data: _node(tree, data))
            before = len(announced)
            tree.select_node(_node(tree, data))
            assert await wait_until(
                pilot, lambda data=data: workspace.selected_kind == data[0]
            )
            await settled(pilot, workspace)
            # Settled means its first focus is in place: a / e / d act there.
            assert workspace.app.focused is not None
            assert workspace._active_section() is not None
            await pilot.pause()
            assert len(announced) == before + 1  # announced once per view
