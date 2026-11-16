"""The covenant's, laboratory's and familiar's printed sheets
(print_records.py): their blocks, the copy each reader gets, and core
tables set for paper, with no UI library."""

from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import print_layout as pl
from ars_magica_manager import print_records as pr
from ars_magica_manager import viewing
from ars_magica_manager.models import (
    CovenantDiaryEntry,
    Familiar,
    Player,
    Secret,
)
from ars_magica_manager.tables import Table as CoreTable
from ars_magica_manager.viewing import STORYGUIDE_VIEWER, TABLE_VIEWER


def _headings(doc: pl.Document) -> list[str]:
    return [b.text for b in doc.blocks if isinstance(b, pl.Heading)]


def _texts(doc: pl.Document) -> str:
    words = []
    for b in doc.blocks:
        for name in ("text", "name", "summary", "note"):
            value = getattr(b, name, None)
            if isinstance(value, str):
                words.append(value)
        if isinstance(b, pl.Table):
            words += [c.text for row in b.rows for c in row]
            words += [name for _, name in b.groups]
    return "\n".join(words)


def _covenant():
    saga = _sample_saga_with_covenant()
    return saga, saga.covenants[0]


# ---------------------------------------------------------------- a covenant


def test_a_covenant_prints_its_chapters_and_not_the_screens():
    saga, covenant = _covenant()
    covenant.notes = "A tower above the Rhine."
    doc = pr.document(saga, "covenant", covenant, viewer=STORYGUIDE_VIEWER)
    headings = _headings(doc)
    assert doc.title == covenant.name
    for chapter in ("Overview", "People", "Covenfolk", "Laboratories", "Treasury"):
        assert any(h.startswith(chapter) for h in headings), chapter
    for screen_only in ("Seasons", "Build", "Manage"):
        assert screen_only not in headings
    assert "A tower above the Rhine." in _texts(doc)


def test_a_player_copy_of_a_covenant_holds_no_unrevealed_secret():
    saga, covenant = _covenant()
    covenant.secrets = [
        Secret("Buried", "A demon sleeps under the cellar."),
        Secret("Known", "The well is cursed.", 1219, "Winter"),
    ]
    player = pr.document(saga, "covenant", covenant, viewer=TABLE_VIEWER)
    assert "A demon sleeps" not in _texts(player)
    assert "The well is cursed." in _texts(player)
    storyguide = pr.document(
        saga,
        "covenant",
        covenant,
        pl.PrintOptions(copy=pl.STORYGUIDE_COPY),
        STORYGUIDE_VIEWER,
    )
    assert "A demon sleeps under the cellar." in _texts(storyguide)


def test_a_long_history_and_diary_print_whole():
    saga, covenant = _covenant()
    covenant.diary = [
        CovenantDiaryEntry(year=1100 + n, name=f"Event {n}") for n in range(60)
    ]
    doc = pr.document(saga, "covenant", covenant, viewer=STORYGUIDE_VIEWER)
    words = _texts(doc)
    assert all(f"Event {n}" in words for n in range(60))
    assert any(h.startswith("Diary (60)") for h in _headings(doc))


def test_a_player_copy_reads_as_the_table_and_then_reads_as_before():
    saga, covenant = _covenant()
    viewing.use(STORYGUIDE_VIEWER, saga)
    pr.document(saga, "covenant", covenant)
    assert viewing.current() is STORYGUIDE_VIEWER


# ---------------------------------------------------------------- a laboratory


def test_a_laboratory_prints_its_owners_lab_totals_with_the_best_in_bold():
    saga = _sample_saga_with_covenant()
    lab = saga.laboratories[0]
    doc = pr.document(saga, "laboratory", lab, viewer=STORYGUIDE_VIEWER)
    headings = _headings(doc)
    assert "Lab Totals" in headings
    assert "Stores" in headings and "Raw Vis" in headings
    (boxes,) = [b for b in doc.blocks if isinstance(b, pl.ScoreBoxes)]
    assert len(boxes.items) == 8
    table = next(
        b
        for b in doc.blocks
        if isinstance(b, pl.Table) and b.rows and b.rows[0][0].text == "Creo"
    )
    bold = [c for row in table.rows for c in row[1:] if c.style == "bold"]
    assert bold, "the best Lab Totals are in bold"
    # Planning is for the screen.
    assert "Planning" not in headings


