"""The Show form (the Virtual Tabletop preview): what to show (a record
with a printed sheet, or a picture already in the saga), its title (the
record's or picture's name unless changed), the open story it belongs to,
and to whom (no one chosen: the Table). Only the Session's storyguide
shows, while the Session is Under way.

Where it goes: the Table this copy acts at (host_table.here): the host's
own Chronicle, or the host through a Remote seat's connection. Either way
the host makes the one frozen copy.

Pattern: the core Form (a FieldsDialog builder), its apply a Command for
the Table to carry out (Remote Proxy), as the Message composer's does."""

from __future__ import annotations

from typing import Any

from .. import (
    at_table,
    chronicle,
    host_table,
    open_stories,
    record_links,
    references,
    scene_aura,
    show_copy,
    shows,
    table_rules,
    viewing,
)
from ..at_table import Table
from ..commands import Choice, Choose, Command, Form, Picked, Refuse, notes
from ..form_spec import DialogField, ListEditor
from ..markup import escape
from ..models import Saga, Session
from . import reveal
from . import secrets as secret_titles

HELP_ID = "chronicle-shows"
TITLE = "Show"
#: What only the Session's storyguide does (table_rules.why_not_lead).
ACT = "shows something"

#: Each kind of record that may be shown, as the form names it.
_KIND_NAMES = {
    kind: cls.__name__
    for cls, kind in references.KINDS.items()
    if cls in shows.SHOWABLE
}
_RECORD, _PICTURE = "record", "picture"


def _record_key(ref: references.Ref) -> str:
    return f"{_RECORD}:{ref.kind}:{ref.id}"


def _picture_key(picture: tuple[str, str]) -> str:
    return f"{_PICTURE}:{picture[0]}:{picture[1]}"


#: What a Show may start on: a record, or a picture as (folder, file name).
Showable = references.Ref | tuple[str, str]


#: The key of the "Also reveal" tick.
ALSO_REVEAL = "also_reveal"
#: The key of the Secrets to show: a list of (place, mark), each a Secret
#: not yet revealed (shows.secret_mark).
SECRETS = "secrets"
SECRETS_TITLE = "Secrets to show"
#: A tick's key in the Secrets chooser, before the Secret's place.
_TICK = "tick_"

Tick = tuple[int, str]


def _sendable(saga: Saga, what: str, who: str) -> tuple[Any, list[int]]:
    """The record `what` names and the places of its Secrets not yet
    revealed that `who` may send (none for another storyguide's record)."""
    record, _picture, _name = _chosen(saga, what)
    found = references.find(saga, record.kind, record.id) if record else None
    if found is None or not shows.sends_secrets(saga, found, who):
        return found, []
    return found, shows.unrevealed(found)


def secrets_chooser(
    saga: Saga, who: str, current: Any, values: dict[str, Any]
) -> Form | Refuse:
    """The chosen record's Secrets not yet revealed, ticked on a list:
    those ticked go with the Show. Each is kept by its place and a mark
    of its words, so a list changed since is refused, not misread."""
    record, rows = _sendable(saga, str(values.get("what") or ""), who)
    if not rows:
        return Refuse(SECRETS_TITLE, "No Secret of it is yours to show.")
    ticked = {row for row, _mark in current or []}

    def fields() -> list[DialogField]:
        return [
            DialogField(
                f"{_TICK}{row}",
                secret_titles.title_of(record.secrets[row]),
                "check",
                row in ticked,
            )
            for row in rows
        ]

    def picked(chosen: dict[str, Any]) -> Picked:
        return Picked(
            [
                (row, shows.secret_mark(record.secrets[row]))
                for row in rows
                if chosen.get(f"{_TICK}{row}") is True
            ]
        )

    return Form(SECRETS_TITLE, fields, picked, save_label="Done", help_id=HELP_ID)


def _secret_fields(saga: Saga, who: str) -> list[DialogField]:
    """The Secrets to show, offered while a record with Secrets `who` may
    send is chosen, then Also reveal, while any record is."""

    def ticked(chosen: Any) -> str:
        count = len(chosen or [])
        if not count:
            return "None: the copy holds only those revealed"
        return f"{count} ticked" if count > 1 else "1 ticked"

    return [
        DialogField(
            SECRETS,
            SECRETS_TITLE,
            "picker",
            [],
            show_if=lambda values: bool(
                _sendable(saga, str(values.get("what") or ""), who)[1]
            ),
            display=ticked,
            choose=lambda current, values: secrets_chooser(saga, who, current, values),
            choose_with_values=True,
            hint="Its Secrets not yet revealed: those you tick go with the copy.",
        ),
        DialogField(
            ALSO_REVEAL,
            "Also reveal",
            "check",
            False,
            show_if=lambda values: str(values.get("what") or "").startswith(_RECORD),
            hint="The players come to know of the record, and the ticked Secrets "
            "are revealed this season, each with its line in the Diary, as "
            "Reveal does. Unticked, nothing changes for the troupe.",
        ),
    ]


