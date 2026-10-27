"""A staged Hermetic Project on a covenant's Projects tab (a chapter on
the desktop): a Burning City, an Intangible Assassin or a Living Corpse.
The project's facts and its chapter's rules, its stages (each with the
works and lab seasons spent on it) and those works; with More's Warning
Bell (a Burning City), Gather a Connection and Lower an Aegis (an
Intangible Assassin) and Death Roll (a Living Corpse). The rules are
rules.staged_projects' (Hermetic Projects pp. 9-118); a volcano's
hazards are Take Harm's (rules.harm).

Pattern: the third set of kinds in the Projects tab's registry (a
Strategy, as hermetic_projects.KIND_TEXT keeps it): the shown project's
kind picks the tab's sections, a block and two lists of neighbour_lists'
KindTab pieces that each front-end already draws. A lab season spent on a
stage is the season registry's own lab work (Strategy), its plan naming
the stage."""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any

from .commands import Command, Confirm, Form, Refuse, SectionOps, notes
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import escape
from .models import (
    SEASONS,
    ArcaneConnection,
    Character,
    Covenant,
    DiaryEntry,
    Neighbour,
    Saga,
)
from .models.covenant import CovenantDiaryEntry
from .models.hermetic_projects import (
    BURNING_CITY,
    INTANGIBLE_ASSASSIN,
    LIVING_CORPSE,
    OTHER,
    STAGED_KINDS,
    HermeticProject,
    ProjectStage,
    ProjectWork,
)
from .models.traits import new_instance_id
from .neighbour_lists import KindBlock, KindList
from .references import Fact
from .rules import derived, dice, realms
from .rules import hermetic_projects as hp
from .rules import staged_projects as sp
from .rules.scores import ability_level
from .sections import STAGE_WORKS_SECTION, STAGED_SECTION, STAGED_STAGES_SECTION

HP = sp.HP
PANEL = "[dim]Choose a project, a stage or a work.[/]"
WARNING_BELL = "Warning Bell"
GATHER = "Gather a Connection"
LOWER_AEGIS = "Lower an Aegis"
DEATH_ROLL = "Death Roll"
GENTLE_GIFT, BLATANT_GIFT, THE_GIFT = (
    "vf_gentle_gift",
    "vf_blatant_gift",
    "vf_the_gift",
)
OPTION_ONE, OPTION_TWO = "chart", "contest"
LORES = ("Dominion Lore", "Infernal Lore", "Faerie Lore")


def covenant_of(saga: Saga, holder: Neighbour) -> Covenant | None:
    return saga.covenant(holder.id)


def shown(saga: Saga, holder: Neighbour) -> HermeticProject | None:
    """The staged project the tab shows (None for a tower or a menagerie,
    or with none)."""
    covenant = covenant_of(saga, holder)
    project = hp.shown_project(covenant) if covenant is not None else None
    return project if project is not None and project.kind in STAGED_KINDS else None


def _name(saga: Saga, character_id: str) -> str:
    found = saga.character(character_id) if character_id else None
    return found.name if found is not None else ""


def _plural(count: int, word: str) -> str:
    return f"{count} {word}{'' if count == 1 else 's'}"


def seed(kind: str) -> list[ProjectStage]:
    """A new staged project's stages: its chapter's, in order."""
    return [ProjectStage(name=name) for name in sp.stage_names(kind)]


def stage_works(project: HermeticProject, stage: ProjectStage) -> list[ProjectWork]:
    return [w for w in project.works if w.stage == stage.id]


def _seasons(works: list[ProjectWork]) -> int:
    return sum(w.seasons for w in works)


def current_stage(project: HermeticProject) -> ProjectStage | None:
    """The first stage not yet done."""
    return next((s for s in project.stages if not s.done), None)


def progress(project: HermeticProject) -> str:
    done = sum(1 for s in project.stages if s.done)
    return f"{done} of {len(project.stages)}"


def note(project: HermeticProject) -> str:
    stage = current_stage(project)
    if not project.stages:
        return ""
    return f"now: {stage.name}" if stage is not None else "all stages done"


# -- the block -----------------------------------------------------------------

