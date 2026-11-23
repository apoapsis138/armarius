"""Harvest Vis by Hand: the "could be harvested now" rule with its reason,
the Harvest form, and the season's play with the setting on and off."""

from __future__ import annotations

from dataclasses import asdict

import pytest

from ars_magica_manager import seasons, seat, storage, undo_season, vis_harvest
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import covenant as cov_forms
from ars_magica_manager.forms import more
from ars_magica_manager.forms.more.covenant import VIS_SOURCES
from ars_magica_manager.forms.page import Page
from ars_magica_manager.models import Character, Covenant, Player, Possession, Saga


def _saga(*, by_hand: bool = True, **source_kw: object) -> Saga:
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
        Possession("store", "vis_store", name="Corpus vis", art="Corpus", pawns=2),
    ]
    saga = Saga(id="s", name="S", covenants=[covenant])
    saga.characters.append(
        Character(id="mag1", name="Leandro", type="magus", covenant_id="cov")
    )
    saga.current_season = "Summer"
    saga.harvest_vis_by_hand = by_hand
    return saga


def _well(saga: Saga) -> Possession:
    return saga.covenants[0].possessions[0]


def _store(saga: Saga) -> Possession:
    return next(p for p in saga.covenants[0].possessions if p.kind == "vis_store")


def _form(saga: Saga) -> Form:
    step = cov_forms.harvest_form(saga, saga.covenants[0], _well(saga))
    assert isinstance(step, Form)
    return step


# -- the rule --


def test_a_source_may_be_harvested_by_hand_in_its_own_season():
    saga = _saga()
    assert vis_harvest.refusal(saga, _well(saga)) == ""
    assert vis_harvest.harvestable(saga, _well(saga))


@pytest.mark.parametrize(
    ("change", "reason"),
    [
        (lambda s: setattr(s, "harvest_vis_by_hand", False), "Harvest Vis by Hand"),
        (lambda s: setattr(s, "current_season", "Autumn"), "harvested in Summer"),
        (lambda s: setattr(_well(s), "harvested_year", 1220), "Already harvested"),
        (lambda s: setattr(_well(s), "contested", True), "Settle"),
        (lambda s: setattr(_well(s), "pawns", 0), "no Art or pawns"),
        (lambda s: setattr(_well(s), "art", ""), "no Art or pawns"),
    ],
)
def test_a_source_that_may_not_be_harvested_says_why(change, reason):
    saga = _saga()
    change(saga)
    assert reason in vis_harvest.refusal(saga, _well(saga))
    assert not vis_harvest.harvestable(saga, _well(saga))


def test_last_years_harvest_doesnt_stop_this_years():
    saga = _saga(harvested_year=1219)
    assert vis_harvest.harvestable(saga, _well(saga))


def test_a_settled_contested_source_may_be_harvested():
    saga = _saga(contested=True, secured_until=1224)
    assert vis_harvest.harvestable(saga, _well(saga))


# -- the Harvest form --


def test_the_form_offers_the_covenant_and_the_covenfolk_and_the_usual_yield():
    saga = _saga()
    fields = {f.key: f for f in _form(saga).fields()}
    assert fields["harvester"].value == ""
    assert fields["harvester"].options == [("The covenfolk", ""), ("Leandro", "mag1")]
    assert fields["pawns"].value == 4
    assert fields["note"].value == ""


def test_harvesting_fills_the_store_marks_the_year_and_writes_the_diary():
    saga = _saga()
    _form(saga).apply({"harvester": "mag1", "pawns": 3, "note": "A wolf watched."})
    assert _store(saga).pawns == 5
    assert _well(saga).harvested_year == 1220
    assert _well(saga).pawns == 4  # this year's harvest only
    entry = saga.covenants[0].diary[-1]
    assert entry.name == "Vis harvested: Healing Well"
    assert (entry.year, entry.season, entry.category) == (
        1220,
        "Summer",
        "Covenant Season",
    )
    assert (entry.vis_pawns, entry.vis_art) == (3, "Corpus")
    assert "Leandro" in entry.details and "A wolf watched." in entry.details
    assert not vis_harvest.harvestable(saga, _well(saga))


def test_the_covenfolk_may_harvest_and_a_new_store_is_made_when_none_fits():
    saga = _saga()
    saga.covenants[0].possessions.pop()  # no store of Corpus vis
    _form(saga).apply({"harvester": "", "pawns": 4, "note": ""})
    [store] = [p for p in saga.covenants[0].possessions if p.kind == "vis_store"]
    assert (store.art, store.pawns) == ("Corpus", 4)
    assert "The covenfolk" in saga.covenants[0].diary[-1].details


def test_a_poor_year_of_nothing_makes_no_empty_store():
    saga = _saga()
    saga.covenants[0].possessions.pop()
    _form(saga).apply({"harvester": "", "pawns": 0, "note": "The well ran dry."})
    assert not [p for p in saga.covenants[0].possessions if p.kind == "vis_store"]
    assert _well(saga).harvested_year == 1220


def test_negative_pawns_are_refused():
    form = _form(_saga())
    assert form.validate is not None
    assert form.validate({"harvester": "", "pawns": -1, "note": ""})
    assert not form.validate({"harvester": "", "pawns": 0, "note": ""})


