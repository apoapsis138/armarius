"""The desktop Saga Content page, read-only, in the Codex layout: what the
saga's pickers offer. Chapters for the books in play and the saga's own
sources, the shared catalogs and the single entries it hides, its House
Rules, every spell (sorted and filtered as on the terminal) and its
players, with the inspector beside them.

What it says comes from the shared core (saga_content_sheet.py and the
modules behind it), as the terminal's Saga Content view does.
"""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QSize, QSortFilterProxyModel, Qt
from PySide6.QtGui import QIcon, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QSpinBox,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from .. import artwork
from .. import house_rules as hr
from .. import players as pl
from .. import saga_content as sc
from .. import saga_content_sheet as scs
from .. import spells as spl
from ..arts import FORMS, TECHNIQUES
from ..models import Saga
from . import pictures
from .character_sheet import section
from .figures import fact_grid
from .pages import card_grid, page_header
from .themes import Palette
from .widgets import (
    ROW_HEIGHT,
    Card,
    ClickableCard,
    Codex,
    badge,
    cells_table,
    chapter_title,
    chip,
    scrolling_page,
    serif,
    table_style,
    text,
)

CHAPTERS = (
    ("Books", "library"),
    ("Catalogs", "lab_text"),
    ("House Rules", "magic"),
    ("Spells", "enchanted_item"),
    ("Players", "players"),
)

#: The spell table's columns.
SPELL_COLUMNS = ["Spell", "Arts", "Level", "Range/Duration/Target", "Ritual", "Source"]

#: The item-data role the spell table sorts by (a level sorts as a number).
SORT = Qt.ItemDataRole.UserRole + 2

#: A level filter's lowest value, shown as "any".
ANY_LEVEL = -1


def _none(words: str, p: Palette) -> QLabel:
    return text(words, p["dim"], serif(12.5, italic=True))


