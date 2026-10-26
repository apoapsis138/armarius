"""More's Sell Finished Goods on a craftsman's This Season: the haggling
roll for a sale the story calls for, its price written in the Diary -- no
UI in here. The rules are rules.selling's."""

from __future__ import annotations

import random
from typing import Any

from . import diaries
from .commands import Command, Form, Refuse, notes
from .form_spec import DialogField
from .markup import escape
from .models import Character, Saga
from .rules import dice
from .rules import selling as sl
from .rules.scores import ability_level

TITLE = "Sell Finished Goods"
HELP_ID = "sell-finished-goods"


def crafts(character: Character) -> list[str]:
    """The Craft Abilities whose goods the character sells."""
    return [a.name for a in character.abilities if a.name.startswith("Craft")]


def _important(values: dict[str, Any]) -> bool:
    return values.get("customer") == sl.IMPORTANT


def sell_fields(character: Character) -> list[DialogField]:
    presence = character.characteristics.presence
    bargain = ability_level(character, "Bargain")
    return [
        DialogField(
            "bargaining",
            "His bargaining",
            "info",
            f"Presence {presence:+d} + Bargain {bargain} = "
            f"{sl.bargain_total(character)}",
        ),
        DialogField(
            "goods",
            "The goods",
            "text",
            "",
            placeholder="(what he sells: a lot of 8 shortswords...)",
        ),
        DialogField(
            "standard",
            "Standard price (pence)",
            "int",
            0,
            hint="The guild's price for standard goods; superior and excellent "
            "goods are unregulated, so price them higher (City & Guild p. 75).",
        ),
        DialogField(
            "customer",
            "Customer",
            "select",
            sl.TYPICAL,
            options=[(label, key) for key, label in sl.CUSTOMERS.items()],
            required=True,
        ),
        DialogField(
            "theirs",
            "The customer's roll",
            "int",
            0,
            show_if=_important,
            hint="His Communication + Bargain + a stress die.",
        ),
        DialogField(
            "die",
            "Die",
            "optint",
            None,
            placeholder="(blank: the app rolls it)",
            hint="A simple die against a typical customer, a stress die "
            "against an important one.",
        ),
        DialogField(
            "botched",
            "The die botched",
            "check",
            False,
            show_if=lambda v: _important(v) and v.get("die") is not None,
        ),
    ]


def _validate(values: dict[str, Any]) -> str | None:
    if int(values.get("standard") or 0) < 1:
        return "Give the standard price, in pence."
    die = values.get("die")
    if die is not None and int(die) < 0:
        return "A die can't be below 0."
    if die is not None and not _important(values) and not 1 <= int(die) <= 10:
        return "A simple die shows 1 to 10."
    return None


def _odds(total: int) -> str:
    """What a simple die must show against a typical customer."""
    need = sl.EASE - total
    best = sl.EASE - 1 + sl.CAP // sl.STEP - total
    if need > 10:
        return "No simple die reaches it: he sells at the standard price."
    over = (
        f"Any die sells at least {sl.STEP}% over"
        if need <= 1
        else f"A die of {need} or more sells {sl.STEP}% over"
    )
    most = f"; {max(1, best)} or more, the most ({sl.CAP}% over)" if best <= 10 else ""
    below = ". Below it, the standard price." if need > 1 else "."
    return over + most + below


def sell_live(character: Character) -> Any:
    """The inspector: the roll he makes and what it needs."""

    def inspect(values: dict[str, Any]) -> str:
        total = sl.bargain_total(character)
        standard = int(values.get("standard") or 0)
        goods = str(values.get("goods") or "").strip()
        lines = [
            f"[b]{escape(character.name)}[/]  [$label]Presence + Bargain {total}[/]",
            f"[i]{escape(goods) if goods else 'His goods'}, at "
            f"{standard} pence standard.[/]",
        ]
        if _important(values):
            theirs = int(values.get("theirs") or 0)
            lines += [
                f"His roll: a stress die + [b]{total}[/] against the customer's "
                f"[b]{theirs}[/] [dim](City & Guild p. 75)[/]",
                f"Each point he wins by is {sl.STEP}% more, each he loses by "
                f"{sl.STEP}% less, at most {sl.CAP}% either way; a botch sells "
                "for next to nothing.",
            ]
        else:
            lines += [
                f"His roll: a simple die + [b]{total}[/] against Ease Factor "
                f"[b]{sl.EASE}[/] [dim](City & Guild p. 75)[/]",
                _odds(total),
            ]
        return "\n".join(lines)

    return inspect


def _roll(
    saga: Saga, values: dict[str, Any], rng: random.Random
) -> tuple[int, bool, str]:
    """The craftsman's die: (its value, whether it botched, as shown)."""
    typed = values.get("die")
    if typed is not None:
        botched = _important(values) and bool(values.get("botched"))
        return int(typed), botched, "a botch" if botched else str(typed)
    if not _important(values):
        die = dice.simple_die(rng)
        return die, False, str(die)
    found = dice.stress_die(rng, 1, saga=saga)
    return found.value, found.botched, "a botch" if found.botched else str(found.value)


def apply_sale(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    standard = int(values.get("standard") or 0)
    goods = str(values.get("goods") or "").strip() or "his goods"
    die, botched, shown = _roll(saga, values, rng)
    mine = sl.bargain_total(character) + die
    customer = str(values.get("customer") or sl.TYPICAL)
    theirs = int(values.get("theirs") or 0)
    found = sl.sale(standard, customer, mine, theirs, botched)
    if customer == sl.IMPORTANT:
        rolled = f"Die {shown}: {mine} against the customer's {theirs}."
    else:
        rolled = f"Die {shown}: {mine} against Ease Factor {sl.EASE}."
    if found.botched:
        outcome = (
            "A botch: desperate for the sale, he lets the goods go for next to nothing."
        )
    elif found.change:
        outcome = (
            f"{abs(found.change)}% {'over' if found.change > 0 else 'under'} the "
            f"standard price: {found.price} pence for {standard}."
        )
    else:
        outcome = f"The standard price: {found.price} pence."
    lines = [f"Sold {goods}. {rolled}", outcome]
    diaries.write(
        saga.current_year,
        saga.current_season,
        f"Sold: {goods}",
        " ".join([*lines, f"Rules: {sl.SOURCE}."]),
        characters=[character],
    )
    return notes(*map(escape, lines), f"Written in {escape(character.name)}'s Diary.")


def sell_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    if character is None:
        return Refuse(TITLE, "Choose a character first.")
    if not crafts(character):
        return Refuse(
            TITLE,
            f"{escape(character.name)} has no Craft to sell the goods of: add "
            "one on Abilities first.",
        )
    return Form(
        f"{TITLE}: {escape(character.name)}",
        lambda: sell_fields(character),
        lambda values: apply_sale(saga, character, values, rng or random.Random()),
        validate=_validate,
        live=sell_live(character),
        save_label="Roll",
        help_id=HELP_ID,
        inspector="The Sale",
    )
