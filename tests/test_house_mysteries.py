"""House Mysteries and spell timing: Faerie Magic's and Spell Timing's
parameters, recurring spells, Faerie Magic in the lab, Secret Name,
Verditius Hubris and casting tools, Tremere sigils, the Nemthengacha and
the free House Virtue (DE pp. 16, 235-244, 272)."""

import pytest

from ars_magica_manager import catalog
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    EnchantedDevice,
    Familiar,
    HermeticBackground,
    KnownSpell,
    Laboratory,
    Saga,
    ScoredTrait,
    SeasonPlan,
    Spell,
    SpellDesign,
    VirtueFlawInstance,
    XpAllocation,
)
from ars_magica_manager.rules import (
    casting_virtues,
    house_virtue,
    lab_seasons,
    lab_virtues,
    penetration,
    sigils,
    verditius,
)
from ars_magica_manager.rules import spell_levels as sl
from ars_magica_manager.rules import supplement_work as sw
from ars_magica_manager.rules.activities import TAUGHT
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _magus(*vf_ids: str, name: str = "Mira", id_: str = "m") -> Character:
    magus = Character(id=id_, name=name, type="magus")
    magus.virtues_flaws = [VirtueFlawInstance(v) for v in vf_ids]
    return magus


# -- spell parameters -------------------------------------------------------


def test_spectacle_costs_as_boundary_without_a_ritual():
    design = sl.spell_level(5, "Personal", "Sun", "Spectacle")
    assert design is not None
    assert design.level == 35  # +2 Sun, +4 as Boundary
    assert not design.ritual_required
    names = [e.name for e in sl.extra_parameters("target", {"vf_sensory_magic"})]
    assert "Spectacle" in names


def test_if_condition_is_the_triggered_duration_plus_four_and_a_ritual():
    design = sl.spell_level(5, "Touch", "If (Sun)", "Individual")
    assert design is not None
    # 5, +1 Touch, +2 Sun +4 = 7 magnitudes: 40.
    assert design.level == 40 and design.ritual_required
    durations = [e.name for e in sl.extra_parameters("duration", {"vf_spell_timing"})]
    assert {"If (Mom)", "If (Year)", "Held", "Season"} <= set(durations)


def test_faerie_magic_opens_its_six_parameters():
    ids = {"vf_faerie_magic"}
    ranges = [e.name for e in sl.extra_parameters("range", ids)]
    durations = [e.name for e in sl.extra_parameters("duration", ids)]
    targets = [e.name for e in sl.extra_parameters("target", ids)]
    assert ranges == ["Road"]
    assert {"Bargain (Mom)", "Fire", "Until (Condition)", "Year + 1"} <= set(durations)
    assert targets == ["Bloodline"]
    # Bargain: the triggered spell's Duration + 3 magnitudes.
    assert sl.steps_of("duration", "Bargain (Sun)") == 5
    assert sl.steps_of("duration", "Fire") == 3
    assert sl.steps_of("target", "Bloodline") == 3
    assert sl.needs_ritual("duration", "Until (Condition)")
    assert sl.needs_ritual("duration", "Year + 1")
    assert not sl.needs_ritual("duration", "Fire")


def test_mercurian_magic_alone_opens_no_road():
    assert sl.extra_parameters("range", {"vf_mercurian_magic"}) == []
    assert [e.name for e in sl.extra_parameters("target", {"vf_road_magic"})] == [
        "Road",
        "Road Network",
    ]


def test_fire_duration_wants_ignem_or_imaginem():
    corpus = sl.spell_level(5, "Voice", "Fire", "Individual", form="Corpus")
    ignem = sl.spell_level(5, "Voice", "Fire", "Individual", form="Ignem")
    assert corpus is not None and ignem is not None
    assert any("Ignem or Imaginem" in n for n in corpus.notes)
    assert not any("Ignem or Imaginem" in n for n in ignem.notes)


def test_a_recurring_spell_adds_its_magnitudes_and_is_a_ritual():
    design = sl.spell_level(5, "Touch", "Sun", "Individual", recurring="day")
    assert design is not None
    # 5, +1 Touch, +2 Sun, +4 recurring daily = 7 magnitudes: 40.
    assert design.level == 40 and design.ritual_required
    assert ("recurs each day", 4) in design.steps
    assert sl.recurring_magnitudes("minute") == 5
    assert sl.recurring_magnitudes("decade") == 1
    assert sl.recurring_magnitudes("") == 0
    with pytest.raises(ValueError):
        sl.recurring_magnitudes("hour")


