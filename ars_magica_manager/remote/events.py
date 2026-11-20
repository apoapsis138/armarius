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
here, at the host: an entry the Player may not see is never sent. Each
frame also says whether the entry is for the seat's Player (`for_you`,
ADR 0031), worked out at the host by chronicle.stamped.

A seat rolls with `roll`: what to roll, never a number (from the sheet,
the Characteristic, the Ability and whether a Specialty applies). The host
rolls it once (chronicle.free_roll), for a character its Player plays
tonight, working the sheet's terms out from the saga. `confidence` spends
Confidence on a roll already made (chronicle.spend_confidence), and
`answer` answers a Roll request for a character the seat's Player rolls
for (chronicle.answer). All count toward the seat's ROLLS_PER_MINUTE.

A seat sends a Message with `say` (protocol 4): its words, those it
Whispers to (none: the Table) and the records it links ("kind:id:name",
refused if the host's saga has renamed one since the seat's copy). The host writes it as its Player
(chronicle.message), and like any entry it is sent only to the seats
that may see it. Messages count toward MESSAGES_PER_MINUTE.

A seat's Table roll made from a form (table_rolls.py) works the form's
rule at the seat, but draws each die from the host with `form_die`, one
at a time: the first opens the roll on that connection (the form, the
character, who sees it), the host draws and keeps every face, and
`form_done` closes it with the form's result lines, the host writing the
entry with the faces it drew itself. `form_cancel`, or the connection
closing first, writes the dice drawn as cancelled. Dice count toward the
seat's DICE_PER_MINUTE.

Pattern: Observer. The host's loop for an events connection watches the
Chronicle file and tells the seat of each entry new to it.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from typing import Any

from .. import chronicle, models, references, shapes, storage, table_rolls
from ..models import Saga
from .limits import RateLimiter
from .protocol import Body, Field, MessageSpec, Reply, Session

#: The reply that turns a connection into an events connection.
EVENTS = "events"
#: One Chronicle entry, sent unasked down an events connection.
CHRONICLE = "chronicle"
#: Rolls one seat may ask for in a minute (other requests have their own
#: limit, Limits.messages_per_window).
ROLLS_PER_MINUTE = 30
#: Messages and Whispers one seat may send in a minute.
MESSAGES_PER_MINUTE = 30
#: Dice one seat may draw for form rolls in a minute: a form with stress
#: doublings and botch dice draws several. Kept below a connection's own
#: limit on messages, so the seat is told why rather than cut off.
DICE_PER_MINUTE = 50
#: The longest result a seat sends back for a form roll (its lines,
#: joined by newlines).
MAX_LINES = 2_000
#: How often an events connection looks for new entries, in seconds.
EVERY = 1.0
#: The longest body (as JSON text) a frame carries; an entry's body is a
#: few hundred characters, far inside the secure channel's message.
MAX_BODY = chronicle.ENTRY_LIMIT


#: An entry too large to send whole: the seat shows it as one it can't
#: show, rather than a body cut short.
TOO_LARGE = "too-large"

#: Where an events connection stands: the Session it is being sent, and
#: the last entry of it sent ("" and 0: nothing yet).
Cursor = tuple[str, int]


def frame(session_id: str, entry: chronicle.Entry) -> Reply:
    """`entry` as a flat frame, as chronicle.stamped hands it to a seat.
    Only who may see it in general (Table, Storyguide or Chosen) goes,
    never the Players chosen (a Whisper's body names those it is to by
    name alone, as its card shows them), and whether it is for this
    seat's Player (`for_you`, ADR 0031)."""
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
            "for_you": entry.for_you is True,
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
        number,
        time_,
        kind,
        author,
        chronicle.Audience(audience),
        data,
        for_you=body.get("for_you") is True,
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


def _links(saga: Saga, text: str) -> tuple[references.Ref, ...] | str:
    """The records a seat's Message links ("kind:id:name" a line, the name
    as the seat wrote it), or why one can't be linked: no record of the
    saga, or one renamed on the host since the seat's copy."""
    found: list[references.Ref] = []
    for line in text.split("\n"):
        if not line:
            continue
        kind, _, rest = line.partition(":")
        record_id, _, written = rest.partition(":")
        record = references.find(saga, kind, record_id)
        if record is None:
            return "Link only records you may open."
        if written and written != record.name:
            return f"{written} is now {record.name} on the host: link it again."
        found.append(references.Ref(kind, record_id, record.name))
    return tuple(found)


