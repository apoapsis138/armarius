"""The score and the next score's total xp shown while an Ability's or
Art's total xp is typed, with Puissant's fixed bonus; and the xp an
Affinity needs to gain a given amount."""

from __future__ import annotations

import pytest

from ars_magica_manager import sheet_text as st
from ars_magica_manager.forms.character import arts_form
from ars_magica_manager.models import Character, VirtueFlawInstance
from ars_magica_manager.rules import creation_access
from ars_magica_manager.rules import xp as xp_rules
from ars_magica_manager.rules.rounding import round_up
from ars_magica_manager.tui.screens.forms import EditArtsScreen
from ars_magica_manager.tui.screens.prompts import _ability_dialog


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


def test_live_score_shows_the_next_scores_total():
    # 15 xp is score 2; score 3 needs 30 in total, not 15 more.
    assert st.live_score(15, xp_rules.ABILITY_FACTOR) == "Score 2 · Score 3 at 30 xp"
    assert st.live_score(0, xp_rules.ART_FACTOR) == "Score 0 · Score 1 at 1 xp"
    assert (
        st.live_score(15, xp_rules.ABILITY_FACTOR, bonus=2)
        == "Score 2 (4) · Score 3 at 30 xp"
    )


@pytest.mark.parametrize("xp", [None, -1])
def test_live_score_for_xp_not_yet_typed(xp):
    assert st.live_score(xp, xp_rules.ABILITY_FACTOR) == "Score ?"


def test_ability_dialog_live_line_names_the_ability_and_uses_puissant():
    virtues = [VirtueFlawInstance("vf_puissant_ability", params={"ability": "brawl"})]
    dialog = _ability_dialog("Brawl", None, virtues)
    assert dialog.live is not None
    assert dialog.live({"xp": 15, "specialty": ""}) == (
        "Brawl: Score 2 (4) · Score 3 at 30 xp"
    )
    plain = _ability_dialog("Athletics", None, virtues)
    assert plain.live is not None
    assert plain.live({"xp": 15, "specialty": ""}) == (
        "Athletics: Score 2 · Score 3 at 30 xp"
    )


def test_arts_grid_shows_score_and_next_total_in_columns():
    virtues = [VirtueFlawInstance("vf_puissant_art", params={"art": "creo"})]
    screen = EditArtsScreen(
        arts_form(Character(id="m", name="M", type="magus")), virtues
    )
    assert screen._score_label("creo", 6) == "3 (6)    10 xp"
    assert screen._score_label("vim", 6) == "3        10 xp"
    assert screen._score_label("vim", None) == "?"
