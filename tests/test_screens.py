import pytest
from textual.widgets import Input, ListView, Select

from ars_magica_manager import storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import (
    Ability,
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
    CharacterDetailScreen,
    CovenantCreateScreen,
    CovenantDetailScreen,
    LaboratoryCreateScreen,
    LaboratoryDetailScreen,
    LibraryDetailScreen,
    ParamPromptScreen,
    RemovalPickerScreen,
    SagaCreateScreen,
    SagaDetailScreen,
    SagaPickerScreen,
    VirtueFlawPickerScreen,
)


@pytest.fixture(autouse=True)
def isolated_sagas_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "SAGAS_DIR", tmp_path)


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


async def test_selecting_a_saga_opens_its_detail_screen():
    storage.save_saga(
        Saga(id="test_saga", name="Test Saga", storyguide="Alex", current_year=1220)
    )

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        list_view = app.screen.query_one("#saga-list", ListView)
        assert list_view.index == 0

        await pilot.press("enter")
        await pilot.pause()

        assert isinstance(app.screen, SagaDetailScreen)
        assert app.screen.saga.id == "test_saga"


async def test_saga_detail_shows_empty_state_with_no_covenants():
    storage.save_saga(Saga(id="test_saga", name="Test Saga", storyguide="Alex"))

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await pilot.press("enter")
        await pilot.pause()

        assert isinstance(app.screen, SagaDetailScreen)
        covenant_list = app.screen.query_one("#covenant-list", ListView)
        assert len(covenant_list.children) == 1
        assert covenant_list.index is None


async def test_create_covenant_flow_saves_covenant_and_empty_library():
    storage.save_saga(Saga(id="test_saga", name="Test Saga", storyguide="Alex"))

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await pilot.press("enter")  # picker -> saga detail
        await pilot.pause()

        await pilot.press("n")
        await pilot.pause()
        assert isinstance(app.screen, CovenantCreateScreen)

        app.screen.query_one("#input-name", Input).value = "Fengheld"
        app.screen.query_one("#input-notes", Input).value = "A border covenant"

        await pilot.click("#btn-create")
        await pilot.pause()

        assert isinstance(app.screen, SagaDetailScreen)
        covenant_list = app.screen.query_one("#covenant-list", ListView)
        assert len(covenant_list.children) == 1

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
        await pilot.press("enter")
        await pilot.pause()
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


async def test_create_character_defaults_to_current_covenant():
    storage.save_saga(_saga_with_empty_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await pilot.press("enter")  # picker -> saga detail
        await pilot.pause()
        await pilot.press("enter")  # saga detail -> covenant detail
        await pilot.pause()

        await pilot.press("n")
        await pilot.pause()
        assert isinstance(app.screen, CharacterCreateScreen)

        app.screen.query_one("#input-name", Input).value = "Leandro"

        await pilot.click("#btn-create")
        await pilot.pause()

        assert isinstance(app.screen, CovenantDetailScreen)
        character_list = app.screen.query_one("#character-list", ListView)
        assert len(character_list.children) == 1

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
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("n")
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
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("n")
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
                arts={"creo": 10, "ignem": 5},
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


async def test_covenant_browsing_shows_summary_and_lists():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await pilot.press("enter")  # saga picker -> saga detail
        await pilot.pause()

        covenant_list = app.screen.query_one("#covenant-list", ListView)
        assert covenant_list.index == 0

        await pilot.press("enter")  # saga detail -> covenant detail
        await pilot.pause()

        assert isinstance(app.screen, CovenantDetailScreen)
        assert app.screen.covenant.id == "cov1"

        summary = app.screen._summary()
        assert "Covenant: Test Covenant" in summary
        assert "Notes: A nice place" in summary
        assert "Ignem: 5" in summary

        assert len(app.screen.query_one("#character-list", ListView).children) == 1
        assert len(app.screen.query_one("#laboratory-list", ListView).children) == 1
        assert len(app.screen.query_one("#library-list", ListView).children) == 1


async def test_character_detail_shows_sheet_fields():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await pilot.press("enter")  # picker -> saga detail
        await pilot.pause()
        await pilot.press("enter")  # saga detail -> covenant detail
        await pilot.pause()
        await pilot.press(
            "enter"
        )  # covenant detail -> character detail (default focus)
        await pilot.pause()

        assert isinstance(app.screen, CharacterDetailScreen)
        summary = app.screen._summary()
        assert "Character: Leandro" in summary
        assert "Covenant: Test Covenant" in summary
        assert "Assigned Laboratory: yes" in summary
        assert "Int 3" in summary
        assert "Creo: 10" in summary
        assert "Magic Theory 5 (Lab Totals)" in summary
        assert "Affinity with Creo" in summary
        assert "Ball of Abysmal Flame (Creo Ignem 20)" in summary


async def test_laboratory_detail_shows_owner_and_virtues():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        await pilot.click("#laboratory-lab1")
        await pilot.pause()

        assert isinstance(app.screen, LaboratoryDetailScreen)
        summary = app.screen._summary()
        assert "Owner: Leandro" in summary
        assert "Aura: 3" in summary
        assert "Well-Stocked" in summary
        assert "Superior Lab Equipment" in summary


async def test_library_detail_shows_books_and_lab_text_spell():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        await pilot.click("#library-lib1")
        await pilot.pause()

        assert isinstance(app.screen, LibraryDetailScreen)
        summary = app.screen._summary()
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


async def _open_covenant_detail(pilot) -> None:
    await pilot.press("enter")  # picker -> saga detail
    await pilot.pause()
    await pilot.press("enter")  # saga detail -> covenant detail
    await pilot.pause()


async def _open_character_detail(pilot) -> None:
    await _open_covenant_detail(pilot)
    await pilot.press("enter")  # covenant detail -> character detail
    await pilot.pause()


async def test_add_virtue_flaw_without_parameters_to_character():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_character_detail(pilot)
        assert isinstance(app.screen, CharacterDetailScreen)

        await pilot.press("v")
        await pilot.pause()
        assert isinstance(app.screen, VirtueFlawPickerScreen)

        await pilot.click("#vf-vf_superior_lab_equipment")
        await pilot.pause()

        assert isinstance(app.screen, CharacterDetailScreen)
        assert "Superior Lab Equipment" in app.screen._summary()

    saga = storage.load_saga("test_saga")
    character = saga.characters[0]
    assert len(character.virtues_flaws) == 1
    assert character.virtues_flaws[0].vf_id == "vf_superior_lab_equipment"


async def test_add_virtue_flaw_with_parameters_to_character():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_character_detail(pilot)

        await pilot.press("v")
        await pilot.pause()

        # Catalog order puts "Affinity with {art}" (which needs a parameter) first.
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, ParamPromptScreen)

        app.screen.query_one("#input-param-art", Input).value = "Creo"
        await pilot.click("#btn-confirm")
        await pilot.pause()

        assert isinstance(app.screen, CharacterDetailScreen)
        assert "Affinity with Creo" in app.screen._summary()

    saga = storage.load_saga("test_saga")
    character = saga.characters[0]
    assert len(character.virtues_flaws) == 1
    assert character.virtues_flaws[0].vf_id == "vf_affinity_with_art"
    assert character.virtues_flaws[0].params == {"art": "creo"}


