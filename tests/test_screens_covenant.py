"""The covenant sheet: saga time, the saga tree, Overview, Boons & Hooks and Reputations."""

import re

from screen_helpers import (
    _find_node,
    _is_form,
    _lab_identity_text,
    _open_cov_section,
    _open_lab_section,
    _open_section,
    _open_workspace,
    _plain_title,
    _saga_with_bare_laboratory,
    _saga_with_configured_covenant,
    _sample_saga_with_covenant,
    _select,
    _select_bh_row,
    _select_character,
    _select_covenant,
    _select_laboratory,
    _wait_for_screen,
)
from support import (
    build_all_tabs,
    close_worksheet,
    menu,
    quiet,
    strip_markup,
    wait_until,
)
from textual.widgets import (
    Button,
    Collapsible,
    Input,
    OptionList,
    Select,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
    Tree,
)

from ars_magica_manager import manors, section_verbs, storage
from ars_magica_manager.models import (
    Character,
    Covenant,
    Saga,
    ScoredTrait,
    Tribunal,
    VirtueFlawInstance,
)
from ars_magica_manager.models.holdings import POSSESSION_KINDS
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import (
    AdvanceSeasonScreen,
    ConfirmScreen,
    FieldsDialog,
    SelectableList,
    WorkspaceScreen,
)
from ars_magica_manager.tui.screens.steps import ChooseScreen

_COVENANT_TABS = (
    "tab-cov-overview",
    "tab-cov-charter",
    "tab-cov-inhabitants",
    "tab-cov-seasons",
    "tab-cov-possessions",
    "tab-cov-economics",
    "tab-cov-manors",
    "tab-cov-library",
    "tab-cov-diary",
    "tab-cov-history",
    "tab-cov-build",
    "tab-secrets",
)


async def test_covenant_sheet_has_info_panel_and_its_tabs():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        assert view is not None

        tabs = view.query_one(TabbedContent)
        assert [pane.id for pane in tabs.query(TabPane)] == list(_COVENANT_TABS)
        assert tabs.active == "tab-cov-overview"

        left = strip_markup(view._info_left_text())
        right = strip_markup(view._info_right_text())
        # Saga-inherited values...
        assert re.search(r"Saga:\s+Pushing the Bounds", left)
        assert re.search(r"Storyguide:\s+Hedda", left)
        assert re.search(r"Current Season:\s+Spring", right)
        assert re.search(r"Current Year:\s+1220", right)
        # ...and the covenant's own.
        assert re.search(r"Year Founded:\s+1100", left)
        assert re.search(r"Aegis of the Hearth:\s+2", left)
        assert re.search(r"Living Conditions \(Magi\):\s+\+3", left)
        assert re.search(r"Aura:\s+4", left)
        assert re.search(r"Tribunal:\s+Rhine", right)
        assert re.search(r"Aegis' Penetration:\s+1", right)
        assert re.search(r"Living Conditions \(Mundane\):\s+-1", right)
        assert re.search(r"Covenant Season:\s+Summer", right)


async def test_covenant_info_panel_layout_is_stable_across_tabs():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        tabbed = view.query_one(TabbedContent)

        for tab_id in _COVENANT_TABS:
            tabbed.active = tab_id
            await pilot.pause()

            info = view.query_one("#section-cov-info").region
            left = view.query_one("#cov-info-left").region
            right = view.query_one("#cov-info-right").region
            assert left.right <= right.x, tab_id  # two columns, side by side
            assert left.y == right.y, tab_id
            assert info.y == view.region.y, tab_id
            # Tab bar directly under the panel; body stays inside the sheet.
            assert tabbed.region.y == info.bottom, tab_id
            assert tabbed.region.bottom <= view.region.bottom, tab_id


async def test_opening_a_covenant_focuses_info_panel_so_edit_hotkey_works():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        assert app.screen._active_section() == "section-cov-info"

        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Covenant")
        await pilot.press("escape")
        await pilot.pause()

        # On the Diary tab 'e' edits a Diary entry; the covenant
        # is still edited via the button.
        view = app.screen._covenant_sheet_view
        view.query_one(TabbedContent).active = "tab-cov-diary"
        await wait_until(pilot, lambda: app.screen._active_section() == "tab-cov-diary")
        assert app.screen._active_section() == "tab-cov-diary"
        view.query_one("#btn-cov-edit", Button).press()
        await _wait_for_screen(
            pilot, app, FieldsDialog
        )  # mounted, before the app closes
        assert _is_form(app.screen, "Edit Covenant")


async def test_edit_covenant_saves_fields_and_labs_inherit_the_aura():
    saga = _saga_with_bare_laboratory()
    saga.tribunals.append(Tribunal(id="rhine", name="Rhine"))
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await pilot.press("e")
        await pilot.pause()
        dialog = app.screen
        assert _is_form(dialog, "Edit Covenant")

        def set_input(field: str, value: str) -> None:
            dialog.query_one(f"#fld-{field.replace('-', '_')}", Input).value = value

        set_input("name", "Dammerstein")
        dialog.query_one("#fld-tribunal_id", Select).value = "rhine"
        set_input("year-founded", "1100")
        set_input("aegis-of-the-hearth", "2")
        set_input("aegis-penetration", "1")
        set_input("living-conditions-magi", "1")
        set_input("living-conditions-mundane", "-2")
        set_input("aura", "3")
        dialog.query_one("#fld-covenant_season", Select).value = "Autumn"
        dialog.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

        view = app.screen._covenant_sheet_view
        assert view.query_one("#section-cov-info", Collapsible).title == "Dammerstein"
        assert "Aura" in view._info_left_text()

        # The lab in this covenant inherits the new base aura.
        await _select(pilot, app, ("laboratory", "lab1"))
        text = _lab_identity_text(app.screen._laboratory_sheet_view)
        assert "Aura: 3 (covenant) +0 (modifier) = 3" in text

    cov = storage.load_saga("test_saga").covenants[0]
    assert (cov.name, cov.tribunal_id, cov.year_founded) == (
        "Dammerstein",
        "rhine",
        1100,
    )
    assert (cov.aegis_of_the_hearth, cov.aegis_penetration) == (2, 1)
    assert (cov.living_conditions_magi, cov.living_conditions_mundane) == (1, -2)
    assert (cov.aura, cov.covenant_season) == (3, "Autumn")


