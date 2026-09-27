"""Golden test of WorkspaceScreen's key dispatch.

For every section (Collapsible) and tab of every kind of sheet, focus it,
press each section-dispatched key and record what happens: whether the
binding is enabled, and which dialog opens (with its title) or which
notice appears. The result is compared with tests/golden/dispatch_matrix.json,
so a refactor of the dispatch/routing code that changes any of it fails
here. After an intended change, regenerate the file with

    UPDATE_GOLDEN=1 uv run pytest -p no:xdist tests/test_dispatch_matrix.py

(serially: each kind rewrites its own entry in the one file) and review
the diff.
"""

import json
import os
from pathlib import Path

import pytest
from support import wait_until
from textual.widgets import Collapsible, TabbedContent, TabPane, Tree

from ars_magica_manager import catalog, storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import (
    Ability,
    BondPower,
    Book,
    Character,
    Covenant,
    DiaryEntry,
    Familiar,
    IncomeSource,
    Inhabitant,
    KnownSpell,
    Laboratory,
    NamedDescription,
    Possession,
    Saga,
    ScoredTrait,
    Spell,
    VirtueFlawInstance,
)
from ars_magica_manager.screens import WorkspaceScreen

GOLDEN = Path(__file__).parent / "golden" / "dispatch_matrix.json"

#: The keys whose action depends on the active section (see
#: WorkspaceScreen.check_action). Action name per key, for check_action.
KEYS: dict[str, str] = {
    "a": "add",
    "A": "remove",
    "e": "edit",
    "r": "restore",
    "i": "improve",
    "I": "import_data",
    "v": "add_virtue_flaw",
    "V": "remove_virtue_flaw",
}

#: Tree node per sheet kind, in the saga built by _saga().
NODES: dict[str, tuple[str, ...]] = {
    "saga": ("saga",),
    "covenant": ("covenant", "cov1"),
    "character": ("character", "mag1"),
    "laboratory": ("laboratory", "lab1"),
    "familiar": ("familiar", "fam1"),
    "book_group": ("book_group",),
    "spells": ("spells",),
}

_SHEET_VIEW_ATTR = {
    "covenant": "_covenant_sheet_view",
    "character": "_character_sheet_view",
    "laboratory": "_laboratory_sheet_view",
    "familiar": "_familiar_sheet_view",
}


def _first_vf(vf_type: str) -> str:
    return next(
        e.id
        for e in catalog.load_virtue_flaw_catalog()
        if e.type == vf_type and not e.parameters
    )


