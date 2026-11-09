"""The Sessions section of the saga page's Saga Management: the evenings
of play, planned soonest first then played newest first, with Add, Edit
and Delete (the core's SectionOps), Cast at a Glance and Print the Cast on
the chosen row, and Previously On beside them."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from PySide6.QtWidgets import QWidget

from .. import cast_sheet, print_layout, section_verbs, storage
from .. import sessions as ss
from ..commands import ChooseFile, Command
from ..forms import printing as print_forms
from ..forms import sessions as session_forms
from ..models import Saga, Session
from ..sections import SESSIONS_SECTION
from ..sheets import saga_content as scs
from . import print_sheet, printing
from .character_sheet import section
from .editing import Chooser, Run, choose_rows, verb_buttons
from .menus import ICONS
from .themes import Palette
from .widgets import cells_table, edit_button, serif, text

Inspect = Callable[[str, str, str], None]

PRINT = ICONS.get("print", "export")


def sessions_section(saga: Saga, p: Palette, run: Run, inspect: Inspect) -> QWidget:
    """The Sessions list and its buttons; choosing a row shows who came
    and who played whom in the inspector."""
    chooser = Chooser()
    shown = ss.in_order(saga)
    table = scs.sessions_table(saga)
    rows = cells_table(
        table.columns,
        table.rows,
        p,
        lambda row: inspect(
            ss.when(shown[row]),
            ss.status(shown[row]),
            ss.detail_text(saga, shown[row]),
        ),
    )
    choose_rows(rows, chooser)
    buttons = verb_buttons(
        section_verbs.ops_of(saga, saga)[SESSIONS_SECTION],
        chooser,
        run,
        p,
        more=[
            (
                "Cast at a Glance",
                "players",
                lambda row: session_forms.cast_glance(saga, shown[row]),
                lambda _row: True,
            ),
            (
                "Print the Cast",
                PRINT,
                lambda row: print_cast(saga, shown[row]),
                lambda row: bool(shown[row].castings),
            ),
        ],
    ) + [
        edit_button(
            "Previously On",
            p,
            lambda: run(session_forms.previously_on(saga)),
            "season",
        ),
        edit_button("Print Previously On", p, lambda: run(print_recap(saga)), PRINT),
    ]
    return section(
        f"Sessions ({len(saga.sessions)})",
        p,
        rows if shown else text("None yet.", p["dim"], serif(12.5, italic=True)),
        buttons=buttons,
    )


def _to_pdf(
    title: str, stem: str, document: Callable[[], print_layout.Document]
) -> Command:
    """The paper first, then where to save the PDF of `document`."""
    folder = storage.exports_dir()

    def where(options: print_layout.PrintOptions) -> ChooseFile:
        def save(path: Path) -> list[str]:
            folder.mkdir(parents=True, exist_ok=True)
            pages = print_sheet.print_document(document(), path, options)
            return [f"{pages} page{'s' if pages != 1 else ''} saved to {path}."]

        return ChooseFile(
            title, ".pdf", folder / f"{printing.file_stem(stem)}.pdf", save, save=True
        )

    return print_forms.print_form(where, sheet=False)


def print_cast(saga: Saga, session: Session) -> Command:
    """The cast at a glance to a PDF, in the Scriptorum style."""
    title = f"{saga.name}: {ss.when(session)}"
    return _to_pdf(
        "Print the Cast to PDF",
        title,
        lambda: print_layout.cast_document(
            saga, title, cast_sheet.session_cast(saga, session.id)
        ),
    )


def print_recap(saga: Saga) -> Command:
    """Previously On to a PDF, as the Player view (to read aloud)."""
    return _to_pdf(
        "Print Previously On to PDF",
        f"{saga.name} previously on",
        lambda: print_layout.recap_document(saga, players=True),
    )
