"""The laboratory sheet: its top panel, specializations, features, vis and inventory."""

import re

from screen_helpers import (
    _choose_lab_row,
    _confirm,
    _is_form,
    _lab_characteristics_text,
    _lab_identity_text,
    _lab_rows,
    _open_lab_section,
    _saga_with_bare_character,
    _saga_with_bare_laboratory,
    _select_character,
    _select_laboratory,
    _wait_for_screen,
)
from support import build_all_tabs, strip_markup, wait_until
from textual.widgets import (
    Button,
    Collapsible,
    Input,
    Select,
    Static,
    TabbedContent,
    TextArea,
)

from ars_magica_manager import storage
from ars_magica_manager.models import (
    LAB_CHARACTERISTICS,
    LAB_SPECIALIZATIONS,
    Book,
    Character,
    DiaryEntry,
    LabCharacteristics,
    LabFeature,
    LabSpecialtyEntry,
    LabSpecialtyGrant,
    NamedDescription,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import (
    ConfirmScreen,
    FieldsDialog,
    LabVirtueFlawPickerScreen,
    SelectableList,
    WorkspaceScreen,
)


def _saga_with_populated_laboratory() -> Saga:
    """A lab with one entry in every editable list (two Raw Vis Arts, so
    sorted order -- aquam, ignem -- is meaningful)."""
    saga = _saga_with_bare_laboratory()
    lab = saga.laboratories[0]
    lab.specialties = [LabSpecialtyEntry("Ignem", 1, "Hearth spirit")]
    lab.virtues_flaws = [VirtueFlawInstance("labvf_lesser_feature", id="vf1")]
    lab.features = [
        LabFeature(
            "feat1", "Arcane Library", None, "vf1", [LabSpecialtyGrant("Texts", 1)]
        )
    ]
    lab.rooms = [NamedDescription(name="Vault", description="Locked")]
    lab.inventory_items = [NamedDescription(name="Silver Mirror", description="Old")]
    lab.raw_vis = {"ignem": 4, "aquam": 2}
    lab.diary = [
        DiaryEntry(year=1220, season="Spring", name="Studied", details="Notes")
    ]
    return saga


async def test_edit_lab_identity_updates_fields_and_owner():
    saga = _saga_with_bare_laboratory()
    saga.characters.append(
        Character(id="char2", name="Guillame", type="magus", covenant_id="cov1")
    )
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        await _open_lab_section(pilot, app, "section-lab-identity")

        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Laboratory Identity")

        app.screen.query_one("#fld-name", Input).value = "Obsidian Crucible"
        app.screen.query_one("#fld-location", Input).value = "Black Forest"
        app.screen.query_one("#fld-owner_id", Select).value = "char2"

        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        text = _lab_identity_text(app.screen._laboratory_sheet_view)
        assert text.splitlines()[0] == "Obsidian Crucible"  # the title
        assert "Location: Black Forest" in text
        assert "Owner: Guillame" in text

    saga = storage.load_saga("test_saga")
    lab = saga.laboratories[0]
    assert lab.name == "Obsidian Crucible"
    assert lab.location == "Black Forest"
    assert lab.owner_id == "char2"
    # Bidirectional sync: the new owner points back, the old one is freed.
    new_owner = next(c for c in saga.characters if c.id == "char2")
    old_owner = next(c for c in saga.characters if c.id == "char1")
    assert new_owner.assigned_lab_id == "lab1"
    assert old_owner.assigned_lab_id is None


async def test_every_character_sheet_section_starts_expanded():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await build_all_tabs(pilot, app.screen._current_sheet_view())
        view = app.screen._character_sheet_view
        sections = list(view.query(Collapsible))
        assert len(sections) >= 10
        assert all(not section.collapsed for section in sections)


async def test_edit_lab_characteristics_updates_manual_values():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        await _open_lab_section(pilot, app, "section-lab-characteristics")

        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Laboratory Characteristics (manual value)")

        app.screen.query_one("#fld-size", Input).value = "2"
        app.screen.query_one("#fld-safety", Input).value = "-1"

        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        view = app.screen._laboratory_sheet_view
        text = _lab_characteristics_text(view)
        # Positive and negative in the theme's colours, zero plain.
        assert re.search(
            r"Size:\s+\[\$text-success\]\+2\[/\] \+0 = \[\$text-success\]\+2\[/\]",
            text,
        )
        assert re.search(
            r"Safety:\s+\[\$text-error\]-1\[/\] \+0 = \[\$text-error\]-1\[/\]", text
        )
        # Values line up in columns once the colour markup is stripped: every
        # row of a column has its '=' in the same place.
        for column in (LAB_CHARACTERISTICS[:4], LAB_CHARACTERISTICS[4:]):
            plain = strip_markup(view._characteristics_column_text(column))
            assert len({line.index("=") for line in plain.splitlines()}) == 1

    saga = storage.load_saga("test_saga")
    characteristics = saga.laboratories[0].characteristics
    assert characteristics.size == 2
    assert characteristics.safety == -1


async def test_lab_top_panel_layout_is_stable_across_tabs():
    """Identity sits above Characteristics, directly above the tab bar,
    fully visible (not clipped), and the tab body stays inside the sheet, on
    every tab. Asserts on-screen geometry, not just widget presence -- the
    original bug was invisible to presence/text assertions."""
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view
        tabbed = view.query_one(TabbedContent)

        for tab_id in (
            "tab-lab-planning",
            "tab-lab-totals",
            "tab-lab-vf",
            "tab-lab-attributes",
            "tab-lab-inventory",
            "tab-lab-diary",
        ):
            tabbed.active = tab_id
            await pilot.pause()

            top = view.query_one("#lab-top-panel").region
            identity = view.query_one("#section-lab-identity").region
            characteristics = view.query_one("#section-lab-characteristics").region

            # Identity above Characteristics, neither clipped by the panel.
            assert identity.y == top.y, tab_id
            assert characteristics.y == identity.bottom, tab_id
            assert characteristics.bottom == top.bottom, tab_id
            # Three columns side by side: derived stats (a row lower, beside
            # Refinement), then the Characteristics four and four.
            # (Content regions: the blank rows are padding.)
            derived = view.query_one("#lab-characteristics-derived").content_region
            left = view.query_one("#lab-characteristics-left").content_region
            right = view.query_one("#lab-characteristics-right").content_region
            assert derived.right <= left.x and left.right <= right.x, tab_id
            assert derived.y == left.y + 1 and left.y == right.y, tab_id
            # Identity's two columns side by side, the Aura line below both.
            id_left = view.query_one("#lab-identity-left").region
            id_right = view.query_one("#lab-identity-right").region
            aura = view.query_one("#lab-identity-aura").region
            assert id_left.right <= id_right.x and id_left.y == id_right.y, tab_id
            assert aura.y >= max(id_left.bottom, id_right.bottom), tab_id
            # Tab bar directly below the top panel, body inside the sheet.
            assert tabbed.region.y == top.bottom, tab_id
            assert tabbed.region.bottom <= view.region.bottom, tab_id


async def test_lab_top_panel_columns_stack_on_a_narrow_pane():
    """At 80x24 the detail pane is too narrow for the columns side by side,
    so each panel stacks them; widening the terminal puts them back."""
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view
        body = view.query_one("#lab-characteristics-body")
        columns = [
            view.query_one(f"#lab-characteristics-{name}")
            for name in ("derived", "left", "right")
        ]
        # The class lands a beat before the re-layout: wait for the layout.
        assert await wait_until(
            pilot,
            lambda: (
                body.has_class("-stacked")
                and len({column.region.x for column in columns}) == 1
            ),
        )

        derived, left, right = (column.content_region for column in columns)
        assert derived.x == left.x == right.x
        assert derived.bottom < left.y and left.bottom < right.y

        await pilot.resize_terminal(160, 50)
        await wait_until(pilot, lambda: not body.has_class("-stacked"))
        assert not view.query_one("#lab-identity-body").has_class("-stacked")


async def test_opening_a_lab_focuses_its_planning_so_edit_hotkey_works():
    """Regression: TabbedContent's own initial TabActivated used to clear the
    focus set on opening a lab, leaving 'e' unavailable until the user
    tabbed into a section by hand. No manual focusing here, on purpose.
    Opening a lab now focuses its Planning tab's seasons, so 'e'
    plans lab work; the Identity panel is still a click (or tab) away."""
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view
        await wait_until(pilot, lambda: view.initial_tab_seen)
        await wait_until(
            pilot, lambda: app.screen._active_section() == "tab-lab-planning"
        )
        assert app.screen._active_section() == "tab-lab-planning"


async def test_clicking_a_lab_top_panel_section_makes_it_active():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_laboratory(pilot, app)
        # Let the sheet finish laying out and take its initial focus, or the
        # click can land on stale coordinates (under load, the header's
        # palette button).
        view = app.screen._laboratory_sheet_view
        await wait_until(pilot, lambda: view.initial_tab_seen)
        await wait_until(
            pilot, lambda: app.screen._active_section() == "tab-lab-planning"
        )
        await pilot.pause()

        await pilot.click("#lab-characteristics-left")
        await wait_until(
            pilot,
            lambda: app.screen._active_section() == "section-lab-characteristics",
        )
        assert app.screen._active_section() == "section-lab-characteristics"

        await pilot.press("e")
        await _wait_for_screen(
            pilot, app, FieldsDialog
        )  # mounted, before the app closes
        assert _is_form(app.screen, "Edit Laboratory Characteristics (manual value)")


async def test_lab_top_panel_edit_buttons_open_edit_dialogs():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view

        view.query_one("#btn-lab-identity-edit", Button).press()
        await pilot.pause()
        assert _is_form(app.screen, "Edit Laboratory Identity")
        await pilot.press("escape")
        await pilot.pause()

        view.query_one("#btn-lab-characteristics-edit", Button).press()
        await _wait_for_screen(
            pilot, app, FieldsDialog
        )  # mounted, before the app closes
        assert _is_form(app.screen, "Edit Laboratory Characteristics (manual value)")


async def test_lab_top_panel_sections_are_open_and_cannot_be_collapsed():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view

        for section_id in ("section-lab-identity", "section-lab-characteristics"):
            collapsible = view.query_one(f"#{section_id}", Collapsible)
            assert not collapsible.collapsed

            title = collapsible.query_one("CollapsibleTitle")
            title.focus()
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            assert not collapsible.collapsed

            await pilot.click(title)
            await pilot.pause()
            assert not collapsible.collapsed


async def test_add_and_remove_a_specialization_source():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view
        await _open_lab_section(pilot, app, "section-lab-specialties")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        app.screen.query_one("#fld-specialization", Select).value = "Terram"
        app.screen.query_one("#fld-source", Input).value = "Subterranean"
        await pilot.click("#btn-save")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))

        assert _lab_rows(view, "lab-specialties-list") == ["Terram  +1  Subterranean"]
        assert _lab_rows(view, "lab-specializations-list") == [
            "Activity (0 of 2)",
            "Art (1 of 4)",
            "Terram  +1",
        ]

        await _choose_lab_row(pilot, view, "lab-specialties-list", 0)
        await pilot.press("d")
        await _confirm(pilot, app, "n")
        assert storage.load_saga("test_saga").laboratories[0].specialties
        await pilot.press("d")
        await _confirm(pilot, app, "y")
        assert _lab_rows(view, "lab-specializations-list") == [
            "Activity (0 of 2)",
            "Art (0 of 4)",
        ]

    assert storage.load_saga("test_saga").laboratories[0].specialties == []


