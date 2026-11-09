"""The seat: who is sitting at this copy of the app, and what that allows.

A front-end seats someone once, when a saga opens (`sign_in`), and again
when the storyguide turns Player view on or off; every menu, button and
save then asks the same three things, so no screen decides for itself:

- what may be read (viewing.use, set here);
- whether an action may run on the record on show (`may_act`);
- what a save keeps (storage.guard, set here: the last check in front of
  the file, which takes back what the player may not change).

Pattern: Facade over viewing (reads), players (changes) and storage (saves)
for the front-ends, which the terminal and the desktop share. The storyguide's
own window is seated with no player."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from . import players, storage, viewing
from .models import Player, Saga


def runs_the_saga(player: Player | None) -> bool:
    """Whether this seat is the storyguide's: the storyguide's own window
    (no player) or a copy signed in as a storyguide."""
    return player is None or player.role == players.STORYGUIDE


def sign_in(
    saga: Saga,
    player: Player | None,
    *,
    player_view: bool = False,
    on_refused: Callable[[list[str]], None] | None = None,
    hosts: bool = True,
) -> None:
    """Seat `player` (None: the storyguide's own window) at `saga`. With
    `player_view`, the storyguide's own window shows what the table sees.
    `on_refused` is told what a save took back from a player. `hosts`:
    whether this copy is the host's (not one joined from a Remote seat)."""
    viewing.use(viewing.viewer_for(player, player_view=player_view, hosts=hosts), saga)
    storage.saved_by = player.name if player is not None else ""
    if runs_the_saga(player):
        storage.guard = None
        return

    def guard(
        before: dict[str, Any], after: dict[str, Any]
    ) -> tuple[dict[str, Any], list[str]]:
        kept, refused = players.guard_changes(player, before, after)
        if refused and on_refused is not None:
            on_refused(refused)
        return kept, refused

    storage.guard = guard


def sign_out() -> None:
    """Empty the seat: the saga closed, or the player signed out."""
    global _on_show
    storage.guard = None
    storage.saved_by = ""
    _on_show = None
    viewing.use(viewing.STORYGUIDE_VIEWER)


# -- the record on show --

#: The saga and the record the page on show is of (None: the saga's own
#: pages), set by the front-end each time it builds a page.
_on_show: tuple[Saga, Any] | None = None


def show(saga: Saga, record: Any = None) -> None:
    """Note the record the page being built is of (None: a page of the
    saga itself), for `read_only`."""
    global _on_show
    _on_show = (saga, record)


def read_only() -> bool:
    """Whether the page on show is one whoever sits here may not change: a
    page draws no Add, Edit or Delete for it, whatever its sections hold."""
    return _on_show is not None and not may_change(*_on_show)


def may_change(saga: Saga, record: Any = None) -> bool:
    """Whether whoever sits in this copy may change `record` (None: the
    saga itself)."""
    player = viewing.current().player
    return runs_the_saga(player) or players.may_change(saga, player, record)


def may_act(saga: Saga, player: Player | None, action: str, record: Any = None) -> bool:
    """Whether the seat's `player` may run `action` on `record` (the record
    on show; None: the whole saga). The storyguide anything; a player moves
    around and reads anywhere (viewing.LOOKING_ACTIONS) and otherwise only
    what their copy offers and players.may_change lets them change."""
    if runs_the_saga(player):
        # All but what only the host's own copy does (viewing.HOST_ONLY_ACTIONS).
        return viewing.may_do(viewing.current(), action)
    if not viewing.may_do(viewing.current(), action):
        return False
    return viewing.is_looking(action) or players.may_change(saga, player, record)
