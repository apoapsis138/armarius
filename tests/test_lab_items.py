"""Magic items in a laboratory: a Virtue an item grants, points bought by
an effect's level, and a very large Magic Item."""

from __future__ import annotations

from dataclasses import asdict

from ars_magica_manager import catalog
from ars_magica_manager.commands import Choose, Then
from ars_magica_manager.forms import lab_item as item_forms
from ars_magica_manager.laboratories import vf_rows
from ars_magica_manager.models import (
    EnchantedDevice,
    InstilledEffect,
    LabCharacteristicGrant,
    LabItemBenefit,
    Laboratory,
    LabSpecialtyGrant,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import lab_items
from ars_magica_manager.rules.lab_stats import (
    lab_build_points,
    lab_characteristic_total,
    lab_free_virtues,
    specialization_scores,
)


def _saga(level: int = 20) -> tuple[Saga, Laboratory]:
    lab = Laboratory(id="lab", covenant_id=None, name="Crucible")
    device = EnchantedDevice(
        id="lectern",
        name="Rowan Lectern",
        holder_kind="laboratory",
        holder_id="lab",
        effects=[InstilledEffect(id="e1", name="Steady Page", level=level)],
    )
    return Saga(id="s", name="S", laboratories=[lab], enchanted_devices=[device]), lab


def _install(lab: Laboratory, *, size: str = "") -> VirtueFlawInstance:
    params = {"device": "lectern"}
    if size:
        params["size"] = size
    host = VirtueFlawInstance("labvf_magic_item", params, id="host")
    lab.virtues_flaws.append(host)
    return host


def _catalog():
    return catalog.load_lab_virtue_flaw_catalog_by_id()


def test_a_virtue_an_item_grants_takes_no_space_and_no_build_points():
    """Auspicious Shape is a Minor Virtue: 1 point of space and 10 Build
    Points, unless an item's effect duplicates it."""
    saga, lab = _saga()
    shape = VirtueFlawInstance("labvf_auspicious_shape", id="shape")
    lab.virtues_flaws.append(shape)
    assert lab_free_virtues(lab, _catalog()) == -1
    assert lab_build_points(lab) == 10
    _install(lab)
    lab.item_benefits.append(
        LabItemBenefit(
            "b1",
            "lectern",
            "e1",
            virtue_id="host",
            name="Rowan Lectern",
            granted_id="shape",
        )
    )
    assert lab_free_virtues(lab, _catalog()) == 0
    assert lab_build_points(lab) == 0
    # Its modifications still apply.
    assert {s.name: s.points for s in specialization_scores(saga, lab)} == {"Vim": 1}
    rows = dict(vf_rows(lab, "Virtue"))
    assert "Auspicious Shape (Minor, from Rowan Lectern)" in rows.values()
    assert "Magic Item (Free, Rowan Lectern)" in rows.values()


def test_a_very_large_magic_item_is_a_minor_virtue():
    _, lab = _saga()
    _install(lab, size="very large")
    assert lab_free_virtues(lab, _catalog()) == -1
    assert lab_build_points(lab) == 10


def test_points_bought_by_level_reach_the_totals():
    saga, lab = _saga(level=40)
    _install(lab)
    benefit = LabItemBenefit(
        "b1",
        "lectern",
        "e1",
        virtue_id="host",
        name="Rowan Lectern",
        specializations=[LabSpecialtyGrant("Texts", 2)],
        characteristics=[LabCharacteristicGrant("safety", 1)],
    )
    lab.item_benefits.append(benefit)
    texts = next(s for s in specialization_scores(saga, lab) if s.name == "Texts")
    assert texts.points == 2
    assert texts.sources == (("Rowan Lectern (magic item)", 2),)
    assert lab_characteristic_total(lab, _catalog(), "safety", saga) == (0, 1, 0, 1)
    assert lab_items.levels_needed(benefit) == 40
    assert lab_items.problems(saga, lab, benefit) == []


def test_problems_name_an_overspent_moved_or_lost_item():
    saga, lab = _saga(level=20)
    benefit = LabItemBenefit(
        "b1", "lectern", "e1", specializations=[LabSpecialtyGrant("Texts", 3)]
    )
    lab.item_benefits.append(benefit)
    assert lab_items.problems(saga, lab, benefit) == [
        "its points need level 30, the effect is 20"
    ]
    assert lab_items.budget_problem(20, 3, 0).startswith(
        "These points need a level 30 effect"
    )
    assert lab_items.budget_problem(40, 0, 2) == ""
    saga.enchanted_devices[0].holder_kind = "covenant"
    assert (
        "Rowan Lectern isn't kept in this laboratory: it gives nothing"
        in lab_items.problems(saga, lab, benefit)
    )
    saga.enchanted_devices.clear()
    assert lab_items.problems(saga, lab, benefit) == ["its device is gone"]


def test_a_granted_virtue_the_lab_has_already_is_flagged():
    saga, lab = _saga()
    lab.virtues_flaws += [
        VirtueFlawInstance("labvf_auspicious_shape", id="own"),
        VirtueFlawInstance("labvf_auspicious_shape", id="shape"),
    ]
    benefit = LabItemBenefit("b1", "lectern", "e1", granted_id="shape")
    lab.item_benefits.append(benefit)
    assert lab_items.problems(saga, lab, benefit) == [
        "the lab has that Virtue already: an effect must be new"
    ]


def test_removing_an_effect_takes_its_virtue_and_an_unused_magic_item():
    saga, lab = _saga()
    _install(lab)
    lab.virtues_flaws.append(VirtueFlawInstance("labvf_auspicious_shape", id="shape"))
    lab.item_benefits += [
        LabItemBenefit("b1", "lectern", "e1", virtue_id="host", granted_id="shape"),
        LabItemBenefit(
            "b2",
            "lectern",
            "e1",
            virtue_id="host",
            specializations=[LabSpecialtyGrant("Vim", 1)],
        ),
    ]
    lab_items.remove(lab, lab.item_benefits[0])
    assert [vf.id for vf in lab.virtues_flaws] == ["host"]
    lab_items.forget_device(saga, "lectern")
    assert lab.item_benefits == [] and lab.virtues_flaws == []


def test_deleting_the_item_virtue_takes_its_effects():
    _, lab = _saga()
    _install(lab)
    lab.virtues_flaws.append(VirtueFlawInstance("labvf_auspicious_shape", id="shape"))
    lab.item_benefits.append(
        LabItemBenefit("b1", "lectern", "e1", virtue_id="host", granted_id="shape")
    )
    del lab.virtues_flaws[1]
    lab_items.prune(lab)
    assert lab.item_benefits[0].granted_id is None
    del lab.virtues_flaws[0]
    lab_items.prune(lab)
    assert lab.item_benefits == []


def test_item_benefits_survive_a_save_and_load():
    _, lab = _saga()
    lab.item_benefits.append(
        LabItemBenefit(
            "b1",
            "lectern",
            "e1",
            virtue_id="host",
            specializations=[LabSpecialtyGrant("Texts", 1)],
            characteristics=[LabCharacteristicGrant("health", 1)],
        )
    )
    loaded = Laboratory.from_dict(asdict(lab))
    assert loaded.item_benefits == lab.item_benefits


def test_installing_a_new_device_makes_it_then_its_effect_then_asks_what_it_gives():
    lab = Laboratory(id="lab", covenant_id=None, name="Crucible")
    saga = Saga(id="s", name="S", laboratories=[lab])
    step = item_forms.install(saga, lab)
    assert isinstance(step, Choose)
    assert [c.value for c in step.choices()] == [item_forms.NEW_DEVICE]
    device_form = step.apply(item_forms.NEW_DEVICE)
    values = {f.key: f.value for f in device_form.fields()}
    assert values["holder"] == "laboratory:lab"
    made = device_form.apply({**values, "name": "Rowan Lectern"})
    assert isinstance(made, Then) and saga.enchanted_devices[0].name == "Rowan Lectern"
    effect_values = {f.key: f.value for f in made.step.fields()}
    instilled = made.step.apply({**effect_values, "name": "Steady Page", "level": 20})
    assert isinstance(instilled, Then)
    device = saga.enchanted_devices[0]
    chosen = {f.key: f.value for f in instilled.step.fields()}
    assert chosen["effect"] == item_forms.effect_value(device.id, device.effects[0].id)
    # A device kept here now: Install offers it too.
    assert [c.value for c in item_forms.install(saga, lab).choices()] == [
        item_forms.NEW_DEVICE,
        item_forms.KEPT_DEVICE,
    ]


def test_an_item_kept_elsewhere_gives_the_lab_nothing_until_it_is_back():
    saga, lab = _saga(level=20)
    host = _install(lab)
    lab.virtues_flaws.append(VirtueFlawInstance("labvf_auspicious_shape", id="shape"))
    lab.item_benefits += [
        LabItemBenefit(
            "b1",
            "lectern",
            "e1",
            virtue_id=host.id,
            specializations=[LabSpecialtyGrant("Texts", 1)],
        ),
        LabItemBenefit("b2", "lectern", "e1", virtue_id=host.id, granted_id="shape"),
    ]
    scores = {s.name: s.points for s in specialization_scores(saga, lab)}
    assert scores == {"Texts": 1, "Vim": 1}
    saga.enchanted_devices[0].holder_kind = "covenant"
    assert specialization_scores(saga, lab) == []
    saga.enchanted_devices[0].holder_kind = "laboratory"
    assert {s.name for s in specialization_scores(saga, lab)} == {"Texts", "Vim"}