def _saga_with_specializations(*entries: tuple[str, int]) -> Saga:
    saga = _saga_with_bare_laboratory()
    saga.laboratories[0].specialties = [
        LabSpecialtyEntry(name, points, "Notes") for name, points in entries
    ]
    return saga


async def test_space_turns_a_specialization_off_and_on_within_the_caps():
    # Two Techniques already count, so a third can't be turned on.
    saga = _saga_with_specializations(("Creo", 1), ("Rego", 2), ("Muto", 1))
    saga.laboratories[0].dropped_specializations = ["Muto"]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view
        await _open_lab_section(pilot, app, "section-lab-specializations")
        grid = view.query_one("#lab-specializations-list", SelectableList)
        muto = LAB_SPECIALIZATIONS.index("Muto")
        rego = LAB_SPECIALIZATIONS.index("Rego")
        grid.focus()

        await _choose_lab_row(pilot, view, "lab-specializations-list", muto)
        await pilot.press("space")
        await pilot.pause()
        assert saga_dropped() == ["Muto"]  # refused: Techniques 2/2
        info = view.query_one("#lab-attr-panel", Static)
        assert "Muto +1: turned off" in strip_markup(str(info.render()))

        await _choose_lab_row(pilot, view, "lab-specializations-list", rego)
        await pilot.press("space")
        await wait_until(pilot, lambda: saga_dropped() == ["Muto", "Rego"])
        # The row stays chosen, and its panel follows.
        assert grid.selected_data_index == rego
        assert "Rego +2: turned off" in strip_markup(str(info.render()))

        await _choose_lab_row(pilot, view, "lab-specializations-list", muto)
        await pilot.press("space")
        await wait_until(pilot, lambda: saga_dropped() == ["Rego"])


