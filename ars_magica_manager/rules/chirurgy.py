"""Art & Academe's chirurgy (Chapter Three: Medicine, The Practice of
Chirurgy, pp. 59-62), under the Art & Academe medicine saga option.

- **First aid and palliative care** take the place of the Definitive
  Edition's "medic's Chirurgy" in the Wound Recovery Total (DE p. 405 gives
  the medic's whole Chirurgy): first aid within a day of the wound adds
  half the first-aider's Chirurgy, rounded up; palliative care, the
  ongoing nursing, adds half the nurse's; the two together never exceed
  the Chirurgy of whoever gives the palliative care (pp. 61-62). A
  chirurgeon nurses up to his Chirurgy in patients without losing his
  season, five times that by pushing himself.
- **The First Aid roll**: Dexterity + Chirurgy + Recovery Modifiers +
  magical aid + stress die against the Improvement Ease Factor of the
  patient's worst wound. Success lets the patient act one category less
  injured for a day; a botch gives no first-aid bonus and provokes an
  immediate Recovery roll (p. 61).
- **Surgery** on a disease: Dexterity + Chirurgy + Recovery Modifiers +
  stress die against the procedure's Ease Factor; it always inflicts the
  procedure's wound (a botch one step worse). Success returns the disease
  to the stage it began at and gives +3 to its next Recovery roll; a
  failure or botch leaves it be. Phlebotomy, cautery and cupping help only
  a disease of Severity 5 or less (p. 61).
- **Surgical intervention**, when a Wound Recovery roll fails: the Surgery
  roll against 9. Success turns the failure into a stable result (with its
  +3); a failure lets the wound worsen; a botch worsens it two steps (a
  Medium wound to Incapacitating, anything worse to death). Whatever the
  roll, the patient keeps a consequence by the wound's severity: a Light
  wound an immediate Aging roll, a Medium two Aging Points in a
  Characteristic of the wound's place, a Heavy a Minor Flaw, an
  Incapacitating a Major Flaw (p. 62).
"""

from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass, field

from ..models import Character, Disease, Saga, WoundState
from . import dice, disease
from .breakdown import Breakdown, Line
from .lab import ability_score

SOURCE = "Art & Academe, Chapter Three: Medicine, The Practice of Chirurgy, pp. 59-62"
CARE_SOURCE = "Art & Academe, First Aid and Palliative Care, pp. 61-62"
FIRST_AID_SOURCE = "Art & Academe, First Aid, p. 61"
SURGERY_SOURCE = disease.SURGERY_SOURCE
INTERVENTION_SOURCE = "Art & Academe, Surgical Intervention, p. 62"
OPTION = disease.OPTION

ABILITY = "Chirurgy"
#: The specialties that apply to each use of the Ability (p. 59).
FIRST_AID = "first aid"
PALLIATIVE = "palliative care"
SURGERY = "surgery"
INTERVENTION = "surgical intervention"

#: Surgery on a disease: (procedure, Ease Factor, wound inflicted), the
#: wound "fatigue" for a Fatigue level (p. 61). The Caesarian delivery is
#: midwifery's, not a disease's.
PROCEDURES: tuple[tuple[str, int, str], ...] = (
    ("Phlebotomy", 3, "fatigue"),
    ("Cautery and cupping", 4, "fatigue"),
    ("Removing a rotten tooth", 6, "light"),
    ("Opening tonsils to cure quinsy", 9, "light"),
    ("Couching a cataract", 9, "light"),
    ("Trepanation", 12, "light"),
    ("Removing a gall stone or fistula", 9, "medium"),
    ("Removing a cold or hot tumor", 12, "medium"),
    ("Removing a consumptive tumor", 15, "medium"),
)
PROCEDURES_BY_NAME = {name: (ease, wound) for name, ease, wound in PROCEDURES}
#: Only the most trivial diseases yield to these alone.
TRIVIAL = ("Phlebotomy", "Cautery and cupping")
TRIVIAL_SEVERITY = 5
SURGERY_BONUS = 3
#: A surgery wound one step worse, on a botch.
WORSE_WOUND = {"fatigue": "light", "light": "medium", "medium": "heavy"}

