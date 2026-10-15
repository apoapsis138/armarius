"""A laboratory's forms, independent of how they are drawn: the fields each
asks for (form_spec.DialogField lists), what saving one does to the
laboratory, and each list's Add, Edit and Delete (commands.SectionOps).

The terminal draws the same fields in its FieldsDialogs; the desktop runs
the commands. Its raw vis is vis_forms' (a character keeps raw vis too).
Every change to what gives Specialization points (the hand-entered
sources, the Features) goes through laboratories.reconcile_dropped, so a
Specialization it newly makes count arrives turned off if it would break
a cap.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from . import catalog, places
from . import laboratories as lab_rules
from .commands import Act, Command, Confirm, Form, Refuse, SectionOps, delete
from .form_spec import DialogField, attr, covenant_options, description_field, pairs
from .markup import escape
from .models import (
    FEATURE_VIRTUE_POINTS,
    LAB_CHARACTERISTICS,
    LAB_SPECIALIZATIONS,
    ArcaneConnection,
    LabCharacteristics,
    LabFeature,
    Laboratory,
    LabSpecialtyEntry,
    NamedDescription,
    Saga,
    VirtueFlawInstance,
    assign_laboratory_owner,
    new_instance_id,
)

# -- Identity and Characteristics --


def identity_fields(saga: Saga, lab: Laboratory) -> list[DialogField]:
    return [
        DialogField("name", "Name", "text", lab.name, required=True),
        DialogField("location", "Location", "text", lab.location),
        DialogField("aura_modifier", "Aura modifier", "int", lab.aura_modifier),
        DialogField(
            "sanctum_marked",
            "Sanctum marked",
            "check",
            lab.sanctum_marked,
            hint="Its boundary is marked (a circle within a square).",
        ),
        DialogField(
            "covenant_id",
            "Covenant",
            "select",
            lab.covenant_id,
            options=covenant_options(saga),
            allow_blank=True,
            placeholder="(unassigned)",
        ),
        places.where_field(
            saga,
            lab,
            "Place",
            "Only if it is not where its covenant is: a lab built in a regio.",
        ),
        DialogField(
            "owner_id",
            "Owner",
            "select",
            lab.owner_id,
            options=owner_options(saga, lab.owner_id),
            allow_blank=True,
            placeholder="(unassigned)",
        ),
    ]


def owner_options(saga: Saga, owner_id: str | None) -> list[tuple[str, str]]:
    """The magi, plus the current owner if they aren't one (any more): they
    stay the owner unless changed."""
    options = [(escape(c.name), c.id) for c in saga.characters if c.type == "magus"]
    owner = saga.character(owner_id)
    if owner is not None and owner.type != "magus":
        options.append((f"{escape(owner.name)} ({owner.type})", owner.id))
    return options


def apply_identity(saga: Saga, lab: Laboratory, values: dict[str, Any]) -> None:
    """Save the Identity form: the details, and the owner both ways (the
    old owner loses the lab, the new one gains it)."""
    lab.name = values["name"]
    lab.location = values["location"]
    lab.aura_modifier = values["aura_modifier"]
    lab.sanctum_marked = values["sanctum_marked"]
    lab.covenant_id = values["covenant_id"]
    if "where" in values:
        places.put(lab, values["where"])
    assign_laboratory_owner(saga, lab, values["owner_id"])


def identity_form(saga: Saga, lab: Laboratory) -> Form:
    return Form(
        "Edit Laboratory Identity",
        lambda: identity_fields(saga, lab),
        lambda values: apply_identity(saga, lab, values),
    )


def characteristics_fields(characteristics: LabCharacteristics) -> list[DialogField]:
    return [
        DialogField(
            name,
            name.replace("_", " ").title(),
            "int",
            getattr(characteristics, name),
        )
        for name in LAB_CHARACTERISTICS
    ]


def characteristics_form(lab: Laboratory) -> Form:
    """The typed (manual) part of each Characteristic; the Virtues and
    Flaws add theirs on top."""

    def apply(values: dict[str, Any]) -> None:
        lab.characteristics = LabCharacteristics(**values)

    return Form(
        "Edit Laboratory Characteristics (manual value)",
        lambda: characteristics_fields(lab.characteristics),
        apply,
    )


# -- Specialization sources --


def specialty_entry_fields(
    existing: LabSpecialtyEntry | None = None,
) -> list[DialogField]:
    """Points in a laboratory Specialization from a source the app doesn't
    work out itself: which Specialization, how many points (a Flaw's may be
    negative) and where they come from."""
    return [
        DialogField(
            "specialization",
            "Specialization",
            "select",
            attr(existing, "specialization", "") or None,
            options=pairs(LAB_SPECIALIZATIONS),
            required=True,
            allow_blank=True,
            placeholder="(choose an Activity or Art)",
        ),
        DialogField(
            "points",
            "Points",
            "int",
            attr(existing, "points", 1),
            hint="Negative for a penalty (e.g. Undecorated).",
        ),
        DialogField(
            "source",
            "Source",
            "text",
            attr(existing, "source", ""),
            placeholder="e.g. Subterranean",
        ),
    ]


def specialty_entry_problem(values: dict[str, Any]) -> str | None:
    return "Points can't be 0." if values["points"] == 0 else None


def specialty_entry_from(values: dict[str, Any]) -> LabSpecialtyEntry:
    return LabSpecialtyEntry(
        values["specialization"], values["points"], values["source"]
    )


def specialty_entry_name(entry: LabSpecialtyEntry) -> str:
    """ "Terram +1 (Subterranean)", for a confirmation or a row."""
    return " ".join(
        part
        for part in (
            entry.specialization,
            f"{entry.points:+d}" if entry.specialization else "",
            f"({entry.source})" if entry.source else "",
        )
        if part
    )


def _reconciled(lab: Laboratory, change: Callable[[], None]) -> None:
    """Make `change` to what gives the lab Specialization points, then turn
    off any Specialization it newly makes count that would break a cap."""
    counted = lab_rules.counted_specializations(lab)
    change()
    lab_rules.reconcile_dropped(lab, counted)


def toggle_specialization(lab: Laboratory, name: str) -> Act:
    """Turn a Specialization off, or back on (refused when it scores 0 or
    less, or when turning it on would break a cap)."""

    def apply() -> Refuse | None:
        refusal = lab_rules.toggle_specialization(lab, name)
        if refusal is None:
            return None
        return Refuse(f"Turn {escape(name)} on or off", escape(refusal))

    return Act(apply)


def specialty_ops(lab: Laboratory) -> SectionOps:
    """Add, Edit and Delete for the lab's hand-entered Specialization
    sources."""
    entries = lab.specialties

    def form(index: int | None) -> Form:
        existing = entries[index] if index is not None else None

        def apply(values: dict[str, Any]) -> None:
            entry = specialty_entry_from(values)

            def change() -> None:
                if index is None:
                    entries.append(entry)
                else:
                    entries[index] = entry

            _reconciled(lab, change)

        return Form(
            "Add a Specialization source"
            if index is None
            else "Edit a Specialization source",
            lambda: specialty_entry_fields(existing),
            apply,
            validate=specialty_entry_problem,
            save_label="Add" if index is None else "Save",
        )

    def remove(index: int) -> Confirm:
        def change() -> None:
            del entries[index]

        def apply() -> None:
            _reconciled(lab, change)

        name = specialty_entry_name(entries[index])
        return Confirm(f"Delete {escape(name)}?", apply)

    return SectionOps(
        add=lambda: form(None),
        edit=form,
        remove=remove,
        rows=lambda: [specialty_entry_name(e) or "(unnamed)" for e in entries],
    )


# -- Features --

#: The Feature form's Virtue choice for adding a new Feature Virtue along
#: with the Feature: this prefix, then the Virtue's catalog id.
NEW_FEATURE_VIRTUE = "new:"


def feature_virtue_options(
    lab: Laboratory, feature: LabFeature | None
) -> list[tuple[str, str]]:
    """The Feature Virtues a Feature can be built on (the free ones, "#2"
    telling apart two of a kind, the one it's on marked "(current)"), then
    adding a new Lesser or Greater one."""
    free = lab_rules.free_feature_virtues(lab, feature)
    options = []
    for vf in free:
        same = [other for other in free if other.vf_id == vf.vf_id]
        number = f" #{same.index(vf) + 1}" if len(same) > 1 else ""
        current = " (current)" if feature and vf.id == feature.virtue_id else ""
        options.append(
            (f"{lab_rules.tier_word(vf.vf_id)} Feature{number}{current}", vf.id)
        )
    for vf_id, points in FEATURE_VIRTUE_POINTS.items():
        options.append(
            (
                f"New {lab_rules.tier_word(vf_id)} Feature Virtue "
                f"({points} {'point' if points == 1 else 'points'})",
                NEW_FEATURE_VIRTUE + vf_id,
            )
        )
    return options


def feature_type_fields(
    lab: Laboratory, feature: LabFeature | None = None
) -> list[DialogField]:
    """First step of adding or editing a Feature: which Feature it is (from
    the catalog, or Custom) and the Feature Virtue it's built on."""
    virtue_options = feature_virtue_options(lab, feature)
    if feature is not None:
        feature_type = feature.feature_id or "custom"
        virtue = feature.virtue_id
    else:
        feature_type = None
        virtue = virtue_options[0][1]  # a free one if there is one
    return [
        DialogField(
            "feature_type",
            "Feature",
            "select",
            feature_type,
            options=[(f.name, f.id) for f in catalog.load_lab_feature_catalog()]
            + [("Custom (any Activity or Art)", "custom")],
            required=True,
            allow_blank=True,
            placeholder="(choose a Feature)",
        ),
        DialogField(
            "virtue",
            "Built on",
            "select",
            virtue,
            options=virtue_options,
            required=True,
            allow_blank=True,
            placeholder="(choose a Feature Virtue)",
            hint="A Lesser Feature gives 1 point, a Greater Feature 3.",
        ),
    ]


def feature_type_from(values: dict[str, Any]) -> tuple[str | None, str]:
    """(catalog id or None for Custom, a VirtueFlawInstance id or
    NEW_FEATURE_VIRTUE + a catalog id)."""
    return (
        None if values["feature_type"] == "custom" else values["feature_type"],
        values["virtue"],
    )


@dataclass(frozen=True)
class FeatureDetails:
    """The second step of a Feature: its fields, and `build` turning what
    was saved into the Feature's name, allocations, focus and focus
    allocations (a dict of those keys)."""

    fields: list[DialogField]
    build: Callable[[dict[str, Any]], dict[str, Any]]


def feature_details(
    lab: Laboratory,
    feature_id: str | None,
    virtue_vf_id: str,
    feature: LabFeature | None = None,
) -> FeatureDetails:
    """The Feature's name, one Specialization per point its Virtue gives
    (the same one twice for 2 points), and -- when the lab has a matching
    Focus Flaw no other Feature holds -- whether it's the Focus, with a
    Specialization per Focus point. Every point must be placed, and only on
    the Specializations the Feature offers."""
    options = pairs(lab_rules.feature_options(feature_id))
    offered = {value for _, value in options}
    definition = catalog.load_lab_feature_catalog_by_id().get(feature_id or "")
    budget = FEATURE_VIRTUE_POINTS[virtue_vf_id]
    tier = lab_rules.tier_word(virtue_vf_id)

    def placed(grants: list[Any], count: int) -> list[str | None]:
        points = [p for p in lab_rules.points_from_grants(grants) if p in offered]
        return [*points[:count], *[None] * (count - len(points))]

    def point_fields(
        key: str, label: str, values: list[str | None], **extra: Any
    ) -> list[DialogField]:
        return [
            DialogField(
                f"{key}{n}",
                f"{label} {n + 1}" if len(values) > 1 else label,
                "select",
                value,
                options=options,
                required=True,
                allow_blank=True,
                placeholder="(choose a Specialization)",
                **extra,
            )
            for n, value in enumerate(values)
        ]

    fields = [
        DialogField(
            "name",
            "Name",
            "text",
            feature.name if feature else (definition.name if definition else ""),
            required=True,
            placeholder="e.g. Large Brass Cauldron",
        ),
        DialogField(
            "_type",
            "Feature",
            "info",
            f"{definition.name if definition else 'Custom'} ({tier} Feature, "
            f"{budget} {'point' if budget == 1 else 'points'})",
        ),
        *point_fields(
            "point", "Point", placed(feature.allocations if feature else [], budget)
        ),
    ]
    focus_count = 0
    if lab_rules.can_focus(lab, feature, virtue_vf_id):
        focus_count = lab_rules.focus_points(virtue_vf_id)
        was_focus = feature is not None and feature.focus
        fields.append(
            DialogField(
                "focus",
                "Focus",
                "check",
                was_focus,
                hint=(
                    f"The lab's {tier} Focus is built around it: {focus_count} "
                    f"more points, -{1 if tier == 'Lesser' else 2} General "
                    "Quality on activities it doesn't aid."
                ),
            )
        )
        fields += point_fields(
            "focus_point",
            "Focus point",
            placed(
                feature.focus_allocations if was_focus and feature else [], focus_count
            ),
            show_if=lambda values: bool(values.get("focus")),
        )

    def build(values: dict[str, Any]) -> dict[str, Any]:
        focus = bool(values.get("focus"))
        return {
            "name": values["name"],
            "allocations": lab_rules.grants_from_points(
                values[f"point{n}"] for n in range(budget)
            ),
            "focus": focus,
            "focus_allocations": lab_rules.grants_from_points(
                values[f"focus_point{n}"] for n in range(focus_count)
            )
            if focus
            else [],
        }

    return FeatureDetails(fields, build)


def new_feature_virtue_question(lab: Laboratory, vf_id: str) -> str:
    """Asked before a Feature adds a new Feature Virtue to the lab."""
    points = FEATURE_VIRTUE_POINTS[vf_id]
    free = lab_rules.lab_free_virtues(lab, catalog.load_lab_virtue_flaw_catalog_by_id())
    return (
        f"Add a {lab_rules.tier_word(vf_id)} Feature Virtue to the "
        f"lab ({points} {'point' if points == 1 else 'points'}; "
        f"Free Virtues {free:g} → {free - points:g})?"
    )


def save_feature(
    lab: Laboratory,
    feature: LabFeature | None,
    feature_id: str | None,
    virtue_choice: str,
    details: dict[str, Any],
) -> None:
    """Add (`feature` None) or update a Feature from its two steps: the
    `feature_id` Feature (None: Custom) on the Virtue `virtue_choice` (an
    instance id, or NEW_FEATURE_VIRTUE + a catalog id, adding that Virtue
    with it), with FeatureDetails.build's `details`."""
    new_virtue: VirtueFlawInstance | None = None
    if virtue_choice.startswith(NEW_FEATURE_VIRTUE):
        new_virtue = VirtueFlawInstance(
            virtue_choice.removeprefix(NEW_FEATURE_VIRTUE), id=new_instance_id()
        )

    def change() -> None:
        if new_virtue is not None:
            lab.virtues_flaws.append(new_virtue)
        target = feature or LabFeature(id=new_instance_id(), name="")
        target.name = details["name"]
        target.feature_id = feature_id
        target.virtue_id = new_virtue.id if new_virtue else virtue_choice
        target.allocations = details["allocations"]
        target.focus = details["focus"]
        target.focus_allocations = details["focus_allocations"]
        if feature is None:
            lab.features.append(target)

    _reconciled(lab, change)


def feature_ops(lab: Laboratory) -> SectionOps:
    """Add, Edit and Delete for the lab's Features. Adding or editing one
    is two forms: which Feature and the Virtue it's built on -- confirming
    first if that means adding a new Feature Virtue -- then its name,
    points and Focus. Nothing changes until the second form is saved."""

    def flow(feature: LabFeature | None) -> Form:
        title = "Add a Feature" if feature is None else "Edit a Feature"

        def details_form(feature_id: str | None, virtue_choice: str) -> Form:
            if virtue_choice.startswith(NEW_FEATURE_VIRTUE):
                virtue_vf_id = virtue_choice.removeprefix(NEW_FEATURE_VIRTUE)
            else:
                virtue_vf_id = next(
                    vf.vf_id for vf in lab.virtues_flaws if vf.id == virtue_choice
                )
            details = feature_details(lab, feature_id, virtue_vf_id, feature)
            return Form(
                title,
                lambda: details.fields,
                lambda values: save_feature(
                    lab, feature, feature_id, virtue_choice, details.build(values)
                ),
                save_label="Add" if feature is None else "Save",
            )

        def chosen(values: dict[str, Any]) -> Command:
            feature_id, virtue_choice = feature_type_from(values)
            if not virtue_choice.startswith(NEW_FEATURE_VIRTUE):
                return details_form(feature_id, virtue_choice)
            vf_id = virtue_choice.removeprefix(NEW_FEATURE_VIRTUE)
            return Confirm(
                new_feature_virtue_question(lab, vf_id),
                lambda: details_form(feature_id, virtue_choice),
                yes_label="Add",
            )

        return Form(
            title,
            lambda: feature_type_fields(lab, feature),
            chosen,
            save_label="Next",
        )

    def remove(index: int) -> Confirm:
        feature = lab.features[index]
        virtue = lab_rules.feature_virtue(lab, feature)
        keeps = (
            f" Its {lab_rules.tier_word(virtue.vf_id)} Feature Virtue stays, "
            "free for another Feature."
            if virtue
            else ""
        )

        def apply() -> None:
            _reconciled(lab, lambda: lab.features.remove(feature))

        return Confirm(f"Delete {escape(feature.name)}?{keeps}", apply)

    return SectionOps(
        add=lambda: flow(None),
        edit=lambda index: flow(lab.features[index]),
        remove=remove,
        rows=lambda: [f.name or "(unnamed)" for f in lab.features],
    )


# -- Rooms and Equipment & Stores (a name and a description) --


def named_description_fields(
    name_placeholder: str, existing: NamedDescription | None = None
) -> list[DialogField]:
    """A laboratory Room or Equipment & Stores entry: a name and a
    (multi-line) description."""
    return [
        DialogField(
            "name",
            "Name",
            "text",
            attr(existing, "name", ""),
            required=True,
            placeholder=name_placeholder,
        ),
        description_field(attr(existing, "description", "")),
    ]


def named_description_from(values: dict[str, Any]) -> NamedDescription:
    return NamedDescription(**values)


@dataclass(frozen=True)
class NamedList:
    """One of the lab's name + description lists, for the shared Add, Edit
    and Delete."""

    attr: str  # the Laboratory list: "rooms" or "inventory_items"
    noun: str  # "Room"
    plural: str  # "Rooms"
    article: str  # "a Room"
    example: str  # the Name field's placeholder


#: Per sheet section, its name + description list.
NAMED_LISTS = {
    "section-lab-rooms": NamedList("rooms", "Room", "Rooms", "a Room", "e.g. Vault"),
    "section-lab-items": NamedList(
        "inventory_items",
        "Equipment & Stores entry",
        "Equipment & Stores entries",
        "an Equipment & Stores entry",
        "e.g. Silver Mirror",
    ),
}


def named_ops(lab: Laboratory, section: str) -> SectionOps:
    """Add, Edit and Delete for the lab's Rooms or Equipment & Stores, by
    its `section` (one of NAMED_LISTS)."""
    spec = NAMED_LISTS[section]
    entries: list[NamedDescription] = getattr(lab, spec.attr)

    def form(index: int | None) -> Form:
        existing = entries[index] if index is not None else None

        def apply(values: dict[str, Any]) -> None:
            entry = named_description_from(values)
            if index is None:
                entries.append(entry)
            else:
                entries[index] = entry

        verb = "Add" if index is None else "Edit"
        return Form(
            f"{verb} {spec.article}",
            lambda: named_description_fields(spec.example, existing),
            apply,
        )

    return SectionOps(
        add=lambda: form(None),
        edit=form,
        remove=lambda index: delete(entries, index, entries[index].name),
        rows=lambda: [e.name or "(unnamed)" for e in entries],
    )


# -- Arcane Connections --


def connection_fields(existing: ArcaneConnection | None = None) -> list[DialogField]:
    """A laboratory's Arcane Connection: what it connects to, fixed or how
    long it lasts, where it came from, and notes."""
    return [
        DialogField(
            "to",
            "Connection to",
            "text",
            attr(existing, "to", ""),
            required=True,
            placeholder="e.g. a lock of Banna's hair",
        ),
        DialogField("fixed", "Fixed", "check", attr(existing, "fixed", False)),
        DialogField(
            "lasts",
            "Lasts",
            "text",
            attr(existing, "lasts", ""),
            placeholder="e.g. until Summer 1222",
            show_if=lambda v: not v.get("fixed"),
        ),
        DialogField(
            "source",
            "Where from",
            "text",
            attr(existing, "source", ""),
            placeholder="e.g. taken at the Tribunal",
        ),
        description_field(attr(existing, "description", "")),
    ]


def connection_from(
    values: dict[str, Any], existing: ArcaneConnection | None = None
) -> ArcaneConnection:
    """The Arcane Connection a form saved; an edit keeps its id, and when
    it was fixed while it stays fixed."""
    fixed = bool(values["fixed"])
    return ArcaneConnection(
        id=existing.id if existing else new_instance_id(),
        to=values["to"],
        fixed=fixed,
        lasts="" if fixed else values.get("lasts", ""),
        source=values["source"],
        description=values["description"],
        fixed_year=existing.fixed_year if existing and fixed else None,
        fixed_season=existing.fixed_season if existing and fixed else "",
    )


def connection_ops(lab: Laboratory) -> SectionOps:
    """Add, Edit and Delete for the lab's Arcane Connections."""
    entries = lab.arcane_connections

    def form(index: int | None) -> Form:
        existing = entries[index] if index is not None else None

        def apply(values: dict[str, Any]) -> None:
            connection = connection_from(values, existing)
            if index is None:
                entries.append(connection)
            else:
                entries[index] = connection

        return Form(
            "Add an Arcane Connection"
            if index is None
            else "Edit an Arcane Connection",
            lambda: connection_fields(existing),
            apply,
        )

    return SectionOps(
        add=lambda: form(None),
        edit=form,
        remove=lambda index: delete(
            entries, index, f"the Arcane Connection to {entries[index].to}"
        ),
        rows=lambda: [c.to or "(unnamed)" for c in entries],
    )
