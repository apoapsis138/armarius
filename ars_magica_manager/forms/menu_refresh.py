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
from ..sections import AGENTS_SECTION, FAITH_SECTION, WHEREABOUTS_SECTION


class Refresh(NamedTuple):
    """The sections to redraw once the action's steps are answered."""

    sections: tuple[str, ...] = ()
    #: The change can rename or add records in the navigation tree.
    tree: bool = False
    #: False for a calculator, which changes nothing and so saves nothing.
    saves: bool = True
    #: The sheet is built again afterwards: the change adds or removes
    #: tabs (a tradition's, a sketch's).
    reshow: bool = False


def changes(*sections: str, tree: bool = False, reshow: bool = False) -> Refresh:
    return Refresh(sections, tree, reshow=reshow)


def calculator() -> Refresh:
    return Refresh(saves=False)


#: Per More action (the keys of menu.MORE_MENU's actions), what it changes.
REFRESH: dict[str, Refresh] = {
    "edit_interests": changes("tab-diary"),
    "edit_traditions": changes("section-char-info", "tab-abilities", reshow=True),
    # A character's or a covenant's detail level; the other's section is ignored.
    "promote": changes("section-char-info", "section-cov-info", tree=True, reshow=True),
    "demote": changes("section-char-info", "section-cov-info", tree=True, reshow=True),
    "share_spell": changes("section-known-spells", tree=True),
    "perform_ritual": changes("section-lab-raw-vis", "tab-lab-diary"),
    "impress_agent": changes(AGENTS_SECTION),
    "spend_agency_xp": changes(AGENTS_SECTION),
    "set_agent_task": changes(AGENTS_SECTION),
    "resolve_agent_task": changes(AGENTS_SECTION, "tab-diary"),
    "plan_copying": changes("section-char-season"),
    "clear_copying": changes("section-char-season"),
    "sell_goods": changes("section-char-season", "tab-diary"),
    "make_ligature": changes("section-char-season", "tab-diary"),
    "apothecary_store": changes("section-char-season", "tab-diary"),
    "artist_career": changes("section-char-season", "tab-diary"),
    "scholar_career": changes("section-char-season", "tab-diary"),
    "discipline_grog": changes(
        "section-personality-traits",
        "section-char-health",
        "section-char-info",
        tree=True,
    ),
    "grog_pension": changes("section-char-info", tree=True),
    "craft_by_magic": calculator(),
    "indulge_sin": changes("section-char-info", "section-aging", "tab-diary"),
    "infernal_influence": changes("section-char-info", "tab-diary"),
    "ars_goetia": calculator(),
    "turbulence": changes("section-char-info", "section-char-season", "tab-diary"),
    "gauntlet": changes(
        "section-char-info",
        "section-vf-virtues",
        "section-vf-flaws",
        "tab-diary",
        tree=True,
    ),
    "lose_the_gift": changes(
        "section-char-info", "section-vf-virtues", "section-vf-flaws", "tab-diary"
    ),
    "learn_cantation": changes("section-known-spells", "tab-diary"),
    "theban_letter": changes("tab-diary"),
    "invoke_oath": changes("section-vf-virtues", "section-vf-flaws", "tab-diary"),
    "make_greek_fire": changes("tab-diary"),
    "paint_icon": changes("tab-diary"),
    "venerate_icon": changes("section-char-health", "tab-diary"),
    "mothers_curse": changes("section-vf-virtues", "section-vf-flaws", "tab-diary"),
    "ars_fabulosa": changes(
        "section-char-health", "section-personality-traits", "tab-diary"
    ),
    "faerie_bargain": changes("section-personality-traits", "tab-diary"),
    "faerie_offer": changes("section-char-health", "tab-diary"),
    "cast_in_lacuna": calculator(),
    "pilgrimage": changes(
        "section-char-season",
        "section-vf-virtues",
        "section-vf-flaws",
        "section-personality-traits",
        "tab-diary",
    ),
    "invoke_saint": changes(FAITH_SECTION, "tab-diary"),
    "threaten_saint": changes(FAITH_SECTION, "section-personality-traits", "tab-diary"),
    "invoke_baraka": changes("tab-diary"),
    "hajj": changes(
        FAITH_SECTION, "section-personality-traits", "section-char-info", "tab-diary"
    ),
    "patron_saint": changes(FAITH_SECTION, "tab-diary"),
    "devotion_points": changes(FAITH_SECTION, "section-char-season", "tab-diary"),
    "act_of_piety": changes(
        "section-char-health",
        "section-personality-traits",
        "section-reputations",
        "tab-diary",
    ),
    "holy_influence": changes("section-char-info", "tab-diary"),
    "mystic_path": changes(FAITH_SECTION, "section-char-season", "tab-diary"),
    "spiritual_path": changes(
        "section-char-season",
        "section-char-info",
        "section-vf-virtues",
        "section-vf-flaws",
        "tab-diary",
    ),
    "monistic_revelation": changes(
        "section-vf-virtues", "section-char-season", "tab-diary"
    ),
    "gods_aid": changes("section-char-info", "tab-diary"),
    "experiment_script": changes("tab-diary"),
    "font_of_knowledge": changes("tab-diary"),
    "commanding_aura": changes("section-char-health", "tab-diary"),
    "verditius_hubris": changes(
        "section-personality-traits", "section-reputations", "tab-diary"
    ),
    "spirits_and_names": calculator(),
    "dream_working": changes("section-known-spells", "tab-diary"),
    "certamen_duel": changes("section-known-spells", "tab-diary"),
    "hermetic_sacrifice": changes("section-known-spells", "tab-diary"),
    "tmre_divination": changes("tab-diary"),
    "tmre_astrology": changes("tab-diary"),
    "house_acclaim": changes("section-reputations", "tab-diary"),
    "reputation_roll": changes("tab-diary"),
    "philosophic_alchemy": changes("section-char-season", "tab-diary"),
    "great_elixir": changes("section-aging", "tab-diary"),
    "change_virtues_flaws": changes(
        "section-vf-virtues",
        "section-vf-flaws",
        "section-char-characteristics",
        "tab-diary",
    ),
    "perform_exorcism": changes("tab-diary"),
    "follow_avenue": changes(
        "section-char-criamon-path", "section-char-ahead", "tab-planning", "tab-diary"
    ),
    "open_tunnel": calculator(),
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
