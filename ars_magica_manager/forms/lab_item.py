"""A laboratory's magic items, independent of how they are drawn: the Magic
Items list's Add, Edit and Delete (commands.SectionOps), each the steps of
one effect of a device kept in the lab (rules.lab_items).

Adding or editing one is two steps. The first chooses the device's effect,
how the item is installed (a Magic Item, a very large one, or an
Enchantment of the lab itself) and what it gives. The second is either the
laboratory Virtue or Flaw it duplicates (and what that names), or the
Specialization and Characteristic points its level buys, which may not
cost more levels than the effect has. Nothing changes until the last step
is saved.

Installing a magic item while a laboratory is being set up (`install`) may
first make the device, and its effect, kept in the lab.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from .. import catalog, sourcebooks
from .. import laboratories as lab_rules
from ..commands import Choice, Choose, Command, Confirm, Form, Refuse, SectionOps, Then
from ..form_spec import DialogField, pairs
from ..markup import escape
from ..models import (
    FEATURE_VIRTUE_POINTS,
    FOCUS_FLAWS,
    ITEM_DEVICE_PARAM,
    ITEM_SIZE_PARAM,
    ITEM_VIRTUES,
    LAB_CHARACTERISTICS,
    LAB_SPECIALIZATIONS,
    VERY_LARGE,
    EnchantedDevice,
    InstilledEffect,
    LabCharacteristicGrant,
    LabItemBenefit,
    Laboratory,
    LabSpecialtyGrant,
    LabVirtueFlawDef,
    Saga,
    VirtueFlawInstance,
    new_instance_id,
)
from ..rules import enchantment, lab_items
from . import device as device_forms
from .virtue import lab_needs_input, lab_param_fields, lab_params_from

#: How an item is installed: (choice, label).
ITEM = "item"
LARGE = "large"
ENCHANTMENT = "enchantment"
INSTALLED_AS: tuple[tuple[str, str], ...] = (
    ("Magic Item (a Free Virtue)", ITEM),
    ("Magic Item, very large (a Minor Virtue: takes space)", LARGE),
    ("Enchantment of the laboratory itself (a Free Virtue)", ENCHANTMENT),
)
#: What an effect gives.
GRANTS = "virtue"
POINTS = "points"
GIVES: tuple[tuple[str, str], ...] = (
    ("A laboratory Virtue or Flaw it duplicates (no space)", GRANTS),
    ("Points bought by its level", POINTS),
)
#: How many Specializations and Characteristics one effect's form offers.
SPECIALIZATION_ROWS = 3
CHARACTERISTIC_ROWS = 2
#: A device and one of its effects, as one select value.
_SEPARATOR = "/"


def characteristic_label(characteristic: str) -> str:
    return characteristic.replace("_", " ").title()


@dataclass
class ItemChoice:
    """The first step's answers: which effect, how the item is installed,
    and what it gives."""

    device_id: str
    effect_id: str
    installed: str
    gives: str


@dataclass
class ItemGives:
    """The second step's answers: the Virtue or Flaw granted, or the
    points bought."""

    granted: VirtueFlawInstance | None = None
    specializations: list[LabSpecialtyGrant] = field(default_factory=list)
    characteristics: list[LabCharacteristicGrant] = field(default_factory=list)


# -- the first step --


def effect_options(
    saga: Saga, lab: Laboratory, benefit: LabItemBenefit | None
) -> list[tuple[str, str]]:
    """Each effect of each device kept in the lab, "Rowan Lectern: Steady
    Page (level 20)", its value the device and effect ids."""
    options = []
    for device in lab_items.held_devices(saga, lab):
        for effect in device.effects:
            level = enchantment.modified_level(device, effect)
            options.append(
                (
                    f"{device.name}: {enchantment.effect_name(effect)} (level {level})",
                    effect_value(device.id, effect.id),
                )
            )
    return options


def installed_as(lab: Laboratory, device_id: str) -> str:
    """How the device is installed now (ITEM for a device not yet)."""
    host = lab_items.item_virtue(lab, device_id)
    if host is None or host.vf_id == lab_items.MAGIC_ITEM:
        return LARGE if host is not None and lab_items.is_very_large(host) else ITEM
    return ENCHANTMENT


def effect_value(device_id: str, effect_id: str) -> str:
    """A device's effect as the Effect field's value."""
    return f"{device_id}{_SEPARATOR}{effect_id}"


