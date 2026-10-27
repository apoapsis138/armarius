"""More's Shape the Land on a covenant's Income: plan an island raised by
magic (its wall, fill, surface life and wards), see the Rituals it needs
and what the new land is worth, and settle manors on it once it stands --
no UI in here. The rules and their pages are rules.land_shaping's
(Transforming Mythic Europe pp. 54-77); the Rituals are cast in a season
(rules.season_work.land_shaping)."""

from __future__ import annotations

from typing import Any

from .. import manors
from ..commands import Choice, Choose, Command, Form, notes
from ..form_spec import DialogField, pairs
from ..markup import BULLET, escape
from ..models import Covenant, CovenantDiaryEntry, LandProject, Saga, new_instance_id
from ..models.land_shaping import (
    FILLS,
    RING,
    SHAPES,
    SOIL,
    SOLID,
    STONE,
    STONE_FILL,
    WALL_MATERIALS,
)
from ..rules import land_shaping as ls

TITLE = "Shape the Land"
SETTLE = "Settle the New Land"
HELP_ID = "land-shaping"
#: The Diary category its entries go under.
CATEGORY = "Improvements"

#: The Choose's value for a new project.
NEW = "__new__"


def _feature_key(key: str) -> str:
    return f"feature_{key}"


def _spell_key(index: int) -> str:
    return f"spell_{index}"


def _not_solid(values: dict[str, Any]) -> bool:
    return values.get("shape") != SOLID


def project_fields(project: LandProject | None) -> list[DialogField]:
    """What a land project asks: its shape and size, wall, fill, surface
    life, wards and land."""
    p = project or LandProject("", "")
    found = [
        DialogField("name", "Name", "text", p.name, required=True),
        DialogField(
            "shape",
            "Shape",
            "select",
            p.shape,
            options=pairs(SHAPES),
            hint="A circular wall serves Circle, Ring and Boundary spells "
            "(TME p. 55); a square maps easily and its walls make quays (p. 56).",
        ),
        DialogField(
            "across_miles",
            "Across (miles)",
            "optfloat",
            p.across_miles,
            required=True,
            hint="The diameter, or a square's side; a solid cylinder is a few "
            "hundred paces (TME pp. 55-56).",
        ),
        DialogField(
            "wall_height",
            "Wall height (paces)",
            "int",
            p.wall_height,
            hint=f"{ls.WALL_HEIGHT} for the southern North Sea, "
            f"{ls.TALL_WALL_HEIGHT} for a tall cylinder in deep water (TME pp. 54-55).",
        ),
        DialogField(
            "wall_thickness",
            "Wall thickness (paces)",
            "int",
            p.wall_thickness,
            show_if=_not_solid,
            hint=f"{ls.WALL_THICKNESS}: thinner may crack (TME p. 54).",
        ),
        DialogField(
            "wall_material",
            "Wall of",
            "select",
            p.wall_material,
            options=pairs(WALL_MATERIALS),
            hint="Base metal is two magnitudes harder and a cubic foot an "
            "Individual; precious metal three more (TME p. 58; DE p. 359).",
        ),
    ]
    for feature in ls.WALL_FEATURES:
        found.append(
            DialogField(
                _feature_key(feature.key),
                f"{feature.label} (+{feature.magnitudes})",
                "check",
                feature.key in p.features,
                hint=feature.note,
            )
        )
    found += [
        DialogField(
            "unnatural",
            "An unnatural material (Muto requisite, +1)",
            "check",
            p.unnatural,
            hint="Burning or self-healing stone needs further requisites (TME p. 58).",
        ),
        DialogField(
            "cap_complexity",
            "Cap complexity at three magnitudes",
            "check",
            p.cap_complexity,
            hint="The troupe's option (TME p. 56).",
        ),
        DialogField(
            "fill",
            "Fill of",
            "select",
            p.fill,
            options=pairs(FILLS),
            show_if=_not_solid,
            hint="Soil over rubbish, two paces of topsoil, or clay (TME p. 59); "
            "stone is three magnitudes harder.",
        ),
        DialogField(
            "mixed_stone",
            "Several kinds of stone (+1)",
            "check",
            p.mixed_stone,
            show_if=lambda v: _not_solid(v) and v.get("fill") == STONE_FILL,
            hint="Soapstone, marble, tin ore... (TME p. 60).",
        ),
        DialogField(
            "slope",
            "An ablative slope at the wall's foot",
            "check",
            p.slope,
            show_if=_not_solid,
            hint="Earth as much as the wall, against the waves (TME p. 56).",
        ),
        DialogField(
            "grassland",
            "Grassland over the island",
            "check",
            p.grassland,
            hint="Creation of Verdant Grassland (TME p. 62).",
        ),
        DialogField(
            "forest_trees",
            "Forest (mature trees)",
            "int",
            p.forest_trees,
            hint="The Creation of a Forest: 1,000 trees at +3 size, ten times as "
            "many each magnitude (TME p. 62).",
        ),
        DialogField(
            "aegis",
            "Aegis of the Hearth's level (0: none)",
            "int",
            p.aegis,
            hint="Over the whole island, raised for its size; it may keep "
            "faeries and their vis away (TME p. 71).",
        ),
    ]
    for index, spell in enumerate(ls.BOUNDARY_SPELLS):
        found.append(
            DialogField(
                _spell_key(index),
                f"{spell.name} ({spell.technique[:2]}{spell.form[:2]} "
                f"{spell.book_level})",
                "check",
                spell.name in p.boundary_spells,
                hint=f"{spell.what} (TME p. {spell.page}).",
            )
        )
    found += [
        DialogField(
            "fertile",
            "Highly fertile land",
            "check",
            p.fertile,
            hint="A manor needs a third less land (TME p. 62).",
        ),
        DialogField("notes", "Notes", "text", p.notes),
    ]
    if project is not None:
        found.append(
            DialogField(
                "abandon",
                "Abandon this project",
                "check",
                False,
                hint="It leaves the covenant; Rituals already cast stay in the "
                "magi's records.",
            )
        )
    return found


