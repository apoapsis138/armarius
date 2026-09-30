"""Enchanting as lab work (STORY-905): opening, instilling, lesser and
charged enchantments, attuning a talisman and investigating an item, each on
a device recorded on an Inventory tab."""

import random

from support import strip_markup

from ars_magica_manager import seasons
from ars_magica_manager.models import (
    CHARGED,
    INVESTED,
    LESSER,
    Ability,
    ArtScore,
    Character,
    Characteristics,
    Covenant,
    EnchantedDevice,
    InstilledEffect,
    Laboratory,
    Saga,
    SeasonPlan,
)
from ars_magica_manager.rules import enchant_seasons as es
from ars_magica_manager.rules import lab_seasons
from ars_magica_manager.rules import seasons as rules
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _saga() -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep")
    magus = Character(id="m", name="Tiberius", type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(intelligence=2)
    magus.abilities = [Ability("Magic Theory", xp=ability_xp(5))]  # vis limit 10
    # CrIg: 10 + 8 + 2 + 5 = 25; InVi: 6 + 5 + 2 + 5 = 18.
    magus.arts = {
        art: ArtScore(xp=art_xp(score))
        for art, score in {"creo": 10, "ignem": 8, "vim": 5, "intellego": 6}.items()
    }
    magus.raw_vis = {"vim": 12, "creo": 5}
    lab = Laboratory(id="lab", covenant_id="cov", name="Tower", owner_id="m")
    staff = EnchantedDevice(
        "staff",
        "Staff",
        INVESTED,
        holder_kind="character",
        holder_id="m",
        capacity_override=6,
        effects=[
            InstilledEffect(
                "fire", "Fire", "Creo", "Ignem", level=15, instilling_progress=0
            )
        ],
    )
    ring = EnchantedDevice(
        "ring",
        "Ring",
        LESSER,
        holder_kind="laboratory",
        holder_id="lab",
        capacity_override=4,
        effects=[InstilledEffect("warm", "Warmth", "Creo", "Ignem", level=5)],
    )
    wand = EnchantedDevice(
        "wand",
        "Wand",
        CHARGED,
        holder_kind="character",
        holder_id="m",
        effects=[InstilledEffect("bolt", "Bolt", "Creo", "Ignem", level=15)],
    )
    box = EnchantedDevice(
        "box",
        "Box",
        INVESTED,
        holder_kind="covenant",
        holder_id="cov",
        pawns_opened=5,
        effects=[
            InstilledEffect("a", "Lid", "Rego", "Terram", level=5, known=False),
            InstilledEffect("b", "Lock", "Rego", "Terram", level=25, known=False),
        ],
    )
    return Saga(
        id="s",
        name="S",
        covenants=[covenant],
        characters=[magus],
        laboratories=[lab],
        enchanted_devices=[staff, ring, wand, box],
    )


def _plan(activity, **kw):
    return SeasonPlan("m", 1220, "Spring", activity, lab_id="lab", **kw)


def _work(saga, plan):
    return lab_seasons.work(saga, saga.character("m"), plan)


def _device(saga, device_id):
    return next(d for d in saga.enchanted_devices if d.id == device_id)


def _run(saga):
    worked = seasons.resolve(saga, random.Random(1))
    seasons.apply(saga, worked)
    return worked


def test_enchanting_is_planned_on_the_laboratory():
    magus = _saga().character("m")
    lab = [a.key for a in rules.activities_for(magus, lab=True)]
    assert all(key in lab for key in es.ACTIVITIES)


def test_opening_an_item_spends_its_capacity_in_vim():
    saga = _saga()
    found, work = _work(saga, _plan(es.OPEN, device_id="staff"))
    assert found == [] and work.vis_cost == {"Vim": 6}
    seasons.plan_lab_work(saga, _plan(es.OPEN, device_id="staff"))
    _run(saga)
    staff = _device(saga, "staff")
    assert (staff.pawns_opened, staff.maker_id) == (6, "m")
    assert saga.character("m").raw_vis == {"vim": 6, "creo": 5}
    found, _ = _work(saga, _plan(es.OPEN, device_id="staff"))
    assert found == ["Staff is already opened."]


def test_opening_is_within_the_vis_limit():
    saga = _saga()
    _device(saga, "staff").capacity_override = 12
    found, _ = _work(saga, _plan(es.OPEN, device_id="staff"))
    assert found == [
        "Opening Staff takes 12 pawns of Vim vis; Tiberius can handle 10 in a "
        "season (twice Magic Theory)."
    ]


def test_instilling_takes_seasons_and_its_vis_in_the_first():
    saga = _saga()
    plan = _plan(es.INSTIL, device_id="staff", effect_id="fire", vis_art="Creo")
    found, _ = _work(saga, plan)
    assert found == ["Staff has to be opened first."]
    _device(saga, "staff").pawns_opened = 6
    found, work = _work(saga, plan)
    assert found == [] and int(work.lab_total.total) == 25
    # 25 - 15 = 10 points a season: 2 seasons; 2 pawns of vis, spent now.
    assert (work.points_gained, work.finished, work.vis_cost) == (
        10,
        False,
        {"Creo": 2},
    )
    added = seasons.plan_lab_work(saga, plan)
    assert [(p.season, p.effect_id) for p in added] == [("Summer", "fire")]
    rows = [
        strip_markup(r) for _, r in seasons.lab_queue_rows(saga, saga.laboratories[0])
    ]
    assert rows[0].startswith("Spring 1220 - Summer 1220  Instil an effect: Fire")
    assert rows[0].endswith("instilled")
    _run(saga)
    effect = _device(saga, "staff").effects[0]
    assert effect.instilling_progress == 10
    assert saga.character("m").raw_vis == {"vim": 12, "creo": 3}
    saga.current_season = "Summer"
    _run(saga)
    assert effect.instilling_progress is None  # finished
    assert saga.character("m").raw_vis == {"vim": 12, "creo": 3}  # no more vis


def test_a_lesser_enchantment_needs_twice_the_level():
    saga = _saga()
    plan = _plan(es.LESSER_WORK, device_id="ring", effect_id="warm", vis_art="Creo")
    found, work = _work(saga, plan)
    assert found == [] and work.vis_cost == {"Creo": 1}
    _device(saga, "ring").effects[0].level = 15
    found, _ = _work(saga, plan)
    assert found[0].startswith("Lab Total 25: a lesser enchantment of level 15")


def test_a_charged_item_gets_charges_for_the_excess():
    saga = _saga()
    plan = _plan(es.CHARGED_WORK, device_id="wand", effect_id="bolt")
    found, work = _work(saga, plan)
    assert found == [] and work.charges == 2  # (25 - 15) / 5
    seasons.plan_lab_work(saga, plan)
    _run(saga)
    wand = _device(saga, "wand")
    assert wand.lab_total == 25 and wand.maker_id == "m"


def test_attuning_makes_the_talisman():
    saga = _saga()
    staff = _device(saga, "staff")
    staff.pawns_opened, staff.maker_id = 6, "m"
    seasons.plan_lab_work(saga, _plan(es.ATTUNE, device_id="staff"))
    _run(saga)
    assert staff.talisman
    # The talisman adds 5 when its magus instils effects in it.
    _, work = _work(
        saga, _plan(es.INSTIL, device_id="staff", effect_id="fire", vis_art="Creo")
    )
    assert int(work.lab_total.total) == 30
    ring = _device(saga, "ring")
    ring.type, ring.pawns_opened, ring.maker_id = INVESTED, 4, "m"
    found, _ = _work(saga, _plan(es.ATTUNE, device_id="ring"))
    assert found[0].startswith("Tiberius already has a talisman (Staff)")


def test_investigating_finds_powers_weakest_first():
    saga = _saga()
    plan = _plan(es.INVESTIGATE, device_id="box", die=3)
    found, work = _work(saga, plan)
    assert found == [] and int(work.lab_total.total) == 18 and work.level == 5
    seasons.plan_lab_work(saga, plan)
    _run(saga)
    box = _device(saga, "box")
    # A typed die is used for one roll: 18 + 3 finds the level 5 power.
    assert [e.known for e in box.effects] == [True, False]
    assert "found Lid" in saga.character("m").diary[-1].details