def _open_form_roll(saga_id: str, session: Session, body: Body) -> table_rolls.HostRoll:
    """A seat's form roll, opened at its first die: the Session under
    way, the form, the character and who sees it, checked as the host's
    own window would (ValueError says why not)."""
    try:
        saga = storage.load_saga(saga_id)
    except OSError, ValueError:
        raise ValueError("The saga can't be read just now.") from None
    under_way = chronicle.under_way(saga)
    if under_way is None:
        raise ValueError("No Session is under way.")
    problem = chronicle.typed_problem(chronicle.FORM_ROLL, {"form": str(body["form"])})
    if problem:
        raise ValueError(problem)
    opening = table_rolls.Opening(
        str(body["form"]), str(body.get("character_id", "")), str(body["visibility"])
    )
    book = chronicle.Chronicle(chronicle.path_of(saga, under_way), [])
    return table_rolls.HostRoll(
        saga, under_way, opening, by=session.player_id, book=book
    )


#: One verb a seat asks the host to do at the table: given the Session's
#: Chronicle, the saga, the Session under way, the seat's Player and what
#: the seat sent, the entry it wrote (ValueError: refused).
Act = Callable[[chronicle.Chronicle, Saga, models.Session, str, Body], chronicle.Entry]


def _at_table(
    saga_id: str,
    limiter: RateLimiter,
    *,
    refused: str,
    done: str,
    too_many: str,
    unsaved: str,
    act: Act,
) -> Callable[[Session, Body], Reply]:
    """A seat's verb at the table, its steps said once: within the seat's
    limit, the saga read afresh, a Session under way, its Chronicle caught
    up, then `act`; its entry's number, or why not (`refused`)."""

    def handle(session: Session, body: Body) -> Reply:
        if not limiter.allow(session.device_id or session.player_id):
            return Reply(refused, {"why": too_many})
        try:
            saga = storage.load_saga(saga_id)
        except OSError, ValueError:
            return Reply(refused, {"why": "The saga can't be read just now."})
        under_way = chronicle.under_way(saga)
        if under_way is None:
            return Reply(refused, {"why": "No Session is under way."})
        # A Chronicle of this thread's own, never the window's open one.
        book = chronicle.Chronicle(chronicle.path_of(saga, under_way), [])
        try:
            book.refresh()
            entry = act(book, saga, under_way, session.player_id, body)
        except ValueError as problem:
            return Reply(refused, {"why": str(problem)[:200]})
        except OSError:
            return Reply(refused, {"why": unsaved})
        return Reply(done, {"number": entry.number})

    return handle


def _request_of(body: Body) -> chronicle.RollRequest:
    """The roll a seat's `roll` asks for (its fields already checked)."""
    ease = body.get("ease_factor")
    characteristic = str(body.get("characteristic", ""))
    sheet = (
        chronicle.SheetRoll(
            characteristic, str(body.get("ability", "")), body.get("specialty") is True
        )
        if characteristic
        else None
    )
    return chronicle.RollRequest(
        stress=body["die"] == "stress",
        modifier=int(body["modifier"]),
        botch_dice=int(body["botch_dice"]) if body["die"] == "stress" else 0,
        ease_factor=ease if isinstance(ease, int) else None,
        for_what=str(body.get("for", "")),
        character_id=str(body.get("character_id", "")),
        visibility=str(body["visibility"]),
        sheet=sheet,
    )


def _roll(
    book: chronicle.Chronicle,
    saga: Saga,
    under_way: models.Session,
    by: str,
    body: Body,
) -> chronicle.Entry:
    return chronicle.free_roll(book, saga, under_way, _request_of(body), by=by)


def _confidence(
    book: chronicle.Chronicle,
    saga: Saga,
    under_way: models.Session,
    by: str,
    body: Body,
) -> chronicle.Entry:
    return chronicle.spend_confidence(
        book, saga, under_way, int(body["roll"]), int(body["points"]), by=by
    )


def _answer(
    book: chronicle.Chronicle,
    saga: Saga,
    under_way: models.Session,
    by: str,
    body: Body,
) -> chronicle.Entry:
    return chronicle.answer(
        book,
        saga,
        under_way,
        int(body["request"]),
        str(body["character_id"]),
        by=by,
        specialty=body.get("specialty") is True,
    )


def _say(
    book: chronicle.Chronicle,
    saga: Saga,
    under_way: models.Session,
    by: str,
    body: Body,
) -> chronicle.Entry:
    to = tuple(t for t in str(body.get("to", "")).split("\n") if t)
    links = _links(saga, str(body.get("links", "")))
    if isinstance(links, str):
        raise ValueError(links)
    return chronicle.message(
        book, saga, under_way, str(body["words"]), to=to, links=links, by=by
    )


def _cancel(session: Session) -> None:
    """Write the dice a seat drew for a form roll it never finished."""
    roll = session.form_roll
    session.form_roll = None
    if isinstance(roll, table_rolls.HostRoll):
        roll.cancel()


