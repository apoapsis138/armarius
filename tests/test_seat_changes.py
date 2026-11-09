"""A Remote seat's change merged back onto the full saga (ADR 0010): the
Player's edit is kept, what is hidden from them survives it, and what is
not theirs to change is refused."""

from __future__ import annotations

from dataclasses import asdict

import pytest
from test_seat_view import hidden_saga

from ars_magica_manager import players, viewing
from ars_magica_manager.models import Character, Player, Saga, Secret
from ars_magica_manager.seat_changes import ChangeRefused, apply_change, record_key
from ars_magica_manager.seat_view import seat_view


def _saga() -> tuple[Saga, Player]:
    saga = hidden_saga()
    anna = players.find(saga, "Anna")
    assert anna is not None
    magus = saga.characters[0]
    magus.background.player_ids = [anna.id]
    magus.secrets.append(Secret("Hers", "LEAK-CHARSECRET"))
    return saga, anna


def _seen(saga: Saga, anna: Player, kind: str, record_id: str) -> dict:
    view = asdict(seat_view(saga, viewing.viewer_for(anna)))
    return next(r for r in view[kind] if r["id"] == record_id)


def test_a_players_edit_is_kept_and_what_they_cant_see_survives_it():
    saga, anna = _saga()
    before = _seen(saga, anna, "characters", saga.characters[0].id)
    assert "LEAK-CHARSECRET" not in str(before) and "LEAK-LINK" not in str(before)
    after = {**before, "name": "Leandro the Bold"}
    done = apply_change(saga, anna, "characters", before["id"], before, after)
    magus = done.saga.characters[0]
    assert magus.name == "Leandro the Bold"
    assert "LEAK-CHARSECRET" in str(magus.secrets)  # the hidden secret
    assert "LEAK-LINK" in str(magus.links)  # the link to an unknown place
    assert done.overlaps == []


def test_a_covenant_change_keeps_its_hidden_diary_lines_and_secrets():
    saga, anna = _saga()
    anna.covenant_rights = True
    covenant = saga.covenants[0]
    before = _seen(saga, anna, "covenants", covenant.id)
    after = {**before, "name": "Keep Renamed"}
    done = apply_change(saga, anna, "covenants", covenant.id, before, after)
    changed = done.saga.covenants[0]
    assert changed.name == "Keep Renamed"
    assert "LEAK-COVDIARY" in str(changed.diary) and "LEAK-SECRET" in str(
        changed.secrets
    )


def test_secrets_sent_by_a_player_are_ignored():
    saga, anna = _saga()
    before = _seen(saga, anna, "characters", saga.characters[0].id)
    forged = {**before, "secrets": [asdict(Secret("Mine", "planted"))]}
    done = apply_change(saga, anna, "characters", before["id"], before, forged)
    assert "planted" not in str(done.saga.characters[0].secrets)
    assert "LEAK-CHARSECRET" in str(done.saga.characters[0].secrets)


def test_another_players_character_or_a_covenant_without_rights_is_refused():
    saga, anna = _saga()
    other = Character(id="other", name="Bertrand", type="magus")
    saga.characters.append(other)
    seen_other = _seen(saga, anna, "characters", "other")
    with pytest.raises(ChangeRefused):
        apply_change(
            saga, anna, "characters", "other", seen_other, {**seen_other, "name": "X"}
        )
    covenant = _seen(saga, anna, "covenants", saga.covenants[0].id)
    with pytest.raises(ChangeRefused):
        apply_change(
            saga, anna, "covenants", covenant["id"], covenant, {**covenant, "name": "X"}
        )


def test_an_unknown_record_cant_be_changed():
    saga, anna = _saga()
    with pytest.raises(ChangeRefused):
        apply_change(
            saga, anna, "characters", "grove", None, {"id": "grove", "name": "x"}
        )
    with pytest.raises(ChangeRefused):
        apply_change(saga, anna, "neighbours", "grove", None, {"id": "grove"})


