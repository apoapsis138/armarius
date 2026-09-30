"""Small prompts: confirmation, advancing the season, the list sub-dialog a
form field can open, and the short FieldsDialog forms the pickers and lists
open."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Label,
    Static,
)
from textual.widgets.button import ButtonVariant

from .. import catalog
from ..arts import ARTS
from ..markup import escape
from ..models import (
    COVENANT_DIARY_CATEGORIES,
    LAB_ACTIVITIES,
    LAB_SPECIALIZATIONS,
    SEASONS,
    STORY_EVENT,
    STORY_EVENT_STATUSES,
    Ability,
    ArcaneConnection,
    Covenant,
    CovenantDiaryEntry,
    DiaryEntry,
    LabSpecialtyEntry,
    LabVirtueFlawDef,
    MasteryAbility,
    NamedDescription,
    ScoredTrait,
    new_instance_id,
    next_season,
)
from .fields import (
    _EMPHASIS_HINT,
    DialogField,
    FieldsDialog,
    ModalDialog,
    _attr,
    _description_field,
    _pairs,
)
from .widgets import SelectableList


def _date_fields(season: str, year: int) -> list[DialogField]:
    """Set the saga's date."""
    return [
        DialogField("season", "Season", "select", season, options=_pairs(SEASONS)),
        DialogField("year", "Year", "int", year),
    ]


#: What the Ability XP field is: the score is worked out from it.
ABILITY_XP_HINT = (
    "Total XP; the score follows from it. Score 1 = 5, 2 = 15, 3 = 30, "
    "4 = 50, 5 = 75, 6 = 105, 7 = 140, 8 = 180."
)


def _ability_fields(ability: Ability | None) -> list[DialogField]:
    """An Ability's xp and Specialty (its name is the form's title)."""
    return [
        DialogField("xp", "XP", "int", _attr(ability, "xp", 0), hint=ABILITY_XP_HINT),
        DialogField(
            "specialty",
            "Specialty",
            "text",
            _attr(ability, "specialty", None) or "",
            placeholder="e.g. Swords",
        ),
    ]


def _ability_problem(values: dict[str, Any]) -> str | None:
    if values["xp"] < 0:
        return "XP can't be negative."
    return None


def _ability_from(name: str, category: str, values: dict[str, Any]) -> Ability:
    return Ability(
        name=name,
        category=category,
        xp=values["xp"],
        specialty=values["specialty"] or None,
    )


def _boon_hook_fields(
    detail: str = "",
    description: str = "",
    *,
    can_be_unknown: bool = False,
    unknown: bool = False,
) -> list[DialogField]:
    """A covenant Boon's or Hook's own Detail (shown in the list) and
    Description (shown ahead of the rules text); both optional. A Minor
    Hook that may be Unknown also gets an Unknown checkbox."""
    unknown_fields = (
        [
            DialogField(
                "unknown",
                "Unknown",
                "check",
                unknown,
                hint="Only the player who storyguides it knows it; "
                "counts 3 points, as a Major Hook.",
            )
        ]
        if can_be_unknown
        else []
    )
    return unknown_fields + [
        DialogField(
            "detail",
            "Detail",
            "text",
            detail,
            placeholder="e.g. the specific building or resource",
        ),
        DialogField(
            "description", "Description", "area", description, hint=_EMPHASIS_HINT
        ),
    ]


def _param_dialog(title: str, parameters: list[str]) -> FieldsDialog[dict[str, str]]:
    """Fill in a catalog entry's {placeholders} ("Affinity with {art}"):
    dismisses with {parameter: value}, values lower-cased."""
    return FieldsDialog(
        title,
        [
            DialogField(
                param, param.title(), "text", "", required=True, placeholder="e.g. Creo"
            )
            for param in parameters
        ],
        save_label="Confirm",
        build=lambda values: {param: values[param].lower() for param in parameters},
    )


def _lab_choice_dialog(entry: LabVirtueFlawDef) -> FieldsDialog[dict[str, str]]:
    """Choose the Specialization a laboratory Virtue or Flaw grants points
    to, from the ones its catalog entry allows (STORY-817)."""
    return FieldsDialog(
        entry.name,
        [
            DialogField(
                param,
                "Specialization",
                "select",
                None,
                options=_pairs(options),
                required=True,
                allow_blank=True,
                placeholder="(choose one)",
                hint=f"{entry.name} grants its points to the one you choose.",
            )
            for param, options in entry.choices.items()
        ],
        save_label="Confirm",
        build=lambda values: {param: values[param] for param in entry.choices},
    )


