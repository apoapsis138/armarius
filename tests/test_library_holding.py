"""The book inspector's block on its covenant's library in the book's
subject: the Holding (Transforming Mythic Europe p. 105) with what the book
does in it, and the Research bonus (Covenants p. 98)."""

from __future__ import annotations

from ars_magica_manager import books as bk
from ars_magica_manager import library_holding as lh
from ars_magica_manager.forms import library as library_forms
from ars_magica_manager.models import ArtScore, Book, Character, Covenant, Saga
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


# -- the Library by subject ---------------------------------------------------


def _mixed_library() -> Saga:
    """Vim (scored), Creo (tractatus only), Latin (an Ability summa) and a
    book Corvinus keeps on Magic Theory, which the shared library lacks."""
    saga = _vim_library()
    saga.books += [
        Book("cr", "Creo Notes", "Tractatus", subject_kind="Art", art="Creo",
             quality=7, owner_kind="covenant", owner_id="cov"),
        Book("la", "Grammar", "Ability Summa", ability="Latin", level=4,
             quality=9, owner_kind="covenant", owner_id="cov"),
        Book("mt", "Corvinus's Theory", "Ability Summa", ability="Magic Theory",
             level=3, quality=8, owner_kind="character", owner_id="ana"),
    ]  # fmt: skip
    return saga


def test_the_subjects_in_hermetic_order_then_abilities():
    saga = _mixed_library()
    found = lh.holdings(saga, saga.covenants[0])
    assert [h.name for h in found] == ["Creo", "Vim", "Latin", "Magic Theory"]


def test_the_subjects_table():
    saga = _mixed_library()
    found = lh.holdings(saga, saga.covenants[0])
    table = lh.subjects_table(found)
    assert table.columns == ["Subject", "Holding", "Best summa", "Books", "Research"]
    assert table.rows == [
        ["Arts", "", "", "", ""],
        ["[dim]Creo[/]", "[dim]—[/]", "[dim]no summa[/]", "[dim]1 tractatus[/]",
         "[dim]—[/]"],
        ["Vim", "L14 Q11", "On the Bounds of Power", "1 summa · 4 tractatus", "+1"],
        ["Abilities", "", "", "", ""],
        ["Latin", "L4 Q9", "Grammar", "1 summa", "—"],
        # Only a book Corvinus keeps: no Holding in the shared library.
        ["[dim]Magic Theory[/]", "[dim]—[/]", "[dim]no summa[/]",
         "[dim]1 kept by its magi[/]", "[dim]—[/]"],
    ]  # fmt: skip
    assert table.keys == [None, 0, 1, None, 2, 3]


def test_the_terminal_rows():
    saga = _mixed_library()
    found = lh.holdings(saga, saga.covenants[0])
    assert lh.subject_header().split() == ["Subject", "Holding", "Best", "summa",
                                           "Books", "Research"]  # fmt: skip
    vim = lh.subject_label(found[1])
    assert vim.startswith("Vim") and "L14 Q11" in vim and vim.endswith("+1")
    assert lh.subject_label(found[0]).startswith("[dim]Creo")


def test_the_subject_inspector_with_the_large_library():
    saga = _vim_library()
    saga.books.append(
        Book("k", "Corvinus's Notes", "Tractatus", subject_kind="Art", art="Vim",
             quality=9, owner_kind="character", owner_id="ana")
    )  # fmt: skip
    saga.characters[0].arts = {"vim": ArtScore(xp=15)}  # Vim 5
    holding = lh.holdings(saga, saga.covenants[0])[0]
    lines = bk.subject_detail_text(saga, holding).splitlines()
    # TME p. 105: below its Level, Quality + 3; at it, its Quality for
    # Quality more seasons.
    assert lines[:3] == [
        "[b]Holding:[/] Level 14, Quality 11",
        "  Below Vim 14: 14 xp a season",
        "  At Vim 14 or more: 11 xp a season, for 11 seasons",
    ]
    assert "[b]Research:[/] library +1" in lines
    books = lines[lines.index("[b]Its books:[/]") + 1 :]
    assert books[:6] == [
        "On the Bounds of Power · L14 Q11 · the best summa: sets the Holding",
        "Tract 1 · Q8 · adds to its Quality",
        "Tract 2 · Q8 · adds to its Quality",
        "Tract 3 · Q6 · adds nothing: more than 3 from the Holding",
        "Tract 4 · Q6 · adds nothing: more than 3 from the Holding",
        "Corvinus's Notes · Q9 · kept by Corvinus: not in the shared library",
    ]
    assert "Corvinus (Vim 5): 14 xp" in lines
    # Only a magus studies an Art.
    saga.characters.append(
        Character(id="co", name="Odo", type="companion", covenant_id="cov")
    )
    assert "Odo" not in bk.subject_detail_text(saga, holding)


def test_the_subject_inspector_without_the_rule():
    saga = _vim_library(large_library=False)
    holding = lh.holdings(saga, saga.covenants[0])[0]
    text = bk.subject_detail_text(saga, holding)
    assert (
        text.splitlines()[0]
        == "[b]Best summa:[/] On the Bounds of Power, Level 14, Quality 11"
    )
    assert "Below Vim" not in text
    assert "Tract 1 · Q8\n" in text + "\n"  # no roles without the rule


def test_add_from_a_subject_starts_a_summa_on_it():
    saga = _mixed_library()
    latin = lh.holdings(saga, saga.covenants[0])[2]
    form = library_forms.book_form(saga, None, "covenant:cov", like=lh.prototype(latin))
    values = {f.key: f.value for f in form.fields()}
    assert (values["type"], values["ability"]) == ("Ability Summa", "Latin")
    assert form.title == "Add a Book"


def test_research_setup_opens_on_the_chosen_subject():
    saga = _mixed_library()
    saga.covenants[0].library_research = {}
    form = library_forms.research_walkthrough(saga, saga.covenants[0], "Latin")
    assert form.title.endswith(": Latin")


def test_the_library_view_is_remembered():
    assert lh.library_view() == lh.SHELVES
    lh.remember_library_view(lh.SUBJECTS)
    assert lh.library_view() == lh.SUBJECTS