async def test_advance_season_moves_the_whole_saga_forward():
    storage.save_saga(quiet(_saga_with_configured_covenant()))

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        assert "Spring 1220" in app.screen.sub_title

        await pilot.press("t")
        await pilot.pause()
        assert isinstance(app.screen, AdvanceSeasonScreen)
        app.screen.query_one("#btn-advance", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

        # Header, the covenant's inherited panel values, and the saga file.
        assert "Summer 1220" in app.screen.sub_title
        right = app.screen._covenant_sheet_view._info_right_text()
        assert "Summer" in right
        assert "1220" in right

    saga = storage.load_saga("test_saga")
    assert (saga.current_season, saga.current_year) == ("Summer", 1220)


async def test_advancing_past_winter_rolls_the_year_and_cancel_changes_nothing():
    saga = quiet(_saga_with_configured_covenant())
    saga.current_season = "Winter"
    # Wealth to cover the deficit: a broke covenant's labs go unmaintained.
    saga.covenants[0].economics.wealth = 100
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _open_workspace(pilot)  # saga level: 't' works from anywhere

        await pilot.press("t")
        await pilot.pause()
        assert isinstance(app.screen, AdvanceSeasonScreen)
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)
        assert "Winter 1220" in app.screen.sub_title

        await pilot.press("t")
        await pilot.pause()
        app.screen.query_one("#btn-advance", Button).press()
        await pilot.pause()
        # No income, and Sundry is at least 1: a deficit, so it asks first.
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")  # Advance anyway
        assert await wait_until(pilot, lambda: "Spring 1221" in app.screen.sub_title)

    saga = storage.load_saga("test_saga")
    assert (saga.current_season, saga.current_year) == ("Spring", 1221)


async def test_set_date_rolls_back_an_accidental_advance():
    storage.save_saga(quiet(_saga_with_configured_covenant()))

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)

        # Advance by "mistake"...
        await pilot.press("t")
        await pilot.pause()
        app.screen.query_one("#btn-advance", Button).press()
        await pilot.pause()
        assert "Summer 1220" in app.screen.sub_title

        # ...then put it back with Set Date: More, on the saga.
        await _select(pilot, app, ("saga",))
        await menu(pilot, app, "m", "Set Date")
        await pilot.pause()
        assert _is_form(app.screen, "Set the Saga's Date")
        # Pre-filled with the current date.
        assert app.screen.query_one("#fld-season", Select).value == "Summer"
        assert app.screen.query_one("#fld-year", Input).value == "1220"
        app.screen.query_one("#fld-season", Select).value = "Spring"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

        # Everything that inherits the calendar follows.
        assert "Spring 1220" in app.screen.sub_title
        await _select(pilot, app, ("covenant", "cov1"))
        right = app.screen._covenant_sheet_view._info_right_text()
        assert "Spring" in right

    saga = storage.load_saga("test_saga")
    assert (saga.current_season, saga.current_year) == ("Spring", 1220)


async def test_set_date_sets_an_arbitrary_date_from_the_saga_level():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _open_workspace(pilot)  # saga level
        await menu(pilot, app, "m", "Set Date")
        await pilot.pause()
        assert _is_form(app.screen, "Set the Saga's Date")
        app.screen.query_one("#fld-season", Select).value = "Winter"
        app.screen.query_one("#fld-year", Input).value = "1195"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert "Winter 1195" in app.screen.sub_title
        # The saga summary pane (shown at saga level) refreshes too.
        detail = app.screen.query_one("#detail-pane")
        text = " ".join(str(static.render()) for static in detail.query(Static))
        assert "Current date: Winter 1195" in text

    saga = storage.load_saga("test_saga")
    assert (saga.current_season, saga.current_year) == ("Winter", 1195)


def _saga_with_two_covenants() -> Saga:
    saga = _saga_with_bare_laboratory()
    saga.covenants.append(Covenant(id="cov2", saga_id="test_saga", name="Fenghold"))
    return saga


def _parent_data(tree, data):
    node = _find_node(tree, data)
    assert node is not None, f"tree node with data={data!r} not found"
    return node.parent.data


async def test_no_unassigned_groups_when_everything_belongs_to_a_covenant():
    storage.save_saga(_saga_with_two_covenants())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_workspace(pilot)
        tree = app.screen.query_one("#nav-tree", Tree)
        assert _find_node(tree, ("character_group", None)) is None
        assert _find_node(tree, ("laboratory_group", None)) is None


