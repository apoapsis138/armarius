import pytest

from ars_magica_manager.csv_import import parse_rows, read_text_any, skipped_preview


def test_read_text_any_handles_a_bom_and_windows_1252(tmp_path):
    bom = tmp_path / "bom.csv"
    bom.write_bytes("name\nÆgidius\n".encode("utf-8-sig"))
    assert read_text_any(bom) == "name\nÆgidius\n"
    legacy = tmp_path / "legacy.csv"
    legacy.write_bytes("name\nÆgidius\n".encode("cp1252"))
    assert read_text_any(legacy) == "name\nÆgidius\n"


def _row(row: dict[str, str]) -> str:
    if not row.get("name", "").strip():
        raise ValueError("no name")
    return row["name"].strip()


def test_parse_rows_reads_records_and_reports_bad_rows_and_extra_columns():
    text = "NAME , Colour\nAlpha,red\n,blue\n\nBeta,green\n"
    records, skipped, unused = parse_rows(text, ("name",), ("name",), _row)
    assert records == ["Alpha", "Beta"]
    assert skipped == ["Row 3: no name."]
    assert unused == ["colour"]


def test_parse_rows_needs_its_required_columns():
    with pytest.raises(ValueError, match="no name or type column"):
        parse_rows("colour\nred\n", ("name", "type"), (), _row, missing_joiner=" or ")


def test_skipped_preview_shows_five_then_a_count():
    assert skipped_preview([]) == []
    lines = skipped_preview([f"Row {i}: bad." for i in range(2, 9)])
    assert lines[1] == "[red]7 row(s) will be skipped:[/]"
    assert len(lines) == 2 + 5 + 1 and lines[-1] == "  ...and 2 more."