def saga_dropped() -> list[str]:
    return storage.load_saga("test_saga").laboratories[0].dropped_specializations


async def test_a_source_that_breaks_a_cap_arrives_turned_off():
    storage.save_saga(_saga_with_specializations(("Spells", 1), ("Items", 1)))

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view
        await _open_lab_section(pilot, app, "section-lab-specialties")
        await pilot.press("a")
        await pilot.pause()
        app.screen.query_one("#fld-specialization", Select).value = "Texts"
        await pilot.click("#btn-save")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))

        assert saga_dropped() == ["Texts"]
        grid = view.query_one("#lab-specializations-list", SelectableList)
        texts_row = next(label for _, label in grid._rows if label and "Texts" in label)
        assert texts_row.startswith("[dim strike]")


async def _wait_for_field(pilot, app, field_id: str) -> None:
    """Wait until the screen on show has the widget `#field_id` (a form
    opened by another form's save mounts a moment later)."""
    assert await wait_until(pilot, lambda: bool(app.screen.query(f"#{field_id}")))
    await pilot.pause()


async def _save_form(pilot, app, **values) -> None:
    """Fill the open form's fields by id (fld-<key>) and press its save
    button, then wait for the next screen."""
    await _wait_for_field(pilot, app, "btn-save")
    for key in values:
        await _wait_for_field(pilot, app, f"fld-{key}")
    dialog = app.screen
    for key, value in values.items():
        dialog.query_one(f"#fld-{key}").value = value
    await pilot.pause()
    dialog.query_one("#btn-save", Button).press()
    await wait_until(pilot, lambda: app.screen is not dialog)


