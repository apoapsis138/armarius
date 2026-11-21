"""Setting and ending a Scene (scene_play.py): while a Session is Under
way its storyguide sets one of the Session's Scenes, which posts a banner
to the Table and ends the one playing; End scene and End Session end it.
A use's state (Prepared, Playing, Ended) moves by one table of moves
(scenes.MOVES); while the Session is Under way the Chronicle's entries
are those moves, replayed over the state kept on the Session, and End
Session writes where they ended back to it."""

from __future__ import annotations

import pytest

from ars_magica_manager import chronicle, scene_play, scenes, viewing
from ars_magica_manager.models import (
    AtlasMap,
    Casting,
    Character,
    Covenant,
    Neighbour,
    Player,
    Saga,
    Scene,
    SceneUse,
    Session,
)

HOST = viewing.HOST


def _begun() -> tuple[Saga, Session, chronicle.Chronicle]:
    """Ana plays Aelfric tonight, which the host runs. Three Scenes are
    loaded: the ford (a typed place, Faerie 2, with a map), the
    Drachenfels (a Place the players don't know of, Magic 3) and Fengheld
    (the troupe's covenant)."""
    saga = Saga(id="s", name="Saga")
    saga.players = [Player("ana", "Ana")]
    saga.characters = [Character(id="aelfric", name="Aelfric", type="magus")]
    saga.covenants = [Covenant(id="c", saga_id="s", name="Fengheld", played=True)]
    saga.neighbours = [
        Neighbour(
            id="drachen",
            name="The Drachenfels",
            kind="place",
            realm="Magic",
            known=False,
            details={"aura": 3},
        )
    ]
    saga.maps = [AtlasMap(id="m", name="The Rhine", picture="rhine.png")]
    saga.scenes = [
        Scene(
            "ford",
            title="The ford",
            place_name="A ford on the Rhine",
            aura=2,
            realm="Faerie",
            picture="rhine.png",
        ),
        Scene("hill", title="The hill", place_id="drachen", aura=3, realm="Magic"),
        Scene("home", title="Home", covenant_id="c", aura=4, realm="Magic"),
    ]
    session = Session("tonight", castings=[Casting("ana", "aelfric")])
    session.scenes = [
        SceneUse("u-ford", scene_id="ford"),
        SceneUse("u-hill", scene_id="hill"),
        SceneUse("u-home", scene_id="home"),
    ]
    saga.sessions = [session]
    return saga, session, chronicle.begin(saga, session, by=HOST)


def _set(
    book: chronicle.Chronicle,
    saga: Saga,
    session: Session,
    use_id: str,
    *,
    tell_aura: bool = False,
    by: str = HOST,
) -> chronicle.Entry:
    call = chronicle.SceneCall(use_id, tell_aura=tell_aura)
    return scene_play.set_scene(book, saga, session, call, by=by)


def _states(session: Session, book: chronicle.Chronicle) -> dict[str, str]:
    return scene_play.now(session, book)


# -- the State --


def test_each_move_of_the_state_is_decided_by_one_table() -> None:
    p, playing, ended = scenes.PREPARED, scenes.PLAYING, scenes.ENDED
    assert scenes.MOVES == {
        (p, scenes.SET): playing,
        (ended, scenes.SET): playing,
        (playing, scenes.END): ended,
    }
    assert scenes.why_not_move(p, scenes.SET) is None
    assert scenes.why_not_move(playing, scenes.SET) == "This Scene is already playing."
    assert scenes.why_not_move(p, scenes.END) == "This Scene isn't playing."
    assert scenes.why_not_move(ended, scenes.END) == "This Scene isn't playing."


def test_replaying_the_moves_plays_one_scene_at_a_time() -> None:
    saga, session, _book = _begun()
    now = scenes.replay(
        session,
        [("u-ford", scenes.SET), ("u-hill", scenes.SET), ("u-ford", scenes.SET)],
    )
    assert now == {
        "u-ford": scenes.PLAYING,
        "u-hill": scenes.ENDED,
        "u-home": scenes.PREPARED,
    }
    assert saga.scenes  # the replay changes nothing kept
    assert [u.state for u in session.scenes] == [scenes.PREPARED] * 3


