import re

import pytest
from textual.app import App
from textual.widgets import (
    Button,
    Checkbox,
    Collapsible,
    Input,
    Label,
    ListView,
    OptionList,
    Select,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
    Tree,
)

from ars_magica_manager import inhabitants as inh
from ars_magica_manager import possessions as pos
from ars_magica_manager import storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import (
    FORMS,
    TECHNIQUES,
    Ability,
    ArtScore,
    Background,
    Book,
    Character,
    Characteristics,
    Covenant,
    DiaryEntry,
    HermeticBackground,
    Inhabitant,
    LabCharacteristics,
    Laboratory,
    Library,
    NamedDescription,
    Possession,
    Saga,
    ScoredTrait,
    Spell,
    VirtueFlawInstance,
)
from ars_magica_manager.screens import (
    AbilityDetailsScreen,
    AbilityPickerScreen,
    AdvanceSeasonScreen,
    BoonHookDetailScreen,
    CharacterCreateScreen,
    ConfirmScreen,
    CovenantBoonHookPickerScreen,
    CovenantCreateScreen,
    DiaryEntryPromptScreen,
    EditAgingScreen,
    EditArtsScreen,
    EditBackgroundScreen,
    EditCharacteristicsScreen,
    EditCovenantDescriptionScreen,
    EditCovenantScreen,
    EditDescriptionScreen,
    EditFatigueScreen,
    EditHermeticBackgroundScreen,
    EditLabCharacteristicsScreen,
    EditLabIdentityScreen,
    EditWoundsScreen,
    FieldsDialog,
    IdentityEditScreen,
    ItemAddScreen,
    LaboratoryCreateScreen,
    LabVirtueFlawPickerScreen,
    NamedDescriptionPromptScreen,
    ParamPromptScreen,
    RawVisPromptScreen,
    RemovalPickerScreen,
    SagaCreateScreen,
    SagaPickerScreen,
    ScoredTraitPromptScreen,
    SelectableList,
    SetDateScreen,
    SpellPickerScreen,
    VirtueFlawPickerScreen,
    WorkspaceScreen,
)


@pytest.fixture(autouse=True)
def isolated_sagas_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "SAGAS_DIR", tmp_path)


def _find_node(tree, data):
    """Walk a Tree looking for the node whose `.data` matches, by value."""

    def walk(node):
        if node.data == data:
            return node
        for child in node.children:
            found = walk(child)
            if found is not None:
                return found
        return None

    return walk(tree.root)


async def _wait_until(
    pilot, condition, timeout: float = 2.0, interval: float = 0.02
) -> None:
    """Poll `condition()` until it's truthy or `timeout` seconds pass.

    A bare `pilot.pause()` (wait-for-idle) has occasionally not been
    enough for a heavy sheet view to finish mounting under load (see
    HANDOFF.md's Lessons Learned) -- a single fixed extra delay
    (`pilot.pause(0.05)`) helped but wasn't fully reliable either. Polling
    for the actual condition, rather than guessing a delay, is the more
    robust fix: fast when mounting is quick, still correct under load.
    """
    elapsed = 0.0
    while not condition() and elapsed < timeout:
        await pilot.pause(interval)
        elapsed += interval


#: Selecting one of these tree-node kinds mounts a heavy sheet view
#: (CharacterSheetView / LaboratorySheetView) asynchronously -- _select()
#: waits for the matching WorkspaceScreen attribute to be set, rather than
#: just the tree's own NodeSelected handling, to avoid the flakiness above.
#: Keyed by kind -> the attribute name on WorkspaceScreen.
_SHEET_VIEW_ATTR: dict[str, str] = {
    "character": "_character_sheet_view",
    "laboratory": "_laboratory_sheet_view",
    "covenant": "_covenant_sheet_view",
}


async def _select(pilot, app, data) -> None:
    """Select a nav-tree node by its `.data`, the same way a click/enter would."""
    tree = app.screen.query_one("#nav-tree", Tree)
    node = _find_node(tree, data)
    assert node is not None, f"tree node with data={data!r} not found"
    tree.select_node(node)
    await pilot.pause()
    attr = _SHEET_VIEW_ATTR.get(data[0])
    if attr is not None:
        await _wait_until(pilot, lambda: getattr(app.screen, attr) is not None)


async def _open_workspace(pilot) -> None:
    await pilot.press("enter")  # picker -> workspace
    await pilot.pause()


async def _select_vf_picker_entry(pilot, app, vf_id: str) -> None:
    """Highlight and activate a VirtueFlawPickerScreen entry by catalog id.

    The catalog now has 600+ entries, so most are well outside the picker
    dialog's visible/scrolled area -- pixel-coordinate pilot.click() raises
    OutOfBounds for anything not currently on screen. Setting ListView.index
    and pressing enter selects it the same way a real click/enter would,
    without needing the item to be visible.
    """
    list_view = app.screen.query_one("#vf-picker-list", ListView)
    target_id = f"vf-{vf_id}"
    for i, item in enumerate(list_view.children):
        if item.id == target_id:
            list_view.index = i
            break
    else:
        raise AssertionError(f"{target_id!r} not found in Virtue/Flaw picker list")
    await pilot.pause()
    await pilot.press("enter")
    await pilot.pause()


#: Which top-level character-sheet tab each Collapsible section lives in.
#: "tab-spells" maps to itself -- the one tab with no sub-sections, keyed by
#: its own tab id (see WorkspaceScreen._active_character_section()).
_SECTION_TAB: dict[str, str] = {
    "section-identity": "tab-identity",
    "section-background": "tab-identity",
    "section-description": "tab-identity",
    "section-characteristics": "tab-identity",
    "section-abilities": "tab-identity",
    "section-vf": "tab-identity",
    "section-aging": "tab-identity",
    "section-personality-traits": "tab-personality",
    "section-reputations": "tab-personality",
    "section-wounds": "tab-personality",
    "section-fatigue": "tab-personality",
    "section-inventory": "tab-personality",
    "section-arts": "tab-hermetic",
    "section-raw-vis": "tab-hermetic",
    "section-hermetic-background": "tab-hermetic",
    "tab-spells": "tab-spells",
}


async def _open_section(pilot, app, section_id: str) -> None:
    """Switch to the tab containing `section_id` and focus that section.

    The generic Add/Remove/Edit bindings dispatch by whichever Collapsible
    section currently has focus (its title, since CollapsibleTitle is the
    focusable part -- see WorkspaceScreen._active_character_section()), so
    most character-mutation tests need this before pressing
    'a'/'A'/'e'/'v'/'V'. `section_id` may also be "tab-spells", the one tab
    with no sub-sections.
    """
    view = app.screen._character_sheet_view
    assert view is not None, "no character sheet is currently shown"
    tab_id = _SECTION_TAB[section_id]
    view.query_one(TabbedContent).active = tab_id
    await pilot.pause()
    if section_id != tab_id:
        collapsible = view.query_one(f"#{section_id}", Collapsible)
        collapsible.query_one("CollapsibleTitle").focus()
        await pilot.pause()


#: Same idea as _SECTION_TAB, for the laboratory sheet.
_LAB_SECTION_TAB: dict[str, str] = {
    "section-lab-identity": "tab-lab-planning",  # top panel, not inside any tab
    "section-lab-characteristics": "tab-lab-planning",
    "tab-lab-planning": "tab-lab-planning",
    "tab-lab-vf": "tab-lab-vf",
    "section-lab-specialties": "tab-lab-attributes",
    "section-lab-features": "tab-lab-attributes",
    "section-lab-rooms": "tab-lab-attributes",
    "section-lab-raw-vis": "tab-lab-inventory",
    "section-lab-items": "tab-lab-inventory",
    "tab-lab-diary": "tab-lab-diary",
}


async def _open_lab_section(pilot, app, section_id: str) -> None:
    """Same idea as _open_section, for the laboratory sheet -- see that
    docstring. The top-panel sections (Identity/Characteristics) aren't
    inside any tab, so they're focused directly regardless of which tab is
    active.
    """
    view = app.screen._laboratory_sheet_view
    assert view is not None, "no laboratory sheet is currently shown"
    # Let the view's own initial focus (set when the lab is first shown, and
    # applied a message-loop cycle later) land before we move focus
    # ourselves -- otherwise it can arrive afterwards and steal it back.
    await _wait_until(pilot, lambda: view.initial_tab_seen)
    await pilot.pause()
    if section_id in ("section-lab-identity", "section-lab-characteristics"):
        collapsible = view.query_one(f"#{section_id}", Collapsible)
        collapsible.query_one("CollapsibleTitle").focus()
        await pilot.pause()
        return
    tab_id = _LAB_SECTION_TAB[section_id]
    view.query_one(TabbedContent).active = tab_id
    await pilot.pause()
    if section_id != tab_id:
        collapsible = view.query_one(f"#{section_id}", Collapsible)
        collapsible.query_one("CollapsibleTitle").focus()
        await pilot.pause()
    else:
        # A flat tab: wait for the tab switch to clear focus so dispatch
        # resolves to the tab itself.
        await _wait_until(pilot, lambda: app.screen._active_section() == section_id)


async def test_picker_shows_placeholder_with_no_sagas():
    app = ArsMagicaManagerApp()
    async with app.run_test():
        assert isinstance(app.screen, SagaPickerScreen)
        list_view = app.screen.query_one("#saga-list", ListView)
        assert len(list_view.children) == 1


async def test_create_saga_flow_saves_and_returns_to_picker():
    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await pilot.press("n")
        await pilot.pause()
        assert isinstance(app.screen, SagaCreateScreen)

        form = app.screen
        form.query_one("#input-name", Input).value = "Dammerstein"
        form.query_one("#input-storyguide", Input).value = "Alex"
        form.query_one("#input-year", Input).value = "1220"

        await pilot.click("#btn-create")
        await pilot.pause()

        assert isinstance(app.screen, SagaPickerScreen)

    assert storage.list_sagas() == ["dammerstein"]
    saga = storage.load_saga("dammerstein")
    assert saga.name == "Dammerstein"
    assert saga.storyguide == "Alex"
    assert saga.current_year == 1220
    assert saga.current_season == "Spring"
    assert saga.description == ""


async def test_create_saga_requires_name_and_storyguide():
    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await pilot.press("n")
        await pilot.pause()

        await pilot.click("#btn-create")
        await pilot.pause()

        # Validation failed, so we're still on the create screen and nothing saved.
        assert isinstance(app.screen, SagaCreateScreen)

    assert storage.list_sagas() == []


async def test_selecting_a_saga_opens_the_workspace():
    storage.save_saga(
        Saga(id="test_saga", name="Test Saga", storyguide="Alex", current_year=1220)
    )

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        list_view = app.screen.query_one("#saga-list", ListView)
        assert list_view.index == 0

        await pilot.press("enter")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert app.screen.saga.id == "test_saga"
        assert app.screen.selected_kind == "saga"


async def test_workspace_tree_has_no_covenants_for_a_fresh_saga():
    storage.save_saga(Saga(id="test_saga", name="Test Saga", storyguide="Alex"))

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_workspace(pilot)

        tree = app.screen.query_one("#nav-tree", Tree)
        assert len(tree.root.children) == 0


async def test_create_covenant_flow_saves_covenant_and_empty_library():
    storage.save_saga(Saga(id="test_saga", name="Test Saga", storyguide="Alex"))

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_workspace(pilot)

        await pilot.press("n")
        await pilot.pause()
        assert isinstance(app.screen, CovenantCreateScreen)

        app.screen.query_one("#input-name", Input).value = "Fengheld"
        app.screen.query_one("#input-notes", Input).value = "A border covenant"

        await pilot.click("#btn-create")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert app.screen.selected_covenant is not None
        assert app.screen.selected_covenant.name == "Fengheld"
        tree = app.screen.query_one("#nav-tree", Tree)
        assert len(tree.root.children) == 1

    saga = storage.load_saga("test_saga")
    assert len(saga.covenants) == 1
    covenant = saga.covenants[0]
    assert covenant.name == "Fengheld"
    assert covenant.notes == "A border covenant"
    assert covenant.id == "fengheld"

    assert len(saga.libraries) == 1
    library = saga.libraries[0]
    assert library.id == covenant.library_id
    assert library.covenant_id == covenant.id
    assert library.books == []


async def test_create_covenant_requires_name():
    storage.save_saga(Saga(id="test_saga", name="Test Saga", storyguide="Alex"))

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_workspace(pilot)

        await pilot.press("n")
        await pilot.pause()

        await pilot.click("#btn-create")
        await pilot.pause()

        assert isinstance(app.screen, CovenantCreateScreen)

    saga = storage.load_saga("test_saga")
    assert saga.covenants == []


def _saga_with_empty_covenant() -> Saga:
    return Saga(
        id="test_saga",
        name="Test Saga",
        storyguide="Alex",
        covenants=[Covenant(id="cov1", saga_id="test_saga", name="Test Covenant")],
    )


async def _select_covenant(pilot, app, covenant_id: str = "cov1") -> None:
    await _open_workspace(pilot)
    await _select(pilot, app, ("covenant", covenant_id))


async def _select_character(pilot, app, character_id: str = "char1") -> None:
    await _select_covenant(pilot, app)
    await _select(pilot, app, ("character", character_id))


async def _select_laboratory(pilot, app, laboratory_id: str = "lab1") -> None:
    await _select_covenant(pilot, app)
    await _select(pilot, app, ("laboratory", laboratory_id))


async def test_create_character_at_saga_level_is_unassigned_and_selectable():
    storage.save_saga(Saga(id="test_saga", name="Test Saga", storyguide="Alex"))

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_workspace(pilot)
        assert app.screen.selected_kind == "saga"

        await pilot.press("c")
        await pilot.pause()
        assert isinstance(app.screen, CharacterCreateScreen)
        # No covenant is selected, so the dialog defaults to none.
        assert app.screen.query_one("#select-covenant", Select).value == Select.NULL
        app.screen.query_one("#input-name", Input).value = "Wandering Grog"
        app.screen.query_one("#select-type", Select).value = "grog"
        await pilot.click("#btn-create")
        await pilot.pause()

        # Listed under the saga, and selectable from the tree.
        tree = app.screen.query_one("#nav-tree", Tree)
        assert _find_node(tree, ("character_group", None)) is not None
        await _select(pilot, app, ("character", "wandering_grog"))
        assert app.screen.selected_character.name == "Wandering Grog"
        assert app.screen.selected_covenant is None

    assert storage.load_saga("test_saga").characters[0].covenant_id is None


async def test_create_character_defaults_to_current_covenant():
    storage.save_saga(_saga_with_empty_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)

        await pilot.press("c")
        await pilot.pause()
        assert isinstance(app.screen, CharacterCreateScreen)

        app.screen.query_one("#input-name", Input).value = "Leandro"

        await pilot.click("#btn-create")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert app.screen.selected_character is not None
        assert app.screen.selected_character.name == "Leandro"

    saga = storage.load_saga("test_saga")
    assert len(saga.characters) == 1
    character = saga.characters[0]
    assert character.name == "Leandro"
    assert character.type == "magus"
    assert character.covenant_id == "cov1"


async def test_create_character_with_no_covenant():
    storage.save_saga(_saga_with_empty_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)

        await pilot.press("c")
        await pilot.pause()

        form = app.screen
        form.query_one("#input-name", Input).value = "Wandering Grog"
        form.query_one("#select-type", Select).value = "grog"
        form.query_one("#select-covenant", Select).value = Select.NULL

        await pilot.click("#btn-create")
        await pilot.pause()

    saga = storage.load_saga("test_saga")
    character = saga.characters[0]
    assert character.name == "Wandering Grog"
    assert character.type == "grog"
    assert character.covenant_id is None


async def test_create_character_requires_name():
    storage.save_saga(_saga_with_empty_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)

        await pilot.press("c")
        await pilot.pause()

        await pilot.click("#btn-create")
        await pilot.pause()

        assert isinstance(app.screen, CharacterCreateScreen)

    saga = storage.load_saga("test_saga")
    assert saga.characters == []


def _sample_saga_with_covenant() -> Saga:
    return Saga(
        id="test_saga",
        name="Test Saga",
        storyguide="Alex",
        covenants=[
            Covenant(
                id="cov1",
                saga_id="test_saga",
                name="Test Covenant",
                notes="A nice place",
                vis_stock={"Ignem": 5},
                library_id="lib1",
                aura=3,
            )
        ],
        characters=[
            Character(
                id="char1",
                name="Leandro",
                type="magus",
                covenant_id="cov1",
                characteristics=Characteristics(intelligence=3, stamina=1),
                arts={
                    "creo": ArtScore(level=10, xp=55),
                    "ignem": ArtScore(level=5, xp=15),
                },
                abilities=[
                    Ability(
                        name="Magic Theory",
                        category="Academic",
                        level=5,
                        xp=75,
                        specialty="Lab Totals",
                    )
                ],
                virtues_flaws=[
                    VirtueFlawInstance(
                        vf_id="vf_affinity_with_art", params={"art": "creo"}
                    )
                ],
                spells_known=["spell1"],
                assigned_lab_id="lab1",
            )
        ],
        laboratories=[
            Laboratory(
                id="lab1",
                covenant_id="cov1",
                name="Leandro's Sanctum",
                owner_id="char1",
                characteristics=LabCharacteristics(size=1),
                features=["Well-Stocked"],
                virtues_flaws=[VirtueFlawInstance(vf_id="labvf_superior_construction")],
            )
        ],
        libraries=[Library(id="lib1", covenant_id="cov1", books=["book1", "book2"])],
        books=[
            Book(
                id="book1",
                type="Summa",
                subject="Magic Theory",
                quality=6,
                level=8,
                author="Bonisagus",
            ),
            Book(
                id="book2",
                type="Lab Text",
                subject="Ignem",
                quality=9,
                spell_id="spell1",
            ),
        ],
        spells=[
            Spell(
                id="spell1",
                name="Ball of Abysmal Flame",
                technique="Creo",
                form="Ignem",
                level=20,
            )
        ],
    )


async def test_selecting_covenant_shows_summary_and_tree_children():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)

        assert app.screen.selected_covenant.id == "cov1"
        view = app.screen._covenant_sheet_view
        assert view is not None
        assert view.query_one("#section-cov-info", Collapsible).title == (
            "Test Covenant"
        )
        assert "A nice place" in view._description_text()
        # The old bare vis_stock became a Raw Vis store on the Possessions tab.
        assert view._pos_rows("vis_store") == [(0, "Ignem Vis | Art: Ignem | Pawns: 5")]

        tree = app.screen.query_one("#nav-tree", Tree)
        assert _find_node(tree, ("character_group", "cov1")) is not None
        assert _find_node(tree, ("laboratory_group", "cov1")) is not None
        assert _find_node(tree, ("library", "cov1")) is not None
        assert _find_node(tree, ("character", "char1")) is not None
        assert _find_node(tree, ("laboratory", "lab1")) is not None


async def test_selecting_character_shows_sheet_fields():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)

        view = app.screen._character_sheet_view
        assert "Name: Leandro" in view._identity_text()
        assert "Covenant: Test Covenant" in view._identity_text()
        assert "Assigned Laboratory: Leandro's Sanctum" in view._identity_text()
        assert "Int 3" in view._characteristics_text()
        assert "Academic:" in view._abilities_text()
        assert "Magic Theory (Lab Totals) 5/75" in view._abilities_text()
        assert "Affinity with Creo" in view._vf_text()
        assert "Creo (Cr): 10/55" in view._arts_text()
        assert "Ball of Abysmal Flame (CrIg 20)" in view._spells_text()


async def test_selecting_laboratory_shows_owner_and_virtues():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)
        await _select(pilot, app, ("laboratory", "lab1"))

        view = app.screen._laboratory_sheet_view
        identity = view._identity_text()
        assert "Owner: Leandro" in identity
        assert "Aura: 3" in identity
        assert "Well-Stocked" in view._features_text()
        assert "Superior Construction" in view._vf_text()


async def test_selecting_library_shows_books_and_lab_text_spell():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)
        await _select(pilot, app, ("library", "cov1"))

        library = next(lib for lib in app.screen.saga.libraries if lib.id == "lib1")
        summary = app.screen._library_summary(library)
        assert "[Summa] Magic Theory L8 Q6 by Bonisagus" in summary
        assert "[Lab Text] Ignem Q9 -- Ball of Abysmal Flame" in summary


def _saga_with_bare_character() -> Saga:
    return Saga(
        id="test_saga",
        name="Test Saga",
        storyguide="Alex",
        covenants=[Covenant(id="cov1", saga_id="test_saga", name="Test Covenant")],
        characters=[
            Character(id="char1", name="Leandro", type="magus", covenant_id="cov1")
        ],
    )


