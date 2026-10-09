"""The Saga Content view: the saga's own sources, and the shared catalogs
and single entries it hides from its pickers."""

from dataclasses import asdict

from support import picker_rows, wait_until
from textual.widgets import Collapsible, Input, Tree

from ars_magica_manager import catalog, sourcebooks, storage
from ars_magica_manager import house_rules as hr
from ars_magica_manager import saga_content as sc
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import Saga, SagaSource
from ars_magica_manager.screens import (
    ConfirmScreen,
    FieldsDialog,
    SelectableList,
    WorkspaceScreen,
)
from ars_magica_manager.screens.pickers import (
    AbilityPickerScreen,
    CatalogEntryPickerScreen,
    VirtueFlawPickerScreen,
)


def _house_rule(saga: Saga, name: str, source: str = "") -> hr.Entry:
    hr.add(
        saga,
        hr.CHARACTER,
        {
            "name": name,
            "type": "Virtue",
            "tier": "Minor",
            "category": "General",
            "repeatable": False,
            "description": "",
            "source": source,
        },
    )
    return saga.custom_virtues_flaws[-1]


def _ids(entries) -> set[str]:
    return {e.id for e in entries}


def teardown_function():
    catalog.use_saga(None)


# -- the saga's own sources --


def test_an_old_save_has_no_sources_and_hides_nothing():
    saga = Saga.from_dict({"id": "s", "name": "S"})
    assert (saga.sources, saga.hidden_catalogs, saga.hidden_entries) == ([], [], {})
    saga.sources.append(SagaSource("HR", "Ours"))
    again = Saga.from_dict(asdict(saga))
    assert again.sources == [SagaSource("HR", "Ours")]


def test_a_source_is_a_book_its_house_rules_cite():
    saga = Saga(id="s", name="S", books_in_play=[])
    assert sc.source_problem(saga, {"abbreviation": "Covenants"})
    assert sc.source_problem(saga, {"abbreviation": "hohtl"})  # another spelling
    source = sc.add_source(saga, {"abbreviation": " HR ", "title": "Ours"})
    assert source.abbreviation == "HR"
    assert saga.books_in_play == ["HR"]  # a new source starts in play
    assert sc.source_problem(saga, {"abbreviation": "hr"})  # taken
    assert sc.source_problem(saga, {"abbreviation": "HR"}, existing=source) is None
    assert sc.every_book(saga)[-1] == "HR"

    entry = _house_rule(saga, "Storm-Touched", source="HR")
    catalog.use_saga(saga)
    assert entry.id in _ids(catalog.load_virtue_flaw_catalog())
    assert sourcebooks.in_play(entry.source, sourcebooks.saga_books(saga))
    # Out of play, like a book: its entries leave the pickers.
    sc.set_books_in_play(saga, [])
    assert not sourcebooks.in_play(entry.source, sourcebooks.saga_books(saga))
    assert "(not in play)" in hr.detail_text(saga, (hr.CHARACTER, entry))

    # A new abbreviation goes with the entries citing it, in play or not.
    sc.set_books_in_play(saga, ["HR"])
    sc.update_source(saga, source, {"abbreviation": "OHR", "title": "Ours"})
    assert entry.source == "OHR"
    assert saga.books_in_play == ["OHR"]
    assert [e.name for e in hr.citing(saga, "OHR")] == ["Storm-Touched"]


def test_every_book_and_source_in_play_is_stored_as_every_book():
    saga = Saga(id="s", name="S")
    sc.add_source(saga, {"abbreviation": "HR"})
    assert saga.books_in_play is None  # every book, sources included
    sc.set_books_in_play(saga, sourcebooks.SUPPLEMENTS)  # all but HR
    assert saga.books_in_play == list(sourcebooks.SUPPLEMENTS)
    assert not sc.is_in_play(saga, "HR")
    sc.set_books_in_play(saga, [*sourcebooks.SUPPLEMENTS, "HR"])
    assert saga.books_in_play is None


# -- hidden catalogs and entries --


def test_a_hidden_entry_leaves_the_pickers_and_comes_back():
    saga = Saga(id="s", name="S")
    athletics = next(a for a in catalog.load_ability_catalog() if a.name == "Athletics")
    sc.hide_entry(saga, "abilities", athletics.id)
    assert catalog.hidden(athletics)
    assert [e.name for _, e in sc.hidden_entries(saga)] == ["Athletics"]
    sc.show_entry(saga, "abilities", athletics.id)
    assert saga.hidden_entries == {}
    assert not catalog.hidden(athletics)


def test_a_hidden_catalog_keeps_the_sagas_own_entries():
    saga = Saga(id="s", name="S")
    own = _house_rule(saga, "Storm-Touched")
    sc.set_catalog_shown(saga, "virtues_flaws", False)
    assert saga.hidden_catalogs == ["virtues_flaws"]
    entries = catalog.load_virtue_flaw_catalog()
    assert [e.id for e in entries if not catalog.hidden(e)] == [own.id]
    # Other catalogs are untouched.
    assert not any(catalog.hidden(a) for a in catalog.load_ability_catalog())
    shared = next(e for e in entries if e.id != own.id)
    assert catalog.VirtueFlawChooser().refusal(shared) == "hidden in this saga"
    sc.set_catalog_shown(saga, "virtues_flaws", True)
    assert saga.hidden_catalogs == []
    assert not catalog.hides_any()


