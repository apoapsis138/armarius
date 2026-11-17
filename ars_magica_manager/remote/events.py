"""The Chronicle sent to Remote seats, and rolls asked from them (protocol 2;
ADRs 0018 and 0019).

A seat opens a second connection used only for events, signs in on it as
on its first, and sends `events_since` once with the number of the last
entry it holds (0 after a restart: a seat keeps entries in memory only).
From then on the host sends a `chronicle` frame down that connection for
each entry of the Session under way that the seat's Player may see, read
from the Chronicle file as it grows (the window writes it too): already
held entries first, then each new one within about a second. The request
connection, and its one-request-one-answer loop, is unchanged.

There is one `chronicle` frame for every kind of entry: its envelope,
with the body as JSON text. A seat that meets a kind it doesn't know
shows that this version can't show it. Who may see an entry is decided
here, at the host: an entry the Player may not see is never sent.

A seat rolls with `roll`: what to roll, never a number. The host rolls it
once (chronicle.free_roll), for a character its Player plays tonight, and
at most ROLLS_PER_MINUTE a minute.

Pattern: Observer. The host's loop for an events connection watches the
Chronicle file and tells the seat of each entry new to it.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from typing import Any

from .. import chronicle, storage
from .limits import RateLimiter
from .protocol import Body, Field, MessageSpec, Reply, Session

#: The reply that turns a connection into an events connection.
EVENTS = "events"
#: One Chronicle entry, sent unasked down an events connection.
CHRONICLE = "chronicle"
#: Rolls one seat may ask for in a minute (other requests have their own
#: limit, Limits.messages_per_window).
ROLLS_PER_MINUTE = 30
#: How often an events connection looks for new entries, in seconds.
EVERY = 1.0
#: The longest body (as JSON text) a frame carries; an entry's body is a
#: few hundred characters, far inside the secure channel's message.
MAX_BODY = 8_000


#: An entry too large to send whole: the seat shows it as one it can't
#: show, rather than a body cut short.
TOO_LARGE = "too-large"

#: Where an events connection stands: the Session it is being sent, and
#: the last entry of it sent ("" and 0: nothing yet).
Cursor = tuple[str, int]


def frame(session_id: str, entry: chronicle.Entry) -> Reply:
    """`entry` as a flat frame. Only who may see it in general (Table,
    Storyguide or Chosen) goes, never the Players chosen."""
    body = json.dumps(entry.body, ensure_ascii=False)
    kind = entry.kind
    if len(body) > MAX_BODY:
        kind, body = TOO_LARGE, "{}"
    return Reply(
        CHRONICLE,
        {
            "session": session_id,
            "number": entry.number,
            "time": entry.time,
            "kind": kind,
            "author": entry.author,
            "audience": entry.audience.to,
            "body": body,
        },
    )


def entry_of(body: Body) -> tuple[str, chronicle.Entry]:
    """A frame's Session and entry, as a seat reads it; ValueError for one
    of the wrong shape (the host may be hostile)."""
    number, inner = body.get("number"), body.get("body")
    texts = [body.get(k) for k in ("session", "time", "kind", "author", "audience")]
    if not isinstance(number, int) or not isinstance(inner, str):
        raise ValueError("A Chronicle entry of the wrong shape.")
    if not all(isinstance(t, str) for t in texts):
        raise ValueError("A Chronicle entry of the wrong shape.")
    session_id, time_, kind, author, audience = (str(t) for t in texts)
    data: Any = json.loads(inner)
    if not isinstance(data, dict):
        raise ValueError("A Chronicle entry's body isn't a record.")
    return session_id, chronicle.Entry(
        number, time_, kind, author, chronicle.Audience(audience), data
    )


def poller(saga_id: str) -> Callable[[str, Cursor], tuple[list[Reply], Cursor]]:
    """For the host's events loop: a Player's frames after `cursor`, and
    where to go on from. The saga is read afresh each time, so a Session
    begun or ended in the window is seen; a file that can't be read just
    now sends nothing this time."""

    def poll(player_id: str, cursor: Cursor) -> tuple[list[Reply], Cursor]:
        session_id, since = cursor
        try:
            saga = storage.load_saga(saga_id)
            if not session_id:
                found_session = chronicle.under_way(saga)
                session_id = found_session.id if found_session is not None else ""
            found = chronicle.feed(saga, player_id, session_id, since)
        except OSError, ValueError:
            return [], cursor
        if found is None:
            return [], cursor
        if found.session_id != cursor[0]:
            since = 0
        frames = [frame(found.session_id, e) for e in found.entries]
        last = found.entries[-1].number if found.entries else since
        return frames, (found.session_id, last)

    return poll


def event_specs(
    saga_id: str, clock: Callable[[], float] = time.monotonic
) -> list[MessageSpec]:
    """`events_since` and `roll`, for a signed-in seat."""
    rolls = RateLimiter(ROLLS_PER_MINUTE, 60.0, clock)

    def events_since(_session: Session, body: Body) -> Reply:
        return Reply(
            EVENTS, {"session": body.get("session", ""), "since": body["since"]}
        )

    def roll(session: Session, body: Body) -> Reply:
        if not rolls.allow(session.device_id or session.player_id):
            return Reply("roll_refused", {"why": "Too many rolls: wait a minute."})
        try:
            saga = storage.load_saga(saga_id)
        except OSError, ValueError:
            return Reply("roll_refused", {"why": "The saga can't be read just now."})
        under_way = chronicle.under_way(saga)
        if under_way is None:
            return Reply("roll_refused", {"why": "No Session is under way."})
        book = chronicle.Chronicle(chronicle.path_of(saga, under_way), [])
        ease = body.get("ease_factor")
        request = chronicle.RollRequest(
            stress=body["die"] == "stress",
            modifier=int(body["modifier"]),
            botch_dice=int(body["botch_dice"]) if body["die"] == "stress" else 0,
            ease_factor=ease if isinstance(ease, int) else None,
            for_what=str(body.get("for", "")),
            character_id=str(body.get("character_id", "")),
            visibility=str(body["visibility"]),
        )
        try:
            entry = chronicle.free_roll(
                book, saga, under_way, request, by=session.player_id
            )
        except ValueError as problem:
            return Reply("roll_refused", {"why": str(problem)[:200]})
        except OSError:
            return Reply("roll_refused", {"why": "The roll couldn't be saved."})
        return Reply("rolled", {"number": entry.number})

    return [
        MessageSpec(
            "events_since",
            {
                "session": Field(str, max_length=64, required=False),
                "since": Field(int, low=0, high=10**6),
            },
            events_since,
        ),
        MessageSpec(
            "roll",
            {
                "die": Field(str, max_length=8),
                "modifier": Field(int, low=-99, high=99),
                "botch_dice": Field(int, low=0, high=10),
                "ease_factor": Field(int, low=0, high=99, required=False),
                "for": Field(str, max_length=120, required=False),
                "character_id": Field(str, max_length=64, required=False),
                "visibility": Field(str, max_length=16),
            },
            roll,
        ),
    ]