def choice_fields(
    saga: Saga,
    lab: Laboratory,
    benefit: LabItemBenefit | None,
    chosen: str | None = None,
) -> list[DialogField]:
    """The first step: the effect, how its item is installed, and what it
    gives. `chosen` (effect_value) is a new one's effect, when known."""
    current = effect_value(benefit.device_id, benefit.effect_id) if benefit else chosen
    gives = POINTS if benefit is not None and not benefit.granted_id else GRANTS
    return [
        DialogField(
            "effect",
            "Effect",
            "select",
            current,
            options=effect_options(saga, lab, benefit),
            required=True,
            allow_blank=True,
            placeholder="(choose a device's effect)",
            hint="The devices kept in this laboratory.",
        ),
        DialogField(
            "installed",
            "Installed as",
            "select",
            installed_as(lab, benefit.device_id) if benefit else ITEM,
            options=list(INSTALLED_AS),
            required=True,
            hint="One Virtue for each item, shared by all its effects.",
        ),
        DialogField(
            "gives",
            "Gives",
            "select",
            gives,
            options=list(GIVES),
            required=True,
            hint="Points: 1 Specialization point per 10 levels, "
            "1 Characteristic point per 20.",
        ),
    ]


def choice_from(values: dict[str, Any]) -> ItemChoice:
    device_id, _, effect_id = str(values["effect"]).partition(_SEPARATOR)
    return ItemChoice(device_id, effect_id, values["installed"], values["gives"])


# -- the second step: a Virtue or Flaw it duplicates --


def grantable(entry: LabVirtueFlawDef) -> bool:
    """Whether an item's effect may grant `entry`: not a Feature Virtue or
    Focus Flaw (an item made into a Feature pays for it as usual), nor a
    Magic Item or Enchantment itself."""
    return (
        entry.id not in FEATURE_VIRTUE_POINTS
        and entry.id not in FOCUS_FLAWS
        and entry.id not in ITEM_VIRTUES
    )


def grant_choice(lab: Laboratory, entry: LabVirtueFlawDef) -> Choice:
    held = any(vf.vf_id == entry.id for vf in lab.virtues_flaws)
    note = "  (the lab has it already)" if held else ""
    return Choice(
        escape(f"{entry.name}  [{entry.type}, {entry.tier}]{note}"),
        entry,
        lab_rules.vf_entry_text(entry),
        f"{entry.type} {entry.category} {entry.tier}",
    )


def choose_grant(
    saga: Saga,
    lab: Laboratory,
    title: str,
    then: Callable[[VirtueFlawInstance], Any],
) -> Choose:
    """Choose the laboratory Virtue or Flaw the effect duplicates, then
    what it names; `then` gets the new instance."""
    books = sourcebooks.saga_books(saga)

    def chosen(entry: LabVirtueFlawDef) -> Command | None:
        if not lab_needs_input(entry):
            return then(VirtueFlawInstance(entry.id, id=new_instance_id()))
        return Form(
            escape(entry.name),
            lambda: lab_param_fields(saga, lab, entry),
            lambda values: then(
                VirtueFlawInstance(
                    entry.id, lab_params_from(entry, values), id=new_instance_id()
                )
            ),
            save_label="Save",
        )

    def offered() -> list[Choice]:
        return [
            grant_choice(lab, entry)
            for entry in catalog.load_lab_virtue_flaw_catalog()
            if grantable(entry)
            and sourcebooks.in_play(entry.source, books)
            and not catalog.hidden(entry)
        ]

    return Choose(f"{title}: the Virtue or Flaw it duplicates", offered, chosen)


# -- the second step: points by level --


def points_fields(level: int, benefit: LabItemBenefit | None) -> list[DialogField]:
    """The Specializations and Characteristics the effect's level buys
    points in, as many rows as the form offers (blank rows left out)."""
    specializations = list(benefit.specializations) if benefit else []
    characteristics = list(benefit.characteristics) if benefit else []
    fields = [
        DialogField(
            "_budget",
            "Level",
            "info",
            f"{level}: up to {level // lab_items.LEVELS_PER_SPECIALIZATION} "
            f"Specialization points, or a Characteristic point for every two.",
        )
    ]
    for n in range(SPECIALIZATION_ROWS):
        grant = specializations[n] if n < len(specializations) else None
        fields += [
            DialogField(
                f"specialization{n}",
                f"Specialization {n + 1}",
                "select",
                grant.specialization if grant else None,
                options=pairs(LAB_SPECIALIZATIONS),
                allow_blank=True,
                placeholder="(none)",
            ),
            DialogField(
                f"specialization_points{n}",
                f"Specialization {n + 1} points",
                "optint",
                grant.points if grant else None,
            ),
        ]
    for n in range(CHARACTERISTIC_ROWS):
        grant = characteristics[n] if n < len(characteristics) else None
        fields += [
            DialogField(
                f"characteristic{n}",
                f"Characteristic {n + 1}",
                "select",
                grant.characteristic if grant else None,
                options=[(characteristic_label(c), c) for c in LAB_CHARACTERISTICS],
                allow_blank=True,
                placeholder="(none)",
            ),
            DialogField(
                f"characteristic_points{n}",
                f"Characteristic {n + 1} points",
                "optint",
                grant.points if grant else None,
            ),
        ]
    return fields


