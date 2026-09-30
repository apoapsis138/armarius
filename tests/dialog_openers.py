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

from ars_magica_manager import catalog, storage
from ars_magica_manager import economics as eco
from ars_magica_manager import screens as scr
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import Ability, Character, Saga
from ars_magica_manager.screens.workspace import _COVENANT_REPUTATIONS


def contract_saga() -> Saga:
    """everything_saga() plus an unbonded magus (so a familiar can be bound),
    in Autumn: not the first season, so a form that defaults to the saga's
    season is told apart from one that defaults to Spring."""
    saga = everything_saga()
    saga.current_season = "Autumn"
    saga.characters.append(
        Character(id="mag2", name="Brother Oda", type="magus", covenant_id="cov1")
    )
    grog = Character(id="grog9", name="Hugo", type="grog", covenant_id="cov1")
    grog.abilities = [Ability("Single Weapon"), Ability("Brawl"), Ability("Awareness")]
    saga.characters.append(grog)
    return saga


@dataclass(frozen=True)
class Opener:
    #: Tree node to select first (a NODES key), or None for the saga picker.
    node: str | None
    #: Opens the dialog, given the workspace (or saga picker) screen.
    open: Callable[[object], object]


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
    view.query_one("#section-vf-virtues CollapsibleTitle").focus()
    await until(lambda: ws._active_section() == "section-vf-virtues")
    ws.action_add_virtue_flaw()
    picker = await wait_for_screen(ws.app, scr.VirtueFlawPickerScreen)
    picker._on_entry_selected(
        catalog.load_virtue_flaw_catalog_by_id()[vf_id or _param_vf()]
    )


async def _open_lab_choice_prompt(ws) -> None:
    """Add a laboratory Flaw whose Specialization the owner chooses: the
    picker asks for it (STORY-817)."""
    view = ws._current_sheet_view()
    view.query_one(TabbedContent).active = "tab-lab-vf"
    # The tab is built as it is first shown.
    await until(lambda: view.query("#section-lab-vf-flaws CollapsibleTitle"))
    view.query_one("#section-lab-vf-flaws CollapsibleTitle").focus()
    await until(lambda: ws._active_section() == "section-lab-vf-flaws")
    ws.action_add_virtue_flaw()
    picker = await wait_for_screen(ws.app, scr.LabVirtueFlawPickerScreen)
    picker._on_entry_selected(
        catalog.load_lab_virtue_flaw_catalog_by_id()["labvf_disorganized"]
    )


def _open_mastery_ability(ws) -> None:
    """Edit a known spell's Mastery, then add a Mastery Ability."""
    ws._edit_spell_mastery_at(0)

    async def add() -> None:
        edit = await wait_for_screen(ws.app, scr.MasteryEditScreen)
        edit._add_ability()

    ws.app.call_later(add)


def _pick(open_picker, index: int = 0):
    """Open a dialog reached through a "which one?" picker, choosing the
    entry at `index`."""

    async def opener(ws) -> None:
        # The chosen row is looked for in the section's tab: build it.
        await ws._current_sheet_view().build_all_tabs()
        open_picker(ws)
        picker = await wait_for_screen(ws.app, scr.RemovalPickerScreen)
        await until(lambda: picker.query("ListItem"))  # mounted
        picker.dismiss(index)

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
    "add research goal": Opener("character", lambda ws: ws._add_research_goal()),
    "virtue parameters": Opener("character", _open_param_prompt),
    "virtue ability choice": Opener(
        "character", lambda ws: _open_param_prompt(ws, "vf_puissant_ability")
    ),
    "add mastery ability": Opener("character", _open_mastery_ability),
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
    # Seasons (STORY-903)
    "plan a season": Opener("character", lambda ws: ws._plan_season()),
    "add character diary entry": Opener(
        "character", lambda ws: ws._add_character_diary_entry()
    ),
    "add covenant diary entry": Opener(
        "covenant", lambda ws: ws._add_covenant_diary_entry()
    ),
    # Enchanted devices (STORY-305)
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
    # Added for STORY-1123 (forms that had only bespoke tests)
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
        "covenant", _pick(lambda ws: ws._edit_income_source())
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
    "add spell": Opener("spells", lambda ws: ws._spell_form(None)),
    "edit spell": Opener("spells", lambda ws: ws._spell_form(ws.saga.spells[0])),
    "add ability": Opener("character", _open_ability_details),
    "edit arts": Opener("character", lambda ws: ws._edit_arts()),
    "edit familiar fatigue": Opener("familiar", lambda ws: ws._edit_familiar_fatigue()),
    "add bond power": Opener("familiar", lambda ws: ws._familiar_bond_power_form(None)),
    "edit bond power": Opener("familiar", lambda ws: ws._familiar_bond_power_form(0)),
    "add lab raw vis": Opener("laboratory", lambda ws: ws._add_lab_raw_vis()),
    "edit lab raw vis": Opener("laboratory", _pick(lambda ws: ws._edit_lab_raw_vis())),
    "edit lab diary entry": Opener(
        "laboratory", _pick(lambda ws: ws._edit_diary_entry())
    ),
    "edit lab specialization source": Opener(
        "laboratory", _pick(lambda ws: ws._edit_specialty_entry())
    ),
    "edit lab room": Opener(
        "laboratory", _pick(lambda ws: ws._edit_named("section-lab-rooms"))
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
        if opener.node not in ("saga", "spells", "book_group"):
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
    scr.MasteryEditScreen,
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