async def test_add_a_feature_with_a_new_feature_virtue_then_remove_it():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        await build_all_tabs(pilot, app.screen._current_sheet_view())
        view = app.screen._laboratory_sheet_view
        await _open_lab_section(pilot, app, "section-lab-features")

        await pilot.press("a")
        await _wait_for_field(pilot, app, "fld-virtue")
        # No free Feature Virtue: the choice is to add one.
        assert app.screen.query_one("#fld-virtue", Select).value == (
            "new:labvf_lesser_feature"
        )
        await _save_form(pilot, app, feature_type="labfeat_altar")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        assert "Free Virtues 0 → -1" in str(
            app.screen.query_one("#confirm-message", Static).render()
        )
        await pilot.press("y")
        await _wait_for_field(pilot, app, "fld-point0")
        assert not app.screen.query("#fld-focus")  # no Focus Flaw
        await _save_form(pilot, app, point0="Vim")

        assert await wait_until(
            pilot,
            lambda: _lab_rows(view, "lab-features-list") == ["Altar  (Altar, Lesser)"],
        )
        assert _lab_rows(view, "lab-specializations-list") == [
            "Activity (0 of 2)",
            "Art (1 of 4)",
            "Vim  +1",
        ]
        assert _lab_rows(view, "lab-vf-virtues-list") == ["Lesser Feature (Minor)"]

        await _choose_lab_row(pilot, view, "lab-features-list", 0)
        await pilot.press("d")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        assert "Lesser Feature Virtue stays" in str(
            app.screen.query_one("#confirm-message", Static).render()
        )
        await _confirm(pilot, app, "y")
        assert _lab_rows(view, "lab-specializations-list") == [
            "Activity (0 of 2)",
            "Art (0 of 4)",
        ]

    lab = storage.load_saga("test_saga").laboratories[0]
    assert lab.features == []
    assert [vf.vf_id for vf in lab.virtues_flaws] == ["labvf_lesser_feature"]


