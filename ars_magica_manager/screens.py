"""Saga picker/creator screens. See DESIGN.md section 7, Phase 1."""

from __future__ import annotations

from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.events import DescendantBlur, DescendantFocus, Key
from textual.screen import ModalScreen, Screen
from textual.widget import Widget
from textual.widgets import (
    Button,
    Checkbox,
    Collapsible,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Select,
    Static,
    TabbedContent,
    TabPane,
    Tree,
)

from . import catalog, storage
from .models import (
    ABILITY_CATEGORIES,
    ART_ABBREVIATIONS,
    FATIGUE_LEVELS,
    FORMS,
    LAB_CHARACTERISTICS,
    SEASONS,
    TECHNIQUES,
    Ability,
    AbilityDef,
    Aging,
    ArtScore,
    Background,
    Character,
    Characteristics,
    Covenant,
    Description,
    DiaryEntry,
    FatigueLevel,
    HermeticBackground,
    LabCharacteristics,
    Laboratory,
    LabVirtueFlawDef,
    Library,
    NamedDescription,
    Saga,
    ScoredTrait,
    Spell,
    VirtueFlawDef,
    VirtueFlawInstance,
    Wounds,
    character_age,
    lab_base_safety,
    lab_characteristic_total,
    lab_free_virtues,
    lab_occupied_size,
)

_SAGA_ITEM_ID_PREFIX = "saga-"
_VIRTUE_FLAW_ITEM_ID_PREFIX = "vf-"
_LAB_VIRTUE_FLAW_ITEM_ID_PREFIX = "labvf-"
_ABILITY_ITEM_ID_PREFIX = "ability-"
_REMOVAL_ITEM_ID_PREFIX = "remove-"
_SPELL_ITEM_ID_PREFIX = "spell-"


class SagaCreateScreen(ModalScreen[str | None]):
    """A form for creating a new saga. Dismisses with the new saga's id, or None if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    SagaCreateScreen {
        align: center middle;
    }

    #create-dialog {
        width: 64;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #create-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="create-dialog"):
            yield Label("Create a New Saga", id="create-title")
            yield Label("Saga name")
            yield Input(placeholder="e.g. Dammerstein", id="input-name")
            yield Label("Storyguide name")
            yield Input(placeholder="e.g. Alex", id="input-storyguide")
            with Horizontal():
                yield Input(value="1220", type="integer", id="input-year")
                yield Select(
                    [(season, season) for season in SEASONS],
                    value=SEASONS[0],
                    allow_blank=False,
                    id="select-season",
                )
            yield Label("Description (optional)")
            yield Input(
                placeholder="A one-line premise for the saga",
                id="input-description",
            )
            yield Static("", id="create-error")
            with Horizontal():
                yield Button("Create", id="btn-create", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-create":
            self._try_create()

    def _try_create(self) -> None:
        error = self.query_one("#create-error", Static)

        name = self.query_one("#input-name", Input).value.strip()
        if not name:
            error.update("Saga name is required.")
            return

        storyguide = self.query_one("#input-storyguide", Input).value.strip()
        if not storyguide:
            error.update("Storyguide name is required.")
            return

        year_raw = self.query_one("#input-year", Input).value.strip()
        try:
            year = int(year_raw)
        except ValueError:
            error.update("Start year must be a whole number.")
            return

        season = self.query_one("#select-season", Select).value
        if not isinstance(season, str):
            error.update("Start season is required.")
            return

        description = self.query_one("#input-description", Input).value.strip()

        saga = Saga(
            id=storage.generate_saga_id(name),
            name=name,
            storyguide=storyguide,
            description=description,
            current_year=year,
            current_season=season,
        )
        storage.save_saga(saga)
        self.dismiss(saga.id)


class CovenantCreateScreen(ModalScreen[str | None]):
    """Creates a covenant (with an empty library) within a saga.

    Dismisses with the new covenant's id, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    CovenantCreateScreen {
        align: center middle;
    }

    #create-dialog {
        width: 64;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #create-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, saga: Saga) -> None:
        super().__init__()
        self.saga = saga

    def compose(self) -> ComposeResult:
        with Vertical(id="create-dialog"):
            yield Label("Create a New Covenant", id="create-title")
            yield Label("Covenant name")
            yield Input(placeholder="e.g. Fengheld", id="input-name")
            yield Label("Notes (optional)")
            yield Input(
                placeholder="A one-line note about the covenant", id="input-notes"
            )
            yield Static("", id="create-error")
            with Horizontal():
                yield Button("Create", id="btn-create", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-create":
            self._try_create()

    def _try_create(self) -> None:
        error = self.query_one("#create-error", Static)

        name = self.query_one("#input-name", Input).value.strip()
        if not name:
            error.update("Covenant name is required.")
            return

        notes = self.query_one("#input-notes", Input).value.strip()

        covenant_id = storage.generate_unique_id(
            name, [c.id for c in self.saga.covenants]
        )
        # Every covenant gets an (initially empty) library -- there's no
        # separate "create library" step, since a covenant without one
        # isn't a meaningful state to leave dangling.
        library = Library(id=f"{covenant_id}_library", covenant_id=covenant_id)
        covenant = Covenant(
            id=covenant_id,
            saga_id=self.saga.id,
            name=name,
            notes=notes,
            library_id=library.id,
        )
        self.saga.covenants.append(covenant)
        self.saga.libraries.append(library)
        storage.save_saga(self.saga)
        self.dismiss(covenant_id)


class CharacterCreateScreen(ModalScreen[str | None]):
    """Creates a bare character: name, type, and covenant.

    Abilities, Virtues/Flaws, Arts, and lab assignment are left for later
    edit actions -- see DESIGN.md's Phase 1 forms slices. Dismisses with
    the new character's id, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    CharacterCreateScreen {
        align: center middle;
    }

    #create-dialog {
        width: 64;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #create-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    _CHARACTER_TYPES: ClassVar[list[tuple[str, str]]] = [
        ("Magus", "magus"),
        ("Companion", "companion"),
        ("Grog", "grog"),
    ]

    def __init__(self, saga: Saga, default_covenant_id: str | None = None) -> None:
        super().__init__()
        self.saga = saga
        self.default_covenant_id = default_covenant_id

    def compose(self) -> ComposeResult:
        with Vertical(id="create-dialog"):
            yield Label("Create a New Character", id="create-title")
            yield Label("Character name")
            yield Input(placeholder="e.g. Leandro", id="input-name")
            yield Label("Type")
            yield Select(
                self._CHARACTER_TYPES,
                value="magus",
                allow_blank=False,
                id="select-type",
            )
            yield Label("Covenant (optional)")
            yield Select(
                [(c.name, c.id) for c in self.saga.covenants],
                value=self.default_covenant_id or Select.NULL,
                allow_blank=True,
                prompt="(no covenant)",
                id="select-covenant",
            )
            yield Static("", id="create-error")
            with Horizontal():
                yield Button("Create", id="btn-create", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-create":
            self._try_create()

    def _try_create(self) -> None:
        error = self.query_one("#create-error", Static)

        name = self.query_one("#input-name", Input).value.strip()
        if not name:
            error.update("Character name is required.")
            return

        character_type = self.query_one("#select-type", Select).value
        if not isinstance(character_type, str):
            error.update("Type is required.")
            return

        covenant_value = self.query_one("#select-covenant", Select).value
        covenant_id = covenant_value if isinstance(covenant_value, str) else None

        character = Character(
            id=storage.generate_unique_id(name, [c.id for c in self.saga.characters]),
            name=name,
            type=character_type,
            covenant_id=covenant_id,
        )
        self.saga.characters.append(character)
        storage.save_saga(self.saga)
        self.dismiss(character.id)


class ParamPromptScreen(ModalScreen[dict[str, str] | None]):
    """Prompts for a catalog entry's placeholder parameters.

    Generic over any catalog entry shape that has a `name` (shown as a
    title) and a list of `parameters` to fill in -- e.g. VirtueFlawDef's
    "Affinity with {art}" needing "art", or AbilityDef's "Craft: {craft}"
    needing "craft". Dismisses with a dict of param name -> value, or
    None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    ParamPromptScreen {
        align: center middle;
    }

    #param-dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #param-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, prompt_title: str, parameters: list[str]) -> None:
        super().__init__()
        self.prompt_title = prompt_title
        self.parameters = parameters

    def compose(self) -> ComposeResult:
        with Vertical(id="param-dialog"):
            yield Label(self.prompt_title, id="param-title")
            for param in self.parameters:
                yield Label(param.title())
                yield Input(placeholder="e.g. Creo", id=f"input-param-{param}")
            yield Static("", id="param-error")
            with Horizontal():
                yield Button("Confirm", id="btn-confirm", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-confirm":
            self._try_confirm()

    def _try_confirm(self) -> None:
        error = self.query_one("#param-error", Static)
        params: dict[str, str] = {}
        for param in self.parameters:
            value = self.query_one(f"#input-param-{param}", Input).value.strip()
            if not value:
                error.update(f"{param.title()} is required.")
                return
            params[param] = value.lower()
        self.dismiss(params)


class SearchablePickerScreen(ModalScreen[Any]):
    """Base for a ListView-backed catalog picker with a live-filtering
    search box above it.

    The Ability and Virtue/Flaw catalogs are large (78 and 624 entries) --
    a flat unsearchable list doesn't scale, so both pickers share this:
    an Input above the ListView that re-filters it on every keystroke.
    Subclasses supply the entry list and how to search/render/activate
    each one; this owns the Input<->ListView wiring, so that trickier bit
    (live rebuild, keeping the search box focused and typable while
    letting Down/Enter reach the list) only has to be gotten right once.

    Subclasses override: `PICKER_TITLE`, `EMPTY_MESSAGE`,
    `SEARCH_PLACEHOLDER`, `LIST_VIEW_ID` (kept distinct per picker, not
    shared, so existing tests that query e.g. "#vf-picker-list" by id
    keep working) and the `_load_entries`/`_search_text`/`_label_for`/
    `_item_id`/`_on_entry_selected` hooks below.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    PICKER_TITLE: ClassVar[str] = "Pick"
    EMPTY_MESSAGE: ClassVar[str] = "(nothing available)"
    SEARCH_PLACEHOLDER: ClassVar[str] = "Search..."
    LIST_VIEW_ID: ClassVar[str] = "picker-list"

    DEFAULT_CSS = """
    SearchablePickerScreen {
        align: center middle;
    }

    #picker-dialog {
        width: 76;
        height: auto;
        max-height: 28;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #picker-search {
        margin-bottom: 1;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._entries: list[Any] = []
        self._by_item_id: dict[str, Any] = {}

    def compose(self) -> ComposeResult:
        with Vertical(id="picker-dialog"):
            yield Label(self.PICKER_TITLE, id="picker-title")
            yield Input(placeholder=self.SEARCH_PLACEHOLDER, id="picker-search")
            yield ListView(id=self.LIST_VIEW_ID)
            yield Button("Cancel", id="btn-cancel")

    async def on_mount(self) -> None:
        self._entries = self._load_entries()
        await self._render_list("")
        self.query_one("#picker-search", Input).focus()

    # -- subclass hooks --

    def _load_entries(self) -> list[Any]:
        raise NotImplementedError

    def _search_text(self, entry: Any) -> str:
        raise NotImplementedError

    def _label_for(self, entry: Any) -> str:
        raise NotImplementedError

    def _item_id(self, entry: Any) -> str:
        raise NotImplementedError

    def _on_entry_selected(self, entry: Any) -> None:
        raise NotImplementedError

    # -- filtering / list rendering --

    async def _render_list(self, query: str) -> None:
        list_view = self.query_one(f"#{self.LIST_VIEW_ID}", ListView)
        await list_view.clear()
        self._by_item_id = {}

        if not self._entries:
            await list_view.append(ListItem(Label(self.EMPTY_MESSAGE)))
            return

        needle = query.strip().lower()
        matches = (
            [e for e in self._entries if needle in self._search_text(e).lower()]
            if needle
            else self._entries
        )
        if not matches:
            await list_view.append(ListItem(Label(f"(no matches for {query!r})")))
            return

        for entry in matches:
            item_id = self._item_id(entry)
            self._by_item_id[item_id] = entry
            await list_view.append(ListItem(Label(self._label_for(entry)), id=item_id))
        list_view.index = 0

    async def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "picker-search":
            await self._render_list(event.value)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        # Enter in the search box activates the top (highlighted) match,
        # the same way arrowing down to it and pressing Enter would.
        if event.input.id != "picker-search":
            return
        list_view = self.query_one(f"#{self.LIST_VIEW_ID}", ListView)
        if list_view.index is None:
            return
        await self._activate(list_view.children[list_view.index])

    def on_key(self, event: Key) -> None:
        # Input has no "down" binding of its own, so it would otherwise
        # just bubble and do nothing -- forward it to move focus into the
        # (already-filtered) list, the natural next step after typing.
        if event.key != "down":
            return
        search = self.query_one("#picker-search", Input)
        if self.focused is not search:
            return
        list_view = self.query_one(f"#{self.LIST_VIEW_ID}", ListView)
        if list_view.children:
            list_view.focus()
            event.stop()

    # -- selection / dismissal --

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        await self._activate(event.item)

    async def _activate(self, item: ListItem) -> None:
        if item.id is None:
            return
        entry = self._by_item_id.get(item.id)
        if entry is None:
            return
        self._on_entry_selected(entry)


class VirtueFlawPickerScreen(SearchablePickerScreen):
    """Pick a character Virtue/Flaw from the catalog, prompting for
    parameters if needed. Dismisses with the new instance, or None if
    cancelled.

    Laboratories have their own, separate Virtue/Flaw catalog and picker
    -- see LabVirtueFlawPickerScreen -- since a lab's Virtues & Flaws
    (ArM5 Chapter 8) are a completely different list from a character's
    (Chapter 4), even though both use the same VirtueFlawInstance shape
    and Free/Minor/Major tiers.
    """

    PICKER_TITLE: ClassVar[str] = "Add a Virtue or Flaw"
    EMPTY_MESSAGE: ClassVar[str] = "(no more Virtues/Flaws available)"
    SEARCH_PLACEHOLDER: ClassVar[str] = "Search Virtues & Flaws..."
    LIST_VIEW_ID: ClassVar[str] = "vf-picker-list"

    def __init__(self, exclude_ids: set[str] | None = None) -> None:
        super().__init__()
        self._exclude_ids = exclude_ids or set()

    def _load_entries(self) -> list[VirtueFlawDef]:
        return [
            entry
            for entry in catalog.load_virtue_flaw_catalog()
            if entry.id not in self._exclude_ids
        ]

    def _search_text(self, entry: VirtueFlawDef) -> str:
        return f"{entry.name} {entry.type} {entry.category} {entry.tier}"

    def _label_for(self, entry: VirtueFlawDef) -> str:
        needs = f"  (needs: {', '.join(entry.parameters)})" if entry.parameters else ""
        return f"{entry.name}  [{entry.type}, {entry.tier}, cost {entry.cost}]{needs}"

    def _item_id(self, entry: VirtueFlawDef) -> str:
        return f"{_VIRTUE_FLAW_ITEM_ID_PREFIX}{entry.id}"

    def _on_entry_selected(self, entry: VirtueFlawDef) -> None:
        if not entry.parameters:
            self.dismiss(VirtueFlawInstance(vf_id=entry.id))
            return

        def handle_params(params: dict[str, str] | None) -> None:
            if params is not None:
                self.dismiss(VirtueFlawInstance(vf_id=entry.id, params=params))

        self.app.push_screen(
            ParamPromptScreen(entry.name, entry.parameters), handle_params
        )


class LabVirtueFlawPickerScreen(SearchablePickerScreen):
    """Pick a Laboratory Virtue/Flaw from the lab catalog (ArM5 Chapter 8
    -- Structure/Outfittings/Supernatural). Dismisses with the new
    instance, or None if cancelled.

    No ParamPromptScreen branch -- unlike character Virtues/Flaws, lab
    entries are never templated. `repeatable` entries (asterisked in the
    book -- Feature*, Person*, etc.) aren't excluded just because one's
    already attached, the same way templated character entries aren't.
    """

    PICKER_TITLE: ClassVar[str] = "Add a Laboratory Virtue or Flaw"
    EMPTY_MESSAGE: ClassVar[str] = "(no more Virtues/Flaws available)"
    SEARCH_PLACEHOLDER: ClassVar[str] = "Search Laboratory Virtues & Flaws..."
    LIST_VIEW_ID: ClassVar[str] = "lab-vf-picker-list"

    def __init__(self, exclude_ids: set[str] | None = None) -> None:
        super().__init__()
        self._exclude_ids = exclude_ids or set()

    def _load_entries(self) -> list[LabVirtueFlawDef]:
        return [
            entry
            for entry in catalog.load_lab_virtue_flaw_catalog()
            if entry.repeatable or entry.id not in self._exclude_ids
        ]

    def _search_text(self, entry: LabVirtueFlawDef) -> str:
        return f"{entry.name} {entry.type} {entry.category} {entry.tier}"

    def _label_for(self, entry: LabVirtueFlawDef) -> str:
        return f"{entry.name}  [{entry.type}, {entry.tier}, cost {entry.cost}]"

    def _item_id(self, entry: LabVirtueFlawDef) -> str:
        return f"{_LAB_VIRTUE_FLAW_ITEM_ID_PREFIX}{entry.id}"

    def _on_entry_selected(self, entry: LabVirtueFlawDef) -> None:
        self.dismiss(VirtueFlawInstance(vf_id=entry.id))


class AbilityDetailsScreen(ModalScreen[Ability | None]):
    """Prompts for level/xp/specialty once an Ability's name+category are known.

    Used both to add a new Ability (existing=None) and to edit one already
    on the sheet (existing provided, prefilled). Dismisses with the
    finished Ability, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    AbilityDetailsScreen {
        align: center middle;
    }

    #details-dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #details-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(
        self, name: str, category: str, existing: Ability | None = None
    ) -> None:
        super().__init__()
        self.ability_name = name
        self.category = category
        self.existing = existing

    def compose(self) -> ComposeResult:
        level = self.existing.level if self.existing else 0
        xp = self.existing.xp if self.existing else 0
        specialty = self.existing.specialty if self.existing else ""

        with Vertical(id="details-dialog"):
            yield Label(self.ability_name, id="details-title")
            yield Label("Level")
            yield Input(value=str(level), type="integer", id="input-level")
            yield Label("XP")
            yield Input(value=str(xp), type="integer", id="input-xp")
            yield Label("Specialty (optional)")
            yield Input(
                value=specialty or "", placeholder="e.g. Swords", id="input-specialty"
            )
            yield Static("", id="details-error")
            with Horizontal():
                yield Button("Confirm", id="btn-confirm", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-confirm":
            self._try_confirm()

    def _try_confirm(self) -> None:
        error = self.query_one("#details-error", Static)
        try:
            level = int(self.query_one("#input-level", Input).value.strip())
            xp = int(self.query_one("#input-xp", Input).value.strip())
        except ValueError:
            error.update("Level and XP must be whole numbers.")
            return

        specialty = self.query_one("#input-specialty", Input).value.strip() or None
        self.dismiss(
            Ability(
                name=self.ability_name,
                category=self.category,
                level=level,
                xp=xp,
                specialty=specialty,
            )
        )


class AbilityPickerScreen(SearchablePickerScreen):
    """Pick an Ability from the catalog, resolve any parameter, set score/specialty.

    Non-templated entries already held are excluded (no point in a second
    "Athletics" row); templated entries ("Craft: {craft}") stay available
    since a character can hold several distinct instances of the same
    family. Dismisses with the new Ability, or None if cancelled.
    """

    PICKER_TITLE: ClassVar[str] = "Add an Ability"
    EMPTY_MESSAGE: ClassVar[str] = "(no more Abilities available)"
    SEARCH_PLACEHOLDER: ClassVar[str] = "Search Abilities..."
    LIST_VIEW_ID: ClassVar[str] = "ability-picker-list"

    def __init__(self, exclude_names: set[str] | None = None) -> None:
        super().__init__()
        self._exclude_names = exclude_names or set()

    def _load_entries(self) -> list[AbilityDef]:
        return [
            entry
            for entry in catalog.load_ability_catalog()
            if entry.parameters or entry.name not in self._exclude_names
        ]

    def _search_text(self, entry: AbilityDef) -> str:
        return f"{entry.name} {entry.category}"

    def _label_for(self, entry: AbilityDef) -> str:
        needs = f"  (needs: {', '.join(entry.parameters)})" if entry.parameters else ""
        return f"{entry.name}  [{entry.category}]{needs}"

    def _item_id(self, entry: AbilityDef) -> str:
        return f"{_ABILITY_ITEM_ID_PREFIX}{entry.id}"

    def _on_entry_selected(self, entry: AbilityDef) -> None:
        if entry.parameters:

            def handle_params(params: dict[str, str] | None) -> None:
                if params is not None:
                    self._prompt_details(
                        catalog.resolve_ability_name(entry, params), entry.category
                    )

            self.app.push_screen(
                ParamPromptScreen(entry.name, entry.parameters), handle_params
            )
        else:
            self._prompt_details(entry.name, entry.category)

    def _prompt_details(self, name: str, category: str) -> None:
        def handle_ability(ability: Ability | None) -> None:
            if ability is not None:
                self.dismiss(ability)

        self.app.push_screen(AbilityDetailsScreen(name, category), handle_ability)


class RemovalPickerScreen(ModalScreen[int | None]):
    """Pick an item to remove from a list of display labels, by index.

    Generic over what's being removed -- Character/Laboratory Virtues &
    Flaws, Character Abilities, etc. -- the caller supplies the labels and
    is responsible for deleting the corresponding item from its own list
    using the returned index. Dismisses with that index, or None if
    cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    RemovalPickerScreen {
        align: center middle;
    }

    #picker-dialog {
        width: 76;
        height: auto;
        max-height: 24;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }
    """

    def __init__(self, title: str, labels: list[str]) -> None:
        super().__init__()
        self.prompt_title = title
        self.labels = labels

    def compose(self) -> ComposeResult:
        with Vertical(id="picker-dialog"):
            yield Label(self.prompt_title, id="picker-title")
            yield ListView(id="removal-picker-list")
            yield Button("Cancel", id="btn-cancel")

    def on_mount(self) -> None:
        list_view = self.query_one("#removal-picker-list", ListView)
        if not self.labels:
            list_view.append(ListItem(Label("(nothing to remove)")))
            return

        for index, label in enumerate(self.labels):
            list_view.append(
                ListItem(Label(label), id=f"{_REMOVAL_ITEM_ID_PREFIX}{index}")
            )
        list_view.index = 0

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id
        if item_id is None or not item_id.startswith(_REMOVAL_ITEM_ID_PREFIX):
            return
        index = int(item_id.removeprefix(_REMOVAL_ITEM_ID_PREFIX))
        self.dismiss(index)


class EditArtsScreen(ModalScreen[dict[str, ArtScore] | None]):
    """Edits all 15 Hermetic Arts at once -- a fixed grid, not an addable list.

    A single column, Techniques first then Forms -- matching how Abilities
    are organized on the sheet by category. (An earlier version split this
    into 3 side-by-side columns; that was reverted after it turned out to
    overflow a normal terminal width and corrupt click hit-testing.) Each
    Art shows a Level / XP pair. Dismisses with a dict of every art's
    lowercase name -> ArtScore, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditArtsScreen {
        align: center middle;
    }

    #arts-dialog {
        width: auto;
        height: auto;
        max-height: 22;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #arts-scroll {
        width: auto;
        height: auto;
        max-height: 13;
        overflow-y: auto;
    }

    #arts-buttons {
        width: auto;
        height: auto;
    }

    #arts-subtitle {
        color: $text-muted;
        margin-bottom: 1;
    }

    .column-heading {
        text-style: bold;
        margin-top: 1;
    }

    .art-row {
        width: auto;
        height: auto;
    }

    .art-row Label {
        width: 10;
        content-align: right middle;
        padding-right: 1;
    }

    .art-row .art-sep {
        width: 1;
        content-align: center middle;
    }

    .art-row Input {
        width: 5;
        height: 1;
        border: none;
    }

    #arts-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, arts: dict[str, ArtScore]) -> None:
        super().__init__()
        self.arts = arts

    def compose(self) -> ComposeResult:
        def row(art_name: str):
            key = art_name.lower()
            score = self.arts.get(key, ArtScore())
            yield Label(f"{art_name} ({ART_ABBREVIATIONS[art_name]})")
            yield Input(
                value=str(score.level),
                type="integer",
                id=f"input-art-{key}-level",
            )
            yield Label("/", classes="art-sep")
            yield Input(
                value=str(score.xp),
                type="integer",
                id=f"input-art-{key}-xp",
            )

        with Vertical(id="arts-dialog"):
            yield Label("Edit Arts", id="arts-title")
            with VerticalScroll(id="arts-scroll"):
                yield Label("Each score is Level / XP", id="arts-subtitle")
                yield Label("Techniques", classes="column-heading")
                for technique in TECHNIQUES:
                    with Horizontal(classes="art-row"):
                        yield from row(technique)
                yield Label("Forms", classes="column-heading")
                for form in FORMS:
                    with Horizontal(classes="art-row"):
                        yield from row(form)
            yield Static("", id="arts-error")
            with Horizontal(id="arts-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#arts-error", Static)
        result: dict[str, ArtScore] = {}
        for art_name in (*TECHNIQUES, *FORMS):
            key = art_name.lower()
            level_raw = self.query_one(f"#input-art-{key}-level", Input).value.strip()
            xp_raw = self.query_one(f"#input-art-{key}-xp", Input).value.strip()
            try:
                level = int(level_raw)
                xp = int(xp_raw)
            except ValueError:
                error.update(f"{art_name} needs whole numbers for Level and XP.")
                return
            result[key] = ArtScore(level=level, xp=xp)
        self.dismiss(result)


