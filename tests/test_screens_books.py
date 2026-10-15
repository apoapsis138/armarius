"""Books on every sheet, importing them from CSV, several at once and duplicates."""

from pathlib import Path

from screen_helpers import (
    _book_names,
    _fill,
    _find_node,
    _is_form,
    _open_workspace,
    _pick_csv,
    _pick_spell,
    _sample_saga_with_covenant,
    _save_dialog,
    _saved_books,
    _select,
    _select_character,
    _select_covenant,
    _show_library_tab,
    _wait_for_screen,
)
from support import build_all_tabs, choose, menu, wait_until
from textual.widgets import (
    Button,
    Collapsible,
    DirectoryTree,
    Input,
    Select,
    Static,
    TabbedContent,
    Tree,
)

from ars_magica_manager import storage
from ars_magica_manager.models import Book, Covenant, Saga
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import (
    ConfirmScreen,
    CsvFilePickerScreen,
    FieldsDialog,
    RemovalPickerScreen,
    SelectableList,
    WorkspaceScreen,
    _CsvDirectoryTree,
)
from ars_magica_manager.tui.screens.steps import ChooseScreen
from ars_magica_manager.tui.screens.widgets import DetailsPanel, section_stop


def _saga_with_books() -> Saga:
    """The sample covenant (Leandro, his lab) with a book held by each kind of
    owner, one in another covenant and one with no owner."""
    saga = _sample_saga_with_covenant()
    saga.covenants.append(Covenant(id="cov2", saga_id="test_saga", name="Elsewhere"))
    saga.books = [
        Book(
            id="b1",
            name="Summa of Flame",
            type="Art Summa",
            art="Ignem",
            level=15,
            quality=17,
            owner_kind="covenant",
            owner_id="cov1",
            description="A **fine** copy.",
        ),
        Book(
            id="b2",
            name="Lab Notes",
            type="Lab Text",
            spell_name="Pilum of Fire",
            level=20,
            owner_kind="laboratory",
            owner_id="lab1",
        ),
        Book(
            id="b3",
            name="Pocket Tract",
            type="Tractatus",
            subject_kind="Ability",
            ability="Magic Theory",
            quality=8,
            owner_kind="character",
            owner_id="char1",
        ),
        Book(
            id="b4",
            name="Far Away",
            type="Other",
            owner_kind="covenant",
            owner_id="cov2",
        ),
        Book(id="b5", name="Lost Folio", type="Other"),
    ]
    return saga


def _books_panel(app) -> str:
    view = app.screen._book_view()
    return str(view.query_one(".books-panel", Static).render())


async def _choose_book(pilot, app, row: int) -> None:
    # A book view just swapped in knows its books before its list mounts.
    assert await wait_until(
        pilot,
        lambda: (
            app.screen._book_view() is not None
            and bool(app.screen._book_view().query(SelectableList))
        ),
    )
    rows = app.screen._book_view().query_one(SelectableList)
    rows.focus()
    await pilot.pause()
    rows.highlighted = row
    await pilot.pause()


async def test_library_tab_lists_every_book_in_the_covenant():
    storage.save_saga(_saga_with_books())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _show_library_tab(pilot, app)
        view = app.screen._covenant_sheet_view
        assert view.query_one("#section-lib-summary", Collapsible).title == "Summary"
        # The covenant's own book plus its lab's and its magus's, not the others.
        assert _book_names(app) == ["Summa of Flame", "Lab Notes", "Pocket Tract"]
        books = app.screen._book_view()
        labels = [label for _, label in books._rows()]
        assert labels[0].endswith("Covenant Library")
        assert labels[1].endswith("Lab: Leandro's S…")  # cut to fit the column
        assert labels[2].endswith("Leandro")
        section = view.query_one("#section-lib-books", Collapsible)
        assert section.title == "Books (3)"

        await _choose_book(pilot, app, 0)
        panel = _books_panel(app)
        assert "Name: Summa of Flame" in panel
        # In play a book shows no Build Points (they're on the Build tab).
        assert "Cost:" not in panel and "Build Points" not in panel
        assert "A fine copy." in panel


