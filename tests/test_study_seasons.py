"""Study seasons: reading, being taught or trained, teaching and
vis study as planned seasons, and who may read which book."""

import random

from support import strip_markup

from ars_magica_manager import books, seasons
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Book,
    Character,
    Characteristics,
    Covenant,
    Laboratory,
    Possession,
    Saga,
    SeasonPlan,
    XpAllocation,
)
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.rules import library, warping
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _saga() -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep")
    student = Character(id="tib", name="Tiberius", type="magus", covenant_id="cov")
    student.abilities = [
        Ability("Latin", xp=ability_xp(4)),
        Ability("Artes Liberales", xp=ability_xp(1)),
        Ability("Parma Magica", xp=ability_xp(1)),
    ]
    student.arts = {"creo": ArtScore(xp=art_xp(4)), "ignem": ArtScore()}
    student.raw_vis = {"creo": 3}
    student.assigned_lab_id = "lab"
    teacher = Character(id="oda", name="Oda", type="magus", covenant_id="cov")
    teacher.characteristics = Characteristics(communication=2)
    teacher.abilities = [
        Ability("Latin", xp=ability_xp(5)),
        Ability("Teaching", xp=ability_xp(2)),
        Ability("Parma Magica", xp=ability_xp(1)),
    ]
    teacher.arts = {"ignem": ArtScore(xp=art_xp(8))}
    companion = Character(id="alys", name="Alys", type="companion", covenant_id="cov")
    lab = Laboratory(id="lab", covenant_id="cov", name="Tower", owner_id="tib")
    saga = Saga(
        id="s",
        name="S",
        covenants=[covenant],
        characters=[student, teacher, companion],
        laboratories=[lab],
    )
    saga.books = [
        Book(
            "summa",
            "De Ignis",
            "Art Summa",
            owner_kind="covenant",
            owner_id="cov",
            art="Ignem",
            level=10,
            quality=12,
        ),
        Book(
            "tract",
            "On Grammar",
            "Tractatus",
            owner_kind="character",
            owner_id="tib",
            subject_kind="Ability",
            ability="Latin",
            quality=7,
        ),
        Book(
            "alys-book",
            "Her Notes",
            "Ability Summa",
            owner_kind="character",
            owner_id="alys",
            ability="Latin",
            level=5,
            quality=10,
        ),
        Book(
            "lab-book",
            "Workbook",
            "Ability Summa",
            owner_kind="laboratory",
            owner_id="lab",
            ability="Magic Theory",
            level=4,
            quality=9,
        ),
        Book("loose", "Loose", "Ability Summa", ability="Latin", level=3, quality=5),
    ]
    return saga


def _plan(who: str, activity: str, *subjects: str, **kw) -> SeasonPlan:
    return SeasonPlan(
        who, 1220, "Spring", activity, [XpAllocation(s) for s in subjects], **kw
    )


def _outcome(saga, plan, rng=None):
    return rules.outcome(saga.character(plan.character_id), plan, saga, rng)


def _xp(worked) -> list[tuple[str, int]]:
    return [(g.subject, g.result.xp) for g in worked.gains]


# -- who may read which book ---------------------------------------------------


def test_the_library_is_open_to_the_covenant_but_kept_books_are_not():
    saga = _saga()
    tib, oda, alys = saga.characters
    book = {b.id: b for b in saga.books}
    assert library.can_read(saga, tib, book["summa"])
    assert library.can_read(saga, alys, book["summa"])
    assert library.can_read(saga, tib, book["tract"])
    assert not library.can_read(saga, oda, book["tract"])
    assert not library.can_read(saga, tib, book["alys-book"])
    assert library.can_read(saga, tib, book["lab-book"])  # his own laboratory's
    assert not library.can_read(saga, oda, book["lab-book"])
    assert not library.can_read(saga, tib, book["loose"])  # in nobody's library
    assert [b.id for b in books.studyable_books(saga, tib)] == [
        "summa",
        "tract",
        "lab-book",
    ]
    assert [c.name for c in books.readers(saga, book["tract"])] == ["Tiberius"]


def test_reading_someone_elses_book_is_refused():
    saga = _saga()
    worked = _outcome(saga, _plan("tib", rules.READ, book_id="alys-book"))
    assert "can't get at Her Notes" in worked.problems[0]


# -- reading -------------------------------------------------------------------


def test_a_summa_gives_its_quality_up_to_its_level():
    saga = _saga()
    worked = _outcome(saga, _plan("tib", rules.READ, book_id="summa"))
    assert _xp(worked) == [("art:Ignem", 12)]
    # At the summa's Level there's nothing more to learn from it.
    saga.characters[0].arts["ignem"] = ArtScore(xp=art_xp(10))
    worked = _outcome(saga, _plan("tib", rules.READ, book_id="summa"))
    assert "nothing more to teach" in worked.problems[0]


def test_only_the_gifted_study_the_arts():
    saga = _saga()
    worked = _outcome(saga, _plan("alys", rules.READ, book_id="summa"))
    assert worked.problems == ["Only the Gifted study the Arts."]


