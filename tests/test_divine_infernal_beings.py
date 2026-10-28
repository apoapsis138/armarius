"""Angels and demons: divine beings and angels (RoP: The Divine pp.
16-26; DE pp. 488-489), holy influence and tempers (pp. 36-41), the holy
Powers' guidelines (pp. 46-56; Errata pp. 48-49) and the maleficia's
(RoP: The Infernal pp. 102-112; Errata p. 56)."""

import random
import re
from dataclasses import replace

from ars_magica_manager import actions, catalog, tradition_text
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import creature as creature_forms
from ars_magica_manager.forms import holy_influence as holy_forms
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.models import (
    Ability,
    Character,
    Characteristics,
    Creature,
    CreaturePower,
    Saga,
    ScoredTrait,
    TraditionEffect,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import divine_build as db
from ars_magica_manager.rules import hedge_effects as he
from ars_magica_manager.rules import holy_influence as hi
from ars_magica_manager.rules import holy_powers as hp
from ars_magica_manager.rules import maleficia as mal
from ars_magica_manager.sections import FAITH_SECTION
from ars_magica_manager.sheets import creature as sheet


def _angel(order: str, might: int, **kw) -> Creature:
    """An angel of the Choirs `order` names, built by the book."""
    choirs = [c for c in db.CHOIRS if c.name.casefold() in order.casefold()] or [
        db.CHOIRS[-1]
    ]
    traits = [ScoredTrait(*db.LOVE_OF_GOD)]
    powers = [
        CreaturePower(p.name, might_cost=p.costs[0], init=p.init, form=p.form)
        for p in db.ANGELIC_POWERS
    ]
    for choir in choirs:
        traits += [ScoredTrait(n, s) for n, s in choir.traits]
        powers += [
            CreaturePower(p.name, might_cost=p.costs[0], init=p.init, form=p.form)
            for p in choir.powers
        ]
    score = db.mental_score(might)
    return Creature(
        id="a",
        name="An angel",
        realm="Divine",
        might=might,
        might_form="Corpus",
        order=order,
        characteristics=Characteristics(
            intelligence=score, perception=score, presence=score, communication=score
        ),
        personality_traits=traits,
        powers=powers,
        **kw,
    )


# -- divine beings and angels --


def test_a_seraph_built_by_the_book_passes():
    seraph = _angel("Seraphim", 35)
    assert [c.name for c in db.choirs_of(seraph)] == ["Seraphim"]
    assert db.problems(seraph) == []
    assert db.least_might(seraph) == 35


def test_the_choirs_least_might_traits_and_powers():
    weak = _angel("Seraphim", 20)
    weak.characteristics = Characteristics(
        intelligence=2, perception=2, presence=2, communication=2
    )
    found = " ".join(db.problems(weak))
    assert "no less than 35, not 20" in found
    cherub = _angel("Cherubim", 30)
    cherub.personality_traits = [ScoredTrait("Love of God", 5), ScoredTrait("Wise", 2)]
    cherub.powers[0].might_cost = 4
    found = " ".join(db.problems(cherub))
    assert "Contemplative +4 (p. 22)" in found and "Wise +4, not +2" in found
    assert "Angelic Mantle costs 2 point(s), Init +12, not 4, +12" in found
    cherub.powers = [p for p in cherub.powers if p.name != "The Chariot"]
    assert "Missing powers: The Chariot (p. 22)" in " ".join(db.problems(cherub))


def test_an_archangel_keeps_its_first_choir():
    # p. 25: an archangel has its own Choir's traits and the Archangels'.
    michael = _angel("Seraphim and Archangels", 60)
    assert [c.name for c in db.choirs_of(michael)] == ["Seraphim", "Archangels"]
    assert db.problems(michael) == []
    assert db.least_might(_angel("Angels, Archangels", 10)) == 50
    # "Archangel" alone is not the Angels' Choir.
    assert [c.name for c in db.choirs_of(_angel("Archangel", 50))] == ["Archangels"]


def test_mental_characteristics_follow_the_might():
    # p. 19: Might 1-10 gives +1, 11-20 +2; Might 90 +9.
    assert [db.mental_score(m) for m in (1, 10, 11, 20, 90)] == [1, 1, 2, 2, 9]
    odd = _angel("Angels", 25)
    odd.characteristics = Characteristics(
        intelligence=2, perception=3, presence=3, communication=3
    )
    assert "are +3: Int differ" in " ".join(db.problems(odd))


def test_a_divine_being_without_a_choir_is_only_checked_for_true_faith():
    # DE p. 488: no True Faith for a creature with Divine Might; the DE's
    # angels name no Choir, so nothing else is checked.
    wolf = Creature(id="w", name="Lupersus", realm="Divine", might=20)
    assert db.problems(wolf) == [] and db.notes(wolf) == []
    wolf.virtues_flaws = [VirtueFlawInstance("vf_true_faith")]
    assert db.problems(wolf) == [
        "A creature with Divine Might can't have True Faith (DE p. 488)."
    ]
    demon = Creature(id="d", name="D", realm="Infernal", might=20, order="Angels")
    assert db.choirs_of(demon) == [] and db.problems(demon) == []


def test_an_angels_notes():
    throne = _angel("Thrones", 40, abilities=[Ability("Penetration", xp=15)])
    found = "; ".join(db.notes(throne))
    assert "Second Sight 8" in found
    assert "illumination penetrates at 2" in found
    assert "Holy Influence Total 20" in found
    assert "+5 to the Penetration multiplier" in found
    assert db.smite_evil_level(3) == 30
    assert db.sway_cost("a town or city") == 15
    assert db.sway_cost("a duchy", temper=4) == 30
    watcher = _angel("Grigori", 15)
    assert db.is_angel(watcher)
    assert "trapped in its Mantle" in "; ".join(db.notes(watcher))


def test_the_sheet_shows_an_angels_design():
    angel = _angel("Angels", 5)
    angel.might = 0
    facts = {f.label: f.value for f in sheet.build_facts(angel)}
    assert "Divine design" in facts and "As an angel" in facts


def test_the_form_keeps_an_angels_choir():
    saga = Saga(id="s", name="S")
    angel = Creature(id="a", name="A")
    saga.creatures.append(angel)
    values = {f.key: f.value for f in creature_forms.info_fields(saga, angel)}
    values.update(realm="Divine", order="Cherubim", might=25, where=None)
    creature_forms.apply_info(saga, angel, values)
    assert angel.order == "Cherubim" and angel.hierarchy is None
    values.update(realm="Magic")
    creature_forms.apply_info(saga, angel, values)
    assert angel.order == ""


# -- the holy Powers' guidelines --


def _t(tradition_id: str):
    return catalog.load_tradition_catalog_by_id()[tradition_id]


def _level(tradition_id: str, guideline: str, uses: list[str], **kw) -> int:
    effect = TraditionEffect(
        "E", tradition=tradition_id, guideline=guideline, uses=uses, **kw
    )
    return he.effect_level(_t(tradition_id), effect)


def test_holy_traditions_hold_their_powers_guidelines():
    ascetics = _t("trad_ascetics")
    powers = {g.arts[0] for g in ascetics.guidelines}
    assert powers == {"Adjuration", "Cursing"}
    assert "Holy Powers' guidelines, pp. 48-56" in ascetics.guideline_source
    assert any(
        p.name == "Boundary" and p.magnitudes == 8 for p in ascetics.effect_parameters
    )
    # The witch-hammers keep their Goetic table and add the maleficia's.
    hammers = _t("trad_witch_hammers")
    assert {g.arts[0] for g in hammers.guidelines} == {
        "Summoning",
        "Ablating",
        "Psychomachia",
    }
    assert (
        "Ars Goetia" in hammers.guideline_source
        and "maleficia" in hammers.guideline_source
    )
    # A tradition naming no set is unchanged.
    assert "Holy Powers" not in _t("trad_folk_witches").guideline_source


def test_the_books_holy_effects():
    # p. 51: Let death seize upon them, Base 30, +3 Sight, +4 Bound, +4 ritual.
    assert (
        _level(
            "trad_ascetics",
            "Cursing: Strike dead (Purity)",
            ["Purity", "Cursing"],
            range="Sight",
            target="Boundary",
        )
        == 85
    )
    # p. 49: The angel of the LORD encampeth, Base 5, +2 Voice, +2 Sun.
    assert (
        _level(
            "trad_ascetics",
            "Adjuration: Drive away (Purity)",
            ["Purity", "Adjuration"],
            range="Voice",
            duration="Sun",
        )
        == 25
    )
    # p. 49: Isabelle's Holy Music blessing, a +6 recovery at Touch, Moon.
    assert (
        _level(
            "trad_cantores",
            "Blessing: Recovery +6 (Meditation)",
            ["Holy Music", "Blessing"],
            range="Touch",
            duration="Moon",
        )
        == 10
    )
    # p. 52: Have mercy upon me, Base 45, +1 Touch.
    assert (
        _level(
            "trad_cantores",
            "Intervention: Heal a Heavy Wound (Purity)",
            ["Purity", "Intervention"],
            range="Touch",
        )
        == 50
    )


def test_the_errata_corrections_are_in_the_data():
    holy = {g.name: g for g in _t("trad_ascetics").guidelines}
    assert "level + 10" in holy["Dispel (Purity)"].summary
    cursing = {g.name: g for g in _t("trad_sol_invictus").guidelines}
    assert "(the magnitude + 1)" in cursing["Penalty to all rolls (Invocation)"].summary
    effusion = [
        g.name
        for g in _t("trad_dread_host").guidelines
        if g.arts == ["Effusion"] and g.level == 10 and "Incantation" in g.name
    ]
    assert effusion == ["Five paces (Incantation)"]


def test_methods_powers_and_tragedies():
    assert hp.works_with("Wonders", "Invocation")
    assert not hp.works_with("Understanding", "Purity")
    assert hp.works_with("Blessing", "Holy Music")
    # p. 46: 15 against level 30 is Major; Faith 2 makes it Minor, 3 none.
    assert hp.tragedy(15, 30) == "a Major tragedy"
    assert hp.tragedy(15, 30, faith=2) == "a Minor tragedy"
    assert hp.tragedy(15, 30, faith=3) == ""
    assert hp.tragedy(5, 30) == "an Ultimate tragedy"


def test_a_holy_effects_row_says_what_it_risks():
    ascetics = _t("trad_ascetics")
    saint = Character(id="h", name="Hermit", type="companion")
    saint.traditions = ["trad_ascetics"]
    saint.background.true_faith_score = 2
    effect = TraditionEffect(
        "Curse",
        tradition="trad_ascetics",
        rule="Holy Method and Power",
        guideline="Cursing: Light Wound (Purity)",
        uses=["Invocation", "Cursing"],
    )
    notes = hp.effect_notes(saint, ascetics, effect)
    assert "its guideline is for Purity (p. 48)" in notes
    assert any("True Faith stands in as 20" in n for n in notes)
    wonder = TraditionEffect("W", tradition="trad_ascetics", uses=["Purity", "Wonders"])
    assert hp.effect_notes(saint, ascetics, wonder)[0].startswith(
        "Wonders works with Invocation, not Purity"
    )
    saint.tradition_effects = [effect]
    saga = Saga(id="s", name="S")
    rows = tradition_text.effect_rows(saga, saint, ascetics)
    assert "tragedy of hubris" in rows[0][1]


# -- the maleficia --


def test_the_books_maleficia():
    # p. 103: Richard's blessing, base 15, Personal, Forsaken, Individual.
    assert (
        _level(
            "trad_dark_gnostics",
            "Diablerie: Minor False Power (Incantation)",
            ["Incantation", "Diablerie"],
            duration="Forsaken",
        )
        == 35
    )
    # p. 109 (Errata p. 56: level 40): Base 20, +2 Voice, +2 Cursed.
    assert (
        _level(
            "trad_luciferans",
            "Malediction: Strike dead (Debauchery)",
            ["Debauchery", "Malediction"],
            range="Voice",
            duration="Cursed (Condition)",
        )
        == 40
    )
    # p. 109: Roll, you clouds, Base 3, +3 Sight, +1 Conc, +2 Group.
    assert (
        _level(
            "trad_strigae",
            "Effusion: Control normal phenomena (Debauchery)",
            ["Debauchery", "Effusion"],
            range="Sight",
            duration="Concentration",
            target="Group",
        )
        == 25
    )
    # p. 112: I will make them of the synagogue of Satan, Base 20, +2 Voice,
    # +2 Sun, +2 Group (here Passion, as Group).
    assert (
        _level(
            "trad_witch_hammers",
            "Psychomachia: Simple command (Incantation)",
            ["Incantation", "Psychomachia"],
            range="Voice",
            duration="Sun",
            target="Passion",
        )
        == 50
    )


def test_falling_short_of_a_maleficium():
    # p. 102: 18 against 30 is two botches and two Warping Points.
    short = mal.failure(18, 30)
    assert (short.botches, short.warping, short.vituperation) == (2, 2, True)
    assert mal.failure(18, 30, hierarchy=3) == mal.Failure(0, 0)
    assert mal.failure(18, 30, hierarchy=2) == mal.Failure(1, 1)
    # p. 103: Richard's 22 against 35 is two, 25 one.
    assert mal.failure(22, 35).botches == 2 and mal.failure(25, 35).botches == 1
    assert mal.vis_cap(5, 5) == 10


def test_a_maleficiums_row_notes():
    gnostics = _t("trad_dark_gnostics")
    witch = Character(id="w", name="Witch", type="companion")
    witch.abilities = [
        Ability("Incantation", xp=50, xp_table="ability"),
        Ability("Diablerie", xp=50, xp_table="ability"),
    ]
    effect = TraditionEffect(
        "Blessing",
        tradition="trad_dark_gnostics",
        guideline="Diablerie: Magic Resistance (Incantation)",
        uses=["Incantation", "Diablerie"],
    )
    notes = mal.effect_notes(witch, gnostics, effect)
    assert any("up to 8" in n for n in notes)
    assert any("each 10 levels short" in n for n in notes)


# -- holy influence and tempers --


def _priest() -> Character:
    return Character(
        id="p",
        name="Father Anselm",
        type="companion",
        characteristics=Characteristics(presence=2, communication=1),
        abilities=[Ability("Leadership", xp=15), Ability("Dominion Lore", xp=15)],
        virtues_flaws=[VirtueFlawInstance("vf_priest")],
        personality_traits=[
            ScoredTrait("Dedicated (Loyal)", 3),
            ScoredTrait("Cruel (Envious)", 2),
        ],
    )


def test_the_influence_and_aid_tables():
    assert [hi.influence_value(t) for t in (8, 9, 14, 15, 23, 24, 40)] == [
        0,
        1,
        1,
        2,
        2,
        3,
        3,
    ]
    assert hi.aid_bonus(9) == 1 and hi.temper_after(3, 2) == 1


def test_traits_lean_to_tempers():
    loyal = hi.temper_named("Loyal")
    assert hi.lean("Dedicated (Loyal)") == (loyal, 1)
    kind = hi.temper_named("Kind")
    assert hi.lean("Cruel (Envious)") == (kind, -1)
    strong = hi.temper_named("Strong")
    assert hi.lean("Selfless") == (strong, 1)
    # RoP: The Infernal's row for the same sin is read too.
    assert hi.lean("Steady") == (strong, 1)
    assert hi.temper_scores(_priest()) == {"Loyal": 3, "Kind": -2}


def test_tempers_and_schism():
    tempers = [ScoredTrait("Calm", 2), ScoredTrait("Brave", 1)]
    # A fight in an aura tempered Calm and Brave: +1 for courage, -2 for
    # the fighting.
    assert hi.roll_modifier(tempers, ["Brave"], ["Calm"]) == -1
    assert hi.in_schism(tempers)
    assert not hi.in_schism(tempers[:1])


def test_who_may_influence():
    priest = _priest()
    assert hi.may_influence(priest, hi.SPIRITUAL, hi.SEASON) == ""
    assert "Temporal Influence" in hi.may_influence(priest, hi.TEMPORAL, hi.SEASON)
    assert "Inspirational" in hi.may_influence(priest, hi.NONE, hi.SEASON)
    assert "Faith or Confidence" in hi.may_influence(priest, hi.SPIRITUAL, hi.CEREMONY)
    priest.virtues_flaws.append(VirtueFlawInstance("vf_inspirational"))
    priest.background.confidence_points = 1
    assert hi.may_influence(priest, hi.NONE, hi.CEREMONY) == ""
    grog = Character(id="g", name="G", type="grog")
    assert "Confidence" in hi.may_invoke_aid(grog)
    assert hi.aid_total(priest) == 1 + 2


def test_the_holy_influence_roll_spends_a_faith_point():
    saga = Saga(id="s", name="S", current_year=1220, current_season="Spring")
    priest = _priest()
    priest.virtues_flaws.append(VirtueFlawInstance("vf_true_faith"))
    priest.background.true_faith_score = 1
    priest.background.faith_points = 2
    saga.characters.append(priest)
    form = holy_forms.holy_influence_form(saga, priest, random.Random(3))
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    assert values["trait"] == "Loyal" and values["temper"] == "Loyal"
    assert holy_forms.lines(priest, values)[0].startswith(
        "Presence + Leadership +4 + simple die"
    )
    assert form.validate is not None
    assert "Inspirational" in (form.validate({**values, "authority": hi.NONE}) or "")
    ceremony = {**values, "method": hi.CEREMONY, "group": 1}
    assert form.validate(ceremony) is None
    assert form.apply(ceremony)
    assert priest.background.faith_points == 1
    assert priest.diary[-1].name == holy_forms.TITLE
    form.apply({**values, "target": holy_forms.AURA})
    assert priest.diary[-1].name == "Holy Temper"
    assert isinstance(holy_forms.holy_influence_form(saga, None), Refuse)


def test_holy_influence_is_offered_to_one_of_holy_standing():
    saga = Saga(id="s", name="S")
    saga.characters += [_priest(), Character(id="m", name="M", type="companion")]
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="p")
    labels = [item.label for item in menu_forms.placed(page, "Faith")]
    assert "Holy Influence" in labels
    faith = replace(page, section=FAITH_SECTION)
    assert actions.available("holy_influence", faith)
    plain = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="m")
    assert not actions.available(
        "holy_influence", replace(plain, section=FAITH_SECTION)
    )
    # A rabbi has it too; a pagan priest's faith gives no holy influence.
    saga.character("p").background.religion = "Jewish"
    assert actions.available("holy_influence", faith)
    saga.character("p").background.religion = "Pagan"
    assert not actions.available("holy_influence", faith)
    saga.character("p").background.religion = ""
    saga.books_in_play = ["DE"]
    assert not actions.available("holy_influence", faith)


