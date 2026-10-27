"""More's Divination and Astrology on a character -- no UI in here.

Divination: a Hermetic diviner's casual or ceremonial divination, or with
Hermetic Dream Interpreter a symbolic reading or Dream Calling; Save rolls
it, says whether it answers (and Penetrates), and writes the Diary.
Astrology: a Daily, Nativity or Periapt Horoscope, an Astrological
Duration's reckoning, a Favorable Hour, or setting a magical armillary
sphere to another place. The rules and their pages are
rules.tmre_divination's.
"""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any

from .. import diaries
from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import BULLET, escape
from ..models import Character, Saga
from ..rules import dice, lab_virtues, realms
from ..rules import gods_aid as odds
from ..rules import penetration as pen
from ..rules import tmre_divination as td

DIVINATION_TITLE = "Divination"
ASTROLOGY_TITLE = "Astrology"
HELP_DIVINATION = "tmre-divination"
HELP_ASTROLOGY = "tmre-astrology"
NO_CONNECTION = "none"

#: The sympathetic connections a ceremony may use (DE p. 220), by field key.
SYMPATHY_KEYS: tuple[tuple[str, pen.Sympathy], ...] = tuple(
    (f"sym_{index}", sympathy) for index, sympathy in enumerate(pen.SYMPATHIES)
)

DAILY, NATIVITY, PERIAPT_ROLL, DURATION, HOUR, ADJUST = (
    "daily",
    "nativity",
    "periapt",
    "duration",
    "hour",
    "adjust",
)


def _number(value: Any) -> int:
    return int(value) if value is not None else 0


def _bullets(lines: list[str]) -> str:
    return "\n".join(f"{BULLET} {escape(line)}" for line in lines)


def _diary(saga: Saga, character: Character, name: str, text: str, source: str) -> None:
    diaries.write(
        saga.current_year,
        saga.current_season,
        name,
        f"{text} Rules: {source}.",
        characters=[character],
    )


def _chance(modifiers: int, ease: int) -> str:
    return f"{odds.stress_chance(modifiers, ease) * 100:.0f}%"


# -- Divination ----------------------------------------------------------------


def offers_divination(_saga: Saga, character: Character) -> bool:
    """Whether More offers Divination: a Hermetic diviner."""
    return td.diviner(character)


def _kinds(character: Character) -> list[tuple[str, str]]:
    found = [(td.KINDS[td.CASUAL], td.CASUAL), (td.KINDS[td.CEREMONIAL], td.CEREMONIAL)]
    if td.dreamer(character):
        found += [
            (td.KINDS[td.SYMBOLIC], td.SYMBOLIC),
            (td.KINDS[td.DREAM_CALLING], td.DREAM_CALLING),
        ]
    return found


def _method_names(character: Character) -> list[str]:
    """The character's own methods, or with none named on his Virtue the
    whole table, to choose the one he follows (p. 61)."""
    return td.methods(character) or [m.name for m in td.METHODS]


def _method_options(character: Character) -> list[tuple[str, str]]:
    return [(name, name) for name in _method_names(character)]


#: A method's question field: its key, by the method's name.
QUESTION_KEY = "question_"
#: The question choice for one the table doesn't list.
OTHER_QUESTION = "other"


def _question_fields(character: Character) -> list[DialogField]:
    """For each method with uses, what the question is about: the table's
    uses and their bonus, which fills the Ceremonial bonus in (p. 61)."""
    found: list[DialogField] = []
    for name in _method_names(character):
        known = td.method(name)
        if known is None or not known.uses or known.uses[0][0] == "any question":
            continue
        options = [
            (f"{use.capitalize()} (+{bonus})", str(bonus) + ":" + use)
            for use, bonus in known.uses
        ]
        found.append(
            DialogField(
                QUESTION_KEY + name.lower(),
                "The question is about",
                "select",
                OTHER_QUESTION,
                options=[*options, ("Something else (type the bonus)", OTHER_QUESTION)],
                show_if=lambda v, n=name: (
                    _is(td.CEREMONIAL)(v) and str(v.get("method") or "") == n
                ),
                fills=_fills_from_question,
            )
        )
    return found


