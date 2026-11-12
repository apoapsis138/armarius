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
power) is as strong as the score allows, so it needs no die for a level;
cast against an Ease Factor it still shows the die that Ease Factor
needs (Hedge Magic RE p. 36). An item is made with the tradition's Lab
Total (a lab rule): its Lab Total is shown beside the item's level, and
its charges are counted down by hand. A stressed casting shows its botch
dice (rules.hedge_casting.botch_dice).

An effect built on one of the tradition's guidelines (TraditionDef.
guidelines) has its level worked out, as spell_levels does for Hermetic
spells: the guideline's base, plus the magnitudes of its Range, Duration
and Target (the tradition's own, or the Hermetic ones when it lists
none) and any further magnitudes, each adding 5 levels (1 below level 5),
or 3 for a tradition whose levels or Ease Factors step by 3 (Soqotran
spells, Rival Magic p. 124; Augustan rites, p. 57; utiseta, p. 90). A
Range or Duration with a base for the Art used (an Amazon Consonant's)
costs a magnitude a step from that base, either way (Rival Magic
pp. 23-25). An effect naming no guideline, or a General one, keeps its
typed level.

Rules: each Hedge Magic tradition's effects and items.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from ..models import (
    CastingRule,
    Character,
    EffectParameter,
    Guideline,
    TraditionDef,
    TraditionEffect,
)
from . import hedge_casting as hc
from . import realms
from .spell_levels import DURATION_STEPS, RANGE_STEPS, TARGET_STEPS, add_magnitudes

SOURCE = "Hedge Magic, Revised Edition, Chapters Two to Seven, pp. 17-141"


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


# ---------------------------------------------------------------------------
# Guidelines and levels


def guideline_key(guideline: Guideline) -> str:
    """How an effect names its guideline: the Arts and the label, as
    several Art pairs share a label ("Gruagach Give/Gruagach Blessing: +1
    to one Ability")."""
    return f"{'/'.join(guideline.arts)}: {guideline.name}"


def guidelines_for(
    tradition: TraditionDef, uses: Sequence[str] = ()
) -> list[Guideline]:
    """The tradition's guidelines an effect using `uses` may be built on:
    those whose Arts it all uses (every one when it names no Arts)."""
    if not uses:
        return list(tradition.guidelines)
    held = set(uses)
    return [g for g in tradition.guidelines if set(g.arts) <= held]


def guideline_of(tradition: TraditionDef, effect: TraditionEffect) -> Guideline | None:
    """The guideline the effect names, by its key or its label (the one
    of the Arts it uses, when several share a label)."""
    if not effect.guideline:
        return None
    for g in tradition.guidelines:
        if guideline_key(g) == effect.guideline:
            return g
    named = [g for g in tradition.guidelines if g.name == effect.guideline]
    fitting = [g for g in named if set(g.arts) <= set(effect.uses)]
    found = fitting or named
    return found[0] if found else None


_HERMETIC_STEPS = {
    "range": RANGE_STEPS,
    "duration": DURATION_STEPS,
    "target": TARGET_STEPS,
}


def parameters_for(
    tradition: TraditionDef,
    kind: str,
    uses: Sequence[str] = (),
    *,
    item: bool = False,
) -> list[EffectParameter]:
    """The Ranges (Durations, Targets) an effect of the tradition may
    have: the tradition's own that suit its Arts and whether it is an
    item, or the Hermetic ones when the tradition lists none at all.
    None for a tradition whose guideline levels are the effect's and
    which lists no parameters (a vitki's runes)."""
    if not tradition.effect_parameters:
        if tradition.level_steps == "none":
            return []
        return [EffectParameter(kind, n, m) for n, m in _HERMETIC_STEPS[kind].items()]
    held = set(uses)
    found: list[EffectParameter] = []
    for p in tradition.effect_parameters:
        if p.kind != kind or (p.arts and not held & set(p.arts)):
            continue
        if (p.items == "items" and not item) or (p.items == "effects" and item):
            continue
        if any(q.name == p.name for q in found):
            continue
        found.append(p)
    return found


def parameter_names(tradition: TraditionDef, kind: str) -> list[str]:
    """Every Range (Duration, Target) any effect of the tradition may
    have, as a form offers them."""
    if not tradition.effect_parameters:
        return [p.name for p in parameters_for(tradition, kind)]
    names: list[str] = []
    for p in tradition.effect_parameters:
        if p.kind == kind and p.name not in names:
            names.append(p.name)
    return names


def parameter_cost(
    tradition: TraditionDef,
    kind: str,
    name: str,
    uses: Sequence[str] = (),
    *,
    item: bool = False,
) -> int | None:
    """The magnitudes a Range, Duration or Target adds, or None when the
    effect can't have it. With a base for one of the Arts used only the
    steps from the base count: up adds, down takes away, or with
    `bases_either_way` each step either way adds one."""
    options = parameters_for(tradition, kind, uses, item=item)
    chosen = next((p for p in options if p.name == name), None)
    if chosen is None:
        return None
    for art in uses:
        base_name = tradition.parameter_bases.get(art, {}).get(kind)
        base = next((p for p in options if p.name == base_name), None)
        if base is not None:
            steps = chosen.magnitudes - base.magnitudes
            return abs(steps) if tradition.bases_either_way else steps
    return chosen.magnitudes


