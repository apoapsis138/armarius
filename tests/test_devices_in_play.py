"""Enchanted devices in play and the laboratory rules around them (DE ch.
8): using an effect (Initiative, Penetration, uses a day), paying an
effect's or a familiar's vis in either Art, who may attune a talisman, a
bond power's modified level, and the Silver Cord's note."""

import random

import pytest
from support import strip_markup
from test_enchant_seasons import _saga as _enchant_saga
from test_familiar_seasons import _saga as _familiar_saga

from ars_magica_manager import actions, familiars, seasons
from ars_magica_manager import enchanted_devices as ed
from ars_magica_manager.commands import Confirm, Refuse
from ars_magica_manager.forms import device as device_forms
from ars_magica_manager.forms import familiar as familiar_forms
from ars_magica_manager.models import (
    CHARGED,
    INVESTED,
    LESSER,
    BondPower,
    Character,
    Characteristics,
    EnchantedDevice,
    InstilledEffect,
    Saga,
    SeasonPlan,
)
from ars_magica_manager.rules import enchant_seasons as es
from ars_magica_manager.rules import enchantment, lab_seasons
from ars_magica_manager.rules import familiar_seasons as fs

# -- using an effect (DE p. 259; Fast Trigger p. 257) ------------------------


def _wand(**effect: object) -> EnchantedDevice:
    values: dict[str, object] = {"uses_per_day": "2", "level": 10}
    values.update(effect)
    return EnchantedDevice(
        "wand",
        "Wand of Flames",
        LESSER,
        holder_kind="character",
        holder_id="m",
        effects=[InstilledEffect("bolt", "Bolt", "Creo", "Ignem", **values)],
    )


def _use_saga(device: EnchantedDevice) -> Saga:
    magus = Character(id="m", name="Tiberius", type="magus")
    magus.characteristics = Characteristics(quickness=2)
    return Saga(id="s", name="S", characters=[magus], enchanted_devices=[device])


def test_an_effect_goes_off_at_quickness_plus_a_die_with_no_penetration():
    device = _wand()
    saga = _use_saga(device)
    effect = device.effects[0]
    lines = ed.use_lines(saga, device, effect)
    assert lines[0] == "Initiative: Quickness +2 + a stress die."
    assert lines[1].startswith("Penetration: 0 (an enchanted device's")
    assert "No Fatigue roll." in lines
    effect.fast_trigger = True
    assert enchantment.use_initiative(effect, 2) == 5
    assert ed.initiative_text(saga, device, effect) == (
        "Quickness +2 + Fast Trigger +3 = +5, + a stress die"
    )
    effect.penetration = 6
    assert ed.use_lines(saga, device, effect)[1] == "Penetration: 6."


def test_uses_are_counted_against_the_day_and_a_new_day_restores_them():
    device = _wand()
    saga = _use_saga(device)
    effect = device.effects[0]
    assert ed.use_effect(effect) and ed.use_effect(effect)
    assert enchantment.uses_left_today(effect) == 0
    assert not ed.use_effect(effect)
    assert ed.uses_today_text(effect) == "2 of 2 used today"
    ed.new_day(saga)
    assert effect.uses_today == 0
    effect.uses_per_day = "Unlimited"
    assert enchantment.uses_left_today(effect) is None
    assert all(ed.use_effect(effect) for _ in range(60))


def test_use_an_effect_asks_first_and_offers_a_new_day_when_spent():
    device = _wand(uses_per_day="1")
    saga = _use_saga(device)
    command = device_forms.use_effect(saga, "character", "m", 1)
    assert isinstance(command, Confirm) and command.yes_label == "Use"
    assert "Quickness +2" in strip_markup(command.question)
    assert command.apply() == ["Bolt: 1 of 1 used today."]
    spent = device_forms.use_effect(saga, "character", "m", 1)
    assert isinstance(spent, Confirm) and spent.yes_label == "New Day"
    assert spent.apply() == ["Bolt: 1 of 1 used today."]
    # The device row, a Charged Item and an unfinished effect can't be used.
    assert isinstance(device_forms.use_effect(saga, "character", "m", 0), Refuse)
    device.type = CHARGED
    assert isinstance(device_forms.use_effect(saga, "character", "m", 1), Refuse)
    device.type, device.effects[0].instilling_progress = INVESTED, 0
    assert not ed.can_use(device, device.effects[0])


