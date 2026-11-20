"""Show (shows.py; glossary: Show): the Session's storyguide shows a record
or a saga picture to the Table or chosen Players while the Session is
Under way. One frozen Player-view copy is written beside the saga; the
Chronicle's "show" entry names it, and who it is for."""

from __future__ import annotations

import json

import pytest

from ars_magica_manager import (
    chronicle,
    paths,
    references,
    show_copy,
    shows,
    table_rules,
    viewing,
)
from ars_magica_manager.models import (
    STORY_EVENT,
    AtlasMap,
    Casting,
    Character,
    Covenant,
    CovenantDiaryEntry,
    Player,
    Saga,
    Secret,
    Session,
)

HOST = viewing.HOST
PICTURE = b"\x89PNG\r\n\x1a\n" + b"rhine" * 20


def _hilda() -> Character:
    """Old Hilda, known to the troupe, with one Secret revealed and one
    not, and private notes; she lives at a covenant the troupe doesn't
    know of."""
    hilda = Character(id="hilda", name="Old Hilda", type="companion", covenant_id="k")
    hilda.known = True
    hilda.secrets = [
        Secret("Seen", "SHOWN-SECRET", 1220, "Spring"),
        Secret("Kept", "KEPT-SECRET"),
    ]
    hilda.private_notes = "PRIVATE-NOTE"
    return hilda


def _begun() -> tuple[Saga, Session, chronicle.Chronicle]:
    """Ana plays Aelfric and Ben Brigit tonight; Cara is Away. The host
    runs the Session, which is Under way."""
    saga = Saga(id="fengheld", name="Fengheld")
    saga.players = [Player("ana", "Ana"), Player("ben", "Ben"), Player("cara", "Cara")]
    saga.covenants = [
        Covenant(
            id="k", saga_id="fengheld", name="Hidden Keep", played=False, known=False
        ),
        Covenant(id="f", saga_id="fengheld", name="Fengheld", played=True),
    ]
    saga.covenants[1].diary = [
        CovenantDiaryEntry(
            1220, name="The Black Tower", category=STORY_EVENT, status="Open"
        )
    ]
    saga.covenants[1].diary[0].id = "tower"
    saga.characters = [
        Character(id="aelfric", name="Aelfric", type="magus"),
        Character(id="brigit", name="Brigit", type="companion"),
        _hilda(),
    ]
    saga.maps = [AtlasMap(id="m", name="The Rhine", picture="rhine.png")]
    maps = paths.data_dir() / paths.MAPS
    maps.mkdir(parents=True, exist_ok=True)
    (maps / "rhine.png").write_bytes(PICTURE)
    session = Session(
        "s1",
        coming=["ana", "ben"],
        away=["cara"],
        castings=[Casting("ana", "aelfric"), Casting("ben", "brigit")],
    )
    saga.sessions = [session]
    return saga, session, chronicle.begin(saga, session, by=HOST)


def _hilda_ref() -> references.Ref:
    return references.Ref("characters", "hilda", "Old Hilda")


def _show(
    book: chronicle.Chronicle,
    saga: Saga,
    session: Session,
    call: chronicle.ShowCall,
    by: str = HOST,
) -> chronicle.Entry:
    return shows.show(book, saga, session, call, by=by, copier=show_copy.player_copy)


# -- who may --


def test_only_the_sessions_storyguide_shows_and_only_while_it_is_under_way() -> None:
    saga, session, book = _begun()
    call = chronicle.ShowCall("Hilda", record=_hilda_ref())

    assert shows.why_not_show(saga, session, call, "ana") == (
        "Only the Session's storyguide shows something."
    )
    assert shows.why_not_show(saga, session, call, HOST) is None
    with pytest.raises(ValueError, match="storyguide"):
        _show(book, saga, session, call, by="ana")
    session.under_way = False
    assert shows.why_not_show(saga, session, call, HOST) == (
        "The Session isn't under way."
    )


