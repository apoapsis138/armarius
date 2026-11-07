"""Writing what happened into the diaries of those it touched: a
character's, a covenant's, and a neighbour's (a lord's, a place's or a
faction's, kept in its details). Battles, fights and sieges write here
when an event is recorded or the conflict ends."""

from __future__ import annotations

from collections.abc import Iterable

from . import viewing
from .models import (
    Character,
    Covenant,
    CovenantDiaryEntry,
    DiaryEntry,
    Neighbour,
    Saga,
    details_list,
)


def write_ruled(
    saga: Saga, character: Character, name: str, text: str, source: str
) -> None:
    """`text` in the character's diary under `name`, the book rule it follows
    cited after it."""
    write(
        saga.current_year,
        saga.current_season,
        name,
        f"{text} Rules: {source}.",
        characters=[character],
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
    written (each record once). A covenant's or neighbour's line is marked
    as about the neighbours, characters and creatures named, so a player
    doesn't read it while one is unknown (viewing.py)."""
    count = 0
    characters, neighbours = list(characters), list(neighbours)
    about = viewing.about(*neighbours, *characters)
    for character in _once(characters):
        character.diary.append(DiaryEntry(year, season, name, text))
        count += 1
    for covenant in _once(covenants):
        covenant.diary.append(
            CovenantDiaryEntry(year, season, name, text, about=list(about))
        )
        count += 1
    for neighbour in _once(neighbours):
        line: dict[str, object] = {
            "year": year,
            "season": season,
            "text": f"{name}: {text}",
        }
        if about:
            line["about"] = list(about)
        details_list(neighbour, "diary").append(line)
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
