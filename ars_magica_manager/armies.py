"""A lord's title, wealth and the army they raise (Lords of Men): kept
apart from lords.py so the battles and sieges that count his army can
read it without importing his sheet."""

from __future__ import annotations

from dataclasses import dataclass

from .models import Neighbour
from .rules.battle import GROUP_SIZE

#: The titles a lord may hold, from least to greatest.
TITLES: dict[str, str] = {
    "landed": "Landed noble",
    "baron": "Baron",
    "count": "Count or earl",
    "duke": "Duke",
}

WEALTH: tuple[str, ...] = ("Poor", "Average", "Wealthy")


@dataclass(frozen=True)
class Army:
    """The men a lord's title raises: knights, serjeants, infantry and
    archers, and the levies he can call on at home."""

    knights: int
    serjeants: int
    infantry: int
    levies: int

    def text(self) -> str:
        return (
            f"{self.knights} knights, {self.serjeants} serjeants, "
            f"{self.infantry} infantry; {self.levies} levies at home"
        )


def army_of(title: str, wealth: str) -> Army:
    """The army a lord of `title` and `wealth` raises."""
    if title == "landed":
        return Army(5, 5, 50, 50) if wealth == "Wealthy" else Army(0, 5, 10, 10)
    return {
        "baron": Army(20, 20, 200, 200),
        "count": Army(50, 50, 500, 500),
        "duke": Army(75, 75, 750, 750),
    }.get(title, Army(0, 5, 10, 10))


def title(neighbour: Neighbour) -> str:
    found = neighbour.details.get("title")
    return found if found in TITLES else "landed"


def wealth(neighbour: Neighbour) -> str:
    found = neighbour.details.get("wealth")
    return found if found in WEALTH else "Average"


def army_groups(neighbour: Neighbour, *, at_home: bool = True) -> int:
    """The combat groups of five his title raises; his levies only on his
    home ground (Lords of Men pp. 31, 102)."""
    army = army_of(title(neighbour), wealth(neighbour))
    levies = army.levies if at_home else 0
    return (army.knights + army.serjeants + army.infantry + levies) // GROUP_SIZE
