"""Creation checks for a magus's Apprenticeship step: 240 xp
between Arts and non-Supernatural Abilities (Supernatural ones only with
their Virtue) and 120 levels of spells, each spell no higher than a Lab
Total with an aura of 3 (Technique + Form + Int + Magic Theory + 3, every
Virtue and Flaw that changes a Lab Total applying; with requisites, the
lower Art). A magus must leave apprenticeship with Parma Magica, Magic
Theory and Latin at 1; the book advises Latin 4 and Artes Liberales 1, and
Parma Magica above 1 is very rare.

The worksheet records spells as "apprenticeship_spells" entries (the spell
id, its level); the spell itself is on the Known Spells list.

Rules: reference/rules-engine-reference.md §4 Apprenticeship budget;
Maximum level of a spell learned at creation; Required and recommended
Abilities at Gauntlet.
"""

from __future__ import annotations

from .. import spells as spl
from ..arts import FORMS, TECHNIQUES
from ..models import Character, Laboratory, Saga, Spell
from . import creation_access as access
from . import lab
from .creation_base import CHARACTER_CHECKS, Check, Record, check
from .creation_character import AGING_AGE, age
from .creation_later import DEFAULT_APPRENTICESHIP_AGE
from .creation_xp import entries, is_art, spent

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Magus Only -- "
    "Apprenticeship (https://www.redcap.org/page/Ars_Magica_Definitive_Edition,"
    "_Chapter_Three:_Characters#Magus_Only_%E2%80%94_Apprenticeship)"
)
MINIMUMS_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Hermetic Magi "
    "Recommended Minimum Abilities (https://www.redcap.org/page/Ars_Magica_"
    "Definitive_Edition,_Chapter_Three:_Characters#Hermetic_Magi_Recommended_"
    "Minimum_Abilities)"
)

APPRENTICESHIP_XP = 240
APPRENTICESHIP_LEVELS = 120
#: Skilled Parens adds this much to the apprenticeship.
SKILLED_PARENS_XP, SKILLED_PARENS_LEVELS = 60, 30
CREATION_AURA = 3
LATIN = "Dead Language: Latin"
#: (Ability, score) a magus must have at Gauntlet, and what's advised.
REQUIRED: tuple[tuple[str, int], ...] = (
    ("Parma Magica", 1),
    ("Magic Theory", 1),
    (LATIN, 1),
)
ADVISED: tuple[tuple[str, int], ...] = ((LATIN, 4), ("Artes Liberales", 1))
SPELLS_STEP = "apprenticeship_spells"


def _skilled(character: Character) -> bool:
    return any(vf.vf_id == "vf_skilled_parens" for vf in character.virtues_flaws)


def xp_budget(character: Character) -> int:
    return APPRENTICESHIP_XP + (SKILLED_PARENS_XP if _skilled(character) else 0)


def level_budget(character: Character) -> int:
    return APPRENTICESHIP_LEVELS + (SKILLED_PARENS_LEVELS if _skilled(character) else 0)


def targets(character: Character) -> list[str]:
    """What apprenticeship xp may buy: every Art and the Abilities open to a
    magus in apprenticeship."""
    return [
        *TECHNIQUES,
        *FORMS,
        *access.learnable_abilities(character, apprenticed=True),
    ]


def allowed(character: Character, target: str) -> bool:
    return is_art(target) or access.may_learn(character, target, apprenticed=True)


#: A stand-in laboratory for the creation Lab Total: no covenant, aura 3.
def _creation_lab() -> Laboratory:
    return Laboratory(
        id="_creation", covenant_id=None, name="Creation", aura_modifier=CREATION_AURA
    )


def _score(character: Character, art: str) -> int:
    score, bonus = lab.art_score(character, art)
    return score + bonus


def spell_cap(saga: Saga, character: Character, spell: Spell) -> int:
    """The highest level of `spell` the magus can learn at creation: the
    Lab Total with an aura of 3, using the lower Art where a requisite
    applies."""
    techniques = [spell.technique, *(r for r in spell.requisites if r in TECHNIQUES)]
    forms = [spell.form, *(r for r in spell.requisites if r in FORMS)]
    technique = min(techniques, key=lambda art: _score(character, art))
    form = min(forms, key=lambda art: _score(character, art))
    total = lab.lab_total(
        saga, character, technique, form, _creation_lab(), activity="invent_spells"
    )
    return int(total.total)


