"""Non-Hermetic traditions: the catalog, the saga's switches, a member's
chapter, and hedge Arts on the Art xp table."""

import pytest

from ars_magica_manager import catalog, traditions
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.models import (
    Ability,
    Character,
    Saga,
    TraditionDef,
    VirtueFlawInstance,
)
from ars_magica_manager.models.definitions import TRADITION_CATEGORIES
from ars_magica_manager.rules import activities
from ars_magica_manager.rules import creation_access as access
from ars_magica_manager.rules import hedge_casting as hc
from ars_magica_manager.rules import hybrid_magic as hybrid
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
    # An instance of a family ("Craft: Runes" of "Craft: {craft}") counts.
    families = {name.split(":")[0] for name in abilities if "{" in name}
    for tradition in entries:
        unknown = {
            name
            for name in set(tradition.abilities) - abilities
            if name.split(":")[0] not in families
        }
        assert not unknown, (tradition.id, unknown)
        assert set(tradition.favored) <= set(tradition.abilities), tradition.id
        assert set(tradition.virtues) <= set(virtues), tradition.id
        if tradition.social_status:
            assert tradition.social_status in virtues, tradition.id


def test_an_unknown_realm_is_rejected():
    with pytest.raises(ValueError, match="realm"):
        TraditionDef(id="t", name="T", realm="Elsewhere")


def test_a_tradition_is_offered_while_its_book_is_in_play_unless_turned_off():
    saga = Saga(id="s", name="S", books_in_play=["HMRE"])
    offered = [t.id for t in traditions.offered(saga)]
    assert "trad_vitkir" in offered
    assert all(
        traditions.book_of(t, saga) in ("DE", "HMRE") for t in traditions.offered(saga)
    )
    traditions.set_on(saga, "trad_vitkir", False)
    assert "trad_vitkir" not in [t.id for t in traditions.offered(saga)]
    saga.books_in_play = []  # the core book only
    assert "trad_elementalists" not in [t.id for t in traditions.offered(saga)]
    # Taking the book out keeps the switch for when it comes back.
    assert saga.traditions_off == ["trad_vitkir"]
    traditions.set_on(saga, "trad_vitkir", True)
    assert saga.traditions_off == []


def test_switches_keep_catalog_order():
    saga = Saga(id="s", name="S")
    traditions.set_on(saga, "trad_vitkir", False)
    traditions.set_on(saga, "trad_elementalists", False)
    assert saga.traditions_off == ["trad_elementalists", "trad_vitkir"]


def test_a_books_traditions_are_listed_under_it_in_the_books_order():
    saga = Saga(id="s", name="S", books_in_play=["HMRE"])
    books = [traditions.book_of(t, saga) for t in traditions.listed(saga)]
    # Grouped: each book's traditions together, the core book's first.
    assert books[0] == "DE"
    assert len(set(books)) == len(
        [b for i, b in enumerate(books) if b not in books[:i]]
    )
    traditions.set_book_on(saga, "HMRE", False)
    under = [
        t for t in traditions.listed(saga) if traditions.book_of(t, saga) == "HMRE"
    ]
    assert saga.traditions_off == [t.id for t in under]
    traditions.set_book_on(saga, "HMRE", True)
    assert saga.traditions_off == []


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


def test_older_saves_load_with_every_tradition_on():
    saga = Saga.from_dict({"id": "s", "name": "S"})
    assert saga.traditions_off == []
    # An older save listed the traditions turned on: it moves to the new
    # default, every one on.
    old = Saga.from_dict({"id": "s", "name": "S", "traditions": ["trad_vitkir"]})
    assert old.traditions_off == []
    assert traditions.is_on(old, "trad_elementalists")
    c = Character.from_dict({"id": "c", "name": "C", "type": "grog"})
    assert c.traditions == []
    assert Ability.from_dict({"name": "Athletics", "xp": 5}).xp_table == "ability"


def test_an_old_medicinal_divining_becomes_the_shared_divining_art():
    old = Ability.from_dict({"name": "Medicinal Divining", "xp": 15})  # score 2
    assert (old.name, old.xp_table, old.level) == ("Elementalist Divining", "art", 2)