def _int(value: Any, default: int = 0) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else default


def project_from(values: dict[str, Any], project: LandProject) -> LandProject:
    """`project` with the form's values set (a copy: the saga is
    untouched)."""
    across = values.get("across_miles")
    shape = str(values.get("shape") or RING)
    return LandProject(
        id=project.id,
        name=str(values.get("name") or "").strip(),
        shape=shape,
        across_miles=float(across)
        if isinstance(across, (int, float)) and across > 0
        else project.across_miles,
        wall_height=max(1, _int(values.get("wall_height"), ls.WALL_HEIGHT)),
        wall_thickness=max(1, _int(values.get("wall_thickness"), ls.WALL_THICKNESS)),
        wall_material=str(values.get("wall_material") or STONE),
        features=[f.key for f in ls.WALL_FEATURES if values.get(_feature_key(f.key))],
        unnatural=bool(values.get("unnatural")),
        cap_complexity=bool(values.get("cap_complexity")),
        fill=str(values.get("fill") or SOIL),
        mixed_stone=bool(values.get("mixed_stone")),
        slope=bool(values.get("slope")) and shape != SOLID,
        grassland=bool(values.get("grassland")),
        forest_trees=max(0, _int(values.get("forest_trees"))),
        aegis=max(0, _int(values.get("aegis"))),
        boundary_spells=[
            s.name
            for i, s in enumerate(ls.BOUNDARY_SPELLS)
            if values.get(_spell_key(i))
        ],
        fertile=bool(values.get("fertile")),
        manors_settled=project.manors_settled,
        notes=str(values.get("notes") or "").strip(),
    )


