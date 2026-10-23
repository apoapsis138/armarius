"""Character creation checks, step by step."""

from __future__ import annotations

from support import wait_until
from textual.widgets import Input, Static

from ars_magica_manager import catalog, storage
from ars_magica_manager.models import Character, Saga, VirtueFlawInstance
from ars_magica_manager.rules import creation as rules
from ars_magica_manager.rules import creation_character as cc
from ars_magica_manager.rules import creation_characteristics as cch
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import FieldsDialog, WorkspaceScreen
from ars_magica_manager.tui.screens.forms import _characteristics_dialog


def _saga() -> Saga:
    return Saga(id="s", name="S", current_year=1220)


def _character(type_: str = "magus", born: int | None = 1195, *vf_ids: str):
    character = Character(id="c", name="C", type=type_, in_creation=True)  # type: ignore[arg-type]
    character.background.year_born = born
    character.virtues_flaws = [VirtueFlawInstance(vf_id) for vf_id in vf_ids]
    return character


def _by_label(found):
    return {c.label: (c.status, c.detail) for c in found}


# -- Concept --


def test_a_magus_needs_the_gift_hermetic_magus_and_a_house():
    saga = _saga()
    magus = _character("magus", 1195, "vf_the_gift")
    found = _by_label(rules.checks(saga, magus, "concept"))
    assert found["Age is set"] == ("pass", "25")
    assert found["A magus has The Gift"] == ("pass", "taken")
    assert found["A magus has Hermetic Magus"] == ("warn", "missing")
    assert found["A magus belongs to a House"] == ("warn", "none chosen")
    assert cc.missing_type_virtues(magus) == ["vf_hermetic_magus"]
    magus.hermetic.house = "house_bonisagus"
    found = _by_label(rules.checks(saga, magus, "concept"))
    assert found["A magus belongs to a House"] == ("pass", "Bonisagus")


def test_an_unknown_age_is_a_broken_must():
    found = _by_label(rules.checks(_saga(), _character("grog", None), "concept"))
    assert found["Age is set"] == ("warn", "set Year Born")


def test_a_mythic_companion_has_one_status_virtue_no_gift_and_its_package():
    saga = _saga()
    mythic = _character("mythic companion", 1200, "vf_faerie_doctor", "vf_dowsing")
    found = _by_label(rules.checks(saga, mythic, "concept"))
    assert found["One Mythic Companion status Virtue"] == ("pass", "1 taken")
    assert found["The package includes Dowsing"] == ("pass", "taken")
    assert found["The package includes Curse-Throwing"] == ("advice", "missing")
    assert "A Mythic Companion has no Gift" not in found
    mythic.virtues_flaws.append(VirtueFlawInstance("vf_the_gift"))
    mythic.virtues_flaws.append(VirtueFlawInstance("vf_nephilim"))
    found = _by_label(rules.checks(saga, mythic, "concept"))
    assert found["One Mythic Companion status Virtue"] == ("warn", "2 taken")
    assert found["A Mythic Companion has no Gift"][0] == "warn"


def test_older_characters_get_advice_and_pre_play_aging():
    saga = _saga()
    companion = _character("companion", 1180)  # 40
    found = _by_label(rules.checks(saga, companion, "concept"))
    assert found["A companion should be under 30"] == ("advice", "11 year(s) too old")
    assert found["Older than 35: aging rolls before play"] == ("pass", "5 roll(s)")
    assert cc.pre_play_aging_rolls(saga, companion) == 5
    young = _by_label(rules.checks(saga, _character("companion", 1200), "concept"))
    assert "A companion should be under 30" not in young
    assert "Older than 35: aging rolls before play" not in young


# -- Virtues and Flaws --


def _vf(character, step="virtues_flaws"):
    return _by_label(rules.checks(_saga(), character, step))


def test_a_companions_virtues_balance_its_flaws():
    companion = _character(
        "companion", 1200, "vf_peasant", "vf_improved_characteristics"
    )
    found = _vf(companion)
    assert found["Virtue points balance Flaw points"] == (
        "warn",
        "1 Virtue, 0 Flaw points",
    )
    assert found["A Social Status"] == ("pass", "Peasant")
    companion.virtues_flaws.append(VirtueFlawInstance("vf_poor_eyesight"))
    found = _vf(companion)
    assert found["Virtue points balance Flaw points"][0] == "pass"


