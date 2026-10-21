"""The covenant Seasons tab as a board: people down, the year to plan
across, and each companion's working seasons this year."""

from __future__ import annotations

from support import everything_saga

from ars_magica_manager import seasons
from ars_magica_manager.models import DiaryEntry, SeasonPlan, XpAllocation
from ars_magica_manager.rules import activities as rules


def _exposure(character_id: str, season: str) -> SeasonPlan:
    return SeasonPlan(
        character_id, 1220, season, rules.EXPOSURE, [XpAllocation("ability:Latin")]
    )


def test_the_board_shows_each_season_of_the_year():
    saga = everything_saga()
    covenant = saga.covenants[0]
    seasons.set_plan(saga, _exposure("mag1", "Autumn"))
    board = seasons.season_board(saga, covenant, "magus")
    assert board.columns == [
        "Name", "Spring 1220", "Summer 1220", "Autumn 1220", "Winter 1220",
    ]  # fmt: skip
    assert board.rows == [
        ["Leandro", "nothing", "nothing", "Work / Exposure", "nothing"]
    ]
    # This season's gap stands out; the later ones are dim.
    assert board.styles[(0, 1)] == "$text-warning"
    assert board.styles[(0, 2)] == "dim"


def test_a_companion_counts_their_working_seasons_this_year():
    saga = everything_saga()
    covenant = saga.covenants[0]
    saga.current_season = "Summer"
    alys = saga.character("comp1")
    assert alys is not None
    alys.diary.append(
        DiaryEntry(name="Work", year=1220, season="Spring", activity="Work / Exposure")
    )
    seasons.set_plan(saga, _exposure("comp1", "Winter"))
    board = seasons.season_board(saga, covenant, "companion")
    assert board.columns[-1] == "Worked"
    assert board.rows[0][0] == "Alys" and board.rows[0][-1] == "2 of 2"


def test_the_details_list_the_seasons_ahead():
    saga = everything_saga()
    seasons.set_plan(saga, _exposure("mag1", "Summer"))
    text = seasons.season_info_text(saga, saga.character("mag1"))
    assert "Seasons ahead" in text and "Summer 1220: Work / Exposure: Latin" in text
    assert "Autumn 1220: [dim]nothing[/]" in text