def _fills_from_question(values: dict[str, Any]) -> dict[str, Any]:
    method = str(values.get("method") or "").lower()
    chosen = str(values.get(QUESTION_KEY + method) or "")
    bonus, _, _ = chosen.partition(":")
    return {"ceremonial": int(bonus)} if bonus.isdigit() else {}


def _is(*kinds: str) -> Callable[[dict[str, Any]], bool]:
    return lambda values: values.get("kind", td.CEREMONIAL) in kinds


def _astrology_chosen(values: dict[str, Any]) -> bool:
    return _is(td.CEREMONIAL)(values) and td.astrology(str(values.get("method") or ""))


def _fills_bonus(values: dict[str, Any]) -> dict[str, Any]:
    """Astrology and Dream Interpretation give +5 to any question (p. 61)."""
    found = td.method(str(values.get("method") or ""))
    if found is not None and found.uses and found.uses[0][0] == "any question":
        return {"ceremonial": found.uses[0][1]}
    return {}


def divination_fields(saga: Saga, character: Character) -> list[DialogField]:
    aura, realm = realms.present_aura(saga, character)
    ceremonial = _is(td.CEREMONIAL)
    fields = [
        DialogField(
            "kind", "Divination", "select", td.CEREMONIAL, options=_kinds(character)
        ),
        DialogField(
            "ease",
            "Ease Factor",
            "int",
            0,
            show_if=_is(td.CASUAL, td.CEREMONIAL),
            hint="The level of the Momentary Intellego spell that would answer "
            "the question (any Form, any Range and Target but Sense).",
        ),
        DialogField(
            "aura",
            "Aura",
            "int",
            aura,
            show_if=_is(td.CASUAL, td.CEREMONIAL, td.DREAM_CALLING),
        ),
        DialogField(
            "aura_realm",
            "Aura's realm",
            "select",
            realm,
            options=[(r, r) for r in realms.REALMS],
            show_if=_is(td.CASUAL, td.CEREMONIAL, td.DREAM_CALLING),
        ),
        DialogField("specialty", "Divination specialty applies", "check", False),
        DialogField(
            "omens",
            "Apt omens (+0 to +3, rarely +5)",
            "int",
            0,
            show_if=_is(td.CASUAL),
            hint="The storyguide's bonus when the signs suit the question: "
            "clouds for the weather.",
        ),
        DialogField(
            "method",
            "Method",
            "select",
            _method_options(character)[0][1],
            options=_method_options(character),
            show_if=ceremonial,
            fills=_fills_bonus,
            hint=""
            if td.methods(character)
            else "His Virtue names no method: "
            "the table's (TMRE p. 61); name his on the Virtue to keep it.",
        ),
        *_question_fields(character),
        DialogField(
            "ceremonial",
            "Ceremonial bonus (+0 to +5)",
            "int",
            0,
            show_if=ceremonial,
            hint="How well the method suits the question: the Ceremonial "
            "Augury Phenomena table (TMRE p. 61).",
        ),
        DialogField(
            "connection",
            "Arcane Connection to the subject",
            "select",
            NO_CONNECTION,
            options=[("None", NO_CONNECTION)]
            + [(f"Lasting {k.lower()}", k) for k in pen.ARCANE_CONNECTIONS],
            show_if=ceremonial,
        ),
    ]
    for key, sympathy in SYMPATHY_KEYS:
        horoscope = "horoscope" in sympathy.name.lower()
        fields.append(
            DialogField(
                key,
                f"{sympathy.name} (+{sympathy.bonus})",
                "check",
                False,
                show_if=_astrology_chosen if horoscope else ceremonial,
            )
        )
    fields += [
        DialogField(
            "device_level",
            "Scrying Device's effect level",
            "int",
            0,
            show_if=ceremonial,
            hint="+1 per 10 levels, rounded up (levels for uses a day don't count).",
        ),
        DialogField(
            "resistance",
            "Magic Resistance to Penetrate",
            "optint",
            None,
            show_if=_is(td.CASUAL, td.CEREMONIAL, td.DREAM_CALLING),
            hint="Blank: none to beat.",
        ),
    ]
    return fields


