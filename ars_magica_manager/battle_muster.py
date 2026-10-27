"""Raising an army and ending a battle (Lords of Men, Chapter Eight): the
steps More's Muster and Aftermath gives a battle, as the core's command
steps, so both front-ends ask the same questions.

- Raise Allies (p. 102): Presence + Leadership + Affinity + a simple die,
  with the Allied Troops Table's modifiers (p. 103); the proportion
  multiplies the lord's core vassal force, and the allies join the side.
- Hire Mercenaries (pp. 103-104): groups bought from the lord's Mercenary
  Budget, at 15 / 5 / 2 / 2 / 1 pounds a group; a War Loan steps his
  wealth down for five times what the step costs his budget (p. 104).
- Roll Deployment (pp. 104-105): Intelligence + Area Lore + a stress die,
  plus the highest magnitude of a spell that shapes the ground.
- End of the Day (p. 109): a winner, or a truce at nightfall.
- The Aftermath (p. 108): a Confidence Point for each event the victors
  won, and an experience point toward the commander's Reputation.

Each side keeps its groups by kind (BattleSide.mix) as they are added, so
an event's losses come from the kind its Enemy names (p. 106).

Pattern: a Choose of steps, each a Form from a builder here, kept in a
dict by name (the Command pattern, as conflicts.COMMANDS is).
"""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any

from . import armies, battles, diaries, lords
from .commands import Choice, Choose, Command, Form, Refuse, notes
from .form_spec import DialogField
from .markup import escape, problem
from .models import Battle, BattleSide, Character, Neighbour, Saga
from .rules import battle, confidence, dice
from .rules import siege as siege_rules
from .rules.scores import ability_level

TITLE = "Muster and Aftermath"
HELP_ID = "battle-muster"
SOURCE = "Lords of Men, Chapter Eight: Massed Combat, pp. 102-109"

#: The Allied Troops Table's modifiers (p. 103), by what the form asks.
ALLY_MODIFIERS: dict[str, tuple[str, int]] = {
    "winter": ("Raising an army in winter", -3),
    "harvest": ("Raising an army around harvest", -1),
    "last_season": ("He raised an army the previous season", -3),
    "this_year": ("He raised one earlier this year", -1),
    "crusade": ("During an active crusade", -3),
    "wealthy": ("He is Wealthy", 1),
    "poor": ("He is Poor", -1),
    "inspirational": ("He is Inspirational", 3),
    "underlings": ("Difficult Underlings", -2),
    "threat": ("The affinity's lands are under threat", 1),
    "revolt": ("He is in revolt against his liege", -2),
    "major_social_virtue": ("A Major social Virtue", 3),
    "minor_social_virtue": ("A Minor social Virtue", 1),
    "minor_social_flaw": ("A Minor social Flaw", -1),
    "major_social_flaw": ("A Major social Flaw", -3),
    "spoils": ("The promise of wealth or title", 3),
}
#: A crusade is called by a churchman with Senior Clergy (Realms of
#: Power: The Divine p. 93), treated as having the Affinity of the most
#: prominent noble of his diocese (Lords of Men p. 104).
SENIOR_CLERGY = "vf_senior_clergy"
#: A War Loan's multiple of the budget it gives up (p. 104).
LOAN_TIMES = 5


def _side_options(saga: Saga, entry: Battle) -> list[tuple[str, str]]:
    return [
        (escape(battles.side_name(saga, entry, i)), str(i))
        for i in range(len(battles.sides(entry)))
    ]


def _characters(saga: Saga) -> list[tuple[str, str]]:
    return [(escape(c.name), c.id) for c in saga.characters]


def _side(entry: Battle, values: dict[str, Any]) -> BattleSide:
    return battles.sides(entry)[int(values.get("side") or 0)]


def _diary(saga: Saga, entry: Battle, side: BattleSide, text: str) -> None:
    lord = saga.neighbour(side.neighbour_id)
    covenant = saga.covenant(side.covenant_id)
    diaries.write(
        saga.current_year,
        saga.current_season,
        entry.name,
        text,
        covenants=[covenant] if covenant else [],
        neighbours=[lord] if lord else [],
    )


# -- Raise Allies (pp. 102-103) ------------------------------------------------


