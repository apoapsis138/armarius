"""End-to-end flows for the sheet lists that share one shape in
WorkspaceScreen: add, edit and remove -- acting on the chosen row when there
is one, otherwise asking with a picker. Every delete asks first."""

from dataclasses import dataclass
from typing import Any

import pytest
from support import build_all_tabs, wait_until
from textual.widgets import Input, TabPane, Tree

from ars_magica_manager import storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import (
    BondPower,
    Breakthrough,
    Character,
    Covenant,
    DiaryEntry,
    Familiar,
    IncomeSource,
    Inhabitant,
    Laboratory,
    NamedDescription,
    Possession,
    Saga,
    ScoredTrait,
)
from ars_magica_manager.screens import (
    ConfirmScreen,
    FieldsDialog,
    RemovalPickerScreen,
    SelectableList,
    WorkspaceScreen,
)


def _saga() -> Saga:
    def two() -> list[ScoredTrait]:
        return [ScoredTrait("Alpha", 1), ScoredTrait("Beta", 2)]

    covenant = Covenant(id="cov1", saga_id="test_saga", name="Keep")
    covenant.reputations = two()
    covenant.possessions = [
        Possession(id="ci1", kind="item", name="Lens [cracked]"),
        Possession(id="ci2", kind="item", name="Mirror"),
        Possession(id="pr1", kind="property", name="Mill [old]"),
        Possession(id="pr2", kind="property", name="Farm"),
    ]
    covenant.inhabitants = [
        Inhabitant(id="tu1", kind="turb", name="Guard [a]"),
        Inhabitant(id="tu2", kind="turb", name="Guard B"),
    ]
    covenant.economics.income_sources = [
        IncomeSource(id="in1", name="Toll [bridge]"),
        IncomeSource(id="in2", name="Ferry"),
    ]
    magus = Character(id="mag1", name="Leandro", type="magus", covenant_id="cov1")
    magus.personality_traits = two()
    magus.reputations = two()
    magus.inventory = [
        Possession(id="it1", kind="item", name="Staff [old]"),
        Possession(id="it2", kind="item", name="Cloak"),
    ]
    magus.breakthroughs = [Breakthrough("Aegis [piercing]"), Breakthrough("Wards")]
    familiar = Familiar(id="fam1", character_id="mag1", name="Corax")
    familiar.personality_traits = two()
    familiar.reputations = two()
    familiar.natural_weapons = [
        Possession(id="nw1", kind="weapon", name="Beak [sharp]"),
        Possession(id="nw2", kind="weapon", name="Talons"),
    ]
    familiar.bond_powers = [
        BondPower(id="bp1", name="Speak [loud]"),
        BondPower(id="bp2", name="Sense"),
    ]
    lab = Laboratory(id="lab1", covenant_id="cov1", name="Tower", owner_id="mag1")
    lab.rooms = [NamedDescription("Study [east]"), NamedDescription("Vault")]
    lab.inventory_items = [NamedDescription("Alembic [glass]"), NamedDescription("Jar")]
    lab.diary = [
        DiaryEntry(1220, "Spring", "Built [first]"),
        DiaryEntry(1220, "Summer", "Moved in"),
    ]
    return Saga(
        id="test_saga",
        name="Flows",
        covenants=[covenant],
        characters=[magus],
        familiars=[familiar],
        laboratories=[lab],
    )


@dataclass(frozen=True)
class ListCase:
    node: tuple[str, str]
    section: str
    list_id: str
    entries: Any  # saved Saga -> the list


TRAIT_LISTS: dict[str, ListCase] = {
    "covenant-reputations": ListCase(
        ("covenant", "cov1"),
        "section-cov-reputations",
        "cov-reputations-list",
        lambda s: s.covenants[0].reputations,
    ),
    "character-traits": ListCase(
        ("character", "mag1"),
        "section-personality-traits",
        "personality-traits-list",
        lambda s: s.characters[0].personality_traits,
    ),
    "character-reputations": ListCase(
        ("character", "mag1"),
        "section-reputations",
        "character-reputations-list",
        lambda s: s.characters[0].reputations,
    ),
    "familiar-traits": ListCase(
        ("familiar", "fam1"),
        "section-fam-personality-traits",
        "fam-personality-traits-list",
        lambda s: s.familiars[0].personality_traits,
    ),
    "familiar-reputations": ListCase(
        ("familiar", "fam1"),
        "section-fam-reputations",
        "fam-reputations-list",
        lambda s: s.familiars[0].reputations,
    ),
}

