"""The desktop Character sheet, read-only, in the Codex layout: a header
with the name and the character's state at a glance, the
Characteristics as cards, a rail of chapters on the left and an
inspector on the right that shows whatever was last chosen.

What it says comes from the shared core (character_sheet.py and the
modules it reads), the same text and figures the terminal sheet shows;
only how it is drawn is here. The tables are Qt Model/View: a
QStandardItemModel of the core's rows, shown by a view (a proxy model
sorts and filters the spells). Every choice is a signal the inspector
listens to.
"""

from __future__ import annotations

import html
import re
from collections.abc import Callable, Sequence
from pathlib import Path

from PySide6.QtCore import QSize, QSortFilterProxyModel, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontDatabase,
    QIcon,
    QStandardItem,
    QStandardItemModel,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QTableView,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from .. import artwork, seasons
from .. import books as bk
from .. import character_sheet as cs
from .. import lab_texts as lt
from .. import laboratories as labs
from .. import saga_overview as ov
from .. import sheet_text as st
from .. import spells as spl
from ..arts import ART_ABBREVIATIONS, FORMS, TECHNIQUES
from ..models import Character, Saga
from . import pictures
from .figures import (
    Dial,
    fact_grid,
    fatigue_ladder,
    prose,
    trait_list,
    wound_track,
)
from .markup_html import plain, to_html
from .themes import Palette
from .timeline import Calendar, legend, season_text
from .widgets import (
    ROW_HEIGHT,
    XP_BAR,
    Card,
    ClickableCard,
    Codex,
    Pips,
    TallRows,
    XpBarDelegate,
    badge,
    chapter_title,
    chip,
    display_name,
    mix,
    scrolling_page,
    serif,
    text,
)

#: The House symbol beside the name, and an Art's in a table, in pixels.
HOUSE_SYMBOL = 56
ART_SYMBOL = 20
#: Row heights of the tables.
ROW = ROW_HEIGHT

#: The chapters, in order, with each one's icon (artwork.ICON_NAMES).
CHAPTERS = (
    ("Description", "character"),
    ("Abilities", "library"),
    ("Virtues & Flaws", "magic"),
    ("Hermetic Magic", "enchanted_item"),
    ("Inventory", "combat"),
    ("Planning", "season"),
    ("Diary", "year"),
)

#: A status tone's colour (character_sheet.condition).
TONES = {cs.GOOD: "text-success", cs.WARNING: "text-warning", cs.BAD: "text-error"}

Rows = Sequence[tuple[int | None, str]]


def _html(words: str) -> str:
    return html.escape(words)


def _fixed_font() -> QFont:
    font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
    font.setFamilies(["Cascadia Mono", "Consolas", font.family()])
    return font


class TextBlock(QLabel):
    """Core text (app markup) as a selectable, wrapping label."""

    def __init__(
        self, words: str, palette: Palette, *, pre: bool = False, mono: bool = False
    ) -> None:
        """`pre` keeps runs of spaces; `mono` also sets a fixed-pitch font,
        for the core's tables padded into columns."""
        super().__init__(to_html(words, palette, pre=pre or mono))
        if mono:
            self.setFont(_fixed_font())
        self.setTextFormat(Qt.TextFormat.RichText)
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)


_ALIGNED = re.compile(r"^\[\$label\](.*?):\s*\[/\] (.*)$")


def label_values(words: str, palette: Palette) -> QWidget:
    """The core's `label: value` lines (markup.aligned) as a two-column
    grid, since a proportional font can't line them up with spaces; any
    other text as a TextBlock."""
    lines = [_ALIGNED.match(line) for line in words.splitlines()]
    if not lines or not all(lines):
        return TextBlock(words, palette)
    box = QWidget()
    grid = QGridLayout(box)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(12)
    grid.setVerticalSpacing(1)
    for row, match in enumerate(lines):
        assert match is not None
        grid.addWidget(
            text(f"{match.group(1)}:", palette["label"]),
            row,
            0,
            Qt.AlignmentFlag.AlignTop,
        )
        grid.addWidget(TextBlock(match.group(2), palette), row, 1)
    grid.setColumnStretch(1, 1)
    grid.setRowStretch(len(lines), 1)
    return box


