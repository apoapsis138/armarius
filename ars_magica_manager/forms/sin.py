"""More's Confidence through Sin and Infernal Influence on a character's
Personality Traits -- no UI in here. The rules and their pages are
rules.sin's (Realms of Power: The Infernal pp. 20-24)."""

from __future__ import annotations

import random
from typing import Any

from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import BULLET, escape
from ..models import Character, DiaryEntry, Saga
from ..rules import confidence, dice
from ..rules import sin as sin_rules
from ..seasons.character_effects import gain_warping

SIN_TITLE = "Confidence through Sin"
SIN_HELP = "confidence-through-sin"
INFLUENCE_TITLE = "Infernal Influence"
INFLUENCE_HELP = "infernal-influence"
PERSON, AURA = "person", "aura"


def _bullets(lines: list[str]) -> str:
    return "\n".join(f"{BULLET} {escape(line)}" for line in lines)


def _chosen(character: Character, values: dict[str, Any]) -> sin_rules.SinfulTrait:
    traits = sin_rules.sinful_traits(character)
    wanted = str(values.get("trait") or "")
    return next((t for t in traits if t.label == wanted), traits[0])


# ---------------------------------------------------------------------------
# Confidence through sin


def sin_fields(character: Character) -> list[DialogField]:
    traits = sin_rules.sinful_traits(character)
    return [
        DialogField(
            "trait",
            "The sinful trait",
            "select",
            traits[0].label,
            options=[(t.shown, t.label) for t in traits],
            hint="A Personality Trait or Flaw with a penchant for the sin "
            "(RoP: The Infernal p. 21).",
        ),
        DialogField(
            "method",
            "How he sins",
            "select",
            sin_rules.SEASON,
            options=[(label, key) for key, label in sin_rules.METHODS.items()],
            hint="A season's indulgence goes alongside other work; a ceremony "
            "of a ritualized sin also gives an Infernal Warping Point (p. 24).",
        ),
    ]


def sin_lines(character: Character, values: dict[str, Any]) -> list[str]:
    trait = _chosen(character, values)
    method = str(values.get("method") or sin_rules.SEASON)
    lines = sin_rules.gain_text(trait, method)
    if not sin_rules.has_confidence_score(character):
        lines.append(
            "With no Confidence Score he may still spend the points: on "
            "influence or tarnish, or with the storyguide's leave +1 a point "
            f"to a fitting roll, at most {sin_rules.spend_cap(trait.score)} on "
            "one roll."
        )
    lines += sin_rules.redemption_lines(character)
    return lines


def _sin_live(character: Character):
    return lambda values: _bullets(sin_lines(character, values))


