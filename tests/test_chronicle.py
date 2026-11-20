"""A Session's Chronicle (chronicle.py; ADRs 0018 and 0020): Begin and End
Session, rolls made at the host, who sees each entry, Void, and the file
it is kept in beside the saga.

Expected die results are the book's: Ars Magica Definitive Edition,
Chapter One, Simple Die, Stress Die and Botch Dice, pp. 7-8."""

from __future__ import annotations

import json
import random

import pytest

from ars_magica_manager import chronicle, paths, viewing
from ars_magica_manager.models import Casting, Character, Player, Saga, Session

HOST = viewing.HOST


class Faces(random.Random):
    """A d10 that shows the faces it is given, in order (0-9, as thrown)."""

    def __init__(self, *faces: int) -> None:
        super().__init__()
        self.faces = list(faces)

    def randrange(self, *_args: object, **_kwargs: object) -> int:  # type: ignore[override]
        return self.faces.pop(0)


def _saga() -> Saga:
    """Ana plays Aelfric tonight; Ben is coming but plays no one; the
    saga's own storyguide (the host) runs the Session."""
    saga = Saga(id="fengheld", name="Fengheld")
    saga.players = [Player("ana", "Ana"), Player("ben", "Ben")]
    saga.characters = [
        Character(id="aelfric", name="Aelfric", type="magus"),
        Character(id="gus", name="Gus", type="grog"),
    ]
    saga.sessions = [
        Session(
            "s1",
            coming=["ana", "ben"],
            castings=[Casting(player_id="ana", character_id="aelfric")],
        ),
        Session("s2"),
    ]
    return saga


def _begun() -> tuple[Saga, Session, chronicle.Chronicle]:
    saga = _saga()
    session = saga.sessions[0]
    return saga, session, chronicle.begin(saga, session, by=HOST)


# -- Begin and End Session --


def test_begin_session_puts_the_session_under_way_with_an_empty_chronicle() -> None:
    saga, session, book = _begun()

    assert session.under_way and not session.played
    assert chronicle.under_way(saga) is session
    assert [e.kind for e in book.entries] == ["begin"]


def test_only_the_sessions_storyguide_may_begin_it() -> None:
    saga = _saga()
    session = saga.sessions[0]

    assert chronicle.why_not_begin(saga, session, "ana") == (
        "Only the Session's storyguide begins it."
    )
    session.storyguide_id = "ana"
    assert chronicle.why_not_begin(saga, session, "ana") is None
    assert chronicle.why_not_begin(saga, session, HOST) is not None


def test_one_session_of_a_saga_is_under_way_at_a_time() -> None:
    saga, _session, _book = _begun()

    assert chronicle.why_not_begin(saga, saga.sessions[1], HOST) == (
        "Another Session is under way: end it first."
    )
    with pytest.raises(ValueError):
        chronicle.begin(saga, saga.sessions[1], by=HOST)


def test_a_played_session_is_not_begun_again() -> None:
    saga = _saga()
    saga.sessions[0].played = True

    assert chronicle.why_not_begin(saga, saga.sessions[0], HOST) == (
        "This Session has been played."
    )


def test_end_session_marks_it_played_and_closes_its_chronicle() -> None:
    saga, session, book = _begun()

    assert chronicle.why_not_end(session, "ana") == (
        "Only the Session's storyguide ends it."
    )
    chronicle.end(saga, session, by=HOST)

    assert session.played and not session.under_way
    assert chronicle.under_way(saga) is None
    assert book.closed
    with pytest.raises(ValueError):
        chronicle.free_roll(
            book, saga, session, chronicle.RollRequest(stress=False), by=HOST
        )
    assert [e.kind for e in chronicle.read(saga, session).entries] == ["begin", "end"]


def test_the_chronicle_is_a_file_beside_the_saga() -> None:
    book = _begun()[2]

    assert book.path == paths.data_dir() / "chronicles" / "fengheld" / "s1.jsonl"
    line = json.loads(book.path.read_text(encoding="utf-8").splitlines()[0])
    assert line["number"] == 1 and line["kind"] == "begin"
    assert line["audience"] == {"to": "table", "players": []}


def test_an_id_that_could_leave_the_folder_is_refused() -> None:
    saga = _saga()
    saga.sessions[0].id = "../s1"

    with pytest.raises(ValueError):
        chronicle.begin(saga, saga.sessions[0], by=HOST)