async def test_adding_a_book_for_a_laboratory_shows_it_in_the_lab_inventory():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _show_library_tab(pilot, app)
        before = len(_book_names(app))
        await pilot.press("a")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        # A new book starts owned by wherever it's added from.
        assert app.screen.query_one("#fld-owner", Select).value == "covenant:cov1"
        _fill(app, name="Summa [Aquam]", type="Art Summa")
        await pilot.pause()
        _fill(app, art="Aquam", level="10", quality="12", owner="laboratory:lab1")
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(_book_names(app)) > before)
        assert _book_names(app)[-1] == "Summa [Aquam]"

        await _select(pilot, app, ("laboratory", "lab1"))
        lab_view = app.screen._laboratory_sheet_view
        lab_view.query_one(TabbedContent).active = "tab-lab-inventory"
        await pilot.pause()
        assert _book_names(app) == ["Summa [Aquam]"]
        section = lab_view.query_one("#section-lab-books", Collapsible)
        assert section.title == "Books (1)"

    saved = next(b for b in _saved_books().values() if b.name == "Summa [Aquam]")
    assert (saved.type, saved.art, saved.level, saved.quality) == (
        "Art Summa",
        "Aquam",
        10,
        12,
    )
    assert (saved.owner_kind, saved.owner_id) == ("laboratory", "lab1")
    assert (saved.ability, saved.spell_name, saved.subject_kind) == ("", "", "")


async def test_book_form_shows_the_fields_the_type_needs():
    saga = _sample_saga_with_covenant()
    saga.covenants[0].in_creation = True  # Build Points show while creating
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _show_library_tab(pilot, app)
        await pilot.press("a")
        await pilot.pause()
        dialog = app.screen

        def shown() -> set[str]:
            keys = ("subject_kind", "art", "ability", "ability_detail", "spell_id")
            keys += ("level", "quality")
            return {k for k in keys if dialog.query_one(f"#fdw-{k}").display}

        def live() -> str:
            return str(dialog.query_one("#fields-live", Static).render())

        assert shown() == set()
        assert "choose a Type" in live()
        _fill(app, type="Tractatus")
        await pilot.pause()
        assert shown() == {"subject_kind", "quality"}
        _fill(app, subject_kind="Ability")
        await pilot.pause()
        assert shown() == {"subject_kind", "ability", "quality"}
        _fill(app, type="Casting Tablet", name="Tablet")
        await pilot.pause()
        # No spell chosen yet: the spell comes first.
        assert shown() == {"spell_id"}
        await _pick_spell(pilot, app, "Aegis of the Hearth")  # a General spell
        assert shown() == {"spell_id", "level"}
        _fill(app, level="12")
        await pilot.pause()
        # Bought as a pool: this one's 12 levels take 3 lots
        # of 5, at 2 Build Points each.
        assert "comes to 12 levels, 6 Build Points (3 levels unspent)" in live()
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: "Tablet" in _book_names(app))

    saved = next(b for b in _saved_books().values() if b.name == "Tablet")
    # The Tractatus Subject picked earlier was hidden on save, so it's not kept.
    assert (saved.type, saved.spell_id, saved.spell_name, saved.level) == (
        "Casting Tablet",
        "spell_aegis_of_the_hearth",
        "Aegis of the Hearth",
        12,
    )
    assert (saved.subject_kind, saved.quality) == ("", None)


async def test_a_templated_ability_needs_its_detail_and_round_trips():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _show_library_tab(pilot, app)
        await pilot.press("a")
        await _wait_for_screen(pilot, app, FieldsDialog)
        _fill(app, name="Rhine Lore", type="Ability Summa")
        await pilot.pause()
        _fill(app, ability="Area Lore: {region}", level="3", quality="10")
        await pilot.pause()
        assert app.screen.query_one("#fdw-ability_detail").display
        await _save_dialog(pilot, app)
        error = str(app.screen.query_one("#fields-error", Static).render())
        assert "needs its Ability detail" in error
        _fill(app, ability_detail="Rhine Tribunal")
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: "Rhine Lore" in _book_names(app))

        # Editing it again splits the name back into the family + detail.
        await _choose_book(pilot, app, _book_names(app).index("Rhine Lore"))
        await pilot.press("e")
        await pilot.pause()
        assert app.screen.query_one("#fld-ability", Select).value == (
            "Area Lore: {region}"
        )
        assert app.screen.query_one("#fld-ability_detail", Input).value == (
            "Rhine Tribunal"
        )

    saved = next(b for b in _saved_books().values() if b.name == "Rhine Lore")
    assert saved.ability == "Area Lore: Rhine Tribunal"


