"""Enchanted Devices & Talismans: a device, its components, bonuses and
instilled effects, drawn from the core's forms (device_forms) with the
terminal's own Shape & Material picker and list screens."""

from __future__ import annotations

from ....forms import device as device_forms
from ....models import EnchantedDevice, InstilledEffect, Saga
from ..fields import FieldsDialog
from ..pickers import ShapeMaterialPickerScreen
from ..prompts import terminal_fields


def _shape_picker(_current: object) -> ShapeMaterialPickerScreen:
    return ShapeMaterialPickerScreen()


def _enchanted_device_dialog(
    saga: Saga,
    device: EnchantedDevice | None,
    *,
    holder: str | None = None,
) -> FieldsDialog[EnchantedDevice]:
    """Add or edit an enchanted device (device_forms.device_fields).
    `holder` ("kind:id") is a new device's default holder. Dismisses with
    the finished device (a new one, or a copy of `device` to put in its
    place)."""
    base = device or EnchantedDevice(id="", name="")
    return FieldsDialog(
        device_forms.device_title(device),
        terminal_fields(
            device_forms.device_fields(
                saga, device, holder=holder, shape_picker=_shape_picker
            )
        ),
        validate=lambda values: device_forms.device_problem(base, values),
        live=lambda values: device_forms.device_live(saga, base, values),
        save_label="Add" if device is None else "Save",
        build=lambda values: device_forms.device_build(saga, device, values),
    )


def _instilled_effect_dialog(
    device: EnchantedDevice, effect: InstilledEffect | None
) -> FieldsDialog[InstilledEffect]:
    """Add ("Instill Effect") or edit one of `device`'s effects
    (device_forms.effect_fields). Dismisses with the finished effect."""
    base = effect or device_forms.new_effect()
    return FieldsDialog(
        device_forms.effect_title(device, effect),
        device_forms.effect_fields(device, effect),
        validate=device_forms.effect_problem,
        live=lambda values: device_forms.effect_live(device, base, values),
        save_label="Add" if effect is None else "Save",
        build=lambda values: device_forms.effect_from_values(base, values),
    )
