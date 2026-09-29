"""Scores derived from xp (STORY-806): the Advancement Table and the
migration of saves that typed a score beside the xp."""

import pytest

from ars_magica_manager.models import Ability, ArtScore, Character
from ars_magica_manager.rules import xp


@pytest.mark.parametrize(
    ("score", "art_total", "ability_total"),
    [(0, 0, 0), (1, 1, 5), (2, 3, 15), (5, 15, 75), (10, 55, 275), (20, 210, 1050)],
)
def test_totals_match_the_advancement_table(score, art_total, ability_total):
    assert xp.art_xp(score) == art_total
    assert xp.ability_xp(score) == ability_total


@pytest.mark.parametrize(
    ("total", "factor", "score"),
    [(0, 1, 0), (1, 1, 1), (2, 1, 1), (14, 1, 4), (15, 1, 5), (74, 5, 4), (75, 5, 5)],
)
def test_score_is_the_highest_the_xp_pays_for(total, factor, score):
    assert xp.score_from_xp(total, factor) == score


def test_progress_keeps_the_total():
    # Magic Theory with 85 xp: score 5, and the total keeps counting (it
    # doesn't reset at 75); score 6 needs 105 in total.
    progress = xp.progress(85, xp.ABILITY_FACTOR)
    assert (progress.score, progress.total, progress.next_total) == (5, 85, 105)
    assert progress.to_next == 20


def test_negative_xp_scores_zero():
    assert xp.score_from_xp(-3, xp.ART_FACTOR) == 0
    assert xp.progress(-3, xp.ART_FACTOR).total == 0


@pytest.mark.parametrize(
    ("level", "saved_xp", "factor", "total", "ambiguous"),
    [
        (5, 75, 5, 75, False),  # a total that buys the level: kept
        (0, 0, 1, 0, False),
        (4, 0, 5, 50, False),  # no xp typed: the level's cost
        (5, 5, 1, 20, False),  # progress toward the next (5(5)): added
        (1, 1, 5, 6, False),  # Area Lore 1(1)
        (1, 20, 1, 1, True),  # neither: the typed score is kept
        (10, 12, 1, 55, True),
    ],
)
def test_migrating_a_typed_level(level, saved_xp, factor, total, ambiguous):
    assert xp.migrate_level_xp(level, saved_xp, factor) == (total, ambiguous)


def test_old_saves_migrate_on_load():
    character = Character.from_dict(
        {
            "id": "c",
            "name": "Corvinus",
            "type": "magus",
            "arts": {
                "intellego": {"level": 5, "xp": 5},
                "creo": {"level": 1, "xp": 20},
            },
            "abilities": [
                {"name": "Magic Theory", "level": 5, "xp": 75, "xp_to_next": 0},
                {"name": "Charm", "score": 2},
            ],
        }
    )
    assert character.arts["intellego"] == ArtScore(xp=20)
    assert character.arts["intellego"].level == 5
    assert character.arts["creo"].level == 1  # ambiguous: typed score kept
    assert [(a.name, a.xp, a.level) for a in character.abilities] == [
        ("Magic Theory", 75, 5),
        ("Charm", 15, 2),
    ]


def test_new_saves_store_only_xp():
    from dataclasses import asdict

    ability = Ability(name="Latin", xp=50)
    assert ability.level == 4
    assert "level" not in asdict(ability)
    assert asdict(ArtScore(xp=15)) == {"xp": 15}