async def test_an_unowned_book_files_under_the_saga():
    storage.save_saga(_saga_with_books())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        tree = app.screen.query_one("#nav-tree", Tree)
        node = _find_node(tree, ("book_group",))
        assert str(node.label) == "Unassigned Books (1)"

        await _show_library_tab(pilot, app)
        await _choose_book(pilot, app, 0)
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        _fill(app, owner="")
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: "Summa of Flame" not in _book_names(app))
        assert str(_find_node(tree, ("book_group",)).label) == "Unassigned Books (2)"

        await _select(pilot, app, ("book_group",))
        await wait_until(
            pilot, lambda: _book_names(app) == ["Summa of Flame", "Lost Folio"]
        )
        assert _book_names(app) == ["Summa of Flame", "Lost Folio"]
        assert app.screen._active_section() == "section-unassigned-books"
        # Give both back to the covenant: the node goes away.
        for _ in range(2):
            before = len(_book_names(app))
            await _choose_book(pilot, app, 0)
            await pilot.press("e")
            await _wait_for_screen(pilot, app, FieldsDialog)
            assert app.screen.query_one("#fld-owner", Select).value == ""
            _fill(app, owner="covenant:cov1")
            await _save_dialog(pilot, app)
            await wait_until(pilot, lambda b=before: len(_book_names(app)) < b)
        assert _find_node(tree, ("book_group",)) is None

    assert _saved_books()["b5"].owner_id == "cov1"


async def test_renaming_a_character_updates_their_book_list():
    # The book list's Location column kept the old owner name until
    # the sheet was shown again.
    storage.save_saga(_saga_with_books())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_character(pilot, app)
        await build_all_tabs(pilot, app.screen._current_sheet_view())
        await pilot.press("e")  # the top panel: Edit Character Info
        await wait_until(pilot, lambda: _is_form(app.screen, "Edit Character Info"))
        app.screen.query_one("#fld-name", Input).value = "Leandro the Elder"
        app.screen.query_one("#btn-save", Button).press()
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        await pilot.pause()
        shown = app.screen._book_view().query_one(SelectableList)._rows
        rows = " | ".join(label for _, label in shown)
        assert "Leandro the Elder" in rows, rows


async def test_character_books_section_and_delete_confirms():
    storage.save_saga(_saga_with_books())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_character(pilot, app)
        view = app.screen._character_sheet_view
        view.query_one(TabbedContent).active = "tab-inventory"
        await pilot.pause()
        section = view.query_one("#section-books", Collapsible)
        assert section.title == "Books (1)"
        assert _book_names(app) == ["Pocket Tract"]
        await _choose_book(pilot, app, 0)
        assert app.screen._active_section() == "section-books"
        # The Inventory tab's one panel shows the book.
        panel = view.query_one("#inventory-info", Static)
        assert await wait_until(
            pilot, lambda: "Owner: Character: Leandro" in str(panel.render())
        )
        await pilot.press("d")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("n")
        await pilot.pause()
        assert _book_names(app) == ["Pocket Tract"]
        await pilot.press("d")
        await pilot.pause()
        await pilot.press("y")
        await wait_until(pilot, lambda: _book_names(app) == [])
        # Nothing left: d says so instead of opening an empty picker.
        await pilot.press("d")
        await pilot.pause()
        assert not isinstance(app.screen, RemovalPickerScreen)

    assert "b3" not in _saved_books()


_BOOKS_CSV = (
    "name,type,language,author,owner,year_published,description,cost,"
    "art,ability,level,quality,tractatus_type,spell\n"
    "On Flame,Art Summae,Latin,Ignatia,Covenant,1174,Fiery.,27,Ignem,,15,12,,\n"
    "Notes,Tractatus,Latin,,Marcus,,,11,,Penetration,,11,Ability,\n"
    "Pilum,Lab Text,Latin,,,,,4,,,20,,,Pilum of Fire\n"
    "Oddity,Scroll,,,,,,,,,,,,\n"
)


