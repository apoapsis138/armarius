"""Sin, tarnish, Confidence through sin and redemption (RoP: The Infernal
pp. 20-24), the Goetic Arts' totals (pp. 114-119) and the apotropaic
spells (pp. 121-123, Errata p. 56)."""

import random

from ars_magica_manager import actions, catalog
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.casting_text import known_spell_casting_lines
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import goetic as goetic_forms
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import sin as sin_forms
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    Characteristics,
    KnownSpell,
    MasteryAbility,
    Saga,
    ScoredTrait,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import apotropaic as ap
from ars_magica_manager.rules import goetic as gr
from ars_magica_manager.rules import sin


def _saga() -> Saga:
    saga = Saga(id="s", name="Test", current_year=1220, current_season="Spring")
    sinner = Character(
        id="c",
        name="Bertrand",
        type="companion",
        characteristics=Characteristics(presence=2, stamina=1, communication=1),
        abilities=[Ability("Leadership", xp=15), Ability("Infernal Lore", xp=5)],
        personality_traits=[
            ScoredTrait("Cruel (Envious)", 3),
            ScoredTrait("Dedicated", 2),
            ScoredTrait("Likes figs", 2),
        ],
    )
    saga.characters.append(sinner)
    saga.characters.append(Character(id="m", name="Plain", type="magus"))
    return saga


def _sinner(saga: Saga) -> Character:
    found = saga.character("c")
    assert found is not None
    return found


# -- sinful traits --


def test_a_trait_leans_toward_its_sin_or_away_by_its_virtue():
    cruel = sin.lean("Cruel")
    assert cruel is not None and (cruel[0].name, cruel[1]) == ("Envious", 1)
    kind = sin.lean("Kind")
    assert kind is not None and (kind[0].name, kind[1]) == ("Envious", -1)
    dedicated = sin.lean("Dedicated (Loyal)")
    assert dedicated is not None and (dedicated[0].name, dedicated[1]) == ("Proud", -1)
    named = sin.lean("Tells tall tales (Proud)")
    assert named is not None and (named[0].name, named[1]) == ("Proud", 1)
    assert sin.lean("Likes figs") is None
    naive = sin.lean("Naïve")
    assert naive is not None and naive[0].name == "Lustful"


def test_personality_flaws_count_three_and_six():
    saga = _saga()
    sinner = _sinner(saga)
    sinner.virtues_flaws.append(VirtueFlawInstance("vf_wrathful_major"))
    sinner.virtues_flaws.append(VirtueFlawInstance("vf_generous"))
    found = {t.label: (t.sin, t.score) for t in sin.leanings(sinner)}
    assert found["Wrathful (Major Flaw)"] == ("Wrathful", 6)
    assert found["Generous (Minor Flaw)"] == ("Envious", -3)
    assert [t.label for t in sin.sinful_traits(sinner)] == [
        "Wrathful (Major Flaw)",
        "Cruel (Envious)",
    ]
    # The pull toward a sin wins over a pull away from it.
    assert sin.sin_scores(sinner) == {"Proud": -2, "Wrathful": 6, "Envious": 3}


def _flaw_sin(name: str, detail: str = "") -> str | None:
    found = sin.flaw_lean(name, detail)
    return None if found is None else found[0].name


def test_the_sinful_flaws_of_page_17():
    assert _flaw_sin("Hatred") == "Wrathful"
    assert _flaw_sin("Lecherous") == "Lustful"
    assert _flaw_sin("Weak Personality") is None  # not the trait Weak
    # Delusion, Obsessed, Compulsion and Weak-Willed need a sin in brackets.
    assert _flaw_sin("Obsessed") is None
    assert _flaw_sin("Obsessed", "the Crusade") is None
    assert _flaw_sin("Obsessed", "greedy") == "Greedy"
    assert _flaw_sin("Compulsion", "gold (greedy)") == "Greedy"
    assert _flaw_sin("Weak-Willed", "cruel to servants") is None
    saga = _saga()
    sinner = _sinner(saga)
    sinner.virtues_flaws.append(VirtueFlawInstance("vf_hatred_major"))
    sinner.virtues_flaws.append(
        VirtueFlawInstance("vf_obsessed", {"detail": "gold (greedy)"})
    )
    sinner.virtues_flaws.append(VirtueFlawInstance("vf_delusion"))
    found = {t.label: (t.sin, t.score) for t in sin.leanings(sinner)}
    assert found["Hatred (Major Flaw)"] == ("Wrathful", 6)
    assert found["Obsessed (Gold (Greedy)) (Minor Flaw)"] == ("Greedy", 3)
    assert not any(label.startswith("Delusion") for label in found)


