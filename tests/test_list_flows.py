"""End-to-end flows for the sheet lists that share one shape in
WorkspaceScreen: a adds, e edits and d deletes the chosen row. A list that
takes focus always has one (the first, until another is chosen), so nothing
asks "which one?". Every delete asks first."""

import copy
from dataclasses import dataclass
from typing import Any

import pytest
from support import build_all_tabs, wait_until
from textual.widgets import Input, Select, TabPane, TextArea, Tree

from ars_magica_manager import battles, place_events, sieges, storage
from ars_magica_manager import goods as gd
from ars_magica_manager import mystery_cults as cult_core
from ars_magica_manager.models import (
    Ability,
    AbilityDef,
    Agent,
    Argument,
    Battle,
    BattleSide,
    BondPower,
    Book,
    BoundBeing,
    Breakthrough,
    CanonCase,
    Character,
    CharacterPower,
    CharterClause,
    ConstantEffect,
    Covenant,
    CraftDevice,
    Creature,
    CreatureAttack,
    CreaturePower,
    CultDegree,
    CultScript,
    DiaryEntry,
    EnchantedDevice,
    Familiar,
    Fight,
    FightSide,
    GoodDef,
    HermeticProject,
    IncomeSource,
    Inhabitant,
    InstilledEffect,
    LabItemBenefit,
    Laboratory,
    LabSpecialtyGrant,
    Marriage,
    MysteryCult,
    NamedDescription,
    Neighbour,
    Petition,
    PolemicText,
    Possession,
    ProjectWork,
    Saga,
    SagaSource,
    ScoredTrait,
    Siege,
    Stigma,
    TraditionEffect,
    Tribunal,
    VirtueFlawInstance,
)
from ars_magica_manager.models.menagerie import Beast, Breeding
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
        # A covenant's ships.
        Possession(id="sh1", kind="ship", name="Möwe [old]"),
        Possession(id="sh2", kind="ship", name="Seehund"),
    ]
    # A covenant's Hermetic Projects: two projects, the first with two
    # works and two craft devices.
    covenant.hermetic_projects = [
        HermeticProject(
            id="hp1",
            name="Spire [old]",
            works=[
                ProjectWork(id="hw1", kind="other", name="Gale [great]"),
                ProjectWork(id="hw2", kind="other", name="Repair"),
            ],
            devices=[
                CraftDevice(id="hd1", name="Crane [big]"),
                CraftDevice(id="hd2", name="Glove"),
            ],
        ),
        HermeticProject(id="hp2", name="Keep"),
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
    magus.agents = [
        Agent("Udo [miller]", resistance=0, impressed=True, bond=1),
        Agent("Father Bertolf", status="minor_virtue"),
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
    "tribunal": "_tribunal_sheet_view",
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
    "character-agents": ListCase(
        ("character", "mag1"),
        "section-char-agents",
        "char-agents-list",
        lambda s: s.characters[0].agents,
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
    # A covenant's ships (Hermetic Projects; City & Guild).
    "covenant-ships": ListCase(
        ("covenant", "cov1"),
        "section-pos-ship",
        "pos-ship-list",
        lambda s: [p for p in s.covenants[0].possessions if p.kind == "ship"],
    ),
    # A covenant's Hermetic Projects, the shown one's works and devices.
    "covenant-projects": ListCase(
        ("covenant", "cov1"),
        "section-cov-projects",
        "cov-projects-list",
        lambda s: s.covenants[0].hermetic_projects,
    ),
    "covenant-project-works": ListCase(
        ("covenant", "cov1"),
        "section-cov-tower-works",
        "cov-tower-works-list",
        lambda s: s.covenants[0].hermetic_projects[0].works,
    ),
    "covenant-project-devices": ListCase(
        ("covenant", "cov1"),
        "section-cov-tower-devices",
        "cov-tower-devices-list",
        lambda s: s.covenants[0].hermetic_projects[0].devices,
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


# -- Saga Content's Goods --


async def test_goods_edit_and_delete_act_on_the_chosen_row():
    """In one session: e opens the chosen good of the saga's own, d deletes
    it after asking; on a catalog good d hides it instead, after asking."""
    saga = _saga()
    saga.custom_goods = [
        GoodDef(id="custom_good_amber", name="Amber [Baltic]"),
        GoodDef(id="custom_good_jet", name="Jet"),
    ]
    storage.save_saga(saga)
    case = ListCase(
        ("saga_content",),
        "section-content-goods",
        "content-goods-list",
        lambda s: [g.name for g in s.custom_goods],
    )
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, case)
        listed = [g.name for g in gd.listed(workspace.saga)]
        amber = listed.index("Amber [Baltic]")
        await _choose_row(pilot, view, case, amber)
        await _press(pilot, app, "e", FieldsDialog)
        assert app.screen.query_one("#fld-name", Input).value == "Amber [Baltic]"
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is workspace)
        await _press(pilot, app, "d", ConfirmScreen)
        assert _confirm_message(app) == "Delete Amber [Baltic]?"
        await pilot.press("y")
        assert await wait_until(pilot, lambda: _saved(case) == ["Jet"])

        await _choose_row(pilot, view, case, listed.index("Brassware"))
        await _press(pilot, app, "d", ConfirmScreen)
        assert _confirm_message(app).startswith("Hide Brassware?")
        await pilot.press("y")
        assert await wait_until(
            pilot,
            lambda: (
                storage.load_saga("test_saga").hidden_entries.get("goods")
                == ["good_brassware"]
            ),
        )
        rows = view.query_one(f"#{case.list_id}", SelectableList)
        assert await wait_until(pilot, lambda: "Brassware" not in str(rows._rows))


# -- A covenant's charter clauses --


async def test_clauses_edit_delete_and_break_act_on_the_chosen_row():
    """In one session, on clauses grouped under their charter sections (so
    the list's order isn't the charter's): e opens the chosen clause, m
    breaks it (More has one item there), and d deletes it after asking."""
    saga = _saga()
    saga.covenants[0].charter_of_covenant.clauses = [
        CharterClause("1", "All is shared.", 1200, "Spring", "Oath of Covenant"),
        CharterClause("Apprentices [old]", "None without leave.", 1201, "Summer"),
        CharterClause("2", "The council decides.", 1200, "Spring", "Membership"),
    ]
    storage.save_saga(saga)
    case = ListCase(
        ("covenant", "cov1"),
        "section-cov-clauses",
        "cov-clauses-list",
        lambda s: s.covenants[0].charter_of_covenant.clauses,
    )
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, case)
        rows = view.query_one(f"#{case.list_id}", SelectableList)
        # Oath of Covenant, Membership, then Other: headings between.
        assert [index for index, _ in rows._rows] == [None, 0, None, 2, None, 1]

        await _choose_row(pilot, view, case, 1)
        await _press(pilot, app, "e", FieldsDialog)
        assert app.screen.query_one("#fld-number", Input).value == "Apprentices [old]"
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is workspace)

        await _press(pilot, app, "m", FieldsDialog)
        assert "Apprentices [old]" in str(
            app.screen.query_one("#fields-title").render()
        )
        dialog = app.screen
        dialog.query_one("#fld-note", TextArea).text = "Taken in secret."
        dialog.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: _saved(case)[1].status == "Broken")
        assert _saved(case)[1].note == "Taken in secret."

        await _choose_row(pilot, view, case, 1)
        await _press(pilot, app, "d", ConfirmScreen)
        assert _confirm_message(app) == "Delete Apprentices [old]?"
        await pilot.press("y")
        assert await wait_until(pilot, lambda: len(_saved(case)) == 2)
        assert [c.number for c in _saved(case)] == ["1", "2"]


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