INTERVENTION_EASE = 9
#: Where a wound is: its Major Flaws, Minor Flaws and the Characteristics
#: its Aging Points go into (p. 62).
LOCATIONS: dict[str, tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]] = {
    "head": (
        ("Blind", "Deaf", "Mute"),
        ("Disfigured", "Missing Eye", "Missing Ear"),
        ("intelligence", "perception", "communication", "presence"),
    ),
    "torso": (
        ("Crippled", "Enfeebled"),
        ("Disfigured", "Fragile Constitution"),
        ("stamina", "strength"),
    ),
    "limbs": (
        ("Crippled", "No Hands"),
        ("Disfigured", "Lame", "Missing Hand", "Palsied Hands"),
        ("dexterity", "quickness"),
    ),
}
INTERVENTION_AGING_POINTS = 2


def on(saga: Saga | None) -> bool:
    return disease.on(saga)


def half(score: int) -> int:
    """Half a Chirurgy score, rounded up."""
    return (max(score, 0) + 1) // 2


def chirurgy(character: Character, specialty: str = "") -> int:
    """Chirurgy with its fixed bonus, and +1 when its specialty is this use."""
    score, bonus = ability_score(character, ABILITY)
    if not score:
        return 0
    found = next((a for a in character.abilities if a.name == ABILITY), None)
    special = bool(
        specialty
        and found is not None
        and (found.specialty or "").strip().casefold() == specialty
    )
    return score + bonus + (1 if special else 0)


def chirurgeons(saga: Saga, patient: Character) -> list[Character]:
    """Everyone living with Chirurgy who could tend the patient (the patient
    too, for his own first aid), the most skilled first."""
    found = [
        c
        for c in saga.characters
        if not c.wounds.dead and sum(ability_score(c, ABILITY)) > 0
    ]
    return sorted(found, key=lambda c: (-chirurgy(c), c.id == patient.id))


# -- the Wound Recovery Total --


def care_lines(first_aid: int, nurse: str, nursing: int) -> list[Line]:
    """The Wound Recovery Total's first aid and palliative care: half the
    first-aider's Chirurgy (`first_aid`) and half the nurse's (`nursing`),
    together at most the nurse's Chirurgy (pp. 61-62)."""
    aid = half(first_aid)
    care = half(nursing)
    if nursing and aid + care > nursing:
        aid = max(0, nursing - care)
    lines: list[Line] = []
    if aid:
        lines.append(Line("First aid", amount=aid, source=CARE_SOURCE))
    if care:
        lines.append(
            Line(f"Palliative care ({nurse})", amount=care, source=CARE_SOURCE)
        )
    return lines


def _modifiers(saga: Saga | None, patient: Character) -> list[Line]:
    """The patient's Recovery Modifiers that bear on chirurgy (herbs are
    the physician's)."""
    return [
        line
        for line in disease.condition_lines(saga, patient)
        if line.label != disease.CONDITIONS[disease.NO_HERBS][0]
    ]


def _roll_total(
    saga: Saga | None,
    patient: Character,
    chirurgeon: Character,
    specialty: str,
    source: str,
) -> Breakdown:
    lines = [
        Line(
            f"Dexterity ({chirurgeon.name})",
            amount=chirurgeon.characteristics.dexterity,
            source=source,
        ),
        Line(ABILITY, amount=chirurgy(chirurgeon, specialty), source=source),
        *_modifiers(saga, patient),
    ]
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def first_aid_total(
    saga: Saga | None, patient: Character, chirurgeon: Character
) -> Breakdown:
    """The First Aid roll's total before the die."""
    found = _roll_total(saga, patient, chirurgeon, FIRST_AID, FIRST_AID_SOURCE)
    if patient.wounds.aid:
        found.lines.append(
            Line("Magical aid", amount=patient.wounds.aid, source=FIRST_AID_SOURCE)
        )
        found.total += patient.wounds.aid
    return found