def test_use_an_effect_is_a_more_menu_entry_for_the_device_lists():
    item = next(i for i in actions.MORE_MENU if i.action == "use_effect")
    assert item.label == "Use an Effect"
    assert "use_effect" in actions._SECTION_RULES


# -- either Art's vis (DE pp. 258, 266-268) -----------------------------------


def test_split_vis_pays_the_rest_in_the_chosen_art():
    assert enchantment.split_vis(("Creo", "Ignem"), "Creo", 1, 3) == {
        "Creo": 2,
        "Ignem": 1,
    }
    assert enchantment.split_vis(("Creo", "Ignem"), "Ignem", 9, 3) == {"Creo": 3}
    assert enchantment.split_vis(("Creo", "Ignem"), "Creo", 0, 2) == {"Creo": 2}


def _plan(activity: str, **kw: object) -> SeasonPlan:
    return SeasonPlan("m", 1220, "Spring", activity, lab_id="lab", **kw)


def test_an_effects_vis_may_be_split_between_technique_and_form():
    saga = _enchant_saga()
    next(d for d in saga.enchanted_devices if d.id == "staff").pawns_opened = 6
    magus = saga.character("m")
    assert magus is not None
    magus.raw_vis = {"creo": 1, "ignem": 1}
    plan = _plan(
        es.INSTIL, device_id="staff", effect_id="fire", vis_art="Creo", other_vis=1
    )
    found, work = lab_seasons.work(saga, magus, plan)
    assert found == [] and work is not None
    assert work.vis_cost == {"Creo": 1, "Ignem": 1}
    magus.raw_vis = {"creo": 2}
    found, _ = lab_seasons.work(saga, magus, plan)
    assert found == ["It takes 1 pawns of Ignem vis; Tiberius's raw vis has 0."]


def test_a_familiars_binding_vis_may_be_split():
    saga = _familiar_saga()
    magus = saga.character("m")
    assert magus is not None
    magus.raw_vis = {"creo": 3, "animal": 2}
    plan = _plan(
        fs.BIND,
        technique="Creo",
        form="Animal",
        vis_art="Creo",
        other_vis=2,
        golden_cord=1,
    )
    found, work = lab_seasons.work(saga, magus, plan)
    assert found == [] and work is not None
    assert work.vis_cost == {"Creo": 3, "Animal": 2}


# -- who may attune a talisman (DE pp. 259-260) -------------------------------


def _opened_staff(saga: Saga) -> EnchantedDevice:
    staff = next(d for d in saga.enchanted_devices if d.id == "staff")
    staff.pawns_opened = 6
    return staff


def test_an_item_another_prepared_cant_be_attuned():
    saga = _enchant_saga()
    staff = _opened_staff(saga)
    staff.maker_id, staff.maker_name = None, "Hyginus"
    magus = saga.character("m")
    assert magus is not None
    found, _ = lab_seasons.work(saga, magus, _plan(es.ATTUNE, device_id="staff"))
    assert found == [
        "Staff was made by Hyginus: only the magus who prepared it for "
        "enchantment can attune it."
    ]


def test_an_item_with_anothers_effect_cant_be_attuned():
    saga = _enchant_saga()
    staff = _opened_staff(saga)
    staff.maker_id = "m"
    saga.characters.append(Character(id="h", name="Hyginus", type="magus"))
    staff.effects[0].instilled_by = "h"
    magus = saga.character("m")
    assert magus is not None
    found, _ = lab_seasons.work(saga, magus, _plan(es.ATTUNE, device_id="staff"))
    assert found[0].startswith("Hyginus instilled effects in Staff")
    staff.talisman = True
    assert any("Another magus instilled" in w for w in ed.warnings(saga, staff))


