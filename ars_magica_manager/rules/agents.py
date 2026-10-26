"""Agents: the people a character controls through personal bonds (Lords
of Men, Control Through Emotional Bonds, pp. 22-25).

- He may keep 2 x (Presence + Intrigue or Leadership - the Gift's social
  penalty) agents, at least 1. Magi, characters with no political role,
  an agent's own people, hirelings and other players' characters don't
  count (p. 22).
- A potential agent's resistance comes from the Agent Recruitment Table
  (p. 23): his Social Status (3 a Major Social Virtue, 1 a Minor, 0 a Free
  one, -1 a Minor Social Flaw, -3 a Major), less 3 or 1 for a Major or
  Minor Flaw that would trouble the principal and 6 for a Flaw the
  principal uses to dominate him, plus each resource he will use in the
  principal's service (+1 or +3 for a high Ability, a Virtue, underlings
  or a useful Flaw; +9 if he serves a rival), +6 for more than three
  resources and +9 for more than six. It is never below 1.
- He is first impressed: a stress die + Presence + Leadership - the Gift's
  penalty against 6 (p. 24); a failure waits for another story. Then each
  point of Adventure experience the principal earns is also a point of
  Agency experience, and his resistance drops by 1 for as many Agency
  points as it now stands at. At 0 he is an agent, with a Bond of 0.
- A Bond rises as an Ability does (5 x the new score), from
  Agency experience in stories that aid the agent, or 5 points a pound for
  an agent not already prosperous (p. 25).
- A task needs the resources, and a Bond of +1: a stress die +
  Communication + Charm, Intrigue or Leadership + Bond - the Gift's penalty
  against the task's Ease Factor (3, 6 or 9) raised for haste (+1 within
  days, +3 within a day) and risk (+1, +3 or +6; 1, 3 or 5 botch dice).
  Passive news needs no roll (p. 24). Once he takes it on, the player
  rolls with the agent's own Characteristics and Abilities against the
  task's Ease Factor: an Easy task's is 6 or less, a Hard one's 12 or
  less, an Impressive one's 18 or less (p. 24). A Minor Flaw that takes his time
  makes him unavailable a quarter of the time, a Major one half (p. 25).
- Social Contacts, Mercenary Captain, Close Family Ties or Landed Noble
  give 12 points of agents at character creation, each costing at least 1
  and with a Bond of +1 or more (p. 23).
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Agent, Character
from . import scores
from .supplement_work import gift_penalty

SOURCE = "Lords of Men, Control Through Emotional Bonds, Agents, pp. 22-25"

#: Resistance by the potential agent's Social Status (p. 23).
STATUS_RESISTANCE: dict[str, tuple[str, int]] = {
    "major_virtue": ("Major Social Virtue (Landed Noble, Redcap...)", 3),
    "minor_virtue": ("Minor Social Virtue (Knight, Priest, Clerk...)", 1),
    "free": ("Free Social Virtue (Craftsman, Merchant, Peasant...)", 0),
    "minor_flaw": ("Minor Social Flaw (Outcast, Outlaw Leader...)", -1),
    "major_flaw": ("Major Social Flaw (Outlaw, Outsider)", -3),
}

#: The circumstances and resources that change his resistance (p. 23):
#: (label, change, whether it is a resource).
MODIFIERS: dict[str, tuple[str, int, bool]] = {
    "major_trouble": ("A Major Flaw likely to trouble the principal", -3, False),
    "minor_trouble": ("A Minor Flaw likely to trouble the principal", -1, False),
    "dominated": ("A Minor Flaw the principal uses to dominate him", -6, False),
    "skill": ("Main Ability 6 or more", 1, True),
    "exceptional": ("Main Ability 8 or more", 3, True),
    "minor_virtue": ("A Minor General or Supernatural Virtue", 1, True),
    "major_virtue": ("A Major General or Supernatural Virtue", 3, True),
    "rival": ("Serves a rival", 9, True),
    "underlings": ("Underlings: up to half a dozen", 1, True),
    "many_underlings": ("Many underlings: up to two dozen", 3, True),
    "useful_flaw": ("A useful Minor Flaw (Busybody, Mentor...)", 1, True),
}

#: The Virtues that give 12 points of agents at creation (p. 23).
CREATION_VIRTUES = frozenset(
    {"Social Contacts", "Mercenary Captain", "Close Family Ties", "Landed Noble"}
)
CREATION_POINTS = 12

#: The impressing roll's Ease Factor (p. 24).
IMPRESS_EASE = 6
#: Agency experience bought with a pound (p. 25).
XP_PER_POUND = 5
#: The xp to raise a Bond by one, as for an Ability: 5 x the new score.
XP_PER_LEVEL = 5

#: The Tasks for Agents table (p. 24): Ease Factor by task.
TASKS: dict[str, tuple[str, int]] = {
    "common": ("Common information, easily had", 3),
    "sensitive": ("Sensitive information, hard to get", 6),
    "secret": ("Secret information known to a few", 9),
    "easy": ("An Easy task (Ease Factor 6 or less)", 3),
    "hard": ("A Hard task (Ease Factor 12 or less)", 6),
    "impressive": ("An Impressive task (Ease Factor 18 or less)", 9),
}
#: How soon it must be done (p. 24).
TIMEFRAME: dict[str, tuple[str, int]] = {
    "weeks": ("Within a few weeks", 0),
    "days": ("Within a few days", 1),
    "day": ("Within one day", 3),
}
#: The risk to the agent (p. 24): (label, modifier, botch dice; None for a
#: simple die).
RISK: dict[str, tuple[str, int, int | None]] = {
    "none": ("None at all", 0, None),
    "embarrassment": ("Embarrassment or his reputation", 1, 1),
    "injury": ("Injury or imprisonment", 3, 3),
    "death": ("Death", 6, 5),
}
#: The Tasks for Agents table's deeds (p. 24): the highest Ease Factor of
#: the task the agent then rolls against.
TASK_BANDS: dict[str, tuple[str, int]] = {
    "easy": ("An Easy task (Ease Factor 6 or less)", 6),
    "hard": ("A Hard task (Ease Factor 12 or less)", 12),
    "impressive": ("An Impressive task (Ease Factor 18 or less)", 18),
}
#: The share of the time a Flaw that takes his time keeps him away (p. 25).
UNAVAILABLE: dict[str, float] = {"minor": 0.25, "major": 0.5}


def max_agents(presence: int, intrigue: int, leadership: int, gift: int) -> int:
    """How many agents he can hold: 2 x (Presence + the better of Intrigue
    and Leadership - the Gift's penalty), at least 1."""
    return max(1, 2 * (presence + max(intrigue, leadership) - gift))


def character_max_agents(character: Character) -> int:
    return max_agents(
        character.characteristics.presence,
        scores.ability_level(character, "Intrigue"),
        scores.ability_level(character, "Leadership"),
        gift_penalty(character),
    )


def resistance(status: str, modifiers: list[str]) -> int:
    """A potential agent's starting resistance from the Agent Recruitment
    Table: never below 1."""
    chosen = [m for m in dict.fromkeys(modifiers) if m in MODIFIERS]
    total = STATUS_RESISTANCE.get(status, STATUS_RESISTANCE["free"])[1]
    total += sum(MODIFIERS[m][1] for m in chosen)
    resources = sum(1 for m in chosen if MODIFIERS[m][2])
    if resources > 6:
        total += 9
    elif resources > 3:
        total += 6
    return max(1, total)


def impress_total(presence: int, leadership: int, gift: int) -> int:
    """What a stress die adds to, to impress him (against IMPRESS_EASE)."""
    return presence + leadership - gift


@dataclass(frozen=True)
class Spent:
    """What Agency experience did: the resistance it wore off or the Bond
    levels it bought, and what is left over."""

    worn: int = 0
    levels: int = 0
    left: int = 0
    recruited: bool = False


def wear_down(agent: Agent, xp: int) -> Spent:
    """Spend Agency experience on an impressed potential agent: each point
    of resistance costs as many points as it now stands at. At 0 he is an
    agent with a Bond of 0. The xp that can't buy a whole point is left."""
    if agent.resistance is None:
        agent.resistance = resistance(agent.status, agent.modifiers)
    if not agent.impressed or agent.resistance <= 0:
        return Spent(left=max(0, xp))
    left, worn = max(0, xp), 0
    while agent.resistance > 0 and left >= agent.resistance:
        left -= agent.resistance
        agent.resistance -= 1
        worn += 1
    recruited = agent.resistance == 0
    if recruited:
        agent.bond = 0
        agent.bond_xp = 0
    return Spent(worn=worn, left=left, recruited=recruited)


def strengthen(agent: Agent, xp: int) -> Spent:
    """Agency experience on a recruited agent's Bond, as an Ability rises."""
    agent.bond_xp += max(0, xp)
    levels = 0
    while agent.bond_xp >= XP_PER_LEVEL * (agent.bond + 1):
        agent.bond_xp -= XP_PER_LEVEL * (agent.bond + 1)
        agent.bond += 1
        levels += 1
    return Spent(levels=levels)


def xp_for_pounds(pounds: int) -> int:
    """Agency experience bought with money (an agent not yet prosperous)."""
    return XP_PER_POUND * max(0, pounds)


def task_ease(task: str, timeframe: str = "weeks", risk: str = "none") -> int:
    """The persuasion roll's Ease Factor for a task."""
    return TASKS[task][1] + TIMEFRAME[timeframe][1] + RISK[risk][1]


def persuasion_total(communication: int, ability: int, bond: int, gift: int) -> int:
    """What a die adds to, to have the agent take the task on."""
    return communication + ability + bond - gift


def band_of(ease: int) -> str | None:
    """The easiest band of deed a task of Ease Factor `ease` fits (None:
    beyond an Impressive task)."""
    return next((key for key, (_, top) in TASK_BANDS.items() if ease <= top), None)


def botch_dice(risk: str) -> int | None:
    """The botch dice a task's risk to the agent gives (None: a simple
    die, with no risk to him)."""
    return RISK[risk][2]


def may_be_asked(agent: Agent) -> bool:
    """Whether he can be set a task: recruited, with a Bond of +1."""
    return agent.resistance == 0 and agent.bond >= 1


def recruited(agent: Agent) -> bool:
    """Whether his resistance is worn to nothing: he is an agent."""
    return agent.resistance == 0


def kept(character: Character) -> int:
    """The agents counted against his limit: the recruited ones only."""
    return sum(1 for agent in character.agents if recruited(agent))


def pending(character: Character) -> int:
    """The people still being won over, not yet counted against the limit."""
    return len(character.agents) - kept(character)


def starting_resistance(agent: Agent) -> int:
    """His resistance from the Agent Recruitment Table."""
    return resistance(agent.status, agent.modifiers)


def current_resistance(agent: Agent) -> int:
    """What is left of his resistance (the table's figure until worn)."""
    if agent.resistance is None:
        return starting_resistance(agent)
    return agent.resistance


def xp_to_recruit(now: int) -> int:
    """The Agency experience that wears a resistance of `now` to nothing:
    now + (now - 1) + ... + 1."""
    return max(0, now) * (max(0, now) + 1) // 2


def hates_principal(agent: Agent) -> bool:
    """Held by coercion, or through a Flaw used to dominate him: the
    principal has Difficult Underlings for this agent (pp. 22-23)."""
    return agent.coerced or "dominated" in agent.modifiers


def can_impress(agent: Agent) -> bool:
    """Whether the impressing roll is still to make for him."""
    return not agent.impressed and not recruited(agent)


def can_spend(character: Character, agent: Agent) -> bool:
    """Whether Agency experience can go on him: an impressed potential
    agent while there is experience to spend, or a recruited agent's Bond
    (which money can also buy)."""
    if recruited(agent):
        return True
    return agent.impressed and character.agency_xp > 0


def adventure_agency(xp: int) -> int:
    """The Agency experience a season's Adventure experience brings: as
    much again (pp. 24-25)."""
    return max(0, xp)
