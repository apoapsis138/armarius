"""Small prompts: confirmation, advancing the season, the list sub-dialog a
form field can open, and the short FieldsDialog forms the pickers and lists
open."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import replace
from pathlib import Path
from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.widgets import (
    Button,
    Label,
    OptionList,
    Static,
)
from textual.widgets.option_list import Option

from ... import hosted_signin, transfer
from ... import house_rules as hr
from ... import lab_texts as lt
from ... import players as pl
from ... import saga_content as sc
from ...arts import FORMS, TECHNIQUES
from ...commands import Form, Picked
from ...form_spec import DialogField, pairs
from ...forms import ability as ability_forms
from ...forms import diary as diary_forms
from ...forms import laboratory as laboratory_forms
from ...forms import menu as menu_forms
from ...forms import saga_content as scf
from ...forms import trait as trait_forms
from ...forms import virtue as virtue_forms
from ...forms import vis as vis_forms
from ...forms.ability import ability_fields as _ability_fields
from ...forms.ability import ability_problem as _ability_problem
from ...forms.advance import AdvanceText
from ...markup import escape, todo
from ...models import (
    LAB_ACTIVITIES,
    LAB_TEXT_KINDS,
    SEASONS,
    Ability,
    ArcaneConnection,
    Book,
    Character,
    Covenant,
    CovenantDiaryEntry,
    DiaryEntry,
    Laboratory,
    LabSpecialtyEntry,
    LabVirtueFlawDef,
    NamedDescription,
    Player,
    Saga,
    SagaSource,
    ScoredTrait,
    VirtueFlawInstance,
)
from .fields import ConfirmScreen, FieldsDialog, ModalDialog
from .widgets import SelectableList

#: In the core now; the terminal's pickers and lists still import them here.
_ability_from = ability_forms.ability_from
param_choices = virtue_forms.param_choices


def _date_fields(season: str, year: int) -> list[DialogField]:
    """Set the saga's date."""
    return [
        DialogField("season", "Season", "select", season, options=pairs(SEASONS)),
        DialogField("year", "Year", "int", year),
    ]


def _ability_dialog(
    name: str,
    ability: Ability | None,
    virtues_flaws: Sequence[VirtueFlawInstance] = (),
    *,
    save_label: str = "Save",
    note: str = "",
) -> FieldsDialog[dict[str, Any]]:
    """Add or edit an Ability: its xp, with the score it buys shown live
    (with the owner's Puissant, from `virtues_flaws`), and its Specialty.
    `note` follows the live line (e.g. how much xp the Creation Worksheet
    gave it)."""
    return FieldsDialog(
        escape(name),
        _ability_fields(ability),
        validate=_ability_problem,
        live=ability_forms.ability_live(name, virtues_flaws, note),
        save_label=save_label,
    )


def _param_dialog(
    title: str,
    parameters: list[str],
    choices: dict[str, list[tuple[str, str]]] | None = None,
) -> FieldsDialog[dict[str, str]]:
    """Fill in a catalog entry's {placeholders} ("Affinity with {art}"):
    dismisses with {parameter: value}, values lower-cased. A parameter with
    `choices` is picked from them; the rest are typed."""
    return FieldsDialog(
        title,
        virtue_forms.param_fields(parameters, choices),
        save_label="Confirm",
        build=lambda values: virtue_forms.params_from(parameters, values),
    )


def _lab_choice_dialog(
    entry: LabVirtueFlawDef,
    saga: Saga | None = None,
    lab: Laboratory | None = None,
) -> FieldsDialog[dict[str, str]]:
    """What adding a laboratory Virtue or Flaw asks for: the Specialization
    it grants points to, and for a Servant its grog or Intelligence
    (virtue_forms.lab_param_fields)."""
    return FieldsDialog(
        entry.name,
        virtue_forms.lab_param_fields(saga, lab, entry),
        save_label="Confirm",
        build=lambda values: virtue_forms.lab_params_from(entry, values),
    )


