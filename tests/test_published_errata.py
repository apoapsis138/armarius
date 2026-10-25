"""Atlas Games' published errata, as the catalogs, the shipped Tribunal
packs and the rules constants carry them."""

from __future__ import annotations

import json

import pytest

from ars_magica_manager import book_packs, catalog
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    Characteristics,
    Saga,
    SeasonPlan,
    XpAllocation,
)
from ars_magica_manager.rules import book_seasons as bs
from ars_magica_manager.rules import languages
from ars_magica_manager.rules.xp import ability_xp, art_xp


@pytest.mark.parametrize(
    ("spell_id", "level", "range_", "target"),
    [
        ("spell_thought_distinctly_burned", 15, "Voice", "Group"),  # Covenants p. 97
        ("spell_sight_of_the_warm_surface", 20, "Sight", "Group"),  # HoH:S p. 65
        ("spell_reveal_the_lingering_spirit", 30, "Personal", "Vision"),  # HoH:TL p. 14
        ("spell_a_window_of_singular_direction", 15, "Touch", "Part"),  # HoH:TL p. 141
        ("spell_craft_the_mechanism", 20, "Touch", "Individual"),  # TMRE p. 52
        ("spell_duplicate_the_mechanism", 25, "Touch", "Individual"),  # TMRE p. 52
        ("spell_familial_secrets", 35, "Touch", "Bloodline"),  # MoH p. 60
        ("spell_arachne_s_tuition", 25, "Touch", "Individual"),  # MoH p. 101
        ("spell_the_ob_of_mot", 25, "Veil", "Individual"),  # AM p. 32
        ("spell_links_of_stone", 20, "Arcane Connection", "Individual"),  # AM p. 36
        ("spell_the_key_of_theodorus", 5, "Touch", "Part"),  # C&G p. 78
        (
            "spell_adjuration_of_the_hell_sworn_spirit",
            35,
            "Arcane Connection",
            "Individual",
        ),
        ("spell_lungs_of_drowning", 15, "Touch", "Individual"),  # HP p. 86
        ("spell_the_prodigal_returns", 15, "Sight", "Individual"),  # HP p. 90
        ("spell_curse_of_the_baby_s_bladder", 4, "Voice", "Individual"),  # App p. 46
        ("spell_sudden_well", 25, "Voice", "Part"),  # AtD p. 31
        ("spell_eyes_of_danibus", 25, "Arcane Connection", "Individual"),  # Hooks p. 79
        ("spell_the_hidden_warren", 45, "Touch", "Part"),  # DI p. 69
    ],
)
def test_catalog_spells_carry_the_errata(spell_id, level, range_, target):
    spell = catalog.load_spell_catalog_by_id()[spell_id]
    assert (spell.level, spell.range, spell.target) == (level, range_, target)


def test_catalog_spell_arts_and_rituals_follow_the_errata():
    spells = catalog.load_spell_catalog_by_id()
    assert spells["spell_the_ob_of_mot"].technique == "Rego"
    assert spells["spell_craft_the_mechanism"].requisites == []
    assert spells["spell_the_elfin_baker"].requisites == ["Aquam"]
    assert spells["spell_the_hidden_warren"].requisites == ["Rego"]
    assert spells["spell_diverting_the_river"].ritual


def test_virtues_and_lab_virtues_follow_the_errata():
    virtues = catalog.load_virtue_flaw_catalog_by_id()
    assert virtues["vf_immortality_of_the_forest"].category == "Supernatural"
    assert "faerie power" not in virtues["vf_feminine_sympathy"].description
    ice = catalog.load_lab_virtue_flaw_catalog_by_id()["labvf_ice_cavern"]
    assert "Aquam" in ice.description and "Terram" not in ice.description


def test_danish_is_east_norse():
    """Guardians of the Forests p. 138, as corrected."""
    assert languages.penalty("Living Language: Low German", "East Norse", "Saxon") == 2
    assert languages.penalty("Living Language: High German", "East Norse") == 4


def _writer() -> tuple[Saga, Character]:
    magus = Character(id="m", name="Tiberius", type="magus")
    magus.characteristics = Characteristics(communication=2)
    magus.abilities = [
        Ability("Dead Language: Latin", xp=ability_xp(5)),
        Ability("Profession: Scribe", xp=ability_xp(4)),
    ]
    magus.arts = {"creo": ArtScore(xp=art_xp(10))}
    saga = Saga(id="s", name="S", characters=[magus])
    saga.rule_options = {"extended_book_quality": True}
    return saga, magus


def test_extended_rules_give_a_tractatus_communication_plus_3():
    """Covenants p. 88, as corrected: + 3 after the author's Communication."""
    saga, magus = _writer()
    plan = SeasonPlan(
        "m", 1220, "Spring", bs.WRITE_TRACTATUS, allocations=[XpAllocation("art:Creo")]
    )
    _, work = bs.work(saga, magus, plan)
    assert work is not None and work.made.quality == 2 + 3


def test_extended_rules_give_no_bonus_for_a_mundane_subject():
    """Covenants p. 88, as corrected: the +3 for non-magical subjects is gone."""
    saga, magus = _writer()
    plan = SeasonPlan(
        "m",
        1220,
        "Spring",
        bs.WRITE_TRACTATUS,
        allocations=[XpAllocation("ability:Profession: Scribe")],
    )
    _, work = bs.work(saga, magus, plan)
    assert work is not None and work.made.quality == 2 + 3


def _shipped(key: str) -> dict:
    path = book_packs.path_of(book_packs.PACKS[key])
    return json.loads(path.read_text(encoding="utf-8"))["saga"]


def test_the_rhine_pack_carries_the_reduced_mights():
    mights = {c["name"]: c["might"] for c in _shipped("rhine")["creatures"]}
    assert mights["The Courts of the Seasons"] == 30
    assert mights["The King Fir of the Black Forest"] == 60
    assert mights["The Glade of the Seven Waterfalls"] == 50
    assert mights["The Ash of Nortorf"] == 10
    assert mights["The Teutoburger Forest"] == 40
    assert mights["The Apple of the Kyffhäuser"] == 45
    assert mights["The Linden of Neustadt"] == 25
    assert mights["The Holm Oak of Romowe"] == 35


def test_philippus_niger_knows_two_shattering_spells():
    saga = _shipped("rhine")
    philippus = next(c for c in saga["characters"] if c["name"] == "Philippus Niger")
    own = {s["name"]: s["level"] for s in philippus["invented_spells"]}
    assert own == {
        "Shattering the Malicious Thurisaz": 30,
        "Shattering the Malicious Kauno": 50,
    }


def test_the_cradle_ghuls_have_corpus_might():
    forms = {c["name"]: c["might_form"] for c in _shipped("cradle")["creatures"]}
    assert forms["Ghula (Faerie)"] == "Corpus"
    assert forms["Ghul (Infernal)"] == "Corpus"
