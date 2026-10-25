"""Covenants, the mundane books and the Tribunal packs: the leftovers of
the rules audit (fixed xp, realia, wondrous items, regimens and eucrasia,
lords and battles, Grogs' creation rules, Thebes' reparations,
Transylvania's privileges and Decorations, Sap the Life, the Tourney's
points and Hibernia's seven days)."""

from __future__ import annotations

import random

import pytest
from support import everything_saga, literate

from ars_magica_manager import (
    aging_chart,
    armies,
    battles,
    book_kinds,
    book_value,
    inhabitants,
    lords,
    meeting,
    sourcebooks,
    theban_meeting,
)
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.models import (
    Ability,
    Battle,
    BattleEvent,
    BattleSide,
    Book,
    Character,
    Covenant,
    Neighbour,
    Saga,
    ScoredTrait,
    SeasonPlan,
    VirtueFlawInstance,
    XpAllocation,
)
from ars_magica_manager.rules import (
    activities,
    battle,
    covenfolk,
    creation_packages,
    disease,
    harm,
    library,
    medicine,
    options,
    supplement_work,
)
from ars_magica_manager.rules.xp import ability_xp, art_xp
from ars_magica_manager.seasons import advance
from ars_magica_manager.tribunal_packages import normandy, theban, transylvania


def _vf(vf_id: str, **params: str) -> VirtueFlawInstance:
    return VirtueFlawInstance(vf_id, dict(params))


# -- fixed xp: correspondence and a folio's Order of Hermes Lore ----------


def _library_saga() -> Saga:
    return Saga(
        id="s",
        name="Saga",
        covenants=[Covenant("cov", "Keep", "s")],
        characters=[
            Character(
                id="ana",
                name="Ana",
                type="companion",
                covenant_id="cov",
                abilities=[Ability("Philosophiae"), *literate()],
            )
        ],
        books=[
            Book(
                id="physics",
                name="Physics",
                type="Ability Summa",
                ability="Philosophiae",
                level=6,
                quality=12,
                owner_kind="covenant",
                owner_id="cov",
            )
        ],
    )


def test_correspondence_is_a_fixed_xp_no_affinity_multiplies():
    saga = _library_saga()
    ana = saga.characters[0]
    ana.virtues_flaws = [_vf("vf_affinity_with_ability", ability="medicine")]
    plan = SeasonPlan("ana", 1220, "Spring", activities.READ, book_id="physics")
    plan.correspondence = "ability:Medicine"
    outcome = activities.outcome(ana, plan, saga)
    letters = next(g for g in outcome.gains if g.subject == "ability:Medicine")
    assert letters.result.xp == 1
    assert letters.via == "Useful correspondence"


def test_a_folios_lore_point_is_fixed_and_outside_master_of_none():
    saga = _library_saga()
    saga.books.append(
        Book(
            id="t",
            name="T",
            type="Tractatus",
            subject_kind="Ability",
            ability="Medicine",
            quality=8,
            owner_kind="covenant",
            owner_id="cov",
            codex_id="folio",
        )
    )
    from ars_magica_manager.models import Codex

    saga.codices = [Codex("folio", "Folio", collection=book_kinds.FOLIO)]
    ana = saga.characters[0]
    ana.virtues_flaws = [
        _vf("vf_affinity_with_ability", ability="organization lore: order of hermes")
    ]
    plan = SeasonPlan("ana", 1220, "Spring", activities.READ, book_id="t")
    gains = activities.outcome(ana, plan, saga).gains
    lore = next(g for g in gains if g.subject.endswith(book_kinds.FOLIO_LORE))
    assert (lore.result.xp, bool(lore.via)) == (1, True)


# -- realia --------------------------------------------------------------


def _realia(quality: int = 2, book_id: str = "bones", **kwargs) -> Book:
    return Book(
        id=book_id,
        name="Bones",
        type="Tractatus",
        subject_kind="Ability",
        ability="Medicine",
        quality=quality,
        opus=book_kinds.REALIA,
        owner_kind="covenant",
        owner_id="cov",
        **kwargs,
    )


