"""A chapter's cast and its aftermath: the Adventure written as plans
(DE pp. 376-377), days away for a magus who keeps his lab work (p. 265),
story experience for a grog (Grogs p. 67)."""

from ars_magica_manager import attention, commands, story_aftermath, story_chapters
from ars_magica_manager.models import (
    STORY_EVENT,
    Ability,
    ArtScore,
    Character,
    Covenant,
    CovenantDiaryEntry,
    Saga,
    SeasonPlan,
)
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.seasons.plans import plan_for


def _saga() -> tuple[Saga, Covenant, CovenantDiaryEntry]:
    saga = Saga(id="s", name="Saga", current_year=1221, current_season="Summer")
    covenant = Covenant(id="c", saga_id="s", name="Fengheld", played=True)
    story = CovenantDiaryEntry(
        1221, name="The Black Tower", category=STORY_EVENT, status="Open"
    )
    covenant.diary = [story]
    magus = Character(id="m", name="Aelfric", type="magus", covenant_id="c")
    magus.arts["ignem"] = ArtScore(xp=10)
    magus.abilities.append(Ability("Brawl", xp=5))
    grog = Character(id="g", name="Gus", type="grog", covenant_id="c")
    grog.abilities.append(Ability("Brawl", xp=5))
    saga.covenants = [covenant]
    saga.characters = [magus, grog]
    return saga, covenant, story


def _run(step: object, *answers: dict) -> object:
    for values in answers:
        assert isinstance(step, commands.Form), step
        filled = {f.key: f.value for f in step.fields()}
        filled.update(values)
        problem = step.validate(filled) if step.validate else None
        assert problem is None, problem
        step = step.apply(filled)
    return step


def _take_up(saga: Saga, covenant: Covenant, story: CovenantDiaryEntry) -> object:
    return story_chapters.take_up_story(saga, covenant, story)


def test_the_cast_goes_on_to_the_adventure_as_plans_and_story_experience():
    saga, covenant, story = _saga()
    end = _run(
        _take_up(saga, covenant, story),
        {"words": "Up the tower", "went_m": True, "went_g": True, "days": 10},
        {"quality": 8},
        {
            "subject_0": "art:ignem",
            "points_0": 5,
            "subject_1": "ability:Brawl",
            "points_1": 3,
        },
        {"subject_0": "ability:Brawl", "points_0": 5},
    )
    assert isinstance(end, list)
    magus, grog = saga.characters
    plan = plan_for(saga, magus, "Summer", 1221)
    assert plan is not None and plan.activity == rules.ADVENTURE
    assert plan.source_quality == 8
    assert {(a.subject, a.points) for a in plan.allocations} == {
        ("art:ignem", 5),
        ("ability:Brawl", 3),
    }
    assert grog.abilities[0].xp == 10
    [chapter] = [e for e in covenant.diary if e.category == "Chapter"]
    assert chapter.cast == ["m", "g"] and chapter.days == 10 and chapter.closed


def test_a_second_chapter_in_the_season_updates_the_adventure_never_doubles_it():
    saga, covenant, story = _saga()
    for quality, points in ((6, 4), (9, 5)):
        _run(
            _take_up(saga, covenant, story),
            {"words": "Again", "went_m": True},
            {"quality": quality},
            {"subject_0": "art:ignem", "points_0": points},
        )
    adventures = [p for p in saga.season_plans if p.activity == rules.ADVENTURE]
    [plan] = adventures
    assert plan.source_quality == 9
    assert [(a.subject, a.points) for a in plan.allocations] == [("art:ignem", 5)]


def test_a_magus_keeping_his_lab_work_has_the_days_away_added():
    saga, covenant, story = _saga()
    saga.season_plans.append(SeasonPlan("m", 1221, "Summer", "vis_study"))
    _run(
        _take_up(saga, covenant, story),
        {"words": "A short ride", "went_m": True, "days": 7},
        {"quality": 5, "take_m": story_aftermath.LAB},
    )
    plan = plan_for(saga, saga.characters[0], "Summer", 1221)
    assert plan is not None and plan.activity == "vis_study" and plan.days_away == 7


def test_more_than_five_to_one_subject_is_refused():
    values = {"subject_0": "art:ignem", "points_0": 6}
    assert story_aftermath.subject_problem(values, 8) is not None
    values = {
        "subject_0": "art:ignem",
        "points_0": 5,
        "subject_1": "ability:Brawl",
        "points_1": 5,
    }
    assert "more than the Source Quality" in (
        story_aftermath.subject_problem(values, 8) or ""
    )


def test_a_cancelled_aftermath_leaves_the_chapter_on_needs_you():
    saga, covenant, story = _saga()
    step = _run(_take_up(saga, covenant, story), {"words": "Up", "went_m": True})
    assert isinstance(step, commands.Form)  # the aftermath, not answered
    closes = [i for i in attention.items(saga) if i.need == attention.CLOSE]
    assert len(closes) == 1 and closes[0].take_up is not None
    assert "went: Aelfric" in "\n".join(
        story_chapters.story_thread(saga, covenant, story)
    )