def _connection(values: dict[str, Any]) -> str | None:
    chosen = str(values.get("connection") or NO_CONNECTION)
    return chosen if chosen in pen.ARCANE_CONNECTIONS else None


def _sympathies(values: dict[str, Any]) -> tuple[pen.Sympathy, ...]:
    return tuple(sympathy for key, sympathy in SYMPATHY_KEYS if values.get(key))


def divination_of(values: dict[str, Any]) -> td.Divination:
    """The form's values as a divination's circumstances."""
    return td.Divination(
        kind=str(values.get("kind") or td.CEREMONIAL),
        ease=_number(values.get("ease")),
        aura=_number(values.get("aura")),
        aura_realm=str(values.get("aura_realm") or realms.HERMETIC),
        specialty=bool(values.get("specialty")),
        omens=_number(values.get("omens")),
        method=str(values.get("method") or ""),
        ceremonial=_number(values.get("ceremonial")),
        arcane_connection=_connection(values),
        sympathies=_sympathies(values),
        device_level=_number(values.get("device_level")),
    )


def divination_problem(character: Character) -> Callable[[dict[str, Any]], str | None]:
    def problem(values: dict[str, Any]) -> str | None:
        kind = str(values.get("kind") or td.CEREMONIAL)
        if kind in (td.CASUAL, td.CEREMONIAL) and _number(values.get("ease")) < 1:
            return "Give the Ease Factor: the level of the spell that would answer."
        if kind == td.CASUAL and not 0 <= _number(values.get("omens")) <= td.OMENS_MAX:
            return f"Apt omens are +0 to +{td.OMENS_MAX}."
        if kind == td.CEREMONIAL:
            if not 0 <= _number(values.get("ceremonial")) <= td.CEREMONIAL_MAX:
                return f"The ceremonial bonus is +0 to +{td.CEREMONIAL_MAX}."
            if _number(values.get("device_level")) < 0:
                return "The Scrying Device's level can't be below 0."
            why = td.method_problem(character, str(values.get("method") or ""))
            if why:
                return why
        return None

    return problem


def _penetration(
    character: Character, divination: td.Divination, divination_total: int
) -> int:
    bonus = pen.penetration_bonus(
        character,
        arcane_connection=divination.arcane_connection,
        sympathies=[
            s
            for s in divination.sympathies
            if td.astrology(divination.method) or "horoscope" not in s.name.lower()
        ],
    )
    return td.penetration(divination_total, td.ease_of(divination), int(bonus.total))


def divination_lines(character: Character, values: dict[str, Any]) -> list[str]:
    divination = divination_of(values)
    working = td.total(character, divination)
    modifiers = int(working.total)
    terms = " + ".join(
        f"{line.label} {int(line.amount or 0):+d}" for line in working.lines
    )
    found = [f"{terms} = {modifiers:+d}, + a stress die."]
    botches = td.botch_dice(divination)
    if divination.kind == td.SYMBOLIC:
        found.append(
            "Read against the Ease Factor table: 9 the dreamer's state, 12-15 "
            "the dream's reasons, 18+ its causes and consequences (TMRE p. 63)."
        )
    else:
        ease = td.ease_of(divination)
        found.append(
            f"Against {ease}: {_chance(modifiers, ease)}, {botches} botch "
            f"{'die' if botches == 1 else 'dice'}; it makes the Ease Factor or "
            "fails (TMRE p. 62)."
        )
    if divination.kind == td.CEREMONIAL:
        found.append(
            f"The ceremony takes {td.ceremony_minutes(divination.ease)} minutes "
            "(15 a magnitude)."
        )
        known = td.method(divination.method)
        if known is not None:
            found.append(td.method_text(known) + ".")
    resistance = values.get("resistance")
    if resistance is not None and divination.kind != td.SYMBOLIC:
        typical = _penetration(character, divination, modifiers + 6)
        found.append(
            f"Penetration = the total + Penetration bonus - {td.ease_of(divination)}: "
            f"about {typical} on an average die, against Magic Resistance "
            f"{resistance}."
        )
    problem = divination_problem(character)(values)
    if problem:
        found.append(problem)
    return found


