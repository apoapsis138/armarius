"""The character sheet: Arts, spells, Mastery, inventory, biography, fatigue and vis."""

import re

from screen_helpers import (
    _ability_labels,
    _fill,
    _find_node,
    _is_form,
    _known_spell_labels,
    _lab_identity_text,
    _open_section,
    _saga_with_bare_character,
    _saga_with_bare_laboratory,
    _saga_with_empty_covenant,
    _sample_saga_with_covenant,
    _save_dialog,
    _select,
    _select_character,
    _select_covenant,
    _select_laboratory,
    _wait_for_picker_ready,
    _wait_for_screen,
)
from support import (
    build_all_tabs,
    close_worksheet,
    menu,
    screen_lines,
    strip_markup,
    wait_until,
)
from textual.widgets import (
    Button,
    Collapsible,
    Input,
    Label,
    Select,
    Static,
    TabbedContent,
    TextArea,
    Tree,
)

from ars_magica_manager import storage
from ars_magica_manager.models import (
    ArtScore,
    Character,
    Covenant,
    KnownSpell,
    Laboratory,
    MasteryAbility,
    Saga,
    Spell,
    VirtueFlawInstance,
)
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import (
    ConfirmScreen,
    DialogField,
    EditArtsScreen,
    FieldsDialog,
    RemovalPickerScreen,
    SelectableList,
    SpellChooserScreen,
    WorkspaceScreen,
)
from ars_magica_manager.tui.screens.prompts import ListFieldScreen
from ars_magica_manager.tui.screens.widgets import LIST_COLUMN_GAP, TEXT_COLUMN_GAP


async def test_edit_arts_prefills_existing_scores_and_saves_full_grid():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-arts")

        await pilot.press("e")
        await _wait_for_screen(pilot, app, EditArtsScreen)
        assert isinstance(app.screen, EditArtsScreen)

        assert app.screen.query_one("#input-art-creo-xp", Input).value == "55"
        assert app.screen.query_one("#input-art-ignem-xp", Input).value == "15"
        assert app.screen.query_one("#input-art-rego-xp", Input).value == "0"
        assert "10       66 xp" in str(
            app.screen.query_one("#art-score-creo", Label).render()
        )

        app.screen.query_one("#input-art-rego-xp", Input).value = "6"
        await pilot.pause()
        # The score beside the XP follows as it's typed.
        assert "3        10 xp" in str(
            app.screen.query_one("#art-score-rego", Label).render()
        )

        await pilot.click("#btn-save")
        await _wait_for_screen(pilot, app, WorkspaceScreen)

        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    arts = saga.characters[0].arts
    assert arts["creo"] == ArtScore(xp=55)
    assert arts["ignem"] == ArtScore(xp=15)
    assert arts["rego"] == ArtScore(xp=6)
    # Every one of the 15 Arts is written, not just the ones that were nonzero.
    assert len(arts) == 15
    assert arts["vim"] == ArtScore(xp=0)


async def test_hermetic_magic_arts_and_spells_share_one_details_panel():
    """Magical Arts' two columns and Known Spells are three separate
    SelectableLists that share a single details panel docked at the
    bottom of the Hermetic Magic tab -- choosing a row in any one of them
    must clear the other two's selection (see
    CharacterSheetView.on_selectable_list_chosen())."""
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        view = app.screen._character_sheet_view
        await _open_section(pilot, app, "section-arts")

        techniques = view.query_one("#arts-techniques-list", SelectableList)
        forms = view.query_one("#arts-forms-list", SelectableList)
        spells = view.query_one("#known-spells-list", SelectableList)
        info = view.query_one("#hermetic-info", Static)

        techniques.highlighted = 0  # Creo
        await pilot.pause()
        assert "Creo (Cr)" in str(info.render())
        assert forms.selected_data_index is None
        assert spells.selected_data_index is None

        forms.highlighted = 5  # Ignem
        await pilot.pause()
        assert "Ignem (Ig)" in str(info.render())
        assert techniques.selected_data_index is None
        assert spells.selected_data_index is None

        spells.highlighted = 0  # Ball of Abysmal Flame
        await pilot.pause()
        assert "Ball of Abysmal Flame" in str(info.render())
        assert techniques.selected_data_index is None
        assert forms.selected_data_index is None


