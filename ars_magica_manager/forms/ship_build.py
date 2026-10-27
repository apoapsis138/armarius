"""More's Build a Ship on a covenant's Ships: a ship built by a
shipwright and his team, by Rego craft magic or by a Creo ritual, and
what opening her for enchantment takes (rules.ship_building; Hermetic
Projects pp. 62-67). The ship joins the Ships list and the covenant's
Diary says how she was made; a shipwright's ship is on Ahead for the
season she is finished.

Pattern: METHODS is a Strategy, reduced to a dict of the functions that
build by each way.
"""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any

from .. import diaries
from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField, pairs
from ..markup import escape
from ..models import CalendarEntry, Character, Covenant, Saga, next_season
from ..models.ships import Ship
from ..rules import dice
from ..rules import ship_building as sb
from ..rules import ships as rules
from ..rules.lab import ability_score
from . import ships as ship_forms

TITLE = "Build a Ship"
HELP_ID = "build-ship"


def _score(character: Character, name: str) -> int:
    """An Ability's score with its Puissant bonus."""
    return sum(ability_score(character, name))


def _people(saga: Saga, covenant: Covenant) -> list[Character]:
    return [c for c in saga.characters if c.covenant_id == covenant.id]


def fields(saga: Saga, covenant: Covenant) -> list[DialogField]:
    people = [(escape(c.name), c.id) for c in _people(saga, covenant)]
    shipwright = lambda v: v.get("method") == sb.SHIPWRIGHT
    workshop = lambda v: v.get("method") in (sb.SHIPWRIGHT, sb.CRAFT_MAGIC)
    return [
        DialogField("name", "Her name", "text", "", required=True),
        DialogField(
            "ship_type",
            "Like",
            "select",
            "buss",
            options=rules.type_options(),
            hint="Her size, cargo and crew, from the book's table (HP p. 54).",
        ),
        DialogField(
            "method",
            "Built by",
            "select",
            sb.SHIPWRIGHT,
            options=[(label, key) for key, label in sb.METHODS.items()],
        ),
        DialogField(
            "builder",
            "Shipwright or magus",
            "select",
            people[0][1] if people else None,
            options=people,
            allow_blank=True,
            placeholder="(choose)",
        ),
        DialogField(
            "ease",
            "Craft magic Ease Factor",
            "optint",
            None,
            hint="For a ship HP p. 63's table doesn't name: a shipwright's "
            "Ease Factor + 6 for a season's work or + 9 for a year's "
            "(Covenants p. 49). Blank: the table's.",
            show_if=lambda v: v.get("method") == sb.CRAFT_MAGIC,
        ),
        DialogField(
            "innovation",
            "Workshop Innovation",
            "int",
            0,
            show_if=workshop,
        ),
        DialogField(
            "raw_materials", "Workshop Raw Materials", "int", 0, show_if=workshop
        ),
        DialogField(
            "in_aura",
            "In a supernatural aura",
            "check",
            False,
            show_if=workshop,
        ),
        DialogField(
            "carpenter",
            "Conscientious Carpenter",
            "check",
            False,
            show_if=shipwright,
        ),
        DialogField(
            "quality",
            "The template's quality",
            "select",
            "Superior",
            options=pairs(("Standard", "Superior", "Excellent")),
            show_if=lambda v: v.get("method") == sb.CREO_RITUAL,
        ),
        *(
            DialogField(f"part_{key}", f"With her {label.lower()}", "check", False)
            for key, (label, _) in sb.PARTS.items()
        ),
    ]


def _builder(saga: Saga, values: dict[str, Any]) -> Character | None:
    return saga.character(values.get("builder"))


def _size(values: dict[str, Any]) -> int:
    found = rules.SHIP_TYPES.get(str(values.get("ship_type") or ""))
    return found.size if found is not None else 5


def _parts(values: dict[str, Any]) -> list[str]:
    return [key for key in sb.PARTS if values.get(f"part_{key}")]