#: The flows that don't depend on which row is chosen run on one character
#: list and the covenant's (which has its own score range): the lists share
#: one handler. The chosen-row flows run on every list, since each list has
#: its own "which row is chosen" method and owner.
SHARED_FLOW_LISTS = ["character-traits", "covenant-reputations"]

_SHEET_VIEW_ATTR = {
    "covenant": "_covenant_sheet_view",
    "character": "_character_sheet_view",
    "familiar": "_familiar_sheet_view",
    "laboratory": "_laboratory_sheet_view",
}


def _saved(case: ListCase) -> list:
    return case.entries(storage.load_saga("test_saga"))


async def _open(pilot, app, case: ListCase):
    """Open the workspace on `case`'s sheet and make its section active."""
    await pilot.press("enter")
    assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
    workspace = app.screen
    tree = workspace.query_one("#nav-tree", Tree)

    def find_node():
        stack = [tree.root]
        while stack:
            node = stack.pop()
            if node.data == case.node:
                return node
            stack.extend(node.children)
        return None

    # The tree is built as the workspace mounts: wait for the node to exist.
    assert await wait_until(pilot, lambda: find_node() is not None)
    tree.select_node(find_node())
    attr = _SHEET_VIEW_ATTR[case.node[0]]
    assert await wait_until(pilot, lambda: getattr(workspace, attr) is not None)
    view = getattr(workspace, attr)
    await build_all_tabs(pilot, view)
    section = view.query_one(f"#{case.section}")
    if isinstance(section, TabPane):
        view.query_one("TabbedContent").active = section.id
        await pilot.pause()
        view.query_one(f"#{case.list_id}").focus()
    else:
        pane = next((a for a in section.ancestors if isinstance(a, TabPane)), None)
        if pane is not None:
            view.query_one("TabbedContent").active = pane.id
            await pilot.pause()
        section.query_one("CollapsibleTitle").focus()
    assert await wait_until(pilot, lambda: workspace._active_section() == case.section)
    return workspace, view


async def _choose_row(pilot, view, case: ListCase, data_index: int) -> None:
    """Choose a row the way the user does: highlight it in the list."""
    rows = view.query_one(f"#{case.list_id}", SelectableList)
    rows.focus()
    await pilot.pause()
    position = next(i for i, (index, _) in enumerate(rows._rows) if index == data_index)
    rows.highlighted = position
    assert await wait_until(pilot, lambda: rows._marked == position)


async def _press(pilot, app, key: str, screen_type: type) -> None:
    await pilot.press(key)
    assert await wait_until(pilot, lambda: isinstance(app.screen, screen_type)), (
        f"{key!r} opened {type(app.screen).__name__}, not {screen_type.__name__}"
    )


async def _save_trait(pilot, app, name: str | None, score: int) -> None:
    dialog = app.screen
    if name is not None:
        dialog.query_one("#fld-name", Input).value = name
    dialog.query_one("#fld-score", Input).value = str(score)
    dialog.query_one("#btn-save").press()
    assert await wait_until(pilot, lambda: app.screen is not dialog)


@pytest.fixture
def case(request) -> ListCase:
    return TRAIT_LISTS[request.param]


@pytest.mark.parametrize("case", SHARED_FLOW_LISTS, indirect=True)
async def test_trait_list_add(case):
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        _, view = await _open(pilot, app, case)
        await _press(pilot, app, "a", FieldsDialog)
        await _save_trait(pilot, app, "Gamma", 3)
        assert await wait_until(pilot, lambda: len(_saved(case)) == 3)
        rows = view.query_one(f"#{case.list_id}", SelectableList)
        assert await wait_until(pilot, lambda: "Gamma: +3" in str(rows._rows))
    assert [(t.name, t.score) for t in _saved(case)] == [
        ("Alpha", 1),
        ("Beta", 2),
        ("Gamma", 3),
    ]