async def test_unassigned_characters_and_labs_are_listed_under_the_saga():
    saga = _saga_with_two_covenants()
    saga.characters[0].covenant_id = None
    saga.laboratories[0].covenant_id = None
    saga.characters.append(
        Character(id="char2", name="Ghost", type="grog", covenant_id="gone")
    )  # points at a covenant that doesn't exist: treated as unassigned
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_workspace(pilot)
        tree = app.screen.query_one("#nav-tree", Tree)

        for kind in ("character_group", "laboratory_group"):
            node = _find_node(tree, (kind, None))
            assert node is not None
            assert node.parent is tree.root  # directly under the saga
        assert _parent_data(tree, ("character", "char1")) == ("character_group", None)
        assert _parent_data(tree, ("character", "char2")) == ("character_group", None)
        assert _parent_data(tree, ("laboratory", "lab1")) == (
            "laboratory_group",
            None,
        )
        assert "Unassigned Characters (2)" in str(
            _find_node(tree, ("character_group", None)).label
        )

        # The bug this fixes: they can actually be selected.
        await _select(pilot, app, ("character", "char1"))
        assert app.screen.selected_character.id == "char1"
        assert app.screen._character_sheet_view is not None
        await _select(pilot, app, ("laboratory", "lab1"))
        assert app.screen.selected_laboratory.id == "lab1"
        assert "Covenant: (none)" in _lab_identity_text(
            app.screen._laboratory_sheet_view
        )

        # The group nodes themselves are selectable and say what they are.
        await _select(pilot, app, ("character_group", None))
        assert app.screen.selected_kind == "character_group"
        assert app.screen.selected_covenant is None
        await _select(pilot, app, ("laboratory_group", None))
        assert app.screen.selected_kind == "laboratory_group"


async def test_character_can_be_moved_out_of_a_covenant_and_back():
    storage.save_saga(_saga_with_two_covenants())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        tree = app.screen.query_one("#nav-tree", Tree)
        assert _parent_data(tree, ("character", "char1")) == ("character_group", "cov1")

        async def set_covenant(value) -> None:
            await _open_section(pilot, app, "section-char-info")
            await pilot.press("e")
            await pilot.pause()
            assert _is_form(app.screen, "Edit Character Info")
            app.screen.query_one("#fld-covenant_id", Select).value = value
            app.screen.query_one("#btn-save", Button).press()
            await pilot.pause()

        # Roll it back to "no covenant": it lands under the saga...
        await set_covenant(Select.NULL)
        tree = app.screen.query_one("#nav-tree", Tree)
        assert _parent_data(tree, ("character", "char1")) == ("character_group", None)
        assert app.screen.selected_covenant is None

        # ...and can be assigned to a different covenant from there.
        await set_covenant("cov2")
        tree = app.screen.query_one("#nav-tree", Tree)
        assert _parent_data(tree, ("character", "char1")) == ("character_group", "cov2")
        assert _find_node(tree, ("character_group", None)) is None  # group gone

    assert storage.load_saga("test_saga").characters[0].covenant_id == "cov2"


async def test_lab_can_be_created_unassigned_or_in_a_covenant():
    storage.save_saga(_saga_with_two_covenants())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_workspace(pilot)  # saga level: no covenant selected

        await menu(pilot, app, "n", "New Laboratory")
        await pilot.pause()
        assert _is_form(app.screen, "Create a New Laboratory")
        assert app.screen.query_one("#fld-covenant_id", Select).value == Select.NULL
        app.screen.query_one("#fld-name", Input).value = "Loose Lab"
        await pilot.click("#btn-save")
        await pilot.pause()
        await close_worksheet(pilot, app)
        assert app.screen.selected_laboratory.name == "Loose Lab"

        # With a covenant selected, the dialog defaults to it.
        await _select(pilot, app, ("covenant", "cov2"))
        await menu(pilot, app, "n", "New Laboratory")
        await pilot.pause()
        assert app.screen.query_one("#fld-covenant_id", Select).value == "cov2"
        app.screen.query_one("#fld-name", Input).value = "Fenghold Lab"
        await pilot.click("#btn-save")
        await pilot.pause()
        await close_worksheet(pilot, app)

        tree = app.screen.query_one("#nav-tree", Tree)
        assert _parent_data(tree, ("laboratory", "loose_lab")) == (
            "laboratory_group",
            None,
        )
        assert _parent_data(tree, ("laboratory", "fenghold_lab")) == (
            "laboratory_group",
            "cov2",
        )

    labs = {lab.id: lab for lab in storage.load_saga("test_saga").laboratories}
    assert labs["loose_lab"].covenant_id is None
    assert labs["fenghold_lab"].covenant_id == "cov2"


async def test_lab_can_be_moved_between_covenants_and_unassigned():
    saga = _saga_with_two_covenants()
    saga.covenants[0].aura = 3
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view
        assert "Aura: 3 (covenant)" in _lab_identity_text(view)

        async def set_covenant(value) -> None:
            await _open_lab_section(pilot, app, "section-lab-identity")
            await pilot.press("e")
            await pilot.pause()
            assert _is_form(app.screen, "Edit Laboratory Identity")
            app.screen.query_one("#fld-covenant_id", Select).value = value
            app.screen.query_one("#btn-save", Button).press()
            await pilot.pause()

        await set_covenant("cov2")
        tree = app.screen.query_one("#nav-tree", Tree)
        assert _parent_data(tree, ("laboratory", "lab1")) == (
            "laboratory_group",
            "cov2",
        )
        text = _lab_identity_text(view)
        assert "Covenant: Fenghold" in text
        assert "Aura: 0 (covenant)" in text  # inherits the new covenant's aura

        await set_covenant(Select.NULL)
        tree = app.screen.query_one("#nav-tree", Tree)
        assert _parent_data(tree, ("laboratory", "lab1")) == ("laboratory_group", None)
        assert "Covenant: (none)" in _lab_identity_text(view)
        assert app.screen.selected_covenant is None

    assert storage.load_saga("test_saga").laboratories[0].covenant_id is None