def _saga_with_bare_laboratory() -> Saga:
    saga = _saga_with_bare_character()
    saga.laboratories.append(
        Laboratory(id="lab1", covenant_id="cov1", name="Test Lab", owner_id="char1")
    )
    return saga


def _saga_with_populated_laboratory() -> Saga:
    """A lab with one entry in every editable list (two Raw Vis Arts, so
    sorted order -- aquam, ignem -- is meaningful)."""
    saga = _saga_with_bare_laboratory()
    lab = saga.laboratories[0]
    lab.specialties = ["Ignem"]
    lab.features = ["Arcane Library"]
    lab.rooms = [NamedDescription(name="Vault", description="Locked")]
    lab.inventory_items = [NamedDescription(name="Silver Mirror", description="Old")]
    lab.raw_vis = {"ignem": 4, "aquam": 2}
    lab.diary = [
        DiaryEntry(year=1220, season="Spring", name="Studied", details="Notes")
    ]
    return saga


async def test_add_virtue_flaw_without_parameters_to_character():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf")

        await pilot.press("v")
        await pilot.pause()
        assert isinstance(app.screen, VirtueFlawPickerScreen)

        await _select_vf_picker_entry(pilot, app, "vf_common_sense")

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Common Sense" in app.screen._character_sheet_view._vf_text()

    saga = storage.load_saga("test_saga")
    character = saga.characters[0]
    assert len(character.virtues_flaws) == 1
    assert character.virtues_flaws[0].vf_id == "vf_common_sense"


async def test_add_virtue_flaw_with_parameters_to_character():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf")

        await pilot.press("v")
        await pilot.pause()

        await _select_vf_picker_entry(pilot, app, "vf_affinity_with_art")
        assert isinstance(app.screen, ParamPromptScreen)

        app.screen.query_one("#input-param-art", Input).value = "Creo"
        await pilot.click("#btn-confirm")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Affinity with Creo" in app.screen._character_sheet_view._vf_text()

    saga = storage.load_saga("test_saga")
    character = saga.characters[0]
    assert len(character.virtues_flaws) == 1
    assert character.virtues_flaws[0].vf_id == "vf_affinity_with_art"
    assert character.virtues_flaws[0].params == {"art": "creo"}


async def test_cancelling_param_screen_returns_to_picker_without_adding():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf")

        await pilot.press("v")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, ParamPromptScreen)

        await pilot.press("escape")
        await pilot.pause()

        assert isinstance(app.screen, VirtueFlawPickerScreen)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].virtues_flaws == []


async def test_virtue_flaw_picker_excludes_already_held_entries():
    saga = _saga_with_bare_character()
    saga.characters[0].virtues_flaws.append(
        VirtueFlawInstance(vf_id="vf_affinity_with_art", params={"art": "creo"})
    )
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf")

        await pilot.press("v")
        await pilot.pause()

        picker_list = app.screen.query_one("#vf-picker-list", ListView)
        item_ids = [item.id for item in picker_list.children]
        assert "vf-vf_affinity_with_art" not in item_ids


async def test_virtue_flaw_picker_search_filters_by_typed_text():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf")

        await pilot.press("v")
        await pilot.pause()
        assert isinstance(app.screen, VirtueFlawPickerScreen)

        picker_list = app.screen.query_one("#vf-picker-list", ListView)
        assert len(picker_list.children) > 100  # the full 624-entry catalog

        app.screen.query_one("#picker-search", Input).value = "common sense"
        await pilot.pause()

        item_ids = [item.id for item in picker_list.children]
        assert item_ids == ["vf-vf_common_sense"]


async def test_virtue_flaw_picker_search_shows_no_matches_message():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf")

        await pilot.press("v")
        await pilot.pause()

        app.screen.query_one("#picker-search", Input).value = "xyzzy nonexistent"
        await pilot.pause()

        picker_list = app.screen.query_one("#vf-picker-list", ListView)
        assert len(picker_list.children) == 1
        assert picker_list.children[0].id is None  # the "(no matches...)" row


async def test_virtue_flaw_picker_enter_in_search_activates_top_match():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf")

        await pilot.press("v")
        await pilot.pause()

        search = app.screen.query_one("#picker-search", Input)
        search.value = "common sense"
        await pilot.pause()
        await search.action_submit()  # same as pressing Enter in the search box
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Common Sense" in app.screen._character_sheet_view._vf_text()

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].virtues_flaws[0].vf_id == "vf_common_sense"


async def test_lab_virtue_flaw_picker_search_filters_by_typed_text():
    saga = _saga_with_bare_character()
    saga.laboratories.append(
        Laboratory(id="lab1", covenant_id="cov1", name="Test Lab", owner_id="char1")
    )
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)
        await _select(pilot, app, ("laboratory", "lab1"))
        await _open_lab_section(pilot, app, "tab-lab-vf")

        await pilot.press("v")
        await pilot.pause()
        assert isinstance(app.screen, LabVirtueFlawPickerScreen)

        picker_list = app.screen.query_one("#lab-vf-picker-list", ListView)
        assert len(picker_list.children) > 30  # the full 53-entry lab catalog

        app.screen.query_one("#picker-search", Input).value = "superior construction"
        await pilot.pause()

        item_ids = [item.id for item in picker_list.children]
        assert item_ids == ["labvf-labvf_superior_construction"]


async def test_ability_picker_search_filters_by_typed_text():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-abilities")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, AbilityPickerScreen)

        picker_list = app.screen.query_one("#ability-picker-list", ListView)
        assert len(picker_list.children) > 30  # the full 78-entry catalog

        app.screen.query_one("#picker-search", Input).value = "athletics"
        await pilot.pause()

        item_ids = [item.id for item in picker_list.children]
        assert item_ids == ["ability-ab_athletics"]


async def test_picker_down_key_moves_focus_from_search_to_list():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-abilities")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, AbilityPickerScreen)

        search = app.screen.query_one("#picker-search", Input)
        assert app.focused is search  # search box is focused on open

        await pilot.press("down")
        await pilot.pause()

        picker_list = app.screen.query_one("#ability-picker-list", ListView)
        assert app.focused is picker_list


async def test_add_virtue_flaw_to_laboratory_uses_lab_picker():
    saga = _saga_with_bare_character()
    saga.laboratories.append(
        Laboratory(id="lab1", covenant_id="cov1", name="Test Lab", owner_id="char1")
    )
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)
        await _select(pilot, app, ("laboratory", "lab1"))
        await _open_lab_section(pilot, app, "tab-lab-vf")

        await pilot.press("v")
        await pilot.pause()
        assert isinstance(app.screen, LabVirtueFlawPickerScreen)

        picker_list = app.screen.query_one("#lab-vf-picker-list", ListView)
        target_id = "labvf-labvf_superior_construction"
        for i, item in enumerate(picker_list.children):
            if item.id == target_id:
                picker_list.index = i
                break
        else:
            raise AssertionError(f"{target_id!r} not found in the lab V&F picker")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Superior Construction" in app.screen._laboratory_sheet_view._vf_text()

    saga = storage.load_saga("test_saga")
    lab = saga.laboratories[0]
    assert len(lab.virtues_flaws) == 1
    assert lab.virtues_flaws[0].vf_id == "labvf_superior_construction"


async def test_create_laboratory_flow_saves_laboratory():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)

        await pilot.press("l")
        await pilot.pause()
        assert isinstance(app.screen, LaboratoryCreateScreen)

        app.screen.query_one("#input-name", Input).value = "The Alchemical Tower"
        app.screen.query_one("#input-size", Input).value = "1"

        await pilot.click("#btn-create")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert app.screen.selected_laboratory is not None
        assert app.screen.selected_laboratory.name == "The Alchemical Tower"

    saga = storage.load_saga("test_saga")
    assert len(saga.laboratories) == 1
    lab = saga.laboratories[0]
    assert lab.name == "The Alchemical Tower"
    assert lab.covenant_id == "cov1"
    assert lab.characteristics.size == 1
    assert lab.owner_id is None


async def test_create_laboratory_requires_name():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)

        await pilot.press("l")
        await pilot.pause()

        await pilot.click("#btn-create")
        await pilot.pause()

        assert isinstance(app.screen, LaboratoryCreateScreen)

    saga = storage.load_saga("test_saga")
    assert saga.laboratories == []


async def test_create_laboratory_requires_integer_size():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)

        await pilot.press("l")
        await pilot.pause()

        app.screen.query_one("#input-name", Input).value = "The Tower"
        app.screen.query_one("#input-size", Input).value = "not a number"

        await pilot.click("#btn-create")
        await pilot.pause()

        assert isinstance(app.screen, LaboratoryCreateScreen)

    saga = storage.load_saga("test_saga")
    assert saga.laboratories == []


async def test_add_ability_without_parameters_to_character():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-abilities")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, AbilityPickerScreen)

        await pilot.click("#ability-ab_athletics")
        await pilot.pause()
        assert isinstance(app.screen, AbilityDetailsScreen)

        app.screen.query_one("#input-level", Input).value = "3"
        app.screen.query_one("#input-specialty", Input).value = "Running"

        await pilot.click("#btn-confirm")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert (
            "Athletics (Running) 3/0"
            in app.screen._character_sheet_view._abilities_text()
        )

    saga = storage.load_saga("test_saga")
    character = saga.characters[0]
    assert len(character.abilities) == 1
    assert character.abilities[0].name == "Athletics"
    assert character.abilities[0].category == "General"
    assert character.abilities[0].level == 3
    assert character.abilities[0].specialty == "Running"


async def test_add_ability_with_parameters_to_character():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-abilities")

        await pilot.press("a")
        await pilot.pause()

        await pilot.click("#ability-ab_craft")
        await pilot.pause()
        assert isinstance(app.screen, ParamPromptScreen)

        app.screen.query_one("#input-param-craft", Input).value = "Blacksmith"
        await pilot.click("#btn-confirm")
        await pilot.pause()

        assert isinstance(app.screen, AbilityDetailsScreen)
        assert app.screen.ability_name == "Craft: Blacksmith"

        app.screen.query_one("#input-level", Input).value = "2"

        await pilot.click("#btn-confirm")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    character = saga.characters[0]
    assert len(character.abilities) == 1
    assert character.abilities[0].name == "Craft: Blacksmith"
    assert character.abilities[0].category == "General"
    assert character.abilities[0].level == 2


async def test_cancelling_ability_details_returns_to_picker_without_adding():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-abilities")

        await pilot.press("a")
        await pilot.pause()

        await pilot.click("#ability-ab_athletics")
        await pilot.pause()
        assert isinstance(app.screen, AbilityDetailsScreen)

        await pilot.press("escape")
        await pilot.pause()

        assert isinstance(app.screen, AbilityPickerScreen)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].abilities == []


async def test_ability_picker_excludes_non_templated_duplicates_but_keeps_templated():
    saga = _saga_with_bare_character()
    saga.characters[0].abilities.append(Ability(name="Athletics", level=1))
    saga.characters[0].abilities.append(Ability(name="Craft: Blacksmith", level=1))
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-abilities")

        await pilot.press("a")
        await pilot.pause()

        picker_list = app.screen.query_one("#ability-picker-list", ListView)
        item_ids = [item.id for item in picker_list.children]
        assert "ability-ab_athletics" not in item_ids
        assert "ability-ab_craft" in item_ids


async def test_remove_ability_from_character():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-abilities")
        assert "Magic Theory" in app.screen._character_sheet_view._abilities_text()

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

        await pilot.press("enter")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Magic Theory" not in app.screen._character_sheet_view._abilities_text()

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].abilities == []


async def test_remove_virtue_flaw_from_character():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf")
        assert "Affinity with Creo" in app.screen._character_sheet_view._vf_text()

        await pilot.press("V")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

        await pilot.press("enter")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Affinity with Creo" not in app.screen._character_sheet_view._vf_text()

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].virtues_flaws == []


async def test_remove_virtue_flaw_from_laboratory():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)
        await _select(pilot, app, ("laboratory", "lab1"))
        await _open_lab_section(pilot, app, "tab-lab-vf")
        assert "Superior Construction" in app.screen._laboratory_sheet_view._vf_text()

        await pilot.press("V")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

        await pilot.press("enter")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert (
            "Superior Construction" not in app.screen._laboratory_sheet_view._vf_text()
        )

    saga = storage.load_saga("test_saga")
    assert saga.laboratories[0].virtues_flaws == []


async def test_remove_with_nothing_to_remove_stays_on_same_screen():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-abilities")

        await pilot.press("A")
        await pilot.pause()

        # Nothing to remove -- stays on the workspace, no picker opened.
        assert isinstance(app.screen, WorkspaceScreen)


async def test_cancelling_removal_picker_keeps_the_item():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf")

        await pilot.press("V")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

        await pilot.press("escape")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Affinity with Creo" in app.screen._character_sheet_view._vf_text()

    saga = storage.load_saga("test_saga")
    assert len(saga.characters[0].virtues_flaws) == 1


async def test_edit_arts_prefills_existing_scores_and_saves_full_grid():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-arts")

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditArtsScreen)

        assert app.screen.query_one("#input-art-creo-level", Input).value == "10"
        assert app.screen.query_one("#input-art-creo-xp", Input).value == "55"
        assert app.screen.query_one("#input-art-ignem-level", Input).value == "5"
        assert app.screen.query_one("#input-art-ignem-xp", Input).value == "15"
        assert app.screen.query_one("#input-art-rego-level", Input).value == "0"
        assert app.screen.query_one("#input-art-rego-xp", Input).value == "0"

        app.screen.query_one("#input-art-rego-level", Input).value = "3"
        app.screen.query_one("#input-art-rego-xp", Input).value = "6"

        await pilot.click("#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    arts = saga.characters[0].arts
    assert arts["creo"] == ArtScore(level=10, xp=55)
    assert arts["ignem"] == ArtScore(level=5, xp=15)
    assert arts["rego"] == ArtScore(level=3, xp=6)
    # Every one of the 15 Arts is written, not just the ones that were nonzero.
    assert len(arts) == 15
    assert arts["vim"] == ArtScore(level=0, xp=0)


async def test_edit_arts_requires_integers():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-arts")

        await pilot.press("e")
        await pilot.pause()

        app.screen.query_one("#input-art-rego-level", Input).value = "not a number"

        await pilot.click("#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, EditArtsScreen)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].arts == {
        "creo": ArtScore(level=10, xp=55),
        "ignem": ArtScore(level=5, xp=15),
    }


async def test_edit_arts_cancel_discards_changes():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-arts")

        await pilot.press("e")
        await pilot.pause()

        app.screen.query_one("#input-art-rego-level", Input).value = "9"

        await pilot.press("escape")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].arts == {
        "creo": ArtScore(level=10, xp=55),
        "ignem": ArtScore(level=5, xp=15),
    }


async def test_edit_arts_grid_fits_default_terminal_and_accepts_real_typing():
    # A default-sized terminal (80x24) is what run_test uses unless told
    # otherwise, and matches a typical real terminal -- this test drives
    # actual clicks and keystrokes (not direct .value assignment) so a
    # layout tall/wide enough to push rows off-screen, or to block real
    # keyboard input, actually fails here.
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-arts")
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditArtsScreen)

        screen_width = app.screen.size.width
        # One Technique row and two Form rows, from opposite ends of the
        # single-column (scrollable) list -- Herbam and Vim aren't visible
        # without scrolling, exercising that the scroll-then-click path
        # itself works, not just whatever's on-screen by default.
        for field_id in (
            "#input-art-rego-level",
            "#input-art-herbam-level",
            "#input-art-vim-level",
        ):
            field = app.screen.query_one(field_id, Input)
            field.scroll_visible(animate=False)
            await pilot.pause()
            assert field.region.x + field.region.width <= screen_width, (
                f"{field_id} is rendered outside the {screen_width}-wide screen"
            )

            await pilot.click(field_id)
            await pilot.pause()
            # Clear whatever's there regardless of where the click landed the
            # cursor, then type -- this is exercising real keystrokes, not
            # asserting exact cursor/selection placement from the click.
            await pilot.press("end", "backspace", "backspace", "backspace")
            await pilot.press("7")
            await pilot.pause()
            assert field.value == "7"

        await pilot.click("#btn-save")
        await pilot.pause()

    saga = storage.load_saga("test_saga")
    arts = saga.characters[0].arts
    assert arts["rego"].level == 7
    assert arts["herbam"].level == 7
    assert arts["vim"].level == 7


async def test_arts_and_spells_tabs_are_absent_for_non_magi():
    saga = _saga_with_empty_covenant()
    saga.characters.append(
        Character(id="grog1", name="Guard", type="grog", covenant_id="cov1")
    )
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)
        await _select(pilot, app, ("character", "grog1"))
        assert app.screen.selected_character.type == "grog"

        view = app.screen._character_sheet_view
        tabbed = view.query_one(TabbedContent)
        tab_ids = {pane.id for pane in tabbed.query("TabPane")}
        assert "tab-hermetic" not in tab_ids
        assert "tab-spells" not in tab_ids
        # Tabs/sections that do apply to every character type are still present.
        assert "tab-identity" in tab_ids
        assert "tab-personality" in tab_ids
        section_ids = {c.id for c in view.query(Collapsible)}
        assert "section-abilities" in section_ids
        assert "section-inventory" in section_ids
        assert "section-arts" not in section_ids
        assert "section-hermetic-background" not in section_ids

        # With no Arts tab to switch to, 'e' on the default Identity tab
        # opens Edit Identity rather than doing nothing.
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, IdentityEditScreen)


async def test_creating_a_second_character_after_viewing_the_first_works():
    storage.save_saga(_saga_with_empty_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)

        # Create the first character.
        await pilot.press("c")
        await pilot.pause()
        app.screen.query_one("#input-name", Input).value = "Leandro"
        await pilot.click("#btn-create")
        await pilot.pause()
        assert app.screen.selected_character.name == "Leandro"

        # View it explicitly, then go back to the covenant before adding a
        # second one -- the reported repro was a crash on this exact sequence.
        await _select(pilot, app, ("character", "leandro"))
        await _select(pilot, app, ("covenant", "cov1"))

        await pilot.press("c")
        await pilot.pause()
        app.screen.query_one("#input-name", Input).value = "Guillame"
        await pilot.click("#btn-create")
        await pilot.pause()

        tree = app.screen.query_one("#nav-tree", Tree)
        char_group = _find_node(tree, ("character_group", "cov1"))
        assert len(char_group.children) == 2

    saga = storage.load_saga("test_saga")
    assert {c.name for c in saga.characters} == {"Leandro", "Guillame"}


def _saga_with_two_labs() -> Saga:
    return Saga(
        id="test_saga",
        name="Test Saga",
        storyguide="Alex",
        covenants=[
            Covenant(id="cov1", saga_id="test_saga", name="Test Covenant"),
            Covenant(id="cov2", saga_id="test_saga", name="Other Covenant"),
        ],
        characters=[
            Character(
                id="char1",
                name="Leandro",
                type="magus",
                covenant_id="cov1",
                assigned_lab_id="lab1",
            )
        ],
        laboratories=[
            Laboratory(id="lab1", covenant_id="cov1", name="Lab One", owner_id="char1"),
            Laboratory(id="lab2", covenant_id="cov1", name="Lab Two"),
        ],
    )


async def test_edit_identity_updates_name_covenant_and_laboratory():
    storage.save_saga(_saga_with_two_labs())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)  # defaults to the Identity tab

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, IdentityEditScreen)

        app.screen.query_one("#input-name", Input).value = "Leandro the Elder"
        app.screen.query_one("#select-covenant", Select).value = "cov2"
        app.screen.query_one("#select-laboratory", Select).value = "lab2"

        await pilot.click("#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert (
            "Name: Leandro the Elder"
            in app.screen._character_sheet_view._identity_text()
        )

    saga = storage.load_saga("test_saga")
    character = saga.characters[0]
    assert character.name == "Leandro the Elder"
    assert character.covenant_id == "cov2"
    assert character.assigned_lab_id == "lab2"

    lab1 = next(lab for lab in saga.laboratories if lab.id == "lab1")
    lab2 = next(lab for lab in saga.laboratories if lab.id == "lab2")
    assert lab1.owner_id is None
    assert lab2.owner_id == "char1"


