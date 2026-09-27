"""End-to-end flows for the sheet lists that share one shape in
WorkspaceScreen: add, edit and remove -- acting on the chosen row when there
is one, otherwise asking with a picker. Every delete asks first."""

from dataclasses import dataclass
from typing import Any

import pytest
from support import wait_until
from textual.widgets import Input, Tree

from ars_magica_manager import storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import (
    Character,
    Covenant,
    Familiar,
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


def _is_form(screen, title: str) -> bool:
    """`screen` is the FieldsDialog titled `title`."""
    return isinstance(screen, FieldsDialog) and screen.title_text == title


def _saga() -> Saga:
    def two() -> list[ScoredTrait]:
        return [ScoredTrait("Alpha", 1), ScoredTrait("Beta", 2)]

    covenant = Covenant(id="cov1", saga_id="test_saga", name="Keep")
    covenant.reputations = two()
    magus = Character(id="mag1", name="Leandro", type="magus", covenant_id="cov1")
    magus.personality_traits = two()
    magus.reputations = two()
    magus.inventory = [
        Possession(id="it1", kind="item", name="Staff"),
        Possession(id="it2", kind="item", name="Cloak"),
    ]
    familiar = Familiar(id="fam1", character_id="mag1", name="Corax")
    familiar.personality_traits = two()
    familiar.reputations = two()
    familiar.natural_weapons = [
        Possession(id="nw1", kind="weapon", name="Beak"),
        Possession(id="nw2", kind="weapon", name="Talons"),
    ]
    return Saga(
        id="test_saga",
        name="Flows",
        covenants=[covenant],
        characters=[magus],
        familiars=[familiar],
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

_SHEET_VIEW_ATTR = {
    "covenant": "_covenant_sheet_view",
    "character": "_character_sheet_view",
    "familiar": "_familiar_sheet_view",
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
    assert await wait_until(pilot, lambda: view.initial_tab_seen)
    await pilot.pause()
    section = view.query_one(f"#{case.section}")
    pane = next(
        (a for a in section.ancestors if a.__class__.__name__ == "TabPane"), None
    )
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


@pytest.mark.parametrize("case", list(TRAIT_LISTS), indirect=True)
async def test_trait_list_add(case):
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _open(pilot, app, case)
        await _press(pilot, app, "a", FieldsDialog)
        await _save_trait(pilot, app, "Gamma", 3)
        assert await wait_until(pilot, lambda: len(_saved(case)) == 3)
    assert [(t.name, t.score) for t in _saved(case)] == [
        ("Alpha", 1),
        ("Beta", 2),
        ("Gamma", 3),
    ]


@pytest.mark.parametrize("case", list(TRAIT_LISTS), indirect=True)
async def test_trait_list_edit_picks_when_nothing_is_chosen(case):
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _open(pilot, app, case)
        await _press(pilot, app, "e", RemovalPickerScreen)
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


@pytest.mark.parametrize("case", list(TRAIT_LISTS), indirect=True)
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
        _, view = await _open(pilot, app, case)
        await _choose_row(pilot, view, case, 0)
        await _press(pilot, app, "A", ConfirmScreen)  # no picker
        await pilot.press("y")
        assert await wait_until(pilot, lambda: len(_saved(case)) == 1)
    assert [t.name for t in _saved(case)] == ["Beta"]


@pytest.mark.parametrize("case", list(TRAIT_LISTS), indirect=True)
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
    "familiar-natural-weapons": ListCase(
        ("familiar", "fam1"),
        "section-fam-natural-weapons",
        "fam-natural-weapons-list",
        lambda s: s.familiars[0].natural_weapons,
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
    assert [p.id for p in _saved(case)] == [p.id for p in case.entries(_saga())]


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
