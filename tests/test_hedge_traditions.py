"""Hedge traditions: the folk witches' kitchen and Witch Moon (Hedge
Magic RE pp. 33-54), nightwalkers (pp. 103-119), the Saxon runes
(Thrice-Told Tales pp. 139-143) and the clesrada (The Contested Isle
pp. 101-105)."""

import pytest

from ars_magica_manager import catalog, sourcebooks, tradition_text
from ars_magica_manager.models import (
    Character,
    Characteristics,
    Saga,
    SeasonPlan,
    TraditionEffect,
    VirtueFlawInstance,
    XpAllocation,
)
from ars_magica_manager.rules import activities, clesrada
from ars_magica_manager.rules import creation_access as access
from ars_magica_manager.rules import creation_tradition as ct
from ars_magica_manager.rules import folk_witches as fw
from ars_magica_manager.rules import hedge_effects as he
from ars_magica_manager.rules import nightwalkers as nw
from ars_magica_manager.rules.xp import xp_for_score


def _t(tradition_id: str):
    return catalog.load_tradition_catalog_by_id()[tradition_id]


def _member(tradition_id: str, *vf_ids: str, gifted: bool = True) -> Character:
    character = Character(id="c", name="Eliza", type="companion")
    character.traditions = [tradition_id]
    ids = (["vf_the_gift"] if gifted else []) + list(vf_ids)
    character.virtues_flaws = [VirtueFlawInstance(v) for v in ids]
    ct.open_tradition(character)
    return character


def _set(character: Character, name: str, score: int) -> None:
    ability = next((a for a in character.abilities if a.name == name), None)
    if ability is None:
        ability = ct.opened_ability(name)
        character.abilities.append(ability)
    ability.xp = xp_for_score(score, ability.factor)


def _book_witch(*vf_ids: str) -> Character:
    """The brewing example (Hedge Magic RE p. 40): Int +1, Folk Witch
    Magic Theory 4, Healing 5."""
    witch = _member("trad_folk_witches", *vf_ids)
    witch.characteristics = Characteristics(intelligence=1, stamina=1)
    _set(witch, fw.THEORY, 4)
    _set(witch, "Healing", 5)
    return witch


# ---------------------------------------------------------------------------
# Folk witches


def test_the_books_healing_brew():
    witch = _book_witch()
    found = fw.brew(witch, _t(fw.TRADITION_ID), "Healing", aura=3, effect_vis=3)
    assert (found.potency, found.doses, found.vis, found.vis_limit) == (13, 4, 7, 8)
    assert found.affordable == 4
    # With a Lab Text of level 4: eight doses cost 11, too much; five can be made.
    texted = fw.brew(
        witch, _t(fw.TRADITION_ID), "Healing", aura=3, effect_vis=3, lab_text_level=4
    )
    assert (texted.doses, texted.vis, texted.affordable) == (8, 11, 5)
    assert fw.potion_lab_text_level(witch) == 4


def test_brewing_virtues_and_the_sabbat():
    tradition = _t(fw.TRADITION_ID)
    expert = fw.brew(_book_witch(fw.EXPERT_BREWER), tradition, "Healing", aura=3)
    assert expert.potency == 18  # the power counts twice
    assert fw.vis_limit(_book_witch(fw.CONCENTRATED_POTIONS)) == 16
    # Three sisters help, but the Magic aura at the sabbat is 2.
    helped = fw.brew(
        _book_witch(), tradition, "Healing", aura=3, sabbat_helpers=3, sabbat_aura=2
    )
    assert helped.potency == 15
    # The power isn't counted twice outside a brew.
    assert (
        fw.power_lab_total(_book_witch(fw.EXPERT_BREWER), tradition, "Healing", aura=3)
        == 13
    )


def test_a_potion_drunk():
    assert fw.potion_casting_total(13, 4) == 17
    assert fw.potion_penetration(13, 4, 6) == 11
    assert fw.potion_works(13, 4, 6, None)
    assert fw.potion_works(13, 4, 6, 10)
    assert not fw.potion_works(13, 4, 6, 11)  # must beat the resistance
    assert not fw.potion_works(10, 2, 18, None)  # a beast curse needs 18
    assert (fw.potion_score(13), fw.potion_days(13), fw.potion_magnitude(13)) == (
        3,
        13,
        2,
    )


