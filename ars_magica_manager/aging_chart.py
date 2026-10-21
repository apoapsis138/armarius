"""A grog's pre-play aging from the Grogs Aging Chart (rules/grog_aging.py),
applied to the character: the decades the pre-play aging rolls cover,
their Aging Points on the Characteristics, Decrepitude, apparent age, a
Diary entry, and the choice and its Ability cap noted on the Creation
Worksheet. Like the yearly rolls it stands in for, it can't be taken
back."""

from __future__ import annotations

import random
import re

from . import seasons, sourcebooks
from .models import Character, DiaryEntry, Saga, character_age
from .rules import aging as aging_rules
from .rules import creation_magus as magus
from .rules import grog_aging as rules

BOOK = "Grogs"


def cite(source: str) -> str:
    """A rule's citation without its web address, as the Diary shows one."""
    return re.sub(r"\s*\(https?://[^)]*\)\s*$", "", source)


def offered(saga: Saga, character: Character) -> bool:
    """Whether the worksheet offers the chart: a grog (not an animal, whose
    kind ages by its own table) with pre-play aging still to make, while
    the Grogs book is in play."""
    return (
        character.type == "grog"
        and character.animal is None
        and sourcebooks.in_play(BOOK, sourcebooks.saga_books(saga))
        and magus.aging_due(saga, character) > 0
    )


def _span(saga: Saga, character: Character) -> tuple[int, int]:
    """The ages the pre-play aging rolls still to make cover: (first, end),
    end not included."""
    years = character_age(character.background.year_born, saga.current_year) or 0
    done = character.creation_conditions.aged_to
    first = magus.aging_age(character) if done is None else done + 1
    return first, years


def decades(saga: Saga, character: Character, kind: rules.Kind) -> list[rules.Decade]:
    """The decades the chart covers for the character, at its covenant's
    Living Conditions."""
    first, end = _span(saga, character)
    living = seasons.living_conditions(saga, character)
    return rules.decades(
        first,
        end,
        lambda age: rules.aging_score(character, age, living, saga),
        kind,
    )


def preview(
    saga: Saga, character: Character, kind: rules.Kind, take_crises: bool
) -> list[str]:
    """What the chart would give, before it is applied: each decade, then
    the total."""
    found = decades(saga, character, kind)
    sum_up = rules.total(found, character.aging.decrepitude_points, take_crises)
    lines = [rules.decade_text(d) + "." for d in found]
    lines.append(total_text(sum_up, take_crises))
    return lines


def total_text(sum_up: rules.ChartTotal, take_crises: bool) -> str:
    if not take_crises or not sum_up.crises:
        return f"Total: {sum_up.points} Aging Point(s)."
    return (
        f"Total: {sum_up.points} Aging Point(s): {sum_up.crisis_points} for "
        f"{sum_up.crises} crisis/crises (Decrepitude {sum_up.decrepitude}), "
        f"{sum_up.chart_points} from the chart."
    )


def cap_text(change: int) -> str:
    return {1: "Ability cap 1 higher", -1: "Ability cap 1 lower"}.get(change, "")


def apply(
    saga: Saga,
    character: Character,
    kind: rules.Kind,
    take_crises: bool,
    move_cap: bool,
    rng: random.Random,
) -> list[str]:
    """Take the chart's Aging Points for every pre-play aging roll still to
    make, in place of the rolls. Returns its notes."""
    found = decades(saga, character, kind)
    if not found:
        return []
    aging = character.aging
    sum_up = rules.total(found, aging.decrepitude_points, take_crises)
    stats = character.characteristics
    scores = {name: getattr(stats, name) for name in aging_rules.CHARACTERISTICS}
    placed = rules.placements(sum_up.chart_points, sum_up.crisis_points, scores)
    applied = rules.place_points(
        placed, scores, aging.aging_points, aging_rules.unaging(character)
    )
    for name, score in scores.items():
        setattr(stats, name, score)
    aging.decrepitude_points += sum_up.points
    aging.decrepitude = aging_rules.decrepitude_score(aging.decrepitude_points)
    apparent = (
        aging.apparent_age if aging.apparent_age is not None else found[0].first - 1
    )
    notes = [f"The Grogs Aging Chart, {kind} aging:"]
    for decade, (die, years) in zip(
        found, rules.roll_apparent(found, rng), strict=True
    ):
        apparent += years
        notes.append(f"{rules.decade_text(decade)}; apparent age +{years} (die {die}).")
    aging.apparent_age = apparent
    notes.append(total_text(sum_up, take_crises))
    if applied.gained:
        gained = ", ".join(f"{n.title()} {p}" for n, p in applied.gained.items())
        notes.append(f"Aging Points: {gained}.")
    notes += applied.notes
    notes.append(f"Apparent age {apparent}; Decrepitude {aging.decrepitude}.")
    conditions = character.creation_conditions
    conditions.aged_to = found[-1].last
    conditions.aging_chart = kind
    conditions.aging_chart_cap = rules.CAP_CHANGE[kind] if move_cap else 0
    if cap := cap_text(conditions.aging_chart_cap):
        notes.append(f"{cap} at creation.")
    born = character.background.year_born or saga.current_year
    character.diary.append(
        DiaryEntry(
            year=born + found[-1].last,
            season="Winter",
            name=f"Pre-play aging, the Grogs Aging Chart ({kind}): "
            f"{sum_up.points} Aging Point(s)",
            details="\n".join(notes) + f"\nRule: {cite(rules.SOURCE)}",
            activity="Aging",
        )
    )
    return notes


def worksheet_text(character: Character) -> str:
    """The worksheet's note of the chart's use ("" when it wasn't used)."""
    conditions = character.creation_conditions
    if not conditions.aging_chart:
        return ""
    cap = cap_text(conditions.aging_chart_cap)
    return f"the Grogs Aging Chart, {conditions.aging_chart} aging" + (
        f" ({cap})" if cap else ""
    )