def _write_books_csv(folder) -> str:
    path = folder / "books.csv"
    path.write_text(_BOOKS_CSV, encoding="utf-8")
    return str(path)


async def test_saga_import_offers_books_and_spells_and_files_books_unassigned(tmp_path):
    storage.save_saga(_sample_saga_with_covenant())
    csv_path = _write_books_csv(tmp_path)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _open_workspace(pilot)
        await menu(pilot, app, "m", "Import")
        await wait_until(pilot, lambda: isinstance(app.screen, ChooseScreen))
        await pilot.pause()
        assert [c.label for c in app.screen.choices] == [
            "Books",
            "Spells",
            "Characters",
            "Covenants",
            "Laboratories",
            "A Whole Saga",
            "A Content Pack",
        ]
        await pilot.press("enter")  # Books is the one highlighted
        await wait_until(pilot, lambda: isinstance(app.screen, CsvFilePickerScreen))
        # The explorer starts in the folder the app runs in.
        assert app.screen.query_one("#picker-path", Input).value == str(Path.cwd())

        await _pick_csv(pilot, app, csv_path)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert message.startswith("Import 3 books from books.csv as unassigned books?")
        assert "Row 5 (Oddity): unknown type 'Scroll'." in message
        await pilot.press("y")
        await wait_until(pilot, lambda: len(app.screen.saga.books) == 5)
        tree = app.screen.query_one("#nav-tree", Tree)
        assert str(_find_node(tree, ("book_group",)).label) == "Unassigned Books (3)"

    saved = _saved_books()
    imported = [b for b in saved.values() if b.id not in ("book1", "book2")]
    assert [b.name for b in imported] == ["On Flame", "Notes", "Pilum"]
    # The file's owner column isn't used: a saga import leaves every book unowned.
    assert all(b.owner_kind is None for b in imported)


async def test_library_import_puts_every_book_in_the_covenant(tmp_path):
    storage.save_saga(_sample_saga_with_covenant())
    csv_path = _write_books_csv(tmp_path)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _show_library_tab(pilot, app)
        before = len(_book_names(app))
        await menu(
            pilot, app, "m", "Import"
        )  # straight to the file picker: only books go here
        await _pick_csv(pilot, app, csv_path)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert "into Test Covenant's library?" in message
        await pilot.press("n")  # declining imports nothing
        await pilot.pause()
        assert len(_book_names(app)) == before

        await menu(pilot, app, "m", "Import")
        await _pick_csv(pilot, app, csv_path)
        await pilot.press("y")
        await wait_until(pilot, lambda: len(_book_names(app)) == before + 3)
        assert _book_names(app)[-3:] == ["On Flame", "Notes", "Pilum"]
        assert (
            _find_node(app.screen.query_one("#nav-tree", Tree), ("book_group",)) is None
        )

    imported = [b for b in _saved_books().values() if b.name in ("On Flame", "Notes")]
    assert {(b.owner_kind, b.owner_id) for b in imported} == {("covenant", "cov1")}


async def test_file_picker_browses_folders_and_rejects_other_files(tmp_path):
    storage.save_saga(_sample_saga_with_covenant())
    (tmp_path / "sub").mkdir()
    (tmp_path / "notes.txt").write_text("hi", encoding="utf-8")
    _write_books_csv(tmp_path / "sub")

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await _open_workspace(pilot)
        await menu(pilot, app, "m", "Import")
        await choose(pilot, app, "Books")
        await wait_until(pilot, lambda: isinstance(app.screen, CsvFilePickerScreen))
        picker = app.screen
        for button in picker.query(Button):  # fits a small terminal
            assert button.region.height > 0 and button.region.bottom <= 45, button.id

        box = picker.query_one("#picker-path", Input)
        box.value = str(tmp_path / "sub")
        box.focus()
        await pilot.press("enter")
        await pilot.pause()
        tree = picker.query_one("#picker-tree", DirectoryTree)
        assert Path(tree.path) == tmp_path / "sub"
        picker.query_one("#btn-picker-up", Button).press()
        await pilot.pause()
        assert Path(tree.path) == tmp_path
        assert box.value == str(tmp_path)
        # Only folders and .csv files are listed.
        assert picker.query_one(_CsvDirectoryTree).filter_paths(
            [tmp_path / "sub", tmp_path / "notes.txt", tmp_path / "sub" / "books.csv"]
        ) == [tmp_path / "sub", tmp_path / "sub" / "books.csv"]

        box.value = str(tmp_path / "notes.txt")
        box.focus()
        await pilot.press("enter")
        await pilot.pause()
        error = str(picker.query_one("#picker-error", Static).render())
        assert error == "notes.txt isn't a .csv file."
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)


