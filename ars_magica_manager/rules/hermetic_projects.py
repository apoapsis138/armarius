"""Hermetic Projects: the Great Tower, and opening a tunnel in Wizard's
War.

The Great Tower (Hermetic Projects pp. 36-41; no errata on these pages):

- A level is 20 feet. A master mason with Craft: Mason 5 builds one level
  a season; an effective score of 10 two, 15 three (pp. 36-37). Craft
  devices add +1 each to that score for the rate alone, each kind of
  device counted once, the total at most his Craft: Mason (p. 39).
- The whole building operation is his workshop: Workshop Total =
  Intelligence + Craft: Mason + Innovation + Raw Materials, against the
  Craft Levels 3 shoddy, 6 standard, 12 superior, 15 excellent (p. 37).
  Owning De Architectura gives +1 Innovation, the Water Wheel +1; the
  workshop's Innovation never passes +3 (pp. 37, 41). City & Guild leaves
  the primary Characteristic to the troupe (p. 67), so Intelligence here
  does not conflict with its workshops.
- Damage levels (p. 38, after City & Guild p. 77): a base of 1, 2, 3 or 4
  by quality (shoddy, standard, superior, excellent), x4 for a tower of
  size 10 or more: 4, 8, 12 or 16. The lowest-quality work in the tower
  sets them. A ritual whose Finesse roll succeeds builds standard work, a
  failed one shoddy (p. 39). A season of the mason's rebuilding makes a
  shoddy section standard; a season of repair restores one damage level,
  and no other building goes on that season (p. 38).
- A stress check (p. 38; City & Guild p. 77): stress die + Craft: Mason,
  -1 if previously repaired, -1 shoddy, +1 superior, +3 excellent, +1 per
  Flying Buttress (at most his Craft: Mason, p. 41), and the
  storyguide's modifier for the event's severity, against 15. A failure
  loses one damage level; a botch one more for each botch die showing 0
  (City & Guild p. 77). Only severe storms, fire, earthquake or
  subsidence, and assault call for one.
- The rituals (pp. 39-40): Conjuring the Great Tower (CrTe 55) raises the
  foundations and two levels; Heights of the Great Tower (CrTe 50) four
  more. Each needs Int + Finesse + stress die against 12: success builds
  standard work, failure shoddy. Heights' botch dice are 1 + one for each
  earlier level built on a failed Finesse roll (a failed Conjuring leaves
  2 shoddy levels, a failed Heights 4), not one a failed casting,
  whoever cast it; each magnitude added for size multiplies the levels by
  ten and adds +3 to the Ease Factor and the botch dice.
  Each casting is a preternatural tether of 1 for the place (Conjuring
  the Great Tower makes a Magic aura of 1 where there was none), and
  Heights adds +1 to the year's aura modifier (Realms of Power: Magic
  pp. 8-11, rules.aura_change).

Tunnels (Hermetic Projects pp. 78-81; DE pp. 219, 372; errata p. 81):

- A tunnel lets the caster cast any spell of Touch range or more (more
  than Personal, DE p. 372) through it, up to a limit: Opening the
  Intangible Tunnel and The Minute of Reckoning their own level, The
  Cursèd Day a magnitude less, Wizard's Siege two less, The Evil Eye and
  The Master's Message a magnitude more.
- The tunnel must Penetrate the target's Magic Resistance (its Form is
  Vim), and so must each spell cast through it. A caster with an
  Arcane Connection to the target multiplies his Penetration by 1 + the
  connection + sympathetic connections for any spell (DE p. 219), so the
  spells cast through an Arcane Connection tunnel share the multiplier.
- Inside an Aegis of the Hearth, every incoming spell must also
  Penetrate the Aegis's level unless its caster took part in the Aegis or
  holds its token (p. 79).
- Break the Siege suppresses a tunnel of less than its own level + 2
  magnitudes (errata p. 81, correcting p. 81)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..models import Character, Covenant, Saga
from ..models.hermetic_projects import (
    BUTTRESS,
    CRAFT,
    EXCELLENT,
    INNOVATION,
    QUALITIES,
    REBUILD,
    REPAIR,
    RITUAL,
    SHODDY,
    STANDARD,
    STRESS,
    SUPERIOR,
    HermeticProject,
    ProjectWork,
)
from .scores import ability_level

SOURCE = "Hermetic Projects, The Great Tower, pp. 36-41"
TUNNEL_SOURCE = "Hermetic Projects, Wizard's War, pp. 78-81; DE pp. 219, 372"
HP = "Hermetic Projects"

MASON_CRAFT = "Craft: Mason"
FINESSE = "Finesse"
#: A level of the tower, in feet (p. 36).
LEVEL_FEET = 20
#: An effective Craft: Mason of this much builds a level a season (p. 36).
LEVEL_PER_SCORE = 5
#: Damage levels: the base by quality, and the multiplier for size 10+.
BASE_DAMAGE: dict[str, int] = {SHODDY: 1, STANDARD: 2, SUPERIOR: 3, EXCELLENT: 4}
SIZE_MULTIPLIER = 4
#: The stress check (p. 38): its Ease Factor and the quality's modifier.
STRESS_EASE = 15
STRESS_MODIFIER: dict[str, int] = {SHODDY: -1, STANDARD: 0, SUPERIOR: 1, EXCELLENT: 3}
REPAIRED_MODIFIER = -1
#: What calls for a stress check (p. 38).
STRESS_EVENTS: tuple[str, ...] = (
    "Severe storm or hurricane winds",
    "Fire inside or outside the tower",
    "Earthquake or subsidence",
    "Magical or mundane assault",
)
#: The Craft Levels a Workshop Total is held against (p. 37), best first.
CRAFT_LEVELS: tuple[tuple[int, str], ...] = (
    (15, EXCELLENT),
    (12, SUPERIOR),
    (6, STANDARD),
    (3, SHODDY),
)
#: The workshop's Innovation and Raw Materials go no higher (p. 37, 41).
WORKSHOP_CAP = 3
DE_ARCHITECTURA = "De Architectura"

#: The rituals that conjure the tower (pp. 39-40).
FINESSE_EASE = 12
#: A magnitude more for size: x10 levels, +3 Ease Factor and botch dice.
MAGNITUDE_EASE = 3
MAGNITUDE_LEVELS = 10


@dataclass(frozen=True)
class Ritual:
    """One way of conjuring the tower: its name, level, the levels it
    adds, the magnitudes of size beyond the printed ritual, and whether it
    raises the foundations (Conjuring the Great Tower)."""

    key: str
    name: str
    level: int
    levels: int
    extra: int = 0
    foundations: bool = False

    @property
    def ease(self) -> int:
        return FINESSE_EASE + MAGNITUDE_EASE * self.extra

    @property
    def label(self) -> str:
        return f"{self.name} (CrTe {self.level}): {self.levels} levels"


RITUALS: tuple[Ritual, ...] = (
    Ritual("conjuring", "Conjuring the Great Tower", 55, 2, foundations=True),
    Ritual("heights", "Heights of the Great Tower", 50, 4),
    Ritual("heights_55", "Heights of the Great Tower, a magnitude larger", 55, 40, 1),
    Ritual(
        "heights_60", "Heights of the Great Tower, two magnitudes larger", 60, 400, 2
    ),
)
RITUAL_BY_KEY: dict[str, Ritual] = {r.key: r for r in RITUALS}


# -- the tower ----------------------------------------------------------------


def mason(saga: Saga, project: HermeticProject) -> Character | None:
    return saga.character(project.mason_id) if project.mason_id else None


def height_levels(project: HermeticProject) -> int:
    return sum(work.levels for work in project.works)


def feet(levels: int) -> int:
    return levels * LEVEL_FEET


def _rebuilt(project: HermeticProject) -> set[str]:
    return {w.rebuilt for w in project.works if w.kind == REBUILD and w.rebuilt}


def section_quality(project: HermeticProject, work: ProjectWork) -> str:
    """The quality a work's section stands at now: standard once a later
    season has rebuilt it, if it was shoddy (p. 38)."""
    if work.quality == SHODDY and work.id in _rebuilt(project):
        return STANDARD
    return work.quality


def sections(project: HermeticProject) -> list[ProjectWork]:
    """The works that built part of the tower, with a quality."""
    return [w for w in project.works if w.levels > 0 and w.quality in QUALITIES]


def weakest(project: HermeticProject) -> ProjectWork | None:
    """The section of the lowest quality (the earliest of equals): it sets
    the tower's damage levels and its stress checks (p. 38)."""
    built = sections(project)
    if not built:
        return None
    return min(built, key=lambda w: QUALITIES.index(section_quality(project, w)))


