"""Young characters, from Apprentices (Chapter Two: Creating Young
Characters), while that book is in play:

- **The Aging Chart** (p. 7): below 14 every Characteristic takes a
  modifier and Size is smaller, by age (under 1: -10 and Size -3; 14 and
  over: 0 and 0). Grows Quickly reads Size one age category higher, Late
  Bloomer both one lower, and Deft (Characteristic) halves that one's
  modifier, rounded toward 0 (pp. 11-12). A Size Virtue or Flaw adds to a
  child's Size from the first birthday, never below -3 (p. 10).
- **Child Virtues and Flaws** (p. 11, age 20 and younger per the Errata
  p. 82) are exchanged by the last transition of maturation; **Inherited**
  ones (pp. 10-11) only for magi and companions, manifested by 21. A
  Virtue that grants xp is barred to a character created younger than 14
  (p. 10). Turbulence Prone is only for the Gifted (p. 12).
- **Vocation** (p. 14): from 6 to 14 a child may put xp in the Ability
  his same-sex parent earns a living by, at most half the parent's score.
- **Transitions of maturation** (pp. 14-15) at 8, 15 and 21, in the first
  season of that year: Virtues and Flaws may be exchanged Minor for Minor,
  Major for Major; Child ones must go by 21.
- **The standard apprenticeship model** (p. 14), a saga option
  (options.STANDARD_APPRENTICESHIP): 19 xp a year for the first 12 years,
  then 6 xp and 40 spell levels a year for the last 3, either spendable on
  the other. A Skilled Parens (Teaching Source Quality 18 and a Lab Total
  of 50, p. 10) gives 5 xp and 10 levels a year more, a Weak Parens (8 and
  30) as much less.

The book disagrees with itself on the model: p. 14 gives 19 xp for each
of the first 12 years and 46 (40 spell levels and 6 xp) for each of the
last 3, 246 xp and 120 levels in all; pp. 15-16, as the Errata (pp. 82-83)
corrects them, give 8 xp the first year, 19 for the next eleven and 8 for
each of the last three, 241 xp and 120 levels. The code follows p. 14, the
rule the book gives for making an apprentice part way through.

Pattern: plain functions and check functions registered in the creation
step registry (creation_base.check), like the other creation steps.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .. import catalog, sourcebooks
from ..models import Character, DiaryEntry, Saga, SeasonRecordLine
from . import creation_access as access
from . import effects
from .creation_base import CHARACTER_CHECKS, Check, Record, check, judged
from .creation_character import age
from .scores import ability_level, character_source

BOOK = "App"
CHART_SOURCE = "Apprentices, Chapter Two: Creating Young Characters, Aging Chart, p. 7"
SIZE_SOURCE = (
    "Apprentices, Chapter Two: Creating Young Characters, Virtues & Flaws That "
    "Affect Size, p. 10"
)
CHILD_SOURCE = (
    "Apprentices, Chapter Two: Creating Young Characters, Child Virtues & Flaws, "
    "pp. 11-12; Errata, p. 82"
)
INHERITED_SOURCE = (
    "Apprentices, Chapter Two: Creating Young Characters, Inherited Virtues & "
    "Flaws, pp. 10-11"
)
XP_VIRTUE_SOURCE = (
    "Apprentices, Chapter Two: Creating Young Characters, Virtues That Grant "
    "Experience Points, p. 10"
)
VOCATION_SOURCE = (
    "Apprentices, Chapter Two: Creating Young Characters, Abilities, p. 14"
)
TRANSITION_SOURCE = (
    "Apprentices, Chapter Two: Creating Young Characters, Transitions of "
    "Maturation, pp. 14-15"
)
MODEL_SOURCE = (
    "Apprentices, Chapter Two: Creating Young Characters, Abilities, p. 14; "
    "Skilled Parens and Weak Parens, p. 10"
)
SOURCE = (
    "Apprentices, Chapter Two: Creating Young Characters, pp. 7-16; Errata, pp. 82-83"
)

#: (from age, Characteristic Modifier, Size) for each age category.
AGING_CHART: tuple[tuple[int, int, int], ...] = (
    (0, -10, -3),
    (1, -9, -3),
    (2, -8, -3),
    (3, -7, -2),
    (4, -6, -2),
    (5, -5, -2),
    (6, -4, -2),
    (8, -3, -2),
    (10, -2, -2),
    (12, -1, -1),
    (14, 0, 0),
)
#: No human child is smaller than this.
SMALLEST_SIZE = -3

GROWS_QUICKLY = "vf_grows_quickly"
LATE_BLOOMER = "vf_late_bloomer"
DEFT = "vf_deft_characteristic"
TURBULENCE_PRONE = "vf_turbulence_prone"
CHILD = "Child"
INHERITED = "Inherited"

#: Child Virtues and Flaws are for characters this age and younger.
CHILD_UNTIL = 20
#: Inherited Virtues and Flaws have manifested by this age.
MANIFESTED_BY = 21
#: Virtues that grant xp are barred to characters created younger.
XP_VIRTUE_AGE = 14
#: The ages a child may follow the parent's vocation.
VOCATION_FROM, VOCATION_UNTIL = 6, 14

#: The transitions of maturation: the age entered, and what it ends.
TRANSITIONS: dict[int, str] = {
    8: "infant to child",
    15: "child to adolescent",
    21: "adolescent to adult",
}


def in_play(saga: Saga | None) -> bool:
    return sourcebooks.in_play(BOOK, sourcebooks.saga_books(saga))


def _held(character: Character, vf_id: str) -> bool:
    return any(vf.vf_id == vf_id for vf in character.virtues_flaws)


def _category(years: int) -> int:
    """The Aging Chart row for an age."""
    return max(i for i, (start, _, _) in enumerate(AGING_CHART) if years >= start)


def _row(years: int, shift: int) -> tuple[int, int, int]:
    index = min(max(_category(years) + shift, 0), len(AGING_CHART) - 1)
    return AGING_CHART[index]


def deft_in(character: Character) -> set[str]:
    """The Characteristics (lower case) a Deft Virtue names."""
    return {
        vf.params.get("characteristic", "").strip().lower()
        for vf in character.virtues_flaws
        if vf.vf_id == DEFT
    } - {""}


def characteristic_modifier(
    character: Character, years: int, characteristic: str = ""
) -> int:
    """The Aging Chart's Characteristic Modifier at `years`: one category
    lower for a Late Bloomer, halved toward 0 for the `characteristic` a
    Deft Virtue names."""
    shift = -1 if _held(character, LATE_BLOOMER) else 0
    modifier = _row(years, shift)[1]
    if characteristic.lower() in deft_in(character):
        modifier = -(-modifier // 2)
    return modifier


def virtue_size(character: Character) -> int:
    """What the character's Size Virtues and Flaws add (Large +1...)."""
    found = effects.collect([character_source(character.virtues_flaws)], "size")
    return int(effects.amount_total(found))


