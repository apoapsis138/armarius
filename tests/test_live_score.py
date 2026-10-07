"""The score and xp-to-next shown while an Ability's or Art's total xp is
typed, with Puissant's fixed bonus and an Affinity's xp."""

from __future__ import annotations

import pytest

from ars_magica_manager import sheet_text as st
from ars_magica_manager.models import VirtueFlawInstance
from ars_magica_manager.rules import creation_access
from ars_magica_manager.rules import xp as xp_rules
from ars_magica_manager.rules.rounding import round_up
from ars_magica_manager.screens.forms import EditArtsScreen
from ars_magica_manager.screens.prompts import _ability_dialog


@pytest.mark.parametrize(
    ("gain", "needed"), [(0, 0), (1, 1), (2, 1), (3, 2), (13, 9), (14, 9), (15, 10)]
)
def test_xp_giving_is_the_least_xp_that_reaches_the_gain(gain, needed):
    assert creation_access.xp_giving(gain, 1.5) == needed


def test_xp_giving_matches_effective_xp_for_every_gain():
    for gain in range(1, 200):
        needed = creation_access.xp_giving(gain, 1.5)
        assert round_up(needed * 1.5) >= gain
        assert round_up((needed - 1) * 1.5) < gain
    assert creation_access.xp_giving(12, 1) == 12


def test_live_score_without_virtues():
    assert st.live_score(85, xp_rules.ABILITY_FACTOR) == (
        "Score 5 · 20 xp to next",
        "",
    )
    assert st.live_score(0, xp_rules.ART_FACTOR) == ("Score 0 · 1 xp to next", "")


@pytest.mark.parametrize("xp", [None, -1])
def test_live_score_for_xp_not_yet_typed(xp):
    assert st.live_score(xp, xp_rules.ABILITY_FACTOR) == ("Score ?", "")


def test_live_score_with_a_bonus_and_an_affinity():
    # Score 2 at 15 xp; 30 for score 3, so 15 to go: 10 gained before the
    # Affinity's half again (10 x 1.5 = 15).
    assert st.live_score(15, xp_rules.ABILITY_FACTOR, bonus=2, multiplier=1.5) == (
        "Score 2 (4) · 15 xp to next",
        "10 with Affinity",
    )


def test_ability_dialog_live_line_uses_the_owners_virtues():
    virtues = [
        VirtueFlawInstance("vf_puissant_ability", params={"ability": "brawl"}),
        VirtueFlawInstance("vf_affinity_with_ability", params={"ability": "brawl"}),
    ]
    dialog = _ability_dialog("Brawl", None, virtues)
    assert dialog.live is not None
    assert dialog.live({"xp": 15, "specialty": ""}) == (
        "Score 2 (4) · 15 xp to next (10 with Affinity)"
    )
    plain = _ability_dialog("Athletics", None, virtues)
    assert plain.live is not None
    assert plain.live({"xp": 15, "specialty": ""}) == "Score 2 · 15 xp to next"


def test_arts_grid_label_shows_puissant_and_affinity():
    virtues = [
        VirtueFlawInstance("vf_puissant_art", params={"art": "creo"}),
        VirtueFlawInstance("vf_affinity_with_art", params={"art": "creo"}),
    ]
    screen = EditArtsScreen({}, virtues)
    # Score 3 at 6 xp, score 4 at 10: 4 to go, 3 before the Affinity.
    assert screen._score_label("creo", 6) == (
        "Score 3 (6) · 4 xp to next\n3 with Affinity"
    )
    assert screen._score_label("vim", 6) == "Score 3 · 4 xp to next"