#: Each kind's rules, as the block shows them (with their pages).
RULES_TEXT: dict[str, tuple[str, ...]] = {
    BURNING_CITY: (
        "A volcano's hazards are Take Harm's (a character's Health, More): lava "
        "+15 a round, x2 a limb, x3 half the body, x4 immersed, armour no help "
        "once it covers half; boiling mud +3; within 30 yards of lava +3 heat a "
        "Diameter; within 15 paces of a crater the fumes, an air Deprivation "
        "check every 30 seconds and a Stamina check against 6 each Diameter or a "
        "Medium Wound; falling rocks +5 to +20 (HP pp. 13-14).",
        "Its laboratories' Virtues, Flaws and Features (Volcanic Minerals, "
        "Dormant and Active Volcano, Mineral Bath, Volcanic Spirit Forge, Hell "
        "Portal; Fumes, Pool of Lava, Thermal Spring, Volcanic Rock) are in the "
        "lab's lists (HP pp. 19, 26-27).",
        "More's Warning Bell rolls Vulcan's Warning Bell: a stress die of days' "
        "warning, a 0 the botch die's hours, a botch none (HP pp. 16-17).",
    ),
    INTANGIBLE_ASSASSIN: (
        "Its tunnels are Open a Tunnel's (a magus's Known Spells, More): what "
        "each lets through, the Penetration it shares, and an Aegis on either "
        "end (HP pp. 78-81).",
        "More's Gather a Connection keeps an Arcane Connection to the quarry in "
        "a laboratory: his blood or the weapon that drew it last years, a text "
        "he wrote lately weeks, his breath hours (HP pp. 86-91).",
        "More's Lower an Aegis works out Guttering of the Home-Fires (an Aegis "
        "under half its level + 15) and Removing the Hearth's Keystone (under "
        "its level + 15 + a stress die); each must Penetrate the Aegis (HP pp. "
        "94-95).",
    ),
    LIVING_CORPSE: (
        "More's Death Roll is a magus's death: the ghost his spirit becomes (the "
        "chart, or the contest of his Magic Lore against his Personality "
        "Traits), its Might, Season and experience, its vis and its one "
        "Personality Trait (HP pp. 107-111).",
        "A corpse animated after death loses its Mental Characteristics, and 1 "
        "from each Physical one a day to -5, which lasts a year (HP p. 108).",
        "A living corpse doesn't age, Warp or fall into Final Twilight, can't be "
        "Incapacitated, and does no lab work; destroying its vessel or its "
        "device ends it (HP pp. 114-115).",
    ),
}


def staged_title(saga: Saga, covenant: Covenant | None) -> str:
    project = hp.shown_project(covenant) if covenant is not None else None
    if project is None:
        return "The Project"
    return f"{project.name or '(unnamed)'}: {project.kind}"


def staged_facts(saga: Saga, holder: Neighbour) -> list[Fact]:
    project = shown(saga, holder)
    if project is None:
        return []
    stage = current_stage(project)
    place = saga.neighbour(project.place_id) if project.place_id else None
    return [
        Fact("What", sp.KIND_LINES.get(project.kind, "")),
        Fact("Begun", f"{project.season} {project.year}"),
        Fact("Stages done", progress(project)),
        Fact(
            "Now",
            f"{stage.name} ({HP} {sp.stage_pages(project.kind, stage.name)})"
            if stage is not None
            else "every stage done",
        ),
        Fact("Seasons spent", str(_seasons(project.works))),
        Fact("Place", place.name if place is not None else ""),
    ]


def rules_text(project: HermeticProject) -> str:
    return "\n".join(f"[dim]{escape(line)}[/]" for line in RULES_TEXT[project.kind])


def block_text(saga: Saga, holder: Neighbour) -> str:
    project = shown(saga, holder)
    if project is None:
        return "[$label]No staged project shown.[/]"
    return rules_text(project)


def project_text(saga: Saga, project: HermeticProject) -> str:
    """A staged project in the projects list's inspector."""
    stage = current_stage(project)
    lines = [
        f"{progress(project)} stages done; "
        + (f"now {escape(stage.name)}." if stage else "every stage done.")
    ]
    return "\n".join(lines)


# -- stages --------------------------------------------------------------------


def stages_title(saga: Saga, holder: Neighbour) -> str:
    project = shown(saga, holder)
    return f"Stages ({len(project.stages)})" if project is not None else "Stages"


def stages_grid(saga: Saga, holder: Neighbour) -> Grid:
    project = shown(saga, holder)
    stages = project.stages if project is not None else []
    rows: list[list[str]] = []
    styles: dict[tuple[int, int], str] = {}
    for i, stage in enumerate(stages):
        works = stage_works(project, stage) if project is not None else []
        rows.append(
            [
                stage.name or "(unnamed)",
                sp.stage_pages(project.kind, stage.name) if project else "",
                str(len(works)),
                str(_seasons(works)),
                "Done" if stage.done else "",
            ]
        )
        if stage.done:
            styles[(i, 4)] = "$text-success"
    return Grid(
        ["Stage", "Pages", "Works", "Seasons", "Done"],
        rows,
        list(range(len(stages))),
        "No stages: Add one.",
        styles=styles,
        caps=[30, 10, 5, 7],
    )