# -- A town's Charter, Guilds and Court --


def _town_saga() -> Saga:
    saga = _saga()
    companion = Character(id="comp1", name="Alys", type="companion")
    saga.characters.append(companion)
    saga.neighbours = [
        Neighbour(
            id="worms",
            name="Worms",
            kind="town",
            details={
                "charter_lords": [
                    {"lord": "Bishop [of Worms]", "kind": "Church"},
                    {"lord": "Count Palatine", "kind": "Noble"},
                ],
                "citizens": [
                    {"character_id": "mag1", "since_year": 1210},
                    {"character_id": "comp1", "since_year": 1219},
                ],
                "guilds": [{"trade": "Weavers"}],
                "guild_members": [
                    {"character_id": "mag1", "guild": "Weavers", "rank": "master"},
                    {"character_id": "comp1", "guild": "Weavers"},
                ],
                "court_cases": [
                    {"accused": "Hartmut [the Tanner]", "charge": "Theft"},
                    {"accused": "Agnes", "charge": "Slander"},
                ],
            },
        )
    ]
    return saga


#: Each town list: its case, the field e changes and the value typed, the
#: key it is saved under, and what d asks about the second row.
TOWN_LISTS: dict[str, tuple[ListCase, str, str, str, str]] = {
    "charter-lords": (
        ListCase(
            ("neighbour", "worms"),
            "section-nb-charter-lords",
            "nb-charter-lords-list",
            lambda s: s.neighbour("worms").details["charter_lords"],
        ),
        "lord",
        "Count of Leiningen",
        "lord",
        "Delete Count of Leiningen?",
    ),
    "citizens": (
        ListCase(
            ("neighbour", "worms"),
            "section-nb-citizens",
            "nb-citizens-list",
            lambda s: s.neighbour("worms").details["citizens"],
        ),
        "note",
        "Swore the oath",
        "note",
        "Delete Alys?",
    ),
    "guild-members": (
        ListCase(
            ("neighbour", "worms"),
            "section-nb-guild-members",
            "nb-guild-members-list",
            lambda s: s.neighbour("worms").details["guild_members"],
        ),
        "note",
        "His father's trade",
        "note",
        "Delete Alys?",
    ),
    "court-cases": (
        ListCase(
            ("neighbour", "worms"),
            "section-nb-court-cases",
            "nb-court-cases-list",
            lambda s: s.neighbour("worms").details["court_cases"],
        ),
        "charge",
        "Slander of an alderman",
        "charge",
        "Delete Agnes?",
    ),
}