def quality(project: HermeticProject) -> str:
    """The tower's quality: its weakest section's; "" with nothing built."""
    found = weakest(project)
    return section_quality(project, found) if found is not None else ""


def damage_levels(project: HermeticProject) -> int:
    """How many damage levels the tower has when whole: its quality's base
    x4 (p. 38); 0 with nothing built."""
    shown = quality(project)
    return BASE_DAMAGE[shown] * SIZE_MULTIPLIER if shown else 0


def damage_lost(project: HermeticProject) -> int:
    """Damage levels lost to stress checks and not yet repaired."""
    lost = sum(w.damage for w in project.works if w.kind == STRESS)
    repaired = sum(w.seasons for w in project.works if w.kind == REPAIR)
    return max(0, lost - repaired)


def damage_left(project: HermeticProject) -> int:
    return max(0, damage_levels(project) - damage_lost(project))


def previously_repaired(project: HermeticProject) -> bool:
    """Whether the tower has been repaired or rebuilt (-1 to stress
    checks, City & Guild p. 77)."""
    return any(w.kind in (REPAIR, REBUILD) for w in project.works)


def tethers(project: HermeticProject) -> int:
    """The preternatural tethers its rituals have made: 1 a casting."""
    return sum(1 for w in project.works if w.kind == RITUAL)


