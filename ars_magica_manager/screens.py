"""Saga picker/creator screens. See DESIGN.md section 7, Phase 1."""

from __future__ import annotations

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.css.query import NoMatches
from textual.screen import ModalScreen, Screen
from textual.widget import Widget
from textual.widgets import (
    Button,
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
    FORMS,
    SEASONS,
    TECHNIQUES,
    Ability,
    ArtScore,
    Character,
    Characteristics,
    Covenant,
    Laboratory,
    Library,
    Saga,
    Spell,
    VirtueFlawInstance,
)

_SAGA_ITEM_ID_PREFIX = "saga-"
_VIRTUE_FLAW_ITEM_ID_PREFIX = "vf-"
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


class VirtueFlawPickerScreen(ModalScreen[VirtueFlawInstance | None]):
    """Pick a Virtue/Flaw from the catalog, prompting for parameters if needed.

    Reused for both Character and Laboratory Virtues/Flaws -- both attach
    the same VirtueFlawInstance shape. Dismisses with the new instance, or
    None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    VirtueFlawPickerScreen {
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

    def __init__(self, exclude_ids: set[str] | None = None) -> None:
        super().__init__()
        self._exclude_ids = exclude_ids or set()

    def compose(self) -> ComposeResult:
        with Vertical(id="picker-dialog"):
            yield Label("Add a Virtue or Flaw", id="picker-title")
            yield ListView(id="vf-picker-list")
            yield Button("Cancel", id="btn-cancel")

    def on_mount(self) -> None:
        list_view = self.query_one("#vf-picker-list", ListView)
        entries = [
            entry
            for entry in catalog.load_virtue_flaw_catalog()
            if entry.id not in self._exclude_ids
        ]
        if not entries:
            list_view.append(ListItem(Label("(no more Virtues/Flaws available)")))
            return

        for entry in entries:
            needs = (
                f"  (needs: {', '.join(entry.parameters)})" if entry.parameters else ""
            )
            label = f"{entry.name}  [{entry.type}, cost {entry.cost}]{needs}"
            list_view.append(
                ListItem(Label(label), id=f"{_VIRTUE_FLAW_ITEM_ID_PREFIX}{entry.id}")
            )
        list_view.index = 0

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id
        if item_id is None or not item_id.startswith(_VIRTUE_FLAW_ITEM_ID_PREFIX):
            return
        vf_id = item_id.removeprefix(_VIRTUE_FLAW_ITEM_ID_PREFIX)
        entry = catalog.load_virtue_flaw_catalog_by_id()[vf_id]

        if not entry.parameters:
            self.dismiss(VirtueFlawInstance(vf_id=entry.id))
            return

        def handle_params(params: dict[str, str] | None) -> None:
            if params is not None:
                self.dismiss(VirtueFlawInstance(vf_id=entry.id, params=params))

        self.app.push_screen(
            ParamPromptScreen(entry.name, entry.parameters), handle_params
        )


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


class AbilityPickerScreen(ModalScreen[Ability | None]):
    """Pick an Ability from the catalog, resolve any parameter, set score/specialty.

    Non-templated entries already held are excluded (no point in a second
    "Athletics" row); templated entries ("Craft: {craft}") stay available
    since a character can hold several distinct instances of the same
    family. Dismisses with the new Ability, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    AbilityPickerScreen {
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

    def __init__(self, exclude_names: set[str] | None = None) -> None:
        super().__init__()
        self._exclude_names = exclude_names or set()

    def compose(self) -> ComposeResult:
        with Vertical(id="picker-dialog"):
            yield Label("Add an Ability", id="picker-title")
            yield ListView(id="ability-picker-list")
            yield Button("Cancel", id="btn-cancel")

    def on_mount(self) -> None:
        list_view = self.query_one("#ability-picker-list", ListView)
        entries = [
            entry
            for entry in catalog.load_ability_catalog()
            if entry.parameters or entry.name not in self._exclude_names
        ]
        if not entries:
            list_view.append(ListItem(Label("(no more Abilities available)")))
            return

        for entry in entries:
            needs = (
                f"  (needs: {', '.join(entry.parameters)})" if entry.parameters else ""
            )
            label = f"{entry.name}  [{entry.category}]{needs}"
            list_view.append(
                ListItem(Label(label), id=f"{_ABILITY_ITEM_ID_PREFIX}{entry.id}")
            )
        list_view.index = 0

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id
        if item_id is None or not item_id.startswith(_ABILITY_ITEM_ID_PREFIX):
            return
        ability_id = item_id.removeprefix(_ABILITY_ITEM_ID_PREFIX)
        entry = catalog.load_ability_catalog_by_id()[ability_id]

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
            with Horizontal():
                yield Label("Size")
                yield Input(value="0", type="integer", id="input-size")
                yield Label("Aura")
                yield Input(value="0", type="integer", id="input-aura")
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

        try:
            aura = int(self.query_one("#input-aura", Input).value.strip())
        except ValueError:
            error.update("Aura must be a whole number.")
            return

        laboratory = Laboratory(
            id=storage.generate_unique_id(
                name, [lab.id for lab in self.saga.laboratories]
            ),
            covenant_id=self.covenant.id,
            name=name,
            size=size,
            aura=aura,
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


class CharacterSheetView(Vertical):
    """The tabbed character sheet mounted into WorkspaceScreen's detail pane.

    Each section is its own tab, rendered as plain text for now (matching
    the rest of the app's read-then-refresh style): Identity,
    Characteristics, Abilities (grouped by category), Virtues & Flaws
    (grouped Virtue/Flaw, tagged Minor/Major), and -- magi only -- Arts
    (Techniques then Forms), Spells known, and Inventory.
    """

    DEFAULT_CSS = """
    CharacterSheetView {
        height: 1fr;
    }

    CharacterSheetView TabPane {
        padding: 1 0;
    }
    """

    def __init__(self, saga: Saga, character: Character) -> None:
        super().__init__()
        self.saga = saga
        self.character = character

    def compose(self) -> ComposeResult:
        with TabbedContent(initial="tab-identity"):
            with TabPane("Identity", id="tab-identity"):
                yield Static(self._identity_text(), id="identity-content")
            with TabPane("Characteristics", id="tab-characteristics"):
                yield Static(self._characteristics_text(), id="characteristics-content")
            with TabPane("Abilities", id="tab-abilities"):
                yield Static(self._abilities_text(), id="abilities-content")
            with TabPane("Virtues & Flaws", id="tab-vf"):
                yield Static(self._vf_text(), id="vf-content")
            if self.character.type == "magus":
                with TabPane("Arts", id="tab-arts"):
                    yield Static(self._arts_text(), id="arts-content")
                with TabPane("Spells", id="tab-spells"):
                    yield Static(self._spells_text(), id="spells-content")
            with TabPane("Inventory", id="tab-inventory"):
                yield Static(self._inventory_text(), id="inventory-content")

    _TAB_CONTENT: ClassVar[dict[str, str]] = {
        "tab-identity": "#identity-content",
        "tab-characteristics": "#characteristics-content",
        "tab-abilities": "#abilities-content",
        "tab-vf": "#vf-content",
        "tab-arts": "#arts-content",
        "tab-spells": "#spells-content",
        "tab-inventory": "#inventory-content",
    }
    _TAB_TEXT: ClassVar[dict[str, str]] = {
        "tab-identity": "_identity_text",
        "tab-characteristics": "_characteristics_text",
        "tab-abilities": "_abilities_text",
        "tab-vf": "_vf_text",
        "tab-arts": "_arts_text",
        "tab-spells": "_spells_text",
        "tab-inventory": "_inventory_text",
    }

    def refresh_tab(self, tab_id: str) -> None:
        selector = self._TAB_CONTENT.get(tab_id)
        text_method = self._TAB_TEXT.get(tab_id)
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
                tier = (
                    catalog.virtue_flaw_tier(definition.cost)
                    if definition is not None
                    else "?"
                )
                lines.append(
                    f"  {catalog.describe_virtue_flaw(vf, vf_catalog)} ({tier})"
                )
            lines.append("")
        return "\n".join(lines).rstrip()

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

    #: Which character-sheet tabs support the generic Add/Remove/Edit
    #: bindings. 'a'/'A'/'e' dispatch by whichever tab is active instead of
    #: each having their own dedicated key, since a fully-built sheet has
    #: too many addable/editable sections for that to scale.
    _ADD_TABS: ClassVar[set[str]] = {"tab-abilities", "tab-spells", "tab-inventory"}
    _REMOVE_TABS: ClassVar[set[str]] = {"tab-abilities", "tab-spells", "tab-inventory"}
    _EDIT_TABS: ClassVar[set[str]] = {
        "tab-identity",
        "tab-characteristics",
        "tab-abilities",
        "tab-arts",
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
            return self._active_character_tab() in self._ADD_TABS
        if action == "remove":
            return self._active_character_tab() in self._REMOVE_TABS
        if action == "edit":
            return self._active_character_tab() in self._EDIT_TABS
        if action in ("add_virtue_flaw", "remove_virtue_flaw"):
            if self.selected_kind == "laboratory":
                return True
            return self._active_character_tab() == "tab-vf"
        return True

    def _active_character_tab(self) -> str | None:
        if self.selected_kind != "character" or self._character_sheet_view is None:
            return None
        try:
            return self._character_sheet_view.query_one(TabbedContent).active
        except NoMatches:
            return None

    def on_tabbed_content_tab_activated(
        self, event: TabbedContent.TabActivated
    ) -> None:
        # Keep the Footer's binding hints (and check_action gating) in sync
        # with whichever tab the user just switched to.
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
        lines = [f"Covenant: {covenant.name}", f"Saga: {self.saga.name}"]
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
        await self._set_detail(
            Static(self._laboratory_summary(lab), id="laboratory-detail")
        )

    def _laboratory_summary(self, lab: Laboratory) -> str:
        saga = self.saga
        vf_catalog = catalog.load_virtue_flaw_catalog_by_id()

        covenant = next((c for c in saga.covenants if c.id == lab.covenant_id), None)
        owner = next((c for c in saga.characters if c.id == lab.owner_id), None)

        lines = [
            f"Laboratory: {lab.name}",
            f"Covenant: {covenant.name if covenant else '(none)'}",
            f"Owner: {owner.name if owner else '(unassigned)'}",
            f"Size: {lab.size}",
            f"Aura: {lab.aura}",
        ]

        lines.append("")
        if lab.features:
            lines.append("Features:")
            lines += [f"  - {feature}" for feature in lab.features]
        else:
            lines.append("Features: (none recorded)")

        lines.append("")
        if lab.virtues_flaws:
            lines.append("Virtues & Flaws:")
            lines += [
                f"  {catalog.describe_virtue_flaw(vf, vf_catalog)}"
                for vf in lab.virtues_flaws
            ]
        else:
            lines.append("Virtues & Flaws: (none recorded)")

        return "\n".join(lines)

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

    def _refresh_character_tab(self, tab_id: str) -> None:
        if self._character_sheet_view is not None:
            self._character_sheet_view.refresh_tab(tab_id)

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

    def _refresh_laboratory_detail(self) -> None:
        if self.selected_laboratory is None:
            return
        self.query_one("#laboratory-detail", Static).update(
            self._laboratory_summary(self.selected_laboratory)
        )

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

    # -- generic Add/Remove/Edit dispatch, by active character-sheet tab --

    def action_add(self) -> None:
        tab = self._active_character_tab()
        if tab == "tab-abilities":
            self._add_ability()
        elif tab == "tab-spells":
            self._add_spell()
        elif tab == "tab-inventory":
            self._add_item()

    def action_remove(self) -> None:
        tab = self._active_character_tab()
        if tab == "tab-abilities":
            self._remove_ability()
        elif tab == "tab-spells":
            self._remove_spell()
        elif tab == "tab-inventory":
            self._remove_item()

    def action_edit(self) -> None:
        tab = self._active_character_tab()
        if tab == "tab-identity":
            self._edit_identity()
        elif tab == "tab-characteristics":
            self._edit_characteristics()
        elif tab == "tab-abilities":
            self._edit_ability()
        elif tab == "tab-arts":
            self._edit_arts()

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
            self._refresh_character_tab("tab-identity")

        self.app.push_screen(IdentityEditScreen(self.saga, character), handle_result)

    def _edit_characteristics(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(characteristics: Characteristics | None) -> None:
            if characteristics is not None:
                character.characteristics = characteristics
                storage.save_saga(self.saga)
                self._refresh_character_tab("tab-characteristics")

        self.app.push_screen(
            EditCharacteristicsScreen(character.characteristics), handle_result
        )

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
                self._refresh_character_tab("tab-abilities")

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
                self._refresh_character_tab("tab-abilities")

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
                    self._refresh_character_tab("tab-abilities")

            self.app.push_screen(
                AbilityDetailsScreen(existing.name, existing.category, existing),
                handle_result,
            )

        self.app.push_screen(
            RemovalPickerScreen("Edit which Ability?", labels), handle_index
        )

    # -- Arts (magi only) --

    def _edit_arts(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(arts: dict[str, ArtScore] | None) -> None:
            if arts is not None:
                character.arts = arts
                storage.save_saga(self.saga)
                self._refresh_character_tab("tab-arts")

        self.app.push_screen(EditArtsScreen(character.arts), handle_result)

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
                self._refresh_character_tab("tab-spells")

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
                self._refresh_character_tab("tab-spells")

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
                self._refresh_character_tab("tab-inventory")

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
                self._refresh_character_tab("tab-inventory")

        self.app.push_screen(
            RemovalPickerScreen("Remove an Item", list(character.inventory)),
            handle_result,
        )

    # -- shared Character/Laboratory Virtue & Flaw actions --

    def action_add_virtue_flaw(self) -> None:
        target = self._virtue_flaw_target()
        if target is None:
            return
        existing_ids = {vf.vf_id for vf in target.virtues_flaws}

        def handle_result(instance: VirtueFlawInstance | None) -> None:
            if instance is not None:
                target.virtues_flaws.append(instance)
                storage.save_saga(self.saga)
                if self.selected_kind == "character":
                    self._refresh_character_tab("tab-vf")
                else:
                    self._refresh_laboratory_detail()

        self.app.push_screen(VirtueFlawPickerScreen(existing_ids), handle_result)

    def action_remove_virtue_flaw(self) -> None:
        target = self._virtue_flaw_target()
        if target is None:
            return
        if not target.virtues_flaws:
            self.notify("No Virtues/Flaws to remove.")
            return

        vf_catalog = catalog.load_virtue_flaw_catalog_by_id()
        labels = [
            catalog.describe_virtue_flaw(vf, vf_catalog) for vf in target.virtues_flaws
        ]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del target.virtues_flaws[index]
                storage.save_saga(self.saga)
                if self.selected_kind == "character":
                    self._refresh_character_tab("tab-vf")
                else:
                    self._refresh_laboratory_detail()

        self.app.push_screen(
            RemovalPickerScreen("Remove a Virtue or Flaw", labels), handle_result
        )

    def _virtue_flaw_target(self) -> Character | Laboratory | None:
        if self.selected_kind == "laboratory":
            return self.selected_laboratory
        if (
            self.selected_kind == "character"
            and self._active_character_tab() == "tab-vf"
        ):
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