@pytest.mark.parametrize("name", list(TOWN_LISTS))
async def test_a_towns_lists_act_on_the_chosen_row(name):
    """In one session on a town's tab: e edits the chosen row, d asks
    about the chosen row before deleting it; on the Court tab More's Court
    Roll decides the chosen case."""
    case, field, typed, key, message = TOWN_LISTS[name]
    storage.save_saga(_town_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, case)
        await _choose_row(pilot, view, case, 1)
        await _press(pilot, app, "e", FieldsDialog)
        dialog = app.screen
        dialog.query_one(f"#fld-{field}", Input).value = typed
        dialog.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: _saved(case)[1].get(key) == typed)
        assert _saved(case)[0].get(key) != typed

        if name == "court-cases":
            await _choose_row(pilot, view, case, 0)
            await _press(pilot, app, "m", FieldsDialog)  # its one More command
            app.screen.query_one("#btn-save").press()
            assert await wait_until(pilot, lambda: bool(_saved(case)[0].get("verdict")))
            assert not _saved(case)[1].get("verdict")
            while app.screen is not workspace:  # the roll's notes
                await pilot.press("escape")
                await pilot.pause()

        await _choose_row(pilot, view, case, 1)
        await _press(pilot, app, "d", ConfirmScreen)
        assert _confirm_message(app) == message
        await pilot.press("y")
        assert await wait_until(pilot, lambda: len(_saved(case)) == 1)


# -- The Manors tab of a lord and of a covenant --


def _manors_saga() -> Saga:
    saga = _saga()
    held = {
        "manor_list": [
            {"name": "Katzenelnbogen [castle]", "acres": 640, "waste": 60},
            {"name": "Hohenstein", "acres": 480, "waste": 80},
        ],
        "establishments": [
            {"kind": "Stables", "quality": "Excellent", "animals": 26},
            {"kind": "Mews", "quality": "Superior", "animals": 7},
        ],
    }
    saga.neighbours = [
        Neighbour(
            id="dieter",
            name="Count Dieter",
            kind="lord",
            details={"title": "count", **copy.deepcopy(held)},
        )
    ]
    saga.covenants[0].manors = copy.deepcopy(held)
    return saga


#: Each Manors list: its case, the field e changes and the value typed,
#: the More command (its letter) on the first row and what it changes,
#: and what d asks about the second row.
MANOR_LISTS: dict[str, tuple[ListCase, str, str, str, Any, str]] = {
    "lord-manors": (
        ListCase(
            ("neighbour", "dieter"),
            "section-manors",
            "manors-list",
            lambda s: s.neighbour("dieter").details["manor_list"],
        ),
        "note",
        "The castle's own manor",
        "s",
        lambda rows: rows[0]["waste"] == 59,
        "Delete Hohenstein?",
    ),
    "lord-establishments": (
        ListCase(
            ("neighbour", "dieter"),
            "section-establishments",
            "establishments-list",
            lambda s: s.neighbour("dieter").details["establishments"],
        ),
        "note",
        "Ulrich's",
        "w",
        lambda rows: "die" in rows[0].get("roll", "") and not rows[1].get("roll"),
        "Delete Mews?",
    ),
    "covenant-manors": (
        ListCase(
            ("covenant", "cov1"),
            "section-manors",
            "manors-list",
            lambda s: s.covenants[0].manors["manor_list"],
        ),
        "note",
        "An allod",
        "s",
        lambda rows: rows[0]["waste"] == 59,
        "Delete Hohenstein?",
    ),
}


@pytest.mark.parametrize("name", list(MANOR_LISTS))
async def test_the_manors_lists_act_on_the_chosen_row(name):
    """In one session on a Manors tab: e edits the chosen row, More's
    Assart or Winter Roll acts on the chosen row, and d asks about the
    chosen row before deleting it."""
    case, field, typed, letter, changed, message = MANOR_LISTS[name]
    storage.save_saga(_manors_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, case)
        await _choose_row(pilot, view, case, 1)
        await _press(pilot, app, "e", FieldsDialog)
        dialog = app.screen
        dialog.query_one(f"#fld-{field}", Input).value = typed
        dialog.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: _saved(case)[1].get(field) == typed)
        assert _saved(case)[0].get(field) != typed

        await _choose_row(pilot, view, case, 0)
        await pilot.press("m")  # a menu, or its one More command at once
        if await wait_until(pilot, lambda: isinstance(app.screen, MenuScreen)):
            await _press(pilot, app, letter, FieldsDialog)
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        app.screen.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: changed(_saved(case)))
        while app.screen is not workspace:  # the command's notes
            await pilot.press("escape")
            await pilot.pause()

        await _choose_row(pilot, view, case, 1)
        await _press(pilot, app, "d", ConfirmScreen)
        assert _confirm_message(app) == message
        await pilot.press("y")
        assert await wait_until(pilot, lambda: len(_saved(case)) == 1)


# -- A place's Tomb tab (Lands of the Nile) --


