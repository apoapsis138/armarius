"""A Chronicle shared by two processes (chronicle.py; ADR 0019): the
Storyguide's window and the Remote seat listener both write the one file,
each under its lock and numbering from the file, and each catches up with
what the other wrote (`refresh`), telling its subscribers. A seat keeps
what it is sent in memory only (SeatChronicle)."""

from __future__ import annotations

import random

from ars_magica_manager import chronicle, viewing
from ars_magica_manager.models import Casting, Character, Player, Saga, Session

HOST = viewing.HOST


class Faces(random.Random):
    def __init__(self, *faces: int) -> None:
        super().__init__()
        self.faces = list(faces)

    def randrange(self, *_args: object, **_kwargs: object) -> int:  # type: ignore[override]
        return self.faces.pop(0)


def _saga() -> Saga:
    saga = Saga(id="fengheld", name="Fengheld")
    saga.players = [Player("ana", "Ana"), Player("ben", "Ben")]
    saga.characters = [Character(id="aelfric", name="Aelfric", type="magus")]
    saga.sessions = [
        Session("s1", castings=[Casting(player_id="ana", character_id="aelfric")])
    ]
    return saga


def _other_process(saga: Saga, session: Session) -> chronicle.Chronicle:
    """The same Chronicle as another process holds it: its own copy."""
    return chronicle.Chronicle(chronicle.path_of(saga, session), [])


def test_two_writers_number_from_the_file_never_from_their_copy() -> None:
    saga = _saga()
    session = saga.sessions[0]
    window = chronicle.begin(saga, session, by=HOST)
    listener = _other_process(saga, session)
    listener.refresh()

    ana = chronicle.RollRequest(character_id="aelfric")
    chronicle.free_roll(listener, saga, session, ana, by="ana", rng=Faces(4))
    chronicle.free_roll(
        window, saga, session, chronicle.RollRequest(), by=HOST, rng=Faces(6)
    )

    assert [e.number for e in window.entries] == [1, 2, 3]
    assert [e.author for e in window.entries] == [HOST, "ana", HOST]
    listener.refresh()
    assert [e.number for e in listener.entries] == [1, 2, 3]


def test_refresh_tells_subscribers_of_what_another_process_wrote() -> None:
    saga = _saga()
    session = saga.sessions[0]
    window = chronicle.begin(saga, session, by=HOST)
    told: list[int] = []
    window.subscribe(lambda entry: told.append(entry.number))
    listener = _other_process(saga, session)

    listener.add("note", "ana", chronicle.table(), {})
    assert told == []  # not until the window looks
    assert [e.number for e in window.refresh()] == [2]

    assert told == [2]
    assert window.refresh() == []


def test_a_chronicle_ended_elsewhere_takes_no_more() -> None:
    saga = _saga()
    session = saga.sessions[0]
    chronicle.begin(saga, session, by=HOST)
    listener = _other_process(saga, session)
    listener.refresh()
    chronicle.end(saga, session, by=HOST)

    assert listener.refresh()[-1].kind == chronicle.END
    assert listener.closed


def test_a_seat_is_fed_only_what_its_player_may_see() -> None:
    saga = _saga()
    session = saga.sessions[0]
    session.under_way = False
    book = chronicle.begin(saga, session, by=HOST)
    private = chronicle.RollRequest(
        character_id="aelfric", visibility=chronicle.PRIVATE, for_what="MARKER"
    )
    chronicle.free_roll(book, saga, session, private, by="ana", rng=Faces(5))
    blind = chronicle.RollRequest(character_id="aelfric", visibility=chronicle.BLIND)
    chronicle.free_roll(book, saga, session, blind, by=HOST, rng=Faces(7))

    for_ana = chronicle.feed(saga, "ana", "s1", 0)
    for_ben = chronicle.feed(saga, "ben", "s1", 0)

    assert for_ana is not None and for_ben is not None
    assert [e.kind for e in for_ana.entries] == ["begin", "roll", "rolled"]
    assert [e.kind for e in for_ben.entries] == ["begin"]
    assert [e.number for e in chronicle.feed(saga, "ana", "s1", 2).entries] == [4]  # type: ignore[union-attr]


def test_no_feed_while_no_session_is_under_way() -> None:
    assert chronicle.feed(_saga(), "ana", "", 0) is None


def test_a_seat_keeps_what_it_is_sent_in_memory_and_tells_subscribers() -> None:
    seat = chronicle.SeatChronicle()
    told: list[int] = []
    seat.subscribe(lambda entry: told.append(entry.number))
    entry = chronicle.Entry(
        3, "2026-11-20T19:42:00+00:00", "roll", "ana", chronicle.table()
    )

    seat.take("s1", entry)
    seat.take("s1", entry)  # sent twice after a reconnect: kept once

    assert seat.last == 3 and told == [3]
    seat.take("s2", chronicle.Entry(1, "", "begin", HOST, chronicle.table()))
    assert [e.number for e in seat.entries] == [1]  # a new Session starts afresh


# -- found in review --


def test_a_new_session_is_fed_from_its_start_whatever_was_held() -> None:
    """Numbers are each Session's own: 40 held of the last Session is not
    40 of this one."""
    saga = _saga()
    saga.sessions.append(Session("s2"))
    chronicle.begin(saga, saga.sessions[0], by=HOST)
    chronicle.end(saga, saga.sessions[0], by=HOST)
    chronicle.begin(saga, saga.sessions[1], by=HOST)

    found = chronicle.feed(saga, "ana", "s1", 40)

    assert found is not None and found.session_id == "s1"
    assert found.entries == []  # s1 ended at 2: nothing after 40 of it
    fresh = chronicle.feed(saga, "ana", "", 40)  # nothing held: from the start
    assert fresh is not None and [e.number for e in fresh.entries] == [1]
    again = chronicle.feed(saga, "ana", "s0", 40)  # a Session the saga lacks
    assert again is not None and again.session_id == "s2"
    assert [e.number for e in again.entries] == [1]


def test_a_session_ended_since_is_fed_to_its_end() -> None:
    saga = _saga()
    session = saga.sessions[0]
    chronicle.begin(saga, session, by=HOST)
    chronicle.end(saga, session, by=HOST)  # saved before the seat looked

    found = chronicle.feed(saga, "ana", "s1", 1)

    assert found is not None and [e.kind for e in found.entries] == ["end"]


def test_subscribers_hear_of_another_process_entries_before_their_own() -> None:
    saga = _saga()
    session = saga.sessions[0]
    window = chronicle.begin(saga, session, by=HOST)
    told: list[int] = []
    window.subscribe(lambda entry: told.append(entry.number))
    _other_process(saga, session).add("note", "ana", chronicle.table(), {})

    window.add("note", HOST, chronicle.table(), {})

    assert told == [2, 3]