def _guideline_set(name: str) -> list[dict]:
    return catalog._guideline_sets(catalog.POWER_GUIDELINES_PATH)[name]["guidelines"]


def test_the_errata_methods_and_signs_of_the_holy_guidelines():
    # Errata p. 48: Transcendence's level 4 is Meditation, its level 10
    # wound and Fatigue effects and level 30 mind are Purity; p. 49: the
    # second Wonders level 15 is Invocation; and every "(level - X)" or
    # "(magnitude - X)" on RoP: The Divine pp. 48-56 is "+ X", except
    # Blessing's three Generals capped at +3.
    holy = _guideline_set("holy_powers")
    named = {(g["arts"][0], g["level"], g["name"]) for g in holy}
    for wanted in (
        ("Transcendence", 4, "Unharmed by a material (Meditation)"),
        ("Transcendence", 10, "Ignore wounds (Purity)"),
        ("Transcendence", 10, "Ignore Fatigue (Purity)"),
        ("Transcendence", 30, "Restore a mind (Purity)"),
        ("Wonders", 15, "Small creature (Invocation)"),
    ):
        assert wanted in named, wanted
    minus = re.compile(r"(level|magnitude)\)?\s*-\s*\d")
    offenders = sorted(
        (g["arts"][0], g["name"]) for g in holy if minus.search(g["summary"])
    )
    assert offenders == [
        ("Blessing", "Bless a tool (Invocation)"),
        ("Blessing", "Temper an aura (Invocation)"),
        ("Blessing", "Virtuous task (Invocation)"),
    ], offenders


def test_the_psychomachia_tarnish_guideline_notes_the_example():
    # RoP: The Infernal p. 112, and the p. 111 example's reading.
    tarnish = next(
        g
        for g in _guideline_set("maleficia")
        if g["name"] == "Tarnish an aura (Debauchery)"
    )
    assert "magnitude + 3, +6 at most" in tarnish["summary"]
    assert "base effect's" in tarnish["summary"]
