"""Helpers shared by the test_screens_*.py tests: sample sagas, waiting for
screens and pickers, opening sections and reading what a sheet shows."""

from support import strip_markup, wait_until
from textual.widgets import (
    Button,
    Collapsible,
    Input,
    OptionList,
    Static,
    TabbedContent,
    TextArea,
    Tree,
)

from ars_magica_manager import storage
from ars_magica_manager.models import (
    LAB_CHARACTERISTICS,
    Ability,
    ArtScore,
    Background,
    Book,
    Character,
    Characteristics,
    Covenant,
    Familiar,
    HermeticBackground,
    KnownSpell,
    LabCharacteristics,
    LabFeature,
    Laboratory,
    Possession,
    Saga,
    Spell,
    Tribunal,
    VirtueFlawInstance,
)
from ars_magica_manager.tui.screens import (
    ConfirmScreen,
    CsvFilePickerScreen,
    FieldsDialog,
    SelectableList,
    SpellChooserScreen,
    WorkspaceScreen,
)
from ars_magica_manager.tui.screens.widgets import section_stop


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
    for that before typing, so the keys land in the search box."""
    await wait_until(
        pilot,
        lambda: app.focused is not None and app.focused.id == "picker-search",
        timeout=10.0,  # building a picker is slow under a parallel run
    )


async def _wait_until_active(pilot, app, section_id: str) -> None:
    """Wait for `section_id` to be what a / e / d dispatch to, and fail clearly
    if it never becomes so."""
    await wait_until(pilot, lambda: app.screen._active_section() == section_id)
    assert app.screen._active_section() == section_id, (
        f"{section_id!r} never became the active section "
        f"(got {app.screen._active_section()!r})"
    )


async def _focus_section(pilot, app, collapsible, section_id: str) -> None:
    """Focus `collapsible` until `section_id` is what a / e / d act on, and
    stays so. Under load a sheet's own first focus can land after ours and
    take it back, so focus again whenever it has moved, rather than trusting
    one focus() and a pause."""
    stop = section_stop(collapsible)
    held = 0
    for _ in range(500):  # 10 s at 0.02 s a step
        if app.screen._active_section() == section_id:
            held += 1
            if held >= 3:
                return
        else:
            held = 0
            stop.focus()
        await pilot.pause(0.02)
    raise AssertionError(
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
    """Select a nav-tree node by its `.data`, the same way a click/enter would.
    A sheet shows only its first tab: other tabs are built when a test shows
    them, or by `build_all_tabs` for a test that reaches into one unseen."""
    tree = app.screen.query_one("#nav-tree", Tree)
    node = _find_node(tree, data)
    assert node is not None, f"tree node with data={data!r} not found"
    tree.select_node(node)
    await pilot.pause()
    attr = _SHEET_VIEW_ATTR.get(data[0])
    if attr is not None:
        await wait_until(pilot, lambda: getattr(app.screen, attr) is not None)
        view = getattr(app.screen, attr)
        await wait_until(pilot, lambda: view.initial_tab_seen)
        await pilot.pause()


async def _open_workspace(pilot) -> None:
    await pilot.press("enter")  # picker -> workspace
    await pilot.pause()


async def _select_vf_picker_entry(pilot, app, vf_id: str) -> None:
    """Highlight and activate a VirtueFlawPickerScreen entry by catalog id.

    The catalog now has 600+ entries, so most are well outside the picker
    dialog's visible/scrolled area -- pixel-coordinate pilot.click() raises
    OutOfBounds for anything not currently on screen. Highlighting it and
    pressing enter selects it the same way a real click/enter would,
    without needing the item to be visible.
    """
    target_id = f"vf-{vf_id}"
    if target_id not in app.screen.shown_ids():
        raise AssertionError(f"{target_id!r} not found in Virtue/Flaw picker list")
    app.screen.highlight(target_id)
    app.screen.query_one("#vf-picker-list").focus()
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
    joined -- Abilities is one selectable list, not one text blob. Each is
    plain text with its column padding collapsed: "Brawl 4 (6) 50/75"."""
    return " | ".join(
        _plain(label) for index, label in view._ability_rows() if index is not None
    )


