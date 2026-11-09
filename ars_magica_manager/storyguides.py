"""A storyguide for each story: who runs a record, and the switch between
Playing and a storyguide's role (ADR 0015; DE pp. 529-530, the troupe's
alpha and beta storyguides).

With a second storyguide (a Storyguide-role Player beside the host), a
record that holds Secrets (a character, covenant, place, lord, faction,
threat, creature or Tribunal) can have its own storyguide: the host or a
Storyguide-role Player. Any storyguide takes one with none; only its own
storyguide releases it or hands it on, so no one takes another's to read
its Secrets. What each storyguide may read and change is viewing.py's and
seat.py's to say; this module is the form that assigns a record, the
words a page shows, and the log of each switch.

Pattern: Command (a commands.Form, the same on both front-ends), beside
the Protection Proxy viewing.py, which reads who runs a record."""

from __future__ import annotations

from typing import Any

from . import viewing
from .commands import Form, Refuse, notes
from .form_spec import DialogField
from .markup import escape
from .models import Player, Saga
from .remote import audit
from .remote.audit import AuditLog, audit_path

TITLE = "Its Storyguide"
HELP_ID = "assign-storyguide"


def offered(saga: Saga, record: Any) -> bool:
    """Whether whoever sits here is offered Its Storyguide on `record`: a
    record that can have one, in a saga with a second storyguide, to a
    storyguide who runs it (theirs, or no one's)."""
    viewer = viewing.current()
    return (
        isinstance(record, viewing.ASSIGNABLE)
        and viewing.troupe_style(saga)
        and viewer.is_storyguide
        and viewing.runs(viewer, record, saga)
    )


def choices(saga: Saga, record: Any, me: str) -> list[tuple[str, str]]:
    """Who `me` may make `record`'s storyguide: themselves when it has
    none; when it is theirs, also any other storyguide (handing it on).
    No one (blank) is always a choice."""
    you = f"{viewing.storyguide_name(saga, me)} (you)"
    found = [(you, me)]
    if viewing.storyguide_of(record, saga) == me:
        found += [
            (viewing.storyguide_name(saga, other), other)
            for other in sorted(viewing.storyguide_ids(saga) - {me})
        ]
    return found


def assign_form(saga: Saga, record: Any) -> Form | Refuse:
    """Its Storyguide: take a record with none, or release or hand on
    one's own."""
    viewer = viewing.current()
    me = viewer.storyguide_id
    owner = viewing.storyguide_of(record, saga)
    if not viewing.runs(viewer, record, saga):
        return Refuse(
            TITLE,
            f"{escape(record.name)} is {escape(viewing.storyguide_name(saga, owner))}'s"
            " story: only they may release it or hand it on.",
        )

    def fields() -> list[DialogField]:
        return [
            DialogField(
                "storyguide",
                "Storyguide",
                "select",
                owner or None,
                options=[
                    (escape(name), key) for name, key in choices(saga, record, me)
                ],
                allow_blank=True,
                hint="Blank: no one's, so any storyguide reads it. Its storyguide "
                "alone reads its Secrets, and any other reads it as a player "
                "would.",
            )
        ]

    def apply(values: dict[str, Any]) -> list[str]:
        chosen = values.get("storyguide") or ""
        if chosen not in ("", me) and owner != me:
            # The form offers no such choice; a stale one is refused.
            return notes("Only its own storyguide may hand it on.")
        viewing.assign(record, chosen)
        who = viewing.storyguide_name(saga, chosen)
        return notes(
            f"{escape(record.name)} has no storyguide now."
            if not chosen
            else f"{escape(record.name)} is {escape(who)}'s story now."
        )

    return Form(TITLE, fields, apply, help_id=HELP_ID)


def freed_warning(saga: Saga, storyguide_id: str) -> str:
    """The warning before a storyguide is deleted or made a player again:
    the records they run, named, which every storyguide will read (""
    with none)."""
    found = viewing.records_of(saga, storyguide_id)
    if not found:
        return ""
    names = ", ".join(escape(r.name) for r in found)
    return (
        f"\n\nTheir stories will have no storyguide, so every storyguide will "
        f"read their Secrets: {names}."
    )


def log_switch(saga: Saga, player: Player | None, *, playing: bool) -> None:
    """Note on the host a storyguide's switch to Playing or to their
    storyguide role, in a saga with a second storyguide. `player`: a
    Storyguide-role Player signed in on the host; None for the host's own
    window. A Remote seat's switch is sent to the host (remote/switches.py)."""
    if not viewing.troupe_style(saga):
        return
    AuditLog(audit_path(saga.name)).record(
        audit.SWITCHED_TO_PLAYING if playing else audit.SWITCHED_TO_STORYGUIDE,
        player_id=player.id if player is not None else "",
    )
