"""Mystery initiation.

    Initiation Total = Mystagogue's Presence + (Mystery Cult) Lore
                       + Script bonus (the sum of its components)

No die: the Initiation succeeds when the total at least equals the Target
Level: a Minor Virtue 15, a Major 21, or 18 / 30 when the Mystagogue lacks
the Virtue (DE pp. 387-388). An Ordeal suffered in an earlier Initiation
lowers the Target of the next three, by 3/2/1 (Minor), 6/4/2 (Medium) or
9/6/3 (Major); only the best one counts, never below 9, and it doesn't help
the Initiation it was suffered in.

Varying a Script (DE pp. 388-389): the Mystagogue may make one change in an
Initiation, a stress die + Intelligence + the Lore against 9 to add a
component or 12 to change one (The Mysteries Revised Edition p. 17 adds 15
to remove one). If the test fails, the Initiation fails; the Script as it
was may be tried another season. A Script that overlaps one the Initiate
already followed (its Quests done, its Ordeals suffered) must be changed:
a component changed at 12, or replaced by a different one at 15 (Legends
of Hermes pp. 50-51).

Only an Initiation that gives its Virtue spends a step of each past
Ordeal's reduction: "the next three Initiations" are the next three
Virtues initiated (DE p. 388).

An experimental Script (The Mysteries Revised Edition p. 18), when there
is none or it falls short: the Mystagogue proposes the rite's components
and a risk of 0 to +3. The Initiate carries the rite out (its Ordeals
are suffered whatever happens), then

1. a stress die + risk on the Extraordinary Results chart (DE p. 275):
   side effects become the Script's Personality Traits, a major flaw an
   extra Ordeal Flaw with no bonus, a fatal flaw an Ordeal with no
   Virtue, a major benefit a stronger Virtue or a second Minor one, a
   Discovery experience for the Mystagogue, a modified effect another
   Virtue, Disaster a failure and a Major Flaw for both;
2. the rite's validity: simple die + risk + Intelligence + Lore against 9
   + the proposed bonus (15 + it when the Initiate is another): a failure
   gives no Virtue;
3. the storyguide's sympathy bonus joins the Script, and the Initiation
   Total adds the risk too (the Script written down afterwards doesn't).

UnGifted Initiates (Hedge Magic Revised Edition p. 14): the Initiation
must include an Ordeal, past Ordeals don't lower its Target, and an
unGifted Mystagogue must know the power, so can't Initiate himself.

A hedge tradition's Script (Hedge Magic Revised Edition p. 13) has its
own Ease Factor, the Target for a Mystagogue who knows the power; one
who doesn't adds 3 for a Minor Virtue, 9 for a Major.
"""

from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass, field

from ..models import Character, Saga
from . import dice
from .apprentice_seasons import gifted
from .breakdown import Breakdown, Line
from .experiment import SIDE_EFFECTS
from .lab import ability_score

SOURCE = (
    "Ars Magica Definitive Edition, Mystery Initiation, pp. 387-389; The "
    "Mysteries Revised Edition, Varying a Script, p. 17"
)
EXPERIMENT_SOURCE = "The Mysteries Revised Edition, Experimental Scripts, p. 18"
OVERLAP_SOURCE = "Legends of Hermes, Multiple or Overlapping Scripts, pp. 50-51"
HEDGE_SOURCE = (
    "Hedge Magic Revised Edition, Initiations p. 13, UnGifted Initiations p. 14"
)

#: (tier, Mystagogue has the Virtue) -> Target Level.
TARGET_LEVELS: dict[tuple[str, bool], int] = {
    ("Minor", True): 15,
    ("Minor", False): 18,
    ("Major", True): 21,
    ("Major", False): 30,
}
MINIMUM_TARGET = 9
#: Mysteries with a rule of their own about who may be Initiated (rules.
#: supplement_work): Secret Name fails with a talisman or a familiar (DE p.
#: 235); Faerie Magic needs one touched by the fay (DE p. 236).
SECRET_NAME = "vf_secret_name"
FAERIE_MAGIC = "vf_faerie_magic"
ADD, CHANGE, REMOVE, REPLACE = "add", "change", "remove", "replace"
#: Varying a Script: the Ease Factor of each kind of change (replacing a
#: component by a different one, for an overlapping Script, is Legends of
#: Hermes p. 51's).
VARY_EASE: dict[str, int] = {ADD: 9, CHANGE: 12, REMOVE: 15, REPLACE: 15}
VARY_LABELS: dict[str, str] = {
    ADD: "Add a component (9)",
    CHANGE: "Change a component (12)",
    REMOVE: "Remove a component (15)",
    REPLACE: "Replace a component (15)",
}
#: A hedge Mystagogue who doesn't know the power: the Script's Ease Factor
#: rises by this, by the Virtue's tier (Hedge Magic Revised Edition p. 13).
UNKNOWN_POWER: dict[str, int] = {"Minor": 3, "Major": 9}
#: An experimental Script: the most risk, and the validity roll's Ease
#: Factor before the proposed bonus, on oneself and on another Initiate.
MAX_SCRIPT_RISK = 3
VALIDITY_SELF, VALIDITY_OTHER = 9, 15

