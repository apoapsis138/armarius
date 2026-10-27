"""A covenant's Projects tab (a chapter on the desktop): its Hermetic
Projects, and for the one shown (a Great Tower) its height, quality and
damage levels, its master mason, the works done on it and its craft
devices; with the forms that add and edit them, and More's Stress Check
and Conjure Levels on the tower.

The tab shows only once a project is begun (Begin Project, on the
Attributes tab). The rules are rules.hermetic_projects' (Hermetic
Projects pp. 36-41); the records models.hermetic_projects'.

Pattern: the kind tabs' Strategy (neighbour_lists.KindTab), as the
covenant's Manors tab uses it: the tab is a KindTab of lists and a block,
drawn by each front-end's kind-tab code, the covenant adapted to a
neighbour's record (manors.manors_of). A kind of project is a dict entry
(KIND_TEXT), not a class: 932-C's Menagerie joins it as a second kind."""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any

from . import menagerie as men
from .commands import Act, Command, Confirm, Form, Refuse, SectionOps, notes
from .form_spec import DialogField, pairs
from .grids import Grid
from .manors import manors_of
from .markup import escape
from .models import (
    SEASONS,
    Character,
    Covenant,
    Neighbour,
    Saga,
)
from .models.hermetic_projects import (
    BOTCHED,
    BUILDING,
    BUTTRESS,
    DAMAGED,
    DEVICE_KIND_LABELS,
    DEVICE_KINDS,
    GREAT_TOWER,
    HELD,
    MENAGERIE,
    OTHER,
    PROJECT_KINDS,
    QUALITIES,
    REBUILD,
    REPAIR,
    RITUAL,
    SHODDY,
    STANDARD,
    STRESS,
    STRESS_OUTCOMES,
    WORK_KIND_LABELS,
    WORK_KINDS,
    CraftDevice,
    HermeticProject,
    ProjectWork,
)
from .neighbour_lists import KindBlock, KindList, KindTab, LedgerEntry, tab_ops
from .references import Fact
from .rules import dice, sites
from .rules import hermetic_projects as hp
from .rules.aura_change import number as aura_number
from .sections import (
    PROJECT_DEVICES_SECTION,
    PROJECT_WORKS_SECTION,
    PROJECTS_SECTION,
    TOWER_SECTION,
)

HP = hp.HP
TAB_ID = "tab-cov-projects"
STRESS_CHECK = "Stress Check"
CONJURE_LEVELS = "Conjure Levels"
SHOW_PROJECT = "Show Project"
BEGIN_PROJECT = "Begin Project"
PANEL = "[dim]Choose a project, a work or a device.[/]"
#: What each kind of project is, in a line.
KIND_TEXT: dict[str, str] = {
    GREAT_TOWER: "a tower raised level by level, by ritual and by masons",
    MENAGERIE: men.KIND_LINE,
}


# -- finding the record --------------------------------------------------------


def covenant_of(saga: Saga, holder: Neighbour) -> Covenant | None:
    """The covenant a Projects tab shows (its record adapted as a
    neighbour's, manors.manors_of)."""
    return saga.covenant(holder.id)


def shown(saga: Saga, holder: Neighbour) -> HermeticProject | None:
    covenant = covenant_of(saga, holder)
    return hp.shown_project(covenant) if covenant is not None else None


def has_projects(covenant: Covenant | None) -> bool:
    """Whether the covenant shows a Projects tab: once a project is begun."""
    return covenant is not None and bool(covenant.hermetic_projects)


def _name(saga: Saga, character_id: str) -> str:
    found = saga.character(character_id) if character_id else None
    return found.name if found is not None else ""


def _when(season: str, year: int) -> str:
    return f"{season} {year}"


def _tone(quality: str) -> str:
    return {
        SHODDY: "text-warning",
        STANDARD: "text-success",
        hp.SUPERIOR: "text-success",
        hp.EXCELLENT: "text-success",
        HELD: "text-success",
        DAMAGED: "text-warning",
        BOTCHED: "text-error",
    }.get(quality, "label")


def _coloured(words: str, tone: str) -> str:
    return f"[${tone}]{escape(words)}[/]" if tone != "label" else escape(words)


# -- the projects list ---------------------------------------------------------


def progress(project: HermeticProject) -> str:
    if project.kind == MENAGERIE:
        return men.progress(project)
    levels = hp.height_levels(project)
    if not levels:
        return "not built"
    return f"{hp.feet(levels):,} ft"


def note(project: HermeticProject) -> str:
    if project.kind == MENAGERIE:
        return men.note(project)
    quality = hp.quality(project)
    if not quality:
        return ""
    if hp.damage_lost(project):
        return f"{hp.damage_lost(project)} damage lost"
    return f"{quality} at weakest"


def projects_title(saga: Saga, holder: Neighbour) -> str:
    covenant = covenant_of(saga, holder)
    count = len(covenant.hermetic_projects) if covenant is not None else 0
    return f"Hermetic Projects ({count})"


def projects_grid(saga: Saga, holder: Neighbour) -> Grid:
    covenant = covenant_of(saga, holder)
    listed = covenant.hermetic_projects if covenant is not None else []
    current = hp.shown_project(covenant) if covenant is not None else None
    rows = [
        [
            ("› " if p is current and len(listed) > 1 else "")
            + (p.name or "(unnamed)"),
            p.kind,
            str(p.year),
            progress(p),
            note(p),
        ]
        for p in listed
    ]
    styles = {
        (i, 4): "$text-warning"
        for i, p in enumerate(listed)
        if hp.quality(p) == SHODDY or hp.damage_lost(p)
    }
    return Grid(
        ["Project", "Kind", "Begun", "Progress", "Note"],
        rows,
        list(range(len(listed))),
        "No project begun.",
        styles=styles,
        caps=[22, 11, 5, 9],
    )


