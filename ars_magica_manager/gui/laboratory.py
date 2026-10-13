"""The desktop laboratory page, read-only, in the Codex layout: a header
with the name, whose sanctum it is and its aura as a seal; the eight
Characteristics as a compass rose beside their cards; then chapters for the
Lab Totals, Virtues & Flaws, Specializations and Features, the stores and
the seasons, with the inspector beside them.

What it says comes from the shared core (laboratory_sheet.py and the
modules it reads), as the terminal's laboratory sheet does.
"""

from __future__ import annotations

import re

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .. import artwork, lab_planning
from .. import books as bk
from .. import laboratories as labs
from .. import laboratory_sheet as ls
from .. import saga_overview as ov
from ..arts import ART_ABBREVIATIONS
from ..models import Laboratory, Saga
from . import pictures
from .character_sheet import TextBlock, side_by_side
from .figures import AuraSeal, CompassRose, bar_list, fact_grid
from .pages import card_grid
from .themes import Palette
from .timeline import Calendar, legend, season_text
from .widgets import (
    Card,
    ClickableCard,
    Codex,
    arts_heat_grid,
    badge,
    chapter_title,
    display_name,
    scrolling_page,
    serif,
    text,
)

#: The chapters, in order, with each one's icon (artwork.ICON_NAMES).
CHAPTERS = (
    ("Lab Totals", "laboratory"),
    ("Virtues & Flaws", "magic"),
    ("Specializations", "lab_text"),
    ("Stores", "vis"),
    ("Seasons", "season"),
)


def _sign_colour(value: float, p: Palette) -> str:
    if value > 0:
        return p["text-success"]
    if value < 0:
        return p["text-error"]
    return p["dim"]