def test_a_magus_house_virtue_is_free():
    # Bonisagus gives Puissant Magic Theory or Puissant Intrigue.
    magus = _character("magus", 1195, "vf_the_gift", "vf_hermetic_magus")
    magus.hermetic.house = "house_bonisagus"
    label = "Virtue points balance Flaw points"
    found = _vf(magus)
    assert found[label] == ("pass", "0 Virtue, 0 Flaw points")
    assert found["The House's free Virtue is taken"][0] == "advice"
    magus.virtues_flaws.append(
        VirtueFlawInstance("vf_puissant_ability", params={"ability": "magic theory"})
    )
    found = _vf(magus)
    assert found[label] == (
        "pass",
        "1 Virtue, 0 Flaw points (free from the House: Puissant Magic Theory)",
    )
    assert "The House's free Virtue is taken" not in found
    # Another Minor Virtue isn't the House's: it has to be paid for.
    magus.virtues_flaws.append(VirtueFlawInstance("vf_improved_characteristics"))
    assert _vf(magus)[label][0] == "warn"
    magus.virtues_flaws.append(VirtueFlawInstance("vf_wealthy"))
    found = _vf(magus)
    assert found["Wealthy and Poor are for companions"] == ("warn", "Wealthy")
    assert found["A magus should have a Hermetic Flaw"] == ("advice", "0, 1 too few")


def test_jerbiton_and_ex_miscellanea_house_benefits():
    from ars_magica_manager.rules import creation_virtues as cv

    jerbiton = _character(
        "magus", 1195, "vf_the_gift", "vf_hermetic_magus", "vf_improved_characteristics"
    )
    jerbiton.hermetic.house = "house_jerbiton"
    assert cv.house_benefit(jerbiton).virtue_points == 1
    assert _vf(jerbiton)["Virtue points balance Flaw points"][0] == "pass"

    ex_misc = _character("magus", 1195, "vf_the_gift", "vf_hermetic_magus")
    ex_misc.hermetic.house = "house_ex_miscellanea"
    found = _vf(ex_misc)
    assert found["Ex Miscellanea's compulsory Flaw is taken"] == (
        "warn",
        "the compulsory Major Hermetic Flaw",
    )
    for vf_id in ("vf_hermetic_prestige", "vf_wealthy", "vf_chthonic_magic"):
        ex_misc.virtues_flaws.append(VirtueFlawInstance(vf_id))
    benefit = cv.house_benefit(ex_misc)
    # Hermetic Prestige (Minor Hermetic) and Wealthy (Major non-Hermetic)
    # are free; Chthonic Magic is a Major Hermetic Virtue, not the Flaw.
    assert (benefit.virtue_points, benefit.flaw_points) == (4, 0)


def test_free_house_virtue_counts_no_sheet_points():
    """The sheet's Virtue/Flaw points leave out the House's free
    Virtue (and Ex Miscellanea's compulsory Flaw), and mark them Free."""
    from ars_magica_manager import sheet_text as st
    from ars_magica_manager.rules import creation_virtues as cv

    jerbiton = _character(
        "magus", 1195, "vf_the_gift", "vf_hermetic_magus", "vf_improved_characteristics"
    )
    jerbiton.hermetic.house = "house_jerbiton"
    vfs = jerbiton.virtues_flaws
    free = cv.house_benefit(jerbiton).free_indices
    assert free == frozenset({2})
    assert st.vf_points(vfs, "Virtue") == 1
    assert st.vf_points(vfs, "Virtue", free) == 0
    assert [label for i, label in st.vf_rows(vfs, "Virtue", free) if i == 2] == [
        "Improved Characteristics (Minor, Free)"
    ]

    ex_misc = _character("magus", 1195, "vf_the_gift", "vf_hermetic_magus")
    ex_misc.hermetic.house = "house_ex_miscellanea"
    for vf_id in ("vf_hermetic_prestige", "vf_wealthy", "vf_chthonic_magic"):
        ex_misc.virtues_flaws.append(VirtueFlawInstance(vf_id))
    free = cv.house_benefit(ex_misc).free_indices
    # Hermetic Prestige and Wealthy are free; Chthonic Magic still costs 3.
    assert free == frozenset({2, 3})
    assert st.vf_points(ex_misc.virtues_flaws, "Virtue", free) == 3

    # Not a magus: nothing is free.
    jerbiton.type = "companion"
    assert cv.house_benefit(jerbiton).free_indices == frozenset()


def test_a_mystery_house_virtue_starts_its_ability_at_one():
    from ars_magica_manager.rules import creation_later as later

    magus = _character("magus", 1195, "vf_the_gift", "vf_hermetic_magus")
    magus.hermetic.house = "house_bjornaer"
    assert later.free_scores_missing(magus) == []
    magus.virtues_flaws.append(VirtueFlawInstance("vf_heartbeast"))
    assert later.free_scores_missing(magus) == ["Heartbeast"]