def spell_entries(character: Character, step: str = SPELLS_STEP):
    return entries(character, step)


def ability_level(character: Character, name: str) -> int:
    ability = next((a for a in character.abilities if a.name == name), None)
    return ability.level if ability is not None else 0


def _check(label: str, ok: bool, detail: str, source: str = SOURCE, *, advice=False):
    status = "pass" if ok else ("advice" if advice else "warn")
    return Check("apprenticeship", label, status, detail, source)


def spell_checks(saga: Saga, character: Character, step: str) -> list[Check]:
    """Each spell at or under its creation cap (for `step`'s spells)."""
    found = []
    for entry in spell_entries(character, step):
        spell = spl.find_spell(saga, entry.target)
        if spell is None:
            found.append(
                Check(
                    step.removesuffix("_spells"),
                    "Spell exists",
                    "warn",
                    entry.target,
                    SOURCE,
                )
            )
            continue
        cap = spell_cap(saga, character, spell)
        found.append(
            Check(
                step.removesuffix("_spells"),
                f"{spell.name} at most the Lab Total",
                "pass" if entry.xp <= cap else "warn",
                f"level {entry.xp}, Lab Total {cap}",
                SOURCE,
            )
        )
    return found


@check("apprenticeship", CHARACTER_CHECKS)
def apprenticeship_checks(saga: Saga, record: Record) -> list[Check]:
    assert isinstance(record, Character)
    character = record
    budget = xp_budget(character)
    used = spent(character, "apprenticeship")
    found = [
        _check(
            f"Apprenticeship xp: {budget}",
            used <= budget,
            f"{used} spent" + (f", {used - budget} too many" if used > budget else ""),
        )
    ]
    if used < budget:
        found.append(
            _check(
                "Apprenticeship xp spent",
                False,
                f"{budget - used} unspent",
                advice=True,
            )
        )
    wrong = sorted(
        {
            x.target
            for x in entries(character, "apprenticeship")
            if not allowed(character, x.target)
        }
    )
    if wrong:
        found.append(
            _check(
                "Only Arts and Abilities open to an apprentice", False, ", ".join(wrong)
            )
        )
    levels = level_budget(character)
    used_levels = spent(character, SPELLS_STEP)
    found.append(
        _check(
            f"Spell levels: {levels}",
            used_levels <= levels,
            f"{used_levels} learned"
            + (f", {used_levels - levels} too many" if used_levels > levels else ""),
        )
    )
    if used_levels < levels:
        found.append(
            _check(
                "Spell levels spent",
                False,
                f"{levels - used_levels} unspent",
                advice=True,
            )
        )
    found += spell_checks(saga, character, SPELLS_STEP)
    for name, least in REQUIRED:
        level = ability_level(character, name)
        found.append(
            _check(
                f"{name.removeprefix('Dead Language: ')} at least {least}",
                level >= least,
                f"{level}",
                MINIMUMS_SOURCE,
            )
        )
    for name, least in ADVISED:
        level = ability_level(character, name)
        found.append(
            _check(
                f"{name.removeprefix('Dead Language: ')} should be {least} "
                "to read the Order's books",
                level >= least,
                f"{level}" + ("" if level >= least else f", {least - level} too few"),
                MINIMUMS_SOURCE,
                advice=True,
            )
        )
    parma = ability_level(character, "Parma Magica")
    if parma > 1:
        found.append(
            _check(
                "Parma Magica above 1 at Gauntlet is very rare",
                False,
                f"{parma}",
                MINIMUMS_SOURCE,
                advice=True,
            )
        )
    return found


# -- Years past Gauntlet and pre-play aging --

GAUNTLET_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Magus Only -- "
    "After Apprenticeship (https://www.redcap.org/page/Ars_Magica_Definitive_"
    "Edition,_Chapter_Three:_Characters#Magus_Only_%E2%80%94_After_Apprenticeship)"
)
AGING_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Starting "
    "Character Age (https://www.redcap.org/page/Ars_Magica_Definitive_Edition,"
    "_Chapter_Three:_Characters#Starting_Character_Age)"
)
APPRENTICESHIP_YEARS = 15
POINTS_A_YEAR = 30
LAB_SEASON_COST = 10
SEASONS_A_YEAR = 4
GAUNTLET_SPELLS = "gauntlet_spells"


