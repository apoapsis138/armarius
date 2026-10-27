"""More's Ars Goetia on a character who holds a Goetic Art: the total of
Summoning, Scouring, Ablating, Binding or Commanding against a spirit's
Might, and a roll of it -- no UI in here, and nothing kept. The rules and
their pages are rules.goetic's (RoP: The Infernal pp. 114-119)."""

from __future__ import annotations

import random
from typing import Any

from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField, pairs
from ..markup import BULLET, escape
from ..models import Character, Saga
from ..rules import dice, penetration, realms
from ..rules import goetic as gr
from ..rules import hybrid_magic as hybrid
from ..rules.infernalists import SACRIFICES
from ..rules.realms import present_aura

TITLE = "Ars Goetia"
HELP_ID = "ars-goetia"
NONE = "none"
AREA_LORE = "Area Lore"


def _arts(character: Character) -> list[str]:
    held = gr.goetic_arts(character)
    if gr.SUMMONING in held:
        held.insert(held.index(gr.SUMMONING) + 1, gr.SCOURING)
    return held


def _area_lores(character: Character) -> list[str]:
    return [a.name for a in character.abilities if a.name.startswith(AREA_LORE)]


def _art(values: dict[str, Any], character: Character) -> str:
    return str(values.get("art") or _arts(character)[0])


def _summons(character: Character):
    return lambda v: _art(v, character) in (gr.SUMMONING, gr.SCOURING)


def goetic_fields(saga: Saga, character: Character) -> list[DialogField]:
    """What Ars Goetia asks."""
    aura, aura_realm = present_aura(saga, character)
    areas = _area_lores(character)
    summons = _summons(character)
    return [
        DialogField(
            "art",
            "Goetic Art",
            "select",
            _arts(character)[0],
            options=pairs(_arts(character)),
        ),
        DialogField(
            "might",
            "The spirit's Might",
            "int",
            10,
            hint="Scouring: the Might he hopes for; it draws about half the total.",
        ),
        DialogField("demon", "The spirit is a demon", "check", False),
        DialogField(
            "demon_hierarchy",
            "The demon's Hierarchy",
            "int",
            0,
            hint="Its Hierarchy x 5 goes on the target; his own x 5 on the total.",
            show_if=lambda v: bool(v.get("demon")),
        ),
        DialogField(
            "lore",
            "Realm Lore",
            "select",
            "Infernal Lore",
            options=pairs(hybrid.REALM_LORES),
            hint="The Lore of the spirit's realm; a magus may use Vim instead.",
            show_if=lambda v: _art(v, character) != gr.SCOURING,
        ),
        DialogField(
            "area",
            "Area Lore",
            "select",
            areas[0] if areas else NONE,
            options=[(name, name) for name in areas] + [("None", NONE)],
            show_if=lambda v: _art(v, character) == gr.SCOURING,
        ),
        DialogField(
            "connection",
            "Arcane Connection",
            "select",
            NONE,
            options=[("None", NONE), *pairs(penetration.ARCANE_CONNECTIONS)],
            hint="A demon's True Name counts as indefinite.",
            show_if=lambda v: _art(v, character) != gr.SCOURING,
        ),
        DialogField(
            "realm",
            "Summoning works as",
            "select",
            "Infernal",
            options=pairs(gr.SUMMONING_REALMS),
            hint="Summoning may be a Magic or Faerie Power; the other Arts are "
            "always Infernal.",
            show_if=summons,
        ),
        DialogField(
            "in_circle",
            "The spirit is held in a summoning circle",
            "check",
            True,
            show_if=lambda v: not summons(v),
        ),
        DialogField(
            "resists",
            "It resists",
            "check",
            True,
            hint="A spirit that agreed lets the effect through.",
            show_if=lambda v: _art(v, character) in (gr.BINDING, gr.COMMANDING),
        ),
        DialogField(
            "sacrifice",
            "Sacrifice",
            "select",
            NONE,
            options=[("None", NONE)]
            + [(f"{what} (+{bonus})", what) for what, bonus in SACRIFICES.items()],
        ),
        DialogField("aura", "Aura", "int", aura),
        DialogField(
            "aura_realm",
            "Aura's realm",
            "select",
            aura_realm,
            options=pairs(realms.REALMS),
        ),
    ]


def _int(values: dict[str, Any], key: str, default: int = 0) -> int:
    value = values.get(key)
    return value if isinstance(value, int) else default