async def test_cancelling_the_second_step_adds_no_feature_virtue():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        await _open_lab_section(pilot, app, "section-lab-features")
        await pilot.press("a")
        await wait_until(pilot, lambda: _is_form(app.screen, "Add a Feature"))
        await _save_form(pilot, app, feature_type="custom")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        await _wait_for_field(pilot, app, "fld-point0")
        await pilot.press("escape")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))

    lab = storage.load_saga("test_saga").laboratories[0]
    assert (lab.features, lab.virtues_flaws) == ([], [])


def _saga_with_focus() -> Saga:
    """A Greater Feature (a Cauldron, the lab's Focus) and a Lesser one."""
    saga = _saga_with_bare_laboratory()
    lab = saga.laboratories[0]
    lab.virtues_flaws = [
        VirtueFlawInstance("labvf_greater_feature", id="g"),
        VirtueFlawInstance("labvf_greater_focus", id="f"),
        VirtueFlawInstance("labvf_lesser_feature", id="l"),
    ]
    lab.features = [
        LabFeature(
            "c",
            "Cauldron",
            "labfeat_cauldron",
            "g",
            [LabSpecialtyGrant("Ignem", 3)],
            focus=True,
            focus_allocations=[LabSpecialtyGrant("Aquam", 4)],
        )
    ]
    return saga


async def test_edit_a_feature_moves_it_to_another_virtue_and_type():
    storage.save_saga(_saga_with_focus())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view
        await _open_lab_section(pilot, app, "section-lab-features")
        await _choose_lab_row(pilot, view, "lab-features-list", 0)
        await pilot.press("e")
        await _wait_for_field(pilot, app, "fld-virtue")
        virtue = app.screen.query_one("#fld-virtue", Select)
        assert virtue.value == "g"
        # Onto the Lesser Feature, as a Forge: the Greater Focus can't follow.
        await _save_form(pilot, app, feature_type="labfeat_forge", virtue="l")
        await _wait_for_field(pilot, app, "fld-point0")
        assert not app.screen.query("#fld-focus")
        # Ignem is offered by a Forge too, so the first point is kept.
        assert await wait_until(
            pilot, lambda: app.screen.query_one("#fld-point0", Select).value == "Ignem"
        )
        await _save_form(pilot, app, name="Forge")
        assert await wait_until(
            pilot,
            lambda: _lab_rows(view, "lab-features-list") == ["Forge  (Forge, Lesser)"],
        )

    feature = storage.load_saga("test_saga").laboratories[0].features[0]
    assert (feature.feature_id, feature.virtue_id, feature.focus) == (
        "labfeat_forge",
        "l",
        False,
    )
    assert feature.allocations == [LabSpecialtyGrant("Ignem", 1)]
    assert feature.focus_allocations == []


