"""WorkspaceScreen: the base plus one mixin of actions per kind of record, and
the table that routes a/A/e/r to them by section."""

from __future__ import annotations

from functools import cached_property, partial

from textual.widgets import (
    Button,
)

from ... import inhabitants as inh
from ...models import (
    INHABITANT_KINDS,
    POSSESSION_KINDS,
)
from ..sheets import (
    BOOK_SECTIONS,
    SPELL_SECTION,
)
from .base import (
    _CHARACTER_REPUTATIONS,
    _CHARACTER_TRAITS,
    _COVENANT_REPUTATIONS,
    _FAMILIAR_REPUTATIONS,
    _FAMILIAR_TRAITS,
    _SectionOps,
)
from .character import CharacterActions
from .covenant import CovenantActions
from .familiar import FamiliarActions
from .laboratory import LaboratoryActions
from .library import LibraryActions


class WorkspaceScreen(
    LibraryActions,
    CovenantActions,
    CharacterActions,
    LaboratoryActions,
    FamiliarActions,
):
    """Persistent nav tree (left) + detail pane (right) for one open saga.

    Replaces the old Saga -> Covenant -> Character/Lab/Library drill-down
    screens with a single workspace: the whole saga's structure is always
    visible in the tree, and selecting any node swaps the detail pane on
    the right, so comparing siblings doesn't mean popping all the way back
    up and down again.
    """

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """The sheets' Edit buttons."""
        handler = {
            "btn-lab-identity-edit": self._edit_lab_identity,
            "btn-lab-characteristics-edit": self._edit_lab_characteristics,
            "btn-cov-edit": self._edit_covenant,
            "btn-char-info-edit": self._edit_character_info,
            "btn-char-characteristics-edit": self._edit_characteristics,
            "btn-char-health-wounds-edit": self._edit_wounds,
            "btn-char-health-fatigue-edit": self._edit_fatigue,
            "btn-fam-info-edit": self._edit_familiar_info,
            "btn-fam-health-wounds-edit": self._edit_familiar_wounds,
            "btn-fam-health-fatigue-edit": self._edit_familiar_fatigue,
        }.get(event.button.id or "")
        if handler is not None:
            event.stop()
            handler()

    # -- generic Add/Remove/Edit dispatch, by the active section of any sheet --

    @cached_property
    def _section_ops(self) -> dict[str, _SectionOps]:
        """What a/A/e/r do in each sheet section, keyed by the section id
        _active_section() reports. check_action enables a key only where it
        has an entry here, so a binding and its action can't disagree. Built
        once: check_action runs on every Footer refresh."""
        ops: dict[str, _SectionOps] = {
            SPELL_SECTION: _SectionOps(
                lambda: self._spell_form(None),
                self._remove_saga_spell,
                self._edit_saga_spell,
            ),
            # Character sheet
            "section-char-info": _SectionOps(edit=self._edit_character_info),
            "section-char-characteristics": _SectionOps(
                edit=self._edit_characteristics
            ),
            "section-char-biographical": _SectionOps(
                edit=self._edit_biographical_detail
            ),
            "tab-abilities": _SectionOps(
                self._add_ability, self._remove_ability, self._edit_ability
            ),
            "section-aging": _SectionOps(edit=self._edit_aging),
            # Health has two dialogs behind two Edit buttons (Wounds and
            # Fatigue); 'e' opens Wounds, Fatigue is button-only.
            "section-char-health": _SectionOps(edit=self._edit_wounds),
            "section-arts": _SectionOps(edit=self._edit_arts),
            "section-hermetic-background": _SectionOps(
                edit=self._edit_hermetic_background
            ),
            "section-known-spells": _SectionOps(
                self._add_spell, self._remove_spell, self._edit_spell_mastery
            ),
            "section-inventory": _SectionOps(
                self._add_item, self._remove_item, self._edit_item
            ),
            "section-raw-vis-hermetic": _SectionOps(
                self._add_raw_vis, self._remove_raw_vis, self._edit_raw_vis
            ),
            "section-raw-vis-inventory": _SectionOps(
                self._add_raw_vis, self._remove_raw_vis, self._edit_raw_vis
            ),
            # Familiar sheet
            "section-fam-info": _SectionOps(edit=self._edit_familiar_info),
            "section-fam-binding": _SectionOps(edit=self._edit_familiar_binding),
            "section-fam-characteristics": _SectionOps(
                edit=self._edit_familiar_characteristics
            ),
            "section-fam-health": _SectionOps(edit=self._edit_familiar_wounds),
            "section-fam-natural-weapons": _SectionOps(
                self._add_familiar_natural_weapon,
                self._remove_familiar_natural_weapon,
                self._edit_familiar_natural_weapon,
            ),
            "tab-fam-abilities": _SectionOps(
                self._add_familiar_ability,
                self._remove_familiar_ability,
                self._edit_familiar_ability,
            ),
            "tab-fam-powers": _SectionOps(
                self._add_familiar_bond_power,
                self._remove_familiar_bond_power,
                self._edit_familiar_bond_power,
            ),
            # Laboratory sheet
            "section-lab-identity": _SectionOps(edit=self._edit_lab_identity),
            "section-lab-characteristics": _SectionOps(
                edit=self._edit_lab_characteristics
            ),
            "section-lab-specialties": _SectionOps(
                self._add_specialty, self._remove_specialty, self._edit_specialty
            ),
            "section-lab-features": _SectionOps(
                self._add_feature, self._remove_feature, self._edit_feature
            ),
            "section-lab-rooms": _SectionOps(
                self._add_room, self._remove_room, self._edit_room
            ),
            "section-lab-raw-vis": _SectionOps(
                self._add_lab_raw_vis, self._remove_lab_raw_vis, self._edit_lab_raw_vis
            ),
            "section-lab-items": _SectionOps(
                self._add_inventory_item,
                self._remove_inventory_item,
                self._edit_inventory_item,
            ),
            "tab-lab-diary": _SectionOps(
                self._add_diary_entry, self._remove_diary_entry, self._edit_diary_entry
            ),
            # Covenant sheet
            "section-cov-info": _SectionOps(edit=self._edit_covenant),
            "section-cov-description": _SectionOps(
                edit=self._edit_covenant_description
            ),
            "section-cov-boons": _SectionOps(
                lambda: self._add_boon_hook("Boon"),
                lambda: self._remove_boon_hook("Boon"),
                lambda: self._edit_boon_hook("Boon"),
            ),
            "section-cov-hooks": _SectionOps(
                lambda: self._add_boon_hook("Hook"),
                lambda: self._remove_boon_hook("Hook"),
                lambda: self._edit_boon_hook("Hook"),
            ),
            "section-eco-wealth": _SectionOps(edit=self._edit_wealth),
            "section-eco-income": _SectionOps(
                self._add_income_source,
                self._remove_income_source,
                self._edit_income_source,
            ),
            "section-eco-expenditure": _SectionOps(
                edit=lambda: self._edit_economics_row("expenditure")
            ),
            "section-eco-savings": _SectionOps(
                edit=lambda: self._edit_economics_row("savings")
            ),
            "section-inh-loyalty": _SectionOps(edit=self._edit_loyalty),
            "section-inh-population": _SectionOps(edit=self._edit_population),
            "section-inh-misc": _SectionOps(edit=self._edit_miscellaneous),
        }
        for spec in (
            _CHARACTER_TRAITS,
            _CHARACTER_REPUTATIONS,
            _FAMILIAR_TRAITS,
            _FAMILIAR_REPUTATIONS,
            _COVENANT_REPUTATIONS,
        ):
            ops[spec.section] = _SectionOps(
                partial(self._add_trait, spec),
                partial(self._remove_trait, spec),
                partial(self._edit_trait, spec),
            )
        for section in BOOK_SECTIONS:
            listed = section != "section-lib-summary"  # the summary lists none
            ops[section] = _SectionOps(
                lambda: self._book_form(None),
                self._remove_book if listed else None,
                self._edit_book if listed else None,
            )
        for kind in INHABITANT_KINDS:
            ops[f"section-inh-{kind}"] = _SectionOps(
                partial(self._add_inhabitant, kind),
                partial(self._remove_inhabitant, kind),
                partial(self._edit_inhabitant, kind),
                # Only Magi/Companions can go "departed" (Inhabitant.departed).
                partial(self._restore_inhabitant, kind)
                if kind in inh.AUTO_KINDS
                else None,
            )
        for kind in POSSESSION_KINDS:
            ops[f"section-pos-{kind}"] = _SectionOps(
                partial(self._add_possession, kind),
                partial(self._remove_possession, kind),
                partial(self._edit_possession, kind),
            )
        return ops
