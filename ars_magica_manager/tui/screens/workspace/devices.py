"""WorkspaceScreen's actions for enchanted devices, on every
sheet's Enchanted Devices section: a adds a device, e edits the chosen
device or effect and A removes it (after confirming), falling back to a
picker when none is chosen; More's Instill an Effect instils one in the
chosen device, Use a Charge uses a charge of the chosen Charged Item and
Use an Effect uses the chosen effect once (the core's steps), each shown
only where it can act."""

from __future__ import annotations

from .... import enchanted_devices as ed
from ....forms import device as device_forms
from ....markup import escape
from ....models import CHARGED, EnchantedDevice, InstilledEffect
from ..forms import _instilled_effect_dialog
from ..sheets import DEVICE_SECTIONS
from ..steps import run_steps
from .base import (
    WorkspaceBase,
    _SectionOps,
)

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

    def _commit_devices(self) -> None:
        self._commit(*_ALL_DEVICE_SECTIONS)

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
        """Instill shows only on a row whose device can take another
        effect, Use a Charge only on a Charged Item and Use an Effect only
        on an effect that can be used (so the menu stays short)."""
        target = self._chosen_target()
        if target is None:
            return False
        device, effect = target
        if action == "instill_effect":
            return device_forms.can_take_effect(device)
        if action == "use_effect":
            return ed.can_use(device, effect)
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

    def action_use_effect(self) -> None:
        """Use the chosen effect once (its Initiative, Penetration and uses
        today shown first)."""
        holder = self._device_holder()
        view = self._current_sheet_view()
        if holder is None or view is None:
            return
        section, kind, holder_id = holder
        row = view.selected_device_row(section)
        if row is None or row >= len(ed.device_targets(self.saga, kind, holder_id)):
            return

        def done(end: object) -> None:
            self._commit_devices()
            if isinstance(end, list) and end:
                self.notify(escape("\n".join(str(line) for line in end)))

        run_steps(
            self.app, device_forms.use_effect(self.saga, kind, holder_id, row), done
        )

    def _device_section_ops(self) -> dict[str, _SectionOps]:
        """a / d / e on the enchanted-device sections (see
        WorkspaceScreen._section_ops)."""
        return {section: self._core_ops_of(section) for section in DEVICE_SECTIONS}