# -- rolls made at the host --


def _roll(
    book: chronicle.Chronicle,
    saga: Saga,
    session: Session,
    rng: random.Random,
    *,
    by: str = HOST,
    **asked: object,
) -> chronicle.Entry:
    request = chronicle.RollRequest(**asked)  # type: ignore[arg-type]
    return chronicle.free_roll(book, saga, session, request, by=by, rng=rng)


def test_a_stress_roll_keeps_every_doubling() -> None:
    """DE p. 7: two 1s then a 5 is 5 x 4 = 20; with +9 the total is 29."""
    saga, session, book = _begun()

    entry = _roll(book, saga, session, Faces(1, 1, 5), modifier=9, ease_factor=12)

    assert entry.kind == "roll" and entry.number == 2
    assert entry.body["faces"] == [1, 1, 5]
    assert entry.body["die"] == 20 and entry.body["total"] == 29
    assert entry.body["succeeded"] is True and entry.body["margin"] == 17


def test_a_botch_keeps_each_botch_die_and_totals_no_more_than_zero() -> None:
    """DE p. 7: a first 0 rolls the botch dice; any 0 among them botches,
    and the total is no higher than 0."""
    saga, session, book = _begun()

    entry = _roll(book, saga, session, Faces(0, 4, 0, 0), modifier=9, botch_dice=3)

    assert entry.body["faces"] == [0]
    assert entry.body["botch_faces"] == [4, 0, 0]
    assert entry.body["botches"] == 2 and entry.body["total"] == 0


def test_a_zero_with_no_botch_dice_is_simply_zero() -> None:
    """DE p. 7: a stress roll that can't botch reads a 0 as 0."""
    saga, session, book = _begun()

    entry = _roll(book, saga, session, Faces(0), modifier=6, botch_dice=0)

    assert entry.body["botch_faces"] == [] and entry.body["total"] == 6


def test_a_simple_die_reads_a_zero_as_ten() -> None:
    """DE p. 7: on a simple die a 0 counts as ten."""
    saga, session, book = _begun()

    entry = _roll(book, saga, session, Faces(0), stress=False, modifier=2)

    assert entry.body["stress"] is False and entry.body["total"] == 12


def test_asking_again_makes_a_second_roll() -> None:
    saga, session, book = _begun()

    first = _roll(book, saga, session, Faces(5), modifier=1)
    second = _roll(book, saga, session, Faces(7), modifier=1)

    assert (first.number, second.number) == (2, 3)
    assert [e.body["total"] for e in book.since(1)] == [6, 8]


def test_a_player_rolls_only_for_a_character_they_play_tonight() -> None:
    saga, session, book = _begun()

    gus = chronicle.RollRequest(character_id="gus")
    assert chronicle.why_not_roll(saga, session, gus, "ana") == (
        "Roll for a character you play tonight."
    )
    nobody = chronicle.RollRequest()
    assert chronicle.why_not_roll(saga, session, nobody, "ana") is not None
    with pytest.raises(ValueError):
        _roll(book, saga, session, Faces(5), by="ben", character_id="aelfric")
    entry = _roll(book, saga, session, Faces(5), by="ana", character_id="aelfric")
    assert entry.author == "ana" and entry.body["character_name"] == "Aelfric"


def test_the_sessions_storyguide_rolls_for_anyone_or_no_one() -> None:
    saga, session, _book = _begun()

    for character in ("gus", ""):
        asked = chronicle.RollRequest(character_id=character)
        assert chronicle.why_not_roll(saga, session, asked, HOST) is None


def test_only_the_storyguide_rolls_blind() -> None:
    saga, session, _book = _begun()

    asked = chronicle.RollRequest(character_id="aelfric", visibility=chronicle.BLIND)
    assert chronicle.why_not_roll(saga, session, asked, "ana") == (
        "Only the Session's storyguide rolls Blind."
    )


# -- who sees what --


def _seen(book: chronicle.Chronicle, session: Session, who: str) -> list[str]:
    return [e.kind for e in book.seen_by(who, session)][1:]


def test_a_public_roll_is_seen_by_everyone_at_the_session() -> None:
    saga, session, book = _begun()
    _roll(book, saga, session, Faces(5), by="ana", character_id="aelfric")

    for who in (HOST, "ana", "ben", ""):
        assert _seen(book, session, who) == ["roll"]