def surgery_total(
    saga: Saga | None, patient: Character, chirurgeon: Character, specialty: str
) -> Breakdown:
    """The Surgery roll's total before the die."""
    return _roll_total(saga, patient, chirurgeon, specialty, SURGERY_SOURCE)


@dataclass
class Rolled:
    """A chirurgeon's roll: its total and whether it succeeded or botched."""

    total: int
    success: bool
    botched: bool


def _roll(
    saga: Saga | None,
    patient: Character,
    base: Breakdown,
    ease: int,
    rng: random.Random,
) -> Rolled:
    die = dice.stress_die(rng, disease.botch_dice(patient), saga=saga)
    result = int(base.total) + (0 if die.botched else die.value)
    return Rolled(result, not die.botched and result >= ease, die.botched)


# -- first aid --


def first_aid(
    saga: Saga | None,
    patient: Character,
    chirurgeon: Character,
    ease: int | None,
    wounds: Sequence[WoundState],
    rng: random.Random,
) -> tuple[Rolled | None, list[str]]:
    """First aid for the patient's injuries (`wounds`, every wound's state,
    as rules.recovery.states gives them): each injury without it yet
    keeps the chirurgeon's Chirurgy for its first-aid bonus, and the roll
    against `ease` (the worst wound's Improvement Ease Factor; None for an
    Incapacitated patient, who can do nothing anyway) says whether he may
    act a category less injured for a day. A botch gives no bonus: the
    caller makes the immediate Recovery roll."""
    rolled = None
    lines: list[str] = []
    if ease is not None:
        rolled = _roll(
            saga, patient, first_aid_total(saga, patient, chirurgeon), ease, rng
        )
        if rolled.botched:
            return rolled, [
                f"First Aid roll by {chirurgeon.name}: botched, no first-aid "
                "bonus and an immediate Recovery roll (A&A p. 61)."
            ]
        lines.append(
            f"First Aid roll by {chirurgeon.name}: {rolled.total} against {ease}, "
            + (
                "a success: for a day the patient may act as if one category "
                "less injured, still taking the Wound Penalty (A&A p. 61)."
                if rolled.success
                else "a failure: no help with activity."
            )
        )
    from_score = chirurgy(chirurgeon, FIRST_AID)
    treated = 0
    for state in wounds:
        if state.source == "injury" and not state.first_aid:
            state.first_aid = from_score
            treated += 1
    if treated:
        lines.append(
            f"First aid: +{half(from_score)} to the wounds' Recovery rolls "
            "(at most the palliative chirurgeon's Chirurgy with his care)."
        )
    else:
        lines.append("No injury left without first aid: no further bonus.")
    return rolled, lines


# -- surgery on a disease --


def surgery_problem(record: Disease, procedure: str) -> str | None:
    """Why a procedure can't help the disease, or None."""
    if procedure not in PROCEDURES_BY_NAME:
        return f"Unknown procedure {procedure!r}."
    if procedure in TRIVIAL and disease.severity(record) > TRIVIAL_SEVERITY:
        return (
            f"{procedure} helps only a disease of Severity {TRIVIAL_SEVERITY} or "
            f"less; {record.name} is Severity {disease.severity(record)} (A&A p. 61)."
        )
    return None


@dataclass
class Operated:
    """A surgery's outcome: the roll, the wound it leaves ("fatigue" for a
    Fatigue level), and what happened in words."""

    rolled: Rolled
    wound: str
    lines: list[str] = field(default_factory=list)


