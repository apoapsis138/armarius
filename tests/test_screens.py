import re
from pathlib import Path

from support import strip_markup, wait_until
from textual.app import App
from textual.widgets import (
    Button,
    Checkbox,
    Collapsible,
    DirectoryTree,
    Input,
    Label,
    ListView,
    OptionList,
    Select,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
    Tree,
)

from ars_magica_manager import catalog, settings, storage
from ars_magica_manager import economics as eco
from ars_magica_manager import familiars as fam
from ars_magica_manager import inhabitants as inh
from ars_magica_manager import possessions as pos
from ars_magica_manager import spells as spl
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.arts import FORMS, TECHNIQUES
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Background,
    Book,
    Character,
    Characteristics,
    Covenant,
    DiaryEntry,
    Familiar,
    HermeticBackground,
    IncomeSource,
    Inhabitant,
    KnownSpell,
    LabCharacteristics,
    Laboratory,
    NamedDescription,
    Possession,
    Saga,
    ScoredTrait,
    Spell,
    VirtueFlawInstance,
)
from ars_magica_manager.screens import (
    AbilityPickerScreen,
    AdvanceSeasonScreen,
    ConfirmScreen,
    CovenantBoonHookPickerScreen,
    CsvFilePickerScreen,
    DialogField,
    DuplicateBookScreen,
    EditArtsScreen,
    EditFamiliarBindingScreen,
    FieldsDialog,
    ImportScreen,
    ImproveIncomeScreen,
    LabVirtueFlawPickerScreen,
    MasteryEditScreen,
    RemovalPickerScreen,
    SagaPickerScreen,
    SelectableList,
    SpellChooserScreen,
    SpellImportHelperScreen,
    SpellListView,
    ThemeBar,
    VirtueFlawPickerScreen,
    WorkspaceScreen,
    _CsvDirectoryTree,
)


def _is_form(screen, title: str) -> bool:
    """`screen` is the FieldsDialog titled `title`."""
    return isinstance(screen, FieldsDialog) and screen.title_text == title


def _find_node(tree, data):
    """Walk a Tree looking for the node whose `.data` matches, by value."""

    def walk(node):
        if node.data == data:
            return node
        for child in node.children:
            found = walk(child)
            if found is not None:
                return found
        return None

    return walk(tree.root)


async def _wait_for_screen(pilot, app, screen_type) -> None:
    """Wait for a pushed screen of `screen_type` to be up and mounted -- a
    bare pause after the key press isn't always enough under load."""
    await wait_until(
        pilot, lambda: isinstance(app.screen, screen_type) and app.screen.is_mounted
    )
    await pilot.pause()


async def _wait_for_picker_ready(pilot, app) -> None:
    """A searchable picker fills its list, then focuses its search box: wait
    for that before typing, or the first fill and the search's refill
    interleave (STORY-1109 B18)."""
    await wait_until(
        pilot,
        lambda: app.focused is not None and app.focused.id == "picker-search",
        timeout=10.0,  # filling 600+ rows one at a time is slow under load
    )


async def _wait_until_active(pilot, app, section_id: str) -> None:
    """Wait for `section_id` to be what a/A/e dispatch to, and fail clearly
    if it never becomes so."""
    await wait_until(pilot, lambda: app.screen._active_section() == section_id)
    assert app.screen._active_section() == section_id, (
        f"{section_id!r} never became the active section "
        f"(got {app.screen._active_section()!r})"
    )


#: Selecting one of these tree-node kinds mounts a heavy sheet view
#: (CharacterSheetView / LaboratorySheetView) asynchronously -- _select()
#: waits for the matching WorkspaceScreen attribute to be set, rather than
#: just the tree's own NodeSelected handling, to avoid the flakiness above.
#: Keyed by kind -> the attribute name on WorkspaceScreen.
_SHEET_VIEW_ATTR: dict[str, str] = {
    "character": "_character_sheet_view",
    "laboratory": "_laboratory_sheet_view",
    "covenant": "_covenant_sheet_view",
    "familiar": "_familiar_sheet_view",
}


async def _select(pilot, app, data) -> None:
    """Select a nav-tree node by its `.data`, the same way a click/enter would."""
    tree = app.screen.query_one("#nav-tree", Tree)
    node = _find_node(tree, data)
    assert node is not None, f"tree node with data={data!r} not found"
    tree.select_node(node)
    await pilot.pause()
    attr = _SHEET_VIEW_ATTR.get(data[0])
    if attr is not None:
        await wait_until(pilot, lambda: getattr(app.screen, attr) is not None)


async def _open_workspace(pilot) -> None:
    await pilot.press("enter")  # picker -> workspace
    await pilot.pause()


async def _select_vf_picker_entry(pilot, app, vf_id: str) -> None:
    """Highlight and activate a VirtueFlawPickerScreen entry by catalog id.

    The catalog now has 600+ entries, so most are well outside the picker
    dialog's visible/scrolled area -- pixel-coordinate pilot.click() raises
    OutOfBounds for anything not currently on screen. Setting ListView.index
    and pressing enter selects it the same way a real click/enter would,
    without needing the item to be visible.
    """
    list_view = app.screen.query_one("#vf-picker-list", ListView)
    target_id = f"vf-{vf_id}"
    for i, item in enumerate(list_view.children):
        if item.id == target_id:
            list_view.index = i
            break
    else:
        raise AssertionError(f"{target_id!r} not found in Virtue/Flaw picker list")
    await pilot.pause()
    await pilot.press("enter")
    await pilot.pause()


def _character_vf_labels(view) -> str:
    """All of a CharacterSheetView's Virtue and Flaw row labels, joined --
    the character V&F section is two selectable lists, not one text blob."""
    rows = view._vf_rows("Virtue") + view._vf_rows("Flaw")
    return " | ".join(label for _, label in rows)


def _ability_labels(view) -> str:
    """All of a CharacterSheetView's Ability row labels (headers excluded),
    joined -- Abilities is one selectable list, not one text blob."""
    return " | ".join(
        label for index, label in view._ability_rows() if index is not None
    )


def _fam_ability_labels(view) -> str:
    """Same idea as _ability_labels(), for a FamiliarSheetView."""
    return " | ".join(
        label for index, label in fam.ability_rows(view.familiar) if index is not None
    )


def _known_spell_labels(view) -> str:
    """All of a CharacterSheetView's known-spell row labels, joined -- the
    Spells tab is a selectable list, not one text blob."""
    return " | ".join(label for _, label in view._known_spell_rows())


#: Which top-level character-sheet tab each Collapsible section lives in.
#: "tab-abilities" maps to itself -- the one tab with no sub-sections, keyed
#: by its own tab id (see WorkspaceScreen._active_section()). The
#: top-panel sections (Info/Characteristics) aren't inside any tab -- see
#: _open_section()'s handling of them, mirroring _open_lab_section().
_SECTION_TAB: dict[str, str] = {
    "section-char-info": "tab-description",  # top panel, not inside any tab
    "section-char-characteristics": "tab-description",
    "section-char-biographical": "tab-description",
    "tab-abilities": "tab-abilities",
    "section-vf-virtues": "tab-vf",
    "section-vf-flaws": "tab-vf",
    "section-personality-traits": "tab-description",
    "section-reputations": "tab-description",
    "section-aging": "tab-description",
    "section-char-health": "tab-description",
    "section-inventory": "tab-inventory",
    "section-raw-vis-inventory": "tab-inventory",
    "section-arts": "tab-hermetic",
    "section-raw-vis-hermetic": "tab-hermetic",
    "section-known-spells": "tab-hermetic",
    "section-hermetic-background": "tab-description",
}


async def _open_section(pilot, app, section_id: str) -> None:
    """Switch to the tab containing `section_id` and focus that section.

    The generic Add/Remove/Edit bindings dispatch by whichever Collapsible
    section currently has focus (its title, since CollapsibleTitle is the
    focusable part -- see WorkspaceScreen._active_section()), so
    most character-mutation tests need this before pressing
    'a'/'A'/'e'/'v'/'V'. `section_id` may also be "tab-abilities", the one
    tab with no sub-sections, or one of the top-panel sections (Info/
    Characteristics), which are focused directly regardless of which tab is
    active.
    """
    view = app.screen._character_sheet_view
    assert view is not None, "no character sheet is currently shown"
    # Let the view's own initial focus land first, or it can arrive after
    # ours and steal it back (see _open_lab_section).
    await wait_until(pilot, lambda: view.initial_tab_seen)
    await pilot.pause()
    if section_id not in ("section-char-info", "section-char-characteristics"):
        tab_id = _SECTION_TAB[section_id]
        view.query_one(TabbedContent).active = tab_id
        await pilot.pause()
    if section_id != _SECTION_TAB[section_id]:
        collapsible = view.query_one(f"#{section_id}", Collapsible)
        collapsible.query_one("CollapsibleTitle").focus()
        await pilot.pause()
    await _wait_until_active(pilot, app, section_id)


#: Same idea as _SECTION_TAB, for the laboratory sheet.
_LAB_SECTION_TAB: dict[str, str] = {
    "section-lab-identity": "tab-lab-planning",  # top panel, not inside any tab
    "section-lab-characteristics": "tab-lab-planning",
    "tab-lab-planning": "tab-lab-planning",
    "tab-lab-vf": "tab-lab-vf",
    "section-lab-specialties": "tab-lab-attributes",
    "section-lab-features": "tab-lab-attributes",
    "section-lab-rooms": "tab-lab-attributes",
    "section-lab-raw-vis": "tab-lab-inventory",
    "section-lab-items": "tab-lab-inventory",
    "tab-lab-diary": "tab-lab-diary",
}


async def _open_lab_section(pilot, app, section_id: str) -> None:
    """Same idea as _open_section, for the laboratory sheet -- see that
    docstring. The top-panel sections (Identity/Characteristics) aren't
    inside any tab, so they're focused directly regardless of which tab is
    active.
    """
    view = app.screen._laboratory_sheet_view
    assert view is not None, "no laboratory sheet is currently shown"
    # Let the view's own initial focus (set when the lab is first shown, and
    # applied a message-loop cycle later) land before we move focus
    # ourselves -- otherwise it can arrive afterwards and steal it back.
    await wait_until(pilot, lambda: view.initial_tab_seen)
    await pilot.pause()
    if section_id in ("section-lab-identity", "section-lab-characteristics"):
        collapsible = view.query_one(f"#{section_id}", Collapsible)
        collapsible.query_one("CollapsibleTitle").focus()
        await pilot.pause()
        return
    tab_id = _LAB_SECTION_TAB[section_id]
    view.query_one(TabbedContent).active = tab_id
    await pilot.pause()
    if section_id != tab_id:
        collapsible = view.query_one(f"#{section_id}", Collapsible)
        collapsible.query_one("CollapsibleTitle").focus()
        await pilot.pause()
    else:
        # A flat tab: wait for the tab switch to clear focus so dispatch
        # resolves to the tab itself.
        await wait_until(pilot, lambda: app.screen._active_section() == section_id)


async def test_picker_shows_placeholder_with_no_sagas():
    app = ArsMagicaManagerApp()
    async with app.run_test():
        assert isinstance(app.screen, SagaPickerScreen)
        list_view = app.screen.query_one("#saga-list", ListView)
        assert len(list_view.children) == 1


async def test_theme_bar_shows_active_theme():
    app = ArsMagicaManagerApp()
    async with app.run_test():
        theme_bar = app.screen.query_one("#theme-bar", ThemeBar)
        assert str(theme_bar.render()) == "Theme: Scriptorum"


async def test_switching_theme_updates_theme_bar_and_persists():
    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        app.theme = "scriptorum-dark"
        await pilot.pause()

        theme_bar = app.screen.query_one("#theme-bar", ThemeBar)
        assert str(theme_bar.render()) == "Theme: Scriptorum Dark"

    assert settings.load_settings() == {"theme": "scriptorum-dark"}


async def test_saving_the_theme_keeps_the_other_settings():
    # B16: every theme change (including the one on launch) rewrote the
    # settings file with the theme alone.
    settings.save_settings({"theme": "scriptorum", "other": 1})

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        app.theme = "scriptorum-dark"
        await pilot.pause()

    assert settings.load_settings() == {"theme": "scriptorum-dark", "other": 1}


async def test_saved_theme_is_restored_on_next_launch():
    settings.save_settings({"theme": "scriptorum-dark"})

    app = ArsMagicaManagerApp()
    async with app.run_test():
        assert app.theme == "scriptorum-dark"


async def test_create_saga_flow_saves_and_returns_to_picker():
    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await pilot.press("n")
        await pilot.pause()
        assert _is_form(app.screen, "Create a New Saga")

        form = app.screen
        form.query_one("#fld-name", Input).value = "Dammerstein"
        form.query_one("#fld-storyguide", Input).value = "Alex"
        form.query_one("#fld-year", Input).value = "1220"

        await pilot.click("#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, SagaPickerScreen)

    assert storage.list_sagas() == ["dammerstein"]
    saga = storage.load_saga("dammerstein")
    assert saga.name == "Dammerstein"
    assert saga.storyguide == "Alex"
    assert saga.current_year == 1220
    assert saga.current_season == "Spring"
    assert saga.description == ""


async def test_create_saga_requires_name_and_storyguide():
    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await pilot.press("n")
        await pilot.pause()

        await pilot.click("#btn-save")
        await pilot.pause()

        # Validation failed, so we're still on the create screen and nothing saved.
        assert _is_form(app.screen, "Create a New Saga")

    assert storage.list_sagas() == []


async def test_selecting_a_saga_opens_the_workspace():
    storage.save_saga(
        Saga(id="test_saga", name="Test Saga", storyguide="Alex", current_year=1220)
    )

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        list_view = app.screen.query_one("#saga-list", ListView)
        assert list_view.index == 0

        await pilot.press("enter")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert app.screen.saga.id == "test_saga"
        assert app.screen.selected_kind == "saga"


async def test_workspace_tree_has_no_covenants_for_a_fresh_saga():
    storage.save_saga(Saga(id="test_saga", name="Test Saga", storyguide="Alex"))

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_workspace(pilot)

        tree = app.screen.query_one("#nav-tree", Tree)
        # No covenants: just the saga's Spells node.
        assert [n.data for n in tree.root.children] == [("spells",)]


async def test_create_covenant_flow_saves_covenant():
    storage.save_saga(Saga(id="test_saga", name="Test Saga", storyguide="Alex"))

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_workspace(pilot)

        await pilot.press("n")
        await pilot.pause()
        assert _is_form(app.screen, "Create a New Covenant")

        app.screen.query_one("#fld-name", Input).value = "Fengheld"
        app.screen.query_one("#fld-notes", Input).value = "A border covenant"

        await pilot.click("#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert app.screen.selected_covenant is not None
        assert app.screen.selected_covenant.name == "Fengheld"
        tree = app.screen.query_one("#nav-tree", Tree)
        # The new covenant, then the Spells node.
        assert [n.data[0] for n in tree.root.children] == ["covenant", "spells"]

    saga = storage.load_saga("test_saga")
    assert len(saga.covenants) == 1
    covenant = saga.covenants[0]
    assert covenant.name == "Fengheld"
    assert covenant.notes == "A border covenant"
    assert covenant.id == "fengheld"


async def test_create_covenant_requires_name():
    storage.save_saga(Saga(id="test_saga", name="Test Saga", storyguide="Alex"))

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_workspace(pilot)

        await pilot.press("n")
        await pilot.pause()

        await pilot.click("#btn-save")
        await pilot.pause()

        assert _is_form(app.screen, "Create a New Covenant")

    saga = storage.load_saga("test_saga")
    assert saga.covenants == []


def _saga_with_empty_covenant() -> Saga:
    return Saga(
        id="test_saga",
        name="Test Saga",
        storyguide="Alex",
        covenants=[Covenant(id="cov1", saga_id="test_saga", name="Test Covenant")],
    )


async def _select_covenant(pilot, app, covenant_id: str = "cov1") -> None:
    await _open_workspace(pilot)
    await _select(pilot, app, ("covenant", covenant_id))


async def _select_character(pilot, app, character_id: str = "char1") -> None:
    await _select_covenant(pilot, app)
    await _select(pilot, app, ("character", character_id))


async def _select_laboratory(pilot, app, laboratory_id: str = "lab1") -> None:
    await _select_covenant(pilot, app)
    await _select(pilot, app, ("laboratory", laboratory_id))


async def _select_familiar(pilot, app, familiar_id: str = "fam1") -> None:
    await _select_covenant(pilot, app)
    await _select(pilot, app, ("familiar", familiar_id))


async def test_create_character_at_saga_level_is_unassigned_and_selectable():
    storage.save_saga(Saga(id="test_saga", name="Test Saga", storyguide="Alex"))

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_workspace(pilot)
        assert app.screen.selected_kind == "saga"

        await pilot.press("c")
        await pilot.pause()
        assert _is_form(app.screen, "Create a New Character")
        # No covenant is selected, so the dialog defaults to none.
        assert app.screen.query_one("#fld-covenant_id", Select).value == Select.NULL
        app.screen.query_one("#fld-name", Input).value = "Wandering Grog"
        app.screen.query_one("#fld-type", Select).value = "grog"
        await pilot.click("#btn-save")
        await pilot.pause()

        # Listed under the saga, and selectable from the tree.
        tree = app.screen.query_one("#nav-tree", Tree)
        assert _find_node(tree, ("character_group", None)) is not None
        await _select(pilot, app, ("character", "wandering_grog"))
        assert app.screen.selected_character.name == "Wandering Grog"
        assert app.screen.selected_covenant is None

    assert storage.load_saga("test_saga").characters[0].covenant_id is None


async def test_edit_saga_saves_name_storyguide_and_description():
    storage.save_saga(Saga(id="test_saga", name="Test Saga", storyguide="Alex"))

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_workspace(pilot)
        assert app.screen.selected_kind == "saga"

        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Saga")
        dialog = app.screen
        dialog.query_one("#fld-name", Input).value = "Dammerstein [Solo]"
        dialog.query_one("#fld-storyguide", Input).value = "Robin"
        dialog.query_one("#fld-description", Input).value = "A one-magus saga."
        dialog.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

        # Header and tree pick up the rename, brackets escaped.
        assert app.screen.sub_title.startswith(r"Dammerstein \[Solo]")
        tree = app.screen.query_one("#nav-tree", Tree)
        assert str(tree.root.label) == "Dammerstein [Solo]"  # brackets survive, literal
        # The saga detail panel too (re-shown after saving).
        panel = app.screen.query_one("#detail-pane").query_one(Static)
        assert "Dammerstein [Solo]" in str(panel.render())

    saga = storage.load_saga("test_saga")
    assert (saga.name, saga.storyguide, saga.description) == (
        "Dammerstein [Solo]",
        "Robin",
        "A one-magus saga.",
    )


async def test_edit_saga_requires_name_and_storyguide():
    storage.save_saga(Saga(id="test_saga", name="Test Saga", storyguide="Alex"))

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _open_workspace(pilot)
        await pilot.press("e")
        await pilot.pause()
        dialog = app.screen
        assert _is_form(dialog, "Edit Saga")

        dialog.query_one("#fld-name", Input).value = "  "
        dialog.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert _is_form(app.screen, "Edit Saga")  # refused

        dialog.query_one("#fld-name", Input).value = "Test Saga"
        dialog.query_one("#fld-storyguide", Input).value = ""
        dialog.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert _is_form(app.screen, "Edit Saga")  # still refused

        dialog.query_one("#fld-storyguide", Input).value = "Alex"
        dialog.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)


async def test_create_character_defaults_to_current_covenant():
    storage.save_saga(_saga_with_empty_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)

        await pilot.press("c")
        await pilot.pause()
        assert _is_form(app.screen, "Create a New Character")

        app.screen.query_one("#fld-name", Input).value = "Leandro"

        await pilot.click("#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert app.screen.selected_character is not None
        assert app.screen.selected_character.name == "Leandro"

    saga = storage.load_saga("test_saga")
    assert len(saga.characters) == 1
    character = saga.characters[0]
    assert character.name == "Leandro"
    assert character.type == "magus"
    assert character.covenant_id == "cov1"


async def test_create_character_with_no_covenant():
    storage.save_saga(_saga_with_empty_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)

        await pilot.press("c")
        await pilot.pause()

        form = app.screen
        form.query_one("#fld-name", Input).value = "Wandering Grog"
        form.query_one("#fld-type", Select).value = "grog"
        form.query_one("#fld-covenant_id", Select).value = Select.NULL

        await pilot.click("#btn-save")
        await pilot.pause()

    saga = storage.load_saga("test_saga")
    character = saga.characters[0]
    assert character.name == "Wandering Grog"
    assert character.type == "grog"
    assert character.covenant_id is None


async def test_create_character_requires_name():
    storage.save_saga(_saga_with_empty_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)

        await pilot.press("c")
        await pilot.pause()

        await pilot.click("#btn-save")
        await pilot.pause()

        assert _is_form(app.screen, "Create a New Character")

    saga = storage.load_saga("test_saga")
    assert saga.characters == []


def _sample_saga_with_covenant() -> Saga:
    return Saga(
        id="test_saga",
        name="Test Saga",
        storyguide="Alex",
        covenants=[
            Covenant(
                id="cov1",
                saga_id="test_saga",
                name="Test Covenant",
                notes="A nice place",
                vis_stock={"Ignem": 5},
                aura=3,
            )
        ],
        characters=[
            Character(
                id="char1",
                name="Leandro",
                type="magus",
                covenant_id="cov1",
                characteristics=Characteristics(intelligence=3, stamina=1),
                arts={
                    "creo": ArtScore(level=10, xp=55),
                    "ignem": ArtScore(level=5, xp=15),
                },
                abilities=[
                    Ability(
                        name="Magic Theory",
                        category="Academic",
                        level=5,
                        xp=75,
                        specialty="Lab Totals",
                    )
                ],
                virtues_flaws=[
                    VirtueFlawInstance(
                        vf_id="vf_affinity_with_art", params={"art": "creo"}
                    )
                ],
                spells_known=[KnownSpell(spell_id="spell1")],
                assigned_lab_id="lab1",
            )
        ],
        laboratories=[
            Laboratory(
                id="lab1",
                covenant_id="cov1",
                name="Leandro's Sanctum",
                owner_id="char1",
                characteristics=LabCharacteristics(size=1),
                features=["Well-Stocked"],
                virtues_flaws=[VirtueFlawInstance(vf_id="labvf_superior_construction")],
            )
        ],
        books=[
            Book(
                id="book1",
                name="On the Theory of Magic",
                type="Ability Summa",
                ability="Magic Theory",
                quality=6,
                level=8,
                author="Bonisagus",
                owner_kind="covenant",
                owner_id="cov1",
            ),
            Book(
                id="book2",
                name="Ball of Abysmal Flame",
                type="Lab Text",
                spell_name="Ball of Abysmal Flame",
                level=20,
                owner_kind="covenant",
                owner_id="cov1",
            ),
        ],
        spells=[
            Spell(
                id="spell1",
                name="Ball of Abysmal Flame",
                technique="Creo",
                form="Ignem",
                level=20,
            )
        ],
    )


async def test_selecting_covenant_shows_summary_and_tree_children():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)

        assert app.screen.selected_covenant.id == "cov1"
        view = app.screen._covenant_sheet_view
        assert view is not None
        assert view.query_one("#section-cov-info", Collapsible).title == (
            "Test Covenant"
        )
        assert "A nice place" in view._description_text()
        # The old bare vis_stock became a Raw Vis store on the Possessions tab.
        assert view._pos_rows("vis_store") == [
            (0, "Ignem Vis           Ignem          5")
        ]

        tree = app.screen.query_one("#nav-tree", Tree)
        assert _find_node(tree, ("character_group", "cov1")) is not None
        assert _find_node(tree, ("laboratory_group", "cov1")) is not None
        # No Library node: a covenant's library lives on its sheet's Library tab.
        assert _find_node(tree, ("library", "cov1")) is None
        assert _find_node(tree, ("character", "char1")) is not None
        assert _find_node(tree, ("laboratory", "lab1")) is not None


async def test_selecting_character_shows_sheet_fields():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)

        view = app.screen._character_sheet_view
        assert view.query_one("#section-char-info", Collapsible).title == "Leandro"
        assert "Test Covenant" in view._info_right_text()
        assert "Leandro's Sanctum" in view._info_right_text()
        assert "Int: +3" in view._characteristics_text()
        labels = _ability_labels(view)
        assert "Magic Theory (Lab Totals) 5 75/0" in labels
        assert "Academic" in [
            label for index, label in view._ability_rows() if index is None
        ]
        assert "Affinity with Creo" in _character_vf_labels(view)
        creo_row = view._art_row_label("Creo")
        assert "Creo (Cr)" in creo_row and "10" in creo_row and "55" in creo_row
        assert "Ball of Abysmal Flame" in _known_spell_labels(view)


async def test_selecting_laboratory_shows_owner_and_virtues():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)
        await _select(pilot, app, ("laboratory", "lab1"))

        view = app.screen._laboratory_sheet_view
        identity = view._identity_text()
        assert "Owner: Leandro" in identity
        assert "Aura: 3" in identity
        assert "Well-Stocked" in view._features_text()
        assert "Superior Construction" in view._vf_text()


def _saga_with_bare_character() -> Saga:
    return Saga(
        id="test_saga",
        name="Test Saga",
        storyguide="Alex",
        covenants=[Covenant(id="cov1", saga_id="test_saga", name="Test Covenant")],
        characters=[
            Character(id="char1", name="Leandro", type="magus", covenant_id="cov1")
        ],
    )


