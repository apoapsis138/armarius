"""Rolls from the sheet and Confidence spent on them, at the host
(chronicle.py; ADR 0018).

Expected values are the book's, Ars Magica Definitive Edition: a
Characteristic + Ability + die, a Specialty as one more point, and an
Ability with no score at 0 with three extra botch dice (p. 157; the
asterisked list, p. 159); Fatigue penalties (p. 403) and wound penalties,
with no action at all when Incapacitated (p. 404); Enduring Constitution
easing both by one (p. 78); Confidence spent after the roll, +3 a point,
never on a botch, at most the Confidence Score (p. 29)."""

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
    Wounds,
)
from ars_magica_manager.models import VirtueFlawInstance as V
from tests.test_chronicle import Faces

HOST = viewing.HOST


def _saga() -> Saga:
    """Ana plays Aelfric tonight (Dexterity +2, Athletics 3 with a
    Specialty in climbing, Confidence 1 with 3 points); Ben plays no one."""
    saga = Saga(id="fengheld", name="Fengheld")
    saga.players = [Player("ana", "Ana"), Player("ben", "Ben")]
    aelfric = Character(id="aelfric", name="Aelfric", type="companion")
    aelfric.characteristics = Characteristics(dexterity=2, stamina=1)
    aelfric.abilities = [Ability("Athletics", xp=30, specialty="climbing")]
    aelfric.background.confidence_score = 1
    aelfric.background.confidence_points = 3
    saga.characters = [aelfric]
    saga.sessions = [
        Session(
            "s1",
            coming=["ana", "ben"],
            castings=[Casting(player_id="ana", character_id="aelfric")],
        )
    ]
    return saga


def _begun() -> tuple[Saga, Session, chronicle.Chronicle]:
    saga = _saga()
    session = saga.sessions[0]
    return saga, session, chronicle.begin(saga, session, by=HOST)


def _sheet(
    characteristic: str = "Dexterity",
    ability: str = "Athletics",
    *,
    specialty: bool = False,
    ease: int | None = None,
    visibility: str = chronicle.PUBLIC,
) -> chronicle.RollRequest:
    return chronicle.RollRequest(
        character_id="aelfric",
        ease_factor=ease,
        for_what="Climb the wall",
        visibility=visibility,
        sheet=chronicle.SheetRoll(characteristic, ability, specialty),
    )


def _terms(entry: chronicle.Entry) -> list[tuple[str, int]]:
    return chronicle.terms_of(entry.body)


def test_a_sheet_roll_adds_characteristic_ability_specialty_and_penalties() -> None:
    saga, session, book = _begun()
    aelfric = saga.characters[0]
    aelfric.wounds = Wounds(light=1)
    aelfric.fatigue_level = "weary"

    roll = chronicle.free_roll(
        book, saga, session, _sheet(specialty=True), by="ana", rng=Faces(7)
    )

    assert _terms(roll) == [
        ("Dexterity", 2),
        ("Athletics", 3),
        ("Specialty (climbing)", 1),
        ("Wounds", -1),
        ("Fatigue", -1),
    ]
    assert roll.body["total"] == 7 + 2 + 3 + 1 - 1 - 1
    assert "Dexterity +2, Athletics +3, Specialty (climbing) +1" in chronicle.line(
        roll, {}
    )


def test_enduring_constitution_eases_both_penalties() -> None:
    saga, session, book = _begun()
    aelfric = saga.characters[0]
    aelfric.wounds = Wounds(light=1)
    aelfric.fatigue_level = "weary"
    aelfric.virtues_flaws = [V("vf_enduring_constitution")]

    roll = chronicle.free_roll(book, saga, session, _sheet(), by="ana", rng=Faces(7))

    assert _terms(roll) == [("Dexterity", 2), ("Athletics", 3)]
    assert roll.body["total"] == 12


def test_a_characteristic_alone_is_rolled_with_no_ability() -> None:
    saga, session, book = _begun()

    roll = chronicle.free_roll(
        book, saga, session, _sheet("Stamina", ""), by="ana", rng=Faces(4)
    )

    assert _terms(roll) == [("Stamina", 1)]
    assert roll.body["total"] == 5


def test_an_ability_with_no_score_is_rolled_at_0_with_three_extra_botch_dice() -> None:
    saga, session, book = _begun()

    # A zero on the stress die: one botch die and three more, none a zero.
    roll = chronicle.free_roll(
        book,
        saga,
        session,
        _sheet("Dexterity", "Stealth"),
        by="ana",
        rng=Faces(0, 3, 4, 5, 6),
    )

    assert _terms(roll) == [("Dexterity", 2), ("Stealth (no score)", 0)]
    assert roll.body["botch_faces"] == [3, 4, 5, 6]
    assert not roll.body["botches"]


def test_an_asterisked_ability_with_no_experience_is_refused() -> None:
    saga, session, _book = _begun()

    assert (
        chronicle.why_not_roll(
            saga, session, _sheet("Intelligence", "Magic Theory"), "ana"
        )
        == "Magic Theory can't be used without experience in it."
    )


