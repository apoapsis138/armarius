"""How to reach each form dialog the way the app does: which tree node to
select and which WorkspaceScreen handler (or picker hook) opens it. Shared
by the dialog contract tests; see dialog_contract_support.py."""

import asyncio
import inspect
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from support import NODES, everything_saga, wait_until
from textual.screen import ModalScreen
from textual.widgets import TabbedContent, Tree

from ars_magica_manager import (
    catalog,
    choice_templates,
    giving,
    grog_templates,
    meeting,
    neighbour_filter,
    storage,
    vis,
)
from ars_magica_manager import economics as eco
from ars_magica_manager import goods as gd
from ars_magica_manager.forms import agents as agent_forms
from ars_magica_manager.forms import animal as animal_forms
from ars_magica_manager.forms import charter as charter_forms
from ars_magica_manager.forms import choice_templates as choice_forms
from ars_magica_manager.forms import creation as creation_forms
from ars_magica_manager.forms import grogs as grog_forms
from ars_magica_manager.forms import lab_item
from ars_magica_manager.forms import tribunal as tribunal_forms
from ars_magica_manager.forms import worksheet as wf
from ars_magica_manager.models import (
    Ability,
    Agent,
    Book,
    Character,
    CharterClause,
    Neighbour,
    Saga,
    SagaSource,
    ScoredTrait,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import creation_xp
from ars_magica_manager.rules import divine_state as ds
from ars_magica_manager.rules import mysticism as my
from ars_magica_manager.tribunal_packages import rhine as rhine_package
from ars_magica_manager.tui import screens as scr
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens.forms import _mastery_dialog
from ars_magica_manager.tui.screens.prompts import ListFieldScreen
from ars_magica_manager.tui.screens.widgets import section_stop
from ars_magica_manager.tui.screens.workspace import _COVENANT_REPUTATIONS


def contract_saga() -> Saga:
    """everything_saga() plus an unbonded magus (so a familiar can be bound),
    in Autumn: not the first season, so a form that defaults to the saga's
    season is told apart from one that defaults to Spring."""
    saga = everything_saga()
    saga.current_season = "Autumn"
    saga.characters.append(
        Character(id="mag2", name="Brother Oda", type="magus", covenant_id="cov1")
    )
    # A Longevity Ritual's Lab Text in the lab, for its owner:
    # he is 10 (2 pawns) and can handle 2 (Magic Theory 1).
    magus = saga.character("mag1")
    assert magus is not None
    magus.background.year_born = saga.current_year - 10
    magus.abilities.append(Ability("Magic Theory", xp=5))
    # Enough Lore to self-initiate into a Mystery.
    magus.abilities.append(Ability("Mercere Lore", xp=5))
    saga.books.append(
        Book(
            id="b-ritual",
            name="Lab Text: Longevity Ritual for Leandro",
            type="Lab Text",
            text_kind="Longevity Ritual",
            technique="Creo",
            form="Corpus",
            level=20,
            ritual_subject="Leandro",
            owner_kind="laboratory",
            owner_id="lab1",
        )
    )
    grog = Character(id="grog9", name="Hugo", type="grog", covenant_id="cov1")
    grog.abilities = [Ability("Single Weapon"), Ability("Brawl"), Ability("Awareness")]
    saga.characters.append(grog)
    # A second lord, for battles between two of them.
    saga.neighbours.append(Neighbour(id="mark", name="Count of Mark", kind="lord"))
    return saga


def _add_story_event_with_pools(ws) -> None:
    """The covenant's Diary form, once the covenant holds a Hidden
    Resources Boon ("bh-hr") and an Illusory Resources Hook ("bh-ir")
    for a Story Event to count against."""
    covenant = ws.selected_covenant
    for vf_id, bh_id in (
        ("covbh_boon_minor_hidden_resources", "bh-hr"),
        ("covbh_hook_minor_illusory_resources", "bh-ir"),
    ):
        if not any(bh.id == bh_id for bh in covenant.boons_hooks):
            covenant.boons_hooks.append(VirtueFlawInstance(vf_id, id=bh_id))
    ws._add_covenant_diary_entry()


@dataclass(frozen=True)
class Opener:
    #: Tree node to select first (a NODES key), or None for the saga picker.
    node: str | None
    #: Opens the dialog, given the workspace (or saga picker) screen.
    open: Callable[[object], object]


def _built(open_editor):
    """Open a dialog from a section on a tab not built yet: build the
    sheet's tabs first."""

    async def opener(ws) -> None:
        await ws._current_sheet_view().build_all_tabs()
        open_editor(ws)

    return opener


async def _on_lords_row(ws, section_id: str, key: str, rows: list, action) -> None:
    """A More command on Gottfried's Manors tab, on the first of `rows`
    put under `key` in memory (saved only with the form)."""
    ws.saga.neighbour("gottfried").details[key] = rows
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    view.refresh_section(section_id)
    listed = view.query_one(
        f"#{section_id.removeprefix('section-')}-list", scr.SelectableList
    )
    listed.select_data_index(0)
    await until(lambda: listed.selected_data_index == 0)
    action(ws)


async def _assart(ws) -> None:
    """Assart on a manor with 60 acres of waste."""
    await _on_lords_row(
        ws,
        "section-manors",
        "manor_list",
        [{"name": "Hagen", "acres": 600, "demesne": 200, "waste": 60}],
        lambda ws: ws.action_assart(),
    )


async def _winter_roll(ws) -> None:
    """The Winter Roll on Excellent stables."""
    await _on_lords_row(
        ws,
        "section-establishments",
        "establishments",
        [{"kind": "Stables", "quality": "Excellent", "animals": 20}],
        lambda ws: ws.action_winter_roll(),
    )


async def _court_roll(ws) -> None:
    """The Court Roll on a case put before Soest's court in memory (saved
    only with the form)."""
    soest = ws.saga.neighbour("soest")
    soest.details["court_cases"] = [{"accused": "Hartmut", "charge": "Theft"}]
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    view.refresh_section("section-nb-court-cases")
    rows = view.query_one("#nb-court-cases-list", scr.SelectableList)
    rows.select_data_index(0)
    await until(lambda: rows.selected_data_index == 0)
    ws.action_court_roll()


def _grogs_aging_chart(ws) -> None:
    """The Grogs Aging Chart for the grog Hugo, made 45 in memory (saved
    only with the form)."""
    grog = ws.saga.character("grog9")
    grog.background.year_born = ws.saga.current_year - 45
    ws._run_steps(wf.grog_aging_chart(ws.saga, grog))


def _found_covenant(ws) -> None:
    """More's Found a Covenant Here, on the place marked a ruin first."""
    ws.saga.neighbour("drachenfels").details["ruined"] = True
    ws.action_found_covenant()


def _open_saga_source(ws) -> None:
    """Edit a saga source, made in memory (saved only with the edit)."""
    if not ws.saga.sources:
        ws.saga.sources.append(SagaSource("HR", "House rules"))
    ws._saga_source_form(ws.saga.sources[0])


def _filter_neighbours(ws) -> None:
    """Filter Neighbours, the Region already narrowed to the
    Siebengebirge, from its Lords and Towns."""
    neighbour_filter.choose(ws.saga, neighbour_filter.Filter(region="siebengebirge"))
    ws._region_sheet_view.refresh_all()
    ws._filter_neighbours()


def _param_vf() -> str:
    """A Virtue whose name has a blank to fill in."""
    return next(
        e.id
        for e in catalog.load_virtue_flaw_catalog()
        if e.parameters and e.type == "Virtue"
    )


async def _open_param_prompt(ws, vf_id: str | None = None) -> None:
    """Add a Virtue with a parameter (from the Virtues section): the picker
    asks for it."""
    view = ws._current_sheet_view()
    view.query_one(TabbedContent).active = "tab-vf"
    # The tab is built as it is first shown.
    await until(lambda: view.query("#section-vf-virtues CollapsibleTitle"))
    section_stop(view.query_one("#section-vf-virtues")).focus()
    await until(lambda: ws._active_section() == "section-vf-virtues")
    ws.action_add_virtue_flaw()
    picker = await wait_for_screen(ws.app, scr.VirtueFlawPickerScreen)
    picker._on_entry_selected(
        catalog.load_virtue_flaw_catalog_by_id()[vf_id or _param_vf()]
    )


async def _open_secrets(ws) -> None:
    """Edit on the Secrets tab, shown first (it is built when shown)."""
    view = ws._current_sheet_view()
    view.query_one(TabbedContent).active = "tab-secrets"
    await until(lambda: view.query("#section-secrets CollapsibleTitle"))
    ws._core_verb("section-secrets", "edit")


async def _open_virtue_change(ws) -> None:
    """Change what a Virtue names (Edit on the Virtues list): Puissant
    Magic Theory, taken first, chosen in the list."""
    magus = ws.selected_character
    if not any(vf.vf_id == "vf_puissant_ability" for vf in magus.virtues_flaws):
        magus.virtues_flaws.append(
            VirtueFlawInstance("vf_puissant_ability", {"ability": "magic theory"})
        )
    view = ws._current_sheet_view()
    view.query_one(TabbedContent).active = "tab-vf"
    await until(lambda: view.query("#section-vf-virtues CollapsibleTitle"))
    view.refresh_all()
    index = len(magus.virtues_flaws) - 1
    rows = view.query_one("#vf-virtues-list", scr.SelectableList)
    await until(lambda: rows.select_data_index(index))
    await until(lambda: rows.selected_data_index == index)
    rows.focus()
    await until(lambda: ws._active_section() == "section-vf-virtues")
    ws.action_edit_virtue_flaw()


async def _open_lab_virtue_change(ws) -> None:
    """Change a laboratory Virtue's Specialization (Edit on the lab's
    Virtues list): Idyllic Surroundings for Creo, taken first, chosen in
    the list."""
    lab = ws.selected_laboratory
    if not any(vf.vf_id == "labvf_idyllic_surroundings" for vf in lab.virtues_flaws):
        lab.virtues_flaws.append(
            VirtueFlawInstance(
                "labvf_idyllic_surroundings", {"specialization": "Creo"}, id="idyll"
            )
        )
    view = ws._current_sheet_view()
    view.query_one(TabbedContent).active = "tab-lab-vf"
    await until(lambda: view.query("#section-lab-vf-virtues CollapsibleTitle"))
    view.refresh_all()
    index = len(lab.virtues_flaws) - 1
    rows = view.query_one("#lab-vf-virtues-list", scr.SelectableList)
    await until(lambda: rows.select_data_index(index))
    await until(lambda: rows.selected_data_index == index)
    rows.focus()
    await until(lambda: ws._active_section() == "section-lab-vf-virtues")
    ws.action_edit_virtue_flaw()


async def _open_lab_choice_prompt(
    ws, section: str = "section-lab-vf-flaws", vf_id: str = "labvf_disorganized"
) -> None:
    """Add a laboratory Virtue or Flaw that asks for something (a Flaw
    whose Specialization the owner chooses, a Servant): the picker asks
    for it."""
    view = ws._current_sheet_view()
    view.query_one(TabbedContent).active = "tab-lab-vf"
    # The tab is built as it is first shown.
    await until(lambda: view.query(f"#{section} CollapsibleTitle"))
    section_stop(view.query_one(f"#{section}")).focus()
    await until(lambda: ws._active_section() == section)
    ws.action_add_virtue_flaw()
    picker = await wait_for_screen(ws.app, scr.LabVirtueFlawPickerScreen)
    picker._on_entry_selected(catalog.load_lab_virtue_flaw_catalog_by_id()[vf_id])


def _open_mastery_ability(ws) -> None:
    """Add a Mastery Ability: the list editor the Mastery form's Mastery
    Abilities field opens, then its Add."""
    known = ws.selected_character.spells_known[0]
    form = _mastery_dialog("Spell", known)
    spec = next(f for f in form.fields if f.key == "mastery_abilities")
    editor = spec.picker(spec.value)
    ws.app.push_screen(editor)
    ws.app.call_later(editor.action_add)


def _pick(open_editor, list_id: str, index: int = 0):
    """Open a dialog that edits a list's chosen row: the one at `index` of
    the list `list_id`, chosen first."""

    async def opener(ws) -> None:
        # The chosen row is looked for in the section's tab: build it.
        view = ws._current_sheet_view()
        await view.build_all_tabs()
        rows = view.query_one(f"#{list_id}", scr.SelectableList)
        rows.select_data_index(index)
        await until(lambda: rows.selected_data_index == index)
        open_editor(ws)

    return opener


async def _open_tradition_effect(ws) -> None:
    """Add an effect in Leandro's vitki chapter (built first, as its
    tab is first shown)."""
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    ws._core_verb("section-teff-trad_vitkir", "add")


async def _open_power(ws) -> None:
    """Add a power on Leandro's Virtues & Flaws tab."""
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    ws._core_verb("section-char-powers", "add")


async def _open_agent(ws) -> None:
    """Add an agent on Leandro's Agents tab."""
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    ws._core_verb("section-char-agents", "add")


async def _open_good(ws) -> None:
    """Add a good of the saga's own on Saga Content's Goods tab."""
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    ws._core_verb("section-content-goods", "add")


async def _open_purity(ws) -> None:
    """More's Add a Purity on silver, chosen on the Goods tab."""
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    index = [g.name for g in gd.listed(ws.saga)].index("Silver")
    rows = view.query_one("#content-goods-list", scr.SelectableList)
    # Focused, as the user leaves it: saving keeps the row chosen.
    rows.focus()
    rows.select_data_index(index)
    await until(lambda: rows.selected_data_index == index)
    ws.action_add_purity()


def _with_agents(ws) -> Character:
    """Leandro with an agent of Bond +1 and an impressed potential agent
    of resistance 3, and 10 Agency experience (once, however often the
    form is opened)."""
    character = ws.selected_character
    if not character.agents:
        character.agents = [
            Agent(
                "Sir Konrad",
                resistance=0,
                impressed=True,
                bond_trait="Owes his life",
                bond=1,
            ),
            Agent(
                "Father Bertolf", status="minor_virtue", impressed=True, resistance=3
            ),
        ]
        character.agency_xp = 10
    return character


async def _open_agent_task(ws) -> None:
    """More's Set a Task for Leandro's first agent."""
    character = _with_agents(ws)
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    ws._run_steps(agent_forms.set_task(ws.saga, character, 0))


async def _open_agent_resolve(ws) -> None:
    """More's Resolve the Task for Leandro's first agent."""
    character = _with_agents(ws)
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    ws._run_steps(agent_forms.resolve(ws.saga, character, 0))


async def _open_agency_spend(ws) -> None:
    """More's Spend Agency Experience on Leandro's potential agent."""
    character = _with_agents(ws)
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    ws._run_steps(agent_forms.spend(character, 1))


def _with_clause(ws):
    """The covenant with one clause in its charter (once, however often
    the form is opened)."""
    covenant = ws.selected_covenant
    charter = covenant.charter_of_covenant
    if not charter.clauses:
        charter.clauses = [CharterClause("1", "All vis is shared.", 1200, "Spring")]
    return covenant


async def _open_charter_verb(ws, section: str, verb: str) -> None:
    """The Charter tab's own Edit or Add, as its key runs it."""
    _with_clause(ws)
    await ws._current_sheet_view().build_all_tabs()
    ws._core_verb(section, verb)


async def _open_edit_clause(ws) -> None:
    covenant = _with_clause(ws)
    await ws._current_sheet_view().build_all_tabs()
    ws._run_steps(charter_forms.clause_ops(ws.saga, covenant).edit(0))


async def _open_break_clause(ws) -> None:
    covenant = _with_clause(ws)
    await ws._current_sheet_view().build_all_tabs()
    ws._run_steps(charter_forms.break_clause(ws.saga, covenant, 0))


async def _open_seal_charter(ws) -> None:
    await ws._current_sheet_view().build_all_tabs()
    ws.action_seal_charter()


def _as_merchant(ws) -> Character:
    """Leandro as a merchant too, with a Profession and 40 Labor Points
    (in memory, saved only with the form)."""
    character = ws.selected_character
    if not any(vf.vf_id == "vf_merchant" for vf in character.virtues_flaws):
        character.virtues_flaws.append(VirtueFlawInstance("vf_merchant"))
        character.abilities.append(Ability("Profession: Merchant", xp=75))
        character.labor_points = 40
    return character


async def _open_labor_story(ws) -> None:
    """More's Labor Points from a Story on Leandro's This Season."""
    _as_merchant(ws)
    ws.action_labor_story()


async def _open_invest_labor(ws) -> None:
    """More's Invest Time or Money on Leandro's This Season."""
    _as_merchant(ws)
    ws.action_invest_labor()


async def _open_sell_goods(ws) -> None:
    """More's Sell Finished Goods on Leandro's This Season, as a smith."""
    character = ws.selected_character
    if not any(a.name == "Craft: Smith" for a in character.abilities):
        character.abilities.append(Ability("Craft: Smith", xp=75))
    ws.action_sell_goods()


async def _open_apothecary(ws, which: str) -> None:
    """More's Make a Ligature or Apothecary's Store on Leandro, given
    Medicine and Profession: Apothecary."""
    character = ws.selected_character
    for name in ("Medicine", "Profession: Apothecary"):
        if not any(a.name == name for a in character.abilities):
            character.abilities.append(Ability(name, xp=15))
    if which == "ligature":
        ws.action_make_ligature()
    else:
        ws.action_apothecary_store()


async def _open_constant_effect(ws) -> None:
    """Add a constant effect under Leandro's Aging & Warping."""
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    ws._core_verb("section-char-constant-effects", "add")


async def _open_lab_trait(ws) -> None:
    """Add a Personality Trait on the lab's Virtues & Flaws tab."""
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    ws._core_verb("section-lab-personality-traits", "add")


async def _open_bound_being(ws) -> None:
    """Add a being bound in Leandro's vitki chapter."""
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    ws._core_verb("section-tbond-trad_vitkir", "add")


def _open_meeting(saga: Saga, tribunal) -> None:
    """Open the Tribunal's meeting (its roll call as it comes), once: the
    dialog is opened again after a cancel."""
    if tribunal.meeting is None:
        opening = meeting.hold(saga, tribunal)
        opening.apply({f.key: f.value for f in opening.fields() if f.kind != "info"})


async def _open_attendance(ws) -> None:
    """Attendance and proxies, the meeting opened first."""
    tribunal = ws.saga.tribunals[0]
    _open_meeting(ws.saga, tribunal)
    await _pick(
        lambda ws: ws._core_verb("section-meeting-attendance", "edit"),
        "meeting-attendance",
    )(ws)


def _open_meeting_step(row: int, list_id: str):
    """The meeting opened, then Edit on `list_id`'s row `row`: the
    Order of Business's second row is the Opening, its third the Rhine's
    rite, its fourth the first case's debate."""

    async def opener(ws) -> None:
        tribunal = ws.saga.tribunals[0]
        _open_meeting(ws.saga, tribunal)
        section = "section-" + list_id
        await _pick(lambda ws: ws._core_verb(section, "edit"), list_id, row)(ws)

    return opener


def _economics_row(which: str, key: str):
    """Edit the Yearly Expenditure / Cost Savings row with `key`."""

    def opener(ws) -> None:
        summary = eco.summarize(ws.saga, ws.selected_covenant)
        rows = summary.expenditure if which == "expenditure" else summary.savings
        ws._economics_row_form(which, next(r for r in rows if r.key == key))

    return opener


async def _open_ability_details(ws) -> None:
    """Add an Ability: pick Athletics, which asks for its details."""
    ws._add_ability()
    picker = await wait_for_screen(ws.app, scr.AbilityPickerScreen)
    picker._on_entry_selected(catalog.load_ability_catalog_by_id()["ab_athletics"])


async def _open_boon_details(ws) -> None:
    """Add a Boon: pick Edifice, which asks for its detail."""
    ws._add_boon_hook("Boon")
    picker = await wait_for_screen(ws.app, scr.CovenantBoonHookPickerScreen)
    picker._on_entry_selected(
        catalog.load_covenant_boon_hook_catalog_by_id()["covbh_boon_minor_edifice"]
    )


def _open_research_bonuses(ws) -> None:
    """The covenant library's research bonuses, with its summa on Ignem."""
    book = next(b for b in ws.saga.books if b.id == "b-cov")
    book.art, book.level, book.quality = "Ignem", 10, 12
    ws.action_research_bonuses()


def _open_book_craft(ws) -> None:
    """Edit the covenant's summa under the extended book Quality rule."""
    ws.saga.rule_options = {"extended_book_quality": True}
    book = next(b for b in ws.saga.books if b.id == "b-cov")
    book.art, book.level, book.quality = "Ignem", 10, 12
    ws._book_form(book)


def _with_rhine_ranks(ws) -> None:
    """Severinus of Fengheld a master of House Tytalus, as Brother Oda is
    of it; Stentorius of Fengheld an archmage (once, however often the
    form is opened)."""
    saga = ws.saga
    if any(c.id == "arch1" for c in saga.characters):
        return
    severinus = saga.character("mag_sketch")
    severinus.virtues_flaws.append(VirtueFlawInstance("vf_master_rhine_tribunal"))
    severinus.hermetic.house = "house_tytalus"
    saga.character("mag2").hermetic.house = "house_tytalus"
    saga.characters.append(
        Character(
            id="arch1",
            name="Stentorius",
            type="magus",
            covenant_id="cov_sketch",
            virtues_flaws=[VirtueFlawInstance("vf_archmage_rhine_tribunal")],
        )
    )


def _open_rhine_verb(action: str):
    async def opener(ws) -> None:
        _with_rhine_ranks(ws)
        await _pick(lambda ws: getattr(ws, f"action_{action}")(), "trib-gilds-list")(ws)

    return opener


async def _open_rhine_rite(ws) -> None:
    """The meeting opened with Severinus made master since the last one:
    Edit on the Order of Business's third row, the Rhine's rite."""
    _with_rhine_ranks(ws)
    tribunal = ws.saga.tribunals[0]
    if not rhine_package.promotions(tribunal):
        rhine_package.promotions(tribunal).append(
            {
                "character_id": "mag_sketch",
                "rank": "vf_master_rhine_tribunal",
                "year": 1220,
                "sigils": 1,
                "conferred": None,
                "names": [],
            }
        )
    await _open_meeting_step(2, "meeting-business")(ws)


OPENERS: dict[str, Opener] = {
    # Saga level
    "create saga": Opener(None, lambda p: p.action_create_saga()),
    "edit saga": Opener("saga", lambda ws: ws._edit_saga()),
    "set date": Opener("saga", lambda ws: ws.action_set_date()),
    "create covenant": Opener("saga", lambda ws: ws.action_create_covenant()),
    "create tribunal": Opener("saga", lambda ws: ws.action_create_tribunal()),
    "add faction": Opener(
        "region", lambda ws: ws._core_verb("section-region-factions", "add")
    ),
    "filter neighbours": Opener("region", _filter_neighbours),
    "create creature": Opener("bestiary", lambda ws: ws.action_create_creature()),
    "edit creature": Opener(
        "creature", lambda ws: ws._core_verb("section-cr-info", "edit")
    ),
    "edit creature characteristics": Opener(
        "creature", lambda ws: ws._core_verb("section-cr-characteristics", "edit")
    ),
    "add creature attack": Opener(
        "creature", lambda ws: ws._core_verb("section-cr-attacks", "add")
    ),
    "add creature power": Opener(
        "creature", lambda ws: ws._core_verb("section-cr-powers", "add")
    ),
    "add creature vis": Opener(
        "creature", lambda ws: ws._core_verb("section-cr-vis", "add")
    ),
    "add battle (conflicts)": Opener(
        "conflicts", lambda ws: ws._core_verb("section-conflict-battles", "add")
    ),
    "edit battle (conflicts)": Opener(
        "conflicts",
        _pick(
            lambda ws: ws._core_verb("section-conflict-battles", "edit"),
            "conflict-battles-list",
        ),
    ),
    "battle event (conflicts)": Opener(
        "conflicts",
        _pick(lambda ws: ws.action_conflict_battle_event(), "conflict-battles-list"),
    ),
    "add fight": Opener("conflicts", lambda ws: ws._core_verb("section-fights", "add")),
    "edit fight": Opener(
        "conflicts",
        _pick(lambda ws: ws._core_verb("section-fights", "edit"), "fights-list"),
    ),
    "add siege": Opener("conflicts", lambda ws: ws._core_verb("section-sieges", "add")),
    "edit siege": Opener(
        "conflicts",
        _pick(lambda ws: ws._core_verb("section-sieges", "edit"), "sieges-list"),
    ),
    "add combatant": Opener(
        "conflicts", _pick(lambda ws: ws.action_add_combatant(), "fights-list")
    ),
    "form a group": Opener(
        "conflicts", _pick(lambda ws: ws.action_form_group(), "fights-list")
    ),
    "next blow": Opener(
        "conflicts", _pick(lambda ws: ws.action_next_blow(), "fights-list")
    ),
    "next siege event": Opener(
        "conflicts", _pick(lambda ws: ws.action_next_siege_event(), "sieges-list")
    ),
    "edit secrets": Opener("neighbour", _open_secrets),
    "edit neighbour": Opener(
        "neighbour", lambda ws: ws._core_verb("section-nb-info", "edit")
    ),
    "add castle": Opener(
        "neighbour", lambda ws: ws._core_verb("section-nb-castles", "add")
    ),
    "add gratitude": Opener(
        "neighbour", lambda ws: ws._core_verb("section-nb-gratitude", "add")
    ),
    "add battle": Opener(
        "neighbour", lambda ws: ws._core_verb("section-nb-battles", "add")
    ),
    "battle event": Opener(
        "neighbour",
        _pick(lambda ws: ws.action_battle_event(), "nb-battles-list"),
    ),
    "edit guild": Opener(
        "town",
        _pick(lambda ws: ws._core_verb("section-nb-guilds", "edit"), "nb-guilds-list"),
    ),
    "edit fair": Opener(
        "town",
        _pick(lambda ws: ws._core_verb("section-nb-fairs", "edit"), "nb-fairs-list"),
    ),
    "add charter lord": Opener(
        "town", _built(lambda ws: ws._core_verb("section-nb-charter-lords", "add"))
    ),
    "edit charter terms": Opener(
        "town", _built(lambda ws: ws._core_verb("section-nb-charter-terms", "edit"))
    ),
    "edit charter gives": Opener(
        "town", _built(lambda ws: ws._core_verb("section-nb-charter-gives", "edit"))
    ),
    "add citizen": Opener(
        "town", _built(lambda ws: ws._core_verb("section-nb-citizens", "add"))
    ),
    "edit town people": Opener(
        "town", _built(lambda ws: ws._core_verb("section-nb-town-people", "edit"))
    ),
    "add guild member": Opener(
        "town", _built(lambda ws: ws._core_verb("section-nb-guild-members", "add"))
    ),
    "add court case": Opener(
        "town", _built(lambda ws: ws._core_verb("section-nb-court-cases", "add"))
    ),
    "court roll": Opener("town", _court_roll),
    "add manor": Opener(
        "neighbour", _built(lambda ws: ws._core_verb("section-manors", "add"))
    ),
    "add establishment": Opener(
        "neighbour", _built(lambda ws: ws._core_verb("section-establishments", "add"))
    ),
    "edit household": Opener(
        "neighbour", _built(lambda ws: ws._core_verb("section-household", "edit"))
    ),
    "buy manor": Opener("neighbour", _built(lambda ws: ws.action_buy_manor())),
    "assart": Opener("neighbour", _assart),
    "winter roll": Opener("neighbour", _winter_roll),
    "settle inheritance": Opener(
        "neighbour", _built(lambda ws: ws.action_settle_inheritance())
    ),
    "edit church": Opener(
        "church", lambda ws: ws._core_verb("section-nb-info", "edit")
    ),
    "add relic": Opener("church", lambda ws: ws._core_verb("section-nb-relics", "add")),
    "add faculty": Opener(
        "university", lambda ws: ws._core_verb("section-nb-faculties", "add")
    ),
    "edit master": Opener(
        "university",
        _pick(
            lambda ws: ws._core_verb("section-nb-masters", "edit"), "nb-masters-list"
        ),
    ),
    "edit faction": Opener(
        "faction", lambda ws: ws._core_verb("section-nb-info", "edit")
    ),
    "add stage": Opener("threat", lambda ws: ws._core_verb("section-nb-stages", "add")),
    "edit stage": Opener(
        "threat",
        _pick(
            lambda ws: ws._core_verb("section-nb-stages", "edit"), "nb-stages-list", 1
        ),
    ),
    "edit place": Opener("place", lambda ws: ws._core_verb("section-nb-info", "edit")),
    "found covenant": Opener("place", _found_covenant),
    "add regio level": Opener(
        "place", lambda ws: ws._core_verb("section-nb-levels", "add")
    ),
    "edit place effect": Opener(
        "place",
        _pick(
            lambda ws: ws._core_verb("section-nb-effects", "edit"), "nb-effects-list"
        ),
    ),
    "add trigger": Opener(
        "place", lambda ws: ws._core_verb("section-nb-triggers", "add")
    ),
    "edit looking ahead": Opener(
        "seasons", lambda ws: ws._core_verb("section-seasons-info", "edit")
    ),
    "add calendar entry": Opener(
        "seasons", lambda ws: ws._core_verb("section-ahead", "add")
    ),
    "travel set out": Opener("seasons", lambda ws: ws.action_plan_journey()),
    "travel close": Opener("seasons", lambda ws: ws.action_plan_journey()),
    "edit roll table": Opener(
        "place",
        _pick(lambda ws: ws._core_verb("section-nb-tables", "edit"), "nb-tables-list"),
    ),
    "add place diary entry": Opener(
        "place", lambda ws: ws._core_verb("section-nb-place-diary", "add")
    ),
    "add faction diary entry": Opener(
        "faction", lambda ws: ws._core_verb("section-nb-place-diary", "add")
    ),
    "edit tribunal": Opener(
        "tribunal", lambda ws: ws._core_verb("section-trib-info", "edit")
    ),
    "edit proxies": Opener(
        "tribunal",
        _pick(
            lambda ws: ws._core_verb("section-trib-roster", "edit"), "trib-roster", 1
        ),
    ),
    "hold tribunal": Opener(
        "tribunal",
        _pick(
            lambda ws: ws._core_verb("section-meeting-business", "edit"),
            "meeting-business",
        ),
    ),
    "open the meeting": Opener("tribunal", _open_meeting_step(1, "meeting-business")),
    "attendance and proxies": Opener("tribunal", _open_attendance),
    "hold the debate": Opener("tribunal", _open_meeting_step(3, "meeting-business")),
    "hold the vote": Opener("tribunal", _open_meeting_step(0, "meeting-vote")),
    "hold the rulings": Opener("tribunal", _open_meeting_step(7, "meeting-business")),
    "add case": Opener(
        "tribunal",
        _pick(lambda ws: ws._core_verb("section-trib-cases", "add"), "trib-cases"),
    ),
    "edit case": Opener(
        "tribunal",
        _pick(lambda ws: ws._core_verb("section-trib-cases", "edit"), "trib-cases"),
    ),
    "add ruling": Opener(
        "tribunal",
        _pick(lambda ws: ws._core_verb("section-trib-code", "add"), "trib-code"),
    ),
    "edit treasury loan": Opener(
        "tribunal",
        _pick(
            lambda ws: ws._core_verb("section-trib-treasury", "edit"),
            "trib-treasury",
            2,
        ),
    ),
    "add gild": Opener(
        "tribunal",
        _pick(lambda ws: ws._core_verb("section-trib-gilds", "add"), "trib-gilds-list"),
    ),
    "add tokens": Opener(
        "theban_tribunal",
        _pick(
            lambda ws: ws._core_verb("section-trib-tokens", "add"), "trib-tokens-list"
        ),
    ),
    "add privilege": Opener(
        "transylvania_tribunal",
        _pick(
            lambda ws: ws._core_verb("section-trib-privileges", "add"),
            "trib-privileges-list",
        ),
    ),
    "add ambassador": Opener(
        "hibernia_tribunal",
        _pick(
            lambda ws: ws._core_verb("section-trib-ambassadors", "add"),
            "trib-ambassadors-list",
        ),
    ),
    "edit treaty": Opener(
        "hibernia_tribunal",
        _pick(
            lambda ws: ws._core_verb("section-trib-treaties", "edit"),
            "trib-treaties-list",
        ),
    ),
    "add tenure": Opener(
        "normandy_tribunal",
        _pick(
            lambda ws: ws._core_verb("section-trib-tenure", "add"), "trib-tenure-list"
        ),
    ),
    "edit tourney result": Opener(
        "normandy_tribunal",
        _pick(
            lambda ws: ws._core_verb("section-trib-tourney", "edit"),
            "trib-tourney-list",
            2,
        ),
    ),
    "edit office": Opener(
        "theban_tribunal",
        _pick(
            lambda ws: ws._core_verb("section-trib-archai", "edit"),
            "trib-archai-list",
            1,
        ),
    ),
    "add tribunal diary entry": Opener(
        "tribunal",
        _pick(lambda ws: ws._core_verb("section-trib-diary", "add"), "trib-diary"),
    ),
    # Covenant
    "create character": Opener("covenant", lambda ws: ws.action_create_character()),
    "grog template": Opener(
        "covenant",
        lambda ws: ws._run_steps(
            creation_forms.grog_template_steps(
                ws.saga,
                {"name": "Ulla", "covenant_id": "cov1"},
                grog_templates.find("gt_animal_trainer"),
            ),
            tree=True,
        ),
    ),
    "companion template": Opener(
        "covenant",
        lambda ws: ws._run_steps(
            choice_forms.choice_template_steps(
                ws.saga,
                {"name": "Ulla", "covenant_id": "cov1"},
                choice_templates.find("ct_quick_martial"),
            ),
            tree=True,
        ),
    ),
    "mythic companion template": Opener(
        "covenant",
        lambda ws: ws._run_steps(
            choice_forms.choice_template_steps(
                ws.saga,
                {"name": "Ulla", "covenant_id": "cov1"},
                choice_templates.find("ct_mc_faerie_doctor"),
            ),
            tree=True,
        ),
    ),
    "companion sample": Opener(
        "covenant",
        lambda ws: ws._run_steps(
            choice_forms.choice_template_steps(
                ws.saga,
                {"name": "Ulla", "covenant_id": "cov1"},
                choice_templates.find("ct_anne_holy_hermit"),
            ),
            tree=True,
        ),
    ),
    "grog template as companion": Opener(
        "covenant",
        lambda ws: ws._run_steps(
            choice_forms.grog_companion_steps(
                ws.saga,
                {"name": "Ulla", "covenant_id": "cov1"},
                grog_templates.find("gt_animal_trainer"),
            ),
            tree=True,
        ),
    ),
    "animal template": Opener(
        "covenant",
        lambda ws: ws._run_steps(
            creation_forms.grog_template_steps(
                ws.saga,
                {"name": "Rex", "covenant_id": "cov1"},
                grog_templates.find("at_dog"),
            ),
            tree=True,
        ),
    ),
    "create laboratory": Opener("covenant", lambda ws: ws.action_create_laboratory()),
    "bind familiar": Opener("covenant", lambda ws: ws.action_create_familiar()),
    "edit covenant": Opener("covenant", lambda ws: ws._edit_covenant()),
    "covenant arms": Opener("covenant", lambda ws: ws.action_edit_arms()),
    "edit sketch covenant": Opener("sketch_covenant", lambda ws: ws._edit_covenant()),
    "what matters": Opener(
        "sketch_covenant", lambda ws: ws._core_verb("section-cov-what-matters", "edit")
    ),
    "add reason": Opener(
        "sketch_covenant", lambda ws: ws._core_verb("section-attitudes", "add")
    ),
    "add favour": Opener(
        "sketch_covenant", lambda ws: ws._core_verb("section-favours", "add")
    ),
    "add sketch magus": Opener(
        "sketch_covenant", lambda ws: ws._core_verb("section-cov-magi", "add")
    ),
    "edit covenant description": Opener(
        "covenant", lambda ws: ws._edit_covenant_description()
    ),
    "edit boon": Opener("covenant", lambda ws: ws._edit_boon_hook_at("Boon", 0)),
    # The fixture's Hook (Contested Resource) may be Unknown.
    "edit hook": Opener("covenant", lambda ws: ws._edit_boon_hook_at("Hook", 1)),
    "improve income": Opener(
        "covenant",
        lambda ws: ws._improve_form(ws.selected_covenant.economics.income_sources[0]),
    ),
    "edit personality trait": Opener(
        "character",
        lambda ws: ws._edit_trait_at(
            scr._CHARACTER_TRAITS, ws.selected_character.personality_traits, 0
        ),
    ),
    "edit covenant weapon": Opener(
        "covenant",
        lambda ws: ws._possession_form("weapon", ws._possession_entries("weapon")[0]),
    ),
    "edit covenant armor": Opener(
        "covenant",
        lambda ws: ws._possession_form("armor", ws._possession_entries("armor")[0]),
    ),
    # Character
    "edit character info": Opener("character", lambda ws: ws._edit_character_info()),
    "edit character traditions": Opener(
        "character", lambda ws: ws.action_edit_traditions()
    ),
    "edit characteristics": Opener("character", lambda ws: ws._edit_characteristics()),
    "edit biographical detail": Opener(
        "character", lambda ws: ws._edit_biographical_detail()
    ),
    "edit aging": Opener("character", lambda ws: ws._edit_aging()),
    "edit wounds": Opener("character", lambda ws: ws._edit_wounds()),
    "edit fatigue": Opener("character", lambda ws: ws._edit_fatigue()),
    "edit hermetic background": Opener(
        "character", lambda ws: ws._edit_hermetic_background()
    ),
    "edit ability": Opener("character", lambda ws: ws._edit_ability_at(0)),
    "edit raw vis": Opener("character", lambda ws: ws._edit_raw_vis_at(0)),
    "give raw vis": Opener(
        "character",
        lambda ws: ws._run_steps(
            giving.give(
                ws.saga,
                giving.VIS,
                ws.selected_character,
                vis.held(ws.selected_character)[0],
            )
        ),
    ),
    "add research goal": Opener("character", lambda ws: ws._add_research_goal()),
    "add integration goal": Opener("character", lambda ws: ws._add_research_goal()),
    "add secret research goal": Opener("character", lambda ws: ws._add_research_goal()),
    "add tradition effect": Opener("character", _open_tradition_effect),
    "add power": Opener("character", _open_power),
    "add agent": Opener("character", _open_agent),
    "set agent task": Opener("character", _open_agent_task),
    "resolve agent task": Opener("character", _open_agent_resolve),
    "spend agency xp": Opener("character", _open_agency_spend),
    "labor from story": Opener("character", _open_labor_story),
    "invest time or money": Opener("character", _open_invest_labor),
    "add constant effect": Opener("character", _open_constant_effect),
    "add bound being": Opener("character", _open_bound_being),
    "virtue parameters": Opener("character", _open_param_prompt),
    "virtue ability choice": Opener(
        "character", lambda ws: _open_param_prompt(ws, "vf_puissant_ability")
    ),
    "change virtue choice": Opener("character", _open_virtue_change),
    "add mastery ability": Opener("character", _open_mastery_ability),
    "edit spell mastery": Opener("character", lambda ws: ws._edit_spell_mastery_at(0)),
    "add personal weapon": Opener(
        "character", lambda ws: ws._inventory_item_form("weapon", None)
    ),
    # Familiar
    "edit familiar info": Opener("familiar", lambda ws: ws._edit_familiar_info()),
    "edit familiar binding": Opener("familiar", lambda ws: ws._edit_familiar_binding()),
    "edit familiar characteristics": Opener(
        "familiar", lambda ws: ws._edit_familiar_characteristics()
    ),
    "edit familiar wounds": Opener("familiar", lambda ws: ws._edit_familiar_wounds()),
    "edit natural weapon": Opener(
        "familiar", lambda ws: ws._familiar_natural_weapon_form(0)
    ),
    # Laboratory
    "edit lab identity": Opener("laboratory", lambda ws: ws._edit_lab_identity()),
    "add lab trait": Opener("laboratory", _open_lab_trait),
    "lab virtue choice": Opener("laboratory", _open_lab_choice_prompt),
    "change lab virtue choice": Opener("laboratory", _open_lab_virtue_change),
    "lab servant": Opener(
        "laboratory",
        lambda ws: _open_lab_choice_prompt(
            ws, "section-lab-vf-virtues", "labvf_servant"
        ),
    ),
    "edit lab characteristics": Opener(
        "laboratory", lambda ws: ws._edit_lab_characteristics()
    ),
    "add lab specialization source": Opener(
        "laboratory", lambda ws: ws._add_specialty_entry()
    ),
    "add lab magic item points": Opener(
        "laboratory",
        lambda ws: ws._run_steps(
            lab_item.points_form(
                ws.saga,
                ws.saga.laboratories[0],
                None,
                lab_item.ItemChoice("dev-lab", "eff1", lab_item.ITEM, lab_item.POINTS),
            )
        ),
    ),
    "edit lab feature": Opener(
        "laboratory",
        lambda ws: ws._feature_details(
            ws.saga.laboratories[0],
            ws.saga.laboratories[0].features[0],
            "labfeat_window",
            "labvf1",
        ),
    ),
    "add lab room": Opener("laboratory", lambda ws: ws._add_named("section-lab-rooms")),
    "reward or punish": Opener(
        "character",
        lambda ws: ws._run_steps(
            grog_forms.discipline_form(ws.saga, ws.saga.character("grog9"))
        ),
    ),
    "retire a grog": Opener(
        "character",
        lambda ws: ws._run_steps(
            grog_forms.pension_form(ws.saga, ws.saga.character("grog9"))
        ),
    ),
    "craft by magic": Opener("character", lambda ws: ws.action_craft_by_magic()),
    "grog yearly update": Opener(
        "character",
        lambda ws: ws._grog_year_for(ws.saga.character("grog9"), "section-char-season"),
    ),
    "add arcane connection": Opener("laboratory", lambda ws: ws._add_connection()),
    "add lab diary entry": Opener("laboratory", lambda ws: ws._add_diary_entry()),
    # Seasons
    "plan a season": Opener("character", lambda ws: ws._plan_season()),
    "plan an initiation": Opener("character", lambda ws: ws._plan_season()),
    "add character diary entry": Opener(
        "character", lambda ws: ws._add_character_diary_entry()
    ),
    "add covenant diary entry": Opener(
        "covenant", lambda ws: ws._add_covenant_diary_entry()
    ),
    "add hidden resources story event": Opener(
        "covenant", lambda ws: _add_story_event_with_pools(ws)
    ),
    "add illusory resources story event": Opener(
        "covenant", lambda ws: _add_story_event_with_pools(ws)
    ),
    # Enchanted devices
    "edit enchanted device": Opener(
        "laboratory", lambda ws: ws._edit_device(_device(ws, "dev-lab"))
    ),
    "instill effect": Opener(
        "laboratory", lambda ws: ws._effect_form(_device(ws, "dev-lab"), None)
    ),
    "edit charged item effect": Opener(
        "covenant",
        lambda ws: ws._effect_form(
            _device(ws, "dev-cov"), _device(ws, "dev-cov").effects[0]
        ),
    ),
    # Forms that had only bespoke tests
    "edit covenant reputation": Opener(
        "covenant",
        lambda ws: ws._edit_trait_at(
            _COVENANT_REPUTATIONS, ws.selected_covenant.reputations, 0
        ),
    ),
    "add boon": Opener("covenant", _open_boon_details),
    "add property": Opener(
        "covenant", lambda ws: ws._possession_form("property", None)
    ),
    "add sanctum": Opener("covenant", lambda ws: ws._possession_form("sanctum", None)),
    "add covenant item": Opener(
        "covenant", lambda ws: ws._possession_form("item", None)
    ),
    "add vis source": Opener(
        "covenant", lambda ws: ws._possession_form("vis_source", None)
    ),
    "add vis store": Opener(
        "covenant", lambda ws: ws._possession_form("vis_store", None)
    ),
    "edit wealth": Opener("covenant", lambda ws: ws._edit_wealth()),
    "add income source": Opener("covenant", lambda ws: ws._income_form(None)),
    "add covenant manor": Opener(
        "covenant", _built(lambda ws: ws._core_verb("section-manors", "add"))
    ),
    "edit manor check": Opener(
        "covenant", _built(lambda ws: ws._core_verb("section-manor-check", "edit"))
    ),
    "edit income source": Opener(
        "covenant", _pick(lambda ws: ws._edit_income_source(), "eco-income-list")
    ),
    "edit expenditure row": Opener(
        "covenant", _economics_row("expenditure", "buildings")
    ),
    "edit tithes": Opener("covenant", _economics_row("expenditure", "tithes")),
    "edit sundry": Opener("covenant", _economics_row("expenditure", "sundry")),
    "edit magic savings": Opener("covenant", _economics_row("savings", "magic")),
    "edit loyalty": Opener("covenant", lambda ws: ws._edit_loyalty()),
    "edit population": Opener("covenant", lambda ws: ws._edit_population()),
    "edit miscellaneous": Opener("covenant", lambda ws: ws._edit_miscellaneous()),
    "add magus": Opener(
        "covenant", lambda ws: ws._inhabitant_form("magus", None, None)
    ),
    "add turb": Opener("covenant", lambda ws: ws._inhabitant_form("turb", None, None)),
    "add covenfolk member": Opener(
        "covenant", lambda ws: ws._inhabitant_form("inhabitant", None, None)
    ),
    "add craftsperson": Opener(
        "covenant", lambda ws: ws._inhabitant_form("craftsperson", None, None)
    ),
    "add horses": Opener(
        "covenant", lambda ws: ws._inhabitant_form("horse", None, None)
    ),
    "add book": Opener("covenant", lambda ws: ws._book_form(None)),
    "edit book": Opener(
        "covenant",
        lambda ws: ws._book_form(next(b for b in ws.saga.books if b.id == "b-cov")),
    ),
    "add book into a codex": Opener("covenant", lambda ws: ws._book_form(None)),
    "add commentary": Opener("covenant", lambda ws: ws._book_form(None)),
    "book craftsmanship": Opener("covenant", _open_book_craft),
    "enchant a book": Opener(
        "covenant",
        lambda ws: ws._book_form(next(b for b in ws.saga.books if b.id == "b-cov")),
    ),
    "research bonuses": Opener("covenant", _open_research_bonuses),
    "add lab text": Opener("laboratory", lambda ws: ws._book_form(None)),
    "perform ritual again": Opener("laboratory", lambda ws: ws.action_perform_ritual()),
    "lab texts read": Opener("character", lambda ws: ws._edit_lab_text_access()),
    "add house rule": Opener("saga", lambda ws: ws._house_rule_form(None)),
    "add player": Opener("saga_content", lambda ws: ws._player_form(None)),
    "edit traditions offered": Opener("saga_content", lambda ws: ws._edit_traditions()),
    "add spell": Opener("saga_content", lambda ws: ws._spell_form(None)),
    "edit spell": Opener("saga_content", lambda ws: ws._spell_form(ws.saga.spells[0])),
    "add saga source": Opener("saga_content", lambda ws: ws._saga_source_form(None)),
    "edit saga source": Opener("saga_content", _open_saga_source),
    "edit catalog": Opener("saga_content", lambda ws: ws._catalog_form("spells")),
    "hide catalog entry": Opener("saga_content", lambda ws: ws._hide_catalog_entry()),
    "add good": Opener("saga_content", _open_good),
    "add purity": Opener("saga_content", _open_purity),
    "add ability": Opener("character", _open_ability_details),
    "edit arts": Opener("character", lambda ws: ws._edit_arts()),
    "edit familiar fatigue": Opener("familiar", lambda ws: ws._edit_familiar_fatigue()),
    "add bond power": Opener("familiar", lambda ws: ws._familiar_bond_power_form(None)),
    "edit bond power": Opener("familiar", lambda ws: ws._familiar_bond_power_form(0)),
    "add lab raw vis": Opener("laboratory", lambda ws: ws._add_lab_raw_vis()),
    "edit lab raw vis": Opener(
        "laboratory", _pick(lambda ws: ws._edit_lab_raw_vis(), "lab-raw-vis-list")
    ),
    "edit lab diary entry": Opener(
        "laboratory", _pick(lambda ws: ws._edit_diary_entry(), "lab-diary-list")
    ),
    "edit lab specialization source": Opener(
        "laboratory",
        _pick(lambda ws: ws._edit_specialty_entry(), "lab-specialties-list"),
    ),
    "edit lab room": Opener(
        "laboratory",
        _pick(lambda ws: ws._edit_named("section-lab-rooms"), "lab-rooms-list"),
    ),
    # Creation Worksheet: the core's steps (worksheet_forms), run by the
    # terminal's step runner.
    "spend creation xp": Opener(
        "character",
        lambda ws: ws._run_steps(
            wf.spend_xp(
                ws.saga,
                ws.selected_character,
                "childhood",
                creation_xp.childhood_targets(),
            )
        ),
    ),
    "native language": Opener(
        "character",
        lambda ws: ws._run_steps(wf.native_language(ws.selected_character)),
    ),
    # The fixture's grog, Hugo, made a dog.
    "animal form": Opener(
        "character",
        lambda ws: ws._run_steps(
            animal_forms.animal_form(ws.saga, ws.saga.character("grog9"))
        ),
    ),
    "general spell level": Opener(
        "character",
        lambda ws: ws._run_steps(
            wf.spell_level_form(
                ws.selected_character,
                "apprenticeship_spells",
                catalog.find_spell(ws.saga, "spell_aegis_of_the_hearth"),
            )
        ),
    ),
    "gauntlet conditions": Opener(
        "character",
        lambda ws: ws._run_steps(wf.gauntlet_conditions(ws.selected_character)),
    ),
    "grogs aging chart": Opener("character", _grogs_aging_chart),
    "power level": Opener(
        "covenant", lambda ws: ws._run_steps(wf.power_level(ws.selected_covenant))
    ),
    "buy specialist": Opener(
        "covenant",
        lambda ws: ws._run_steps(wf.buy_specialist(ws.saga, ws.selected_covenant)),
    ),
    "edit charter": Opener(
        "covenant",
        lambda ws: _open_charter_verb(ws, "section-cov-charter", "edit"),
    ),
    "add clause": Opener(
        "covenant",
        lambda ws: _open_charter_verb(ws, "section-cov-clauses", "add"),
    ),
    "edit clause": Opener("covenant", _open_edit_clause),
    "break clause": Opener("covenant", _open_break_clause),
    "seal charter": Opener("covenant", _open_seal_charter),
    # The Theban treasury's loans of vis.
    "lend vis": Opener(
        "theban_tribunal",
        _pick(lambda ws: ws.action_lend_vis(), "trib-tokens-list"),
    ),
    "childhood blanks": Opener(
        "character",
        lambda ws: ws._run_steps(
            wf.use_childhood(
                ws.selected_character,
                next(c for c in creation_xp.CHILDHOODS if c.name == "Traveling"),
            )
        ),
    ),
    # A craftsman's sale of his finished goods (City & Guild).
    "sell finished goods": Opener("character", _open_sell_goods),
    # Complexion, with Art & Academe's medicine.
    "edit biographical detail (complexion)": Opener(
        "character", lambda ws: _open_biographical_academe(ws)
    ),
    # The Rhine's ranks and its meeting's rite.
    "mark of approval": Opener("tribunal", _open_rhine_verb("rhine_mark")),
    "archmage's challenge": Opener("tribunal", _open_rhine_verb("rhine_challenge")),
    "rhine rite": Opener("tribunal", _open_rhine_rite),
    # A young character's parent's vocation (Apprentices).
    "parent vocation": Opener(
        "character",
        lambda ws: ws._run_steps(wf.parent_vocation(ws.selected_character)),
    ),
    # Art & Academe's ligatures and the apothecary's store.
    "make a ligature": Opener("character", lambda ws: _open_apothecary(ws, "ligature")),
    "apothecary's store": Opener("character", lambda ws: _open_apothecary(ws, "store")),
    # The Theban Tribunal's Byzantine customs (The Sundered Eagle).
    "hermetic letter": Opener("character", lambda ws: _open_byzantine(ws, "letter")),
    "invoke a broken oath": Opener("character", lambda ws: _open_byzantine(ws, "oath")),
    "make greek fire": Opener("character", lambda ws: _open_byzantine(ws, "fire")),
    "paint an icon": Opener("character", lambda ws: _open_byzantine(ws, "paint")),
    "venerate an icon": Opener("character", lambda ws: _open_byzantine(ws, "venerate")),
    "a mother's curse": Opener("character", lambda ws: _open_byzantine(ws, "curse")),
    # Sin, tarnish and the Goetic Arts (RoP: The Infernal).
    "confidence through sin": Opener("character", lambda ws: _open_sin(ws, "sin")),
    "infernal influence": Opener("character", lambda ws: _open_sin(ws, "influence")),
    "ars goetia": Opener("character", lambda ws: _open_sin(ws, "goetia")),
    # Transylvania's promissory notes (Against the Dark).
    "add promissory note": Opener(
        "transylvania_tribunal", lambda ws: _open_treasury_kind(ws, "note")
    ),
    # The hunt and Area Lore, on a manor and on the road (LoM, C&G).
    "hunt on a manor": Opener("neighbour", lambda ws: _on_hagen(ws, "hunt")),
    "area lore on a manor": Opener("neighbour", lambda ws: _on_hagen(ws, "lore")),
    "hunt on the road": Opener("seasons", lambda ws: ws.action_hunt_on_journey()),
    "area lore on the road": Opener(
        "seasons", lambda ws: ws.action_area_lore_on_journey()
    ),
    # An apprentice's magic and the Gauntlet (Apprentices).
    "turbulence": Opener("character", lambda ws: _open_apprentice(ws, "turbulence")),
    "the gauntlet": Opener("character", lambda ws: _open_apprentice(ws, "gauntlet")),
    "lose the gift": Opener("character", lambda ws: _open_apprentice(ws, "lose")),
    "learn a cantation": Opener(
        "character", lambda ws: _open_apprentice(ws, "cantation")
    ),
    # Art & Academe's artists and scholars, between their seasons.
    "an artist's career": Opener("character", lambda ws: _open_career(ws, "artist")),
    "a scholar's career": Opener("character", lambda ws: _open_career(ws, "scholar")),
    # Dealing with faeries (RoP: Faerie).
    "ars fabulosa": Opener("character", lambda ws: _open_faerie(ws, "ars")),
    "a faerie bargain": Opener("character", lambda ws: _open_faerie(ws, "bargain")),
    "an offer to faerie": Opener("character", lambda ws: _open_faerie(ws, "offer")),
    # The lacuna and the pilgrim (HoH:S, The Church).
    "cast in a lacuna": Opener("character", lambda ws: ws.action_cast_in_lacuna()),
    "pilgrimage": Opener("character", lambda ws: ws.action_pilgrimage()),
    # Hermetic law on the docket (HoH:S, HoH:TL).
    "add wizard's war": Opener(
        "tribunal",
        _pick(lambda ws: ws._core_verb("section-trib-cases", "add"), "trib-cases"),
    ),
    # Devotion and the saints (The Church, RoP: The Divine).
    "invoke a saint": Opener("character", lambda ws: ws.action_invoke_saint()),
    "threaten a saint": Opener("character", lambda ws: ws.action_threaten_saint()),
    "devotion points": Opener("character", lambda ws: ws.action_devotion_points()),
    "indulgence, vigil or fast": Opener(
        "character", lambda ws: ws.action_act_of_piety()
    ),
    # Holy influence and tempers (RoP: The Divine).
    "holy influence": Opener("character", lambda ws: ws.action_holy_influence()),
    # Mystic paths, God's aid, the Font and the Commanding Aura.
    "mystic path": Opener("character", lambda ws: _open_mystic(ws, "path")),
    "spiritual path": Opener("character", lambda ws: _open_mystic(ws, "spiritual")),
    "monistic revelation": Opener(
        "character", lambda ws: _open_mystic(ws, "revelation")
    ),
    "invoke god's aid": Opener("character", lambda ws: _open_mystic(ws, "aid")),
    "font of knowledge": Opener("character", lambda ws: _open_mystic(ws, "font")),
    "commanding aura": Opener("character", lambda ws: _open_mystic(ws, "aura")),
    # House Verditius's Hubris and vendettas.
    "hubris": Opener("character", lambda ws: _open_hubris(ws)),
}


def _open_biographical_academe(ws) -> None:
    """Edit Biographical Detail with Art & Academe's medicine on."""
    ws.saga.rule_options = {**ws.saga.rule_options, "art_academe_medicine": True}
    ws._edit_biographical_detail()


def _device(ws, device_id: str):
    return next(d for d in ws.saga.enchanted_devices if d.id == device_id)


async def until(condition, timeout: float = 3.0) -> bool:
    """Wait (without a pilot) until `condition()` holds."""
    elapsed = 0.0
    while not condition() and elapsed < timeout:
        await asyncio.sleep(0.02)
        elapsed += 0.02
    return bool(condition())


async def wait_for_screen(app, cls, timeout: float = 3.0):
    """Wait (without a pilot) until the top screen is a `cls`."""
    await until(lambda: isinstance(app.screen, cls), timeout)
    return app.screen


async def open_dialog(
    pilot, app, name: str, saga: Saga | None = None
) -> tuple[object, object]:
    """Start at the saga picker with `saga` saved (default contract_saga()),
    reach `name`'s tree node and open the dialog. Returns (the screen the
    dialog was opened from, the dialog)."""
    opener = OPENERS[name]
    await pilot.pause()
    if opener.node is None:
        base = app.screen
    else:
        await pilot.press("enter")  # picker -> workspace
        assert await wait_until(
            pilot, lambda: isinstance(app.screen, scr.WorkspaceScreen)
        )
        base = app.screen
        tree = base.query_one(Tree)

        def find_node():
            stack = [tree.root]
            while stack:
                candidate = stack.pop()
                if candidate.data == NODES[opener.node]:
                    return candidate
                stack.extend(candidate.children)
            return None

        assert await wait_until(pilot, lambda: find_node() is not None)
        tree.select_node(find_node())
        assert await wait_until(
            pilot, lambda: base.selected_kind == NODES[opener.node][0]
        )
        if opener.node not in ("saga", "book_group"):
            assert await wait_until(
                pilot, lambda: base._current_sheet_view() is not None
            )
            view = base._current_sheet_view()
            assert await wait_until(pilot, lambda: view.initial_tab_seen)
        await pilot.pause()
    return base, await reopen_dialog(pilot, app, base, name)


async def reopen_dialog(pilot, app, base, name: str) -> object:
    """Open `name`'s dialog again from `base` (the screen open_dialog
    returned, back on top), and return it."""
    opened = OPENERS[name].open(base)
    if inspect.isawaitable(opened):
        await opened
    assert await wait_until(pilot, lambda: _is_dialog(app.screen, base), timeout=3.0), (
        f"{name!r} didn't open (top screen: {type(app.screen).__name__})"
    )
    await pilot.pause()
    return app.screen


#: Screens a dialog is opened through (not the dialog itself).
_ON_THE_WAY = (
    scr.VirtueFlawPickerScreen,
    ListFieldScreen,
    scr.RemovalPickerScreen,
    scr.AbilityPickerScreen,
    scr.CovenantBoonHookPickerScreen,
)


def _is_dialog(screen, base) -> bool:
    return (
        screen is not base
        and isinstance(screen, ModalScreen)
        and not isinstance(screen, _ON_THE_WAY)
    )


def new_app(saga: Saga | None = None) -> ArsMagicaManagerApp:
    storage.save_saga(saga if saga is not None else contract_saga())
    return ArsMagicaManagerApp()


Opens = Callable[..., Awaitable[tuple[object, object]]]


def _open_byzantine(ws, which: str) -> None:
    """A Byzantine custom's More command on Leandro: painting needs him a
    priest with Theology 3, venerating an icon on Cologne's Relics."""
    character = ws.selected_character
    if which == "paint":
        character.virtues_flaws.append(VirtueFlawInstance("vf_eastern_priest"))
        character.abilities.append(Ability("Theology: Christian", xp=30))
    if which == "venerate":
        church = ws.saga.neighbour("cologne")
        church.details.setdefault("relics", []).append(
            {
                "name": "The Hodegetria",
                "saint": "the Theotokos",
                "kind": "eikon",
                "quality": 12,
            }
        )
    {
        "letter": ws.action_theban_letter,
        "oath": ws.action_invoke_oath,
        "fire": ws.action_make_greek_fire,
        "paint": ws.action_paint_icon,
        "venerate": ws.action_venerate_icon,
        "curse": ws.action_mothers_curse,
    }[which]()


def _open_sin(ws, which: str) -> None:
    """More's Confidence through Sin, Infernal Influence or Ars Goetia on
    Leandro, given a cruel streak and the Summoning Art."""
    character = ws.selected_character
    if not any(t.name == "Cruel (Envious)" for t in character.personality_traits):
        character.personality_traits.append(ScoredTrait("Cruel (Envious)", 3))
    if not any(a.name == "Summoning" for a in character.abilities):
        character.abilities.append(Ability("Summoning", xp=55, xp_table="art"))
    if which == "sin":
        ws.action_indulge_sin()
    elif which == "influence":
        ws.action_infernal_influence()
    else:
        ws.action_ars_goetia()


def _open_treasury_kind(ws, kind: str) -> None:
    """The treasury's Add on Transylvania, with `kind` chosen."""
    ops = tribunal_forms.treasury_ops(ws.saga.tribunal("transylvania"))
    assert ops.add is not None
    ws._run_steps(ops.add().apply(kind))


async def _on_hagen(ws, which: str) -> None:
    """The Hunt or Area Lore on Gottfried's manor of Hagen."""
    await _on_lords_row(
        ws,
        "section-manors",
        "manor_list",
        [{"name": "Hagen", "acres": 600}],
        lambda ws: (
            ws.action_hunt_on_manor()
            if which == "hunt"
            else ws.action_area_lore_on_manor()
        ),
    )


def _open_apprentice(ws, which: str) -> None:
    """Turbulence, the Gauntlet, Lose the Gift or Learn a Cantation on
    Leandro, made an apprentice (and the cantations option turned on)."""
    character = ws.selected_character
    if which in ("gauntlet", "lose") and not any(
        vf.vf_id == "vf_apprentice" for vf in character.virtues_flaws
    ):
        character.virtues_flaws.append(VirtueFlawInstance("vf_apprentice"))
    if which == "turbulence":
        ws.action_turbulence()
    elif which == "gauntlet":
        ws.action_gauntlet()
    elif which == "lose":
        ws.action_lose_the_gift()
    else:
        ws.saga.rule_options["cantations_in_play"] = True
        ws.action_learn_cantation()


def _open_career(ws, which: str) -> None:
    """An Artist's Career (Leandro given Craft: Painting) or A Scholar's
    Career on Leandro."""
    character = ws.selected_character
    if which == "artist":
        if not any(a.name == "Craft: Painting" for a in character.abilities):
            character.abilities.append(Ability("Craft: Painting", xp=15))
        ws.action_artist_career()
    else:
        ws.action_scholar_career()


def _open_faerie(ws, which: str) -> None:
    """Ars Fabulosa, A Faerie Bargain or An Offer to Faerie on Leandro,
    given (Faerie) Summoning and an Oak +2 Sympathy Trait."""
    character = ws.selected_character
    if not any(a.name == "(Faerie) Summoning" for a in character.abilities):
        character.abilities.append(Ability("(Faerie) Summoning", xp=15, xp_table="art"))
    if not any(t.name == "Oak" for t in character.personality_traits):
        character.personality_traits.append(ScoredTrait("Oak", 2, type="Sympathy"))
    if which == "ars":
        ws.action_ars_fabulosa()
    elif which == "bargain":
        ws.action_faerie_bargain()
    else:
        ws.action_faerie_offer()


def _open_mystic(ws, which: str) -> None:
    """A holy life's More forms on the magus on show, made Pious +3 with
    Sense Holiness and Unholiness and Confidence to spend: a contemplative
    on a path to Premonitions, a monist after an Ascent, the Font of
    Knowledge, or an archbishop."""
    character = ws.selected_character
    if not any(t.name == "Pious" for t in character.personality_traits):
        character.personality_traits.append(ScoredTrait("Pious", 3))
    if not any(a.name == "Sense Holiness and Unholiness" for a in character.abilities):
        character.abilities.append(
            Ability("Sense Holiness and Unholiness", "Supernatural", xp=5)
        )
    character.background.confidence_points = max(
        3, character.background.confidence_points
    )
    if which == "path":
        ws.action_mystic_path()
    elif which == "spiritual":
        ds.set_path(character, my.CONTEMPLATIVE)
        if my.find_path(character, "Premonitions") is None:
            my.begin(character, "Premonitions", "minor_holy")
        ws.action_spiritual_path()
    elif which == "revelation":
        ds.set_path(character, my.MONISTIC)
        if not ds.ascents(character):
            ds.note_ascent(character)
        ws.action_monistic_revelation()
    elif which == "aid":
        ws.action_gods_aid()
    elif which == "font":
        if not any(a.name == "Font of Knowledge" for a in character.abilities):
            character.abilities.append(
                Ability("Font of Knowledge", "Supernatural", xp=5)
            )
        ws.action_font_of_knowledge()
    else:
        character.background.church_rank = "Archbishop"
        ws.action_commanding_aura()


def _open_hubris(ws) -> None:
    """More's Hubris on the magus on show, given the Flaw and Hubris 1."""
    character = ws.selected_character
    if VirtueFlawInstance("vf_hubris") not in character.virtues_flaws:
        character.virtues_flaws.append(VirtueFlawInstance("vf_hubris"))
    if not any(t.name == "Hubris" for t in character.personality_traits):
        character.personality_traits.append(ScoredTrait("Hubris", 1))
    ws.action_verditius_hubris()