def test_a_tractatus_teaches_each_reader_once():
    saga = _saga()
    seasons.set_plan(saga, _plan("tib", rules.READ, book_id="tract"))
    seasons.apply(saga, seasons.resolve(saga))
    tib = saga.characters[0]
    assert tib.tractatus_read == ["tract"]
    assert tib.abilities[0].xp == ability_xp(4) + 7
    worked = _outcome(saga, _plan("tib", rules.READ, book_id="tract"))
    assert "already studied On Grammar" in worked.problems[0]


def test_the_plan_names_the_book_it_reads():
    saga = _saga()
    plan = _plan("tib", rules.READ, book_id="summa")
    summary = seasons.plan_summary(saga, saga.characters[0], plan)
    assert summary == "Read a book: De Ignis (Ignem summa, L10 Q12)"


# -- teaching and training ------------------------------------------------------


def test_a_student_is_taught_only_if_the_teacher_plans_to_teach():
    saga = _saga()
    taught = _plan("alys", rules.TAUGHT, "ability:Latin", teacher_id="oda")
    seasons.set_plan(saga, taught)
    assert "Oda hasn't planned to Teach" in _outcome(saga, taught).problems[0]
    seasons.set_plan(saga, _plan("oda", rules.TEACH, "ability:Teaching"))
    # Com 2 + Teaching 2 + 3, +6 for one student = 13; Latin is new to Alys.
    assert _xp(_outcome(saga, taught)) == [("ability:Latin", 13)]
    seasons.apply(saga, seasons.resolve(saga))
    alys, oda = saga.character("alys"), saga.character("oda")
    assert [(a.name, a.xp) for a in alys.abilities] == [("Latin", 13)]
    assert oda.abilities[1].xp == ability_xp(2) + 2  # the teacher's Exposure


def test_the_arts_are_taught_one_on_one():
    saga = _saga()
    saga.characters.append(
        Character(id="gaius", name="Gaius", type="magus", covenant_id="cov")
    )
    seasons.set_plan(saga, _plan("oda", rules.TEACH, "ability:Teaching"))
    for who in ("tib", "gaius"):
        seasons.set_plan(saga, _plan(who, rules.TAUGHT, "art:Ignem", teacher_id="oda"))
    worked = _outcome(saga, _plan("tib", rules.TAUGHT, "art:Ignem", teacher_id="oda"))
    assert "one student at a time" in worked.problems[0]


def test_a_teacher_must_know_more_than_the_student():
    saga = _saga()
    seasons.set_plan(saga, _plan("oda", rules.TEACH, "ability:Teaching"))
    saga.characters[0].abilities[0].xp = ability_xp(5)
    plan = _plan("tib", rules.TAUGHT, "ability:Latin", teacher_id="oda")
    seasons.set_plan(saga, plan)
    assert "higher than the student's" in _outcome(saga, plan).problems[0]


def test_training_is_the_masters_score_plus_3_up_to_it():
    saga = _saga()
    worked = _outcome(
        saga, _plan("tib", rules.TRAINED, "ability:Latin", teacher_id="oda")
    )
    # Latin 5 + 3 = 8; Tiberius has 50 xp of the 75 Latin 5 needs: room for 25.
    assert _xp(worked) == [("ability:Latin", 8)]
    arts = _outcome(saga, _plan("tib", rules.TRAINED, "art:Ignem", teacher_id="oda"))
    assert "Only Abilities can be trained" in arts.problems[0]


# -- vis study -----------------------------------------------------------------------


def test_vis_study_with_a_typed_die():
    saga = _saga()
    plan = _plan("tib", rules.VIS_STUDY, "art:Creo", die=7, vis_from="character")
    worked = _outcome(saga, plan)
    # Creo 4: 1 pawn; no covenant aura: Source Quality = 7.
    assert _xp(worked) == [("art:Creo", 7)]
    assert worked.effect_of(rules.SpendVis) == rules.SpendVis("character", "Creo", 1)
    seasons.set_plan(saga, plan)
    seasons.apply(saga, seasons.resolve(saga))
    assert saga.characters[0].raw_vis == {"creo": 2}
    assert saga.characters[0].arts["creo"].xp == art_xp(4) + 7


def test_vis_study_is_rolled_when_applied_and_previewed_before():
    saga = _saga()
    plan = _plan("tib", rules.VIS_STUDY, "art:Creo", vis_from="character")
    preview = _outcome(saga, plan)
    assert preview.pending_roll and preview.gains == []
    rolled = _outcome(saga, plan, random.Random(3))
    assert not rolled.pending_roll and len(rolled.gains) == 1
    assert any(n.startswith("Die rolled") for n in rolled.notes)


def test_vis_study_needs_the_vis():
    saga = _saga()
    plan = _plan("tib", rules.VIS_STUDY, "art:Creo", die=5, vis_from="laboratory")
    worked = _outcome(saga, plan)
    assert "the laboratory's raw vis has 0" in worked.problems[0]
    saga.laboratories[0].raw_vis = {"creo": 1}
    assert _outcome(saga, plan).ok


