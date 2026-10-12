"""Enchanted Devices & Talismans: a device, its components, bonuses and
instilled effects."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from typing import Any

from ... import enchanted_devices as ed
from ... import storage
from ...arts import FORMS, TECHNIQUES
from ...form_spec import DialogField, attr, description_field, pairs
from ...markup import escape, problem
from ...models import (
    CHARGED,
    DEVICE_PAYMENTS,
    DEVICE_TYPES,
    EFFECT_EXPIRIES,
    EFFECT_FREQUENCIES,
    ENCHANT_MATERIALS,
    ENCHANT_SIZES,
    INVESTED,
    LESSER,
    MATERIAL_SIZE_CITATION,
    SEASONS,
    DeviceComponent,
    EnchantedDevice,
    InstilledEffect,
    Saga,
    ShapeMaterialBonus,
    new_instance_id,
)
from ..fields import FieldsDialog
from ..pickers import ShapeMaterialPickerScreen
from ..prompts import _list_field

#: The Maker select's value for a maker who isn't one of the saga's
#: characters (their name is typed).
_OTHER_MAKER = "_other"


def _component_dialog(
    component: DeviceComponent | None,
) -> FieldsDialog[DeviceComponent]:
    """One component of an item: what it is, its Material and its Size."""

    def capacity(values: dict[str, Any]) -> str:
        c = DeviceComponent("", values.get("material") or "", values.get("size") or "")
        return f"Capacity: {ed.component_capacity(c)} pawns"

    return FieldsDialog(
        "Add a component" if component is None else "Edit a component",
        [
            DialogField(
                "description",
                "Description",
                "text",
                attr(component, "description", ""),
                placeholder="e.g. oak staff",
            ),
            DialogField(
                "material",
                "Material",
                "select",
                attr(component, "material", "wood"),
                options=[
                    (f"{name} ({base})", name)
                    for name, base in ENCHANT_MATERIALS.items()
                ],
            ),
            DialogField(
                "size",
                "Size",
                "select",
                attr(component, "size", "small"),
                options=[(f"{name} (x{n})", name) for name, n in ENCHANT_SIZES.items()],
                hint=f"From the {MATERIAL_SIZE_CITATION}.",
            ),
        ],
        live=capacity,
        build=lambda values: DeviceComponent(
            values["description"], values["material"], values["size"]
        ),
    )


def _bonus_fields(
    bonus: ShapeMaterialBonus | None, *, attunement: bool, year: int, season: str
) -> list[DialogField]:
    fields = [
        DialogField(
            "catalog",
            "From DE's table",
            "picker",
            None,
            placeholder="(choose a shape or material...)",
            picker=lambda _current: ShapeMaterialPickerScreen(),
            display=lambda b: f"{b.shape}: {b.bonus:+d} {b.applies_to}",
            fills=lambda values: (
                {
                    "bonus": values["catalog"].bonus,
                    "applies_to": values["catalog"].applies_to,
                    "shape": values["catalog"].shape,
                }
                if values.get("catalog") is not None
                else {}
            ),
        ),
        DialogField("bonus", "Bonus", "int", attr(bonus, "bonus", 0)),
        DialogField(
            "applies_to",
            "Applies to",
            "text",
            attr(bonus, "applies_to", ""),
            required=True,
            placeholder="e.g. project bolt or other missile",
        ),
        DialogField(
            "shape",
            "Shape or material",
            "text",
            attr(bonus, "shape", ""),
            placeholder="e.g. Wand/Staff",
        ),
    ]
    if attunement:
        fields += [
            DialogField(
                "season",
                "Season gained",
                "select",
                attr(bonus, "season", season) or season,
                options=pairs(SEASONS),
            ),
            DialogField("year", "Year gained", "optint", attr(bonus, "year", year)),
        ]
    return fields


def _bonus_dialog(
    bonus: ShapeMaterialBonus | None,
    *,
    attunement: bool = False,
    year: int = 1220,
    season: str = "Spring",
) -> FieldsDialog[ShapeMaterialBonus]:
    """A Shape & Material bonus, picked from DE's table or typed; for an
    attunement, also the season and year it was gained."""
    noun = "an attunement" if attunement else "a Shape & Material bonus"
    return FieldsDialog(
        f"Add {noun}" if bonus is None else f"Edit {noun}",
        _bonus_fields(bonus, attunement=attunement, year=year, season=season),
        build=lambda values: ShapeMaterialBonus(
            values["bonus"],
            values["applies_to"],
            values["shape"],
            values.get("year") if attunement else None,
            values.get("season") or "" if attunement else "",
        ),
    )


def _holder_options(saga: Saga) -> list[tuple[str, str]]:
    """Every character, laboratory and covenant, as "kind:id" values."""
    return [
        *(
            (f"{escape(c.name)} (character)", f"character:{c.id}")
            for c in saga.characters
        ),
        *(
            (f"{escape(lab.name)} (laboratory)", f"laboratory:{lab.id}")
            for lab in saga.laboratories
        ),
        *((f"{escape(c.name)} (covenant)", f"covenant:{c.id}") for c in saga.covenants),
    ]


def _device_from_values(
    saga: Saga, device: EnchantedDevice, values: dict[str, Any]
) -> EnchantedDevice:
    """A copy of `device` with the form's `values` (a hidden field keeps the
    device's own value)."""
    copy = replace(device, effects=list(device.effects))
    holder = values.get("holder") or ""
    kind, _, holder_id = holder.partition(":")
    maker_choice = values.get("maker")
    typed = values.get("type") or device.type
    copy.name = values.get("name", device.name) or ""
    copy.type = typed
    copy.talisman = typed == INVESTED and bool(values.get("talisman", device.talisman))
    copy.holder_kind, copy.holder_id = (kind, holder_id) if holder else (None, None)
    copy.maker_id = (
        maker_choice if maker_choice and maker_choice != _OTHER_MAKER else None
    )
    copy.maker_name = (
        values.get("maker_name") or "" if maker_choice == _OTHER_MAKER else ""
    )
    for key in (
        "components",
        "payment",
        "capacity_override",
        "pawns_opened",
        "bonuses",
        "lab_total",
        "charges_made",
        "charges_left",
        "objects",
        "attunements",
        "description",
    ):
        if key in values:
            setattr(copy, key, values[key])
    if copy.components is None:
        copy.components = []
    return copy


