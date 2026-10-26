"""An aura's kind: Magic alignments (RoP: Magic pp. 15-16), Faerie tints
(RoP: Faerie p. 104), Dominion and Empyreal auras (RoP: The Divine pp.
7-13), and the realm-insight Virtues (Legends of Hermes pp. 14-16)."""

from __future__ import annotations

import pytest
from support import everything_saga

from ars_magica_manager import catalog, places
from ars_magica_manager.models import Ability, VirtueFlawInstance, WoundState
from ars_magica_manager.rules import (
    aura_kinds,
    casting,
    lab,
    realm_insight,
    realms,
    recovery,
    sites,
)
from ars_magica_manager.rules import hybrid_magic as hybrid

# -- the tables --


@pytest.mark.parametrize(
    ("aura", "feeling", "luck"),
    [(0, 0, 0), (1, 1, 1), (3, 1, 1), (4, 2, 1), (5, 2, 2), (6, 2, 2), (7, 3, 2),
     (8, 3, 2), (9, 3, 3), (10, 3, 3)],
)  # fmt: skip
def test_the_aura_effect_table_and_luck(aura, feeling, luck):
    assert aura_kinds.feeling_adjustment(aura) == feeling
    assert aura_kinds.luck_bonus(aura) == luck


def test_alignments_are_an_art_another_or_a_feeling():
    assert aura_kinds.alignment_kind("ignem") == "art"
    assert aura_kinds.aligned_art("ignem") == "Ignem"
    assert aura_kinds.alignment_kind("Healing") == aura_kinds.HEALING
    assert aura_kinds.alignment_kind("lucky") == aura_kinds.LUCK
    assert aura_kinds.alignment_kind("Distracting") == aura_kinds.DISTRACTING
    assert aura_kinds.alignment_kind("Fearful") == "feeling"
    assert aura_kinds.alignment_kind("  ") == ""


def test_healing_is_half_rounded_up_and_distraction_from_five():
    assert [aura_kinds.healing_bonus(a) for a in (1, 2, 3, 5)] == [1, 1, 2, 3]
    assert aura_kinds.distracting_ease(4) == 0
    assert aura_kinds.distracting_ease(5) == 3


def test_an_art_alignment_counts_only_in_a_magic_aura_for_its_art():
    assert aura_kinds.art_bonus("Ignem", "Magic", 4, ("Creo", "Ignem")) == 4
    assert aura_kinds.art_bonus("Ignem", "Magic", 4, ("Creo", "Aquam")) == 0
    assert aura_kinds.art_bonus("Ignem", "Faerie", 4, ("Creo", "Ignem")) == 0
    # A requisite uses the Art too.
    assert aura_kinds.art_bonus("Rego", "Magic", 3, ("Creo", "Ignem", "Rego")) == 3


def test_a_creature_of_the_aligned_form_pays_a_point_less():
    assert aura_kinds.power_cost(2, "Ignem", "Ignem", "Magic") == 1
    assert aura_kinds.power_cost(0, "Ignem", "Ignem", "Magic") == 0
    assert aura_kinds.power_cost(2, "Aquam", "Ignem", "Magic") == 2
    assert aura_kinds.power_cost(2, "Creo", "Creo", "Magic") == 2  # not a Form


def test_tints_read_and_stay_below_the_aura():
    assert aura_kinds.parse_tints("Drawn to Children +3; Light -2") == [
        ("Drawn to Children", 3),
        ("Light", -2),
    ]
    assert aura_kinds.parse_tints("Children") is None
    assert aura_kinds.tints("Children +6, Light -5", 4) == [
        ("Children", 4),
        ("Light", -4),
    ]
    assert aura_kinds.tint_ease(4) == 12
    assert aura_kinds.tint_ease(-12) == 30


def test_dominion_and_empyreal_auras_both_wane_at_night():
    assert aura_kinds.divine_kind("") == aura_kinds.DOMINION
    assert aura_kinds.divine_kind("empyreal") == aura_kinds.EMPYREAL
    assert aura_kinds.divine_aura(4, night=True) == 3
    assert aura_kinds.divine_aura(4, holy_day=True) == 5
    assert aura_kinds.divine_aura(4, "Empyreal", night=True) == 3
    assert aura_kinds.divine_aura(4, "Empyreal", holy_day=True) == 5


