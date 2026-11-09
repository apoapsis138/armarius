"""The desktop Saga Content page in the Codex layout: what the saga's
pickers offer. Chapters for the books in play and the saga's own sources,
the shared catalogs and the single entries it hides, its House Rules,
every spell (sorted and filtered as on the terminal) and its players,
with the inspector beside them, and each section's Add, Edit and Delete.

What it says comes from the shared core (sheets/saga_content.py and the
modules behind it), and what its buttons do from forms/saga_content.py,
as the terminal's Saga Content view does.
"""

from __future__ import annotations

from PySide6.QtCore import QModelIndex, QSize, QSortFilterProxyModel, Qt
from PySide6.QtGui import QFont, QIcon, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QSpinBox,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from .. import (
    artwork,
    section_verbs,
    traditions,
)
from .. import house_rules as hr
from .. import saga_content as sc
from .. import spells as spl
from ..arts import FORMS, TECHNIQUES
from ..forms import goods as goods_forms
from ..forms import saga_content as scf
from ..models import Saga, Spell
from ..sections import (
    GOODS_SECTION,
    HOUSE_RULES_SECTION,
    SOURCES_SECTION,
)
from ..sheets import saga_content as scs
from . import pictures
from .character_sheet import TextBlock, section
from .editing import (
    Chooser,
    Run,
    choose_cards,
    choose_rows,
    verb_buttons,
)
from .figures import fact_grid
from .mystery_cults import CultsChapter
from .pages import card_grid, page_header
from .themes import Palette
from .widgets import (
    ANY_LEVEL,
    ROW_HEIGHT,
    ClickableCard,
    Codex,
    Symbol,
    ToggleSwitch,
    badge,
    cells_table,
    chip,
    chip_button,
    edit_button,
    filter_choice,
    level_box,
    scrolling_page,
    serif,
    table_style,
    table_view,
    text,
    tier_badge,
)

CHAPTERS = (
    ("Books", "library"),
    ("Traditions", "magic"),
    ("Catalogs", "lab_text"),
    ("Goods", "silver"),
    ("House Rules", "magic"),
    ("Mystery Cults", "secrets"),
    ("Spells", "enchanted_item"),
)

#: The chapters too long to draw every time the page opens.
LATER = ("Goods", "Traditions")

#: The spell table's columns.
SPELL_COLUMNS = ["Spell", "Arts", "Level", "Range/Duration/Target", "Ritual", "Source"]

#: The item-data role the spell table sorts by (a level sorts as a number).
SORT = Qt.ItemDataRole.UserRole + 2

#: A level filter's lowest value, shown as "any".


def _none(words: str, p: Palette) -> QLabel:
    return text(words, p["dim"], serif(12.5, italic=True))


