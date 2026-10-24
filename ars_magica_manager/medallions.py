"""The season medallions: six sets of roundels, one emblem per season (a
flower for Spring, the sun for Summer, grapes for Autumn, a snow-star for
Winter), each drawn in its own manner. The saga chooses its set
(Saga.medallions); the desktop draws them (gui/medallions.py), and the
terminal keeps to words. Only the siege's season track shows them yet.
"""

from __future__ import annotations

from .models import SEASONS, Saga

STAINED_GLASS = "stained_glass"
#: Each set's key, name and what it looks like.
SETS: tuple[tuple[str, str, str], ...] = (
    (
        STAINED_GLASS,
        "Stained glass",
        "Leaded panes with light through them, the season worked in its own glass.",
    ),
    (
        "illuminated",
        "As an illuminated letter",
        "The initial's lapis and vermilion, white pen-work, a gold plait and ivy.",
    ),
    ("wax_seal", "A wax seal", "Coloured wax, the season's Latin name and the year."),
    ("enamel", "Limoges enamel", "Gilt copper, a jewelled ring and enamel."),
    (
        "book_of_hours",
        "A Book of Hours roundel",
        "A calendar page's little landscape: the season's sky and tree.",
    ),
    ("pen_and_wash", "Pen and wash", "The quietest: inked and hatched over a wash."),
)
KEYS = tuple(key for key, _, _ in SETS)
#: The seasons' Latin names, for the wax seals' legends.
LATIN = {"Spring": "VER", "Summer": "AESTAS", "Autumn": "AUTUMNUS", "Winter": "HIEMS"}


def chosen(saga: Saga) -> str:
    """The saga's set (stained glass when it names none the app knows)."""
    return saga.medallions if saga.medallions in KEYS else STAINED_GLASS


def options() -> list[tuple[str, str]]:
    """The sets as a select field's (label, value) pairs."""
    return [(name, key) for key, name, _ in SETS]


def roman(year: int) -> str:
    """A year in Roman numerals, as a seal's legend has it (1221: MCCXXI)."""
    found = ""
    for value, letters in (
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ):
        while year >= value:
            found += letters
            year -= value
    return found


def seasons_between(
    season: str, year: int, count: int, *, last: int = 8
) -> list[tuple[str, int]]:
    """The `count` seasons from (season, year) on, the first included; at
    most the `last` few of them."""
    index = SEASONS.index(season) if season in SEASONS else 0
    found = [
        (SEASONS[(index + n) % len(SEASONS)], year + (index + n) // len(SEASONS))
        for n in range(max(1, count))
    ]
    return found[-last:]
