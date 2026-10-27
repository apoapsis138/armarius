"""Gaining and losing Virtues and Flaws in play (Grogs pp. 61-64; DE p. 63,
p. 391): the rules, and More's Gain or Lose in Play on Virtues & Flaws."""

from __future__ import annotations

from dataclasses import replace

from ars_magica_manager import actions, catalog
from ars_magica_manager.commands import Choose
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import vf_change as forms
from ars_magica_manager.forms import virtue as virtue_forms
from ars_magica_manager.models import Ability, Character, Saga, VirtueFlawInstance
from ars_magica_manager.rules import vf_change as vc

BY_ID = catalog.load_virtue_flaw_catalog_by_id()


def person(kind: str = "companion", *vf_ids: str) -> Character:
    character = Character(id="c", name="Tomas", type=kind)
    character.virtues_flaws = [VirtueFlawInstance(vf_id) for vf_id in vf_ids]
    return character


def saga_with(character: Character) -> Saga:
    saga = Saga(id="s", name="Test")
    saga.characters.append(character)
    return saga


def held(character: Character) -> list[str]:
    return [vf.vf_id for vf in character.virtues_flaws]


# -- the rules --


def test_a_second_major_personality_flaw_is_refused():
    character = person("companion", "vf_wrathful_major")
    why = vc.gain_refusal(character, BY_ID["vf_greedy_major"], BY_ID)
    assert "one Major Personality Flaw" in why
    assert vc.gain_refusal(character, BY_ID["vf_greedy"], BY_ID) == ""


def test_a_social_status_is_gained_only_as_a_change_of_status():
    character = person("grog", "vf_covenfolk")
    assert "change of Social Status" in vc.gain_refusal(
        character, BY_ID["vf_custos"], BY_ID
    )
    assert vc.gain_refusal(person("grog"), BY_ID["vf_custos"], BY_ID) == ""


def test_a_grog_is_warned_off_story_flaws_and_major_virtues():
    grog = person("grog", "vf_covenfolk")
    story = vc.gain_notes(grog, BY_ID["vf_enemies"], BY_ID)
    assert any("shouldn't gain a Story Flaw" in line for line in story)
    major = next(
        e
        for e in catalog.load_virtue_flaw_catalog()
        if e.side == "Virtue" and e.tier == "Major" and e.category == "General"
    )
    assert any("cautious" in line for line in vc.gain_notes(grog, major, BY_ID))
    companion = person("companion")
    assert not any(
        "cautious" in line for line in vc.gain_notes(companion, major, BY_ID)
    )


def test_personality_flaws_past_the_guideline_are_noted():
    grog = person("grog", "vf_greedy")
    assert any(
        "no more than 1" in line
        for line in vc.gain_notes(grog, BY_ID["vf_wrathful"], BY_ID)
    )
    companion = person("companion", "vf_greedy")
    assert not any(
        "Personality Flaws" in line
        for line in vc.gain_notes(companion, BY_ID["vf_wrathful"], BY_ID)
    )


def test_a_virtue_changing_experience_keeps_what_was_gained():
    lines = vc.gain_notes(person(), BY_ID["vf_affinity_with_ability"], BY_ID)
    assert any("isn't recalculated" in line for line in lines)


def test_initiation_needs_an_organization_lore():
    character = person()
    assert "Organization Lore first" in vc.initiation_note(character)
    character.abilities.append(Ability("Organization Lore: Mithraic Cult", xp=5))
    assert "Organization Lore: Mithraic Cult" in vc.initiation_note(character)


def test_warping_says_what_a_mundane_score_has_brought():
    character = person()
    character.aging.warping_score = 3
    lines = vc.warping_notes(character)
    assert any("Warping Score 1" in line for line in lines)
    assert any("second Minor Flaw" in line for line in lines)
    assert "Twilight" in vc.warping_notes(person("magus"))[0]


def test_a_lost_hand_isnt_restored_by_initiation():
    entry = BY_ID["vf_missing_hand"]
    assert "not Initiation" in vc.loss_notes(entry, vc.INITIATION)[0]
    assert vc.loss_notes(entry, vc.MAGIC) == []


def test_exchanges_are_like_for_like():
    wrathful, reclusive = BY_ID["vf_wrathful"], BY_ID["vf_reclusive"]
    assert vc.exchange_refusal(wrathful, reclusive, False) == ""
    assert "Minor" in vc.exchange_refusal(wrathful, BY_ID["vf_greedy_major"], False)
    assert vc.exchange_refusal(wrathful, BY_ID["vf_greedy_major"], True) == ""
    assert "Flaw" in vc.exchange_refusal(wrathful, BY_ID["vf_tough"], True)


def test_a_status_changes_only_for_another_status():
    knight, outlaw = BY_ID["vf_knight"], BY_ID["vf_outlaw_leader"]
    assert vc.status_refusal(knight, outlaw) == ""
    assert "not a Social Status" in vc.status_refusal(knight, BY_ID["vf_tough"])
    assert "already" in vc.status_refusal(knight, knight)


