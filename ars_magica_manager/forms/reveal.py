"""Reveal: the storyguide tells the players of a record, or takes it back.

Revealing a record ticks it known to the players (viewing.py) and writes
a dated line in each troupe covenant's Diary, so the troupe's own record
says when they learned of it; hiding it again unticks it and takes that
line out. Hide from the Players on the Region marks many at once: every
record of one of its lists, or those in one Tribunal's lands.

Pattern: Command (commands.Confirm and Form), the same steps on both
front-ends."""

from __future__ import annotations

from typing import Any

from .. import neighbours, places, viewing, world
from ..commands import Confirm, Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import escape
from ..models import CovenantDiaryEntry, Saga, Secret
from . import secrets

#: How a reveal's Diary line is named: "Revealed: Gottfried of Arnsberg".
REVEALED = "Revealed: "
REVEAL_TITLE = "Reveal to the Players"
CONCEAL_TITLE = "Hide from the Players"
MARK_TITLE = "Hide from the Players"
MARK_HELP = "mark-unknown"


def _line(saga: Saga, record: Any) -> CovenantDiaryEntry:
    return CovenantDiaryEntry(
        saga.current_year,
        saga.current_season,
        f"{REVEALED}{record.name}",
        f"The players now know of {record.name}.",
        about=viewing.about(record),
    )


def _is_its_line(entry: CovenantDiaryEntry, record: Any) -> bool:
    return entry.name.startswith(REVEALED) and entry.about == viewing.about(record)


def set_known(saga: Saga, record: Any, known: bool) -> None:
    """Tick `record` known (writing its line in each troupe covenant's
    Diary) or unknown (taking those lines out)."""
    if record.known == known:
        return
    record.known = known
    for covenant in world.player_covenants(saga):
        if known:
            covenant.diary.append(_line(saga, record))
        else:
            covenant.diary[:] = [
                e for e in covenant.diary if not _is_its_line(e, record)
            ]


def reveal(saga: Saga, record: Any) -> Confirm | Refuse:
    """Reveal to the Players, after asking."""
    if not viewing.can_be_unknown(record):
        return Refuse(REVEAL_TITLE, "The troupe's own records are always known.")
    if record.known:
        return Refuse(
            REVEAL_TITLE, f"The players already know of {escape(record.name)}."
        )

    def apply() -> list[str]:
        set_known(saga, record, True)
        return notes(f"The players now know of {escape(record.name)}.")

    covenants = world.player_covenants(saga)
    where = (
        " A line saying so goes in "
        + escape(", ".join(c.name for c in covenants))
        + "'s Diary."
        if covenants
        else ""
    )
    return Confirm(
        f"Reveal {escape(record.name)} to the players? They will see it in "
        f"lists, Find and the Atlas, and its name on the pages that name it.{where}",
        apply,
        yes_label="Reveal",
        title=REVEAL_TITLE,
    )


def conceal(saga: Saga, record: Any) -> Confirm | Refuse:
    """Hide from the Players: unknown again, after asking."""
    if not viewing.can_be_unknown(record):
        return Refuse(CONCEAL_TITLE, "The troupe's own records are always known.")
    if not record.known:
        return Refuse(
            CONCEAL_TITLE, f"The players don't know of {escape(record.name)} yet."
        )

    def apply() -> list[str]:
        set_known(saga, record, False)
        return notes(f"{escape(record.name)} is hidden from the players.")

    return Confirm(
        f"Hide {escape(record.name)} from the players? It is left out of "
        "everything they read until you reveal it, and the Diary line its "
        "reveal wrote is taken out.",
        apply,
        yes_label="Hide",
        title=CONCEAL_TITLE,
    )


# -- many at once --

#: What Hide from the Players can mark, beside the Region's lists.
OTHER_COVENANTS = "covenants"
CHARACTERS = "characters"
CREATURES = "creatures"


def _which(saga: Saga) -> list[tuple[str, str]]:
    return [
        *((g.title, g.key) for g in neighbours.GROUPS),
        ("Other covenants", OTHER_COVENANTS),
        ("Non-player characters", CHARACTERS),
        ("The Bestiary", CREATURES),
    ]


def _records(saga: Saga, which: str) -> list[Any]:
    if which == OTHER_COVENANTS:
        found: list[Any] = [c for c in saga.covenants if not c.played]
    elif which == CHARACTERS:
        found = [c for c in saga.characters if viewing.can_be_unknown(c)]
    elif which == CREATURES:
        found = list(saga.creatures)
    else:
        found = [n for n in saga.neighbours if neighbours.kind_of(n).group == which]
    return found