async def test_clicking_an_art_row_keeps_focus_on_the_list():
    # A click inside the pinned Magical Arts section focused its title,
    # taking focus off the list just clicked, so the arrow keys stopped
    # moving through the Arts.
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_character(pilot, app)
        view = app.screen._character_sheet_view
        await _open_section(pilot, app, "section-arts")
        techniques = view.query_one("#arts-techniques-list", SelectableList)

        await pilot.click(techniques, offset=(2, 1))  # the second row: Intellego
        await wait_until(pilot, lambda: techniques.highlighted == 1)
        await pilot.pause()
        assert app.focused is techniques
        assert app.screen._active_section() == "section-arts"
        await pilot.press("down")
        assert await wait_until(pilot, lambda: techniques.highlighted == 2)


async def test_magical_arts_collapses_like_the_other_sections():
    # Magical Arts starts open and can be collapsed; 'e' still
    # edits the Arts, and the tab's other sections keep working.
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_character(pilot, app)
        view = app.screen._character_sheet_view
        await _open_section(pilot, app, "section-arts")
        arts = view.query_one("#section-arts", Collapsible)
        assert not arts.collapsed
        await pilot.press("enter")  # Enter doesn't collapse a section...
        await pilot.pause()
        assert not arts.collapsed
        await pilot.press("c")  # ...c does
        assert await wait_until(pilot, lambda: arts.collapsed)
        assert app.screen._active_section() == "section-arts"
        await pilot.press("e")
        assert await wait_until(pilot, lambda: isinstance(app.screen, EditArtsScreen))
        await pilot.press("escape")
        await pilot.pause()
        await _open_section(pilot, app, "section-known-spells")
        assert app.screen._active_section() == "section-known-spells"
        assert arts.collapsed


async def test_edit_arts_grid_fits_default_terminal_and_accepts_real_typing():
    # The smallest terminal the app is checked at (120x45) -- this test drives
    # actual clicks and keystrokes (not direct .value assignment) so a
    # layout tall/wide enough to push rows off-screen, or to block real
    # keyboard input, actually fails here.
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-arts")
        await pilot.press("e")
        await _wait_for_screen(pilot, app, EditArtsScreen)
        assert isinstance(app.screen, EditArtsScreen)

        screen_width = app.screen.size.width
        # One Technique row and two Form rows, from opposite ends of the
        # single-column (scrollable) list -- Herbam and Vim aren't visible
        # without scrolling, exercising that the scroll-then-click path
        # itself works, not just whatever's on-screen by default.
        for field_id in (
            "#input-art-rego-xp",
            "#input-art-herbam-xp",
            "#input-art-vim-xp",
        ):
            field = app.screen.query_one(field_id, Input)
            field.scroll_visible(animate=False)
            await pilot.pause()
            assert field.region.x + field.region.width <= screen_width, (
                f"{field_id} is rendered outside the {screen_width}-wide screen"
            )

            await pilot.click(field_id)
            await pilot.pause()
            # Clear whatever's there regardless of where the click landed the
            # cursor, then type -- this is exercising real keystrokes, not
            # asserting exact cursor/selection placement from the click.
            await pilot.press("end", "backspace", "backspace", "backspace")
            await pilot.press("2", "8")
            await pilot.pause()
            assert field.value == "28"

        await pilot.click("#btn-save")
        await pilot.pause()

    saga = storage.load_saga("test_saga")
    arts = saga.characters[0].arts
    assert arts["rego"].level == 7
    assert arts["herbam"].level == 7
    assert arts["vim"].level == 7