def test_every_traditions_chapter_works_out_for_a_new_member():
    """Each tradition's record opens, casts and shows its chapter for a new
    Gifted member (where the tradition takes the Gift) with every Art at 3."""
    from ars_magica_manager import tradition_text
    from ars_magica_manager.models import Saga, VirtueFlawInstance
    from ars_magica_manager.rules import creation_tradition as ct
    from ars_magica_manager.rules import tradition_seasons as ts
    from ars_magica_manager.rules.xp import xp_for_score

    saga = Saga(id="s", name="S")
    for tradition in traditions.all_traditions():
        c = Character(id="c", name="C", type="companion")
        c.traditions = [tradition.id]
        if tradition.training.gift != "never":
            c.virtues_flaws = [VirtueFlawInstance("vf_the_gift")]
        ct.open_tradition(c)
        for name in tradition.abilities:
            if "{" in name:
                continue
            ability = next((a for a in c.abilities if a.name == name), None)
            if ability is None:
                ability = ct.opened_ability(name)
                c.abilities.append(ability)
            ability.xp = xp_for_score(3, ability.factor)
        texts = [
            tradition_text.casting_text(saga, c, tradition),
            tradition_text.defenses_text(c, tradition),
            tradition_text.seasons_text(saga, c, tradition),
            tradition_text.warping_text(saga, c, tradition),
            tradition_text.bonds_text(tradition),
            tradition_text.pools_text(c, tradition),
        ]
        assert all(isinstance(t, str) for t in texts), tradition.id
        assert ts.openable(c) is not None
        assert ct.xp_budget(c) >= 0 and ct.level_budget(c) >= 0, tradition.id
        ct.missing_virtues(c)
        ct.targets(c)


def test_every_tradition_has_a_category_and_says_its_realm_only_when_new():
    shown = {t.id: t for t in traditions.all_traditions()}
    assert all(t.category in TRADITION_CATEGORIES for t in shown.values())
    line = {i: traditions.type_line(t) for i, t in shown.items()}
    assert line["trad_vitkir"] == "Hedge Tradition"
    assert line["trad_ascetics"] == "Holy Tradition"
    assert line["trad_luciferans"] == "Infernal Tradition"
    assert line["trad_ollamhain"] == "Faerie Tradition"
    assert line["trad_lector_priests"] == "Ancient Tradition · Faerie"
    assert line["trad_bouda"] == "Hedge Tradition · Faerie"
    assert line["trad_children_of_olympos"] == "Mystery Cult · Faerie"
    assert line["trad_sahirs"] == "Rival Tradition · Magic, Faerie, Divine or Infernal"
    assert line["trad_hermetic_sahirs"] == "Ex Miscellanea Tradition · Magic or Faerie"


def test_initiation_scripts_alone_dont_make_a_mystery_cult():
    folk = traditions.find("trad_folk_witches")
    assert folk is not None and folk.initiation is not None
    assert folk.category == "Hedge Tradition"


def test_a_tradition_cites_only_the_books_it_is_in():
    sources = {t.id: t.source for t in traditions.all_traditions()}
    assert sources["trad_debterah"] == "LotN"
    assert sources["trad_bedouin_hakima"] == "TC&TC"
    assert sources["trad_imhergi"] == sources["trad_bouda"] == "BS&S"
    assert sources["trad_wordsmiths"] == "TCI"
    assert sources["trad_caerflorons_line"] == "LoH"


def _sahir(realm: str = "") -> Character:
    sahir = Character(id="s", name="Tariq", type="companion", sihr_realm=realm)
    sahir.traditions = ["trad_sahirs"]
    sahir.abilities = [Ability("Sihr", "Supernatural", xp=30)]
    return sahir


def _rule(name: str):
    tradition = traditions.find("trad_sahirs")
    assert tradition is not None
    return tradition, next(r for r in tradition.casting if r.name == name)


def test_a_sahirs_sihr_reads_the_aura_by_its_own_realm():
    # DE p. 545: Magic takes 3 x a Divine aura; Divine powers take nothing
    # from a Magic aura, and Faerie adds half of one.
    tradition, rule = _rule("Summoning")
    aura = {"aura": 4, "aura_realm": "Magic"}
    plain = hc.casting_score(_sahir(), tradition, rule, ["Sihr"], **aura)
    faerie = hc.casting_score(_sahir("Faerie"), tradition, rule, ["Sihr"], **aura)
    divine = hc.casting_score(_sahir("Divine"), tradition, rule, ["Sihr"], **aura)
    assert plain.total - faerie.total == 4 - 2
    assert plain.total - divine.total == 4
    assert hc.power_realm(_sahir("Infernal"), tradition, rule) == "Infernal"