def _device_live(saga: Saga, device: EnchantedDevice, values: dict[str, Any]) -> str:
    """The form's live line: the capacity (or charges) as the fields stand,
    and any warning."""
    draft = _device_from_values(saga, device, values)
    if draft.type == CHARGED:
        most = ed.max_charges(draft)
        text = (
            f"Charges: at most {most} from its Lab Total"
            if most is not None
            else "Charges: worked out once it has a Lab Total and its effect"
        )
    else:
        text = f"Capacity: {ed.capacity_text(saga, draft)}"
        if draft.effects:
            text += f"; its effects use {ed.pawns_used(draft)}"
    problems = ed.warnings(saga, draft)
    if problems:
        text += "\n" + "\n".join(problem(line) for line in problems)
    return text


def _device_problem(device: EnchantedDevice, values: dict[str, Any]) -> str | None:
    kind = values["type"]
    if kind in (LESSER, CHARGED) and len(device.effects) > 1:
        return (
            f"A {kind} has exactly one effect: remove the others before changing "
            "its type."
        )
    for key, label in (
        ("pawns_opened", "Pawns opened"),
        ("capacity_override", "Capacity"),
        ("lab_total", "Lab Total"),
        ("charges_made", "Charges made"),
        ("charges_left", "Charges left"),
    ):
        value = values.get(key)
        if value is not None and value < 0:
            return f"{label} can't be negative."
    if values.get("objects") is not None and values["objects"] < 1:
        return "Objects must be at least 1."
    made, left = values.get("charges_made"), values.get("charges_left")
    if made is not None and left is not None and left > made:
        return "Charges left can't be more than charges made."
    return None


