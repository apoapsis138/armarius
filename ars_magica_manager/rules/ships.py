"""Ships: what a covenant's ship can take, carry and do, without a
front-end. The record is models.ships.Ship, kept on a Possession of kind
"ship"; ship combat and, later, fleet battles pick ships from there.

SOURCE: Hermetic Projects (HP), The Hermetic Shipyard: Ship Damage p. 53,
the Ship Sizes and Capacity table p. 54, mundane craftsmen and quality
p. 63; City & Guild (C&G), Damaged Goods p. 77, superior and excellent
items pp. 69-70, ships, crews and costs pp. 84-85, Ship Combat pp. 86-87;
Errata p. 57 (to C&G p. 69: one quality bonus a total) and p. 80 (to HP:
no change to these rules); Definitive Edition, group combat pp. 395-396
and Travel p. 408.

- **Damage levels** (HP p. 53; C&G p. 77): the quality's base (Shoddy 1,
  Standard 2, Superior 3, Excellent 4, Supernatural 5) times the size's
  modifier, which HP's table gives ship by ship: x2 up to size +5, x3 for
  +6 to +8, x4 for +9 (and x1 for size +1 or less, C&G p. 77). A ship
  keeps working until every level is lost; then she is wrecked and any
  enchantment in her is lost (HP p. 65).
- **Stress checks** (C&G p. 77; HP p. 53): storms, fire, naval combat and
  magical attacks. Stress die + modifiers against 15: the captain's
  Profession (trained to use her), -1 previously repaired, -1 Shoddy, +1
  Superior, +3 Excellent, +5 Supernatural, + the magnitudes of her
  invested effects, -1 poor weather, -3 severe. Failure loses a damage
  level; a botch one level plus one more for every botch.
- **Crews** (HP p. 54): the table's crew is square-rigged; lateen rigging
  adds half as many again (the grain barges already include it). Cargo
  space given up carries fighting men: 8 a ton on a long voyage, 16 a
  quarter ton close to home (C&G p. 87).
- **Artillery** (C&G p. 86): a quarter ton of cargo each, at most one per
  20 tons of cargo space. A ballista kills a crewman a hit at up to 600
  yards; a light catapult incapacitates a simple die / 2 at up to 200;
  each reloads in ten rounds.
- **Quality** (HP p. 63; C&G pp. 69-70): Superior +1 to navigation and
  ship-handling rolls; Excellent its bonus (HP's example +2) there and to
  Lab Totals enchanting her; enchanting a Standard ship costs -1, a
  Shoddy one -3. Only one item's quality bonus counts on a roll (errata
  p. 57).
- **Worth** (HP p. 54; C&G pp. 84-85): HP's table prices each kind; C&G
  says four pounds per ten tons of cargo, and a galley 25 times its tons.
- **Ship combat** (C&G p. 86): each captain rolls stress die +
  Intelligence + Profession + up to 3 for an experienced crew, with what
  favours either side (a faster ship, fog). The winner boards or slips
  away; a galley rams (the rammed ship founders in 5 x a simple die
  minutes; a sailing ship that rams stays entangled) or shears oars (2 x
  a simple die rowers incapacitated, no way made until new oars are
  shipped). Boarding is a melee by the group combat rules (DE pp.
  395-396); the taller ship's men have +3 Attack and Defense until they
  are boarded.
- **Speed**: rules.journeys' sailing ship (C&G p. 85, 60 to 80 miles a
  day; DE p. 408, about 30, good ships with good wind three or four
  times that).

The app's readings, where the books leave a gap:
- HP's table and C&G p. 85 differ on crews and prices (neither is the
  DE): the form's "Like" fills HP's figures, and C&G's price is shown
  beside them;
- C&G's damage table lists size +5 under both x2 and x3; HP's ship table
  gives +5 ships x2, which is followed;
- the captain's Profession is the best of his Professions whose name
  speaks of ships (Sailor, Mariner, Captain, Ship, Navigator, Pilot);
- the taller ship is the larger one (by size); equal sizes give neither
  the +3;
- half again a crew rounds down (DE p. 6's default);
- a ballista or catapult shoots once when the ships come within its
  range, then every ten rounds.

Pattern: the ship types are a table of data (a dict), read by the form's
Like field as the Goods catalog fills a good; the stress check and ship
combat are plain functions over the record.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Character, Covenant, Possession, Saga
from ..models.ships import Ship
from . import equipment
from .lab import ability_score
from .rounding import round_down, round_up

SOURCE = (
    "Hermetic Projects, The Hermetic Shipyard, pp. 53-54, 63, 65; City & "
    "Guild, Damaged Goods p. 77, pp. 69-70, 84-87; Errata pp. 57, 80; "
    "Definitive Edition pp. 395-396, 408"
)
HP = "HP"
CG = "C&G"

SHIP_KIND = "ship"

#: Base damage levels by quality (HP p. 53; C&G p. 77).
BASE_DAMAGE_LEVELS: dict[str, int] = {
    equipment.SHODDY: 1,
    "Standard": equipment.STANDARD_DAMAGE_LEVELS,
    equipment.SUPERIOR: 3,
    equipment.EXCELLENT: 4,
    "Supernatural": 5,
}
#: Stress check modifier by quality (C&G p. 77).
QUALITY_STRESS: dict[str, int] = {
    equipment.SHODDY: -1,
    "Standard": 0,
    equipment.SUPERIOR: 1,
    equipment.EXCELLENT: 3,
    "Supernatural": 5,
}
#: Lab Total modifier for enchanting her (C&G p. 70): an Excellent ship
#: adds her bonus instead; a wondrous one counts as Superior.
ENCHANTING: dict[str, int] = {
    equipment.SHODDY: -3,
    "Standard": -1,
    equipment.SUPERIOR: 0,
    "Supernatural": 0,
}
SUPERIOR_BONUS = 1
REPAIRED = -1
#: Weather (C&G p. 77): its stress-check modifier.
WEATHER: dict[str, int] = {"fair": 0, "poor": -1, "severe": -3}
WEATHER_WORDS: dict[str, str] = {
    "fair": "Fair",
    "poor": "Poor (-1)",
    "severe": "Severe or no light (-3)",
}
#: What threatens a ship (HP p. 53).
EVENTS: dict[str, str] = {
    "storm": "A storm",
    "fire": "Fire",
    "combat": "Naval combat",
    "magic": "A magical attack",
}

#: Cargo for fighting men (C&G p. 87).
MEN_PER_TON_VOYAGE = 8
MEN_PER_QUARTER_TON_HOME = 16
#: Artillery (C&G p. 86).
ARTILLERY_TONS = 0.25
TONS_PER_ARTILLERY = 20
BALLISTA_RANGE = 600
CATAPULT_RANGE = 200
RELOAD_ROUNDS = 10
#: Ship combat (C&G p. 86).
MOST_CREW_BONUS = 3
TALLER_BONUS = 3
FOUNDER_MINUTES_PER_DIE = 5
SHEARED_ROWERS_PER_DIE = 2
#: Worth (C&G pp. 84-85).
POUNDS_PER_TEN_TONS = 4
GALLEY_POUNDS_PER_TON = 25
#: Words that make a Profession a seafaring one.
SEAFARING_WORDS = ("sail", "mariner", "captain", "ship", "navig", "pilot", "sea")
PROFESSION_PREFIX = "Profession:"
DEFAULT_PROFESSION = "Profession: Sailor"


@dataclass(frozen=True)
class ShipType:
    """A line of HP p. 54's Ship Sizes and Capacity table."""

    key: str
    name: str
    size: int
    tons: int
    crew: int
    cost: float  # pounds
    damage_modifier: int
    example: str


