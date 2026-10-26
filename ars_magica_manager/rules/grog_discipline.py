"""Rewards, punishments and pensions for a covenant's covenfolk.

Grogs, Chapter Two (pp. 23-26):

- Rewards are set by the turb captain, steward or chamberlain and
  announced before the turb. Improved rations last a day to a year; a
  year of them improves the grog's Living Conditions Modifier for aging
  by 1. Pay and a Half lasts a season or more, or for good. Improved
  equipment (Expensive, or well made, rarely enchanted) is his for good,
  but surrendered on a demotion. Promotion raises his rank: better food,
  lodging, pay and pension.
- Punishments, in order of severity: castigation, relegation to inferior
  duties, reduction of rations (a season or two of the year on them is
  -1 to his Living Conditions for aging, three or four -2), flogging (1, 5
  or 10 blows: 1, 2 or 3 Light Wounds and 1, 3 or 5 Long-Term Fatigue
  levels), reduction in rank, whipping (10 lashes a Light Wound, 30 a
  Medium, 50 a Heavy; the short whip two of each; a week to recover, a day
  for ten lashes or fewer, pay docked for longer), dismissal and the
  fustuarium (death; few covenants have the right). A fair punishment,
  clearly given, costs no Prevailing Loyalty; the grog's own Loyal may
  drop.
- A retired grog still counts as one of the covenant for its finances;
  his pension is half to three-quarters of his pay, or he pays rent
  instead and is fed free; a widow gets the pension her husband would
  have had.

The Definitive Edition sets the pension at half Wages until death, +10
Loyalty points when the covenant grants one (DE p. 186); it wins over
Grogs' half to three-quarters. A Year of rations is read as the four
seasons of the aging year. In the Definitive Edition's aging roll the
Living Conditions are subtracted, so Grogs' "-1 improvement" is +1 here
and its "+1 penalty" -1.

Covenants pp. 38-40 give the Loyalty points: a punishment ordered by a
magus costs points by its kind (minor humiliation -1, public humiliation
-3, restraint -6, infliction of pain -9, brutal punishment -12, brutal
and clearly enjoyed -15); with a positive Prevailing Loyalty only an
unjust one does; one the turb captain, steward or chamberlain gives
fittingly costs none. The victim's Reputation adds to the penalty if he
is loved, and takes from it if he is disliked. A wound a magus deals
himself costs points too (superficial -1, light -3, medium -6, heavy -9,
incapacitating -12, death -15), one step worse by magic.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..models import SEASONS, Character, Covenant, Discipline, Saga
from ..models.seasons import season_order
from . import covenfolk

SOURCE = (
    "Grogs, Chapter Two: Life in the Covenant, Free Time, Rewards, Punishments, "
    "Accommodation, Families, Retirement and Pensions, pp. 23-26; Covenants, "
    "Chapter Three: Governance, Decreasing and Increasing Loyalty, pp. 38-40; "
    "Ars Magica Definitive Edition, Situational Modifiers to Loyalty, p. 186"
)

# -- kinds, in the books' order --

IMPROVED_RATIONS = "improved_rations"
PAY_AND_A_HALF = "pay_and_a_half"
IMPROVED_EQUIPMENT = "improved_equipment"
PROMOTION = "promotion"
REWARDS: tuple[str, ...] = (
    IMPROVED_RATIONS,
    PAY_AND_A_HALF,
    IMPROVED_EQUIPMENT,
    PROMOTION,
)

CASTIGATION = "castigation"
INFERIOR_DUTIES = "inferior_duties"
REDUCED_RATIONS = "reduced_rations"
FLOGGING = "flogging"
REDUCTION_IN_RANK = "reduction_in_rank"
WHIPPING = "whipping"
DISMISSAL = "dismissal"
FUSTUARIUM = "fustuarium"
#: The punishments, least severe first (Grogs pp. 24-25).
PUNISHMENTS: tuple[str, ...] = (
    CASTIGATION,
    INFERIOR_DUTIES,
    REDUCED_RATIONS,
    FLOGGING,
    REDUCTION_IN_RANK,
    WHIPPING,
    DISMISSAL,
    FUSTUARIUM,
)

RETIRED = "retired"
WIDOW_PENSION = "widow_pension"

LABELS: dict[str, str] = {
    IMPROVED_RATIONS: "Improved rations",
    PAY_AND_A_HALF: "Pay and a Half",
    IMPROVED_EQUIPMENT: "Improved equipment",
    PROMOTION: "Promotion in rank",
    CASTIGATION: "Castigation",
    INFERIOR_DUTIES: "Relegation to inferior duties",
    REDUCED_RATIONS: "Reduction of rations",
    FLOGGING: "Flogging",
    REDUCTION_IN_RANK: "Reduction in rank",
    WHIPPING: "Whipping",
    DISMISSAL: "Dismissal",
    FUSTUARIUM: "Fustuarium",
    RETIRED: "Retired",
    WIDOW_PENSION: "Widow's pension",
}
KINDS: tuple[str, ...] = (*REWARDS, *PUNISHMENTS, RETIRED, WIDOW_PENSION)

#: How long rations or Pay and a Half last: the label and the seasons
#: (0: less than a season; None: for good).
DURATIONS: tuple[tuple[str, int | None], ...] = (
    ("A day", 0),
    ("A month", 0),
    ("A season", 1),
    ("Two seasons", 2),
    ("Three seasons", 3),
    ("A year", 4),
    ("For good", None),
)
DURATION_SEASONS: dict[str, int | None] = dict(DURATIONS)
#: The kinds that last a while.
LASTING: tuple[str, ...] = (IMPROVED_RATIONS, PAY_AND_A_HALF, REDUCED_RATIONS)

#: The usual ranks, lowest first (Grogs p. 24), as a hint.
RANKS = "grog, custos, sergeant, then captain, chamberlain or steward"

# -- the punishments' effects --

#: Flogging: blows -> (Light Wounds, Long-Term Fatigue levels) (p. 25).
FLOGGING_BLOWS: dict[int, tuple[int, int]] = {1: (1, 1), 5: (2, 3), 10: (3, 5)}

#: Whipping: the fewest lashes for each wound (p. 25).
WHIPPING_WOUNDS: tuple[tuple[int, str], ...] = (
    (50, "heavy"),
    (30, "medium"),
    (10, "light"),
)
#: The short whip gives this many wounds of the kind.
SHORT_WHIP_WOUNDS = 2
#: Days to recover before his pay is docked: a week, or a day after ten
#: lashes or fewer.
WHIPPING_RECOVERY_DAYS = 7
LIGHT_WHIPPING_DAYS = 1
LIGHT_WHIPPING_LASHES = 10

#: Living Conditions for aging from rations (p. 23, p. 25).
IMPROVED_RATIONS_LIVING = 1
REDUCED_RATIONS_LIVING = ((3, -2), (1, -1))

# -- Loyalty (Covenants pp. 38-39) --

MINOR_HUMILIATION = "Minor humiliation"
PUBLIC_HUMILIATION = "Public humiliation"
RESTRAINT = "Restraint"
INFLICTION_OF_PAIN = "Infliction of pain"
BRUTAL = "Brutal punishment"
BRUTAL_ENJOYED = "Brutal punishment clearly enjoyed by the magus"
#: Example Loyalty Point Penalties, Punishment column.
PUNISHMENT_PENALTIES: tuple[tuple[str, int], ...] = (
    (MINOR_HUMILIATION, -1),
    (PUBLIC_HUMILIATION, -3),
    (RESTRAINT, -6),
    (INFLICTION_OF_PAIN, -9),
    (BRUTAL, -12),
    (BRUTAL_ENJOYED, -15),
)
PENALTY_POINTS: dict[str, int] = dict(PUNISHMENT_PENALTIES)
#: Which row each of Grogs' punishments usually falls in: a single blow
#: is a minor humiliation, the shaming ones public, reduced rations
#: restraint ("a week on half rations"), those that wound brutal.
USUAL_CATEGORY: dict[str, str] = {
    CASTIGATION: MINOR_HUMILIATION,
    INFERIOR_DUTIES: PUBLIC_HUMILIATION,
    REDUCED_RATIONS: RESTRAINT,
    FLOGGING: BRUTAL,
    REDUCTION_IN_RANK: PUBLIC_HUMILIATION,
    WHIPPING: BRUTAL,
    DISMISSAL: PUBLIC_HUMILIATION,
    FUSTUARIUM: BRUTAL,
}
#: The Wound column: what a wound a magus deals himself costs.
WOUND_STEPS: tuple[str, ...] = (
    "superficial",
    "light",
    "medium",
    "heavy",
    "incapacitating",
    "dead",
)
WOUND_PENALTIES: dict[str, int] = dict(zip(WOUND_STEPS, (-1, -3, -6, -9, -12, -15)))

OFFICER = "officer"
MAGUS = "magus"
ORDERED_BY: tuple[tuple[str, str], ...] = (
    ("The turb captain, steward or chamberlain", OFFICER),
    ("A magus", MAGUS),
)

#: A one-off celebration after a notable event earns a Loyalty point; a
#: yearly cycle of four or more feasts, a point a year (Covenants p. 40).
CELEBRATION_LOYALTY = 1


def is_reward(kind: str) -> bool:
    return kind in REWARDS


def is_punishment(kind: str) -> bool:
    return kind in PUNISHMENTS


def flogging(blows: int) -> tuple[int, int]:
    """(Light Wounds, Long-Term Fatigue levels) for 1, 5 or 10 blows."""
    return FLOGGING_BLOWS[blows]


def whipping(lashes: int, short: bool) -> list[str]:
    """The wounds a whipping deals: one of the kind its lashes reach, two
    with the short whip; none under ten lashes."""
    for least, severity in WHIPPING_WOUNDS:
        if lashes >= least:
            return [severity] * (SHORT_WHIP_WOUNDS if short else 1)
    return []


def whipping_recovery(lashes: int) -> int:
    """The days he is given to recover."""
    return (
        LIGHT_WHIPPING_DAYS
        if lashes <= LIGHT_WHIPPING_LASHES
        else WHIPPING_RECOVERY_DAYS
    )


def wounds_dealt(
    kind: str, *, blows: int = 1, lashes: int = 10, short: bool = False
) -> list[str]:
    """The wounds a punishment deals, by severity ("dead" for the
    fustuarium)."""
    if kind == FLOGGING:
        return ["light"] * flogging(blows)[0]
    if kind == WHIPPING:
        return whipping(lashes, short)
    if kind == FUSTUARIUM:
        return ["dead"]
    return []


def fatigue_dealt(kind: str, blows: int = 1) -> int:
    """The Long-Term Fatigue levels a punishment costs."""
    return flogging(blows)[1] if kind == FLOGGING else 0


def worse_wound(severity: str) -> str:
    """One step more severe (a wound dealt by magic)."""
    at = WOUND_STEPS.index(severity)
    return WOUND_STEPS[min(at + 1, len(WOUND_STEPS) - 1)]


@dataclass(frozen=True)
class LoyaltyCost:
    """What a punishment costs the covenant's Loyalty points, with why."""

    points: int = 0
    lines: list[str] = field(default_factory=list)


