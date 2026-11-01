"""Galdor, the song-magic of Iceland's traditional galdramen, and what is
left of a trollson's fylgja (Land of Fire & Ice, Chapter 6). The book is
Fourth Edition, so Hedge Magic Revised Edition's frame goes over it: no
general Magic Resistance (p. 9) and no Twilight (p. 10). The catalog's
Traditional Galdramen hold the data; this module holds the numbers.

A song conjures a spirit to work an effect (pp. 46-48):

    Conjuring Total = stress die + Com + Music + Galdor Wisdom
                      + Song Talent + aura

- It works when the total is greater than the level; it is halved, down,
  while he touches the ground (the casting rule's divisor).
- No magnitude above the Song Talent; Song Talents go no higher than
  Galdor Wisdom. Duration is Momentary or Concentration.
- A minute of song a magnitude, or for what would be a Hermetic ritual 15
  minutes and a pawn a magnitude to the spirit. No vis boosts it.
- The spirit's Might is the total. Penetration is reckoned as the
  Definitive Edition's, total + bonus - level (DE p. 83): the book's "the
  Might is the Penetration" is older than the subtraction (DE p. 537).
- Concentration lasts while he sings: Sta + Music every hour against 6 +
  the hours; up to 3 short costs a Fatigue level, worse ends it. A total of
  twice the level leaves the spirit working a quality die of hours after.
- The landvaettir count as Faerie in every aura but a Magic one (p. 33):
  the tradition's `outside_magic` (rules.hedge_casting.power_realm).

More than Concentration comes from a lord of the landvaettir (p. 48). The
lord agrees or refuses in play, and the deal (BoundBeing, kind DEAL) holds
him, the service, the vis a year and any favour owed. Rolling for it is an
option, the Bargain of Houses of Hermes: Societates p. 136, with a
Summoning Strength of 0 as he goes to the lord:

    Bargain Total = Com + Bargain + 0 + stress die
    Ease Factor   = 18 + scope + length + duty + vis

The book's price, about double the magnitude in vis, is the standard the
vis modifier reads.

Binding a spirit in an item (p. 49): a total as the Conjuring Total's with
the item's Form and effect bonuses, Galdor Wisdom and the Song limited by
the Craft used. For life it must reach twice the level plus the frequency's
modifier; for one service, lasting a year and a day, the level.

A fylgja (pp. 32, 54-55) comes with Premonitions, or for a trollson with
the Fetch (Hedge Magic RE p. 76): Might 10, Size -3 at most. Each Mighty
Fylgja adds 10 Might and the next power; the first Large Fylgja allows Size
0, each more +1. The book's bear, Size +2 and Might 40, corporeal, is six
Virtues, three of each.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import BoundBeing, Character, TraditionDef
from . import hedge_casting as hc
from .casting import magnitude
from .creation_access import SONG_TALENTS
from .hyperborean import relic_vis
from .rounding import round_down, round_up

SOURCE = "Land of Fire & Ice, Icelandic Magic, pp. 46-50"
REALM_SOURCE = "Land of Fire & Ice, Landvaettir, p. 33"
BARGAIN_SOURCE = (
    "Land of Fire & Ice, Bargaining, p. 48; Houses of Hermes: Societates, "
    "Bargaining with the Jinni, p. 136"
)
FYLGJA_SOURCE = (
    "Land of Fire & Ice, Fylgjur and Mighty Fylgja, pp. 32, 54-55; Hedge Magic "
    "Revised Edition, Trollsynir, p. 76"
)

TRADITION_ID = "trad_galdramen"
TROLLSYNIR_ID = "trad_trollsynir"
WISDOM = "Galdor Wisdom"
SING = "Music"
CONJURING = "vf_galdor_conjuring"
ENCHANTMENT = "vf_galdor_enchantment"
#: The casting rules of the tradition's record.
CONJURE_RULE = "Galdor Conjuring"
GROUND_RULE = "Galdor Conjuring on the ground"
#: The bond (TraditionDef.bonds) a deal with a lord is kept under.
DEAL = "Deal with a lord"
#: The Song Talents commonly known (p. 47).
SONGS = SONG_TALENTS
#: The Durations a song, and a bound item, may have (pp. 47, 49).
DURATIONS: tuple[str, ...] = ("Momentary", "Concentration")
CONCENTRATION = "Concentration"
#: Minutes of song a magnitude, as a plain effect and as a ritual (p. 47).
MINUTES_PER_MAGNITUDE = 1
RITUAL_MINUTES_PER_MAGNITUDE = 15
#: Holding a song (p. 47).
HOLD_BASE = 6
HOLD_TIRED_MARGIN = 3
#: Distractions read Int + Music, 3 harder on the ground (p. 47).
GROUND_DISTRACTION = 3
#: True landvaettir are 10 Might stronger against Faerie spells (p. 33).
FAERIE_SPELL_MIGHT = 10

BARGAIN_EASE = 18
#: Houses of Hermes: Societates p. 136.
SCOPES: dict[str, int] = {"General": 3, "Specific": 0, "A single task": -3}
LENGTHS: dict[str, int] = {
    "A day": -3,
    "A week": 0,
    "A month": 3,
    "A season": 6,
    "A year": 9,
}
DUTIES: dict[str, int] = {"None": 0, "A simple duty": -3, "An onerous duty": -6}
VIS_UNDER = 2
VIS_OVER = -2
#: A botched bargain's Flaw, by how strong the lord is (p. 136).
NUISANCE = "vf_supernatural_nuisance"
PLAGUED = "vf_plagued_by_supernatural_entity"

#: Added to a Concentration effect's level for Constant Use (p. 49).
CONSTANT_USE = 5
#: A single-service enchantment lasts a year and a day (p. 49).
SERVICE_LIFE = "a year and a day"
BOUND_ITEM = "bound item"
RUNES = "Craft: Runes"

PREMONITIONS = "vf_premonitions"
FETCH = "vf_fetch"
MIGHTY_FYLGJA = "vf_mighty_fylgja"
LARGE_FYLGJA = "vf_large_fylgja"
BASE_MIGHT = 10
MIGHT_STEP = 10
BASE_SIZE = -3
#: What each Mighty Fylgja adds, in order (p. 55).
FYLGJA_POWERS: tuple[str, ...] = ("Phantom", "Spirit Voice", "Corporeality")


def tradition_rule(tradition: TraditionDef, name: str):
    """The tradition's casting rule of that name."""
    return next(rule for rule in tradition.casting if rule.name == name)