class LaboratoryPage(QWidget):
    """One laboratory in the Codex layout."""

    def __init__(self, saga: Saga, lab: Laboratory, palette: Palette) -> None:
        super().__init__()
        self.saga, self.lab, self.p = saga, lab, palette
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 12, 12, 8)
        outer.setSpacing(10)
        outer.addWidget(self._header())
        self.codex = Codex(palette)
        self.inspector = self.codex.inspector
        outer.addWidget(self._characteristics())
        builders = {
            "Lab Totals": self._totals,
            "Virtues & Flaws": self._virtues_flaws,
            "Specializations": self._specializations,
            "Stores": self._stores,
            "Seasons": self._seasons,
        }
        for name, concept in CHAPTERS:
            self.codex.add(name, concept, builders[name]())
        outer.addWidget(self.codex, 1)

    def chapters(self) -> list[str]:
        return self.codex.chapters()

    def inspect(self, title: str, subtitle: str, markup: str, symbol=None) -> None:
        self.codex.inspect(title, subtitle, markup, symbol)

    # Above the chapters

    def _header(self) -> QWidget:
        p, saga, lab = self.p, self.saga, self.lab
        box = QWidget()
        row = QHBoxLayout(box)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(14)
        magus = ls.owner(saga, lab)
        house = artwork.house_symbol(magus.hermetic.house) if magus else None
        symbol = QLabel()
        symbol.setPixmap(
            pictures.pixmap(house or artwork.icon("laboratory"), p["heading"], 56, 2.0)
        )
        row.addWidget(symbol, 0, Qt.AlignmentFlag.AlignTop)
        names = QVBoxLayout()
        names.setSpacing(0)
        names.addWidget(display_name(lab.name, p))
        names.addWidget(
            text(ls.subtitle(saga, lab), p["label"], serif(12.5, italic=True))
        )
        row.addLayout(names)
        row.addStretch(1)
        row.addWidget(fact_grid(ls.capacity_facts(lab), p, 3))
        row.addSpacing(10)
        row.addWidget(AuraSeal(ls.aura(saga, lab), p))
        return box

    def _characteristics(self) -> QWidget:
        """The eight Characteristics: a compass rose of them, and a card
        each with its total and where it comes from."""
        p = self.p
        rows = ls.characteristics(self.lab)
        cards = []
        for characteristic in rows:
            card = ClickableCard(p, pad=6)
            card.setFixedHeight(70)
            card.column.setSpacing(0)
            number = text(
                f"{characteristic.total:+d}" if characteristic.total else "0",
                _sign_colour(characteristic.total, p),
                serif(20, bold=True),
            )
            number.setAlignment(Qt.AlignmentFlag.AlignCenter)
            caption = text(characteristic.name, p["label"], serif(10.5, caps=True))
            caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
            from_vf = characteristic.virtues + characteristic.flaws
            working = text(
                f"{characteristic.manual:+d} typed · {from_vf:+d} Virtues & Flaws",
                p["dim"],
            )
            working.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card.column.addWidget(number)
            card.column.addWidget(caption)
            card.column.addWidget(working)
            card.clicked = lambda row=characteristic: self.inspect(
                row.name, "Laboratory Characteristic", ls.characteristic_text(row)
            )
            cards.append(card)
        self.characteristic_cards = cards
        box = QWidget()
        line = QHBoxLayout(box)
        line.setContentsMargins(0, 0, 0, 0)
        line.setSpacing(14)
        line.addWidget(CompassRose(rows, p))
        line.addWidget(card_grid(cards, 4), 1)
        return box

    # Chapters

    def _totals(self) -> QWidget:
        p, saga, lab = self.p, self.saga, self.lab
        totals = ls.lab_totals(saga, lab)
        magus = ls.owner(saga, lab)
        if totals is None:
            self.totals_view = None
            return scrolling_page(
                chapter_title("Lab Totals", p),
                text(
                    "Lab Totals are worked out for the magus who works here: "
                    "give the laboratory an owner to see them.",
                    p["dim"],
                    serif(13, italic=True),
                    wrap=True,
                ),
            )
        assert magus is not None

        def show(technique: str, form: str) -> None:
            self.inspect(
                f"{technique} {form}",
                f"{ART_ABBREVIATIONS[technique]}{ART_ABBREVIATIONS[form]} Lab Total"
                f"  ·  {magus.name}",
                ls.lab_total_text(totals[technique, form]),
                artwork.art_symbol(form),
            )

        self.totals_view = arts_heat_grid(
            {pair: int(total.total) for pair, total in totals.items()}, p, show
        )
        base, by_activity = Card(p), Card(p)
        base.column.addWidget(
            text("Base Lab Total", p["heading"], serif(13, bold=True))
        )
        base.column.addWidget(
            _markup(lab_planning.base_lab_total_text(saga, lab, magus), p)
        )
        by_activity.column.addWidget(
            text("By Activity", p["heading"], serif(13, bold=True))
        )
        by_activity.column.addWidget(
            _markup(lab_planning.activity_totals_text(saga, lab, magus), p)
        )
        return scrolling_page(
            chapter_title(f"Lab Totals  ·  {magus.name} working here", p),
            self.totals_view,
            side_by_side(base, by_activity, spacing=14),
        )

    def _virtues_flaws(self) -> QWidget:
        p, lab = self.p, self.lab
        columns = []
        for side, tone in (("Virtue", "text-success"), ("Flaw", "text-error")):
            column = QWidget()
            stack = QVBoxLayout(column)
            stack.setContentsMargins(0, 0, 0, 0)
            stack.setSpacing(10)
            points = labs.vf_points(lab, side)
            stack.addWidget(chapter_title(f"{side}s  ·  {points:g} points", p))
            cards = ls.virtue_flaw_cards(lab, side)
            for card in cards:
                stack.addWidget(self._vf_card(card, p[tone]))
            if not cards:
                stack.addWidget(
                    text(f"No {side}s.", p["dim"], serif(12.5, italic=True))
                )
            stack.addStretch(1)
            columns.append(column)
        return scrolling_page(side_by_side(*columns, spacing=18))

    def _vf_card(self, card: ls.VirtueFlawCard, colour: str) -> QWidget:
        p, lab = self.p, self.lab
        frame = ClickableCard(p, edge=colour, pad=10)
        top = QHBoxLayout()
        top.addWidget(
            text(card.name, p["foreground"], serif(13.5, bold=True), wrap=True), 1
        )
        top.addWidget(badge(card.tier, p["dim"] if card.tier == "Free" else colour, p))
        frame.column.addLayout(top)
        if card.summary:
            frame.column.addWidget(text(card.summary, p["label"], wrap=True))
        frame.column.addWidget(text(card.category, p["dim"], serif(10, caps=True)))
        frame.clicked = lambda: self.inspect(
            card.name,
            f"{card.tier}  ·  {card.category}",
            labs.vf_info_text(lab, card.index),
        )
        return frame

    def _specializations(self) -> QWidget:
        p, lab = self.p, self.lab
        rows = ls.specializations(lab)
        parts: list[QWidget] = []
        for kind in ("Activity", "Art"):
            group = [s for s in rows if s.kind == kind]
            if not group:
                continue
            parts.append(chapter_title(f"{kind} Specializations", p))
            parts.append(bar_list([(s.name, s.points, s.counts) for s in group], p))
        if not parts:
            parts += [
                chapter_title("Specializations", p),
                text("None yet.", p["dim"], serif(12.5, italic=True)),
            ]
        features = ls.feature_cards(lab)
        parts.append(chapter_title(f"Features ({len(features)})", p))
        cards = []
        for feature in features:
            card = ClickableCard(p, pad=10)
            card.column.addWidget(
                text(feature.name, p["foreground"], serif(13.5, bold=True))
            )
            card.column.addWidget(
                text(feature.kind, p["label"], serif(11.5, italic=True))
            )
            if feature.problem:
                card.column.addWidget(text(feature.problem, p["text-warning"]))
            card.clicked = lambda index=feature.index, name=feature.name: self.inspect(
                name, "Feature", labs.feature_info_text(lab, index)
            )
            cards.append(card)
        parts.append(
            card_grid(cards, 3)
            if cards
            else text("None yet.", p["dim"], serif(12.5, italic=True))
        )
        parts.append(chapter_title(f"Rooms ({len(lab.rooms)})", p))
        parts.append(self._named_cards(lab.rooms, "a room"))
        return scrolling_page(*parts)

    def _named_cards(self, entries, noun: str) -> QWidget:
        p = self.p
        cards = []
        for index, entry in enumerate(entries):
            card = ClickableCard(p, pad=10)
            card.column.addWidget(
                text(entry.name, p["foreground"], serif(13, bold=True))
            )
            if entry.description:
                card.column.addWidget(
                    text(_first_line(entry.description), p["label"], wrap=True)
                )
            card.clicked = lambda index=index, name=entry.name: self.inspect(
                name, "", labs.named_info_text(entries, index, noun)
            )
            cards.append(card)
        if not cards:
            return text("None recorded.", p["dim"], serif(12.5, italic=True))
        return card_grid(cards, 3)

    def _stores(self) -> QWidget:
        """Raw vis as a phial for each Art, then the equipment and stores,
        Arcane Connections and books."""
        p, saga, lab = self.p, self.saga, self.lab
        phials = []
        for index, art in enumerate(sorted(lab.raw_vis)):
            pawns = lab.raw_vis[art]
            card = ClickableCard(p, pad=10)
            top = QHBoxLayout()
            symbol = QLabel()
            name = art.title()
            symbol.setPixmap(
                pictures.pixmap(artwork.art_symbol(name), p["heading"], 30, 2.0)
            )
            top.addWidget(symbol)
            words = QVBoxLayout()
            words.setSpacing(0)
            words.addWidget(text(name, p["foreground"], serif(13.5, italic=True)))
            words.addWidget(
                text(f"{pawns} {'pawn' if pawns == 1 else 'pawns'}", p["label"])
            )
            top.addLayout(words, 1)
            top.addWidget(text(str(pawns), p["heading"], serif(20, bold=True)))
            card.column.addLayout(top)
            card.clicked = lambda index=index, name=name: self.inspect(
                f"{name} vis",
                "Raw Vis",
                labs.raw_vis_info_text(lab, index),
                artwork.art_symbol(name),
            )
            phials.append(card)
        connections = []
        for index, connection in enumerate(lab.arcane_connections):
            card = ClickableCard(p, pad=10)
            card.column.addWidget(
                text(connection.to, p["foreground"], serif(13, bold=True))
            )
            card.column.addWidget(
                text(labs.connection_state(connection).capitalize(), p["label"])
            )
            card.clicked = lambda index=index, to=connection.to: self.inspect(
                f"Arcane Connection to {to}", "", labs.connection_info_text(lab, index)
            )
            connections.append(card)
        books = bk.books_owned_by(saga, "laboratory", lab.id)
        book_cards = []
        for book in books:
            card = ClickableCard(p, pad=10)
            card.column.addWidget(
                text(book.name, p["foreground"], serif(13, bold=True), wrap=True)
            )
            card.clicked = lambda book=book: self.inspect(
                book.name, "", bk.detail_text(saga, book)
            )
            book_cards.append(card)
        none = "None recorded."
        return scrolling_page(
            chapter_title("Raw Vis", p),
            card_grid(phials, 4)
            if phials
            else text(none, p["dim"], serif(12.5, italic=True)),
            chapter_title(f"Equipment & Stores ({len(lab.inventory_items)})", p),
            self._named_cards(lab.inventory_items, "an item"),
            chapter_title(f"Arcane Connections ({len(connections)})", p),
            card_grid(connections, 3)
            if connections
            else text(none, p["dim"], serif(12.5, italic=True)),
            chapter_title(f"Books ({len(books)})", p),
            card_grid(book_cards, 3)
            if book_cards
            else text(none, p["dim"], serif(12.5, italic=True)),
        )

    def _seasons(self) -> QWidget:
        p, saga, lab = self.p, self.saga, self.lab
        self.calendar = Calendar(
            ov.calendar_rows(saga, ov.lab_seasons(saga, lab)),
            p,
            lambda who, when, season: self.inspect(who, when, season_text(season)),
            who=lab.name,
            current=(saga.current_season, saga.current_year),
        )
        entries = []
        for index, entry in enumerate(lab.diary):
            card = ClickableCard(p, pad=8)
            card.column.addWidget(
                text(
                    f"{entry.season} {entry.year}  ·  {entry.activity or '—'}",
                    p["label"],
                    serif(11, caps=True),
                )
            )
            if entry.name:
                card.column.addWidget(text(entry.name, p["foreground"], serif(13)))
            card.clicked = lambda index=index: self.inspect(
                "Diary", "", labs.diary_info_text(lab.diary, index)
            )
            entries.append(card)
        return scrolling_page(
            chapter_title("Seasons", p),
            legend(p),
            self.calendar,
            chapter_title(f"Diary ({len(lab.diary)})", p),
            card_grid(list(reversed(entries)), 2)
            if entries
            else text("Nothing written yet.", p["dim"], serif(12.5, italic=True)),
        )


_GAP = re.compile(r"\s{2,}")


def _markup(words: str, p: Palette) -> QWidget:
    """The core's text padded into two columns with spaces, as a grid,
    since the page's proportional type can't line them up."""
    box = QWidget()
    grid = QGridLayout(box)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(14)
    grid.setVerticalSpacing(1)
    for row, line in enumerate(words.splitlines()):
        cells = _GAP.split(line.strip(), maxsplit=1)
        if len(cells) == 2:
            name = TextBlock(cells[0], p)
            name.setWordWrap(False)
            grid.addWidget(name, row, 0)
            grid.addWidget(TextBlock(cells[1], p), row, 1)
        else:
            grid.addWidget(TextBlock(line or " ", p), row, 0, 1, 2)
    grid.setColumnStretch(1, 1)
    return box


def _first_line(words: str) -> str:
    line = words.strip().splitlines()[0] if words.strip() else ""
    return line if len(line) <= 90 else line[:87] + "…"
