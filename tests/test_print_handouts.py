"""Any Handout a player holds laid out for paper (print_handouts): a
written Handout's blocks on its Stationery, a record's copy read back from
the Markdown it was frozen as, a picture on a page of its own."""

from __future__ import annotations

from pathlib import Path

import pytest
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import handout_layout, markdown_sheet, shows
from ars_magica_manager import print_handouts as ph
from ars_magica_manager import print_layout as pl
from ars_magica_manager.commands import ChooseFile
from ars_magica_manager.forms import printing
from ars_magica_manager.forms import show as show_forms
from ars_magica_manager.handout_list import PICTURE, RECORD, WRITTEN
from ars_magica_manager.models import PROCLAMATION, SEALED_LETTER

LETTER = """[heading] To the Abbot
[centre] Greetings
[initial] Know that the **bridge** is down.
And the road with it.

[flourish]
[picture 2]
[right] Given at Cologne
[picture 7]"""


def _written(text: str = LETTER, pictures: tuple[bytes | None, ...] = (b"one", b"two")):
    return shows.Shown("A letter", text, stationery=SEALED_LETTER, pictures=pictures)


def test_each_kind_of_handout_has_its_builder() -> None:
    assert set(ph.LAYOUTS) == {WRITTEN, RECORD, PICTURE}
    assert ph.kind_of(_written()) == WRITTEN
    assert ph.kind_of(shows.Shown("Map", picture=b"png")) == PICTURE
    assert ph.kind_of(shows.Shown("Hilda", "# Hilda")) == RECORD


def test_a_written_handout_is_laid_on_its_stationery() -> None:
    doc = ph.document(_written())

    assert doc.stationery == SEALED_LETTER
    assert doc.title == "A letter"
    assert doc.subtitle == handout_layout.stationery(SEALED_LETTER).label
    assert doc.blocks[0] == pl.Title("A letter", doc.subtitle)
    assert doc.blocks[1:] == [
        pl.Passage("To the Abbot", "c", heading=True),
        pl.Passage("Greetings", "c"),
        pl.Passage(
            "now that the [b]bridge[/b] is down.\nAnd the road with it.",
            initial="K",
        ),
        pl.Flourish(),
        pl.Picture(b"two", handout_layout.COPY_CAPTION, number=2),
        pl.Passage("Given at Cologne", "r"),
        # A picture the Handout hasn't got is text, as on screen.
        pl.Passage("\\[picture 7]"),
    ]


def test_a_written_handouts_heading_keeps_with_what_follows() -> None:
    assert pl.keeps_with_next(pl.Passage("To the Abbot", "c", heading=True))
    assert not pl.keeps_with_next(pl.Passage("Greetings", "c"))


def test_a_picture_not_to_hand_is_printed_as_a_placeholder() -> None:
    doc = ph.document(_written("[picture 1]", (None,)))

    assert doc.blocks[1] == pl.Picture(None, handout_layout.COPY_CAPTION, number=1)


def test_a_stationery_the_app_doesnt_know_prints_as_vellum() -> None:
    shown = shows.Shown("Odd", "Words", stationery="parchment-of-doom")

    assert ph.document(shown).stationery == handout_layout.stationery("x").name


def test_a_picture_handout_fills_a_page_under_its_title() -> None:
    doc = ph.document(shows.Shown("The Map", picture=b"png", picture_name="ab12.png"))

    assert doc.stationery == ""
    assert doc.blocks == [
        pl.Title("The Map", ph.PICTURE_SUBTITLE),
        pl.Picture(b"png", "The Map", page=True),
    ]
    # Never the copy's file name.
    assert "ab12" not in repr(doc)