def _workshop_total(builder: Character, values: dict[str, Any]) -> tuple[int, int]:
    score = _score(builder, sb.PROFESSION)
    total = (
        builder.characteristics.intelligence
        + score
        + int(values.get("innovation") or 0)
        + int(values.get("raw_materials") or 0)
    )
    return total, score


def _opening_lines(values: dict[str, Any]) -> list[str]:
    size = _size(values)
    hull = sb.hull_pawns(size)
    lines = [
        f"Opened as her hull alone: {hull} pawns of Vim (Magic Theory "
        f"{sb.theory_needed(hull)} to do it in a season)."
    ]
    parts = _parts(values)
    if parts:
        most, all_ = sb.opening(size, parts)
        lines.append(
            f"As a compound device with her {', '.join(sb.PARTS[p][0].lower() for p in parts)}: "
            f"{most} pawns for the costliest part, or {all_} for them all "
            f"(Magic Theory {sb.theory_needed(all_)}) (HP pp. 66-67)."
        )
    return lines


def live(saga: Saga) -> Callable[[dict[str, Any]], str]:
    def inspect(values: dict[str, Any]) -> str:
        builder = _builder(saga, values)
        method = values.get("method") or sb.SHIPWRIGHT
        lines: list[str] = []
        if builder is not None and method == sb.SHIPWRIGHT:
            total, score = _workshop_total(builder, values)
            seasons = sb.seasons_to_build(score + (1 if values.get("carpenter") else 0))
            quality = sb.workshop_quality(total, bool(values.get("in_aura"))) or "none"
            lines.append(
                f"Workshop Total {total}: {quality}. "
                + (
                    f"{seasons} season(s) to build her."
                    if seasons
                    else f"{escape(builder.name)} has no {sb.PROFESSION}."
                )
            )
        elif builder is not None and method == sb.CRAFT_MAGIC:
            base = builder.characteristics.perception + _score(builder, "Finesse")
            ease = _ease(values)
            total = _workshop_total(builder, values)[0]
            quality = sb.workshop_quality(total, bool(values.get("in_aura"))) or "none"
            lines.append(
                f"Perception + Finesse {base} + a stress die against "
                + (str(ease) if ease is not None else "the Ease Factor typed")
                + f"; his Workshop Total {total} makes her {quality} (HP p. 63)."
            )
        elif builder is not None:
            base = builder.characteristics.intelligence + _score(builder, "Finesse")
            lines.append(
                f"Intelligence + Finesse {base} + a stress die against {sb.RITUAL_EASE}."
            )
        lines += _opening_lines(values)
        return escape("\n".join(lines))

    return inspect


def _ease(values: dict[str, Any]) -> int | None:
    typed = values.get("ease")
    if typed is not None:
        return int(typed)
    return sb.craft_magic_ease(str(values.get("ship_type") or ""))


def problem(saga: Saga, values: dict[str, Any]) -> str | None:
    builder = _builder(saga, values)
    if builder is None:
        return "Choose who builds her."
    if values.get("method") == sb.CRAFT_MAGIC and _ease(values) is None:
        return (
            "HP p. 63's table names a river barge, coastal buss, large cog and "
            "grain barge: type her craft magic Ease Factor (Covenants p. 49)."
        )
    if values.get("method") == sb.SHIPWRIGHT and not _score(builder, sb.PROFESSION):
        return f"{builder.name} has no {sb.PROFESSION}."
    return None


def _by_shipwright(
    saga: Saga, builder: Character, values: dict[str, Any], rng: random.Random
) -> tuple[str, int, int, str]:
    """(quality, Excellent bonus, seasons, what it says)."""
    total, score = _workshop_total(builder, values)
    in_aura = bool(values.get("in_aura"))
    seasons = sb.seasons_to_build(score + (1 if values.get("carpenter") else 0))
    quality = sb.workshop_quality(total, in_aura) or "Shoddy"
    bonus = sb.excellent_bonus(total, score, in_aura) if quality == "Excellent" else 0
    return (
        quality,
        bonus,
        seasons,
        f"{builder.name}'s Workshop Total {total} makes her {quality}; "
        f"{seasons} season(s) to build.",
    )


