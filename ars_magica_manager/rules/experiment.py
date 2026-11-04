"""Arcane experimentation and Arcane Discovery.

Experimentation, with any lab work that allows it (inventing a spell,
enchanting, a familiar, a Longevity Ritual, investigating an item):

- The Lab Total adds a simple die + the risk modifier (0 to +3).
- Each season rolls a stress die + risk on the Extraordinary Results chart,
  with 1 + risk + aura botch dice: Disaster (by zeroes: Warping Points, the
  season wasted, the creation destroyed, the lab Damaged, then Wrecked),
  0-4 nothing, 5-6 a side effect, 7 no benefit (the die and risk are lost),
  8 complete failure (the season wasted), 9 a special or story event, 10 a
  Discovery (xp), 11 a modified effect, 12+ two more rolls.

Arcane Discovery (original research in Houses of Hermes; a magus's breakthrough goals, Minor ~30, Major ~45,
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

import random
from dataclasses import dataclass, field
from typing import Any

from ..models import Breakthrough, Character, ExperimentalEffect, Saga, SeasonPlan
from . import dice, scores
from . import xp as xp_rules
from .rounding import round_up

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Experimentation, pp. 274-276"
)
LAB_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Laboratory "
    "Personalization Rules, Safety and Warping (pp. 288-289)"
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
    #: No Benefit left the Lab Total too low for the work: the project is
    #: abandoned (its progress lost), and the season with it.
    abandoned: bool = False
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
    effects: list[ExperimentalEffect] = field(default_factory=list)
    #: Each effect's sub-table results to choose from: two with two dice
    #: (Exciting Experimentation, Creative Block), the first standing until
    #: the storyguide chooses.
    effect_options: list[list[str]] = field(default_factory=list)
    #: Each roll on the Discovery table, as the candidates rolled (two with
    #: two dice); `xp` holds what the first of each gives.
    discoveries: list[list[int]] = field(default_factory=list)
    #: Investigating an item: the id of the power each effect falls on
    #: (the storyguide's choice).
    targets: list[str] = field(default_factory=list)
    #: Special results or story events (9), each the storyguide's choice.
    specials: int = 0
    #: The Art the experience of a Discovery goes to unless chosen
    #: otherwise.
    art: str = ""
    #: What the storyguide made of the special results: story events (a
    #: line each, for the Diaries), the extra vis the work needs ({Art:
    #: pawns}), and the spells the magus also creates (each a spell form's
    #: values, made when the season is applied).
    stories: list[str] = field(default_factory=list)
    extra_vis: dict[str, int] = field(default_factory=dict)
    bonus_spells: list[dict[str, Any]] = field(default_factory=list)
    #: A Disaster of 5+: "covenant" (a story threatens it) or "lab" (the
    #: laboratory destroyed, the default).
    disaster_choice: str = ""
    #: Investigating an item, a result that destroys it (a Disaster of two
    #: zeroes or more, or a Complete Failure's 0) or changes it (a side or
    #: modified effect): `item_at_risk`; and `protected` when one of its
    #: effects protects it with a level above the Lab Total (the
    #: storyguide's word), so it survives and resists the harmful effects.
    item_at_risk: bool = False
    protected: bool = False
    #: With two dice on the chart (Exciting Experimentation, Creative
    #: Block), the other roll, whole, for the storyguide to choose.
    other: Extraordinary | None = None
    #: No experiment: only what an unsafe or Warping laboratory did to the
    #: season's work (lab_hazards).
    lab_only: bool = False

    @property
    def second(self) -> list[str]:
        """The other roll's results (none without two dice)."""
        return self.other.results if self.other is not None else []

    @property
    def choices(self) -> bool:
        """Whether anything in it waits on the storyguide: which roll
        stands, a sub-table's two dice, an effect to describe or apply, a
        Discovery's subject, a special result, a Disaster of 5+, or a move
        onto a Discovery."""
        return bool(
            self.other is not None
            or self.effects
            or self.discoveries
            or self.specials
            or self.zeroes >= DISASTER_CHOICE
            or self.item_at_risk
            or self.discovery_shift is not None
        )