def indulge(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    """The Confidence Point, and a ceremony's Warping Point, kept, with
    a Diary entry."""
    trait = _chosen(character, values)
    method = str(values.get("method") or sin_rules.SEASON)
    points, warping = sin_rules.confidence_through_sin(method)
    confidence.award(character, points)
    said = [
        f"{trait.label}: +{points} Confidence Point through sin; now "
        f"{character.background.confidence_points}."
    ]
    character.diary.append(
        DiaryEntry(
            saga.current_year,
            saga.current_season,
            SIN_TITLE,
            "\n".join(
                [
                    *sin_rules.gain_text(trait, method),
                    *said,
                    f"Rules: {sin_rules.SOURCE}",
                ]
            ),
        )
    )
    if warping:
        said += gain_warping(saga, character, warping, rng, realm="Infernal")
    return notes(*said)


def sin_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Confidence through Sin: the trait and the way; Save keeps
    the Confidence Point (and a ceremony's Warping Point)."""
    if character is None:
        return Refuse(SIN_TITLE, "Choose a character first.")
    if not sin_rules.sinful_traits(character):
        return Refuse(
            SIN_TITLE,
            "Confidence through sin needs a Personality Trait or Flaw with a "
            "penchant for a sin (RoP: The Infernal p. 24).",
        )
    chance = rng or random.Random()
    sinner = character
    return Form(
        f"{SIN_TITLE}: {escape(sinner.name)}",
        lambda: sin_fields(sinner),
        lambda values: indulge(saga, sinner, values, chance),
        live=_sin_live(sinner),
        help_id=SIN_HELP,
        inspector="Sin and Redemption",
    )


# ---------------------------------------------------------------------------
# Infernal influence and tarnish


def _is_person(values: dict[str, Any]) -> bool:
    return values.get("target", PERSON) == PERSON


def influence_fields(character: Character) -> list[DialogField]:
    traits = sin_rules.sinful_traits(character)
    return [
        DialogField(
            "target",
            "Influence",
            "select",
            PERSON,
            options=[
                ("A person who follows his lead", PERSON),
                ("An Infernal aura (tarnish it)", AURA),
            ],
        ),
        DialogField(
            "method",
            "How",
            "select",
            sin_rules.SEASON,
            options=[
                ("Personal: a season in company", sin_rules.SEASON),
                (
                    "Ceremonial: a short ceremony, a Confidence Point",
                    sin_rules.CEREMONY,
                ),
            ],
        ),
        DialogField(
            "trait",
            "The trait awakened",
            "text",
            traits[0].sin if traits else "",
            required=True,
            hint="Any sinful trait; it may seem virtuous (Violent as Brave) or "
            "be a virtue at a negative score (RoP: The Infernal p. 23).",
        ),
        DialogField(
            "stranger",
            "The target is a stranger to him",
            "check",
            False,
            show_if=_is_person,
        ),
    ]


def influence_lines(character: Character, values: dict[str, Any]) -> list[str]:
    method = str(values.get("method") or sin_rules.SEASON)
    person = _is_person(values)
    base = sin_rules.influence_total(character)
    die = "simple die" if person else "stress die"
    lines = [
        f"Presence + Leadership {base:+d} + {die}: 9 gives +1, then +1 every 3 "
        "to +6 at 24."
    ]
    if method == sin_rules.CEREMONY:
        lines.append(
            sin_rules.may_influence_ceremonially(character)
            or (
                "The ceremony spends a Confidence Point "
                f"(he has {character.background.confidence_points})."
            )
        )
    if person:
        lines.append(
            "Only one willing to follow his lead is touched; a character who "
            f"resists is not. The trait {sin_rules.lasts(method, tarnish=False)}."
        )
        if values.get("stranger") and not sin_rules.may_influence_strangers(character):
            lines.append(
                "Strangers only with Inspirational (or within Temporal Influence)."
            )
    else:
        lines.append(
            "The tarnish is added to similar traits of all inside, taken from "
            "opposing ones, gained by anyone with neither; only the strongest "
            f"counts, and it {sin_rules.lasts(method, tarnish=True)}. A botch: "
            "Warping Points or Fatigue (p. 24)."
        )
    return lines


def _influence_live(character: Character):
    return lambda values: _bullets(influence_lines(character, values))


def influence_problem(character: Character, values: dict[str, Any]) -> str | None:
    if values.get("method") == sin_rules.CEREMONY:
        why = sin_rules.may_influence_ceremonially(character)
        if why:
            return why
    if (
        _is_person(values)
        and values.get("stranger")
        and not sin_rules.may_influence_strangers(character)
    ):
        return "Only a character with Inspirational influences strangers (p. 23)."
    return None


def influence(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    """The roll, said, and a ceremony's Confidence Point spent, in the
    Diary."""
    person = _is_person(values)
    method = str(values.get("method") or sin_rules.SEASON)
    trait = str(values.get("trait") or "").strip()
    base = sin_rules.influence_total(character)
    rolled = dice.roll(rng, base, stress=not person, saga=saga)
    lines: list[str] = []
    if method == sin_rules.CEREMONY:
        character.background.confidence_points -= 1
        lines.append(
            "A Confidence Point spent on the ceremony; "
            f"{character.background.confidence_points} left."
        )
    if rolled.die.botched:
        lines.insert(
            0, f"Botched ({rolled.die.botches} zero(s)): Warping Points or Fatigue."
        )
    else:
        value = sin_rules.influence_trait(rolled.total)
        what = "The tarnish" if not person else "The trait"
        lines.insert(
            0,
            f"{base:+d} + {rolled.die.value} = {rolled.total}: "
            + (
                f"{what} {trait} {value:+d}, which "
                f"{sin_rules.lasts(method, tarnish=not person)}."
                if value
                else "short of 9: no trait."
            ),
        )
    character.diary.append(
        DiaryEntry(
            saga.current_year,
            saga.current_season,
            "Tarnish" if not person else INFLUENCE_TITLE,
            "\n".join([*lines, f"Rules: {sin_rules.SOURCE}"]),
        )
    )
    return notes(*lines)


def influence_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Infernal Influence: on a person or an Infernal aura; Roll
    rolls it, kept in the Diary."""
    if character is None:
        return Refuse(INFLUENCE_TITLE, "Choose a character first.")
    chance = rng or random.Random()
    who = character
    return Form(
        f"{INFLUENCE_TITLE}: {escape(who.name)}",
        lambda: influence_fields(who),
        lambda values: influence(saga, who, values, chance),
        validate=lambda values: influence_problem(who, values),
        live=_influence_live(who),
        save_label="Roll",
        help_id=INFLUENCE_HELP,
        inspector="The Influence Roll",
    )
