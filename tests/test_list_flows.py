"""End-to-end flows for the sheet lists that share one shape in
WorkspaceScreen: a adds, e edits and d deletes the chosen row. A list that
takes focus always has one (the first, until another is chosen), so nothing
asks "which one?". Every delete asks first."""

from dataclasses import dataclass
from typing import Any

import pytest
from support import build_all_tabs, wait_until
from textual.widgets import Input, Select, TabPane, Tree

from ars_magica_manager import battles, place_events, sieges, storage
from ars_magica_manager.models import (
    Battle,
    BattleSide,
    BondPower,
    BoundBeing,
    Breakthrough,
    Character,
    CharacterPower,
    ConstantEffect,
    Covenant,
    Creature,
    CreatureAttack,
    CreaturePower,
    DiaryEntry,
    EnchantedDevice,
    Familiar,
    Fight,
    FightSide,
    IncomeSource,
    Inhabitant,
    InstilledEffect,
    LabItemBenefit,
    Laboratory,
    LabSpecialtyGrant,
    NamedDescription,
    Neighbour,
    Possession,
    Saga,
    SagaSource,
    ScoredTrait,
    Siege,
    TraditionEffect,
    VirtueFlawInstance,
)
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import (
    ConfirmScreen,
    FieldsDialog,
    SelectableList,
    WorkspaceScreen,
)
from ars_magica_manager.tui.screens.prompts import MenuScreen
from ars_magica_manager.tui.screens.widgets import SheetSection, section_stop
from ars_magica_manager.tui.screens.workspace.base import CHOOSE_FIRST


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
        Inhabitant(id="ho1", kind="hound", name="Alaunt [war]", quantity=2),
        Inhabitant(id="ho2", kind="hound", name="Goshawk"),
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
    magus.traditions = ["trad_vitkir"]
    magus.tradition_effects = [
        TraditionEffect("Rune [wealth]", tradition="trad_vitkir"),
        TraditionEffect("Ward", tradition="trad_vitkir"),
    ]
    magus.powers = [
        CharacterPower("Owl [grey]", "Greater Power"),
        CharacterPower("Warmth", "Lesser Power"),
    ]
    magus.constant_effects = [
        ConstantEffect("Ring [of flight]", powerful=True),
        ConstantEffect("Ward"),
    ]
    magus.bound_beings = [
        BoundBeing("Huginn [raven]", tradition="trad_vitkir"),
        BoundBeing("Muninn", tradition="trad_vitkir"),
    ]
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
    lab.personality_traits = two()
    lab.inventory_items = [NamedDescription("Alembic [glass]"), NamedDescription("Jar")]
    lab.diary = [
        DiaryEntry(1220, "Spring", "Built [first]"),
        DiaryEntry(1220, "Summer", "Moved in"),
    ]
    creature = Creature(id="cr1", name="Boglin")
    creature.personality_traits = two()
    creature.reputations = two()
    creature.attacks = [CreatureAttack("Bite [sharp]"), CreatureAttack("Claws")]
    creature.powers = [CreaturePower("Hide [in mud]"), CreaturePower("Lure")]
    return Saga(
        id="test_saga",
        name="Flows",
        creatures=[creature],
        covenants=[covenant],
        characters=[magus],
        familiars=[familiar],
        laboratories=[lab],
    )