def test_an_overlap_is_won_by_the_later_save_and_reported():
    saga, anna = _saga()
    before = _seen(saga, anna, "characters", saga.characters[0].id)
    saga.characters[0].name = "Renamed by the storyguide"
    after = {**before, "name": "Renamed by Anna"}
    done = apply_change(saga, anna, "characters", before["id"], before, after)
    assert done.saga.characters[0].name == "Renamed by Anna"
    assert done.overlaps == ["characters.name"]


def test_a_season_plan_only_for_ones_own_character():
    saga, anna = _saga()
    mine = {
        "character_id": saga.characters[0].id,
        "year": 1221,
        "season": "Spring",
        "activity": "practice",
    }
    key = record_key("season_plans", mine)
    done = apply_change(saga, anna, "season_plans", key, None, mine)
    assert any(p.year == 1221 for p in done.saga.season_plans)
    saga.characters.append(Character(id="other", name="Bertrand", type="magus"))
    theirs = {**mine, "character_id": "other"}
    with pytest.raises(ChangeRefused):
        apply_change(
            saga, anna, "season_plans", record_key("season_plans", theirs), None, theirs
        )


def test_a_seat_sends_every_list_a_player_may_change() -> None:
    """Whatever guard_changes lets a player change (a list not refused as a
    whole), a Remote seat sends: a list missing from CHANGEABLE never
    reaches the host from a seat."""
    from ars_magica_manager.seat_changes import CHANGEABLE

    saga, anna = _saga()
    before = asdict(saga)
    after = dict(before)
    for key, value in before.items():
        if isinstance(value, list):
            after[key] = [*value, {"id": "zz-new", "character_id": "zz"}]
        elif isinstance(value, dict):
            after[key] = {**value, "zz-new": 1}
        elif isinstance(value, bool):
            after[key] = not value
        elif isinstance(value, int):
            after[key] = value + 1
        elif isinstance(value, str):
            after[key] = value + "x"
        elif value is None:
            after[key] = ["zz-new"]
    _kept, refused = players.guard_changes(anna, before, after)
    whole = {r for r in refused if "[" not in r}
    open_to_players = {k for k in before if k not in whole} - {"app_version"}
    assert open_to_players <= CHANGEABLE, open_to_players - CHANGEABLE


def test_a_teaching_ask_from_a_seat() -> None:
    saga, anna = _saga()
    mine = saga.characters[0].id
    ask = {
        "id": "ask1",
        "student_id": mine,
        "teacher_id": "someone-elses",
        "subject": "ability:Latin",
        "season": "Spring",
        "year": 1221,
        "status": "asked",
        "note": "",
    }
    done = apply_change(saga, anna, "teach_requests", "ask1", None, ask)
    assert [r.id for r in done.saga.teach_requests] == ["ask1"]
    theirs = {**ask, "id": "ask2", "student_id": "nobody-of-hers"}
    with pytest.raises(ChangeRefused):
        apply_change(saga, anna, "teach_requests", "ask2", None, theirs)


def test_a_steward_plans_the_season_of_a_character_kept_unknown() -> None:
    saga, anna = _saga()
    grog = Character(id="grog", name="Hob", type="grog")
    grog.known = False
    grog.background.steward_id = anna.id
    saga.characters.append(grog)
    plan = {"character_id": "grog", "year": 1221, "season": "Spring", "activity": "x"}
    done = apply_change(
        saga, anna, "season_plans", record_key("season_plans", plan), None, plan
    )
    assert any(p.character_id == "grog" for p in done.saga.season_plans)


def test_a_change_must_name_the_record_it_carries():
    saga, anna = _saga()
    before = _seen(saga, anna, "characters", saga.characters[0].id)
    with pytest.raises(ChangeRefused):
        apply_change(saga, anna, "characters", "someone-else", before, before)