def test_a_source_that_may_not_be_harvested_is_refused_with_the_reason():
    saga = _saga(harvested_year=1220)
    step = cov_forms.harvest_form(saga, saga.covenants[0], _well(saga))
    assert isinstance(step, Refuse) and "Already harvested" in step.why


def test_harvesting_costs_nobody_a_season():
    saga = _saga()
    _form(saga).apply({"harvester": "mag1", "pawns": 4, "note": ""})
    assert saga.season_plans == []
    assert saga.characters[0].diary == []


# -- the terminal's More --


def _on_sources(saga: Saga) -> Page:
    """The covenant's Vis Sources list, its first source chosen."""
    return Page(
        saga,
        NodeKind.COVENANT,
        covenant=saga.covenants[0],
        section=VIS_SOURCES,
        rows=lambda section: 0 if section == VIS_SOURCES else None,
    )


def test_more_offers_harvest_on_a_source_while_the_saga_gathers_by_hand():
    saga = _saga()
    assert more.available("harvest_vis", _on_sources(saga))
    saga.harvest_vis_by_hand = False
    assert not more.available("harvest_vis", _on_sources(saga))


def test_mores_harvest_on_a_source_it_cant_harvest_says_why():
    saga = _saga(harvested_year=1220)
    step = more.STEPS["harvest_vis"](_on_sources(saga))
    assert isinstance(step, Refuse) and "Already harvested" in step.why
    assert isinstance(more.STEPS["harvest_vis"](_on_sources(_saga())), Form)


def test_more_offers_settle_on_a_contested_source_only():
    assert not more.available("settle_vis_source", _on_sources(_saga()))
    saga = _saga(contested=True)
    assert more.available("settle_vis_source", _on_sources(saga))
    step = more.STEPS["settle_vis_source"](_on_sources(saga))
    assert isinstance(step, Form) and step.title == "Settle Healing Well"


# -- the season's play --


def test_with_the_setting_off_the_season_harvests_as_before():
    saga = _saga(by_hand=False)
    lines = seasons.covenant_season(saga, {})
    assert _store(saga).pawns == 6
    assert lines[0].result == "4 Corpus"
    assert _well(saga).harvested_year == 1220


def test_with_the_setting_on_a_source_left_waiting_is_lost_for_the_year():
    saga = _saga()
    lines = seasons.covenant_season(saga, {})
    assert _store(saga).pawns == 2
    assert saga.covenants[0].diary[-1].name == "Healing Well not harvested"
    assert lines == []


def test_a_source_harvested_by_hand_is_not_harvested_again_and_is_counted():
    saga = _saga()
    _form(saga).apply({"harvester": "mag1", "pawns": 5, "note": ""})
    lines = seasons.covenant_season(saga, {})
    assert _store(saga).pawns == 7
    assert [e.name for e in saga.covenants[0].diary] == ["Vis harvested: Healing Well"]
    assert lines[0].activity == "Vis harvest" and lines[0].result == "5 Corpus"


def test_an_unsecured_contested_source_keeps_its_old_behaviour():
    saga = _saga(contested=True, secured_until=1219)
    seasons.covenant_season(saga, {"well": False})
    assert saga.covenants[0].diary[-1].details == (
        "A contested resource not yet secured: no harvest."
    )


# -- saves, seats and undo --


def test_an_older_save_loads_with_the_setting_off():
    saga = _saga()
    data = asdict(saga)
    del data["harvest_vis_by_hand"]
    del data["covenants"][0]["possessions"][0]["harvested_year"]
    loaded = storage.saga_from_data(data)
    assert loaded.harvest_vis_by_hand is False
    assert loaded.covenants[0].possessions[0].harvested_year is None


def test_a_new_saga_starts_with_the_setting_off():
    assert Saga(id="n", name="New").harvest_vis_by_hand is False


@pytest.mark.parametrize("action", ["harvest_vis", "settle_vis_source"])
def test_only_a_player_with_covenant_rights_may_harvest_or_settle(action):
    saga = _saga()
    anna = Player("p1", "Anna")
    saga.players.append(anna)
    covenant = saga.covenants[0]
    assert not seat.may_act(saga, anna, action, covenant)
    anna.covenant_rights = True
    assert seat.may_act(saga, anna, action, covenant)


def test_undo_last_season_takes_back_the_season_after_a_hand_harvest():
    """Undo Last Season puts the saga back as it stood before the advance:
    the hand harvest made in the season undone is kept, as it was, and
    what the advance did to the covenant goes."""
    saga = _saga()
    saga.covenants[0].possessions.append(
        Possession(
            "pond", "vis_source", name="Pond", art="Aquam", pawns=2, season="Summer"
        )
    )
    storage.save_saga(saga)
    _form(saga).apply({"harvester": "mag1", "pawns": 4, "note": ""})
    storage.save_saga(saga)
    storage.backup_saga(saga)  # as Advance Season does
    seasons.covenant_season(saga, {})  # the Pond, left waiting, is lost
    saga.current_season = "Autumn"
    storage.remember_after(saga)
    storage.save_saga(saga)
    found = undo_season.offer(saga)
    assert found is not None
    undo_season.undo(saga, found)
    assert saga.current_season == "Summer"
    assert _store(saga).pawns == 6 and _well(saga).harvested_year == 1220
    assert [e.name for e in saga.covenants[0].diary] == ["Vis harvested: Healing Well"]
    pond = saga.covenants[0].possessions[-1]
    assert vis_harvest.harvestable(saga, pond)  # still waiting, as before
