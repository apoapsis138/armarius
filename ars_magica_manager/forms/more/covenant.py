"""More on a covenant: income and wealth, library, charter, guests, ships, projects, agents and the menagerie."""

from __future__ import annotations

from collections.abc import Callable

from ... import mobile_covenants, possessions, sourcebooks
from ...actions import ActionFacts, NodeKind
from ...commands import Command, Refuse
from ...models import Covenant, Possession
from ...models.hermetic_projects import BURNING_CITY, INTANGIBLE_ASSASSIN, LIVING_CORPSE
from ...rules import agents as agent_rules
from ...sections import AGENTS_SECTION, WHEREABOUTS_SECTION
from .. import agents as agent_forms
from .. import covenant as cov_forms
from .. import hook_stories as hook_story_forms
from .. import land_shaping as land_forms
from .. import ship_build as ship_build_forms
from ..menu_refresh import changes
from ..menu_steps import covenant, improve, needs, on_agent, research_bonuses
from ..page import INCOME_SECTION, Page
from .entry import MoreAction
from .rules import (
    acts_on_agent,
    begins_project,
    breaks_clause,
    censures_clause,
    charges_clause,
    ends_membership,
    forgets_template,
    improves,
    logs_stop,
    on_ship_row,
    owes_fee,
    research_bonuses_rule,
    staged,
)

#: The covenant's Vis Sources list, whose chosen source Harvest and Settle
#: act on.
VIS_SOURCES = "section-pos-vis_source"


def _vis_source(facts: ActionFacts) -> Possession | None:
    """The vis source chosen in the Vis Sources list, if any."""
    covenant, row = facts.selected_covenant, facts.chosen_row(VIS_SOURCES)
    if covenant is None or row is None:
        return None
    sources = [
        e.record
        for e in possessions.entries_for_kind(facts.saga, covenant, "vis_source")
        if e.record is not None
    ]
    return sources[row] if 0 <= row < len(sources) else None


def _on_vis_source(
    offered: Callable[[ActionFacts, Possession], bool],
) -> Callable[[ActionFacts, str], bool]:
    """Offered on the Vis Sources list, while `offered` says so of the
    chosen source."""

    def rule(facts: ActionFacts, section: str) -> bool:
        if section != VIS_SOURCES:
            return False
        source = _vis_source(facts)
        return source is not None and offered(facts, source)

    return rule


def _on_chosen_source(
    title: str, build: Callable[[Page, Covenant, Possession], Command]
) -> Callable[[Page], Command]:
    def step(page: Page) -> Command:
        source = _vis_source(page)
        if page.covenant is None or source is None:
            return Refuse(title, "Choose a vis source first.")
        return build(page, page.covenant, source)

    return step