def _lab_specialty_entry_dialog(
    existing: LabSpecialtyEntry | None = None,
) -> FieldsDialog[LabSpecialtyEntry]:
    """Points in a laboratory Specialization from a source the app doesn't
    work out itself (laboratory_forms.specialty_entry_fields)."""
    return FieldsDialog(
        "Add a Specialization source"
        if existing is None
        else "Edit a Specialization source",
        laboratory_forms.specialty_entry_fields(existing),
        save_label="Add" if existing is None else "Save",
        validate=laboratory_forms.specialty_entry_problem,
        build=laboratory_forms.specialty_entry_from,
    )


def _scored_trait_dialog(
    title: str,
    name_placeholder: str,
    existing: ScoredTrait | None = None,
    *,
    min_score: int | None = None,
    max_score: int | None = None,
    include_known: bool = False,
    include_reach: bool = False,
    include_sympathy: bool = False,
) -> FieldsDialog[ScoredTrait]:
    """A Personality Trait or Reputation (trait_forms.scored_trait_fields)."""
    return FieldsDialog(
        title,
        trait_forms.scored_trait_fields(
            name_placeholder,
            existing,
            min_score=min_score,
            max_score=max_score,
            include_known=include_known,
            include_reach=include_reach,
            include_sympathy=include_sympathy,
        ),
        validate=lambda values: trait_forms.score_problem(values, min_score, max_score),
        build=trait_forms.trait_from,
    )


def _raw_vis_dialog(
    existing: tuple[str, int] | None = None,
) -> FieldsDialog[tuple[str, int]]:
    """An Art (stored lower-case) and a number of pawns."""
    return FieldsDialog(
        "Add Raw Vis" if existing is None else "Edit Raw Vis",
        vis_forms.raw_vis_fields(existing),
        save_label="Add" if existing is None else "Save",
        build=vis_forms.raw_vis_from,
    )


def _export_dialog(
    record: transfer.Record, folder: Path
) -> FieldsDialog[tuple[Path, bool]]:
    """Export a covenant, laboratory or character to a file:
    where to write it, and for a covenant whether its laboratories and
    characters go too. Builds (the file, with members?)."""
    kind = transfer.kind_of(record)

    def path_of(values: dict[str, Any]) -> Path:
        name = (values.get("file") or "").strip().strip('"')
        path = Path(name).expanduser()
        if name and not path.name.lower().endswith(".json"):
            path = path.with_name(path.name + transfer.SUFFIX)
        return path

    def problem(values: dict[str, Any]) -> str | None:
        if not (values.get("file") or "").strip():
            return "Give the file to write."
        if path_of(values).is_dir():
            return "That is a folder: add a file name."
        return None

    def live(values: dict[str, Any]) -> str:
        if problem(values):
            return ""
        path = path_of(values)
        if path.exists():
            return todo(f"{escape(path.name)} exists: it will be replaced.")
        return f"[dim]Writes {escape(str(path))}[/]"

    fields = [
        DialogField(
            "_what", "Exporting", "info", f"{transfer.KIND_LABELS[kind]}: {record.name}"
        ),
        DialogField(
            "file",
            "File",
            "text",
            str(folder / transfer.default_file_name(record)),
            hint="What it holds travels with it: a character's familiar, devices, "
            "books and Diary; a laboratory's books and devices. Import it into "
            "another saga with More's Import on that saga.",
        ),
    ]
    if kind == transfer.COVENANT:
        fields.append(
            DialogField(
                "with_members",
                "With its laboratories and characters",
                "check",
                False,
            )
        )
    return FieldsDialog(
        f"Export {escape(record.name)}",
        fields,
        save_label="Export",
        validate=problem,
        live=live,
        build=lambda values: (path_of(values), bool(values.get("with_members"))),
    )