async def test_a_boon_hook_refresh_rebuilds_economics_once(monkeypatch):
    # Refreshing Boons/Hooks rebuilt the Economics tab twice (once for
    # the info panel's refresh it triggered, once for itself).
    saga = _saga_with_configured_covenant()  # covenant aura 4
    storage.save_saga(saga)

    # Counted on the class: the sheet registers its refreshers as it's made.
    from ars_magica_manager.tui.screens.sheets import CovenantSheetView

    rebuilds = []
    original = CovenantSheetView._rebuild_economics
    monkeypatch.setattr(
        CovenantSheetView,
        "_rebuild_economics",
        lambda self: rebuilds.append(1) or original(self),
    )
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        rebuilds.clear()
        view.covenant.boons_hooks.append(
            VirtueFlawInstance(vf_id="covbh_boon_minor_aura")
        )
        view.refresh_section("section-cov-boons")
        await pilot.pause()
        assert len(rebuilds) == 1
        assert "5 (base 4, +1 Boons)" in str(
            view.query_one("#cov-info-left", Static).render()
        )


def _title_styles(section) -> list[str]:
    """The styles actually applied to a Collapsible's rendered title."""
    return [
        str(span.style) for span in section.query_one("CollapsibleTitle").render().spans
    ]


def _theme_coloured(section) -> bool:
    """Whether a Collapsible's rendered title has any theme colour on it."""
    return any("$text-" in style for style in _title_styles(section))


def _bh_labels(view, kind: str) -> str:
    """The attached Boons or Hooks of `kind`, as displayed, joined."""
    return " | ".join(label for _, label in view._bh_entries(kind))


def _rep_labels(view) -> list[str]:
    """The covenant Reputations rows as displayed."""
    return [label for _, label in view._reputation_rows()]


async def _select_rep_row(pilot, app, list_index: int) -> None:
    view = app.screen._covenant_sheet_view
    await wait_until(pilot, lambda: view.initial_tab_seen)
    await pilot.pause()
    reputations = view.query_one("#cov-reputations-list", SelectableList)
    reputations.focus()
    await pilot.pause()
    reputations.highlighted = list_index
    await pilot.pause()


def _catalog_count(kind: str) -> int:
    """How many entries of `kind` ("Boon"/"Hook") the covenant catalog has."""
    from ars_magica_manager import catalog as _catalog

    return sum(e.type == kind for e in _catalog.load_covenant_boon_hook_catalog())


async def _choose_boon_hook(pilot, app, catalog_id: str) -> None:
    """In the Add a Boon / Hook chooser, take the entry `catalog_id`."""
    assert await wait_until(pilot, lambda: isinstance(app.screen, ChooseScreen))
    picker = app.screen
    assert await wait_until(pilot, lambda: bool(picker.query("#choose-list")))
    picker.dismiss(
        next(
            i
            for i, c in enumerate(picker._all())
            if getattr(c.value, "id", None) == catalog_id
        )
    )


def _offered(saga, section_id: str):
    """The labels of the entries the table's Add offers in `section_id`,
    by catalog id."""
    ops = section_verbs.section_ops(saga, saga.covenants[0], section_id)
    return {c.value.id: strip_markup(c.label) for c in ops.add().choices()}


async def _add_boon_hook_via_picker(
    pilot,
    app,
    section_id: str,
    catalog_id: str,
    detail: str = "",
    description: str = "",
) -> None:
    covenant = app.screen.selected_covenant
    before = len(covenant.boons_hooks)
    await _open_cov_section(pilot, app, section_id)
    await pilot.press("a")
    await _choose_boon_hook(pilot, app, catalog_id)
    assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
    assert await wait_until(pilot, lambda: bool(app.screen.query("#fld-detail")))
    app.screen.query_one("#fld-detail", Input).value = detail
    if description:
        app.screen.query_one("#fld-description", TextArea).text = description
    app.screen.query_one("#btn-save", Button).press()
    await pilot.pause()
    assert isinstance(app.screen, WorkspaceScreen)
    # The dialog's result callback (which stores and saves the entry) can land
    # a beat after the screen switches back, so wait for the real state change.
    await wait_until(pilot, lambda: len(covenant.boons_hooks) > before)
    await pilot.pause()


async def test_edit_covenant_description_is_multi_line_and_persists():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].notes = "A border covenant"
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        assert "A border covenant" in view._description_text()

        await _open_cov_section(pilot, app, "section-cov-description")
        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Covenant Description")
        area = app.screen.query_one(TextArea)
        assert area.text == "A border covenant"  # pre-filled
        area.text = "First line.\nSecond line [with brackets]."
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert "Second line" in view._description_text()

        # Clearing it shows the empty state.
        await pilot.press("e")
        await pilot.pause()
        app.screen.query_one(TextArea).text = ""
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert view._description_text() == "(no description)"

    assert storage.load_saga("test_saga").covenants[0].notes == ""


async def test_boon_picker_lists_only_boons_with_notes_and_asks_for_a_blank_detail():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _open_cov_section(pilot, app, "section-cov-boons")
        await pilot.press("a")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ChooseScreen))

        # Choosing one opens the detail prompt, blank by default.
        await _choose_boon_hook(pilot, app, "covbh_boon_minor_edifice")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        assert await wait_until(pilot, lambda: bool(app.screen.query("#fld-detail")))
        assert app.screen.query_one("#fld-detail", Input).value == ""

        # Cancelling the detail prompt adds nothing.
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))

    assert storage.load_saga("test_saga").covenants[0].boons_hooks == []


