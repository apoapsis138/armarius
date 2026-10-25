"""Art & Academe's diseases (Chapter Three: Medicine), a saga option.

Without the option a disease is a wound (DE p. 406, rules.harm); with it
a disease is its own record:

- **Stages** Minor, Serious, Major and Critical, with Disease Penalties of
  -1, -3, -5 and no action at all; a disease that gives Flaws instead has
  none. Disease Penalties add to Wound Penalties, but a disease's own
  Recovery rolls don't take them (p. 46).
- **Severity**: the stage's base (6, 9, 12, 15) + its Interval (week 0,
  month +1, season +3, lifelong +10) + its Stable Ease Factor (4: -1, 6: 0,
  9: +1, 12: +3) + its Improvement Ease Factor (10: -1, 12: 0, 15: +1, 18:
  +3); each stage worse or better moves it 3 (pp. 46-47).
- **Avoidance**: Stamina + Living Conditions + Corpus / 5 (a magus's Form
  Bonus) + the Wound Penalty + stress die must reach the Stable Ease
  Factor (the DE's equals-or-exceeds, DE p. 7, over A&A's "exceed"); a
  botch catches it a stage worse (p. 46).
- **Recovery**, at the end of each Interval: Stamina + the physician's
  Medicine (only when his Prognosis Total beats the Severity) + Corpus / 5
  + the Wound Penalty + Recovery Modifiers + magical aid + stress die (pp.
  47 and 58 give the two halves of this). Below the Stable Ease Factor it
  worsens a stage; at or over it, +3 to the next roll, cumulative; at or
  over the Improvement Ease Factor it improves a stage, and a Minor one is
  cured. A lifelong disease never changes without the supernatural.
- **Crisis** (Critical): two rolls a day; 0 or less dies within the day,
  at or over the Stable Ease Factor it becomes Major, anything else a
  cumulative -1 to later rolls. A survivor gains an Aging Point in a
  Characteristic the storyguide chooses (p. 47), left due on the record
  until it is placed.
- **Prognosis Total** = the physician's Intelligence + Medicine + the
  patient's Living Conditions + an apothecary's Profession: Apothecary
  (at most 3) + a chirurgeon's Chirurgy (at most 3); no die (p. 58).
- **Recovery Modifiers** (p. 54): living and diet -1 to +1, routinely
  active -1, no medicinal herbs -3 (less an apothecary's Profession:
  Apothecary); each one that applies is an extra botch die.

Pattern: the option chooses which Strategy a disease follows, the DE's
wound or this record.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from ..models import Character, Disease, Saga
from . import derived, dice, options
from .breakdown import Breakdown, Line
from .lab import ability_score

SOURCE = "Art & Academe, Chapter Three: Medicine, Disease, pp. 45-51"
PROGNOSIS_SOURCE = "Art & Academe, Diagnosis and Prognosis, p. 58"
MODIFIERS_SOURCE = "Art & Academe, Recovery Modifiers, p. 54"
SURGERY_SOURCE = "Art & Academe, Chapter Three: Medicine, Surgery, p. 61"
OPTION = "art_academe_medicine"

LEVELS: tuple[str, ...] = ("Minor", "Serious", "Major", "Critical")
CRITICAL = "Critical"
BASE_SEVERITY = {"Minor": 6, "Serious": 9, "Major": 12, "Critical": 15}
PENALTY = derived.DISEASE_PENALTIES
SEVERITY_STEP = 3
INTERVALS: tuple[str, ...] = ("week", "month", "season", "lifelong")
LIFELONG = "lifelong"
INTERVAL_MOD = {"week": 0, "month": 1, "season": 3, "lifelong": 10}
STABLE_MOD = {4: -1, 6: 0, 9: 1, 12: 3}
IMPROVE_MOD = {10: -1, 12: 0, 15: 1, 18: 3}
STABLE_BONUS = 3
CRISIS_DIES = 0
#: Most an apothecary or a chirurgeon adds to the Prognosis Total.
HELPER_MOST = 3
#: The patient's surroundings, as Recovery Modifiers.
CONDITIONS: dict[str, tuple[str, int]] = {
    "poor_living": ("Poor or unsanitary living", -1),
    "wealthy_living": ("Wealthy living or an infirmary", 1),
    "peasant_diet": ("A peasant's diet", -1),
    "noble_diet": ("A noble's or magus's diet", 1),
    "active": ("Routinely active while healing", -1),
    "no_herbs": ("No medicinal herbs", -3),
}
NO_HERBS = "no_herbs"
WEEKS = 13
MONTH_WEEKS = (4, 8, 13)
DAYS = 91


@dataclass(frozen=True)
class DiseaseDef:
    """A disease from the book: its first stage, Severity, Ease Factors and
    Interval; `penalty` False when it gives Flaws instead."""

    name: str
    level: str
    severity: int
    stable: int | None
    improve: int | None
    interval: str
    penalty: bool = True
    note: str = ""
    #: Caught only by a Disease Avoidance roll failed; False for one a
    #: power inflicts (its Penetration decides, not the roll).
    avoidable: bool = True
    #: Long-term Fatigue levels it takes, not regained until it abates.
    fatigue: int = 0


#: Art & Academe's common diseases (pp. 47-51).
CATALOG: tuple[DiseaseDef, ...] = (
    DiseaseDef("The Ague", "Major", 14, 9, 15, "week"),
    DiseaseDef("Anal Fistula", "Minor", 5, 4, 10, "month", note="Needs surgery."),
    DiseaseDef("Apoplexy", "Critical", 16, 6, 15, "week", note="A faerie's elfshot."),
    DiseaseDef("Bloody Flux", "Serious", 9, 6, 12, "week"),
    DiseaseDef(
        "Chaudepysse",
        "Minor",
        9,
        6,
        12,
        "season",
        note="At Major, sterility and impotence.",
    ),
    DiseaseDef("Childbed Fever", "Major", 11, 6, 10, "week"),
    DiseaseDef("Childbed Fever, with complications", "Critical", 14, 6, 10, "week"),
    DiseaseDef("Coryza", "Minor", 4, 4, 10, "week"),
    DiseaseDef(
        "Diabetes",
        "Minor",
        14,
        4,
        None,
        LIFELONG,
        penalty=False,
        note="Faints a few minutes whenever a Fatigue roll fails.",
    ),
    DiseaseDef("Erysipelas", "Minor", 6, 6, 10, "month"),
    DiseaseDef(
        "The Falling Evil",
        "Major",
        16,
        6,
        15,
        "season",
        penalty=False,
        note="Convulsions instead of a penalty: a secret stress die of 9+ in an "
        "event; Stamina against 9 each round ends one.",
    ),
    DiseaseDef("Febris Semitertiana", "Major", 18, 12, 18, "week"),
    DiseaseDef(
        "Gangrene",
        "Minor",
        8,
        9,
        15,
        "week",
        note="Its wound can't improve until it is gone.",
    ),
    DiseaseDef("Garotillo", "Serious", 9, 6, 12, "week"),
    DiseaseDef(
        "Leprosy",
        "Major",
        21,
        None,
        None,
        LIFELONG,
        penalty=False,
        note="Can't be avoided; the Leprosy Flaw: Living Conditions -2, a Heavy "
        "Wound at each Aging Crisis, no positive Reputation, no Recovery rolls.",
    ),
    DiseaseDef("Leprosy, Hermetic", "Critical", 16, 6, 12, "month"),
    DiseaseDef(
        "Phimosis",
        "Minor",
        6,
        6,
        10,
        "month",
        note="A man surviving its Crisis is impotent.",
    ),
    DiseaseDef(
        "Phthisis", "Major", 17, 9, 18, "month", penalty=False, note="Enfeebled."
    ),
    DiseaseDef(
        "Pneumonia",
        "Serious",
        9,
        6,
        12,
        "week",
        note="Winded until it improves; at Major, Enfeebled in place of the penalty.",
    ),
    DiseaseDef(
        "Quinsy",
        "Serious",
        9,
        6,
        10,
        "month",
        note="Afflicted Tongue (penalty -1 at Serious); Mute at Major.",
    ),
    DiseaseDef("Rabies", "Serious", 13, 9, 18, "week"),
    DiseaseDef(
        "Saint Anthony's Fire",
        "Minor",
        12,
        6,
        18,
        "season",
        note="A demon: exorcism ends it; it usually worsens each season.",
    ),
    DiseaseDef(
        "Scrofula", "Serious", 10, 6, 12, "month", note="At Major, Disfigured too."
    ),
    DiseaseDef("Stones", "Serious", 11, 9, 15, "week"),
    DiseaseDef(
        "Suffusio",
        "Serious",
        11,
        9,
        12,
        "month",
        penalty=False,
        note="Poor Eyesight; can't kill, a failed Crisis blinds.",
    ),
    DiseaseDef(
        "Tumor, consumptive",
        "Serious",
        10,
        6,
        12,
        "month",
        note="A roll short of Improvement makes a new Minor tumor.",
    ),
    DiseaseDef(
        "Variola",
        "Serious",
        11,
        9,
        15,
        "week",
        note="Crisis survivors are often blinded or disfigured: the storyguide's call.",
    ),
    DiseaseDef(
        "Worms",
        "Minor",
        9,
        6,
        12,
        "season",
        penalty=False,
        note="No penalty at first; worsening after a season makes it Serious.",
    ),
)
#: A vampire's Sap the Life (Against the Dark p. 115): the Lesser Power
#: inflicts a Serious disease of Severity 15, rolled weekly against 12 to
#: stay stable and 18 to improve, and two Fatigue levels that come back
#: only when it abates; Faerie Lore treats it as well as Medicine.
SAP_THE_LIFE = DiseaseDef(
    "Sap the Life",
    "Serious",
    15,
    12,
    18,
    "week",
    note="A vampire's power: Faerie Lore treats it as Medicine does "
    "(Against the Dark p. 115).",
    avoidable=False,
    fatigue=2,
)
CATALOG = (*CATALOG, SAP_THE_LIFE)
CATALOG_BY_NAME = {d.name: d for d in CATALOG}


def on(saga: Saga | None) -> bool:
    return options.is_on(saga, OPTION)


def severity_of(
    level: str, interval: str, stable: int | None, improve: int | None
) -> int:
    """A disease's Severity from its parts (for one the troupe makes)."""
    return (
        BASE_SEVERITY[level]
        + INTERVAL_MOD.get(interval, 0)
        + STABLE_MOD.get(stable or 0, 0)
        + IMPROVE_MOD.get(improve or 0, 0)
    )


