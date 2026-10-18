"""Places and regiones: nesting, where records are, a level's aura and
who can see or enter it, the effects that reach the totals, and a
covenant's aura from its place."""

from __future__ import annotations

import random

from support import everything_saga

from ars_magica_manager import laboratory_sheet, neighbour_forms, place_events, places
from ars_magica_manager.commands import Confirm, Form, Refuse
from ars_magica_manager.covenant_forms import covenant_form
from ars_magica_manager.laboratory_forms import identity_form
from ars_magica_manager.models import Ability, Neighbour
from ars_magica_manager.rules import aging, lab
from ars_magica_manager.seasons import character_effects


def _drachenfels(saga):
    found = places.place(saga, "drachenfels")
    assert found is not None
    return found


def test_a_place_sits_inside_another_and_lists_what_is_here():
    saga = everything_saga()
    drachenfels = _drachenfels(saga)
    assert [p.name for p in places.inside_of(saga, drachenfels)] == [
        "The Siebengebirge"
    ]
    outer = places.place(saga, "siebengebirge")
    assert outer is not None
    assert places.within(saga, outer) == {"drachenfels"}
    saga.covenants[0].place_id = "drachenfels"
    assert places.here(saga, drachenfels) == ["Keep", "Aeolus"]
    assert places.here(saga, outer) == ["The Drachenfels"]
    assert places.inside_text(saga, drachenfels) == "The Siebengebirge"
    drachenfels.place_level = 0
    facts = {f.label: f.value for f in places.facts(saga, drachenfels)}
    assert facts["Aura"] == "Magic 5"
    assert facts["Regio"] == "2 levels"
    assert facts["Gazetteer"] == "Visited, locally"
    assert facts["Claimed by"] == "Keep"


def test_a_place_cannot_be_put_inside_itself_or_what_is_inside_it():
    saga = everything_saga()
    outer = places.place(saga, "siebengebirge")
    assert outer is not None
    form = neighbour_forms.edit_neighbour_form(saga, outer)
    inside = next(f for f in form.fields() if f.key == "where")
    assert inside.label == "Inside"
    offered = {value for _label, value in inside.options}
    assert not any(v.startswith(("siebengebirge", "drachenfels")) for v in offered)
    keys = [f.key for f in form.fields()]
    assert "ruler" not in keys and "answers_to" not in keys


def test_each_level_has_its_aura_and_an_aura_effect_replaces_it():
    saga = everything_saga()
    drachenfels = _drachenfels(saga)
    assert places.aura_at(drachenfels, 0) == (5, "Magic")
    assert places.aura_at(drachenfels, 1) == (6, "Faerie")
    assert places.aura_at(drachenfels, 2) == (7, "Magic")
    places.effects(drachenfels).append(
        {"what": "aura", "amount": 3, "target": "faerie", "where": "1+"}
    )
    assert places.aura_at(drachenfels, 0) == (5, "Magic")
    assert places.aura_at(drachenfels, 2) == (3, "Faerie")


def test_a_roll_says_who_can_see_or_enter_a_level():
    assert places.parse_roll("Per + Awareness against 9") == places.Roll(
        "perception", "Awareness", 9
    )
    assert places.parse_roll("Intelligence + Magic Lore vs 15") == places.Roll(
        "intelligence", "Magic Lore", 15
    )
    assert places.parse_roll("walk the path backwards at dusk") is None
    saga = everything_saga()
    magus = saga.character("mag1")
    assert magus is not None
    magus.characteristics.perception = 3
    magus.abilities.append(Ability("Awareness", xp=105))
    assert places.who_can(saga, "Per + Awareness against 9") == [(magus.name, 9)]
    assert places.who_can(saga, "Per + Awareness against 10") == []
    assert places.who_can_text(saga, "Per + Awareness against 10") == "no one yet"
    assert places.who_can_text(saga, "sing the dawn hymn") == ""


