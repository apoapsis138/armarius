"""How to reach each form dialog the way the app does: which tree node to
select and which WorkspaceScreen handler (or picker hook) opens it. Shared
by the dialog contract tests; see dialog_contract_support.py."""

import asyncio
import inspect
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from support import NODES, everything_saga, wait_until
from textual.screen import ModalScreen
from textual.widgets import TabbedContent, Tree

from ars_magica_manager import (
    battle_muster,
    catalog,
    choice_templates,
    combat_options_form,
    giving,
    grog_templates,
    guest_stays,
    meeting,
    melee_events,
    menagerie,
    neighbour_filter,
    siege_actions,
    staged_projects,
    storage,
    tombs,
    vis,
)
from ars_magica_manager import economics as eco
from ars_magica_manager import goods as gd
from ars_magica_manager import house_rules as hr
from ars_magica_manager import mystery_cults as cult_core
from ars_magica_manager.forms import agents as agent_forms
from ars_magica_manager.forms import animal as animal_forms
from ars_magica_manager.forms import certamen_duel as certamen_forms
from ars_magica_manager.forms import charter as charter_forms
from ars_magica_manager.forms import choice_templates as choice_forms
from ars_magica_manager.forms import covenant as cov_forms
from ars_magica_manager.forms import covers as cover_forms
from ars_magica_manager.forms import creation as creation_forms
from ars_magica_manager.forms import (
    grog_story,
    lab_item,
    ship_build,
    whereabouts,
    wizards_war,
)
from ars_magica_manager.forms import grogs as grog_forms
from ars_magica_manager.forms import hook_stories as hook_story_forms
from ars_magica_manager.forms import inhabitant as inhabitant_forms
from ars_magica_manager.forms import land_shaping as land_forms
from ars_magica_manager.forms import threshold as threshold_forms
from ars_magica_manager.forms import trait_roll as trait_roll_forms
from ars_magica_manager.forms import tribunal as tribunal_forms
from ars_magica_manager.forms import worksheet as wf

# Hermetic Projects (a covenant's Great Tower; Wizard's War's tunnels).
from ars_magica_manager.models import (
    CLAUSE_BROKEN,
    STORY_EVENT,
    Ability,
    AbilityDef,
    Agent,
    Argument,
    ArtScore,
    Battle,
    BattleSide,
    Book,
    BoundBeing,
    Case,
    Character,
    CharterClause,
    CovenantDiaryEntry,
    CraftDevice,
    CultDegree,
    CultScript,
    DeepCover,
    GuestStay,
    HermeticProject,
    IncomeSource,
    Inhabitant,
    KnownSpell,
    LandProject,
    Marriage,
    MysteryCult,
    Neighbour,
    PolemicText,
    Possession,
    Progress,
    ProjectWork,
    Saga,
    SagaSource,
    ScoredTrait,
    Ship,
    Spell,
    VirtueFlawInstance,
)
from ars_magica_manager.models.criamon import Stigma
from ars_magica_manager.models.menagerie import Beast, Breeding
from ars_magica_manager.rules import covenfolk, creation_xp, hermetic_law
from ars_magica_manager.rules import devotion as devotion_rules
from ars_magica_manager.rules import divine_state as ds
from ars_magica_manager.rules import mysticism as my
from ars_magica_manager.rules.xp import ability_xp as cult_ability_xp
from ars_magica_manager.sections import (
    BEASTS_SECTION,
    BREEDINGS_SECTION,
    PROJECT_DEVICES_SECTION,
    PROJECT_WORKS_SECTION,
    STAGE_WORKS_SECTION,
    STAGED_STAGES_SECTION,
    TOWER_SECTION,
)
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


def _refused_then_threaten(ws) -> None:
    """Threaten a Saint, once The Magi have refused his invocation: only
    then is it offered (RoP: The Divine p. 87)."""
    devotion_rules.note_answer(ws.selected_character, "The Magi", False, "Spring", 1220)
    ws.action_threaten_saint()


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


def _move_to_source(ws) -> None:
    """Move to Source, with a saga source and a House Rule to move, made in
    memory (saved only with the move)."""
    if not ws.saga.sources:
        ws.saga.sources.append(SagaSource("HR", "House rules"))
    if not hr.all_entries(ws.saga):
        hr.add(
            ws.saga, hr.CHARACTER, {"name": "Ours", "type": "Virtue", "tier": "Minor"}
        )
    ws.action_move_to_source()


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


async def _grow_a_story(ws) -> None:
    """Grow into a Threat on an open story the troupe's covenant's Diary
    holds, chosen on the Region's Open Stories."""
    covenant = ws.saga.covenants[0]
    covenant.played = True
    # The contract opens the form several times: one story is enough.
    if not any(e.name == "A salamander in the lab" for e in covenant.diary):
        covenant.diary.append(
            CovenantDiaryEntry(
                1220,
                "Summer",
                "A salamander in the lab",
                "It may want to become his familiar.",
                category=STORY_EVENT,
                status="Open",
                concerns="characters:mag1",
            )
        )
    view = ws._current_sheet_view()
    view.refresh_all()
    rows = view.query_one("#region-stories-list", scr.SelectableList)
    await until(lambda: rows.row_count > 1)
    rows.select_data_index(0)
    await until(lambda: rows.selected_data_index == 0)
    ws.action_grow_story()


async def _take_up_a_story(ws) -> None:
    """Take Up the Tale on an open story, chosen (and focused) on the
    Region's Open Stories."""
    await _grow_a_story_chosen(ws)
    ws.action_take_up_story()


async def _grow_a_story_chosen(ws) -> None:
    """The open story of _grow_a_story, chosen and focused on the Region's
    Open Stories."""
    covenant = ws.saga.covenants[0]
    covenant.played = True
    if not any(e.name == "A salamander in the lab" for e in covenant.diary):
        covenant.diary.append(
            CovenantDiaryEntry(
                1220,
                "Summer",
                "A salamander in the lab",
                category=STORY_EVENT,
                status="Open",
            )
        )
    view = ws._current_sheet_view()
    view.refresh_all()
    rows = view.query_one("#region-stories-list", scr.SelectableList)
    await until(lambda: rows.row_count > 1)
    rows.select_data_index(0)
    rows.focus()
    await until(lambda: ws._active_section() == "section-region-stories")


def _with_crown_on_a_track(ws) -> None:
    """Add a trigger once the Hollow Crown moves along a track, which a
    trigger can move."""
    crown = ws.saga.neighbour("crown")
    crown.details["moves"] = "A track"
    ws._core_verb("section-nb-triggers", "add")


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