def test_the_boon_chooser_lists_only_boons_with_their_notes():
    saga = _saga_with_configured_covenant()
    labels = _offered(saga, "section-cov-boons")
    assert len(labels) == _catalog_count("Boon")  # no Hooks
    assert all("covbh_boon_" in item_id for item_id in labels)
    assert "requires: Castle" in labels["covbh_boon_minor_shell_keep"]
    assert "not with: Road, Urban" in labels["covbh_boon_minor_seclusion"]


async def test_boons_and_hooks_totals_details_and_aura():
    storage.save_saga(_saga_with_configured_covenant())  # covenant aura 4

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        boons = view.query_one("#section-cov-boons", Collapsible)
        hooks = view.query_one("#section-cov-hooks", Collapsible)

        await _add_boon_hook_via_picker(
            pilot,
            app,
            "section-cov-boons",
            "covbh_boon_minor_edifice",
            "Obsidian Crucible",
        )
        assert "Edifice - Obsidian Crucible" in _bh_labels(view, "Boon")
        assert _plain_title(boons) == "Boons (1 pt)"

        await _add_boon_hook_via_picker(
            pilot, app, "section-cov-boons", "covbh_boon_minor_aura"
        )
        await _add_boon_hook_via_picker(
            pilot, app, "section-cov-boons", "covbh_boon_major_wealth"
        )
        assert _plain_title(boons) == "Boons (5 pts)"
        assert "Wealth" in _bh_labels(view, "Boon")  # no detail: just the name
        assert "Wealth -" not in _bh_labels(view, "Boon")
        # The Aura Boon shows up in the info panel straight away.
        assert "5 (base 4, +1 Boons)" in view._info_left_text()

        await _add_boon_hook_via_picker(
            pilot,
            app,
            "section-cov-hooks",
            "covbh_hook_minor_contested_resource",
            "Whispering Well (Vim Vis)",
        )
        await _add_boon_hook_via_picker(
            pilot, app, "section-cov-hooks", "covbh_hook_major_castle"
        )
        # Hooks show the (positive) points they provide.
        assert _plain_title(hooks) == "Hooks (4 pts)"
        assert "Contested Resource - Whispering Well (Vim Vis)" in _bh_labels(
            view, "Hook"
        )
        assert "Edifice" not in _bh_labels(view, "Hook")

    cov = storage.load_saga("test_saga").covenants[0]
    assert [bh.vf_id for bh in cov.boons_hooks] == [
        "covbh_boon_minor_edifice",
        "covbh_boon_minor_aura",
        "covbh_boon_major_wealth",
        "covbh_hook_minor_contested_resource",
        "covbh_hook_major_castle",
    ]
    assert cov.boons_hooks[0].params == {"detail": "Obsidian Crucible"}
    assert cov.boons_hooks[1].params == {}  # blank detail stores nothing


async def test_picker_marks_taken_entries_but_still_offers_them():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_edifice", params={"detail": "A"}),
        VirtueFlawInstance(vf_id="covbh_boon_minor_edifice", params={"detail": "B"}),
        VirtueFlawInstance(vf_id="covbh_boon_minor_wealth"),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        items = _offered(saga, "section-cov-boons")
        assert len(items) == _catalog_count("Boon")  # nothing is hidden
        assert "(taken x2)" in items["covbh_boon_minor_edifice"]
        assert "(taken x1)" in items["covbh_boon_minor_wealth"]
        assert "taken" not in items["covbh_boon_minor_regio"]

        # A second Edifice can be taken (your sheet has two).
        await _open_cov_section(pilot, app, "section-cov-boons")
        await pilot.press("a")
        await _choose_boon_hook(pilot, app, "covbh_boon_minor_edifice")
        assert await wait_until(pilot, lambda: bool(app.screen.query("#fld-detail")))
        app.screen.query_one("#fld-detail", Input).value = "C"
        app.screen.query_one("#btn-save", Button).press()
        await wait_until(
            pilot,
            lambda: len(storage.load_saga("test_saga").covenants[0].boons_hooks) == 4,
        )

    boons = storage.load_saga("test_saga").covenants[0].boons_hooks
    assert [bh.params.get("detail") for bh in boons] == ["A", "B", None, "C"]


async def test_edit_and_remove_target_the_right_boon_or_hook_when_interleaved():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_hook_minor_rival"),
        VirtueFlawInstance(vf_id="covbh_boon_minor_edifice", params={"detail": "A"}),
        VirtueFlawInstance(vf_id="covbh_hook_minor_road"),
        VirtueFlawInstance(vf_id="covbh_boon_minor_wealth", params={"detail": "B"}),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view

        # Edit the SECOND Boon's detail (Wealth), which sits at index 3.
        await _open_cov_section(pilot, app, "section-cov-boons")
        await pilot.press("down")
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        assert app.screen.query_one("#fld-detail", Input).value == "B"  # prefilled
        app.screen.query_one("#fld-detail", Input).value = ""  # clear it
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert "Wealth" in _bh_labels(view, "Boon")
        assert "Wealth -" not in _bh_labels(view, "Boon")  # no detail any more
        assert "Edifice - A" in _bh_labels(view, "Boon")  # the other Boon untouched

        # Remove the SECOND Hook (Road), index 2: the row below the one the
        # section takes focus on, then the delete confirmation.
        await _open_cov_section(pilot, app, "section-cov-hooks")
        await pilot.press("down")
        await pilot.press("d")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await pilot.pause()

    cov = storage.load_saga("test_saga").covenants[0]
    assert [bh.vf_id for bh in cov.boons_hooks] == [
        "covbh_hook_minor_rival",
        "covbh_boon_minor_edifice",
        "covbh_boon_minor_wealth",
    ]
    assert cov.boons_hooks[2].params == {}
    assert cov.boons_hooks[1].params == {"detail": "A"}


