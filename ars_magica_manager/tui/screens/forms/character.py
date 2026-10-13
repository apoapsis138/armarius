"""A character's forms: Characteristics and Character Info (their fields
and what saving does are in the core's character_forms.py), and the Arts
editor. A familiar's are in the core's familiar_forms.py."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Label, Static

from .... import character_forms
from .... import sheet_text as st
from ....arts import ART_ABBREVIATIONS, ARTS, FORMS, TECHNIQUES
from ....markup import escape
from ....models import (
    ArtScore,
    Character,
    Saga,
    VirtueFlawInstance,
)
from ....rules import scores
from ....rules import xp as xp_rules
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


class EditArtsScreen(ModalDialog[dict[str, ArtScore] | None]):
    """Edits all 15 Hermetic Arts at once -- a fixed grid, not an addable
    list. Two side-by-side columns (Techniques, Forms), mirroring the sheet's
    own two-column Magical Arts display -- sized to fit every row without a
    scrollbar (Forms, the taller column, is only 10 rows). Each Art's total
    XP is typed, with its score and the total xp the next score needs
    beside it in columns, updated as it changes. Dismisses with a dict of every art's lowercase name ->
    ArtScore, or None if cancelled.
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
        arts: dict[str, ArtScore],
        virtues_flaws: Sequence[VirtueFlawInstance] = (),
        *,
        note: str = "",
    ) -> None:
        """`note`: a line under the subtitle (e.g. how much xp the Creation
        Worksheet gave the Arts)."""
        super().__init__()
        self.arts = arts
        self.note = note
        # the owner's Puissant, for each Art's live score
        self._bonus = {
            art.lower(): scores.art_bonus(virtues_flaws, art)[0] for art in ARTS
        }

    def compose(self) -> ComposeResult:
        def row(art_name: str):
            key = art_name.lower()
            score = self.arts.get(key, ArtScore())
            yield Label(f"{art_name} ({ART_ABBREVIATIONS[art_name]})")
            yield Input(
                value=str(score.xp),
                type="integer",
                id=f"input-art-{key}-xp",
                compact=True,
            )
            yield Label(
                self._score_label(key, score.xp),
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
        if xp is None or xp < 0:
            return "?"
        progress = xp_rules.progress(xp, xp_rules.ART_FACTOR)
        score = st.adjusted_score(progress.score, self._bonus[key])
        return f"{score:<{self._SCORE_WIDTH}}{progress.next_total} xp"

    def on_input_changed(self, event: Input.Changed) -> None:
        """Keep each Art's score and next total beside its XP as the user
        types."""
        input_id = event.input.id or ""
        if not (input_id.startswith("input-art-") and input_id.endswith("-xp")):
            return
        key = input_id.removeprefix("input-art-").removesuffix("-xp")
        try:
            xp: int | None = int(event.value.strip())
        except ValueError:
            xp = None
        self.query_one(f"#art-score-{key}", Label).update(self._score_label(key, xp))

    def _try_save(self) -> None:
        error = self.query_one("#arts-error", Static)
        result: dict[str, ArtScore] = {}
        for art_name in ARTS:
            key = art_name.lower()
            xp_raw = self.query_one(f"#input-art-{key}-xp", Input).value.strip()
            try:
                xp = int(xp_raw)
            except ValueError:
                error.update(f"{art_name} needs a whole number of XP.")
                return
            if xp < 0:
                error.update(f"{art_name}'s XP can't be negative.")
                return
            result[key] = ArtScore(xp=xp)
        self.dismiss(result)
