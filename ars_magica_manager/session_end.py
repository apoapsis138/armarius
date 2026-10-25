"""More's End of Session on a character's Reputations: the Confidence
Points the session earned and the noteworthy deeds that grow Reputations,
written in the Diary -- no UI in here. The rules are rules.confidence's."""

from __future__ import annotations

from typing import Any

from .commands import Command, Form, Refuse, notes
from .form_spec import DialogField
from .markup import escape
from .models import Character, DiaryEntry, Saga, ScoredTrait
from .rules import confidence, nobility

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
    deeds: list[DialogField] = []
    for index, r in enumerate(character.reputations):
        old = confidence.replaced(character.reputations, r)
        if old is None:
            deeds.append(
                DialogField(
                    f"deeds_{index}",
                    f"Noteworthy deeds for {escape(r.name)} ({r.score:+d})",
                    "int",
                    0,
                    hint=_deeds_hint(r),
                )
            )
            continue
        deeds += _replacing_fields(index, r, old)
    return [played, *awards, *deeds]


def _deeds_hint(reputation: ScoredTrait) -> str:
    if nobility.is_noble(reputation):
        return (
            "Each is an experience point in it (DE p. 386). Among nobles a "
            "season of great deeds is 1; gaining a noble liege 3, a royal "
            "liege 6 (Lords of Men p. 26)."
        )
    return (
        "Each one, before witnesses who will talk, is an experience point in "
        "it (DE p. 386)."
    )


def _replacing_fields(
    index: int, new: ScoredTrait, old: ScoredTrait
) -> list[DialogField]:
    """A Reputation replacing a bad one: the deeds that support it, the
    other deeds (which go to the old one until it is passed), and whether
    a rise lowers the old one instead (DE pp. 386-387)."""
    return [
        DialogField(
            f"deeds_{index}",
            f"Deeds that support {escape(new.name)} ({new.score:+d})",
            "int",
            0,
            hint=f"It is replacing {escape(old.name)} ({old.score:+d}): "
            "these count toward it alone.",
        ),
        DialogField(
            f"general_{index}",
            "Other noteworthy deeds",
            "int",
            0,
            hint=f"They count toward {escape(old.name)} until "
            f"{escape(new.name)}'s score passes it, then toward "
            f"{escape(new.name)} (DE p. 387).",
        ),
        DialogField(
            f"lower_{index}",
            f"Once ahead, lower {escape(old.name)} instead of raising "
            f"{escape(new.name)}",
            "check",
            True,
        ),
    ]


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
    for index, reputation in enumerate(list(character.reputations)):
        done = int(values.get(f"deeds_{index}") or 0)
        old = confidence.replaced(character.reputations, reputation)
        if old is not None:
            lines += _replacing_lines(
                reputation,
                old,
                done,
                int(values.get(f"general_{index}") or 0),
                bool(values.get(f"lower_{index}")),
            )
            continue
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
    for name in confidence.drop_spent(character.reputations):
        lines.append(f"{name} is gone: the new Reputation has replaced it.")
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


def _replacing_lines(
    new: ScoredTrait, old: ScoredTrait, supporting: int, general: int, lower: bool
) -> list[str]:
    if supporting <= 0 and general <= 0:
        return []
    before_new, before_old = new.score, old.score
    confidence.count_replacing(new, old, supporting, general, lower_old=lower)
    return [
        f"{new.name}: {supporting} supporting and {general} other deed(s); "
        f"{new.name} {before_new:+d} to {new.score:+d}, "
        f"{old.name} {before_old:+d} to {old.score:+d}."
    ]


def end_session_form(saga: Saga, character: Character | None) -> Command:
    if character is None:
        return Refuse(TITLE, "Choose a character first.")
    return Form(
        f"{TITLE}: {escape(character.name)}",
        lambda: session_fields(character),
        lambda values: end_session(saga, character, values),
        help_id="end-of-session",
    )
