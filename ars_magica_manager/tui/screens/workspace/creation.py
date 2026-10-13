"""WorkspaceScreen's runner for the core's command steps (commands.py),
which the Creation Worksheet's buttons and rows start: each step shown in
the terminal's own dialogs (tui/screens/steps.py), then the saga saved
and everything showing the record redrawn."""

from __future__ import annotations

from collections.abc import Callable

from ....commands import Command
from ..steps import run_steps
from .base import WorkspaceBase


class CreationActions(WorkspaceBase):
    def _run_steps(
        self,
        command: Command,
        *,
        tree: bool = False,
        then: Callable[[], None] | None = None,
    ) -> None:
        """Run `command`'s steps; once the last is answered, save the saga,
        redraw the sheet on show, the book lists and an open worksheet
        (and the tree, if `tree`), show the notes it ended with, then call
        `then`."""

        def done(end: object) -> None:
            self._books_changed()
            view = self._current_sheet_view()
            if view is not None:
                view.refresh_all()
            self._commit(tree=tree)
            if isinstance(end, list) and end:
                self.notify("\n".join(end))
            if then is not None:
                then()

        run_steps(self.app, command, done)