def surgery(
    saga: Saga | None,
    patient: Character,
    chirurgeon: Character,
    record: Disease,
    procedure: str,
    rng: random.Random,
) -> Operated:
    """Surgery on one of the patient's diseases, applied to `record`; the
    caller inflicts the returned wound."""
    ease, wound = PROCEDURES_BY_NAME[procedure]
    rolled = _roll(
        saga, patient, surgery_total(saga, patient, chirurgeon, SURGERY), ease, rng
    )
    said = f"{procedure} by {chirurgeon.name} on {record.name}: {rolled.total} against {ease}"
    if rolled.botched:
        wound = WORSE_WOUND[wound]
        lines = [f"{said}, botched: a worse wound, and the disease is unaffected."]
    elif rolled.success:
        back = record.level != record.first_level
        record.level = record.first_level
        record.surgery = SURGERY_BONUS
        lines = [
            f"{said}, a success: "
            + (f"back to {record.first_level}, " if back else "")
            + "+3 to its next Recovery roll."
        ]
    else:
        lines = [f"{said}, a failure: no benefit."]
    lines.append(
        "It leaves "
        + ("a Fatigue level." if wound == "fatigue" else f"a {wound.title()} Wound.")
    )
    return Operated(rolled, wound, lines)


# -- surgical intervention --


@dataclass
class Consequence:
    """What a surgical intervention leaves for good, by the wound's severity
    before the roll and its place on the body."""

    severity: str
    location: str

    def text(self) -> str:
        major, minor, characteristics = LOCATIONS[self.location]
        where = f"the {self.location}"
        if self.severity == "light":
            return "An immediate Aging roll."
        if self.severity == "medium":
            return (
                f"Two Aging Points in a Characteristic fitting {where} "
                f"({', '.join(c.title() for c in characteristics)}): placed "
                "with Place Aging Points."
            )
        if self.severity == "heavy":
            return f"A Minor Flaw fitting {where}: {_either(minor)}."
        return f"A Major Flaw fitting {where}: {_either(major)}."


def _either(names: tuple[str, ...]) -> str:
    *rest, last = names
    return f"{', '.join(rest)} or {last}" if rest else last


@dataclass
class Surgeon:
    """A chirurgeon standing by to intervene when a Recovery roll fails, the
    wounds' place on the body, and the consequences gathered so far."""

    character: Character
    location: str = "torso"
    consequences: list[Consequence] = field(default_factory=list)


def intervene(
    saga: Saga | None,
    patient: Character,
    surgeon: Surgeon,
    severity: str,
    rng: random.Random,
) -> tuple[str, str]:
    """A surgical intervention on a wound of `severity` whose Recovery roll
    failed: "success", "failure" or "botch", and the words for it. The
    consequence is kept on the surgeon."""
    rolled = _roll(
        saga,
        patient,
        surgery_total(saga, patient, surgeon.character, INTERVENTION),
        INTERVENTION_EASE,
        rng,
    )
    consequence = Consequence(severity, surgeon.location)
    surgeon.consequences.append(consequence)
    said = (
        f"Surgical intervention by {surgeon.character.name}: {rolled.total} "
        f"against {INTERVENTION_EASE}"
    )
    if rolled.botched:
        outcome, how = "botch", "botched, the wound worsens two steps"
    elif rolled.success:
        outcome, how = "success", "the wound holds instead"
    else:
        outcome, how = "failure", "a failure, the wound worsens"
    return outcome, f"{said}, {how}. {consequence.text()}"


def aging_due_lines(
    patient: Character, consequences: list[Consequence], when: str
) -> list[str]:
    """Add the Aging Points a Medium wound's intervention leaves to those
    due (the storyguide places them); the lines saying so."""
    lines: list[str] = []
    for consequence in consequences:
        if consequence.severity != "medium":
            continue
        suggested = LOCATIONS[consequence.location][2][0].title()
        patient.aging.aging_due += [
            f"Surgical intervention on the {consequence.location}, {when} "
            f"(suggested: {suggested})"
        ] * INTERVENTION_AGING_POINTS
        lines.append(
            f"{INTERVENTION_AGING_POINTS} Aging Points due from the surgical "
            f"intervention on the {consequence.location} (Place Aging Points)."
        )
    return lines


def aging_rolls(consequences: list[Consequence]) -> int:
    """How many immediate Aging rolls the interventions call for."""
    return sum(1 for c in consequences if c.severity == "light")