# ---------------------------------------------------------------- a familiar


def test_a_familiar_prints_its_cords_combat_and_master():
    saga = _sample_saga_with_covenant()
    familiar = Familiar(id="fam", character_id="char1", name="Grey", golden_cord=2)
    saga.familiars.append(familiar)
    doc = pr.document(saga, "familiar", familiar, viewer=STORYGUIDE_VIEWER)
    assert doc.title == "Grey"
    headings = _headings(doc)
    for chapter in ("Cords & Binding", "Combat & Condition"):
        assert chapter in headings
    assert any(isinstance(b, pl.Condition) for b in doc.blocks)
    assert "Leandro" in _texts(doc) or any(
        "Leandro" in v
        for b in doc.blocks
        if isinstance(b, pl.Facts)
        for _, v in b.facts
    )


# ---------------------------------------------------------------- core tables


def test_core_markup_becomes_plain_words_and_their_setting():
    table = CoreTable(
        ["Name", "Income"],
        [["[b]Mill[/]", "[s]5[/]"], ["Heading", ""], ["Farm", "[$text-error]2[/]"]],
        keys=[0, None, 1],
        markup=True,
    )
    printed = pr.from_table(table)
    assert [c.text for c in printed.rows[0]] == ["Mill", "5"]
    assert printed.rows[0][0].style == "bold"
    assert printed.rows[0][1].style == "struck"
    # A colour alone sets nothing: no meaning carried by colour.
    assert printed.rows[1][1].style == ""
    assert printed.groups == ((1, "Heading"),)
    assert abs(sum(c.width for c in printed.columns) - 1) < 1e-9


def test_each_prints_in_its_houses_colours_or_scriptorum():
    saga = _sample_saga_with_covenant()
    magus = saga.characters[0]
    magus.hermetic.house = "house_tremere"
    lab = saga.laboratories[0]
    for record in (magus, lab):
        assert pr.theme_for(saga, record, pl.HOUSE_COLOURS) == "Tremere"
    assert pr.theme_for(saga, saga.covenants[0], pl.HOUSE_COLOURS) == "Scriptorum"
    magus.type = "companion"
    assert pr.theme_for(saga, magus, pl.HOUSE_COLOURS) == "Scriptorum"
    # A theme chosen by name is everyone's.
    assert pr.theme_for(saga, saga.covenants[0], "Bonisagus") == "Bonisagus"
    assert pr.theme_for(saga, magus, "No Such Theme") == "Scriptorum"


def test_a_dark_theme_on_plain_white_prints_its_light_twin():
    assert (
        pr.printed_palette("Scriptorum Dark", textured=True).name == "Scriptorum Dark"
    )
    assert pr.printed_palette("Scriptorum Dark", textured=False).name == "Scriptorum"
    # A dark House with no light twin yet: Scriptorum's colours.
    assert pr.printed_palette("Criamon", textured=False).name == "Scriptorum"
    assert pr.printed_palette("Criamon", textured=True).name == "Criamon"
    # A light theme keeps its colours on white.
    assert pr.printed_palette("Bonisagus", textured=False).name == "Bonisagus"


def test_a_player_prints_the_troupe_in_player_copies_only():
    saga = _sample_saga_with_covenant()
    magus = saga.characters[0]
    pat = Player(id="pat", name="Pat")
    saga.players.append(pat)
    magus.background.player_ids = [pat.id]
    magus.secrets = [Secret("Hidden", "A pact with the Spinner.")]
    asked = pl.PrintOptions(copy=pl.STORYGUIDE_COPY)
    ((doc, _theme),) = pr.troupe_sheets(saga, asked, viewing.viewer_for(pat))
    assert "A pact with the Spinner." not in _texts(doc)
    ((doc, _theme),) = pr.troupe_sheets(saga, asked, STORYGUIDE_VIEWER)
    assert "A pact with the Spinner." in _texts(doc)


def test_kinds_and_file_names():
    saga = _sample_saga_with_covenant()
    assert pr.kind_of(saga.covenants[0]) == "covenant"
    assert pr.kind_of(saga.characters[0]) == "character"
    assert pr.kind_of(saga) is None
    assert pr.file_stem('Leandro: "the Red"?') == "Leandro the Red"
    assert pr.file_stem("///") == "Untitled"