def _with_broken_clause(ws, *, notarized: bool = False):
    """The covenant's one clause broken by Leandro (and its charter
    notarized, so a breach can be charged at Tribunal)."""
    covenant = _with_clause(ws)
    clause = covenant.charter_of_covenant.clauses[0]
    clause.status, clause.since_year = CLAUSE_BROKEN, 1220
    clause.note = "Leandro kept the Vim vis."
    covenant.charter_of_covenant.ratified = notarized
    return covenant


async def _open_censure_clause(ws) -> None:
    covenant = _with_broken_clause(ws)
    await ws._current_sheet_view().build_all_tabs()
    ws._run_steps(charter_forms.censure_clause(ws.saga, covenant, 0))


async def _open_charge_clause(ws) -> None:
    covenant = _with_broken_clause(ws, notarized=True)
    await ws._current_sheet_view().build_all_tabs()
    ws._run_steps(charter_forms.charge(ws.saga, covenant, 0))


async def _open_use_template(ws) -> None:
    await ws._current_sheet_view().build_all_tabs()
    ws.action_use_charter_template()


async def _open_save_template(ws) -> None:
    _with_clause(ws)
    await ws._current_sheet_view().build_all_tabs()
    ws.action_save_charter_template()


def _with_guest(ws):
    """Severinus of Fengheld as a guest of the Keep, owing 3 pawns of vis
    this year, with 5 pawns of Vim (in memory, saved only with the
    form)."""
    guest = next(c for c in ws.saga.characters if c.id == "mag_sketch")
    guest.raw_vis = {"vim": 5}
    guest.stay = GuestStay(
        ws.selected_covenant.id, ws.saga.current_year, "Spring", fee_kind="vis", fee=3
    )
    return ws.selected_covenant


async def _open_pay_fee(ws) -> None:
    covenant = _with_guest(ws)
    await ws._current_sheet_view().build_all_tabs()
    ws._run_steps(guest_stays.pay_form(ws.saga, covenant, 0))


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


def _on_conflict_row(list_id: str, step):
    """A step of a More command on Conflicts' first battle, siege or fight
    (chosen first), run on its own: Muster's and Siege Actions' steps are
    each a form."""

    async def opener(ws) -> None:
        view = ws._current_sheet_view()
        await view.build_all_tabs()
        rows = view.query_one(f"#{list_id}", scr.SelectableList)
        rows.select_data_index(0)
        await until(lambda: rows.selected_data_index == 0)
        ws._run_steps(step(ws.saga))

    return opener


async def _open_cover(ws) -> None:
    """Add a Cover for Leandro (the section shows only for a Tytalus or
    one with a cover, so the form is run on its own)."""
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    ws._run_steps(cover_forms.ops(ws.selected_character).add())


def _with_harbour(ws) -> None:
    """A Place to stop at, The Sound (in memory, saved only with the form)."""
    if ws.saga.neighbour("the_sound") is None:
        ws.saga.neighbours.append(
            Neighbour("the_sound", "The Sound", kind="place", details={"aura": 2})
        )


def _open_add_stop(ws) -> None:
    """More's Add a Stop, on any covenant."""
    _with_harbour(ws)
    ws.action_add_stop()


def _open_plan_route(ws) -> None:
    """More's Plan Route on Whereabouts."""
    _with_harbour(ws)
    ws.action_plan_route()


async def _open_ship_fate(ws) -> None:
    """More's Sunk or Taken on the covenant's first ship, Seehund."""
    await _open_ship(ws, "fate")


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


def _settle_contested(ws) -> None:
    """Settle a contested source of income."""
    covenant = ws.selected_covenant
    source = IncomeSource("rents", "Rents", contested=True)
    covenant.economics.income_sources.append(source)
    ws._run_steps(cov_forms.settle_form(ws.saga, covenant, source))


def _covenfolk_line(ws):
    """A turb line of 3, as the covenfolk forms act on."""
    covenant = ws.selected_covenant
    covenant.inhabitants.append(
        Inhabitant(id="watch", kind="turb", name="The watch", quantity=3)
    )
    return next(
        e
        for e in covenfolk.entries_for_kind(ws.saga, covenant, "turb")
        if e.record is not None and e.record.id == "watch"
    )


def _recruit(ws) -> None:
    line = _covenfolk_line(ws)
    ws._run_steps(inhabitant_forms.recruit_form(ws.saga, ws.selected_covenant, line))


def _depart(ws) -> None:
    line = _covenfolk_line(ws)
    ws._run_steps(inhabitant_forms.depart_form(ws.saga, ws.selected_covenant, line))


def _add_purchase(ws) -> None:
    ws._run_steps(cov_forms.purchase_ops(ws.saga, ws.selected_covenant).add())


def _economics_row(which: str, key: str):
    """Edit the Yearly Expenditure / Cost Savings row with `key`."""

    def opener(ws) -> None:
        summary = eco.summarize(ws.saga, ws.selected_covenant)
        rows = summary.expenditure if which == "expenditure" else summary.savings
        ws._economics_row_form(which, next(r for r in rows if r.key == key))

    return opener


def _open_ritual_again(ws) -> None:
    """Perform the ritual again, Leandro holding Creo 5: from its Lab Text
    he may use at most his Creo score in Creo vis (DE p. 261)."""
    leandro = next(c for c in ws.saga.characters if c.name == "Leandro")
    leandro.arts["creo"] = ArtScore(xp=15)
    ws.action_perform_ritual()


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


# -- the guides' gaps, round two --


def _run(build):
    """An opener that runs `build(ws)`'s first step."""
    return lambda ws: ws._run_steps(build(ws))


async def _open_staged(ws, kind: str, open_form) -> None:
    """A form of the covenant's Projects tab with a staged project of
    `kind` shown, Vulcan's Hearth, its chapter's stages (added in memory,
    saved only with the form)."""
    covenant = ws.selected_covenant
    if not any(p.id == "hearth" for p in covenant.hermetic_projects):
        covenant.hermetic_projects.insert(
            0,
            HermeticProject(
                id="hearth",
                name="Vulcan's Hearth",
                kind=kind,
                stages=staged_projects.seed(kind),
            ),
        )
        covenant.project_shown = "hearth"
        await ws._show_covenant_detail(covenant)
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    open_form()


def _staged(kind: str, form):
    """An opener running `form(ws)` with a staged project of `kind` shown."""
    return lambda ws: _open_staged(ws, kind, lambda: form(ws))


async def _open_menagerie_award(ws) -> None:
    """More's Reputation Award on the Spur Menagerie, Alys its owner."""

    def form() -> None:
        project = ws.selected_covenant.hermetic_projects[0]
        project.owner_id, project.reputation = "comp1", "Keeper of Beasts"
        ws._run_steps(menagerie.award_form(ws.saga, ws.selected_covenant))

    await _open_menagerie(ws, form)