def test_a_design_keeps_its_recurrence():
    design = SpellDesign(
        key="k",
        base_level=5,
        range="Touch",
        duration="Sun",
        target="Individual",
        recurring="year",
    )
    # 5, +1 Touch, +2 Sun, +2 recurring yearly = 5 magnitudes: 30.
    assert lab_seasons.design_level(design) == 30
    assert SpellDesign.from_dict({"key": "k"}).recurring == ""


def test_only_an_initiate_learns_a_mysterys_parameters():
    assert sl.virtue_needed(set(), "Road", "Fire", "Individual") == [
        "Fire Duration needs Faerie Magic."
    ]
    assert sl.virtue_needed({"vf_faerie_magic"}, "Road", "Fire", "Bloodline") == []
    assert sl.virtue_needed(set(), "Touch", "Held", "Spectacle") == [
        "Held Duration needs Spell Timing.",
        "Spectacle Target needs Sensory Magic.",
    ]
    spell = Spell(
        id="s",
        name="Hearth Ward",
        technique="Rego",
        form="Ignem",
        level=20,
        range="Touch",
        duration="Fire",
        target="Individual",
    )
    assert lab_seasons._mystery_needed(_magus(), spell) == (
        "Mira can't learn Hearth Ward: Fire Duration needs Faerie Magic."
    )
    assert lab_seasons._mystery_needed(_magus("vf_faerie_magic"), spell) == ""


# -- Faerie Magic in the lab ---------------------------------------------------


def test_faerie_magic_stands_in_for_magic_theory_and_raises_the_vis_limit():
    magus = _magus("vf_faerie_magic")
    magus.abilities = [
        Ability("Magic Theory", xp=ability_xp(2)),
        Ability("Faerie Magic", xp=ability_xp(5)),
    ]
    lines, notes = lab_virtues.faerie_lines(magus)
    assert [(line.label, line.amount) for line in lines] == [
        ("Faerie Magic in place of Magic Theory", 3)
    ]
    assert "5 more botch dice" in notes[0]
    assert lab_virtues.faerie_vis_limit(magus) == 14  # (2 + 5) x 2
    assert "14 if all of it is faerie vis" in lab_virtues.faerie_vis_note(magus)
    assert lab_virtues.faerie_vis_limit(_magus()) == 0


def test_faerie_work_is_experimenting_or_a_faerie_parameter():
    plain = SeasonPlan("m", 1220, "Spring", lab_seasons.INVENT)
    assert not lab_seasons._faerie_work(None, plain)
    plain.experimenting = True
    assert lab_seasons._faerie_work(None, plain)
    designed = SeasonPlan(
        "m",
        1220,
        "Spring",
        lab_seasons.INVENT,
        design=SpellDesign(key="k", duration="Year + 1"),
    )
    assert lab_seasons._faerie_work(None, designed)


# -- Secret Name -----------------------------------------------------------------


def test_secret_name_cuts_sympathetic_connections():
    caster = _magus()
    caster.abilities = [Ability("Penetration", xp=ability_xp(2))]
    target = _magus("vf_secret_name", name="Ilfetu", id_="t")
    sympathy = [penetration.SYMPATHIES[0]]
    plain = penetration.penetration_bonus(
        caster, arcane_connection="Hours or days", sympathies=sympathy
    )
    named = penetration.penetration_bonus(
        caster, arcane_connection="Hours or days", sympathies=sympathy, target=target
    )
    assert plain.total == 2 * 3 and named.total == 2 * 2


def test_secret_name_fails_with_a_talisman_or_familiar():
    magus = _magus()
    saga = Saga(id="s", name="S", characters=[magus])
    assert sw._mystery_problem(saga, magus, "vf_secret_name") == ""
    saga.familiars.append(Familiar(id="f", character_id="m", name="Owl"))
    assert "familiar" in sw._mystery_problem(saga, magus, "vf_secret_name")
    saga.familiars.clear()
    saga.enchanted_devices.append(
        EnchantedDevice(id="d", name="Staff", talisman=True, maker_id="m")
    )
    assert "talisman" in sw._mystery_problem(saga, magus, "vf_secret_name")


def test_faerie_magic_needs_one_touched_by_the_fay():
    magus = _magus()
    saga = Saga(id="s", name="S", characters=[magus])
    assert "touched by the fay" in sw._mystery_problem(saga, magus, "vf_faerie_magic")
    magus.aging.warping_points = 1
    assert sw._mystery_problem(saga, magus, "vf_faerie_magic") == ""
    other = _magus("vf_faerie_blood", id_="o")
    assert sw._mystery_problem(saga, other, "vf_faerie_magic") == ""


