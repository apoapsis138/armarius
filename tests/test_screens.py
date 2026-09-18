import pytest
from textual.widgets import Input, ListView, Select, Tree

from ars_magica_manager import storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Book,
    Character,
    Characteristics,
    Covenant,
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
    EditArtsScreen,
    LaboratoryCreateScreen,
    ParamPromptScreen,
    RemovalPickerScreen,
    SagaCreateScreen,
    SagaPickerScreen,
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


async def _select(pilot, app, data) -> None:
    """Select a nav-tree node by its `.data`, the same way a click/enter would."""
    tree = app.screen.query_one("#nav-tree", Tree)
    node = _find_node(tree, data)
    assert node is not None, f"tree node with data={data!r} not found"
    tree.select_node(node)
    await pilot.pause()


async def _open_workspace(pilot) -> None:
    await pilot.press("enter")  # picker -> workspace
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
                    Ability(name="Magic Theory", score=5, specialty="Lab Totals")
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
                size=1,
                aura=3,
                features=["Well-Stocked"],
                virtues_flaws=[VirtueFlawInstance(vf_id="vf_superior_lab_equipment")],
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

        summary = app.screen._character_summary(app.screen.selected_character)
        assert "Character: Leandro" in summary
        assert "Covenant: Test Covenant" in summary
        assert "Assigned Laboratory: yes" in summary
        assert "Int 3" in summary
        assert "Creo (Cr): 10/55" in summary
        assert "Magic Theory 5 (Lab Totals)" in summary
        assert "Affinity with Creo" in summary
        assert "Ball of Abysmal Flame (Creo Ignem 20)" in summary


async def test_selecting_laboratory_shows_owner_and_virtues():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)
        await _select(pilot, app, ("laboratory", "lab1"))

        summary = app.screen._laboratory_summary(app.screen.selected_laboratory)
        assert "Owner: Leandro" in summary
        assert "Aura: 3" in summary
        assert "Well-Stocked" in summary
        assert "Superior Lab Equipment" in summary


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


async def test_add_virtue_flaw_without_parameters_to_character():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)

        await pilot.press("v")
        await pilot.pause()
        assert isinstance(app.screen, VirtueFlawPickerScreen)

        await pilot.click("#vf-vf_superior_lab_equipment")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Superior Lab Equipment" in app.screen._character_summary(
            app.screen.selected_character
        )

    saga = storage.load_saga("test_saga")
    character = saga.characters[0]
    assert len(character.virtues_flaws) == 1
    assert character.virtues_flaws[0].vf_id == "vf_superior_lab_equipment"


async def test_add_virtue_flaw_with_parameters_to_character():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)

        await pilot.press("v")
        await pilot.pause()

        # Catalog order puts "Affinity with {art}" (which needs a parameter) first.
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, ParamPromptScreen)

        app.screen.query_one("#input-param-art", Input).value = "Creo"
        await pilot.click("#btn-confirm")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Affinity with Creo" in app.screen._character_summary(
            app.screen.selected_character
        )

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

        await pilot.press("v")
        await pilot.pause()

        picker_list = app.screen.query_one("#vf-picker-list", ListView)
        item_ids = [item.id for item in picker_list.children]
        assert "vf-vf_affinity_with_art" not in item_ids


