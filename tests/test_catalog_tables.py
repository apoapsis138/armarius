"""Tables in catalog text: a pipe table in a description is read as a table
block (handout_markup.blocks), drawn as a table on the Read in full page in
both front-ends, and makes the entry long, so no panel shows it."""

from __future__ import annotations

from typing import Any

from support import wait_until
from textual.app import App

from ars_magica_manager import entry_reading, handout_layout
from ars_magica_manager import handout_markup as hm
from ars_magica_manager.commands import Form
from ars_magica_manager.forms import read_in_full as read_forms
from ars_magica_manager.markup import plain
from ars_magica_manager.models import Character, VirtueFlawInstance
from ars_magica_manager.tui.screens.handout_reading import table
from ars_magica_manager.tui.screens.steps import run_steps

RUNES = (
    "| Meaning | Tree | Art |\n"
    "|---|---|---|\n"
    "| Health | Birch | Creo |\n"
    "| Sight | Yew | Intellego |"
)


def test_a_short_entry_with_a_table_is_long() -> None:
    assert entry_reading.is_long(RUNES)
    assert not entry_reading.is_long("A | is not a table.")


def _reading() -> handout_layout.Reading:
    return entry_reading.reading(
        "Elder Runes", "Minor Virtue", "Mystery", "", f"Runes.\n\n{RUNES}", ""
    )


def test_the_reading_page_lays_the_table_out_with_its_rows() -> None:
    [table] = [b for b in _reading().laid.blocks if b.kind == hm.TABLE]

    assert len(table.rows) == 3 and plain(table.rows[2][2]) == "Intellego"


async def test_read_in_full_draws_elder_runes_table_in_the_terminal() -> None:
    magus = Character(
        id="m",
        name="Magus",
        type="magus",
        virtues_flaws=[VirtueFlawInstance(vf_id="vf_verditius_elder_runes")],
    )
    form = read_forms.read_in_full(magus, "section-vf-virtues", 0)
    assert isinstance(form, Form) and form.reading is not None
    app: App[Any] = App()
    async with app.run_test(size=(120, 45)) as pilot:
        run_steps(app, form, lambda _end: None)
        await wait_until(pilot, lambda: bool(app.screen.query(".handout-table")))
        tables = list(app.screen.query(".handout-table"))
        [laid_table] = [b for b in form.reading.laid.blocks if b.kind == hm.TABLE]
        drawn = table(laid_table)

    assert len(tables) == 1
    assert drawn.row_count == 12 and len(drawn.columns) == 4


def test_the_creation_worksheet_shows_a_table_as_lines_of_words() -> None:
    shown = plain(entry_reading.whole_text(f"Runes.\n\n{RUNES}"))

    assert "Runes." in shown and "Health · Birch · Creo" in shown
    assert "|" not in shown


def test_a_handouts_text_has_no_tables() -> None:
    assert hm.TABLE not in [b.kind for b in hm.blocks(RUNES)]


def test_a_panel_leaves_a_table_out_when_there_is_no_summary() -> None:
    shown = plain(entry_reading.panel_text(f"Runes.\n\n{RUNES}", ""))

    assert "Runes." in shown and "Birch" not in shown and "|" not in shown


def test_a_panel_shows_the_summary_when_there_is_one() -> None:
    assert plain(entry_reading.panel_text(RUNES, "The gist.")) == "The gist."


def _kinds(text: str) -> list[str]:
    return [b.kind for b in hm.blocks(text, tables=True)]


def test_a_table_that_isnt_well_made_is_read_as_text() -> None:
    no_rule = "| Meaning | Tree |\n| Health | Birch |"
    too_wide = "|" + "a|" * 9 + "\n|" + "---|" * 9

    for text in (no_rule, too_wide):
        assert hm.TABLE not in _kinds(text), text


def test_a_table_ends_at_a_ragged_row_or_its_last_row() -> None:
    ragged = "| A | B |\n|---|---|\n| x | y |\n| z |"
    too_long = "| a |\n|---|\n" + "| x |\n" * (hm.MOST_TABLE_ROWS + 5)

    assert _kinds(ragged) == [hm.TABLE, hm.TEXT]
    assert _kinds(too_long) == [hm.TABLE, hm.TEXT]
    [table, _rest] = hm.blocks(too_long, tables=True)
    assert len(table.rows) == hm.MOST_TABLE_ROWS


def test_a_table_takes_short_rules_and_escaped_bars() -> None:
    [table] = hm.blocks("| A | B |\n|-|:-:|\n| a \\| b | c |", tables=True)

    assert [plain(cell) for cell in table.rows[1]] == ["a | b", "c"]


def test_a_tables_cells_are_words_not_markup() -> None:
    [table] = hm.blocks("| A |\n|---|\n| [red]x[/] **b** |", tables=True)

    assert plain(table.rows[1][0]) == "[red]x[/] b"
    assert table.rows[1][0].endswith("[b]b[/b]")


def test_a_pipe_table_is_read_as_one_table_block() -> None:
    found = hm.blocks(
        f"Each rune has a tree.\n\n{RUNES}\n\nIt costs a pawn.", tables=True
    )

    assert [b.kind for b in found] == [hm.TEXT, hm.TABLE, hm.TEXT]
    table = found[1]
    assert [[plain(cell) for cell in row] for row in table.rows] == [
        ["Meaning", "Tree", "Art"],
        ["Health", "Birch", "Creo"],
        ["Sight", "Yew", "Intellego"],
    ]
