"""Seasons spent on books (STORY-910) and Lab Texts (STORY-914)."""

from ars_magica_manager import seasons
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Book,
    Character,
    Characteristics,
    Covenant,
    Laboratory,
    LabTextAccess,
    Saga,
    SeasonPlan,
    Spell,
    XpAllocation,
)
from ars_magica_manager.rules import book_seasons as bs
from ars_magica_manager.rules import lab_seasons
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _saga() -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep")
    magus = Character(id="m", name="Tiberius", type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(intelligence=2, communication=2)
    magus.abilities = [
        Ability("Dead Language: Latin", xp=ability_xp(5)),
        Ability("Magic Theory", xp=ability_xp(3)),
        Ability("Profession: Scribe", xp=ability_xp(3)),
    ]
    magus.arts = {"creo": ArtScore(xp=art_xp(10)), "ignem": ArtScore(xp=art_xp(8))}
    magus.assigned_lab_id = "lab"
    other = Character(id="o", name="Flavia", type="magus", covenant_id="cov")
    other.abilities = [Ability("Magic Theory", xp=ability_xp(1))]
    lab = Laboratory(id="lab", covenant_id="cov", name="Tower", owner_id="m")
    saga = Saga(
        id="s",
        name="S",
        covenants=[covenant],
        characters=[magus, other],
        laboratories=[lab],
    )
    saga.spells = [Spell("bolt", "Bolt", "Creo", "Ignem", level=15)]
    saga.books = [
        Book(
            "summa",
            "Flames",
            "Art Summa",
            owner_kind="covenant",
            owner_id="cov",
            art="Ignem",
            level=6,
            quality=10,
        ),
        Book(
            "raw",
            "Lab Text: Bolt",
            "Lab Text",
            author="Flavia",
            author_id="o",
            raw=True,
            owner_kind="covenant",
            owner_id="cov",
            spell_id="bolt",
        ),
    ]
    return saga


def _plan(activity, character="m", **kw):
    return SeasonPlan(character, 1220, "Spring", activity, **kw)


def _work(saga, plan):
    return bs.work(saga, saga.character(plan.character_id), plan)


def _run(saga):
    seasons.apply(saga, seasons.resolve(saga))


def test_a_summa_is_written_up_to_half_the_score():
    saga = _saga()
    plan = _plan(bs.WRITE_SUMMA, allocations=[XpAllocation("art:Creo")])
    found, work = _work(saga, plan)
    assert found == []
    # Level 5 (half of 10), Quality 2 + 6 = 8; 2 + 5 = 7 points a season.
    assert (work.made.level, work.made.quality, work.points_gained) == (5, 8, 7)
    assert work.finished
    lower = _plan(bs.WRITE_SUMMA, allocations=[XpAllocation("art:Creo")], book_level=3)
    _, work = _work(saga, lower)
    assert work.made.quality == 10  # +1 per Level below the most
    found, _ = _work(
        saga,
        _plan(bs.WRITE_SUMMA, allocations=[XpAllocation("art:Creo")], book_level=6),
    )
    assert found == ["The summa's Level is 1 to 5 (half the score)."]


def test_a_long_summa_takes_seasons_and_is_then_the_authors():
    saga = _saga()
    saga.character("m").arts["creo"] = ArtScore(xp=art_xp(20))  # Level 10
    plan = _plan(bs.WRITE_SUMMA, allocations=[XpAllocation("art:Creo")], title="Fire")
    seasons.set_plan(saga, plan)
    _run(saga)
    assert [p.points for p in saga.lab_projects] == [7]
    assert [p.season for p in saga.season_plans] == ["Summer"]  # planned again
    saga.current_season = "Summer"
    _run(saga)
    book = saga.books[-1]
    assert (book.name, book.type, book.level, book.owner_id) == (
        "Fire",
        "Art Summa",
        10,
        "m",
    )
    assert saga.lab_projects == []
    latin = next(a for a in saga.character("m").abilities if a.name.endswith("Latin"))
    assert latin.xp == ability_xp(5) + 4  # Exposure, twice


def test_a_tractatus_takes_one_season():
    saga = _saga()
    found, work = _work(
        saga, _plan(bs.WRITE_TRACTATUS, allocations=[XpAllocation("art:Creo")])
    )
    assert found == [] and work.made.quality == 8 and work.made.subject_kind == "Art"


def test_copying_a_summa_carefully_or_quickly():
    saga = _saga()
    _, careful = _work(saga, _plan(bs.COPY_BOOK, book_id="summa"))
    assert (careful.points_gained, careful.needed, careful.made.quality) == (9, 6, 10)
    _, quick = _work(saga, _plan(bs.COPY_BOOK, book_id="summa", quick=True))
    assert (quick.points_gained, quick.made.quality) == (27, 9)
    seasons.set_plan(saga, _plan(bs.COPY_BOOK, book_id="summa"))
    _run(saga)
    assert saga.books[-1].name == "Flames" and saga.books[-1].owner_id == "m"


def test_translating_needs_both_languages():
    saga = _saga()
    found, _ = _work(saga, _plan(bs.TRANSLATE_BOOK, book_id="summa", language="Greek"))
    assert found == ["Translating needs Latin and Greek at 5."]


def test_a_raw_lab_text_is_only_for_its_author():
    saga = _saga()
    magus = saga.character("m")
    assert lab_seasons.lab_texts(saga, magus) == []
    assert bs.can_use_lab_text(saga.character("o"), saga.books[1])


def test_decoding_reads_the_authors_texts_up_to_its_level():
    saga = _saga()
    plan = SeasonPlan("m", 1220, "Spring", bs.DECODE_TEXT, lab_id="lab", book_id="raw")
    found, work = lab_seasons.work(saga, saga.character("m"), plan)
    # CrIg 10 + 8 + 2 + 3 = 23 points: level 15 decoded in one season.
    assert found == [] and work.finished
    seasons.plan_lab_work(saga, plan)
    _run(saga)
    magus = saga.character("m")
    assert magus.lab_text_access == {"o": LabTextAccess(15, "decoded")}
    assert [b.id for b in lab_seasons.lab_texts(saga, magus)] == ["raw"]


def test_rewriting_opens_the_authors_texts_to_all():
    saga = _saga()
    saga.books[1].author_id, saga.books[1].author = "m", "Tiberius"
    found, work = _work(saga, _plan(bs.REWRITE_TEXTS))
    assert found == [] and work.rewritten == ["raw"]  # 15 <= Latin 5 x 20
    seasons.set_plan(saga, _plan(bs.REWRITE_TEXTS))
    _run(saga)
    assert not saga.books[1].raw


def test_copying_lab_texts_by_scribe_x_60():
    saga = _saga()
    saga.books[1].raw = False
    found, work = _work(saga, _plan(bs.COPY_TEXTS, book_id="raw"))
    assert found == [] and work.copies == 12  # 3 x 60 = 180 / 15


def test_teaching_abbreviations():
    saga = _saga()
    seasons.set_plan(saga, _plan(bs.TEACH_ABBREVIATIONS, subject_id="o"))
    _run(saga)
    # Filed under the teacher's id, so renaming him loses nothing.
    assert saga.character("o").lab_text_access == {"m": LabTextAccess(100, "taught")}


def test_an_invented_spells_lab_text_is_raw():
    saga = _saga()
    magus = saga.character("m")
    plan = SeasonPlan(
        "m", 1220, "Spring", lab_seasons.INVENT, lab_id="lab", spell_id="bolt"
    )
    saga.spells[0].level = 5
    seasons.plan_lab_work(saga, plan)
    _run(saga)
    text = saga.books[-1]
    assert (text.raw, text.author_id) == (True, "m")
    assert magus.spells_known[0].spell_id == "bolt"
