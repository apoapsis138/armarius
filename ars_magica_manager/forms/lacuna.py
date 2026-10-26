"""More's Cast in a Lacuna on a magus's Known Spells: a spell cast in a
city, from a lacuna or in the Dominion, ceremonially or not -- the Casting
Score the place gives, the ceremony's time in its prepared space, and a
roll of it. No UI in here, and nothing kept. The rules and their pages are
rules.lacunae's (HoH:S pp. 57-60; DE pp. 99, 217-218) and rules.casting's.
"""

from __future__ import annotations

import random
from typing import Any

from .. import catalog
from .. import spells as spl
from ..arts import FORMS, TECHNIQUES
from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField, pairs
from ..markup import BULLET, escape
from ..models import Character, KnownSpell, Saga, Spell
from ..rules import casting, dice, lacunae
from ..rules.breakdown import Breakdown

TITLE = "Cast in a Lacuna"
HELP_ID = "cast-in-lacuna"
#: The spell choice for a Spontaneous spell, its Arts and level typed.
SPONTANEOUS = "spontaneous"
REALM_LABELS = {
    lacunae.NO_AURA: "No aura (the commonest)",
    "Magic": "A Magic aura",
    "Faerie": "A Faerie aura",
    "Infernal": "An Infernal aura",
}
PROP_LABELS = (
    "No props",
    "+1 gemstones and tiny items",
    "+2 small props",
    "+3 medium props",
    "+4 large props",
    "+5 props too large to move",
)


def _known(saga: Saga, magus: Character) -> list[tuple[KnownSpell, Spell]]:
    found = []
    for known in magus.spells_known:
        spell = catalog.find_spell(saga, known.spell_id)
        if spell is not None and spell.level is not None:
            found.append((known, spell))
    return found


def _chosen(
    saga: Saga, magus: Character, values: dict[str, Any]
) -> tuple[KnownSpell, Spell] | None:
    """The known spell chosen (None: a Spontaneous spell)."""
    key = values.get("spell") or SPONTANEOUS
    return next(((k, s) for k, s in _known(saga, magus) if k.spell_id == key), None)


def _int(values: dict[str, Any], key: str, default: int = 0) -> int:
    found = values.get(key)
    return found if isinstance(found, int) else default


def _may_ceremony(saga: Saga, magus: Character, values: dict[str, Any]) -> bool:
    """A Spontaneous spell, or a Formulaic one with Ceremonial Casting
    Mastery, by a magus with Artes Liberales or Philosophiae (DE pp. 218,
    226)."""
    if not casting.can_ceremonial(magus):
        return False
    chosen = _chosen(saga, magus, values)
    if chosen is None:
        return True
    known, spell = chosen
    mastery = casting.mastery_counts(known.mastery_abilities)
    return not spell.ritual and bool(mastery.get(casting.CEREMONIAL_CASTING))


def _ceremonial(saga: Saga, magus: Character, values: dict[str, Any]) -> bool:
    return bool(values.get("ceremonial")) and _may_ceremony(saga, magus, values)