def test_a_move_the_table_refuses_is_passed_over_and_one_taken_out_too() -> None:
    _saga, session, _book = _begun()
    now = scenes.replay(
        session,
        [("u-hill", scenes.END), ("gone", scenes.SET), ("u-home", scenes.SET)],
    )
    assert now["u-hill"] == scenes.PREPARED and now["u-home"] == scenes.PLAYING


# -- setting a Scene --


def test_only_the_sessions_storyguide_sets_a_scene_and_only_while_under_way() -> None:
    saga, session, book = _begun()
    call = chronicle.SceneCall("u-ford")
    assert scene_play.why_not_set(saga, session, call, "ana", book) == (
        "Only the Session's storyguide sets a Scene."
    )
    with pytest.raises(ValueError, match="storyguide"):
        _set(book, saga, session, "u-ford", by="ana")
    chronicle.end(saga, session, by=HOST)
    assert scene_play.why_not_set(saga, session, call, HOST, book) == (
        "The Session isn't under way."
    )


def test_setting_a_scene_posts_a_banner_to_the_table_without_its_aura() -> None:
    saga, session, book = _begun()
    entry = _set(book, saga, session, "u-ford")
    assert entry.kind == chronicle.SCENE_SET
    assert entry.audience == chronicle.table()
    assert entry.body == {
        "use": "u-ford",
        "title": "The ford",
        "place": "A ford on the Rhine",
        "picture": "rhine.png",
    }
    assert chronicle.KINDS[chronicle.SCENE_SET].line(entry.body) == (
        "Scene: The ford, at A ford on the Rhine"
    )


def test_the_banner_tells_the_aura_only_when_asked() -> None:
    saga, session, book = _begun()
    entry = _set(book, saga, session, "u-ford", tell_aura=True)
    assert entry.body["aura"] == "Faerie 2"
    assert chronicle.KINDS[chronicle.SCENE_SET].line(entry.body) == (
        "Scene: The ford, at A ford on the Rhine (aura Faerie 2)"
    )


def test_the_banner_names_the_place_as_the_players_know_it() -> None:
    saga, session, book = _begun()
    hill = _set(book, saga, session, "u-hill")
    home = _set(book, saga, session, "u-home")
    assert hill.body["place"] == "an unknown place"
    assert "Drachenfels" not in str(hill.body)
    assert home.body["place"] == "Fengheld"
    assert "place_ref" not in hill.body
    assert home.body["place_ref"] == ["covenants", "c"]
    saga.neighbours[0].known = True
    known = _set(book, saga, session, "u-hill")
    assert known.body["place"] == "The Drachenfels"
    assert known.body["place_ref"] == ["neighbours", "drachen"]


def test_the_banner_never_names_a_regio_level() -> None:
    saga, session, book = _begun()
    saga.neighbours[0].known = True
    saga.neighbours[0].details["levels"] = [{"name": "The Hidden Vineyard"}]
    saga.scenes[1].place_level = 1
    body = _set(book, saga, session, "u-hill").body
    assert body["place"] == "The Drachenfels"
    assert "Vineyard" not in str(body)


def test_an_unknown_place_reads_as_its_typed_description() -> None:
    saga, session, book = _begun()
    saga.scenes[1].place_name = "A wooded crag"
    assert _set(book, saga, session, "u-hill").body["place"] == "A wooded crag"


def test_setting_a_scene_ends_the_one_playing() -> None:
    saga, session, book = _begun()
    _set(book, saga, session, "u-ford")
    _set(book, saga, session, "u-hill")
    assert _states(session, book) == {
        "u-ford": scenes.ENDED,
        "u-hill": scenes.PLAYING,
        "u-home": scenes.PREPARED,
    }
    assert scene_play.playing(session, book) is session.scenes[1]


