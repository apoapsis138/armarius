"""Creation checks for the Later Life step: 15 xp a year from
age 5 to the character's age (a magus: to the start of apprenticeship),
20 if Wealthy, 10 if Poor; spent only on Abilities the character may
learn at this step. Virtue-granted xp and free Ability scores are
recorded here first: each Virtue's own xp on what it names, and the free
first 5 xp in a Supernatural Ability a Virtue grants. Every Ability also
keeps under the creation cap for the character's age.

An animal grog's Later Life runs from the age its kind is grown, at 15
a year, and its cap is advice (rules.animal_grogs).

Rules: reference/rules-engine-reference.md §3 Later life experience;
Creation Ability cap by age; Ability types and who may learn them.
"""

from __future__ import annotations

from .. import catalog
from ..arts import ARTS
from ..models import Character, Saga
from . import animal_grogs
from . import creation_access as access
from . import creation_packages as packages
from .creation_base import CHARACTER_CHECKS, Check, Record, check
from .creation_character import (
    later_life_years,
)
from .creation_virtues import held_option
from .creation_xp import entries, spent

SOURCE = "Ars Magica Definitive Edition, Chapter Three: Characters, Later Life, p. 49"

XP_A_YEAR = 15
WEALTHY_XP, POOR_XP = 20, 10
#: The free xp in a Supernatural Ability its Virtue grants (score 1).
FREE_SUPERNATURAL_XP = 5


def xp_a_year(character: Character) -> int:
    if animal_grogs.is_animal(character):
        return animal_grogs.LATER_XP_A_YEAR
    ids = {vf.vf_id for vf in character.virtues_flaws}
    if "vf_wealthy" in ids:
        return WEALTHY_XP
    if "vf_poor" in ids:
        return POOR_XP
    return XP_A_YEAR


def bought_years(saga: Saga, character: Character) -> int:
    """The Later Life years bought at the xp a year: those the training
    packages don't take."""
    return max(0, later_life_years(saga, character) - packages.years_used(character))


#: A Redcap's fifteen years of apprenticeship gave 300 xp (DE p. 105);
#: a savant has half the xp at creation (DE p. 143).
REDCAP, REDCAP_YEARS, REDCAP_XP = "vf_redcap", 15, 300


def later_life_budget(saga: Saga, character: Character) -> int:
    years, each = bought_years(saga, character), xp_a_year(character)
    ids = {vf.vf_id for vf in character.virtues_flaws}
    if REDCAP in ids:
        apprenticed = min(years, REDCAP_YEARS)
        budget = (years - apprenticed) * each + apprenticed * REDCAP_XP // REDCAP_YEARS
    else:
        budget = years * each
    return budget // 2 if access.SAVANTISM in ids else budget


def later_life_targets(character: Character) -> list[str]:
    """What Later Life xp may buy (an animal's own Language never rises)."""
    return [
        name
        for name in access.learnable_abilities(character, apprenticed=False)
        if not animal_grogs.own_language(character, name)
    ]


def virtue_targets(character: Character, vf_id: str) -> list[str]:
    """What a Virtue's own xp may buy (it may open types normal xp can't)."""
    rule = access.VIRTUE_XP[vf_id]
    found = {
        entry.name
        for entry in catalog.load_ability_catalog()
        if entry.category != access.SUPERNATURAL
        # A family is checked by its prefix ("Area Lore: ").
        and access.virtue_xp_allows(rule, entry.name.split("{", 1)[0])
    }
    # Names from a family ("Dead Language: Latin") the Virtue names itself,
    # and the Arts when it may buy them.
    return sorted(found | set(rule.names)) + (list(ARTS) if rule.arts else [])


def free_score_abilities(character: Character) -> set[str]:
    """The Abilities a Virtue starts at a free score of 1: a Supernatural
    Ability its Virtue grants, and a Mystery Cult House's Ability
    (Heartbeast, Enigmatic Wisdom, Faerie Magic) for a magus holding the
    House's Virtue."""
    abilities = set(access.granted_supernatural(character))
    if character.type == "magus":
        house = catalog.load_house_catalog_by_id().get(character.hermetic.house or "")
        if (
            house is not None
            and house.ability
            and any(held_option(character, o) is not None for o in house.virtues)
        ):
            abilities.add(house.ability)
    return abilities


