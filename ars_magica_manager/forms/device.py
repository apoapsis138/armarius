"""Enchanted Devices & Talismans, independent of how they are drawn: the
device form (its components, Shape & Material bonuses and a talisman's
attunements are list fields), the instilled effect form, and an
Enchanted Devices list's Add, Edit and Delete (commands.SectionOps),
Instill an Effect and Use a Charge.

A device list's rows are each device followed by its effects
(enchanted_devices.device_targets): Edit and Delete act on whichever the
row is."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from typing import Any

from .. import catalog, storage
from .. import enchanted_devices as ed
from ..arts import FORMS, TECHNIQUES
from ..commands import (
    Choice,
    Choose,
    Command,
    Confirm,
    Form,
    Picked,
    Refuse,
    SectionOps,
    notes,
    picked,
)
from ..form_spec import DialogField, ListEditor, attr, description_field, pairs
from ..markup import escape, problem
from ..models import (
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
    ShapeMaterialDef,
    new_instance_id,
)
from ..rules import enchantment, lab_items
from . import experimental_effects

#: The Maker select's value for a maker who isn't one of the saga's
#: characters (their name is typed).
OTHER_MAKER = "_other"

#: A front-end's own chooser for a "picker" field (see form_spec).
Picker = Callable[[Any], Any]


# -- a component --


def component_title(component: DeviceComponent | None) -> str:
    return "Add a component" if component is None else "Edit a component"


def component_fields(component: DeviceComponent | None) -> list[DialogField]:
    """One component of an item: what it is, its Material and its Size."""
    return [
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
                (f"{name} ({base})", name) for name, base in ENCHANT_MATERIALS.items()
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
    ]


def component_live(values: dict[str, Any]) -> str:
    """The component form's live line: its capacity."""
    c = DeviceComponent("", values.get("material") or "", values.get("size") or "")
    return f"Capacity: {enchantment.component_capacity(c)} pawns"


def component_from(values: dict[str, Any]) -> DeviceComponent:
    return DeviceComponent(values["description"], values["material"], values["size"])


def component_form(component: DeviceComponent | None) -> Form:
    return Form(
        component_title(component),
        lambda: component_fields(component),
        picked(component_from),
        live=component_live,
        save_label="Add" if component is None else "Save",
    )


# -- a Shape & Material bonus or an attunement --


def shape_material_bonus(
    entry: ShapeMaterialDef, index: int | None
) -> ShapeMaterialBonus:
    """One row of DE's Shape and Material Bonuses Table as a bonus (a row
    with no bonus, e.g. Living Tree, gives its note and +0)."""
    if index is None:
        return ShapeMaterialBonus(0, entry.note, entry.name)
    bonus, effect = entry.bonuses[index]
    return ShapeMaterialBonus(bonus, effect, entry.name)


def shape_material_choices() -> list[Choice]:
    """Every bonus of DE's table: a row per (shape or material, bonus),
    searchable by either."""
    found: list[Choice] = []
    for entry in catalog.load_shape_material_catalog():
        indices: list[int | None] = [None] if not entry.bonuses else []
        indices += list(range(len(entry.bonuses)))
        for index in indices:
            bonus = shape_material_bonus(entry, index)
            figure = f"{bonus.bonus:+d} " if index is not None else ""
            found.append(
                Choice(
                    f"{escape(bonus.shape)}  [dim]{figure}{escape(bonus.applies_to)}[/]",
                    bonus,
                    f"[dim]{escape('Source: ' + entry.source)}[/]",
                    bonus.applies_to,
                )
            )
    return found


def choose_shape_material(_current: Any = None) -> Choose:
    return Choose(
        "Choose a Shape & Material bonus",
        shape_material_choices,
        Picked,
        empty="(no bonuses)",
    )


def bonus_title(bonus: ShapeMaterialBonus | None, *, attunement: bool) -> str:
    noun = "an attunement" if attunement else "a Shape & Material bonus"
    return f"Add {noun}" if bonus is None else f"Edit {noun}"


