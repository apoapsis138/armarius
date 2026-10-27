"""What else happens in a siege besides its events (Lords of Men pp.
112-116): the steps More's Siege Actions gives a siege, as the core's
command steps.

- Change Deployments (p. 113): the units at each wall, with a warning for
  a wall the besiegers hold and the garrison leaves undefended.
- A Supplies Story or Spell (pp. 112, 116): a blockade or a relief moves
  the Supplies a step; Conjuration of Bread adds +7 to the season's
  supplies rolls; Raise the Siege (ReMe 30, Duration Sun) sets the
  commander a roll against 12 to resist its pessimism.
- Run the Stockade (p. 112's batch rolls): the waiting and its supplies
  rolls, interval after interval, for as long as asked or until it ends.
- The Castle Taken (p. 116): it changes hands, with its fate in the Diary.

Pattern: a Choose of steps, each a Form from a builder here, kept in a
dict by name (the Command pattern, as conflicts.COMMANDS is).
"""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any

from . import sieges
from .commands import Choice, Choose, Command, Form, Refuse, notes
from .form_spec import DialogField
from .markup import escape
from .models import WALLS, Saga, Siege, SiegeEvent
from .rules import dice
from .rules import siege as rules

TITLE = "Siege Actions"
HELP_ID = "siege-actions"
#: Conjuration of Bread's bonus to a season's supplies rolls (p. 116).
BREAD_BONUS = rules.BREAD_BONUS
#: Raise the Siege: the commander's Intelligence + Leadership simple roll
#: to resist its suggestion (p. 116). The spell only darkens his view until
#: sunset; whether he lifts the siege is the storyguide's.
RAISE_EASE = 12
#: A siege ended by a breach: its castle still to be recorded taken.
BREACHED = "Breached"
#: The most intervals Run the Stockade plays at once.
MOST_INTERVALS = 52


def undefended(siege: Siege) -> list[int]:
    """The walls the besiegers hold that no garrison unit defends: each
    may provoke an undefended escalade (p. 113)."""
    if siege.flag_until is not None and siege.days < siege.flag_until:
        # Raise the Veronese Flag's men-at-arms seem to hold every wall.
        return []
    return [
        i
        for i in range(4)
        if siege.besieger_walls[i] > 0 and siege.garrison_walls[i] == 0
    ]


def _wall(i: int) -> str:
    return WALLS[i] if i < len(WALLS) else f"Wall {i + 1}"


# -- deployments (p. 113) ------------------------------------------------------


def _deploy_fields(siege: Siege) -> list[DialogField]:
    found: list[DialogField] = []
    for i in range(4):
        found.append(
            DialogField(
                f"besieger_{i}",
                f"Besiegers at the {_wall(i)}",
                "int",
                siege.besieger_walls[i],
            )
        )
        found.append(
            DialogField(
                f"garrison_{i}",
                f"Garrison at the {_wall(i)}",
                "int",
                siege.garrison_walls[i],
            )
        )
    return found


def deployments(saga: Saga, siege: Siege) -> Form:
    def apply(values: dict[str, Any]) -> list[str]:
        siege.besieger_walls = [
            max(0, values.get(f"besieger_{i}") or 0) for i in range(4)
        ]
        siege.garrison_walls = [
            max(0, values.get(f"garrison_{i}") or 0) for i in range(4)
        ]
        open_walls = undefended(siege)
        held = sum(1 for n in siege.besieger_walls if n)
        told = [
            f"Besiegers at {held} wall(s): "
            + (
                "a stockade."
                if rules.stockaded(siege)
                else "no stockade (three walls are needed)."
            )
        ]
        if open_walls:
            told.append(
                "Undefended: "
                + ", ".join(_wall(i) for i in open_walls)
                + ". The besiegers there may escalade it unopposed (p. 113)."
            )
        return notes(*(escape(t) for t in told))

    return Form(
        "Change Deployments",
        lambda: _deploy_fields(siege),
        apply,
        live=lambda values: _deploy_live(values),
        help_id=HELP_ID,
    )