def core_groups(saga: Saga, side: BattleSide) -> int:
    """The side's lord's core vassal force in groups, levies only on home
    ground (p. 102); 0 for a side with no lord."""
    lord = saga.neighbour(side.neighbour_id)
    if lord is None:
        return 0
    return armies.army_groups(lord, at_home=side.at_home)


def ally_total(saga: Saga, values: dict[str, Any]) -> tuple[int, list[str]]:
    """Presence + Leadership + Affinity + the modifiers ticked, before the
    die, and its terms."""
    who = saga.character(values.get("commander"))
    presence = who.characteristics.presence if who else 0
    leadership = ability_level(who, "Leadership") if who else 0
    affinity = values.get("affinity") or 0
    total = presence + leadership + affinity
    terms = [
        f"Presence {presence:+d}",
        f"Leadership {leadership}",
        f"Affinity {affinity}",
    ]
    for key, (label, amount) in ALLY_MODIFIERS.items():
        if values.get(key):
            total += amount
            terms.append(f"{label} {amount:+d}")
    return total, terms


def _ally_fields(saga: Saga, entry: Battle) -> list[DialogField]:
    first = battles.sides(entry)[0]
    return [
        DialogField("side", "Side", "select", "0", options=_side_options(saga, entry)),
        DialogField(
            "commander",
            "Who calls them",
            "select",
            None,
            options=_characters(saga),
            allow_blank=True,
            placeholder="(a lord with no sheet: Presence and Leadership 0)",
        ),
        DialogField(
            "crusade",
            "A crusade",
            "check",
            False,
            hint="Called by a churchman with Senior Clergy: his Affinity is "
            "the most prominent noble's of his diocese, rolled on the Allied "
            "Troops Table (Lords of Men p. 104; the book's Army Size Table "
            "doesn't exist, so the troupe's reading).",
        ),
        DialogField(
            "affinity",
            "Affinity score",
            "int",
            0,
            hint="His Affinity (p. 102); for a crusade, the noble's.",
        ),
        DialogField(
            "core",
            "Core vassal groups",
            "int",
            core_groups(saga, first) or first.groups,
            hint="His household and vassals before scutage or mercenaries: "
            "his lord's title gives it, levies only on home ground (p. 102).",
        ),
        *(
            DialogField(key, label, "check", False)
            for key, (label, _amount) in ALLY_MODIFIERS.items()
        ),
        DialogField(
            "die",
            "Simple die",
            "optint",
            None,
            hint="Blank: rolled now. A total better than 12 adds troops past "
            "his own force (p. 103).",
        ),
    ]


def _ally_live(saga: Saga, values: dict[str, Any]) -> str:
    total, terms = ally_total(saga, values)
    core = values.get("core") or 0
    rows = [
        f"{battle.ALLIED_TROOPS[i][2]} at {battle.ALLIED_TROOPS[i][0]}"
        for i in range(4)
    ]
    return (
        f"[$label]Before the die[/] {total}  [dim]({', '.join(terms)})[/]\n"
        f"[i]A simple die more; the table: {', '.join(reversed(rows))} of his "
        f"{core} core groups.[/]"
    )


def _ally_problem(saga: Saga, values: dict[str, Any]) -> str | None:
    if not values.get("crusade"):
        return None
    who = saga.character(values.get("commander"))
    if who is None or all(vf.vf_id != SENIOR_CLERGY for vf in who.virtues_flaws):
        return "A crusade is called by a churchman with Senior Clergy (p. 104)."
    return None


def raise_allies(saga: Saga, entry: Battle, rng: random.Random | None = None) -> Form:
    def apply(values: dict[str, Any]) -> list[str]:
        side = _side(entry, values)
        total, _terms = ally_total(saga, values)
        typed = values.get("die")
        die = typed if typed is not None else dice.simple_die(rng or random.Random())
        rolled = total + die
        _share, name = battle.allied_proportion(rolled)
        extra = battle.allied_groups(values.get("core") or 0, rolled)
        battles.add_groups(side, battles.ALLIES, extra)
        called = "Crusaders" if values.get("crusade") else "Allies"
        text = f"{called} called: {total} + die {die} = {rolled}" + (
            f": {name}, {extra} group(s) join." if extra else ": none come."
        )
        _diary(saga, entry, side, text)
        return notes(escape(text))

    return Form(
        "Raise Allies",
        lambda: _ally_fields(saga, entry),
        apply,
        validate=lambda values: _ally_problem(saga, values),
        live=lambda values: _ally_live(saga, values),
        save_label="Roll",
        help_id=HELP_ID,
        inspector="The Affinity",
    )


