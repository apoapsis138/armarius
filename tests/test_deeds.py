"""The Deeds chapter's actions: a supplement's actions for play, under the
interest each belongs to, and the terminal's More grouped the same way."""

from __future__ import annotations

from dataclasses import asdict, replace

import pytest

from ars_magica_manager import deeds
from ars_magica_manager.actions import NodeKind, available
from ars_magica_manager.commands import FormCard
from ars_magica_manager.forms import interests
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import religion as religion_forms
from ars_magica_manager.models import Character, Covenant, Saga
from ars_magica_manager.rules import creation_base


def test_every_deed_has_an_interest_and_sits_under_it():
    for action in deeds.DEEDS:
        interest = deeds.INTEREST_OF[action]
        assert (NodeKind.CHARACTER, interest) in menu_forms.PLACES[action], action


def test_every_interest_is_listed_and_names_no_section():
    assert set(deeds.INTEREST_OF.values()) <= set(deeds.INTERESTS)
    for action, interest in deeds.INTEREST_OF.items():
        placed = (*menu_forms.PLACES, *deeds.RELIGION_NOTES, *deeds.AGENT_NOTES)
        assert action in placed, action
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
    assert [i.action for i in menu_forms.placed(page, deeds.SESSION)] == [
        "end_session",
        "what_changed",
    ]


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
    assert [i.action for i in menu_forms.placed(page, deeds.SESSION)] == [
        "end_session",
        "what_changed",
    ]


def test_the_interests_form_turns_interests_off_and_on():
    saga = _knight(False)
    knight = saga.characters[0]
    form = interests.interests_form(saga, knight)
    values = {f.key: f.value for f in form.fields()}
    assert all(values.values())
    assert len(values) == len(deeds.OPTIONAL) - len(deeds.MAGI_ONLY)
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


def _person(religion: str = "") -> Character:
    person = Character.from_dict({"id": "k", "name": "K", "type": "grog"})
    person.background.religion = religion
    return person


def _religion_card(person: Character) -> FormCard:
    cards = interests.interest_cards(None, person)
    return next(c for c in cards if c.title == deeds.RELIGION)


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
    cards = {c.title: c for c in interests.interest_cards(None, _person())}
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
        c
        for c in interests.interest_cards(None, _person())
        if c.title == deeds.APPRENTICESHIP
    )
    assert card.count == "4 actions"
    assert card.detail.count("[b]Turbulence[/]") == 2


def test_session_and_reputation_is_a_card_with_no_switch():
    card = interests.interest_cards(None, _person())[0]
    assert card.title == deeds.SESSION
    assert card.key == "" and card.fixed == interests.ALWAYS_ON


def test_the_terminals_ticks_say_what_each_interest_is():
    knight = Character.from_dict({"id": "k", "name": "K", "type": "grog"})
    form = interests.interests_form(None, knight)
    fields = {f.label: f for f in form.fields()}
    assert fields[deeds.INSIGHT].hint == deeds.SUMMARIES[deeds.INSIGHT]


def test_religions_count_goes_by_the_faith(monkeypatch):
    monkeypatch.setattr(
        interests.action_books, "book_allows", lambda _action, _saga: True
    )
    assert _religion_card(_person()).count == "15 actions for a Christian"
    muslim = _religion_card(_person("Muslim"))
    assert muslim.count == "9 actions for a Muslim"
    assert "[dim]For other faiths: Invoke a Saint," in muslim.detail
    assert "[b]The Hajj[/]" in muslim.detail
    assert _religion_card(_person("Other")).count.endswith("for their faith")


def test_religion_off_hides_the_chapter_but_not_for_a_church_career(monkeypatch):
    monkeypatch.setattr(religion_forms.devotion_forms, "invokes", lambda _saga: True)
    person = _person()
    assert religion_forms.shows(None, person)
    person.interests_off = [deeds.RELIGION]
    assert not religion_forms.shows(None, person)
    assert deeds.interests_off(person) == [deeds.RELIGION]
    person.church.petitions.append(object())
    assert religion_forms.shows(None, person)
    assert deeds.interests_off(person) == []