def _saga() -> Saga:
    """One of everything, with every list holding at least one entry, so
    edit/remove reach their pickers rather than an "empty" notice."""
    boon = next(
        e.id for e in catalog.load_covenant_boon_hook_catalog() if e.type == "Boon"
    )
    hook = next(
        e.id for e in catalog.load_covenant_boon_hook_catalog() if e.type == "Hook"
    )
    lab_vf = catalog.load_lab_virtue_flaw_catalog()[0].id
    spell_id = next(iter(catalog.load_spell_catalog_by_id()))
    trait = [ScoredTrait("Brave", 2)]
    rep = [ScoredTrait("Wise", 1)]

    covenant = Covenant(id="cov1", saga_id="s", name="Keep")
    covenant.reputations = [ScoredTrait("Fair dealing", 2)]
    covenant.boons_hooks = [VirtueFlawInstance(boon), VirtueFlawInstance(hook)]
    covenant.inhabitants = [
        Inhabitant(id=f"inh-{kind}", kind=kind, name=f"A {kind}")
        for kind in ("specialist", "craftsperson", "turb", "inhabitant")
    ] + [
        Inhabitant(id="inh-horse", kind="horse", name="Horses", quantity=2),
        Inhabitant(id="inh-livestock", kind="livestock", name="Sheep", quantity=5),
    ]
    covenant.possessions = [
        Possession(id=f"pos-{kind}", kind=kind, name=f"A {kind}")
        for kind in ("property", "weapon", "armor", "vis_source", "vis_store", "item")
    ]
    covenant.economics.income_sources = [IncomeSource(id="inc1", name="Mill")]

    magus = Character(id="mag1", name="Leandro", type="magus", covenant_id="cov1")
    magus.abilities = [Ability("Latin", level=4)]
    magus.virtues_flaws = [
        VirtueFlawInstance(_first_vf("Virtue")),
        VirtueFlawInstance(_first_vf("Flaw")),
    ]
    magus.personality_traits = list(trait)
    magus.reputations = list(rep)
    magus.raw_vis = {"creo": 3}
    magus.spells_known = [KnownSpell(spell_id)]
    magus.inventory = [Possession(id="item1", kind="item", name="Staff")]
    magus.assigned_lab_id = "lab1"
    companion = Character(id="comp1", name="Alys", type="companion", covenant_id="cov1")

    lab = Laboratory(id="lab1", covenant_id="cov1", name="Tower", owner_id="mag1")
    lab.specialties = ["Ignem"]
    lab.features = ["Big windows"]
    lab.rooms = [NamedDescription("Study")]
    lab.inventory_items = [NamedDescription("Alembic")]
    lab.raw_vis = {"ignem": 2}
    lab.diary = [DiaryEntry(1220, "Spring", "Built")]
    lab.virtues_flaws = [VirtueFlawInstance(lab_vf)]

    familiar = Familiar(id="fam1", character_id="mag1", name="Corax")
    familiar.virtues_flaws = [VirtueFlawInstance(_first_vf("Virtue"))]
    familiar.personality_traits = list(trait)
    familiar.reputations = list(rep)
    familiar.natural_weapons = [Possession(id="nw1", kind="weapon", name="Beak")]
    familiar.abilities = [Ability("Awareness", level=2)]
    familiar.bond_powers = [BondPower(id="bp1", name="Speak")]

    books = [
        Book(
            id="b-cov",
            name="Summa",
            type="Art Summa",
            owner_kind="covenant",
            owner_id="cov1",
        ),
        Book(
            id="b-lab",
            name="Notes",
            type="Other",
            owner_kind="laboratory",
            owner_id="lab1",
        ),
        Book(
            id="b-char",
            name="Diary",
            type="Other",
            owner_kind="character",
            owner_id="mag1",
        ),
        Book(id="b-none", name="Loose", type="Other"),
    ]
    return Saga(
        id="test_saga",
        name="Matrix",
        covenants=[covenant],
        characters=[magus, companion],
        laboratories=[lab],
        familiars=[familiar],
        books=books,
        spells=[
            Spell(id="own1", name="Own Spell", technique="Creo", form="Ignem", level=5)
        ],
    )


def _title(screen) -> str:
    """The text of a dialog's first Label/Static whose id mentions "title"."""
    for widget in screen.query("Label, Static"):
        if widget.id and "title" in widget.id:
            return str(widget.render()).strip()
    return ""


async def _back_to_workspace(pilot, app, workspace) -> None:
    for _ in range(6):
        if app.screen is workspace:
            return
        await pilot.press("escape")
        await pilot.pause()
    assert app.screen is workspace, f"stuck on {type(app.screen).__name__}"


async def _focus_target(pilot, app, view, target) -> None:
    """Make `target` (a Collapsible or TabPane of `view`) the active section
    the way a user would: show its tab, then focus its title (a Collapsible)
    or nothing (a tab)."""
    app.screen.set_focus(None)
    await pilot.pause()
    pane = (
        target
        if isinstance(target, TabPane)
        else next((a for a in target.ancestors if isinstance(a, TabPane)), None)
    )
    if pane is not None:
        view.query_one(TabbedContent).active = pane.id
        await pilot.pause()
    if isinstance(target, Collapsible):
        target.query_one("CollapsibleTitle").focus()
        await wait_until(pilot, lambda: app.screen._active_section() == target.id)
    else:
        app.screen.set_focus(None)
        await pilot.pause()


