"""Diabolai, the Theban slander rites: shaming a supernatural being into
using one of its powers for the caller (The Sundered Eagle pp. 121-122).

Only a sentient being that has taken a place or a matter under its care,
and has a personal tie to the caller (his village's nymph, his craft's
god, a mythic forebear), can be slandered, and only by someone with the
(Realm) Lore of its Might. The rite takes several hours; the caller names
the power and its target, and a being without that power simply fails
him.

    Diabolai = Presence + (Realm) Lore + modifiers + stress die
    Ease Factor = 9 + the being's Might / 5

Success: the being uses the power at once. Failure: it is annoyed and
hears no more petitions from the caller for a month. Failure by 10 or
more, or a botch: it turns one of its powers on the caller, and hears no
one at all for a year.

The book doesn't say how Might / 5 rounds; the app rounds down, the
Definitive Edition's default (rules.rounding, DE p. 6)."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from ..models import Character, Saga
from . import dice
from .breakdown import Breakdown, Line
from .lab import ability_score
from .rounding import round_down

SOURCE = "The Sundered Eagle, Diabolai, pp. 121-122"

#: The Lore a being of each realm is slandered with.
REALM_LORE: dict[str, str] = {
    "Magic": "Magic Lore",
    "Faerie": "Faerie Lore",
    "Divine": "Dominion Lore",
    "Infernal": "Infernal Lore",
}

BASE_EASE = 9
#: Failing by this much or more brings the being's wrath on the caller.
WRATH_MARGIN = 10


@dataclass(frozen=True)
class Modifier:
    """One of the book's modifiers to a slander rite."""

    key: str
    label: str
    amount: int


#: The book's modifiers (p. 122). An apt power is +1 to +5, the
#: storyguide's choice, so it is typed (`apt`) rather than listed here.
MODIFIERS: tuple[Modifier, ...] = (
    Modifier("public", "Performed in public", 2),
    Modifier("synthemata", "The being's synthemata known", 3),
    Modifier("true_name", "The being's True Name known", 9),
    Modifier("recent", "A diabolai performed in the last month", -9),
    Modifier("unfamiliar", "Threatening an unfamiliar being", -6),
)
BY_KEY: dict[str, Modifier] = {m.key: m for m in MODIFIERS}
MAX_APT = 5

SUCCESS, ANNOYED, WRATH = "success", "annoyed", "wrath"
OUTCOMES: dict[str, str] = {
    SUCCESS: "The being uses the power demanded, at once.",
    ANNOYED: "The being is annoyed: it hears no more petitions from the caller "
    "for a month.",
    WRATH: "The being turns one of its powers on the caller, and hears no "
    "petitions from anyone for a year.",
}


def ease_factor(might: int) -> int:
    """9 + the being's Might / 5 (rounded down)."""
    return BASE_EASE + round_down(max(0, might) / 5)


def lore_for(realm: str) -> str:
    """The (Realm) Lore a being of `realm` is slandered with."""
    if realm not in REALM_LORE:
        raise ValueError(f"No realm called {realm!r}.")
    return REALM_LORE[realm]


def problem(caller: Character, realm: str, has_power: bool = True) -> str:
    """Why the rite can't be tried ("" if it can): the caller needs the
    being's (Realm) Lore, and a being without the power named fails."""
    lore = lore_for(realm)
    if not any(a.name == lore for a in caller.abilities):
        return f"{caller.name} has no {lore}, so can't perform a slander rite."
    if not has_power:
        return "The being has no such power: the rite fails."
    return ""


def total(
    caller: Character, realm: str, modifiers: tuple[str, ...] = (), apt: int = 0
) -> Breakdown:
    """The rite's total before the stress die: Presence + (Realm) Lore + the
    modifiers chosen (MODIFIERS' keys) + an apt power's +1 to +5."""
    lore = lore_for(realm)
    lines = [
        Line("Presence", amount=caller.characteristics.presence, source=SOURCE),
        Line(lore, amount=sum(ability_score(caller, lore)), source=SOURCE),
    ]
    for key in modifiers:
        if key not in BY_KEY:
            raise ValueError(f"No slander-rite modifier called {key!r}.")
        found = BY_KEY[key]
        lines.append(Line(found.label, amount=found.amount, source=SOURCE))
    if apt:
        if not 1 <= apt <= MAX_APT:
            raise ValueError(f"An apt power is worth +1 to +{MAX_APT}.")
        lines.append(Line("The power demanded is apt", amount=apt, source=SOURCE))
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def outcome(roll_total: int, ease: int, botched: bool = False) -> str:
    """SUCCESS, ANNOYED or WRATH for a rite that rolled `roll_total`
    against `ease`."""
    if botched or roll_total <= ease - WRATH_MARGIN:
        return WRATH
    return SUCCESS if roll_total >= ease else ANNOYED


@dataclass
class Rite:
    """A slander rite rolled: the total, the Ease Factor, what came of it."""

    total: int
    ease: int
    result: str
    botched: bool = False
    notes: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return OUTCOMES[self.result]


def perform(
    rng: random.Random,
    caller: Character,
    realm: str,
    might: int,
    modifiers: tuple[str, ...] = (),
    apt: int = 0,
    saga: Saga | None = None,
) -> Rite:
    """Roll a slander rite against a being of `realm` and `might`."""
    base = total(caller, realm, modifiers, apt)
    ease = ease_factor(might)
    rolled = dice.roll(rng, int(base.total), ease_factor=ease, saga=saga)
    result = outcome(rolled.total, ease, rolled.die.botched)
    return Rite(
        total=rolled.total,
        ease=ease,
        result=result,
        botched=rolled.die.botched,
        notes=[f"{line.label} {line.amount:+g}" for line in base.lines],
    )
