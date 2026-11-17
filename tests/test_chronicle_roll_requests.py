"""Roll requests at the host (chronicle.py): the storyguide's call for
chosen characters to roll, each answer a roll of its own from the sheet
pointing back at it (a Macro Command of RollRequests), an Ease Factor the
storyguide may keep from the players, and who answers a shared grog."""

from __future__ import annotations

import pytest

from ars_magica_manager import chronicle, viewing
from ars_magica_manager.models import (
    Ability,
    Casting,
    Character,
    Characteristics,
    Player,
    Saga,
    Session,
)
from tests.test_chronicle import Faces

HOST = viewing.HOST


def _saga() -> Saga:
    """Ana plays Aelfric and Ben plays Brigit tonight; Gus, a shared grog
    with no Players named, is stewarded by Ben."""
    saga = Saga(id="fengheld", name="Fengheld")
    saga.players = [Player("ana", "Ana"), Player("ben", "Ben")]
    aelfric = Character(id="aelfric", name="Aelfric", type="companion")
    aelfric.characteristics = Characteristics(perception=1)
    aelfric.abilities = [Ability("Awareness", xp=15, specialty="alertness")]
    brigit = Character(id="brigit", name="Brigit", type="companion")
    brigit.characteristics = Characteristics(perception=2)
    gus = Character(id="gus", name="Gus", type="grog")
    gus.background.steward_id = "ben"
    saga.characters = [aelfric, brigit, gus]
    saga.sessions = [
        Session(
            "s1",
            coming=["ana", "ben"],
            castings=[
                Casting(player_id="ana", character_id="aelfric"),
                Casting(player_id="ben", character_id="brigit"),
            ],
        )
    ]
    return saga


def _begun() -> tuple[Saga, Session, chronicle.Chronicle]:
    saga = _saga()
    session = saga.sessions[0]
    return saga, session, chronicle.begin(saga, session, by=HOST)


def _call(**changed: object) -> chronicle.RollCall:
    asked: dict[str, object] = {
        "characters": ("aelfric", "brigit"),
        "characteristic": "Perception",
        "ability": "Awareness",
        "ease_factor": 9,
        "visibility": chronicle.PUBLIC,
        "for_what": "Spot the ambush",
    }
    asked.update(changed)
    return chronicle.RollCall(**asked)  # type: ignore[arg-type]


def test_answers_are_rolls_from_each_sheet_gathered_under_the_request() -> None:
    saga, session, book = _begun()
    request = chronicle.request_rolls(book, saga, session, _call(), by=HOST)

    first = chronicle.answer(
        book,
        saga,
        session,
        request.number,
        "aelfric",
        by="ana",
        specialty=True,
        rng=Faces(6),
    )
    second = chronicle.answer(
        book, saga, session, request.number, "brigit", by="ben", rng=Faces(3)
    )

    assert chronicle.answers(book, request.number) == [first, second]
    assert first.body["request"] == request.number
    # Perception 1 + Awareness 2 + Specialty 1 + die 6 against 9 (DE p. 157).
    assert first.body["total"] == 10 and first.body["succeeded"]
    # Brigit has no Awareness: 0, with three more botch dice; die 3 + 2.
    assert second.body["total"] == 5 and not second.body["succeeded"]
    assert chronicle.line(request, {}) == (
        "Roll request: Perception + Awareness for Aelfric, Brigit "
        "(Spot the ambush), against 9"
    )


def test_a_hidden_ease_factor_is_the_storyguides_alone() -> None:
    saga, session, book = _begun()
    request = chronicle.request_rolls(
        book, saga, session, _call(hide_ease=True), by=HOST
    )
    roll = chronicle.answer(
        book, saga, session, request.number, "aelfric", by="ana", rng=Faces(6)
    )

    assert request.body["ease_factor"] is None
    assert roll.body["ease_factor"] is None and roll.body["succeeded"] is None
    assert chronicle.hidden_ease(book, request.number) == 9
    seen_by_ana = book.seen_by("ana", session, saga)
    assert all(e.kind != chronicle.REQUEST_EASE for e in seen_by_ana)
    assert any(e.kind == chronicle.REQUEST_EASE for e in book.seen_by(HOST, session))


def test_a_blind_request_tells_its_answerer_only_that_it_was_rolled() -> None:
    saga, session, book = _begun()
    request = chronicle.request_rolls(
        book, saga, session, _call(visibility=chronicle.BLIND), by=HOST
    )

    roll = chronicle.answer(
        book, saga, session, request.number, "aelfric", by="ana", rng=Faces(6)
    )

    assert roll.audience == chronicle.storyguide_only()
    told = book.entries[-1]
    assert told.kind == chronicle.ROLLED and told.audience.players == ["ana"]
    assert request.audience == chronicle.chosen("ana", "ben")


def test_each_character_answers_once_and_only_by_its_roller_or_the_storyguide() -> None:
    saga, session, book = _begun()
    request = chronicle.request_rolls(book, saga, session, _call(), by=HOST)
    number = request.number

    assert chronicle.why_not_answer(book, saga, session, number, "aelfric", "ben") == (
        "Another Player rolls for that character."
    )
    assert chronicle.why_not_answer(book, saga, session, number, "gus", "ben") == (
        "That character isn't asked to roll."
    )
    chronicle.answer(book, saga, session, number, "aelfric", by=HOST, rng=Faces(4))
    assert chronicle.why_not_answer(book, saga, session, number, "aelfric", "ana") == (
        "That character has answered already."
    )


def test_a_shared_grog_is_rolled_by_its_steward_or_whoever_it_is_handed_to() -> None:
    saga, session, book = _begun()

    assert chronicle.answerer(saga, session, "gus") == "ben"
    handed = chronicle.request_rolls(
        book,
        saga,
        session,
        _call(characters=("gus",), ability="", rollers={"gus": "ana"}),
        by=HOST,
    )
    assert chronicle.roller_of(handed, "gus") == "ana"
    assert chronicle.why_not_answer(
        book, saga, session, handed.number, "gus", "ben"
    ) == ("Another Player rolls for that character.")
    assert (
        chronicle.why_not_answer(book, saga, session, handed.number, "gus", HOST)
        is None
    )


def test_only_the_storyguide_makes_a_request_or_notes_its_outcome() -> None:
    saga, session, book = _begun()

    assert chronicle.why_not_call(saga, session, _call(), "ana") == (
        "Only the Session's storyguide makes a Roll request."
    )
    request = chronicle.request_rolls(book, saga, session, _call(), by=HOST)
    with pytest.raises(ValueError):
        chronicle.note_outcome(book, session, request.number, "Seen!", by="ana")

    note = chronicle.note_outcome(
        book, session, request.number, "They spot the archers.", by=HOST, saga=saga
    )

    assert note.audience == request.audience
    assert (
        chronicle.line(note, {}) == f"Request {request.number}: They spot the archers."
    )
