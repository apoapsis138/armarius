"""Previously On: what happened since the last played Session, read as
the storyguide or as the Player view."""

from ars_magica_manager import print_layout, recap
from ars_magica_manager.models import (
    CHAPTER,
    Character,
    Covenant,
    CovenantDiaryEntry,
    Saga,
    SeasonRecord,
    SeasonRecordLine,
    Session,
    WorldTurn,
)


def _saga() -> Saga:
    saga = Saga(id="s", name="Saga", current_year=1222, current_season="Spring")
    hero = Character(id="h", name="Hugo", type="companion", covenant_id="c")
    hero.background.player_ids = ["ana"]
    saga.characters = [hero, Character(id="x", name="Abbot", type="companion")]
    covenant = Covenant(id="c", saga_id="s", name="Fengheld", played=True)
    covenant.diary = [
        CovenantDiaryEntry(
            1221,
            "Autumn",
            "The Black Tower",
            "Up the stair",
            category=CHAPTER,
            cast=["h"],
            session_id="last",
        )
    ]
    saga.covenants = [covenant]
    saga.sessions = [
        Session("last", played=True, played_season="Autumn", played_year=1221)
    ]
    saga.season_records = [
        SeasonRecord(1221, "Summer", [SeasonRecordLine("h", "Hugo", None, "Practice")]),
        SeasonRecord(
            1221,
            "Winter",
            [
                SeasonRecordLine("h", "Hugo", None, "Practice", result="Brawl +4 xp"),
                SeasonRecordLine("x", "Abbot", None, "Teach"),
            ],
        ),
    ]
    saga.world_turns = [WorldTurn(1221, lines=["The fair at Hildesheim: +12"])]
    return saga


def test_it_reads_from_the_last_played_session():
    found = {p.heading: p.lines for p in recap.parts(_saga())}
    assert found["The last Session's chapters"] == (
        "The Black Tower: Up the stair (Hugo)",
    )
    # Summer 1221 came before the Session; Winter came after.
    assert found["The seasons since"] == (
        "Winter 1221: Hugo: Practice, Brawl +4 xp; Abbot: Teach",
    )
    assert "What the world did" in found


def test_the_player_view_leaves_out_the_world_and_other_characters():
    found = {p.heading: p.lines for p in recap.parts(_saga(), players=True)}
    assert "What the world did" not in found
    assert found["The seasons since"] == ("Winter 1221: Hugo: Practice, Brawl +4 xp",)


def test_with_no_played_session_it_looks_back_four_seasons():
    saga = _saga()
    saga.sessions = []
    assert "last 4 seasons" in recap.lead(saga)


def test_it_prints_for_reading_aloud():
    doc = print_layout.recap_document(_saga(), players=True)
    assert doc.title == recap.TITLE
    assert any(isinstance(b, print_layout.Heading) for b in doc.blocks)