def _saga_with_bare_laboratory() -> Saga:
    saga = _saga_with_bare_character()
    saga.laboratories.append(
        Laboratory(id="lab1", covenant_id="cov1", name="Test Lab", owner_id="char1")
    )
    return saga


def _saga_with_familiar() -> Saga:
    saga = _saga_with_bare_character()
    saga.familiars.append(Familiar(id="fam1", character_id="char1", name="Ashwing"))
    return saga


#: Same idea as _SECTION_TAB, for the familiar sheet.
_FAM_SECTION_TAB: dict[str, str] = {
    "section-fam-info": "tab-fam-identity",  # top panel, not inside any tab
    "section-fam-binding": "tab-fam-identity",
    "section-fam-vf-virtues": "tab-fam-identity",
    "section-fam-vf-flaws": "tab-fam-identity",
    "section-fam-personality-traits": "tab-fam-identity",
    "section-fam-reputations": "tab-fam-identity",
    "section-fam-characteristics": "tab-fam-characteristics",
    "section-fam-health": "tab-fam-combat",
    "section-fam-natural-weapons": "tab-fam-combat",
    "tab-fam-abilities": "tab-fam-abilities",
    "tab-fam-powers": "tab-fam-powers",
}


async def _open_familiar_section(pilot, app, section_id: str) -> None:
    """Switch to the tab containing `section_id` and focus that section (so
    its a/A/e/v/V keys apply). Same idea as the character sheet's own
    _open_section()."""
    view = app.screen._familiar_sheet_view
    assert view is not None, "no familiar sheet is currently shown"
    await wait_until(pilot, lambda: view.initial_tab_seen)
    await pilot.pause()
    tab_id = _FAM_SECTION_TAB[section_id]
    view.query_one(TabbedContent).active = tab_id
    await pilot.pause()
    if section_id != tab_id:
        collapsible = view.query_one(f"#{section_id}", Collapsible)
        collapsible.query_one("CollapsibleTitle").focus()
        await pilot.pause()
    await _wait_until_active(pilot, app, section_id)


async def test_binding_a_familiar_nests_it_under_its_magus_and_grants_shared_traits():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_character(pilot, app)
        assert isinstance(app.screen, WorkspaceScreen)

        await pilot.press("f")
        await pilot.pause()
        assert _is_form(app.screen, "Bind a New Familiar")
        # A magus was already selected: it's preselected as the default.
        assert app.screen.query_one("#fld-character_id", Select).value == "char1"

        app.screen.query_one("#fld-name", Input).value = "Ashwing"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)
        assert app.screen.selected_kind == "familiar"

        # The magus's tree node is now expandable, with the Familiar nested
        # as its one child leaf.
        tree = app.screen.query_one("#nav-tree", Tree)
        magus_node = _find_node(tree, ("character", "char1"))
        familiar_id = next(f.id for f in app.screen.saga.familiars)
        assert [c.data for c in magus_node.children] == [("familiar", familiar_id)]

    saga = storage.load_saga("test_saga")
    [familiar] = saga.familiars
    magus = saga.characters[0]
    assert (familiar.character_id, familiar.name) == ("char1", "Ashwing")
    # True Friend and Loyal (Partner) +3 granted to both partners.
    assert {vf.vf_id for vf in familiar.virtues_flaws} == {"vf_true_friend"}
    assert {vf.vf_id for vf in magus.virtues_flaws} == {"vf_true_friend"}
    assert [(t.name, t.score) for t in familiar.personality_traits] == [
        ("Loyal (Partner)", 3)
    ]
    assert [(t.name, t.score) for t in magus.personality_traits] == [
        ("Loyal (Partner)", 3)
    ]


async def test_bind_familiar_only_defaults_to_the_magus_on_show():
    # B7: after showing a magus, then a laboratory or Spells, the dialog
    # still preselected that magus.
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_character(pilot, app)
        for node in (("laboratory", "lab1"), ("spells",), ("covenant", "cov1")):
            await _select(pilot, app, node)
            await pilot.press("f")
            assert await wait_until(
                pilot, lambda: _is_form(app.screen, "Bind a New Familiar")
            )
            value = app.screen.query_one("#fld-character_id", Select).value
            assert value is Select.NULL, (node, value)
            await pilot.press("escape")
            await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))


async def test_create_familiar_is_disabled_once_every_magus_has_one():
    storage.save_saga(_saga_with_familiar())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_character(pilot, app)
        assert app.screen.check_action("create_familiar", ()) is False
        await pilot.press("f")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)  # refused, no dialog


async def test_editing_familiar_info_updates_the_top_panel_and_tree():
    storage.save_saga(_saga_with_familiar())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_familiar(pilot, app)
        assert app.screen._active_section() == "section-fam-info"

        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Familiar")
        app.screen.query_one("#fld-name", Input).value = "Nightwing"
        app.screen.query_one("#fld-species", Input).value = "Raven"
        app.screen.query_one("#fld-magic_might", Input).value = "8"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        view = app.screen._familiar_sheet_view
        text = str(view.query_one("#fam-info-content", Static).render())
        assert "Species / Description: Raven" in text
        assert "Magic Might Score: 8" in text

        tree = app.screen.query_one("#nav-tree", Tree)
        magus_node = _find_node(tree, ("character", "char1"))
        assert "Nightwing" in str(magus_node.children[0].label)

    [familiar] = storage.load_saga("test_saga").familiars
    assert (familiar.name, familiar.species, familiar.magic_might) == (
        "Nightwing",
        "Raven",
        8,
    )


async def test_editing_familiar_binding_shows_live_cord_cost_and_saves():
    storage.save_saga(_saga_with_familiar())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_familiar(pilot, app)
        await _open_familiar_section(pilot, app, "section-fam-binding")
        assert app.screen._active_section() == "section-fam-binding"

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditFamiliarBindingScreen)
        app.screen.query_one("#select-fam-golden_cord", Select).value = 3
        await pilot.pause()
        assert (
            str(app.screen.query_one("#cost-fam-golden_cord", Static).render())
            == "30 pts"
        )
        app.screen.query_one("#input-fam-lab-total", Input).value = "45"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        view = app.screen._familiar_sheet_view
        text = str(view.query_one("#fam-binding-content", Static).render())
        assert "Golden Cord: +3 (30 pts)" in text
        assert "Initial Binding Lab Total: 45" in text

    [familiar] = storage.load_saga("test_saga").familiars
    assert (familiar.golden_cord, familiar.binding_lab_total) == (3, 45)


async def test_editing_familiar_characteristics_updates_the_panel_and_saves():
    storage.save_saga(_saga_with_familiar())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_familiar(pilot, app)
        await _open_familiar_section(pilot, app, "section-fam-characteristics")
        assert app.screen._active_section() == "section-fam-characteristics"

        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Characteristics")
        app.screen.query_one("#fld-stamina", Input).value = "3"
        app.screen.query_one("#fld-base_soak", Input).value = "5"
        app.screen.query_one("#fld-magic_resistance", Input).value = "12"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        view = app.screen._familiar_sheet_view
        text = str(view.query_one("#fam-characteristics-content", Static).render())
        assert "Sta: +3" in text
        assert "Base Soak: 5" in text
        assert "Magic Resistance: 12" in text

    [familiar] = storage.load_saga("test_saga").familiars
    assert familiar.characteristics.stamina == 3
    assert (familiar.base_soak, familiar.magic_resistance) == (5, 12)


async def test_editing_familiar_wounds_and_fatigue_updates_the_health_panel():
    storage.save_saga(_saga_with_familiar())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_familiar(pilot, app)
        await _open_familiar_section(pilot, app, "section-fam-health")
        assert app.screen._active_section() == "section-fam-health"

        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Wounds")
        app.screen.query_one("#fld-light", Input).value = "2"
        app.screen.query_one("#fld-incapacitated", Checkbox).value = True
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        view = app.screen._familiar_sheet_view
        wounds_text = str(view.query_one("#fam-wounds-content", Static).render())
        assert "Light Wounds:  2" in wounds_text
        assert "Incapacitated: yes" in wounds_text

        await pilot.click("#btn-fam-health-fatigue-edit")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Fatigue Level")
        app.screen.query_one("#fld-level", Select).value = "weary"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        fatigue_text = str(view.query_one("#fam-fatigue-content", Static).render())
        assert "Fatigue Level: Weary" in fatigue_text

    [familiar] = storage.load_saga("test_saga").familiars
    assert (familiar.wounds.light, familiar.wounds.incapacitated) == (2, True)
    assert familiar.fatigue_level == "weary"


async def test_familiar_natural_weapons_use_generic_add_edit_remove():
    storage.save_saga(_saga_with_familiar())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_familiar(pilot, app)
        await _open_familiar_section(pilot, app, "section-fam-natural-weapons")
        assert app.screen.check_action("add", ()) is True

        await pilot.press("a")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        _fill(app, name="Bite", weapon_attack=5)
        await _save_dialog(pilot, app)

        [familiar] = storage.load_saga("test_saga").familiars
        assert len(familiar.natural_weapons) == 1
        assert familiar.natural_weapons[0].name == "Bite"
        assert familiar.natural_weapons[0].weapon_attack == 5

        view = app.screen._familiar_sheet_view
        list_widget = view.query_one("#fam-natural-weapons-list", SelectableList)
        assert any("Bite" in str(o.prompt) for o in list_widget.options)

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    assert storage.load_saga("test_saga").familiars[0].natural_weapons == []


async def test_familiar_abilities_use_generic_add_edit_remove():
    storage.save_saga(_saga_with_familiar())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_familiar(pilot, app)
        await _open_familiar_section(pilot, app, "tab-fam-abilities")
        assert app.screen.check_action("add", ()) is True

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, AbilityPickerScreen)
        await pilot.click("#ability-ab_athletics")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        app.screen.query_one("#fld-level", Input).value = "3"
        app.screen.query_one("#fld-specialty", Input).value = "Running"
        await pilot.click("#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        view = app.screen._familiar_sheet_view
        assert "Athletics (Running) 3 0/0" in _fam_ability_labels(view)

        [familiar] = storage.load_saga("test_saga").familiars
        assert len(familiar.abilities) == 1
        assert familiar.abilities[0].name == "Athletics"
        assert familiar.abilities[0].level == 3
        assert familiar.abilities[0].specialty == "Running"

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        app.screen.query_one("#fld-level", Input).value = "4"
        await pilot.click("#btn-save")
        await pilot.pause()
        assert "Athletics (Running) 4 0/0" in _fam_ability_labels(view)

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    assert storage.load_saga("test_saga").familiars[0].abilities == []


async def test_familiar_bond_powers_use_generic_add_edit_remove():
    storage.save_saga(_saga_with_familiar())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_familiar(pilot, app)
        await _open_familiar_section(pilot, app, "tab-fam-powers")
        assert app.screen.check_action("add", ()) is True

        await pilot.press("a")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        _fill(app, name="Speak with Beasts", level=15, uses_per_day=3)
        await _save_dialog(pilot, app)

        [familiar] = storage.load_saga("test_saga").familiars
        assert len(familiar.bond_powers) == 1
        assert familiar.bond_powers[0].name == "Speak with Beasts"
        assert familiar.bond_powers[0].level == 15
        assert familiar.bond_powers[0].uses_per_day == 3
        assert familiar.bond_powers[0].technique == ""

        view = app.screen._familiar_sheet_view
        list_widget = view.query_one("#fam-bond-powers-list", SelectableList)
        assert any("Speak with Beasts" in str(o.prompt) for o in list_widget.options)

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        _fill(app, vis_spent=2)
        await _save_dialog(pilot, app)

        [familiar] = storage.load_saga("test_saga").familiars
        assert familiar.bond_powers[0].vis_spent == 2

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    assert storage.load_saga("test_saga").familiars[0].bond_powers == []


async def test_familiar_virtues_flaws_add_via_v_and_remove_via_shift_v():
    storage.save_saga(_saga_with_familiar())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_familiar(pilot, app)
        await _open_familiar_section(pilot, app, "section-fam-vf-virtues")
        assert app.screen.check_action("add_virtue_flaw", ()) is True

        await pilot.press("v")
        await pilot.pause()
        assert isinstance(app.screen, VirtueFlawPickerScreen)
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    saga.familiars[0].virtues_flaws.append(VirtueFlawInstance(vf_id="vf_true_friend"))
    storage.save_saga(saga)

    app2 = ArsMagicaManagerApp()
    async with app2.run_test(size=(140, 70)) as pilot:
        await _select_familiar(pilot, app2)
        await _open_familiar_section(pilot, app2, "section-fam-vf-virtues")
        assert app2.screen.check_action("remove_virtue_flaw", ()) is True
        await pilot.press("V")
        await pilot.pause()
        assert isinstance(app2.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await wait_until(pilot, lambda: isinstance(app2.screen, ConfirmScreen))
        await pilot.press("y")
        await wait_until(pilot, lambda: isinstance(app2.screen, WorkspaceScreen))

    assert storage.load_saga("test_saga").familiars[0].virtues_flaws == []


async def test_removing_a_familiar_virtue_flaw_uses_the_chosen_row_and_confirms():
    # B6: familiar V&F removal ignored the chosen row and never asked.
    saga = _saga_with_familiar()
    saga.familiars[0].virtues_flaws = [
        VirtueFlawInstance(vf_id="vf_true_friend"),
        VirtueFlawInstance(vf_id="vf_true_friend"),
        VirtueFlawInstance(vf_id="vf_puissant_ability", params={"ability": "Brawl"}),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_familiar(pilot, app)
        await _open_familiar_section(pilot, app, "section-fam-vf-virtues")
        rows = app.screen._familiar_sheet_view.query_one(
            "#fam-vf-virtues-list", SelectableList
        )
        rows.focus()
        await pilot.pause()
        position = next(i for i, (index, _) in enumerate(rows._rows) if index == 2)
        rows.highlighted = position
        assert await wait_until(pilot, lambda: rows._marked == position)

        await pilot.press("V")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert "Puissant" in message, message
        await pilot.press("n")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        assert len(storage.load_saga("test_saga").familiars[0].virtues_flaws) == 3

        await pilot.press("V")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))

    assert [
        vf.vf_id for vf in storage.load_saga("test_saga").familiars[0].virtues_flaws
    ] == [
        "vf_true_friend",
        "vf_true_friend",
    ]


async def test_familiar_details_panels_are_shaded_like_every_other_sheet():
    # B13: the familiar sheet's details panels had no shaded panel style.
    storage.save_saga(_saga_with_familiar())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_familiar(pilot, app)
        view = app.screen._familiar_sheet_view
        for panel_id in (
            "fam-vf-info",
            "fam-natural-weapons-info",
            "fam-ability-info",
            "fam-bond-powers-info",
        ):
            panel = view.query_one(f"#{panel_id}", Static)
            assert panel.has_class("details-panel"), panel_id
            assert panel.styles.background.a > 0, panel_id


async def test_familiar_personality_traits_use_generic_add_edit_remove():
    storage.save_saga(_saga_with_familiar())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_familiar(pilot, app)
        await _open_familiar_section(pilot, app, "section-fam-personality-traits")
        assert app.screen.check_action("add", ()) is True

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        app.screen.query_one("#fld-name", Input).value = "Fearless"
        app.screen.query_one("#fld-score", Input).value = "2"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        [familiar] = storage.load_saga("test_saga").familiars
        assert [(t.name, t.score) for t in familiar.personality_traits] == [
            ("Fearless", 2)
        ]

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))

    assert storage.load_saga("test_saga").familiars[0].personality_traits == []


def _saga_with_populated_laboratory() -> Saga:
    """A lab with one entry in every editable list (two Raw Vis Arts, so
    sorted order -- aquam, ignem -- is meaningful)."""
    saga = _saga_with_bare_laboratory()
    lab = saga.laboratories[0]
    lab.specialties = ["Ignem"]
    lab.features = ["Arcane Library"]
    lab.rooms = [NamedDescription(name="Vault", description="Locked")]
    lab.inventory_items = [NamedDescription(name="Silver Mirror", description="Old")]
    lab.raw_vis = {"ignem": 4, "aquam": 2}
    lab.diary = [
        DiaryEntry(year=1220, season="Spring", name="Studied", details="Notes")
    ]
    return saga


async def test_add_virtue_flaw_without_parameters_to_character():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf-virtues")

        await pilot.press("v")
        await pilot.pause()
        assert isinstance(app.screen, VirtueFlawPickerScreen)

        await _select_vf_picker_entry(pilot, app, "vf_common_sense")

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Common Sense" in _character_vf_labels(app.screen._character_sheet_view)

    saga = storage.load_saga("test_saga")
    character = saga.characters[0]
    assert len(character.virtues_flaws) == 1
    assert character.virtues_flaws[0].vf_id == "vf_common_sense"


async def test_add_virtue_flaw_with_parameters_to_character():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf-virtues")

        await pilot.press("v")
        await pilot.pause()

        await _select_vf_picker_entry(pilot, app, "vf_affinity_with_art")
        assert isinstance(app.screen, FieldsDialog)

        app.screen.query_one("#fld-art", Input).value = "Creo"
        await pilot.click("#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Affinity with Creo" in _character_vf_labels(
            app.screen._character_sheet_view
        )

    saga = storage.load_saga("test_saga")
    character = saga.characters[0]
    assert len(character.virtues_flaws) == 1
    assert character.virtues_flaws[0].vf_id == "vf_affinity_with_art"
    assert character.virtues_flaws[0].params == {"art": "creo"}


async def test_cancelling_param_screen_returns_to_picker_without_adding():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf-virtues")

        await pilot.press("v")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)

        await pilot.press("escape")
        await pilot.pause()

        assert isinstance(app.screen, VirtueFlawPickerScreen)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].virtues_flaws == []


async def test_virtue_flaw_picker_excludes_already_held_entries():
    saga = _saga_with_bare_character()
    saga.characters[0].virtues_flaws.append(
        VirtueFlawInstance(vf_id="vf_affinity_with_art", params={"art": "creo"})
    )
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf-virtues")

        await pilot.press("v")
        await pilot.pause()

        picker_list = app.screen.query_one("#vf-picker-list", ListView)
        item_ids = [item.id for item in picker_list.children]
        assert "vf-vf_affinity_with_art" not in item_ids


async def test_virtue_flaw_picker_search_filters_by_typed_text():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf-virtues")

        await pilot.press("v")
        await pilot.pause()
        assert isinstance(app.screen, VirtueFlawPickerScreen)

        picker_list = app.screen.query_one("#vf-picker-list", ListView)
        assert len(picker_list.children) > 100  # the full 624-entry catalog

        await _wait_for_picker_ready(pilot, app)

        app.screen.query_one("#picker-search", Input).value = "common sense"
        await wait_until(pilot, lambda: len(picker_list.children) == 1)

        item_ids = [item.id for item in picker_list.children]
        assert item_ids == ["vf-vf_common_sense"]


async def test_virtue_flaw_picker_search_shows_no_matches_message():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf-virtues")

        await pilot.press("v")
        await pilot.pause()

        await _wait_for_picker_ready(pilot, app)

        app.screen.query_one("#picker-search", Input).value = "xyzzy nonexistent"
        picker_list = app.screen.query_one("#vf-picker-list", ListView)
        await wait_until(pilot, lambda: len(picker_list.children) == 1)

        assert len(picker_list.children) == 1
        assert picker_list.children[0].id is None  # the "(no matches...)" row


async def test_virtue_flaw_picker_enter_in_search_activates_top_match():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf-virtues")

        await pilot.press("v")
        await pilot.pause()

        search = app.screen.query_one("#picker-search", Input)
        search.value = "common sense"
        await pilot.pause()
        await search.action_submit()  # same as pressing Enter in the search box
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Common Sense" in _character_vf_labels(app.screen._character_sheet_view)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].virtues_flaws[0].vf_id == "vf_common_sense"


async def test_lab_virtue_flaw_picker_search_filters_by_typed_text():
    saga = _saga_with_bare_character()
    saga.laboratories.append(
        Laboratory(id="lab1", covenant_id="cov1", name="Test Lab", owner_id="char1")
    )
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)
        await _select(pilot, app, ("laboratory", "lab1"))
        await _open_lab_section(pilot, app, "tab-lab-vf")

        await pilot.press("v")
        await pilot.pause()
        assert isinstance(app.screen, LabVirtueFlawPickerScreen)

        picker_list = app.screen.query_one("#lab-vf-picker-list", ListView)
        assert len(picker_list.children) > 30  # the full 53-entry lab catalog

        await _wait_for_picker_ready(pilot, app)

        app.screen.query_one("#picker-search", Input).value = "superior construction"
        await wait_until(pilot, lambda: len(picker_list.children) == 1)

        item_ids = [item.id for item in picker_list.children]
        assert item_ids == ["labvf-labvf_superior_construction"]


async def test_ability_picker_search_filters_by_typed_text():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "tab-abilities")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, AbilityPickerScreen)

        picker_list = app.screen.query_one("#ability-picker-list", ListView)
        assert len(picker_list.children) > 30  # the full 78-entry catalog

        await _wait_for_picker_ready(pilot, app)

        app.screen.query_one("#picker-search", Input).value = "athletics"
        await wait_until(pilot, lambda: len(picker_list.children) == 1)

        item_ids = [item.id for item in picker_list.children]
        assert item_ids == ["ability-ab_athletics"]


async def test_picker_down_key_moves_focus_from_search_to_list():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "tab-abilities")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, AbilityPickerScreen)

        search = app.screen.query_one("#picker-search", Input)
        assert app.focused is search  # search box is focused on open

        await pilot.press("down")
        await pilot.pause()

        picker_list = app.screen.query_one("#ability-picker-list", ListView)
        assert app.focused is picker_list


async def test_add_virtue_flaw_to_laboratory_uses_lab_picker():
    saga = _saga_with_bare_character()
    saga.laboratories.append(
        Laboratory(id="lab1", covenant_id="cov1", name="Test Lab", owner_id="char1")
    )
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)
        await _select(pilot, app, ("laboratory", "lab1"))
        await _open_lab_section(pilot, app, "tab-lab-vf")

        await pilot.press("v")
        await pilot.pause()
        assert isinstance(app.screen, LabVirtueFlawPickerScreen)

        picker_list = app.screen.query_one("#lab-vf-picker-list", ListView)
        target_id = "labvf-labvf_superior_construction"
        for i, item in enumerate(picker_list.children):
            if item.id == target_id:
                picker_list.index = i
                break
        else:
            raise AssertionError(f"{target_id!r} not found in the lab V&F picker")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Superior Construction" in app.screen._laboratory_sheet_view._vf_text()

    saga = storage.load_saga("test_saga")
    lab = saga.laboratories[0]
    assert len(lab.virtues_flaws) == 1
    assert lab.virtues_flaws[0].vf_id == "labvf_superior_construction"


async def test_create_laboratory_flow_saves_laboratory():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)

        await pilot.press("l")
        await pilot.pause()
        assert _is_form(app.screen, "Create a New Laboratory")

        app.screen.query_one("#fld-name", Input).value = "The Alchemical Tower"
        app.screen.query_one("#fld-size", Input).value = "1"

        await pilot.click("#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert app.screen.selected_laboratory is not None
        assert app.screen.selected_laboratory.name == "The Alchemical Tower"

    saga = storage.load_saga("test_saga")
    assert len(saga.laboratories) == 1
    lab = saga.laboratories[0]
    assert lab.name == "The Alchemical Tower"
    assert lab.covenant_id == "cov1"
    assert lab.characteristics.size == 1
    assert lab.owner_id is None


async def test_create_laboratory_requires_name():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)

        await pilot.press("l")
        await pilot.pause()

        await pilot.click("#btn-save")
        await pilot.pause()

        assert _is_form(app.screen, "Create a New Laboratory")

    saga = storage.load_saga("test_saga")
    assert saga.laboratories == []


async def test_create_laboratory_requires_integer_size():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)

        await pilot.press("l")
        await pilot.pause()

        app.screen.query_one("#fld-name", Input).value = "The Tower"
        app.screen.query_one("#fld-size", Input).value = "not a number"

        await pilot.click("#btn-save")
        await pilot.pause()

        assert _is_form(app.screen, "Create a New Laboratory")

    saga = storage.load_saga("test_saga")
    assert saga.laboratories == []


async def test_add_ability_without_parameters_to_character():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "tab-abilities")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, AbilityPickerScreen)

        await pilot.click("#ability-ab_athletics")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)

        app.screen.query_one("#fld-level", Input).value = "3"
        app.screen.query_one("#fld-specialty", Input).value = "Running"

        await pilot.click("#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Athletics (Running) 3 0/0" in _ability_labels(
            app.screen._character_sheet_view
        )

    saga = storage.load_saga("test_saga")
    character = saga.characters[0]
    assert len(character.abilities) == 1
    assert character.abilities[0].name == "Athletics"
    assert character.abilities[0].category == "General"
    assert character.abilities[0].level == 3
    assert character.abilities[0].specialty == "Running"


async def test_add_ability_with_parameters_to_character():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "tab-abilities")

        await pilot.press("a")
        await pilot.pause()

        await pilot.click("#ability-ab_craft")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)

        app.screen.query_one("#fld-craft", Input).value = "Blacksmith"
        await pilot.click("#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, FieldsDialog)
        assert app.screen.title_text == "Craft: Blacksmith"

        app.screen.query_one("#fld-level", Input).value = "2"

        await pilot.click("#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    character = saga.characters[0]
    assert len(character.abilities) == 1
    assert character.abilities[0].name == "Craft: Blacksmith"
    assert character.abilities[0].category == "General"
    assert character.abilities[0].level == 2


async def test_cancelling_ability_details_returns_to_picker_without_adding():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "tab-abilities")

        await pilot.press("a")
        await pilot.pause()

        await pilot.click("#ability-ab_athletics")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)

        await pilot.press("escape")
        await pilot.pause()

        assert isinstance(app.screen, AbilityPickerScreen)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].abilities == []