def row_list(rows: Rows, on_choose: Callable[[int], None] | None = None) -> QListWidget:
    """A list of the core's padded rows, in a fixed-pitch font so their
    columns line up; a header row (no index) can't be chosen. Choosing a
    row calls `on_choose` with its index."""
    widget = QListWidget()
    widget.setFont(_fixed_font())
    for index, words in rows:
        item = QListWidgetItem(plain(words))
        if index is None:
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
        else:
            item.setData(Qt.ItemDataRole.UserRole, index)
        widget.addItem(item)
    # Tall enough for its rows (up to 14), measured as drawn, so a
    # high-DPI screen's taller rows aren't cut off.
    row = widget.sizeHintForRow(0) if rows else widget.fontMetrics().height() + 8
    widget.setFixedHeight(
        min(max(len(rows), 1), 14) * row + 2 * widget.frameWidth() + 4
    )
    if on_choose is not None:
        widget.currentItemChanged.connect(
            lambda item, _old: (
                on_choose(item.data(Qt.ItemDataRole.UserRole))
                if item is not None and item.data(Qt.ItemDataRole.UserRole) is not None
                else None
            )
        )
    return widget


def side_by_side(*widgets: QWidget, spacing: int = 24) -> QWidget:
    box = QWidget()
    row = QHBoxLayout(box)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(spacing)
    for widget in widgets:
        row.addWidget(widget, 1, Qt.AlignmentFlag.AlignTop)
    return box


def section(title: str, p: Palette, *widgets: QWidget) -> QWidget:
    box = QWidget()
    column = QVBoxLayout(box)
    column.setContentsMargins(0, 0, 0, 0)
    column.setSpacing(6)
    column.addWidget(chapter_title(title, p))
    for widget in widgets:
        column.addWidget(widget)
    return box


def _table_style(view: QAbstractItemView, p: Palette) -> None:
    view.setStyleSheet(
        f"QAbstractItemView {{ background:{p['surface']};"
        f" alternate-background-color:{p['background']};"
        f" border:1px solid {p['rule']}; selection-background-color:"
        f" {p['selection']}; selection-color:{p['foreground']}; }}"
        f" QHeaderView::section {{ background:{p['panel']}; color:{p['foreground']};"
        " border:none; padding:5px; font-weight:600; }"
    )


def _fit_height(view: QAbstractItemView, rows: int) -> None:
    """Show every row, so the chapter scrolls rather than the table."""
    header = view.horizontalHeader() if isinstance(view, QTableView) else None
    if isinstance(view, QTreeView):
        header = view.header()
    top = header.sizeHint().height() if header is not None else 0
    view.setFixedHeight(rows * ROW + top + 2 * view.frameWidth() + 2)
    view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


def _item(words: str = "", *, font: QFont | None = None) -> QStandardItem:
    item = QStandardItem(words)
    item.setEditable(False)
    if font is not None:
        item.setFont(font)
    return item


class XpTable(QTreeView):
    """Arts or Abilities as a table grouped under headings, the last column
    an experience bar to the next score. A row's `key` (an Art's name or
    an Ability's index) goes to `on_choose` when the row is chosen."""

    def __init__(
        self, columns: Sequence[str], p: Palette, on_choose: Callable[[object], None]
    ) -> None:
        super().__init__()
        self.p, self.on_choose = p, on_choose
        self.model_ = QStandardItemModel(0, len(columns))
        self.model_.setHorizontalHeaderLabels(list(columns))
        self.setModel(self.model_)
        self.setItemDelegate(TallRows())
        self.setItemDelegateForColumn(len(columns) - 1, XpBarDelegate(p))
        self.setRootIsDecorated(False)
        self.setIndentation(10)
        self.setUniformRowHeights(True)
        self.setIconSize(QSize(ART_SYMBOL, ART_SYMBOL))
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        _table_style(self, p)
        self.rows = 0
        self.selectionModel().currentRowChanged.connect(self._chosen)

    def group(self, title: str) -> QStandardItem:
        head = _item(title, font=serif(13, caps=True, bold=True))
        head.setForeground(QBrush(QColor(self.p["heading"])))
        head.setSelectable(False)
        self.model_.appendRow(head)
        self.setFirstColumnSpanned(self.model_.rowCount() - 1, self.rootIndex(), True)
        self.rows += 1
        return head

    def add(
        self,
        group: QStandardItem | None,
        key: object,
        cells: Sequence[QStandardItem],
        fraction: float,
        bar: str,
    ) -> None:
        cells[0].setData(key, Qt.ItemDataRole.UserRole)
        last = _item()
        last.setData((fraction, bar), XP_BAR)
        (group or self.model_).appendRow([*cells, last])
        self.rows += 1

    def finish(self) -> None:
        self.expandAll()
        header = self.header()
        for column in range(self.model_.columnCount() - 1):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(
            self.model_.columnCount() - 1, QHeaderView.ResizeMode.Stretch
        )
        header.setStretchLastSection(True)
        _fit_height(self, self.rows)

    def sizeHintForRow(self, row: int) -> int:
        return ROW

    def _chosen(self, current, _previous) -> None:
        key = current.siblingAtColumn(0).data(Qt.ItemDataRole.UserRole)
        if key is not None:
            self.on_choose(key)


