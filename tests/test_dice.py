"""Dice (STORY-805), checked against the Definitive Edition's examples."""

import random

import pytest

from ars_magica_manager.models import Saga
from ars_magica_manager.rules import dice


class Scripted(random.Random):
    """A d10 that throws the faces given, in order."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *args, **kwargs):  # type: ignore[override]
        return self.faces.pop(0)


def test_simple_die_reads_0_as_10():
    assert dice.simple_die(Scripted(0)) == 10
    assert dice.simple_die(Scripted(7)) == 7


@pytest.mark.parametrize(
    ("faces", "value"),
    [
        ((5,), 5),
        ((1, 5), 10),  # 1 then 5 = 10
        ((1, 1, 5), 20),  # 1, 1, 5 = 20
        ((1, 0), 20),  # a re-rolled 0 reads as 10
        ((1,) * 10 + (3,), 3 * 1024),
    ],
)
def test_stress_die_explodes_on_1(faces, value):
    result = dice.stress_die(Scripted(*faces))
    assert result.value == value
    assert not result.botched


def test_a_0_rolls_the_botch_dice():
    result = dice.stress_die(Scripted(0, 4, 0, 0), botch_dice=3)
    assert (result.value, result.botches) == (0, 2)
    clean = dice.stress_die(Scripted(0, 4, 5), botch_dice=2)
    assert (clean.value, clean.botched) == (0, False)


def test_a_roll_that_cannot_botch_just_scores_0():
    result = dice.stress_die(Scripted(0), botch_dice=0)
    assert (result.value, result.botched) == (0, False)


def test_a_botch_cancels_the_positive_modifiers():
    assert dice.roll(Scripted(0, 0), 7, ease_factor=6).total == 0
    botched = dice.roll(Scripted(0, 0), -3, ease_factor=6)
    assert botched.total == -3 and botched.succeeded is False


def test_success_and_margin_against_the_ease_factor():
    result = dice.roll(Scripted(6), 4, ease_factor=9)
    assert (result.total, result.succeeded, result.margin) == (10, True, 1)
    assert dice.roll(Scripted(4), 4, ease_factor=9).succeeded is False
    assert dice.roll(Scripted(4), 4).succeeded is None


def test_simple_dice_only_turns_stress_dice_into_simple_ones():
    saga = Saga(id="s", name="S", rule_options={"simple_dice_only": True})
    result = dice.stress_die(Scripted(0), botch_dice=5, saga=saga)
    assert (result.value, result.botched, result.stress) == (10, False, False)


@pytest.mark.parametrize(
    ("botch_dice", "chance"), [(0, 0.0), (1, 0.01), (3, 0.027), (10, 0.065)]
)
def test_botch_chance_matches_the_table(botch_dice, chance):
    assert dice.botch_chance(botch_dice) == pytest.approx(chance, abs=0.0005)


@pytest.mark.parametrize(
    ("ease_factor", "label"),
    [(0, "Trivial"), (9, "Average"), (10, "Average"), (30, "Almost impossible")],
)
def test_ease_factor_labels(ease_factor, label):
    assert dice.ease_factor_label(ease_factor) == label


def test_a_real_generator_stays_in_range():
    rng = random.Random(1)
    for _ in range(500):
        assert 1 <= dice.simple_die(rng) <= 10
        assert dice.stress_die(rng).value >= 0
