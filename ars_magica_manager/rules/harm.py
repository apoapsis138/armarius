"""Harm from more than weapons: injuries, poisons, diseases, deprivation
and, with the Lords of Men option, bruises.

- **Injury** (DE p. 407): a damage bonus + stress die (one botch die, a
  botch doing nothing) against Soak + stress die; the excess is read on the
  Damage Table for the character's Size. Heat and corrosion multiply their
  bonus by how much of the body they cover (x1 a hand, x2 a limb, x3 half
  the body, x4 immersion); falling does +1 per two feet, doubled on a hard
  surface and halved on a soft one.
- **Poison and disease** (DE p. 406, "Debilitation"; City & Guild pp.
  25-28): a Stamina check (stress die) against the agent's Ease Factor;
  failure inflicts its wound, which heals with Medicine. A disease spirit's
  is a magical attack, resisted by Magic Resistance first.
- **Deprivation** of air (30 seconds), water (a day) or food (three days),
  for some number of those periods (DE p. 407): a Stamina check each period
  against 3, then 1 more each period; a failure costs a Fatigue level
  (long-term for food and water); once unconscious each failure is a Light
  Wound, the next one a level worse.
- **Bruise** (Lords of Men pp. 131-132, an optional rule): the blow's
  excess read on the Damage Table as a bruise, which heals within hours and
  leaves a residual wound when it first improves (Heavy: Light;
  Incapacitating: Medium; Fatal: Incapacitating).

Pattern: each kind is a Strategy, a function kept in HARMS by its name.
"""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from ..models import FATIGUE_LEVELS, Character, Saga
from . import derived, dice, disease, living, options, recovery

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Eleven: Obstacles, Other Perils, "
    "pp. 406-407"
)
BRUISE_SOURCE = "Lords of Men, Chapter Nine: Non-Lethal Combat, pp. 131-132"
BRUISES_OPTION = "bruises"

INJURY, POISON, DISEASE, DEPRIVATION, BRUISE = (
    "injury",
    "poison",
    "disease",
    "deprivation",
    "bruise",
)

#: (name, damage bonus) from the Heat and Corrosion table (DE p. 407).
HEAT: tuple[tuple[str, int], ...] = (
    ("Wood fire", 5),
    ("Boiling water", 3),
    ("Boiling oil", 6),
    ("Molten lead", 9),
    ("Molten iron", 12),
    ("Ice", 1),
    ("Lye", 3),
    ("Quicklime", 6),
    ("Vitriol", 9),
)
#: How much of the body it covers -> the multiple of its bonus.
COVERAGE: tuple[tuple[str, int], ...] = (
    ("A hand or foot", 1),
    ("A limb", 2),
    ("Half the body", 3),
    ("All of it", 4),
)
#: The Impact table's examples (DE p. 407).
IMPACT: tuple[tuple[str, int], ...] = (
    ("Jug dropped from a second floor", 6),
    ("Inside a collapsing wooden house", 15),
    ("Mature tree felled onto the character", 18),
    ("Inside a collapsing stone building", 21),
)
#: (name, Ease Factor, wound) from the Poison table (DE p. 406).
POISONS: tuple[tuple[str, int, str], ...] = (
    ("Adder bite", 6, "light"),
    ("Asp bite", 9, "incapacitating"),
    ("Monkshood", 9, "heavy"),
    ("Arsenic", 9, "medium"),
)
#: (name, Ease Factor, wound) for City & Guild's diseases (pp. 27-28); the
#: Ague and Bloody Flux take the air's strength.
DISEASES: tuple[tuple[str, int, str], ...] = (
    ("The Ague, continual fever (bad air 3/6/9)", 6, "heavy"),
    ("The Ague, other fevers (bad air 3/6/9)", 6, "medium"),
    ("Bloody Flux, mild", 3, "medium"),
    ("Bloody Flux", 6, "heavy"),
    ("Bloody Flux, severe", 9, "incapacitating"),
    ("Childbed Fever (a demon; Magic Resistance resists)", 6, "heavy"),
    ("Childbed Fever with complications", 6, "incapacitating"),
    ("Worms (each season)", 6, "medium"),
    ("St. Anthony's Fire (a magical attack)", 9, "light"),
)
#: (kind, the check's period) for deprivation (DE p. 407).
DEPRIVATIONS: tuple[tuple[str, str], ...] = (
    ("air", "30 seconds"),
    ("water", "a day"),
    ("food", "three days"),
)
#: A bruise's residual wound (Lords of Men p. 132).
RESIDUAL: dict[str, str | None] = {
    "light": None,
    "medium": None,
    "heavy": "light",
    "incapacitating": "medium",
    "fatal": "incapacitating",
}
SEVERITY_OF_BAND = {
    "Light": "light",
    "Medium": "medium",
    "Heavy": "heavy",
    "Incapacitating": "incapacitating",
    "Dead": "dead",
}