def severity(disease: Disease) -> int:
    """Its Severity now: 3 a stage from where it began."""
    steps = LEVELS.index(disease.level) - LEVELS.index(disease.first_level)
    return disease.severity + SEVERITY_STEP * steps


def penalty(disease: Disease) -> int:
    return PENALTY[disease.level] if disease.penalty else 0


def from_def(found: DiseaseDef, *, worse: bool = False) -> Disease:
    """The record of a disease just caught; `worse` a stage worse (a
    botched avoidance)."""
    level = found.level
    if worse and level != CRITICAL:
        level = LEVELS[LEVELS.index(level) + 1]
    return Disease(
        found.name,
        level=level,
        first_level=found.level,
        severity=found.severity,
        stable=found.stable,
        improve=found.improve,
        interval=found.interval,
        penalty=found.penalty,
        notes=found.note,
    )


def corpus_bonus(character: Character) -> int:
    return derived.form_bonus(character, "Corpus") if character.type == "magus" else 0


def avoidance_total(character: Character, living: int) -> Breakdown:
    """The Disease Avoidance Total before the die; `living` is the
    character's Living Conditions Modifier."""
    lines = [
        Line("Stamina", amount=character.characteristics.stamina, source=SOURCE),
        Line("Living Conditions", amount=living, source=SOURCE),
    ]
    if corpus := corpus_bonus(character):
        lines.append(Line("Corpus Form Bonus", amount=corpus, source=SOURCE))
    if wounded := derived.wound_penalty(
        character.wounds, character.virtues_flaws, diseases=False
    ):
        lines.append(Line("Wound Penalty", amount=wounded, source=SOURCE))
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def avoids(total: int, disease: Disease) -> bool:
    """The avoidance total must reach the Stable Ease Factor (A&A p. 46
    says "exceed", but its own Recovery and Crisis rolls meet or beat theirs,
    and the DE's general rule is equals or exceeds, DE p. 7); with none
    (leprosy) there is no avoiding it."""
    return disease.stable is not None and total >= disease.stable