#: This area's actions, in the order More lists them.
ENTRIES: tuple[MoreAction, ...] = (
    # A vis source's harvest by hand, in its season (vis_harvest): offered
    # on any source while the saga gathers by hand, and refused with the
    # reason on one that can't be harvested now, as the desktop's greyed
    # button says it.
    MoreAction(
        "harvest_vis",
        "h",
        "Harvest",
        step=_on_chosen_source(
            "Harvest",
            lambda page, covenant, source: cov_forms.harvest_form(
                page.saga, covenant, source
            ),
        ),
        refresh=changes(VIS_SOURCES, "section-pos-vis_store", "tab-cov-diary"),
        on_page=False,
        in_section=_on_vis_source(
            lambda facts, _source: facts.saga.harvest_vis_by_hand
        ),
    ),
    # Settle: the story that secures a contested vis source for five years
    # (DE p. 181); the desktop's row button beside it.
    MoreAction(
        "settle_vis_source",
        "s",
        "Settle",
        step=_on_chosen_source(
            "Settle",
            lambda page, covenant, source: cov_forms.settle_form(
                page.saga, covenant, source
            ),
        ),
        refresh=changes(VIS_SOURCES, "tab-cov-diary"),
        on_page=False,
        in_section=_on_vis_source(lambda _facts, source: source.contested),
    ),
    MoreAction(
        "improve",
        "i",
        "Improve Income",
        step=lambda page: (
            improve(
                page.saga,
                page.covenant,
                page.row if page.section == INCOME_SECTION else None,
            )
            if page.covenant is not None
            else Refuse("More", "That isn't available here.")
        ),
        refresh=changes("section-eco-income"),
        places=((NodeKind.COVENANT, "Income"),),
        in_section=improves,
    ),
    MoreAction(
        "research_bonuses",
        "b",
        "Set Up Research Library",
        step=needs(covenant, research_bonuses),
        refresh=changes(whole_page=True),
        places=((NodeKind.COVENANT, "Library"),),
        in_section=research_bonuses_rule,
    ),
    MoreAction(
        "impress_agent",
        "i",
        "Impress",
        step=on_agent(
            lambda page, character, row: agent_forms.impress(page.saga, character, row)
        ),
        refresh=changes(AGENTS_SECTION),
        on_page=False,
        in_section=acts_on_agent(lambda _c, agent: agent_rules.can_impress(agent)),
    ),
    MoreAction(
        "spend_agency_xp",
        "x",
        "Spend Agency Experience",
        step=on_agent(lambda _page, character, row: agent_forms.spend(character, row)),
        refresh=changes(AGENTS_SECTION),
        on_page=False,
        in_section=acts_on_agent(agent_rules.can_spend),
    ),
    MoreAction(
        "set_agent_task",
        "t",
        "Set a Task",
        step=on_agent(
            lambda page, character, row: agent_forms.set_task(page.saga, character, row)
        ),
        refresh=changes(AGENTS_SECTION),
        on_page=False,
        in_section=acts_on_agent(lambda _c, agent: agent_rules.may_be_asked(agent)),
    ),
    MoreAction(
        "resolve_agent_task",
        "r",
        "Resolve the Task",
        step=on_agent(
            lambda page, character, row: agent_forms.resolve(page.saga, character, row)
        ),
        refresh=changes(AGENTS_SECTION, "tab-diary"),
        on_page=False,
        in_section=acts_on_agent(lambda _c, agent: agent_rules.recruited(agent)),
    ),
    # A covenant's Hook proposes a story to accept.
    MoreAction(
        "suggest_story",
        "y",
        "Suggest a Story",
        step=needs(covenant, hook_story_forms.story_form),
        refresh=changes("section-cov-hooks", "tab-cov-diary"),
        section="section-cov-hooks",
        places=((NodeKind.COVENANT, "Hooks"),),
    ),
    MoreAction(
        "seal_charter",
        "s",
        "Seal the Charter",
        section="section-cov-charter",
        on_page=False,
    ),
    MoreAction(
        "break_clause", "b", "Break a Clause", on_page=False, in_section=breaks_clause
    ),
    MoreAction(
        "censure_clause", "c", "Censure", on_page=False, in_section=censures_clause
    ),
    MoreAction(
        "charge_clause",
        "g",
        "Charge at Tribunal",
        on_page=False,
        in_section=charges_clause,
    ),
    # A covenant's charter: its templates and its expelled members.
    MoreAction(
        "use_charter_template",
        "u",
        "Use a Template",
        section="section-cov-charter",
        on_page=False,
    ),
    MoreAction(
        "save_charter_template",
        "t",
        "Save as Template",
        section="section-cov-charter",
        on_page=False,
    ),
    MoreAction(
        "forget_charter_template",
        "f",
        "Forget a Template",
        on_page=False,
        in_section=forgets_template,
    ),
    MoreAction(
        "end_membership",
        "x",
        "End Membership",
        on_page=False,
        in_section=ends_membership,
    ),
    # A guest's yearly fee for his hospitality, on the host's Guests.
    MoreAction("pay_fee", "p", "Pay the Fee", on_page=False, in_section=owes_fee),
    # A covenant's ships (Hermetic Projects; City & Guild).
    MoreAction(
        "ship_stress", "s", "Stress Check", section="section-pos-ship", on_page=False
    ),
    MoreAction(
        "ship_combat", "c", "Ship Combat", section="section-pos-ship", on_page=False
    ),
    MoreAction(
        "ship_fate", "f", "Sunk or Taken", section="section-pos-ship", on_page=False
    ),
    MoreAction(
        "build_ship",
        "b",
        "Build a Ship",
        step=needs(covenant, ship_build_forms.build_form),
        refresh=changes("section-pos-ship", "tab-cov-diary"),
        section="section-pos-ship",
        on_page=False,
    ),
    MoreAction(
        "detach_ship",
        "x",
        "Detach",
        on_page=False,
        in_section=on_ship_row(mobile_covenants.can_detach),
    ),
    MoreAction(
        "rejoin_ship",
        "j",
        "Rejoin",
        on_page=False,
        in_section=on_ship_row(mobile_covenants.can_rejoin),
    ),
    # Where a covenant is: a mobile covenant logs its stops; its route is
    # planned on Whereabouts.
    MoreAction(
        "add_stop",
        "o",
        "Add a Stop",
        step=needs(covenant, mobile_covenants.add_stop),
        refresh=changes(WHEREABOUTS_SECTION),
        on_page=False,
        in_section=logs_stop,
    ),
    MoreAction(
        "plan_route",
        "t",
        "Plan Route",
        section="section-cov-whereabouts",
        on_page=False,
    ),
    # Shaping the land by magic (Transforming Mythic Europe).
    MoreAction(
        "shape_land",
        "l",
        "Shape the Land",
        step=needs(covenant, land_forms.shape_form),
        refresh=changes("section-eco-income", "tab-cov-diary"),
        places=((NodeKind.COVENANT, "Income"),),
        in_section=lambda facts, section: (
            section == "section-eco-income"
            and facts.selected_kind == NodeKind.COVENANT
            and facts.selected_covenant is not None
            and sourcebooks.in_play("TME", sourcebooks.saga_books(facts.saga))
        ),
    ),
    # A covenant's Hermetic Projects: the tower's stress check and rituals,
    # the project shown, beginning one; a magus's Wizard's War tunnel.
    MoreAction(
        "tower_stress", "s", "Stress Check", section="section-cov-tower", on_page=False
    ),
    MoreAction(
        "tower_conjure",
        "c",
        "Conjure Levels",
        section="section-cov-tower",
        on_page=False,
    ),
    MoreAction(
        "show_project",
        "w",
        "Show Project",
        section="section-cov-projects",
        on_page=False,
    ),
    MoreAction(
        "begin_project", "b", "Begin Project", on_page=False, on_record=begins_project
    ),
    # A covenant's Menagerie (Hermetic Projects): taming the chosen beast.
    MoreAction(
        "tame_beast",
        "t",
        "Tame a Beast",
        section="section-cov-menagerie-beasts",
        on_page=False,
    ),
    MoreAction(
        "menagerie_award",
        "w",
        "Reputation Award",
        section="section-cov-menagerie-beasts",
        on_page=False,
    ),
    # A covenant's staged Hermetic Project: a Burning City's warning bell,
    # an Intangible Assassin's connections and Aegis, a Living Corpse's
    # death roll.
    MoreAction(
        "warning_bell",
        "b",
        "Warning Bell",
        on_page=False,
        on_record=staged(BURNING_CITY),
    ),
    MoreAction(
        "gather_connection",
        "g",
        "Gather a Connection",
        on_page=False,
        on_record=staged(INTANGIBLE_ASSASSIN),
    ),
    MoreAction(
        "lower_aegis",
        "a",
        "Lower an Aegis",
        on_page=False,
        on_record=staged(INTANGIBLE_ASSASSIN),
    ),
    MoreAction(
        "death_roll", "r", "Death Roll", on_page=False, on_record=staged(LIVING_CORPSE)
    ),
)