def conjures(character: Character) -> bool:
    return _holds(character, CONJURING)


def enchants(character: Character) -> bool:
    return _holds(character, ENCHANTMENT)


def bargains(character: Character) -> bool:
    return conjures(character) or enchants(character)


def _holds(character: Character, vf_id: str) -> bool:
    return any(vf.vf_id == vf_id for vf in character.virtues_flaws)


def songs_of(character: Character) -> list[str]:
    """The Song Talents the character holds, in the book's order, and any
    other of the tradition's the troupe added."""
    return [song for song in SONGS if hc.holds(character, song)]


def song_score(character: Character, song: str) -> int:
    """A Song Talent's score, no higher than Galdor Wisdom (p. 46)."""
    return min(hc.score(character, song), hc.score(character, WISDOM))


def song_problem(character: Character, song: str, level: int) -> str | None:
    """A galdraman can't ask a service of more magnitudes than his Song
    Talent (pp. 47, 49)."""
    most = song_score(character, song)
    if magnitude(level) > most:
        return (
            f"Level {level} is magnitude {magnitude(level)}; {song} {most} asks "
            f"no more than magnitude {most}."
        )
    return None


def on_the_ground(total: int) -> int:
    """A total worked in contact with the ground (p. 47)."""
    return round_down(total / 2)


def song_minutes(level: int, *, ritual: bool = False) -> int:
    """How long the song takes (p. 47)."""
    each = RITUAL_MINUTES_PER_MAGNITUDE if ritual else MINUTES_PER_MAGNITUDE
    return each * magnitude(level)


def ritual_vis(level: int) -> int:
    """The pawns a ritual gives the spirit on arrival (p. 47)."""
    return magnitude(level)


@dataclass(frozen=True)
class Conjured:
    """What a Conjuring Total does: whether the spirit comes, its Might,
    and whether it works on after the song stops."""

    works: bool
    might: int
    lingers: bool


def conjured(total: int, level: int, duration: str) -> Conjured:
    """The total must be greater than the level; twice the level leaves a
    Concentration effect working on (pp. 47-48)."""
    works = total > level
    lingers = works and duration == CONCENTRATION and total >= 2 * level
    return Conjured(works, total, lingers)


def hold_total(character: Character) -> int:
    """Sta + Music, before the die (p. 47)."""
    return character.characteristics.stamina + hc.score(character, SING)


def hold_ease(hour: int) -> int:
    """The roll at the end of a song's hour (p. 47)."""
    return HOLD_BASE + hour


def holds_song(total: int, hour: int) -> tuple[bool, bool]:
    """(the song goes on, a Fatigue level is lost) for an hour's roll."""
    short = hold_ease(hour) - total
    if short <= 0:
        return True, False
    if short <= HOLD_TIRED_MARGIN:
        return True, True
    return False, False


def distraction_ease(ease: int, *, on_ground: bool) -> int:
    """A distraction's Ease Factor (rolled with Int + Music, p. 47)."""
    return ease + (GROUND_DISTRACTION if on_ground else 0)


def against_faerie_spell(might: int) -> int:
    """A true landvaett's or yarthkin's Might against a spell that affects
    faeries (p. 33)."""
    return might + FAERIE_SPELL_MIGHT


# ---------------------------------------------------------------------------
# Deals with a lord


def standard_vis(level: int) -> int:
    """The price a lord asks, about double the magnitude (p. 48)."""
    return 2 * magnitude(level)


