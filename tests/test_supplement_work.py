"""The supplements' sub-systems (decision 38): Labor Points, workshops,
progress records, Initiation, universities, wounds."""

import random

import pytest

from ars_magica_manager import seasons
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Book,
    Character,
    Characteristics,
    Ordeal,
    Saga,
    ScoredTrait,
    SeasonPlan,
    VirtueFlawInstance,
    Wounds,
    XpAllocation,
)
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.rules import supplement_work as sw
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _saga() -> Saga:
    smith = Character(id="c", name="Wulf", type="companion")
    smith.characteristics = Characteristics(dexterity=2, communication=1, presence=2)
    smith.abilities = [
        Ability("Craft: Smith", xp=ability_xp(6)),
        Ability("Artes Liberales", xp=ability_xp(1)),
        Ability("Animal Handling", xp=ability_xp(4)),
        Ability("Mercere Lore", xp=ability_xp(5)),
    ]
    return Saga(id="s", name="S", characters=[smith])


def _plan(activity, subject="ability:Craft: Smith", **kw):
    return SeasonPlan(
        "c", 1220, "Spring", activity, [XpAllocation(subject)] if subject else [], **kw
    )


def _run(saga, plan, rng=None):
    seasons.set_plan(saga, plan)
    seasons.apply(saga, seasons.resolve(saga, rng or random.Random(1)))
    return saga.character("c")


def test_a_working_season_earns_labor_points():
    wulf = _run(_saga(), _plan("working_season"))
    assert wulf.labor_points == (2 + 6) * 3  # (Dex + Craft) x average


def test_wealthy_and_poor_change_the_multiplier():
    saga = _saga()
    saga.character("c").virtues_flaws = [VirtueFlawInstance("vf_wealthy")]
    assert _run(saga, _plan("working_season")).labor_points == 48


def test_workshop_production_reaches_a_quality_and_writes_a_manual():
    saga = _saga()
    wulf = _run(saga, _plan("workshop_production", quick=True, other_modifier=4))
    # Dex 2 + Craft 6 + 4 = 12: Superior; a manual for 1 Labor Point.
    assert (
        "Workshop Total 12 against Craft Level 6: Superior goods"
        in wulf.diary[-1].details
    )
    assert wulf.labor_points == 24 - 1
    assert saga.books[-1].description.startswith("A craft manual on Craft: Smith: +2")


def test_improving_the_workshop_costs_labor_points():
    saga = _saga()
    wulf = saga.character("c")
    found = rules.problems(wulf, _plan("improve_workshop", title="raw materials"), saga)
    assert found[0].startswith("Raising Raw Materials to 1 costs 50 Labor Points")
    wulf.labor_points = 60
    _run(saga, _plan("improve_workshop", title="raw materials"))
    assert (wulf.workshop_raw_materials, wulf.labor_points) == (1, 10)


def test_business_upkeep_in_winter():
    saga = _saga()
    wulf = saga.character("c")
    wulf.labor_points, wulf.workshop_raw_materials = 100, 2
    seasons.year_end_business(saga)
    assert wulf.labor_points == 100 - 36 - 10


def test_a_pilgrimage_is_progress_toward_its_target():
    saga = _saga()

    def pilgrimage():
        return SeasonPlan(
            "c",
            1220,
            saga.current_season,
            "pilgrimage",
            [XpAllocation("ability:Church Lore")],
            title="Santiago",
            other_modifier=6,
        )

    wulf = _run(saga, pilgrimage())
    (record,) = wulf.progress
    assert (record.points, record.target, record.done) == (9, 18, False)
    saga.current_season = "Summer"
    _run(saga, pilgrimage())
    assert record.done
    assert "Finished: Santiago" in [d.name for d in wulf.diary]


def test_taming_an_animal():
    wulf = _run(
        _saga(),
        _plan(
            "tame_animal", subject="ability:Animal Handling", title="Grey", book_level=2
        ),
    )
    assert wulf.progress[0].points == 0 + 4 - 2  # Int + Handling - Might


def test_a_formula_needs_five_xp():
    wulf = _run(
        _saga(),
        _plan("research_formula", subject="ability:Philosophiae", title="Aqua vitae"),
    )
    assert wulf.formulas == ["Aqua vitae"]


