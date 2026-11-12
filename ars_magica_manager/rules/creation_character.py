"""Character creation checks, step by step. Each
function is registered for its worksheet step in rules.creation.

Rules: Creation order; Virtues and Flaws; Starting age and pre-play aging.
"""

from __future__ import annotations

from .. import catalog
from ..models import Character, Saga, character_age
from . import aging, animal_aging, animal_grogs
from .creation_base import CHARACTER_CHECKS, Check, Record, check

DE_CH3 = "Ars Magica Definitive Edition, Chapter Three: Characters, pp. 25-58"
SOURCE = DE_CH3
MYTHIC_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Mythic Companions, p. 55"
)
AGE_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Starting Character Age, "
    "p. 43"
)

THE_GIFT = "vf_the_gift"
HERMETIC_MAGUS = "vf_hermetic_magus"
#: What choosing the type adds: the Virtues every magus takes.
MAGUS_VIRTUES: tuple[str, ...] = (THE_GIFT, HERMETIC_MAGUS)
#: Virtues that stand for Hermetic Magus: the Rhine Tribunal's ranks
#: (Guardians of the Forests p. 20).
STANDS_FOR: dict[str, tuple[str, ...]] = {
    HERMETIC_MAGUS: (
        "vf_journeyman_rhine_tribunal",
        "vf_master_rhine_tribunal",
        "vf_archmage_rhine_tribunal",
    ),
}

#: The DE sample Mythic Companions' packages: (Virtue/Flaw ids, one of which
#: is needed, label) per status Virtue. Substitutes are allowed by the book,
#: so a missing one is advice, not a must.
MYTHIC_PACKAGES: dict[str, tuple[tuple[tuple[str, ...], str], ...]] = {
    "vf_devil_child": (
        (("vf_demonic_blood",), "Demonic Blood"),
        (("vf_demonic_might", "vf_demonic_powers"), "Demonic Might or Demonic Powers"),
        (("vf_puissant_ability",), "Puissant Guile"),
        (("vf_tragic_life",), "Tragic Life (or an agreed substitute)"),
    ),
    "vf_faerie_doctor": (
        (("vf_dowsing",), "Dowsing"),
        (("vf_wise_one",), "Wise One"),
        (("vf_curse_throwing",), "Curse-Throwing"),
        (("vf_faerie_friend",), "Faerie Friend (or a substitute)"),
        (("vf_dutybound",), "Dutybound (or a substitute)"),
    ),
    "vf_nephilim": (
        (("vf_blood_of_the_nephilim",), "Blood of the Nephilim"),
        (("vf_greater_immunity",), "Greater Immunity: Disease"),
        (("vf_great_characteristic",), "Great Stamina and Great Strength"),
        (("vf_improved_characteristics",), "Improved Characteristics"),
        (("vf_sense_holiness_and_unholiness",), "Sense Holiness and Unholiness"),
        (("vf_strong_angelic_heritage",), "Strong Angelic Heritage"),
    ),
    "vf_spirit_votary": (
        (("vf_second_sight",), "Second Sight"),
        (("vf_spiritual_pact",), "Spiritual Pact"),
        (("vf_pagan", "vf_pagan_major"), "Pagan (or a substitute)"),
    ),
}

#: Pre-play aging starts here, and companions should be younger than
#: COMPANION_AGE.
AGING_AGE = 35
COMPANION_AGE = 30


def _ids(character: Character) -> list[str]:
    return [vf.vf_id for vf in character.virtues_flaws]


def mythic_status_ids() -> set[str]:
    """The Free Virtues that make a character a Mythic Companion."""
    return {
        entry.id
        for entry in catalog.load_virtue_flaw_catalog()
        if entry.tier == "Free" and "mythic companion" in entry.audience
    }


def house_name(house_id: str) -> str:
    house = catalog.load_house_catalog_by_id().get(house_id)
    return house.name if house is not None else house_id


#: Childhood's end, when Later Life starts.
CHILDHOOD_ENDS = 5
#: When a magus's apprenticeship starts if the sheet doesn't say.
DEFAULT_APPRENTICESHIP_AGE = 10


def age(saga: Saga, character: Character) -> int | None:
    return character_age(character.background.year_born, saga.current_year)


