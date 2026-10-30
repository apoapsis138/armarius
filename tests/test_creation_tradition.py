"""Creating a hedge tradition's member: the Tradition Training step."""

from support import offer_only

from ars_magica_manager import creation, worksheet
from ars_magica_manager.forms import worksheet as wf
from ars_magica_manager.models import Character, CreationXp, Saga, VirtueFlawInstance
from ars_magica_manager.rules import creation as rules
from ars_magica_manager.rules import creation_access as access
from ars_magica_manager.rules import creation_tradition as ct
from ars_magica_manager.rules import creation_virtues as cv


def _saga(*offered: str) -> Saga:
    return offer_only(Saga(id="s", name="S"), *offered)


def _member(tradition: str, *vf_ids: str, kind: str = "companion") -> Character:
    character = Character(id="c", name="Hild", type=kind)
    character.traditions = [tradition]
    character.in_creation = True
    character.virtues_flaws = [VirtueFlawInstance(v) for v in vf_ids]
    return character


def _checks(saga: Saga, character: Character) -> dict[str, str]:
    return {
        c.label: c.status for c in rules.checks(saga, character) if c.step == "training"
    }


def test_a_gifted_vitki_trains_and_is_opened():
    saga = _saga("trad_vitkir")
    vitki = _member("trad_vitkir", "vf_the_gift")
    assert "training" in [s.key for s in rules.steps_for(vitki)]
    assert (ct.xp_budget(vitki), ct.level_budget(vitki)) == (290, 120)
    wf.add_tradition_virtues(vitki).apply()
    assert {vf.vf_id for vf in vitki.virtues_flaws} >= {"vf_vitki"}
    assert len(ct.unopened(vitki)) == 24
    wf.open_tradition(vitki).apply()
    fehu = next(a for a in vitki.abilities if a.name == "Fehu")
    assert (fehu.xp, fehu.xp_table) == (0, "art")
    assert "Fehu" in ct.targets(vitki)
    checks = _checks(saga, vitki)
    assert checks["The Opening's Arts and Abilities given"] == "pass"
    assert checks["Rune Magic at least 1"] == "warn"
    assert checks["At least 120 xp on the tradition's Arts"] == "warn"


def test_runes_have_the_tradition_cap_not_the_age_cap():
    vitki = _member("trad_vitkir", "vf_the_gift")
    assert access.ability_cap_for(vitki, 25, "Fehu") == 10
    assert access.ability_cap_for(vitki, 25, "Brawl") is not None


def test_spending_the_apprenticeship_and_the_rune_cap():
    saga = _saga("trad_vitkir")
    vitki = _member("trad_vitkir", "vf_the_gift", "vf_vitki")
    wf.open_tradition(vitki).apply()
    creation.spend_creation_xp(vitki, CreationXp("training", "Fehu", 66))  # 11
    creation.spend_creation_xp(vitki, CreationXp("training", "Uruz", 55))
    checks = _checks(saga, vitki)
    assert checks["At least 120 xp on the tradition's Arts"] == "pass"
    assert checks["No Art above 10 at creation"] == "warn"
    assert checks["Apprenticeship xp: 290"] == "pass"


def test_an_ungifted_vitki_is_told_to_take_the_gift():
    saga = _saga("trad_vitkir")
    found = rules.checks(saga, _member("trad_vitkir", "vf_vitki"))
    gift = next(c for c in found if c.label == "A Vitkir member has The Gift")
    assert (gift.step, gift.status) == ("concept", "warn")


def test_well_and_poorly_trained_change_the_apprenticeship():
    gruagach = _member(
        "trad_gruagachan", "vf_well_trained_gruagach", "vf_well_trained_gruagach"
    )
    assert (ct.xp_budget(gruagach), ct.level_budget(gruagach)) == (164, 82)
    gifted = _member("trad_gruagachan", "vf_the_gift", "vf_poorly_trained_gruagach")
    assert (ct.xp_budget(gifted), ct.level_budget(gifted)) == (110, 55)


def test_a_nightwalker_has_no_training_step():
    nightwalker = _member("trad_nightwalkers", "vf_nightwalker")
    assert "training" not in [s.key for s in rules.steps_for(nightwalker)]
    assert ct.missing_virtues(nightwalker) == ["vf_nightwalker_tradition"]


