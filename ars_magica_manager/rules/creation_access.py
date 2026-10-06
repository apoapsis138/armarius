"""Which Abilities a character may buy at creation:
General ones always; Academic, Arcane and Martial ones only with a Virtue
that opens them (or, for a magus, from apprenticeship on); a Supernatural
one only with the Virtue that grants it (a Gifted non-magus may take one
without). Also the Virtues whose own xp is spent at creation, and the
creation Ability cap by age.

Rules: reference/rules-engine-reference.md §3 Ability types and who may
learn them; Later life experience; Creation Ability cap by age.
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import catalog
from ..models import AbilityDef, Character
from .creation_character import THE_GIFT
from .rounding import round_up

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Five: Abilities, Ability Types "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Five:"
    "_Abilities#Ability_Types)"
)
CAP_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Abilities "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Three:"
    "_Characters#Abilities_2)"
)

ACADEMIC, ARCANE, MARTIAL, SUPERNATURAL = (
    "Academic",
    "Arcane",
    "Martial",
    "Supernatural",
)
RESTRICTED = (ACADEMIC, ARCANE, MARTIAL)

#: The Virtues (and a few Flaws) whose text lets a character buy a
#: restricted type of Ability at creation (the catalog's DE entries).
OPENS: dict[str, tuple[str, ...]] = {
    **{
        vf_id: (ACADEMIC,)
        for vf_id in (
            "vf_alim",
            "vf_archieunuch",
            "vf_beadle",
            "vf_brother_chaplain",
            "vf_bureaucrat",
            "vf_cathedral_school_master",
            "vf_clerk",
            "vf_doctor_in_faculty",
            "vf_educated",
            "vf_educated_hebrew",
            "vf_educated_islamic",
            "vf_educated_vernacular",
            "vf_eunuch",
            "vf_failed_monk",
            "vf_guild_dean",
            "vf_guild_master",
            "vf_magister_in_artibus",
            "vf_mazdean_priest",
            "vf_mendicant_friar",
            "vf_notary",
            "vf_perfectus",
            "vf_priest",
            "vf_rabbi",
            "vf_religious",
            "vf_rosh_beth_din",
            "vf_senior_clergy",
            "vf_senior_master",
            "vf_templar_administrator",
            "vf_town_magistrate",
            "vf_troubadour_trobairitz",
            "vf_venditor",
        )
    },
    **{
        vf_id: (MARTIAL,)
        for vf_id in (
            "vf_almogaten",
            "vf_almogavar",
            "vf_berserk",
            "vf_branded_criminal",
            "vf_fidai",
            "vf_knight",
            "vf_lasiq",
            "vf_mamluk",
            "vf_marshal",
            "vf_master_of_kennels",
            "vf_mercenary_captain",
            "vf_outlaw",
            "vf_outlaw_leader",
            "vf_turb_trained",
            "vf_warrior",
        )
    },
    "vf_arcane_lore": (ARCANE,),
    "vf_master_bard": (ARCANE,),
    "vf_brother_knight": (ACADEMIC, MARTIAL),
    "vf_wise_one": (ACADEMIC, ARCANE),
    # "One restricted group" of the player's choosing: any of them.
    "vf_custos": RESTRICTED,
    "vf_templar_specialist": RESTRICTED,
    "vf_failed_apprentice": RESTRICTED,
    "vf_redcap": RESTRICTED,
}
#: Virtues opening one named Arcane Ability only.
OPENS_ABILITY: dict[str, tuple[str, ...]] = {
    "vf_diabolic_past": ("Infernal Lore",),
    "vf_familiarity_with_the_fae": ("Faerie Lore",),
    "vf_student_of_realm": (
        "Dominion Lore",
        "Faerie Lore",
        "Infernal Lore",
        "Magic Lore",
    ),
    "vf_senior_bard": ("Dominion Lore", "Faerie Lore", "Infernal Lore", "Magic Lore"),
}


@dataclass(frozen=True)
class VirtueXp:
    """A Virtue's own xp, spent at creation on what it names."""

    xp: int
    #: Ability types it may buy ("Academic"...), exact Ability names, and
    #: name prefixes ("Craft: "); all empty means any Ability.
    types: tuple[str, ...] = ()
    names: tuple[str, ...] = ()
    prefixes: tuple[str, ...] = ()


