import pytest

from ars_magica_manager import catalog
from ars_magica_manager.models import Modifier, VirtueFlawDef


def test_seed_catalog_loads_and_validates():
    entries = catalog.load_virtue_flaw_catalog()
    assert any(entry.id == "vf_the_gift" for entry in entries)


def test_single_virtue_can_have_differently_scoped_modifiers():
    # A single Virtue carrying two Lab Total modifiers of different sizes,
    # scoped to different lab activities -- not sourced from the catalog,
    # since none of the real Virtues/Flaws have had their modifiers encoded
    # yet (see HANDOFF.md); this just proves the Modifier shape itself.
    gifted_researcher = VirtueFlawDef(
        id="vf_gifted_researcher",
        name="Gifted Researcher",
        type="Virtue",
        category="Hermetic",
        tier="Minor",
        cost=1,
        modifiers=[
            Modifier(applies_to="lab_total", activity="original_research", amount=3),
            Modifier(applies_to="lab_total", activity="invent_spells", amount=6),
        ],
    )

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
                "tier": "Minor",
                "cost": 1,
                "modifiers": [{"applies_to": "not_a_real_total", "amount": 1}],
            }
        )