async def test_ability_picker_excludes_non_templated_duplicates_but_keeps_templated():
    saga = _saga_with_bare_character()
    saga.characters[0].abilities.append(Ability(name="Athletics", level=1))
    saga.characters[0].abilities.append(Ability(name="Craft: Blacksmith", level=1))
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "tab-abilities")

        await pilot.press("a")
        await pilot.pause()

        picker_list = app.screen.query_one("#ability-picker-list", ListView)
        item_ids = [item.id for item in picker_list.children]
        assert "ability-ab_athletics" not in item_ids
        assert "ability-ab_craft" in item_ids


async def test_remove_ability_from_character():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "tab-abilities")
        assert "Magic Theory" in _ability_labels(app.screen._character_sheet_view)

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Magic Theory" not in _ability_labels(app.screen._character_sheet_view)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].abilities == []


async def test_remove_virtue_flaw_from_character():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf-virtues")
        assert "Affinity with Creo" in _character_vf_labels(
            app.screen._character_sheet_view
        )

        await pilot.press("V")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Affinity with Creo" not in _character_vf_labels(
            app.screen._character_sheet_view
        )

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].virtues_flaws == []


async def test_remove_virtue_flaw_from_laboratory():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)
        await _select(pilot, app, ("laboratory", "lab1"))
        await _open_lab_section(pilot, app, "tab-lab-vf")
        assert "Superior Construction" in app.screen._laboratory_sheet_view._vf_text()

        await pilot.press("V")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

        await pilot.press("enter")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))

        assert (
            "Superior Construction" not in app.screen._laboratory_sheet_view._vf_text()
        )

    saga = storage.load_saga("test_saga")
    assert saga.laboratories[0].virtues_flaws == []


async def test_remove_with_nothing_to_remove_stays_on_same_screen():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "tab-abilities")

        await pilot.press("A")
        await pilot.pause()

        # Nothing to remove -- stays on the workspace, no picker opened.
        assert isinstance(app.screen, WorkspaceScreen)


async def test_cancelling_removal_picker_keeps_the_item():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf-virtues")

        await pilot.press("V")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

        await pilot.press("escape")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Affinity with Creo" in _character_vf_labels(
            app.screen._character_sheet_view
        )

    saga = storage.load_saga("test_saga")
    assert len(saga.characters[0].virtues_flaws) == 1


async def test_edit_arts_prefills_existing_scores_and_saves_full_grid():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-arts")

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditArtsScreen)

        assert app.screen.query_one("#input-art-creo-level", Input).value == "10"
        assert app.screen.query_one("#input-art-creo-xp", Input).value == "55"
        assert app.screen.query_one("#input-art-ignem-level", Input).value == "5"
        assert app.screen.query_one("#input-art-ignem-xp", Input).value == "15"
        assert app.screen.query_one("#input-art-rego-level", Input).value == "0"
        assert app.screen.query_one("#input-art-rego-xp", Input).value == "0"

        app.screen.query_one("#input-art-rego-level", Input).value = "3"
        app.screen.query_one("#input-art-rego-xp", Input).value = "6"

        await pilot.click("#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    arts = saga.characters[0].arts
    assert arts["creo"] == ArtScore(level=10, xp=55)
    assert arts["ignem"] == ArtScore(level=5, xp=15)
    assert arts["rego"] == ArtScore(level=3, xp=6)
    # Every one of the 15 Arts is written, not just the ones that were nonzero.
    assert len(arts) == 15
    assert arts["vim"] == ArtScore(level=0, xp=0)


async def test_edit_arts_requires_integers():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-arts")

        await pilot.press("e")
        await pilot.pause()

        app.screen.query_one("#input-art-rego-level", Input).value = "not a number"

        await pilot.click("#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, EditArtsScreen)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].arts == {
        "creo": ArtScore(level=10, xp=55),
        "ignem": ArtScore(level=5, xp=15),
    }


async def test_edit_arts_cancel_discards_changes():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-arts")

        await pilot.press("e")
        await pilot.pause()

        app.screen.query_one("#input-art-rego-level", Input).value = "9"

        await pilot.press("escape")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].arts == {
        "creo": ArtScore(level=10, xp=55),
        "ignem": ArtScore(level=5, xp=15),
    }


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
    # B8: a click inside the pinned Magical Arts section focused its title,
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


async def test_edit_arts_grid_fits_default_terminal_and_accepts_real_typing():
    # A default-sized terminal (80x24) is what run_test uses unless told
    # otherwise, and matches a typical real terminal -- this test drives
    # actual clicks and keystrokes (not direct .value assignment) so a
    # layout tall/wide enough to push rows off-screen, or to block real
    # keyboard input, actually fails here.
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-arts")
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, EditArtsScreen)

        screen_width = app.screen.size.width
        # One Technique row and two Form rows, from opposite ends of the
        # single-column (scrollable) list -- Herbam and Vim aren't visible
        # without scrolling, exercising that the scroll-then-click path
        # itself works, not just whatever's on-screen by default.
        for field_id in (
            "#input-art-rego-level",
            "#input-art-herbam-level",
            "#input-art-vim-level",
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
            await pilot.press("7")
            await pilot.pause()
            assert field.value == "7"

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


async def test_switching_to_laboratory_or_diary_tab_falls_back_to_top_panel():
    """Laboratory and Diary are flat placeholder tabs (no Collapsible) --
    switching to either must clear a stale Collapsible focus from whatever
    tab was active before, so 'e' falls back to editing the top panel
    instead of silently re-dispatching to the section that's no longer
    visible (see CLAUDE.md's flat-tab focus-tracking gotcha)."""
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        # Focus a real Collapsible section first (Aging, in Description).
        await _open_section(pilot, app, "section-aging")
        assert app.screen._active_section() == "section-aging"

        view = app.screen._character_sheet_view
        view.query_one(TabbedContent).active = "tab-lab"
        await pilot.pause()

        assert app.screen._active_section() == "section-char-info"
        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Character Info")
        await pilot.press("escape")
        await pilot.pause()

        # Same check for Diary, switching from a tab with no Collapsible
        # (Laboratory) to another flat tab.
        view.query_one(TabbedContent).active = "tab-diary"
        await pilot.pause()
        assert app.screen._active_section() == "section-char-info"
        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Character Info")


async def test_creating_a_second_character_after_viewing_the_first_works():
    storage.save_saga(_saga_with_empty_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_covenant(pilot, app)

        # Create the first character.
        await pilot.press("c")
        await pilot.pause()
        app.screen.query_one("#fld-name", Input).value = "Leandro"
        await pilot.click("#btn-save")
        await pilot.pause()
        assert app.screen.selected_character.name == "Leandro"

        # View it explicitly, then go back to the covenant before adding a
        # second one -- the reported repro was a crash on this exact sequence.
        await _select(pilot, app, ("character", "leandro"))
        await _select(pilot, app, ("covenant", "cov1"))

        await pilot.press("c")
        await pilot.pause()
        app.screen.query_one("#fld-name", Input).value = "Guillame"
        await pilot.click("#btn-save")
        await pilot.pause()

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
    # B4: the title was escaped when composed but not when refreshed, so
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
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        view = app.screen._character_sheet_view
        assert view.query_one("#section-char-info", Collapsible).title == (
            "Leandro the Elder"
        )
        info_lines = view._info_right_text().splitlines()
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


async def test_edit_character_info_requires_name():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)

        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Character Info")

        app.screen.query_one("#fld-name", Input).value = ""

        await pilot.click("#btn-save")
        await pilot.pause()

        assert _is_form(app.screen, "Edit Character Info")

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].name == "Leandro"


async def test_edit_characteristics_updates_values():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-char-characteristics")

        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Characteristics")

        app.screen.query_one("#fld-intelligence", Input).value = "3"
        app.screen.query_one("#fld-quickness", Input).value = "-1"

        # An explicit interior offset: this button's default (0, 0) --
        # its exact top-left corner pixel -- doesn't register through the
        # full click pipeline here even though get_widget_at() confirms
        # the button owns that pixel; an interior point is the documented
        # workaround (see the pilot.click() docstring's own example).
        await pilot.click("#btn-save", offset=(8, 1))
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        text = app.screen._character_sheet_view._characteristics_text()
        assert "Int: +3" in text
        assert "Qik: -1" in text

    saga = storage.load_saga("test_saga")
    c = saga.characters[0].characteristics
    assert c.intelligence == 3
    assert c.quickness == -1


async def test_edit_ability_updates_existing_entry():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "tab-abilities")

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

        await pilot.press("enter")  # only one ability -- select it
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        assert app.screen.query_one("#fld-level", Input).value == "5"
        assert app.screen.query_one("#fld-xp", Input).value == "75"

        app.screen.query_one("#fld-level", Input).value = "6"
        app.screen.query_one("#fld-xp", Input).value = "90"

        await pilot.click("#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Magic Theory (Lab Totals) 6 90/0" in _ability_labels(
            app.screen._character_sheet_view
        )

    saga = storage.load_saga("test_saga")
    ability = saga.characters[0].abilities[0]
    assert ability.level == 6
    assert ability.xp == 90
    assert ability.category == "Academic"


def _saga_with_character_and_spell() -> Saga:
    saga = _saga_with_bare_character()
    saga.spells.append(
        Spell(
            id="spell1", name="Pilum of Fire", technique="Creo", form="Ignem", level=20
        )
    )
    return saga


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
        await pilot.pause()

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

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert app.screen._character_sheet_view._known_spell_rows() == []

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].spells_known == []


async def test_known_spells_can_be_catalog_spells():
    saga = _saga_with_character_and_spell()
    saga.characters[0].spells_known = [
        KnownSpell(spell_id="spell_aegis_of_the_hearth"),
        KnownSpell(spell_id="gone"),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        labels = _known_spell_labels(app.screen._character_sheet_view)
        assert "Aegis of the Hearth" in labels and "Ritual" in labels
        assert "gone (unknown spell)" in labels


async def test_edit_spell_mastery_sets_score_xp_and_abilities():
    saga = _saga_with_character_and_spell()
    saga.characters[0].spells_known = [KnownSpell(spell_id="spell1")]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-known-spells")

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)  # only one known spell
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, MasteryEditScreen)

        app.screen.query_one("#input-mastery-score", Input).value = "2"
        app.screen.query_one("#input-mastery-xp", Input).value = "10"
        await pilot.click("#btn-add-ability")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        app.screen.query_one("#fld-name", Input).value = "Fast Casting"
        app.screen.query_one("#fld-level", Input).value = "1"
        await pilot.click("#btn-save")
        await pilot.pause()
        assert isinstance(app.screen, MasteryEditScreen)

        # Removing one asks first (B6); No keeps it.
        mastery = app.screen
        mastery.query_one("#mastery-abilities-list", ListView).index = 0
        await pilot.pause()
        mastery.query_one("#btn-remove-ability", Button).press()
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        assert "Delete Fast Casting?" in str(
            app.screen.query_one("#confirm-message", Static).render()
        )
        await pilot.press("n")
        await wait_until(pilot, lambda: app.screen is mastery)
        assert len(mastery._abilities) == 1

        await pilot.click("#btn-save")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    known = saga.characters[0].spells_known[0]
    assert known.mastery_score == 2
    assert known.mastery_xp == 10
    assert len(known.mastery_abilities) == 1
    assert known.mastery_abilities[0].name == "Fast Casting"
    assert known.mastery_abilities[0].level == 1


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
        await pilot.pause()
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

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].inventory == []


async def test_add_action_disabled_on_tabs_without_addable_lists():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)  # defaults to the top panel

        await pilot.press("a")
        await pilot.pause()

        # The top panel has nothing to "add" -- the binding is disabled there.
        assert isinstance(app.screen, WorkspaceScreen)


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
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        view = app.screen._character_sheet_view
        left = view._biographical_left_text()
        assert "Player: Alex" in left
        assert "Height: 1.8" in left
        assert "Handedness: left" in left
        assert view._biographical_right_text() == "Born in Aachen."
        # Age (derived from Year Born) lives in the top panel, refreshed
        # alongside Biographical Detail since they share Year Born.
        assert re.search(r"Age:\s+40\b", view._info_left_text())  # 1220 - 1180

    saga = storage.load_saga("test_saga")
    character = saga.characters[0]
    assert character.background.player == "Alex"
    assert character.background.year_born == 1180
    assert character.description.height == 1.8
    assert character.description.handedness == "left"
    assert character.description.biography == "Born in Aachen."


async def test_edit_aging_updates_decrepitude_and_warping():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-aging")

        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Aging & Warping")

        app.screen.query_one("#fld-decrepitude", Input).value = "2"
        app.screen.query_one("#fld-warping_score", Input).value = "1"
        app.screen.query_one("#fld-warping_points", Input).value = "6"

        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        text = app.screen._character_sheet_view._aging_text()
        assert "Decrepitude: 2" in text
        assert "Warping: 1/6" in text

    saga = storage.load_saga("test_saga")
    aging = saga.characters[0].aging
    assert aging.decrepitude == 2
    assert aging.warping_score == 1
    assert aging.warping_points == 6


async def test_edit_wounds_updates_counts_and_flags():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-char-health")

        # 'e' on the merged Health section defaults to Wounds (column 1).
        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Wounds")

        app.screen.query_one("#fld-soak", Input).value = "5"
        app.screen.query_one("#fld-medium", Input).value = "2"
        app.screen.query_one("#fld-incapacitated", Checkbox).value = True

        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        text = app.screen._character_sheet_view._wounds_text()
        assert "Soak: 5" in text
        assert "Medium Wounds: 2" in text
        assert "Incapacitated: yes" in text

    saga = storage.load_saga("test_saga")
    wounds = saga.characters[0].wounds
    assert wounds.soak == 5
    assert wounds.medium == 2
    assert wounds.incapacitated is True


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
        await pilot.pause()
        assert _is_form(app.screen, "Edit Fatigue Level")

        app.screen.query_one("#fld-level", Select).value = "tired"
        await pilot.click("#btn-save", offset=(8, 1))
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert (
            "Fatigue Level: Tired" in app.screen._character_sheet_view._fatigue_text()
        )

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].fatigue_level == "tired"


async def test_add_and_remove_personality_trait():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-personality-traits")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)

        app.screen.query_one("#fld-name", Input).value = "Curious"
        app.screen.query_one("#fld-score", Input).value = "3"
        await pilot.click("#btn-save", offset=(8, 1))
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        rows = app.screen._character_sheet_view._personality_trait_rows()
        assert "Curious: +3" in rows[0][1]

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].personality_traits == []


async def test_add_and_remove_reputation():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-reputations")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)

        app.screen.query_one("#fld-name", Input).value = "Skilled Enchanter"
        app.screen.query_one("#fld-score", Input).value = "2"
        await pilot.click("#btn-save", offset=(8, 1))
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        rows = app.screen._character_sheet_view._reputation_rows()
        assert "Skilled Enchanter: 2" in rows[0][1]

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].reputations == []


async def test_add_and_remove_raw_vis():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-raw-vis-hermetic")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)

        app.screen.query_one("#fld-art", Select).value = "creo"
        app.screen.query_one("#fld-pawns", Input).value = "5"
        await pilot.click("#btn-save", offset=(8, 1))
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        rows = app.screen._character_sheet_view._raw_vis_rows()
        assert "Creo: 5 pawn(s)" in rows[0][1]

        # Adding the same Art again accumulates rather than overwriting.
        await pilot.press("a")
        await pilot.pause()
        app.screen.query_one("#fld-art", Select).value = "creo"
        app.screen.query_one("#fld-pawns", Input).value = "3"
        await pilot.click("#btn-save", offset=(8, 1))
        await pilot.pause()
        rows = app.screen._character_sheet_view._raw_vis_rows()
        assert "Creo: 8 pawn(s)" in rows[0][1]

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    assert saga.characters[0].raw_vis == {}


async def test_raw_vis_stays_live_across_both_tabs():
    """Raw Vis deliberately appears twice (Hermetic Magic and Inventory),
    both backed by character.raw_vis -- adding/editing/removing from one
    tab's list must also update the other tab's list, even though it's not
    the active tab when the mutation happens (see STORY-207's draft2 note:
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
        await pilot.pause()
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
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)  # only one entry
        await pilot.press("enter")
        await pilot.pause()
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
        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)  # only one entry
        await pilot.press("enter")
        await pilot.pause()
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
        await pilot.pause()

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
    """STORY-204: a name with [brackets] must not vanish -- Textual/Rich
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
        identity = app.screen._laboratory_sheet_view._identity_text()
        assert "[Vault] Lab" in identity