def bonus_fields(
    bonus: ShapeMaterialBonus | None,
    *,
    attunement: bool,
    year: int,
    season: str,
    shape_picker: Picker | None = None,
) -> list[DialogField]:
    """A Shape & Material bonus, picked from DE's table or typed; for an
    attunement, also the season and year it was gained."""
    fields = [
        DialogField(
            "catalog",
            "From DE's table",
            "picker",
            None,
            placeholder="(choose a shape or material...)",
            picker=shape_picker,
            choose=choose_shape_material,
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


def bonus_from(values: dict[str, Any], *, attunement: bool) -> ShapeMaterialBonus:
    return ShapeMaterialBonus(
        values["bonus"],
        values["applies_to"],
        values["shape"],
        values.get("year") if attunement else None,
        values.get("season") or "" if attunement else "",
    )


def bonus_form(
    bonus: ShapeMaterialBonus | None,
    *,
    attunement: bool = False,
    year: int = 1220,
    season: str = "Spring",
    shape_picker: Picker | None = None,
) -> Form:
    return Form(
        bonus_title(bonus, attunement=attunement),
        lambda: bonus_fields(
            bonus,
            attunement=attunement,
            year=year,
            season=season,
            shape_picker=shape_picker,
        ),
        picked(lambda values: bonus_from(values, attunement=attunement)),
        save_label="Add" if bonus is None else "Save",
    )


# -- a device --


def holder_options(saga: Saga) -> list[tuple[str, str]]:
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


def device_from_values(
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
        maker_choice if maker_choice and maker_choice != OTHER_MAKER else None
    )
    copy.maker_name = (
        values.get("maker_name") or "" if maker_choice == OTHER_MAKER else ""
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
        "verditius_runes",
        "verditius_craft",
        "description",
    ):
        if key in values:
            setattr(copy, key, values[key])
    if copy.components is None:
        copy.components = []
    return copy


def device_live(saga: Saga, device: EnchantedDevice, values: dict[str, Any]) -> str:
    """The form's live line: the capacity (or charges) as the fields stand,
    and any warning."""
    draft = device_from_values(saga, device, values)
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
            text += f"; its effects use {enchantment.pawns_used(draft)}"
    problems = ed.warnings(saga, draft)
    if problems:
        text += "\n" + "\n".join(problem(line) for line in problems)
    return text


def device_problem(device: EnchantedDevice, values: dict[str, Any]) -> str | None:
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


def device_title(device: EnchantedDevice | None) -> str:
    return "Add an Enchanted Device" if device is None else "Edit an Enchanted Device"


def _list_field(
    key: str,
    label: str,
    items: list[Any],
    title: str,
    row: Callable[[Any], str],
    entry: Callable[[Any], Form],
    **extra: Any,
) -> DialogField:
    """A field holding a small list, edited entry by entry."""
    return DialogField(
        key,
        label,
        "picker",
        list(items),
        display=lambda chosen: "; ".join(row(item) for item in chosen) or "(none)",
        items=ListEditor(row, entry, title),
        **extra,
    )


def _is_type(*kinds: str) -> Callable[[dict[str, Any]], bool]:
    """A field's show_if: shown while the device's Type is one of `kinds`."""
    return lambda values: values.get("type") in kinds


def _device_identity_fields(base: EnchantedDevice) -> list[DialogField]:
    """The device's name and Type, and whether it is a talisman."""
    return [
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
            show_if=_is_type(INVESTED),
            hint=ed.TALISMAN_HINT,
        ),
    ]


def _device_holder_fields(
    saga: Saga, device: EnchantedDevice | None, holder: str | None
) -> list[DialogField]:
    """Who holds the device and who made it (one of the saga's characters,
    or a typed name). `holder` is a new device's default holder."""
    base = device or EnchantedDevice(id="", name="")
    maker_options = [(escape(c.name), c.id) for c in saga.characters] + [
        ("Someone else (type the name)", OTHER_MAKER)
    ]
    if device is None:
        maker_value: str | None = None
        holder_value = holder
    else:
        maker_value = device.maker_id or (OTHER_MAKER if device.maker_name else None)
        holder_value = (
            f"{device.holder_kind}:{device.holder_id}" if device.holder_kind else None
        )
    return [
        DialogField(
            "holder",
            "Holder",
            "select",
            holder_value,
            options=holder_options(saga),
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
            show_if=lambda values: values.get("maker") == OTHER_MAKER,
        ),
    ]


def _device_opening_fields(base: EnchantedDevice) -> list[DialogField]:
    """An invested or lesser device's components and capacity, and how an
    invested one's opening was paid for and how far it is opened."""
    return [
        _list_field(
            "components",
            "Components",
            base.components,
            "Components (Material and Size)",
            ed.component_text,
            component_form,
            show_if=_is_type(INVESTED, LESSER),
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
            show_if=_is_type(INVESTED, LESSER),
        ),
        DialogField(
            "pawns_opened",
            "Pawns opened",
            "int",
            base.pawns_opened,
            show_if=_is_type(INVESTED),
            hint="Only a talisman can be opened a few pawns at a time.",
        ),
    ]


def _device_bonus_fields(
    saga: Saga, base: EnchantedDevice, shape_picker: Picker | None
) -> list[DialogField]:
    """The device's Shape & Material bonuses, and a talisman's attunements."""
    return [
        _list_field(
            "bonuses",
            "Shape & Material",
            base.bonuses,
            "Shape & Material bonuses",
            ed.bonus_text,
            lambda b: bonus_form(b, shape_picker=shape_picker),
            hint=ed.BONUS_HINT,
        ),
        _list_field(
            "attunements",
            "Attunements",
            base.attunements,
            "Talisman attunements",
            lambda b: ed.bonus_text(b, when=True),
            lambda b: bonus_form(
                b,
                attunement=True,
                year=saga.current_year,
                season=saga.current_season,
                shape_picker=shape_picker,
            ),
            show_if=lambda values: (
                values.get("type") == INVESTED and bool(values.get("talisman"))
            ),
            hint="One each time it is opened or given an effect.",
        ),
        DialogField(
            "verditius_runes",
            "Verditius Runes",
            "check",
            base.verditius_runes,
            hint=(
                "Its Verditius maker crafted it in its first season (Verditius "
                "Magic, DE pp. 240-241): his Philosophiae adds to its Shape & "
                "Material bonuses."
            ),
        ),
        DialogField(
            "verditius_craft",
            "Crafted with",
            "text",
            base.verditius_craft,
            show_if=lambda values: bool(values.get("verditius_runes")),
            hint=(
                "The Craft Ability, e.g. Craft: Jeweler (blank: shaped by "
                "magic). The maker adds it to his Lab Totals for the item and "
                "opens it for that many fewer pawns."
            ),
        ),
    ]


def _charged_fields(base: EnchantedDevice) -> list[DialogField]:
    """A charged device's Lab Total, its charges and the objects sharing
    them."""
    return [
        DialogField(
            "lab_total",
            "Lab Total",
            "optint",
            base.lab_total,
            show_if=_is_type(CHARGED),
        ),
        DialogField(
            "charges_made",
            "Charges made (blank = most)",
            "optint",
            base.charges_made,
            show_if=_is_type(CHARGED),
        ),
        DialogField(
            "charges_left",
            "Charges left (blank = all)",
            "optint",
            base.charges_left,
            show_if=_is_type(CHARGED),
        ),
        DialogField(
            "objects",
            "Objects sharing the charges",
            "int",
            base.objects,
            show_if=_is_type(CHARGED),
            hint="e.g. 5 arrows or potions.",
        ),
    ]


def device_fields(
    saga: Saga,
    device: EnchantedDevice | None,
    *,
    holder: str | None = None,
    shape_picker: Picker | None = None,
) -> list[DialogField]:
    """Add or edit an enchanted device (DE ch. 8): its type decides which
    fields show. Components, Shape & Material bonuses and a talisman's
    attunements are list fields. `holder` ("kind:id") is a new device's
    default holder."""
    base = device or EnchantedDevice(id="", name="")
    return [
        *_device_identity_fields(base),
        *_device_holder_fields(saga, device, holder),
        *_device_opening_fields(base),
        *_device_bonus_fields(saga, base, shape_picker),
        *_charged_fields(base),
        description_field(base.description),
    ]


def device_build(
    saga: Saga, device: EnchantedDevice | None, values: dict[str, Any]
) -> EnchantedDevice:
    """The finished device: a new one (with an id), or a copy of `device`
    to put in its place."""
    base = device or EnchantedDevice(id="", name="")
    built = device_from_values(saga, base, values)
    if device is None:
        built.id = storage.generate_unique_id(
            built.name, [d.id for d in saga.enchanted_devices]
        )
    return built


def device_form(
    saga: Saga,
    device: EnchantedDevice | None,
    apply: Callable[[EnchantedDevice], Any],
    *,
    holder: str | None = None,
) -> Form:
    """The device form; `apply` gets the finished device."""
    base = device or EnchantedDevice(id="", name="")
    return Form(
        device_title(device),
        lambda: device_fields(saga, device, holder=holder),
        lambda values: apply(device_build(saga, device, values)),
        validate=lambda values: device_problem(base, values),
        live=lambda values: device_live(saga, base, values),
        save_label="Add" if device is None else "Save",
    )


# -- an instilled effect --


#: The effect's text fields a blank select leaves "" (not None).
_EFFECT_TEXT = frozenset({"technique", "form", "linked_to", "uses_per_day", "expiry"})


def effect_from_values(
    effect: InstilledEffect, values: dict[str, Any]
) -> InstilledEffect:
    """A copy of `effect` with the form's `values` (a hidden field keeps the
    effect's own value, except the ones a checkbox turned off)."""
    copy = replace(effect)
    for key, value in values.items():
        if not hasattr(copy, key) or key == experimental_effects.KEY:
            continue
        setattr(copy, key, "" if value is None and key in _EFFECT_TEXT else value)
    if not copy.restricted_use:
        copy.restricted_to = ""
    if not copy.linked_trigger:
        copy.linked_to = ""
    if copy.expiry == "None":
        copy.first_use_year = None
    experimental_effects.keep(copy, values)
    return copy


def effect_live(
    device: EnchantedDevice, effect: InstilledEffect, values: dict[str, Any]
) -> str:
    """The form's live line: the modified level with its breakdown, the vis,
    and how full the device would be."""
    draft = effect_from_values(effect, values)
    others = [e for e in device.effects if e.id != effect.id]
    trial = replace(device, effects=[*others, draft])
    level = enchantment.modified_level(trial, draft)
    parts = enchantment.level_breakdown(trial, draft)
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
    used = enchantment.pawns_used(trial)
    text += f"; vis {enchantment.vis_cost(trial, draft)}; the device's effects would use {used}"
    room = device.pawns_opened if device.type == INVESTED else None
    if room is not None and used > room:
        text += "\n" + problem(f"More than the {room} pawns opened.")
    return text


def effect_problem(values: dict[str, Any]) -> str | None:
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


def effect_title(device: EnchantedDevice, effect: InstilledEffect | None) -> str:
    return (
        f"Instill an Effect in {escape(device.name)}"
        if effect is None
        else f"Edit an Effect of {escape(device.name)}"
    )


def _effect_check(
    base: InstilledEffect, key: str, label: str, **extra: Any
) -> DialogField:
    """A tick box for the effect's `key`."""
    return DialogField(key, label, "check", getattr(base, key), **extra)


def _effect_design_fields(base: InstilledEffect) -> list[DialogField]:
    """The effect's design: its name, Arts, Range / Duration / Target and
    level."""
    return [
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
            "requisites", "Requisites", "text", base.requisites, placeholder="e.g. Rego"
        ),
        DialogField("range", "Range", "text", base.range, placeholder="e.g. Voice"),
        DialogField(
            "duration", "Duration", "text", base.duration, placeholder="e.g. Mom"
        ),
        DialogField("target", "Target", "text", base.target, placeholder="e.g. Ind"),
        DialogField("level", "Effect level", "int", base.level, hint=ed.LEVEL_HINT),
    ]


