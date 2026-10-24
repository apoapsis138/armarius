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
from ars_magica_manager.forms import animal as animal_forms
from ars_magica_manager.forms import choice_templates as choice_forms
from ars_magica_manager.forms import creation as creation_forms
from ars_magica_manager.forms import lab_item
from ars_magica_manager.forms import worksheet as wf
from ars_magica_manager.models import (
    Ability,
    Book,
    Character,
    Neighbour,
    Saga,
    SagaSource,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import creation_xp
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
    Order of Business's second row is the Opening, its third the first
    case's debate."""

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
    "hold the debate": Opener("tribunal", _open_meeting_step(2, "meeting-business")),
    "hold the vote": Opener("tribunal", _open_meeting_step(0, "meeting-vote")),
    "hold the rulings": Opener("tribunal", _open_meeting_step(6, "meeting-business")),
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
    "childhood blanks": Opener(
        "character",
        lambda ws: ws._run_steps(
            wf.use_childhood(
                ws.selected_character,
                next(c for c in creation_xp.CHILDHOODS if c.name == "Traveling"),
            )
        ),
    ),
}


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