async def test_arts_and_spells_tabs_are_absent_for_non_magi():
    saga = _saga_with_empty_covenant()
    saga.characters.append(
        Character(id="grog1", name="Guard", type="grog", covenant_id="cov1")
    )
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)
        await _select(pilot, app, ("character", "grog1"))
        await build_all_tabs(pilot, app.screen._current_sheet_view())
        assert app.screen.selected_character.type == "grog"

        view = app.screen._character_sheet_view
        tabbed = view.query_one(TabbedContent)
        tab_ids = {pane.id for pane in tabbed.query("TabPane")}
        assert "tab-hermetic" not in tab_ids
        assert "tab-lab" not in tab_ids
        # Tabs/sections that do apply to every character type are still present.
        assert "tab-description" in tab_ids
        assert "tab-abilities" in tab_ids
        assert "tab-vf" in tab_ids
        assert "tab-inventory" in tab_ids
        assert "tab-diary" in tab_ids
        section_ids = {c.id for c in view.query(Collapsible)}
        assert "section-inventory" in section_ids
        assert "section-arts" not in section_ids
        assert "section-hermetic-background" not in section_ids
        assert "section-known-spells" not in section_ids
        assert "section-raw-vis-inventory" not in section_ids

        # With no Arts tab to switch to, 'e' on the default view (focus
        # lands on the top panel) opens Edit Character Info rather than
        # doing nothing.
        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Character Info")


async def test_switching_tabs_moves_a_a_e_with_the_tab():
    """Switching tabs must clear a stale Collapsible focus from whatever tab
    was active before (see CLAUDE.md's flat-tab focus-tracking gotcha), so
    'e' never re-dispatches to a section that's no longer visible. Planning
    has a section: switching to it focuses This Season. The
    Diary is a flat tab with its own a / e / d. (The Laboratory tab, the old
    flat tab this covered, moved to the laboratory sheet as Lab Totals.)"""
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        # Focus a real Collapsible section first (Aging, in Description).
        await _open_section(pilot, app, "section-aging")
        assert app.screen._active_section() == "section-aging"

        view = app.screen._character_sheet_view
        view.query_one(TabbedContent).active = "tab-planning"
        await pilot.pause()
        assert app.screen._active_section() == "section-char-season"
        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Plan Leandro's Season (Spring 1220)")
        await pilot.press("escape")
        await pilot.pause()

        view.query_one(TabbedContent).active = "tab-diary"
        await pilot.pause()
        assert app.screen._active_section() == "tab-diary"


async def test_creating_a_second_character_after_viewing_the_first_works():
    storage.save_saga(_saga_with_empty_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)

        # Create the first character.
        await menu(pilot, app, "n", "New Character")
        await pilot.pause()
        app.screen.query_one("#fld-name", Input).value = "Leandro"
        await pilot.click("#btn-save")
        await pilot.pause()
        await close_worksheet(pilot, app)
        assert app.screen.selected_character.name == "Leandro"

        # View it explicitly, then go back to the covenant before adding a
        # second one -- the reported repro was a crash on this exact sequence.
        await _select(pilot, app, ("character", "leandro"))
        await _select(pilot, app, ("covenant", "cov1"))

        await menu(pilot, app, "n", "New Character")
        await pilot.pause()
        app.screen.query_one("#fld-name", Input).value = "Guillame"
        await pilot.click("#btn-save")
        await pilot.pause()
        await close_worksheet(pilot, app)

        tree = app.screen.query_one("#nav-tree", Tree)
        char_group = _find_node(tree, ("character_group", "cov1"))
        assert len(char_group.children) == 2

    saga = storage.load_saga("test_saga")
    assert {c.name for c in saga.characters} == {"Leandro", "Guillame"}


def _saga_with_two_labs() -> Saga:
    return Saga(
        id="test_saga",
        name="Test Saga",
        storyguide="Alex",
        covenants=[
            Covenant(id="cov1", saga_id="test_saga", name="Test Covenant"),
            Covenant(id="cov2", saga_id="test_saga", name="Other Covenant"),
        ],
        characters=[
            Character(
                id="char1",
                name="Leandro",
                type="magus",
                covenant_id="cov1",
                assigned_lab_id="lab1",
            )
        ],
        laboratories=[
            Laboratory(id="lab1", covenant_id="cov1", name="Lab One", owner_id="char1"),
            Laboratory(id="lab2", covenant_id="cov1", name="Lab Two"),
        ],
    )


async def test_a_renamed_characters_title_is_not_read_as_markup():
    # The title was escaped when composed but not when refreshed, so
    # "[the]" vanished (and "[/]" could raise).
    storage.save_saga(_saga_with_two_labs())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await pilot.press("e")
        await wait_until(pilot, lambda: _is_form(app.screen, "Edit Character Info"))
        app.screen.query_one("#fld-name", Input).value = "Tim [the] Bold [/]"
        await pilot.click("#btn-save")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        await pilot.pause()
        title = app.screen._character_sheet_view.query_one(
            "#section-char-info CollapsibleTitle"
        )
        assert "Tim [the] Bold [/]" in str(title.render())


