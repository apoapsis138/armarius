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
from ars_magica_manager import screens as scr
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import Character, Saga


def contract_saga() -> Saga:
    """everything_saga() plus an unbonded magus (so a familiar can be bound)."""
    saga = everything_saga()
    saga.characters.append(
        Character(id="mag2", name="Brother Oda", type="magus", covenant_id="cov1")
    )
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


async def _open_param_prompt(ws) -> None:
    """Add a Virtue with a parameter (from the Virtues section): the picker
    asks for it."""
    view = ws._current_sheet_view()
    view.query_one(TabbedContent).active = "tab-vf"
    await until(lambda: view.query_one(TabbedContent).active == "tab-vf")
    view.query_one("#section-vf-virtues CollapsibleTitle").focus()
    await until(lambda: ws._active_section() == "section-vf-virtues")
    ws.action_add_virtue_flaw()
    picker = await wait_for_screen(ws.app, scr.VirtueFlawPickerScreen)
    picker._on_entry_selected(catalog.load_virtue_flaw_catalog_by_id()[_param_vf()])


def _open_mastery_ability(ws) -> None:
    """Edit a known spell's Mastery, then add a Mastery Ability."""
    ws._edit_spell_mastery_at(0)

    async def add() -> None:
        edit = await wait_for_screen(ws.app, scr.MasteryEditScreen)
        edit._add_ability()

    ws.app.call_later(add)


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
    "virtue parameters": Opener("character", _open_param_prompt),
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
    "add lab diary entry": Opener("laboratory", lambda ws: ws._add_diary_entry()),
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
    opened = opener.open(base)
    if inspect.isawaitable(opened):
        await opened
    assert await wait_until(pilot, lambda: _is_dialog(app.screen, base), timeout=3.0), (
        f"{name!r} didn't open (top screen: {type(app.screen).__name__})"
    )
    await pilot.pause()
    return base, app.screen


#: Screens a dialog is opened through (not the dialog itself).
_ON_THE_WAY = (
    scr.VirtueFlawPickerScreen,
    scr.MasteryEditScreen,
    scr.RemovalPickerScreen,
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