def test_the_who_may_rule_is_the_tables_one_for_every_storyguide_verb() -> None:
    saga, session, _book = _begun()
    assert table_rules.why_not_lead(saga, session, HOST, "shows something") is None
    assert table_rules.why_not_lead(saga, session, "ben", "ends a scene") == (
        "Only the Session's storyguide ends a scene."
    )


def test_a_show_is_to_players_at_the_session_and_of_something_showable() -> None:
    saga, session, _book = _begun()

    def why(**asked: object) -> str | None:
        call = chronicle.ShowCall(**{"title": "T", "record": _hilda_ref(), **asked})  # type: ignore[arg-type]
        return shows.why_not_show(saga, session, call, HOST)

    assert why(to=("cara",)) == "Show only to Players at the Session."
    assert why(to=(HOST,)) == "Show only to Players at the Session."
    assert why(title="  ") == "Give the Show a title."
    assert why(record=references.Ref("characters", "gone", "Gone")) == (
        "Choose a record or picture to show."
    )
    assert why(record=None) == "Choose a record or picture to show."
    assert why(record=None, picture=("maps", "nowhere.png")) == (
        "Choose a record or picture to show."
    )
    assert why(record=None, picture=("maps", "rhine.png")) is None


# -- the entry --


def test_a_show_to_chosen_players_is_for_each_of_them_and_seen_by_them_alone() -> None:
    saga, session, book = _begun()

    entry = _show(
        book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref(), to=("ana",))
    )

    assert entry.kind == chronicle.SHOW
    assert {
        w for w in ("ana", "ben", HOST) if chronicle.sees(entry, w, session, saga)
    } == {
        "ana",
        HOST,
    }
    assert chronicle.for_whom(entry, session, saga) == {"ana"}
    assert entry.body["title"] == "Hilda"
    assert entry.body["to_names"] == ["Ana"]
    assert entry.body["ref"] == ["characters", "hilda", "Old Hilda"]
    stamped = chronicle.stamped(entry, "ana", session, saga)
    assert "to" not in stamped.body and stamped.for_you is True


def test_a_show_to_the_table_is_seen_by_all_and_pulses_no_one() -> None:
    saga, session, book = _begun()

    entry = _show(book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref()))

    assert entry.audience.to == chronicle.TABLE
    assert chronicle.for_whom(entry, session, saga) == frozenset()
    assert chronicle.line(entry, {}) == "The storyguide shows: Hilda"


def test_a_show_names_the_story_it_belongs_to() -> None:
    saga, session, book = _begun()

    entry = _show(
        book,
        saga,
        session,
        chronicle.ShowCall("Hilda", _hilda_ref(), story_id="tower"),
    )

    assert (entry.body["story_id"], entry.body["story"]) == ("tower", "The Black Tower")


def test_a_shows_typed_title_keeps_the_character_rule() -> None:
    saga, session, _book = _begun()
    call = chronicle.ShowCall("Bad\x07title", _hilda_ref())
    assert shows.why_not_show(saga, session, call, HOST) is not None


# -- the frozen copy --


def test_the_copy_is_the_player_view_without_kept_secrets_notes_or_unknown_names() -> (
    None
):
    saga, session, book = _begun()

    entry = _show(book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref()))
    copy = shows.opened(saga.id, entry)

    assert copy.title == "Hilda"
    assert "Old Hilda" in copy.text
    assert "SHOWN-SECRET" in copy.text
    for hidden in ("KEPT-SECRET", "PRIVATE-NOTE", "Hidden Keep"):
        assert hidden not in copy.text
    assert copy.picture is None


def test_the_copy_is_kept_beside_the_saga_and_stays_as_it_was_shown() -> None:
    saga, session, book = _begun()
    entry = _show(book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref()))
    saga.characters[2].name = "Hilda the Changed"
    saga.characters[2].secrets[1].revealed_year = 1221

    copy = shows.opened(saga.id, entry)

    kept = paths.data_dir() / shows.FOLDER / saga.id / f"{entry.body['show']}.json"
    assert json.loads(kept.read_text(encoding="utf-8"))["text"] == copy.text
    assert "Hilda the Changed" not in copy.text
    assert "KEPT-SECRET" not in copy.text