class LaboratoryCreateScreen(ModalScreen[str | None]):
    """Creates a bare laboratory within a covenant.

    Owner assignment and Features are left for later edit actions, same
    reasoning as Character creation leaving lab assignment for later.
    Dismisses with the new laboratory's id, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    LaboratoryCreateScreen {
        align: center middle;
    }

    #create-dialog {
        width: 64;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #create-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, saga: Saga, covenant: Covenant) -> None:
        super().__init__()
        self.saga = saga
        self.covenant = covenant

    def compose(self) -> ComposeResult:
        with Vertical(id="create-dialog"):
            yield Label("Create a New Laboratory", id="create-title")
            yield Label("Laboratory name")
            yield Input(placeholder="e.g. The Alchemical Tower", id="input-name")
            yield Label("Size")
            yield Input(value="0", type="integer", id="input-size")
            yield Static("", id="create-error")
            with Horizontal():
                yield Button("Create", id="btn-create", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-create":
            self._try_create()

    def _try_create(self) -> None:
        error = self.query_one("#create-error", Static)

        name = self.query_one("#input-name", Input).value.strip()
        if not name:
            error.update("Laboratory name is required.")
            return

        try:
            size = int(self.query_one("#input-size", Input).value.strip())
        except ValueError:
            error.update("Size must be a whole number.")
            return

        laboratory = Laboratory(
            id=storage.generate_unique_id(
                name, [lab.id for lab in self.saga.laboratories]
            ),
            covenant_id=self.covenant.id,
            name=name,
            characteristics=LabCharacteristics(size=size),
        )
        self.saga.laboratories.append(laboratory)
        storage.save_saga(self.saga)
        self.dismiss(laboratory.id)


class IdentityEditScreen(ModalScreen[dict[str, str | None] | None]):
    """Edits a character's Name, Covenant, and (for magi) Laboratory.

    Type is fixed at creation -- changing it after Arts/Spells already
    exist would leave the sheet in an inconsistent state, so it isn't
    editable here. Dismisses with
    {"name": ..., "covenant_id": ..., "laboratory_id": ...}, or None if
    cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    IdentityEditScreen {
        align: center middle;
    }

    #edit-dialog {
        width: 64;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #edit-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, saga: Saga, character: Character) -> None:
        super().__init__()
        self.saga = saga
        self.character = character

    def compose(self) -> ComposeResult:
        character = self.character
        with Vertical(id="edit-dialog"):
            yield Label("Edit Identity", id="edit-title")
            yield Label("Name")
            yield Input(value=character.name, id="input-name")
            yield Label("Covenant")
            yield Select(
                [(c.name, c.id) for c in self.saga.covenants],
                value=character.covenant_id or Select.NULL,
                allow_blank=True,
                prompt="(unassigned)",
                id="select-covenant",
            )
            if character.type == "magus":
                yield Label("Assigned Laboratory")
                yield Select(
                    [(lab.name, lab.id) for lab in self.saga.laboratories],
                    value=character.assigned_lab_id or Select.NULL,
                    allow_blank=True,
                    prompt="(unassigned)",
                    id="select-laboratory",
                )
            yield Static("", id="edit-error")
            with Horizontal():
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#edit-error", Static)

        name = self.query_one("#input-name", Input).value.strip()
        if not name:
            error.update("Name is required.")
            return

        covenant_value = self.query_one("#select-covenant", Select).value
        covenant_id = covenant_value if isinstance(covenant_value, str) else None

        laboratory_id: str | None = None
        if self.character.type == "magus":
            lab_value = self.query_one("#select-laboratory", Select).value
            laboratory_id = lab_value if isinstance(lab_value, str) else None

        self.dismiss(
            {"name": name, "covenant_id": covenant_id, "laboratory_id": laboratory_id}
        )