def size_for_age(character: Character, years: int) -> int:
    """The character's Size at `years`: the Aging Chart's (one category
    higher with Grows Quickly, lower as a Late Bloomer) plus the Size
    Virtues and Flaws, which start after the first year; never below -3."""
    if years < 1:
        return SMALLEST_SIZE
    shift = _held(character, GROWS_QUICKLY) - _held(character, LATE_BLOOMER)
    return max(SMALLEST_SIZE, _row(years, shift)[2] + virtue_size(character))


def charted(character: Character, years: int) -> bool:
    """Whether the Aging Chart still changes the character at `years`:
    younger than 14, or a Late Bloomer a category behind."""
    return years < AGING_CHART[-1][0] or characteristic_modifier(character, years) != 0


def _names(character: Character, category: str) -> list[str]:
    """The names of the character's Virtues and Flaws of `category`."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    found = []
    for vf in character.virtues_flaws:
        entry = by_id.get(vf.vf_id)
        if entry is not None and entry.category == category:
            name = entry.name
            for key, value in vf.params.items():
                name = name.replace("{" + key + "}", value)
            found.append(name)
    return found


def child_virtues(character: Character) -> list[str]:
    """The character's Child Virtues and Flaws, by name."""
    return _names(character, CHILD)


def inherited_virtues(character: Character) -> list[str]:
    """The character's Inherited Virtues and Flaws, by name."""
    return _names(character, INHERITED)


def gifted(character: Character) -> bool:
    held = {vf.vf_id for vf in character.virtues_flaws}
    return character.type == "magus" or bool(held & catalog.GIFT_IDS)


