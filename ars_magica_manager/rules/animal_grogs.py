"""Animal grogs: horses, hounds, hawks and any other beast played as a
grog (Grogs, Chapter 7, Horses & Hounds). A grog is an animal when its
sheet has an AnimalForm (Character.animal).

- Kinds: the bestiaries' clawed beasts, hoofed beasts, birds, and fish
  and serpents (vermin are too small). Each takes a penalty to Presence
  and Communication when dealing with humans: Clawed -2/-5, Hoofed
  -4/-5, Bird -1/-2, Fish -5/-6 (the book's table names no serpent: they
  take the fish's). Each ages as rules.animal_aging says.
- Size: the animal form's, normally -3 (cat-sized) to +2 (horse-sized);
  Large and Small Frame move it a step. After the 7 Characteristic
  points are spent, Strength gets twice the Size and Quickness loses it.
- Virtues and Flaws: Restricted Learning is required; No Hands and Mute
  are held free (outside the Flaw limits, buying no Virtues); the Social
  Status is Domestic Animal, Wanderer or Companion Animal; a Major
  Personality Flaw is taken as a Minor one; nothing about human society.
- Creation xp: no Native Language and no Early Childhood: 120 xp of
  pre-adult life up to the age the kind is grown, then 15 a year. The
  kind's own Language (Dog, Horse, Hawk) is 2 and never rises. A human
  Language is learned at Source Quality 4 + Cunning, and a negative
  Cunning reads it down (to no less than 0). Animal Ken can stand for a
  Language, never above the animal's own. No training packages. The
  Ability cap is the human one for the animal's age scaled to a human
  lifespan, and the book makes it the storyguide's choice, so it is
  advice.

Rules: SOURCE.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, replace

from ..models import AnimalForm, Character, Saga, VirtueFlawDef, character_age
from . import animal_aging
from .rounding import round_down

SOURCE = (
    "Grogs, Chapter 7: Grog Templates, Horses & Hounds, pages 133-137 "
    "(https://www.redcap.org/page/Grogs_Chapter_Seven:_Grog_Templates"
    "#Horses_.26_Hounds)"
)
SIZE_SOURCE = (
    "Grogs, Chapter 7: Grog Templates, Horses & Hounds, Characteristics and "
    "Size (https://www.redcap.org/page/Grogs_Chapter_Seven:_Grog_Templates"
    "#Characteristics_and_Size)"
)
LANGUAGE_SOURCE = (
    "Grogs, Chapter 7: Grog Templates, Horses & Hounds, Lack of Language "
    "Abilities (https://www.redcap.org/page/Grogs_Chapter_Seven:_Grog_"
    "Templates#Lack_of_Language_Abilities)"
)


@dataclass(frozen=True)
class Kind:
    """A bestiary kind: its name, and its Presence and Communication when
    dealing with humans."""

    key: str
    name: str
    presence: int
    communication: int


KINDS: dict[str, Kind] = {
    "clawed": Kind("clawed", "Clawed Beast", -2, -5),
    "hoofed": Kind("hoofed", "Hoofed Beast", -4, -5),
    "bird": Kind("bird", "Bird", -1, -2),
    "fish": Kind("fish", "Fish or Serpent", -5, -6),
}

#: The book's guideline for an animal grog's Size.
SIZE_RANGE = (-3, 2)
#: The xp of pre-adult life, and the animal Language's fixed score.
YOUTH_XP = 120
LANGUAGE_SCORE = 2
LANGUAGE_XP = 15
#: The note on the youth step's entry for the animal Language.
LANGUAGE_NOTE = "animal language"
LATER_XP_A_YEAR = 15

RESTRICTED_LEARNING = "vf_restricted_learning"
#: Restricted Learning's five chosen Abilities.
RESTRICTED_ABILITIES = 5
#: Intrinsic to an animal: held free.
FREE_FLAWS: tuple[str, ...] = ("vf_no_hands", "vf_mute")
STATUSES: tuple[str, ...] = (
    "vf_domestic_animal",
    "vf_wanderer",
    "vf_companion_animal",
)
COMPANION_ANIMAL = "vf_companion_animal"
ANIMAL_KEN = "Animal Ken"
#: The book's other suggestions (Pack Leader is Natural Leader's name for
#: an animal).
POOL_VIRTUES: tuple[str, ...] = (
    "vf_berserk",
    "vf_enduring_constitution",
    "vf_ferocity",
    "vf_improved_characteristics",
    "vf_lightning_reflexes",
    "vf_long_winded",
    "vf_natural_leader",
    "vf_perfect_balance",
    "vf_rapid_convalescence",
    "vf_piercing_gaze",
    "vf_reserves_of_strength",
    "vf_self_confident",
    "vf_tough",
    "vf_wilderness_sense",
)
POOL_FLAWS: tuple[str, ...] = (
    "vf_clumsy",
    "vf_fragile_constitution",
    "vf_fear",
    "vf_noncombatant",
    "vf_nocturnal",
    "vf_pack_mentality",
    "vf_poor_eyesight",
    "vf_poor_hearing",
    "vf_poor_living_conditions",
    "vf_reckless",
    "vf_reclusive",
    "vf_weakness",
)
#: Virtues and Flaws about a life among people, which an animal can't
#: have (besides every Social Status but its three, and the Virtues that
#: open Academic, Arcane or Martial Abilities).
HUMAN_SOCIETY: frozenset[str] = frozenset(
    {
        "vf_academic_concentration_subject",
        "vf_aristotelian_training",
        "vf_book_learner",
        "vf_craft_guild_training",
        "vf_educated_bardic",
        "vf_famous",
        "vf_free_expression",
        "vf_good_teacher",
        "vf_gossip",
        "vf_hermetic_experience",
        "vf_knows_people",
        "vf_linguist",
        "vf_magic_items",
        "vf_perfect_eye_for_commodity",
        "vf_physician_of_salerno",
        "vf_prestigious_student",
        "vf_privileged_upbringing",
        "vf_protection",
        "vf_relic",
        "vf_schooled_in_crime",
        "vf_skilled_smuggler",
        "vf_social_contacts",
        "vf_tainted_treasure",
        "vf_templar_prestige",
        "vf_temporal_influence",
        "vf_troupe_upbringing",
        "vf_well_traveled",
        "vf_apostate",
        "vf_blackmail",
        "vf_castratus",
        "vf_curse_of_slander",
        "vf_dhimmi",
        "vf_employed_by_company",
        "vf_failed_student",
        "vf_feral_upbringing",
        "vf_heir",
        "vf_hermetic_patron",
        "vf_independent_craftsman",
        "vf_poor_student",
        "vf_primitive_equipment",
        "vf_primogeniture_lineage",
        "vf_raised_in_the_gutter",
        "vf_regular",
        "vf_stuck_in_your_ways",
    }
)
#: Abilities an animal grog typically has.
TYPICAL_ABILITIES: tuple[str, ...] = (
    "Area Lore",
    "Athletics",
    "Awareness",
    "Brawl",
    "Hunt",
    "Leadership",
    "Music",
    "Stealth",
    "Survival",
    "Swim",
)
_HUMAN_LANGUAGES = ("Living Language: ", "Dead Language: ")


def is_animal(character: Character) -> bool:
    return character.animal is not None


def kind_of(character: Character) -> Kind | None:
    """An animal grog's kind; None for a person (or an unknown kind)."""
    if character.animal is None:
        return None
    return KINDS.get(character.animal.kind)