def test_an_initiation_gives_the_virtue_and_counts_the_ordeal():
    saga = _saga()
    plan = _plan(
        "undergo_initiation",
        subject="",
        teacher_id="c",
        title="Mercere Lore",
        effect_id="vf_adept_laboratory_student",
        device_id="vf_ambitious",
        research_kind="Minor",
        other_modifier=12,
    )
    # Presence 2 + Lore 5 + Script 12 = 19 against 18 (Minor, self-initiated).
    wulf = _run(saga, plan)
    ids = [vf.vf_id for vf in wulf.virtues_flaws]
    assert ids == ["vf_adept_laboratory_student", "vf_ambitious"]
    assert wulf.ordeals == [Ordeal("Minor", 0)]
    # Now he has the Virtue (15), and the Ordeal takes 3 off the next.
    assert sw.initiation_target(saga, wulf, plan) == 12


def test_a_mystagogue_has_the_virtue_only_with_what_it_names():
    saga = _saga()
    wulf = saga.character("c")
    assert wulf is not None
    mystagogue = Character(id="m", name="Mira", type="magus")
    mystagogue.virtues_flaws = [
        VirtueFlawInstance("vf_puissant_ability", {"ability": "Latin"})
    ]
    saga.characters.append(mystagogue)
    plan = _plan(
        "undergo_initiation",
        subject="",
        teacher_id="m",
        effect_id="vf_puissant_ability",
        effect_params={"ability": "Penetration"},
    )
    assert sw.initiation_target(saga, wulf, plan) == 18
    plan.effect_params = {"ability": "Latin"}
    assert sw.initiation_target(saga, wulf, plan) == 15


def test_the_initiate_needs_the_lore_unless_it_is_their_house_s():
    saga = _saga()
    wulf = saga.character("c")
    assert wulf is not None
    mira = Character(id="m", name="Mira", type="magus")
    mira.abilities = [Ability("House Bjornaer Lore", xp=ability_xp(8))]
    saga.characters.append(mira)
    plan = _plan(
        "undergo_initiation",
        subject="",
        teacher_id="m",
        title="House Bjornaer Lore",
        effect_id="vf_puissant_ability",
    )
    assert sw.problems(saga, wulf, plan) == [
        "Wulf needs House Bjornaer Lore 1 to be Initiated."
    ]
    wulf.hermetic.house = "house_bjornaer"
    assert sw.problems(saga, wulf, plan) == []


def test_no_mystagogue_is_a_self_initiation():
    saga = _saga()
    plan = _plan(
        "undergo_initiation",
        subject="",
        title="Mercere Lore",
        effect_id="vf_affinity_with_art",
        effect_params={"art": "ignem"},
        other_modifier=11,
    )
    # Wulf's own Presence 2 + Mercere Lore 5 + 11 = 18 against 18.
    assert sw.problems(saga, saga.character("c"), plan) == []
    wulf = _run(saga, plan)
    assert wulf.virtues_flaws[-1] == VirtueFlawInstance(
        "vf_affinity_with_art", {"art": "ignem"}
    )


def test_the_past_ordeal_that_lowers_the_target_most_counts():
    saga = _saga()
    wulf = saga.character("c")
    assert wulf is not None
    plan = _plan("undergo_initiation", subject="", effect_id="vf_puissant_ability")
    # A Major Ordeal two Initiations ago (-6), then a Minor one (-3).
    wulf.ordeals = [Ordeal("Major", 1), Ordeal("Minor", 0)]
    assert sw.initiation_target(saga, wulf, plan) == 18 - 6
    wulf.ordeals = [Ordeal("Major", 2), Ordeal("Minor", 1)]
    assert sw.initiation_target(saga, wulf, plan) == 18 - 3


def test_each_initiation_counts_down_every_past_ordeal():
    saga = _saga()
    wulf = saga.character("c")
    assert wulf is not None
    wulf.ordeals = [Ordeal("Major", 2), Ordeal("Medium", 0)]
    plan = _plan(
        "undergo_initiation",
        subject="",
        title="Mercere Lore",
        effect_id="vf_adept_laboratory_student",
        device_id="vf_ambitious",
        other_modifier=12,
    )
    # The Major Ordeal's third Initiation is spent; the new Minor one joins.
    wulf = _run(saga, plan)
    assert wulf.ordeals == [Ordeal("Medium", 1), Ordeal("Minor", 0)]


