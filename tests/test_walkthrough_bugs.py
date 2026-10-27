"""The bugs the walkthroughs found, fixed: names with their placeholders
filled, the Tribunal's name once, the worksheet's type and Flaw lists,
the creation spell cap's Magic Theory specialty (DE pp. 50, 168), a folk
witch's creation (Hedge Magic RE p. 34), Be taught's single student (DE
p. 378), similar spells when instilling (DE p. 258), debates' choice of
Abilities (Houses of Hermes: Societates p. 90) and a varied Script's
preview (DE p. 389)."""

from __future__ import annotations

import random

import pytest

from ars_magica_manager import ahead, catalog, tribunals
from ars_magica_manager.forms import character as character_forms
from ars_magica_manager.forms.lab_plan import LabPlanForm
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    Characteristics,
    CreationXp,
    Laboratory,
    Saga,
    SeasonPlan,
    Tribunal,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import (
    activities,
    apprentice_seasons,
    creation_magus,
    debate,
    study,
)
from ars_magica_manager.rules import creation_access as access
from ars_magica_manager.rules import creation_later as later
from ars_magica_manager.rules import enchant_seasons as es
from ars_magica_manager.rules.effects import fill_name
from ars_magica_manager.rules.xp import ability_xp, art_xp

FOLK = "trad_folk_witches"


# -- names (bugs 13, 17) -------------------------------------------------------


def test_a_virtue_s_name_has_what_it_names_filled_in():
    assert fill_name("Affinity with {art}", {"art": "ignem"}) == "Affinity with Ignem"
    assert fill_name("Affinity with {art}", {}) == "Affinity with {art}"
    assert catalog.blank_name("Affinity with {art}") == "Affinity with (Art)"
    assert catalog.needs_note("Affinity with {art}", ["art"]) == ""
    assert catalog.needs_note("Puissant", ["ability"]) == "  (needs: ability)"


def test_teach_a_hermetic_virtue_lists_the_magus_s_own_virtues():
    magus = Character(id="m", name="M", type="magus")
    magus.virtues_flaws = [
        VirtueFlawInstance("vf_affinity_with_art", {"art": "ignem"}),
        VirtueFlawInstance("vf_puissant_art", {"art": "creo"}),
    ]
    names = [name for name, _ in apprentice_seasons.teachable_virtues(magus)]
    assert names == ["Affinity with Ignem", "Puissant Creo"]


def test_a_tribunal_named_the_rhine_tribunal_is_named_once():
    assert tribunals.title_text("The Rhine Tribunal") == "Rhine Tribunal"
    assert tribunals.title_text("Rhine") == "Rhine Tribunal"
    saga = Saga(id="s", name="S", current_year=1220)
    saga.tribunals = [
        Tribunal(
            id="t", name="The Rhine Tribunal", next_year=1221, next_season="Summer"
        )
    ]
    texts = [e.title for e in ahead._tribunals(saga, 0, 10**6)]
    assert "The Rhine Tribunal meets" in texts


# -- the worksheet (bugs 8, 9) -------------------------------------------------


def test_edit_type_offers_every_type_while_in_creation():
    saga = Saga(id="s", name="S")
    magus = Character(id="m", name="M", type="magus", in_creation=True)
    fields = {f.key: f for f in character_forms.character_info_fields(saga, magus)}
    assert dict(fields["type"].options or []) == dict(
        character_forms.CHARACTER_TYPE_OPTIONS
    )
    magus.in_creation = False
    keys = {f.key for f in character_forms.character_info_fields(saga, magus)}
    assert "type" not in keys


def test_add_a_flaw_lists_the_flaws_alphabetically():
    flaws = [e for e in catalog.load_virtue_flaw_catalog() if e.side == "Flaw"]
    names = [e.name.casefold() for e in catalog.virtue_flaws_by_name(flaws)]
    assert names == sorted(names)


# -- the creation spell cap (bug 7) --------------------------------------------


def _adelheid(specialty: str) -> tuple[Saga, Character]:
    magus = Character(id="a", name="Adelheid", type="magus", in_creation=True)
    magus.characteristics = Characteristics(intelligence=3)
    magus.abilities = [Ability("Magic Theory", xp=ability_xp(3), specialty=specialty)]
    magus.arts = {"creo": ArtScore(xp=art_xp(6)), "ignem": ArtScore(xp=art_xp(14))}
    return Saga(id="s", name="S", characters=[magus]), magus


def test_a_magic_theory_specialty_in_the_spell_s_art_raises_the_cap():
    spell = next(
        s for s in catalog.load_spell_catalog() if s.id == "spell_ball_of_abysmal_flame"
    )
    saga, plain = _adelheid("Vim")
    _, ignem = _adelheid("Ignem")
    _, inventing = _adelheid("inventing spells")
    cap = creation_magus.spell_cap(saga, plain, spell)
    assert creation_magus.spell_cap(saga, ignem, spell) == cap + 1
    assert creation_magus.spell_cap(saga, inventing, spell) == cap + 1


