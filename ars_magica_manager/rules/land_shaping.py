"""Shaping the land by magic: the Rituals that raise an island from the
sea, their levels and vis, and what the new land is worth (Transforming
Mythic Europe, Chapter Three, pp. 54-67 and 71-77).

- **Making stuff** (DE p. 359; TME pp. 55-59). A permanent creation is a
  Momentary Creo Ritual, Touch, Individual: at least level 20, so a
  smaller work costs no less (DE p. 311). The guideline sets the base
  (dirt, sand, mud or clay 1; stone or glass 3; base metal 5; precious
  metal 15; gemstone 25) and the base Individual (ten cubic paces of
  dirt, one of stone, a cubic foot of base metal, a tenth of that of
  precious metal, a cubic inch of gemstone); each magnitude for size makes
  ten times as much (DE p. 310). Below level 5 a magnitude adds 1 level
  (rules.spell_levels). So level 20 makes 10,000 cubic paces of stone, or
  10 million of soil (TME pp. 55, 59). Wood and animal bone are as hard
  as stone, human bone as base metal (pp. 58-59).
- **The wall** (pp. 54-58). Its volume is its circumference (or four
  sides, for a square) x height x thickness; a solid cylinder is all
  stone. The book's wall is 30 paces high and 2 thick (240 high for a tall
  cylinder). Complexity adds magnitudes: crenellations +1, machicolations
  +1, a sea gate +1, artistic statuary +1 (a sigil's is free); a fire
  step, hoardings or a greater height add none, only stone (pp. 56-57). An
  unnatural wall needs a Muto requisite, +1 (DE p. 359; TME p. 58). The
  troupe may cap complexity at three magnitudes (p. 56).
- **The ablative slope** (p. 56): earth equal in volume to the wall at
  its foot; three magnitudes below the wall's spell.
- **The fill** (p. 59): the enclosed space, to the wall's height, of soil
  or clay; stone is three magnitudes harder, +1 for several kinds (p. 60).
- **Surface life** (p. 62). Grassland: CrHe Group Ritual, Base 1, +1
  Touch, +2 Group; +1 size covers 1.25 acres, each more ten times that. A
  forest: Base 1, +1 Touch, +2 for trees of Size +2, +2 Group; +3 size
  makes 1,000 trees.
- **The land** (p. 62). A manor is 600 acres of mixed land (400 if highly
  fertile, a third less) yielding 20 pounds a year before expenses, with 5
  to 60 peasant families (as LoM p. 72, manors.py).
- **Boundary spells** (pp. 71-77). A base Boundary is a hundred paces
  across; each magnitude for size multiplies its area by ten (DE p. 310).
  A ward is the level chosen + 35 for Touch, Sun and Boundary (p. 71),
  plus the island's size. The book's island-wide spells are listed with
  their designs and raised for the island.
- **Casting** (DE p. 213). Fifteen minutes and one pawn of vis (of the
  Technique or the Form, at most the caster's score in that Art of each)
  per magnitude; the long-term Fatigue a Ritual costs comes back with a
  night's sleep.
- **Auras** (TME p. 66, RoP: Magic p. 10). A great Ritual leaves a
  preternatural tether of (level - 40) / 10, rounded down; an ancient
  monument 1 per full century of use; a magical being that dwells there a
  year (Might / 10).

Where the Definitive Edition and TME disagree, the DE is used: a
Boundary's size multiplies its area by ten each magnitude, so a 3-mile
island needs 4 magnitudes, not TME's 2 (p. 74); Intellego Boundary spells
need no magnitudes for size (DE p. 310). The Herbam spells' printed levels
are TME's own arithmetic slips (p. 62): its forest's working (Base 1, +8
magnitudes, rising by 1 a magnitude below level 5) comes to level 25, not
the 40 printed, and its grassland's (Base 1, +4) to level 5, raised to 20
as every Ritual is (DE p. 311), not the 10 printed. The Errata (p. 84) puts TME's 126-mile
canal spell at level 30.

Pattern: plain functions over the project's design (models.LandProject),
so both front-ends, the season's outcome and the tests ask the same.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..models import LAND_KIND, LandProject, Saga
from ..models.land_shaping import (
    ANIMAL_BONE,
    BASE_METAL,
    HUMAN_BONE,
    PRECIOUS_METAL,
    SOIL,
    SOLID,
    SQUARE,
    STONE,
    WOOD,
)
from .casting import magnitude
from .rounding import round_down
from .spell_levels import RITUAL_MINIMUM, add_magnitudes

SOURCE = (
    "Transforming Mythic Europe, Chapter Three: The Island of the Magicians, "
    "pp. 54-67, 71-77; Errata p. 84; Ars Magica Definitive Edition pp. 213, "
    "310-311, 359; Realms of Power: Magic p. 10"
)

#: A pace is about a yard: TME's figures use 1,760 to the mile.
PACES_PER_MILE = 1760
SQUARE_PACES_PER_ACRE = 4840

#: The magnitudes a permanent creation's Touch Range adds (DE p. 311).
TOUCH = 1


@dataclass(frozen=True)
class Material:
    """What Creo Terram makes (DE p. 359): its guideline and how many
    cubic paces its base Individual holds."""

    name: str
    base: int
    individual: float
    form: str = "Terram"


EARTH = Material("earth", 1, 10.0)
STONE_STUFF = Material("stone", 3, 1.0)
METAL = Material("base metal", 5, 1 / 27)
NOBLE = Material("precious metal", 15, 1 / 270)
GEMSTONE = Material("gemstone", 25, 1 / 46656)

#: Each wall material, as the book reckons its difficulty (TME pp. 58-59),
#: with the Form that creates it.
WALL_STUFF: dict[str, Material] = {
    STONE: STONE_STUFF,
    BASE_METAL: METAL,
    PRECIOUS_METAL: NOBLE,
    WOOD: Material("wood", 3, 1.0, "Herbam"),
    ANIMAL_BONE: Material("animal bone", 3, 1.0, "Animal"),
    HUMAN_BONE: Material("human bone", 5, 1 / 27, "Corpus"),
}


@dataclass(frozen=True)
class Feature:
    """A wall's ornament or defence: the magnitudes it adds (TME pp.
    56-57)."""

    key: str
    label: str
    magnitudes: int
    note: str


WALL_FEATURES: tuple[Feature, ...] = (
    Feature("crenellations", "Crenellations", 1, "crenels and merlons (p. 56)"),
    Feature("fire_step", "A fire step", 0, "uses more fill, not levels (p. 57)"),
    Feature("machicolations", "Machicolations", 1, "on corbels (p. 57)"),
    Feature("hoardings", "Beam holes for hoardings", 0, "no levels (p. 57)"),
    Feature("sea_gate", "A sea gate and harbor", 1, "its metal parts (p. 57)"),
    Feature("statuary", "Artistic statuary", 1, "free if the caster's sigil (p. 57)"),
)
FEATURES_BY_KEY: dict[str, Feature] = {f.key: f for f in WALL_FEATURES}
#: The troupe's optional cap on complexity's magnitudes (p. 56).
COMPLEXITY_CAP = 3
#: A Muto requisite for an unnatural material (DE p. 359; TME p. 58), and
#: several kinds of stone in one fill (p. 60).
UNNATURAL = 1
MIXED_STONE = 1

#: TME's standard wall (p. 54) and a tall cylinder's (p. 55).
WALL_HEIGHT = 30
TALL_WALL_HEIGHT = 240
WALL_THICKNESS = 2

#: Grassland (p. 62): CrHe Ritual, Base 1, +1 Touch, +2 Group; a base
#: Group covers an eighth of an acre (+1 size, 1.25 acres).
GRASS_BASE, GRASS_STEPS, GRASS_ACRES = 1, TOUCH + 2, 0.125
#: A forest (p. 62): Base 1, +1 Touch, +2 Size +2 trees, +2 Group; a base
#: Group is one such tree's worth (+3 size, 1,000 trees).
FOREST_BASE, FOREST_STEPS, FOREST_TREES = 1, TOUCH + 2 + 2, 1

#: A manor (TME p. 62, LoM p. 72): acres of mixed land, a third fewer if
#: highly fertile, its pounds a year before expenses, and its families.
MANOR_ACRES = 600
FERTILE_ACRES = 400
MANOR_POUNDS = 20
FAMILIES = (5, 60)

#: A base Boundary's diameter in paces (DE p. 310).
BOUNDARY_PACES = 100
#: Touch, Sun and Boundary on a ward (TME p. 71): seven magnitudes.
WARD_STEPS = 1 + 2 + 4

#: A Ritual's minutes a magnitude (DE p. 213).
MINUTES_PER_MAGNITUDE = 15


# -- making stuff --


def level_for_size(base: int, steps: int, size: int) -> int:
    """A Ritual's level: `base` raised by `steps` magnitudes (Range,
    Target, complexity) and `size` more for size, at least level 20."""
    return max(RITUAL_MINIMUM, add_magnitudes(base, steps + size))


def size_reached(base: int, steps: int, level: int) -> int | None:
    """The magnitudes of size a Ritual of `level` has room for (None when
    it is too low for the design at all)."""
    if level < level_for_size(base, steps, 0):
        return None
    size = 0
    while level_for_size(base, steps, size + 1) <= level:
        size += 1
    return size


def size_needed(amount: float, unit: float) -> int:
    """The magnitudes of size that reach `amount`, each ten times the
    last, from `unit` at none."""
    size = 0
    while unit * 10**size < amount * (1 - 1e-9):
        size += 1
    return size


def created_volume(material: Material, level: int, complexity: int = 0) -> float:
    """The cubic paces a permanent creation of `material` at `level`
    makes, with `complexity` magnitudes spent on its shape (0 when the
    level is too low)."""
    size = size_reached(material.base, TOUCH + complexity, level)
    return 0.0 if size is None else material.individual * 10**size


def creation_level(material: Material, volume: float, complexity: int = 0) -> int:
    """The level a permanent creation of `volume` cubic paces of
    `material` needs."""
    size = size_needed(volume, material.individual)
    return level_for_size(material.base, TOUCH + complexity, size)


# -- the island's measures --


def paces(miles: float) -> float:
    return miles * PACES_PER_MILE


def land_area(shape: str, across: float) -> float:
    """The island's area in square paces: a circle `across` paces wide,
    or a square of that side."""
    if shape == SQUARE:
        return across * across
    return math.pi * (across / 2) ** 2


def acres(shape: str, across: float) -> float:
    return land_area(shape, across) / SQUARE_PACES_PER_ACRE


def wall_volume(shape: str, across: float, height: int, thickness: int) -> float:
    """The wall's stone in cubic paces (TME pp. 55-56): its length times
    its height and thickness; a solid cylinder is all stone."""
    if shape == SOLID:
        return land_area(shape, across) * height
    length = 4 * across if shape == SQUARE else math.pi * across
    return length * height * thickness


def wall_reach(shape: str, volume: float, height: int, thickness: int) -> float:
    """How wide (paces) a wall of `volume` cubic paces makes the island."""
    if shape == SOLID:
        return 2 * math.sqrt(volume / height / math.pi)
    per_pace = 4 if shape == SQUARE else math.pi
    return volume / (per_pace * height * thickness)


def fill_volume(shape: str, across: float, depth: int) -> float:
    """The enclosed space to fill, in cubic paces, to the wall's height
    (p. 59); a solid cylinder has none."""
    if shape == SOLID:
        return 0.0
    return land_area(shape, across) * depth


def complexity(project: LandProject) -> int:
    """The wall's magnitudes for complexity: its features and an unnatural
    material, capped at three when the troupe uses the option."""
    found = sum(FEATURES_BY_KEY[k].magnitudes for k in project.features)
    found += UNNATURAL if project.unnatural else 0
    return min(found, COMPLEXITY_CAP) if project.cap_complexity else found


# -- surface life --


def grass_level(area_acres: float) -> int:
    return level_for_size(GRASS_BASE, GRASS_STEPS, size_needed(area_acres, GRASS_ACRES))


def grass_acres(level: int) -> float:
    size = size_reached(GRASS_BASE, GRASS_STEPS, level)
    return 0.0 if size is None else GRASS_ACRES * 10**size


def forest_level(trees: int) -> int:
    return level_for_size(FOREST_BASE, FOREST_STEPS, size_needed(trees, FOREST_TREES))


def forest_trees(level: int) -> int:
    size = size_reached(FOREST_BASE, FOREST_STEPS, level)
    return 0 if size is None else FOREST_TREES * 10**size


# -- the land and its worth --


def manors_supported(area_acres: float, *, fertile: bool = False) -> int:
    """Whole manors the land makes (TME p. 62)."""
    return int(area_acres // (FERTILE_ACRES if fertile else MANOR_ACRES))


def manor_acres(fertile: bool) -> int:
    return FERTILE_ACRES if fertile else MANOR_ACRES


def yearly_pounds(manors: int) -> int:
    """The manors' income before expenses (TME p. 62)."""
    return manors * MANOR_POUNDS


