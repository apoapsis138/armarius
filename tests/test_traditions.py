"""Non-Hermetic traditions: the catalog, the saga's switches, a member's
chapter, and hedge Arts on the Art xp table."""

import pytest

from ars_magica_manager import catalog, traditions
from ars_magica_manager.models import (
    Ability,
    Character,
    Saga,
    TraditionDef,
)
from ars_magica_manager.rules import activities
from ars_magica_manager.rules import creation_access as access
from ars_magica_manager.sheets import character as cs


def _witch(*abilities: Ability) -> Character:
    c = Character(id="c1", name="Gunnhild", type="companion")
    c.traditions = ["trad_folk_witches"]
    c.abilities = list(abilities)
    return c


def test_every_tradition_names_catalog_abilities_and_virtues():
    abilities = {e.name for e in catalog.load_ability_catalog()}
    virtues = catalog.load_virtue_flaw_catalog_by_id()
    entries = traditions.all_traditions()
    assert {t.id for t in entries} >= {
        "trad_elementalists", "trad_folk_witches", "trad_gruagachan",
        "trad_learned_magicians", "trad_nightwalkers", "trad_vitkir",
    }  # fmt: skip
    for tradition in entries:
        templated = {"Craft: Runes"}  # an instance of "Craft: {craft}"
        assert set(tradition.abilities) - templated <= abilities, tradition.id
        assert set(tradition.favored) <= set(tradition.abilities), tradition.id
        assert set(tradition.virtues) <= set(virtues), tradition.id
        if tradition.social_status:
            assert tradition.social_status in virtues, tradition.id


def test_an_unknown_realm_is_rejected():
    with pytest.raises(ValueError, match="realm"):
        TraditionDef(id="t", name="T", realm="Elsewhere")


def test_a_tradition_is_offered_only_once_turned_on_and_with_its_book():
    saga = Saga(id="s", name="S")
    assert traditions.offered(saga) == []
    traditions.set_on(saga, "trad_vitkir", True)
    assert [t.id for t in traditions.offered(saga)] == ["trad_vitkir"]
    saga.books_in_play = []  # the core book only
    assert traditions.offered(saga) == []
    # Taking the book out keeps the switch for when it comes back.
    assert saga.traditions == ["trad_vitkir"]
    saga.books_in_play = None
    traditions.set_on(saga, "trad_vitkir", False)
    assert saga.traditions == []


def test_switches_keep_catalog_order():
    saga = Saga(id="s", name="S")
    traditions.set_on(saga, "trad_vitkir", True)
    traditions.set_on(saga, "trad_elementalists", True)
    assert saga.traditions == ["trad_elementalists", "trad_vitkir"]


def test_a_members_tradition_abilities_leave_the_abilities_chapter():
    witch = _witch(
        Ability("Athletics", xp=5),
        Ability("Folk Witch Magic Theory", "Arcane", xp=15),
        Ability("Second Sight", "Supernatural", xp=5),
    )
    tradition = traditions.find("trad_folk_witches")
    assert tradition is not None
    assert [r.name for r in cs.abilities_chapter_table(witch)] == ["Athletics"]
    rows = cs.tradition_table(witch, tradition)
    # Second Sight comes before the Theory: the tradition's own order.
    assert [r.name for r in rows] == ["Second Sight", "Folk Witch Magic Theory"]
    assert {r.category for r in rows} == {"Abilities"}
    # Everyone else keeps every Ability in the Abilities chapter.
    witch.traditions = []
    assert len(cs.abilities_chapter_table(witch)) == 3


def test_a_chapter_groups_arts_by_role():
    vitki = Character(id="v", name="Ulf", type="companion")
    vitki.traditions = ["trad_vitkir"]
    vitki.abilities = [Ability("Rune Magic", "Arcane"), Ability("Fehu", "Hedge Art")]
    tradition = traditions.find("trad_vitkir")
    assert tradition is not None
    assert [
        (h, [a.name for _, a in g])
        for h, g in traditions.chapter_groups(vitki, tradition)
    ] == [("Runes", ["Fehu"]), ("Abilities", ["Rune Magic"])]


def test_an_accelerated_ability_advances_on_the_art_table():
    assert access.ability_xp_table("Fehu") == "art"
    assert access.ability_xp_table("Gruagach Give") == "ability"  # Difficult
    assert access.ability_xp_table("Athletics") == "ability"
    assert access.ability_xp_table("Not In The Catalog") == "ability"
    fehu = Ability("Fehu", "Hedge Art", xp=10, xp_table="art")
    assert fehu.level == 4  # 1 + 2 + 3 + 4 xp, as an Art
    assert Ability("Athletics", xp=10).level == 1
    assert activities.subject_factor("ability:Fehu") == 1
    assert activities.subject_factor("ability:Athletics") == 5


def test_older_saves_load_with_no_traditions():
    saga = Saga.from_dict({"id": "s", "name": "S"})
    assert saga.traditions == []
    c = Character.from_dict({"id": "c", "name": "C", "type": "grog"})
    assert c.traditions == []
    assert Ability.from_dict({"name": "Athletics", "xp": 5}).xp_table == "ability"


def test_an_old_medicinal_divining_becomes_the_shared_divining_art():
    old = Ability.from_dict({"name": "Medicinal Divining", "xp": 15})  # score 2
    assert (old.name, old.xp_table, old.level) == ("Elementalist Divining", "art", 2)