def project_info(saga: Saga, holder: Neighbour, index: int) -> str:
    covenant = covenant_of(saga, holder)
    if covenant is None or index >= len(covenant.hermetic_projects):
        return ""
    project = covenant.hermetic_projects[index]
    lines = [
        f"{escape(project.kind)}, {KIND_TEXT.get(project.kind, '')}; begun "
        f"{_when(project.season, project.year)}.",
        men.menagerie_text(saga, covenant, project)
        if project.kind == MENAGERIE
        else tower_text(saga, covenant, project),
    ]
    if project.description.strip():
        lines.append(escape(project.description.strip()))
    return "\n".join(lines)


# -- the tower -----------------------------------------------------------------


def tower_title(saga: Saga, covenant: Covenant | None) -> str:
    project = hp.shown_project(covenant) if covenant is not None else None
    if project is None:
        return "The Project"
    return f"{project.name or '(unnamed)'}: {project.kind}"


def tower_facts(saga: Saga, holder: Neighbour) -> list[Fact]:
    project = shown(saga, holder)
    if project is None:
        return []
    levels = hp.height_levels(project)
    quality = hp.quality(project)
    weakest = hp.weakest(project)
    failed = hp.failed_finesse(project)
    whole = hp.damage_levels(project)
    return [
        Fact("Height", f"{hp.feet(levels):,} ft ({levels} levels)"),
        Fact("Begun", _when(project.season, project.year)),
        Fact(
            "Quality",
            f"{quality} at its weakest ({weakest.year})"
            if quality and weakest is not None
            else "nothing built yet",
        ),
        Fact(
            "Damage levels",
            f"{hp.damage_left(project)} of {whole} ({quality} "
            f"{hp.BASE_DAMAGE[quality]} x {hp.SIZE_MULTIPLIER})"
            if quality
            else "none yet",
        ),
        Fact("Tethers", f"{hp.tethers(project)} preternatural, its rituals'"),
        Fact(
            "Failed Finesse",
            f"{failed} levels: next Heights {1 + failed} botch dice"
            if failed
            else "none: next Heights 1 botch die",
        ),
    ]


