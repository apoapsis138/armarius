"""A Muslim's baraka from the holy forbears, and the Hajj, as plain rules
(Realms of Power: The Divine pp. 103-108).

- Baraka (pp. 103-104): a Muslim asks a holy forbear's blessing as a
  Christian invokes a saint: Communication + Charm + modifiers + a simple
  die against 15 + the storyguide's simple die (p. 87). He must be at a
  shrine of the forbear, usually his tomb (Muhammad at several places in
  and around Mecca and Medina); the Qur'an itself may be invoked anywhere.
  Muslims never threaten their forbears. The modifiers (p. 103): his
  highest Muslim Personality Trait (+ its value), a Divine aura (+1 a
  level; raised by 1 during the ritual prayer and on Muslim holidays and
  in Ramadan, pp. 107-108), the forbear's feast day, normally his
  birthday (+3), a pilgrimage made to his tomb or shrine (+2), touching
  his relic (+1), owning it (+2), a donation (+1 to +3), imminent peril
  (+2); a recent sinful act (-1 to -3), no zakat paid within a year (-3),
  a miracle received within a month (-5), an unfamiliar forbear (-10),
  and asking a specific miracle of his rather than general aid (-5).
  The book doesn't say which traits are "Muslim" ones: the player
  chooses the trait, Pious offered first, which is the app's reading.
- The forbears (pp. 104-105), with their Divine Might, where baraka may
  be sought and their powers: the Qur'an (Khawass al-Qur'an), Muhammad,
  Abraham, David, al-Husayn, Rabi'a al-'Adawiyya, al-Shafi'i and Nur
  al-Din. David is a greater saint (Might 75) whose powers the book
  doesn't list. Their powers are RoP: The Divine's saints' (pp. 88-89;
  its "Ignem Domini" is the power p. 89 calls Ignis Domini).
- The Hajj (p. 108): a Muslim who completes it gains Pious +3 and 3 Faith
  Points; made again, it restores both, but never raises Pious above +3.

The errata change nothing on these pages (Errata pp. 48-49)."""

from __future__ import annotations

import random
from dataclasses import dataclass

from ..models import Character, ScoredTrait
from . import devotion as dv
from .scores import ability_level
from .theban_customs import Invocation, pious

SOURCE = "Realms of Power: The Divine pp. 103-105, 108"
BOOK = "RoP:D"

#: The forbear invoked anywhere (p. 104).
QURAN = "quran"


@dataclass(frozen=True)
class Forbear:
    """A holy forbear as the book gives him: his Divine Might, where his
    baraka may be sought, his powers (rules.saints.POWERS keys) and the
    page."""

    name: str
    might: int
    places: str
    powers: tuple[str, ...]
    page: int
    anywhere: bool = False


FORBEARS: dict[str, Forbear] = {
    QURAN: Forbear(
        "Khawass al-Qur'an (the Qur'an)",
        100,
        "Anywhere",
        (
            "acknowledgment_of_evil",
            "expel_demons",
            "resist_temptation",
            "grant_of_serenity",
            "the_incombustible_shroud",
            "straighten_the_crippled",
            "the_faithful_made_whole",
            "celestial_immunity",
        ),
        104,
        anywhere=True,
    ),
    "muhammad": Forbear(
        "Muhammad",
        100,
        "Various sites in and around Mecca and Medina, and the Dome of the "
        "Rock in Jerusalem",
        (
            "apparition",
            "acknowledgment_of_evil",
            "expel_demons",
            "resist_temptation",
            "grant_of_serenity",
            "cure_blindness",
            "tomorrows_bounty",
            "the_incombustible_shroud",
            "straighten_the_crippled",
            "the_dutiful_shepherd",
            "sanctuary_of_virginity",
            "the_faithful_made_whole",
            "celestial_immunity",
            "the_leap_of_the_faithful",
            "mass_healing",
            "raise_the_dead",
            "humility_of_caesar",
            "terrify_the_unbeliever",
            "ignis_domini",
            "rebuke_the_unfaithful",
        ),
        104,
    ),
    "abraham": Forbear(
        "Abraham",
        75,
        "His tomb at Hebron, and the haram in Mecca",
        (
            "apparition",
            "resist_temptation",
            "grant_of_serenity",
            "the_incombustible_shroud",
            "the_dutiful_shepherd",
            "the_faithful_made_whole",
            "celestial_immunity",
            "mass_healing",
            "raise_the_dead",
        ),
        104,
    ),
    "david": Forbear("David", 75, "His tomb in Jerusalem", (), 105),
    "al_husayn": Forbear(
        "Al-Husayn",
        75,
        "His tombs at Karbala' and Cairo",
        (
            "apparition",
            "acknowledgment_of_evil",
            "expel_demons",
            "resist_temptation",
            "grant_of_serenity",
            "straighten_the_crippled",
            "the_faithful_made_whole",
            "celestial_immunity",
            "mass_healing",
            "humility_of_caesar",
            "terrify_the_unbeliever",
        ),
        105,
    ),
    "rabia": Forbear(
        "Rabi'a al-'Adawiyya",
        50,
        "Various sites in Basra, and her tomb in Jerusalem",
        (
            "acknowledgment_of_evil",
            "resist_temptation",
            "grant_of_serenity",
            "the_laborers_boon",
            "tomorrows_bounty",
            "the_faithful_made_whole",
            "humility_of_caesar",
            "the_earths_riches",
        ),
        105,
    ),
    "al_shafii": Forbear(
        "Al-Shafi'i",
        25,
        "His tomb in Cairo",
        (
            "acknowledgment_of_evil",
            "resist_temptation",
            "grant_of_serenity",
            "the_dutiful_shepherd",
            "humility_of_caesar",
        ),
        105,
    ),
    "nur_al_din": Forbear(
        "Nur al-Din",
        25,
        "His tomb in Damascus",
        (
            "apparition",
            "expel_demons",
            "the_laborers_boon",
            "the_leap_of_the_faithful",
            "terrify_the_unbeliever",
            "ignis_domini",
        ),
        105,
    ),
}