def apply_divination(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    """Roll the divination, say what it did and keep it in the Diary."""
    divination = divination_of(values)
    modifiers = int(td.total(character, divination).total)
    ease = None if divination.kind == td.SYMBOLIC else td.ease_of(divination)
    rolled = dice.roll(
        rng,
        modifiers,
        ease_factor=ease,
        botch_dice=td.botch_dice(divination),
        saga=saga,
    )
    lines = [f"{td.KINDS[divination.kind]}: {td.outcome(divination, rolled)}"]
    resistance = values.get("resistance")
    if resistance is not None and divination.kind != td.SYMBOLIC and rolled.succeeded:
        through = _penetration(character, divination, rolled.total)
        verb = (
            "Penetrates"
            if pen.penetrates(through, int(resistance))
            else "fails to Penetrate"
        )
        lines.append(f"Penetration {through}: {verb} Magic Resistance {resistance}.")
    source = (
        td.DREAM_SOURCE
        if divination.kind in (td.SYMBOLIC, td.DREAM_CALLING)
        else td.SOURCE
    )
    _diary(saga, character, DIVINATION_TITLE, " ".join(lines), source)
    return notes(*(escape(line) for line in lines))


def divination_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Divination: the roll, kept in the Diary."""
    if character is None:
        return Refuse(DIVINATION_TITLE, "Choose a character first.")
    if not offers_divination(saga, character):
        return Refuse(
            DIVINATION_TITLE,
            "Hermetic divination needs Divination & Augury or Hermetic Dream "
            "Interpreter (The Mysteries Revised Edition, p. 59).",
        )
    who, chance = character, rng or random.Random()
    return Form(
        f"{DIVINATION_TITLE}: {escape(who.name)}",
        lambda: divination_fields(saga, who),
        lambda values: apply_divination(saga, who, values, chance),
        validate=divination_problem(who),
        live=lambda values: _bullets(divination_lines(who, values)),
        save_label="Roll",
        help_id=HELP_DIVINATION,
        inspector="The Divination",
    )


# -- Astrology -----------------------------------------------------------------


def _celestial(character: Character) -> bool:
    return lab_virtues.has(character, lab_virtues.CELESTIAL)


def offers_astrology(_saga: Saga, character: Character) -> bool:
    """Whether More offers Astrology: Planetary or Celestial Magic, a
    Periapt, or divining by Astrology."""
    return (
        lab_virtues.has(character, lab_virtues.PLANETARY)
        or _celestial(character)
        or lab_virtues.has(character, td.PERIAPT)
        or any(td.astrology(name) for name in td.methods(character))
    )


def _reckonings(character: Character) -> list[tuple[str, str]]:
    found = [
        ("Daily Horoscope (an hour)", DAILY),
        ("Nativity Horoscope (a day)", NATIVITY),
    ]
    if lab_virtues.has(character, td.PERIAPT):
        found.append(("Periapt Horoscope (the season's first day)", PERIAPT_ROLL))
    if _celestial(character):
        found += [
            ("An Astrological Duration", DURATION),
            ("A Favorable Hour for spellcasting", HOUR),
        ]
    found.append(("Set a magical armillary sphere to another place", ADJUST))
    return found


def _what(*keys: str) -> Callable[[dict[str, Any]], bool]:
    return lambda values: values.get("what", DAILY) in keys


def astrology_fields(character: Character) -> list[DialogField]:
    duration = _what(DURATION)
    return [
        DialogField(
            "what", "Reckoning", "select", DAILY, options=_reckonings(character)
        ),
        DialogField(
            "duration",
            "Duration",
            "select",
            "Sun",
            options=[(f"{k} ({v})", k) for k, v in td.DURATION_UNITS.items()],
            show_if=duration,
        ),
        DialogField("units", "How many", "int", 1, show_if=duration),
        DialogField(
            "daily_horoscope",
            "Daily Horoscope for the place (-3)",
            "check",
            False,
            show_if=duration,
        ),
        DialogField(
            "measured",
            "The exact time measured (-3)",
            "check",
            False,
            show_if=duration,
            hint="By a spell such as Sight of the Astrological Hour.",
        ),
        DialogField(
            "precision",
            "Precision: an exact end (+3)",
            "check",
            False,
            show_if=duration,
        ),
        DialogField(
            "sphere",
            "Consulting a magical armillary sphere (halved)",
            "check",
            False,
            show_if=duration,
        ),
        DialogField(
            "calm",
            "Checked over a Diameter (a simple die)",
            "check",
            False,
            show_if=duration,
            hint="Needs the exact time and a Daily Horoscope or a sphere.",
        ),
        DialogField("bonus", "Bonus wanted (+1 to +5)", "int", 1, show_if=_what(HOUR)),
        DialogField(
            "lab_total",
            "Lab Total for the charged device",
            "int",
            0,
            show_if=_what(PERIAPT_ROLL),
        ),
        DialogField(
            "level",
            "The effect's level",
            "int",
            0,
            show_if=_what(PERIAPT_ROLL),
        ),
    ]


def _ease(values: dict[str, Any]) -> int:
    what = str(values.get("what") or DAILY)
    if what == DURATION:
        return td.duration_ease(
            _number(values.get("units")),
            daily_horoscope=bool(values.get("daily_horoscope")),
            measured=bool(values.get("measured")),
            precision=bool(values.get("precision")),
            sphere=bool(values.get("sphere")),
        )
    if what == HOUR:
        return td.favorable_hour_ease(_number(values.get("bonus")))
    return td.HOROSCOPE_EASE


def _calm(values: dict[str, Any]) -> bool:
    return bool(values.get("calm")) and td.calm_calculation(
        measured=bool(values.get("measured")),
        daily_horoscope=bool(values.get("daily_horoscope")),
        sphere=bool(values.get("sphere")),
    )


def astrology_problem(character: Character) -> Callable[[dict[str, Any]], str | None]:
    def problem(values: dict[str, Any]) -> str | None:
        what = str(values.get("what") or DAILY)
        if what == DURATION:
            units = _number(values.get("units"))
            if units < 1:
                return "How many units must the spell last? At least 1."
            if values.get("duration") == "Year" and units > td.MAX_SIGNS:
                return f"A spell lasts {td.MAX_SIGNS} Signs (a year) at most."
            if values.get("calm") and not _calm(values):
                return (
                    "A simple die needs the exact time and a Daily Horoscope "
                    "or a sphere."
                )
        if what == HOUR and not 1 <= _number(values.get("bonus")) <= td.BONUS_MAX:
            return f"The bonus is +1 to +{td.BONUS_MAX}."
        if what == PERIAPT_ROLL:
            level = _number(values.get("level"))
            most = td.periapt_max_level(character)
            if level > most:
                return f"A Periapt instills at most level {most} (5 x Astronomy)."
            if _number(values.get("lab_total")) < level:
                return "The Lab Total must at least equal the effect's level."
        return None

    return problem


def astrology_lines(character: Character, values: dict[str, Any]) -> list[str]:
    what = str(values.get("what") or DAILY)
    modifiers = td.astronomy_total(character)
    ease = _ease(values)
    die = "a simple die" if what == DURATION and _calm(values) else "a stress die"
    found = [
        f"Intelligence + {lab_virtues.horoscope_ability(character)} {modifiers:+d} "
        f"+ {die} against {ease}: {_chance(modifiers, ease)}."
    ]
    if what == DAILY:
        found.append(
            "A Daily Horoscope: +1 sympathetic connection today, -3 on an "
            "Astrological Duration's reckoning there (DE p. 220; TMRE p. 50)."
        )
    elif what == NATIVITY:
        found.append(
            "A Nativity Horoscope: +2 sympathetic connection; needs the "
            "subject's time and place of birth (DE p. 220)."
        )
    elif what == PERIAPT_ROLL:
        total = _number(values.get("lab_total"))
        found.append(
            f"Sound, it serves as a one-use Lab Text: {td.periapt_charges(total)} "
            f"charge(s) from Lab Total {total}; effects up to level "
            f"{td.periapt_max_level(character)}. A botch wastes the season "
            "(TMRE p. 48)."
        )
    elif what == DURATION:
        unit = td.DURATION_UNITS.get(str(values.get("duration") or "Sun"), "")
        found.append(
            f"{_number(values.get('units'))} {unit}: 6 + the units, then the "
            "options; a miss leaves it out by up to the shortfall, a botch "
            "botches the spell (TMRE pp. 49-50)."
        )
    elif what == HOUR:
        bonus = _number(values.get("bonus"))
        found.append(
            f"+{bonus} to spells in the favorable hour; a botch is -{bonus} "
            "for that hour (TMRE p. 50)."
        )
    else:
        found.append(
            "A single round, once he knows the place's conditions (Divine "
            "Heaven's Aspect); a failure may be tried again, a botch botches "
            "the spell (TMRE p. 54)."
        )
    problem = astrology_problem(character)(values)
    if problem:
        found.append(problem)
    return found


def apply_astrology(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    """Roll the reckoning, say what it did and keep it in the Diary."""
    what = str(values.get("what") or DAILY)
    stress = not (what == DURATION and _calm(values))
    rolled = dice.roll(
        rng,
        td.astronomy_total(character),
        ease_factor=_ease(values),
        stress=stress,
        saga=saga,
    )
    source = td.ASTROLOGY_SOURCE
    if what == DAILY:
        line = td.horoscope_outcome(rolled, "Daily Horoscope")
        source = td.HOROSCOPE_SOURCE
    elif what == NATIVITY:
        line = td.horoscope_outcome(rolled, "Nativity Horoscope")
        source = td.HOROSCOPE_SOURCE
    elif what == PERIAPT_ROLL:
        line = td.horoscope_outcome(rolled, "Periapt Horoscope")
        if rolled.die.botched:
            line += " The season's periapts are wasted."
        elif rolled.succeeded:
            line += (
                f" {td.periapt_charges(_number(values.get('lab_total')))} charge(s)."
            )
    elif what == DURATION:
        duration = str(values.get("duration") or "Sun")
        line = td.duration_outcome(
            rolled, _number(values.get("units")), td.DURATION_UNITS[duration]
        )
    elif what == HOUR:
        bonus = _number(values.get("bonus"))
        line = td.favorable_hour_outcome(rolled, bonus)
        if rolled.succeeded:
            line += f" The hour: hour {td.favorable_hour(rng)} after midnight."
    else:
        line = td.horoscope_outcome(rolled, "sphere's setting")
        source = td.SPHERE_SOURCE
    reckoning = next(
        (label for label, key in _reckonings(character) if key == what),
        ASTROLOGY_TITLE,
    )
    _diary(saga, character, ASTROLOGY_TITLE, f"{reckoning}: {line}", source)
    return notes(escape(f"{reckoning}: {line}"))


def astrology_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Astrology: a horoscope or reckoning rolled, kept in the Diary."""
    if character is None:
        return Refuse(ASTROLOGY_TITLE, "Choose a character first.")
    if not offers_astrology(saga, character):
        return Refuse(
            ASTROLOGY_TITLE,
            "Hermetic astrology needs Planetary Magic, Celestial Magic, a "
            "Periapt or divining by Astrology (The Mysteries Revised Edition, "
            "pp. 47-50).",
        )
    who, chance = character, rng or random.Random()
    return Form(
        f"{ASTROLOGY_TITLE}: {escape(who.name)}",
        lambda: astrology_fields(who),
        lambda values: apply_astrology(saga, who, values, chance),
        validate=astrology_problem(who),
        live=lambda values: _bullets(astrology_lines(who, values)),
        save_label="Roll",
        help_id=HELP_ASTROLOGY,
        inspector="The Reckoning",
    )