def _enchanted_device_dialog(
    saga: Saga,
    device: EnchantedDevice | None,
    *,
    holder: str | None = None,
) -> FieldsDialog[EnchantedDevice]:
    """Add or edit an enchanted device (DE ch. 8): its type decides which
    fields show. Components, Shape & Material bonuses and a talisman's
    attunements are lists edited in a sub-dialog. `holder` ("kind:id") is a
    new device's default holder. Dismisses with the finished device (a new
    one, or a copy of `device` to put in its place)."""
    base = device or EnchantedDevice(id="", name="")
    maker_options = [(escape(c.name), c.id) for c in saga.characters] + [
        ("Someone else (type the name)", _OTHER_MAKER)
    ]
    if device is None:
        maker_value: str | None = None
        holder_value = holder
    else:
        maker_value = device.maker_id or (_OTHER_MAKER if device.maker_name else None)
        holder_value = (
            f"{device.holder_kind}:{device.holder_id}" if device.holder_kind else None
        )

    def is_type(*kinds: str) -> Callable[[dict[str, Any]], bool]:
        return lambda values: values.get("type") in kinds

    fields = [
        DialogField(
            "name",
            "Name",
            "text",
            base.name,
            required=True,
            placeholder="e.g. Wand of Flames",
        ),
        DialogField("type", "Type", "select", base.type, options=pairs(DEVICE_TYPES)),
        DialogField(
            "talisman",
            "Talisman",
            "check",
            base.talisman,
            show_if=is_type(INVESTED),
            hint=ed.TALISMAN_HINT,
        ),
        DialogField(
            "holder",
            "Holder",
            "select",
            holder_value,
            options=_holder_options(saga),
            required=True,
            allow_blank=True,
            placeholder="(choose who holds it)",
        ),
        DialogField(
            "maker",
            "Maker",
            "select",
            maker_value,
            options=maker_options,
            allow_blank=True,
            placeholder="(unknown: found or bought)",
        ),
        DialogField(
            "maker_name",
            "Maker's name",
            "text",
            base.maker_name,
            show_if=lambda values: values.get("maker") == _OTHER_MAKER,
        ),
        _list_field(
            "components",
            "Components",
            base.components,
            "Components (Material and Size)",
            ed.component_text,
            _component_dialog,
            show_if=is_type(INVESTED, LESSER),
            hint="Normally one; at most the maker's Magic Theory.",
        ),
        DialogField(
            "payment",
            "Opening paid for",
            "select",
            base.payment,
            options=pairs(DEVICE_PAYMENTS),
            show_if=lambda values: (
                values.get("type") == INVESTED
                and len(values.get("components") or []) > 1
            ),
            hint="A one-time choice when it is opened.",
        ),
        DialogField(
            "capacity_override",
            "Capacity (blank = worked out)",
            "optint",
            base.capacity_override,
            show_if=is_type(INVESTED, LESSER),
        ),
        DialogField(
            "pawns_opened",
            "Pawns opened",
            "int",
            base.pawns_opened,
            show_if=is_type(INVESTED),
            hint="Only a talisman can be opened a few pawns at a time.",
        ),
        _list_field(
            "bonuses",
            "Shape & Material",
            base.bonuses,
            "Shape & Material bonuses",
            ed.bonus_text,
            lambda b: _bonus_dialog(b),
            hint=ed.BONUS_HINT,
        ),
        _list_field(
            "attunements",
            "Attunements",
            base.attunements,
            "Talisman attunements",
            lambda b: ed.bonus_text(b, when=True),
            lambda b: _bonus_dialog(
                b,
                attunement=True,
                year=saga.current_year,
                season=saga.current_season,
            ),
            show_if=lambda values: (
                values.get("type") == INVESTED and bool(values.get("talisman"))
            ),
            hint="One each time it is opened or given an effect.",
        ),
        DialogField(
            "lab_total",
            "Lab Total",
            "optint",
            base.lab_total,
            show_if=is_type(CHARGED),
        ),
        DialogField(
            "charges_made",
            "Charges made (blank = most)",
            "optint",
            base.charges_made,
            show_if=is_type(CHARGED),
        ),
        DialogField(
            "charges_left",
            "Charges left (blank = all)",
            "optint",
            base.charges_left,
            show_if=is_type(CHARGED),
        ),
        DialogField(
            "objects",
            "Objects sharing the charges",
            "int",
            base.objects,
            show_if=is_type(CHARGED),
            hint="e.g. 5 arrows or potions.",
        ),
        description_field(base.description),
    ]

    def build(values: dict[str, Any]) -> EnchantedDevice:
        built = _device_from_values(saga, base, values)
        if device is None:
            built.id = storage.generate_unique_id(
                built.name, [d.id for d in saga.enchanted_devices]
            )
        return built

    return FieldsDialog(
        "Add an Enchanted Device" if device is None else "Edit an Enchanted Device",
        fields,
        validate=lambda values: _device_problem(base, values),
        live=lambda values: _device_live(saga, base, values),
        save_label="Add" if device is None else "Save",
        build=build,
    )