def test_an_older_save_s_last_ordeal_loads_as_one():
    data = {"id": "c", "name": "Wulf", "type": "companion"}
    data |= {"ordeal": "Major", "initiations_since_ordeal": 1}
    assert Character.from_dict(data).ordeals == [Ordeal("Major", 1)]
    assert Character.from_dict({**data, "ordeal": ""}).ordeals == []


def test_wounds_limit_what_a_season_can_be():
    saga = _saga()
    wulf = saga.character("c")
    wulf.wounds = Wounds(medium=1)
    found = rules.problems(wulf, _plan("workshop_production"), saga)
    assert found == ["Wulf's wounds (-3) allow no lab or craft work."]
    worked = rules.outcome(
        wulf, _plan(rules.PRACTICE, subject="ability:Animal Handling"), saga
    )
    assert worked.gains[0].result.xp == 2  # 4, halved
    wulf.wounds = Wounds(heavy=2)
    found = rules.problems(wulf, _plan(rules.PRACTICE), saga)
    assert found[0].startswith("Wulf's wounds (-10) allow nothing productive")


def test_an_inspeximus_raises_the_summas_level():
    saga = _saga()
    wulf = saga.character("c")
    wulf.type = "magus"
    wulf.arts = {"ignem": ArtScore(xp=art_xp(16))}
    saga.books = [
        Book("s1", "Flames", "Art Summa", author="Wulf", art="Ignem", level=5)
    ]
    _run(saga, _plan("inspeximus", subject="art:Ignem", book_id="s1", book_level=10))
    assert saga.books[0].level == 7  # 5 + (16 - 10) / 3, capped at 8


def test_recorded_lectures_add_half_the_scribes_score_rounded_down():
    """Quality = the teacher's Communication + the scribe's Profession:
    Scribe / 2; Art & Academe states no rounding, so down."""
    saga = _saga()
    teacher = Character(id="t", name="Magister", type="companion")
    teacher.characteristics = Characteristics(communication=3)
    saga.characters.append(teacher)
    scribe = saga.character("c")
    scribe.abilities.append(Ability("Profession: Scribe", xp=ability_xp(3)))
    plan = _plan("record_lectures", "ability:Latin", teacher_id="t")
    result = sw.work(saga, scribe, plan, random.Random(1))
    assert [b.quality for b in result.books] == [3 + 1]


# -- every branch of problems() and work() (cover before moving) ----


def _with(**changes) -> Saga:
    saga = _saga()
    wulf = saga.character("c")
    assert wulf is not None
    for key, value in changes.items():
        setattr(wulf, key, value)
    return saga


@pytest.mark.parametrize(
    ("changes", "plan", "problem"),
    [
        ({}, _plan("apothecary", None), "Choose the Ability the season works with."),
        ({}, _plan("workshop_production", None), "Choose the Craft."),
        (
            {},
            _plan("improve_workshop", title="x"),
            "Choose Innovation or Raw Materials to improve.",
        ),
        (
            {},
            _plan("improve_workshop", title="Innovation"),
            "Raising Innovation to 1 costs 100 Labor Points; Wulf has 0.",
        ),
        (
            {"workshop_innovation": 3},
            _plan("improve_workshop", title="Innovation"),
            "Innovation is already at its most (3).",
        ),
        ({}, _plan("undergo_initiation"), "Choose the Mystery Virtue initiated."),
        (
            {},
            _plan("undergo_initiation", effect_id="vf_ambitious"),
            "Ambitious is not a Virtue: choose the Virtue initiated.",
        ),
        (
            {},
            _plan("undergo_initiation", effect_id="vf_puissant_ability"),
            "Name the Mystagogue's (Mystery Cult) Lore.",
        ),
        (
            {},
            _plan(
                "undergo_initiation",
                effect_id="vf_puissant_ability",
                title="Mithraic Lore",
            ),
            "Wulf doesn't know Mithraic Lore.",
        ),
        (
            {},
            _plan(
                "undergo_initiation",
                effect_id="vf_puissant_ability",
                title="Mercere Lore",
                device_id="vf_adept_laboratory_student",
            ),
            "Adept Laboratory Student is not a Flaw: choose the Ordeal Flaw.",
        ),
        (
            {},
            _plan(
                "undergo_initiation",
                effect_id="vf_puissant_ability",
                title="Mercere Lore",
                device_id="vf_ambitious",
                research_kind="Medium",
            ),
            "A Minor Flaw is a Minor Ordeal.",
        ),
        (
            {},
            _plan(
                "undergo_initiation",
                effect_id="vf_puissant_ability",
                title="Mercere Lore",
                device_id="vf_poor",
                research_kind="Minor",
            ),
            "A Major Flaw is a Major Ordeal, or Medium when it raises a related "
            "Minor Flaw.",
        ),
        (
            {},
            _plan("create_art"),
            "Name it (the pilgrimage, the animal, the work, the formula).",
        ),
        ({}, _plan("tame_animal", title="Wolf"), "Type the animal's Might."),
        (
            {},
            _plan("record_lectures"),
            "Choose the teacher whose lectures are recorded.",
        ),
        ({}, _plan("inspeximus"), "Choose the summa to annotate."),
        (
            {},
            _plan("bind_catalog"),
            "Binding the catalog takes 1 pawn of Vim; Wulf has none.",
        ),
    ],
)
def test_what_stops_a_supplement_season(changes, plan, problem):
    saga = _with(**changes)
    assert sw.problems(saga, saga.character("c"), plan) == [problem]


