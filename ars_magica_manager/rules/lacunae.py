"""Lacunae and urban ceremonial magic: the holes in a city's Dominion where
a magus casts unhindered, how he finds them, and how a ceremony's
prepared space speeds his casting.

- A lacuna (HoH:S p. 57) is a small patch of another aura, or of none,
  inside a city's Dominion. Cast from it, a spell meets the lacuna's aura
  instead of the Dominion's, provided its target is not itself within the
  Dominion. Most have no aura at all; some are Magic, Faerie or Infernal.
- Searching (HoH:S p. 57): a season, then Intelligence + Area Lore against
  9. The first success finds all the obvious lacunae; seasons searching
  after it are Area Lore practice, and the Area Lore's specialty may become
  lacunae. A character raised in the area by a magus knows them already.
- A character who knows the city's lacunae knows three small ones per
  level of Area Lore, named by the player with the troupe. A lacuna that
  gives more than a place to cast, not bought at covenant or character
  creation and not a story's reward, also carries a limitation.
- Ceremonial casting's prepared spaces (DE p. 218; HoH:S pp. 59-60): 15
  minutes a magnitude without one, 12 a temporary one, 9 a natural one, 6
  a designed one, 3 the laboratory, 1 a room built for it; Mystical
  Choreography makes it 5, or 1 with any prepared space (DE p. 99, which
  the HoH:S errata for p. 56 agrees with). The spell's magnitude is capped
  by the quarter-hours spent at 15 minutes (DE p. 218); with a faster space
  the time spent sets the cap the same way, a magnitude per its minutes.
- Most cities have a Dominion of 3 (HoH:S p. 58): -9 to a Hermetic
  Casting Score.

Pattern: functions over the character and the casting's choices; the
season's search is the activity registry's Strategy (season_work.societates)
and a found city a Progress record (kind "lacunae").
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Character, Progress
from . import casting_virtues, hunting, realms

SOURCE = "Houses of Hermes: Societates, Urban Magic, Lacunae, p. 57"
CEREMONY_SOURCE = (
    "Ars Magica Definitive Edition, Ceremonial Casting, p. 218 (Houses of "
    "Hermes: Societates pp. 58-60); Mystical Choreography, p. 99"
)

#: The Progress record of a city whose obvious lacunae are found.
KIND = "lacunae"
#: Intelligence + Area Lore + a die against this finds them.
SEARCH_EASE = 9
#: Small lacunae known per level of the city's Area Lore.
PER_LORE = 3
#: The Dominion of most cities (HoH:S p. 58).
CITY_DOMINION = 3
DOMINION = "Divine"
#: A lacuna's realm: none (the commonest), Magic, Faerie or Infernal.
NO_AURA = ""
LACUNA_REALMS: tuple[str, ...] = (NO_AURA, "Magic", "Faerie", "Infernal")
#: What may limit a lacuna that gives more than a place to cast (p. 57).
LIMITATIONS: tuple[str, ...] = (
    "unavailable by daylight",
    "inhabitants to placate each time it is used",
    "overuse risks mundane exposure",
    "an Infernal aura",
)
#: Where a lacuna that gives more than a place to cast may come from
#: without needing a limitation (p. 57).
FREE_ORIGINS = ("covenant", "virtue", "story")


def area_of(lore: str) -> str:
    """The area an Area Lore names ("Area Lore: Paris" -> "Paris")."""
    _, sep, area = lore.partition(":")
    return area.strip() if sep and area.strip() else lore.strip()


def record_name(area: str) -> str:
    """The Progress record's name for a city's lacunae."""
    return f"Lacunae of {area}"


def search_lore(character: Character, chosen: str = "") -> tuple[str, int]:
    """The Area Lore the search uses, (name, score): the one chosen if it is
    an Area Lore, else his best ("", 0 with none)."""
    lores = hunting.area_lores(character)
    for name, score in lores:
        if name == chosen:
            return name, score
    return lores[0] if lores else ("", 0)


def search_base(character: Character, lore_score: int) -> int:
    """Intelligence + Area Lore, before the die."""
    return character.characteristics.intelligence + lore_score


def found_record(character: Character, area: str) -> Progress | None:
    """The record of the city's obvious lacunae found, if they are."""
    name = record_name(area)
    return next(
        (p for p in character.progress if p.kind == KIND and p.name == name and p.done),
        None,
    )


def found_areas(character: Character) -> list[str]:
    """The cities whose lacunae he has found, as their records name them."""
    return [p.name for p in character.progress if p.kind == KIND and p.done]


def known_count(lore_score: int) -> int:
    """Small lacunae known in a city: three per level of its Area Lore."""
    return PER_LORE * max(0, lore_score)


def needs_limitation(more_than_casting: bool, origin: str) -> bool:
    """Whether a lacuna needs a limitation: one that gives more than a place
    to cast unless it came with the covenant, a Virtue or a story."""
    return more_than_casting and origin not in FREE_ORIGINS


def casting_aura(
    city_aura: int,
    *,
    in_lacuna: bool,
    lacuna_realm: str = NO_AURA,
    lacuna_aura: int = 0,
    target_in_dominion: bool = False,
) -> tuple[str, int]:
    """The aura a spell cast in the city meets, (realm, rating): the
    lacuna's when cast from one at a target outside the Dominion, else the
    city's Dominion. A lacuna with no aura is a mundane place: no
    modifier."""
    if not in_lacuna or target_in_dominion:
        return DOMINION, max(0, city_aura)
    if lacuna_realm == NO_AURA:
        return realms.HERMETIC, 0
    return lacuna_realm, max(0, lacuna_aura)


@dataclass(frozen=True)
class Space:
    key: str
    label: str
    minutes: int


#: Ceremonial casting's prepared spaces, minutes per magnitude (DE p. 218).
SPACES: tuple[Space, ...] = (
    Space("none", "No prepared space", 15),
    Space("temporary", "A temporary space (chalk circles in a rented room)", 12),
    Space("natural", "A space naturally suited (a cliff ledge at sunrise)", 9),
    Space("designed", "A space carefully designed for it", 6),
    Space("laboratory", "His laboratory", 3),
    Space("ceremonial_room", "A room built only for ceremonial casting", 1),
)
SPACE_BY_KEY = {space.key: space for space in SPACES}
#: Mystical Choreography: five minutes a magnitude, one in any prepared
#: space (DE p. 99).
CHOREOGRAPHY_MINUTES = 5
CHOREOGRAPHY_SPACE_MINUTES = 1


def minutes_per_magnitude(space: str, choreography: bool = False) -> int:
    """How long a ceremony takes a magnitude in this space."""
    found = SPACE_BY_KEY.get(space, SPACES[0])
    if choreography:
        return (
            CHOREOGRAPHY_MINUTES if found.key == "none" else CHOREOGRAPHY_SPACE_MINUTES
        )
    return found.minutes


def has_choreography(character: Character) -> bool:
    return any(
        vf.vf_id == casting_virtues.CHOREOGRAPHY for vf in character.virtues_flaws
    )


def ceremony_minutes(magnitudes: int, space: str, choreography: bool = False) -> int:
    """The minutes a ceremony of this many magnitudes takes."""
    return max(1, magnitudes) * minutes_per_magnitude(space, choreography)
