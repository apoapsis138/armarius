"""The Fourth Edition character conversion: where experience goes."""

from __future__ import annotations

from ars_magica_manager.book_packs.fourth import (
    SPELL_DESIGNS,
    SWAPS,
    Fourth,
    Kin,
    convert,
    rebuild_combat,
    reconvert,
    soak_of,
    take_kin,
)
from ars_magica_manager.models import Characteristics, Creature, CreatureAttack, Saga
from ars_magica_manager.rules.xp import ability_xp


def _block(abilities, virtues=(), spells=(), arts=None):
    return Fourth(
        age=40,
        apparent=None,
        characteristics={},
        confidence=3,
        twilight=0,
        decrepitude=0,
        virtues=virtues,
        abilities=abilities,
        arts=arts or {},
        spells=spells,
        traits={},
    )


def _scores(stat):
    return {name: score for name, score, _ in stat["abilities"]}


def test_a_removed_ability_moves_its_experience_with_no_cap():
    stat, _ = convert(
        "x", _block([("Guile", 5, ""), ("Forgery", 5, "")]), area="Rhine Tribunal"
    )
    assert _scores(stat) == {"Guile": 7}
    assert stat["spare_xp"] == {"Guile": 2 * ability_xp(5) - ability_xp(7)}


def test_abilities_go_where_the_definitive_edition_puts_them():
    stat, _ = convert(
        "x",
        _block(
            [
                ("Speak Latin", 6, ""),
                ("Speak Irish", 4, ""),
                ("Speak Greek", 5, ""),
                ("Legend Lore", 3, "myths"),
                ("Disputatio", 2, ""),
                ("Storytelling", 1, ""),
                ("Crossbow", 1, ""),
                ("Certamen", 3, ""),
            ]
        ),
        area="Rhine Tribunal",
    )
    scores = _scores(stat)
    assert scores["Area Lore: Rhine Tribunal"] == 3
    assert scores["Teaching"] == 2 and scores["Crossbow"] == 1
    assert scores["Penetration"] == 3 and "Certamen" not in scores
    # Storytelling goes to the best living language, not to Latin.
    assert scores["Living Language: Greek"] == 5
    assert stat["spare_xp"]["Living Language: Greek"] == ability_xp(1)


def test_an_affinity_feeds_the_art_it_served():
    stat, _ = convert(
        "x",
        _block([("Magic Affinity", 6, "bones")], arts={"Corpus": 10}),
        area="Rhine Tribunal",
    )
    assert "Magic Affinity" not in _scores(stat)
    # Score 10 is 55 xp; 21 more make 76, which is 11 (66) and 10 over.
    assert stat["arts"]["Corpus"] == 11
    assert stat["spare_art_xp"] == {"Corpus": 10}


def test_a_talent_brings_its_virtue():
    stat, _ = convert("x", _block([("Curse", 4, "")]), area="Rhine Tribunal")
    assert _scores(stat) == {"Curse-Throwing": 4}
    assert "Curse-Throwing" in stat["virtues_flaws"]


def test_a_spell_is_swapped_only_if_hermetic_magic_cannot_cast_it():
    stat, _ = convert(
        "x",
        _block(
            [],
            spells=[("Eyes of the Past", "InCo", 30), ("Spell Analysis", "InVi", 20)],
        ),
        area="Rhine Tribunal",
    )
    names = [name for name, *_ in stat["spells"]]
    assert names == [SWAPS["Eyes of the Past"], "Spell Analysis"]


def test_a_story_flaw_is_major_at_any_old_cost():
    stat, _ = convert(
        "x", _block([], virtues=[("True Love", -1)]), area="Rhine Tribunal"
    )
    assert "True Love (Major)" in stat["virtues_flaws"]


def _beast(strength, stamina, dexterity, quickness, size, attacks, soak):
    return Creature(
        id="x",
        name="Beast",
        characteristics=Characteristics(
            strength=strength,
            stamina=stamina,
            dexterity=dexterity,
            quickness=quickness,
        ),
        size=size,
        attacks=attacks,
        soak=soak,
    )


def test_the_lion_comes_out_as_the_definitive_edition_prints_it():
    """Medieval Bestiary Revised p. 37; DE p. 434."""
    lion = _beast(6, 3, 2, 1, 2, [CreatureAttack("Bite and Claws", 7, 7, 5, 12)], 6)
    rebuild_combat(lion)
    line = lion.attacks[0]
    assert (line.init, line.attack, line.defense, line.damage) == (1, 15, 12, 10)
    # The 5e lion is Tough besides: Soak is its Stamina and old Protection.
    assert lion.soak == 4
    assert "Attack +7" in lion.notes


def test_a_griffin_keeps_its_monstrous_damage_as_improved_damage():
    """ArM4 p. 251; Legends of Hermes p. 134 has Damage +20."""
    griffin = _beast(7, 9, 2, 2, 4, [CreatureAttack("Claw", 6, 7, 2, 28)], 26)
    rebuild_combat(griffin)
    assert griffin.attacks[0].damage == 7 + 4 + 4 * 3


def test_soak_is_compressed_past_four_of_protection_and_eight_of_stamina():
    assert soak_of(3, 3) == 6
    assert soak_of(15, 9) == 8 + 0 + 4 + 6
    assert soak_of(0, 20) == 14


def test_a_small_creature_carries_its_size_in_quickness():
    gnome = _beast(0, 0, 0, 2, -2, [], 0)
    rebuild_combat(gnome)
    assert gnome.characteristics.quickness == 4


def test_a_pack_s_might_table_replaces_the_printed_score_and_says_so():
    saga = Saga(id="s", name="S")
    saga.creatures.append(_beast(0, 0, 0, 0, 0, [], 0))
    saga.creatures[0].might = 20
    reconvert(saga, {"Beast": 5})
    assert saga.creatures[0].might == 5
    assert "Might 20 as printed" in saga.creatures[0].notes


def test_a_kept_spell_takes_its_de_design():
    stat, _ = convert(
        "x",
        _block([], spells=[("Eyes of Flame", "CrIg", 35)]),
        area="Rhine Tribunal",
    )
    assert stat["spells"][0][2] == SPELL_DESIGNS["Eyes of Flame"][0] == 25


def test_a_creature_can_take_its_kin_s_stamina_and_soak():
    giant = _beast(15, 20, -1, -1, 6, [], 26)
    take_kin(giant, Kin(3, 9, "the typical giant"))
    assert giant.characteristics.stamina == 3 and giant.soak == 9
    assert "typical giant" in giant.notes