# -- who treats it --


def _best(saga: Saga | None, character: Character, ability: str) -> Character | None:
    """The covenant-mate (not the patient) with the most `ability`."""
    if saga is None or character.covenant_id is None:
        return None
    found = [
        other
        for other in saga.characters
        if other.id != character.id
        and other.covenant_id == character.covenant_id
        and not other.wounds.dead
        and sum(ability_score(other, ability)) > 0
    ]
    return max(found, key=lambda c: sum(ability_score(c, ability)), default=None)


def _score(character: Character | None, ability: str) -> int:
    return sum(ability_score(character, ability)) if character is not None else 0


def prognosis(saga: Saga | None, character: Character, living: int) -> Breakdown:
    """The covenant's best physician's Prognosis Total for the patient (0
    lines when there is none)."""
    physician = _best(saga, character, "Medicine")
    if physician is None:
        return Breakdown(total=0, lines=[])
    apothecary = min(
        HELPER_MOST,
        _score(
            _best(saga, character, "Profession: Apothecary"), "Profession: Apothecary"
        ),
    )
    chirurgeon = min(
        HELPER_MOST, _score(_best(saga, character, "Chirurgy"), "Chirurgy")
    )
    lines = [
        Line(
            f"Intelligence ({physician.name})",
            amount=physician.characteristics.intelligence,
            source=PROGNOSIS_SOURCE,
        ),
        Line("Medicine", amount=_score(physician, "Medicine"), source=PROGNOSIS_SOURCE),
        Line("Diet (Living Conditions)", amount=living, source=PROGNOSIS_SOURCE),
    ]
    if apothecary:
        lines.append(Line("Apothecary", amount=apothecary, source=PROGNOSIS_SOURCE))
    if chirurgeon:
        lines.append(Line("Chirurgeon", amount=chirurgeon, source=PROGNOSIS_SOURCE))
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def condition_lines(saga: Saga | None, character: Character) -> list[Line]:
    """The Recovery Modifiers of where and how the patient heals; no
    medicinal herbs costs less with an apothecary at the covenant."""
    lines = []
    for key in character.wounds.conditions:
        if key not in CONDITIONS:
            continue
        label, amount = CONDITIONS[key]
        if key == NO_HERBS:
            apothecary = _score(
                _best(saga, character, "Profession: Apothecary"),
                "Profession: Apothecary",
            )
            amount = min(0, amount + apothecary)
        lines.append(Line(label, amount=amount, source=MODIFIERS_SOURCE))
    return lines


