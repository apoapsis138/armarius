"""Creation checks for the Later Life step: 15 xp a year from
age 5 to the character's age (a magus: to the start of apprenticeship),
20 if Wealthy, 10 if Poor; spent only on Abilities the character may
learn at this step. Virtue-granted xp and free Ability scores are
recorded here first: each Virtue's own xp on what it names, and the free
first 5 xp in a Supernatural Ability a Virtue grants. Every Ability also
keeps under the creation cap for the character's age.

Rules: reference/rules-engine-reference.md §3 Later life experience;
Creation Ability cap by age; Ability types and who may learn them.
"""

from __future__ import annotations

from .. import catalog
from ..models import Character, Saga
from . import creation_access as access
from . import creation_packages as packages
from .creation_base import CHARACTER_CHECKS, Check, Record, check
from .creation_character import age
from .creation_virtues import held_option
from .creation_xp import entries, spent

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Later Life "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Three:"
    "_Characters#Later_Life)"
)

CHILDHOOD_ENDS = 5
#: When a magus's apprenticeship starts if the sheet doesn't say.
DEFAULT_APPRENTICESHIP_AGE = 10
XP_A_YEAR = 15
WEALTHY_XP, POOR_XP = 20, 10
#: The free xp in a Supernatural Ability its Virtue grants (score 1).
FREE_SUPERNATURAL_XP = 5


def xp_a_year(character: Character) -> int:
    ids = {vf.vf_id for vf in character.virtues_flaws}
    if "vf_wealthy" in ids:
        return WEALTHY_XP
    if "vf_poor" in ids:
        return POOR_XP
    return XP_A_YEAR


def later_life_ends(saga: Saga, character: Character) -> int | None:
    """The age Later Life runs to: the character's age, or a magus's start
    of apprenticeship."""
    if character.type == "magus":
        start = character.hermetic.age_of_apprenticeship
        return start if start is not None else DEFAULT_APPRENTICESHIP_AGE
    return age(saga, character)


def later_life_years(saga: Saga, character: Character) -> int:
    ends = later_life_ends(saga, character)
    return max(0, ends - CHILDHOOD_ENDS) if ends is not None else 0


def bought_years(saga: Saga, character: Character) -> int:
    """The Later Life years bought at the xp a year: those the training
    packages don't take."""
    return max(0, later_life_years(saga, character) - packages.years_used(character))


def later_life_budget(saga: Saga, character: Character) -> int:
    return bought_years(saga, character) * xp_a_year(character)


def later_life_targets(character: Character) -> list[str]:
    return access.learnable_abilities(character, apprenticed=False)


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
    # Names from a family ("Dead Language: Latin") the Virtue names itself.
    return sorted(found | set(rule.names))


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


def _check(label: str, ok: bool, detail: str, source: str = SOURCE, *, advice=False):
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
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    for vf_id, rule in access.virtue_xp(character).items():
        name = by_id[vf_id].name
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
    years = age(saga, character)
    cap = access.ability_cap(years)
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
    found.append(
        _check(
            label,
            not over,
            ", ".join(over) or "none above",
            access.CAP_SOURCE,
        )
    )
    return found