def test_the_mysteries_casting_reminders():
    found = casting_virtues.reminders(
        _magus("vf_faerie_magic", "vf_spell_timing", "vf_secret_name")
    )
    assert any(r.startswith("Faerie Magic: a Bargain spell") for r in found)
    assert any(r.startswith("Spell Timing:") for r in found)
    assert any(r.startswith("Secret Name:") for r in found)


# -- Verditius -----------------------------------------------------------------


def test_hubris_starts_at_one_and_grows_like_an_ability():
    assert verditius.starting_hubris(_magus()) == 1
    assert verditius.starting_hubris(_magus("vf_proud")) == 2
    assert verditius.starting_hubris(_magus("vf_proud_major")) == 4
    # Score 1 is 5 xp; 10 more reach 15, score 2; 15 more reach 30, score 3.
    assert verditius.hubris_score(9) == 1
    assert verditius.hubris_score(10) == 2
    assert verditius.hubris_score(25) == 3
    assert verditius.hubris_xp("Winning the Contest, masters") == 6
    assert verditius.hubris_xp(verditius.AUTOMATON, might_magnitude=4) == 4
    with pytest.raises(ValueError):
        verditius.hubris_xp("Gloating")


def test_a_casting_tools_level_and_vis():
    level = verditius.casting_tool_level(
        15, {"Fast Casting": 1, "Quiet Casting": 2}, casting_bonus=3
    )
    assert level == 15 + 2 + 4 + 3
    assert verditius.casting_tool_vis(level) == 3
    assert verditius.casting_tool_vis(10) == 1
    with pytest.raises(ValueError):
        verditius.casting_tool_level(15, {"Fast Casting": 2})
    with pytest.raises(ValueError):
        verditius.casting_tool_level(15, {"Quiet Casting": 3})
    assert verditius.properties_text([("Fast Casting", 1), ("Quiet Casting", 2)]) == (
        "Fast Casting, Quiet Casting x2"
    )


def test_a_casting_tools_lab_total_and_what_it_must_reach():
    magus = _magus("vf_verditius_magic", "vf_enchant_casting_tools")
    magus.arts = {"rego": ArtScore(xp=art_xp(10)), "ignem": ArtScore(xp=art_xp(8))}
    magus.abilities = [
        Ability("Magic Theory", xp=ability_xp(4)),
        Ability("Philosophiae", xp=ability_xp(2)),
        Ability("Craft: Woodworking", xp=ability_xp(3)),
    ]
    magus.personality_traits = [ScoredTrait("Hubris", 2)]
    spell = Spell(id="sp", name="Ward", technique="Rego", form="Ignem", level=15)
    magus.spells_known = [KnownSpell("sp")]
    lab = Laboratory(id="lab", covenant_id=None, name="Forge", owner_id="m")
    saga = Saga(id="s", name="S", characters=[magus], laboratories=[lab])
    total = verditius.casting_tool_total(
        saga, magus, spell, lab, craft="Craft: Woodworking"
    )
    base = int(lab_seasons.lab.lab_total(saga, magus, "Rego", "Ignem", lab).total)
    # + Philosophiae 2 + Hubris 2 + magnitude 3 + Craft 3.
    assert total.total == base + 10
    assert verditius.casting_tool_problems(magus, spell, 30, 15) == []
    assert verditius.casting_tool_problems(magus, spell, 29, 15) == [
        "Lab Total 29 is below twice the effect level, 30."
    ]


# -- Tremere sigils ----------------------------------------------------------------


def _tremere(name: str, parens: str = "", holds_own_sigil: bool = False) -> Character:
    magus = Character(id=name.lower(), name=name, type="magus")
    magus.hermetic = HermeticBackground(
        house="house_tremere", parens=parens, holds_own_sigil=holds_own_sigil
    )
    return magus


def test_a_tremere_parens_holds_his_filius_s_sigil():
    elder = _tremere("Elder", holds_own_sigil=True)
    middle = _tremere("Middle", parens="Elder")
    young = _tremere("Young", parens="Middle")
    saga = Saga(id="s", name="S", characters=[elder, middle, young])
    assert sigils.sigil_holder(saga, elder) == ("", None)
    assert sigils.sigil_holder(saga, middle) == ("Elder", elder)
    # Middle doesn't hold his own, so Young's passes up to Elder.
    assert sigils.sigil_holder(saga, young) == ("Elder", elder)
    middle.hermetic.holds_own_sigil = True
    assert sigils.sigil_holder(saga, young) == ("Middle", middle)
    assert "held by Middle" in sigils.sigil_text(saga, young)
    # A parens the saga doesn't have holds it; a dead one doesn't.
    loner = _tremere("Loner", parens="Unknown Master")
    assert sigils.sigil_holder(saga, loner) == ("Unknown Master", None)
    middle.wounds.dead = True
    assert sigils.sigil_holder(saga, young) == ("", None)
    assert sigils.sigil_text(saga, _magus()) == ""


