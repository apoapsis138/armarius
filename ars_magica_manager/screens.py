"""Saga picker/creator screens. See DESIGN.md section 7, Phase 1."""

from __future__ import annotations

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen, Screen
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
)

from . import catalog, storage
from .models import (
    FORMS,
    SEASONS,
    TECHNIQUES,
    Ability,
    Character,
    Covenant,
    Laboratory,
    Library,
    Saga,
    VirtueFlawInstance,
)

_SAGA_ITEM_ID_PREFIX = "saga-"
_COVENANT_ITEM_ID_PREFIX = "covenant-"
_CHARACTER_ITEM_ID_PREFIX = "character-"
_LABORATORY_ITEM_ID_PREFIX = "laboratory-"
_LIBRARY_ITEM_ID_PREFIX = "library-"
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


class SagaDetailScreen(Screen[None]):
    """Saga summary plus a browsable list of its covenants."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("n", "create_covenant", "New Covenant"),
        ("escape", "app.pop_screen", "Back"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, saga: Saga) -> None:
        super().__init__()
        self.saga = saga

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(self._summary(), id="saga-detail")
        yield Static("Covenants", id="covenant-list-heading")
        yield ListView(id="covenant-list")
        yield Footer()

    def on_mount(self) -> None:
        self._populate_covenant_list()

    def action_create_covenant(self) -> None:
        def handle_result(covenant_id: str | None) -> None:
            if covenant_id is not None:
                self._populate_covenant_list()

        self.app.push_screen(CovenantCreateScreen(self.saga), handle_result)

    def _summary(self) -> str:
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
            f"Characters: {len(saga.characters)}",
            f"Laboratories: {len(saga.laboratories)}",
            f"Libraries: {len(saga.libraries)}",
            f"Books: {len(saga.books)}",
            f"Spells: {len(saga.spells)}",
        ]
        return "\n".join(lines)

    def _populate_covenant_list(self) -> None:
        list_view = self.query_one("#covenant-list", ListView)
        list_view.clear()

        if not self.saga.covenants:
            list_view.append(
                ListItem(
                    Label(
                        "No covenants yet -- covenant creation is coming in a "
                        "future Phase 1 slice."
                    )
                )
            )
            return

        for covenant in self.saga.covenants:
            character_count = sum(
                1 for c in self.saga.characters if c.covenant_id == covenant.id
            )
            lab_count = sum(
                1 for lab in self.saga.laboratories if lab.covenant_id == covenant.id
            )
            summary = (
                f"{covenant.name}  —  {character_count} character(s), "
                f"{lab_count} lab(s)"
            )
            list_view.append(
                ListItem(Label(summary), id=f"{_COVENANT_ITEM_ID_PREFIX}{covenant.id}")
            )
        list_view.index = 0

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id
        if item_id is None or not item_id.startswith(_COVENANT_ITEM_ID_PREFIX):
            return
        covenant_id = item_id.removeprefix(_COVENANT_ITEM_ID_PREFIX)
        covenant = next(c for c in self.saga.covenants if c.id == covenant_id)
        self.app.push_screen(CovenantDetailScreen(self.saga, covenant))


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


class CovenantDetailScreen(Screen[None]):
    """Covenant summary (vis stock, notes) plus browsable Character/Lab/Library lists."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("n", "create_character", "New Character"),
        ("l", "create_laboratory", "New Laboratory"),
        ("escape", "app.pop_screen", "Back"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, saga: Saga, covenant: Covenant) -> None:
        super().__init__()
        self.saga = saga
        self.covenant = covenant

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(self._summary(), id="covenant-detail")
        yield Static("Characters", id="character-list-heading")
        yield ListView(id="character-list")
        yield Static("Laboratories", id="laboratory-list-heading")
        yield ListView(id="laboratory-list")
        yield Static("Library", id="library-list-heading")
        yield ListView(id="library-list")
        yield Footer()

    def on_mount(self) -> None:
        self._populate_character_list()
        self._populate_laboratory_list()
        self._populate_library_list()

    def action_create_laboratory(self) -> None:
        def handle_result(lab_id: str | None) -> None:
            if lab_id is not None:
                self._populate_laboratory_list()

        self.app.push_screen(
            LaboratoryCreateScreen(self.saga, self.covenant), handle_result
        )

    def action_create_character(self) -> None:
        def handle_result(character_id: str | None) -> None:
            if character_id is not None:
                self._populate_character_list()

        self.app.push_screen(
            CharacterCreateScreen(self.saga, default_covenant_id=self.covenant.id),
            handle_result,
        )

    def _summary(self) -> str:
        covenant = self.covenant
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

    def _populate_character_list(self) -> None:
        list_view = self.query_one("#character-list", ListView)
        list_view.clear()

        characters = [
            c for c in self.saga.characters if c.covenant_id == self.covenant.id
        ]
        if not characters:
            list_view.append(ListItem(Label("(none)")))
            return

        for character in characters:
            list_view.append(
                ListItem(
                    Label(f"{character.name} ({character.type})"),
                    id=f"{_CHARACTER_ITEM_ID_PREFIX}{character.id}",
                )
            )
        list_view.index = 0

    def _populate_laboratory_list(self) -> None:
        list_view = self.query_one("#laboratory-list", ListView)
        list_view.clear()

        labs = [
            lab for lab in self.saga.laboratories if lab.covenant_id == self.covenant.id
        ]
        if not labs:
            list_view.append(ListItem(Label("(none)")))
            return

        for lab in labs:
            owner = next(
                (c for c in self.saga.characters if c.id == lab.owner_id), None
            )
            label = f"{lab.name}  —  owner: {owner.name if owner else 'unassigned'}"
            list_view.append(
                ListItem(Label(label), id=f"{_LABORATORY_ITEM_ID_PREFIX}{lab.id}")
            )
        list_view.index = 0

    def _populate_library_list(self) -> None:
        list_view = self.query_one("#library-list", ListView)
        list_view.clear()

        library = next(
            (lib for lib in self.saga.libraries if lib.id == self.covenant.library_id),
            None,
        )
        if library is None:
            list_view.append(ListItem(Label("(none)")))
            return

        list_view.append(
            ListItem(
                Label(f"Library ({len(library.books)} book(s))"),
                id=f"{_LIBRARY_ITEM_ID_PREFIX}{library.id}",
            )
        )
        list_view.index = 0

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id
        if item_id is None:
            return

        if event.list_view.id == "character-list" and item_id.startswith(
            _CHARACTER_ITEM_ID_PREFIX
        ):
            character_id = item_id.removeprefix(_CHARACTER_ITEM_ID_PREFIX)
            character = next(c for c in self.saga.characters if c.id == character_id)
            self.app.push_screen(CharacterDetailScreen(self.saga, character))
        elif event.list_view.id == "laboratory-list" and item_id.startswith(
            _LABORATORY_ITEM_ID_PREFIX
        ):
            lab_id = item_id.removeprefix(_LABORATORY_ITEM_ID_PREFIX)
            lab = next(lab for lab in self.saga.laboratories if lab.id == lab_id)
            self.app.push_screen(LaboratoryDetailScreen(self.saga, lab))
        elif event.list_view.id == "library-list" and item_id.startswith(
            _LIBRARY_ITEM_ID_PREFIX
        ):
            library_id = item_id.removeprefix(_LIBRARY_ITEM_ID_PREFIX)
            library = next(lib for lib in self.saga.libraries if lib.id == library_id)
            self.app.push_screen(LibraryDetailScreen(self.saga, library))


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