def _lab_specialty_entry_dialog(
    existing: LabSpecialtyEntry | None = None,
) -> FieldsDialog[LabSpecialtyEntry]:
    """Points in a laboratory Specialization from a source the app doesn't
    work out itself: which Specialization, how many points (a Flaw's may be
    negative) and where they come from."""
    return FieldsDialog(
        "Add a Specialization source"
        if existing is None
        else "Edit a Specialization source",
        [
            DialogField(
                "specialization",
                "Specialization",
                "select",
                _attr(existing, "specialization", "") or None,
                options=_pairs(LAB_SPECIALIZATIONS),
                required=True,
                allow_blank=True,
                placeholder="(choose an Activity or Art)",
            ),
            DialogField(
                "points",
                "Points",
                "int",
                _attr(existing, "points", 1),
                hint="Negative for a penalty (e.g. Undecorated).",
            ),
            DialogField(
                "source",
                "Source",
                "text",
                _attr(existing, "source", ""),
                placeholder="e.g. Subterranean",
            ),
        ],
        save_label="Add" if existing is None else "Save",
        validate=lambda values: "Points can't be 0." if values["points"] == 0 else None,
        build=lambda values: LabSpecialtyEntry(
            values["specialization"], values["points"], values["source"]
        ),
    )


def _scored_trait_dialog(
    title: str,
    name_placeholder: str,
    existing: ScoredTrait | None = None,
    *,
    min_score: int | None = None,
    max_score: int | None = None,
    include_known: bool = False,
) -> FieldsDialog[ScoredTrait]:
    """A Personality Trait or Reputation: a name and a score, optionally
    bounded (covenant Reputations are -3..+3) and, for a covenant
    Reputation, whether the covenant knows of it (see
    inhabitants.reputation_loyalty_penalty())."""
    bounded = min_score is not None and max_score is not None
    score_label = f"Score ({min_score:+d} to {max_score:+d})" if bounded else "Score"
    fields = [
        DialogField(
            "name",
            "Name",
            "text",
            _attr(existing, "name", ""),
            required=True,
            placeholder=name_placeholder,
        ),
        DialogField("score", score_label, "int", _attr(existing, "score", 0)),
    ]
    if include_known:
        fields.append(
            DialogField(
                "known",
                "Known by the covenant?",
                "check",
                _attr(existing, "known", True),
            )
        )

    def validate(values: dict[str, Any]) -> str | None:
        score = values["score"]
        if (min_score is not None and score < min_score) or (
            max_score is not None and score > max_score
        ):
            return f"Score must be between {score_label[6:-1]}."
        return None

    return FieldsDialog(
        title,
        fields,
        validate=validate,
        build=lambda values: ScoredTrait(
            name=values["name"], score=values["score"], known=values.get("known", True)
        ),
    )


def _mastery_ability_dialog(
    title: str, existing: MasteryAbility | None = None
) -> FieldsDialog[MasteryAbility]:
    return FieldsDialog(
        title,
        [
            DialogField(
                "name",
                "Name",
                "text",
                _attr(existing, "name", ""),
                required=True,
                placeholder="e.g. Fast Casting",
            ),
            DialogField("level", "Level", "int", _attr(existing, "level", 0)),
            DialogField("xp", "XP", "int", _attr(existing, "xp", 0)),
        ],
        build=lambda values: MasteryAbility(**values),
    )


def _raw_vis_dialog(
    existing: tuple[str, int] | None = None,
) -> FieldsDialog[tuple[str, int]]:
    """An Art (stored lower-case) and a number of pawns."""
    return FieldsDialog(
        "Add Raw Vis" if existing is None else "Edit Raw Vis",
        [
            DialogField(
                "art",
                "Art",
                "select",
                existing[0] if existing else None,
                options=[(art, art.lower()) for art in ARTS],
                required=True,
                allow_blank=True,
                placeholder="(choose an Art)",
            ),
            DialogField("pawns", "Pawns", "int", existing[1] if existing else 1),
        ],
        save_label="Add" if existing is None else "Save",
        build=lambda values: (values["art"], values["pawns"]),
    )


def _named_description_dialog(
    title: str, name_placeholder: str, existing: NamedDescription | None = None
) -> FieldsDialog[NamedDescription]:
    """A laboratory Room or Equipment & Stores entry: a name and a
    (multi-line) description."""
    return FieldsDialog(
        title,
        [
            DialogField(
                "name",
                "Name",
                "text",
                _attr(existing, "name", ""),
                required=True,
                placeholder=name_placeholder,
            ),
            _description_field(_attr(existing, "description", "")),
        ],
        build=lambda values: NamedDescription(**values),
    )


