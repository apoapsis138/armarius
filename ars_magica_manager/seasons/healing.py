"""The season's healing: every wounded character's Recovery rolls, their
bruises' residual wounds, and Fatigue rested away (rules.recovery,
rules.harm), each written in the Diary."""

from __future__ import annotations

import random

from ..health import season_text
from ..models import DiaryEntry, Saga, SeasonRecordLine
from ..rules import harm, recovery
from ..world import takes_part_in_play


def season_healing(saga: Saga, rng: random.Random) -> list[SeasonRecordLine]:
    """This season's healing for every character in play: a record line for
    each one who had wounds to heal."""
    lines: list[SeasonRecordLine] = []
    for character in saga.characters:
        if not takes_part_in_play(character) or character.wounds.dead:
            continue
        bruised = harm.heal_bruises(character)
        had = bool(recovery.states(character.wounds))
        played = recovery.season(saga, character, rng)
        if not had and not bruised:
            continue
        details = "\n".join([*bruised, season_text(character, played)]).strip()
        left = recovery.states(character.wounds)
        summary = (
            "died of their wounds"
            if played.died
            else ", ".join(
                f"{sum(s.severity == sev for s in left)} {sev.title()}"
                for sev in recovery.SEVERITIES
                if any(s.severity == sev for s in left)
            )
            or "healed"
        )
        character.diary.append(
            DiaryEntry(
                year=saga.current_year,
                season=saga.current_season,
                name=f"Recovery: {summary}",
                details=f"{details}\nRule: {recovery.SOURCE}",
                activity="Recovery",
            )
        )
        lines.append(
            SeasonRecordLine(
                character.id,
                character.name,
                character.covenant_id,
                "Recovery",
                "",
                summary,
            )
        )
    return lines