def _total(character: Character, values: dict[str, Any]):
    art = _art(values, character)
    if art == gr.SCOURING:
        area = str(values.get("area") or NONE)
        lore = area if area != NONE else AREA_LORE
    else:
        lore = str(values.get("lore") or "Infernal Lore")
    connection = str(values.get("connection") or NONE)
    sacrifice = SACRIFICES.get(str(values.get("sacrifice") or NONE), 0)
    return gr.total(
        character,
        art,
        lore=lore,
        aura=_int(values, "aura"),
        aura_realm=str(values.get("aura_realm") or realms.HERMETIC),
        arcane_connection=None if connection == NONE else connection,
        demon=bool(values.get("demon")),
        sacrifice=sacrifice,
        summoning_realm=str(values.get("realm") or "Infernal"),
    )


def _against(
    character: Character, values: dict[str, Any]
) -> tuple[str, int, int, bool, bool, int]:
    art = _art(values, character)
    might = max(0, _int(values, "might", 10))
    in_circle = bool(values.get("in_circle", True))
    resists = bool(values.get("resists", True))
    rank = _int(values, "demon_hierarchy") if values.get("demon") else 0
    return (
        art,
        might,
        rank,
        in_circle,
        resists,
        gr.target_level(
            art, might, in_circle=in_circle, resists=resists, demon_hierarchy=rank
        ),
    )


def lines(character: Character, values: dict[str, Any]) -> list[str]:
    """The total and what it must reach, plain."""
    breakdown = _total(character, values)
    base = int(breakdown.total)
    art, might, rank, in_circle, resists, level = _against(character, values)
    terms = ", ".join(
        f"{line.label} {int(line.amount or 0):+d}" for line in breakdown.lines
    )
    said = [f"{art} total {base:+d} + stress die ({terms})."]
    if art in (gr.SUMMONING, gr.SCOURING):
        weak = might + gr.HIERARCHY_STEP * rank
        said.append(
            f"Against {level}: a die of {max(level - base, 0)} holds the spirit in "
            f"the circle; {max(weak - base, 0)} calls it only while he "
            "concentrates. A Fatigue level either way."
        )
    elif art in (gr.BINDING, gr.COMMANDING) and in_circle and not resists:
        said.append("It allows the effect: only a botch fails.")
    else:
        said.append(f"It must exceed {level}: a die of {max(level - base + 1, 0)}.")
    if art == gr.ABLATING:
        said.append(
            "Each 5 over the target is an Ablation Point: "
            + "; ".join(f"{k}: {v}" for k, v in gr.ABLATION_USES.items())
            + "."
        )
    if art == gr.COMMANDING:
        said.append("Commands: " + ", ".join(gr.COMMANDS) + ".")
    return said


def _live(character: Character):
    def live(values: dict[str, Any]) -> str:
        return "\n".join(
            f"{BULLET} {escape(line)}" for line in lines(character, values)
        )

    return live


def roll(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    """The roll, said: nothing is kept."""
    base = int(_total(character, values).total)
    art, might, rank, in_circle, resists, _level = _against(character, values)
    rolled = dice.roll(rng, base, saga=saga)
    result = gr.outcome(
        art,
        rolled.total,
        might,
        in_circle=in_circle,
        resists=resists,
        demon_hierarchy=rank,
        botched=rolled.die.botched,
    )
    extra = ""
    if art == gr.SCOURING and not rolled.die.botched:
        extra = f"A spirit of about Might {gr.scouring_might(rolled.total)} answers."
    return notes(
        f"{art} {base:+d} + {rolled.die.value} = {rolled.total}: {result.text}",
        extra,
        "Summoning costs a Fatigue level."
        if art in (gr.SUMMONING, gr.SCOURING)
        else "",
    )


def goetic_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Ars Goetia: the calculator; Roll rolls it once."""
    if character is None or not gr.holds_goetic_art(character):
        return Refuse(TITLE, "Only one who holds a Goetic Art works the Ars Goetia.")
    chance = rng or random.Random()
    sorcerer = character
    return Form(
        f"{TITLE}: {escape(sorcerer.name)}",
        lambda: goetic_fields(saga, sorcerer),
        lambda values: roll(saga, sorcerer, values, chance),
        live=_live(sorcerer),
        save_label="Roll",
        cancel_label="Close",
        help_id=HELP_ID,
        inspector="The Goetic Total",
    )
