"""Study path, book holds and teaching requests."""

from dataclasses import asdict

from ars_magica_manager import book_holds, commands, study_path, teaching
from ars_magica_manager import players as pl
from ars_magica_manager.models import (
    Ability,
    Book,
    Character,
    Covenant,
    Player,
    Saga,
    SeasonPlan,
)
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.rules import xp as xp_rules
from ars_magica_manager.seasons.plans import plan_for, waiting_text


def _saga() -> Saga:
    saga = Saga(id="s", name="Saga", current_year=1220, current_season="Spring")
    saga.covenants = [Covenant(id="c", saga_id="s", name="Fengheld", played=True)]
    student = Character(id="st", name="Aelfric", type="companion", covenant_id="c")
    student.abilities.append(Ability("Latin", xp=xp_rules.ability_xp(2)))
    student.background.player_ids = ["ana"]
    teacher = Character(id="te", name="Bruno", type="companion", covenant_id="c")
    teacher.abilities.append(Ability("Latin", xp=xp_rules.ability_xp(6)))
    teacher.abilities.append(Ability("Teaching", xp=xp_rules.ability_xp(3)))
    teacher.background.player_ids = ["ben"]
    saga.characters = [student, teacher]
    saga.players = [Player("ana", "Ana"), Player("ben", "Ben")]
    saga.books = [
        Book(
            "summa",
            "On Grammar",
            "Ability Summa",
            owner_kind="covenant",
            owner_id="c",
            ability="Latin",
            level=5,
            quality=12,
        )
    ]
    return saga


def test_a_book_held_by_another_that_season_is_refused_naming_them():
    saga = _saga()
    for season in ("Spring", "Summer"):
        saga.season_plans.append(
            SeasonPlan("te", 1220, season, rules.READ, book_id="summa")
        )
    asked = SeasonPlan("st", 1220, "Spring", rules.READ, book_id="summa")
    assert book_holds.problem(saga, asked) == (
        "On Grammar is held by Bruno until Summer 1220."
    )
    later = SeasonPlan("st", 1220, "Autumn", rules.READ, book_id="summa")
    assert book_holds.problem(saga, later) is None


def test_the_path_takes_the_best_source_each_season_and_reaches_the_goal():
    saga = _saga()
    path = study_path.find(saga, saga.characters[0], "ability:Latin", 4, 1221)
    assert path.reached
    assert path.steps[0].activity in (rules.READ, rules.TAUGHT)
    assert all(step.xp > 0 for step in path.steps)


def test_a_path_never_takes_a_book_another_holds():
    saga = _saga()
    saga.season_plans.append(
        SeasonPlan("te", 1220, "Spring", rules.READ, book_id="summa")
    )
    path = study_path.find(saga, saga.characters[0], "ability:Latin", 4, 1220)
    assert path.steps[0].book_id is None


def test_a_teacher_another_player_plays_is_asked_and_accepting_plans_both():
    saga = _saga()
    student, teacher = saga.characters
    request = teaching.ask(saga, student, teacher, "ability:Latin", "Spring", 1220)
    assert waiting_text(saga, student) == "Waiting for Bruno to teach Latin."
    before = asdict(saga)
    teaching.accept(saga, request)
    taught = plan_for(saga, student)
    assert taught is not None and taught.activity == rules.TAUGHT
    assert plan_for(saga, teacher) is not None
    assert saga.teach_requests == []
    # Ben, Bruno's Player, may write Aelfric's Taught plan as he accepts.
    kept, refused = pl.guard_changes(saga.players[1], before, asdict(saga))
    assert not [r for r in refused if r.startswith("season_plans")]
    assert len(kept["season_plans"]) == 2


def test_declining_tells_the_student():
    saga = _saga()
    student, teacher = saga.characters
    request = teaching.ask(saga, student, teacher, "ability:Latin", "Spring", 1220)
    teaching.decline(saga, request, "Busy with the abbot")
    assert waiting_text(saga, student) == (
        "Bruno declined to teach Latin (Busy with the abbot)."
    )


def test_the_requests_list_offers_the_teacher_the_ask():
    saga = _saga()
    student, teacher = saga.characters
    teaching.ask(saga, student, teacher, "ability:Latin", "Spring", 1220)
    step = teaching.requests_command(saga, teacher)
    assert isinstance(step, commands.Choose)
    [choice] = step.choices()
    assert "Aelfric asks Bruno to teach Latin" in choice.label
