"""A laboratory's forms: its details, characteristics and features."""

from __future__ import annotations

from typing import Any

from .... import catalog
from .... import laboratories as lab_rules
from ....form_spec import DialogField, covenant_options, pairs
from ....markup import escape
from ....models import (
    FEATURE_VIRTUE_POINTS,
    LAB_CHARACTERISTICS,
    LabCharacteristics,
    LabFeature,
    Laboratory,
    Saga,
)
from ..fields import FieldsDialog


def _lab_identity_fields(saga: Saga, lab: Laboratory) -> list[DialogField]:
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
        DialogField(
            "owner_id",
            "Owner",
            "select",
            lab.owner_id,
            options=_lab_owner_options(saga, lab.owner_id),
            allow_blank=True,
            placeholder="(unassigned)",
        ),
    ]


def _lab_owner_options(saga: Saga, owner_id: str | None) -> list[tuple[str, str]]:
    """The magi, plus the current owner if they aren't one (any more): they
    stay the owner unless changed."""
    options = [(escape(c.name), c.id) for c in saga.characters if c.type == "magus"]
    owner = saga.character(owner_id)
    if owner is not None and owner.type != "magus":
        options.append((f"{escape(owner.name)} ({owner.type})", owner.id))
    return options


def _lab_characteristics_fields(
    characteristics: LabCharacteristics,
) -> list[DialogField]:
    return [
        DialogField(
            name,
            name.replace("_", " ").title(),
            "int",
            getattr(characteristics, name),
        )
        for name in LAB_CHARACTERISTICS
    ]


#: The Feature form's Virtue choice for adding a new Feature Virtue along
#: with the Feature: this prefix, then the Virtue's catalog id.
NEW_FEATURE_VIRTUE = "new:"


def _feature_virtue_options(
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


def _lab_feature_type_dialog(
    lab: Laboratory, feature: LabFeature | None = None
) -> FieldsDialog[tuple[str | None, str]]:
    """First step of adding or editing a Feature: which Feature it is (from
    the catalog, or Custom) and the Feature Virtue it's built on. Gives
    (catalog id or None for Custom, a VirtueFlawInstance id or
    NEW_FEATURE_VIRTUE + a catalog id)."""
    virtue_options = _feature_virtue_options(lab, feature)
    if feature is not None:
        feature_type = feature.feature_id or "custom"
        virtue = feature.virtue_id
    else:
        feature_type = None
        virtue = virtue_options[0][1]  # a free one if there is one
    return FieldsDialog(
        "Add a Feature" if feature is None else "Edit a Feature",
        [
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
        ],
        save_label="Next",
        build=lambda values: (
            None if values["feature_type"] == "custom" else values["feature_type"],
            values["virtue"],
        ),
    )


def _lab_feature_dialog(
    lab: Laboratory,
    feature_id: str | None,
    virtue_vf_id: str,
    feature: LabFeature | None = None,
) -> FieldsDialog[dict[str, Any]]:
    """Second step: the Feature's name, one Specialization per point its
    Virtue gives (the same one twice for 2 points), and -- when the lab has
    a matching Focus Flaw no other Feature holds -- whether it's the Focus,
    with a Specialization per Focus point. Every point must be placed, and
    only on the Specializations the Feature offers."""
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

    return FieldsDialog(
        "Add a Feature" if feature is None else "Edit a Feature",
        fields,
        save_label="Add" if feature is None else "Save",
        build=build,
    )
