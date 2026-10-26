"""Experimental philosophy (Art & Academe, Chapter Five, pp. 67-78): the
formulae a philosopher learns and concocts, and the ligatures any scholar
makes. No supernatural aura, vis, Magic Resistance or Warping touches it
(p. 67).

Formulae (pp. 69-71):

- Three kinds, each learned through its Academic Ability: astrological
  **inceptions** (Artes Liberales), alchemical **reagents** (Philosophiae)
  and pharmaceutical **theriacs** (Medicine).
- **Research**: 5 xp in the Ability make a formula; a season practising
  it gives those 5 xp (not Practice's 4). The xp go into the formula
  instead of the Ability.
- **Level**: a base level raised by magnitudes as a Hermetic spell's is
  (5 levels each, 1 below level 5), on its one parameter: an inception's
  Detail (+ the time asked about), a reagent's Alteration (+ size), a
  theriac's Potency (pp. 72, 75, 77).
- **Lab Total** = Intelligence + the Ability + Philosophic Bonuses (Shape
  and Material bonuses, an experiment's Risk Modifier, the laboratory's
  bonuses); the bonuses together never exceed the Ability (pp. 70-71).
- **Concocting**, in a laboratory: the Lab Total must reach the level.
  The first time, each season adds Lab Total - level points; the formula
  is done at points equal to its level, and its Laboratory Text written.
  With the Laboratory Text a season makes Lab Total / 5 doses (rounded
  up), at a Lab Total no lower than the level (p. 71).
- **Ingredients**: each reagent or theriac costs an apothecary's store 1
  Labor Point per 5 levels (or fraction), the level times the doses
  (pp. 75, 77). A&A p. 65 and Errata p. 61 say per 5 of the Ease Factor,
  and the Errata would win, but a formula has no Ease Factor for
  concocting (it is a level against the Lab Total, p. 71); read
  literally it would charge the Rego Craft Finesse roll's level + 9
  (p. 70). Charging by the level is a judgement call against that
  literal reading, agreeing with pp. 75 and 77. An inception is
  parchment and ink: it costs none.

Ligatures (pp. 68-69): a charm for one roll, made in a few hours by anyone
with Artes Liberales, Philosophiae or Medicine (at least 1 in the one it is
tied to): Intelligence + the Ability + a stress die; 9 gives +1, 15 +2, 24
+3 (the most). A botch works against the action: -2 and two more botch
dice, unknown to the maker. One ligature at a time helps a person; none
helps a season's work, and a medical one no Recovery roll. Each costs an
apothecary's store 1 Labor Point.

Inceptions (pp. 72-73, with the Errata p. 61): using one needs the
target's nativity horoscope, a day's work once per target: Intelligence +
Artes Liberales + a die against 9. Then a minute per level of the
inception gives the answer.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Character, Formula, Possession, new_instance_id
from .lab import ability_score
from .rounding import round_up
from .scores import ability_level
from .spell_levels import add_magnitudes

SOURCE = "Art & Academe, Chapter Five: Experimental Philosophy, pp. 67-78"
FORMULA_SOURCE = "Art & Academe, Formulae, pp. 69-71"
LIGATURE_SOURCE = "Art & Academe, Ligatures, pp. 68-69"

INCEPTION, REAGENT, THERIAC = "inception", "reagent", "theriac"
#: Each kind's Academic Ability (p. 69).
KIND_ABILITY: dict[str, str] = {
    INCEPTION: "Artes Liberales",
    REAGENT: "Philosophiae",
    THERIAC: "Medicine",
}
ABILITY_KIND: dict[str, str] = {ability: kind for kind, ability in KIND_ABILITY.items()}

#: The xp that make a formula, and what a season practising it gives.
FORMULA_XP = 5

#: Each kind's parameter and its steps' magnitudes (pp. 72, 75, 77).
DETAIL = (("Binary", 0), ("Basic", 1), ("Brief", 2), ("Thorough", 3))
#: What an inception asks about: the present adds nothing, the past or
#: the future past an astrological month 1, the near future 2 (p. 72).
INCEPTION_TIME = (
    ("The present", 0),
    ("The past", 1),
    ("The distant future", 1),
    ("The near future", 2),
)
ALTERATION = (("Slight", 0), ("Minor", 1), ("Substantial", 2), ("Major", 3))
POTENCY = (("Weak", 0), ("Mild", 1), ("Moderate", 2), ("Strong", 3), ("Mighty", 4))
PARAMETER: dict[str, tuple[str, tuple[tuple[str, int], ...]]] = {
    INCEPTION: ("Detail", DETAIL),
    REAGENT: ("Alteration", ALTERATION),
    THERIAC: ("Potency", POTENCY),
}

#: Levels of a formula per Labor Point of ingredients (A&A pp. 75, 77): by
#: the level, a judgement call against Errata p. 61's literal "Ease Factor".
LEVELS_PER_LABOR_POINT = 5
#: Lab Total per dose made with a Laboratory Text.
LAB_TOTAL_PER_DOSE = 5


def kind_of(ability: str) -> str:
    """The kind of formula an Ability's xp research ("" for another)."""
    return ABILITY_KIND.get(ability, "")