#: Rolls of 12+ ("roll twice more") followed in a row before the rest is
#: left to the storyguide, a bound the dice almost never reach.
MAX_DEPTH = 10

#: A Disaster with this many zeroes or more is the storyguide's choice:
#: a story threatening the covenant, or the laboratory destroyed.
DISASTER_CHOICE = 5


def botch_dice(
    character: Character | None, risk: int, aura: int, safety: int = 0
) -> int:
    """1 + risk + the lab's aura, with the Virtues and Flaws that change lab
    botch dice (Cautious Sorcerer takes 3 off, never below 1 by itself),
    then less the lab's Safety (a negative Safety adds dice)."""
    count = 1 + risk + max(0, aura)
    if character is not None:
        change, _ = scores.botch_dice_change(character.virtues_flaws, ("laboratory",))
        count = scores.with_botch_change(count, change)
    return max(0, count - safety)


def too_low(why: str) -> str:
    """The note on an experiment whose Lab Total is too low for its work:
    the season goes ahead, as experimenting is a gamble."""
    return (
        f"{why}, unless the experiment's die lifts it. Experimenting, the "
        "season goes ahead all the same: the Extraordinary Results chart is "
        "rolled, any vis paid is lost, and the work makes no progress."
    )


def two_dice(character: Character | None) -> bool:
    """Whether the experimenter rolls two dice on every experimentation
    table (Exciting Experimentation, Creative Block)."""
    return character is not None and any(
        vf.vf_id in TWO_DICE for vf in character.virtues_flaws
    )