def _with_war(ws):
    """A Wizard's War on the Rhine's docket: Leandro on Brother Oda."""
    tribunal = ws.saga.tribunals[0]
    if not any(c.id == "war-contract" for c in tribunal.cases):
        tribunal.cases.insert(
            0,
            Case(
                "Leandro on Brother Oda",
                kind=hermetic_law.WAR,
                brought_by="Leandro",
                against="Brother Oda",
                filed_year=ws.saga.current_year,
                filed_season="Spring",
                month=1,
                id="war-contract",
            ),
        )
    return wizards_war.end_form(ws.saga, tribunal, 0)


def _faerie_hill(ws):
    """Cross the Threshold at the Drachenfels, made a Faerie place of aura
    5 with Realms of Power: Faerie in play (in memory)."""
    place = ws.saga.neighbour("drachenfels")
    place.realm = "Faerie"
    place.details["levels"] = []
    if ws.saga.books_in_play is not None and "RoP:F" not in ws.saga.books_in_play:
        ws.saga.books_in_play.append("RoP:F")
    return threshold_forms.threshold_form(ws.saga, place)


def _with_cover(ws):
    """A Disguise Roll for Leandro, given a cover (in memory)."""
    character = ws.selected_character
    if not character.covers:
        character.covers.append(DeepCover("Reynard", role="a mercenary"))
    return cover_forms.disguise_form(ws.saga, character)


def _with_hook(ws):
    """Suggest a Story from Rabenstein's Hook."""
    return hook_story_forms.story_form(ws.saga, ws.selected_covenant)


def _leandro(ws):
    return ws.saga.character("mag1")


def _springing(ws, *, ward: bool = False, acted: bool = False) -> tombs.Springing:
    """Overcome It part way through, on the sample tomb, for Leandro alone."""
    place = ws.saga.neighbour("drachenfels")
    obstacle = (
        tombs.Obstacle("Turn the Interloper", 15, "its effect", penetration=0)
        if ward
        else tombs._trap_obstacle(tombs.traps(place)[0])
    )
    who = _leandro(ws)
    spring = tombs.Springing(ws.saga, place, obstacle, [who], random.Random(1))
    if acted:
        spring.acted.append(tombs.Acted(who, "Leandro fails.", False))
    return spring


