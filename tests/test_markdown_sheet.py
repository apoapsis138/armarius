"""A sheet as Markdown (markdown_sheet.py) and Export as Markdown
(forms/markdown.py): each kind renders, the copy rules hold, and what
paper alone needs is left off. No UI library."""

from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import markdown_sheet, viewing
from ars_magica_manager import print_layout as pl
from ars_magica_manager import print_records as pr
from ars_magica_manager.commands import Form
from ars_magica_manager.forms import markdown as md_forms
from ars_magica_manager.models import Familiar, Secret


def _saga():
    saga = _sample_saga_with_covenant()
    saga.familiars.append(Familiar(id="fam1", character_id="char1", name="Grey"))
    return saga


def test_each_kind_renders():
    saga = _saga()
    for kind, record in (
        ("character", saga.characters[0]),
        ("covenant", saga.covenants[0]),
        ("laboratory", saga.laboratories[0]),
        ("familiar", saga.familiars[0]),
    ):
        doc = pr.document(saga, kind, record, viewer=viewing.STORYGUIDE_VIEWER)
        text = markdown_sheet.render(doc)
        assert text.startswith(f"# {record.name}\n"), kind
        assert "\n| --- |" in text or "| --- " in text, kind


def test_a_character_sheet_has_its_tables_and_marks_the_fatigue_level():
    saga = _saga()
    magus = saga.characters[0]
    magus.fatigue_level = "weary"
    text = markdown_sheet.render(pr.document(saga, "character", magus))
    assert "| Intelligence |" in text
    assert "## Abilities" in text and "Magic Theory" in text
    weary = next(line for line in text.splitlines() if line.startswith("| Weary"))
    assert weary.endswith(f"{markdown_sheet.NOW} |")
    # Paper's pencil-in lines and symbols are left off.
    assert "Equipment:" not in text  # no gear, so no line for it
    assert "## Grimoire" in text


def test_a_player_copy_holds_no_secret():
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.secrets = [Secret("Buried", "A demon sleeps under the cellar.")]
    player = markdown_sheet.render(
        pr.document(saga, "covenant", covenant, viewer=viewing.TABLE_VIEWER)
    )
    assert "A demon sleeps" not in player
    storyguide = markdown_sheet.render(
        pr.document(
            saga,
            "covenant",
            covenant,
            pl.PrintOptions(copy=pl.STORYGUIDE_COPY),
            viewing.STORYGUIDE_VIEWER,
        )
    )
    assert "A demon sleeps under the cellar." in storyguide


def test_a_table_cell_with_a_bar_keeps_its_column():
    doc = pl.Document(
        "T",
        "",
        [
            pl.Table(
                (pl.Column("A", 0.5), pl.Column("B", 0.5)),
                ((pl.Cell("x|y"), pl.Cell("z")),),
            )
        ],
    )
    assert "| x\\|y | z |" in markdown_sheet.render(doc)


def test_export_writes_the_file_in_the_folder(tmp_path):
    saga = _saga()
    viewing.use(viewing.STORYGUIDE_VIEWER, saga)
    form = md_forms.export_markdown(saga, saga.characters[0], tmp_path)
    assert isinstance(form, Form)
    keys = [f.key for f in form.fields()]
    assert keys == ["copy", "sheet", "file"]
    values = {f.key: f.value for f in form.fields()}
    said = form.apply(values)
    path = tmp_path / "Leandro.md"
    assert path.read_text(encoding="utf-8").startswith("# Leandro")
    assert str(path) in said[0]


def test_a_browser_copy_downloads_it_and_a_player_is_not_asked_the_copy(tmp_path):
    saga = _saga()
    viewing.use(viewing.TABLE_VIEWER, saga)
    got: list[tuple[str, str]] = []

    def deliver(name: str, words: str) -> list[str]:
        got.append((name, words))
        return ["downloaded"]

    form = md_forms.export_markdown(saga, saga.covenants[0], tmp_path, deliver)
    assert isinstance(form, Form)
    assert [f.key for f in form.fields()] == []
    assert form.apply({}) == ["downloaded"]
    assert got[0][0] == "Test Covenant.md"
    assert not list(tmp_path.iterdir())