async def test_fields_dialog_info_field_escapes_bracketed_values():
    """STORY-204: FieldsDialog's read-only "info" row (screens/fields.py's
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
        app.screen.query_one("#fld-build_points", Input).value = "50"
        app.screen.query_one("#fld-owner_id", Select).value = "char2"

        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        text = app.screen._laboratory_sheet_view._identity_text()
        assert "Name: Obsidian Crucible" in text
        assert "Location: Black Forest" in text
        assert "Points: 50" in text
        assert "Owner: Guillame" in text

    saga = storage.load_saga("test_saga")
    lab = saga.laboratories[0]
    assert lab.name == "Obsidian Crucible"
    assert lab.location == "Black Forest"
    assert lab.build_points == 50
    assert lab.owner_id == "char2"
    # Bidirectional sync: the new owner points back, the old one is freed.
    new_owner = next(c for c in saga.characters if c.id == "char2")
    old_owner = next(c for c in saga.characters if c.id == "char1")
    assert new_owner.assigned_lab_id == "lab1"
    assert old_owner.assigned_lab_id is None


async def test_edit_lab_characteristics_buttons_are_visible_on_screen():
    """Regression: Save/Cancel were scrolled out of view inside the dialog's
    VerticalScroll. Asserts on-screen position, at a small and a large size."""
    storage.save_saga(_saga_with_bare_laboratory())

    for size in ((80, 24), (140, 50)):
        app = ArsMagicaManagerApp()
        async with app.run_test(size=size) as pilot:
            await _select_laboratory(pilot, app)
            await _open_lab_section(pilot, app, "section-lab-characteristics")
            await pilot.press("e")
            await pilot.pause()
            assert _is_form(
                app.screen, "Edit Laboratory Characteristics (manual value)"
            )

            for button_id in ("#btn-save", "#btn-cancel"):
                region = app.screen.query_one(button_id, Button).region
                assert region.height > 0, (size, button_id)
                assert region.bottom <= size[1], (size, button_id)
                assert region.right <= size[0], (size, button_id)


async def test_every_character_sheet_section_starts_expanded():
    storage.save_saga(_saga_with_bare_character())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_character(pilot, app)
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
        text = app.screen._laboratory_sheet_view._characteristics_table_text()
        # Positive green, zero cyan, negative red.
        assert re.search(
            r"Size:\s+\[green\]\+2\[/\] \[cyan\]\+0\[/\] = \[green\]\+2\[/\]", text
        )
        assert re.search(
            r"Safety:\s+\[red\]-1\[/\] \[cyan\]\+0\[/\] = \[red\]-1\[/\]", text
        )
        # Values line up in columns once the colour markup is stripped: every
        # row has its '=' in the same place.
        plain = strip_markup(text)
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
            # Derived stats left of the table.
            derived = view.query_one("#lab-characteristics-derived").region
            table = view.query_one("#lab-characteristics-content").region
            assert derived.right <= table.x, tab_id
            assert derived.y == table.y, tab_id
            # Tab bar directly below the top panel, body inside the sheet.
            assert tabbed.region.y == top.bottom, tab_id
            assert tabbed.region.bottom <= view.region.bottom, tab_id


async def test_opening_a_lab_focuses_identity_so_edit_hotkey_works():
    """Regression: TabbedContent's own initial TabActivated used to clear the
    focus set on opening a lab, leaving 'e' unavailable until the user
    tabbed into a section by hand. No manual focusing here, on purpose."""
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        assert app.screen._active_section() == "section-lab-identity"

        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Laboratory Identity")


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
            pilot, lambda: app.screen._active_section() == "section-lab-identity"
        )
        await pilot.pause()

        await pilot.click("#lab-characteristics-content")
        await wait_until(
            pilot,
            lambda: app.screen._active_section() == "section-lab-characteristics",
        )
        assert app.screen._active_section() == "section-lab-characteristics"

        await pilot.press("e")
        await pilot.pause()
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
        await pilot.pause()
        assert _is_form(app.screen, "Edit Laboratory Characteristics (manual value)")


async def test_lab_attributes_and_inventory_sections_start_expanded():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view

        for section_id in (
            "section-lab-specialties",
            "section-lab-features",
            "section-lab-rooms",
            "section-lab-raw-vis",
            "section-lab-items",
        ):
            assert not view.query_one(f"#{section_id}", Collapsible).collapsed


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


async def test_add_and_remove_specialty():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        await _open_lab_section(pilot, app, "section-lab-specialties")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)

        app.screen.query_one("#fld-item", Input).value = "Ignem"
        await pilot.click("#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Ignem" in app.screen._laboratory_sheet_view._specialties_text()

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    assert saga.laboratories[0].specialties == []


async def test_add_and_remove_feature():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        await _open_lab_section(pilot, app, "section-lab-features")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)

        app.screen.query_one("#fld-item", Input).value = "Altar"
        await pilot.click("#btn-save")
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        assert "Altar" in app.screen._laboratory_sheet_view._features_text()

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    assert saga.laboratories[0].features == []


async def test_add_and_remove_room():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        await _open_lab_section(pilot, app, "section-lab-rooms")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)

        app.screen.query_one("#fld-name", Input).value = "Vault"
        app.screen.query_one("#fld-description", Input).value = "A locked cellar"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        text = app.screen._laboratory_sheet_view._rooms_text()
        assert "Vault: A locked cellar" in text

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    assert saga.laboratories[0].rooms == []


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
        text = app.screen._laboratory_sheet_view._raw_vis_text()
        assert "Ignem: 4 pawn(s)" in text

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

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
        app.screen.query_one("#fld-description", Input).value = "For scrying"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        text = app.screen._laboratory_sheet_view._items_text()
        assert "Silver Mirror: For scrying" in text

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    assert saga.laboratories[0].inventory_items == []


async def test_add_and_remove_diary_entry():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        await _open_lab_section(pilot, app, "tab-lab-diary")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)

        app.screen.query_one("#fld-year", Input).value = "1220"
        app.screen.query_one("#fld-season", Select).value = "Autumn"
        app.screen.query_one("#fld-name", Input).value = "Invented a spell"
        app.screen.query_one("#fld-details", Input).value = "A quiet season of study."
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        assert isinstance(app.screen, WorkspaceScreen)
        text = app.screen._laboratory_sheet_view._diary_text()
        assert "1220 Autumn -- Invented a spell" in text
        assert "A quiet season of study." in text

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    saga = storage.load_saga("test_saga")
    assert saga.laboratories[0].diary == []


async def _pick_first_and_open_editor(pilot, app, section_id: str, editor_type) -> None:
    """Open `section_id`, press 'e', choose the first entry in the picker,
    and check the pre-filled editor dialog appeared."""
    await _open_lab_section(pilot, app, section_id)
    await pilot.press("e")
    await pilot.pause()
    assert isinstance(app.screen, RemovalPickerScreen)
    await pilot.press("enter")
    await pilot.pause()
    assert isinstance(app.screen, editor_type)


async def test_edit_specialty_and_feature():
    storage.save_saga(_saga_with_populated_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view

        await _pick_first_and_open_editor(
            pilot, app, "section-lab-specialties", FieldsDialog
        )
        assert app.screen.query_one("#fld-item", Input).value == "Ignem"
        app.screen.query_one("#fld-item", Input).value = "Vim"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)
        assert "Vim" in view._specialties_text()
        assert "Ignem" not in view._specialties_text()

        await _pick_first_and_open_editor(
            pilot, app, "section-lab-features", FieldsDialog
        )
        assert app.screen.query_one("#fld-item", Input).value == "Arcane Library"
        app.screen.query_one("#fld-item", Input).value = "Aegis"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert "Aegis" in view._features_text()

    lab = storage.load_saga("test_saga").laboratories[0]
    assert lab.specialties == ["Vim"]
    assert lab.features == ["Aegis"]


async def test_edit_room_and_item():
    storage.save_saga(_saga_with_populated_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view

        await _pick_first_and_open_editor(pilot, app, "section-lab-rooms", FieldsDialog)
        name = app.screen.query_one("#fld-name", Input)
        description = app.screen.query_one("#fld-description", Input)
        assert (name.value, description.value) == ("Vault", "Locked")
        name.value = "Strongroom"
        description.value = "Iron-bound"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert "Strongroom: Iron-bound" in view._rooms_text()

        await _pick_first_and_open_editor(pilot, app, "section-lab-items", FieldsDialog)
        assert app.screen.query_one("#fld-name", Input).value == "Silver Mirror"
        app.screen.query_one("#fld-description", Input).value = "Cracked"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert "Silver Mirror: Cracked" in view._items_text()

    lab = storage.load_saga("test_saga").laboratories[0]
    assert lab.rooms == [NamedDescription(name="Strongroom", description="Iron-bound")]
    assert lab.inventory_items == [
        NamedDescription(name="Silver Mirror", description="Cracked")
    ]


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


async def test_edit_diary_entry():
    storage.save_saga(_saga_with_populated_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)

        await _pick_first_and_open_editor(pilot, app, "tab-lab-diary", FieldsDialog)
        assert app.screen.query_one("#fld-year", Input).value == "1220"
        assert app.screen.query_one("#fld-season", Select).value == "Spring"
        assert app.screen.query_one("#fld-name", Input).value == "Studied"
        app.screen.query_one("#fld-season", Select).value = "Winter"
        app.screen.query_one("#fld-details", Input).value = "Revised."
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

        text = app.screen._laboratory_sheet_view._diary_text()
        assert "1220 Winter -- Studied" in text
        assert "Revised." in text

    assert storage.load_saga("test_saga").laboratories[0].diary == [
        DiaryEntry(year=1220, season="Winter", name="Studied", details="Revised.")
    ]


async def test_the_diary_edit_picker_shows_brackets_in_an_entry_name():
    # B5: the remove picker escaped entry names; the edit picker didn't.
    saga = _saga_with_populated_laboratory()
    saga.laboratories[0].diary[0].name = "Studied [Ignem] notes"
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        for key in ("e", "A"):  # edit, remove
            await _open_lab_section(pilot, app, "tab-lab-diary")
            await pilot.press(key)
            assert await wait_until(
                pilot,
                lambda: (
                    isinstance(app.screen, RemovalPickerScreen)
                    and len(app.screen.query("ListItem Label")) == 1
                ),
            )
            labels = [str(label.render()) for label in app.screen.query(Label)]
            assert "1220 Spring -- Studied [Ignem] notes" in labels, (key, labels)
            await pilot.press("escape")
            await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))


async def test_editing_an_empty_lab_list_or_cancelling_changes_nothing():
    storage.save_saga(_saga_with_populated_laboratory())
    bare = _saga_with_bare_laboratory()

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)

        # Cancelling the picker leaves the entry alone.
        await _open_lab_section(pilot, app, "section-lab-specialties")
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

        # Cancelling the editor does too.
        await _pick_first_and_open_editor(
            pilot, app, "section-lab-specialties", FieldsDialog
        )
        app.screen.query_one("#fld-item", Input).value = "Changed"
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    assert storage.load_saga("test_saga").laboratories[0].specialties == ["Ignem"]

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
        assert "Aura: 3 (covenant) +0 (modifier) = 3" in view._identity_text()

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
            assert expected in view._identity_text()

    assert storage.load_saga("test_saga").laboratories[0].aura_modifier == -1


async def test_lab_characteristics_numbers_are_coloured_by_sign():
    saga = _saga_with_bare_laboratory()
    saga.laboratories[0].characteristics = LabCharacteristics(
        size=1, refinement=2, safety=-3
    )
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await _select_laboratory(pilot, app)
        view = app.screen._laboratory_sheet_view

        table = view._characteristics_table_text()
        assert re.search(r"Size:\s+\[green\]\+1\[/\]", table)  # positive
        assert re.search(r"Safety:\s+\[red\]-3\[/\]", table)  # negative
        assert re.search(r"Upkeep:\s+\[cyan\]\+0\[/\]", table)  # zero

        derived = view._characteristics_derived_text()
        assert "Occupied Size: [red]-2[/]" in derived
        assert re.search(r"Free Virtues:\s+\[green\]3\[/\]", derived)
        assert re.search(r"Base Safety:\s+\[green\]2\[/\]", derived)


async def test_lab_edit_dialogs_fit_a_small_terminal():
    """Save/Cancel must be on-screen at 80x24 for the roomier lab dialogs."""
    storage.save_saga(_saga_with_populated_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _select_laboratory(pilot, app)

        def assert_buttons_on_screen(*ids: str) -> None:
            for button_id in ids:
                region = app.screen.query_one(button_id, Button).region
                assert region.height > 0, button_id
                assert region.bottom <= 24, (type(app.screen).__name__, button_id)

        await _open_lab_section(pilot, app, "section-lab-identity")
        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Laboratory Identity")
        assert_buttons_on_screen("#btn-save", "#btn-cancel")
        await pilot.press("escape")
        await pilot.pause()

        await _pick_first_and_open_editor(pilot, app, "tab-lab-diary", FieldsDialog)
        assert_buttons_on_screen("#btn-save", "#btn-cancel")


# -- Covenant sheet + saga time ------------------------------------------------

_COVENANT_TABS = (
    "tab-cov-attributes",
    "tab-cov-inhabitants",
    "tab-cov-possessions",
    "tab-cov-economics",
    "tab-cov-library",
    "tab-cov-diary",
)


def _saga_with_configured_covenant() -> Saga:
    saga = _saga_with_bare_laboratory()
    saga.name = "Pushing the Bounds"
    saga.storyguide = "Hedda"
    saga.current_season = "Spring"
    saga.current_year = 1220
    cov = saga.covenants[0]
    cov.tribunal = "Rhine"
    cov.year_founded = 1100
    cov.aegis_of_the_hearth = 2
    cov.aegis_penetration = 1
    cov.living_conditions_magi = 3
    cov.living_conditions_mundane = -1
    cov.aura = 4
    cov.covenant_season = "Summer"
    return saga


async def test_covenant_sheet_has_info_panel_and_six_tabs():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        assert view is not None

        tabs = view.query_one(TabbedContent)
        assert [pane.id for pane in tabs.query(TabPane)] == list(_COVENANT_TABS)
        assert tabs.active == "tab-cov-attributes"

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
        assert re.search(r"Living Conditions \(Magi\):\s+3", left)
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

        # Still available after switching to a tab with nothing to focus (Diary
        # is still a placeholder).
        view = app.screen._covenant_sheet_view
        view.query_one(TabbedContent).active = "tab-cov-diary"
        await pilot.pause()
        assert app.screen._active_section() == "section-cov-info"
        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Covenant")
        await pilot.press("escape")
        await pilot.pause()

        # And via the button.
        view.query_one("#btn-cov-edit", Button).press()
        await pilot.pause()
        assert _is_form(app.screen, "Edit Covenant")


async def test_edit_covenant_saves_fields_and_labs_inherit_the_aura():
    storage.save_saga(_saga_with_bare_laboratory())

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
        set_input("tribunal", "Rhine")
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
        text = app.screen._laboratory_sheet_view._identity_text()
        assert "Aura: 3 (covenant) +0 (modifier) = 3" in text

    cov = storage.load_saga("test_saga").covenants[0]
    assert (cov.name, cov.tribunal, cov.year_founded) == ("Dammerstein", "Rhine", 1100)
    assert (cov.aegis_of_the_hearth, cov.aegis_penetration) == (2, 1)
    assert (cov.living_conditions_magi, cov.living_conditions_mundane) == (1, -2)
    assert (cov.aura, cov.covenant_season) == (3, "Autumn")


async def test_edit_covenant_requires_name_and_allows_blank_year_founded():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await pilot.press("e")
        await pilot.pause()
        dialog = app.screen

        dialog.query_one("#fld-name", Input).value = "  "
        dialog.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert _is_form(app.screen, "Edit Covenant")  # refused

        dialog.query_one("#fld-name", Input).value = "Kept"
        dialog.query_one("#fld-year_founded", Input).value = ""
        dialog.query_one("#btn-save", Button).press()
        await pilot.pause()

    cov = storage.load_saga("test_saga").covenants[0]
    assert cov.name == "Kept"
    assert cov.year_founded is None


async def test_edit_covenant_dialog_fits_a_small_terminal():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _select_covenant(pilot, app)
        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Covenant")
        for button_id in ("#btn-save", "#btn-cancel"):
            region = app.screen.query_one(button_id, Button).region
            assert region.height > 0, button_id
            assert region.bottom <= 24, button_id


async def test_advance_season_moves_the_whole_saga_forward():
    storage.save_saga(_saga_with_configured_covenant())

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
    saga = _saga_with_configured_covenant()
    saga.current_season = "Winter"
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
        await pilot.press("n")
        await pilot.pause()
        assert "Spring 1221" in app.screen.sub_title

    saga = storage.load_saga("test_saga")
    assert (saga.current_season, saga.current_year) == ("Spring", 1221)


async def test_lab_diary_entries_default_to_the_saga_current_season():
    saga = _saga_with_configured_covenant()
    saga.current_season = "Autumn"
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_laboratory(pilot, app)
        await _open_lab_section(pilot, app, "tab-lab-diary")
        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        assert app.screen.query_one("#fld-season", Select).value == "Autumn"
        assert app.screen.query_one("#fld-year", Input).value == "1220"


async def test_set_date_rolls_back_an_accidental_advance():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)

        # Advance by "mistake"...
        await pilot.press("t")
        await pilot.pause()
        app.screen.query_one("#btn-advance", Button).press()
        await pilot.pause()
        assert "Summer 1220" in app.screen.sub_title

        # ...then put it back with Set Date.
        await pilot.press("T")
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
        right = app.screen._covenant_sheet_view._info_right_text()
        assert "Spring" in right

    saga = storage.load_saga("test_saga")
    assert (saga.current_season, saga.current_year) == ("Spring", 1220)


async def test_set_date_sets_an_arbitrary_date_from_the_saga_level():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _open_workspace(pilot)  # saga level
        await pilot.press("T")
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


async def test_set_date_rejects_a_blank_year_and_cancel_changes_nothing():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _open_workspace(pilot)

        await pilot.press("T")
        await pilot.pause()
        app.screen.query_one("#fld-year", Input).value = ""
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert _is_form(app.screen, "Set the Saga's Date")  # refused, still open
        for button_id in ("#btn-save", "#btn-cancel"):
            region = app.screen.query_one(button_id, Button).region
            assert region.height > 0 and region.bottom <= 24, button_id

        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)
        assert "Spring 1220" in app.screen.sub_title

    saga = storage.load_saga("test_saga")
    assert (saga.current_season, saga.current_year) == ("Spring", 1220)


# -- Characters and labs without a covenant live under the saga ---------------


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
        assert "Covenant: (none)" in app.screen._laboratory_sheet_view._identity_text()

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

        await pilot.press("l")
        await pilot.pause()
        assert _is_form(app.screen, "Create a New Laboratory")
        assert app.screen.query_one("#fld-covenant_id", Select).value == Select.NULL
        app.screen.query_one("#fld-name", Input).value = "Loose Lab"
        await pilot.click("#btn-save")
        await pilot.pause()
        assert app.screen.selected_laboratory.name == "Loose Lab"

        # With a covenant selected, the dialog defaults to it.
        await _select(pilot, app, ("covenant", "cov2"))
        await pilot.press("l")
        await pilot.pause()
        assert app.screen.query_one("#fld-covenant_id", Select).value == "cov2"
        app.screen.query_one("#fld-name", Input).value = "Fenghold Lab"
        await pilot.click("#btn-save")
        await pilot.pause()

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
        assert "Aura: 3 (covenant)" in view._identity_text()

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
        text = view._identity_text()
        assert "Covenant: Fenghold" in text
        assert "Aura: 0 (covenant)" in text  # inherits the new covenant's aura

        await set_covenant(Select.NULL)
        tree = app.screen.query_one("#nav-tree", Tree)
        assert _parent_data(tree, ("laboratory", "lab1")) == ("laboratory_group", None)
        assert "Covenant: (none)" in view._identity_text()
        assert app.screen.selected_covenant is None

    assert storage.load_saga("test_saga").laboratories[0].covenant_id is None


async def test_aura_boons_raise_the_aura_labs_inherit_and_the_covenant_panel_shows_it():
    saga = _saga_with_configured_covenant()  # covenant aura 4
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_aura"),
        VirtueFlawInstance(vf_id="covbh_boon_minor_aura"),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        left = app.screen._covenant_sheet_view._info_left_text()
        assert "6 (base 4, +2 Boons)" in left

        # The covenant's lab inherits the raised value, not just the base.
        await _select(pilot, app, ("laboratory", "lab1"))
        text = app.screen._laboratory_sheet_view._identity_text()
        assert "Aura: 6 (covenant) +0 (modifier) = 6" in text


async def test_a_boon_hook_refresh_rebuilds_economics_once(monkeypatch):
    # B12: refreshing Boons/Hooks rebuilt the Economics tab twice (once for
    # the info panel's refresh it triggered, once for itself).
    saga = _saga_with_configured_covenant()  # covenant aura 4
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        rebuilds = []
        original = view._rebuild_economics
        monkeypatch.setattr(
            view, "_rebuild_economics", lambda: rebuilds.append(1) or original()
        )
        view.covenant.boons_hooks.append(
            VirtueFlawInstance(vf_id="covbh_boon_minor_aura")
        )
        view.refresh_section("section-cov-boons")
        await pilot.pause()
        assert len(rebuilds) == 1
        assert "5 (base 4, +1 Boons)" in str(
            view.query_one("#cov-info-left", Static).render()
        )


# -- Covenant Attributes tab: Description, Reputations, Boons & Hooks ---------


async def _open_cov_section(pilot, app, section_id: str) -> None:
    """Focus one of the covenant Attributes tab's sections, after letting the
    view's own initial focus settle (see _open_lab_section)."""
    view = app.screen._covenant_sheet_view
    assert view is not None, "no covenant sheet is currently shown"
    await wait_until(pilot, lambda: view.initial_tab_seen)
    await pilot.pause()
    view.query_one(TabbedContent).active = "tab-cov-attributes"
    await pilot.pause()
    view.query_one(f"#{section_id}", Collapsible).query_one("CollapsibleTitle").focus()
    await pilot.pause()
    await wait_until(pilot, lambda: app.screen._active_section() == section_id)


async def _choose_in_list(pilot, app, list_id: str, item_id: str) -> None:
    """Highlight and activate one entry of a picker list by item id (it may
    be off-screen, so no pixel clicking)."""
    list_view = app.screen.query_one(f"#{list_id}", ListView)
    for index, item in enumerate(list_view.children):
        if item.id == item_id:
            list_view.index = index
            break
    else:
        raise AssertionError(f"{item_id!r} not found in {list_id!r}")
    await pilot.pause()
    await pilot.press("enter")
    await pilot.pause()


def _plain_title(section) -> str:
    """A Collapsible's title as displayed (colour markup stripped)."""
    return section.query_one("CollapsibleTitle").label.plain


def _title_styles(section) -> list[str]:
    """The styles actually applied to a Collapsible's rendered title."""
    return [
        str(span.style) for span in section.query_one("CollapsibleTitle").render().spans
    ]


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


def _pick_id(catalog_id: str) -> str:
    return f"covbhpick-{catalog_id}"


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
    await pilot.pause()
    assert isinstance(app.screen, CovenantBoonHookPickerScreen)
    await _choose_in_list(pilot, app, "covbh-picker-list", _pick_id(catalog_id))
    assert isinstance(app.screen, FieldsDialog)
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


async def test_covenant_attributes_tab_has_its_four_sections():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        ids = [
            "section-cov-description",
            "section-cov-reputations",
            "section-cov-boons",
            "section-cov-hooks",
        ]
        sections = [view.query_one(f"#{i}", Collapsible) for i in ids]
        assert all(not section.collapsed for section in sections)
        assert _plain_title(sections[2]) == "Boons (0 pts)"
        assert _plain_title(sections[3]) == "Hooks (0 pts)"

        # Boons and Hooks sit side by side, like the reference sheet.
        boons, hooks = sections[2].region, sections[3].region
        assert boons.right <= hooks.x
        assert boons.y == hooks.y


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


async def test_covenant_reputations_add_edit_remove_within_range():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        assert _rep_labels(view) == []
        await _open_cov_section(pilot, app, "section-cov-reputations")

        async def submit(name: str, score: str) -> None:
            app.screen.query_one("#fld-name", Input).value = name
            app.screen.query_one("#fld-score", Input).value = score
            app.screen.query_one("#btn-save", Button).press()
            await pilot.pause()

        # Add -- out-of-range scores are refused, the dialog stays open.
        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        await submit("Feared by nobles", "4")
        assert isinstance(app.screen, FieldsDialog)
        await submit("Feared by nobles", "-4")
        assert isinstance(app.screen, FieldsDialog)
        await submit("Feared by nobles", "3")
        assert isinstance(app.screen, WorkspaceScreen)
        await pilot.press("a")
        await pilot.pause()
        await submit("Well liked", "-3")
        await wait_until(pilot, lambda: len(_rep_labels(view)) == 2)
        assert _rep_labels(view) == ["Feared by nobles: +3", "Well liked: -3"]

        # Edit the first one (pre-filled), then remove the second.
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert app.screen.query_one("#fld-name", Input).value == ("Feared by nobles")
        await submit("Feared by nobles", "1")
        await wait_until(pilot, lambda: "Feared by nobles: +1" in _rep_labels(view))

        # Nothing is selected, so 'A' asks which one, then confirms.
        await pilot.press("A")
        await pilot.pause()
        await pilot.press("down")
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await wait_until(pilot, lambda: len(_rep_labels(view)) == 1)
        assert _rep_labels(view) == ["Feared by nobles: +1"]

    reputations = storage.load_saga("test_saga").covenants[0].reputations
    assert [(r.name, r.score) for r in reputations] == [("Feared by nobles", 1)]


async def test_boon_picker_lists_only_boons_with_notes_and_asks_for_a_blank_detail():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _open_cov_section(pilot, app, "section-cov-boons")
        await pilot.press("a")
        await pilot.pause()
        picker = app.screen
        assert isinstance(picker, CovenantBoonHookPickerScreen)

        items = list(picker.query_one("#covbh-picker-list", ListView).children)
        assert len(items) == _catalog_count("Boon")  # every Boon, no Hooks
        assert all("covbh_boon_" in (item.id or "") for item in items)

        labels = {item.id: str(item.query_one(Label).render()) for item in items}
        shell = labels[_pick_id("covbh_boon_minor_shell_keep")]
        assert "requires: Castle" in shell
        assert "not with: Road, Urban" in labels[_pick_id("covbh_boon_minor_seclusion")]

        # Choosing one opens the detail prompt, blank by default.
        await _choose_in_list(
            pilot, app, "covbh-picker-list", _pick_id("covbh_boon_minor_edifice")
        )
        assert isinstance(app.screen, FieldsDialog)
        assert app.screen.query_one("#fld-detail", Input).value == ""

        # Cancelling the detail prompt goes back to the picker; nothing added.
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, CovenantBoonHookPickerScreen)
        await pilot.press("escape")
        await pilot.pause()

    assert storage.load_saga("test_saga").covenants[0].boons_hooks == []


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
        await _open_cov_section(pilot, app, "section-cov-boons")
        await pilot.press("a")
        await pilot.pause()
        items = {
            item.id: str(item.query_one(Label).render())
            for item in app.screen.query_one("#covbh-picker-list", ListView).children
        }
        assert len(items) == _catalog_count("Boon")  # nothing is hidden
        assert "(taken x2)" in items[_pick_id("covbh_boon_minor_edifice")]
        assert "(taken x1)" in items[_pick_id("covbh_boon_minor_wealth")]
        assert "taken" not in items[_pick_id("covbh_boon_minor_regio")]

        # A second Edifice can be taken (your sheet has two).
        await _choose_in_list(
            pilot, app, "covbh-picker-list", _pick_id("covbh_boon_minor_edifice")
        )
        app.screen.query_one("#fld-detail", Input).value = "C"
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()

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
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("down")
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        assert app.screen.query_one("#fld-detail", Input).value == "B"  # prefilled
        app.screen.query_one("#fld-detail", Input).value = ""  # clear it
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert "Wealth" in _bh_labels(view, "Boon")
        assert "Wealth -" not in _bh_labels(view, "Boon")  # no detail any more
        assert "Edifice - A" in _bh_labels(view, "Boon")  # the other Boon untouched

        # Remove the SECOND Hook (Road), index 2 -- through the picker (nothing
        # is selected), then the delete confirmation.
        await _open_cov_section(pilot, app, "section-cov-hooks")
        await pilot.press("A")
        await pilot.pause()
        await pilot.press("down")
        await pilot.press("enter")
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


async def test_switching_back_to_the_attributes_tab_focuses_its_first_section():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        await wait_until(pilot, lambda: view.initial_tab_seen)
        await pilot.pause()

        tabbed = view.query_one(TabbedContent)
        tabbed.active = "tab-cov-diary"  # a flat tab (still a placeholder)
        await pilot.pause()
        assert app.screen._active_section() == "section-cov-info"  # fallback

        tabbed.active = "tab-cov-attributes"
        await wait_until(
            pilot, lambda: app.screen._active_section() == "section-cov-description"
        )
        assert app.screen._active_section() == "section-cov-description"


async def test_covenant_attributes_dialogs_fit_a_small_terminal():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _select_covenant(pilot, app)

        def buttons_on_screen() -> None:
            for button in app.screen.query(Button):
                region = button.region
                assert region.height > 0 and region.bottom <= 24, (
                    type(app.screen).__name__,
                    button.id,
                )

        await _open_cov_section(pilot, app, "section-cov-description")
        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Covenant Description")
        buttons_on_screen()
        await pilot.press("escape")
        await pilot.pause()

        await _open_cov_section(pilot, app, "section-cov-boons")
        await pilot.press("a")
        await pilot.pause()
        await _choose_in_list(
            pilot, app, "covbh-picker-list", _pick_id("covbh_boon_minor_wealth")
        )
        assert isinstance(app.screen, FieldsDialog)
        buttons_on_screen()


# -- Boons/Hooks: colour-coded totals, selector rows and the details panel -----


def _saga_with_boons_and_hooks(*ids: str) -> Saga:
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [VirtueFlawInstance(vf_id=i) for i in ids]
    return saga


async def test_boon_and_hook_totals_are_coloured_by_how_they_compare():
    # (attached entries, expected colour, expected plain titles)
    cases = [
        ((), "green", ("Boons (0 pts)", "Hooks (0 pts)")),  # equal
        (
            ("covbh_boon_minor_wealth", "covbh_hook_major_castle"),
            "cyan",  # Boons (1) < Hooks (3)
            ("Boons (1 pt)", "Hooks (3 pts)"),
        ),
        (
            ("covbh_boon_major_wealth", "covbh_hook_minor_rival"),
            "red",  # Boons (3) > Hooks (1)
            ("Boons (3 pts)", "Hooks (1 pt)"),
        ),
        (
            ("covbh_boon_major_wealth", "covbh_hook_major_castle"),
            "green",  # equal, non-zero
            ("Boons (3 pts)", "Hooks (3 pts)"),
        ),
    ]
    for attached, colour, plain in cases:
        storage.save_saga(_saga_with_boons_and_hooks(*attached))
        app = ArsMagicaManagerApp()
        async with app.run_test(size=(140, 50)) as pilot:
            await _select_covenant(pilot, app)
            view = app.screen._covenant_sheet_view
            boons = view.query_one("#section-cov-boons", Collapsible)
            hooks = view.query_one("#section-cov-hooks", Collapsible)
            # Both share the colour, and only the parenthesised total has it.
            assert boons.title == f"Boons [{colour}]{plain[0][6:]}[/]", attached
            assert hooks.title == f"Hooks [{colour}]{plain[1][6:]}[/]", attached
            assert (_plain_title(boons), _plain_title(hooks)) == plain


async def test_totals_recolour_when_a_hook_is_added():
    storage.save_saga(_saga_with_boons_and_hooks("covbh_boon_minor_wealth"))

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        boons = view.query_one("#section-cov-boons", Collapsible)
        hooks = view.query_one("#section-cov-hooks", Collapsible)
        assert "[red]" in boons.title and "[red]" in hooks.title  # 1 > 0

        await _add_boon_hook_via_picker(
            pilot, app, "section-cov-hooks", "covbh_hook_minor_rival"
        )
        assert "[green]" in boons.title and "[green]" in hooks.title  # 1 == 1

        await _add_boon_hook_via_picker(
            pilot, app, "section-cov-hooks", "covbh_hook_minor_favors"
        )
        # Adding a Hook re-coloured the Boons title too (1 < 2).
        assert "[cyan]" in boons.title and "[cyan]" in hooks.title
        # ...and what is actually painted follows, including the Hooks total
        # whose text ("(2 pts)") changed but which must also recolour when only
        # the colour changes (Textual compares label text, not style).
        assert "cyan" in _title_styles(boons) and "cyan" in _title_styles(hooks)


async def test_a_colour_only_change_repaints_the_title():
    # Hooks stay at 3 points throughout; only the Boons change, so the Hooks
    # title text is identical while its colour must change.
    storage.save_saga(_saga_with_boons_and_hooks("covbh_hook_major_castle"))

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        hooks = view.query_one("#section-cov-hooks", Collapsible)
        assert "green" not in _title_styles(hooks)
        assert "cyan" in _title_styles(hooks)  # Boons 0 < Hooks 3

        for boon in ("covbh_boon_major_wealth", "covbh_boon_minor_aura"):
            await _add_boon_hook_via_picker(pilot, app, "section-cov-boons", boon)
            plain = _plain_title(hooks)
            assert plain == "Hooks (3 pts)"  # text never changed
        # Boons (4) > Hooks (3): red, though the Hooks text stayed identical.
        assert "red" in _title_styles(hooks)
        assert "cyan" not in _title_styles(hooks)


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