def marked(saga: Saga, values: dict[str, Any]) -> list[Any]:
    """The known records Hide from the Players would mark, for the form's
    values."""
    which = values.get("which") or ""
    tribunal = values.get("tribunal") or ""
    return [
        r
        for r in _records(saga, which)
        if r.known
        and (
            not tribunal
            or (
                (lands := places.lands_of(saga, r)) is not None and lands.id == tribunal
            )
        )
    ]


def mark_fields(saga: Saga) -> list[DialogField]:
    return [
        DialogField(
            "which",
            "Which",
            "select",
            neighbours.GROUPS[0].key,
            options=_which(saga),
            required=True,
            hint="Every record of this list is hidden from the players.",
        ),
        DialogField(
            "tribunal",
            "In the lands of",
            "select",
            None,
            options=[(t.name, t.id) for t in saga.tribunals],
            allow_blank=True,
            hint="Blank: wherever they are.",
        ),
    ]


def mark_unknown(saga: Saga) -> Form:
    """Hide from the Players, many at once."""

    def live(values: dict[str, Any]) -> str:
        count = len(marked(saga, values))
        return f"{count} record{'s' if count != 1 else ''} known now would be hidden."

    def apply(values: dict[str, Any]) -> list[str]:
        found = marked(saga, values)
        for record in found:
            set_known(saga, record, False)
        return notes(
            f"{len(found)} record{'s' if len(found) != 1 else ''} hidden from the "
            "players."
            if found
            else "Nothing to hide: the players knew of none of them."
        )

    return Form(
        MARK_TITLE,
        lambda: mark_fields(saga),
        apply,
        live=live,
        save_label="Hide",
        help_id=MARK_HELP,
    )


# -- one secret --

SECRET_TITLE = "Reveal the Secret"
HIDE_SECRET_TITLE = "Hide the Secret Again"


def _secret_line_name(record: Any, secret: Secret) -> str:
    return f"{REVEALED}{record.name}: {secrets.title_of(secret)}"


def set_revealed(saga: Saga, record: Any, secret: Secret, on: bool) -> None:
    """Mark `secret` of `record` revealed this season (writing its line in
    each troupe covenant's Diary) or not (taking those lines out)."""
    if secret.revealed == on:
        return
    name = _secret_line_name(record, secret)
    covenants = world.player_covenants(saga)
    if on:
        secret.revealed_year = saga.current_year
        secret.revealed_season = saga.current_season
        for covenant in covenants:
            covenant.diary.append(
                CovenantDiaryEntry(
                    saga.current_year,
                    saga.current_season,
                    name,
                    secret.text.strip(),
                    about=viewing.about(record),
                )
            )
        return
    secret.revealed_year, secret.revealed_season = None, ""
    for covenant in covenants:
        covenant.diary[:] = [
            e
            for e in covenant.diary
            if not (e.name == name and e.about == viewing.about(record))
        ]


def _chosen(record: Any, row: int | None) -> Secret | None:
    if row is None or not 0 <= row < len(record.secrets):
        return None
    return record.secrets[row]


def reveal_secret(saga: Saga, record: Any, row: int | None) -> Confirm | Refuse:
    """Reveal one secret to the troupe, after asking: the same Reveal as a
    record's, given the secret."""
    secret = _chosen(record, row)
    if secret is None:
        return Refuse(SECRET_TITLE, "Choose a secret first.")
    if secret.revealed:
        return Refuse(SECRET_TITLE, "The players already know that one.")

    def apply() -> list[str]:
        set_revealed(saga, record, secret, True)
        return notes(f"Revealed {escape(secrets.title_of(secret))}.")

    hidden = (
        ""
        if viewing.is_known(record)
        else f" They don't know of {escape(record.name)} yet, so it shows only "
        "once that is revealed too."
    )
    return Confirm(
        f"Reveal {escape(secrets.title_of(secret))} to the players? It shows in "
        f"{escape(record.name)}'s Known section, and a line dated this season "
        f"goes in the troupe's covenants' Diary.{hidden}",
        apply,
        yes_label="Reveal",
        title=SECRET_TITLE,
    )


def conceal_secret(saga: Saga, record: Any, row: int | None) -> Confirm | Refuse:
    """Take a revealed secret back, after asking."""
    secret = _chosen(record, row)
    if secret is None:
        return Refuse(HIDE_SECRET_TITLE, "Choose a secret first.")
    if not secret.revealed:
        return Refuse(HIDE_SECRET_TITLE, "The players don't know that one yet.")

    def apply() -> list[str]:
        set_revealed(saga, record, secret, False)
        return notes(f"{escape(secrets.title_of(secret))} is the storyguide's again.")

    return Confirm(
        f"Hide {escape(secrets.title_of(secret))} from the players again? The "
        "Diary line its reveal wrote is taken out.",
        apply,
        yes_label="Hide",
        title=HIDE_SECRET_TITLE,
    )