def test_realia_quality_and_cost_follow_the_pieces():
    assert [book_kinds.realia_quality(n) for n in (0, 1, 2, 3, 4, 31, 32)] == [
        0,
        1,
        2,
        2,
        3,
        5,
        6,
    ]
    assert [book_kinds.realia_cost(q) for q in range(1, 7)] == [1, 3, 6, 10, 15, 21]
    assert library.cost(_realia(4)) == 10
    assert [book_kinds.realia_sharing_penalty(n) for n in (1, 2, 3, 4, 5, 8, 9)] == [
        0,
        1,
        2,
        2,
        3,
        3,
        4,
    ]


def test_a_realia_is_studied_as_often_as_its_quality_and_shared():
    saga = _library_saga()
    saga.books = [_realia(2)]
    ana = saga.characters[0]
    plan = SeasonPlan("ana", 1220, "Spring", activities.READ, book_id="bones")
    saga.season_plans.append(plan)
    first = activities.outcome(ana, plan, saga)
    assert not first.problems and first.realia
    advance.apply(saga, [first])
    assert ana.tractatus_read == ["bones"]
    again = SeasonPlan("ana", 1220, "Summer", activities.READ, book_id="bones")
    second = activities.outcome(ana, again, saga)
    assert not second.problems
    advance.apply(saga, [second])
    third = SeasonPlan("ana", 1220, "Autumn", activities.READ, book_id="bones")
    assert any("as many times as its Quality" in p for p in activities.problems(
        ana, third, saga))  # fmt: skip
    # Two readers in one season split it: -1 Quality.
    saga.characters.append(
        Character(
            id="bo",
            name="Bo",
            type="companion",
            covenant_id="cov",
            abilities=list(literate()),
        )
    )
    ana.tractatus_read = []
    mine = SeasonPlan("ana", 1221, "Spring", activities.READ, book_id="bones")
    theirs = SeasonPlan("bo", 1221, "Spring", activities.READ, book_id="bones")
    saga.season_plans = [mine, theirs]
    shared = activities.outcome(ana, mine, saga)
    assert not shared.problems
    assert shared.gains[0].result.advancement_total == 1


def test_realia_and_correspondence_stack_only_by_house_rule():
    saga = _library_saga()
    covenant = saga.covenants[0]
    saga.books = [
        _realia(3),
        Book(
            id="letters",
            name="Letters",
            type="Tractatus",
            subject_kind="Ability",
            ability="Medicine",
            quality=6,
            opus=book_kinds.EXPERT_CORRESPONDENCE,
            owner_kind="covenant",
            owner_id="cov",
        ),
        _realia(2, "more"),
    ]
    # The book doesn't say they stack: together they add one.
    assert book_value.library_level(saga, covenant, "Medicine") == 1
    saga.rule_options[options.RESEARCH_AIDS_STACK] = True
    assert book_value.library_level(saga, covenant, "Medicine") == 2


def test_a_realia_exhibit_on_an_art_meets_study_requirement_below_fifteen():
    saga = _library_saga()
    magus = Character(
        id="mag",
        name="Mag",
        type="magus",
        covenant_id="cov",
        abilities=list(literate()),
        virtues_flaws=[_vf("vf_study_requirement")],
    )
    saga.characters.append(magus)
    saga.books = [
        Book(
            id="ex",
            name="Corpus exhibit",
            type="Tractatus",
            subject_kind="Art",
            art="Corpus",
            quality=8,
            opus=book_kinds.REALIA,
            owner_kind="covenant",
            owner_id="cov",
        )
    ]
    plan = SeasonPlan("mag", 1220, "Spring", activities.READ, book_id="ex")
    # Only an exhibit of hundreds of objects counts (Against the Dark p. 61).
    assert any("Study Requirement" in p for p in activities.problems(magus, plan, saga))
    saga.books[0].exhibit = True
    assert not any(
        "Study Requirement" in p for p in activities.problems(magus, plan, saga)
    )
    from ars_magica_manager.models import ArtScore

    magus.arts["corpus"] = ArtScore(xp=art_xp(15))
    assert any("Study Requirement" in p for p in activities.problems(magus, plan, saga))


# -- wondrous items -------------------------------------------------------