def _score_item(score: str) -> QStandardItem:
    font = QFont(pictures.UI)
    font.setPointSizeF(11)
    font.setBold(True)
    item = _item(score, font=font)
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    return item


def _xp_words(xp: int, next_xp: int) -> str:
    return f"{xp} / {next_xp} xp"


class CharacterSheet(QWidget):
    """One character's sheet in the Codex layout."""

    def __init__(self, saga: Saga, character: Character, palette: Palette) -> None:
        super().__init__()
        self.saga, self.character, self.p = saga, character, palette
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 12, 12, 8)
        outer.setSpacing(10)
        outer.addWidget(self._header())
        outer.addWidget(self._characteristics())

        self.codex = Codex(palette)
        self.inspector = self.codex.inspector
        builders = {
            "Description": self._description,
            "Abilities": self._abilities,
            "Virtues & Flaws": self._virtues_flaws,
            "Hermetic Magic": self._hermetic,
            "Inventory": self._inventory,
            "Planning": self._planning,
            "Diary": self._diary,
        }
        for name, concept in CHAPTERS:
            if name == "Hermetic Magic" and character.type != "magus":
                continue
            self.codex.add(name, concept, builders[name]())
        outer.addWidget(self.codex, 1)

    def chapters(self) -> list[str]:
        return self.codex.chapters()

    def open_chapter(self, name: str) -> None:
        self.codex.open_chapter(name)

    def inspect(
        self, title: str, subtitle: str, markup: str, symbol: Path | None = None
    ) -> None:
        self.codex.inspect(title, subtitle, markup, symbol)

    # The header

    def _header(self) -> QWidget:
        """The House symbol, the name with a rubricated initial, the line
        under it, and Confidence, Warping, Decrepitude and condition."""
        p, c = self.p, self.character
        box = QWidget()
        row = QHBoxLayout(box)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(14)
        house = artwork.house_symbol(c.hermetic.house)
        if c.type == "magus" and house is not None:
            symbol = QLabel()
            symbol.setPixmap(pictures.pixmap(house, p["heading"], HOUSE_SYMBOL, 2.0))
            symbol.setToolTip(f"House {cs.house_name(c)}")
            row.addWidget(symbol, 0, Qt.AlignmentFlag.AlignTop)
        names = QVBoxLayout()
        names.setSpacing(0)
        heading = display_name(c.name, p)
        names.addWidget(heading)
        names.addWidget(
            text(cs.subtitle(self.saga, c), p["label"], serif(12.5, italic=True))
        )
        row.addLayout(names)
        row.addStretch(1)

        b = c.background
        confidence = QVBoxLayout()
        confidence.setSpacing(2)
        confidence.addWidget(text("Confidence", p["label"], serif(10, caps=True)))
        pips = QHBoxLayout()
        pips.addWidget(
            text(str(b.confidence_score), p["foreground"], serif(18, bold=True))
        )
        pips.addWidget(
            Pips(b.confidence_points, max(5, b.confidence_points), p["accent"])
        )
        confidence.addLayout(pips)
        confidence.addStretch(1)
        row.addLayout(confidence)
        row.addSpacing(10)
        row.addWidget(Dial(cs.warping_dial(c), "Warping", p["text-warning"], p))
        row.addWidget(Dial(cs.decrepitude_dial(c), "Decrepitude", p["text-error"], p))
        status = QVBoxLayout()
        status.setSpacing(4)
        for words, tone in cs.condition(c):
            status.addWidget(chip(words, p[TONES[tone]]))
        status.addStretch(1)
        row.addLayout(status)
        return box

    def _characteristics(self) -> QWidget:
        p, ch = self.p, self.character.characteristics
        box = QWidget()
        row = QHBoxLayout(box)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        for name in (
            "intelligence",
            "perception",
            "strength",
            "stamina",
            "presence",
            "communication",
            "dexterity",
            "quickness",
        ):
            value = getattr(ch, name)
            colour = (
                p["text-success"]
                if value > 0
                else p["text-error"]
                if value < 0
                else p["dim"]
            )
            card = Card(p, pad=6)
            card.setFixedHeight(64)
            card.column.setSpacing(0)
            number = text(f"{value:+d}" if value else "0", colour, serif(20, bold=True))
            number.setAlignment(Qt.AlignmentFlag.AlignCenter)
            caption = text(name.title(), p["label"], serif(10.5, caps=True))
            caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card.column.addWidget(number)
            card.column.addWidget(caption)
            row.addWidget(card, 1)
        return box

    # Chapters

    def _description(self) -> QWidget:
        """Who the character is, in the book's type: facts with small-caps
        labels, prose with a rubricated initial, and traits, wounds and
        Fatigue drawn rather than listed."""
        saga, c, p = self.saga, self.character, self.p
        parts: list[QWidget] = [
            section("At a Glance", p, fact_grid(cs.glance_facts(saga, c), p, 6))
        ]
        if c.type == "magus":
            sigil = c.hermetic.wizards_sigil
            lineage: list[QWidget] = [fact_grid(cs.hermetic_facts(c), p)]
            if sigil:
                lineage.append(_sigil(sigil, p))
            lineage.append(TextBlock(lt.access_text(saga, c), p))
            parts.append(section("Hermetic Background", p, *lineage))
        traits = [(t.name, t.score) for t in c.personality_traits]
        reputations = [(t.name, t.score) for t in c.reputations]
        parts.append(
            side_by_side(
                section(
                    f"Personality Traits ({len(traits)})", p, trait_list(traits, p)
                ),
                section(
                    f"Reputations ({len(reputations)})", p, trait_list(reputations, p)
                ),
            )
        )
        parts.append(
            section(
                "Biographical Detail",
                p,
                fact_grid(cs.biographical_facts(saga, c), p, 4),
                _subheading("Appearance", p),
                prose(c.description.physical_description, p, initial=False),
                _subheading("Biography", p),
                prose(c.description.biography, p),
            )
        )
        health: list[QWidget] = [
            wound_track(cs.wound_track(c), p),
            _subheading("Fatigue", p),
            fatigue_ladder(cs.fatigue_track(c), p),
            fact_grid(cs.health_facts(c), p, 4),
        ]
        parts.append(section("Health", p, *health))
        aging = cs.aging_facts(c)
        effects = c.aging.effects
        if aging or effects:
            parts.append(
                section(
                    "Aging",
                    p,
                    *([fact_grid(aging, p, 4)] if aging else []),
                    *([prose(effects, p, initial=False)] if effects else []),
                )
            )
        return scrolling_page(*parts)

    def _abilities(self) -> QWidget:
        p, c = self.p, self.character

        def show(index: object) -> None:
            assert isinstance(index, int)
            ability = c.abilities[index]
            specialty = f"  ·  {ability.specialty}" if ability.specialty else ""
            self.inspect(
                ability.name,
                f"{ability.category} Ability{specialty}",
                st.ability_info_text(c.abilities, index, c.virtues_flaws),
            )

        table = XpTable(["Ability", "Specialty", "Score", "Experience"], p, show)
        groups: dict[str, QStandardItem] = {}
        for row in cs.ability_table(c):
            if row.category not in groups:
                groups[row.category] = table.group(row.category)
            specialty = _item(row.specialty, font=serif(11.5, italic=True))
            specialty.setForeground(QBrush(QColor(p["label"])))
            table.add(
                groups[row.category],
                row.index,
                [_item(row.name), specialty, _score_item(row.score)],
                row.fraction,
                _xp_words(row.xp, row.next_xp),
            )
        table.finish()
        return scrolling_page(
            chapter_title(f"Abilities ({len(c.abilities)})", p), table
        )

    def _virtues_flaws(self) -> QWidget:
        p, c = self.p, self.character
        columns = []
        for side, tone in (("Virtue", "text-success"), ("Flaw", "text-error")):
            column = QWidget()
            stack = QVBoxLayout(column)
            stack.setContentsMargins(0, 0, 0, 0)
            stack.setSpacing(10)
            points = cs.virtue_flaw_points(c, side)
            stack.addWidget(chapter_title(f"{side}s  ·  {points:g} points", p))
            for card in cs.virtue_flaw_cards(c, side):
                stack.addWidget(self._vf_card(card, p[tone]))
            stack.addStretch(1)
            columns.append(column)
        return scrolling_page(side_by_side(*columns, spacing=18))

    def _vf_card(self, card: cs.VirtueFlawCard, colour: str) -> QWidget:
        p, c = self.p, self.character
        frame = ClickableCard(p, edge=colour, pad=10)
        top = QHBoxLayout()
        top.addWidget(text(card.name, p["foreground"], serif(13.5, bold=True)))
        top.addStretch(1)
        top.addWidget(badge(card.tier, p["dim"] if card.tier == "Free" else colour, p))
        frame.column.addLayout(top)
        if card.summary:
            summary = text(card.summary, p["label"], wrap=True)
            frame.column.addWidget(summary)
        frame.column.addWidget(text(card.category, p["dim"], serif(10, caps=True)))
        frame.clicked = lambda: self.inspect(
            card.name,
            f"{card.tier}  ·  {card.category}",
            st.vf_info_text(c.virtues_flaws, card.index),
        )
        return frame

    def _hermetic(self) -> QWidget:
        p, c = self.p, self.character
        parts: list[QWidget] = [
            chapter_title("Magical Arts", p),
            self._arts(),
            chapter_title("Casting Scores", p),
            self._casting_grid(),
            chapter_title(f"Known Spells ({len(c.spells_known)})", p),
            self._spells(),
            chapter_title("Raw Vis", p),
            row_list(cs.raw_vis_rows(c)),
        ]
        if c.breakthroughs:
            parts.append(chapter_title(f"Research Goals ({len(c.breakthroughs)})", p))
            parts.append(
                row_list(
                    [(i, st.goal_row(goal)) for i, goal in enumerate(c.breakthroughs)],
                    lambda index: self.inspect(
                        "Research Goal", "", st.goal_text(c.breakthroughs[index])
                    ),
                )
            )
        return scrolling_page(*parts)

    def _show_art(self, art: object) -> None:
        assert isinstance(art, str)
        kind = "Technique" if art in TECHNIQUES else "Form"
        self.inspect(
            art,
            f"{kind}  ·  {ART_ABBREVIATIONS[art]}",
            cs.art_info_text(self.character, art),
            artwork.art_symbol(art),
        )

    def _arts(self) -> QWidget:
        """The Arts as tables like the Abilities, the Techniques beside the
        Forms: each Art with its symbol, score and experience."""
        p, c = self.p, self.character
        views = []
        for title, arts in (("Technique", TECHNIQUES), ("Form", FORMS)):
            table = XpTable([title, "Score", "Experience"], p, self._show_art)
            for row in cs.art_rows(c, arts):
                name = _item(row.art, font=serif(12.5, italic=True))
                symbol = artwork.art_symbol(row.art)
                name.setIcon(
                    QIcon(pictures.pixmap(symbol, p["foreground"], ART_SYMBOL, 2.0))
                )
                name.setToolTip(f"{row.art} ({row.abbreviation})")
                table.add(
                    None,
                    row.art,
                    [name, _score_item(row.score)],
                    row.fraction,
                    _xp_words(row.xp, row.next_xp),
                )
            table.finish()
            views.append(table)
        self.technique_view, self.form_view = views
        return side_by_side(*views, spacing=14)

    def _casting_grid(self) -> QWidget:
        """Every Casting Score as a heat map, Forms across and Techniques
        down; choosing a cell shows its terms."""
        p = self.p
        scores = cs.casting_grid(self.saga, self.character)
        totals = [int(score.total) for score in scores.values()]
        low, high = min(totals), max(totals)
        model = QStandardItemModel(len(TECHNIQUES), len(FORMS))
        for column, form in enumerate(FORMS):
            head = _item(ART_ABBREVIATIONS[form])
            head.setIcon(
                QIcon(
                    pictures.pixmap(artwork.art_symbol(form), p["foreground"], 20, 2.0)
                )
            )
            head.setToolTip(form)
            model.setHorizontalHeaderItem(column, head)
        for row, technique in enumerate(TECHNIQUES):
            head = _item(technique)
            head.setIcon(
                QIcon(
                    pictures.pixmap(
                        artwork.art_symbol(technique), p["foreground"], 20, 2.0
                    )
                )
            )
            model.setVerticalHeaderItem(row, head)
            for column, form in enumerate(FORMS):
                total = int(scores[technique, form].total)
                heat = (total - low) / max(high - low, 1)
                cell = _item(str(total))
                cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                cell.setBackground(
                    QBrush(mix(p["surface"], p["primary"], 0.08 + 0.62 * heat))
                )
                cell.setForeground(
                    QBrush(QColor(p["background"] if heat > 0.55 else p["foreground"]))
                )
                font = QFont(pictures.UI)
                font.setPointSizeF(11)
                font.setBold(heat > 0.55)
                cell.setFont(font)
                cell.setToolTip(f"{technique} {form}: {total}")
                model.setItem(row, column, cell)
        view = QTableView()
        view.setModel(model)
        view.setIconSize(QSize(20, 20))
        view.setShowGrid(False)
        view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        view.verticalHeader().setDefaultSectionSize(34)
        view.verticalHeader().setFont(serif(12, italic=True))
        _table_style(view, p)
        view.setFixedHeight(
            34 * len(TECHNIQUES) + view.horizontalHeader().sizeHint().height() + 4
        )
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        def show(index) -> None:
            technique, form = TECHNIQUES[index.row()], FORMS[index.column()]
            self.inspect(
                f"{technique} {form}",
                f"{ART_ABBREVIATIONS[technique]}{ART_ABBREVIATIONS[form]}"
                " Casting Score",
                cs.casting_cell_text(scores[technique, form]),
                artwork.art_symbol(form),
            )

        view.clicked.connect(show)
        self.casting_view = view
        return view

    def _spells(self) -> QWidget:
        """Known Spells as a table that sorts by any column and filters by
        name."""
        p, saga, c = self.p, self.saga, self.character
        rows = cs.spell_table(saga, c)
        model = _spell_model(rows, p)
        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        proxy.setFilterKeyColumn(0)
        proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        view = QTableView()
        view.setModel(proxy)
        view.setSortingEnabled(True)
        view.sortByColumn(2, Qt.SortOrder.DescendingOrder)
        view.setIconSize(QSize(18, 18))
        view.verticalHeader().hide()
        view.verticalHeader().setDefaultSectionSize(ROW)
        view.setShowGrid(False)
        view.setAlternatingRowColors(True)
        view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        header = view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        _table_style(view, p)
        _fit_height(view, max(len(rows), 1))

        def show(current, _previous) -> None:
            index = current.siblingAtColumn(0).data(Qt.ItemDataRole.UserRole)
            if index is None:
                return
            known = c.spells_known[index]
            spell = spl.find_spell(saga, known.spell_id)
            subtitle = (
                f"{spl.shorthand(spell)}  ·  {spell.range}/{spell.duration}/{spell.target}"
                if spell
                else ""
            )
            symbol = artwork.art_symbol(spell.form) if spell else None
            self.inspect(
                spell.name if spell else known.spell_id,
                subtitle,
                cs.known_spell_info_text(saga, c, index),
                symbol,
            )

        view.selectionModel().currentRowChanged.connect(show)

        search = QLineEdit()
        search.setPlaceholderText("Filter spells…")
        search.addAction(
            pictures.icon("search", p["label"], 16),
            QLineEdit.ActionPosition.LeadingPosition,
        )
        search.setStyleSheet(
            f"background:{p['surface']}; border:1px solid {p['rule']};"
            " border-radius:4px; padding:4px;"
        )
        search.textChanged.connect(proxy.setFilterFixedString)
        self.spell_view, self.spell_filter = view, search
        box = QWidget()
        column = QVBoxLayout(box)
        column.setContentsMargins(0, 0, 0, 0)
        column.addWidget(search)
        column.addWidget(view)
        return box

    def _inventory(self) -> QWidget:
        p, saga, c = self.p, self.saga, self.character
        parts: list[QWidget] = []
        if c.type == "magus":
            parts.append(section("Raw Vis", p, row_list(cs.raw_vis_rows(c))))
        parts.append(
            section(
                f"Personal Gear ({len(c.inventory)})",
                p,
                row_list(
                    cs.inventory_rows(c),
                    lambda index: self.inspect(
                        c.inventory[index].name, "", cs.inventory_item_text(c, index)
                    ),
                ),
            )
        )
        books = bk.books_owned_by(saga, "character", c.id)
        parts.append(
            section(
                f"Books ({len(books)})",
                p,
                row_list(
                    [(i, bk.row_label(saga, book)) for i, book in enumerate(books)],
                    lambda index: self.inspect(
                        books[index].name, "", bk.detail_text(saga, books[index])
                    ),
                ),
            )
        )
        return scrolling_page(*parts)

    def _planning(self) -> QWidget:
        saga, p = self.saga, self.p
        return scrolling_page(
            section(
                f"This Season ({saga.current_season} {saga.current_year})",
                p,
                TextBlock(seasons.plan_text(saga, self.character), p),
            )
        )

    def _diary(self) -> QWidget:
        """The character's seasons as a calendar, a row per year, over the
        Diary's entries."""
        saga, c, p, diary = self.saga, self.character, self.p, self.character.diary
        self.calendar = Calendar(
            ov.calendar(saga, c),
            p,
            lambda who, when, season: self.inspect(who, when, season_text(season)),
            who=c.name,
            current=(saga.current_season, saga.current_year),
        )
        return scrolling_page(
            section("Seasons", p, legend(p), self.calendar),
            section(
                f"Diary ({len(diary)})",
                p,
                row_list(
                    labs.diary_rows(diary),
                    lambda index: self.inspect(
                        "Diary", "", labs.diary_info_text(diary, index)
                    ),
                ),
            ),
        )


