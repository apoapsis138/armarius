"""The terminal's Find (Ctrl+F): a field over the saga's records; typing
narrows them, Enter opens the chosen one in the tree, Esc closes it."""

from __future__ import annotations

from support import everything_saga, wait_until
from textual.widgets import Input

from ars_magica_manager import storage
from ars_magica_manager.models import Book, EnchantedDevice, KnownSpell, Spell
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import WorkspaceScreen
from ars_magica_manager.tui.screens.finder import FinderScreen
from ars_magica_manager.tui.screens.widgets import SelectableList


async def test_ctrl_f_finds_a_record_and_enter_opens_it():
    saga = everything_saga()
    storage.save_saga(saga)
    aeolus = saga.creature("aeolus")
    assert aeolus is not None
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#saga-list").focus()
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        workspace = app.screen

        await pilot.press("ctrl+f")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FinderScreen))
        finder = app.screen
        assert isinstance(finder, FinderScreen)
        assert finder.focused is finder.query_one("#picker-search", Input)
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: app.screen is workspace)

        await pilot.press("ctrl+f")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FinderScreen))
        finder = app.screen
        assert isinstance(finder, FinderScreen)
        await pilot.press(*aeolus.name[:4].lower())
        assert await wait_until(
            pilot, lambda: finder.shown_ids()[:1] == [finder._item_id(_entry(finder))]
        )
        await pilot.press("enter")
        assert await wait_until(
            pilot,
            lambda: (
                (view := workspace._creature_sheet_view) is not None
                and view.creature.id == "aeolus"
            ),
        )
        assert app.screen is workspace


def _entry(finder: FinderScreen):
    """Aeolus's entry in the finder's index."""
    return next(e for e in finder._entries if e.ref.id == "aeolus")


async def test_a_book_device_or_spell_opens_at_its_row():
    """Each opens its holder's sheet on the tab that lists it, its row
    chosen: books, devices and Known Spells, each second in its list so
    the row is not just the first."""
    saga = everything_saga()
    magus = saga.character("mag1")
    assert magus is not None
    second = Spell(
        id="own-ward", name="Ward of Quills", technique="Rego", form="Herbam"
    )
    magus.invented_spells.append(second)
    magus.spells_known.append(KnownSpell(spell_id=second.id))
    saga.enchanted_devices.append(
        EnchantedDevice(
            id="dev-cov-2", name="Quillstaff", holder_kind="covenant", holder_id="cov1"
        )
    )
    saga.books.append(
        Book(
            id="b-char-2",
            name="Quires of Thorn",
            type="Art Summa",
            owner_kind="character",
            owner_id="mag1",
        )
    )
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#saga-list").focus()
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        workspace = app.screen
        cases = [
            # (typed, the list its row is chosen in, that row's label start)
            ("ward of q", "known-spells-list", "Ward of Quills"),
            ("quillst", "section-cov-devices-list", "Quillstaff"),
            ("quires", "section-books-list", "Quires of Thorn"),
            ("wand", "section-lab-devices-list", "Wand"),
            ("summa", "section-lib-books-list", "Summa"),
        ]
        for typed, list_id, label in cases:
            await pilot.press("ctrl+f")
            assert await wait_until(pilot, lambda: isinstance(app.screen, FinderScreen))
            finder = app.screen
            assert isinstance(finder, FinderScreen)
            await pilot.press(*typed)
            wanted = finder._item_id(
                next(e for e in finder._entries if e.name.startswith(label))
            )
            assert await wait_until(
                pilot,
                lambda finder=finder, wanted=wanted: finder.shown_ids()[:1] == [wanted],
            )
            await pilot.press("enter")

            def chosen(list_id: str = list_id, label: str = label) -> bool:
                focused = app.focused
                return (
                    app.screen is workspace
                    and isinstance(focused, SelectableList)
                    and focused.id == list_id
                    and focused.selected_data_index is not None
                    and focused.chosen_text.startswith(label)
                )

            assert await wait_until(pilot, chosen, timeout=4.0), (
                typed,
                app.focused,
                getattr(app.focused, "chosen_text", None),
            )
