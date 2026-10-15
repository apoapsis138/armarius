"""The pages at the top, in the Codex's style: the shelf of sagas and a
saga's covenants, and the cards and headings the pages below them share
(the covenant's is covenant.py), such as a familiar's card.

Each is cards and headings over the core's figures (saga_overview);
choosing a card calls back to the window, which opens the next page.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .. import artwork, menu_forms, tribunal_sheet
from .. import character_sheet as cs
from .. import familiar_sheet as fs
from .. import saga_content_sheet as scs
from .. import saga_overview as ov
from ..models import Character, Saga
from . import pictures
from .figures import fact_grid
from .menus import Placer
from .themes import Palette
from .widgets import (
    ClickableCard,
    Codex,
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


def person_card(saga: Saga, character: Character, p: Palette, open_: Open) -> QWidget:
    """A person as a card, with their House's symbol, that opens their
    sheet."""
    figures = ov.person_card(saga, character)
    house = artwork.house_symbol(figures.house)
    card = ClickableCard(p, pad=12)
    card_title(
        card,
        figures.name,
        figures.subtitle,
        p,
        symbol_label(house, p, 40)
        if house
        else symbol_label(artwork.icon("character"), p, 32),
    )
    if figures.detail:
        card.column.addWidget(text(figures.detail, p["label"]))
    card.clicked = lambda: open_(figures.id)
    return card


def lab_card(figures: ov.LabCard, p: Palette, open_: Open) -> QWidget:
    """A laboratory as a card with its main figures, that opens it."""
    card = ClickableCard(p, pad=14)
    card_title(
        card,
        figures.name,
        figures.subtitle,
        p,
        symbol_label(artwork.icon("laboratory"), p),
    )
    card.column.addWidget(fact_grid(list(figures.facts), p, 4))
    card.clicked = lambda: open_(figures.id)
    return card


def with_new(cards: list[QWidget], new: QWidget | None) -> list[QWidget]:
    """`cards`, then the New card that adds to them, if there is one."""
    return [*cards, new] if new is not None else cards


def action_rows(rows: Sequence[tuple[QWidget, str]], p: Palette) -> QWidget:
    """Each button beside a line on what it does."""
    box = QWidget()
    grid = QGridLayout(box)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(16)
    grid.setVerticalSpacing(14)
    grid.setColumnStretch(1, 1)
    for row, (button, detail) in enumerate(rows):
        grid.addWidget(button, row, 0, Qt.AlignmentFlag.AlignTop)
        grid.addWidget(
            text(detail, p["label"], serif(12.5, italic=True), wrap=True), row, 1
        )
    return box


class SagaPage(QWidget):
    """A saga as a Codex: The World (its covenants, and the characters and
    laboratories that belong to none, each list ending in a New card),
    its Seasons, its Rules and Content, and Saga Management."""

    def __init__(
        self,
        saga: Saga,
        p: Palette,
        open_covenant: Callable[[str | None], None],
        open_content: Callable[[], None] = lambda: None,
        open_seasons: Callable[[], None] = lambda: None,
        placer: Placer | None = None,
        open_character: Open = lambda _id: None,
        open_laboratory: Open = lambda _id: None,
        open_tribunal: Open = lambda _id: None,
    ) -> None:
        super().__init__()
        self.saga, self.p = saga, p
        self.open_tribunal = open_tribunal
        self.placer = placer
        self.open_covenant = open_covenant
        self.open_character, self.open_laboratory = open_character, open_laboratory
        column = QVBoxLayout(self)
        column.setContentsMargins(18, 12, 12, 8)
        column.setSpacing(10)
        column.addWidget(page_header(saga.name, ov.saga_card(saga).subtitle, p, "saga"))
        if saga.description:
            column.addWidget(
                text(saga.description, p["foreground"], serif(13), wrap=True)
            )
        self.codex = Codex(p)
        self.codex.add("The World", "covenant", self._world())
        self.codex.add("Seasons", "season", self._seasons(open_seasons))
        self.codex.add(
            "Rules and Content", "library", self._rules_and_content(open_content)
        )
        self.codex.add("Saga Management", "manage", self._management())
        column.addWidget(self.codex, 1)

    def chapters(self) -> list[str]:
        return self.codex.chapters()

    def _new(self, spot: str, hint: str = "") -> QWidget | None:
        return self.placer.new_card(spot, hint=hint) if self.placer else None

    def _buttons(self, spot: str) -> list[QPushButton]:
        return self.placer.buttons(spot) if self.placer else []

    def _world(self) -> QWidget:
        p, saga = self.p, self.saga
        covenants: list[QWidget] = []
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
            card.clicked = lambda covenant_id=figures.id: self.open_covenant(
                covenant_id
            )
            covenants.append(card)
        courts: list[QWidget] = []
        for tribunal in saga.tribunals:
            card = ClickableCard(p, pad=16)
            card_title(
                card,
                tribunal.name,
                f"Next meeting: {tribunal_sheet.next_meeting(tribunal)}",
                p,
                symbol_label(artwork.icon("tribunal"), p),
            )
            card.column.addWidget(
                fact_grid(tribunal_sheet.facts(saga, tribunal)[5:], p, 3)
            )
            card.clicked = lambda tribunal_id=tribunal.id: self.open_tribunal(
                tribunal_id
            )
            courts.append(card)
        people = [
            person_card(saga, c, p, self.open_character) for c in ov.members(saga, None)
        ]
        labs = [lab_card(f, p, self.open_laboratory) for f in ov.lab_cards(saga, None)]
        parts: list[QWidget] = []
        for title, cards, across in (
            ("Covenants", covenants, 2),
            ("Tribunals", courts, 2),
            ("Unassigned Characters", people, CARDS_ACROSS),
            ("Unassigned Laboratories", labs, 2),
        ):
            listed = with_new(cards, self._new(title))
            parts.append(chapter_title(f"{title} ({len(cards)})", p))
            parts.append(
                card_grid(listed, across)
                if listed
                else text("None.", p["dim"], serif(12.5, italic=True))
            )
        return scrolling_page(p, *parts)

    def _seasons(self, open_seasons: Callable[[], None]) -> QWidget:
        p, saga = self.p, self.saga
        kept = len(saga.season_records)
        past = ClickableCard(p, pad=16)
        card_title(
            past,
            "The Seasons Played",
            "What everyone did each season, and what it gave them",
            p,
            symbol_label(artwork.icon("season"), p),
        )
        past.column.addWidget(fact_grid([cs.Fact("Recorded", str(kept))], p, 4))
        past.clicked = open_seasons
        self.seasons = past
        heading = QWidget()
        row = QHBoxLayout(heading)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        row.addWidget(chapter_title("The Date", p), 1)
        for button in self._buttons("Seasons"):
            row.addWidget(button, 0, Qt.AlignmentFlag.AlignTop)
        return scrolling_page(
            p,
            heading,
            text(
                f"It is {saga.current_season} {saga.current_year}. Advance Season, "
                "at the top of the window, plays the season out.",
                p["foreground"],
                serif(13),
                wrap=True,
            ),
            chapter_title("Records", p),
            card_grid([past], 2),
        )

    def _rules_and_content(self, open_content: Callable[[], None]) -> QWidget:
        p, saga = self.p, self.saga
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
        return scrolling_page(
            p, chapter_title("Rules and Content", p), card_grid([content], 2)
        )

    def _management(self) -> QWidget:
        p = self.p
        placed = self.placer.placed_buttons("Saga Management") if self.placer else []
        rows = [
            (button, menu_forms.SAGA_MANAGEMENT.get(item.action, ""))
            for item, button in placed
        ]
        return scrolling_page(
            p,
            chapter_title("Saga Management", p),
            action_rows(rows, p)
            if rows
            else text("Nothing to manage.", p["dim"], serif(12.5, italic=True)),
        )