_SOCIAL = ("Charm", "Etiquette", "Folk Ken", "Guile", "Intrigue", "Leadership")
_AREA, _LANGUAGE, _ORG = "Area Lore: ", "Living Language: ", "Organization Lore: "

#: The DE Virtues that give xp at creation (their catalog summaries).
VIRTUE_XP: dict[str, VirtueXp] = {
    "vf_educated": VirtueXp(50, names=("Dead Language: Latin", "Artes Liberales")),
    "vf_arcane_lore": VirtueXp(50, types=(ARCANE,)),
    "vf_warrior": VirtueXp(50, types=(MARTIAL,)),
    "vf_privileged_upbringing": VirtueXp(50, types=("General", ACADEMIC, MARTIAL)),
    "vf_trained_assassin": VirtueXp(
        50, types=(MARTIAL,), names=("Athletics", "Guile", "Stealth")
    ),
    "vf_well_traveled": VirtueXp(
        50,
        names=("Bargain", "Carouse", "Charm", "Etiquette", "Folk Ken", "Guile"),
        prefixes=(_AREA, _LANGUAGE),
    ),
    "vf_schooled_in_crime": VirtueXp(
        50,
        names=(
            "Athletics",
            "Awareness",
            "Bargain",
            "Brawl",
            "Charm",
            "Guile",
            "Legerdemain",
            "Stealth",
        ),
        prefixes=(_AREA,),
    ),
    "vf_craft_guild_training": VirtueXp(
        50,
        names=("Bargain", "Organization Lore: Guild"),
        prefixes=("Craft: ", "Profession: "),
    ),
    "vf_hermetic_experience": VirtueXp(
        50,
        names=(
            "Organization Lore: Order of Hermes",
            "Magic Lore",
            "Dead Language: Latin",
        ),
    ),
    "vf_baccalaureus": VirtueXp(90, names=("Dead Language: Latin", "Artes Liberales")),
    "vf_magister_in_artibus": VirtueXp(240, types=(ACADEMIC,), names=("Teaching",)),
    "vf_cathedral_school_master": VirtueXp(240, types=(ACADEMIC,), names=("Teaching",)),
    "vf_doctor_in_faculty": VirtueXp(
        300, types=(ACADEMIC,), names=("Dead Language: Latin",)
    ),
    "vf_physician_of_salerno": VirtueXp(50, names=("Medicine", "Philosophiae")),
    "vf_marshal": VirtueXp(
        50,
        names=("Animal Handling", "Etiquette", "Hunt", "Dead Language: Latin", "Ride"),
        prefixes=("Profession: ",),
    ),
    "vf_master_of_kennels": VirtueXp(
        50,
        names=("Animal Handling", "Etiquette", "Hunt", "Dead Language: Latin", "Ride"),
        prefixes=("Profession: ",),
    ),
    "vf_falconer": VirtueXp(
        50,
        names=("Animal Handling", "Etiquette", "Hunt", "Dead Language: Latin", "Ride"),
        prefixes=(_AREA, "Profession: "),
    ),
    "vf_shadchan": VirtueXp(50, names=_SOCIAL, prefixes=(_AREA,)),
    "vf_venditor": VirtueXp(
        50,
        names=("Bargain", "Charm", "Folk Ken", "Guile", "Intrigue"),
        prefixes=(_LANGUAGE,),
    ),
    "vf_educated_vernacular": VirtueXp(
        50,
        types=(ACADEMIC,),
        names=("Bargain",),
        prefixes=(_ORG, "Profession: ", _LANGUAGE),
    ),
    "vf_educated_bardic": VirtueXp(
        50, names=("Art of Memory",), prefixes=("Profession: ", _AREA, _ORG)
    ),
    "vf_mentored_by_demons": VirtueXp(50),
}


def ability_def(name: str) -> AbilityDef | None:
    """The catalog entry an Ability name comes from: its own, or its
    family's ("Area Lore: Rhine" -> "Area Lore: {region}")."""
    for entry in catalog.load_ability_catalog():
        if not entry.parameters:
            if entry.name == name:
                return entry
        elif name.startswith(entry.name.split("{", 1)[0]):
            return entry
    return None