# -- the form --


def test_gaining_a_flaw_by_mishap_adds_it_and_keeps_the_diary():
    character = person("grog", "vf_covenfolk")
    saga = saga_with(character)
    values = {
        "change": vc.GAIN_FLAW,
        "flaw_cause": vc.MISHAP,
        "flaw": VirtueFlawInstance("vf_missing_hand"),
        "story": "lost his hand at the ford",
    }
    lines = forms.change_lines(saga, character, values)
    assert "Missing Hand (Minor Flaw) is added." in lines[0]
    assert any("Missing Hand Flaw" in line for line in lines)
    forms.record(saga, character, values)
    assert held(character) == ["vf_covenfolk", "vf_missing_hand"]
    entry = character.diary[-1]
    assert entry.name == "Gain a Flaw: Missing Hand"
    assert "lost his hand at the ford" in entry.details
    assert "Grogs" in entry.details


def test_the_form_asks_for_the_flaw():
    character = person()
    problem = forms._problem(saga_with(character), character)
    assert problem({"change": vc.GAIN_FLAW}) == "Choose the Flaw gained."
    assert problem({"change": vc.LOSE_FLAW}) == "Choose the Flaw lost."


def test_gaining_a_great_characteristic_moves_it():
    character = person()
    character.characteristics.strength = 3
    saga = saga_with(character)
    values = {
        "change": vc.GAIN_VIRTUE,
        "virtue_cause": vc.MAGIC,
        "virtue": VirtueFlawInstance(
            "vf_great_characteristic", {"characteristic": "strength"}
        ),
    }
    assert any(
        "Strength +3 to +4" in line
        for line in forms.change_lines(saga, character, values)
    )
    forms.record(saga, character, values)
    assert character.characteristics.strength == 4


def test_losing_a_flaw_takes_it_off():
    character = person("companion", "vf_wrathful", "vf_lame")
    saga = saga_with(character)
    values = {"change": vc.LOSE_FLAW, "lost_flaw": "1", "loss_cause": vc.MAGIC}
    forms.record(saga, character, values)
    assert held(character) == ["vf_wrathful"]
    assert character.diary[-1].name == "Lose a Flaw: Lame"


def test_a_change_of_status_replaces_the_old_in_its_place():
    character = person("companion", "vf_knight", "vf_tough")
    saga = saga_with(character)
    values = {
        "change": vc.SOCIAL_STATUS,
        "old_status": "0",
        "new_status": VirtueFlawInstance("vf_outlaw_leader"),
    }
    assert "replaces Knight" in forms.change_lines(saga, character, values)[0]
    forms.record(saga, character, values)
    assert held(character) == ["vf_outlaw_leader", "vf_tough"]
    kept = person("companion", "vf_knight")
    forms.record(saga, kept, {**values, "keep_old": True})
    assert held(kept) == ["vf_knight", "vf_outlaw_leader"]


def test_an_exchange_swaps_like_for_like_in_place():
    character = person("companion", "vf_wrathful", "vf_tough")
    saga = saga_with(character)
    problem = forms._problem(saga, character)
    values = {
        "change": vc.EXCHANGE,
        "old": "0",
        "new_flaw": VirtueFlawInstance("vf_reclusive"),
    }
    assert problem(values) is None
    assert "Minor" in (
        problem({**values, "new_flaw": VirtueFlawInstance("vf_greedy_major")}) or ""
    )
    forms.record(saga, character, values)
    assert held(character) == ["vf_reclusive", "vf_tough"]


def test_an_exchange_may_not_move_characteristics():
    character = person("companion", "vf_great_characteristic", "vf_tough")
    character.virtues_flaws[0].params = {"characteristic": "strength"}
    character.characteristics.strength = 4
    saga = saga_with(character)
    problem = forms._problem(saga, character)
    values = {
        "change": vc.EXCHANGE,
        "old": "0",
        "new_virtue": VirtueFlawInstance("vf_clear_thinker"),
    }
    assert "Characteristics" in (problem(values) or "")


def test_in_play_a_grog_may_choose_a_major_flaw():
    grog = person("grog", "vf_covenfolk")
    saga = saga_with(grog)
    chosen = virtue_forms.choose_virtue_flaw(saga, grog, "Flaw", in_play=True)
    assert isinstance(chosen, Choose)
    tiers = {choice.value.tier for choice in chosen.choices()}
    assert "Major" in tiers
    at_creation = virtue_forms.choose_virtue_flaw(saga, grog, "Flaw")
    assert "Major" not in {choice.value.tier for choice in at_creation.choices()}


def test_the_status_chooser_lists_only_statuses():
    character = person("companion", "vf_knight")
    saga = saga_with(character)
    chosen = virtue_forms.choose_virtue_flaw(
        saga, character, None, in_play=True, category="Social Status"
    )
    entries = [choice.value for choice in chosen.choices()]
    assert entries and all(vc.is_social_status(e) for e in entries)
    assert {"Virtue", "Flaw"} <= {e.side for e in entries}