def _ticks(value: Any) -> tuple[Tick, ...]:
    """The Secrets to show, from the picker's value."""
    return tuple((int(row), str(mark)) for row, mark in value or [])


def _also_reveal(saga: Saga, ref: references.Ref, rows: tuple[int, ...]) -> None:
    """Reveal's own steps: the record known, with its Diary line, and its
    Secrets at `rows` revealed this season, each with its line."""
    record = references.find(saga, ref.kind, ref.id)
    if record is None:
        return
    if viewing.can_be_unknown(record):
        reveal.set_known(saga, record, True)
    for row in rows:
        reveal.set_revealed(saga, record, record.secrets[row], True)


def _key_of(preset: Showable | None) -> str:
    if preset is None:
        return ""
    if isinstance(preset, references.Ref):
        return _record_key(preset)
    return _picture_key(preset)


def what_options(saga: Saga) -> list[tuple[str, str]]:
    """What may be shown: each record by name and kind, then each picture
    already in the saga: on the host's computer, those whose file it has;
    at a Remote seat, which holds no files, each the saga names."""
    records = [
        (f"{r.name} ({_KIND_NAMES[r.kind]})", _record_key(r))
        for r in shows.records(saga)
    ]
    named = (
        record_links.pictures(saga)
        if at_table.seat() is not None
        else shows.pictures(saga)
    )
    pictures = [
        (f"Picture: {shows.picture_label(saga, p)}", _picture_key(p)) for p in named
    ]
    return records + pictures


def story_options(saga: Saga) -> list[tuple[str, str]]:
    """The open stories a Show may belong to: those with an id (one is
    given when a story is first taken up)."""
    return [("(none)", "")] + [
        (s.entry.name, s.entry.id) for s in open_stories.stories(saga) if s.entry.id
    ]


def _chosen(
    saga: Saga, key: str
) -> tuple[references.Ref | None, tuple[str, str] | None, str]:
    """The record or picture `key` names, and its name ("" for none)."""
    kind, _, rest = key.partition(":")
    if kind == _RECORD:
        list_kind, _, record_id = rest.partition(":")
        record = references.find(saga, list_kind, record_id)
        if record is not None:
            return references.Ref(list_kind, record_id, record.name), None, record.name
    if kind == _PICTURE:
        folder, _, name = rest.partition(":")
        return None, (folder, name), shows.picture_label(saga, (folder, name))
    return None, None, ""


def show_form(
    saga: Saga,
    session: Session,
    who: str,
    table: Table,
    preset: Showable | None = None,
    to: tuple[str, ...] = (),
) -> Form:
    """A Show by `who` at `session`, handed to `table`; `preset` is what it
    starts on (the record whose page it was opened on, or an entry of
    another list, such as a picture), `to` the Players it starts with (any
    not at the Session left off; none: the Table)."""
    storyguide = table_rules.storyguide_of(session, saga)
    people = [p for p in chronicle.at_session(saga, session) if p != storyguide]
    first = _key_of(preset)
    first_to = [p for p in dict.fromkeys(to) if p in people]

    def person(each: Any) -> str:
        return chronicle.name_at(saga, session, str(each))

    def choose_person(_current: Any = None) -> Choose:
        return Choose(
            "Show to",
            lambda: [Choice(escape(person(p)), p) for p in people],
            Picked,
            empty="No Player is at the Session.",
        )

    def named(values: dict[str, Any]) -> dict[str, Any]:
        """Something else chosen: its name, and no Secret ticked."""
        return {"title": _chosen(saga, str(values.get("what") or ""))[2], SECRETS: []}

    def fields() -> list[DialogField]:
        return [
            DialogField(
                "what",
                "Show",
                "select",
                first,
                options=[("(choose)", ""), *what_options(saga)],
                fills=named,
                hint="A record's copy is as the players read it now, kept as it "
                "is; a picture is copied as it is.",
            ),
            DialogField(
                "title",
                "Title",
                "text",
                _chosen(saga, first)[2],
                hint="What the Show is called on its card.",
            ),
            DialogField(
                "story",
                "Story",
                "select",
                "",
                options=story_options(saga),
                hint="The open story it belongs to, if any.",
            ),
            DialogField(
                "to",
                "To",
                "picker",
                list(first_to),
                display=lambda chosen: (
                    ", ".join(person(p) for p in chosen or [])
                    or "The Table: everyone at the Session"
                ),
                items=ListEditor(person, choose_person, "Show to"),
                hint="No one chosen: the Table. The storyguide sees every Show.",
            ),
            *_secret_fields(saga, who),
        ]

    def call(values: dict[str, Any]) -> chronicle.ShowCall:
        record, picture, _name = _chosen(saga, str(values.get("what") or ""))
        return chronicle.ShowCall(
            str(values.get("title") or "").strip(),
            record=record,
            picture=picture,
            to=tuple(str(t) for t in values.get("to") or []),
            story_id=str(values.get("story") or ""),
            secrets=_ticks(values.get(SECRETS)) if record is not None else (),
            reveal=record is not None and values.get(ALSO_REVEAL) is True,
        )

    def validate(values: dict[str, Any]) -> str | None:
        return shows.why_not_ask(saga, session, call(values), who)

    def apply(values: dict[str, Any]) -> list[str]:
        asked = call(values)
        refused = table.show(asked)
        if refused:
            return notes(refused)
        if asked.reveal and asked.record is not None:
            _also_reveal(saga, asked.record, tuple(row for row, _ in asked.secrets))
        return []

    return Form(
        TITLE, fields, apply, validate=validate, save_label="Show", help_id=HELP_ID
    )