# -- a folk witch's creation (bugs 10, 11, 12) ---------------------------------


def _grete() -> tuple[Saga, Character]:
    grete = Character(id="g", name="Grete", type="companion", in_creation=True)
    grete.background.year_born = 1195  # 25 in 1220
    grete.traditions = [FOLK]
    grete.virtues_flaws = [VirtueFlawInstance("vf_the_gift")]
    return Saga(id="s", name="S", current_year=1220, characters=[grete]), grete


def test_a_folk_witch_s_apprenticeship_years_are_not_later_life():
    saga, grete = _grete()
    assert later.apprenticed_years(saga, grete) == 10
    assert later.bought_years(saga, grete) == 10
    assert later.later_life_budget(saga, grete) == 150


@pytest.mark.parametrize(
    "tradition",
    ["trad_sorginak", "trad_bouda", "trad_settuten_berber", "trad_settuten_tuareg"],
)
def test_witch_traditions_built_as_folk_witches_take_the_same_years(tradition: str):
    saga, grete = _grete()
    grete.traditions = [tradition]
    assert later.apprenticed_years(saga, grete) == 10


def test_the_bedouin_hakima_s_book_gives_no_years():
    saga, grete = _grete()
    grete.traditions = ["trad_bedouin_hakima"]
    assert later.apprenticed_years(saga, grete) == 0


def test_a_gifted_folk_witch_may_learn_penetration():
    _, grete = _grete()
    assert access.may_learn(grete, "Penetration")


def test_a_gifted_folk_witch_s_opened_powers_need_no_virtue():
    saga, grete = _grete()
    for power in ("Cursing", "Flight", "Healing"):
        grete.creation_xp.append(CreationXp("training", power, 5))
    found = {c.label: c.status for c in later.later_life_checks(saga, grete)}
    assert found["The Gift allows one Supernatural Ability without its Virtue"] == (
        "pass"
    )


# -- Be taught (bug 14) --------------------------------------------------------


def test_a_lone_student_s_preview_counts_the_single_student_bonus():
    teacher = Character(id="t", name="Leandro", type="magus")
    teacher.characteristics = Characteristics(communication=1)
    teacher.abilities = [Ability("Teaching", xp=ability_xp(2))]
    student = Character(id="a", name="Adelheid", type="magus")
    saga = Saga(id="s", name="S", characters=[teacher, student])
    plan = SeasonPlan("a", 1220, "Spring", activities.TAUGHT, teacher_id="t")
    assert activities.students_of(saga, plan) == 1  # not saved yet
    saga.season_plans.append(plan)
    assert activities.students_of(saga, plan) == 1
    assert study.teaching_quality(teacher, 1) == 1 + 2 + 3 + 6


# -- instilling with a similar spell (bug 15) ----------------------------------


def test_instilling_keeps_the_similar_spell_chosen():
    magus = Character(id="m", name="M", type="magus", assigned_lab_id="lab")
    lab = Laboratory(id="lab", covenant_id=None, name="Lab", owner_id="m")
    saga = Saga(id="s", name="S", characters=[magus], laboratories=[lab])
    form = LabPlanForm(saga, magus, lab, "Spring", 1220, None)
    for activity in (es.INSTIL, es.LESSER_WORK):
        plan = form.plan_of({"activity": activity, "similar": "spell_pilum_of_fire"})
        assert plan.similar_spell_id == "spell_pilum_of_fire"


# -- debates (bug 19) ----------------------------------------------------------


def test_equal_speakers_choose_their_tacks_by_lot():
    rng = random.Random(3)
    speaker = debate.skilled("A")
    attacks = {speaker.choose_attack(rng) for _ in range(30)}
    defences = {speaker.choose_defence(rng) for _ in range(30)}
    assert attacks == set(debate.ATTACKS)
    assert defences == set(debate.DEFENCES)
    able = debate.Debater("B", attacks={"Intrigue": 3, "Folk Ken": 1})
    assert {able.choose_attack(rng) for _ in range(10)} == {"Intrigue"}


# -- the gaps: creation advice (gap 36, 37) and Living Conditions (gap 38) -----


def test_an_ability_without_a_specialty_is_advice():
    from ars_magica_manager.rules import creation as creation_rules

    saga, grete = _grete()
    grete.creation_xp.append(CreationXp("later_life", "Folk Ken", 15))
    grete.abilities.append(Ability("Folk Ken", xp=15))
    found = {c.label: c for c in creation_rules.checks(saga, grete, "later_life")}
    assert found["Each Ability has a specialty"].status == "advice"
    assert found["Each Ability has a specialty"].detail == "Folk Ken"
    grete.abilities[-1].specialty = "lies"
    found = {c.label: c for c in creation_rules.checks(saga, grete, "later_life")}
    assert found["Each Ability has a specialty"].status == "pass"


