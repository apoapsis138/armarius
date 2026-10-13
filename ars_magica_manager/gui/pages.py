"""The pages above a character's sheet, in the Codex's style: the shelf
of sagas, a saga's covenants, and a covenant with its people,
laboratories and seasons.

Each is cards and headings over the core's figures (saga_overview);
choosing a card calls back to the window, which opens the next page.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .. import artwork
from .. import character_sheet as cs
from .. import saga_overview as ov
from ..models import Saga
from . import pictures
from .figures import fact_grid
from .themes import Palette
from .timeline import SeasonTimeline, legend, season_text
from .widgets import (
    ClickableCard,
    Codex,
    chapter_title,
    display_name,
    scrolling_page,
    serif,
    text,
)

#: How many cards a row holds.
CARDS_ACROSS = 3

Open = Callable[[str], None]


def card_grid(cards: Sequence[QWidget], across: int = CARDS_ACROSS) -> QWidget:
    box = QWidget()
    grid = QGridLayout(box)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setSpacing(14)
    for i, card in enumerate(cards):
        grid.addWidget(card, i // across, i % across)
    for column in range(across):
        grid.setColumnStretch(column, 1)
    return box


def page_header(
    title: str, subtitle: str, p: Palette, concept: str | None = None
) -> QWidget:
    """A page's title: an icon, the name with a rubricated initial and the
    line under it, as the Character sheet opens."""
    box = QWidget()
    row = QHBoxLayout(box)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(14)
    if concept is not None:
        symbol = QLabel()
        symbol.setPixmap(pictures.pixmap(artwork.icon(concept), p["heading"], 48, 2.0))
        row.addWidget(symbol, 0, Qt.AlignmentFlag.AlignTop)
    names = QVBoxLayout()
    names.setSpacing(0)
    names.addWidget(display_name(title, p))
    if subtitle:
        names.addWidget(text(subtitle, p["label"], serif(12.5, italic=True)))
    row.addLayout(names)
    row.addStretch(1)
    return box


def _card_title(
    card: ClickableCard, title: str, subtitle: str, p: Palette, symbol: QLabel | None
) -> None:
    top = QHBoxLayout()
    top.setSpacing(10)
    if symbol is not None:
        top.addWidget(symbol, 0, Qt.AlignmentFlag.AlignTop)
    names = QVBoxLayout()
    names.setSpacing(0)
    names.addWidget(text(title, p["foreground"], serif(16, bold=True), wrap=True))
    if subtitle:
        names.addWidget(text(subtitle, p["label"], serif(11.5, italic=True), wrap=True))
    top.addLayout(names, 1)
    card.column.addLayout(top)


def _symbol(path, p: Palette, size: int = 36) -> QLabel:
    label = QLabel()
    label.setPixmap(pictures.pixmap(path, p["heading"], size, 2.0))
    return label


class SagaShelf(QWidget):
    """Every saga as a card; choosing one opens it."""

    def __init__(self, sagas: Sequence[Saga], p: Palette, open_saga: Open) -> None:
        super().__init__()
        cards = []
        for saga in sagas:
            figures = ov.saga_card(saga)
            card = ClickableCard(p, pad=16)
            _card_title(
                card,
                figures.name,
                figures.subtitle,
                p,
                _symbol(artwork.icon("saga"), p),
            )
            card.column.addWidget(
                fact_grid(
                    [
                        cs.Fact("Covenants", str(figures.covenants)),
                        cs.Fact("Characters", str(figures.characters)),
                    ],
                    p,
                    2,
                )
            )
            card.clicked = lambda saga_id=figures.id: open_saga(saga_id)
            cards.append(card)
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.addWidget(
            scrolling_page(
                page_header("Sagas", "Choose a saga to open", p, "saga"),
                card_grid(cards)
                if cards
                else text("No sagas yet.", p["dim"], serif(13, italic=True)),
            )
        )


class SagaPage(QWidget):
    """A saga's covenants as cards, with anyone who belongs to none."""

    def __init__(
        self, saga: Saga, p: Palette, open_covenant: Callable[[str | None], None]
    ) -> None:
        super().__init__()
        cards = []
        for figures in ov.covenant_cards(saga):
            card = ClickableCard(p, pad=16)
            _card_title(
                card,
                figures.name,
                figures.subtitle,
                p,
                _symbol(artwork.icon("covenant"), p),
            )
            card.column.addWidget(fact_grid(list(figures.facts), p, 5))
            card.clicked = lambda covenant_id=figures.id: open_covenant(covenant_id)
            cards.append(card)
        parts: list[QWidget] = [
            page_header(saga.name, ov.saga_card(saga).subtitle, p, "saga"),
            chapter_title("Covenants", p),
            card_grid(cards, 2),
        ]
        if saga.description:
            parts.insert(
                1, text(saga.description, p["foreground"], serif(13), wrap=True)
            )
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.addWidget(scrolling_page(*parts))


