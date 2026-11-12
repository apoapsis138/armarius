"""Which Abilities a character may buy at creation:
General ones always; Academic, Arcane and Martial ones only with a Virtue
that opens them (or, for a magus, from apprenticeship on); a Supernatural
one only with the Virtue that grants it (a Gifted non-magus may take one
without). Also the Virtues whose own xp is spent at creation, and the
creation Ability cap by age.

Rules: Ability types and who may learn them; Later life experience; Creation Ability cap by age.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from .. import catalog
from ..arts import ARTS
from ..models import (
    SUPERNATURAL_CATEGORIES,
    AbilityDef,
    Character,
    TraditionDef,
    VirtueFlawInstance,
)
from . import animal_grogs, grog_aging, schools, xp
from .creation_character import THE_GIFT
from .rounding import round_up

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Five: Abilities, Ability Types, pp. 158-159"
)
CAP_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Abilities, p. 48"
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
#: A Virtue giving a Supernatural Ability that may need to penetrate Magic
#: Resistance lets the character take Penetration too (DE p. 158).
PENETRATION = "Penetration"
#: Virtues opening one named Arcane Ability only.
OPENS_ABILITY: dict[str, tuple[str, ...]] = {
    "vf_diabolic_past": ("Infernal Lore",),
    "vf_familiarity_with_the_fae": ("Faerie Lore",),
    "vf_faerie_blood": ("Faerie Lore",),
    "vf_strong_faerie_blood": ("Faerie Lore",),
    # Warped by Magic's encounters open Magic Lore (DE p. 151).
    "vf_warped_by_magic": ("Magic Lore",),
    "vf_senior_bard": ("Dominion Lore", "Faerie Lore", "Infernal Lore", "Magic Lore"),
    # DE pp. 93, 96, 128, 133, 136, 138, 140.
    "vf_faerie_upbringing": ("Faerie Lore",),
    "vf_faerie_friend": ("Faerie Lore",),
    "vf_imagined_folk_tradition_vulnerability": ("Faerie Lore",),
    "vf_magical_blood": ("Magic Lore",),
    "vf_monstrous_blood": ("Magic Lore",),
    "vf_master_of_form_creatures": ("Magic Lore",),
    "vf_magical_fascination": ("Magic Lore", "Faerie Lore"),
    "vf_outsider": ("Magic Lore", "Faerie Lore"),
    # Land of Fire & Ice p. 54.
    "vf_galdor_conjuring": ("Galdor Wisdom",),
    "vf_galdor_enchantment": ("Galdor Wisdom",),
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
    #: Whether it may buy the Arts too (one xp an xp).
    arts: bool = False
    #: The Virtue a second pool of its xp belongs to, when the pool's key
    #: isn't the Virtue's id; and the pool's name after the Virtue's.
    virtue: str = ""
    label: str = ""


_SOCIAL = ("Charm", "Etiquette", "Folk Ken", "Guile", "Intrigue", "Leadership")
_AREA, _LANGUAGE, _ORG = "Area Lore: ", "Living Language: ", "Organization Lore: "
_BARDIC = (
    "Art of Memory",
    "Profession: Storyteller",
    "Profession: Poet",
    "Faerie Lore",
    "Magic Lore",
)

#: (Gild) Trained's second pool of xp, on the gild's own learning.
GILD_POOL = "vf_gild_trained:gild"

#: The Virtues that give xp at creation (their catalog summaries), by
#: the pool's key: the Virtue's id, or another for a Virtue's second
#: pool (VirtueXp.virtue).
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
    "vf_educated_hebrew": VirtueXp(
        50,
        names=(
            "Dead Language: Hebrew",
            "Living Language: Hebrew",
            "Dead Language: Aramaic",
            "Living Language: Aramaic",
            "Theology: Judaism",
            "Judaic Lore",
        ),
    ),
    "vf_educated_islamic": VirtueXp(
        50,
        names=(
            "Living Language: Arabic",
            "Living Language: Persian",
            "Living Language: Greek",
            "Dead Language: Greek",
            "Dead Language: Latin",
            "Theology: Islam",
            "Islamic Law",
            "Artes Liberales",
        ),
    ),
    "vf_rosh_beth_din": VirtueXp(
        50, types=(ACADEMIC,), names=("Rabbinic Law", "Theology: Judaism")
    ),
    "vf_master_bard": VirtueXp(240, names=_BARDIC, prefixes=(_AREA, _ORG)),
    "vf_senior_bard": VirtueXp(90, names=_BARDIC, prefixes=(_AREA, _ORG)),
    "vf_clan_ilfetu": VirtueXp(
        50,
        names=(
            "Bjornaer Lore",
            "House Bjornaer Lore",
            "Magic Lore",
            "Dead Language: Gothic",
        ),
    ),
    "vf_ineslemen": VirtueXp(
        50,
        names=(
            "Theology: Islam",
            "Islamic Law",
            "Dominion Lore",
            "Faerie Lore",
            "Infernal Lore",
            "Magic Lore",
        ),
    ),
    "vf_forge_companion": VirtueXp(50, prefixes=("Craft: ",)),
    "vf_herbalism": VirtueXp(50, names=("Herbalism", "Profession: Apothecary")),
    # Guardians of the Forests p. 20: 30 xp on Order of Hermes Lore,
    # Intrigue and Durenmar Lore, and 60 more on General or Arcane
    # Abilities, Arts and spells suited to the gild. Spell levels aren't
    # bought with pooled xp here, so the 60 go on Abilities and Arts.
    "vf_gild_trained": VirtueXp(
        30,
        names=(
            "Organization Lore: Order of Hermes",
            "Intrigue",
            "Durenmar Lore",
            "Organization Lore: Durenmar",
        ),
    ),
    GILD_POOL: VirtueXp(
        60,
        types=("General", ARCANE),
        arts=True,
        virtue="vf_gild_trained",
        label="the gild's Abilities and Arts",
    ),
    "vf_improved_abilities": VirtueXp(50),
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


def ability_xp_table(name: str) -> str:
    """The xp table an Ability advances on (models.XP_TABLES): its catalog
    entry's, so an Accelerated Ability or a hedge Art on the Art table
    says "art"; the Ability table for one the catalog doesn't have."""
    entry = ability_def(name)
    return entry.xp_table if entry is not None else "ability"


