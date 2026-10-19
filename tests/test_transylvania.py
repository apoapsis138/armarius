"""Transylvania's customs: its magi live in oppida, each magus holds the
privilege of one of the five legal covenants, and each oppidum has its
aediles."""

from __future__ import annotations

from support import everything_saga

from ars_magica_manager import saga_overview, tribunal_packages
from ars_magica_manager.commands import Form
from ars_magica_manager.forms import tribunal as tribunal_forms
from ars_magica_manager.models import Saga, Tribunal
from ars_magica_manager.sheets import character as character_sheet
from ars_magica_manager.sheets import covenant as covenant_sheet
from ars_magica_manager.sheets import tribunal as tribunal_sheet
from ars_magica_manager.tribunal_packages import transylvania as tr


def _transylvanian() -> tuple[Saga, Tribunal]:
    """The sample saga with its Rhine Tribunal following Transylvania's
    customs: Keep (Leandro's) and the sketched covenant are its oppida."""
    saga = everything_saga()
    rhine = saga.tribunal("rhine")
    assert rhine is not None
    rhine.package = "transylvania"
    return saga, rhine


def test_its_screens_call_the_place_an_oppidum():
    saga, rhine = _transylvanian()
    keep = saga.covenant("cov1")
    assert keep is not None
    assert tribunal_sheet.roster_title(saga, rhine) == "Oppida (2)"
    assert tribunal_sheet.roster_grid(saga, rhine).columns[0] == "Oppidum"
    assert tribunal_sheet.magi_grid(saga, rhine).columns[2] == "Oppidum"
    assert "Spring oppidum" in covenant_sheet.subtitle(saga, keep)
    assert "Spring oppidum" in saga_overview.covenant_subtitle(saga, keep)
    # Elsewhere the place is still a covenant.
    rhine.package = "rhine"
    assert tribunal_sheet.roster_title(saga, rhine) == "Covenants (2)"
    assert "Spring covenant" in covenant_sheet.subtitle(saga, keep)


def test_a_magus_sheet_shows_their_oppidum_and_privilege():
    saga, rhine = _transylvanian()
    leandro = saga.character("mag1")
    assert leandro is not None
    facts = {f.label: f.value for f in character_sheet.glance_facts(saga, leandro)}
    assert facts["Oppidum"] == "Keep"
    assert facts["Privilege"] == "(not entered)"
    tr.members(saga, rhine).append({"character_id": "mag1", "privilege": "cives"})
    text = character_sheet.info_right_text(saga, leandro)
    assert "Oppidum" in text and "Cives (Coeris)" in text
    rhine.package = "rhine"
    facts = {f.label: f.value for f in character_sheet.glance_facts(saga, leandro)}
    assert "Privilege" not in facts and facts["Covenant"] == "Keep"


def test_the_five_covenants_list_by_legal_covenant_with_offices():
    saga, rhine = _transylvanian()
    keep = saga.covenant("cov1")
    assert keep is not None
    rhine.praeco_id = "mag_sketch"
    tr.members(saga, rhine).extend(
        [
            {"character_id": "mag1", "privilege": "coloniae", "office": "Curantis"},
            {"character_id": "mag_sketch", "privilege": "cives"},
        ]
    )
    tr.save_aediles(rhine, keep.id, {"aedile_0": "mag1"})
    grid = tr.members_grid(saga, rhine)
    assert grid.columns == ["Magus", "Oppidum", "Privilege", "Office"]
    assert [row[2] for row in grid.rows] == ["Cives (Coeris)", "Coloniae (Asclepius)"]
    assert grid.keys == [1, 0]
    assert grid.rows[0][3] == "Praeco"
    assert grid.rows[1][1:] == ["Keep", "Coloniae (Asclepius)", "Aedile, Curantis"]
    assert tr.members_title(saga, rhine) == "The Five Covenants (2)"


def test_a_magus_has_one_privilege():
    saga, rhine = _transylvanian()
    ops = tr.member_ops(saga, rhine)
    form = ops.add()
    assert isinstance(form, Form)
    form.apply({"character_id": "mag1", "privilege": "socii", "office": ""})
    assert tr.privilege_label(tr.entry_of(saga, rhine, "mag1")) == "Socii (Domostron)"
    again = ops.add()
    assert isinstance(again, Form) and again.validate is not None
    assert "already has a privilege" in (again.validate({"character_id": "mag1"}) or "")
    edit = ops.edit(0)
    assert isinstance(edit, Form) and edit.validate is not None
    assert edit.validate({"character_id": "mag1"}) is None


def test_an_oppidum_s_own_form_chooses_its_aediles_from_its_magi():
    saga, rhine = _transylvanian()
    keep = saga.covenant("cov1")
    assert keep is not None
    fields = tribunal_forms.package_fields(saga, keep)
    aediles = [f for f in fields if f.key.startswith("package_rhine_aedile")]
    assert len(aediles) == 2
    assert [value for _, value in aediles[0].options] == ["mag1"]
    assert aediles[0].show_if is not None
    assert aediles[0].show_if({"tribunal_id": "rhine"})
    assert not aediles[0].show_if({"tribunal_id": "thebes"})
    values = {aediles[0].key: "mag1", aediles[1].key: None, "name": "Keep"}
    tribunal_forms.save_package_fields(saga, keep, values)
    assert values == {"name": "Keep"}
    assert tr.aediles(rhine) == {"cov1": ["mag1"]}
    roster = tribunal_sheet.roster_grid(saga, rhine)
    assert roster.columns[5] == "Aediles"
    assert roster.rows[0][5] == "Leandro"
    tr.save_aediles(rhine, keep.id, {"aedile_0": None, "aedile_1": None})
    assert tr.aediles(rhine) == {}


def test_only_a_transylvanian_tribunal_asks_for_aediles():
    saga = everything_saga()
    keep = saga.covenant("cov1")
    keys = [f.key for f in tribunal_forms.package_fields(saga, keep)]
    assert not any(k.startswith("package_rhine_aedile") for k in keys)
    assert "package_transylvania_aedile_0" in keys


def test_a_save_that_gave_an_oppidum_a_class_gives_it_to_its_magi():
    saga, rhine = _transylvanian()
    tribunal_packages.data(rhine, tr.KEY)["classes"] = {
        "cov1": "Hospites",
        "cov_sketch": "Foederati",
    }
    tr.members(saga, rhine).append({"character_id": "mag_sketch"})
    found = tr.members(saga, rhine)
    assert "classes" not in rhine.package_data[tr.KEY]
    assert {m["character_id"]: m.get("privilege") for m in found} == {
        "mag_sketch": None,
        "mag1": "hospites",
    }