async def test_edit_identity_requires_name():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, IdentityEditScreen)

        app.screen.query_one("#input-name", Input).value = ""

        await pilot.click("#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, IdentityEditScreen)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].name == "Leandro"


async def test_edit_characteristics_updates_values():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-characteristics")

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditCharacteristicsScreen)

        app.screen.query_one("#input-char-intelligence", Input).value = "3"
        app.screen.query_one("#input-char-quickness", Input).value = "-1"

        # An explicit interior offset: this button's default (0, 0) --
        # its exact top-left corner pixel -- doesn't register through the
        # full click pipeline here even though get_widget_at() confirms
        # the button owns that pixel; an interior point is the documented
        # workaround (see the pilot.click() docstring's own example).
        await pilot.click("#btn-save", offset=(8, 1))
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        text = app.screen._character_sheet_view._characteristics_text()
        assert "Int 3" in text
        assert "Qik -1" in text

    saga = storage.load_saga("test_saga")
    c = saga.characters[0].characteristics
    assert c.intelligence == 3
    assert c.quickness == -1


async def test_edit_ability_updates_existing_entry():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-abilities")

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

        await pilot.press("enter")  # only one ability -- select it
        await pilot.pause()
        assert isinstance(app.screen, AbilityDetailsScreen)
        assert app.screen.query_one("#input-level", Input).value == "5"
        assert app.screen.query_one("#input-xp", Input).value == "75"

        app.screen.query_one("#input-level", Input).value = "6"
        app.screen.query_one("#input-xp", Input).value = "90"

        await pilot.click("#btn-confirm")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert (
            "Magic Theory (Lab Totals) 6/90"
            in app.screen._character_sheet_view._abilities_text()
        )

    saga = storage.load_saga("test_saga")
    ability = saga.characters[0].abilities[0]
    assert ability.level == 6
    assert ability.xp == 90
    assert ability.category == "Academic"


def _saga_with_character_and_spell() -> Saga:
    saga = _saga_with_bare_character()
    saga.spells.append(
        Spell(
            id="spell1", name="Pilum of Fire", technique="Creo", form="Ignem", level=20
        )
    )
    return saga


async def test_add_and_remove_spell_known():
    storage.save_saga(_saga_with_character_and_spell())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "tab-spells")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, SpellPickerScreen)

        await pilot.click("#spell-spell1")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert (
            "Pilum of Fire (CrIg 20)" in app.screen._character_sheet_view._spells_text()
        )

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

        await pilot.press("enter")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert app.screen._character_sheet_view._spells_text() == "(none recorded)"

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].spells_known == []


async def test_add_and_remove_inventory_item():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-inventory")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, ItemAddScreen)

        app.screen.query_one("#input-item", Input).value = "Fine wool cloak"
        await pilot.click("#btn-create")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Fine wool cloak" in app.screen._character_sheet_view._inventory_text()

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

        await pilot.press("enter")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].inventory == []


async def test_add_action_disabled_on_tabs_without_addable_lists():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)  # defaults to the Identity tab

        await pilot.press("a")
        await pilot.pause()

        # Identity has nothing to "add" -- the binding is disabled there.
        assert isinstance(app.screen, WorkspaceScreen)


async def test_edit_background_updates_fields():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-background")

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditBackgroundScreen)

        app.screen.query_one("#input-bg-player", Input).value = "Alex"
        app.screen.query_one("#input-bg-year_born", Input).value = "1180"

        # The Background dialog has 10 fields, taller than the default
        # 80x24 test terminal -- pilot.click() needs an on-screen target,
        # so trigger the button directly rather than by pixel coordinate.
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        text = app.screen._character_sheet_view._background_text()
        assert "Player: Alex" in text
        assert "Age: 40" in text  # current_year 1220 (default) - 1180

    saga = storage.load_saga("test_saga")
    background = saga.characters[0].background
    assert background.player == "Alex"
    assert background.year_born == 1180


async def test_edit_description_updates_fields_including_handedness():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-description")

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditDescriptionScreen)

        app.screen.query_one("#input-desc-height", Input).value = "1.8"
        app.screen.query_one("#select-desc-handedness", Select).value = "left"

        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        text = app.screen._character_sheet_view._description_text()
        assert "Height: 1.8" in text
        assert "Handedness: left" in text

    saga = storage.load_saga("test_saga")
    description = saga.characters[0].description
    assert description.height == 1.8
    assert description.handedness == "left"


async def test_edit_aging_updates_decrepitude_and_warping():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-aging")

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditAgingScreen)

        app.screen.query_one("#input-aging-decrepitude", Input).value = "2"
        app.screen.query_one("#input-aging-warping_score", Input).value = "1"
        app.screen.query_one("#input-aging-warping_points", Input).value = "6"

        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        text = app.screen._character_sheet_view._aging_text()
        assert "Decrepitude: 2" in text
        assert "Warping: 1/6" in text

    saga = storage.load_saga("test_saga")
    aging = saga.characters[0].aging
    assert aging.decrepitude == 2
    assert aging.warping_score == 1
    assert aging.warping_points == 6


async def test_edit_wounds_updates_counts_and_flags():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-wounds")

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditWoundsScreen)

        app.screen.query_one("#input-wounds-medium", Input).value = "2"
        app.screen.query_one("#check-wounds-incapacitated", Checkbox).value = True

        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        text = app.screen._character_sheet_view._wounds_text()
        assert "Medium Wounds: 2" in text
        assert "Incapacitated: yes" in text

    saga = storage.load_saga("test_saga")
    wounds = saga.characters[0].wounds
    assert wounds.medium == 2
    assert wounds.incapacitated is True


async def test_edit_fatigue_updates_level():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-fatigue")

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditFatigueScreen)

        app.screen.query_one("#select-fatigue-level", Select).value = "tired"
        await pilot.click("#btn-save", offset=(8, 1))
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert (
            "Fatigue Level: Tired" in app.screen._character_sheet_view._fatigue_text()
        )

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].fatigue_level == "tired"


async def test_add_and_remove_personality_trait():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-personality-traits")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, ScoredTraitPromptScreen)

        app.screen.query_one("#input-trait-name", Input).value = "Curious"
        app.screen.query_one("#input-trait-score", Input).value = "3"
        await pilot.click("#btn-save", offset=(8, 1))
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        text = app.screen._character_sheet_view._personality_traits_text()
        assert "Curious: +3" in text

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].personality_traits == []


async def test_add_and_remove_reputation():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-reputations")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, ScoredTraitPromptScreen)

        app.screen.query_one("#input-trait-name", Input).value = "Skilled Enchanter"
        app.screen.query_one("#input-trait-score", Input).value = "2"
        await pilot.click("#btn-save", offset=(8, 1))
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        text = app.screen._character_sheet_view._reputations_text()
        assert "Skilled Enchanter: 2" in text

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].reputations == []


async def test_add_and_remove_raw_vis():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-raw-vis")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, RawVisPromptScreen)

        app.screen.query_one("#select-vis-art", Select).value = "creo"
        app.screen.query_one("#input-vis-pawns", Input).value = "5"
        await pilot.click("#btn-create", offset=(8, 1))
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        text = app.screen._character_sheet_view._raw_vis_text()
        assert "Creo: 5 pawn(s)" in text

        # Adding the same Art again accumulates rather than overwriting.
        await pilot.press("a")
        await pilot.pause()
        app.screen.query_one("#select-vis-art", Select).value = "creo"
        app.screen.query_one("#input-vis-pawns", Input).value = "3"
        await pilot.click("#btn-create", offset=(8, 1))
        await pilot.pause()
        assert "Creo: 8 pawn(s)" in (app.screen._character_sheet_view._raw_vis_text())

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].raw_vis == {}


async def test_edit_hermetic_background_sets_house_and_fields():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-hermetic-background")

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditHermeticBackgroundScreen)

        app.screen.query_one("#select-hermetic-house", Select).value = "house_bonisagus"
        app.screen.query_one("#input-hermetic-parens", Input).value = "Trianoma"

        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        text = app.screen._character_sheet_view._hermetic_background_text()
        assert "House: Bonisagus" in text
        assert "Parens: Trianoma" in text

    saga = storage.load_saga("test_saga")
    hermetic = saga.characters[0].hermetic
    assert hermetic.house == "house_bonisagus"
    assert hermetic.parens == "Trianoma"


async def test_edit_lab_identity_updates_fields_and_owner():
    saga = _saga_with_bare_laboratory()
    saga.characters.append(
        Character(id="char2", name="Guillame", type="magus", covenant_id="cov1")
    )
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        await _open_lab_section(pilot, app, "section-lab-identity")

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditLabIdentityScreen)

        app.screen.query_one("#input-lab-name", Input).value = "Obsidian Crucible"
        app.screen.query_one("#input-lab-location", Input).value = "Black Forest"
        app.screen.query_one("#input-lab-points", Input).value = "50"
        app.screen.query_one("#select-lab-owner", Select).value = "char2"

        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        text = app.screen._laboratory_sheet_view._identity_text()
        assert "Name: Obsidian Crucible" in text
        assert "Location: Black Forest" in text
        assert "Points: 50" in text
        assert "Owner: Guillame" in text

    saga = storage.load_saga("test_saga")
    lab = saga.laboratories[0]
    assert lab.name == "Obsidian Crucible"
    assert lab.location == "Black Forest"
    assert lab.build_points == 50
    assert lab.owner_id == "char2"
    # Bidirectional sync: the new owner points back, the old one is freed.
    new_owner = next(c for c in saga.characters if c.id == "char2")
    old_owner = next(c for c in saga.characters if c.id == "char1")
    assert new_owner.assigned_lab_id == "lab1"
    assert old_owner.assigned_lab_id is None


async def test_edit_lab_characteristics_buttons_are_visible_on_screen():
    """Regression: Save/Cancel were scrolled out of view inside the dialog's
    VerticalScroll. Asserts on-screen position, at a small and a large size."""
    storage.save_saga(_saga_with_bare_laboratory())

    for size in ((80, 24), (140, 50)):
        app = ArsMagicaManagerApp()
        async with app.run_test(size=size) as pilot:
            await _select_laboratory(pilot, app)
            await _open_lab_section(pilot, app, "section-lab-characteristics")
            await pilot.press("e")
            await pilot.pause()
            assert isinstance(app.screen, EditLabCharacteristicsScreen)

            for button_id in ("#btn-save", "#btn-cancel"):
                region = app.screen.query_one(button_id, Button).region
                assert region.height > 0, (size, button_id)
                assert region.bottom <= size[1], (size, button_id)
                assert region.right <= size[0], (size, button_id)


async def test_every_character_sheet_section_starts_expanded():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        view = app.screen._character_sheet_view
        sections = list(view.query(Collapsible))
        assert len(sections) >= 10
        assert all(not section.collapsed for section in sections)


async def test_edit_lab_characteristics_updates_manual_values():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        await _open_lab_section(pilot, app, "section-lab-characteristics")

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditLabCharacteristicsScreen)

        app.screen.query_one("#input-labchar-size", Input).value = "2"
        app.screen.query_one("#input-labchar-safety", Input).value = "-1"

        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        text = app.screen._laboratory_sheet_view._characteristics_table_text()
        # Positive green, zero cyan, negative red.
        assert re.search(
            r"Size:\s+\[green\]\+2\[/\] \[cyan\]\+0\[/\] = \[green\]\+2\[/\]", text
        )
        assert re.search(
            r"Safety:\s+\[red\]-1\[/\] \[cyan\]\+0\[/\] = \[red\]-1\[/\]", text
        )
        # Values line up in columns once the colour markup is stripped: every
        # row has its '=' in the same place.
        plain = re.sub(r"\[/?[a-z]*\]", "", text)
        assert len({line.index("=") for line in plain.splitlines()}) == 1

    saga = storage.load_saga("test_saga")
    characteristics = saga.laboratories[0].characteristics
    assert characteristics.size == 2
    assert characteristics.safety == -1


async def test_lab_top_panel_layout_is_stable_across_tabs():
    """Identity sits above Characteristics, directly above the tab bar,
    fully visible (not clipped), and the tab body stays inside the sheet, on
    every tab. Asserts on-screen geometry, not just widget presence -- the
    original bug was invisible to presence/text assertions."""
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view
        tabbed = view.query_one(TabbedContent)

        for tab_id in (
            "tab-lab-planning",
            "tab-lab-vf",
            "tab-lab-attributes",
            "tab-lab-inventory",
            "tab-lab-diary",
        ):
            tabbed.active = tab_id
            await pilot.pause()

            top = view.query_one("#lab-top-panel").region
            identity = view.query_one("#section-lab-identity").region
            characteristics = view.query_one("#section-lab-characteristics").region

            # Identity above Characteristics, neither clipped by the panel.
            assert identity.y == top.y, tab_id
            assert characteristics.y == identity.bottom, tab_id
            assert characteristics.bottom == top.bottom, tab_id
            # Derived stats left of the table.
            derived = view.query_one("#lab-characteristics-derived").region
            table = view.query_one("#lab-characteristics-content").region
            assert derived.right <= table.x, tab_id
            assert derived.y == table.y, tab_id
            # Tab bar directly below the top panel, body inside the sheet.
            assert tabbed.region.y == top.bottom, tab_id
            assert tabbed.region.bottom <= view.region.bottom, tab_id


async def test_opening_a_lab_focuses_identity_so_edit_hotkey_works():
    """Regression: TabbedContent's own initial TabActivated used to clear the
    focus set on opening a lab, leaving 'e' unavailable until the user
    tabbed into a section by hand. No manual focusing here, on purpose."""
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        assert app.screen._active_section() == "section-lab-identity"

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditLabIdentityScreen)


async def test_clicking_a_lab_top_panel_section_makes_it_active():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_laboratory(pilot, app)

        await pilot.click("#lab-characteristics-content")
        await pilot.pause()
        assert app.screen._active_section() == "section-lab-characteristics"

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditLabCharacteristicsScreen)


async def test_lab_top_panel_edit_buttons_open_edit_dialogs():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view

        view.query_one("#btn-lab-identity-edit", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, EditLabIdentityScreen)
        await pilot.press("escape")
        await pilot.pause()

        view.query_one("#btn-lab-characteristics-edit", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, EditLabCharacteristicsScreen)


async def test_lab_attributes_and_inventory_sections_start_expanded():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view

        for section_id in (
            "section-lab-specialties",
            "section-lab-features",
            "section-lab-rooms",
            "section-lab-raw-vis",
            "section-lab-items",
        ):
            assert not view.query_one(f"#{section_id}", Collapsible).collapsed


async def test_lab_top_panel_sections_are_open_and_cannot_be_collapsed():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view

        for section_id in ("section-lab-identity", "section-lab-characteristics"):
            collapsible = view.query_one(f"#{section_id}", Collapsible)
            assert not collapsible.collapsed

            title = collapsible.query_one("CollapsibleTitle")
            title.focus()
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            assert not collapsible.collapsed

            await pilot.click(title)
            await pilot.pause()
            assert not collapsible.collapsed


async def test_add_and_remove_specialty():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        await _open_lab_section(pilot, app, "section-lab-specialties")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, ItemAddScreen)

        app.screen.query_one("#input-item", Input).value = "Ignem"
        await pilot.click("#btn-create")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Ignem" in app.screen._laboratory_sheet_view._specialties_text()

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    assert saga.laboratories[0].specialties == []


async def test_add_and_remove_feature():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        await _open_lab_section(pilot, app, "section-lab-features")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, ItemAddScreen)

        app.screen.query_one("#input-item", Input).value = "Altar"
        await pilot.click("#btn-create")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Altar" in app.screen._laboratory_sheet_view._features_text()

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    assert saga.laboratories[0].features == []


async def test_add_and_remove_room():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        await _open_lab_section(pilot, app, "section-lab-rooms")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, NamedDescriptionPromptScreen)

        app.screen.query_one("#input-named-desc-name", Input).value = "Vault"
        app.screen.query_one(
            "#input-named-desc-description", Input
        ).value = "A locked cellar"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        text = app.screen._laboratory_sheet_view._rooms_text()
        assert "Vault: A locked cellar" in text

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    assert saga.laboratories[0].rooms == []


async def test_add_and_remove_lab_raw_vis():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        await _open_lab_section(pilot, app, "section-lab-raw-vis")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, RawVisPromptScreen)

        app.screen.query_one("#select-vis-art", Select).value = "ignem"
        app.screen.query_one("#input-vis-pawns", Input).value = "4"
        await pilot.click("#btn-create", offset=(8, 1))
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        text = app.screen._laboratory_sheet_view._raw_vis_text()
        assert "Ignem: 4 pawn(s)" in text

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    assert saga.laboratories[0].raw_vis == {}


async def test_add_and_remove_inventory_item_on_lab():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        await _open_lab_section(pilot, app, "section-lab-items")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, NamedDescriptionPromptScreen)

        app.screen.query_one("#input-named-desc-name", Input).value = "Silver Mirror"
        app.screen.query_one(
            "#input-named-desc-description", Input
        ).value = "For scrying"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        text = app.screen._laboratory_sheet_view._items_text()
        assert "Silver Mirror: For scrying" in text

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    assert saga.laboratories[0].inventory_items == []


async def test_add_and_remove_diary_entry():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        await _open_lab_section(pilot, app, "tab-lab-diary")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, DiaryEntryPromptScreen)

        app.screen.query_one("#input-diary-year", Input).value = "1220"
        app.screen.query_one("#select-diary-season", Select).value = "Autumn"
        app.screen.query_one("#input-diary-name", Input).value = "Invented a spell"
        app.screen.query_one(
            "#input-diary-details", Input
        ).value = "A quiet season of study."
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        text = app.screen._laboratory_sheet_view._diary_text()
        assert "1220 Autumn -- Invented a spell" in text
        assert "A quiet season of study." in text

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    assert saga.laboratories[0].diary == []


async def _pick_first_and_open_editor(pilot, app, section_id: str, editor_type) -> None:
    """Open `section_id`, press 'e', choose the first entry in the picker,
    and check the pre-filled editor dialog appeared."""
    await _open_lab_section(pilot, app, section_id)
    await pilot.press("e")
    await pilot.pause()
    assert isinstance(app.screen, RemovalPickerScreen)
    await pilot.press("enter")
    await pilot.pause()
    assert isinstance(app.screen, editor_type)


