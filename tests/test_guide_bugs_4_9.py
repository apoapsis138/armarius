"""The slips the 4.9 walkthrough guides found, fixed: articles before a
realm or an animal, a familiar's species written as a description, a
House Rule's placeholder, a Tribunal with more covenants than its book
counts, and the meeting's first step on either front-end."""

from __future__ import annotations

from ars_magica_manager import catalog, meeting
from ars_magica_manager.markup import a_or_an
from ars_magica_manager.models import Familiar, Saga, Tribunal
from ars_magica_manager.rules import familiar_seasons as fs
from ars_magica_manager.sheets import tribunal as tribunal_sheet


def test_a_or_an_follows_the_first_letter():
    assert a_or_an("Infernal") == "an Infernal"
    assert a_or_an("Magic") == "a Magic"
    assert a_or_an("owl") == "an owl"


def test_a_species_written_as_a_description_reads_as_its_animal():
    falcon = Familiar(
        id="f",
        character_id="m",
        name="Scintilla",
        species="A falcon of the Swabian Alb, its feathers glowing like embers",
    )
    note = fs.fitting_note(falcon, "Creo", "Ignem")
    assert "Neither list names a falcon of the Swabian Alb by name" in note
    owl = Familiar(id="g", character_id="m", name="Hoot", species="owl")
    assert "The list names an owl for Rego." in fs.fitting_note(owl, "Rego", "Vim")


def test_a_house_rule_s_placeholder_reads_as_a_word():
    assert catalog.blank_name("Saint's Blessing ({ability})") == (
        "Saint's Blessing (Ability)"
    )
    assert catalog.blank_name("Affinity with {art}") == "Affinity with (Art)"


def test_more_covenants_than_the_book_counts():
    assert tribunal_sheet._of_total(8, 10) == "8 recorded of 10"
    assert tribunal_sheet._of_total(12, 10) == "12 (book: 10)"
    assert tribunal_sheet._of_total(3, None) == "3"


def test_the_meeting_s_first_step_names_no_terminal_key():
    saga = Saga(id="s", name="S")
    tribunal = Tribunal(id="t", name="Rhine")
    saga.tribunals.append(tribunal)
    now = next(f.value for f in meeting.facts(saga, tribunal) if f.label == "Now")
    assert "(e)" not in now
