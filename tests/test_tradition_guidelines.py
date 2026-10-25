"""Hedge, rival and ancient traditions by the book: guideline tables and
worked-out effect levels, botch dice, the Opening Ease Factor's Arts, the
sabbat's helpers, and the single traditions' own totals."""

import pytest

from ars_magica_manager import catalog
from ars_magica_manager.forms import tradition as tf
from ars_magica_manager.models import (
    ArtScore,
    Character,
    Characteristics,
    Saga,
    TraditionDef,
    TraditionEffect,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import creation_tradition as ct
from ars_magica_manager.rules import hedge_casting as hc
from ars_magica_manager.rules import hedge_effects as he
from ars_magica_manager.rules import integrations
from ars_magica_manager.rules import tradition_seasons as ts
from ars_magica_manager.rules import tradition_totals as tt
from ars_magica_manager.rules.xp import xp_for_score


def _t(tradition_id: str) -> TraditionDef:
    return catalog.load_tradition_catalog_by_id()[tradition_id]


def _member(tradition_id: str, gifted: bool = True) -> Character:
    character = Character(id="c", name="C", type="companion")
    character.traditions = [tradition_id]
    character.virtues_flaws = [VirtueFlawInstance("vf_the_gift")] if gifted else []
    ct.open_tradition(character)
    return character


def _set(character: Character, name: str, score: int) -> None:
    ability = next((a for a in character.abilities if a.name == name), None)
    if ability is None:
        ability = ct.opened_ability(name)
        character.abilities.append(ability)
    ability.xp = xp_for_score(score, ability.factor)


def _effect(
    tradition_id: str, guideline: str, uses: list[str], **kw
) -> TraditionEffect:
    return TraditionEffect(
        "E", tradition=tradition_id, guideline=guideline, uses=uses, **kw
    )


# ---------------------------------------------------------------------------
# The catalog's tables


def test_every_guideline_and_parameter_names_its_traditions_arts():
    faults = []
    for t in catalog.load_tradition_catalog():
        held = set(t.abilities)
        for g in t.guidelines:
            if not set(g.arts) <= held:
                faults.append(f"{t.id}: guideline {g.name!r} uses {g.arts}")
        for p in t.effect_parameters:
            if p.arts and not set(p.arts) <= held:
                faults.append(f"{t.id}: parameter {p.name!r} for {p.arts}")
        for art, bases in t.parameter_bases.items():
            if art not in held:
                faults.append(f"{t.id}: base for {art!r}")
            for kind, name in bases.items():
                if not any(
                    p.kind == kind and p.name == name for p in t.effect_parameters
                ):
                    faults.append(f"{t.id}: base {kind} {name!r} isn't a parameter")
    assert not faults, faults


def test_the_tables_the_card_names_are_filled():
    sizes = {
        "trad_gruagachan": 60,
        "trad_learned_magicians": 70,
        "trad_vitkir": 150,
        "trad_amazon_sorceresses": 60,
        "trad_augustan_brotherhood": 40,
        "trad_muspelli": 50,
        "trad_soqotran_sorcerers": 30,
        "trad_sahirs": 90,
        "trad_columbae": 20,
    }
    for tradition_id, least in sizes.items():
        assert len(_t(tradition_id).guidelines) >= least, tradition_id


def test_an_unknown_level_step_or_parameter_kind_is_rejected():
    with pytest.raises(ValueError, match="level steps"):
        TraditionDef(id="t", name="T", level_steps="fourfold")
    with pytest.raises(ValueError, match="parameter kind"):
        TraditionDef.from_dict(
            {
                "id": "t",
                "name": "T",
                "effect_parameters": [{"kind": "size", "name": "X"}],
            }
        )


# ---------------------------------------------------------------------------
# Effect levels worked out


def test_a_gruagach_spell_level_from_its_guideline():
    gruagachan = _t("trad_gruagachan")
    # Give Blessing +1 to one Ability (5), Voice +1, Sun +2: 5 + 3 magnitudes.
    spell = _effect(
        "trad_gruagachan",
        "+1 to one Ability",
        ["Gruagach Give", "Gruagach Blessing"],
        range="Voice",
        duration="Sun",
    )
    design = he.effect_design(gruagachan, spell)
    assert design is not None and design.level == 20
    assert design.design_line() == "Base 5, +1 Voice, +2 Sun"
    # Conversation costs a magnitude for Shape, none for Blessing.
    shape = _effect(
        "trad_gruagachan", "Size up to +3", ["Gruagach Give", "Gruagach Shape"],
        range="Conversation",
    )  # fmt: skip
    assert he.effect_level(gruagachan, shape) == 3
    geas = _effect(
        "trad_gruagachan", "+1 to one Ability", ["Gruagach Give", "Gruagach Blessing"],
        duration="Geas (sweeping)",
    )  # fmt: skip
    assert he.effect_level(gruagachan, geas) == 25


def test_charms_and_amulets_use_their_own_parameters():
    learned = _t("trad_learned_magicians")
    uses = ["Succurro", "Salutem"]
    charm = _effect(
        "trad_learned_magicians", "+6 Recovery", uses, range="Touch", duration="Sun"
    )
    assert he.effect_level(learned, charm) == 5  # 2 + 1 + 2 magnitudes
    amulet = _effect(
        "trad_learned_magicians", "+6 Recovery", uses, kind="amulet",
        range="Touch", duration="Season",
    )  # fmt: skip
    assert he.effect_level(learned, amulet) == 5  # Touch is an amulet's base
    season = he.parameters_for(learned, "duration", uses, item=False)
    assert "Season" not in [p.name for p in season]


def test_a_rune_or_a_ward_is_its_guidelines_level():
    vitkir = _t("trad_vitkir")
    assert he.parameters_for(vitkir, "range", ["Fehu"]) == []
    assert (
        he.effect_level(
            vitkir, _effect("trad_vitkir", "Detect precious metal", ["Fehu"])
        )
        == 20
    )
    columbae = _t("trad_columbae")
    ward = _effect("trad_columbae", "Terram: stone", ["Warding"])
    assert he.effect_level(columbae, ward) == 25


def test_an_amazon_step_from_the_consonants_base_costs_either_way():
    amazons = _t("trad_amazon_sorceresses")
    # Api's base is Cousin and Hour: Sister is a step down, Day a step up.
    spell = _effect(
        "trad_amazon_sorceresses", "Violently open earth", ["Alala", "Api"],
        range="Sister", duration="Day",
    )  # fmt: skip
    assert he.effect_level(amazons, spell) == 15
    at_base = _effect(
        "trad_amazon_sorceresses", "Violently open earth", ["Alala", "Api"],
        range="Cousin", duration="Hour",
    )  # fmt: skip
    assert he.effect_level(amazons, at_base) == 5


def test_ease_factors_that_step_by_three():
    augustan = _t("trad_augustan_brotherhood")
    rite = _effect(
        "trad_augustan_brotherhood", "Minor weather", ["School of Boreas"],
        range="Sight", target="Structure",
    )  # fmt: skip
    assert he.effect_level(augustan, rite) == 3 + 3 * 4
    muspelli = _t("trad_muspelli")
    # Entrancement's utiseta base is Eye/Concentration/Individual.
    utiseta = _effect(
        "trad_muspelli", "Utiseta base: innocuous request", ["Entrancement"],
        range="Voice", duration="Sun",
    )  # fmt: skip
    assert he.effect_level(muspelli, utiseta) == 9 + 6
    soqotra = _t("trad_soqotran_sorcerers")
    aloe = _effect(
        "trad_soqotran_sorcerers", "Living things regrow", ["Aloe Magic"],
        range="Touch", duration="Perpetual",
    )  # fmt: skip
    # Touch +3; Perpetual is three steps past Aloe's Regrowth: +9.
    assert he.effect_level(soqotra, aloe) == 15 + 3 + 9
    nem = _t("trad_nemthengacha")
    lord = _effect(
        "trad_nemthengacha", "Lord", ["Embitterment"], duration="Moon", magnitudes=1
    )
    assert he.effect_level(nem, lord) == 15 + 3 + 3


def test_a_solomonic_arts_one_parameter():
    sahirs = _t("trad_sahirs")
    names = [p.name for p in he.parameters_for(sahirs, "target", ["Solomonic Physic"])]
    assert "Potency Moderate" in names and "Alteration Minor" not in names


def test_a_general_guideline_or_none_keeps_the_typed_level():
    vitkir = _t("trad_vitkir")
    general = _effect("trad_vitkir", "Wealth seeking", ["Fehu"], level=15)
    assert he.effect_design(vitkir, general) is None
    assert he.effect_level(vitkir, general) == 15
    typed = TraditionEffect("T", tradition="trad_vitkir", uses=["Fehu"], level=10)
    assert he.effect_level(vitkir, typed) == 10


def test_the_effect_form_works_the_level_out_and_checks_the_parameters():
    gruagachan = _t("trad_gruagachan")
    key = "Gruagach Give/Gruagach Blessing: +1 to one Ability"
    values = {
        "name": "Luck of the Hare",
        "kind": "spell",
        "rule": "Formulaic spell",
        "use_1": "Gruagach Give",
        "use_2": "Gruagach Blessing",
        "guideline": key,
        "range": "Voice",
        "duration": "Sun",
        "magnitudes": 0,
    }
    made = tf.effect_from(gruagachan, None, values)
    assert (made.guideline, made.level) == (key, 20)
    assert tf.design_problem(gruagachan, values) is None
    wrong = {**values, "use_2": "Gruagach Curse"}
    assert "guideline is for" in (tf.design_problem(gruagachan, wrong) or "")
    labels = [f.key for f in tf.effect_fields(gruagachan, made)]
    assert {"guideline", "range", "duration", "target", "magnitudes"} <= set(labels)


# ---------------------------------------------------------------------------
# Casting totals: Ease Factors, botch dice


def test_a_folk_witch_power_shows_the_die_its_ease_factor_needs():
    witch = _member("trad_folk_witches")
    witch.characteristics = Characteristics(dexterity=2)
    _set(witch, "Cursing", 4)
    tradition = _t("trad_folk_witches")
    curse = _effect(
        "trad_folk_witches", "Curse of Aging", ["Cursing"], rule="Folk witch powers"
    )
    found = he.effect_total(witch, tradition, curse)
    assert found is not None
    assert (found.die, found.against, found.level, found.equivalent) == (
        6,
        "Ease Factor",
        12,
        20,
    )
    words = he.total_words(found, curse)
    assert "needs a die of 6 against Ease Factor 12" in words
    assert "counts as level 20" in words


def test_hedge_castings_roll_botch_dice():
    vitkir = _t("trad_vitkir")
    script = next(r for r in vitkir.casting if r.name == "Rune script")
    assert hc.botch_dice(vitkir, script) == 1
    # Vis and another realm's aura add, as for Hermetic magi.
    assert hc.botch_dice(vitkir, script, vis_pawns=2, aura=3, aura_realm="Divine") == 6
    assert hc.botch_dice(vitkir, script, aura=3, aura_realm="Magic") == 1
    lab = next(r for r in vitkir.casting if r.lab)
    assert hc.botch_dice(vitkir, lab) == 0
    learned = _t("trad_learned_magicians")
    known = next(r for r in learned.casting if r.name == "Known charm")
    assert hc.botch_dice(learned, known) == 0  # a simple die
    amazons = _t("trad_amazon_sorceresses")
    rite = next(r for r in amazons.casting if r.name == "Rite")
    assert hc.botch_dice(amazons, rite, level=20, aura=3) == 4 + 3
    muspelli = _t("trad_muspelli")
    ordinary = next(r for r in muspelli.casting if r.name == "Ordinary use")
    assert "Wildfire" in ordinary.botch_notes


# ---------------------------------------------------------------------------
# Opening and the sabbat


def test_the_opening_ease_factor_counts_hermetic_arts_with_xp():
    tradition = _t("trad_learned_magicians")
    student = Character(id="s", name="S", type="companion")
    student.arts = {"Creo": ArtScore(xp=0), "Vim": ArtScore(xp=15)}  # Vim 5
    # Vim 5 doubled, +12 for Arts already opened; Creo at 0 xp counts nothing.
    assert ts.opening_ease(student, tradition) == 10 + 12
    unopened = Character(id="u", name="U", type="companion")
    unopened.arts = {"Creo": ArtScore(xp=0)}
    assert ts.opening_ease(unopened, tradition) == 0
    magus = Character(id="m", name="M", type="magus")
    assert ts.already_opened(magus, tradition)


def test_the_sabbat_helps_up_to_the_magic_aura():
    witches = _t("trad_folk_witches")
    assert ts.sabbat_bonus(witches, "Opening Total", 5, 3, "Magic") == 3
    assert ts.sabbat_bonus(witches, "Opening Total", 2, 3, "Magic") == 2
    assert ts.sabbat_bonus(witches, "Opening Total", 5, 3, "Faerie") == 0
    assert ts.sabbat_bonus(_t("trad_vitkir"), "Opening Total", 5, 3, "Magic") == 0
    group = witches.groups[0]
    assert hc.most_helpers(group, aura=4, aura_realm="Divine") == 0


# ---------------------------------------------------------------------------
# Hunters: any Foe Art with any Practice Art


def test_a_hunter_pairs_any_foe_art_he_holds():
    hunter = _member("trad_hunters", gifted=False)
    _set(hunter, "Scry", 3)
    _set(hunter, "Foe: Werewolf", 2)
    _set(hunter, "Foe: Dragon", 1)
    hunters = _t("trad_hunters")
    scry = next(r for r in hunters.casting if r.name == "Scry")
    labels = {c.label for c in hc.castings(hunter, hunters, scry)}
    assert {"Scry Foe: Werewolf", "Scry Foe: Dragon"} <= labels
    sight = _effect("trad_hunters", "Direction and distance", ["Scry"], range="Sight")
    assert he.effect_level(hunters, sight) == 4


# ---------------------------------------------------------------------------
# The traditions' own totals


def test_what_a_season_of_refining_yields():
    saga = Saga(id="s", name="S", current_year=1220)
    elementalist = _member("trad_elementalists")
    elementalist.background.year_born = 1170
    _set(elementalist, "Elementalist Fire", 4)
    _set(elementalist, "Elementalist Earth", 6)
    elementalist.virtues_flaws.append(
        VirtueFlawInstance("vf_type_refining_major", params={"type": "Medicinal"})
    )
    lines = tt.refining_yields(saga, elementalist, 25)
    assert lines[0].startswith("Longevity potion: +5 to Aging rolls")
    assert "10 pawns at age 50" in lines[0]
    assert any(
        line.startswith("Characteristic potion for a year: +5, to at most +3")
        for line in lines
    )
    assert not any(line.startswith("Vis from an aura") for line in lines)
    assert tt.refining_types(_member("trad_elementalists")) == list(tt.REFINING_TYPES)
    assert tt.characteristic_potion(25, 4) == 2  # the book's example
    # Total / 10 with no rounding given rounds down (DE p. 6).
    assert tt.extracted_vis(25) == 2
    assert tt.longevity_bonus(24) == 4
    assert tt.vis_moved(25) == 5
    assert tt.might_change(30, 20, same_form=False, opposed=False) == 5


def test_augustan_animations_and_rites():
    assert tt.animation_might(size=0, material_points=4) == 7
    assert tt.awakening_ease(7, mobile=True, aware=True) == 19
    assert tt.most_inscribed_ease(7) == 14
    assert tt.rite_vis(21) == 4
    assert tt.rite_is_ritual(33) and tt.rite_is_ritual(12, target="City")
    assert not tt.rite_is_ritual(30)


def test_the_fertility_ritual_and_single_ease_factors():
    assert tt.trait_points(25) == 3
    assert tt.trait_points(25, own_child=True) == 5
    assert tt.trait_cost({"The Gift": 1, "Minor Virtue or Flaw": 2}) == 5
    assert tt.repeat_warping(5) == 3
    assert tt.necromancy_ease(15) == 9  # the book's InCo 15 example
    assert tt.amulet_charges(30, 15) == 3
    assert tt.amulet_charges(10, 15) == 0
    assert tt.charta_total(25) == 12
    assert tt.scroll_ease(15) == 6
    assert tt.geomancy_ease("Minor", "Short sentence") == 15
    assert tt.stylus_bonus("Human bone", fits=True) == 3
    assert tt.stylus_bonus("Finger", fits=True) == 0


def test_aetheric_magic_is_a_breakthrough_goal():
    goal = integrations.BY_NAME["Aetheric Magic"]
    assert (goal.kind, goal.target) == ("Hermetic", 100)
    assert "20" in goal.gives