async def test_cancelling_param_screen_returns_to_picker_without_adding():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_character_detail(pilot)

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
        await _open_character_detail(pilot)

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
        await _open_covenant_detail(pilot)

        await pilot.click("#laboratory-lab1")
        await pilot.pause()
        assert isinstance(app.screen, LaboratoryDetailScreen)

        await pilot.press("v")
        await pilot.pause()
        assert isinstance(app.screen, VirtueFlawPickerScreen)

        await pilot.click("#vf-vf_superior_lab_equipment")
        await pilot.pause()

        assert isinstance(app.screen, LaboratoryDetailScreen)
        assert "Superior Lab Equipment" in app.screen._summary()

    saga = storage.load_saga("test_saga")
    lab = saga.laboratories[0]
    assert len(lab.virtues_flaws) == 1
    assert lab.virtues_flaws[0].vf_id == "vf_superior_lab_equipment"


async def test_create_laboratory_flow_saves_laboratory():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_covenant_detail(pilot)

        await pilot.press("l")
        await pilot.pause()
        assert isinstance(app.screen, LaboratoryCreateScreen)

        app.screen.query_one("#input-name", Input).value = "The Alchemical Tower"
        app.screen.query_one("#input-size", Input).value = "1"
        app.screen.query_one("#input-aura", Input).value = "3"

        await pilot.click("#btn-create")
        await pilot.pause()

        assert isinstance(app.screen, CovenantDetailScreen)
        lab_list = app.screen.query_one("#laboratory-list", ListView)
        assert len(lab_list.children) == 1

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
        await _open_covenant_detail(pilot)

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
        await _open_covenant_detail(pilot)

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
        await _open_character_detail(pilot)

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

        assert isinstance(app.screen, CharacterDetailScreen)
        assert "Athletics 3 (Running)" in app.screen._summary()

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
        await _open_character_detail(pilot)

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

        assert isinstance(app.screen, CharacterDetailScreen)

    saga = storage.load_saga("test_saga")
    character = saga.characters[0]
    assert len(character.abilities) == 1
    assert character.abilities[0].name == "Craft: Blacksmith"
    assert character.abilities[0].score == 2


async def test_cancelling_ability_details_returns_to_picker_without_adding():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_character_detail(pilot)

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
        await _open_character_detail(pilot)

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
        await _open_character_detail(pilot)
        assert "Magic Theory" in app.screen._summary()

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

        await pilot.press("enter")
        await pilot.pause()

        assert isinstance(app.screen, CharacterDetailScreen)
        assert "Magic Theory" not in app.screen._summary()

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].abilities == []


async def test_remove_virtue_flaw_from_character():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_character_detail(pilot)
        assert "Affinity with Creo" in app.screen._summary()

        await pilot.press("V")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

        await pilot.press("enter")
        await pilot.pause()

        assert isinstance(app.screen, CharacterDetailScreen)
        assert "Affinity with Creo" not in app.screen._summary()

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].virtues_flaws == []


async def test_remove_virtue_flaw_from_laboratory():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_covenant_detail(pilot)

        await pilot.click("#laboratory-lab1")
        await pilot.pause()
        assert isinstance(app.screen, LaboratoryDetailScreen)
        assert "Superior Lab Equipment" in app.screen._summary()

        await pilot.press("V")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

        await pilot.press("enter")
        await pilot.pause()

        assert isinstance(app.screen, LaboratoryDetailScreen)
        assert "Superior Lab Equipment" not in app.screen._summary()

    saga = storage.load_saga("test_saga")
    assert saga.laboratories[0].virtues_flaws == []


async def test_remove_with_nothing_to_remove_stays_on_same_screen():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_character_detail(pilot)

        await pilot.press("A")
        await pilot.pause()

        # Nothing to remove -- stays on the character screen, no picker opened.
        assert isinstance(app.screen, CharacterDetailScreen)


async def test_cancelling_removal_picker_keeps_the_item():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_character_detail(pilot)

        await pilot.press("V")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

        await pilot.press("escape")
        await pilot.pause()

        assert isinstance(app.screen, CharacterDetailScreen)
        assert "Affinity with Creo" in app.screen._summary()

    saga = storage.load_saga("test_saga")
    assert len(saga.characters[0].virtues_flaws) == 1