def _player_dialog(saga: Saga, existing: Player | None) -> FieldsDialog[dict[str, Any]]:
    """Add or edit someone who can sign in to the saga from a browser
    (saga_content_forms.player_fields). Builds the values players.add /
    update take."""
    dialog = FieldsDialog(
        scf.player_title(existing),
        scf.player_fields(existing),
        validate=lambda values: scf.player_problem(saga, existing, values),
    )
    dialog.help_id = "tab-content-players"
    return dialog


def _saga_source_dialog(
    saga: Saga, existing: SagaSource | None
) -> FieldsDialog[dict[str, Any]]:
    """Add or edit a source of the saga's own
    (saga_content_forms.source_fields). Builds the values
    saga_content.add_source / update_source take."""
    dialog = FieldsDialog(
        scf.source_title(existing),
        scf.source_fields(existing),
        validate=lambda values: sc.source_problem(saga, values, existing),
    )
    dialog.help_id = "saga-content"
    return dialog


def _catalog_dialog(saga: Saga, key: str) -> FieldsDialog[dict[str, Any]]:
    """Whether the saga's pickers offer a shared catalog at all."""
    dialog = FieldsDialog(scf.catalog_title(key), scf.catalog_fields(saga, key))
    dialog.help_id = "saga-content"
    return dialog


def _hide_entry_dialog(key: str | None) -> FieldsDialog[dict[str, Any]]:
    """Which catalog to hide an entry of (the entry is picked next)."""
    dialog = FieldsDialog(
        "Hide a Catalog Entry", scf.hide_entry_fields(key), save_label="Next"
    )
    dialog.help_id = "saga-content"
    return dialog


def _sign_in_dialog(saga: Saga) -> FieldsDialog[hosted_signin.Outcome]:
    """Who is there: a browser copy of a hosted app asks for a
    player's name and passcode before it opens `saga` (hosted_signin.attempt:
    wrong passcodes wait, a short one is let in once more). Dismisses with
    the outcome of a sign-in that let the player in, or None if cancelled."""
    book = hosted_signin.SignInBook(hosted_signin.book_path(saga.name))
    outcome: list[hosted_signin.Outcome] = []

    def problem(values: dict[str, Any]) -> str | None:
        found = hosted_signin.attempt(
            book, saga, values.get("name") or "", values.get("passcode") or ""
        )
        outcome[:] = [found]
        return found.refused or None

    dialog = FieldsDialog(
        f"Sign in to {escape(saga.name)}",
        [
            DialogField("name", "Name", "text", "", required=True),
            DialogField("passcode", "Passcode", "secret", "", required=True),
        ],
        validate=problem,
        save_label="Sign in",
        build=lambda _values: outcome[0],
    )
    dialog.help_id = "sign-in"
    return dialog


def _new_passcode_dialog(
    saga: Saga, player: Player, *, may_put_off: bool
) -> FieldsDialog[bool]:
    """A player who signed in with a passcode shorter than the rule allows
    chooses a new one (hosted_signin.change_passcode saves it). With
    `may_put_off`, Not Now lets them in this once. Dismisses with True once
    saved, None if put off."""

    def problem(values: dict[str, Any]) -> str | None:
        new = values.get("new") or ""
        if new != (values.get("again") or ""):
            return "The two passcodes differ."
        return hosted_signin.change_passcode(saga, player, new)

    dialog = FieldsDialog(
        "Choose a new passcode",
        [
            DialogField(
                "_why",
                "Why",
                "info",
                f"Your passcode is shorter than {pl.MIN_PASSCODE} characters, "
                "the least a passcode may be. Choose a longer one now."
                + (
                    " Not Now lets you in this once; the next time, the short "
                    "one won't."
                    if may_put_off
                    else ""
                ),
            ),
            DialogField("new", "New passcode", "secret", "", required=True),
            DialogField("again", "Again", "secret", "", required=True),
        ],
        validate=problem,
        save_label="Save",
        build=lambda _values: True,
        cancel_label="Not Now" if may_put_off else "Cancel",
    )
    dialog.help_id = "sign-in"
    return dialog


