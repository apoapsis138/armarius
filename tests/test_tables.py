"""The lists the desktop draws as tables (tables.py): each `*_table` has
the rows of the terminal's padded `*_rows`, in the same order, a cell per
column."""

from __future__ import annotations

from support import everything_saga

from ars_magica_manager import books as bk
from ars_magica_manager import creation, seasons
from ars_magica_manager import enchanted_devices as ed
from ars_magica_manager import lab_texts as lt
from ars_magica_manager import laboratories as labs
from ars_magica_manager import worksheet as ws
from ars_magica_manager.markup import PROBLEM_GLYPH
from ars_magica_manager.models import (
    Book,
    CreationXp,
    DiaryEntry,
    Possession,
    SeasonRecord,
    SeasonRecordLine,
)
from ars_magica_manager.rules import creation as rules
from ars_magica_manager.sheets import character as cs
from ars_magica_manager.tables import Table


def _square(table: Table) -> None:
    """Every row has at most a cell per column, and keys, if any, one per
    row."""
    assert all(len(row) <= len(table.columns) for row in table.rows)
    assert table.keys is None or len(table.keys) == len(table.rows)


def _magus(saga):
    return next(c for c in saga.characters if c.type == "magus")


def test_a_row_is_chosen_by_its_key_or_its_place():
    assert Table(["A"], [["x"], ["y"]]).key(1) == 1
    assert Table(["A"], [["x"], ["y"]], [None, 7]).key(0) is None
    assert Table(["A"], [["x"], ["y"]], [None, 7]).key(1) == 7


def test_personal_gear_is_a_table_per_kind_keyed_by_inventory_place():
    saga = everything_saga()
    magus = _magus(saga)
    magus.inventory = [
        Possession("i1", "item", "Staff"),
        Possession("w1", "weapon", "Sword", gear_type="Long Sword", weapon_attack=4),
        Possession("i2", "item", "Lantern", quantity=2),
    ]
    tables = cs.inventory_tables(magus)
    assert [title for title, _ in tables] == ["Weapons", "Other Items"]
    weapons, items = tables[0][1], tables[1][1]
    assert weapons.columns[:3] == ["Name", "Type", "Quality"]
    assert weapons.rows[0][0] == "Sword" and "+4" in weapons.rows[0]
    assert items.rows == [["Staff", "1"], ["Lantern", "2"]]
    assert items.keys == [0, 2]


def test_raw_vis_is_by_art():
    table = cs.raw_vis_table({"vim": 12, "creo": 3})
    assert table.rows == [["Creo", "3"], ["Vim", "12"]]


def test_the_diary_has_its_rows_in_order():
    diary = [
        DiaryEntry(1219, "Autumn", "Pilum of Fire", activity="Invent Spell"),
        DiaryEntry(1220, "Spring", "A walk"),
    ]
    table = labs.diary_table(diary)
    assert len(table.rows) == len(labs.diary_rows(diary))
    assert table.rows[1] == ["1220", "Spring", "-", "A walk"]
    assert table.columns[table.stretch] == "Entry"


def test_devices_have_device_rows_then_their_effects():
    saga = everything_saga()
    magus = _magus(saga)
    table = ed.device_table(saga, "character", magus.id)
    _square(table)
    assert len(table.rows) == len(ed.device_rows(saga, "character", magus.id)) > 0


def test_a_book_with_a_problem_is_in_the_error_colour():
    saga = everything_saga()
    good = Book(
        id="b1", name="Summa", type="Art Summa", art="Ignem", level=10, quality=11
    )
    bad = Book(id="b2", name="Odd", type="Art Summa", art="Ignem")
    table = bk.book_table(saga, [good, bad])
    _square(table)
    assert table.rows[0][0] == "Summa" and table.rows[0][3:5] == ["10", "11"]
    assert bk.status_problems(bad, saga)
    assert all(cell.startswith("[$text-error]") for cell in table.rows[1])
    assert PROBLEM_GLYPH in table.rows[1][-1]


def test_lab_texts_have_every_column_whole():
    saga = everything_saga()
    lab = saga.laboratories[0]
    reader = saga.character(lab.owner_id)
    text = Book(
        id="t1", name="Lab Text: A Very Long Name For A Spell Indeed", type="Lab Text"
    )
    table = lt.text_table(saga, reader, [text])
    _square(table)
    assert "A Very Long Name For A Spell Indeed" in table.rows[0][0]
    assert table.columns == [
        "Name",
        "Kind",
        "Te",
        "Fo",
        "Lvl",
        "Author",
        "Sigil",
        "Status",
        "Copy",
    ]


def test_seasons_and_planning_match_their_rows():
    saga = everything_saga()
    covenant = saga.covenants[0]
    for kind in ("magus", "companion", "grog"):
        table = seasons.season_table(saga, covenant, kind)
        # The rows have a heading of the seasons.
        assert len(table.rows) + 1 == len(seasons.season_rows(saga, covenant, kind))
        _square(table)
    lab = saga.laboratories[0]
    table = seasons.lab_queue_table(saga, lab)
    assert len(table.rows) == len(seasons.lab_queue_rows(saga, lab)) > 0
    assert table.columns == ["Seasons", "Plan"]


def test_a_season_record_heads_each_covenant():
    saga = everything_saga()
    magus = _magus(saga)
    record = SeasonRecord(
        1220,
        "Spring",
        [
            SeasonRecordLine(magus.id, magus.name, magus.covenant_id, "Study", "x", ""),
            SeasonRecordLine("x", "Bran", None, "", "", ""),
        ],
    )
    table = seasons.record_table(saga, record)
    assert table.keys is not None
    assert [key is None for key in table.keys] == [True, False, True, False]
    assert table.rows[2][0] == "[b]No covenant[/]"
    assert table.rows[3][0] == "Bran" and "nothing planned" in table.rows[3][1]


def test_every_worksheet_list_row_has_its_cells():
    saga = everything_saga()
    covenant = creation.add_covenant(saga, "New Keep")
    magus = creation.add_character(saga, "Anselm", "magus", covenant.id)
    magus.creation_xp.append(CreationXp("childhood", "Brawl", 15))
    lab = creation.add_laboratory(saga, "Cell", 0, covenant.id)
    seen = 0
    for record in (magus, covenant, lab):
        for step in rules.steps_for(record):
            step_list = ws.panel_for(record, step.key).list
            if step_list is None:
                continue
            assert step_list.columns, step.key
            for row in step_list.rows(saga, record):
                assert row.cells is not None, (step.key, row.label)
                assert len(row.cells) <= len(step_list.columns)
                seen += 1
    assert seen > 0
