"""More's forms for an apprentice's end: The Gauntlet (a story judged,
passed without one, or rolled), Lose the Gift, and Learn a Cantation (a
spontaneous spell learned by casting it, a saga option) -- no UI in here.
The rules and their pages are rules.gauntlet's (Apprentices pp. 44-48,
58-61)."""

from __future__ import annotations

import random
from typing import Any

from .. import sourcebooks
from .. import spells as spl
from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import BULLET, escape
from ..models import Character, DiaryEntry, KnownSpell, Saga, Spell
from ..rules import gauntlet as gt

GAUNTLET_TITLE = "The Gauntlet"
GAUNTLET_HELP = "gauntlet"
LOSE_TITLE = "Lose the Gift"
LOSE_HELP = "lose-the-gift"
CANTATION_TITLE = "Learn a Cantation"
CANTATION_HELP = "learn-cantation"


def _bullets(lines: list[str]) -> str:
    return "\n".join(f"{BULLET} {escape(line)}" for line in lines)


def _int(values: dict[str, Any], key: str) -> int:
    value = values.get(key)
    return value if isinstance(value, int) else 0


# ---------------------------------------------------------------------------
# The Gauntlet


def _method(values: dict[str, Any]) -> str:
    return str(values.get("method") or gt.STORY)


def _abilities(character: Character) -> list[tuple[str, str]]:
    names = sorted({a.name for a in character.abilities if a.name})
    if "Magic Theory" not in names:
        names.insert(0, "Magic Theory")
    return [(name, name) for name in names]


def gauntlet_fields(character: Character) -> list[DialogField]:
    return [
        DialogField(
            "method",
            "How it is decided",
            "select",
            gt.STORY,
            options=[(label, key) for key, label in gt.METHODS.items()],
            hint="Each parens sets his own test, passed to his satisfaction "
            "(Apprentices pp. 59-60).",
        ),
        DialogField(
            "verdict",
            "The parens' verdict",
            "select",
            gt.PASS,
            options=[("Passed", gt.PASS), ("Failed", gt.FAIL)],
            show_if=lambda v: _method(v) == gt.STORY,
        ),
        DialogField(
            "ability",
            "Ability tested",
            "select",
            "Magic Theory",
            options=_abilities(character),
            hint="One fitting his House (the Houses of Hermes summary, DE).",
            show_if=lambda v: _method(v) == gt.ROLLED,
        ),
        DialogField("test", "The test", "text", "", placeholder="What he was set"),
    ]


def gauntlet_lines(
    saga: Saga, character: Character, values: dict[str, Any]
) -> list[str]:
    method = _method(values)
    lines = gt.gauntlet_notes(saga, character)
    if method == gt.ROLLED:
        ability = str(values.get("ability") or "Magic Theory")
        lines.append(
            f"Intelligence + {ability} {gt.roll_base(character, ability):+d} + "
            f"stress die against {gt.GAUNTLET_EASE}; failed, another year as an "
            "apprentice; botched, something dire."
        )
    elif method == gt.AUTOMATIC:
        lines.append("He passes, having served his seasons of study.")
    lines.append(
        "Passed, Hermetic Magus replaces Apprentice and, after the Oath, "
        "Parma Magica's final key is his."
    )
    return lines


def gauntlet_problem(
    saga: Saga, character: Character, values: dict[str, Any]
) -> str | None:
    served = gt.years_served(saga, character)
    if (
        _method(values) == gt.AUTOMATIC
        and served is not None
        and served < gt.APPRENTICESHIP_YEARS
    ):
        return (
            f"{served} years served: passing without a story needs his "
            f"{gt.APPRENTICESHIP_YEARS} years of study."
        )
    return None