@dataclass
class EffectDesign:
    """An effect's level worked out from its guideline: the base, and
    (what, magnitudes) for each step, as a design line lists them."""

    level: int
    base: int
    steps: list[tuple[str, int]] = field(default_factory=list)
    #: Parameters the tradition doesn't allow the effect.
    problems: list[str] = field(default_factory=list)

    def design_line(self) -> str:
        """The design as a stat block gives it: "Base 5, +1 Voice, +2 Sun"."""
        return ", ".join(
            [f"Base {self.base}", *(f"{n:+d} {what}" for what, n in self.steps if n)]
        )


def raise_level(tradition: TraditionDef, base: int, magnitudes: int) -> int:
    """`base` raised by magnitudes as the tradition's levels step."""
    if tradition.level_steps == "three":
        return max(base + 3 * magnitudes, 0)
    return add_magnitudes(base, magnitudes)


def effect_design(
    tradition: TraditionDef, effect: TraditionEffect
) -> EffectDesign | None:
    """The level of an effect built on a guideline; None when it names
    none or a General one (its typed level stands)."""
    guideline = guideline_of(tradition, effect)
    if guideline is None or guideline.general:
        return None
    design = EffectDesign(level=guideline.level, base=guideline.level)
    for kind, name in (
        ("range", effect.range),
        ("duration", effect.duration),
        ("target", effect.target),
    ):
        if not name:
            continue
        cost = parameter_cost(tradition, kind, name, effect.uses, item=effect.item)
        if cost is None:
            design.problems.append(f"{name} isn't one of the tradition's {kind}s.")
            continue
        design.steps.append((name, cost))
    if effect.magnitudes:
        design.steps.append(("more", effect.magnitudes))
    design.level = raise_level(
        tradition, guideline.level, sum(n for _, n in design.steps)
    )
    return design


def effect_level(tradition: TraditionDef, effect: TraditionEffect) -> int:
    """The level (or Ease Factor) the effect is cast against: worked out
    from its guideline, or as typed."""
    design = effect_design(tradition, effect)
    return design.level if design is not None else effect.level


@dataclass(frozen=True)
class EffectTotal:
    """What an effect's casting comes to: the Casting Score (or Lab
    Total), and the least die that reaches its level, plain and for a
    Fatigue level (None when there is no die or no margin)."""

    score: int
    lab: bool
    die: int | None = None
    fatigue_die: int | None = None
    #: What the die is rolled against ("level" or "Ease Factor"), the
    #: level or Ease Factor, the level a Supernatural Ability's effect
    #: counts as (5 x score), and the botch dice of a stressed casting.
    against: str = "level"
    level: int = 0
    equivalent: int | None = None
    botch_dice: int = 0


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
    level = effect_level(tradition, effect)
    ease = rule.against == "Ease Factor"
    equivalent = (
        hc.equivalent_level(rule, max(hc.score(character, u) for u in effect.uses))
        if rule.magnitude_is_score
        else None
    )
    botch = hc.botch_dice(
        tradition, rule, level=level, aura=aura, aura_realm=aura_realm
    )
    if (
        rule.lab
        or rule.die == "none"
        or (rule.magnitude_is_score and not (ease and level))
    ):
        return EffectTotal(
            score, rule.lab, level=level, equivalent=equivalent, botch_dice=botch
        )
    die = level * rule.divisor - score
    fatigue = (
        (level - rule.failure_margin) * rule.divisor - score
        if rule.failure_margin
        else None
    )
    return EffectTotal(
        score,
        False,
        die,
        fatigue,
        against="Ease Factor" if ease else "level",
        level=level,
        equivalent=equivalent,
        botch_dice=botch,
    )


def total_words(found: EffectTotal | None, effect: TraditionEffect) -> str:
    """The effect's total as the sheet says it, and an item's charges."""
    if found is None:
        words = "choose its casting rule and Arts"
    elif found.lab:
        words = f"Lab Total {found.score}"
    else:
        words = f"Casting Score {found.score}"
        ease = found.against == "Ease Factor"
        if found.die is not None:
            if found.die <= 1:
                words += ", always reaches its " + (
                    f"Ease Factor of {found.level}" if ease else "level"
                )
            else:
                words += f", needs a die of {found.die}"
                if ease:
                    words += f" against Ease Factor {found.level}"
                if found.fatigue_die is not None:
                    words += f" ({max(found.fatigue_die, 1)} for a Fatigue level)"
        if found.equivalent is not None:
            words += f"; counts as level {found.equivalent}"
        if found.botch_dice:
            dice = "die" if found.botch_dice == 1 else "dice"
            words += f"; {found.botch_dice} botch {dice} if stressed"
    if effect.item and effect.charges:
        words += f"; {effect.charges} left"
    return words