class EditCharacteristicsScreen(ModalScreen[Characteristics | None]):
    """Edits all 8 Characteristics at once: Int/Per/Str/Sta, Pre/Com/Dex/Qik.

    Dismisses with the finished Characteristics, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditCharacteristicsScreen {
        align: center middle;
    }

    #char-dialog {
        width: auto;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    .char-row {
        width: auto;
        height: auto;
    }

    .char-row Label {
        width: 5;
        content-align: right middle;
        padding-right: 1;
    }

    .char-row Input {
        width: 5;
        height: 1;
        border: none;
        margin-right: 2;
    }

    #char-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #char-buttons {
        width: auto;
        height: auto;
    }
    """

    _ROW1: ClassVar[list[tuple[str, str]]] = [
        ("Int", "intelligence"),
        ("Per", "perception"),
        ("Str", "strength"),
        ("Sta", "stamina"),
    ]
    _ROW2: ClassVar[list[tuple[str, str]]] = [
        ("Pre", "presence"),
        ("Com", "communication"),
        ("Dex", "dexterity"),
        ("Qik", "quickness"),
    ]

    def __init__(self, characteristics: Characteristics) -> None:
        super().__init__()
        self.characteristics = characteristics

    def compose(self) -> ComposeResult:
        with Vertical(id="char-dialog"):
            yield Label("Edit Characteristics", id="char-title")
            for row in (self._ROW1, self._ROW2):
                with Horizontal(classes="char-row"):
                    for label, field_name in row:
                        yield Label(label)
                        yield Input(
                            value=str(getattr(self.characteristics, field_name)),
                            type="integer",
                            id=f"input-char-{field_name}",
                        )
            yield Static("", id="char-error")
            with Horizontal(id="char-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#char-error", Static)
        values: dict[str, int] = {}
        for label, field_name in (*self._ROW1, *self._ROW2):
            raw = self.query_one(f"#input-char-{field_name}", Input).value.strip()
            try:
                values[field_name] = int(raw)
            except ValueError:
                error.update(f"{label} must be a whole number.")
                return
        self.dismiss(Characteristics(**values))


class SpellPickerScreen(ModalScreen[str | None]):
    """Pick a spell (by id) from the saga's spells, to add as known.

    Only lists spells not already known. There's no custom spell creation
    yet (see the backlog in DESIGN.md); this just wires up the "known
    spells" relationship against whatever spells already exist in the
    saga. Dismisses with the spell id, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    SpellPickerScreen {
        align: center middle;
    }

    #picker-dialog {
        width: 76;
        height: auto;
        max-height: 24;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }
    """

    def __init__(self, available_spells: list[Spell]) -> None:
        super().__init__()
        self.available_spells = available_spells

    def compose(self) -> ComposeResult:
        with Vertical(id="picker-dialog"):
            yield Label("Add a Known Spell", id="picker-title")
            yield ListView(id="spell-picker-list")
            yield Button("Cancel", id="btn-cancel")

    def on_mount(self) -> None:
        list_view = self.query_one("#spell-picker-list", ListView)
        if not self.available_spells:
            list_view.append(ListItem(Label("(no spells available)")))
            return

        for spell in self.available_spells:
            technique = ART_ABBREVIATIONS.get(spell.technique, spell.technique[:2])
            form = ART_ABBREVIATIONS.get(spell.form, spell.form[:2])
            label = f"{spell.name} ({technique}{form} {spell.level})"
            list_view.append(
                ListItem(Label(label), id=f"{_SPELL_ITEM_ID_PREFIX}{spell.id}")
            )
        list_view.index = 0

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id
        if item_id is None or not item_id.startswith(_SPELL_ITEM_ID_PREFIX):
            return
        self.dismiss(item_id.removeprefix(_SPELL_ITEM_ID_PREFIX))


class ItemAddScreen(ModalScreen[str | None]):
    """Freeform text entry for an inventory item.

    Dismisses with the item description, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    ItemAddScreen {
        align: center middle;
    }

    #create-dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #create-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="create-dialog"):
            yield Label("Add an Item", id="create-title")
            yield Input(placeholder="e.g. Fine wool cloak", id="input-item")
            yield Static("", id="create-error")
            with Horizontal():
                yield Button("Add", id="btn-create", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-create":
            self._try_create()

    def _try_create(self) -> None:
        error = self.query_one("#create-error", Static)
        item = self.query_one("#input-item", Input).value.strip()
        if not item:
            error.update("Item description is required.")
            return
        self.dismiss(item)


class ScoredTraitPromptScreen(ModalScreen[ScoredTrait | None]):
    """Name + integer score prompt, reused for Personality Traits and
    Reputations -- both are just a label and a score on the character
    sheet. Dismisses with a ScoredTrait, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    ScoredTraitPromptScreen {
        align: center middle;
    }

    #trait-dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #trait-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(
        self, title: str, name_placeholder: str, existing: ScoredTrait | None = None
    ) -> None:
        super().__init__()
        self.title_text = title
        self.name_placeholder = name_placeholder
        self.existing = existing

    def compose(self) -> ComposeResult:
        with Vertical(id="trait-dialog"):
            yield Label(self.title_text, id="trait-title")
            yield Label("Name")
            yield Input(
                value=self.existing.name if self.existing else "",
                placeholder=self.name_placeholder,
                id="input-trait-name",
            )
            yield Label("Score")
            yield Input(
                value=str(self.existing.score) if self.existing else "0",
                type="integer",
                id="input-trait-score",
            )
            yield Static("", id="trait-error")
            with Horizontal():
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#trait-error", Static)
        name = self.query_one("#input-trait-name", Input).value.strip()
        if not name:
            error.update("Name is required.")
            return
        raw_score = self.query_one("#input-trait-score", Input).value.strip()
        try:
            score = int(raw_score)
        except ValueError:
            error.update("Score must be a whole number.")
            return
        self.dismiss(ScoredTrait(name=name, score=score))


class RawVisPromptScreen(ModalScreen[tuple[str, int] | None]):
    """Prompts for an Art + a number of pawns, to add to a character's Raw
    Vis. Dismisses with (art, pawns), or None if cancelled. Adding an Art
    that's already held increases its existing pawn count -- see
    WorkspaceScreen._add_raw_vis().
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    RawVisPromptScreen {
        align: center middle;
    }

    #vis-dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #vis-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="vis-dialog"):
            yield Label("Add Raw Vis", id="vis-title")
            yield Label("Art")
            yield Select(
                [(art, art.lower()) for art in (*TECHNIQUES, *FORMS)],
                id="select-vis-art",
            )
            yield Label("Pawns")
            yield Input(value="1", type="integer", id="input-vis-pawns")
            yield Static("", id="vis-error")
            with Horizontal():
                yield Button("Add", id="btn-create", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-create":
            self._try_create()

    def _try_create(self) -> None:
        error = self.query_one("#vis-error", Static)
        art = self.query_one("#select-vis-art", Select).value
        if not isinstance(art, str):
            error.update("Choose an Art.")
            return
        raw_pawns = self.query_one("#input-vis-pawns", Input).value.strip()
        try:
            pawns = int(raw_pawns)
        except ValueError:
            error.update("Pawns must be a whole number.")
            return
        self.dismiss((art, pawns))


class EditBackgroundScreen(ModalScreen[Background | None]):
    """Edits the sheet's page-1 biographical block. Dismisses with the
    finished Background, or None if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditBackgroundScreen {
        align: center middle;
    }

    #background-dialog {
        width: 70;
        height: auto;
        max-height: 30;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #background-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    _STR_FIELDS: ClassVar[list[tuple[str, str]]] = [
        ("Player", "player"),
        ("Setting", "setting"),
        ("Birth Name", "birth_name"),
        ("Race/Nationality", "race_nationality"),
        ("Place of Origin", "place_of_origin"),
        ("Religion", "religion"),
        ("Title/Profession", "title_profession"),
    ]

    def __init__(self, background: Background) -> None:
        super().__init__()
        self.background = background

    def compose(self) -> ComposeResult:
        b = self.background
        with VerticalScroll(id="background-dialog"):
            yield Label("Edit Background", id="background-title")
            for label, field_name in self._STR_FIELDS:
                yield Label(label)
                yield Input(value=getattr(b, field_name), id=f"input-bg-{field_name}")
            yield Label("Size")
            yield Input(value=str(b.size), type="integer", id="input-bg-size")
            yield Label("Confidence")
            yield Input(
                value=str(b.confidence), type="integer", id="input-bg-confidence"
            )
            yield Label("Year Born")
            yield Input(
                value="" if b.year_born is None else str(b.year_born),
                type="integer",
                id="input-bg-year_born",
            )
            yield Static("", id="background-error")
            with Horizontal():
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#background-error", Static)
        values: dict[str, object] = {}
        for _label, field_name in self._STR_FIELDS:
            values[field_name] = self.query_one(
                f"#input-bg-{field_name}", Input
            ).value.strip()

        for label, field_name in (("Size", "size"), ("Confidence", "confidence")):
            raw = self.query_one(f"#input-bg-{field_name}", Input).value.strip()
            try:
                values[field_name] = int(raw)
            except ValueError:
                error.update(f"{label} must be a whole number.")
                return

        raw_year_born = self.query_one("#input-bg-year_born", Input).value.strip()
        if raw_year_born:
            try:
                values["year_born"] = int(raw_year_born)
            except ValueError:
                error.update("Year Born must be a whole number.")
                return
        else:
            values["year_born"] = None

        self.dismiss(Background(**values))