def _deploy_live(values: dict[str, Any]) -> str:
    open_walls = [
        _wall(i)
        for i in range(4)
        if (values.get(f"besieger_{i}") or 0) > 0 and not values.get(f"garrison_{i}")
    ]
    if not open_walls:
        return "[dim]Every wall the besiegers hold is defended.[/]"
    return f"[$text-warning]Undefended: {escape(', '.join(open_walls))}[/]"


# -- supplies stories and spells (pp. 112, 116) --------------------------------


STORY_BLOCKADE, STORY_RELIEF, SPELL_BREAD, SPELL_RAISE, SPELL_FLAG = (
    "blockade",
    "relief",
    "bread",
    "raise",
    "flag",
)
STORIES: list[tuple[str, str]] = [
    ("A blockade: the Supplies fall a step", STORY_BLOCKADE),
    ("A relief: the Supplies rise a step", STORY_RELIEF),
    ("Conjuration of Bread: +7 to this season's supplies rolls", SPELL_BREAD),
    ("Raise the Siege: the commander resists, or despairs until sunset", SPELL_RAISE),
    (
        "Raise the Veronese Flag: illusory men-at-arms on every wall until sunset",
        SPELL_FLAG,
    ),
]


def _better(quality: str) -> str | None:
    order = list(rules.SUPPLIES)
    at = order.index(quality)
    return order[at + 1] if at + 1 < len(order) else None


def _story_fields() -> list[DialogField]:
    return [
        DialogField("story", "What happens", "select", STORY_BLOCKADE, options=STORIES),
        DialogField(
            "resist",
            "The commander's Intelligence + Leadership",
            "int",
            0,
            show_if=lambda v: v.get("story") == SPELL_RAISE,
        ),
        DialogField(
            "die",
            "Simple die",
            "optint",
            None,
            show_if=lambda v: v.get("story") == SPELL_RAISE,
            hint="Blank: rolled now.",
        ),
    ]


def supplies_story(saga: Saga, siege: Siege, rng: random.Random | None = None) -> Form:
    def apply(values: dict[str, Any]) -> list[str]:
        story = values.get("story") or STORY_BLOCKADE
        if story == STORY_BLOCKADE:
            lower = rules.worse(siege.supplies)
            if lower is None:
                text = "The Supplies are Shoddy already: they can fall no further."
            else:
                siege.supplies = lower
                text = f"A blockade: the Supplies fall to {lower}."
        elif story == STORY_RELIEF:
            higher = _better(siege.supplies)
            if higher is None:
                text = "The Supplies are Excellent already."
            else:
                siege.supplies = higher
                text = f"A relief: the Supplies rise to {higher}."
        elif story == SPELL_FLAG:
            siege.flag_until = siege.days + 1
            text = (
                "Raise the Veronese Flag (CrIm 30, Sun): ten illusory men-at-arms "
                "seem to hold the walls until sunset, so no wall looks undefended "
                "(p. 116)."
            )
        elif story == SPELL_BREAD:
            siege.bread_until = siege.days + rules.DAYS_PER_SEASON
            text = (
                f"Conjuration of Bread: +{BREAD_BONUS} to the supplies rolls of "
                "the next season (p. 116)."
            )
        else:
            typed = values.get("die")
            die = (
                typed if typed is not None else dice.simple_die(rng or random.Random())
            )
            total = (values.get("resist") or 0) + die
            if total >= RAISE_EASE:
                text = f"Raise the Siege: the commander resists ({total} against {RAISE_EASE})."
            else:
                text = (
                    f"Raise the Siege: the commander fails to resist ({total} "
                    f"against {RAISE_EASE}): until sunset he takes the darkest "
                    "view of the siege. Whether he lifts it is the storyguide's "
                    "call: record it in the siege's Ended (Edit)."
                )
        siege.events.append(rules_event(siege, text))
        return notes(escape(text), *sieges.record_ending(saga, siege))

    return Form(
        "A Supplies Story or Spell",
        _story_fields,
        apply,
        help_id=HELP_ID,
    )