def failed_finesse(project: HermeticProject, before: ProjectWork | None = None) -> int:
    """The levels built by rituals whose Finesse roll failed (their work
    shoddy), each a botch die more on a later Heights (p. 40): a failed
    Conjuring leaves 2, a failed Heights 4. Only those before `before`
    when it is given."""
    works = project.works
    if before is not None and before in works:
        works = works[: works.index(before)]
    return sum(w.levels for w in works if w.kind == RITUAL and w.quality == SHODDY)


def ritual_botch_dice(ritual: Ritual, failed: int) -> int:
    """A ritual's botch dice: 1, + one per earlier level built on a failed
    Finesse roll and +3 for each magnitude of size for Heights (p. 40)."""
    if ritual.foundations:
        return 1
    return 1 + failed + MAGNITUDE_EASE * ritual.extra


def finesse_score(caster: Character) -> int:
    return caster.characteristics.intelligence + ability_level(caster, FINESSE)


@dataclass(frozen=True)
class Mason:
    """What the master mason brings: his Intelligence and Craft: Mason,
    the craft devices' bonus (at most his score), the effective score and
    the levels a season it builds; the Workshop Total and the quality."""

    name: str
    intelligence: int
    craft: int
    devices: int
    innovation: int
    raw_materials: int

    @property
    def effective(self) -> int:
        return self.craft + min(self.devices, self.craft)

    @property
    def levels_a_season(self) -> int:
        return levels_a_season(self.effective)

    @property
    def workshop_total(self) -> int:
        return self.intelligence + self.craft + self.innovation + self.raw_materials

    @property
    def quality(self) -> str:
        return workshop_quality(self.workshop_total)


def levels_a_season(effective: int) -> int:
    """The levels an effective Craft: Mason builds in a season (p. 37)."""
    return effective // LEVEL_PER_SCORE