async def test_edit_character_info_updates_name_covenant_and_laboratory():
    storage.save_saga(_saga_with_two_labs())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)  # defaults to the top panel

        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Character Info")

        app.screen.query_one("#fld-name", Input).value = "Leandro the Elder"
        app.screen.query_one("#fld-covenant_id", Select).value = "cov2"
        app.screen.query_one("#fld-laboratory_id", Select).value = "lab2"
        app.screen.query_one("#fld-confidence_score", Input).value = "2"
        app.screen.query_one("#fld-confidence_points", Input).value = "5"

        await pilot.click("#btn-save")
        await _wait_for_screen(pilot, app, WorkspaceScreen)

        assert isinstance(app.screen, WorkspaceScreen)
        view = app.screen._character_sheet_view
        assert view.query_one("#section-char-info", Collapsible).title == (
            "Leandro the Elder"
        )
        info_lines = strip_markup(view._info_right_text()).splitlines()
        assert any(
            line.startswith("Confidence Score:") and line.endswith("2")
            for line in info_lines
        )
        assert any(
            line.startswith("Confidence Points:") and line.endswith("5")
            for line in info_lines
        )

    saga = storage.load_saga("test_saga")
    character = saga.characters[0]
    assert character.name == "Leandro the Elder"
    assert character.covenant_id == "cov2"
    assert character.assigned_lab_id == "lab2"
    assert character.background.confidence_score == 2
    assert character.background.confidence_points == 5

    lab1 = next(lab for lab in saga.laboratories if lab.id == "lab1")
    lab2 = next(lab for lab in saga.laboratories if lab.id == "lab2")
    assert lab1.owner_id is None
    assert lab2.owner_id == "char1"


async def test_edit_ability_updates_existing_entry():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "tab-abilities")

        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        assert app.screen.query_one("#fld-xp", Input).value == "75"

        app.screen.query_one("#fld-xp", Input).value = "105"

        await pilot.click("#btn-save")
        await _wait_for_screen(pilot, app, WorkspaceScreen)

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Magic Theory (Lab Totals) 6 105/140" in _ability_labels(
            app.screen._character_sheet_view
        )

    saga = storage.load_saga("test_saga")
    ability = saga.characters[0].abilities[0]
    assert ability.level == 6
    assert ability.xp == 105
    assert ability.category == "Academic"


def _saga_with_character_and_spell() -> Saga:
    saga = _saga_with_bare_character()
    saga.spells.append(
        Spell(
            id="spell1", name="Pilum of Fire", technique="Creo", form="Ignem", level=20
        )
    )
    return saga


