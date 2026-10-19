"""Vassal covenants: the liege shown while both share a Tribunal, the
liege's vassals, and the oath's Boons and Hooks."""

from __future__ import annotations

from ars_magica_manager import packs, transfer, vassals
from ars_magica_manager.forms import world as world_forms
from ars_magica_manager.models import BOON_HOOK_DETAIL, Covenant, Saga
from ars_magica_manager.sheets import covenant as covenant_sheet


def _saga() -> tuple[Saga, Covenant, Covenant]:
    saga = Saga(id="s", name="Saga")
    liege = Covenant(id="fud", saga_id="s", name="Fudarus", tribunal_id="nor")
    vassal = Covenant(
        id="oleron", saga_id="s", name="Oleron", tribunal_id="nor", liege_id="fud"
    )
    saga.covenants += [liege, vassal]
    return saga, liege, vassal


def test_a_vassal_and_its_liege():
    saga, liege, vassal = _saga()
    assert vassals.liege_of(saga, vassal) is liege
    assert vassals.vassals_of(saga, liege) == [vassal]
    assert vassals.rows(saga, vassal) == [("Vassal of", "Fudarus")]
    assert vassals.rows(saga, liege) == [("Vassals", "Oleron")]


def test_the_tie_shows_only_within_one_tribunal():
    saga, liege, vassal = _saga()
    vassal.tribunal_id = "rhine"
    assert vassals.liege_of(saga, vassal) is None
    assert vassals.vassals_of(saga, liege) == []
    assert vassals.rows(saga, vassal) == []


def test_a_liege_that_is_gone_shows_nothing():
    saga, liege, vassal = _saga()
    saga.covenants.remove(liege)
    assert vassals.liege_of(saga, vassal) is None


def test_the_sheets_show_the_tie():
    saga, liege, vassal = _saga()
    facts = {f.label: f.value for f in covenant_sheet.sketch_facts(saga, vassal)}
    assert facts["Vassal of"] == "Fudarus"
    facts = {f.label: f.value for f in covenant_sheet.charter_facts(saga, liege)}
    assert facts["Vassals"] == "Oleron"


def test_swearing_adds_the_oaths_boons_and_hooks_once():
    saga, liege, vassal = _saga()
    vassal.liege_id = None
    form = world_forms.sketch_covenant_form(saga, vassal)
    values = {f.key: f.value for f in form.fields()}
    assert values["liege_id"] is None
    values.update(liege_id="fud", oath="Ten pawns a year.", oath_boons_hooks=True)
    form.apply(dict(values))
    form.apply(dict(values))
    assert (vassal.liege_id, vassal.oath) == ("fud", "Ten pawns a year.")
    assert [(b.vf_id, b.params[BOON_HOOK_DETAIL]) for b in vassal.boons_hooks] == [
        ("covbh_hook_major_beholden", "Fudarus"),
        ("covbh_boon_major_powerful_ally", "Fudarus"),
    ]
    assert [(b.vf_id, b.params[BOON_HOOK_DETAIL]) for b in liege.boons_hooks] == [
        ("covbh_boon_major_favors_owed", "Oleron"),
        ("covbh_hook_minor_protector", "Oleron"),
    ]


def test_clearing_the_liege():
    saga, _liege, vassal = _saga()
    form = world_forms.sketch_covenant_form(saga, vassal)
    values = {f.key: f.value for f in form.fields()}
    form.apply({**values, "liege_id": None})
    assert vassal.liege_id is None


def test_an_import_keeps_the_tie_when_ids_change():
    saga, liege, vassal = _saga()
    data = packs.pack_data(saga, "Normandy", [], [liege, vassal], [])
    target = Saga(id="t", name="Target")
    target.covenants.append(Covenant(id="fud", saga_id="t", name="Other"))
    transfer.apply(target, transfer.plan_import(target, data))
    fudarus = next(c for c in target.covenants if c.name == "Fudarus")
    oleron = next(c for c in target.covenants if c.name == "Oleron")
    assert fudarus.id != "fud" and oleron.liege_id == fudarus.id