# -- the Nemthengacha ----------------------------------------------------------------


def test_the_nemthengacha_tradition():
    found = next(
        t for t in catalog.load_tradition_catalog() if t.id == "trad_nemthengacha"
    )
    assert found.virtues == [
        "vf_embitterment",
        "vf_subtle_magic",
        "vf_deficient_technique",
    ]
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    assert all(v in by_id for v in found.virtues)


# -- the free House Virtue -------------------------------------------------------


def _house_saga(house: str = "house_flambeau") -> Saga:
    parens = _magus("vf_puissant_art", name="Ignatius", id_="p")
    parens.virtues_flaws = [VirtueFlawInstance("vf_puissant_art", {"art": "Ignem"})]
    parens.hermetic = HermeticBackground(house=house)
    child = Character(id="a", name="Ash", type="companion")
    child.hermetic = HermeticBackground(parens="Ignatius")
    return Saga(id="s", name="S", characters=[parens, child])


def _taught(year: int, season: str, subject: str = "art:Ignem") -> SeasonPlan:
    return SeasonPlan(
        "a", year, season, TAUGHT, [XpAllocation(subject)], teacher_id="p"
    )


def test_ten_seasons_with_the_parens_give_the_house_virtue():
    saga = _house_saga()
    child = saga.character("a")
    assert child is not None
    seasons_ = [
        (1220 + i // 4, ("Spring", "Summer", "Autumn", "Winter")[i % 4])
        for i in range(10)
    ]
    for year, season in seasons_[:9]:
        house_virtue.count_seasons(saga, [_taught(year, season)])
    # The same season twice counts once.
    house_virtue.count_seasons(saga, [_taught(*seasons_[8])])
    assert house_virtue.seasons_with_parens(child) == 9
    assert child.virtues_flaws == []
    reached = house_virtue.count_seasons(saga, [_taught(*seasons_[9])])
    assert reached == [child]
    assert child.virtues_flaws == [
        VirtueFlawInstance("vf_puissant_art", {"art": "Ignem"})
    ]
    assert child.diary[-1].name == "The House Virtue"


def test_what_counts_as_one_to_one_work():
    saga = _house_saga()
    # Teaching a mundane Ability doesn't count; an Art does.
    assert house_virtue.one_to_one(saga, _taught(1220, "Spring")) is not None
    brawl = _taught(1220, "Spring", "ability:Brawl")
    assert house_virtue.one_to_one(saga, brawl) is None
    stranger = SeasonPlan(
        "a", 1220, "Spring", TAUGHT, [XpAllocation("art:Ignem")], teacher_id="x"
    )
    assert house_virtue.one_to_one(saga, stranger) is None


def test_a_mystery_house_initiates_its_virtue_instead():
    saga = _house_saga("house_merinita")
    for i in range(12):
        house_virtue.count_seasons(saga, [_taught(1220 + i, "Spring")])
    child = saga.character("a")
    assert child is not None
    assert house_virtue.seasons_with_parens(child) == 0


def test_a_mercurian_magus_opens_road_once_he_has_learned_it():
    from ars_magica_manager.rules import spell_levels

    ids = {"vf_mercurian_magic"}
    assert spell_levels.ROAD_MAGIC not in spell_levels.opening_ids(
        ids, learned_road=False
    )
    assert spell_levels.ROAD_MAGIC in spell_levels.opening_ids(ids, learned_road=True)
    assert spell_levels.ROAD_MAGIC not in spell_levels.opening_ids(
        set(), learned_road=True
    )


def test_older_saves_keep_a_mercurian_magus_road():
    from ars_magica_manager.models import Character

    old = {
        "id": "m",
        "name": "Marcus",
        "type": "magus",
        "virtues_flaws": [{"vf_id": "vf_mercurian_magic"}],
        "hermetic": {"house": "house_ex_miscellanea"},
    }
    assert Character.from_dict(old).hermetic.road_magic
    old["hermetic"]["road_magic"] = False
    assert not Character.from_dict(old).hermetic.road_magic
    plain = {"id": "p", "name": "Plain", "type": "magus"}
    assert not Character.from_dict(plain).hermetic.road_magic