def stage_info(saga: Saga, holder: Neighbour, index: int) -> str:
    project = shown(saga, holder)
    if project is None or index >= len(project.stages):
        return ""
    stage = project.stages[index]
    pages = sp.stage_pages(project.kind, stage.name)
    lines = [
        f"[b]{escape(stage.name)}[/]"
        + (f" ({HP} {pages})" if pages else "")
        + (": done." if stage.done else ".")
    ]
    for work in stage_works(project, stage):
        who = _name(saga, work.who)
        lines.append(
            f"  {work.season} {work.year}: {escape(work.name or '(unnamed)')}"
            + (f", {escape(who)}" if who else "")
            + (f", {_plural(work.seasons, 'season')}" if work.seasons else "")
        )
    if stage.note.strip():
        lines.append(escape(stage.note.strip()))
    return "\n".join(lines)


def stage_fields(stage: ProjectStage | None) -> list[DialogField]:
    return [
        DialogField(
            "name", "Stage", "text", stage.name if stage else "", required=True
        ),
        DialogField("done", "Done", "check", bool(stage and stage.done)),
        DialogField("note", "Note", "area", stage.note if stage else ""),
    ]


def _write_stage(stage: ProjectStage, values: dict[str, Any]) -> None:
    stage.name = values["name"]
    stage.done = bool(values.get("done"))
    stage.note = values.get("note") or ""


def stage_form(project: HermeticProject, stage: ProjectStage | None) -> Form:
    def apply(values: dict[str, Any]) -> None:
        if stage is not None:
            _write_stage(stage, values)
            return
        made = ProjectStage()
        _write_stage(made, values)
        project.stages.append(made)

    return Form(
        "Edit Stage" if stage is not None else "Add Stage",
        lambda: stage_fields(stage),
        apply,
        help_id=STAGED_STAGES_SECTION,
    )


def stages_ops(saga: Saga, holder: Neighbour) -> SectionOps:
    def project() -> HermeticProject | None:
        return shown(saga, holder)

    def add() -> Command:
        found = project()
        if found is None:
            return Refuse("Add Stage", "Show a staged project first.")
        return stage_form(found, None)

    def edit(index: int) -> Command:
        found = project()
        if found is None or index >= len(found.stages):
            return Refuse("Edit Stage", "Choose a stage first.")
        return stage_form(found, found.stages[index])

    def remove(index: int) -> Command:
        found = project()
        if found is None or index >= len(found.stages):
            return Refuse("Delete", "Choose a stage first.")
        stage = found.stages[index]

        def apply() -> None:
            found.stages.remove(stage)
            for work in found.works:
                if work.stage == stage.id:
                    work.stage = ""

        return Confirm(f"Delete {escape(stage.name or 'this stage')}?", apply)

    def rows() -> list[str]:
        found = project()
        return [s.name or "(unnamed)" for s in found.stages] if found else []

    return SectionOps(add=add, edit=edit, remove=remove, rows=rows)


# -- works ---------------------------------------------------------------------


def _stage_name(project: HermeticProject, stage_id: str) -> str:
    return next((s.name for s in project.stages if s.id == stage_id), "")


def works_title(saga: Saga, holder: Neighbour) -> str:
    project = shown(saga, holder)
    return f"Works ({len(project.works)})" if project is not None else "Works"


def works_grid(saga: Saga, holder: Neighbour) -> Grid:
    project = shown(saga, holder)
    works = project.works if project is not None else []
    rows = [
        [
            w.name or "(unnamed)",
            _stage_name(project, w.stage) if project is not None else "",
            f"{w.season} {w.year}",
            _name(saga, w.who),
            str(w.seasons),
        ]
        for w in works
    ]
    return Grid(
        ["Work", "Stage", "When", "Who", "Seasons"],
        rows,
        list(range(len(works))),
        "No works yet: a lab season spent on a stage adds one, or Add one.",
        caps=[28, 22, 11, 16],
    )


def work_info(saga: Saga, holder: Neighbour, index: int) -> str:
    project = shown(saga, holder)
    if project is None or index >= len(project.works):
        return ""
    work = project.works[index]
    stage = _stage_name(project, work.stage)
    who = _name(saga, work.who)
    lines = [
        f"[b]{escape(work.name or '(unnamed)')}[/], {work.season} {work.year}"
        + (f", on {escape(stage)}" if stage else "")
        + (f", by {escape(who)}" if who else "")
        + f": {_plural(work.seasons, 'season')}.",
    ]
    if work.details.strip():
        lines.append(escape(work.details.strip()))
    if work.note.strip():
        lines.append(escape(work.note.strip()))
    return "\n".join(lines)


def _people(saga: Saga, covenant: Covenant) -> list[tuple[str, str]]:
    return [
        (escape(f"{c.name} ({c.type})"), c.id)
        for c in sorted(saga.characters, key=lambda c: c.name.casefold())
        if c.covenant_id == covenant.id
    ]


