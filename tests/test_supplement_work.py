"""The supplements' sub-systems (decision 38): Labor Points, workshops,
progress records, Initiation, universities, wounds."""

import random

from ars_magica_manager import seasons
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Book,
    Character,
    Characteristics,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
    Wounds,
    XpAllocation,
)
from ars_magica_manager.rules import seasons as rules
from ars_magica_manager.rules import supplement_work as sw
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _saga() -> Saga:
    smith = Character(id="c", name="Wulf", type="companion")
    smith.characteristics = Characteristics(dexterity=2, communication=1, presence=2)
    smith.abilities = [
        Ability("Craft: Smith", xp=ability_xp(6)),
        Ability("Artes Liberales", xp=ability_xp(1)),
        Ability("Animal Handling", xp=ability_xp(4)),
        Ability("Mercere Lore", xp=ability_xp(5)),
    ]
    return Saga(id="s", name="S", characters=[smith])


def _plan(activity, subject="ability:Craft: Smith", **kw):
    return SeasonPlan(
        "c", 1220, "Spring", activity, [XpAllocation(subject)] if subject else [], **kw
    )


def _run(saga, plan, rng=None):
    seasons.set_plan(saga, plan)
    seasons.apply(saga, seasons.resolve(saga, rng or random.Random(1)))
    return saga.character("c")


def test_a_working_season_earns_labor_points():
    wulf = _run(_saga(), _plan("working_season"))
    assert wulf.labor_points == (2 + 6) * 3  # (Dex + Craft) x average


def test_wealthy_and_poor_change_the_multiplier():
    saga = _saga()
    saga.character("c").virtues_flaws = [VirtueFlawInstance("vf_wealthy")]
    assert _run(saga, _plan("working_season")).labor_points == 48


def test_workshop_production_reaches_a_quality_and_writes_a_manual():
    saga = _saga()
    wulf = _run(saga, _plan("workshop_production", quick=True, other_modifier=4))
    # Dex 2 + Craft 6 + 4 = 12: Superior; a manual for 1 Labor Point.
    assert (
        "Workshop Total 12 against Craft Level 6: Superior goods"
        in wulf.diary[-1].details
    )
    assert wulf.labor_points == 24 - 1
    assert saga.books[-1].description.startswith("A craft manual on Craft: Smith: +2")


def test_improving_the_workshop_costs_labor_points():
    saga = _saga()
    wulf = saga.character("c")
    found = rules.problems(wulf, _plan("improve_workshop", title="raw materials"), saga)
    assert found[0].startswith("Raising Raw Materials to 1 costs 50 Labor Points")
    wulf.labor_points = 60
    _run(saga, _plan("improve_workshop", title="raw materials"))
    assert (wulf.workshop_raw_materials, wulf.labor_points) == (1, 10)


def test_business_upkeep_in_winter():
    saga = _saga()
    wulf = saga.character("c")
    wulf.labor_points, wulf.workshop_raw_materials = 100, 2
    seasons.year_end_business(saga)
    assert wulf.labor_points == 100 - 36 - 10


def test_a_pilgrimage_is_progress_toward_its_target():
    saga = _saga()

    def pilgrimage():
        return SeasonPlan(
            "c",
            1220,
            saga.current_season,
            "pilgrimage",
            [XpAllocation("ability:Church Lore")],
            title="Santiago",
            other_modifier=6,
        )

    wulf = _run(saga, pilgrimage())
    (record,) = wulf.progress
    assert (record.points, record.target, record.done) == (9, 18, False)
    saga.current_season = "Summer"
    _run(saga, pilgrimage())
    assert record.done
    assert "Finished: Santiago" in [d.name for d in wulf.diary]


def test_taming_an_animal():
    wulf = _run(
        _saga(),
        _plan(
            "tame_animal", subject="ability:Animal Handling", title="Grey", book_level=2
        ),
    )
    assert wulf.progress[0].points == 0 + 4 - 2  # Int + Handling - Might


def test_a_formula_needs_five_xp():
    wulf = _run(
        _saga(),
        _plan("research_formula", subject="ability:Philosophiae", title="Aqua vitae"),
    )
    assert wulf.formulas == ["Aqua vitae"]


def test_an_initiation_gives_the_virtue_and_counts_the_ordeal():
    saga = _saga()
    plan = _plan(
        "undergo_initiation",
        subject="",
        teacher_id="c",
        title="Mercere Lore",
        effect_id="vf_adept_laboratory_student",
        device_id="vf_poor",
        research_kind="Minor",
        other_modifier=12,
    )
    # Presence 2 + Lore 5 + Script 12 = 19 against 18 (Minor, self-initiated).
    wulf = _run(saga, plan)
    ids = [vf.vf_id for vf in wulf.virtues_flaws]
    assert ids == ["vf_adept_laboratory_student", "vf_poor"]
    assert (wulf.ordeal, wulf.initiations_since_ordeal) == ("Minor", 0)
    # Now he has the Virtue (15), and the Ordeal takes 3 off the next.
    assert sw.initiation_target(saga, wulf, plan) == 12


def test_wounds_limit_what_a_season_can_be():
    saga = _saga()
    wulf = saga.character("c")
    wulf.wounds = Wounds(medium=1)
    found = rules.problems(wulf, _plan("workshop_production"), saga)
    assert found == ["Wulf's wounds (-3) allow no lab or craft work."]
    worked = rules.outcome(
        wulf, _plan(rules.PRACTICE, subject="ability:Animal Handling"), saga
    )
    assert worked.gains[0].result.xp == 2  # 4, halved
    wulf.wounds = Wounds(heavy=2)
    found = rules.problems(wulf, _plan(rules.PRACTICE), saga)
    assert found[0].startswith("Wulf's wounds (-10) allow nothing productive")


def test_an_inspeximus_raises_the_summas_level():
    saga = _saga()
    wulf = saga.character("c")
    wulf.type = "magus"
    wulf.arts = {"ignem": ArtScore(xp=art_xp(16))}
    saga.books = [
        Book("s1", "Flames", "Art Summa", author="Wulf", art="Ignem", level=5)
    ]
    _run(saga, _plan("inspeximus", subject="art:Ignem", book_id="s1", book_level=10))
    assert saga.books[0].level == 7  # 5 + (16 - 10) / 3, capped at 8