def mason_text(saga: Saga, covenant: Covenant, project: HermeticProject) -> str:
    """The master mason's lines: his effective score and rate, and the
    Workshop Total with the quality it builds."""
    found = hp.mason_of(saga, project, covenant.id)
    if found is None:
        return (
            "[$label]Master mason:[/] none yet. Edit the project to name one "
            f"({HP} pp. 36-37)."
        )
    levels = found.levels_a_season
    rate = (
        f"{levels} level{'s' if levels != 1 else ''} a season, "
        f"{hp.feet(levels * 4):,} ft a year"
        if levels
        else "not yet a level a season (it takes 5)"
    )
    nxt = (found.effective // hp.LEVEL_PER_SCORE + 1) * hp.LEVEL_PER_SCORE
    devices = f", devices +{found.devices} (at most his score)" if found.devices else ""
    extras: list[str] = []
    if hp.owns_de_architectura(saga, project, covenant.id):
        extras.append("De Architectura +1")
    if any(d.kind == hp.INNOVATION for d in project.devices):
        extras.append("the Water Wheel +1")
    innovation = f" ({', '.join(extras)})" if extras else ""
    quality = found.quality
    shown_quality = (
        _coloured(quality, _tone(quality)) if quality else "[$text-error]nothing[/]"
    )
    return (
        f"[$label]Master mason:[/] {escape(found.name)}, Int "
        f"{found.intelligence:+d}, {hp.MASON_CRAFT} {found.craft}{devices} = "
        f"[b]{found.effective}[/]: {rate}; {nxt} for "
        f"{_count_words(nxt // hp.LEVEL_PER_SCORE)} levels.\n"
        f"[$label]Workshop Total:[/] Int {found.intelligence} + {hp.MASON_CRAFT} "
        f"{found.craft} + Innovation {found.innovation}{innovation} + Raw "
        f"Materials {found.raw_materials} = [b]{found.workshop_total}[/]: "
        f"{shown_quality} work now."
    )


def _count_words(number: int) -> str:
    return {2: "two", 3: "three", 4: "four"}.get(number, str(number))


def tower_text(saga: Saga, covenant: Covenant, project: HermeticProject) -> str:
    return (
        mason_text(saga, covenant, project)
        + "\n[dim]The weakest section sets the damage levels; a season's "
        f"rebuilding makes a shoddy section standard ({HP} pp. 37-38).[/]"
    )


def tower_block_text(saga: Saga, holder: Neighbour) -> str:
    covenant = covenant_of(saga, holder)
    project = shown(saga, holder)
    if covenant is None or project is None:
        return "[$label]No project begun.[/]"
    return tower_text(saga, covenant, project)


# -- the works -----------------------------------------------------------------


def _work_when(work: ProjectWork) -> str:
    if work.kind in (BUILDING, REPAIR) and work.seasons > 1:
        return f"{work.year} ({work.seasons} seasons)"
    return _when(work.season, work.year)


def _work_name(saga: Saga, work: ProjectWork) -> str:
    who = _name(saga, work.who)
    name = work.name or WORK_KIND_LABELS[work.kind]
    return f"{name} ({who})" if who and who not in name else name


def _work_badge(project: HermeticProject, work: ProjectWork) -> str:
    if work.kind == STRESS:
        return work.outcome or "–"
    if work.kind == REPAIR:
        return f"+{work.seasons} damage" if work.seasons > 1 else "+1 damage"
    if work.kind == REBUILD:
        return STANDARD
    return hp.section_quality(project, work) if work.quality else "–"


def works_title(saga: Saga, holder: Neighbour) -> str:
    project = shown(saga, holder)
    return f"Works ({len(project.works) if project is not None else 0})"


def works_grid(saga: Saga, holder: Neighbour) -> Grid:
    project = shown(saga, holder)
    works = project.works if project is not None else []
    rows: list[list[str]] = []
    styles: dict[tuple[int, int], str] = {}
    for i, work in enumerate(works):
        badge = _work_badge(project, work) if project is not None else ""
        rows.append(
            [
                _work_when(work),
                _work_name(saga, work),
                f"+{work.levels}" if work.levels else "–",
                badge,
            ]
        )
        tone = _tone(badge)
        if tone != "label":
            styles[(i, 3)] = f"${tone}"
    return Grid(
        ["Season", "Work", "Levels", "Quality"],
        rows,
        list(range(len(works))),
        "Nothing done yet: Add a work, or More's Conjure Levels.",
        styles=styles,
        caps=[16, 44, 8],
    )


def works_ledger(saga: Saga, holder: Neighbour) -> list[LedgerEntry]:
    project = shown(saga, holder)
    if project is None:
        return []
    return [
        LedgerEntry(
            title=_work_name(saga, work),
            rubric="!" if work.kind == STRESS else "§",
            meta=_work_when(work),
            badge=_work_badge(project, work),
            tone=_tone(_work_badge(project, work)),
            body=escape(work.details),
            note=escape(work.note),
            subtitle=_work_when(work),
        )
        for work in project.works
    ]


def work_info(saga: Saga, holder: Neighbour, index: int) -> str:
    project = shown(saga, holder)
    if project is None or index >= len(project.works):
        return ""
    work = project.works[index]
    badge = _work_badge(project, work)
    lines = [
        f"{escape(_work_name(saga, work))}  ·  {WORK_KIND_LABELS[work.kind]}  ·  "
        f"{_coloured(badge, _tone(badge))}"
    ]
    if work.levels:
        lines.append(f"+{work.levels} levels, {hp.feet(work.levels):,} ft.")
    if work.quality == SHODDY and hp.section_quality(project, work) == STANDARD:
        lines.append("Rebuilt since as standard work.")
    if work.kind == STRESS and work.damage:
        lines.append(
            f"Lost {work.damage} damage level{'s' if work.damage > 1 else ''}."
        )
    if work.details:
        lines.append(escape(work.details))
    if work.note:
        lines.append(f"[i]{escape(work.note)}[/]")
    return "\n".join(lines)


# -- the craft devices ---------------------------------------------------------


def _device_bonus(device: CraftDevice) -> str:
    if device.kind == BUTTRESS:
        return f"+{device.count} stress" if device.count > 1 else "+1 stress"
    if device.kind == hp.INNOVATION:
        return "+1 Innovation"
    return "+1 Craft"


def devices_title(saga: Saga, holder: Neighbour) -> str:
    project = shown(saga, holder)
    covenant = covenant_of(saga, holder)
    if project is None or covenant is None:
        return "Craft Devices"
    found = hp.mason_of(saga, project, covenant.id)
    bonus = hp.craft_devices(project)
    cap = f", at most +{found.craft}" if found is not None else ""
    return f"Craft Devices (+{bonus}{cap})"


def devices_grid(saga: Saga, holder: Neighbour) -> Grid:
    project = shown(saga, holder)
    devices = project.devices if project is not None else []
    rows = [
        [
            d.name or "(unnamed)",
            ", ".join(part for part in (d.shape, d.effect) if part),
            _device_bonus(d),
        ]
        for d in devices
    ]
    return Grid(
        ["Device", "Effect", "Bonus"],
        rows,
        list(range(len(devices))),
        "No craft devices.",
        styles={(i, 2): "$text-success" for i in range(len(devices))},
        caps=[30, 22],
    )


def devices_ledger(saga: Saga, holder: Neighbour) -> list[LedgerEntry]:
    project = shown(saga, holder)
    if project is None:
        return []
    return [
        LedgerEntry(
            title=d.name or "(unnamed)",
            rubric="¶",
            meta=", ".join(part for part in (d.effect, d.shape) if part),
            badge=_device_bonus(d),
            tone="text-success",
            body=escape(d.description),
            subtitle=d.effect,
        )
        for d in project.devices
    ]


def device_info(saga: Saga, holder: Neighbour, index: int) -> str:
    project = shown(saga, holder)
    if project is None or index >= len(project.devices):
        return ""
    device = project.devices[index]
    lines = [
        "  ·  ".join(part for part in (device.effect, device.shape) if part),
        f"{DEVICE_KIND_LABELS[device.kind]}"
        + (f", {device.count} of them" if device.kind == BUTTRESS else "")
        + f" ({HP} pp. 39-41).",
    ]
    if device.description.strip():
        lines.append(escape(device.description.strip()))
    if device.kind == hp.CRAFT:
        lines.append(
            "[dim]Each kind of device counts once, and their total is at most "
            f"his {hp.MASON_CRAFT} ({HP} p. 39).[/]"
        )
    elif device.kind == BUTTRESS:
        lines.append(
            "[dim]The tower can use as many Flying Buttresses as the master "
            f"mason's {hp.MASON_CRAFT} ({HP} p. 41).[/]"
        )
    else:
        lines.append(f"[dim]Innovation never passes +3 ({HP} p. 41).[/]")
    return "\n".join(line for line in lines if line)


# -- forms ---------------------------------------------------------------------


def _people(saga: Saga, covenant: Covenant) -> list[Character]:
    return [c for c in saga.characters if c.covenant_id == covenant.id]


def _people_options(saga: Saga, covenant: Covenant) -> list[tuple[str, str]]:
    return [
        (escape(f"{c.name} ({c.type})"), c.id)
        for c in sorted(_people(saga, covenant), key=lambda c: c.name.casefold())
    ]


def _is_tower(values: dict[str, Any]) -> bool:
    return values.get("kind", GREAT_TOWER) == GREAT_TOWER


def project_fields(
    saga: Saga, covenant: Covenant, project: HermeticProject | None
) -> list[DialogField]:
    """A Hermetic Project: its name and kind, when begun, its master
    mason and place, and the workshop's Innovation and Raw Materials."""
    places = [(escape(p.name), p.id) for p in sites.all_places(saga)]
    return [
        DialogField(
            "name", "Name", "text", project.name if project else "", required=True
        ),
        DialogField(
            "kind",
            "Kind",
            "select",
            project.kind if project else GREAT_TOWER,
            options=pairs(PROJECT_KINDS),
        ),
        DialogField(
            "season",
            "Begun",
            "select",
            project.season if project else saga.current_season,
            options=pairs(SEASONS),
        ),
        DialogField(
            "year", "Year", "int", project.year if project else saga.current_year
        ),
        DialogField(
            "mason_id",
            "Master mason",
            "select",
            (project.mason_id if project else "") or None,
            options=_people_options(saga, covenant),
            allow_blank=True,
            placeholder="(none yet)",
            hint=f"His {hp.MASON_CRAFT} sets how fast the tower rises ({HP} p. 36).",
            show_if=_is_tower,
        ),
        DialogField(
            "place_id",
            "Its place",
            "select",
            (project.place_id if project else covenant.place_id) or None,
            options=places,
            allow_blank=True,
            placeholder="(none)",
            hint="Its rituals' tethers go to this place's aura; a menagerie's "
            "beasts live in its aura.",
        ),
        DialogField(
            "innovation",
            "Innovation",
            "int",
            project.innovation if project else 0,
            hint="The building operation's own, 0 to 3; De Architectura and the "
            f"Water Wheel add theirs ({HP} pp. 37, 41).",
            show_if=_is_tower,
        ),
        DialogField(
            "raw_materials",
            "Raw Materials",
            "int",
            project.raw_materials if project else 0,
            hint="0 to 3.",
            show_if=_is_tower,
        ),
        # A Menagerie's staff and owner.
        *men.project_fields(saga, covenant, project),
        DialogField(
            "description",
            "Description",
            "area",
            project.description if project else "",
        ),
    ]


def validate_project(values: dict[str, Any]) -> str | None:
    for key, label in (
        ("innovation", "Innovation"),
        ("raw_materials", "Raw Materials"),
    ):
        if not 0 <= (values.get(key) or 0) <= hp.WORKSHOP_CAP:
            return f"{label} is 0 to {hp.WORKSHOP_CAP} ({HP} p. 37)."
    return None


def _write_project(project: HermeticProject, values: dict[str, Any]) -> None:
    project.name = values["name"]
    project.kind = values.get("kind") or GREAT_TOWER
    project.season = values.get("season") or "Spring"
    project.year = values["year"]
    project.mason_id = values.get("mason_id") or ""
    project.place_id = values.get("place_id") or ""
    project.innovation = values.get("innovation") or 0
    project.raw_materials = values.get("raw_materials") or 0
    project.description = values.get("description") or ""
    men.write_project(project, values)


def project_form(
    saga: Saga,
    covenant: Covenant,
    project: HermeticProject | None,
    title: str = "",
) -> Form:
    def apply(values: dict[str, Any]) -> None:
        if project is not None:
            _write_project(project, values)
            return
        made = HermeticProject()
        _write_project(made, values)
        covenant.hermetic_projects.append(made)
        covenant.project_shown = made.id

    return Form(
        title or ("Edit Project" if project is not None else "Add Project"),
        lambda: project_fields(saga, covenant, project),
        apply,
        validate=validate_project,
        help_id=PROJECTS_SECTION,
    )


def begin_form(saga: Saga, covenant: Covenant) -> Command:
    """Begin Project, on the Attributes tab: the first project shows the
    Projects tab."""
    return project_form(saga, covenant, None, BEGIN_PROJECT)


def projects_ops(saga: Saga, holder: Neighbour) -> SectionOps:
    covenant = covenant_of(saga, holder)
    if covenant is None:
        return SectionOps()
    listed = covenant.hermetic_projects

    def remove(index: int) -> Command:
        project = listed[index]

        def apply() -> None:
            listed.remove(project)
            if covenant.project_shown == project.id:
                covenant.project_shown = ""

        return Confirm(f"Delete {escape(project.name or 'this project')}?", apply)

    return SectionOps(
        add=lambda: project_form(saga, covenant, None),
        edit=lambda index: project_form(saga, covenant, listed[index]),
        remove=remove,
        rows=lambda: [p.name or "(unnamed)" for p in listed],
    )


def tower_edit(saga: Saga, holder: Neighbour) -> Command:
    covenant = covenant_of(saga, holder)
    project = shown(saga, holder)
    if covenant is None or project is None:
        return Refuse("Edit Project", "Begin a project first.")
    return project_form(saga, covenant, project)


def show_project(saga: Saga, covenant: Covenant, index: int | None) -> Command:
    """More's Show Project: the chosen project's tower, works and devices
    on the tab."""
    listed = covenant.hermetic_projects
    if index is None or not 0 <= index < len(listed):
        return Refuse(SHOW_PROJECT, "Choose a project first.")
    project = listed[index]

    def apply() -> None:
        covenant.project_shown = project.id

    return Act(apply, SHOW_PROJECT)


# -- works ---------------------------------------------------------------------


def _kind_is(*kinds: str) -> Callable[[dict[str, Any]], bool]:
    return lambda values: values.get("kind") in kinds


def work_fields(
    saga: Saga, covenant: Covenant, project: HermeticProject, work: ProjectWork | None
) -> list[DialogField]:
    """A work done on the tower, as its ledger keeps it."""
    shoddy = [
        (escape(f"{w.name or WORK_KIND_LABELS[w.kind]}, {_work_when(w)}"), w.id)
        for w in hp.sections(project)
        if w.quality == SHODDY and w is not work
    ]
    return [
        DialogField(
            "kind",
            "Kind",
            "select",
            work.kind if work else BUILDING,
            options=[(WORK_KIND_LABELS[k], k) for k in WORK_KINDS],
        ),
        DialogField("name", "Work", "text", work.name if work else ""),
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
            "Seasons it covers",
            "int",
            work.seasons if work else 1,
            show_if=_kind_is(BUILDING, REPAIR),
            hint="A repair restores a damage level each season (HP p. 38).",
        ),
        DialogField(
            "levels",
            "Levels added",
            "int",
            work.levels if work else 0,
            show_if=_kind_is(RITUAL, BUILDING, OTHER),
            hint="20 ft a level.",
        ),
        DialogField(
            "quality",
            "Quality",
            "select",
            (work.quality if work else "") or None,
            options=pairs(QUALITIES),
            allow_blank=True,
            show_if=_kind_is(RITUAL, BUILDING, OTHER),
            hint="A ritual whose Finesse roll failed builds shoddy work (HP p. 39).",
        ),
        DialogField(
            "rebuilt",
            "Section rebuilt",
            "select",
            (work.rebuilt if work else "") or None,
            options=shoddy,
            allow_blank=True,
            show_if=_kind_is(REBUILD),
            hint="The shoddy section made standard.",
        ),
        DialogField(
            "outcome",
            "Outcome",
            "select",
            (work.outcome if work else "") or HELD,
            options=pairs(STRESS_OUTCOMES),
            show_if=_kind_is(STRESS),
        ),
        DialogField(
            "damage",
            "Damage levels lost",
            "int",
            work.damage if work else 0,
            show_if=_kind_is(STRESS),
        ),
        DialogField(
            "who",
            "Who",
            "select",
            (work.who if work else project.mason_id) or None,
            options=_people_options(saga, covenant),
            allow_blank=True,
            placeholder="(no one named)",
        ),
        DialogField("details", "The roll", "text", work.details if work else ""),
        DialogField("note", "Note", "text", work.note if work else ""),
    ]