def _tomb_saga() -> Saga:
    saga = _saga()
    saga.neighbours = [
        Neighbour(
            id="grave",
            name="The Giant's Grave",
            kind="place",
            details={
                "tomb": True,
                "tomb_curses": [
                    {"name": "Fear [of the King]", "kind": "Hermetic effect"}
                    | {"art": "CrMe", "level": 25, "condition": "By night"},
                    {"name": "Lost", "kind": "Lesser Malediction"}
                    | {"art": "CrMe", "level": 25, "condition": "The capstone"},
                ],
                "tomb_wards": [
                    {"name": "Boar [bronze]", "kind": "Talisman", "level": 40},
                    {"name": "Turn", "kind": "Ward", "level": 30},
                ],
                "tomb_traps": [
                    {"name": "Drop [stone]", "harm": "fatal", "ease": 12},
                    {"name": "Maze", "harm": "scare", "ease": 6},
                ],
            },
        )
    ]
    return saga


def _tomb_case(section: str, key: str) -> ListCase:
    return ListCase(
        ("neighbour", "grave"),
        f"section-nb-tomb-{section}",
        f"nb-tomb-{section}-list",
        lambda s: s.neighbour("grave").details[key],
    )


TOMB_LISTS: dict[str, ListCase] = {
    "tomb-curses": _tomb_case("curses", "tomb_curses"),
    "tomb-wards": _tomb_case("wards", "tomb_wards"),
    "tomb-traps": _tomb_case("traps", "tomb_traps"),
}


@pytest.mark.parametrize("name", list(TOMB_LISTS))
async def test_a_tombs_lists_act_on_the_chosen_row(name):
    """In one session on a place's Tomb tab: e edits the chosen row, d
    asks about the chosen row before deleting it; on Traps, More's
    Overcome It rolls for the chosen trap and Write puts it in the place's
    diary."""
    case = TOMB_LISTS[name]
    storage.save_saga(_tomb_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, case)
        await _choose_row(pilot, view, case, 1)
        await _press(pilot, app, "e", FieldsDialog)
        await _save_name(pilot, app, "Renamed")
        assert await wait_until(pilot, lambda: _saved(case)[1]["name"] == "Renamed")
        assert _saved(case)[0]["name"] != "Renamed"

        if name == "tomb-traps":
            await _choose_row(pilot, view, case, 0)
            await pilot.press("m")  # a menu, or its one More command at once
            if await wait_until(pilot, lambda: isinstance(app.screen, MenuScreen)):
                await _press(pilot, app, "o", FieldsDialog)
            assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
            assert "Drop [stone]" in str(app.screen.query_one("#fields-live").render())
            app.screen.query_one("#btn-save").press()
            await _confirm_write(pilot, app)

            def diary() -> list:
                return (
                    storage.load_saga("test_saga")
                    .neighbour("grave")
                    .details.get("diary", [])
                )

            assert await wait_until(pilot, lambda: len(diary()) == 1)
            assert "Drop [stone]" in diary()[0]["text"]
            assert await wait_until(pilot, lambda: app.screen is workspace)

        await _choose_row(pilot, view, case, 1)
        await _press(pilot, app, "d", ConfirmScreen)
        assert _confirm_message(app) == "Delete Renamed?"
        await pilot.press("y")
        assert await wait_until(pilot, lambda: len(_saved(case)) == 1)


async def _confirm_write(pilot, app) -> None:
    """Answer Write on the roll's question."""
    assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
    await pilot.press("y")


# -- A saga's own Abilities in House Rules (HoH:S pp. 103-106) --


async def test_house_rule_abilities_edit_and_delete_act_on_the_chosen_row():
    """In one session: e opens the chosen Ability of the saga's own, d
    refuses one a character holds, and deletes another after asking."""
    saga = _saga()
    saga.custom_abilities = [
        AbilityDef("custom_ability_tide", "Call the Tide [sea]", "Supernatural"),
        AbilityDef("custom_ability_ravens", "Speak with Ravens", "Supernatural"),
    ]
    saga.characters[0].abilities.append(
        Ability("Call the Tide [sea]", "Supernatural", xp=5)
    )
    storage.save_saga(saga)
    case = ListCase(
        ("saga_content",),
        "section-house-rules",
        "house-rules-list",
        lambda s: [a.name for a in s.custom_abilities],
    )
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, case)
        await _press(pilot, app, "e", FieldsDialog)  # no picker
        assert app.screen.query_one("#fld-name", Input).value == "Call the Tide [sea]"
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is workspace)
        # Held by a character: refused, nothing asked.
        await pilot.press("d")
        await pilot.pause()
        assert app.screen is workspace
        assert len(_saved(case)) == 2
        await _choose_row(pilot, view, case, 1)
        await _press(pilot, app, "d", ConfirmScreen)
        assert _confirm_message(app) == "Delete Speak with Ravens?"
        await pilot.press("y")
        assert await wait_until(pilot, lambda: _saved(case) == ["Call the Tide [sea]"])


# -- The Rhine's Great Library at Durenmar (Guardians of the Forests) --


