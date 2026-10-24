"""The season's healing: every wounded character's Recovery rolls, their
bruises' residual wounds, and Fatigue rested away (rules.recovery,
rules.harm), each written in the Diary."""

from __future__ import annotations

import random

from ..health import season_text
from ..models import DiaryEntry, Saga, SeasonRecordLine
from ..rules import disease, harm, recovery
from ..rules import living as living_rules
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
        sick = bool(character.wounds.diseases)
        living = living_rules.living_conditions(saga, character) if sick else 0
        illness = disease.season(saga, character, living, rng) if sick else []
        died_of_disease = character.wounds.dead
        played = (
            recovery.Season(died=True)
            if died_of_disease
            else recovery.season(saga, character, rng)
        )
        if not had and not bruised and not sick:
            continue
        tail = [] if died_of_disease else [season_text(character, played)]
        details = "\n".join([*bruised, *illness, *tail]).strip()
        left = recovery.states(character.wounds)
        summary = (
            "died of disease"
            if died_of_disease
            else "died of their wounds"
            if played.died
            else ", ".join(
                [
                    *(
                        f"{sum(s.severity == sev for s in left)} {sev.title()}"
                        for sev in recovery.SEVERITIES
                        if any(s.severity == sev for s in left)
                    ),
                    *(f"{d.name} ({d.level})" for d in character.wounds.diseases),
                ]
            )
            or "healed"
        )
        character.diary.append(
            DiaryEntry(
                year=saga.current_year,
                season=saga.current_season,
                name=f"Recovery: {summary}",
                details=f"{details}\nRule: {recovery.SOURCE}"
                + (f"; {disease.SOURCE}" if sick else ""),
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