@dataclass(frozen=True)
class ListCase:
    node: tuple[str, ...]
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
    "lab-traits": ListCase(
        ("laboratory", "lab1"),
        "section-lab-personality-traits",
        "lab-traits-list",
        lambda s: s.laboratories[0].personality_traits,
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
    "creature-traits": ListCase(
        ("creature", "cr1"),
        "section-cr-personality-traits",
        "cr-personality-traits-list",
        lambda s: s.creatures[0].personality_traits,
    ),
    "creature-reputations": ListCase(
        ("creature", "cr1"),
        "section-cr-reputations",
        "cr-reputations-list",
        lambda s: s.creatures[0].reputations,
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
    "saga_content": "_saga_content_view",
    "creature": "_creature_sheet_view",
    "conflicts": "_conflicts_view",
    "neighbour": "_neighbour_sheet_view",
}


def _saved(case: ListCase) -> list:
    return case.entries(storage.load_saga("test_saga"))


async def _open(pilot, app, case: ListCase):
    """Open the workspace on `case`'s sheet and give its section focus,
    as Tab or a click would: in its list, with the first row chosen."""
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
        section_stop(section).focus()
    assert await wait_until(pilot, lambda: workspace._active_section() == case.section)
    rows = view.query_one(f"#{case.list_id}", SelectableList)
    assert await wait_until(pilot, lambda: rows.selected_data_index == 0)
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
async def test_trait_list_edit_needs_no_choosing_first(case):
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        _, view = await _open(pilot, app, case)
        # Every score is shown signed, Reputations too.
        rows = view.query_one(f"#{case.list_id}", SelectableList)
        assert [label for _, label in rows._rows] == ["Alpha: +1", "Beta: +2"]
        # The section took focus with its first row chosen: e edits it.
        await _press(pilot, app, "e", FieldsDialog)
        assert app.screen.query_one("#fld-name", Input).value == "Alpha"
        await pilot.press("escape")
        await pilot.press("down")
        await _press(pilot, app, "e", FieldsDialog)
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
async def test_trait_list_delete_needs_no_choosing_first(case):
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, _ = await _open(pilot, app, case)
        await pilot.press("down")
        await _press(pilot, app, "d", ConfirmScreen)
        assert _confirm_message(app) == "Delete Beta?"
        await pilot.press("y")
        assert await wait_until(pilot, lambda: len(_saved(case)) == 1)
        assert app.screen is workspace
    assert [t.name for t in _saved(case)] == ["Alpha"]


@pytest.mark.parametrize("case", SHARED_FLOW_LISTS, indirect=True)
async def test_a_collapsed_section_has_no_row_to_act_on(case):
    """c collapses the focused section, leaving focus on its title: with no
    row chosen e and d say so rather than asking which one."""
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    notices: list[str] = []
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, case)
        section = view.query_one(f"#{case.section}", SheetSection)
        rows = view.query_one(f"#{case.list_id}", SelectableList)
        app.notify = lambda message, **_: notices.append(str(message))  # type: ignore[method-assign]
        await pilot.press("c")
        assert await wait_until(pilot, lambda: section.collapsed)
        assert workspace._active_section() == case.section
        for key in ("e", "d"):
            await pilot.press(key)
            await pilot.pause()
            assert app.screen is workspace
        assert notices == [CHOOSE_FIRST, CHOOSE_FIRST]
        # c again opens it, with focus back in the list on a row.
        await pilot.press("c")
        assert await wait_until(pilot, lambda: not section.collapsed)
        assert await wait_until(pilot, lambda: app.focused is rows)
        assert await wait_until(pilot, lambda: rows.selected_data_index == 0)
    assert len(_saved(case)) == 2


@pytest.mark.parametrize("case", list(TRAIT_LISTS), indirect=True)
async def test_trait_list_remove_uses_the_chosen_row(case):
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, case)
        await _choose_row(pilot, view, case, 0)
        await _press(pilot, app, "d", ConfirmScreen)  # no picker
        assert _confirm_message(app) == "Delete Alpha?"
        await pilot.press("n")  # keeps it
        assert await wait_until(pilot, lambda: app.screen is workspace)
        assert len(_saved(case)) == 2
        await _press(pilot, app, "d", ConfirmScreen)
        await pilot.press("y")
        assert await wait_until(pilot, lambda: len(_saved(case)) == 1)
        # The list keeps focus, so the row that moved up is chosen: d again
        # is about that one.
        await _press(pilot, app, "d", ConfirmScreen)
        assert _confirm_message(app) == "Delete Beta?"
    assert [t.name for t in _saved(case)] == ["Beta"]


@pytest.mark.parametrize("case", SHARED_FLOW_LISTS, indirect=True)
async def test_trait_list_cancelling_changes_nothing(case):
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, _ = await _open(pilot, app, case)
        for key in ("a", "e", "d"):
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
    "tradition-effects": ListCase(
        ("character", "mag1"),
        "section-teff-trad_vitkir",
        "trad-trad_vitkir-effects",
        lambda s: s.characters[0].tradition_effects,
    ),
    "character-constant-effects": ListCase(
        ("character", "mag1"),
        "section-char-constant-effects",
        "char-constant-effects-list",
        lambda s: s.characters[0].constant_effects,
    ),
    "character-powers": ListCase(
        ("character", "mag1"),
        "section-char-powers",
        "char-powers-list",
        lambda s: s.characters[0].powers,
    ),
    "tradition-bonds": ListCase(
        ("character", "mag1"),
        "section-tbond-trad_vitkir",
        "trad-trad_vitkir-bonds",
        lambda s: s.characters[0].bound_beings,
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
        lambda s: [i for i in s.covenants[0].inhabitants if i.kind == "turb"],
    ),
    "covenant-hounds": ListCase(
        ("covenant", "cov1"),
        "section-inh-hound",
        "inh-hound-list",
        lambda s: [i for i in s.covenants[0].inhabitants if i.kind == "hound"],
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
    "creature-attacks": ListCase(
        ("creature", "cr1"),
        "section-cr-attacks",
        "cr-attacks-list",
        lambda s: s.creatures[0].attacks,
    ),
    "creature-powers": ListCase(
        ("creature", "cr1"),
        "section-cr-powers",
        "cr-powers-list",
        lambda s: s.creatures[0].powers,
    ),
}