class EditDescriptionScreen(ModalScreen[Description | None]):
    """Edits the sheet's Description box (page 1). Dismisses with the
    finished Description, or None if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditDescriptionScreen {
        align: center middle;
    }

    #description-dialog {
        width: 70;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #description-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    _HANDEDNESS_OPTIONS: ClassVar[list[tuple[str, str]]] = [
        ("Right", "right"),
        ("Left", "left"),
        ("Ambidextrous", "ambidextrous"),
    ]

    def __init__(self, description: Description) -> None:
        super().__init__()
        self.description = description

    def compose(self) -> ComposeResult:
        d = self.description
        with Vertical(id="description-dialog"):
            yield Label("Edit Description", id="description-title")
            yield Label("Height")
            yield Input(
                value="" if d.height is None else str(d.height),
                id="input-desc-height",
            )
            yield Label("Weight")
            yield Input(
                value="" if d.weight is None else str(d.weight),
                id="input-desc-weight",
            )
            yield Label("Hair")
            yield Input(value=d.hair, id="input-desc-hair")
            yield Label("Eyes")
            yield Input(value=d.eyes, id="input-desc-eyes")
            yield Label("Handedness")
            yield Select(
                self._HANDEDNESS_OPTIONS,
                value=d.handedness,
                allow_blank=False,
                id="select-desc-handedness",
            )
            yield Label("Physical Description")
            yield Input(
                value=d.physical_description, id="input-desc-physical_description"
            )
            yield Static("", id="description-error")
            with Horizontal():
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#description-error", Static)

        height: float | None = None
        raw_height = self.query_one("#input-desc-height", Input).value.strip()
        if raw_height:
            try:
                height = float(raw_height)
            except ValueError:
                error.update("Height must be a number.")
                return

        weight: float | None = None
        raw_weight = self.query_one("#input-desc-weight", Input).value.strip()
        if raw_weight:
            try:
                weight = float(raw_weight)
            except ValueError:
                error.update("Weight must be a number.")
                return

        handedness = self.query_one("#select-desc-handedness", Select).value
        self.dismiss(
            Description(
                height=height,
                weight=weight,
                hair=self.query_one("#input-desc-hair", Input).value.strip(),
                eyes=self.query_one("#input-desc-eyes", Input).value.strip(),
                handedness=handedness,  # type: ignore[arg-type]
                physical_description=self.query_one(
                    "#input-desc-physical_description", Input
                ).value.strip(),
            )
        )


class EditAgingScreen(ModalScreen[Aging | None]):
    """Edits Decrepitude and Warping (Score/Points, like an Ability's
    Level/XP -- see Aging's docstring). Dismisses with the finished Aging,
    or None if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditAgingScreen {
        align: center middle;
    }

    #aging-dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #aging-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, aging: Aging) -> None:
        super().__init__()
        self.aging = aging

    def compose(self) -> ComposeResult:
        a = self.aging
        with Vertical(id="aging-dialog"):
            yield Label("Edit Aging & Warping", id="aging-title")
            yield Label("Decrepitude")
            yield Input(
                value=str(a.decrepitude), type="integer", id="input-aging-decrepitude"
            )
            yield Label("Effects of Aging")
            yield Input(value=a.effects, id="input-aging-effects")
            yield Label("Warping Score")
            yield Input(
                value=str(a.warping_score),
                type="integer",
                id="input-aging-warping_score",
            )
            yield Label("Warping Points")
            yield Input(
                value=str(a.warping_points),
                type="integer",
                id="input-aging-warping_points",
            )
            yield Static("", id="aging-error")
            with Horizontal():
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#aging-error", Static)
        values: dict[str, object] = {}
        for label, field_name in (
            ("Decrepitude", "decrepitude"),
            ("Warping Score", "warping_score"),
            ("Warping Points", "warping_points"),
        ):
            raw = self.query_one(f"#input-aging-{field_name}", Input).value.strip()
            try:
                values[field_name] = int(raw)
            except ValueError:
                error.update(f"{label} must be a whole number.")
                return
        values["effects"] = self.query_one("#input-aging-effects", Input).value.strip()
        self.dismiss(Aging(**values))


class EditWoundsScreen(ModalScreen[Wounds | None]):
    """Edits Wound counts per severity, plus Incapacitated/Dead. Simple
    counts, not individual wound records -- matches checking boxes on the
    paper sheet, not the calculated Wound Penalty (see Wounds's docstring).
    Dismisses with the finished Wounds, or None if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditWoundsScreen {
        align: center middle;
    }

    #wounds-dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #wounds-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, wounds: Wounds) -> None:
        super().__init__()
        self.wounds = wounds

    def compose(self) -> ComposeResult:
        w = self.wounds
        with Vertical(id="wounds-dialog"):
            yield Label("Edit Wounds", id="wounds-title")
            yield Label("Light Wounds (-1 each)")
            yield Input(value=str(w.light), type="integer", id="input-wounds-light")
            yield Label("Medium Wounds (-3 each)")
            yield Input(value=str(w.medium), type="integer", id="input-wounds-medium")
            yield Label("Heavy Wounds (-5 each)")
            yield Input(value=str(w.heavy), type="integer", id="input-wounds-heavy")
            yield Checkbox(
                "Incapacitated", value=w.incapacitated, id="check-wounds-incapacitated"
            )
            yield Checkbox("Dead", value=w.dead, id="check-wounds-dead")
            yield Static("", id="wounds-error")
            with Horizontal():
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#wounds-error", Static)
        values: dict[str, object] = {}
        for label, field_name in (
            ("Light Wounds", "light"),
            ("Medium Wounds", "medium"),
            ("Heavy Wounds", "heavy"),
        ):
            raw = self.query_one(f"#input-wounds-{field_name}", Input).value.strip()
            try:
                values[field_name] = int(raw)
            except ValueError:
                error.update(f"{label} must be a whole number.")
                return
        values["incapacitated"] = self.query_one(
            "#check-wounds-incapacitated", Checkbox
        ).value
        values["dead"] = self.query_one("#check-wounds-dead", Checkbox).value
        self.dismiss(Wounds(**values))


class EditFatigueScreen(ModalScreen[FatigueLevel | None]):
    """Picks the character's current Fatigue Level. Dismisses with the
    chosen level, or None if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditFatigueScreen {
        align: center middle;
    }

    #fatigue-dialog {
        width: 50;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }
    """

    def __init__(self, current: FatigueLevel) -> None:
        super().__init__()
        self.current = current

    def compose(self) -> ComposeResult:
        with Vertical(id="fatigue-dialog"):
            yield Label("Edit Fatigue Level", id="fatigue-title")
            yield Select(
                [(level.title(), level) for level in FATIGUE_LEVELS],
                value=self.current,
                allow_blank=False,
                id="select-fatigue-level",
            )
            with Horizontal():
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            level = self.query_one("#select-fatigue-level", Select).value
            self.dismiss(level)  # type: ignore[arg-type]


class EditHermeticBackgroundScreen(ModalScreen[HermeticBackground | None]):
    """Edits a magus's Hermetic lineage block: House (picked from the
    catalog) plus Domus Magna/Primus/Parens/Covenant of Apprenticeship/
    Wizard's Sigil. Dismisses with the finished HermeticBackground, or None
    if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditHermeticBackgroundScreen {
        align: center middle;
    }

    #hermetic-dialog {
        width: 70;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }
    """

    _STR_FIELDS: ClassVar[list[tuple[str, str]]] = [
        ("Domus Magna", "domus_magna"),
        ("Primus", "primus"),
        ("Parens", "parens"),
        ("Covenant of Apprenticeship", "covenant_of_apprenticeship"),
        ("Wizard's Sigil", "wizards_sigil"),
    ]

    def __init__(self, hermetic: HermeticBackground) -> None:
        super().__init__()
        self.hermetic = hermetic

    def compose(self) -> ComposeResult:
        h = self.hermetic
        houses = catalog.load_house_catalog()
        with Vertical(id="hermetic-dialog"):
            yield Label("Edit Hermetic Background", id="hermetic-title")
            yield Label("House")
            yield Select(
                [(house.name, house.id) for house in houses],
                value=h.house or Select.NULL,
                allow_blank=True,
                prompt="(none selected)",
                id="select-hermetic-house",
            )
            for label, field_name in self._STR_FIELDS:
                yield Label(label)
                yield Input(
                    value=getattr(h, field_name), id=f"input-hermetic-{field_name}"
                )
            with Horizontal():
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            house_value = self.query_one("#select-hermetic-house", Select).value
            house = house_value if isinstance(house_value, str) else None
            values: dict[str, object] = {"house": house}
            for _label, field_name in self._STR_FIELDS:
                values[field_name] = self.query_one(
                    f"#input-hermetic-{field_name}", Input
                ).value.strip()
            self.dismiss(HermeticBackground(**values))


class EditLabIdentityScreen(ModalScreen[dict[str, object] | None]):
    """Edits a Laboratory's Name/Location/Build Points, and (unlike
    character Identity editing) lets you reassign its Owner from the
    lab's own side -- WorkspaceScreen._assign_laboratory() already
    handles the bidirectional sync, this just calls it from here too.
    Dismisses with {"name", "location", "build_points", "owner_id"}, or
    None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditLabIdentityScreen {
        align: center middle;
    }

    #lab-identity-dialog {
        width: 64;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #lab-identity-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, saga: Saga, laboratory: Laboratory) -> None:
        super().__init__()
        self.saga = saga
        self.laboratory = laboratory

    def compose(self) -> ComposeResult:
        lab = self.laboratory
        with Vertical(id="lab-identity-dialog"):
            yield Label("Edit Laboratory Identity", id="lab-identity-title")
            yield Label("Name")
            yield Input(value=lab.name, id="input-lab-name")
            yield Label("Location")
            yield Input(value=lab.location, id="input-lab-location")
            yield Label("Points (covenant Build Points spent)")
            yield Input(
                value=str(lab.build_points), type="integer", id="input-lab-points"
            )
            yield Label("Owner")
            yield Select(
                [(c.name, c.id) for c in self.saga.characters if c.type == "magus"],
                value=lab.owner_id or Select.NULL,
                allow_blank=True,
                prompt="(unassigned)",
                id="select-lab-owner",
            )
            yield Static("", id="lab-identity-error")
            with Horizontal():
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#lab-identity-error", Static)

        name = self.query_one("#input-lab-name", Input).value.strip()
        if not name:
            error.update("Name is required.")
            return

        raw_points = self.query_one("#input-lab-points", Input).value.strip()
        try:
            build_points = int(raw_points)
        except ValueError:
            error.update("Points must be a whole number.")
            return

        owner_value = self.query_one("#select-lab-owner", Select).value
        owner_id = owner_value if isinstance(owner_value, str) else None

        self.dismiss(
            {
                "name": name,
                "location": self.query_one("#input-lab-location", Input).value.strip(),
                "build_points": build_points,
                "owner_id": owner_id,
            }
        )


class EditLabCharacteristicsScreen(ModalScreen[LabCharacteristics | None]):
    """Edits the manual (base) component of the 8 Laboratory
    Characteristics -- see LabCharacteristics's docstring for why this is
    only the manual component, not the Virtue/Flaw-derived total.
    Dismisses with the finished LabCharacteristics, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditLabCharacteristicsScreen {
        align: center middle;
    }

    #lab-char-dialog {
        width: 64;
        height: auto;
        max-height: 30;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #lab-char-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, characteristics: LabCharacteristics) -> None:
        super().__init__()
        self.characteristics = characteristics

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="lab-char-dialog"):
            yield Label("Edit Laboratory Characteristics (manual value)")
            for characteristic in LAB_CHARACTERISTICS:
                yield Label(characteristic.replace("_", " ").title())
                yield Input(
                    value=str(getattr(self.characteristics, characteristic)),
                    type="integer",
                    id=f"input-labchar-{characteristic}",
                )
            yield Static("", id="lab-char-error")
            with Horizontal():
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#lab-char-error", Static)
        values: dict[str, int] = {}
        for characteristic in LAB_CHARACTERISTICS:
            raw = self.query_one(
                f"#input-labchar-{characteristic}", Input
            ).value.strip()
            try:
                values[characteristic] = int(raw)
            except ValueError:
                error.update(
                    f"{characteristic.replace('_', ' ').title()} must be "
                    "a whole number."
                )
                return
        self.dismiss(LabCharacteristics(**values))


class NamedDescriptionPromptScreen(ModalScreen[NamedDescription | None]):
    """Name + free-text description prompt, reused for a Laboratory's
    Rooms and its Inventory items. Dismisses with a NamedDescription, or
    None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    NamedDescriptionPromptScreen {
        align: center middle;
    }

    #named-desc-dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #named-desc-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, title: str, name_placeholder: str) -> None:
        super().__init__()
        self.title_text = title
        self.name_placeholder = name_placeholder

    def compose(self) -> ComposeResult:
        with Vertical(id="named-desc-dialog"):
            yield Label(self.title_text, id="named-desc-title")
            yield Label("Name")
            yield Input(placeholder=self.name_placeholder, id="input-named-desc-name")
            yield Label("Description")
            yield Input(id="input-named-desc-description")
            yield Static("", id="named-desc-error")
            with Horizontal():
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#named-desc-error", Static)
        name = self.query_one("#input-named-desc-name", Input).value.strip()
        if not name:
            error.update("Name is required.")
            return
        description = self.query_one(
            "#input-named-desc-description", Input
        ).value.strip()
        self.dismiss(NamedDescription(name=name, description=description))