# -- Hire Mercenaries and a War Loan (pp. 103-104) -----------------------------


def loan(lord: Neighbour, becomes: str) -> int:
    """What a War Loan that leaves the lord `becomes` (a lower wealth)
    raises: five times the budget he gives up (p. 104). An Average lord
    becoming Poor borrows five times his budget; a Wealthy one becoming
    Average gains five times the difference, becoming Poor five times the
    Wealthy budget."""
    budgets = lords.SURPLUS[lords.title(lord)]
    return LOAN_TIMES * (budgets[armies.wealth(lord)] - budgets[becomes])


def loan_options(lord: Neighbour | None) -> list[tuple[str, str]]:
    """The wealth a War Loan may leave the lord with: none for a Poor lord,
    who can't borrow (p. 104)."""
    if lord is None:
        return []
    now = armies.WEALTH.index(armies.wealth(lord))
    return [(f"Become {w}: {loan(lord, w)} pounds", w) for w in armies.WEALTH[:now]][
        ::-1
    ]


def budget(saga: Saga, side: BattleSide, *, becomes: str = "") -> int | None:
    """What the side's lord may spend on mercenaries: his Mercenary Budget,
    or with a War Loan the loan and the budget of the wealth it leaves him
    (p. 104); None for a side with no lord."""
    lord = saga.neighbour(side.neighbour_id)
    if lord is None:
        return None
    if not becomes:
        return lords.surplus(lord)
    return loan(lord, becomes) + lords.SURPLUS[lords.title(lord)][becomes]


def _hire_fields(saga: Saga, entry: Battle) -> list[DialogField]:
    return [
        DialogField("side", "Side", "select", "0", options=_side_options(saga, entry)),
        *(
            DialogField(
                kind,
                f"{kind.title()} ({cost} pounds a group)",
                "int",
                0,
            )
            for kind, cost in battle.MERCENARY_COST.items()
        ),
        DialogField(
            "loan",
            "A War Loan",
            "select",
            None,
            options=[("Become Average", "Average"), ("Become Poor", "Poor")],
            allow_blank=True,
            placeholder="(no loan)",
            hint="A Wealthy lord may become Average for five times the "
            "difference of the two budgets, or Poor for five times the "
            "Wealthy budget; an Average one Poor for five times his; a Poor "
            "lord can't borrow. Repaid from spoils or stories. He spends the "
            "loan and his new wealth's budget. It needs a banker able to "
            "lend it and to collect if he defaults, and may take weeks: not "
            "for a lightning war (p. 104).",
        ),
    ]


def _hired(values: dict[str, Any]) -> dict[str, int]:
    return {k: max(0, values.get(k) or 0) for k in battle.MERCENARY_COST}


def _hire_problem(saga: Saga, entry: Battle, values: dict[str, Any]) -> str | None:
    side = _side(entry, values)
    lord = saga.neighbour(side.neighbour_id)
    becomes = values.get("loan") or ""
    if becomes and lord is not None:
        allowed = [w for _label, w in loan_options(lord)]
        if not allowed:
            return "A Poor lord can't take a War Loan (p. 104)."
        if becomes not in allowed:
            return f"{lord.name} is {armies.wealth(lord)}: a loan can't leave him {becomes}."
    room = budget(saga, side, becomes=becomes if lord is not None else "")
    cost = battle.mercenary_cost(_hired(values))
    if room is not None and cost > room:
        return f"They cost {cost} pounds; the budget is {room}."
    return None