def test_a_private_roll_is_seen_by_the_roller_and_the_storyguide() -> None:
    saga, session, book = _begun()
    _roll(
        book,
        saga,
        session,
        Faces(5),
        by="ana",
        character_id="aelfric",
        visibility=chronicle.PRIVATE,
    )

    assert _seen(book, session, "ana") == ["roll"]
    assert _seen(book, session, HOST) == ["roll"]
    assert _seen(book, session, "ben") == []
    assert _seen(book, session, "") == []


def test_a_blind_rolls_number_is_the_storyguides_alone() -> None:
    saga, session, book = _begun()
    _roll(
        book,
        saga,
        session,
        Faces(5),
        character_id="aelfric",
        for_what="Notice the ambush",
        visibility=chronicle.BLIND,
    )

    assert _seen(book, session, HOST) == ["roll", "rolled"]
    assert _seen(book, session, "ana") == ["rolled"]
    rolled = book.seen_by("ana", session)[-1]
    assert "total" not in rolled.body and rolled.body["for"] == "Notice the ambush"
    assert _seen(book, session, "ben") == []


def test_another_storyguide_at_the_session_is_a_player_that_evening() -> None:
    """Troupe-style play: a second storyguide doesn't see a Blind roll."""
    saga, session, book = _begun()
    saga.players.append(Player("cara", "Cara", "storyguide"))
    _roll(book, saga, session, Faces(5), visibility=chronicle.BLIND)

    assert _seen(book, session, "cara") == []


def test_the_host_who_is_not_the_sessions_storyguide_sees_as_a_player() -> None:
    saga = _saga()
    session = saga.sessions[0]
    session.storyguide_id = "ben"
    book = chronicle.begin(saga, session, by="ben")
    _roll(book, saga, session, Faces(5), by="ben", visibility=chronicle.BLIND)

    assert _seen(book, session, HOST) == []
    assert _seen(book, session, "ben") == ["roll"]


def test_who_a_viewer_is_at_the_session() -> None:
    ana = Player("ana", "Ana")
    assert chronicle.person(viewing.viewer_for(ana)) == "ana"
    assert chronicle.person(viewing.STORYGUIDE_VIEWER) == HOST
    assert chronicle.person(viewing.TABLE_VIEWER) == ""


# -- Void --


def test_a_void_strikes_a_roll_with_a_reason_and_the_roll_stays() -> None:
    saga, session, book = _begun()
    roll = _roll(book, saga, session, Faces(5))

    chronicle.strike(book, session, roll.number, "Rolled for the wrong grog", by=HOST)

    assert [e.kind for e in book.entries] == ["begin", "roll", "void"]
    assert chronicle.voided(book) == {2: "Rolled for the wrong grog"}


def test_only_the_storyguide_voids_and_only_once_with_a_reason() -> None:
    saga, session, book = _begun()
    roll = _roll(book, saga, session, Faces(5), by="ana", character_id="aelfric")

    with pytest.raises(ValueError):
        chronicle.strike(book, session, roll.number, "No", by="ana")
    with pytest.raises(ValueError):
        chronicle.strike(book, session, roll.number, "  ", by=HOST)
    with pytest.raises(ValueError):
        chronicle.strike(book, session, 1, "Not a roll", by=HOST)
    chronicle.strike(book, session, roll.number, "Wrong roll", by=HOST)
    with pytest.raises(ValueError):
        chronicle.strike(book, session, roll.number, "Again", by=HOST)


def test_a_void_of_a_blind_roll_is_seen_only_by_who_saw_the_roll() -> None:
    saga, session, book = _begun()
    roll = _roll(book, saga, session, Faces(5), visibility=chronicle.BLIND)

    chronicle.strike(book, session, roll.number, "Never mind", by=HOST)

    assert _seen(book, session, "ana") == []


# -- the file, after a restart --


def test_a_session_under_way_is_read_back_after_a_restart() -> None:
    saga, session, book = _begun()
    _roll(book, saga, session, Faces(1, 1, 5), modifier=9)
    chronicle.forget_open()  # the app stopped and started again

    again = chronicle.read(saga, session)

    assert [e.kind for e in again.entries] == ["begin", "roll"]
    assert again.entries[1].body["faces"] == [1, 1, 5]
    assert again.entries[1].audience == chronicle.table()
    assert _roll(again, saga, session, Faces(4)).number == 3


