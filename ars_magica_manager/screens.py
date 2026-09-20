"""Saga picker/creator screens. See DESIGN.md section 7, Phase 1."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.content import Content
from textual.css.query import NoMatches
from textual.events import Click, DescendantBlur, DescendantFocus, Key
from textual.message import Message
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
    OptionList,
    Select,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
    Tree,
)
from textual.widgets.option_list import Option

from . import catalog, storage
from . import inhabitants as inh
from . import possessions as pos
from .markup import escape, markdown_inline
from .models import (
    ABILITY_CATEGORIES,
    ART_ABBREVIATIONS,
    BOON_HOOK_DESCRIPTION,
    BOON_HOOK_DETAIL,
    COVENANT_BOON_HOOK_CATEGORIES,
    COVENANT_ROLES,
    CRAFT_FIELDS,
    FATIGUE_LEVELS,
    FORMS,
    INHABITANT_KINDS,
    LAB_CHARACTERISTICS,
    LOYALTY_EQUIPMENT,
    LOYALTY_MONEY,
    POSSESSION_KINDS,
    SANCTUM_USAGES,
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
    CovenantBoonHookDef,
    Description,
    DiaryEntry,
    FatigueLevel,
    HermeticBackground,
    Inhabitant,
    LabCharacteristics,
    Laboratory,
    LabVirtueFlawDef,
    Library,
    NamedDescription,
    Possession,
    Saga,
    ScoredTrait,
    Spell,
    VirtueFlawDef,
    VirtueFlawInstance,
    Wounds,
    character_age,
    covenant_boon_points,
    covenant_effective_aura,
    covenant_hook_points,
    lab_aura_total,
    lab_base_safety,
    lab_characteristic_total,
    lab_free_virtues,
    lab_occupied_size,
    next_season,
)

_SAGA_ITEM_ID_PREFIX = "saga-"
_VIRTUE_FLAW_ITEM_ID_PREFIX = "vf-"
_LAB_VIRTUE_FLAW_ITEM_ID_PREFIX = "labvf-"
_ABILITY_ITEM_ID_PREFIX = "ability-"
_REMOVAL_ITEM_ID_PREFIX = "remove-"
_SPELL_ITEM_ID_PREFIX = "spell-"
_COVENANT_BOON_HOOK_ITEM_ID_PREFIX = "covbhpick-"


def _balance_colour(boon_points: float, hook_points: float) -> str:
    """Colour for the Boons/Hooks point totals, shared by both: cyan while
    Boons cost less than Hooks provide, red once they cost more, green when
    they exactly balance."""
    if boon_points < hook_points:
        return "cyan"
    if boon_points > hook_points:
        return "red"
    return "green"


def _boon_hook_params(
    detail: str, description: str, base: dict[str, str] | None = None
) -> dict[str, str]:
    """The `params` of a covenant Boon/Hook: `base` (any keys we don't own)
    plus the detail and description, each stored only when non-empty."""
    params = {
        k: v
        for k, v in (base or {}).items()
        if k not in (BOON_HOOK_DETAIL, BOON_HOOK_DESCRIPTION)
    }
    if detail.strip():
        params[BOON_HOOK_DETAIL] = detail.strip()
    if description.strip():
        params[BOON_HOOK_DESCRIPTION] = description.strip()
    return params


_TIER_ORDER = {"Free": 0, "Minor": 1, "Major": 2}


def _boon_hook_sort_key(entry: CovenantBoonHookDef) -> tuple[int, int, str]:
    """Picker order: by type in the book's order (untyped last), then Free,
    Minor, Major, then name."""
    categories = COVENANT_BOON_HOOK_CATEGORIES
    category = (
        categories.index(entry.category)
        if entry.category in categories
        else len(categories)
    )
    return (category, _TIER_ORDER.get(entry.tier, 9), entry.name.lower())


def _tier_text(entry: CovenantBoonHookDef) -> str:
    """ "Minor Boon (1 pt)", "Major Hook (3 pts)" or "Free Boon"."""
    points = abs(entry.cost)
    if not points:
        return f"{entry.tier} {entry.type}"
    return f"{entry.tier} {entry.type} ({points:g} {'pt' if points == 1 else 'pts'})"


def _year_born_field(value: int | None) -> DialogField:
    """Year Born is never required: blank means Unknown."""
    return DialogField("year_born", "Year Born (blank = Unknown)", "optint", value)


def _inhabitant_fields(
    kind: str,
    entry: inh.InhabitantEntry | None,
    grog: Character | None,
    covenant_year: int,
) -> list[DialogField]:
    """The add/edit form for one kind of inhabitant. For a person listed from a
    character sheet, name/house/year are shown read-only (edit them on the
    sheet) and only the covenant-side fields are editable."""
    auto = entry is not None and entry.auto
    character = entry.character if entry is not None else grog
    houses = [(h.name, h.id) for h in catalog.load_house_catalog()]
    fields: list[DialogField] = []

    if auto and entry is not None:
        fields.append(
            DialogField(
                "_n", "Name", "info", f"{entry.name} (from the character sheet)"
            )
        )
        if kind == "magus":
            fields.append(
                DialogField(
                    "_h", "House", "info", inh.house_name(entry.house_id) or "Unknown"
                )
            )
        year = entry.year_born
        fields.append(
            DialogField("_y", "Year Born", "info", "Unknown" if year is None else year)
        )
    else:
        name = entry.name if entry is not None else (grog.name if grog else "")
        year_born = (
            entry.year_born
            if entry is not None
            else (grog.background.year_born if grog else None)
        )
        fields.append(DialogField("name", "Name", "text", name, required=True))
        if kind == "magus":
            fields.append(
                DialogField(
                    "house",
                    "House",
                    "select",
                    entry.house_id if entry else None,
                    options=houses,
                    allow_blank=True,
                    placeholder="Unknown",
                )
            )
        fields.append(_year_born_field(year_born))

    if kind in ("companion", "specialist", "craftsperson", "turb", "inhabitant"):
        fields.append(
            DialogField(
                "responsibility",
                "Responsibility",
                "text",
                entry.responsibility if entry else "",
            )
        )
    if kind in ("companion", "specialist"):
        fields.append(
            DialogField(
                "role",
                "Covenant Role",
                "select",
                entry.role if entry else "",
                options=[(r, r) for r in COVENANT_ROLES],
                allow_blank=True,
            )
        )
    if kind == "craftsperson":
        from_ability = entry.skill_from_ability if entry is not None else None
        if from_ability is not None and entry is not None:
            # Tied to a sheet's Ability: the score is that Ability's Level.
            fields.append(
                DialogField(
                    "_s",
                    "Value of Crafting Skill",
                    "info",
                    f"{from_ability} (Level of {entry.linked_ability})",
                )
            )
        else:
            fields.append(
                DialogField(
                    "skill_value",
                    "Value of Crafting Skill",
                    "int",
                    entry.record.skill_value if entry and entry.record else 0,
                )
            )
        fields += [
            DialogField(
                "field_of_work",
                "Field of Work",
                "select",
                entry.field_of_work if entry else "None",
                options=[(f, f) for f in CRAFT_FIELDS],
            ),
            DialogField("rare", "Rare", "check", entry.rare if entry else False),
        ]
        abilities = inh.ability_names(character)
        current = entry.linked_ability if entry else ""
        if character is not None:
            options = [(a, a) for a in abilities]
            if current and current not in abilities:
                options.append((current, current))
            fields.append(
                DialogField(
                    "linked_ability",
                    "Linked Ability",
                    "select",
                    current,
                    options=options,
                    allow_blank=True,
                )
            )
        else:
            fields.append(
                DialogField("linked_ability", "Linked Ability", "text", current)
            )
    if kind not in inh.AUTO_KINDS:
        fields.append(
            DialogField("quantity", "Quantity", "int", entry.quantity if entry else 1)
        )
    fields.append(
        DialogField("loyalty", "Loyalty", "int", entry.loyalty if entry else 0)
    )
    fields.append(
        DialogField(
            "description",
            "Description",
            "area",
            entry.description if entry else "",
            hint="Supports **bold** and *italic*.",
        )
    )
    return fields


_ARTS = (*TECHNIQUES, *FORMS)


def _possession_fields(
    kind: str, entry: pos.PossessionEntry | None
) -> list[DialogField]:
    """The add/edit form for one kind of possession. For a laboratory listed as
    a sanctum, name/owner/location/build points are shown read-only (edit them
    on the laboratory) and only the covenant-side fields are editable."""
    fields: list[DialogField] = []
    auto = entry is not None and entry.auto

    def value(attribute: str, default):
        return getattr(entry, attribute) if entry is not None else default

    if auto and entry is not None:
        note = " (from the laboratory)"
        fields.append(DialogField("_n", "Name", "info", entry.name + note))
        fields.append(
            DialogField("_o", "Owner", "info", (entry.owner or "(none)") + note)
        )
        fields.append(
            DialogField("_l", "Location", "info", entry.location or "(not set)")
        )
        fields.append(
            DialogField(
                "_b",
                "Build Points",
                "info",
                "(not set)" if entry.build_points is None else entry.build_points,
            )
        )
    else:
        fields.append(
            DialogField("name", "Name", "text", value("name", ""), required=True)
        )

    if kind == "property":
        fields += [
            DialogField("location", "Location", "text", value("location", "")),
            DialogField("dimensions", "Dimensions", "text", value("dimensions", "")),
            DialogField("inhabitants", "Inhabitants", "text", value("inhabitants", "")),
        ]
    elif kind == "sanctum":
        if not auto:
            fields += [
                # Unowned sanctums are "Free": narratively, visitors can use them.
                DialogField("owner", "Owner", "text", value("owner", "Free")),
                DialogField("location", "Location", "text", value("location", "")),
            ]
        fields += [
            DialogField("quality", "Quality", "optint", value("quality", None)),
            DialogField("upkeep", "Upkeep (Points)", "optint", value("upkeep", None)),
        ]
        if not auto:
            fields.append(
                DialogField(
                    "build_points",
                    "Build Points",
                    "optint",
                    value("build_points", None),
                )
            )
        fields.append(
            DialogField(
                "usage",
                "Usage",
                "select",
                value("usage", SANCTUM_USAGES[1]),
                options=[(u, u) for u in SANCTUM_USAGES],
            )
        )
    elif kind in pos.QUANTITY_KINDS:
        fields.append(DialogField("quantity", "Quantity", "int", value("quantity", 1)))
    elif kind in ("vis_source", "vis_store"):
        fields.append(
            DialogField(
                "art",
                "Art",
                "select",
                value("art", ""),
                options=[(a, a) for a in _ARTS],
                required=True,
                allow_blank=True,
                placeholder="(choose an Art)",
            )
        )
        if kind == "vis_source":
            fields.append(
                DialogField(
                    "season",
                    "Season harvested",
                    "select",
                    value("season", ""),
                    options=[(x, x) for x in SEASONS],
                    required=True,
                    allow_blank=True,
                    placeholder="(choose a Season)",
                )
            )
        fields += [
            DialogField("pawns", "Pawns", "int", value("pawns", 1) or 1),
            DialogField("location", "Location", "text", value("location", "")),
            DialogField(
                "physical_form", "Physical Form", "text", value("physical_form", "")
            ),
        ]

    if kind != "vis_store":
        fields.append(
            DialogField(
                "description",
                "Description",
                "area",
                value("description", ""),
                hint="Supports **bold** and *italic*.",
            )
        )
    return fields


def _possession_problem(values: dict[str, Any]) -> str | None:
    if values.get("quantity", 1) < 1:
        return "Quantity must be at least 1."
    if values.get("pawns", 1) < 1:
        return "Pawns must be at least 1."
    return None


def _inhabitant_problem(values: dict[str, Any]) -> str | None:
    if values.get("quantity", 1) < 1:
        return "Quantity must be at least 1."
    return None


def _boon_hook_names(ids: list[str], by_id: dict[str, CovenantBoonHookDef]) -> str:
    """Names of catalog entries, each listed once (Road/Urban exist at both
    tiers), for prerequisite/exclusion notes."""
    return ", ".join(dict.fromkeys(by_id[i].name for i in ids if i in by_id))


#: Covenant Reputations run from -3 to +3.
_COVENANT_REPUTATION_RANGE = (-3, 3)

#: Which sheet section each covenant Boon/Hook kind lives in.
_BOON_HOOK_SECTION = {"Boon": "section-cov-boons", "Hook": "section-cov-hooks"}


def _sign_colored(value: float, text: str) -> str:
    """Wraps `text` in Textual markup coloured by the sign of `value`:
    zero is cyan, positive green, negative red."""
    colour = "cyan" if value == 0 else "green" if value > 0 else "red"
    return f"[{colour}]{text}[/]"


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


class CovenantBoonHookPickerScreen(SearchablePickerScreen):
    """Pick a covenant Boon or Hook (ArM5 Chapter 6) from the catalog, then
    optionally name what it applies to (which Edifice, which contested
    resource...). Dismisses with the new VirtueFlawInstance, or None if
    cancelled.

    One picker for either kind: `kind` is "Boon" or "Hook". Nothing is
    hidden or blocked: entries already attached are marked "(taken)" but
    can be taken again (a covenant may well have two Edifices), and
    prerequisites and exclusions are shown as notes only.
    """

    LIST_VIEW_ID: ClassVar[str] = "covbh-picker-list"

    def __init__(self, kind: str, attached_ids: list[str] | None = None) -> None:
        super().__init__()
        self.kind = kind
        self._taken = Counter(attached_ids or [])
        self._by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        self.PICKER_TITLE = f"Add a {kind}"
        self.EMPTY_MESSAGE = f"(no more {kind}s available)"
        self.SEARCH_PLACEHOLDER = f"Search {kind}s..."

    def _load_entries(self) -> list[CovenantBoonHookDef]:
        return sorted(
            (entry for entry in self._by_id.values() if entry.type == self.kind),
            key=_boon_hook_sort_key,
        )

    def _search_text(self, entry: CovenantBoonHookDef) -> str:
        return f"{entry.name} {entry.category} {entry.tier} {entry.description}"

    def _names(self, ids: list[str]) -> str:
        return _boon_hook_names(ids, self._by_id)

    def _label_for(self, entry: CovenantBoonHookDef) -> str:
        facts = [entry.category] if entry.category else []
        facts.append(entry.tier)
        if entry.cost:
            facts.append(f"{abs(entry.cost):g} pt")
        label = f"{entry.name}  [{', '.join(facts)}]"
        if entry.requires:
            label += f"  (requires: {self._names(entry.requires)})"
        if entry.excludes:
            label += f"  (not with: {self._names(entry.excludes)})"
        if self._taken[entry.id]:
            label += f"  (taken x{self._taken[entry.id]})"
        return label

    def _item_id(self, entry: CovenantBoonHookDef) -> str:
        return f"{_COVENANT_BOON_HOOK_ITEM_ID_PREFIX}{entry.id}"

    def _on_entry_selected(self, entry: CovenantBoonHookDef) -> None:
        def handle_detail(result: tuple[str, str] | None) -> None:
            if result is None:
                return  # cancelled: back to the picker
            detail, description = result
            self.dismiss(
                VirtueFlawInstance(
                    vf_id=entry.id, params=_boon_hook_params(detail, description)
                )
            )

        self.app.push_screen(BoonHookDetailScreen(self.kind, entry.name), handle_detail)


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

    def __init__(self, saga: Saga, covenant: Covenant | None = None) -> None:
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
            yield Label("Covenant (optional)")
            yield Select(
                [(c.name, c.id) for c in self.saga.covenants],
                value=self.covenant.id if self.covenant else Select.NULL,
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
            error.update("Laboratory name is required.")
            return

        try:
            size = int(self.query_one("#input-size", Input).value.strip())
        except ValueError:
            error.update("Size must be a whole number.")
            return

        covenant_value = self.query_one("#select-covenant", Select).value
        covenant_id = covenant_value if isinstance(covenant_value, str) else None

        laboratory = Laboratory(
            id=storage.generate_unique_id(
                name, [lab.id for lab in self.saga.laboratories]
            ),
            covenant_id=covenant_id,
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

    def __init__(self, title: str = "Add an Item", existing: str | None = None) -> None:
        super().__init__()
        self.title_text = title
        self.existing = existing

    def compose(self) -> ComposeResult:
        with Vertical(id="create-dialog"):
            yield Label(self.title_text, id="create-title")
            yield Input(
                value=self.existing or "",
                placeholder="e.g. Fine wool cloak",
                id="input-item",
            )
            yield Static("", id="create-error")
            with Horizontal():
                yield Button(
                    "Add" if self.existing is None else "Save",
                    id="btn-create",
                    variant="success",
                )
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
        self,
        title: str,
        name_placeholder: str,
        existing: ScoredTrait | None = None,
        *,
        min_score: int | None = None,
        max_score: int | None = None,
    ) -> None:
        super().__init__()
        self.title_text = title
        self.name_placeholder = name_placeholder
        self.existing = existing
        #: Optional inclusive bounds (covenant Reputations are -3..+3).
        self.min_score = min_score
        self.max_score = max_score

    def _score_label(self) -> str:
        if self.min_score is None or self.max_score is None:
            return "Score"
        return f"Score ({self.min_score:+d} to {self.max_score:+d})"

    def compose(self) -> ComposeResult:
        with Vertical(id="trait-dialog"):
            yield Label(self.title_text, id="trait-title")
            yield Label("Name")
            yield Input(
                value=self.existing.name if self.existing else "",
                placeholder=self.name_placeholder,
                id="input-trait-name",
            )
            yield Label(self._score_label())
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
        if (self.min_score is not None and score < self.min_score) or (
            self.max_score is not None and score > self.max_score
        ):
            error.update(f"Score must be between {self._score_label()[6:-1]}.")
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

    def __init__(self, existing: tuple[str, int] | None = None) -> None:
        super().__init__()
        self.existing = existing

    def compose(self) -> ComposeResult:
        existing = self.existing
        with Vertical(id="vis-dialog"):
            yield Label(
                "Add Raw Vis" if existing is None else "Edit Raw Vis", id="vis-title"
            )
            yield Label("Art")
            yield Select(
                [(art, art.lower()) for art in (*TECHNIQUES, *FORMS)],
                value=existing[0] if existing else Select.NULL,
                id="select-vis-art",
            )
            yield Label("Pawns")
            yield Input(
                value="1" if existing is None else str(existing[1]),
                type="integer",
                id="input-vis-pawns",
            )
            yield Static("", id="vis-error")
            with Horizontal():
                yield Button(
                    "Add" if existing is None else "Save",
                    id="btn-create",
                    variant="success",
                )
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
    """Edits a Laboratory's Name/Location/Build Points/Aura modifier, and (unlike
    character Identity editing) lets you reassign its Owner from the
    lab's own side -- WorkspaceScreen._assign_laboratory() already
    handles the bidirectional sync, this just calls it from here too.
    Dismisses with {"name", "location", "build_points", "aura_modifier",
    "covenant_id", "owner_id"}, or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditLabIdentityScreen {
        align: center middle;
    }

    #lab-identity-dialog {
        width: 64;
        height: auto;
        max-height: 100%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    .labid-row {
        width: 100%;
        height: 1;
    }

    .labid-row Label {
        width: 22;
    }

    .labid-row Input, .labid-row Select {
        width: 1fr;
    }

    #lab-identity-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #lab-identity-buttons {
        width: 100%;
        height: auto;
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
            with Horizontal(classes="labid-row"):
                yield Label("Name")
                yield Input(value=lab.name, id="input-lab-name", compact=True)
            with Horizontal(classes="labid-row"):
                yield Label("Location")
                yield Input(value=lab.location, id="input-lab-location", compact=True)
            with Horizontal(classes="labid-row"):
                yield Label("Points (Build Points)")
                yield Input(
                    value=str(lab.build_points),
                    type="integer",
                    id="input-lab-points",
                    compact=True,
                )
            with Horizontal(classes="labid-row"):
                yield Label("Aura modifier")
                yield Input(
                    value=str(lab.aura_modifier),
                    type="integer",
                    id="input-lab-aura-modifier",
                    compact=True,
                )
            with Horizontal(classes="labid-row"):
                yield Label("Covenant")
                yield Select(
                    [(c.name, c.id) for c in self.saga.covenants],
                    value=lab.covenant_id or Select.NULL,
                    allow_blank=True,
                    prompt="(unassigned)",
                    id="select-lab-covenant",
                    compact=True,
                )
            with Horizontal(classes="labid-row"):
                yield Label("Owner")
                yield Select(
                    [(c.name, c.id) for c in self.saga.characters if c.type == "magus"],
                    value=lab.owner_id or Select.NULL,
                    allow_blank=True,
                    prompt="(unassigned)",
                    id="select-lab-owner",
                    compact=True,
                )
            yield Static("", id="lab-identity-error")
            with Horizontal(id="lab-identity-buttons"):
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

        raw_aura = self.query_one("#input-lab-aura-modifier", Input).value.strip()
        try:
            aura_modifier = int(raw_aura)
        except ValueError:
            error.update("Aura modifier must be a whole number.")
            return

        owner_value = self.query_one("#select-lab-owner", Select).value
        owner_id = owner_value if isinstance(owner_value, str) else None

        covenant_value = self.query_one("#select-lab-covenant", Select).value
        covenant_id = covenant_value if isinstance(covenant_value, str) else None

        self.dismiss(
            {
                "name": name,
                "location": self.query_one("#input-lab-location", Input).value.strip(),
                "build_points": build_points,
                "aura_modifier": aura_modifier,
                "covenant_id": covenant_id,
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
        max-height: 100%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #lab-char-fields {
        height: auto;
        max-height: 14;
    }

    .labchar-row {
        width: 100%;
        height: 1;
    }

    .labchar-row Label {
        width: 18;
    }

    .labchar-row Input {
        width: 1fr;
    }

    #lab-char-buttons {
        width: 100%;
        height: auto;
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
        # Fields scroll (if the terminal is very short); the buttons sit
        # outside the scroll region so Save/Cancel are always visible.
        with Vertical(id="lab-char-dialog"):
            yield Label("Edit Laboratory Characteristics (manual value)")
            with VerticalScroll(id="lab-char-fields"):
                for characteristic in LAB_CHARACTERISTICS:
                    with Horizontal(classes="labchar-row"):
                        yield Label(characteristic.replace("_", " ").title())
                        yield Input(
                            value=str(getattr(self.characteristics, characteristic)),
                            type="integer",
                            id=f"input-labchar-{characteristic}",
                            compact=True,
                        )
            yield Static("", id="lab-char-error")
            with Horizontal(id="lab-char-buttons"):
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

    def __init__(
        self,
        title: str,
        name_placeholder: str,
        existing: NamedDescription | None = None,
    ) -> None:
        super().__init__()
        self.title_text = title
        self.name_placeholder = name_placeholder
        self.existing = existing

    def compose(self) -> ComposeResult:
        existing = self.existing
        with Vertical(id="named-desc-dialog"):
            yield Label(self.title_text, id="named-desc-title")
            yield Label("Name")
            yield Input(
                value=existing.name if existing else "",
                placeholder=self.name_placeholder,
                id="input-named-desc-name",
            )
            yield Label("Description")
            yield Input(
                value=existing.description if existing else "",
                id="input-named-desc-description",
            )
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

    def __init__(
        self,
        default_year: int,
        existing: DiaryEntry | None = None,
        default_season: str = SEASONS[0],
    ) -> None:
        super().__init__()
        self.default_year = default_year
        self.default_season = default_season
        self.existing = existing

    def compose(self) -> ComposeResult:
        existing = self.existing
        with Vertical(id="diary-dialog"):
            yield Label(
                "Add a Diary Entry" if existing is None else "Edit a Diary Entry",
                id="diary-title",
            )
            yield Label("Year")
            yield Input(
                value=str(existing.year if existing else self.default_year),
                type="integer",
                id="input-diary-year",
            )
            yield Label("Season")
            yield Select(
                [(season, season) for season in SEASONS],
                value=existing.season if existing else self.default_season,
                allow_blank=False,
                id="select-diary-season",
            )
            yield Label("Name")
            yield Input(
                value=existing.name if existing else "",
                placeholder="e.g. Invented a spell",
                id="input-diary-name",
            )
            yield Label("Details")
            yield Input(
                value=existing.details if existing else "", id="input-diary-details"
            )
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


class EditCovenantScreen(ModalScreen[dict[str, object] | None]):
    """Edits the covenant-owned fields of the covenant sheet's top panel.

    The saga's name, Storyguide, current season and current year are
    inherited from the Saga and aren't editable here. Dismisses with a
    dict of field values (see _INT_FIELDS plus "name", "tribunal",
    "year_founded", "covenant_season"), or None if cancelled.
    """

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    #: (Covenant attribute, label) for the plain whole-number fields.
    _INT_FIELDS: ClassVar[tuple[tuple[str, str], ...]] = (
        ("aegis_of_the_hearth", "Aegis of the Hearth"),
        ("aegis_penetration", "Aegis' Penetration"),
        ("living_conditions_magi", "Living Conditions (Magi)"),
        ("living_conditions_mundane", "Living Conditions (Mundane)"),
        ("aura", "Aura"),
    )

    DEFAULT_CSS = """
    EditCovenantScreen {
        align: center middle;
    }

    #cov-edit-dialog {
        width: 64;
        height: auto;
        max-height: 100%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    .covedit-row {
        width: 100%;
        height: 1;
    }

    .covedit-row Label {
        width: 30;
    }

    .covedit-row Input, .covedit-row Select {
        width: 1fr;
    }

    #cov-edit-hint {
        color: $text-muted;
        height: auto;
        margin-top: 1;
    }

    #cov-edit-error {
        color: $error;
        height: auto;
    }

    #cov-edit-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, covenant: Covenant) -> None:
        super().__init__()
        self.covenant = covenant

    @staticmethod
    def _input_id(field: str) -> str:
        return f"input-cov-{field.replace('_', '-')}"

    def compose(self) -> ComposeResult:
        cov = self.covenant
        with Vertical(id="cov-edit-dialog"):
            yield Label("Edit Covenant")
            with Horizontal(classes="covedit-row"):
                yield Label("Name")
                yield Input(value=cov.name, id=self._input_id("name"), compact=True)
            with Horizontal(classes="covedit-row"):
                yield Label("Tribunal")
                yield Input(
                    value=cov.tribunal, id=self._input_id("tribunal"), compact=True
                )
            with Horizontal(classes="covedit-row"):
                yield Label("Year Founded")
                yield Input(
                    value="" if cov.year_founded is None else str(cov.year_founded),
                    type="integer",
                    id=self._input_id("year_founded"),
                    compact=True,
                )
            for field, label in self._INT_FIELDS:
                with Horizontal(classes="covedit-row"):
                    yield Label(label)
                    yield Input(
                        value=str(getattr(cov, field)),
                        type="integer",
                        id=self._input_id(field),
                        compact=True,
                    )
            with Horizontal(classes="covedit-row"):
                yield Label("Covenant Season")
                yield Select(
                    [(season, season) for season in SEASONS],
                    value=cov.covenant_season,
                    allow_blank=False,
                    id="select-cov-season",
                    compact=True,
                )
            yield Static(
                "Aura is the base aura of every laboratory in this covenant.",
                id="cov-edit-hint",
            )
            yield Static("", id="cov-edit-error")
            with Horizontal(id="cov-edit-buttons"):
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
        error = self.query_one("#cov-edit-error", Static)

        name = self.query_one(f"#{self._input_id('name')}", Input).value.strip()
        if not name:
            error.update("Name is required.")
            return

        result: dict[str, object] = {
            "name": name,
            "tribunal": self.query_one(
                f"#{self._input_id('tribunal')}", Input
            ).value.strip(),
        }

        raw_year = self.query_one(
            f"#{self._input_id('year_founded')}", Input
        ).value.strip()
        try:
            result["year_founded"] = int(raw_year) if raw_year else None
        except ValueError:
            error.update("Year Founded must be a whole number.")
            return

        for field, label in self._INT_FIELDS:
            raw = self.query_one(f"#{self._input_id(field)}", Input).value.strip()
            try:
                result[field] = int(raw)
            except ValueError:
                error.update(f"{label} must be a whole number.")
                return

        result["covenant_season"] = self.query_one("#select-cov-season", Select).value
        self.dismiss(result)


class AdvanceSeasonScreen(ModalScreen[bool]):
    """Confirms advancing the saga's calendar by one season. Dismisses with
    True to advance, False (or via Escape) to leave the date alone."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    AdvanceSeasonScreen {
        align: center middle;
    }

    #advance-dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #advance-note {
        color: $text-muted;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, season: str, year: int) -> None:
        super().__init__()
        self.season = season
        self.year = year

    def compose(self) -> ComposeResult:
        new_season, new_year = next_season(self.season, self.year)
        with Vertical(id="advance-dialog"):
            yield Label("Advance Time", id="advance-title")
            yield Static(
                f"Advance the saga from {self.season} {self.year} "
                f"to {new_season} {new_year}?",
                id="advance-message",
            )
            yield Static(
                "Advanced by mistake? Use Set Date (T) to put it back.",
                id="advance-note",
            )
            with Horizontal():
                yield Button("Advance", id="btn-advance", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "btn-advance")