class SagaContentPage(QWidget):
    """The saga's content in the Codex layout; choosing anything shows it
    in the inspector."""

    #: The tradition whose inspector switch was clicked: shown again when
    #: the page is redrawn.
    reopen = ""

    def __init__(
        self, saga: Saga, p: Palette, run: Run = lambda _command: None
    ) -> None:
        super().__init__()
        self.saga, self.p = saga, p
        self.run = run
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
            "Traditions": self._traditions,
            "Catalogs": self._catalogs,
            "Goods": self._goods,
            "House Rules": self._house_rules,
            "Mystery Cults": self._mystery_cults,
            "Spells": self._spells,
        }
        # The Players are in the saga page's Saga Management on the desktop.
        for name, concept in CHAPTERS:
            # The Goods ledger and the traditions' cards are long: drawn
            # when first turned to.
            build = builders[name]
            self.codex.add(name, concept, build if name in LATER else build())
        outer.addWidget(self.codex, 1)

    def chapters(self) -> list[str]:
        return self.codex.chapters()

    def inspect(
        self, title: str, subtitle: str, markup: str, symbol: Symbol | None = None
    ) -> None:
        self.codex.inspect(title, subtitle, markup, symbol)

    # Chapters

    def _books(self) -> QWidget:
        """The books as cards under their book line's heading, each saying
        what it brings, then the saga's own sources."""
        p, saga = self.p, self.saga
        cards = scs.book_cards(saga)
        groups = QWidget()
        column = QVBoxLayout(groups)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(8)
        heading = ""
        for group in scs.book_groups(saga, cards):
            if group.heading != heading:
                heading = group.heading
                column.addWidget(
                    text(heading, p["heading"], serif(13, caps=True, bold=True))
                )
            if group.subheading:
                column.addWidget(
                    text(group.subheading, p["label"], serif(12, italic=True))
                )
            column.addWidget(card_grid([self._book_card(b) for b in group.cards], 3))
        in_play = sum(1 for c in cards if c.state != scs.OUT_OF_PLAY)
        sources_chooser = Chooser()
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
        choose_rows(self.sources, sources_chooser)
        return scrolling_page(
            p,
            section(
                f"Books in Play ({in_play} of {len(cards)})",
                p,
                groups,
                edits={"Edit": lambda: self.run(scf.books_form(saga))},
            ),
            section(
                f"Saga Sources ({len(saga.sources)})",
                p,
                self.sources if saga.sources else _none("None yet.", p),
                buttons=verb_buttons(
                    section_verbs.ops_of(saga, saga)[SOURCES_SECTION],
                    sources_chooser,
                    self.run,
                    p,
                ),
            ),
        )

    def _book_card(self, book: scs.BookCard) -> ClickableCard:
        """A book's card: its abbreviation, whether it is in play (a
        supplement's chip puts it in or out), its title and what it brings;
        faded while out of play. Clicking it shows it in the inspector."""
        p, saga = self.p, self.saga
        tone = {
            scs.ALWAYS: p["accent"],
            scs.IN_PLAY: p["text-success"],
            scs.OUT_OF_PLAY: p["dim"],
        }[book.state]
        card = ClickableCard(p, pad=12, edge=tone)
        top = QHBoxLayout()
        top.addWidget(badge(book.book, tone, p))
        top.addStretch(1)
        if book.state == scs.ALWAYS:
            state = chip(book.state, tone)
            state.setToolTip("The core book is always in play.")
        else:
            state = chip_button(
                book.state, tone, lambda: self.run(scf.toggle_book(saga, book.book))
            )
            state.setToolTip(
                "Click to take it out of play."
                if book.state == scs.IN_PLAY
                else "Click to put it in play."
            )
        top.addWidget(state)
        card.column.addLayout(top)
        card.column.addWidget(
            text(book.title, p["foreground"], serif(13.5, bold=True), wrap=True)
        )
        if book.own:
            card.column.addWidget(
                text("The saga's own source", p["label"], serif(11, italic=True))
            )
        card.column.addWidget(
            text(book.brings, p["label"], serif(11.5), wrap=True)
            if book.brings
            else text(scs.NOTHING_COUNTED, p["dim"], serif(11, italic=True), wrap=True)
        )
        card.column.addStretch(1)
        card.clicked = lambda: self.inspect(
            book.title, book.book, scs.book_text(saga, book.book)
        )
        if book.state == scs.OUT_OF_PLAY:
            # Faded in place of the lift's shadow: a card has one effect.
            faded = QGraphicsOpacityEffect(card)
            faded.setOpacity(0.45)
            card.setGraphicsEffect(faded)
        return card

    def _traditions(self) -> QWidget:
        """Every tradition as a card under its book's heading: the
        heading's switch offers all of the book's traditions or none, each
        card's that one; a book out of play greys its cards out."""
        p, saga = self.p, self.saga
        body = QWidget()
        column = QVBoxLayout(body)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(8)
        for group in scs.tradition_groups(saga):
            head = QHBoxLayout()
            head.addWidget(
                text(group.title, p["heading"], serif(13, caps=True, bold=True))
            )
            head.addStretch(1)
            head.addWidget(text(group.state, p["label"], serif(11, italic=True)))
            switch = ToggleSwitch(
                group.state == scs.ALL_OFFERED,
                p,
                lambda book=group.book: self.run(scf.toggle_tradition_book(saga, book)),
            )
            switch.setEnabled(group.in_play)
            switch.setToolTip(
                f"Put {group.title} in play on Books in Play to offer its traditions."
                if not group.in_play
                else "Click to offer none of them."
                if group.state == scs.ALL_OFFERED
                else "Click to offer all of them."
            )
            head.addWidget(switch)
            column.addLayout(head)
            cards = card_grid([self._tradition_card(group, r) for r in group.rows], 3)
            if not group.in_play:
                faded = QGraphicsOpacityEffect(cards)
                faded.setOpacity(0.45)
                cards.setGraphicsEffect(faded)
            column.addWidget(cards)
        return scrolling_page(p, section(sc.traditions_title(saga), p, body))

    def _tradition_switch(
        self, group: scs.TraditionGroup, row: scs.TraditionRow, again: bool = False
    ) -> ToggleSwitch:
        """The switch that offers a tradition or stops; greyed out while
        its book is out of play. With `again`, the inspector shows the
        tradition again once the page is redrawn."""
        saga = self.saga

        def toggle() -> None:
            if again:
                SagaContentPage.reopen = row.id
            self.run(scf.toggle_tradition(saga, row.id))

        switch = ToggleSwitch(row.on and group.in_play, self.p, toggle)
        switch.setEnabled(group.in_play)
        switch.setToolTip(
            f"Put {group.title} in play on Books in Play to offer it."
            if not group.in_play
            else "Click to stop offering it."
            if row.on
            else "Click to offer it."
        )
        return switch

    def _tradition_card(
        self, group: scs.TraditionGroup, row: scs.TraditionRow
    ) -> ClickableCard:
        """A tradition in two lines: its name and switch, then its kind.
        Clicking it shows it in the inspector, with a switch of its own."""
        p, saga = self.p, self.saga
        card = ClickableCard(
            p, pad=8, edge=p["text-success"] if row.on and group.in_play else p["dim"]
        )
        card.column.setSpacing(2)
        top = QHBoxLayout()
        top.addWidget(
            text(row.name, p["foreground"], serif(12.5, bold=True), wrap=True), 1
        )
        top.addWidget(self._tradition_switch(group, row))
        card.column.addLayout(top)
        card.column.addWidget(
            text(row.kind, p["label"], serif(11, italic=True), wrap=True)
        )
        tradition = traditions.find(row.id)
        if tradition is not None:
            card.clicked = lambda: self.codex.inspect(
                row.name,
                row.kind,
                sc.tradition_text(saga, tradition),
                None,
                self._tradition_switch(group, row, again=True),
            )
        if SagaContentPage.reopen == row.id:
            SagaContentPage.reopen = ""
            card.clicked()
        return card

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
        catalogs_chooser = Chooser()
        choose_rows(self.catalogs, catalogs_chooser)
        hidden = sc.hidden_entries(saga)
        hidden_chooser = Chooser()
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
        choose_rows(hidden_view, hidden_chooser)

        def chosen_key() -> str | None:
            row = hidden_chooser.row(len(hidden))
            if row is not None:
                return hidden[row][0]
            row = catalogs_chooser.row(len(keys))
            return keys[row] if row is not None else None

        return scrolling_page(
            p,
            section(
                f"Catalogs ({len(keys)})",
                p,
                self.catalogs,
                buttons=verb_buttons(
                    scf.catalog_ops(saga), catalogs_chooser, self.run, p
                ),
            ),
            section(
                f"Hidden Entries ({len(hidden)})",
                p,
                hidden_view if hidden else _none("The saga hides none.", p),
                buttons=verb_buttons(
                    scf.hidden_ops(saga, chosen_key),
                    hidden_chooser,
                    self.run,
                    p,
                    nouns=("Hide", "Edit", "Offer again"),
                ),
            ),
        )

    def _goods(self) -> QWidget:
        """The Goods catalog and the saga's own goods as a ledger, a
        heading over each group; Add, Edit, Hide and Add a Purity act on
        the chosen good."""
        p, saga = self.p, self.saga
        table = goods_forms.table(saga)

        def show(index: int) -> None:
            name, subtitle = goods_forms.inspector_title(saga, index)
            self.inspect(name, subtitle, goods_forms.info(saga, index, wide=False))

        view = table_view(table, p, show)
        # The prices are words as printed ("1,650*", "#"), so table_view
        # doesn't take them for numbers: centre them as it does numbers.
        model = view.model()
        prices = range(len(goods_forms.COLUMNS) - 4, len(goods_forms.COLUMNS))
        if isinstance(model, QStandardItemModel):
            for column in prices:
                head = model.horizontalHeaderItem(column)
                if head is not None:
                    head.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                for row in range(model.rowCount()):
                    item = model.item(row, column)
                    if item is not None and table.key(row) is not None:
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        chooser = Chooser()
        choose_rows(view, chooser, table.key)
        more = [
            (
                "Add a Purity",
                "silver",
                lambda row: goods_forms.add_purity(saga, row),
                lambda row: goods_forms.offers_purity(saga, row),
            )
        ]
        return scrolling_page(
            p,
            section(
                goods_forms.title(saga),
                p,
                TextBlock(goods_forms.header(saga, two_lines=True), p),
                view,
                buttons=verb_buttons(
                    section_verbs.ops_of(saga, saga)[GOODS_SECTION],
                    chooser,
                    self.run,
                    p,
                    nouns=("Add", "Edit", "Hide"),
                    more=more,
                ),
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
                tier_badge(rule.tier, colour, p), 0, Qt.AlignmentFlag.AlignTop
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
        chooser = Chooser()
        choose_cards(cards, chooser)
        return scrolling_page(
            p,
            section(
                f"House Rules ({len(cards)})",
                p,
                card_grid(cards, 2) if cards else _none("None yet.", p),
                buttons=[
                    *verb_buttons(
                        section_verbs.ops_of(saga, saga)[HOUSE_RULES_SECTION],
                        chooser,
                        self.run,
                        p,
                    ),
                    *(
                        [
                            edit_button(
                                "Move to Source",
                                p,
                                lambda: self.run(scf.move_to_source(saga)),
                                "library",
                            )
                        ]
                        if saga.sources and cards
                        else []
                    ),
                ],
            ),
        )

    def _mystery_cults(self) -> QWidget:
        """The saga's own Mystery Cults, the chosen one, its degrees and
        the chosen degree's Script (gui/mystery_cults.py)."""
        return CultsChapter(self.saga, self.p, self.run, self.inspect)

    def _spells(self) -> QWidget:
        """Every spell the saga knows of in a table that sorts by any column,
        under the terminal's filters: words, source, Technique, Form, ritual
        and a range of levels."""
        p = self.p
        box = QWidget()
        column = QVBoxLayout(box)
        column.setContentsMargins(18, 4, 18, 12)
        self.spell_chooser = Chooser()
        self.spell_ops = scf.spell_ops(self.saga, lambda: self.shown_spells)
        self.shown_spells: list[Spell] = []
        heading = section(
            "Spells",
            p,
            buttons=verb_buttons(self.spell_ops, self.spell_chooser, self.run, p),
        )
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
        choose_rows(view, self.spell_chooser)
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
        self.spell_source = filter_choice(
            "Any source",
            [(f"{key} – {name}", key) for key, name in spl.catalog_sources()]
            + [
                ("The saga's own", spl.OWN_SOURCE),
                ("Not in play", spl.OUT_OF_PLAY_SOURCE),
            ],
        )
        self.spell_technique = filter_choice(
            "Any Technique", [(t, t) for t in TECHNIQUES]
        )
        self.spell_form = filter_choice("Any Form", [(f, f) for f in FORMS])
        self.spell_ritual = filter_choice(
            "Rituals or not", [("Rituals", True), ("Formulaic", False)]
        )
        self.spell_min = level_box("From level")
        self.spell_max = level_box("To level")
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
        self.spell_chooser.choose(None)
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

    def _show_spell(self, current: QModelIndex, _previous: QModelIndex) -> None:
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


def _cell(words: str, sort: object, *, font: QFont | None = None) -> QStandardItem:
    item = QStandardItem(words)
    item.setEditable(False)
    item.setData(sort, SORT)
    if font is not None:
        item.setFont(font)
    return item
