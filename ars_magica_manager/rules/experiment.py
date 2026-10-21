"""Arcane experimentation and original research.

Experimentation, with any lab work that allows it (inventing a spell,
enchanting, a familiar, a Longevity Ritual, investigating an item):

- The Lab Total adds a simple die + the risk modifier (0 to +3).
- Each season rolls a stress die + risk on the Extraordinary Results chart,
  with 1 + risk + aura botch dice: Disaster (by zeroes: Warping Points, the
  season wasted, the creation destroyed, the lab Damaged, then Wrecked),
  0-4 nothing, 5-6 a side effect, 7 no benefit (the die and risk are lost),
  8 complete failure (the season wasted), 9 a special or story event, 10 a
  Discovery (xp), 11 a modified effect, 12+ two more rolls.

Original research (a magus's breakthrough goals, Minor ~30, Major ~45,
Hermetic ~60 points):

- Seeking a Discovery: experimenting on a goal, the risk goes on the chart
  only. A roll the risk can move onto 10 may be moved: the Discovery comes
  in addition to the roll's own result, unless that result wastes the
  season. The Discovery table's experience is ignored. Later seasons of the
  same project make the same move. Each spell or enchantment gives one
  Discovery at most.
- Stabilizing it: the same experiment again, its roll moved as before;
  unless the result is harmful (Disaster, No Benefit, Complete Failure),
  the effect's magnitude goes to the goal's points, and any beneficial
  result is ignored. A failure may be retried the next season. Every
  attempt Warps: magnitude - a simple die.
- Integrating an insight: stress die + Intelligence + Magic Theory (+3 for
  Inventive Genius) against 18, a season studying a source.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..models import Breakthrough, Character, SeasonPlan
from . import dice, scores
from . import xp as xp_rules
from .rounding import round_up

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Experimentation "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Eight:"
    "_Laboratory#Experimentation)"
)
RESEARCH_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Arcane Discovery "
    "(pp. 277-281); Houses of Hermes: True Lineages, Chapter One: House "
    "Bonisagus, Original Research"
)

STABILIZE = "stabilize_discovery"
INTEGRATE = "integrate_insight"
ACTIVITIES: tuple[str, ...] = (STABILIZE, INTEGRATE)
#: Breakthrough kinds and their typical point targets.
KINDS: dict[str, int] = {"Minor": 30, "Major": 45, "Hermetic": 60}
INSIGHT_EASE = 18
MAX_RISK = 3

SIDE_EFFECTS = {
    1: "sigil greatly exaggerated",
    2: "minor flaw",
    3: "minor flaw",
    4: "minor side effect",
    5: "minor side effect",
    6: "minor side benefit",
    7: "major flaw",
    8: "major side effect",
    9: "major side benefit",
    10: "fatal flaw",
}
#: The Modified Effect sub-table (an Extraordinary Result of 11): one simple
#: die + the risk modifier, read against each row's top; past the last, the
#: effect is changed completely (SOURCE, Extraordinary Results Chart).
MODIFIED = (
    (3, "reduced range, duration, target or potency"),
    (6, "increased range, duration, target or potency"),
    (8, "use restricted (fails in some circumstance)"),
    (10, "actual effect modified"),
)


def max_risk(magic_theory: int) -> int:
    """At most +1 (Magic Theory 1-5), +2 (6-10), +3 (11+)."""
    return max(0, min(MAX_RISK, round_up(magic_theory / 5)))


#: Virtues and Flaws that change experimentation.
CAUTIOUS = "vf_cautious_sorcerer"
TWO_DICE = ("vf_exciting_experimentation", "vf_creative_block")
PRONE = "vf_prone_to_chance"
AVERSE = "vf_averse_to_risk"
INVENTIVE = "vf_inventive_genius"
INVENTIVE_INSIGHT = 3


@dataclass
class Extraordinary:
    """What a season's roll on the Extraordinary Results chart does."""

    results: list[str] = field(default_factory=list)
    #: The stress die (0 when it botched), the botch dice a 0 rolls, and the
    #: move made to the roll (0: none), for the Research log.
    die: int = 0
    botch_dice: int = 0
    move: int = 0
    #: The season's work is lost (Disaster, Complete Failure).
    wasted: bool = False
    #: The experimentation bonus is lost (No Benefit).
    no_benefit: bool = False
    #: A Complete Failure (for a familiar or an item, a simple die of 0
    #: destroys it: `failure_die`).
    failure: bool = False
    failure_die: int = 1
    #: Disaster: zeroes on the botch dice.
    zeroes: int = 0
    #: A Discovery (10), and its xp: (subject, xp).
    discovery: bool = False
    xp: list[tuple[str, int]] = field(default_factory=list)
    #: Seeking a Discovery: the move of the roll (up to the risk) that would
    #: land on 10 (None: none in reach). Asked before it counts.
    discovery_shift: int | None = None
    #: The lab Flaw a Disaster gives ("labvf_damaged"/"labvf_wrecked").
    lab_flaw: str = ""
    #: Side effects and modified effects the creation keeps ("warts and
    #: all").
    effects: list[str] = field(default_factory=list)
    #: A second roll's results (Exciting Experimentation, Creative Block),
    #: for the storyguide to choose.
    second: list[str] = field(default_factory=list)