def _check(
    step: str, label: str, ok: bool, detail: str, source: str, *, advice: bool = False
) -> Check:
    return judged(step, label, ok, detail, source, advice=advice)


@check("virtues_flaws", CHARACTER_CHECKS)
def young_virtue_checks(saga: Saga, record: Record) -> list[Check]:
    """Child, Inherited and xp-granting Virtues for the character's age,
    and Turbulence Prone only for the Gifted."""
    assert isinstance(record, Character)
    character = record
    if not in_play(saga):
        return []
    years = age(saga, character)
    found: list[Check] = []
    child = child_virtues(character)
    if child and years is not None:
        found.append(
            _check(
                "virtues_flaws",
                f"Child Virtues and Flaws only to age {CHILD_UNTIL}",
                years <= CHILD_UNTIL,
                f"age {years}: " + ", ".join(child),
                CHILD_SOURCE,
            )
        )
    inherited = inherited_virtues(character)
    if inherited:
        found.append(
            _check(
                "virtues_flaws",
                "Inherited Virtues and Flaws only for magi and companions",
                character.type != "grog",
                f"{character.type}: " + ", ".join(inherited),
                INHERITED_SOURCE,
            )
        )
        if years is not None:
            found.append(
                _check(
                    "virtues_flaws",
                    f"Inherited Virtues and Flaws manifest by {MANIFESTED_BY}",
                    years < MANIFESTED_BY,
                    f"age {years}: " + ", ".join(inherited),
                    INHERITED_SOURCE,
                )
            )
    pools = access.virtue_xp(character)
    if pools and years is not None and years < XP_VIRTUE_AGE:
        names = sorted({access.pool_name(key) for key in pools})
        found.append(
            _check(
                "virtues_flaws",
                f"No Virtue that grants xp younger than {XP_VIRTUE_AGE}",
                False,
                f"age {years}: " + ", ".join(names),
                XP_VIRTUE_SOURCE,
            )
        )
    if _held(character, TURBULENCE_PRONE) and not gifted(character):
        found.append(
            _check(
                "virtues_flaws",
                "Turbulence Prone only with The Gift",
                False,
                "not Gifted",
                CHILD_SOURCE,
            )
        )
    return found


@check("characteristics", CHARACTER_CHECKS)
def young_characteristic_checks(saga: Saga, record: Record) -> list[Check]:
    """The Aging Chart's Characteristic Modifier and Size for a young
    character's age."""
    assert isinstance(record, Character)
    character = record
    years = age(saga, character)
    if not in_play(saga) or years is None or character.animal is not None:
        return []
    if not charted(character, years):
        return []
    modifier = characteristic_modifier(character, years)
    detail = f"{modifier:+d} to every Characteristic's rolls" + "".join(
        f"; {name.title()} {characteristic_modifier(character, years, name):+d} (Deft)"
        for name in sorted(deft_in(character))
    )
    found = [
        _check(
            "characteristics",
            f"Characteristic Modifier at age {years}",
            True,
            detail,
            CHART_SOURCE,
        )
    ]
    want = size_for_age(character, years)
    # The sheet's Size is the typed base plus the Size Virtues.
    have = character.background.size + virtue_size(character)
    base = want - virtue_size(character)
    found.append(
        _check(
            "characteristics",
            f"Size {want:+d} at age {years}",
            have == want,
            f"Size {have:+d}"
            + ("" if have == want else f": set the base Size to {base:+d}"),
            SIZE_SOURCE,
            advice=True,
        )
    )
    return found


# -- Vocation --


def vocation(character: Character) -> str:
    return character.creation_conditions.vocation.strip()


def vocation_cap(character: Character) -> int:
    """The highest score the parent's vocation lets the child reach to age
    14: half the parent's score, rounded down."""
    return character.creation_conditions.vocation_score // 2


def vocation_offered(saga: Saga, character: Character) -> bool:
    """Whether the worksheet asks for the parent's vocation: a person of
    14 or younger, or one who has it set already."""
    if not in_play(saga) or character.animal is not None:
        return False
    years = age(saga, character)
    young_enough = years is not None and years <= VOCATION_UNTIL
    return young_enough or bool(vocation(character))