# -- Boundaries --


def boundary_magnitudes(area_square_paces: float) -> int:
    """The magnitudes a Boundary spell adds for an area this big: each
    multiplies a base Boundary's area by ten (DE p. 310)."""
    base = math.pi * (BOUNDARY_PACES / 2) ** 2
    return size_needed(area_square_paces, base)


@dataclass(frozen=True)
class BoundarySpell:
    """One of TME's island-wide spells (pp. 71-77): its Arts, base and the
    magnitudes of its design before the island's size."""

    name: str
    technique: str
    form: str
    base: int
    steps: int
    page: int
    what: str

    @property
    def book_level(self) -> int:
        return level_for_size(self.base, self.steps, 0)

    def level(self, extra: int) -> int:
        """Its level raised `extra` magnitudes for the Boundary's size; an
        Intellego spell's size doesn't matter (DE p. 310)."""
        if self.technique == "Intellego":
            extra = 0
        return level_for_size(self.base, self.steps, extra)


BOUNDARY_SPELLS: tuple[BoundarySpell, ...] = (
    BoundarySpell(
        "Weather Made Good",
        "Muto",
        "Aquam",
        4,
        1 + 3 + 4,
        71,
        "no rain falls on the island for a month",
    ),
    BoundarySpell(
        "The Command of Every Beast",
        "Rego",
        "Animal",
        2,
        1 + 1 + 4,
        74,
        "one command to every beast on the island",
    ),
    BoundarySpell(
        "The Eyes of Every Beast",
        "Intellego",
        "Animal",
        10,
        1 + 1 + 4,
        74,
        "sense what the island's animals see",
    ),
    BoundarySpell(
        "The Lost City",
        "Perdo",
        "Imaginem",
        4,
        1 + 2 + 4 + 1 + 1,
        74,
        "the wall and all within it invisible from outside, for a day",
    ),
    BoundarySpell(
        "Murderous Woodland",
        "Rego",
        "Herbam",
        10,
        1 + 2 + 4 + 2,
        74,
        "every tree on the island walks and fights, for a day",
    ),
    BoundarySpell(
        "Remembered Messages",
        "Muto",
        "Mentem",
        1,
        1 + 2 + 4,
        74,
        "a prepared memory replaced with one message, in everyone",
    ),
    BoundarySpell(
        "Strange Tricks Using Canal Contents",
        "Muto",
        "Aquam",
        2,
        1 + 2 + 4,
        77,
        "the canals' water becomes another natural liquid, for a day",
    ),
)
SPELLS_BY_NAME: dict[str, BoundarySpell] = {s.name: s for s in BOUNDARY_SPELLS}