#: The book's ship types (HP p. 54), smallest first.
SHIP_TYPES: dict[str, ShipType] = {
    t.key: t
    for t in (
        ShipType("ferry", "Small river ferry", 3, 1, 2, 0.2, 2, "Small river ferry"),
        ShipType("lighter", "Lighter", 3, 8, 2, 2, 2, "Lighter"),
        ShipType("river_barge", "River barge", 4, 20, 3, 4, 2, "River barge"),
        ShipType(
            "buss", "Coastal buss", 5, 20, 8, 8, 2, "Coastal buss, knarr, small cog"
        ),
        ShipType(
            "medium_cog", "Medium cog", 6, 100, 12, 40, 3, "Medium cog, large nef"
        ),
        ShipType(
            "large_cog", "Large merchant cog", 7, 240, 18, 100, 3, "Large merchant cog"
        ),
        ShipType(
            "grain_barge",
            "Mediterranean grain barge",
            8,
            800,
            150,
            320,
            3,
            "Mediterranean grain barge (lateen crew included)",
        ),
        ShipType(
            "large_grain_barge",
            "Large Mediterranean grain barge",
            9,
            1200,
            200,
            600,
            4,
            "Large Mediterranean grain barge (lateen crew included)",
        ),
    )
}


def type_options() -> list[tuple[str, str]]:
    """The Like field's choices: each type, its example, size and tons."""
    return [
        (f"{t.example} (size {t.size:+d}, {_tons(t.tons)})", t.key)
        for t in SHIP_TYPES.values()
    ]


def _tons(tons: float) -> str:
    return f"{tons:g} ton" + ("" if tons == 1 else "s")