@pytest.mark.parametrize("case", SHARED_FLOW_LISTS, indirect=True)
async def test_trait_list_edit_picks_when_nothing_is_chosen(case):
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _open(pilot, app, case)
        await _press(pilot, app, "e", RemovalPickerScreen)
        # Every score is shown signed, Reputations too (B14).
        assert await wait_until(pilot, lambda: len(app.screen.query("ListItem")) == 2)
        labels = [str(label.render()) for label in app.screen.query("ListItem Label")]
        assert labels == ["Alpha: +1", "Beta: +2"]
        await pilot.press("down")
        await _press(pilot, app, "enter", FieldsDialog)
        assert app.screen.query_one("#fld-name", Input).value == "Beta"
        await _save_trait(pilot, app, "Beta prime", 3)
        assert await wait_until(pilot, lambda: _saved(case)[1].name == "Beta prime")
    assert [(t.name, t.score) for t in _saved(case)] == [
        ("Alpha", 1),
        ("Beta prime", 3),
    ]


@pytest.mark.parametrize("case", list(TRAIT_LISTS), indirect=True)
async def test_trait_list_edit_uses_the_chosen_row(case):
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        _, view = await _open(pilot, app, case)
        await _choose_row(pilot, view, case, 1)
        await _press(pilot, app, "e", FieldsDialog)  # no picker
        assert app.screen.query_one("#fld-name", Input).value == "Beta"
        await _save_trait(pilot, app, None, -1)
        assert await wait_until(pilot, lambda: _saved(case)[1].score == -1)
    assert [(t.name, t.score) for t in _saved(case)] == [("Alpha", 1), ("Beta", -1)]


@pytest.mark.parametrize("case", SHARED_FLOW_LISTS, indirect=True)
async def test_trait_list_remove_picks_when_nothing_is_chosen(case):
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, _ = await _open(pilot, app, case)
        await _press(pilot, app, "A", RemovalPickerScreen)
        await pilot.press("down")
        await _press(pilot, app, "enter", ConfirmScreen)
        await pilot.press("y")
        assert await wait_until(pilot, lambda: len(_saved(case)) == 1)
        assert app.screen is workspace
    assert [t.name for t in _saved(case)] == ["Alpha"]


@pytest.mark.parametrize("case", list(TRAIT_LISTS), indirect=True)
async def test_trait_list_remove_uses_the_chosen_row(case):
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, case)
        await _choose_row(pilot, view, case, 0)
        await _press(pilot, app, "A", ConfirmScreen)  # no picker
        assert _confirm_message(app) == "Delete Alpha?"
        await pilot.press("n")  # keeps it
        assert await wait_until(pilot, lambda: app.screen is workspace)
        assert len(_saved(case)) == 2
        await _press(pilot, app, "A", ConfirmScreen)
        await pilot.press("y")
        assert await wait_until(pilot, lambda: len(_saved(case)) == 1)
        # Nothing is chosen any more: A asks which one.
        await _press(pilot, app, "A", RemovalPickerScreen)
    assert [t.name for t in _saved(case)] == ["Beta"]


@pytest.mark.parametrize("case", SHARED_FLOW_LISTS, indirect=True)
async def test_trait_list_cancelling_changes_nothing(case):
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, _ = await _open(pilot, app, case)
        for key in ("a", "e", "A"):
            await pilot.press(key)
            assert await wait_until(pilot, lambda: app.screen is not workspace)
            await pilot.press("escape")
            assert await wait_until(pilot, lambda: app.screen is workspace)
    assert [(t.name, t.score) for t in _saved(case)] == [("Alpha", 1), ("Beta", 2)]


#: Possession-shaped lists whose edit handlers had no test.
ITEM_LISTS: dict[str, ListCase] = {
    "character-inventory": ListCase(
        ("character", "mag1"),
        "section-inventory",
        "inventory-list",
        lambda s: s.characters[0].inventory,
    ),
    "research-goals": ListCase(
        ("character", "mag1"),
        "section-research-goals",
        "research-goals-list",
        lambda s: s.characters[0].breakthroughs,
    ),
    "familiar-natural-weapons": ListCase(
        ("familiar", "fam1"),
        "section-fam-natural-weapons",
        "fam-natural-weapons-list",
        lambda s: s.familiars[0].natural_weapons,
    ),
    "familiar-bond-powers": ListCase(
        ("familiar", "fam1"),
        "tab-fam-powers",
        "fam-bond-powers-list",
        lambda s: s.familiars[0].bond_powers,
    ),
    "covenant-items": ListCase(
        ("covenant", "cov1"),
        "section-pos-item",
        "pos-item-list",
        lambda s: [p for p in s.covenants[0].possessions if p.kind == "item"],
    ),
    "covenant-property": ListCase(
        ("covenant", "cov1"),
        "section-pos-property",
        "pos-property-list",
        lambda s: [p for p in s.covenants[0].possessions if p.kind == "property"],
    ),
    "covenant-turb": ListCase(
        ("covenant", "cov1"),
        "section-inh-turb",
        "inh-turb-list",
        lambda s: s.covenants[0].inhabitants,
    ),
    "covenant-income": ListCase(
        ("covenant", "cov1"),
        "section-eco-income",
        "eco-income-list",
        lambda s: s.covenants[0].economics.income_sources,
    ),
    "lab-rooms": ListCase(
        ("laboratory", "lab1"),
        "section-lab-rooms",
        "lab-rooms-list",
        lambda s: s.laboratories[0].rooms,
    ),
    "lab-items": ListCase(
        ("laboratory", "lab1"),
        "section-lab-items",
        "lab-items-list",
        lambda s: s.laboratories[0].inventory_items,
    ),
    "lab-diary": ListCase(
        ("laboratory", "lab1"),
        "tab-lab-diary",
        "lab-diary-list",
        lambda s: s.laboratories[0].diary,
    ),
}


