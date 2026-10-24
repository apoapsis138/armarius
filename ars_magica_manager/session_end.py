"""More's End of Session on a character's Reputations: the Confidence
Points the session earned and the noteworthy deeds that grow Reputations,
written in the Diary -- no UI in here. The rules are rules.confidence's."""

from __future__ import annotations

from typing import Any

from .commands import Command, Form, Refuse, notes
from .form_spec import DialogField
from .markup import escape
from .models import Character, DiaryEntry, Saga
from .rules import confidence

TITLE = "End of Session"


def session_fields(character: Character) -> list[DialogField]:
    """Whether the character took a real part, the five awards, and the
    deeds done for each Reputation."""
    played = DialogField(
        "played",
        "Played for a good part of it, and contributed",
        "check",
        True,
        hint="Without it the session earns no Confidence (DE p. 29).",
    )
    awards = [
        DialogField(key, label, "check", False, show_if=lambda v: bool(v.get("played")))
        for key, label in confidence.AWARDS.items()
    ]
    deeds = [
        DialogField(
            f"deeds_{index}",
            f"Noteworthy deeds for {escape(r.name)} ({r.score:+d})",
            "int",
            0,
            hint="Each one, before witnesses who will talk, is an experience "
            "point in it (DE p. 386).",
        )
        for index, r in enumerate(character.reputations)
    ]
    return [played, *awards, *deeds]


def end_session(saga: Saga, character: Character, values: dict[str, Any]) -> list[str]:
    """Apply the session's awards and deeds; the notes, also in the Diary."""
    chosen = {key for key in confidence.AWARDS if values.get(key)}
    points = confidence.points_earned(bool(values.get("played")), chosen)
    confidence.award(character, points)
    lines = [
        f"{points} Confidence Point(s): "
        + (
            ", ".join(confidence.AWARDS[k] for k in confidence.AWARDS if k in chosen)
            or "none"
        )
        + f"; now {character.background.confidence_points}."
    ]
    for index, reputation in enumerate(character.reputations):
        done = int(values.get(f"deeds_{index}") or 0)
        if done <= 0:
            continue
        before = reputation.score
        confidence.add_deeds(reputation, done)
        lines.append(
            f"{reputation.name}: {done} deed(s)"
            + (
                f", {before:+d} to {reputation.score:+d}"
                if reputation.score != before
                else f", {reputation.deeds} toward the next level"
            )
            + "."
        )
    character.diary.append(
        DiaryEntry(
            saga.current_year,
            saga.current_season,
            "End of session",
            "\n".join(
                [*lines, f"Rules: {confidence.SOURCE}; {confidence.REPUTATION_SOURCE}"]
            ),
        )
    )
    return notes(*lines)


def end_session_form(saga: Saga, character: Character | None) -> Command:
    if character is None:
        return Refuse(TITLE, "Choose a character first.")
    return Form(
        f"{TITLE}: {escape(character.name)}",
        lambda: session_fields(character),
        lambda values: end_session(saga, character, values),
        help_id="end-of-session",
    )