async def test_deleting_a_feature_virtue_or_focus_flaw_takes_its_feature_or_focus():
    storage.save_saga(_saga_with_focus())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        await build_all_tabs(pilot, app.screen._current_sheet_view())
        view = app.screen._laboratory_sheet_view
        await _open_lab_section(pilot, app, "section-lab-vf-flaws")

        # The Focus Flaw: the Cauldron stays, without its Focus points.
        await _choose_lab_row(pilot, view, "lab-vf-flaws-list", 1)
        await pilot.press("d")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        assert "Cauldron stops being the Focus" in str(
            app.screen.query_one("#confirm-message", Static).render()
        )
        await _confirm(pilot, app, "y")
        lab = storage.load_saga("test_saga").laboratories[0]
        assert lab.features[0].focus is False
        assert lab.features[0].focus_allocations == []
        assert "Aquam" not in " ".join(_lab_rows(view, "lab-specializations-list"))

        # The Greater Feature: the Cauldron goes with it.
        await _choose_lab_row(pilot, view, "lab-vf-virtues-list", 0)
        await pilot.press("d")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        assert "Its Feature, Cauldron, goes too" in str(
            app.screen.query_one("#confirm-message", Static).render()
        )
        await _confirm(pilot, app, "y")
        assert _lab_rows(view, "lab-features-list") == []

    lab = storage.load_saga("test_saga").laboratories[0]
    assert [vf.id for vf in lab.virtues_flaws] == ["l"]
    assert lab.features == []


async def test_a_new_feature_virtue_is_given_to_a_feature_waiting_for_one():
    saga = _saga_with_bare_laboratory()
    saga.laboratories[0].features = [LabFeature("x", "Old cauldron")]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        await build_all_tabs(pilot, app.screen._current_sheet_view())
        view = app.screen._laboratory_sheet_view
        await _open_lab_section(pilot, app, "section-lab-vf-virtues")
        await pilot.press("a")
        await wait_until(
            pilot, lambda: isinstance(app.screen, LabVirtueFlawPickerScreen)
        )
        app.screen.dismiss(VirtueFlawInstance("labvf_greater_feature"))
        assert await wait_until(
            pilot,
            lambda: (
                _lab_rows(view, "lab-features-list")
                == ["Old cauldron  (Custom, Greater)  ☞ 3 points to allocate"]
            ),
        )

    lab = storage.load_saga("test_saga").laboratories[0]
    assert lab.features[0].virtue_id == lab.virtues_flaws[0].id != ""


async def test_add_and_remove_lab_raw_vis():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        await _open_lab_section(pilot, app, "section-lab-raw-vis")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)

        app.screen.query_one("#fld-art", Select).value = "ignem"
        app.screen.query_one("#fld-pawns", Input).value = "4"
        await pilot.click("#btn-save", offset=(8, 1))
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        view = app.screen._laboratory_sheet_view
        assert _lab_rows(view, "lab-raw-vis-list") == ["Ignem: 4 pawn(s)"]

        await pilot.press("d")  # nothing chosen: pick which one
        await pilot.pause()
        await _confirm(pilot, app, "y")

    saga = storage.load_saga("test_saga")
    assert saga.laboratories[0].raw_vis == {}


async def test_add_and_remove_inventory_item_on_lab():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        await _open_lab_section(pilot, app, "section-lab-items")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)

        app.screen.query_one("#fld-name", Input).value = "Silver Mirror"
        app.screen.query_one("#fld-description", TextArea).text = "For scrying"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        view = app.screen._laboratory_sheet_view
        assert _lab_rows(view, "lab-items-list") == ["Silver Mirror"]
        section = view.query_one("#section-lab-items", Collapsible)
        assert section.title == "Equipment & Stores (1)"

        await pilot.press("d")
        await pilot.pause()
        await _confirm(pilot, app, "y")

    saga = storage.load_saga("test_saga")
    assert saga.laboratories[0].inventory_items == []


