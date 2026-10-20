"""A tradition member's effects (spells, charms, rune scripts, rites,
powers) and items (amulets, chartae, fetishes, potions, tattoos,
wondrous items), each a TraditionEffect on the character.

An effect is cast with one of the tradition's casting rules
(rules.hedge_casting): its Casting Score, from the Arts, Ability or runes
it uses, sets the die it needs to reach its level:

    (Casting Score + die) / divisor >= level
    die >= level x divisor - Casting Score

and up to the rule's failure margin short it still works, for a Fatigue
level. An effect whose magnitude is its Ability's score (a folk witch's
power) is as strong as the score allows, so it needs no die for its
level. An item is made with the tradition's Lab Total (a lab rule): its
Lab Total is shown beside the item's level, and its charges are counted
down by hand.

Rules: reference/rules-engine-reference.md §18 (each tradition's
effects and items).
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import CastingRule, Character, TraditionDef, TraditionEffect
from . import hedge_casting as hc
from . import realms

SOURCE = (
    "Hedge Magic, Revised Edition "
    "(https://www.redcap.org/page/Hedge_Magic_Revised_Edition_Open_Content)"
)


def of_tradition(
    character: Character, tradition_id: str
) -> list[tuple[int, TraditionEffect]]:
    """The tradition's effects and items the character has, each with its
    index into character.tradition_effects."""
    return [
        (i, e)
        for i, e in enumerate(character.tradition_effects)
        if e.tradition == tradition_id
    ]


def rule_of(tradition: TraditionDef, effect: TraditionEffect) -> CastingRule | None:
    return next((r for r in tradition.casting if r.name == effect.rule), None)


@dataclass(frozen=True)
class EffectTotal:
    """What an effect's casting comes to: the Casting Score (or Lab
    Total), and the least die that reaches its level, plain and for a
    Fatigue level (None when there is no die or no margin)."""

    score: int
    lab: bool
    die: int | None = None
    fatigue_die: int | None = None


def effect_total(
    character: Character,
    tradition: TraditionDef,
    effect: TraditionEffect,
    aura: int = 0,
    aura_realm: str = realms.HERMETIC,
) -> EffectTotal | None:
    """None when the effect names no rule of the tradition, or uses
    nothing."""
    rule = rule_of(tradition, effect)
    if rule is None or not effect.uses:
        return None
    score = int(
        hc.casting_score(
            character, tradition, rule, effect.uses, aura=aura, aura_realm=aura_realm
        ).total
    )
    if rule.lab or rule.die == "none" or rule.magnitude_is_score:
        return EffectTotal(score, rule.lab)
    die = effect.level * rule.divisor - score
    fatigue = (
        (effect.level - rule.failure_margin) * rule.divisor - score
        if rule.failure_margin
        else None
    )
    return EffectTotal(score, False, die, fatigue)


def total_words(found: EffectTotal | None, effect: TraditionEffect) -> str:
    """The effect's total as the sheet says it, and an item's charges."""
    if found is None:
        words = "choose its casting rule and Arts"
    elif found.lab:
        words = f"Lab Total {found.score}"
    else:
        words = f"Casting Score {found.score}"
        if found.die is not None:
            if found.die <= 1:
                words += ", always reaches its level"
            else:
                words += f", needs a die of {found.die}"
                if found.fatigue_die is not None:
                    words += f" ({max(found.fatigue_die, 1)} for a Fatigue level)"
    if effect.item and effect.charges:
        words += f"; {effect.charges} left"
    return words