async def test_edit_specialty_and_feature():
    storage.save_saga(_saga_with_populated_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view

        await _pick_first_and_open_editor(
            pilot, app, "section-lab-specialties", ItemAddScreen
        )
        assert app.screen.query_one("#input-item", Input).value == "Ignem"
        app.screen.query_one("#input-item", Input).value = "Vim"
        app.screen.query_one("#btn-create", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)
        assert "Vim" in view._specialties_text()
        assert "Ignem" not in view._specialties_text()

        await _pick_first_and_open_editor(
            pilot, app, "section-lab-features", ItemAddScreen
        )
        assert app.screen.query_one("#input-item", Input).value == "Arcane Library"
        app.screen.query_one("#input-item", Input).value = "Aegis"
        app.screen.query_one("#btn-create", Button).press()
        await pilot.pause()
        assert "Aegis" in view._features_text()

    lab = storage.load_saga("test_saga").laboratories[0]
    assert lab.specialties == ["Vim"]
    assert lab.features == ["Aegis"]


async def test_edit_room_and_item():
    storage.save_saga(_saga_with_populated_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view

        await _pick_first_and_open_editor(
            pilot, app, "section-lab-rooms", NamedDescriptionPromptScreen
        )
        name = app.screen.query_one("#input-named-desc-name", Input)
        description = app.screen.query_one("#input-named-desc-description", Input)
        assert (name.value, description.value) == ("Vault", "Locked")
        name.value = "Strongroom"
        description.value = "Iron-bound"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert "Strongroom: Iron-bound" in view._rooms_text()

        await _pick_first_and_open_editor(
            pilot, app, "section-lab-items", NamedDescriptionPromptScreen
        )
        assert (
            app.screen.query_one("#input-named-desc-name", Input).value
            == "Silver Mirror"
        )
        app.screen.query_one("#input-named-desc-description", Input).value = "Cracked"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert "Silver Mirror: Cracked" in view._items_text()

    lab = storage.load_saga("test_saga").laboratories[0]
    assert lab.rooms == [NamedDescription(name="Strongroom", description="Iron-bound")]
    assert lab.inventory_items == [
        NamedDescription(name="Silver Mirror", description="Cracked")
    ]


async def test_edit_lab_raw_vis_changes_pawns_and_merges_on_art_change():
    storage.save_saga(_saga_with_populated_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)

        # First picker entry is "aquam" (entries are sorted by Art).
        await _pick_first_and_open_editor(
            pilot, app, "section-lab-raw-vis", RawVisPromptScreen
        )
        assert app.screen.query_one("#select-vis-art", Select).value == "aquam"
        assert app.screen.query_one("#input-vis-pawns", Input).value == "2"
        app.screen.query_one("#input-vis-pawns", Input).value = "7"
        app.screen.query_one("#btn-create", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

        # Re-point the same entry at an Art that's already held: it merges.
        await _pick_first_and_open_editor(
            pilot, app, "section-lab-raw-vis", RawVisPromptScreen
        )
        app.screen.query_one("#select-vis-art", Select).value = "ignem"
        app.screen.query_one("#btn-create", Button).press()
        await pilot.pause()

    lab = storage.load_saga("test_saga").laboratories[0]
    assert lab.raw_vis == {"ignem": 11}


async def test_edit_diary_entry():
    storage.save_saga(_saga_with_populated_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)

        await _pick_first_and_open_editor(
            pilot, app, "tab-lab-diary", DiaryEntryPromptScreen
        )
        assert app.screen.query_one("#input-diary-year", Input).value == "1220"
        assert app.screen.query_one("#select-diary-season", Select).value == "Spring"
        assert app.screen.query_one("#input-diary-name", Input).value == "Studied"
        app.screen.query_one("#select-diary-season", Select).value = "Winter"
        app.screen.query_one("#input-diary-details", Input).value = "Revised."
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        text = app.screen._laboratory_sheet_view._diary_text()
        assert "1220 Winter -- Studied" in text
        assert "Revised." in text

    assert storage.load_saga("test_saga").laboratories[0].diary == [
        DiaryEntry(year=1220, season="Winter", name="Studied", details="Revised.")
    ]


async def test_editing_an_empty_lab_list_or_cancelling_changes_nothing():
    storage.save_saga(_saga_with_populated_laboratory())
    bare = _saga_with_bare_laboratory()

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)

        # Cancelling the picker leaves the entry alone.
        await _open_lab_section(pilot, app, "section-lab-specialties")
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

        # Cancelling the editor does too.
        await _pick_first_and_open_editor(
            pilot, app, "section-lab-specialties", ItemAddScreen
        )
        app.screen.query_one("#input-item", Input).value = "Changed"
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    assert storage.load_saga("test_saga").laboratories[0].specialties == ["Ignem"]

    # Nothing to edit: a notification, not a dialog.
    storage.save_saga(bare)
    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        await _open_lab_section(pilot, app, "section-lab-specialties")
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)


async def test_lab_identity_shows_aura_breakdown_and_modifier_is_editable():
    saga = _saga_with_bare_laboratory()
    saga.covenants[0].aura = 3
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view
        assert "Aura: 3 (covenant) +0 (modifier) = 3" in view._identity_text()

        for modifier, expected in (
            ("2", "+2 (modifier) = 5"),
            ("-1", "-1 (modifier) = 2"),
        ):
            await _open_lab_section(pilot, app, "section-lab-identity")
            await pilot.press("e")
            await pilot.pause()
            assert isinstance(app.screen, EditLabIdentityScreen)
            app.screen.query_one("#input-lab-aura-modifier", Input).value = modifier
            app.screen.query_one("#btn-save", Button).press()
            await pilot.pause()
            assert expected in view._identity_text()

    assert storage.load_saga("test_saga").laboratories[0].aura_modifier == -1


async def test_lab_characteristics_numbers_are_coloured_by_sign():
    saga = _saga_with_bare_laboratory()
    saga.laboratories[0].characteristics = LabCharacteristics(
        size=1, refinement=2, safety=-3
    )
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view

        table = view._characteristics_table_text()
        assert re.search(r"Size:\s+\[green\]\+1\[/\]", table)  # positive
        assert re.search(r"Safety:\s+\[red\]-3\[/\]", table)  # negative
        assert re.search(r"Upkeep:\s+\[cyan\]\+0\[/\]", table)  # zero

        derived = view._characteristics_derived_text()
        assert "Occupied Size: [red]-2[/]" in derived
        assert re.search(r"Free Virtues:\s+\[green\]3\[/\]", derived)
        assert re.search(r"Base Safety:\s+\[green\]2\[/\]", derived)


async def test_lab_edit_dialogs_fit_a_small_terminal():
    """Save/Cancel must be on-screen at 80x24 for the roomier lab dialogs."""
    storage.save_saga(_saga_with_populated_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _select_laboratory(pilot, app)

        def assert_buttons_on_screen(*ids: str) -> None:
            for button_id in ids:
                region = app.screen.query_one(button_id, Button).region
                assert region.height > 0, button_id
                assert region.bottom <= 24, (type(app.screen).__name__, button_id)

        await _open_lab_section(pilot, app, "section-lab-identity")
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditLabIdentityScreen)
        assert_buttons_on_screen("#btn-save", "#btn-cancel")
        await pilot.press("escape")
        await pilot.pause()

        await _pick_first_and_open_editor(
            pilot, app, "tab-lab-diary", DiaryEntryPromptScreen
        )
        assert_buttons_on_screen("#btn-save", "#btn-cancel")


# -- Covenant sheet + saga time ------------------------------------------------

_COVENANT_TABS = (
    "tab-cov-attributes",
    "tab-cov-inhabitants",
    "tab-cov-possessions",
    "tab-cov-economics",
    "tab-cov-library",
    "tab-cov-diary",
)


def _saga_with_configured_covenant() -> Saga:
    saga = _saga_with_bare_laboratory()
    saga.name = "Pushing the Bounds"
    saga.storyguide = "Hedda"
    saga.current_season = "Spring"
    saga.current_year = 1220
    cov = saga.covenants[0]
    cov.tribunal = "Rhine"
    cov.year_founded = 1100
    cov.aegis_of_the_hearth = 2
    cov.aegis_penetration = 1
    cov.living_conditions_magi = 3
    cov.living_conditions_mundane = -1
    cov.aura = 4
    cov.covenant_season = "Summer"
    return saga


def test_covenant_new_fields_default_for_pre_existing_saves():
    covenant = Covenant(id="cov1", saga_id="s", name="Old Save")
    assert covenant.tribunal == ""
    assert covenant.year_founded is None
    assert covenant.aegis_of_the_hearth == 0
    assert covenant.aegis_penetration == 0
    assert covenant.living_conditions_magi == 0
    assert covenant.living_conditions_mundane == 0
    assert covenant.aura == 0
    assert covenant.covenant_season == "Spring"


async def test_covenant_sheet_has_info_panel_and_six_tabs():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        assert view is not None

        tabs = view.query_one(TabbedContent)
        assert [pane.id for pane in tabs.query(TabPane)] == list(_COVENANT_TABS)
        assert tabs.active == "tab-cov-attributes"

        def plain(text: str) -> str:
            return re.sub(r"\[/?[a-z]*\]", "", text)

        left = plain(view._info_left_text())
        right = plain(view._info_right_text())
        # Saga-inherited values...
        assert re.search(r"Saga:\s+Pushing the Bounds", left)
        assert re.search(r"Storyguide:\s+Hedda", left)
        assert re.search(r"Current Season:\s+Spring", right)
        assert re.search(r"Current Year:\s+1220", right)
        # ...and the covenant's own.
        assert re.search(r"Year Founded:\s+1100", left)
        assert re.search(r"Aegis of the Hearth:\s+2", left)
        assert re.search(r"Living Conditions \(Magi\):\s+3", left)
        assert re.search(r"Aura:\s+4", left)
        assert re.search(r"Tribunal:\s+Rhine", right)
        assert re.search(r"Aegis' Penetration:\s+1", right)
        assert re.search(r"Living Conditions \(Mundane\):\s+-1", right)
        assert re.search(r"Covenant Season:\s+Summer", right)


async def test_covenant_info_panel_layout_is_stable_across_tabs():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        tabbed = view.query_one(TabbedContent)

        for tab_id in _COVENANT_TABS:
            tabbed.active = tab_id
            await pilot.pause()

            info = view.query_one("#section-cov-info").region
            left = view.query_one("#cov-info-left").region
            right = view.query_one("#cov-info-right").region
            assert left.right <= right.x, tab_id  # two columns, side by side
            assert left.y == right.y, tab_id
            assert info.y == view.region.y, tab_id
            # Tab bar directly under the panel; body stays inside the sheet.
            assert tabbed.region.y == info.bottom, tab_id
            assert tabbed.region.bottom <= view.region.bottom, tab_id


async def test_opening_a_covenant_focuses_info_panel_so_edit_hotkey_works():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        assert app.screen._active_section() == "section-cov-info"

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditCovenantScreen)
        await pilot.press("escape")
        await pilot.pause()

        # Still available after switching to any other tab.
        view = app.screen._covenant_sheet_view
        view.query_one(TabbedContent).active = "tab-cov-economics"
        await pilot.pause()
        assert app.screen._active_section() == "section-cov-info"
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditCovenantScreen)
        await pilot.press("escape")
        await pilot.pause()

        # And via the button.
        view.query_one("#btn-cov-edit", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, EditCovenantScreen)


async def test_edit_covenant_saves_fields_and_labs_inherit_the_aura():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await pilot.press("e")
        await pilot.pause()
        dialog = app.screen
        assert isinstance(dialog, EditCovenantScreen)

        def set_input(field: str, value: str) -> None:
            dialog.query_one(f"#input-cov-{field}", Input).value = value

        set_input("name", "Dammerstein")
        set_input("tribunal", "Rhine")
        set_input("year-founded", "1100")
        set_input("aegis-of-the-hearth", "2")
        set_input("aegis-penetration", "1")
        set_input("living-conditions-magi", "1")
        set_input("living-conditions-mundane", "-2")
        set_input("aura", "3")
        dialog.query_one("#select-cov-season", Select).value = "Autumn"
        dialog.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

        view = app.screen._covenant_sheet_view
        assert view.query_one("#section-cov-info", Collapsible).title == "Dammerstein"
        assert "Aura" in view._info_left_text()

        # The lab in this covenant inherits the new base aura.
        await _select(pilot, app, ("laboratory", "lab1"))
        text = app.screen._laboratory_sheet_view._identity_text()
        assert "Aura: 3 (covenant) +0 (modifier) = 3" in text

    cov = storage.load_saga("test_saga").covenants[0]
    assert (cov.name, cov.tribunal, cov.year_founded) == ("Dammerstein", "Rhine", 1100)
    assert (cov.aegis_of_the_hearth, cov.aegis_penetration) == (2, 1)
    assert (cov.living_conditions_magi, cov.living_conditions_mundane) == (1, -2)
    assert (cov.aura, cov.covenant_season) == (3, "Autumn")


async def test_edit_covenant_requires_name_and_allows_blank_year_founded():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await pilot.press("e")
        await pilot.pause()
        dialog = app.screen

        dialog.query_one("#input-cov-name", Input).value = "  "
        dialog.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, EditCovenantScreen)  # refused

        dialog.query_one("#input-cov-name", Input).value = "Kept"
        dialog.query_one("#input-cov-year-founded", Input).value = ""
        dialog.query_one("#btn-save", Button).press()
        await pilot.pause()

    cov = storage.load_saga("test_saga").covenants[0]
    assert cov.name == "Kept"
    assert cov.year_founded is None


async def test_edit_covenant_dialog_fits_a_small_terminal():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _select_covenant(pilot, app)
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditCovenantScreen)
        for button_id in ("#btn-save", "#btn-cancel"):
            region = app.screen.query_one(button_id, Button).region
            assert region.height > 0, button_id
            assert region.bottom <= 24, button_id


async def test_advance_season_moves_the_whole_saga_forward():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        assert "Spring 1220" in app.screen.sub_title

        await pilot.press("t")
        await pilot.pause()
        assert isinstance(app.screen, AdvanceSeasonScreen)
        app.screen.query_one("#btn-advance", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

        # Header, the covenant's inherited panel values, and the saga file.
        assert "Summer 1220" in app.screen.sub_title
        right = app.screen._covenant_sheet_view._info_right_text()
        assert "Summer" in right
        assert "1220" in right

    saga = storage.load_saga("test_saga")
    assert (saga.current_season, saga.current_year) == ("Summer", 1220)


async def test_advancing_past_winter_rolls_the_year_and_cancel_changes_nothing():
    saga = _saga_with_configured_covenant()
    saga.current_season = "Winter"
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _open_workspace(pilot)  # saga level: 't' works from anywhere

        await pilot.press("t")
        await pilot.pause()
        assert isinstance(app.screen, AdvanceSeasonScreen)
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)
        assert "Winter 1220" in app.screen.sub_title

        await pilot.press("t")
        await pilot.pause()
        app.screen.query_one("#btn-advance", Button).press()
        await pilot.pause()
        assert "Spring 1221" in app.screen.sub_title

    saga = storage.load_saga("test_saga")
    assert (saga.current_season, saga.current_year) == ("Spring", 1221)


async def test_lab_diary_entries_default_to_the_saga_current_season():
    saga = _saga_with_configured_covenant()
    saga.current_season = "Autumn"
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_laboratory(pilot, app)
        await _open_lab_section(pilot, app, "tab-lab-diary")
        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, DiaryEntryPromptScreen)
        assert app.screen.query_one("#select-diary-season", Select).value == "Autumn"
        assert app.screen.query_one("#input-diary-year", Input).value == "1220"


async def test_set_date_rolls_back_an_accidental_advance():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)

        # Advance by "mistake"...
        await pilot.press("t")
        await pilot.pause()
        app.screen.query_one("#btn-advance", Button).press()
        await pilot.pause()
        assert "Summer 1220" in app.screen.sub_title

        # ...then put it back with Set Date.
        await pilot.press("T")
        await pilot.pause()
        assert isinstance(app.screen, SetDateScreen)
        # Pre-filled with the current date.
        assert app.screen.query_one("#select-date-season", Select).value == "Summer"
        assert app.screen.query_one("#input-date-year", Input).value == "1220"
        app.screen.query_one("#select-date-season", Select).value = "Spring"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

        # Everything that inherits the calendar follows.
        assert "Spring 1220" in app.screen.sub_title
        right = app.screen._covenant_sheet_view._info_right_text()
        assert "Spring" in right

    saga = storage.load_saga("test_saga")
    assert (saga.current_season, saga.current_year) == ("Spring", 1220)


async def test_set_date_sets_an_arbitrary_date_from_the_saga_level():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _open_workspace(pilot)  # saga level
        await pilot.press("T")
        await pilot.pause()
        assert isinstance(app.screen, SetDateScreen)
        app.screen.query_one("#select-date-season", Select).value = "Winter"
        app.screen.query_one("#input-date-year", Input).value = "1195"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert "Winter 1195" in app.screen.sub_title
        # The saga summary pane (shown at saga level) refreshes too.
        detail = app.screen.query_one("#detail-pane")
        text = " ".join(str(static.render()) for static in detail.query(Static))
        assert "Current date: Winter 1195" in text

    saga = storage.load_saga("test_saga")
    assert (saga.current_season, saga.current_year) == ("Winter", 1195)


async def test_set_date_rejects_a_blank_year_and_cancel_changes_nothing():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _open_workspace(pilot)

        await pilot.press("T")
        await pilot.pause()
        app.screen.query_one("#input-date-year", Input).value = ""
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, SetDateScreen)  # refused, still open
        for button_id in ("#btn-save", "#btn-cancel"):
            region = app.screen.query_one(button_id, Button).region
            assert region.height > 0 and region.bottom <= 24, button_id

        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)
        assert "Spring 1220" in app.screen.sub_title

    saga = storage.load_saga("test_saga")
    assert (saga.current_season, saga.current_year) == ("Spring", 1220)


# -- Characters and labs without a covenant live under the saga ---------------


def _saga_with_two_covenants() -> Saga:
    saga = _saga_with_bare_laboratory()
    saga.covenants.append(Covenant(id="cov2", saga_id="test_saga", name="Fenghold"))
    return saga


def _parent_data(tree, data):
    node = _find_node(tree, data)
    assert node is not None, f"tree node with data={data!r} not found"
    return node.parent.data


async def test_no_unassigned_groups_when_everything_belongs_to_a_covenant():
    storage.save_saga(_saga_with_two_covenants())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_workspace(pilot)
        tree = app.screen.query_one("#nav-tree", Tree)
        assert _find_node(tree, ("character_group", None)) is None
        assert _find_node(tree, ("laboratory_group", None)) is None


async def test_unassigned_characters_and_labs_are_listed_under_the_saga():
    saga = _saga_with_two_covenants()
    saga.characters[0].covenant_id = None
    saga.laboratories[0].covenant_id = None
    saga.characters.append(
        Character(id="char2", name="Ghost", type="grog", covenant_id="gone")
    )  # points at a covenant that doesn't exist: treated as unassigned
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_workspace(pilot)
        tree = app.screen.query_one("#nav-tree", Tree)

        for kind in ("character_group", "laboratory_group"):
            node = _find_node(tree, (kind, None))
            assert node is not None
            assert node.parent is tree.root  # directly under the saga
        assert _parent_data(tree, ("character", "char1")) == ("character_group", None)
        assert _parent_data(tree, ("character", "char2")) == ("character_group", None)
        assert _parent_data(tree, ("laboratory", "lab1")) == (
            "laboratory_group",
            None,
        )
        assert "Unassigned Characters (2)" in str(
            _find_node(tree, ("character_group", None)).label
        )

        # The bug this fixes: they can actually be selected.
        await _select(pilot, app, ("character", "char1"))
        assert app.screen.selected_character.id == "char1"
        assert app.screen._character_sheet_view is not None
        await _select(pilot, app, ("laboratory", "lab1"))
        assert app.screen.selected_laboratory.id == "lab1"
        assert "Covenant: (none)" in app.screen._laboratory_sheet_view._identity_text()

        # The group nodes themselves are selectable and say what they are.
        await _select(pilot, app, ("character_group", None))
        assert app.screen.selected_kind == "character_group"
        assert app.screen.selected_covenant is None
        await _select(pilot, app, ("laboratory_group", None))
        assert app.screen.selected_kind == "laboratory_group"


async def test_character_can_be_moved_out_of_a_covenant_and_back():
    storage.save_saga(_saga_with_two_covenants())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        tree = app.screen.query_one("#nav-tree", Tree)
        assert _parent_data(tree, ("character", "char1")) == ("character_group", "cov1")

        async def set_covenant(value) -> None:
            await _open_section(pilot, app, "section-identity")
            await pilot.press("e")
            await pilot.pause()
            assert isinstance(app.screen, IdentityEditScreen)
            app.screen.query_one("#select-covenant", Select).value = value
            app.screen.query_one("#btn-save", Button).press()
            await pilot.pause()

        # Roll it back to "no covenant": it lands under the saga...
        await set_covenant(Select.NULL)
        tree = app.screen.query_one("#nav-tree", Tree)
        assert _parent_data(tree, ("character", "char1")) == ("character_group", None)
        assert app.screen.selected_covenant is None

        # ...and can be assigned to a different covenant from there.
        await set_covenant("cov2")
        tree = app.screen.query_one("#nav-tree", Tree)
        assert _parent_data(tree, ("character", "char1")) == ("character_group", "cov2")
        assert _find_node(tree, ("character_group", None)) is None  # group gone

    assert storage.load_saga("test_saga").characters[0].covenant_id == "cov2"


async def test_lab_can_be_created_unassigned_or_in_a_covenant():
    storage.save_saga(_saga_with_two_covenants())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_workspace(pilot)  # saga level: no covenant selected

        await pilot.press("l")
        await pilot.pause()
        assert isinstance(app.screen, LaboratoryCreateScreen)
        assert app.screen.query_one("#select-covenant", Select).value == Select.NULL
        app.screen.query_one("#input-name", Input).value = "Loose Lab"
        await pilot.click("#btn-create")
        await pilot.pause()
        assert app.screen.selected_laboratory.name == "Loose Lab"

        # With a covenant selected, the dialog defaults to it.
        await _select(pilot, app, ("covenant", "cov2"))
        await pilot.press("l")
        await pilot.pause()
        assert app.screen.query_one("#select-covenant", Select).value == "cov2"
        app.screen.query_one("#input-name", Input).value = "Fenghold Lab"
        await pilot.click("#btn-create")
        await pilot.pause()

        tree = app.screen.query_one("#nav-tree", Tree)
        assert _parent_data(tree, ("laboratory", "loose_lab")) == (
            "laboratory_group",
            None,
        )
        assert _parent_data(tree, ("laboratory", "fenghold_lab")) == (
            "laboratory_group",
            "cov2",
        )

    labs = {lab.id: lab for lab in storage.load_saga("test_saga").laboratories}
    assert labs["loose_lab"].covenant_id is None
    assert labs["fenghold_lab"].covenant_id == "cov2"