#: Ordeal size -> the Target reduction for the 1st, 2nd and 3rd later
#: Initiation (the Definitive Edition's table).
ORDEAL_REDUCTIONS: dict[str, tuple[int, int, int]] = {
    "Minor": (3, 2, 1),
    "Medium": (6, 4, 2),
    "Major": (9, 6, 3),
}


@dataclass(frozen=True)
class Component:
    """A Script component: its bonus, and whether a Script may hold it only
    once."""

    name: str
    bonus: int
    once: bool = False


#: The Definitive Edition's example components (the sacrifice of something
#: of great symbolic value is +3 to +6, chosen per Script).
COMPONENTS: tuple[Component, ...] = (
    Component("Special place at a special time", 3),
    Component("Specific Quest", 3),
    Component("Sacrifice of time serving the cult", 1, once=True),
    Component("Sacrifice of material goods", 1),
    Component("Minor Ordeal", 3),
    Component("Medium Ordeal", 6),
    Component("Major Ordeal", 9),
)


def target_level(
    tier: str,
    mystagogue_has_virtue: bool,
    past_ordeals: Sequence[tuple[str, int]] = (),
) -> Breakdown:
    """The Target Level, less the best reduction from past Ordeals, each
    given as (size, how many Initiations ago: 1 for the next one)."""
    base = TARGET_LEVELS[tier, mystagogue_has_virtue]
    lines = [Line(f"{tier} Virtue", amount=base, source=SOURCE)]
    best = 0
    for size, since in past_ordeals:
        if 1 <= since <= 3:
            best = max(best, ORDEAL_REDUCTIONS[size][since - 1])
    if best:
        lines.append(Line("Past Ordeal", amount=-best, source=SOURCE))
    return Breakdown(total=max(MINIMUM_TARGET, base - best), lines=lines)


def script_bonus(components: Sequence[Component]) -> int:
    """A Script's bonus: the sum of its components. A once-only component
    held twice makes the Script invalid (ValueError)."""
    for component in components:
        if component.once and components.count(component) > 1:
            raise ValueError(f"A Script may include {component.name!r} only once.")
    return sum(component.bonus for component in components)


def initiation_total(
    mystagogue: Character, lore: str, components: Sequence[Component]
) -> Breakdown:
    lines = [
        Line("Presence", amount=mystagogue.characteristics.presence, source=SOURCE),
        Line(lore, amount=sum(ability_score(mystagogue, lore)), source=SOURCE),
    ]
    lines += [Line(c.name, amount=c.bonus, source=SOURCE) for c in components]
    script_bonus(components)  # validates
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def succeeds(total: int, target: int) -> bool:
    return total >= target


# ---------------------------------------------------------------------------
# UnGifted Initiates and hedge Scripts


def ordeals_count(initiate: Character) -> bool:
    """Whether the Initiate's past Ordeals lower an Initiation's Target: an
    unGifted Initiate's never do (HEDGE_SOURCE)."""
    return gifted(initiate)


def ungifted_problem(
    initiate: Character, mystagogue: Character, knows: bool, has_ordeal: bool
) -> str:
    """What the unGifted rules forbid ("" if nothing): an unGifted
    Initiate's Initiation needs an Ordeal, and an unGifted Mystagogue must
    know the power, so can't Initiate himself."""
    if not gifted(initiate) and not has_ordeal:
        return (
            f"{initiate.name} is unGifted: the Initiation must include an Ordeal "
            "(Hedge Magic Revised Edition p. 14)."
        )
    if not gifted(mystagogue) and not knows:
        who = (
            f"{mystagogue.name} can't Initiate himself"
            if mystagogue is initiate
            else f"{mystagogue.name} can't be the Mystagogue"
        )
        return (
            f"{who}: an unGifted Mystagogue must know the power "
            "(Hedge Magic Revised Edition p. 14)."
        )
    return ""


def script_tier(ease_factor: int, gains: str = "") -> str:
    """The tier of the power a hedge Script gives, when no Virtue names it:
    "(Major)" in what it gains, or an Ease Factor of 21 or more (a Major
    Virtue's known Target)."""
    if "(Major)" in gains:
        return "Major"
    if "(Minor)" in gains:
        return "Minor"
    return "Major" if ease_factor >= TARGET_LEVELS["Major", True] else "Minor"