async def test_details_panel_shows_prerequisites_exclusions_and_repeatability():
    storage.save_saga(
        _saga_with_boons_and_hooks(
            "covbh_boon_minor_shell_keep",
            "covbh_boon_minor_seclusion",
            "covbh_boon_minor_aura",
            "covbh_boon_minor_wealth",
            "covbh_boon_minor_edifice",
        )
    )

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view

        def info(index: int) -> str:
            # entry index -> text with the colour/bold markup stripped
            return strip_markup(view._bh_info_text(index))

        assert "Requires: Castle" in info(0)
        assert "Not with: Road, Urban" in info(1)
        assert "May be taken more than once; the effects stack." in info(2)
        assert "Effect: The covenant's Magic aura +1" in info(2)
        assert "Requires" not in info(3) and "Not with" not in info(3)
        assert "May be taken" not in info(3) and "Effect:" not in info(3)
        # A building Boon: its Buildings surcharge, and it may be repeated.
        assert "Effect: Yearly expenditure: Buildings +2" in info(4)
        assert "May be taken more than once" in info(4)


async def test_details_panel_shows_the_detail_and_escapes_markup():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(
            vf_id="covbh_boon_minor_edifice", params={"detail": "The [Tower] of Iris"}
        )
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        view.query_one("#cov-boons-list", OptionList).highlighted = 0
        await pilot.pause()
        text = str(view.query_one("#cov-bh-info", Static).render())
        assert "Name: Edifice - The [Tower] of Iris" in text  # brackets survive


async def test_empty_boon_and_hook_lists_show_a_disabled_placeholder():
    storage.save_saga(_saga_with_boons_and_hooks())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        for list_id in ("cov-boons-list", "cov-hooks-list"):
            option_list = view.query_one(f"#{list_id}", OptionList)
            assert len(option_list.options) == 1
            assert option_list.options[0].disabled
            assert "none recorded" in str(option_list.options[0].prompt)


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
        await pilot.pause()
        assert isinstance(app.screen, CovenantBoonHookPickerScreen)
        assert app.screen.kind == "Boon"


async def test_adding_a_boon_rebuilds_the_list_and_resets_the_panel():
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
        assert all("○" in str(o.prompt) for o in boon_list.options)  # no stale marker
        assert "Select a Boon or Hook" in str(
            view.query_one("#cov-bh-info", Static).render()
        )


# -- Boon/Hook Description, and e / A acting on the selected row ---------------


async def _select_bh_row(pilot, app, kind: str, list_index: int) -> None:
    """Select a row of the Boons/Hooks list the way a user does: focus the
    list and highlight the row."""
    view = app.screen._covenant_sheet_view
    await wait_until(pilot, lambda: view.initial_tab_seen)
    await pilot.pause()
    view.query_one("#section-cov-" + kind.lower() + "s")  # exists
    option_list = view.query_one(f"#cov-{kind.lower()}s-list", OptionList)
    option_list.focus()
    await pilot.pause()
    option_list.highlighted = list_index
    await pilot.pause()


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


async def test_A_deletes_the_selected_item_only_after_confirmation():
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
        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert message == "Delete Edifice - B [x]?"  # brackets survive
        await pilot.press("n")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)
        assert len(view._bh_entries("Boon")) == 3

        await pilot.press("A")
        await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()
        assert len(view._bh_entries("Boon")) == 3

        # Yes deletes exactly the selected one, then the panel resets.
        await pilot.press("A")
        await pilot.pause()
        await pilot.press("y")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)
        assert [label for _, label in view._bh_entries("Boon")] == [
            "Edifice - A",
            "Wealth",
        ]
        assert "Select a Boon or Hook" in _panel_text(app)
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
        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        assert app.screen.focused is app.screen.query_one("#btn-no", Button)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    assert len(storage.load_saga("test_saga").covenants[0].boons_hooks) == 1


async def test_selection_in_the_other_list_or_none_falls_back_to_the_picker():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_wealth"),
        VirtueFlawInstance(vf_id="covbh_hook_minor_rival"),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)

        # A Boon is selected, but 'A' in the Hooks section isn't about it:
        # the picker asks which Hook, then confirms.
        await _select_bh_row(pilot, app, "Boon", 0)
        await _open_cov_section(pilot, app, "section-cov-hooks")
        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")
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
    async with app.run_test(size=(80, 24)) as pilot:
        await _select_covenant(pilot, app)
        await _select_bh_row(pilot, app, "Boon", 0)
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        for button in app.screen.query(Button):
            region = button.region
            assert region.height > 0 and region.bottom <= 24, button.id
        await pilot.press("escape")
        await pilot.pause()

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        for button in app.screen.query(Button):
            region = button.region
            assert region.height > 0 and region.bottom <= 24, button.id


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

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        assert app.screen.query_one("#confirm-dialog").region.height < 12


# -- Covenant Reputations on the selectable-list pattern ----------------------


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


async def test_e_edits_the_selected_reputation_directly():
    storage.save_saga(_saga_with_reputations(("Feared", 2), ("Liked", -1)))

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        await _select_rep_row(pilot, app, 1)

        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)  # no picker first
        assert app.screen.query_one("#fld-name", Input).value == "Liked"
        assert app.screen.query_one("#fld-score", Input).value == "-1"
        app.screen.query_one("#fld-name", Input).value = "Well liked"
        app.screen.query_one("#fld-score", Input).value = "3"
        app.screen.query_one("#btn-save", Button).press()
        await wait_until(pilot, lambda: "Well liked: +3" in _rep_labels(view))

    reputations = storage.load_saga("test_saga").covenants[0].reputations
    assert [(r.name, r.score) for r in reputations] == [
        ("Feared", 2),
        ("Well liked", 3),
    ]


async def test_A_deletes_the_selected_reputation_only_after_confirmation():
    storage.save_saga(
        _saga_with_reputations(("Feared", 2), ("Odd [name]", -1), ("Known", 0))
    )

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        await _select_rep_row(pilot, app, 1)

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert message == "Delete Odd [name]?"  # brackets survive
        await pilot.press("n")
        await pilot.pause()
        assert len(_rep_labels(view)) == 3

        await pilot.press("A")
        await pilot.pause()
        await pilot.press("y")
        await wait_until(pilot, lambda: len(_rep_labels(view)) == 2)
        assert _rep_labels(view) == ["Feared: +2", "Known: +0"]
        assert view.selected_reputation() is None  # selection reset

    names = [r.name for r in storage.load_saga("test_saga").covenants[0].reputations]
    assert names == ["Feared", "Known"]


async def test_reputation_keys_work_from_the_list_and_fall_back_to_a_picker():
    storage.save_saga(_saga_with_reputations(("Feared", 2)))

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view
        await wait_until(pilot, lambda: view.initial_tab_seen)
        await pilot.pause()

        # List focused, nothing chosen: the section still owns the keys.
        view.query_one("#cov-reputations-list", SelectableList).focus()
        await pilot.pause()
        assert app.screen._active_section() == "section-cov-reputations"
        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        assert [f.label for f in app.screen.fields][1] == "Score (-3 to +3)"
        await pilot.press("escape")
        await pilot.pause()

        # Nothing chosen: 'e' falls back to "which one?".
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)


# -- SelectableList, the reusable widget ------------------------------------


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

        assert widget.highlighted is None and widget.selected_data_index is None
        assert all("○" in p for p in prompts())

        widget.highlighted = 1
        await pilot.pause()
        assert app.chosen == [7]  # the data index, not the row position
        assert widget.selected_data_index == 7
        assert "●" in prompts()[1] and "●" not in prompts()[0] + prompts()[2]

        widget.highlighted = 2
        await pilot.pause()
        assert app.chosen == [7, 9]
        assert sum("●" in p for p in prompts()) == 1  # one marker at a time

        widget.clear_selection()
        await pilot.pause()
        assert widget.selected_data_index is None
        assert not any("●" in p for p in prompts())
        assert app.chosen == [7, 9]  # clearing posts nothing


async def test_selectable_list_set_rows_replaces_everything_and_handles_empty():
    app = _ListHarness([(0, "one"), (1, "two")])
    async with app.run_test() as pilot:
        widget = app.query_one("#the-list", SelectableList)
        widget.highlighted = 1
        await pilot.pause()
        assert widget.selected_data_index == 1

        widget.set_rows([(5, "five")])
        await pilot.pause()
        assert len(widget.options) == 1
        assert widget.selected_data_index is None  # selection cleared
        assert "○" in str(widget.options[0].prompt)  # no stale marker

        # Empty: one disabled placeholder that can't be chosen.
        widget.set_rows([])
        await pilot.pause()
        assert len(widget.options) == 1
        assert widget.options[0].disabled
        assert "none recorded" in str(widget.options[0].prompt)
        assert widget.selected_data_index is None
        assert app.chosen == [1]  # only the one real choice was ever posted


# -- Inline emphasis in user-written descriptions ----------------------------


def _styled_words(static) -> set[tuple[str, str]]:
    """(text, style) for every styled span of a rendered Static."""
    content = static.render()
    return {(content.plain[s.start : s.end], str(s.style)) for s in content.spans}


async def test_boon_hook_description_renders_bold_and_italic_in_the_panel():
    saga = _saga_with_configured_covenant()
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(
            vf_id="covbh_boon_minor_hidden_resources",
            params={
                "description": (
                    "**Accessible Value:** 250 Build Points\n\n"
                    "**Location:** sealed *behind* a wall in [The Tower]"
                )
            },
        )
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _select_bh_row(pilot, app, "Boon", 0)
        panel = app.screen._covenant_sheet_view.query_one("#cov-bh-info", Static)

        plain = str(panel.render())
        assert "**" not in plain and "*behind*" not in plain  # markers consumed
        assert "Accessible Value: 250 Build Points" in plain
        assert "[The Tower]" in plain  # brackets still literal

        styled = _styled_words(panel)
        assert ("Accessible Value:", "b") in styled
        assert ("Location:", "b") in styled
        assert ("behind", "i") in styled
        # The official rules text is NOT interpreted as Markdown.
        assert not any(
            style == "i" and "Build Points" in text for text, style in styled
        )


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
    async with app.run_test(size=(80, 24)) as pilot:
        await _select_covenant(pilot, app)
        await _select_bh_row(pilot, app, "Boon", 0)
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        assert "**bold**" in str(app.screen.query_one(".fd-hint", Static).render())
        # Still fits a small terminal with the extra hint line.
        for button in app.screen.query(Button):
            assert button.region.height > 0 and button.region.bottom <= 24, button.id
        await pilot.press("escape")
        await pilot.pause()

        await _open_cov_section(pilot, app, "section-cov-description")
        await pilot.press("e")
        await pilot.pause()
        assert _is_form(app.screen, "Edit Covenant Description")
        assert "*italic*" in str(app.screen.query_one(".fd-hint", Static).render())
        for button in app.screen.query(Button):
            assert button.region.height > 0 and button.region.bottom <= 24, button.id


# -- The expanded catalog: types (categories) in the picker and the panel -------


async def test_picker_lists_boons_in_the_books_type_order_with_the_type_shown():
    storage.save_saga(_saga_with_configured_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _open_cov_section(pilot, app, "section-cov-boons")
        await pilot.press("a")
        await pilot.pause()
        items = list(app.screen.query_one("#covbh-picker-list", ListView).children)
        labels = [str(item.query_one(Label).render()) for item in items]

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
        picker_list = app.screen.query_one("#covbh-picker-list", ListView)

        def shown() -> list[str]:
            # Mid-refill, a row can be mounted before its Label: skip it.
            return [
                str(labels.first().render())
                for item in picker_list.children
                if (labels := item.query(Label))
            ]

        await _wait_for_picker_ready(pilot, app)

        app.screen.query_one("#picker-search", Input).value = "surroundings"
        # The list refills row by row: wait for the finished result.
        await wait_until(
            pilot,
            lambda: (
                all("[Surroundings," in x for x in shown())
                and any(x.startswith("Pilgrimage Site") for x in shown())
            ),
            timeout=10.0,  # a row-by-row refill is slow under a parallel run
        )
        labels = shown()
        assert labels and all("[Surroundings," in label for label in labels)
        assert any(label.startswith("Pilgrimage Site") for label in labels)


async def test_details_panel_shows_the_type_and_omits_it_for_untyped_entries():
    storage.save_saga(
        _saga_with_boons_and_hooks(
            "covbh_boon_free_manor_house",
            "covbh_hook_major_unknown",
            "covbh_hook_minor_weak_aura",
        )
    )

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        view = app.screen._covenant_sheet_view

        def plain(index: int) -> str:
            return strip_markup(view._bh_info_text(index))

        assert "Type: Fortifications" in plain(0)
        assert "Tier: Free Boon" in plain(0)  # no cost line for a Free Choice
        assert "pt)" not in plain(0).split("Rules:")[0]
        assert "Type:" not in plain(1)  # Unknown isn't filed under a type
        assert "Tier: Major Hook (3 pts)" in plain(1)
        assert "Type: Site" in plain(2)


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
        text = app.screen._laboratory_sheet_view._identity_text()
        assert "Aura: 3 (covenant) +0 (modifier) = 3" in text


# -- Covenant Inhabitants tab ---------------------------------------------------


def _saga_with_people() -> Saga:
    """Covenant cov1 with a listed magus and companion and three grogs (two
    unassigned + one in another covenant), so both sources of inhabitants exist."""
    saga = _saga_with_bare_character()
    saga.characters = [
        Character(
            id="mag1",
            name="Corvinus",
            type="magus",
            covenant_id="cov1",
            background=Background(year_born=1195),
            hermetic=HermeticBackground(house="house_bonisagus"),
        ),
        Character(id="comp1", name="Alys", type="companion", covenant_id="cov1"),
        Character(
            id="grog1",
            name="Old Thomae",
            type="grog",
            covenant_id="cov1",
            background=Background(year_born=1193),
            abilities=[Ability(name="Athletics"), Ability(name="Brawl")],
        ),
        Character(id="grog2", name="Dieter", type="grog", covenant_id="cov1"),
        Character(id="grog3", name="Not Ours", type="grog", covenant_id=None),
    ]
    return saga


async def _show_inhabitants_tab(pilot, app) -> None:
    view = app.screen._covenant_sheet_view
    await wait_until(pilot, lambda: view.initial_tab_seen)
    await pilot.pause()
    view.query_one(TabbedContent).active = "tab-cov-inhabitants"
    await pilot.pause()


async def _open_inh_section(pilot, app, section_id: str) -> None:
    """Focus a section of the Inhabitants tab (so its a/A/e keys apply)."""
    await _show_inhabitants_tab(pilot, app)
    view = app.screen._covenant_sheet_view
    view.query_one(f"#{section_id}", Collapsible).query_one("CollapsibleTitle").focus()
    await pilot.pause()
    await wait_until(pilot, lambda: app.screen._active_section() == section_id)


async def _select_inh_row(pilot, app, kind: str, row: int) -> None:
    await _show_inhabitants_tab(pilot, app)
    view = app.screen._covenant_sheet_view
    rows = view.query_one(f"#inh-{kind}-list", SelectableList)
    rows.focus()
    await pilot.pause()
    rows.highlighted = row
    await pilot.pause()


def _fill(app, **values) -> None:
    """Set FieldsDialog fields by key: Input/Select/Checkbox/TextArea alike."""
    for key, value in values.items():
        widget = app.screen.query_one(f"#fld-{key}")
        if isinstance(widget, TextArea):
            widget.text = str(value)
        elif isinstance(widget, Input):
            widget.value = str(value)
        else:  # Select or Checkbox
            widget.value = value


async def _save_dialog(pilot, app) -> None:
    """Press a FieldsDialog's Save, then wait for it to close -- or to show a
    validation error and stay open."""
    dialog = app.screen
    dialog.query_one("#btn-save", Button).press()
    await pilot.pause()
    await wait_until(
        pilot,
        lambda: (
            app.screen is not dialog
            or str(dialog.query_one("#fields-error", Static).render()).strip()
        ),
    )
    await pilot.pause()  # the result callback can land a beat after the switch


def _records(kind: str | None = None) -> list[Inhabitant]:
    cov = storage.load_saga("test_saga").covenants[0]
    return [r for r in cov.inhabitants if kind is None or r.kind == kind]


def _cov_view(app):
    return app.screen._covenant_sheet_view


def _inh_labels(app, kind: str) -> list[str]:
    return [label for _, label in _cov_view(app)._inh_rows(kind)]


def _inh_title(app, kind: str) -> str:
    return _plain_title(_cov_view(app).query_one(f"#section-inh-{kind}", Collapsible))


async def test_inhabitants_tab_has_all_its_sections_with_headcount_titles():
    saga = _saga_with_people()
    cov = saga.covenants[0]
    cov.boons_hooks = [VirtueFlawInstance(vf_id="covbh_boon_free_autocracy")]
    cov.inhabitants = [
        Inhabitant(id="t1", kind="turb", name="Guard", quantity=3),
        Inhabitant(id="i1", kind="inhabitant", name="Marta and Simon", quantity=2),
        Inhabitant(id="i2", kind="inhabitant", name="Jakob"),
    ]
    cov.population.other_people = 4
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _show_inhabitants_tab(pilot, app)
        view = _cov_view(app)

        ids = [
            "section-inh-loyalty",
            "section-inh-population",
            "section-inh-misc",
            *(f"section-inh-{k}" for k in inh.INHABITANT_KINDS),
        ]
        sections = [view.query_one(f"#{i}", Collapsible) for i in ids]
        assert all(not section.collapsed for section in sections)
        assert [_plain_title(x) for x in sections[:3]] == [
            "Loyalty",
            "Inhabitants",
            "Miscellaneous",
        ]
        # Titles carry the headcount: quantities added up, not rows.
        assert [_plain_title(x) for x in sections[3:]] == [
            "Magi (1)",
            "Companions (1)",
            "Specialists (0)",
            "Craftspeople (0)",
            "Turb (3)",
            "Other Covenfolk (3)",
            "Horses (0)",
            "Livestock (0)",
        ]
        text = str(view.query_one("#inh-population-content", Static).render())
        assert re.search(r"Total Inhabitants:\s+12\b", text)  # 4+1+1+3+3
        left = str(view.query_one("#inh-loyalty-left", Static).render())
        assert "Autocracy" in left  # the governance follows the Boon
        assert "Select an inhabitant" in str(
            view.query_one("#inh-panel", Static).render()
        )


async def test_magi_and_companions_are_listed_from_sheets_and_choosing_fills_the_panel():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        assert _inh_labels(app, "magus") == [
            "Corvinus            Bonisagus             1195  The Gift"
        ]
        assert _inh_labels(app, "companion") == [
            "Alys                                                   Unknown"
        ]

        await _select_inh_row(pilot, app, "magus", 0)
        panel = _cov_view(app).query_one("#inh-panel", Static)
        text = str(panel.render())
        assert "House: Bonisagus" in text and "Year Born: 1195 (age 25)" in text
        assert "From the character sheet of Corvinus." in text

        # One selection across all the lists.
        await _select_inh_row(pilot, app, "companion", 0)
        assert _cov_view(app).selected_inhabitant("magus") is None
        assert "Name: Alys" in str(panel.render())


async def test_add_an_npc_magus_with_an_unknown_year():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-magus")
        await pilot.press("a")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)  # straight to the form
        _fill(app, name="Hidden Hermit", house="house_criamon", gift="Blatant")
        assert app.screen.query_one("#fld-year_born", Input).value == ""  # blank
        _fill(app, description="Lives in a *sealed* tower.")
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(_inh_labels(app, "magus")) == 2)

        assert _inh_labels(app, "magus")[1] == (
            "Hidden Hermit       Criamon            Unknown  Blatant Gift"
        )
        assert _inh_title(app, "magus") == "Magi (2)"

    [npc] = _records("magus")
    assert (npc.name, npc.house, npc.year_born, npc.character_id) == (
        "Hidden Hermit",
        "house_criamon",
        None,
        None,
    )


async def test_editing_a_listed_magus_only_changes_covenant_side_fields():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_inh_row(pilot, app, "magus", 0)
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        # Name/house/year come from the sheet: shown, not editable.
        assert not app.screen.query("#fld-name")
        assert not app.screen.query("#fld-house")
        # Gift too: read straight from the sheet's Virtues, not editable here.
        assert not app.screen.query("#fld-gift")
        _fill(app, description="Trusted **completely**.")
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        assert _inh_labels(app, "magus")[0].startswith("Corvinus            Bonisagus")

    [record] = _records("magus")
    assert record.character_id == "mag1" and record.description.startswith("Trusted")
    assert not record.departed


async def test_removing_a_listed_magus_keeps_them_in_the_covenant_but_stops_counting_them():
    saga = _saga_with_people()
    # Already edited once, so a covenant-side record exists to be marked.
    saga.covenants[0].inhabitants = [
        Inhabitant(id="m", kind="magus", character_id="mag1", description="Trusted.")
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_inh_row(pilot, app, "magus", 0)
        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert "Remove Corvinus from the Magi list?" in message
        assert "stay in the covenant on their character sheet" in message
        await pilot.press("n")
        await pilot.pause()
        assert len(_inh_labels(app, "magus")) == 1  # No keeps them

        await pilot.press("A")
        await pilot.pause()
        await pilot.press("y")
        await wait_until(pilot, lambda: not _inh_labels(app, "magus"))
        assert _inh_title(app, "magus") == "Magi (0)"
        text = str(_cov_view(app).query_one("#inh-population-content", Static).render())
        assert re.search(r"Total Inhabitants:\s+1\b", text)  # only Alys now

    saved = storage.load_saga("test_saga")
    assert next(c for c in saved.characters if c.id == "mag1").covenant_id == "cov1"
    [record] = _records("magus")
    assert record.departed
    assert record.description == "Trusted." and record.character_id == "mag1"
    assert inh.entries_for_kind(saved, saved.covenants[0], "magus") == []


async def test_removing_a_listed_companion_with_no_record_creates_one():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_inh_row(pilot, app, "companion", 0)
        await pilot.press("A")
        await pilot.pause()
        await pilot.press("y")
        await wait_until(pilot, lambda: not _inh_labels(app, "companion"))
        assert _inh_title(app, "companion") == "Companions (0)"
        # The magus is untouched.
        assert len(_inh_labels(app, "magus")) == 1

    [record] = _records("companion")
    assert record.departed and record.character_id == "comp1"


async def test_restoring_a_departed_magus_makes_them_count_again():
    saga = _saga_with_people()
    saga.covenants[0].inhabitants = [
        Inhabitant(
            id="m",
            kind="magus",
            character_id="mag1",
            description="Trusted.",
            departed=True,
        )
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        assert _inh_labels(app, "magus") == []  # departed: not listed
        await _open_inh_section(pilot, app, "section-inh-magus")
        await pilot.press("r")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)  # only one entry
        await pilot.press("enter")
        await wait_until(pilot, lambda: len(_inh_labels(app, "magus")) == 1)
        assert _inh_labels(app, "magus")[0].startswith("Corvinus")

    [record] = _records("magus")
    assert not record.departed
    assert record.description == "Trusted."  # covenant-side extras kept


async def test_restore_with_nothing_departed_notifies_and_does_nothing():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-companion")
        await pilot.press("r")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)  # no picker popped


async def test_specialist_from_an_unassigned_grog_prefills_and_marks_it_assigned():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-specialist")

        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        labels = [
            str(item.query_one(Label).render())
            for item in app.screen.query_one("#removal-picker-list", ListView).children
        ]
        # New person first, then only THIS covenant's unassigned grogs.
        assert labels[0].startswith("(New person")
        assert [l.split("  ")[0] for l in labels[1:]] == ["Old Thomae", "Dieter"]

        await pilot.press("down")  # Old Thomae
        await pilot.press("enter")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        assert app.screen.query_one("#fld-name", Input).value == "Old Thomae"
        assert app.screen.query_one("#fld-year_born", Input).value == "1193"
        _fill(app, responsibility="Teaches Latin", role="Teacher")
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(_inh_labels(app, "specialist")) == 1)
        assert _inh_labels(app, "specialist") == [
            "Old Thomae          Teaches Latin     Teacher             1193"
        ]

        # Now assigned, so he's no longer offered.
        await pilot.press("a")
        await pilot.pause()
        labels = [
            str(item.query_one(Label).render())
            for item in app.screen.query_one("#removal-picker-list", ListView).children
        ]
        assert [l.split("  ")[0] for l in labels[1:]] == ["Dieter"]

    [record] = _records("specialist")
    assert (record.character_id, record.role) == ("grog1", "Teacher")


async def test_a_brand_new_grog_type_person_needs_a_name_but_year_born_may_stay_unknown():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-specialist")
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("enter")  # "(New person...)"
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)

        await _save_dialog(pilot, app)
        assert isinstance(app.screen, FieldsDialog)  # refused: no name
        assert "Name is required" in str(app.screen.query_one("#fields-error").render())
        _fill(app, name="Visiting Steward", role="Steward")
        await _save_dialog(pilot, app)  # no year: fine
        await wait_until(pilot, lambda: len(_inh_labels(app, "specialist")) == 1)
        assert _inh_labels(app, "specialist") == [
            "Visiting Steward                      Steward          Unknown"
        ]

    [record] = _records("specialist")
    assert record.character_id is None and record.year_born is None


