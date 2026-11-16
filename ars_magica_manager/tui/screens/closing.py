"""Screen work that outlives its screen.

A screen's async work (an `on_mount` that awaits, a worker, a callback
queued with `call_after_refresh`) can still be running when the screen is
dismissed or the app quits. Textual removes the screen's widgets while that
work waits its turn, so its next `query_one` raises NoMatches: not a bug in
the screen, only work that has nothing left to fill in.

`OpenAwareScreen.is_open` says whether a screen is still open, and
`while_open` wraps a screen method so that NoMatches raised once its screen
has closed ends the method quietly. NoMatches raised while the screen is
still open is a real bug (a widget id that is wrong or was never composed)
and is raised as before; any other error always is.
"""

from __future__ import annotations

import functools
import inspect
from collections.abc import Callable, Coroutine
from typing import Any, Concatenate, cast, overload

from textual.css.query import NoMatches
from textual.screen import Screen


class OpenAwareScreen[ResultT](Screen[ResultT]):
    """A screen that can say whether it is still open, for `while_open`."""

    @property
    def is_open(self) -> bool:
        """Whether the screen is still open: attached to a running app and
        on its screen stack. A screen covered by a dialog is still open; one
        dismissed, or in an app that is quitting, is not (a quitting app
        removes each screen's widgets while the screen is still on the
        stack, so the app's own running flag is checked too)."""
        return (
            self.is_attached and self.app.is_running and self in self.app.screen_stack
        )


@overload
def while_open[S: OpenAwareScreen[Any], **P, R](
    method: Callable[Concatenate[S, P], Coroutine[Any, Any, R]],
) -> Callable[Concatenate[S, P], Coroutine[Any, Any, R | None]]: ...


@overload
def while_open[S: OpenAwareScreen[Any], **P, R](
    method: Callable[Concatenate[S, P], R],
) -> Callable[Concatenate[S, P], R | None]: ...


def while_open[S: OpenAwareScreen[Any], **P, R](
    method: Callable[Concatenate[S, P], Any],
) -> Callable[Concatenate[S, P], Any]:
    """Run the screen method `method` (sync or async); if it raises
    NoMatches after its screen has closed, return None instead. Only
    NoMatches, and only once the screen is closed, is let go."""
    if inspect.iscoroutinefunction(method):
        run_async = cast(Callable[Concatenate[S, P], Coroutine[Any, Any, R]], method)

        @functools.wraps(method)
        async def run_while_open_async(
            screen: S, *args: P.args, **kwargs: P.kwargs
        ) -> R | None:
            try:
                return await run_async(screen, *args, **kwargs)
            except NoMatches:
                if screen.is_open:
                    raise
                return None

        return run_while_open_async

    @functools.wraps(method)
    def run_while_open(screen: S, *args: P.args, **kwargs: P.kwargs) -> Any:
        try:
            return method(screen, *args, **kwargs)
        except NoMatches:
            if screen.is_open:
                raise
            return None

    return run_while_open