def _tomb_step(step) -> Opener:
    """Open one of Overcome It's later steps directly."""
    return Opener("place", _built(lambda ws: ws._run_steps(step(ws))))


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
    "hire mercenaries": Opener(
        "conflicts",
        _on_conflict_row(
            "conflict-battles-list",
            lambda s: battle_muster.hire_mercenaries(s, s.battles[0]),
        ),
    ),
    "end of the day": Opener(
        "conflicts",
        _on_conflict_row(
            "conflict-battles-list", lambda s: battle_muster.end_of_day(s, s.battles[0])
        ),
    ),
    "combat options": Opener(
        "conflicts",
        _on_conflict_row(
            "fights-list", lambda s: combat_options_form.options_form(s, s.fights[0])
        ),
    ),
    "change deployments": Opener(
        "conflicts",
        _on_conflict_row(
            "sieges-list", lambda s: siege_actions.deployments(s, s.sieges[0])
        ),
    ),
    "supplies story": Opener(
        "conflicts",
        _on_conflict_row(
            "sieges-list", lambda s: siege_actions.supplies_story(s, s.sieges[0])
        ),
    ),
    "castle taken": Opener(
        "conflicts",
        _on_conflict_row(
            "sieges-list", lambda s: siege_actions.castle_taken(s, s.sieges[0])
        ),
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
    "tie trigger": Opener("place", _with_crown_on_a_track),
    "grow story": Opener("region", _grow_a_story),
    "delay threat": Opener("threat", lambda ws: ws.action_delay_threat()),
    "take up story": Opener("region", _take_up_a_story),
    "take up threat": Opener("threat", lambda ws: ws.action_take_up_tale()),
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
    "edit ostracism": Opener(
        "alps_tribunal",
        _pick(
            lambda ws: ws._core_verb("section-trib-ostracism", "edit"),
            "trib-ostracism-list",
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
    "add cover": Opener("character", _open_cover),
    "resolve twilight": Opener("character", lambda ws: ws.action_resolve_twilight()),
    "cast a power": Opener("character", lambda ws: ws.action_hedge_cast()),
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
    "add story event concerning a character": Opener(
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
    "add covenant era": Opener(
        "covenant", _built(lambda ws: ws._core_verb("section-cov-eras", "add"))
    ),
    "edit history view": Opener(
        "covenant",
        _built(lambda ws: ws._core_verb("section-cov-history-view", "edit")),
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
    "settle a contested resource": Opener("covenant", _settle_contested),
    "add a purchase": Opener("covenant", _add_purchase),
    "recruit to a covenfolk line": Opener("covenant", _recruit),
    "depart from a covenfolk line": Opener("covenant", _depart),
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
    "perform ritual again": Opener("laboratory", _open_ritual_again),
    "lab texts read": Opener("character", lambda ws: ws._edit_lab_text_access()),
    "add house rule": Opener("saga", lambda ws: ws._house_rule_form(None)),
    "add player": Opener("saga_content", lambda ws: ws._player_form(None)),
    "edit traditions offered": Opener("saga_content", lambda ws: ws._edit_traditions()),
    "add spell": Opener("saga_content", lambda ws: ws._spell_form(None)),
    "edit spell": Opener("saga_content", lambda ws: ws._spell_form(ws.saga.spells[0])),
    "add saga source": Opener("saga_content", lambda ws: ws._saga_source_form(None)),
    "edit saga source": Opener("saga_content", _open_saga_source),
    "move to source": Opener("saga_content", _move_to_source),
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
    "censure clause": Opener("covenant", _open_censure_clause),
    "charge clause": Opener("covenant", _open_charge_clause),
    "use charter template": Opener("covenant", _open_use_template),
    "save charter template": Opener("covenant", _open_save_template),
    "pay the fee": Opener("covenant", _open_pay_fee),
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
    "conjure a spirit": Opener("character", lambda ws: _open_galdor(ws, "conjure")),
    "bargain with a lord": Opener("character", lambda ws: _open_galdor(ws, "bargain")),
    "bind an item": Opener("character", lambda ws: _open_galdor(ws, "bind")),
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
    "threaten a saint": Opener("character", lambda ws: _refused_then_threaten(ws)),
    "patron saint": Opener("character", lambda ws: ws.action_patron_saint()),
    "invoke baraka": Opener("character", lambda ws: ws.action_invoke_baraka()),
    "the hajj": Opener("character", lambda ws: ws.action_hajj()),
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
    "interests": Opener("character", lambda ws: ws.action_edit_interests()),
    "covenant interests": Opener("covenant", lambda ws: ws.action_edit_interests()),
    "commanding aura": Opener("character", lambda ws: _open_mystic(ws, "aura")),
    # House Verditius's Hubris and vendettas.
    "hubris": Opener("character", lambda ws: _open_hubris(ws)),
    # Hermetic spirit magic and theurgy (The Mysteries Revised Edition).
    "spirits and names": Opener("character", lambda ws: _open_spirits(ws)),
    # Dream magic and Hermetic sacrifice (The Mysteries Revised Edition).
    "dream working": Opener("character", lambda ws: _open_dreams(ws, "dream")),
    "hermetic sacrifice": Opener("character", lambda ws: _open_dreams(ws, "sacrifice")),
    # House Acclaim and Reputation rolls (HoH:TL, HoH:S, LoH, DE).
    "house acclaim": Opener("character", lambda ws: _open_acclaim(ws)),
    "reputation roll": Opener("character", lambda ws: _open_reputation_roll(ws)),
    # Divination and Hermetic astrology (The Mysteries Revised Edition).
    "divination": Opener("character", lambda ws: _open_tmre_divination(ws, "divine")),
    "astrology": Opener("character", lambda ws: _open_tmre_divination(ws, "stars")),
    # Philosophic Alchemy's digestions (The Mysteries Revised Edition).
    "philosophic alchemy": Opener("character", lambda ws: _open_alchemy(ws)),
    # The Great Elixir's test (The Mysteries Revised Edition).
    "test the great elixir": Opener("character", lambda ws: _open_great_elixir(ws)),
    # Gaining and losing Virtues and Flaws in play (Grogs pp. 61-64).
    "gain or lose in play": Opener(
        "character", lambda ws: ws.action_change_virtues_flaws()
    ),
    # A saga's own Abilities in House Rules (HoH:S pp. 103-106).
    "add house rule ability": Opener(
        "saga_content", lambda ws: ws._house_rule_form(None)
    ),
    "edit house rule ability": Opener("saga_content", lambda ws: _open_own_ability(ws)),
    # A place's Tomb tab (Lands of the Nile).
    "edit tomb": Opener(
        "place", _built(lambda ws: ws._core_verb("section-nb-tomb", "edit"))
    ),
    "add tomb curse": Opener(
        "place", _built(lambda ws: ws._core_verb("section-nb-tomb-curses", "add"))
    ),
    "edit tomb ward": Opener(
        "place",
        _pick(
            lambda ws: ws._core_verb("section-nb-tomb-wards", "edit"),
            "nb-tomb-wards-list",
        ),
    ),
    "add tomb trap": Opener(
        "place", _built(lambda ws: ws._core_verb("section-nb-tomb-traps", "add"))
    ),
    "overcome trap": Opener(
        "place", _pick(lambda ws: ws.action_overcome_trap(), "nb-tomb-traps-list")
    ),
    "overcome ward": Opener(
        "place", _pick(lambda ws: ws.action_overcome_ward(), "nb-tomb-wards-list")
    ),
    "trap spotted": _tomb_step(
        lambda ws: tombs.seen_form(_springing(ws), [_leandro(ws)])
    ),
    "character acts": _tomb_step(lambda ws: tombs.action_form(_springing(ws))),
    "character faces ward": _tomb_step(
        lambda ws: tombs.action_form(_springing(ws, ward=True))
    ),
    "trap acts": _tomb_step(lambda ws: tombs.it_acts(_springing(ws, acted=True))),
    # A covenant's ships (Hermetic Projects; City & Guild).
    "add ship": Opener("covenant", lambda ws: ws._possession_form("ship", None)),
    "ship stress check": Opener("covenant", lambda ws: _open_ship(ws, "stress")),
    "ship combat": Opener("covenant", lambda ws: _open_ship(ws, "combat")),
    "sunk or taken": Opener("covenant", _open_ship_fate),
    "detach ship": Opener("covenant", lambda ws: _open_ship(ws, "detach")),
    "add a stop": Opener("covenant", _open_add_stop),
    "plan route": Opener("covenant", _open_plan_route),
    # Shaping the land by magic (Transforming Mythic Europe).
    "shape land": Opener("covenant", lambda ws: ws.action_shape_land()),
    "settle new land": Opener("covenant", lambda ws: _open_settle_land(ws)),
    # The Rhine's Great Library at Durenmar (Guardians of the Forests).
    "search the great library": Opener(
        "tribunal", lambda ws: _open_library(ws, lambda ws: ws.action_library_search())
    ),
    "contribute to the great library": Opener(
        "tribunal",
        lambda ws: _open_library(
            ws, lambda ws: ws._core_verb("section-trib-library-credit", "add")
        ),
    ),
    "edit library credit": Opener(
        "tribunal",
        lambda ws: _open_library(
            ws,
            lambda ws: ws._core_verb("section-trib-library-credit", "edit"),
            "trib-library-credit-list",
        ),
    ),
    "edit library search": Opener(
        "tribunal",
        lambda ws: _open_library(
            ws,
            lambda ws: ws._core_verb("section-trib-library-searches", "edit"),
            "trib-library-searches-list",
        ),
    ),
    # A cleric's career (The Church): the Church tab's forms.
    "petition the church": Opener("character", lambda ws: _open_church(ws, "petition")),
    "add canon case": Opener("character", lambda ws: _open_church(ws, "canon")),
    "edit holy orders": Opener("character", lambda ws: _open_church(ws, "orders")),
    "edit religion": Opener("character", lambda ws: _open_church(ws, "religion")),
    "perform an exorcism": Opener("character", lambda ws: _open_church(ws, "exorcism")),
    "add ordination": Opener("character", lambda ws: _open_church(ws, "ordination")),
    # Saga Content's Mystery Cults.
    "add mystery cult": Opener(
        "saga_content", lambda ws: _open_cults(ws, None, "section-content-cults", "add")
    ),
    "edit mystery cult": Opener(
        "saga_content",
        lambda ws: _open_cults(ws, None, "section-content-cult", "edit"),
    ),
    "add cult degree": Opener(
        "saga_content",
        lambda ws: _open_cults(ws, None, "section-content-cult-degrees", "add"),
    ),
    "edit cult script": Opener(
        "saga_content",
        lambda ws: _open_cults(
            ws, "content-cult-scripts-list", "section-content-cult-scripts", "edit"
        ),
    ),
    "add cult component": Opener(
        "saga_content",
        lambda ws: _open_cults(ws, None, "section-content-cult-scripts", "add"),
    ),
    # A covenant's Hermetic Projects (Hermetic Projects pp. 36-41) and
    # Wizard's War's tunnel (pp. 78-81).
    "begin project": Opener("covenant", lambda ws: ws.action_begin_project()),
    "edit project": Opener(
        "covenant",
        lambda ws: _open_tower(ws, lambda: ws._core_verb(TOWER_SECTION, "edit")),
    ),
    "add work": Opener(
        "covenant",
        lambda ws: _open_tower(ws, lambda: ws._core_verb(PROJECT_WORKS_SECTION, "add")),
    ),
    "add device": Opener(
        "covenant",
        lambda ws: _open_tower(
            ws, lambda: ws._core_verb(PROJECT_DEVICES_SECTION, "add")
        ),
    ),
    "tower stress check": Opener(
        "covenant", lambda ws: _open_tower(ws, ws.action_tower_stress)
    ),
    "conjure levels": Opener(
        "covenant", lambda ws: _open_tower(ws, ws.action_tower_conjure)
    ),
    "open a tunnel": Opener("character", lambda ws: _open_tunnel(ws)),
    # A Virtue gained by magic for a while ends (Grogs pp. 62-63).
    "end a temporary virtue": Opener("character", lambda ws: _open_temporary(ws)),
    # Fleet battles (Tales of Power): a Battle at sea with the covenant's ships.
    "edit fleet battle": Opener(
        "conflicts",
        lambda ws: _open_fleet(
            ws, lambda ws: ws._core_verb("section-conflict-battles", "edit")
        ),
    ),
    "fleet battle event": Opener(
        "conflicts",
        lambda ws: _open_fleet(ws, lambda ws: ws.action_conflict_battle_event()),
    ),
    # A covenant's Menagerie (Hermetic Projects pp. 119-142).
    "add beast": Opener(
        "covenant",
        lambda ws: _open_menagerie(ws, lambda: ws._core_verb(BEASTS_SECTION, "add")),
    ),
    "breed a pair": Opener(
        "covenant",
        lambda ws: _open_menagerie(ws, lambda: ws._core_verb(BREEDINGS_SECTION, "add")),
    ),
    "edit breeding": Opener(
        "covenant",
        lambda ws: _open_menagerie(
            ws, lambda: ws._core_verb(BREEDINGS_SECTION, "edit"), "breedings"
        ),
    ),
    "tame a beast": Opener(
        "covenant",
        lambda ws: _open_menagerie(ws, ws.action_tame_beast, "beasts", 2),
    ),
    # A lord's marriages (Lords of Men pp. 10-11).
    "arrange marriage": Opener(
        "neighbour", _built(lambda ws: ws._core_verb("section-nb-marriages", "add"))
    ),
    "edit marriage": Opener(
        "neighbour",
        lambda ws: _on_marriage(
            ws, lambda ws: ws._core_verb("section-nb-marriages", "edit")
        ),
    ),
    "edit marriage terms": Opener(
        "neighbour",
        lambda ws: _on_marriage(
            ws, lambda ws: ws._core_verb("section-nb-marriage", "edit")
        ),
    ),
    "end marriage": Opener(
        "neighbour", lambda ws: _on_marriage(ws, lambda ws: ws.action_end_marriage())
    ),
    # A Criamon magus's The Enigma tab (HoH:MC pp. 50-73).
    "change path": Opener(
        "character",
        lambda ws: _open_criamon(ws, lambda: ws._core_verb(CRIAMON_PATH, "edit")),
    ),
    "follow an avenue": Opener(
        "character", lambda ws: _open_criamon(ws, ws.action_follow_avenue)
    ),
    "add stigma": Opener(
        "character",
        lambda ws: _open_criamon(ws, lambda: ws._core_verb(STIGMATA, "add")),
    ),
    "edit stigma": Opener(
        "character",
        lambda ws: _open_criamon(ws, lambda: ws._core_verb(STIGMATA, "edit"), True),
    ),
    # Polemic and Charter Strength (Transforming Mythic Europe pp. 27-36).
    "add argument": Opener(
        "tribunal", _built(lambda ws: ws._core_verb("section-trib-arguments", "add"))
    ),
    "edit argument": Opener(
        "tribunal",
        lambda ws: _on_argument(
            ws, lambda ws: ws._core_verb("section-trib-argument", "edit")
        ),
    ),
    "add text": Opener(
        "tribunal",
        lambda ws: _on_argument(
            ws, lambda ws: ws._core_verb("section-trib-argument-texts", "add")
        ),
    ),
    "circulate text": Opener(
        "tribunal",
        lambda ws: _on_argument(ws, lambda ws: ws.action_circulate_text(), text=True),
    ),
    "draft charter": Opener(
        "town", lambda ws: _on_charter_lord(ws, lambda ws: ws.action_draft_charter())
    ),
    "seek loophole": Opener(
        "town", lambda ws: _on_charter_lord(ws, lambda ws: ws.action_seek_loophole())
    ),
    # The guides' gaps, round two.
    "grog story experience": Opener(
        "character",
        _run(lambda ws: grog_story.story_form(ws.saga, ws.saga.character("grog9"))),
    ),
    "melee event": Opener(
        "character",
        _run(lambda ws: melee_events.melee_form(ws.saga, ws.selected_character)),
    ),
    "certamen": Opener(
        "character",
        _run(lambda ws: certamen_forms.duel_form(ws.saga, ws.selected_character)),
    ),
    "where he is": Opener(
        "character",
        _run(lambda ws: whereabouts.where_form(ws.saga, ws.selected_character)),
    ),
    "stay as guest": Opener(
        "character",
        _run(lambda ws: guest_stays.stay_form(ws.saga, ws.selected_character)),
    ),
    "trait roll": Opener(
        "character",
        _run(lambda ws: trait_roll_forms.roll_form(ws.saga, ws.selected_character)),
    ),
    "build a ship": Opener(
        "covenant",
        _run(lambda ws: ship_build.build_form(ws.saga, ws.selected_covenant)),
    ),
    "suggest a story": Opener("covenant", _run(_with_hook)),
    "disguise roll": Opener("character", _run(_with_cover)),
    "menagerie reputation award": Opener("covenant", _open_menagerie_award),
    # A staged Hermetic Project (Hermetic Projects pp. 9-118).
    "add project stage": Opener(
        "covenant",
        _staged("Burning City", lambda ws: ws._core_verb(STAGED_STAGES_SECTION, "add")),
    ),
    "add stage work": Opener(
        "covenant",
        _staged("Burning City", lambda ws: ws._core_verb(STAGE_WORKS_SECTION, "add")),
    ),
    "warning bell": Opener(
        "covenant", _staged("Burning City", lambda ws: ws.action_warning_bell())
    ),
    "gather a connection": Opener(
        "covenant",
        _staged("Intangible Assassin", lambda ws: ws.action_gather_connection()),
    ),
    "lower an aegis": Opener(
        "covenant",
        _staged("Intangible Assassin", lambda ws: ws.action_lower_aegis()),
    ),
    "death roll": Opener(
        "covenant", _staged("Living Corpse", lambda ws: ws.action_death_roll())
    ),
    "war's end": Opener("tribunal", _run(_with_war)),
    "cross the threshold": Opener("place", _run(_faerie_hill)),
}


async def _on_marriage(ws, action) -> None:
    """A command on Gottfried's Marriages tab, on his marriage to Adelheid
    of Sayn, added in memory (saved only with the form)."""
    if not ws.saga.marriages:
        ws.saga.marriages.append(
            Marriage(
                groom_ref="neighbour:gottfried",
                bride="Adelheid of Sayn",
                state="married",
                lands=4,
            )
        )
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    view.refresh_section("section-nb-marriages")
    listed = view.query_one("#nb-marriages-list", scr.SelectableList)
    listed.select_data_index(0)
    await until(lambda: listed.selected_data_index == 0)
    action(ws)


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


def _open_galdor(ws, which: str) -> None:
    """Conjure a Spirit, Bargain with a Lord or Bind an Item on Leandro,
    made a galdraman with Ol-galdor 5, Galdor Wisdom 5, Craft: Runes 5 and
    a deal."""
    character = ws.selected_character
    if "trad_galdramen" not in character.traditions:
        character.traditions.append("trad_galdramen")
        character.virtues_flaws += [
            VirtueFlawInstance("vf_galdor_conjuring"),
            VirtueFlawInstance("vf_galdor_enchantment"),
        ]
        character.abilities += [
            Ability("Ol-galdor", xp=15, xp_table="art"),
            Ability("Galdor Wisdom", xp=75),
            Ability("Craft: Runes", xp=75),
        ]
        character.bound_beings.append(
            BoundBeing("The Ol lord", "trad_galdramen", "Deal with a lord")
        )
    {
        "conjure": ws.action_galdor_conjure,
        "bargain": ws.action_galdor_bargain,
        "bind": ws.action_galdor_bind,
    }[which]()


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


def _open_spirits(ws) -> None:
    """More's Spirits and Names on the magus on show, given Hermetic
    Theurgy."""
    character = ws.selected_character
    if VirtueFlawInstance("vf_hermetic_theurgy") not in character.virtues_flaws:
        character.virtues_flaws.append(VirtueFlawInstance("vf_hermetic_theurgy"))
    ws.action_spirits_and_names()


def _open_dreams(ws, which: str) -> None:
    """More's Dream Working (given Dream Magic) or Hermetic Sacrifice (given
    the Virtue and a known level 30 Ritual) on the magus on show."""
    character = ws.selected_character
    vf_id = "vf_dream_magic" if which == "dream" else "vf_hermetic_sacrifice"
    if VirtueFlawInstance(vf_id) not in character.virtues_flaws:
        character.virtues_flaws.append(VirtueFlawInstance(vf_id))
    if which == "dream":
        ws.action_dream_working()
        return
    if not any(s.id == "sp_summon_mercury" for s in ws.saga.spells):
        ws.saga.spells.append(
            Spell("sp_summon_mercury", "Call Mercury", "Rego", "Vim", 30, ritual=True)
        )
        character.spells_known.insert(0, KnownSpell("sp_summon_mercury"))
    ws.action_hermetic_sacrifice()


def _open_acclaim(ws) -> None:
    """More's House Acclaim on the magus on show, made a Bonisagus without
    House Acclaim yet."""
    character = ws.selected_character
    character.hermetic.house = "house_bonisagus"
    character.reputations = [
        r for r in character.reputations if not r.name.startswith("House Acclaim")
    ]
    ws.action_house_acclaim()


def _open_reputation_roll(ws) -> None:
    """More's Reputation Roll on the character on show, given a Reputation."""
    character = ws.selected_character
    if not character.reputations:
        character.reputations.append(ScoredTrait("Dragon-slayer", 3, type="Local"))
    ws.action_reputation_roll()


def _open_tmre_divination(ws, which: str) -> None:
    """More's Divination (given Divination & Augury by Pyromancy and
    Divination 3) or Astrology (given Planetary Magic) on the person on
    show."""
    character = ws.selected_character
    if which == "divine":
        augury = VirtueFlawInstance("vf_divination_and_augury", {"method": "Pyromancy"})
        if augury not in character.virtues_flaws:
            character.virtues_flaws.append(augury)
        if not any(a.name == "Divination" for a in character.abilities):
            character.abilities.append(Ability("Divination", "Supernatural", xp=15))
        ws.action_tmre_divination()
        return
    if VirtueFlawInstance("vf_planetary_magic") not in character.virtues_flaws:
        character.virtues_flaws.append(VirtueFlawInstance("vf_planetary_magic"))
    ws.action_tmre_astrology()


def _open_alchemy(ws) -> None:
    """More's Philosophic Alchemy on This Season, given Hermetic Alchemy,
    the Major Virtue and a laboratory."""
    character = ws.selected_character
    for vf_id in ("vf_hermetic_alchemy", "vf_philosophic_alchemy_major"):
        if VirtueFlawInstance(vf_id) not in character.virtues_flaws:
            character.virtues_flaws.append(VirtueFlawInstance(vf_id))
    character.assigned_lab_id = character.assigned_lab_id or "lab1"
    ws.action_philosophic_alchemy()


def _open_great_elixir(ws) -> None:
    """More's Test the Great Elixir on Aging & Warping, given Unaging, the
    Lesser and Great Elixirs and an age of 60."""
    character = ws.selected_character
    for vf_id in ("vf_unaging", "vf_the_lesser_elixir", "vf_the_great_elixir"):
        if VirtueFlawInstance(vf_id) not in character.virtues_flaws:
            character.virtues_flaws.append(VirtueFlawInstance(vf_id))
    character.background.year_born = ws.saga.current_year - 60
    ws.action_great_elixir()


def _open_own_ability(ws) -> None:
    """Edit one of the saga's own Abilities in House Rules: Speak with Ravens,
    held by no one."""
    if not ws.saga.custom_abilities:
        ws.saga.custom_abilities.append(
            AbilityDef(
                id="custom_ability_speak_with_ravens",
                name="Speak with Ravens",
                category="Supernatural",
                source="",
                realm="Magic",
                characteristic="Communication",
            )
        )
        catalog.use_saga(ws.saga)
    ability = ws.saga.custom_abilities[0]
    ws._house_rule_form((hr.ABILITY, ability))


async def _open_ship(ws, which: str) -> None:
    """More's Stress Check or Ship Combat on the covenant's first ship,
    Seehund (added in memory, saved only with the form)."""
    covenant = ws.selected_covenant
    if not any(p.kind == "ship" for p in covenant.possessions):
        covenant.possessions.insert(
            0,
            Possession(
                id="seehund",
                kind="ship",
                name="Seehund",
                ship=Ship(ship_type="buss", kind_name="Coastal buss"),
            ),
        )
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    rows = view.query_one("#pos-ship-list", scr.SelectableList)
    rows.select_data_index(0)
    await until(lambda: rows.selected_data_index == 0)
    if which == "stress":
        ws.action_ship_stress()
    elif which == "detach":
        _with_harbour(ws)
        ws.action_detach_ship()
    elif which == "fate":
        ws.action_ship_fate()
    else:
        ws.action_ship_combat()


def _open_settle_land(ws) -> None:
    """Settle the New Land on a finished 3-mile island (its four Rituals
    cast by Leandro; added in memory, saved only with the form)."""
    covenant = ws.selected_covenant
    if not covenant.land_projects:
        covenant.land_projects.append(LandProject("isle", "Insula"))
        magus = ws.saga.character("mag1")
        magus.progress.append(Progress("land_shaping", "Insula", 4, 4))
    ws._run_steps(land_forms.settle_form(ws.saga, covenant, covenant.land_projects[0]))


async def _open_library(ws, open_editor, list_id: str = "") -> None:
    """A form of the Rhine's Great Library tab: Leandro holds two seasons of
    credit there and has sought a Vim tractatus (in memory, saved only with
    the form); the row of `list_id` is chosen first."""
    tribunal = ws.saga.tribunal("rhine")
    data = tribunal.package_data.setdefault("rhine", {})
    if not data.get("library_credit"):
        data["library_credit"] = [
            {
                "magus_id": "mag1",
                "given": [{"kind": "book", "what": "Tractatus, Vim Q 8", "seasons": 2}],
                "granted": 0,
                "used": 0,
                "note": "",
            }
        ]
        data["library_searches"] = [
            {
                "magus_id": "mag1",
                "year": 1220,
                "season": "Spring",
                "sought": "tractatus",
                "subject": "Vim",
                "level": None,
                "ease": None,
                "lore_used": False,
                "roll": "Q 5 + 2",
                "outcome": "found",
                "quality": 7,
                "mastery": [],
                "lines": [],
                "book_id": None,
                "credit_taken": False,
            }
        ]
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    if list_id:
        rows = view.query_one(f"#{list_id}", scr.SelectableList)
        rows.select_data_index(0)
        await until(lambda: rows.selected_data_index == 0)
    open_editor(ws)


async def _open_church(ws, which: str) -> None:
    """A form of Leandro's Church tab: he is made an exorcist of Konstanz
    (in memory, saved only with the form) and shown again, so the sheet
    has the tab, built."""
    character = ws.selected_character
    if not character.church.grade:
        character.church.grade = "Exorcist"
        character.church.diocese = "Konstanz"
        await ws._show_character_detail(character)
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    if which == "exorcism":
        ws.action_perform_exorcism()
        return
    section, verb = {
        "petition": ("section-char-petitions", "add"),
        "canon": ("section-char-canon", "add"),
        "orders": ("section-char-orders", "edit"),
        "ordination": ("section-char-ordinations", "add"),
        "religion": ("section-char-faith", "edit"),
    }[which]
    ws._core_verb(section, verb)


def _with_cult(ws) -> None:
    """The Spinner's Thread, the saga's own cult (once, however often the
    form is opened): its first degree's Script is +10; the first character
    has its Lore 5 and the Virtue."""
    saga = ws.saga
    if any(c.id == "custom_cult_spinners_thread" for c in saga.custom_cults):
        return
    lore = "Spinner's Thread Lore"
    script = CultScript(
        "The Silk Hall",
        [
            cult_core.component("place", note="To the Silk Hall"),
            cult_core.component("quest"),
            cult_core.component("ordeal_minor", flaw_id="vf_visions"),
            cult_core.component("goods"),
        ],
    )
    saga.custom_cults.append(
        MysteryCult(
            "custom_cult_spinners_thread",
            "The Spinner's Thread",
            lore,
            realm="Faerie",
            degrees=[
                CultDegree("degree_1", "Spinner", "vf_second_sight", script=script)
            ],
        )
    )
    mystagogue = saga.characters[0]
    mystagogue.abilities.append(Ability(lore, xp=cult_ability_xp(5)))
    mystagogue.virtues_flaws.append(VirtueFlawInstance("vf_second_sight"))
    catalog.use_saga(saga)


async def _open_cults(ws, list_id: str | None, section: str, verb: str) -> None:
    """A verb on Saga Content's Mystery Cults tab (an empty saga for Add
    Mystery Cult), on the first row of `list_id` when given."""
    view = ws._current_sheet_view()
    if section != "section-content-cults":
        _with_cult(ws)
    await view.build_all_tabs()
    for each in (
        "section-content-cults",
        "section-content-cult",
        "section-content-cult-degrees",
        "section-content-cult-scripts",
    ):
        view.refresh_section(each)
    if list_id:
        rows = view.query_one(f"#{list_id}", scr.SelectableList)
        rows.focus()
        rows.select_data_index(0)
        await until(lambda: rows.selected_data_index == 0)
    ws._core_verb(section, verb)


async def _open_tower(ws, open_form) -> None:
    """A form of the covenant's Projects tab: the Schattenbach Spire, its
    two rituals (one shoddy) and a craft device, added in memory (saved
    only with the form); the sheet is shown again with its Projects tab."""
    covenant = ws.selected_covenant
    if not covenant.hermetic_projects:
        covenant.hermetic_projects.append(
            HermeticProject(
                id="spire",
                name="The Schattenbach Spire",
                mason_id="comp1",
                works=[
                    ProjectWork(
                        id="w1",
                        name="Conjuring the Great Tower",
                        levels=2,
                        quality="Standard",
                    ),
                    ProjectWork(
                        id="w2",
                        name="Heights of the Great Tower",
                        levels=4,
                        quality="Shoddy",
                    ),
                ],
                devices=[CraftDevice(id="d1", name="The Arms of Hercules")],
            )
        )
        await ws._show_covenant_detail(covenant)
        await ws._current_sheet_view().build_all_tabs()
    open_form()


def _open_tunnel(ws) -> None:
    """Open a Tunnel for Leandro, who knows The Cursed Day (added in
    memory, saved only with the form)."""
    magus = ws.selected_character
    if not any(k.spell_id == "spell_the_curs_d_day" for k in magus.spells_known):
        magus.spells_known.append(KnownSpell("spell_the_curs_d_day"))
    ws.action_open_tunnel()


def _open_temporary(ws) -> None:
    """Gain or Lose in Play for Leandro, whose Virtue is marked temporary
    (in memory, saved only with the form)."""
    ws.selected_character.virtues_flaws[0].temporary = True
    ws.action_change_virtues_flaws()


async def _open_fleet(ws, open_editor) -> None:
    """A form on a battle at sea, chosen first: the covenant's Seehund and
    Möwe against two pirate ships (added in memory, saved only with the
    form)."""
    covenant = ws.saga.covenants[0]
    if not any(p.id == "seehund" for p in covenant.possessions):
        covenant.possessions += [
            Possession(
                id=pid,
                kind="ship",
                name=name,
                ship=Ship(ship_type="buss", kind_name="Coastal buss"),
            )
            for pid, name in (("seehund", "Seehund"), ("moewe", "Möwe"))
        ]
        ws.saga.battles.insert(
            0,
            Battle(
                "Off Terschelling",
                at_sea=True,
                sides=[
                    BattleSide(
                        covenant_id=covenant.id, groups=3, ships=["seehund", "moewe"]
                    ),
                    BattleSide("Pirates", groups=4, other_ships=2),
                ],
            ),
        )
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    view.refresh_section("section-conflict-battles")
    rows = view.query_one("#conflict-battles-list", scr.SelectableList)
    rows.select_data_index(0)
    await until(lambda: rows.selected_data_index == 0)
    open_editor(ws)


async def _open_menagerie(ws, open_form, rows: str = "", row: int = 0) -> None:
    """A form of the covenant's Projects tab with the Spur Menagerie shown:
    Bock and Geiß (tamed Goats of Virtue), four wild Hares of Virtue, and
    a breeding of the goats; Alys its lead handler (added in memory, saved
    only with the form). `rows` names the list whose `row` is chosen."""
    covenant = ws.selected_covenant
    if not any(p.id == "spur" for p in covenant.hermetic_projects):
        covenant.hermetic_projects.insert(
            0,
            HermeticProject(
                id="spur",
                name="The Spur Menagerie",
                kind="Menagerie",
                handler_ids=["comp1"],
                beasts=[
                    Beast(id="bock", name="Bock", might=10, sex="male", tamed=True),
                    Beast(id="geiss", name="Geiß", might=10, tamed=True),
                    Beast(
                        id="hares",
                        name="Hare of Virtue",
                        might=5,
                        size=-3,
                        count=4,
                        sex="both",
                    ),
                ],
                breedings=[Breeding(id="b1", pair="Bock × Geiß", result="No young")],
            ),
        )
        covenant.project_shown = "spur"
        await ws._show_covenant_detail(covenant)
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    if rows:
        found = view.query_one(f"#cov-menagerie-{rows}-list", scr.SelectableList)
        found.select_data_index(row)
        await until(lambda: found.selected_data_index == row)
    open_form()


CRIAMON_PATH = "section-char-criamon-path"
STIGMATA = "section-char-stigmata"


async def _open_criamon(ws, open_form, choose: bool = False) -> None:
    """A form of Leandro's The Enigma tab: he is made a Criamon magus two
    stations along the Path of Seeming, with House Criamon Lore 4 and a
    stigma on his temples (in memory, saved only with the form), and shown
    again so the sheet has the tab; `choose` picks the stigma first."""
    character = ws.selected_character
    if character.hermetic.house != "house_criamon":
        character.hermetic.house = "house_criamon"
        for vf_id in (
            "vf_the_enigma",
            "vf_station_of_differentiation_of_seeming",
            "vf_station_of_true_sight",
        ):
            character.virtues_flaws.append(VirtueFlawInstance(vf_id))
        character.abilities.append(
            Ability("Mystery Cult Lore: Criamon", xp=cult_ability_xp(4))
        )
        character.enigma.stigmata.append(
            Stigma("Temples", "Rings of open eyes", "riddle", year=1196)
        )
        await ws._show_character_detail(character)
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    if choose:
        rows = view.query_one("#char-stigmata-list", scr.SelectableList)
        rows.select_data_index(0)
        await until(lambda: rows.selected_data_index == 0)
    open_form()


async def _on_argument(ws, open_form, text: bool = False) -> None:
    """A form of the Rhine's Arguments tab, on an argument for its first
    case with a summa on Code of Hermes in the library to write it in (in
    memory, saved only with the form); `text` gives it its polemic, not
    yet circulated, chosen first."""
    saga = ws.saga
    tribunal = saga.tribunal("rhine")
    if not any(b.id == "b-polemic" for b in saga.books):
        saga.books.append(
            Book(
                id="b-polemic",
                name="On Charters",
                type="Ability Summa",
                ability="Code of Hermes",
                level=4,
                quality=11,
                author_id="mag1",
            )
        )
    if not tribunal.arguments:
        argument = Argument(
            "Covenants may hold charters",
            ideal="Charters",
            proponent_id="mag1",
            case_id=tribunal.cases[0].id,
        )
        if text:
            argument.texts.append(PolemicText(book_id="b-polemic", author_id="mag1"))
        tribunal.arguments.append(argument)
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    view.refresh_section("section-trib-arguments")
    if text:
        rows = view.query_one("#trib-argument-texts", scr.SelectableList)
        rows.select_data_index(0)
        await until(lambda: rows.selected_data_index == 0)
    open_form(ws)


async def _on_charter_lord(ws, open_form) -> None:
    """A Charter Strength command on Soest's charter, its lord the
    Archbishop of Cologne with his strength drafted at 0, the saga using
    the optional rule (in memory, saved only with the form)."""
    saga = ws.saga
    saga.rule_options["charter_strength"] = True
    town = saga.neighbour("soest")
    if not town.details.get("charter_lords"):
        town.details["charter_lords"] = [
            {"lord": "The Archbishop of Cologne", "superior_strength": 0}
        ]
    view = ws._current_sheet_view()
    await view.build_all_tabs()
    view.refresh_section("section-nb-charter-lords")
    rows = view.query_one("#nb-charter-lords-list", scr.SelectableList)
    rows.select_data_index(0)
    await until(lambda: rows.selected_data_index == 0)
    open_form(ws)