async def _mark_books(pilot, app, rows: list[int]) -> None:
    """Mark rows of the book list with Space."""
    rows_list = app.screen._book_view().query_one(SelectableList)
    rows_list.focus()
    await pilot.pause()
    for row in rows:
        rows_list.highlighted = row
        await pilot.press("space")
    await pilot.pause()


async def test_space_marks_books_and_d_deletes_them_all_after_confirming():
    storage.save_saga(_saga_with_books())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _show_library_tab(pilot, app)
        await _mark_books(pilot, app, [0, 2, 1, 2])  # the second 2 unmarks it
        view = app.screen._book_view()
        assert [b.name for b in view.checked_books()] == ["Summa of Flame", "Lab Notes"]
        section = app.screen._covenant_sheet_view.query_one(
            "#section-lib-books", Collapsible
        )
        assert section.title.endswith(" - 2 marked")

        await pilot.press("d")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert message == "Are you sure you want to delete 2 books?"
        await pilot.press("n")
        await pilot.pause()
        assert len(_book_names(app)) == 3
        await pilot.press("d")
        await pilot.pause()
        await pilot.press("y")
        await wait_until(pilot, lambda: _book_names(app) == ["Pocket Tract"])
        assert not section.title.endswith("marked")  # the marks went with them

    assert set(_saved_books()) == {"b3", "b4", "b5"}


async def test_e_with_books_marked_changes_only_their_owner():
    storage.save_saga(_saga_with_books())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _show_library_tab(pilot, app)
        await _mark_books(pilot, app, [0, 2])
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        assert [f.key for f in app.screen.fields] == ["_books", "owner"]
        # Different owners: nothing preselected, and one must be chosen.
        assert app.screen.query_one("#fld-owner", Select).value is Select.NULL
        await _save_dialog(pilot, app)
        assert isinstance(app.screen, FieldsDialog)
        _fill(app, owner="laboratory:lab1")
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert message == (
            "Changing ownership of 2 books to Laboratory: Leandro's Sanctum. Continue?"
        )
        await pilot.press("y")
        await wait_until(pilot, lambda: _saved_books()["b3"].owner_kind == "laboratory")

    saved = _saved_books()
    assert {(saved[i].owner_kind, saved[i].owner_id) for i in ("b1", "b3")} == {
        ("laboratory", "lab1")
    }
    assert saved["b1"].level == 15  # nothing else about the books changed


async def test_mark_key_is_only_for_book_lists():
    storage.save_saga(_saga_with_books())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        reputations = view.query_one("#cov-reputations-list", SelectableList)
        assert reputations.check_action("toggle_check", ()) is False
        await _show_library_tab(pilot, app)
        books = app.screen._book_view().query_one(SelectableList)
        assert books.check_action("toggle_check", ()) is True


async def _import_with_answers(pilot, app, csv_path: str, answers: list[str]) -> None:
    await menu(pilot, app, "m", "Import")
    await _pick_csv(pilot, app, csv_path)
    await pilot.press("y")
    for answer in answers:
        await choose(pilot, app, answer)
        await pilot.pause()
    await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))


