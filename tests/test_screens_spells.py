"""The saga's Spells view, Lab Texts and Casting Tablets, and importing spells."""

from screen_helpers import (
    _book_names,
    _fill,
    _open_workspace,
    _pick_csv,
    _pick_spell,
    _sample_saga_with_covenant,
    _save_dialog,
    _saved_books,
    _select,
    _select_covenant,
    _show_library_tab,
    _wait_for_screen,
)
from support import choose, menu, screen_lines, wait_until
from textual.widgets import (
    Button,
    Checkbox,
    Collapsible,
    Input,
    Select,
    Static,
    TabbedContent,
)

from ars_magica_manager import catalog, storage
from ars_magica_manager import spells as spl
from ars_magica_manager.models import Spell
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import (
    ConfirmScreen,
    FieldsDialog,
    SelectableList,
    SpellListView,
    WorkspaceScreen,
)


async def _open_spells(pilot, app) -> SpellListView:
    await _open_workspace(pilot)
    await _select(pilot, app, ("saga_content",))
    assert await wait_until(pilot, lambda: app.screen._saga_content_view)
    content = app.screen._saga_content_view
    assert await wait_until(pilot, lambda: content.initial_tab_seen)
    content.query_one(TabbedContent).active = "tab-content-spells"
    await wait_until(pilot, lambda: bool(app.screen.query(SpellListView)))
    return app.screen.query_one(SpellListView)


def _shown_names(view: SpellListView) -> list[str]:
    return [spell.name for spell in view.shown]


async def _choose_spell(pilot, view: SpellListView, name: str) -> None:
    rows = view.query_one("#spell-list", SelectableList)
    rows.focus()
    await pilot.pause()
    rows.highlighted = _shown_names(view).index(name)
    await pilot.pause()


async def test_the_spells_node_lists_the_catalog_with_search_and_filters():
    saga = _sample_saga_with_covenant()
    storage.save_saga(saga)
    # The catalog plus the saga's own spells (this saga has one).
    total = len(catalog.load_spell_catalog()) + len(saga.spells)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _open_workspace(pilot)
        view = await _open_spells(pilot, app)
        section = view.query_one("#section-spells", Collapsible)
        assert section.title == f"Spells ({total} of {total})"

        # Every word, in the name or the description.
        view.query_one("#spell-search", Input).value = "pilum palms"
        await pilot.pause()
        assert _shown_names(view) == ["Pilum of Fire"]
        assert section.title == f"Spells (1 of {total})"

        view.query_one("#spell-search", Input).value = ""
        view.query_one("#spell-technique", Select).value = "Rego"
        view.query_one("#spell-form", Select).value = "Vim"
        view.query_one("#spell-ritual", Select).value = "yes"
        await pilot.pause()
        assert "Aegis of the Hearth" in _shown_names(view)
        assert all(s.ritual for s in view.shown)
        view.query_one("#spell-min-level", Input).value = "100"
        await pilot.pause()
        # General spells pass any level range; the rest are filtered out.
        assert all(s.level is None for s in view.shown)

        await _choose_spell(pilot, view, "Aegis of the Hearth")
        panel = str(view.query_one("#spell-panel-text", Static).render())
        assert "ReVi Gen" in panel and "General (cast at any level)" in panel

        # Catalog spells are read-only.
        await pilot.press("e")
        await pilot.pause()
        assert not isinstance(app.screen, FieldsDialog)
        assert any("read-only" in n.message for n in app._notifications)