async def test_switching_back_to_the_overview_tab_focuses_its_first_section():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        await wait_until(pilot, lambda: view.initial_tab_seen)
        await pilot.pause()

        tabbed = view.query_one(TabbedContent)
        tabbed.active = "tab-cov-diary"  # a flat tab: dispatches on its own id
        # Its first showing builds it: wait for that, or the TabActivated
        # still on its way can switch the tabs back after the next line.
        diary = view.query_one("#tab-cov-diary", TabPane)
        await wait_until(pilot, lambda: len(diary.children) > 0)
        await pilot.pause()
        await wait_until(pilot, lambda: app.screen._active_section() == "tab-cov-diary")
        assert app.screen._active_section() == "tab-cov-diary"

        tabbed.active = "tab-cov-overview"
        await wait_until(
            pilot, lambda: app.screen._active_section() == "section-cov-description"
        )
        assert app.screen._active_section() == "section-cov-description"


def _saga_with_boons_and_hooks(*ids: str) -> Saga:
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [VirtueFlawInstance(vf_id=i) for i in ids]
    return saga


async def test_totals_recolour_when_a_hook_is_added():
    storage.save_saga(_saga_with_boons_and_hooks("covbh_boon_minor_wealth"))

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        boons = view.query_one("#section-cov-boons", Collapsible)
        hooks = view.query_one("#section-cov-hooks", Collapsible)
        assert "[$text-error]" in boons.title  # 1 > 0
        assert "[$text-error]" in hooks.title

        await _add_boon_hook_via_picker(
            pilot, app, "section-cov-hooks", "covbh_hook_minor_rival"
        )
        assert "[$text-success]" in boons.title  # 1 == 1
        assert "[$text-success]" in hooks.title

        await _add_boon_hook_via_picker(
            pilot, app, "section-cov-hooks", "covbh_hook_minor_favors"
        )
        # Adding a Hook re-coloured the Boons title too (1 < 2: plain).
        assert (boons.title, hooks.title) == ("Boons (1 pt)", "Hooks (2 pts)")
        # ...and what is actually painted follows, including the Hooks total
        # whose text ("(2 pts)") changed but which must also recolour when only
        # the colour changes (Textual compares label text, not style).
        assert not _theme_coloured(boons) and not _theme_coloured(hooks)


async def test_a_colour_only_change_repaints_the_title():
    # Hooks stay at 3 points throughout; only the Boons change, so the Hooks
    # title text is identical while its colour must change.
    storage.save_saga(_saga_with_boons_and_hooks("covbh_hook_major_castle"))

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        hooks = view.query_one("#section-cov-hooks", Collapsible)
        assert not _theme_coloured(hooks)  # Boons 0 < Hooks 3: plain

        for boon in ("covbh_boon_major_wealth", "covbh_boon_minor_aura"):
            await _add_boon_hook_via_picker(pilot, app, "section-cov-boons", boon)
            plain = _plain_title(hooks)
            assert plain == "Hooks (3 pts)"  # text never changed
        # Boons (4) > Hooks (3): error colour, though the Hooks text stayed
        # identical.
        assert "$text-error" in _title_styles(hooks)


async def test_boon_hook_rows_have_a_selector_and_fill_the_details_panel():
    storage.save_saga(
        _saga_with_boons_and_hooks(
            "covbh_boon_minor_aura",
            "covbh_boon_minor_edifice",
            "covbh_hook_minor_favors",
            "covbh_boon_minor_shell_keep",
            "covbh_hook_major_castle",
        )
    )

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        boon_list = view.query_one("#cov-boons-list", OptionList)
        hook_list = view.query_one("#cov-hooks-list", OptionList)
        panel = view.query_one("#cov-bh-info", Static)

        def prompts(option_list) -> list[str]:
            return [str(o.prompt) for o in option_list.options]

        # Every row has an (unselected) selector; the panel invites a choice.
        assert len(boon_list.options) == 3 and len(hook_list.options) == 2
        assert all("○" in p and "●" not in p for p in prompts(boon_list))
        assert "Select a Boon or Hook" in str(panel.render())

        # Highlight the second Boon: its marker fills in, the panel shows it.
        boon_list.highlighted = 1
        await pilot.pause()
        assert "●" in prompts(boon_list)[1]
        assert "○" in prompts(boon_list)[0] and "○" in prompts(boon_list)[2]
        text = str(panel.render())
        assert "Name: Edifice" in text
        assert "Type: Fortifications" in text  # the book's type of Boon/Hook
        assert "Tier: Minor Boon (1 pt)" in text
        assert "major building erected to inspire awe" in text  # the rules text

        # Highlighting a Hook moves the selection over: one marker in total.
        hook_list.highlighted = 1
        await pilot.pause()
        assert not any("●" in p for p in prompts(boon_list))
        assert "●" in prompts(hook_list)[1]
        text = str(panel.render())
        assert "Name: Castle" in text
        assert "Type: Fortifications" in text
        assert "Tier: Major Hook (3 pts)" in text