def copy_form(shown: shows.Shown) -> Form:
    """A Show's copy to read: the record's sheet as it was shown, or, for a
    picture, its name (the desktop draws the picture itself)."""
    if shown.picture is not None:
        words = f"A picture: {escape(shown.title)}. Open it on the desktop to see it."
    else:
        words = escape(shown.text)
    return Form(
        f"Shown: {escape(shown.title)}",
        lambda: [DialogField("_shown", "", "info", words)],
        lambda _values: None,
        save_label="Close",
        help_id=HELP_ID,
    )


def live_record(saga: Saga, entry: chronicle.Entry, who: str) -> references.Ref | None:
    """The record Show `entry` copied, when `who` may read it now (its
    "Open the live record"); None for a picture, a record gone, or one
    they may not read."""
    ref = entry.body.get("ref")
    if not isinstance(ref, list) or len(ref) != 3:
        return None
    found = references.Ref(*(str(part) for part in ref))
    record = references.target(saga, found)
    if record is None:
        return None
    viewer = chronicle.viewer_of(saga, who)
    return references.ref(record) if viewing.readable(viewer, record, saga) else None


def shown_entries(
    saga: Saga, session: Session, who: str, book: chronicle.HasEntries
) -> list[chronicle.Entry]:
    """The Shows of `book` that `who` reads, newest first."""
    reader = chronicle.Reader(book, who, session, saga)
    return [e for e in reversed(reader.entries()) if e.kind == chronicle.SHOW]


def open_one(table: Table, entry: chronicle.Entry) -> Command:
    """Open Show `entry`'s copy, at the Table this copy acts at."""
    found = table.open_show(entry)
    if isinstance(found, str):
        return Refuse(TITLE, escape(found))
    return copy_form(found)


def shows_held(
    saga: Saga, session: Session, who: str
) -> tuple[Table, list[chronicle.Entry]]:
    """The Table this copy acts at, and the Shows of `session` that `who`
    reads in the Chronicle it holds: none when it holds another Session's
    (a Remote seat holds only the one its host is feeding it)."""
    table = host_table.here(saga, session, who)
    book = table.held()
    if book is None or (
        isinstance(book, chronicle.SeatChronicle) and book.session_id != session.id
    ):
        return table, []
    return table, shown_entries(saga, session, who, book)


def open_show(saga: Saga, session: Session) -> Command:
    """Open a Show of `session`: choose one of those whoever uses this copy
    reads, then read its copy (the terminal's way to the Show cards)."""
    table, found = shows_held(saga, session, chronicle.here())
    return Choose(
        "Open a Show",
        lambda: [Choice(escape(str(e.body.get("title", ""))), e.number) for e in found],
        lambda number: open_one(table, next(e for e in found if e.number == number)),
        empty="Nothing has been shown at this Session.",
    )


def default_to(saga: Saga, session: Session) -> tuple[str, ...]:
    """Whom a Show starts on while a Scene plays: the players of the
    characters present there, tonight (none: the Table). It never limits
    whom it may go to."""
    present = scene_aura.present_ids(session, scene_aura.held(saga, session))
    if not present:
        return ()
    storyguide = table_rules.storyguide_of(session, saga)
    players = (table_rules.player_of(session, cid) for cid in sorted(present))
    return tuple(dict.fromkeys(p for p in players if p and p != storyguide))


def why_not_here(saga: Saga, session: Session) -> str | None:
    """Why whoever uses this copy can't Show at `session` now, or None."""
    return table_rules.why_not_lead(saga, session, chronicle.here(), ACT)


def show_here(
    saga: Saga,
    session: Session,
    preset: Showable | None = None,
    to: tuple[str, ...] = (),
) -> Form | Refuse:
    """A Show by whoever uses this copy, at the Table it acts at, starting
    on `preset` and the Players `to` when a caller gives them (a Scene's
    list of things to show); else, while a Scene plays, the players of
    those present (default_to)."""
    problem = why_not_here(saga, session)
    if problem:
        return Refuse(TITLE, problem)
    who = chronicle.here()
    table = host_table.here(saga, session, who, show_copy.player_copy)
    return show_form(saga, session, who, table, preset, to or default_to(saga, session))


def show_record(saga: Saga, record: Any) -> Form | Refuse:
    """Show, opened on `record`'s page: at the Session Under way."""
    session = chronicle.under_way(saga)
    if session is None:
        return Refuse(TITLE, "No Session is under way.")
    return show_here(saga, session, references.ref(record))