def _hire_live(saga: Saga, entry: Battle, values: dict[str, Any]) -> str:
    side = _side(entry, values)
    cost = battle.mercenary_cost(_hired(values))
    lord = saga.neighbour(side.neighbour_id)
    becomes = values.get("loan") or ""
    if lord is not None and becomes not in [w for _l, w in loan_options(lord)]:
        becomes = ""
    room = budget(saga, side, becomes=becomes)
    line = f"[$label]Cost[/] {cost} pounds"
    if room is None:
        return line + "  [dim](a side with no lord: no budget to check)[/]"
    words = f"{line}  ·  [$label]Budget[/] {room} pounds"
    return words if cost <= room else words + "\n" + problem("Over the budget.")


def hire_mercenaries(saga: Saga, entry: Battle) -> Form:
    def apply(values: dict[str, Any]) -> list[str]:
        side = _side(entry, values)
        hired = _hired(values)
        for kind, count in hired.items():
            battles.add_groups(side, kind, count)
        said = ", ".join(f"{n} {k}" for k, n in hired.items() if n) or "none"
        text = f"Mercenaries hired: {said}, {battle.mercenary_cost(hired)} pounds."
        lord = saga.neighbour(side.neighbour_id)
        becomes = values.get("loan") or ""
        if becomes and lord is not None:
            raised = loan(lord, becomes)
            lord.details["wealth"] = becomes
            text += f" A War Loan of {raised} pounds leaves {lord.name} {becomes}."
        _diary(saga, entry, side, text)
        return notes(escape(text))

    return Form(
        "Hire Mercenaries",
        lambda: _hire_fields(saga, entry),
        apply,
        validate=lambda values: _hire_problem(saga, entry, values),
        live=lambda values: _hire_live(saga, entry, values),
        save_label="Hire",
        help_id=HELP_ID,
        inspector="The Purse",
    )


# -- Deployment (pp. 104-105) --------------------------------------------------


def deployment_total(who: Character | None, area_lore: str) -> int:
    """Intelligence + Area Lore, before the die and any terrain spell."""
    if who is None:
        return 0
    lore = (
        ability_level(who, f"Area Lore: {area_lore}")
        if area_lore
        else max(
            (
                ability_level(who, a.name)
                for a in who.abilities
                if a.name.startswith("Area Lore")
            ),
            default=0,
        )
    )
    return who.characteristics.intelligence + lore


def _deploy_fields(saga: Saga, entry: Battle) -> list[DialogField]:
    return [
        DialogField("side", "Side", "select", "0", options=_side_options(saga, entry)),
        DialogField(
            "who",
            "Who chooses the ground",
            "select",
            None,
            options=_characters(saga),
            allow_blank=True,
            hint="The commander, or a lieutenant; a commander who rolls after "
            "his lieutenant must keep his own total (p. 104).",
        ),
        DialogField("area", "Area Lore of", "text", "", placeholder="blank: his best"),
        DialogField(
            "spell",
            "A spell on the ground (magnitude)",
            "int",
            0,
            hint="The highest magnitude of a spell that shapes the terrain or "
            "the troops' deployment (p. 105).",
        ),
        DialogField("die", "Stress die", "optint", None, hint="Blank: rolled now."),
    ]


def roll_deployment(
    saga: Saga, entry: Battle, rng: random.Random | None = None
) -> Form:
    def apply(values: dict[str, Any]) -> list[str]:
        side = _side(entry, values)
        who = saga.character(values.get("who"))
        base = deployment_total(who, (values.get("area") or "").strip())
        typed = values.get("die")
        die = (
            typed
            if typed is not None
            else dice.stress_die(rng or random.Random(), 0).value
        )
        side.deployment = base + (values.get("spell") or 0) + die
        text = f"Deployment Total {side.deployment} (Int + Area Lore {base}, die {die}"
        text += f", spell {values['spell']})." if values.get("spell") else ")."
        _diary(saga, entry, side, text)
        return notes(escape(text))

    return Form(
        "Roll Deployment",
        lambda: _deploy_fields(saga, entry),
        apply,
        save_label="Roll",
        help_id=HELP_ID,
    )


# -- the end of the day, and the aftermath (pp. 108-109) -----------------------


END_WON, END_TRUCE = "won", "truce"


