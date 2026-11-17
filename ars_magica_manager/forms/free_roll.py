"""The Free roll form: a roll made from the Chronicle rather than from a
sheet (the Virtual Tabletop preview). It asks what to roll and never a
number: stress or simple, the modifier, botch dice, an optional Ease
Factor, what it is for, the character, and who sees it. Saving hands the
RollRequest to `submit`, which rolls it at the host (chronicle.free_roll on
the host's own window, a roll request from a Remote seat) and says why if
it can't.

Pattern: the core Form, its apply making a Command (chronicle.RollRequest)
for the host to carry out once."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .. import chronicle
from ..commands import Form, notes
from ..form_spec import DialogField
from ..markup import escape
from ..models import Saga, Session

#: Hands a request to the host; the reason it was refused, or None.
Submit = Callable[[chronicle.RollRequest], str | None]

STRESS, SIMPLE = "stress", "simple"
#: The most botch dice the form takes (DE p. 8's table goes to ten).
MOST_BOTCH_DICE = 10

FREE_ROLL_HELP = "free-roll"


def character_options(saga: Saga, session: Session, who: str) -> list[tuple[str, str]]:
    """The characters `who` may roll for: a player's own tonight, or for
    the Session's storyguide, no one or any character."""
    if who == chronicle.storyguide_of(session, saga):
        return [("(no one)", "")] + [(escape(c.name), c.id) for c in saga.characters]
    mine = {c.character_id for c in session.castings if c.player_id == who}
    return [(escape(c.name), c.id) for c in saga.characters if c.id in mine]


def visibility_options(saga: Saga, session: Session, who: str) -> list[tuple[str, str]]:
    shown = [
        ("Public: everyone at the Session", chronicle.PUBLIC),
        ("Private: you and the storyguide", chronicle.PRIVATE),
    ]
    if who == chronicle.storyguide_of(session, saga):
        shown.append(("Blind: the number is yours alone", chronicle.BLIND))
    return shown


def _problem(values: dict[str, Any]) -> str | None:
    botch_dice = values.get("botch_dice") or 0
    if not 0 <= botch_dice <= MOST_BOTCH_DICE:
        return f"Botch dice: from 0 to {MOST_BOTCH_DICE}."
    return None


def request_of(values: dict[str, Any]) -> chronicle.RollRequest:
    """The RollRequest the form's values ask for."""
    stress = values.get("die", STRESS) == STRESS
    return chronicle.RollRequest(
        stress=stress,
        modifier=values.get("modifier") or 0,
        botch_dice=(values.get("botch_dice") or 0) if stress else 0,
        ease_factor=values.get("ease_factor"),
        for_what=(values.get("for_what") or "").strip(),
        character_id=values.get("character_id") or "",
        visibility=values.get("visibility") or chronicle.PUBLIC,
    )


def void_form(
    book: chronicle.Chronicle, session: Session, number: int, who: str, saga: Saga
) -> Form:
    """Cancel roll `number` (a Void: it stays in the Chronicle, struck),
    with the reason asked."""

    def apply(values: dict[str, Any]) -> list[str]:
        try:
            chronicle.void(
                book, session, number, values.get("reason") or "", by=who, saga=saga
            )
        except ValueError as problem:
            return notes(str(problem))
        return []

    return Form(
        f"Cancel Roll {number}",
        lambda: [
            DialogField(
                "reason",
                "Reason",
                "text",
                "",
                required=True,
                hint="Why the roll doesn't count. It stays in the Chronicle, "
                "marked Canceled.",
            )
        ],
        apply,
        save_label="Cancel the Roll",
        cancel_label="Keep It",
        help_id=FREE_ROLL_HELP,
    )


def may_roll(saga: Saga, session: Session, who: str) -> bool:
    """Whether `who` has anything to roll for: the Session's storyguide
    always, a player only with a character tonight."""
    return bool(character_options(saga, session, who))


def free_roll_form(saga: Saga, session: Session, who: str, submit: Submit) -> Form:
    """A Free roll by `who` at `session`."""
    characters = character_options(saga, session, who)

    def fields() -> list[DialogField]:
        return [
            DialogField(
                "die",
                "Die",
                "select",
                STRESS,
                options=[("Stress die", STRESS), ("Simple die", SIMPLE)],
            ),
            DialogField(
                "modifier",
                "Modifier",
                "int",
                0,
                hint="Characteristic + Ability + anything else, typed in.",
            ),
            DialogField(
                "botch_dice",
                "Botch dice",
                "int",
                1,
                hint="For a stress die: 1 most of the time, 0 if it can't botch.",
            ),
            DialogField(
                "ease_factor",
                "Ease Factor",
                "optint",
                None,
                hint="Blank for none; with one, the margin is shown.",
            ),
            DialogField("for_what", "For", "text", "", placeholder="Climb the wall"),
            DialogField(
                "character_id",
                "Character",
                "select",
                characters[0][1] if characters else "",
                options=characters,
            ),
            DialogField(
                "visibility",
                "Who sees it",
                "select",
                chronicle.PUBLIC,
                options=visibility_options(saga, session, who),
            ),
        ]

    def apply(values: dict[str, Any]) -> list[str]:
        refused = submit(request_of(values))
        return notes(refused) if refused else []

    return Form(
        "Free Roll",
        fields,
        apply,
        validate=_problem,
        save_label="Roll",
        help_id=FREE_ROLL_HELP,
    )
