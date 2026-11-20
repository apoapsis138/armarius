"""Shows from and to Remote seats (protocol 4; shows.py).

A storyguide's seat Shows with `show`: what to show (a record by kind and
id, or a picture already in the saga by folder and name), its title, the
Players shown (none: the Table) and an open story. The host makes the one
copy itself, through the Player view, and writes the entry as that seat's
Player; the who-may rule is the host's (table_rules.why_not_lead).

Any seat opens a Show's copy with `show_copy`, by the Show's id: the host
sends it only while the seat's Player sees the Show's entry, and refuses
any other id as if there were none. A shown picture comes by the picture
request (records.py), in the Show folder, on the same terms.

This module sits a layer above the rest of the listener's messages: the
copy is the record's printed sheet (show_copy.py)."""

from __future__ import annotations

import time
from collections.abc import Callable

from .. import chronicle, models, references, show_copy, shows, storage
from ..models import Saga
from .events import table_verb
from .limits import RateLimiter
from .protocol import Body, Field, MessageSpec, Refused, Reply, Session
from .records import PICTURE_NAME_MAX, in_parts

#: Shows one seat may make in a minute.
SHOWS_PER_MINUTE = 30
#: Show copies one seat may open in a minute: each reads the Chronicles
#: until it finds the Show.
OPENS_PER_MINUTE = 30
#: The longest Show id a seat may ask for.
SHOW_ID_MAX = 64


def _call_of(body: Body) -> chronicle.ShowCall:
    """The Show a seat's `show` asks for (its fields already checked)."""
    kind, record_id = str(body.get("kind", "")), str(body.get("id", ""))
    folder, name = str(body.get("folder", "")), str(body.get("name", ""))
    return chronicle.ShowCall(
        str(body["title"]),
        record=references.Ref(kind, record_id, "") if kind else None,
        picture=(folder, name) if folder else None,
        to=tuple(t for t in str(body.get("to", "")).split("\n") if t),
        story_id=str(body.get("story_id", "")),
    )


def _show(
    book: chronicle.Chronicle,
    saga: Saga,
    under_way: models.Session,
    by: str,
    body: Body,
) -> chronicle.Entry:
    return shows.show(
        book, saga, under_way, _call_of(body), by=by, copier=show_copy.player_copy
    )


def show_specs(
    saga_id: str, clock: Callable[[], float] = time.monotonic
) -> list[MessageSpec]:
    """`show` and `show_copy`, for a signed-in seat."""
    show = table_verb(
        saga_id,
        RateLimiter(SHOWS_PER_MINUTE, 60.0, clock),
        refused="show_refused",
        done="shown",
        too_many="Too many Shows: wait a minute.",
        unsaved="The Show couldn't be saved.",
        act=_show,
    )

    opens = RateLimiter(OPENS_PER_MINUTE, 60.0, clock)

    def copy(session: Session, body: Body) -> Reply:
        show_id = str(body["show"])
        if not opens.allow(session.device_id or session.player_id):
            return Reply(
                "show_refused", {"why": "Too many Shows opened: wait a minute."}
            )
        try:
            saga = storage.load_saga(saga_id)
            if shows.seen(saga, show_id, session.player_id) is None:
                raise Refused
            blob = shows.copy_text(saga_id, show_id)
        except OSError, ValueError:
            raise Refused from None
        return in_parts("show_copy", blob, {"show": show_id})

    return [
        MessageSpec(
            "show",
            {
                "title": Field(str, max_length=200),
                "kind": Field(str, max_length=32, required=False),
                "id": Field(str, max_length=SHOW_ID_MAX, required=False),
                "folder": Field(str, max_length=16, required=False),
                "name": Field(str, max_length=PICTURE_NAME_MAX, required=False),
                "to": Field(str, max_length=2_000, required=False),
                "story_id": Field(str, max_length=SHOW_ID_MAX, required=False),
            },
            show,
        ),
        MessageSpec("show_copy", {"show": Field(str, max_length=SHOW_ID_MAX)}, copy),
    ]