async def test_virtue_and_flaw_titles_show_the_points_and_whether_they_balance():
    # Each side's points, both in the success colour when they
    # match and the error colour when they don't; Free Virtues count 0.
    saga = _saga_with_bare_character()
    character = saga.characters[0]
    character.virtues_flaws = [
        VirtueFlawInstance("vf_adept_laboratory_student"),  # Minor Virtue, 1
        VirtueFlawInstance("vf_abandoned_apprentice"),  # Major Flaw, 3
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _select_character(pilot, app)
        await build_all_tabs(pilot, app.screen._current_sheet_view())
        view = app.screen._character_sheet_view
        virtues = view.query_one("#section-vf-virtues", Collapsible)
        flaws = view.query_one("#section-vf-flaws", Collapsible)
        assert virtues.title == "Virtues [$text-error](1 pt)[/]"
        assert flaws.title == "Flaws [$text-error](3 pts)[/]"

        # The app's own copy of the character (loaded from the save).
        view.character.virtues_flaws.append(VirtueFlawInstance("vf_alim"))
        view.character.virtues_flaws.append(VirtueFlawInstance("vf_almogaten"))
        app.screen._commit("section-vf-virtues")
        await pilot.pause()
        assert virtues.title == "Virtues [$text-success](3 pts)[/]"
        assert flaws.title == "Flaws [$text-success](3 pts)[/]"


async def test_side_by_side_lists_and_text_blocks_have_one_gap_each():
    # Lists sit LIST_COLUMN_GAP apart and blocks of text
    # TEXT_COLUMN_GAP apart, on every sheet; the last column has none.
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _select_character(pilot, app)
        await build_all_tabs(pilot, app.screen._current_sheet_view())
        view = app.screen._character_sheet_view
        for row_id, gap in (
            ("pt-rep-row", LIST_COLUMN_GAP),
            ("vf-row", LIST_COLUMN_GAP),
            ("char-info-body", TEXT_COLUMN_GAP),
            ("char-biographical-row", TEXT_COLUMN_GAP),
        ):
            first, last = view.query_one(f"#{row_id}").children
            assert first.styles.margin.right == gap, row_id
            assert last.styles.margin.right == 0, row_id


async def test_add_and_remove_spell_known():
    storage.save_saga(_saga_with_character_and_spell())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-known-spells")

        await pilot.press("a")
        await wait_until(pilot, lambda: isinstance(app.screen, SpellChooserScreen))
        await pilot.pause()
        # The saga's own spell and the catalog's are both offered.
        assert "spellpick-spell1" in app.screen._by_item_id
        assert "spellpick-spell_pilum_of_fire" in app.screen._by_item_id
        # Search, then pick the second match (the saga's own; the catalog's
        # Pilum of Fire comes first).
        await _wait_for_picker_ready(pilot, app)
        app.screen.query_one("#picker-search", Input).value = "pilum"
        await pilot.pause()
        await pilot.pause()
        app.screen.query_one("#picker-search", Input).focus()
        await pilot.press("down", "down", "enter")
        await _wait_for_screen(pilot, app, WorkspaceScreen)

        assert isinstance(app.screen, WorkspaceScreen)
        labels = _known_spell_labels(app.screen._character_sheet_view)
        assert "Pilum of Fire" in labels and "CrIg" in labels
        # A spell already known isn't offered again.
        await pilot.press("a")
        await wait_until(pilot, lambda: isinstance(app.screen, SpellChooserScreen))
        await pilot.pause()
        assert "spellpick-spell1" not in app.screen._by_item_id
        await pilot.press("escape")
        await pilot.pause()

        await pilot.press("d")
        await _wait_for_screen(pilot, app, ConfirmScreen)
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await _wait_for_screen(pilot, app, WorkspaceScreen)

        assert isinstance(app.screen, WorkspaceScreen)
        assert app.screen._character_sheet_view._known_spell_rows() == []

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].spells_known == []


async def test_the_known_spell_delete_prompt_shows_brackets_once():
    # The prompt escaped a label that was already escaped, so "[" in a
    # spell name showed as "\[".
    saga = _saga_with_character_and_spell()
    saga.spells[0].name = "Pilum of [Greater] Fire"
    saga.characters[0].spells_known = [KnownSpell(spell_id="spell1")]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-known-spells")
        await pilot.press("d")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert message == "Delete Pilum of [Greater] Fire?", message


async def test_edit_spell_mastery_sets_score_xp_and_abilities():
    saga = _saga_with_character_and_spell()
    saga.characters[0].spells_known = [KnownSpell(spell_id="spell1")]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-known-spells")

        await pilot.press("e")
        mastery = await wait_until(
            pilot, lambda: isinstance(app.screen, FieldsDialog) and app.screen
        )
        await pilot.pause()
        assert str(mastery.query_one("#fields-title", Label).render()).startswith(
            "Mastery: "
        )

        mastery.query_one("#fld-mastery_score", Input).value = "2"
        mastery.query_one("#fld-mastery_xp", Input).value = "10"
        mastery.query_one("#fld-mastery_abilities", Button).press()
        editor = await wait_until(
            pilot, lambda: isinstance(app.screen, ListFieldScreen) and app.screen
        )
        await pilot.pause()
        editor.action_add()
        added = await wait_until(
            pilot,
            lambda: (
                isinstance(app.screen, FieldsDialog)
                and app.screen is not mastery
                and app.screen
            ),
        )
        await pilot.pause()
        added.query_one("#fld-name", Input).value = "Fast Casting"
        added.query_one("#fld-level", Input).value = "1"
        added.query_one("#btn-save", Button).press()
        assert await wait_until(pilot, lambda: app.screen is editor)

        # Removing one asks first; No keeps it.
        await pilot.pause()
        editor.action_remove()
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.pause()
        assert "Delete Fast Casting" in str(
            app.screen.query_one("#confirm-message", Static).render()
        )
        await pilot.press("n")
        await wait_until(pilot, lambda: app.screen is editor)
        assert len(editor.items) == 1

        editor.query_one("#btn-done", Button).press()
        assert await wait_until(pilot, lambda: app.screen is mastery)
        await pilot.pause()
        assert str(mastery.query_one("#fld-mastery_abilities", Button).label) == (
            "Fast Casting 1/0"
        )
        mastery.query_one("#btn-save", Button).press()
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))

    saga = storage.load_saga("test_saga")
    known = saga.characters[0].spells_known[0]
    assert known.mastery_score == 2
    assert known.mastery_xp == 10
    assert len(known.mastery_abilities) == 1
    assert known.mastery_abilities[0].name == "Fast Casting"
    assert known.mastery_abilities[0].level == 1


