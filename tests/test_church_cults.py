"""The Church and the cults: religious seasons for every Christian, the
Theban slander rites, a church's Boons and Hooks, and the Franciscan and
Hermetic cult Scripts."""

import random

import pytest

from ars_magica_manager import catalog, churches, seasons
from ars_magica_manager.models import Ability, Character, Saga, SeasonPlan, XpAllocation
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.rules import church_build, diabolai, mysteries
from ars_magica_manager.rules import tradition_seasons as ts

# -- religious seasons (The Church pp. 16, 27, 130) --


@pytest.mark.parametrize(
    "key", ["good_works", "follow_preacher", "pilgrimage", "penance"]
)
def test_a_magus_may_spend_a_season_on_faith(key):
    magus = Character(id="m", name="Ignatius", type="magus")
    offered = {a.key for a in rules.activities_for(magus)}
    assert key in offered
    assert not any("can't do" in p for p in rules.problems(magus, _plan(key), None))


def test_care_of_souls_stays_a_priests():
    magus = Character(id="m", name="Ignatius", type="magus")
    assert "care_of_souls" not in {a.key for a in rules.activities_for(magus)}


def test_a_magus_doing_good_works_gains_a_faith_point():
    saga = Saga(
        id="s", name="S", characters=[Character(id="m", name="Ig", type="magus")]
    )
    seasons.set_plan(saga, _plan("good_works"))
    seasons.apply(saga, seasons.resolve(saga))
    assert saga.character("m").background.faith_points == 1


def _plan(activity: str) -> SeasonPlan:
    return SeasonPlan(
        "m", 1220, "Spring", activity, [XpAllocation("ability:Church Lore")]
    )


# -- diabolai (The Sundered Eagle pp. 121-122) --


