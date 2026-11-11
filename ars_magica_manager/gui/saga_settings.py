"""The saga page's Saga Settings chapter: every setting as a card under its
section's heading, each with its switch or its value at the upper right,
as Books in Play's cards have, and Content in Play's card, which opens
Saga Content. Clicking a card shows it in full in the
inspector, with a switch of its own. A switch changes the saga at once.

What it says comes from sheets/saga_settings.py and what it does from
forms/saga_settings.py.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .. import medallions
from ..forms import saga_settings as ssf
from ..models import Saga
from ..sheets import saga_settings as sss
from ..sheets.saga_settings import SettingCard
from .editing import Run
from .figures import fact_grid
from .medallions import Medallion
from .style.pieces import card_grid, chapter_title, scrolling_page, text
from .themes import Palette
from .widgets import ClickableCard, Codex, ToggleSwitch, chip_button, serif

#: Cards across a section, as on Books in Play.
ACROSS = 3
#: How large the Inspector draws each set of medallions.
SAMPLE_RADIUS = 20


class SettingsChapter:
    """Builds the chapter, and keeps which card the inspector is showing."""

    #: The card last changed: shown again when the page is redrawn.
    reopen = ""

    def __init__(
        self,
        saga: Saga,
        p: Palette,
        codex: Codex,
        run: Run,
        buttons: Sequence[QPushButton],
        content_card: Callable[[], QWidget],
    ) -> None:
        self.saga, self.p, self.codex, self.run = saga, p, codex, run
        self.buttons = list(buttons)
        #: Builds Content in Play's card, Saga Content's (the saga page
        #: draws it, as it draws every card that opens a page).
        self.content_card = content_card
        self.cards: dict[str, ClickableCard] = {}

    def page(self) -> QWidget:
        p, saga = self.p, self.saga
        details = fact_grid(sss.facts(saga), p, 3)
        row = QWidget()
        along = QHBoxLayout(row)
        along.setContentsMargins(0, 0, 0, 0)
        for button in self.buttons:
            along.addWidget(button)
        along.addStretch(1)
        rules = QWidget()
        column = QVBoxLayout(rules)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(8)
        column.addWidget(
            text(sss.rules_lead(saga), p["label"], serif(12, italic=True), wrap=True)
        )
        for group in sss.rule_groups(saga):
            column.addWidget(
                text(group.heading, p["heading"], serif(13, caps=True, bold=True))
            )
            column.addWidget(self._grid(group.cards))
        chapter = scrolling_page(
            p,
            chapter_title(sss.THE_SAGA, p),
            details,
            row,
            chapter_title("Seasons", p),
            self._grid(sss.season_cards(saga)),
            chapter_title("Content in Play", p),
            card_grid([self.content_card()], 2),
            chapter_title("Optional Rules", p),
            rules,
            chapter_title("Tribunal", p),
            self._grid(sss.tribunal_cards(saga)),
        )
        again = SettingsChapter.reopen
        SettingsChapter.reopen = ""
        for card in self._all():
            if card.key == again:
                self._choose(card)
        return chapter

    def _all(self) -> list[SettingCard]:
        saga = self.saga
        rules = [c for group in sss.rule_groups(saga) for c in group.cards]
        return [*sss.season_cards(saga), *rules, *sss.tribunal_cards(saga)]

    def _grid(self, cards: list[SettingCard]) -> QWidget:
        return card_grid([self._card(card) for card in cards], ACROSS)

    def _change(self, card: SettingCard) -> None:
        SettingsChapter.reopen = card.key
        self.run(
            ssf.choice_form(self.saga, card.key)
            if card.choice
            else ssf.toggle_setting(self.saga, card.key)
        )

    def _control(self, card: SettingCard) -> QWidget:
        """`card`'s switch, or the chip that shows its value and changes it."""
        p = self.p
        if card.choice:
            chosen = chip_button(card.choice, p["accent"], lambda: self._change(card))
            chosen.setToolTip("Click to change it.")
            return chosen
        switch = ToggleSwitch(card.on, p, lambda: self._change(card))
        switch.setEnabled(card.usable)
        switch.setToolTip(
            card.refused
            or ("Click to turn it off." if card.on else "Click to turn it on.")
        )
        return switch

    def _card(self, card: SettingCard) -> ClickableCard:
        p = self.p
        lit = card.on or bool(card.choice)
        drawn = ClickableCard(p, pad=8, edge=p["text-success"] if lit else p["dim"])
        drawn.column.setSpacing(2)
        top = QHBoxLayout()
        top.addWidget(
            text(card.title, p["foreground"], serif(12.5, bold=True), wrap=True), 1
        )
        top.addWidget(self._control(card))
        drawn.column.addLayout(top)
        drawn.column.addWidget(
            text(card.summary, p["foreground"], serif(11.5), wrap=True)
        )
        if card.book:
            drawn.column.addWidget(
                text(card.book, p["label"], serif(11, italic=True), wrap=True)
            )
        drawn.column.addStretch(1)
        drawn.clicked = lambda: self._choose(card)
        if not card.usable:
            faded = QGraphicsOpacityEffect(drawn)
            faded.setOpacity(0.45)
            drawn.setGraphicsEffect(faded)
        self.cards[card.key] = drawn
        return drawn

    def _sets(self) -> QWidget:
        """Each set of medallions drawn, this season's, with what it is."""
        p, saga = self.p, self.saga
        sets = QWidget()
        column = QVBoxLayout(sets)
        column.setContentsMargins(0, 8, 0, 0)
        column.setSpacing(6)
        in_use = medallions.chosen(saga)
        for key, name, looks in medallions.SETS:
            row = QHBoxLayout()
            row.setSpacing(6)
            row.addWidget(
                Medallion(
                    saga,
                    saga.current_season,
                    saga.current_year,
                    p,
                    radius=SAMPLE_RADIUS,
                    drawn_as=key,
                )
            )
            words = QVBoxLayout()
            words.setSpacing(0)
            words.addStretch(1)
            words.addWidget(
                text(
                    f"{name} (in use)" if key == in_use else name,
                    p["heading" if key == in_use else "foreground"],
                    serif(12, bold=True),
                    wrap=True,
                )
            )
            words.addWidget(text(looks, p["label"], serif(11, italic=True), wrap=True))
            words.addStretch(1)
            row.addLayout(words, 1)
            column.addLayout(row)
        return sets

    def _choose(self, card: SettingCard) -> None:
        """Show `card` in the inspector and outline it."""
        for key, drawn in self.cards.items():
            drawn.set_chosen(key == card.key)
        self.codex.inspect(
            card.title,
            card.subtitle,
            card.detail,
            None,
            self._control(card),
            self._sets() if card.key == sss.MEDALLIONS else None,
        )