async def test_lab_can_be_moved_between_covenants_and_unassigned():
    saga = _saga_with_two_covenants()
    saga.covenants[0].aura = 3
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view
        assert "Aura: 3 (covenant)" in view._identity_text()

        async def set_covenant(value) -> None:
            await _open_lab_section(pilot, app, "section-lab-identity")
            await pilot.press("e")
            await pilot.pause()
            assert isinstance(app.screen, EditLabIdentityScreen)
            app.screen.query_one("#select-lab-covenant", Select).value = value
            app.screen.query_one("#btn-save", Button).press()
            await pilot.pause()

        await set_covenant("cov2")
        tree = app.screen.query_one("#nav-tree", Tree)
        assert _parent_data(tree, ("laboratory", "lab1")) == (
            "laboratory_group",
            "cov2",
        )
        text = view._identity_text()
        assert "Covenant: Fenghold" in text
        assert "Aura: 0 (covenant)" in text  # inherits the new covenant's aura

        await set_covenant(Select.NULL)
        tree = app.screen.query_one("#nav-tree", Tree)
        assert _parent_data(tree, ("laboratory", "lab1")) == ("laboratory_group", None)
        assert "Covenant: (none)" in view._identity_text()
        assert app.screen.selected_covenant is None

    assert storage.load_saga("test_saga").laboratories[0].covenant_id is None


async def test_aura_boons_raise_the_aura_labs_inherit_and_the_covenant_panel_shows_it():
    saga = _saga_with_configured_covenant()  # covenant aura 4
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_aura"),
        VirtueFlawInstance(vf_id="covbh_boon_minor_aura"),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        left = app.screen._covenant_sheet_view._info_left_text()
        assert "6 (base 4, +2 Boons)" in left

        # The covenant's lab inherits the raised value, not just the base.
        await _select(pilot, app, ("laboratory", "lab1"))
        text = app.screen._laboratory_sheet_view._identity_text()
        assert "Aura: 6 (covenant) +0 (modifier) = 6" in text


# -- Covenant Attributes tab: Description, Reputations, Boons & Hooks ---------


async def _open_cov_section(pilot, app, section_id: str) -> None:
    """Focus one of the covenant Attributes tab's sections, after letting the
    view's own initial focus settle (see _open_lab_section)."""
    view = app.screen._covenant_sheet_view
    assert view is not None, "no covenant sheet is currently shown"
    await _wait_until(pilot, lambda: view.initial_tab_seen)
    await pilot.pause()
    view.query_one(TabbedContent).active = "tab-cov-attributes"
    await pilot.pause()
    view.query_one(f"#{section_id}", Collapsible).query_one("CollapsibleTitle").focus()
    await pilot.pause()
    await _wait_until(pilot, lambda: app.screen._active_section() == section_id)


async def _choose_in_list(pilot, app, list_id: str, item_id: str) -> None:
    """Highlight and activate one entry of a picker list by item id (it may
    be off-screen, so no pixel clicking)."""
    list_view = app.screen.query_one(f"#{list_id}", ListView)
    for index, item in enumerate(list_view.children):
        if item.id == item_id:
            list_view.index = index
            break
    else:
        raise AssertionError(f"{item_id!r} not found in {list_id!r}")
    await pilot.pause()
    await pilot.press("enter")
    await pilot.pause()


def _plain_title(section) -> str:
    """A Collapsible's title as displayed (colour markup stripped)."""
    return section.query_one("CollapsibleTitle").label.plain


def _title_styles(section) -> list[str]:
    """The styles actually applied to a Collapsible's rendered title."""
    return [
        str(span.style) for span in section.query_one("CollapsibleTitle").render().spans
    ]


def _bh_labels(view, kind: str) -> str:
    """The attached Boons or Hooks of `kind`, as displayed, joined."""
    return " | ".join(label for _, label in view._bh_entries(kind))


def _rep_labels(view) -> list[str]:
    """The covenant Reputations rows as displayed."""
    return [label for _, label in view._reputation_rows()]


async def _select_rep_row(pilot, app, list_index: int) -> None:
    view = app.screen._covenant_sheet_view
    await _wait_until(pilot, lambda: view.initial_tab_seen)
    await pilot.pause()
    reputations = view.query_one("#cov-reputations-list", SelectableList)
    reputations.focus()
    await pilot.pause()
    reputations.highlighted = list_index
    await pilot.pause()


def _catalog_count(kind: str) -> int:
    """How many entries of `kind` ("Boon"/"Hook") the covenant catalog has."""
    from ars_magica_manager import catalog as _catalog

    return sum(e.type == kind for e in _catalog.load_covenant_boon_hook_catalog())


def _pick_id(catalog_id: str) -> str:
    return f"covbhpick-{catalog_id}"


async def _add_boon_hook_via_picker(
    pilot,
    app,
    section_id: str,
    catalog_id: str,
    detail: str = "",
    description: str = "",
) -> None:
    covenant = app.screen.selected_covenant
    before = len(covenant.boons_hooks)
    await _open_cov_section(pilot, app, section_id)
    await pilot.press("a")
    await pilot.pause()
    assert isinstance(app.screen, CovenantBoonHookPickerScreen)
    await _choose_in_list(pilot, app, "covbh-picker-list", _pick_id(catalog_id))
    assert isinstance(app.screen, BoonHookDetailScreen)
    app.screen.query_one("#input-bh-detail", Input).value = detail
    if description:
        app.screen.query_one("#bh-description-text", TextArea).text = description
    app.screen.query_one("#btn-save", Button).press()
    await pilot.pause()
    assert isinstance(app.screen, WorkspaceScreen)
    # The dialog's result callback (which stores and saves the entry) can land
    # a beat after the screen switches back, so wait for the real state change.
    await _wait_until(pilot, lambda: len(covenant.boons_hooks) > before)
    await pilot.pause()


async def test_covenant_attributes_tab_has_its_four_sections():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        ids = [
            "section-cov-description",
            "section-cov-reputations",
            "section-cov-boons",
            "section-cov-hooks",
        ]
        sections = [view.query_one(f"#{i}", Collapsible) for i in ids]
        assert all(not section.collapsed for section in sections)
        assert _plain_title(sections[2]) == "Boons (0 pts)"
        assert _plain_title(sections[3]) == "Hooks (0 pts)"

        # Boons and Hooks sit side by side, like the reference sheet.
        boons, hooks = sections[2].region, sections[3].region
        assert boons.right <= hooks.x
        assert boons.y == hooks.y


async def test_edit_covenant_description_is_multi_line_and_persists():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].notes = "A border covenant"
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        assert "A border covenant" in view._description_text()

        await _open_cov_section(pilot, app, "section-cov-description")
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditCovenantDescriptionScreen)
        area = app.screen.query_one(TextArea)
        assert area.text == "A border covenant"  # pre-filled
        area.text = "First line.\nSecond line [with brackets]."
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert "Second line" in view._description_text()

        # Clearing it shows the empty state.
        await pilot.press("e")
        await pilot.pause()
        app.screen.query_one(TextArea).text = ""
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert view._description_text() == "(no description)"

    assert storage.load_saga("test_saga").covenants[0].notes == ""


async def test_covenant_reputations_add_edit_remove_within_range():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        assert _rep_labels(view) == []
        await _open_cov_section(pilot, app, "section-cov-reputations")

        async def submit(name: str, score: str) -> None:
            app.screen.query_one("#input-trait-name", Input).value = name
            app.screen.query_one("#input-trait-score", Input).value = score
            app.screen.query_one("#btn-save", Button).press()
            await pilot.pause()

        # Add -- out-of-range scores are refused, the dialog stays open.
        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, ScoredTraitPromptScreen)
        await submit("Feared by nobles", "4")
        assert isinstance(app.screen, ScoredTraitPromptScreen)
        await submit("Feared by nobles", "-4")
        assert isinstance(app.screen, ScoredTraitPromptScreen)
        await submit("Feared by nobles", "3")
        assert isinstance(app.screen, WorkspaceScreen)
        await pilot.press("a")
        await pilot.pause()
        await submit("Well liked", "-3")
        await _wait_until(pilot, lambda: len(_rep_labels(view)) == 2)
        assert _rep_labels(view) == ["Feared by nobles: +3", "Well liked: -3"]

        # Edit the first one (pre-filled), then remove the second.
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert app.screen.query_one("#input-trait-name", Input).value == (
            "Feared by nobles"
        )
        await submit("Feared by nobles", "1")
        await _wait_until(pilot, lambda: "Feared by nobles: +1" in _rep_labels(view))

        # Nothing is selected, so 'A' asks which one, then confirms.
        await pilot.press("A")
        await pilot.pause()
        await pilot.press("down")
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await _wait_until(pilot, lambda: len(_rep_labels(view)) == 1)
        assert _rep_labels(view) == ["Feared by nobles: +1"]

    reputations = storage.load_saga("test_saga").covenants[0].reputations
    assert [(r.name, r.score) for r in reputations] == [("Feared by nobles", 1)]


async def test_boon_picker_lists_only_boons_with_notes_and_asks_for_a_blank_detail():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _open_cov_section(pilot, app, "section-cov-boons")
        await pilot.press("a")
        await pilot.pause()
        picker = app.screen
        assert isinstance(picker, CovenantBoonHookPickerScreen)

        items = list(picker.query_one("#covbh-picker-list", ListView).children)
        assert len(items) == _catalog_count("Boon")  # every Boon, no Hooks
        assert all("covbh_boon_" in (item.id or "") for item in items)

        labels = {item.id: str(item.query_one(Label).render()) for item in items}
        shell = labels[_pick_id("covbh_boon_minor_shell_keep")]
        assert "requires: Castle" in shell
        assert "not with: Road, Urban" in labels[_pick_id("covbh_boon_minor_seclusion")]

        # Choosing one opens the detail prompt, blank by default.
        await _choose_in_list(
            pilot, app, "covbh-picker-list", _pick_id("covbh_boon_minor_edifice")
        )
        assert isinstance(app.screen, BoonHookDetailScreen)
        assert app.screen.query_one("#input-bh-detail", Input).value == ""

        # Cancelling the detail prompt goes back to the picker; nothing added.
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, CovenantBoonHookPickerScreen)
        await pilot.press("escape")
        await pilot.pause()

    assert storage.load_saga("test_saga").covenants[0].boons_hooks == []


async def test_boons_and_hooks_totals_details_and_aura():
    storage.save_saga(_saga_with_configured_covenant())  # covenant aura 4

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        boons = view.query_one("#section-cov-boons", Collapsible)
        hooks = view.query_one("#section-cov-hooks", Collapsible)

        await _add_boon_hook_via_picker(
            pilot,
            app,
            "section-cov-boons",
            "covbh_boon_minor_edifice",
            "Obsidian Crucible",
        )
        assert "Edifice - Obsidian Crucible" in _bh_labels(view, "Boon")
        assert _plain_title(boons) == "Boons (1 pt)"

        await _add_boon_hook_via_picker(
            pilot, app, "section-cov-boons", "covbh_boon_minor_aura"
        )
        await _add_boon_hook_via_picker(
            pilot, app, "section-cov-boons", "covbh_boon_major_wealth"
        )
        assert _plain_title(boons) == "Boons (5 pts)"
        assert "Wealth" in _bh_labels(view, "Boon")  # no detail: just the name
        assert "Wealth -" not in _bh_labels(view, "Boon")
        # The Aura Boon shows up in the info panel straight away.
        assert "5 (base 4, +1 Boons)" in view._info_left_text()

        await _add_boon_hook_via_picker(
            pilot,
            app,
            "section-cov-hooks",
            "covbh_hook_minor_contested_resource",
            "Whispering Well (Vim Vis)",
        )
        await _add_boon_hook_via_picker(
            pilot, app, "section-cov-hooks", "covbh_hook_major_castle"
        )
        # Hooks show the (positive) points they provide.
        assert _plain_title(hooks) == "Hooks (4 pts)"
        assert "Contested Resource - Whispering Well (Vim Vis)" in _bh_labels(
            view, "Hook"
        )
        assert "Edifice" not in _bh_labels(view, "Hook")

    cov = storage.load_saga("test_saga").covenants[0]
    assert [bh.vf_id for bh in cov.boons_hooks] == [
        "covbh_boon_minor_edifice",
        "covbh_boon_minor_aura",
        "covbh_boon_major_wealth",
        "covbh_hook_minor_contested_resource",
        "covbh_hook_major_castle",
    ]
    assert cov.boons_hooks[0].params == {"detail": "Obsidian Crucible"}
    assert cov.boons_hooks[1].params == {}  # blank detail stores nothing


async def test_picker_marks_taken_entries_but_still_offers_them():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_edifice", params={"detail": "A"}),
        VirtueFlawInstance(vf_id="covbh_boon_minor_edifice", params={"detail": "B"}),
        VirtueFlawInstance(vf_id="covbh_boon_minor_wealth"),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _open_cov_section(pilot, app, "section-cov-boons")
        await pilot.press("a")
        await pilot.pause()
        items = {
            item.id: str(item.query_one(Label).render())
            for item in app.screen.query_one("#covbh-picker-list", ListView).children
        }
        assert len(items) == _catalog_count("Boon")  # nothing is hidden
        assert "(taken x2)" in items[_pick_id("covbh_boon_minor_edifice")]
        assert "(taken x1)" in items[_pick_id("covbh_boon_minor_wealth")]
        assert "taken" not in items[_pick_id("covbh_boon_minor_regio")]

        # A second Edifice can be taken (your sheet has two).
        await _choose_in_list(
            pilot, app, "covbh-picker-list", _pick_id("covbh_boon_minor_edifice")
        )
        app.screen.query_one("#input-bh-detail", Input).value = "C"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

    boons = storage.load_saga("test_saga").covenants[0].boons_hooks
    assert [bh.params.get("detail") for bh in boons] == ["A", "B", None, "C"]


async def test_edit_and_remove_target_the_right_boon_or_hook_when_interleaved():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_hook_minor_rival"),
        VirtueFlawInstance(vf_id="covbh_boon_minor_edifice", params={"detail": "A"}),
        VirtueFlawInstance(vf_id="covbh_hook_minor_road"),
        VirtueFlawInstance(vf_id="covbh_boon_minor_wealth", params={"detail": "B"}),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view

        # Edit the SECOND Boon's detail (Wealth), which sits at index 3.
        await _open_cov_section(pilot, app, "section-cov-boons")
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("down")
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, BoonHookDetailScreen)
        assert app.screen.query_one("#input-bh-detail", Input).value == "B"  # prefilled
        app.screen.query_one("#input-bh-detail", Input).value = ""  # clear it
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert "Wealth" in _bh_labels(view, "Boon")
        assert "Wealth -" not in _bh_labels(view, "Boon")  # no detail any more
        assert "Edifice - A" in _bh_labels(view, "Boon")  # the other Boon untouched

        # Remove the SECOND Hook (Road), index 2 -- through the picker (nothing
        # is selected), then the delete confirmation.
        await _open_cov_section(pilot, app, "section-cov-hooks")
        await pilot.press("A")
        await pilot.pause()
        await pilot.press("down")
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await pilot.pause()

    cov = storage.load_saga("test_saga").covenants[0]
    assert [bh.vf_id for bh in cov.boons_hooks] == [
        "covbh_hook_minor_rival",
        "covbh_boon_minor_edifice",
        "covbh_boon_minor_wealth",
    ]
    assert cov.boons_hooks[2].params == {}
    assert cov.boons_hooks[1].params == {"detail": "A"}


async def test_switching_back_to_the_attributes_tab_focuses_its_first_section():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        await _wait_until(pilot, lambda: view.initial_tab_seen)
        await pilot.pause()

        tabbed = view.query_one(TabbedContent)
        tabbed.active = "tab-cov-economics"  # a flat tab
        await pilot.pause()
        assert app.screen._active_section() == "section-cov-info"  # fallback

        tabbed.active = "tab-cov-attributes"
        await _wait_until(
            pilot, lambda: app.screen._active_section() == "section-cov-description"
        )
        assert app.screen._active_section() == "section-cov-description"


async def test_covenant_attributes_dialogs_fit_a_small_terminal():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _select_covenant(pilot, app)

        def buttons_on_screen() -> None:
            for button in app.screen.query(Button):
                region = button.region
                assert region.height > 0 and region.bottom <= 24, (
                    type(app.screen).__name__,
                    button.id,
                )

        await _open_cov_section(pilot, app, "section-cov-description")
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditCovenantDescriptionScreen)
        buttons_on_screen()
        await pilot.press("escape")
        await pilot.pause()

        await _open_cov_section(pilot, app, "section-cov-boons")
        await pilot.press("a")
        await pilot.pause()
        await _choose_in_list(
            pilot, app, "covbh-picker-list", _pick_id("covbh_boon_minor_wealth")
        )
        assert isinstance(app.screen, BoonHookDetailScreen)
        buttons_on_screen()


# -- Boons/Hooks: colour-coded totals, selector rows and the details panel -----


def _saga_with_boons_and_hooks(*ids: str) -> Saga:
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [VirtueFlawInstance(vf_id=i) for i in ids]
    return saga


async def test_boon_and_hook_totals_are_coloured_by_how_they_compare():
    # (attached entries, expected colour, expected plain titles)
    cases = [
        ((), "green", ("Boons (0 pts)", "Hooks (0 pts)")),  # equal
        (
            ("covbh_boon_minor_wealth", "covbh_hook_major_castle"),
            "cyan",  # Boons (1) < Hooks (3)
            ("Boons (1 pt)", "Hooks (3 pts)"),
        ),
        (
            ("covbh_boon_major_wealth", "covbh_hook_minor_rival"),
            "red",  # Boons (3) > Hooks (1)
            ("Boons (3 pts)", "Hooks (1 pt)"),
        ),
        (
            ("covbh_boon_major_wealth", "covbh_hook_major_castle"),
            "green",  # equal, non-zero
            ("Boons (3 pts)", "Hooks (3 pts)"),
        ),
    ]
    for attached, colour, plain in cases:
        storage.save_saga(_saga_with_boons_and_hooks(*attached))
        app = ArsMagicaManagerApp()
        async with app.run_test(size=(140, 50)) as pilot:
            await _select_covenant(pilot, app)
            view = app.screen._covenant_sheet_view
            boons = view.query_one("#section-cov-boons", Collapsible)
            hooks = view.query_one("#section-cov-hooks", Collapsible)
            # Both share the colour, and only the parenthesised total has it.
            assert boons.title == f"Boons [{colour}]{plain[0][6:]}[/]", attached
            assert hooks.title == f"Hooks [{colour}]{plain[1][6:]}[/]", attached
            assert (_plain_title(boons), _plain_title(hooks)) == plain


async def test_totals_recolour_when_a_hook_is_added():
    storage.save_saga(_saga_with_boons_and_hooks("covbh_boon_minor_wealth"))

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        boons = view.query_one("#section-cov-boons", Collapsible)
        hooks = view.query_one("#section-cov-hooks", Collapsible)
        assert "[red]" in boons.title and "[red]" in hooks.title  # 1 > 0

        await _add_boon_hook_via_picker(
            pilot, app, "section-cov-hooks", "covbh_hook_minor_rival"
        )
        assert "[green]" in boons.title and "[green]" in hooks.title  # 1 == 1

        await _add_boon_hook_via_picker(
            pilot, app, "section-cov-hooks", "covbh_hook_minor_favors"
        )
        # Adding a Hook re-coloured the Boons title too (1 < 2).
        assert "[cyan]" in boons.title and "[cyan]" in hooks.title
        # ...and what is actually painted follows, including the Hooks total
        # whose text ("(2 pts)") changed but which must also recolour when only
        # the colour changes (Textual compares label text, not style).
        assert "cyan" in _title_styles(boons) and "cyan" in _title_styles(hooks)


async def test_a_colour_only_change_repaints_the_title():
    # Hooks stay at 3 points throughout; only the Boons change, so the Hooks
    # title text is identical while its colour must change.
    storage.save_saga(_saga_with_boons_and_hooks("covbh_hook_major_castle"))

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        hooks = view.query_one("#section-cov-hooks", Collapsible)
        assert "green" not in _title_styles(hooks)
        assert "cyan" in _title_styles(hooks)  # Boons 0 < Hooks 3

        for boon in ("covbh_boon_major_wealth", "covbh_boon_minor_aura"):
            await _add_boon_hook_via_picker(pilot, app, "section-cov-boons", boon)
            plain = _plain_title(hooks)
            assert plain == "Hooks (3 pts)"  # text never changed
        # Boons (4) > Hooks (3): red, though the Hooks text stayed identical.
        assert "red" in _title_styles(hooks)
        assert "cyan" not in _title_styles(hooks)