def botch_dice(character: Character, risk: int, aura: int) -> int:
    """1 + risk + the aura, with the Virtues and Flaws that change lab botch
    dice (Cautious Sorcerer takes 3 off, never below 1)."""
    change, _ = scores.botch_dice_change(character.virtues_flaws, ("laboratory",))
    return scores.with_botch_change(1 + risk + max(0, aura), change)


def chart(
    rng,
    risk: int,
    aura: int,
    art: str,
    saga=None,
    *,
    character: Character | None = None,
    seeking: bool = False,
    shift: int | None = None,
    stabilizing: bool = False,
    depth: int = 0,
) -> Extraordinary:
    """Roll the Extraordinary Results chart. Seeking a Discovery, a roll the
    risk modifier can move onto 10 records the move (`discovery_shift`) to
    be asked about, or, with `shift` given (the project's move so far),
    makes that same move. Stabilizing, the roll is moved by `shift` and
    read there."""
    result = Extraordinary()
    dice_count = botch_dice(character, risk, aura) if character else 1 + risk + aura
    _roll_once(
        result,
        rng,
        risk,
        dice_count,
        art,
        saga,
        seeking,
        shift,
        stabilizing=stabilizing,
        character=character,
    )
    if character is not None and any(
        vf.vf_id in TWO_DICE for vf in character.virtues_flaws
    ):
        other = Extraordinary()
        _roll_once(other, rng, risk, dice_count, art, saga, False, None)
        result.second = other.results
        result.results.append(
            "A second roll (Exciting Experimentation / Creative Block): "
            + " ".join(other.results)
            + " The storyguide may use it instead."
        )
    return result


def _roll_once(
    result,
    rng,
    risk,
    dice_count,
    art,
    saga,
    seeking,
    shift,
    *,
    stabilizing: bool = False,
    character: Character | None = None,
) -> None:
    die = dice.stress_die(rng, dice_count, saga=saga)
    result.die, result.botch_dice = die.value, dice_count
    if die.botched:
        zeroes = die.botches
        result.zeroes = zeroes
        result.wasted = True
        result.results.append(
            f"Disaster ({zeroes} zero(es)): {zeroes} Warping Point(s), the season "
            "wasted"
            + ("; the creation destroyed" if zeroes >= 2 else "")
            + ("; the lab is Damaged" if zeroes == 3 else "")
            + (
                "; an explosion wrecks the lab (two Heavy Wounds each)"
                if zeroes >= 4
                else ""
            )
            + (
                "; the lab is destroyed and everyone in it takes an Incapacitating "
                "Wound (the storyguide may choose a covenant disaster instead)"
                if zeroes >= 5
                else ""
            )
            + "."
        )
        if zeroes >= 4:
            result.lab_flaw = "labvf_wrecked"
        elif zeroes == 3:
            result.lab_flaw = "labvf_damaged"
        return
    roll = die.value + risk
    if stabilizing:
        if shift:
            result.results.append(
                f"The roll {roll} moved by {shift:+d}, as when the Discovery was made."
            )
            roll += shift
            result.move = shift
        _apply(result, roll, rng, risk, art, saga, 0, research=True)
        return
    _apply(result, roll, rng, risk, art, saga, 0, research=seeking, character=character)
    if not seeking or result.discovery or result.wasted:
        return
    if shift is not None:
        if roll + shift == 10:
            result.discovery = True
            result.move = shift
            result.results.append(
                f"The roll {roll} moved by {shift:+d}, as before: a Discovery as well."
            )
    elif abs(roll - 10) <= risk:
        result.discovery_shift = 10 - roll


def move_to_discovery(result: Extraordinary) -> None:
    """The magus takes the move onto 10 (`discovery_shift`): a Discovery, in
    addition to the roll's own result."""
    shift = result.discovery_shift
    result.discovery_shift = None
    if shift is None or result.wasted:
        return
    result.discovery = True
    result.move = shift
    result.results.append(
        f"The roll moved {shift:+d} onto 10: a Discovery as well (the roll's own "
        "result stands)."
    )