async def test_boon_list_works_from_the_keyboard_and_keeps_add_remove_dispatch():
    storage.save_saga(
        _saga_with_boons_and_hooks("covbh_boon_minor_aura", "covbh_boon_minor_wealth")
    )

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        await wait_until(pilot, lambda: view.initial_tab_seen)
        await pilot.pause()

        boon_list = view.query_one("#cov-boons-list", OptionList)
        boon_list.focus()
        await pilot.pause()
        # Focus inside the Boons section: 'a' still adds a Boon (not a Hook).
        assert app.screen._active_section() == "section-cov-boons"

        await pilot.press("down")
        await pilot.pause()
        assert boon_list.highlighted is not None
        first = boon_list.highlighted
        await pilot.press("down")
        await pilot.pause()
        assert boon_list.highlighted != first
        assert "Name:" in str(view.query_one("#cov-bh-info", Static).render())

        await pilot.press("a")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ChooseScreen))
        assert app.screen.step.title == "Add a Boon"


async def test_adding_a_boon_rebuilds_the_list_and_the_panel_follows():
    storage.save_saga(_saga_with_boons_and_hooks("covbh_boon_minor_aura"))

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        boon_list = view.query_one("#cov-boons-list", OptionList)
        boon_list.highlighted = 0
        await pilot.pause()
        assert "Name: Aura" in str(view.query_one("#cov-bh-info", Static).render())

        await _add_boon_hook_via_picker(
            pilot, app, "section-cov-boons", "covbh_boon_minor_wealth"
        )
        assert len(boon_list.options) == 2
        # One marker, on the row the focused list is on, and the panel
        # shows that row (nothing stale).
        assert sum("●" in str(o.prompt) for o in boon_list.options) == 1
        chosen = view.selected_boon_hook("Boon")
        assert chosen is not None
        shown = str(view.query_one("#cov-bh-info", Static).render())
        assert ("Name: Aura" in shown) == ("●" in str(boon_list.options[0].prompt))


def _panel_text(app) -> str:
    view = app.screen._covenant_sheet_view
    return str(view.query_one("#cov-bh-info", Static).render())


async def test_boon_hook_description_is_saved_and_leads_the_details_panel():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view

        await _add_boon_hook_via_picker(
            pilot,
            app,
            "section-cov-boons",
            "covbh_boon_minor_hidden_resources",
            detail="The Lost Library of the Founder",
            description="Accessible Value: 250 Build Points\n\nLocation: sealed [Muto] wall",
        )
        # Blank description on a second one stores nothing.
        await _add_boon_hook_via_picker(
            pilot, app, "section-cov-boons", "covbh_boon_minor_wealth"
        )

        cov = storage.load_saga("test_saga").covenants[0]
        assert cov.boons_hooks[0].params == {
            "detail": "The Lost Library of the Founder",
            "description": "Accessible Value: 250 Build Points\n\nLocation: sealed [Muto] wall",
        }
        assert cov.boons_hooks[1].params == {}

        # The list still shows only the one-line detail...
        assert "Hidden Resources - The Lost Library of the Founder" in _bh_labels(
            view, "Boon"
        )
        assert "Accessible Value" not in _bh_labels(view, "Boon")

        # ...and the panel shows the user's description BEFORE the rules.
        await _select_bh_row(pilot, app, "Boon", 0)
        text = _panel_text(app)
        assert "Description:" in text and "Rules:" in text
        assert text.index("Accessible Value: 250 Build Points") < text.index("Rules:")
        assert "sealed [Muto] wall" in text  # multi-line, brackets survive
        assert text.index("Description:") < text.index("The covenant has 250 Build")
        assert "Location:" in text

        # No description: no Description heading, just the rules.
        await _select_bh_row(pilot, app, "Boon", 1)
        text = _panel_text(app)
        assert "Description:" not in text
        assert "Rules:" in text


async def test_e_edits_the_selected_boon_directly_without_a_picker():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_edifice", params={"detail": "A"}),
        VirtueFlawInstance(
            vf_id="covbh_boon_minor_edifice",
            params={"detail": "B", "description": "Old text"},
        ),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _select_bh_row(pilot, app, "Boon", 1)  # the second Edifice

        await pilot.press("e")
        await pilot.pause()
        # Straight to the edit dialog for that row -- no "which one?" picker.
        assert isinstance(app.screen, FieldsDialog)
        assert app.screen.query_one("#fld-detail", Input).value == "B"
        assert app.screen.query_one("#fld-description", TextArea).text == "Old text"
        app.screen.query_one("#fld-detail", Input).value = "B2"
        app.screen.query_one("#fld-description", TextArea).text = "New\ntext"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

    boons = storage.load_saga("test_saga").covenants[0].boons_hooks
    assert boons[0].params == {"detail": "A"}  # untouched
    assert boons[1].params == {"detail": "B2", "description": "New\ntext"}