@dataclass
class Harmed:
    """What befell the character, in words, and the wounds it left."""

    lines: list[str] = field(default_factory=list)
    wounds: list[str] = field(default_factory=list)


def _stamina_check(
    character: Character, ease: int, rng: random.Random, saga: Saga | None
) -> tuple[int, bool]:
    die = dice.stress_die(rng, saga=saga)
    result = character.characteristics.stamina + (0 if die.botched else die.value)
    return result, not die.botched and result >= ease


def damage(
    character: Character,
    bonus: int,
    rng: random.Random,
    saga: Saga | None = None,
    *,
    armour: bool = True,
) -> tuple[int, int, str | None]:
    """A non-combat blow: (damage total, soak total, the wound it deals or
    None). `armour` False leaves the armour out of Soak (boiling water)."""
    die = dice.stress_die(rng, saga=saga)
    hit = 0 if die.botched else bonus + die.value
    soak = derived.soak(character)
    worn = derived.worn_armour(character.inventory)
    base = int(soak.total)
    if not armour and worn is not None:
        base -= worn.armor_protection
    guard = dice.stress_die(rng, 0, saga=saga)
    soaked = base + guard.value
    size = int(derived.size(character).total)
    band = derived.wound_for(hit - soaked, size)
    return hit, soaked, SEVERITY_OF_BAND[band] if band is not None else None


def injury(
    saga: Saga | None, character: Character, values: dict[str, Any], rng: random.Random
) -> Harmed:
    bonus = int(values.get("bonus") or 0) * int(values.get("coverage") or 1)
    hit, soaked, wound = damage(
        character, bonus, rng, saga, armour=bool(values.get("armour", True))
    )
    done = Harmed([f"Damage {hit} against Soak {soaked}"])
    if wound is None:
        done.lines.append("No wound.")
        return done
    recovery.add_wound(character.wounds, wound)
    done.wounds.append(wound)
    done.lines.append(
        "Killed outright." if wound == "dead" else f"A {wound.title()} Wound."
    )
    return done


def _debilitation(source: str) -> Callable[..., Harmed]:
    def apply(
        saga: Saga | None,
        character: Character,
        values: dict[str, Any],
        rng: random.Random,
    ) -> Harmed:
        ease = int(values.get("ease") or 0)
        wound = str(values.get("wound") or "light")
        result, resisted = _stamina_check(character, ease, rng, saga)
        done = Harmed([f"Stamina check {result} against {ease}"])
        if resisted:
            done.lines.append("Resisted: nothing more than discomfort.")
            return done
        recovery.add_wound(character.wounds, wound, source)
        done.wounds.append(wound)
        done.lines.append(f"A {wound.title()} Wound ({source}), healed with Medicine.")
        return done

    return apply


def _lose_fatigue(character: Character, long_term: bool) -> bool:
    """One Fatigue level more; whether the character was already
    unconscious."""
    at = FATIGUE_LEVELS.index(character.fatigue_level)
    if at >= len(FATIGUE_LEVELS) - 1:
        return True
    character.fatigue_level = FATIGUE_LEVELS[at + 1]
    if long_term:
        character.long_term_fatigue = min(
            character.long_term_fatigue + 1, len(FATIGUE_LEVELS) - 1
        )
    return False