def test_the_opening_gives_free_virtues_outside_the_balance():
    magician = _member("trad_learned_magicians", "vf_the_gift", "vf_entreat_the_powers")
    benefit = cv.free_benefit(magician)
    assert benefit.virtue_points == 3
    assert benefit.giver == "the tradition"
    assert cv.virtue_allowance(magician, 0) == (3, 3)


def test_a_vitki_takes_one_free_minor_supernatural_virtue():
    vitki = _member("trad_vitkir", "vf_the_gift", "vf_vitki")
    assert cv.free_benefit(vitki).missing == (
        "a Minor Supernatural Virtue from the master",
    )
    vitki.virtues_flaws.append(VirtueFlawInstance("vf_fast_caster_runes"))
    assert cv.free_benefit(vitki).virtue_points == 1


def test_the_worksheet_offers_the_tradition_on_concept():
    saga = _saga("trad_folk_witches")
    witch = Character(id="c", name="Agnes", type="companion")
    labels = [
        a.label for a in worksheet.panel_for(witch, "concept").actions(saga, witch)
    ]
    assert "Choose tradition" in labels
    choose = wf.choose_tradition(saga, witch)
    (choice,) = choose.choices()
    choose.apply(choice.value)
    assert witch.traditions == ["trad_folk_witches"]
    assert "vf_folk_witch" in {vf.vf_id for vf in witch.virtues_flaws}


def test_a_saga_offering_no_tradition_offers_nothing():
    saga = _saga()
    companion = Character(id="c", name="A", type="companion")
    labels = [
        a.label
        for a in worksheet.panel_for(companion, "concept").actions(saga, companion)
    ]
    assert "Choose tradition" not in labels
    assert "training" not in [s.key for s in rules.steps_for(companion)]


def _ex_misc(*vf_ids: str) -> Character:
    magus = _member("trad_tempestaria", "vf_the_gift", *vf_ids, kind="magus")
    magus.hermetic.house = "house_ex_miscellanea"
    return magus


def test_a_magus_of_ex_miscellanea_chooses_his_houses_tradition():
    saga = _saga("trad_tempestaria", "trad_sol_invictus", "trad_folk_witches")
    magus = Character(id="m", name="Ulla", type="magus")
    magus.hermetic.house = "house_ex_miscellanea"
    labels = [
        a.label for a in worksheet.panel_for(magus, "concept").actions(saga, magus)
    ]
    assert "Choose tradition" in labels
    choose = wf.choose_tradition(saga, magus)
    assert [c.value for c in choose.choices()] == [
        "trad_sol_invictus",
        "trad_tempestaria",
    ]
    choose.apply("trad_tempestaria")
    assert magus.traditions == ["trad_tempestaria"]
    held = {vf.vf_id for vf in magus.virtues_flaws}
    assert {
        "vf_whistle_up_the_wind",
        "vf_affinity_with_art",
        "vf_necessary_condition",
    } <= held
    # A magus of another House may join only a Hermetic society.
    other = Character(id="o", name="Odo", type="magus")
    other.hermetic.house = "house_bonisagus"
    assert [t.id for t in wf.traditions.joinable(saga, other)] == ["trad_sol_invictus"]


def test_the_ex_miscellanea_package_is_the_traditions_virtues():
    magus = _ex_misc()
    assert cv.house_benefit(magus).missing == (
        "Affinity with Art (a free Minor Hermetic Virtue, from the Tempestaria)",
        "Whistle Up The Wind (a free Major non-Hermetic Virtue, from the Tempestaria)",
        "Necessary Condition (the compulsory Major Hermetic Flaw, from the Tempestaria)",
    )
    # Another Major Supernatural Virtue isn't the tradition's free one.
    magus.virtues_flaws.append(VirtueFlawInstance("vf_entrancement"))
    assert cv.house_benefit(magus).virtue_points == 0
    wf.add_tradition_virtues(magus).apply()
    benefit = cv.house_benefit(magus)
    assert (benefit.virtue_points, benefit.flaw_points, benefit.missing) == (4, 3, ())