def work_fields(
    saga: Saga, covenant: Covenant, project: HermeticProject, work: ProjectWork | None
) -> list[DialogField]:
    stage = current_stage(project)
    return [
        DialogField("name", "Work", "text", work.name if work else "", required=True),
        DialogField(
            "stage",
            "Stage",
            "select",
            (work.stage if work else (stage.id if stage else "")) or None,
            options=[(escape(s.name), s.id) for s in project.stages],
            allow_blank=True,
            placeholder="(none)",
        ),
        DialogField(
            "season",
            "Season",
            "select",
            work.season if work else saga.current_season,
            options=pairs(SEASONS),
        ),
        DialogField("year", "Year", "int", work.year if work else saga.current_year),
        DialogField(
            "seasons",
            "Seasons spent",
            "int",
            work.seasons if work else 1,
            hint="0 for a work that took no season (a story's).",
        ),
        DialogField(
            "who",
            "Who",
            "select",
            (work.who if work else "") or None,
            options=_people(saga, covenant),
            allow_blank=True,
            placeholder="(none)",
        ),
        DialogField("note", "Note", "area", work.note if work else ""),
    ]


def validate_work(values: dict[str, Any]) -> str | None:
    if (values.get("seasons") or 0) < 0:
        return "Seasons spent can't be below 0."
    return None


def _write_work(work: ProjectWork, values: dict[str, Any]) -> None:
    work.kind = OTHER
    work.name = values["name"]
    work.stage = values.get("stage") or ""
    work.season = values.get("season") or "Spring"
    work.year = values["year"]
    work.seasons = max(0, values.get("seasons") or 0)
    work.who = values.get("who") or ""
    work.note = values.get("note") or ""


def work_form(
    saga: Saga, covenant: Covenant, project: HermeticProject, work: ProjectWork | None
) -> Form:
    def apply(values: dict[str, Any]) -> None:
        if work is not None:
            _write_work(work, values)
            return
        made = ProjectWork()
        _write_work(made, values)
        project.works.append(made)

    return Form(
        "Edit Work" if work is not None else "Add Work",
        lambda: work_fields(saga, covenant, project, work),
        apply,
        validate=validate_work,
        help_id=STAGE_WORKS_SECTION,
    )


def works_ops(saga: Saga, holder: Neighbour) -> SectionOps:
    covenant = covenant_of(saga, holder)

    def project() -> HermeticProject | None:
        return shown(saga, holder)

    def add() -> Command:
        found = project()
        if found is None or covenant is None:
            return Refuse("Add Work", "Show a staged project first.")
        return work_form(saga, covenant, found, None)

    def edit(index: int) -> Command:
        found = project()
        if found is None or covenant is None or index >= len(found.works):
            return Refuse("Edit Work", "Choose a work first.")
        return work_form(saga, covenant, found, found.works[index])

    def remove(index: int) -> Command:
        found = project()
        if found is None or index >= len(found.works):
            return Refuse("Delete", "Choose a work first.")
        work = found.works[index]
        return Confirm(
            f"Delete {escape(work.name or 'this work')}?",
            lambda: found.works.remove(work),
        )

    def rows() -> list[str]:
        found = project()
        return [w.name or "(unnamed)" for w in found.works] if found else []

    return SectionOps(add=add, edit=edit, remove=remove, rows=rows)


# -- lab seasons spent on a stage ----------------------------------------------


def stage_options(saga: Saga, character: Character) -> list[tuple[str, str]]:
    """The stages of his covenant's staged projects a lab season may be
    spent on, as "Project: Stage"."""
    covenant = saga.covenant(character.covenant_id) if character.covenant_id else None
    if covenant is None:
        return []
    return [
        (escape(f"{p.name or p.kind}: {s.name}"), s.id)
        for p in covenant.hermetic_projects
        if p.kind in STAGED_KINDS
        for s in p.stages
    ]


def find_stage(
    saga: Saga, stage_id: str
) -> tuple[HermeticProject, ProjectStage] | None:
    for covenant in saga.covenants:
        for project in covenant.hermetic_projects:
            for stage in project.stages:
                if stage.id == stage_id:
                    return project, stage
    return None


def spend_season(
    saga: Saga,
    character: Character,
    stage_id: str,
    name: str,
    season: str,
    year: int,
) -> str:
    """A lab season spent on a stage: a work in its project's works;
    the note for the season's record ("" when the stage is gone)."""
    found = find_stage(saga, stage_id)
    if found is None:
        return ""
    project, stage = found
    project.works.append(
        ProjectWork(
            kind=OTHER,
            name=name,
            season=season,
            year=year,
            who=character.id,
            stage=stage.id,
            details="A season of lab work.",
        )
    )
    return f"{project.name or project.kind}: a season on {stage.name}."