def test_flaw_point_and_minor_flaw_caps():
    flaws = (
        "vf_poor_eyesight",
        "vf_poor_hearing",
        "vf_poor_memory",
        "vf_poor_concentration",
        "vf_poor_student",
        "vf_pagan",
    )
    companion = _character("companion", 1200, "vf_peasant", *flaws)
    found = _vf(companion)
    assert found["At most 5 Minor Flaws"] == ("warn", "6, 1 too many")
    assert found["At most 10 Flaw points"] == ("pass", "6")
    grog = _character("grog", 1200, "vf_peasant", *flaws[:4], "vf_wealthy")
    found = _vf(grog)
    assert found["At most 3 Flaw points"] == ("warn", "4, 1 too many")
    assert found["A grog takes no Major Virtues or Flaws"] == ("warn", "1, 1 too many")


def test_status_personality_story_and_hermetic_limits():
    companion = _character(
        "companion",
        1200,
        "vf_peasant",
        "vf_covenfolk",
        "vf_ambitious_major",
        "vf_avaricious_major",
        "vf_pagan",
        "vf_faerie_friend",
        "vf_tragic_life",
        "vf_poor_formulaic_magic",
    )
    found = _vf(companion)
    assert found["One Social Status, unless they fit together"] == (
        "advice",
        "2 taken",
    )
    assert found["At most 1 Major Personality Flaw"] == ("warn", "2, 1 too many")
    assert found["At most 2 Personality Flaws"] == ("advice", "3, 1 too many")
    assert found["At most 1 Story Flaw"] == ("advice", "2, 1 too many")
    assert found["Hermetic Virtues and Flaws need The Gift"] == ("warn", "1 taken")
    # Tragic Life is Tainted: the Tainted caps show once any is taken.
    assert found["Tainted Flaws at most 5 points"] == ("pass", "3")
    grog = _character("grog", 1200, "vf_peasant", "vf_faerie_friend")
    assert _vf(grog)["A grog should have no Story Flaws"] == ("advice", "1, 1 too many")
    assert _vf(_character("grog", 1200))["A Social Status"] == ("warn", "none")


def test_a_mythic_companion_gets_two_virtue_points_per_flaw_point():
    mythic = _character(
        "mythic companion", 1200, "vf_peasant", "vf_poor_eyesight", "vf_wealthy"
    )
    found = _vf(mythic)
    # 1 Flaw point: 2 Virtue points plus the free Minor = 3.
    assert found["Virtue points: 2 per Flaw point, plus the free Minor"] == (
        "pass",
        "3 of 3",
    )
    assert "Virtue points spent" not in found
    mythic.virtues_flaws.append(VirtueFlawInstance("vf_improved_characteristics"))
    found = _vf(mythic)
    assert found["Virtue points: 2 per Flaw point, plus the free Minor"][0] == "warn"


# -- Characteristics --


def _scores(character, **scores):
    for key, value in scores.items():
        setattr(character.characteristics, key, value)
    return character


def test_characteristics_cost_seven_points_on_the_table():
    from ars_magica_manager.rules import creation_characteristics as cch

    assert [cch.cost(n) for n in (-3, -2, -1, 0, 1, 2, 3)] == [-6, -3, -1, 0, 1, 3, 6]
    grog = _scores(_character("grog", 1200), intelligence=3, strength=1)
    found = _vf(grog, "characteristics")
    assert found["Characteristics cost at most 7 points"] == ("pass", "7 spent")
    assert "Characteristic points spent" not in found
    _scores(grog, stamina=1)
    found = _vf(grog, "characteristics")
    assert found["Characteristics cost at most 7 points"] == (
        "warn",
        "8 spent, 1 too many",
    )
    _scores(grog, stamina=-1, strength=0)
    found = _vf(grog, "characteristics")
    assert found["Characteristic points spent"] == ("advice", "2 unspent")


def test_improved_characteristics_add_three_points_and_the_range_is_three():
    grog = _scores(_character("grog", 1200, "vf_improved_characteristics"), dexterity=4)
    found = _vf(grog, "characteristics")
    assert found["Characteristics cost at most 10 points"] == ("pass", "10 spent")
    assert found["Dexterity is bought from -3 to +3"] == ("warn", "+4 bought")


def test_great_characteristic_needs_three_then_one_a_copy():
    great = VirtueFlawInstance(
        "vf_great_characteristic", params={"characteristic": "strength"}
    )
    grog = _scores(_character("grog", 1200), strength=2)
    grog.virtues_flaws.append(great)
    found = _vf(grog, "characteristics")
    label = "Great Strength: Strength at +3, then +1 a copy"
    assert found[label] == ("warn", "+2, should be +4")
    _scores(grog, strength=4, intelligence=1)
    found = _vf(grog, "characteristics")
    assert found[label] == ("pass", "+4, should be +4")
    # +4 with Great costs what +3 does.
    assert found["Characteristics cost at most 7 points"] == ("pass", "7 spent")