def workshop_quality(total: int) -> str:
    """The quality a Workshop Total reaches (p. 37); "" below 3."""
    return next((label for level, label in CRAFT_LEVELS if total >= level), "")


def craft_devices(project: HermeticProject) -> int:
    """The craft devices' bonus to the rate: +1 for each kind (by name),
    before his Craft: Mason caps it (p. 39)."""
    return len(
        {d.name.strip().casefold() or d.id for d in project.devices if d.kind == CRAFT}
    )


def buttresses(project: HermeticProject) -> int:
    return sum(d.count for d in project.devices if d.kind == BUTTRESS)


def owns_de_architectura(
    saga: Saga, project: HermeticProject, covenant_id: str
) -> bool:
    """Whether the covenant or its mason owns a copy of De Architectura."""
    owners = {("covenant", covenant_id)}
    if project.mason_id:
        owners.add(("character", project.mason_id))
    return any(
        DE_ARCHITECTURA.casefold() in book.name.casefold()
        and (book.owner_kind, book.owner_id) in owners
        for book in saga.books
    )


def innovation(saga: Saga, project: HermeticProject, covenant_id: str) -> int:
    """The workshop's Innovation: its own, +1 for De Architectura, +1 for
    the Water Wheel; never above +3 (pp. 37, 41)."""
    total = project.innovation
    total += owns_de_architectura(saga, project, covenant_id)
    total += any(d.kind == INNOVATION for d in project.devices)
    return min(WORKSHOP_CAP, total)


def mason_of(saga: Saga, project: HermeticProject, covenant_id: str) -> Mason | None:
    who = mason(saga, project)
    if who is None:
        return None
    return Mason(
        name=who.name,
        intelligence=who.characteristics.intelligence,
        craft=ability_level(who, MASON_CRAFT),
        devices=craft_devices(project),
        innovation=innovation(saga, project, covenant_id),
        raw_materials=min(WORKSHOP_CAP, project.raw_materials),
    )


@dataclass(frozen=True)
class StressCheck:
    """A stress check's modifiers: the total before the die and its terms."""

    total: int
    parts: tuple[str, ...]

    @property
    def needed(self) -> int:
        """The die it needs to reach 15."""
        return STRESS_EASE - self.total


def stress_check(
    saga: Saga,
    project: HermeticProject,
    *,
    severity: int = 0,
    repaired: bool | None = None,
    buttress_count: int | None = None,
) -> StressCheck:
    """The modifiers to the tower's stress check (p. 38)."""
    who = mason(saga, project)
    craft = ability_level(who, MASON_CRAFT) if who is not None else 0
    parts: list[str] = []
    total = 0
    if who is not None:
        total += craft
        parts.append(f"{MASON_CRAFT} {craft}")
    shown = quality(project)
    if shown and STRESS_MODIFIER[shown]:
        total += STRESS_MODIFIER[shown]
        parts.append(f"{shown.lower()} {STRESS_MODIFIER[shown]:+d}")
    if previously_repaired(project) if repaired is None else repaired:
        total += REPAIRED_MODIFIER
        parts.append(f"repaired {REPAIRED_MODIFIER:+d}")
    count = buttresses(project) if buttress_count is None else buttress_count
    count = min(count, craft)
    if count:
        total += count
        parts.append(f"Flying Buttresses +{count}")
    if severity:
        total += severity
        parts.append(f"severity {severity:+d}")
    return StressCheck(total, tuple(parts))


def stress_damage(succeeded: bool, botches: int) -> int:
    """Damage levels a stress check takes: none on a success, one on a
    failure, one more for each botch (City & Guild p. 77)."""
    if botches:
        return 1 + botches
    return 0 if succeeded else 1


def season_work(project: HermeticProject, work: str) -> str:
    """What stops a mason's season of `work` ("" when nothing does)."""
    if work == REPAIR and not damage_lost(project):
        return "The tower has lost no damage levels: there is nothing to repair."
    if work == REBUILD and not shoddy_sections(project):
        return "No section of the tower is shoddy: there is nothing to rebuild."
    return ""