#: The Muslim Invocation Modifiers that are a tick (p. 103), by key.
TICKS: dict[str, tuple[str, int]] = {
    "feast_day": ("His feast day, normally his birthday", 3),
    "pilgrimage": ("A pilgrimage made to his tomb or shrine", 2),
    "relic_touched": ("Touching his relic", 1),
    "relic_owned": ("Owning his relic", 2),
    "peril": ("Imminent peril", 2),
    "no_zakat": ("No zakat paid within a year", -3),
    "miracle_lately": ("A miracle received within a month", -5),
    "unfamiliar": ("An unfamiliar forbear", -10),
}
#: Asking a specific miracle of his rather than general aid (p. 103).
SPECIFIC = -5

#: The Hajj (p. 108).
HAJJ_PIOUS = 3
HAJJ_FAITH = 3
PIOUS = "Pious"


@dataclass(frozen=True)
class Asking:
    """A baraka's total and each term as words."""

    total: int
    terms: tuple[str, ...]


def asking(
    character: Character,
    *,
    trait: int = 0,
    aura: int = 0,
    ticks: tuple[str, ...] = (),
    donation: int = 0,
    sin: int = 0,
    specific: bool = False,
) -> Asking:
    """Communication + Charm + the Muslim Invocation Modifiers (p. 103)."""
    c = character.characteristics
    charm = ability_level(character, "Charm")
    terms = [f"Communication {c.communication:+d}", f"+ Charm {charm}"]
    total = c.communication + charm

    def add(label: str, value: int) -> None:
        nonlocal total
        if value:
            terms.append(f"{'+' if value > 0 else '-'} {label} {abs(value)}")
            total += value

    add("his trait", max(0, trait))
    add("Divine aura", max(0, aura))
    for key in ticks:
        label, value = TICKS[key]
        add(label.lower(), value)
    add("donation", min(3, max(0, donation)))
    add("recent sin", -min(3, max(0, sin)))
    add("a specific miracle", SPECIFIC if specific else 0)
    return Asking(total, tuple(terms))


def ask(total: int, rng: random.Random) -> Invocation:
    """His simple die and the storyguide's, against 15 + it (p. 87)."""
    return dv.invoke(total, rng)


def chance(total: int) -> float:
    return dv.chance(total)


def make_hajj(character: Character) -> list[str]:
    """Pious +3 (never raised above it by the Hajj, nor lowered) and 3
    Faith Points (p. 108); what changed, in words."""
    lines: list[str] = []
    held = next(
        (t for t in character.personality_traits if t.name.casefold() == "pious"),
        None,
    )
    if held is None:
        character.personality_traits.append(ScoredTrait(PIOUS, HAJJ_PIOUS))
        lines.append(f"He gains Pious +{HAJJ_PIOUS}.")
    elif held.score < HAJJ_PIOUS:
        lines.append(f"Pious rises from {held.score:+d} to +{HAJJ_PIOUS}.")
        held.score = HAJJ_PIOUS
    else:
        lines.append(
            f"Pious stays {pious(character):+d}: the Hajj never raises it above +3."
        )
    character.background.faith_points += HAJJ_FAITH
    lines.append(f"He gains {HAJJ_FAITH} Faith Points.")
    return lines
