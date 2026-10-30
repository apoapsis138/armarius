"""The Deeds chapter's actions: a supplement's actions for play, under the
interest each belongs to, and the terminal's More grouped the same way."""

from __future__ import annotations

from dataclasses import replace

import pytest

from ars_magica_manager import deeds
from ars_magica_manager.actions import NodeKind, available
from ars_magica_manager.forms import interests
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.models import Character, Saga
from ars_magica_manager.rules import creation_base


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


def test_an_unticked_interest_hides_its_actions_but_never_the_session():
    saga = _knight(False)
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="k")
    assert menu_forms.placed(page, deeds.KNIGHTLY)
    saga.characters[0].interests_off = [deeds.KNIGHTLY, deeds.SESSION]
    assert not menu_forms.placed(page, deeds.KNIGHTLY)
    assert "tourney_season" not in {
        i.action for i in menu_forms.placed(page, deeds.SEASON_WORK)
    }
    assert [i.action for i in menu_forms.placed(page, deeds.SESSION)] == ["end_session"]


def test_the_interests_form_turns_interests_off_and_on():
    saga = _knight(False)
    knight = saga.characters[0]
    form = interests.interests_form(saga, knight)
    values = {f.key: f.value for f in form.fields()}
    assert all(values.values())
    assert len(values) == len(deeds.OPTIONAL)
    values[next(k for k in values if "knightly" in k)] = False
    assert form.apply(values) == ["Sir Hugo: Turned off: Knightly."]
    assert knight.interests_off == [deeds.KNIGHTLY]
    assert form.apply({k: True for k in values}) == [
        "Sir Hugo: Every interest is ticked."
    ]


def test_old_saves_load_with_every_interest_ticked_and_bad_ones_are_refused():
    assert (
        Character.from_dict({"id": "k", "name": "K", "type": "grog"}).interests_off
        == []
    )
    with pytest.raises(ValueError, match="interests_off"):
        Character.from_dict(
            {"id": "k", "name": "K", "type": "grog", "interests_off": "Knightly"}
        )


def test_the_worksheet_reviews_interests_before_the_finishing_touches():
    keys = [step.key for step in creation_base.CHARACTER_STEPS]
    assert keys.index("interests") == keys.index("finish") - 1


def test_every_interest_has_its_words_and_every_action_a_name():
    assert set(deeds.SUMMARIES) == set(deeds.ABOUT) == set(deeds.INTERESTS)
    for action in deeds.INTEREST_OF:
        assert interests._name(action)


def test_a_card_counts_what_the_sagas_books_bring(monkeypatch):
    monkeypatch.setattr(
        interests.action_books,
        "book_allows",
        lambda action, _saga: (
            action
            not in ("sell_goods", "labor_story", "invest_labor", "make_greek_fire")
            and action not in ("melee_event", "tourney_season")
        ),
    )
    cards = {c.title: c for c in interests.interest_cards(None)}
    craft = cards[deeds.CRAFT]
    assert craft.count == "2 actions, 4 more with other books"
    assert "On Planning, in A Season's Work" in craft.detail
    assert "On the Deeds chapter" not in craft.detail
    assert "With City & Guild: " in craft.detail
    knightly = cards[deeds.KNIGHTLY]
    assert knightly.count == "Its books aren't in play" and not knightly.usable


def test_an_action_on_both_pages_shows_on_both_and_counts_once(monkeypatch):
    monkeypatch.setattr(
        interests.action_books, "book_allows", lambda _action, _saga: True
    )
    card = next(
        c for c in interests.interest_cards(None) if c.title == deeds.APPRENTICESHIP
    )
    assert card.count == "3 actions"
    assert card.detail.count("[b]Turbulence[/]") == 2


def test_session_and_reputation_is_a_card_with_no_switch():
    card = interests.interest_cards(None)[0]
    assert card.title == deeds.SESSION
    assert card.key == "" and card.fixed == interests.ALWAYS_ON


def test_the_terminals_ticks_say_what_each_interest_is():
    knight = Character.from_dict({"id": "k", "name": "K", "type": "grog"})
    form = interests.interests_form(None, knight)
    fields = {f.label: f for f in form.fields()}
    assert fields[deeds.INSIGHT].hint == deeds.SUMMARIES[deeds.INSIGHT]
