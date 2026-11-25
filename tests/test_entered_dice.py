"""Entered dice: the faces a person read off their own d10s give the
book's dice (DE pp. 7-8: a stress die's 1 is rolled again and doubled, a
first 0 calls for the botch dice), and a die not yet entered stops the
roll with what is needed and why."""

from __future__ import annotations

import pytest

from ars_magica_manager.entered_dice import EnteringDice, NeedDie
from ars_magica_manager.rules import dice


def _needs(faces: list[int], botch_dice: int = 1) -> str:
    with pytest.raises(NeedDie) as stopped:
        dice.stress_die(EnteringDice(faces), botch_dice)
    return stopped.value.why


def test_a_stress_die_reads_its_entered_faces() -> None:
    assert dice.stress_die(EnteringDice([7])).value == 7
    # 1, 1, 5: rolled again twice, 5 doubled twice (DE p. 7).
    assert dice.stress_die(EnteringDice([1, 1, 5])).value == 20


def test_a_first_zero_takes_its_botch_dice_from_the_entered_faces() -> None:
    die = dice.stress_die(EnteringDice([0, 4, 0]), 2)
    assert die.value == 0
    assert die.botch_faces == (4, 0)
    assert die.botches == 1


def test_a_die_not_yet_entered_stops_the_roll_saying_why() -> None:
    assert _needs([]) == "stress die"
    assert _needs([1]) == "a 1: roll again and double"
    assert _needs([1, 1]) == "a 1: roll again and double"
    assert _needs([0], 2) == "a 0: botch die 1 of 2"
    assert _needs([0, 3], 2) == "a 0: botch die 2 of 2"
    assert _needs([0]) == "a 0: the botch die"


def test_the_roll_being_made_heads_the_reason() -> None:
    source = EnteringDice([])
    dice.rolling(source, "Bero's Defence")
    with pytest.raises(NeedDie) as stopped:
        dice.stress_die(source)
    assert stopped.value.why == "Bero's Defence: stress die"


def test_a_simple_die_is_asked_for_as_one() -> None:
    assert dice.simple_die(EnteringDice([0])) == 10
    with pytest.raises(NeedDie) as stopped:
        dice.simple_die(EnteringDice([]))
    assert stopped.value.why == "simple die"


def test_a_draw_that_is_no_d10_is_not_asked_for() -> None:
    """A tie broken by chance isn't a die anyone throws: it is settled
    without asking."""
    source = EnteringDice([])
    assert 0.0 <= source.random() < 1.0
