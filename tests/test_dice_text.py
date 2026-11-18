"""One dice line for every roll (dice_text.py; STORY-2348): the die, each
stress doubling, the botch dice, the modifiers, the total and any Ease
Factor, in the words the Chronicle card uses.

Expected values are the Definitive Edition's own worked examples (Die
Rolls, Stress Die, p. 7): a character with Characteristic + Ability 9."""

from __future__ import annotations

from ars_magica_manager import dice_text
from ars_magica_manager.rules.dice import DieResult

NINE = [("Characteristic + Ability", 9)]


def test_two_ones_then_a_five_is_twenty_and_a_total_of_29() -> None:
    """DE p. 7: "two 1s and then a 5 ... a final total of 29"."""
    die = DieResult(value=20, faces=(1, 1, 5))

    assert dice_text.dice_line(die, NINE, 29) == (
        "Stress die 1, 1, 5 → 5 × 4 = 20, Characteristic + Ability +9 = 29"
    )


def test_a_six_is_a_total_of_15() -> None:
    """DE p. 7: "If the roll comes up 6, he has a total of 15"."""
    die = DieResult(value=6, faces=(6,))

    assert dice_text.dice_line(die, NINE, 15, 12) == (
        "Stress die 6, Characteristic + Ability +9 = 15 vs 12: succeeds by 3"
    )


def test_a_zero_with_no_zero_on_the_botch_dice_adds_nothing() -> None:
    """DE p. 7: "If none of the botch dice come up 0, his total is 9"."""
    die = DieResult(value=0, faces=(0,), botch_faces=(3, 7))

    assert dice_text.dice_line(die, NINE, 9, 12) == (
        "Stress die 0, Characteristic + Ability +9 = 9 vs 12: fails by 3; "
        "2 botch dice 3, 7: no zeros"
    )


def test_a_botch_totals_zero_and_names_its_zeros() -> None:
    """DE p. 7: "If any of the botch dice come up 0, his total is 0"."""
    die = DieResult(value=0, faces=(0,), botch_faces=(0, 4, 0))

    assert dice_text.dice_line(die, NINE, 0, 6) == (
        "Stress die 0, Characteristic + Ability +9 = 0 vs 6: fails by 6; "
        "3 botch dice 0, 4, 0: botch, 2 zeros"
    )


def test_a_re_rolled_zero_reads_as_ten() -> None:
    """DE p. 7: "On second and subsequent rolls, a zero counts as ten"."""
    die = DieResult(value=20, faces=(1, 0))

    assert dice_text.die_text(die) == "Stress die 1, 10 → 10 × 2 = 20"


def test_a_simple_die_and_a_free_rolls_lone_modifier() -> None:
    die = DieResult(value=10, faces=(0,), stress=False)

    assert dice_text.dice_line(die, [("Modifier", -2)], 8) == "Simple die 10, −2 = 8"


def test_a_lone_roll_of_botch_dice() -> None:
    """An unsafe laboratory's botch dice, rolled on their own (DE p. 8)."""
    die = DieResult(value=0, faces=(), botch_faces=(4, 0, 9))

    assert dice_text.die_text(die) == "3 botch dice 4, 0, 9: 1 zero"


def test_a_kept_die_missing_a_field_reads_as_far_as_it_can() -> None:
    """A form roll's kept die is read from a file: a missing or odd field
    reads as empty, never as an error that hides the whole Chronicle."""
    kept = [{"stress": True, "faces": [1, "x", 5]}, {"face": "?"}]

    assert dice_text.dice_text(kept) == "Stress die 1, 5 → 5 × 2 = 10"