def test_the_kitchens_other_work():
    witch = _book_witch()
    tradition = _t(fw.TRADITION_ID)
    assert fw.plain_lab_total(witch, tradition, aura=3) == 8
    assert fw.extracted_vis(8) == 1
    assert fw.extracted_vis(11) == 2
    assert fw.fixed_connection("weeks", 8) == "8 months"
    assert fw.fixed_connection("hours", 8) == "8 days"
    assert fw.fixed_connection("years", 8) == "8 decades"
    for lifetime in ("forever", "decades", "indefinite"):
        with pytest.raises(ValueError):
            fw.fixed_connection(lifetime, 8)
    assert fw.can_set_up_kitchen(witch)
    assert not fw.can_convert_laboratory(witch)  # no Magic Theory
    assert fw.kitchen_size(0) == 3
    assert fw.familiar_binding_total(-4, 0) == 6
    assert fw.binds_familiar(7, -4, 0) and not fw.binds_familiar(6, -4, 0)
    assert fw.familiar_lab_bonus(-3, 2) == -1
    assert fw.investigation_total(witch, 4) == 9


def test_powers_in_play():
    assert fw.flight_combat_bonus(3, opponent_flies=False) == 3
    assert fw.flight_combat_bonus(3, opponent_flies=True) == 0
    assert fw.flight_fatigue(fetish=True) == 1
    assert fw.flight_fatigue(fetish=False, botches=2) == 2
    assert fw.healing_vis(9) == 4 and fw.healing_vis(9, fatigue=True) == 2
    with pytest.raises(ValueError):
        fw.healing_vis(7)
    assert fw.mark_ease(which_witch=True) == 9
    assert fw.mark_ease(which_witch=False) == 6
    assert fw.life_linked_bonus(_book_witch(), 2) == 0
    assert fw.life_linked_bonus(_book_witch(fw.LIFE_LINKED), 2) == 10


def test_the_witch_moon():
    witch = _book_witch()
    witch.aging.warping_score = 2
    assert fw.moon_total(witch, 7) == 6 and fw.moon_ends(witch, 7)
    assert not fw.moon_ends(witch, 6)
    assert fw.moon_wound(witch) == "Medium"
    assert fw.moon_wound(_book_witch(fw.HARSH_MOON)) == "Heavy"
    assert fw.moon_wound(_book_witch(fw.PAINLESS_MOON)) == ""
    assert fw.moon_experience(2, 2) == "good"
    assert fw.moon_experience(3, 2) == "bad"
    assert (fw.moon_xp_gained(3), fw.moon_xp_lost(3)) == (15, 6)


def test_covens():
    assert fw.coven_power(143) == "Low"  # the Witches of Reims
    assert fw.coven_power(150) == "Medium"
    assert fw.coven_power(599) == "High"
    assert fw.coven_power(600) == "Legendary"
    # Reims's four scripts: +6, +6, +10, +7 Build Points.
    assert sum(fw.script_build_points(b) for b in (6, 6, 10, 7)) == 29


def test_a_brewing_season_says_what_it_makes():
    witch = _book_witch()
    saga = Saga(id="x", name="X", characters=[witch])
    keys = [a.key for a in activities.activities_for(witch)]
    assert {"folk_witch_extract_vis", "folk_witch_fix_connection"} <= set(keys)
    plan = SeasonPlan(
        "c", 1220, "Spring", "folk_witch_brew",
        allocations=[XpAllocation("ability:Healing", 0)],
    )  # fmt: skip
    outcome = activities.outcome(witch, plan, saga)
    assert outcome.problems == []
    notes = " ".join(outcome.notes)
    assert "Folk witch Lab Total (Healing): 10." in notes  # no aura at home
    assert "Brew Potency 10" in notes and "4 doses" in notes
    plan = SeasonPlan(
        "c", 1220, "Spring", "folk_witch_extract_vis",
        allocations=[XpAllocation(f"ability:{fw.THEORY}", 0)],
    )  # fmt: skip
    notes = " ".join(activities.outcome(witch, plan, saga).notes)
    assert "Folk witch Lab Total (no power) (Folk Witch Magic Theory): 5." in notes
    assert "1 pawns of Vim vis" in notes


# ---------------------------------------------------------------------------
# Nightwalkers