def _library_saga() -> Saga:
    """The flows' saga with a Rhine Tribunal: Leandro and Ricardus hold
    credit at the Great Library, and Leandro has made two searches."""
    saga = _saga()
    saga.characters.append(
        Character(id="ric", name="Ricardus [glass]", type="magus", covenant_id="cov1")
    )
    saga.covenants[0].tribunal_id = "rhine"
    ledger = {"given": [{"kind": "book", "what": "A tract", "seasons": 2}], "used": 0}
    search = {"year": 1220, "season": "Spring", "magus_id": "mag1", "roll": "Q 7"}
    saga.tribunals = [
        Tribunal(
            id="rhine",
            name="Rhine",
            package="rhine",
            package_data={
                "rhine": {
                    "library_credit": [
                        {"magus_id": "mag1", **ledger},
                        {"magus_id": "ric", **ledger},
                    ],
                    "library_searches": [
                        {**search, "sought": "tractatus", "subject": "Vim"},
                        {**search, "sought": "tractatus", "subject": "Ignem"},
                    ],
                }
            },
        )
    ]
    return saga


def _library_case(section: str, key: str) -> ListCase:
    return ListCase(
        ("tribunal", "rhine"),
        f"section-trib-library-{section}",
        f"trib-library-{section}-list",
        lambda s: s.tribunal("rhine").package_data["rhine"][key],
    )


LIBRARY_LISTS: dict[str, ListCase] = {
    "library-credit": _library_case("credit", "library_credit"),
    "library-searches": _library_case("searches", "library_searches"),
}


@pytest.mark.parametrize("name", list(LIBRARY_LISTS))
async def test_the_great_librarys_lists_act_on_the_chosen_row(name):
    """In one session on the Rhine's Great Library tab: e edits the chosen
    row (a magus's credit, or a search as recorded), and d asks about the
    chosen row before deleting it."""
    case = LIBRARY_LISTS[name]
    storage.save_saga(_library_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, case)
        await _choose_row(pilot, view, case, 1)
        await _press(pilot, app, "e", FieldsDialog)
        if name == "library-credit":
            app.screen.query_one("#fld-used", Input).value = "2"
        else:
            app.screen.query_one("#fld-subject", Input).value = "Creo"
        app.screen.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: app.screen is workspace)

        def changed() -> bool:
            second, first = _saved(case)[1], _saved(case)[0]
            if name == "library-credit":
                return second["used"] == 2 and first["used"] == 0
            return second["subject"] == "Creo" and first["subject"] == "Vim"

        assert await wait_until(pilot, changed)
        await _choose_row(pilot, view, case, 1)
        await _press(pilot, app, "d", ConfirmScreen)
        expected = (
            "Ricardus [glass]'s credit"
            if name == "library-credit"
            else "the search for Creo tractatus"
        )
        assert expected in _confirm_message(app)
        await pilot.press("y")
        assert await wait_until(pilot, lambda: len(_saved(case)) == 1)
        if name == "library-searches":
            # More on the rule of access: Search the Great Library.
            view.query_one("#section-trib-library", SheetSection).focus_section()
            await pilot.pause()
            await pilot.press("m")
            if await wait_until(pilot, lambda: isinstance(app.screen, MenuScreen)):
                await _press(pilot, app, "s", FieldsDialog)
            assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
            assert "The Stacks" in str(
                app.screen.query_one("#fields-live").border_title
            )


# -- A cleric's career: the Church tab's Petitions and Canon Court --

CHURCH_LISTS: dict[str, tuple[ListCase, str, list[str]]] = {
    "petitions": (
        ListCase(
            ("character", "mag1"),
            "section-char-petitions",
            "char-petitions-list",
            lambda s: s.characters[0].church.petitions,
        ),
        "ask",
        ["Leave to read [crypt]", "A blessing"],
    ),
    "canon-cases": (
        ListCase(
            ("character", "mag1"),
            "section-char-canon",
            "char-canon-list",
            lambda s: s.characters[0].church.cases,
        ),
        "what",
        ["Tithes", "Slander"],
    ),
}


def _church_saga() -> Saga:
    saga = _saga()
    church = saga.characters[0].church
    church.petitions = [
        Petition("Leave to read [crypt]", "Access to the parish crypt or library", 6),
        Petition("A blessing", "A marriage blessing", 3),
    ]
    church.cases = [CanonCase("Tithes"), CanonCase("Slander")]
    return saga


