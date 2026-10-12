"""The desktop Character sheet, read-only: the terminal sheet's top panel
and tabs, drawn with Qt widgets from the same core text.

Lists that the terminal draws as padded columns keep those rows for now,
in a fixed-pitch font so they line up; the Arts are a real table, each
with its symbol.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .. import artwork, casting_text, seasons
from .. import books as bk
from .. import character_sheet as cs
from .. import laboratories as labs
from .. import sheet_text as st
from ..arts import FORMS, TECHNIQUES
from ..models import Character, Saga
from ..rules import creation_virtues as cv
from . import pictures
from .markup_html import plain, to_html
from .themes import Palette

#: The Arts table's symbol size, in pixels.
ART_SYMBOL = 22
#: The House symbol beside the name.
HOUSE_SYMBOL = 40

Rows = Sequence[tuple[int | None, str]]


def _fixed_font() -> QFont:
    font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
    font.setFamilies(["Cascadia Mono", "Consolas", font.family()])
    return font


class TextBlock(QLabel):
    """Core text (app markup) as a selectable, wrapping label."""

    def __init__(
        self, text: str, palette: Palette, *, pre: bool = False, mono: bool = False
    ) -> None:
        """`pre` keeps runs of spaces; `mono` also sets a fixed-pitch font,
        for the core's tables padded into columns."""
        super().__init__(to_html(text, palette, pre=pre or mono))
        if mono:
            self.setFont(_fixed_font())
        self.setTextFormat(Qt.TextFormat.RichText)
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)


class Details(QFrame):
    """The details panel under a tab's lists: what the chosen row is."""

    def __init__(self, palette: Palette, hint: str) -> None:
        super().__init__()
        self.setObjectName("details")
        self.palette_ = palette
        self.label = TextBlock(hint, palette)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.addWidget(self.label)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

    def show_text(self, text: str) -> None:
        self.label.setText(to_html(text, self.palette_))


_ALIGNED = re.compile(r"^\[\$label\](.*?):\s*\[/\] (.*)$")


def label_values(text: str, palette: Palette) -> QWidget:
    """The core's `label: value` lines (markup.aligned) as a two-column
    grid, since a proportional font can't line them up with spaces; any
    other text as a TextBlock."""
    lines = [_ALIGNED.match(line) for line in text.splitlines()]
    if not lines or not all(lines):
        return TextBlock(text, palette)
    box = QWidget()
    grid = QGridLayout(box)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(12)
    grid.setVerticalSpacing(1)
    for row, match in enumerate(lines):
        assert match is not None
        label = QLabel(f"{_html(match.group(1))}:")
        label.setStyleSheet(f"color:{palette['label']}")
        grid.addWidget(label, row, 0, Qt.AlignmentFlag.AlignTop)
        grid.addWidget(TextBlock(match.group(2), palette), row, 1)
    grid.setColumnStretch(1, 1)
    grid.setRowStretch(len(lines), 1)
    return box