def _craftsman(realm: str = "Faerie") -> tuple[Saga, Character]:
    saga = _library_saga()
    saga.covenants[0].aura = 4
    saga.covenants[0].aura_realm = "Magic"
    smith = Character(
        id="smith",
        name="Smith",
        type="companion",
        covenant_id="cov",
        abilities=[Ability("Craft: Smith", xp=ability_xp(6))],
        virtues_flaws=[_vf("vf_touched_by_realm", realm=realm)],
    )
    saga.characters.append(smith)
    return saga, smith


def _wondrous(**kwargs) -> SeasonPlan:
    return SeasonPlan(
        "smith",
        1220,
        "Spring",
        "make_wondrous_item",
        title="Ring",
        allocations=[XpAllocation("ability:Craft: Smith")],
        book_level=15,
        **({"site_aura": 4, "site_realm": "Magic"} | kwargs),
    )


def test_a_wondrous_items_total_takes_the_aura_and_one_assistants_help():
    saga, smith = _craftsman("Faerie")
    # The workshop's aura, not the covenant's (City & Guild p. 72).
    assert supplement_work.wondrous_aura(smith, _wondrous()) == 2  # Faerie in Magic
    assert supplement_work.wondrous_aura(smith, _wondrous(site_aura=None)) == 0
    helper = Character(
        id="help",
        name="Help",
        type="grog",
        covenant_id="cov",
        abilities=[Ability("Craft: Smith", xp=ability_xp(5))],
    )
    saga.characters.append(helper)
    work = supplement_work.work(saga, smith, _wondrous(teacher_id="help"), None)
    assert any("aura +2" in n and "Help's help +2" in n for n in work.notes)
    divine, smith = _craftsman("Divine")
    assert supplement_work.wondrous_aura(smith, _wondrous()) == 0
    # Touched by (Realm) names one of the four realms (p. 71).
    smith.virtues_flaws = [_vf("vf_touched_by_realm", realm="Storms")]
    assert "Name the realm" in supplement_work.problems(divine, smith, _wondrous())[0]
    assert supplement_work.problems(saga, saga.character("smith"), _wondrous(
        teacher_id="smith")) == ["The assistant is someone other than the craftsman."]  # fmt: skip


def test_a_mythic_farrier_makes_wondrous_horseshoes():
    saga, smith = _craftsman()
    smith.virtues_flaws = [_vf("vf_mythic_farrier")]
    # No realm by default: most likely Magic or Faerie (Grogs p. 76).
    assert "Name the realm" in supplement_work.problems(saga, smith, _wondrous())[0]
    smith.virtues_flaws = [_vf("vf_mythic_farrier", realm="Faerie")]
    assert supplement_work.problems(saga, smith, _wondrous()) == []
    assert supplement_work.problems(saga, smith, _wondrous(characteristic="presence"))
    work = supplement_work.work(saga, smith, _wondrous(), None)
    assert any("horseshoes only" in n for n in work.notes)


# -- regimens and eucrasia ------------------------------------------------


def _regimen_saga() -> Saga:
    saga = everything_saga()
    covenant = Covenant("cov", "Keep", "s", covenant_season="Spring")
    saga.covenants = [covenant]
    doctor = Character(
        id="doc",
        name="Doc",
        type="companion",
        covenant_id="cov",
        abilities=[
            Ability("Medicine", xp=ability_xp(4)),
            Ability("Chirurgy", xp=ability_xp(3)),
        ],
    )
    patients = [
        Character(id=f"p{n}", name=f"P{n}", type="companion", covenant_id="cov")
        for n in range(2)
    ]
    for patient in patients:
        patient.aging.regimen = 2
        patient.aging.regimen_by = "doc"
        patient.aging.regimen_since = 1200
    saga.characters = [doctor, *patients]
    return saga


def test_a_regimen_multiplies_its_patients_inhabitant_points():
    saga = _regimen_saga()
    covenant = saga.covenants[0]
    # Two companions at 0 raised to +2: 6 -> 9 -> 18 (A&A p. 58's example).
    start = [living for living in (0,)]
    assert start == [0]
    assert covenfolk.regimen_points(saga, covenant) == 12
    covenant.economics.emergency_savings = 10
    assert covenfolk.regimen_points(saga, covenant) == 0
    assert any(
        "Emergency Savings" in p
        for p in medicine.regimen_problems(saga, saga.character("p0"))
    )


