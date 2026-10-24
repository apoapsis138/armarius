"""Hybrid magic: Holy and Chthonic Magic, Goetic Arts and Hermetic rites
changing a magus's Hermetic formulas."""

import random

from ars_magica_manager import catalog, seasons
from ars_magica_manager.casting_text import casting_scores_text
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    Characteristics,
    Covenant,
    Laboratory,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import casting, hedge_casting, lab, warping
from ars_magica_manager.rules import hybrid_magic as hybrid
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _magus(*abilities: tuple[str, int], vf_ids=(), kind="magus") -> Character:
    return Character(
        id="m",
        name="Magus",
        type=kind,
        covenant_id="c",
        characteristics=Characteristics(intelligence=3, stamina=2),
        arts={
            "creo": ArtScore(xp=art_xp(10)),
            "ignem": ArtScore(xp=art_xp(6)),
            "rego": ArtScore(xp=art_xp(9)),
            "vim": ArtScore(xp=art_xp(7)),
        },
        abilities=[
            Ability("Magic Theory", xp=ability_xp(5)),
            Ability("Artes Liberales", xp=ability_xp(1)),
            Ability("Philosophiae", xp=ability_xp(1)),
            *(Ability(name, xp=ability_xp(score)) for name, score in abilities),
        ],
        virtues_flaws=[VirtueFlawInstance(vf_id) for vf_id in vf_ids],
    )


def _saga(magus: Character, realm: str = "Magic", aura: int = 3):
    laboratory = Laboratory(id="l", covenant_id="c", name="Lab", owner_id="m")
    covenant = Covenant(id="c", saga_id="s", name="C", aura=aura, aura_realm=realm)
    saga = Saga(
        id="s",
        name="S",
        covenants=[covenant],
        characters=[magus],
        laboratories=[laboratory],
    )
    return saga, laboratory


def _terms(total) -> dict[str, float]:
    return {line.label: line.amount for line in total.lines if line.amount is not None}


def test_a_plain_magus_has_no_style():
    assert hybrid.styles(_magus()) == []
    assert hybrid.styles(_magus(("Holy Magic", 2), kind="companion")) == []


def test_holy_magic_stands_in_for_magic_theory_and_likes_divine_auras():
    magus = _magus(("Holy Magic", 2), vf_ids=["vf_holy_magic"])
    assert [s.name for s in hybrid.styles(magus)] == ["Holy Magic"]
    saga, laboratory = _saga(magus, realm="Divine", aura=3)
    terms = _terms(lab.lab_total(saga, magus, "Creo", "Ignem", laboratory))
    assert terms["Holy Magic (for Magic Theory)"] == 2
    assert "Magic Theory" not in terms
    assert terms["Aura (Divine 3), Holy Magic"] == 3  # not -9
    assert lab.vis_limit(magus) == 4
    # Infernal auras take nothing from it; Faerie ones give half.
    assert hybrid.aura_modifier(magus, "Infernal", 4) == (0, "Holy Magic")
    assert hybrid.aura_modifier(magus, "Faerie", 4) == (2, "")


def test_chthonic_magic_draws_on_infernal_auras():
    magus = _magus(("Chthonic Magic", 1), vf_ids=["vf_chthonic_magic"])
    score = casting.casting_score(magus, "Creo", "Ignem", aura=4, aura_realm="Infernal")
    assert _terms(score)["Aura (Infernal 4), Chthonic Magic"] == 4
    # Magic Theory is still his lab's.
    assert hybrid.theory(magus) == ("Magic Theory", 5)
    plain = casting.casting_score(
        _magus(), "Creo", "Ignem", aura=4, aura_realm="Infernal"
    )
    assert score.total - plain.total == 8


def test_a_ritual_adds_method_and_power_when_better():
    magus = _magus(
        ("Holy Magic", 1), ("Invocation", 3), ("Blessing", 2), ("Cursing", 1)
    )
    pair = hybrid.ritual_pair(magus)
    assert (pair.method, pair.power, pair.total) == ("Invocation", "Blessing", 5)
    score = casting.casting_score(magus, "Creo", "Ignem", ritual=True)
    terms = _terms(score)
    assert terms["Invocation + Blessing (Holy Magic)"] == 5
    assert "Artes Liberales" not in terms
    # A plain magus with the same Abilities keeps his Artes Liberales.
    plain = _magus(("Invocation", 3), ("Blessing", 2))
    assert "Artes Liberales" in _terms(
        casting.casting_score(plain, "Creo", "Ignem", ritual=True)
    )


def test_a_faerie_method_and_power_give_hermetic_rites():
    methods, powers = hybrid.methods_and_powers("Faerie")
    method, power = min(methods), min(powers)
    magus = _magus((method, 4), (power, 3))
    assert [s.name for s in hybrid.styles(magus)] == ["Hermetic rites"]
    # Rites change no aura: Hermetic magic's table still applies.
    assert hybrid.aura_modifier(magus, "Divine", 2) == (-6, "")
    assert hybrid.ritual_pair(magus).total == 7