def recovery_total(
    saga: Saga | None, character: Character, disease: Disease, living: int
) -> Breakdown:
    """The Disease Recovery Total before the die."""
    lines = [Line("Stamina", amount=character.characteristics.stamina, source=SOURCE)]
    planned = prognosis(saga, character, living)
    if planned.lines and planned.total > severity(disease):
        physician = _best(saga, character, "Medicine")
        lines.append(
            Line(
                f"Medicine ({physician.name if physician else ''})",
                amount=_score(physician, "Medicine"),
                source=PROGNOSIS_SOURCE,
            )
        )
    if corpus := corpus_bonus(character):
        lines.append(Line("Corpus Form Bonus", amount=corpus, source=SOURCE))
    if wounded := derived.wound_penalty(
        character.wounds, character.virtues_flaws, diseases=False
    ):
        lines.append(Line("Wound Penalty", amount=wounded, source=SOURCE))
    lines += condition_lines(saga, character)
    if character.wounds.aid:
        lines.append(Line("Magical aid", amount=character.wounds.aid, source=SOURCE))
    if disease.bonus:
        lines.append(Line("Stable rolls", amount=disease.bonus, source=SOURCE))
    if disease.crisis:
        lines.append(Line("In Crisis", amount=-disease.crisis, source=SOURCE))
    if disease.surgery:
        lines.append(Line("Surgery", amount=disease.surgery, source=SURGERY_SOURCE))
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def botch_dice(character: Character) -> int:
    """One, and one more for each Recovery Modifier that applies."""
    return 1 + sum(1 for key in character.wounds.conditions if key in CONDITIONS)


# -- rolls --