def test_eucrasia_is_lost_to_a_season_convalescing_and_a_disease():
    saga = _regimen_saga()
    patient = saga.character("p0")
    note = medicine.lose_eucrasia(patient, 1225, "a season convalescing")
    assert patient.aging.regimen_since == 1225 and "from 1226" in note
    assert medicine.lose_eucrasia(saga.character("doc"), 1225, "x") == ""
    saga.current_year = 1230
    done = harm.catch_disease(
        saga, patient, {"aa_disease": "Sap the Life"}, random.Random(1)
    )
    assert any("no Disease Avoidance" in line for line in done.lines)
    assert patient.long_term_fatigue == 2
    assert patient.wounds.diseases[-1].name == "Sap the Life"
    assert patient.aging.regimen_since == 1230


def test_sap_the_life_is_a_serious_disease_of_severity_15():
    sap = disease.CATALOG_BY_NAME["Sap the Life"]
    assert (sap.level, sap.severity, sap.stable, sap.improve) == ("Serious", 15, 12, 18)
    assert not sap.avoidable and sap.fatigue == 2


# -- lords and battles ----------------------------------------------------


def _lord(title: str, wealth: str) -> Neighbour:
    return Neighbour(
        id="l", name="Lord", kind="lord", details={"title": title, "wealth": wealth}
    )


def test_the_mercenary_budget_and_free_seasons_name_their_book():
    assert lords.budget_text(_lord("duke", "Wealthy")) == "500+ pounds a year"
    assert lords.budget_text(_lord("baron", "Average")) == "40 pounds a year"
    facts = {
        f.label: f.value for f in lords.facts(Saga("s", "S"), _lord("landed", "Poor"))
    }
    assert facts["Mercenary budget"] == "0 pounds a year"
    assert "Lords of Men p. 31" in facts["Free time"]


def test_levies_are_raised_only_on_home_ground():
    lord = _lord("landed", "Wealthy")
    assert armies.army_groups(lord) == 22
    assert armies.army_groups(lord, at_home=False) == 12


def test_a_rout_after_a_failed_rally_ends_the_battle():
    assert battle.morale_result(None, None) == ""
    assert battle.morale_result(7, None) == battle.HOLDS
    assert battle.morale_result(4, None) == battle.WAVERS
    assert battle.morale_result(4, 10) == battle.RALLIES
    assert battle.morale_result(4, 5) == battle.ROUTS
    entry = Battle(
        "Ford",
        sides=[BattleSide("Ours", groups=10), BattleSide("Theirs", groups=10)],
        events=[BattleEvent("x", 0, won=True, morale=3, rally=2)],
    )
    assert battles.routed(entry) == 1
    assert isinstance(battles.event_form(Saga("s", "S"), entry), Refuse)


# -- Grogs and creation ---------------------------------------------------


def test_the_grogs_aging_chart_is_offered_to_companions_too():
    saga = Saga("s", "S", current_year=1220)
    saga.books_in_play = [*sourcebooks.SOURCEBOOKS]
    old = Character(id="c", name="Old", type="companion")
    old.background.year_born = 1170
    assert aging_chart.offered(saga, old)
    old.type = "magus"
    assert not aging_chart.offered(saga, old)


def test_a_jurist_needs_no_academic_virtue_for_the_advocate_package():
    saga = Saga("s", "S", current_year=1220)
    lawyer = Character(id="j", name="Jurist", type="companion")
    lawyer.background.year_born = 1190
    lawyer.virtues_flaws = [_vf("vf_jurist")]
    from ars_magica_manager.models import CreationXp

    lawyer.creation_xp = [
        CreationXp("package", "Civil and Canon Law", 40, note="Advocate:5:1")
    ]
    checks = creation_packages.package_checks(saga, lawyer)
    needs = next(c for c in checks if "Academic" in c.label)
    assert needs.status == "pass" and "Jurist" in needs.detail


def test_a_grogs_loyal_toward_a_gifted_magus():
    grog = Character(
        id="g",
        name="G",
        type="grog",
        personality_traits=[
            ScoredTrait("Loyal to Covenant", 2),
            ScoredTrait("Loyal to Tillitus", 3),
        ],
    )
    tillitus = Character(id="t", name="Tillitus", type="magus")
    other = Character(id="o", name="Other", type="magus")
    assert inhabitants.loyal_toward(grog, tillitus)[0] == 0
    assert inhabitants.loyal_toward(grog, other)[0] == -1