def _effect_from_values(
    effect: InstilledEffect, values: dict[str, Any]
) -> InstilledEffect:
    """A copy of `effect` with the form's `values` (a hidden field keeps the
    effect's own value, except the ones a checkbox turned off)."""
    copy = replace(effect)
    for key, value in values.items():
        if not hasattr(copy, key):
            continue
        setattr(copy, key, "" if value is None and key in _EFFECT_TEXT else value)
    if not copy.restricted_use:
        copy.restricted_to = ""
    if not copy.linked_trigger:
        copy.linked_to = ""
    if copy.expiry == "None":
        copy.first_use_year = None
    return copy


#: The effect's text fields a blank select leaves "" (not None).
_EFFECT_TEXT = frozenset({"technique", "form", "linked_to", "uses_per_day", "expiry"})


def _effect_live(
    device: EnchantedDevice, effect: InstilledEffect, values: dict[str, Any]
) -> str:
    """The form's live line: the modified level with its breakdown, the vis,
    and how full the device would be."""
    draft = _effect_from_values(effect, values)
    others = [e for e in device.effects if e.id != effect.id]
    trial = replace(device, effects=[*others, draft])
    level = ed.modified_level(trial, draft)
    parts = ed.level_breakdown(trial, draft)
    breakdown = " + ".join(
        [str(parts[0][1]), *(f"{n} ({label})" for label, n in parts[1:])]
    )
    text = f"Modified level: {level}" + (
        f" = {breakdown}"
        if len(parts) > 1 and draft.modified_level_override is None
        else ""
    )
    if device.type == CHARGED:
        return text
    used = ed.pawns_used(trial)
    text += f"; vis {ed.vis_cost(trial, draft)}; the device's effects would use {used}"
    room = device.pawns_opened if device.type == INVESTED else None
    if room is not None and used > room:
        text += "\n" + problem(f"More than the {room} pawns opened.")
    return text


def _effect_problem(values: dict[str, Any]) -> str | None:
    penetration = values.get("penetration")
    if penetration is not None and (penetration < 0 or penetration % 2):
        return "Penetration must be a whole even number (+1 level per 2 points)."
    for key, label in (
        ("level", "Effect level"),
        ("instilling_progress", "Instilling progress"),
        ("modified_level_override", "Modified level"),
        ("vis_override", "Vis"),
    ):
        value = values.get(key)
        if value is not None and value < 0:
            return f"{label} can't be negative."
    return None


