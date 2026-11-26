"""Default Interests: the interests a new character starts with, each with
the reason it is on.

The defaults are Session & Reputation, which every character has, plus
the union of what each rule below turns on. A rule is a small function
registered in RULES with @rule; adding a source of defaults is one more
rule, with no change to the callers. The type rule is the approved design
of the app, not a book rule.

The interests are named as `deeds` names them (deeds.INTERESTS). `deeds`
asks this module for a character's defaults, so this one sits below it and
spells the names out; a test checks each is one of deeds'.
"""

from __future__ import annotations

from collections.abc import Callable

from .models import Character

#: An interest the defaults turn on, and why ("a magus").
Reason = tuple[str, str]
Rule = Callable[[Character], list[Reason]]

SESSION = "Session & Reputation"

#: The default-interest rules, in the order their reasons are given.
RULES: list[Rule] = []


def rule(fn: Rule) -> Rule:
    """Register a default-interest rule."""
    RULES.append(fn)
    return fn


#: What each type of character takes up, and how its reason names it. An
#: animal grog is a grog with an animal form, looked up as ANIMAL_GROG.
ANIMAL_GROG = "animal grog"
BY_TYPE: dict[str, tuple[str, tuple[str, ...]]] = {
    "magus": ("a magus", ("Research", "Tribunal & Order")),
    "companion": ("a companion", ("Religion",)),
    "mythic companion": ("a mythic companion", ("Religion",)),
    "grog": ("a grog", ("Covenfolk", "Craft & Trade")),
    ANIMAL_GROG: ("an animal grog", ("Covenfolk",)),
}


@rule
def by_type(character: Character) -> list[Reason]:
    """The interests its type takes up."""
    kind = ANIMAL_GROG if character.animal is not None else character.type
    why, interests = BY_TYPE.get(kind, ("", ()))
    return [(interest, why) for interest in interests]


def defaults(character: Character) -> list[Reason]:
    """`character`'s Default Interests, each with its reason: Session &
    Reputation first, then each rule's in turn (an interest two rules turn
    on is listed once for each)."""
    found: list[Reason] = [(SESSION, "every character")]
    for fn in RULES:
        found += fn(character)
    return found
