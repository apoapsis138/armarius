"""Story Flaw spotlight: Needs You names a player character whose Story
or Major Personality Flaw has waited the saga's span for a story (DE p. 66)."""

from ars_magica_manager import attention, catalog, spotlight
from ars_magica_manager.models import (
    STORY_EVENT,
    Character,
    Covenant,
    CovenantDiaryEntry,
    Saga,
    SeasonRecord,
    VirtueFlawInstance,
)


def _flaw(category: str, tier: str) -> str:
    known = catalog.load_virtue_flaw_catalog_by_id()
    return next(
        v.id
        for v in known.values()
        if v.type == "Flaw"
        and v.category == category
        and v.tier == tier
        and not v.parameters
    )


def _saga(category: str = "Story", tier: str = "Major") -> Saga:
    saga = Saga(id="s", name="Saga", current_year=1225)
    hero = Character(id="h", name="Hugo", type="companion", covenant_id="c")
    hero.background.player_ids = ["ana"]
    hero.virtues_flaws.append(VirtueFlawInstance(_flaw(category, tier)))
    saga.characters = [hero]
    saga.covenants = [Covenant(id="c", saga_id="s", name="Fengheld", played=True)]
    saga.season_records = [SeasonRecord(1220, "Spring")]
    return saga


def _spot(saga: Saga) -> list[str]:
    return [i.title for i in attention.items(saga) if i.need == attention.SPOTLIGHT]


def test_a_story_flaw_with_no_told_story_since_the_saga_began_is_named():
    saga = _saga()
    [title] = _spot(saga)
    assert title.startswith("Hugo: ")


def test_a_told_story_about_them_within_the_span_keeps_them_off():
    saga = _saga()
    saga.covenants[0].diary = [
        CovenantDiaryEntry(
            1223,
            name="Hugo's oath",
            category=STORY_EVENT,
            status="Resolved",
            concerns="characters:h",
        )
    ]
    assert _spot(saga) == []
    saga.current_year = 1226
    assert len(_spot(saga)) == 1


def test_a_minor_personality_flaw_does_not_call_and_zero_turns_it_off():
    assert _spot(_saga("Personality", "Minor")) == []
    assert len(_spot(_saga("Personality", "Major"))) == 1
    saga = _saga()
    saga.story_flaw_years = 0
    assert spotlight.waiting(saga) == []
