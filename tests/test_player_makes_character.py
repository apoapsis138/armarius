"""A player makes their own character: one they may add, named as its
Player, through the one guard every save passes (players.guard_changes),
at a browser seat or a Remote seat alike."""

from __future__ import annotations

from dataclasses import asdict

import pytest

from ars_magica_manager import creation, players, seat, viewing
from ars_magica_manager.forms import creation as creation_forms
from ars_magica_manager.models import (
    Character,
    CharacterType,
    Covenant,
    Player,
    Saga,
)
from ars_magica_manager.seat_changes import ChangeRefused, apply_change


@pytest.fixture(autouse=True)
def _empty_seat():
    yield
    seat.sign_out()


def _saga() -> tuple[Saga, Player]:
    ana = Player(id="ana", name="Ana", role=players.PLAYER)
    saga = Saga(
        id="s",
        name="S",
        covenants=[Covenant(id="home", saga_id="s", name="Fengheld")],
        players=[ana, Player(id="ben", name="Ben", role=players.PLAYER)],
    )
    return saga, ana


def _new(
    player_ids: list[str], kind: CharacterType = "magus", **background: object
) -> dict:
    record = asdict(Character(id="new", name="Leandro", type=kind))
    record["background"].update(player_ids=player_ids, **background)
    return record


def _guarded(player: Player, record: dict) -> list[str]:
    before = {"characters": []}
    _kept, refused = players.guard_changes(player, before, {"characters": [record]})
    return refused


def test_a_new_character_naming_the_player_alone_is_theirs_to_add():
    ana = _saga()[1]
    assert _guarded(ana, _new(["ana"])) == []
    assert _guarded(ana, _new(["ana"], "companion")) == []


@pytest.mark.parametrize(
    "record",
    [
        _new([]),  # no one's
        _new(["ben"]),  # made for another player
        _new(["ana", "ben"]),  # handed a share to another
        _new([], everyone_plays=True),  # the troupe's
        _new([], steward_id="ana"),  # stewarded, not played
    ],
)
def test_any_other_new_character_is_refused(record: dict):
    ana = _saga()[1]
    assert _guarded(ana, record) == ["characters[new]"]


def test_a_grog_needs_covenant_rights():
    ana = _saga()[1]
    assert _guarded(ana, _new(["ana"], "grog")) == ["characters[new]"]
    ana.covenant_rights = True
    assert _guarded(ana, _new(["ana"], "grog")) == []


def test_a_player_still_cant_take_over_a_character_already_there():
    ana = _saga()[1]
    old = _new(["ben"])
    before = {"characters": [old]}
    taken = _new(["ana"])
    _kept, refused = players.guard_changes(ana, before, {"characters": [taken]})
    assert refused


def test_the_character_a_seated_player_makes_names_them():
    saga, ana = _saga()
    seat.sign_in(saga, ana)
    made = creation.add_character(saga, "Leandro", "magus", "home")
    assert made.background.player_ids == ["ana"]
    assert players.characters_of(saga, ana) == [made]


def test_the_storyguide_makes_a_character_no_one_plays():
    saga = _saga()[0]
    seat.sign_in(saga, None)
    made = creation.add_character(saga, "Leandro", "magus", "home")
    assert made.background.player_ids == []


def test_a_player_is_offered_new_character_on_the_saga_and_a_covenant():
    saga, ana = _saga()
    seat.sign_in(saga, ana)
    assert seat.may_act(saga, ana, "create_character")
    assert seat.may_act(saga, ana, "create_character", saga.covenants[0])
    assert not seat.may_act(saga, ana, "create_covenant")
    assert not seat.may_act(saga, ana, "create_laboratory")


def test_a_player_without_covenant_rights_isnt_offered_a_grog():
    saga, ana = _saga()
    seat.sign_in(saga, ana)
    kinds = [k for _, k in creation_forms.makeable_types()]
    assert "grog" not in kinds and "magus" in kinds
    # The covenant's Grogs New card opens the form on a Type they may make.
    fields = creation_forms.character_create_fields(saga, "home", "grog")
    assert fields[1].value == "magus"
    ana.covenant_rights = True
    assert "grog" in [k for _, k in creation_forms.makeable_types()]


def test_a_remote_seat_adds_the_character_its_player_made():
    saga, ana = _saga()
    seat.sign_in(saga, ana, hosts=False)
    copy = Saga(**{**saga.__dict__, "characters": []})
    made = creation.add_character(copy, "Leandro", "magus", "home")
    seat.sign_out()
    done = apply_change(saga, ana, "characters", made.id, None, asdict(made))
    added = done.saga.character(made.id)
    assert added is not None and players.plays(added.background, ana)


def test_a_remote_seat_cant_add_a_character_for_someone_else():
    saga, ana = _saga()
    record = _new(["ben"])
    with pytest.raises(ChangeRefused):
        apply_change(saga, ana, "characters", "new", None, record)


def test_only_a_player_is_seated_as_a_maker():
    saga, ana = _saga()
    seat.sign_in(saga, ana)
    assert viewing.seated_player() is ana
    guide = Player(id="sg", name="Sam", role=players.STORYGUIDE)
    seat.sign_in(saga, guide, player_view=True)  # a storyguide Playing
    assert viewing.seated_player() is None