def chart(
    rng: random.Random,
    risk: int,
    aura: int,
    art: str,
    saga: Saga | None = None,
    *,
    character: Character | None = None,
    seeking: bool = False,
    shift: int | None = None,
    stabilizing: bool = False,
    safety: int = 0,
) -> Extraordinary:
    """Roll the Extraordinary Results chart. Seeking a Discovery, a roll the
    risk modifier can move onto 10 records the move (`discovery_shift`) to
    be asked about, or, with `shift` given (the project's move so far),
    makes that same move. Stabilizing, the roll is moved by `shift` and
    read there. With two dice (Exciting Experimentation, Creative Block)
    the other roll is made the same way and kept whole (`other`), for the
    storyguide to choose. `aura` and `safety` are the lab's."""
    dice_count = botch_dice(character, risk, aura, safety)
    result = Extraordinary(art=art)
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
    if two_dice(character):
        other = Extraordinary(art=art)
        _roll_once(
            other,
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
        result.other = other
        result.results.append(
            "A second roll (Exciting Experimentation / Creative Block): "
            + " ".join(other.results)
            + " The storyguide chooses which stands."
        )
    return result


#: What the storyguide can make of a special result (9): the creation
#: needs more vis, the magus also creates a spell, the creation is changed
#: some other way, or a story event.
SPECIALS: tuple[tuple[str, str], ...] = (
    ("story", "A story event"),
    ("changed", "The creation is changed some other way"),
    ("vis", "The work needs more vis (magnitude + risk pawns)"),
    ("spell", "The magus also creates a spell"),
)


@dataclass
class EffectChoice:
    """The storyguide's word on one side or modified effect: which of two
    dice stands (`result`), what it is, any new Range, Duration or Target,
    the potency's change in steps, and, investigating an item, the power it
    falls on."""

    result: str = ""
    description: str = ""
    range: str = ""
    duration: str = ""
    target: str = ""
    potency: int = 0
    power: str = ""


@dataclass
class DiscoveryChoice:
    """One Discovery roll: which of two dice stands, and the Ability (for
    5-6) or the Art used (for 7-9) its experience goes to."""

    roll: int = 0
    ability: str = "Magic Theory"
    art: str = ""


@dataclass
class SpecialChoice:
    """What the storyguide makes of a special result (a key of SPECIALS),
    and its words (the story, or how the creation is changed)."""

    kind: str = "story"
    text: str = ""


@dataclass
class Settlement:
    """Everything the storyguide decides about one experiment's season,
    in the order the chart gave it: which of two rolls stands, then each
    effect, Discovery roll and special result of that roll, a Disaster of
    5+, and whether to move the roll onto a Discovery."""

    second: bool = False
    effects: list[EffectChoice] = field(default_factory=list)
    discoveries: list[DiscoveryChoice] = field(default_factory=list)
    specials: list[SpecialChoice] = field(default_factory=list)
    disaster: str = ""
    move: bool = False
    protected: bool = False


def destroys(result: Extraordinary) -> bool:
    """Whether the roll destroys the creation: a Disaster of two zeroes or
    more, or a Complete Failure whose simple die is 0."""
    return result.zeroes >= 2 or (result.failure and result.failure_die == 0)


def harmful(effect: ExperimentalEffect) -> bool:
    """Whether an experimental effect damages or changes its creation for
    the worse: all but a side benefit and an increased parameter."""
    return effect.result not in BENEFICIAL


def harms_item(result: Extraordinary) -> bool:
    """Whether the roll would destroy or change an item investigated (its
    protection may resist it): a destroying result or a side or modified
    effect."""
    return destroys(result) or bool(result.effects)


def settle(
    result: Extraordinary, settlement: Settlement, character: Character | None
) -> None:
    """Apply the storyguide's choices (but the choice of roll and the move,
    which the season's work answers) to the roll that stands: each effect
    as chosen, the Discoveries' experience recomputed, the special results
    turned into a changed creation or a story (the extra vis and the spell
    are the season's to settle), and a Disaster's choice."""
    for effect, choice, options in zip(
        result.effects, settlement.effects, result.effect_options, strict=False
    ):
        if choice.result in options:
            effect.result = choice.result
        effect.fatal = effect.result == FATAL_FLAW
        effect.description = choice.description.strip()
        effect.range, effect.duration, effect.target = (
            choice.range,
            choice.duration,
            choice.target,
        )
        effect.potency = choice.potency
    result.targets = [choice.power for choice in settlement.effects]
    if result.discoveries and settlement.discoveries:
        gains: list[tuple[str, int]] = []
        for candidates, choice in zip(
            result.discoveries, settlement.discoveries, strict=False
        ):
            roll = choice.roll if choice.roll in candidates else candidates[0]
            gain, _ = discovery_gain(
                roll, character, choice.art or result.art, choice.ability
            )
            gains.append(gain)
        result.xp = gains
    for special in settlement.specials[: result.specials]:
        words = special.text.strip()
        if special.kind == "changed":
            result.effects.append(
                ExperimentalEffect("special", "the creation changed", words)
            )
            result.effect_options.append(["the creation changed"])
        elif special.kind == "story":
            result.stories.append(words or "A story event (the storyguide's).")
    if result.zeroes >= DISASTER_CHOICE:
        result.disaster_choice = settlement.disaster or "lab"
    result.protected = result.item_at_risk and settlement.protected


def take_other(result: Extraordinary) -> Extraordinary:
    """The other roll of two dice, chosen by the storyguide to stand."""
    other = result.other
    assert other is not None
    other.results = [
        *other.results,
        "The storyguide chose this, the second roll, to stand.",
    ]
    return other


def _roll_once(
    result: Extraordinary,
    rng: random.Random,
    risk: int,
    dice_count: int,
    art: str,
    saga: Saga | None,
    seeking: bool,
    shift: int | None,
    *,
    stabilizing: bool = False,
    character: Character | None = None,
) -> None:
    die = dice.stress_die(rng, dice_count, saga=saga)
    result.die, result.botch_dice = die.value, dice_count
    if die.botched:
        _disaster(result, die.botches)
        return
    roll = die.value + risk
    if stabilizing:
        if shift:
            result.results.append(
                f"The roll {roll} moved by {shift:+d}, as when the Discovery was made."
            )
            roll += shift
            result.move = shift
        _apply(
            result,
            roll,
            rng,
            risk,
            art,
            saga,
            0,
            research=True,
            character=character,
            dice_count=dice_count,
        )
        return
    _apply(
        result,
        roll,
        rng,
        risk,
        art,
        saga,
        0,
        research=seeking,
        character=character,
        dice_count=dice_count,
    )
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


def _disaster(result: Extraordinary, zeroes: int) -> None:
    """A botch: by its zeroes, Warping for everyone in the lab and the
    season wasted, then the creation destroyed, the lab Damaged, an
    explosion that wrecks it, and at 5+ the storyguide's choice."""
    zeroes = max(zeroes, result.zeroes)
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
            "; the storyguide chooses a story threatening the covenant, or the "
            "lab destroyed and an Incapacitating Wound for everyone in it"
            if zeroes >= DISASTER_CHOICE
            else ""
        )
        + "."
    )
    if zeroes >= 4:
        result.lab_flaw = "labvf_wrecked"
    elif zeroes == 3:
        result.lab_flaw = "labvf_damaged"