def test_straying():
    assert nw.insensibility_minutes(3) == 7
    assert nw.insensibility_minutes(12) == 1
    assert nw.straying_fatigue() == 1  # any time up to an hour
    assert nw.straying_fatigue(talked=True) == 2
    assert nw.straying_fatigue(whole_night=True, talked=True) == 3
    assert nw.travel_ease("seen this year", objects=1) == 12
    assert nw.lead_astray_ease("seen daily") == 6
    with pytest.raises(ValueError):
        nw.travel_ease("the moon")
    arno = Character(id="a", name="Arno", type="companion")
    arno.characteristics = Characteristics(stamina=1, presence=0)
    assert nw.travel_total(arno, 1, 5) == 7
    assert nw.stays_awake(arno, 0, 2) and not nw.stays_awake(arno, 0, 1)
    assert nw.form_change(in_combat=True) == "Stamina + Concentration against 15"


def test_the_phantasticum_combines_characteristics():
    assert nw.combined_characteristic(-1, -3) == -3
    assert nw.combined_characteristic(2, 3) == 3
    assert nw.combined_characteristic(-2, 3) == 1
    taltos = Character(id="t", name="T", type="companion")
    taltos.characteristics = Characteristics(intelligence=1, perception=1, strength=-1)
    flame = nw.phantastic_characteristics(taltos, nw.FLAME_SHAPE)
    assert flame["intelligence"] == 1
    assert flame["perception"] == -7  # +1 and -8 added
    assert flame["strength"] == 3  # -1 and +4 added
    assert flame["presence"] == 0


def test_fertility_battles_and_the_dead():
    assert nw.battle_income("wins the field") == "Status Quo"
    assert nw.battle_income("traps and annihilates the enemy militia") == "Boom"
    assert nw.harvest("routs its enemies") == "bountiful"
    assert nw.harvest("wins the field") == "normal"
    assert nw.harvest("routed") == "failed"
    with pytest.raises(ValueError):
        nw.battle_income("a draw")
    assert nw.recognition_ease(2) == 13
    assert nw.recognition_ease(2, battle=False, waking="weekly") == 4
    assert nw.witch_recognition_ease(3) == 15
    assert nw.intimidation_ease(2, ghost_allies=3) == 11
    arno = Character(id="a", name="Arno", type="companion")
    arno.characteristics = Characteristics(presence=1)
    assert nw.intimidation_total(arno, 2, 5, allies=2) == 10
    assert nw.question_ease("a sentence") == 6


def test_the_nightwalkers_rolls_are_on_the_sheet():
    tradition = _t(nw.TRADITION_ID)
    names = [r.name for r in tradition.casting]
    assert names[0] == "Spirit travel"
    assert {"Lead a spirit astray", "Question the dead"} <= set(names)
    arno = _member(nw.TRADITION_ID, "vf_nightwalker", gifted=False)
    _set(arno, "Leadership", 2)
    text = tradition_text.casting_text(Saga(id="x", name="X"), arno, tradition)
    assert "Lead a spirit astray" in text and "Leadership (Sta)" in text


# ---------------------------------------------------------------------------
# The Saxon runes


def test_the_saxon_runes_are_vitkar_runes():
    vitkir = _t("trad_vitkir")
    saxon = ["Ac", "Æsc", "Yr", "Ear", "Gar", "Calc", "Cweorth", "Stan", "Ior"]
    assert set(saxon) <= set(vitkir.abilities)
    assert not set(saxon) & set(vitkir.training.opening)  # by Initiation only
    assert access.ability_xp_table("Æsc") == "art"
    assert sourcebooks.titles("TTT") == "Thrice-Told Tales"
    runes = {g.arts[0] for g in vitkir.guidelines if g.page in (140, 141, 142)}
    assert runes == set(saxon) - {"Ac"}  # Ac has no printed guidelines


def test_a_saxon_rune_script_has_its_guidelines_level():
    vitkir = _t("trad_vitkir")
    script = TraditionEffect(
        "Egil's Arrow", tradition="trad_vitkir", kind="rune script",
        rule="Rune script", uses=["Yr"], guideline="Yr: Unerring missile",
    )  # fmt: skip
    assert he.effect_level(vitkir, script) == 20
    general = TraditionEffect(
        "Commemorate the Dead", tradition="trad_vitkir", kind="rune script",
        rule="Rune script", uses=["Calc", "Ear"], guideline="Raise a Reputation",
        level=15,
    )  # fmt: skip
    assert he.effect_level(vitkir, general) == 15  # General: its own level
    vitki = _member("trad_vitkir")
    vitki.characteristics = Characteristics(stamina=2)
    _set(vitki, "Yr", 6)
    found = he.effect_total(vitki, vitkir, script)
    assert found is not None and found.score == 8 and found.die == 12


