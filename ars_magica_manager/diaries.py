"""Writing what happened into the diaries of those it touched: a
character's, a covenant's, and a neighbour's (a lord's, a place's or a
faction's, kept in its details). Battles, fights and sieges write here
when an event is recorded or the conflict ends."""

from __future__ import annotations

from collections.abc import Iterable

from .models import (
    Character,
    Covenant,
    CovenantDiaryEntry,
    DiaryEntry,
    Neighbour,
    details_list,
)


def write(
    year: int,
    season: str,
    name: str,
    text: str,
    *,
    characters: Iterable[Character] = (),
    covenants: Iterable[Covenant] = (),
    neighbours: Iterable[Neighbour] = (),
) -> int:
    """One line, under `name`, in each diary; returns how many were
    written (each record once)."""
    count = 0
    for character in _once(characters):
        character.diary.append(DiaryEntry(year, season, name, text))
        count += 1
    for covenant in _once(covenants):
        covenant.diary.append(CovenantDiaryEntry(year, season, name, text))
        count += 1
    for neighbour in _once(neighbours):
        details_list(neighbour, "diary").append(
            {"year": year, "season": season, "text": f"{name}: {text}"}
        )
        count += 1
    return count


def _once[R](records: Iterable[R]) -> list[R]:
    """Each record once, in order (records compare by value, so by
    identity here)."""
    seen: set[int] = set()
    found: list[R] = []
    for record in records:
        if id(record) not in seen:
            seen.add(id(record))
            found.append(record)
    return found