def test_instilling_records_who_did_it():
    saga = _enchant_saga()
    staff = _opened_staff(saga)
    seasons.plan_lab_work(
        saga, _plan(es.INSTIL, device_id="staff", effect_id="fire", vis_art="Creo")
    )
    seasons.apply(saga, seasons.resolve(saga, random.Random(1)))
    assert staff.effects[0].instilled_by == "m"
    text = strip_markup(ed.effect_info_text(staff, staff.effects[0], saga))
    assert "Instilled by: Tiberius" in text
    # Attuning it is still allowed: its effect is the magus's own.
    staff.maker_id = "m"
    magus = saga.character("m")
    assert magus is not None
    found, _ = lab_seasons.work(
        saga,
        magus,
        SeasonPlan("m", 1221, "Spring", es.ATTUNE, lab_id="lab", device_id="staff"),
    )
    assert found == []


# -- a bond power's modified level (DE pp. 256-258, 267-268) ------------------


def test_a_typed_bond_power_level_is_final():
    power = BondPower("p", "Speech", level=20, uses_per_day=1, penetration=10)
    assert enchantment.bond_power_level(power) == 20


@pytest.mark.parametrize(
    ("uses", "row"),
    [(1, "1"), (4, "6"), (24, "24"), (0, "Unlimited"), (51, "Unlimited")],
)
def test_bond_power_uses_are_priced_at_the_row_at_or_above(uses: int, row: str):
    assert enchantment.frequency_of(uses) == row


def test_a_worked_out_bond_power_adds_uses_penetration_and_modifications():
    # Shared Senses (DE p. 268): base 5 + Touch + Concentration = 15, and +5
    # for the bond to maintain it: 20 once a day.
    power = BondPower(
        "p",
        "Shared Senses",
        level=15,
        uses_per_day=1,
        worked_out=True,
        maintains_concentration=True,
    )
    assert enchantment.bond_power_level(power) == 20
    power.uses_per_day, power.penetration = 0, 5
    assert enchantment.bond_power_level(power) == 33  # +10 unlimited, +3 Pen 5
    text = strip_markup(familiars.bond_power_info_text(_with(power), 0))
    assert "Level: 33 = 15 + 10 (unlimited) + 3 (Pen 5) + 5 (Item" in text


def _with(power: BondPower):
    saga = _familiar_saga()
    familiar = saga.familiars[0]
    familiar.bond_powers = [power]
    return familiar


def test_empowering_the_bond_uses_the_modified_level():
    saga = _familiar_saga()
    power = saga.familiars[0].bond_powers[0]
    power.level, power.worked_out, power.uses_per_day = 10, True, 0  # 20
    magus = saga.character("m")
    assert magus is not None
    magus.raw_vis = {"creo": 1, "animal": 1}
    plan = _plan(fs.EMPOWER, effect_id="sight", vis_art="Creo", other_vis=1)
    found, work = lab_seasons.work(saga, magus, plan)
    # Creo Animal 25 (no binding Arts recorded to share) is above 20.
    assert found == [] and work is not None
    assert work.level == 20 and work.points_gained == 5
    assert work.vis_cost == {"Creo": 1, "Animal": 1}


def test_the_bond_power_form_saves_the_worked_out_parts():
    powers: list[BondPower] = []
    familiar_forms.save_bond_power(
        powers,
        None,
        {
            "name": "Claws",
            "level": 25,
            "uses_per_day": 1,
            "worked_out": True,
            "fast_trigger": True,
        },
    )
    assert enchantment.bond_power_level(powers[0]) == 30
    keys = [f.key for f in familiar_forms.bond_power_fields(None)]
    assert {"worked_out", "maintains_concentration", "fast_trigger"} <= set(keys)


# -- the Silver Cord (DE p. 267) ----------------------------------------------


def test_the_silver_cord_says_it_is_added_at_the_table():
    saga = _familiar_saga()
    text = familiars.cords_text(saga.familiars[0])
    assert "add it at the table: the app rolls neither" in text
