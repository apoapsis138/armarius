"""My sheet in the core: which characters are a player's own, in order,
and whose sheet My sheet opens (players.my_characters, players.my_sheet);
and the records beside one on the trail (siblings.py)."""

from __future__ import annotations

import pytest

from ars_magica_manager import players, siblings, viewing
from ars_magica_manager.models import Character, Covenant, Laboratory, Player, Saga


@pytest.fixture(autouse=True)
def _storyguide_again():
    yield
    viewing.use(viewing.STORYGUIDE_VIEWER)


def _person(cid: str, name: str, kind: str = "magus", covenant: str | None = "home"):
    return Character(id=cid, name=name, type=kind, covenant_id=covenant)  # type: ignore[arg-type]


def _saga() -> Saga:
    ana = Player(id="ana", name="Ana", role=players.PLAYER)
    sg = Player(id="sg", name="Sam", role=players.STORYGUIDE)
    shared = _person("grog1", "Bertolf", "grog")
    shared.background.everyone_plays = True
    aurelia = _person("mag1", "Aurelia of Bonisagus")
    aurelia.background.player_ids = ["ana"]
    hugo = _person("comp1", "Hugo", "companion")
    hugo.background.player_ids = ["ana"]
    kept = _person("grog2", "Wenzel", "grog")
    kept.background.steward_id = "ana"
    other = _person("mag2", "Leandro")
    other.background.player_ids = ["ben"]
    return Saga(
        id="s",
        name="S",
        # The shared grog comes first in the saga, ahead of her own.
        characters=[shared, aurelia, hugo, kept, other],
        covenants=[Covenant(id="home", saga_id="s", name="Fengheld", played=True)],
        players=[ana, sg],
    )


# -- My sheet --


def test_her_own_characters_come_before_those_everyone_plays():
    saga = _saga()
    mine = players.my_characters(saga, saga.players[0])
    assert [c.id for c in mine] == ["mag1", "comp1", "grog1"]
    # The same characters as the Troupe page's Your Characters, reordered;
    # a stewarded one is not hers.
    assert {c.id for c in mine} == {
        c.id for c in players.characters_of(saga, saga.players[0])
    }


def test_my_sheet_is_her_first_named_character():
    saga = _saga()
    assert players.my_sheet(saga, saga.players[0]).id == "mag1"  # type: ignore[union-attr]


def test_my_sheet_is_the_one_last_opened_while_it_is_hers():
    saga = _saga()
    ana = saga.players[0]
    assert players.my_sheet(saga, ana, "comp1").id == "comp1"  # type: ignore[union-attr]
    assert players.my_sheet(saga, ana, "grog1").id == "grog1"  # type: ignore[union-attr]
    # Someone else's, or one gone: her first again.
    assert players.my_sheet(saga, ana, "mag2").id == "mag1"  # type: ignore[union-attr]
    assert players.my_sheet(saga, ana, "gone").id == "mag1"  # type: ignore[union-attr]


def test_an_everyone_plays_character_is_hers_only_when_none_names_her():
    saga = _saga()
    for c in saga.characters:
        c.background.player_ids = []
    assert players.my_sheet(saga, saga.players[0]).id == "grog1"  # type: ignore[union-attr]


def test_no_sheet_with_no_characters_in_the_storyguide_role_or_a_solo_saga():
    saga = _saga()
    for c in saga.characters:
        c.background.player_ids = []
        c.background.everyone_plays = False
    assert players.my_sheet(saga, saga.players[0]) is None
    # The storyguide's role, and a saga with no players: no one to play.
    assert players.my_sheet(_saga(), None) is None
    solo = _saga()
    solo.players = []
    assert players.my_sheet(solo, None, "mag1") is None


# -- siblings --


def _world() -> Saga:
    saga = _saga()
    hidden = _person("npc1", "Secret Grog", "grog")
    hidden.known = False
    loner = _person("lone", "Wandering Hermit", covenant=None)
    saga.characters += [hidden, loner]
    saga.covenants += [
        Covenant(id="sketch", saga_id="s", name="Durenmar", played=False),
        Covenant(
            id="unknown", saga_id="s", name="Hidden Keep", played=False, known=False
        ),
        Covenant(id="second", saga_id="s", name="Second Home", played=True),
    ]
    saga.laboratories = [
        Laboratory(id="lab1", covenant_id="home", name="North Tower"),
        Laboratory(id="lab2", covenant_id="sketch", name="Elsewhere"),
        Laboratory(id="lab3", covenant_id="home", name="Cellar"),
    ]
    return saga


def _listed(saga: Saga, kind: str, record_id: str | None) -> list[tuple[str, str]]:
    return [(s.group, s.name) for s in siblings.siblings(saga, kind, record_id)]


def test_a_characters_siblings_are_their_covenants_people_by_group():
    saga = _world()
    assert _listed(saga, siblings.CHARACTER, "comp1") == [
        ("Magi", "Aurelia of Bonisagus"),
        ("Magi", "Leandro"),
        ("Companions", "Hugo"),
        ("Grogs", "Bertolf"),
        ("Grogs", "Wenzel"),
        ("Grogs", "Secret Grog"),
    ]
    # One of no covenant: the saga's unassigned people.
    assert _listed(saga, siblings.CHARACTER, "lone") == [("Magi", "Wandering Hermit")]


def test_a_laboratorys_siblings_are_its_covenants_laboratories():
    saga = _world()
    assert _listed(saga, siblings.LABORATORY, "lab3") == [
        ("", "North Tower"),
        ("", "Cellar"),
    ]


def test_the_covenants_are_the_troupes_then_the_regions():
    saga = _world()
    assert _listed(saga, siblings.COVENANT, "home") == [
        (siblings.TROUPE, "Fengheld"),
        (siblings.TROUPE, "Second Home"),
        (siblings.REGION, "Durenmar"),
        (siblings.REGION, "Hidden Keep"),
    ]


def test_player_view_and_a_seat_list_only_what_they_may_read():
    saga = _world()
    for viewer in (
        viewing.TABLE_VIEWER,
        viewing.Viewer(viewing.PLAYER, saga.players[0]),
    ):
        viewing.use(viewer, saga)
        people = [name for _g, name in _listed(saga, siblings.CHARACTER, "mag1")]
        assert "Secret Grog" not in people and "Aurelia of Bonisagus" in people
        covenants = [name for _g, name in _listed(saga, siblings.COVENANT, "home")]
        assert "Hidden Keep" not in covenants and "Durenmar" in covenants


def test_nothing_for_a_record_gone_or_a_kind_without_siblings():
    saga = _world()
    assert _listed(saga, siblings.CHARACTER, "gone") == []
    assert _listed(saga, siblings.LABORATORY, None) == []
    assert _listed(saga, "tribunal", "any") == []