async def _save_name(pilot, app, name: str) -> None:
    dialog = app.screen
    dialog.query_one("#fld-name", Input).value = name
    dialog.query_one("#btn-save").press()
    assert await wait_until(pilot, lambda: app.screen is not dialog)


def _confirm_message(app) -> str:
    return str(app.screen.query_one("#confirm-message").render())


@pytest.mark.parametrize("name", list(ITEM_LISTS))
async def test_item_list_edit_and_delete_act_on_the_chosen_row(name):
    """In one session: e and d need no choosing first (the list opens with
    its first row chosen), act on the chosen row, and d asks "Delete
    <name>?" (brackets and all) first -- No keeps it, Yes deletes it, and
    afterwards the row that took its place is chosen."""
    case = ITEM_LISTS[name]
    storage.save_saga(_saga())
    first, _ = (entry.name for entry in case.entries(_saga()))
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, case)
        rows = view.query_one(f"#{case.list_id}", SelectableList)

        await pilot.press("down")  # from the first row, chosen on opening
        await _press(pilot, app, "e", FieldsDialog)
        await _save_name(pilot, app, "Renamed")
        assert await wait_until(pilot, lambda: _saved(case)[1].name == "Renamed")
        assert _saved(case)[0].name == first

        await _choose_row(pilot, view, case, 0)
        await _press(pilot, app, "d", ConfirmScreen)  # no picker
        assert _confirm_message(app) == f"Delete {first}?"
        await pilot.press("n")
        assert await wait_until(pilot, lambda: app.screen is workspace)
        assert len(_saved(case)) == 2

        await _press(pilot, app, "e", FieldsDialog)  # no picker
        await _save_name(pilot, app, "Chosen")
        assert await wait_until(pilot, lambda: _saved(case)[0].name == "Chosen")
        assert _saved(case)[1].name == "Renamed"

        await _press(pilot, app, "d", ConfirmScreen)
        assert _confirm_message(app) == "Delete Chosen?"
        await pilot.press("y")
        assert await wait_until(pilot, lambda: len(_saved(case)) == 1)
        assert [entry.name for entry in _saved(case)] == ["Renamed"]
        assert await wait_until(pilot, lambda: "Chosen" not in str(rows._rows))

        await _press(pilot, app, "d", ConfirmScreen)
        assert _confirm_message(app) == "Delete Renamed?"


# -- Saga Content's own lists --


def _content_saga() -> Saga:
    """_saga() with two sources of its own and two hidden Abilities (listed
    by name: Animal Handling, then Athletics)."""
    saga = _saga()
    saga.sources = [SagaSource("HR", "House [rules]"), SagaSource("FS", "Fan")]
    saga.hidden_entries = {"abilities": ["ab_athletics", "ab_animal_handling"]}
    return saga


CONTENT_LISTS: dict[str, ListCase] = {
    "saga-sources": ListCase(
        ("saga_content",),
        "section-saga-sources",
        "content-sources-list",
        lambda s: [x.abbreviation for x in s.sources],
    ),
    "hidden-entries": ListCase(
        ("saga_content",),
        "section-hidden-entries",
        "content-hidden-list",
        lambda s: sorted(s.hidden_entries.get("abilities", [])),
    ),
}

#: What d asks about each list's second row, and what is left after Yes.
_CONTENT_DELETE = {
    "saga-sources": ("Delete FS?", ["HR"]),
    "hidden-entries": ("Offer Athletics again?", ["ab_animal_handling"]),
}


async def test_saga_source_edit_uses_the_chosen_row():
    case = CONTENT_LISTS["saga-sources"]
    storage.save_saga(_content_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        _, view = await _open(pilot, app, case)
        await _choose_row(pilot, view, case, 1)
        await _press(pilot, app, "e", FieldsDialog)  # no picker
        dialog = app.screen
        assert dialog.query_one("#fld-abbreviation", Input).value == "FS"
        dialog.query_one("#fld-abbreviation", Input).value = "FAN"
        dialog.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: _saved(case) == ["HR", "FAN"])


