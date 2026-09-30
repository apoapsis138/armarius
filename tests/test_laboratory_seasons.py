"""Work on the laboratory itself, and assisting in one (STORY-915)."""

from ars_magica_manager import seasons
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    Characteristics,
    Covenant,
    LabCharacteristics,
    Laboratory,
    Saga,
    SeasonPlan,
    Spell,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import lab_seasons
from ars_magica_manager.rules import laboratory_seasons as ls
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _saga() -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep")
    magus = Character(id="m", name="Tiberius", type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(intelligence=2, perception=1)
    magus.abilities = [Ability("Magic Theory", xp=ability_xp(5))]
    magus.arts = {"creo": ArtScore(xp=art_xp(5)), "ignem": ArtScore(xp=art_xp(5))}
    helper = Character(id="h", name="Marcus", type="companion", covenant_id="cov")
    helper.characteristics = Characteristics(intelligence=1)
    helper.abilities = [Ability("Magic Theory", xp=ability_xp(2))]
    helper.virtues_flaws = [VirtueFlawInstance("vf_the_gift")]
    lab = Laboratory(
        id="lab",
        covenant_id="cov",
        name="Tower",
        owner_id="m",
        characteristics=LabCharacteristics(refinement=1),
    )
    saga = Saga(
        id="s",
        name="S",
        covenants=[covenant],
        characters=[magus, helper],
        laboratories=[lab],
    )
    saga.spells = [Spell("bolt", "Bolt", "Creo", "Ignem", level=10)]
    return saga


def _plan(activity, **kw):
    return SeasonPlan("m", 1220, "Spring", activity, lab_id="lab", **kw)


def _run(saga):
    seasons.apply(saga, seasons.resolve(saga))


def _vfs(lab):
    return [vf.vf_id for vf in lab.virtues_flaws]


def test_setting_up_takes_two_seasons_basic_after_the_first():
    saga = _saga()
    seasons.plan_lab_work(saga, _plan(ls.BUILD))
    _run(saga)
    lab = saga.laboratories[0]
    assert _vfs(lab) == [ls.BASIC]
    assert [p.season for p in saga.season_plans] == ["Summer"]
    saga.current_season = "Summer"
    _run(saga)
    assert _vfs(lab) == []


def test_refining_raises_refinement_and_rolls_for_organization():
    saga = _saga()
    seasons.plan_lab_work(saga, _plan(ls.REFINE, die=6))  # 2 + 5 + 6 = 13
    _run(saga)
    lab = saga.laboratories[0]
    assert lab.characteristics.refinement == 2  # MT 5 >= 2 + 3
    assert _vfs(lab) == [ls.HIGHLY_ORGANIZED]


def test_refinement_needs_magic_theory():
    saga = _saga()
    saga.laboratories[0].characteristics.refinement = 2  # 3 needs MT 6
    _, work = lab_seasons.work(saga, saga.character("m"), _plan(ls.REFINE))
    assert work.refinement == 2 and "needs Magic Theory 6" in work.notes[0]


def test_a_botch_hides_a_defect():
    saga = _saga()
    seasons.plan_lab_work(saga, _plan(ls.REFINE, die=0))
    _run(saga)
    assert _vfs(saga.laboratories[0]) == [ls.HIDDEN_DEFECT]


def test_taking_over_caps_refinement_at_magic_theory_minus_3():
    saga = _saga()
    saga.laboratories[0].characteristics.refinement = 4
    _, work = lab_seasons.work(saga, saga.character("m"), _plan(ls.TAKE_OVER))
    assert (work.refinement, work.old_refinement) == (2, 4)


def test_an_assistant_adds_int_and_magic_theory():
    saga = _saga()
    seasons.set_plan(saga, SeasonPlan("h", 1220, "Spring", ls.ASSIST, teacher_id="m"))
    helper = saga.character("h")
    found = ls.assist_problems(saga, helper, saga.season_plans[0])
    assert found == ["Tiberius has no lab work planned for Spring 1220."]
    seasons.set_plan(saga, _plan(lab_seasons.INVENT, spell_id="bolt"))
    _, work = lab_seasons.work(
        saga, saga.character("m"), _plan(lab_seasons.INVENT, spell_id="bolt")
    )
    # CrIg 5 + 5 + 2 + 5 = 17, + Marcus 1 + 2.
    assert int(work.lab_total.total) == 20
    _run(saga)
    mt = next(a for a in helper.abilities if a.name == "Magic Theory")
    assert mt.xp == ability_xp(2) + 2


def test_moving_by_mundane_means_takes_three_seasons():
    saga = _saga()
    seasons.plan_lab_work(saga, _plan(ls.MOVE, title="the new tower"))
    lab = saga.laboratories[0]
    for season in ("Spring", "Summer", "Autumn"):
        saga.current_season = season
        _run(saga)
    assert (lab.location, lab.move_seasons) == ("the new tower", 0)
    assert "broke two years' maintenance" in lab.diary[-1].details


def test_moving_by_spell_can_leave_it_disorganized():
    saga = _saga()
    # Perception 1 + Finesse 0 + die 3 = 4 against 9 + 3 x Refinement 1.
    seasons.plan_lab_work(
        saga, _plan(ls.MOVE, title="the cellar", by_spell=True, die=3)
    )
    _run(saga)
    lab = saga.laboratories[0]
    assert lab.location == "the cellar"
    assert _vfs(lab) == [ls.DISORGANIZED]


def test_hermetic_taming_until_the_points_reach_its_might():
    from ars_magica_manager.rules import lab_seasons as labs

    saga = _saga()
    magus = saga.character("m")
    magus.arts["rego"] = ArtScore(xp=art_xp(8))
    magus.arts["animal"] = ArtScore(xp=art_xp(6))
    # ReAn 8 + 6 + Int 2 + MT 5 = 21 - Might 15 = 6 a season: 3 seasons.
    plan = _plan(labs.TAMING, title="Grey Wolf", form="Animal", book_level=15)
    added = seasons.plan_lab_work(saga, plan)
    assert [p.season for p in added] == ["Summer", "Autumn"]
    for season in ("Spring", "Summer", "Autumn"):
        saga.current_season = season
        _run(saga)
    (record,) = magus.progress
    assert record.done and record.points == 18
    assert saga.books[-1].name == "Lab Text: taming Grey Wolf"
