"""Story Flaw spotlight: a player character whose Story Flaw or Major
Personality Flaw no told story has concerned in a while (DE p. 66).

A Story Flaw is the player's promise to play the stories it brings, and a
Major Personality Flaw drives the character into them; with a troupe's
worth of such Flaws, any one comes up about one story in twenty (DE p. 66).
Needs You names a character with one of these Flaws when no story that
concerned them has been told (Resolved) for the saga's Story Flaw
spotlight span, `Saga.story_flaw_years` (0 turns it off).

A story counts for the character it concerns, whichever Flaw it drew on.
The years are counted from the last such story's last chapter (else the
story's own date); a character no told story has concerned yet counts from
the first season the saga recorded, else is left alone.

Pattern: one more source of Needs You (attention.register), as a plain
function."""

from __future__ import annotations

from dataclasses import dataclass

from . import catalog
from .models import CHAPTER, STORY_EVENT, Character, Saga
from .seasons.defaults import is_player_character

SOURCE = "Ars Magica Definitive Edition, Story and Personality Flaws, p. 66"

#: The default span, in years.
DEFAULT_YEARS = 3


@dataclass(frozen=True)
class Spotlight:
    """A character waiting for a story: the Flaws that call for one, and
    the year a told story last concerned them (None: never)."""

    character: Character
    flaws: tuple[str, ...]
    last: int | None


def calling_flaws(character: Character) -> list[str]:
    """The character's Story Flaws and Major Personality Flaws, by name."""
    known = catalog.load_virtue_flaw_catalog_by_id()
    found = []
    for instance in character.virtues_flaws:
        definition = known.get(instance.vf_id)
        if definition is None or definition.type != "Flaw":
            continue
        story = definition.category == "Story"
        major_personality = (
            definition.category == "Personality" and definition.tier == "Major"
        )
        if story or major_personality:
            found.append(catalog.describe_virtue_flaw(instance, known))
    return found


def last_told(saga: Saga, character: Character) -> int | None:
    """The year a told story last concerned `character`: its last chapter's
    year, else its own."""
    wanted = f"characters:{character.id}"
    years: list[int] = []
    for covenant in saga.covenants:
        for entry in covenant.diary:
            if not (
                entry.category == STORY_EVENT
                and entry.concerns == wanted
                and entry.status == "Resolved"
            ):
                continue
            chapters = [
                e.year
                for e in covenant.diary
                if e.category == CHAPTER and entry.id and e.story_id == entry.id
            ]
            years.append(max([entry.year, *chapters]))
    return max(years) if years else None


def _first_recorded(saga: Saga) -> int | None:
    years = [r.year for r in saga.season_records]
    return min(years) if years else None


def waiting(saga: Saga) -> list[Spotlight]:
    """The player characters whose calling Flaws have waited the span."""
    span = saga.story_flaw_years
    if span <= 0:
        return []
    found = []
    for character in saga.characters:
        if not is_player_character(character):
            continue
        flaws = calling_flaws(character)
        if not flaws:
            continue
        last = last_told(saga, character)
        since = last if last is not None else _first_recorded(saga)
        if since is not None and saga.current_year - since >= span:
            found.append(Spotlight(character, tuple(flaws), last))
    return found
