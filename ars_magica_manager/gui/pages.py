"""The pages at the top, in the Codex's style: the shelf of sagas and a
saga's covenants, and the cards and headings the pages below them share
(the covenant's is covenant.py), such as a familiar's card.

Each is cards and headings over the core's figures (saga_overview);
choosing a card calls back to the window, which opens the next page.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .. import artwork
from .. import character_sheet as cs
from .. import familiar_sheet as fs
from .. import saga_content_sheet as scs
from .. import saga_overview as ov
from ..models import Saga
from . import pictures
from .figures import fact_grid
from .themes import Palette
from .widgets import (
    ClickableCard,
    chapter_title,
    display_name,
    edit_button,
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


def card_title(
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


def symbol_label(path, p: Palette, size: int = 36) -> QLabel:
    label = QLabel()
    label.setPixmap(pictures.pixmap(path, p["heading"], size, 2.0))
    return label


def familiar_card(
    figures: fs.FamiliarCard, p: Palette, open_familiar: Open
) -> ClickableCard:
    """A familiar as a card that opens its page."""
    card = ClickableCard(p, pad=12)
    card_title(
        card,
        figures.name,
        figures.subtitle,
        p,
        symbol_label(artwork.icon("familiar"), p, 32),
    )
    card.column.addWidget(text(figures.detail, p["label"]))
    card.clicked = lambda: open_familiar(figures.id)
    return card


class SagaShelf(QWidget):
    """Every saga as a card; choosing one opens it. Above them, New Saga
    and Change Save Folder with the folder the saves are in; each card has
    a Delete."""

    def __init__(
        self,
        sagas: Sequence[Saga],
        p: Palette,
        open_saga: Open,
        new_saga: Callable[[], None] = lambda: None,
        delete_saga: Open = lambda _saga_id: None,
        change_folder: Callable[[], None] = lambda: None,
        folder: str = "",
    ) -> None:
        super().__init__()
        cards = []
        for saga in sagas:
            figures = ov.saga_card(saga)
            card = ClickableCard(p, pad=16)
            card_title(
                card,
                figures.name,
                figures.subtitle,
                p,
                symbol_label(artwork.icon("saga"), p),
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
            delete = edit_button(
                "Delete",
                p,
                lambda _checked=False, saga_id=figures.id: delete_saga(saga_id),
                "delete",
            )
            card.column.addWidget(delete, 0, Qt.AlignmentFlag.AlignRight)
            card.clicked = lambda saga_id=figures.id: open_saga(saga_id)
            cards.append(card)
        self.new_saga = edit_button("New Saga", p, new_saga, "add")
        self.change_folder = edit_button("Change Save Folder", p, change_folder, "edit")
        buttons = QHBoxLayout()
        buttons.setContentsMargins(0, 0, 0, 0)
        buttons.addWidget(self.new_saga)
        buttons.addWidget(self.change_folder)
        buttons.addStretch(1)
        actions = QWidget()
        actions.setLayout(buttons)
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.addWidget(
            scrolling_page(
                p,
                page_header(
                    "Sagas",
                    "Choose a saga to open"
                    + (f" · the saves are in {folder}" if folder else ""),
                    p,
                    "saga",
                ),
                actions,
                card_grid(cards)
                if cards
                else text(
                    "No sagas yet: New Saga starts one.",
                    p["dim"],
                    serif(13, italic=True),
                ),
            )
        )


class SagaPage(QWidget):
    """A saga's covenants as cards, with anyone who belongs to none, and
    a card that opens its Saga Content."""

    def __init__(
        self,
        saga: Saga,
        p: Palette,
        open_covenant: Callable[[str | None], None],
        open_content: Callable[[], None] = lambda: None,
        open_seasons: Callable[[], None] = lambda: None,
    ) -> None:
        super().__init__()
        cards = []
        for figures in ov.covenant_cards(saga):
            card = ClickableCard(p, pad=16)
            card_title(
                card,
                figures.name,
                figures.subtitle,
                p,
                symbol_label(artwork.icon("covenant"), p),
            )
            card.column.addWidget(fact_grid(list(figures.facts), p, 5))
            card.clicked = lambda covenant_id=figures.id: open_covenant(covenant_id)
            cards.append(card)
        content = ClickableCard(p, pad=16)
        card_title(
            content,
            "Saga Content",
            "The books in play, catalogs, House Rules and spells",
            p,
            symbol_label(artwork.icon("library"), p),
        )
        content.column.addWidget(fact_grid(scs.header_facts(saga), p, 4))
        content.clicked = open_content
        self.content = content
        kept = len(saga.season_records)
        past = ClickableCard(p, pad=16)
        card_title(
            past,
            "Seasons",
            f"It is {saga.current_season} {saga.current_year}; the seasons "
            "played out, and what each gave",
            p,
            symbol_label(artwork.icon("season"), p),
        )
        past.column.addWidget(fact_grid([cs.Fact("Recorded", str(kept))], p, 4))
        past.clicked = open_seasons
        self.seasons = past
        parts: list[QWidget] = [
            page_header(saga.name, ov.saga_card(saga).subtitle, p, "saga"),
            chapter_title("Covenants", p),
            card_grid(cards, 2),
            chapter_title("The Saga's Books, Rules and Seasons", p),
            card_grid([content, past], 2),
        ]
        if saga.description:
            parts.insert(
                1, text(saga.description, p["foreground"], serif(13), wrap=True)
            )
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.addWidget(scrolling_page(p, *parts))