def rules_event(siege: Siege, text: str) -> SiegeEvent:
    """A line in the siege's chronicle for a story, a spell or its end."""
    return SiegeEvent(siege.days, "story", text)


# -- running the stockade (p. 112) ---------------------------------------------


def run_stockade(saga: Saga, siege: Siege, rng: random.Random | None = None) -> Form:
    def apply(values: dict[str, Any]) -> list[str]:
        dice_ = rng or random.Random()
        wanted = max(1, min(MOST_INTERVALS, values.get("intervals") or 1))
        told: list[str] = []
        played = 0
        for _ in range(wanted):
            if siege.ended:
                break
            rules.begin(siege)
            lines = rules.pass_interval(siege, dice_, saga)
            siege.events.append(
                SiegeEvent(siege.days, rules.WAIT, "The stockade holds.", lines)
            )
            told += [line for line in lines if not line.startswith("Supplies roll")]
            played += 1
        told.insert(0, f"{played} interval(s) waited: day {siege.days}.")
        return notes(*(escape(t) for t in told), *sieges.record_ending(saga, siege))

    return Form(
        "Run the Stockade",
        lambda: [
            DialogField(
                "intervals",
                "Intervals to wait",
                "int",
                4,
                hint=f"The castle's interval is {rules.interval_days(siege)} days; "
                "each brings the supplies rolls due. It stops when the siege ends.",
            )
        ],
        apply,
        save_label="Wait",
        help_id=HELP_ID,
    )


# -- the castle taken (p. 116) -------------------------------------------------


def castle_taken(saga: Saga, siege: Siege) -> Form:
    def apply(values: dict[str, Any]) -> list[str]:
        holder = siege.besieger or sieges.besieger_name(saga, siege)
        siege.holder = holder
        siege.ended = "Taken"
        fate = (values.get("fate") or "").strip()
        governor = (values.get("governor") or "").strip()
        text = f"{sieges.castle_name(saga, siege)} is taken: it is {holder}'s now."
        if governor:
            text += f" {governor} holds it as governor."
        if fate:
            text += f" {fate}"
        siege.events.append(rules_event(siege, text))
        return notes(escape(text), *sieges.record_ending(saga, siege))

    return Form(
        "The Castle Taken",
        lambda: [
            DialogField("governor", "Its governor", "text", ""),
            DialogField(
                "fate",
                "What becomes of it",
                "text",
                "",
                placeholder="e.g. the garrison ransomed, the town spared",
                hint="Men of value ransomed, civilians robbed, the garrison "
                "often hanged: the victor's choice (p. 116).",
            ),
        ],
        apply,
        save_label="Record",
        help_id=HELP_ID,
    )


#: Siege Actions' steps, by their choice.
STEPS: dict[str, tuple[str, Callable[[Saga, Siege], Command]]] = {
    "deploy": ("Change Deployments", deployments),
    "story": ("A Supplies Story or Spell", supplies_story),
    "stockade": ("Run the Stockade", run_stockade),
    "taken": ("The Castle Taken", castle_taken),
}


def actions(saga: Saga, siege: Siege | None) -> Command:
    if siege is None:
        return Refuse(TITLE, "Choose a siege first.")
    if siege.ended == BREACHED:
        # A breached castle's battle inside decides it: The Castle Taken
        # records the end (Lords of Men p. 115).
        return castle_taken(saga, siege)
    if siege.ended:
        return Refuse(TITLE, f"The siege has ended: {escape(siege.ended)}.")
    return Choose(
        TITLE,
        lambda: [Choice(label, key) for key, (label, _build) in STEPS.items()],
        lambda key: STEPS[key][1](saga, siege),
        help_id=HELP_ID,
    )