def kind_options() -> list[tuple[str, str]]:
    return [(kind.name, key) for key, kind in KINDS.items()]


def describe(animal: AnimalForm) -> str:
    """ "Dog, a Clawed Beast"."""
    kind = KINDS.get(animal.kind)
    name = kind.name if kind is not None else animal.kind
    article = "an" if name[:1] in "AEIOU" else "a"
    return f"{animal.species}, {article} {name}" if animal.species else name


def penalties_text(character: Character, *, short: bool = False) -> str:
    """What an animal has with humans: "Presence -2, Communication -5"
    ("Pre -2, Com -5" `short`); "" for a person."""
    kind = kind_of(character)
    if kind is None:
        return ""
    if short:
        return f"Pre {kind.presence:+d}, Com {kind.communication:+d}"
    return f"Presence {kind.presence:+d}, Communication {kind.communication:+d}"


# -- Size --


def size_adjustment(character: Character, key: str, size: int) -> int:
    """What `size` adds to Characteristic `key` after the points are
    spent: twice the Size to Strength, less the Size from Quickness; 0
    for a person."""
    if not is_animal(character):
        return 0
    if key == "strength":
        return 2 * size
    if key == "quickness":
        return -size
    return 0


# -- Virtues and Flaws --


def free_flaw(character: Character, vf_id: str) -> bool:
    """Whether `vf_id` is one of the Flaws an animal holds free."""
    return is_animal(character) and vf_id in FREE_FLAWS


