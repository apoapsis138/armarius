import pytest
from textual.widgets import (
    Button,
    Checkbox,
    Collapsible,
    Input,
    ListView,
    Select,
    TabbedContent,
    Tree,
)

from ars_magica_manager import storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Book,
    Character,
    Characteristics,
    Covenant,
    LabCharacteristics,
    Laboratory,
    Library,
    Saga,
    Spell,
    VirtueFlawInstance,
)
from ars_magica_manager.screens import (
    AbilityDetailsScreen,
    AbilityPickerScreen,
    CharacterCreateScreen,
    CovenantCreateScreen,
    DiaryEntryPromptScreen,
    EditAgingScreen,
    EditArtsScreen,
    EditBackgroundScreen,
    EditCharacteristicsScreen,
    EditDescriptionScreen,
    EditFatigueScreen,
    EditHermeticBackgroundScreen,
    EditLabCharacteristicsScreen,
    EditLabIdentityScreen,
    EditWoundsScreen,
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


async def test_create_character_action_disabled_without_covenant_selected():
    storage.save_saga(Saga(id="test_saga", name="Test Saga", storyguide="Alex"))

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_workspace(pilot)
        assert app.screen.selected_kind == "saga"

        await pilot.press("c")
        await pilot.pause()

        # "New Character" only applies once a covenant is selected -- the
        # binding is disabled at the saga root, so nothing should open.
        assert isinstance(app.screen, WorkspaceScreen)


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
        summary = app.screen._covenant_summary(app.screen.selected_covenant)
        assert "Covenant: Test Covenant" in summary
        assert "Notes: A nice place" in summary
        assert "Ignem: 5" in summary

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
        text = app.screen._laboratory_sheet_view._characteristics_text()
        assert "Size: +2 (manual)" in text
        assert "Safety: -1 (manual)" in text

    saga = storage.load_saga("test_saga")
    characteristics = saga.laboratories[0].characteristics
    assert characteristics.size == 2
    assert characteristics.safety == -1


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
