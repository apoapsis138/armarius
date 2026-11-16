"""Print the Troupe: every player character's sheet in one PDF, each from
a fresh page and in its own theme, with a bookmark for each.

The options are Print to PDF's (forms/printing.py): who the copy is for,
play sheets or full records, the paper, the spells, the theme and the
background. The sheets are print_records.troupe_sheets, drawn one after
another by print_sheet.print_book (a Composite of documents)."""

from __future__ import annotations

from pathlib import Path

from .. import print_layout, print_records, storage
from ..commands import ChooseFile, Command
from ..forms import printing as print_forms
from ..models import Saga
from . import print_sheet


def print_troupe(saga: Saga) -> Command:
    """The options, then where to save the troupe's PDF."""
    folder = storage.exports_dir()
    title = f"{saga.name}: The Troupe"

    def where(options: print_layout.PrintOptions) -> ChooseFile:
        def save(path: Path) -> list[str]:
            sheets = print_records.troupe_sheets(saga, options)
            if not sheets:
                return ["The troupe has no player characters to print."]
            folder.mkdir(parents=True, exist_ok=True)
            starts = print_sheet.print_book(title, sheets, path, options)
            people = f"{len(starts)} character{'s' if len(starts) != 1 else ''}"
            return [f"{people} saved to {path}."]

        return ChooseFile(
            "Print the Troupe to PDF",
            ".pdf",
            folder / f"{print_records.file_stem(title)}.pdf",
            save,
            save=True,
        )

    return print_forms.print_form(
        where, character=True, asks_copy=print_forms.offers_copy(saga)
    )
