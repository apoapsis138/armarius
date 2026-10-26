"""More's Turbulence on a Gifted character: the rolls to incur and to
control a Turbulence, after a botch, forced with Confidence, or midway
through a stressful laboratory season he assists in -- no UI in here. The
rules and their pages are rules.turbulence's (Apprentices pp. 12, 22-24,
56, 59)."""

from __future__ import annotations

import random
from typing import Any

from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import BULLET, escape
from ..models import REALMS, Character, DiaryEntry, Saga, SeasonPlan
from ..rules import lab_seasons, realms
from ..rules import turbulence as tb

TITLE = "Turbulence"
HELP_ID = "turbulence"


def _bullets(lines: list[str]) -> str:
    return "\n".join(f"{BULLET} {escape(line)}" for line in lines)


def _int(values: dict[str, Any], key: str) -> int:
    value = values.get(key)
    return value if isinstance(value, int) else 0


def _occasion(values: dict[str, Any]) -> str:
    return str(values.get("occasion") or tb.BOTCH)


def _lab(values: dict[str, Any]) -> bool:
    return _occasion(values) == tb.LAB


def _lab_check(saga: Saga, character: Character) -> SeasonPlan | None:
    """His Assist plan this season, if it hasn't been checked yet."""
    plan = tb.assist_plan(saga, character)
    return plan if plan is not None and not plan.turbulence else None


def lead_work(saga: Saga, assisting: SeasonPlan) -> tuple[str, int, list[str]]:
    """The magus assisted, his Lab Total, and what makes the season
    stressful that his plan shows."""
    found = tb.lead_plan(saga, assisting)
    if found is None:
        return "", 0, []
    lead, plan = found
    _, made = lab_seasons.work(saga, lead, plan)
    if made is None:
        return lead.name, 0, tb.stressful_reasons(plan.experimenting, 0)
    vis = sum(made.vis_cost.values())
    return (
        lead.name,
        int(made.lab_total.total),
        tb.stressful_reasons(plan.experimenting, vis),
    )


def occasions(saga: Saga, character: Character) -> list[tuple[str, str]]:
    found = [(tb.OCCASIONS[tb.BOTCH], tb.BOTCH)]
    if tb.prone(character):
        found.append((tb.OCCASIONS[tb.PRONE], tb.PRONE))
    found.append((tb.OCCASIONS[tb.FORCED], tb.FORCED))
    if _lab_check(saga, character) is not None:
        found.append((tb.OCCASIONS[tb.LAB], tb.LAB))
    return found


def turbulence_fields(saga: Saga, character: Character) -> list[DialogField]:
    aura, realm = realms.home_aura(saga, character)
    assisting = _lab_check(saga, character)
    lab_total = lead_work(saga, assisting)[1] if assisting is not None else 0
    return [
        DialogField(
            "occasion",
            "Why",
            "select",
            tb.BOTCH,
            options=occasions(saga, character),
            hint="A botch on a stressful activity that includes magic (how "
            "loosely is the troupe's call), or forced at will (Apprentices "
            "pp. 22, 24).",
        ),
        DialogField("aura", "Aura", "int", aura),
        DialogField(
            "aura_realm",
            "Aura's realm",
            "select",
            realm,
            options=[(r, r) for r in REALMS],
            hint="A Turbulence is a Magic power (the Realms Interaction Table).",
        ),
        DialogField(
            "aegis",
            "Aegis of the Hearth he had no part in",
            "int",
            0,
            hint="Its level: half of it comes off the incurring roll (0: none, "
            "or he took part in it).",
        ),
        DialogField(
            "confidence_incur",
            "Confidence spent on incurring",
            "int",
            0,
            hint="+3 a point, at most his Confidence Score.",
        ),
        DialogField(
            "confidence_control",
            "Confidence spent on controlling",
            "int",
            0,
            hint="+3 a point, at most his Confidence Score.",
        ),
        DialogField(
            "sympathy",
            "Sympathetic multiplier",
            "int",
            0,
            hint="Multiplies Penetration with the Ability (Apprentices p. 24).",
        ),
        DialogField(
            "gift_roll",
            "A storyguide character: roll for losing the Gift",
            "check",
            False,
            show_if=_lab,
        ),
        DialogField(
            "lab_total",
            "The parens' Lab Total",
            "int",
            lab_total,
            hint="A 0 on the stress die rolls a botch die for every 10 of it.",
            show_if=lambda v: _lab(v) and bool(v.get("gift_roll")),
        ),
    ]


def _spent(values: dict[str, Any]) -> int:
    forced = 1 if _occasion(values) == tb.FORCED else 0
    return (
        forced
        + max(0, _int(values, "confidence_incur"))
        + max(0, _int(values, "confidence_control"))
    )


def _incur_lines(saga: Saga, character: Character, values: dict[str, Any]):
    return tb.incurring_lines(
        saga,
        character,
        aura=_int(values, "aura"),
        aura_realm=str(values.get("aura_realm") or realms.HERMETIC),
        aegis=max(0, _int(values, "aegis")),
        confidence=max(0, _int(values, "confidence_incur")),
    )