async def test_the_mastery_dialog_shows_brackets_in_names():
    # The spell's name (title) and its Mastery Abilities' names (list)
    # were read as markup.
    saga = _saga_with_character_and_spell()
    saga.spells[0].name = "Pilum of [Greater] Fire"
    saga.characters[0].spells_known = [
        KnownSpell(
            spell_id="spell1",
            mastery_abilities=[MasteryAbility(name="Fast [Casting]", level=1)],
        )
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-known-spells")
        await pilot.press("e")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        await pilot.pause()
        labels = [str(label.render()) for label in app.screen.query(Label)]
        assert "Mastery: Pilum of [Greater] Fire" in labels, labels
        button = app.screen.query_one("#fld-mastery_abilities", Button)
        assert str(button.label) == "Fast [Casting] 1/0"
        button.press()
        assert await wait_until(pilot, lambda: isinstance(app.screen, ListFieldScreen))
        await pilot.pause()
        assert "Mastery Abilities: Pilum of [Greater] Fire" in [
            str(label.render()) for label in app.screen.query(Label)
        ]
        rows = "\n".join(screen_lines(app))
        assert "Fast [Casting] 1/0" in rows, rows


def _inventory_labels(view) -> str:
    """All of a CharacterSheetView's Inventory row labels (headers excluded),
    joined -- Inventory is one selectable list, not one text blob."""
    return " | ".join(
        label for index, label in view._inventory_rows() if index is not None
    )


async def test_add_and_remove_inventory_item():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-inventory")

        await pilot.press("a")
        await _wait_for_screen(pilot, app, RemovalPickerScreen)
        assert isinstance(app.screen, RemovalPickerScreen)  # which kind?
        await pilot.press("down")  # Weapon, Armor, [Item]
        await pilot.press("down")
        await pilot.press("enter")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)

        _fill(app, name="Fine wool cloak")
        await _save_dialog(pilot, app)

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Fine wool cloak" in _inventory_labels(app.screen._character_sheet_view)

        await pilot.press("d")
        await _wait_for_screen(pilot, app, ConfirmScreen)
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await _wait_for_screen(pilot, app, WorkspaceScreen)

        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].inventory == []


async def test_edit_biographical_detail_updates_background_and_description():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-char-biographical")

        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Biographical Detail")

        app.screen.query_one("#fld-player", Input).value = "Alex"
        app.screen.query_one("#fld-year_born", Input).value = "1180"
        app.screen.query_one("#fld-height", Input).value = "1.8"
        app.screen.query_one("#fld-handedness", Select).value = "left"
        app.screen.query_one("#fld-biography", TextArea).text = "Born in Aachen."

        # The dialog has many fields, taller than the default 80x24 test
        # terminal -- pilot.click() needs an on-screen target, so trigger
        # the button directly rather than by pixel coordinate.
        app.screen.query_one("#btn-save", Button).press()
        await _wait_for_screen(pilot, app, WorkspaceScreen)

        assert isinstance(app.screen, WorkspaceScreen)
        view = app.screen._character_sheet_view
        left = view._biographical_left_text()
        assert "Player: Alex" in left
        assert "Height: 1.8" in left
        assert "Handedness: left" in left
        assert view._biographical_right_text() == "Born in Aachen."
        # Age (derived from Year Born) lives in the top panel, refreshed
        # alongside Biographical Detail since they share Year Born.
        assert re.search(r"Age:\s+40\b", strip_markup(view._info_left_text()))

    saga = storage.load_saga("test_saga")
    character = saga.characters[0]
    assert character.background.player == "Alex"
    assert character.background.year_born == 1180
    assert character.description.height == 1.8
    assert character.description.handedness == "left"
    assert character.description.biography == "Born in Aachen."