def _work(saga, plan, rng=None):
    wulf = saga.character("c")
    assert sw.problems(saga, wulf, plan) == []
    return sw.work(saga, wulf, plan, rng)


def test_an_inspeximus_annotates_only_the_authors_own_summa():
    saga = _saga()
    saga.books.append(
        Book(
            id="b",
            name="Of Smiths",
            type="Ability Summa",
            ability="Craft: Smith",
            level=2,
            quality=8,
            author="Someone",
        )
    )
    plan = _plan("inspeximus", book_id="b")
    assert sw.problems(saga, saga.character("c"), plan) == [
        "An inspeximus annotates the author's own summa."
    ]
    saga.books[0].author = "Wulf"
    # Craft 6 now against 4 then (Level 2 x 2): +2 / 3 -> 0.
    assert _work(saga, plan).summa_level == ("b", 2)
    # Written at score 0: +6 / 3 = 2 -> 4, capped at half of 6: 3.
    then = _plan("inspeximus", book_id="b", book_level=0)
    assert _work(saga, then).summa_level == ("b", 3)


def test_labor_point_seasons_use_their_characteristic():
    saga = _saga()
    assert _work(saga, _plan("tournament", "ability:Animal Handling")).notes == [
        "Labor Points: (Dexterity + Animal Handling) x 3 (average) = 18."
    ]
    scribe = _work(saga, _plan("working_season", "ability:Profession: Scribe"))
    assert scribe.labor_points == 3  # Communication 1 + Scribe 0, x 3


def test_workshop_exertion_is_rolled_when_played():
    saga = _saga()
    pending = _work(saga, _plan("workshop_production", experimenting=True))
    assert (
        pending.notes[0] == "Exertion: its dice are rolled when the season is played."
    )
    assert not pending.aging_roll
    rolled = _work(
        saga, _plan("workshop_production", experimenting=True), random.Random(7)
    )
    assert rolled.aging_roll
    assert rolled.notes == [
        "Exertion: + simple die 5; the exertion roll 2: no special result. An Aging "
        "roll this season.",
        "Workshop Total 13 against Craft Level 6: Superior goods. Labor Points 24.",
    ]


def test_a_craft_manual_needs_artes_liberales():
    saga = _saga()
    wulf = saga.character("c")
    assert wulf is not None
    wulf.abilities = [a for a in wulf.abilities if a.name != "Artes Liberales"]
    work = _work(saga, _plan("workshop_production", quick=True))
    assert work.notes[-1] == "No craft manual: it needs Artes Liberales 1."
    assert (work.books, work.labor_points) == ([], 24)


def test_excellent_items_ventures_remedies_and_medicine():
    saga = _saga()
    item = _work(saga, _plan("make_excellent_item", title="Sword"))
    assert item.progress == [("item", "Sword", 15, 0)]
    assert _work(saga, _plan("merchant_venture", other_modifier=12)).labor_points == 12
    remedies = _work(saga, _plan("produce_remedies", book_level=12, extra_vis=3))
    assert remedies.labor_points == -8  # 12 x 3 / 5 = 7.2, rounded up
    assert "Can care for 0 patients" in _work(saga, _plan("medical_season")).notes[0]


def test_improving_raw_materials():
    work = _work(
        _with(labor_points=500), _plan("improve_workshop", title="Raw Materials")
    )
    assert (work.labor_points, work.raw_materials) == (-50, 1)