def vocational(saga: Saga, character: Character, ability: str) -> bool:
    """Whether `ability` is the vocation the character's parent taught,
    which a child may put xp in although it is of a type he can't learn."""
    name = vocation(character)
    return in_play(saga) and bool(name) and ability == name


@check("later_life", CHARACTER_CHECKS)
def vocation_checks(saga: Saga, record: Record) -> list[Check]:
    """A child's score in the parent's vocation, at most half the parent's
    to age 14."""
    assert isinstance(record, Character)
    character = record
    name = vocation(character)
    years = age(saga, character)
    if not in_play(saga) or not name or years is None or years > VOCATION_UNTIL:
        return []
    cap = vocation_cap(character)
    level = ability_level(character, name)
    parent = character.creation_conditions.vocation_score
    return [
        _check(
            "later_life",
            f"{name} at most half the parent's {parent}",
            level <= cap,
            f"{level} of {cap}",
            VOCATION_SOURCE,
        )
    ]


# -- Transitions of maturation --


def transition(years: int) -> str:
    """The transition of maturation the age `years` begins with ("child to
    adolescent"), or ""."""
    return TRANSITIONS.get(years, "")


def transition_text(character: Character, years: int) -> str:
    """What a transition at `years` allows, and what it requires of the
    character's Child and Inherited Virtues and Flaws."""
    text = (
        f"Turns {years}: a transition of maturation ({transition(years)}). "
        "Virtues and Flaws may be exchanged, Minor for Minor and Major for "
        "Major (not those that changed experience points, nor to a lower Size)."
    )
    child = child_virtues(character)
    if child:
        lead = (
            " Child Virtues and Flaws must be exchanged now: "
            if years >= MANIFESTED_BY
            else " Child Virtues and Flaws may be kept until 21: "
        )
        text += lead + ", ".join(child) + "."
    inherited = inherited_virtues(character)
    if inherited and years >= MANIFESTED_BY:
        text += " Inherited ones must have manifested: " + ", ".join(inherited) + "."
    return text


def year_end_transitions(
    saga: Saga, players: Sequence[Character]
) -> list[SeasonRecordLine]:
    """At the year's end, a line (and a Diary entry) for each of
    `players` entering a transition of maturation next year, made in its
    first season."""
    if not in_play(saga):
        return []
    lines: list[SeasonRecordLine] = []
    for character in players:
        born = character.background.year_born
        if born is None or character.animal is not None:
            continue
        years = saga.current_year + 1 - born
        if not transition(years):
            continue
        text = transition_text(character, years)
        character.diary.append(
            DiaryEntry(
                year=saga.current_year,
                season=saga.current_season,
                name=f"Transition of maturation at {years}",
                details=f"{text}\nRule: {TRANSITION_SOURCE}",
                activity="Aging",
            )
        )
        lines.append(
            SeasonRecordLine(
                character.id,
                character.name,
                character.covenant_id,
                "Transition of maturation",
                transition(years),
                text,
            )
        )
    return lines


# -- The standard apprenticeship model (a saga option) --

MODEL_YEARS = 15
#: The years the parens teaches Arts and Abilities, then spells.
TAUGHT_YEARS = 12
TAUGHT_XP = 19
SPELL_YEAR_XP, SPELL_YEAR_LEVELS = 6, 40
#: What a Skilled Parens adds a year (a Weak one takes away).
PARENS_XP, PARENS_LEVELS = 5, 10


@dataclass(frozen=True)
class ModelBudget:
    """The standard model's apprenticeship so far."""

    years: int
    xp: int
    levels: int

    @property
    def points(self) -> int:
        """xp and spell levels together: either may buy the other."""
        return self.xp + self.levels


def model_budget(years: int, parens: int = 0) -> ModelBudget:
    """The model's xp and spell levels for `years` of apprenticeship
    (at most 15), with a Skilled (+1) or Weak (-1) Parens."""
    years = min(max(years, 0), MODEL_YEARS)
    taught = min(years, TAUGHT_YEARS)
    spells = years - taught
    xp = taught * (TAUGHT_XP + PARENS_XP * parens) + spells * SPELL_YEAR_XP
    levels = spells * (SPELL_YEAR_LEVELS + PARENS_LEVELS * parens)
    return ModelBudget(years, xp, levels)