def formula_level(base: int, magnitudes: int) -> int:
    """A formula's level: its guideline's base raised by its magnitudes
    as a Hermetic spell's level is (p. 71)."""
    return add_magnitudes(base, magnitudes)


def parameter_magnitudes(kind: str, step: str) -> int:
    """The magnitudes the kind's parameter adds at `step` (0 if unknown)."""
    _, steps = PARAMETER[kind]
    return dict(steps).get(step, 0)


def design(character: Character, name: str) -> Formula | None:
    """The character's formula of that name, if its design is recorded."""
    return next((f for f in character.formula_designs if f.name == name), None)


@dataclass(frozen=True)
class LabTotal:
    """A philosopher's Lab Total for one kind of formula, and its parts."""

    kind: str
    intelligence: int
    ability: int
    specialty: int
    #: The Philosophic Bonuses typed, and what of them counts (no more
    #: than the Ability).
    bonuses: int
    counted: int

    @property
    def total(self) -> int:
        return self.intelligence + self.ability + self.specialty + self.counted

    def line(self) -> str:
        """The total as a sum: "Int +2 + Philosophiae 5 + 1 + bonuses 4 = 12"."""
        parts = [f"Intelligence {self.intelligence:+d}"]
        parts.append(f"{KIND_ABILITY[self.kind]} {self.ability}")
        if self.specialty:
            parts.append(f"specialty {self.specialty:+d}")
        if self.bonuses:
            capped = (
                f" (of {self.bonuses}: no more than the Ability)"
                if self.counted != self.bonuses
                else ""
            )
            parts.append(f"Philosophic Bonuses {self.counted:+d}{capped}")
        return " + ".join(parts) + f" = {self.total}"


def _specialty(character: Character, ability: str, kind: str) -> int:
    """+1 when the Ability's specialty is the kind of formula ("Reagents")."""
    held = next((a for a in character.abilities if a.name == ability), None)
    specialty = (held.specialty or "").strip().lower() if held else ""
    return 1 if specialty and specialty.startswith(kind) else 0


def lab_total(character: Character, kind: str, bonuses: int = 0) -> LabTotal:
    """Intelligence + the kind's Ability + Philosophic Bonuses, the bonuses
    no more than the Ability's score (pp. 70-71)."""
    ability = KIND_ABILITY[kind]
    score, puissant = ability_score(character, ability)
    counted = min(bonuses, score + puissant)
    return LabTotal(
        kind,
        character.characteristics.intelligence,
        score + puissant,
        _specialty(character, ability, kind),
        bonuses,
        counted,
    )


@dataclass(frozen=True)
class Concoction:
    """What a season concocting a formula does."""

    #: Why it can't be done ("" when it can).
    problem: str = ""
    #: Points toward a first concoction (no Laboratory Text yet).
    points: int = 0
    #: Doses made with the Laboratory Text.
    doses: int = 0


def concoction(total: int, level: int, lab_text: bool) -> Concoction:
    """A season's work on a formula of `level` at Lab Total `total`."""
    if total < level:
        return Concoction(
            f"The Lab Total {total} doesn't reach the formula's level {level}."
        )
    if lab_text:
        return Concoction(doses=round_up(total / LAB_TOTAL_PER_DOSE))
    if total == level:
        return Concoction(
            f"A Lab Total of {total}, just the level, earns no points toward a "
            "first concoction: it must exceed the level."
        )
    return Concoction(points=total - level)


def seasons_to_concoct(total: int, level: int) -> int | None:
    """Seasons to concoct a formula the first time (None: never)."""
    if total <= level or level <= 0:
        return None
    return round_up(level / (total - level))