# -- More: Warning Bell (a Burning City) ---------------------------------------


def _staged(covenant: Covenant, kind: str, title: str) -> HermeticProject | Refuse:
    project = hp.shown_project(covenant)
    if project is None or project.kind != kind:
        return Refuse(title, f"Show a {kind} first.")
    return project


def bell_form(
    saga: Saga, covenant: Covenant, rng: random.Random | None = None
) -> Command:
    """More's Warning Bell on a Burning City: Vulcan's Warning Bell's
    warning of an eruption, rolled and kept in the covenant's Diary."""
    project = _staged(covenant, BURNING_CITY, WARNING_BELL)
    if isinstance(project, Refuse):
        return project
    chance = rng or random.Random()

    def apply(_values: dict[str, Any]) -> list[str]:
        warning = sp.warning_bell(chance, saga)
        covenant.diary.append(
            CovenantDiaryEntry(
                saga.current_year,
                saga.current_season,
                f"{WARNING_BELL}: {project.name or project.kind}",
                f"{warning.words()}\nRules: {sp.BELL_SOURCE}",
            )
        )
        return notes(warning.words())

    return Form(
        f"{WARNING_BELL}: {escape(project.name or project.kind)}",
        list,
        apply,
        live=lambda _values: (
            "The volcano stirs: roll for the bell's warning. A stress die of "
            "days; a 0 gives the botch die's hours, and a botch no warning at "
            f"all ({HP} pp. 16-17)."
        ),
        save_label="Roll",
        help_id=STAGED_SECTION,
    )


# -- More: Gather a Connection (an Intangible Assassin) ------------------------


def _labs(saga: Saga, covenant: Covenant) -> list[tuple[str, str]]:
    return [
        (escape(lab.name or lab.id), lab.id)
        for lab in saga.laboratories
        if lab.covenant_id == covenant.id
    ]


def _quarries(saga: Saga) -> list[tuple[str, str]]:
    return [
        (escape(c.name), c.id)
        for c in sorted(saga.characters, key=lambda c: c.name.casefold())
    ]


def gather_fields(saga: Saga, covenant: Covenant) -> list[DialogField]:
    labs = _labs(saga, covenant)
    return [
        DialogField(
            "quarry",
            "Quarry",
            "select",
            None,
            options=_quarries(saga),
            allow_blank=True,
            placeholder="(typed below)",
        ),
        DialogField("named", "Or by name", "text", ""),
        DialogField(
            "how",
            "Gathered from",
            "select",
            sp.GATHERINGS[0].key,
            options=[(g.label, g.key) for g in sp.GATHERINGS],
        ),
        DialogField(
            "lab",
            "Kept in",
            "select",
            labs[0][1] if labs else None,
            options=labs,
            required=True,
            hint="Fixing it, a season and a pawn of Vim, makes it last for good "
            "(DE p. 250).",
        ),
    ]


def _quarry_name(saga: Saga, values: dict[str, Any]) -> str:
    found = saga.character(values.get("quarry")) if values.get("quarry") else None
    return found.name if found is not None else (values.get("named") or "").strip()


def validate_gather(saga: Saga) -> Callable[[dict[str, Any]], str | None]:
    def validate(values: dict[str, Any]) -> str | None:
        if not _quarry_name(saga, values):
            return "Choose the quarry, or type his name."
        return None

    return validate


def gather_form(saga: Saga, covenant: Covenant) -> Command:
    """More's Gather a Connection on an Intangible Assassin: an Arcane
    Connection to the quarry kept in a laboratory, lasting as the way it
    was gathered does (HP pp. 86-91), and a work on the Gathering
    connections stage."""
    project = _staged(covenant, INTANGIBLE_ASSASSIN, GATHER)
    if isinstance(project, Refuse):
        return project
    if not _labs(saga, covenant):
        return Refuse(GATHER, "The covenant has no laboratory to keep it in.")

    def live(values: dict[str, Any]) -> str:
        gathering = sp.GATHERING_BY_KEY.get(values.get("how") or "")
        if gathering is None:
            return ""
        return (
            f"An Arcane Connection lasting {gathering.lasts.lower()} ({HP} "
            f"{gathering.pages}). Kept unfixed, it lapses."
        )

    def apply(values: dict[str, Any]) -> list[str]:
        gathering = sp.GATHERING_BY_KEY[values.get("how") or sp.GATHERINGS[0].key]
        lab = saga.laboratory(values.get("lab"))
        if lab is None:
            return notes("That laboratory is gone.")
        quarry = _quarry_name(saga, values)
        lab.arcane_connections.append(
            ArcaneConnection(
                id=new_instance_id(),
                to=f"{quarry}: {gathering.label.lower()}",
                lasts=gathering.lasts,
                source=f"{project.name or project.kind} ({HP} {gathering.pages})",
            )
        )
        stage = next(
            (s for s in project.stages if s.name == "Gathering connections"), None
        )
        project.works.append(
            ProjectWork(
                kind=OTHER,
                name=f"A connection to {quarry}",
                season=saga.current_season,
                year=saga.current_year,
                seasons=0,
                stage=stage.id if stage is not None else "",
                details=gathering.label,
            )
        )
        return notes(
            f"{escape(gathering.label)}: an Arcane Connection to {escape(quarry)}, "
            f"kept in {escape(lab.name or lab.id)}."
        )

    return Form(
        f"{GATHER}: {escape(project.name or project.kind)}",
        lambda: gather_fields(saga, covenant),
        apply,
        validate=validate_gather(saga),
        live=live,
        help_id=STAGED_SECTION,
    )


