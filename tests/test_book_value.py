"""What a book is worth and what a library is good for (Covenants, Chapter
Seven: Library; Art & Academe, Encyclopedias)."""

import pytest

from ars_magica_manager import book_value as bv
from ars_magica_manager import books as bk
from ars_magica_manager.models import Book, Codex, Covenant, Saga


def _book(book_type: str, **kwargs) -> Book:
    return Book(id="b", name="A Book", type=book_type, **kwargs)


@pytest.mark.parametrize(
    ("book", "expected"),
    [
        # Art summae: Quality + Level against the bands.
        (_book("Art Summa", art="Ignem", level=20, quality=15), bv.EXCELLENT),
        (_book("Art Summa", art="Ignem", level=15, quality=12), bv.SOUND),
        (_book("Art Summa", art="Ignem", level=10, quality=10), bv.VAIN),
        (_book("Art Summa", art="Ignem", level=6, quality=10), bv.DISCARDED),
        # An Ability summa's Level counts three times, as in its cost.
        (_book("Ability Summa", ability="Magic Theory", level=5, quality=11), bv.SOUND),
        # Tractatus: about 14 / 11 / 6.
        (_book("Tractatus", subject_kind="Art", art="Vim", quality=14), bv.EXCELLENT),
        (_book("Tractatus", subject_kind="Art", art="Vim", quality=11), bv.SOUND),
        (_book("Tractatus", subject_kind="Art", art="Vim", quality=6), bv.VAIN),
        (_book("Tractatus", subject_kind="Art", art="Vim", quality=2), bv.DISCARDED),
        # No category: other books, and one whose numbers are still to be set.
        (_book("Other"), None),
        (_book("Art Summa", art="Vim", level=None, quality=10), None),
    ],
)
def test_category(book, expected):
    assert bv.category(book) == expected


def test_price_guide():
    sound = _book("Art Summa", art="Ignem", level=15, quality=12)
    assert bv.price_text(sound) == ("about 15 pawns of vis (18 for a copy at once)")
    vain = _book("Art Summa", art="Ignem", level=9, quality=12)
    assert bv.price_text(vain) == "about 5 pawns of vis"
    excellent = _book("Tractatus", subject_kind="Art", art="Vim", quality=15)
    assert "gift" in bv.price_text(excellent)
    # A book on a mundane Ability is bought for money, not vis.
    mundane = _book("Ability Summa", ability="Medicine", level=5, quality=14)
    assert bv.price_text(mundane).startswith("about a pound")


def _library() -> Saga:
    covenant = Covenant(
        id="cov", name="Keep", saga_id="s", library_research={"Philosophiae": 2}
    )

    def tract(i: int, ability: str, codex: str | None) -> Book:
        return Book(
            id=f"t{i}",
            name=f"Tract {i}",
            type="Tractatus",
            subject_kind="Ability",
            ability=ability,
            quality=6,
            owner_kind="covenant",
            owner_id="cov",
            codex_id=codex,
        )

    books = [tract(i, "Philosophiae", "pliny") for i in range(3)]
    books += [tract(3, "Medicine", "pliny"), tract(4, "Philosophiae", "bound")]
    books.append(
        Book(
            id="summa",
            name="Physics",
            type="Ability Summa",
            ability="Philosophiae",
            level=6,
            quality=12,
            owner_kind="covenant",
            owner_id="cov",
        )
    )
    return Saga(
        id="s",
        name="Saga",
        covenants=[covenant],
        books=books,
        codices=[
            Codex("pliny", "Natural Histories", encyclopedia=True),
            Codex("bound", "Bound Notes"),
        ],
    )


def test_encyclopedias_aid_research_per_tractatus():
    saga = _library()
    covenant = saga.covenants[0]
    assert bv.encyclopedias(saga, covenant, "Philosophiae") == [
        bv.EncyclopediaBonus("Natural Histories", 3)
    ]
    assert bv.guide_text(
        saga, covenant, "Philosophiae", bv.library_subjects(saga, covenant)["Philosophiae"]
    ) == ("1 summa (best Level 6 Quality 12), 4 tractatus; encyclopedias: "
          "Natural Histories +3")  # fmt: skip


def test_research_in_the_summary_and_the_details_panel():
    saga = _library()
    covenant = saga.covenants[0]
    assert bv.research_count(saga, covenant) == "2 subjects"
    assert bv.subject_research_text(saga, covenant, "Philosophiae") == (
        "library +2 · Natural Histories +3"
    )
    physics = saga.books[-1]
    assert "Research (Philosophiae):[/] library +2 · Natural Histories +3" in (
        bk.detail_text(saga, physics)
    )


def test_the_details_panel_shows_the_value():
    saga = _library()
    text = bk.detail_text(saga, saga.books[-1])
    assert "Value:[/] Sound" in text  # 12 + 3 x 6 = 30


def test_a_csv_marks_a_codex_as_an_encyclopedia():
    csv = (
        "name,type,ability,quality,codex,encyclopedia\n"
        "Book 1,Tractatus,Philosophiae,6,Natural Histories,yes\n"
        "Book 2,Tractatus,Philosophiae,6,Natural Histories,yes\n"
        "Notes,Tractatus,Medicine,6,Bound,\n"
    )
    result = bk.parse_books_csv(csv)
    assert result.encyclopedias == {"Natural Histories"}
    saga = Saga(id="s", name="Saga")
    bk.add_imported_books(saga, result.books, None, result.encyclopedias)
    assert [(c.name, c.encyclopedia) for c in saga.codices] == [
        ("Natural Histories", True),
        ("Bound", False),
    ]


def test_library_research_rolls_with_the_better_bonus():
    from ars_magica_manager.models import Ability, Character, SeasonPlan, XpAllocation
    from ars_magica_manager.rules import activities
    from ars_magica_manager.rules.xp import ability_xp

    saga = _library()
    ana = Character(id="ana", name="Ana", type="companion", covenant_id="cov")
    ana.characteristics.intelligence = 2
    ana.abilities = [Ability("Philosophiae", xp=ability_xp(3))]
    saga.characters.append(ana)
    plan = SeasonPlan(
        "ana",
        1220,
        "Spring",
        "library_research",
        allocations=[XpAllocation("ability:Philosophiae")],
    )
    notes = activities.outcome(ana, plan, saga).notes
    # The encyclopedia's +3 beats the library's +2.
    assert any(
        "Intelligence + Philosophiae + Natural Histories +3 = 8" in n for n in notes
    )


def test_read_a_commentary_is_retired():
    from ars_magica_manager.models import Character, SeasonPlan, XpAllocation
    from ars_magica_manager.rules import activities

    ana = Character(id="ana", name="Ana", type="companion")
    assert "read_commentary" not in [a.key for a in activities.activities_for(ana)]
    plan = SeasonPlan(
        "ana", 1220, "Spring", "read_commentary",
        allocations=[XpAllocation("ability:Latin")], source_quality=8,
    )  # fmt: skip
    assert activities.problems(ana, plan, Saga(id="s", name="S"))[0].startswith(
        "Plan Read a book instead"
    )


def test_pictorial_works_and_expert_correspondence_raise_research():
    saga = _library()
    covenant = saga.covenants[0]
    covenant.pictorial_works = ["Philosophiae"]
    assert bv.library_level(saga, covenant, "Philosophiae") == 3  # 2 + 1
    saga.books[4].opus = "Expert correspondence"  # a Philosophiae tractatus
    assert bv.library_level(saga, covenant, "Philosophiae") == 4
    covenant.library_research["Philosophiae"] = 5
    assert bv.library_level(saga, covenant, "Philosophiae") == 5  # at most +5