def validate_work(values: dict[str, Any]) -> str | None:
    if (values.get("levels") or 0) < 0 or (values.get("damage") or 0) < 0:
        return "Levels and damage levels are 0 or more."
    if values.get("kind") in (BUILDING, REPAIR) and (values.get("seasons") or 0) < 1:
        return "A work covers a season or more."
    return None


def _write_work(work: ProjectWork, values: dict[str, Any]) -> None:
    kind = values.get("kind") or BUILDING
    work.kind = kind
    work.name = values.get("name") or ""
    work.season = values.get("season") or "Spring"
    work.year = values["year"]
    builds = kind in (RITUAL, BUILDING, OTHER)
    work.seasons = (values.get("seasons") or 1) if kind in (BUILDING, REPAIR) else 1
    work.levels = (values.get("levels") or 0) if builds else 0
    work.quality = (values.get("quality") or "") if builds else ""
    work.rebuilt = (values.get("rebuilt") or "") if kind == REBUILD else ""
    work.outcome = (values.get("outcome") or "") if kind == STRESS else ""
    work.damage = (values.get("damage") or 0) if kind == STRESS else 0
    work.who = values.get("who") or ""
    work.details = values.get("details") or ""
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
        help_id=PROJECT_WORKS_SECTION,
    )


def works_ops(saga: Saga, holder: Neighbour) -> SectionOps:
    covenant = covenant_of(saga, holder)
    if covenant is None:
        return SectionOps()

    def project() -> HermeticProject | None:
        return hp.shown_project(covenant)

    def add() -> Command:
        found = project()
        if found is None:
            return Refuse("Add Work", "Begin a project first.")
        return work_form(saga, covenant, found, None)

    def edit(index: int) -> Command:
        found = project()
        if found is None or index >= len(found.works):
            return Refuse("Edit Work", "Choose a work first.")
        return work_form(saga, covenant, found, found.works[index])

    def remove(index: int) -> Command:
        found = project()
        if found is None or index >= len(found.works):
            return Refuse("Delete", "Choose a work first.")
        work = found.works[index]
        return Confirm(
            f"Delete {escape(_work_name(saga, work))}?",
            lambda: found.works.remove(work),
        )

    def rows() -> list[str]:
        found = project()
        return [_work_name(saga, w) for w in found.works] if found else []

    return SectionOps(add=add, edit=edit, remove=remove, rows=rows)