def accident_dice(character: Character | None, safety: int) -> int:
    """An unsafe lab's botch dice for work that rolls none of its own: one
    per point of negative Safety, with the Virtues and Flaws that change lab
    botch dice, and always at least one."""
    count = max(0, -safety)
    if character is not None:
        change, _ = scores.botch_dice_change(character.virtues_flaws, ("laboratory",))
        count = scores.with_botch_change(count, change)
    return max(1, count)


def lab_hazards(
    rng: random.Random,
    character: Character | None,
    safety: int,
    warping: int,
    *,
    saga: Saga | None = None,
    botch_count: int | None = None,
) -> Extraordinary | None:
    """What an unsafe or a Warping laboratory does to a season's work, or
    None when nothing happens. With negative Safety a simple die at or
    under its size risks an accident: the season's botch dice
    (`botch_count`, an experiment's, else `accident_dice`), and any zero is
    a Disaster. With positive Warping a simple die at or under it warps the
    product: a side effect on an odd die, a modified effect on an even one
    (LAB_SOURCE)."""
    found = Extraordinary()
    if safety < 0 and dice.simple_die(rng) <= -safety:
        count = max(
            1, accident_dice(character, safety) if botch_count is None else botch_count
        )
        zeroes = dice.botch_roll(rng, count, saga=saga)
        found.botch_dice = count
        if zeroes:
            found.results.append(
                f"The laboratory is unsafe (Safety {safety:+d}): an accident."
            )
            _disaster(found, zeroes)
    if warping > 0:
        die = dice.simple_die(rng)
        if die <= warping:
            if die % 2:
                options = [SIDE_EFFECTS[dice.simple_die(rng)]]
                found.effects.append(
                    ExperimentalEffect(
                        "side", options[0], fatal=options[0] == FATAL_FLAW
                    )
                )
                what = "a side effect"
            else:
                options = [modified_result(dice.simple_die(rng))]
                found.effects.append(ExperimentalEffect("modified", options[0]))
                what = "a modified effect"
            found.effect_options.append(options)
            found.results.append(
                f"The laboratory's Warping ({warping:+d}) warps the work: {what} "
                f"({options[0]})."
            )
    return found if found.results else None


def add_hazards(chart: Extraordinary, hazards: Extraordinary) -> None:
    """A season's experiment takes what the laboratory did to it as well."""
    chart.results += hazards.results
    if hazards.zeroes:
        _disaster(chart, hazards.zeroes)
        chart.results.pop()
    chart.effects += hazards.effects
    chart.effect_options += hazards.effect_options


def needs_description(effect: ExperimentalEffect) -> bool:
    """Whether the storyguide has still to say what `effect` is: it has no
    words, and is a side effect, a special result's change, or a modified
    effect that changes nothing the app works out (Range, Duration, Target
    or potency)."""
    if effect.description.strip():
        return False
    if effect.kind != "modified":
        return True
    return not (effect.range or effect.duration or effect.target or effect.potency)