def test_a_childs_scores_carry_the_age_modifier():
    # Age 10: -2 on every Characteristic, so -2 shown is 0 bought.
    child = _character("grog", 1210)
    for key in ("perception", "strength", "stamina", "presence"):
        _scores(child, **{key: -2})
    _scores(child, communication=-2, dexterity=-2, quickness=-2, intelligence=1)
    found = _vf(child, "characteristics")
    assert found["A child's Characteristics carry the age modifier"] == (
        "pass",
        "-2 on each (under 14)",
    )
    # Int +1 shown is +3 bought: 6 points.
    assert found["Characteristic points spent"] == ("advice", "1 unspent")


# -- Early Childhood --


def test_spending_creation_xp_adds_it_to_the_ability_and_taking_it_back_removes_it():
    from ars_magica_manager import creation
    from ars_magica_manager.models import CreationXp

    grog = _character("grog", 1200)
    entry = CreationXp("childhood", "Area Lore: Rhine", 15)
    creation.spend_creation_xp(grog, entry)
    assert [(a.name, a.category, a.xp) for a in grog.abilities] == [
        ("Area Lore: Rhine", "General", 15)
    ]
    creation.change_creation_xp(grog, entry, "Brawl", 5)
    assert [(a.name, a.xp) for a in grog.abilities] == [("Brawl", 5)]
    creation.refund_creation_xp(grog, entry)
    assert grog.abilities == [] and grog.creation_xp == []


def test_childhood_is_75_native_xp_and_45_from_the_list():
    from ars_magica_manager import creation
    from ars_magica_manager.models import CreationXp

    grog = _character("grog", 1200)
    found = _vf(grog, "childhood")
    assert found["75 xp in the Native Language"] == ("warn", "0 set")
    assert found["Childhood xp spent"] == ("advice", "45 unspent")
    for step_xp in (
        CreationXp("childhood", "Living Language: German", 75, "native"),
        CreationXp("childhood", "Brawl", 30),
        CreationXp("childhood", "Living Language: French", 5),
        CreationXp("childhood", "Living Language: Latin", 5),
        CreationXp("childhood", "Latin", 10),
    ):
        creation.spend_creation_xp(grog, step_xp)
    found = _vf(grog, "childhood")
    assert found["75 xp in the Native Language"] == (
        "pass",
        "Living Language: German",
    )
    assert found["At most 45 more xp"] == ("warn", "50 spent, 5 too many")
    assert found["Only the childhood Abilities"] == ("warn", "Latin")
    assert found["One second Living Language"][0] == "warn"
    assert (
        "Judaic Lore is for Jewish characters, unless the storyguide approves"
        not in found
    )
    creation.spend_creation_xp(grog, CreationXp("childhood", "Judaic Lore", 5))
    found = _vf(grog, "childhood")
    assert found[
        "Judaic Lore is for Jewish characters, unless the storyguide approves"
    ] == ("advice", "Judaic Lore taken")


def test_a_sample_childhood_fills_its_blanks():
    from ars_magica_manager.rules import creation_xp as cx

    traveling = next(c for c in cx.CHILDHOODS if c.name == "Traveling")
    assert cx.childhood_blanks(traveling) == ["area", "second_area", "language"]
    filled = cx.fill_childhood(
        traveling, {"area": "Rhine", "second_area": "Alps", "language": "French"}
    )
    assert filled[:2] == [("Area Lore: Rhine", 5), ("Area Lore: Alps", 5)]
    assert sum(xp for _, xp in filled) == 45
    assert all(
        sum(xp for _, xp in c.xp) == (120 if c.name == "Feral" else 45)
        for c in cx.CHILDHOODS
    )
    names = [
        c.name for c in cx.childhoods_in_play(Saga(id="s", name="S", books_in_play=[]))
    ]
    assert names == ["Athletic", "Exploring", "Mischievous", "Social", "Traveling"]


def test_the_grogs_childhoods_need_their_upbringing():
    from ars_magica_manager.rules import creation_xp as cx

    saga = Saga(id="s", name="S", books_in_play=["Grogs"])
    plain = Character(id="c", name="C", type="grog")
    names = [c.name for c in cx.childhoods_in_play(saga, plain)]
    assert "Covenant-bred" not in names and "Feral" not in names
    bred = Character(
        id="b",
        name="B",
        type="grog",
        virtues_flaws=[VirtueFlawInstance("vf_covenant_upbringing")],
    )
    assert "Covenant-bred" in [c.name for c in cx.childhoods_in_play(saga, bred)]
    # Covenant Upbringing opens Latin and Order of Hermes Lore to the childhood.
    assert cx.childhood_allows("Dead Language: Latin", bred)
    assert not cx.childhood_allows("Dead Language: Latin", plain)