def test_the_equipment_step_advises_recording_gear():
    from ars_magica_manager.models import Possession
    from ars_magica_manager.rules import creation as creation_rules
    from ars_magica_manager.rules.creation_base import steps_for

    saga, grete = _grete()
    keys = [s.key for s in steps_for(grete)]
    assert keys[-2:] == ["equipment", "finish"]
    found = creation_rules.checks(saga, grete, "equipment")
    assert [c.status for c in found] == ["advice"]
    grete.inventory.append(Possession(id="staff", kind="item", name="Staff"))
    assert [c.status for c in creation_rules.checks(saga, grete, "equipment")] == [
        "pass"
    ]


def test_living_conditions_follow_the_covenant_s_season():
    from ars_magica_manager.models import Covenant
    from ars_magica_manager.rules import living

    spring = Covenant(id="c", saga_id="s", name="Keep")
    assert living.covenant_living(spring, magi=True) == 1
    assert living.covenant_living(spring, magi=False) == 0
    assert living.living_text(spring, magi=True) == "+1 (Spring)"
    spring.covenant_season = "Autumn"
    assert (
        living.covenant_living(spring, magi=True),
        living.covenant_living(spring, magi=False),
    ) == (2, 1)
    spring.living_conditions_magi = -1
    assert living.living_text(spring, magi=True) == "-1"
    old = Covenant.from_dict(
        {"id": "o", "saga_id": "s", "name": "Old", "living_conditions_magi": 0}
    )
    assert old.living_conditions_magi is None


# -- familiars (gap 40) --------------------------------------------------------


def test_the_binding_names_the_book_s_suggested_familiars():
    from ars_magica_manager.models import Familiar
    from ars_magica_manager.rules import familiar_seasons as fs

    owl = Familiar(id="f", character_id="m", name="Scintilla", species="Barn owl")
    note = fs.fitting_note(owl, "Intellego", "Mentem")
    assert note.startswith("Suggested familiars (DE p. 266): Intellego: ")
    assert "The list names a Barn owl for Mentem." in note
    falcon = Familiar(id="g", character_id="m", name="Fal", species="falcon")
    assert "Neither list names a falcon by name" in fs.fitting_note(
        falcon, "Creo", "Ignem"
    )
    assert fs.fitting_note(falcon, "", "") == ""


# -- Twilight's effects (gaps 43, 44) ------------------------------------------


def test_resolving_a_twilight_applies_its_effect_and_keeps_the_scar():
    from ars_magica_manager.forms import twilight

    magus = Character(id="m", name="Adelheid", type="magus")
    magus.arts = {"corpus": ArtScore(xp=10)}
    saga = Saga(id="s", name="S", current_year=1220, characters=[magus])
    lost = {"comprehended": False, "points": 3, "effect": twilight.XP, "art": "Corpus"}
    assert twilight.problem(lost) is None
    twilight.apply(saga, magus, lost | {"scar": "Meat she touches looks rotten."})
    assert magus.arts["corpus"].xp == 4  # 2 a point lost (DE p. 230)
    assert magus.aging.twilight_scars == "Meat she touches looks rotten."
    assert magus.diary[-1].details.startswith("A Twilight not comprehended (3 Warping")
    gained = {
        "comprehended": True,
        "points": 4,
        "effect": twilight.XP,
        "art": "Magic Theory",
    }
    twilight.apply(saga, magus, gained | {"scar": "Her eyes glitter."})
    assert next(a for a in magus.abilities if a.name == "Magic Theory").xp == 8
    assert magus.aging.twilight_scars.splitlines() == [
        "Meat she touches looks rotten.",
        "Her eyes glitter.",
    ]


def test_a_twilight_s_virtue_needs_seven_points_and_its_tier():
    from ars_magica_manager.forms import twilight

    assert twilight.tier_for(6, comprehended=True) == ""
    assert twilight.tier_for(10, comprehended=True) == "Minor"
    assert twilight.tier_for(11, comprehended=True) == "Major"
    assert twilight.tier_for(10, comprehended=False) == "Major"
    values = {"comprehended": True, "points": 5, "effect": twilight.VIRTUE}
    assert twilight.problem(values) == (
        "A Virtue or Flaw needs 7 Warping Points or more."
    )
    minor = next(
        v
        for _, v in twilight.virtue_options(comprehended=True)
        if catalog.load_virtue_flaw_catalog_by_id()[v].tier == "Minor"
    )
    assert twilight.problem(values | {"points": 12, "virtue": minor}) == (
        "12 points give a Major one, not Minor."
    )
    assert twilight.problem(values | {"points": 8, "virtue": minor}) is None


# -- the bond's Virtue at the binding (gap 41) ---------------------------------


