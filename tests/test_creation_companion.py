"""A Gifted companion: allowed, with the Definitive Edition's advice that
it should be extremely unusual (Chapter Three, page 45)."""

import pytest

from ars_magica_manager.models import Character, Saga, VirtueFlawInstance
from ars_magica_manager.rules import creation

ADVICE = "A Gifted companion should be extremely unusual"


def _labels(character: Character) -> dict[str, str]:
    saga = Saga(id="s", name="S", current_year=1220)
    return {
        c.label: c.status
        for c in creation.checks(saga, character)
        if c.step == "virtues_flaws"
    }


def _character(kind: str, *vf_ids: str) -> Character:
    return Character(
        id="c",
        name="C",
        type=kind,
        in_creation=True,
        virtues_flaws=[VirtueFlawInstance(i) for i in vf_ids],
    )


def test_a_gifted_companion_gets_the_books_advice():
    labels = _labels(_character("companion", "vf_the_gift", "vf_covenfolk"))
    assert labels[ADVICE] == "advice"
    assert "Hermetic Virtues and Flaws need The Gift" not in labels


@pytest.mark.parametrize(
    "kind, vf_ids",
    [
        ("companion", ("vf_covenfolk",)),
        ("magus", ("vf_the_gift", "vf_hermetic_magus")),
        ("mythic companion", ("vf_the_gift",)),
    ],
)
def test_no_advice_for_anyone_else(kind, vf_ids):
    assert ADVICE not in _labels(_character(kind, *vf_ids))
