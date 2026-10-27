"""House-specific magic: House Mercere's Mutantum spells, boosting and
Portals, the Cult of Heroes' rituals (Houses of Hermes: True Lineages pp.
100-107; Errata pp. 45-46), and House Tytalus's disguises, deep covers
and personae (Houses of Hermes: Societates pp. 87-90; DE p. 169)."""

import pytest
from test_enchant_seasons import _plan as _enchant_plan
from test_enchant_seasons import _saga as _enchant_saga
from test_enchant_seasons import _work as _enchant_work
from test_lab_virtues import _plan, _saga, _vf

from ars_magica_manager import casting_text, catalog, sheet_text
from ars_magica_manager.models import (
    INVESTED,
    Ability,
    ArtScore,
    Breakthrough,
    Character,
    Characteristics,
    EnchantedDevice,
    InstilledEffect,
    KnownSpell,
    Saga,
    Spell,
)
from ars_magica_manager.rules import casting_virtues, house_mastery, lab_seasons
from ars_magica_manager.rules import enchant_seasons as es
from ars_magica_manager.rules import house_magic as hm
from ars_magica_manager.rules.xp import ability_xp, art_xp

_EMPTY = Saga(id="s", name="S")


def _catalog_spell(spell_id: str) -> Spell:
    spell = catalog.find_spell(_EMPTY, spell_id)
    assert spell is not None, spell_id
    return spell


def _mutantum(spell_id: str = "arrow", quality: str = "Tethered") -> Spell:
    return Spell(
        spell_id,
        "Lethal Spark",
        "Creo",
        "Ignem",
        level=10,
        range="Touch",
        description=f"A spark. (Base 5, +1 Touch; {quality})",
    )


# -- Mutantum qualities --


def test_the_catalogs_mutantum_spells_name_their_qualities():
    assert hm.spell_qualities(_catalog_spell("spell_hunter_s_lethal_arrow")) == (
        hm.TETHERED,
    )
    assert hm.spell_qualities(_catalog_spell("spell_the_tireless_flight")) == (
        hm.BOOSTED,
        hm.HARNESSED,
        hm.TETHERED,
    )
    # Its level working names them though no "Requires" line does.
    assert hm.spell_qualities(_catalog_spell("spell_shape_of_the_ancient_kite")) == (
        hm.HARNESSED,
        hm.TETHERED,
    )
    assert hm.spell_qualities(_catalog_spell("spell_twinning_the_tome")) == (
        hm.BOOSTED,
    )
    assert hm.qualities("(Base 5, +1 Touch, +2 Sun)") == ()


def test_learning_a_mutantum_spell_needs_its_virtue_or_mutantum_magic():
    saga = _saga()
    magus = saga.characters[0]
    saga.spells.append(_mutantum())
    found, _ = lab_seasons.work(saga, magus, _plan(spell_id="arrow"))
    assert found and "Mutantum Magic" in found[0]
    # Inventing one needs Mutantum Magic itself (p. 107).
    magus.virtues_flaws = [_vf(hm.TETHERED_MAGIC)]
    found, _ = lab_seasons.work(saga, magus, _plan(spell_id="arrow"))
    assert found and "invented only with Mutantum Magic" in found[0]
    magus.virtues_flaws = [_vf(hm.MUTANTUM_MAGIC)]
    found, work = lab_seasons.work(saga, magus, _plan(spell_id="arrow"))
    assert found == [] and work is not None


def test_tethered_or_tamed_magic_is_enough_to_learn_it():
    magus = Character(id="m", name="Milvus", type="magus")
    spell = _mutantum()
    assert hm.learn_problem(magus, spell)
    magus.virtues_flaws = [_vf(hm.TETHERED_MAGIC)]
    assert hm.learn_problem(magus, spell) == ""
    magus.virtues_flaws = [_vf(hm.TAMED_MAGIC)]
    assert hm.learn_problem(magus, spell) == ""
    # Tamed Magic doesn't boost.
    assert hm.learn_problem(magus, _mutantum(quality="Boosted"))


def test_a_known_mutantum_spell_says_what_its_qualities_do():
    saga = _saga()
    magus = saga.characters[0]
    spell = _catalog_spell("spell_the_tireless_flight")
    lines = " ".join(
        casting_text.known_spell_casting_lines(saga, magus, KnownSpell(spell.id), spell)
    )
    assert "Mutantum spell: Boosted" in lines and "Tethered:" in lines
    assert "can&#x27;t cast it" in lines or "can't cast it" in lines
    magus.virtues_flaws = [_vf(hm.MUTANTUM_MAGIC)]
    assert hm.cast_problem(magus, spell) == ""