def test_vis_study_can_pay_from_the_covenants_vis_stores():
    saga = _saga()
    keep = saga.covenants[0]
    plan = _plan("tib", rules.VIS_STUDY, "art:Creo", die=5, vis_from="covenant")
    assert "the covenant's raw vis has 0" in _outcome(saga, plan).problems[0]
    keep.possessions = [
        Possession(id="v1", kind="vis_store", name="Cask", art="Creo", pawns=1),
        Possession(id="v2", kind="vis_store", name="Urn", art="Vim", pawns=2),
    ]
    assert _outcome(saga, plan).ok
    own = dict(saga.characters[0].raw_vis)
    seasons.set_plan(saga, plan)
    seasons.apply(saga, seasons.resolve(saga))
    # The emptied store is gone, his own vis untouched, the Diary notes it.
    assert [p.name for p in keep.possessions] == ["Urn"]
    assert saga.characters[0].raw_vis == own
    entry = keep.diary[-1]
    assert entry.name == f"{saga.characters[0].name} used 1 pawn of Creo vis"
    assert (entry.category, entry.vis_pawns, entry.vis_art) == ("Vis", -1, "Creo")


def test_vis_study_is_for_magi_only():
    saga = _saga()
    assert rules.VIS_STUDY not in [
        a.key for a in rules.activities_for(saga.character("alys"))
    ]


def test_the_book_panel_lists_only_those_who_may_read_it():
    saga = _saga()
    lines = strip_markup("\n".join(books._study_lines(saga, saga.books[1])))
    assert "Tiberius" in lines and "Oda" not in lines


class _Zeros(random.Random):
    """Every die shows 0."""

    def randrange(self, *args, **kwargs):
        return 0


def test_a_vis_study_botch_warps_and_a_double_one_brings_twilight():
    saga = _saga()
    student = saga.characters[0]
    student.arts["creo"] = ArtScore(xp=art_xp(10))  # 2 pawns: 2 botch dice
    plan = _plan("tib", rules.VIS_STUDY, "art:Creo", die=0, vis_from="character")
    worked = _outcome(saga, plan, _Zeros())
    assert worked.effect_of(rules.Warp).points == 2
    seasons.set_plan(saga, plan)
    seasons.apply(saga, seasons.resolve(saga, _Zeros()))
    assert warping.total_points(student) >= 2
    assert any(e.name in ("Warping +2", "Wizard's Twilight") for e in student.diary)


def test_nobody_studies_his_own_tractatus_or_a_book_he_cant_read():
    saga = _saga()
    tract = next(b for b in saga.books if b.id == "tract")
    tract.author, tract.author_id = "Tiberius", "tib"
    worked = _outcome(saga, _plan("tib", rules.READ, book_id="tract"))
    assert any("a tractatus of his own" in p for p in worked.problems)
    tract.author_id = None
    tract.author = "Someone"
    student = saga.characters[0]
    student.abilities = [Ability("Latin", xp=ability_xp(3))]
    worked = _outcome(saga, _plan("tib", rules.READ, book_id="tract"))
    assert any("needs Latin at 4" in p for p in worked.problems)
    assert any("Artes Liberales" in p for p in worked.problems)


def test_a_teachers_students_count_across_subjects():
    saga = _saga()
    alys = saga.character("alys")
    alys.abilities = [Ability("Latin", xp=ability_xp(4))]
    one = _plan("tib", rules.TAUGHT, "art:Ignem", teacher_id="oda")
    two = _plan("alys", rules.TAUGHT, "ability:Latin", teacher_id="oda")
    teach = _plan("oda", rules.TEACH, "ability:Teaching")
    for plan in (one, two, teach):
        seasons.set_plan(saga, plan)
    worked = _outcome(saga, one)
    assert any("one student at a time" in p for p in worked.problems)


def test_a_first_season_in_a_supernatural_ability():
    saga = _saga()
    teacher = saga.character("oda")
    teacher.abilities.append(Ability("Second Sight", "Supernatural", xp=ability_xp(4)))
    plan = _plan("alys", rules.TAUGHT, "ability:Second Sight", teacher_id="oda")
    seasons.set_plan(saga, plan)
    seasons.set_plan(saga, _plan("oda", rules.TEACH, "ability:Teaching"))
    worked = _outcome(saga, plan)
    assert worked.problems == [
        "Only the Gifted learn a Supernatural Ability of Magic like Second Sight "
        "(DE p. 383)."
    ]
    # A magus: 15 off for his opened Arts (Creo 4 and Ignem 0 are less).
    tib = _plan("tib", rules.TAUGHT, "ability:Second Sight", teacher_id="oda")
    seasons.set_plan(saga, tib)
    saga.season_plans.remove(plan)
    worked = _outcome(saga, tib)
    # Communication 2 + Teaching 2 + 3 + 6 = 13, less 15: nothing learned.
    assert any("-15 for the student's" in n for n in worked.notes)
    assert _xp(worked) == [("ability:Second Sight", 0)]