async def test_adding_editing_and_deleting_the_sagas_own_spells():
    saga = _sample_saga_with_covenant()
    saga.spells = []  # start with none of the saga's own
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        view = await _open_spells(pilot, app)
        await pilot.press("a")
        await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        live = lambda: str(app.screen.query_one("#fields-live", Static).render())
        assert "Choose a Technique and a Form" in live()
        _fill(
            app,
            name="Lantern [of] Truth",
            technique="Intellego",
            form="Ignem",
            level="15",
            requisites="Rego",
            range="__other__",
            duration="Sun",
            target="Individual",
            ritual=True,
        )
        await pilot.pause()
        assert "In(Re)Ig 15" in live() and "magnitude 3" in live()
        assert app.screen.query_one("#fdw-range_other").display
        await _save_dialog(pilot, app)  # "Other" chosen but not typed
        error = str(app.screen.query_one("#fields-error", Static).render())
        assert "Type the Range" in error
        _fill(app, range_other="Road", requisites="Rego, Bogus")
        await _save_dialog(pilot, app)
        error = str(app.screen.query_one("#fields-error", Static).render())
        assert "Requisites must be Arts" in error
        _fill(app, requisites="Rego")
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(app.screen.saga.spells) == 1)

        spell = app.screen.saga.spells[0]
        assert spell.id == "saga_lantern_of_truth"
        assert (spell.range, spell.requisites, spell.ritual) == ("Road", ["Rego"], True)
        view.query_one("#spell-source", Select).value = "__own__"
        await pilot.pause()
        assert _shown_names(view) == ["Lantern [of] Truth"]

        await _choose_spell(pilot, view, "Lantern [of] Truth")
        await pilot.press("e")
        await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        assert app.screen.query_one("#fld-range", Select).value == "__other__"
        assert app.screen.query_one("#fld-range_other", Input).value == "Road"
        _fill(app, level="", ritual=False)  # make it General
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: app.screen.saga.spells[0].level is None)

        await pilot.press("d")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await wait_until(pilot, lambda: app.screen.saga.spells == [])
        assert _shown_names(view) == []

    assert storage.load_saga("test_saga").spells == []


async def test_choosing_a_spell_gives_a_lab_text_its_level():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _show_library_tab(pilot, app)
        await pilot.press("a")
        await _wait_for_screen(pilot, app, FieldsDialog)
        _fill(app, name="Notes on the Pilum", type="Lab Text")
        await pilot.pause()
        await _save_dialog(pilot, app)  # no spell chosen yet
        error = str(app.screen.query_one("#fields-error", Static).render())
        assert "Choose the spell" in error
        await _pick_spell(pilot, app, "Pilum of Fire")
        button = app.screen.query_one("#fld-spell_id", Button)
        assert "Pilum of Fire" in str(button.label) and "CrIg 20" in str(button.label)
        # A spell with a fixed level: the book's Level isn't asked for.
        assert not app.screen.query_one("#fdw-level").display
        live = str(app.screen.query_one("#fields-live", Static).render())
        # In play: the Level the spell gives, no Build Points.
        assert live == "Level 20, from the spell"
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: "Notes on the Pilum" in _book_names(app))

    saved = next(b for b in _saved_books().values() if b.name == "Notes on the Pilum")
    assert (saved.spell_id, saved.spell_name, saved.level) == (
        "spell_pilum_of_fire",
        "Pilum of Fire",
        20,
    )


async def test_the_spell_picker_lists_the_sagas_own_and_invented_spells():
    saga = _sample_saga_with_covenant()
    saga.characters[0].invented_spells = [
        Spell(
            id="inv_x",
            name="Leandro's Lantern",
            technique="Creo",
            form="Ignem",
            level=5,
        )
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _show_library_tab(pilot, app)
        await pilot.press("a")
        await _wait_for_screen(pilot, app, FieldsDialog)
        _fill(app, name="Lantern notes", type="Lab Text")
        await pilot.pause()
        await _pick_spell(pilot, app, "Lantern")
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: "Lantern notes" in _book_names(app))

    saved = next(b for b in _saved_books().values() if b.name == "Lantern notes")
    assert (saved.spell_id, saved.level) == ("inv_x", 5)


async def _import_spells(pilot, app) -> FieldsDialog:
    """More's Import, Spells: the Import Spells form (its CSV help)."""
    await menu(pilot, app, "m", "Import")
    await choose(pilot, app, "Spells")
    assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
    await pilot.pause()
    return app.screen


