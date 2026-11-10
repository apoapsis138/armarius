"""WorkspaceScreen: the base plus one mixin of actions per kind of record, and
the table that routes a / e / d to them by section."""

from __future__ import annotations

from functools import cached_property, partial

from textual.widgets import (
    Button,
)

from ....sections import (
    NEIGHBOUR_INFO_SECTION,
    SEASONS_INFO_SECTION,
    TRIBUNAL_INFO_SECTION,
)
from .base import (
    _SectionOps,
)
from .character import CharacterActions
from .covenant import CovenantActions
from .creation import CreationActions
from .devices import DeviceActions
from .export import ExportActions
from .familiar import FamiliarActions
from .giving import GivingActions
from .laboratory import LaboratoryActions
from .library import LibraryActions
from .navigation import NavigationActions
from .records import RecordActions
from .season_turn import SeasonActions
from .virtues import VirtueFlawActions


class WorkspaceScreen(
    LibraryActions,
    CovenantActions,
    CharacterActions,
    LaboratoryActions,
    FamiliarActions,
    DeviceActions,
    VirtueFlawActions,
    RecordActions,
    SeasonActions,
    ExportActions,
    NavigationActions,
    GivingActions,
    CreationActions,
):
    """Persistent nav tree (left) + detail pane (right) for one open saga.

    Replaces the old Saga -> Covenant -> Character/Lab/Library drill-down
    screens with a single workspace: the whole saga's structure is always
    visible in the tree, and selecting any node swaps the detail pane on
    the right, so comparing siblings doesn't mean popping all the way back
    up and down again.
    """

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """The sheets' Edit buttons and In Creation / In Play switch."""
        handler = {
            "btn-lab-identity-edit": self._edit_lab_identity,
            "btn-lab-characteristics-edit": self._edit_lab_characteristics,
            "btn-cov-edit": self._edit_covenant,
            "btn-trib-edit": partial(self._core_verb, TRIBUNAL_INFO_SECTION, "edit"),
            "btn-nb-edit": partial(self._core_verb, NEIGHBOUR_INFO_SECTION, "edit"),
            "btn-seasons-edit": partial(self._core_verb, SEASONS_INFO_SECTION, "edit"),
            "btn-char-info-edit": self._edit_character_info,
            "btn-char-characteristics-edit": self._edit_characteristics,
            "btn-char-health-wounds-edit": self._edit_wounds,
            "btn-char-health-fatigue-edit": self._edit_fatigue,
            "btn-char-lab-text-access": self._edit_lab_text_access,
            "btn-fam-info-edit": self._edit_familiar_info,
            "btn-fam-health-wounds-edit": self._edit_familiar_wounds,
            "btn-fam-health-fatigue-edit": self._edit_familiar_fatigue,
            "btn-mode": self._toggle_creation_mode,
            "btn-worksheet": self._open_creation_worksheet,
        }.get(event.button.id or "")
        if handler is not None:
            event.stop()
            if not self._may_change_here():
                self.notify("Only the storyguide can change this.", severity="warning")
                return
            handler()

    # -- generic Add/Remove/Edit dispatch, by the active section of any sheet --

    @cached_property
    def _section_ops(self) -> dict[str, _SectionOps]:
        """What a / d / e (and More's Restore) do in each sheet section, keyed by the section id
        _active_section() reports. check_action enables a key only where it
        has an entry here, so a binding and its action can't disagree. Built
        once: check_action runs on every Footer refresh. Each mixin lists
        its own sheet's sections."""
        return {
            **self._library_section_ops(),
            **self._character_section_ops(),
            **self._familiar_section_ops(),
            **self._laboratory_section_ops(),
            **self._covenant_section_ops(),
            **self._shared_section_ops(),
            **self._virtue_flaw_section_ops(),
            **self._device_section_ops(),
            # The Armarium's Edit and Delete act on its marked books first.
            **self._store_section_ops(),
        }
