"""Hermetic Projects' season: a master mason's season on a Great Tower
(Hermetic Projects pp. 36-38).

- Building: his effective Craft: Mason (with the craft devices' bonus, at
  most his score) builds a level a season for each 5; the Workshop Total
  (Intelligence + Craft: Mason + Innovation + Raw Materials) sets the
  quality of what he builds (3 shoddy, 6 standard, 12 superior, 15
  excellent; below 3, nothing worth building).
- Repair: a season restores one damage level, and no other building goes
  on that season (p. 38).
- Rebuilding: a season of repairs and restructuring makes a shoddy section
  standard (p. 38).

The work is kept in the project's works when the season is played, as
the mason's own project (the first he is master mason of). Like a
workshop's season, it gives Exposure in the Craft."""

from __future__ import annotations

import random

from ...models import Character, Saga, SeasonPlan
from ...models.hermetic_projects import (
    BUILDING,
    REBUILD,
    REPAIR,
    HermeticProject,
    ProjectWork,
)
from .. import activity_groups as groups
from .. import hermetic_projects as hp
from .base import COMPANIONS, SimpleActivity, SupplementWork, register, source

HERMETIC_PROJECTS = source("Hermetic Projects, The Great Tower, pp. 36-38", "HP")
BUILD_TOWER = "build_great_tower"
#: The season's work, by the plan's title.
TOWER_WORKS: dict[str, str] = {
    BUILDING: "Build new levels",
    REPAIR: "Repair a damage level",
    REBUILD: "Rebuild a shoddy section as standard",
}


def work_of(plan: SeasonPlan) -> str:
    """The season's work (BUILDING, REPAIR or REBUILD): the plan's title."""
    return plan.title if plan.title in TOWER_WORKS else BUILDING


def _project(saga: Saga, character: Character) -> HermeticProject | None:
    found = hp.projects_of_mason(saga, character)
    return found[0] if found else None


def _problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    project = _project(saga, character)
    if project is None:
        return [
            f"{character.name} is master mason of no Hermetic Project: name him "
            "on the covenant's Projects tab."
        ]
    why = hp.season_work(project, work_of(plan))
    return [why] if why else []


def _outcome(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    project = _project(saga, character)
    if project is None:
        return
    covenant = hp.covenant_of(saga, project)
    mason = hp.mason_of(saga, project, covenant.id if covenant is not None else "")
    if mason is None:
        return
    work = work_of(plan)
    made = ProjectWork(
        kind=work,
        name=f"{character.name} {TOWER_WORKS[work].lower()}",
        season=plan.season,
        year=plan.year,
        who=character.id,
    )
    if work == REPAIR:
        made.details = "A season's repair: one damage level restored."
        result.notes.append(
            f"{project.name}: one damage level repaired; no other building this "
            "season (Hermetic Projects p. 38)."
        )
    elif work == REBUILD:
        section = hp.shoddy_sections(project)
        if not section:
            return
        made.rebuilt = section[0].id
        made.details = (
            f"The shoddy section of {section[0].season} {section[0].year} made "
            "standard."
        )
        result.notes.append(
            f"{project.name}: {made.details} (Hermetic Projects p. 38)."
        )
    else:
        quality = mason.quality
        levels = mason.levels_a_season if quality else 0
        made.levels, made.quality = levels, quality
        made.details = (
            f"Effective {hp.MASON_CRAFT} {mason.effective}: {levels} "
            f"level{'s' if levels != 1 else ''}. Workshop Total "
            f"{mason.workshop_total}: {quality.lower() or 'nothing worth building'}."
        )
        result.notes.append(
            f"{project.name}: +{levels} level{'s' if levels != 1 else ''} "
            f"({hp.feet(levels)} ft) of "
            f"{quality.lower() or 'no'} work (Hermetic Projects pp. 36-37)."
        )
    result.project_works.append((project.id, made))


register(
    SimpleActivity(
        BUILD_TOWER,
        "Build the Great Tower",
        "A master mason's season on a Great Tower: new levels (one a season "
        "for each 5 of his effective Craft: Mason), a damage level repaired, "
        "or a shoddy section rebuilt as standard. Exposure 2.",
        HERMETIC_PROJECTS,
        "932",
        who=COMPANIONS,
        group=groups.WORK,
    ),
    _outcome,
    _problems,
)
