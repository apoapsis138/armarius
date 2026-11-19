"""More on a covenant: income and wealth, library, charter, guests, ships, projects, agents and the menagerie."""

from __future__ import annotations

from ... import mobile_covenants, sourcebooks
from ...actions import NodeKind
from ...commands import Refuse
from ...models.hermetic_projects import BURNING_CITY, INTANGIBLE_ASSASSIN, LIVING_CORPSE
from ...rules import agents as agent_rules
from ...sections import AGENTS_SECTION, WHEREABOUTS_SECTION
from .. import agents as agent_forms
from .. import hook_stories as hook_story_forms
from .. import land_shaping as land_forms
from .. import ship_build as ship_build_forms
from ..menu_refresh import changes
from ..menu_steps import covenant, improve, needs, on_agent, research_bonuses
from ..page import INCOME_SECTION
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

#: This area's actions, in the order More lists them.
ENTRIES: tuple[MoreAction, ...] = (
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