def take_gauntlet(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    method = _method(values)
    lines = gt.gauntlet_notes(saga, character)
    if method == gt.ROLLED:
        verdict = gt.rolled(
            saga, character, str(values.get("ability") or "Magic Theory"), rng
        )
        lines.append(verdict.line)
        passed = verdict.passed
    else:
        passed = method == gt.AUTOMATIC or values.get("verdict") == gt.PASS
        lines.append("Passed." if passed else "Failed, in his parens' judgement.")
    lines += gt.fail_gauntlet(character) if not passed else gt.pass_gauntlet(character)
    test = str(values.get("test") or "").strip()
    character.diary.append(
        DiaryEntry(
            saga.current_year,
            saga.current_season,
            gt.PASSED if passed else gt.FAILED,
            "\n".join(
                [
                    *([f"The test: {test}."] if test else []),
                    *lines,
                    f"Rules: {gt.SOURCE}",
                ]
            ),
        )
    )
    return notes(*lines)


def gauntlet_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Gauntlet on an apprentice: the verdict kept, and on a pass
    he becomes a magus."""
    if character is None:
        return Refuse(GAUNTLET_TITLE, "Choose a character first.")
    if not gt.apprentice(character):
        return Refuse(
            GAUNTLET_TITLE, "Only an apprentice (Social Status) faces the Gauntlet."
        )
    chance = rng or random.Random()
    who = character
    return Form(
        f"{GAUNTLET_TITLE}: {escape(who.name)}",
        lambda: gauntlet_fields(who),
        lambda values: take_gauntlet(saga, who, values, chance),
        validate=lambda values: gauntlet_problem(saga, who, values),
        live=lambda values: _bullets(gauntlet_lines(saga, who, values)),
        save_label="Record",
        help_id=GAUNTLET_HELP,
        inspector="The Gauntlet",
    )


# ---------------------------------------------------------------------------
# Losing the Gift


def lose_fields() -> list[DialogField]:
    return [
        DialogField(
            "how",
            "The Gift is",
            "select",
            gt.SUPPRESSED,
            options=[(label, key) for key, label in gt.LOSSES.items()],
            hint="Always the player's choice (Apprentices p. 59).",
        ),
        DialogField(
            "cause",
            "What happened",
            "text",
            "",
            required=True,
            placeholder="a lab accident, a nasty Turbulence...",
        ),
    ]


def lose_lines(character: Character, values: dict[str, Any]) -> list[str]:
    if values.get("how") == gt.LOST:
        return [
            "The Gift and its Gentle or Blatant kind are taken away: no "
            "Hermetic spells, no magic, and no use of Supernatural Virtues or "
            "Abilities."
            + (
                " Failed Apprentice (Minor) replaces Apprentice."
                if gt.apprentice(character)
                else ""
            )
        ]
    return [
        "Suppressed Gift (Major Hermetic Flaw) is added: his existing "
        "Supernatural Virtues and Abilities still work, but no new "
        "Supernatural or Hermetic Virtues while it lasts. It may return, by a "
        "story."
    ]


def lose(saga: Saga, character: Character, values: dict[str, Any]) -> list[str]:
    how = str(values.get("how") or gt.SUPPRESSED)
    cause = str(values.get("cause") or "").strip()
    lines = gt.lose_gift(character, how)
    character.diary.append(
        DiaryEntry(
            saga.current_year,
            saga.current_season,
            "The Gift lost" if how == gt.LOST else "The Gift suppressed",
            "\n".join([f"{cause}.", *lines, f"Rules: {gt.FAILING_SOURCE}"]),
        )
    )
    return notes(*lines)


def lose_gift_form(saga: Saga, character: Character | None) -> Command:
    """More's Lose the Gift on a Gifted apprentice."""
    if character is None:
        return Refuse(LOSE_TITLE, "Choose a character first.")
    if not gt.gifted(character):
        return Refuse(LOSE_TITLE, f"{escape(character.name)} has no Gift to lose.")
    who = character
    return Form(
        f"{LOSE_TITLE}: {escape(who.name)}",
        lose_fields,
        lambda values: lose(saga, who, values),
        live=lambda values: _bullets(lose_lines(who, values)),
        help_id=LOSE_HELP,
        inspector="What Changes",
    )


# ---------------------------------------------------------------------------
# Cantations learned in play


def cantation_spells(saga: Saga, character: Character) -> list[Spell]:
    """Formulaic spells he doesn't know, from books in play, by name. The
    book sets no level cap (Apprentices p. 46): having cast it as many
    times as its level is the limit. Never a Ritual spell: spontaneous
    magic can never replicate a Ritual's effect (DE p. 311)."""
    known = {k.spell_id for k in character.spells_known}
    books = sourcebooks.saga_books(saga)
    found: dict[str, Spell] = {}
    for spell, origin in spl.pickable_spells(saga):
        source = spell.source if origin == spell.source else ""
        if (
            spell.id in known
            or spell.ritual
            or spell.level is None
            or not sourcebooks.in_play(source, books)
        ):
            continue
        found.setdefault(spell.id, spell)
    return sorted(found.values(), key=lambda s: (s.name.lower(), s.id))


def cantation_fields(saga: Saga, character: Character) -> list[DialogField]:
    spells = cantation_spells(saga, character)
    return [
        DialogField(
            "spell_id",
            "The spell",
            "select",
            spells[0].id if spells else "",
            options=[(f"{s.name} ({spl.shorthand(s)})", s.id) for s in spells],
            hint="The spontaneous spell he kept casting, as a formulaic one.",
        ),
        DialogField(
            "times",
            "Times cast spontaneously",
            "int",
            0,
            hint="At least as many as its level (Apprentices p. 46).",
        ),
    ]


def _spell(saga: Saga, character: Character, values: dict[str, Any]) -> Spell | None:
    wanted = str(values.get("spell_id") or "")
    return next((s for s in cantation_spells(saga, character) if s.id == wanted), None)


def cantation_lines(
    saga: Saga, character: Character, values: dict[str, Any]
) -> list[str]:
    spell = _spell(saga, character, values)
    if spell is None:
        return ["Choose the spell."]
    level = spell.level or 0
    return [
        f"{spell.name} is level {level}: cast at least {level} times, and "
        f"{gt.cantation_cost(level)} xp of this adventure's experience, given "
        "that much less to Abilities and Arts.",
        "He knows it as a formulaic spell: cast at a casting total short of "
        "its level by under 10, it still works, for a Fatigue level.",
    ]


def cantation_problem(
    saga: Saga, character: Character, values: dict[str, Any]
) -> str | None:
    spell = _spell(saga, character, values)
    if spell is None:
        return "Choose the spell."
    return gt.cantation_problem(spell.level or 0, _int(values, "times"), False)


def learn_cantation(
    saga: Saga, character: Character, values: dict[str, Any]
) -> list[str]:
    spell = _spell(saga, character, values)
    if spell is None:
        return []
    character.spells_known.append(KnownSpell(spell.id))
    line = (
        f"{spell.name} learned by casting it {_int(values, 'times')} times: "
        f"{gt.cantation_cost(spell.level or 0)} adventure xp spent on it."
    )
    character.diary.append(
        DiaryEntry(
            saga.current_year,
            saga.current_season,
            CANTATION_TITLE,
            "\n".join([line, f"Rules: {gt.CANTATION_SOURCE}"]),
        )
    )
    return notes(line)


def cantation_form(saga: Saga, character: Character | None) -> Command:
    """More's Learn a Cantation on Known Spells, with the saga option on."""
    if character is None:
        return Refuse(CANTATION_TITLE, "Choose a character first.")
    if not gt.cantations_in_play(saga):
        return Refuse(
            CANTATION_TITLE,
            "Turn on the saga option Learning cantations in play (Apprentices).",
        )
    if not cantation_spells(saga, character):
        return Refuse(CANTATION_TITLE, "No formulaic spell is left to learn.")
    who = character
    return Form(
        f"{CANTATION_TITLE}: {escape(who.name)}",
        lambda: cantation_fields(saga, who),
        lambda values: learn_cantation(saga, who, values),
        validate=lambda values: cantation_problem(saga, who, values),
        live=lambda values: _bullets(cantation_lines(saga, who, values)),
        save_label="Learn",
        help_id=CANTATION_HELP,
        inspector="The Cantation",
    )