def _arcane_connection_dialog(
    title: str, existing: ArcaneConnection | None = None
) -> FieldsDialog[ArcaneConnection]:
    """A laboratory's Arcane Connection: what it connects to, fixed or how
    long it lasts, where it came from, and notes."""

    def build(values: dict[str, Any]) -> ArcaneConnection:
        fixed = bool(values["fixed"])
        return ArcaneConnection(
            id=existing.id if existing else new_instance_id(),
            to=values["to"],
            fixed=fixed,
            lasts="" if fixed else values.get("lasts", ""),
            source=values["source"],
            description=values["description"],
            fixed_year=existing.fixed_year if existing and fixed else None,
            fixed_season=existing.fixed_season if existing and fixed else "",
        )

    return FieldsDialog(
        title,
        [
            DialogField(
                "to",
                "Connection to",
                "text",
                _attr(existing, "to", ""),
                required=True,
                placeholder="e.g. a lock of Banna's hair",
            ),
            DialogField("fixed", "Fixed", "check", _attr(existing, "fixed", False)),
            DialogField(
                "lasts",
                "Lasts",
                "text",
                _attr(existing, "lasts", ""),
                placeholder="e.g. until Summer 1222",
                show_if=lambda v: not v.get("fixed"),
            ),
            DialogField(
                "source",
                "Where from",
                "text",
                _attr(existing, "source", ""),
                placeholder="e.g. taken at the Tribunal",
            ),
            _description_field(_attr(existing, "description", "")),
        ],
        build=build,
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
        "Add a Diary Entry" if existing is None else "Edit a Diary Entry",
        [
            DialogField("year", "Year", "int", _attr(existing, "year", default_year)),
            DialogField(
                "season",
                "Season",
                "select",
                _attr(existing, "season", default_season),
                options=_pairs(SEASONS),
            ),
            DialogField(
                "activity",
                "Activity Type",
                "select",
                _attr(existing, "activity", "") or None,
                options=_pairs(activities),
                allow_blank=True,
            ),
            DialogField(
                "name", "Name", "text", _attr(existing, "name", ""), required=True
            ),
            DialogField(
                "details",
                "Details",
                "area",
                _attr(existing, "details", ""),
                hint=_EMPHASIS_HINT,
            ),
        ],
        build=lambda values: DiaryEntry(
            **{**values, "activity": values["activity"] or ""}
        ),
    )


def _covenant_diary_entry_dialog(
    covenant: Covenant,
    default_year: int,
    existing: CovenantDiaryEntry | None = None,
    default_season: str = SEASONS[0],
) -> FieldsDialog[CovenantDiaryEntry]:
    """Add or edit a covenant Diary entry (STORY-406). The amounts are
    optional; Status, the linked Boon/Hook and Revisit are shown for Story
    Events only (a hidden field is left out, so it falls back to blank)."""
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    boons_hooks = [
        (
            escape(catalog.describe_boon_hook(bh, by_id))
            + f" ({by_id[bh.vf_id].type if bh.vf_id in by_id else 'Boon/Hook'})",
            bh.id,
        )
        for bh in covenant.boons_hooks
        if bh.id
    ]

    def story(values: dict[str, Any]) -> bool:
        return values.get("category") == STORY_EVENT

    def build(values: dict[str, Any]) -> CovenantDiaryEntry:
        values = {**values, "category": values["category"] or ""}
        values["vis_art"] = values.get("vis_art") or ""
        if story(values):
            values["status"] = values.get("status") or STORY_EVENT_STATUSES[0]
        return CovenantDiaryEntry(**values)

    return FieldsDialog(
        "Add a Diary Entry" if existing is None else "Edit a Diary Entry",
        [
            DialogField("year", "Year", "int", _attr(existing, "year", default_year)),
            DialogField(
                "season",
                "Season",
                "select",
                _attr(existing, "season", default_season),
                options=_pairs(SEASONS),
            ),
            DialogField(
                "category",
                "Category",
                "select",
                _attr(existing, "category", "") or None,
                options=_pairs(COVENANT_DIARY_CATEGORIES),
                allow_blank=True,
            ),
            DialogField(
                "name", "Name", "text", _attr(existing, "name", ""), required=True
            ),
            DialogField(
                "status",
                "Status",
                "select",
                _attr(existing, "status", "") or STORY_EVENT_STATUSES[0],
                options=_pairs(STORY_EVENT_STATUSES),
                show_if=story,
            ),
            DialogField(
                "boon_hook_id",
                "Linked Boon/Hook",
                "select",
                _attr(existing, "boon_hook_id", None),
                options=boons_hooks,
                allow_blank=True,
                placeholder="(none)",
                show_if=story,
            ),
            DialogField(
                "revisit_year",
                "Revisit in year",
                "optint",
                _attr(existing, "revisit_year", None),
                show_if=story,
            ),
            DialogField(
                "pounds",
                "Pounds (+ received, - spent)",
                "optfloat",
                _attr(existing, "pounds", None),
            ),
            DialogField(
                "vis_pawns",
                "Vis pawns (+ gained, - spent)",
                "optint",
                _attr(existing, "vis_pawns", None),
            ),
            DialogField(
                "vis_art",
                "Vis Art",
                "select",
                _attr(existing, "vis_art", "") or None,
                options=_pairs(ARTS),
                allow_blank=True,
            ),
            DialogField(
                "loyalty",
                "Loyalty points",
                "optint",
                _attr(existing, "loyalty", None),
                hint="Added into the Loyalty block's Actions and Events.",
            ),
            DialogField(
                "details",
                "Details",
                "area",
                _attr(existing, "details", ""),
                hint=_EMPHASIS_HINT,
            ),
        ],
        build=build,
    )