async def test_import_data_offers_spells_with_a_helper_and_an_example_file(
    tmp_path, monkeypatch
):
    storage.save_saga(_sample_saga_with_covenant())
    monkeypatch.chdir(tmp_path)  # the app's folder: where the example goes

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _open_workspace(pilot)
        workspace = app.screen
        helper = await _import_spells(pilot, app)
        assert helper.title_text == "Import Spells"
        assert helper.help_id == "import-spells"
        shown = "\n".join(screen_lines(app))
        assert "technique" in shown and "Gen (or blank)" in shown

        helper.query_one("#fld-example", Checkbox).value = True
        helper.query_one("#btn-save", Button).press()
        assert await wait_until(pilot, lambda: app.screen is workspace)
        example = tmp_path / "spells_example.csv"
        assert example.read_text(encoding="utf-8") == spl.EXAMPLE_CSV
        # A second save doesn't overwrite the first.
        helper = await _import_spells(pilot, app)
        helper.query_one("#fld-example", Checkbox).value = True
        helper.query_one("#btn-save", Button).press()
        assert await wait_until(pilot, lambda: app.screen is workspace)
        assert (tmp_path / "spells_example_2.csv").exists()

        helper = await _import_spells(pilot, app)
        helper.query_one("#btn-save", Button).press()
        await _pick_csv(pilot, app, str(example))
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert "Import 2 spells from spells_example.csv" in message
        await pilot.press("y")
        await wait_until(pilot, lambda: len(app.screen.saga.spells) == 3)

    saved = {s.name: s for s in storage.load_saga("test_saga").spells}
    assert saved["Ward of the Quiet Hearth"].id == "saga_ward_of_the_quiet_hearth"
    assert saved["Ward of the Quiet Hearth"].level is None


async def test_importing_spells_twice_asks_about_duplicates(tmp_path):
    saga = _sample_saga_with_covenant()
    saga.spells = []
    storage.save_saga(saga)
    csv_path = tmp_path / "spells.csv"
    csv_path.write_text(spl.EXAMPLE_CSV, encoding="utf-8")

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _open_workspace(pilot)
        for answers in ([], ["Skip All"]):
            helper = await _import_spells(pilot, app)
            helper.query_one("#btn-save", Button).press()
            await _pick_csv(pilot, app, str(csv_path))
            await pilot.press("y")
            for answer in answers:
                picker = await choose(pilot, app, answer)
                assert "A spell named Palm of Warming Flame" in picker.picker_title
                await pilot.pause()
            await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
            await pilot.pause()
        assert len(app.screen.saga.spells) == 2  # the second import added none


async def test_a_spell_import_asks_about_a_name_in_another_case(tmp_path):
    # The preview counts "palm of warming flame" as a duplicate of
    # "Palm of Warming Flame"; the import asks about it too.
    saga = _sample_saga_with_covenant()
    saga.spells = []
    spl.add_own_spell(saga, "Palm of Warming Flame", "Creo", "Ignem")
    storage.save_saga(saga)
    csv_path = tmp_path / "spells.csv"
    csv_path.write_text(
        "name,technique,form,level\npalm of warming flame,Creo,Ignem,5\n",
        encoding="utf-8",
    )

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _open_workspace(pilot)
        helper = await _import_spells(pilot, app)
        helper.query_one("#btn-save", Button).press()
        await _pick_csv(pilot, app, str(csv_path))
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert "1 has the same name as another spell" in message
        await pilot.press("y")
        await choose(pilot, app, "Skip")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        assert [s.name for s in app.screen.saga.spells] == ["Palm of Warming Flame"]


async def test_the_spell_import_helper_fits_a_small_terminal():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await _open_workspace(pilot)
        helper = await _import_spells(pilot, app)
        for button in helper.query(Button):
            assert button.region.height > 0 and button.region.bottom <= 45, button.id
