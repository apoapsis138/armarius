"""The covenant's seasons (STORY-906): vis harvests, Contested and Dwindling
Resources."""

from ars_magica_manager import economics, seasons
from ars_magica_manager.models import Covenant, IncomeSource, Possession, Saga


def _saga(**source_kw) -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep")
    covenant.possessions = [
        Possession(
            "well",
            "vis_source",
            name="Healing Well",
            art="Corpus",
            pawns=4,
            season="Summer",
            **source_kw,
        ),
        Possession("store", "vis_store", name="Corpus vis", art="Corpus", pawns=2),
    ]
    saga = Saga(id="s", name="S", covenants=[covenant])
    saga.current_season = "Summer"
    return saga


def _store(saga):
    return next(p for p in saga.covenants[0].possessions if p.kind == "vis_store")


def test_a_vis_source_is_harvested_in_its_season():
    saga = _saga()
    lines = seasons.covenant_season(saga, {})
    assert _store(saga).pawns == 6
    assert saga.covenants[0].diary[-1].name == "Vis harvested: Healing Well"
    assert lines[0].result == "4 Corpus"
    saga.current_season = "Autumn"
    seasons.covenant_season(saga, {})
    assert _store(saga).pawns == 6  # not its season


def test_an_unaddressed_contested_source_gives_nothing():
    saga = _saga(contested=True, secured_until=1219)
    assert seasons.lapsed_resources(saga) == [("well", "Keep's Healing Well")]
    seasons.covenant_season(saga, {"well": False})
    assert _store(saga).pawns == 2  # no harvest
    assert saga.covenants[0].diary[-1].name == "Healing Well not harvested"
    seasons.covenant_season(saga, {"well": True})
    well = saga.covenants[0].possessions[0]
    assert well.secured_until == 1224 and _store(saga).pawns == 6
    assert seasons.lapsed_resources(saga) == []


def test_an_unresolved_income_source_gives_nothing_and_is_noted_at_year_end():
    saga = _saga()
    saga.current_season = "Winter"
    covenant = saga.covenants[0]
    covenant.economics.income_sources = [
        IncomeSource("mill", "Mill", contested=True, dwindling=True)
    ]
    assert economics.summarize(saga, covenant).income == 0  # not yet secured
    assert seasons.lapsed_resources(saga) == [("mill", "Keep's Mill")]
    seasons.covenant_season(saga, {"mill": False})
    assert covenant.diary[-1].name == "Mill not received"
    mill = covenant.economics.income_sources[0]
    assert mill.income == 90  # Dwindling: -10% a year
    mill.secured_until = 1224
    assert economics.summarize(saga, covenant).income == 90


async def test_advancing_asks_whether_a_lapsed_resource_was_secured():
    from support import everything_saga, wait_until
    from textual.widgets import Button

    from ars_magica_manager import storage
    from ars_magica_manager.app import ArsMagicaManagerApp
    from ars_magica_manager.screens.prompts import ConfirmScreen

    saga = everything_saga()
    covenant = saga.covenants[0]
    covenant.possessions.append(
        Possession(
            "well",
            "vis_source",
            name="Healing Well",
            art="Corpus",
            pawns=4,
            season=saga.current_season,
            contested=True,
        )
    )
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await pilot.press("enter")
        await pilot.pause()
        workspace = app.screen
        await pilot.press("t")
        await pilot.pause()
        app.screen.query_one("#btn-advance", Button).press()
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        app.screen.query_one("#btn-yes", Button).press()
        assert await wait_until(
            pilot, lambda: workspace.saga.current_season != saga.current_season
        )
    saved = storage.load_saga(saga.id)
    well = next(p for p in saved.covenants[0].possessions if p.id == "well")
    assert well.secured_until == saga.current_year + 4
    assert any(
        p.kind == "vis_store" and p.art == "Corpus"
        for p in saved.covenants[0].possessions
    )
