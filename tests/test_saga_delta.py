"""A storyguide's change to the whole saga, folded into the host's
(saga_delta.py, ADR 0014)."""

from __future__ import annotations

import copy
from dataclasses import asdict

import pytest
from test_seat_view import hidden_saga

from ars_magica_manager.saga_delta import DeltaRefused, fold, saga_delta


def _delta(change: object) -> tuple[dict, dict]:
    saga = hidden_saga()
    base = asdict(saga)
    now = copy.deepcopy(base)
    change(now)  # type: ignore[operator]
    return saga_delta(base, now)


def test_only_what_changed_is_sent_record_by_record() -> None:
    def rename(now: dict) -> None:
        now["characters"][0]["name"] = "Leandro the Bold"
        now["current_year"] += 1

    before, after = _delta(rename)
    record = next(iter(k for k in after if k.startswith("characters[")))
    assert set(after) == {record, "current_year"}
    assert after[record]["name"] == "Leandro the Bold"
    assert before["current_year"] + 1 == after["current_year"]


def test_a_change_made_meanwhile_is_kept_unless_it_touched_the_same_place() -> None:
    host = hidden_saga()
    seat = asdict(host)
    now = copy.deepcopy(seat)
    now["characters"][0]["name"] = "Leandro the Bold"
    before, after = saga_delta(seat, now)
    # Meanwhile a player changed another character, and a field of this one.
    host.characters[1].name = "Changed meanwhile"
    host.characters[0].sihr_realm = "Faerie"
    folded = fold(host, before, after)
    assert folded.saga.characters[0].name == "Leandro the Bold"
    assert folded.saga.characters[0].sihr_realm == "Faerie"
    assert folded.saga.characters[1].name == "Changed meanwhile"
    assert not folded.advanced and folded.overlaps == []


def test_records_added_and_deleted() -> None:
    host = hidden_saga()
    seat = asdict(host)
    now = copy.deepcopy(seat)
    gone = now["characters"].pop(0)
    added = copy.deepcopy(now["characters"][0])
    added["id"] = "new-one"
    added["name"] = "New Grog"
    now["characters"].append(added)
    folded = fold(host, *saga_delta(seat, now))
    ids = [c.id for c in folded.saga.characters]
    assert gone["id"] not in ids and "new-one" in ids


def test_advancing_is_marked_and_a_second_advance_is_refused() -> None:
    host = hidden_saga()
    seat = asdict(host)
    now = copy.deepcopy(seat)
    now["current_season"] = "Summer"
    folded = fold(host, *saga_delta(seat, now))
    assert folded.advanced and folded.saga.current_season == "Summer"
    folded.saga.saved_by = "Bruno"
    with pytest.raises(DeltaRefused) as refused:
        fold(folded.saga, *saga_delta(seat, now))
    assert refused.value.advanced == f"Bruno|Summer {host.current_year}"


def test_the_players_are_the_hosts() -> None:
    host = hidden_saga()
    seat = asdict(host)
    now = copy.deepcopy(seat)
    now["players"][0]["role"] = "storyguide"
    with pytest.raises(DeltaRefused):
        fold(host, *saga_delta(seat, now))


def test_a_place_the_saga_hasnt_is_refused() -> None:
    with pytest.raises(DeltaRefused):
        fold(hidden_saga(), {}, {"no_such_field": 1})