def test_empyreal_auras_from_miracles_creatures_and_the_faithful():
    assert aura_kinds.miracle_empyreal(45) == 0
    assert aura_kinds.miracle_empyreal(50) == 1
    assert aura_kinds.miracle_empyreal(65) == 4
    assert aura_kinds.creature_empyreal(35, 1) == 1
    assert aura_kinds.creature_empyreal(35, 9) == 3
    assert not aura_kinds.radiates_empyreal(4)
    assert aura_kinds.radiates_empyreal(5)


def test_a_form_refuses_tints_it_cannot_read():
    assert aura_kinds.problem({"realm": "Faerie", "tints": "Light +3"}) is None
    assert aura_kinds.problem({"realm": "Faerie", "tints": "Light"})
    assert aura_kinds.problem({"realm": "Faerie", "tints": "Light +11"})
    # Not a Faerie aura: its tints aren't read.
    assert aura_kinds.problem({"realm": "Magic", "tints": "Light"}) is None


# -- on a place --


def _drachenfels(saga):
    found = sites.place(saga, "drachenfels")
    assert found is not None
    return found


def test_a_place_and_its_levels_keep_their_kind_by_realm():
    saga = everything_saga()
    drachenfels = _drachenfels(saga)  # Magic 5, Faerie 6, Magic 7
    drachenfels.details["alignment"] = "Ignem"
    drachenfels.details["tints"] = "Light +2"  # not a Faerie aura: unread
    sites.levels(drachenfels)[0]["tints"] = "Drawn to Children +3"
    assert sites.aura_kind_at(drachenfels, 0) == "Ignem"
    assert sites.aura_kind_at(drachenfels, 1) == "Drawn to Children +3"
    assert sites.aura_kind_at(drachenfels, 2) == ""
    facts = {f.label: f.value for f in places.facts(saga, drachenfels)}
    assert facts["Aura kind"].startswith("aligned with Ignem: +5 more")
    assert (
        "Level 1: tinted: everyone here takes Drawn to Children +3" in (facts["Within"])
    )


def test_the_forms_ask_each_realm_for_its_own_kind():
    saga = everything_saga()
    drachenfels = _drachenfels(saga)
    shown = {
        f.key: f
        for f in places.fields(saga, drachenfels)
        if f.key in aura_kinds.KIND_KEYS.values()
    }
    assert set(shown) == {"alignment", "tints", "divine_kind"}
    assert shown["alignment"].show_if is not None
    assert shown["alignment"].show_if({"realm": "Magic"})
    assert not shown["alignment"].show_if({"realm": "Faerie"})
    assert shown["divine_kind"].show_if({"realm": "Divine"})
    level = places.level_fields(saga, drachenfels, None)
    assert {"alignment", "tints", "divine_kind"} <= {f.key for f in level}


def test_an_empyreal_place_says_so_and_a_dominion_its_hours():
    saga = everything_saga()
    drachenfels = _drachenfels(saga)
    drachenfels.realm = "Divine"
    facts = {f.label: f.value for f in places.facts(saga, drachenfels)}
    assert facts["Aura kind"].startswith("Dominion: 4 at night, 6 on Sundays")
    drachenfels.details["divine_kind"] = "Empyreal"
    facts = {f.label: f.value for f in places.facts(saga, drachenfels)}
    assert facts["Aura kind"].startswith(
        "Empyreal: from no worship; 4 at night, 6 on Sundays"
    )


# -- where the aura counts --


def _placed(saga, alignment: str, level: int = 0):
    drachenfels = _drachenfels(saga)
    if level:
        sites.levels(drachenfels)[level - 1]["alignment"] = alignment
    else:
        drachenfels.details["alignment"] = alignment
    covenant = saga.covenants[0]
    covenant.place_id, covenant.place_level = "drachenfels", level
    places.sync(saga)
    magus = saga.character("mag1")
    assert magus is not None
    return magus


def test_an_aligned_aura_counts_again_in_the_casting_score():
    saga = everything_saga()
    magus = _placed(saga, "Ignem")
    aura, realm = realms.home_aura(saga, magus)
    kind = realms.home_aura_kind(saga, magus)
    assert (realm, kind) == ("Magic", "Ignem")
    fire = casting.casting_score(
        magus, "Creo", "Ignem", aura=aura, aura_realm=realm, aura_kind=kind
    )
    water = casting.casting_score(
        magus, "Creo", "Aquam", aura=aura, aura_realm=realm, aura_kind=kind
    )
    aligned = [line for line in fire.lines if line.label == "Aura aligned with Ignem"]
    assert [line.amount for line in aligned] == [aura]
    assert not any(line.label.startswith("Aura aligned") for line in water.lines)