def test_a_sahirs_solomonic_arts_stay_magic():
    tradition, rule = _rule("Naranj")
    assert hc.power_realm(_sahir("Infernal"), tradition, rule) == "Magic"


def test_an_aligned_sihr_changes_the_botch_dice_and_says_what_it_changes():
    tradition, rule = _rule("Summoning")
    realm = hc.power_realm(_sahir("Faerie"), tradition, rule)
    assert (
        hc.botch_dice(tradition, rule, aura=3, aura_realm="Divine", realm=realm)
        == 1 + 3
    )
    assert hc.botch_dice(tradition, rule, aura=3, aura_realm="Faerie", realm=realm) == 1
    assert hc.botch_dice(tradition, rule, aura=3, aura_realm="Faerie") == 1 + 3


def test_the_traditions_form_sets_the_realm_of_sihr_for_one_who_has_it():
    saga = Saga(id="s", name="S")
    sahir = _sahir()
    fields = {f.key: f for f in menu_forms.character_traditions_fields(saga, sahir)}
    assert fields["sihr_realm"].value == "Magic"
    menu_forms.apply_character_traditions(sahir, {"sihr_realm": "Faerie"})
    assert sahir.sihr_realm == "Faerie"
    menu_forms.apply_character_traditions(sahir, {"sihr_realm": "Magic"})
    assert sahir.sihr_realm == ""
    other = Character(id="o", name="O", type="companion")
    keys = [f.key for f in menu_forms.character_traditions_fields(saga, other)]
    assert "sihr_realm" not in keys


def test_a_bad_realm_of_sihr_is_reported_on_load():
    with pytest.raises(ValueError, match="realm of Sihr"):
        Character.from_dict(
            {"id": "c", "name": "C", "type": "grog", "sihr_realm": "Elsewhere"}
        )


def _yatu(realm: str = "") -> Character:
    yatu = _sahir(realm)
    yatu.virtues_flaws.append(VirtueFlawInstance("vf_yatu_magic"))
    return yatu


def test_yatu_magic_reads_every_effect_by_the_better_of_magic_or_faerie():
    tradition, naranj = _rule("Naranj")
    best = lambda who, realm: hc.power_realm(
        who, tradition, naranj, aura=4, aura_realm=realm
    )
    assert best(_yatu(), "Magic") == "Magic"
    assert best(_yatu(), "Faerie") == "Faerie"
    # In a Divine aura, Magic's -3 x the aura beats Faerie's -4 x (DE p. 545).
    assert best(_yatu(), "Divine") == "Magic"
    assert best(_sahir(), "Faerie") == "Magic"


def test_a_yatus_aligned_sihr_takes_the_best_of_three():
    tradition, rule = _rule("Summoning")
    pick = lambda realm: hc.power_realm(
        _yatu("Divine"), tradition, rule, ["Sihr"], aura=4, aura_realm=realm
    )
    assert pick("Faerie") == "Faerie"
    # In Infernal and Divine auras its own Divine Sihr does best.
    assert pick("Divine") == "Divine"
    assert pick("Infernal") == "Divine"


def test_yatu_magics_choice_sets_the_botch_dice():
    tradition, rule = _rule("Naranj")
    yatu = _yatu()
    realm = hc.power_realm(yatu, tradition, rule, aura=3, aura_realm="Faerie")
    assert hc.botch_dice(tradition, rule, aura=3, aura_realm="Faerie", realm=realm) == 1


def test_yatu_magic_gives_no_warping_from_magic_or_faerie_auras():
    assert not hybrid.warps_from_aura(_yatu(), "Magic")
    assert not hybrid.warps_from_aura(_yatu(), "Faerie")
    assert hybrid.warps_from_aura(_sahir(), "Faerie")
    assert hybrid.warps_from_aura(_yatu(), "Infernal")


def test_a_sahirs_summoning_rolls_any_summoning_art_by_its_realm():
    tradition, rule = _rule("Summoning")
    sahir = _sahir()
    sahir.abilities = [Ability("(Faerie) Summoning", "Supernatural", xp=30)]
    assert [c.uses for c in hc.castings(sahir, tradition, rule)] == [
        ("(Faerie) Summoning",)
    ]
    assert hc.power_realm(sahir, tradition, rule, ["(Faerie) Summoning"]) == "Faerie"
    assert hc.power_realm(sahir, tradition, rule, ["Summoning"]) == "Infernal"
    assert hc.power_realm(sahir, tradition, rule, ["Elementalist Summoning"]) == "Magic"
