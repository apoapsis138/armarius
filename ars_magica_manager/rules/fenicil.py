"""Fenicil's rituals: House Guernicus's Mercurian rituals (Houses of
Hermes: True Lineages, Guernicus, Fenicil's Rituals, pp. 76-77).

Each ritual is learned like a spell from a teacher, a season each, and has
an Ability of its own (its name) that the casting rolls with; the Arts it
names count only for Magic Resistance, and Unstructured Casters can't
learn them. The group first casts Wizard's Communion of a combined
magnitude equal to the Ease Factor. The ritual leader rolls Stamina + the
sum of the participants' scores in the ritual's Ability + aura + die
against the Ease Factor; the excess is its Penetration. It is slow and
safe: no botch dice unless stressed or disrupted. It costs as many pawns
of vis as its Ease Factor, of which half may be replaced by prepared
materials at a pound of silver a pawn (a season's lab work); Mercurian
Magic halves vis and materials only if every participant has it. A
greater ritual takes a season; a lesser one five minutes a point of Ease
Factor."""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Character
from .lab import ability_score
from .lab_virtues import has
from .rounding import round_down, round_up

SOURCE = "Houses of Hermes: True Lineages, Guernicus, Fenicil's Rituals, pp. 76-77"

GREATER, LESSER = "greater", "lesser"
MERCURIAN_MAGIC = "vf_mercurian_magic"
UNSTRUCTURED_CASTER = "vf_unstructured_caster"
#: Minutes of casting a lesser ritual takes for each point of Ease Factor.
LESSER_MINUTES = 5
#: Silver for each pawn of vis replaced by prepared materials.
SILVER_A_PAWN = 1


@dataclass(frozen=True)
class Ritual:
    name: str
    arts: str
    rdt: str
    ease: int
    kind: str
    does: str


RITUALS: tuple[Ritual, ...] = (
    Ritual(
        "Curse of Thoth",
        "PeVi",
        "R: Arc, D: Year, T: Spec",
        78,
        GREATER,
        "A magical group's members, penetrated, are always stressed on magical "
        "rolls, roll twice the botch dice and are Twilight Prone for a year.",
    ),
    Ritual(
        "Curse of Mars",
        "ReMe",
        "R: Arc, D: Year, T: Spec",
        78,
        GREATER,
        "A nation's nobles, penetrated, are drawn to civil war.",
    ),
    Ritual(
        "Call for Justice",
        "ReVi",
        "R: Arc, D: Mom, T: Ind",
        78,
        GREATER,
        "Calls Nemesis to punish a criminal, or those who called unjustly.",
    ),
    Ritual(
        "Wisdom of Athena",
        "CrMe",
        "R: Per, D: Sun, T: Ind",
        12,
        LESSER,
        "+5 to the leader's Folk Ken, Intrigue and Awareness.",
    ),
    Ritual(
        "Sight of Alatheia",
        "InVi",
        "R: Per, D: Sun, T: Vision",
        12,
        LESSER,
        "Second Sight 5 for the leader, or +5 to Second Sight rolls.",
    ),
    Ritual(
        "Veil All Eyes",
        "ReMe(An)",
        "R: Touch, D: Moon, T: Spec",
        18,
        LESSER,
        "The participants pass unnoticed and are forgotten.",
    ),
    Ritual(
        "The Oath of Truth",
        "PeCo",
        "R: Voice, D: Spec, T: Ind",
        18,
        LESSER,
        "A willing subject swears to tell the truth at a trial; breaking it is "
        "death or worse (resists dispelling as level 60).",
    ),
    Ritual(
        "The Will of Alatheia",
        "PeCo",
        "R: Voice, D: Spec, T: Ind",
        24,
        LESSER,
        "A willing subject swears to avoid an action, for ever (resists "
        "dispelling as level 80); sometimes a Tribunal punishment.",
    ),
)

BY_NAME: dict[str, Ritual] = {r.name: r for r in RITUALS}


def casting_total(stamina: int, ability_scores: list[int], aura: int, die: int) -> int:
    """The leader's Stamina + every participant's score in the ritual's
    Ability + the aura + the die."""
    return stamina + sum(ability_scores) + aura + die


def penetration(total: int, ritual: Ritual) -> int | None:
    """Its Penetration (the total less the Ease Factor), or None when the
    total falls short and the ritual fails."""
    return total - ritual.ease if total >= ritual.ease else None


def vis_and_silver(
    ritual: Ritual, *, materials: bool = False, all_mercurian: bool = False
) -> tuple[int, int]:
    """Pawns of vis and pounds of silver it costs: its Ease Factor in vis,
    half of it in silver instead with `materials`, all halved when every
    participant has Mercurian Magic."""
    pawns = ritual.ease
    silver = round_down(pawns / 2) if materials else 0
    pawns -= silver
    if all_mercurian:
        pawns, silver = round_up(pawns / 2), round_up(silver / 2)
    return pawns, silver * SILVER_A_PAWN


def casting_time(ritual: Ritual) -> str:
    if ritual.kind == GREATER:
        return "a season"
    return f"{LESSER_MINUTES * ritual.ease} minutes"


def known(magus: Character) -> list[Ritual]:
    """The rituals whose Ability the magus has."""
    names = {a.name for a in magus.abilities}
    return [r for r in RITUALS if r.name in names]


def reminders(magus: Character) -> list[str]:
    """A sentence (plain text) for each of Fenicil's rituals the magus
    knows."""
    found: list[str] = []
    for ritual in known(magus):
        score = sum(ability_score(magus, ritual.name))
        if has(magus, UNSTRUCTURED_CASTER):
            found.append(f"{ritual.name}: an Unstructured Caster can't cast it.")
            continue
        found.append(
            f"{ritual.name} ({ritual.arts}, Fenicil's {ritual.kind} ritual, Ease "
            f"Factor {ritual.ease}): Wizard's Communion of {ritual.ease} "
            f"magnitudes, then Stamina + everyone's {ritual.name} (yours "
            f"{score}) + aura + die; Penetration the excess; {ritual.ease} "
            f"pawns of vis; {casting_time(ritual)}. {ritual.does}"
        )
    return found
