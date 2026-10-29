"""Dealing with faeries: fable and offers to the Faerie Realm (RoP: Faerie
pp. 25-29) and the Ars Fabulosa's bargaining powers (pp. 131-134)."""

import random

from ars_magica_manager import actions, deeds
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import faerie_dealings as forms
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.models import (
    Ability,
    Character,
    Characteristics,
    Saga,
    ScoredTrait,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import faerie_dealings as fd
from ars_magica_manager.rules.faerie_sympathy import SYMPATHY


def _bargainer() -> Character:
    return Character(
        id="b",
        name="Vasilisa",
        type="companion",
        characteristics=Characteristics(
            presence=2, communication=1, perception=1, intelligence=2, quickness=1
        ),
        abilities=[
            Ability("(Faerie) Summoning", xp=15, xp_table="art"),
            Ability("Bonding", xp=0, xp_table="art"),
            Ability("Penetration", xp=5),
            Ability("Bargain", xp=15),
            Ability("Faerie Lore", xp=5),
        ],
        personality_traits=[
            ScoredTrait("Oak", 2, type=SYMPATHY),
            ScoredTrait("Iron", -1, type=SYMPATHY),
            ScoredTrait("Brave", 2),
        ],
    )


def _saga() -> Saga:
    saga = Saga(id="s", name="Test", current_year=1220, current_season="Spring")
    saga.characters.append(_bargainer())
    saga.characters.append(Character(id="m", name="Plain", type="companion"))
    return saga


def _oak(character: Character) -> list[ScoredTrait]:
    return [t for t in character.personality_traits if t.name == "Oak"]


# -- fable (p. 26) --


def test_fable_score_costs_its_next_value_in_points():
    assert fd.fable_points_to_raise(0) == 1
    assert fd.fable_points_to_raise(5) == 6
    assert fd.fable_from_points(1) == (1, 0)
    assert fd.fable_from_points(3) == (2, 0)
    assert fd.fable_from_points(7) == (3, 1)


# -- offers (pp. 27-29) --


def test_the_minstrels_offer_matches_the_books_example():
    """Communication + Profession 8 and Free Expression make 11; a hut
    from a tree (+3) by mundane actions (-6) is -3 (p. 29)."""
    minstrel = Character(
        id="x",
        name="Minstrel",
        type="companion",
        characteristics=Characteristics(communication=3),
        abilities=[Ability("Profession: Storyteller", xp=75)],
        virtues_flaws=[VirtueFlawInstance(fd.FREE_EXPRESSION)],
    )
    offer = fd.Offer(
        ability="Profession: Storyteller",
        goods="Minor mortal goods (bread, beer, milk, cheese, wine)",
        promise="Mundane actions overcome the threat",
        change="An object becomes a tool against the threat",
    )
    total = fd.offer_total(minstrel, offer)
    assert total.total == 8
    labels = [line.label for line in total.lines]
    assert "Free Expression (the highest bonus)" in labels
    assert "Goods offered (the highest bonus)" not in labels


def test_offer_ease_factors_and_places():
    assert fd.offer_ease_factor("Trivial") == 6
    assert fd.offer_ease_factor("Overwhelming") == 18
    assert fd.offer_ease_factor("Serious", fd.RESTORING) == 9
    plain = Character(id="p", name="P", type="companion")
    elysium = fd.offer_total(plain, fd.Offer(ability="Charm", place=fd.ELYSIUM))
    assert elysium.total == -6
    fable = fd.Offer(ability="Charm", fable_score=4, spend_fable=True)
    assert fd.offer_total(plain, fable).total == 4
    assert fd.offer_fable_cost(fable) == 2


def test_art_and_academe_bonuses_round_up():
    plain = Character(id="p", name="P", type="companion")
    offer = fd.Offer(ability="Charm", artistic_reputation=4, patron_might=6)
    assert fd.offer_total(plain, offer).total == 2 + 2


def test_offer_abilities_are_charm_professions_crafts_and_music():
    person = Character(
        id="p",
        name="P",
        type="companion",
        abilities=[Ability("Craft: Carving", xp=5), Ability("Brawl", xp=5)],
    )
    assert fd.offer_abilities(person) == ["Craft: Carving"]
    assert fd.offer_abilities(Character(id="q", name="Q", type="companion")) == [
        "Charm"
    ]


# -- the Ars Fabulosa (pp. 131-134) --


def test_power_totals_add_rank_and_aura():
    who = _bargainer()
    assert fd.held_powers(who) == [fd.SUMMONING, fd.BONDING]
    assert fd.faerie_rank(who) == 1
    summoning = fd.power_total(who, fd.SUMMONING, aura=3, aura_realm="Faerie")
    assert summoning.total == 5 + 2 + 1 + 3
    magic = fd.power_total(who, fd.SUMMONING, aura=3, aura_realm="Magic")
    assert magic.total < summoning.total


def test_might_limit_counts_negatives_by_size():
    who = _bargainer()
    assert fd.might_limit(_oak(who)) == 10
    assert fd.might_limit(who.personality_traits[:2]) == 15
    assert fd.best_trait(who.personality_traits[:2]) == 2


def test_summoning_needs_penetration_only_with_an_arcane_connection():
    who = _bargainer()
    bonus = int(fd.penetration_bonus(who, _oak(who)).total)
    assert bonus == 1 + 2
    wild = fd.Target(fd.SUMMONING, might=10)
    assert fd.total_needed(wild, bonus) == 10
    assert fd.outcome(wild, 10, bonus).worked
    assert not fd.outcome(wild, 9, bonus).worked
    connected = fd.Target(fd.SUMMONING, might=10, connected=True)
    linked = int(fd.penetration_bonus(who, _oak(who), "Hours or days").total)
    assert linked == 1 * 2 + 2
    assert fd.total_needed(connected, linked) == 10 + 1 + 10 - 4
    assert fd.outcome(connected, 16, linked).penetrated is False
    assert fd.outcome(connected, 17, linked).worked


def test_bonding_a_held_faerie_counts_its_might_as_level_zero():
    """Might 15: a total + bonus of 31 not held, 16 held (pp. 132-133; the
    DE's strict Penetration, one more than the book's example)."""
    held = fd.Target(fd.BONDING, might=15, held=True)
    free = fd.Target(fd.BONDING, might=15)
    assert fd.penetration_level(held) == 0
    assert fd.total_needed(free, 0) == 31
    assert fd.total_needed(held, 0) == 16
    assert not fd.outcome(free, 15, 15).worked
    assert fd.outcome(free, 16, 15).worked
    assert not fd.outcome(held, 15, 10).worked


def test_dismissing_works_against_the_effects_level_or_the_might():
    cancel = fd.Target(fd.DISMISSING, might=20, effect_level=10)
    assert fd.target_score(cancel) == 10
    assert fd.total_needed(cancel, 0) == 20 + 1 + 10
    release = fd.Target(fd.DISMISSING, might=20, dismissal=fd.RELEASE, held=True)
    assert fd.target_score(release) == 20
    assert fd.total_needed(release, 0) == 21
    assert "freed" in fd.outcome(release, 21, 0).text
    who = _bargainer()
    two = fd.power_total(who, fd.BONDING)
    assert fd.power_total(who, fd.BONDING, dismissed=3).total == two.total
    who.abilities.append(Ability("Dismissing", xp=0, xp_table="art"))
    one = fd.power_total(who, fd.DISMISSING).total
    assert fd.power_total(who, fd.DISMISSING, dismissed=3).total == one - 12


def test_deflecting_adds_the_best_trait_only_with_finesse():
    who = _bargainer()
    assert fd.deflect_total(who, _oak(who)) == 1
    who.abilities.append(Ability("Finesse", xp=5))
    assert fd.deflect_total(who, _oak(who)) == 1 + 1 + 2


def test_a_botch_summons_a_faerie_all_the_same():
    result = fd.outcome(fd.Target(fd.SUMMONING, might=5), 0, 0, botched=True)
    assert not result.worked and "comes all the same" in result.text


def test_captivating_warps_a_season_and_a_year():
    assert fd.captivating_warping(1) == 1
    assert fd.captivating_warping(4) == 5
    assert fd.captivating_warping(8) == 10


def test_botch_dice_add_the_worst_negative_trait_and_a_foreign_aura():
    who = _bargainer()
    assert fd.botch_dice(who, 3, "Faerie") == 2
    assert fd.botch_dice(who, 3, "Magic") == 5


# -- Sympathy experience (pp. 103, 131-132) --


def test_trait_experience_raises_lowers_and_respects_the_warping_limit():
    trait = ScoredTrait("Oak", 0, type=SYMPATHY, deeds=4)
    assert fd.trait_experience(trait, 1, 1, limited=True) == 1
    assert (trait.score, trait.deeds) == (1, 0)
    assert fd.trait_experience(trait, -1, 1, limited=True) == -1
    assert (trait.score, trait.deeds) == (0, 4)
    zero = ScoredTrait("Ash", 0, type=SYMPATHY)
    fd.trait_experience(zero, -1, 0, limited=False)
    assert (zero.score, zero.deeds) == (-1, 9)
    blocked = ScoredTrait("Iron", -1, type=SYMPATHY, deeds=9)
    assert fd.trait_experience(blocked, 1, 1, limited=True) == 0
    assert blocked.deeds == 10
    assert fd.trait_experience(blocked, 0, 1, limited=False) == 1
    assert (blocked.score, blocked.deeds) == (0, 0)


def test_die_experience():
    assert fd.die_experience(1, 0) == 1
    assert fd.die_experience(5, 0) == 0
    assert fd.die_experience(0, 2) == -2


def test_bargain_and_wants_totals():
    who = _bargainer()
    assert fd.bargain_total(who, _oak(who)) == 1 + 2 + 1 + 2
    assert fd.bargain_total(who) == 1 + 2 + 1
    assert fd.wants_total(who) == 2 + 1
    assert fd.wants_total(who, _oak(who)) == 2 + 1 + 2
    assert fd.specialty_botch_dice(who) == 2


def test_a_trait_as_faerie_lores_specialty_rolls_a_stress_die():
    saga = _saga()
    who = saga.character("b")
    form = forms.faerie_bargain_form(saga, who, random.Random(1))
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    wants = {**values, "wants": True, "trait": "Oak"}
    assert form.live is not None
    assert "simple die" in form.live(wants)
    assert "stress die" in form.live({**wants, "wants_specialty": True})
    tie = {**values, "ending": forms.CONTEST, "trait": "Oak"}
    assert "tie striking no bargain" in form.live(tie)


def test_breaking_a_bargain_gives_a_minus_three_trait():
    who = _bargainer()
    trait = fd.break_bargain(who, "Oak Maidens")
    assert trait in who.personality_traits
    assert (trait.score, trait.type) == (-3, SYMPATHY)


# -- the forms --


def test_ars_fabulosa_form_rolls_spends_fatigue_and_keeps_a_diary():
    saga = _saga()
    who = saga.character("b")
    assert isinstance(forms.ars_fabulosa_form(saga, saga.character("m")), Refuse)
    form = forms.ars_fabulosa_form(saga, who, random.Random(3))
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    assert form.validate is not None
    assert "Tick" in (form.validate(values) or "")
    values["trait_0"] = True
    assert form.live is not None and "reach Might 10" in form.live(values)
    assert "10 at most" in (form.validate({**values, "might": 11}) or "")
    assert form.validate({**values, "might": 8}) is None
    said = form.apply({**values, "might": 8})
    assert said and who.fatigue_level == "winded"
    assert who.diary[-1].name == "Ars Fabulosa: (Faerie) Summoning"
    who.fatigue_level = "unconscious"
    assert "Fatigue" in (form.validate({**values, "might": 8}) or "")


def test_bargain_form_moves_the_trait_or_adds_the_broken_one():
    saga = _saga()
    who = saga.character("b")
    form = forms.faerie_bargain_form(saga, who, random.Random(1))
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    form.apply({**values, "faerie": "the Oak King", "trait": "Oak"})
    oak = _oak(who)[0]
    assert (oak.score, oak.deeds) == (2, 1)
    assert who.diary[-1].name == forms.BARGAIN_TITLE
    form.apply({**values, "faerie": "a dryad", "ending": forms.NO_BARGAIN})
    assert oak.deeds == 0
    broken = {**values, "ending": forms.BROKEN, "new_trait": "Oak"}
    assert form.validate is not None
    assert "already" in (form.validate(broken) or "")
    form.apply({**broken, "faerie": "the Oak King", "new_trait": "Oak Kings"})
    assert any(t.name == "Oak Kings" and t.score == -3 for t in who.personality_traits)


def test_offer_form_spends_long_term_fatigue():
    saga = _saga()
    who = saga.character("m")
    form = forms.faerie_offer_form(saga, who, random.Random(5))
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    assert form.validate is not None
    assert "fable" in (form.validate({**values, "fable_score": 0}) or "")
    assert form.live is not None and "Accepted on 12" in form.live(values)
    form.apply({**values, "change_text": "a bridge of leaves"})
    assert who.long_term_fatigue == 1
    assert who.diary[-1].name == forms.OFFER_TITLE


def test_the_faerie_commands_are_offered_in_the_deeds_chapter():
    saga = _saga()
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="b")
    labels = [item.label for item in menu_forms.placed(page, deeds.FAERIE)]
    assert {"Ars Fabulosa", "A Faerie Bargain", "An Offer to Faerie"} <= set(labels)
    plain = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="m")
    assert not actions.available("ars_fabulosa", plain)
    assert actions.available("faerie_offer", plain)
    saga.books_in_play = ["DE"]
    assert not actions.available("faerie_offer", plain)