def counted(character: Character, definition: VirtueFlawDef) -> VirtueFlawDef | None:
    """`definition` as an animal's Flaw limits count it: None for one held
    free, a Major Personality Flaw as a Minor one; as it is for a person."""
    if not is_animal(character):
        return definition
    if definition.id in FREE_FLAWS:
        return None
    if (
        definition.side == "Flaw"
        and definition.tier == "Major"
        and "Personality" in (definition.category, *definition.extra_categories)
    ):
        return replace(definition, tier="Minor", cost=-1)
    return definition


def about_society(definition: VirtueFlawDef, opens: Iterable[str] = ()) -> bool:
    """Whether `definition` is about a life among people: a Social Status
    other than an animal's three, one of HUMAN_SOCIETY, or a Virtue that
    opens Academic, Arcane or Martial Abilities (`opens`)."""
    types = (definition.category, *definition.extra_categories)
    if "Social Status" in types:
        return definition.id not in STATUSES
    return definition.id in HUMAN_SOCIETY or definition.id in set(opens)


def refusal(definition: VirtueFlawDef, opens: Iterable[str] = ()) -> str:
    """Why an animal can't take `definition` ("" if it can): human
    society, or a Major other than its free Flaws and the Personality
    Flaws it takes as Minor."""
    if about_society(definition, opens):
        return "not for animals: human society"
    if definition.tier == "Major":
        personality = "Personality" in (
            definition.category,
            *definition.extra_categories,
        )
        if definition.id in FREE_FLAWS or (definition.side == "Flaw" and personality):
            return ""
        return "not for grogs: Major"
    return ""


# -- Languages --


def human_language(name: str) -> bool:
    return name.startswith(_HUMAN_LANGUAGES)


def own_language(character: Character, name: str) -> bool:
    """Whether `name` is an animal's own Language (Dog, Horse)."""
    animal = character.animal
    return animal is not None and bool(animal.language) and name == animal.language


def understood(character: Character, name: str, score: int) -> int:
    """The score an animal understands a human Language at: less a
    negative Cunning, not below 0."""
    cunning = character.characteristics.intelligence
    if not is_animal(character) or not human_language(name) or cunning >= 0:
        return score
    return max(0, score + cunning)


def language_quality(character: Character, name: str) -> int | None:
    """The Source Quality an animal always has for a human Language, 4 +
    Cunning (not below 0); None for anyone or anything else."""
    if not is_animal(character) or not human_language(name):
        return None
    return max(0, 4 + character.characteristics.intelligence)


def language_lines(character: Character) -> list[str]:
    """ "Understands Living Language: French 1 as 0 (Cunning -1)", for
    each human Language a negative Cunning reads down."""
    lines = []
    for ability in character.abilities:
        shown = understood(character, ability.name, ability.level)
        if shown != ability.level:
            lines.append(
                f"Understands {ability.name} {ability.level} as {shown} "
                f"(Cunning {character.characteristics.intelligence:+d})"
            )
    return lines


# -- ages and xp --


def figures(character: Character) -> animal_aging.AgingFigures | None:
    return animal_aging.figures(character)


def grown(character: Character) -> int | None:
    """The age an animal's pre-adult life ends; None for a person."""
    found = figures(character)
    return found.grown if found is not None else None


def years_xp(kind: str, age: int, lifespan: int | None = None) -> int:
    """An animal's starting xp at `age`: 120 to the age its kind is grown,
    then 15 a year."""
    found = animal_aging.kind_figures(kind, lifespan)
    return YOUTH_XP + max(0, age - found.grown) * LATER_XP_A_YEAR


def cap_age(saga: Saga, character: Character) -> int | None:
    """The age the creation Ability cap is read at: a person's own; an
    animal's scaled to a human lifespan (a 4-year-old dog as a man of
    22)."""
    years = character_age(character.background.year_born, saga.current_year)
    found = figures(character)
    if years is None or found is None:
        return years
    return round_down(years * animal_aging.HUMAN.lifespan / found.lifespan)


def restricted_choices(character: Character, entries: Iterable[str]) -> list[str]:
    """The Abilities xp went on that count against Restricted Learning's
    five: all but the animal's own Language and a Virtue's Supernatural
    Ability (`entries`: the creation xp targets)."""
    from .creation_access import granted_supernatural

    granted = granted_supernatural(character)
    found: list[str] = []
    for name in entries:
        if own_language(character, name) or name in granted or name in found:
            continue
        found.append(name)
    return found
