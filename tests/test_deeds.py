"""The Deeds chapter's actions: a supplement's actions for play, under the
interest each belongs to, and the terminal's More grouped the same way."""

from __future__ import annotations

from dataclasses import replace

from ars_magica_manager import deeds
from ars_magica_manager.actions import NodeKind, available
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.models import Character, Saga


def test_every_deed_has_an_interest_and_sits_under_it():
    for action in deeds.DEEDS:
        interest = deeds.INTEREST_OF[action]
        assert (NodeKind.CHARACTER, interest) in menu_forms.PLACES[action], action


def test_every_interest_is_listed_and_names_no_section():
    assert set(deeds.INTEREST_OF.values()) <= set(deeds.INTERESTS)
    for action, interest in deeds.INTEREST_OF.items():
        assert action in menu_forms.PLACES, action
        assert interest not in ("Abilities", "Reputations"), action


def test_a_menu_lists_its_ungrouped_actions_first_then_each_interest():
    actions = ["melee_event", "take_harm", "end_session", "disputatio", "trait_roll"]
    assert deeds.grouped(actions) == [
        (None, ["take_harm", "trait_roll"]),
        (deeds.SESSION, ["end_session"]),
        (deeds.KNIGHTLY, ["melee_event"]),
        (deeds.SCHOLARLY, ["disputatio"]),
    ]


def _knight(in_creation: bool) -> Saga:
    knight = Character(id="k", name="Sir Hugo", type="companion")
    knight.in_creation = in_creation
    return Saga(id="s", name="S", characters=[knight])


def test_deeds_wait_while_the_character_is_in_creation():
    page = menu_forms.page_for(_knight(True), NodeKind.CHARACTER, character_id="k")
    assert not menu_forms.placed(page, deeds.SESSION)
    reputations = replace(page, section="section-reputations")
    assert not available("end_session", reputations)
    page = menu_forms.page_for(_knight(False), NodeKind.CHARACTER, character_id="k")
    assert [i.action for i in menu_forms.placed(page, deeds.SESSION)] == ["end_session"]


def test_the_reputations_section_keeps_only_its_own_buttons():
    page = menu_forms.page_for(_knight(False), NodeKind.CHARACTER, character_id="k")
    assert menu_forms.placed(page, "Reputations") == []
    assert "tourney_season" in {
        i.action for i in menu_forms.placed(page, deeds.SEASON_WORK)
    }
