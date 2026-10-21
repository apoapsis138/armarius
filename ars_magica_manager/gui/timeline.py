"""The season timeline: people down, seasons across, each season a pill in
its kind's colour (laboratory, study, writing...), a planned one hollow;
and one character's seasons as a calendar, a row per year.

What each season was comes from the core (saga_overview); this draws it.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QRectF, QSize, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPen,
    QStandardItem,
    QStandardItemModel,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from .. import saga_overview as ov
from ..markup import markdown_text
from ..models import SEASONS
from . import pictures
from .themes import Palette
from .widgets import serif, text

#: The item-data role holding a cell's ov.Season.
SEASON = Qt.ItemDataRole.UserRole + 2
#: The palette colour of each kind of season.
KIND_COLOURS = {
    ov.LAB: "season-lab",
    ov.STUDY: "season-study",
    ov.WRITING: "season-writing",
    ov.WORK: "season-work",
    ov.ADVENTURE: "season-adventure",
    ov.REST: "season-rest",
    ov.OTHER: "season-other",
}
CELL_WIDTH, CELL_HEIGHT = 92, 40
SHORT = {"Spring": "Sp", "Summer": "Su", "Autumn": "Au", "Winter": "Wi"}

Choose = Callable[[str, str, ov.Season | None], None]


class SeasonDelegate(QStyledItemDelegate):
    """Draws a cell's season as a rounded pill in its kind's colour:
    filled once done, hollow while only planned; the saga's current season
    is shaded, and a rule marks where each year begins."""

    def __init__(self, p: Palette, current: int, *, year_starts: Sequence[int]) -> None:
        super().__init__()
        self.p, self.current, self.year_starts = p, current, set(year_starts)

    def sizeHint(
        self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex
    ) -> QSize:
        return QSize(CELL_WIDTH, CELL_HEIGHT)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        p = self.p
        cell = QRectF(option.rect)  # type: ignore[attr-defined]
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if index.column() == self.current:
            painter.fillRect(cell, QColor(p["selection"]))
        if index.column() in self.year_starts:
            painter.setPen(QPen(QColor(p["rule"]), 1))
            painter.drawLine(cell.topLeft(), cell.bottomLeft())
        season = index.data(SEASON)
        if season is not None:
            colour = QColor(p[KIND_COLOURS[season.kind]])
            pill = cell.adjusted(4, 7, -4, -7)
            if season.planned:
                pen = QPen(colour, 2, Qt.PenStyle.DashLine)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
            else:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(colour)
            painter.drawRoundedRect(pill, 6, 6)
            painter.setPen(QColor(p["background"] if not season.planned else colour))
            font = QFont(pictures.UI)
            font.setPointSizeF(8.5)
            painter.setFont(font)
            painter.drawText(
                pill.adjusted(3, 0, -3, 0),
                Qt.AlignmentFlag.AlignCenter,
                painter.fontMetrics().elidedText(
                    season.label, Qt.TextElideMode.ElideRight, round(pill.width()) - 6
                ),
            )
        if option.state & QStyle.StateFlag.State_Selected:  # type: ignore[attr-defined]
            painter.setPen(QPen(QColor(p["heading"]), 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(cell.adjusted(2, 4, -2, -4), 7, 7)
        painter.restore()


def legend(p: Palette) -> QWidget:
    """A key to the colours, and how a planned season looks, four to a
    line so it fits a narrow chapter."""
    box = QWidget()
    grid = QGridLayout(box)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(14)
    grid.setVerticalSpacing(4)
    keys: list[tuple[str, str]] = [
        (kind, f"background:{p[KIND_COLOURS[kind]]}; border-radius:4px")
        for kind in ov.KINDS
    ]
    keys.append(
        (
            "Planned",
            f"border:2px dashed {p['label']}; border-radius:4px;"
            " background:transparent",
        )
    )
    for index, (words, style) in enumerate(keys):
        entry = QWidget()
        row = QHBoxLayout(entry)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        swatch = QLabel()
        swatch.setFixedSize(14, 14)
        swatch.setStyleSheet(style)
        row.addWidget(swatch)
        row.addWidget(text(words, p["label"]))
        row.addStretch(1)
        grid.addWidget(entry, index // 4, index % 4)
    grid.setColumnStretch(4, 1)
    return box


class SeasonTimeline(QTableView):
    """People down, seasons across; choosing a season calls `on_choose`
    with the person's name, the season ("Spring 1220") and what they did,
    if anything."""

    def __init__(self, timeline: ov.Timeline, p: Palette, on_choose: Choose) -> None:
        super().__init__()
        self.timeline, self.on_choose = timeline, on_choose
        model = QStandardItemModel(len(timeline.rows), len(timeline.columns))
        for column, (season, year) in enumerate(timeline.columns):
            words = (
                f"{SHORT[season]}\n{year}" if season == SEASONS[0] else SHORT[season]
            )
            head = QStandardItem(words)
            head.setToolTip(f"{season} {year}")
            model.setHorizontalHeaderItem(column, head)
        for row, (_id, name, seasons) in enumerate(timeline.rows):
            model.setVerticalHeaderItem(row, QStandardItem(name))
            for column in range(len(timeline.columns)):
                cell = QStandardItem()
                cell.setEditable(False)
                season = seasons.get(column)
                if season is not None:
                    cell.setData(season, SEASON)
                    cell.setToolTip(f"{season.label}\n{season.detail}".strip())
                model.setItem(row, column, cell)
        self.setModel(model)
        starts = [
            i
            for i, (season, _year) in enumerate(timeline.columns)
            if season == SEASONS[0]
        ]
        self.setItemDelegate(SeasonDelegate(p, timeline.current, year_starts=starts))
        self.setShowGrid(False)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        across = self.horizontalHeader()
        across.setDefaultSectionSize(CELL_WIDTH)
        across.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        across.setFont(serif(10.5))
        across.setMinimumHeight(44)
        down = self.verticalHeader()
        down.setDefaultSectionSize(CELL_HEIGHT)
        down.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        down.setFont(serif(12.5))
        down.setMinimumWidth(150)
        self.setStyleSheet(
            f"QTableView {{ background:{p['surface']}; border:1px solid {p['rule']}; }}"
            f" QHeaderView::section {{ background:{p['surface']}; color:{p['label']};"
            f" border:none; border-bottom:1px solid {p['rule']}; padding:2px 8px; }}"
        )
        self.setFixedHeight(
            CELL_HEIGHT * max(len(timeline.rows), 1) + 44 + 2 * self.frameWidth() + 16
        )
        self.selectionModel().currentChanged.connect(self._chosen)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        # Open on now: the current season toward the right, the past to
        # its left.
        index = self.model().index(
            0, min(self.timeline.current + 3, self.model().columnCount() - 1)
        )
        self.scrollTo(index, QAbstractItemView.ScrollHint.PositionAtCenter)
        bar = self.horizontalScrollBar()
        bar.setValue(
            max(0, (self.timeline.current + 4) * CELL_WIDTH - self.viewport().width())
        )

    def _chosen(self, current: QModelIndex, _previous: QModelIndex) -> None:
        if not current.isValid():
            return
        _id, name, seasons = self.timeline.rows[current.row()]
        season, year = self.timeline.columns[current.column()]
        self.on_choose(name, f"{season} {year}", seasons.get(current.column()))


def season_text(season: ov.Season | None) -> str:
    """A chosen season's details for the inspector (app markup)."""
    if season is None:
        return "[dim]Nothing recorded or planned.[/]"
    state = "Planned" if season.planned else "Done"
    lines = [f"[b]{season.label}[/]", f"[$label]{season.kind}  ·  {state}[/]"]
    if season.detail:
        lines += ["", markdown_text(season.detail)]
    return "\n".join(lines)


