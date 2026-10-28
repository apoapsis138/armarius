"""A Muslim's Faith actions: Invoke Baraka from a holy forbear, and the
Hajj. Each is a form, rolled or kept on saving -- no UI in here. The rules
are rules.baraka's (Realms of Power: The Divine pp. 103-108); the forbears'
powers are rules.saints'.

What is kept: a baraka asked, and a Hajj made, are written in the Diary;
the Hajj's Pious +3 and 3 Faith Points go on the sheet."""

from __future__ import annotations

import random
from typing import Any

from . import diaries
from .commands import Command, Form, Refuse, notes
from .form_spec import DialogField
from .markup import escape
from .models import Character, Saga
from .rules import baraka as bk
from .rules import saints as sr
from .rules.theban_customs import pious

HELP_ID = "baraka"
HAJJ_HELP = "hajj"
INVOKE = "Invoke Baraka"
HAJJ = "The Hajj"
NONE = "-none-"


def _number(value: Any) -> int:
    return int(value) if value is not None else 0


def _diary(saga: Saga, character: Character, name: str, text: str) -> None:
    diaries.write(
        saga.current_year,
        saga.current_season,
        name,
        f"{text} Rules: {bk.SOURCE}.",
        characters=[character],
    )


def _trait_options(character: Character) -> list[tuple[str, str]]:
    """His positive Personality Traits, Pious first."""
    traits = sorted(
        (t for t in character.personality_traits if t.score > 0),
        key=lambda t: (t.name.casefold() != "pious", -t.score),
    )
    return [(escape(f"{t.name} {t.score:+d}"), t.name) for t in traits]


def baraka_fields(character: Character) -> list[DialogField]:
    traits = _trait_options(character)
    return [
        DialogField(
            "forbear",
            "The forbear",
            "select",
            bk.QURAN,
            options=[
                (escape(f"{f.name} (Might {f.might})"), key)
                for key, f in bk.FORBEARS.items()
            ],
            required=True,
        ),
        DialogField(
            "at_shrine",
            "At his shrine",
            "check",
            False,
            hint="Baraka is sought only at the forbear's shrine, usually his "
            "tomb; the Qur'an anywhere (RoP: The Divine p. 103).",
            show_if=lambda v: v.get("forbear") != bk.QURAN,
        ),
        DialogField(
            "trait",
            "His highest Muslim Personality Trait",
            "select",
            traits[0][1] if traits else NONE,
            options=[*traits, ("(none)", NONE)],
            required=True,
            hint="The book doesn't list the Muslim traits: the player chooses.",
        ),
        DialogField(
            "aura",
            "Divine aura where he asks",
            "int",
            0,
            hint="+1 a level; the ritual prayer, a Muslim holiday and Ramadan "
            "each raise a Muslim Dominion aura by 1 (pp. 107-108).",
        ),
        *(
            DialogField(key, f"{label} ({value:+d})", "check", False)
            for key, (label, value) in bk.TICKS.items()
        ),
        DialogField("donation", "Donation now (+1 to +3)", "int", 0),
        DialogField("sin", "A recent sinful act (-1 to -3)", "int", 0),
        DialogField(
            "power",
            "The miracle asked",
            "select",
            None,
            options=[(escape(sr.POWERS[key].name), key) for key in _powers()],
            allow_blank=True,
            placeholder="(general aid; the storyguide decides)",
            hint="A specific miracle rather than general aid is -5 (p. 103); "
            "it must be one of the forbear's powers.",
        ),
    ]


def _powers() -> list[str]:
    """Every forbear's powers, each once, in the order the book first gives
    them."""
    return list(dict.fromkeys(k for f in bk.FORBEARS.values() for k in f.powers))


def _trait_score(character: Character, values: dict[str, Any]) -> int:
    name = values.get("trait")
    return next((t.score for t in character.personality_traits if t.name == name), 0)


def _asking(character: Character, values: dict[str, Any]) -> bk.Asking:
    return bk.asking(
        character,
        trait=_trait_score(character, values),
        aura=_number(values.get("aura")),
        ticks=tuple(key for key in bk.TICKS if values.get(key)),
        donation=_number(values.get("donation")),
        sin=_number(values.get("sin")),
        specific=bool(values.get("power")),
    )


def _problem(values: dict[str, Any]) -> str | None:
    forbear = bk.FORBEARS.get(str(values.get("forbear") or ""))
    if forbear is None:
        return "Choose the forbear."
    if not forbear.anywhere and not values.get("at_shrine"):
        return (
            f"Baraka is sought at {forbear.name}'s shrine (p. 103): {forbear.places}."
        )
    if _number(values.get("aura")) < 0:
        return "A Divine aura can't be below 0."
    if not 0 <= _number(values.get("donation")) <= 3:
        return "A donation adds +1 to +3."
    if not 0 <= _number(values.get("sin")) <= 3:
        return "A recent sinful act takes -1 to -3."
    power = values.get("power")
    if power and power not in forbear.powers:
        return f"{forbear.name} has no such power in the book."
    return None


