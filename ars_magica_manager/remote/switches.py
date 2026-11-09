"""A storyguide's switch between Playing and their storyguide role, from a
Remote seat, noted in the host's log (ADR 0015).

The switch itself is the seat's own: what the window shows. The host only
writes it down, so each storyguide can see when another looked at the saga
as a storyguide. Only a Storyguide-role seat may say so; anything else gets
the one refusal.

Pattern: one more Command in the member registry's table (protocol.py).
"""

from __future__ import annotations

from .. import players, storage
from . import audit
from .protocol import Body, Field, MessageSpec, Refused, Reply, Session


def switch_specs(saga_id: str, log: audit.AuditLog | None = None) -> list[MessageSpec]:
    """`switched`, for a signed-in storyguide's seat."""

    def switched(session: Session, body: Body) -> Reply:
        try:
            saga = storage.load_saga(saga_id)
        except (OSError, ValueError) as gone:
            raise Refused from gone
        player = players.player_by_id(saga, session.player_id)
        if player is None or player.role != players.STORYGUIDE:
            raise Refused
        if log is not None:
            log.record(
                audit.SWITCHED_TO_PLAYING
                if body["playing"]
                else audit.SWITCHED_TO_STORYGUIDE,
                player_id=session.player_id,
                device_id=session.device_id,
            )
        return Reply("noted")

    return [MessageSpec("switched", {"playing": Field(bool)}, switched)]