def test_the_rows_say_what_is_offered():
    saga = Saga(id="s", name="S", books_in_play=["Covenants"])
    sc.set_catalog_shown(saga, "spells", False)
    assert sc.catalog_row(saga, "spells").startswith("Spells")
    assert "[dim]no" in sc.catalog_row(saga, "spells")
    assert sc.book_row(saga, sourcebooks.CORE).startswith("always")
    assert sc.book_row(saga, "Covenants").startswith("yes")
    assert "[dim]no" in sc.book_row(saga, "HoH:TL")


async def test_a_picker_leaves_out_what_the_saga_hides_until_f3():
    saga = Saga(id="s", name="S")
    athletics = next(a for a in catalog.load_ability_catalog() if a.name == "Athletics")
    sc.hide_entry(saga, "abilities", athletics.id)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        picker = AbilityPickerScreen()
        await app.push_screen(picker)
        await pilot.pause()

        def listed() -> bool:
            return any(i and i.endswith(athletics.id) for i, _ in picker_rows(picker))

        assert picker_rows(picker) and not listed()
        await pilot.press("f3")
        assert await wait_until(pilot, listed)


async def test_a_hidden_catalog_leaves_only_the_sagas_own_in_its_picker():
    saga = Saga(id="s", name="S")
    own = _house_rule(saga, "Storm-Touched")
    sc.set_catalog_shown(saga, "virtues_flaws", False)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        picker = VirtueFlawPickerScreen()
        await app.push_screen(picker)
        await pilot.pause()
        listed = [item_id for item_id, _ in picker_rows(picker) if item_id]
        assert listed == [f"vf-{own.id}"]


# -- the view --


async def _open_content(pilot, app) -> WorkspaceScreen:
    await pilot.press("enter")
    assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
    workspace = app.screen
    tree = workspace.query_one("#nav-tree", Tree)
    node = next(n for n in tree.root.children if n.data == ("saga_content",))
    tree.select_node(node)
    assert await wait_until(pilot, lambda: workspace._saga_content_view)
    assert await wait_until(
        pilot, lambda: workspace._saga_content_view.initial_tab_seen
    )
    return workspace


async def test_sources_are_added_and_a_cited_one_isnt_deleted():
    saga = Saga(id="test_saga", name="Sources")
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    notices: list[str] = []
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open_content(pilot, app)
        view = workspace._saga_content_view
        original = app.notify
        app.notify = lambda message, *a, **k: (  # type: ignore[method-assign]
            notices.append(str(message)),
            original(message, *a, **k),
        )
        section = view.query_one("#section-saga-sources", Collapsible)
        view.query_one("#content-sources-list", SelectableList).focus()
        assert await wait_until(
            pilot, lambda: workspace._active_section() == "section-saga-sources"
        )
        await pilot.press("a")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        app.screen.query_one("#fld-abbreviation", Input).value = "HR"
        app.screen.query_one("#fld-title", Input).value = "Our house rules"
        app.screen.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: app.screen is workspace)
        assert await wait_until(pilot, lambda: section.title == "Saga Sources (1)")
        books = view.query_one("#content-books-list", SelectableList)
        assert "the saga's own" in books._rows[-1][1]

        # A House Rule cites it: d refuses, and says which.
        _house_rule(workspace.saga, "Storm-Touched", source="HR")
        view.query_one("#content-sources-list", SelectableList).focus()
        await pilot.pause()
        await pilot.press("d")
        assert await wait_until(pilot, lambda: bool(notices))
        assert "Storm-Touched" in notices[-1]
        assert app.screen is workspace

        # Once nothing cites it, d deletes it after asking.
        workspace.saga.custom_virtues_flaws.clear()
        await pilot.press("d")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        assert await wait_until(pilot, lambda: section.title == "Saga Sources (0)")
    assert storage.load_saga("test_saga").sources == []


async def test_an_entry_is_hidden_from_the_catalogs_tab_and_offered_again():
    storage.save_saga(Saga(id="test_saga", name="Hiding"))
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open_content(pilot, app)
        view = workspace._saga_content_view
        await pilot.press("2")
        hidden_list = view.query_one("#content-hidden-list", SelectableList)
        hidden_list.focus()
        assert await wait_until(
            pilot, lambda: workspace._active_section() == "section-hidden-entries"
        )
        await pilot.press("a")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        app.screen.query_one("#fld-catalog").value = "abilities"
        app.screen.query_one("#btn-save").press()
        assert await wait_until(
            pilot, lambda: isinstance(app.screen, CatalogEntryPickerScreen)
        )
        picker = app.screen
        athletics = next(
            a for a in catalog.load_ability_catalog() if a.name == "Athletics"
        )
        assert await wait_until(
            pilot,
            lambda: f"hide-{athletics.id}" in [i for i, _ in picker_rows(picker)],
        )
        picker.dismiss(athletics.id)
        assert await wait_until(pilot, lambda: app.screen is workspace)
        section = view.query_one("#section-hidden-entries", Collapsible)
        assert await wait_until(pilot, lambda: section.title == "Hidden Entries (1)")
        assert "Athletics" in hidden_list._rows[0][1]
        assert catalog.hidden(athletics)
        assert storage.load_saga("test_saga").hidden_entries == {
            "abilities": [athletics.id]
        }

        hidden_list.focus()
        await pilot.pause()
        await pilot.press("d")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        message = str(app.screen.query_one("#confirm-message").render())
        assert message == "Offer Athletics again?"
        await pilot.press("y")
        assert await wait_until(pilot, lambda: section.title == "Hidden Entries (0)")
    assert storage.load_saga("test_saga").hidden_entries == {}