def _signed(total: int) -> str:
    return f"{'-' if total < 0 else '+'} [b]{abs(total)}[/]"


def baraka_live(character: Character) -> Any:
    def live(values: dict[str, Any]) -> str:
        forbear = bk.FORBEARS.get(str(values.get("forbear") or ""))
        if forbear is None:
            return "[dim]Choose the forbear.[/]"
        found = _asking(character, values)
        chance = bk.chance(found.total) * 100
        powers = ", ".join(sr.POWERS[k].name for k in forbear.powers)
        lines = [
            "[i]A forbear's blessing, sought at his shrine; he is never threatened.[/]",
            f"Simple die {_signed(found.total)} [dim]= {' '.join(found.terms)}[/]",
            f"Against [b]15 + the storyguide's simple die[/], rolled in secret: "
            f"[b]{chance:.0f}%[/] [dim](RoP: The Divine pp. 87, 103)[/]",
            f"[dim]{escape(forbear.name)}: Divine Might {forbear.might}; at "
            f"{escape(forbear.places)}.[/]",
            f"[dim]Powers: {escape(powers) or 'the book lists none'} (p. "
            f"{forbear.page}).[/]",
        ]
        problem = _problem(values)
        if problem:
            lines.append(f"[$text-error]{escape(problem)}[/]")
        return "\n".join(lines)

    return live


def baraka_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Invoke Baraka: the roll, and if the forbear blesses him, the
    aid asked; written in the Diary."""
    if character is None:
        return Refuse(INVOKE, "Choose a character first.")

    def apply(values: dict[str, Any]) -> list[str]:
        forbear = bk.FORBEARS[str(values["forbear"])]
        found = _asking(character, values)
        rolled = bk.ask(found.total, rng or random.Random())
        lines = [
            f"Die {rolled.die} + {found.total} = {rolled.rolled} against 15 + "
            f"{rolled.ease_die} = {rolled.ease}."
        ]
        power = sr.POWERS.get(str(values.get("power") or ""))
        if rolled.heard:
            asked = f": {power.name}" if power is not None else ""
            lines.append(f"The baraka of {forbear.name} aids him{asked}.")
            title = f"Baraka of {forbear.name}"
        else:
            lines.append("No blessing comes; he may ask again another day.")
            title = f"Sought the baraka of {forbear.name}"
        _diary(saga, character, title, " ".join(lines))
        return notes(*map(escape, lines))

    return Form(
        f"{INVOKE}: {escape(character.name)}",
        lambda: baraka_fields(character),
        apply,
        validate=_problem,
        live=baraka_live(character),
        save_label="Pray",
        help_id=HELP_ID,
        inspector="The Baraka",
    )


# -- the Hajj (p. 108) --


def hajj_live(character: Character) -> Any:
    def live(_values: dict[str, Any]) -> str:
        now = pious(character)
        after = max(now, bk.HAJJ_PIOUS)
        return "\n".join(
            [
                "[i]The pilgrimage to Mecca every Muslim who is able makes "
                "once: in the first half of Dhu'l-Hijja, in a state of "
                "ritual purity.[/]",
                f"Pious {now:+d} → [b]{after:+d}[/] [dim](never above +3 by the "
                "Hajj)[/]",
                f"Faith Points {character.background.faith_points} → "
                f"[b]{character.background.faith_points + bk.HAJJ_FAITH}[/] "
                "[dim](RoP: The Divine p. 108)[/]",
            ]
        )

    return live


def hajj_form(saga: Saga, character: Character | None) -> Command:
    """More's The Hajj: Pious +3 and 3 Faith Points, written in the Diary."""
    if character is None:
        return Refuse(HAJJ, "Choose a character first.")

    def apply(values: dict[str, Any]) -> list[str]:
        lines = bk.make_hajj(character)
        place = str(values.get("notes") or "").strip()
        _diary(
            saga,
            character,
            "Made the Hajj",
            " ".join([*lines, *([place] if place else [])]),
        )
        return notes(*map(escape, lines))

    return Form(
        f"{HAJJ}: {escape(character.name)}",
        lambda: [
            DialogField(
                "notes",
                "Notes",
                "text",
                "",
                placeholder="e.g. with the caravan from Damascus",
            )
        ],
        apply,
        live=hajj_live(character),
        save_label="Complete the Hajj",
        help_id=HAJJ_HELP,
        inspector="The Hajj",
    )
