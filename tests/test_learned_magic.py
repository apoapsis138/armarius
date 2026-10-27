"""Learned magic: Ars Notoria (RoP:D pp. 97-100), Jewish mysticism
(pp. 141-144) and the Solomonic integrations (TC&TC pp. 44-45)."""

import pytest

from ars_magica_manager import catalog
from ars_magica_manager.models import (
    Ability,
    Character,
    Characteristics,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import hybrid_magic, integrations
from ars_magica_manager.rules import learned_magic as lm
from ars_magica_manager.rules.xp import ability_xp


def _scholar(*abilities: tuple[str, int], kind="companion", vf_ids=()) -> Character:
    c = Character(
        id="s",
        name="Scholar",
        type=kind,
        characteristics=Characteristics(intelligence=3, perception=1, stamina=2),
        abilities=[Ability(name, xp=ability_xp(score)) for name, score in abilities],
        virtues_flaws=[VirtueFlawInstance(vf_id=v) for v in vf_ids],
    )
    return c


# -- Ars Notoria --------------------------------------------------------


def test_find_text_total_and_ease():
    c = _scholar(("Divine Lore", 4))
    assert lm.find_text_total(c, 7) == 14
    assert lm.FIND_TEXT_EASE == 21


def test_reading_needs_four_languages_and_artes():
    short = _scholar(
        ("Dead Language: Latin", 5),
        ("Living Language: Greek", 2),
        ("Dead Language: Hebrew", 4),
        ("Artes Liberales", 3),
    )
    assert lm.reading_shortfalls(short) == [
        "Greek 2 of 4",
        "Chaldean 0 of 4",
        "Artes Liberales 3 of 4",
    ]
    ready = _scholar(
        ("Dead Language: Latin", 5),
        ("Living Language: Greek", 4),
        ("Dead Language: Hebrew", 4),
        ("Dead Language: Aramaic", 4),
        ("Artes Liberales", 4),
    )
    assert lm.reading_shortfalls(ready) == []


def test_first_study_needs_five_xp():
    assert lm.first_study_xp(0) == 20
    assert lm.first_study_xp(15) == 5
    assert lm.first_study_xp(16) == 0


def test_starting_problems():
    clerk = _scholar(vf_ids=("vf_clerk",))
    assert lm.starting_problems(clerk, gifted=True) == []
    assert len(lm.starting_problems(clerk, gifted=False)) == 1
    knight = _scholar(vf_ids=("vf_knight",))
    assert len(lm.starting_problems(knight, gifted=True)) == 1
    assert lm.starting_problems(_scholar(kind="magus"), gifted=True) == []


def test_ring_ease_first_and_known():
    # First recitation of the first ring for one season: 6 + 3 + 1.
    assert lm.ring_ease(1, 1, known=False) == 10
    assert lm.ring_ease(1, 1, known=True) == 7
    assert lm.ring_ease(7, 4, known=False) == 31
    with pytest.raises(ValueError):
        lm.ring_ease(8, 1, known=False)
    with pytest.raises(ValueError):
        lm.ring_ease(1, 0, known=False)


def test_recitation_score_counts_supernatural_and_faith():
    c = _scholar(
        ("Ars Notoria", 3),
        ("Second Sight", 2),
        ("Sense Holiness and Unholiness", 4),
    )
    c.background.true_faith_score = 1
    supernatural = frozenset({"Second Sight", "Sense Holiness and Unholiness"})
    # Int 3 + Ars Notoria 3 + chastity 1 - Second Sight 2 + Faith 1.
    assert lm.recitation_score(c, modifiers=1, supernatural=supernatural) == 6


def test_fasting_ease_rises_each_season():
    assert [lm.fasting_ease(s) for s in (1, 2, 3)] == [6, 7, 8]
    with pytest.raises(ValueError):
        lm.fasting_ease(0)


def test_recitation_days_and_order():
    assert lm.recitation_days(3) == 7
    assert lm.recitation_days(12) == 1
    assert lm.may_learn(3, 2)
    assert not lm.may_learn(4, 2)
    assert lm.may_learn(1, 6)


def test_ring_seasons():
    assert lm.season_allowed(1, "Autumn")
    assert not lm.season_allowed(2, "Spring")
    assert lm.season_allowed(3, "Summer")
    assert lm.season_allowed(5, "Summer") and not lm.season_allowed(5, "Winter")
    assert lm.ring(6).seasons == ("Spring",)
    assert [r.level for r in lm.RINGS] == list(range(1, 8))


def test_ring_rewards():
    assert lm.ring(1).ability == "Philosophiae" and lm.ring(1).xp == 100
    assert lm.raised_characteristic(1) == 4
    assert lm.raised_characteristic(3) == 5
    assert lm.raised_characteristic(6) == 6
    # p. 99's example: 115 xp, +25 by study, less the ring's 100 leaves 40.
    assert lm.xp_after_ring(140) == 40
    for r in lm.RINGS:
        if r.virtue:
            assert r.virtue in catalog.load_virtue_flaw_catalog_by_id()


def test_fifth_ring():
    assert lm.sense_realm_ease(0) == 6
    assert lm.sense_realm_ease(24) == 10
    assert lm.powers_learned(14, 10) == 0
    assert lm.powers_learned(15, 10) == 1
    assert lm.powers_learned(25, 10) == 3


def test_divinations_and_auspicious_bonus():
    assert {q.ease for q in lm.DIVINATIONS} == {9, 12, 15, 18}
    assert lm.auspicious_bonus(_scholar(("Ars Notoria", 4))) == 4


def test_divine_aura_relief():
    c = _scholar(("Ars Notoria", 2))
    assert lm.divine_aura_relief(c, -9) == -3
    assert lm.divine_aura_relief(c, -4) == 0
    assert lm.divine_aura_relief(c, 3) == 3
    assert not lm.divine_aura_warps(ring_active=True)


def test_hybrid_aura_uses_ars_notoria():
    magus = _scholar(("Ars Notoria", 2), kind="magus")
    plain = _scholar(kind="magus")
    assert hybrid_magic.aura_modifier(plain, "Divine", 3, casting=True) == (-9, "")
    assert hybrid_magic.aura_modifier(magus, "Divine", 3, casting=True) == (
        -3,
        "Ars Notoria",
    )
    assert hybrid_magic.aura_modifier(magus, "Magic", 3, casting=True) == (3, "")
    # Only casting: Lab Totals and Penetration take the whole penalty
    # (RoP: The Divine p. 100).
    assert hybrid_magic.aura_modifier(magus, "Divine", 3) == (-9, "")
    assert hybrid_magic.aura_label(magus, "Divine", 3) == ("Aura (Divine 3)", -9)
    assert hybrid_magic.aura_label(magus, "Divine", 3, casting=True) == (
        "Aura (Divine 3), Ars Notoria",
        -3,
    )


# -- Jewish mysticism ---------------------------------------------------


def test_gematria_books():
    assert not lm.gematria_book_usable(accelerated=True)
    assert lm.gematria_needs_stress_die(torah=False)
    assert not lm.gematria_needs_stress_die(torah=True)


def test_shinnui_shem_bonus():
    c = _scholar(("Gematria", 5), ("Understanding", 2))
    # (6 + 3 + 5 + 2 + 9 + 3) / 5 = 28 / 5 -> 5.
    assert lm.shinnui_shem_bonus(c, die=6, book_quality=9, aura=3) == 5


def test_golem_example_p143():
    moshe = Character(
        id="m",
        name="Moshe",
        type="companion",
        characteristics=Characteristics(intelligence=2),
        abilities=[
            Ability("Kabbalah", xp=ability_xp(6)),
            Ability("Wonders", xp=ability_xp(3)),
        ],
    )
    total = lm.golem_total(moshe, aura=4, ceremony=20)
    assert total == 35
    points = sum(lm.banked(total, lm.AWAKEN_EASE) for _ in range(3))
    assert points == 15
    assert lm.golem_might(points, 8, kabbalah=6) == 23
    assert lm.golem_might(points, 20, kabbalah=6) == 30
    assert lm.golem_botch_dice(4) == 4
    # The level 40 power leaves 23 - 8 = 15 magnitudes.
    assert lm.power_room(23, 8) == 15
    assert lm.power_gained(40, 40) and not lm.power_gained(39, 40)


def test_golem_madness_table():
    assert lm.golem_madness(0, botch=True) == "Madness"
    assert lm.golem_madness(3) == "Trusting -1"
    assert lm.golem_madness(7) == "Vengeful +1"
    assert lm.golem_madness(12) == "Loyal to Community -1"
    assert lm.golem_madness(15) == "Roll twice more"
    for vf in (*lm.GOLEM_VIRTUES, *lm.GOLEM_FLAWS):
        assert vf in catalog.load_virtue_flaw_catalog_by_id()


def test_merkavah():
    c = _scholar(("Merkavah", 4), ("Adjuration", 3))
    assert lm.merkavah_total(c, aura=2, ceremony=5) == 16
    assert not lm.true_name_revealed(20, 20)
    assert lm.true_name_revealed(21, 20)
    assert lm.merkavah_discipline(9) == ""
    assert lm.merkavah_discipline(8).startswith("Obsession")
    assert "Plagued" in lm.merkavah_discipline(0, botch=True)


# -- The Cradle and the Crescent ------------------------------------------


def test_fatra_bayna_spends():
    assert lm.fatra_bayna_reward(3) == 15
    assert {e.cost for e in lm.SPIRIT_POINT_EFFECTS} == {1, 3}
    assert {e.cost for e in lm.CORRUPTION_POINT_EFFECTS} == {1, 3}


def test_solomonic_breakthroughs():
    assert lm.spontaneous_solomonic(25, fatiguing=True) == 12
    assert lm.spontaneous_solomonic(24, fatiguing=False) == 4
    assert lm.independent_solomonic(30, 7) == 23
    for b in lm.SOLOMONIC_BREAKTHROUGHS:
        if b.virtue:
            assert b.virtue in catalog.load_virtue_flaw_catalog_by_id()


def test_hermetic_integrations():
    for name, kind in (
        ("Hermetic True Names", "Minor"),
        ("Scientates Suleimanis", "Hermetic"),
        ("Hermetic Realm Initiation", "Hermetic"),
    ):
        found = integrations.BY_NAME[name]
        assert found.kind == kind
        assert found.book == "The Cradle and the Crescent"
        if found.grant_kind == "Virtue":
            assert found.grant in catalog.load_virtue_flaw_catalog_by_id()
