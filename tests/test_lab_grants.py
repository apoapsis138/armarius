"""Structured laboratory Specialization grants."""

from ars_magica_manager import catalog
from ars_magica_manager.laboratories import (
    migrate_specialty_stand_ins,
    specialization_grant_text,
    vf_warnings,
)
from ars_magica_manager.models import (
    Laboratory,
    LabSpecialtyEntry,
    VirtueFlawInstance,
)
from ars_magica_manager.rules.lab_stats import specialization_scores


def _lab(*instances: VirtueFlawInstance, specialties=()) -> Laboratory:
    lab = Laboratory(id="lab", covenant_id=None, name="Lab")
    lab.virtues_flaws = list(instances)
    lab.specialties = list(specialties)
    return lab


def _scores(lab: Laboratory) -> dict[str, int]:
    return {s.name: s.points for s in specialization_scores(lab)}


def test_fixed_grants_apply_automatically():
    lab = _lab(
        VirtueFlawInstance(vf_id="labvf_subterranean"),
        VirtueFlawInstance(vf_id="labvf_abyss"),
        VirtueFlawInstance(vf_id="labvf_superior_lighting"),
    )
    assert _scores(lab) == {"Texts": 1, "Perdo": 2, "Imaginem": 1, "Terram": 1}


def test_a_chosen_grant_goes_where_it_was_chosen():
    lab = _lab(
        VirtueFlawInstance(vf_id="labvf_chaotic", params={"specialization": "Rego"})
    )
    assert _scores(lab) == {"Experimentation": 1, "Rego": 2}
    by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
    assert (
        specialization_grant_text(lab.virtues_flaws[0], by_id["labvf_chaotic"])
        == "Experimentation +1, Rego +2"
    )


def test_an_unchosen_grant_counts_nothing_and_is_flagged():
    lab = _lab(VirtueFlawInstance(vf_id="labvf_disorganized"))
    assert _scores(lab) == {}
    assert "Disorganized: its Specialization isn't chosen" in vf_warnings(lab)
    by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
    assert (
        specialization_grant_text(lab.virtues_flaws[0], by_id["labvf_disorganized"])
        == "(Muto or Experimentation, not chosen) +1"
    )


def test_undecorated_takes_a_point_from_each_specialization_at_2_or_more():
    lab = _lab(
        VirtueFlawInstance(vf_id="labvf_abyss"),  # Perdo +2
        VirtueFlawInstance(vf_id="labvf_subterranean"),  # Terram +1
        VirtueFlawInstance(vf_id="labvf_undecorated"),
    )
    assert _scores(lab) == {"Perdo": 1, "Terram": 1}


def test_old_typed_stand_ins_are_absorbed():
    lab = _lab(
        VirtueFlawInstance(vf_id="labvf_subterranean"),
        VirtueFlawInstance(vf_id="labvf_deformed"),
        specialties=[
            LabSpecialtyEntry("Terram", 1, "Subterranean"),
            LabSpecialtyEntry("Perdo", 1, "Deformed"),
            LabSpecialtyEntry("Familiar", 1, "Fancy Cages"),
        ],
    )
    migrate_specialty_stand_ins(lab)
    assert [e.source for e in lab.specialties] == ["Fancy Cages"]
    assert lab.virtues_flaws[1].params == {"specialization": "Perdo"}
    assert _scores(lab) == {"Familiar": 1, "Perdo": 1, "Terram": 1}


def test_a_stand_in_that_differs_from_the_grant_is_kept():
    lab = _lab(
        VirtueFlawInstance(vf_id="labvf_subterranean"),
        specialties=[LabSpecialtyEntry("Terram", 2, "Subterranean")],
    )
    migrate_specialty_stand_ins(lab)
    assert len(lab.specialties) == 1


def test_every_choice_lists_real_specializations():
    for entry in catalog.load_lab_virtue_flaw_catalog():
        for target, _points in entry.specialization_grants:
            if target == "{specialization}":
                assert entry.choices["specialization"]
