"""More's Disputatio on a character: a schoolmen's debate with another
character, rolled out exchange by exchange, then kept in both Diaries
with the real fatigue it cost. The rules are rules.disputatio's."""

from __future__ import annotations

import random
from typing import Any

from .commands import Command, Confirm, Form, Refuse
from .form_spec import DialogField, pairs
from .markup import escape
from .models import FATIGUE_LEVELS, Character, DiaryEntry, Saga
from .rules import disputatio

TITLE = "Disputatio"


def _subject(character: Character) -> str:
    """The subject the character knows best (Artes Liberales on a tie)."""
    return max(
        disputatio.SUBJECTS,
        key=lambda s: (disputatio.subject_score(character, s), s == "Artes Liberales"),
    )


def fields(saga: Saga, character: Character) -> list[DialogField]:
    others = [c for c in saga.characters if c.id != character.id]
    return [
        DialogField(
            "against",
            "Against",
            "select",
            others[0].id,
            options=[(escape(c.name), c.id) for c in others],
            required=True,
        ),
        DialogField(
            "role",
            f"{escape(character.name)} is the",
            "select",
            "opponent",
            options=[
                ("Opponent (states first)", "opponent"),
                ("Respondent (defends)", "respondent"),
            ],
            required=True,
        ),
        DialogField(
            "subject",
            "Subject",
            "select",
            _subject(character),
            options=pairs(disputatio.SUBJECTS),
            required=True,
        ),
        DialogField(
            "kind",
            "Kind",
            "select",
            "deliberative",
            options=[
                ("Epideictic (praise or blame)", "epideictic"),
                ("Deliberative (an opinion)", "deliberative"),
                ("Forensic (a case at law)", "forensic"),
            ],
            required=True,
        ),
        DialogField(
            "exchanges",
            "Questions",
            "int",
            disputatio.DEFAULT_EXCHANGES,
            hint="The judge's questions: usually 7, 9 or 12.",
        ),
        DialogField(
            "ease",
            "Statements must reach",
            "select",
            "0",
            options=[
                ("No Ease Factor", "0"),
                ("6 (students)", "6"),
                ("9 (baccalaureates)", "9"),
                ("12 (a candidate's examination)", "12"),
            ],
        ),
        DialogField(
            "crowd",
            "Before a crowd",
            "check",
            False,
            hint="A Gifted disputer (not a Gentle Gift) takes 3 from each roll.",
        ),
    ]


def problem(values: dict[str, Any]) -> str | None:
    if not 1 <= (values.get("exchanges") or 0) <= disputatio.MAX_EXCHANGES:
        return f"A disputatio has 1 to {disputatio.MAX_EXCHANGES} questions."
    return None


def sides(
    saga: Saga, character: Character, values: dict[str, Any]
) -> tuple[disputatio.Disputer, disputatio.Disputer] | None:
    """The opponent and the respondent, from the form's values."""
    other = saga.character(values.get("against"))
    if other is None:
        return None
    subject = values.get("subject") or "Artes Liberales"
    kind = values.get("kind") or "deliberative"
    crowd = bool(values.get("crowd"))
    first, second = _people(character, other, values)
    return (
        disputatio.disputer(first, subject, kind, crowd=crowd),
        disputatio.disputer(second, subject, kind, crowd=crowd),
    )


def _people(
    character: Character, other: Character, values: dict[str, Any]
) -> tuple[Character, Character]:
    """The opponent and the respondent."""
    if values.get("role") == "respondent":
        return other, character
    return character, other


def _side_text(side: disputatio.Disputer) -> str:
    counted = f" ({'; '.join(side.counted)})" if side.counted else ""
    return (
        f"{escape(side.name)}: Attack {side.attack:+d}, Defence {side.defence:+d}, "
        f"Resistance {side.resistance}{counted}"
    )


def live(saga: Saga, character: Character, values: dict[str, Any]) -> str:
    both = sides(saga, character, values)
    if both is None:
        return "Choose who disputes with them."
    return "; ".join(_side_text(side) for side in both) + ", each with a stress die."


def disputatio_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Disputatio: choose the other disputer and the terms, roll it
    out, and keep it in both Diaries."""
    if character is None:
        return Refuse(TITLE, "Choose a character first.")
    if len(saga.characters) < 2:
        return Refuse(TITLE, "A disputatio needs a second character to dispute with.")
    dice = rng or random.Random()

    def apply(values: dict[str, Any]) -> Command:
        both = sides(saga, character, values)
        assert both is not None
        other = saga.character(values["against"])
        assert other is not None
        exchanges = int(values["exchanges"])
        result = disputatio.run(both, exchanges, dice, int(values.get("ease") or 0))
        checks = [
            disputatio.over_exertion(side, result.exchanges, dice) for side in both
        ]
        kind = values.get("kind") or "deliberative"
        winner = result.winner
        if winner is None:
            outcome = "A draw: neither side wins."
        else:
            outcome = (
                f"{both[winner].name} wins, {result.lost[winner]} level(s) lost "
                f"to {result.lost[1 - winner]}. "
                + disputatio.reward(kind, both[winner].name, both[1 - winner].name)
            )
        tired = [
            f"{side.name}: Stamina {total} against {result.exchanges}"
            + (f", {lost} Long-Term Fatigue level(s) lost" if lost else ", no fatigue")
            for side, (total, lost) in zip(both, checks, strict=True)
        ]
        people = _people(character, other, values)
        details = "\n".join([*result.lines, outcome, *tired])

        def keep() -> None:
            for who, (_total, lost) in zip(people, checks, strict=True):
                who.diary.append(
                    DiaryEntry(
                        saga.current_year,
                        saga.current_season,
                        f"Disputatio in {values['subject']} with "
                        f"{(other if who is character else character).name}",
                        details,
                    )
                )
                if lost:
                    at = FATIGUE_LEVELS.index(who.fatigue_level)
                    who.fatigue_level = FATIGUE_LEVELS[
                        min(at + lost, len(FATIGUE_LEVELS) - 1)
                    ]

        return Confirm(
            "\n".join(escape(line) for line in [*result.lines, "", outcome, *tired]),
            keep,
            yes_label="Keep",
            title=TITLE,
        )

    return Form(
        f"{TITLE}: {escape(character.name)}",
        lambda: fields(saga, character),
        apply,
        validate=problem,
        live=lambda values: live(saga, character, values),
        save_label="Dispute",
        help_id="disputatio",
    )
