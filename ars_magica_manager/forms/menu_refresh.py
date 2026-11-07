"""What a More action changes, so a front-end that runs its first step
(menu.command) knows what to save and redraw afterwards.

An action with an entry here needs no handler of its own in the terminal:
it builds the page's `menu.Page`, runs the action's first step, then saves
and redraws the sections named. Where an action is offered is not where its
result lands (Cast a Power is offered on Aging & Warping and also writes the
Diary), so these are data of their own. An action with no entry is run by a
handler the front-end writes.
"""

from __future__ import annotations

from typing import NamedTuple

from .. import traditions
from ..rules import galdor
from ..sections import WHEREABOUTS_SECTION


class Refresh(NamedTuple):
    """The sections to redraw once the action's steps are answered."""

    sections: tuple[str, ...] = ()
    #: The change can rename or add records in the navigation tree.
    tree: bool = False
    #: False for a calculator, which changes nothing and so saves nothing.
    saves: bool = True


def changes(*sections: str, tree: bool = False) -> Refresh:
    return Refresh(sections, tree)


def calculator() -> Refresh:
    return Refresh(saves=False)


#: Per More action (the keys of menu.MORE_MENU's actions), what it changes.
REFRESH: dict[str, Refresh] = {
    "take_harm": changes("section-char-health"),
    "place_aging_points": changes("section-aging", "section-char-characteristics"),
    "boost_spell": calculator(),
    "hedge_cast": changes("section-aging", "tab-diary"),
    "galdor_conjure": changes("section-aging", "section-char-health", "tab-diary"),
    "galdor_bargain": changes(
        traditions.bonds_section(galdor.TRADITION_ID), "tab-diary"
    ),
    "galdor_bind": changes(
        traditions.effects_section(galdor.TRADITION_ID), "section-aging", "tab-diary"
    ),
    "trait_roll": calculator(),
    "disguise_roll": calculator(),
    "resolve_twilight": changes("section-aging"),
    "end_session": changes("section-reputations", "section-char-info"),
    "tourney_season": changes("section-reputations", "tab-diary"),
    "melee_event": changes("section-reputations", "tab-diary"),
    "labor_story": changes("section-char-season", "tab-diary"),
    "grog_story_xp": changes("section-char-season", "tab-diary"),
    "invest_labor": changes(
        "section-char-season", "section-reputations", "section-inventory", "tab-diary"
    ),
    "command_beast": changes("section-personality-traits"),
    "recovery_roll": changes("section-char-health"),
    "disputatio": changes("section-char-info"),
    "whereabouts": changes("section-casting"),
    "guest_stay": changes("section-casting"),
    "build_ship": changes("section-pos-ship", "tab-cov-diary"),
    "suggest_story": changes("section-cov-hooks", "tab-cov-diary"),
    "add_stop": changes(WHEREABOUTS_SECTION),
    "shape_land": changes("section-eco-income", "tab-cov-diary"),
}