def _apply(
    result: Extraordinary,
    roll: int,
    rng,
    risk,
    art,
    saga,
    depth,
    *,
    research: bool = False,
    character: Character | None = None,
) -> None:
    """The result of a chart roll. For original research (`research`), a
    Discovery is the research's and gives no experience."""
    if roll <= 4:
        result.results.append(f"{roll}: no extraordinary effects.")
    elif roll <= 6:
        side = SIDE_EFFECTS[dice.simple_die(rng)]
        result.results.append(f"{roll}: a side effect ({side}).")
        result.effects.append(f"Side effect: {side}")
    elif roll == 7:
        result.no_benefit = True
        result.results.append(f"{roll}: no benefit (the die and risk are lost).")
    elif roll == 8:
        result.wasted = True
        result.failure = True
        result.failure_die = dice.simple_die(rng) % 10
        result.results.append(f"{roll}: complete failure (the season is wasted).")
    elif roll == 9:
        result.results.append(f"{roll}: a special result or story event (storyguide).")
    elif roll == 10:
        result.discovery = True
        if research:
            result.results.append(
                f"{roll}: a Discovery toward the research (its experience table "
                "doesn't apply)."
            )
        else:
            whats = _discovery_xp(result, rng, risk, art, character)
            result.results.append(f"{roll}: a Discovery: {'; '.join(whats)}.")
    elif roll == 11:
        # One die for the whole table (it was rolled again for each row).
        modified_roll = dice.simple_die(rng) + risk
        modified = next(
            (text for top, text in MODIFIED if modified_roll <= top),
            "effect changed completely (same Technique and Form, similar level)",
        )
        result.results.append(f"{roll}: a modified effect ({modified}).")
        result.effects.append(f"Modified effect: {modified}")
    else:
        result.results.append(f"{roll}: roll twice more.")
        if depth < 3:
            for _ in range(2):
                more = dice.stress_die(rng, 0, saga=saga).value + risk
                _apply(
                    result,
                    more,
                    rng,
                    risk,
                    art,
                    saga,
                    depth + 1,
                    research=research,
                    character=character,
                )


def _discovery_xp(
    result: Extraordinary, rng, risk: int, art: str, character, rolls: int = 1
) -> list[str]:
    """The Discovery table (a simple die + the risk): its experience added to
    `result.xp`, and what each roll gave. 10+ rolls twice more, rolling again
    any 10+ among them."""
    whats: list[str] = []
    for _ in range(rolls):
        roll = dice.simple_die(rng) + risk
        if rolls > 1:
            tries = 0
            while roll >= 10 and tries < 20:
                roll, tries = dice.simple_die(rng) + risk, tries + 1
            roll = min(roll, 9)
        if roll <= 4:
            result.xp.append(("ability:Magic Theory", 15))
            whats.append("15 xp in Magic Theory")
        elif roll <= 6:
            result.xp.append(("ability:Magic Theory", 15))
            whats.append(
                "15 xp in an Ability related to it (Magic Theory here; change it)"
            )
        elif roll <= 8:
            result.xp.append((f"art:{art}", 3))
            whats.append(f"3 xp in {art}")
        elif roll == 9:
            need = _to_next_score(character, art)
            result.xp.append((f"art:{art}", need))
            whats.append(f"{need} xp, to raise {art} to its next score")
        else:
            whats += _discovery_xp(result, rng, risk, art, character, rolls=2)
    return whats


def _to_next_score(character: Character | None, art: str) -> int:
    """The xp that brings `art` to its next score, at least 3."""
    if character is None:
        return 3
    held = character.arts.get(art.lower())
    xp = held.xp if held is not None else 0
    score = xp_rules.score_from_xp(xp, xp_rules.ART_FACTOR)
    return max(3, xp_rules.art_xp(score + 1) - xp)


def find_goal(character: Character, name: str) -> Breakthrough | None:
    return next(
        (b for b in character.breakthroughs if b.name.lower() == name.strip().lower()),
        None,
    )


def goal(character: Character, name: str, kind: str = "Minor") -> Breakthrough:
    """The magus's research goal called `name`, made if new."""
    found = next(
        (b for b in character.breakthroughs if b.name.lower() == name.strip().lower()),
        None,
    )
    if found is None:
        found = Breakthrough(
            name=name.strip(), kind=kind, target=KINDS.get(kind, KINDS["Minor"])
        )
        character.breakthroughs.append(found)
    return found


def insight_roll(character: Character, plan: SeasonPlan, rng, theory: int, saga=None):
    """Integrating: stress die + Intelligence + Magic Theory vs 18, +3 for
    Inventive Genius."""
    if plan.die is not None:
        value, botched = plan.die, plan.die == 0
    else:
        die = dice.stress_die(rng, 1, saga=saga)
        value, botched = die.value, die.botched
    genius = (
        INVENTIVE_INSIGHT
        if any(vf.vf_id == INVENTIVE for vf in character.virtues_flaws)
        else 0
    )
    total = character.characteristics.intelligence + theory + value + genius
    if botched:
        return False, "Botch: a false insight (it seems real until tried)."
    if total >= INSIGHT_EASE:
        return True, f"{total} against {INSIGHT_EASE}: an insight."
    return False, f"{total} against {INSIGHT_EASE}: nothing this season."