@pytest.mark.parametrize("name", list(CHURCH_LISTS))
async def test_church_lists_edit_and_delete_act_on_the_chosen_row(name):
    """In one session, on the Church tab a petition or a case brings: e
    opens the chosen row's form and saves into it, and d asks first, then
    deletes only the chosen row."""
    case, key, names = CHURCH_LISTS[name]
    storage.save_saga(_church_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        _, view = await _open(pilot, app, case)

        await _choose_row(pilot, view, case, 1)
        await _press(pilot, app, "e", FieldsDialog)
        dialog = app.screen
        dialog.query_one(f"#fld-{key}", Input).value = "Changed"
        dialog.query_one("#btn-save").press()
        assert await wait_until(
            pilot, lambda: getattr(_saved(case)[1], key) == "Changed"
        )

        await _choose_row(pilot, view, case, 0)
        await _press(pilot, app, "d", ConfirmScreen)
        assert _confirm_message(app) == f"Delete {names[0]}?"
        await pilot.press("y")
        assert await wait_until(pilot, lambda: len(_saved(case)) == 1)
        assert getattr(_saved(case)[0], key) == "Changed"


# -- Saga Content's Mystery Cults --


def _cults_saga() -> Saga:
    """_saga() with two cults of its own, the second with three degrees, its
    first degree's Script of two components."""
    saga = _saga()
    script = CultScript(
        "Rite [old]",
        [cult_core.component("place"), cult_core.component("quest", note="A gown")],
    )
    # A Mystagogue who may lead its Initiations.
    saga.characters[0].abilities.append(Ability("Second Lore", xp=75))
    saga.custom_cults = [
        MysteryCult("custom_cult_a", "First Cult", "First Lore"),
        MysteryCult(
            "custom_cult_b",
            "Second [Cult]",
            "Second Lore",
            degrees=[
                CultDegree("degree_1", "Spinner", "vf_second_sight", script=script),
                CultDegree("degree_2", "Weaver", "vf_clear_thinker"),
                CultDegree("degree_3", "Reader", "vf_strong_willed"),
            ],
        ),
    ]
    return saga


async def test_mystery_cults_lists_act_on_the_chosen_rows():
    """In one session: the degrees follow the chosen cult; e and d on the
    degrees act on the chosen degree; the Script follows the chosen degree,
    and d removes its chosen component after asking; More offers
    Experiment on a Script only for a degree with no Script."""
    storage.save_saga(_cults_saga())
    cults = ListCase(
        ("saga_content",),
        "section-content-cults",
        "content-cults-list",
        lambda s: [c.name for c in s.custom_cults],
    )
    degrees = ListCase(
        ("saga_content",),
        "section-content-cult-degrees",
        "content-cult-degrees-list",
        lambda s: [d.name for d in s.custom_cults[1].degrees],
    )
    script = ListCase(
        ("saga_content",),
        "section-content-cult-scripts",
        "content-cult-scripts-list",
        lambda s: [c.key for c in s.custom_cults[1].degrees[0].script.components],
    )
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, cults)
        await _choose_row(pilot, view, cults, 1)
        degree_rows = view.query_one(f"#{degrees.list_id}", SelectableList)
        assert await wait_until(pilot, lambda: "Weaver" in str(degree_rows._rows))

        await _choose_row(pilot, view, degrees, 1)
        await _press(pilot, app, "e", FieldsDialog)
        assert app.screen.query_one("#fld-name", Input).value == "Weaver"
        app.screen.query_one("#fld-name", Input).value = "Weaver [new]"
        app.screen.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: _saved(degrees)[1] == "Weaver [new]")

        await _choose_row(pilot, view, degrees, 2)
        # More has one item there: m opens it.
        await _press(pilot, app, "m", FieldsDialog)
        assert "Experiment on a Script: Reader" in str(
            app.screen.query_one("#fields-title").render()
        )
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is workspace)
        await _press(pilot, app, "d", ConfirmScreen)
        assert _confirm_message(app) == "Delete the degree Reader and its Script?"
        await pilot.press("y")
        assert await wait_until(
            pilot, lambda: _saved(degrees) == ["Spinner", "Weaver [new]"]
        )

        await _choose_row(pilot, view, degrees, 0)
        script_rows = view.query_one(f"#{script.list_id}", SelectableList)
        assert await wait_until(pilot, lambda: "A gown" in str(script_rows._rows))
        await _choose_row(pilot, view, script, 1)
        await _press(pilot, app, "d", ConfirmScreen)
        assert _confirm_message(app) == "Delete A gown from the Script?"
        await pilot.press("y")
        assert await wait_until(pilot, lambda: _saved(script) == ["place"])
        await _choose_row(pilot, view, script, 0)
        await _press(pilot, app, "e", FieldsDialog)
        assert app.screen.query_one("#fld-name", Input).value == "Rite [old]"


# -- Fleet battles (Tales of Power): a Battle at sea with the covenant's ships --


async def test_battle_event_at_sea_acts_on_the_chosen_fleet_battle():
    """More's Battle Event on the chosen battle, fought at sea with the
    Keep's two ships: the ships engaged go on that battle's event alone."""
    saga = _conflicts_saga()
    saga.battles[1].at_sea = True
    saga.battles[1].sides[0].covenant_id = "cov1"
    saga.battles[1].sides[0].ships = ["sh1", "sh2"]
    saga.battles[1].sides[1].other_ships = 2
    storage.save_saga(saga)
    case = CONFLICT_LISTS["battles"][0]
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, case)
        await _choose_row(pilot, view, case, 1)
        await _press(pilot, app, "m", FieldsDialog)
        dialog = app.screen
        assert "at sea" in str(dialog.query_one("#fields-title").render())
        dialog.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: app.screen is workspace)
        saved = storage.load_saga("test_saga")
        assert saved.battles[0].events == []
        [event] = saved.battles[1].events
        assert (event.deed, event.engaged_ships, event.engaged_other) == (
            "cut",
            ["sh1", "sh2"],
            [0, 2],
        )


