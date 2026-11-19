"""The Message composer (the Virtual Tabletop preview): words to the Table,
or a Whisper to people chosen at the Session, with records linked from a
list of those the writer may open. Linking a record writes its name into
the words, so a reader sees the name where the link is. Before Send, the
composer says in words who will read it, because nothing sent can be
taken back.

Where it goes: into the Chronicle open here on the host's own copy; at a
Remote seat, to the host through the seat's connection (the sender the
Chronicle pane is given).

Pattern: the core Form (a FieldsDialog builder), its apply making a
Command (chronicle.message) for the host to carry out once, as the Free
roll's does."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .. import chronicle, host_table, references, viewing
from ..commands import Choice, Choose, Form, Picked, Refuse, notes
from ..form_spec import DialogField, ListEditor
from ..markup import escape
from ..models import Saga, Session

HELP_ID = "chronicle-messages"

#: Hands a Message to whoever writes it: the words, those whispered to
#: (none: the Table) and the records linked. The reason it was refused,
#: or None.
Send = Callable[[str, tuple[str, ...], tuple[references.Ref, ...]], str | None]

#: The kinds of record a Message may link (each a page shows), by the
#: saga's list of them, with the name the chooser filters by.
_KINDS = {kind: cls.__name__ for cls, kind in references.KINDS.items()}


def linkable(saga: Saga, viewer: viewing.Viewer) -> list[references.Ref]:
    """The records `viewer` may link: every one of a kind a page shows
    that they may open, by name."""
    found: list[references.Ref] = []
    for kind in _KINDS:
        for record in getattr(saga, kind, []):
            if record.name and viewing.readable(viewer, record, saga):
                found.append(references.Ref(kind, record.id, record.name))
    return sorted(found, key=lambda r: r.name)


def _key(ref: references.Ref) -> str:
    return f"{ref.kind}:{ref.id}"


def _audience(saga: Saga, session: Session, to: list[str]) -> str:
    """Who will read a Message sent to `to`, in words."""
    if not to:
        return "The Table: everyone at the Session"
    storyguide = chronicle.storyguide_of(session, saga)
    names = [chronicle.name_at(saga, session, t) for t in to if t != storyguide]
    if not names:
        return "A Whisper to the storyguide"
    return f"A Whisper to {', '.join(names)}, which the storyguide also sees"


def message_form(saga: Saga, session: Session, who: str, send: Send) -> Form:
    """A Message by `who` at `session`, handed to `send`."""
    people = [p for p in chronicle.at_session(saga, session) if p != who]
    refs = {_key(r): r for r in linkable(saga, chronicle.viewer_of(saga, who))}

    def person(each: Any) -> str:
        return chronicle.name_at(saga, session, str(each))

    def choose_person(_current: Any = None) -> Choose:
        return Choose(
            "Whisper to",
            lambda: [Choice(escape(person(p)), p) for p in people],
            Picked,
            empty="No one else is at the Session.",
        )

    def record(each: Any) -> str:
        found = refs.get(str(each))
        return found.name if found is not None else str(each)

    def choose_record(_current: Any = None) -> Choose:
        return Choose(
            "Link a record",
            lambda: [
                Choice(escape(r.name), key, facets=(("Kind", _KINDS[r.kind]),))
                for key, r in refs.items()
            ],
            Picked,
            empty="No records to link.",
            filters=("Kind",),
        )

    def name_new_links(values: dict[str, Any]) -> dict[str, Any]:
        words = str(values.get("words") or "")
        for each in values.get("links") or []:
            name = record(each)
            if name not in words:
                words = f"{words} {name}" if words else name
        return {"words": words}

    def fields() -> list[DialogField]:
        return [
            DialogField(
                "to",
                "To",
                "picker",
                [],
                display=lambda chosen: _audience(saga, session, list(chosen or [])),
                items=ListEditor(person, choose_person, "Whisper to"),
                hint="No one chosen: the Table. The storyguide sees every Whisper.",
            ),
            DialogField(
                "words",
                "Message",
                "area",
                "",
                hint="Plain words; once sent, it can't be changed or taken back.",
            ),
            DialogField(
                "links",
                "Link records",
                "picker",
                [],
                display=lambda chosen: (
                    "; ".join(record(c) for c in chosen or []) or "(none)"
                ),
                items=ListEditor(record, choose_record, "Link a record"),
                fills=name_new_links,
                hint="Each one's name goes into the Message; a reader who may "
                "open it gets a link.",
            ),
        ]

    def parts(
        values: dict[str, Any],
    ) -> tuple[str, tuple[str, ...], tuple[references.Ref, ...]]:
        words = str(values.get("words") or "").strip()
        to = tuple(str(t) for t in values.get("to") or [])
        links = tuple(refs[k] for k in values.get("links") or [] if k in refs)
        return words, to, links

    def validate(values: dict[str, Any]) -> str | None:
        words, to, links = parts(values)
        return chronicle.why_not_message(saga, session, words, to, who, links=links)

    def apply(values: dict[str, Any]) -> list[str]:
        refused = send(*parts(values))
        return notes(refused) if refused else []

    return Form(
        "Message",
        fields,
        apply,
        validate=validate,
        save_label="Send",
        help_id=HELP_ID,
    )


def why_not_here(saga: Saga, session: Session) -> str | None:
    """Why whoever uses this copy can't send a Message at `session` now,
    or None: it must be Under way, and they at it."""
    if not session.under_way:
        return "The Session isn't under way."
    if chronicle.here() not in chronicle.at_session(saga, session):
        return "Only someone at the Session sends a Message."
    return None


def message_here(saga: Saga, session: Session) -> Form | Refuse:
    """A Message by whoever uses this copy, written to the Chronicle open
    here (the host's own copy, or the terminal it serves)."""
    problem = why_not_here(saga, session)
    if problem:
        return Refuse("Message", problem)
    who = chronicle.here()
    return message_form(saga, session, who, send_here(saga, session, who))


def send_here(saga: Saga, session: Session, who: str) -> Send:
    """Writes `who`'s Message to the Chronicle open on this computer (the
    host's): the reason it was refused or couldn't be saved, or None."""

    return host_table.HostTable(saga, session, who).say