# -- where it is offered --


def test_offered_on_a_characters_virtues_and_flaws():
    character = person()
    saga = saga_with(character)
    page = menu_forms.page_for(saga, actions.NodeKind.CHARACTER, character_id="c")
    assert "change_virtues_flaws" in {
        i.action for i in menu_forms.placed(page, "Virtues & Flaws")
    }
    assert actions.available(
        "change_virtues_flaws", replace(page, section="section-vf-flaws")
    )
    assert not actions.available(
        "change_virtues_flaws", replace(page, section="section-char-info")
    )


# -- a Virtue or Flaw gained by magic for a while (Grogs pp. 62-63) --


def test_a_virtue_gained_by_magic_may_be_marked_temporary_with_its_end():
    character = person()
    saga = saga_with(character)
    saga.current_year, saga.current_season = 1220, "Spring"
    values = {
        "change": vc.GAIN_VIRTUE,
        "virtue_cause": vc.MAGIC,
        "virtue": VirtueFlawInstance("vf_keen_vision"),
        "temporary": True,
        "ends_season": "Winter",
        "ends_year": 1221,
    }
    assert "It is temporary, ending Winter 1221." in forms.change_lines(
        saga, character, values
    )
    forms.record(saga, character, values)
    [gained] = character.virtues_flaws
    assert (gained.temporary, gained.ends_year, gained.ends_season) == (
        True,
        1221,
        "Winter",
    )
    assert vc.temporary_text(gained) == "temporary, until Winter 1221"


def test_only_a_magical_gain_is_marked_temporary():
    character = person()
    saga = saga_with(character)
    values = {
        "change": vc.GAIN_VIRTUE,
        "virtue_cause": vc.ACTIONS,
        "virtue": VirtueFlawInstance("vf_keen_vision"),
        "temporary": True,
    }
    forms.record(saga, character, values)
    assert not character.virtues_flaws[0].temporary


def test_an_end_season_already_past_is_refused():
    character = person()
    saga = saga_with(character)
    saga.current_year, saga.current_season = 1220, "Summer"
    problem = forms._problem(saga, character)
    values = {
        "change": vc.GAIN_FLAW,
        "flaw_cause": vc.MAGIC,
        "flaw": VirtueFlawInstance("vf_lame"),
        "temporary": True,
        "ends_season": "Spring",
        "ends_year": 1220,
    }
    assert "already past" in (problem(values) or "")
    assert "year" in (problem({**values, "ends_year": None}) or "")
    assert problem({**values, "ends_season": None, "ends_year": 1220}) is None


def test_a_temporary_virtue_ends_and_is_taken_off():
    character = person("companion", "vf_tough", "vf_keen_vision")
    character.virtues_flaws[1].temporary = True
    saga = saga_with(character)
    fields = {f.key: f for f in forms.change_fields(saga, character)}
    assert [value for _, value in fields["ended"].options] == ["1"]
    values = {"change": vc.TEMPORARY_ENDS, "ended": "1"}
    forms.record(saga, character, values)
    assert held(character) == ["vf_tough"]
    assert character.diary[-1].name == "A temporary Virtue or Flaw ends: Keen Vision"
    problem = forms._problem(saga, character)
    assert problem({"change": vc.TEMPORARY_ENDS, "ended": "0"})


def test_the_season_it_ends_is_noted_in_the_diary():
    from ars_magica_manager.seasons import advance

    character = person("companion", "vf_keen_vision", "vf_tough")
    character.virtues_flaws[0].temporary = True
    character.virtues_flaws[0].ends_year = 1220
    saga = saga_with(character)
    saga.current_year, saga.current_season = 1220, "Autumn"
    assert advance.temporary_virtues_end(saga) == []
    saga.current_season = "Winter"  # a year alone ends at its Winter
    [line] = advance.temporary_virtues_end(saga)
    assert line.what == "Keen Vision"
    assert character.diary[-1].name == "Keen Vision ends"
    assert held(character) == ["vf_keen_vision", "vf_tough"]  # left for the player


def test_the_sheet_marks_a_temporary_virtue():
    from ars_magica_manager import sheet_text

    character = person("companion", "vf_keen_vision")
    vf = character.virtues_flaws[0]
    vf.temporary, vf.ends_season, vf.ends_year = True, "Summer", 1222
    [(_, label)] = sheet_text.vf_rows(character.virtues_flaws, "Virtue")
    assert "temporary, until Summer 1222" in label
    assert "Gained by magic" in sheet_text.vf_info_text(character.virtues_flaws, 0)


def test_a_temporary_virtue_survives_a_save():
    import dataclasses

    character = person("companion", "vf_keen_vision")
    vf = character.virtues_flaws[0]
    vf.temporary, vf.ends_season, vf.ends_year = True, "Summer", 1222
    loaded = Character.from_dict(dataclasses.asdict(character)).virtues_flaws[0]
    assert (loaded.temporary, loaded.ends_year, loaded.ends_season) == (
        True,
        1222,
        "Summer",
    )