# -- A covenant's Menagerie (Hermetic Projects): its beasts and breedings --


async def test_menagerie_lists_act_on_the_chosen_rows():
    """In one session, with a Menagerie shown: e edits the chosen beast, m
    Tames the chosen beast, d deletes it after asking; e and d on the
    chosen breeding likewise."""
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.hermetic_projects.insert(
        0,
        HermeticProject(
            id="men1",
            name="Zoo",
            kind="Menagerie",
            beasts=[
                Beast(id="be1", name="Bock [old]", sex="male", might=10),
                Beast(id="be2", name="Geiß", might=10),
            ],
            breedings=[
                Breeding(id="br1", pair="Bock × Geiß [1]"),
                Breeding(id="br2", pair="Bock × Geiß [2]"),
            ],
        ),
    )
    covenant.project_shown = "men1"
    storage.save_saga(saga)
    beasts = ListCase(
        ("covenant", "cov1"),
        "section-cov-menagerie-beasts",
        "cov-menagerie-beasts-list",
        lambda s: s.covenants[0].hermetic_projects[0].beasts,
    )
    breedings = ListCase(
        ("covenant", "cov1"),
        "section-cov-menagerie-breedings",
        "cov-menagerie-breedings-list",
        lambda s: s.covenants[0].hermetic_projects[0].breedings,
    )
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, beasts)
        await _choose_row(pilot, view, beasts, 1)
        await _press(pilot, app, "e", FieldsDialog)
        await _save_name(pilot, app, "Geiss")
        assert await wait_until(pilot, lambda: _saved(beasts)[1].name == "Geiss")
        await _press(pilot, app, "m", FieldsDialog)
        assert "Geiss" in str(app.screen.query_one("#fields-title").render())
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is workspace)
        await _choose_row(pilot, view, beasts, 0)
        await _press(pilot, app, "d", ConfirmScreen)
        assert _confirm_message(app) == "Delete Bock [old]?"
        await pilot.press("y")
        assert await wait_until(pilot, lambda: len(_saved(beasts)) == 1)

        view.query_one(f"#{breedings.list_id}").focus()
        await _choose_row(pilot, view, breedings, 1)
        await _press(pilot, app, "e", FieldsDialog)
        assert app.screen.query_one("#fld-pair", Input).value == "Bock × Geiß [2]"
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is workspace)
        await _press(pilot, app, "d", ConfirmScreen)
        assert _confirm_message(app) == "Delete the breeding of Bock × Geiß [2]?"
        await pilot.press("y")
        assert await wait_until(
            pilot, lambda: [b.id for b in _saved(breedings)] == ["br1"]
        )


# -- A lord's Marriages tab (Lords of Men pp. 10-11) --


async def test_a_lords_marriages_act_on_the_chosen_row():
    """In one session on a lord's Marriages tab: e edits the chosen
    marriage, More's End a Marriage ends the chosen one (and only it), and
    d asks about the chosen one before deleting it."""
    saga = _saga()
    saga.neighbours = [Neighbour(id="dieter", name="Count Dieter", kind="lord")]
    saga.marriages = [
        Marriage(groom_ref="neighbour:dieter", bride="Adelheid [of Sayn]"),
        Marriage(bride="Kunigunde", groom="Otto", bride_house="dieter"),
    ]
    storage.save_saga(saga)
    case = ListCase(
        ("neighbour", "dieter"),
        "section-nb-marriages",
        "nb-marriages-list",
        lambda s: s.marriages,
    )
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, case)
        await _choose_row(pilot, view, case, 1)
        await _press(pilot, app, "e", FieldsDialog)
        dialog = app.screen
        dialog.query_one("#fld-note", Input).value = "A love match"
        dialog.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: _saved(case)[1].note == "A love match")
        assert _saved(case)[0].note == ""

        await _choose_row(pilot, view, case, 0)
        await pilot.press("m")  # a menu, or its one More command at once
        if await wait_until(pilot, lambda: isinstance(app.screen, MenuScreen)):
            await _press(pilot, app, "x", FieldsDialog)
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        app.screen.query_one("#fld-how", Select).value = "part"
        await pilot.pause()
        app.screen.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: _saved(case)[0].ended == "part")
        assert _saved(case)[1].ended == ""
        while app.screen is not workspace:  # the command's notes
            await pilot.press("escape")
            await pilot.pause()

        await _choose_row(pilot, view, case, 1)
        await _press(pilot, app, "d", ConfirmScreen)
        assert _confirm_message(app) == "Delete the marriage of Kunigunde and Otto?"
        await pilot.press("y")
        assert await wait_until(pilot, lambda: len(_saved(case)) == 1)


# -- A Criamon magus's The Enigma tab (HoH:MC pp. 50-73) --


