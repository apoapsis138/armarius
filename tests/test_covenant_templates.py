"""The book's base covenants: placeholders that spend exactly their Build
Points, and choosing another."""

from __future__ import annotations

import pytest

from ars_magica_manager import covenant_templates as templates
from ars_magica_manager.models import Covenant, Saga
from ars_magica_manager.rules import base_covenants
from ars_magica_manager.rules import creation as rules
from ars_magica_manager.rules import creation_covenant as cov


def _saga() -> tuple[Saga, Covenant]:
    covenant = Covenant(id="c", saga_id="s", name="Keep", in_creation=True)
    return Saga(id="s", name="S", covenants=[covenant]), covenant


@pytest.mark.parametrize("base", base_covenants.BASE_COVENANTS, ids=lambda b: b.key)
def test_a_base_covenant_spends_its_build_points(base):
    """Its books and vis, plus the Lab Text and enchanted item levels it
    leaves to choose, come to exactly its Build Points."""
    saga, covenant = _saga()
    templates.apply(saga, covenant, base)
    allowance = base.lab_text_levels // 5 + 2 * (base.enchanted_levels // 5)
    assert cov.spent(saga, covenant) + allowance == base.build_points
    assert (covenant.power_level, covenant.build_points_budget) == (
        base.power_level,
        base.build_points,
    )
    books, vis = base_covenants.placeholders(saga, covenant)
    assert len(books) == (
        len(base.art_summae) + len(base.ability_summae) + len(base.tractatus)
    )
    assert sum(p.pawns for p in vis if p.kind == "vis_source") == base.vis_pawns


def test_filling_in_and_choosing_another_base_covenant():
    saga, covenant = _saga()
    weak, medium = (
        base_covenants.BASE_BY_KEY["weak"],
        base_covenants.BASE_BY_KEY["medium"],
    )
    templates.apply(saga, covenant, weak)
    found = {c.label: c for c in rules.checks(saga, covenant, "build_points")}
    placeholders = found["The base covenant's placeholders are filled in"]
    assert (
        placeholders.detail
        == "8 book(s) need a subject, 1 vis source(s) or stock(s) need an Art"
    )
    lab = found["The base covenant's Lab Texts chosen"]
    assert (lab.status, lab.detail) == ("advice", "0 of 200 levels")
    # The troupe chooses one book's Art; another base covenant keeps it.
    books, _ = base_covenants.placeholders(saga, covenant)
    books[0].art = "Creo"
    templates.apply(saga, covenant, medium)
    books, vis = base_covenants.placeholders(saga, covenant)
    assert len(books) == 8 + 3 + 7  # Medium: Art summae, Ability summae, tractatus
    assert any(b.art == "Creo" for b in saga.books)
    assert covenant.base_covenant == "medium"
    assert len(vis) == 3 + 1