def loyalty_cost(
    category: str,
    *,
    ordered_by: str,
    just: bool,
    prevailing: int,
    reputation: int = 0,
    own_wounds: list[str] | None = None,
    by_magic: bool = False,
) -> LoyaltyCost:
    """The Loyalty points a punishment of `category` costs (Covenants pp.
    38-39). A fitting one from the turb captain, steward or chamberlain
    costs nothing; one a magus orders costs the table's points unless it
    is just and Prevailing Loyalty is positive. The victim's Reputation
    (loved positive, disliked negative) moves the penalty, never past 0.
    `own_wounds`: the wounds the magus deals himself, each costing its
    own points, one step worse by magic."""
    lines: list[str] = []
    points = 0
    counts = not just if ordered_by == OFFICER or prevailing > 0 else True
    if counts:
        base = PENALTY_POINTS[category]
        points = min(base - reputation, 0)
        lines.append(
            f"{category} {base:+d}"
            + (f", his Reputation {-reputation:+d}" if reputation else "")
            + "."
        )
    elif ordered_by == OFFICER:
        lines.append("A fitting punishment from an officer: no Loyalty lost.")
    else:
        lines.append(
            f"Just, with Prevailing Loyalty {prevailing:+d}: no Loyalty lost for "
            "the punishment."
        )
    for severity in own_wounds or []:
        step = worse_wound(severity) if by_magic else severity
        cost = WOUND_PENALTIES[step]
        points += cost
        lines.append(
            f"A {step} wound dealt by the magus himself"
            + (" (by magic, one step worse)" if by_magic else "")
            + f" {cost:+d}."
        )
    return LoyaltyCost(points, lines)