def test_a_familiar_bound_by_lab_work_gains_the_bond_when_it_is_played():
    from ars_magica_manager import familiars as fam

    magus = Character(id="m", name="Adelheid", type="magus")
    saga = Saga(id="s", name="S", characters=[magus])
    falcon = fam.bind_familiar(saga, magus, "Scintilla", bound=False)
    assert not falcon.virtues_flaws and not magus.personality_traits
    assert fam.grant_bond(falcon, magus) == ["Scintilla", "Adelheid"]
    assert fam.grant_bond(falcon, magus) == []  # once only
    assert [t.name for t in magus.personality_traits] == ["Loyal (Partner)"]


# -- hedge casting rolled (gap 54) ---------------------------------------------


def test_a_folk_witch_casts_a_power_and_the_diary_keeps_it():
    from ars_magica_manager.forms import hedge_cast
    from ars_magica_manager.rules import hedge_casting as hc

    saga, grete = _grete()
    grete.characteristics = Characteristics(stamina=2)
    grete.abilities = [Ability("Healing", xp=ability_xp(4))]
    assert hc.can_cast(grete)
    fields = {f.key: f for f in hedge_cast.fields(saga, grete)}
    values = {key: f.value for key, f in fields.items()}
    assert "Healing" in dict(fields["casting"].options).values()
    values |= {"casting": "Healing", "level": 5, "die": 7}
    assert hedge_cast.problem(grete, values) is None
    told = hedge_cast.cast(saga, grete, values, random.Random(1))
    assert "Healing" in told[0] and "die 7 (typed)" in told[0]
    assert grete.diary[-1].name == "Cast: Healing"


# -- a Script's sacrifice (gap 47), the baseline's people (gap 48) -------------


def test_an_initiation_s_sacrifice_is_given_up_when_it_is_played():
    from ars_magica_manager.models import EnchantedDevice, Possession
    from ars_magica_manager.seasons.lab_apply import _make_sacrifice

    magus = Character(id="m", name="M", type="magus")
    magus.inventory = [Possession(id="ring", kind="item", name="Gold ring")]
    wand = EnchantedDevice(
        "wand", "Wand", "Invested Device", holder_kind="character", holder_id="m"
    )
    saga = Saga(id="s", name="S", characters=[magus], enchanted_devices=[wand])
    plan = SeasonPlan("m", 1220, "Spring", "undergo_initiation", [])
    from ars_magica_manager.forms.season import sacrifice_options

    assert [v for _, v in sacrifice_options(saga, magus)][:2] == [
        "device:wand",
        "item:ring",
    ]
    _make_sacrifice(saga, magus, "device:wand", plan)
    _make_sacrifice(saga, magus, "item:ring", plan)
    assert not saga.enchanted_devices and not magus.inventory
    assert [d.name for d in magus.diary] == [
        "Sacrificed: Wand",
        "Sacrificed: Gold ring",
    ]


def test_the_baseline_s_people_are_added_once():
    from ars_magica_manager import worksheet
    from ars_magica_manager.commands import Confirm, Refuse
    from ars_magica_manager.models import Covenant

    covenant = Covenant(id="c", saga_id="s", name="Keep", in_creation=True)
    saga = Saga(id="s", name="S", covenants=[covenant])
    assert isinstance(worksheet._add_baseline_people(saga, covenant), Refuse)
    saga.characters = [
        Character(id=f"m{i}", name=f"M{i}", type="magus", covenant_id="c")
        for i in range(3)
    ]
    step = worksheet._add_baseline_people(saga, covenant)
    assert isinstance(step, Confirm)
    step.apply()
    assert [(i.kind, i.quantity) for i in covenant.inhabitants] == [
        ("turb", 3),
        ("inhabitant", 6),
    ]
    assert isinstance(worksheet._add_baseline_people(saga, covenant), Refuse)


# -- gilds (gap 51) and a threat's stage (gap 52) ------------------------------


def test_a_rhine_covenant_leans_with_its_gild():
    from ars_magica_manager import meeting
    from ars_magica_manager.models import Case, Covenant
    from ars_magica_manager.tribunal_packages import rhine

    tribunal = Tribunal(id="t", name="Rhine", package=rhine.KEY)
    a = Covenant(id="a", saga_id="s", name="Fengheld", tribunal_id="t")
    b = Covenant(id="b", saga_id="s", name="Crintera", tribunal_id="t")
    saga = Saga(id="s", name="S", covenants=[a, b], tribunals=[tribunal])
    rhine.gilds(tribunal).append({"name": "Oak Gild", "members": ["a", "b"]})
    case = Case(id="k", title="Theft", brought_by="Fengheld", against="Someone")
    side, why = meeting.leaning_why(saga, case, b, tribunal)
    assert side == meeting.FOR and "Oak Gild" in why
    assert meeting.leaning_why(saga, case, b)[0] == meeting.UNDECIDED