def lacuna_fields(saga: Saga, magus: Character) -> list[DialogField]:
    """What Cast in a Lacuna asks."""
    spells = [
        (f"{s.name} ({s.technique} {s.form} {s.level})", k.spell_id)
        for k, s in _known(saga, magus)
    ]
    spells.append(("A Spontaneous spell", SPONTANEOUS))

    def spontaneous(values: dict[str, Any]) -> bool:
        return _chosen(saga, magus, values) is None

    def in_lacuna(values: dict[str, Any]) -> bool:
        return bool(values.get("in_lacuna"))

    def plain(values: dict[str, Any]) -> bool:
        chosen = _chosen(saga, magus, values)
        ritual = chosen is not None and chosen[1].ritual
        return not ritual and not _ceremonial(saga, magus, values)

    return [
        DialogField(
            "spell",
            "Spell",
            "select",
            spells[0][1],
            options=spells,
            required=True,
        ),
        DialogField(
            "technique",
            "Technique",
            "select",
            TECHNIQUES[0],
            options=pairs(TECHNIQUES),
            show_if=spontaneous,
        ),
        DialogField(
            "form",
            "Form",
            "select",
            FORMS[0],
            options=pairs(FORMS),
            show_if=spontaneous,
        ),
        DialogField(
            "level",
            "Level wanted",
            "int",
            5,
            show_if=spontaneous,
            hint="A fatiguing Spontaneous spell: (score + stress die) / 2.",
        ),
        DialogField(
            "city_aura",
            "The city's Dominion",
            "int",
            lacunae.CITY_DOMINION,
            hint="Most cities have a Dominion of 3: -9 to a Hermetic Casting "
            "Score (HoH:S p. 58).",
        ),
        DialogField(
            "in_lacuna",
            "Cast from a lacuna",
            "check",
            True,
        ),
        DialogField(
            "realm",
            "The lacuna's aura",
            "select",
            lacunae.NO_AURA,
            options=[(REALM_LABELS[r], r) for r in lacunae.LACUNA_REALMS],
            show_if=in_lacuna,
        ),
        DialogField(
            "lacuna_aura",
            "Its aura's strength",
            "int",
            1,
            show_if=lambda v: in_lacuna(v) and bool(v.get("realm")),
        ),
        DialogField(
            "target_in_dominion",
            "The target is within the Dominion",
            "check",
            False,
            show_if=in_lacuna,
            hint="A lacuna helps only a spell at a target outside the Dominion "
            "(HoH:S p. 57).",
        ),
        DialogField(
            "ceremonial",
            "Cast ceremonially",
            "check",
            False,
            show_if=lambda v: _may_ceremony(saga, magus, v),
            hint="+ Artes Liberales + Philosophiae and props, in place of words "
            "and gestures (DE p. 218).",
        ),
        DialogField(
            "props",
            "Props",
            "select",
            "0",
            options=[(label, str(i)) for i, label in enumerate(PROP_LABELS)],
            show_if=lambda v: _ceremonial(saga, magus, v),
        ),
        DialogField(
            "space",
            "Prepared space",
            "select",
            "none",
            options=[
                (f"{space.label} ({space.minutes} min a magnitude)", space.key)
                for space in lacunae.SPACES
            ],
            show_if=lambda v: _ceremonial(saga, magus, v),
        ),
        DialogField(
            "words",
            "Words",
            "select",
            "Firm",
            options=pairs(casting.WORDS),
            show_if=plain,
            hint="Subtle gestures and quiet words (-7) or neither (-15) keep "
            "witnesses from seeing a magus (HoH:S p. 58).",
        ),
        DialogField(
            "gestures",
            "Gestures",
            "select",
            "Bold",
            options=pairs(casting.GESTURES),
            show_if=plain,
        ),
    ]


def _validate(values: dict[str, Any]) -> str | None:
    for key, label in (
        ("city_aura", "The city's Dominion"),
        ("lacuna_aura", "An aura's strength"),
    ):
        if _int(values, key) < 0 or _int(values, key) > 10:
            return f"{label} is 0 to 10."
    if values.get("spell") == SPONTANEOUS and _int(values, "level", 1) < 1:
        return "A Spontaneous spell's level is 1 or more."
    return None


def _aura(values: dict[str, Any], *, in_lacuna: bool | None = None) -> tuple[str, int]:
    return lacunae.casting_aura(
        _int(values, "city_aura", lacunae.CITY_DOMINION),
        in_lacuna=bool(values.get("in_lacuna")) if in_lacuna is None else in_lacuna,
        lacuna_realm=str(values.get("realm") or lacunae.NO_AURA),
        lacuna_aura=_int(values, "lacuna_aura"),
        target_in_dominion=bool(values.get("target_in_dominion")),
    )


def _score(
    saga: Saga,
    magus: Character,
    values: dict[str, Any],
    realm: str,
    aura: int,
) -> Breakdown:
    ceremonial = _ceremonial(saga, magus, values)
    how: dict[str, Any] = {
        "words": str(values.get("words") or "Firm"),
        "gestures": str(values.get("gestures") or "Bold"),
        "ceremonial": ceremonial,
        "props": int(str(values.get("props") or "0")) if ceremonial else 0,
    }
    chosen = _chosen(saga, magus, values)
    if chosen is None:
        return casting.casting_score(
            magus,
            str(values.get("technique") or TECHNIQUES[0]),
            str(values.get("form") or FORMS[0]),
            aura=aura,
            aura_realm=realm,
            spontaneous=True,
            **how,
        )
    known, spell = chosen
    return casting.spell_casting_score(
        magus,
        spell,
        aura=aura,
        aura_realm=realm,
        mastery=known.mastery_score,
        mastery_abilities=casting.mastery_counts(known.mastery_abilities),
        **how,
    )


def _level(saga: Saga, magus: Character, values: dict[str, Any]) -> int:
    chosen = _chosen(saga, magus, values)
    if chosen is None:
        return max(1, _int(values, "level", 5))
    return int(chosen[1].level or 0)


def _botch_dice(
    saga: Saga, magus: Character, values: dict[str, Any], realm: str, aura: int
) -> int:
    chosen = _chosen(saga, magus, values)
    mastery = chosen[0].mastery_score if chosen is not None else 0
    vis = (spl.vis_cost(chosen[1]) or 0) if chosen is not None else 0
    return casting.botch_dice(
        vis_pawns=vis,
        aura_realm=realm,
        aura=aura,
        mastery=mastery,
        golden_cord=casting.golden_cord(saga, magus),
        virtues_flaws=magus.virtues_flaws,
        magus=magus,
        saga=saga,
    )