# ---------------------------------------------------------------------------
# The clesrada


def _redcap(*vf_ids: str) -> Character:
    redcap = _member(clesrada.TRADITION_ID, *vf_ids, gifted=False)
    redcap.characteristics = Characteristics(dexterity=2, strength=1)
    _set(redcap, "Thrown Weapon", 4)
    _set(redcap, "Athletics", 3)
    return redcap


def test_the_clesrada_entry():
    tradition = _t(clesrada.TRADITION_ID)
    assert tradition.realm == "Faerie" and tradition.source == "TCI"
    assert len(tradition.guidelines) == len(clesrada.CLESA) == 18
    initiation = tradition.initiation
    assert initiation is not None and not initiation.self_initiation
    script = initiation.scripts[0]
    assert (script.ease_factor, script.bonus) == (15, 6)
    # Each cles in the catalog matches the module's table.
    for cles in clesrada.CLESA:
        g = next(g for g in tradition.guidelines if g.name.startswith(cles.name + " ("))
        assert g.level == cles.ease
        assert g.summary.startswith(f"{cles.characteristic[:3]} + {cles.ability}")


def test_a_feat_roll():
    redcap = _redcap()
    javelin = clesrada.find("Javelin Feat")
    assert clesrada.feat_total(redcap, javelin, 4) == 10
    # A Faerie power: a Faerie aura adds, a Divine one takes away.
    assert clesrada.feat_total(redcap, javelin, 4, aura=2, aura_realm="Faerie") == 12
    assert clesrada.feat_total(redcap, javelin, 4, aura=1, aura_realm="Divine") == 6
    rope = clesrada.find("Tétchless")
    assert clesrada.feat_total(redcap, rope, 0) == 5
    assert clesrada.feat_total(_redcap(clesrada.PERFECT_BALANCE), rope, 0) == 11
    stroke = clesrada.find("Stroke of Precision")
    assert clesrada.feat_total(redcap, stroke, 0, ability="Great Weapon") == 2
    with pytest.raises(ValueError):
        clesrada.feat_total(redcap, javelin, 0, ability="Brawl")
    with pytest.raises(LookupError):
        clesrada.find("Somersault")


def test_the_feats_own_numbers():
    assert clesrada.chain([(10, 9), (12, 9), (5, 9), (20, 3)]) == 2
    assert clesrada.rope_ease(unstable=True, moving=True) == 9
    assert clesrada.rope_ease(slope=60) == 9 and clesrada.rope_ease(slope=30) == 6
    assert clesrada.fall_damage_ignored(8) == 2
    assert clesrada.nine_men_ease(9) == 14
    assert clesrada.apple_ease(3) == 9
    assert clesrada.thunder_ease(5) == 11
    assert clesrada.swooping_ease(4) == 7 and clesrada.swooping_protection_lost(4) == 1
    assert clesrada.crushing_roar_ease("Enchanted") == 15
    assert clesrada.profit_of_speed(1, 0) == (33, 66)
    assert clesrada.cat_feat_heights(3) == 5
    assert clesrada.salmon_leap_heights(3) == 2
    assert clesrada.javelin_damage(1, 3, 2) == 10


def test_a_known_cles_shows_the_die_it_needs():
    tradition = _t(clesrada.TRADITION_ID)
    redcap = _redcap()
    cles = TraditionEffect(
        "Javelin Feat", tradition=clesrada.TRADITION_ID, kind="power",
        rule="Feat roll (Dexterity)", uses=["Thrown Weapon"],
        guideline="Cless Cletenach (Javelin Feat)",
    )  # fmt: skip
    redcap.tradition_effects = [cles]
    found = he.effect_total(redcap, tradition, cles)
    assert found is not None
    assert (found.score, found.level, found.die, found.botch_dice) == (6, 9, 3, 1)
    text = tradition_text.casting_text(Saga(id="x", name="X"), redcap, tradition)
    assert "Feat roll (Dexterity)" in text and "Thrown Weapon (Dex)" in text