class EditArtsScreen(ModalScreen[dict[str, int] | None]):
    """Edits all 15 Hermetic Arts at once -- a fixed grid, not an addable list.

    Forms (10, in two columns of 5) on the left, Techniques (5, one
    column) on the right. Dismisses with a dict of every art's lowercase
    name -> score, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditArtsScreen {
        align: center middle;
    }

    #arts-dialog {
        width: auto;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    .art-column {
        width: auto;
        margin-right: 3;
    }

    .art-row {
        height: auto;
    }

    .art-row Label {
        width: 11;
        content-align: right middle;
        padding-right: 1;
    }

    .art-row Input {
        width: 8;
    }

    #arts-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, arts: dict[str, int]) -> None:
        super().__init__()
        self.arts = arts

    def compose(self) -> ComposeResult:
        def row(art_name: str):
            key = art_name.lower()
            yield Label(art_name)
            yield Input(
                value=str(self.arts.get(key, 0)),
                type="integer",
                id=f"input-art-{key}",
            )

        with Vertical(id="arts-dialog"):
            yield Label("Edit Arts", id="arts-title")
            with Horizontal():
                with Vertical(classes="art-column"):
                    yield Label("Forms", classes="column-heading")
                    with Horizontal():
                        with Vertical():
                            for form in FORMS[:5]:
                                with Horizontal(classes="art-row"):
                                    yield from row(form)
                        with Vertical():
                            for form in FORMS[5:]:
                                with Horizontal(classes="art-row"):
                                    yield from row(form)
                with Vertical(classes="art-column"):
                    yield Label("Techniques", classes="column-heading")
                    for technique in TECHNIQUES:
                        with Horizontal(classes="art-row"):
                            yield from row(technique)
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
        result: dict[str, int] = {}
        for art_name in (*TECHNIQUES, *FORMS):
            key = art_name.lower()
            raw = self.query_one(f"#input-art-{key}", Input).value.strip()
            try:
                result[key] = int(raw)
            except ValueError:
                error.update(f"{art_name} must be a whole number.")
                return
        self.dismiss(result)


class CharacterDetailScreen(Screen[None]):
    """Character sheet summary; can add Abilities, Virtues/Flaws, and (for
    magi) edit Arts.
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        ("a", "add_ability", "Add Ability"),
        ("A", "remove_ability", "Remove Ability"),
        ("v", "add_virtue_flaw", "Add Virtue/Flaw"),
        ("V", "remove_virtue_flaw", "Remove Virtue/Flaw"),
        ("e", "edit_arts", "Edit Arts"),
        ("escape", "app.pop_screen", "Back"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, saga: Saga, character: Character) -> None:
        super().__init__()
        self.saga = saga
        self.character = character

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(self._summary(), id="character-detail")
        yield Footer()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        return action != "edit_arts" or self.character.type == "magus"

    def action_edit_arts(self) -> None:
        def handle_result(arts: dict[str, int] | None) -> None:
            if arts is not None:
                self.character.arts = arts
                storage.save_saga(self.saga)
                self._refresh_summary()

        self.app.push_screen(EditArtsScreen(self.character.arts), handle_result)

    def action_add_ability(self) -> None:
        exclude_names = {a.name for a in self.character.abilities}

        def handle_result(ability: Ability | None) -> None:
            if ability is not None:
                self.character.abilities.append(ability)
                storage.save_saga(self.saga)
                self._refresh_summary()

        self.app.push_screen(AbilityPickerScreen(exclude_names), handle_result)

    def action_remove_ability(self) -> None:
        if not self.character.abilities:
            self.notify("No Abilities to remove.")
            return

        labels = [
            f"{a.name} {a.score}" + (f" ({a.specialty})" if a.specialty else "")
            for a in self.character.abilities
        ]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del self.character.abilities[index]
                storage.save_saga(self.saga)
                self._refresh_summary()

        self.app.push_screen(
            RemovalPickerScreen("Remove an Ability", labels), handle_result
        )

    def action_add_virtue_flaw(self) -> None:
        existing_ids = {vf.vf_id for vf in self.character.virtues_flaws}

        def handle_result(instance: VirtueFlawInstance | None) -> None:
            if instance is not None:
                self.character.virtues_flaws.append(instance)
                storage.save_saga(self.saga)
                self._refresh_summary()

        self.app.push_screen(VirtueFlawPickerScreen(existing_ids), handle_result)

    def action_remove_virtue_flaw(self) -> None:
        if not self.character.virtues_flaws:
            self.notify("No Virtues/Flaws to remove.")
            return

        vf_catalog = catalog.load_virtue_flaw_catalog_by_id()
        labels = [
            catalog.describe_virtue_flaw(vf, vf_catalog)
            for vf in self.character.virtues_flaws
        ]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del self.character.virtues_flaws[index]
                storage.save_saga(self.saga)
                self._refresh_summary()

        self.app.push_screen(
            RemovalPickerScreen("Remove a Virtue or Flaw", labels), handle_result
        )

    def _refresh_summary(self) -> None:
        self.query_one("#character-detail", Static).update(self._summary())

    def _summary(self) -> str:
        saga, character = self.saga, self.character
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
                    f"  {art.title()}: {score}" for art, score in character.arts.items()
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