def ability_factor(name: str) -> int:
    """xp per score step for an Ability of this name (see ability_xp_table)."""
    return xp.ART_FACTOR if ability_xp_table(name) == "art" else xp.ABILITY_FACTOR


def _ids(character: Character) -> list[str]:
    return [vf.vf_id for vf in character.virtues_flaws]


def traditions_of(character: Character) -> list[TraditionDef]:
    """The catalog traditions the character belongs to, in their order."""
    by_id = catalog.load_tradition_catalog_by_id()
    return [by_id[t] for t in character.traditions if t in by_id]


def apprenticeship_years(character: Character, ends: int) -> int:
    """The years of a tradition's apprenticeship that fall inside Later
    Life, which runs to age `ends`: a folk witch adopted at ten and
    trained ten years spends 10 to 20 there, not earning Later Life xp
    (Hedge Magic RE p. 34)."""
    if character.type == "magus":
        return 0
    found = traditions_of(character)
    if not found or not found[0].training.years:
        return 0
    training = found[0].training
    return max(0, min(ends, training.starts + training.years) - max(5, training.starts))


def tradition_opened(character: Character) -> set[str]:
    """The Arts and Abilities a Gifted member's Opening lets them buy:
    their tradition's, even the Supernatural ones with no Virtue."""
    if THE_GIFT not in _ids(character):
        return set()
    return {name for t in traditions_of(character) for name in t.training.opening}


def opened_types(character: Character, *, apprenticed: bool = False) -> set[str]:
    """The restricted Ability types the character may buy: those its
    Virtues open, and every one for a magus from apprenticeship on."""
    types: set[str] = {"General"}
    for vf_id in _ids(character):
        types.update(OPENS.get(vf_id, ()))
    if character.type == "magus" and apprenticed:
        types.update(RESTRICTED)
    return types


#: The Song Talents, which either galdor Virtue opens (rules.galdor.SONGS).
SONG_TALENTS: tuple[str, ...] = (
    "Yfel-galdor",
    "Mal-galdor",
    "Hug-galdor",
    "Sig-galdor",
    "Lim-galdor",
    "Biarg-galdor",
    "Orlog-galdor",
    "Svart-galdor",
    "Ol-galdor",
    "Brun-galdor",
)
#: Virtues granting a Supernatural Ability of another name: Divination &
#: Augury and Hermetic Dream Interpreter give Divination (The Mysteries
#: Revised Edition pp. 59, 62).
GRANTS_SUPERNATURAL: dict[str, tuple[str, ...]] = {
    "vf_divination_and_augury": ("Divination",),
    "vf_hermetic_dream_interpreter": ("Divination",),
    # Partial training in galdor, for one outside it (Land of Fire & Ice p. 59).
    "vf_galdor_conjuring": SONG_TALENTS,
    "vf_galdor_enchantment": SONG_TALENTS,
}