def _house_rule_dialog(
    saga: Saga, existing: tuple[str, hr.Entry] | None
) -> FieldsDialog[dict[str, Any]]:
    """Add or edit a user-made catalog entry
    (saga_content_forms.house_rule_fields). Builds the values
    house_rules.add / update take (with "kind")."""
    return FieldsDialog(
        scf.house_rule_title(existing),
        scf.house_rule_fields(saga, existing),
        validate=lambda values: scf.house_rule_problem(saga, existing, values),
        live=lambda values: scf.house_rule_live(existing, values),
        build=lambda values: scf.house_rule_values(existing, values),
    )


def _lab_text_access_dialog(
    saga: Saga, character: Character
) -> FieldsDialog[tuple[str, int, str]]:
    """Whose raw Lab Texts a magus reads: an author -- a magus
    of the saga, or a name typed for one outside it --, the level he reads
    them to (0 forgets the author) and how he came to. Choosing an author
    he already reads fills in what is recorded. Builds (the author's key,
    level, how)."""
    magi = lt.author_options(saga, character)
    known = dict(lt.access_rows(saga, character))
    outside = [key for key in known if saga.character(key) is None]

    def recorded(values: dict[str, Any]) -> dict[str, Any]:
        access = character.lab_text_access.get(values.get("author") or "")
        if access is None:
            return {}
        return {"level": access.level, "via": access.via or None}

    def author(values: dict[str, Any]) -> str:
        return values.get("author") or (values.get("name") or "").strip()

    def problem(values: dict[str, Any]) -> str | None:
        if not author(values):
            return "Choose the author, or type the name of one outside the saga."
        if values["level"] < 0:
            return "Level can't be negative."
        return None

    return FieldsDialog(
        f"Lab Texts {escape(character.name)} reads",
        [
            DialogField(
                "_known",
                "Reads now",
                "info",
                "; ".join(known.values()) or "(only his own and general texts)",
            ),
            DialogField(
                "author",
                "Author",
                "select",
                None,
                options=magi,
                allow_blank=True,
                placeholder="(a magus of the saga)",
                fills=recorded,
            ),
            DialogField(
                "name",
                "or an author outside it",
                "text",
                outside[0] if len(outside) == 1 and not magi else "",
                show_if=lambda values: not values.get("author"),
            ),
            DialogField(
                "level",
                "Reads to level",
                "int",
                0,
                hint="0 forgets this author. A text above the level needs more "
                "decoding.",
            ),
            DialogField(
                "via",
                "How",
                "select",
                None,
                options=[("Decoded", "decoded"), ("Taught", "taught")],
                allow_blank=True,
                placeholder="(not recorded)",
            ),
        ],
        validate=problem,
        build=lambda values: (author(values), values["level"], values.get("via") or ""),
    )


def _ritual_again_dialog(
    saga: Saga, magus: Character, lab: Laboratory, text: Book
) -> FieldsDialog[tuple[str, str]]:
    """Perform a Longevity Ritual again from its Lab Text: the
    vis to pay with and whose. Refuses what the rules do (the live line says
    what it will cost and restore). Builds (the Art, whose vis)."""
    problem, live = menu_forms.ritual_again_checks(saga, magus, lab, text)
    return FieldsDialog(
        "Perform the Longevity Ritual again",
        menu_forms.ritual_again_fields(magus, text),
        save_label="Perform",
        validate=problem,
        live=live,
        build=lambda values: (values["vis_art"], values["vis_from"]),
    )


