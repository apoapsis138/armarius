"""Vis sources still waiting at Advance Season, with Harvest Vis by Hand on:
listed with a tick each (ticked, the covenfolk gather it; unticked, it is
lost for the year), Cancel leaving the date, and a downtime run gathering
every one itself."""

from __future__ import annotations

from typing import Any

from ars_magica_manager import commands, seasons, vis_harvest
from ars_magica_manager.forms import advance, downtime
from ars_magica_manager.models import Covenant, Possession, Saga

WAITING = "Vis Sources Waiting"


def _saga(**source_kw: object) -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep")
    covenant.possessions = [
        Possession(
            "well",
            "vis_source",
            name="Healing Well",
            art="Corpus",
            pawns=4,
            season="Summer",
            **source_kw,  # type: ignore[arg-type]
        ),
        Possession(
            "pond", "vis_source", name="Pond", art="Aquam", pawns=2, season="Summer"
        ),
    ]
    saga = Saga(id="s", name="S", covenants=[covenant], current_season="Summer")
    saga.harvest_vis_by_hand = True
    return saga


def _stores(saga: Saga) -> dict[str, int]:
    return {
        p.art: p.pawns for p in saga.covenants[0].possessions if p.kind == "vis_store"
    }


def _answer(asked: list[str], ticks: dict[str, bool] | None = None) -> Any:
    """Answer each step as given: the waiting list with `ticks` by label
    (None: Cancel it), every other form as it comes, every question Yes."""

    def ask(question: commands.Question) -> object:
        title = getattr(question, "title", "")
        asked.append(title)
        if isinstance(question, commands.Form):
            fields = question.fields()
            values = {f.key: f.value for f in fields}
            if title == WAITING:
                if ticks is None:
                    return commands.CANCELLED
                for f in fields:
                    for label, ticked in ticks.items():
                        if f.kind == "check" and label in f.label:
                            values[f.key] = ticked
            return values
        return True

    return ask


def _advance(saga: Saga, asked: list[str], ticks: dict[str, bool] | None = None):
    return commands.drive(advance.play_season(saga), _answer(asked, ticks))


# -- which sources are waiting --


def test_the_sources_waiting_are_those_that_could_be_harvested_now():
    saga = _saga()
    assert [s.id for _c, s in seasons.waiting_sources(saga, {})] == ["well", "pond"]
    saga.covenants[0].possessions[0].harvested_year = 1220
    assert [s.id for _c, s in seasons.waiting_sources(saga, {})] == ["pond"]
    saga.harvest_vis_by_hand = False
    assert seasons.waiting_sources(saga, {}) == []


def test_a_contested_source_secured_this_season_is_waiting_too():
    saga = _saga(contested=True, secured_until=1219)
    assert [s.id for _c, s in seasons.waiting_sources(saga, {})] == ["pond"]
    secured = {"well": True}
    found = seasons.waiting_sources(saga, secured)
    assert [s.id for _c, s in found] == ["well", "pond"]


# -- the season's play --


def test_a_source_the_covenfolk_gather_is_harvested_and_counted():
    saga = _saga()
    lines = seasons.covenant_season(saga, {}, gathered=frozenset({"well"}))
    assert _stores(saga) == {"Corpus": 4}
    diary = saga.covenants[0].diary
    assert diary[0].name == "Vis harvested: Healing Well"
    assert vis_harvest.COVENFOLK in diary[0].details
    assert diary[1].name == "Pond not harvested"
    assert lines[0].result == "4 Corpus"


# -- Advance Season --


def test_advance_lists_each_waiting_source_with_a_tick():
    saga = _saga()
    asked: list[str] = []
    _advance(saga, asked, {"Healing Well": True, "Pond": False})
    assert WAITING in asked
    assert saga.current_season == "Autumn"
    assert _stores(saga) == {"Corpus": 4}
    names = [e.name for e in saga.covenants[0].diary]
    assert names == ["Vis harvested: Healing Well", "Pond not harvested"]


def test_the_list_names_each_source_with_its_covenant():
    saga = _saga()
    asked: list[str] = []
    seen: list[str] = []

    def ask(question: commands.Question) -> object:
        if getattr(question, "title", "") == WAITING:
            assert isinstance(question, commands.Form)
            seen.extend(f.label for f in question.fields() if f.kind == "check")
        return _answer(asked, {})(question)

    commands.drive(advance.play_season(saga), ask)
    assert any("Keep's Healing Well" in label for label in seen)
    assert any("Keep's Pond" in label for label in seen)


def test_cancel_on_the_list_leaves_the_date():
    saga = _saga()
    asked: list[str] = []
    _advance(saga, asked, None)
    assert WAITING in asked
    assert saga.current_season == "Summer"
    assert _stores(saga) == {} and saga.covenants[0].diary == []


def test_nothing_is_asked_when_no_source_is_waiting():
    saga = _saga()
    for source in saga.covenants[0].possessions:
        source.harvested_year = 1220  # both gathered by hand already
    asked: list[str] = []
    _advance(saga, asked, {})
    assert WAITING not in asked
    off = _saga()
    off.harvest_vis_by_hand = False
    _advance(off, asked, {})
    assert WAITING not in asked
    assert _stores(off) == {"Corpus": 4, "Aquam": 2}


def test_a_downtime_run_gathers_every_waiting_source_itself():
    saga = _saga()
    saga.current_season = "Spring"
    asked: list[str] = []
    form = downtime.downtime_form(saga)
    filled = {f.key: f.value for f in form.fields()} | {
        "season": "Autumn",
        "year": 1220,
    }
    outcome = commands.drive(form.apply(filled), _answer(asked, None))
    while isinstance(outcome, commands.Then):
        outcome = commands.drive(outcome.step, _answer(asked, None))
    assert WAITING not in asked
    assert saga.current_season == "Autumn"
    assert _stores(saga) == {"Corpus": 4, "Aquam": 2}
    assert all(vis_harvest.COVENFOLK in e.details for e in saga.covenants[0].diary)