def test_a_trait_over_three_needs_a_mortal_sin():
    assert sin.sin_needed(3) == sin.VENIAL
    assert sin.sin_needed(4) == sin.MORTAL
    assert sin.spend_cap(3) == 3 and sin.spend_cap(-2) == 0


def test_confidence_through_sin_and_a_ceremonys_warping():
    assert sin.confidence_through_sin(sin.SEASON) == (1, 0)
    assert sin.confidence_through_sin(sin.CEREMONY) == (1, 1)


# -- influence and tarnish --


def test_the_influence_table():
    assert sin.influence_trait(8) == 0
    assert sin.influence_trait(9) == 1
    assert sin.influence_trait(17) == 3
    assert sin.influence_trait(24) == 6
    assert sin.influence_trait(40) == 6


def test_a_ceremony_needs_infernal_lore_and_a_point():
    saga = _saga()
    sinner = _sinner(saga)
    assert "Confidence Point" in sin.may_influence_ceremonially(sinner)
    sinner.background.confidence_points = 1
    assert sin.may_influence_ceremonially(sinner) == ""
    sinner.abilities = [a for a in sinner.abilities if a.name != "Infernal Lore"]
    assert "Infernal Lore" in sin.may_influence_ceremonially(sinner)


def test_a_tarnish_strengthens_weakens_or_is_gained():
    traits = [ScoredTrait("Cruel", 1), ScoredTrait("Kind", 2), ScoredTrait("Brave", 1)]
    shown = sin.under_tarnish(traits, ScoredTrait("Envious", 3))
    assert [(t.name, t.score) for t in shown] == [
        ("Cruel", 4),
        ("Kind", -1),
        ("Brave", 1),
    ]
    assert traits[0].score == 1
    gained = sin.under_tarnish([ScoredTrait("Brave", 1)], ScoredTrait("Lustful", 2))
    assert [(t.name, t.score) for t in gained] == [("Brave", 1), ("Lustful", 2)]
    assert sin.tarnish_after(3, 2) == 1 and sin.tarnish_after(2, 5) == 0
    assert sin.tarnish_after(-2, 1) == -1
    strongest = sin.strongest_tarnish(
        [ScoredTrait("Lustful", 2), ScoredTrait("Proud", -4)]
    )
    assert strongest is not None and strongest.name == "Proud"


# -- redemption --


def test_absolution_costs_the_false_gift_and_false_powers():
    saga = _saga()
    sinner = _sinner(saga)
    assert sin.absolution_costs(sinner) == []
    sinner.virtues_flaws += [
        VirtueFlawInstance("vf_the_false_gift"),
        VirtueFlawInstance("vf_false_power", {"virtue": "Second Sight"}),
    ]
    costs = sin.absolution_costs(sinner)
    assert "Hermetic Arts" in costs[0]
    assert "Second Sight" in costs[1]


# -- the forms --


def test_confidence_through_sin_keeps_the_points():
    saga = _saga()
    sinner = _sinner(saga)
    sinner.background.confidence_points = 0
    form = sin_forms.sin_form(saga, sinner, random.Random(1))
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    assert values["trait"] == "Cruel (Envious)"
    said = sin_forms.sin_lines(sinner, values)
    assert "venial" in said[0]
    assert any("at most 3" in line for line in said)  # no Confidence Score
    form.apply({**values, "method": sin.CEREMONY})
    assert sinner.background.confidence_points == 1
    assert sinner.aging.warping_realms == {"Infernal": 1}
    assert any(d.name == sin_forms.SIN_TITLE for d in sinner.diary)
    plain = saga.character("m")
    assert isinstance(sin_forms.sin_form(saga, plain), Refuse)


