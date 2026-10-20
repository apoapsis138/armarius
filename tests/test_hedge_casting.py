"""Hedge casting totals, Penetration and Magical Defenses."""

from ars_magica_manager import catalog, tradition_text
from ars_magica_manager.models import (
    Ability,
    CastingRule,
    Character,
    GroupCasting,
    Saga,
    TraditionDef,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import creation_access as access
from ars_magica_manager.rules import creation_tradition as ct
from ars_magica_manager.rules import hedge_casting as hc
from ars_magica_manager.rules.xp import xp_for_score


def _tradition(tradition_id: str) -> TraditionDef:
    return catalog.load_tradition_catalog_by_id()[tradition_id]


def _member(tradition_id: str, *vf_ids: str) -> Character:
    """A Gifted member, Opened: the tradition's Arts at 0."""
    character = Character(id="c", name="Hild", type="companion")
    character.traditions = [tradition_id]
    character.virtues_flaws = [VirtueFlawInstance(v) for v in ("vf_the_gift", *vf_ids)]
    ct.open_tradition(character)
    return character


def _set(character: Character, name: str, score: int) -> None:
    factor = 1 if _is_art(name) else 5
    ability = next((a for a in character.abilities if a.name == name), None)
    if ability is None:
        ability = Ability(name=name, xp=0)
        character.abilities.append(ability)
    ability.xp = xp_for_score(score, factor)


def _is_art(name: str) -> bool:
    return access.ability_xp_table(name) == "art"


def _rule(tradition: TraditionDef, name: str) -> CastingRule:
    return next(r for r in tradition.casting if r.name == name)


def test_a_gruagach_formulaic_score_adds_both_arts_and_stamina():
    gruagach = _tradition("trad_gruagachan")
    c = _member("trad_gruagachan")
    c.characteristics.stamina = 2
    _set(c, "Gruagach Give", 6)
    _set(c, "Gruagach Curse", 9)
    rule = _rule(gruagach, "Formulaic spell")
    score = hc.casting_score(
        c, gruagach, rule, ("Gruagach Give", "Gruagach Curse"), aura=3
    )
    assert score.total == 6 + 9 + 2 + 3
    assert [line.label for line in score.lines][:3] == [
        "Gruagach Give",
        "Gruagach Curse",
        "Stamina",
    ]
    # Up to 10 short still casts, for a Fatigue level.
    assert hc.outcome(rule, 15, 25) == hc.Outcome(True, True)
    assert hc.outcome(rule, 14, 25) == hc.Outcome(False, True)
    assert hc.outcome(rule, 25, 25) == hc.Outcome(True, False)


def test_spontaneous_and_text_charms_divide_the_total():
    gruagach = _tradition("trad_gruagachan")
    assert hc.casting_total(_rule(gruagach, "Spontaneous spell"), 15, 6) == 10
    learned = _tradition("trad_learned_magicians")
    assert hc.casting_total(_rule(learned, "Known charm"), 15, 4) == 9
    assert hc.casting_total(_rule(learned, "Charm from a text"), 15, 6) == 4


def test_a_lab_total_adds_no_die():
    vitkir = _tradition("trad_vitkir")
    rule = _rule(vitkir, "Vitkar Lab Total")
    assert hc.casting_total(rule, 20, 9) == 20


def test_a_rune_script_uses_its_lowest_rune():
    vitkir = _tradition("trad_vitkir")
    c = _member("trad_vitkir")
    c.characteristics.stamina = 1
    _set(c, "Gebo", 8)
    _set(c, "Ansuz", 3)
    rule = _rule(vitkir, "Rune script")
    score = hc.casting_score(c, vitkir, rule, ("Gebo", "Ansuz"))
    assert score.total == 3 + 1
    assert score.lines[0].label == "Ansuz (lowest rune)"
    assert hc.vis_cap(c, vitkir, rule, ("Gebo", "Ansuz")) == 3


def test_a_folk_witch_casts_each_ability_with_its_characteristic():
    witches = _tradition("trad_folk_witches")
    c = _member("trad_folk_witches")
    c.characteristics.dexterity = 2
    _set(c, "Cursing", 4)
    rule = witches.casting[0]
    score = hc.casting_score(c, witches, rule, ("Cursing",))
    assert score.total == 4 + 2
    assert hc.equivalent_level(rule, 4) == 20
    # An Ability's effect must reach its Ease Factor: no margin.
    assert hc.outcome(rule, 8, 9) == hc.Outcome(False, False)
    assert hc.vis_cap(c, witches, rule, ("Cursing",)) == 4
    ungifted = Character(id="u", name="U", type="companion")
    ungifted.abilities = [Ability(name="Cursing", xp=50)]
    assert hc.vis_cap(ungifted, witches, rule, ("Cursing",)) == 0


def test_an_elementalists_vis_is_capped_by_all_four_forms():
    elementalists = _tradition("trad_elementalists")
    c = _member("trad_elementalists")
    for form, value in (("Air", 2), ("Earth", 3), ("Fire", 1), ("Water", 4)):
        _set(c, f"Elementalist {form}", value)
    _set(c, "Elementalist Summoning", 5)
    rule = elementalists.casting[0]
    assert hc.vis_cap(c, elementalists, rule, ("Elementalist Summoning",)) == 10
    labels = [x.label for x in hc.castings(c, elementalists, rule)]
    assert labels == [
        "Summoning Air",
        "Summoning Earth",
        "Summoning Fire",
        "Summoning Water",
    ]


def test_the_aura_counts_for_the_traditions_realm():
    gruagach = _tradition("trad_gruagachan")
    rule = _rule(gruagach, "Formulaic spell")
    c = _member("trad_gruagachan")
    divine = hc.casting_score(
        c,
        gruagach,
        rule,
        ("Gruagach Give", "Gruagach Curse"),
        aura=3,
        aura_realm="Divine",
    )
    assert divine.total == -9


def test_magical_defenses_bonus_and_doubling():
    gruagach = _tradition("trad_gruagachan")
    c = _member("trad_gruagachan")
    _set(c, "Gruagach Shape", 11)
    rows = {r.source: r for r in hc.magical_defenses(c, gruagach)}
    shape = rows["Gruagach Shape"]
    assert (shape.kind, shape.bonus) == ("Strength of Form", 3)
    assert "Stamina + 3" in shape.effect
    c.virtues_flaws.append(VirtueFlawInstance("vf_greater_magical_defenses"))
    rows = {r.source: r for r in hc.magical_defenses(c, gruagach)}
    assert rows["Gruagach Shape"].bonus == 6
    c.virtues_flaws.append(VirtueFlawInstance("vf_no_magical_defenses"))
    assert hc.magical_defenses(c, gruagach) == []


def test_an_ability_defense_is_its_score_and_only_the_best_counts():
    witches = _tradition("trad_folk_witches")
    c = _member("trad_folk_witches")
    _set(c, "Animal Ken", 2)
    _set(c, "Healing", 4)
    rows = hc.magical_defenses(c, witches)
    best = hc.best_defense(rows, "Magical Fortitude")
    assert best is not None and (best.source, best.bonus) == ("Healing", 4)


def test_dispelling_and_group_casting():
    gruagach = _tradition("trad_gruagachan")
    another = next(r for r in gruagach.dispels if r.multiple == 2)
    assert hc.dispel_needs(another, 15) == 30
    assert hc.dispels(another, 30, 15)
    assert hc.ability_effect_level(3) == 15
    sabbat = _tradition("trad_folk_witches").groups[0]
    assert hc.group_bonus(sabbat, [1, 1, 1, 1, 1], aura=3) == 3
    ceremony = GroupCasting(name="Ceremony")
    assert hc.group_bonus(ceremony, [4, 6, 2], leader_ceremony=2) == 10
    assert hc.leaderless_modifier([2, 1, 0]) == 0


def test_the_chapter_text_shows_the_scores_and_defenses():
    saga = Saga(id="s", name="S")
    gruagach = _tradition("trad_gruagachan")
    c = _member("trad_gruagachan")
    c.characteristics.stamina = 1
    _set(c, "Gruagach Give", 5)
    text = tradition_text.casting_text(saga, c, gruagach)
    assert "Formulaic spell" in text
    assert "Give" in text and "Vision" in text
    assert "up to 10 short" in text
    assert "Take Curse" in text
    defenses = tradition_text.defenses_text(c, gruagach)
    assert "Magical Fortitude" in defenses
    assert "+1 from Gruagach Give" in defenses
    vitkir = _tradition("trad_vitkir")
    assert "no Magical Defenses" in tradition_text.defenses_text(c, vitkir)