async def test_boon_hook_rows_have_a_selector_and_fill_the_details_panel():
    storage.save_saga(
        _saga_with_boons_and_hooks(
            "covbh_boon_minor_aura",
            "covbh_boon_minor_edifice",
            "covbh_hook_minor_favors",
            "covbh_boon_minor_shell_keep",
            "covbh_hook_major_castle",
        )
    )

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        boon_list = view.query_one("#cov-boons-list", OptionList)
        hook_list = view.query_one("#cov-hooks-list", OptionList)
        panel = view.query_one("#cov-bh-info", Static)

        def prompts(option_list) -> list[str]:
            return [str(o.prompt) for o in option_list.options]

        # Every row has an (unselected) selector; the panel invites a choice.
        assert len(boon_list.options) == 3 and len(hook_list.options) == 2
        assert all("○" in p and "●" not in p for p in prompts(boon_list))
        assert "Select a Boon or Hook" in str(panel.render())

        # Highlight the second Boon: its marker fills in, the panel shows it.
        boon_list.highlighted = 1
        await pilot.pause()
        assert "●" in prompts(boon_list)[1]
        assert "○" in prompts(boon_list)[0] and "○" in prompts(boon_list)[2]
        text = str(panel.render())
        assert "Name: Edifice" in text
        assert "Type: Fortifications" in text  # the book's type of Boon/Hook
        assert "Tier: Minor Boon (1 pt)" in text
        assert "major building erected to inspire awe" in text  # the rules text

        # Highlighting a Hook moves the selection over: one marker in total.
        hook_list.highlighted = 1
        await pilot.pause()
        assert not any("●" in p for p in prompts(boon_list))
        assert "●" in prompts(hook_list)[1]
        text = str(panel.render())
        assert "Name: Castle" in text
        assert "Type: Fortifications" in text
        assert "Tier: Major Hook (3 pts)" in text


async def test_details_panel_shows_prerequisites_exclusions_and_repeatability():
    storage.save_saga(
        _saga_with_boons_and_hooks(
            "covbh_boon_minor_shell_keep",
            "covbh_boon_minor_seclusion",
            "covbh_boon_minor_aura",
            "covbh_boon_minor_edifice",
        )
    )

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view

        def info(index: int) -> str:
            # entry index -> text with the colour/bold markup stripped
            return re.sub(r"\[/?[a-z]*\]", "", view._bh_info_text(index))

        assert "Requires: Castle" in info(0)
        assert "Not with: Road, Urban" in info(1)
        assert "May be taken more than once" in info(2)
        assert "Requires" not in info(3) and "Not with" not in info(3)
        assert "May be taken" not in info(3)


async def test_details_panel_shows_the_detail_and_escapes_markup():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(
            vf_id="covbh_boon_minor_edifice", params={"detail": "The [Tower] of Iris"}
        )
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        view.query_one("#cov-boons-list", OptionList).highlighted = 0
        await pilot.pause()
        text = str(view.query_one("#cov-bh-info", Static).render())
        assert "Name: Edifice - The [Tower] of Iris" in text  # brackets survive


async def test_empty_boon_and_hook_lists_show_a_disabled_placeholder():
    storage.save_saga(_saga_with_boons_and_hooks())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        for list_id in ("cov-boons-list", "cov-hooks-list"):
            option_list = view.query_one(f"#{list_id}", OptionList)
            assert len(option_list.options) == 1
            assert option_list.options[0].disabled
            assert "none recorded" in str(option_list.options[0].prompt)


async def test_boon_list_works_from_the_keyboard_and_keeps_add_remove_dispatch():
    storage.save_saga(
        _saga_with_boons_and_hooks("covbh_boon_minor_aura", "covbh_boon_minor_wealth")
    )

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        await _wait_until(pilot, lambda: view.initial_tab_seen)
        await pilot.pause()

        boon_list = view.query_one("#cov-boons-list", OptionList)
        boon_list.focus()
        await pilot.pause()
        # Focus inside the Boons section: 'a' still adds a Boon (not a Hook).
        assert app.screen._active_section() == "section-cov-boons"

        await pilot.press("down")
        await pilot.pause()
        assert boon_list.highlighted is not None
        first = boon_list.highlighted
        await pilot.press("down")
        await pilot.pause()
        assert boon_list.highlighted != first
        assert "Name:" in str(view.query_one("#cov-bh-info", Static).render())

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, CovenantBoonHookPickerScreen)
        assert app.screen.kind == "Boon"


async def test_adding_a_boon_rebuilds_the_list_and_resets_the_panel():
    storage.save_saga(_saga_with_boons_and_hooks("covbh_boon_minor_aura"))

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        boon_list = view.query_one("#cov-boons-list", OptionList)
        boon_list.highlighted = 0
        await pilot.pause()
        assert "Name: Aura" in str(view.query_one("#cov-bh-info", Static).render())

        await _add_boon_hook_via_picker(
            pilot, app, "section-cov-boons", "covbh_boon_minor_wealth"
        )
        assert len(boon_list.options) == 2
        assert all("○" in str(o.prompt) for o in boon_list.options)  # no stale marker
        assert "Select a Boon or Hook" in str(
            view.query_one("#cov-bh-info", Static).render()
        )


# -- Boon/Hook Description, and e / A acting on the selected row ---------------


async def _select_bh_row(pilot, app, kind: str, list_index: int) -> None:
    """Select a row of the Boons/Hooks list the way a user does: focus the
    list and highlight the row."""
    view = app.screen._covenant_sheet_view
    await _wait_until(pilot, lambda: view.initial_tab_seen)
    await pilot.pause()
    view.query_one("#section-cov-" + kind.lower() + "s")  # exists
    option_list = view.query_one(f"#cov-{kind.lower()}s-list", OptionList)
    option_list.focus()
    await pilot.pause()
    option_list.highlighted = list_index
    await pilot.pause()


def _panel_text(app) -> str:
    view = app.screen._covenant_sheet_view
    return str(view.query_one("#cov-bh-info", Static).render())


async def test_boon_hook_description_is_saved_and_leads_the_details_panel():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view

        await _add_boon_hook_via_picker(
            pilot,
            app,
            "section-cov-boons",
            "covbh_boon_minor_hidden_resources",
            detail="The Lost Library of the Founder",
            description="Accessible Value: 250 Build Points\n\nLocation: sealed [Muto] wall",
        )
        # Blank description on a second one stores nothing.
        await _add_boon_hook_via_picker(
            pilot, app, "section-cov-boons", "covbh_boon_minor_wealth"
        )

        cov = storage.load_saga("test_saga").covenants[0]
        assert cov.boons_hooks[0].params == {
            "detail": "The Lost Library of the Founder",
            "description": "Accessible Value: 250 Build Points\n\nLocation: sealed [Muto] wall",
        }
        assert cov.boons_hooks[1].params == {}

        # The list still shows only the one-line detail...
        assert "Hidden Resources - The Lost Library of the Founder" in _bh_labels(
            view, "Boon"
        )
        assert "Accessible Value" not in _bh_labels(view, "Boon")

        # ...and the panel shows the user's description BEFORE the rules.
        await _select_bh_row(pilot, app, "Boon", 0)
        text = _panel_text(app)
        assert "Description:" in text and "Rules:" in text
        assert text.index("Accessible Value: 250 Build Points") < text.index("Rules:")
        assert "sealed [Muto] wall" in text  # multi-line, brackets survive
        assert text.index("Description:") < text.index("The covenant has 250 Build")
        assert "Location:" in text

        # No description: no Description heading, just the rules.
        await _select_bh_row(pilot, app, "Boon", 1)
        text = _panel_text(app)
        assert "Description:" not in text
        assert "Rules:" in text


async def test_e_edits_the_selected_boon_directly_without_a_picker():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_edifice", params={"detail": "A"}),
        VirtueFlawInstance(
            vf_id="covbh_boon_minor_edifice",
            params={"detail": "B", "description": "Old text"},
        ),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _select_bh_row(pilot, app, "Boon", 1)  # the second Edifice

        await pilot.press("e")
        await pilot.pause()
        # Straight to the edit dialog for that row -- no "which one?" picker.
        assert isinstance(app.screen, BoonHookDetailScreen)
        assert app.screen.query_one("#input-bh-detail", Input).value == "B"
        assert app.screen.query_one("#bh-description-text", TextArea).text == "Old text"
        app.screen.query_one("#input-bh-detail", Input).value = "B2"
        app.screen.query_one("#bh-description-text", TextArea).text = "New\ntext"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

    boons = storage.load_saga("test_saga").covenants[0].boons_hooks
    assert boons[0].params == {"detail": "A"}  # untouched
    assert boons[1].params == {"detail": "B2", "description": "New\ntext"}


async def test_A_deletes_the_selected_item_only_after_confirmation():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_edifice", params={"detail": "A"}),
        VirtueFlawInstance(
            vf_id="covbh_boon_minor_edifice", params={"detail": "B [x]"}
        ),
        VirtueFlawInstance(vf_id="covbh_boon_minor_wealth"),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        await _select_bh_row(pilot, app, "Boon", 1)

        # Answering No (or Escape) keeps it.
        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert message == "Delete Edifice - B [x]?"  # brackets survive
        await pilot.press("n")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)
        assert len(view._bh_entries("Boon")) == 3

        await pilot.press("A")
        await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()
        assert len(view._bh_entries("Boon")) == 3

        # Yes deletes exactly the selected one, then the panel resets.
        await pilot.press("A")
        await pilot.pause()
        await pilot.press("y")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)
        assert [label for _, label in view._bh_entries("Boon")] == [
            "Edifice - A",
            "Wealth",
        ]
        assert "Select a Boon or Hook" in _panel_text(app)
        assert _plain_title(view.query_one("#section-cov-boons", Collapsible)) == (
            "Boons (2 pts)"
        )

    cov = storage.load_saga("test_saga").covenants[0]
    assert [bh.vf_id for bh in cov.boons_hooks] == [
        "covbh_boon_minor_edifice",
        "covbh_boon_minor_wealth",
    ]


async def test_delete_confirmation_defaults_to_no_so_a_stray_enter_is_safe():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_wealth")
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _select_bh_row(pilot, app, "Boon", 0)
        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        assert app.screen.focused is app.screen.query_one("#btn-no", Button)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    assert len(storage.load_saga("test_saga").covenants[0].boons_hooks) == 1


async def test_selection_in_the_other_list_or_none_falls_back_to_the_picker():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_wealth"),
        VirtueFlawInstance(vf_id="covbh_hook_minor_rival"),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)

        # A Boon is selected, but 'A' in the Hooks section isn't about it:
        # the picker asks which Hook, then confirms.
        await _select_bh_row(pilot, app, "Boon", 0)
        await _open_cov_section(pilot, app, "section-cov-hooks")
        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await pilot.pause()

    cov = storage.load_saga("test_saga").covenants[0]
    assert [bh.vf_id for bh in cov.boons_hooks] == ["covbh_boon_minor_wealth"]


async def test_boon_hook_detail_dialog_with_description_fits_a_small_terminal():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_wealth")
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _select_covenant(pilot, app)
        await _select_bh_row(pilot, app, "Boon", 0)
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, BoonHookDetailScreen)
        for button in app.screen.query(Button):
            region = button.region
            assert region.height > 0 and region.bottom <= 24, button.id
        await pilot.press("escape")
        await pilot.pause()

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        for button in app.screen.query(Button):
            region = button.region
            assert region.height > 0 and region.bottom <= 24, button.id


async def test_boon_hook_dialogs_hug_their_content_on_a_tall_terminal():
    """Regression: a bare Horizontal (defaults to 1fr) inside an auto-height
    dialog stretched it to fill the whole window."""
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_wealth")
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _select_covenant(pilot, app)
        await _select_bh_row(pilot, app, "Boon", 0)

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, BoonHookDetailScreen)
        assert app.screen.query_one("#bh-detail-dialog").region.height < 30
        await pilot.press("escape")
        await pilot.pause()

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        assert app.screen.query_one("#confirm-dialog").region.height < 12


# -- Covenant Reputations on the selectable-list pattern ----------------------


def _saga_with_reputations(*rows: tuple[str, int]) -> Saga:
    saga = _saga_with_configured_covenant()
    saga.covenants[0].reputations = [ScoredTrait(name=n, score=v) for n, v in rows]
    return saga


async def test_reputation_rows_are_selectable_and_independent_of_the_boon_panel():
    saga = _saga_with_reputations(("Feared", 2), ("Liked", -1), ("Known", 0))
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_wealth")
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        reputations = view.query_one("#cov-reputations-list", SelectableList)

        def prompts() -> list[str]:
            return [str(o.prompt) for o in reputations.options]

        assert len(reputations.options) == 3
        assert reputations.highlighted is None  # nothing chosen on open
        assert all("○" in p and "●" not in p for p in prompts())
        assert _rep_labels(view) == ["Feared: +2", "Liked: -1", "Known: +0"]

        # Choose a Boon first: the panel fills in.
        await _select_bh_row(pilot, app, "Boon", 0)
        assert "Name: Wealth" in _panel_text(app)

        # Choosing a Reputation moves ITS marker and leaves the Boon panel be.
        await _select_rep_row(pilot, app, 1)
        assert "●" in prompts()[1]
        assert "○" in prompts()[0] and "○" in prompts()[2]
        assert view.selected_reputation() == 1
        assert "Name: Wealth" in _panel_text(app)


async def test_e_edits_the_selected_reputation_directly():
    storage.save_saga(_saga_with_reputations(("Feared", 2), ("Liked", -1)))

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        await _select_rep_row(pilot, app, 1)

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, ScoredTraitPromptScreen)  # no picker first
        assert app.screen.query_one("#input-trait-name", Input).value == "Liked"
        assert app.screen.query_one("#input-trait-score", Input).value == "-1"
        app.screen.query_one("#input-trait-name", Input).value = "Well liked"
        app.screen.query_one("#input-trait-score", Input).value = "3"
        app.screen.query_one("#btn-save", Button).press()
        await _wait_until(pilot, lambda: "Well liked: +3" in _rep_labels(view))

    reputations = storage.load_saga("test_saga").covenants[0].reputations
    assert [(r.name, r.score) for r in reputations] == [
        ("Feared", 2),
        ("Well liked", 3),
    ]


async def test_A_deletes_the_selected_reputation_only_after_confirmation():
    storage.save_saga(
        _saga_with_reputations(("Feared", 2), ("Odd [name]", -1), ("Known", 0))
    )

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        await _select_rep_row(pilot, app, 1)

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert message == "Delete Odd [name]?"  # brackets survive
        await pilot.press("n")
        await pilot.pause()
        assert len(_rep_labels(view)) == 3

        await pilot.press("A")
        await pilot.pause()
        await pilot.press("y")
        await _wait_until(pilot, lambda: len(_rep_labels(view)) == 2)
        assert _rep_labels(view) == ["Feared: +2", "Known: +0"]
        assert view.selected_reputation() is None  # selection reset

    names = [r.name for r in storage.load_saga("test_saga").covenants[0].reputations]
    assert names == ["Feared", "Known"]


async def test_reputation_keys_work_from_the_list_and_fall_back_to_a_picker():
    storage.save_saga(_saga_with_reputations(("Feared", 2)))

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        await _wait_until(pilot, lambda: view.initial_tab_seen)
        await pilot.pause()

        # List focused, nothing chosen: the section still owns the keys.
        view.query_one("#cov-reputations-list", SelectableList).focus()
        await pilot.pause()
        assert app.screen._active_section() == "section-cov-reputations"
        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, ScoredTraitPromptScreen)
        assert app.screen._score_label() == "Score (-3 to +3)"
        await pilot.press("escape")
        await pilot.pause()

        # Nothing chosen: 'e' falls back to "which one?".
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)


# -- SelectableList, the reusable widget ------------------------------------


class _ListHarness(App):
    def __init__(self, rows) -> None:
        super().__init__()
        self._rows = rows
        self.chosen: list[int] = []

    def compose(self):
        yield SelectableList(self._rows, id="the-list")

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        self.chosen.append(event.data_index)


async def test_selectable_list_uses_data_indexes_and_a_single_marker():
    # Data indexes need not be contiguous (a filtered view of a bigger list).
    app = _ListHarness([(3, "alpha"), (7, "beta"), (9, "gamma")])
    async with app.run_test() as pilot:
        widget = app.query_one("#the-list", SelectableList)
        prompts = lambda: [str(o.prompt) for o in widget.options]

        assert widget.highlighted is None and widget.selected_data_index is None
        assert all("○" in p for p in prompts())

        widget.highlighted = 1
        await pilot.pause()
        assert app.chosen == [7]  # the data index, not the row position
        assert widget.selected_data_index == 7
        assert "●" in prompts()[1] and "●" not in prompts()[0] + prompts()[2]

        widget.highlighted = 2
        await pilot.pause()
        assert app.chosen == [7, 9]
        assert sum("●" in p for p in prompts()) == 1  # one marker at a time

        widget.clear_selection()
        await pilot.pause()
        assert widget.selected_data_index is None
        assert not any("●" in p for p in prompts())
        assert app.chosen == [7, 9]  # clearing posts nothing


async def test_selectable_list_set_rows_replaces_everything_and_handles_empty():
    app = _ListHarness([(0, "one"), (1, "two")])
    async with app.run_test() as pilot:
        widget = app.query_one("#the-list", SelectableList)
        widget.highlighted = 1
        await pilot.pause()
        assert widget.selected_data_index == 1

        widget.set_rows([(5, "five")])
        await pilot.pause()
        assert len(widget.options) == 1
        assert widget.selected_data_index is None  # selection cleared
        assert "○" in str(widget.options[0].prompt)  # no stale marker

        # Empty: one disabled placeholder that can't be chosen.
        widget.set_rows([])
        await pilot.pause()
        assert len(widget.options) == 1
        assert widget.options[0].disabled
        assert "none recorded" in str(widget.options[0].prompt)
        assert widget.selected_data_index is None
        assert app.chosen == [1]  # only the one real choice was ever posted


# -- Inline emphasis in user-written descriptions ----------------------------


def _styled_words(static) -> set[tuple[str, str]]:
    """(text, style) for every styled span of a rendered Static."""
    content = static.render()
    return {(content.plain[s.start : s.end], str(s.style)) for s in content.spans}


async def test_boon_hook_description_renders_bold_and_italic_in_the_panel():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(
            vf_id="covbh_boon_minor_hidden_resources",
            params={
                "description": (
                    "**Accessible Value:** 250 Build Points\n\n"
                    "**Location:** sealed *behind* a wall in [The Tower]"
                )
            },
        )
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _select_bh_row(pilot, app, "Boon", 0)
        panel = app.screen._covenant_sheet_view.query_one("#cov-bh-info", Static)

        plain = str(panel.render())
        assert "**" not in plain and "*behind*" not in plain  # markers consumed
        assert "Accessible Value: 250 Build Points" in plain
        assert "[The Tower]" in plain  # brackets still literal

        styled = _styled_words(panel)
        assert ("Accessible Value:", "b") in styled
        assert ("Location:", "b") in styled
        assert ("behind", "i") in styled
        # The official rules text is NOT interpreted as Markdown.
        assert not any(
            style == "i" and "Build Points" in text for text, style in styled
        )


async def test_covenant_description_renders_emphasis_too():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].notes = "A **remote** covenant, *rarely* visited. 5 * 3 stays."
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        static = view.query_one("#cov-description-content", Static)
        assert str(static.render()) == "A remote covenant, rarely visited. 5 * 3 stays."
        assert _styled_words(static) == {("remote", "b"), ("rarely", "i")}


async def test_description_dialogs_mention_the_emphasis_syntax():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_wealth")
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _select_covenant(pilot, app)
        await _select_bh_row(pilot, app, "Boon", 0)
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, BoonHookDetailScreen)
        assert "**bold**" in str(
            app.screen.query_one("#bh-detail-hint", Static).render()
        )
        # Still fits a small terminal with the extra hint line.
        for button in app.screen.query(Button):
            assert button.region.height > 0 and button.region.bottom <= 24, button.id
        await pilot.press("escape")
        await pilot.pause()

        await _open_cov_section(pilot, app, "section-cov-description")
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditCovenantDescriptionScreen)
        assert "*italic*" in str(
            app.screen.query_one("#cov-desc-hint", Static).render()
        )
        for button in app.screen.query(Button):
            assert button.region.height > 0 and button.region.bottom <= 24, button.id


# -- The expanded catalog: types (categories) in the picker and the panel -------


