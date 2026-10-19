"""A character's forms: Characteristics and Character Info (their fields
and what saving does are in the core's character_forms.py), and the Arts
grid (the core's Edit Arts form, drawn two columns wide). A familiar's are in the core's familiar_forms.py."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Label, Static

from .... import form_spec
from ....arts import FORMS, TECHNIQUES
from ....commands import Form
from ....form_spec import DialogField
from ....forms import character as character_forms
from ....markup import escape
from ....models import (
    Character,
    Saga,
    VirtueFlawInstance,
)
from ..fields import FieldsDialog, ModalDialog


def _characteristics_dialog(
    saga: Saga, character: Character
) -> FieldsDialog[dict[str, Any]]:
    """Edit Characteristics. While the character is In Creation the form
    shows the points spent and left as each score is typed."""
    return FieldsDialog(
        "Edit Characteristics",
        character_forms.characteristics_fields(character.characteristics),
        live=character_forms.characteristics_live(saga, character),
    )


_characteristics_from = character_forms.characteristics_from


def _character_info_dialog(saga: Saga, character: Character) -> FieldsDialog:
    """Edit Character Info, warning (not refusing) as the True Faith Score
    is typed if the character can't have it (faith.faith_warnings)."""
    return FieldsDialog(
        "Edit Character Info",
        character_forms.character_info_fields(saga, character),
        live=character_forms.character_info_live(character),
    )


class EditArtsScreen(ModalDialog[dict[str, Any] | None]):
    """The core's Edit Arts form (character_forms.arts_form) drawn as a
    fixed grid of all 15 Hermetic Arts at once, rather than a FieldsDialog's
    one field a row. Two side-by-side columns (Techniques, Forms), mirroring
    the sheet's own two-column Magical Arts display -- sized to fit every
    row without a scrollbar (Forms, the taller column, is only 10 rows).
    Each Art's total XP is typed, with its score and the total xp the next
    score needs beside it in columns, updated as it changes. Dismisses with
    the form's values (for its apply), or None if cancelled.
    """

    DEFAULT_CSS = """
    EditArtsScreen {
        align: center middle;
    }

    #arts-dialog {
        width: auto;
        height: auto;
        max-height: 100%;
        padding: 1 2;
    }

    #arts-subtitle {
        color: $text-muted;
        margin-bottom: 1;
    }

    #arts-note {
        width: 80;
        margin-bottom: 1;
    }

    #arts-columns {
        width: auto;
        height: auto;
    }

    #arts-techniques-col {
        width: auto;
        height: auto;
        margin-right: 3;
    }

    #arts-forms-col {
        width: auto;
        height: auto;
    }

    .column-heading {
        text-style: bold;
    }

    /* a column's heading names the Arts' column, then the others */
    .art-head-row {
        margin-bottom: 1;
    }

    .art-row {
        width: auto;
        height: auto;
    }

    .art-row Label {
        width: 16;
        content-align: right middle;
        padding-right: 1;
    }

    /* "20 (23)  231 xp": the score, then the next score's total */
    .art-row .art-score {
        width: 18;
        content-align: left middle;
        padding-left: 1;
        color: $text-muted;
    }

    .art-row .art-head-xp {
        width: 7;
        content-align: left middle;
        padding-right: 0;
        color: $text-muted;
    }

    /* 3 digits plus the field's padding */
    .art-row Input {
        width: 7;
    }

    #arts-buttons {
        width: auto;
        height: auto;
    }

    #arts-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(
        self,
        form: Form,
        virtues_flaws: Sequence[VirtueFlawInstance] = (),
        *,
        note: str = "",
    ) -> None:
        """`note`: a line under the subtitle (e.g. how much xp the Creation
        Worksheet gave the Arts)."""
        super().__init__()
        self.form = form
        self.fields = {spec.key: spec for spec in form.fields()}
        self.note = note
        # the owner's Puissant, for each Art's live score
        self._bonus = {
            art.lower(): bonus
            for art, bonus in character_forms.art_bonuses(virtues_flaws).items()
        }

    def compose(self) -> ComposeResult:
        def row(art_name: str):
            key = art_name.lower()
            spec = self.fields[f"art_{key}"]
            yield Label(spec.label.removesuffix(" XP"))
            yield Input(
                value=str(spec.value),
                type="integer",
                id=f"input-art-{key}-xp",
                compact=True,
            )
            xp = spec.value if isinstance(spec.value, int) else None
            yield Label(
                self._score_label(key, xp),
                id=f"art-score-{key}",
                classes="art-score",
            )

        def head(title: str):
            with Horizontal(classes="art-row art-head-row"):
                yield Label(title, classes="column-heading")
                yield Label("XP", classes="art-head-xp")
                yield Label(
                    f"{'Score':<{self._SCORE_WIDTH}}Next at", classes="art-score"
                )

        with Vertical(id="arts-dialog", classes="dialog-box"):
            yield Label("Edit Arts", id="arts-title", classes="dialog-title")
            yield Label(
                "Enter each Art's total XP; its score follows", id="arts-subtitle"
            )
            if self.note:
                yield Static(f"[$text-warning]{escape(self.note)}[/]", id="arts-note")
            with Horizontal(id="arts-columns"):
                with Vertical(id="arts-techniques-col"):
                    yield from head("Techniques")
                    for technique in TECHNIQUES:
                        with Horizontal(classes="art-row"):
                            yield from row(technique)
                with Vertical(id="arts-forms-col"):
                    yield from head("Forms")
                    for form in FORMS:
                        with Horizontal(classes="art-row"):
                            yield from row(form)
            yield Static("", id="arts-error")
            with Horizontal(id="arts-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.action_cancel()
        elif event.button.id == "btn-save":
            self._try_save()

    #: The Score column's width, before Next at.
    _SCORE_WIDTH = 9

    def _score_label(self, key: str, xp: int | None) -> str:
        """The Art's score and the total xp the next score needs, "10 (13)
        66 xp" with Puissant, or "?" while the XP isn't a number."""
        found = character_forms.art_score(xp, self._bonus[key])
        if found is None:
            return "?"
        shown, next_total = found
        return f"{shown:<{self._SCORE_WIDTH}}{next_total} xp"

    def on_input_changed(self, event: Input.Changed) -> None:
        """Keep each Art's score and next total beside its XP as the user
        types."""
        input_id = event.input.id or ""
        if not (input_id.startswith("input-art-") and input_id.endswith("-xp")):
            return
        key = input_id.removeprefix("input-art-").removesuffix("-xp")
        xp = form_spec.lenient(self.fields[f"art_{key}"], event.value.strip())
        self.query_one(f"#art-score-{key}", Label).update(self._score_label(key, xp))

    def _read(self, spec: DialogField) -> str:
        key = spec.key.removeprefix("art_")
        return self.query_one(f"#input-art-{key}-xp", Input).value.strip()

    def _try_save(self) -> None:
        error = self.query_one("#arts-error", Static)
        try:
            values = form_spec.result(self.fields.values(), self._read)
        except form_spec.FieldError as problem:
            error.update(escape(str(problem)))
            return
        refused = self.form.validate(values) if self.form.validate else None
        if refused:
            error.update(escape(refused))
            return
        self.dismiss(values)