def labor_cost(kind: str, level: int, doses: int) -> int:
    """The apothecary's Labor Points the ingredients cost: the level times
    the doses / 5, rounded up; none for an inception (pp. 75, 77; the
    level, not Errata p. 61's Ease Factor, is a judgement call)."""
    if kind == INCEPTION:
        return 0
    return round_up(level * doses / LEVELS_PER_LABOR_POINT)


def product_name(formula_name: str, kind: str) -> str:
    """How a formula's doses are named among a character's gear."""
    return f"{formula_name} ({kind})"


def formula_label(character: Character, name: str) -> str:
    """A known formula as the Planning tab lists it: "Cement (reagent 5,
    Laboratory Text)", or its bare name with no design recorded."""
    known = design(character, name)
    if known is None:
        return name
    level = f" {known.level}" if known.level else ""
    text = ", Laboratory Text" if known.lab_text else ""
    return f"{name} ({known.kind}{level}{text})"


def record_work(
    character: Character,
    designs: list[Formula],
    lab_texts: list[str],
    products: list[tuple[str, int]],
) -> None:
    """What a season of experimental philosophy leaves: formulae designed
    (a level typed later fills one set at 0), Laboratory Texts written, and
    doses added to the character's gear (one item per product)."""
    for formula in designs:
        known = design(character, formula.name)
        if known is None:
            character.formula_designs.append(formula)
        elif formula.level and not known.level:
            known.level = formula.level
    for name in lab_texts:
        known = design(character, name)
        if known is not None:
            known.lab_text = True
    for name, doses in products:
        held = next(
            (p for p in character.inventory if p.kind == "item" and p.name == name),
            None,
        )
        if held is not None:
            held.quantity += doses
        else:
            character.inventory.append(
                Possession(new_instance_id(), "item", name, quantity=doses)
            )


# -- theriacs as poisons, and poisons without a formula -----------------------

#: A theriac that wounds: its guideline's level -> the Stamina roll's Ease
#: Factor to resist (p. 77).
POISON_EASE: dict[int, int] = {4: 6, 5: 9, 10: 12}
#: The wound a theriac's Potency causes or treats (p. 77).
POTENCY_WOUND: dict[str, str] = {
    "Mild": "Light",
    "Moderate": "Medium",
    "Strong": "Heavy",
    "Mighty": "Incapacitating",
}
#: The strongest poison made without a formula: a Light Wound, resisted at
#: Ease Factor 6 or less (A&A p. 65); nothing under 3 is a poison (DE p. 406).
SIMPLE_POISON_WOUND = "Light"
SIMPLE_POISON_EASE = 6
LEAST_POISON_EASE = 3


def poison_needs_formula(wound: str, ease: int) -> bool:
    """Whether a poison of this wound and Ease Factor needs its formula."""
    return wound != SIMPLE_POISON_WOUND or ease > SIMPLE_POISON_EASE


# -- ligatures -----------------------------------------------------------------

#: The Abilities a ligature is made with (p. 68).
LIGATURE_ABILITIES = ("Artes Liberales", "Philosophiae", "Medicine")
#: The Ligature Bonus Table: (total reached, bonus), best first (p. 69).
LIGATURE_BONUS = ((24, 3), (15, 2), (9, 1))
#: A botched ligature's penalty, and the extra botch dice it gives.
LIGATURE_BOTCH_PENALTY = -2
LIGATURE_BOTCH_DICE = 2
#: Labor Points of an apothecary's store each ligature takes.
LIGATURE_LABOR = 1


def ligature_base(character: Character, ability: str) -> int:
    """Intelligence + the Ability, the ligature roll before its die."""
    return character.characteristics.intelligence + sum(
        ability_score(character, ability)
    )


def ligature_bonus(total: int) -> int:
    """The bonus a ligature roll's total gives (0 below 9)."""
    return next((bonus for need, bonus in LIGATURE_BONUS if total >= need), 0)


def ligature_abilities(character: Character) -> list[str]:
    """The Abilities the character can make a ligature with (score 1+)."""
    return [a for a in LIGATURE_ABILITIES if ability_level(character, a) >= 1]


# -- inceptions' nativities ----------------------------------------------------

NATIVITY_EASE = 9


def nativity_base(character: Character) -> int:
    """Intelligence + Artes Liberales, the nativity roll before its die."""
    return character.characteristics.intelligence + sum(
        ability_score(character, KIND_ABILITY[INCEPTION])
    )
