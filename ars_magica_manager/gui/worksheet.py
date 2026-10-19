"""The desktop Creation Worksheet: a covenant, laboratory or character In
Creation, walked through the book's steps.

It is a Codex: the rail lists the steps, each marked with how its
creation checks stand; the chapter shows the chosen step (its budget and
what's spent, its list with Add, Edit and Delete for the row clicked, its
checks and its buttons); the inspector shows the row clicked. The last
step ends with Move to In Play. What every step shows and does comes from
the core (worksheet.py), as the terminal's worksheet does; its buttons
run the core's commands through the window, which saves the saga and
draws the page again at the same step.
"""

from __future__ import annotations

import html
from collections.abc import Callable

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget

from .. import worksheet as ws
from .. import worksheet_feedback as feedback
from ..commands import Command, SectionOps
from ..forms import worksheet as wf
from ..markup import escape
from ..models import Character
from ..rules import creation as rules
from ..tables import Table
from .character_sheet import TextBlock, is_aligned, label_values, section
from .editing import Chooser, Run, verb_buttons
from .markup_html import plain
from .pages import page_header
from .themes import Palette
from .widgets import Codex, edit_button, scrolling_page, serif, table_view

#: The record kinds' icons (artwork.ICON_NAMES).
_ICONS = {"character": "character", "covenant": "covenant", "laboratory": "laboratory"}


class WorksheetPage(QWidget):
    """The worksheet for `record`. `played` is called once Move to In Play
    has moved it (to leave the worksheet for the record's page)."""

    def __init__(
        self,
        saga,
        record: wf.Record,
        palette: Palette,
        run: Run = lambda _command: None,
        played: Callable[[Command], None] | None = None,
    ) -> None:
        super().__init__()
        self.saga, self.record, self.p = saga, record, palette
        self.run = run
        self.played = played or run
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 12, 12, 8)
        outer.setSpacing(10)
        mode = "In Creation" if record.in_creation else "In Play"
        outer.addWidget(
            page_header(
                record.name,
                f"Creation Worksheet · {mode} · "
                + plain(ws.progress_text(saga, record)).replace("\n", " · "),
                palette,
                _ICONS.get(ws.record_kind(record)),
            )
        )
        self.broken = broken_line(saga, record, palette, self.open_step)
        outer.addWidget(self.broken)
        self.codex = Codex(palette)
        self.codex.inspect(
            "Creation Worksheet",
            "",
            "[dim]Choose a row of a step's list to see it here.[/]",
        )
        self.steps = rules.steps_for(record)
        for step in self.steps:
            self.codex.add(
                plain(ws.step_label(saga, record, step)), "lab_text", self._step(step)
            )
        outer.addWidget(self.codex, 1)

    def chapters(self) -> list[str]:
        return self.codex.chapters()

    def open_step(self, key: str) -> None:
        """Show the step `key` (rules.creation's step keys)."""
        self.codex.rail.setCurrentRow([s.key for s in self.steps].index(key))

    def _step(self, step: rules.Step) -> QWidget:
        saga, record, p = self.saga, self.record, self.p
        panel = ws.panel_for(record, step.key)
        parts: list[QWidget] = []
        budget = panel.budget(saga, record)
        shown: list[QWidget] = [
            MeterBar(meter, p) for meter in feedback.meters(saga, record, step.key)
        ]
        if budget:
            shown.append(budget_view(budget, p))
        if panel.list is not None:
            parts.append(self._list(step, panel.list, shown))
        elif shown:
            parts.append(section(step.title, p, *shown))
        if feedback.shows_ledger(record, step.key):
            assert isinstance(record, Character)
            table = feedback.ledger(record, step.key)
            parts.append(
                section(
                    "Experience So Far",
                    p,
                    table_view(table, p, lambda _row: None)
                    if table.rows
                    else TextBlock("[dim]No experience spent yet.[/]", p),
                )
            )
        found = rules.checks(saga, record, step.key)
        parts.append(section("Creation Checks", p, TextBlock(ws.check_lines(found), p)))
        buttons = [
            edit_button(
                action.label,
                p,
                lambda start=action.start: self.run(start()),
                "edit",
            )
            for action in panel.actions(saga, record)
        ]
        if step is self.steps[-1]:
            buttons.append(
                edit_button(
                    "Move to In Play",
                    p,
                    lambda: self.played(wf.move_to_play(saga, record)),
                    "saga",
                )
            )
        if buttons:
            holder = QWidget()
            column = QVBoxLayout(holder)
            column.setContentsMargins(0, 0, 0, 0)
            column.setSpacing(4)
            for button in buttons:
                column.addWidget(button)
            column.addStretch(1)
            parts.append(section("This Step", p, holder))
        return scrolling_page(p, *parts)

    def _list(
        self, step: rules.Step, step_list: ws.StepList, above: list[QWidget]
    ) -> QWidget:
        """The step's list under `above` (its budget), with Add, and Edit
        and Delete for the row clicked (greyed out on a row that can't
        take them)."""
        saga, record, p = self.saga, self.record, self.p
        rows = step_list.rows(saga, record)
        chooser = Chooser()
        add = step_list.add
        ops = SectionOps(
            add=(lambda: add(saga, record)) if add is not None else None,
            rows=lambda: [plain(row.label).strip().split("  ")[0] for row in rows],
        )

        def verb(which: str) -> Callable[[int], Command]:
            def start(index: int) -> Command:
                act = getattr(rows[index], which)
                assert act is not None
                return act()

            return start

        more = []
        if step_list.edit_label is not None:
            more.append(
                (
                    step_list.edit_label,
                    "edit",
                    verb("edit"),
                    lambda index: rows[index].edit is not None,
                )
            )
        more.append(
            (
                step_list.delete_label,
                "delete",
                verb("delete"),
                lambda index: rows[index].delete is not None,
            )
        )

        def show(index: int) -> None:
            chooser.choose(index)
            row = rows[index]
            name = (
                plain(row.cells[0]).strip()
                if row.cells
                else plain(row.label).strip().split("  ")[0]
            )
            self.codex.inspect(name, step.title, row.details or escape(name))

        table = Table(
            step_list.columns,
            [row.cells or [row.label] for row in rows],
            [None if row.heading else index for index, row in enumerate(rows)],
            markup=True,
        )
        body: QWidget = (
            table_view(table, p, show)
            if rows
            else TextBlock(f"[dim]{escape(step_list.hint)}[/]", p)
        )
        return section(
            step.title,
            p,
            *above,
            body,
            buttons=verb_buttons(
                ops,
                chooser,
                self.run,
                p,
                nouns=(step_list.add_label, "", ""),
                more=more,
            ),
        )


