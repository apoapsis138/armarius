"""What the desktop's Chronicle pane reads from the core (chronicle.py):
one entry's line, and which entries call a collapsed pane's attention."""

from __future__ import annotations

import random

import pytest

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


def _every_kind(saga: Saga, session: Session, book: chronicle.Chronicle) -> None:
    """One entry of each kind the Chronicle writes, with Ana and Ben at the
    table: a Blind roll for Ana's character (and its line for her), a
    Private and a Table roll, a form's roll, a Roll request to Ana's
    character with its Ease Factor kept, a Strike, a Confidence spend, an
    outcome, a Message to the Table, Whispers each way, and the end."""
    _blind(saga, session, book)
    rolled = chronicle.RollRequest(character_id="aelfric", visibility=chronicle.PRIVATE)
    chronicle.free_roll(book, saga, session, rolled, by="ana", rng=Faces(3))
    chronicle.free_roll(
        book, saga, session, chronicle.RollRequest(), by=HOST, rng=Faces(2)
    )
    book.add(
        chronicle.FORM_ROLL,
        HOST,
        chronicle.storyguide_only(),
        {"form": "Aging", "lines": [], "faces": [4]},
    )
    call = chronicle.RollCall(("aelfric",), "Perception", ease_factor=6, hide_ease=True)
    request = chronicle.request_rolls(book, saga, session, call, by=HOST)
    book.add(chronicle.VOID, HOST, chronicle.table(), {"strikes": 3, "reason": "Typo"})
    book.add(chronicle.CONFIDENCE, "ana", chronicle.table(), {"roll": 3, "points": 1})
    book.add(
        chronicle.OUTCOME,
        HOST,
        chronicle.table(),
        {"request": request.number, "text": "The door gives."},
    )
    chronicle.message(book, saga, session, "Evening.", by="ben")
    chronicle.message(book, saga, session, "Psst.", to=("ana",), by="ben")
    chronicle.message(book, saga, session, "Hush.", to=("ben",), by=HOST)
    chronicle.end(saga, session, by=HOST)


def test_each_kind_says_who_it_is_for() -> None:
    """The kind registry holds the "for whom" rule (Strategy): a Blind
    roll's number is for the storyguide, its line for the player rolled
    for, a Whisper for those it is to, a Roll request for the player of
    each character offered it, and anything else for no one."""
    saga, session, book = _begun()
    _every_kind(saga, session, book)

    def kinds_for(who: str) -> list[str]:
        return [
            e.kind for e in book.entries if who in chronicle.for_whom(e, session, saga)
        ]

    assert kinds_for(HOST) == ["roll", "form_roll"]
    assert kinds_for("ana") == ["rolled", "request", "message"]
    assert kinds_for("ben") == ["message"]


def test_an_entry_at_a_seat_equals_the_hosts_whatever_it_was_told() -> None:
    saga, session, book = _begun()
    _blind(saga, session, book)
    rolled = book.entries[-1]

    assert chronicle.stamped(rolled, "ana", session, saga) == rolled


def test_a_kind_must_say_who_it_is_for() -> None:
    """A new kind can't forget its rule: leaving it out is refused."""
    with pytest.raises(TypeError):
        chronicle.Kind("handout", lambda _body: "A handout.")  # type: ignore[call-arg]


def test_a_rolled_line_is_for_its_chosen_player_alone() -> None:
    _saga, session, _book = _begun()
    stray = chronicle.Entry(
        5, "", "rolled", HOST, chronicle.Audience(chronicle.TABLE, ["ana"]), {}
    )

    assert chronicle.for_whom(stray, session) == frozenset()


def test_a_roll_request_to_your_character_calls_your_attention() -> None:
    saga, session, book = _begun()
    call = chronicle.RollCall(("aelfric",), "Perception", visibility=chronicle.PUBLIC)
    request = chronicle.request_rolls(book, saga, session, call, by=HOST)

    assert chronicle.calls_attention(request, "ana", session, saga)
    assert not chronicle.calls_attention(request, "ben", session, saga)
    assert not chronicle.calls_attention(request, HOST, session, saga)


def test_a_seat_is_told_which_entries_are_for_it() -> None:
    """The host stamps "for you" on each entry it feeds a seat; the frame
    carries it and the seat keeps it on the entry it holds."""
    saga, session, book = _begun()
    _every_kind(saga, session, book)

    for who in (HOST, "ana", "ben"):
        held = _sent(saga, session, who)
        assert all(isinstance(e.for_you, bool) for e in held.entries)
        assert [e.number for e in held.entries if e.for_you] == [
            e.number
            for e in book.entries
            if who in chronicle.for_whom(e, session, saga)
        ], who


def test_a_seat_pulses_on_the_hosts_word_alone() -> None:
    """A seat's reader no longer guesses from the kind: an entry the host
    says is for it calls its pane, one it doesn't, doesn't."""
    _saga, session, _book = _begun()
    held = chronicle.SeatChronicle()
    rolled = {"character_name": "Aelfric", "for": ""}
    held.take("s1", chronicle.Entry(1, "", "rolled", HOST, chronicle.chosen(), rolled))
    held.take(
        "s1",
        chronicle.Entry(2, "", "begin", HOST, chronicle.table(), {}, for_you=True),
    )
    reader = chronicle.Reader(held, "ana", session)

    assert [reader.calls_attention(e) for e in held.entries] == [False, True]


def test_every_kind_calls_the_same_people_at_the_host_and_at_a_seat() -> None:
    """A new kind can't forget its rule: one of each kind in the registry,
    read by the host's reader and each seat's, calls the same panes."""
    saga, session, book = _begun()
    _every_kind(saga, session, book)

    assert {e.kind for e in book.entries} == set(chronicle.KINDS)
    for who in (HOST, "ana", "ben"):
        here = chronicle.Reader(book, who, session, saga)
        there = chronicle.Reader(_sent(saga, session, who), who, session, saga)
        assert [(e.number, here.calls_attention(e)) for e in here.entries()] == [
            (e.number, there.calls_attention(e)) for e in there.entries()
        ], who


def test_for_you_is_never_written_to_the_chronicle_file() -> None:
    saga, session, book = _begun()
    _blind(saga, session, book)

    assert "for_you" not in book.path.read_text(encoding="utf-8")
    chronicle.forget_open()
    assert all(e.for_you is None for e in chronicle.read(saga, session).entries)


def test_a_public_roll_does_not_call_attention() -> None:
    saga, session, book = _begun()
    request = chronicle.RollRequest(character_id="aelfric")
    entry = chronicle.free_roll(book, saga, session, request, by="ana", rng=Faces(4))

    assert not chronicle.calls_attention(entry, HOST, session, saga)