def _instilled_effect_dialog(
    device: EnchantedDevice, effect: InstilledEffect | None
) -> FieldsDialog[InstilledEffect]:
    """Add ("Instill Effect") or edit one of `device`'s effects (DE ch. 8,
    Designing the Effect and Effect Modifications). Uses per day, Effect
    Expiry and instilling progress only show on the types that have them.
    Dismisses with the finished effect."""
    base = effect or InstilledEffect(id=new_instance_id())
    invested = device.type == INVESTED
    linked_options = [
        (escape(ed.effect_name(e)) or "(unnamed)", e.id)
        for e in device.effects
        if e.id != base.id
    ]

    def check(key: str, label: str, **extra: Any) -> DialogField:
        return DialogField(key, label, "check", getattr(base, key), **extra)

    fields = [
        DialogField(
            "name",
            "Name",
            "text",
            base.name,
            required=True,
            placeholder="e.g. Pilum of Fire",
        ),
        DialogField(
            "technique",
            "Technique",
            "select",
            base.technique,
            options=pairs(TECHNIQUES),
            allow_blank=True,
            placeholder="(none)",
        ),
        DialogField(
            "form",
            "Form",
            "select",
            base.form,
            options=pairs(FORMS),
            allow_blank=True,
            placeholder="(none)",
        ),
        DialogField(
            "requisites",
            "Requisites",
            "text",
            base.requisites,
            placeholder="e.g. Rego",
        ),
        DialogField("range", "Range", "text", base.range, placeholder="e.g. Voice"),
        DialogField(
            "duration", "Duration", "text", base.duration, placeholder="e.g. Mom"
        ),
        DialogField("target", "Target", "text", base.target, placeholder="e.g. Ind"),
        DialogField("level", "Effect level", "int", base.level, hint=ed.LEVEL_HINT),
    ]
    if device.type != CHARGED:
        fields.append(
            DialogField(
                "uses_per_day",
                "Uses per day",
                "select",
                base.uses_per_day,
                options=[
                    (f"{ed.uses_text(uses)} (+{added})", uses)
                    for uses, added in EFFECT_FREQUENCIES.items()
                ],
            )
        )
    fields += [
        DialogField(
            "penetration",
            "Penetration",
            "int",
            base.penetration,
            hint="+1 level per 2 points.",
        ),
        check("maintains_concentration", "Maintains concentration (+5)"),
        check("restricted_use", "Restricted use (+3)"),
        DialogField(
            "restricted_to",
            "Restricted to",
            "text",
            base.restricted_to,
            placeholder="who may use it",
            show_if=lambda values: bool(values.get("restricted_use")),
        ),
        check("environmental_trigger", "Environmental trigger (+3)"),
        check("fast_trigger", "Fast trigger (+5)"),
        check("linked_trigger", "Linked trigger (+3)"),
        DialogField(
            "linked_to",
            "Triggered by",
            "select",
            base.linked_to or None,
            options=linked_options,
            allow_blank=True,
            placeholder="(choose the effect)",
            show_if=lambda values: bool(values.get("linked_trigger")),
        ),
        DialogField(
            "trigger",
            "Trigger",
            "text",
            base.trigger,
            placeholder="the word, gesture or condition",
        ),
    ]
    if invested:
        fields += [
            DialogField(
                "expiry",
                "Effect Expiry",
                "select",
                base.expiry,
                options=pairs(EFFECT_EXPIRIES),
            ),
            DialogField(
                "first_use_year",
                "Year of first use",
                "optint",
                base.first_use_year,
                show_if=lambda values: values.get("expiry") not in (None, "None"),
            ),
        ]
    fields.append(
        check(
            "known", "Known", hint="Untick for a power not yet found by Investigation."
        )
    )
    if invested:
        fields.append(
            DialogField(
                "instilling_progress",
                "Instilling (blank = finished)",
                "optint",
                base.instilling_progress,
            )
        )
    fields.append(
        DialogField(
            "modified_level_override",
            "Modified level (blank = auto)",
            "optint",
            base.modified_level_override,
        )
    )
    if device.type != CHARGED:
        fields.append(
            DialogField(
                "vis_override",
                "Vis (blank = worked out)",
                "optint",
                base.vis_override,
            )
        )
    fields.append(description_field(base.description))
    return FieldsDialog(
        f"Instill an Effect in {escape(device.name)}"
        if effect is None
        else f"Edit an Effect of {escape(device.name)}",
        fields,
        validate=_effect_problem,
        live=lambda values: _effect_live(device, base, values),
        save_label="Add" if effect is None else "Save",
        build=lambda values: _effect_from_values(base, values),
    )