async def test_a_grog_without_a_year_born_is_assigned_with_it_unknown():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-turb")
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("down", "down")  # Dieter: no year on his sheet
        await pilot.press("enter")
        await pilot.pause()
        assert app.screen.query_one("#fld-name", Input).value == "Dieter"
        assert app.screen.query_one("#fld-year_born", Input).value == ""
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(_inh_labels(app, "turb")) == 1)
        assert _inh_labels(app, "turb")[0].endswith("Unknown")


async def test_other_covenfolk_requires_a_covenant_role_and_suppresses_it_when_redundant():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-inhabitant")
        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)  # a GROG_KINDS section
        await pilot.press("enter")  # "(New person...)"
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)

        _fill(app, name="Old Marta", responsibility="Nursemaid")
        await _save_dialog(pilot, app)
        assert isinstance(app.screen, FieldsDialog)  # refused: no Covenant Role
        assert "Covenant Role is required" in str(
            app.screen.query_one("#fields-error").render()
        )
        options = [
            v
            for _, v in app.screen.query_one("#fld-role", Select)._options
            if isinstance(v, str)
        ]
        assert options == ["Laborer", "Servant", "Teamster", "Dependent"]
        _fill(app, role="Dependent", year_born=1180)
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(_inh_labels(app, "inhabitant")) == 1)
        assert _inh_labels(app, "inhabitant") == [
            "Old Marta           Dependent         1        1180"
        ]

        await _select_inh_row(pilot, app, "inhabitant", 0)
        panel = _cov_view(app).query_one("#inh-panel", Static)
        text = str(panel.render())
        assert "Covenant Role: Dependent" in text
        assert "Responsibility: Nursemaid" in text

    [record] = _records("inhabitant")
    assert (record.name, record.role, record.year_born) == (
        "Old Marta",
        "Dependent",
        1180,
    )


async def test_other_covenfolk_named_the_plural_of_its_role_hides_the_role_in_the_row():
    saga = _saga_with_people()
    saga.covenants[0].inhabitants = [
        Inhabitant(
            id="a", kind="inhabitant", name="Servants", role="Servant", quantity=4
        )
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        # Qty > 1: the role is redundant with the name, and the Year Born
        # column is "-" (no single birth year for a group).
        assert _inh_labels(app, "inhabitant") == [
            "Servants                              4           -"
        ]

        await _select_inh_row(pilot, app, "inhabitant", 0)
        panel = str(_cov_view(app).query_one("#inh-panel", Static).render())
        assert "Covenant Role: Servant" in panel  # still shown in the panel


async def test_craftsperson_links_one_of_the_grogs_abilities_and_stores_craft_fields():
    saga = _saga_with_people()
    saga.characters[2].abilities[1].level = 4  # Old Thomae's Brawl
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-craftsperson")
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("down")
        await pilot.press("enter")  # Old Thomae
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)

        ability = app.screen.query_one("#fld-linked_ability", Select)
        assert isinstance(ability, Select)  # a dropdown of the grog's Abilities
        assert [value for _, value in ability._options if isinstance(value, str)] == [
            "Athletics",
            "Brawl",
        ]
        assert app.screen.query_one("#fld-field_of_work", Select).value == "None"
        _fill(
            app,
            responsibility="Blacksmithing",
            skill_value=7,
            field_of_work="Books",
            rare=True,
            linked_ability="Brawl",
        )
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(_inh_labels(app, "craftsperson")) == 1)
        # Tied to the sheet's Brawl (Level 4): that wins over the typed 7.
        assert _inh_labels(app, "craftsperson") == [
            "Old Thomae          Blacksmithing           4    1        1193"
        ]

        # Editing again shows the score as read-only, taken from the Ability.
        await _select_inh_row(pilot, app, "craftsperson", 0)
        await pilot.press("e")
        await pilot.pause()
        assert not app.screen.query("#fld-skill_value")
        info = " ".join(
            str(s.render()) for s in app.screen.query(".fd-value").results(Static)
        )
        assert "4 (Level of Brawl)" in info
        await pilot.press("escape")

    [record] = _records("craftsperson")
    assert (record.field_of_work, record.rare, record.linked_ability) == (
        "Books",
        True,
        "Brawl",
    )
    # The typed number is kept as the fallback if the link is ever cleared.
    assert (record.skill_value, record.character_id) == (7, "grog1")


async def test_forms_and_the_remove_confirmation_fit_an_80_by_24_terminal():
    saga = _saga_with_people()
    saga.characters[2].abilities[1].level = 4
    saga.covenants[0].inhabitants = [
        Inhabitant(
            id="c",
            kind="craftsperson",
            name="Old Thomae",
            character_id="grog1",
            linked_ability="Brawl",
        )
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _select_covenant(pilot, app)
        await _select_inh_row(pilot, app, "craftsperson", 0)
        await pilot.press("e")
        await pilot.pause()
        region = app.screen.query_one("#fields-dialog").region
        assert region.right <= 80 and region.bottom <= 24  # right border on screen
        await pilot.press("escape")
        await pilot.pause()

        await _select_inh_row(pilot, app, "magus", 0)
        await pilot.press("A")
        await pilot.pause()
        region = app.screen.query_one("#confirm-dialog").region
        assert region.right <= 80 and region.bottom <= 24


async def test_craftsperson_score_is_typed_when_there_is_no_sheet_ability():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-craftsperson")
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("enter")  # (New person): no sheet at all
        await pilot.pause()
        _fill(app, name="Travelling Smith", responsibility="Smith", skill_value=6)
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(_inh_labels(app, "craftsperson")) == 1)
        assert _inh_labels(app, "craftsperson")[0] == (
            "Travelling Smith    Smith                   6    1     Unknown"
        )

        await _select_inh_row(pilot, app, "craftsperson", 0)
        await pilot.press("e")
        await pilot.pause()
        assert app.screen.query_one("#fld-skill_value", Input).value == "6"  # editable


async def test_quantity_drives_the_headcounts_and_must_be_at_least_one():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-turb")
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("enter")  # new person
        await pilot.pause()
        _fill(
            app, name="Guards", year_born=1200, responsibility="Gatehouse", quantity=0
        )
        await _save_dialog(pilot, app)
        assert isinstance(app.screen, FieldsDialog)  # quantity 0 refused
        assert "at least 1" in str(app.screen.query_one("#fields-error").render())
        _fill(app, quantity=3)
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: _inh_title(app, "turb") == "Turb (3)")

        text = str(_cov_view(app).query_one("#inh-population-content", Static).render())
        assert re.search(r"Total Inhabitants:\s+5\b", text)  # magus + companion + 3


async def test_horses_and_livestock_take_a_blank_year_and_a_quantity():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        for kind, name in (("horse", "Grey Mare"), ("livestock", "Sheep")):
            await _open_inh_section(pilot, app, f"section-inh-{kind}")
            await pilot.press("a")
            await _wait_for_screen(pilot, app, FieldsDialog)
            assert isinstance(app.screen, FieldsDialog)  # no picker for animals
            _fill(app, name=name, quantity=4)
            await _save_dialog(pilot, app)
            await wait_until(pilot, lambda kind=kind: len(_inh_labels(app, kind)) == 1)
            assert _inh_labels(app, kind) == [f"{name:<20}    4     Unknown"]
        assert _inh_title(app, "horse") == "Horses (4)"


async def test_e_and_A_act_on_the_selected_inhabitant_and_delete_confirms():
    saga = _saga_with_people()
    saga.covenants[0].inhabitants = [
        Inhabitant(id="a", kind="turb", name="First", year_born=1200),
        Inhabitant(id="b", kind="turb", name="Second [x]", year_born=1201),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_inh_row(pilot, app, "turb", 1)

        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)  # no "which one?" picker
        assert app.screen.query_one("#fld-name", Input).value == "Second [x]"
        await pilot.press("escape")
        await pilot.pause()

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert message == "Delete Second [x]?"
        await pilot.press("n")
        await pilot.pause()
        assert len(_inh_labels(app, "turb")) == 2

        await pilot.press("A")
        await pilot.pause()
        await pilot.press("y")
        await wait_until(pilot, lambda: len(_inh_labels(app, "turb")) == 1)
        assert _inh_labels(app, "turb")[0].startswith("First")

        # Nothing chosen any more: 'A' falls back to asking which one.
        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

    assert [r.name for r in _records("turb")] == ["First"]


async def test_deleting_an_assigned_grog_returns_it_to_the_available_list():
    saga = _saga_with_people()
    saga.covenants[0].inhabitants = [
        Inhabitant(id="a", kind="specialist", name="Old Thomae", character_id="grog1")
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_inh_row(pilot, app, "specialist", 0)
        await pilot.press("A")
        await pilot.pause()
        await pilot.press("y")
        await wait_until(pilot, lambda: not _inh_labels(app, "specialist"))
        cov = app.screen.selected_covenant
        assert "Old Thomae" in [
            g.name for g in inh.available_grogs(app.screen.saga, cov)
        ]


async def test_the_panel_renders_description_emphasis_for_the_chosen_inhabitant():
    saga = _saga_with_people()
    saga.covenants[0].inhabitants = [
        Inhabitant(
            id="a",
            kind="craftsperson",
            name="Gerhard",
            year_born=1187,
            description="Master **smith**, works *only* in iron. 5 * 3 stays.",
        )
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_inh_row(pilot, app, "craftsperson", 0)
        panel = _cov_view(app).query_one("#inh-panel", Static)
        assert "Master smith, works only in iron. 5 * 3 stays." in str(panel.render())
        styled = _styled_words(panel)
        assert ("smith", "b") in styled and ("only", "i") in styled


async def test_loyalty_governance_is_typed_unless_a_governance_boon_provides_it():
    saga = _saga_with_people()
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-loyalty")
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        assert app.screen.query_one("#fld-equipment", Select).value == "Standard"
        assert app.screen.query_one("#fld-money", Select).value == "Standard salary"
        # The four totals are calculated, not typed.
        for key in ("base_points", "current_points", "prevailing_score"):
            assert not app.screen.query(f"#fld-{key}")
        _fill(
            app,
            governance="Guild of Mercers",
            equipment="Anything they need",
            money="Lavish salary",
            familiarity=1,
        )
        await _save_dialog(pilot, app)
        await wait_until(
            pilot,
            lambda: (
                "Guild of Mercers"
                in str(_cov_view(app).query_one("#inh-loyalty-left", Static).render())
            ),
        )
        left = str(_cov_view(app).query_one("#inh-loyalty-left", Static).render())
        right = str(_cov_view(app).query_one("#inh-loyalty-right", Static).render())
        assert "Guild of Mercers" in left
        # 1 magus, The Gift (-30); +20 Equipment, +20 Money, +1 Familiarity -> 11.
        assert re.search(r"Base Loyalty Points:\s+-30", left)
        assert re.search(r"Total modifiers:\s+41", left)
        assert re.search(r"Current Loyalty Points:\s+11", left)
        assert re.search(r"Prevailing Loyalty Score:\s+1\b", left)
        assert "Anything they need  (+20)" in right and "Lavish salary  (+20)" in right

    loyalty = storage.load_saga("test_saga").covenants[0].loyalty
    assert loyalty.governance == "Guild of Mercers"
    assert (loyalty.equipment, loyalty.money) == ("Anything they need", "Lavish salary")

    # With a governance Boon the type isn't typed in: the field becomes info.
    saga = storage.load_saga("test_saga")
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_free_council")
    ]
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-loyalty")
        await pilot.press("e")
        await pilot.pause()
        assert not app.screen.query("#fld-governance")
        await pilot.press("escape")
        await pilot.pause()
        left = str(_cov_view(app).query_one("#inh-loyalty-left", Static).render())
        assert "Council" in left and "Guild of Mercers" not in left


async def test_population_and_miscellaneous_fields_are_editable_and_total_is_calculated():
    saga = _saga_with_people()
    saga.covenants[0].inhabitants = [
        Inhabitant(
            id="s", kind="inhabitant", name="Servants", role="Servant", quantity=3
        )
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        view = _cov_view(app)

        await _open_inh_section(pilot, app, "section-inh-population")
        await pilot.press("e")
        await pilot.pause()
        assert not app.screen.query("#fld-total")  # calculated: not an input
        # Teamsters/Servants/Laborers and their two "Needed" minimums are all
        # calculated now, from the Other Covenfolk list -- nothing to type.
        for key in ("teamsters", "teamsters_needed", "servants", "servants_needed"):
            assert not app.screen.query(f"#fld-{key}")
        assert not app.screen.query("#fld-laborers")
        _fill(app, other_people=6)
        await _save_dialog(pilot, app)
        await wait_until(
            pilot,
            lambda: re.search(
                r"Total Inhabitants:\s+11\b",
                str(view.query_one("#inh-population-content", Static).render()),
            ),
        )
        text = str(view.query_one("#inh-population-content", Static).render())
        minimum = inh.minimum_servants(view.saga, view.covenant)
        assert f"3 / {minimum}" in text  # 3 servants already on the list
        assert re.search(
            r"Total Inhabitants:\s+11\b", text
        )  # 6 other + magus + companion + 3 servants

        await _open_inh_section(pilot, app, "section-inh-misc")
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        _fill(app, aging_magi=1, magic_laborers=2, magic_turbula=5)
        await _save_dialog(pilot, app)
        await wait_until(
            pilot,
            lambda: "5" in str(view.query_one("#inh-misc-right", Static).render()),
        )

    pop = storage.load_saga("test_saga").covenants[0].population
    assert pop.other_people == 6
    assert (pop.aging_magi, pop.magic_laborers, pop.magic_turbula) == (1, 2, 5)


async def test_add_is_not_offered_on_the_summary_sections_but_edit_is():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        for section in (
            "section-inh-loyalty",
            "section-inh-population",
            "section-inh-misc",
        ):
            await _open_inh_section(pilot, app, section)
            await pilot.press("a")
            await pilot.pause()
            assert isinstance(app.screen, WorkspaceScreen), section  # nothing to add
            await pilot.press("e")
            await _wait_for_screen(pilot, app, FieldsDialog)
            assert isinstance(app.screen, FieldsDialog), section
            await pilot.press("escape")
            await pilot.pause()


async def test_inhabitant_dialogs_fit_a_small_terminal_and_hug_content_on_a_tall_one():
    storage.save_saga(_saga_with_people())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _select_covenant(pilot, app)
        # The busiest form: a craftsperson (many fields + a description).
        await _open_inh_section(pilot, app, "section-inh-craftsperson")
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("down")
        await pilot.press("enter")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        for button in app.screen.query(Button):
            assert button.region.height > 0 and button.region.bottom <= 24, button.id
        await pilot.press("escape")
        await pilot.pause()

        # ...and the biggest summary form: Loyalty.
        await _open_inh_section(pilot, app, "section-inh-loyalty")
        await pilot.press("e")
        await pilot.pause()
        for button in app.screen.query(Button):
            assert button.region.height > 0 and button.region.bottom <= 24, button.id

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_inh_section(pilot, app, "section-inh-horse")
        await pilot.press("a")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        assert app.screen.query_one("#fields-dialog").region.height < 30


# -- Covenant Possessions tab ---------------------------------------------------


async def _show_possessions_tab(pilot, app) -> None:
    view = app.screen._covenant_sheet_view
    await wait_until(pilot, lambda: view.initial_tab_seen)
    await pilot.pause()
    view.query_one(TabbedContent).active = "tab-cov-possessions"
    await pilot.pause()


async def _open_pos_section(pilot, app, kind: str) -> None:
    """Focus a Possessions section (so its a/A/e keys apply)."""
    await _show_possessions_tab(pilot, app)
    view = app.screen._covenant_sheet_view
    view.query_one(f"#section-pos-{kind}", Collapsible).query_one(
        "CollapsibleTitle"
    ).focus()
    await pilot.pause()
    await wait_until(
        pilot, lambda: app.screen._active_section() == f"section-pos-{kind}"
    )


async def _select_pos_row(pilot, app, kind: str, row: int) -> None:
    await _show_possessions_tab(pilot, app)
    rows = app.screen._covenant_sheet_view.query_one(
        f"#pos-{kind}-list", SelectableList
    )
    rows.focus()
    await pilot.pause()
    rows.highlighted = row
    await pilot.pause()


def _pos_labels(app, kind: str) -> list[str]:
    return [label for _, label in app.screen._covenant_sheet_view._pos_rows(kind)]


def _pos_records(kind: str | None = None) -> list[Possession]:
    cov = storage.load_saga("test_saga").covenants[0]
    return [r for r in cov.possessions if kind is None or r.kind == kind]


def _pos_panel(app) -> str:
    return str(app.screen._covenant_sheet_view.query_one("#pos-panel", Static).render())


async def _add_possession(pilot, app, kind: str, **values) -> None:
    """Press 'a' in a section, fill the form and save it."""
    before = len(_pos_labels(app, kind))
    await _open_pos_section(pilot, app, kind)
    await pilot.press("a")
    await _wait_for_screen(pilot, app, FieldsDialog)
    assert isinstance(app.screen, FieldsDialog)
    _fill(app, **values)
    await _save_dialog(pilot, app)
    await wait_until(pilot, lambda: len(_pos_labels(app, kind)) > before)


async def test_possessions_tab_has_its_seven_sections_and_lists_the_labs_as_sanctums():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _show_possessions_tab(pilot, app)
        view = app.screen._covenant_sheet_view
        sections = [
            view.query_one(f"#section-pos-{kind}", Collapsible)
            for kind in pos.KIND_TITLES
        ]
        assert [_plain_title(x) for x in sections] == [
            "Properties and Land",
            "Sanctums",
            "Weapons",
            "Armor",
            "Vis Sources",
            "Raw Vis Stores",
            "Items",
        ]
        assert all(not section.collapsed for section in sections)
        # The laboratory is a sanctum without anyone adding it, Quality/Upkeep
        # read live from its Lab Characteristics.
        assert _pos_labels(app, "sanctum") == [
            "Test Lab            Leandro               0       0"
        ]
        assert "Select a possession" in _pos_panel(app)


async def test_the_panel_is_docked_below_the_lists_and_stays_on_screen():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _show_possessions_tab(pilot, app)
        view = app.screen._covenant_sheet_view
        scroll = view.query_one("#pos-scroll").region
        panel = view.query_one("#pos-panel").region
        assert panel.y >= scroll.bottom  # below the scrolling lists
        assert panel.bottom <= 50  # and fully on screen


async def test_property_needs_only_a_name_and_supports_edit_and_delete():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_pos_section(pilot, app, "property")
        await pilot.press("a")
        await pilot.pause()
        await _save_dialog(pilot, app)  # nothing filled in
        assert "Name is required" in str(app.screen.query_one("#fields-error").render())
        _fill(app, name="Bare Plot")
        await _save_dialog(pilot, app)  # every other field is optional
        await wait_until(pilot, lambda: len(_pos_labels(app, "property")) == 1)
        assert _pos_labels(app, "property") == ["Bare Plot"]

        # Edit it: all the fields, then the row and panel show them.
        await _select_pos_row(pilot, app, "property", 0)
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        _fill(
            app,
            location="By the river",
            dimensions="40 acres",
            inhabitants="Two tenant families",
            description="Rich **black** soil.",
        )
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: "Location" in _pos_labels(app, "property")[0])
        assert _pos_labels(app, "property") == [
            "Bare Plot           By the river      40 acres      Two tenant families"
        ]
        await _select_pos_row(pilot, app, "property", 0)
        panel = _pos_panel(app)
        assert "Rich black soil." in panel and "Dimensions: 40 acres" in panel

        # Delete confirms.
        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await wait_until(pilot, lambda: not _pos_labels(app, "property"))

    assert _pos_records("property") == []


async def test_a_laboratory_sanctum_edits_only_covenant_side_fields_and_cannot_be_deleted():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_pos_row(pilot, app, "sanctum", 0)
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        for key in ("name", "owner", "location", "build_points", "quality", "upkeep"):
            assert not app.screen.query(f"#fld-{key}"), key  # from the laboratory
        assert (
            app.screen.query_one("#fld-usage", Select).value == "Standard (2 Seasons)"
        )  # the default
        _fill(
            app,
            usage="Heavy (3+ Seasons)",
            description="Busy *all* year.",
        )
        await _save_dialog(pilot, app)
        assert _pos_labels(app, "sanctum") == [
            "Test Lab            Leandro               0       0"
        ]

        await _select_pos_row(pilot, app, "sanctum", 0)
        panel = _pos_panel(app)
        for expected in (
            "Usage: Heavy (3+ Seasons)",
            "Build Points: 0",
            "Busy all year.",
        ):
            assert expected in panel, expected

        # A laboratory of the covenant can't be deleted from here.
        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)  # no confirmation
        assert len(_pos_labels(app, "sanctum")) == 1

    [record] = _pos_records("sanctum")
    assert record.lab_id == "lab1" and record.usage == "Heavy (3+ Seasons)"


async def test_manual_sanctums_have_every_field_and_can_be_deleted():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_pos_section(pilot, app, "sanctum")
        await pilot.press("a")
        await pilot.pause()
        assert (
            app.screen.query_one("#fld-usage", Select).value == "Standard (2 Seasons)"
        )
        # Nobody owns it yet: free for visitors to use (the Usage says how hard).
        assert app.screen.query_one("#fld-owner", Input).value == "Free"
        _fill(
            app,
            name="Hidden Study",
            owner="Corvinus",
            location="Under the stairs",
            quality=2,
            upkeep=5,
            build_points=15,
        )
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(_pos_labels(app, "sanctum")) == 2)
        assert _pos_labels(app, "sanctum")[1] == (
            "Hidden Study        Corvinus              2       5"
        )
        await _select_pos_row(pilot, app, "sanctum", 1)
        assert "Build Points: 15" in _pos_panel(app)

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await wait_until(pilot, lambda: len(_pos_labels(app, "sanctum")) == 1)

    assert _pos_records("sanctum") == []


async def test_weapons_armor_and_items_need_a_name_and_a_quantity_defaulting_to_one():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        for kind, name in (
            ("weapon", "Crossbows"),
            ("armor", "Mail Hauberks"),
            ("item", "The Weeping Lens"),
        ):
            await _open_pos_section(pilot, app, kind)
            await pilot.press("a")
            await pilot.pause()
            assert app.screen.query_one("#fld-quantity", Input).value == "1"  # default
            await _save_dialog(pilot, app)
            assert "Name is required" in str(
                app.screen.query_one("#fields-error").render()
            )
            _fill(app, name=name, quantity=0)
            await _save_dialog(pilot, app)
            assert "at least 1" in str(app.screen.query_one("#fields-error").render())
            _fill(app, quantity=3, description="Well **kept**.")
            await _save_dialog(pilot, app)
            await wait_until(pilot, lambda kind=kind: len(_pos_labels(app, kind)) == 1)
            # Weapons and armor carry a Type and Quality (their points); items don't.
            expected = {
                # Weapons get four extra trailing combat-figure columns
                # (Init/Attack/Defense/Damage), defaulting to 0; armor/items
                # don't (see STORY-205).
                "weapon": (
                    "Crossbows           Weapon or shield    Standard"
                    "        3    0    0    0    0"
                ),
                "armor": "Mail Hauberks       Partial armor       Standard        3",
                "item": "The Weeping Lens        3",
            }[kind]
            assert _pos_labels(app, kind) == [expected]

        await _select_pos_row(pilot, app, "item", 0)
        panel = _pos_panel(app)
        assert "Quantity: 3" in panel and "Well kept." in panel
        assert "Points" not in panel

        await _select_pos_row(pilot, app, "weapon", 0)
        panel = _pos_panel(app)
        for expected in (
            "Type: Weapon or shield",
            "Quality: Standard",
            "Quantity: 3",
            "Points: 12 (4 each",
            "Init: 0",
            "Attack: 0",
            "Defense: 0",
            "Damage: 0",
        ):
            assert expected in panel, expected


async def test_weapon_combat_figures_are_typed_in_and_shown_on_the_row_and_panel():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_pos_section(pilot, app, "weapon")
        await pilot.press("a")
        await pilot.pause()
        _fill(
            app,
            name="Longsword",
            weapon_init=2,
            weapon_attack=5,
            weapon_defense=3,
            weapon_damage=7,
        )
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(_pos_labels(app, "weapon")) == 1)

        assert _pos_labels(app, "weapon")[0].endswith("    2    5    3    7")

        await _select_pos_row(pilot, app, "weapon", 0)
        panel = _pos_panel(app)
        for expected in ("Init: 2", "Attack: 5", "Defense: 3", "Damage: 7"):
            assert expected in panel, expected

        # Armor doesn't get these fields at all.
        await _open_pos_section(pilot, app, "armor")
        await pilot.press("a")
        await pilot.pause()
        assert not app.screen.query("#fld-weapon_init")

    [record] = _pos_records("weapon")
    assert (
        record.weapon_init,
        record.weapon_attack,
        record.weapon_defense,
        record.weapon_damage,
    ) == (2, 5, 3, 7)


