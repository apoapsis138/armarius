"""Turbulence: a Gifted child's untrained Gift lashing out, from Apprentices
(Chapter Three, pp. 22-24; the laboratory's on p. 56, losing the Gift by
the dice on p. 59), while that book is in play.

- **Incurring** (pp. 22-23): when a Gifted character botches a stressful
  activity that includes magic, Intelligence + stress die + the aura's
  modifier (a Turbulence is a Magic power: the Realms Interaction Table,
  DE pp. 410-411) against the higher of the storyguide's stress die (no
  botch) and the character's age. Beating both, he has a Turbulence.
  Only the storyguide's die is no-botch by the book: the player's die,
  and both dice of the control roll, are ordinary stress dice that can
  botch (a botched die counts 0; what else it brings is the troupe's).
  Inside an Aegis of the Hearth he had no part in, half its level comes
  off the roll (p. 24).
- **Forcing** (p. 24): a Confidence Point spent forces the incurring roll
  at will; more Confidence may be spent on either roll (+3 a point, at
  most the Confidence Score on one roll, DE p. 29).
- **Controlling** (p. 23, Stamina per the Errata p. 83): Stamina + stress
  die against Warping Score + stress die; higher controls it. The effect's
  magnitude is half the difference of the two totals, any Technique and
  Form (an Affinity or Puissant Art a good choice). The book gives no
  rounding for an odd difference: rounding down is the app's gap-fill.
- **Penetration** (pp. 23-24): none, unless he has Penetration: its score
  x (1 + the sympathetic multiplier).
- **Turbulence Prone** (p. 12): every potential botch on magic checks for
  one, and he can't control it; its effects are always bad.
- **In the laboratory** (p. 56): an apprentice in a stressful season
  checks midway through it; an uncontrolled one halves his aid to the
  Lab Total. A storyguide character's apprentice may also roll a stress
  die: on a 0, as many botch dice as the parens' Lab Total / 10 (rounded
  up); any 0 and he loses the Gift (p. 59).

A young character's Characteristics take the Aging Chart's modifier
(rules.childhood), as the book's example does (p. 23).

Pattern: plain functions over dice results; the More form (forms.turbulence)
rolls them and keeps the result.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from ..models import Character, Saga, SeasonPlan
from . import childhood, dice, laboratory_seasons, realms
from .breakdown import Line
from .creation_character import age
from .penetration import aegis_penalty
from .rounding import round_down, round_up
from .scores import ability_level

SOURCE = "Apprentices, Chapter Three: Infans, Turbulence, pp. 22-24; Errata, p. 83"
PRONE_SOURCE = (
    "Apprentices, Chapter Two: Child Virtues & Flaws, Turbulence Prone, p. 12"
)
LAB_SOURCE = (
    "Apprentices, Chapter Five: Adulescentia, Laboratory Turbulences, p. 56; "
    "Losing the Gift, p. 59"
)

#: Why a Turbulence is checked for.
BOTCH = "botch"
PRONE = "prone"
FORCED = "forced"
LAB = "lab"
OCCASIONS: dict[str, str] = {
    BOTCH: "A botched stressful roll that includes magic",
    PRONE: "A potential botch on magic (Turbulence Prone)",
    FORCED: "Forced, spending a Confidence Point",
    LAB: "Midway through a stressful laboratory season",
}

#: What a laboratory season's check found, kept on the apprentice's Assist
#: plan (SeasonPlan.turbulence): none, controlled, or uncontrolled (his aid
#: halved).
NONE, CONTROLLED, UNCONTROLLED = "none", "controlled", "uncontrolled"

#: A Confidence Point's bonus to a roll (DE p. 29).
CONFIDENCE_BONUS = 3
#: Pawns of vis that make a laboratory season stressful (p. 56).
STRESSFUL_VIS = 10

AFFINITY = "vf_affinity_with_art"
PUISSANT = "vf_puissant_art"


def gifted(character: Character) -> bool:
    return childhood.gifted(character)


def in_play(saga: Saga | None) -> bool:
    return childhood.in_play(saga)


def prone(character: Character) -> bool:
    return any(vf.vf_id == childhood.TURBULENCE_PRONE for vf in character.virtues_flaws)


def years(saga: Saga, character: Character) -> int | None:
    return age(saga, character)


def characteristic(saga: Saga, character: Character, name: str) -> tuple[int, int]:
    """(score, the Aging Chart's modifier at his age) of a Characteristic."""
    score = getattr(character.characteristics, name.lower())
    old = years(saga, character)
    if old is None:
        return score, 0
    return score, childhood.characteristic_modifier(character, old, name)


def suggested_arts(character: Character) -> list[str]:
    """The Arts an Affinity or Puissant Art names: a good choice for the
    effect (p. 23)."""
    found: list[str] = []
    for vf in character.virtues_flaws:
        if vf.vf_id in (AFFINITY, PUISSANT):
            art = vf.params.get("art", "").strip().title()
            if art and art not in found:
                found.append(art)
    return found


def penetration(character: Character, sympathy: int = 0) -> int:
    """A Turbulence's Penetration: Penetration x (1 + the sympathetic
    multiplier); 0 without the Ability (p. 24)."""
    return ability_level(character, "Penetration") * (1 + max(0, sympathy))


def magnitude_level(magnitude: int) -> str:
    """'level 15' for magnitude 3; a magnitude 0 effect is below level 5."""
    return f"level {5 * magnitude}" if magnitude > 0 else "below level 5"


@dataclass(frozen=True)
class Incurring:
    """The roll to incur a Turbulence: its modifiers, the player's die,
    the storyguide's die and the character's age."""

    lines: tuple[Line, ...]
    die: int
    storyguide: int
    years: int
    #: The player's die botched (the storyguide's can't, p. 22).
    botched: bool = False

    @property
    def modifiers(self) -> int:
        return int(sum(line.amount or 0 for line in self.lines))

    @property
    def total(self) -> int:
        return self.modifiers + self.die

    @property
    def against(self) -> int:
        return max(self.storyguide, self.years)

    @property
    def incurred(self) -> bool:
        return self.total > self.storyguide and self.total > self.years


@dataclass(frozen=True)
class Control:
    """The roll to control a Turbulence: Stamina + stress die against
    Warping Score + stress die."""

    stamina: int
    stamina_die: int
    warping: int
    warping_die: int
    #: Turbulence Prone: he can't control it, whatever the dice say.
    prone: bool = False
    #: Either die botched: both are ordinary stress dice (p. 23).
    stamina_botched: bool = False
    warping_botched: bool = False

    @property
    def player_total(self) -> int:
        return self.stamina + self.stamina_die

    @property
    def warping_total(self) -> int:
        return self.warping + self.warping_die

    @property
    def controlled(self) -> bool:
        return not self.prone and self.player_total > self.warping_total

    @property
    def magnitude(self) -> int:
        """Half the difference of the two totals (p. 23). The book gives no
        rounding for an odd difference; rounding down is the app's
        gap-fill."""
        return abs(self.player_total - self.warping_total) // 2


def incurring_lines(
    saga: Saga,
    character: Character,
    *,
    aura: int,
    aura_realm: str = realms.HERMETIC,
    aegis: int = 0,
    confidence: int = 0,
) -> list[Line]:
    """The terms of the incurring roll: Intelligence (and its age
    modifier), the aura's modifier to a Magic power, an Aegis he had no part
    in, and Confidence spent."""
    score, modifier = characteristic(saga, character, "Intelligence")
    lines = [Line("Intelligence", amount=score, source=SOURCE)]
    if modifier:
        lines.append(
            Line("Age (Aging Chart)", amount=modifier, source=childhood.CHART_SOURCE)
        )
    aura_part = realms.aura_modifier(realms.HERMETIC, aura_realm, aura)
    if aura_part:
        lines.append(
            Line(f"{aura_realm} aura {aura}", amount=aura_part, source=realms.SOURCE)
        )
    if aegis > 0:
        lines.append(
            Line(
                f"Aegis of the Hearth {aegis}",
                amount=aegis_penalty(aegis),
                source=SOURCE,
            )
        )
    if confidence > 0:
        lines.append(
            Line(
                f"Confidence x {confidence}",
                amount=CONFIDENCE_BONUS * confidence,
                source=SOURCE,
            )
        )
    return lines


def control_stamina(saga: Saga, character: Character, confidence: int = 0) -> int:
    """Stamina (with its age modifier) + Confidence spent."""
    score, modifier = characteristic(saga, character, "Stamina")
    return score + modifier + CONFIDENCE_BONUS * max(0, confidence)


def incur(
    saga: Saga,
    character: Character,
    rng: random.Random,
    lines: list[Line],
) -> Incurring:
    """Roll the incurring check: the player's stress die, which can botch,
    and the storyguide's, which can't (p. 22)."""
    old = years(saga, character)
    rolled = dice.stress_die(rng, 1, saga=saga)
    storyguide = dice.stress_die(rng, 0, saga=saga).value
    return Incurring(tuple(lines), rolled.value, storyguide, old or 0, rolled.botched)


def control(
    saga: Saga,
    character: Character,
    rng: random.Random,
    *,
    confidence: int = 0,
    cannot_control: bool = False,
) -> Control:
    """Roll the control check (rolled for the magnitude even when he can't
    control it): two ordinary stress dice, either able to botch (p. 23)."""
    player = dice.stress_die(rng, 1, saga=saga)
    warping = dice.stress_die(rng, 1, saga=saga)
    return Control(
        control_stamina(saga, character, confidence),
        player.value,
        character.aging.warping_score,
        warping.value,
        prone=cannot_control,
        stamina_botched=player.botched,
        warping_botched=warping.botched,
    )


def _die(value: int, botched: bool) -> str:
    return "a botch (0)" if botched else str(value)


def uncontrollable(character: Character, occasion: str) -> bool:
    """Turbulence Prone: a check on a potential (or actual) botch can't be
    controlled (p. 12)."""
    return prone(character) and occasion in (BOTCH, PRONE)


def result_lines(
    character: Character,
    incurring: Incurring,
    controlling: Control | None,
    *,
    sympathy: int = 0,
    occasion: str = BOTCH,
) -> list[str]:
    """What the rolls came to, in plain words."""
    lines = [
        f"Incurring: {incurring.modifiers:+d} + "
        f"{_die(incurring.die, incurring.botched)} = {incurring.total} "
        f"against the storyguide's {incurring.storyguide} and age {incurring.years}: "
        + ("a Turbulence." if incurring.incurred else "no Turbulence.")
    ]
    if incurring.botched:
        lines.append("The player's incurring die botched: the troupe says what else.")
    if controlling is None:
        return lines
    effect = magnitude_level(controlling.magnitude)
    verdict = (
        "controlled: the player chooses the effect, with the storyguide's approval"
        if controlling.controlled
        else "uncontrolled: the storyguide chooses the effect"
        + (", always a bad one" if controlling.prone else "")
    )
    lines.append(
        f"Controlling: Stamina {controlling.stamina:+d} + "
        f"{_die(controlling.stamina_die, controlling.stamina_botched)} = "
        f"{controlling.player_total} against Warping Score {controlling.warping} + "
        f"{_die(controlling.warping_die, controlling.warping_botched)} = "
        f"{controlling.warping_total}"
        + (" (Turbulence Prone: he can't control it)" if controlling.prone else "")
        + f": {verdict}."
    )
    if controlling.stamina_botched or controlling.warping_botched:
        lines.append(
            "A control die botched ("
            + " and ".join(
                side
                for side, botched in (
                    ("Stamina", controlling.stamina_botched),
                    ("Warping", controlling.warping_botched),
                )
                if botched
            )
            + "): the troupe says what else."
        )
    lines.append(
        f"Magnitude {controlling.magnitude} ({effect}, half the difference "
        "rounded down: the app's choice), any Technique and Form."
    )
    arts = suggested_arts(character)
    if arts:
        lines.append(f"A good choice of Art: {', '.join(arts)}.")
    reach = penetration(character, sympathy)
    lines.append(
        f"Penetration {reach}."
        if reach
        else "No Penetration: it can't touch anything with Magic Resistance."
    )
    if occasion == LAB and not controlling.controlled:
        lines.append("His aid to the Lab Total is halved this season.")
    return lines


# -- in the laboratory --


def assist_plan(saga: Saga, character: Character) -> SeasonPlan | None:
    """The character's plan to assist in a laboratory this season."""
    return next(
        (
            p
            for p in saga.season_plans
            if p.character_id == character.id
            and p.activity == laboratory_seasons.ASSIST
            and (p.season, p.year) == (saga.current_season, saga.current_year)
        ),
        None,
    )


def lead_plan(saga: Saga, assisting: SeasonPlan) -> tuple[Character, SeasonPlan] | None:
    """The magus assisted and his plan for the same season."""
    lead = saga.character(assisting.teacher_id)
    if lead is None:
        return None
    plan = next(
        (
            p
            for p in saga.season_plans
            if p.character_id == lead.id
            and (p.season, p.year) == (assisting.season, assisting.year)
        ),
        None,
    )
    return None if plan is None else (lead, plan)


def stressful_reasons(experimenting: bool, vis: int) -> list[str]:
    """What makes the season stressful, of what the plan shows (p. 56):
    experimenting, or more than 10 pawns of vis. Odd hours and a Lab Total
    barely enough are the troupe's call."""
    found: list[str] = []
    if experimenting:
        found.append("the parens experiments")
    if vis > STRESSFUL_VIS:
        found.append(f"{vis} pawns of vis, more than {STRESSFUL_VIS}")
    return found


def aid_halved(saga: Saga | None, helper: Character, plan: SeasonPlan) -> bool:
    """Whether an uncontrolled Turbulence halved `helper`'s aid to the lab
    work planned in `plan` (the lead's plan)."""
    if saga is None:
        return False
    return any(
        p.character_id == helper.id
        and p.activity == laboratory_seasons.ASSIST
        and (p.season, p.year) == (plan.season, plan.year)
        and p.turbulence == UNCONTROLLED
        for p in saga.season_plans
    )


def halved_aid_lines(
    saga: Saga | None, helper: Character, plan: SeasonPlan, aid: list[Line]
) -> list[Line]:
    """Half the helper's aid taken off again after an uncontrolled
    Turbulence (p. 56); nothing otherwise."""
    if not aid_halved(saga, helper, plan):
        return []
    total = int(sum(line.amount or 0 for line in aid))
    if total <= 0:
        return []
    return [
        Line(
            f"{helper.name}'s uncontrolled Turbulence (aid halved)",
            amount=-(total - round_down(total / 2)),
            source=LAB_SOURCE,
        )
    ]


@dataclass(frozen=True)
class GiftRoll:
    """A storyguide character's roll to keep the Gift in a stressful lab
    season (p. 59): the die, and the botch dice's faces on a 0."""

    die: int
    botch_dice: int
    botch_faces: tuple[int, ...] = field(default_factory=tuple)

    @property
    def lost(self) -> bool:
        return 0 in self.botch_faces


def gift_botch_dice(lab_total: int) -> int:
    """The parens' Lab Total / 10, rounded up."""
    return max(0, round_up(lab_total / 10))


def gift_roll(saga: Saga, rng: random.Random, lab_total: int) -> GiftRoll:
    rolled = dice.stress_die(rng, gift_botch_dice(lab_total), saga=saga)
    return GiftRoll(rolled.value, gift_botch_dice(lab_total), rolled.botch_faces)


def gift_roll_line(rolled: GiftRoll) -> str:
    if rolled.die != 0 or not rolled.botch_faces:
        return f"Losing the Gift: the die shows {rolled.die}; the Gift is safe."
    zeros = rolled.botch_faces.count(0)
    if not zeros:
        return (
            f"Losing the Gift: a 0, and {rolled.botch_dice} botch dice show no 0: "
            "the Gift is safe."
        )
    return (
        f"Losing the Gift: a 0, and {zeros} of {rolled.botch_dice} botch dice "
        "show 0: the apprentice loses his Gift (the botches and his place in the "
        "saga say whether for good: More, Lose the Gift)."
    )
