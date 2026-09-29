"""Rounding. The Definitive Edition's rule: a rule says whether to round up
or down, and where it doesn't, round down (rules reference section 1,
Default rounding; decision 29). Every division in the Rules Engine rounds
through one of these, named by the rule that decides, so no rule rounds by
accident."""

from __future__ import annotations

import math

SOURCE = (
    "Ars Magica Definitive Edition, Chapter One: Introduction, Rounding "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_One:"
    "_Introduction#Rounding)"
)


def round_down(value: float) -> int:
    """The default: the next whole number down (2.5 -> 2, -2.5 -> -3)."""
    return math.floor(value)


def round_up(value: float) -> int:
    """For a rule that says to round up (2.1 -> 3), such as Affinity."""
    return math.ceil(value)


def round_toward_zero(value: float) -> int:
    """For a rule that halves "toward zero" (-3 / 2 -> -1), such as a Deft
    Characteristic's negative modifier (decision 52)."""
    return math.trunc(value)


def round_nearest(value: float) -> int:
    """To the nearest whole number, halves away from zero (-37.5 -> -38),
    for a rule that says so (Covenants' Base Loyalty example, deferred)."""
    return math.floor(value + 0.5) if value >= 0 else -math.floor(-value + 0.5)
