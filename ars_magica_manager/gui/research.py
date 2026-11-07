"""A magus's Research chapter, set like a page of a book: each goal on
its own card with the road of its research drawn as a line of roundels,
the Research Log as a ruled ledger, and the season chosen from it shown
on the Extraordinary Results chart, its band picked out in rubric.

The words come from the core (research_text); only the roundels and the
chart are drawn here, in the palette's gilt and inks.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QHBoxLayout, QWidget

from .. import research_text as rt
from .. import section_verbs
from ..commands import Command
from ..markup import escape
from ..models import Breakthrough, Character, ResearchAttempt, Saga
from ..rules import research
from .editing import Chooser, choose_cards, verb_buttons
from .style.ornaments import Headpiece
from .themes import Palette
from .widgets import (
    Card,
    ClickableCard,
    badge,
    mix,
    scrolling_page,
    serif,
    table_view,
    text,
)

#: How the chapter shows what was chosen: a title, a line under it and
#: the details (app markup), in the inspector.
Inspect = Callable[[str, str, str], None]


class StepPath(QWidget):
    """The road of a goal's research: a roundel for each step, joined by
    a gilt rule; the steps behind filled in green, the one it is on ringed
    in rubric, those ahead left open."""

    HEIGHT = 46

    def __init__(self, goal: Breakthrough, p: Palette) -> None:
        super().__init__()
        self.p = p
        self.current = research.step(goal)
        self.reached = goal.reached
        self.setFixedHeight(self.HEIGHT)
        self.setMinimumWidth(360)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        p, steps = self.p, research.STEPS
        # Each step has an equal share of the width, its roundel centred in
        # it, so the names at either end aren't cut.
        gap = self.width() / len(steps)
        cy, radius = 12.0, 7.0
        xs = [gap / 2 + i * gap for i in range(len(steps))]
        painter.setPen(QPen(QColor(p["accent"]), 1.4))
        painter.drawLine(QPointF(xs[0], cy), QPointF(xs[-1], cy))
        painter.setFont(serif(9, caps=True))
        for index, (x, name) in enumerate(zip(xs, steps, strict=True)):
            done = index < self.current or (self.reached and index <= self.current)
            here = index == self.current and not done
            if done:
                painter.setPen(QPen(QColor(p["accent"]), 1.2))
                painter.setBrush(QColor(p["text-success"]))
            elif here:
                painter.setPen(QPen(QColor(p["heading"]), 2.4))
                painter.setBrush(mix(p["heading"], p["background"], 0.75))
            else:
                painter.setPen(QPen(QColor(p["accent"]), 1.2))
                painter.setBrush(QColor(p["background"]))
            painter.drawEllipse(QPointF(x, cy), radius, radius)
            if here:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(p["heading"]))
                painter.drawEllipse(QPointF(x, cy), 2.6, 2.6)
            painter.setPen(
                QColor(
                    p["heading"] if here else p["foreground"] if done else p["label"]
                )
            )
            painter.drawText(
                QRectF(x - gap / 2, cy + radius + 3, gap, 16),
                Qt.AlignmentFlag.AlignCenter,
                name,
            )
        painter.end()


class ChartStrip(QWidget):
    """The Extraordinary Results chart as a ribbon of its bands, each with
    its rolls over its result; the band a roll landed in is filled in
    rubric, the harmful ones edged in red and the Discovery in green."""

    HEIGHT = 50

    def __init__(self, p: Palette, roll: int | None = None) -> None:
        super().__init__()
        self.p, self.roll = p, roll
        self.setFixedHeight(self.HEIGHT)
        self.setMinimumWidth(420)

    def show_roll(self, roll: int | None) -> None:
        self.roll = roll
        self.update()

    def paintEvent(self, _event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        p, bands = self.p, research.BANDS
        width = (self.width() - 2) / len(bands)
        for index, band in enumerate(bands):
            cell = QRectF(1 + index * width, 4, width - 3, self.HEIGHT - 12)
            landed = self.roll is not None and band.holds(max(self.roll, 0))
            edge = {
                "harm": p["text-error"],
                "discovery": p["text-success"],
            }.get(band.tone, p["rule"])
            painter.setPen(QPen(QColor(edge), 1.6 if landed else 1.0))
            painter.setBrush(
                QColor(p["heading"]) if landed else mix(p["surface"], edge, 0.12)
            )
            painter.drawRoundedRect(cell, 4, 4)
            ink = QColor(p["background"] if landed else p["foreground"])
            span = (
                f"{band.low}+"
                if band.high is None
                else str(band.low)
                if band.high == band.low
                else f"{band.low}–{band.high}"
            )
            painter.setPen(ink)
            painter.setFont(serif(11, bold=True))
            painter.drawText(
                cell.adjusted(0, 2, 0, -cell.height() / 2),
                Qt.AlignmentFlag.AlignCenter,
                span,
            )
            painter.setFont(serif(8.5, italic=True))
            painter.drawText(
                cell.adjusted(2, cell.height() / 2 - 2, -2, 0),
                Qt.AlignmentFlag.AlignCenter,
                rt.SHORT_LABELS.get(band.label, band.label),
            )
        painter.end()


def _goal_card(goal: Breakthrough, p: Palette) -> ClickableCard:
    card = ClickableCard(p, edge=p["accent"] if goal.reached else None)
    top = QHBoxLayout()
    top.setSpacing(8)
    top.addWidget(text(goal.name, p["heading"], serif(15, bold=True)), 1)
    top.addWidget(badge(goal.kind, p["accent"], p))
    card.column.addLayout(top)
    card.column.addWidget(
        text(
            f"{research.target_text(goal)} · {research.stage(goal).value}",
            p["label"],
            serif(11.5, italic=True),
            wrap=True,
        )
    )
    card.column.addWidget(StepPath(goal, p))
    return card


class RollCard(Card):
    """The season chosen from the log: its roll, set over the chart."""

    def __init__(self, p: Palette) -> None:
        super().__init__(p)
        self.p = p
        self.title = text(
            "Choose a season of the log to see its roll.",
            p["label"],
            serif(12.5, italic=True),
            wrap=True,
        )
        self.column.addWidget(self.title)
        self.chart = ChartStrip(p)
        self.column.addWidget(self.chart)

    def show_attempt(self, goal: Breakthrough, attempt: ResearchAttempt) -> None:
        landed = rt.landed(attempt)
        if landed is None:
            words = "No roll on the chart this season."
        else:
            roll = landed - attempt.move
            words = f"Die {attempt.die} + risk {attempt.risk} = {roll}"
            if attempt.move:
                words += f", moved {attempt.move:+d} to {landed}"
        self.title.setText(f"{attempt.season} {attempt.year}, {goal.name}: {words}")
        self.title.setStyleSheet(f"color:{self.p['foreground']}")
        self.chart.show_roll(landed)


def research_chapter(
    saga: Saga,
    character: Character,
    p: Palette,
    run: Callable[[Command], None] | None,
    inspect: Inspect,
    *,
    only: Sequence[Breakthrough] | None = None,
) -> QWidget:
    """The Research chapter: the goals as cards, the log as a ledger and
    the chosen season's roll on the chart. With `only`, just those goals,
    read only (a laboratory's view of its owner's research under way);
    with `run`, the goals can be added, edited and deleted."""
    # cycle: character_sheet builds this chapter.
    from .character_sheet import TextBlock, section

    shown = list(character.breakthroughs if only is None else only)
    goals = Chooser()
    cards = [_goal_card(goal, p) for goal in shown]
    for card, goal in zip(cards, shown, strict=True):

        def show_goal(goal: Breakthrough = goal) -> None:
            inspect(
                goal.name,
                rt.goal_line(goal),
                rt.goal_panel(saga, character, goal),
            )

        card.clicked = show_goal
    choose_cards(cards, goals)
    goal_body: list[QWidget] = (
        list(cards) if cards else [TextBlock("[dim]None recorded.[/]", p)]
    )

    roll = RollCard(p)
    entries = rt.log_entries(character, shown)

    def show_attempt(index: int) -> None:
        goal, attempt = entries[index]
        roll.show_attempt(goal, attempt)
        inspect(
            f"{attempt.season} {attempt.year}",
            escape(goal.name),
            rt.attempt_panel(goal, attempt, strip=False),
        )

    log: list[QWidget] = (
        [table_view(rt.log_table(character, shown), p, show_attempt), roll]
        if entries
        else [TextBlock("[dim]No season spent on research yet.[/]", p)]
    )
    title = (
        f"Research Goals ({len(shown)})"
        if only is None
        else f"{character.name}'s research under way"
    )
    return scrolling_page(
        p,
        Headpiece(p),
        section(
            title,
            p,
            *goal_body,
            buttons=(
                verb_buttons(
                    section_verbs.ops_of(saga, character)[
                        section_verbs.RESEARCH_GOALS_SECTION
                    ],
                    goals,
                    run,
                    p,
                )
                if run is not None
                else ()
            ),
        ),
        section(f"Research Log ({len(entries)})", p, *log),
    )
