"""More on a laboratory."""

from __future__ import annotations

from ... import deeds
from ...actions import NodeKind
from ...commands import Refuse
from ..menu_refresh import changes
from ..menu_steps import perform_ritual
from .entry import MoreAction
from .rules import performs_ritual

#: This area's actions, in the order More lists them.
ENTRIES: tuple[MoreAction, ...] = (
    MoreAction(
        "perform_ritual",
        "p",
        "Perform Ritual",
        step=lambda page: (
            perform_ritual(page.saga, page.laboratory, page.chosen_book)
            if page.laboratory is not None
            else Refuse("More", "That isn't available here.")
        ),
        refresh=changes("section-lab-raw-vis", "tab-lab-diary"),
        places=((NodeKind.LABORATORY, deeds.SEASON_WORK),),
        in_section=performs_ritual,
    ),
)
