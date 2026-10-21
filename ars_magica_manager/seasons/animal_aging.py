"""An animal grog's aging rolls as the seasons pass: as many each season
as its kind makes (rules.animal_aging: five a year for a clawed beast,
one each season and two in Winter; two for a hoofed beast, in Summer and
Winter; one every two or five years for a bird or a fish, in Winter),
from the age its aging starts, or at any age under a Longevity Ritual.
Each roll is the ordinary one (character_effects.age_character),
written in the Diary.
"""

from __future__ import annotations

import random

from ..models import Saga, SeasonRecordLine
from ..rules import animal_aging
from ..world import takes_part_in_play
from .character_effects import age_character


def season_aging(saga: Saga, rng: random.Random) -> list[SeasonRecordLine]:
    """This season's aging rolls for every animal grog in play: a record
    line for each roll."""
    lines: list[SeasonRecordLine] = []
    for character in saga.characters:
        start = animal_aging.start_age(character)
        born = character.background.year_born
        if start is None or born is None or not takes_part_in_play(character):
            continue
        age = saga.current_year - born
        if age < start and character.aging.longevity_modifier <= 0:
            continue
        rolls = animal_aging.rolls_in_season(character, age, saga.current_season)
        lines += [age_character(saga, character, age, rng) for _ in range(rolls)]
    return lines
