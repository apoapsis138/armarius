"""The desktop's dialogs for the steps a sheet's buttons run
(commands.py): a form drawn from a list of form_spec.DialogFields, the
same lists the terminal's FieldsDialog draws, and checked with form_spec,
so both front-ends accept and refuse the same entries; a searchable list
to choose from; and a yes-or-no question.

A field's kind picks its widget: a line for text and numbers, a box for
multi-line text, a drop-down for a choice, a tick box for a check, and a
plain line for read-only information. A "picker" field, whose chooser is
a terminal screen, is shown read-only.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from .. import form_spec
from ..commands import Choice
from ..form_spec import DialogField, FieldError
from .markup_html import plain, to_html
from .ornaments import FleuronRule, corner_flourishes
from .paper import Paper
from .themes import Palette
from .widgets import serif, text

#: Field kinds the dialog reads as typed text, parsed by form_spec.
_LINE_KINDS = {"text", "secret", "int", "optint", "optfloat"}


def _shown_text(value: object) -> str:
    return "" if value is None else str(value)


class _Page(Paper):
    """A dialog's sheet of paper, with a flourish in each corner."""

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        corner_flourishes(QPainter(self), QRectF(self.rect()), self.p, 18)


class _Sheet(QDialog):
    """A dialog on paper: its title over a hedera rule, a body, an error
    line and its buttons (Cancel, then the action). `inline`: drawn in
    place on the page (editing.InPlace) rather than as a window, a smaller
    title with no rule, sized to its contents."""

    def __init__(
        self,
        title: str,
        p: Palette,
        action: str,
        parent: QWidget | None,
        *,
        inline: bool = False,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(plain(title))
        self.p, self.inline = p, inline
        if inline:
            self.setWindowFlags(Qt.WindowType.Widget)
            self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        page = _Page(p)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(page)
        self.column = QVBoxLayout(page)
        self.column.setSpacing(8)
        if inline:
            self.column.setContentsMargins(20, 14, 20, 14)
            self.column.addWidget(
                text(plain(title), p["heading"], serif(14, bold=True, caps=True))
            )
        else:
            self.column.setContentsMargins(26, 20, 26, 18)
            self.column.addWidget(
                text(plain(title), p["heading"], serif(17, bold=True))
            )
            self.column.addWidget(FleuronRule(p))
        self.error = text("", p["text-error"], serif(12, italic=True), wrap=True)
        self.error.hide()
        self.cancel = QPushButton("Cancel")
        self.cancel.clicked.connect(self.reject)
        self.save = QPushButton(action)
        self.save.setDefault(True)

    def finish(self) -> None:
        """Put the error line and the buttons under the body."""
        self.column.addWidget(self.error)
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(self.cancel)
        buttons.addWidget(self.save)
        self.column.addLayout(buttons)

    def refuse(self, words: str) -> None:
        self.error.setText(plain(words))
        self.error.show()


class FieldsDialog(_Sheet):
    """A form from `fields`; `values` holds what it saved, after exec()
    returns Accepted. `validate` and `live` are commands.Form's."""

    def __init__(
        self,
        title: str,
        fields: list[DialogField],
        p: Palette,
        parent: QWidget | None = None,
        *,
        validate: Callable[[dict[str, Any]], str | None] | None = None,
        live: Callable[[dict[str, Any]], str] | None = None,
        save_label: str = "Save",
        inline: bool = False,
    ) -> None:
        super().__init__(title, p, save_label, parent, inline=inline)
        self.fields = fields
        self.validate, self.live = validate, live
        self.values: dict[str, Any] = {}
        self.inputs: dict[str, QWidget] = {}
        self.rows: dict[str, tuple[QLabel, QWidget]] = {}

        body = QWidget()
        self.form = QFormLayout(body)
        self.form.setContentsMargins(0, 4, 8, 4)
        self.form.setHorizontalSpacing(16)
        self.form.setVerticalSpacing(8)
        for spec in fields:
            self._add_row(spec)
        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setWidget(body)
        area.setMinimumWidth(520)
        self.area, self.body = area, body
        self.column.addWidget(area, 1)
        self.live_line = QLabel()
        self.live_line.setTextFormat(Qt.TextFormat.RichText)
        self.live_line.setWordWrap(True)
        self.live_line.setVisible(live is not None)
        self.column.addWidget(self.live_line)
        self.save.clicked.connect(self.try_save)
        self.finish()
        self._update_shown()
        if inline:
            # As tall as its fields: the chapter scrolls, not the form.
            area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            area.setMinimumWidth(0)
            self._fit()
        else:
            self.resize(640, min(780, 170 + 44 * len(fields)))

    # Drawing the fields

    def _add_row(self, spec: DialogField) -> None:
        widget = self._input(spec)
        label = QLabel(plain(spec.label))
        label.setFont(serif(12.5))
        label.setStyleSheet(f"color:{self.p['label']}; background:transparent")
        if spec.hint:
            cell = QWidget()
            stack = QVBoxLayout(cell)
            stack.setContentsMargins(0, 0, 0, 0)
            stack.setSpacing(1)
            stack.addWidget(widget)
            stack.addWidget(
                text(
                    plain(spec.hint), self.p["dim"], serif(10.5, italic=True), wrap=True
                )
            )
            shown: QWidget = cell
        else:
            shown = widget
        self.form.addRow(label, shown)
        self.rows[spec.key] = (label, shown)
        if spec.kind != "info":
            self.inputs[spec.key] = widget

    def _input(self, spec: DialogField) -> QWidget:
        changed = self._changed(spec)
        if spec.kind in _LINE_KINDS:
            line = QLineEdit(_shown_text(spec.value))
            line.setPlaceholderText(plain(spec.placeholder))
            if spec.kind == "secret":
                line.setEchoMode(QLineEdit.EchoMode.Password)
            line.textEdited.connect(changed)
            return line
        if spec.kind == "area":
            box = QPlainTextEdit(_shown_text(spec.value))
            box.setFixedHeight(120)
            box.textChanged.connect(changed)
            return box
        if spec.kind == "select":
            combo = QComboBox()
            options, chosen = form_spec.select_choices(spec)
            if spec.allow_blank:
                combo.addItem(plain(spec.placeholder) or "(none)", None)
            for label, value in options:
                combo.addItem(plain(label), value)
            combo.setCurrentIndex(max(0, combo.findData(chosen)))
            combo.currentIndexChanged.connect(changed)
            return combo
        if spec.kind == "check":
            tick = QCheckBox()
            tick.setChecked(bool(spec.value))
            tick.toggled.connect(changed)
            return tick
        if spec.kind == "picker":
            shown = spec.display(spec.value) if spec.display else spec.value
            return _Held(spec.value, plain(_shown_text(shown)), self.p)
        if spec.kind == "info":
            return text(
                plain(_shown_text(spec.value)), self.p["foreground"], serif(12.5)
            )
        raise ValueError(f"The desktop can't draw a {spec.kind!r} field yet.")

    # Reading them back

    def read(self, spec: DialogField) -> Any:
        """What a field's widget holds, as form_spec reads it."""
        widget = self.inputs[spec.key]
        if isinstance(widget, QLineEdit):
            return widget.text().strip()
        if isinstance(widget, QPlainTextEdit):
            return widget.toPlainText().rstrip()
        if isinstance(widget, QComboBox):
            return widget.currentData()
        if isinstance(widget, QCheckBox):
            return widget.isChecked()
        if isinstance(widget, _Held):
            return widget.value
        return None

    def set_value(self, key: str, value: Any) -> None:
        """Put `value` in a field's widget, as the user typing it would."""
        self._put(self.inputs[key], value)
        self._changed(next(s for s in self.fields if s.key == key))()

    @staticmethod
    def _put(widget: QWidget, value: Any) -> None:
        if isinstance(widget, QLineEdit):
            widget.setText(_shown_text(value))
        elif isinstance(widget, QPlainTextEdit):
            widget.setPlainText(_shown_text(value))
        elif isinstance(widget, QComboBox):
            widget.setCurrentIndex(max(0, widget.findData(value)))
        elif isinstance(widget, QCheckBox):
            widget.setChecked(bool(value))

    def _changed(self, spec: DialogField) -> Callable[..., None]:
        def changed(*_args) -> None:
            if spec.fills is not None:
                current = form_spec.current_values(self._readable(), self.read)
                for key, value in spec.fills(current).items():
                    if key in self.inputs and key != spec.key:
                        self._fill(key, value)
            self._update_shown()

        return changed

    def _fill(self, key: str, value: Any) -> None:
        """Set a field another one suggests, without running its own
        fills."""
        widget = self.inputs[key]
        widget.blockSignals(True)
        try:
            self._put(widget, value)
        finally:
            widget.blockSignals(False)

    def _readable(self) -> list[DialogField]:
        return [spec for spec in self.fields if spec.key in self.inputs]

    def _update_shown(self) -> None:
        if not self.rows:
            return
        current = form_spec.current_values(self._readable(), self.read)
        for spec in self.fields:
            label, widget = self.rows[spec.key]
            visible = form_spec.shown(spec, current)
            label.setVisible(visible)
            widget.setVisible(visible)
        if self.live is not None:
            words = self.live(current)
            self.live_line.setText(to_html(words, self.p))
            self.live_line.setVisible(bool(words))
        if self.inline and hasattr(self, "area"):
            self._fit()

    def _fit(self) -> None:
        """In place, be as tall as the fields shown now."""
        self.form.activate()
        width = self.area.viewport().width()
        tall = self.body.heightForWidth(width) if self.body.hasHeightForWidth() else -1
        if tall < 0:
            tall = self.body.sizeHint().height()
        self.area.setFixedHeight(tall + 2 * self.area.frameWidth() + 4)

    def try_save(self) -> None:
        """Save if every field parses and `validate` allows it, else say
        what is wrong and stay."""
        try:
            values = form_spec.result(self._readable(), self.read)
        except FieldError as error:
            self.refuse(str(error))
            return
        problem = self.validate(values) if self.validate is not None else None
        if problem:
            self.refuse(problem)
            return
        self.values = values
        self.accept()


class _Held(QLabel):
    """A value the desktop shows but can't change (a picker field)."""

    def __init__(self, value: Any, shown: str, p: Palette) -> None:
        super().__init__(shown or "—")
        self.value = value
        self.setStyleSheet(f"color:{p['foreground']}; background:transparent")
        self.setToolTip("Change this in the terminal app for now.")


class ChooseDialog(_Sheet):
    """A searchable list of `choices`, with the highlighted one's details
    beside it; `chosen` holds the value picked, after exec() returns
    Accepted (a double-click picks too)."""

    def __init__(
        self,
        title: str,
        choices: list[Choice],
        p: Palette,
        parent: QWidget | None = None,
        *,
        empty: str = "Nothing to choose from.",
        inline: bool = False,
    ) -> None:
        super().__init__(title, p, "Choose", parent, inline=inline)
        self.choices = choices
        self.chosen: Any = None
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search…")
        self.search.textChanged.connect(self.refilter)
        self.column.addWidget(self.search)
        self.list = QListWidget()
        self.list.setFont(serif(12.5))
        self.details = QLabel()
        self.details.setTextFormat(Qt.TextFormat.RichText)
        self.details.setWordWrap(True)
        self.details.setAlignment(Qt.AlignmentFlag.AlignTop)
        details = QScrollArea()
        details.setWidgetResizable(True)
        details.setWidget(self.details)
        split = QSplitter()
        split.addWidget(self.list)
        split.addWidget(details)
        split.setSizes([360, 320])
        if not any(choice.detail for choice in choices):
            details.hide()
        self.column.addWidget(split, 1)
        self.empty = text(plain(empty), p["dim"], serif(12.5, italic=True))
        self.column.addWidget(self.empty)
        self.list.currentRowChanged.connect(self._show)
        self.list.itemDoubleClicked.connect(lambda _item: self.try_save())
        self.save.clicked.connect(self.try_save)
        self.finish()
        self.refilter("")
        if inline:
            split.setMinimumHeight(320)
        else:
            self.resize(760 if not details.isHidden() else 520, 620)

    def refilter(self, words: str) -> None:
        """List the choices whose label or search words have every word
        typed."""
        wanted = words.lower().split()
        self.list.clear()
        for index, choice in enumerate(self.choices):
            haystack = f"{plain(choice.label)} {choice.search}".lower()
            if all(word in haystack for word in wanted):
                item = QListWidgetItem(plain(choice.label))
                item.setData(Qt.ItemDataRole.UserRole, index)
                self.list.addItem(item)
        self.empty.setVisible(self.list.count() == 0)
        if self.list.count():
            self.list.setCurrentRow(0)

    def shown(self) -> list[str]:
        """The labels listed now."""
        return [self.list.item(i).text() for i in range(self.list.count())]

    def _show(self, row: int) -> None:
        item = self.list.item(row)
        if item is None:
            self.details.setText("")
            return
        choice = self.choices[item.data(Qt.ItemDataRole.UserRole)]
        self.details.setText(to_html(choice.detail, self.p))

    def choose(self, label: str) -> None:
        """Highlight the listed entry called `label`."""
        self.list.setCurrentRow(self.shown().index(label))

    def try_save(self) -> None:
        item = self.list.currentItem()
        if item is None:
            self.refuse("Choose one first.")
            return
        self.chosen = self.choices[item.data(Qt.ItemDataRole.UserRole)].value
        self.accept()


class ConfirmDialog(_Sheet):
    """A yes-or-no question; Accepted means yes."""

    def __init__(
        self,
        question: str,
        p: Palette,
        parent: QWidget | None = None,
        *,
        yes_label: str = "Delete",
        inline: bool = False,
    ) -> None:
        super().__init__("Are you sure?", p, yes_label, parent, inline=inline)
        words = QLabel(to_html(question, p))
        words.setTextFormat(Qt.TextFormat.RichText)
        words.setWordWrap(True)
        words.setFont(serif(13))
        self.question = plain(question)
        self.column.addWidget(words)
        self.save.clicked.connect(self.accept)
        # No by default, as on the terminal.
        self.save.setDefault(False)
        self.cancel.setDefault(True)
        self.finish()
        if not inline:
            self.resize(460, 200)