def _plain(label: str) -> str:
    """A list row as plain text with runs of spaces collapsed."""
    return " ".join(strip_markup(label).split())


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
    "section-char-agents": "tab-agents",
    "section-arts": "tab-hermetic",
    "section-raw-vis-hermetic": "tab-hermetic",
    "section-known-spells": "tab-hermetic",
    "section-research-goals": "tab-research",
    "section-research-log": "tab-research",
    "section-hermetic-background": "tab-description",
}


async def _open_section(pilot, app, section_id: str) -> None:
    """Switch to the tab containing `section_id` and focus that section.

    The generic Add/Remove/Edit bindings dispatch by whichever Collapsible
    section currently has focus (its title, since CollapsibleTitle is the
    focusable part -- see WorkspaceScreen._active_section()), so
    most character-mutation tests need this before pressing
    a / e / d. `section_id` may also be "tab-abilities", the one
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
        await _focus_section(pilot, app, collapsible, section_id)
    await _wait_until_active(pilot, app, section_id)


#: Same idea as _SECTION_TAB, for the laboratory sheet.
_LAB_SECTION_TAB: dict[str, str] = {
    "section-lab-identity": "tab-lab-planning",  # top panel, not inside any tab
    "section-lab-characteristics": "tab-lab-planning",
    "tab-lab-planning": "tab-lab-planning",
    "section-lab-vf-virtues": "tab-lab-vf",
    "section-lab-vf-flaws": "tab-lab-vf",
    "section-lab-specializations": "tab-lab-attributes",
    "section-lab-specialties": "tab-lab-attributes",
    "section-lab-features": "tab-lab-attributes",
    "section-lab-magic-items": "tab-lab-attributes",
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
        await _focus_section(pilot, app, collapsible, section_id)
        return
    tab_id = _LAB_SECTION_TAB[section_id]
    view.query_one(TabbedContent).active = tab_id
    await pilot.pause()
    if section_id != tab_id:
        collapsible = view.query_one(f"#{section_id}", Collapsible)
        await _focus_section(pilot, app, collapsible, section_id)
    else:
        # A flat tab: wait for the tab switch to clear focus so dispatch
        # resolves to the tab itself.
        await wait_until(pilot, lambda: app.screen._active_section() == section_id)


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
    await _open_workspace(pilot)
    await _select(pilot, app, ("character", character_id))


async def _select_laboratory(pilot, app, laboratory_id: str = "lab1") -> None:
    await _open_workspace(pilot)
    await _select(pilot, app, ("laboratory", laboratory_id))


def _lab_identity_text(view) -> str:
    """The lab's Identity panel as one text -- the title (the lab's name),
    both columns and the Aura line -- with the label padding collapsed, so
    "Owner: Leandro" matches however wide the column's labels are."""
    parts = (
        str(view.query_one("#section-lab-identity", Collapsible).title),
        view._identity_left_text(),
        view._identity_right_text(),
        view._aura_text(),
    )
    return "\n".join(
        " ".join(line.split())
        for part in parts
        for line in strip_markup(part).splitlines()
    )


def _lab_rows(view, list_id: str) -> list[str]:
    """A lab sheet list's rows as displayed (markup stripped)."""
    selectable = view.query_one(f"#{list_id}", SelectableList)
    return [strip_markup(label).replace("\\[", "[") for _, label in selectable._rows]


async def _choose_lab_row(pilot, view, list_id: str, data_index: int) -> None:
    """Choose a lab sheet list's row by data index, as a click would."""
    assert view.query_one(f"#{list_id}", SelectableList).select_data_index(data_index)
    await pilot.pause()


async def _confirm(pilot, app, answer: str) -> None:
    """Answer the delete confirmation ("y"/"n") and wait to be back."""
    assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
    await pilot.press(answer)
    await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))


def _lab_characteristics_text(view) -> str:
    """Both columns of the 8 Characteristics, Size first."""
    return "\n".join(
        (
            view._characteristics_column_text(LAB_CHARACTERISTICS[:4]),
            view._characteristics_column_text(LAB_CHARACTERISTICS[4:]),
        )
    )