def test_a_stage_marked_as_happened_writes_what_follows():
    from ars_magica_manager import threats
    from ars_magica_manager.models import Covenant, Neighbour

    keep = Covenant(id="c", saga_id="s", name="Keep", played=True)
    threat = Neighbour(id="n", name="The Wolf", kind="threat")
    threat.details["stages"] = [
        {"title": "The flocks die", "ignored": "The villagers blame the magi."}
    ]
    saga = Saga(
        id="s", name="S", current_year=1220, covenants=[keep], neighbours=[threat]
    )
    ops = threats.stage_ops(saga, threat)
    assert ops.edit is not None
    form = ops.edit(0)
    form.apply({"title": "The flocks die", "outcome": "Happened"})
    assert keep.diary[-1].details == (
        "The flocks die (happened): The villagers blame the magi."
    )


# -- the Boost calculator (audit piece) ----------------------------------------


def test_the_boost_calculator_counts_pawns_and_botch_dice():
    from ars_magica_manager.forms import boost
    from ars_magica_manager.models import KnownSpell

    magus = Character(id="m", name="Celer", type="magus")
    saga = Saga(id="s", name="S", characters=[magus])
    assert boost.boostable(saga, magus) == []
    magus.virtues_flaws = [VirtueFlawInstance("vf_boosted_magic")]
    magus.spells_known = [KnownSpell("spell_pilum_of_fire")]
    spells = boost.boostable(saga, magus)
    assert [s.id for s in spells] == ["spell_pilum_of_fire"]
    pilum = spells[0]
    text = boost.live(
        saga, {"spell": pilum.id, "range": "Sight", "target": pilum.target, "size": 0}
    )
    # Voice to Sight is one magnitude: a pawn and a botch die (DE p. 73).
    assert "[$label]Pawns of vis[/] 1  ·  [$label]Botch dice[/] +1" in text
    lowered = boost.live(saga, {"spell": pilum.id, "range": "Touch", "size": 0})
    assert "Boosting never lowers its Range." in lowered


# -- a ship sunk or taken (audit piece) ----------------------------------------


def test_a_ship_sunk_counts_in_no_fleet_and_one_taken_moves():
    from ars_magica_manager.forms import ships as ship_forms
    from ars_magica_manager.models import Covenant, Possession
    from ars_magica_manager.models.ships import Ship
    from ars_magica_manager.rules import ships as rules

    keep = Covenant(id="k", saga_id="s", name="Keep")
    rival = Covenant(id="r", saga_id="s", name="Rival")
    cog = Possession(id="cog", kind="ship", name="Seahawk", ship=Ship())
    keep.possessions = [cog]
    saga = Saga(id="s", name="S", current_year=1221, covenants=[keep, rival])
    form = ship_forms.mark_fate(saga, keep, 0)
    form.apply({"fate": "Sunk"})
    assert (
        rules.lost(rules.ship_of(cog)) and rules.ship_of(cog).fate_when == "Spring 1221"
    )
    form.apply({"fate": "afloat"})
    assert not rules.lost(rules.ship_of(cog))
    form.apply({"fate": "Taken", "captor": "r"})
    assert cog in rival.possessions and cog not in keep.possessions
    assert keep.diary[-1].details == "Seahawk was taken by Rival."


# -- a saga's own Mystery Cult exported (audit piece) --------------------------


def test_a_saga_cult_exports_and_imports_into_another_saga(tmp_path):
    from ars_magica_manager import cult_transfer
    from ars_magica_manager.models import MysteryCult

    cult = MysteryCult(
        "custom_cult_owls", "Owls of Minerva", "Owl Lore", founder_id="x"
    )
    path = cult_transfer.export_to(tmp_path / "owls.cult.json", cult)
    other = Saga(
        id="o",
        name="Other",
        custom_cults=[MysteryCult("custom_cult_c", "Owls of Minerva", "")],
    )
    added = cult_transfer.add(other, cult_transfer.read(path))
    assert added.name == "Owls of Minerva (imported)" and added.founder_id == ""
    assert added in other.custom_cults and added.id != "custom_cult_c"
    (tmp_path / "bad.json").write_text("{}", encoding="utf-8")
    import pytest

    with pytest.raises(ValueError, match="not a Mystery Cult export"):
        cult_transfer.read(tmp_path / "bad.json")


# -- studying from a large library (TME p. 105) --------------------------------