async def _pick_first_and_open_editor(pilot, app, section_id: str, editor_type) -> None:
    """Open `section_id`, press 'e', choose the first entry in the picker,
    and check the pre-filled editor dialog appeared."""
    await _open_lab_section(pilot, app, section_id)
    await pilot.press("e")
    await pilot.pause()
    assert isinstance(app.screen, editor_type)


async def test_edit_specialization_source_and_feature():
    storage.save_saga(_saga_with_populated_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view

        await _pick_first_and_open_editor(
            pilot, app, "section-lab-specialties", FieldsDialog
        )
        specialization = app.screen.query_one("#fld-specialization", Select)
        assert specialization.value == "Ignem"
        specialization.value = "Vim"
        app.screen.query_one("#fld-points", Input).value = "2"
        app.screen.query_one("#btn-save", Button).press()
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        assert _lab_rows(view, "lab-specialties-list") == ["Vim  +2  Hearth spirit"]

        # With no Feature chosen, 'e' asks which one.
        await _pick_first_and_open_editor(
            pilot, app, "section-lab-features", FieldsDialog
        )
        await _save_form(pilot, app)
        await _wait_for_field(pilot, app, "fld-name")
        name = app.screen.query_one("#fld-name", Input)
        assert name.value == "Arcane Library"
        await _save_form(pilot, app, name="Aegis")
        assert await wait_until(
            pilot,
            lambda: _lab_rows(view, "lab-features-list") == ["Aegis  (Custom, Lesser)"],
        )

    lab = storage.load_saga("test_saga").laboratories[0]
    assert lab.specialties == [LabSpecialtyEntry("Vim", 2, "Hearth spirit")]
    assert [f.name for f in lab.features] == ["Aegis"]
    assert lab.features[0].allocations == [LabSpecialtyGrant("Texts", 1)]


async def test_attributes_and_inventory_share_one_panel_docked_below_the_lists():
    saga = _saga_with_populated_laboratory()
    saga.books.append(
        Book(
            id="b1",
            name="Notes",
            type="Other",
            owner_kind="laboratory",
            owner_id="lab1",
        )
    )
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view
        await _open_lab_section(pilot, app, "section-lab-rooms")
        panel = view.query_one("#lab-attr-panel", Static)
        # Outside the scrolling lists, below them.
        scroll = view.query_one("#lab-attr-scroll")
        assert panel.parent is not scroll and panel not in scroll.query(Static)
        assert panel.region.y >= scroll.region.bottom

        def shown(widget) -> str:
            return strip_markup(str(widget.render()))

        await _choose_lab_row(pilot, view, "lab-rooms-list", 0)
        assert shown(panel).startswith("Vault")
        # One choice across the tab's lists.
        await _choose_lab_row(pilot, view, "lab-features-list", 0)
        assert shown(panel).startswith("Arcane Library")
        assert view.selected_room() is None
        await _choose_lab_row(pilot, view, "lab-specialties-list", 0)
        assert shown(panel).startswith("Ignem +1")
        assert view.selected_feature() is None
        # A change elsewhere keeps the chosen row's panel.
        app.screen._commit("section-lab-rooms")
        await pilot.pause()
        assert shown(panel).startswith("Ignem +1")

        await _open_lab_section(pilot, app, "section-lab-items")
        panel = view.query_one("#lab-inv-panel", Static)
        assert not view.query(".books-panel")
        await _choose_lab_row(pilot, view, "section-lab-books-list", 0)
        assert await wait_until(pilot, lambda: "Type:" in shown(panel))
        assert "Notes" in shown(panel)
        await _choose_lab_row(pilot, view, "lab-items-list", 0)
        assert shown(panel).startswith("Silver Mirror")
        await _choose_lab_row(pilot, view, "lab-raw-vis-list", 0)
        assert shown(panel) == "Aquam vis\n2 pawns"


async def test_edit_lab_raw_vis_changes_pawns_and_merges_on_art_change():
    storage.save_saga(_saga_with_populated_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)

        # First picker entry is "aquam" (entries are sorted by Art).
        await _pick_first_and_open_editor(
            pilot, app, "section-lab-raw-vis", FieldsDialog
        )
        assert app.screen.query_one("#fld-art", Select).value == "aquam"
        assert app.screen.query_one("#fld-pawns", Input).value == "2"
        app.screen.query_one("#fld-pawns", Input).value = "7"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

        # Re-point the same entry at an Art that's already held: it merges.
        await _pick_first_and_open_editor(
            pilot, app, "section-lab-raw-vis", FieldsDialog
        )
        app.screen.query_one("#fld-art", Select).value = "ignem"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

    lab = storage.load_saga("test_saga").laboratories[0]
    assert lab.raw_vis == {"ignem": 11}


async def test_the_diary_edit_and_delete_show_brackets_in_an_entry_name():
    # The remove picker escaped entry names; the edit picker didn't.
    saga = _saga_with_populated_laboratory()
    saga.laboratories[0].diary[0].name = "Studied [Ignem] notes"
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        await _open_lab_section(pilot, app, "tab-lab-diary")
        await pilot.press("e")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        assert app.screen.query_one("#fld-name", Input).value == "Studied [Ignem] notes"
        await pilot.press("escape")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        await pilot.press("d")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert "Studied [Ignem] notes" in message, message
        await pilot.press("escape")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))


