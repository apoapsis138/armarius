"""Print to PDF's options, as the core's command steps (commands.py): who
the copy is for, the paper, for a character's printed sheet a play sheet
or the full record and whether the Grimoire gives the spells in full, and
whether the pages are textured parchment or plain white.

The last choices are kept in the app's settings, so a troupe that prints
on A4 chooses it once. The copy is not kept: it starts at the Player copy
each time, so nothing secret goes out by accident, and only someone who
reads everything is asked at all (print_layout.reader_for).
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from .. import settings, storage, viewing
from ..commands import ChooseFile, Form
from ..form_spec import DialogField
from ..markup import escape
from ..models import Saga
from ..print_layout import (
    A4,
    DEFAULT_OPTIONS,
    FULL_RECORD,
    HOUSE_COLOURS,
    LETTER,
    PAPER_SIZES,
    PLAY_SHEET,
    PLAYER_COPY,
    SHEETS,
    STORYGUIDE_COPY,
    PrintOptions,
)
from ..print_records import THEME_NAMES, file_stem

#: The settings key the last choices are kept under.
PRINT_SETTINGS = "print_options"

PAPER_LABELS = {LETTER: "US Letter", A4: "A4"}
TEXTURED, WHITE = "textured", "white"


def offers_copy(saga: Saga | None, viewer: viewing.Viewer | None = None) -> bool:
    """Whether the print options ask who the copy is for: only when the
    viewer (by default whoever is looking) reads all of `saga`, the host
    or a Storyguide-role player. Anyone else gets the Player copy."""
    looking = viewer or viewing.current()
    return saga is not None and viewing.reads_everything(looking, saga)


def saved_options() -> PrintOptions:
    """The options chosen last time, or the defaults: anything unknown in
    the settings file falls back to its default. The copy is always the
    Player copy."""
    saved = settings.load_settings().get(PRINT_SETTINGS)
    if not isinstance(saved, dict):
        return DEFAULT_OPTIONS
    paper = saved.get("paper")
    sheet = saved.get("sheet")
    return PrintOptions(
        paper=paper if paper in PAPER_SIZES else DEFAULT_OPTIONS.paper,
        textured=saved.get("background", TEXTURED) != WHITE,
        sheet=sheet if sheet in SHEETS else DEFAULT_OPTIONS.sheet,
        theme=_theme(saved.get("theme")),
    )


def print_fields(
    options: PrintOptions, *, character: bool = True, asks_copy: bool = False
) -> list[DialogField]:
    """With `asks_copy`, who the copy is for; for a `character` the sheet;
    the paper, the theme and the background."""
    fields: list[DialogField] = []
    if asks_copy:
        fields.append(
            DialogField(
                "copy",
                "Copy",
                "select",
                options.copy,
                options=[
                    ("Player copy: what the players may read", PLAYER_COPY),
                    ("Storyguide copy: everything, Secrets too", STORYGUIDE_COPY),
                ],
                hint="A Player copy leaves off unrevealed Secrets.",
            )
        )
    if character:
        fields.append(
            DialogField(
                "sheet",
                "Sheet",
                "select",
                options.sheet,
                options=[
                    ("Play sheet: a page or two to play from", PLAY_SHEET),
                    ("Full record: everything, story and all", FULL_RECORD),
                ],
            )
        )
    fields.append(
        DialogField(
            "paper",
            "Paper size",
            "select",
            options.paper,
            options=[(PAPER_LABELS[size], size) for size in PAPER_SIZES],
            hint="US Letter, or A4 outside North America.",
        )
    )
    fields += [
        DialogField(
            "theme",
            "Theme",
            "select",
            options.theme,
            options=[
                ("Each in its House's colours", HOUSE_COLOURS),
                *((name, name) for name in THEME_NAMES),
            ],
            hint="House colours: a magus, their lab and familiar in their "
            "House's theme; anything else in Scriptorum.",
        ),
        DialogField(
            "background",
            "Background",
            "select",
            TEXTURED if options.textured else WHITE,
            options=[
                ("The theme's paper (a dark one takes a lot of ink)", TEXTURED),
                ("Plain white, to save ink", WHITE),
            ],
            hint="On plain white a dark theme prints in light colours.",
        ),
    ]
    return fields


def options_from(values: dict[str, Any], *, asks_copy: bool = False) -> PrintOptions:
    """The options a filled-in form chose; a field left off keeps its
    default. A Storyguide copy only when the form asked."""
    sheet = values.get("sheet")
    return PrintOptions(
        paper=values.get("paper") or DEFAULT_OPTIONS.paper,
        textured=values.get("background", TEXTURED) != WHITE,
        copy=STORYGUIDE_COPY
        if asks_copy and values.get("copy") == STORYGUIDE_COPY
        else PLAYER_COPY,
        sheet=sheet if sheet in SHEETS else DEFAULT_OPTIONS.sheet,
        theme=_theme(values.get("theme")),
    )


def _theme(value: object) -> str:
    """A theme choice as saved or chosen; the default for anything else."""
    return next(
        (name for name in (HOUSE_COLOURS, *THEME_NAMES) if value == name),
        DEFAULT_OPTIONS.theme,
    )


def _kept_paper(paper: str) -> None:
    """Keep `paper` as the paper chosen last, with the other choices."""
    saved = settings.load_settings().get(PRINT_SETTINGS)
    kept = (saved if isinstance(saved, dict) else {}) | {"paper": paper}
    settings.update_settings(**{PRINT_SETTINGS: kept})


def handout_pdf_form(title: str, draw: Callable[[PrintOptions, Path], int]) -> Form:
    """Save a Handout a player holds as a PDF: only the paper (kept with
    the other print choices; the Stationery or the copy sets the rest),
    then where to save it; `draw` prints it there and says how many
    pages it took."""
    folder = storage.exports_dir()

    def where(values: dict[str, Any]) -> ChooseFile:
        paper = values.get("paper")
        options = PrintOptions(paper=paper if paper in PAPER_SIZES else LETTER)
        _kept_paper(options.paper)

        def save(path: Path) -> list[str]:
            folder.mkdir(parents=True, exist_ok=True)
            pages = draw(options, path)
            return [f"{pages} page{'s' if pages != 1 else ''} saved to {path}."]

        return ChooseFile(
            f"Save {escape(title)} as PDF",
            ".pdf",
            folder / f"{file_stem(title)}.pdf",
            save,
            save=True,
        )

    return Form(
        "Save as PDF",
        lambda: [
            field
            for field in print_fields(saved_options(), character=False)
            if field.key == "paper"
        ],
        where,
        save_label="Next",
        help_id="handouts",
    )


def print_form(
    then: Callable[[PrintOptions], Any],
    *,
    character: bool = True,
    asks_copy: bool = False,
) -> Form:
    """Print to PDF's options, starting from the last ones chosen, which it
    keeps (all but the copy); `then` gets the options and returns the next
    step (where to save the PDF). `asks_copy`: offers_copy's answer."""

    def apply(values: dict[str, Any]) -> Any:
        options = options_from(values, asks_copy=asks_copy)
        kept: dict[str, Any] = {"paper": options.paper}
        if character:
            kept["sheet"] = options.sheet
        kept["background"] = TEXTURED if options.textured else WHITE
        kept["theme"] = options.theme
        saved = settings.load_settings().get(PRINT_SETTINGS)
        settings.update_settings(
            **{PRINT_SETTINGS: (saved if isinstance(saved, dict) else {}) | kept}
        )
        return then(options)

    return Form(
        "Print to PDF",
        lambda: print_fields(saved_options(), character=character, asks_copy=asks_copy),
        apply,
        save_label="Next",
        help_id="print-record",
    )
