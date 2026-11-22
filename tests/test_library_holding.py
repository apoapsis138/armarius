"""The book inspector's block on its covenant's library in the book's
subject: the Holding (Transforming Mythic Europe p. 105) with what the book
does in it, and the Research bonus (Covenants p. 98)."""

from __future__ import annotations

from ars_magica_manager import books as bk
from ars_magica_manager.models import Book, Character, Covenant, Saga
from ars_magica_manager.rules import options as rule_options


def _vim_library(large_library: bool = True) -> Saga:
    """Dammërstein's Vim shelf in the real save: a L14 Q11 summa, two Q8
    tractatus that add to its Quality, two Q6 ones that don't."""
    covenant = Covenant(
        id="cov", name="Dammërstein", saga_id="s", library_research={"Vim": 1}
    )

    def tract(i: int, quality: int) -> Book:
        return Book(f"t{i}", f"Tract {i}", "Tractatus", subject_kind="Art",
                    art="Vim", quality=quality, owner_kind="covenant",
                    owner_id="cov")  # fmt: skip

    saga = Saga(
        id="s",
        name="Saga",
        covenants=[covenant],
        characters=[
            Character(id="ana", name="Corvinus", type="magus", covenant_id="cov")
        ],
        books=[
            Book(
                "bounds",
                "On the Bounds of Power",
                "Art Summa",
                art="Vim",
                level=14,
                quality=11,
                owner_kind="covenant",
                owner_id="cov",
            ),
            tract(1, 8),
            tract(2, 8),
            tract(3, 6),
            tract(4, 6),
        ],
    )
    if large_library:
        saga.rule_options[rule_options.LARGE_LIBRARY] = True
        saga.books_in_play = ["ArM5", "TME"]
    return saga


def _block(saga: Saga, book_id: str) -> list[str]:
    """The inspector's lines from the library heading to the Value line."""
    lines = bk.detail_text(saga, next(b for b in saga.books if b.id == book_id))
    lines = lines.splitlines()
    start = next(
        (i for i, line in enumerate(lines) if "Vim library" in line or "Kept" in line),
        None,
    )
    if start is None:
        return []
    end = next(i for i, line in enumerate(lines) if "Value:" in line)
    return lines[start:end]


def test_the_best_summa_shows_the_holding_it_sets():
    assert _block(_vim_library(), "bounds") == [
        "[b]Dammërstein's Vim library[/]",
        "  [b]Holding:[/] Level 14, Quality 11 · this is its best summa "
        "(2 of its 4 tractatus add to it)",
        "  [b]Research:[/] library +1",
    ]


def test_a_best_summa_nothing_adds_to():
    saga = _vim_library()
    saga.books = [b for b in saga.books if b.id in ("bounds", "t3")]
    assert _block(saga, "bounds")[1].endswith(
        "this is its best summa (no other book adds to it)"
    )


def test_a_tractatus_shows_whether_it_adds_to_the_holding():
    saga = _vim_library()
    assert _block(saga, "t1")[1] == (
        "  [b]Holding:[/] Level 14, Quality 11 · this book adds to its Quality"
    )
    # Q6 is 5 below the Holding's Quality 11 (TME p. 105: within three).
    assert _block(saga, "t3")[1] == (
        "  [b]Holding:[/] Level 14, Quality 11 · this book adds nothing: "
        "more than 3 from the Holding"
    )


def test_a_copy_adds_nothing():
    saga = _vim_library()
    saga.books.append(
        Book("c", "Copy", "Tractatus", subject_kind="Art", art="Vim", quality=8,
             copy_of="t1", owner_kind="covenant", owner_id="cov")
    )  # fmt: skip
    assert _block(saga, "c")[1].endswith(
        "this book adds nothing: a copy of a book it has"
    )


def test_a_book_a_magus_keeps_is_not_in_the_shared_library():
    saga = _vim_library()
    saga.books.append(
        Book("k", "Corvinus's Notes", "Tractatus", subject_kind="Art", art="Vim",
             quality=9, owner_kind="character", owner_id="ana")
    )  # fmt: skip
    assert _block(saga, "k") == [
        "[b]Kept by Corvinus:[/] not in Dammërstein's shared library"
    ]


def test_with_the_rule_off_only_research_shows():
    assert _block(_vim_library(large_library=False), "bounds") == [
        "[b]Dammërstein's Vim library[/]",
        "  [b]Research:[/] library +1",
    ]


def test_no_summa_means_no_holding():
    saga = _vim_library()
    saga.books = [b for b in saga.books if b.id != "bounds"]
    assert _block(saga, "t1")[1] == (
        "  [b]Holding:[/] none: the library has no summa on it"
    )


def test_no_citation_on_the_book():
    text = bk.detail_text(_vim_library(), _vim_library().books[0])
    assert "Transforming Mythic Europe" not in text
    assert "The library on it" not in text