@pytest.mark.parametrize("name", list(CONTENT_LISTS))
async def test_saga_content_delete_uses_the_chosen_row_after_asking(name):
    case = CONTENT_LISTS[name]
    message, left = _CONTENT_DELETE[name]
    storage.save_saga(_content_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, case)
        await _choose_row(pilot, view, case, 1)
        await _press(pilot, app, "d", ConfirmScreen)  # no picker
        assert _confirm_message(app) == message
        await pilot.press("n")
        assert await wait_until(pilot, lambda: app.screen is workspace)
        assert len(_saved(case)) == 2
        await _press(pilot, app, "d", ConfirmScreen)
        await pilot.press("y")
        assert await wait_until(pilot, lambda: _saved(case) == left)


# -- A laboratory's Magic Items --


async def test_lab_magic_items_edit_and_delete_act_on_the_chosen_row():
    """e opens the chosen effect's first step, its effect filled in; d asks
    first, then removes only the chosen effect's benefit, keeping the
    device and the Magic Item Virtue the other still uses."""
    saga = _saga()
    lab = saga.laboratories[0]
    saga.enchanted_devices = [
        EnchantedDevice(
            id="wand",
            name="Wand",
            holder_kind="laboratory",
            holder_id="lab1",
            effects=[
                InstilledEffect(id="e1", name="Steady", level=20),
                InstilledEffect(id="e2", name="Spark", level=10),
            ],
        )
    ]
    lab.virtues_flaws = [
        VirtueFlawInstance("labvf_magic_item", {"device": "wand"}, id="host")
    ]
    lab.item_benefits = [
        LabItemBenefit(
            "b1",
            "wand",
            "e1",
            virtue_id="host",
            name="Wand",
            specializations=[LabSpecialtyGrant("Texts", 1)],
        ),
        LabItemBenefit(
            "b2",
            "wand",
            "e2",
            virtue_id="host",
            name="Wand",
            specializations=[LabSpecialtyGrant("Ignem", 1)],
        ),
    ]
    storage.save_saga(saga)
    case = ListCase(
        ("laboratory", "lab1"),
        "section-lab-magic-items",
        "lab-magic-items-list",
        lambda s: s.laboratories[0].item_benefits,
    )
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, case)

        await _choose_row(pilot, view, case, 1)
        await _press(pilot, app, "e", FieldsDialog)
        assert app.screen.query_one("#fld-effect", Select).value == "wand/e2"
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is workspace)

        await _press(pilot, app, "d", ConfirmScreen)
        assert _confirm_message(app).startswith("Remove what Wand gives")
        await pilot.press("y")
        assert await wait_until(pilot, lambda: len(_saved(case)) == 1)
        saved = storage.load_saga("test_saga")
        assert [b.id for b in saved.laboratories[0].item_benefits] == ["b1"]
        assert [vf.id for vf in saved.laboratories[0].virtues_flaws] == ["host"]
        assert [e.id for e in saved.enchanted_devices[0].effects] == ["e1", "e2"]


# -- Conflicts: fights and sieges --


def _conflicts_saga() -> Saga:
    saga = _saga()
    saga.fights = [
        Fight("Fray [ford]", sides=[FightSide("Ours"), FightSide("Theirs")]),
        Fight("Ambush", sides=[FightSide("Ours"), FightSide("Theirs")]),
    ]
    saga.sieges = [
        Siege("Siege [north]", castle="Burg A", besieger_walls=[1, 1, 1, 0]),
        Siege("Blockade", castle="Burg B"),
    ]
    saga.neighbours = [
        Neighbour(id="gottfried", name="Count Gottfried", kind="lord"),
        Neighbour(id="mark", name="Count of Mark", kind="lord"),
    ]
    saga.battles = [
        Battle(
            "Werl [ford]",
            sides=[
                BattleSide(neighbour_id="gottfried", groups=20),
                BattleSide(neighbour_id="mark", groups=10),
            ],
        ),
        Battle("Unna", sides=[BattleSide("Ours", groups=5), BattleSide("Theirs")]),
    ]
    return saga


CONFLICT_LISTS: dict[str, tuple[ListCase, str]] = {
    "battles": (
        ListCase(
            ("conflicts",),
            "section-conflict-battles",
            "conflict-battles-list",
            lambda s: s.battles,
        ),
        "Delete the battle Unna?",
    ),
    "fights": (
        ListCase(("conflicts",), "section-fights", "fights-list", lambda s: s.fights),
        "Delete the fight Ambush? Wounds it dealt stay on the characters' sheets.",
    ),
    "sieges": (
        ListCase(("conflicts",), "section-sieges", "sieges-list", lambda s: s.sieges),
        "Delete the siege Blockade?",
    ),
}