# -- devices -------------------------------------------------------------------


def device_fields(device: CraftDevice | None) -> list[DialogField]:
    return [
        DialogField(
            "name", "Device", "text", device.name if device else "", required=True
        ),
        DialogField(
            "effect",
            "Effect",
            "text",
            device.effect if device else "",
            placeholder="ReHe 40",
        ),
        DialogField(
            "shape",
            "Made as",
            "text",
            device.shape if device else "",
            placeholder="a crane",
        ),
        DialogField(
            "kind",
            "What it adds",
            "select",
            device.kind if device else hp.CRAFT,
            options=[(DEVICE_KIND_LABELS[k], k) for k in DEVICE_KINDS],
        ),
        DialogField(
            "count",
            "How many stand",
            "int",
            device.count if device else 1,
            show_if=lambda values: values.get("kind") == BUTTRESS,
        ),
        DialogField(
            "description", "Description", "area", device.description if device else ""
        ),
    ]


def validate_device(values: dict[str, Any]) -> str | None:
    if values.get("kind") == BUTTRESS and (values.get("count") or 0) < 1:
        return "At least one buttress stands."
    return None


def _write_device(device: CraftDevice, values: dict[str, Any]) -> None:
    device.name = values["name"]
    device.effect = values.get("effect") or ""
    device.shape = values.get("shape") or ""
    device.kind = values.get("kind") or hp.CRAFT
    device.count = (values.get("count") or 1) if device.kind == BUTTRESS else 1
    device.description = values.get("description") or ""


