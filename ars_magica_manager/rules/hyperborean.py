"""The Hyperborean hymns' totals (Ancient Magic, Chapter Eight).

A hymn is a Supernatural Ability; each point of it (the score alone,
Puissant aside) holds 15 levels of Powers. A Power's level is worked out
on the Hermetic guidelines within the hymn's principles, with the
Hermetic effect modifications (uses a day, Penetration, triggers; DE
pp. 256-258), and the new 19 Years Duration one magnitude above Year
(p. 108). A season of recitation infuses it:

    Recitation Total = Com + Hymn + modifiers + aura
    Ease Factor      = (Power levels + modifiers) / 3, rounded up

after which the Power works at will with no roll (pp. 106-108). A relic
is enchanted the same way with Intelligence, one Power a season and no
devotional bonus, paying 2 Warping Points for each pawn of vis Hermetic
enchanting would need, its opening once (pp. 116-117). A choir sings a
one-off effect together: +5 levels a hymn beyond the first, vis equal to
the final Ease Factor, every helper's Com + Hymn added, and a bonus for
days spent (pp. 114-116). A Gifted hymnist suffers Illumination in place
of Twilight (pp. 105-106).

The book rounds the Ease Factor up (p. 108); other divisions round down
(DE p. 6).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from ..models import (
    EFFECT_FREQUENCIES,
    Character,
    Saga,
    TraditionDef,
    TraditionEffect,
)
from . import hedge_casting as hc
from .enchantment import frequency_of
from .lab import ability_score
from .rounding import round_down, round_up
from .spell_levels import DURATION_STEPS, RANGE_STEPS, TARGET_STEPS, add_magnitudes
from .warping import score_for, total_points

SOURCE = "Ancient Magic, Hyperborean Magic, pp. 103-118; Errata p. 58"
FREQUENCY_SOURCE = (
    "Ars Magica Definitive Edition, Effect Frequency and Effect "
    "Modifications, pp. 256-258"
)

TRADITION_ID = "trad_hyperborean_hymnists"
INFUSE = "Infuse a Power"
RELIC = "Enchant a relic"
CHOIR = "Choir"
POWER_POOL = "Power levels"

#: Levels of Powers each point of a hymn holds, and the most a hymn
#: holds in practice without vis (pp. 104, 109).
LEVELS_PER_POINT = 15
PRACTICAL_LEVELS = 150
#: Finding a hymn's source: Int + Magic Lore + a stress die (p. 107).
FINDING_EASE = 21
#: The new Duration, a magnitude above Year (p. 108).
NINETEEN_YEARS = "19 Years"
NINETEEN_YEARS_MAGNITUDES = DURATION_STEPS["Year"] + 1
#: Levels an environmental trigger adds (DE p. 257).
ENVIRONMENTAL_TRIGGER = 3

#: The recitation modifiers (p. 107): devotional behaviour +3 a season
#: before, at most three seasons; -1 a day without reciting, at most 20.
DEVOTION_PER_SEASON = 3
DEVOTION_SEASONS = 3
DISTRACTION_DAYS = 20
#: Hyperborean Descent, Minor and Major (pp. 104, 107).
DESCENT_BONUSES: dict[str, int] = {
    "vf_hyperborean_descent": 2,
    "vf_hyperborean_descent_major": 4,
}
#: A Personality Flaw Apollo favours or dislikes (p. 107).
TRAIT_MODIFIERS: dict[str, int] = {
    "Honourable Minor Personality Flaw": 1,
    "Honourable Major Personality Flaw": 3,
    "Dishonourable Minor Personality Flaw": -1,
    "Dishonourable Major Virtue or Flaw": -3,
}

#: Warping Points per pawn of vis a relic's enchanting would need (p. 117).
RELIC_WARPING_PER_PAWN = 2
#: A choir: +5 levels a hymn beyond the first (p. 115), and its bonus by
#: days spent (Choir Recitation Modifier, p. 115), longest first.
CHOIR_LEVELS_PER_HYMN = 5
CHOIR_DAYS: tuple[tuple[int, int], ...] = (
    (28, 5),
    (21, 4),
    (14, 3),
    (7, 2),
    (3, 1),
    (1, 0),
)
#: Invoking a Power at night: 15 minutes a point of its Ease Factor
#: (p. 110).
NIGHT_MINUTES_PER_EASE = 15
#: Illumination (pp. 105-106): it threatens when more than two Warping
#: Points come at once, and its Ease Factor gains +1 a 30 levels infused.
ILLUMINATION_POINTS = 2
LEVELS_PER_ILLUMINATION = 30
ILLUMINATION_DESCENT: dict[str, int] = {
    "vf_hyperborean_descent": -2,
    "vf_hyperborean_descent_major": -4,
}


# ---------------------------------------------------------------------------
# Powers and their Ease Factors


def magnitudes_of(range_: str = "", duration: str = "", target: str = "") -> int:
    """The magnitudes a Range, Duration and Target add: the Hermetic
    ones, and 19 Years at Year + 1 (p. 108). A blank one adds none."""
    durations = {**DURATION_STEPS, NINETEEN_YEARS: NINETEEN_YEARS_MAGNITUDES}
    total = 0
    for name, steps in (
        (range_, RANGE_STEPS),
        (duration, durations),
        (target, TARGET_STEPS),
    ):
        if not name:
            continue
        if name not in steps:
            raise ValueError(f"{name!r} isn't a Range, Duration or Target")
        total += steps[name]
    return total


def power_cost(
    base: int,
    *,
    range_: str = "",
    duration: str = "",
    target: str = "",
    magnitudes: int = 0,
    penetration: int = 0,
    uses_per_day: int = 1,
    environmental: bool = False,
    levels: int = 0,
) -> int:
    """A Power's level cost: the guideline's base raised by its Range,
    Duration, Target and further magnitudes (size, requisites), then the
    effect modifications: a level a 2 Penetration (rounded up), the uses a
    day as the Effect Frequency Table prices them, +3 for an environmental
    trigger, and any other levels (DE pp. 256-258; Ancient Magic p. 108)."""
    level = add_magnitudes(base, magnitudes_of(range_, duration, target) + magnitudes)
    level += round_up(max(penetration, 0) / 2)
    level += EFFECT_FREQUENCIES[frequency_of(uses_per_day)] if uses_per_day > 1 else 0
    level += ENVIRONMENTAL_TRIGGER if environmental else 0
    return level + levels


def recitation_ease(levels: int) -> int:
    """The recitation (or a relic's enchantment) Ease Factor: the Power
    levels with their modifiers, divided by 3 and rounded up (p. 108)."""
    return round_up(max(levels, 0) / 3)


def most_levels(total: int) -> int:
    """The most Power levels a recitation total reaches: an Ease Factor
    of `total` is (3 x total) levels at most."""
    return max(total, 0) * 3


def night_minutes(ease: int) -> int:
    """How long a Power takes to invoke at night (p. 110)."""
    return NIGHT_MINUTES_PER_EASE * max(ease, 0)


def numina_resistance(level: int) -> int:
    """The Magic Resistance a Numina of Apollo Power gives against effects
    of its hymn's principles: its level - 5. Any hymn may hold it; the
    book prints it as a Vim Power (p. 110), its Form counting only for
    Magic Resistance (p. 109)."""
    return max(level - 5, 0)


# ---------------------------------------------------------------------------
# The levels a hymnist holds


def hymns_of(tradition: TraditionDef) -> list[str]:
    """The hymns: the tradition's favored Abilities."""
    return list(tradition.favored)


def hymn_levels(character: Character, hymn: str) -> int:
    """The Power levels a hymn holds: 15 a point of its score. Puissant
    does not raise them (p. 107)."""
    base, _ = ability_score(character, hymn)
    return LEVELS_PER_POINT * base


def infused_powers(
    character: Character, hymn: str | None = None
) -> list[TraditionEffect]:
    """The Powers the character has infused (the hymnists' effects on the
    Infuse a Power rule), of one hymn or of all."""
    return [
        e
        for e in character.tradition_effects
        if e.tradition == TRADITION_ID
        and e.rule == INFUSE
        and not e.item
        and (hymn is None or hymn in e.uses)
    ]


def infused_levels(character: Character, hymn: str | None = None) -> int:
    """The levels of Powers infused: each Power's level as typed (its
    level cost)."""
    return sum(max(e.level, 0) for e in infused_powers(character, hymn))


def levels_left(character: Character, hymn: str, vis_levels: int = 0) -> int:
    """The levels a hymn has still to spend on Powers, with any bought with
    vis (a level a pawn, p. 109)."""
    return hymn_levels(character, hymn) + vis_levels - infused_levels(character, hymn)


def vis_levels(pawns: int, pawns_per_level: int = 1) -> int:
    """Extra Power levels bought with vis: one a pawn, or fewer where the
    troupe makes them dearer (p. 109)."""
    return max(pawns, 0) // max(pawns_per_level, 1)


# ---------------------------------------------------------------------------
# The recitation total's modifiers


def descent_bonus(character: Character) -> int:
    """+2 for Hyperborean Descent, +4 for the Major Virtue (p. 107); the
    best one counts."""
    held = {vf.vf_id for vf in character.virtues_flaws}
    return max((n for vf, n in DESCENT_BONUSES.items() if vf in held), default=0)


def recitation_modifiers(
    character: Character,
    *,
    devotional_seasons: int = 0,
    days_without: int = 0,
    traits: Mapping[str, int] | None = None,
    relic: bool = False,
) -> list[tuple[str, int]]:
    """The modifiers a recitation total adds besides Com, the Hymn, the
    Dead Language and the aura (p. 107): devotional behaviour (not for a
    relic, p. 116), days without reciting, Hyperborean Descent, and the
    Personality Flaws Apollo favours or dislikes (TRAIT_MODIFIERS: how
    many of each)."""
    found: list[tuple[str, int]] = []
    if devotional_seasons > 0 and not relic:
        seasons = min(devotional_seasons, DEVOTION_SEASONS)
        found.append(
            (f"Devotional behaviour, {seasons} seasons", DEVOTION_PER_SEASON * seasons)
        )
    if days_without > 0:
        days = min(days_without, DISTRACTION_DAYS)
        found.append((f"{days} days without reciting", -days))
    descent = descent_bonus(character)
    if descent:
        found.append(("Hyperborean Descent", descent))
    for name, count in (traits or {}).items():
        if count:
            found.append((name, TRAIT_MODIFIERS[name] * count))
    return found


# ---------------------------------------------------------------------------
# Relics and choirs


def relic_vis(level: int) -> int:
    """The pawns Hermetic enchanting would spend instilling a Power: a
    pawn a 10 levels or fraction (DE p. 258)."""
    return round_up(max(level, 0) / 10)


def relic_warping(level: int, opening_pawns: int = 0) -> int:
    """Warping Points a relic's Power costs its enchanter: 2 a pawn its
    vis would need, plus 2 a pawn of the item's opening the first time
    (p. 117). They never set off Illumination (p. 105)."""
    return RELIC_WARPING_PER_PAWN * (relic_vis(level) + max(opening_pawns, 0))


def choir_level(level: int, hymns: int = 1) -> int:
    """A choir's effect level: +5 for every hymn beyond the first."""
    return level + CHOIR_LEVELS_PER_HYMN * max(hymns - 1, 0)


def choir_vis(ease: int) -> int:
    """A choir spends as many pawns as its final Ease Factor (p. 115)."""
    return max(ease, 0)


def choir_days_bonus(days: int) -> int:
    """The choir's bonus for days of meditation: at least a day; +5 at
    most, from 28 days (p. 115)."""
    return next((bonus for least, bonus in CHOIR_DAYS if days >= least), 0)


def choir_total(
    focus_total: int,
    helpers: Sequence[int],
    *,
    leader_ceremony: int | None,
    days: int = 1,
) -> int:
    """The focus's recitation total, the Ceremony Bonus (each helper's
    Com + Hymn; a leader's Ceremony caps how many count, and without a
    leader the bonus loses a point for each participant, counted as the
    helpers alone, as in the choir example, where the focus stands apart
    from the "five participants") and the days' bonus (pp. 115-116)."""
    if leader_ceremony is None:
        bonus = sum(helpers) - len(helpers)
    else:
        counted = sorted(helpers, reverse=True)[: max(leader_ceremony, 0)]
        bonus = sum(counted)
    return focus_total + bonus + choir_days_bonus(days)


# ---------------------------------------------------------------------------
# Illumination


def illumination_applies(character: Character) -> bool:
    """Illumination replaces Twilight for a Gifted hymnist whose first
    tradition is the hymns; a Hermetic magus always has Twilight (p. 105)."""
    return (
        hc.gifted(character)
        and character.type != "magus"
        and bool(character.traditions)
        and character.traditions[0] == TRADITION_ID
    )


def highest_hymn(character: Character) -> int:
    hymns = [a.name for a in character.abilities if a.name.startswith("Hymn ")]
    return max((hc.score(character, h) for h in hymns), default=0)


def illumination_control(character: Character) -> int:
    """Stamina + Concentration + the highest Hymn, before the stress die
    (p. 105)."""
    return (
        character.characteristics.stamina
        + hc.score(character, "Concentration")
        + highest_hymn(character)
    )


def illumination_modifiers(character: Character) -> int:
    """The Illumination Ease Factor's modifiers: -2 or -4 for Hyperborean
    Descent, +1 a 30 levels of Powers infused (p. 105)."""
    held = {vf.vf_id for vf in character.virtues_flaws}
    descent = min(
        (n for vf, n in ILLUMINATION_DESCENT.items() if vf in held), default=0
    )
    return descent + round_down(infused_levels(character) / LEVELS_PER_ILLUMINATION)


def illumination_ease(character: Character, points: int, aura: int) -> int:
    """The Illumination Ease Factor before its stress die: the Warping
    Score once `points` are added + the points + the aura + the
    modifiers. 0 when two or fewer points come at once (no roll)."""
    if points <= ILLUMINATION_POINTS:
        return 0
    return (
        updated_score(character, points)
        + points
        + aura
        + illumination_modifiers(character)
    )


def updated_score(character: Character, points: int) -> int:
    """The Warping Score after gaining `points`."""
    return score_for(total_points(character) + max(points, 0))


def transformed_hours(character: Character, points: int) -> int:
    """How long Apollo's Light transforms him: an hour for every Warping
    Point he has, those just gained included (p. 105)."""
    return total_points(character) + max(points, 0)


def bright_lightening(character: Character, points: int, aura: int) -> int:
    """Failing the control roll on purpose: Warping Score + aura +
    modifiers more Warping Points, and as many xp in hymns. The score is
    the one after the `points` that called for the roll, as in the
    example and the roll's own Ease Factor (pp. 105-106)."""
    return max(
        updated_score(character, points) + aura + illumination_modifiers(character),
        0,
    )


def return_ease(score: int, aura: int, modifiers: int, failures: int = 0) -> int:
    """Asserting his human nature when the transformation ends: Warping
    Score + aura + modifiers with no die, each failure a day more and a
    cumulative -1 to the roll (counted here as +1 to the Ease Factor)."""
    return score + aura + modifiers + max(failures, 0)


# ---------------------------------------------------------------------------
# What the tradition chapter says


def levels_lines(character: Character) -> list[str]:
    """Each hymn held: the levels its score holds, those infused and those
    left."""
    lines = []
    for ability in character.abilities:
        if not ability.name.startswith("Hymn "):
            continue
        held = hymn_levels(character, ability.name)
        used = infused_levels(character, ability.name)
        lines.append(
            f"{ability.name} {ability_score(character, ability.name)[0]}: "
            f"{held} levels, {used} infused, {held - used} left."
        )
    return lines


def infuse_yields(saga: Saga, character: Character, total: int) -> list[str]:
    """A season of recitation: the most Power levels the total infuses,
    with Hyperborean Descent added, and each hymn's levels left."""
    descent = descent_bonus(character)
    lines = []
    if descent:
        total += descent
        lines.append(f"With Hyperborean Descent (+{descent}): {total}.")
    lines.append(
        f"Infuses Powers of up to {most_levels(total)} levels (Ease Factor "
        "= levels / 3, rounded up); a season of devotion before adds +3, "
        "up to +9, and each day without reciting -1."
    )
    lines += levels_lines(character)
    lines.append("Each pawn of vis spent adds a level beyond the hymn's.")
    return lines


def relic_yields(saga: Saga, character: Character, total: int) -> list[str]:
    """A season enchanting a relic: the most levels of one Power, and the
    Warping Points it costs."""
    descent = descent_bonus(character)
    lines = []
    if descent:
        total += descent
        lines.append(f"With Hyperborean Descent (+{descent}): {total}.")
    levels = most_levels(total)
    lines.append(
        f"Enchants one Power of up to {levels} levels; a Power of that level "
        f"costs {relic_warping(levels)} Warping Points (2 a pawn of the vis it "
        "would need), and the item's opening 2 a pawn the first time."
    )
    return lines


def illumination_lines(character: Character, aura: int) -> list[str]:
    """Illumination as the character faces it: the control total, the
    Ease Factor's modifiers and the Apollonian Personality Trait."""
    if not illumination_applies(character):
        return [
            "Illumination is only for a Gifted hymnist whose first tradition "
            "is the hymns; others Warp as usual."
        ]
    score = character.aging.warping_score
    modifiers = illumination_modifiers(character)
    fewest = ILLUMINATION_POINTS + 1
    return [
        f"Apollonian Personality Trait {score:+d}, and Dutybound (Minor).",
        f"Control: Sta + Concentration + highest Hymn = "
        f"{illumination_control(character)} + a stress die.",
        f"Ease Factor: updated Warping Score + points gained + aura {aura} "
        f"{modifiers:+d} (Descent, infused levels) + a stress die.",
        f"Bright Lightening: updated Warping Score + aura {aura} "
        f"{modifiers:+d} more Warping Points and as many xp in hymns "
        f"({bright_lightening(character, fewest, aura)} after {fewest} points).",
    ]