def test_a_church_career_locks_the_religion_card_and_keeps_the_choice(monkeypatch):
    person = _person()
    person.interests_off = [deeds.RELIGION]
    person.church.petitions.append(object())
    card = _religion_card(person)
    assert card.fixed == "On for a Church career" and not card.key
    assert "Church career keeps this on" in card.detail
    form = interests.interests_form(None, person)
    values = {f.key: f.value for f in form.fields()}
    assert not any("religion" in key for key in values)
    form.apply(values)
    assert person.interests_off == [deeds.RELIGION]


def _magus() -> Character:
    return Character.from_dict({"id": "m", "name": "M", "type": "magus"})


def test_every_tagged_action_says_where_it_is():
    known = (
        *deeds.NOTES,
        *deeds.SEASON_NOTES,
        *deeds.RELIGION_NOTES,
        *deeds.AGENT_NOTES,
        *deeds.HERMETIC_NOTES,
        *deeds.AGING_NOTES,
    )
    assert [a for a in deeds.INTEREST_OF if a not in known] == []


def test_agents_and_research_hide_their_chapters_until_a_record_keeps_them():
    magus = _magus()
    magus.interests_off = [deeds.AGENTS, deeds.RESEARCH]
    assert deeds.chapters_off(magus) == {"Agents", "Research"}
    magus.agents.append(object())
    assert deeds.chapters_off(magus) == {"Research"}
    magus.breakthroughs.append(object())
    assert deeds.chapters_off(magus) == set()
    assert magus.interests_off == [deeds.AGENTS, deeds.RESEARCH]


def test_a_card_kept_on_by_its_record_has_no_switch_and_says_why():
    magus = _magus()
    magus.agents.append(object())
    cards = {c.title: c for c in interests.interest_cards(None, magus)}
    agents = cards[deeds.AGENTS]
    assert agents.fixed == "On while they have agents" and not agents.key
    assert agents.detail.startswith("[$label]Their agents keep this on")
    assert cards[deeds.RESEARCH].count == "The Research chapter"
    assert cards[deeds.RESEARCH].usable


def test_only_a_magus_has_research_and_the_hermetic_mysteries():
    grog = {c.title for c in interests.interest_cards(None, _person())}
    magus = {c.title for c in interests.interest_cards(None, _magus())}
    assert magus - grog == set(deeds.MAGI_ONLY)


def _covenant() -> Covenant:
    return Covenant.from_dict({"id": "c", "name": "C", "saga_id": "s"})


def test_a_covenants_interests_turn_off_and_load_again():
    covenant = _covenant()
    form = interests.covenant_interests_form(None, covenant)
    values = {f.key: f.value for f in form.fields()}
    assert len(values) == 2 and all(values.values())
    values["interest_ships"] = False
    assert form.apply(values) == ["C: Turned off: Ships."]
    assert covenant.interests_off == [deeds.SHIPS]
    assert Covenant.from_dict(asdict(covenant)).interests_off == [deeds.SHIPS]


def test_a_covenants_bad_interests_are_named_when_it_loads():
    with pytest.raises(ValueError, match="interests_off"):
        Covenant.from_dict(
            {"id": "c", "name": "C", "saga_id": "s", "interests_off": "Ships"}
        )


def test_a_ship_or_a_manor_keeps_a_covenants_interest_on():
    covenant = _covenant()
    covenant.interests_off = [deeds.MANORS, deeds.SHIPS]
    assert deeds.covenant_interests_off(covenant) == [deeds.MANORS, deeds.SHIPS]
    covenant.manors["establishments"] = [{"name": "Mill"}]
    assert deeds.covenant_interests_off(covenant) == [deeds.SHIPS]
    form = interests.covenant_interests_form(None, covenant)
    assert [f.key for f in form.fields()] == ["interest_ships"]
    assert form.cards is not None
    assert form.cards()[0].fixed == "On while it has manors"


def test_the_covenant_worksheet_reviews_interests_before_its_review():
    keys = [step.key for step in creation_base.COVENANT_STEPS]
    assert keys.index("interests") == keys.index("finish") - 1