def test_a_record_copy_is_read_back_into_the_blocks_it_was_written_from() -> None:
    sheet = pl.Document(
        "Hilda",
        "A grog",
        [
            pl.Title("Hilda", "A grog of Durenmar"),
            pl.Heading("Abilities"),
            pl.Table(
                (pl.Column("Ability", 0.6), pl.Column("Score", 0.4, "c")),
                (
                    (pl.Cell("Brawl", "bold"), pl.Cell("3")),
                    (pl.Cell("Area | Lore", "italic"), pl.Cell("2")),
                ),
                ((0, "Martial"), (1, "General")),
            ),
            pl.Facts((("Born", "1190"), ("Size", "0"))),
            pl.Heading("Virtues", 2),
            pl.Entry("Tough", "Minor · General", "Soak +3", run_in=True),
            pl.Entry("Large", "", "", run_in=True),
            pl.Paragraph("Not revealed to the players", "italic", "small"),
            pl.Paragraph("She guards the gate.\nAnd the well."),
        ],
    )
    shown = shows.Shown("Hilda, as shown", markdown_sheet.render(sheet))

    doc = ph.document(shown)

    assert doc.stationery == ""
    assert doc.title == "Hilda, as shown"
    table = doc.blocks[2]
    assert isinstance(table, pl.Table)
    # The copy keeps no widths: each column's share is by its longest words.
    assert [c.title for c in table.columns] == ["Ability", "Score"]
    assert table.columns[0].width > table.columns[1].width
    assert sum(c.width for c in table.columns) == pytest.approx(1)
    assert doc.blocks == [
        pl.Title("Hilda", "A grog of Durenmar"),
        pl.Heading("Abilities"),
        pl.Table(
            table.columns,
            (
                (pl.Cell("Brawl", "bold"), pl.Cell("3")),
                (pl.Cell("Area | Lore", "italic"), pl.Cell("2")),
            ),
            ((0, "Martial"), (1, "General")),
        ),
        pl.Facts((("Born", "1190"), ("Size", "0"))),
        pl.Heading("Virtues", 2),
        pl.Entry("Tough", "Minor · General", "Soak +3", run_in=True),
        pl.Entry("Large", "", "", run_in=True),
        pl.Paragraph("Not revealed to the players", "italic"),
        pl.Paragraph("She guards the gate.\nAnd the well."),
    ]


def test_a_real_record_copy_prints_every_part_it_shows() -> None:
    saga = _sample_saga_with_covenant()
    words = markdown_sheet.render(pl.character_document(saga, saga.characters[0]))

    doc = ph.document(shows.Shown("Leandro", words))

    assert isinstance(doc.blocks[0], pl.Title)
    assert doc.blocks[0].name == "Leandro"
    headings = {b.text for b in doc.blocks if isinstance(b, pl.Heading)}
    assert {"Abilities", "Combat & Condition", "Hermetic Arts"} <= headings
    # Nothing of the Markdown's own marks is left to print.
    for block in doc.blocks:
        if isinstance(block, pl.Paragraph):
            assert "**" not in block.text and not block.text.startswith("#")


def test_a_record_copy_with_no_title_line_takes_the_shows() -> None:
    doc = ph.document(shows.Shown("Hilda", "Just words."))

    assert doc.blocks == [
        pl.Title("Hilda", ph.RECORD_SUBTITLE),
        pl.Paragraph("Just words."),
    ]


def test_a_record_copy_with_no_line_under_its_title_has_one_at_its_foot() -> None:
    doc = ph.document(shows.Shown("Hilda", "# Hilda\n\nWords."))

    assert doc.blocks[0] == pl.Title("Hilda", "")
    assert doc.subtitle == ph.RECORD_SUBTITLE


def test_words_only_partly_marked_print_plain_without_the_marks() -> None:
    words = "# H\n\n*sub*\n\n*Seen at Durenmar* and *Magvillus*\n\n**A** and ~~B~~"

    doc = ph.document(shows.Shown("H", words))

    assert doc.blocks[1:] == [
        pl.Paragraph("Seen at Durenmar and Magvillus"),
        pl.Paragraph("A and B"),
    ]


def test_every_opened_copy_offers_its_printed_pages() -> None:
    for shown in (
        _written(),
        shows.Shown("Map", picture=b"png"),
        shows.Shown("Hilda", "# Hilda"),
    ):
        printed = show_forms.copy_form(shown).printed
        assert printed is not None
        assert printed() == ph.document(shown)


def test_save_as_pdf_asks_only_the_paper_then_where(tmp_path: Path) -> None:
    drawn: list[tuple[pl.PrintOptions, Path]] = []

    def draw(options: pl.PrintOptions, path: Path) -> int:
        drawn.append((options, path))
        return 2

    form = printing.handout_pdf_form('A "letter"', draw)

    assert [f.key for f in form.fields()] == ["paper"]
    where = form.apply({"paper": pl.A4})
    assert isinstance(where, ChooseFile) and where.save
    assert where.start.name == "A letter.pdf"
    told = where.apply(tmp_path / "x.pdf")
    assert drawn == [(pl.PrintOptions(paper=pl.A4), tmp_path / "x.pdf")]
    assert told == [f"2 pages saved to {tmp_path / 'x.pdf'}."]
    assert printing.saved_options().paper == pl.A4


def test_a_proclamation_names_its_stationery_under_the_title() -> None:
    shown = shows.Shown("Hear ye", "Words", stationery=PROCLAMATION)

    assert ph.document(shown).subtitle == "A proclamation"
