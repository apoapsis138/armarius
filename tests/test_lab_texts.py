"""The Lab Texts database (STORY-508): kinds, a reader's status, the filter,
the migrations, and the laboratory's Lab Texts list."""

from __future__ import annotations

from dataclasses import asdict

from support import strip_markup, wait_until
from test_list_flows import ListCase, _open
from textual.widgets import Collapsible, Select, Static

from ars_magica_manager import lab_texts as lt
from ars_magica_manager import seasons, storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Book,
    Character,
    Characteristics,
    Covenant,
    Laboratory,
    LabProject,
    LabTextAccess,
    Saga,
    SeasonPlan,
    Spell,
)
from ars_magica_manager.rules import book_seasons as bs
from ars_magica_manager.rules import lab_seasons
from ars_magica_manager.rules.xp import ability_xp, art_xp
from ars_magica_manager.screens import FieldsDialog, SelectableList


def _saga() -> Saga:
    covenant = Covenant(id="cov1", saga_id="test_saga", name="Keep")
    reader = Character(id="mag1", name="Leandro", type="magus", covenant_id="cov1")
    reader.characteristics = Characteristics(intelligence=2)
    reader.abilities = [
        Ability("Magic Theory", xp=ability_xp(3)),
        Ability("Profession: Scribe", xp=ability_xp(1)),
    ]
    reader.arts = {
        "rego": ArtScore(xp=art_xp(8)),
        "animal": ArtScore(xp=art_xp(6)),
    }
    reader.assigned_lab_id = "lab1"
    author = Character(id="mag2", name="Flavia", type="magus", covenant_id="cov1")
    author.hermetic.wizards_sigil = "A smell of rain"
    lab = Laboratory(id="lab1", covenant_id="cov1", name="Tower", owner_id="mag1")
    spell = Spell(
        id="sp1", name="Pilum of Fire", technique="Creo", form="Ignem", level=20
    )

    def text(book_id: str, name: str, **fields) -> Book:
        return Book(
            id=book_id,
            name=name,
            type="Lab Text",
            owner_kind="laboratory",
            owner_id="lab1",
            **fields,
        )

    books = [
        text(
            "t-own",
            "Lab Text: Pilum of Fire",
            text_kind="Spell",
            spell_id="sp1",
            spell_name="Pilum of Fire",
            raw=True,
            author="Leandro",
            author_id="mag1",
        ),
        text(
            "t-wolf",
            "Lab Text: taming Grey Wolf",
            text_kind="Other",
            technique="Rego",
            form="Animal",
            level=15,
            raw=True,
            author="Flavia",
            author_id="mag2",
        ),
        text(
            "t-ring",
            "Lab Text: Warmth (Ring)",
            text_kind="Enchantment",
            technique="Creo",
            form="Ignem",
            level=10,
            effect_rdt="Touch / Sun / Individual",
            device_type="Lesser Enchantment",
            shape_material="tiny gold ring",
            author="Flavia",
            author_id="mag2",
        ),
        text(
            "t-long",
            "Lab Text: Longevity Ritual for Flavia",
            text_kind="Longevity Ritual",
            technique="Creo",
            form="Corpus",
            level=45,
            ritual_subject="Flavia",
            raw=True,
            author="Old Jacobus",
        ),
        Book(
            id="b-other",
            name="Notes",
            type="Other",
            owner_kind="laboratory",
            owner_id="lab1",
        ),
    ]
    return Saga(
        id="test_saga",
        name="Saga",
        covenants=[covenant],
        characters=[reader, author],
        laboratories=[lab],
        spells=[spell],
        books=books,
    )


def _texts(saga: Saga) -> dict[str, Book]:
    return {b.id: b for b in saga.books}


def test_a_laboratorys_lab_texts_are_listed_apart_from_its_other_books():
    saga = _saga()
    assert [b.id for b in lt.texts_of(saga, "laboratory", "lab1")] == [
        "t-own",
        "t-wolf",
        "t-ring",
        "t-long",
    ]
    assert [b.id for b in lt.other_books_of(saga, "laboratory", "lab1")] == ["b-other"]