def test_reading_the_library_studies_its_whole_holding_of_a_subject():
    from ars_magica_manager import seasons
    from ars_magica_manager.forms.season import library_options
    from ars_magica_manager.models import Book, Covenant
    from ars_magica_manager.rules import options as rule_options

    magus = Character(id="m", name="M", type="magus", covenant_id="k")
    books = [
        Book(
            f"s{i}",
            f"Ignem {i}",
            "Art Summa",
            art="Ignem",
            level=6,
            quality=7 - i % 2,
            owner_kind="covenant",
            owner_id="k",
        )
        for i in range(3)
    ]
    saga = Saga(
        id="s",
        name="S",
        current_year=1220,
        characters=[magus],
        covenants=[Covenant(id="k", saga_id="s", name="Keep")],
        books=books,
    )
    plan = SeasonPlan(
        "m", 1220, "Spring", activities.READ, [], book_id="library:art:Ignem"
    )
    assert "Large Library optional rule" in activities.problems(magus, plan, saga)[0]
    saga.rule_options[rule_options.LARGE_LIBRARY] = True
    saga.books_in_play = ["ArM5", "TME"]
    assert [v for _, v in library_options(saga, magus)] == ["library:art:Ignem"]
    assert activities.problems(magus, plan, saga) == []
    figures = activities.library_figures(saga, magus, "art:Ignem")
    assert figures is not None and figures.quality == 7
    worked = activities.outcome(magus, plan, saga)
    # Below its Level: Quality + 3 (TME p. 105).
    assert worked.gains[0].result.xp == figures.quality + 3
    seasons.set_plan(saga, plan)
    seasons.apply(saga, seasons.resolve(saga, random.Random(1)))
    assert magus.arts["ignem"].xp == figures.quality + 3
    assert "The library on Ignem" in magus.diary[-1].details


# -- the covenant's land works (TME pp. 53-77) ---------------------------------


def test_the_land_works_list_ticks_each_ritual_cast():
    from ars_magica_manager.forms import land_shaping
    from ars_magica_manager.models import Covenant, LandProject, Progress
    from ars_magica_manager.rules import land_shaping as ls

    keep = Covenant(id="k", saga_id="s", name="Keep")
    saga = Saga(id="s", name="S", covenants=[keep])
    assert "None planned" in land_shaping.land_works_text(saga, keep)
    keep.land_projects = [LandProject(id="p", name="New Isle")]
    magus = Character(id="m", name="M", type="magus")
    magus.progress = [Progress(ls.LAND_KIND, "New Isle", 0, 1)]
    saga.characters = [magus]
    text = land_shaping.land_works_text(saga, keep)
    works = ls.works(keep.land_projects[0])
    assert f"1 of {len(works)} Ritual(s) cast" in text
    assert text.count("✔") == 1


# -- a character's own Marriages section ---------------------------------------


def test_a_character_s_sheet_lists_the_marriages_naming_them():
    from ars_magica_manager import marriages
    from ars_magica_manager.models import Marriage
    from ars_magica_manager.models.marriage import CHARACTER_REF

    karl = Character(id="k", name="Karlotte", type="companion")
    saga = Saga(id="s", name="S", characters=[karl])
    assert marriages.character_text(saga, karl) == ""
    saga.marriages = [
        Marriage(
            id="m", bride_ref=CHARACTER_REF + "k", groom="Wolfram von Schattenbach"
        )
    ]
    assert marriages.of_character(saga, karl) == saga.marriages
    assert "Wolfram von Schattenbach" in marriages.character_text(saga, karl)


# -- deep covers and personae (HoH:S pp. 87-90) --------------------------------


def test_a_deep_cover_gains_reputation_each_season_it_is_kept_up():
    from ars_magica_manager.forms import covers
    from ars_magica_manager.models import DeepCover
    from ars_magica_manager.rules import house_magic

    tytalus = Character(id="t", name="Carolus Furax", type="magus")
    assert not covers.shown(tytalus)
    tytalus.hermetic.house = "house_tytalus"
    assert covers.shown(tytalus)
    ops = covers.ops(tytalus)
    assert ops.add is not None
    form = ops.add()
    form.apply(
        {
            "kind": "cover",
            "name": "Reynard the Mercenary",
            "contact": "lives there",
            "reputation_xp": 5,
        }
    )
    reynard = tytalus.covers[0]
    assert covers.reputation(tytalus, reynard) == 1
    assert house_magic.keep_covers(tytalus) == [
        "Cover Reynard the Mercenary: +2 Reputation xp (1)."
    ]
    assert reynard.reputation_xp == 7
    again = Character.from_dict(
        {
            "id": "t",
            "name": "C",
            "type": "magus",
            "covers": [{"name": "R", "contact": "lives there"}],
        }
    )
    assert again.covers[0].name == "R"
    import pytest

    with pytest.raises(ValueError, match="unknown kind"):
        DeepCover.from_dict({"name": "X", "kind": "spy"})


# -- raising an army and ending a battle (LoM pp. 102-109) ---------------------