def _rows(values: dict[str, Any], key: str, count: int) -> list[tuple[str, int | None]]:
    """The (name, points) rows of one kind with a name chosen."""
    return [
        (values[f"{key}{n}"], values.get(f"{key}_points{n}"))
        for n in range(count)
        if values.get(f"{key}{n}")
    ]


def points_problem(level: int, values: dict[str, Any]) -> str | None:
    """Why the points can't be saved: none chosen, a row without points or
    with fewer than 1, one named twice, or more than the level buys."""
    specializations = _rows(values, "specialization", SPECIALIZATION_ROWS)
    characteristics = _rows(values, "characteristic", CHARACTERISTIC_ROWS)
    rows = specializations + characteristics
    if not rows:
        return "Choose at least one Specialization or Characteristic."
    for name, points in rows:
        if points is None or points < 1:
            return f"Give {characteristic_label(name)} 1 point or more."
    names = [name for name, _ in rows]
    if len(set(names)) < len(names):
        return "Name each Specialization or Characteristic once."
    return (
        lab_items.budget_problem(
            level,
            sum(p or 0 for _, p in specializations),
            sum(p or 0 for _, p in characteristics),
        )
        or None
    )


def points_from(values: dict[str, Any]) -> ItemGives:
    return ItemGives(
        specializations=[
            LabSpecialtyGrant(name, points or 0)
            for name, points in _rows(values, "specialization", SPECIALIZATION_ROWS)
        ],
        characteristics=[
            LabCharacteristicGrant(name, points or 0)
            for name, points in _rows(values, "characteristic", CHARACTERISTIC_ROWS)
        ],
    )


# -- saving --


def _host(lab: Laboratory, choice: ItemChoice) -> VirtueFlawInstance:
    """The Magic Item or Enchantment Virtue the device is installed as,
    added if it has none yet, set to how it is installed now."""
    host = lab_items.item_virtue(lab, choice.device_id)
    if host is None:
        host = VirtueFlawInstance(
            lab_items.MAGIC_ITEM,
            {ITEM_DEVICE_PARAM: choice.device_id},
            id=new_instance_id(),
        )
        lab.virtues_flaws.append(host)
    host.vf_id = (
        lab_items.ENCHANTMENT
        if choice.installed == ENCHANTMENT
        else lab_items.MAGIC_ITEM
    )
    host.params.pop(ITEM_SIZE_PARAM, None)
    if choice.installed == LARGE:
        host.params[ITEM_SIZE_PARAM] = VERY_LARGE
    return host


def save(
    saga: Saga,
    lab: Laboratory,
    benefit: LabItemBenefit | None,
    choice: ItemChoice,
    gives: ItemGives,
) -> None:
    """Add (`benefit` None) or update one magic item effect from its two
    steps, adding the item's Virtue and the Virtue it grants, and taking
    away what an edit replaces."""

    def change() -> None:
        target = benefit or LabItemBenefit(
            id=new_instance_id(), device_id="", effect_id=""
        )
        old_host = target.virtue_id
        if target.granted_id:
            lab.virtues_flaws[:] = [
                vf for vf in lab.virtues_flaws if vf.id != target.granted_id
            ]
        host = _host(lab, choice)
        device = next(d for d in saga.enchanted_devices if d.id == choice.device_id)
        target.device_id, target.effect_id = choice.device_id, choice.effect_id
        target.virtue_id = host.id
        target.name = device.name
        target.granted_id = None
        target.specializations = gives.specializations
        target.characteristics = gives.characteristics
        if gives.granted is not None:
            lab.virtues_flaws.append(gives.granted)
            target.granted_id = gives.granted.id
        if benefit is None:
            lab.item_benefits.append(target)
        if (
            old_host
            and old_host != host.id
            and not any(b.virtue_id == old_host for b in lab.item_benefits)
        ):
            lab.virtues_flaws[:] = [vf for vf in lab.virtues_flaws if vf.id != old_host]

    counted = lab_rules.counted_specializations(saga, lab)
    change()
    lab_rules.reconcile_dropped(saga, lab, counted)