def test_a_covenant_takes_its_aura_from_its_place_and_keeps_its_own():
    saga = everything_saga()
    covenant = saga.covenants[0]
    covenant.aura, covenant.aura_realm = 2, "Magic"
    form = covenant_form(saga, covenant)
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    values["where"] = "drachenfels@1"
    form.apply(values)
    assert (covenant.aura, covenant.aura_realm) == (6, "Faerie")
    assert covenant.own_aura == 2
    keys = [f.key for f in covenant_form(saga, covenant).fields()]
    assert "aura" not in keys and "aura_realm" not in keys
    form = covenant_form(saga, covenant)
    values = {f.key: f.value for f in form.fields()}
    values["where"] = None
    form.apply(values)
    assert (covenant.aura, covenant.aura_realm, covenant.own_aura) == (2, "Magic", None)


def test_deleting_a_place_places_what_was_in_it_nowhere():
    saga = everything_saga()
    covenant = saga.covenants[0]
    covenant.aura = 2
    covenant.place_id = "drachenfels"
    places.sync(saga)
    assert covenant.aura == 5
    command = neighbour_forms.delete_neighbour(saga, _drachenfels(saga))
    assert isinstance(command, Confirm)
    assert "Keep, Aeolus will be placed nowhere" in command.question
    command.apply()
    assert (covenant.place_id, covenant.aura) == (None, 2)


def _aura_line(total) -> int:
    return next(
        int(line.amount or 0) for line in total.lines if line.label.startswith("Aura")
    )


def test_a_lab_placed_in_a_regio_takes_its_aura_and_its_lab_bonus():
    saga = everything_saga()
    laboratory = saga.laboratory("lab1")
    magus = saga.character("mag1")
    assert laboratory is not None and magus is not None
    before = lab.lab_total(saga, magus, "Creo", "Herbam", laboratory)
    form = identity_form(saga, laboratory)
    values = {f.key: f.value for f in form.fields()}
    values["where"] = "drachenfels@2"
    form.apply(values)
    assert (laboratory.place_id, laboratory.place_level) == ("drachenfels", 2)
    shown = laboratory_sheet.aura(saga, laboratory)
    assert (shown.covenant, shown.realm) == (7, "Magic")
    after = lab.lab_total(saga, magus, "Creo", "Herbam", laboratory)
    assert _aura_line(after) == 7 + laboratory.aura_modifier
    assert any(line.label == "The Drachenfels" for line in after.lines)
    assert after.total - before.total == 2 + _aura_line(after) - _aura_line(before)
    ignem = lab.lab_total(saga, magus, "Creo", "Ignem", laboratory)
    assert not any(line.label == "The Drachenfels" for line in ignem.lines)


def test_warping_and_aging_reach_those_who_live_there():
    saga = everything_saga()
    magus = saga.character("mag1")
    assert magus is not None
    covenant = saga.covenants[0]
    covenant.place_id, covenant.place_level = "drachenfels", 2
    assert places.warping_per_year(saga, magus) == 4
    places.effects(_drachenfels(saga)).append(
        {"what": "aging_roll", "amount": -1, "where": "all"}
    )
    found = places.character_effects(saga, magus, "aging_roll")
    assert [e.modifier.amount for e in found] == [-1]
    result = aging.roll(magus, 60, 0, 0, random.Random(3), saga)
    assert "The Drachenfels 1" in result.notes[0]
    covenant.place_level = 0
    assert places.warping_per_year(saga, magus) == 0
    covenant.place_level = 2
    magus.aging.longevity_modifier = 0
    before = magus.aging.warping_score
    note = character_effects._yearly_warping(saga, magus)
    assert "The Drachenfels: 4" in note
    assert magus.aging.warping_score >= before


def test_new_place_is_offered_and_made():
    saga = everything_saga()
    form = neighbour_forms.new_neighbour(saga, "places")
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    values.update(name="The Ahse ford", aura=2, where="siebengebirge")
    form.apply(values)
    made = saga.neighbours[-1]
    assert isinstance(made, Neighbour)
    assert (made.kind, made.place_id, made.details["aura"]) == (
        "place",
        "siebengebirge",
        2,
    )