async def test_d_deletes_the_selected_item_only_after_confirmation():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_edifice", params={"detail": "A"}),
        VirtueFlawInstance(
            vf_id="covbh_boon_minor_edifice", params={"detail": "B [x]"}
        ),
        VirtueFlawInstance(vf_id="covbh_boon_minor_wealth"),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        await _select_bh_row(pilot, app, "Boon", 1)

        # Answering No (or Escape) keeps it.
        await pilot.press("d")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert message == "Delete Edifice - B [x]?"  # brackets survive
        await pilot.press("n")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)
        assert len(view._bh_entries("Boon")) == 3

        await pilot.press("d")
        await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()
        assert len(view._bh_entries("Boon")) == 3

        # Yes deletes exactly the selected one, then the panel resets.
        await pilot.press("d")
        await pilot.pause()
        await pilot.press("y")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)
        assert [label for _, label in view._bh_entries("Boon")] == [
            "Edifice - A",
            "Wealth",
        ]
        # The list keeps focus: the row that moved up is chosen and shown.
        assert "Name: Wealth" in _panel_text(app)
        assert _plain_title(view.query_one("#section-cov-boons", Collapsible)) == (
            "Boons (2 pts)"
        )

    cov = storage.load_saga("test_saga").covenants[0]
    assert [bh.vf_id for bh in cov.boons_hooks] == [
        "covbh_boon_minor_edifice",
        "covbh_boon_minor_wealth",
    ]


async def test_delete_confirmation_defaults_to_no_so_a_stray_enter_is_safe():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_wealth")
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _select_bh_row(pilot, app, "Boon", 0)
        await pilot.press("d")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        assert app.screen.focused is app.screen.query_one("#btn-no", Button)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    assert len(storage.load_saga("test_saga").covenants[0].boons_hooks) == 1


async def test_d_acts_on_the_focused_list_not_a_row_chosen_in_the_other():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_wealth"),
        VirtueFlawInstance(vf_id="covbh_hook_minor_rival"),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)

        # A Boon was selected, but d in the Hooks section isn't about it:
        # the Hooks list takes focus on its own row, and d confirms that one.
        await _select_bh_row(pilot, app, "Boon", 0)
        await _open_cov_section(pilot, app, "section-cov-hooks")
        await pilot.press("d")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await pilot.pause()

    cov = storage.load_saga("test_saga").covenants[0]
    assert [bh.vf_id for bh in cov.boons_hooks] == ["covbh_boon_minor_wealth"]


async def test_boon_hook_detail_dialog_with_description_fits_a_small_terminal():
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
        for button in app.screen.query(Button):
            region = button.region
            assert region.height > 0 and region.bottom <= 45, button.id
        await pilot.press("escape")
        await pilot.pause()

        await pilot.press("d")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        for button in app.screen.query(Button):
            region = button.region
            assert region.height > 0 and region.bottom <= 45, button.id


async def test_boon_hook_dialogs_hug_their_content_on_a_tall_terminal():
    """Regression: a bare Horizontal (defaults to 1fr) inside an auto-height
    dialog stretched it to fill the whole window."""
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_wealth")
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _select_covenant(pilot, app)
        await _select_bh_row(pilot, app, "Boon", 0)

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        assert app.screen.query_one("#fields-dialog").region.height < 30
        await pilot.press("escape")
        await pilot.pause()

        await pilot.press("d")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        assert app.screen.query_one("#confirm-dialog").region.height < 12


def _saga_with_reputations(*rows: tuple[str, int]) -> Saga:
    saga = _saga_with_configured_covenant()
    saga.covenants[0].reputations = [ScoredTrait(name=n, score=v) for n, v in rows]
    return saga


async def test_reputation_rows_are_selectable_and_independent_of_the_boon_panel():
    saga = _saga_with_reputations(("Feared", 2), ("Liked", -1), ("Known", 0))
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_wealth")
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        reputations = view.query_one("#cov-reputations-list", SelectableList)

        def prompts() -> list[str]:
            return [str(o.prompt) for o in reputations.options]

        assert len(reputations.options) == 3
        assert reputations.highlighted is None  # nothing chosen on open
        assert all("○" in p and "●" not in p for p in prompts())
        assert _rep_labels(view) == ["Feared: +2", "Liked: -1", "Known: +0"]

        # Choose a Boon first: the panel fills in.
        await _select_bh_row(pilot, app, "Boon", 0)
        assert "Name: Wealth" in _panel_text(app)

        # Choosing a Reputation moves ITS marker and leaves the Boon panel be.
        await _select_rep_row(pilot, app, 1)
        assert "●" in prompts()[1]
        assert "○" in prompts()[0] and "○" in prompts()[2]
        assert view.selected_reputation() == 1
        assert "Name: Wealth" in _panel_text(app)


async def test_reputation_keys_work_from_the_list_without_a_picker():
    storage.save_saga(_saga_with_reputations(("Feared", 2)))

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        await wait_until(pilot, lambda: view.initial_tab_seen)
        await pilot.pause()

        # List focused: the section still owns the keys.
        view.query_one("#cov-reputations-list", SelectableList).focus()
        await pilot.pause()
        assert app.screen._active_section() == "section-cov-reputations"
        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        assert [f.label for f in app.screen.fields][1] == "Score"
        await pilot.press("escape")
        await pilot.pause()

        # The focused list has its first row chosen: 'e' edits it, no
        # "which one?".
        await pilot.press("e")
        await _wait_for_screen(
            pilot, app, FieldsDialog
        )  # mounted, before the app closes
        assert isinstance(app.screen, FieldsDialog)


async def test_a_covenants_interests_leave_manors_and_ships_off_its_sheet():
    saga = _sample_saga_with_covenant()
    saga.covenants[0].interests_off = ["Manors", "Ships"]
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        await build_all_tabs(pilot, view)
        assert not view.query("#" + manors.COVENANT_TAB.tab_id)
        assert not view.query_one("#section-pos-ship").display
        others = [k for k in POSSESSION_KINDS if k != "ship"]
        assert all(view.query_one(f"#section-pos-{k}").display for k in others)
        assert not view.stale()
        view.covenant.interests_off = []
        assert view.stale()