async def _select_familiar(pilot, app, familiar_id: str = "fam1") -> None:
    await _open_workspace(pilot)
    await _select(pilot, app, ("familiar", familiar_id))


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
                aura=3,
                possessions=[
                    Possession(
                        id="vis_store_ignem",
                        kind="vis_store",
                        name="Ignem Vis",
                        art="Ignem",
                        pawns=5,
                    )
                ],
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
                    "creo": ArtScore(xp=55),
                    "ignem": ArtScore(xp=15),
                },
                abilities=[
                    Ability(
                        name="Magic Theory",
                        category="Academic",
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
                features=[LabFeature("feat1", "Well-Stocked")],
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
    its a / e / d keys apply). Same idea as the character sheet's own
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
        await _focus_section(pilot, app, collapsible, section_id)
    await _wait_until_active(pilot, app, section_id)


def _saga_with_configured_covenant() -> Saga:
    saga = _saga_with_bare_laboratory()
    saga.name = "Pushing the Bounds"
    saga.storyguide = "Hedda"
    saga.current_season = "Spring"
    saga.current_year = 1220
    cov = saga.covenants[0]
    saga.tribunals.append(Tribunal(id="rhine", name="Rhine"))
    cov.tribunal_id = "rhine"
    cov.year_founded = 1100
    cov.aegis_of_the_hearth = 2
    cov.aegis_penetration = 1
    cov.living_conditions_magi = 3
    cov.living_conditions_mundane = -1
    cov.aura = 4
    cov.covenant_season = "Summer"
    return saga


async def _open_cov_section(pilot, app, section_id: str) -> None:
    """Focus one of the covenant Attributes tab's sections, after letting the
    view's own initial focus settle (see _open_lab_section)."""
    view = app.screen._covenant_sheet_view
    assert view is not None, "no covenant sheet is currently shown"
    await wait_until(pilot, lambda: view.initial_tab_seen)
    await pilot.pause()
    view.query_one(TabbedContent).active = "tab-cov-overview"
    await pilot.pause()
    collapsible = view.query_one(f"#{section_id}", Collapsible)
    await _focus_section(pilot, app, collapsible, section_id)


async def _choose_in_list(pilot, app, list_id: str, item_id: str) -> None:
    """Highlight and activate one entry of a picker list by item id (it may
    be off-screen, so no pixel clicking)."""
    picker = app.screen
    assert picker.LIST_VIEW_ID == list_id
    if item_id not in picker.shown_ids():
        raise AssertionError(f"{item_id!r} not found in {list_id!r}")
    picker.highlight(item_id)
    picker.query_one(f"#{list_id}").focus()
    await pilot.pause()
    await pilot.press("enter")
    await pilot.pause()


def _plain_title(section) -> str:
    """A Collapsible's title as displayed (colour markup stripped)."""
    return section.query_one("CollapsibleTitle").label.plain


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
    """Focus a section of the Inhabitants tab (so its a / e / d keys apply)."""
    await _show_inhabitants_tab(pilot, app)
    view = app.screen._covenant_sheet_view
    collapsible = view.query_one(f"#{section_id}", Collapsible)
    await _focus_section(pilot, app, collapsible, section_id)


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


def _cov_view(app):
    return app.screen._covenant_sheet_view


def _inh_labels(app, kind: str) -> list[str]:
    return [label for _, label in _cov_view(app)._inh_rows(kind)]


async def _show_library_tab(pilot, app) -> None:
    """Open the covenant's Library tab and focus its Books section."""
    view = app.screen._covenant_sheet_view
    await wait_until(pilot, lambda: view.initial_tab_seen)
    await pilot.pause()
    view.query_one(TabbedContent).active = "tab-cov-library"
    await pilot.pause()
    section_stop(view.query_one("#section-lib-books", Collapsible)).focus()
    await wait_until(pilot, lambda: app.screen._active_section() == "section-lib-books")


def _book_names(app) -> list[str]:
    view = app.screen._book_view()
    return [b.name for b in view.books] if view is not None else []


def _saved_books() -> dict[str, Book]:
    return {b.id: b for b in storage.load_saga("test_saga").books}


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


async def _pick_csv(pilot, app, path: str) -> None:
    """In the file picker, type the file's path and press Enter."""
    await wait_until(pilot, lambda: isinstance(app.screen, CsvFilePickerScreen))
    await pilot.pause()  # let it mount first: mounting moves the focus
    box = app.screen.query_one("#picker-path", Input)
    box.value = path
    box.focus()
    await pilot.press("enter")
    await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
