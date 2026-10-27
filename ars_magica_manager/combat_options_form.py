"""Combat Options (More on a fight): Lords of Men's optional combat rules
(Chapter Nine) worked out for one of the fight's characters, as a
calculator the table plays from: a charge's bonus and its shock, a
horse's gait, cover and concealment, higher ground, how many may attack
one man, interrupting, and leaping into or from the saddle. It changes
nothing in the fight; the figures are rules.combat_options's.

Pattern: OPTIONS is a dict from an option to the function that words it
(Strategy, reduced to a dict of functions)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from . import fights
from .commands import Form, Refuse
from .form_spec import DialogField, pairs
from .markup import escape
from .models import CHARACTER_FIGHTER, Character, Fight, Saga
from .rules import combat_options as co
from .rules.scores import ability_level

TITLE = "Combat Options"
HELP_ID = "combat-options"


def _characters(saga: Saga, fight: Fight) -> list[tuple[str, str]]:
    found = []
    for side in fights.sides(fight):
        for c in side.combatants:
            if c.kind == CHARACTER_FIGHTER and (who := saga.character(c.ref_id)):
                found.append((escape(who.name), who.id))
    return found


def _charge(who: Character | None, values: dict[str, Any]) -> str:
    ability = values.get("ability") or "Single Weapon"
    score = ability_level(who, ability) if who else 0
    return (
        f"[$label]Charge[/] +{score} to the Attack ({escape(ability)}), and a "
        "Fatigue level spent: the horse's, mounted; none across difficult "
        "ground (LoM pp. 123, 126). The one charged resists its shock: "
        f"[$label]mounted[/] {co.resist_charge(who, 0, mounted=True) if who else 0} "
        f"+ die, [$label]on foot[/] Strength + Size + Ability + die, against the "
        "charge's Damage Total + the horse's Size (p. 127)."
    )


def _gait(_who: Character | None, values: dict[str, Any]) -> str:
    gait = values.get("gait") or "Walk or Trot"
    missile, fall, ease, guard = co.GAITS[gait]
    return (
        f"[$label]{escape(gait)}[/]: missiles {missile:+d}, a fall does Size "
        f"+{fall} + stress die, an extended action needs {ease}, and "
        f"(optional) Defense +{guard} (LoM p. 127; Errata p. 75)."
    )


def _cover(_who: Character | None, values: dict[str, Any]) -> str:
    cover = values.get("cover") or "One-quarter"
    hidden = values.get("concealment") or ""
    words = f"[$label]Cover[/] {escape(cover)}: Defense +{co.COVER[cover]}"
    if hidden:
        attack, defence = co.CONCEALMENT[hidden]
        words += (
            f"  ·  [$label]Concealment[/] {escape(hidden)}: Attack +{attack}, "
            f"Defense +{defence}"
        )
    return words + f"  ·  higher ground +{co.HIGHER_GROUND} (LoM pp. 130-131)."


def _crowd(_who: Character | None, _values: dict[str, Any]) -> str:
    most = co.MOST_ATTACKERS
    return (
        f"At most {most['open']} attack one man in the open, {most['wall']} with "
        f"his back to a wall, {most['doorway']} from each side of a doorway (LoM "
        "p. 131)."
    )


def _interrupt(who: Character | None, values: dict[str, Any]) -> str:
    ability = values.get("ability") or "Single Weapon"
    priority = co.action_priority(who, ability) if who else 0
    return (
        f"[$label]Action Priority[/] {priority} + stress die (Quickness + "
        f"{escape(ability)} - Encumbrance); the higher acts first (LoM p. 119)."
    )


def _saddle(who: Character | None, _values: dict[str, Any]) -> str:
    leap = co.leap_from_saddle(who) if who else 0
    vault = co.vault_into_saddle(who) if who else 0
    return (
        f"[$label]Leap from the saddle[/] {leap} + die against {co.LEAP_EASE}  ·  "
        f"[$label]Vault into it[/] {vault} + die against {co.VAULT_EASE}  ·  "
        f"pinned under a horse: {co.PINNED_EASE} to get free (LoM pp. 127-128)."
    )


#: Each option the form offers, and what it says for the character.
OPTIONS: dict[str, tuple[str, Callable[[Character | None, dict[str, Any]], str]]] = {
    "charge": ("A charge, and its shock", _charge),
    "gait": ("A horse's gait", _gait),
    "cover": ("Cover, concealment and higher ground", _cover),
    "crowd": ("How many may attack one man", _crowd),
    "interrupt": ("Interrupting", _interrupt),
    "saddle": ("Into and out of the saddle", _saddle),
}


def fields(saga: Saga, fight: Fight) -> list[DialogField]:
    people = _characters(saga, fight)
    return [
        DialogField(
            "option",
            "Option",
            "select",
            "charge",
            options=[(label, key) for key, (label, _fn) in OPTIONS.items()],
        ),
        DialogField(
            "who",
            "Character",
            "select",
            people[0][1] if people else None,
            options=people,
            allow_blank=True,
            placeholder="(none of the fight's characters)",
        ),
        DialogField(
            "ability",
            "Combat Ability",
            "text",
            "Single Weapon",
            show_if=lambda v: v.get("option") in ("charge", "interrupt"),
        ),
        DialogField(
            "gait",
            "Gait",
            "select",
            "Walk or Trot",
            options=pairs(tuple(co.GAITS)),
            show_if=lambda v: v.get("option") == "gait",
        ),
        DialogField(
            "cover",
            "Cover",
            "select",
            "One-quarter",
            options=pairs(tuple(co.COVER)),
            show_if=lambda v: v.get("option") == "cover",
        ),
        DialogField(
            "concealment",
            "Concealment",
            "select",
            None,
            options=pairs(tuple(co.CONCEALMENT)),
            allow_blank=True,
            placeholder="(none)",
            show_if=lambda v: v.get("option") == "cover",
        ),
    ]


def live(saga: Saga, values: dict[str, Any]) -> str:
    option = values.get("option") or "charge"
    who = saga.character(values.get("who"))
    return OPTIONS[option][1](who, values)


def options_form(saga: Saga, fight: Fight | None) -> Form | Refuse:
    if fight is None:
        return Refuse(TITLE, "Choose a fight first.")
    return Form(
        f"{TITLE}: {escape(fight.name)}",
        lambda: fields(saga, fight),
        lambda _values: None,
        live=lambda values: live(saga, values),
        save_label="Done",
        cancel_label="Close",
        help_id=HELP_ID,
        inspector="The Option",
    )
