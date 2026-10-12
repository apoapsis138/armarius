"""Shared widgets: SelectableList, inline emphasis, and catalog types in the picker."""

from screen_helpers import (
    _is_form,
    _lab_identity_text,
    _open_cov_section,
    _saga_with_configured_covenant,
    _select,
    _select_bh_row,
    _select_covenant,
    _wait_for_picker_ready,
)
from support import picker_labels, wait_until
from textual.app import App
from textual.widgets import Button, Input, Static

from ars_magica_manager import storage
from ars_magica_manager.models import VirtueFlawInstance
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import (
    CovenantBoonHookPickerScreen,
    FieldsDialog,
    SelectableList,
)


class _ListHarness(App):
    def __init__(self, rows) -> None:
        super().__init__()
        self._rows = rows
        self.chosen: list[int] = []

    def compose(self):
        yield SelectableList(self._rows, id="the-list")

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        self.chosen.append(event.data_index)


async def test_selectable_list_uses_data_indexes_and_a_single_marker():
    # Data indexes need not be contiguous (a filtered view of a bigger list).
    app = _ListHarness([(3, "alpha"), (7, "beta"), (9, "gamma")])
    async with app.run_test() as pilot:
        widget = app.query_one("#the-list", SelectableList)
        prompts = lambda: [str(o.prompt) for o in widget.options]

        # The list has focus (the app's only widget), so its first row is
        # chosen: a focused list always has a row to act on.
        await pilot.pause()
        assert app.chosen == [3]
        assert "●" in prompts()[0] and "●" not in prompts()[1] + prompts()[2]

        widget.highlighted = 1
        await pilot.pause()
        assert app.chosen == [3, 7]  # the data index, not the row position
        assert widget.selected_data_index == 7
        assert "●" in prompts()[1] and "●" not in prompts()[0] + prompts()[2]

        widget.highlighted = 2
        await pilot.pause()
        assert app.chosen == [3, 7, 9]
        assert sum("●" in p for p in prompts()) == 1  # one marker at a time

        widget.clear_selection()
        await pilot.pause()
        assert widget.selected_data_index is None
        assert not any("●" in p for p in prompts())
        assert app.chosen == [3, 7, 9]  # clearing posts nothing


async def test_selectable_list_set_rows_replaces_everything_and_handles_empty():
    app = _ListHarness([(0, "one"), (1, "two")])
    async with app.run_test() as pilot:
        widget = app.query_one("#the-list", SelectableList)
        widget.highlighted = 1
        await pilot.pause()
        assert widget.selected_data_index == 1

        # The list has focus, so the nearest row to the old one is chosen.
        widget.set_rows([(5, "five")])
        await pilot.pause()
        assert len(widget.options) == 1
        assert widget.selected_data_index == 5
        assert "●" in str(widget.options[0].prompt)

        # Without focus, new rows leave nothing chosen.
        app.set_focus(None)
        await pilot.pause()
        widget.set_rows([(6, "six"), (7, "seven")])
        await pilot.pause()
        assert widget.selected_data_index is None
        assert all("○" in str(option.prompt) for option in widget.options)

        # Empty: one disabled placeholder that can't be chosen.
        widget.focus()
        widget.set_rows([])
        await pilot.pause()
        assert len(widget.options) == 1
        assert widget.options[0].disabled
        assert "none recorded" in str(widget.options[0].prompt)
        assert widget.selected_data_index is None
        assert app.chosen[:3] == [0, 1, 5]


def _styled_words(static) -> set[tuple[str, str]]:
    """(text, style) for every styled span of a rendered Static."""
    content = static.render()
    return {(content.plain[s.start : s.end], str(s.style)) for s in content.spans}


async def test_covenant_description_renders_emphasis_too():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].notes = "A **remote** covenant, *rarely* visited. 5 * 3 stays."
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        static = view.query_one("#cov-description-content", Static)
        assert str(static.render()) == "A remote covenant, rarely visited. 5 * 3 stays."
        assert _styled_words(static) == {("remote", "b"), ("rarely", "i")}


async def test_description_dialogs_mention_the_emphasis_syntax():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_wealth")
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await _select_covenant(pilot, app)
        await _select_bh_row(pilot, app, "Boon", 0)
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        assert "**bold**" in str(app.screen.query_one(".fd-hint", Static).render())
        # Still fits a small terminal with the extra hint line.
        for button in app.screen.query(Button):
            assert button.region.height > 0 and button.region.bottom <= 45, button.id
        await pilot.press("escape")
        await pilot.pause()

        await _open_cov_section(pilot, app, "section-cov-description")
        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Covenant Description")
        assert "*italic*" in str(app.screen.query_one(".fd-hint", Static).render())
        for button in app.screen.query(Button):
            assert button.region.height > 0 and button.region.bottom <= 45, button.id


async def test_picker_lists_boons_in_the_books_type_order_with_the_type_shown():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _open_cov_section(pilot, app, "section-cov-boons")
        await pilot.press("a")
        await pilot.pause()
        await _wait_for_picker_ready(pilot, app)
        labels = list(picker_labels(app.screen).values())

        # The type is part of each label...
        # (the original entry keeps its name, "Edifice"; the book says "Edifices")
        assert "Edifice  [Fortifications, Minor, 1 pt]" in " ".join(labels)
        assert any("Island  [Fortifications, Free]" in label for label in labels)

        # ...and rows follow the book's order: Site first, then Fortifications...
        order = [
            "Site",
            "Fortifications",
            "Resources",
            "Residents",
            "External Relations",
            "Surroundings",
        ]
        seen = [next(c for c in order if f"[{c}," in label) for label in labels]
        assert seen == sorted(seen, key=order.index)
        assert seen[0] == "Site" and seen[-1] == "Surroundings"
        # ...and within a type, Free before Minor before Major.
        fortifications = [l for l in labels if "[Fortifications," in l]
        tiers = [
            next(t for t in ("Free", "Minor", "Major") if f", {t}" in l)
            for l in fortifications
        ]
        assert tiers == sorted(tiers, key=("Free", "Minor", "Major").index)


async def test_picker_search_finds_entries_by_their_type():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _open_cov_section(pilot, app, "section-cov-hooks")
        await pilot.press("a")
        await wait_until(
            pilot, lambda: isinstance(app.screen, CovenantBoonHookPickerScreen)
        )
        picker = app.screen

        def shown() -> list[str]:
            return list(picker_labels(picker).values())

        await _wait_for_picker_ready(pilot, app)

        app.screen.query_one("#picker-search", Input).value = "surroundings"
        await wait_until(
            pilot,
            lambda: (
                all("[Surroundings," in x for x in shown())
                and any(x.startswith("Pilgrimage Site") for x in shown())
            ),
        )
        labels = shown()
        assert labels and all("[Surroundings," in label for label in labels)
        assert any(label.startswith("Pilgrimage Site") for label in labels)


async def test_weak_aura_hook_lowers_the_aura_labs_inherit():
    saga = _saga_with_configured_covenant()  # covenant aura 4
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_hook_minor_weak_aura"),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        assert "3 (base 4, -1 Boons)" in (
            app.screen._covenant_sheet_view._info_left_text()
        )
        await _select(pilot, app, ("laboratory", "lab1"))
        text = _lab_identity_text(app.screen._laboratory_sheet_view)
        assert "Aura: 3 (covenant) +0 (modifier) = 3" in text
