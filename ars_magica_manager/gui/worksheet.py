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

from collections.abc import Callable

from PySide6.QtWidgets import QVBoxLayout, QWidget

from .. import worksheet as ws
from .. import worksheet_forms as wf
from ..commands import Command, SectionOps
from ..markup import escape
from ..rules import creation as rules
from ..tables import Table
from .character_sheet import TextBlock, is_aligned, label_values, section
from .editing import Chooser, Run, verb_buttons
from .markup_html import plain
from .pages import page_header
from .themes import Palette
from .widgets import Codex, edit_button, scrolling_page, table_view

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
        shown: list[QWidget] = [budget_view(budget, p)] if budget else []
        if panel.list is not None:
            parts.append(self._list(step, panel.list, shown))
        elif shown:
            parts.append(section(step.title, p, *shown))
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