def test_an_incapacitated_character_takes_no_action() -> None:
    saga, session, _book = _begun()
    saga.characters[0].wounds = Wounds(incapacitated=True)

    assert chronicle.why_not_roll(saga, session, _sheet(), "ana") == (
        "Aelfric is Incapacitated: no actions."
    )


def test_a_specialty_must_be_the_characters_own() -> None:
    saga, session, _book = _begun()
    saga.characters[0].abilities = [Ability("Athletics", xp=30)]

    assert chronicle.why_not_roll(saga, session, _sheet(specialty=True), "ana") == (
        "Aelfric has no Specialty in Athletics."
    )


def test_a_player_rolls_from_the_sheet_only_for_a_character_they_play() -> None:
    saga, session, _book = _begun()

    assert chronicle.why_not_roll(saga, session, _sheet(), "ben") == (
        "Roll for a character you play tonight."
    )


# -- Confidence --


def test_confidence_after_a_roll_adds_three_a_point_as_a_new_entry() -> None:
    saga, session, book = _begun()
    roll = chronicle.free_roll(
        book, saga, session, _sheet(ease=15), by="ana", rng=Faces(8)
    )
    assert roll.body["total"] == 13 and not roll.body["succeeded"]

    spent = chronicle.spend_confidence(book, saga, session, roll.number, 1, by="ana")

    assert spent.kind == chronicle.CONFIDENCE
    assert spent.body["total"] == 16 and spent.body["succeeded"]
    assert spent.body["margin"] == 1
    assert spent.audience == roll.audience
    assert roll.body["total"] == 13  # the roll itself is never changed


def test_confidence_is_at_most_the_score_on_one_roll() -> None:
    saga, session, book = _begun()
    roll = chronicle.free_roll(book, saga, session, _sheet(), by="ana", rng=Faces(8))
    chronicle.spend_confidence(book, saga, session, roll.number, 1, by="ana")

    assert chronicle.why_not_spend(book, saga, session, roll.number, 1, "ana") == (
        "At most 1 on one roll (the Confidence Score)."
    )


def test_confidence_is_never_spent_on_a_botch() -> None:
    saga, session, book = _begun()
    botched = chronicle.free_roll(
        book, saga, session, _sheet(), by="ana", rng=Faces(0, 0)
    )
    assert botched.body["botches"]

    assert chronicle.why_not_spend(book, saga, session, botched.number, 1, "ana") == (
        "Confidence can't be spent on a botch."
    )


def test_confidence_needs_someone_who_sees_the_number_and_plays_the_character() -> None:
    saga, session, book = _begun()
    blind = chronicle.free_roll(
        book, saga, session, _sheet(visibility=chronicle.BLIND), by=HOST, rng=Faces(5)
    )
    public = chronicle.free_roll(book, saga, session, _sheet(), by="ana", rng=Faces(5))

    assert chronicle.why_not_spend(book, saga, session, blind.number, 1, "ana") == (
        "Only someone who sees the roll's number spends Confidence on it."
    )
    assert chronicle.why_not_spend(book, saga, session, public.number, 1, "ben") == (
        "Spend Confidence for a character you play tonight."
    )
    assert chronicle.why_not_spend(book, saga, session, blind.number, 1, HOST) is None


def test_confidence_spent_on_a_struck_roll_is_refused() -> None:
    saga, session, book = _begun()
    roll = chronicle.free_roll(book, saga, session, _sheet(), by="ana", rng=Faces(5))
    chronicle.strike(book, session, roll.number, "Wrong wall", by=HOST, saga=saga)

    assert chronicle.why_not_spend(book, saga, session, roll.number, 1, "ana") == (
        "That roll is struck."
    )


def test_end_session_takes_the_evenings_confidence_off_the_points() -> None:
    saga, session, book = _begun()
    for _ in range(2):
        roll = chronicle.free_roll(
            book, saga, session, _sheet(), by="ana", rng=Faces(5)
        )
        chronicle.spend_confidence(book, saga, session, roll.number, 1, by="ana")
    aelfric = saga.characters[0]
    assert aelfric.background.confidence_points == 3
    assert chronicle.confidence_left(book, aelfric) == 1

    chronicle.end(saga, session, by=HOST)

    assert aelfric.background.confidence_points == 1


def test_the_points_left_this_session_limit_what_is_spent() -> None:
    saga, session, book = _begun()
    saga.characters[0].background.confidence_points = 0
    roll = chronicle.free_roll(book, saga, session, _sheet(), by="ana", rng=Faces(5))

    assert chronicle.why_not_spend(book, saga, session, roll.number, 1, "ana") == (
        "Aelfric has 0 Confidence left."
    )


@pytest.mark.parametrize("points", [0, -1])
def test_at_least_one_point_is_spent(points: int) -> None:
    saga, session, book = _begun()
    roll = chronicle.free_roll(book, saga, session, _sheet(), by="ana", rng=Faces(5))

    assert chronicle.why_not_spend(book, saga, session, roll.number, points, "ana") == (
        "Spend at least one point."
    )