# -- More: Lower an Aegis (an Intangible Assassin) -----------------------------


def aegis_fields(saga: Saga) -> list[DialogField]:
    covenants = [
        (escape(f"{c.name} (Aegis {c.aegis_of_the_hearth})"), c.id)
        for c in saga.covenants
        if c.aegis_of_the_hearth
    ]
    return [
        DialogField(
            "spell",
            "Spell",
            "select",
            sp.GUTTERING,
            options=[
                ("Guttering of the Home-Fires (suppresses it)", sp.GUTTERING),
                ("Removing the Hearth's Keystone (dispels it)", sp.KEYSTONE),
            ],
        ),
        DialogField("level", "Its level", "int", 30),
        DialogField(
            "covenant",
            "The Aegis of",
            "select",
            covenants[0][1] if covenants else None,
            options=covenants,
            allow_blank=True,
            placeholder="(typed below)",
        ),
        DialogField("aegis", "Or an Aegis of level", "optint", None),
        DialogField(
            "penetration",
            "Its Penetration Total",
            "optint",
            None,
            hint="It must Penetrate the Aegis too (HP p. 94).",
        ),
    ]


def _aegis_level(saga: Saga, values: dict[str, Any]) -> int | None:
    typed = values.get("aegis")
    if typed is not None:
        return typed
    found = saga.covenant(values.get("covenant")) if values.get("covenant") else None
    return found.aegis_of_the_hearth if found is not None else None


def aegis_live(saga: Saga) -> Callable[[dict[str, Any]], str]:
    def live(values: dict[str, Any]) -> str:
        aegis = _aegis_level(saga, values)
        if aegis is None:
            return "Choose the covenant whose Aegis it is, or type its level."
        level = values.get("level") or 0
        pen = values.get("penetration")
        lines: list[str] = []
        if values.get("spell") == sp.KEYSTONE:
            reach = sp.keystone_reach(level, 0)
            need = aegis - reach + 1
            lines.append(
                f"Removing the Hearth's Keystone {level} dispels an Aegis under "
                f"{reach} + a stress die: against {aegis}, "
                + (
                    "[$text-success]any die[/]"
                    if need <= 0
                    else f"a die of {need} or more"
                )
                + "."
            )
        else:
            reach = sp.guttering_reach(level)
            fits = aegis < reach
            tone = "$text-success" if fits else "$text-warning"
            lines.append(
                f"Guttering of the Home-Fires {level} suppresses an Aegis under "
                f"{reach}: against {aegis}, [{tone}]"
                + ("it reaches" if fits else "too strong")
                + "[/] (for a Diameter)."
            )
        if pen is not None:
            tone = "$text-success" if pen > aegis else "$text-warning"
            lines.append(
                f"Penetration {pen} against the Aegis {aegis}: [{tone}]"
                + ("penetrates" if pen > aegis else "fails to penetrate")
                + "[/]."
            )
        lines.append(
            "[dim]A magus casting from inside a hostile Aegis loses half its level "
            "from his Casting Total; destroying one is likely deprivation of "
            f"magical power, unless the war is declared on the whole covenant "
            f"({HP} pp. 79, 94).[/]"
        )
        return "\n".join(lines)

    return live