def hedge_target(
    ease_factor: int, tier: str, knows: bool, reduction: int = 0
) -> Breakdown:
    """A hedge Script's Target: its Ease Factor, + 3 / + 9 when the
    Mystagogue doesn't know the power, less a past Ordeal's reduction
    (which never takes it below 9, nor a lower Ease Factor below itself)."""
    lines = [Line("Script's Ease Factor", amount=ease_factor, source=HEDGE_SOURCE)]
    base = ease_factor
    if not knows:
        raised = UNKNOWN_POWER.get(tier, UNKNOWN_POWER["Minor"])
        lines.append(
            Line(
                f"Mystagogue doesn't know the power ({tier})",
                amount=raised,
                source=HEDGE_SOURCE,
            )
        )
        base += raised
    total = base
    if reduction:
        total = max(min(base, MINIMUM_TARGET), base - reduction)
        lines.append(Line("Past Ordeal", amount=total - base, source=SOURCE))
    return Breakdown(total=total, lines=lines)


# ---------------------------------------------------------------------------
# Experimental Scripts


def validity_ease(proposed_bonus: int, on_self: bool) -> int:
    """The validity roll's Ease Factor: 9 + the proposed bonus, 15 + it
    when experimenting on another Initiate."""
    return (VALIDITY_SELF if on_self else VALIDITY_OTHER) + proposed_bonus


@dataclass
class ExperimentalRite:
    """What the Extraordinary Results chart made of an experimental rite:
    its notes, whether the Virtue is lost (the Ordeal still suffered), and
    whether the risk still counts in the Initiation Total."""

    notes: list[str] = field(default_factory=list)
    no_virtue: bool = False
    risk_counts: bool = True


#: Rolls of 12+ followed in a row before the rest is left to the storyguide.
_MAX_ROLLS = 10


def experimental_rite(
    rng: random.Random, risk: int, saga: Saga | None = None
) -> ExperimentalRite:
    """Roll a stress die + risk on the Extraordinary Results chart (1 +
    risk botch dice: there is no laboratory or aura), read for an
    Initiation rite (EXPERIMENT_SOURCE)."""
    rite = ExperimentalRite()
    pending, rolls = 1, 0
    while pending and rolls < _MAX_ROLLS:
        pending -= 1
        rolls += 1
        die = dice.stress_die(rng, 1 + risk, saga=saga)
        if die.botched:
            rite.no_virtue = True
            rite.notes.append(
                "Extraordinary Results: Disaster. The Initiation fails, and the "
                "Mystagogue and the Initiate each gain a Major Flaw (the "
                "troupe's choice; add them by hand)."
            )
            continue
        roll = die.value + risk
        if roll >= 12:
            rite.notes.append(f"Extraordinary Results {roll}: roll twice more.")
            pending += 2
            continue
        _read_rite(rite, roll, rng, risk)
    if pending:
        rite.notes.append("More rolls are due: the storyguide decides the rest.")
    return rite


def _read_rite(
    rite: ExperimentalRite, roll: int, rng: random.Random, risk: int
) -> None:
    said = f"Extraordinary Results {roll}: "
    if roll <= 4:
        rite.notes.append(said + "no extraordinary effects.")
    elif roll <= 6:
        side = min(10, dice.simple_die(rng) + risk)
        effect = SIDE_EFFECTS[side]
        if side == 10:
            rite.no_virtue = True
            rite.notes.append(
                said + "a fatal flaw: the Ordeal is suffered but the Virtue "
                "isn't gained."
            )
        elif side == 7:
            rite.notes.append(
                said + "a major flaw: an extra Ordeal Flaw (usually Minor) joins "
                "the Script, with no bonus (add it by hand)."
            )
        elif side == 9:
            rite.notes.append(
                said + "a major benefit: the Virtue is stronger, or a second "
                "Minor Virtue is gained, as part of the Script (add it by hand)."
            )
        else:
            rite.notes.append(
                said + f"a side effect ({effect}): a Personality Trait tied to "
                "the cult's goals joins the Script (add it by hand)."
            )
    elif roll == 7:
        rite.risk_counts = False
        rite.notes.append(said + "no benefit: the risk isn't added to the total.")
    elif roll == 8:
        rite.no_virtue = True
        rite.notes.append(
            said + "complete failure: no Virtue; the Ordeal is still suffered."
        )
    elif roll == 9:
        rite.notes.append(said + "a special or story event (the storyguide's).")
    elif roll == 10:
        rite.notes.append(
            said + "a Discovery: the Mystagogue gains experience in the Lore or "
            "the Ability initiated (the storyguide's amount; add it by hand)."
        )
    else:
        rite.notes.append(
            said + "a modified effect: a different Virtue, related to the "
            "cult's goals, is initiated (change it by hand)."
        )