def free_scores_missing(character: Character) -> list[str]:
    """The Abilities whose free 5 xp isn't recorded."""
    recorded = {x.target for x in entries(character, "free")}
    return sorted(free_score_abilities(character) - recorded)


def _check(
    label: str, ok: bool, detail: str, source: str = SOURCE, *, advice: bool = False
):
    status = "pass" if ok else ("advice" if advice else "warn")
    return Check("later_life", label, status, detail, source)


@check("later_life", CHARACTER_CHECKS)
def later_life_checks(saga: Saga, record: Record) -> list[Check]:
    assert isinstance(record, Character)
    character = record
    budget = later_life_budget(saga, character)
    used = spent(character, "later_life")
    years = bought_years(saga, character)
    found = [
        _check(
            f"Later Life xp: {years} years at {xp_a_year(character)}",
            used <= budget,
            f"{used} of {budget}"
            + (f", {used - budget} too many" if used > budget else ""),
        )
    ]
    if used < budget:
        found.append(
            _check(
                "Later Life xp spent", False, f"{budget - used} unspent", advice=True
            )
        )
    wrong = sorted(
        {
            x.target
            for x in entries(character, "later_life")
            if not access.may_learn(character, x.target)
        }
    )
    if wrong:
        found.append(
            _check(
                "Only Abilities the character may learn",
                False,
                ", ".join(wrong),
                access.SOURCE,
            )
        )
    if access.gifted_non_magus(character):
        extra = {
            x.target
            for x in character.creation_xp
            if access.ability_category(x.target) == access.SUPERNATURAL
            and x.target not in access.granted_supernatural(character)
        }
        found.append(
            _check(
                "One Supernatural Ability without its Virtue (The Gift)",
                len(extra) <= 1,
                f"{len(extra)}",
                access.SOURCE,
            )
        )
    for vf_id, rule in access.virtue_xp(character).items():
        name = access.pool_name(vf_id)
        own = [x for x in entries(character, "virtue") if x.note == vf_id]
        total = sum(x.xp for x in own)
        found.append(
            _check(
                f"{name}: {rule.xp} xp",
                total <= rule.xp,
                f"{total} spent"
                + (f", {total - rule.xp} too many" if total > rule.xp else ""),
            )
        )
        if total < rule.xp:
            found.append(
                _check(
                    f"{name} xp spent",
                    False,
                    f"{rule.xp - total} unspent",
                    advice=True,
                )
            )
        bad = sorted(
            {x.target for x in own if not access.virtue_xp_allows(rule, x.target)}
        )
        if bad:
            found.append(
                _check(f"{name} xp only on what it names", False, ", ".join(bad))
            )
    granted = free_score_abilities(character)
    for entry in entries(character, "free"):
        ok = entry.target in granted and entry.xp == FREE_SUPERNATURAL_XP
        if not ok:
            found.append(
                _check(
                    "Free scores only from Virtues",
                    False,
                    f"{entry.target}: {entry.xp} xp",
                )
            )
    missing = free_scores_missing(character)
    if missing:
        found.append(
            _check(
                "Free Ability scores from Virtues recorded",
                False,
                ", ".join(missing),
                advice=True,
            )
        )
    # An animal's cap is read at its age scaled to a human lifespan, and
    # the book leaves it to the storyguide: advice.
    years = animal_grogs.cap_age(saga, character)
    animal = animal_grogs.is_animal(character)
    cap = access.character_ability_cap(character, years)
    over = []
    for ability in sorted(character.abilities, key=lambda a: a.name):
        own_cap = access.ability_cap_for(character, years, ability.name)
        if own_cap is not None and ability.level > own_cap:
            over.append(
                ability.name if own_cap == cap else f"{ability.name} (cap {own_cap})"
            )
    if access.ability_cap_for(character, years, "") is None:
        label = "No Ability cap at creation (Mentored by Demons)"
    elif any(vf.vf_id == "vf_affinity_with_ability" for vf in character.virtues_flaws):
        label = f"No Ability above {cap} at creation (2 more with an Affinity)"
    else:
        label = f"No Ability above {cap} at creation"
    if animal:
        label += f" (as a person of {years})"
    found.append(
        _check(
            label,
            not over,
            ", ".join(over) or "none above",
            animal_grogs.SOURCE if animal else access.CAP_SOURCE,
            advice=animal,
        )
    )
    return found