class SetDateScreen(ModalScreen[tuple[str, int] | None]):
    """Sets the saga's calendar date directly -- for the initial date, or to
    roll back an accidental Advance. Dismisses with (season, year), or None
    if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    SetDateScreen {
        align: center middle;
    }

    #set-date-dialog {
        width: 50;
        height: auto;
        max-height: 100%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    .setdate-row {
        width: 100%;
        height: 1;
    }

    .setdate-row Label {
        width: 10;
    }

    .setdate-row Input, .setdate-row Select {
        width: 1fr;
    }

    #set-date-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #set-date-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, season: str, year: int) -> None:
        super().__init__()
        self.season = season
        self.year = year

    def compose(self) -> ComposeResult:
        with Vertical(id="set-date-dialog"):
            yield Label("Set the Saga's Date", id="set-date-title")
            with Horizontal(classes="setdate-row"):
                yield Label("Season")
                yield Select(
                    [(season, season) for season in SEASONS],
                    value=self.season,
                    allow_blank=False,
                    id="select-date-season",
                    compact=True,
                )
            with Horizontal(classes="setdate-row"):
                yield Label("Year")
                yield Input(
                    value=str(self.year),
                    type="integer",
                    id="input-date-year",
                    compact=True,
                )
            yield Static("", id="set-date-error")
            with Horizontal(id="set-date-buttons"):
                yield Button("Set", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._try_save()

    def _try_save(self) -> None:
        error = self.query_one("#set-date-error", Static)
        raw_year = self.query_one("#input-date-year", Input).value.strip()
        try:
            year = int(raw_year)
        except ValueError:
            error.update("Year must be a whole number.")
            return
        season = self.query_one("#select-date-season", Select).value
        self.dismiss((str(season), year))


class BoonHookDetailScreen(ModalScreen[tuple[str, str] | None]):
    """Asks for the two optional, user-written fields of a covenant
    Boon/Hook: a one-line Detail (which Edifice, which contested resource --
    shown in the list) and a multi-line Description (what the Hidden
    Resources actually contain -- shown in the details panel ahead of the
    official rules text). Both blank by default. Used when adding one and
    when editing it later. Dismisses with (detail, description), each
    stripped and possibly empty, or None if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    BoonHookDetailScreen {
        align: center middle;
    }

    #bh-detail-dialog {
        width: 72;
        height: auto;
        max-height: 100%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #bh-description-text {
        height: 8;
    }

    #bh-detail-hint {
        color: $text-muted;
        height: auto;
        margin: 1 0;
    }

    #bh-detail-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(
        self, kind: str, name: str, detail: str = "", description: str = ""
    ) -> None:
        super().__init__()
        self.kind = kind
        self.entry_name = name
        self.detail = detail
        self.description = description

    def compose(self) -> ComposeResult:
        with Vertical(id="bh-detail-dialog"):
            yield Label(f"{self.kind}: {self.entry_name}", id="bh-detail-title")
            yield Label("Detail (optional)")
            yield Input(
                value=self.detail,
                placeholder="e.g. the specific building or resource",
                id="input-bh-detail",
                compact=True,
            )
            yield Label("Description (optional)")
            yield TextArea(self.description, id="bh-description-text")
            yield Static(
                "Description supports **bold** and *italic*.",
                id="bh-detail-hint",
            )
            with Horizontal(id="bh-detail-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._save()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._save()

    def _save(self) -> None:
        self.dismiss(
            (
                self.query_one("#input-bh-detail", Input).value.strip(),
                self.query_one("#bh-description-text", TextArea).text.strip(),
            )
        )


class ConfirmScreen(ModalScreen[bool]):
    """A Yes/No confirmation, e.g. before deleting something. Dismisses with
    True for Yes, False for No / Escape. No is focused by default so a stray
    Enter can't delete; `y` and `n` answer directly. `message` is shown as
    markup, so escape any user text in it."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("escape", "no", "No"),
        ("n", "no", "No"),
        ("y", "yes", "Yes"),
    ]

    DEFAULT_CSS = """
    ConfirmScreen {
        align: center middle;
    }

    #confirm-dialog {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #confirm-message {
        height: auto;
        margin-bottom: 1;
    }

    #confirm-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, message: str, *, yes_label: str = "Yes") -> None:
        super().__init__()
        self.message = message
        self.yes_label = yes_label

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-dialog"):
            yield Static(self.message, id="confirm-message")
            with Horizontal(id="confirm-buttons"):
                yield Button(self.yes_label, id="btn-yes", variant="error")
                yield Button("No", id="btn-no")

    def on_mount(self) -> None:
        self.query_one("#btn-no", Button).focus()

    def action_yes(self) -> None:
        self.dismiss(True)

    def action_no(self) -> None:
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "btn-yes")