class CovenantPage(QWidget):
    """A covenant in the Codex layout: its people as cards, its
    laboratories, and the timeline of everyone's seasons. Choosing a
    person or a laboratory opens their page."""

    def __init__(
        self,
        saga: Saga,
        covenant_id: str | None,
        p: Palette,
        open_character: Open,
        open_laboratory: Open,
    ) -> None:
        super().__init__()
        self.saga, self.p = saga, p
        self.open_laboratory = open_laboratory
        covenant = saga.covenant(covenant_id)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 12, 12, 8)
        outer.setSpacing(10)
        outer.addWidget(
            page_header(
                covenant.name if covenant else "Unassigned",
                ov.covenant_subtitle(covenant)
                if covenant
                else "Characters who belong to no covenant",
                p,
                "covenant",
            )
        )
        self.codex = Codex(p)
        self.codex.add("People", "character", self._people(covenant_id, open_character))
        labs = ov.lab_cards(saga, covenant_id)
        if covenant is not None or labs:
            self.codex.add("Laboratories", "laboratory", self._labs(labs))
        self.codex.add("Seasons", "season", self._seasons(covenant_id))
        outer.addWidget(self.codex, 1)

    def _people(self, covenant_id: str | None, open_character: Open) -> QWidget:
        p, saga = self.p, self.saga
        parts: list[QWidget] = []
        for title, people in ov.people_groups(saga, covenant_id):
            cards = []
            for character in people:
                figures = ov.person_card(saga, character)
                house = artwork.house_symbol(figures.house)
                card = ClickableCard(p, pad=12)
                _card_title(
                    card,
                    figures.name,
                    figures.subtitle,
                    p,
                    _symbol(house, p, 40)
                    if house
                    else _symbol(artwork.icon("character"), p, 32),
                )
                if figures.detail:
                    card.column.addWidget(text(figures.detail, p["label"]))
                card.clicked = lambda character_id=figures.id: open_character(
                    character_id
                )
                cards.append(card)
            parts += [chapter_title(f"{title} ({len(people)})", p), card_grid(cards)]
        if not parts:
            parts.append(text("No one yet.", p["dim"], serif(13, italic=True)))
        return scrolling_page(*parts)

    def _labs(self, labs: Sequence[ov.LabCard]) -> QWidget:
        p = self.p
        cards = []
        for figures in labs:
            card = ClickableCard(p, pad=14)
            _card_title(
                card,
                figures.name,
                figures.subtitle,
                p,
                _symbol(artwork.icon("laboratory"), p),
            )
            card.column.addWidget(fact_grid(list(figures.facts), p, 4))
            card.clicked = lambda lab_id=figures.id: self.open_laboratory(lab_id)
            cards.append(card)
        return scrolling_page(
            chapter_title(f"Laboratories ({len(labs)})", p),
            card_grid(cards, 2)
            if cards
            else text("No laboratories yet.", p["dim"], serif(13, italic=True)),
        )

    def _seasons(self, covenant_id: str | None) -> QWidget:
        p, saga = self.p, self.saga
        people = [
            c for _title, group in ov.people_groups(saga, covenant_id) for c in group
        ]
        self.timeline = SeasonTimeline(
            ov.timeline(saga, people),
            p,
            lambda name, when, season: self.codex.inspect(
                name, when, season_text(season)
            ),
        )
        return scrolling_page(
            chapter_title(
                f"Seasons  ·  now {saga.current_season} {saga.current_year}", p
            ),
            legend(p),
            self.timeline,
        )
