"""The terminal's Session page: each Session a node under Sessions in the
tree, its page naming it and showing its facts; Open Session's link opens
the same node (tui/screens/sheets/session.py)."""

from __future__ import annotations

from screen_helpers import _find_node, _open_workspace
from support import settled, wait_until
from textual.widgets import Collapsible, Tree

from ars_magica_manager import storage
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.models import Casting, Character, Player, Saga, Session
from ars_magica_manager.sections import SESSION_INFO_SECTION
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import WorkspaceScreen


def _saga() -> Saga:
    saga = Saga(id="fengheld", name="Fengheld")
    saga.players = [Player("ana", "Ana")]
    saga.characters = [Character(id="aelfric", name="Aelfric", type="magus")]
    saga.sessions = [
        Session(
            "s1",
            real_date="2026-11-21",
            coming=["ana"],
            castings=[Casting("ana", "aelfric")],
        ),
        Session("s2"),
    ]
    return saga


async def test_a_session_opens_as_its_own_page_from_the_tree_and_a_link() -> None:
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#saga-list").focus()
        await _open_workspace(pilot)
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        workspace = app.screen
        assert isinstance(workspace, WorkspaceScreen)
        tree = workspace.query_one("#nav-tree", Tree)
        assert _find_node(tree, (NodeKind.SESSION, "s2")) is not None

        assert workspace.action_open_ref("sessions", "s1")
        assert await wait_until(
            pilot,
            lambda: (
                (view := workspace._session_sheet_view) is not None
                and view.session.id == "s1"
            ),
        )
        await settled(pilot, workspace)
        view = workspace._session_sheet_view
        assert view is not None
        title = str(view.query_one(f"#{SESSION_INFO_SECTION}", Collapsible).title)
        assert "Session of 21 Nov 2026" in title and "Planned" in title
        assert "Ana as Aelfric" in view._facts(1)
        assert workspace._available("edit")
