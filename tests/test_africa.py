"""Mythic Africa's rules (Lands of the Nile pp. 95-126, Between Sand and Sea
pp. 119-124): the Cult of Dedun, Corpse Magic, Ethiopia, the Aithiopians,
the Plinian races and the jnun."""

from __future__ import annotations

import pytest

from ars_magica_manager import catalog, traditions
from ars_magica_manager.rules import africa


def test_dedun_rank_needs():
    assert africa.dedun_rank_problems("Adherent", organization_lore=0) == []
    assert (
        africa.dedun_rank_problems("Altar Priest", organization_lore=1, meroitic=3)
        == []
    )
    short = africa.dedun_rank_problems("Temple Priest", organization_lore=2, meroitic=4)
    assert short == ["Organization Lore: Cult of Dedun 3 (has 2)"]
    undying = africa.dedun_rank_problems(
        "Undying One", organization_lore=5, warping=3, decrepitude=3
    )
    assert len(undying) == 3  # Warping + Decrepitude 6, no Enfeebled, no Gift
    assert (
        africa.dedun_rank_problems(
            "Undying One",
            organization_lore=5,
            warping=4,
            decrepitude=3,
            gifted=True,
            temple_priest_with_enfeebled=True,
        )
        == []
    )
    with pytest.raises(ValueError):
        africa.dedun_rank_problems("High Priest", organization_lore=5)


def test_dedun_blessing_pools_failures_and_doubles_the_aura():
    assert africa.blessing_ease(4) == 13
    # Two priests, one failed year each: +2 to both their rolls.
    assert africa.blessing_total(2, 4, 5, failed_years=(1, 1)) == 13
    assert africa.aligned_aura(4, matches=True) == 8
    assert africa.aligned_aura(4, matches=False) == 4
    assert africa.undying_resistance_bonus(4, aligned_to_the_dead=True) == 8
    assert africa.undying_resistance_bonus(4, aligned_to_the_dead=False) == 0


def test_a_court_and_the_undying_ones_might():
    assert africa.court_member(0) == 1
    assert africa.court_member(africa.KING_REPUTATION) == 7
    assert africa.court_member(7, divine_burial=True) == 4
    assert africa.court_member(2, divine_burial=True) == 0
    assert africa.court_strength([(7, False), (5, False), (0, False), (7, True)]) == 17
    # The book's example: a Court of 62 is an aura of 7 and Might 10, which
    # lets an Undying One of Might 10 dwell among it half the time.
    assert africa.court_aura(62) == 7
    assert africa.court_aura(60) == 6
    assert africa.undying_might(62) == 10
    assert africa.court_keeps_off_acclimation(62, 10).startswith("half")
    assert africa.court_keeps_off_acclimation(0, 10).startswith("the Court is")


def test_unnatural_vitality():
    assert africa.vitality_bonus(2) == 6
    assert africa.vitality_penalty(-4, 1) == -1
    assert africa.vitality_penalty(-4, 2) == 0
    assert africa.vitality_penalty(3, 2) == 3
    assert africa.vitality_stress_crisis(4)
    assert not africa.vitality_stress_crisis(5)


def test_dedun_shadow_flaws_and_the_corpse_magic_casting_are_in_the_catalogs():
    virtues = catalog.load_virtue_flaw_catalog_by_id()
    assert set(africa.DEDUN_SHADOW_FLAWS) <= set(virtues)
    dedun = traditions.find("trad_cult_of_dedun")
    assert dedun is not None
    rule = next(r for r in dedun.casting if r.name == "Corpse Magic")
    assert rule.characteristic == "Communication" and rule.against == "Ease Factor"


def test_corpse_magic():
    assert africa.corpse_magic_total(2, 4, 3, 6) == 15
    assert africa.corpse_magic_outcome(8) == ""
    assert africa.corpse_magic_outcome(9).startswith("speak")
    assert africa.corpse_magic_outcome(15).startswith("animate it, to follow")
    assert africa.corpse_magic_outcome(18).startswith("animate it under")
    # A corpse protected by a Corpse Magic 3 caster: every EF is 3 higher.
    assert africa.corpse_magic_outcome(15, protection=3).startswith("speak to it and")
    assert africa.COMMAND_EASE == {"word": 6, "simple": 9, "complex": 12}
    assert africa.command_total(2, 5, 3, 4) == 9  # Leadership capped at 3
    assert africa.command_total(2, 5, 5, 4) == 11
    assert africa.command_total(2, 5, 0, 4) is None
    assert not africa.corpse_leaves_grave(9)
    assert africa.corpse_leaves_grave(10)