def test_a_magus_may_use_rego_and_vim_for_a_goetic_art():
    tradition = catalog.load_tradition_catalog_by_id()["trad_witches_of_thessaly"]
    rule = tradition.casting[0]
    magus = _magus(("Summoning", 2), ("Infernal Lore", 1))
    terms = _terms(hedge_casting.casting_score(magus, tradition, rule, ("Summoning",)))
    assert terms["Rego (for Summoning)"] == 9
    assert terms["Vim (for Infernal Lore)"] == 7
    # Anyone else casts with the Art itself.
    witch = _magus(("Summoning", 2), ("Infernal Lore", 1), kind="companion")
    terms = _terms(hedge_casting.casting_score(witch, tradition, rule, ("Summoning",)))
    assert terms["Summoning"] == 2 and terms["Infernal Lore"] == 1


def test_no_warping_from_the_styles_realms():
    magus = _magus(("Holy Magic", 1))
    assert not hybrid.warps_from_aura(magus, "Divine")
    assert hybrid.warps_from_aura(magus, "Faerie")
    assert not hybrid.warps_from_aura(_magus(), "Magic")
    assert hybrid.warps_from_aura(_magus(), "Divine")
    saga, _ = _saga(magus, realm="Divine", aura=8)
    saga.current_season = "Winter"
    magus.background.year_born = 1180
    seasons.year_end_aging(saga, random.Random(0))
    assert warping.total_points(magus) == 0


def test_the_casting_scores_text_names_the_styles():
    magus = _magus(("Holy Magic", 1), ("Summoning", 1))
    saga, _ = _saga(magus)
    text = casting_scores_text(saga, magus)
    assert "Holy Magic: Holy Magic replaces Magic Theory" in text
    assert "Goetic magic: Rego may stand in" in text


def test_every_integration_breakthrough_grants_what_the_catalogs_have():
    from ars_magica_manager.forms import character as cf
    from ars_magica_manager.rules import experiment, integrations

    virtues = catalog.load_virtue_flaw_catalog_by_id()
    abilities = {a.name for a in catalog.load_ability_catalog()}
    for known in integrations.INTEGRATIONS:
        assert known.kind in experiment.KINDS
        if known.grant_kind == "Virtue":
            assert known.grant in virtues, known.name
        if known.grant_kind == "Ability":
            assert known.grant in abilities, known.name
    filled = cf._integration_fill({"known": "Canaanite Magic"})
    assert filled["target"] == 45 and filled["grant_virtue"] == "vf_canaanite_magic"
    goal = cf.research_goal_from(None, {**filled, "points": 0})
    assert (goal.kind, goal.grant_kind, goal.grant) == (
        "Major",
        "Virtue",
        "vf_canaanite_magic",
    )


def test_a_magus_in_a_hedge_tradition_keeps_twilight():
    from ars_magica_manager import tradition_text

    sol = catalog.load_tradition_catalog_by_id()["trad_sol_invictus"]
    text = tradition_text.warping_text(_magus(), sol)
    assert "Warping and Twilight as for any magus" in text


def test_faerie_magic_attunes_a_magus_to_faerie_auras():
    # DE p. 236: the full aura in both, no Warping from either, no extra
    # botch dice in either.
    merinita = _magus(vf_ids=("vf_faerie_magic",))
    plain = _magus()
    assert hybrid.FAERIE_MAGIC in hybrid.styles(merinita)
    assert hybrid.aura_modifier(merinita, "Faerie", 4)[0] == 4
    assert hybrid.aura_modifier(plain, "Faerie", 4)[0] == 2
    assert not hybrid.warps_from_aura(merinita, "Faerie")
    assert hybrid.warps_from_aura(plain, "Faerie")
    assert hybrid.foreign_botch_dice(merinita, "Faerie", 4) == 0
    assert hybrid.foreign_botch_dice(plain, "Faerie", 4) == 4
    assert casting.botch_dice(aura_realm="Faerie", aura=4, magus=merinita) == 1
    assert casting.botch_dice(aura_realm="Faerie", aura=4, magus=plain) == 5
    # A foreign regio level doubles them (DE p. 553).
    assert hybrid.foreign_botch_dice(plain, "Faerie", 4, in_regio=True) == 8


def test_anyone_is_at_home_where_their_powers_come_from():
    # DE p. 390: supernatural abilities from the aura's realm spare its
    # Warping, Hermetic or not.
    seer = _magus(("Second Sight", 2), kind="companion")
    seer.arts = {}
    assert hybrid.attuned(seer) == frozenset({"Magic"})
    assert not hybrid.warps_from_aura(seer, "Magic")
    holy = _magus(("Sense Holiness and Unholiness", 1), kind="companion")
    holy.arts = {}
    assert hybrid.attuned(holy) == frozenset({"Divine"})
    mundane = _magus(kind="grog")
    mundane.arts = {}
    assert hybrid.attuned(mundane) == frozenset()
    assert hybrid.warps_from_aura(mundane, "Magic")
    witch = _magus(kind="companion")
    witch.arts = {}
    infernal = next(
        t for t in catalog.load_tradition_catalog() if t.realm == "Infernal"
    )
    witch.traditions = [infernal.id]
    assert "Infernal" in hybrid.attuned(witch)