class EditCovenantDescriptionScreen(ModalScreen[str | None]):
    """A multi-line text editor for the covenant's description. Dismisses
    with the new text, or None if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    EditCovenantDescriptionScreen {
        align: center middle;
    }

    #cov-desc-dialog {
        width: 76;
        height: auto;
        max-height: 100%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #cov-desc-text {
        height: 12;
    }

    #cov-desc-hint {
        color: $text-muted;
        height: auto;
        margin-bottom: 1;
    }
    """

    def __init__(self, text: str) -> None:
        super().__init__()
        self.text = text

    def compose(self) -> ComposeResult:
        with Vertical(id="cov-desc-dialog"):
            yield Label("Edit Covenant Description")
            yield TextArea(self.text, id="cov-desc-text")
            yield Static("Supports **bold** and *italic*.", id="cov-desc-hint")
            with Horizontal():
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self.dismiss(self.query_one("#cov-desc-text", TextArea).text.rstrip())


class SelectableList(OptionList):
    """The standard "selectable list" (see DESIGN.md, UI Conventions): rows
    that each carry a selector -- a dim `○`, or a blue bold `●` on the chosen
    row -- with at most one row chosen at a time.

    Rows are `(data index, label)` pairs: the data index is the entry's
    position in whatever list the sheet keeps its data in (it becomes the
    Option id, so a filtered list still maps back to the true entry), and
    the label is markup -- escape user text with `escape()` first. An empty
    list shows one disabled "(none recorded)" row.

    Choosing a row (arrow keys or click) moves the marker and posts
    `SelectableList.Chosen(data_index)`; the owning view reacts (fills a
    details panel, clears a sibling list...). Nothing is chosen until the
    user picks a row, and `set_rows()` clears the choice.
    """

    DEFAULT_CSS = """
    SelectableList,
    SelectableList:focus {
        height: auto;
        max-height: 14;
        border: none;
        padding: 0;
        background: transparent;
    }

    /* The marker is the selection indicator: a solid highlight bar would
       swallow it, so the bar is neutralised (normal and focused) and the
       chosen row is just bold. */
    SelectableList > .option-list--option-highlighted,
    SelectableList:focus > .option-list--option-highlighted {
        background: transparent;
        color: $foreground;
        text-style: bold;
    }
    """

    class Chosen(Message):
        """A row was chosen; `data_index` is its entry's data index."""

        def __init__(self, selectable_list: SelectableList, data_index: int) -> None:
            super().__init__()
            self.selectable_list = selectable_list
            self.data_index = data_index

        @property
        def control(self) -> SelectableList:
            return self.selectable_list

    def __init__(
        self, rows: list[tuple[int, str]] | None = None, *, id: str | None = None
    ) -> None:
        super().__init__(id=id, compact=True)
        self._rows: list[tuple[int, str]] = []
        self._marked: int | None = None
        self._add_rows(rows or [])

    @staticmethod
    def _prompt(label: str, *, selected: bool) -> str:
        marker = "[dodgerblue]●[/]" if selected else "[dim]○[/]"
        return f"{marker} {label}"

    def _add_rows(self, rows: list[tuple[int, str]]) -> None:
        # Added after construction on purpose: OptionList(*options)
        # highlights its first row, and nothing should be chosen until the
        # user picks one.
        self._rows = list(rows)
        if not self._rows:
            self.add_option(Option("[dim](none recorded)[/]", disabled=True))
            return
        self.add_options(
            Option(self._prompt(label, selected=False), id=str(index))
            for index, label in self._rows
        )

    def set_rows(self, rows: list[tuple[int, str]]) -> None:
        """Replace all rows (synchronous; nothing is chosen afterwards)."""
        self.clear_options()
        self._marked = None
        self._add_rows(rows)

    @property
    def selected_data_index(self) -> int | None:
        """Data index of the chosen row, or None if none is chosen."""
        option = self.highlighted_option
        return int(option.id) if option is not None and option.id else None

    def clear_selection(self) -> None:
        """Unchoose everything. Posts no message."""
        self._mark(None)
        self.highlighted = None

    def _mark(self, row: int | None) -> None:
        """Move the selector marker to list position `row` (None: no marker)."""
        previous = self._marked
        if previous == row:
            return
        if previous is not None and previous < len(self._rows):
            self.replace_option_prompt_at_index(
                previous, self._prompt(self._rows[previous][1], selected=False)
            )
        if row is not None and row < len(self._rows):
            self.replace_option_prompt_at_index(
                row, self._prompt(self._rows[row][1], selected=True)
            )
        self._marked = row

    def on_option_list_option_highlighted(
        self, event: OptionList.OptionHighlighted
    ) -> None:
        event.stop()
        if event.option.id is None:  # the disabled "(none recorded)" row
            return
        self._mark(event.option_index)
        self.post_message(self.Chosen(self, int(event.option.id)))


@dataclass
class DialogField:
    """One row of a FieldsDialog.

    `kind`: "text" (a stripped string), "int" (a whole number), "optint" (a
    whole number or blank -> None), "select" (one of `options` as (label,
    value) pairs; blank -> None when `allow_blank`), "check" (a boolean),
    "area" (multi-line text) or "info" (read-only text, not returned).
    """

    key: str
    label: str
    kind: str
    value: object = None
    options: list[tuple[str, str]] = dataclass_field(default_factory=list)
    required: bool = False
    allow_blank: bool = False
    placeholder: str = ""
    hint: str = ""


