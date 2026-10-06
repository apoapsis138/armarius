"""Familiars as lab work: binding (or strengthening) the bond and
empowering it with bond powers."""

from support import strip_markup

from ars_magica_manager import seasons
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    BondPower,
    Character,
    Characteristics,
    Covenant,
    Familiar,
    Laboratory,
    Saga,
    SeasonPlan,
)
from ars_magica_manager.rules import familiar_seasons as fs
from ars_magica_manager.rules import lab_seasons
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _saga() -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep")
    magus = Character(id="m", name="Tiberius", type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(intelligence=2)
    magus.abilities = [Ability("Magic Theory", xp=ability_xp(5))]
    # CrAn 10 + 8 + 2 + 5 = 25.
    magus.arts = {
        "creo": ArtScore(xp=art_xp(10)),
        "animal": ArtScore(xp=art_xp(8)),
    }
    magus.raw_vis = {"creo": 8}
    lab = Laboratory(id="lab", covenant_id="cov", name="Tower", owner_id="m")
    raven = Familiar(
        id="raven",
        character_id="m",
        name="Raven",
        magic_might=5,
        size=-2,
        bond_powers=[
            BondPower(
                "sight",
                "Shared Sight",
                level=10,
                technique="Creo",
                form="Animal",
                instilling_progress=0,
            )
        ],
    )
    return Saga(
        id="s",
        name="S",
        covenants=[covenant],
        characters=[magus],
        laboratories=[lab],
        familiars=[raven],
    )


def _plan(activity, **kw):
    return SeasonPlan("m", 1220, "Spring", activity, lab_id="lab", **kw)


def _work(saga, plan):
    return lab_seasons.work(saga, saga.character("m"), plan)


def _run(saga):
    seasons.apply(saga, seasons.resolve(saga))


def _bind(**kw):
    values = {
        "technique": "Creo",
        "form": "Animal",
        "vis_art": "Creo",
        "golden_cord": 1,
        "silver_cord": 1,
        "bronze_cord": 1,
    }
    return _plan(fs.BIND, **(values | kw))


def test_binding_needs_25_plus_might_plus_five_times_size():
    saga = _saga()
    found, work = _work(saga, _bind())
    assert found == [] and work.level == 20  # 25 + 5 - 10
    assert int(work.lab_total.total) == 25 and work.vis_cost == {"Creo": 5}
    saga.familiars[0].magic_might = 15
    found, _ = _work(saga, _bind())
    assert found[0].startswith("Lab Total 25 is below the binding level 30")


def test_the_cords_are_bought_from_the_lab_total():
    saga = _saga()
    found, _ = _work(saga, _bind(golden_cord=3))  # 30 + 5 + 5 = 40 > 25
    assert found == ["The cords cost 40 points; the Lab Total is 25."]


def test_binding_records_the_bond_and_spends_the_vis():
    saga = _saga()
    seasons.plan_lab_work(saga, _bind())
    _run(saga)
    raven = saga.familiars[0]
    assert (raven.binding_lab_total, raven.vis_spent_binding) == (25, 5)
    assert (raven.golden_cord, raven.silver_cord, raven.bronze_cord) == (1, 1, 1)
    assert (raven.season_bound, raven.year_bound) == ("Spring", 1220)
    assert saga.character("m").raw_vis == {"creo": 3}
    assert saga.laboratories[0].diary[-1].activity == "Bind Familiar"
    # Strengthening it later pays only the vis not spent already.
    _, work = _work(saga, _bind())
    assert work.vis_cost == {}


def test_a_bond_power_is_instilled_over_seasons():
    saga = _saga()
    saga.familiars[0].bond_powers[0].level = 15
    plan = _plan(fs.EMPOWER, effect_id="sight", vis_art="Animal")
    saga.character("m").raw_vis = {"animal": 2}
    found, work = _work(saga, plan)
    assert found == [] and (work.points_gained, work.finished) == (10, False)
    assert work.vis_cost == {"Animal": 2}
    added = seasons.plan_lab_work(saga, plan)
    assert [p.season for p in added] == ["Summer"]
    rows = [
        strip_markup(r) for _, r in seasons.lab_queue_rows(saga, saga.laboratories[0])
    ]
    assert rows[0].startswith(
        "Spring 1220 - Summer 1220  Empower the familiar's bond: Shared Sight"
    )
    _run(saga)
    power = saga.familiars[0].bond_powers[0]
    assert (power.instilling_progress, power.vis_spent) == (10, 2)
    saga.current_season = "Summer"
    _run(saga)
    assert power.instilling_progress is None


def test_without_a_familiar_there_is_nothing_to_bind():
    saga = _saga()
    saga.familiars = []
    found, _ = _work(saga, _bind())
    assert found[0].startswith("Tiberius has no familiar")