def test_a_dated_trigger_comes_on_its_next_date():
    saga = everything_saga()
    saga.current_year, saga.current_season = 1220, "Autumn"
    drachenfels = _drachenfels(saga)
    yearly, every = place_events.triggers(drachenfels)
    assert place_events.next_date(saga, yearly) == (1221, "Summer")
    assert place_events.next_date(saga, every) == (1225, "Winter")
    assert place_events.when_text(every) == "Winter every 7 years"
    once = {"name": "Level 3 opens", "when": "Once", "season": "Winter", "year": 1220}
    assert place_events.next_date(saga, once) == (1220, "Winter")
    once["year"] = 1219
    assert place_events.next_date(saga, once) is None
    assert place_events.next_date(saga, {"name": "x", "when": "Whenever"}) is None
    assert place_events.next_text(saga, drachenfels) == "Level 2 opens, Summer 1221"
    facts = {f.label: f.value for f in place_events.place_facts(saga, drachenfels)}
    assert facts["Next"] == "Level 2 opens, Summer 1221"


def test_a_trigger_needs_what_its_kind_of_date_needs():
    problem = place_events._trigger_problem
    assert problem({"when": "Once", "season": "Summer", "year": None})
    assert problem({"when": "Each year", "season": None})
    assert problem({"when": "Every N years", "season": "Winter", "every": 0})
    assert problem({"when": "Whenever", "what": ""})
    assert problem({"when": "Each year", "season": "Summer"}) is None


def test_a_roll_table_reads_its_rows_and_writes_to_the_diary():
    rows = place_events.parse_rows("1-3: Nothing\n4: A hare\n9+: The Hall\nbotch: Mist")
    assert rows is not None
    assert [r.result for r in rows if r.covers(4, False)] == ["A hare"]
    assert [r.result for r in rows if r.covers(12, False)] == ["The Hall"]
    assert [r.result for r in rows if r.covers(0, True)] == ["Mist"]
    assert place_events.parse_rows("a stag") is None
    saga = everything_saga()
    drachenfels = _drachenfels(saga)
    before = len(place_events.diary(drachenfels))
    command = place_events.roll_table(saga, drachenfels, 0, random.Random(1))
    assert isinstance(command, Confirm)
    assert command.yes_label == "Write"
    command.apply()
    entry = place_events.diary(drachenfels)[-1]
    assert len(place_events.diary(drachenfels)) == before + 1
    assert entry["text"].startswith("Who walks the Mist Wood: rolled ")
    assert place_events.tables(drachenfels)[0]["last"].startswith("Spring 1220: ")
    assert isinstance(place_events.roll_table(saga, drachenfels, 5), Refuse)


def test_auras_change_only_with_the_option():
    saga = everything_saga()
    drachenfels = _drachenfels(saga)
    assert place_events.change_text(saga, drachenfels) == ""
    assert place_events.raise_aura(saga, drachenfels, random.Random(1)) == ""
    keys = [f.key for f in place_events.place_fields(saga, drachenfels)]
    assert "raising" not in keys
    saga.rule_options["aura_change"] = True
    keys = [f.key for f in place_events.place_fields(saga, drachenfels)]
    assert "raising" in keys and "focus_gone" in keys
    drachenfels.details["raising"] = 30  # sure to rise
    assert "rose to Magic 6" in place_events.raise_aura(
        saga, drachenfels, random.Random(1)
    )
    assert drachenfels.details["aura"] == 6
    assert "aura rose" in place_events.diary(drachenfels)[-1]["text"]
    facts = {f.label: f.value for f in place_events.place_facts(saga, drachenfels)}
    assert facts["Aura change"].startswith("Rises by 1 on a stress die +30")


def test_an_infernal_aura_fades_once_its_focus_is_gone():
    saga = everything_saga()
    saga.rule_options["aura_change"] = True
    pit = Neighbour(id="pit", name="The Pit", kind="place", realm="Infernal")
    pit.details = {"aura": 3}
    assert place_events.change_text(saga, pit) == "Steady while its focus remains"
    pit.details["focus_gone"] = 1215  # 3 to 2 in 1218, to 1 in 1220
    saga.current_year = 1220
    assert place_events.infernal_aura(saga, pit) == 1
    saga.current_year = 1219
    assert place_events.change_text(saga, pit) == "Fading: Infernal 2 this year"
    saga.current_year = 1221
    assert place_events.infernal_aura(saga, pit) == 0