class FieldsDialog(ModalScreen[dict[str, Any] | None]):
    """A config-driven form: one compact row per DialogField, scrolling if the
    terminal is short (Save/Cancel stay put). Dismisses with {key: value} for
    every non-info field, or None if cancelled. `validate` gets the finished
    dict and returns an error message, or None if it's fine."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    FieldsDialog {
        align: center middle;
    }

    #fields-dialog {
        width: 84;
        max-width: 100%;
        height: auto;
        max-height: 100%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #fields-scroll {
        height: auto;
    }

    .fd-row {
        width: 100%;
        height: 1;
    }

    .fd-label {
        width: 30;
    }

    .fd-row Input, .fd-row Select {
        width: 1fr;
    }

    .fd-value {
        width: 1fr;
        color: $text-muted;
    }

    .fd-area-label {
        margin-top: 1;
    }

    .fd-area {
        height: 6;
    }

    .fd-hint {
        color: $text-muted;
        height: auto;
    }

    #fields-error {
        color: $error;
        height: auto;
    }

    #fields-buttons {
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(
        self,
        title: str,
        fields: list[DialogField],
        *,
        validate: Callable[[dict[str, Any]], str | None] | None = None,
    ) -> None:
        super().__init__()
        self.title_text = title
        self.fields = fields
        self.validate = validate

    def compose(self) -> ComposeResult:
        with Vertical(id="fields-dialog"):
            yield Label(self.title_text, id="fields-title")
            with VerticalScroll(id="fields-scroll"):
                for spec in self.fields:
                    yield from self._widgets(spec)
            yield Static("", id="fields-error")
            with Horizontal(id="fields-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def _widgets(self, spec: DialogField) -> ComposeResult:
        widget_id = f"fld-{spec.key}"
        if spec.kind == "area":
            yield Label(spec.label, classes="fd-area-label")
            yield TextArea(str(spec.value or ""), id=widget_id, classes="fd-area")
            if spec.hint:
                yield Static(spec.hint, classes="fd-hint")
            return
        with Horizontal(classes="fd-row"):
            yield Label(spec.label, classes="fd-label")
            if spec.kind == "text":
                yield Input(
                    value=str(spec.value or ""),
                    placeholder=spec.placeholder,
                    id=widget_id,
                    compact=True,
                )
            elif spec.kind in ("int", "optint"):
                yield Input(
                    value="" if spec.value is None else str(spec.value),
                    type="integer",
                    id=widget_id,
                    compact=True,
                )
            elif spec.kind == "select":
                values = [value for _, value in spec.options]
                if spec.value in values:
                    current = spec.value
                elif spec.allow_blank or not values:
                    current = Select.NULL
                else:
                    current = values[0]
                yield Select(
                    spec.options,
                    value=current,
                    allow_blank=spec.allow_blank,
                    prompt=spec.placeholder or "(none)",
                    id=widget_id,
                    compact=True,
                )
            elif spec.kind == "check":
                yield Checkbox("", value=bool(spec.value), id=widget_id, compact=True)
            else:  # info
                yield Static(str(spec.value), classes="fd-value")

    def on_mount(self) -> None:
        self._fit()

    def on_resize(self) -> None:
        self._fit()

    def _fit(self) -> None:
        """Cap the scrolling region so the title, error line and buttons always
        stay on screen, however short the terminal is."""
        self.query_one("#fields-scroll").styles.max_height = max(
            4, self.size.height - 11
        )

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._save()

    def _save(self) -> None:
        error = self.query_one("#fields-error", Static)
        result: dict[str, Any] = {}
        for spec in self.fields:
            if spec.kind == "info":
                continue
            widget = self.query_one(f"#fld-{spec.key}")
            if spec.kind == "text":
                value: Any = widget.value.strip()
                if spec.required and not value:
                    error.update(f"{spec.label} is required.")
                    return
            elif spec.kind in ("int", "optint"):
                raw = widget.value.strip()
                if not raw and spec.kind == "optint":
                    value = None
                    if spec.required:
                        error.update(f"{spec.label} is required.")
                        return
                else:
                    try:
                        value = int(raw)
                    except ValueError:
                        error.update(f"{spec.label} must be a whole number.")
                        return
            elif spec.kind == "select":
                value = widget.value if isinstance(widget.value, str) else None
                if spec.required and value is None:
                    error.update(f"{spec.label} is required.")
                    return
            elif spec.kind == "check":
                value = bool(widget.value)
            else:  # area
                value = widget.text.strip()
            result[spec.key] = value
        problem = self.validate(result) if self.validate else None
        if problem:
            error.update(problem)
            return
        self.dismiss(result)


class SheetSection(Collapsible):
    """A character/laboratory sheet section: a Collapsible that starts
    expanded. Textual's own default is collapsed, so every sheet section
    goes through this (project convention: sections are open by default,
    the user can still collapse them)."""

    def __init__(self, *children: Widget, title: str, **kwargs: Any) -> None:
        kwargs.setdefault("collapsed", False)
        super().__init__(*children, title=title, **kwargs)


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
                with SheetSection(title="Identity", id="section-identity"):
                    yield Static(self._identity_text(), id="identity-content")
                with SheetSection(title="Background", id="section-background"):
                    yield Static(self._background_text(), id="background-content")
                with SheetSection(title="Description", id="section-description"):
                    yield Static(self._description_text(), id="description-content")
                with SheetSection(
                    title="Characteristics", id="section-characteristics"
                ):
                    yield Static(
                        self._characteristics_text(), id="characteristics-content"
                    )
                with SheetSection(title="Abilities", id="section-abilities"):
                    yield Static(self._abilities_text(), id="abilities-content")
                with SheetSection(title="Virtues & Flaws", id="section-vf"):
                    yield Static(self._vf_text(), id="vf-content")
                with SheetSection(title="Aging & Warping", id="section-aging"):
                    yield Static(self._aging_text(), id="aging-content")
            with (
                TabPane("Personality & Health", id="tab-personality"),
                VerticalScroll(),
            ):
                with SheetSection(
                    title="Personality Traits", id="section-personality-traits"
                ):
                    yield Static(
                        self._personality_traits_text(),
                        id="personality-traits-content",
                    )
                with SheetSection(title="Reputations", id="section-reputations"):
                    yield Static(self._reputations_text(), id="reputations-content")
                with SheetSection(title="Wounds", id="section-wounds"):
                    yield Static(self._wounds_text(), id="wounds-content")
                with SheetSection(title="Fatigue", id="section-fatigue"):
                    yield Static(self._fatigue_text(), id="fatigue-content")
                with SheetSection(title="Inventory", id="section-inventory"):
                    yield Static(self._inventory_text(), id="inventory-content")
            if character.type == "magus":
                with TabPane("Hermetic", id="tab-hermetic"), VerticalScroll():
                    with SheetSection(title="Magical Arts", id="section-arts"):
                        yield Static(self._arts_text(), id="arts-content")
                    with SheetSection(title="Raw Vis", id="section-raw-vis"):
                        yield Static(self._raw_vis_text(), id="raw-vis-content")
                    with SheetSection(
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


class PinnedCollapsible(Collapsible):
    """A Collapsible that is permanently expanded and ignores toggling.

    Used for the laboratory sheet's always-visible top panel. It stays a
    real Collapsible (with a focusable CollapsibleTitle) so the focus-
    ancestry dispatch in WorkspaceScreen treats it like every other
    section, but it can never be collapsed.
    """

    def __init__(self, *children: Widget, title: str, id: str | None = None) -> None:
        super().__init__(
            *children, title=title, collapsed=False, expanded_symbol="", id=id
        )

    def _on_collapsible_title_toggle(self, event: Message) -> None:
        # Textual dispatches a message to every class in the MRO's handler
        # of the same name, so stop() alone isn't enough -- prevent_default()
        # is what keeps Collapsible's own handler from flipping `collapsed`.
        event.stop()
        event.prevent_default()

    def on_click(self, event: Click) -> None:
        # Clicking anywhere in the section (not just its title) makes it the
        # active section, so 'e' and the Footer hint work after a click.
        self.query_one("CollapsibleTitle").focus()


class LaboratorySheetView(Vertical):
    """The laboratory sheet mounted into WorkspaceScreen's detail pane.

    A fixed top panel (Identity above Characteristics -- not inside any
    tab, permanently expanded) above a 5-tab body mirroring the
    sheet's own pages: Planning (placeholder), Virtues & Flaws, Attributes
    (Specialties/Features/Rooms), Inventory (Raw Vis/Items), Diary. Same
    Collapsible-section + read-then-refresh Static pattern as
    CharacterSheetView.
    """

    DEFAULT_CSS = """
    LaboratorySheetView {
        height: 1fr;
    }

    LaboratorySheetView #lab-top-panel {
        width: 1fr;
        height: auto;
    }

    LaboratorySheetView #lab-characteristics-body {
        width: 1fr;
        height: auto;
    }

    LaboratorySheetView #lab-characteristics-derived {
        width: auto;
        height: auto;
        margin-right: 6;
    }

    LaboratorySheetView #lab-characteristics-content {
        width: auto;
        height: auto;
    }

    LaboratorySheetView TabbedContent {
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
        #: Set once TabbedContent's initial TabActivated has been seen -- see
        #: WorkspaceScreen.on_tabbed_content_tab_activated().
        self.initial_tab_seen = False

    def compose(self) -> ComposeResult:
        with Vertical(id="lab-top-panel"):
            with PinnedCollapsible(title="Identity", id="section-lab-identity"):
                yield Static(self._identity_text(), id="lab-identity-content")
                yield Button("Edit (e)", id="btn-lab-identity-edit", compact=True)
            with PinnedCollapsible(
                title="Characteristics", id="section-lab-characteristics"
            ):
                with Horizontal(id="lab-characteristics-body"):
                    yield Static(
                        self._characteristics_derived_text(),
                        id="lab-characteristics-derived",
                    )
                    yield Static(
                        self._characteristics_table_text(),
                        id="lab-characteristics-content",
                    )
                yield Button(
                    "Edit (e)", id="btn-lab-characteristics-edit", compact=True
                )
        with TabbedContent(initial="tab-lab-planning"):
            with TabPane("Planning", id="tab-lab-planning"):
                yield Static(self._planning_text(), id="lab-planning-content")
            with TabPane("Virtues & Flaws", id="tab-lab-vf"):
                yield Static(self._vf_text(), id="lab-vf-content")
            with TabPane("Attributes", id="tab-lab-attributes"), VerticalScroll():
                with SheetSection(title="Specialties", id="section-lab-specialties"):
                    yield Static(self._specialties_text(), id="lab-specialties-content")
                with SheetSection(title="Features", id="section-lab-features"):
                    yield Static(self._features_text(), id="lab-features-content")
                with SheetSection(title="Rooms", id="section-lab-rooms"):
                    yield Static(self._rooms_text(), id="lab-rooms-content")
            with TabPane("Inventory", id="tab-lab-inventory"), VerticalScroll():
                with SheetSection(title="Raw Vis", id="section-lab-raw-vis"):
                    yield Static(self._raw_vis_text(), id="lab-raw-vis-content")
                with SheetSection(title="Items", id="section-lab-items"):
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
        "section-lab-characteristics": "_characteristics_table_text",
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
        if section_id == "section-lab-characteristics":
            # Two-column section: the derived stats sit in a sibling Static.
            self.query_one("#lab-characteristics-derived", Static).update(
                self._characteristics_derived_text()
            )

    def _identity_text(self) -> str:
        saga, lab = self.saga, self.laboratory
        covenant = next((c for c in saga.covenants if c.id == lab.covenant_id), None)
        owner = next((c for c in saga.characters if c.id == lab.owner_id), None)
        # Inherited from the covenant, including any Boons that raise it.
        covenant_aura = (
            covenant_effective_aura(
                covenant, catalog.load_covenant_boon_hook_catalog_by_id()
            )
            if covenant
            else 0
        )
        return "\n".join(
            [
                f"Name: {lab.name}",
                f"Location: {lab.location or '(not set)'}",
                f"Points: {lab.build_points}",
                f"Owner: {owner.name if owner else '(unassigned)'}",
                f"Covenant: {covenant.name if covenant else '(none)'}",
                f"Aura: {covenant_aura} (covenant) {lab.aura_modifier:+d} (modifier) "
                f"= {lab_aura_total(lab, covenant_aura)}",
            ]
        )

    def _characteristics_derived_text(self) -> str:
        lab_catalog = catalog.load_lab_virtue_flaw_catalog_by_id()
        lab = self.laboratory
        rows = [
            ("Occupied Size:", lab_occupied_size(lab, lab_catalog)),
            ("Free Virtues:", lab_free_virtues(lab, lab_catalog)),
            ("Base Safety:", lab_base_safety(lab, lab_catalog)),
        ]
        width = max(len(label) for label, _ in rows)
        return "\n".join(
            f"{label:<{width}} {_sign_colored(value, f'{value:g}')}"
            for label, value in rows
        )

    def _characteristics_table_text(self) -> str:
        """The 8 Characteristics as an aligned table: manual value, the
        summed Virtue+Flaw modifier, and the total after '='. Every number
        is coloured by sign (see _sign_colored())."""
        lab_catalog = catalog.load_lab_virtue_flaw_catalog_by_id()
        lab = self.laboratory
        rows = []
        for characteristic in LAB_CHARACTERISTICS:
            manual, virtue_sum, flaw_sum, total = lab_characteristic_total(
                lab, lab_catalog, characteristic
            )
            label = characteristic.replace("_", " ").title() + ":"
            rows.append((label, manual, virtue_sum + flaw_sum, total))
        label_width = max(len(label) for label, *_ in rows)
        num_width = max(
            len(f"{value:+d}")
            for _, manual, vf, total in rows
            for value in (manual, vf, total)
        )

        def cell(value: int) -> str:
            return _sign_colored(value, f"{value:>+{num_width}d}")

        return "\n".join(
            f"{label:<{label_width}} {cell(manual)} {cell(vf)} = {cell(total)}"
            for label, manual, vf, total in rows
        )

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


class CovenantSheetView(Vertical):
    """The covenant sheet mounted into WorkspaceScreen's detail pane.

    A permanent info panel (not inside any tab) above six tabs mirroring
    the covenant record sheet: Attributes, Inhabitants, Possessions,
    Economics, Library, Diary. The tabs are mostly placeholders for now.

    The panel's saga-level values (Saga, Storyguide, Current Season,
    Current Year) are inherited from the Saga and shown dimmed/read-only;
    the rest belong to the covenant and are edited with 'e'.
    """

    DEFAULT_CSS = """
    CovenantSheetView {
        height: 1fr;
    }

    CovenantSheetView #cov-info-body {
        width: 1fr;
        height: auto;
    }

    CovenantSheetView #cov-info-left {
        width: 1fr;
        height: auto;
        margin-right: 4;
    }

    CovenantSheetView #cov-info-right {
        width: 1fr;
        height: auto;
    }

    CovenantSheetView TabbedContent {
        height: 1fr;
    }

    CovenantSheetView TabPane {
        padding: 1 0;
    }

    CovenantSheetView VerticalScroll {
        height: 1fr;
        width: 1fr;
    }

    CovenantSheetView #cov-bh-row {
        width: 1fr;
        height: auto;
    }

    CovenantSheetView #section-cov-boons {
        margin-right: 2;
    }

    CovenantSheetView #inh-body {
        height: 1fr;
    }

    CovenantSheetView #inh-loyalty-body,
    CovenantSheetView #inh-misc-body {
        width: 1fr;
        height: auto;
    }

    CovenantSheetView #inh-loyalty-left,
    CovenantSheetView #inh-misc-left {
        width: 1fr;
        height: auto;
        margin-right: 4;
    }

    CovenantSheetView #inh-loyalty-right,
    CovenantSheetView #inh-misc-right {
        width: 1fr;
        height: auto;
    }

    CovenantSheetView #inh-panel {
        width: 1fr;
        height: auto;
        min-height: 6;
        max-height: 14;
        margin-top: 1;
        padding: 1 2;
        background: $panel;
    }

    CovenantSheetView #pos-body {
        height: 1fr;
    }

    CovenantSheetView #pos-panel {
        width: 1fr;
        height: auto;
        min-height: 6;
        max-height: 14;
        margin-top: 1;
        padding: 1 2;
        background: $panel;
    }

    CovenantSheetView #cov-bh-info {
        width: 1fr;
        height: auto;
        min-height: 8;
        margin-top: 1;
        padding: 1 2;
        background: $panel;
    }
    """

    def __init__(self, saga: Saga, covenant: Covenant) -> None:
        super().__init__()
        self.saga = saga
        self.covenant = covenant
        #: Set once TabbedContent's initial TabActivated has been seen -- see
        #: WorkspaceScreen.on_tabbed_content_tab_activated().
        self.initial_tab_seen = False

    def compose(self) -> ComposeResult:
        with PinnedCollapsible(title=self.covenant.name, id="section-cov-info"):
            with Horizontal(id="cov-info-body"):
                yield Static(self._info_left_text(), id="cov-info-left")
                yield Static(self._info_right_text(), id="cov-info-right")
            yield Button("Edit (e)", id="btn-cov-edit", compact=True)
        with TabbedContent(initial="tab-cov-attributes"):
            with TabPane("Attributes", id="tab-cov-attributes"), VerticalScroll():
                with SheetSection(title="Description", id="section-cov-description"):
                    yield Static(self._description_text(), id="cov-description-content")
                with SheetSection(title="Reputations", id="section-cov-reputations"):
                    yield SelectableList(
                        self._reputation_rows(), id="cov-reputations-list"
                    )
                with Horizontal(id="cov-bh-row"):
                    with SheetSection(
                        title=self._bh_title("Boon"), id="section-cov-boons"
                    ):
                        yield SelectableList(
                            self._bh_entries("Boon"), id="cov-boons-list"
                        )
                    with SheetSection(
                        title=self._bh_title("Hook"), id="section-cov-hooks"
                    ):
                        yield SelectableList(
                            self._bh_entries("Hook"), id="cov-hooks-list"
                        )
                yield Static(self._bh_info_text(None), id="cov-bh-info")
            with TabPane("Inhabitants", id="tab-cov-inhabitants"):
                yield from self._inhabitants_tab()
            with TabPane("Possessions", id="tab-cov-possessions"):
                yield from self._possessions_tab()
            with TabPane("Economics", id="tab-cov-economics"):
                yield Static(self._placeholder("Economics"))
            with TabPane("Library", id="tab-cov-library"):
                yield Static(self._placeholder("Library"))
            with TabPane("Diary", id="tab-cov-diary"):
                yield Static(self._placeholder("Diary"))

    def _inhabitants_tab(self) -> ComposeResult:
        """Loyalty, the Inhabitants summary and Miscellaneous blocks, one
        collapsible list per kind of inhabitant, and (docked below the
        scrolling part) the details panel of the chosen inhabitant."""
        covenant, saga = self.covenant, self.saga
        with Vertical(id="inh-body"):
            with VerticalScroll(id="inh-scroll"):
                with (
                    SheetSection(title="Loyalty", id="section-inh-loyalty"),
                    Horizontal(id="inh-loyalty-body"),
                ):
                    yield Static(inh.loyalty_left_text(covenant), id="inh-loyalty-left")
                    yield Static(
                        inh.loyalty_right_text(covenant), id="inh-loyalty-right"
                    )
                with SheetSection(title="Inhabitants", id="section-inh-population"):
                    yield Static(
                        inh.population_text(saga, covenant), id="inh-population-content"
                    )
                with SheetSection(title="Miscellaneous", id="section-inh-misc"):
                    left, right = inh.misc_text(covenant)
                    with Horizontal(id="inh-misc-body"):
                        yield Static(left, id="inh-misc-left")
                        yield Static(right, id="inh-misc-right")
                for kind in INHABITANT_KINDS:
                    with SheetSection(
                        title=self._inh_title(kind), id=f"section-inh-{kind}"
                    ):
                        yield SelectableList(
                            self._inh_rows(kind), id=f"inh-{kind}-list"
                        )
            yield Static(inh.detail_text(None, saga.current_year), id="inh-panel")

    def _possessions_tab(self) -> ComposeResult:
        """One collapsible list per kind of possession over the details panel of
        the chosen one (docked below the scrolling part)."""
        with Vertical(id="pos-body"):
            with VerticalScroll(id="pos-scroll"):
                for kind in POSSESSION_KINDS:
                    with SheetSection(
                        title=pos.KIND_TITLES[kind], id=f"section-pos-{kind}"
                    ):
                        yield SelectableList(
                            self._pos_rows(kind), id=f"pos-{kind}-list"
                        )
            yield Static(pos.detail_text(None), id="pos-panel")

    def _pos_entries(self, kind: str) -> list[pos.PossessionEntry]:
        return pos.entries_for_kind(self.saga, self.covenant, kind)

    def _pos_rows(self, kind: str) -> list[tuple[int, str]]:
        return [(i, pos.row_label(e)) for i, e in enumerate(self._pos_entries(kind))]

    def selected_possession(self, kind: str) -> int | None:
        """Index into the `kind` list's entries of the chosen row, or None."""
        return self.query_one(f"#pos-{kind}-list", SelectableList).selected_data_index

    def _rebuild_possessions(self) -> None:
        """Re-render every list and reset the panel."""
        for kind in POSSESSION_KINDS:
            self.query_one(f"#pos-{kind}-list", SelectableList).set_rows(
                self._pos_rows(kind)
            )
        self.query_one("#pos-panel", Static).update(pos.detail_text(None))

    def _inh_entries(self, kind: str) -> list[inh.InhabitantEntry]:
        return inh.entries_for_kind(self.saga, self.covenant, kind)

    def _inh_rows(self, kind: str) -> list[tuple[int, str]]:
        return [(i, inh.row_label(e)) for i, e in enumerate(self._inh_entries(kind))]

    def _inh_title(self, kind: str) -> str:
        """ "Magi (1)": the list's headcount -- quantities added up."""
        return f"{inh.KIND_TITLES[kind]} ({inh.headcount(self._inh_entries(kind))})"

    def selected_inhabitant(self, kind: str) -> int | None:
        """Index into the `kind` list's entries of the chosen row, or None."""
        return self.query_one(f"#inh-{kind}-list", SelectableList).selected_data_index

    def _rebuild_inhabitants(self) -> None:
        """Re-render every list, its title, the population total and the panel
        (any change can move the headcounts and the calculated total)."""
        for kind in INHABITANT_KINDS:
            self._set_section_title(
                self.query_one(f"#section-inh-{kind}", Collapsible),
                self._inh_title(kind),
            )
            self.query_one(f"#inh-{kind}-list", SelectableList).set_rows(
                self._inh_rows(kind)
            )
        self.query_one("#inh-population-content", Static).update(
            inh.population_text(self.saga, self.covenant)
        )
        self.query_one("#inh-panel", Static).update(
            inh.detail_text(None, self.saga.current_year)
        )

    def refresh_section(self, section_id: str) -> None:
        try:
            self._refresh_section(section_id)
        except NoMatches:
            # The sheet is being replaced or torn down (a refresh from a
            # dialog callback can land after that) -- nothing left to update.
            return

    def _refresh_section(self, section_id: str) -> None:
        if section_id == "section-cov-info":
            self.query_one("#section-cov-info", Collapsible).title = self.covenant.name
            self.query_one("#cov-info-left", Static).update(self._info_left_text())
            self.query_one("#cov-info-right", Static).update(self._info_right_text())
        elif section_id == "section-cov-description":
            self.query_one("#cov-description-content", Static).update(
                self._description_text()
            )
        elif section_id == "section-cov-reputations":
            self.query_one("#cov-reputations-list", SelectableList).set_rows(
                self._reputation_rows()
            )
        elif section_id == "section-inh-loyalty":
            self.query_one("#inh-loyalty-left", Static).update(
                inh.loyalty_left_text(self.covenant)
            )
            self.query_one("#inh-loyalty-right", Static).update(
                inh.loyalty_right_text(self.covenant)
            )
        elif section_id in ("section-inh-population", "section-inh-misc"):
            self.query_one("#inh-population-content", Static).update(
                inh.population_text(self.saga, self.covenant)
            )
            left, right = inh.misc_text(self.covenant)
            self.query_one("#inh-misc-left", Static).update(left)
            self.query_one("#inh-misc-right", Static).update(right)
        elif section_id.startswith("section-inh-"):
            self._rebuild_inhabitants()
        elif section_id.startswith("section-pos-"):
            self._rebuild_possessions()
        elif section_id in ("section-cov-boons", "section-cov-hooks"):
            self._rebuild_boons_hooks()
            # An Aura Boon changes the Aura shown in the info panel.
            self.refresh_section("section-cov-info")

    def _rebuild_boons_hooks(self) -> None:
        """Re-render both lists, both titles and the details panel. Always
        both: the two titles share one colour driven by comparing the totals,
        so a change to either kind can change the other's title too."""
        for kind in ("Boon", "Hook"):
            self._set_section_title(
                self.query_one(f"#section-cov-{kind.lower()}s", Collapsible),
                self._bh_title(kind),
            )
            self.query_one(f"#cov-{kind.lower()}s-list", SelectableList).set_rows(
                self._bh_entries(kind)
            )
        self.query_one("#cov-bh-info", Static).update(self._bh_info_text(None))

    def selected_boon_hook(self, kind: str) -> int | None:
        """Index into covenant.boons_hooks of the row currently selected in
        the `kind` ("Boon"/"Hook") list, or None if none is."""
        return self.query_one(
            f"#cov-{kind.lower()}s-list", SelectableList
        ).selected_data_index

    def selected_reputation(self) -> int | None:
        """Index into covenant.reputations of the chosen row, or None."""
        return self.query_one(
            "#cov-reputations-list", SelectableList
        ).selected_data_index

    @staticmethod
    def _set_section_title(section: Collapsible, title: str) -> None:
        """Set a section's title, forcing the label to repaint. Textual's
        Content compares equal on plain text alone, so a colour-only change
        (Hooks (7 pts) turning red) would otherwise leave the old colour
        showing."""
        section.title = title
        title_widget = section.query_one("CollapsibleTitle")
        # The label reactive skips "unchanged" values too, so store the new
        # Content directly (set_reactive bypasses that check), then repaint.
        title_widget.set_reactive(type(title_widget).label, Content.from_text(title))
        title_widget._update_label()

    def on_selectable_list_chosen(self, event: SelectableList.Chosen) -> None:
        """A Boon or Hook row was chosen: fill the details panel. (Reputations
        have no panel -- a name and a score have nothing more to show.)"""
        list_id = event.selectable_list.id or ""
        if list_id.startswith("inh-") and list_id.endswith("-list"):
            event.stop()
            kind = list_id[len("inh-") : -len("-list")]
            # One selection across all the inhabitant lists.
            for other in INHABITANT_KINDS:
                if other != kind:
                    self.query_one(
                        f"#inh-{other}-list", SelectableList
                    ).clear_selection()
            entries = self._inh_entries(kind)
            chosen = (
                entries[event.data_index] if event.data_index < len(entries) else None
            )
            self.query_one("#inh-panel", Static).update(
                inh.detail_text(chosen, self.saga.current_year)
            )
            return
        if list_id.startswith("pos-") and list_id.endswith("-list"):
            event.stop()
            kind = list_id[len("pos-") : -len("-list")]
            for other in POSSESSION_KINDS:  # one selection across the lists
                if other != kind:
                    self.query_one(
                        f"#pos-{other}-list", SelectableList
                    ).clear_selection()
            entries = self._pos_entries(kind)
            chosen = (
                entries[event.data_index] if event.data_index < len(entries) else None
            )
            self.query_one("#pos-panel", Static).update(pos.detail_text(chosen))
            return
        if list_id not in ("cov-boons-list", "cov-hooks-list"):
            return
        event.stop()
        # One selection across both lists: unchoose the other one.
        other = "cov-hooks-list" if list_id == "cov-boons-list" else "cov-boons-list"
        self.query_one(f"#{other}", SelectableList).clear_selection()
        self.query_one("#cov-bh-info", Static).update(
            self._bh_info_text(event.data_index)
        )

    @staticmethod
    def _aligned(rows: list[tuple[str, str]]) -> str:
        width = max(len(label) for label, _ in rows)
        return "\n".join(f"{label + ':':<{width + 1}} {value}" for label, value in rows)

    @staticmethod
    def _inherited(value: str) -> str:
        """Dim a value that comes from the saga and isn't edited here."""
        return f"[dim]{escape(value)}[/]"

    def _aura_text(self) -> str:
        """The base Aura, plus where a Boon-raised total comes from."""
        cov = self.covenant
        effective = covenant_effective_aura(
            cov, catalog.load_covenant_boon_hook_catalog_by_id()
        )
        if effective == cov.aura:
            return str(cov.aura)
        return f"{effective} (base {cov.aura}, {effective - cov.aura:+d} Boons)"

    def _info_left_text(self) -> str:
        cov, saga = self.covenant, self.saga
        founded = "(not set)" if cov.year_founded is None else str(cov.year_founded)
        return self._aligned(
            [
                ("Saga", self._inherited(saga.name)),
                ("Storyguide", self._inherited(saga.storyguide or "(not set)")),
                ("Year Founded", founded),
                ("Aegis of the Hearth", str(cov.aegis_of_the_hearth)),
                ("Living Conditions (Magi)", str(cov.living_conditions_magi)),
                ("Aura", self._aura_text()),
            ]
        )

    def _info_right_text(self) -> str:
        cov, saga = self.covenant, self.saga
        return self._aligned(
            [
                ("Tribunal", escape(cov.tribunal) if cov.tribunal else "(not set)"),
                ("Current Season", self._inherited(saga.current_season)),
                ("Current Year", self._inherited(str(saga.current_year))),
                ("Aegis' Penetration", str(cov.aegis_penetration)),
                ("Living Conditions (Mundane)", str(cov.living_conditions_mundane)),
                ("Covenant Season", cov.covenant_season),
            ]
        )

    def _placeholder(self, tab_name: str) -> str:
        return f"{tab_name} aren't built yet -- coming in a future update."

    def _description_text(self) -> str:
        # Backed by Covenant.notes (the free-text field set at creation).
        text = self.covenant.notes.strip()
        return markdown_inline(text) if text else "(no description)"

    def _reputation_rows(self) -> list[tuple[int, str]]:
        """The covenant's Reputations as (index, label) rows."""
        return [
            (index, f"{escape(r.name)}: {r.score:+d}")
            for index, r in enumerate(self.covenant.reputations)
        ]

    def _bh_title(self, kind: str) -> str:
        """ "Boons (7 pts)" / "Hooks (7 pts)": Boons show the points they
        cost, Hooks the points they provide. The parenthesised total of BOTH
        titles takes one colour from comparing the two (see _balance_colour)."""
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        boons = covenant_boon_points(self.covenant, by_id)
        hooks = covenant_hook_points(self.covenant, by_id)
        points = boons if kind == "Boon" else hooks
        colour = _balance_colour(boons, hooks)
        unit = "pt" if points == 1 else "pts"
        return f"{kind}s [{colour}]({points:g} {unit})[/]"

    def _bh_entries(self, kind: str) -> list[tuple[int, str]]:
        """The attached Boons or Hooks of `kind` as (index into
        covenant.boons_hooks, display label) pairs, in attach order."""
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        return [
            (index, escape(catalog.describe_boon_hook(bh, by_id)))
            for index, bh in enumerate(self.covenant.boons_hooks)
            if bh.vf_id in by_id and by_id[bh.vf_id].type == kind
        ]

    def _bh_info_text(self, index: int | None) -> str:
        """The details panel for the attached Boon/Hook at `index` into
        covenant.boons_hooks: its name, type, notes, the user's own
        description (if any) and then the official rules text."""
        if index is None:
            return "[dim]Select a Boon or Hook to read its rules.[/]"
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        instance = self.covenant.boons_hooks[index]
        definition = by_id.get(instance.vf_id)
        if definition is None:
            return escape(f"{instance.vf_id} (not in catalog)")

        lines = [f"[b]Name:[/] {escape(catalog.describe_boon_hook(instance, by_id))}"]
        if definition.category:
            lines.append(f"[b]Type:[/] {definition.category}")
        lines.append(f"[b]Tier:[/] {_tier_text(definition)}")
        if definition.requires:
            lines.append(
                f"[b]Requires:[/] {_boon_hook_names(definition.requires, by_id)}"
            )
        if definition.excludes:
            lines.append(
                f"[b]Not with:[/] {_boon_hook_names(definition.excludes, by_id)}"
            )
        if definition.repeatable:
            lines.append("[dim]May be taken more than once.[/]")
        # The user's own description leads; the official rules text follows.
        description = instance.params.get(BOON_HOOK_DESCRIPTION, "").strip()
        if description:
            lines += ["", "[b]Description:[/]", markdown_inline(description)]
        lines += ["", "[b]Rules:[/]", escape(definition.description)]
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
        ("t", "advance_season", "Advance Season"),
        ("T", "set_date", "Set Date"),
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
        "section-cov-reputations",
        "section-cov-boons",
        "section-cov-hooks",
        *(f"section-inh-{kind}" for kind in INHABITANT_KINDS),
        *(f"section-pos-{kind}" for kind in POSSESSION_KINDS),
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
        "section-cov-reputations",
        "section-cov-boons",
        "section-cov-hooks",
        *(f"section-inh-{kind}" for kind in INHABITANT_KINDS),
        *(f"section-pos-{kind}" for kind in POSSESSION_KINDS),
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
        "section-lab-specialties",
        "section-lab-features",
        "section-lab-rooms",
        "section-lab-raw-vis",
        "section-lab-items",
        "tab-lab-diary",
        "section-cov-info",
        "section-cov-description",
        "section-cov-reputations",
        "section-cov-boons",
        "section-cov-hooks",
        "section-inh-loyalty",
        "section-inh-population",
        "section-inh-misc",
        *(f"section-inh-{kind}" for kind in INHABITANT_KINDS),
        *(f"section-pos-{kind}" for kind in POSSESSION_KINDS),
    }

    #: Covenant tabs that own their own a/A/e dispatch (keyed by tab id).
    #: None yet -- every covenant tab is a placeholder, so the dispatch falls
    #: back to the always-visible info panel. See _active_covenant_section().
    _COVENANT_DISPATCH_TABS: ClassVar[set[str]] = set()

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
        self._covenant_sheet_view: CovenantSheetView | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="workspace-body"):
            yield Tree(self.saga.name, data=("saga",), id="nav-tree")
            yield VerticalScroll(id="detail-pane")
        yield Footer()

    async def on_mount(self) -> None:
        self._update_saga_clock()
        self._rebuild_tree()
        await self._show_saga_detail()

    def _update_saga_clock(self) -> None:
        """Shows the saga's current date in the Header, on every screen of
        the workspace -- the saga owns the calendar, everything inherits it."""
        saga = self.saga
        self.sub_title = f"{saga.name} | {saga.current_season} {saga.current_year}"

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

        # Characters and labs with no (or a no-longer-existing) covenant live
        # directly under the saga -- assigning to a covenant is optional, and
        # this is where things land if they're taken out of one.
        covenant_ids = {c.id for c in self.saga.covenants}
        loose_characters = [
            c for c in self.saga.characters if c.covenant_id not in covenant_ids
        ]
        if loose_characters:
            group = tree.root.add(
                f"Unassigned Characters ({len(loose_characters)})",
                data=("character_group", None),
                expand=True,
            )
            for character in loose_characters:
                group.add_leaf(
                    f"{character.name} ({character.type})",
                    data=("character", character.id),
                )
        loose_labs = [
            lab for lab in self.saga.laboratories if lab.covenant_id not in covenant_ids
        ]
        if loose_labs:
            group = tree.root.add(
                f"Unassigned Laboratories ({len(loose_labs)})",
                data=("laboratory_group", None),
                expand=True,
            )
            for lab in loose_labs:
                group.add_leaf(lab.name, data=("laboratory", lab.id))

    def _covenant_by_id(self, covenant_id: str | None) -> Covenant | None:
        return next((c for c in self.saga.covenants if c.id == covenant_id), None)

    async def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        data = event.node.data
        if data is None:
            return

        kind = data[0]
        self.selected_kind = kind
        self._character_sheet_view = None
        self._laboratory_sheet_view = None
        self._covenant_sheet_view = None

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
            covenant = self._covenant_by_id(data[1])
            self.selected_covenant = covenant
            self.selected_character = None
            await self._show_placeholder_detail(
                f"Characters in {covenant.name}"
                if covenant
                else "Unassigned Characters",
                "Select a character from the tree, or press 'c' to add one."
                if covenant
                else "These characters aren't assigned to a covenant. Select one "
                "from the tree, or press 'c' to add one.",
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
            covenant = self._covenant_by_id(data[1])
            self.selected_covenant = covenant
            self.selected_laboratory = None
            await self._show_placeholder_detail(
                f"Laboratories in {covenant.name}"
                if covenant
                else "Unassigned Laboratories",
                "Select a laboratory from the tree, or press 'l' to add one."
                if covenant
                else "These laboratories aren't assigned to a covenant. Select "
                "one from the tree, or press 'l' to add one.",
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
        # Characters and labs may be created anywhere: a selected covenant
        # is just the default for the dialog's optional Covenant field.
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
        if self.selected_kind == "covenant":
            return self._active_covenant_section()
        return None

    def _active_covenant_section(self) -> str | None:
        """Same idea as _active_laboratory_section(), except that every
        covenant tab is a placeholder for now: with nothing focused inside a
        Collapsible (and no tab owning its own dispatch), fall back to the
        always-visible info panel so 'e' edits the covenant from any tab."""
        if self._covenant_sheet_view is None:
            return None
        try:
            tab_id = self._covenant_sheet_view.query_one(TabbedContent).active
        except NoMatches:
            return None
        if not tab_id:
            return None

        focused = self.app.focused
        if focused is not None:
            for widget in focused.ancestors_with_self:
                if isinstance(widget, Collapsible) and widget.id:
                    return widget.id
        if tab_id in self._COVENANT_DISPATCH_TABS:
            return tab_id
        return "section-cov-info"

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
        view = {
            "laboratory": self._laboratory_sheet_view,
            "covenant": self._covenant_sheet_view,
        }.get(self.selected_kind)
        initial = False
        if view is not None:
            # TabbedContent announces its initial tab once, right after
            # mounting. That's not a user tab switch, and treating it as one
            # would clear the focus _show_*_detail() just set.
            initial = not view.initial_tab_seen
            view.initial_tab_seen = True
        self._focus_first_section(initial=initial)
        self.refresh_bindings()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-lab-identity-edit":
            event.stop()
            self._edit_lab_identity()
        elif event.button.id == "btn-lab-characteristics-edit":
            event.stop()
            self._edit_lab_characteristics()
        elif event.button.id == "btn-cov-edit":
            event.stop()
            self._edit_covenant()

    def _focus_first_section(self, *, initial: bool = False) -> None:
        if self.selected_kind == "character":
            self._focus_first_character_section()
        elif self.selected_kind == "laboratory":
            self._focus_first_laboratory_section(initial=initial)
        elif self.selected_kind == "covenant":
            self._focus_first_covenant_section(initial=initial)

    def _focus_first_covenant_section(self, *, initial: bool = False) -> None:
        """Focus the always-visible info panel when a covenant is first
        shown, so 'e' works straight away. On a later tab switch focus that
        tab's first section, or -- for a flat tab -- clear focus (see
        _focus_first_laboratory_section() for why); dispatch then falls back
        to the info panel."""
        if self._covenant_sheet_view is None:
            return
        view = self._covenant_sheet_view
        try:
            if initial:
                collapsible = view.query(Collapsible).first()
            else:
                tabbed = view.query_one(TabbedContent)
                if not tabbed.active:
                    return
                pane = view.query_one(f"#{tabbed.active}", TabPane)
                collapsible = pane.query(Collapsible).first()
        except NoMatches:
            # A flat tab (nothing to focus): clear focus so dispatch falls
            # back to the info panel -- see _active_covenant_section().
            if not initial:
                self.screen.set_focus(None)
            return
        collapsible.query_one("CollapsibleTitle").focus()

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
            f"Current date: {saga.current_season} {saga.current_year}",
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
        view = CovenantSheetView(self.saga, covenant)
        await self._set_detail(view)
        self._covenant_sheet_view = view
        self._focus_first_section(initial=True)

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

    def _refresh_covenant_section(self, section_id: str) -> None:
        if self._covenant_sheet_view is not None:
            self._covenant_sheet_view.refresh_section(section_id)

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
            CharacterCreateScreen(
                self.saga, default_covenant_id=covenant.id if covenant else None
            ),
            handle_result,
        )

    def action_create_laboratory(self) -> None:
        covenant = self.selected_covenant

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
        elif section == "section-cov-reputations":
            self._add_covenant_reputation()
        elif section == "section-cov-boons":
            self._add_boon_hook("Boon")
        elif section == "section-cov-hooks":
            self._add_boon_hook("Hook")
        elif (kind := self._inhabitant_kind(section)) is not None:
            self._add_inhabitant(kind)
        elif (kind := self._possession_kind(section)) is not None:
            self._add_possession(kind)

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
        elif section == "section-cov-reputations":
            self._remove_covenant_reputation()
        elif section == "section-cov-boons":
            self._remove_boon_hook("Boon")
        elif section == "section-cov-hooks":
            self._remove_boon_hook("Hook")
        elif (kind := self._inhabitant_kind(section)) is not None:
            self._remove_inhabitant(kind)
        elif (kind := self._possession_kind(section)) is not None:
            self._remove_possession(kind)

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
        elif section == "section-lab-specialties":
            self._edit_specialty()
        elif section == "section-lab-features":
            self._edit_feature()
        elif section == "section-lab-rooms":
            self._edit_room()
        elif section == "section-lab-raw-vis":
            self._edit_lab_raw_vis()
        elif section == "section-lab-items":
            self._edit_inventory_item()
        elif section == "tab-lab-diary":
            self._edit_diary_entry()
        elif section == "section-cov-info":
            self._edit_covenant()
        elif section == "section-cov-description":
            self._edit_covenant_description()
        elif section == "section-cov-reputations":
            self._edit_covenant_reputation()
        elif section == "section-cov-boons":
            self._edit_boon_hook("Boon")
        elif section == "section-cov-hooks":
            self._edit_boon_hook("Hook")
        elif section == "section-inh-loyalty":
            self._edit_loyalty()
        elif section == "section-inh-population":
            self._edit_population()
        elif section == "section-inh-misc":
            self._edit_miscellaneous()
        elif (kind := self._inhabitant_kind(section)) is not None:
            self._edit_inhabitant(kind)
        elif (kind := self._possession_kind(section)) is not None:
            self._edit_possession(kind)

    # -- Covenant: Possessions tab --

    @staticmethod
    def _possession_kind(section: str | None) -> str | None:
        """The possession kind a list section id stands for, or None."""
        if section and section.startswith("section-pos-"):
            kind = section[len("section-pos-") :]
            if kind in POSSESSION_KINDS:
                return kind
        return None

    def _selected_possession(self, kind: str) -> int | None:
        view = self._covenant_sheet_view
        return view.selected_possession(kind) if view is not None else None

    def _possession_entries(self, kind: str) -> list[pos.PossessionEntry]:
        covenant = self.selected_covenant
        if covenant is None:
            return []
        return pos.entries_for_kind(self.saga, covenant, kind)

    def _add_possession(self, kind: str) -> None:
        self._possession_form(kind, None)

    def _edit_possession(self, kind: str) -> None:
        """Edit the chosen possession; with none chosen, ask which one."""
        entries = self._possession_entries(kind)
        selected = self._selected_possession(kind)
        if selected is not None and selected < len(entries):
            self._possession_form(kind, entries[selected])
            return
        if not entries:
            self.notify(f"No {pos.KIND_TITLES[kind]} to edit.")
            return

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._possession_form(kind, entries[index])

        self.app.push_screen(
            RemovalPickerScreen(
                f"Edit which {pos.KIND_SINGULAR[kind]}?",
                [e.name or "(unnamed)" for e in entries],
            ),
            handle_index,
        )

    def _possession_form(self, kind: str, entry: pos.PossessionEntry | None) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        title = (
            f"Add a {pos.KIND_SINGULAR[kind]}"
            if entry is None
            else f"Edit {entry.name or 'this ' + pos.KIND_SINGULAR[kind].lower()}"
        )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            if entry is not None and entry.record is not None:
                for key, value in values.items():
                    setattr(entry.record, key, value)
            else:
                # A new entry, or a laboratory's sanctum edited for the first time.
                lab_id = entry.lab.id if entry is not None and entry.lab else None
                covenant.possessions.append(
                    Possession(
                        id=storage.generate_unique_id(
                            values.get("name") or f"{kind}-{lab_id or 'new'}",
                            [r.id for r in covenant.possessions],
                        ),
                        kind=kind,
                        lab_id=lab_id,
                        **values,
                    )
                )
            storage.save_saga(self.saga)
            self._refresh_covenant_section(f"section-pos-{kind}")

        self.app.push_screen(
            FieldsDialog(
                title, _possession_fields(kind, entry), validate=_possession_problem
            ),
            handle_result,
        )

    def _remove_possession(self, kind: str) -> None:
        """Delete the chosen possession (after confirming); with none chosen,
        ask which one. A laboratory listed as a sanctum can't be deleted here."""
        entries = self._possession_entries(kind)
        selected = self._selected_possession(kind)
        if selected is not None and selected < len(entries):
            self._confirm_remove_possession(kind, entries[selected])
            return
        if not entries:
            self.notify(f"No {pos.KIND_TITLES[kind]} to remove.")
            return

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._confirm_remove_possession(kind, entries[index])

        self.app.push_screen(
            RemovalPickerScreen(
                f"Remove a {pos.KIND_SINGULAR[kind]}",
                [e.name or "(unnamed)" for e in entries],
            ),
            handle_index,
        )

    def _confirm_remove_possession(self, kind: str, entry: pos.PossessionEntry) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        if entry.auto:
            self.notify(
                f"{entry.name} is a laboratory of this covenant, so it can't be deleted "
                "here. Move it to another covenant from the laboratory's Identity instead."
            )
            return

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed and entry.record in covenant.possessions:
                covenant.possessions.remove(entry.record)
                storage.save_saga(self.saga)
                self._refresh_covenant_section(f"section-pos-{kind}")

        self.app.push_screen(
            ConfirmScreen(f"Delete {escape(entry.name or 'this entry')}?"),
            handle_confirmed,
        )

    # -- Covenant: Inhabitants tab --

    @staticmethod
    def _inhabitant_kind(section: str | None) -> str | None:
        """The inhabitant kind a list section id stands for, or None."""
        if section and section.startswith("section-inh-"):
            kind = section[len("section-inh-") :]
            if kind in INHABITANT_KINDS:
                return kind
        return None

    def _selected_inhabitant(self, kind: str) -> int | None:
        view = self._covenant_sheet_view
        return view.selected_inhabitant(kind) if view is not None else None

    def _inhabitant_entries(self, kind: str) -> list[inh.InhabitantEntry]:
        covenant = self.selected_covenant
        if covenant is None:
            return []
        return inh.entries_for_kind(self.saga, covenant, kind)

    def _add_inhabitant(self, kind: str) -> None:
        """Add one. Grog-derived kinds first offer the covenant's unassigned
        grogs (or a brand-new person); Magi, Companions and animals go
        straight to the form."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        if kind not in inh.GROG_KINDS:
            self._inhabitant_form(kind, None, None)
            return

        grogs = inh.available_grogs(self.saga, covenant)
        labels = ["(New person -- not from a character sheet)"] + [
            g.name
            + (f"  (born {g.background.year_born})" if g.background.year_born else "")
            for g in grogs
        ]

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._inhabitant_form(kind, None, grogs[index - 1] if index else None)

        self.app.push_screen(
            RemovalPickerScreen(f"Add a {inh.KIND_SINGULAR[kind]}", labels),
            handle_index,
        )

    def _edit_inhabitant(self, kind: str) -> None:
        """Edit the chosen inhabitant; with none chosen, ask which one."""
        entries = self._inhabitant_entries(kind)
        selected = self._selected_inhabitant(kind)
        if selected is not None and selected < len(entries):
            self._inhabitant_form(kind, entries[selected], None)
            return
        if not entries:
            self.notify(f"No {inh.KIND_TITLES[kind]} to edit.")
            return

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._inhabitant_form(kind, entries[index], None)

        self.app.push_screen(
            RemovalPickerScreen(
                f"Edit which {inh.KIND_SINGULAR[kind]}?",
                [e.name or "(unnamed)" for e in entries],
            ),
            handle_index,
        )

    def _inhabitant_form(
        self, kind: str, entry: inh.InhabitantEntry | None, grog: Character | None
    ) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        title = (
            f"Add a {inh.KIND_SINGULAR[kind]}"
            if entry is None
            else f"Edit {entry.name or 'this ' + inh.KIND_SINGULAR[kind].lower()}"
        )

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            if entry is None:
                covenant.inhabitants.append(
                    Inhabitant(
                        id=storage.generate_unique_id(
                            values.get("name") or kind,
                            [r.id for r in covenant.inhabitants],
                        ),
                        kind=kind,
                        character_id=grog.id if grog is not None else None,
                        **values,
                    )
                )
            elif entry.record is not None:
                for key, value in values.items():
                    setattr(entry.record, key, value)
            else:  # a character listed from its sheet, edited for the first time
                covenant.inhabitants.append(
                    Inhabitant(
                        id=storage.generate_unique_id(
                            f"{kind}-{entry.name}", [r.id for r in covenant.inhabitants]
                        ),
                        kind=kind,
                        character_id=entry.character.id if entry.character else None,
                        **values,
                    )
                )
            storage.save_saga(self.saga)
            self._refresh_covenant_section(f"section-inh-{kind}")

        self.app.push_screen(
            FieldsDialog(
                title,
                _inhabitant_fields(kind, entry, grog, self.saga.current_year),
                validate=_inhabitant_problem,
            ),
            handle_result,
        )

    def _remove_inhabitant(self, kind: str) -> None:
        """Delete the chosen inhabitant (after confirming); with none chosen,
        ask which one. People listed from a character sheet can't be deleted
        here -- that would mean changing the sheet."""
        entries = self._inhabitant_entries(kind)
        selected = self._selected_inhabitant(kind)
        if selected is not None and selected < len(entries):
            self._confirm_remove_inhabitant(kind, entries[selected])
            return
        if not entries:
            self.notify(f"No {inh.KIND_TITLES[kind]} to remove.")
            return

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._confirm_remove_inhabitant(kind, entries[index])

        self.app.push_screen(
            RemovalPickerScreen(
                f"Remove a {inh.KIND_SINGULAR[kind]}",
                [e.name or "(unnamed)" for e in entries],
            ),
            handle_index,
        )

    def _confirm_remove_inhabitant(self, kind: str, entry: inh.InhabitantEntry) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        name = escape(entry.name or "this entry")

        if entry.auto and entry.character is not None:
            # Listed from a character sheet (e.g. a magus who died): they stay
            # in the covenant on their sheet, but stop counting as an inhabitant.
            character_id = entry.character.id

            def handle_departed(confirmed: bool | None) -> None:
                if not confirmed:
                    return
                if entry.record is not None and entry.record in covenant.inhabitants:
                    entry.record.departed = True
                else:
                    covenant.inhabitants.append(
                        Inhabitant(
                            id=storage.generate_unique_id(
                                f"{kind}-{entry.name}",
                                [r.id for r in covenant.inhabitants],
                            ),
                            kind=kind,
                            character_id=character_id,
                            departed=True,
                        )
                    )
                storage.save_saga(self.saga)
                self._refresh_covenant_section(f"section-inh-{kind}")

            self.app.push_screen(
                ConfirmScreen(
                    f"Remove {name} from the {inh.KIND_TITLES[kind]} list?\n\n"
                    "They stay in the covenant on their character sheet, but "
                    "will no longer count as an inhabitant."
                ),
                handle_departed,
            )
            return

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed and entry.record in covenant.inhabitants:
                covenant.inhabitants.remove(entry.record)
                storage.save_saga(self.saga)
                self._refresh_covenant_section(f"section-inh-{kind}")

        self.app.push_screen(ConfirmScreen(f"Delete {name}?"), handle_confirmed)

    def _edit_loyalty(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        loyalty = covenant.loyalty
        styles = inh.governance_names(covenant)
        if styles:
            governance = DialogField(
                "_g",
                "Type of Governance",
                "info",
                f"{', '.join(styles)} (from your Boons)",
            )
        else:
            governance = DialogField(
                "governance", "Type of Governance", "text", loyalty.governance
            )
        fields = [
            governance,
            DialogField(
                "base_points", "Base Loyalty Points", "int", loyalty.base_points
            ),
            DialogField(
                "total_modifiers", "Total modifiers", "int", loyalty.total_modifiers
            ),
            DialogField(
                "current_points",
                "Current Loyalty Points",
                "int",
                loyalty.current_points,
            ),
            DialogField(
                "prevailing_score",
                "Prevailing Loyalty Score",
                "int",
                loyalty.prevailing_score,
            ),
            DialogField(
                "living_conditions",
                "Living Conditions",
                "int",
                loyalty.living_conditions,
            ),
            DialogField(
                "equipment",
                "Equipment",
                "select",
                loyalty.equipment,
                options=[(o, o) for o in LOYALTY_EQUIPMENT],
            ),
            DialogField(
                "equipment_modifier",
                "  Equipment modifier",
                "int",
                loyalty.equipment_modifier,
            ),
            DialogField(
                "money",
                "Money",
                "select",
                loyalty.money,
                options=[(o, o) for o in LOYALTY_MONEY],
            ),
            DialogField(
                "money_modifier", "  Money modifier", "int", loyalty.money_modifier
            ),
            DialogField("specialists", "Specialists", "int", loyalty.specialists),
            DialogField("familiarity", "Familiarity", "int", loyalty.familiarity),
            DialogField(
                "actions_and_events",
                "Actions and events",
                "int",
                loyalty.actions_and_events,
            ),
        ]

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            for key, value in values.items():
                setattr(loyalty, key, value)
            storage.save_saga(self.saga)
            self._refresh_covenant_section("section-inh-loyalty")

        self.app.push_screen(FieldsDialog("Edit Loyalty", fields), handle_result)

    def _edit_population(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        pop = covenant.population
        fields = [
            DialogField("teamsters", "Number of Teamsters", "int", pop.teamsters),
            DialogField(
                "teamsters_needed", "Teamsters Needed", "int", pop.teamsters_needed
            ),
            DialogField("servants", "Number of Servants", "int", pop.servants),
            DialogField(
                "servants_needed", "Servants Needed", "int", pop.servants_needed
            ),
            DialogField("other_people", "Other People", "int", pop.other_people),
            DialogField(
                "_t",
                "Total Inhabitants",
                "info",
                f"{inh.total_inhabitants(self.saga, covenant)} (calculated)",
            ),
        ]

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            for key, value in values.items():
                setattr(pop, key, value)
            storage.save_saga(self.saga)
            self._refresh_covenant_section("section-inh-population")

        self.app.push_screen(FieldsDialog("Edit Inhabitants", fields), handle_result)

    def _edit_miscellaneous(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        pop = covenant.population
        fields = [
            DialogField("aging_magi", "Aging for Magi", "int", pop.aging_magi),
            DialogField("aging_mundane", "Aging for Mundane", "int", pop.aging_mundane),
            DialogField("magic_laborers", "Magic Laborers", "int", pop.magic_laborers),
            DialogField("magic_servants", "Magic Servants", "int", pop.magic_servants),
            DialogField(
                "magic_teamsters", "Magic Teamsters", "int", pop.magic_teamsters
            ),
            DialogField("magic_turbula", "Magic Turbula", "int", pop.magic_turbula),
        ]

        def handle_result(values: dict[str, Any] | None) -> None:
            if values is None:
                return
            for key, value in values.items():
                setattr(pop, key, value)
            storage.save_saga(self.saga)
            self._refresh_covenant_section("section-inh-misc")

        self.app.push_screen(FieldsDialog("Edit Miscellaneous", fields), handle_result)

    # -- Covenant: Description / Reputations / Boons & Hooks --

    def _edit_covenant_description(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return

        def handle_result(text: str | None) -> None:
            if text is not None:
                covenant.notes = text
                storage.save_saga(self.saga)
                self._refresh_covenant_section("section-cov-description")

        self.app.push_screen(
            EditCovenantDescriptionScreen(covenant.notes), handle_result
        )

    def _reputation_prompt(
        self, title: str, existing: ScoredTrait | None = None
    ) -> ScoredTraitPromptScreen:
        low, high = _COVENANT_REPUTATION_RANGE
        return ScoredTraitPromptScreen(
            title,
            "e.g. Feared by the local nobility",
            existing,
            min_score=low,
            max_score=high,
        )

    def _add_covenant_reputation(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return

        def handle_result(trait: ScoredTrait | None) -> None:
            if trait is not None:
                covenant.reputations.append(trait)
                storage.save_saga(self.saga)
                self._refresh_covenant_section("section-cov-reputations")

        self.app.push_screen(self._reputation_prompt("Add a Reputation"), handle_result)

    def _selected_reputation(self) -> int | None:
        view = self._covenant_sheet_view
        return view.selected_reputation() if view is not None else None

    def _edit_covenant_reputation(self) -> None:
        """Edit the chosen Reputation; with none chosen, ask which one."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        selected = self._selected_reputation()
        if selected is not None:
            self._edit_covenant_reputation_at(selected)
            return
        if not covenant.reputations:
            self.notify("No Reputations to edit.")
            return

        labels = [f"{r.name}: {r.score:+d}" for r in covenant.reputations]

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._edit_covenant_reputation_at(index)

        self.app.push_screen(
            RemovalPickerScreen("Edit which Reputation?", labels), handle_index
        )

    def _edit_covenant_reputation_at(self, index: int) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return

        def handle_result(trait: ScoredTrait | None) -> None:
            if trait is not None:
                covenant.reputations[index] = trait
                storage.save_saga(self.saga)
                self._refresh_covenant_section("section-cov-reputations")

        self.app.push_screen(
            self._reputation_prompt("Edit a Reputation", covenant.reputations[index]),
            handle_result,
        )

    def _remove_covenant_reputation(self) -> None:
        """Delete the chosen Reputation (after confirming); with none
        chosen, ask which one first."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        selected = self._selected_reputation()
        if selected is not None:
            self._confirm_remove_covenant_reputation(selected)
            return
        if not covenant.reputations:
            self.notify("No Reputations to remove.")
            return

        labels = [f"{r.name}: {r.score:+d}" for r in covenant.reputations]

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._confirm_remove_covenant_reputation(index)

        self.app.push_screen(
            RemovalPickerScreen("Remove a Reputation", labels), handle_index
        )

    def _confirm_remove_covenant_reputation(self, index: int) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        name = covenant.reputations[index].name

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                del covenant.reputations[index]
                storage.save_saga(self.saga)
                self._refresh_covenant_section("section-cov-reputations")

        self.app.push_screen(ConfirmScreen(f"Delete {escape(name)}?"), handle_confirmed)

    def _attached_boons_hooks(
        self, covenant: Covenant, kind: str
    ) -> list[tuple[int, VirtueFlawInstance]]:
        """The covenant's attached Boons or Hooks (`kind`), each with its
        index into covenant.boons_hooks so callers can edit/delete the real
        entry from a filtered list."""
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        return [
            (index, bh)
            for index, bh in enumerate(covenant.boons_hooks)
            if bh.vf_id in by_id and by_id[bh.vf_id].type == kind
        ]

    def _add_boon_hook(self, kind: str) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        attached_ids = [bh.vf_id for bh in covenant.boons_hooks]

        def handle_result(instance: VirtueFlawInstance | None) -> None:
            if instance is not None:
                covenant.boons_hooks.append(instance)
                storage.save_saga(self.saga)
                self._refresh_covenant_section(_BOON_HOOK_SECTION[kind])

        self.app.push_screen(
            CovenantBoonHookPickerScreen(kind, attached_ids), handle_result
        )

    def _selected_boon_hook(self, kind: str) -> int | None:
        view = self._covenant_sheet_view
        return view.selected_boon_hook(kind) if view is not None else None

    def _remove_boon_hook(self, kind: str) -> None:
        """Delete the selected Boon/Hook (after confirming). With nothing
        selected in this section, ask which one first."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        selected = self._selected_boon_hook(kind)
        if selected is not None:
            self._confirm_remove_boon_hook(kind, selected)
            return

        attached = self._attached_boons_hooks(covenant, kind)
        if not attached:
            self.notify(f"No {kind}s to remove.")
            return
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        labels = [catalog.describe_boon_hook(bh, by_id) for _, bh in attached]

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._confirm_remove_boon_hook(kind, attached[index][0])

        self.app.push_screen(
            RemovalPickerScreen(f"Remove a {kind}", labels), handle_index
        )

    def _confirm_remove_boon_hook(self, kind: str, index: int) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        label = catalog.describe_boon_hook(covenant.boons_hooks[index], by_id)

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                del covenant.boons_hooks[index]
                storage.save_saga(self.saga)
                self._refresh_covenant_section(_BOON_HOOK_SECTION[kind])

        self.app.push_screen(
            ConfirmScreen(f"Delete {escape(label)}?"), handle_confirmed
        )

    def _edit_boon_hook(self, kind: str) -> None:
        """Edit the selected Boon/Hook's detail and description. With nothing
        selected in this section, ask which one first."""
        covenant = self.selected_covenant
        if covenant is None:
            return
        selected = self._selected_boon_hook(kind)
        if selected is not None:
            self._edit_boon_hook_at(kind, selected)
            return

        attached = self._attached_boons_hooks(covenant, kind)
        if not attached:
            self.notify(f"No {kind}s to edit.")
            return
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        labels = [catalog.describe_boon_hook(bh, by_id) for _, bh in attached]

        def handle_index(index: int | None) -> None:
            if index is not None:
                self._edit_boon_hook_at(kind, attached[index][0])

        self.app.push_screen(
            RemovalPickerScreen(f"Edit which {kind}?", labels), handle_index
        )

    def _edit_boon_hook_at(self, kind: str, index: int) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return
        by_id = catalog.load_covenant_boon_hook_catalog_by_id()
        instance = covenant.boons_hooks[index]

        def handle_result(result: tuple[str, str] | None) -> None:
            if result is None:
                return
            detail, description = result
            instance.params = _boon_hook_params(detail, description, instance.params)
            storage.save_saga(self.saga)
            self._refresh_covenant_section(_BOON_HOOK_SECTION[kind])

        self.app.push_screen(
            BoonHookDetailScreen(
                kind,
                by_id[instance.vf_id].name,
                detail=instance.params.get(BOON_HOOK_DETAIL, ""),
                description=instance.params.get(BOON_HOOK_DESCRIPTION, ""),
            ),
            handle_result,
        )

    # -- Covenant --

    def _edit_covenant(self) -> None:
        covenant = self.selected_covenant
        if covenant is None:
            return

        def handle_result(result: dict[str, object] | None) -> None:
            if result is None:
                return
            for field, value in result.items():
                setattr(covenant, field, value)
            storage.save_saga(self.saga)
            self._rebuild_tree()
            self._refresh_covenant_section("section-cov-info")

        self.app.push_screen(EditCovenantScreen(covenant), handle_result)

    # -- Saga time --

    async def _apply_saga_date(self, season: str, year: int) -> None:
        """Single path for every change to the saga's calendar: store it, then
        refresh everything that inherits it (Header, covenant panel, saga
        summary)."""
        saga = self.saga
        saga.current_season, saga.current_year = season, year
        storage.save_saga(saga)
        self._update_saga_clock()
        self._refresh_covenant_section("section-cov-info")
        if self.selected_kind == "saga":
            await self._show_saga_detail()

    def action_advance_season(self) -> None:
        saga = self.saga

        async def handle_result(confirmed: bool | None) -> None:
            if not confirmed:
                return
            await self._apply_saga_date(
                *next_season(saga.current_season, saga.current_year)
            )
            self.notify(f"It is now {saga.current_season} {saga.current_year}.")

        self.app.push_screen(
            AdvanceSeasonScreen(saga.current_season, saga.current_year),
            handle_result,
        )

    def action_set_date(self) -> None:
        saga = self.saga

        async def handle_result(result: tuple[str, int] | None) -> None:
            if result is None:
                return
            season, year = result
            if (season, year) == (saga.current_season, saga.current_year):
                return
            await self._apply_saga_date(season, year)
            self.notify(f"Date set to {season} {year}.")

        self.app.push_screen(
            SetDateScreen(saga.current_season, saga.current_year), handle_result
        )

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
            self.selected_covenant = self._covenant_by_id(character.covenant_id)
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
            lab.aura_modifier = result["aura_modifier"]
            lab.covenant_id = result["covenant_id"]
            self.selected_covenant = self._covenant_by_id(lab.covenant_id)
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
            DiaryEntryPromptScreen(
                self.saga.current_year, default_season=self.saga.current_season
            ),
            handle_result,
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

    # -- Laboratory: edit an existing list entry --

    def _edit_lab_entry(
        self,
        *,
        picker_title: str,
        empty_message: str,
        labels: list[str],
        screen_for: Callable[[int], ModalScreen[Any]],
        apply: Callable[[int, Any], None],
        section_id: str,
    ) -> None:
        """Shared two-step flow for editing one entry of a laboratory list:
        pick which entry (same picker as Remove), then edit it in a
        pre-filled dialog built by `screen_for(index)`; `apply(index,
        result)` writes the result back before saving and refreshing."""
        if not labels:
            self.notify(empty_message)
            return

        def handle_index(index: int | None) -> None:
            if index is None:
                return

            def handle_result(result: Any) -> None:
                if result is None:
                    return
                apply(index, result)
                storage.save_saga(self.saga)
                self._refresh_laboratory_section(section_id)

            self.app.push_screen(screen_for(index), handle_result)

        self.app.push_screen(RemovalPickerScreen(picker_title, labels), handle_index)

    def _edit_specialty(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        self._edit_lab_entry(
            picker_title="Edit which Specialty?",
            empty_message="No Specialties to edit.",
            labels=list(lab.specialties),
            screen_for=lambda i: ItemAddScreen(
                "Edit a Specialty", existing=lab.specialties[i]
            ),
            apply=lab.specialties.__setitem__,
            section_id="section-lab-specialties",
        )

    def _edit_feature(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        self._edit_lab_entry(
            picker_title="Edit which Feature?",
            empty_message="No Features to edit.",
            labels=list(lab.features),
            screen_for=lambda i: ItemAddScreen(
                "Edit a Feature", existing=lab.features[i]
            ),
            apply=lab.features.__setitem__,
            section_id="section-lab-features",
        )

    def _edit_room(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        self._edit_lab_entry(
            picker_title="Edit which Room?",
            empty_message="No Rooms to edit.",
            labels=[room.name for room in lab.rooms],
            screen_for=lambda i: NamedDescriptionPromptScreen(
                "Edit a Room", "e.g. Vault", existing=lab.rooms[i]
            ),
            apply=lab.rooms.__setitem__,
            section_id="section-lab-rooms",
        )

    def _edit_inventory_item(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        self._edit_lab_entry(
            picker_title="Edit which Item?",
            empty_message="No Items to edit.",
            labels=[item.name for item in lab.inventory_items],
            screen_for=lambda i: NamedDescriptionPromptScreen(
                "Edit an Item", "e.g. Silver Mirror", existing=lab.inventory_items[i]
            ),
            apply=lab.inventory_items.__setitem__,
            section_id="section-lab-items",
        )

    def _edit_lab_raw_vis(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        arts = sorted(lab.raw_vis)

        def apply(index: int, result: tuple[str, int]) -> None:
            art, pawns = result
            del lab.raw_vis[arts[index]]
            # Re-pointing an entry at an Art that's already held merges the
            # pawns into it, same as adding Raw Vis of a held Art does.
            lab.raw_vis[art] = lab.raw_vis.get(art, 0) + pawns

        self._edit_lab_entry(
            picker_title="Edit which Raw Vis entry?",
            empty_message="No Raw Vis to edit.",
            labels=[f"{art.title()}: {lab.raw_vis[art]} pawn(s)" for art in arts],
            screen_for=lambda i: RawVisPromptScreen(
                existing=(arts[i], lab.raw_vis[arts[i]])
            ),
            apply=apply,
            section_id="section-lab-raw-vis",
        )

    def _edit_diary_entry(self) -> None:
        lab = self.selected_laboratory
        if lab is None:
            return
        self._edit_lab_entry(
            picker_title="Edit which Diary Entry?",
            empty_message="No Diary entries to edit.",
            labels=[f"{e.year} {e.season} -- {e.name}" for e in lab.diary],
            screen_for=lambda i: DiaryEntryPromptScreen(
                self.saga.current_year, existing=lab.diary[i]
            ),
            apply=lab.diary.__setitem__,
            section_id="tab-lab-diary",
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