def gauntlet_age(character: Character) -> int:
    """The age the magus passed Gauntlet: the start of apprenticeship
    (10 if not set) plus 15 years."""
    start = character.hermetic.age_of_apprenticeship
    start = start if start is not None else DEFAULT_APPRENTICESHIP_AGE
    return start + APPRENTICESHIP_YEARS


def years_past_gauntlet(saga: Saga, character: Character) -> int:
    years = age(saga, character)
    return max(0, years - gauntlet_age(character)) if years is not None else 0


def lab_season_cost(lab_seasons: int) -> int:
    """The points the lab seasons take, packed four to a year (the most
    efficient way: a year's cost never goes past its 30 points)."""
    full, rest = divmod(lab_seasons, SEASONS_A_YEAR)
    return full * POINTS_A_YEAR + min(POINTS_A_YEAR, rest * LAB_SEASON_COST)


def gauntlet_points(saga: Saga, character: Character) -> int:
    years = years_past_gauntlet(saga, character)
    seasons = character.creation_conditions.lab_seasons
    return max(0, years * POINTS_A_YEAR - lab_season_cost(seasons))


def gauntlet_spent(character: Character) -> int:
    """Points spent: xp in Arts and Abilities, and levels of spells."""
    return spent(character, "gauntlet") + spent(character, GAUNTLET_SPELLS)


def gauntlet_targets(character: Character) -> list[str]:
    return targets(character)


def _g(
    label: str, ok: bool, detail: str, source: str = GAUNTLET_SOURCE, *, advice=False
):
    status = "pass" if ok else ("advice" if advice else "warn")
    return Check("gauntlet", label, status, detail, source)


@check("gauntlet", CHARACTER_CHECKS)
def gauntlet_checks(saga: Saga, record: Record) -> list[Check]:
    assert isinstance(record, Character)
    character = record
    years = years_past_gauntlet(saga, character)
    seasons = character.creation_conditions.lab_seasons
    found = [
        _g(
            "Lab seasons fit in the years past Gauntlet",
            seasons <= years * SEASONS_A_YEAR,
            f"{seasons} of {years * SEASONS_A_YEAR}",
        )
    ]
    points = gauntlet_points(saga, character)
    used = gauntlet_spent(character)
    found.append(
        _g(
            f"Points: {years} years at {POINTS_A_YEAR}, less lab seasons",
            used <= points,
            f"{used} of {points}"
            + (f", {used - points} too many" if used > points else ""),
        )
    )
    if used < points:
        found.append(_g("Points spent", False, f"{points - used} unspent", advice=True))
    wrong = sorted(
        {
            x.target
            for x in entries(character, "gauntlet")
            if not allowed(character, x.target)
        }
    )
    if wrong:
        found.append(
            _g("Only Arts and Abilities open to a magus", False, ", ".join(wrong))
        )
    found += spell_checks(saga, character, GAUNTLET_SPELLS)
    return found


def aging_due(saga: Saga, character: Character) -> int:
    """The pre-play aging rolls not yet made (one a year from 35)."""
    years = age(saga, character)
    if years is None or years <= AGING_AGE:
        return 0
    done = character.creation_conditions.aged_to
    start = AGING_AGE if done is None else done + 1
    return max(0, years - start)


def aging_check(saga: Saga, character: Character, step: str) -> list[Check]:
    years = age(saga, character)
    if years is None or years <= AGING_AGE:
        return []
    due = aging_due(saga, character)
    return [
        Check(
            step,
            "Pre-play aging rolled",
            "pass" if not due else "warn",
            "done" if not due else f"{due} roll(s) to make",
            AGING_SOURCE,
        )
    ]


@check("gauntlet", CHARACTER_CHECKS)
def magus_aging(saga: Saga, record: Record) -> list[Check]:
    assert isinstance(record, Character)
    return aging_check(saga, record, "gauntlet")


@check("finish", CHARACTER_CHECKS)
def other_aging(saga: Saga, record: Record) -> list[Check]:
    """Non-magi make their pre-play aging rolls on the last step."""
    assert isinstance(record, Character)
    if record.type == "magus":
        return []
    return aging_check(saga, record, "finish")