def test_a_feral_child_has_no_language_and_120_childhood_xp():
    from ars_magica_manager.models import CreationXp
    from ars_magica_manager.rules import creation_xp as cx

    saga = Saga(id="s", name="S", books_in_play=["Grogs"])
    wild = Character(
        id="w",
        name="W",
        type="grog",
        virtues_flaws=[VirtueFlawInstance("vf_feral_upbringing")],
    )
    feral = next(c for c in cx.CHILDHOODS if c.name == "Feral")
    assert feral in cx.childhoods_in_play(saga, wild)
    assert cx.childhood_xp(wild) == 120
    assert "Living Language: {language}" not in cx.childhood_targets(wild)
    wild.creation_xp = [
        CreationXp("childhood", name, xp)
        for name, xp in cx.fill_childhood(feral, {"area": "Black Forest"})
    ]
    found = {c.label: c.status for c in cx.childhood_checks(saga, wild)}
    assert found["No Language (Feral Upbringing)"] == "pass"
    assert found["At most 120 more xp"] == "pass"
    assert "Only the childhood Abilities" not in found
    wild.creation_xp.append(
        CreationXp("childhood", "Living Language: German", 75, cx.NATIVE)
    )
    found = {c.label: c.status for c in cx.childhood_checks(saga, wild)}
    assert found["No Language (Feral Upbringing)"] == "warn"


# -- Later Life --


def test_later_life_is_15_xp_a_year_from_5_wealthy_20_poor_10():
    from ars_magica_manager.rules import creation_later as later

    saga = _saga()
    companion = _character("companion", 1195)  # 25: 20 years
    assert later.later_life_budget(saga, companion) == 300
    companion.virtues_flaws.append(VirtueFlawInstance("vf_wealthy"))
    assert later.later_life_budget(saga, companion) == 400
    magus = _character("magus", 1195)
    assert later.later_life_budget(saga, magus) == 75  # apprenticed at 10
    magus.hermetic.age_of_apprenticeship = 8
    assert later.later_life_budget(saga, magus) == 45


def test_later_life_buys_only_what_the_character_may_learn():
    from ars_magica_manager import creation
    from ars_magica_manager.models import CreationXp

    grog = _character("grog", 1195, "vf_warrior")
    for target, xp in (("Single Weapon", 30), ("Magic Theory", 5), ("Brawl", 15)):
        creation.spend_creation_xp(grog, CreationXp("later_life", target, xp))
    found = _vf(grog, "later_life")
    assert found["Only Abilities the character may learn"] == ("warn", "Magic Theory")
    assert found["Later Life xp: 20 years at 15"] == ("pass", "50 of 300")
    assert found["Later Life xp spent"] == ("advice", "250 unspent")
    assert found["Warrior: 50 xp"] == ("pass", "0 spent")
    assert found["Warrior xp spent"] == ("advice", "50 unspent")
    creation.spend_creation_xp(grog, CreationXp("virtue", "Brawl", 10, "vf_warrior"))
    found = _vf(grog, "later_life")
    assert found["Warrior xp only on what it names"] == ("warn", "Brawl")


def test_a_magus_gets_academic_abilities_only_from_apprenticeship():
    from ars_magica_manager.rules import creation_access as access

    magus = _character("magus", 1195)
    assert not access.may_learn(magus, "Magic Theory")
    assert access.may_learn(magus, "Magic Theory", apprenticed=True)
    assert "Magic Theory" not in access.learnable_abilities(magus)
    educated = _character("companion", 1195, "vf_educated")
    assert access.may_learn(educated, "Artes Liberales")
    assert not access.may_learn(educated, "Second Sight")


def test_free_supernatural_scores_and_the_ability_cap():
    from ars_magica_manager import creation
    from ars_magica_manager.models import CreationXp
    from ars_magica_manager.rules import creation_later as later

    companion = _character("companion", 1195, "vf_second_sight")
    assert later.free_scores_missing(companion) == ["Second Sight"]
    found = _vf(companion, "later_life")
    assert found["Free Ability scores from Virtues recorded"] == (
        "advice",
        "Second Sight",
    )
    creation.spend_creation_xp(companion, CreationXp("free", "Second Sight", 5))
    assert later.free_scores_missing(companion) == []
    creation.spend_creation_xp(companion, CreationXp("later_life", "Brawl", 105))
    found = _vf(companion, "later_life")
    assert found["No Ability above 5 at creation"] == ("warn", "Brawl")


def test_the_sheet_says_how_much_xp_came_from_the_worksheet():
    from ars_magica_manager import creation
    from ars_magica_manager.models import CreationXp

    magus = _character("magus", 1195)
    magus.virtues_flaws = [VirtueFlawInstance("vf_affinity_with_art", {"art": "creo"})]
    creation.spend_creation_xp(magus, CreationXp("apprenticeship", "Creo", 10))
    creation.spend_creation_xp(magus, CreationXp("later_life", "Brawl", 5))
    assert creation.worksheet_note(magus, ["Creo", "Brawl", "Ignem"]) == (
        "From the Creation Worksheet: Creo 15 xp (10 spent x1.5), Brawl 5 xp "
        "(5 spent). Take worksheet xp back on the worksheet, not here."
    )
    assert creation.spend_preview(magus, "Creo", 4, magus.creation_xp[0]) == (6, 6)
    magus.in_creation = False
    assert creation.worksheet_note(magus, ["Creo"]) == ""