def _end_fields(saga: Saga, entry: Battle) -> list[DialogField]:
    return [
        DialogField(
            "how",
            "How the day ends",
            "select",
            END_WON,
            options=[
                ("A side wins the day", END_WON),
                ("A truce at nightfall", END_TRUCE),
            ],
        ),
        DialogField(
            "side",
            "The victors",
            "select",
            "0",
            options=_side_options(saga, entry),
            show_if=lambda v: v.get("how") != END_TRUCE,
        ),
        DialogField(
            "commander",
            "The victors' commander",
            "select",
            None,
            options=_characters(saga),
            allow_blank=True,
            show_if=lambda v: v.get("how") != END_TRUCE,
            hint="Gains 1 xp toward an appropriate Reputation (p. 108).",
        ),
        DialogField(
            "reputation",
            "That Reputation",
            "text",
            "Victorious commander",
            show_if=lambda v: v.get("how") != END_TRUCE,
        ),
    ]


def events_won(entry: Battle, side: int) -> int:
    """The battlefield events won by `side`."""
    return sum(1 for e in entry.events if (e.side == side) == e.won)


def end_of_day(saga: Saga, entry: Battle) -> Form:
    """A winner of the day, or a truce: the victors who fought gain a
    Confidence Point for each event their side won, and the commander an
    xp toward a Reputation (p. 108)."""

    def apply(values: dict[str, Any]) -> list[str]:
        if values.get("how") == END_TRUCE:
            entry.ended = "A truce at nightfall: the dead and wounded are gathered."
            for side in battles.sides(entry):
                _diary(saga, entry, side, entry.ended)
            return notes(escape(entry.ended))
        side_index = int(values.get("side") or 0)
        won = events_won(entry, side_index)
        name = battles.side_name(saga, entry, side_index)
        entry.ended = f"{name} won the day, {won} event(s) won."
        told = [entry.ended]
        heroes = {e.who for e in entry.events if e.side == side_index and e.who}
        for who_id in heroes:
            hero = saga.character(who_id)
            if hero is not None and won:
                hero.background.confidence_points += won
                told.append(f"{hero.name}: +{won} Confidence Point(s).")
        leader = saga.character(values.get("commander"))
        if leader is not None:
            label = (values.get("reputation") or "Victorious commander").strip()
            confidence.deed_toward(leader, label, 1)
            told.append(f"{leader.name}: 1 xp toward {label}.")
        for side in battles.sides(entry):
            _diary(saga, entry, side, entry.ended)
        told += _breach(saga, entry, side_index)
        return notes(*(escape(t) for t in told))

    return Form(
        "End of the Day",
        lambda: _end_fields(saga, entry),
        apply,
        save_label="Record",
        help_id=HELP_ID,
    )


def _breach(saga: Saga, entry: Battle, victors: int) -> list[str]:
    """An escalade battle won by the besiegers (the first side) at a Shoddy
    wall breaches the castle, which becomes the backdrop of a standard
    battle (Lords of Men p. 115)."""
    siege = next((s for s in saga.sieges if s.id == entry.siege_id), None)
    if siege is None or victors != 0:
        return []
    if (
        siege.defenses != siege_rules.QUALITIES[0]
        and siege_rules.walls(siege)[entry.siege_wall]
    ):
        return ["The wall stands: the castle holds, its garrison the poorer."]
    siege.ended = "Breached"
    return [
        "The castle is breached: fight the battle inside as a standard battle, "
        "and record it taken with Siege Actions' The Castle Taken."
    ]


#: Muster and Aftermath's steps, by their choice.
STEPS: dict[str, tuple[str, Callable[[Saga, Battle], Command]]] = {
    "allies": ("Raise Allies (Presence + Leadership + Affinity)", raise_allies),
    "mercenaries": ("Hire Mercenaries, or take a War Loan", hire_mercenaries),
    "deployment": ("Roll a Deployment Total", roll_deployment),
    "end": ("End of the Day: a winner, or a truce", end_of_day),
}


def muster(saga: Saga, entry: Battle | None) -> Command:
    if entry is None:
        return Refuse(TITLE, "Choose a battle first.")
    return Choose(
        TITLE,
        lambda: [Choice(label, key) for key, (label, _build) in STEPS.items()],
        lambda key: STEPS[key][1](saga, entry),
        help_id=HELP_ID,
    )
