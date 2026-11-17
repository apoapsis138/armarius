"""What the desktop's Chronicle pane reads from the core (chronicle.py):
one entry's line, and which entries call a collapsed pane's attention."""

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
        == "Storyguide (Weather): stress die 7, +3 = 10"
    )


def test_a_blind_result_calls_attention_for_whom_it_is_meant() -> None:
    saga, session, book = _begun()
    _blind(saga, session, book)
    roll, rolled = book.entries[-2:]

    assert chronicle.calls_attention(roll, HOST, session, saga)
    assert chronicle.calls_attention(rolled, "ana", session, saga)
    assert not chronicle.calls_attention(rolled, "ben", session, saga)


def test_a_public_roll_does_not_call_attention() -> None:
    saga, session, book = _begun()
    request = chronicle.RollRequest(character_id="aelfric")
    entry = chronicle.free_roll(book, saga, session, request, by="ana", rng=Faces(4))

    assert not chronicle.calls_attention(entry, HOST, session, saga)