def device_form(project: HermeticProject, device: CraftDevice | None) -> Form:
    def apply(values: dict[str, Any]) -> None:
        if device is not None:
            _write_device(device, values)
            return
        made = CraftDevice()
        _write_device(made, values)
        project.devices.append(made)

    return Form(
        "Edit Device" if device is not None else "Add Device",
        lambda: device_fields(device),
        apply,
        validate=validate_device,
        help_id=PROJECT_DEVICES_SECTION,
    )


def devices_ops(saga: Saga, holder: Neighbour) -> SectionOps:
    covenant = covenant_of(saga, holder)
    if covenant is None:
        return SectionOps()

    def project() -> HermeticProject | None:
        return hp.shown_project(covenant)

    def add() -> Command:
        found = project()
        if found is None:
            return Refuse("Add Device", "Begin a project first.")
        return device_form(found, None)

    def edit(index: int) -> Command:
        found = project()
        if found is None or index >= len(found.devices):
            return Refuse("Edit Device", "Choose a device first.")
        return device_form(found, found.devices[index])

    def remove(index: int) -> Command:
        found = project()
        if found is None or index >= len(found.devices):
            return Refuse("Delete", "Choose a device first.")
        device = found.devices[index]
        return Confirm(
            f"Delete {escape(device.name or 'this device')}?",
            lambda: found.devices.remove(device),
        )

    def rows() -> list[str]:
        found = project()
        return [d.name for d in found.devices] if found else []

    return SectionOps(add=add, edit=edit, remove=remove, rows=rows)


# -- More: Stress Check --------------------------------------------------------


def stress_fields(saga: Saga, project: HermeticProject) -> list[DialogField]:
    return [
        DialogField(
            "event",
            "What happens",
            "select",
            hp.STRESS_EVENTS[0],
            options=pairs(hp.STRESS_EVENTS),
        ),
        DialogField(
            "severity",
            "How severe",
            "int",
            0,
            hint=f"The storyguide's modifier for the event ({HP} p. 38).",
        ),
        DialogField(
            "repaired",
            "Previously repaired (−1)",
            "check",
            hp.previously_repaired(project),
        ),
        DialogField(
            "buttresses",
            "Flying Buttresses (+1 each)",
            "int",
            hp.buttresses(project),
            hint=f"As many as the master mason's {hp.MASON_CRAFT} count ({HP} p. 41).",
        ),
        DialogField(
            "season",
            "Season",
            "select",
            saga.current_season,
            options=pairs(SEASONS),
        ),
        DialogField("year", "Year", "int", saga.current_year),
    ]


def _check(
    saga: Saga, project: HermeticProject, values: dict[str, Any]
) -> hp.StressCheck:
    return hp.stress_check(
        saga,
        project,
        severity=values.get("severity") or 0,
        repaired=bool(values.get("repaired")),
        buttress_count=values.get("buttresses") or 0,
    )


def stress_live(
    saga: Saga, project: HermeticProject
) -> Callable[[dict[str, Any]], str]:
    def live(values: dict[str, Any]) -> str:
        check = _check(saga, project, values)
        parts = " + ".join(check.parts) or "nothing"
        need = check.needed
        lines = [
            f"stress die + {parts} = [b]{check.total} + die[/] against "
            f"{hp.STRESS_EASE}",
            f"The die must show {need} or more."
            + (" [$text-warning]Only an exploding die will do.[/]" if need > 10 else "")
            if need > 0
            else "It holds unless the die botches.",
        ]
        if not hp.quality(project):
            lines.append("[$text-warning]Nothing is built yet: nothing to strain.[/]")
        if hp.mason(saga, project) is None:
            lines.append(
                f"[$text-warning]No master mason: his {hp.MASON_CRAFT} "
                "counts for nothing.[/]"
            )
        lines += [
            "",
            "Failure loses a damage level, a botch one more for each botch: a "
            "partial collapse somewhere inside, and a story. Each lost level "
            "takes the mason a season to repair, and no other building goes on "
            "meanwhile (City & Guild p. 77).",
            f"[dim]Quality is the weakest section's ({HP} p. 38).[/]",
        ]
        return "\n".join(lines)

    return live


def stress_form(
    saga: Saga,
    covenant: Covenant,
    rng: random.Random | None = None,
) -> Command:
    """More's Stress Check on the tower: rolled, and kept in its works."""
    project = hp.shown_project(covenant)
    if project is None:
        return Refuse(STRESS_CHECK, "Begin a project first.")
    if not hp.stands(project):
        return Refuse(STRESS_CHECK, "Nothing of the tower is built yet.")

    def apply(values: dict[str, Any]) -> list[str]:
        check = _check(saga, project, values)
        die = dice.stress_die(rng or random.Random(), saga=saga)
        roll = dice.Roll(check.total, die, hp.STRESS_EASE)
        lost = hp.stress_damage(bool(roll.succeeded), die.botches)
        outcome = BOTCHED if die.botched else HELD if roll.succeeded else DAMAGED
        shown_die = (
            f"a botch ({die.botches})" if die.botched else f"stress die {die.value}"
        )
        event = values.get("event") or hp.STRESS_EVENTS[0]
        details = (
            f"{shown_die.capitalize()} + {' + '.join(check.parts) or '0'} = "
            f"{roll.total} against {hp.STRESS_EASE}."
        )
        project.works.append(
            ProjectWork(
                kind=STRESS,
                name=f"Stress check: {event.lower()}",
                season=values.get("season") or saga.current_season,
                year=values.get("year") or saga.current_year,
                outcome=outcome,
                damage=lost,
                details=details,
            )
        )
        result = (
            "The tower holds."
            if not lost
            else f"The tower loses {lost} damage level{'s' if lost > 1 else ''} "
            f"({hp.damage_left(project)} of {hp.damage_levels(project)} left): a "
            "partial collapse inside, and a story."
        )
        if lost and not hp.damage_left(project):
            result += " [$text-error]No damage levels are left: the tower falls.[/]"
        return notes(details, result)

    return Form(
        f"{STRESS_CHECK}: {escape(project.name)}",
        lambda: stress_fields(saga, project),
        apply,
        live=stress_live(saga, project),
        save_label="Roll",
        inspector="The Tower Under Strain",
        help_id=TOWER_SECTION,
    )