def _villager(lore: int = 3, presence: int = 1) -> Character:
    c = Character(id="v", name="Eleni", type="companion")
    c.characteristics.presence = presence
    c.abilities = [Ability("Faerie Lore", xp=5 * lore * (lore + 1) // 2)]
    return c


def test_the_ease_factor_is_9_plus_a_fifth_of_the_might():
    assert diabolai.ease_factor(0) == 9
    assert diabolai.ease_factor(14) == 11  # rounded down
    assert diabolai.ease_factor(25) == 14


def test_the_total_adds_presence_the_lore_and_the_modifiers():
    eleni = _villager()
    plain = diabolai.total(eleni, "Faerie")
    assert plain.total == 4
    full = diabolai.total(eleni, "Faerie", ("public", "true_name", "recent"), apt=3)
    assert full.total == 4 + 2 + 9 - 9 + 3
    with pytest.raises(ValueError):
        diabolai.total(eleni, "Faerie", apt=6)
    with pytest.raises(ValueError):
        diabolai.total(eleni, "Faerie", ("bribe",))


def test_outcomes_success_annoyance_and_wrath():
    assert diabolai.outcome(14, 14) == diabolai.SUCCESS
    assert diabolai.outcome(13, 14) == diabolai.ANNOYED
    assert diabolai.outcome(5, 14) == diabolai.ANNOYED
    assert diabolai.outcome(4, 14) == diabolai.WRATH  # 10 short
    assert diabolai.outcome(30, 14, botched=True) == diabolai.WRATH
    assert "a year" in diabolai.OUTCOMES[diabolai.WRATH]
    assert "a month" in diabolai.OUTCOMES[diabolai.ANNOYED]


def test_no_lore_no_rite_and_a_missing_power_fails():
    eleni = _villager()
    assert diabolai.problem(eleni, "Faerie") == ""
    assert "Magic Lore" in diabolai.problem(eleni, "Magic")
    assert "no such power" in diabolai.problem(eleni, "Faerie", has_power=False)


def test_a_rite_rolled_matches_its_outcome():
    eleni = _villager()
    for seed in range(40):
        rite = diabolai.perform(random.Random(seed), eleni, "Faerie", 15, ("public",))
        assert rite.ease == 12
        assert rite.result == diabolai.outcome(rite.total, rite.ease, rite.botched)


# -- a church's Build Points, Boons and Hooks (The Church pp. 48-51) --


def test_every_kind_of_church_has_its_build_points():
    assert set(church_build.BUILD_POINTS) == set(churches.CHURCH_KINDS)
    assert church_build.BUILD_POINTS["Archbishop's cathedral"] == 1000
    assert church_build.BUILD_POINTS["Chapel"] == 50


def test_relic_costs():
    assert [church_build.relic_cost(s) for s in range(1, 6)] == [1, 3, 6, 10, 15]
    assert church_build.relic_cost(3, powers=2) == 16  # the urban parish's
    assert church_build.relic_cost(6) == 21
    with pytest.raises(ValueError):
        church_build.relic_cost(0)


def test_church_boons_and_hooks_are_kept_from_the_covenant_catalog():
    covenant = {(e.name, e.tier) for e in catalog.load_covenant_boon_hook_catalog()}
    church = {(e.name, e.tier) for e in church_build.BOONS_AND_HOOKS}
    assert not covenant & church
    # Covenants' Minor Heretics (the people around) isn't the church's
    # Major Heretics (its own priests).
    assert ("Heretics", "Minor") in covenant and ("Heretics", "Major") in church


def test_church_boon_and_hook_checks():
    assert church_build.problems("Parish church", ["Corrupt", "Burial Rights"]) == []
    assert church_build.aura_change(["Anchorite/Anchoress"]) == 1
    found = church_build.problems(
        "Bishop's cathedral", ["Incompetent Curate", "Military Order"]
    )
    assert any("bishop's cathedral" in p for p in found)
    assert any("Boons" in p for p in found)
    many = ["Corrupt", "Heretics", "Jurisdiction", "Absent Rector", "Vast Sanctuary"]
    assert any("up to 10" in p for p in church_build.problems("Parish church", many))
    assert (
        church_build.problems("Parish church", ["Corrupt", "Chantry", "Chantry"]) == []
    )
    assert church_build.problems(
        "Parish church", ["Heretics", "Burial Rights", "Burial Rights"]
    )


# -- cult Scripts (The Church pp. 137-139; Faith & Flame pp. 26-30; TMRE) --


def _tradition(tid: str):
    return catalog.load_tradition_catalog_by_id()[tid]


def test_the_franciscan_scripts():
    friars = _tradition("trad_franciscans")
    assert friars.realm == "Divine" and friars.virtues == ["vf_monastic_vows"]
    scripts = {s.name: s for s in friars.initiation.scripts}
    assert {n: (s.ease_factor, s.bonus) for n, s in scripts.items()} == {
        "Meditation": (21, 15),
        "Understanding": (21, 7),
        "Intervention": (21, 9),
        "Purity": (21, 9),
    }
    # Each Script's printed total is its Presence + Lore need + its bonus.
    assert 6 + scripts["Meditation"].bonus == 21
    # After Meditation's Major Ordeal, Understanding's Target is 12 (p. 138).
    target = mysteries.hedge_target(21, "Major", knows=True, reduction=9)
    assert target.total == 12 == 5 + scripts["Understanding"].bonus


def test_the_hermetic_cults_are_societates_with_their_printed_scripts():
    mercury = _tradition("trad_cult_of_mercury")
    priamitus = mercury.initiation.scripts[0]
    assert (priamitus.ease_factor, priamitus.bonus, priamitus.who) == (21, 18, "gifted")
    assert "Pagan" in priamitus.ordeal
    raven = _tradition("trad_legion_of_mithras").initiation.scripts[0]
    assert (raven.ease_factor, raven.bonus) == (15, 5)
    page = _tradition("trad_knights_of_the_green_stone").initiation.scripts[0]
    assert (page.ease_factor, page.bonus) == (15, 7)
    matres = _tradition("trad_matres_et_matrones")
    assert matres.initiation.scripts == [] and "Matrons need the Lore 6" in matres.notes
    for tid in (
        "trad_cult_of_mercury",
        "trad_legion_of_mithras",
        "trad_knights_of_the_green_stone",
        "trad_matres_et_matrones",
    ):
        assert _tradition(tid).hermetic == "societas"


def test_an_initiation_offers_the_scripts_of_a_cult_someone_belongs_to():
    lion = Character(
        id="l", name="Gaius", type="magus", traditions=["trad_legion_of_mithras"]
    )
    lion.characteristics.presence = 2
    lion.abilities = [Ability("Mystery Cult Lore: Legion of Mithras", xp=105)]  # 6
    raven = Character(id="r", name="Livia", type="magus")
    saga = Saga(id="s", name="S", characters=[lion, raven])
    keys = [key for _, key in ts.script_options(saga, raven)]
    assert "trad_legion_of_mithras/Raven: Strong-Willed" in keys
    tradition, script = ts.hedge_script("trad_legion_of_mithras/Raven: Strong-Willed")
    assert ts.initiation_total(lion, tradition, script.bonus) == 2 + 6 + 5