class DiaryEntryPromptScreen(ModalScreen[DiaryEntry | None]):
    """Year/Season/Name/Details prompt for a Laboratory diary entry.
    Dismisses with a DiaryEntry, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    DiaryEntryPromptScreen {
        align: center middle;
    }

    #diary-dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #diary-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, default_year: int) -> None:
        super().__init__()
        self.default_year = default_year

    def compose(self) -> ComposeResult:
        with Vertical(id="diary-dialog"):
            yield Label("Add a Diary Entry", id="diary-title")
            yield Label("Year")
            yield Input(
                value=str(self.default_year), type="integer", id="input-diary-year"
            )
            yield Label("Season")
            yield Select(
                [(season, season) for season in SEASONS],
                value=SEASONS[0],
                allow_blank=False,
                id="select-diary-season",
            )
            yield Label("Name")
            yield Input(placeholder="e.g. Invented a spell", id="input-diary-name")
            yield Label("Details")
            yield Input(id="input-diary-details")
            yield Static("", id="diary-error")
            with Horizontal():
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#diary-error", Static)
        raw_year = self.query_one("#input-diary-year", Input).value.strip()
        try:
            year = int(raw_year)
        except ValueError:
            error.update("Year must be a whole number.")
            return
        name = self.query_one("#input-diary-name", Input).value.strip()
        if not name:
            error.update("Name is required.")
            return
        season = self.query_one("#select-diary-season", Select).value
        details = self.query_one("#input-diary-details", Input).value.strip()
        self.dismiss(DiaryEntry(year=year, season=season, name=name, details=details))


class CharacterSheetView(Vertical):
    """The character sheet mounted into WorkspaceScreen's detail pane.

    One tab per page of the official character sheet, each a scrolling
    stack of collapsible sections (rendered as plain text for now, matching
    the rest of the app's read-then-refresh style):

    - Identity (page 1): Identity, Background, Description, Characteristics,
      Abilities (grouped by category), Virtues & Flaws (grouped
      Virtue/Flaw, tagged Free/Minor/Major), Aging & Warping.
    - Personality & Health (page 2): Personality Traits, Reputations,
      Wounds, Fatigue, Inventory (the sheet's Equipment section).
    - Hermetic (page 3, magi only): Magical Arts (Techniques then Forms),
      Raw Vis, Hermetic Background.
    - Spells (page 4, magi only): Spells known -- a single pane, no
      sub-sections, since nothing new was added here.
    """

    DEFAULT_CSS = """
    CharacterSheetView {
        height: 1fr;
    }

    CharacterSheetView TabPane {
        padding: 1 0;
    }

    CharacterSheetView VerticalScroll {
        height: 1fr;
        width: 1fr;
    }
    """

    def __init__(self, saga: Saga, character: Character) -> None:
        super().__init__()
        self.saga = saga
        self.character = character

    def compose(self) -> ComposeResult:
        character = self.character
        with TabbedContent(initial="tab-identity"):
            with TabPane("Identity", id="tab-identity"), VerticalScroll():
                with Collapsible(title="Identity", id="section-identity"):
                    yield Static(self._identity_text(), id="identity-content")
                with Collapsible(title="Background", id="section-background"):
                    yield Static(self._background_text(), id="background-content")
                with Collapsible(title="Description", id="section-description"):
                    yield Static(self._description_text(), id="description-content")
                with Collapsible(title="Characteristics", id="section-characteristics"):
                    yield Static(
                        self._characteristics_text(), id="characteristics-content"
                    )
                with Collapsible(title="Abilities", id="section-abilities"):
                    yield Static(self._abilities_text(), id="abilities-content")
                with Collapsible(title="Virtues & Flaws", id="section-vf"):
                    yield Static(self._vf_text(), id="vf-content")
                with Collapsible(title="Aging & Warping", id="section-aging"):
                    yield Static(self._aging_text(), id="aging-content")
            with (
                TabPane("Personality & Health", id="tab-personality"),
                VerticalScroll(),
            ):
                with Collapsible(
                    title="Personality Traits", id="section-personality-traits"
                ):
                    yield Static(
                        self._personality_traits_text(),
                        id="personality-traits-content",
                    )
                with Collapsible(title="Reputations", id="section-reputations"):
                    yield Static(self._reputations_text(), id="reputations-content")
                with Collapsible(title="Wounds", id="section-wounds"):
                    yield Static(self._wounds_text(), id="wounds-content")
                with Collapsible(title="Fatigue", id="section-fatigue"):
                    yield Static(self._fatigue_text(), id="fatigue-content")
                with Collapsible(title="Inventory", id="section-inventory"):
                    yield Static(self._inventory_text(), id="inventory-content")
            if character.type == "magus":
                with TabPane("Hermetic", id="tab-hermetic"), VerticalScroll():
                    with Collapsible(title="Magical Arts", id="section-arts"):
                        yield Static(self._arts_text(), id="arts-content")
                    with Collapsible(title="Raw Vis", id="section-raw-vis"):
                        yield Static(self._raw_vis_text(), id="raw-vis-content")
                    with Collapsible(
                        title="Hermetic Background",
                        id="section-hermetic-background",
                    ):
                        yield Static(
                            self._hermetic_background_text(),
                            id="hermetic-background-content",
                        )
                with TabPane("Spells", id="tab-spells"):
                    yield Static(self._spells_text(), id="spells-content")

    #: Bare Collapsible-section ids, except "tab-spells" which has no
    #: sub-sections (a single flat pane, keyed by its own tab id) -- see
    #: WorkspaceScreen._active_character_section().
    _SECTION_CONTENT: ClassVar[dict[str, str]] = {
        "section-identity": "#identity-content",
        "section-background": "#background-content",
        "section-description": "#description-content",
        "section-characteristics": "#characteristics-content",
        "section-abilities": "#abilities-content",
        "section-vf": "#vf-content",
        "section-aging": "#aging-content",
        "section-personality-traits": "#personality-traits-content",
        "section-reputations": "#reputations-content",
        "section-wounds": "#wounds-content",
        "section-fatigue": "#fatigue-content",
        "section-inventory": "#inventory-content",
        "section-arts": "#arts-content",
        "section-raw-vis": "#raw-vis-content",
        "section-hermetic-background": "#hermetic-background-content",
        "tab-spells": "#spells-content",
    }
    _SECTION_TEXT: ClassVar[dict[str, str]] = {
        "section-identity": "_identity_text",
        "section-background": "_background_text",
        "section-description": "_description_text",
        "section-characteristics": "_characteristics_text",
        "section-abilities": "_abilities_text",
        "section-vf": "_vf_text",
        "section-aging": "_aging_text",
        "section-personality-traits": "_personality_traits_text",
        "section-reputations": "_reputations_text",
        "section-wounds": "_wounds_text",
        "section-fatigue": "_fatigue_text",
        "section-inventory": "_inventory_text",
        "section-arts": "_arts_text",
        "section-raw-vis": "_raw_vis_text",
        "section-hermetic-background": "_hermetic_background_text",
        "tab-spells": "_spells_text",
    }

    def refresh_section(self, section_id: str) -> None:
        selector = self._SECTION_CONTENT.get(section_id)
        text_method = self._SECTION_TEXT.get(section_id)
        if selector is None or text_method is None:
            return
        try:
            static = self.query_one(selector, Static)
        except NoMatches:
            return
        static.update(getattr(self, text_method)())

    def _identity_text(self) -> str:
        saga, character = self.saga, self.character
        covenant = next(
            (c for c in saga.covenants if c.id == character.covenant_id), None
        )
        lines = [
            f"Name: {character.name}",
            f"Type: {character.type}",
            f"Covenant: {covenant.name if covenant else '(unassigned)'}",
        ]
        if character.type == "magus":
            lab = next(
                (
                    lab
                    for lab in saga.laboratories
                    if lab.id == character.assigned_lab_id
                ),
                None,
            )
            lines.append(f"Assigned Laboratory: {lab.name if lab else '(unassigned)'}")
        return "\n".join(lines)

    def _background_text(self) -> str:
        b = self.character.background
        age = character_age(b.year_born, self.saga.current_year)
        return "\n".join(
            [
                f"Player: {b.player or '(not set)'}",
                f"Setting: {b.setting or '(not set)'}",
                f"Current Year: {self.saga.current_year}",
                f"Age: {age if age is not None else '(unknown -- set Year Born)'}",
                f"Size: {b.size}",
                f"Confidence: {b.confidence}",
                f"Birth Name: {b.birth_name or '(not set)'}",
                f"Year Born: {b.year_born if b.year_born is not None else '(not set)'}",
                f"Race/Nationality: {b.race_nationality or '(not set)'}",
                f"Place of Origin: {b.place_of_origin or '(not set)'}",
                f"Religion: {b.religion or '(not set)'}",
                f"Title/Profession: {b.title_profession or '(not set)'}",
            ]
        )

    def _description_text(self) -> str:
        d = self.character.description
        return "\n".join(
            [
                f"Height: {d.height if d.height is not None else '(not set)'}",
                f"Weight: {d.weight if d.weight is not None else '(not set)'}",
                f"Hair: {d.hair or '(not set)'}",
                f"Eyes: {d.eyes or '(not set)'}",
                f"Handedness: {d.handedness}",
                "",
                "Physical Description:",
                d.physical_description or "(none recorded)",
            ]
        )

    def _characteristics_text(self) -> str:
        c = self.character.characteristics
        return (
            f"Int {c.intelligence}   Per {c.perception}   "
            f"Str {c.strength}   Sta {c.stamina}\n"
            f"Pre {c.presence}   Com {c.communication}   "
            f"Dex {c.dexterity}   Qik {c.quickness}"
        )

    def _abilities_text(self) -> str:
        if not self.character.abilities:
            return "(none recorded)"

        lines: list[str] = []
        for category in ABILITY_CATEGORIES:
            abilities = [a for a in self.character.abilities if a.category == category]
            if not abilities:
                continue
            lines.append(f"{category}:")
            for ability in abilities:
                specialty = f" ({ability.specialty})" if ability.specialty else ""
                lines.append(
                    f"  {ability.name}{specialty} {ability.level}/{ability.xp}"
                )
            lines.append("")
        return "\n".join(lines).rstrip()

    def _vf_text(self) -> str:
        if not self.character.virtues_flaws:
            return "(none recorded)"

        vf_catalog = catalog.load_virtue_flaw_catalog_by_id()
        lines: list[str] = []
        for vf_type in ("Virtue", "Flaw"):
            entries = [
                vf
                for vf in self.character.virtues_flaws
                if (definition := vf_catalog.get(vf.vf_id)) is not None
                and definition.type == vf_type
            ]
            if not entries:
                continue
            lines.append(f"{vf_type}s:")
            for vf in entries:
                definition = vf_catalog.get(vf.vf_id)
                tier = definition.tier if definition is not None else "?"
                lines.append(
                    f"  {catalog.describe_virtue_flaw(vf, vf_catalog)} ({tier})"
                )
            lines.append("")
        return "\n".join(lines).rstrip()

    def _aging_text(self) -> str:
        a = self.character.aging
        return "\n".join(
            [
                f"Decrepitude: {a.decrepitude}",
                "Effects of Aging:",
                a.effects or "(none recorded)",
                "",
                f"Warping: {a.warping_score}/{a.warping_points}",
            ]
        )

    def _personality_traits_text(self) -> str:
        return self._scored_traits_text(
            self.character.personality_traits, "(none recorded)", signed=True
        )

    def _reputations_text(self) -> str:
        return self._scored_traits_text(
            self.character.reputations, "(none recorded)", signed=False
        )

    @staticmethod
    def _scored_traits_text(
        traits: list[ScoredTrait], empty_message: str, *, signed: bool
    ) -> str:
        if not traits:
            return empty_message
        fmt = "{name}: {score:+d}" if signed else "{name}: {score}"
        return "\n".join(fmt.format(name=t.name, score=t.score) for t in traits)

    def _wounds_text(self) -> str:
        w = self.character.wounds
        return "\n".join(
            [
                f"Light Wounds:  {w.light} (-1 each)",
                f"Medium Wounds: {w.medium} (-3 each)",
                f"Heavy Wounds:  {w.heavy} (-5 each)",
                f"Incapacitated: {'yes' if w.incapacitated else 'no'}",
                f"Dead: {'yes' if w.dead else 'no'}",
            ]
        )

    def _fatigue_text(self) -> str:
        return f"Fatigue Level: {self.character.fatigue_level.title()}"

    def _raw_vis_text(self) -> str:
        if not self.character.raw_vis:
            return "(none recorded)"
        return "\n".join(
            f"{art.title()}: {pawns} pawn(s)"
            for art, pawns in sorted(self.character.raw_vis.items())
        )

    def _hermetic_background_text(self) -> str:
        h = self.character.hermetic
        house_catalog = catalog.load_house_catalog_by_id()
        house = house_catalog.get(h.house) if h.house else None
        return "\n".join(
            [
                f"House: {house.name if house else '(not set)'}",
                f"Domus Magna: {h.domus_magna or '(not set)'}",
                f"Primus: {h.primus or '(not set)'}",
                f"Parens: {h.parens or '(not set)'}",
                f"Covenant of Apprenticeship: "
                f"{h.covenant_of_apprenticeship or '(not set)'}",
                f"Wizard's Sigil: {h.wizards_sigil or '(not set)'}",
            ]
        )

    def _arts_text(self) -> str:
        lines = ["Techniques:"]
        for art in TECHNIQUES:
            score = self.character.arts.get(art.lower(), ArtScore())
            lines.append(
                f"  {art} ({ART_ABBREVIATIONS[art]}): {score.level}/{score.xp}"
            )
        lines.append("")
        lines.append("Forms:")
        for art in FORMS:
            score = self.character.arts.get(art.lower(), ArtScore())
            lines.append(
                f"  {art} ({ART_ABBREVIATIONS[art]}): {score.level}/{score.xp}"
            )
        return "\n".join(lines)

    def _spells_text(self) -> str:
        if not self.character.spells_known:
            return "(none recorded)"

        spell_lookup = {s.id: s for s in self.saga.spells}
        lines = []
        for spell_id in self.character.spells_known:
            spell = spell_lookup.get(spell_id)
            if spell is None:
                lines.append(f"  {spell_id} (unknown spell)")
                continue
            technique = ART_ABBREVIATIONS.get(spell.technique, spell.technique[:2])
            form = ART_ABBREVIATIONS.get(spell.form, spell.form[:2])
            lines.append(f"  {spell.name} ({technique}{form} {spell.level})")
        return "\n".join(lines)

    def _inventory_text(self) -> str:
        if not self.character.inventory:
            return "(none recorded)"
        return "\n".join(f"  - {item}" for item in self.character.inventory)


class LaboratorySheetView(Vertical):
    """The laboratory sheet mounted into WorkspaceScreen's detail pane.

    A fixed top panel (Identity, Characteristics -- not inside any tab)
    above a 5-tab body mirroring the sheet's own pages:
    Planning (placeholder), Virtues & Flaws, Attributes (Specialties/
    Features/Rooms), Inventory (Raw Vis/Items), Diary. Same Collapsible-
    section + read-then-refresh Static pattern as CharacterSheetView.
    """

    DEFAULT_CSS = """
    LaboratorySheetView {
        height: 1fr;
    }

    LaboratorySheetView TabPane {
        padding: 1 0;
    }

    LaboratorySheetView VerticalScroll {
        height: 1fr;
        width: 1fr;
    }
    """

    def __init__(self, saga: Saga, laboratory: Laboratory) -> None:
        super().__init__()
        self.saga = saga
        self.laboratory = laboratory

    def compose(self) -> ComposeResult:
        with Vertical(id="lab-top-panel"):
            with Collapsible(title="Identity", id="section-lab-identity"):
                yield Static(self._identity_text(), id="lab-identity-content")
            with Collapsible(title="Characteristics", id="section-lab-characteristics"):
                yield Static(
                    self._characteristics_text(), id="lab-characteristics-content"
                )
        with TabbedContent(initial="tab-lab-planning"):
            with TabPane("Planning", id="tab-lab-planning"):
                yield Static(self._planning_text(), id="lab-planning-content")
            with TabPane("Virtues & Flaws", id="tab-lab-vf"):
                yield Static(self._vf_text(), id="lab-vf-content")
            with TabPane("Attributes", id="tab-lab-attributes"), VerticalScroll():
                with Collapsible(title="Specialties", id="section-lab-specialties"):
                    yield Static(self._specialties_text(), id="lab-specialties-content")
                with Collapsible(title="Features", id="section-lab-features"):
                    yield Static(self._features_text(), id="lab-features-content")
                with Collapsible(title="Rooms", id="section-lab-rooms"):
                    yield Static(self._rooms_text(), id="lab-rooms-content")
            with TabPane("Inventory", id="tab-lab-inventory"), VerticalScroll():
                with Collapsible(title="Raw Vis", id="section-lab-raw-vis"):
                    yield Static(self._raw_vis_text(), id="lab-raw-vis-content")
                with Collapsible(title="Items", id="section-lab-items"):
                    yield Static(self._items_text(), id="lab-items-content")
            with TabPane("Diary", id="tab-lab-diary"):
                yield Static(self._diary_text(), id="lab-diary-content")

    _SECTION_CONTENT: ClassVar[dict[str, str]] = {
        "section-lab-identity": "#lab-identity-content",
        "section-lab-characteristics": "#lab-characteristics-content",
        "tab-lab-planning": "#lab-planning-content",
        "tab-lab-vf": "#lab-vf-content",
        "section-lab-specialties": "#lab-specialties-content",
        "section-lab-features": "#lab-features-content",
        "section-lab-rooms": "#lab-rooms-content",
        "section-lab-raw-vis": "#lab-raw-vis-content",
        "section-lab-items": "#lab-items-content",
        "tab-lab-diary": "#lab-diary-content",
    }
    _SECTION_TEXT: ClassVar[dict[str, str]] = {
        "section-lab-identity": "_identity_text",
        "section-lab-characteristics": "_characteristics_text",
        "tab-lab-planning": "_planning_text",
        "tab-lab-vf": "_vf_text",
        "section-lab-specialties": "_specialties_text",
        "section-lab-features": "_features_text",
        "section-lab-rooms": "_rooms_text",
        "section-lab-raw-vis": "_raw_vis_text",
        "section-lab-items": "_items_text",
        "tab-lab-diary": "_diary_text",
    }

    def refresh_section(self, section_id: str) -> None:
        selector = self._SECTION_CONTENT.get(section_id)
        text_method = self._SECTION_TEXT.get(section_id)
        if selector is None or text_method is None:
            return
        try:
            static = self.query_one(selector, Static)
        except NoMatches:
            return
        static.update(getattr(self, text_method)())

    def _identity_text(self) -> str:
        saga, lab = self.saga, self.laboratory
        covenant = next((c for c in saga.covenants if c.id == lab.covenant_id), None)
        owner = next((c for c in saga.characters if c.id == lab.owner_id), None)
        return "\n".join(
            [
                f"Name: {lab.name}",
                f"Location: {lab.location or '(not set)'}",
                f"Points: {lab.build_points}",
                f"Owner: {owner.name if owner else '(unassigned)'}",
                f"Covenant: {covenant.name if covenant else '(none)'}",
                f"Aura: {covenant.aura if covenant else 0} "
                "(inherited from the covenant)",
            ]
        )

    def _characteristics_text(self) -> str:
        lab_catalog = catalog.load_lab_virtue_flaw_catalog_by_id()
        lab = self.laboratory
        lines = [
            f"Occupied Size: {lab_occupied_size(lab, lab_catalog):g}",
            f"Free Virtues: {lab_free_virtues(lab, lab_catalog):g}",
            f"Base Safety: {lab_base_safety(lab, lab_catalog):g}",
            "",
        ]
        for characteristic in LAB_CHARACTERISTICS:
            manual, virtue_sum, flaw_sum, total = lab_characteristic_total(
                lab, lab_catalog, characteristic
            )
            label = characteristic.replace("_", " ").title()
            lines.append(
                f"{label}: {manual:+d} (manual) {virtue_sum:+d} (Virtues) "
                f"{flaw_sum:+d} (Flaws) = {total:+d}"
            )
        return "\n".join(lines)

    def _planning_text(self) -> str:
        return "Lab activity planning isn't built yet -- coming in a future update."

    def _vf_text(self) -> str:
        if not self.laboratory.virtues_flaws:
            return "(none recorded)"

        lab_catalog = catalog.load_lab_virtue_flaw_catalog_by_id()
        lines: list[str] = []
        for vf_type in ("Virtue", "Flaw"):
            entries = [
                vf
                for vf in self.laboratory.virtues_flaws
                if (definition := lab_catalog.get(vf.vf_id)) is not None
                and definition.type == vf_type
            ]
            if not entries:
                continue
            lines.append(f"{vf_type}s:")
            for vf in entries:
                definition = lab_catalog.get(vf.vf_id)
                tier = definition.tier if definition is not None else "?"
                lines.append(
                    f"  {catalog.describe_virtue_flaw(vf, lab_catalog)} ({tier})"
                )
            lines.append("")
        return "\n".join(lines).rstrip()

    def _specialties_text(self) -> str:
        if not self.laboratory.specialties:
            return "(none recorded)"
        return "\n".join(f"  - {s}" for s in self.laboratory.specialties)

    def _features_text(self) -> str:
        if not self.laboratory.features:
            return "(none recorded)"
        return "\n".join(f"  - {f}" for f in self.laboratory.features)

    def _rooms_text(self) -> str:
        if not self.laboratory.rooms:
            return "(none recorded)"
        return "\n".join(
            f"  {room.name}: {room.description or '(no description)'}"
            for room in self.laboratory.rooms
        )

    def _raw_vis_text(self) -> str:
        if not self.laboratory.raw_vis:
            return "(none recorded)"
        return "\n".join(
            f"{art.title()}: {pawns} pawn(s)"
            for art, pawns in sorted(self.laboratory.raw_vis.items())
        )

    def _items_text(self) -> str:
        if not self.laboratory.inventory_items:
            return "(none recorded)"
        return "\n".join(
            f"  {item.name}: {item.description or '(no description)'}"
            for item in self.laboratory.inventory_items
        )

    def _diary_text(self) -> str:
        if not self.laboratory.diary:
            return "(none recorded)"
        lines = []
        for entry in self.laboratory.diary:
            lines.append(f"{entry.year} {entry.season} -- {entry.name}")
            if entry.details:
                lines.append(f"  {entry.details}")
        return "\n".join(lines)


class WorkspaceScreen(Screen[None]):
    """Persistent nav tree (left) + detail pane (right) for one open saga.

    Replaces the old Saga -> Covenant -> Character/Lab/Library drill-down
    screens with a single workspace: the whole saga's structure is always
    visible in the tree, and selecting any node swaps the detail pane on
    the right, so comparing siblings doesn't mean popping all the way back
    up and down again.
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        ("n", "create_covenant", "New Covenant"),
        ("c", "create_character", "New Character"),
        ("l", "create_laboratory", "New Laboratory"),
        ("a", "add", "Add"),
        ("A", "remove", "Remove"),
        ("e", "edit", "Edit"),
        ("v", "add_virtue_flaw", "Add Virtue/Flaw"),
        ("V", "remove_virtue_flaw", "Remove Virtue/Flaw"),
        ("escape", "app.pop_screen", "Back"),
        ("q", "quit", "Quit"),
    ]

    #: Which character-sheet and laboratory-sheet sections support the
    #: generic Add/Remove/Edit bindings. 'a'/'A'/'e' dispatch by whichever
    #: section currently has focus instead of each having their own
    #: dedicated key, since a fully-built sheet has too many addable/
    #: editable sections for that to scale. Sections live inside
    #: Collapsibles (several per tab), so the dispatch key is normally a
    #: Collapsible's id -- "tab-spells"/"tab-lab-vf"/"tab-lab-diary" are
    #: the exceptions, tabs with no sub-sections, keyed by their own tab
    #: id (see _active_section()).
    _ADD_SECTIONS: ClassVar[set[str]] = {
        "section-abilities",
        "section-personality-traits",
        "section-reputations",
        "section-raw-vis",
        "section-inventory",
        "tab-spells",
        "section-lab-specialties",
        "section-lab-features",
        "section-lab-rooms",
        "section-lab-raw-vis",
        "section-lab-items",
        "tab-lab-diary",
    }
    _REMOVE_SECTIONS: ClassVar[set[str]] = {
        "section-abilities",
        "section-personality-traits",
        "section-reputations",
        "section-raw-vis",
        "section-inventory",
        "tab-spells",
        "section-lab-specialties",
        "section-lab-features",
        "section-lab-rooms",
        "section-lab-raw-vis",
        "section-lab-items",
        "tab-lab-diary",
    }
    _EDIT_SECTIONS: ClassVar[set[str]] = {
        "section-identity",
        "section-background",
        "section-description",
        "section-characteristics",
        "section-abilities",
        "section-aging",
        "section-wounds",
        "section-fatigue",
        "section-arts",
        "section-hermetic-background",
        "section-lab-identity",
        "section-lab-characteristics",
    }

    DEFAULT_CSS = """
    #workspace-body {
        height: 1fr;
    }

    #nav-tree {
        width: 34;
        border-right: solid $accent;
    }

    #detail-pane {
        width: 1fr;
        padding: 1 2;
    }
    """

    def __init__(self, saga: Saga) -> None:
        super().__init__()
        self.saga = saga
        self.selected_kind: str = "saga"
        self.selected_covenant: Covenant | None = None
        self.selected_character: Character | None = None
        self.selected_laboratory: Laboratory | None = None
        self._character_sheet_view: CharacterSheetView | None = None
        self._laboratory_sheet_view: LaboratorySheetView | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="workspace-body"):
            yield Tree(self.saga.name, data=("saga",), id="nav-tree")
            yield VerticalScroll(id="detail-pane")
        yield Footer()

    async def on_mount(self) -> None:
        self._rebuild_tree()
        await self._show_saga_detail()

    def _rebuild_tree(self) -> None:
        tree = self.query_one("#nav-tree", Tree)
        tree.reset(self.saga.name, data=("saga",))
        tree.root.expand()

        for covenant in self.saga.covenants:
            cov_node = tree.root.add(
                covenant.name, data=("covenant", covenant.id), expand=True
            )

            characters = [
                c for c in self.saga.characters if c.covenant_id == covenant.id
            ]
            char_group = cov_node.add(
                f"Characters ({len(characters)})",
                data=("character_group", covenant.id),
                expand=True,
            )
            for character in characters:
                char_group.add_leaf(
                    f"{character.name} ({character.type})",
                    data=("character", character.id),
                )

            labs = [
                lab for lab in self.saga.laboratories if lab.covenant_id == covenant.id
            ]
            lab_group = cov_node.add(
                f"Laboratories ({len(labs)})",
                data=("laboratory_group", covenant.id),
                expand=True,
            )
            for lab in labs:
                lab_group.add_leaf(lab.name, data=("laboratory", lab.id))

            library = next(
                (lib for lib in self.saga.libraries if lib.id == covenant.library_id),
                None,
            )
            library_label = "Library"
            if library is not None:
                library_label += f" ({len(library.books)} book(s))"
            cov_node.add_leaf(library_label, data=("library", covenant.id))

    async def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        data = event.node.data
        if data is None:
            return

        kind = data[0]
        self.selected_kind = kind
        self._character_sheet_view = None
        self._laboratory_sheet_view = None

        if kind == "saga":
            self.selected_covenant = None
            self.selected_character = None
            self.selected_laboratory = None
            await self._show_saga_detail()
        elif kind == "covenant":
            covenant = next(c for c in self.saga.covenants if c.id == data[1])
            self.selected_covenant = covenant
            self.selected_character = None
            self.selected_laboratory = None
            await self._show_covenant_detail(covenant)
        elif kind == "character_group":
            covenant = next(c for c in self.saga.covenants if c.id == data[1])
            self.selected_covenant = covenant
            self.selected_character = None
            await self._show_placeholder_detail(
                f"Characters in {covenant.name}",
                "Select a character from the tree, or press 'c' to add one.",
            )
        elif kind == "character":
            character = next(c for c in self.saga.characters if c.id == data[1])
            self.selected_character = character
            self.selected_covenant = next(
                (c for c in self.saga.covenants if c.id == character.covenant_id),
                None,
            )
            await self._show_character_detail(character)
        elif kind == "laboratory_group":
            covenant = next(c for c in self.saga.covenants if c.id == data[1])
            self.selected_covenant = covenant
            self.selected_laboratory = None
            await self._show_placeholder_detail(
                f"Laboratories in {covenant.name}",
                "Select a laboratory from the tree, or press 'l' to add one.",
            )
        elif kind == "laboratory":
            lab = next(lab for lab in self.saga.laboratories if lab.id == data[1])
            self.selected_laboratory = lab
            self.selected_covenant = next(
                (c for c in self.saga.covenants if c.id == lab.covenant_id), None
            )
            await self._show_laboratory_detail(lab)
        elif kind == "library":
            covenant = next(c for c in self.saga.covenants if c.id == data[1])
            self.selected_covenant = covenant
            library = next(
                (lib for lib in self.saga.libraries if lib.id == covenant.library_id),
                None,
            )
            await self._show_library_detail(library)

        self.refresh_bindings()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "create_covenant":
            return self.selected_kind == "saga"
        if action == "create_character":
            return self.selected_kind in ("covenant", "character_group", "character")
        if action == "create_laboratory":
            return self.selected_kind in (
                "covenant",
                "laboratory_group",
                "laboratory",
            )
        if action == "add":
            return self._active_section() in self._ADD_SECTIONS
        if action == "remove":
            return self._active_section() in self._REMOVE_SECTIONS
        if action == "edit":
            return self._active_section() in self._EDIT_SECTIONS
        if action in ("add_virtue_flaw", "remove_virtue_flaw"):
            if self.selected_kind == "laboratory":
                return self._active_section() == "tab-lab-vf"
            return self._active_section() == "section-vf"
        return True

    def _active_section(self) -> str | None:
        """Which sheet section is "active" for a/A/e (and v/V) dispatch --
        a thin router to whichever sheet is actually showing."""
        if self.selected_kind == "character":
            return self._active_character_section()
        if self.selected_kind == "laboratory":
            return self._active_laboratory_section()
        return None

    def _active_character_section(self) -> str | None:
        """Which character-sheet section is "active" for a/A/e dispatch.

        Sections live inside Collapsibles now (several per tab), so tab id
        alone can no longer disambiguate -- resolve the nearest Collapsible
        ancestor of whatever's currently focused instead. Falls back to the
        bare tab id when nothing's focused inside a Collapsible (including
        tabs with no sub-sections at all, like Spells), matching the old
        whole-tab dispatch exactly for that case.
        """
        if self._character_sheet_view is None:
            return None
        try:
            tab_id = self._character_sheet_view.query_one(TabbedContent).active
        except NoMatches:
            return None
        if not tab_id:
            return None

        focused = self.app.focused
        if focused is not None:
            for widget in focused.ancestors_with_self:
                if isinstance(widget, Collapsible) and widget.id:
                    return widget.id
        return tab_id

    def _active_laboratory_section(self) -> str | None:
        """Same mechanism as _active_character_section(), against the
        laboratory sheet instead -- see that method's docstring."""
        if self._laboratory_sheet_view is None:
            return None
        try:
            tab_id = self._laboratory_sheet_view.query_one(TabbedContent).active
        except NoMatches:
            return None
        if not tab_id:
            return None

        focused = self.app.focused
        if focused is not None:
            for widget in focused.ancestors_with_self:
                if isinstance(widget, Collapsible) and widget.id:
                    return widget.id
        return tab_id

    def on_tabbed_content_tab_activated(
        self, event: TabbedContent.TabActivated
    ) -> None:
        # Keep the Footer's binding hints (and check_action gating) in sync
        # with whichever tab the user just switched to, and give the new
        # tab's first section focus so 'e'/'a'/'A' work immediately without
        # requiring an explicit Tab-key navigation first.
        self._focus_first_section()
        self.refresh_bindings()

    def _focus_first_section(self, *, initial: bool = False) -> None:
        if self.selected_kind == "character":
            self._focus_first_character_section()
        elif self.selected_kind == "laboratory":
            self._focus_first_laboratory_section(initial=initial)

    def _focus_first_character_section(self) -> None:
        if self._character_sheet_view is None:
            return
        try:
            tabbed = self._character_sheet_view.query_one(TabbedContent)
            if not tabbed.active:
                return
            active_pane = self._character_sheet_view.query_one(
                f"#{tabbed.active}", TabPane
            )
            collapsible = active_pane.query(Collapsible).first()
        except NoMatches:
            return
        collapsible.query_one("CollapsibleTitle").focus()

    def _focus_first_laboratory_section(self, *, initial: bool = False) -> None:
        if self._laboratory_sheet_view is None:
            return
        try:
            tabbed = self._laboratory_sheet_view.query_one(TabbedContent)
            if not tabbed.active:
                return
            active_pane = self._laboratory_sheet_view.query_one(
                f"#{tabbed.active}", TabPane
            )
            collapsible = active_pane.query(Collapsible).first()
        except NoMatches:
            # The active tab is flat (Planning/Virtues & Flaws/Diary have
            # no Collapsible). On first showing the lab (its initial tab,
            # Planning, is one of these flat tabs) fall back to the top
            # panel's first Collapsible (Identity), so something is always
            # focused rather than nothing. On a later tab *switch* to a
            # flat tab, clear focus instead of falling back -- the top
            # panel's Collapsibles live outside the TabbedContent, so
            # switching tabs never blurs them on its own, and leaving a
            # stale one focused would make _active_laboratory_section()
            # keep reporting it instead of this flat tab.
            if not initial:
                self.screen.set_focus(None)
                return
            try:
                collapsible = self._laboratory_sheet_view.query(Collapsible).first()
            except NoMatches:
                return
        collapsible.query_one("CollapsibleTitle").focus()

    def on_descendant_focus(self, event: DescendantFocus) -> None:
        # Focus can move between Collapsible sections within the same tab
        # (no TabActivated message for that) -- keep bindings in sync then
        # too, or the Footer hint and check_action gating go stale.
        self.refresh_bindings()

    def on_descendant_blur(self, event: DescendantBlur) -> None:
        self.refresh_bindings()

    async def _set_detail(self, *widgets: Widget) -> None:
        detail_pane = self.query_one("#detail-pane", VerticalScroll)
        # Must be awaited before mounting replacements below, or a same-id
        # widget not yet removed collides with its freshly-mounted
        # replacement and Textual raises DuplicateIds.
        await detail_pane.remove_children()
        await detail_pane.mount(*widgets)

    async def _show_placeholder_detail(self, title: str, hint: str) -> None:
        await self._set_detail(Static(f"{title}\n\n{hint}"))

    async def _show_saga_detail(self) -> None:
        saga = self.saga
        lines = [
            f"Saga: {saga.name}",
            f"Storyguide: {saga.storyguide}",
            f"Start date: {saga.current_season} {saga.current_year}",
        ]
        if saga.description:
            lines.append(f"Description: {saga.description}")
        lines += [
            "",
            f"Covenants: {len(saga.covenants)}",
            f"Characters: {len(saga.characters)}",
            f"Laboratories: {len(saga.laboratories)}",
            f"Libraries: {len(saga.libraries)}",
            f"Books: {len(saga.books)}",
            f"Spells: {len(saga.spells)}",
        ]
        await self._set_detail(Static("\n".join(lines)))

    async def _show_covenant_detail(self, covenant: Covenant) -> None:
        await self._set_detail(Static(self._covenant_summary(covenant)))

    def _covenant_summary(self, covenant: Covenant) -> str:
        lines = [
            f"Covenant: {covenant.name}",
            f"Saga: {self.saga.name}",
            f"Aura: {covenant.aura}",
        ]
        if covenant.notes:
            lines.append(f"Notes: {covenant.notes}")

        lines.append("")
        if covenant.vis_stock:
            lines.append("Vis stock:")
            lines += [
                f"  {form}: {amount}" for form, amount in covenant.vis_stock.items()
            ]
        else:
            lines.append("Vis stock: (none recorded)")
        return "\n".join(lines)

    async def _show_laboratory_detail(self, lab: Laboratory) -> None:
        view = LaboratorySheetView(self.saga, lab)
        await self._set_detail(view)
        self._laboratory_sheet_view = view
        self._focus_first_section(initial=True)

    async def _show_library_detail(self, library: Library | None) -> None:
        await self._set_detail(Static(self._library_summary(library)))

    def _library_summary(self, library: Library | None) -> str:
        saga = self.saga
        if library is None:
            return "Library: (none)"

        covenant = next(
            (c for c in saga.covenants if c.id == library.covenant_id), None
        )
        book_lookup = {b.id: b for b in saga.books}
        spell_lookup = {s.id: s for s in saga.spells}

        lines = [f"Library (covenant: {covenant.name if covenant else '(none)'})", ""]

        if not library.books:
            lines.append("Books: (none recorded)")
            return "\n".join(lines)

        lines.append(f"Books ({len(library.books)}):")
        for book_id in library.books:
            book = book_lookup.get(book_id)
            if book is None:
                lines.append(f"  - {book_id} (unknown book)")
                continue

            level = f" L{book.level}" if book.level is not None else ""
            line = f"  - [{book.type}] {book.subject}{level} Q{book.quality}"
            if book.author:
                line += f" by {book.author}"
            if book.type == "Lab Text" and book.spell_id:
                spell = spell_lookup.get(book.spell_id)
                line += f" -- {spell.name}" if spell else " -- (unknown spell)"
            lines.append(line)

        return "\n".join(lines)

    async def _show_character_detail(self, character: Character) -> None:
        view = CharacterSheetView(self.saga, character)
        await self._set_detail(view)
        self._character_sheet_view = view
        self._focus_first_section()

    def _refresh_character_section(self, section_id: str) -> None:
        if self._character_sheet_view is not None:
            self._character_sheet_view.refresh_section(section_id)

    def _refresh_laboratory_section(self, section_id: str) -> None:
        if self._laboratory_sheet_view is not None:
            self._laboratory_sheet_view.refresh_section(section_id)

    def _assign_laboratory(self, character: Character, new_lab_id: str | None) -> None:
        """Keeps Character.assigned_lab_id and Laboratory.owner_id in sync
        from both directions: the character's old lab (if any) is freed,
        and if the newly-assigned lab already had a different owner, that
        character is unassigned too, so a lab never has an owner who
        doesn't point back at it or vice versa.
        """
        saga = self.saga
        old_lab = next(
            (lab for lab in saga.laboratories if lab.id == character.assigned_lab_id),
            None,
        )
        if old_lab is not None:
            old_lab.owner_id = None

        character.assigned_lab_id = new_lab_id
        if new_lab_id is None:
            return

        new_lab = next(lab for lab in saga.laboratories if lab.id == new_lab_id)
        previous_owner = next(
            (c for c in saga.characters if c.id == new_lab.owner_id), None
        )
        if previous_owner is not None:
            previous_owner.assigned_lab_id = None
        new_lab.owner_id = character.id

    def _assign_laboratory_owner(
        self, lab: Laboratory, new_owner_id: str | None
    ) -> None:
        """Owner reassignment from the laboratory's side -- the inverse of
        _assign_laboratory(character, lab_id), reusing the same sync logic
        rather than duplicating it."""
        if new_owner_id is None:
            if lab.owner_id is not None:
                old_owner = next(
                    (c for c in self.saga.characters if c.id == lab.owner_id), None
                )
                if old_owner is not None:
                    old_owner.assigned_lab_id = None
                lab.owner_id = None
            return
        new_owner = next(c for c in self.saga.characters if c.id == new_owner_id)
        self._assign_laboratory(new_owner, lab.id)

    # -- creation actions --

    def action_create_covenant(self) -> None:
        async def handle_result(covenant_id: str | None) -> None:
            if covenant_id is not None:
                self._rebuild_tree()
                covenant = next(c for c in self.saga.covenants if c.id == covenant_id)
                self.selected_covenant = covenant
                self.selected_kind = "covenant"
                await self._show_covenant_detail(covenant)

        self.app.push_screen(CovenantCreateScreen(self.saga), handle_result)

    def action_create_character(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            self.notify("Select a covenant first.")
            return

        async def handle_result(character_id: str | None) -> None:
            if character_id is not None:
                self._rebuild_tree()
                character = next(
                    c for c in self.saga.characters if c.id == character_id
                )
                self.selected_character = character
                self.selected_kind = "character"
                await self._show_character_detail(character)

        self.app.push_screen(
            CharacterCreateScreen(self.saga, default_covenant_id=covenant.id),
            handle_result,
        )

    def action_create_laboratory(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            self.notify("Select a covenant first.")
            return

        async def handle_result(lab_id: str | None) -> None:
            if lab_id is not None:
                self._rebuild_tree()
                lab = next(lab for lab in self.saga.laboratories if lab.id == lab_id)
                self.selected_laboratory = lab
                self.selected_kind = "laboratory"
                await self._show_laboratory_detail(lab)

        self.app.push_screen(LaboratoryCreateScreen(self.saga, covenant), handle_result)

    # -- generic Add/Remove/Edit dispatch, by active character-sheet section --

    def action_add(self) -> None:
        section = self._active_section()
        if section == "section-abilities":
            self._add_ability()
        elif section == "tab-spells":
            self._add_spell()
        elif section == "section-inventory":
            self._add_item()
        elif section == "section-personality-traits":
            self._add_personality_trait()
        elif section == "section-reputations":
            self._add_reputation()
        elif section == "section-raw-vis":
            self._add_raw_vis()
        elif section == "section-lab-specialties":
            self._add_specialty()
        elif section == "section-lab-features":
            self._add_feature()
        elif section == "section-lab-rooms":
            self._add_room()
        elif section == "section-lab-raw-vis":
            self._add_lab_raw_vis()
        elif section == "section-lab-items":
            self._add_inventory_item()
        elif section == "tab-lab-diary":
            self._add_diary_entry()

    def action_remove(self) -> None:
        section = self._active_section()
        if section == "section-abilities":
            self._remove_ability()
        elif section == "tab-spells":
            self._remove_spell()
        elif section == "section-inventory":
            self._remove_item()
        elif section == "section-personality-traits":
            self._remove_personality_trait()
        elif section == "section-reputations":
            self._remove_reputation()
        elif section == "section-raw-vis":
            self._remove_raw_vis()
        elif section == "section-lab-specialties":
            self._remove_specialty()
        elif section == "section-lab-features":
            self._remove_feature()
        elif section == "section-lab-rooms":
            self._remove_room()
        elif section == "section-lab-raw-vis":
            self._remove_lab_raw_vis()
        elif section == "section-lab-items":
            self._remove_inventory_item()
        elif section == "tab-lab-diary":
            self._remove_diary_entry()

    def action_edit(self) -> None:
        section = self._active_section()
        if section == "section-identity":
            self._edit_identity()
        elif section == "section-background":
            self._edit_background()
        elif section == "section-description":
            self._edit_description()
        elif section == "section-characteristics":
            self._edit_characteristics()
        elif section == "section-abilities":
            self._edit_ability()
        elif section == "section-aging":
            self._edit_aging()
        elif section == "section-wounds":
            self._edit_wounds()
        elif section == "section-fatigue":
            self._edit_fatigue()
        elif section == "section-arts":
            self._edit_arts()
        elif section == "section-hermetic-background":
            self._edit_hermetic_background()
        elif section == "section-lab-identity":
            self._edit_lab_identity()
        elif section == "section-lab-characteristics":
            self._edit_lab_characteristics()

    # -- Identity / Characteristics --

    def _edit_identity(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: dict[str, str | None] | None) -> None:
            if result is None:
                return
            character.name = result["name"]
            character.covenant_id = result["covenant_id"]
            if character.type == "magus":
                self._assign_laboratory(character, result["laboratory_id"])
            storage.save_saga(self.saga)
            self._rebuild_tree()
            self._refresh_character_section("section-identity")

        self.app.push_screen(IdentityEditScreen(self.saga, character), handle_result)

    def _edit_characteristics(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(characteristics: Characteristics | None) -> None:
            if characteristics is not None:
                character.characteristics = characteristics
                storage.save_saga(self.saga)
                self._refresh_character_section("section-characteristics")

        self.app.push_screen(
            EditCharacteristicsScreen(character.characteristics), handle_result
        )

    def _edit_background(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(background: Background | None) -> None:
            if background is not None:
                character.background = background
                storage.save_saga(self.saga)
                self._refresh_character_section("section-background")

        self.app.push_screen(EditBackgroundScreen(character.background), handle_result)

    def _edit_description(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(description: Description | None) -> None:
            if description is not None:
                character.description = description
                storage.save_saga(self.saga)
                self._refresh_character_section("section-description")

        self.app.push_screen(
            EditDescriptionScreen(character.description), handle_result
        )

    def _edit_aging(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(aging: Aging | None) -> None:
            if aging is not None:
                character.aging = aging
                storage.save_saga(self.saga)
                self._refresh_character_section("section-aging")

        self.app.push_screen(EditAgingScreen(character.aging), handle_result)

    # -- Abilities --

    def _add_ability(self) -> None:
        character = self.selected_character
        if character is None:
            return
        exclude_names = {a.name for a in character.abilities}

        def handle_result(ability: Ability | None) -> None:
            if ability is not None:
                character.abilities.append(ability)
                storage.save_saga(self.saga)
                self._refresh_character_section("section-abilities")

        self.app.push_screen(AbilityPickerScreen(exclude_names), handle_result)

    def _remove_ability(self) -> None:
        character = self.selected_character
        if character is None:
            return
        if not character.abilities:
            self.notify("No Abilities to remove.")
            return

        labels = [
            f"{a.name} {a.level}/{a.xp}" + (f" ({a.specialty})" if a.specialty else "")
            for a in character.abilities
        ]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del character.abilities[index]
                storage.save_saga(self.saga)
                self._refresh_character_section("section-abilities")

        self.app.push_screen(
            RemovalPickerScreen("Remove an Ability", labels), handle_result
        )

    def _edit_ability(self) -> None:
        character = self.selected_character
        if character is None:
            return
        if not character.abilities:
            self.notify("No Abilities to edit.")
            return

        labels = [
            f"{a.name} {a.level}/{a.xp}" + (f" ({a.specialty})" if a.specialty else "")
            for a in character.abilities
        ]

        def handle_index(index: int | None) -> None:
            if index is None:
                return
            existing = character.abilities[index]

            def handle_result(ability: Ability | None) -> None:
                if ability is not None:
                    character.abilities[index] = ability
                    storage.save_saga(self.saga)
                    self._refresh_character_section("section-abilities")

            self.app.push_screen(
                AbilityDetailsScreen(existing.name, existing.category, existing),
                handle_result,
            )

        self.app.push_screen(
            RemovalPickerScreen("Edit which Ability?", labels), handle_index
        )

    # -- Personality Traits / Reputations / Wounds / Fatigue --

    def _add_personality_trait(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(trait: ScoredTrait | None) -> None:
            if trait is not None:
                character.personality_traits.append(trait)
                storage.save_saga(self.saga)
                self._refresh_character_section("section-personality-traits")

        self.app.push_screen(
            ScoredTraitPromptScreen("Add a Personality Trait", "e.g. Brave"),
            handle_result,
        )

    def _remove_personality_trait(self) -> None:
        character = self.selected_character
        if character is None:
            return
        if not character.personality_traits:
            self.notify("No Personality Traits to remove.")
            return

        labels = [f"{t.name}: {t.score:+d}" for t in character.personality_traits]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del character.personality_traits[index]
                storage.save_saga(self.saga)
                self._refresh_character_section("section-personality-traits")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Personality Trait", labels), handle_result
        )

    def _add_reputation(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(trait: ScoredTrait | None) -> None:
            if trait is not None:
                character.reputations.append(trait)
                storage.save_saga(self.saga)
                self._refresh_character_section("section-reputations")

        self.app.push_screen(
            ScoredTraitPromptScreen("Add a Reputation", "e.g. Skilled Enchanter"),
            handle_result,
        )

    def _remove_reputation(self) -> None:
        character = self.selected_character
        if character is None:
            return
        if not character.reputations:
            self.notify("No Reputations to remove.")
            return

        labels = [f"{t.name}: {t.score}" for t in character.reputations]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del character.reputations[index]
                storage.save_saga(self.saga)
                self._refresh_character_section("section-reputations")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Reputation", labels), handle_result
        )

    def _edit_wounds(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(wounds: Wounds | None) -> None:
            if wounds is not None:
                character.wounds = wounds
                storage.save_saga(self.saga)
                self._refresh_character_section("section-wounds")

        self.app.push_screen(EditWoundsScreen(character.wounds), handle_result)

    def _edit_fatigue(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(level: FatigueLevel | None) -> None:
            if level is not None:
                character.fatigue_level = level
                storage.save_saga(self.saga)
                self._refresh_character_section("section-fatigue")

        self.app.push_screen(EditFatigueScreen(character.fatigue_level), handle_result)

    # -- Arts (magi only) --

    def _edit_arts(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(arts: dict[str, ArtScore] | None) -> None:
            if arts is not None:
                character.arts = arts
                storage.save_saga(self.saga)
                self._refresh_character_section("section-arts")

        self.app.push_screen(EditArtsScreen(character.arts), handle_result)

    # -- Raw Vis / Hermetic Background (magi only) --

    def _add_raw_vis(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(result: tuple[str, int] | None) -> None:
            if result is not None:
                art, pawns = result
                character.raw_vis[art] = character.raw_vis.get(art, 0) + pawns
                storage.save_saga(self.saga)
                self._refresh_character_section("section-raw-vis")

        self.app.push_screen(RawVisPromptScreen(), handle_result)

    def _remove_raw_vis(self) -> None:
        character = self.selected_character
        if character is None:
            return
        if not character.raw_vis:
            self.notify("No Raw Vis to remove.")
            return

        arts = sorted(character.raw_vis)
        labels = [f"{art.title()}: {character.raw_vis[art]} pawn(s)" for art in arts]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del character.raw_vis[arts[index]]
                storage.save_saga(self.saga)
                self._refresh_character_section("section-raw-vis")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Raw Vis entry", labels), handle_result
        )

    def _edit_hermetic_background(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(hermetic: HermeticBackground | None) -> None:
            if hermetic is not None:
                character.hermetic = hermetic
                storage.save_saga(self.saga)
                self._refresh_character_section("section-hermetic-background")

        self.app.push_screen(
            EditHermeticBackgroundScreen(character.hermetic), handle_result
        )

    # -- Spells known (magi only) --

    def _add_spell(self) -> None:
        character = self.selected_character
        if character is None:
            return
        known = set(character.spells_known)
        available = [s for s in self.saga.spells if s.id not in known]

        def handle_result(spell_id: str | None) -> None:
            if spell_id is not None:
                character.spells_known.append(spell_id)
                storage.save_saga(self.saga)
                self._refresh_character_section("tab-spells")

        self.app.push_screen(SpellPickerScreen(available), handle_result)

    def _remove_spell(self) -> None:
        character = self.selected_character
        if character is None:
            return
        if not character.spells_known:
            self.notify("No Spells to remove.")
            return

        spell_lookup = {s.id: s for s in self.saga.spells}
        labels = [
            spell_lookup[sid].name if sid in spell_lookup else f"{sid} (unknown spell)"
            for sid in character.spells_known
        ]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del character.spells_known[index]
                storage.save_saga(self.saga)
                self._refresh_character_section("tab-spells")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Known Spell", labels), handle_result
        )

    # -- Inventory --

    def _add_item(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(item: str | None) -> None:
            if item is not None:
                character.inventory.append(item)
                storage.save_saga(self.saga)
                self._refresh_character_section("section-inventory")

        self.app.push_screen(ItemAddScreen(), handle_result)

    def _remove_item(self) -> None:
        character = self.selected_character
        if character is None:
            return
        if not character.inventory:
            self.notify("No Items to remove.")
            return

        def handle_result(index: int | None) -> None:
            if index is not None:
                del character.inventory[index]
                storage.save_saga(self.saga)
                self._refresh_character_section("section-inventory")

        self.app.push_screen(
            RemovalPickerScreen("Remove an Item", list(character.inventory)),
            handle_result,
        )

    # -- Laboratory: Identity / Characteristics --

    def _edit_lab_identity(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(result: dict[str, object] | None) -> None:
            if result is None:
                return
            lab.name = result["name"]
            lab.location = result["location"]
            lab.build_points = result["build_points"]
            self._assign_laboratory_owner(lab, result["owner_id"])
            storage.save_saga(self.saga)
            self._rebuild_tree()
            self._refresh_laboratory_section("section-lab-identity")

        self.app.push_screen(EditLabIdentityScreen(self.saga, lab), handle_result)

    def _edit_lab_characteristics(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(characteristics: LabCharacteristics | None) -> None:
            if characteristics is not None:
                lab.characteristics = characteristics
                storage.save_saga(self.saga)
                self._refresh_laboratory_section("section-lab-characteristics")

        self.app.push_screen(
            EditLabCharacteristicsScreen(lab.characteristics), handle_result
        )

    # -- Laboratory: Specialties / Features / Rooms --

    def _add_specialty(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(item: str | None) -> None:
            if item is not None:
                lab.specialties.append(item)
                storage.save_saga(self.saga)
                self._refresh_laboratory_section("section-lab-specialties")

        self.app.push_screen(ItemAddScreen(), handle_result)

    def _remove_specialty(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.specialties:
            self.notify("No Specialties to remove.")
            return

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.specialties[index]
                storage.save_saga(self.saga)
                self._refresh_laboratory_section("section-lab-specialties")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Specialty", list(lab.specialties)),
            handle_result,
        )

    def _add_feature(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(item: str | None) -> None:
            if item is not None:
                lab.features.append(item)
                storage.save_saga(self.saga)
                self._refresh_laboratory_section("section-lab-features")

        self.app.push_screen(ItemAddScreen(), handle_result)

    def _remove_feature(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.features:
            self.notify("No Features to remove.")
            return

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.features[index]
                storage.save_saga(self.saga)
                self._refresh_laboratory_section("section-lab-features")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Feature", list(lab.features)), handle_result
        )

    def _add_room(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(room: NamedDescription | None) -> None:
            if room is not None:
                lab.rooms.append(room)
                storage.save_saga(self.saga)
                self._refresh_laboratory_section("section-lab-rooms")

        self.app.push_screen(
            NamedDescriptionPromptScreen("Add a Room", "e.g. Vault"), handle_result
        )

    def _remove_room(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.rooms:
            self.notify("No Rooms to remove.")
            return

        labels = [room.name for room in lab.rooms]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.rooms[index]
                storage.save_saga(self.saga)
                self._refresh_laboratory_section("section-lab-rooms")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Room", labels), handle_result
        )

    # -- Laboratory: Raw Vis / Items --

    def _add_lab_raw_vis(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(result: tuple[str, int] | None) -> None:
            if result is not None:
                art, pawns = result
                lab.raw_vis[art] = lab.raw_vis.get(art, 0) + pawns
                storage.save_saga(self.saga)
                self._refresh_laboratory_section("section-lab-raw-vis")

        self.app.push_screen(RawVisPromptScreen(), handle_result)

    def _remove_lab_raw_vis(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.raw_vis:
            self.notify("No Raw Vis to remove.")
            return

        arts = sorted(lab.raw_vis)
        labels = [f"{art.title()}: {lab.raw_vis[art]} pawn(s)" for art in arts]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.raw_vis[arts[index]]
                storage.save_saga(self.saga)
                self._refresh_laboratory_section("section-lab-raw-vis")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Raw Vis entry", labels), handle_result
        )

    def _add_inventory_item(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(item: NamedDescription | None) -> None:
            if item is not None:
                lab.inventory_items.append(item)
                storage.save_saga(self.saga)
                self._refresh_laboratory_section("section-lab-items")

        self.app.push_screen(
            NamedDescriptionPromptScreen("Add an Item", "e.g. Silver Mirror"),
            handle_result,
        )

    def _remove_inventory_item(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.inventory_items:
            self.notify("No Items to remove.")
            return

        labels = [item.name for item in lab.inventory_items]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.inventory_items[index]
                storage.save_saga(self.saga)
                self._refresh_laboratory_section("section-lab-items")

        self.app.push_screen(
            RemovalPickerScreen("Remove an Item", labels), handle_result
        )

    # -- Laboratory: Diary --

    def _add_diary_entry(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return

        def handle_result(entry: DiaryEntry | None) -> None:
            if entry is not None:
                lab.diary.append(entry)
                storage.save_saga(self.saga)
                self._refresh_laboratory_section("tab-lab-diary")

        self.app.push_screen(
            DiaryEntryPromptScreen(self.saga.current_year), handle_result
        )

    def _remove_diary_entry(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        if not lab.diary:
            self.notify("No Diary entries to remove.")
            return

        labels = [f"{entry.year} {entry.season} -- {entry.name}" for entry in lab.diary]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del lab.diary[index]
                storage.save_saga(self.saga)
                self._refresh_laboratory_section("tab-lab-diary")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Diary Entry", labels), handle_result
        )

    # -- shared Character/Laboratory Virtue & Flaw actions --

    def action_add_virtue_flaw(self) -> None:
        target = self._virtue_flaw_target()
        if target is None:
            return
        existing_ids = {vf.vf_id for vf in target.virtues_flaws}
        is_lab = self.selected_kind == "laboratory"
        picker = LabVirtueFlawPickerScreen if is_lab else VirtueFlawPickerScreen

        def handle_result(instance: VirtueFlawInstance | None) -> None:
            if instance is not None:
                target.virtues_flaws.append(instance)
                storage.save_saga(self.saga)
                if is_lab:
                    self._refresh_laboratory_section("tab-lab-vf")
                else:
                    self._refresh_character_section("section-vf")

        self.app.push_screen(picker(existing_ids), handle_result)

    def action_remove_virtue_flaw(self) -> None:
        target = self._virtue_flaw_target()
        if target is None:
            return
        if not target.virtues_flaws:
            self.notify("No Virtues/Flaws to remove.")
            return

        is_lab = self.selected_kind == "laboratory"
        vf_catalog = (
            catalog.load_lab_virtue_flaw_catalog_by_id()
            if is_lab
            else catalog.load_virtue_flaw_catalog_by_id()
        )
        labels = [
            catalog.describe_virtue_flaw(vf, vf_catalog) for vf in target.virtues_flaws
        ]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del target.virtues_flaws[index]
                storage.save_saga(self.saga)
                if is_lab:
                    self._refresh_laboratory_section("tab-lab-vf")
                else:
                    self._refresh_character_section("section-vf")

        self.app.push_screen(
            RemovalPickerScreen("Remove a Virtue or Flaw", labels), handle_result
        )

    def _virtue_flaw_target(self) -> Character | Laboratory | None:
        if (
            self.selected_kind == "laboratory"
            and self._active_section() == "tab-lab-vf"
        ):
            return self.selected_laboratory
        if self.selected_kind == "character" and self._active_section() == "section-vf":
            return self.selected_character
        return None


class SagaPickerScreen(Screen[None]):
    """Lists existing sagas and offers to create a new one."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("n", "create_saga", "New Saga"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            "Select a saga to open, or press 'n' to create a new one.",
            id="picker-hint",
        )
        yield ListView(id="saga-list")
        yield Footer()

    async def on_mount(self) -> None:
        await self.refresh_list()

    async def refresh_list(self) -> None:
        list_view = self.query_one("#saga-list", ListView)
        # Must be awaited before re-adding items below, or a same-id item not
        # yet removed collides with its freshly-mounted replacement and
        # Textual raises DuplicateIds.
        await list_view.clear()

        saga_ids = storage.list_sagas()
        if not saga_ids:
            await list_view.append(
                ListItem(Label("No sagas yet -- press 'n' to create one."))
            )
            return

        items = []
        for saga_id in saga_ids:
            saga = storage.load_saga(saga_id)
            summary = (
                f"{saga.name}  —  Storyguide: {saga.storyguide or '(unset)'}"
                f"  —  {saga.current_season} {saga.current_year}"
            )
            items.append(
                ListItem(Label(summary), id=f"{_SAGA_ITEM_ID_PREFIX}{saga_id}")
            )
        await list_view.extend(items)
        # append()/extend() don't set an initial highlight the way construction-time
        # children do, so keyboard/enter selection wouldn't work without this.
        list_view.index = 0

    def action_create_saga(self) -> None:
        async def handle_result(saga_id: str | None) -> None:
            if saga_id is not None:
                await self.refresh_list()

        self.app.push_screen(SagaCreateScreen(), handle_result)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id
        if item_id is None or not item_id.startswith(_SAGA_ITEM_ID_PREFIX):
            return
        saga_id = item_id.removeprefix(_SAGA_ITEM_ID_PREFIX)
        saga = storage.load_saga(saga_id)
        self.app.push_screen(WorkspaceScreen(saga))