def test_an_affinity_raises_its_abilitys_cap_and_mentored_by_demons_lifts_it():
    from ars_magica_manager import creation
    from ars_magica_manager.models import CreationXp

    companion = _character("companion", 1195)
    companion.virtues_flaws = [
        VirtueFlawInstance("vf_affinity_with_ability", {"ability": "brawl"})
    ]
    label = "No Ability above 5 at creation (2 more with an Affinity)"
    # 94 spent gives 141 xp: Brawl 7, the cap with its Affinity.
    creation.spend_creation_xp(companion, CreationXp("later_life", "Brawl", 94))
    creation.spend_creation_xp(companion, CreationXp("later_life", "Awareness", 105))
    assert _vf(companion, "later_life")[label] == ("warn", "Awareness")
    creation.spend_creation_xp(companion, CreationXp("later_life", "Brawl", 30))
    assert _vf(companion, "later_life")[label] == (
        "warn",
        "Awareness, Brawl (cap 7)",
    )
    companion.virtues_flaws.append(VirtueFlawInstance("vf_mentored_by_demons"))
    found = _vf(companion, "later_life")
    assert found["No Ability cap at creation (Mentored by Demons)"][0] == "pass"


# -- Grogs training packages --


def test_training_packages_take_later_life_years():
    from ars_magica_manager import creation
    from ars_magica_manager.models import CreationXp
    from ars_magica_manager.rules import creation_later as later
    from ars_magica_manager.rules import creation_packages as packages

    saga = _saga()
    grog = _character("grog", 1195)  # 20 Later Life years
    soldier = next(p for p in packages.PACKAGES if p.name == "Soldier")
    note = packages.Taken("Soldier", 5, 1).note
    for target, xp in packages.package_xp(soldier, 5):
        creation.spend_creation_xp(grog, CreationXp("package", target, xp, note))
    assert later.bought_years(saga, grog) == 15
    assert later.later_life_budget(saga, grog) == 225
    found = _vf(grog, "later_life")
    assert found["Training packages fit in Later Life"] == ("pass", "5 of 20 years")
    assert found["Soldier needs a Virtue opening Martial Abilities"] == (
        "warn",
        "not opened",
    )
    grog.virtues_flaws.append(VirtueFlawInstance("vf_wealthy"))
    assert packages.years_used(grog) == 4  # 5 x 3/4, rounded up


def test_an_affinity_adds_half_again_and_15_years_is_the_most():
    from ars_magica_manager import creation
    from ars_magica_manager.models import CreationXp
    from ars_magica_manager.rules import creation_packages as packages

    grog = _character("grog", 1180)
    grog.virtues_flaws.append(
        VirtueFlawInstance("vf_affinity_with_ability", params={"ability": "brawl"})
    )
    brawler = next(p for p in packages.PACKAGES if p.name == "Brawler")
    note = packages.Taken("Brawler", 3, 1).note
    for target, xp in packages.package_xp(brawler, 3):
        creation.spend_creation_xp(grog, CreationXp("package", target, xp, note))
    assert next(a.xp for a in grog.abilities if a.name == "Brawl") == 45
    grog.creation_xp.clear()
    for time in range(1, 7):
        note = packages.Taken("Brawler", 3, time).note
        creation.spend_creation_xp(grog, CreationXp("package", "Brawl", 1, note))
    found = _vf(grog, "later_life")
    assert found["At most 15 years in Brawler"] == ("warn", "18 years")


def test_every_package_is_15_xp_a_year_and_failed_apprentice_needs_its_virtue():
    from ars_magica_manager import creation
    from ars_magica_manager.models import CreationXp
    from ars_magica_manager.rules import creation_packages as packages

    for package in packages.PACKAGES:
        for years, rows in ((5, package.five), (3, package.three)):
            # Natural Philosopher's formulae stand for the rest of its xp.
            if rows and package.name != "Natural Philosopher":
                assert sum(xp for _, xp in rows) == 15 * years, package.name
    failed = next(p for p in packages.PACKAGES if p.name == "Failed Apprentice")
    assert packages.package_label(failed, 3).startswith("Failed Apprentice, 3 years")
    philosopher = next(p for p in packages.PACKAGES if p.name == "Natural Philosopher")
    assert packages.package_label(philosopher, 5).endswith("7 formulae")
    grog = _character("grog", 1190)
    note = packages.Taken("Failed Apprentice", 3, 1).note
    for target, xp in packages.package_xp(failed, 3):
        creation.spend_creation_xp(grog, CreationXp("package", target, xp, note))
    found = _vf(grog, "later_life")
    assert found["Failed Apprentice needs the Failed Apprentice Virtue"] == (
        "warn",
        "not taken",
    )
    grog.virtues_flaws.append(VirtueFlawInstance("vf_failed_apprentice"))
    found = _vf(grog, "later_life")
    assert found["Failed Apprentice needs the Failed Apprentice Virtue"] == (
        "pass",
        "taken",
    )