# -- what the records add up to --


def _start(record: Discipline) -> int:
    return season_order(season=record.season, year=record.year)


def stop_of(character: Character, record: Discipline) -> int | None:
    """The season (as a number) a lasting reward stops early: his
    retirement, or for Pay and a Half a later reduction in rank too; None
    while nothing has cut it short."""
    stops = (
        (RETIRED, REDUCTION_IN_RANK) if record.kind == PAY_AND_A_HALF else (RETIRED,)
    )
    later = [
        _start(r)
        for r in character.discipline
        if r is not record and r.kind in stops and _start(r) >= _start(record)
    ]
    return min(later) if later else None


def seasons_in_year(record: Discipline, year: int, stop: int | None = None) -> int:
    """How many seasons of `year` the record covers, up to (not including)
    the season `stop`: none for one under a season, every one after its
    start for one for good."""
    if record.seasons == 0:
        return 0
    first = _start(record)
    last = None if record.seasons is None else first + record.seasons - 1
    count = 0
    for index in range(len(SEASONS)):
        order = year * len(SEASONS) + index
        if order < first or (last is not None and order > last):
            continue
        if stop is not None and order >= stop:
            continue
        count += 1
    return count


def covered(character: Character, record: Discipline, year: int) -> int:
    """The seasons of `year` the record covers for him, cut short where
    stop_of says."""
    stop = stop_of(character, record) if record.kind in REWARDS else None
    return seasons_in_year(record, year, stop)


