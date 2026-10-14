"""Print to PDF's options, as the core's command steps (commands.py): the
paper, and for a character's printed sheet whether the Grimoire gives the
spells in full and whether the pages are textured parchment or plain white.

The last choices are kept in the app's settings, so a troupe that prints
on A4 chooses it once.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from . import settings
from .commands import Form
from .form_spec import DialogField
from .print_layout import A4, DEFAULT_OPTIONS, LETTER, PAPER_SIZES, PrintOptions

#: The settings key the last choices are kept under.
PRINT_SETTINGS = "print_options"

PAPER_LABELS = {LETTER: "US Letter", A4: "A4"}
SHORT, FULL = "short", "full"
TEXTURED, WHITE = "textured", "white"


def saved_options() -> PrintOptions:
    """The options chosen last time, or the defaults: anything unknown in
    the settings file falls back to its default."""
    saved = settings.load_settings().get(PRINT_SETTINGS)
    if not isinstance(saved, dict):
        return DEFAULT_OPTIONS
    paper = saved.get("paper")
    return PrintOptions(
        paper=paper if paper in PAPER_SIZES else DEFAULT_OPTIONS.paper,
        full_spells=saved.get("spells") == FULL,
        textured=saved.get("background", TEXTURED) != WHITE,
    )


def print_fields(options: PrintOptions, *, sheet: bool = True) -> list[DialogField]:
    """The paper; with `sheet` (a character's printed sheet) also the
    spells and the background."""
    fields = [
        DialogField(
            "paper",
            "Paper size",
            "select",
            options.paper,
            options=[(PAPER_LABELS[size], size) for size in PAPER_SIZES],
            hint="US Letter, or A4 outside North America.",
        )
    ]
    if sheet:
        fields += [
            DialogField(
                "spells",
                "Spells in the Grimoire",
                "select",
                FULL if options.full_spells else SHORT,
                options=[
                    ("Short: just the parameters", SHORT),
                    ("Full description", FULL),
                ],
            ),
            DialogField(
                "background",
                "Background",
                "select",
                TEXTURED if options.textured else WHITE,
                options=[
                    ("Textured parchment", TEXTURED),
                    ("Plain white, to save ink", WHITE),
                ],
            ),
        ]
    return fields


def options_from(values: dict[str, Any]) -> PrintOptions:
    """The options a filled-in form chose; a field left off keeps its
    default."""
    return PrintOptions(
        paper=values.get("paper") or DEFAULT_OPTIONS.paper,
        full_spells=values.get("spells") == FULL,
        textured=values.get("background", TEXTURED) != WHITE,
    )


def print_form(then: Callable[[PrintOptions], Any], *, sheet: bool = True) -> Form:
    """Print to PDF's options, starting from the last ones chosen, which it
    keeps; `then` gets the options and returns the next step (where to
    save the PDF)."""

    def apply(values: dict[str, Any]) -> Any:
        options = options_from(values)
        kept = {"paper": options.paper}
        if sheet:
            kept |= {
                "spells": FULL if options.full_spells else SHORT,
                "background": TEXTURED if options.textured else WHITE,
            }
        saved = settings.load_settings().get(PRINT_SETTINGS)
        settings.update_settings(
            **{PRINT_SETTINGS: (saved if isinstance(saved, dict) else {}) | kept}
        )
        return then(options)

    return Form(
        "Print to PDF",
        lambda: print_fields(saved_options(), sheet=sheet),
        apply,
        save_label="Next",
        help_id="print-record",
    )