def budget_view(words: str, p: Palette) -> QWidget:
    """A step's budget: its `label: value` lines as a grid, the core's
    indented columns (a tally) in a fixed-pitch font so they line up, and
    any other line as text."""
    runs: list[tuple[str, list[str]]] = []
    for line in words.splitlines():
        kind = (
            "aligned"
            if is_aligned(line)
            else "columns"
            if line.startswith("  ")
            else "text"
        )
        if runs and runs[-1][0] == kind:
            runs[-1][1].append(line)
        else:
            runs.append((kind, [line]))
    parts = [
        label_values("\n".join(lines), p)
        if kind == "aligned"
        else TextBlock("\n".join(lines), p, mono=kind == "columns")
        for kind, lines in runs
    ]
    if len(parts) == 1:
        return parts[0]
    box = QWidget()
    column = QVBoxLayout(box)
    column.setContentsMargins(0, 0, 0, 0)
    column.setSpacing(4)
    for part in parts:
        column.addWidget(part)
    return box


class MeterBar(QWidget):
    """A step's budget as a bar that fills as it is spent: gold while some
    is left, red once it is over, with what it is and the sums beside it."""

    HEIGHT = 26

    def __init__(self, meter: feedback.Meter, p: Palette) -> None:
        super().__init__()
        self.meter, self.p = meter, p
        self.setFixedHeight(self.HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setToolTip(f"{meter.label}: {meter.words()}")

    def colour(self) -> str:
        return self.p["text-error"] if self.meter.over else self.p["accent"]

    def paintEvent(self, event) -> None:
        meter, p = self.meter, self.p
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        whole = QRectF(self.rect())
        label_width = min(220.0, whole.width() * 0.3)
        words_width = min(200.0, whole.width() * 0.3)
        track = QRectF(
            whole.left() + label_width,
            whole.center().y() - 6,
            whole.width() - label_width - words_width - 12,
            12,
        )
        painter.setFont(serif(12))
        painter.setPen(QColor(p["foreground"]))
        painter.drawText(
            QRectF(0, 0, label_width - 8, whole.height()),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            meter.label,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(p["panel"]))
        painter.drawRoundedRect(track, 6, 6)
        share = 1.0 if meter.total <= 0 else min(meter.spent / meter.total, 1.0)
        if meter.spent > 0:
            filled = QRectF(track)
            filled.setWidth(max(track.width() * share, track.height()))
            painter.setBrush(QColor(self.colour()))
            painter.drawRoundedRect(filled, 6, 6)
        painter.setPen(QColor(p["text-error"] if meter.over else p["label"]))
        painter.drawText(
            QRectF(track.right() + 12, 0, words_width, whole.height()),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            meter.words(),
        )
        painter.end()


def broken_line(
    saga, record: wf.Record, p: Palette, open_step: Callable[[str], None]
) -> QLabel:
    """One line naming each step with a broken creation rule and how many,
    each a link to that step (its rules in the tooltip); hidden while none
    is broken."""
    found = feedback.broken(saga, record)
    by_step: dict[str, list[feedback.Broken]] = {}
    for rule in found:
        by_step.setdefault(rule.step, []).append(rule)
    colour = p["text-error"]
    links = "  ·  ".join(
        f'<a href="{step}" style="color:{colour}">'
        f"{html.escape(rules[0].step_title)} ({len(rules)})</a>"
        for step, rules in by_step.items()
    )
    line = QLabel(f'<span style="color:{colour}">Rules broken: </span>{links}')
    line.setTextFormat(Qt.TextFormat.RichText)
    line.setWordWrap(True)
    line.setFont(serif(12.5, italic=True))
    line.setToolTip("\n".join(rule.words() for rule in found))
    line.linkActivated.connect(open_step)
    line.setVisible(bool(found))
    return line