def section_title(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("sectionTitle")
    font = label.font()
    font.setCapitalization(QFont.Capitalization.SmallCaps)
    label.setFont(font)
    return label


def row_list(rows: Rows, on_choose: Callable[[int], None] | None = None) -> QListWidget:
    """A list of the core's rows; a header row (no index) can't be chosen.
    Choosing a row calls `on_choose` with its index."""
    widget = QListWidget()
    widget.setFont(_fixed_font())
    for index, text in rows:
        item = QListWidgetItem(plain(text))
        if index is None:
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
        else:
            item.setData(Qt.ItemDataRole.UserRole, index)
        widget.addItem(item)
    widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
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


def scrolling(*widgets: QWidget, details: Details | None = None) -> QWidget:
    """A tab: its sections scrolling, with any details panel below them."""
    body = QWidget()
    column = QVBoxLayout(body)
    column.setContentsMargins(12, 10, 12, 10)
    column.setSpacing(10)
    for widget in widgets:
        column.addWidget(widget)
    column.addStretch(1)
    area = QScrollArea()
    area.setWidgetResizable(True)
    area.setWidget(body)
    if details is None:
        return area
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setContentsMargins(0, 0, 0, 8)
    layout.addWidget(area, 1)
    holder = QHBoxLayout()
    holder.setContentsMargins(12, 0, 12, 0)
    holder.addWidget(details)
    layout.addLayout(holder)
    return tab


def section(title: str, *widgets: QWidget) -> QWidget:
    box = QWidget()
    column = QVBoxLayout(box)
    column.setContentsMargins(0, 0, 0, 0)
    column.setSpacing(6)
    column.addWidget(section_title(title))
    for widget in widgets:
        column.addWidget(widget)
    return box


def side_by_side(*widgets: QWidget) -> QWidget:
    box = QWidget()
    row = QHBoxLayout(box)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(24)
    for widget in widgets:
        row.addWidget(widget, 1)
    return box


class CharacterSheet(QWidget):
    """One character's sheet: name, top panel and tabs."""

    def __init__(self, saga: Saga, character: Character, palette: Palette) -> None:
        super().__init__()
        self.saga, self.character, self.palette_ = saga, character, palette
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 8)
        layout.setSpacing(8)
        layout.addWidget(self._heading())
        layout.addWidget(self._top_panel())
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.addTab(self._description_tab(), "Description")
        self.tabs.addTab(self._abilities_tab(), "Abilities")
        self.tabs.addTab(self._virtues_flaws_tab(), "Virtues && Flaws")
        if character.type == "magus":
            self.tabs.addTab(self._hermetic_tab(), "Hermetic Magic")
        self.tabs.addTab(self._inventory_tab(), "Inventory")
        self.tabs.addTab(self._planning_tab(), "Planning")
        self.tabs.addTab(self._diary_tab(), "Diary")
        layout.addWidget(self.tabs, 1)

    # The top of the sheet

    def _heading(self) -> QWidget:
        """The name, its first letter a rubricated initial, and the House
        symbol of a magus."""
        name = self.character.name or "(unnamed)"
        p = self.palette_
        text = (
            f"<span style=\"font-family:'{pictures.DISPLAY}';color:{p['heading']};"
            f'font-size:30pt">{_html(name[0])}</span>{_html(name[1:])}'
        )
        label = QLabel(text)
        label.setObjectName("sheetName")
        label.setTextFormat(Qt.TextFormat.RichText)
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)
        row.addWidget(label)
        house = artwork.house_symbol(self.character.hermetic.house)
        if self.character.type == "magus" and house is not None:
            symbol = QLabel()
            symbol.setPixmap(pictures.pixmap(house, p["heading"], HOUSE_SYMBOL, 2.0))
            symbol.setToolTip(f"House {cs.house_name(self.character)}")
            row.addWidget(symbol)
        row.addStretch(1)
        box = QWidget()
        box.setLayout(row)
        return box

    def _top_panel(self) -> QWidget:
        saga, c, p = self.saga, self.character, self.palette_
        info = side_by_side(
            label_values(cs.info_left_text(saga, c), p),
            label_values(cs.info_right_text(saga, c), p),
            section(
                "Characteristics",
                TextBlock(st.characteristics_text(c.characteristics), p, mono=True),
            ),
        )
        return info

    # Tabs

    def _description_tab(self) -> QWidget:
        saga, c, p = self.saga, self.character, self.palette_
        parts: list[QWidget] = []
        if c.type == "magus":
            parts.append(
                section(
                    "Hermetic Background",
                    side_by_side(
                        TextBlock(cs.hermetic_background_left_text(c), p),
                        TextBlock(cs.hermetic_background_right_text(saga, c), p),
                    ),
                )
            )
        parts.append(
            section(
                "Biographical Detail",
                side_by_side(
                    TextBlock(cs.biographical_left_text(saga, c), p),
                    TextBlock(cs.biographical_right_text(c), p),
                ),
            )
        )
        parts.append(
            side_by_side(
                section(
                    f"Personality Traits ({len(c.personality_traits)})",
                    row_list(st.trait_rows(c.personality_traits)),
                ),
                section(
                    f"Reputations ({len(c.reputations)})",
                    row_list(st.trait_rows(c.reputations)),
                ),
            )
        )
        parts.append(section("Aging & Warping", TextBlock(cs.aging_text(c), p)))
        parts.append(
            section(
                "Health",
                side_by_side(
                    TextBlock(st.character_wounds_text(c), p, pre=True),
                    TextBlock(st.character_fatigue_text(c), p, pre=True),
                ),
            )
        )
        return scrolling(*parts)

    def _abilities_tab(self) -> QWidget:
        c = self.character
        details = Details(
            self.palette_, "[dim]Choose an Ability to see its details.[/]"
        )
        abilities = row_list(
            st.ability_rows(c.abilities, c.virtues_flaws),
            lambda index: details.show_text(
                st.ability_info_text(c.abilities, index, c.virtues_flaws)
            ),
        )
        return scrolling(
            section(f"Abilities ({len(c.abilities)})", abilities), details=details
        )

    def _virtues_flaws_tab(self) -> QWidget:
        c = self.character
        free = cv.house_benefit(c).free_indices
        details = Details(
            self.palette_, "[dim]Choose a Virtue or Flaw to see its details.[/]"
        )

        def show(index: int) -> None:
            details.show_text(st.vf_info_text(c.virtues_flaws, index))

        columns = []
        for kind in ("Virtue", "Flaw"):
            points = st.vf_points(c.virtues_flaws, kind, free)
            columns.append(
                section(
                    f"{kind}s ({points} pts)",
                    row_list(st.vf_rows(c.virtues_flaws, kind, free), show),
                )
            )
        return scrolling(side_by_side(*columns), details=details)

    def _hermetic_tab(self) -> QWidget:
        saga, c, p = self.saga, self.character, self.palette_
        details = Details(
            p, "[dim]Choose an Art or a Known Spell to see its details.[/]"
        )
        arts = side_by_side(
            self._arts_table("Techniques", TECHNIQUES, details),
            self._arts_table("Forms", FORMS, details),
        )
        parts: list[QWidget] = [
            section("Magical Arts", arts),
            section(
                "Casting Scores",
                TextBlock(casting_text.casting_scores_text(saga, c), p, mono=True),
            ),
            section("Raw Vis", row_list(cs.raw_vis_rows(c))),
            section(
                f"Known Spells ({len(c.spells_known)})",
                row_list(
                    st.known_spell_rows(saga, c),
                    lambda index: details.show_text(
                        cs.known_spell_info_text(saga, c, index)
                    ),
                ),
            ),
        ]
        if c.breakthroughs:
            parts.append(
                section(
                    f"Research Goals ({len(c.breakthroughs)})",
                    row_list(
                        [
                            (i, st.goal_row(goal))
                            for i, goal in enumerate(c.breakthroughs)
                        ],
                        lambda index: details.show_text(
                            st.goal_text(c.breakthroughs[index])
                        ),
                    ),
                )
            )
        return scrolling(*parts, details=details)

    def _arts_table(self, title: str, arts: Sequence[str], details: Details) -> QWidget:
        """One column of Arts: symbol, name, abbreviation, score and XP;
        clicking an Art shows its details."""
        p = self.palette_
        box = QWidget()
        grid = QGridLayout(box)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(2)
        heading = QLabel(title)
        heading.setStyleSheet(f"color:{p['label']};font-weight:600")
        grid.addWidget(heading, 0, 0, 1, 3)
        for column, text in ((3, "Score"), (4, "XP")):
            label = QLabel(text)
            label.setStyleSheet(f"color:{p['label']}")
            label.setAlignment(Qt.AlignmentFlag.AlignRight)
            grid.addWidget(label, 0, column)
        for row_number, row in enumerate(cs.art_rows(self.character, arts), 1):
            symbol = ArtButton(row.art, details, self.character)
            symbol.setPixmap(
                pictures.pixmap(
                    artwork.art_symbol(row.art), p["foreground"], ART_SYMBOL, 2.0
                )
            )
            name = ArtButton(row.art, details, self.character)
            name.setText(row.art)
            serif = QFont(pictures.SERIF)
            serif.setItalic(True)
            serif.setPointSizeF(12)
            name.setFont(serif)
            abbreviation = QLabel(row.abbreviation)
            abbreviation.setStyleSheet(f"color:{p['label']}")
            score = QLabel(row.score)
            score.setAlignment(Qt.AlignmentFlag.AlignRight)
            bold = score.font()
            bold.setBold(True)
            score.setFont(bold)
            xp = QLabel(str(row.xp))
            xp.setAlignment(Qt.AlignmentFlag.AlignRight)
            xp.setStyleSheet(f"color:{p['label']}")
            for column, widget in enumerate((symbol, name, abbreviation, score, xp)):
                grid.addWidget(widget, row_number, column)
        grid.setColumnStretch(5, 1)
        grid.setRowStretch(len(arts) + 1, 1)
        return box

    def _inventory_tab(self) -> QWidget:
        saga, c = self.saga, self.character
        details = Details(
            self.palette_, "[dim]Choose an item or a book to see its details.[/]"
        )
        parts: list[QWidget] = []
        if c.type == "magus":
            parts.append(section("Raw Vis", row_list(cs.raw_vis_rows(c))))
        parts.append(
            section(
                f"Personal Gear ({len(c.inventory)})",
                row_list(
                    cs.inventory_rows(c),
                    lambda index: details.show_text(cs.inventory_item_text(c, index)),
                ),
            )
        )
        books = bk.books_owned_by(saga, "character", c.id)
        parts.append(
            section(
                f"Books ({len(books)})",
                row_list(
                    [(i, bk.row_label(saga, book)) for i, book in enumerate(books)],
                    lambda index: details.show_text(bk.detail_text(saga, books[index])),
                ),
            )
        )
        return scrolling(*parts, details=details)

    def _planning_tab(self) -> QWidget:
        saga = self.saga
        return scrolling(
            section(
                f"This Season ({saga.current_season} {saga.current_year})",
                TextBlock(seasons.plan_text(saga, self.character), self.palette_),
            )
        )

    def _diary_tab(self) -> QWidget:
        diary = self.character.diary
        details = Details(self.palette_, labs.diary_info_text(diary, None))
        return scrolling(
            section(
                f"Diary ({len(diary)})",
                row_list(
                    labs.diary_rows(diary),
                    lambda index: details.show_text(labs.diary_info_text(diary, index)),
                ),
            ),
            details=details,
        )


class ArtButton(QLabel):
    """An Art's symbol or name in the Arts table: clicking it shows the
    Art's details."""

    def __init__(self, art: str, details: Details, character: Character) -> None:
        super().__init__()
        self.art, self.details, self.character = art, details, character
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(art)

    def mousePressEvent(self, event) -> None:
        self.details.show_text(cs.art_info_text(self.character, self.art))
        super().mousePressEvent(event)


def _html(text: str) -> str:
    import html

    return html.escape(text)
