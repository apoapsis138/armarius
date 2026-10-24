"""A creature's build (DE pp. 425-426; Realms of Power: Magic pp. 30-36)."""

from ars_magica_manager.forms import creature as creature_forms
from ars_magica_manager.models import Creature, CreaturePower, VirtueFlawInstance
from ars_magica_manager.rules import creature_build as cb


def test_a_magic_creatures_quality_points():
    horse = Creature(
        id="h",
        name="Aeolus",
        realm="Magic",
        might=8,
        size=2,
        virtues_flaws=[
            VirtueFlawInstance("vf_magic_animal"),
            VirtueFlawInstance("vf_lesser_power_quality"),
            VirtueFlawInstance("vf_greater_power_quality"),
        ],
    )
    budget = cb.quality_budget(horse)
    assert budget is not None
    # Might 8 + Size 2 back = 10 points; Lesser 1 + Greater 3 spent.
    assert (budget.from_might, budget.spent, budget.left) == (10, 4, 6)
    assert cb.typical_vis(horse) == 2


def test_what_doesnt_fit_the_creature_rules():
    fae = Creature(
        id="f",
        name="Fae",
        realm="Faerie",
        might=10,
        might_pool=12,
        virtues_flaws=[VirtueFlawInstance("vf_the_gift")],
        powers=[CreaturePower("Storm", might_cost=15)],
    )
    found = cb.problems(fae)
    assert len(found) == 3
    assert "Only a creature with Magic Might" in found[0]


def test_a_power_from_a_quality_suggests_its_cost_and_initiative():
    # RoP: Magic p. 36; Greater Power: cost magnitude / 2, Init Qik - that.
    beast = Creature(id="b", name="B", realm="Magic", might=20)
    beast.characteristics.quickness = 2
    power = CreaturePower("Storm", quality="Greater Power", level=25)  # magnitude 5
    assert cb.suggested(beast, power) == (2, 0)
    filled = creature_forms.fill_suggested(beast, power)
    assert (filled.might_cost, filled.init) == (2, 0)
    typed = CreaturePower(
        "Gale", quality="Lesser Power", level=10, might_cost=0, init=3
    )
    beast.powers = [typed]
    assert "as a Lesser Power, cost 2" in cb.problems(beast)[0]
    assert not cb.power_notes(beast, CreaturePower("Typed", might_cost=4))