# -- More: Conjure Levels ------------------------------------------------------


def _casters(saga: Saga, covenant: Covenant) -> list[Character]:
    magi = [c for c in _people(saga, covenant) if c.type == "magus"]
    return sorted(magi, key=lambda c: c.name.casefold())


def conjure_fields(
    saga: Saga, covenant: Covenant, project: HermeticProject
) -> list[DialogField]:
    casters = _casters(saga, covenant)
    first = hp.RITUAL_BY_KEY["heights" if hp.stands(project) else "conjuring"]
    return [
        DialogField(
            "ritual",
            "Ritual",
            "select",
            first.key,
            options=[(escape(r.label), r.key) for r in hp.RITUALS],
        ),
        DialogField(
            "caster",
            "Cast by",
            "select",
            casters[0].id if casters else None,
            options=[
                (
                    escape(
                        f"{c.name} (Int {c.characteristics.intelligence:+d}, "
                        f"{hp.FINESSE} {hp.ability_level(c, hp.FINESSE)})"
                    ),
                    c.id,
                )
                for c in casters
            ],
            required=True,
        ),
        DialogField(
            "season", "Season", "select", saga.current_season, options=pairs(SEASONS)
        ),
        DialogField("year", "Year", "int", saga.current_year),
    ]


def _ritual(values: dict[str, Any]) -> hp.Ritual:
    return hp.RITUAL_BY_KEY.get(values.get("ritual") or "", hp.RITUALS[1])


def conjure_live(
    saga: Saga, covenant: Covenant, project: HermeticProject
) -> Callable[[dict[str, Any]], str]:
    def live(values: dict[str, Any]) -> str:
        ritual = _ritual(values)
        caster = saga.character(values.get("caster"))
        failed = hp.failed_finesse(project)
        botch = hp.ritual_botch_dice(ritual, failed)
        lines = [
            f"[b]{ritual.levels} levels[/], {hp.feet(ritual.levels):,} ft, in an "
            "instant" + (", on new foundations." if ritual.foundations else "."),
        ]
        if caster is not None:
            lines.append(
                f"Int {caster.characteristics.intelligence:+d} + {hp.FINESSE} "
                f"{hp.ability_level(caster, hp.FINESSE)} + stress die = "
                f"[b]{hp.finesse_score(caster)} + die[/] against {ritual.ease}: "
                "[$text-success]standard[/] if it reaches, "
                "[$text-warning]shoddy[/] if not."
            )
            spell = "spell_conjuring_the_great_tower"
            if not ritual.foundations:
                spell = "spell_heights_of_the_great_tower"
            if not any(k.spell_id == spell for k in caster.spells_known):
                lines.append(
                    f"[$text-warning]{escape(caster.name)} doesn't know "
                    f"{escape(ritual.name.split(',')[0])}.[/]"
                )
        terms = (
            [] if ritual.foundations else [f"{failed} for levels built on failed rolls"]
        )
        if ritual.extra:
            terms.append(f"{hp.MAGNITUDE_EASE * ritual.extra} for the larger size")
        lines.append(
            f"Botch dice: [b]{botch}[/]"
            + (f" (1 + {' + '.join(terms)})" if terms else "")
            + ". A botch is a story: thousands of tons of stone"
            + (
                "; the foundations won't bear the tower, and it needs a stress "
                "check every year."
                if ritual.foundations
                else "."
            )
        )
        if ritual.foundations and hp.stands(project):
            lines.append("[$text-error]The foundations already stand.[/]")
        place = sites.place(saga, project.place_id)
        where = escape(place.name) if place is not None else "its place (none named)"
        lines += [
            "",
            f"A preternatural tether of 1 for {where}"
            + (
                " (a Magic aura of 1 where there was none)"
                if ritual.foundations
                else " and +1 to this year's aura modifier"
            )
            + " (Realms of Power: Magic pp. 8-11).",
            "[dim]Each magnitude more: x10 levels, +3 to the Ease Factor and to "
            f"the botch dice ({HP} pp. 39-40).[/]",
        ]
        return "\n".join(lines)

    return live


def validate_conjure(
    project: HermeticProject,
) -> Callable[[dict[str, Any]], str | None]:
    def check(values: dict[str, Any]) -> str | None:
        if _ritual(values).foundations and hp.stands(project):
            return "The foundations already stand: cast Heights of the Great Tower."
        return None

    return check