def type_fills(key: str, kind_name: str) -> dict[str, object]:
    """What choosing a type fills in: size, cargo and crew, and her kind
    unless one of the user's own is typed."""
    found = SHIP_TYPES.get(key)
    if found is None:
        return {}
    filled: dict[str, object] = {
        "size": found.size,
        "tons": found.tons,
        "crew": found.crew,
    }
    if not kind_name or kind_name in {t.name for t in SHIP_TYPES.values()}:
        filled["kind_name"] = found.name
    return filled


# -- damage --


def damage_modifier(size: int) -> int:
    """The size's damage level modifier (HP p. 54's table; C&G p. 77)."""
    if size <= 1:
        return 1
    if size <= 5:
        return 2
    if size <= 8:
        return 3
    return 4


def damage_levels(ship: Ship) -> int:
    """How many damage levels she has whole."""
    return BASE_DAMAGE_LEVELS[ship.quality] * damage_modifier(ship.size)


def damage_left(ship: Ship) -> int:
    return max(0, damage_levels(ship) - ship.damage_lost)


def wrecked(ship: Ship) -> bool:
    """Every damage level lost: broken, and her enchantments gone."""
    return damage_left(ship) == 0


def lost(ship: Ship) -> bool:
    """Wrecked, sunk or taken: no longer a ship to sail or fight."""
    return wrecked(ship) or bool(ship.fate)


def condition(ship: Ship) -> str:
    """ "whole", "damaged" (more than half left) or "badly" (half or
    fewer), for the colour of her damage; a ship sunk or taken is "badly"."""
    if ship.fate:
        return "badly"
    if ship.damage_lost <= 0:
        return "whole"
    whole = damage_levels(ship)
    return "damaged" if damage_left(ship) > whole // 2 else "badly"


# -- crew, cargo and artillery --


def crew(ship: Ship) -> int:
    """Her sailing crew: half again for lateen rigging (HP p. 54)."""
    if ship.lateen:
        return ship.crew + round_down(ship.crew / 2)
    return ship.crew


def fighting_men(ship: Ship) -> int:
    """The fighting men her given-up cargo carries (C&G p. 87)."""
    if ship.close_to_home:
        return round_down(ship.fighters_tons * 4 * MEN_PER_QUARTER_TON_HOME)
    return round_down(ship.fighters_tons * MEN_PER_TON_VOYAGE)


def artillery(ship: Ship) -> int:
    return ship.ballistae + ship.catapults


def artillery_limit(ship: Ship) -> int:
    """At most one piece per 20 tons of cargo space (C&G p. 86)."""
    return ship.tons // TONS_PER_ARTILLERY


def cargo_left(ship: Ship) -> float:
    """Tons left for cargo once artillery and fighting men are aboard."""
    return ship.tons - artillery(ship) * ARTILLERY_TONS - ship.fighters_tons


def problem(ship: Ship) -> str | None:
    """What's wrong with her figures, if anything."""
    if ship.tons < 0 or ship.crew < 0:
        return "Cargo and crew can't be negative."
    if ship.damage_lost < 0:
        return "Damage levels lost can't be negative."
    if ship.damage_lost > damage_levels(ship):
        return (
            f"She has only {damage_levels(ship)} damage levels to lose "
            f"({ship.quality} {BASE_DAMAGE_LEVELS[ship.quality]} x "
            f"{damage_modifier(ship.size)} for size {ship.size:+d})."
        )
    if min(ship.magnitudes, ship.ballistae, ship.catapults) < 0:
        return "Magnitudes and artillery can't be negative."
    if ship.fighters_tons < 0:
        return "Cargo given to fighting men can't be negative."
    if artillery(ship) > artillery_limit(ship):
        return (
            f"At most {artillery_limit(ship)} artillery pieces: one per 20 tons "
            "of cargo space (C&G p. 86)."
        )
    if cargo_left(ship) < 0:
        return (
            "Her artillery and fighting men take more than her "
            f"{_tons(ship.tons)} of cargo space."
        )
    return None


# -- quality --


def quality_bonus(ship: Ship) -> int:
    """Her bonus to navigation and ship-handling rolls (HP p. 63)."""
    if ship.quality == equipment.SUPERIOR:
        return SUPERIOR_BONUS
    if ship.quality == equipment.EXCELLENT:
        return ship.excellent_bonus
    return 0


def enchanting_modifier(ship: Ship) -> int:
    """Her quality's effect on Lab Totals enchanting her (C&G p. 70; HP
    p. 63)."""
    if ship.quality == equipment.EXCELLENT:
        return ship.excellent_bonus
    return ENCHANTING[ship.quality]


# -- worth --