async def test_picker_lists_boons_in_the_books_type_order_with_the_type_shown():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _open_cov_section(pilot, app, "section-cov-boons")
        await pilot.press("a")
        await pilot.pause()
        items = list(app.screen.query_one("#covbh-picker-list", ListView).children)
        labels = [str(item.query_one(Label).render()) for item in items]

        # The type is part of each label...
        # (the original entry keeps its name, "Edifice"; the book says "Edifices")
        assert "Edifice  [Fortifications, Minor, 1 pt]" in " ".join(labels)
        assert any("Island  [Fortifications, Free]" in label for label in labels)

        # ...and rows follow the book's order: Site first, then Fortifications...
        order = [
            "Site",
            "Fortifications",
            "Resources",
            "Residents",
            "External Relations",
            "Surroundings",
        ]
        seen = [next(c for c in order if f"[{c}," in label) for label in labels]
        assert seen == sorted(seen, key=order.index)
        assert seen[0] == "Site" and seen[-1] == "Surroundings"
        # ...and within a type, Free before Minor before Major.
        fortifications = [l for l in labels if "[Fortifications," in l]
        tiers = [
            next(t for t in ("Free", "Minor", "Major") if f", {t}" in l)
            for l in fortifications
        ]
        assert tiers == sorted(tiers, key=("Free", "Minor", "Major").index)


async def test_picker_search_finds_entries_by_their_type():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _open_cov_section(pilot, app, "section-cov-hooks")
        await pilot.press("a")
        await pilot.pause()
        app.screen.query_one("#picker-search", Input).value = "surroundings"
        await pilot.pause()
        items = list(app.screen.query_one("#covbh-picker-list", ListView).children)
        labels = [str(item.query_one(Label).render()) for item in items]
        assert labels and all("[Surroundings," in label for label in labels)
        assert any(label.startswith("Pilgrimage Site") for label in labels)


async def test_details_panel_shows_the_type_and_omits_it_for_untyped_entries():
    storage.save_saga(
        _saga_with_boons_and_hooks(
            "covbh_boon_free_manor_house",
            "covbh_hook_major_unknown",
            "covbh_hook_minor_weak_aura",
        )
    )

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view

        def plain(index: int) -> str:
            return re.sub(r"\[/?[a-z]*\]", "", view._bh_info_text(index))

        assert "Type: Fortifications" in plain(0)
        assert "Tier: Free Boon" in plain(0)  # no cost line for a Free Choice
        assert "pt)" not in plain(0).split("Rules:")[0]
        assert "Type:" not in plain(1)  # Unknown isn't filed under a type
        assert "Tier: Major Hook (3 pts)" in plain(1)
        assert "Type: Site" in plain(2)


async def test_weak_aura_hook_lowers_the_aura_labs_inherit():
    saga = _saga_with_configured_covenant()  # covenant aura 4
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_hook_minor_weak_aura"),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        assert "3 (base 4, -1 Boons)" in (
            app.screen._covenant_sheet_view._info_left_text()
        )
        await _select(pilot, app, ("laboratory", "lab1"))
        text = app.screen._laboratory_sheet_view._identity_text()
        assert "Aura: 3 (covenant) +0 (modifier) = 3" in text


# -- Covenant Inhabitants tab ---------------------------------------------------


def _saga_with_people() -> Saga:
    """Covenant cov1 with a listed magus and companion and three grogs (two
    unassigned + one in another covenant), so both sources of inhabitants exist."""
    saga = _saga_with_bare_character()
    saga.characters = [
        Character(
            id="mag1",
            name="Corvinus",
            type="magus",
            covenant_id="cov1",
            background=Background(year_born=1195),
            hermetic=HermeticBackground(house="house_bonisagus"),
        ),
        Character(id="comp1", name="Alys", type="companion", covenant_id="cov1"),
        Character(
            id="grog1",
            name="Old Thomae",
            type="grog",
            covenant_id="cov1",
            background=Background(year_born=1193),
            abilities=[Ability(name="Athletics"), Ability(name="Brawl")],
        ),
        Character(id="grog2", name="Dieter", type="grog", covenant_id="cov1"),
        Character(id="grog3", name="Not Ours", type="grog", covenant_id=None),
    ]
    return saga


async def _show_inhabitants_tab(pilot, app) -> None:
    view = app.screen._covenant_sheet_view
    await _wait_until(pilot, lambda: view.initial_tab_seen)
    await pilot.pause()
    view.query_one(TabbedContent).active = "tab-cov-inhabitants"
    await pilot.pause()


async def _open_inh_section(pilot, app, section_id: str) -> None:
    """Focus a section of the Inhabitants tab (so its a/A/e keys apply)."""
    await _show_inhabitants_tab(pilot, app)
    view = app.screen._covenant_sheet_view
    view.query_one(f"#{section_id}", Collapsible).query_one("CollapsibleTitle").focus()
    await pilot.pause()
    await _wait_until(pilot, lambda: app.screen._active_section() == section_id)


async def _select_inh_row(pilot, app, kind: str, row: int) -> None:
    await _show_inhabitants_tab(pilot, app)
    view = app.screen._covenant_sheet_view
    rows = view.query_one(f"#inh-{kind}-list", SelectableList)
    rows.focus()
    await pilot.pause()
    rows.highlighted = row
    await pilot.pause()


def _fill(app, **values) -> None:
    """Set FieldsDialog fields by key: Input/Select/Checkbox/TextArea alike."""
    for key, value in values.items():
        widget = app.screen.query_one(f"#fld-{key}")
        if isinstance(widget, TextArea):
            widget.text = str(value)
        elif isinstance(widget, Input):
            widget.value = str(value)
        else:  # Select or Checkbox
            widget.value = value


async def _save_dialog(pilot, app) -> None:
    app.screen.query_one("#btn-save", Button).press()
    await pilot.pause()


def _records(kind: str | None = None) -> list[Inhabitant]:
    cov = storage.load_saga("test_saga").covenants[0]
    return [r for r in cov.inhabitants if kind is None or r.kind == kind]


def _inh_view(app):
    return app.screen._covenant_sheet_view


def _inh_labels(app, kind: str) -> list[str]:
    return [label for _, label in _inh_view(app)._inh_rows(kind)]


def _inh_title(app, kind: str) -> str:
    return _plain_title(_inh_view(app).query_one(f"#section-inh-{kind}", Collapsible))


async def test_inhabitants_tab_has_all_its_sections_with_headcount_titles():
    saga = _saga_with_people()
    cov = saga.covenants[0]
    cov.boons_hooks = [VirtueFlawInstance(vf_id="covbh_boon_free_autocracy")]
    cov.inhabitants = [
        Inhabitant(id="t1", kind="turb", name="Guard", quantity=3),
        Inhabitant(id="i1", kind="inhabitant", name="Marta and Simon", quantity=2),
        Inhabitant(id="i2", kind="inhabitant", name="Jakob"),
    ]
    cov.population.other_people = 4
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _show_inhabitants_tab(pilot, app)
        view = _inh_view(app)

        ids = [
            "section-inh-loyalty",
            "section-inh-population",
            "section-inh-misc",
            *(f"section-inh-{k}" for k in inh.INHABITANT_KINDS),
        ]
        sections = [view.query_one(f"#{i}", Collapsible) for i in ids]
        assert all(not section.collapsed for section in sections)
        assert [_plain_title(x) for x in sections[:3]] == [
            "Loyalty",
            "Inhabitants",
            "Miscellaneous",
        ]
        # Titles carry the headcount: quantities added up, not rows.
        assert [_plain_title(x) for x in sections[3:]] == [
            "Magi (1)",
            "Companions (1)",
            "Specialists (0)",
            "Craftspeople (0)",
            "Turb (3)",
            "Inhabitants (3)",
            "Horses (0)",
            "Livestock (0)",
        ]
        text = str(view.query_one("#inh-population-content", Static).render())
        assert re.search(r"Total Inhabitants:\s+12\b", text)  # 4+1+1+3+3
        left = str(view.query_one("#inh-loyalty-left", Static).render())
        assert "Autocracy" in left  # the governance follows the Boon
        assert "Select an inhabitant" in str(
            view.query_one("#inh-panel", Static).render()
        )


async def test_magi_and_companions_are_listed_from_sheets_and_choosing_fills_the_panel():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        assert _inh_labels(app, "magus") == [
            "Corvinus | House Bonisagus | Year Born: 1195 | Loyalty: 0"
        ]
        assert _inh_labels(app, "companion") == [
            "Alys | Year Born: Unknown | Loyalty: 0"
        ]

        await _select_inh_row(pilot, app, "magus", 0)
        panel = _inh_view(app).query_one("#inh-panel", Static)
        text = str(panel.render())
        assert "House: Bonisagus" in text and "Year Born: 1195 (age 25)" in text
        assert "From the character sheet of Corvinus." in text

        # One selection across all the lists.
        await _select_inh_row(pilot, app, "companion", 0)
        assert _inh_view(app).selected_inhabitant("magus") is None
        assert "Name: Alys" in str(panel.render())


async def test_add_an_npc_magus_with_an_unknown_year():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-magus")
        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)  # straight to the form
        _fill(app, name="Hidden Hermit", house="house_criamon", loyalty=2)
        assert app.screen.query_one("#fld-year_born", Input).value == ""  # blank
        _fill(app, description="Lives in a *sealed* tower.")
        await _save_dialog(pilot, app)
        await _wait_until(pilot, lambda: len(_inh_labels(app, "magus")) == 2)

        assert _inh_labels(app, "magus")[1] == (
            "Hidden Hermit | House Criamon | Year Born: Unknown | Loyalty: 2"
        )
        assert _inh_title(app, "magus") == "Magi (2)"

    [npc] = _records("magus")
    assert (npc.name, npc.house, npc.year_born, npc.character_id) == (
        "Hidden Hermit",
        "house_criamon",
        None,
        None,
    )


async def test_editing_a_listed_magus_only_changes_covenant_side_fields():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_inh_row(pilot, app, "magus", 0)
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        # Name/house/year come from the sheet: shown, not editable.
        assert not app.screen.query("#fld-name")
        assert not app.screen.query("#fld-house")
        _fill(app, loyalty=3, description="Trusted **completely**.")
        await _save_dialog(pilot, app)
        await _wait_until(pilot, lambda: "Loyalty: 3" in _inh_labels(app, "magus")[0])
        assert _inh_labels(app, "magus")[0].startswith("Corvinus | House Bonisagus")

    [record] = _records("magus")
    assert record.character_id == "mag1" and record.loyalty == 3
    assert not record.departed


async def test_removing_a_listed_magus_keeps_them_in_the_covenant_but_stops_counting_them():
    saga = _saga_with_people()
    # Already edited once, so a covenant-side record exists to be marked.
    saga.covenants[0].inhabitants = [
        Inhabitant(id="m", kind="magus", character_id="mag1", loyalty=3)
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_inh_row(pilot, app, "magus", 0)
        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert "Remove Corvinus from the Magi list?" in message
        assert "stay in the covenant on their character sheet" in message
        await pilot.press("n")
        await pilot.pause()
        assert len(_inh_labels(app, "magus")) == 1  # No keeps them

        await pilot.press("A")
        await pilot.pause()
        await pilot.press("y")
        await _wait_until(pilot, lambda: not _inh_labels(app, "magus"))
        assert _inh_title(app, "magus") == "Magi (0)"
        text = str(_inh_view(app).query_one("#inh-population-content", Static).render())
        assert re.search(r"Total Inhabitants:\s+1\b", text)  # only Alys now

    saved = storage.load_saga("test_saga")
    assert next(c for c in saved.characters if c.id == "mag1").covenant_id == "cov1"
    [record] = _records("magus")
    assert record.departed and record.loyalty == 3 and record.character_id == "mag1"
    assert inh.entries_for_kind(saved, saved.covenants[0], "magus") == []


async def test_removing_a_listed_companion_with_no_record_creates_one():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_inh_row(pilot, app, "companion", 0)
        await pilot.press("A")
        await pilot.pause()
        await pilot.press("y")
        await _wait_until(pilot, lambda: not _inh_labels(app, "companion"))
        assert _inh_title(app, "companion") == "Companions (0)"
        # The magus is untouched.
        assert len(_inh_labels(app, "magus")) == 1

    [record] = _records("companion")
    assert record.departed and record.character_id == "comp1"


async def test_specialist_from_an_unassigned_grog_prefills_and_marks_it_assigned():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-specialist")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        labels = [
            str(item.query_one(Label).render())
            for item in app.screen.query_one("#removal-picker-list", ListView).children
        ]
        # New person first, then only THIS covenant's unassigned grogs.
        assert labels[0].startswith("(New person")
        assert [l.split("  ")[0] for l in labels[1:]] == ["Old Thomae", "Dieter"]

        await pilot.press("down")  # Old Thomae
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        assert app.screen.query_one("#fld-name", Input).value == "Old Thomae"
        assert app.screen.query_one("#fld-year_born", Input).value == "1193"
        _fill(app, responsibility="Teaches Latin", role="Teacher")
        await _save_dialog(pilot, app)
        await _wait_until(pilot, lambda: len(_inh_labels(app, "specialist")) == 1)
        assert _inh_labels(app, "specialist") == [
            "Old Thomae | Teaches Latin | Teacher | Year Born: 1193 | Loyalty: 0"
        ]

        # Now assigned, so he's no longer offered.
        await pilot.press("a")
        await pilot.pause()
        labels = [
            str(item.query_one(Label).render())
            for item in app.screen.query_one("#removal-picker-list", ListView).children
        ]
        assert [l.split("  ")[0] for l in labels[1:]] == ["Dieter"]

    [record] = _records("specialist")
    assert (record.character_id, record.role) == ("grog1", "Teacher")


async def test_a_brand_new_grog_type_person_needs_a_name_but_year_born_may_stay_unknown():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-specialist")
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("enter")  # "(New person...)"
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)

        await _save_dialog(pilot, app)
        assert isinstance(app.screen, FieldsDialog)  # refused: no name
        assert "Name is required" in str(app.screen.query_one("#fields-error").render())
        _fill(app, name="Visiting Steward", role="Steward")
        await _save_dialog(pilot, app)  # no year: fine
        await _wait_until(pilot, lambda: len(_inh_labels(app, "specialist")) == 1)
        assert _inh_labels(app, "specialist") == [
            "Visiting Steward | Steward | Year Born: Unknown | Loyalty: 0"
        ]

    [record] = _records("specialist")
    assert record.character_id is None and record.year_born is None


async def test_a_grog_without_a_year_born_is_assigned_with_it_unknown():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-turb")
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("down", "down")  # Dieter: no year on his sheet
        await pilot.press("enter")
        await pilot.pause()
        assert app.screen.query_one("#fld-name", Input).value == "Dieter"
        assert app.screen.query_one("#fld-year_born", Input).value == ""
        await _save_dialog(pilot, app)
        await _wait_until(pilot, lambda: len(_inh_labels(app, "turb")) == 1)
        assert "Year Born: Unknown" in _inh_labels(app, "turb")[0]


async def test_craftsperson_links_one_of_the_grogs_abilities_and_stores_craft_fields():
    saga = _saga_with_people()
    saga.characters[2].abilities[1].level = 4  # Old Thomae's Brawl
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-craftsperson")
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("down")
        await pilot.press("enter")  # Old Thomae
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)

        ability = app.screen.query_one("#fld-linked_ability", Select)
        assert isinstance(ability, Select)  # a dropdown of the grog's Abilities
        assert [value for _, value in ability._options if isinstance(value, str)] == [
            "Athletics",
            "Brawl",
        ]
        assert app.screen.query_one("#fld-field_of_work", Select).value == "None"
        _fill(
            app,
            responsibility="Blacksmithing",
            skill_value=7,
            field_of_work="Books",
            rare=True,
            linked_ability="Brawl",
        )
        await _save_dialog(pilot, app)
        await _wait_until(pilot, lambda: len(_inh_labels(app, "craftsperson")) == 1)
        # Tied to the sheet's Brawl (Level 4): that wins over the typed 7.
        assert _inh_labels(app, "craftsperson") == [
            "Old Thomae | Blacksmithing | Score: 4 | Qty: 1 | Year Born: 1193 | Loyalty: 0"
        ]

        # Editing again shows the score as read-only, taken from the Ability.
        await _select_inh_row(pilot, app, "craftsperson", 0)
        await pilot.press("e")
        await pilot.pause()
        assert not app.screen.query("#fld-skill_value")
        info = " ".join(
            str(s.render()) for s in app.screen.query(".fd-value").results(Static)
        )
        assert "4 (Level of Brawl)" in info
        await pilot.press("escape")

    [record] = _records("craftsperson")
    assert (record.field_of_work, record.rare, record.linked_ability) == (
        "Books",
        True,
        "Brawl",
    )
    # The typed number is kept as the fallback if the link is ever cleared.
    assert (record.skill_value, record.character_id) == (7, "grog1")