def test_an_aligned_aura_counts_again_in_the_lab_total():
    saga = everything_saga()
    magus = _placed(saga, "Herbam")
    laboratory = saga.laboratory("lab1")
    assert laboratory is not None
    herbam = lab.lab_total(saga, magus, "Creo", "Herbam", laboratory)
    ignem = lab.lab_total(saga, magus, "Creo", "Ignem", laboratory)
    aura, _ = lab.lab_aura(saga, laboratory)
    found = [line.amount for line in herbam.lines if line.label.startswith("Aura al")]
    assert found == [aura]
    assert not any(line.label.startswith("Aura al") for line in ignem.lines)


def test_a_healing_aura_adds_half_to_recovery():
    saga = everything_saga()
    magus = _placed(saga, "Healing")
    aura, _ = realms.home_aura(saga, magus)
    total = recovery.total(saga, magus, WoundState("light"))
    found = [line.amount for line in total.lines if line.label == "Healing aura"]
    assert found == [aura_kinds.healing_bonus(aura)]


# -- the realm-insight Virtues --


def _with(magus, vf_id: str, lore: str = "", xp: int = 0):
    magus.virtues_flaws.append(VirtueFlawInstance(vf_id))
    if lore:
        magus.abilities.append(Ability(lore, category="Arcane", xp=xp))
    return magus


def test_the_virtues_are_in_the_catalog():
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    assert by_id[realm_insight.CONFLUENCE].tier == "Minor"
    assert by_id[realm_insight.INSIGHT].tier == "Minor"
    assert by_id[realm_insight.TRUE_UNDERSTANDING].tier == "Major"
    boons = catalog.load_covenant_boon_hook_catalog_by_id()
    assert boons["covbh_boon_major_fine_aura"].tier == "Major"
    assert boons["covbh_hook_minor_troublesome_aura"].type == "Hook"


def test_true_understanding_lessens_a_foreign_aura_by_its_lore():
    saga = everything_saga()
    magus = saga.character("mag1")
    assert magus is not None
    plain_mod, _ = hybrid.aura_modifier(magus, "Divine", 3)
    plain_dice = hybrid.foreign_botch_dice(magus, "Divine", 3)
    _with(magus, realm_insight.TRUE_UNDERSTANDING, "Dominion Lore", 15)  # 2
    assert realm_insight.effective_aura(magus, "Divine", 3) == 1
    amount, why = hybrid.aura_modifier(magus, "Divine", 3)
    assert (plain_mod, amount, why) == (-9, -3, "True Understanding of the Realms")
    assert (plain_dice, hybrid.foreign_botch_dice(magus, "Divine", 3)) == (3, 1)
    label, shown = hybrid.aura_label(magus, "Divine", 3)
    assert shown == -3 and label.endswith("True Understanding of the Realms")


def test_true_understanding_keeps_a_faerie_bonus_and_drops_its_botch_dice():
    saga = everything_saga()
    magus = saga.character("mag1")
    assert magus is not None
    _with(magus, realm_insight.TRUE_UNDERSTANDING, "Faerie Lore", 15)  # 2
    assert hybrid.aura_modifier(magus, "Faerie", 2) == (1, "")
    assert hybrid.foreign_botch_dice(magus, "Faerie", 2) == 0
    # His own realm's aura is untouched.
    assert realm_insight.effective_aura(magus, "Magic", 5) == 5


def test_insight_puts_a_realms_lore_in_a_rituals_learning():
    saga = everything_saga()
    magus = saga.character("mag1")
    assert magus is not None
    _with(magus, realm_insight.INSIGHT, "Faerie Lore", 75)  # 5
    found = {"Artes Liberales": 1, "Philosophiae": 2}
    swapped = realm_insight.learning_scores(found, magus, "Faerie", 3)
    assert swapped == {
        "Philosophiae": 2,
        "Faerie Lore (for Artes Liberales, Insight of the Realms)": 5,
    }
    # Not in a Faerie aura, or no better: unchanged.
    assert realm_insight.learning_scores(found, magus, "Faerie", 0) == found
    assert realm_insight.learning_scores(found, magus, "Divine", 3) == found
    assert realm_insight.regio_abilities(magus, "Faerie") == ("Faerie Lore",)
    score = casting.casting_score(
        magus, "Creo", "Ignem", aura=3, aura_realm="Faerie", ritual=True
    )
    assert any("Insight of the Realms" in line.label for line in score.lines)