def granted_supernatural(character: Character) -> set[str]:
    """The Supernatural Abilities the character's Virtues grant: a Virtue
    named for the Ability (Second Sight grants Second Sight), or one
    GRANTS_SUPERNATURAL names."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    ids = _ids(character)
    names = {by_id[vf_id].name for vf_id in ids if vf_id in by_id}
    names |= {name for vf_id in ids for name in GRANTS_SUPERNATURAL.get(vf_id, ())}
    return {
        entry.name
        for entry in catalog.load_ability_catalog()
        if entry.category in SUPERNATURAL_CATEGORIES and entry.name in names
    }


def restricted_choices(character: Character, entries: Iterable[str]) -> list[str]:
    """The Abilities xp went on that count against Restricted Learning's
    five: all but the animal's own Language and a Virtue's Supernatural
    Ability (`entries`: the creation xp targets)."""
    granted = granted_supernatural(character)
    found: list[str] = []
    for name in entries:
        if (
            animal_grogs.own_language(character, name)
            or name in granted
            or name in found
        ):
            continue
        found.append(name)
    return found


def may_learn(character: Character, name: str, *, apprenticed: bool = False) -> bool:
    """Whether the character may buy Ability `name` at creation (a magus
    before or during apprenticeship: `apprenticed`)."""
    category = ability_category(name)
    if category in SUPERNATURAL_CATEGORIES:
        return name in granted_supernatural(character) | tradition_opened(character)
    if name in SHELTERED_ABILITIES and SHELTERED in _ids(character):
        return False
    if name in opened_by_virtues(character):
        return True
    # Penetration goes with a supernatural power: one a Virtue grants, or
    # one a tradition's Opening gives (Hedge Magic RE p. 34 recommends it
    # to a folk witch).
    if name == PENETRATION and (
        granted_supernatural(character) or tradition_opened(character)
    ):
        return True
    return category in opened_types(character, apprenticed=apprenticed)


#: Sheltered Upbringing: none of these at creation, though they may be
#: learned in play (DE p. 144).
SHELTERED = "vf_sheltered_upbringing"
SHELTERED_ABILITIES = frozenset(
    {"Bargain", "Charm", "Etiquette", "Folk Ken", "Guile", "Intrigue", "Leadership"}
)
STUDENT_OF_REALM = "vf_student_of_realm"
REALM_LORES = {
    "Divine": "Dominion Lore",
    "Dominion": "Dominion Lore",
    "Faerie": "Faerie Lore",
    "Infernal": "Infernal Lore",
    "Magic": "Magic Lore",
}


def opened_by_virtues(character: Character) -> set[str]:
    """The Arcane Abilities the character's Virtues and Flaws open by name;
    Student of (Realm) opens only the Lore of the realm it names (DE p.
    110)."""
    named = {n for vf in _ids(character) for n in OPENS_ABILITY.get(vf, ())}
    for vf in character.virtues_flaws:
        if vf.vf_id == STUDENT_OF_REALM:
            realm = str(vf.params.get("realm") or "").strip().title()
            lore = REALM_LORES.get(realm)
            named |= {lore} if lore else set(REALM_LORES.values())
    return named


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
    granted = granted_supernatural(character) | tradition_opened(character)
    named = opened_by_virtues(character)
    gifted = gifted_non_magus(character)
    names = set()
    for entry in catalog.load_ability_catalog():
        if entry.category in SUPERNATURAL_CATEGORIES:
            ok = entry.name in granted or gifted
        else:
            ok = entry.name in named or entry.category in types
            ok = ok or (entry.name == PENETRATION and bool(granted))
        if ok:
            names.add(entry.name)
    names.update(
        a.name
        for a in character.abilities
        if may_learn(character, a.name, apprenticed=apprenticed)
    )
    return sorted(names)


def virtue_xp_allows(rule: VirtueXp, name: str) -> bool:
    if name in ARTS:
        return rule.arts
    if not (rule.types or rule.names or rule.prefixes):
        return True
    return (
        ability_category(name) in rule.types
        or name in rule.names
        or name.startswith(rule.prefixes)
    )


def virtue_xp(character: Character) -> dict[str, VirtueXp]:
    """The pools of xp the character's Virtues give at creation, by key."""
    held = set(_ids(character))
    return {
        key: rule for key, rule in VIRTUE_XP.items() if (rule.virtue or key) in held
    }


