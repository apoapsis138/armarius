import pytest

from ars_magica_manager import catalog
from ars_magica_manager.models import Modifier, VirtueFlawDef


def test_seed_catalog_loads_and_validates():
    entries = catalog.load_virtue_flaw_catalog()
    assert any(entry.id == "vf_gifted_researcher" for entry in entries)


def test_single_virtue_can_have_differently_scoped_modifiers():
    entries = catalog.load_virtue_flaw_catalog()
    gifted_researcher = next(e for e in entries if e.id == "vf_gifted_researcher")

    by_activity = {m.activity: m.amount for m in gifted_researcher.modifiers}
    assert by_activity == {"original_research": 3, "invent_spells": 6}
    assert all(m.applies_to == "lab_total" for m in gifted_researcher.modifiers)


def test_unknown_applies_to_is_rejected():
    with pytest.raises(ValueError, match="applies_to"):
        Modifier(applies_to="not_a_real_total", amount=3)


def test_unknown_activity_for_a_type_is_rejected():
    with pytest.raises(ValueError, match="activity"):
        Modifier(applies_to="lab_total", activity="not_a_real_activity", amount=3)


def test_activity_from_wrong_type_is_rejected():
    # "reading" is a study_total activity, not a lab_total one.
    with pytest.raises(ValueError, match="activity"):
        Modifier(applies_to="lab_total", activity="reading", amount=3)


def test_virtue_flaw_def_from_dict_propagates_validation():
    with pytest.raises(ValueError, match="applies_to"):
        VirtueFlawDef.from_dict(
            {
                "id": "vf_bad",
                "name": "Bad Data",
                "type": "Virtue",
                "category": "General",
                "cost": 1,
                "modifiers": [{"applies_to": "not_a_real_total", "amount": 1}],
            }
        )
