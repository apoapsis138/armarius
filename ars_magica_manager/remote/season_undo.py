"""Undo Last Season from a storyguide's Remote seat (undo_season.py).

The backups are the host's, so the seat only asks: `undo_offer` says what
can be undone (the season it goes back to, the season it is now, and the
records changed since), and `undo_season` does it, on the host's own saga
and backups, with the same checks. Every seat then reads the saga as it is
again. Only a Storyguide-role seat may ask (ADR 0014); anything else gets
the one refusal.

Pattern: two more Commands in the member registry's table (protocol.py).
"""

from __future__ import annotations

from .. import players, storage, undo_season
from ..models import Saga
from . import audit
from .protocol import Body, Field, MessageSpec, Refused, Reply, Session

#: How the changed records travel in one reply.
SEPARATOR = "\n"


def _storyguides_saga(saga_id: str, session: Session) -> tuple[Saga, str]:
    """The host's saga and the seat's player's name, or Refused unless the
    seat is a storyguide's."""
    try:
        saga = storage.load_saga(saga_id)
    except (OSError, ValueError) as gone:
        raise Refused from gone
    player = players.player_by_id(saga, session.player_id)
    if player is None or player.role != players.STORYGUIDE:
        raise Refused
    return saga, player.name


def undo_specs(saga_id: str, log: audit.AuditLog | None = None) -> list[MessageSpec]:
    """`undo_offer` and `undo_season`, for a signed-in storyguide's seat."""

    def offer(session: Session, body: Body) -> Reply:
        saga, _name = _storyguides_saga(saga_id, session)
        found = undo_season.offer(saga)
        if found is None:
            return Reply("no_undo")
        return Reply(
            "undo",
            {
                "back_to": found.back_to,
                "now": found.now,
                "lost": SEPARATOR.join(found.lost)[:4000],
            },
        )

    def undo(session: Session, body: Body) -> Reply:
        saga, name = _storyguides_saga(saga_id, session)
        found = undo_season.offer(saga)
        if found is None or found.now != str(body["now"]):
            return Reply("no_undo")  # gone, or the saga moved meanwhile
        try:
            done = undo_season.undo(saga, found)
        except ValueError:
            raise Refused from None
        storage.save_saga(saga, storage.Saver(name))
        if log is not None:
            log.record(
                audit.SEASON_UNDONE,
                player_id=session.player_id,
                device_id=session.device_id,
            )
        return Reply("undone", {"message": done.message})

    return [
        MessageSpec("undo_offer", {}, offer),
        MessageSpec("undo_season", {"now": Field(str, max_length=40)}, undo),
    ]
