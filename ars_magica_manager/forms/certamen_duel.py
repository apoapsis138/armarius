"""More's Certamen on a magus's Known Spells: a certamen duel with
another magus of the saga, played out as each side's plan says
(rules.certamen_duel; DE pp. 231-233). The rounds are shown, the Fatigue
each lost is taken if asked, the vis spent comes off their raw vis, and
both Diaries record the duel and its stakes.

Pattern: a commands.Form, as the other More rolls are; the duel itself is
a plain function of the two plans.
"""

from __future__ import annotations

import random
from typing import Any

from .. import diaries
from ..arts import FORMS, TECHNIQUES
from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField, pairs
from ..markup import escape
from ..models import FATIGUE_LEVELS, Character, Saga
from ..rules import certamen
from ..rules import certamen_duel as cd

TITLE = "Certamen"
HELP_ID = "certamen-duel"
#: When a side concedes: at a Fatigue penalty, or never.
CONCEDE: list[tuple[str, str]] = [
    ("At -1 (Weary)", "1"),
    ("At -3 (Tired)", "3"),
    ("At -5 (Dazed)", "5"),
    ("Never: fights until he falls", ""),
]


def offers(saga: Saga, character: Character) -> bool:
    return character.type == "magus" and bool(_rivals(saga, character))


def _rivals(saga: Saga, magus: Character) -> list[Character]:
    return [c for c in saga.characters if c.type == "magus" and c is not magus]


def _side_fields(prefix: str, who: str) -> list[DialogField]:
    return [
        DialogField(
            f"{prefix}attack",
            f"{who} attacks",
            "select",
            cd.BETTER,
            options=[(label, key) for key, label in cd.ATTACKS.items()],
        ),
        DialogField(f"{prefix}attack_vis", f"{who}'s vis, attacking", "int", 0),
        DialogField(f"{prefix}defence_vis", f"{who}'s vis, defending", "int", 0),
        DialogField(
            f"{prefix}concede", f"{who} concedes", "select", "3", options=CONCEDE
        ),
    ]


def fields(saga: Saga, magus: Character) -> list[DialogField]:
    rivals = [(escape(c.name), c.id) for c in _rivals(saga, magus)]
    return [
        DialogField(
            "rival",
            "Against",
            "select",
            rivals[0][1],
            options=rivals,
            required=True,
        ),
        DialogField(
            "technique",
            "Technique",
            "select",
            TECHNIQUES[0],
            options=pairs(TECHNIQUES),
        ),
        DialogField(
            "form",
            "Form",
            "select",
            FORMS[0],
            options=pairs(FORMS),
            hint="By custom the challenger chooses the Technique and the "
            "challenged the Form; each may veto the other's first choice, "
            "then must accept the second (DE p. 231).",
        ),
        DialogField(
            "stakes",
            "The stakes",
            "text",
            "",
            hint="What the loser does or refrains from doing.",
        ),
        *_side_fields("", escape(magus.name)),
        *_side_fields("their_", "His rival"),
        DialogField(
            "take_fatigue",
            "Take the Fatigue they lose",
            "check",
            True,
            hint="Certamen causes no wounds, only exhaustion (DE p. 233).",
        ),
    ]


def _plan(magus: Character, values: dict[str, Any], prefix: str) -> cd.Plan:
    concede = str(values.get(f"{prefix}concede") or "")
    return cd.Plan(
        magus,
        attack=str(values.get(f"{prefix}attack") or cd.BETTER),
        attack_vis=int(values.get(f"{prefix}attack_vis") or 0),
        defence_vis=int(values.get(f"{prefix}defence_vis") or 0),
        concede_at=int(concede) if concede else None,
    )


def live(saga: Saga, magus: Character) -> Any:
    def inspect(values: dict[str, Any]) -> str:
        rival = saga.character(values.get("rival"))
        technique = str(values.get("technique") or TECHNIQUES[0])
        form = str(values.get("form") or FORMS[0])
        lines = []
        for who in (magus, rival):
            if who is None:
                continue
            t = certamen.certamen_totals(who, technique, form)
            lines.append(
                f"[b]{escape(who.name)}[/] Initiative {t.initiative:+d}; Attack "
                f"{t.attack_technique:+d} ({technique}) or {t.attack_form:+d} "
                f"({form}); Defense {t.defence_form:+d} ({form}) or "
                f"{t.defence_technique:+d} ({technique}); Weakening "
                f"{t.weakening_base:+d}; Resistance {t.resistance:+d}"
                + (" [dim](Tremere Focus)[/]" if certamen.certamen_focus(who) else "")
            )
        return "\n".join(lines)

    return inspect


def _take(magus: Character, lost: int, spent: dict[str, int], take: bool) -> None:
    if take and lost:
        magus.fatigue_level = FATIGUE_LEVELS[
            min(
                len(FATIGUE_LEVELS) - 1,
                FATIGUE_LEVELS.index(magus.fatigue_level) + lost,
            )
        ]
    for art, pawns in spent.items():
        key = art.lower()
        magus.raw_vis[key] = max(0, magus.raw_vis.get(key, 0) - pawns)
        if not magus.raw_vis[key]:
            del magus.raw_vis[key]


def duel(
    saga: Saga, magus: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    rival = saga.character(values.get("rival"))
    assert rival is not None
    technique = str(values.get("technique") or TECHNIQUES[0])
    form = str(values.get("form") or FORMS[0])
    played = cd.play(
        saga,
        _plan(magus, values, ""),
        _plan(rival, values, "their_"),
        technique,
        form,
        rng,
    )
    take = bool(values.get("take_fatigue"))
    _take(magus, played.fatigue_lost[0], played.vis_spent[0], take)
    _take(rival, played.fatigue_lost[1], played.vis_spent[1], take)
    result = (
        f"{played.winner.name} wins: {played.how}."
        if played.winner is not None
        else f"After {cd.MOST_ROUNDS} rounds, {played.how}."
    )
    stakes = str(values.get("stakes") or "").strip()
    diaries.write(
        saga.current_year,
        saga.current_season,
        f"{TITLE}: {magus.name} and {rival.name} ({technique} {form})",
        " ".join(
            [
                *([f"Stakes: {stakes}."] if stakes else []),
                result,
                f"Rules: {cd.SOURCE}.",
            ]
        ),
        characters=[magus, rival],
    )
    return notes(*map(escape, [*played.lines, result]))


def duel_form(saga: Saga, magus: Character | None) -> Command:
    if magus is None:
        return Refuse(TITLE, "Choose a magus first.")
    if not offers(saga, magus):
        return Refuse(TITLE, "Certamen is between two magi of the saga.")
    return Form(
        f"{TITLE}: {escape(magus.name)}",
        lambda: fields(saga, magus),
        lambda values: duel(saga, magus, values, random.Random()),
        live=live(saga, magus),
        save_label="Duel",
        help_id=HELP_ID,
        inspector="The Duelists",
    )