def project_lines(saga: Saga, project: LandProject) -> list[str]:
    """What the design comes to, plain: its Rituals, their vis and time,
    the land and its worth, the Boundary and the tethers."""
    found = ls.works(project)
    cast = ls.cast_count(saga, project)
    said = []
    for index, work in enumerate(found):
        done = " (cast)" if index < cast else ""
        said.append(
            f"{work.name}: {work.arts} {work.level} Ritual, {work.pawns} pawn(s), "
            f"{work.minutes} minutes; {work.what}{done}."
        )
    pawns = sum(w.pawns for w in found)
    minutes = sum(w.minutes for w in found)
    said.append(
        f"In all {pawns} pawn(s) of vis and {minutes / 60:g} hours of casting "
        "(DE p. 213)."
    )
    area = ls.project_acres(project)
    made = ls.manors_supported(area, fertile=project.fertile)
    low, high = ls.FAMILIES
    said.append(
        f"The land: {area:,.0f} acres, {made:,} manor(s) of "
        f"{ls.manor_acres(project.fertile)} acres, {ls.yearly_pounds(made):,} "
        f"pounds a year before expenses, {low * made:,} to {high * made:,} "
        "peasant families (TME p. 62)."
    )
    extra = ls.island_boundary(project)
    said.append(
        f"A Boundary spell over the island adds {extra} magnitude(s) for its "
        "size (DE p. 310); a ward is its level + 35 + those (TME p. 71)."
    )
    tethers = ls.tethers(project)
    if tethers:
        said.append(
            "Tethers for its aura: "
            + "; ".join(f"{name} (preternatural {n})" for name, n in tethers)
            + " (RoP: Magic p. 10)."
        )
    else:
        said.append(
            "None of its Rituals is great enough to leave a tether: an aura "
            "needs natural beauty, ancient structures or magical beings "
            "(TME pp. 64-67)."
        )
    if cast:
        said.append(f"{cast} of its {len(found)} Ritual(s) cast so far.")
    return said


def _live(saga: Saga, project: LandProject):
    def live(values: dict[str, Any]) -> str:
        draft = project_from(values, project)
        return "\n".join(
            f"{BULLET} {escape(line)}" for line in project_lines(saga, draft)
        )

    return live


def _problem(saga: Saga, project: LandProject, values: dict[str, Any]) -> str | None:
    name = str(values.get("name") or "").strip()
    if not name:
        return "Name the project."
    across = values.get("across_miles")
    if not isinstance(across, (int, float)) or across <= 0:
        return "Say how many miles across it is."
    found = ls.find_project(saga, name)
    if found is not None and found[1].id != project.id:
        return f"A land project is already called {name}."
    return None


def _diary(saga: Saga, covenant: Covenant, name: str, text: str) -> None:
    covenant.diary.append(
        CovenantDiaryEntry(
            saga.current_year,
            saga.current_season,
            name,
            text,
            category=CATEGORY,
        )
    )


def _save(
    saga: Saga, covenant: Covenant, project: LandProject | None, values: dict[str, Any]
) -> list[str]:
    old = project or LandProject(new_instance_id(), "")
    if project is not None and values.get("abandon"):
        covenant.land_projects.remove(project)
        _diary(
            saga,
            covenant,
            f"Abandoned: {project.name}",
            "The land project is set aside.",
        )
        return notes(f"{project.name} is abandoned.")
    made = project_from(values, old)
    if project is None:
        covenant.land_projects.append(made)
    else:
        covenant.land_projects[covenant.land_projects.index(project)] = made
    found = ls.works(made)
    _diary(
        saga,
        covenant,
        f"Land project: {made.name}",
        f"{len(found)} Ritual(s), {sum(w.pawns for w in found)} pawn(s) of vis; "
        f"{ls.project_acres(made):,.0f} acres when done.",
    )
    return notes(
        f"{made.name}: {len(found)} Ritual(s) to cast.",
        "A magus casts them in a season of Shape the land.",
    )


def project_form(saga: Saga, covenant: Covenant, project: LandProject | None) -> Form:
    draft = project or LandProject("", "")
    return Form(
        f"{TITLE}: {escape(project.name) if project else 'a new project'}",
        lambda: project_fields(project),
        lambda values: _save(saga, covenant, project, values),
        validate=lambda values: _problem(saga, draft, values),
        live=_live(saga, draft),
        help_id=HELP_ID,
        inspector="The Rituals and the Land",
    )