# -- Apprenticeship --


def _magus_with(**arts):
    from ars_magica_manager.models import Ability, ArtScore

    magus = _character("magus", 1195, "vf_the_gift", "vf_hermetic_magus")
    for art, xp in arts.items():
        magus.arts[art] = ArtScore(xp)
    magus.characteristics.intelligence = 2
    magus.abilities.append(Ability("Magic Theory", "Arcane", 30))  # 3
    return magus


def test_a_spells_creation_cap_is_the_lab_total_with_aura_3():
    from ars_magica_manager.rules import creation_magus as magus_rules

    saga = _saga()
    magus = _magus_with(creo=15, ignem=21)  # Creo 5, Ignem 6
    pilum = catalog.find_spell(saga, "spell_pilum_of_fire")
    assert pilum is not None
    # 5 + 6 + Int 2 + Magic Theory 3 + aura 3.
    assert magus_rules.spell_cap(saga, magus, pilum) == 19


def test_apprenticeship_budget_spells_and_the_gauntlet_minimums():
    from ars_magica_manager import creation
    from ars_magica_manager.models import CreationXp

    magus = _magus_with(creo=15, ignem=21)
    creation.spend_creation_xp(magus, CreationXp("apprenticeship", "Creo", 100))
    creation.learn_creation_spell(
        magus, "apprenticeship_spells", "spell_pilum_of_fire", 20
    )
    found = _vf(magus, "apprenticeship")
    assert found["Apprenticeship xp: 240"] == ("pass", "100 spent")
    assert found["Spell levels: 120"] == ("pass", "20 learned")
    assert found["Pilum of Fire at most the Lab Total"][0] == "pass"  # Creo now 115
    assert found["Parma Magica at least 1"] == ("warn", "0")
    assert found["Magic Theory at least 1"] == ("pass", "3")
    assert found["Latin at least 1"] == ("warn", "0")
    assert found["Latin should be 4 to read the Order's books"] == (
        "advice",
        "0, 4 too few",
    )
    assert [k.spell_id for k in magus.spells_known] == ["spell_pilum_of_fire"]
    creation.forget_creation_spell(magus, magus.creation_xp[-1])
    assert magus.spells_known == []


def test_an_affinity_with_an_art_adds_half_again_rounded_up():
    from ars_magica_manager import creation
    from ars_magica_manager.models import CreationXp

    magus = _magus_with()
    magus.virtues_flaws.append(
        VirtueFlawInstance("vf_affinity_with_art", params={"art": "perdo"})
    )
    entry = CreationXp("apprenticeship", "Perdo", 37)
    creation.spend_creation_xp(magus, entry)
    assert magus.arts["perdo"].xp == 56
    creation.refund_creation_xp(magus, entry)
    assert magus.arts["perdo"].xp == 0


# -- Years past Gauntlet and pre-play aging --


def test_years_past_gauntlet_give_30_points_less_lab_seasons():
    from ars_magica_manager.rules import creation_magus as magus_rules

    saga = _saga()
    magus = _character("magus", 1185)  # 35: Gauntlet at 25, 10 years
    assert magus_rules.years_past_gauntlet(saga, magus) == 10
    assert magus_rules.gauntlet_points(saga, magus) == 300
    assert [magus_rules.lab_season_cost(n) for n in (1, 2, 3, 4, 5, 8)] == [
        10,
        20,
        30,
        30,
        40,
        60,
    ]
    magus.creation_conditions.lab_seasons = 5
    assert magus_rules.gauntlet_points(saga, magus) == 260
    magus.creation_conditions.lab_seasons = 41
    found = _vf(magus, "gauntlet")
    assert found["Lab seasons fit in the years past Gauntlet"] == ("warn", "41 of 40")


def test_pre_play_aging_rolls_each_year_from_35_once():
    import random

    from ars_magica_manager import creation
    from ars_magica_manager.rules import creation_magus as magus_rules

    saga = _saga()
    companion = _character("companion", 1180)  # 40: rolls at 35..39
    assert magus_rules.aging_due(saga, companion) == 5
    assert _vf(companion, "finish")["Pre-play aging rolled"] == (
        "warn",
        "5 roll(s) to make",
    )
    summaries = creation.pre_play_aging(saga, companion, random.Random(1))
    assert [s.split(":")[0] for s in summaries] == ["35", "36", "37", "38", "39"]
    assert [e.name.split(":")[0] for e in companion.diary] == [
        f"Pre-play aging at {age}" for age in range(35, 40)
    ]
    assert {(e.season, e.year) for e in companion.diary} >= {("Winter", 1215)}
    assert magus_rules.aging_due(saga, companion) == 0
    assert _vf(companion, "finish")["Pre-play aging rolled"] == ("pass", "done")
    assert creation.pre_play_aging(saga, companion, random.Random(1)) == []


