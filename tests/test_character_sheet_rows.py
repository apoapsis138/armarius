"""The Character sheet's rows and figures in the shared core, which the
desktop sheet draws (character_sheet.py)."""

from __future__ import annotations

from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import character_sheet as cs
from ars_magica_manager.models import Ability, VirtueFlawInstance


def test_an_ability_row_knows_its_way_to_the_next_score():
    saga = _sample_saga_with_covenant()
    c = saga.characters[0]
    c.abilities.append(Ability("Awareness", "General", 20))
    rows = cs.ability_table(c)
    # Grouped in the book's order of categories, General first, whatever
    # order they were added in.
    assert [r.name for r in rows] == ["Awareness", "Magic Theory"]
    awareness = rows[0]
    assert (awareness.index, awareness.score, awareness.xp) == (1, "2", 20)
    assert (awareness.level_xp, awareness.next_xp) == (15, 30)
    assert awareness.fraction == 5 / 15


def test_the_condition_says_fresh_and_unhurt_until_hurt():
    c = _sample_saga_with_covenant().characters[0]
    assert cs.condition(c) == [("Fresh", cs.GOOD), ("Unhurt", cs.GOOD)]
    c.fatigue_level = "winded"
    c.wounds.light = 2
    tones = dict(cs.condition(c))
    assert tones["Winded"] == cs.WARNING
    assert tones["2 Light Wounds"] == cs.WARNING
    assert tones["-2 to rolls"] == cs.BAD


def test_the_subtitle_names_the_house_covenant_and_season():
    saga = _sample_saga_with_covenant()
    c = saga.characters[0]
    c.hermetic.house = "house_bonisagus"
    assert cs.subtitle(saga, c) == (
        "Magus of House Bonisagus  ·  Test Covenant  ·  Spring 1220"
    )


def test_a_spell_row_and_a_spell_the_saga_cant_find():
    saga = _sample_saga_with_covenant()
    c = saga.characters[0]
    c.spells_known[0].mastery_score = 2
    c.spells_known.append(type(c.spells_known[0])("no_such_spell"))
    found, lost = cs.spell_table(saga, c)
    assert (found.name, found.arts, found.level, found.mastery) == (
        "Ball of Abysmal Flame",
        "CrIg",
        20,
        2,
    )
    assert (lost.name, lost.arts, lost.level) == ("no_such_spell", "?", None)


def test_virtue_cards_mark_a_house_virtue_free():
    c = _sample_saga_with_covenant().characters[0]
    c.virtues_flaws.append(VirtueFlawInstance("vf_ambitious"))
    (affinity,) = cs.virtue_flaw_cards(c, "Virtue")
    assert (affinity.name, affinity.tier) == ("Affinity with Creo", "Minor")
    (ambitious,) = cs.virtue_flaw_cards(c, "Flaw")
    assert (ambitious.index, ambitious.tier) == (1, "Minor")
    assert cs.virtue_flaw_points(c, "Flaw") == 1


def test_the_casting_grid_has_every_technique_and_form():
    saga = _sample_saga_with_covenant()
    c = saga.characters[0]
    grid = cs.casting_grid(saga, c)
    assert len(grid) == 50
    creo_ignem = grid["Creo", "Ignem"]
    text = cs.casting_cell_text(creo_ignem)
    assert f"[b]Casting Score {int(creo_ignem.total)}[/]" in text
    assert "[$label]Creo[/] +10" in text


def test_facts_leave_unset_values_empty_so_a_sheet_can_dim_them():
    saga = _sample_saga_with_covenant()
    character = saga.characters[0]
    character.hermetic.parens = "Ulrich"
    facts = {f.label: f for f in cs.hermetic_facts(character)}
    assert facts["Parens"].value == "Ulrich"
    assert facts["Primus"].missing
    glance = {f.label: f.value for f in cs.glance_facts(saga, character)}
    assert glance["Covenant"] == "Test Covenant"


def test_a_dial_counts_the_points_toward_the_next_score():
    character = _sample_saga_with_covenant().characters[0]
    character.aging.warping_score, character.aging.warping_points = 2, 9
    dial = cs.warping_dial(character)
    assert (dial.score, dial.points, dial.span, dial.top) == (2, 9, 15, 10)
    assert dial.fraction == 0.6
    character.aging.decrepitude, character.aging.decrepitude_points = 1, 9
    assert cs.decrepitude_dial(character) == cs.Dial(1, 4, 10, 5)


def test_the_wound_track_counts_each_wound_in_its_band():
    character = _sample_saga_with_covenant().characters[0]
    character.wounds.light = 2
    bands = cs.wound_track(character)
    assert [b.name for b in bands] == [
        "Light",
        "Medium",
        "Heavy",
        "Incapacitating",
        "Dead",
    ]
    assert (bands[0].count, bands[0].penalty, bands[4].high) == (2, -1, None)
    assert [name for name, _, current in cs.fatigue_track(character) if current] == [
        "Fresh"
    ]