def pool_name(key: str) -> str:
    """A pool's name: its Virtue's, and what a second pool is for."""
    rule = VIRTUE_XP[key]
    entry = catalog.load_virtue_flaw_catalog_by_id().get(rule.virtue or key)
    name = entry.name if entry is not None else key
    return f"{name}: {rule.label}" if rule.label else name


def xp_multiplier(character: Character, target: str) -> float:
    """1.5 with an Affinity with this Art or Ability, else 1."""
    return affinity_multiplier(character.virtues_flaws, target)


def affinity_multiplier(
    virtues_flaws: Sequence[VirtueFlawInstance], target: str
) -> float:
    """1.5 if `virtues_flaws` hold an Affinity with this Art or Ability,
    else 1 (for a Familiar as much as a Character)."""
    wanted = target.lower()
    for vf in virtues_flaws:
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


def xp_giving(gain: int, multiplier: float) -> int:
    """The least xp that gives at least `gain` once `multiplier` (an
    Affinity's 1.5, rounded up) is applied: 13 needs 9, but 14 also
    needs only 9 (9 x 1.5 = 13.5, rounded up to 14)."""
    if gain <= 0:
        return 0
    xp = max(0, int((gain - 1) // multiplier))
    while round_up(xp * multiplier) < gain:
        xp += 1
    return xp


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


def character_ability_cap(character: Character, age: int | None) -> int:
    """The age cap for this character: the Grogs Aging Chart's harsh aging
    may raise it by 1, its mild aging lower it by 1."""
    return ability_cap(age) + grog_aging.cap_change(character)


#: How far Affinity with Ability lets its Ability go over the age cap.
AFFINITY_CAP_BONUS = 2
#: Lifts the age cap on every Ability.
NO_CAP_VIRTUE = "vf_mentored_by_demons"


def art_cap(character: Character, ability: str) -> int | None:
    """The highest score a tradition's Art on the Art table may have at
    creation (a vitki's runes: 10), None when its tradition sets none."""
    caps = [
        t.training.art_cap
        for t in traditions_of(character)
        if t.training.art_cap and ability in t.abilities
    ]
    return min(caps) if caps else None


def ability_cap_for(character: Character, age: int | None, ability: str) -> int | None:
    """The highest score `ability` may have at creation: the age cap, two
    more with an Affinity with it, None (no cap) when Mentored by Demons;
    no higher than the school named on Educated teaches it (schools.cap).
    An Ability on the Art table has no age cap, only its tradition's
    (art_cap). Puissant adds when the Ability is used, so it never
    counts."""
    if ability and ability_xp_table(ability) == "art":
        return art_cap(character, ability)
    if any(vf.vf_id == NO_CAP_VIRTUE for vf in character.virtues_flaws):
        return None
    cap = character_ability_cap(character, age)
    if affinity_multiplier(character.virtues_flaws, ability) > 1:
        cap += AFFINITY_CAP_BONUS
    if ability and FOREIGN in _ids(character) and local_ability(ability):
        cap = round_up(cap / 2)
    favoured = savant_ability(character)
    if favoured is not None:
        cap = min(cap, SAVANT_FAVOURED_CAP if ability == favoured else SAVANT_CAP)
    taught = schools.cap(character, ability)
    if taught is not None:
        cap = min(cap, taught)
    return cap


#: Foreign Upbringing halves (rounding up) the creation caps of Abilities
#: that depend on the locality: Language, Area Lore, Organization Lore and
#: the social ones (DE p. 131).
FOREIGN = "vf_foreign_upbringing"
_LOCAL_PREFIXES = ("Living Language: ", "Area Lore: ", "Organization Lore: ")
_LOCAL_SOCIAL = frozenset(
    {"Charm", "Etiquette", "Folk Ken", "Guile", "Intrigue", "Leadership"}
)


def local_ability(name: str) -> bool:
    return name.startswith(_LOCAL_PREFIXES) or name in _LOCAL_SOCIAL


#: Savantism: no Ability above 3 at creation but the favoured one, up to 6
#: (DE p. 143).
SAVANTISM = "vf_savantism"
SAVANT_CAP, SAVANT_FAVOURED_CAP = 3, 6


def savant_ability(character: Character) -> str | None:
    """A savant's favoured Ability ("" if not yet named), None for anyone
    else."""
    for vf in character.virtues_flaws:
        if vf.vf_id == SAVANTISM:
            return str(vf.params.get("ability") or "")
    return None