def test_mutantum_and_tamed_magic_have_casting_reminders():
    magus = Character(id="m", name="Milvus", type="magus")
    magus.virtues_flaws = [_vf(hm.MUTANTUM_MAGIC), _vf(hm.TAMED_MAGIC)]
    text = " ".join(casting_virtues.reminders(magus))
    assert "Mutantum Magic:" in text and "Tamed Magic:" in text


# -- boosting --


def test_boosting_costs_a_pawn_and_a_botch_die_a_magnitude():
    spell = Spell(
        "s",
        "S",
        "Creo",
        "Ignem",
        level=10,
        range="Touch",
        duration="Momentary",
        target="Individual",
    )
    # The Errata's example: Touch to Sight and Individual to Group, 4 pawns.
    found = hm.boost(spell, range_="Sight", target="Group")
    assert (found.pawns, found.botch_dice, found.problems) == (4, 4, [])
    assert hm.boost(spell, size=2).pawns == 2


def test_boosting_never_lowers_and_reaches_year_only_for_a_ritual():
    spell = Spell(
        "s",
        "S",
        "Creo",
        "Ignem",
        level=10,
        range="Voice",
        duration="Moon",
        target="Individual",
    )
    assert hm.boost(spell, range_="Touch").problems
    assert hm.boost(spell, duration="Year").problems
    spell.ritual = True
    found = hm.boost(spell, duration="Year")
    assert found.problems == [] and found.pawns == 1


def test_who_may_boost():
    magus = Character(id="m", name="Milvus", type="magus")
    boosted = _mutantum(quality="Boosted")
    plain = _mutantum(quality="Harnessed")
    assert not hm.can_boost(magus, boosted)
    assert hm.can_boost(magus, plain, {house_mastery.BOOSTED: 1})
    magus.virtues_flaws = [_vf(hm.MUTANTUM_MAGIC)]
    assert hm.can_boost(magus, boosted) and not hm.can_boost(magus, plain)
    magus.virtues_flaws = [_vf(hm.BOOSTED_MAGIC)]  # any Formulaic spell (DE p. 72)
    assert hm.can_boost(magus, plain)
    plain.ritual = True
    assert not hm.can_boost(magus, plain)


# -- Mercere's Portals --


def test_a_portals_archway_is_rego_terram_65():
    found = hm.portal_level()
    assert found.total == hm.PORTAL_LEVEL == 65
    assert [line.amount for line in found.lines] == [35, 20, 10]


def _portal_saga():
    saga = _enchant_saga()
    magus = saga.character("m")
    magus.arts["rego"] = ArtScore(xp=art_xp(30))
    magus.arts["terram"] = ArtScore(xp=art_xp(30))
    magus.raw_vis["rego"] = 20
    saga.enchanted_devices.append(
        EnchantedDevice(
            "arch",
            "Archway",
            INVESTED,
            holder_kind="covenant",
            holder_id="cov",
            capacity_override=20,
            pawns_opened=20,
            effects=[
                InstilledEffect(
                    "portal",
                    "Mercere's Portal",
                    "Rego",
                    "Terram",
                    level=65,
                    instilling_progress=0,
                )
            ],
        )
    )
    return saga


def test_instilling_a_portal_needs_the_method():
    saga = _portal_saga()
    plan = _enchant_plan(
        es.INSTIL, device_id="arch", effect_id="portal", vis_art="Rego"
    )
    found, _ = _enchant_work(saga, plan)
    assert found and "method of Mercere's Portals" in found[0]
    saga.character("m").breakthroughs = [Breakthrough("Mercere's Portal", reached=True)]
    found, work = _enchant_work(saga, plan)
    assert found == [], found
    assert hm.PORTAL_NOTE in (work.lab_total.notes or [])


def test_a_portal_is_rego_terram_65_on_an_invested_device():
    magus = Character(id="m", name="Mercere", type="magus")
    magus.breakthroughs = [Breakthrough("Mercere's Portal", reached=True)]
    wrong = InstilledEffect("p", "Mercere's Portal", "Muto", "Terram", level=50)
    found = hm.effect_problems(magus, wrong, invested=False)
    assert len(found) == 3


def test_investing_a_mutantum_effect_needs_mutantum_magic():
    magus = Character(id="m", name="Milvus", type="magus")
    effect = InstilledEffect(
        "e",
        "Tether",
        "Creo",
        "Ignem",
        level=10,
        description="(Base 5, +1 Touch; Tethered)",
    )
    assert hm.effect_problems(magus, effect)
    magus.virtues_flaws = [_vf(hm.MUTANTUM_MAGIC)]
    assert hm.effect_problems(magus, effect) == []