def ward_level(chosen: int, extra: int) -> int:
    """A ward's level over the island (TME p. 71): the level chosen, +35
    for Touch, Sun and Boundary, and `extra` magnitudes for its size."""
    return add_magnitudes(chosen, WARD_STEPS + extra)


def aegis_level(chosen: int, extra: int) -> int:
    """An Aegis of the Hearth over the whole island: its level, raised for
    the Boundary's size."""
    return add_magnitudes(chosen, extra)


def fumigant_might(level: int, extra: int) -> int:
    """The Might of the minor demons a Fumigant of Minor Demons of `level`
    destroys (TME p. 74): level - 25, less for a larger Boundary."""
    return max(0, level - 25 - 5 * extra)


# -- casting --


def ritual_pawns(level: int) -> int:
    return magnitude(level)


def ritual_minutes(level: int) -> int:
    return MINUTES_PER_MAGNITUDE * magnitude(level)


def vis_limit(technique_score: int, form_score: int) -> int:
    """The most pawns a magus can put into one Ritual: at most his score
    in each Art the vis is of (DE p. 213)."""
    return max(0, technique_score) + max(0, form_score)


# -- auras --


def residue_tether(level: int) -> int:
    """The preternatural tether a Ritual's casting leaves (RoP: Magic p.
    10): (level - 40) / 10, rounded down."""
    return max(0, round_down((level - 40) / 10))


