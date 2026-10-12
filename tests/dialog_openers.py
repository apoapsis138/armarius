"""How to reach each form dialog the way the app does: which tree node to
select and which WorkspaceScreen handler (or picker hook) opens it. Shared
by the dialog contract tests; see test_dialog_contracts.py."""

import asyncio
import inspect
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from support import NODES, everything_saga, wait_until
from textual.screen import ModalScreen
from textual.widgets import TabbedContent, Tree

from ars_magica_manager import catalog, spells, storage, vis
from ars_magica_manager import economics as eco
from ars_magica_manager.models import (
    Ability,
    Book,
    Character,
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


def _open_saga_source(ws) -> None:
    """Edit a saga source, made in memory (saved only with the edit)."""
    if not ws.saga.sources:
        ws.saga.sources.append(SagaSource("HR", "House rules"))
    ws._saga_source_form(ws.saga.sources[0])


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


async def _open_lab_choice_prompt(ws) -> None:
    """Add a laboratory Flaw whose Specialization the owner chooses: the
    picker asks for it."""
    view = ws._current_sheet_view()
    view.query_one(TabbedContent).active = "tab-lab-vf"
    # The tab is built as it is first shown.
    await until(lambda: view.query("#section-lab-vf-flaws CollapsibleTitle"))
    section_stop(view.query_one("#section-lab-vf-flaws")).focus()
    await until(lambda: ws._active_section() == "section-lab-vf-flaws")
    ws.action_add_virtue_flaw()
    picker = await wait_for_screen(ws.app, scr.LabVirtueFlawPickerScreen)
    picker._on_entry_selected(
        catalog.load_lab_virtue_flaw_catalog_by_id()["labvf_disorganized"]
    )


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
    # Covenant
    "create character": Opener("covenant", lambda ws: ws.action_create_character()),
    "create laboratory": Opener("covenant", lambda ws: ws.action_create_laboratory()),
    "bind familiar": Opener("covenant", lambda ws: ws.action_create_familiar()),
    "edit covenant": Opener("covenant", lambda ws: ws._edit_covenant()),
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
    "move raw vis": Opener(
        "character",
        lambda ws: ws._move_vis_form(
            ws.selected_character, vis.held(ws.selected_character)[0]
        ),
    ),
    "add research goal": Opener("character", lambda ws: ws._add_research_goal()),
    "virtue parameters": Opener("character", _open_param_prompt),
    "virtue ability choice": Opener(
        "character", lambda ws: _open_param_prompt(ws, "vf_puissant_ability")
    ),
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
    "edit lab characteristics": Opener(
        "laboratory", lambda ws: ws._edit_lab_characteristics()
    ),
    "add lab specialization source": Opener(
        "laboratory", lambda ws: ws._add_specialty_entry()
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
    # Creation Worksheet
    "spend creation xp": Opener(
        "character",
        lambda ws: ws._spend_creation_xp(
            ws.selected_character, "childhood", creation_xp.childhood_targets()
        ),
    ),
    "native language": Opener(
        "character", lambda ws: ws._set_native_language(ws.selected_character)
    ),
    "general spell level": Opener(
        "character",
        lambda ws: ws._learn_spell_at_its_level(
            ws.selected_character,
            "apprenticeship_spells",
            spells.find_spell(ws.saga, "spell_aegis_of_the_hearth"),
        ),
    ),
    "gauntlet conditions": Opener(
        "character", lambda ws: ws._edit_gauntlet_conditions(ws.selected_character)
    ),
    "power level": Opener(
        "covenant", lambda ws: ws._choose_power_level(ws.selected_covenant)
    ),
    "buy specialist": Opener(
        "covenant", lambda ws: ws._buy_specialist(ws.selected_covenant)
    ),
    "childhood blanks": Opener(
        "character",
        lambda ws: ws._ask_childhood_blanks(
            ws.selected_character,
            next(c for c in creation_xp.CHILDHOODS if c.name == "Traveling"),
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
        assert await wait_until(pilot, lambda: base.selected_kind == opener.node)
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