async def test_the_enigmas_stigmata_act_on_the_chosen_row():
    """In one session on The Enigma: choosing a station shows it in the
    panel; e edits the chosen stigma, d asks about the chosen one before
    deleting it; More on the path offers Follow an Avenue."""
    saga = _saga()
    magus = saga.characters[0]
    magus.hermetic.house = "house_criamon"
    magus.virtues_flaws += [
        VirtueFlawInstance("vf_the_enigma"),
        VirtueFlawInstance("vf_station_of_differentiation_of_seeming"),
    ]
    magus.abilities.append(Ability("Mystery Cult Lore: Criamon", xp=50))
    magus.enigma.stigmata = [
        Stigma("Temples", "Rings [open] eyes", "riddle"),
        Stigma("Wrists", "A loop", "twilight"),
    ]
    storage.save_saga(saga)
    case = ListCase(
        ("character", magus.id),
        "section-char-stigmata",
        "char-stigmata-list",
        lambda s: s.characters[0].enigma.stigmata,
    )
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, case)
        stations = ListCase(
            case.node,
            "section-char-criamon-stations",
            "char-criamon-stations-list",
            case.entries,
        )
        await _choose_row(pilot, view, stations, 1)
        assert await wait_until(
            pilot,
            lambda: "True Sight" in str(view.query_one("#criamon-info").render()),
        )

        await _choose_row(pilot, view, case, 1)
        await _press(pilot, app, "e", FieldsDialog)
        dialog = app.screen
        dialog.query_one("#fld-where", Input).value = "Forearms"
        dialog.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: _saved(case)[1].where == "Forearms")
        assert _saved(case)[0].where == "Temples"

        await _choose_row(pilot, view, case, 0)
        await _press(pilot, app, "d", ConfirmScreen)
        assert _confirm_message(app) == "Delete the stigma Rings [open] eyes?"
        await pilot.press("y")
        assert await wait_until(pilot, lambda: len(_saved(case)) == 1)

        view.query_one("#section-char-criamon-path", SheetSection).focus_section()
        await pilot.pause()
        await pilot.press("m")
        if await wait_until(pilot, lambda: isinstance(app.screen, MenuScreen)):
            await _press(pilot, app, "v", FieldsDialog)
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        assert "The Avenue" in str(app.screen.query_one("#fields-live").border_title)
        assert workspace is not None


# -- A Tribunal's Arguments tab (Transforming Mythic Europe pp. 27-35) --


async def test_a_tribunals_arguments_act_on_the_chosen_row():
    """In one session on the Arguments tab: choosing an argument shows its
    texts; e edits the chosen argument and the chosen text; d asks about
    the chosen text before deleting it (and only it); More on the texts
    offers Circulate a Text on the chosen one."""
    saga = _saga()
    saga.books += [
        Book(
            id="pol",
            name="On Charters",
            type="Ability Summa",
            ability="Code of Hermes",
            level=4,
            quality=11,
        ),
        Book(
            id="dia",
            name="Against [them]",
            type="Tractatus",
            ability="Code of Hermes",
            quality=9,
        ),
    ]
    saga.tribunals = [
        Tribunal(
            id="rhine",
            name="Rhine",
            arguments=[
                Argument(
                    "Charters [for]",
                    texts=[
                        PolemicText(book_id="pol", circulated=True),
                        PolemicText(kind="diatribe", book_id="dia", studied=True),
                    ],
                ),
                Argument("The silk pact", reach="covenant"),
            ],
        )
    ]
    storage.save_saga(saga)
    arguments = ListCase(
        ("tribunal", "rhine"),
        "section-trib-arguments",
        "trib-arguments",
        lambda s: s.tribunals[0].arguments,
    )
    texts = ListCase(
        ("tribunal", "rhine"),
        "section-trib-argument-texts",
        "trib-argument-texts",
        lambda s: s.tribunals[0].arguments[0].texts,
    )
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, arguments)
        await _choose_row(pilot, view, arguments, 1)
        assert await wait_until(
            pilot, lambda: "No text yet" in _list_text(view, texts.list_id)
        )
        await _press(pilot, app, "e", FieldsDialog)
        assert app.screen.query_one("#fld-topic", Input).value == "The silk pact"
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is workspace)

        await _choose_row(pilot, view, arguments, 0)
        assert await wait_until(
            pilot, lambda: "Tractatus" in _list_text(view, texts.list_id)
        )
        await _choose_row(pilot, view, texts, 1)
        await _press(pilot, app, "e", FieldsDialog)
        assert app.screen.query_one("#fld-book_id", Select).value == "dia"
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is workspace)

        await pilot.press("m")  # a menu, or its one More command at once
        if await wait_until(pilot, lambda: isinstance(app.screen, MenuScreen)):
            await _press(pilot, app, "c", FieldsDialog)
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is workspace)

        await _choose_row(pilot, view, texts, 1)
        await _press(pilot, app, "d", ConfirmScreen)
        assert _confirm_message(app).startswith(
            "Delete the diatribe Tractatus, Code of Hermes Q9?"
        )
        await pilot.press("y")
        assert await wait_until(
            pilot, lambda: [t.book_id for t in _saved(texts)] == ["pol"]
        )


def _list_text(view, list_id: str) -> str:
    rows = view.query_one(f"#{list_id}", SelectableList)
    return " ".join(str(markup) for _index, markup in rows._rows)
