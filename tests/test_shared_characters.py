"""Characters played by more than one player (troupe-style), or by everyone
in the troupe: who plays them, who may change them, and older saves' one
player moved over."""

from __future__ import annotations

from dataclasses import asdict

from ars_magica_manager import players as pl
from ars_magica_manager import storage
from ars_magica_manager.forms import character as character_forms
from ars_magica_manager.models import Character, Player, Saga
from ars_magica_manager.models.character import Background


def _troupe() -> tuple[Saga, Player, Player, Player]:
    saga = Saga(id="s", name="S")
    ana = Player(id="ana", name="Ana", role=pl.PLAYER)
    ben = Player(id="ben", name="Ben", role=pl.PLAYER)
    gus = Player(id="gus", name="Gus", role=pl.STORYGUIDE)
    saga.players = [ana, ben, gus]
    shared = Character(id="c1", name="Shared", type="companion")
    shared.background.player_ids = [ana.id, ben.id]
    grog = Character(id="g1", name="Gunther", type="grog")
    grog.background.everyone_plays = True
    alone = Character(id="m1", name="Alone", type="magus")
    alone.background.player_ids = [ana.id]
    saga.characters = [shared, grog, alone]
    return saga, ana, ben, gus


def test_an_older_saves_one_player_moves_over() -> None:
    assert Background.from_dict({"player_id": "ana"}).player_ids == ["ana"]
    assert Background.from_dict({"player_id": None}).player_ids == []
    newer = Background.from_dict({"player_ids": ["ben"], "player_id": "ana"})
    assert newer.player_ids == ["ben"]


def test_who_plays_what() -> None:
    saga, ana, ben, gus = _troupe()
    assert [c.id for c in pl.characters_of(saga, ana)] == ["c1", "g1", "m1"]
    assert [c.id for c in pl.characters_of(saga, ben)] == ["c1", "g1"]
    assert pl.characters_of(saga, gus) == []  # everyone means the players
    assert pl.played_by(saga.characters[0].background, saga.players) == "Ana, Ben"
    assert pl.played_by(saga.characters[1].background, saga.players) == (
        "Everyone in the troupe"
    )
    assert pl.may_change(saga, ben, saga.characters[0])
    assert not pl.may_change(saga, ben, saga.characters[2])


def test_each_player_of_a_shared_character_may_change_it() -> None:
    saga, _ana, ben, _gus = _troupe()
    before = asdict(saga)
    after = asdict(saga)
    after["characters"][0]["name"] = "Shared, renamed by Ben"
    after["characters"][1]["name"] = "Gunther the Bold"
    kept, refused = pl.guard_changes(ben, before, after)
    assert refused == []
    assert kept["characters"][0]["name"] == "Shared, renamed by Ben"
    assert kept["characters"][1]["name"] == "Gunther the Bold"


def test_only_the_storyguide_says_who_plays_a_character() -> None:
    saga, ana, ben, gus = _troupe()
    before = asdict(saga)
    after = asdict(saga)
    after["characters"][2]["background"]["player_ids"] = [ana.id, ben.id]
    kept, refused = pl.guard_changes(ana, before, after)
    assert kept["characters"][2]["background"]["player_ids"] == [ana.id]
    assert refused == ["characters[m1].background.player_ids"]
    kept, refused = pl.guard_changes(gus, before, after)
    assert refused == [] and kept["characters"][2]["background"]["player_ids"] == [
        ana.id,
        ben.id,
    ]


def test_a_change_of_the_wrong_shape_plays_no_one() -> None:
    _saga, ana, _ben, _gus = _troupe()
    assert not pl.plays(["not", "a", "record"], ana)
    assert not pl.plays({"player_ids": "ana"}, ana)  # not a list
    assert not pl.plays({"everyone_plays": "yes"}, ana)  # not True


def test_removing_a_player_takes_them_off_every_character() -> None:
    saga, ana, _ben, _gus = _troupe()
    pl.remove(saga, ana)
    assert saga.characters[0].background.player_ids == ["ben"]
    assert saga.characters[2].background.player_ids == []


def test_the_biographical_form_ticks_players_and_everyone() -> None:
    saga, ana, ben, _gus = _troupe()
    character = saga.characters[2]
    fields = character_forms.played_by_field(character.background, saga.players, True)
    keys = [f.key for f in fields]
    assert keys == [
        "everyone_plays",
        f"plays_{ana.id}",
        f"plays_{ben.id}",
        "steward_id",
    ]
    character_forms.apply_biographical(
        character, {"everyone_plays": False, "plays_ana": True, "plays_ben": True}
    )
    assert character.background.player_ids == ["ana", "ben"]
    character_forms.apply_biographical(character, {"everyone_plays": True})
    assert character.background.everyone_plays


def test_a_save_round_trips_the_players() -> None:
    saga, *_ = _troupe()
    storage.save_saga(saga)
    loaded = storage.load_saga(saga.id)
    assert loaded.characters[0].background.player_ids == ["ana", "ben"]
    assert loaded.characters[1].background.everyone_plays