def test_the_ethiopian_calendar_as_the_book_prints_it():
    assert africa.ethiopian_date(1220, 1, 1) == (1212, "Tarr", 5)
    assert africa.ethiopian_date(1219, 9, 15) == (1212, "Meskerem", 17)
    assert africa.ethiopian_date(1220, 1, 6) == (1212, "Tarr", 10)
    assert africa.ethiopian_date(1219, 12, 25) == (1212, "Tahśaś", 28)
    # 1220 is a Julian leap year: Miyazya begins on 28 March.
    assert africa.ethiopian_date(1220, 3, 28) == (1212, "Miyazya", 1)
    assert africa.ethiopian_date(1221, 3, 29) == (1213, "Miyazya", 1)
    assert africa.ethiopian_date(1220, 8, 25) == (1212, "Pagume", 1)
    assert africa.ethiopian_date(1220, 8, 30) == (1213, "Meskerem", 1)
    assert {h.name for h in africa.HOLIDAYS} >= {"Maskal", "Timket", "Gena"}


def test_church_forests_relics_and_outsiders():
    assert africa.church_forest_aura(5, has_forest=False, in_forest=False) == 5
    assert africa.church_forest_aura(5, has_forest=True) == 5
    assert africa.church_forest_aura(5, has_forest=True, in_forest=False) == 4
    assert africa.church_forest_aura(5, has_forest=True, lush=True) == 6
    assert africa.relic_faith("ark", "ethiopian") == 10
    assert africa.relic_faith("ark", "muslim") == 7
    assert africa.relic_faith("ring", "other christian") == 5
    assert africa.relic_faith("ring", "muslim") is None
    with pytest.raises(ValueError):
        africa.relic_faith("grail", "ethiopian")
    assert not africa.ethiopian_outsider(jewish=True, blacksmith=False)
    assert africa.ethiopian_outsider(jewish=True, blacksmith=True)


def test_the_scorpion_fishs_acid():
    assert africa.acid_damage() == 36
    assert africa.acid_damage(5) == 36
    assert africa.acid_damage(6) == 27
    assert africa.acid_damage(9) == 18
    assert africa.acid_damage(12) == 9


def test_every_kindreds_virtues_and_flaws_are_catalog_entries():
    virtues = catalog.load_virtue_flaw_catalog_by_id()
    named = [
        vf_id
        for kin in africa.AITHIOPES + africa.PLINIAN_RACES
        for vf_id, _ in kin.virtues + kin.flaws
    ]
    named += [vf_id for vf_id, _ in africa.HYLOPHAGUS]
    named += list(africa.AITHIOPE_AS_MAGIC_HUMAN)
    missing = sorted(set(named) - set(virtues))
    assert not missing, missing
    keys = [kin.key for kin in africa.AITHIOPES + africa.PLINIAN_RACES]
    assert len(keys) == len(set(keys))


def test_aithiopians():
    assert africa.kindred("cynegi").virtues == (("vf_puissant_ability", "Hunt"),)
    with pytest.raises(LookupError):
        africa.kindred("hylophagi")
    assert not africa.kombe_charged(3, 0, 10)  # no Ability, never charged
    assert africa.kombe_charged(1, 2, 3)
    assert not africa.kombe_charged(1, 2, 2)
    assert africa.kombe_resisted(12) and not africa.kombe_resisted(11)
    assert africa.carnivorous_bull_ambush(spotted=False) == (True, 3)
    assert africa.carnivorous_bull_ambush(spotted=True) == (False, 0)


def test_the_plinian_races():
    assert africa.kindred("nubian_blemmya").virtues[0][1] == "Puissant Thrown Weapon"
    assert africa.kindred("blemmya").virtues[0][1] == "Puissant Bargain"
    assert africa.PLINIAN_MIGHT["companion"] == (5, 15)
    assert africa.plinian_social_status(tribelands=True) == "any Social Status"
    assert africa.plinian_social_status() == "vf_outcast"
    assert africa.plinian_social_status(long_association=True).startswith("a Free")
    assert africa.plinian_social_status(long_association=True, other_region=True) == (
        "vf_outcast"
    )
    assert africa.plinian_social_status(unknown_or_hostile=True) == "vf_outsider_major"


def test_the_anthropophagi_feast():
    assert africa.corpses_for_feast(5) == 1
    assert africa.corpses_for_feast(6) == 2
    assert africa.qualities_after_missed_feasts(3, 5) == 0
    assert africa.transformed_anthropophagus(4) == "still human in looks"
    assert africa.transformed_anthropophagus(5) == "Disfigured"
    assert africa.transformed_anthropophagus(15).startswith("monstrous")


def test_the_jnun():
    assert africa.affected_by_sihr("shayatin")
    assert not africa.affected_by_sihr("leriah")
    assert not africa.affected_by_sihr("baharia")
    with pytest.raises(ValueError):
        africa.affected_by_sihr("marid")
    # The book's example: Size +1 and Shapeshifter 3 is -5 to +4.
    assert africa.shapeshifter_sizes(1, 3) == (-5, 4)


def test_the_debterah_are_a_divine_tradition_with_holy_guidelines():
    debterah = traditions.find("trad_debterah")
    assert debterah is not None
    assert debterah.realm == "Divine"
    assert set(debterah.favored) == {
        "Adjuration",
        "Blessing",
        "Craft Amulets",
        "Invocation",
    }
    assert debterah.guidelines  # the holy_powers set
    # Christian and Falasha Jewish members alike (LotN p. 114).
    assert {"Theology: Christian", "Theology: Judaism"} <= set(debterah.abilities)