@pytest.mark.parametrize("name", list(CONFLICT_LISTS))
async def test_conflict_lists_act_on_the_chosen_row(name):
    """In one session: e edits the chosen battle, fight or siege, More
    plays the chosen one (Battle Event on a battle, Add Combatant on a
    fight, Next Siege Event on a siege), and d asks about the chosen one
    before deleting it."""
    case, message = CONFLICT_LISTS[name]
    storage.save_saga(_conflicts_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, case)
        await _choose_row(pilot, view, case, 1)
        await _press(pilot, app, "e", FieldsDialog)
        await _save_name(pilot, app, "Renamed")
        assert await wait_until(pilot, lambda: _saved(case)[1].name == "Renamed")
        assert _saved(case)[0].name.endswith("]")

        await _choose_row(pilot, view, case, 0)
        if name == "fights":
            await _press(pilot, app, "m", MenuScreen)
            await _press(pilot, app, "a", FieldsDialog)
            dialog = app.screen
            dialog.query_one("#fld-character", Select).value = "mag1|"
            await pilot.pause()
        else:  # its one More command runs straight away
            await _press(pilot, app, "m", FieldsDialog)
            dialog = app.screen
        dialog.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: app.screen is workspace)
        saved = storage.load_saga("test_saga")
        if name == "fights":
            assert [c.name for c in saved.fights[0].sides[0].combatants] == ["Leandro"]
            assert saved.fights[1].sides[0].combatants == []
        elif name == "battles":
            assert len(saved.battles[0].events) == 1
            assert saved.battles[1].events == []
        else:
            assert len(saved.sieges[0].events) == 1
            assert saved.sieges[1].events == []

        await _choose_row(pilot, view, case, 1)
        await _press(pilot, app, "d", ConfirmScreen)
        old = {"fights": "Ambush", "sieges": "Blockade", "battles": "Unna"}[name]
        assert _confirm_message(app) == message.replace(old, "Renamed")
        await pilot.press("y")
        assert await wait_until(pilot, lambda: len(_saved(case)) == 1)


LORD_BATTLES = ListCase(
    ("neighbour", "gottfried"),
    "section-nb-battles",
    "nb-battles-list",
    lambda s: battles.involving(s, s.neighbour("gottfried")),
)
LORD_SIEGES = ListCase(
    ("neighbour", "gottfried"),
    "section-nb-sieges",
    "nb-sieges-list",
    lambda s: sieges.involving(s, s.neighbour("gottfried")),
)


async def test_a_lords_fief_plays_his_battles_and_edits_his_sieges():
    """On a lord's Fief tab: Battle Event plays the chosen battle naming
    him (writing both lords' Diaries), and his Sieges list edits and
    deletes the chosen siege he lays or holds out in."""
    saga = _conflicts_saga()
    saga.sieges[0].besieger_id = "gottfried"
    saga.sieges[1].castle_id = "gottfried"
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, LORD_BATTLES)
        assert [b.name for b in _saved(LORD_BATTLES)] == ["Werl [ford]"]
        await pilot.press("m")
        if await wait_until(pilot, lambda: isinstance(app.screen, MenuScreen)):
            await _press(pilot, app, "b", FieldsDialog)
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        app.screen.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: app.screen is workspace)
        saved = storage.load_saga("test_saga")
        assert len(saved.battles[0].events) == 1
        for lord in ("gottfried", "mark"):
            assert place_events.diary(saved.neighbour(lord))[-1]["text"].startswith(
                "Werl [ford]:"
            )

        section_stop(view.query_one("#section-nb-sieges")).focus()
        assert await wait_until(
            pilot, lambda: workspace._active_section() == "section-nb-sieges"
        )
        await _choose_row(pilot, view, LORD_SIEGES, 1)
        await _press(pilot, app, "e", FieldsDialog)
        await _save_name(pilot, app, "Held out")
        assert await wait_until(
            pilot, lambda: [s.name for s in _saved(LORD_SIEGES)][1] == "Held out"
        )
        await _press(pilot, app, "d", ConfirmScreen)
        assert _confirm_message(app) == "Delete the siege Held out?"
        await pilot.press("y")
        assert await wait_until(pilot, lambda: len(_saved(LORD_SIEGES)) == 1)