def _effect_use_fields(
    device: EnchantedDevice, base: InstilledEffect
) -> list[DialogField]:
    """How often and how strongly it works, and who may use it (uses per
    day only on a device that isn't charged)."""
    fields: list[DialogField] = []
    if device.type != CHARGED:
        fields.append(
            DialogField(
                "uses_per_day",
                "Uses per day",
                "select",
                base.uses_per_day,
                options=[
                    (f"{enchantment.uses_text(uses)} (+{added})", uses)
                    for uses, added in EFFECT_FREQUENCIES.items()
                ],
            )
        )
    return [
        *fields,
        DialogField(
            "penetration",
            "Penetration",
            "int",
            base.penetration,
            hint="+1 level per 2 points.",
        ),
        _effect_check(base, "maintains_concentration", "Maintains concentration (+5)"),
        _effect_check(base, "restricted_use", "Restricted use (+3)"),
        DialogField(
            "restricted_to",
            "Restricted to",
            "text",
            base.restricted_to,
            placeholder="who may use it",
            show_if=lambda values: bool(values.get("restricted_use")),
        ),
    ]


def _effect_trigger_fields(
    device: EnchantedDevice, base: InstilledEffect
) -> list[DialogField]:
    """What sets it off: an environmental, fast or linked trigger (and the
    device's other effect it is linked to), and the trigger itself."""
    linked_options = [
        (escape(enchantment.effect_name(e)) or "(unnamed)", e.id)
        for e in device.effects
        if e.id != base.id
    ]
    return [
        _effect_check(base, "environmental_trigger", "Environmental trigger (+3)"),
        _effect_check(base, "fast_trigger", "Fast trigger (+5)"),
        _effect_check(base, "linked_trigger", "Linked trigger (+3)"),
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


def _effect_state_fields(
    device: EnchantedDevice, base: InstilledEffect
) -> list[DialogField]:
    """Its expiry, whether it is known, how far instilling has got, and
    its modified level and vis when not worked out. Expiry and instilling
    show only on an invested device, vis only on one that isn't charged."""
    invested = device.type == INVESTED
    fields: list[DialogField] = []
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
        _effect_check(
            base,
            "known",
            "Known",
            hint="Untick for a power not yet found by Investigation.",
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
    return fields


def effect_fields(
    device: EnchantedDevice, effect: InstilledEffect | None
) -> list[DialogField]:
    """Add ("Instill an Effect") or edit one of `device`'s effects (DE ch.
    8, Designing the Effect and Effect Modifications). Uses per day,
    Effect Expiry and instilling progress only show on the types that have
    them."""
    base = effect or InstilledEffect(id="")
    return [
        *_effect_design_fields(base),
        *_effect_use_fields(device, base),
        *_effect_trigger_fields(device, base),
        *_effect_state_fields(device, base),
        description_field(base.description),
        experimental_effects.effects_field(base.experimental_effects, base.name),
    ]


def new_effect() -> InstilledEffect:
    return InstilledEffect(id=new_instance_id())


def effect_form(
    device: EnchantedDevice,
    effect: InstilledEffect | None,
    apply: Callable[[InstilledEffect], Any],
) -> Form:
    """The effect form; `apply` gets the finished effect."""
    base = effect or new_effect()
    return Form(
        effect_title(device, effect),
        lambda: effect_fields(device, effect),
        lambda values: apply(effect_from_values(base, values)),
        validate=effect_problem,
        live=lambda values: effect_live(device, base, values),
        save_label="Add" if effect is None else "Save",
    )


# -- an Enchanted Devices list --


def can_take_effect(device: EnchantedDevice) -> bool:
    """An invested device takes any number of effects; the others one."""
    return device.type == INVESTED or not device.effects


def remove_question(device: EnchantedDevice, effect: InstilledEffect | None) -> str:
    if effect is None:
        count = len(device.effects)
        extra = f" and its {count} effect{'' if count == 1 else 's'}" if count else ""
        return f"Delete {escape(device.name)}{extra}?"
    return (
        f"Delete {escape(enchantment.effect_name(effect))} from {escape(device.name)}?"
    )


def remove_target(
    saga: Saga, device: EnchantedDevice, effect: InstilledEffect | None
) -> None:
    """Delete a device (with its effects), or one effect, unlinking any
    effect it triggered."""
    if effect is None:
        saga.enchanted_devices.remove(device)
        lab_items.forget_device(saga, device.id)
        return
    device.effects.remove(effect)
    lab_items.forget_device(saga, device.id, effect.id)
    for other in device.effects:
        if other.linked_to == effect.id:
            other.linked_to = ""


def device_ops(saga: Saga, kind: str, holder_id: str) -> SectionOps:
    """Add, Edit and Delete for the devices `kind` `holder_id` holds: Edit
    and Delete act on the row's device or effect."""

    def targets() -> list[tuple[EnchantedDevice, InstilledEffect | None]]:
        return ed.device_targets(saga, kind, holder_id)

    def add() -> Form:
        return device_form(
            saga, None, saga.enchanted_devices.append, holder=f"{kind}:{holder_id}"
        )

    def edit(row: int) -> Form:
        device, effect = targets()[row]
        if effect is None:

            def replaced(edited: EnchantedDevice) -> None:
                devices = saga.enchanted_devices
                devices[devices.index(device)] = edited

            return device_form(saga, device, replaced)

        def changed(edited: InstilledEffect) -> None:
            device.effects[device.effects.index(effect)] = edited

        return effect_form(device, effect, changed)

    def remove(row: int) -> Confirm:
        device, effect = targets()[row]
        return Confirm(
            remove_question(device, effect),
            lambda: remove_target(saga, device, effect),
        )

    return SectionOps(
        add=add,
        edit=edit,
        remove=remove,
        rows=lambda: [
            enchantment.effect_name(e) if e is not None else d.name
            for d, e in targets()
        ],
    )


def instill(saga: Saga, kind: str, holder_id: str, row: int) -> Command:
    """Instill an Effect in the row's device (or the device of the row's
    effect): a Lesser Enchantment or Charged Item has exactly one."""
    device, _effect = ed.device_targets(saga, kind, holder_id)[row]
    if not can_take_effect(device):
        return Refuse(
            "Instill an Effect",
            f"{escape(device.name)} is a {device.type} and already has its effect.",
        )
    return effect_form(device, None, device.effects.append)


def use_charge(saga: Saga, kind: str, holder_id: str, row: int) -> Command:
    """Take a charge off the row's Charged Item, after asking."""
    device, effect = ed.device_targets(saga, kind, holder_id)[row]
    if effect is not None or device.type != CHARGED:
        return Refuse("Use a Charge", "Only a Charged Item has charges to use.")
    left = ed.charges_left(device)
    if not left:
        return Refuse("Use a Charge", f"{escape(device.name)} has no charges left.")

    def apply() -> list[str]:
        ed.use_charge(device)
        now = ed.charges_left(device)
        return notes(f"{device.name}: {now} charge{'' if now == 1 else 's'} left.")

    return Confirm(
        f"Use a charge of {escape(device.name)}? It has {left} left.",
        apply,
        yes_label="Use a Charge",
    )