def _lab_text_filter_dialog(current: lt.Filter) -> FieldsDialog[lt.Filter]:
    """Narrow a laboratory's Lab Texts: by kind, Technique,
    Form, a range of levels, and to those its owner can read. Everything
    left blank shows them all. Builds the Filter."""

    def build(values: dict[str, Any]) -> lt.Filter:
        return lt.Filter(
            kind=values.get("kind") or "",
            technique=values.get("technique") or "",
            form=values.get("form") or "",
            min_level=values.get("min_level"),
            max_level=values.get("max_level"),
            readable=bool(values.get("readable")),
        )

    def choice(key: str, label: str, value: str, options: Sequence[str]):
        return DialogField(
            key,
            label,
            "select",
            value or None,
            options=[(option, option) for option in options],
            allow_blank=True,
            placeholder="(any)",
        )

    return FieldsDialog(
        "Filter Lab Texts",
        [
            choice("kind", "Kind", current.kind, LAB_TEXT_KINDS),
            choice("technique", "Technique", current.technique, TECHNIQUES),
            choice("form", "Form", current.form, FORMS),
            DialogField("min_level", "Lowest level", "optint", current.min_level),
            DialogField("max_level", "Highest level", "optint", current.max_level),
            DialogField(
                "readable",
                "Readable only",
                "check",
                current.readable,
                hint="Leaves out raw texts the laboratory's owner hasn't decoded. "
                "Blank everything to show them all.",
            ),
        ],
        save_label="Filter",
        validate=lambda values: lt.filter_problem(build(values)),
        build=build,
    )


def _named_description_dialog(
    title: str, name_placeholder: str, existing: NamedDescription | None = None
) -> FieldsDialog[NamedDescription]:
    """A laboratory Room or Equipment & Stores entry: a name and a
    (multi-line) description."""
    return FieldsDialog(
        title,
        laboratory_forms.named_description_fields(name_placeholder, existing),
        build=laboratory_forms.named_description_from,
    )


def _arcane_connection_dialog(
    title: str, existing: ArcaneConnection | None = None
) -> FieldsDialog[ArcaneConnection]:
    """A laboratory's Arcane Connection (laboratory_forms.connection_fields)."""
    return FieldsDialog(
        title,
        laboratory_forms.connection_fields(existing),
        build=lambda values: laboratory_forms.connection_from(values, existing),
    )


def _diary_entry_dialog(
    default_year: int,
    existing: DiaryEntry | None = None,
    default_season: str = SEASONS[0],
    activities: Sequence[str] = LAB_ACTIVITIES,
) -> FieldsDialog[DiaryEntry]:
    """Add or edit a Diary entry: a laboratory's (`activities` the lab
    activities) or a character's (the seasonal activities)."""
    return FieldsDialog(
        diary_forms.entry_title(existing),
        diary_forms.entry_fields(default_year, existing, default_season, activities),
        build=diary_forms.entry_from,
    )


def _covenant_diary_entry_dialog(
    covenant: Covenant,
    default_year: int,
    existing: CovenantDiaryEntry | None = None,
    default_season: str = SEASONS[0],
    saga: Saga | None = None,
) -> FieldsDialog[CovenantDiaryEntry]:
    """Add or edit a covenant Diary entry (diary_forms.covenant_entry_fields)."""
    return FieldsDialog(
        diary_forms.entry_title(existing),
        diary_forms.covenant_entry_fields(
            covenant, default_year, existing, default_season, saga
        ),
        validate=diary_forms.covenant_entry_problem(covenant, existing),
        build=diary_forms.covenant_entry_from(covenant, existing),
    )