async def _record_keys(pilot, app, workspace, notices: list[str]) -> dict[str, str]:
    outcomes: dict[str, str] = {}
    for key, action in KEYS.items():
        if not workspace.check_action(action, ()):
            outcomes[key] = "(disabled)"
            continue
        notices.clear()
        await pilot.press(key)
        await pilot.pause()
        await wait_until(
            pilot, lambda: app.screen is not workspace or notices, timeout=1.0
        )
        if app.screen is not workspace:
            screen = app.screen
            title = _title(screen)
            outcomes[key] = type(screen).__name__ + (f": {title}" if title else "")
            await _back_to_workspace(pilot, app, workspace)
        elif notices:
            outcomes[key] = f"notice: {notices[0]}"
        else:
            outcomes[key] = "(nothing)"
    return outcomes


async def _matrix_for(
    kind: str, shard: int | None = None, shards: int = 1
) -> tuple[dict[str, dict], list[str]]:
    """The recorded outcomes for `kind` -- only every `shards`-th target,
    starting at `shard`, unless `shard` is None -- plus the labels of all
    of the sheet's targets."""
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    notices: list[str] = []
    async with app.run_test(size=(140, 70)) as pilot:
        await pilot.press("enter")  # picker -> workspace
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        workspace = app.screen
        original_notify = app.notify

        def record(message, *args, **kwargs):
            notices.append(str(message))
            return original_notify(message, *args, **kwargs)

        app.notify = record  # type: ignore[method-assign]

        tree = workspace.query_one("#nav-tree", Tree)

        def find_node():
            stack = [tree.root]
            while stack:
                candidate = stack.pop()
                if candidate.data == NODES[kind]:
                    return candidate
                stack.extend(candidate.children)
            return None

        # The tree is built as the workspace mounts: wait for the node.
        assert await wait_until(pilot, lambda: find_node() is not None)
        node = find_node()
        tree.select_node(node)
        await pilot.pause()

        attr = _SHEET_VIEW_ATTR.get(kind)
        if attr is None:  # no sheet: the node itself decides the section
            record = {
                "active": workspace._active_section(),
                "keys": await _record_keys(pilot, app, workspace, notices),
            }
            return {"(node)": record}, ["(node)"]

        assert await wait_until(pilot, lambda: getattr(workspace, attr) is not None)
        view = getattr(workspace, attr)
        assert await wait_until(pilot, lambda: view.initial_tab_seen)
        await pilot.pause()
        targets = [w for w in view.query("Collapsible, TabPane") if w.id]
        labels = [f"{type(t).__name__}#{t.id}" for t in targets]
        if shard is not None:
            targets = targets[shard::shards]
        result: dict[str, dict] = {}
        for target in targets:
            await _focus_target(pilot, app, view, target)
            result[f"{type(target).__name__}#{target.id}"] = {
                "active": workspace._active_section(),
                "keys": await _record_keys(pilot, app, workspace, notices),
            }
        return result, labels


def _golden() -> dict:
    if not GOLDEN.exists():
        return {}
    return json.loads(GOLDEN.read_text(encoding="utf-8"))


#: Each sheet's targets are split across this many tests, so that parallel
#: workers share the long ones. Targets are independent: every dialog a key
#: opens is cancelled, so nothing in the saga changes.
SHARDS: dict[str, int] = {"covenant": 6, "character": 4, "familiar": 3, "laboratory": 2}


@pytest.mark.parametrize(
    ("kind", "shard"),
    [(kind, shard) for kind in NODES for shard in range(SHARDS.get(kind, 1))],
)
async def test_dispatch_matrix(kind, shard):
    shards = SHARDS.get(kind, 1)
    if os.environ.get("UPDATE_GOLDEN"):
        if shard:
            pytest.skip("regenerating: shard 0 records the whole sheet")
        matrix, _ = await _matrix_for(kind)
        golden = _golden() | {kind: matrix}
        GOLDEN.parent.mkdir(exist_ok=True)
        GOLDEN.write_text(
            json.dumps(golden, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        return
    matrix, labels = await _matrix_for(kind, shard, shards)
    expected = _golden()[kind]
    assert labels == list(expected)  # same sections and tabs, in the same order
    assert matrix == {label: expected[label] for label in labels[shard::shards]}