async def _save_name(pilot, app, name: str) -> None:
    dialog = app.screen
    dialog.query_one("#fld-name", Input).value = name
    dialog.query_one("#btn-save").press()
    assert await wait_until(pilot, lambda: app.screen is not dialog)


@pytest.mark.parametrize("name", list(ITEM_LISTS))
async def test_item_list_edit_picks_when_nothing_is_chosen(name):
    case = ITEM_LISTS[name]
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _open(pilot, app, case)
        await _press(pilot, app, "e", RemovalPickerScreen)
        await pilot.press("down")
        await _press(pilot, app, "enter", FieldsDialog)
        await _save_name(pilot, app, "Renamed")
        assert await wait_until(pilot, lambda: _saved(case)[1].name == "Renamed")
    assert len(_saved(case)) == 2


@pytest.mark.parametrize("name", list(ITEM_LISTS))
async def test_item_list_edit_uses_the_chosen_row(name):
    case = ITEM_LISTS[name]
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        _, view = await _open(pilot, app, case)
        await _choose_row(pilot, view, case, 0)
        await _press(pilot, app, "e", FieldsDialog)  # no picker
        await _save_name(pilot, app, "Renamed")
        assert await wait_until(pilot, lambda: _saved(case)[0].name == "Renamed")
    assert _saved(case)[1].name == case.entries(_saga())[1].name


def _confirm_message(app) -> str:
    return str(app.screen.query_one("#confirm-message").render())


@pytest.mark.parametrize("name", list(ITEM_LISTS))
async def test_item_list_remove_uses_the_chosen_row_after_asking(name):
    """A on the chosen row asks "Delete <name>?" (brackets and all): No
    keeps it, Yes deletes it, and afterwards nothing is chosen, so A asks
    which one."""
    case = ITEM_LISTS[name]
    storage.save_saga(_saga())
    first, second = (entry.name for entry in case.entries(_saga()))
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, case)
        await _choose_row(pilot, view, case, 0)
        await _press(pilot, app, "A", ConfirmScreen)  # no picker
        assert _confirm_message(app) == f"Delete {first}?"
        await pilot.press("n")
        assert await wait_until(pilot, lambda: app.screen is workspace)
        assert len(_saved(case)) == 2

        await _press(pilot, app, "A", ConfirmScreen)
        await pilot.press("y")
        assert await wait_until(pilot, lambda: len(_saved(case)) == 1)
        assert [entry.name for entry in _saved(case)] == [second]
        rows = view.query_one(f"#{case.list_id}", SelectableList)
        assert await wait_until(pilot, lambda: first not in str(rows._rows))

        await _press(pilot, app, "A", RemovalPickerScreen)


@pytest.mark.parametrize("name", list(ITEM_LISTS))
async def test_item_list_remove_picks_when_nothing_is_chosen(name):
    case = ITEM_LISTS[name]
    storage.save_saga(_saga())
    first, _ = (entry.name for entry in case.entries(_saga()))
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _open(pilot, app, case)
        await _press(pilot, app, "A", RemovalPickerScreen)
        await pilot.press("down")
        await _press(pilot, app, "enter", ConfirmScreen)
        await pilot.press("y")
        assert await wait_until(pilot, lambda: len(_saved(case)) == 1)
    assert [entry.name for entry in _saved(case)] == [first]