class AdvanceSeasonScreen(ModalDialog[bool]):
    """Confirms advancing the saga's calendar by one season. Dismisses with
    True to advance, False (or via Escape) to leave the date alone."""

    help_id = "advance-season"

    CANCEL_RESULT = False

    DEFAULT_CSS = """
    AdvanceSeasonScreen {
        align: center middle;
    }

    #advance-dialog {
        width: 72;
        height: auto;
        padding: 1 2;
    }

    #advance-note {
        color: $text-muted;
        height: auto;
        margin-top: 1;
    }

    #advance-year-note, #advance-plans {
        height: auto;
        margin-top: 1;
    }

    #advance-buttons {
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, text: AdvanceText) -> None:
        super().__init__()
        #: What advancing will do (advance_forms.advance_text).
        self.text = text

    def compose(self) -> ComposeResult:
        text = self.text
        with Vertical(id="advance-dialog", classes="dialog-box"):
            yield Label("Advance Time", id="advance-title", classes="dialog-title")
            yield Static(text.question, id="advance-message")
            if text.plans:
                yield Static(text.plans, id="advance-plans")
            if text.year_note:
                yield Static(text.year_note, id="advance-year-note")
            yield Static(text.note, id="advance-note")
            with Horizontal(id="advance-buttons"):
                yield Button("Advance", id="btn-advance", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "btn-advance")


class MenuScreen(ModalDialog[str | None]):
    """A short menu of actions (the workspace's More and New):
    each item has its own letter, shown in front of it. Pressing the letter,
    or Enter on the highlighted item, dismisses with that item's key; Escape
    with None. `items` are (letter, key, label); labels are markup. An item
    with no letter is a header over the items after it, not chosen."""

    DEFAULT_CSS = """
    MenuScreen {
        align: center middle;
    }

    #menu-dialog {
        width: auto;
        min-width: 30;
        max-width: 76;
        height: auto;
        padding: 1 2;
    }

    #menu-list {
        width: auto;
        min-width: 24;
        height: auto;
        max-height: 16;
        border: none;
        padding: 0;
        background: transparent;
    }
    """

    def __init__(self, title: str, items: Sequence[tuple[str, str, str]]) -> None:
        super().__init__()
        self.menu_title = title
        self.items = list(items)

    def compose(self) -> ComposeResult:
        with Vertical(id="menu-dialog", classes="dialog-box"):
            yield Label(self.menu_title, id="menu-title", classes="dialog-title")
            yield OptionList(
                *(
                    Option(f"[b]{letter}[/]  {label}", id=key)
                    if letter
                    else Option(f"[dim]{label}[/]", disabled=True)
                    for letter, key, label in self.items
                ),
                id="menu-list",
                compact=True,
            )

    def on_mount(self) -> None:
        self.query_one("#menu-list", OptionList).focus()

    def on_key(self, event: Key) -> None:
        for letter, key, _ in self.items:
            if letter and event.character == letter:
                event.stop()
                self.dismiss(key)
                return

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        event.stop()
        self.dismiss(event.option.id)


class ListFieldScreen[ItemT](ModalDialog[list[ItemT] | None]):
    """A small list edited inside a form (e.g. a device's components): its
    rows, with a to add one, e to edit the chosen row and d to delete it
    (after confirming), each entry through `dialog` (a FieldsDialog for one
    entry; None: a new one). Nothing reaches the record until the form it
    was opened from is saved: Done dismisses with the edited list,
    Escape/Cancel with None."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("a", "add", "Add"),
        Binding("e", "edit", "Edit"),
        Binding("d", "remove", "Delete"),
        Binding("delete", "remove", "Delete", show=False),
    ]

    DEFAULT_CSS = """
    ListFieldScreen {
        align: center middle;
    }

    #list-field-dialog {
        width: 84;
        max-width: 100%;
        height: auto;
        max-height: 100%;
        padding: 1 2;
    }

    #list-field-hint {
        color: $text-muted;
        height: auto;
        margin: 1 0;
    }

    #list-field-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(
        self,
        title: str,
        items: list[ItemT],
        label: Callable[[ItemT], str],
        dialog: Callable[[ItemT | None], FieldsDialog[ItemT]],
        *,
        hint: str = "",
    ) -> None:
        super().__init__()
        self.title_text = title
        self.items = list(items)
        self.label = label
        self.dialog = dialog
        self.hint = hint

    def _rows(self) -> list[tuple[int | None, str]]:
        return [(index, self.label(item)) for index, item in enumerate(self.items)]

    def compose(self) -> ComposeResult:
        with Vertical(id="list-field-dialog", classes="dialog-box"):
            yield Label(self.title_text, id="list-field-title", classes="dialog-title")
            yield SelectableList(self._rows(), id="list-field-list")
            yield Static(
                "a adds, e edits the chosen row, d deletes it."
                + (f" {self.hint}" if self.hint else ""),
                id="list-field-hint",
            )
            with Horizontal(id="list-field-buttons"):
                yield Button("Add", id="btn-add")
                yield Button("Done", id="btn-done", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#list-field-list", SelectableList).focus()

    def _chosen(self) -> int | None:
        index = self.query_one("#list-field-list", SelectableList).selected_data_index
        if index is None and len(self.items) == 1:
            return 0
        return index

    def _refill(self, choose: int | None = None) -> None:
        rows = self.query_one("#list-field-list", SelectableList)
        rows.set_rows(self._rows())
        if choose is not None:
            rows.select_data_index(choose)

    def action_add(self) -> None:
        def handle_result(item: ItemT | None) -> None:
            if item is not None:
                self.items.append(item)
                self._refill(len(self.items) - 1)

        self.app.push_screen(self.dialog(None), handle_result)

    def action_edit(self) -> None:
        index = self._chosen()
        if index is None:
            self.notify("Choose a row to edit first.")
            return

        def handle_result(item: ItemT | None) -> None:
            if item is not None:
                self.items[index] = item
                self._refill(index)

        self.app.push_screen(self.dialog(self.items[index]), handle_result)

    def action_remove(self) -> None:
        index = self._chosen()
        if index is None:
            self.notify("Choose a row to delete first.")
            return

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                del self.items[index]
                self._refill()

        self.app.push_screen(
            ConfirmScreen(f"Delete {self.label(self.items[index])}?"),
            handle_confirmed,
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if event.button.id == "btn-add":
            self.action_add()
        elif event.button.id == "btn-done":
            self.dismiss(list(self.items))
        elif event.button.id == "btn-cancel":
            self.action_cancel()


def _list_display(label: Callable[[Any], str]) -> Callable[[Any], str]:
    """A list field's button text (plain): its entries, or "(none)"."""

    def display(items: list[Any]) -> str:
        if not items:
            return "(none: press to add)"
        return "; ".join(label(item) for item in items)

    return display