def _subheading(words: str, p: Palette) -> QLabel:
    label = text(words, p["heading"], serif(12, italic=True))
    label.setContentsMargins(0, 6, 0, 0)
    return label


def _sigil(sigil: str, p: Palette) -> QWidget:
    """The Wizard's Sigil, set apart as a quotation."""
    label = text(
        f"Wizard's Sigil: \u201c{sigil}\u201d",
        p["foreground"],
        serif(13, italic=True),
        wrap=True,
    )
    label.setStyleSheet(
        f"color:{p['foreground']}; background:transparent;"
        f" border-left:3px solid {p['accent']}; padding-left:10px"
    )
    return label


def _spell_model(rows: Sequence[cs.SpellRow], p: Palette) -> QStandardItemModel:
    """The known spells as a model a table view shows, one row each."""
    columns = ["Spell", "Arts", "Level", "Range", "Duration", "Target", "Mastery"]
    model = QStandardItemModel(0, len(columns))
    model.setHorizontalHeaderLabels(columns)
    for row in rows:
        name = _item(row.name, font=serif(12))
        name.setData(row.index, Qt.ItemDataRole.UserRole)
        if row.form:
            name.setIcon(
                QIcon(
                    pictures.pixmap(
                        artwork.art_symbol(row.form), p["foreground"], 18, 2.0
                    )
                )
            )
        level = _item()
        level.setData(
            row.level if row.level is not None else -1, Qt.ItemDataRole.DisplayRole
        )
        if row.level is None:
            level.setText("Gen")
        mastery = _item("★" * row.mastery if row.mastery else "")
        mastery.setForeground(QBrush(QColor(p["accent"])))
        mastery.setToolTip(f"Mastery {row.mastery}")
        duration = row.duration + (", Ritual" if row.ritual else "")
        model.appendRow(
            [
                name,
                _item(row.arts),
                level,
                _item(row.range),
                _item(duration),
                _item(row.target),
                mastery,
            ]
        )
    return model