def test_the_influence_roll_spends_a_ceremonys_point():
    saga = _saga()
    sinner = _sinner(saga)
    form = sin_forms.influence_form(saga, sinner, random.Random(2))
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    assert values["trait"] == "Envious"
    assert sin_forms.influence_lines(sinner, values)[0].startswith(
        "Presence + Leadership +4 + simple die"
    )
    ceremony = {**values, "method": sin.CEREMONY}
    assert form.validate is not None
    assert "Confidence Point" in (form.validate(ceremony) or "")
    assert "Inspirational" in (form.validate({**values, "stranger": True}) or "")
    sinner.background.confidence_points = 2
    assert form.validate(ceremony) is None
    said = form.apply(ceremony)
    assert said and sinner.background.confidence_points == 1
    assert sinner.diary[-1].name == sin_forms.INFLUENCE_TITLE


def test_the_sin_commands_are_offered_on_personality_traits():
    saga = _saga()
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="c")
    labels = [item.label for item in menu_forms.placed(page, "Personality Traits")]
    assert labels == [
        "Confidence through Sin",
        "Infernal Influence",
        # Devotion and the saints sit beside them, for any person.
        "Invoke a Saint",
        "Threaten a Saint",
        "Devotion Points",
        "Indulgence, Vigil or Fast",
        "Mystic Path",
        "Invoke God's Aid",
    ]
    plain = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="m")
    plain_labels = [
        item.label for item in menu_forms.placed(plain, "Personality Traits")
    ]
    assert "Confidence through Sin" not in plain_labels
    assert "Infernal Influence" not in plain_labels
    assert not actions.available("ars_goetia", page)


# -- the Goetic Arts --


def _sorcerer() -> Character:
    return Character(
        id="g",
        name="Nicolai",
        type="companion",
        characteristics=Characteristics(presence=1, stamina=0, intelligence=3),
        abilities=[
            Ability("Summoning", xp=55, xp_table="art"),  # 10
            Ability("Binding", xp=0, xp_table="art"),
            Ability("Infernal Lore", xp=30),  # 3
            Ability("Penetration", xp=15),  # 2
        ],
    )


def test_a_summoning_total_and_its_target():
    nicolai = _sorcerer()
    total = gr.total(nicolai, gr.SUMMONING, arcane_connection="Indefinitely")
    # Presence 1 + Summoning 10 + Infernal Lore 3 + aura 0 + Penetration 2 x 5.
    assert total.total == 1 + 10 + 3 + 0 + 2 * 5
    scouring = gr.total(nicolai, gr.SCOURING, lore="Area Lore: Lithuania")
    assert scouring.total == 1 + 10 + 0 + 2
    assert gr.target_level(gr.SUMMONING, 10) == 20
    assert gr.target_level(gr.SUMMONING, 10, demon_hierarchy=2) == 30
    # Against a demon his own Hierarchy x 5 goes on the total (p. 114).
    nicolai.reputations.append(ScoredTrait("Diabolist", 2, type="Infernal"))
    against = gr.total(
        nicolai, gr.SUMMONING, arcane_connection="Indefinitely", demon=True
    )
    assert against.total == total.total + 2 * 5
    assert gr.outcome(gr.SUMMONING, 20, 10).text.startswith("Summoned and held")
    assert "concentrates" in gr.outcome(gr.SUMMONING, 12, 10).text
    assert not gr.outcome(gr.SUMMONING, 9, 10).worked
    assert gr.scouring_might(25) == 12


def test_ablating_binding_and_commanding_must_exceed_the_might():
    assert gr.target_level(gr.ABLATING, 10) == 10
    assert gr.target_level(gr.ABLATING, 10, in_circle=False) == 20
    assert gr.target_level(gr.ABLATING, 10, in_circle=False, resists=False) == 20
    assert gr.target_level(gr.BINDING, 10, in_circle=False, resists=False) == 10
    assert not gr.outcome(gr.ABLATING, 10, 10).worked
    ablated = gr.outcome(gr.ABLATING, 22, 10)
    # Margin 12, no more than the Might: 10 taken, 2 points.
    assert (ablated.might_taken, ablated.ablation_points) == (10, 2)
    assert gr.ablation(17, 10, 20) == (7, 1)
    assert gr.outcome(gr.COMMANDING, 0, 30, resists=False).worked
    assert "60 spell levels" in gr.outcome(gr.BINDING, 13, 12).text
    assert "Vituperation" in gr.outcome(gr.ABLATING, 50, 10, botched=True).text


def test_a_magus_uses_rego_and_vim_for_the_goetic_arts():
    magus = _sorcerer()
    magus.type = "magus"
    magus.arts["rego"] = ArtScore(xp=105)  # 14
    magus.arts["vim"] = ArtScore(xp=55)  # 10
    total = gr.total(magus, gr.BINDING)
    labels = [line.label for line in total.lines]
    assert "Rego (for Binding)" in labels and "Vim (for Infernal Lore)" in labels
    assert total.total == 3 + 14 + 10 + 2


