"""The sourcebooks in play for each saga: the shared book list,
which entries are in play, the saga setting, and the pickers hiding the
rest."""

from support import picker_rows, wait_until
from textual.widgets import Button, Collapsible, SelectionList, Tree

from ars_magica_manager import catalog, sourcebooks, storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import Saga
from ars_magica_manager.screens import FieldsDialog, SelectableList, WorkspaceScreen
from ars_magica_manager.screens.pickers import (
    LabVirtueFlawPickerScreen,
    SourcebookPickerScreen,
)


def test_every_book_the_catalogs_cite_is_listed():
    cited: set[str] = set()
    for entries in (
        catalog.load_virtue_flaw_catalog(),
        catalog.load_lab_virtue_flaw_catalog(),
        catalog.load_covenant_boon_hook_catalog(),
        catalog.load_ability_catalog(),
        catalog.load_house_catalog(),
        catalog.load_lab_feature_catalog(),
        catalog.load_weapon_catalog(),
        catalog.load_armor_catalog(),
        catalog.load_spell_catalog(),
    ):
        for entry in entries:
            cited |= sourcebooks.books_of(entry.source)
    assert cited <= set(sourcebooks.SOURCEBOOKS), cited - set(sourcebooks.SOURCEBOOKS)


def test_other_spellings_of_a_book_are_the_same_book():
    assert sourcebooks.books_of("ArM5; Covenants") == {"DE", "Covenants"}
    assert sourcebooks.books_of("HoHTL") == {"HoH:TL"}


def test_in_play():
    assert sourcebooks.in_play("RoP:F", None)  # every book
    assert not sourcebooks.in_play("RoP:F", {"TMRE"})
    assert sourcebooks.in_play("RoP:F; TC&TC", {"TC&TC"})  # any of its books
    assert sourcebooks.in_play("ArM5", set())  # the core book, always
    assert sourcebooks.in_play("", set())  # no book: a user-made entry


def test_a_saga_has_every_book_until_narrowed():
    saga = Saga(id="s", name="S")
    assert sourcebooks.saga_books(saga) is None
    assert Saga.from_dict({"id": "s", "name": "S"}).books_in_play is None  # old save
    saga.books_in_play = ["Covenants"]
    assert sourcebooks.saga_books(saga) == {"DE", "Covenants"}


def test_choosing_every_supplement_stores_every_book():
    assert sourcebooks.normalized(sourcebooks.SUPPLEMENTS) is None
    assert sourcebooks.normalized(["TMRE", "App"]) == ["App", "TMRE"]
    assert sourcebooks.normalized([]) == []


def test_summary():
    assert sourcebooks.summary(None) == "All books"
    assert sourcebooks.summary([]) == "Core book only"
    assert sourcebooks.summary(["App"]) == "Core book + 1 supplement"
    assert (
        sourcebooks.summary(["App", "HR"], ["HR"])
        == "Core book + 1 supplement + 1 saga source"
    )


async def test_saga_content_sets_the_books_in_play():
    storage.save_saga(Saga(id="s", name="Matrix", storyguide="Ann"))
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.press("enter")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        workspace = app.screen
        # Edit Saga no longer has the books: Saga Content does.
        await pilot.press("e")
        await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        assert not app.screen.query("#fld-books_in_play")
        await pilot.press("escape")
        await wait_until(pilot, lambda: app.screen is workspace)

        tree = workspace.query_one("#nav-tree", Tree)
        node = next(n for n in tree.root.children if n.data == ("saga_content",))
        tree.select_node(node)
        assert await wait_until(pilot, lambda: workspace._saga_content_view)
        view = workspace._saga_content_view
        section = view.query_one("#section-books-in-play", Collapsible)
        assert await wait_until(
            pilot, lambda: workspace._active_section() == "section-books-in-play"
        )
        every = 1 + len(sourcebooks.SUPPLEMENTS)
        assert section.title == f"Books in Play ({every} of {every})"
        await pilot.press("e")
        await wait_until(pilot, lambda: isinstance(app.screen, SourcebookPickerScreen))
        await pilot.press("f3")  # none
        books = app.screen.query_one("#books-list", SelectionList)
        books.select("Covenants")
        await pilot.pause()
        app.screen.query_one("#btn-save", Button).press()
        await wait_until(pilot, lambda: app.screen is workspace)
        assert await wait_until(
            pilot, lambda: section.title == f"Books in Play (2 of {every})"
        )
        rows = view.query_one("#content-books-list", SelectableList)
        covenants = next(label for _, label in rows._rows if "Covenants" in label)
        assert covenants.startswith("yes")

    assert storage.load_saga("s").books_in_play == ["Covenants"]


def _listed(picker) -> list[str]:
    return [item_id or "" for item_id, _ in picker_rows(picker)]


async def test_a_picker_hides_entries_from_books_not_in_play_until_f3():
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        # The lab catalog is all Covenants: out of play with the core book only.
        picker = LabVirtueFlawPickerScreen(books=frozenset({"DE"}))
        await app.push_screen(picker)
        await pilot.pause()
        assert _listed(picker) == [""]  # the "(nothing matches...)" row
        await pilot.press("f3")
        everything = len(catalog.load_lab_virtue_flaw_catalog())
        assert await wait_until(pilot, lambda: len(_listed(picker)) == everything)

        # With Covenants in play, nothing is hidden.
        shown = LabVirtueFlawPickerScreen(books=frozenset({"DE", "Covenants"}))
        await app.push_screen(shown)
        await pilot.pause()
        assert len(_listed(shown)) == len(catalog.load_lab_virtue_flaw_catalog())