def test_a_work_of_art_takes_a_season_per_ten_aesthetic_quality():
    saga = _saga()
    assert _work(saga, _plan("create_art", title="Gate")).progress == [
        ("artwork", "Gate", 1, 1)
    ]
    ode = _work(saga, _plan("create_art", "ability:Craft: Poetry", title="Ode"))
    assert ode.notes == ["Aesthetic Quality 1; 1 season(s) to make it."]  # Com 1
    inspired = _with(virtues_flaws=[VirtueFlawInstance("vf_free_expression")])
    assert _work(inspired, _plan("create_art", title="Gate")).progress == [
        ("artwork", "Gate", 2, 1)  # Dex 2 + Smith 6 + 3 = 11
    ]


def test_a_formula_researched_with_the_storyguides_quality():
    work = _work(_saga(), _plan("research_formula", title="Theriac", source_quality=3))
    assert work.progress == [("formula", "Theriac", 5, 3)]


def test_university_exams():
    saga = _with(reputations=[ScoredTrait("Academic", 2)])
    assert _work(saga, _plan("attend_university")).notes == []
    pending = _work(saga, _plan("attend_university", title="Baccalaureus"))
    assert pending.notes == [
        "The baccalaureus exam is rolled when the season is played."
    ]
    doctor = _work(
        saga,
        _plan("attend_university", "ability:Theology", title="Doctor"),
        random.Random(4),
    )
    assert doctor.notes == [
        "The doctor exam: 6 against 12: failed (another year first)."
    ]


def test_pilgrimage_care_of_souls_and_taming():
    saga = _saga()
    rome = _work(
        saga, _plan("pilgrimage", title="Rome", book_level=30, other_modifier=2)
    )
    assert rome.progress == [("pilgrimage", "Rome", 30, 5)]
    # A Target Level other than 18 or 30 is taken as 18.
    other = _work(saga, _plan("pilgrimage", title="Rome", book_level=12))
    assert other.progress == [("pilgrimage", "Rome", 18, 3)]
    souls = _work(saga, _plan("care_of_souls"))
    assert "fitting the sermons' theme" in souls.notes[0]
    wolf = _work(saga, _plan("tame_animal", title="Wolf", book_level=3))
    assert wolf.progress == [("taming", "Wolf", 3, 1)]  # Int 0 + Handling 4 - 3
    gifted = _with(virtues_flaws=[VirtueFlawInstance("vf_the_gift")])
    tamed = _work(gifted, _plan("tame_animal", title="Wolf", book_level=3))
    assert tamed.progress == [("taming", "Wolf", 3, 0)]


def test_searching_for_lacunae():
    saga = _saga()
    assert _work(saga, _plan("search_lacuna")).notes == [
        "The search is rolled when the season is played."
    ]
    assert _work(saga, _plan("search_lacuna", die=6)).notes == [
        "Int + Area Lore + die = 6 against 9: none found."
    ]


def test_initiation_against_the_target_less_a_past_ordeal():
    saga = _saga()
    wulf = saga.character("c")
    assert wulf is not None
    wulf.characteristics.presence = 3
    wulf.abilities.append(Ability("Mithraic Lore", xp=ability_xp(5)))
    plan = _plan(
        "undergo_initiation",
        effect_id="vf_puissant_ability",
        effect_params={"ability": "Penetration"},
        teacher_id="c",
        title="Mithraic Lore",
        other_modifier=12,
        device_id="vf_deficient_technique",
        ordeal_params={"technique": "Creo"},
        research_kind="Medium",
    )
    done = _work(saga, plan)
    assert (done.add_vfs, done.ordeal) == (
        [
            VirtueFlawInstance("vf_puissant_ability", {"ability": "Penetration"}),
            VirtueFlawInstance("vf_deficient_technique", {"technique": "Creo"}),
        ],
        "Medium",
    )
    assert not sw.problems(saga, wulf, plan)
    plan.other_modifier = 0
    assert _work(saga, plan).notes[-1].endswith("against 18: not initiated.")
    wulf.ordeals = [Ordeal("Major", 1)]
    assert _work(saga, plan).notes[-1].endswith("against 12: not initiated.")


def test_binding_a_catalog():
    saga = _with(raw_vis={"vim": 2})
    assert "Arcane Connection" in _work(saga, _plan("bind_catalog")).notes[0]
