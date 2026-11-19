"""What the desktop's Chronicle pane reads from the core (chronicle.py):
one entry's line, and which entries call a collapsed pane's attention."""

from __future__ import annotations

import random

from ars_magica_manager import chronicle, viewing
from ars_magica_manager.models import Casting, Character, Player, Saga, Session
from ars_magica_manager.remote import events

HOST = viewing.HOST


class Faces(random.Random):
    def __init__(self, *faces: int) -> None:
        super().__init__()
        self.faces = list(faces)

    def randrange(self, *_args: object, **_kwargs: object) -> int:  # type: ignore[override]
        return self.faces.pop(0)


def _begun() -> tuple[Saga, Session, chronicle.Chronicle]:
    saga = Saga(id="fengheld", name="Fengheld")
    saga.players = [Player("ana", "Ana"), Player("ben", "Ben")]
    saga.characters = [Character(id="aelfric", name="Aelfric", type="magus")]
    session = Session("s1", castings=[Casting(player_id="ana", character_id="aelfric")])
    saga.sessions = [session]
    return saga, session, chronicle.begin(saga, session, by=HOST)


def _blind(saga: Saga, session: Session, book: chronicle.Chronicle) -> None:
    request = chronicle.RollRequest(
        character_id="aelfric", visibility=chronicle.BLIND, for_what="Ambush"
    )
    chronicle.free_roll(book, saga, session, request, by=HOST, rng=Faces(5))


def test_one_entrys_line_is_the_chronicles_line_for_it() -> None:
    saga, session, book = _begun()
    request = chronicle.RollRequest(modifier=3, for_what="Weather")
    entry = chronicle.free_roll(book, saga, session, request, by=HOST, rng=Faces(7))

    assert (
        chronicle.line(entry, chronicle.voided(book))
        == "Storyguide (Weather): Stress die 7, +3 = 10"
    )


def test_a_blind_result_calls_attention_for_whom_it_is_meant() -> None:
    saga, session, book = _begun()
    _blind(saga, session, book)
    roll, rolled = book.entries[-2:]

    assert chronicle.calls_attention(roll, HOST, session, saga)
    assert chronicle.calls_attention(rolled, "ana", session, saga)
    assert not chronicle.calls_attention(rolled, "ben", session, saga)


def _sent(saga: Saga, session: Session, who: str) -> chronicle.SeatChronicle:
    """What `who`'s seat holds: the host's feed, through the wire's frames
    (which carry no Players chosen)."""
    held = chronicle.SeatChronicle()
    found = chronicle.feed(saga, who, session.id, 0)
    assert found is not None
    for entry in found.entries:
        held.take(*events.entry_of(events.frame(found.session_id, entry).body))
    return held


def test_a_reader_reads_the_same_at_the_host_and_at_a_seat() -> None:
    """The reader view hides the difference a seat's feed makes: the
    Players chosen don't travel, yet what is read and what calls a
    collapsed pane come out the same."""
    saga, session, book = _begun()
    _blind(saga, session, book)
    chronicle.message(book, saga, session, "Psst.", to=("ana",), by="ben")
    for who in (HOST, "ana", "ben"):
        here = chronicle.Reader(book, who, session, saga)
        there = chronicle.Reader(_sent(saga, session, who), who, session, saga)
        assert [e.kind for e in here.entries()] == [e.kind for e in there.entries()]
        assert [here.calls_attention(e) for e in here.entries()] == [
            there.calls_attention(e) for e in there.entries()
        ], who


def test_a_reader_sees_an_answer_against_the_ease_factor_kept_from_players() -> None:
    saga, session, book = _begun()
    call = chronicle.RollCall(("aelfric",), "Perception", ease_factor=6, hide_ease=True)
    request = chronicle.request_rolls(book, saga, session, call, by=HOST)
    chronicle.answer(book, saga, session, request.number, "aelfric", by="ana")
    storyguide = chronicle.Reader(book, HOST, session, saga)
    ana = chronicle.Reader(book, "ana", session, saga)

    assert storyguide.kept_ease(request) == 6 and ana.kept_ease(request) is None
    assert storyguide.answer_result(request, "aelfric")[-1] in "✓✗"
    assert ana.answer_result(request, "aelfric") == "rolled"  # Blind: not hers
    assert not ana.may_answer(request, "aelfric")  # answered already


def test_a_public_roll_does_not_call_attention() -> None:
    saga, session, book = _begun()
    request = chronicle.RollRequest(character_id="aelfric")
    entry = chronicle.free_roll(book, saga, session, request, by="ana", rng=Faces(4))

    assert not chronicle.calls_attention(entry, HOST, session, saga)
