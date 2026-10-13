"""WorkspaceScreen's actions for enchanted devices, on every
sheet's Enchanted Devices section: a adds a device, e edits the chosen
device or effect and A removes it (after confirming), falling back to a
picker when none is chosen; i instils an effect in the chosen device and u
uses a charge of the chosen Charged Item, each shown only where it can act."""

from __future__ import annotations

from collections.abc import Callable

from .... import device_forms
from .... import enchanted_devices as ed
from ....markup import escape
from ....models import CHARGED, EnchantedDevice, InstilledEffect
from ..forms import _enchanted_device_dialog, _instilled_effect_dialog
from ..prompts import ConfirmScreen
from ..sheets import DEVICE_SECTIONS
from .base import WorkspaceBase

#: Every section a device change can show in: the lists, and the Hermetic
#: Magic tab's talisman line (refreshed with the character's list).
_ALL_DEVICE_SECTIONS = tuple(DEVICE_SECTIONS)

Target = tuple[EnchantedDevice, InstilledEffect | None]


class DeviceActions(WorkspaceBase):
    """WorkspaceScreen's actions for the Enchanted Devices sections."""

    def _device_holder(self) -> tuple[str, str, str] | None:
        """(section id, holder kind, holder id) of the active Enchanted
        Devices section, or None outside one."""
        section = self._active_section()
        kind = DEVICE_SECTIONS.get(section or "")
        record = {
            "character": self.selected_character,
            "laboratory": self.selected_laboratory,
            "covenant": self.selected_covenant,
        }.get(kind or "")
        if section is None or kind is None or record is None:
            return None
        return section, kind, record.id

    def _devices_or_pick(
        self,
        *,
        empty: str,
        then: Callable[[Target], object],
    ) -> None:
        """Act on the chosen row of the active device list (saying `empty`
        when it has none)."""
        holder = self._device_holder()
        view = self._current_sheet_view()
        if holder is None or view is None:
            return
        section, kind, holder_id = holder
        targets = ed.device_targets(self.saga, kind, holder_id)
        labels = ed.target_labels(self.saga, kind, holder_id)
        chosen = view.selected_device_row(section)
        if chosen is not None and chosen < len(targets):
            then(targets[chosen])
            return
        self._chosen_or_pick(None, labels, empty=empty, then=lambda i: then(targets[i]))

    def _commit_devices(self) -> None:
        self._commit(*_ALL_DEVICE_SECTIONS)

    # -- a / e / A --

    def _add_device(self) -> None:
        holder = self._device_holder()
        if holder is None:
            return
        _, kind, holder_id = holder

        def handle_result(device: EnchantedDevice | None) -> None:
            if device is not None:
                self.saga.enchanted_devices.append(device)
                self._commit_devices()

        self.app.push_screen(
            _enchanted_device_dialog(self.saga, None, holder=f"{kind}:{holder_id}"),
            handle_result,
        )

    def _edit_device_row(self) -> None:
        """Edit the chosen device or effect."""
        self._devices_or_pick(
            empty="No enchanted devices to edit.",
            then=self._edit_target,
        )

    def _edit_target(self, target: Target) -> None:
        device, effect = target
        if effect is None:
            self._edit_device(device)
        else:
            self._effect_form(device, effect)

    def _edit_device(self, device: EnchantedDevice) -> None:
        def handle_result(edited: EnchantedDevice | None) -> None:
            if edited is None or device not in self.saga.enchanted_devices:
                return
            devices = self.saga.enchanted_devices
            devices[devices.index(device)] = edited
            self._commit_devices()

        self.app.push_screen(_enchanted_device_dialog(self.saga, device), handle_result)

    def _remove_device_row(self) -> None:
        """Delete the chosen device (with its effects) or effect, after
        confirming."""
        self._devices_or_pick(
            empty="No enchanted devices to remove.",
            then=self._confirm_remove,
        )

    def _confirm_remove(self, target: Target) -> None:
        device, effect = target

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                device_forms.remove_target(self.saga, device, effect)
                self._commit_devices()

        self.app.push_screen(
            ConfirmScreen(device_forms.remove_question(device, effect)),
            handle_confirmed,
        )

    # -- i: Instill Effect, u: Use Charge (only where they can act) --

    def _chosen_target(self) -> Target | None:
        """The row chosen in the active Enchanted Devices list, if any."""
        holder = self._device_holder()
        view = self._current_sheet_view()
        if holder is None or view is None:
            return None
        section, kind, holder_id = holder
        targets = ed.device_targets(self.saga, kind, holder_id)
        chosen = view.selected_device_row(section)
        if chosen is None or chosen >= len(targets):
            return None
        return targets[chosen]

    def _device_action_enabled(self, action: str) -> bool:
        """i shows only on a row whose device can take another effect, u
        only on a Charged Item (so the footer stays short)."""
        target = self._chosen_target()
        if target is None:
            return False
        device, effect = target
        if action == "instill_effect":
            return device_forms.can_take_effect(device)
        return effect is None and device.type == CHARGED

    def action_instill_effect(self) -> None:
        """Instil an effect in the chosen device (or the chosen effect's
        device). A Lesser Enchantment or Charged Item has exactly one."""
        target = self._chosen_target()
        if target is not None and device_forms.can_take_effect(target[0]):
            self._effect_form(target[0], None)

    def _effect_form(
        self, device: EnchantedDevice, effect: InstilledEffect | None
    ) -> None:
        def handle_result(result: InstilledEffect | None) -> None:
            if result is None:
                return
            if effect is None:
                device.effects.append(result)
            elif effect in device.effects:
                device.effects[device.effects.index(effect)] = result
            self._commit_devices()

        self.app.push_screen(_instilled_effect_dialog(device, effect), handle_result)

    def action_use_charge(self) -> None:
        """Take a charge off the chosen Charged Item (nothing at 0)."""
        target = self._chosen_target()
        if target is None or target[0].type != CHARGED:
            return
        device = target[0]
        if not ed.use_charge(device):
            self.notify(f"{escape(device.name)} has no charges left.")
            return
        self._commit_devices()
        left = ed.charges_left(device)
        self.notify(
            f"{escape(device.name)}: {left} charge{'' if left == 1 else 's'} left."
        )