def tether_place(
    saga: Saga, project: HermeticProject, ritual: hp.Ritual, when: str
) -> str:
    """Give the project's place the ritual's tether (and Heights' +1 to
    the year's aura modifier, or Conjuring's aura of 1 where there was
    none); what was done, as a note."""
    place = sites.place(saga, project.place_id)
    if place is None:
        return "No place named for the project: its tether is only noted."
    tether = f"{project.name or 'the tower'}'s ritual, {when} (preternatural 1)"
    before = str(place.details.get("tethers") or "").strip()
    place.details["tethers"] = f"{before}; {tether}" if before else tether
    done = [f"{escape(place.name)}: a preternatural tether of 1"]
    if ritual.foundations:
        if aura_number(place.details.get("aura")) <= 0:
            place.details["aura"] = 1
            place.realm = "Magic"
            done.append("a Magic aura of 1")
    else:
        adjust = aura_number(place.details.get("aura_adjust"))
        place.details["aura_adjust"] = adjust + 1
        done.append("+1 to this year's aura modifier")
    return ", ".join(done) + " (Realms of Power: Magic pp. 8-11)."


def conjure_form(
    saga: Saga, covenant: Covenant, rng: random.Random | None = None
) -> Command:
    """More's Conjure Levels on the tower: the ritual's Finesse roll, its
    levels and their quality kept in the works, and its tether given to
    the place (HP pp. 39-40)."""
    project = hp.shown_project(covenant)
    if project is None:
        return Refuse(CONJURE_LEVELS, "Begin a project first.")
    if not _casters(saga, covenant):
        return Refuse(CONJURE_LEVELS, "No magus of the covenant to cast it.")

    def apply(values: dict[str, Any]) -> list[str]:
        ritual = _ritual(values)
        caster = saga.character(values.get("caster"))
        if caster is None:
            return ["Choose who casts it."]
        failed = hp.failed_finesse(project)
        botch = hp.ritual_botch_dice(ritual, failed)
        die = dice.stress_die(rng or random.Random(), botch, saga=saga)
        roll = dice.Roll(hp.finesse_score(caster), die, ritual.ease)
        quality = STANDARD if roll.succeeded else SHODDY
        season = values.get("season") or saga.current_season
        year = values.get("year") or saga.current_year
        shown_die = (
            f"a botch ({die.botches} of {botch} botch dice)"
            if die.botched
            else f"stress die {die.value}"
        )
        details = (
            f"Int + {hp.FINESSE} {hp.finesse_score(caster)} + {shown_die} = "
            f"{roll.total} against {ritual.ease}: "
            + ("standard." if roll.succeeded else "failed, so shoddy.")
        )
        tether = tether_place(saga, project, ritual, _when(season, year))
        botched = (
            "A botch: a story of thousands of tons of stone"
            + (
                "; the foundations won't bear the tower: a stress check each year."
                if ritual.foundations
                else "."
            )
            if die.botched
            else ""
        )
        project.works.append(
            ProjectWork(
                kind=RITUAL,
                name=f"{ritual.name.split(',')[0]} ({caster.name})",
                season=season,
                year=year,
                levels=ritual.levels,
                quality=quality,
                who=caster.id,
                details=details,
                note=" ".join(part for part in (botched, tether) if part),
            )
        )
        return notes(
            details,
            f"+{ritual.levels} levels ({hp.feet(ritual.levels):,} ft) of "
            f"{quality.lower()} work.",
            "One failed Finesse roll recorded: later castings roll one more botch die."
            if not roll.succeeded
            else "",
            botched,
            tether,
        )

    return Form(
        CONJURE_LEVELS,
        lambda: conjure_fields(saga, covenant, project),
        apply,
        validate=validate_conjure(project),
        live=conjure_live(saga, covenant, project),
        save_label="Cast",
        inspector="The Ritual",
        help_id=TOWER_SECTION,
    )


# -- the tab -------------------------------------------------------------------


PROJECTS_LIST = KindList(
    PROJECTS_SECTION,
    projects_title,
    projects_grid,
    projects_ops,
    project_info,
)


def shown_kind(covenant: Covenant) -> str:
    """The kind of the project the tab shows ("" with none): it picks the
    tab's sections."""
    project = hp.shown_project(covenant)
    return project.kind if project is not None else ""


def menagerie_tab(saga: Saga, covenant: Covenant) -> KindTab:
    """The Projects tab with a Menagerie shown: its projects, the
    menagerie, its beasts and its breedings (menagerie.py)."""
    return KindTab(
        "Projects",
        TAB_ID,
        (PROJECTS_LIST, men.BEASTS_LIST, men.BREEDINGS_LIST),
        blocks=(men.menagerie_block(saga, covenant, tower_edit, PROJECTS_SECTION),),
        icon="covenant",
        panel=men.PANEL,
    )


def projects_tab(saga: Saga, covenant: Covenant) -> KindTab:
    """The covenant's Projects tab: its projects, the one shown's tower,
    works and craft devices; a Menagerie's own sections when one is
    shown."""
    if shown_kind(covenant) == MENAGERIE:
        return menagerie_tab(saga, covenant)
    return KindTab(
        "Projects",
        TAB_ID,
        (
            PROJECTS_LIST,
            KindList(
                PROJECT_WORKS_SECTION,
                works_title,
                works_grid,
                works_ops,
                work_info,
                ledger=works_ledger,
            ),
            KindList(
                PROJECT_DEVICES_SECTION,
                devices_title,
                devices_grid,
                devices_ops,
                device_info,
                ledger=devices_ledger,
            ),
        ),
        blocks=(
            KindBlock(
                TOWER_SECTION,
                tower_title(saga, covenant),
                tower_block_text,
                tower_edit,
                edit_label="Edit Project",
                after=PROJECTS_SECTION,
                facts=tower_facts,
                facts_inline=True,
            ),
        ),
        icon="covenant",
        panel=PANEL,
    )


def covenant_ops(saga: Saga, covenant: Covenant) -> dict[str, SectionOps]:
    """The Projects tab's lists and the tower's Edit, by section."""
    return tab_ops(saga, manors_of(covenant), projects_tab(saga, covenant))