def _by_magic(
    saga: Saga,
    builder: Character,
    values: dict[str, Any],
    rng: random.Random,
    ritual: bool,
) -> tuple[str, int, int, str]:
    trait = (
        builder.characteristics.intelligence
        if ritual
        else builder.characteristics.perception
    )
    base = trait + _score(builder, "Finesse")
    ease = sb.RITUAL_EASE if ritual else (_ease(values) or 0)
    die = dice.stress_die(rng, 1, saga=saga)
    total = base + die.value
    made = not die.botched and total >= ease
    bonus = 0
    if not made:
        quality = ""
    elif ritual:
        quality = str(values.get("quality") or "Superior")
    else:
        # Led by a Hermetic shipwright: his Profession and the workshop
        # (HP p. 63).
        workshop, score = _workshop_total(builder, values)
        in_aura = bool(values.get("in_aura"))
        quality = sb.workshop_quality(workshop, in_aura) or "Shoddy"
        if quality == "Excellent":
            bonus = sb.excellent_bonus(workshop, score, in_aura)
    said = (
        f"{'Intelligence' if ritual else 'Perception'} + Finesse {base} + die "
        f"{die.value} = {total} against {ease}: "
        + (
            "she is made."
            if made
            else ("a botch: no ship." if die.botched else "no ship.")
        )
    )
    return quality, bonus, 0, said


METHODS: dict[
    str,
    Callable[
        [Saga, Character, dict[str, Any], random.Random], tuple[str, int, int, str]
    ],
] = {
    sb.SHIPWRIGHT: _by_shipwright,
    sb.CRAFT_MAGIC: lambda s, b, v, r: _by_magic(s, b, v, r, ritual=False),
    sb.CREO_RITUAL: lambda s, b, v, r: _by_magic(s, b, v, r, ritual=True),
}


def build(
    saga: Saga, covenant: Covenant, values: dict[str, Any], rng: random.Random
) -> list[str]:
    builder = _builder(saga, values)
    assert builder is not None
    method = str(values.get("method") or sb.SHIPWRIGHT)
    quality, bonus, seasons, said = METHODS[method](saga, builder, values, rng)
    name = str(values.get("name") or "").strip()
    lines = [said, *_opening_lines(values)]
    if quality:
        kind = rules.SHIP_TYPES[str(values.get("ship_type"))]
        record = ship_forms.save_ship(
            covenant,
            None,
            {
                "name": name,
                "ship_type": kind.key,
                "kind_name": kind.name,
                "size": kind.size,
                "tons": kind.tons,
                "crew": kind.crew,
                "quality": quality,
                "excellent_bonus": bonus or Ship.excellent_bonus,
            },
        )
        lines.append(f"{record.name} joins the Ships list.")
        if seasons > 1:
            season, year = saga.current_season, saga.current_year
            for _ in range(seasons - 1):
                season, year = next_season(season, year)
            saga.calendar.append(
                CalendarEntry(
                    f"{name} is finished", year, season, covenant_id=covenant.id
                )
            )
            lines.append(f"She is finished at the end of {season} {year} (on Ahead).")
    diaries.write(
        saga.current_year,
        saga.current_season,
        f"{TITLE}: {name}",
        " ".join([*lines, f"Rules: {sb.SOURCE}."]),
        covenants=[covenant],
    )
    return notes(*map(escape, lines))


def build_form(saga: Saga, covenant: Covenant | None) -> Command:
    if covenant is None:
        return Refuse(TITLE, "Choose a covenant first.")
    if not _people(saga, covenant):
        return Refuse(TITLE, f"{escape(covenant.name)} has no one to build her.")
    return Form(
        f"{TITLE}: {escape(covenant.name)}",
        lambda: fields(saga, covenant),
        lambda values: build(saga, covenant, values, random.Random()),
        validate=lambda values: problem(saga, values),
        live=live(saga),
        save_label="Build",
        help_id=HELP_ID,
        inspector="The Ship",
    )
