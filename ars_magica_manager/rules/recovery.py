"""Recovery from wounds and Fatigue (DE pp. 403-406).

- **Recovery Total** = Stamina + the medic's Chirurgy (for an injury) or
  Medicine (for a disease, poison or deprivation) + magical aid + stress
  die (DE p. 405). The app adds what the books add to it: the stable rolls'
  +3s, the laboratory's Health for those who live in it (p. 289), a
  familiar's Bronze Cord (p. 267), Virtues such as Rapid Convalescence, and
  minus an Infernal aura's strength where they live (Realms of Power: The
  Infernal p. 12, where a disease never improves). Recovery rolls don't take
  the Wound Penalty.
- **Intervals and Ease Factors**: Light weekly, Stable 4, Improvement 10;
  Medium monthly, 6 and 12; Heavy once a season, 9 and 15. At or over
  Improvement the wound improves a level; at or over Stable it stays, with
  +3 to its later rolls; below, it worsens (infection).
- **Incapacitated**: two rolls a day; 0 or less dies; 9+ makes it Heavy;
  anything else a cumulative -1 to later rolls.
- **A season** plays these out week by week: 13 weeks, a Medium wound
  rolling every fourth week (and the season's last), a Heavy one at the
  season's end, an Incapacitating one first, twice a day until it ends.
- **Fatigue** is rested away within hours (short-term) or a night a level
  (long-term), so a season clears it.

Where Art & Academe disagrees (its first aid and palliative care in place
of the medic's Chirurgy, its own disease system), the Definitive Edition's
rule is used.
"""

from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass, field

from .. import catalog
from ..models import Character, Saga, Wounds, WoundState
from . import dice, effects, lab_stats, realms
from .breakdown import Breakdown, Line
from .lab import ability_score
from .scores import character_source

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Eleven: Obstacles, Recovering "
    "From Wounds, pp. 405-406"
)
HEALTH_SOURCE = "Ars Magica Definitive Edition, Laboratory Health, p. 289"
CORD_SOURCE = "Ars Magica Definitive Edition, Bronze Cord, p. 267"
INFERNAL_SOURCE = "Realms of Power: The Infernal, Effects of an Infernal Aura, p. 12"

INJURY = "injury"
#: The severities wounds take, least first (the incapacitated flag is the
#: last).
SEVERITIES = ("light", "medium", "heavy", "incapacitating")
#: severity -> (interval, Stable Ease Factor, Improvement Ease Factor).
TABLE: dict[str, tuple[str, int, int]] = {
    "light": ("week", 4, 10),
    "medium": ("month", 6, 12),
    "heavy": ("season", 9, 15),
}
STABLE_BONUS = 3
INCAPACITATED_DIES = 0  # a roll of this or less
INCAPACITATED_RECOVERS = 9
WEEKS = 13  # in a season
MONTH_WEEKS = (4, 8, 13)  # when a Medium wound rolls within a season
DAYS = 91


def medic_ability(source: str) -> str:
    """The Ability that tends a wound: Chirurgy for an injury, Medicine for
    the rest (DE p. 405)."""
    return "Chirurgy" if source == INJURY else "Medicine"


# -- the counts and the states --


def states(wounds: Wounds) -> list[WoundState]:
    """Each wound's state, lined up with the counts: the kept states of
    each severity first, then plain injuries for the rest."""
    counts = {
        "light": wounds.light,
        "medium": wounds.medium,
        "heavy": wounds.heavy,
        "incapacitating": 1 if wounds.incapacitated else 0,
    }
    found: list[WoundState] = []
    for severity in SEVERITIES:
        kept = [s for s in wounds.states if s.severity == severity]
        for index in range(counts[severity]):
            found.append(kept[index] if index < len(kept) else WoundState(severity))
    return found


