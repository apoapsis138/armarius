"""Work on the laboratory itself, and assisting in one."""

import random

from ars_magica_manager import seasons
from ars_magica_manager.forms import season as season_forms
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
from ars_magica_manager.rules import activities, lab_seasons
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


def test_a_laboratory_with_no_owner_is_taken_over_from_the_sheet():
    saga = _saga()
    magus = saga.character("m")
    magus.assigned_lab_id = "lab"
    vacant = Laboratory(id="old", covenant_id="cov", name="Crucible")
    saga.laboratories.append(vacant)
    offered = {a.key for a in activities.activities_for(magus)}
    assert ls.TAKE_OVER in offered and ls.REFINE not in offered
    assert ls.can_take_over(saga, magus) == [vacant]
    values = {"activity": ls.TAKE_OVER, "take_over_lab_id": "old"}
    assert season_forms.season_plan_problem(saga, magus, values) is None
    season_forms.save_season(saga, magus, values, None, None)
    _run(saga)
    # It becomes his; the laboratory he had is left without an owner.
    assert (vacant.owner_id, magus.assigned_lab_id) == ("m", "old")
    assert saga.laboratory("lab").owner_id is None


def test_only_a_laboratory_with_no_owner_can_be_taken_over():
    saga = _saga()
    magus = saga.character("m")
    rival = Character(id="r", name="Kyrillos", type="magus", covenant_id="cov")
    saga.characters.append(rival)
    saga.laboratories.append(
        Laboratory(id="theirs", covenant_id="cov", name="Hall", owner_id="r")
    )
    assert ls.can_take_over(saga, magus) == []
    found, _ = lab_seasons.work(
        saga, magus, SeasonPlan("m", 1220, "Spring", ls.TAKE_OVER, lab_id="theirs")
    )
    assert found == [
        "Hall is Kyrillos's laboratory: only one with no owner can be taken over."
    ]
    found, _ = lab_seasons.work(
        saga, magus, SeasonPlan("m", 1220, "Spring", ls.TAKE_OVER)
    )
    assert found == ["Choose the laboratory to take over."]


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
    text = saga.books[-1]
    assert text.name == "Lab Text: taming Grey Wolf"
    # Its Technique and Form are recorded, so another magus can decode it.
    assert (text.text_kind, text.technique, text.form) == ("Other", "Rego", "Animal")


# -- work() and roll() branch by branch -----------------------------


class _Dice(random.Random):
    """A random source throwing `faces` (d10 faces, 0-9) in order."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *args, **kwargs):
        return self.faces.pop(0) if self.faces else 5


def _work(saga, plan):
    return ls.work(saga, saga.character("m"), plan, saga.laboratories[0])


def test_setting_up_needs_magic_theory_3():
    saga = _saga()
    saga.character("m").abilities = [Ability("Magic Theory", xp=ability_xp(2))]
    assert _work(saga, _plan(ls.BUILD)) == (
        ["Setting up a laboratory needs Magic Theory 3 (2)."],
        None,
    )


def test_moving_needs_somewhere_to_go():
    assert _work(_saga(), _plan(ls.MOVE)) == (
        ["Say where the laboratory is moving to."],
        None,
    )
    _, work = _work(_saga(), _plan(ls.MOVE, title="The valley"))
    magus = _saga().character("m")
    # A mundane move has no roll.
    assert ls.roll(work, magus, _plan(ls.MOVE, title="The valley"), None, None) == []


def test_the_organization_roll_with_the_dice():
    saga = _saga()
    magus = saga.character("m")
    plan = _plan(ls.REFINE)
    _, work = _work(saga, plan)
    # Int 2 + Magic Theory 5 + a stress die of 9.
    notes = ls.roll(work, magus, plan, _Dice(9), saga)
    assert notes[0].startswith("Intelligence + Magic Theory 7 + die 9 = 16")
    high = _plan(ls.REFINE, die=20)
    _, work = _work(saga, high)
    assert ls.roll(work, magus, high, None, saga) == [
        "Intelligence + Magic Theory 7 + die 20 = 27: Highly Organized; any Hidden "
        "Defect is found."
    ]
    assert work.gains_vf == [ls.HIGHLY_ORGANIZED]
    assert work.loses_vf == [ls.HIDDEN_DEFECT]


def test_taking_over_checks_the_predecessors_arrangements():
    saga = _saga()
    magus = saga.character("m")
    plan = _plan(ls.TAKE_OVER, die=5)
    _, work = _work(saga, plan)
    assert work.old_refinement == 1
    # Perception 1 + Magic Theory 5 + 2 = 8 against 3 x 1: fine (a stress
    # die's 1 would roll again, doubled).
    assert ls.roll(work, magus, plan, _Dice(2), saga) == [
        "Intelligence + Magic Theory 7 + die 5 = 12: Highly Organized."
    ]
    saga.laboratories[0].characteristics.refinement = 3
    _, work = _work(saga, plan)
    notes = ls.roll(work, magus, plan, _Dice(2), saga)
    assert notes[-1] == (
        "Perception + Magic Theory 6 + 2 < 9: the Predecessor's arrangements remain."
    )
    _, work = _work(saga, plan)
    botched = ls.roll(work, magus, plan, _Dice(0, 0), saga)
    assert botched[-1] == (
        "The storyguide's roll botched: Predecessor and a Hidden Defect."
    )
    # Highly Organized from the first roll (12), then the botch's two.
    assert work.gains_vf == [ls.HIGHLY_ORGANIZED, ls.PREDECESSOR, ls.HIDDEN_DEFECT]


def test_moving_by_spell_with_the_dice():
    saga = _saga()
    magus = saga.character("m")
    plan = _plan(ls.MOVE, title="The valley", by_spell=True)
    _, work = _work(saga, plan)
    # Perception 1 + Finesse 0 + 9, against 9 + 3 x Refinement 1 = 12.
    assert ls.roll(work, magus, plan, _Dice(9), saga)[0].endswith(
        "= 10 against 12: it arrives Disorganized (and loses Highly Organized)."
    )
    _, work = _work(saga, plan)
    moved = ls.roll(
        work, magus, _plan(ls.MOVE, title="v", by_spell=True, die=11), None, saga
    )
    assert moved == ["Perception + Finesse 1 + 11 = 12 against 12: moved."]
    _, work = _work(saga, plan)
    assert ls.roll(work, magus, plan, _Dice(0, 0), saga) == [
        "Botch: the laboratory gains a Hidden Defect."
    ]
    assert work.gains_vf == [ls.HIDDEN_DEFECT]


def test_who_can_assist():
    saga = _saga()
    helper = saga.character("h")
    assert ls.assist_problems(saga, helper, _plan(ls.ASSIST)) == [
        "Choose the magus to assist."
    ]
    plan = SeasonPlan("h", 1220, "Spring", ls.ASSIST, teacher_id="m")
    helper.virtues_flaws = []
    assert ls.assist_problems(saga, helper, plan) == [
        "Marcus needs The Gift to help in a laboratory."
    ]
    helper.virtues_flaws = [VirtueFlawInstance("vf_the_gift")]
    helper.abilities = []
    assert ls.assist_problems(saga, helper, plan) == [
        "Marcus needs Magic Theory to help in a laboratory."
    ]
