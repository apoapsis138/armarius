"""Building a ship and opening her for enchantment (Hermetic Projects,
The Hermetic Shipyard, pp. 62-67; City & Guild pp. 67-70).

- **By a shipwright and his team** (HP p. 62; C&G p. 68): a master with
  Profession: Shipwright 5 builds half a ship a season, more or less in
  proportion to his score, taken to the nearest nice fraction (two
  seasons at 5, one at 10). The Conscientious Carpenter adds 1 to his
  score for the time (HP p. 64). Her quality is his Workshop Total
  (Characteristic + Profession: Shipwright + the workshop's Innovation
  and Raw Materials) against the Craft Levels: 3 Shoddy, 6 Standard, 12
  Superior, 15 Excellent, each a point higher in a supernatural aura; an
  Excellent ship's bonus is +1 for every 3 over, at most his score / 3,
  rounded up (C&G pp. 67-69; HP p. 63).
- **By Rego craft magic** (HP pp. 63-64): Perception + Finesse + a stress
  die against the ship's Ease Factor: a river barge 15, a coastal buss
  21, a large cog 27, a grain barge 30. Each is a shipwright's task's
  Ease Factor + what its time adds (a season +6, a year +9, Covenants p.
  49), so another ship's is typed. Led by a Hermetic shipwright, her
  quality is his Profession: Shipwright plus the workshop's bonus (HP p.
  63), his Workshop Total as for a shipwright's build.
- **By a Creo ritual** (HP p. 65): Intelligence + Finesse + a stress die
  against 9; the conjured ship is a copy of the ritual's template, in
  perfect condition.
- **Opening her** (HP pp. 66-67): pawns by part: the hull 10 (small) to
  18 (huge), a keel alone 10, a mast 8, rigging 10, sails 5, a rudder or
  steering oar 8, a castle 8, an anchor 20. Opened as one part, effects
  in her have her shape bonuses but not the other parts' materials; as a
  compound device, her capacity is the costliest part or the sum of the
  parts, and the season takes that many pawns (at most twice Magic
  Theory).

The app's readings, where the books leave a gap:
- a ship's Workshop Total takes Intelligence, as the master mason's
  does, the shipwright designing and leading the team rather than
  working the wood;
- a Creo ritual makes a ship of the template's quality; a failed roll,
  by craft magic or ritual, makes no ship;
- the hull's pawns follow her size: +5 and smaller 10, +6 12, +7 14, +8
  16, +9 18.
"""

from __future__ import annotations

from .rounding import round_up

SOURCE = (
    "Hermetic Projects, The Hermetic Shipyard, pp. 62-67; City & Guild, "
    "Finished Goods, pp. 67-70"
)

SHIPWRIGHT, CRAFT_MAGIC, CREO_RITUAL = "shipwright", "craft_magic", "creo_ritual"
METHODS: dict[str, str] = {
    SHIPWRIGHT: "A shipwright and his team",
    CRAFT_MAGIC: "Rego craft magic (The Hands of Phereclus)",
    CREO_RITUAL: "A Creo ritual (Conjuration of the Seaworthy Cog)",
}
PROFESSION = "Profession: Shipwright"
#: The score at which a shipwright builds half a ship a season.
HALF_A_SHIP_AT = 5
#: The Creo ritual's Finesse roll (HP p. 65).
RITUAL_EASE = 9
#: The Craft Levels (C&G p. 67), best first, and the aura's +1 (p. 69).
CRAFT_LEVELS: tuple[tuple[int, str], ...] = (
    (15, "Excellent"),
    (12, "Superior"),
    (6, "Standard"),
    (3, "Shoddy"),
)
AURA_CRAFT_LEVEL = 1
EXCELLENT_LEVEL = 15


def seasons_to_build(score: int) -> int:
    """The seasons a master of `score` takes: half a ship a season at 5,
    in proportion to his score, to the nearest nice fraction (C&G p. 68:
    0.4 of one is a third, so three seasons)."""
    if score <= 0:
        return 0
    share = score / (2 * HALF_A_SHIP_AT)
    if share >= 1:
        return 1
    return min(range(1, 41), key=lambda n: abs(1 / n - share))


def workshop_quality(total: int, in_aura: bool = False) -> str:
    """The quality a Workshop Total reaches (C&G p. 67); "" below
    Shoddy."""
    raised = AURA_CRAFT_LEVEL if in_aura else 0
    return next((label for level, label in CRAFT_LEVELS if total >= level + raised), "")


def excellent_bonus(total: int, score: int, in_aura: bool = False) -> int:
    """An Excellent ship's bonus: +1 for every 3 over its Craft Level, at
    most the score / 3, rounded up (C&G p. 69)."""
    level = EXCELLENT_LEVEL + (AURA_CRAFT_LEVEL if in_aura else 0)
    return max(0, min((total - level) // 3, round_up(score / 3)))


#: The Rego craft magic Ease Factors of the ships HP p. 63's table names.
CRAFT_MAGIC_EASE: dict[str, int] = {
    "river_barge": 15,
    "buss": 21,
    "large_cog": 27,
    "grain_barge": 30,
}


def craft_magic_ease(ship_type: str) -> int | None:
    """The Rego craft magic Ease Factor to build a ship of `ship_type`
    (HP p. 63's table); None for a ship it doesn't name, whose Ease
    Factor the troupe works out (Covenants p. 49)."""
    return CRAFT_MAGIC_EASE.get(ship_type)


#: Pawns to open each part of a ship (HP p. 66).
PARTS: dict[str, tuple[str, int]] = {
    "keel": ("Keel (alone)", 10),
    "mast": ("Mast", 8),
    "rigging": ("Rigging", 10),
    "sails": ("Sails", 5),
    "rudder": ("Rudder or steering oar", 8),
    "castle": ("Castle", 8),
    "anchor": ("Anchor", 20),
}


def hull_pawns(size: int) -> int:
    """The hull's pawns, by the ship's size (HP p. 66)."""
    return 2 * max(5, min(size, 9))


def opening(size: int, parts: list[str]) -> tuple[int, int]:
    """Pawns to open her as a compound device of the hull and `parts`: the
    costliest part's, and all of them together (HP p. 67)."""
    costs = [hull_pawns(size), *(PARTS[p][1] for p in parts if p in PARTS)]
    return max(costs), sum(costs)


def theory_needed(pawns: int) -> int:
    """The Magic Theory that handles `pawns` in a season (twice it)."""
    return round_up(pawns / 2)