def describe(effect: ExperimentalEffect) -> str:
    """An experimental effect in a line (plain text): what the chart gave,
    what it is, what it changed, and a fatal flaw marked."""
    text = effect.label or "An experimental effect"
    if effect.fatal and effect.result != FATAL_FLAW:
        text += " (fatal flaw)"
    if effect.description.strip():
        text += f": {effect.description.strip()}"
    elif needs_description(effect):
        text += " (not yet described)"
    changes = [
        f"{label} {value}"
        for label, value in (
            ("Range", effect.range),
            ("Duration", effect.duration),
            ("Target", effect.target),
        )
        if value
    ]
    if effect.potency:
        steps = abs(effect.potency)
        changes.append(
            f"potency {'+' if effect.potency > 0 else '-'}{steps} step"
            + ("s" if steps > 1 else "")
        )
    if changes:
        text += f" [{', '.join(changes)}; level kept]"
    if effect.year:
        text += f" ({effect.season} {effect.year})"
    return text


def apply_changes(made: object, effects: list[ExperimentalEffect]) -> None:
    """A creation (a spell or an instilled effect) takes each effect's new
    Range, Duration or Target. Its level is never changed."""
    for effect in effects:
        for name in ("range", "duration", "target"):
            value = getattr(effect, name)
            if value and hasattr(made, name):
                setattr(made, name, value)


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


def _sub_dice(rng: random.Random, two: bool, risk: int = 0) -> list[int]:
    """A sub-table's roll: a simple die (+ the risk), or two of them."""
    return [dice.simple_die(rng) + risk for _ in range(2 if two else 1)]


def _or(options: list[str]) -> str:
    return ", or ".join(dict.fromkeys(options))


def modified_result(roll: int) -> str:
    """The Modified Effect sub-table's result for a simple die + risk."""
    return next(
        (text for top, text in MODIFIED if roll <= top),
        CHANGED_COMPLETELY,
    )


CHANGED_COMPLETELY = (
    "effect changed completely (same Technique and Form, similar level)"
)
#: The Modified Effect results that change a parameter or the potency,
#: and which way.
REDUCED, INCREASED = MODIFIED[0][1], MODIFIED[1][1]
FATAL_FLAW = SIDE_EFFECTS[10]
#: The effects that leave a creation better off.
BENEFICIAL = (SIDE_EFFECTS[6], SIDE_EFFECTS[9], INCREASED)


def _apply(
    result: Extraordinary,
    roll: int,
    rng: random.Random,
    risk: int,
    art: str,
    saga: Saga | None,
    depth: int,
    *,
    research: bool = False,
    character: Character | None = None,
    dice_count: int = 0,
) -> None:
    """The result of a chart roll. For Arcane Discovery (`research`), a
    Discovery is the research's and gives no experience. Two dice
    (Exciting Experimentation, Creative Block) roll each sub-table twice.
    The further rolls of a 12+ are stress dice with `dice_count` botch
    dice."""
    two = two_dice(character)
    if roll <= 4:
        result.results.append(f"{roll}: no extraordinary effects.")
    elif roll <= 6:
        options = [SIDE_EFFECTS[d] for d in _sub_dice(rng, two)]
        result.results.append(f"{roll}: a side effect ({_or(options)}).")
        result.effects.append(
            ExperimentalEffect("side", options[0], fatal=options[0] == FATAL_FLAW)
        )
        result.effect_options.append(options)
    elif roll == 7:
        result.no_benefit = True
        result.results.append(f"{roll}: no benefit (the die and risk are lost).")
    elif roll == 8:
        result.wasted = True
        result.failure = True
        result.failure_die = dice.simple_die(rng) % 10
        result.results.append(f"{roll}: complete failure (the season is wasted).")
    elif roll == 9:
        result.specials += 1
        result.results.append(f"{roll}: a special result or story event (storyguide).")
    elif roll == 10:
        result.discovery = True
        if research:
            result.results.append(
                f"{roll}: a Discovery toward the research (its experience table "
                "doesn't apply)."
            )
        else:
            whats = _discovery_xp(result, rng, risk, art, character, two=two)
            result.results.append(f"{roll}: a Discovery: {'; '.join(whats)}.")
    elif roll == 11:
        # One die for the whole table (it was rolled again for each row).
        options = [modified_result(r) for r in _sub_dice(rng, two, risk)]
        result.results.append(f"{roll}: a modified effect ({_or(options)}).")
        result.effects.append(ExperimentalEffect("modified", options[0]))
        result.effect_options.append(options)
    else:
        result.results.append(f"{roll}: roll twice more.")
        if depth >= MAX_DEPTH:
            result.results.append(
                f"(After {MAX_DEPTH} rolls of 12+ in a row, the storyguide rolls "
                "the rest.)"
            )
        else:
            for _ in range(2):
                die = dice.stress_die(rng, dice_count, saga=saga)
                if die.botched:
                    _disaster(result, die.botches)
                    continue
                _apply(
                    result,
                    die.value + risk,
                    rng,
                    risk,
                    art,
                    saga,
                    depth + 1,
                    research=research,
                    character=character,
                    dice_count=dice_count,
                )


