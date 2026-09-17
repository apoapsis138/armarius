import pytest
from textual.widgets import Input, ListView

from ars_magica_manager import storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import Character, Covenant, Laboratory, Library, Saga
from ars_magica_manager.screens import (
    CovenantDetailScreen,
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


async def test_covenant_browsing_shows_counts_and_detail():
    saga = Saga(
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
            Character(id="char1", name="Leandro", type="magus", covenant_id="cov1")
        ],
        laboratories=[Laboratory(id="lab1", covenant_id="cov1")],
        libraries=[Library(id="lib1", covenant_id="cov1", books=["book1", "book2"])],
    )
    storage.save_saga(saga)

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
        assert "Library: 2 book(s)" in summary
        assert "Characters (1):" in summary
        assert "- Leandro (magus)" in summary
        assert "Laboratories (1):" in summary