def test_a_picture_is_copied_as_it_is() -> None:
    saga, session, book = _begun()

    entry = _show(
        book,
        saga,
        session,
        chronicle.ShowCall("The Rhine", picture=("maps", "rhine.png"), to=("ben",)),
    )
    (paths.data_dir() / paths.MAPS / "rhine.png").write_bytes(b"changed since")
    copy = shows.opened(saga.id, entry)

    assert copy.picture == PICTURE
    assert entry.body["picture"] == copy.picture_name
    assert copy.picture_name.endswith(".png")
    assert shows.picture_bytes(saga.id, copy.picture_name) == PICTURE


def test_only_a_player_shown_may_open_a_show() -> None:
    saga, session, book = _begun()
    entry = _show(
        book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref(), to=("ana",))
    )
    show_id = str(entry.body["show"])

    assert shows.seen(saga, show_id, "ana") == entry
    assert shows.seen(saga, show_id, HOST) == entry
    assert shows.seen(saga, show_id, "ben") is None
    assert shows.seen(saga, "no-such-show", "ana") is None


def test_only_a_picture_of_a_show_a_player_sees_is_theirs_to_fetch() -> None:
    saga, session, book = _begun()
    entry = _show(
        book,
        saga,
        session,
        chronicle.ShowCall("The Rhine", picture=("maps", "rhine.png"), to=("ben",)),
    )
    name = str(entry.body["picture"])

    assert shows.shows_picture(saga, name, "ben")
    assert not shows.shows_picture(saga, name, "ana")
    assert not shows.shows_picture(saga, "other.png", "ben")


# -- from the review --


def test_a_story_of_a_covenant_the_troupe_doesnt_play_isnt_offered() -> None:
    """The host's rule is the form's: open stories of the troupe's
    covenants only."""
    saga, session, _book = _begun()
    hidden = saga.covenants[0]
    hidden.diary = [
        CovenantDiaryEntry(1220, name="Their Plot", category=STORY_EVENT, status="Open")
    ]
    hidden.diary[0].id = "plot"
    call = chronicle.ShowCall("Hilda", _hilda_ref(), story_id="plot")

    assert shows.why_not_show(saga, session, call, HOST) == "That story isn't open."


def test_a_damaged_chronicle_hides_only_its_own_shows() -> None:
    saga, session, book = _begun()
    entry = _show(
        book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref(), to=("ana",))
    )
    old = Session("s0", played=True)
    saga.sessions.insert(0, old)
    path = chronicle.path_of(saga, old)
    path.write_text("not json\n{}\n", encoding="utf-8")

    assert shows.seen(saga, str(entry.body["show"]), "ana") == entry


def test_a_copy_that_cant_be_made_says_so_and_leaves_no_file() -> None:
    saga, session, book = _begun()

    def broken(_saga: Saga, _record: object) -> str:
        raise KeyError("sheet")

    with pytest.raises(ValueError, match="copy couldn't be made"):
        shows.show(
            book,
            saga,
            session,
            chronicle.ShowCall("Hilda", _hilda_ref()),
            by=HOST,
            copier=broken,
        )
    assert shows.files_of(saga.id) == []


def test_a_picture_whose_copy_fails_to_save_leaves_no_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    saga, session, book = _begun()

    def full(*_args: object, **_kwargs: object) -> int:
        raise OSError("disk full")

    monkeypatch.setattr(type(paths.data_dir()), "write_text", full)
    with pytest.raises(OSError):
        _show(
            book,
            saga,
            session,
            chronicle.ShowCall("Map", picture=("maps", "rhine.png")),
        )
    assert shows.files_of(saga.id) == []
