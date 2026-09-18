"""Saga picker/creator screens. See DESIGN.md section 7, Phase 1."""

from __future__ import annotations

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
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
    Tree,
)

from . import catalog, storage
from .models import (
    ART_ABBREVIATIONS,
    FORMS,
    SEASONS,
    TECHNIQUES,
    Ability,
    ArtScore,
    Character,
    Covenant,
    Laboratory,
    Library,
    Saga,
    VirtueFlawInstance,
)

_SAGA_ITEM_ID_PREFIX = "saga-"
_VIRTUE_FLAW_ITEM_ID_PREFIX = "vf-"
_ABILITY_ITEM_ID_PREFIX = "ability-"
_REMOVAL_ITEM_ID_PREFIX = "remove-"


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
    """Prompts for score/specialty once an Ability's name is resolved.

    Dismisses with the finished Ability, or None if cancelled.
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

    def __init__(self, name: str) -> None:
        super().__init__()
        self.ability_name = name

    def compose(self) -> ComposeResult:
        with Vertical(id="details-dialog"):
            yield Label(self.ability_name, id="details-title")
            yield Label("Score")
            yield Input(value="0", type="integer", id="input-score")
            yield Label("Specialty (optional)")
            yield Input(placeholder="e.g. Swords", id="input-specialty")
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
            score = int(self.query_one("#input-score", Input).value.strip())
        except ValueError:
            error.update("Score must be a whole number.")
            return

        specialty = self.query_one("#input-specialty", Input).value.strip() or None
        self.dismiss(Ability(name=self.ability_name, score=score, specialty=specialty))


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
                    self._prompt_details(catalog.resolve_ability_name(entry, params))

            self.app.push_screen(
                ParamPromptScreen(entry.name, entry.parameters), handle_params
            )
        else:
            self._prompt_details(entry.name)

    def _prompt_details(self, name: str) -> None:
        def handle_ability(ability: Ability | None) -> None:
            if ability is not None:
                self.dismiss(ability)

        self.app.push_screen(AbilityDetailsScreen(name), handle_ability)


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

    Three columns of 5: Techniques (left, its own header), then Forms
    split across the middle and right columns (header only on the middle
    one, since the right column is just its continuation). Each Art shows
    a Level / XP pair. Dismisses with a dict of every art's lowercase name
    -> ArtScore, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditArtsScreen {
        align: center middle;
    }

    #arts-dialog {
        width: auto;
        max-width: 100%;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #arts-subtitle {
        color: $text-muted;
        margin-bottom: 1;
    }

    .art-column {
        width: auto;
        margin-right: 2;
    }

    .column-heading {
        text-style: bold;
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
            yield Label(art_name)
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
            yield Label("Each score is Level / XP", id="arts-subtitle")
            with Horizontal():
                with Vertical(classes="art-column"):
                    yield Label("Techniques", classes="column-heading")
                    for technique in TECHNIQUES:
                        with Horizontal(classes="art-row"):
                            yield from row(technique)
                with Vertical(classes="art-column"):
                    yield Label("Forms", classes="column-heading")
                    for form in FORMS[:5]:
                        with Horizontal(classes="art-row"):
                            yield from row(form)
                with Vertical(classes="art-column"):
                    yield Label("", classes="column-heading")
                    for form in FORMS[5:]:
                        with Horizontal(classes="art-row"):
                            yield from row(form)
            yield Static("", id="arts-error")
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
        ("a", "add_ability", "Add Ability"),
        ("A", "remove_ability", "Remove Ability"),
        ("v", "add_virtue_flaw", "Add Virtue/Flaw"),
        ("V", "remove_virtue_flaw", "Remove Virtue/Flaw"),
        ("e", "edit_arts", "Edit Arts"),
        ("escape", "app.pop_screen", "Back"),
        ("q", "quit", "Quit"),
    ]

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
        if action in ("add_ability", "remove_ability"):
            return self.selected_kind == "character"
        if action == "edit_arts":
            return (
                self.selected_kind == "character"
                and self.selected_character is not None
                and self.selected_character.type == "magus"
            )
        if action in ("add_virtue_flaw", "remove_virtue_flaw"):
            return self.selected_kind in ("character", "laboratory")
        return True

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
        await self._set_detail(
            Static(self._character_summary(character), id="character-detail")
        )

    def _character_summary(self, character: Character) -> str:
        saga = self.saga
        vf_catalog = catalog.load_virtue_flaw_catalog_by_id()

        covenant = next(
            (c for c in saga.covenants if c.id == character.covenant_id), None
        )

        lines = [
            f"Character: {character.name}",
            f"Type: {character.type}",
            f"Covenant: {covenant.name if covenant else '(none)'}",
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
            lines.append(f"Assigned Laboratory: {'yes' if lab else '(none)'}")

        c = character.characteristics
        lines += [
            "",
            "Characteristics:",
            f"  Int {c.intelligence}, Per {c.perception}, Str {c.strength}, "
            f"Sta {c.stamina}",
            f"  Pre {c.presence}, Com {c.communication}, Dex {c.dexterity}, "
            f"Qik {c.quickness}",
        ]

        if character.type == "magus":
            lines.append("")
            if character.arts:
                lines.append("Arts:")
                lines += [
                    f"  {art.title()} ({ART_ABBREVIATIONS.get(art.title(), '?')}): "
                    f"{score.level}/{score.xp}"
                    for art, score in character.arts.items()
                ]
            else:
                lines.append("Arts: (none recorded)")

        lines.append("")
        if character.abilities:
            lines.append("Abilities:")
            for ability in character.abilities:
                specialty = f" ({ability.specialty})" if ability.specialty else ""
                lines.append(f"  {ability.name} {ability.score}{specialty}")
        else:
            lines.append("Abilities: (none recorded)")

        lines.append("")
        if character.virtues_flaws:
            lines.append("Virtues & Flaws:")
            lines += [
                f"  {catalog.describe_virtue_flaw(vf, vf_catalog)}"
                for vf in character.virtues_flaws
            ]
        else:
            lines.append("Virtues & Flaws: (none recorded)")

        if character.type == "magus":
            lines.append("")
            if character.spells_known:
                spell_lookup = {s.id: s for s in saga.spells}
                lines.append("Spells known:")
                for spell_id in character.spells_known:
                    spell = spell_lookup.get(spell_id)
                    if spell is None:
                        lines.append(f"  {spell_id} (unknown spell)")
                    else:
                        lines.append(
                            f"  {spell.name} ({spell.technique} {spell.form} "
                            f"{spell.level})"
                        )
            else:
                lines.append("Spells known: (none recorded)")

        return "\n".join(lines)

    def _refresh_character_detail(self) -> None:
        if self.selected_character is None:
            return
        self.query_one("#character-detail", Static).update(
            self._character_summary(self.selected_character)
        )

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

    # -- character-only actions --

    def action_add_ability(self) -> None:
        character = self.selected_character
        if character is None:
            return
        exclude_names = {a.name for a in character.abilities}

        def handle_result(ability: Ability | None) -> None:
            if ability is not None:
                character.abilities.append(ability)
                storage.save_saga(self.saga)
                self._refresh_character_detail()

        self.app.push_screen(AbilityPickerScreen(exclude_names), handle_result)

    def action_remove_ability(self) -> None:
        character = self.selected_character
        if character is None:
            return
        if not character.abilities:
            self.notify("No Abilities to remove.")
            return

        labels = [
            f"{a.name} {a.score}" + (f" ({a.specialty})" if a.specialty else "")
            for a in character.abilities
        ]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del character.abilities[index]
                storage.save_saga(self.saga)
                self._refresh_character_detail()

        self.app.push_screen(
            RemovalPickerScreen("Remove an Ability", labels), handle_result
        )

    def action_edit_arts(self) -> None:
        character = self.selected_character
        if character is None:
            return

        def handle_result(arts: dict[str, ArtScore] | None) -> None:
            if arts is not None:
                character.arts = arts
                storage.save_saga(self.saga)
                self._refresh_character_detail()

        self.app.push_screen(EditArtsScreen(character.arts), handle_result)

    # -- shared Character/Laboratory Virtue & Flaw actions --

    def action_add_virtue_flaw(self) -> None:
        target = self.selected_character or self.selected_laboratory
        if target is None:
            return
        existing_ids = {vf.vf_id for vf in target.virtues_flaws}

        def handle_result(instance: VirtueFlawInstance | None) -> None:
            if instance is not None:
                target.virtues_flaws.append(instance)
                storage.save_saga(self.saga)
                if self.selected_character is not None:
                    self._refresh_character_detail()
                else:
                    self._refresh_laboratory_detail()

        self.app.push_screen(VirtueFlawPickerScreen(existing_ids), handle_result)

    def action_remove_virtue_flaw(self) -> None:
        target = self.selected_character or self.selected_laboratory
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
                if self.selected_character is not None:
                    self._refresh_character_detail()
                else:
                    self._refresh_laboratory_detail()

        self.app.push_screen(
            RemovalPickerScreen("Remove a Virtue or Flaw", labels), handle_result
        )


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