def test_the_core_house_rules_say_they_are_house_rules():
    assert "(house rules)" in options.SOURCE


# -- Thebes: a contrition's reparation ------------------------------------


def _values(form: Form, **changes):
    values = {f.key: f.value for f in form.fields() if f.kind != "info"}
    values.update(changes)
    return values


def _save(form, **changes):
    assert isinstance(form, Form)
    values = _values(form, **changes)
    assert form.validate is None or form.validate(values) is None
    form.apply(values)


@pytest.fixture
def _seeded(monkeypatch):
    monkeypatch.setattr(meeting, "rng", lambda: random.Random(7))


def test_a_reparations_vis_goes_from_the_penitent_to_the_treasury(_seeded):
    saga = everything_saga()
    thebes = saga.tribunal("thebes")
    assert thebes is not None
    for covenant in saga.covenants:
        covenant.tribunal_id = "thebes"
    penitent = Character(id="pen", name="Penitent", type="magus")
    penitent.covenant_id = saga.covenants[0].id
    penitent.raw_vis = {"vim": 5}
    saga.characters.append(penitent)
    theban.magi(thebes).append({"character_id": "pen", "shards": 1})
    _save(meeting.hold(saga, thebes))
    step = next(s for s in meeting.steps(thebes, thebes.meeting) if s.key == "assembly")
    _save(
        meeting.step_form(saga, thebes, step),
        contrition_pen=True,
        reparation_pen="a summa on Corpus",
        reparation_pawns_pen=7,
        reparation_art_pen="Vim",
    )
    assert penitent.raw_vis == {}
    paid = [t for t in thebes.treasury if t.who == "Penitent"]
    assert [(t.kind, t.amount, t.art) for t in paid] == [("vis", 5, "Vim")]
    words = theban_meeting.reparation_text(
        thebes.meeting["theban"]["assembly"]["reparations"]["pen"]
    )
    assert (
        words
        == "a summa on Corpus and 5 pawns of Vim (2 of the pawns offered he hadn't)"
    )
    # Holding the step again gives the vis back first.
    _save(meeting.step_form(saga, thebes, step), contrition_pen=False)
    assert penitent.raw_vis == {"vim": 5}
    assert not [t for t in thebes.treasury if t.who == "Penitent"]


# -- Transylvania: privileges' terms and Decorations ----------------------


def test_a_lower_decoration_never_replaces_a_higher():
    assert transylvania.decoration_problem("Myrtle", "Parsley") is not None
    assert transylvania.decoration_problem("Parsley", "Myrtle") is None
    assert transylvania.decoration_problem("", "Grass") is None


def test_a_privileges_other_terms_are_noted():
    saga = Saga("s", "S")
    hospes = Character(id="h", name="H", type="magus")
    notes = transylvania.terms_notes(saga, hospes, "hospites")
    assert any("binding a familiar" in n for n in notes)
    assert any(
        "archmagus" in n for n in transylvania.terms_notes(saga, hospes, "coloniae")
    )
    words, refuses = transylvania.office_rule("cives", transylvania.CURATOR)
    assert not refuses and "vote of the Tribunal" in words and "master" in words


# -- Normandy and Hibernia ------------------------------------------------


def test_the_tourneys_points_come_from_each_events_placing():
    assert normandy.event_points("certamen", "winner") == 26
    assert normandy.event_points("melee", "fifth") == 1
    assert normandy.event_points("melee", normandy.ENTERED) == 0
    assert normandy.event_points("joust", normandy.ENTERED) == 1
    assert normandy.event_points("joust", "") == 0
    result = {"points": 5, "events": {"hastiludium": "finalist", "host": "second"}}
    assert normandy.total_points(result) == 5 + 11 + 9


def test_a_hibernian_meeting_lasts_seven_days():
    saga = everything_saga()
    tribunal = saga.tribunals[0]
    tribunal.package = "hibernia"
    assert meeting.days(meeting.record(saga, tribunal)) == 7
    tribunal.package = ""
    assert meeting.days(meeting.record(saga, tribunal)) == meeting.DEFAULT_DAYS
