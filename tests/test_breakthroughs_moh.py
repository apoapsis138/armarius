"""Magi of Hermes' and Legends of Hermes' breakthroughs: a fertile
Longevity Ritual (MoH p. 20), Hermetic Metamorphosis (MoH pp. 82-84),
Exciting Experimentation (MoH p. 26, Errata p. 12) and Hermetic
Viresculture (LoH pp. 72-76)."""

from __future__ import annotations

import random

import pytest

from ars_magica_manager import catalog
from ars_magica_manager.forms import lab_plan
from ars_magica_manager.forms import season as season_forms
from ars_magica_manager.forms import viresculture_seasons as vires_forms
from ars_magica_manager.models import (
    TEXT_LONGEVITY,
    Ability,
    ArtScore,
    Book,
    Breakthrough,
    Character,
    Characteristics,
    Covenant,
    Laboratory,
    Progress,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import breakthroughs_moh as moh
from ars_magica_manager.rules import (
    casting_virtues,
    experiment,
    integrations,
    lab_seasons,
)
from ars_magica_manager.rules import viresculture as vc
from ars_magica_manager.rules.activities import ACTIVITIES
from ars_magica_manager.rules.season_work import REGISTRY, SupplementWork
from ars_magica_manager.rules.xp import ability_xp, art_xp
from ars_magica_manager.seasons.lab_apply import apply_supplement


def _saga(*, vires: int = 4, lab: bool = True) -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep")
    magus = Character(id="m", name="Elaine", type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(intelligence=2)
    magus.abilities = [Ability("Magic Theory", xp=ability_xp(3))]
    if vires:
        magus.abilities.append(Ability(vc.ABILITY, xp=ability_xp(vires)))
    magus.arts = {
        "creo": ArtScore(xp=art_xp(5)),
        "vim": ArtScore(xp=art_xp(4)),
        "corpus": ArtScore(xp=art_xp(3)),
        "animal": ArtScore(xp=art_xp(6)),
    }
    magus.background.year_born = 1195
    magus.raw_vis = {"creo": 8}
    labs = []
    if lab:
        magus.assigned_lab_id = "lab"
        labs = [Laboratory(id="lab", covenant_id="cov", name="Tower", owner_id="m")]
    return Saga(
        id="s", name="S", covenants=[covenant], characters=[magus], laboratories=labs
    )


# -- the breakthroughs as data --------------------------------------------


@pytest.mark.parametrize(
    ("name", "kind", "target", "grant_kind", "grant"),
    [
        ("Fertile Longevity Ritual", "Minor", 30, "", ""),
        ("Hermetic Metamorphosis", "Major", 45, "Virtue", "vf_hermetic_metamorphosis"),
        ("Hermetic Viresculture", "Major", 45, "Ability", "Hermetic Viresculture"),
        ("Viresculture of Lesser Enchantment Vis", "Minor", 30, "", ""),
    ],
)
def test_the_books_breakthroughs_are_goals_to_choose(
    name: str, kind: str, target: int, grant_kind: str, grant: str
) -> None:
    known = integrations.BY_NAME[name]
    assert (known.kind, known.target, known.grant_kind, known.grant) == (
        kind,
        target,
        grant_kind,
        grant,
    )
    assert known.learned


def test_what_they_grant_is_in_the_catalogs() -> None:
    virtue = catalog.load_virtue_flaw_catalog_by_id()[moh.METAMORPHOSIS_VIRTUE]
    assert (virtue.type, virtue.tier, virtue.source) == ("Virtue", "Minor", "MoH")
    assert any(
        a.name == vc.ABILITY and a.category == "Supernatural"
        for a in catalog.load_ability_catalog()
    )


# -- a fertile Longevity Ritual -------------------------------------------


def _longevity(saga: Saga) -> lab_seasons.LabWork:
    plan = SeasonPlan(
        "m", 1220, "Spring", lab_seasons.LONGEVITY, lab_id="lab", vis_art="Creo"
    )
    found, work = lab_seasons.work(saga, saga.character("m"), plan)
    assert found == [] and work is not None
    return work


def test_a_longevity_ritual_leaves_its_subject_sterile() -> None:
    work = _longevity(_saga())
    assert "Elaine permanently sterile (DE p. 261" in " ".join(work.notes)


def test_the_breakthrough_leaves_the_subject_fertile() -> None:
    saga = _saga()
    magus = saga.character("m")
    assert magus is not None
    magus.breakthroughs.append(
        Breakthrough(moh.FERTILE_LONGEVITY, points=30, reached=True)
    )
    assert moh.leaves_fertile(magus)
    assert "leaves Elaine fertile" in " ".join(_longevity(saga).notes)
    # A goal still being researched doesn't.
    magus.breakthroughs[0].reached = False
    assert not moh.leaves_fertile(magus)


def test_a_lab_text_using_the_breakthrough_makes_a_fertile_ritual() -> None:
    # Any Hermetic magus with a Lab Text using a Minor Breakthrough can
    # use it (DE p. 281); the plan says the ritual is made from one.
    saga = _saga()
    magus = saga.character("m")
    assert magus is not None
    assert moh.leaves_fertile(magus, from_lab_text=True)
    plan = SeasonPlan(
        "m",
        1220,
        "Spring",
        lab_seasons.LONGEVITY,
        lab_id="lab",
        vis_art="Creo",
        fertile_text=True,
    )
    found, work = lab_seasons.work(saga, magus, plan)
    assert found == [] and work is not None
    assert "leaves Elaine fertile" in " ".join(work.notes)


def test_the_lab_plan_asks_whether_the_ritual_is_fertile() -> None:
    saga = _saga()
    magus = saga.character("m")
    assert magus is not None and saga.laboratories
    form = lab_plan.LabPlanForm(saga, magus, saga.laboratories[0], "Spring", 1220, None)
    tick = next(f for f in form.fields() if f.key == "fertile_text")
    assert "No Longevity Lab Text at hand" in tick.hint
    values = {
        "activity": lab_seasons.LONGEVITY,
        "subject": "m",
        "longevity_vis": "Creo",
        "fertile_text": True,
    }
    assert form.plan_of(values).fertile_text
    # A magus who reached the breakthrough isn't asked.
    magus.breakthroughs.append(
        Breakthrough(moh.FERTILE_LONGEVITY, points=30, reached=True)
    )
    form = lab_plan.LabPlanForm(saga, magus, saga.laboratories[0], "Spring", 1220, None)
    assert "fertile_text" not in {f.key for f in form.fields()}


def test_the_longevity_texts_at_hand() -> None:
    saga = _saga()
    magus = saga.character("m")
    assert magus is not None
    saga.books.append(
        Book(
            id="b",
            name="Aurulentus' ritual",
            type="Lab Text",
            text_kind=TEXT_LONGEVITY,
            owner_kind="covenant",
            owner_id="cov",
        )
    )
    assert [b.id for b in lab_seasons.longevity_texts_at_hand(saga, magus)] == ["b"]


# -- Hermetic Metamorphosis -----------------------------------------------


def test_the_surgery_ease_factor() -> None:
    assert moh.surgery_ease() == 9
    assert moh.surgery_ease(transposed=True) == 12
    # The book's eagle's head on a lion: a Virtue (Keen Vision) given.
    assert moh.surgery_ease(grants_virtue=True) == 12
    assert moh.surgery_ease(transposed=True, grants_virtue=True) == 15


def test_the_surgery_roll() -> None:
    assert "graft takes" in moh.surgery_outcome(12, 12)
    assert "animal dies" in moh.surgery_outcome(11, 12)
    assert "monster" in moh.surgery_outcome(20, 9, botched=True)


def test_a_holder_is_reminded_of_the_surgery() -> None:
    magus = Character(id="m", name="Marcus", type="magus")
    assert not any("Metamorphosis" in r for r in casting_virtues.reminders(magus))
    magus.virtues_flaws.append(VirtueFlawInstance(moh.METAMORPHOSIS_VIRTUE))
    text = " ".join(casting_virtues.reminders(magus))
    assert "Dexterity + Chirurgy against 9, +3" in text


# -- Exciting Experimentation ---------------------------------------------


def test_exciting_experimentation_rolls_every_table_twice() -> None:
    assert "vf_exciting_experimentation" in experiment.TWO_DICE
    magus = Character(id="m", name="Conscientia", type="magus")
    assert (
        experiment.chart(random.Random(3), 1, 0, "Creo", character=magus).other is None
    )
    magus.virtues_flaws.append(VirtueFlawInstance("vf_exciting_experimentation"))
    rolled = experiment.chart(random.Random(3), 1, 0, "Creo", character=magus)
    assert rolled.other is not None
    assert "storyguide chooses" in " ".join(rolled.results)


# -- Hermetic Viresculture: the rules --------------------------------------


def test_the_vitalization_total_uses_viresculture_for_magic_theory() -> None:
    for with_lab in (True, False):
        saga = _saga(lab=with_lab)
        magus = saga.character("m")
        assert magus is not None
        # Int 2 + Creo 5 + Vim 4 + Viresculture 4 (+ aura 0).
        assert vc.vitalization_total(saga, magus).total == 15


def test_the_invigoration_total_counts_the_lower_of_form_and_vim() -> None:
    saga = _saga()
    magus = saga.character("m")
    assert magus is not None
    # Animal 6 is above Vim 4: the requisite counts.
    assert vc.requisite_form(magus, "Animal") == "Vim"
    assert vc.invigoration_total(saga, magus, "Animal").total == 15
    # Corpus 3 is the lower.
    assert vc.requisite_form(magus, "Corpus") == "Corpus"
    assert vc.invigoration_total(saga, magus, "Corpus").total == 14


def test_vitalizing_points_and_vis() -> None:
    assert vc.vitalization_points(41, 10) == 31
    assert vc.vitalization_points(8, 10) == 0
    assert vc.vitalization_vis(10) == 1
    assert vc.vitalization_vis(11) == 2
    assert vc.vitalization_vis(0) == 0


def test_breeding_seasons_and_yields_follow_the_examples() -> None:
    # Elaine's 43 shared between two roosters: 22 each, three seasons.
    assert vc.breeding_seasons(22) == 3
    assert vc.breeding_seasons(0) == 0
    # A Might 10 rooster: two pawns; a level 25 wheat: five; Might 15: three.
    assert [vc.pawns_per_breeding(m) for m in (10, 25, 15)] == [2, 5, 3]


def test_a_harvest_short_of_labor_or_attention() -> None:
    # The example's second year: three roosters, 30 Labor Points of 36.
    assert vc.labor_needed(3) == 36
    assert vc.harvest(6, 3, 30) == 5
    assert vc.harvest(6, 3, 23) == 3  # 13 short: three pawns
    assert vc.harvest(6, 3, 36, neglected_months=2) == 4
    assert vc.harvest(1, 3, 0) == 0


def test_tending_harvested_auras_and_new_stirpes() -> None:
    saga = _saga(vires=2)
    magus = saga.character("m")
    assert magus is not None
    assert vc.tended(magus, 5) == 2
    assert vc.aura_drain(9) == 2
    assert vc.aura_drain(0) == 0
    found = vc.roll_stirpes(random.Random(1), 100)
    assert 0 < found < 30


# -- Hermetic Viresculture: the seasons -------------------------------------


def _plan(
    activity: str, title: str = "", book_level: int | None = None, form: str = ""
) -> SeasonPlan:
    return SeasonPlan(
        "m", 1220, "Spring", activity, title=title, book_level=book_level, form=form
    )


def test_the_seasons_are_magi_lab_work_without_experience() -> None:
    for key in (vc.VITALIZE, vc.INVIGORATE):
        assert not ACTIVITIES[key].gives_xp
        assert ACTIVITIES[key].who == ("magus",)
        assert ACTIVITIES[key].book == "LoH"


def test_what_stops_a_season() -> None:
    saga = _saga(vires=0)
    magus = saga.character("m")
    assert magus is not None
    check = REGISTRY[vc.VITALIZE].check
    plan = _plan(vc.VITALIZE, title="Rooster", book_level=10)
    assert "Hermetic Viresculture" in check(saga, magus, plan)[0]
    magus.abilities.append(Ability(vc.ABILITY, xp=ability_xp(1)))
    # Its Vim is paid from the stores (LoH p. 73).
    assert "Vim vis; Elaine's raw vis has 0" in check(saga, magus, plan)[0]
    magus.raw_vis["vim"] = 1
    assert check(saga, magus, plan) == []
    assert "Name the Stirps" in check(saga, magus, _plan(vc.VITALIZE, book_level=1))[0]
    assert "Magic Might" in check(saga, magus, _plan(vc.VITALIZE, title="R"))[0]
    invigorate = REGISTRY[vc.INVIGORATE].check
    assert (
        "Form"
        in invigorate(saga, magus, _plan(vc.INVIGORATE, title="R", book_level=10))[0]
    )
    assert (
        invigorate(
            saga, magus, _plan(vc.INVIGORATE, title="R", book_level=10, form="Animal")
        )
        == []
    )


def test_vitalizing_a_stirps_over_two_seasons() -> None:
    saga = _saga()
    magus = saga.character("m")
    assert magus is not None
    entry = REGISTRY[vc.VITALIZE]
    # Total 15 against Might 10: 5 points a season.
    plan = _plan(vc.VITALIZE, title="Rooster of Virtue", book_level=10)
    result = SupplementWork()
    entry.outcome(saga, magus, plan, None, result)
    assert result.progress == [(vc.VITALIZING, "Rooster of Virtue", 10, 5)]
    notes = " ".join(result.notes)
    assert "Pays 1 pawn(s) of Vim vis" in notes and "(5/10)" in notes
    assert result.vis_cost == {"Vim": 1}
    magus.raw_vis["vim"] = 3
    apply_supplement(saga, magus, plan, result)
    assert magus.raw_vis["vim"] == 2
    second = _plan(vc.VITALIZE, title="Rooster of Virtue", book_level=10)
    second.season = "Summer"
    result = SupplementWork()
    entry.outcome(saga, magus, second, None, result)
    assert "Pays" not in " ".join(result.notes) and not result.vis_cost
    assert "is a Stirps" in " ".join(result.notes)
    apply_supplement(saga, magus, second, result)
    record = next(p for p in magus.progress if p.kind == vc.VITALIZING)
    assert (record.points, record.done) == (10, True)


def test_invigorating_a_stirps_records_its_breeding_seasons() -> None:
    saga = _saga()
    magus = saga.character("m")
    assert magus is not None
    magus.progress.append(Progress(vc.VITALIZING, "Rooster", 10, 10, done=True))
    plan = _plan(vc.INVIGORATE, title="Rooster", book_level=10, form="Animal")
    result = SupplementWork()
    REGISTRY[vc.INVIGORATE].outcome(saga, magus, plan, None, result)
    # Total 15 (Vim for the lower Art): two breeding seasons of 2 pawns.
    assert result.progress == [(vc.INVIGORATED, "Rooster", 0, 2)]
    notes = " ".join(result.notes)
    assert "2 breeding season(s), each giving 2 pawn(s) of Animal vis" in notes
    assert "taken to be a Stirps already" not in notes
    assert "12 Labor Points" in notes
    apply_supplement(saga, magus, plan, result)
    record = next(p for p in magus.progress if p.kind == vc.INVIGORATED)
    assert (record.points, record.done) == (2, False)


def test_the_season_form_reads_the_stirps() -> None:
    saga = _saga()
    magus = saga.character("m")
    assert magus is not None
    values = {
        "activity": vc.INVIGORATE,
        season_forms.WHEN: "Spring 1220",
        "stirps_name": " Rooster ",
        "stirps_might": 10,
        "stirps_form": "Animal",
    }
    plan = season_forms.season_plan_from(saga, magus, values)
    assert (plan.title, plan.book_level, plan.form) == ("Rooster", 10, "Animal")
    keys = {f.key for f in season_forms.season_plan_fields(saga, magus, None)}
    assert {"stirps_name", "stirps_might", "stirps_form"} <= keys


def test_several_stirpes_vitalized_in_one_season() -> None:
    # LoH p. 75: two roosters of Might 10 in one season under Multiple
    # Laboratory Activities (DE p. 264), for two pawns of Vim.
    saga = _saga(vires=4)
    magus = saga.character("m")
    assert magus is not None
    magus.raw_vis["vim"] = 2
    plan = _plan(vc.VITALIZE, title="Rooster", book_level=5)
    plan.more_stirpes = {"Second rooster": 2}
    entry = REGISTRY[vc.VITALIZE]
    # Total 15 against 7 together: 8 points, enough to finish both.
    assert entry.check(saga, magus, plan) == []
    result = SupplementWork()
    entry.outcome(saga, magus, plan, None, result)
    assert result.progress == [
        (vc.VITALIZING, "Rooster", 5, 5),
        (vc.VITALIZING, "Second rooster", 2, 2),
    ]
    assert result.vis_cost == {"Vim": 2}
    apply_supplement(saga, magus, plan, result)
    assert "vim" not in magus.raw_vis
    assert all(p.done for p in magus.progress if p.kind == vc.VITALIZING)
    # Too much for one season: Vitalize them one at a time.
    plan.more_stirpes = {"Second rooster": 10}
    assert "finish them all" in entry.check(saga, magus, plan)[0]
    plan.more_stirpes = {"Hen": -1}
    assert "Type a Magic Might for Hen" in entry.check(saga, magus, plan)[0]
    # A Might of 0 is allowed (LoH p. 72).
    assert vc.vitalization_level(0) == 0


def test_several_stirpes_share_the_invigoration_total() -> None:
    assert vc.shared_total(43, 2) == 22  # LoH p. 75's two roosters
    saga = _saga()
    magus = saga.character("m")
    assert magus is not None
    plan = _plan(vc.INVIGORATE, title="Rooster", book_level=10, form="Animal")
    plan.more_stirpes = {"Second rooster": 10}
    result = SupplementWork()
    REGISTRY[vc.INVIGORATE].outcome(saga, magus, plan, None, result)
    # Total 15 shared: 8 each, one breeding season each.
    assert result.progress == [
        (vc.INVIGORATED, "Rooster", 0, 1),
        (vc.INVIGORATED, "Second rooster", 0, 1),
    ]
    assert "shared among 2 Stirpes: 8 each" in " ".join(result.notes)


def test_the_form_reads_other_stirpes() -> None:
    assert vires_forms.parse_stirpes("Second rooster: 10; Hen 12\nMare") == {
        "Second rooster": 10,
        "Hen": 12,
        "Mare": -1,
    }
    assert vires_forms.stirpes_text({"Hen": 12, "Mare": -1}) == "Hen: 12; Mare"
    saga = _saga()
    magus = saga.character("m")
    assert magus is not None
    values = {
        "activity": vc.VITALIZE,
        season_forms.WHEN: "Spring 1220",
        "stirps_name": "Rooster",
        "stirps_might": 10,
        "more_stirpes": "Second rooster: 10",
        "vis_from": "covenant",
    }
    plan = season_forms.season_plan_from(saga, magus, values)
    assert plan.more_stirpes == {"Second rooster": 10}
    assert plan.vis_from == "covenant"