def _aura_text(realm: str, aura: int) -> str:
    if realm == lacunae.DOMINION:
        return f"the Dominion {aura}"
    if not aura:
        return "no aura"
    return f"a {realm} aura of {aura}"


def lines(saga: Saga, magus: Character, values: dict[str, Any]) -> list[str]:
    """What the casting is, plain."""
    realm, aura = _aura(values)
    score = int(_score(saga, magus, values, realm, aura).total)
    level = _level(saga, magus, values)
    said = [f"Casting Score {score} in {_aura_text(realm, aura)}."]
    if values.get("in_lacuna"):
        city_realm, city = _aura(values, in_lacuna=False)
        outside = int(_score(saga, magus, values, city_realm, city).total)
        if values.get("target_in_dominion"):
            said.append(
                "Its target is within the Dominion: the lacuna doesn't spare it "
                "the Dominion's penalty."
            )
        else:
            said.append(f"Outside the lacuna, in the Dominion: {outside}.")
    chosen = _chosen(saga, magus, values)
    if chosen is None:
        said.append(
            f"Spontaneous, fatiguing: (score + stress die) / 2 must reach {level}; "
            f"the die must reach {max(0, 2 * level - score)}."
        )
    elif chosen[1].ritual:
        said.append(
            f"Ritual: score + stress die against {level}; the die must reach "
            f"{max(0, level - score)} (long-term Fatigue as it falls short)."
        )
    else:
        said.append(
            f"Formulaic: score + die against {level}; the die must reach "
            f"{max(0, level - score)}, or {max(0, level - score - 10)} with a "
            "Fatigue level."
        )
    if _ceremonial(saga, magus, values):
        magnitudes = casting.magnitude(level)
        space = str(values.get("space") or "none")
        choreography = lacunae.has_choreography(magus)
        minutes = lacunae.ceremony_minutes(magnitudes, space, choreography)
        said.append(
            f"The ceremony: {minutes} minutes for {magnitudes} magnitude(s) "
            f"({lacunae.minutes_per_magnitude(space, choreography)} a magnitude"
            + (", Mystical Choreography" if choreography else "")
            + "); a spell no greater than the magnitudes the time spent allows."
        )
    botch = _botch_dice(saga, magus, values, realm, aura)
    said.append(f"{botch} botch {'die' if botch == 1 else 'dice'} on a stress die.")
    found = lacunae.found_areas(magus)
    if found:
        said.append(f"Lacunae found: {', '.join(found)}.")
    return said


def _live(saga: Saga, magus: Character):
    def live(values: dict[str, Any]) -> str:
        return "\n".join(
            f"{BULLET} {escape(line)}" for line in lines(saga, magus, values)
        )

    return live


def roll(
    saga: Saga, magus: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    """The casting roll, said: nothing is kept."""
    realm, aura = _aura(values)
    score = _score(saga, magus, values, realm, aura)
    level = _level(saga, magus, values)
    die = dice.stress_die(rng, _botch_dice(saga, magus, values, realm, aura), saga=saga)
    if die.botched:
        return notes(
            f"Die 0 with {die.botches} botch(es) in {_aura_text(realm, aura)}: the "
            "spell botches; each 0 is a Warping Point (DE p. 227)."
        )
    chosen = _chosen(saga, magus, values)
    if chosen is None:
        total = casting.spontaneous_total(score, die.value)
        cast = total >= level
        return notes(
            f"({int(score.total)} + {die.value}) / 2 = {total} against {level}: "
            + ("cast" if cast else "the spell fails")
            + ", for a Fatigue level."
        )
    total = casting.casting_total(score, die.value)
    if chosen[1].ritual:
        outcome = casting.ritual_outcome(total, level)
    else:
        outcome = casting.formulaic_outcome(total, level)
    cost = casting.fatigue_levels(
        outcome.fatigue,
        magus.virtues_flaws,
        "ritual" if chosen[1].ritual else "formulaic",
    )
    return notes(
        f"{int(score.total)} + {die.value} = {total} against {level}: "
        + ("cast" if outcome.cast else "the spell fails")
        + (
            f", {cost} {'long-term ' if outcome.long_term else ''}Fatigue level(s)."
            if cost
            else "."
        ),
        f"Penetration before its Ability: {total - level}." if outcome.cast else "",
    )


def lacuna_form(
    saga: Saga, magus: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Cast in a Lacuna: the calculator; Roll rolls it once."""
    if magus is None or magus.type != "magus":
        return Refuse(TITLE, "Only a magus casts Hermetic spells.")
    chance = rng or random.Random()
    caster = magus
    return Form(
        f"{TITLE}: {escape(caster.name)}",
        lambda: lacuna_fields(saga, caster),
        lambda values: roll(saga, caster, values, chance),
        validate=_validate,
        live=_live(saga, caster),
        save_label="Roll",
        cancel_label="Close",
        help_id=HELP_ID,
        inspector="The Casting",
    )