# -- Finishing Touches --


def test_traits_confidence_and_reputations_at_the_end():
    from ars_magica_manager.models import Ability, ScoredTrait

    grog = _character("grog", 1195)
    grog.abilities.append(Ability("Single Weapon", "Martial", 15))
    grog.personality_traits = [ScoredTrait("Brave", 2), ScoredTrait("Greedy", 5)]
    grog.background.confidence_score = 1
    found = _vf(grog, "finish")
    assert found["A grog has Loyal"] == ("warn", "missing")
    assert found["A warrior has Brave"] == ("pass", "taken")
    assert found["Greedy past 3 only from a Personality Flaw"] == ("advice", "+5")
    assert found["A grog has no Confidence"] == ("warn", "1, 0 points")
    companion = _character("companion", 1200, "vf_self_confident")
    companion.reputations = [ScoredTrait("Brave Knight", 2)]
    found = _vf(companion, "finish")
    assert found["A few Personality Traits"] == (
        "advice",
        "0, pick some (a third is suggested)",
    )
    assert found["Confidence Score 2, 5 Confidence Points"][0] == "warn"
    assert found["Reputations come only from Virtues and Flaws"] == (
        "advice",
        "no Virtue or Flaw gives one",
    )


# -- live points on the Characteristics form --


def test_points_text_follows_the_scores_being_typed():
    saga = Saga(id="test_saga", name="S")
    character = Character(id="c1", name="Ana", type="companion", in_creation=True)
    saga.characters.append(character)
    blank = dict.fromkeys((key for key, _ in cch.CHARACTERISTICS), 0)
    assert cch.points_text(saga, character, blank).splitlines() == [
        "[b]Points:[/] 0 of 7 spent, 7 left",
        "[b]Cost:[/] Int 0  Per 0  Str 0  Sta 0  Pre 0  Com 0  Dex 0  Qik 0",
    ]
    # +3 costs 6, +1 costs 1, -2 gives 3 back; a blank field counts as 0.
    typed = {
        **blank,
        "intelligence": 3,
        "stamina": 1,
        "quickness": -2,
        "presence": None,
    }
    assert cch.points_text(saga, character, typed).splitlines() == [
        "[b]Points:[/] 4 of 7 spent, 3 left",
        "[b]Cost:[/] Int +6  Per 0  Str 0  Sta +1  Pre 0  Com 0  Dex 0  Qik -3",
    ]
    exact = {**blank, "intelligence": 3, "stamina": 1}
    assert "[$text-success]7 of 7 spent[/]" in cch.points_text(saga, character, exact)
    over = {**blank, "intelligence": 4}
    lines = cch.points_text(saga, character, over).splitlines()
    assert lines[0] == "[b]Points:[/] [$text-error]10 of 7 spent, 3 too many[/]"
    assert lines[2].startswith("[$text-warning]☞ Intelligence: bought from -3 to +3")
    # The sheet's own scores are untouched by what is typed.
    assert character.characteristics.intelligence == 0


async def test_the_characteristics_form_shows_points_as_they_are_typed():
    saga = Saga(id="test_saga", name="S")
    creating = Character(id="c1", name="Ana", type="companion", in_creation=True)
    playing = Character(id="c2", name="Bo", type="companion")
    saga.characters += [creating, playing]
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        workspace = app.screen

        def live() -> str:
            # "" until the dialog has composed.
            found = app.screen.query("#fields-live")
            return str(found.first(Static).render()) if found else ""

        workspace.app.push_screen(_characteristics_dialog(workspace.saga, creating))
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        assert await wait_until(pilot, lambda: "0 of 7 spent, 7 left" in live())
        app.screen.query_one("#fld-intelligence", Input).value = "3"
        assert await wait_until(pilot, lambda: "6 of 7 spent, 1 left" in live())
        app.screen.query_one("#fld-strength", Input).value = "2"
        assert await wait_until(pilot, lambda: "9 of 7 spent, 2 too many" in live())
        assert "Str +3" in live()
        # Fits the screen with the live lines showing.
        region = app.screen.query_one("#fields-dialog").region
        assert region.bottom <= 45 and region.right <= 120
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is workspace)
        # A character In Play has no budget to show.
        workspace.app.push_screen(_characteristics_dialog(workspace.saga, playing))
        assert await wait_until(pilot, lambda: bool(app.screen.query("#fld-strength")))
        assert isinstance(app.screen, FieldsDialog)
        assert not app.screen.query("#fields-live")