def _form_roll_specs(saga_id: str, clock: Callable[[], float]) -> list[MessageSpec]:
    """`form_die`, `form_done` and `form_cancel`: a seat's Table roll made
    from a form, its dice drawn by the host one at a time."""
    dice = RateLimiter(DICE_PER_MINUTE, 60.0, clock)

    def form_die(session: Session, body: Body) -> Reply:
        if not dice.allow(session.device_id or session.player_id):
            return Reply("roll_refused", {"why": "Too many dice: wait a minute."})
        roll = session.form_roll
        if not isinstance(roll, table_rolls.HostRoll):
            try:
                roll = _open_form_roll(saga_id, session, body)
            except ValueError as problem:
                return Reply("roll_refused", {"why": str(problem)[:200]})
            session.form_roll = roll
            session.on_close.append(lambda: _cancel(session))
        start, stop, step = int(body["start"]), int(body["stop"]), int(body["step"])
        try:
            face = roll.dice.randrange(start, stop, step)
        except ValueError:
            return Reply("roll_refused", {"why": "No such die."})
        return Reply("die", {"face": face})

    def form_done(session: Session, body: Body) -> Reply:
        roll = session.form_roll
        if not isinstance(roll, table_rolls.HostRoll) or not roll.faces:
            return Reply("roll_refused", {"why": "No dice were drawn for that roll."})
        session.form_roll = None
        lines = [line for line in str(body.get("lines", "")).split("\n") if line]
        problem = next(
            (said for line in lines if (said := shapes.why_not_words(line))), None
        )
        if problem:
            # Its dice stay in the Chronicle, as drawn, then cancelled.
            roll.cancel()
            return Reply("roll_refused", {"why": problem[:200]})
        refused = roll.finish(lines)
        if refused:
            return Reply("roll_refused", {"why": refused[:200]})
        return Reply("rolled", {"number": roll.number})

    def form_cancel(session: Session, _body: Body) -> Reply:
        _cancel(session)
        return Reply("noted")

    return [
        MessageSpec(
            "form_die",
            {
                "form": Field(str, max_length=120),
                "character_id": Field(str, max_length=64, required=False),
                "visibility": Field(str, max_length=16),
                "start": Field(int, low=-(2**31), high=2**31 - 1),
                "stop": Field(int, low=-(2**31), high=2**31 - 1),
                "step": Field(int, low=-(2**31), high=2**31 - 1),
            },
            form_die,
        ),
        MessageSpec(
            "form_done",
            {"lines": Field(str, max_length=MAX_LINES, required=False)},
            form_done,
        ),
        MessageSpec("form_cancel", {}, form_cancel),
    ]


def _message_specs(saga_id: str, clock: Callable[[], float]) -> list[MessageSpec]:
    """`say`: a Message or Whisper from a seat, written by the host as its
    Player."""
    say = _at_table(
        saga_id,
        RateLimiter(MESSAGES_PER_MINUTE, 60.0, clock),
        refused="message_refused",
        done="said",
        too_many="Too many Messages: wait a minute.",
        unsaved="The Message couldn't be saved.",
        act=_say,
    )

    return [
        MessageSpec(
            "say",
            {
                "words": Field(str, max_length=chronicle.MESSAGE_LIMIT),
                "to": Field(str, max_length=2_000, required=False),
                "links": Field(str, max_length=4_000, required=False),
            },
            say,
        ),
    ]


def event_specs(
    saga_id: str, clock: Callable[[], float] = time.monotonic
) -> list[MessageSpec]:
    """`events_since` and `roll`, for a signed-in seat."""
    rolls = RateLimiter(ROLLS_PER_MINUTE, 60.0, clock)

    def events_since(_session: Session, body: Body) -> Reply:
        return Reply(
            EVENTS, {"session": body.get("session", ""), "since": body["since"]}
        )

    def rolling(act: Act, unsaved: str) -> Callable[[Session, Body], Reply]:
        return _at_table(
            saga_id,
            rolls,
            refused="roll_refused",
            done="rolled",
            too_many="Too many rolls: wait a minute.",
            unsaved=unsaved,
            act=act,
        )

    roll = rolling(_roll, "The roll couldn't be saved.")
    confidence = rolling(_confidence, "The Chronicle couldn't be saved.")
    answer = rolling(_answer, "The roll couldn't be saved.")

    return [
        *_form_roll_specs(saga_id, clock),
        *_message_specs(saga_id, clock),
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
                "characteristic": Field(str, max_length=16, required=False),
                "ability": Field(str, max_length=120, required=False),
                "specialty": Field(bool, required=False),
            },
            roll,
        ),
        MessageSpec(
            "confidence",
            {
                "roll": Field(int, low=1, high=10**6),
                "points": Field(int, low=1, high=99),
            },
            confidence,
        ),
        MessageSpec(
            "answer",
            {
                "request": Field(int, low=1, high=10**6),
                "character_id": Field(str, max_length=64),
                "specialty": Field(bool, required=False),
            },
            answer,
        ),
    ]