def test_a_last_line_left_half_written_is_dropped() -> None:
    saga, session, book = _begun()
    _roll(book, saga, session, Faces(5))
    with book.path.open("a", encoding="utf-8") as out:
        out.write('{"number": 3, "time": "2026-')
    chronicle.forget_open()

    assert [e.number for e in chronicle.read(saga, session).entries] == [1, 2]


def test_a_damaged_line_before_the_last_is_refused() -> None:
    saga, session, book = _begun()
    _roll(book, saga, session, Faces(5))
    lines = book.path.read_text(encoding="utf-8").splitlines()
    book.path.write_text("not json\n" + lines[1] + "\n", encoding="utf-8")
    chronicle.forget_open()

    with pytest.raises(ValueError):
        chronicle.read(saga, session)


def test_an_ended_sessions_chronicle_is_still_read_from_its_row() -> None:
    saga, session, book = _begun()
    _roll(book, saga, session, Faces(5))
    chronicle.end(saga, session, by=HOST)
    chronicle.forget_open()

    again = chronicle.read(saga, session)

    assert again.closed
    assert [e.kind for e in again.entries] == ["begin", "roll", "end"]


# -- as text --


def test_the_chronicle_as_text_shows_each_face_and_a_void() -> None:
    saga, session, book = _begun()
    roll = _roll(
        book,
        saga,
        session,
        Faces(1, 1, 5),
        by="ana",
        character_id="aelfric",
        modifier=9,
        ease_factor=12,
        for_what="Climb the wall",
    )
    _roll(book, saga, session, Faces(0, 0), modifier=3, for_what="The weather")
    chronicle.strike(book, session, roll.number, "Wrong wall", by=HOST)

    shown = chronicle.text(book.seen_by(HOST, session), book)

    assert (
        "STRUCK (Wrong wall): Aelfric (Climb the wall): "
        "Stress die 1, 1, 5 → 5 × 4 = 20, +9 = 29 vs 12: succeeds by 17" in shown
    )
    assert (
        "Storyguide (The weather): Stress die 0, +3 = 0; 1 botch die 0: botch, 1 zero"
        in shown
    )


def test_an_entry_of_a_kind_this_version_doesnt_know_asks_to_update() -> None:
    book = _begun()[2]
    book.add("handout", HOST, chronicle.table(), {"picture": "map"})

    assert chronicle.UNKNOWN in chronicle.text(book.entries, book)


# -- found in review --


def test_the_next_entry_after_a_half_written_line_starts_a_line_of_its_own() -> None:
    saga, session, book = _begun()
    _roll(book, saga, session, Faces(5))
    with book.path.open("a", encoding="utf-8") as out:
        out.write('{"number": 3, "time": "2026-')
    chronicle.forget_open()

    again = chronicle.read(saga, session)
    _roll(again, saga, session, Faces(6))
    chronicle.forget_open()

    numbers = [e.number for e in chronicle.read(saga, session).entries]
    assert numbers == [1, 2, 3]


def test_an_ended_session_marked_unplayed_is_not_begun_again() -> None:
    saga, session, _book = _begun()
    chronicle.end(saga, session, by=HOST)
    session.played = False  # unticked in Edit

    assert chronicle.why_not_begin(saga, session, HOST) == (
        "This Session has ended: its Chronicle is closed."
    )


def test_a_storyguide_no_longer_in_the_saga_leaves_the_session_to_the_host() -> None:
    saga = _saga()
    session = saga.sessions[0]
    session.storyguide_id = "ben"
    chronicle.begin(saga, session, by="ben")
    saga.players = [p for p in saga.players if p.id != "ben"]

    assert chronicle.why_not_end(session, HOST, saga) is None
    assert chronicle.why_not_end(session, "ben", saga) is not None


def test_a_saga_whose_id_names_no_chronicle_file_has_none_to_back_up() -> None:
    assert chronicle.files_of("my.old saga") == []
    saga = _saga()
    saga.id = "my.old saga"
    assert chronicle.why_not_begin(saga, saga.sessions[0], HOST) is not None
    assert not chronicle.has_chronicle(saga, saga.sessions[0])