def test_an_ended_scene_can_be_set_again_as_a_new_entry() -> None:
    saga, session, book = _begun()
    first = _set(book, saga, session, "u-ford")
    _set(book, saga, session, "u-hill")
    again = _set(book, saga, session, "u-ford")
    assert again.number > first.number
    assert _states(session, book)["u-ford"] == scenes.PLAYING


def test_the_scene_playing_cant_be_set_again() -> None:
    saga, session, book = _begun()
    _set(book, saga, session, "u-ford")
    with pytest.raises(ValueError, match="already playing"):
        _set(book, saga, session, "u-ford")


def test_a_scene_not_loaded_or_since_deleted_cant_be_set() -> None:
    saga, session, book = _begun()
    with pytest.raises(ValueError, match="isn't loaded"):
        _set(book, saga, session, "nowhere")
    saga.scenes = saga.scenes[1:]
    with pytest.raises(ValueError, match="deleted"):
        _set(book, saga, session, "u-ford")


# -- ending one --


def test_end_scene_ends_the_one_playing_and_says_so() -> None:
    saga, session, book = _begun()
    with pytest.raises(ValueError, match="No Scene is playing"):
        scene_play.end_scene(book, saga, session, by=HOST)
    _set(book, saga, session, "u-ford")
    ended = scene_play.end_scene(book, saga, session, by=HOST)
    assert (ended.kind, ended.audience) == (chronicle.SCENE_ENDED, chronicle.table())
    assert ended.body == {"use": "u-ford", "title": "The ford"}
    assert chronicle.KINDS[chronicle.SCENE_ENDED].line(ended.body) == (
        "Scene ended: The ford"
    )
    assert scene_play.playing(session, book) is None
    with pytest.raises(ValueError, match="storyguide"):
        scene_play.end_scene(book, saga, session, by="ana")


def test_end_session_ends_the_playing_scene_and_keeps_each_ones_state() -> None:
    saga, session, book = _begun()
    _set(book, saga, session, "u-ford")
    _set(book, saga, session, "u-hill")
    scene_play.end_session(saga, session, by=HOST)
    assert [e.kind for e in book.entries[-2:]] == [chronicle.SCENE_ENDED, chronicle.END]
    assert [u.state for u in session.scenes] == [
        scenes.ENDED,
        scenes.ENDED,
        scenes.PREPARED,
    ]
    assert session.played and not session.under_way


def test_a_scene_never_set_stays_prepared_after_end_session_and_can_move() -> None:
    saga, session, _book = _begun()
    later = Session("later")
    saga.sessions.append(later)
    scene_play.end_session(saga, session, by=HOST)
    home = session.scenes[2]
    assert scenes.state(session, home) == scenes.PREPARED
    assert scenes.allows(session, home).move


def test_only_the_sessions_storyguide_ends_it() -> None:
    saga, session, _book = _begun()
    with pytest.raises(ValueError, match="storyguide"):
        scene_play.end_session(saga, session, by="ana")
    assert session.under_way


def test_while_under_way_the_state_comes_from_the_chronicle() -> None:
    saga, session, book = _begun()
    _set(book, saga, session, "u-ford")
    now = _states(session, book)
    ford = session.scenes[0]
    assert scenes.state(session, ford) == scenes.PREPARED  # as kept
    assert scenes.state(session, ford, now) == scenes.PLAYING
    assert not scenes.allows(session, ford, now).take_out
    assert scenes.why_not_delete(saga, saga.scenes[0], now) is not None


def test_a_played_session_keeps_what_was_left_playing_as_ended() -> None:
    _saga, session, _book = _begun()
    session.played = True
    session.scenes[0].state = scenes.PLAYING
    session.scenes[1].state = "a state this version doesn't know"
    states = [scenes.state(session, u) for u in session.scenes]
    assert states == [scenes.ENDED, scenes.ENDED, scenes.PREPARED]