def deprivation(
    saga: Saga | None, character: Character, values: dict[str, Any], rng: random.Random
) -> Harmed:
    kind = str(values.get("kind") or "food")
    periods = max(1, int(values.get("periods") or 1))
    long_term = kind != "air"
    done = Harmed()
    worsening = "light"
    for period in range(1, periods + 1):
        ease = 3 + period - 1
        result, resisted = _stamina_check(character, ease, rng, saga)
        if resisted:
            done.lines.append(f"Period {period}: {result} against {ease}, holds out.")
            continue
        if _lose_fatigue(character, long_term):
            recovery.add_wound(character.wounds, worsening, "deprivation")
            done.wounds.append(worsening)
            done.lines.append(
                f"Period {period}: {result} against {ease}, a {worsening.title()} Wound."
            )
            index = recovery.SEVERITIES.index(worsening)
            worsening = recovery.SEVERITIES[
                min(index + 1, len(recovery.SEVERITIES) - 1)
            ]
        else:
            done.lines.append(
                f"Period {period}: {result} against {ease}, "
                f"{'a long-term' if long_term else 'a'} Fatigue level "
                f"({character.fatigue_level.title()})."
            )
    return done


def bruise(
    saga: Saga | None, character: Character, values: dict[str, Any], rng: random.Random
) -> Harmed:
    bonus = int(values.get("bonus") or 0)
    hit, soaked, wound = damage(character, bonus, rng, saga)
    done = Harmed([f"Damage {hit} against Soak {soaked}"])
    if wound is None:
        done.lines.append("No bruise.")
        return done
    severity = "fatal" if wound == "dead" else wound
    bruises = character.wounds.bruises
    bruises[severity] = bruises.get(severity, 0) + 1
    done.lines.append(f"A {severity.title()} Bruise.")
    return done


def catch_disease(
    saga: Saga | None,
    character: Character,
    values: dict[str, Any],
    rng: random.Random,
) -> Harmed:
    """Art & Academe's Disease Avoidance roll (p. 46): Stamina + Living
    Conditions + Corpus / 5 + the Wound Penalty + stress die must exceed
    the Stable Ease Factor; failing catches the disease as its own record,
    a botch a stage worse."""
    found = disease.CATALOG_BY_NAME.get(str(values.get("aa_disease") or ""))
    if found is None:
        level = str(values.get("level") or "Minor")
        interval = str(values.get("interval") or "week")
        stable = values.get("stable")
        improve = values.get("improve") if interval != disease.LIFELONG else None
        found = disease.DiseaseDef(
            str(values.get("name") or "A disease"),
            level,
            disease.severity_of(level, interval, stable, improve),
            stable,
            improve,
            interval,
        )
    living_now = living.living_conditions(saga, character) if saga is not None else 0
    total = int(disease.avoidance_total(character, living_now).total)
    die = dice.stress_die(rng, saga=saga)
    rolled = total + (0 if die.botched else die.value)
    caught = disease.from_def(found, worse=die.botched)
    if found.stable is None:
        done = Harmed([f"{found.name} can't be avoided."])
    else:
        done = Harmed([f"Disease Avoidance {rolled} against {found.stable}"])
        if disease.avoids(rolled, caught):
            done.lines.append("Avoided.")
            return done
    if die.botched:
        done.lines.append("Botched: caught a stage worse.")
    character.wounds.diseases.append(caught)
    done.wounds.append(caught.level.lower())
    done.lines.append(disease.describe(caught))
    return done


HARMS: dict[str, Callable[..., Harmed]] = {
    INJURY: injury,
    POISON: _debilitation(POISON),
    DISEASE: _debilitation(DISEASE),
    DEPRIVATION: deprivation,
    BRUISE: bruise,
}


def kinds(saga: Saga | None) -> list[str]:
    """The kinds of harm the saga offers: bruises only with their option."""
    return [k for k in HARMS if k != BRUISE or options.is_on(saga, BRUISES_OPTION)]


def apply(
    saga: Saga | None,
    character: Character,
    kind: str,
    values: dict[str, Any],
    rng: random.Random,
) -> Harmed:
    """Harm the character by `kind`'s rule: a disease by Art & Academe's
    when its option is on."""
    if kind == DISEASE and disease.on(saga):
        return catch_disease(saga, character, values, rng)
    return HARMS[kind](saga, character, values, rng)


def heal_bruises(character: Character) -> list[str]:
    """Bruises heal within hours, each leaving its residual wound; a season
    always outlasts them."""
    lines: list[str] = []
    for severity, count in sorted(character.wounds.bruises.items()):
        residual = RESIDUAL.get(severity)
        for _ in range(count):
            if residual is not None:
                recovery.add_wound(character.wounds, residual)
                lines.append(
                    f"A {severity.title()} Bruise left a {residual.title()} Wound."
                )
    character.wounds.bruises = {}
    return lines
