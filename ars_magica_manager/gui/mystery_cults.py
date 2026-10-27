"""The desktop Saga Content page's Mystery Cults chapter: the saga's own
cults, the chosen cult's facts and what it is, its degrees and the chosen
degree's Script, each a ledger of entries ruled off on the page, with the
chosen entry in the inspector and each section's Add, Edit and Delete (and
the degrees' Experiment on a Script).

What it says and what its buttons do are forms/mystery_cults.py's, as on
the terminal's Mystery Cults tab.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QMouseEvent, QPainter, QPaintEvent
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from .. import artwork
from ..forms import mystery_cults as cf
from ..models import Saga
from ..references import Fact
from .character_sheet import TextBlock, section
from .editing import Chooser, Run, verb_buttons
from .figures import fact_grid, prose
from .markup_html import plain
from .ornaments import ledger_entry
from .themes import Palette
from .widgets import Symbol, badge, scrolling_page, serif, text

Inspect = Callable[[str, str, str, Symbol], None]


@dataclass
class CultChoice:
    """The cult and degree chosen on the chapter: kept while the saga is
    open, as the page is drawn again after every change."""

    cult: int | None = None
    degree: int | None = None


#: Each open saga's choice, by its id.
_CHOICES: dict[str, CultChoice] = {}


def choice_of(saga: Saga) -> CultChoice:
    return _CHOICES.setdefault(saga.id, CultChoice())


class LedgerRow(QWidget):
    """One entry ruled off on the page: the margin's mark, a heading, an
    italic line, a badge, its words and a note."""

    def __init__(self, entry: cf.EntryText, p: Palette) -> None:
        super().__init__()
        self.p = p
        self.chosen = False
        self.clicked: Callable[[], None] = lambda: None
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        row = QHBoxLayout(self)
        row.setContentsMargins(16, 8, 10, 10)
        row.setSpacing(12)
        mark = text(entry.rubric, p["heading"], serif(18, bold=True))
        mark.setFixedWidth(40)
        mark.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        row.addWidget(mark, 0, Qt.AlignmentFlag.AlignTop)
        column = QVBoxLayout()
        column.setSpacing(3)
        top = QHBoxLayout()
        top.setSpacing(8)
        top.addWidget(
            text(entry.title, p["heading"], serif(12.5, bold=True, caps=True))
        )
        if entry.meta:
            top.addWidget(text(entry.meta, p["label"], serif(11, italic=True)))
        top.addStretch(1)
        if entry.badge:
            top.addWidget(badge(entry.badge, p["text-success"], p))
        column.addLayout(top)
        if entry.body:
            words = TextBlock(entry.body, p)
            words.setFont(serif(13))
            column.addWidget(words)
        if entry.note:
            note = TextBlock(entry.note, p)
            note.setFont(serif(11.5))
            column.addWidget(note)
        row.addLayout(column, 1)

    def set_chosen(self, chosen: bool) -> None:
        self.chosen = chosen
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.clicked()
        super().mousePressEvent(event)

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        ledger_entry(
            painter,
            QRectF(self.rect()).adjusted(12, 0, 0, 0),
            self.p,
            marked=self.chosen,
        )
        painter.end()


def _below_title(entry: cf.EntryText) -> str:
    """The details under the inspector's own title: their first line left
    out when it only names the entry again."""
    first, _, rest = entry.info.partition("\n")
    return rest.strip() if plain(entry.title) in plain(first) else entry.info


def _ledger(
    entries: Sequence[cf.EntryText],
    p: Palette,
    chooser: Chooser,
    chosen: Callable[[int], None],
    inspect: Inspect,
    symbol: Symbol = None,
) -> tuple[QWidget, list[LedgerRow]]:
    """The entries one under another; clicking one chooses it and shows it
    in the inspector, and the chosen one is bracketed."""
    body = QWidget()
    stack = QVBoxLayout(body)
    stack.setContentsMargins(0, 0, 0, 0)
    stack.setSpacing(2)
    rows = [LedgerRow(e, p) for e in entries]
    for index, (row, entry) in enumerate(zip(rows, entries, strict=True)):

        def clicked(index: int = index, entry: cf.EntryText = entry) -> None:
            chooser.choose(index)
            chosen(index)
            inspect(entry.title, entry.subtitle, _below_title(entry), symbol)

        row.clicked = clicked
        stack.addWidget(row)

    def mark(index: int | None) -> None:
        for n, row in enumerate(rows):
            row.set_chosen(n == index)

    chooser.listeners.append(mark)
    return body, rows


def _none(words: str, p: Palette) -> QWidget:
    return text(words, p["dim"], serif(12.5, italic=True))


class CultsChapter(QWidget):
    """The chapter, drawn again in place when a cult or a degree is
    chosen (what the sections below show follows it)."""

    def __init__(self, saga: Saga, p: Palette, run: Run, inspect: Inspect) -> None:
        super().__init__()
        self.saga, self.p, self.run, self.inspect = saga, p, run, inspect
        self.choice = choice_of(saga)
        self.column = QVBoxLayout(self)
        self.column.setContentsMargins(0, 0, 0, 0)
        self.page: QWidget | None = None
        self.draw()

    def chosen_cult(self) -> int | None:
        return self.choice.cult

    def chosen_degree(self) -> int | None:
        return self.choice.degree

    def draw(self) -> None:
        """Lay the chapter out again from the saga and the choice."""
        if self.page is not None:
            self.column.removeWidget(self.page)
            self.page.hide()
            self.page.setParent(None)
            self.page.deleteLater()
        self.page = scrolling_page(
            self.p, self._cults(), self._cult(), self._degrees(), self._script()
        )
        self.column.addWidget(self.page)

    def _choose_cult(self, index: int) -> None:
        if index != self.choice.cult:
            self.choice.cult, self.choice.degree = index, None
            self.draw()

    def _choose_degree(self, index: int) -> None:
        if index != self.choice.degree:
            self.choice.degree = index
            self.draw()

    def _cults(self) -> QWidget:
        p, saga = self.p, self.saga
        chooser = Chooser()
        entries = [
            cf.EntryText(
                rubric=str(n + 1),
                title=cult.name,
                meta=f"{cult.realm}  ·  {cult.lore}",
                badge=f"{len(cult.degrees)} degrees",
                body=f"Founded {cf.founded_words(saga, cult)}",
                note="",
                subtitle=f"{cult.realm} Mystery Cult",
                info=cf.cult_info(saga, cult),
            )
            for n, cult in enumerate(saga.custom_cults)
        ]
        body, _ = _ledger(
            entries,
            p,
            chooser,
            self._choose_cult,
            self.inspect,
            artwork.SAGA_CULT_SYMBOL,
        )
        if self.choice.cult is not None:
            chooser.choose(self.choice.cult)
        return section(
            cf.cults_title(saga),
            p,
            body
            if entries
            else _none("None yet: Add one. Its founders start with its Lore at 0.", p),
            buttons=verb_buttons(cf.cults_ops(saga), chooser, self.run, p),
        )

    def _cult(self) -> QWidget:
        p, saga = self.p, self.saga
        found = cf.chosen_cult(saga, self.chosen_cult)
        if found is None:
            return _none("Add a cult to see its degrees and Scripts.", p)
        facts = [Fact(label, value) for label, value in cf.cult_facts(saga, found)]
        note = TextBlock(cf.cult_note(saga, found), p)
        note.setFont(serif(12.5))
        return section(
            found.name,
            p,
            fact_grid(facts, p, 3),
            prose(found.description.strip(), p),
            note,
            edits={"Edit Cult": lambda: self.run(cf.cult_form(saga, found))},
        )

    def _degrees(self) -> QWidget:
        p, saga = self.p, self.saga
        chooser = Chooser()
        entries = cf.degree_entries(saga, self.chosen_cult)
        body, _ = _ledger(entries, p, chooser, self._choose_degree, self.inspect)
        if self.choice.degree is not None:
            chooser.choose(self.choice.degree)
        more = [
            (
                "Experiment on a Script",
                "secrets",
                lambda row: cf.experiment_form(saga, self.chosen_cult, row),
                lambda row: cf.offers_experiment(saga, self.chosen_cult, row),
            )
        ]
        return section(
            cf.degrees_title(saga, self.chosen_cult),
            p,
            body
            if entries
            else _none("No degree yet: Add one, each teaching a Mystery Virtue.", p),
            buttons=verb_buttons(
                cf.degree_ops(saga, self.chosen_cult),
                chooser,
                self.run,
                p,
                more=more,
            ),
        )

    def _script(self) -> QWidget:
        p, saga = self.p, self.saga
        chooser = Chooser()
        entries = cf.component_entries(saga, self.chosen_cult, self.chosen_degree)
        body, _ = _ledger(entries, p, chooser, lambda _index: None, self.inspect)
        rows = cf.script_rows(saga, self.chosen_cult, self.chosen_degree)
        empty = TextBlock(rows[0][1], p) if not entries and rows else None
        return section(
            cf.script_title(saga, self.chosen_cult, self.chosen_degree),
            p,
            body if entries or empty is None else empty,
            buttons=verb_buttons(
                cf.script_ops(saga, self.chosen_cult, self.chosen_degree),
                chooser,
                self.run,
                p,
            ),
        )