def book_cost(ship: Ship) -> float | None:
    """HP p. 54's price for her type (None: typed in)."""
    found = SHIP_TYPES.get(ship.ship_type)
    return None if found is None else found.cost


def guild_worth(ship: Ship) -> int:
    """C&G's price: four pounds per ten tons, a galley 25 a ton."""
    if ship.galley:
        return ship.tons * GALLEY_POUNDS_PER_TON
    return round_down(ship.tons * POUNDS_PER_TEN_TONS / 10)


# -- the captain --


def captain(saga: Saga, ship: Ship) -> Character | None:
    return next((c for c in saga.characters if c.id == ship.captain_id), None)


def profession(character: Character | None) -> tuple[str, int]:
    """The captain's seafaring Profession and its score (with Puissant):
    the best one whose name speaks of ships; Profession: Sailor 0 if he
    has none."""
    if character is None:
        return DEFAULT_PROFESSION, 0
    best = (DEFAULT_PROFESSION, 0)
    for ability in character.abilities:
        name = ability.name
        if not name.startswith(PROFESSION_PREFIX):
            continue
        if not any(word in name.lower() for word in SEAFARING_WORDS):
            continue
        score, bonus = ability_score(character, name)
        if score + bonus > best[1] or best == (DEFAULT_PROFESSION, 0):
            best = (name, score + bonus)
    return best


# -- the stress check --


@dataclass(frozen=True)
class Term:
    words: str
    value: int


def stress_terms(
    ship: Ship, captain_of: Character | None, weather: str, repaired: bool
) -> list[Term]:
    """What adds to the stress die (C&G p. 77)."""
    name, score = profession(captain_of)
    terms = [
        Term(
            f"{captain_of.name}'s {name}" if captain_of is not None else "no captain",
            score,
        ),
        Term(ship.quality, QUALITY_STRESS[ship.quality]),
        Term("enchanted", ship.magnitudes),
        Term("weather", WEATHER.get(weather, 0)),
        Term("repaired", REPAIRED if repaired else 0),
    ]
    return [t for t in terms if t.value or t is terms[0]]


def stress_total(terms: list[Term]) -> int:
    return sum(t.value for t in terms)


def levels_lost(total: int, die: int, botches: int) -> int:
    """Damage levels a stress check costs: none on a success, one on a
    failure, one plus one for each botch on a botch (C&G p. 77)."""
    if botches > 0:
        return 1 + botches
    return 0 if total + die >= equipment.STRESS_EASE else 1


def take_damage(ship: Ship, levels: int) -> int:
    """She loses `levels` damage levels (never more than she has);
    returns how many she lost."""
    lost = min(levels, damage_left(ship))
    ship.damage_lost += lost
    return lost


# -- ship combat --


def captain_terms(
    intelligence: int, profession_score: int, crew_bonus: int, conditions: int
) -> int:
    """A captain's roll's modifiers: Intelligence + Profession + up to 3
    for an experienced crew, + what favours his side (C&G p. 86)."""
    return (
        intelligence
        + profession_score
        + max(0, min(MOST_CREW_BONUS, crew_bonus))
        + conditions
    )


def shots(rounds: int) -> int:
    """How many times a piece shoots while the ships close for `rounds`
    rounds within its range: once, then every ten rounds."""
    return round_up(max(0, rounds) / RELOAD_ROUNDS)


def taller(ours: int, theirs: int) -> str:
    """Which ship's men have +3 Attack and Defense until boarded: "ours",
    "theirs", or "" (the same size)."""
    if ours > theirs:
        return "ours"
    if theirs > ours:
        return "theirs"
    return ""


def founder_minutes(simple_die: int) -> int:
    return FOUNDER_MINUTES_PER_DIE * simple_die


def sheared_rowers(simple_die: int) -> int:
    return SHEARED_ROWERS_PER_DIE * simple_die


def catapult_struck(simple_die: int) -> int:
    """Crewmen a light catapult's hit incapacitates: a simple die / 2."""
    return round_down(simple_die / 2)


# -- finding ships --


def ships_of(covenant: Covenant) -> list[Possession]:
    """A covenant's ships, in the order added."""
    return [
        p for p in covenant.possessions if p.kind == SHIP_KIND and p.ship is not None
    ]


def saga_ships(saga: Saga) -> list[tuple[Covenant, Possession]]:
    """Every ship in the saga, with the covenant that keeps her: what ship
    combat and fleet battles pick from."""
    return [(c, p) for c in saga.covenants for p in ships_of(c)]


def ship_of(record: Possession) -> Ship:
    """A ship entry's figures (a fresh Ship if it has none yet)."""
    return record.ship if record.ship is not None else Ship()