def _battle_saga():
    from ars_magica_manager.models import Battle, BattleSide, Neighbour

    lord = Neighbour(id="l", name="Baron Eckhart", kind="lord")
    lord.details.update({"title": "baron", "wealth": "Average"})
    knight = Character(id="k", name="Sir Konrad", type="companion")
    knight.characteristics = Characteristics(presence=2, intelligence=1)
    knight.abilities = [Ability("Leadership", xp=ability_xp(4))]
    fight = Battle(
        "Falkenstein",
        sides=[
            BattleSide(neighbour_id="l", groups=10),
            BattleSide("Raiders", groups=8),
        ],
    )
    saga = Saga(
        id="s", name="S", characters=[knight], neighbours=[lord], battles=[fight]
    )
    return saga, fight


def test_allies_join_by_the_allied_troops_table():
    from ars_magica_manager import battle_muster as bm

    saga, fight = _battle_saga()
    form = bm.raise_allies(saga, fight)
    # 2 + 4 + 3 = 9, + die 4 = 13: Equal, as many again as his 40 core groups.
    form.apply({"side": "0", "commander": "k", "affinity": 3, "core": 40, "die": 4})
    assert fight.sides[0].groups == 50 and fight.sides[0].mix == {"allies": 40}


def test_mercenaries_cost_the_budget_and_a_loan_drops_wealth():
    from ars_magica_manager import battle_muster as bm

    saga, fight = _battle_saga()
    form = bm.hire_mercenaries(saga, fight)
    # A baron's Average budget is 40 pounds (LoM p. 103).
    assert "budget is 40" in form.validate({"side": "0", "knights": 3})
    # Average to Poor: five times his 40 (p. 104).
    assert form.validate({"side": "0", "knights": 3, "loan": "Poor"}) is None
    assert "can't leave him Average" in form.validate(
        {"side": "0", "knights": 3, "loan": "Average"}
    )
    form.apply({"side": "0", "knights": 3, "loan": "Poor"})
    assert fight.sides[0].mix["knights"] == 3
    lord = saga.neighbour("l")
    assert lord.details["wealth"] == "Poor"
    assert "can't take a War Loan" in form.validate(
        {"side": "0", "knights": 1, "loan": "Poor"}
    )


def test_a_wealthy_lords_war_loans_follow_lords_of_men_p_104():
    from ars_magica_manager import battle_muster as bm

    saga, _fight = _battle_saga()
    lord = saga.neighbour("l")
    lord.details["wealth"] = "Wealthy"
    # A baron: Wealthy 100, Average 40.
    assert bm.loan(lord, "Average") == 300
    assert bm.loan(lord, "Poor") == 500


def test_an_event_s_losses_come_from_the_kind_its_enemy_names():
    from ars_magica_manager import battles

    _saga, fight = _battle_saga()
    side = fight.sides[0]
    side.mix = {"knights": 2, "levies": 3}
    taken = battles.take_losses(side, "Expensive", 3)
    assert taken == ["2 of knights", "1 of levies"] and side.groups == 7


def test_the_victors_gain_confidence_for_each_event_won():
    from ars_magica_manager import battle_muster as bm
    from ars_magica_manager.models import BattleEvent

    saga, fight = _battle_saga()
    fight.events = [BattleEvent("k", 0, won=True), BattleEvent("k", 0, won=True)]
    bm.end_of_day(saga, fight).apply({"how": "won", "side": "0", "commander": "k"})
    knight = saga.character("k")
    assert knight.background.confidence_points == 2
    assert knight.reputations[0].name == "Victorious commander"
    assert "won the day" in fight.ended


# -- standard combat groups (LoM p. 108) ---------------------------------------


def test_a_standard_combat_group_joins_a_fight_as_five_in_a_group():
    from ars_magica_manager import fights
    from ars_magica_manager.models import Fight, FightSide

    fight = Fight("Skirmish", sides=[FightSide("Ours"), FightSide("Theirs")])
    saga = Saga(id="s", name="S", fights=[fight])
    form = fights.add_combatant(saga, fight)
    assert form.validate({"kind": fights.TROOP, "troop": "0"}) is None
    form.apply({"side": "1", "kind": fights.TROOP, "troop": "0"})
    knights = fight.sides[1].combatants
    assert len(knights) == 5 and knights[0].attack == 17 and knights[0].mounted
    group = fight.sides[1].groups[0]
    assert group.trained and len(group.members) == 5


def test_combat_options_word_the_gait_and_the_charge():
    from ars_magica_manager import combat_options_form as cof
    from ars_magica_manager.models import Combatant, Fight, FightSide

    rider = Character(id="r", name="Sir Konrad", type="companion")
    rider.abilities = [Ability("Single Weapon", xp=ability_xp(5))]
    fight = Fight(
        "Joust",
        sides=[
            FightSide("A", combatants=[Combatant("Konrad", "character", "r")]),
            FightSide("B"),
        ],
    )
    saga = Saga(id="s", name="S", characters=[rider], fights=[fight])
    assert "Gallop[/]: missiles -6" in cof.live(
        saga, {"option": "gait", "gait": "Gallop"}
    )
    assert "+5 to the Attack" in cof.live(saga, {"option": "charge", "who": "r"})