def turbulence_lines(
    saga: Saga, character: Character, values: dict[str, Any]
) -> list[str]:
    occasion = _occasion(values)
    terms = _incur_lines(saga, character, values)
    modifiers = int(sum(t.amount or 0 for t in terms))
    shown = ", ".join(f"{t.label} {int(t.amount or 0):+d}" for t in terms)
    old = tb.years(saga, character)
    lines = [
        f"Incurring: {shown} = {modifiers:+d} + stress die (it can botch), "
        "against the higher of the storyguide's stress die (no botch) and his age"
        + (f" ({old})." if old is not None else " (no birth year: 0).")
    ]
    if tb.uncontrollable(character, occasion):
        lines.append(
            "Turbulence Prone: he can't control it, and its effects are always "
            "bad; the control roll only sizes it."
        )
    else:
        lines.append(
            f"If incurred, controlling: Stamina "
            f"{tb.control_stamina(saga, character, _int(values, 'confidence_control')):+d}"
            f" + stress die against Warping Score {character.aging.warping_score} + "
            "stress die (either can botch); half the difference, rounded down "
            "(the app's choice), is its magnitude."
        )
    if occasion == tb.FORCED:
        lines.append(
            "Forcing it spends a Confidence Point "
            f"(he has {character.background.confidence_points})."
        )
    if occasion == tb.LAB and (assisting := _lab_check(saga, character)):
        lead, _, reasons = lead_work(saga, assisting)
        lines.append(
            f"Assisting {lead or 'the parens'}: "
            + (
                "stressful, as " + " and ".join(reasons) + "."
                if reasons
                else "stressful by the troupe's call (odd hours, a Lab Total "
                "barely enough)."
            )
            + " Uncontrolled, his aid to the Lab Total is halved."
        )
        if values.get("gift_roll"):
            lines.append(
                "Losing the Gift: a stress die; on a 0, "
                f"{tb.gift_botch_dice(_int(values, 'lab_total'))} botch dice, any 0 "
                "and the Gift is lost."
            )
    reach = tb.penetration(character, _int(values, "sympathy"))
    lines.append(
        f"Penetration {reach}."
        if reach
        else "No Penetration: it can't affect anything with Magic Resistance."
    )
    return lines


def turbulence_problem(character: Character, values: dict[str, Any]) -> str | None:
    score = character.background.confidence_score
    for key in ("confidence_incur", "confidence_control"):
        spent = _int(values, key)
        if spent < 0:
            return "Confidence spent can't be negative."
        if spent > score:
            return f"At most his Confidence Score ({score}) on one roll."
    if _spent(values) > character.background.confidence_points:
        return (
            f"That spends {_spent(values)} Confidence Points; he has "
            f"{character.background.confidence_points}."
        )
    if _int(values, "aegis") < 0:
        return "An Aegis's level can't be negative."
    return None


def roll(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    """The rolls, the Confidence spent, a laboratory season's result on his
    Assist plan, and a Diary entry."""
    occasion = _occasion(values)
    spent = _spent(values)
    character.background.confidence_points -= spent
    incurring = tb.incur(saga, character, rng, _incur_lines(saga, character, values))
    controlling = None
    if incurring.incurred:
        controlling = tb.control(
            saga,
            character,
            rng,
            confidence=_int(values, "confidence_control"),
            cannot_control=tb.uncontrollable(character, occasion),
        )
    lines = tb.result_lines(
        character,
        incurring,
        controlling,
        sympathy=_int(values, "sympathy"),
        occasion=occasion,
    )
    if spent:
        lines.append(
            f"{spent} Confidence Point{'s' if spent > 1 else ''} spent; "
            f"{character.background.confidence_points} left."
        )
    if occasion == tb.LAB and (assisting := _lab_check(saga, character)):
        assisting.turbulence = (
            tb.NONE
            if controlling is None
            else tb.CONTROLLED
            if controlling.controlled
            else tb.UNCONTROLLED
        )
        if values.get("gift_roll"):
            lines.append(
                tb.gift_roll_line(tb.gift_roll(saga, rng, _int(values, "lab_total")))
            )
    character.diary.append(
        DiaryEntry(
            saga.current_year,
            saga.current_season,
            TITLE,
            "\n".join(
                [
                    tb.OCCASIONS.get(occasion, occasion) + ".",
                    *lines,
                    f"Rules: {tb.LAB_SOURCE if occasion == tb.LAB else tb.SOURCE}",
                ]
            ),
        )
    )
    return notes(*lines)


def turbulence_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Turbulence: Roll rolls it, kept in the Diary."""
    if character is None:
        return Refuse(TITLE, "Choose a character first.")
    if not tb.gifted(character):
        return Refuse(TITLE, "Only the Gifted suffer Turbulences (Apprentices p. 22).")
    chance = rng or random.Random()
    who = character
    return Form(
        f"{TITLE}: {escape(who.name)}",
        lambda: turbulence_fields(saga, who),
        lambda values: roll(saga, who, values, chance),
        validate=lambda values: turbulence_problem(who, values),
        live=lambda values: _bullets(turbulence_lines(saga, who, values)),
        save_label="Roll",
        help_id=HELP_ID,
        inspector="The Turbulence Rolls",
    )