def vis_modifier(standard: int, offered: int) -> int:
    """+2 a pawn under the standard, -2 a pawn over it (HoH:S p. 136)."""
    gap = offered - standard
    return gap * (VIS_OVER if gap > 0 else -VIS_UNDER)


def bargain_ease(
    scope: str, length: str, duty: str, *, standard: int, offered: int
) -> int:
    """The Bargain's Ease Factor (HoH:S p. 136)."""
    return (
        BARGAIN_EASE
        + SCOPES[scope]
        + LENGTHS[length]
        + DUTIES[duty]
        + vis_modifier(standard, offered)
    )


def bargain_total(character: Character, die: int = 0) -> int:
    """Com + Bargain + die; the Summoning Strength is 0, as he goes to the
    lord and summons nothing."""
    return (
        character.characteristics.communication + hc.score(character, "Bargain") + die
    )


def botch_flaw(*, weak: bool) -> str:
    """What a botched bargain lays on him (HoH:S p. 136)."""
    return NUISANCE if weak else PLAGUED


def deals(character: Character) -> list[BoundBeing]:
    """The character's deals with lords."""
    return [b for b in character.bound_beings if b.kind == DEAL]


def deal_words(deal: BoundBeing) -> str:
    """A deal as the sheet says it."""
    parts = [deal.service or "No service written down"]
    if deal.vis_yearly:
        parts.append(f"{deal.vis_yearly} pawns a year")
    if deal.favour:
        parts.append(f"owes: {deal.favour}")
    return "; ".join(parts)


def tithes(character: Character) -> int:
    """The pawns his deals take a year."""
    return sum(deal.vis_yearly for deal in deals(character))


# ---------------------------------------------------------------------------
# Binding a spirit in an item


def bind_score(
    character: Character,
    song: str,
    craft: str,
    *,
    bonuses: int = 0,
    aura: int = 0,
) -> int:
    """The enchantment total before its die: Com + Music, Galdor Wisdom and
    the Song each no higher than the Craft, the item's bonuses and the
    aura's modifier (p. 49)."""
    limit = hc.score(character, craft)
    return (
        character.characteristics.communication
        + hc.score(character, SING)
        + min(hc.score(character, WISDOM), limit)
        + min(song_score(character, song), limit)
        + bonuses
        + aura
    )


def bind_level(level: int, *, constant: bool = False) -> int:
    """The effect's level, +5 made Constant Use (p. 49)."""
    return level + (CONSTANT_USE if constant else 0)


def bind_needs(level: int, *, lifetime: bool, frequency: int = 0) -> int:
    """What the total must reach: double the level plus the frequency's
    modifier for life, the level for a single service (p. 49)."""
    return 2 * level + frequency if lifetime else level


def bind_vis(level: int) -> int:
    """The pawns the spirit takes first, about the Hermetic item's: one a
    10 levels or fraction (p. 49; DE p. 258)."""
    return relic_vis(level)


def crafts_of(character: Character) -> list[str]:
    """The Crafts he could make the item with: any he holds. Craft: Runes
    is Scribe Runes, which may stand as the Craft and inscribe a ready-made
    item (p. 49)."""
    return [a.name for a in character.abilities if a.name.startswith("Craft: ")]


# ---------------------------------------------------------------------------
# Longevity


def mead_pawns(age: int) -> int:
    """The least pawns in a year's mead: one a decade of his life (p. 49)."""
    return round_up(max(age, 0) / 10)


# ---------------------------------------------------------------------------
# The fylgja


@dataclass(frozen=True)
class Fylgja:
    """A fylgja's Might, powers and the largest Size it may take."""

    might: int
    powers: tuple[str, ...]
    size: int


def has_fylgja(character: Character) -> bool:
    """Premonitions brings one (p. 54); a trollson's is the Fetch (HMRE p.
    76)."""
    if _holds(character, PREMONITIONS):
        return True
    return _holds(character, FETCH) and TROLLSYNIR_ID in character.traditions


def _copies(character: Character, vf_id: str) -> int:
    return sum(1 for vf in character.virtues_flaws if vf.vf_id == vf_id)


def fylgja_of(character: Character) -> Fylgja | None:
    """The character's fylgja, or None."""
    if not has_fylgja(character):
        return None
    mighty = _copies(character, MIGHTY_FYLGJA)
    large = _copies(character, LARGE_FYLGJA)
    return Fylgja(
        might=BASE_MIGHT + MIGHT_STEP * mighty,
        powers=FYLGJA_POWERS[:mighty],
        size=large - 1 if large else BASE_SIZE,
    )


def fylgja_lines(character: Character) -> list[str]:
    """The fylgja as the chapter shows it."""
    found = fylgja_of(character)
    if found is None:
        return []
    powers = ", ".join(found.powers) or "none"
    tithe = tithes(character)
    lines = [
        f"Fylgja: Might {found.might}; powers {powers}; Size up to {found.size:+d}."
    ]
    if tithe:
        lines.append(f"Deals with lords: {tithe} pawns a year.")
    return lines