def test_a_text_takes_its_arts_and_level_from_its_spell_or_itself():
    saga = _saga()
    texts = _texts(saga)
    assert lt.arts(saga, texts["t-own"]) == ("Creo", "Ignem")
    assert lt.level(saga, texts["t-own"]) == 20
    assert lt.arts(saga, texts["t-wolf"]) == ("Rego", "Animal")
    assert lt.level(saga, texts["t-long"]) == 45
    # Only an author with a sheet has a Sigil to show.
    assert lt.sigil(saga, texts["t-wolf"]) == "A smell of rain"
    assert lt.sigil(saga, texts["t-long"]) == ""


def test_status_is_for_one_reader():
    saga = _saga()
    reader, texts = saga.character("mag1"), _texts(saga)

    def status(book_id: str) -> str:
        return lt.status(saga, reader, texts[book_id])

    assert status("t-own") == "Own raw text"
    assert status("t-ring") == "General use"
    assert status("t-wolf") == "Not decoded"
    assert lt.cant_read_tag(saga, reader, texts["t-wolf"]) == (
        " (can't read: decode first)"
    )
    # A decoding under way shows its points.
    key = lab_seasons.decode_key(reader, "mag2")
    saga.lab_projects.append(LabProject("mag1", key, 6))
    assert status("t-wolf") == "Not decoded (6 of 15 points)"
    saga.lab_projects.clear()
    # Read to a lower level: not enough for this text.
    reader.lab_text_access["mag2"] = LabTextAccess(10, "taught")
    assert status("t-wolf") == "Not decoded (taught to 10)"
    assert lt.cant_read_tag(saga, reader, texts["t-wolf"]) == (
        " (can't read: taught to 10)"
    )
    reader.lab_text_access["mag2"] = LabTextAccess(15, "decoded")
    assert status("t-wolf") == "Readable (decoded to 15)"
    assert lt.cant_read_tag(saga, reader, texts["t-wolf"]) == ""
    # An author outside the saga is filed under the typed name.
    reader.lab_text_access["Old Jacobus"] = LabTextAccess(50)
    assert status("t-long") == "Readable (reads to 50)"
    # The author reads her own.
    assert lt.status(saga, saga.character("mag2"), texts["t-wolf"]) == "Own raw text"


def test_copy_shows_a_share_of_a_scribes_season():
    saga = _saga()
    reader, texts = saga.character("mag1"), _texts(saga)
    # Profession: Scribe 1 x 60 levels a season.
    assert lt.copy_text(saga, reader, texts["t-own"]) == (
        "Copy 1/3 season (20 of 60 levels)"
    )
    assert lt.short_copy(saga, reader, texts["t-own"]) == "1/3 season"
    assert lt.copy_text(saga, reader, texts["t-ring"]) == (
        "Copy 1/6 season (10 of 60 levels)"
    )
    assert lt.copy_text(saga, reader, texts["t-wolf"]) == "Copy: decode first"
    assert lt.short_copy(saga, reader, texts["t-wolf"]) == "decode 1st"
    reader.lab_text_access["Old Jacobus"] = LabTextAccess(50)
    assert lt.copy_text(saga, reader, texts["t-long"]) == (
        "Copy 1 season (45 of 60 levels)"
    )
    reader.abilities.pop()
    assert lt.copy_text(saga, reader, texts["t-own"]) == (
        "Copy: needs Profession: Scribe"
    )
    assert lt.short_copy(saga, reader, texts["t-own"]) == "-"


def test_the_filter_narrows_by_kind_art_level_and_readability():
    saga = _saga()
    reader = saga.character("mag1")
    texts = lt.texts_of(saga, "laboratory", "lab1")

    def ids(**wanted) -> list[str]:
        return [b.id for b in lt.filtered(saga, reader, texts, lt.Filter(**wanted))]

    assert ids() == ["t-own", "t-wolf", "t-ring", "t-long"]
    assert ids(kind="Enchantment") == ["t-ring"]
    assert ids(technique="Creo") == ["t-own", "t-ring", "t-long"]
    assert ids(technique="Creo", form="Ignem") == ["t-own", "t-ring"]
    assert ids(min_level=15, max_level=20) == ["t-own", "t-wolf"]
    assert ids(readable=True) == ["t-own", "t-ring"]
    wanted = lt.Filter(kind="Spell", min_level=10, readable=True)
    assert wanted.describe() == "Spell, level 10+, readable"
    assert lt.title(1, 4, wanted) == "Lab Texts (1 of 4: Spell, level 10+, readable)"
    assert lt.title(4, 4, lt.Filter()) == "Lab Texts (4)"
    assert lt.filter_problem(lt.Filter(min_level=20, max_level=10)) == (
        "The lowest level is above the highest."
    )