async def test_importing_duplicates_asks_about_each(tmp_path):
    saga = _sample_saga_with_covenant()
    saga.books = [
        Book(id="x1", name="On Flame", type="Other"),
        Book(id="x2", name="Notes", type="Other"),
        Book(id="x3", name="Pilum", type="Other"),
    ]
    storage.save_saga(saga)
    csv_path = _write_books_csv(tmp_path)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _open_workspace(pilot)
        await menu(pilot, app, "m", "Import")
        await choose(pilot, app, "Books")
        await _pick_csv(pilot, app, csv_path)
        await pilot.press("y")
        await wait_until(pilot, lambda: isinstance(app.screen, ChooseScreen))
        await pilot.pause()
        question = app.screen
        assert "A book named On Flame is already in the saga" in question.picker_title
        assert "2 more duplicate(s) after this one." in question.picker_title
        assert question.choices[0].label == "Skip"  # the safe answer, first
        await choose(pilot, app, "Duplicate")  # add On Flame
        await pilot.pause()
        await choose(pilot, app, "Skip All")  # skip the rest
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        await wait_until(pilot, lambda: len(app.screen.saga.books) == 4)

    names = [b.name for b in storage.load_saga("test_saga").books]
    assert names == ["On Flame", "Notes", "Pilum", "On Flame"]


async def test_duplicate_all_adds_every_duplicate_without_asking_again(tmp_path):
    storage.save_saga(_sample_saga_with_covenant())
    csv_path = _write_books_csv(tmp_path)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _show_library_tab(pilot, app)
        await _import_with_answers(pilot, app, csv_path, [])  # nothing to ask
        await wait_until(pilot, lambda: len(_book_names(app)) == 5)
        # The same file again: all three are duplicates now.
        await _import_with_answers(pilot, app, csv_path, ["Skip", "Duplicate All"])
        await wait_until(pilot, lambda: len(_book_names(app)) == 7)
        assert _book_names(app)[-2:] == ["Notes", "Pilum"]


async def test_library_summary_is_read_only_and_the_list_reaches_the_panel():
    storage.save_saga(_saga_with_books())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _show_library_tab(pilot, app)
        view = app.screen._covenant_sheet_view
        left = str(view.query_one("#lib-summary-left", Static).render())
        right = str(view.query_one("#lib-summary-right", Static).render())
        assert "Summae:" in left and "Tractatus:" in left
        assert "Total Books: 3" in " ".join(left.split())
        assert "Lab Texts:" in right
        assert "Build Points" not in right

        # The list runs down to the details panel, two rows above it (the
        # section's bottom padding and the panel's margin).
        section = view.query_one("#section-lib-books", Collapsible)
        panel = app.screen._book_view().query_one(DetailsPanel)
        assert panel.region.y - section.region.bottom == 1
        assert view.query_one("#section-lib-books-list").region.height > 10

        # Nothing to edit or remove on the Summary; adding a book still works.
        section_stop(view.query_one("#section-lib-summary", Collapsible)).focus()
        await wait_until(
            pilot, lambda: app.screen._active_section() == "section-lib-summary"
        )
        assert app.screen.check_action("edit", ()) is False
        assert app.screen.check_action("remove", ()) is False
        assert app.screen.check_action("add", ()) is True

        # The summary follows edits.
        await _choose_book(pilot, app, 0)
        await pilot.press("d")
        await pilot.pause()
        await pilot.press("y")
        await wait_until(pilot, lambda: len(_book_names(app)) == 2)
        left = str(view.query_one("#lib-summary-left", Static).render())
        assert "Total Books: 2" in left


async def test_the_subject_column_widens_with_the_terminal():
    saga = _saga_with_books()
    saga.books[0].art = "Ignem"
    saga.books[2].ability = "Area Lore: The Rhine Tribunal and its Environs"
    storage.save_saga(saga)

    for width, expected in ((110, 12), (140, 21), (200, 40)):
        app = ArsMagicaManagerApp()
        async with app.run_test(size=(width, 60)) as pilot:
            await _select_covenant(pilot, app)
            await _show_library_tab(pilot, app)
            books = app.screen._book_view()
            await wait_until(pilot, lambda b=books, e=expected: b._subject_cols == e)
            assert books._subject_cols == expected, width
            header = str(books.query_one(".books-header", Static).render())
            assert "Subject" in header and "Art/Ability/Spell" not in header
            # Rows are re-laid out to match the header.
            rows = books.query_one(SelectableList)
            label = rows._rows[2][1]
            # Leandro owns this book; the header carries 4 marker columns.
            assert label.index("Leandro") == header.index("Location") - 4