class AdvanceSeasonScreen(ModalDialog[bool]):
    """Confirms advancing the saga's calendar by one season. Dismisses with
    True to advance, False (or via Escape) to leave the date alone."""

    CANCEL_RESULT = False

    DEFAULT_CSS = """
    AdvanceSeasonScreen {
        align: center middle;
    }

    #advance-dialog {
        width: 72;
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

    def __init__(self, season: str, year: int, plans: str = "") -> None:
        super().__init__()
        self.season = season
        self.year = year
        #: What happens to the season's plans (seasons.advance_summary):
        #: markup, "" for nothing to say.
        self.plans = plans

    def compose(self) -> ComposeResult:
        new_season, new_year = next_season(self.season, self.year)
        with Vertical(id="advance-dialog"):
            yield Label("Advance Time", id="advance-title")
            yield Static(
                f"Advance the saga from {self.season} {self.year} "
                f"to {new_season} {new_year}?",
                id="advance-message",
            )
            if self.plans:
                yield Static(self.plans, id="advance-plans")
            if new_year != self.year:
                yield Static(
                    "A new year: each covenant's surplus is added to its Wealth, "
                    "and Emergency Savings start again at 0.",
                    id="advance-year-note",
                )
            yield Static(
                "Advanced by mistake? Use Set Date (T) to put the date back"
                + (" (Wealth isn't changed back)." if new_year != self.year else ".")
                + (
                    " The saga is backed up first (data/sagas/backups)."
                    if self.plans
                    else ""
                ),
                id="advance-note",
            )
            with Horizontal(id="advance-buttons"):
                yield Button("Advance", id="btn-advance", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "btn-advance")


class ConfirmScreen(ModalScreen[bool]):
    """A Yes/No confirmation, e.g. before deleting something. Dismisses with
    True for Yes, False for No / Escape. No is focused by default so a stray
    Enter can't delete; `y` and `n` answer directly. `message` is shown as
    markup, so escape any user text in it."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("escape", "escape", "Cancel"),
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

    def __init__(
        self,
        message: str,
        *,
        yes_label: str = "Yes",
        yes_variant: ButtonVariant = "error",
        safe_answer: bool = False,
    ) -> None:
        """`safe_answer` is the answer a stray key should give: False (No) for
        the usual "Delete X?"; True when No is the risky choice, which also
        focuses Yes and makes Escape answer Yes."""
        super().__init__()
        self.message = message
        self.yes_label = yes_label
        self.yes_variant: ButtonVariant = yes_variant
        self.safe_answer = safe_answer

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-dialog"):
            yield Static(self.message, id="confirm-message")
            with Horizontal(id="confirm-buttons"):
                yield Button(self.yes_label, id="btn-yes", variant=self.yes_variant)
                yield Button("No", id="btn-no")

    def on_mount(self) -> None:
        self.query_one("#btn-yes" if self.safe_answer else "#btn-no", Button).focus()

    def action_escape(self) -> None:
        self.dismiss(self.safe_answer)

    def action_yes(self) -> None:
        self.dismiss(True)

    def action_no(self) -> None:
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "btn-yes")


class ListFieldScreen[ItemT](ModalDialog[list[ItemT] | None]):
    """A small list edited inside a form (e.g. a device's components): its
    rows, with a to add one, e to edit the chosen row and A to remove it,
    each entry through `dialog` (a FieldsDialog for one entry; None: a new
    one). Nothing reaches the record until the form it was opened from is
    saved: Done dismisses with the edited list, Escape/Cancel with None."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("a", "add", "Add"),
        Binding("e", "edit", "Edit"),
        Binding("A", "remove", "Remove"),
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
        border: round $accent;
        padding: 1 2;
        background: $surface;
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
        with Vertical(id="list-field-dialog"):
            yield Label(self.title_text, id="list-field-title")
            yield SelectableList(self._rows(), id="list-field-list")
            yield Static(
                "a adds, e edits the chosen row, A removes it."
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
            self.notify("Choose a row to remove first.")
            return
        del self.items[index]
        self._refill()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if event.button.id == "btn-add":
            self.action_add()
        elif event.button.id == "btn-done":
            self.dismiss(list(self.items))
        elif event.button.id == "btn-cancel":
            self.action_cancel()