# -- the Cult of Heroes --


def test_followers_rituals_raise_to_zero_heroes_to_five():
    followers = "spell_physical_characteristic_of_the_followers"
    heroes = "spell_mental_characteristic_of_the_heroes"
    assert hm.heroes_ritual(followers, "Strength", -2) == (-1, "")
    assert hm.heroes_ritual(followers, "Strength", 0)[1]
    assert hm.heroes_ritual(heroes, "Presence", 4) == (5, "")
    assert hm.heroes_ritual(heroes, "Presence", 5)[1]
    assert hm.heroes_ritual(heroes, "Strength", 1)[1]  # a mental ritual
    with pytest.raises(ValueError):
        hm.heroes_ritual("spell_pilum_of_fire", "Strength", 0)
    for spell_id in hm.HEROES_RITUALS:
        assert catalog.find_spell(_EMPTY, spell_id) is not None


def test_the_cult_of_heroes_spells_say_what_they_do():
    lines = hm.spell_lines(
        _catalog_spell("spell_physical_characteristic_of_the_heroes")
    )
    assert lines == [
        "Raises one physical Characteristic by 1, to no more than +5 "
        "(Houses of Hermes: True Lineages p. 103)."
    ]
    assert "Mercurian Ritual" in hm.spell_lines(_catalog_spell(hm.MERCURYS_BLESSING))[0]


# -- disguises and deep cover --


def _tytalus() -> Character:
    c = Character(id="t", name="Carolus", type="magus")
    c.characteristics = Characteristics(intelligence=2, presence=1, stamina=1)
    c.abilities = [
        Ability("Guile", xp=ability_xp(4)),
        Ability("Folk Ken", xp=ability_xp(2)),
        Ability("Persona", xp=ability_xp(3)),
    ]
    return c


def test_a_disguise_is_int_plus_guile_against_nine_and_its_modifiers():
    carolus = _tytalus()
    assert hm.disguise_total(carolus).total == 6
    ease = hm.disguise_ease(["Change social status", "Minimal preparation"])
    assert ease.total == 15
    assert hm.disguise_ease(["Change sex"], cover_reputation=2).total == 13
    with pytest.raises(ValueError):
        hm.disguise_ease(["Wearing a hat"])


def test_talking_in_disguise_is_pre_plus_guile_less_the_gift():
    carolus = _tytalus()
    assert hm.deceive_total(carolus).total == 2  # Presence 1 + Guile 4 - 3
    carolus.type = "companion"
    assert hm.deceive_total(carolus).total == 5
    assert hm.see_through_total(carolus).total == 4


def test_a_deep_covers_reputation_grows_and_fades():
    assert hm.cover_xp("lives there") == (2, False)
    assert hm.cover_xp("visits regularly", events=2) == (3, True)
    with pytest.raises(ValueError):
        hm.cover_xp("by letter")
    # The book's example: Reputation 2 leaves the Gift's -3 at -1.
    assert hm.cover_gift_penalty(3, 2) == 1
    assert hm.cover_gift_penalty(3, 5) == 0
    assert hm.dormant_reputation(3, 3) == 3
    assert hm.dormant_reputation(3, 5) == 1
    assert hm.dormant_reputation(1, 9) == 0
    assert hm.gift_returns(2, 2) and not hm.gift_returns(2, 1)
    assert hm.cover_burden("Minor").startswith("a Minor Story Flaw")
    assert hm.cover_burden("Major").startswith("a Major Story Flaw")
    assert hm.cover_burden(None, other_virtues=True).startswith("impossible")


# -- Persona --


def test_persona_rolls_identities_and_traces():
    carolus = _tytalus()
    assert hm.persona_total(carolus).total == 4  # Stamina 1 + Persona 3
    assert hm.persona_trace_magnitude(0) == 2
    assert hm.persona_trace_magnitude(3) == -1
    assert hm.persona_spell_level(3) == 15


def test_the_abilities_details_explain_guile_and_persona():
    carolus = _tytalus()
    persona = sheet_text.ability_info_text(carolus.abilities, 2)
    assert "Persona 3: 3 identities" in persona and "level 15" in persona
    guile = sheet_text.ability_info_text(carolus.abilities, 0)
    assert "Disguise: Intelligence + Guile" in guile
    assert "Persona" not in sheet_text.ability_info_text(carolus.abilities, 1)