def rations_living(character: Character, year: int) -> int:
    """What his rations add to his Living Conditions for the aging roll of
    `year`: +1 for a whole year of improved rations, -1 for a season or two
    of reduced ones, -2 for three or four."""
    improved = sum(
        covered(character, r, year)
        for r in character.discipline
        if r.kind == IMPROVED_RATIONS
    )
    reduced = sum(
        covered(character, r, year)
        for r in character.discipline
        if r.kind == REDUCED_RATIONS
    )
    living = IMPROVED_RATIONS_LIVING if improved >= len(SEASONS) else 0
    for least, change in REDUCED_RATIONS_LIVING:
        if reduced >= least:
            living += change
            break
    return living


def rank(character: Character) -> str:
    """His rank after the last promotion or reduction ("" with none)."""
    changes = [
        r for r in character.discipline if r.kind in (PROMOTION, REDUCTION_IN_RANK)
    ]
    return changes[-1].rank if changes else ""


def retirement(character: Character) -> Discipline | None:
    return next((r for r in character.discipline if r.kind == RETIRED), None)


def widow_pensioned(character: Character) -> bool:
    return any(r.kind == WIDOW_PENSION for r in character.discipline)


def rewards_held(character: Character) -> list[Discipline]:
    """The improved equipment he has been given, which a demotion takes
    back."""
    return [r for r in character.discipline if r.kind == IMPROVED_EQUIPMENT]


def _wage_share(
    saga: Saga, covenant: Covenant, character: Character, multiplier: float
) -> float:
    """His share of the covenant's Wages a year: his Points of Inhabitants
    x 2 / 10 x the salary multiplier, on each list he is on."""
    points = 0
    for kind in covenfolk.INHABITANT_POINTS:
        for entry in covenfolk.entries_for_kind(saga, covenant, kind):
            if entry.character is character:
                points += covenfolk.kind_points(kind, covenant)
    return points * 2 / 10 * multiplier


def wage_adjustment(saga: Saga, covenant: Covenant, multiplier: float) -> float:
    """What the covenfolk's rewards and retirements change the year's
    Wages by, in pounds: half his share again for each season of Pay and a
    Half this year, a pensioner's share halved (his pension is half his
    Wages), a retiree who pays rent instead drawing none."""
    year = saga.current_year
    total = 0.0
    for character in saga.characters:
        if character.covenant_id != covenant.id or not character.discipline:
            continue
        share = _wage_share(saga, covenant, character, multiplier)
        if not share:
            continue
        for record in character.discipline:
            if record.kind == PAY_AND_A_HALF:
                total += share / 2 * covered(character, record, year) / len(SEASONS)
        retired = retirement(character)
        if retired is not None and season_order(
            season=retired.season, year=retired.year
        ) < season_order(season="Spring", year=year + 1):
            total -= share if retired.note == RENT else share / 2
    return total


PENSION = "pension"
RENT = "rent"
RETIREMENT_TERMS: tuple[tuple[str, str], ...] = (
    ("A pension (half his Wages)", PENSION),
    ("Rent instead (fed free)", RENT),
)