class SagaContentPage(QWidget):
    """The saga's content in the Codex layout; choosing anything shows it
    in the inspector."""

    def __init__(self, saga: Saga, p: Palette) -> None:
        super().__init__()
        self.saga, self.p = saga, p
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 12, 12, 8)
        outer.setSpacing(10)
        header = page_header(
            "Saga Content",
            f"What {saga.name}'s pickers offer: books, catalogs, House Rules"
            " and spells",
            p,
            "library",
        )
        top = QHBoxLayout()
        top.addWidget(header, 1)
        top.addWidget(fact_grid(scs.header_facts(saga), p, 2))
        outer.addLayout(top)
        self.codex = Codex(p)
        self.inspector = self.codex.inspector
        builders = {
            "Books": self._books,
            "Catalogs": self._catalogs,
            "House Rules": self._house_rules,
            "Spells": self._spells,
            "Players": self._players,
        }
        for name, concept in CHAPTERS:
            if name == "Players" and not saga.players:
                continue
            self.codex.add(name, concept, builders[name]())
        outer.addWidget(self.codex, 1)

    def chapters(self) -> list[str]:
        return self.codex.chapters()

    def inspect(self, title: str, subtitle: str, markup: str, symbol=None) -> None:
        self.codex.inspect(title, subtitle, markup, symbol)

    # Chapters

    def _books(self) -> QWidget:
        """Each book as a card marked in play or not, then the saga's own
        sources."""
        p, saga = self.p, self.saga
        tones = {
            scs.ALWAYS: p["accent"],
            scs.IN_PLAY: p["text-success"],
            scs.OUT_OF_PLAY: p["dim"],
        }
        cards = []
        for book in scs.book_cards(saga):
            card = ClickableCard(p, pad=12, edge=tones[book.state])
            top = QHBoxLayout()
            top.addWidget(badge(book.book, tones[book.state], p))
            top.addStretch(1)
            top.addWidget(chip(book.state, tones[book.state]))
            card.column.addLayout(top)
            card.column.addWidget(
                text(book.title, p["foreground"], serif(13.5, bold=True), wrap=True)
            )
            if book.own:
                card.column.addWidget(
                    text("The saga's own source", p["label"], serif(11, italic=True))
                )
            card.column.addStretch(1)
            card.clicked = lambda book=book: self.inspect(
                book.title, book.book, sc.book_detail(saga, book.book)
            )
            cards.append(card)
        in_play = sum(1 for c in scs.book_cards(saga) if c.state != scs.OUT_OF_PLAY)
        sources = scs.sources_table(saga)
        self.sources = cells_table(
            sources.columns,
            sources.rows,
            p,
            lambda row: self.inspect(
                saga.sources[row].title or saga.sources[row].abbreviation,
                "The saga's own source",
                sc.source_detail(saga, saga.sources[row]),
            ),
        )
        return scrolling_page(
            p,
            chapter_title(f"Books in Play ({in_play} of {len(cards)})", p),
            card_grid(cards, 3),
            section(
                f"Saga Sources ({len(saga.sources)})",
                p,
                self.sources if saga.sources else _none("None yet.", p),
            ),
        )

    def _catalogs(self) -> QWidget:
        p, saga = self.p, self.saga
        keys = list(sc.CATALOGS)
        catalogs = scs.catalogs_table(saga)
        self.catalogs = cells_table(
            catalogs.columns,
            catalogs.rows,
            p,
            lambda row: self.inspect(
                sc.CATALOGS[keys[row]].label,
                "Shared catalog",
                sc.catalog_detail(saga, keys[row]),
            ),
        )
        hidden = sc.hidden_entries(saga)
        table = scs.hidden_table(saga)
        hidden_view = cells_table(
            table.columns,
            table.rows,
            p,
            lambda row: self.inspect(
                hidden[row][1].name,
                sc.CATALOGS[hidden[row][0]].label,
                sc.hidden_detail(hidden[row]),
            ),
        )
        return scrolling_page(
            p,
            section(f"Catalogs ({len(keys)})", p, self.catalogs),
            section(
                f"Hidden Entries ({len(hidden)})",
                p,
                hidden_view if hidden else _none("The saga hides none.", p),
            ),
        )

    def _house_rules(self) -> QWidget:
        """The saga's own Virtues, Flaws, Boons and Hooks as cards, edged
        green when they cost points and red when they give them."""
        p, saga = self.p, self.saga
        entries = hr.all_entries(saga)
        cards = []
        for rule in scs.house_rule_cards(saga):
            colour = p["text-error"] if rule.gives else p["text-success"]
            card = ClickableCard(p, pad=10, edge=colour)
            top = QHBoxLayout()
            top.addWidget(text(rule.name, p["foreground"], serif(13.5, bold=True)))
            top.addStretch(1)
            top.addWidget(
                badge(rule.tier, p["dim"] if rule.tier == "Free" else colour, p)
            )
            card.column.addLayout(top)
            card.column.addWidget(
                text(f"{rule.kind} {rule.type}  ·  {rule.points}", p["label"])
            )
            card.column.addWidget(text(rule.category, p["dim"], serif(10, caps=True)))
            card.clicked = lambda rule=rule: self.inspect(
                rule.name,
                f"{rule.kind} {rule.type}  ·  {rule.tier}",
                hr.detail_text(saga, entries[rule.index]),
            )
            cards.append(card)
        return scrolling_page(
            p,
            chapter_title(f"House Rules ({len(cards)})", p),
            card_grid(cards, 2) if cards else _none("None yet.", p),
        )

    def _spells(self) -> QWidget:
        """Every spell the saga knows of in a table that sorts by any column,
        under the terminal's filters: words, source, Technique, Form, ritual
        and a range of levels."""
        p = self.p
        box = QWidget()
        column = QVBoxLayout(box)
        column.setContentsMargins(18, 4, 18, 12)
        heading = chapter_title("Spells", p)
        self.spell_title = heading.findChild(QLabel)
        column.addWidget(heading)

        column.addLayout(self._spell_filters())

        self.spell_model = QStandardItemModel(0, len(SPELL_COLUMNS))
        self.spell_model.setHorizontalHeaderLabels(SPELL_COLUMNS)
        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(self.spell_model)
        proxy.setSortRole(SORT)
        view = QTableView()
        view.setModel(proxy)
        view.setSortingEnabled(True)
        view.setIconSize(QSize(18, 18))
        view.verticalHeader().hide()
        view.verticalHeader().setDefaultSectionSize(ROW_HEIGHT)
        view.setShowGrid(False)
        view.setAlternatingRowColors(True)
        view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        header = view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table_style(view, p)
        view.selectionModel().currentRowChanged.connect(self._show_spell)
        self.spell_view = view
        column.addWidget(view, 1)

        self.spell_search.textChanged.connect(self.refilter)
        for combo in (
            self.spell_source,
            self.spell_technique,
            self.spell_form,
            self.spell_ritual,
        ):
            combo.currentIndexChanged.connect(self.refilter)
        for spin in (self.spell_min, self.spell_max):
            spin.valueChanged.connect(self.refilter)
        self.all_spells = spl.all_spells(self.saga)
        self.refilter()
        view.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        return box

    def _spell_filters(self) -> QVBoxLayout:
        """The filter bar over the spells, as on the terminal."""
        p = self.p
        self.spell_search = QLineEdit()
        self.spell_search.setPlaceholderText("Search spell names and descriptions…")
        self.spell_search.addAction(
            pictures.icon("search", p["label"], 16),
            QLineEdit.ActionPosition.LeadingPosition,
        )
        self.spell_source = _choice(
            "Any source",
            [(f"{key} – {name}", key) for key, name in spl.catalog_sources()]
            + [
                ("The saga's own", spl.OWN_SOURCE),
                ("Not in play", spl.OUT_OF_PLAY_SOURCE),
            ],
        )
        self.spell_technique = _choice("Any Technique", [(t, t) for t in TECHNIQUES])
        self.spell_form = _choice("Any Form", [(f, f) for f in FORMS])
        self.spell_ritual = _choice(
            "Rituals or not", [("Rituals", True), ("Formulaic", False)]
        )
        self.spell_min = _level("From level")
        self.spell_max = _level("To level")
        first, second = QHBoxLayout(), QHBoxLayout()
        first.addWidget(self.spell_search, 1)
        first.addWidget(self.spell_source)
        for widget in (
            self.spell_technique,
            self.spell_form,
            self.spell_ritual,
            self.spell_min,
            self.spell_max,
        ):
            second.addWidget(widget)
        second.addStretch(1)
        rows = QVBoxLayout()
        rows.addLayout(first)
        rows.addLayout(second)
        return rows

    def refilter(self) -> None:
        """Show the spells that pass the filters, as the terminal's list."""
        p, saga = self.p, self.saga

        def level(spin: QSpinBox) -> int | None:
            return None if spin.value() == ANY_LEVEL else spin.value()

        self.shown_spells = spl.filter_spells(
            saga,
            self.all_spells,
            text=self.spell_search.text(),
            technique=self.spell_technique.currentData(),
            form=self.spell_form.currentData(),
            ritual=self.spell_ritual.currentData(),
            source=self.spell_source.currentData(),
            min_level=level(self.spell_min),
            max_level=level(self.spell_max),
        )
        model = self.spell_model
        model.removeRows(0, model.rowCount())
        for index, row in enumerate(scs.spell_rows(saga, self.shown_spells)):
            name = _cell(row.name, row.name.lower(), font=serif(12.5))
            name.setData(index, Qt.ItemDataRole.UserRole)
            arts = _cell(row.arts, row.arts)
            if row.form in FORMS:
                arts.setIcon(
                    QIcon(
                        pictures.pixmap(
                            artwork.art_symbol(row.form), p["foreground"], 18, 2.0
                        )
                    )
                )
            level_cell = _cell(row.level_text, -1 if row.level is None else row.level)
            level_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            model.appendRow(
                [
                    name,
                    arts,
                    level_cell,
                    _cell(row.rdt, row.rdt),
                    _cell("Ritual" if row.ritual else "", int(row.ritual)),
                    _cell(row.source, row.source),
                ]
            )
        if self.spell_title is not None:
            self.spell_title.setText(
                f"Spells ({len(self.shown_spells)} of {len(self.all_spells)})"
            )

    def _show_spell(self, current, _previous) -> None:
        index = current.siblingAtColumn(0).data(Qt.ItemDataRole.UserRole)
        if index is None:
            return
        spell = self.shown_spells[index]
        self.inspect(
            spell.name,
            f"{spl.shorthand(spell)}  ·  {spl.rdt_text(spell)}",
            spl.detail_text(self.saga, spell),
            artwork.art_symbol(spell.form) if spell.form in FORMS else None,
        )

    def _players(self) -> QWidget:
        p, saga = self.p, self.saga
        players = scs.players_table(saga)
        self.players = cells_table(
            players.columns,
            players.rows,
            p,
            lambda row: self.inspect(
                saga.players[row].name,
                pl.ROLE_LABELS.get(saga.players[row].role, ""),
                pl.detail_text(saga, saga.players[row]),
            ),
        )
        note = Card(p, pad=10)
        note.column.addWidget(
            text(
                "Players sign in to the hosted terminal app; passcodes are kept"
                " only as hashes.",
                p["label"],
                wrap=True,
            )
        )
        return scrolling_page(
            p, section(f"Players ({len(saga.players)})", p, self.players), note
        )


def _cell(words: str, sort: object, *, font=None) -> QStandardItem:
    item = QStandardItem(words)
    item.setEditable(False)
    item.setData(sort, SORT)
    if font is not None:
        item.setFont(font)
    return item


def _choice(blank: str, options: Sequence[tuple[str, object]]) -> QComboBox:
    """A filter's drop-down: `blank` (no filter) first, then `options` as
    (label, value)."""
    combo = QComboBox()
    combo.addItem(blank, None)
    for label, value in options:
        combo.addItem(label, value)
    return combo


def _level(prefix: str) -> QSpinBox:
    spin = QSpinBox()
    spin.setRange(ANY_LEVEL, 100)
    spin.setSingleStep(5)
    spin.setValue(ANY_LEVEL)
    spin.setSpecialValueText(f"{prefix}: any")
    spin.setPrefix(f"{prefix}: ")
    return spin