def roll(
    saga: Saga | None,
    character: Character,
    disease: Disease,
    living: int,
    rng: random.Random,
) -> str:
    """One Disease Recovery roll, applied to `disease` (its stage, bonus
    and crisis); "cured" leaves it at stage "" for the caller to drop, and
    a death in Crisis marks the character dead. Returns what happened."""
    if disease.interval == LIFELONG:
        return f"{disease.name} is lifelong: no Recovery roll."
    base = int(recovery_total(saga, character, disease, living).total)
    disease.surgery = 0  # it helps the next roll only
    die = dice.stress_die(rng, botch_dice(character), saga=saga)
    total = base + (0 if die.botched else die.value)
    stable = disease.stable if disease.stable is not None else 0
    improve = disease.improve if disease.improve is not None else stable + 1
    before = disease.level
    if disease.level == CRITICAL:
        if total <= CRISIS_DIES:
            character.wounds.dead = True
            return f"{disease.name}, in Crisis: {total}, the terminal stage: dies."
        if total >= stable:
            disease.level, disease.crisis = "Major", 0
            character.aging.aging_due.append(f"Survived {disease.name}'s Crisis")
            return (
                f"{disease.name}, in Crisis: {total}, the Crisis passes (Major); "
                "an Aging Point in a fitting Characteristic is due (A&A p. 47)."
            )
        disease.crisis += 1
        return f"{disease.name}, in Crisis: {total}, worse (-{disease.crisis})."
    if total >= improve:
        disease.bonus = 0
        if before == "Minor":
            disease.level = ""
            return f"{disease.name}: {total}, cured."
        disease.level = LEVELS[LEVELS.index(before) - 1]
        return f"{disease.name}: {total}, improves to {disease.level}."
    if total >= stable:
        disease.bonus += STABLE_BONUS
        return f"{disease.name}: {total}, holds (+3 to its next rolls)."
    disease.bonus = 0
    disease.level = LEVELS[LEVELS.index(before) + 1]
    crisis = " (a Crisis)" if disease.level == CRITICAL else ""
    return f"{disease.name}: {total}, worsens to {disease.level}{crisis}."


def _due(disease: Disease, week: int) -> bool:
    return (
        disease.interval == "week"
        or (disease.interval == "month" and week in MONTH_WEEKS)
        or (disease.interval == "season" and week == WEEKS)
    )


def season(
    saga: Saga | None, character: Character, living: int, rng: random.Random
) -> list[str]:
    """A season of every disease's rolls: a Crisis twice a day until it
    ends, then each at its Interval week by week."""
    wounds = character.wounds
    lines: list[str] = []
    for disease in list(wounds.diseases):
        if disease.level != CRITICAL:
            continue
        for _ in range(2 * DAYS):
            said = roll(saga, character, disease, living, rng)
            if disease.level != CRITICAL or wounds.dead:
                lines.append(said)
                break
        else:
            lines.append(f"{disease.name}: still in Crisis at the season's end.")
        if wounds.dead:
            return lines
    for week in range(1, WEEKS + 1):
        for disease in wounds.diseases:
            if disease.level and disease.level != CRITICAL and _due(disease, week):
                lines.append(
                    f"Week {week}: " + roll(saga, character, disease, living, rng)
                )
        wounds.diseases = [d for d in wounds.diseases if d.level]
        if wounds.dead:
            break
    return lines


def roll_now(
    saga: Saga | None, character: Character, living: int, rng: random.Random
) -> list[str]:
    """One Recovery roll for each disease now."""
    wounds = character.wounds
    lines = [roll(saga, character, d, living, rng) for d in wounds.diseases]
    wounds.diseases = [d for d in wounds.diseases if d.level]
    return lines


def describe(disease: Disease) -> str:
    """ "Bloody Flux: Serious, Severity 9, -3; rolls weekly, Stable 6,
    Improve 12; +3 from stable rolls." """
    parts = [f"{disease.name}: {disease.level}, Severity {severity(disease)}"]
    parts[0] += f", {penalty(disease)}" if disease.penalty else ", no Disease Penalty"
    if disease.interval == LIFELONG:
        parts.append("lifelong")
    else:
        each = {"week": "weekly", "month": "monthly", "season": "each season"}
        parts.append(
            f"rolls {each.get(disease.interval, disease.interval)}, Stable "
            f"{disease.stable}, Improve {disease.improve}"
        )
    if disease.level == CRITICAL:
        parts.append(
            "in Crisis: two rolls a day"
            + (f", -{disease.crisis}" if disease.crisis else "")
        )
    if disease.bonus:
        parts.append(f"+{disease.bonus} from stable rolls")
    if disease.notes:
        parts.append(disease.notes)
    return "; ".join(parts) + "."
