"""Faerie rites: the hedge wizardry of the ollamhain, the volkhvy and the
wise folk (Realms of Power: Faerie, Chapter Six: Faerie Wizardry,
pp. 121-131; Errata p. 68).

A rite pairs any Faerie Method with any Faerie Power: the Method's
Characteristic + Method + Power + the Faerie aura + a stress die is the
level of the effect made (p. 121). The Powers' guidelines (each
tradition's entry holds those of the Powers it lists) and the Faerie
Ranges, Durations and Targets are catalog data (TraditionDef.guidelines
and effect_parameters), so a rite's level is
worked out as any hedge effect's is (rules.hedge_effects.effect_level:
the base, then 5 levels a magnitude). Faerie rites may also use the
Hermetic parameters and House Merinita's Faerie Magic ones (DE pp.
237-238), and the catalog lists them all but Merinita's Bargain Duration,
which RoP: Faerie doesn't give rites. Geas (Condition) and If (Condition)
take the triggered effect's Duration as further magnitudes (pp. 122-123). What is particular to rites:

- **The Sympathy limit** (p. 121): a rite reaches at most 5 x the
  applicable Sympathy Traits, negatives counted as positive (Traits +1 and
  -4 allow level 25). With Empathy each further Fatigue level spent adds
  the limit again (Traits 3: 30 for two Fatigue levels, 45 for three;
  p. 124). Only the Traits that apply to the rite's target count, and a
  Conjure change counts the Traits of both its states (p. 125). The book's
  limit is firm; the app can't tell which Traits apply, so it only warns
  when a rite needs more than all the character's Sympathy Traits
  together, temporary ones included (they work as Sympathy Traits,
  p. 127), and its note says which Traits the book counts.
- **Symbol** (pp. 122-123): each Symbol parameter needs 3 points of
  applicable Sympathy Traits (all three, 9). Symbol, Season, Aura, Faerie,
  Hidden and If (Condition) need a ritual, as Merinita's Until
  (Condition) and Year + 1 do; a ritual rite takes fifteen minutes a
  magnitude but no vis, and no rite is permanent except through a natural
  process (aging, healing, Warping) (p. 121).
- **The Methods** (pp. 122-124): Evocation (Communication) costs a
  Warping Point or a Confidence Point and lets vis feed any rite, +2 a
  pawn up to Evocation + the Power; Enchantment (Presence) is a
  performance against 3 x the rite's magnitude first; Empathy (Stamina)
  costs a Fatigue level (a Light Wound without one) and an hour's trance.
- **Presence** as a Range reaches as far as the caster's Presence
  (p. 122); it counts as Voice.
- **Summoning** a faerie (Ars Fabulosa, p. 131) reaches a Might of at
  most 5 x the applicable Sympathy Traits.

Pattern: plain functions over the effect and the character's Traits;
the data is the catalog's, as every hedge tradition's guidelines are.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..models import Character, ScoredTrait, TraditionDef, TraditionEffect
from . import faerie_sympathy
from . import hedge_effects as he
from .casting import magnitude
from .rounding import round_up
from .scores import ability_level

SOURCE = (
    "Realms of Power: Faerie, Chapter Six: Faerie Wizardry, pp. 121-131; "
    "Errata p. 68; Ars Magica Definitive Edition, Faerie Magic, pp. 237-238"
)

#: The casting rule faerie rites are cast with, in the traditions' data.
FAERIE_RITE = "Faerie rite"
#: Levels each point of applicable Sympathy Traits allows (p. 121).
LEVELS_PER_POINT = 5
#: Points of applicable Sympathy Traits each Symbol parameter needs.
SYMBOL, SYMBOL_POINTS = "Symbol", 3
#: The Faerie and Faerie Magic parameters that need a ritual (DE p. 237;
#: RoP: Faerie pp. 122-123), by kind.
RITUAL_ONLY: dict[str, frozenset[str]] = {
    "range": frozenset({SYMBOL}),
    "duration": frozenset(
        {
            SYMBOL,
            "Season",
            "Aura",
            "Faerie",
            "Hidden",
            "If (Condition)",
            "Until (Condition)",
            "Year + 1",
        }
    ),
    "target": frozenset({SYMBOL}),
}
#: Each three-fold step of an Enchantment performance (p. 123).
ENCHANTMENT_STEP = 3
#: Pawns of vis Evocation adds to the total, each (p. 123).
EVOCATION_VIS = 2


#: The Faerie Methods (pp. 122-124).
EVOCATION, ENCHANTMENT, EMPATHY = "Evocation", "Enchantment", "Empathy"
#: The Power whose changes count the Traits of both states (p. 125).
CONJURE = "Conjure"


#: How far the Presence Range reaches, by the caster's Presence (p. 122):
#: (least Presence, paces).
PRESENCE_PACES: tuple[tuple[int, int], ...] = (
    (4, 100),
    (2, 50),
    (-1, 15),
    (-3, 5),
)


def presence_paces(presence: int) -> int:
    """The paces the Presence Range reaches: 0 (the caster alone) at
    Presence -4 or below (p. 122)."""
    return next((paces for least, paces in PRESENCE_PACES if presence >= least), 0)


def sympathy_points(traits: Sequence[ScoredTrait]) -> int:
    """The Sympathy Traits' sizes added up, negatives as positive
    (p. 121)."""
    return sum(abs(t.score) for t in faerie_sympathy.sympathy_traits(traits))


def max_rite_level(points: int, fatigue_levels: int = 1) -> int:
    """The highest rite `points` of applicable Sympathy Traits allow; with
    Empathy, multiplied by the Fatigue levels spent (pp. 121, 124)."""
    return LEVELS_PER_POINT * max(0, points) * max(1, fatigue_levels)


def points_needed(level: int) -> int:
    """The Sympathy points a rite of `level` needs: a fifth of it, rounded
    up (p. 121)."""
    return round_up(max(0, level) / LEVELS_PER_POINT)


def symbol_points(effect: TraditionEffect) -> int:
    """The applicable Sympathy points its Symbol parameters need, 3 each
    (pp. 122-123)."""
    count = sum(
        1 for name in (effect.range, effect.duration, effect.target) if name == SYMBOL
    )
    return SYMBOL_POINTS * count


def needs_ritual(effect: TraditionEffect) -> list[str]:
    """Its parameters that need a ritual."""
    return [
        name
        for kind, name in (
            ("range", effect.range),
            ("duration", effect.duration),
            ("target", effect.target),
        )
        if name in RITUAL_ONLY[kind]
    ]


def enchantment_ease_factor(level: int) -> int:
    """The performance an Enchantment rite of `level` first needs: 3 x its
    magnitude (p. 123)."""
    return ENCHANTMENT_STEP * magnitude(level)


def evocation_vis_cap(evocation: int, power: int) -> int:
    """The most pawns Evocation lets a rite use: Evocation + the Power
    (p. 123)."""
    return max(0, evocation) + max(0, power)


def max_summoned_might(points: int) -> int:
    """The highest Might a summoner's applicable Sympathy Traits reach
    (Ars Fabulosa, p. 131)."""
    return LEVELS_PER_POINT * max(0, points)


def is_rite(effect: TraditionEffect) -> bool:
    return effect.rule == FAERIE_RITE


def rite_notes(
    character: Character, tradition: TraditionDef, effect: TraditionEffect
) -> list[str]:
    """What a faerie rite asks of the caster beyond its level: the
    Sympathy points it needs against those he has, Symbol's points, a
    ritual its parameters need, and its Method's cost; none for another
    kind of effect (advice: the Traits that apply are the troupe's call)."""
    if not is_rite(effect):
        return []
    level = he.effect_level(tradition, effect)
    have = sympathy_points(character.personality_traits)
    notes: list[str] = []
    need = points_needed(level)
    if level:
        conjure = CONJURE in effect.uses
        line = (
            f"needs {need} point(s) of the Sympathy Traits that apply to its "
            "target, negatives by their size"
            + (", the Traits of both states for a change" if conjure else "")
        )
        if need > have:
            line += f"; more than all his ({have})"
        notes.append(line + f" (RoP: Faerie p. 121{', 125' if conjure else ''})")
    symbols = symbol_points(effect)
    if symbols:
        notes.append(f"Symbol needs {symbols} fitting Sympathy points (p. 122)")
    ritual = needs_ritual(effect)
    if ritual:
        notes.append(
            f"{' and '.join(ritual)}: a ritual, fifteen minutes a magnitude, no vis"
        )
    notes += _method_notes(character, effect, level, have)
    return notes


def _method_notes(
    character: Character, effect: TraditionEffect, level: int, have: int
) -> list[str]:
    """What the rite's Method asks (pp. 122-124)."""
    method = next(
        (u for u in effect.uses if u in (EVOCATION, ENCHANTMENT, EMPATHY)), ""
    )
    power = next((u for u in effect.uses if u != method), "")
    if method == ENCHANTMENT:
        return [
            f"first a performance against {enchantment_ease_factor(level)} (p. 123)"
        ]
    if method == EVOCATION:
        cap = evocation_vis_cap(
            ability_level(character, EVOCATION), ability_level(character, power)
        )
        return [
            f"a Warping or Confidence Point; vis +{EVOCATION_VIS} a pawn, up to "
            f"{cap} (p. 123)"
        ]
    if method == EMPATHY:
        return [
            "a Fatigue level and an hour's trance; each further Fatigue level "
            f"raises the limit by {max_rite_level(have)} (p. 124)"
        ]
    return []
