import pytest
from textual.widgets import Input, ListView

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
    CharacterDetailScreen,
    CovenantCreateScreen,
    CovenantDetailScreen,
    LaboratoryDetailScreen,
    LibraryDetailScreen,
    SagaCreateScreen,
    SagaDetailScreen,
    SagaPickerScreen,
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