async def test_siege_engines_only_come_expensive_and_points_follow_the_table():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_pos_section(pilot, app, "weapon")
        await pilot.press("a")
        await pilot.pause()
        types = app.screen.query_one("#fld-gear_type", Select)
        assert [v for _, v in types._options if isinstance(v, str)] == [
            "Weapon or shield",
            "Ballista or light catapult",
            "Heavy catapult or trebuchet",
        ]
        _fill(app, name="Ballista", gear_type="Ballista or light catapult")
        await _save_dialog(pilot, app)  # still Standard
        assert isinstance(app.screen, FieldsDialog)
        assert "only comes expensive" in str(
            app.screen.query_one("#fields-error").render()
        )
        _fill(app, gear_quality="Expensive")
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(_pos_labels(app, "weapon")) == 1)
        cov = app.screen.selected_covenant
        assert pos.gear_points(app.screen.saga, cov) == 16


async def test_vis_source_requires_name_art_season_and_pawns():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_pos_section(pilot, app, "vis_source")
        await pilot.press("a")
        await pilot.pause()
        error = lambda: str(app.screen.query_one("#fields-error").render())

        await _save_dialog(pilot, app)
        assert "Name is required" in error()
        _fill(app, name="Whispering Well")
        await _save_dialog(pilot, app)
        assert "Art is required" in error()
        _fill(app, art="Vim")
        await _save_dialog(pilot, app)
        assert "Season harvested is required" in error()
        _fill(app, season="Winter", pawns=0)
        await _save_dialog(pilot, app)
        assert "Pawns must be at least 1" in error()
        _fill(
            app,
            pawns=3,
            location="Beneath the chapel",
            physical_form="Water in a stone basin",
            description="Only flows *after* midwinter.",
        )
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(_pos_labels(app, "vis_source")) == 1)
        assert _pos_labels(app, "vis_source") == [
            "Whispering Well     Vim            3  Winter"
        ]

        await _select_pos_row(pilot, app, "vis_source", 0)
        panel = _pos_panel(app)
        for expected in (
            "Season: Winter",
            "Location: Beneath the chapel",
            "Physical Form: Water in a stone basin",
            "Only flows after midwinter.",
        ):
            assert expected in panel, expected

    [record] = _pos_records("vis_source")
    assert (record.art, record.season, record.pawns) == ("Vim", "Winter", 3)


async def test_art_and_season_choices_are_the_real_lists():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_pos_section(pilot, app, "vis_source")
        await pilot.press("a")
        await pilot.pause()
        arts = [
            v
            for _, v in app.screen.query_one("#fld-art", Select)._options
            if isinstance(v, str)
        ]
        seasons = [
            v
            for _, v in app.screen.query_one("#fld-season", Select)._options
            if isinstance(v, str)
        ]
        assert arts == [*TECHNIQUES, *FORMS] and len(arts) == 15
        assert seasons == ["Spring", "Summer", "Autumn", "Winter"]


async def test_raw_vis_stores_take_name_art_pawns_and_optional_location_and_form():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_pos_section(pilot, app, "vis_store")
        await pilot.press("a")
        await pilot.pause()
        assert not app.screen.query("#fld-description")  # not one of its fields
        assert not app.screen.query("#fld-season")  # a vis SOURCE field
        await _save_dialog(pilot, app)
        assert "Name is required" in str(app.screen.query_one("#fields-error").render())
        _fill(app, name="Vim Vis", art="Vim", pawns=9)  # location/form left blank
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(_pos_labels(app, "vis_store")) == 1)
        assert _pos_labels(app, "vis_store") == ["Vim Vis             Vim            9"]

        await _select_pos_row(pilot, app, "vis_store", 0)
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        _fill(app, location="The vault", physical_form="Lumps of amber")
        await _save_dialog(pilot, app)
        await _select_pos_row(pilot, app, "vis_store", 0)
        await wait_until(pilot, lambda: "The vault" in _pos_panel(app))
        panel = _pos_panel(app)
        assert (
            "Location: The vault" in panel and "Physical Form: Lumps of amber" in panel
        )


async def test_e_and_A_act_on_the_chosen_possession_with_a_picker_fallback():
    saga = _saga_with_bare_laboratory()
    saga.covenants[0].possessions = [
        Possession(id="a", kind="item", name="First"),
        Possession(id="b", kind="item", name="Second [x]"),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_pos_row(pilot, app, "item", 1)

        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)  # no "which one?" picker
        assert app.screen.query_one("#fld-name", Input).value == "Second [x]"
        await pilot.press("escape")
        await pilot.pause()

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert message == "Delete Second [x]?"
        await pilot.press("n")
        await pilot.pause()
        assert len(_pos_labels(app, "item")) == 2
        await pilot.press("A")
        await pilot.pause()
        await pilot.press("y")
        await wait_until(pilot, lambda: len(_pos_labels(app, "item")) == 1)

        # Nothing chosen any more: 'A' falls back to asking which one.
        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

    assert [r.name for r in _pos_records("item")] == ["First"]


async def test_one_selection_across_the_possession_lists():
    saga = _saga_with_bare_laboratory()
    saga.covenants[0].possessions = [
        Possession(id="a", kind="weapon", name="Crossbows"),
        Possession(id="b", kind="armor", name="Mail"),
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_pos_row(pilot, app, "weapon", 0)
        assert "Name: Crossbows" in _pos_panel(app)
        await _select_pos_row(pilot, app, "armor", 0)
        view = app.screen._covenant_sheet_view
        assert view.selected_possession("weapon") is None  # the other list let go
        assert "Name: Mail" in _pos_panel(app)


async def test_legacy_vis_stock_shows_up_as_raw_vis_stores():
    saga = _saga_with_bare_laboratory()
    saga.covenants[0].vis_stock = {"Ignem": 5, "Vim": 2}
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _show_possessions_tab(pilot, app)
        assert _pos_labels(app, "vis_store") == [
            "Ignem Vis           Ignem          5",
            "Vim Vis             Vim            2",
        ]


async def test_possession_forms_fit_a_small_terminal_and_hug_content_on_a_tall_one():
    storage.save_saga(_saga_with_bare_laboratory())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _select_covenant(pilot, app)
        await _open_pos_section(pilot, app, "vis_source")  # the busiest form
        await pilot.press("a")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        for button in app.screen.query(Button):
            assert button.region.height > 0 and button.region.bottom <= 24, button.id

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_pos_section(pilot, app, "weapon")
        await pilot.press("a")
        await pilot.pause()
        assert app.screen.query_one("#fields-dialog").region.height < 30


# -- Covenant Economics tab ------------------------------------------------------


def _saga_for_economics() -> Saga:
    """Corvinus (magus) and Alys (companion) plus six turb and three laborers:
    17 points of inhabitants, one source of income."""
    saga = _saga_with_people()
    cov = saga.covenants[0]
    cov.inhabitants = [
        Inhabitant(id="t", kind="turb", name="Guards", quantity=6),
        Inhabitant(
            id="l", kind="inhabitant", name="Laborers", role="Laborer", quantity=3
        ),
    ]
    cov.economics.income_sources = [
        IncomeSource(
            id="a", name="Salt Mine", type="Typical", description="A **rich** seam."
        )
    ]
    return saga


async def _show_economics_tab(pilot, app) -> None:
    view = app.screen._covenant_sheet_view
    await wait_until(pilot, lambda: view.initial_tab_seen)
    await pilot.pause()
    view.query_one(TabbedContent).active = "tab-cov-economics"
    await pilot.pause()


async def _open_eco_section(pilot, app, which: str) -> None:
    """Focus an Economics section (so its a/A/e keys apply)."""
    await _show_economics_tab(pilot, app)
    view = app.screen._covenant_sheet_view
    view.query_one(f"#section-eco-{which}", Collapsible).query_one(
        "CollapsibleTitle"
    ).focus()
    await pilot.pause()
    await wait_until(
        pilot, lambda: app.screen._active_section() == f"section-eco-{which}"
    )


async def _select_eco_row(pilot, app, which: str, row: int) -> None:
    await _show_economics_tab(pilot, app)
    rows = app.screen._covenant_sheet_view.query_one(
        f"#eco-{which}-list", SelectableList
    )
    rows.focus()
    await pilot.pause()
    rows.highlighted = row
    await pilot.pause()


def _eco_panel(app) -> str:
    return str(_cov_view(app).query_one("#eco-panel", Static).render())


def _eco_labels(app, which: str) -> list[str]:
    view = _cov_view(app)
    summary = eco.summarize(view.saga, view.covenant)
    return [re.sub(r"\s+", " ", label) for _, label in view._eco_rows(which, summary)]


def _eco_wealth(app) -> str:
    view = _cov_view(app)
    return "\n".join(
        str(view.query_one(f"#eco-wealth-{side}", Static).render())
        for side in ("left", "right")
    )


def _saved_economics():
    return storage.load_saga("test_saga").covenants[0].economics


async def test_economics_tab_shows_calculated_wealth_and_all_its_sections():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _show_economics_tab(pilot, app)
        view = _cov_view(app)

        sections = [
            view.query_one(f"#section-eco-{k}", Collapsible)
            for k in ("wealth", "income", "expenditure", "savings")
        ]
        assert [_plain_title(x) for x in sections] == [
            "Wealth",
            "Sources of Income",
            "Yearly Expenditure",
            "Cost Savings",
        ]
        assert all(not x.collapsed for x in sections)

        wealth = _eco_wealth(app)
        # 5 (magus) + 3 (companion) + 6 turb + 3 laborers
        assert re.search(r"Points of Inhabitants:\s+17\b", wealth)
        assert re.search(r"Points of Laboratories:\s+0\b", wealth)
        assert re.search(r"Points of Weapons and Armor:\s+0\b", wealth)
        assert re.search(r"Wealth:\s+0\b", wealth)
        assert re.search(r"Total Income:\s+100\b", wealth)
        # 2 + 4 + 9 + 4 + 1 writing + 1 sundry (the minimum) = 21; laborers save 3
        assert re.search(r"Expenditure \(Before Cost Savings\):\s+21\b", wealth)
        assert re.search(r"Cost Savings:\s+3\b", wealth)
        assert re.search(r"Total Expenditure:\s+18\b", wealth)

        names = lambda which: [x.split(" ")[0] for x in _eco_labels(app, which)]
        assert names("expenditure") == [
            "Buildings",
            "Consumables",
            "Laboratories",
            "Provisions",
            "Wages",
            "Weapons",
            "Writing",
            "Tithes",
            "Inflation",
            "Sundry",
        ]
        assert names("savings") == ["Laborers", "Craftspeople", "Magic", "Emergency"]
        headers = [str(w.render()) for w in view.query(".eco-header").results(Static)]
        assert "Type" in headers[0] and "Income" in headers[0]  # income source header
        assert "Cost" in headers[1] and "Quantity" in headers[2]
        assert "Savings" in headers[1] and "Notes" in headers[1]
        assert _eco_labels(app, "income") == ["Salt Mine Typical 100"]
        assert "Select a source" in _eco_panel(app)


async def test_wealth_is_typed_with_e():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_eco_section(pilot, app, "wealth")
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        assert app.screen.query_one("#fld-wealth", Input).value == "0"
        _fill(app, wealth=25)
        await _save_dialog(pilot, app)
        await wait_until(
            pilot, lambda: re.search(r"Wealth:\s+25\b", _eco_wealth(app)) is not None
        )

    assert _saved_economics().wealth == 25


async def _add_income(pilot, app, **values) -> None:
    before = len(_eco_labels(app, "income"))
    await _open_eco_section(pilot, app, "income")
    await pilot.press("a")
    await _wait_for_screen(pilot, app, FieldsDialog)
    assert isinstance(app.screen, FieldsDialog)
    _fill(app, **values)
    await _save_dialog(pilot, app)
    await wait_until(pilot, lambda: len(_eco_labels(app, "income")) > before)


async def test_a_new_income_source_takes_its_income_from_its_type_unless_typed_over():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_eco_section(pilot, app, "income")
        await pilot.press("a")
        await pilot.pause()
        assert app.screen.query_one("#fld-type", Select).value == "Typical"
        assert app.screen.query_one("#fld-income", Input).value == ""  # follows type
        types = app.screen.query_one("#fld-type", Select)
        assert [v for _, v in types._options if isinstance(v, str)] == [
            "None",
            "Lesser",
            "Typical",
            "Greater",
            "Legendary",
        ]
        await _save_dialog(pilot, app)
        assert isinstance(app.screen, FieldsDialog)  # a name is required
        assert "Name is required" in str(app.screen.query_one("#fields-error").render())
        _fill(app, name="Old Quarry", type="Legendary")
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(_eco_labels(app, "income")) == 2)

        await _add_income(pilot, app, name="Toll", type="Lesser", income=55)
        await _add_income(pilot, app, name="Idle Land", type="None")
        assert _eco_labels(app, "income") == [
            "Salt Mine Typical 100",
            "Old Quarry Legendary 1000",
            "Toll Lesser 55",
            "Idle Land None 0",
        ]
        # 100 + 1000 + 55 + 0
        assert re.search(r"Total Income:\s+1155\b", _eco_wealth(app))

    sources = _saved_economics().income_sources
    assert [s.income for s in sources] == [None, None, 55, None]  # only typed ones kept


async def test_choosing_rows_fills_the_panel_with_one_selection_across_the_lists():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_eco_row(pilot, app, "income", 0)
        panel = _eco_panel(app)
        assert "Name: Salt Mine" in panel and "Type: Typical" in panel
        assert "Current Income: 100 (the usual for Typical)" in panel
        assert "A rich seam." in panel and "**" not in panel  # emphasis rendered

        await _select_eco_row(pilot, app, "expenditure", 3)
        view = _cov_view(app)
        assert view.selected_economics("income") is None  # unchosen
        panel = _eco_panel(app)
        assert "Name: Provisions" in panel
        assert "Rule: 5 pounds per 10 pts Inhabitants" in panel
        assert "Cost: 9" in panel and "Savings: 3" in panel
        assert "17 pts of inhabitants x 5 / 10" in panel

        await _select_eco_row(pilot, app, "savings", 0)
        assert view.selected_economics("expenditure") is None
        panel = _eco_panel(app)
        assert "Name: Laborers" in panel and "Quantity: 3" in panel


async def test_e_and_A_act_on_the_selected_income_source_and_delete_confirms():
    saga = _saga_for_economics()
    saga.covenants[0].economics.income_sources.append(
        IncomeSource(id="b", name="[Toll] bridge", type="Lesser")
    )
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        # The brackets are escaped so they aren't read as markup.
        assert _eco_labels(app, "income")[1].startswith("\\[Toll] bridge")
        await _select_eco_row(pilot, app, "income", 1)

        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)  # no "which one?" picker
        assert app.screen.query_one("#fld-name", Input).value == "[Toll] bridge"
        assert app.screen.query_one("#fld-income", Input).value == ""
        _fill(app, type="Greater", income=260)
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: "260" in _eco_labels(app, "income")[1])
        assert "Current Income: 260 (typed; Greater is usually 250)" in _eco_panel(app)

        await _select_eco_row(pilot, app, "income", 1)
        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert message == "Delete [Toll] bridge?"
        await pilot.press("n")
        await pilot.pause()
        assert len(_eco_labels(app, "income")) == 2

        await pilot.press("A")
        await pilot.pause()
        await pilot.press("y")
        await wait_until(pilot, lambda: len(_eco_labels(app, "income")) == 1)
        assert re.search(r"Total Income:\s+100\b", _eco_wealth(app))

        # Nothing chosen any more: 'A' and 'e' fall back to asking which one.
        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("escape")
        await pilot.pause()
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)

    assert [s.name for s in _saved_economics().income_sources] == ["Salt Mine"]


async def test_improve_updates_multiplier_and_projected_income_live_then_confirms():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_eco_row(pilot, app, "income", 0)  # Salt Mine, income 100

        await pilot.press("i")
        await pilot.pause()
        assert isinstance(app.screen, ImproveIncomeScreen)
        assert app.screen.query_one("#improve-effect", Select).value == "Status Quo"
        multiplier = lambda: str(
            app.screen.query_one("#improve-multiplier", Static).render()
        )
        projected = lambda: str(
            app.screen.query_one("#improve-projected", Static).render()
        )
        assert multiplier() == "x1" and projected() == "100"

        app.screen.query_one("#improve-effect", Select).value = "Boom"
        await pilot.pause()
        assert multiplier() == "x1.5" and projected() == "150"

        app.screen.query_one("#btn-commit", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert message == "Update Salt Mine's income from 100 to 150?"

        await pilot.press("n")  # decline: still on the Improve dialog, unchanged
        await pilot.pause()
        assert isinstance(app.screen, ImproveIncomeScreen)

        app.screen.query_one("#btn-commit", Button).press()
        await pilot.pause()
        await pilot.press("y")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))

        await wait_until(
            pilot, lambda: "experienced Boom" in _eco_labels(app, "income")[0]
        )
        label = _eco_labels(app, "income")[0]
        assert label == (
            "Salt Mine Typical 150 1220 - Salt Mine experienced Boom "
            "changing Income from 100 to 150."
        )
        await _select_eco_row(pilot, app, "income", 0)
        panel = _eco_panel(app)
        assert panel.index("Note:") < panel.index("Description:")
        assert "A rich seam." in panel  # the description, still there afterward

    source = _saved_economics().income_sources[0]
    assert source.income == 150
    assert source.note == (
        "1220 - Salt Mine experienced Boom changing Income from 100 to 150."
    )


async def test_improve_with_status_quo_records_the_no_change_note():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_eco_row(pilot, app, "income", 0)
        await pilot.press("i")
        await pilot.pause()
        app.screen.query_one("#btn-commit", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        assert "from 100 to 100" in str(
            app.screen.query_one("#confirm-message", Static).render()
        )
        await pilot.press("y")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))

    source = _saved_economics().income_sources[0]
    assert source.income == 100
    assert source.note == (
        "1220 - Salt Mine experienced no growth or setbacks. Status Quo maintained."
    )


async def test_improve_cancel_and_the_which_one_fallback():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        # Nothing chosen: 'i' falls back to asking which one, same as e/A.
        await _open_eco_section(pilot, app, "income")
        await pilot.press("i")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("enter")  # Salt Mine
        await pilot.pause()
        assert isinstance(app.screen, ImproveIncomeScreen)
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    assert _saved_economics().income_sources[0].income is None  # untouched


async def test_expenditure_rows_take_notes_and_the_typed_ones_take_amounts():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)

        # A calculated row: only its Notes can be typed.
        await _select_eco_row(pilot, app, "expenditure", 0)
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        assert not app.screen.query("#fld-tithes")
        _fill(app, notes="Roof of the north tower")
        await _save_dialog(pilot, app)
        await wait_until(
            pilot,
            lambda: "Roof of the north tower" in _eco_labels(app, "expenditure")[0],
        )
        await wait_until(pilot, lambda: "Roof of the north tower" in _eco_panel(app))
        assert "Roof of the north tower" in _eco_panel(app)  # panel refreshed too

        # A typed row: an amount, which feeds the totals.
        await _select_eco_row(pilot, app, "expenditure", 7)
        await pilot.press("e")
        await pilot.pause()
        assert app.screen.query_one("#fld-tithes", Input).value == "0"
        _fill(app, tithes=4, notes="Church")
        await _save_dialog(pilot, app)
        await wait_until(
            pilot, lambda: _eco_labels(app, "expenditure")[7].startswith("Tithes 4")
        )
        assert re.search(r"Before Cost Savings\):\s+25\b", _eco_wealth(app))  # 21 + 4

        # An empty note is removed, not stored blank.
        await _select_eco_row(pilot, app, "expenditure", 0)
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        _fill(app, notes="")
        await _save_dialog(pilot, app)
        await wait_until(
            pilot, lambda: "Roof" not in _eco_labels(app, "expenditure")[0]
        )

    economics = _saved_economics()
    assert economics.tithes == 4
    assert economics.notes == {"tithes": "Church"}


async def test_without_a_chosen_row_e_asks_which_row_to_edit():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_eco_section(pilot, app, "expenditure")
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, RemovalPickerScreen)
        await pilot.press("down", "enter")  # Consumables (the picker starts on row 0)
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        assert "Consumables" in str(app.screen.query_one("#fields-title").render())


async def test_cost_savings_rows_are_calculated_except_magic_and_emergency_savings():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_eco_row(pilot, app, "savings", 0)  # Laborers
        await pilot.press("e")
        await pilot.pause()
        assert not app.screen.query("#fld-magic_savings")
        await pilot.press("escape")
        await pilot.pause()

        await _select_eco_row(pilot, app, "savings", 2)  # Magic
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        _fill(app, magic_savings=6, notes="A self-sweeping broom")
        await _save_dialog(pilot, app)
        await wait_until(
            pilot, lambda: _eco_labels(app, "savings")[2].startswith("Magic 0 6")
        )

        await _select_eco_row(pilot, app, "savings", 3)  # Emergency Savings
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        _fill(app, emergency_savings=4)
        await _save_dialog(pilot, app)
        await wait_until(
            pilot,
            lambda: _eco_labels(app, "savings")[3].startswith("Emergency Savings 0 4"),
        )
        # 3 (laborers) + 6 + 4
        assert re.search(r"Cost Savings:\s+13\b", _eco_wealth(app))
        assert re.search(r"Total Expenditure:\s+8\b", _eco_wealth(app))  # 21 - 13

    economics = _saved_economics()
    assert (economics.magic_savings, economics.emergency_savings) == (6, 4)
    assert economics.notes == {"magic": "A self-sweeping broom"}


async def test_economics_follows_changes_made_on_other_tabs_and_keeps_the_chosen_row():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_eco_row(pilot, app, "expenditure", 3)  # Provisions
        assert "Cost: 9" in _eco_panel(app)

        # Four more turb on the Inhabitants tab: 17 -> 21 points.
        await _open_inh_section(pilot, app, "section-inh-turb")
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("enter")  # (New person)
        await pilot.pause()
        _fill(app, name="More Guards", quantity=4)
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(_inh_labels(app, "turb")) == 2)

        await _show_economics_tab(pilot, app)
        assert re.search(r"Points of Inhabitants:\s+21\b", _eco_wealth(app))
        view = _cov_view(app)
        assert view.selected_economics("expenditure") == 3  # still chosen
        await wait_until(pilot, lambda: "Cost: 11" in _eco_panel(app))
        assert "Name: Provisions" in _eco_panel(app)

        # The salary in Loyalty drives the Wages multiplier.
        view.covenant.loyalty.money = "Generous salary"
        view.refresh_section("section-inh-loyalty")
        assert "Wages (x1.5)" in _eco_labels(app, "expenditure")[4]


async def test_a_laboratorys_upkeep_and_a_weapons_type_feed_the_points():
    saga = _saga_with_bare_laboratory()
    saga.laboratories[0].characteristics = LabCharacteristics(upkeep=2)
    saga.covenants[0].possessions = [
        Possession(
            id="w",
            kind="weapon",
            name="Swords",
            quantity=10,
            gear_type="Weapon or shield",
            gear_quality="Expensive",
        )
    ]
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _show_economics_tab(pilot, app)
        wealth = _eco_wealth(app)
        assert re.search(r"Points of Laboratories:\s+30\b", wealth)  # Upkeep +2
        assert re.search(r"Points of Weapons and Armor:\s+160\b", wealth)  # 10 x 16


async def test_the_economics_forms_fit_an_80_by_24_terminal():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _select_covenant(pilot, app)
        await _open_eco_section(pilot, app, "income")
        await pilot.press("a")
        await pilot.pause()
        region = app.screen.query_one("#fields-dialog").region
        assert region.right <= 80 and region.bottom <= 24
        # The usual income of each type is shown as a hint.
        hints = " ".join(str(h.render()) for h in app.screen.query(".fd-hint"))
        assert "Lesser 40" in hints and "Legendary 1000" in hints
        await pilot.press("escape")
        await pilot.pause()

        await _open_eco_section(pilot, app, "expenditure")
        await pilot.press("e")
        await pilot.pause()
        await pilot.press("enter")  # the first row of the picker
        await pilot.pause()
        region = app.screen.query_one("#fields-dialog").region
        assert region.right <= 80 and region.bottom <= 24


async def test_the_economics_forms_do_not_stretch_on_a_tall_terminal():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_eco_section(pilot, app, "income")
        await pilot.press("a")
        await pilot.pause()
        assert app.screen.query_one("#fields-dialog").region.height < 30


def _save_sagas(*names: str) -> None:
    for name in names:
        storage.save_saga(
            Saga(id=storage.generate_saga_id(name), name=name, storyguide="Alex")
        )


def _picker_labels(app) -> list[str]:
    return [
        str(item.query_one(Label).render())
        for item in app.screen.query_one("#saga-list", ListView).children
    ]


async def test_A_deletes_the_highlighted_saga_only_after_confirmation():
    _save_sagas("Alpha", "[Beta] Saga", "Gamma")

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        list_view = app.screen.query_one("#saga-list", ListView)
        list_view.index = 1
        await pilot.pause()
        assert len(_picker_labels(app)) == 3
        assert _picker_labels(app)[1].startswith("[Beta] Saga")  # not read as markup

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert "Delete the saga [Beta] Saga?" in message  # brackets survive
        assert "cannot be undone" in message

        # No (and Escape) keep it; so does Enter on the default No.
        await pilot.press("n")
        await pilot.pause()
        assert storage.list_sagas() == ["alpha", "beta_saga", "gamma"]
        await pilot.press("A")
        await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()
        await pilot.press("A")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, SagaPickerScreen)
        assert storage.list_sagas() == ["alpha", "beta_saga", "gamma"]

        await pilot.press("A")
        await pilot.pause()
        await pilot.press("y")
        await wait_until(pilot, lambda: len(_picker_labels(app)) == 2)
        assert storage.list_sagas() == ["alpha", "gamma"]  # exactly that one
        assert [l.split("  ")[0] for l in _picker_labels(app)] == ["Alpha", "Gamma"]
        assert app.screen.query_one("#saga-list", ListView).index == 1  # stays put

        # Opening still works on what is left.
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)
        assert app.screen.saga.id == "gamma"