def shoddy_sections(project: HermeticProject) -> list[ProjectWork]:
    """The sections still shoddy, earliest first: a rebuild takes the first."""
    return [w for w in sections(project) if section_quality(project, w) == SHODDY]


def stands(project: HermeticProject) -> bool:
    """Whether the tower is built at all."""
    return height_levels(project) > 0


def shown_project(covenant: Covenant) -> HermeticProject | None:
    """The project the Projects tab shows: the one chosen, else the first."""
    listed = covenant.hermetic_projects
    return next((p for p in listed if p.id == covenant.project_shown), None) or (
        listed[0] if listed else None
    )


def projects_of_mason(saga: Saga, character: Character) -> list[HermeticProject]:
    """The projects whose master mason `character` is, in the saga."""
    return [
        p
        for covenant in saga.covenants
        for p in covenant.hermetic_projects
        if p.mason_id == character.id
    ]


def covenant_of(saga: Saga, project: HermeticProject) -> Covenant | None:
    return next((c for c in saga.covenants if project in c.hermetic_projects), None)


def find_project(saga: Saga, project_id: str) -> HermeticProject | None:
    return next(
        (
            p
            for covenant in saga.covenants
            for p in covenant.hermetic_projects
            if p.id == project_id
        ),
        None,
    )


def add_works(saga: Saga, works: Sequence[tuple[str, ProjectWork]]) -> None:
    """Keep a season's works (a mason's), each (project id, work), in its
    project's works."""
    for project_id, work in works:
        project = find_project(saga, project_id)
        if project is not None:
            project.works.append(work)


# -- tunnels ------------------------------------------------------------------


@dataclass(frozen=True)
class Tunnel:
    """A tunnel spell (HP pp. 80-81; DE p. 372): its catalog id, and what
    the spells cast through it may reach beside its own level."""

    spell_id: str
    name: str
    offset: int
    arcane: bool = True


TUNNELS: tuple[Tunnel, ...] = (
    Tunnel("spell_opening_the_intangible_tunnel", "Opening the Intangible Tunnel", 0),
    Tunnel("spell_the_minute_of_reckoning", "The Minute of Reckoning", 0),
    Tunnel("spell_the_curs_d_day", "The Cursèd Day", -5),
    Tunnel("spell_wizard_s_siege", "Wizard's Siege", -10),
    Tunnel("spell_the_evil_eye", "The Evil Eye", 5, arcane=False),
    Tunnel("spell_the_master_s_message", "The Master's Message", 5, arcane=False),
)
TUNNEL_BY_ID: dict[str, Tunnel] = {t.spell_id: t for t in TUNNELS}
#: Spells of these ranges can't be cast through a tunnel (DE p. 372).
NOT_THROUGH = ("Personal",)
#: Break the Siege reaches tunnels below its level + this (errata p. 81).
BREAK_THE_SIEGE_REACH = 10


def tunnel_limit(tunnel: Tunnel, level: int) -> int:
    """The highest level a spell cast through it may be."""
    return max(0, level + tunnel.offset)


def break_the_siege_reaches(level: int, tunnel_level: int) -> bool:
    """Whether Break the Siege of `level` suppresses a tunnel of
    `tunnel_level` (errata p. 81: less than its level + 2 magnitudes)."""
    return tunnel_level < level + BREAK_THE_SIEGE_REACH


def penetrates(penetration: int, resistance: int, aegis: int | None) -> bool:
    """Whether a spell through the tunnel affects the target: above his
    Magic Resistance, and above the Aegis he shelters in (p. 79)."""
    return penetration > resistance and (aegis is None or penetration > aegis)


def through(levels: Sequence[tuple[str, int | None, str]], limit: int) -> list[int]:
    """The indexes of the spells (name, level, range) that may be cast
    through a tunnel reaching `limit`: Touch range or more, of a set level
    no higher than the limit."""
    return [
        i
        for i, (_, level, reach) in enumerate(levels)
        if level is not None and level <= limit and reach not in NOT_THROUGH
    ]