def points_form(
    saga: Saga, lab: Laboratory, benefit: LabItemBenefit | None, choice: ItemChoice
) -> Form:
    """The second step for points bought by the effect's level: saving
    adds or updates the magic item."""
    device = next(d for d in saga.enchanted_devices if d.id == choice.device_id)
    effect = next(e for e in device.effects if e.id == choice.effect_id)
    level = enchantment.modified_level(device, effect)
    same = benefit is not None and not benefit.granted_id
    return Form(
        "Add a magic item" if benefit is None else "Edit a magic item",
        lambda: points_fields(level, benefit if same else None),
        lambda values: save(saga, lab, benefit, choice, points_from(values)),
        validate=lambda values: points_problem(level, values),
        save_label="Add" if benefit is None else "Save",
    )


# -- the list --


def item_flow(
    saga: Saga,
    lab: Laboratory,
    benefit: LabItemBenefit | None,
    chosen: str | None = None,
) -> Command:
    """Add (`benefit` None) or edit what one effect gives the lab: the
    choice of effect, then the Virtue it grants or the points it buys.
    `chosen` (effect_value) is a new one's effect, when known."""
    title = "Add a magic item" if benefit is None else "Edit a magic item"
    if not effect_options(saga, lab, benefit):
        return Refuse(
            title,
            "No enchanted device with an effect is kept in this laboratory. "
            "Add one under Enchanted Devices (Inventory), or move one here, "
            "first.",
        )

    def second(values: dict[str, Any]) -> Command:
        choice = choice_from(values)
        if choice.gives == GRANTS:
            return choose_grant(
                saga,
                lab,
                title,
                lambda granted: save(
                    saga, lab, benefit, choice, ItemGives(granted=granted)
                ),
            )
        return points_form(saga, lab, benefit, choice)

    return Form(
        title,
        lambda: choice_fields(saga, lab, benefit, chosen),
        second,
        save_label="Next",
    )


#: Install's choices.
NEW_DEVICE = "new"
KEPT_DEVICE = "kept"


def install(saga: Saga, lab: Laboratory) -> Command:
    """Install a magic item, as a laboratory is set up: one of the devices
    kept in it, or a new device made first, with its effect. The device
    and its effect are each kept as they are saved, so cancelling a later
    step leaves them in the lab's Enchanted Devices."""

    def offered() -> list[Choice]:
        choices = [
            Choice(
                "A new enchanted device",
                NEW_DEVICE,
                "Make the device, kept in this laboratory, then its effect, then "
                "what the effect gives the laboratory.",
            )
        ]
        if effect_options(saga, lab, None):
            choices.append(
                Choice(
                    "A device kept in this laboratory",
                    KEPT_DEVICE,
                    "Choose one of the devices already kept here.",
                )
            )
        return choices

    def chosen(which: str) -> Command:
        return (
            new_device(saga, lab) if which == NEW_DEVICE else item_flow(saga, lab, None)
        )

    return Choose("Install a magic item", offered, chosen)


def new_device(saga: Saga, lab: Laboratory) -> Form:
    """Make a device kept in the lab, then its effect, then what the effect
    gives the lab."""

    def effect_added(device: EnchantedDevice, effect: InstilledEffect) -> Then | None:
        device.effects.append(effect)
        if device not in lab_items.held_devices(saga, lab):
            return None  # moved elsewhere on the device form: nothing to install
        return Then(item_flow(saga, lab, None, effect_value(device.id, effect.id)))

    def device_added(device: EnchantedDevice) -> Then:
        saga.enchanted_devices.append(device)
        return Then(
            device_forms.effect_form(
                device, None, lambda effect: effect_added(device, effect)
            )
        )

    return device_forms.device_form(
        saga, None, device_added, holder=f"laboratory:{lab.id}"
    )


def item_ops(saga: Saga, lab: Laboratory) -> SectionOps:
    """Add, Edit and Delete for what the lab's magic items give it."""

    def remove(index: int) -> Confirm:
        benefit = lab.item_benefits[index]

        def apply() -> None:
            counted = lab_rules.counted_specializations(saga, lab)
            lab_items.remove(lab, benefit)
            lab_rules.reconcile_dropped(saga, lab, counted)

        granted = " and the Virtue it grants" if benefit.granted_id else ""
        return Confirm(
            f"Remove what {escape(benefit.name or 'this item')} gives the "
            f"laboratory{granted}? The device itself stays.",
            apply,
        )

    return SectionOps(
        add=lambda: item_flow(saga, lab, None),
        edit=lambda index: item_flow(saga, lab, lab.item_benefits[index]),
        remove=remove,
        rows=lambda: [lab_rules.item_name(saga, b) for b in lab.item_benefits],
    )