def set_states(wounds: Wounds, found: Sequence[WoundState]) -> None:
    """Make the counts what `found` says, and keep it as the states."""
    wounds.light = sum(s.severity == "light" for s in found)
    wounds.medium = sum(s.severity == "medium" for s in found)
    wounds.heavy = sum(s.severity == "heavy" for s in found)
    wounds.incapacitated = any(s.severity == "incapacitating" for s in found)
    wounds.states = list(found)
    if not wounds.incapacitated:
        wounds.crisis = 0


def add_wound(wounds: Wounds, severity: str, source: str = INJURY) -> None:
    """One more wound of `severity` ("dead" marks the character dead)."""
    if severity == "dead":
        wounds.dead = True
        return
    found = states(wounds)
    if severity == "incapacitating" and wounds.incapacitated:
        return  # one Incapacitating wound is the state, not a count
    found.append(WoundState(severity, source))
    set_states(wounds, found)


# -- the Recovery Total --


def medic(saga: Saga | None, character: Character, ability: str) -> tuple[str, int]:
    """Who tends the wound: the best `ability` among the character's
    covenant-mates (not the patient), with the score; ("", 0) for none."""
    if saga is None or character.covenant_id is None:
        return "", 0
    best = ("", 0)
    for other in saga.characters:
        if other.id == character.id or other.covenant_id != character.covenant_id:
            continue
        if other.wounds.dead:
            continue
        score, bonus = ability_score(other, ability)
        if score + bonus > best[1]:
            best = (other.name, score + bonus)
    return best


def _infernal_aura(saga: Saga | None, character: Character) -> int:
    if saga is None:
        return 0
    aura, realm = realms.home_aura(saga, character)
    return aura if realm == "Infernal" else 0


def total(saga: Saga | None, character: Character, state: WoundState) -> Breakdown:
    """The Recovery Total for one wound, before the stress die."""
    lines = [Line("Stamina", amount=character.characteristics.stamina, source=SOURCE)]
    ability = medic_ability(state.source)
    name, score = medic(saga, character, ability)
    if score:
        lines.append(Line(f"{ability} ({name})", amount=score, source=SOURCE))
    if state.bonus:
        lines.append(Line("Stable rolls", amount=state.bonus, source=SOURCE))
    if character.wounds.aid:
        lines.append(Line("Magical aid", amount=character.wounds.aid, source=SOURCE))
    if saga is not None:
        lab = saga.laboratory(character.assigned_lab_id)
        if lab is not None:
            by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
            health = lab_stats.lab_characteristic_total(lab, by_id, "health", saga)[3]
            if health:
                lines.append(
                    Line("Laboratory Health", amount=health, source=HEALTH_SOURCE)
                )
        familiar = saga.familiar_of(character.id)
        if familiar is not None and familiar.bronze_cord:
            lines.append(
                Line("Bronze Cord", amount=familiar.bronze_cord, source=CORD_SOURCE)
            )
    found = effects.collect([character_source(character.virtues_flaws)], "recovery")
    for effect in found:
        if effect.modifier.amount:
            lines.append(Line(effect.entry.name, amount=effect.modifier.amount))
    infernal = _infernal_aura(saga, character)
    if infernal:
        lines.append(Line("Infernal aura", amount=-infernal, source=INFERNAL_SOURCE))
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


# -- rolls --


@dataclass
class Roll:
    """One Recovery roll: the wound before and after, the total, and what
    happened in words."""

    before: str
    after: str
    total: int
    text: str


def _worse(severity: str) -> str:
    index = SEVERITIES.index(severity)
    return SEVERITIES[min(index + 1, len(SEVERITIES) - 1)]


