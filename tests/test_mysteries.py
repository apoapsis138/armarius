"""Mystery initiation totals."""

import pytest

from ars_magica_manager.models import Ability, Character, Characteristics
from ars_magica_manager.rules import mysteries as m
from ars_magica_manager.rules.xp import ability_xp


def _component(name: str) -> m.Component:
    return next(c for c in m.COMPONENTS if c.name == name)


def test_the_books_worked_example():
    # Presence 3 + Lore 7 + Script 12 = 22 against 18 (Minor, Virtue unknown).
    mystagogue = Character(
        id="m",
        name="M",
        type="magus",
        characteristics=Characteristics(presence=3),
        abilities=[Ability("House Verditius Lore", xp=ability_xp(7))],
    )
    script = [
        _component("Minor Ordeal"),
        _component("Specific Quest"),
        _component("Special place at a special time"),
        _component("Specific Quest"),
    ]
    total = m.initiation_total(mystagogue, "House Verditius Lore", script)
    target = m.target_level("Minor", mystagogue_has_virtue=False)
    assert (total.total, target.total) == (22, 18)
    assert m.succeeds(int(total.total), int(target.total))
    assert m.succeeds(18, 18)  # equal is enough


@pytest.mark.parametrize(
    ("ordeals", "target"),
    [
        ((), 21),
        ((("Major", 1),), 12),
        ((("Minor", 1), ("Major", 2)), 15),  # only the best counts
        ((("Major", 4),), 21),  # after three Initiations it no longer helps
    ],
)
def test_past_ordeals_lower_the_target(ordeals, target):
    assert m.target_level("Major", True, ordeals).total == target


def test_the_target_never_drops_below_9():
    assert m.target_level("Minor", True, [("Major", 1)]).total == 9


def test_a_once_only_component_twice_invalidates_the_script():
    service = _component("Sacrifice of time serving the cult")
    with pytest.raises(ValueError, match="only once"):
        m.script_bonus([service, service])
