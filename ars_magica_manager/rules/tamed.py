"""Tamed creatures in play (DE pp. 385-386): commanding one, and its
Loyalty tests.

Commanding a tamed creature is Presence + Animal Handling (Ride for a
mount, Magic Lore for a tamed elemental and the like) + stress die against
the task's Ease Factor; a task it fears asks a Loyalty test against 6 as
well when it has no Confidence Score, a suicidal one against 9 always. A
Loyalty test is its Loyal Personality Trait + stress die.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from ..models import Character, Saga
from . import dice
from .scores import ability_level

SOURCE = "Ars Magica Definitive Edition, Chapter 10: Training Creatures, pp. 385-386"

#: The Abilities a command may use (DE p. 386).
COMMAND_ABILITIES = ("Animal Handling", "Ride", "Magic Lore")


@dataclass(frozen=True)
class Task:
    """A kind of command: its Ease Factor (None: done without a roll), and
    the Loyalty test it may also ask."""

    label: str
    ease: int | None
    loyalty: int | None = None
    #: Whether the Loyalty test is asked only of a creature with no
    #: Confidence Score.
    loyalty_without_confidence: bool = False


#: The Command Beast table (DE p. 386).
TASKS: dict[str, Task] = {
    "habit": Task("Something it has done many times, with an Ability it has", None),
    "unusual": Task("Not often done, or a stressful moment", 6),
    "complex": Task("A long, complex task, or one it has never done", 9),
    "feared": Task(
        "A task it fears (a battle, fire)",
        12,
        loyalty=6,
        loyalty_without_confidence=True,
    ),
    "suicidal": Task("Clearly suicidal, or very dangerous", 15, loyalty=9),
}


def loyalty(animal: Character) -> int:
    """A tamed animal's Loyal Personality Trait (0 without one)."""
    return max(
        (t.score for t in animal.personality_traits if t.name.startswith("Loyal")),
        default=0,
    )


def command_total(commander: Character, ability: str) -> int:
    """Presence + the Ability used, before the die."""
    return commander.characteristics.presence + ability_level(commander, ability)


def command(
    saga: Saga,
    commander: Character,
    animal: Character,
    task_key: str,
    ability: str,
    rng: random.Random,
) -> list[str]:
    """Roll a command and any Loyalty test it asks: the lines saying what
    happened."""
    task = TASKS[task_key]
    if task.ease is None:
        return [f"{animal.name} does it without a roll: a task it knows well."]
    base = command_total(commander, ability)
    die = dice.stress_die(rng, 1, saga=saga)
    lines: list[str] = []
    if die.botched:
        lines.append(
            f"Presence + {ability} {base:+d} + a botch: {animal.name} may flee, "
            "do something else, or turn on its master."
        )
        return lines
    total = base + die.value
    obeys = total >= task.ease
    lines.append(
        f"Presence + {ability} {base:+d} + die {die.value} = {total} against "
        f"{task.ease}: " + ("it obeys." if obeys else "it doesn't.")
    )
    asks = task.loyalty is not None and (
        not task.loyalty_without_confidence or not animal.background.confidence_score
    )
    if obeys and asks and task.loyalty is not None:
        test = dice.stress_die(rng, 1, saga=saga)
        loyal = loyalty(animal) + test.value
        held = not test.botched and loyal >= task.loyalty
        lines.append(
            f"Loyalty test: Loyal {loyalty(animal):+d} + die {test.value} = "
            f"{loyal} against {task.loyalty}: "
            + ("it follows through." if held else "it balks.")
        )
    return lines