def roll_wound(
    saga: Saga | None,
    character: Character,
    state: WoundState,
    rng: random.Random,
    *,
    can_improve: bool = True,
) -> Roll:
    """One Recovery roll for a Light, Medium or Heavy wound, applied to
    `state` (its severity and bonus). `can_improve` False is the roll for
    doing more than the wounds allow: it can only stay or worsen."""
    base = int(total(saga, character, state).total)
    die = dice.stress_die(rng, saga=saga)
    value = 0 if die.botched else die.value
    result = base + value
    _, stable, improve = TABLE[state.severity]
    before = state.severity
    disease = state.source != INJURY and _infernal_aura(saga, character) > 0
    if result >= improve and can_improve and not disease:
        state.bonus = 0
        state.severity = (
            "healed" if before == "light" else SEVERITIES[SEVERITIES.index(before) - 1]
        )
        text = "improves" if state.severity != "healed" else "heals"
    elif result >= stable:
        if can_improve:
            state.bonus += STABLE_BONUS
        text = "holds (+3 to its next rolls)" if can_improve else "holds"
    else:
        state.bonus = 0
        state.severity = _worse(before)
        text = "worsens"
    return Roll(
        before, state.severity, result, f"{before.title()} wound {text} ({result})"
    )


def roll_incapacitated(
    saga: Saga | None, character: Character, state: WoundState, rng: random.Random
) -> Roll:
    """One of the twice-daily rolls for an Incapacitating wound, with the
    cumulative -1 kept on the character's wounds."""
    base = int(total(saga, character, state).total) - character.wounds.crisis
    die = dice.stress_die(rng, saga=saga)
    result = base + (0 if die.botched else die.value)
    if result <= INCAPACITATED_DIES:
        character.wounds.dead = True
        return Roll("incapacitating", "dead", result, f"Dies ({result})")
    if result >= INCAPACITATED_RECOVERS:
        state.severity = "heavy"
        state.bonus = 0
        character.wounds.crisis = 0
        return Roll("incapacitating", "heavy", result, f"Improves to Heavy ({result})")
    character.wounds.crisis += 1
    return Roll("incapacitating", "incapacitating", result, f"Worse ({result})")


@dataclass
class Season:
    """A season of recovery: the rolls made, in words, and how it ended."""

    rolls: list[str] = field(default_factory=list)
    died: bool = False


def season(saga: Saga | None, character: Character, rng: random.Random) -> Season:
    """Play out a season's Recovery rolls for every wound (DE p. 405), and
    rest away the Fatigue."""
    character.fatigue_level = "fresh"
    character.long_term_fatigue = 0
    wounds = character.wounds
    found = states(wounds)
    played = Season()
    if wounds.dead or not found:
        return played
    for state in found:
        if state.severity != "incapacitating":
            continue
        for _ in range(2 * DAYS):
            rolled = roll_incapacitated(saga, character, state, rng)
            if rolled.after != "incapacitating":
                played.rolls.append(f"Incapacitated: {rolled.text}")
                break
        else:
            played.rolls.append("Still Incapacitated at the season's end")
        if wounds.dead:
            played.died = True
            set_states(wounds, [s for s in found if s.severity != "incapacitating"])
            return played
    for week in range(1, WEEKS + 1):
        for state in found:
            due = (
                state.severity == "light"
                or (state.severity == "medium" and week in MONTH_WEEKS)
                or (state.severity == "heavy" and week == WEEKS)
            )
            if due:
                rolled = roll_wound(saga, character, state, rng)
                played.rolls.append(f"Week {week}: {rolled.text}")
        found = [s for s in found if s.severity != "healed"]
    set_states(wounds, found)
    return played


def roll_now(
    saga: Saga | None,
    character: Character,
    rng: random.Random,
    *,
    worst_only: bool = False,
) -> list[str]:
    """One Recovery roll for each wound now (a story's moment), or, with
    `worst_only`, for the most serious one only: the roll for doing more
    than the wounds allow, which can't improve it (DE p. 405)."""
    wounds = character.wounds
    found = states(wounds)
    chosen = found[-1:] if worst_only else list(found)
    lines: list[str] = []
    for state in chosen:
        if state.severity == "incapacitating":
            lines.append(roll_incapacitated(saga, character, state, rng).text)
        else:
            rolled = roll_wound(saga, character, state, rng, can_improve=not worst_only)
            lines.append(rolled.text)
    kept = [s for s in found if s.severity != "healed"]
    if wounds.dead:
        kept = [s for s in kept if s.severity != "incapacitating"]
    set_states(wounds, kept)
    return lines
