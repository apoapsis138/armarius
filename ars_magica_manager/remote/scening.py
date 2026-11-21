"""Setting and ending a Scene from a Remote seat (protocol 4;
scene_play.py).

A storyguide's seat sets one of the Session's Scenes with `set_scene`: the
use's id, and whether the table is told its aura. `end_scene` ends the one
playing. The host writes the banner from its own saga, as that seat's
Player; the who-may rule is the host's (table_rules.why_not_lead), so a
player's seat is refused as at the host's own window."""

from __future__ import annotations

import time
from collections.abc import Callable

from .. import chronicle, models, scene_play
from ..models import Saga
from .events import Act, table_verb
from .limits import RateLimiter
from .protocol import Body, Field, MessageSpec, Reply, Session

#: Scenes one seat may set or end in a minute.
SCENES_PER_MINUTE = 30
#: The longest use id a seat may name.
USE_ID_MAX = 64


def _set(
    book: chronicle.Chronicle,
    saga: Saga,
    under_way: models.Session,
    by: str,
    body: Body,
) -> chronicle.Entry:
    call = chronicle.SceneCall(
        str(body["use"]), tell_aura=body.get("tell_aura") is True
    )
    return scene_play.set_scene(book, saga, under_way, call, by=by)


def _end(
    book: chronicle.Chronicle,
    saga: Saga,
    under_way: models.Session,
    by: str,
    _body: Body,
) -> chronicle.Entry:
    return scene_play.end_scene(book, saga, under_way, by=by)


def scene_specs(
    saga_id: str, clock: Callable[[], float] = time.monotonic
) -> list[MessageSpec]:
    """`set_scene` and `end_scene`, for a signed-in seat."""
    limiter = RateLimiter(SCENES_PER_MINUTE, 60.0, clock)

    def verb(act: Act, unsaved: str) -> Callable[[Session, Body], Reply]:
        return table_verb(
            saga_id,
            limiter,
            refused="scene_refused",
            done="scene_moved",
            too_many="Too many Scenes: wait a minute.",
            unsaved=unsaved,
            act=act,
        )

    return [
        MessageSpec(
            "set_scene",
            {
                "use": Field(str, max_length=USE_ID_MAX),
                "tell_aura": Field(bool, required=False),
            },
            verb(_set, "The Scene couldn't be saved."),
        ),
        MessageSpec("end_scene", {}, verb(_end, "The Scene's end couldn't be saved.")),
    ]