async def test_add_virtue_flaw_to_laboratory_reuses_same_picker():
    saga = _saga_with_bare_character()
    saga.laboratories.append(
        Laboratory(id="lab1", covenant_id="cov1", name="Test Lab", owner_id="char1")
    )
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)
        await _select(pilot, app, ("laboratory", "lab1"))

        await pilot.press("v")
        await pilot.pause()
        assert isinstance(app.screen, VirtueFlawPickerScreen)

        await pilot.click("#vf-vf_superior_lab_equipment")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Superior Lab Equipment" in app.screen._laboratory_summary(
            app.screen.selected_laboratory
        )

    saga = storage.load_saga("test_saga")
    lab = saga.laboratories[0]
    assert len(lab.virtues_flaws) == 1
    assert lab.virtues_flaws[0].vf_id == "vf_superior_lab_equipment"


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
        app.screen.query_one("#input-aura", Input).value = "3"

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
    assert lab.size == 1
    assert lab.aura == 3
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

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, AbilityPickerScreen)

        await pilot.click("#ability-ab_athletics")
        await pilot.pause()
        assert isinstance(app.screen, AbilityDetailsScreen)

        app.screen.query_one("#input-score", Input).value = "3"
        app.screen.query_one("#input-specialty", Input).value = "Running"

        await pilot.click("#btn-confirm")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Athletics 3 (Running)" in app.screen._character_summary(
            app.screen.selected_character
        )

    saga = storage.load_saga("test_saga")
    character = saga.characters[0]
    assert len(character.abilities) == 1
    assert character.abilities[0].name == "Athletics"
    assert character.abilities[0].score == 3
    assert character.abilities[0].specialty == "Running"


async def test_add_ability_with_parameters_to_character():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)

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

        app.screen.query_one("#input-score", Input).value = "2"

        await pilot.click("#btn-confirm")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    character = saga.characters[0]
    assert len(character.abilities) == 1
    assert character.abilities[0].name == "Craft: Blacksmith"
    assert character.abilities[0].score == 2


async def test_cancelling_ability_details_returns_to_picker_without_adding():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)

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
    saga.characters[0].abilities.append(Ability(name="Athletics", score=1))
    saga.characters[0].abilities.append(Ability(name="Craft: Blacksmith", score=1))
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)

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
        assert "Magic Theory" in app.screen._character_summary(
            app.screen.selected_character
        )

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

        await pilot.press("enter")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Magic Theory" not in app.screen._character_summary(
            app.screen.selected_character
        )

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].abilities == []


async def test_remove_virtue_flaw_from_character():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        assert "Affinity with Creo" in app.screen._character_summary(
            app.screen.selected_character
        )

        await pilot.press("V")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

        await pilot.press("enter")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Affinity with Creo" not in app.screen._character_summary(
            app.screen.selected_character
        )

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].virtues_flaws == []


async def test_remove_virtue_flaw_from_laboratory():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)
        await _select(pilot, app, ("laboratory", "lab1"))
        assert "Superior Lab Equipment" in app.screen._laboratory_summary(
            app.screen.selected_laboratory
        )

        await pilot.press("V")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

        await pilot.press("enter")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Superior Lab Equipment" not in app.screen._laboratory_summary(
            app.screen.selected_laboratory
        )

    saga = storage.load_saga("test_saga")
    assert saga.laboratories[0].virtues_flaws == []


async def test_remove_with_nothing_to_remove_stays_on_same_screen():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)

        await pilot.press("A")
        await pilot.pause()

        # Nothing to remove -- stays on the workspace, no picker opened.
        assert isinstance(app.screen, WorkspaceScreen)


async def test_cancelling_removal_picker_keeps_the_item():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)

        await pilot.press("V")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

        await pilot.press("escape")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Affinity with Creo" in app.screen._character_summary(
            app.screen.selected_character
        )

    saga = storage.load_saga("test_saga")
    assert len(saga.characters[0].virtues_flaws) == 1


async def test_edit_arts_prefills_existing_scores_and_saves_full_grid():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)

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
    # layout wide enough to push columns off-screen, or to block real
    # keyboard input, actually fails here.
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _select_character(pilot, app)
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditArtsScreen)

        screen_width = app.screen.size.width
        # One field from each of the 3 columns: Techniques, Forms col A, Forms col B.
        for field_id in (
            "#input-art-rego-level",
            "#input-art-herbam-level",
            "#input-art-vim-level",
        ):
            field = app.screen.query_one(field_id, Input)
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


async def test_edit_arts_is_unavailable_for_non_magi():
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

        await pilot.press("e")
        await pilot.pause()

        # Arts editing doesn't apply to non-magi -- the binding is disabled.
        assert isinstance(app.screen, WorkspaceScreen)
        assert app.screen.selected_kind == "character"


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
