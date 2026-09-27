"""Small prompts: confirmation, advancing the season, and the short
FieldsDialog forms the pickers and lists open."""

from __future__ import annotations

from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Label,
    Static,
)

from ..arts import ARTS
from ..models import (
    SEASONS,
    Ability,
    DiaryEntry,
    MasteryAbility,
    NamedDescription,
    ScoredTrait,
    next_season,
)
from .fields import (
    _EMPHASIS_HINT,
    DialogField,
    FieldsDialog,
    ModalDialog,
    _attr,
    _pairs,
)


def _date_fields(season: str, year: int) -> list[DialogField]:
    """Set the saga's date."""
    return [
        DialogField("season", "Season", "select", season, options=_pairs(SEASONS)),
        DialogField("year", "Year", "int", year),
    ]


def _ability_fields(ability: Ability | None) -> list[DialogField]:
    """An Ability's score and Specialty (its name is the form's title)."""
    return [
        DialogField("level", "Level", "int", _attr(ability, "level", 0)),
        DialogField("xp", "XP", "int", _attr(ability, "xp", 0)),
        DialogField(
            "xp_to_next", "XP to next level", "int", _attr(ability, "xp_to_next", 0)
        ),
        DialogField(
            "specialty",
            "Specialty",
            "text",
            _attr(ability, "specialty", None) or "",
            placeholder="e.g. Swords",
        ),
    ]


def _ability_from(name: str, category: str, values: dict[str, Any]) -> Ability:
    return Ability(
        name=name,
        category=category,
        level=values["level"],
        xp=values["xp"],
        xp_to_next=values["xp_to_next"],
        specialty=values["specialty"] or None,
    )


def _boon_hook_fields(detail: str = "", description: str = "") -> list[DialogField]:
    """A covenant Boon's or Hook's own Detail (shown in the list) and
    Description (shown ahead of the rules text); both optional."""
    return [
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


def _item_dialog(
    title: str, label: str, existing: str | None = None
) -> FieldsDialog[str]:
    """One line of text -- a laboratory Specialty or Feature."""
    return FieldsDialog(
        title,
        [DialogField("item", label, "text", existing or "", required=True)],
        save_label="Add" if existing is None else "Save",
        build=lambda values: values["item"],
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
    """A laboratory Room or Inventory item: a name and a description."""
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
            DialogField(
                "description", "Description", "text", _attr(existing, "description", "")
            ),
        ],
        build=lambda values: NamedDescription(**values),
    )


def _diary_entry_dialog(
    default_year: int,
    existing: DiaryEntry | None = None,
    default_season: str = SEASONS[0],
) -> FieldsDialog[DiaryEntry]:
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
                "name", "Name", "text", _attr(existing, "name", ""), required=True
            ),
            DialogField("details", "Details", "text", _attr(existing, "details", "")),
        ],
        build=lambda values: DiaryEntry(**values),
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

    #advance-year-note {
        height: auto;
        margin-top: 1;
    }

    #advance-buttons {
        width: 100%;
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
            if new_year != self.year:
                yield Static(
                    "A new year: each covenant's surplus is added to its Wealth, "
                    "and Emergency Savings start again at 0.",
                    id="advance-year-note",
                )
            yield Static(
                "Advanced by mistake? Use Set Date (T) to put the date back"
                + (" (Wealth isn't changed back)." if new_year != self.year else "."),
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
        yes_variant: str = "error",
        safe_answer: bool = False,
    ) -> None:
        """`safe_answer` is the answer a stray key should give: False (No) for
        the usual "Delete X?"; True when No is the risky choice, which also
        focuses Yes and makes Escape answer Yes."""
        super().__init__()
        self.message = message
        self.yes_label = yes_label
        self.yes_variant = yes_variant
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
