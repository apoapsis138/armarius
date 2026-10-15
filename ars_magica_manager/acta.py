"""The Acta: a meeting's acts as a charter, built a part at a time
(Builder) from what the meeting decided: its heading, who attended, each
ruling with its fine, the offices filled, and the witnesses. The text is
written into the Tribunal's Diary when the meeting closes, where it can
be reworded like any entry, and the desktop prints it to PDF."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from . import print_layout as pl
from . import storage
from .commands import ChooseFile, Command, Refuse
from .models import Tribunal, TribunalDiaryEntry

#: The Diary entry's title starts with this, so an Acta can be told from
#: the minutes.
TITLE = "Acta of the"


@dataclass
class ActaBuilder:
    """Builds the Acta's paragraphs, in the order a charter sets them
    out; `text` joins them."""

    parts: list[str] = field(default_factory=list)

    def heading(self, tribunal: str, place: str, season: str, year: int) -> ActaBuilder:
        held = f" at {place}" if place else ""
        self.parts.append(
            f"The {tribunal}, gathered{held} in the {season} of the year "
            f"{year}, under the Code of Hermes and its own Peripheral Code, "
            "set down these acts."
        )
        return self

    def attendance(self, present: list[str], votes: str) -> ActaBuilder:
        if present:
            names = ", ".join(present[:-1]) + " and " if len(present) > 1 else ""
            self.parts.append(f"Present: {names}{present[-1]}, with {votes}.")
        return self

    def ruling(
        self, case: str, words: str, fine: str = "", payer: str = ""
    ) -> ActaBuilder:
        line = f"In the matter of {case}, the Tribunal ruled: {words}".rstrip(".")
        if fine:
            line += f"; {payer or 'the party found against'} is to pay a fine of {fine}"
        self.parts.append(line + ".")
        return self

    def office(self, office: str, holder: str, term: str = "") -> ActaBuilder:
        until = f", until {term}" if term else ""
        self.parts.append(f"{holder} was chosen {office}{until}.")
        return self

    def witnesses(self, names: list[str]) -> ActaBuilder:
        if names:
            self.parts.append(f"Witnessed by {' and '.join(names)}.")
        return self

    def text(self) -> str:
        return "\n\n".join(self.parts)


def title(tribunal: str, season: str, year: int) -> str:
    """ "Acta of the Rhine Tribunal, Summer 1228"."""
    return f"{TITLE} {tribunal}, {season} {year}"


def is_acta(entry_title: str) -> bool:
    return entry_title.startswith(TITLE)


def document(entry: TribunalDiaryEntry, tribunal: str) -> pl.Document:
    """The Acta laid out for paper: its title, then each paragraph."""
    paragraphs = [p.strip() for p in entry.details.split("\n\n") if p.strip()]
    return pl.Document(
        entry.title,
        tribunal,
        # The title face is large: "Acta" heads the page, and the rest of
        # the entry's title goes under it.
        [
            pl.Title("Acta", entry.title.removeprefix("Acta of the ")),
            *(pl.Paragraph(p) for p in paragraphs),
        ],
    )


#: Prints a Document to the PDF at a path; how many pages it took. The
#: desktop's own (gui.print_sheet.print_document).
Printer = Callable[[pl.Document, Path], int]


def print_entry(
    tribunal: Tribunal, title: str, entry: TribunalDiaryEntry, printer: Printer
) -> Command:
    """Print the Acta `entry` to a PDF chosen where to save."""
    if not is_acta(entry.title):
        return Refuse(
            "Print", "Only an Acta prints; the minutes are read in the Diary."
        )
    folder = storage.EXPORTS_DIR
    stem = re.sub(r'[\\/:*?"<>|]', "", entry.title).strip() or "Acta"

    def save(path: Path) -> list[str]:
        folder.mkdir(parents=True, exist_ok=True)
        pages = printer(document(entry, title), path)
        return [f"{pages} page{'s' if pages != 1 else ''} saved to {path}."]

    return ChooseFile(
        f"Print {entry.title} to PDF", ".pdf", folder / f"{stem}.pdf", save, save=True
    )
