"""More on a familiar."""

from __future__ import annotations

from .entry import MoreAction

#: This area's actions, in the order More lists them.
ENTRIES: tuple[MoreAction, ...] = (
    MoreAction(
        "familiar_trait_roll",
        "o",
        "Roll",
        section="section-fam-personality-traits",
        on_page=False,
    ),
    MoreAction(
        "edit_familiar_fatigue",
        "f",
        "Edit Fatigue",
        section="section-fam-health",
        on_page=False,
    ),
)