def later_life_ends(saga: Saga, character: Character) -> int | None:
    """The age Later Life runs to: the character's age, or a magus's start
    of apprenticeship."""
    if character.type == "magus":
        start = character.hermetic.age_of_apprenticeship
        return start if start is not None else DEFAULT_APPRENTICESHIP_AGE
    return age(saga, character)


def later_life_starts(character: Character) -> int:
    """The age Later Life starts at: 5, or the age an animal's kind is
    grown."""
    grown = animal_grogs.grown(character)
    return CHILDHOOD_ENDS if grown is None else grown


def later_life_years(saga: Saga, character: Character) -> int:
    ends = later_life_ends(saga, character)
    start = later_life_starts(character)
    return max(0, ends - start) if ends is not None else 0


def pre_play_aging_rolls(saga: Saga, character: Character) -> int:
    """How many aging rolls the character makes before play: one for each
    year from 35 (50 with Strong Faerie Blood) up to their starting age."""
    years = age(saga, character)
    if years is None:
        return 0
    if animal_aging.figures(character) is not None:
        # An animal's kind rolls several a year, or one every few years.
        return animal_aging.rolls_between(character, aging_age(character), years)
    return max(0, years - aging_age(character))


def aging_age(character: Character) -> int:
    """The age the character's aging rolls start at."""
    return aging.start_age(character)


@check("concept", CHARACTER_CHECKS)
def concept_checks(saga: Saga, record: Record) -> list[Check]:
    assert isinstance(record, Character)
    character = record
    found: list[Check] = []
    ids = _ids(character)
    years = age(saga, character)
    found.append(
        Check(
            "concept",
            "Age is set",
            "pass" if years is not None else "warn",
            f"{years}" if years is not None else "set Year Born",
            DE_CH3,
        )
    )
    if character.type == "magus":
        by_id = catalog.load_virtue_flaw_catalog_by_id()
        for vf_id in MAGUS_VIRTUES:
            name = by_id[vf_id].name if vf_id in by_id else vf_id
            found.append(
                Check(
                    "concept",
                    f"A magus has {name}",
                    "pass" if vf_id in ids else "warn",
                    "taken" if vf_id in ids else "missing",
                    DE_CH3,
                )
            )
        house = character.hermetic.house
        found.append(
            Check(
                "concept",
                "A magus belongs to a House",
                "pass" if house else "warn",
                house_name(house) if house else "none chosen",
                DE_CH3,
            )
        )
    if character.type == "mythic companion":
        statuses = [i for i in ids if i in mythic_status_ids()]
        found.append(
            Check(
                "concept",
                "One Mythic Companion status Virtue",
                "pass" if len(statuses) == 1 else "warn",
                f"{len(statuses)} taken",
                MYTHIC_SOURCE,
            )
        )
        if THE_GIFT in ids:
            found.append(
                Check(
                    "concept",
                    "A Mythic Companion has no Gift",
                    "warn",
                    "The Gift taken",
                    MYTHIC_SOURCE,
                )
            )
        for status in statuses[:1]:
            for choices, label in MYTHIC_PACKAGES.get(status, ()):
                has = any(choice in ids for choice in choices)
                found.append(
                    Check(
                        "concept",
                        f"The package includes {label}",
                        "pass" if has else "advice",
                        "taken" if has else "missing",
                        MYTHIC_SOURCE,
                    )
                )
    companion = character.type in ("companion", "mythic companion")
    if companion and years is not None and years >= COMPANION_AGE:
        found.append(
            Check(
                "concept",
                f"A companion should be under {COMPANION_AGE}",
                "advice",
                f"{years - COMPANION_AGE + 1} year(s) too old",
                AGE_SOURCE,
            )
        )
    rolls = pre_play_aging_rolls(saga, character)
    if rolls:
        found.append(
            Check(
                "concept",
                f"Older than {aging_age(character)}: aging rolls before play",
                "pass",
                f"{rolls} roll(s)",
                AGE_SOURCE,
            )
        )
    return found


def missing_type_virtues(character: Character) -> list[str]:
    """The Virtues the character's type requires that it hasn't taken yet
    (a magus: The Gift and Hermetic Magus)."""
    if character.type != "magus":
        return []
    ids = _ids(character)
    return [
        vf_id
        for vf_id in MAGUS_VIRTUES
        if vf_id not in ids and not set(ids) & set(STANDS_FOR.get(vf_id, ()))
    ]