# -- settling the new land --


def settle_fields(saga: Saga, project: LandProject) -> list[DialogField]:
    left = ls.manors_left(saga, project)
    return [
        DialogField(
            "count",
            f"Manors to settle (of {left} left)",
            "int",
            min(left, 10),
            required=True,
        ),
        DialogField("prefix", "Named", "text", project.name, required=True),
    ]


def settle_live(project: LandProject):
    def live(values: dict[str, Any]) -> str:
        count = _int(values.get("count"))
        acres = ls.manor_acres(project.fertile)
        return (
            f"{BULLET} {count} manor(s) of {acres} acres, held as allods: "
            f"{ls.yearly_pounds(count):,} pounds a year before expenses (TME p. "
            "62; LoM p. 72), shown beside the covenant's Agriculture source on "
            "Manors."
        )

    return live


def _settle_problem(
    saga: Saga, project: LandProject, values: dict[str, Any]
) -> str | None:
    count = _int(values.get("count"))
    left = ls.manors_left(saga, project)
    if count < 1:
        return "Settle at least one manor."
    if count > left:
        return f"The land has room for {left} more manor(s)."
    if not str(values.get("prefix") or "").strip():
        return "Name the manors."
    return None


def settle(
    saga: Saga, covenant: Covenant, project: LandProject, values: dict[str, Any]
) -> list[str]:
    count = _int(values.get("count"))
    prefix = str(values.get("prefix") or project.name).strip()
    acres = ls.manor_acres(project.fertile)
    listed = manors.manor_list(manors.manors_of(covenant))
    first = project.manors_settled + 1
    for number in range(first, first + count):
        listed.append(
            {
                "name": f"{prefix} {number}",
                "acres": acres,
                "allod": True,
                "note": f"Land made by magic ({project.name}).",
            }
        )
    project.manors_settled += count
    text = (
        f"{count} manor(s) settled on {project.name}: "
        f"{ls.yearly_pounds(count):,} pounds a year before expenses."
    )
    _diary(saga, covenant, f"Settled: {project.name}", text)
    return notes(text, "Set its Agriculture source's income on the Income tab.")


def settle_form(saga: Saga, covenant: Covenant, project: LandProject) -> Form:
    return Form(
        f"{SETTLE}: {escape(project.name)}",
        lambda: settle_fields(saga, project),
        lambda values: settle(saga, covenant, project, values),
        validate=lambda values: _settle_problem(saga, project, values),
        live=settle_live(project),
        save_label="Settle",
        help_id=HELP_ID,
    )


# -- More's Shape the Land --


def _choices(saga: Saga, covenant: Covenant) -> list[Choice]:
    found = [Choice("A new land project", (NEW, None))]
    for project in covenant.land_projects:
        works = ls.works(project)
        cast = ls.cast_count(saga, project)
        found.append(
            Choice(
                escape(project.name),
                ("edit", project),
                escape(f"{min(cast, len(works))} of {len(works)} Ritual(s) cast."),
            )
        )
        left = ls.manors_left(saga, project)
        if left:
            found.append(
                Choice(
                    f"Settle {escape(project.name)}",
                    ("settle", project),
                    escape(f"Room for {left:,} more manor(s)."),
                )
            )
    return found


def shape_form(saga: Saga, covenant: Covenant) -> Command:
    """More's Shape the Land: a new project, one to change, or the new
    land to settle."""
    if not covenant.land_projects:
        return project_form(saga, covenant, None)

    def chosen(value: tuple[str, LandProject | None]) -> Command:
        what, project = value
        if what == "settle" and project is not None:
            return settle_form(saga, covenant, project)
        return project_form(saga, covenant, project)

    return Choose(TITLE, lambda: _choices(saga, covenant), chosen, help_id=HELP_ID)