def core_form_dialog(form: Form) -> FieldsDialog[Any]:
    """A core Form whose apply hands back a commands.Picked value (a list
    field's entry), as a dialog dismissing with that value."""

    def build(values: dict[str, Any]) -> Any:
        chosen = form.apply(values)
        return chosen.value if isinstance(chosen, Picked) else chosen

    return FieldsDialog(
        form.title,
        form.fields(),
        validate=form.validate,
        live=form.live,
        save_label=form.save_label,
        build=build,
    )


def terminal_fields(fields: list[DialogField]) -> list[DialogField]:
    """Core fields with the terminal's own chooser for each list field
    (one with `items` and no `picker`): a ListFieldScreen whose entries are
    edited through the core's entry forms."""
    return [
        _with_list_screen(spec)
        if spec.items is not None and spec.picker is None
        else spec
        for spec in fields
    ]


def _with_list_screen(spec: DialogField) -> DialogField:
    editor = spec.items
    assert editor is not None

    def dialog(item: Any) -> FieldsDialog[Any]:
        step = editor.entry(item)
        assert isinstance(step, Form)
        return core_form_dialog(step)

    return replace(
        spec,
        picker=lambda current: ListFieldScreen(
            editor.title, current or [], lambda item: escape(editor.row(item)), dialog
        ),
        display=_list_display(editor.row),
    )