# -- siege actions (LoM pp. 112-116) -------------------------------------------


def test_siege_actions_deploy_feed_the_castle_and_take_it():
    from ars_magica_manager import siege_actions as sa
    from ars_magica_manager.models import Siege

    siege = Siege(
        "The Siege of Burg Falkenstein",
        castle="Burg Falkenstein",
        besieger="Baron Eckhart",
    )
    saga = Saga(id="s", name="S", sieges=[siege])
    told = sa.deployments(saga, siege).apply(
        {
            "besieger_0": 2,
            "besieger_1": 2,
            "besieger_2": 2,
            "garrison_0": 3,
            "garrison_1": 3,
        }
    )
    assert sa.undefended(siege) == [2] and "a stockade" in told[0]
    sa.supplies_story(saga, siege).apply({"story": sa.SPELL_BREAD})
    assert siege.bread_until is not None
    sa.supplies_story(saga, siege).apply({"story": sa.STORY_BLOCKADE})
    assert siege.supplies == "Shoddy"
    told = sa.run_stockade(saga, siege, random.Random(2)).apply({"intervals": 3})
    assert told[0].endswith(f"day {siege.days}.")
    if not siege.ended:
        sa.castle_taken(saga, siege).apply({"governor": "Sir Odo"})
        assert siege.ended == "Taken" and siege.holder == "Baron Eckhart"


def test_allies_are_lost_after_the_sides_own_groups():
    from ars_magica_manager import battles
    from ars_magica_manager.models import BattleSide

    side = BattleSide()
    battles.add_groups(side, "infantry", 2)
    battles.add_groups(side, battles.ALLIES, 3)
    battles.take_losses(side, "Expensive", 4)
    assert side.mix == {"infantry": 0, battles.ALLIES: 1}
    assert side.groups == 1


def test_raise_the_siege_only_darkens_the_commanders_view():
    from ars_magica_manager import siege_actions as sa
    from ars_magica_manager.models import Siege

    siege = Siege("The Siege", castle="Burg", besieger="Baron Eckhart")
    saga = Saga(id="s", name="S", sieges=[siege])
    told = sa.supplies_story(saga, siege).apply(
        {"story": sa.SPELL_RAISE, "resist": 3, "die": 2}
    )
    assert not siege.ended
    assert "until sunset" in told[0]


def test_a_noble_lives_as_the_magi_do():
    from ars_magica_manager.models import VirtueFlawInstance
    from ars_magica_manager.rules import living

    knight = Character(id="odo", name="Sir Odo", type="companion")
    assert not living.lives_as_magus(knight)
    knight.virtues_flaws.append(VirtueFlawInstance("vf_knight"))
    assert living.lives_as_magus(knight)


def test_a_script_may_sacrifice_books_a_familiar_or_a_season():
    from ars_magica_manager.forms import season as season_forms
    from ars_magica_manager.models import Book, Familiar, SeasonPlan
    from ars_magica_manager.seasons import lab_apply

    magus = Character(id="m", name="Ulric", type="magus")
    book = Book("b", "De Igne", "Tractatus", owner_kind="character", owner_id="m")
    saga = Saga(
        id="s",
        name="S",
        characters=[magus],
        books=[book],
        familiars=[Familiar("f", "m", name="Corax")],
    )
    offered = {v for _label, v in season_forms.sacrifice_options(saga, magus)}
    assert {"book:b", "familiar:f", "wealth", "service", "vis"} <= offered
    plan = SeasonPlan("m", 1220, "Spring", "undergo_initiation")
    lab_apply._make_sacrifice(saga, magus, "book:b", plan)
    lab_apply._make_sacrifice(saga, magus, "familiar:f", plan)
    assert not saga.books and not saga.familiars
    lab_apply._make_sacrifice(saga, magus, "service", plan)
    served = saga.season_plans[-1]
    assert (served.season, served.year, served.activity) == ("Summer", 1220, "other")
    assert "serving the cult" in magus.diary[-1].details


def test_a_persona_starts_at_1_and_grows_with_the_persona_ability():
    from ars_magica_manager.forms import covers
    from ars_magica_manager.models import Ability
    from ars_magica_manager.rules import house_magic as hm

    magus = Character(id="m", name="Ulric", type="magus")
    magus.abilities.append(Ability("Persona", "Supernatural", xp=5))
    covers.ops(magus).add().apply({"kind": "persona", "name": "Reynard"})
    persona = magus.covers[0]
    assert hm.cover_reputation(persona, magus) == 1
    magus.abilities[0].xp += 10  # 15 xp: Reputation 2
    assert hm.cover_reputation(persona, magus) == 2