def ability_category(name: str) -> str:
    entry = ability_def(name)
    return entry.category if entry is not None else "General"


def _ids(character: Character) -> list[str]:
    return [vf.vf_id for vf in character.virtues_flaws]


def opened_types(character: Character, *, apprenticed: bool = False) -> set[str]:
    """The restricted Ability types the character may buy: those its
    Virtues open, and every one for a magus from apprenticeship on."""
    types: set[str] = {"General"}
    for vf_id in _ids(character):
        types.update(OPENS.get(vf_id, ()))
    if character.type == "magus" and apprenticed:
        types.update(RESTRICTED)
    return types


def granted_supernatural(character: Character) -> set[str]:
    """The Supernatural Abilities the character's Virtues grant: a Virtue
    named for the Ability (Second Sight grants Second Sight)."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    names = {by_id[vf_id].name for vf_id in _ids(character) if vf_id in by_id}
    return {
        entry.name
        for entry in catalog.load_ability_catalog()
        if entry.category == SUPERNATURAL and entry.name in names
    }


def may_learn(character: Character, name: str, *, apprenticed: bool = False) -> bool:
    """Whether the character may buy Ability `name` at creation (a magus
    before or during apprenticeship: `apprenticed`)."""
    category = ability_category(name)
    if category == SUPERNATURAL:
        return name in granted_supernatural(character)
    if name in {n for vf in _ids(character) for n in OPENS_ABILITY.get(vf, ())}:
        return True
    return category in opened_types(character, apprenticed=apprenticed)


def gifted_non_magus(character: Character) -> bool:
    """A Gifted non-magus may take one Supernatural Ability without its
    Virtue."""
    return character.type != "magus" and THE_GIFT in _ids(character)


def learnable_abilities(
    character: Character, *, apprenticed: bool = False
) -> list[str]:
    """Catalog Ability names (a family with its blank, "Craft: {craft}")
    and the character's own Abilities that it may buy at this step."""
    types = opened_types(character, apprenticed=apprenticed)
    granted = granted_supernatural(character)
    named = {n for vf in _ids(character) for n in OPENS_ABILITY.get(vf, ())}
    gifted = gifted_non_magus(character)
    names = set()
    for entry in catalog.load_ability_catalog():
        if entry.category == SUPERNATURAL:
            ok = entry.name in granted or gifted
        else:
            ok = entry.name in named or entry.category in types
        if ok:
            names.add(entry.name)
    names.update(
        a.name
        for a in character.abilities
        if may_learn(character, a.name, apprenticed=apprenticed)
    )
    return sorted(names)


def virtue_xp_allows(rule: VirtueXp, name: str) -> bool:
    if not (rule.types or rule.names or rule.prefixes):
        return True
    return (
        ability_category(name) in rule.types
        or name in rule.names
        or name.startswith(rule.prefixes)
    )


def virtue_xp(character: Character) -> dict[str, VirtueXp]:
    """The character's Virtues that give xp at creation."""
    return {vf_id: VIRTUE_XP[vf_id] for vf_id in _ids(character) if vf_id in VIRTUE_XP}


def xp_multiplier(character: Character, target: str) -> float:
    """1.5 with an Affinity with this Art or Ability, else 1."""
    wanted = target.lower()
    for vf in character.virtues_flaws:
        if vf.vf_id == "vf_affinity_with_art" and vf.params.get("art") == wanted:
            return 1.5
        if (
            vf.vf_id == "vf_affinity_with_ability"
            and vf.params.get("ability") == wanted
        ):
            return 1.5
    return 1.0


def effective_xp(character: Character, target: str, xp: int) -> int:
    """The xp that `xp` spent on `target` gives: half again with an
    Affinity, rounded up (the Affinity with Art Virtue says so; the same
    is used for an Ability)."""
    return round_up(xp * xp_multiplier(character, target))


def ability_cap(age: int | None) -> int:
    """The highest Ability score at creation for a character of `age`."""
    if age is None or age < 30:
        return 5
    if age <= 35:
        return 6
    if age <= 40:
        return 7
    if age <= 45:
        return 8
    return 9