class LaboratoryDetailScreen(Screen[None]):
    """Laboratory summary; can add Virtues/Flaws from the catalog."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("v", "add_virtue_flaw", "Add Virtue/Flaw"),
        ("V", "remove_virtue_flaw", "Remove Virtue/Flaw"),
        ("escape", "app.pop_screen", "Back"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, saga: Saga, laboratory: Laboratory) -> None:
        super().__init__()
        self.saga = saga
        self.laboratory = laboratory

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(self._summary(), id="laboratory-detail")
        yield Footer()

    def action_add_virtue_flaw(self) -> None:
        existing_ids = {vf.vf_id for vf in self.laboratory.virtues_flaws}

        def handle_result(instance: VirtueFlawInstance | None) -> None:
            if instance is not None:
                self.laboratory.virtues_flaws.append(instance)
                storage.save_saga(self.saga)
                self._refresh_summary()

        self.app.push_screen(VirtueFlawPickerScreen(existing_ids), handle_result)

    def action_remove_virtue_flaw(self) -> None:
        if not self.laboratory.virtues_flaws:
            self.notify("No Virtues/Flaws to remove.")
            return

        vf_catalog = catalog.load_virtue_flaw_catalog_by_id()
        labels = [
            catalog.describe_virtue_flaw(vf, vf_catalog)
            for vf in self.laboratory.virtues_flaws
        ]

        def handle_result(index: int | None) -> None:
            if index is not None:
                del self.laboratory.virtues_flaws[index]
                storage.save_saga(self.saga)
                self._refresh_summary()

        self.app.push_screen(
            RemovalPickerScreen("Remove a Virtue or Flaw", labels), handle_result
        )

    def _refresh_summary(self) -> None:
        self.query_one("#laboratory-detail", Static).update(self._summary())

    def _summary(self) -> str:
        saga, lab = self.saga, self.laboratory
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


class LibraryDetailScreen(Screen[None]):
    """Read-only library summary: every book it holds."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("escape", "app.pop_screen", "Back"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, saga: Saga, library: Library) -> None:
        super().__init__()
        self.saga = saga
        self.library = library

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(self._summary(), id="library-detail")
        yield Footer()

    def _summary(self) -> str:
        saga, library = self.saga, self.library
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

    def on_mount(self) -> None:
        self.refresh_list()

    def refresh_list(self) -> None:
        list_view = self.query_one("#saga-list", ListView)
        list_view.clear()

        saga_ids = storage.list_sagas()
        if not saga_ids:
            list_view.append(
                ListItem(Label("No sagas yet -- press 'n' to create one."))
            )
            return

        for saga_id in saga_ids:
            saga = storage.load_saga(saga_id)
            summary = (
                f"{saga.name}  —  Storyguide: {saga.storyguide or '(unset)'}"
                f"  —  {saga.current_season} {saga.current_year}"
            )
            list_view.append(
                ListItem(Label(summary), id=f"{_SAGA_ITEM_ID_PREFIX}{saga_id}")
            )
        # append()/extend() don't set an initial highlight the way construction-time
        # children do, so keyboard/enter selection wouldn't work without this.
        list_view.index = 0

    def action_create_saga(self) -> None:
        def handle_result(saga_id: str | None) -> None:
            if saga_id is not None:
                self.refresh_list()

        self.app.push_screen(SagaCreateScreen(), handle_result)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id
        if item_id is None or not item_id.startswith(_SAGA_ITEM_ID_PREFIX):
            return
        saga_id = item_id.removeprefix(_SAGA_ITEM_ID_PREFIX)
        saga = storage.load_saga(saga_id)
        self.app.push_screen(SagaDetailScreen(saga))