#: What each Discovery roll gives: (the highest roll, the kind of gain).
DISCOVERY = (
    (4, "theory"),
    (6, "ability"),
    (8, "art"),
    (9, "next"),
)


def discovery_kind(roll: int) -> str:
    """ "theory" (15 xp in Magic Theory), "ability" (15 xp in an Ability
    related to the experiment), "art" (3 xp in an Art used) or "next"
    (an Art used to its next score)."""
    return next((kind for top, kind in DISCOVERY if roll <= top), "next")


def discovery_gain(
    roll: int, character: Character | None, art: str, ability: str = "Magic Theory"
) -> tuple[tuple[str, int], str]:
    """A Discovery roll's experience, (subject, xp), toward `art` (an Art
    used) or `ability` (for 5-6), and what it gave in words."""
    kind = discovery_kind(roll)
    if kind == "theory":
        return ("ability:Magic Theory", 15), "15 xp in Magic Theory"
    if kind == "ability":
        return (f"ability:{ability}", 15), f"15 xp in {ability}"
    if kind == "art":
        return (f"art:{art}", 3), f"3 xp in {art}"
    need = _to_next_score(character, art)
    return (f"art:{art}", need), f"{need} xp, to raise {art} to its next score"


def _discovery_xp(
    result: Extraordinary,
    rng: random.Random,
    risk: int,
    art: str,
    character: Character | None,
    rolls: int = 1,
    *,
    two: bool = False,
) -> list[str]:
    """The Discovery table (a simple die + the risk): each roll kept in
    `result.discoveries`, the first candidate's experience added to
    `result.xp`, and what each roll gave. 10+ rolls twice more, rolling
    again any 10+ among them."""
    whats: list[str] = []
    for _ in range(rolls):
        candidates = _sub_dice(rng, two, risk)
        if rolls > 1:
            kept = []
            for roll in candidates:
                tries = 0
                while roll >= 10 and tries < 20:
                    roll, tries = dice.simple_die(rng) + risk, tries + 1
                kept.append(min(roll, 9))
            candidates = kept
        roll = candidates[0]
        if roll >= 10:
            whats += _discovery_xp(result, rng, risk, art, character, rolls=2, two=two)
            continue
        result.discoveries.append(candidates)
        gain, what = discovery_gain(roll, character, art)
        result.xp.append(gain)
        if discovery_kind(roll) == "ability":
            what = "15 xp in an Ability related to it (Magic Theory unless chosen)"
        whats.append(
            what if len(candidates) == 1 else f"{what} (or roll {candidates[1]})"
        )
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


def insight_roll(
    character: Character,
    plan: SeasonPlan,
    rng: random.Random,
    theory: int,
    saga: Saga | None = None,
):
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