async def test_edit_fatigue_updates_level():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-char-health")

        # Fatigue is the merged Health section's second column -- reached
        # via its own Edit button, not the 'e' keybinding (which defaults
        # to Wounds, column 1).
        view = app.screen._character_sheet_view
        view.query_one("#btn-char-health-fatigue-edit", Button).press()
        assert await wait_until(
            pilot, lambda: _is_form(app.screen, "Edit Fatigue Level")
        )
        await pilot.pause()

        app.screen.query_one("#fld-level", Select).value = "tired"
        await pilot.click("#btn-save", offset=(8, 1))
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        assert (
            "Fatigue Level: Tired" in app.screen._character_sheet_view._fatigue_text()
        )

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].fatigue_level == "tired"


async def test_add_and_remove_raw_vis():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-raw-vis-hermetic")

        await pilot.press("a")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)

        app.screen.query_one("#fld-art", Select).value = "creo"
        app.screen.query_one("#fld-pawns", Input).value = "5"
        await pilot.click("#btn-save", offset=(8, 1))
        await _wait_for_screen(pilot, app, WorkspaceScreen)

        assert isinstance(app.screen, WorkspaceScreen)
        rows = app.screen._character_sheet_view._raw_vis_rows()
        assert "Creo: 5 pawn(s)" in rows[0][1]

        # Adding the same Art again accumulates rather than overwriting.
        await pilot.press("a")
        await _wait_for_screen(pilot, app, FieldsDialog)
        app.screen.query_one("#fld-art", Select).value = "creo"
        app.screen.query_one("#fld-pawns", Input).value = "3"
        await pilot.click("#btn-save", offset=(8, 1))
        await pilot.pause()
        rows = app.screen._character_sheet_view._raw_vis_rows()
        assert "Creo: 8 pawn(s)" in rows[0][1]

        await pilot.press("d")
        await _wait_for_screen(pilot, app, ConfirmScreen)
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await _wait_for_screen(pilot, app, WorkspaceScreen)
        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].raw_vis == {}


async def test_raw_vis_stays_live_across_both_tabs():
    """Raw Vis deliberately appears twice (Hermetic Magic and Inventory),
    both backed by character.raw_vis -- adding/editing/removing from one
    tab's list must also update the other tab's list, even though it's not
    the active tab when the mutation happens (it is
    "the first section in the app that deliberately appears twice")."""
    storage.save_saga(_saga_with_bare_character())

    def rows(view, list_id: str) -> list[str]:
        widget = view.query_one(f"#{list_id}", SelectableList)
        return [str(o.prompt) for o in widget.options]

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        view = app.screen._character_sheet_view

        # Add from the Hermetic Magic tab.
        await _open_section(pilot, app, "section-raw-vis-hermetic")
        await pilot.press("a")
        await _wait_for_screen(pilot, app, FieldsDialog)
        app.screen.query_one("#fld-art", Select).value = "creo"
        app.screen.query_one("#fld-pawns", Input).value = "5"
        await pilot.click("#btn-save", offset=(8, 1))
        await pilot.pause()

        assert any(
            "Creo: 5 pawn(s)" in row for row in rows(view, "raw-vis-list-hermetic")
        )
        # Switch to Inventory: its list already reflects the addition, even
        # though it wasn't the active tab when the add happened.
        view.query_one(TabbedContent).active = "tab-inventory"
        await pilot.pause()
        assert any(
            "Creo: 5 pawn(s)" in row for row in rows(view, "raw-vis-list-inventory")
        )

        # Edit from the Inventory tab.
        await _open_section(pilot, app, "section-raw-vis-inventory")
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        app.screen.query_one("#fld-pawns", Input).value = "3"
        await pilot.click("#btn-save", offset=(8, 1))
        await pilot.pause()

        assert any(
            "Creo: 3 pawn(s)" in row for row in rows(view, "raw-vis-list-inventory")
        )
        await _open_section(pilot, app, "section-raw-vis-hermetic")
        assert any(
            "Creo: 3 pawn(s)" in row for row in rows(view, "raw-vis-list-hermetic")
        )

        # Remove from the Hermetic Magic tab.
        await pilot.press("d")
        await _wait_for_screen(pilot, app, ConfirmScreen)
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await pilot.pause()

        assert "none recorded" in rows(view, "raw-vis-list-hermetic")[0]
        view.query_one(TabbedContent).active = "tab-inventory"
        await pilot.pause()
        assert "none recorded" in rows(view, "raw-vis-list-inventory")[0]

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].raw_vis == {}