def test_rows_and_details_show_what_a_text_records():
    saga = _saga()
    reader, texts = saga.character("mag1"), _texts(saga)
    header = lt.table_header()
    row = strip_markup(lt.row_label(saga, reader, texts["t-wolf"]))
    assert header.split() == [
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
    # A narrow list drops the Sigil column (the details panel shows it)
    # before the Name gets too short; a wide one gives Name the room.
    assert lt.columns(72) == lt.Columns(14, sigil=False)
    assert lt.columns(92) == lt.Columns(23, sigil=True)
    assert lt.columns(200) == lt.Columns(34, sigil=True)
    narrow = lt.columns(72)
    assert "Sigil" not in lt.table_header(narrow)
    assert len(strip_markup(lt.row_label(saga, reader, texts["t-wolf"], narrow))) <= 70
    # The "Lab Text: " every text starts with is dropped; columns line up.
    assert row.startswith("taming Grey W")
    assert row[header.index("Kind") - 2 :].split()[:4] == ["Other", "Re", "An", "15"]
    assert row.endswith("Not decoded decode 1st")
    # A text the reader can't use yet is dimmed.
    assert lt.row_label(saga, reader, texts["t-wolf"]).startswith("[dim]")
    assert not lt.row_label(saga, reader, texts["t-ring"]).startswith("[dim]")
    detail = strip_markup(lt.detail_text(saga, reader, texts["t-ring"]))
    assert "Kind: Enchantment   Arts: Creo Ignem   Level: 10" in detail
    assert "Range / Duration / Target: Touch / Sun / Individual" in detail
    assert "Device: Lesser Enchantment   Shape and material: tiny gold ring" in detail
    assert "Author: Flavia   Sigil: A smell of rain" in detail
    assert "Status for Leandro: General use   Copy 1/6 season" in detail
    assert "Using a Lab Text:" in detail
    spell = strip_markup(lt.detail_text(saga, reader, texts["t-own"]))
    assert "Kind: Spell: Pilum of Fire   Arts: Creo Ignem   Level: 20" in spell
    long = strip_markup(lt.detail_text(saga, reader, texts["t-long"]))
    assert "Subject: Flavia" in long and "Author: Old Jacobus" in long


def test_a_readers_access_is_listed_by_author():
    saga = _saga()
    reader = saga.character("mag1")
    assert lt.access_text(saga, reader) == "Reads Lab Texts of: (no one else's)"
    reader.lab_text_access = {
        "mag2": LabTextAccess(20, "decoded"),
        "Old Jacobus": LabTextAccess(15),
    }
    assert lt.access_text(saga, reader).splitlines() == [
        "Reads Lab Texts of:",
        "  Flavia to 20 (decoded)",
        "  Old Jacobus to 15",
    ]
    # A rename shows at once: the entry is filed under her id.
    saga.character("mag2").name = "Flavia of Flambeau"
    assert "Flavia of Flambeau to 20 (decoded)" in lt.access_text(saga, reader)
    assert lt.author_options(saga, reader) == [("Flavia of Flambeau", "mag2")]


def test_a_taming_text_can_be_decoded_now_it_records_its_arts():
    saga = _saga()
    reader = saga.character("mag1")
    plan = SeasonPlan(
        "mag1", 1220, "Spring", bs.DECODE_TEXT, lab_id="lab1", book_id="t-wolf"
    )
    found, work = lab_seasons.work(saga, reader, plan)
    # ReAn 8 + 6 + Int 2 + Magic Theory 3 = 19: level 15 in one season.
    assert found == [] and work.finished
    assert work.access == ("mag1", "mag2", 15)
    seasons.plan_lab_work(saga, plan)
    seasons.apply(saga, seasons.resolve(saga))
    assert reader.lab_text_access == {"mag2": LabTextAccess(15, "decoded")}
    # A text recording neither still can't be.
    _texts(saga)["t-wolf"].technique = ""
    reader.lab_text_access.clear()
    found, _ = lab_seasons.work(saga, reader, plan)
    assert found == [
        "Lab Text: taming Grey Wolf doesn't record its Technique and Form."
    ]


def test_old_saves_get_kinds_and_access_keyed_by_author():
    saga = _saga()
    data = asdict(saga)
    for book in data["books"]:
        book.pop("text_kind")
    reader = next(c for c in data["characters"] if c["id"] == "mag1")
    # Before STORY-508: the author's name, and just the level.
    reader["lab_text_access"] = {"Flavia": 15, "Old Jacobus": 30}
    data["lab_projects"] = [
        {"character_id": "mag1", "spell_id": "decode:mag1:Flavia", "points": 6},
        {"character_id": "mag1", "spell_id": "sp1", "points": 3},
    ]
    loaded = Saga.from_dict(data)
    kinds = {b.id: b.text_kind for b in loaded.books}
    assert kinds == {
        "t-own": "Spell",
        "t-wolf": "Other",
        "t-ring": "Other",
        "t-long": "Other",
        "b-other": "",
    }
    assert loaded.character("mag1").lab_text_access == {
        "mag2": LabTextAccess(15),
        "Old Jacobus": LabTextAccess(30),
    }
    assert [p.spell_id for p in loaded.lab_projects] == ["decode:mag1:mag2", "sp1"]
    # Loading again changes nothing.
    assert asdict(Saga.from_dict(asdict(loaded))) == asdict(loaded)


CASE = ListCase(
    ("laboratory", "lab1"),
    "section-lab-texts",
    "section-lab-texts-list",
    lambda s: [b for b in s.books if b.type == "Lab Text"],
)


async def test_the_lab_sheet_lists_lab_texts_and_filters_them():
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, CASE)
        section = view.query_one("#section-lab-texts", Collapsible)
        assert section.title == "Lab Texts (4)"
        # Its other books keep their own list.
        assert view.query_one("#section-lab-books", Collapsible).title == "Books (1)"
        texts = view.lab_text_view()
        assert [b.id for b in texts.books] == ["t-own", "t-wolf", "t-ring", "t-long"]
        assert workspace._book_view() is texts
        assert workspace.check_action("filter_lab_texts", ())
        await pilot.press("F")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        assert await wait_until(pilot, lambda: bool(app.screen.query("#fld-kind")))
        app.screen.query_one("#fld-technique", Select).value = "Creo"
        app.screen.query_one("#fld-readable").value = True
        await pilot.pause()
        app.screen.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: app.screen is workspace)
        assert await wait_until(
            pilot, lambda: [b.id for b in texts.books] == ["t-own", "t-ring"]
        )
        assert section.title == "Lab Texts (2 of 4: Creo, readable)"
        # The chosen text's details are in the tab's panel, for the owner.
        rows = view.query_one("#section-lab-texts-list", SelectableList)
        rows.focus()
        rows.highlighted = 1
        await pilot.pause()
        await pilot.press("enter")
        panel = view.query_one("#lab-inv-panel", Static)
        assert await wait_until(
            pilot, lambda: "Status for Leandro: General use" in str(panel.render())
        )
        # 'e' edits the chosen text: the book form, with its Kind.
        await pilot.press("e")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        assert await wait_until(pilot, lambda: bool(app.screen.query("#fld-text_kind")))
        assert app.screen.query_one("#fld-text_kind", Select).value == "Enchantment"
        assert app.screen.query_one("#fdw-effect_rdt").display
        assert not app.screen.query_one("#fdw-spell_id").display
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is workspace)
        # 'a' adds a Lab Text here.
        await pilot.press("a")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        assert await wait_until(pilot, lambda: bool(app.screen.query("#fld-type")))
        assert app.screen.query_one("#fld-type", Select).value == "Lab Text"