async def test_an_unreadable_saga_is_listed_and_can_be_deleted():
    # B2: one damaged file used to crash the picker on startup.
    _save_sagas("Alpha", "Gamma")
    (storage.SAGAS_DIR / "broken.json").write_text("{not json", encoding="utf-8")

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        labels = _picker_labels(app)
        assert labels[0].startswith("Alpha") and labels[2].startswith("Gamma")
        assert labels[1] == "broken  —  can't be read"

        # Opening it says why instead of crashing; the picker stays.
        list_view = app.screen.query_one("#saga-list", ListView)
        list_view.index = 1
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, SagaPickerScreen)

        await pilot.press("A")
        await pilot.pause()
        assert "Delete the saga broken?" in str(
            app.screen.query_one("#confirm-message", Static).render()
        )
        await pilot.press("y")
        await wait_until(pilot, lambda: storage.list_sagas() == ["alpha", "gamma"])


async def test_the_delete_key_works_and_deleting_the_last_saga_shows_the_placeholder():
    _save_sagas("Only")

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await pilot.press("delete")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await wait_until(pilot, lambda: storage.list_sagas() == [])
        await wait_until(
            pilot, lambda: any("No sagas yet" in l for l in _picker_labels(app))
        )
        assert len(_picker_labels(app)) == 1

        # Nothing left to delete: no dialog, just a notice.
        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, SagaPickerScreen)


async def test_a_saga_can_still_be_created_after_deleting_all_of_them():
    _save_sagas("Old")

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await pilot.press("A")
        await pilot.pause()
        await pilot.press("y")
        await wait_until(pilot, lambda: storage.list_sagas() == [])

        await pilot.press("n")
        await pilot.pause()
        assert _is_form(app.screen, "Create a New Saga")
        app.screen.query_one("#fld-name", Input).value = "Old"  # the same name
        app.screen.query_one("#fld-storyguide", Input).value = "Alex"
        app.screen.query_one("#fld-year", Input).value = "1220"
        await pilot.click("#btn-save")
        await pilot.pause()
        assert isinstance(app.screen, SagaPickerScreen)

    assert storage.list_sagas() == ["old"]


# -- Books: covenant Library tab, laboratory/character Books, Unassigned Books ---


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


async def _show_library_tab(pilot, app) -> None:
    """Open the covenant's Library tab and focus its Books section."""
    view = app.screen._covenant_sheet_view
    await wait_until(pilot, lambda: view.initial_tab_seen)
    await pilot.pause()
    view.query_one(TabbedContent).active = "tab-cov-library"
    await pilot.pause()
    view.query_one("#section-lib-books", Collapsible).query_one(
        "CollapsibleTitle"
    ).focus()
    await wait_until(pilot, lambda: app.screen._active_section() == "section-lib-books")


def _book_names(app) -> list[str]:
    view = app.screen._book_view()
    return [b.name for b in view.books] if view is not None else []


def _books_panel(app) -> str:
    view = app.screen._book_view()
    return str(view.query_one(".books-panel", Static).render())


async def _choose_book(pilot, app, row: int) -> None:
    rows = app.screen._book_view().query_one(SelectableList)
    rows.focus()
    await pilot.pause()
    rows.highlighted = row
    await pilot.pause()


def _saved_books() -> dict[str, Book]:
    return {b.id: b for b in storage.load_saga("test_saga").books}


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
        assert section.title == "Books (3) - 44 Build Points"  # 32 + 4 + 8

        assert "Select a book" in _books_panel(app)
        await _choose_book(pilot, app, 0)
        panel = _books_panel(app)
        assert "Name: Summa of Flame" in panel
        assert "Cost: 32 Build Points (Level 15 + Quality 17)" in panel
        assert "Quality 17 is over the covenant-creation limit of 16." in panel
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
        assert section.title == "Books (1) - 22 Build Points"

    saved = next(b for b in _saved_books().values() if b.name == "Summa [Aquam]")
    assert (saved.type, saved.art, saved.level, saved.quality) == (
        "Art Summa",
        "Aquam",
        10,
        12,
    )
    assert (saved.owner_kind, saved.owner_id) == ("laboratory", "lab1")
    assert (saved.ability, saved.spell_name, saved.subject_kind) == ("", "", "")


async def _pick_spell(pilot, app, name: str) -> None:
    """In a book form, open the Spell picker, search for `name`, take the top
    match."""
    app.screen.query_one("#fld-spell_id", Button).press()
    await wait_until(pilot, lambda: isinstance(app.screen, SpellChooserScreen))
    await pilot.pause()
    search = app.screen.query_one("#picker-search", Input)
    search.value = name
    await pilot.pause()
    search.focus()
    await pilot.press("enter")
    await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
    await pilot.pause()


async def test_book_form_shows_the_fields_the_type_needs():
    storage.save_saga(_sample_saga_with_covenant())

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
        assert "Cost: 5 Build Points" in live()
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


async def test_character_books_section_and_delete_confirms():
    storage.save_saga(_saga_with_books())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_character(pilot, app)
        view = app.screen._character_sheet_view
        view.query_one(TabbedContent).active = "tab-inventory"
        await pilot.pause()
        section = view.query_one("#section-books", Collapsible)
        assert section.title == "Books (1) - 8 Build Points"
        assert _book_names(app) == ["Pocket Tract"]
        await _choose_book(pilot, app, 0)
        assert app.screen._active_section() == "section-books"
        assert "Owner: Character: Leandro" in _books_panel(app)
        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("n")
        await pilot.pause()
        assert _book_names(app) == ["Pocket Tract"]
        await pilot.press("A")
        await pilot.pause()
        await pilot.press("y")
        await wait_until(pilot, lambda: _book_names(app) == [])
        # Nothing left: 'A' says so instead of opening an empty picker.
        await pilot.press("A")
        await pilot.pause()
        assert not isinstance(app.screen, RemovalPickerScreen)

    assert "b3" not in _saved_books()


async def test_book_form_fits_a_small_terminal():
    storage.save_saga(_saga_with_books())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _select_covenant(pilot, app)
        await _show_library_tab(pilot, app)
        await _choose_book(pilot, app, 0)
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        for button in app.screen.query("#btn-save, #btn-cancel"):
            assert button.region.height > 0 and button.region.bottom <= 24, button.id


# -- Importing books from a CSV file ---------------------------------------------

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


async def _pick_csv(pilot, app, path: str) -> None:
    """In the file picker, type the file's path and press Enter."""
    await wait_until(pilot, lambda: isinstance(app.screen, CsvFilePickerScreen))
    await pilot.pause()  # let it mount first: mounting moves the focus
    box = app.screen.query_one("#picker-path", Input)
    box.value = path
    box.focus()
    await pilot.press("enter")
    await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))


async def test_saga_import_offers_books_and_spells_and_files_books_unassigned(tmp_path):
    storage.save_saga(_sample_saga_with_covenant())
    csv_path = _write_books_csv(tmp_path)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _open_workspace(pilot)
        await pilot.press("I")
        await wait_until(pilot, lambda: isinstance(app.screen, ImportScreen))
        options = app.screen.query_one("#import-list", OptionList)
        kinds = [options.get_option_at_index(i) for i in range(options.option_count)]
        assert [(o.id, o.disabled) for o in kinds] == [
            ("characters", True),
            ("covenants", True),
            ("laboratories", True),
            ("books", False),
            ("spells", False),
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
        await pilot.press("I")  # straight to the file picker: only books go here
        await _pick_csv(pilot, app, csv_path)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert "into Test Covenant's library?" in message
        await pilot.press("n")  # declining imports nothing
        await pilot.pause()
        assert len(_book_names(app)) == before

        await pilot.press("I")
        await _pick_csv(pilot, app, csv_path)
        await pilot.press("y")
        await wait_until(pilot, lambda: len(_book_names(app)) == before + 3)
        assert _book_names(app)[-3:] == ["On Flame", "Notes", "Pilum"]
        assert (
            _find_node(app.screen.query_one("#nav-tree", Tree), ("book_group",)) is None
        )

    imported = [b for b in _saved_books().values() if b.name in ("On Flame", "Notes")]
    assert {(b.owner_kind, b.owner_id) for b in imported} == {("covenant", "cov1")}


async def test_import_key_only_where_books_can_be_imported():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        assert app.screen.check_action("import_data", ()) is False  # info panel
        await _show_library_tab(pilot, app)
        assert app.screen.check_action("import_data", ()) is True


async def test_file_picker_browses_folders_and_rejects_other_files(tmp_path):
    storage.save_saga(_sample_saga_with_covenant())
    (tmp_path / "sub").mkdir()
    (tmp_path / "notes.txt").write_text("hi", encoding="utf-8")
    _write_books_csv(tmp_path / "sub")

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _open_workspace(pilot)
        await pilot.press("I")
        await wait_until(pilot, lambda: isinstance(app.screen, ImportScreen))
        await pilot.press("enter")
        await wait_until(pilot, lambda: isinstance(app.screen, CsvFilePickerScreen))
        picker = app.screen
        for button in picker.query(Button):  # fits a small terminal
            assert button.region.height > 0 and button.region.bottom <= 24, button.id

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


# -- Books: several at once, and duplicates on import ----------------------------


async def _mark_books(pilot, app, rows: list[int]) -> None:
    """Mark rows of the book list with Space."""
    rows_list = app.screen._book_view().query_one(SelectableList)
    rows_list.focus()
    await pilot.pause()
    for row in rows:
        rows_list.highlighted = row
        await pilot.press("space")
    await pilot.pause()


async def test_space_marks_books_and_A_deletes_them_all_after_confirming():
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

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert message == "Are you sure you want to delete 2 books?"
        await pilot.press("n")
        await pilot.pause()
        assert len(_book_names(app)) == 3
        await pilot.press("A")
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
    await pilot.press("I")
    await _pick_csv(pilot, app, csv_path)
    await pilot.press("y")
    for answer in answers:
        await wait_until(pilot, lambda: isinstance(app.screen, DuplicateBookScreen))
        app.screen.query_one(f"#btn-{answer}", Button).press()
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
        await pilot.press("I")
        await wait_until(pilot, lambda: isinstance(app.screen, ImportScreen))
        await pilot.press("enter")
        await _pick_csv(pilot, app, csv_path)
        await pilot.press("y")
        await wait_until(pilot, lambda: isinstance(app.screen, DuplicateBookScreen))
        message = str(app.screen.query_one("#duplicate-message", Static).render())
        assert "A book named On Flame is already in the saga" in message
        assert "2 more duplicate(s) after this one." in message
        assert app.screen.focused.id == "btn-skip"  # the safe answer
        app.screen.query_one("#btn-duplicate", Button).press()  # add On Flame
        await pilot.pause()
        app.screen.query_one("#btn-skip-all", Button).press()  # skip the rest
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
        await _import_with_answers(pilot, app, csv_path, ["skip", "duplicate-all"])
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
        assert "Total Books:     3" in right
        assert "Total Cost:      44 Build Points" in right

        # The list runs down to the details panel, two rows above it (the
        # section's bottom padding and the panel's margin).
        section = view.query_one("#section-lib-books", Collapsible)
        panel = app.screen._book_view().query_one(".books-panel", Static)
        assert panel.region.y - section.region.bottom == 1
        assert view.query_one("#section-lib-books-list").region.height > 10

        # Nothing to edit or remove on the Summary; adding a book still works.
        view.query_one("#section-lib-summary", Collapsible).query_one(
            "CollapsibleTitle"
        ).focus()
        await wait_until(
            pilot, lambda: app.screen._active_section() == "section-lib-summary"
        )
        assert app.screen.check_action("edit", ()) is False
        assert app.screen.check_action("remove", ()) is False
        assert app.screen.check_action("add", ()) is True

        # The summary follows edits.
        await _choose_book(pilot, app, 0)
        await pilot.press("A")
        await pilot.pause()
        await pilot.press("y")
        await wait_until(pilot, lambda: len(_book_names(app)) == 2)
        right = str(view.query_one("#lib-summary-right", Static).render())
        assert "Total Books:     2" in right


async def test_the_subject_column_widens_with_the_terminal():
    saga = _saga_with_books()
    saga.books[0].art = "Ignem"
    saga.books[2].ability = "Area Lore: The Rhine Tribunal and its Environs"
    storage.save_saga(saga)

    for width, expected in ((110, 17), (140, 23), (200, 40)):
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


# -- Emergency Savings and the year's end -----------------------------------------


def _saga_with_a_deficit(deficit: int, wealth: int) -> Saga:
    saga = _saga_for_economics()
    cov = saga.covenants[0]
    cov.economics.tithes = 0
    cov.economics.tithes = eco.summarize(saga, cov).surplus_deficit + deficit
    cov.economics.wealth = wealth
    return saga


async def _edit_emergency_savings(pilot, app) -> None:
    view = app.screen._covenant_sheet_view
    rows = view.query_one("#eco-savings-list", SelectableList)
    await _select_eco_row(pilot, app, "savings", len(rows._rows) - 1)
    await pilot.press("e")
    await pilot.pause()


async def test_editing_emergency_savings_offers_to_draw_from_wealth():
    storage.save_saga(_saga_with_a_deficit(36, wealth=100))

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _select_covenant(pilot, app)
        await _edit_emergency_savings(pilot, app)
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert message.startswith(
            "Do you wish to draw from Wealth to cover the deficit?"
        )
        assert "Deficit: 36    Wealth: 100" in message
        await pilot.press("y")
        await wait_until(pilot, lambda: _saved_economics().emergency_savings == 36)
        assert _saved_economics().wealth == 64
        rows = app.screen._covenant_sheet_view.query_one(
            "#eco-savings-list", SelectableList
        )
        assert "deficit" not in rows._rows[-1][1]  # covered: the warning goes


async def test_declining_the_draw_opens_the_ordinary_form():
    storage.save_saga(_saga_with_a_deficit(36, wealth=100))

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _select_covenant(pilot, app)
        await _edit_emergency_savings(pilot, app)
        await pilot.press("n")
        await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        assert app.screen.query_one("#fld-emergency_savings", Input).value == "0"
        await pilot.press("escape")
        await pilot.pause()
    assert (_saved_economics().emergency_savings, _saved_economics().wealth) == (0, 100)


async def test_a_short_draw_empties_wealth_and_the_covenant_is_broke():
    storage.save_saga(_saga_with_a_deficit(36, wealth=10))

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _select_covenant(pilot, app)
        await _edit_emergency_savings(pilot, app)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert "Wealth only covers 10 of it" in message
        assert "26 stays uncovered" in message
        await pilot.press("y")
        await wait_until(pilot, lambda: _saved_economics().wealth == 0)
        assert _saved_economics().emergency_savings == 10
        rows = app.screen._covenant_sheet_view.query_one(
            "#eco-savings-list", SelectableList
        )
        assert "Covenant is broke" in rows._rows[-1][1]
        # With no Wealth left there's nothing to offer: straight to the form.
        await _edit_emergency_savings(pilot, app)
        assert isinstance(app.screen, FieldsDialog)


async def test_the_new_year_adds_each_covenants_surplus_to_its_wealth():
    saga = _saga_for_economics()
    saga.current_season = "Winter"
    cov = saga.covenants[0]
    cov.economics.wealth = 5
    cov.economics.emergency_savings = 3
    surplus = eco.summarize(saga, cov).surplus_deficit
    assert surplus > 0
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open_workspace(pilot)
        await pilot.press("t")
        await pilot.pause()
        assert isinstance(app.screen, AdvanceSeasonScreen)
        note = str(app.screen.query_one("#advance-year-note", Static).render())
        assert "surplus is added to its Wealth" in note
        # The dialog hugs its content rather than filling the screen.
        assert app.screen.query_one("#advance-dialog").region.height < 20
        app.screen.query_one("#btn-advance", Button).press()
        await wait_until(pilot, lambda: _saved_economics().wealth == 5 + surplus)

    loaded = storage.load_saga("test_saga")
    assert (loaded.current_season, loaded.current_year) == ("Spring", 1221)
    assert loaded.covenants[0].economics.emergency_savings == 0


async def test_other_seasons_leave_wealth_alone():
    saga = _saga_for_economics()
    saga.current_season = "Autumn"
    saga.covenants[0].economics.wealth = 5
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open_workspace(pilot)
        await pilot.press("t")
        await pilot.pause()
        assert not app.screen.query("#advance-year-note")
        app.screen.query_one("#btn-advance", Button).press()
        await wait_until(
            pilot, lambda: storage.load_saga("test_saga").current_season == "Winter"
        )
    assert _saved_economics().wealth == 5


async def _advance_from_winter(pilot, app) -> None:
    """Press t and confirm the Advance Time dialog."""
    await pilot.press("t")
    await wait_until(pilot, lambda: isinstance(app.screen, AdvanceSeasonScreen))
    app.screen.query_one("#btn-advance", Button).press()
    await pilot.pause()


def _winter_saga_with_a_deficit() -> Saga:
    saga = _saga_with_a_deficit(36, wealth=100)
    saga.current_season = "Winter"
    return saga


async def test_rolling_the_year_over_in_deficit_offers_to_resolve_it_first():
    storage.save_saga(_winter_saga_with_a_deficit())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open_workspace(pilot)
        await _advance_from_winter(pilot, app)
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert message.startswith(
            "The Covenant is currently in a deficit - do you wish to attempt to "
            "resolve this?"
        )
        assert "Test Covenant: -36" in message
        # Yes is the safe answer here: it has the focus.
        assert app.screen.focused.id == "btn-yes"
        await pilot.press("y")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))

    saga = storage.load_saga("test_saga")
    assert (saga.current_season, saga.current_year) == ("Winter", 1220)
    assert saga.covenants[0].economics.wealth == 100


async def test_escape_at_the_deficit_prompt_also_keeps_the_year():
    storage.save_saga(_winter_saga_with_a_deficit())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open_workspace(pilot)
        await _advance_from_winter(pilot, app)
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("escape")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
    assert storage.load_saga("test_saga").current_season == "Winter"


async def test_answering_no_advances_the_year_regardless():
    storage.save_saga(_winter_saga_with_a_deficit())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open_workspace(pilot)
        await _advance_from_winter(pilot, app)
        await pilot.press("n")
        await wait_until(
            pilot, lambda: storage.load_saga("test_saga").current_season == "Spring"
        )

    saga = storage.load_saga("test_saga")
    assert saga.current_year == 1221
    # The deficit isn't taken from Wealth by itself.
    assert saga.covenants[0].economics.wealth == 100


async def test_no_deficit_prompt_without_a_deficit_or_outside_winter():
    saga = _saga_for_economics()  # a surplus
    saga.current_season = "Winter"
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open_workspace(pilot)
        await _advance_from_winter(pilot, app)
        await wait_until(
            pilot, lambda: storage.load_saga("test_saga").current_season == "Spring"
        )
        assert not isinstance(app.screen, ConfirmScreen)

    saga = _saga_with_a_deficit(36, wealth=100)
    saga.current_season = "Autumn"  # a deficit, but not the year's end
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open_workspace(pilot)
        await _advance_from_winter(pilot, app)
        await wait_until(
            pilot, lambda: storage.load_saga("test_saga").current_season == "Winter"
        )


# -- The saga's Spells view ------------------------------------------------------


async def _open_spells(pilot, app) -> SpellListView:
    await _open_workspace(pilot)
    await _select(pilot, app, ("spells",))
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
        tree = app.screen.query_one("#nav-tree", Tree)
        assert str(_find_node(tree, ("spells",)).label) == f"Spells ({total})"
        view = await _open_spells(pilot, app)
        section = view.query_one("#section-spells", Collapsible)
        assert section.title == f"Spells ({total} of {total})"

        view.query_one("#spell-search", Input).value = "pilum"
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
    total = len(catalog.load_spell_catalog())

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
        tree = app.screen.query_one("#nav-tree", Tree)
        assert str(_find_node(tree, ("spells",)).label) == f"Spells ({total + 1})"
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

        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await wait_until(pilot, lambda: app.screen.saga.spells == [])
        assert _shown_names(view) == []

    assert storage.load_saga("test_saga").spells == []


# -- Lab Texts and Casting Tablets link to spells ----------------------------------


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
        assert "Cost: 4 Build Points" in live and "Level 20, from the spell" in live
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


async def test_importing_lab_texts_links_them_to_their_spells(tmp_path):
    storage.save_saga(_sample_saga_with_covenant())
    csv_path = tmp_path / "texts.csv"
    csv_path.write_text(
        "name,type,level,spell\n"
        "Pilum notes,Lab Text,,pilum of fire\n"
        "Mystery notes,Lab Text,15,The Lost Art\n",
        encoding="utf-8",
    )

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _select_covenant(pilot, app)
        await _show_library_tab(pilot, app)
        await pilot.press("I")
        await _pick_csv(pilot, app, str(csv_path))
        await pilot.press("y")
        await wait_until(pilot, lambda: "Mystery notes" in _book_names(app))
        labels = [label for _, label in app.screen._book_view()._rows()]
        mystery = next(label for label in labels if "Mystery notes" in label)
        assert mystery.startswith("[red]")  # Unknown spell

    saved = {b.name: b for b in _saved_books().values()}
    assert saved["Pilum notes"].spell_id == "spell_pilum_of_fire"
    assert (saved["Mystery notes"].spell_id, saved["Mystery notes"].level) == (None, 15)


# -- Importing spells from a CSV file ---------------------------------------------


async def test_import_data_offers_spells_with_a_helper_and_an_example_file(
    tmp_path, monkeypatch
):
    storage.save_saga(_sample_saga_with_covenant())
    monkeypatch.chdir(tmp_path)  # the app's folder: where the example goes

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        await _open_workspace(pilot)
        await pilot.press("I")
        await wait_until(pilot, lambda: isinstance(app.screen, ImportScreen))
        options = app.screen.query_one("#import-list", OptionList)
        options.highlighted = next(
            i
            for i in range(options.option_count)
            if options.get_option_at_index(i).id == "spells"
        )
        await pilot.press("enter")
        await wait_until(pilot, lambda: isinstance(app.screen, SpellImportHelperScreen))
        helper = str(app.screen.query_one("#spell-import-help", Static).render())
        assert "technique" in helper and "Gen (or blank)" in helper

        app.screen.query_one("#btn-spell-import-example", Button).press()
        await pilot.pause()
        example = tmp_path / "spells_example.csv"
        assert example.read_text(encoding="utf-8") == spl.EXAMPLE_CSV
        status = str(app.screen.query_one("#spell-import-status", Static).render())
        assert "Saved spells_example.csv" in status
        # A second save doesn't overwrite the first.
        app.screen.query_one("#btn-spell-import-example", Button).press()
        await pilot.pause()
        assert (tmp_path / "spells_example_2.csv").exists()

        app.screen.query_one("#btn-spell-import-choose", Button).press()
        await _pick_csv(pilot, app, str(example))
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert "Import 2 spells from spells_example.csv" in message
        await pilot.press("y")
        await wait_until(pilot, lambda: len(app.screen.saga.spells) == 3)
        tree = app.screen.query_one("#nav-tree", Tree)
        total = len(catalog.load_spell_catalog()) + 3
        assert str(_find_node(tree, ("spells",)).label) == f"Spells ({total})"

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
        for answers in ([], ["skip-all"]):
            app.screen._import_spells()
            await wait_until(
                pilot, lambda: isinstance(app.screen, SpellImportHelperScreen)
            )
            await pilot.pause()
            app.screen.query_one("#btn-spell-import-choose", Button).press()
            await _pick_csv(pilot, app, str(csv_path))
            await pilot.press("y")
            for answer in answers:
                await wait_until(
                    pilot, lambda: isinstance(app.screen, DuplicateBookScreen)
                )
                message = str(
                    app.screen.query_one("#duplicate-message", Static).render()
                )
                assert "A spell named Palm of Warming Flame" in message
                app.screen.query_one(f"#btn-{answer}", Button).press()
                await pilot.pause()
            await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
            await pilot.pause()
        assert len(app.screen.saga.spells) == 2  # the second import added none


async def test_a_spell_import_asks_about_a_name_in_another_case(tmp_path):
    # B1: the preview counts "palm of warming flame" as a duplicate of
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
        app.screen._import_spells()
        await wait_until(pilot, lambda: isinstance(app.screen, SpellImportHelperScreen))
        await pilot.pause()
        app.screen.query_one("#btn-spell-import-choose", Button).press()
        await _pick_csv(pilot, app, str(csv_path))
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert "1 has the same name as another spell" in message
        await pilot.press("y")
        await wait_until(pilot, lambda: isinstance(app.screen, DuplicateBookScreen))
        app.screen.query_one("#btn-skip", Button).press()
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        assert [s.name for s in app.screen.saga.spells] == ["Palm of Warming Flame"]


async def test_the_spell_import_helper_fits_a_small_terminal():
    storage.save_saga(_sample_saga_with_covenant())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await _open_workspace(pilot)
        app.screen._import_spells()
        await wait_until(pilot, lambda: isinstance(app.screen, SpellImportHelperScreen))
        await pilot.pause()
        for button in app.screen.query(Button):
            assert button.region.height > 0 and button.region.bottom <= 24, button.id