def aegis_form(
    saga: Saga, covenant: Covenant, rng: random.Random | None = None
) -> Command:
    """More's Lower an Aegis on an Intangible Assassin: whether Guttering
    of the Home-Fires or Removing the Hearth's Keystone reaches an Aegis
    (HP pp. 94-95); Roll throws the Keystone's stress die."""
    project = _staged(covenant, INTANGIBLE_ASSASSIN, LOWER_AEGIS)
    if isinstance(project, Refuse):
        return project
    chance = rng or random.Random()

    def apply(values: dict[str, Any]) -> list[str]:
        aegis = _aegis_level(saga, values)
        if aegis is None:
            return notes("No Aegis chosen.")
        level = values.get("level") or 0
        pen = values.get("penetration")
        through = pen is None or pen > aegis
        if values.get("spell") == sp.KEYSTONE:
            die = dice.stress_die(chance, saga=saga)
            reach = sp.keystone_reach(level, 0 if die.botched else die.value)
            done = through and not die.botched and aegis < reach
            return notes(
                f"Stress die {die.value}"
                + (" (a botch)" if die.botched else "")
                + f": the Keystone reaches an Aegis under {reach}. "
                + ("The Aegis falls." if done else "The Aegis holds.")
            )
        done = through and aegis < sp.guttering_reach(level)
        return notes(
            "The Aegis gutters out for a Diameter." if done else "The Aegis holds."
        )

    return Form(
        f"{LOWER_AEGIS}: {escape(project.name or project.kind)}",
        lambda: aegis_fields(saga),
        apply,
        live=aegis_live(saga),
        save_label="Roll",
        cancel_label="Close",
        help_id=STAGED_SECTION,
    )


# -- More: Death Roll (a Living Corpse) -----------------------------------------


def _gift(character: Character) -> str:
    """ "Gentle", "Blatant", "Normal", or "" for the unGifted."""
    ids = {vf.vf_id for vf in character.virtues_flaws}
    if THE_GIFT not in ids:
        return ""
    if GENTLE_GIFT in ids:
        return "Gentle"
    if BLATANT_GIFT in ids:
        return "Blatant"
    return "Normal"


def _magi(saga: Saga, covenant: Covenant) -> list[tuple[str, str]]:
    return [
        (escape(f"{c.name} ({c.type})"), c.id)
        for c in sorted(saga.characters, key=lambda c: c.name.casefold())
        if c.covenant_id == covenant.id
    ]


def death_fields(saga: Saga, covenant: Covenant) -> list[DialogField]:
    people = _magi(saga, covenant)
    return [
        DialogField(
            "who",
            "Who dies",
            "select",
            people[0][1] if people else None,
            options=people,
            required=True,
        ),
        DialogField(
            "option",
            "The troupe's option",
            "select",
            OPTION_TWO,
            options=[
                ("Two: Magic has impact (a contest)", OPTION_TWO),
                ("One: random chance (the chart)", OPTION_ONE),
            ],
            hint=f"{HP} pp. 107-108: the troupe picks one for its saga.",
        ),
        DialogField(
            "power",
            "The saga's power",
            "select",
            "Medium",
            options=pairs(sp.POWERS),
            hint="Sets a magic ghost's starting Might (pp. 108-109).",
        ),
        DialogField(
            "days",
            "Days dead before animated",
            "int",
            0,
            hint="His corpse's Physical Characteristics fall 1 a day, to -5 "
            "(p. 108). 0 for his own body, kept by the ward.",
        ),
    ]


def _traits_total(character: Character) -> int:
    return sum(abs(t.score) for t in character.personality_traits)


def _lore(character: Character) -> tuple[str, int]:
    scored = [(name, ability_level(character, name)) for name in LORES]
    return max(scored, key=lambda pair: pair[1])


def _player_roll(
    saga: Saga, character: Character, rng: random.Random
) -> tuple[int, bool, str]:
    aura, _realm = realms.present_aura(saga, character)
    lore = ability_level(character, "Magic Lore")
    vim = derived.form_bonus(character, "Vim")
    die = dice.stress_die(rng, saga=saga)
    total = (0 if die.botched else die.value) + aura + lore + vim
    words = (
        f"his stress die {die.value}{' (a botch)' if die.botched else ''} + aura "
        f"{aura} + Magic Lore {lore} + Vim Form Bonus {vim} = {total}"
    )
    return total, die.botched, words


def _storyguide_roll(character: Character, rng: random.Random) -> tuple[int, str, str]:
    traits = _traits_total(character)
    lore_name, lore = _lore(character)
    die = dice.stress_die(rng, 0)
    total = die.value + traits + lore
    words = (
        f"the storyguide's stress die {die.value} + his Personality Traits {traits} "
        f"+ {lore_name} {lore} = {total}"
    )
    return total, lore_name, words


def _sole_trait(character: Character) -> str:
    traits = character.personality_traits
    if not traits:
        return "none (he had none)"
    top = max(traits, key=lambda t: abs(t.score))
    return f"{top.name} {top.score * 2:+d}"


