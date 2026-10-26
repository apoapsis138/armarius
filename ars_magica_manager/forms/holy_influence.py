"""More's Holy Influence on a character's Personality Traits: inspiring a
trait in his followers, or tempering a Divine aura -- no UI in here. The
rules and their pages are rules.holy_influence's (Realms of Power: The
Divine pp. 36-41)."""

from __future__ import annotations

import random
from typing import Any

from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import BULLET, escape
from ..models import Character, DiaryEntry, Saga
from ..rules import dice
from ..rules import holy_influence as holy

TITLE = "Holy Influence"
HELP = "holy-influence"
PERSON, AURA = "person", "aura"


def _bullets(lines: list[str]) -> str:
    return "\n".join(f"{BULLET} {escape(line)}" for line in lines)


def _is_person(values: dict[str, Any]) -> bool:
    return values.get("target", PERSON) == PERSON


def _is_aura(values: dict[str, Any]) -> bool:
    return not _is_person(values)


def _is_ceremony(values: dict[str, Any]) -> bool:
    return values.get("method") == holy.CEREMONY


def fields(character: Character) -> list[DialogField]:
    leaning = holy.temper_scores(character)
    best = max(leaning, key=lambda name: leaning[name], default=holy.TEMPER_NAMES[0])
    return [
        DialogField(
            "target",
            "Influence",
            "select",
            PERSON,
            options=[
                ("Those in his spiritual care (a trait)", PERSON),
                ("A Divine aura (temper it)", AURA),
            ],
        ),
        DialogField(
            "method",
            "How",
            "select",
            holy.SEASON,
            options=[
                ("Personal: a season among them", holy.SEASON),
                (
                    "Ceremonial: a short ceremony, a Faith or Confidence Point",
                    holy.CEREMONY,
                ),
            ],
        ),
        DialogField(
            "authority",
            "His authority over them",
            "select",
            holy.SPIRITUAL,
            options=[
                ("Spiritual: his parish, child, pupil or guest", holy.SPIRITUAL),
                ("Temporal only (Temporal Influence)", holy.TEMPORAL),
                ("None: strangers who will listen (Inspirational)", holy.NONE),
            ],
            show_if=_is_person,
        ),
        DialogField(
            "trait",
            "The trait inspired",
            "text",
            best,
            required=True,
            hint="A virtuous trait, or its temper (Loyal, Calm, Kind, Brave, Wise, "
            "Strong, Just); RoP: The Divine pp. 38-40.",
            show_if=_is_person,
        ),
        DialogField(
            "temper",
            "The temper",
            "select",
            best,
            options=[(f"{t.name} (against {t.sin})", t.name) for t in holy.TEMPERS],
            show_if=_is_aura,
        ),
        DialogField(
            "group",
            "The ceremony's group modifier",
            "int",
            0,
            hint="Others praying with him: everyone's Ceremony less their number, "
            "and each one's Presence + Leadership (p. 36).",
            show_if=_is_ceremony,
        ),
    ]


def lines(character: Character, values: dict[str, Any]) -> list[str]:
    method = str(values.get("method") or holy.SEASON)
    person = _is_person(values)
    group = int(values.get("group") or 0) if method == holy.CEREMONY else 0
    base = holy.influence_total(character, group)
    die = "simple die" if person else "stress die"
    found = [f"Presence + Leadership {base:+d} + {die}: 9 gives +1, 15 +2, 24 +3."]
    if method == holy.CEREMONY:
        point = holy.point_to_spend(character)
        found.append(
            f"The ceremony spends a {point} Point, which adds nothing to the roll."
            if point
            else "A ceremony spends a Faith or Confidence Point, and he has none."
        )
    if person:
        why = holy.may_influence(
            character, str(values.get("authority") or holy.SPIRITUAL), method
        )
        if why:
            found.append(why)
        found.append(
            "Only the willing are touched. The trait "
            f"{holy.lasts(method, temper=False)}; against a Personality Flaw "
            "it never becomes lasting (p. 38)."
        )
    else:
        found.append(
            "The temper adds to every roll in the aura that suits it and takes "
            "from those against it; it "
            f"{holy.lasts(method, temper=True)}. He holds one temper at a time, "
            "a new one replacing his last; another leader's temper in the same "
            "aura is schism (pp. 38, 41). A botch: Warping, Fatigue or a bad name."
        )
    return found


def _live(character: Character):
    return lambda values: _bullets(lines(character, values))


def problem(character: Character, values: dict[str, Any]) -> str | None:
    method = str(values.get("method") or holy.SEASON)
    if _is_person(values):
        why = holy.may_influence(
            character, str(values.get("authority") or holy.SPIRITUAL), method
        )
        return why or None
    if method == holy.CEREMONY and not holy.point_to_spend(character):
        return "A ceremony spends a Faith or Confidence Point, and he has none."
    return None


def influence(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    """The roll, said, and a ceremony's point spent, in the Diary."""
    person = _is_person(values)
    method = str(values.get("method") or holy.SEASON)
    group = int(values.get("group") or 0) if method == holy.CEREMONY else 0
    named = str((values.get("trait") if person else values.get("temper")) or "").strip()
    base = holy.influence_total(character, group)
    rolled = dice.roll(rng, base, stress=not person, saga=saga)
    said: list[str] = []
    if method == holy.CEREMONY:
        point = holy.point_to_spend(character)
        if point == "Faith":
            character.background.faith_points -= 1
            left = character.background.faith_points
        else:
            character.background.confidence_points -= 1
            left = character.background.confidence_points
        said.append(f"A {point} Point spent on the ceremony; {left} left.")
    if rolled.die.botched:
        said.insert(
            0,
            f"Botched ({rolled.die.botches} zero(s)): Warping, Fatigue or a bad "
            "name among the people.",
        )
    else:
        value = holy.influence_value(rolled.total)
        what = "The trait" if person else "The temper"
        said.insert(
            0,
            f"{base:+d} + {rolled.die.value} = {rolled.total}: "
            + (
                f"{what} {named} {value:+d}, which "
                f"{holy.lasts(method, temper=not person)}."
                if value
                else "short of 9: nothing."
            ),
        )
    character.diary.append(
        DiaryEntry(
            saga.current_year,
            saga.current_season,
            TITLE if person else "Holy Temper",
            "\n".join([*said, f"Rules: {holy.SOURCE}"]),
        )
    )
    return notes(*said)


def holy_influence_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Holy Influence: a trait in those in his care, or a temper on
    a Divine aura; Roll rolls it, kept in the Diary."""
    if character is None:
        return Refuse(TITLE, "Choose a character first.")
    chance = rng or random.Random()
    who = character
    return Form(
        f"{TITLE}: {escape(who.name)}",
        lambda: fields(who),
        lambda values: influence(saga, who, values, chance),
        validate=lambda values: problem(who, values),
        live=_live(who),
        save_label="Roll",
        help_id=HELP,
        inspector="The Influence Roll",
    )