def test_the_goetic_calculator_keeps_nothing():
    saga = _saga()
    nicolai = _sorcerer()
    saga.characters.append(nicolai)
    form = goetic_forms.goetic_form(saga, nicolai, random.Random(4))
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    assert values["art"] == gr.SUMMONING
    said = goetic_forms.lines(nicolai, values)
    assert said[0].startswith("Summoning total +16")
    assert "Against 20" in said[1]
    assert form.apply(values)
    assert nicolai.diary == []
    assert isinstance(goetic_forms.goetic_form(saga, _sinner(saga)), Refuse)
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="g")
    assert "Ars Goetia" in [i.label for i in menu_forms.placed(page, "Abilities")]


def test_the_goetic_traditions_list_the_arts_effects():
    by_id = catalog.load_tradition_catalog_by_id()
    mulhidun = by_id["trad_mulhidun"]
    names = {g.name for g in mulhidun.guidelines}
    assert {"Summon a named spirit", "Ablate a spirit", "Bind a spirit"} <= names
    assert {f"Ablation: {k}" for k in gr.ABLATION_USES} <= names
    assert {f'"{k}"' for k in gr.COMMANDS} <= names
    thessaly = by_id["trad_witches_of_thessaly"]
    assert not any(g.arts == ["Binding"] for g in thessaly.guidelines)
    assert all(g.general for g in mulhidun.guidelines)


def test_goetic_mastery_on_a_known_spell():
    nicolai = _sorcerer()
    notes = gr.mastery_notes(nicolai, {gr.GOETIC_MASTERY: 1}, 2)
    assert notes and "Summoning 10" in notes[0]
    assert gr.mastery_notes(nicolai, {}, 2) == []


# -- apotropaic spells --


def test_the_apotropaic_spells_at_their_levels():
    assert ap.oblivion(25) == 25
    assert ap.might_pool_change(30) == 20  # level - 10 (p. 121)
    assert ap.might_pool_change(5) == 0
    assert ap.jar_holds(35) == 25
    assert ap.devils_hands(25) == (10, 2)
    assert ap.punishment_reach(20, 7) == 22  # 20 / 2 + 5 + 7
    assert ap.punishment_reach(25, 0) == 17
    assert ap.punishment_damage(15) == 7
    assert ap.power_level(ability_score=3) == 15
    assert ap.exorcism(30, 12) == 18 and ap.exorcism(5, 12) == 0
    assert ap.mastery_bonus(3, 2) == 6


def test_an_apotropaic_effect_line_with_mastery():
    line = ap.effect_line(
        "Demon's Eternal Oblivion",
        30,
        mastery_score=2,
        apotropaic_mastery=True,
        hierarchy_score=3,
    )
    assert "loses 36 Might Score" in line and "+6" in line
    # Mastery only raises spells on Infernal Might.
    jar = ap.effect_line(
        "Bind the Devil's Hands", 25, mastery_score=2, hierarchy_score=3
    )
    assert "-10" in jar
    assert ap.effect_line("Pilum of Fire", 20) == ""
    assert ap.effect_line("The Wicked Jar", None) == ""


def test_the_catalogs_spells_carry_the_errata():
    spells = {s.name: s for s in catalog.load_spell_catalog()}
    assert spells["Lash of the Chastened Servant"].level == 5
    assert spells["Adjuration of the Hell-Sworn Spirit"].level == 35
    assert ap.SUMMON_GUIDELINE == 15


def test_a_known_apotropaic_spell_says_what_it_does():
    saga = _saga()
    magus = saga.character("m")
    assert magus is not None
    spell = catalog.load_spell_catalog_by_id()["spell_lash_of_the_chastened_servant"]
    known = KnownSpell(
        spell.id,
        mastery_score=2,
        mastery_abilities=[MasteryAbility("Apotropaic Mastery")],
    )
    magus.reputations.append(ScoredTrait("Demon-hunter", 3, type="Infernal"))
    lines = known_spell_casting_lines(saga, magus, known, spell)
    assert any("a demon loses 5 Might Points" in line for line in lines)
    assert any("Apotropaic Mastery: +6" in line for line in lines)
