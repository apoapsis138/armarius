"""Laboratory Virtues whose Safety is read from an Intelligence: Servant
(half the servant's, rounded up; the servant may be one of the saga's
grogs), Greater Guardian and Greater Horde (the creature's)."""

from __future__ import annotations

import pytest
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import catalog
from ars_magica_manager import laboratories as labs
from ars_magica_manager.commands import Choose, Form
from ars_magica_manager.forms import virtue as virtue_forms
from ars_magica_manager.models import Character, Characteristics, VirtueFlawInstance
from ars_magica_manager.models.traits import new_instance_id
from ars_magica_manager.rules import lab_stats
from ars_magica_manager.sheets import laboratory as ls


def _lab(*instances: VirtueFlawInstance):
    saga = _sample_saga_with_covenant()
    lab = saga.laboratories[0]
    lab.virtues_flaws[:] = list(instances)
    return saga, lab


def _servant(**params: str) -> VirtueFlawInstance:
    return VirtueFlawInstance("labvf_servant", params, id=new_instance_id())


def _grog(saga, id_: str, name: str, intelligence: int, covenant_id=None):
    grog = Character(
        id=id_,
        name=name,
        type="grog",
        covenant_id=covenant_id,
        characteristics=Characteristics(intelligence=intelligence),
    )
    saga.characters.append(grog)
    return grog


def _safety(saga, lab) -> int:
    by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
    return lab_stats.lab_characteristic_total(lab, by_id, "safety", saga)[3]


@pytest.mark.parametrize(
    ("intelligence", "safety"), [(3, 2), (2, 1), (1, 1), (0, 0), (-1, 0), (-3, -1)]
)
def test_a_servant_adds_half_their_intelligence_rounded_up(intelligence, safety):
    saga, lab = _lab(_servant(intelligence=str(intelligence)))
    assert _safety(saga, lab) == safety


def test_two_servants_stack_and_keep_their_other_effects():
    saga, lab = _lab(_servant(intelligence="3"), _servant(intelligence="1"))
    assert _safety(saga, lab) == 3
    by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
    assert lab_stats.lab_characteristic_total(lab, by_id, "aesthetics", saga)[3] == 2


def test_a_servant_with_nothing_entered_adds_nothing_and_says_so():
    saga, lab = _lab(_servant())
    assert _safety(saga, lab) == 0
    assert "Servant: no servant or Intelligence entered" in labs.vf_warnings(lab, saga)


def test_an_assigned_grogs_intelligence_wins_and_follows_their_sheet():
    saga, lab = _lab(_servant(servant="grog1", intelligence="0"))
    grog = _grog(saga, "grog1", "Kurt", 3)
    assert _safety(saga, lab) == 2
    grog.characteristics.intelligence = 5
    assert _safety(saga, lab) == 3
    assert labs.vf_warnings(lab, saga) == ""


def test_a_servant_who_is_gone_falls_back_to_the_typed_number():
    saga, lab = _lab(_servant(servant="gone", intelligence="2"))
    assert _safety(saga, lab) == 1
    assert "its servant is no longer one of the saga's grogs" in labs.vf_warnings(
        lab, saga
    )


def test_a_servant_must_still_be_a_grog():
    saga, lab = _lab(_servant(servant="grog1"))
    _grog(saga, "grog1", "Kurt", 3).type = "companion"
    assert _safety(saga, lab) == 0


@pytest.mark.parametrize("vf_id", ["labvf_greater_guardian", "labvf_greater_horde"])
def test_a_greater_guardian_or_horde_adds_the_creatures_intelligence(vf_id):
    saga, lab = _lab(VirtueFlawInstance(vf_id, {"intelligence": "3"}, id="g"))
    assert _safety(saga, lab) == 3
    lab.virtues_flaws[0].params = {}
    assert _safety(saga, lab) == 0
    assert "no Intelligence entered" in labs.vf_warnings(lab, saga)


def test_the_sheet_says_whose_intelligence_it_is():
    saga, lab = _lab(_servant(servant="grog1"))
    _grog(saga, "grog1", "Kurt", 3)
    rows = {row.key: row for row in ls.characteristics(lab, saga)}
    assert rows["safety"].sources == (
        "Servant +2 (Kurt's Intelligence +3, halved, rounded up)",
    )
    (card,) = ls.virtue_flaw_cards(lab, "Virtue", saga)
    assert card.name == "Servant"  # its grog is not part of its name
    assert card.summary == (
        "Safety +2 (Kurt's Intelligence +3, halved, rounded up), "
        "Aesthetics +1, Mentem +1"
    )
    info = labs.vf_info_text(lab, 0, saga)
    assert "[b]Servant:[/] Kurt" in info
    assert "Safety +2 (Kurt's Intelligence +3, halved, rounded up)" in info


def test_the_catalog_entry_says_what_it_is_read_from():
    entry = catalog.load_lab_virtue_flaw_catalog_by_id()["labvf_servant"]
    assert "Safety +(Intelligence, halved, rounded up)" in labs.vf_entry_text(entry)


def test_adding_a_servant_offers_the_grogs_of_the_labs_covenant_first():
    saga, lab = _lab()
    _grog(saga, "g2", "Anna", 1)
    _grog(saga, "g1", "Kurt", 3, covenant_id=lab.covenant_id)
    entry = catalog.load_lab_virtue_flaw_catalog_by_id()["labvf_servant"]
    fields = {f.key: f for f in virtue_forms.lab_param_fields(saga, lab, entry)}
    assert fields["servant"].options == [("Kurt", "g1"), ("Anna", "g2")]
    show_if = fields["intelligence"].show_if
    assert show_if is not None
    assert show_if({"servant": None}) and not show_if({"servant": "g1"})
    assert virtue_forms.lab_params_from(entry, {"servant": "g1"}) == {"servant": "g1"}
    assert virtue_forms.lab_params_from(
        entry, {"servant": None, "intelligence": -1}
    ) == {"intelligence": "-1"}
    assert virtue_forms.lab_params_from(entry, {"servant": None}) == {}


def test_without_grogs_adding_a_servant_asks_only_for_the_intelligence():
    saga, lab = _lab()
    entry = catalog.load_lab_virtue_flaw_catalog_by_id()["labvf_servant"]
    fields = virtue_forms.lab_param_fields(saga, lab, entry)
    assert [(f.key, f.show_if) for f in fields] == [("intelligence", None)]


def test_adding_through_the_section_ops_stores_the_choice():
    saga, lab = _lab()
    _grog(saga, "g1", "Kurt", 3)
    ops = virtue_forms.virtue_flaw_ops(saga, lab, "Virtue")
    assert ops.add is not None
    choose = ops.add()
    assert isinstance(choose, Choose)
    entry = catalog.load_lab_virtue_flaw_catalog_by_id()["labvf_servant"]
    form = choose.apply(entry)
    assert isinstance(form, Form)
    form.apply({"servant": "g1", "intelligence": None})
    assert lab.virtues_flaws[-1].params == {"servant": "g1"}
    assert _safety(saga, lab) == 2