async def test_editing_an_empty_lab_list_or_cancelling_changes_nothing():
    storage.save_saga(_saga_with_populated_laboratory())
    bare = _saga_with_bare_laboratory()

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)

        # Cancelling the editor does too.
        await _pick_first_and_open_editor(
            pilot, app, "section-lab-specialties", FieldsDialog
        )
        app.screen.query_one("#fld-source", Input).value = "Changed"
        await pilot.press("escape", "y")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    assert storage.load_saga("test_saga").laboratories[0].specialties == [
        LabSpecialtyEntry("Ignem", 1, "Hearth spirit")
    ]

    # Nothing to edit: a notification, not a dialog.
    storage.save_saga(bare)
    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        await _open_lab_section(pilot, app, "section-lab-specialties")
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)


async def test_lab_identity_shows_aura_breakdown_and_modifier_is_editable():
    saga = _saga_with_bare_laboratory()
    saga.covenants[0].aura = 3
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view
        assert "Aura: 3 (covenant) +0 (modifier) = 3" in _lab_identity_text(view)

        for modifier, expected in (
            ("2", "+2 (modifier) = 5"),
            ("-1", "-1 (modifier) = 2"),
        ):
            await _open_lab_section(pilot, app, "section-lab-identity")
            await pilot.press("e")
            await pilot.pause()
            assert _is_form(app.screen, "Edit Laboratory Identity")
            app.screen.query_one("#fld-aura_modifier", Input).value = modifier
            app.screen.query_one("#btn-save", Button).press()
            await pilot.pause()
            assert expected in _lab_identity_text(view)

    assert storage.load_saga("test_saga").laboratories[0].aura_modifier == -1


async def test_lab_characteristics_numbers_take_theme_colours_by_sign():
    saga = _saga_with_bare_laboratory()
    saga.laboratories[0].characteristics = LabCharacteristics(
        size=1, refinement=2, safety=-3
    )
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view

        table = _lab_characteristics_text(view)
        assert re.search(r"Size:\s+\[\$text-success\]\+1\[/\]", table)  # positive
        assert re.search(r"Safety:\s+\[\$text-error\]-3\[/\]", table)  # negative
        assert re.search(
            r"Upkeep:\s+\+0 \+0 = \+0$", table, re.MULTILINE
        )  # zero: plain

        derived = view._characteristics_derived_text()
        assert "Occupied Size: [$text-error]-2[/]" in derived
        assert re.search(r"Free Virtues:\s+\[\$text-success\]3\[/\]", derived)
        assert re.search(r"Base Safety:\s+\[\$text-success\]2\[/\]", derived)