def monument_tether(years: int) -> int:
    """An ancient structure's tether: 1 per full century of use (RoP:
    Magic p. 10; TME p. 66)."""
    return max(0, years // 100)


def being_tether(might: int) -> int:
    """A magical being dwelling there a year or more: Might / 10, rounded
    down (RoP: Magic p. 10)."""
    return max(0, might // 10)


# -- the works of a project --


@dataclass(frozen=True)
class Work:
    """One Ritual of a project: what it does, its Arts and level."""

    name: str
    technique: str
    form: str
    level: int
    what: str

    @property
    def arts(self) -> str:
        return f"{self.technique[:2]}{self.form[:2]}"

    @property
    def pawns(self) -> int:
        return ritual_pawns(self.level)

    @property
    def minutes(self) -> int:
        return ritual_minutes(self.level)

    @property
    def tether(self) -> int:
        return residue_tether(self.level)


def across_paces(project: LandProject) -> float:
    return paces(project.across_miles)


def project_acres(project: LandProject) -> float:
    return acres(project.shape, across_paces(project))


def island_boundary(project: LandProject) -> int:
    """The magnitudes a Boundary spell over the whole island adds."""
    return boundary_magnitudes(land_area(project.shape, across_paces(project)))


def works(project: LandProject) -> list[Work]:
    """The project's Rituals, in the order they are cast: the wall, its
    slope, the fill, grassland, a forest, the Aegis and the Boundary
    spells."""
    across = across_paces(project)
    stuff = WALL_STUFF[project.wall_material]
    wall = wall_volume(
        project.shape, across, project.wall_height, project.wall_thickness
    )
    found = [
        Work(
            "The island's wall",
            "Creo",
            stuff.form,
            creation_level(stuff, wall, complexity(project)),
            f"{wall:,.0f} cubic paces of {stuff.name}",
        )
    ]
    if project.slope and project.shape != SOLID:
        found.append(
            Work(
                "The ablative slope",
                "Creo",
                "Terram",
                creation_level(EARTH, wall),
                f"{wall:,.0f} cubic paces of earth at the wall's foot",
            )
        )
    fill = fill_volume(project.shape, across, project.wall_height)
    if fill:
        stone = project.fill != SOIL
        extra = MIXED_STONE if stone and project.mixed_stone else 0
        found.append(
            Work(
                "The fill",
                "Creo",
                "Terram",
                creation_level(STONE_STUFF if stone else EARTH, fill, extra),
                f"{fill:,.0f} cubic paces of {'stone' if stone else 'soil'}",
            )
        )
    area = project_acres(project)
    if project.grassland:
        found.append(
            Work(
                "Verdant grassland",
                "Creo",
                "Herbam",
                grass_level(area),
                f"grass over {area:,.0f} acres",
            )
        )
    if project.forest_trees:
        found.append(
            Work(
                "A forest",
                "Creo",
                "Herbam",
                forest_level(project.forest_trees),
                f"{project.forest_trees:,} mature trees",
            )
        )
    extra = island_boundary(project)
    if project.aegis:
        found.append(
            Work(
                "Aegis of the Hearth",
                "Rego",
                "Vim",
                aegis_level(project.aegis, extra),
                f"level {project.aegis}, over the whole island",
            )
        )
    for name in project.boundary_spells:
        spell = SPELLS_BY_NAME.get(name)
        if spell is not None:
            found.append(
                Work(
                    spell.name,
                    spell.technique,
                    spell.form,
                    spell.level(extra),
                    f"{spell.what} (TME p. {spell.page})",
                )
            )
    return found


def find_project(saga: Saga, name: str) -> tuple[str, LandProject] | None:
    """The project of this name on any covenant: (its covenant's id, it)."""
    wanted = name.strip().lower()
    for covenant in saga.covenants:
        for project in covenant.land_projects:
            if project.name.strip().lower() == wanted:
                return covenant.id, project
    return None


def cast_count(saga: Saga, project: LandProject) -> int:
    """How many of its Rituals are cast: every magus's Progress records
    toward it, which a season of shaping the land keeps."""
    wanted = project.name.strip().lower()
    return sum(
        record.points
        for character in saga.characters
        for record in character.progress
        if record.kind == LAND_KIND and record.name.strip().lower() == wanted
    )


def remaining(saga: Saga, project: LandProject) -> list[Work]:
    return works(project)[cast_count(saga, project) :]


def land_made(saga: Saga, project: LandProject) -> bool:
    """Whether the island stands: its wall and fill (the first works) cast."""
    needed = sum(1 for w in works(project) if w.name in _LAND_WORKS)
    return cast_count(saga, project) >= needed


_LAND_WORKS = ("The island's wall", "The ablative slope", "The fill")


def manors_left(saga: Saga, project: LandProject) -> int:
    """Manors still to settle on the finished land (0 before it stands)."""
    if not land_made(saga, project):
        return 0
    made = manors_supported(project_acres(project), fertile=project.fertile)
    return max(0, made - project.manors_settled)


def tethers(project: LandProject) -> list[tuple[str, int]]:
    """The preternatural tethers its Rituals leave: (work, score)."""
    return [(w.name, w.tether) for w in works(project) if w.tether]