async def test_forms_and_the_remove_confirmation_fit_an_80_by_24_terminal():
    saga = _saga_with_people()
    saga.characters[2].abilities[1].level = 4
    saga.covenants[0].inhabitants = [
        Inhabitant(
            id="c",
            kind="craftsperson",
            name="Old Thomae",
            character_id="grog1",
            linked_ability="Brawl",
        )
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _select_covenant(pilot, app)
        await _select_inh_row(pilot, app, "craftsperson", 0)
        await pilot.press("e")
        await pilot.pause()
        region = app.screen.query_one("#fields-dialog").region
        assert region.right <= 80 and region.bottom <= 24  # right border on screen
        await pilot.press("escape")
        await pilot.pause()

        await _select_inh_row(pilot, app, "magus", 0)
        await pilot.press("A")
        await pilot.pause()
        region = app.screen.query_one("#confirm-dialog").region
        assert region.right <= 80 and region.bottom <= 24


async def test_craftsperson_score_is_typed_when_there_is_no_sheet_ability():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-craftsperson")
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("enter")  # (New person): no sheet at all
        await pilot.pause()
        _fill(app, name="Travelling Smith", responsibility="Smith", skill_value=6)
        await _save_dialog(pilot, app)
        await _wait_until(pilot, lambda: len(_inh_labels(app, "craftsperson")) == 1)
        assert "Score: 6" in _inh_labels(app, "craftsperson")[0]

        await _select_inh_row(pilot, app, "craftsperson", 0)
        await pilot.press("e")
        await pilot.pause()
        assert app.screen.query_one("#fld-skill_value", Input).value == "6"  # editable


async def test_quantity_drives_the_headcounts_and_must_be_at_least_one():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-turb")
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("enter")  # new person
        await pilot.pause()
        _fill(
            app, name="Guards", year_born=1200, responsibility="Gatehouse", quantity=0
        )
        await _save_dialog(pilot, app)
        assert isinstance(app.screen, FieldsDialog)  # quantity 0 refused
        assert "at least 1" in str(app.screen.query_one("#fields-error").render())
        _fill(app, quantity=3)
        await _save_dialog(pilot, app)
        await _wait_until(pilot, lambda: _inh_title(app, "turb") == "Turb (3)")

        text = str(_inh_view(app).query_one("#inh-population-content", Static).render())
        assert re.search(r"Total Inhabitants:\s+5\b", text)  # magus + companion + 3


async def test_horses_and_livestock_take_a_blank_year_and_a_quantity():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        for kind, name in (("horse", "Grey Mare"), ("livestock", "Sheep")):
            await _open_inh_section(pilot, app, f"section-inh-{kind}")
            await pilot.press("a")
            await pilot.pause()
            assert isinstance(app.screen, FieldsDialog)  # no picker for animals
            _fill(app, name=name, quantity=4)
            await _save_dialog(pilot, app)
            await _wait_until(pilot, lambda kind=kind: len(_inh_labels(app, kind)) == 1)
            assert _inh_labels(app, kind) == [
                f"{name} | Qty: 4 | Year Born: Unknown | Loyalty: 0"
            ]
        assert _inh_title(app, "horse") == "Horses (4)"


async def test_e_and_A_act_on_the_selected_inhabitant_and_delete_confirms():
    saga = _saga_with_people()
    saga.covenants[0].inhabitants = [
        Inhabitant(id="a", kind="turb", name="First", year_born=1200),
        Inhabitant(id="b", kind="turb", name="Second [x]", year_born=1201),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_inh_row(pilot, app, "turb", 1)

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)  # no "which one?" picker
        assert app.screen.query_one("#fld-name", Input).value == "Second [x]"
        await pilot.press("escape")
        await pilot.pause()

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert message == "Delete Second [x]?"
        await pilot.press("n")
        await pilot.pause()
        assert len(_inh_labels(app, "turb")) == 2

        await pilot.press("A")
        await pilot.pause()
        await pilot.press("y")
        await _wait_until(pilot, lambda: len(_inh_labels(app, "turb")) == 1)
        assert _inh_labels(app, "turb")[0].startswith("First")

        # Nothing chosen any more: 'A' falls back to asking which one.
        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

    assert [r.name for r in _records("turb")] == ["First"]


async def test_deleting_an_assigned_grog_returns_it_to_the_available_list():
    saga = _saga_with_people()
    saga.covenants[0].inhabitants = [
        Inhabitant(id="a", kind="specialist", name="Old Thomae", character_id="grog1")
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_inh_row(pilot, app, "specialist", 0)
        await pilot.press("A")
        await pilot.pause()
        await pilot.press("y")
        await _wait_until(pilot, lambda: not _inh_labels(app, "specialist"))
        cov = app.screen.selected_covenant
        assert "Old Thomae" in [
            g.name for g in inh.available_grogs(app.screen.saga, cov)
        ]


async def test_the_panel_renders_description_emphasis_for_the_chosen_inhabitant():
    saga = _saga_with_people()
    saga.covenants[0].inhabitants = [
        Inhabitant(
            id="a",
            kind="craftsperson",
            name="Gerhard",
            year_born=1187,
            description="Master **smith**, works *only* in iron. 5 * 3 stays.",
        )
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_inh_row(pilot, app, "craftsperson", 0)
        panel = _inh_view(app).query_one("#inh-panel", Static)
        assert "Master smith, works only in iron. 5 * 3 stays." in str(panel.render())
        styled = _styled_words(panel)
        assert ("smith", "b") in styled and ("only", "i") in styled


async def test_loyalty_governance_is_typed_unless_a_governance_boon_provides_it():
    saga = _saga_with_people()
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-loyalty")
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        assert app.screen.query_one("#fld-equipment", Select).value == "Standard"
        assert app.screen.query_one("#fld-money", Select).value == "Standard salary"
        _fill(
            app,
            governance="Guild of Mercers",
            base_points=-30,
            current_points=-28,
            prevailing_score=-3,
            equipment="Anything they need",
            equipment_modifier=2,
            money="Lavish salary",
            money_modifier=-1,
            familiarity=1,
        )
        await _save_dialog(pilot, app)
        await _wait_until(
            pilot,
            lambda: (
                "Guild of Mercers"
                in str(_inh_view(app).query_one("#inh-loyalty-left", Static).render())
            ),
        )
        left = str(_inh_view(app).query_one("#inh-loyalty-left", Static).render())
        right = str(_inh_view(app).query_one("#inh-loyalty-right", Static).render())
        assert "Guild of Mercers" in left
        assert re.search(r"Base Loyalty Points:\s+-30", left)
        assert "Anything they need  (2)" in right and "Lavish salary  (-1)" in right

    loyalty = storage.load_saga("test_saga").covenants[0].loyalty
    assert (loyalty.governance, loyalty.base_points) == ("Guild of Mercers", -30)
    assert (loyalty.equipment, loyalty.money) == ("Anything they need", "Lavish salary")

    # With a governance Boon the type isn't typed in: the field becomes info.
    saga = storage.load_saga("test_saga")
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_free_council")
    ]
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-loyalty")
        await pilot.press("e")
        await pilot.pause()
        assert not app.screen.query("#fld-governance")
        await pilot.press("escape")
        await pilot.pause()
        left = str(_inh_view(app).query_one("#inh-loyalty-left", Static).render())
        assert "Council" in left and "Guild of Mercers" not in left


async def test_population_and_miscellaneous_fields_are_editable_and_total_is_calculated():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        view = _inh_view(app)

        await _open_inh_section(pilot, app, "section-inh-population")
        await pilot.press("e")
        await pilot.pause()
        assert not app.screen.query("#fld-total")  # calculated: not an input
        _fill(
            app,
            teamsters=1,
            teamsters_needed=2,
            servants=3,
            servants_needed=4,
            other_people=6,
        )
        await _save_dialog(pilot, app)
        await _wait_until(
            pilot,
            lambda: (
                "1 / 2"
                in str(view.query_one("#inh-population-content", Static).render())
            ),
        )
        text = str(view.query_one("#inh-population-content", Static).render())
        assert "3 / 4" in text
        assert re.search(
            r"Total Inhabitants:\s+8\b", text
        )  # 6 other + magus + companion

        await _open_inh_section(pilot, app, "section-inh-misc")
        await pilot.press("e")
        await pilot.pause()
        _fill(app, aging_magi=1, magic_laborers=2, magic_turbula=5)
        await _save_dialog(pilot, app)
        await _wait_until(
            pilot,
            lambda: "5" in str(view.query_one("#inh-misc-right", Static).render()),
        )

    pop = storage.load_saga("test_saga").covenants[0].population
    assert (pop.teamsters_needed, pop.other_people) == (2, 6)
    assert (pop.aging_magi, pop.magic_laborers, pop.magic_turbula) == (1, 2, 5)


async def test_add_is_not_offered_on_the_summary_sections_but_edit_is():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        for section in (
            "section-inh-loyalty",
            "section-inh-population",
            "section-inh-misc",
        ):
            await _open_inh_section(pilot, app, section)
            await pilot.press("a")
            await pilot.pause()
            assert isinstance(app.screen, WorkspaceScreen), section  # nothing to add
            await pilot.press("e")
            await pilot.pause()
            assert isinstance(app.screen, FieldsDialog), section
            await pilot.press("escape")
            await pilot.pause()


async def test_inhabitant_dialogs_fit_a_small_terminal_and_hug_content_on_a_tall_one():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _select_covenant(pilot, app)
        # The busiest form: a craftsperson (many fields + a description).
        await _open_inh_section(pilot, app, "section-inh-craftsperson")
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("down")
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        for button in app.screen.query(Button):
            assert button.region.height > 0 and button.region.bottom <= 24, button.id
        await pilot.press("escape")
        await pilot.pause()

        # ...and the biggest summary form: Loyalty.
        await _open_inh_section(pilot, app, "section-inh-loyalty")
        await pilot.press("e")
        await pilot.pause()
        for button in app.screen.query(Button):
            assert button.region.height > 0 and button.region.bottom <= 24, button.id

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-horse")
        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        assert app.screen.query_one("#fields-dialog").region.height < 30


# -- Covenant Possessions tab ---------------------------------------------------


def _saga_with_a_lab() -> Saga:
    """Covenant cov1 with one laboratory ("Test Lab", owned by Leandro)."""
    return _saga_with_bare_laboratory()


async def _show_possessions_tab(pilot, app) -> None:
    view = app.screen._covenant_sheet_view
    await _wait_until(pilot, lambda: view.initial_tab_seen)
    await pilot.pause()
    view.query_one(TabbedContent).active = "tab-cov-possessions"
    await pilot.pause()


async def _open_pos_section(pilot, app, kind: str) -> None:
    """Focus a Possessions section (so its a/A/e keys apply)."""
    await _show_possessions_tab(pilot, app)
    view = app.screen._covenant_sheet_view
    view.query_one(f"#section-pos-{kind}", Collapsible).query_one(
        "CollapsibleTitle"
    ).focus()
    await pilot.pause()
    await _wait_until(
        pilot, lambda: app.screen._active_section() == f"section-pos-{kind}"
    )


async def _select_pos_row(pilot, app, kind: str, row: int) -> None:
    await _show_possessions_tab(pilot, app)
    rows = app.screen._covenant_sheet_view.query_one(
        f"#pos-{kind}-list", SelectableList
    )
    rows.focus()
    await pilot.pause()
    rows.highlighted = row
    await pilot.pause()


def _pos_labels(app, kind: str) -> list[str]:
    return [label for _, label in app.screen._covenant_sheet_view._pos_rows(kind)]


def _pos_records(kind: str | None = None) -> list[Possession]:
    cov = storage.load_saga("test_saga").covenants[0]
    return [r for r in cov.possessions if kind is None or r.kind == kind]


def _pos_panel(app) -> str:
    return str(app.screen._covenant_sheet_view.query_one("#pos-panel", Static).render())


async def _add_possession(pilot, app, kind: str, **values) -> None:
    """Press 'a' in a section, fill the form and save it."""
    before = len(_pos_labels(app, kind))
    await _open_pos_section(pilot, app, kind)
    await pilot.press("a")
    await pilot.pause()
    assert isinstance(app.screen, FieldsDialog)
    _fill(app, **values)
    await _save_dialog(pilot, app)
    await _wait_until(pilot, lambda: len(_pos_labels(app, kind)) > before)


async def test_possessions_tab_has_its_seven_sections_and_lists_the_labs_as_sanctums():
    storage.save_saga(_saga_with_a_lab())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _show_possessions_tab(pilot, app)
        view = app.screen._covenant_sheet_view
        sections = [
            view.query_one(f"#section-pos-{kind}", Collapsible)
            for kind in pos.KIND_TITLES
        ]
        assert [_plain_title(x) for x in sections] == [
            "Properties and Land",
            "Sanctums",
            "Weapons",
            "Armor",
            "Vis Sources",
            "Raw Vis Stores",
            "Items",
        ]
        assert all(not section.collapsed for section in sections)
        # The laboratory is a sanctum without anyone adding it.
        assert _pos_labels(app, "sanctum") == ["Test Lab | Owner: Leandro"]
        assert "Select a possession" in _pos_panel(app)


async def test_the_panel_is_docked_below_the_lists_and_stays_on_screen():
    storage.save_saga(_saga_with_a_lab())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _show_possessions_tab(pilot, app)
        view = app.screen._covenant_sheet_view
        scroll = view.query_one("#pos-scroll").region
        panel = view.query_one("#pos-panel").region
        assert panel.y >= scroll.bottom  # below the scrolling lists
        assert panel.bottom <= 50  # and fully on screen


async def test_property_needs_only_a_name_and_supports_edit_and_delete():
    storage.save_saga(_saga_with_a_lab())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_pos_section(pilot, app, "property")
        await pilot.press("a")
        await pilot.pause()
        await _save_dialog(pilot, app)  # nothing filled in
        assert "Name is required" in str(app.screen.query_one("#fields-error").render())
        _fill(app, name="Bare Plot")
        await _save_dialog(pilot, app)  # every other field is optional
        await _wait_until(pilot, lambda: len(_pos_labels(app, "property")) == 1)
        assert _pos_labels(app, "property") == ["Bare Plot"]

        # Edit it: all the fields, then the row and panel show them.
        await _select_pos_row(pilot, app, "property", 0)
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        _fill(
            app,
            location="By the river",
            dimensions="40 acres",
            inhabitants="Two tenant families",
            description="Rich **black** soil.",
        )
        await _save_dialog(pilot, app)
        await _wait_until(pilot, lambda: "Location" in _pos_labels(app, "property")[0])
        assert _pos_labels(app, "property") == [
            "Bare Plot | Location: By the river | Dimensions: 40 acres | "
            "Inhabitants: Two tenant families"
        ]
        await _select_pos_row(pilot, app, "property", 0)
        panel = _pos_panel(app)
        assert "Rich black soil." in panel and "Dimensions: 40 acres" in panel

        # Delete confirms.
        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await _wait_until(pilot, lambda: not _pos_labels(app, "property"))

    assert _pos_records("property") == []


async def test_a_laboratory_sanctum_edits_only_covenant_side_fields_and_cannot_be_deleted():
    storage.save_saga(_saga_with_a_lab())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_pos_row(pilot, app, "sanctum", 0)
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        for key in ("name", "owner", "location", "build_points"):
            assert not app.screen.query(f"#fld-{key}"), key  # from the laboratory
        assert (
            app.screen.query_one("#fld-usage", Select).value == "Standard (2 Seasons)"
        )  # the default
        _fill(
            app,
            quality=3,
            upkeep=30,
            usage="Heavy (3+ Seasons)",
            description="Busy *all* year.",
        )
        await _save_dialog(pilot, app)
        await _wait_until(pilot, lambda: "Quality: 3" in _pos_labels(app, "sanctum")[0])
        assert _pos_labels(app, "sanctum") == [
            "Test Lab | Owner: Leandro | Quality: 3 | Upkeep: 30 Points"
        ]

        await _select_pos_row(pilot, app, "sanctum", 0)
        panel = _pos_panel(app)
        for expected in (
            "Usage: Heavy (3+ Seasons)",
            "Build Points: 0",
            "Busy all year.",
        ):
            assert expected in panel, expected

        # A laboratory of the covenant can't be deleted from here.
        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)  # no confirmation
        assert len(_pos_labels(app, "sanctum")) == 1

    [record] = _pos_records("sanctum")
    assert record.lab_id == "lab1" and record.usage == "Heavy (3+ Seasons)"


async def test_manual_sanctums_have_every_field_and_can_be_deleted():
    storage.save_saga(_saga_with_a_lab())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_pos_section(pilot, app, "sanctum")
        await pilot.press("a")
        await pilot.pause()
        assert (
            app.screen.query_one("#fld-usage", Select).value == "Standard (2 Seasons)"
        )
        # Nobody owns it yet: free for visitors to use (the Usage says how hard).
        assert app.screen.query_one("#fld-owner", Input).value == "Free"
        _fill(
            app,
            name="Hidden Study",
            owner="Corvinus",
            location="Under the stairs",
            quality=2,
            upkeep=5,
            build_points=15,
        )
        await _save_dialog(pilot, app)
        await _wait_until(pilot, lambda: len(_pos_labels(app, "sanctum")) == 2)
        assert _pos_labels(app, "sanctum")[1] == (
            "Hidden Study | Owner: Corvinus | Quality: 2 | Upkeep: 5 Points"
        )
        await _select_pos_row(pilot, app, "sanctum", 1)
        assert "Build Points: 15" in _pos_panel(app)

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await _wait_until(pilot, lambda: len(_pos_labels(app, "sanctum")) == 1)

    assert _pos_records("sanctum") == []


async def test_weapons_armor_and_items_need_a_name_and_a_quantity_defaulting_to_one():
    storage.save_saga(_saga_with_a_lab())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        for kind, name in (
            ("weapon", "Crossbows"),
            ("armor", "Mail Hauberks"),
            ("item", "The Weeping Lens"),
        ):
            await _open_pos_section(pilot, app, kind)
            await pilot.press("a")
            await pilot.pause()
            assert app.screen.query_one("#fld-quantity", Input).value == "1"  # default
            await _save_dialog(pilot, app)
            assert "Name is required" in str(
                app.screen.query_one("#fields-error").render()
            )
            _fill(app, name=name, quantity=0)
            await _save_dialog(pilot, app)
            assert "at least 1" in str(app.screen.query_one("#fields-error").render())
            _fill(app, quantity=3, description="Well **kept**.")
            await _save_dialog(pilot, app)
            await _wait_until(pilot, lambda kind=kind: len(_pos_labels(app, kind)) == 1)
            assert _pos_labels(app, kind) == [f"{name} | Qty: 3"]

        await _select_pos_row(pilot, app, "item", 0)
        panel = _pos_panel(app)
        assert "Quantity: 3" in panel and "Well kept." in panel


async def test_vis_source_requires_name_art_season_and_pawns():
    storage.save_saga(_saga_with_a_lab())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_pos_section(pilot, app, "vis_source")
        await pilot.press("a")
        await pilot.pause()
        error = lambda: str(app.screen.query_one("#fields-error").render())

        await _save_dialog(pilot, app)
        assert "Name is required" in error()
        _fill(app, name="Whispering Well")
        await _save_dialog(pilot, app)
        assert "Art is required" in error()
        _fill(app, art="Vim")
        await _save_dialog(pilot, app)
        assert "Season harvested is required" in error()
        _fill(app, season="Winter", pawns=0)
        await _save_dialog(pilot, app)
        assert "Pawns must be at least 1" in error()
        _fill(
            app,
            pawns=3,
            location="Beneath the chapel",
            physical_form="Water in a stone basin",
            description="Only flows *after* midwinter.",
        )
        await _save_dialog(pilot, app)
        await _wait_until(pilot, lambda: len(_pos_labels(app, "vis_source")) == 1)
        assert _pos_labels(app, "vis_source") == [
            "Whispering Well | Art: Vim | Pawns: 3 | Season: Winter"
        ]

        await _select_pos_row(pilot, app, "vis_source", 0)
        panel = _pos_panel(app)
        for expected in (
            "Season: Winter",
            "Location: Beneath the chapel",
            "Physical Form: Water in a stone basin",
            "Only flows after midwinter.",
        ):
            assert expected in panel, expected

    [record] = _pos_records("vis_source")
    assert (record.art, record.season, record.pawns) == ("Vim", "Winter", 3)


async def test_art_and_season_choices_are_the_real_lists():
    storage.save_saga(_saga_with_a_lab())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_pos_section(pilot, app, "vis_source")
        await pilot.press("a")
        await pilot.pause()
        arts = [
            v
            for _, v in app.screen.query_one("#fld-art", Select)._options
            if isinstance(v, str)
        ]
        seasons = [
            v
            for _, v in app.screen.query_one("#fld-season", Select)._options
            if isinstance(v, str)
        ]
        assert arts == [*TECHNIQUES, *FORMS] and len(arts) == 15
        assert seasons == ["Spring", "Summer", "Autumn", "Winter"]


async def test_raw_vis_stores_take_name_art_pawns_and_optional_location_and_form():
    storage.save_saga(_saga_with_a_lab())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_pos_section(pilot, app, "vis_store")
        await pilot.press("a")
        await pilot.pause()
        assert not app.screen.query("#fld-description")  # not one of its fields
        assert not app.screen.query("#fld-season")  # a vis SOURCE field
        await _save_dialog(pilot, app)
        assert "Name is required" in str(app.screen.query_one("#fields-error").render())
        _fill(app, name="Vim Vis", art="Vim", pawns=9)  # location/form left blank
        await _save_dialog(pilot, app)
        await _wait_until(pilot, lambda: len(_pos_labels(app, "vis_store")) == 1)
        assert _pos_labels(app, "vis_store") == ["Vim Vis | Art: Vim | Pawns: 9"]

        await _select_pos_row(pilot, app, "vis_store", 0)
        await pilot.press("e")
        await pilot.pause()
        _fill(app, location="The vault", physical_form="Lumps of amber")
        await _save_dialog(pilot, app)
        await _select_pos_row(pilot, app, "vis_store", 0)
        await _wait_until(pilot, lambda: "The vault" in _pos_panel(app))
        panel = _pos_panel(app)
        assert (
            "Location: The vault" in panel and "Physical Form: Lumps of amber" in panel
        )


async def test_e_and_A_act_on_the_chosen_possession_with_a_picker_fallback():
    saga = _saga_with_a_lab()
    saga.covenants[0].possessions = [
        Possession(id="a", kind="item", name="First"),
        Possession(id="b", kind="item", name="Second [x]"),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_pos_row(pilot, app, "item", 1)

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)  # no "which one?" picker
        assert app.screen.query_one("#fld-name", Input).value == "Second [x]"
        await pilot.press("escape")
        await pilot.pause()

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert message == "Delete Second [x]?"
        await pilot.press("n")
        await pilot.pause()
        assert len(_pos_labels(app, "item")) == 2
        await pilot.press("A")
        await pilot.pause()
        await pilot.press("y")
        await _wait_until(pilot, lambda: len(_pos_labels(app, "item")) == 1)

        # Nothing chosen any more: 'A' falls back to asking which one.
        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

    assert [r.name for r in _pos_records("item")] == ["First"]


async def test_one_selection_across_the_possession_lists():
    saga = _saga_with_a_lab()
    saga.covenants[0].possessions = [
        Possession(id="a", kind="weapon", name="Crossbows"),
        Possession(id="b", kind="armor", name="Mail"),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_pos_row(pilot, app, "weapon", 0)
        assert "Name: Crossbows" in _pos_panel(app)
        await _select_pos_row(pilot, app, "armor", 0)
        view = app.screen._covenant_sheet_view
        assert view.selected_possession("weapon") is None  # the other list let go
        assert "Name: Mail" in _pos_panel(app)


async def test_legacy_vis_stock_shows_up_as_raw_vis_stores():
    saga = _saga_with_a_lab()
    saga.covenants[0].vis_stock = {"Ignem": 5, "Vim": 2}
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _show_possessions_tab(pilot, app)
        assert _pos_labels(app, "vis_store") == [
            "Ignem Vis | Art: Ignem | Pawns: 5",
            "Vim Vis | Art: Vim | Pawns: 2",
        ]


async def test_possession_forms_fit_a_small_terminal_and_hug_content_on_a_tall_one():
    storage.save_saga(_saga_with_a_lab())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _select_covenant(pilot, app)
        await _open_pos_section(pilot, app, "vis_source")  # the busiest form
        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        for button in app.screen.query(Button):
            assert button.region.height > 0 and button.region.bottom <= 24, button.id

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_pos_section(pilot, app, "weapon")
        await pilot.press("a")
        await pilot.pause()
        assert app.screen.query_one("#fields-dialog").region.height < 30