class Calendar(QWidget):
    """One character's seasons, a row per year (newest first) with its four
    seasons; choosing one calls `on_choose`."""

    def __init__(
        self,
        rows: Sequence[tuple[int, Sequence[ov.Season | None]]],
        p: Palette,
        on_choose: Choose,
        *,
        who: str,
        current: tuple[str, int],
    ) -> None:
        super().__init__()
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        model = QStandardItemModel(len(rows), len(SEASONS))
        model.setHorizontalHeaderLabels(list(SEASONS))
        for row, (year, seasons) in enumerate(rows):
            model.setVerticalHeaderItem(row, QStandardItem(str(year)))
            for i, season in enumerate(seasons):
                cell = QStandardItem()
                cell.setEditable(False)
                if season is not None:
                    cell.setData(season, SEASON)
                    cell.setToolTip(f"{season.label}\n{season.detail}".strip())
                model.setItem(row, i, cell)
        view = QTableView()
        view.setModel(model)
        years = [year for year, _ in rows]
        now = years.index(current[1]) if current[1] in years else -1
        view.setItemDelegate(_CalendarDelegate(p, now, SEASONS.index(current[0])))
        view.setShowGrid(False)
        view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        view.horizontalHeader().setFont(serif(12, caps=True))
        down = view.verticalHeader()
        down.setDefaultSectionSize(CELL_HEIGHT)
        down.setFont(serif(12.5, bold=True))
        view.setStyleSheet(
            f"QTableView {{ background:{p['surface']}; border:1px solid {p['rule']}; }}"
            f" QHeaderView::section {{ background:{p['surface']}; color:{p['label']};"
            f" border:none; border-bottom:1px solid {p['rule']}; padding:4px 10px; }}"
        )
        view.setFixedHeight(
            CELL_HEIGHT * len(rows) + view.horizontalHeader().sizeHint().height() + 4
        )
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        def chosen(current_index: QModelIndex, _previous: QModelIndex) -> None:
            if current_index.isValid():
                year = rows[current_index.row()][0]
                season = SEASONS[current_index.column()]
                on_choose(who, f"{season} {year}", current_index.data(SEASON))

        view.selectionModel().currentChanged.connect(chosen)
        self.view = view
        column.addWidget(view)


class _CalendarDelegate(SeasonDelegate):
    """The timeline's pills, with the current season marked by its row
    and column rather than a whole column."""

    def __init__(self, p: Palette, row: int, column: int) -> None:
        super().__init__(p, -1, year_starts=())
        self.now = (row, column)

    def sizeHint(
        self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex
    ) -> QSize:
        return QSize(120, CELL_HEIGHT)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        if (index.row(), index.column()) == self.now:
            painter.fillRect(option.rect, QColor(self.p["selection"]))  # type: ignore[attr-defined]
        super().paint(painter, option, index)