def death_lines(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    """The death roll and what the ghost is, line by line."""
    gift = _gift(character)
    lines: list[str] = []
    realm = ""
    if values.get("option") == OPTION_ONE:
        roll = dice.simple_die(rng)
        ghost = sp.chart(roll)
        lines.append(f"The chart: a simple die of {roll}.")
    else:
        player, botched, player_words = _player_roll(saga, character, rng)
        guide, lore_name, guide_words = _storyguide_roll(character, rng)
        ghost = sp.contest(player, guide, botched)
        realm = {"Dominion Lore": "Divine", "Infernal Lore": "Infernal"}.get(
            lore_name, "Faerie"
        )
        lines.append(f"The contest: {player_words}, against {guide_words}.")
    if not gift:
        ghost = sp.ungifted(ghost)
    words = sp.GHOST_WORDS[ghost]
    if ghost == sp.OTHER_REALM and realm:
        words = f"A ghost of the {realm} realm"
    lines.append(f"[b]{words}.[/]")
    if ghost in (sp.NO_SPIRIT, sp.OTHER_REALM, sp.MINDLESS):
        if ghost == sp.OTHER_REALM:
            lines.append(
                "Devices made for a magic ghost don't bind it; one of another realm "
                f"is made as that realm's rules give ({HP} pp. 111-113)."
            )
        return lines
    might = sp.starting_might(values.get("power") or "Medium", ghost)
    season, xp = sp.SEASON_XP[ghost]
    lines.append(
        f"Magic Might {might} (raised by Improved Might Qualities); a {season} "
        f"spirit, {xp} experience to buy back the Abilities he had; "
        f"{sp.vis_pawns(might)} pawns of vis of its Form ({HP} pp. 108-110)."
    )
    air = sp.magical_air(gift) if gift else "Magical Air"
    lines.append(
        "Virtues: Magic Spirit for The Gift, Transformed (Being)"
        + (f", and {air}" if air else "")
        + f"; his one Personality Trait {_sole_trait(character)} ({HP} pp. 109, "
        "111)."
    )
    days = values.get("days") or 0
    fall = sp.decay(days)
    if days:
        lines.append(
            "His corpse: Mental Characteristics n/a; Physical ones "
            + (f"{fall} each" if fall is not None else "n/a, a year dead")
            + f" ({HP} p. 108)."
        )
    return lines


def death_form(
    saga: Saga, covenant: Covenant, rng: random.Random | None = None
) -> Command:
    """More's Death Roll on a Living Corpse: a magus's death roll and the
    ghost it makes, kept in his Diary and on the transformation stage.
    His sheet isn't rebuilt: the player buys his Qualities, Abilities and
    Powers again by hand (HP pp. 108-111)."""
    project = _staged(covenant, LIVING_CORPSE, DEATH_ROLL)
    if isinstance(project, Refuse):
        return project
    if not _magi(saga, covenant):
        return Refuse(DEATH_ROLL, "No one of the covenant to roll for.")
    chance = rng or random.Random()

    def apply(values: dict[str, Any]) -> list[str]:
        character = saga.character(values.get("who"))
        if character is None:
            return notes("Choose who dies.")
        lines = death_lines(saga, character, values, chance)
        plain = [line.replace("[b]", "").replace("[/]", "") for line in lines]
        character.diary.append(
            DiaryEntry(
                saga.current_year,
                saga.current_season,
                f"{DEATH_ROLL}: {project.name or project.kind}",
                "\n".join(plain) + f"\nRules: {sp.CORPSE_SOURCE}",
            )
        )
        stage = next(
            (s for s in project.stages if s.name == "The transformation"), None
        )
        project.works.append(
            ProjectWork(
                kind=OTHER,
                name=f"{character.name}'s death",
                season=saga.current_season,
                year=saga.current_year,
                seasons=0,
                who=character.id,
                stage=stage.id if stage is not None else "",
                details=plain[-1] if plain else "",
            )
        )
        return lines

    return Form(
        f"{DEATH_ROLL}: {escape(project.name or project.kind)}",
        lambda: death_fields(saga, covenant),
        apply,
        live=lambda _values: (
            "Rolled when he dies: the ghost his spirit becomes, if any. His "
            "sheet is then rebuilt by hand as a magic creature's (HP pp. "
            "107-111; Realms of Power: Magic)."
        ),
        save_label="Roll",
        help_id=STAGED_SECTION,
    )


# -- the tab's pieces ----------------------------------------------------------


STAGES_LIST = KindList(
    STAGED_STAGES_SECTION, stages_title, stages_grid, stages_ops, stage_info
)
STAGE_WORKS_LIST = KindList(
    STAGE_WORKS_SECTION, works_title, works_grid, works_ops, work_info
)


def staged_block(
    saga: Saga,
    covenant: Covenant,
    edit: Callable[[Saga, Neighbour], Command],
    after: str,
) -> KindBlock:
    """The project's facts and its chapter's rules, after the projects
    list; its Edit is the project's form (`edit`)."""
    return KindBlock(
        STAGED_SECTION,
        staged_title(saga, covenant),
        block_text,
        edit,
        edit_label="Edit Project",
        after=after,
        facts=staged_facts,
        facts_inline=True,
    )