async def test_edit_hermetic_background_sets_house_and_fields():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-hermetic-background")

        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Hermetic Background")

        app.screen.query_one("#fld-house", Select).value = "house_bonisagus"
        app.screen.query_one("#fld-parens", Input).value = "Trianoma"
        app.screen.query_one("#fld-age_of_apprenticeship", Input).value = "12"

        app.screen.query_one("#btn-save", Button).press()
        await _wait_for_screen(pilot, app, WorkspaceScreen)

        assert isinstance(app.screen, WorkspaceScreen)
        view = app.screen._character_sheet_view
        text = view._hermetic_background_left_text()
        assert "House: Bonisagus" in text
        assert "Parens: Trianoma" in text
        assert "Age of Apprenticeship: 12" in text

    saga = storage.load_saga("test_saga")
    hermetic = saga.characters[0].hermetic
    assert hermetic.house == "house_bonisagus"
    assert hermetic.parens == "Trianoma"
    assert hermetic.age_of_apprenticeship == 12


async def test_bracketed_names_survive_the_nav_tree_and_top_panels():
    """A name with [brackets] must not vanish -- Textual/Rich
    markup would otherwise swallow "[Tower]" as an (invalid) tag. Covers the
    nav tree (saga/covenant/character/lab labels) and the Collapsible
    section titles that mirror a character's/covenant's own name."""
    saga = _saga_with_bare_laboratory()
    saga.name = "[Ars] Saga"
    saga.covenants[0].name = "[Tower] Covenant"
    saga.characters[0].name = "[Leandro] the Bracketed"
    saga.laboratories[0].name = "[Vault] Lab"
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_character(pilot, app)
        tree = app.screen.query_one("#nav-tree", Tree)
        assert "[Ars] Saga" in str(tree.root.label)
        assert "[Tower] Covenant" in str(_find_node(tree, ("covenant", "cov1")).label)
        assert "[Leandro] the Bracketed" in str(
            _find_node(tree, ("character", "char1")).label
        )
        assert "[Vault] Lab" in str(_find_node(tree, ("laboratory", "lab1")).label)

        char_title = app.screen._character_sheet_view.query_one(
            "#section-char-info", Collapsible
        ).title
        assert "[Leandro] the Bracketed" in str(char_title)

        await _select_covenant(pilot, app)
        cov_title = app.screen._covenant_sheet_view.query_one(
            "#section-cov-info", Collapsible
        ).title
        assert "[Tower] Covenant" in str(cov_title)

        await _select_laboratory(pilot, app)
        identity = _lab_identity_text(app.screen._laboratory_sheet_view)
        assert "[Vault] Lab" in identity


async def test_fields_dialog_info_field_escapes_bracketed_values():
    """FieldsDialog's read-only "info" row (screens/fields.py's
    `_widgets`, kind == "info") is a single shared render sink used by
    dozens of DialogField call sites (Inhabitant "from the character
    sheet" fields, Possession Owner/Location, Economics calculated rows,
    Loyalty totals, ...). A bracketed value must render literally, not
    vanish as a swallowed markup tag."""
    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        app.push_screen(
            FieldsDialog(
                "Test",
                [DialogField("_n", "Name", "info", "[Leandro] the Bracketed")],
            )
        )
        await pilot.pause()
        value = app.screen.query_one(".fd-value", Static)
        assert "[Leandro] the Bracketed" in str(value.render())
