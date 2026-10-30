"""Cast a Power (More on a hedge wizard): one casting rolled by the
tradition's own rule (rules.hedge_casting): the Casting Score, the die the
rule rolls, divided as it says, against the effect's level or Ease
Factor; a botch's zeroes give Warping Points (DE pp. 227, 389), and the result
goes in the Diary. Each tradition's rule is data on its catalog record
(Hedge Magic RE and the other books), so one form casts them all."""

from __future__ import annotations

import random
from typing import Any

from .. import diaries, seasons
from ..commands import Form, notes
from ..form_spec import DialogField
from ..markup import escape
from ..models import Character, Saga, TraditionDef
from ..rules import casting as hermetic_casting
from ..rules import creation_access as access
from ..rules import dice, realms
from ..rules import hedge_casting as hc

TITLE = "Cast a Power"
#: Cast a Power's own help page.
HELP_ID = "hedge-cast"


def _rules(character: Character) -> list[tuple[TraditionDef, int, str]]:
    """(tradition, rule index, the choice's value) for every non-lab
    casting rule of the character's traditions."""
    return [
        (t, i, f"{t.id}|{i}")
        for t in access.traditions_of(character)
        for i, rule in enumerate(t.casting)
        if not rule.lab
    ]


def _chosen(character: Character, values: dict[str, Any]):
    """The tradition, rule and casting the form's values name."""
    for tradition, index, key in _rules(character):
        if key == values.get("rule"):
            rule = tradition.casting[index]
            castings = hc.castings(character, tradition, rule)
            casting = next(
                (c for c in castings if c.label == values.get("casting")),
                castings[0] if castings else None,
            )
            return tradition, rule, casting
    return None, None, None


def fields(saga: Saga, character: Character) -> list[DialogField]:
    found = _rules(character)
    aura, _ = realms.present_aura(saga, character)
    castings: list[tuple[str, str]] = []
    for tradition, index, _key in found:
        for c in hc.castings(character, tradition, tradition.casting[index]):
            if (c.label, c.label) not in castings:
                castings.append((escape(c.label), c.label))
    return [
        DialogField(
            "rule",
            "Way of casting",
            "select",
            found[0][2] if found else None,
            options=[
                (f"{escape(t.name)}: {escape(t.casting[i].name)}", key)
                for t, i, key in found
            ],
        ),
        DialogField(
            "casting",
            "Arts or Ability used",
            "select",
            castings[0][1] if castings else None,
            options=castings,
            hint="What the casting adds, as the tradition's chapter lists it.",
        ),
        DialogField(
            "level",
            "Level or Ease Factor",
            "int",
            0,
            hint="The effect's level (its guideline), or the Ease Factor the "
            "rule rolls against.",
        ),
        DialogField("aura", "Aura", "int", aura, hint="Where it is cast."),
        DialogField(
            "aura_realm",
            "Aura realm",
            "select",
            realms.HERMETIC,
            options=[(r, r) for r in realms.aura_realms(saga)],
        ),
        DialogField("vis", "Pawns of vis", "int", 0),
        DialogField(
            "die",
            "Die",
            "optint",
            None,
            hint="Blank: rolled now. Type the die shown at the table to use it "
            "instead (0 is a zero, which may botch).",
        ),
    ]


def problem(character: Character, values: dict[str, Any]) -> str | None:
    tradition, rule, casting = _chosen(character, values)
    if tradition is None or rule is None:
        return "Choose the way of casting."
    if casting is None:
        return f"{escape(character.name)} has no Art or Ability this rule uses."
    if (values.get("vis") or 0) < 0:
        return "Pawns of vis can't be fewer than 0."
    return None


def cast(
    saga: Saga,
    character: Character,
    values: dict[str, Any],
    rng: random.Random | None = None,
) -> list[str]:
    """Roll the casting, write it in the Diary, and give Warping for a
    botch's zeroes."""
    rng = rng or random.Random()
    tradition, rule, casting = _chosen(character, values)
    assert tradition is not None and rule is not None and casting is not None
    level = values.get("level") or 0
    aura, realm = values.get("aura") or 0, values.get("aura_realm") or realms.HERMETIC
    pawns = values.get("vis") or 0
    score = hc.casting_score(
        character,
        tradition,
        rule,
        casting.uses,
        aura=aura,
        aura_realm=realm,
        vis_pawns=pawns,
    )
    botch_dice = hc.botch_dice(
        tradition,
        rule,
        level=level,
        vis_pawns=pawns,
        aura=aura,
        aura_realm=realm,
        realm=hc.power_realm(character, tradition, rule),
    )
    # A familiar's Golden Cord takes dice off any magic, never to none (DE
    # p. 267).
    cord = hermetic_casting.golden_cord(saga, character)
    if botch_dice > 1 and cord:
        botch_dice = max(1, botch_dice - cord)
    typed = values.get("die")
    zeroes = 0
    if rule.die == "none":
        die_text, value = "no die", 0
    elif typed is not None:
        value = max(0, int(typed))
        die_text = f"die {value} (typed)"
    elif rule.die == "simple":
        value = dice.simple_die(rng)
        die_text = f"simple die {value}"
    else:
        rolled = dice.stress_die(rng, botch_dice, saga=saga)
        value = rolled.value
        zeroes = rolled.botches if rolled.botched else 0
        die_text = f"stress die {value}" + (
            f", botched with {zeroes} zero{'' if zeroes == 1 else 's'}"
            if rolled.botched
            else ""
        )
    total = hc.casting_total(rule, int(score.total), value)
    against = "Ease Factor" if rule.against != "level" else "level"
    result = hc.outcome(rule, total, level)
    if zeroes:
        verdict = "It botches."
    elif result.works:
        verdict = "It works" + (", for a Fatigue level." if result.fatigue else ".")
    else:
        verdict = "It fails."
    line = (
        f"{casting.label} ({rule.name}): Casting Score {int(score.total)}, "
        f"{die_text}: {total} against {against} {level}. {verdict}"
    )
    told = [line]
    diaries.write(
        saga.current_year,
        saga.current_season,
        f"Cast: {casting.label}",
        line,
        characters=[character],
    )
    if zeroes:
        # A botch on a supernatural power: a Warping Point a zero (DE pp. 227, 389).
        told += seasons.gain_warping(saga, character, zeroes, rng, aura=aura)
    return notes(*(escape(t) for t in told))


def cast_form(saga: Saga, character: Character) -> Form:
    return Form(
        f"{TITLE}: {escape(character.name)}",
        lambda: fields(saga, character),
        lambda values: cast(saga, character, values),
        validate=lambda values: problem(character, values),
        save_label="Cast",
        help_id=HELP_ID,
    )
