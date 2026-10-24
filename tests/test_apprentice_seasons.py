"""Apprentices: searching, Opening the Arts, teaching Hermetic
Virtues."""

from ars_magica_manager import seasons
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    Characteristics,
    Laboratory,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import apprentice_seasons as aps
from ars_magica_manager.rules import lab
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _saga() -> Saga:
    magus = Character(id="m", name="Tiberius", type="magus")
    magus.characteristics = Characteristics(communication=2, perception=1)
    magus.abilities = [Ability("Teaching", xp=ability_xp(3))]
    magus.arts = {"creo": ArtScore(xp=art_xp(10)), "ignem": ArtScore(xp=art_xp(6))}
    magus.virtues_flaws = [VirtueFlawInstance("vf_adept_laboratory_student")]
    child = Character(id="c", name="Wolf", type="companion")
    child.virtues_flaws = [VirtueFlawInstance("vf_the_gift")]
    return Saga(id="s", name="S", characters=[magus, child])


def _plan(activity, **kw):
    return SeasonPlan("m", 1220, "Spring", activity, **kw)


def _run(saga):
    return seasons.apply(saga, seasons.resolve(saga))


def test_opening_the_arts_gives_arts_at_0_and_deficiencies():
    saga = _saga()
    seasons.set_plan(saga, _plan(aps.OPEN_ARTS, subject_id="c"))
    _run(saga)
    child = saga.character("c")
    assert len(child.arts) == 15 and child.arts["creo"].xp == 0
    deficient = [vf.params for vf in child.virtues_flaws if "deficient" in vf.vf_id]
    # Every Art but Creo and Ignem (10 and 6) is below 5 for the master.
    assert len(deficient) == 13 and {"form": "Ignem"} not in deficient
    teaching = next(a for a in saga.character("m").abilities if a.name == "Teaching")
    assert teaching.xp == ability_xp(3) + 2  # Exposure


def test_only_a_gifted_child_can_be_opened():
    saga = _saga()
    saga.character("c").virtues_flaws = []
    found, _ = aps.work(saga, saga.character("m"), _plan(aps.OPEN_ARTS, subject_id="c"))
    assert found == ["Wolf doesn't have The Gift."]


def test_teaching_a_hermetic_virtue():
    saga = _saga()
    child = saga.character("c")
    child.abilities = [Ability("Magic Theory", xp=ability_xp(1))]
    plan = _plan(
        aps.TEACH_VIRTUE, subject_id="c", effect_id="vf_adept_laboratory_student"
    )
    found, work = aps.work(saga, saga.character("m"), plan)
    # 2 + 3 + 9 = 14 against 15 (a Minor Virtue).
    assert found == [] and (work.quality, work.target, work.succeeds) == (14, 15, False)
    saga.character("m").abilities[0].xp = ability_xp(4)
    seasons.set_plan(saga, plan)
    _run(saga)
    assert "vf_adept_laboratory_student" in [vf.vf_id for vf in child.virtues_flaws]


def test_searching_for_an_apprentice():
    saga = _saga()
    seasons.set_plan(saga, _plan(aps.SEARCH, die=8))
    _run(saga)
    assert "a Gifted child is found" in saga.character("m").diary[-1].details


def _second_sight(saga, intellego):
    """Wolf with Second Sight 3 (needs 15); Tiberius in his laboratory with
    Intellego and Vim `intellego`."""
    child = saga.character("c")
    child.virtues_flaws.append(VirtueFlawInstance("vf_second_sight"))
    child.abilities = [Ability("Second Sight", "Supernatural", xp=ability_xp(3))]
    magus = saga.character("m")
    magus.arts.update(
        intellego=ArtScore(xp=art_xp(intellego)), vim=ArtScore(xp=art_xp(intellego))
    )
    saga.laboratories = [
        Laboratory(id="lab", covenant_id=None, name="Tower", owner_id="m")
    ]
    magus.assigned_lab_id = "lab"
    return int(
        lab.lab_total(saga, magus, "Intellego", "Vim", saga.laboratories[0]).total
    )


def test_supernatural_abilities_need_an_intellego_vim_lab_total():
    saga = _saga()
    total = _second_sight(saga, 3)
    assert total < 15
    found, _ = aps.work(saga, saga.character("m"), _plan(aps.OPEN_ARTS, subject_id="c"))
    assert found == [
        f"Opening Wolf's Arts needs an Intellego Vim Lab Total of 15; "
        f"Tiberius's is {total}."
    ]


def test_reaching_it_loses_them_and_double_may_keep_them():
    saga = _saga()
    total = _second_sight(saga, 8)
    assert 15 <= total < 30
    seasons.set_plan(saga, _plan(aps.OPEN_ARTS, subject_id="c", keep_supernatural=True))
    _run(saga)
    child = saga.character("c")
    assert not any(a.name == "Second Sight" for a in child.abilities)
    assert not any(vf.vf_id == "vf_second_sight" for vf in child.virtues_flaws)

    saga = _saga()
    assert _second_sight(saga, 15) >= 30
    seasons.set_plan(saga, _plan(aps.OPEN_ARTS, subject_id="c", keep_supernatural=True))
    _run(saga)
    child = saga.character("c")
    assert any(a.name == "Second Sight" for a in child.abilities)
    assert len(child.arts) == 15
