"""The desktop's dialogs for the steps a sheet's buttons run
(commands.py): a form drawn from a list of form_spec.DialogFields, the
same lists the terminal's FieldsDialog draws, and checked with form_spec,
so both front-ends accept and refuse the same entries; a searchable list
to choose from; and a yes-or-no question.

A field's kind picks its widget: a line for text and numbers, a box for
multi-line text, a drop-down for a choice, a tick box for a check, and a
plain line for read-only information. A "picker" field is a button
showing its value that runs the field's chooser (its core steps, each as
a window over the form), or, holding a list, the list with Add, Edit and
Delete; one with only a terminal chooser is shown read-only.

`run_steps` runs a chain of steps as windows; the window runs a button's
steps the same way, in place.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
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
from ..commands import (
    RECENT,
    Act,
    Choice,
    Choose,
    ChooseFile,
    Confirm,
    Form,
    Picked,
    Refuse,
    filter_values,
    heading,
    passes,
)
from ..form_spec import DialogField, FieldError, ListEditor
from . import heraldry, sounds
from .markup_html import plain, to_html
from .ornaments import FleuronRule, corner_flourishes
from .paper import Paper
from .themes import Palette
from .widgets import filter_choice, serif, text

#: Shows a step's dialog and waits: Accepted or Rejected. The window's
#: `ask`, which tests replace to answer without showing anything.
Ask = Callable[[QDialog], int]

#: Field kinds the dialog reads as typed text, parsed by form_spec.
_LINE_KINDS = {"text", "secret", "int", "optint", "optfloat"}


def _shown_text(value: object) -> str:
    return "" if value is None else str(value)


class _Page(Paper):
    """A dialog's sheet of paper, with a flourish in each corner; ruled
    round its edge when it is a window of its own (`edged`)."""

    edged = False

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        if self.edged:
            painter.setPen(QPen(QColor(self.p["rule"]), 1))
            painter.drawRect(QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5))
        corner_flourishes(painter, QRectF(self.rect()), self.p, 18)


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
        page = self.page = _Page(p)
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
        sounds.play("tock")
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
        ask: Ask | None = None,
        picture: Callable[[dict[str, Any]], Any] | None = None,
    ) -> None:
        super().__init__(title, p, save_label, parent, inline=inline)
        self.picture = picture
        self.fields = fields
        self.ask: Ask = ask or (lambda dialog: dialog.exec())
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
        area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.area, self.body = area, body
        self.column.addWidget(area, 1)
        self.live_line = QLabel()
        self.live_line.setTextFormat(Qt.TextFormat.RichText)
        self.live_line.setWordWrap(True)
        self.live_line.setVisible(live is not None)
        # The picture (a shield) sits left of the live line.
        self.picture_label = QLabel()
        self.picture_label.setVisible(False)
        under = QHBoxLayout()
        under.setSpacing(16)
        under.addWidget(self.picture_label)
        under.addWidget(self.live_line, 1)
        self.column.addLayout(under)
        self.save.clicked.connect(self.try_save)
        self.finish()
        self._update_shown()
        if inline:
            # As tall as its fields: the chapter scrolls, not the form.
            area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            area.setMinimumWidth(0)
            self._fit()
        else:
            pictured = 140 if picture is not None else 0
            self.resize(700, min(820, 170 + 44 * len(fields) + pictured))

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
            # A long choice is cut short in the box, not let widen the
            # form; its list still opens wide enough to read it.
            combo.setSizeAdjustPolicy(
                QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
            )
            combo.setMinimumContentsLength(16)
            combo.view().setMinimumWidth(combo.view().sizeHintForColumn(0) + 24)
            combo.currentIndexChanged.connect(changed)
            return combo
        if spec.kind == "check":
            tick = QCheckBox()
            tick.setChecked(bool(spec.value))
            tick.toggled.connect(changed)
            return tick
        if spec.kind == "picker":
            if spec.items is not None:
                return _ListField(spec, spec.items, self)
            if spec.choose is not None:
                return _PickerField(spec, self)
            shown = spec.display(spec.value) if spec.display else spec.value
            return _Held(spec.value, plain(_shown_text(shown)), self.p)
        if spec.kind == "info":
            return text(
                plain(_shown_text(spec.value)),
                self.p["foreground"],
                serif(12.5),
                wrap=True,
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
        if isinstance(widget, _Held | _PickerField | _ListField):
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
        elif isinstance(widget, _PickerField | _ListField):
            widget.put(value)

    def pick(self, key: str) -> None:
        """Run a picker field's chooser, as clicking it does."""
        widget = self.inputs[key]
        assert isinstance(widget, _PickerField)
        widget.pick()

    def run(self, step: object) -> tuple[bool, object]:
        """Run a field's steps as windows over the form (run_steps); a
        refusal is shown as the form's error."""
        answered, result = run_steps(step, self.p, self, self.ask)
        if isinstance(result, Refuse):
            self.refuse(f"{result.title}: {result.why}")
            return False, None
        if answered and isinstance(result, Picked):
            self.error.hide()
        return answered, result

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
        if self.picture is not None:
            drawn = self.picture(current)
            if drawn is not None:
                self.picture_label.setPixmap(
                    heraldry.pixmap(drawn, 96, self.p["accent"])
                )
            self.picture_label.setVisible(drawn is not None)
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


class _PickerField(QWidget):
    """A picker field: a button showing the value, which runs the field's
    chooser, and Clear when the field may be blank."""

    def __init__(self, spec: DialogField, form: FieldsDialog) -> None:
        super().__init__()
        self.spec, self.form = spec, form
        self.value: Any = spec.value
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        self.button = QPushButton()
        self.button.setObjectName("picker")
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button.setStyleSheet("text-align:left; padding:3px 8px")
        self.button.clicked.connect(lambda _checked=False: self.pick())
        row.addWidget(self.button, 1)
        self.clear = QPushButton("Clear")
        self.clear.clicked.connect(lambda _checked=False: self._set(None))
        self.clear.setVisible(spec.allow_blank)
        row.addWidget(self.clear)
        self._show()

    def _show(self) -> None:
        if self.value is None:
            words = plain(self.spec.placeholder) or "(choose…)"
        elif self.spec.display is not None:
            words = plain(self.spec.display(self.value))
        else:
            words = _shown_text(self.value)
        self.button.setText(words)
        self.button.setToolTip(words)
        self.clear.setEnabled(self.value is not None)

    def pick(self) -> None:
        assert self.spec.choose is not None
        answered, result = self.form.run(self.spec.choose(self.value))
        if answered and isinstance(result, Picked):
            self._set(result.value)

    def put(self, value: Any) -> None:
        self.value = value
        self._show()

    def _set(self, value: Any) -> None:
        self.put(value)
        self.form._changed(self.spec)()


class _ListField(QWidget):
    """A picker field holding a small list: its entries, with Add, Edit
    and Delete for the one chosen (each entry's steps as windows)."""

    def __init__(
        self, spec: DialogField, editor: ListEditor, form: FieldsDialog
    ) -> None:
        super().__init__()
        self.spec, self.editor, self.form = spec, editor, form
        self.value: list[Any] = list(spec.value) if isinstance(spec.value, list) else []
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(4)
        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list.itemDoubleClicked.connect(lambda _item: self.edit())
        self.list.currentRowChanged.connect(lambda _row: self._enable())
        column.addWidget(self.list)
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        self.buttons: dict[str, QPushButton] = {}
        for words, act in (
            ("Add", self.add),
            ("Edit", self.edit),
            ("Delete", self.delete),
        ):
            button = QPushButton(words)
            button.clicked.connect(lambda _checked=False, act=act: act())
            row.addWidget(button)
            self.buttons[words] = button
        row.addStretch(1)
        column.addLayout(row)
        self._show()

    def _show(self, chosen: int | None = None) -> None:
        self.list.clear()
        for item in self.value:
            self.list.addItem(plain(self.editor.row(item)))
        if not self.value:
            self.list.addItem("(none)")
            self.list.item(0).setFlags(Qt.ItemFlag.NoItemFlags)
        elif chosen is not None:
            self.list.setCurrentRow(min(chosen, len(self.value) - 1))
        rows = max(1, len(self.value))
        self.list.setFixedHeight(min(6, rows) * 22 + 2 * self.list.frameWidth() + 4)
        self._enable()

    def _chosen(self) -> int | None:
        row = self.list.currentRow()
        if 0 <= row < len(self.value):
            return row
        return 0 if len(self.value) == 1 else None

    def _enable(self) -> None:
        some = self._chosen() is not None
        self.buttons["Edit"].setEnabled(some)
        self.buttons["Delete"].setEnabled(some)

    def choose(self, row: int) -> None:
        self.list.setCurrentRow(row)

    def add(self) -> None:
        answered, result = self.form.run(self.editor.entry(None))
        if answered and isinstance(result, Picked):
            self._set([*self.value, result.value], len(self.value))

    def edit(self) -> None:
        row = self._chosen()
        if row is None:
            return
        answered, result = self.form.run(self.editor.entry(self.value[row]))
        if answered and isinstance(result, Picked):
            items = list(self.value)
            items[row] = result.value
            self._set(items, row)

    def delete(self) -> None:
        row = self._chosen()
        if row is None:
            return
        items = list(self.value)
        del items[row]
        self._set(items, row)

    def put(self, value: Any) -> None:
        self.value = list(value or [])
        self._show()

    def _set(self, items: list[Any], chosen: int | None) -> None:
        self.value = items
        self._show(chosen)
        self.form._changed(self.spec)()
        if self.form.inline and hasattr(self.form, "area"):
            self.form._fit()


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
        others: Callable[[], list[Choice]] | None = None,
        step: Choose | None = None,
    ) -> None:
        super().__init__(title, p, "Choose", parent, inline=inline)
        self.offered = choices
        self.choices = choices
        self.chosen: Any = None
        #: The Choose drawn, for its filters and recent entries.
        self.step = step
        self.recent = step.recent() if step is not None and step.recent else []
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search…")
        self.search.textChanged.connect(self.refilter)
        self.column.addWidget(self.search)
        #: A drop-down per filter the Choose has, by its name.
        self.filters: dict[str, QComboBox] = {}
        if step is not None and step.filters:
            self._add_filters(step, choices)
        #: Lists the entries not offered too, each marked with why (the
        #: terminal's F3); only for a list that has any.
        self.everything = QCheckBox("Show everything")
        self.everything.setToolTip(
            "Also list what isn't offered here (from books not in play, or "
            "what the rules say can't be taken), marked with why."
        )
        self.everything.toggled.connect(lambda on: self._list_everything(on, others))
        self.everything.setVisible(others is not None)
        self.column.addWidget(self.everything)
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

    def _add_filters(self, step: Choose, choices: list[Choice]) -> None:
        """A row of drop-downs over the list, one per filter, each "any"
        until a value is chosen."""
        row = QHBoxLayout()
        for name in step.filters:
            combo = filter_choice(
                f"{name}: any",
                [(f"{name}: {v}", v) for v in filter_values(choices, name)],
            )
            combo.currentIndexChanged.connect(
                lambda _index: self.refilter(self.search.text())
            )
            self.filters[name] = combo
            row.addWidget(combo)
        row.addStretch(1)
        self.column.addLayout(row)

    def _list_everything(
        self, on: bool, others: Callable[[], list[Choice]] | None
    ) -> None:
        self.choices = [*self.offered, *(others() if on and others else [])]
        self.refilter(self.search.text())

    def wanted(self) -> dict[str, str | None]:
        """Each filter's chosen value (None: any)."""
        return {name: combo.currentData() for name, combo in self.filters.items()}

    def refilter(self, words: str) -> None:
        """List the choices whose label or search words have every word
        typed and that every filter lets through, under their headings;
        with nothing typed or chosen, the recent ones first."""
        wanted = words.lower().split()
        chosen = self.wanted()
        self.list.clear()
        listed: list[tuple[str, Choice, int]] = []
        if not wanted and not any(v is not None for v in chosen.values()):
            listed += [(RECENT, choice, -1 - i) for i, choice in enumerate(self.recent)]
        for index, choice in enumerate(self.choices):
            haystack = f"{plain(choice.label)} {choice.search}".lower()
            if all(word in haystack for word in wanted) and passes(choice, chosen):
                under = heading(self.step, choice) if self.step is not None else ""
                listed.append((under, choice, index))
        heading_now = ""
        for under, choice, index in listed:
            if under and under != heading_now:
                head = QListWidgetItem(under)
                head.setFlags(Qt.ItemFlag.NoItemFlags)
                head.setFont(serif(12.5, bold=True, caps=True))
                head.setForeground(QColor(self.p["heading"]))
                self.list.addItem(head)
            heading_now = under
            item = QListWidgetItem(plain(choice.label))
            item.setData(Qt.ItemDataRole.UserRole, index)
            self.list.addItem(item)
        self.empty.setVisible(not listed)
        if listed:
            self.list.setCurrentRow(self._first_entry())

    def _first_entry(self) -> int:
        """The row of the first entry listed (not a heading)."""
        return next(
            row
            for row in range(self.list.count())
            if self.list.item(row).data(Qt.ItemDataRole.UserRole) is not None
        )

    def _choice_at(self, item: QListWidgetItem) -> Choice | None:
        index = item.data(Qt.ItemDataRole.UserRole)
        if index is None:
            return None
        return self.recent[-1 - index] if index < 0 else self.choices[index]

    def shown(self) -> list[str]:
        """The labels listed now (headings left out)."""
        return [
            self.list.item(i).text()
            for i in range(self.list.count())
            if self.list.item(i).data(Qt.ItemDataRole.UserRole) is not None
        ]

    def _show(self, row: int) -> None:
        item = self.list.item(row)
        choice = self._choice_at(item) if item is not None else None
        self.details.setText(to_html(choice.detail, self.p) if choice else "")

    def choose(self, label: str) -> None:
        """Highlight the (first) listed entry called `label`."""
        rows = [
            row
            for row in range(self.list.count())
            if self.list.item(row).data(Qt.ItemDataRole.UserRole) is not None
        ]
        self.list.setCurrentRow(rows[self.shown().index(label)])

    def try_save(self) -> None:
        item = self.list.currentItem()
        choice = self._choice_at(item) if item is not None else None
        if choice is None:
            self.refuse("Choose one first.")
            return
        self.chosen = choice.value
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
        title: str = "",
    ) -> None:
        super().__init__(title or "Are you sure?", p, yes_label, parent, inline=inline)
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


class NoticeDialog(_Sheet):
    """A message on paper with an OK button: what a step refused, or the
    notes after it."""

    def __init__(
        self, title: str, words: str, p: Palette, parent: QWidget | None = None
    ) -> None:
        super().__init__(title, p, "OK", parent)
        # Paper all over: no system title bar, ruled round, and moved by
        # dragging the paper.
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.page.edged = True
        body = QLabel(to_html(words, p))
        body.setTextFormat(Qt.TextFormat.RichText)
        body.setWordWrap(True)
        body.setFont(serif(13))
        self.words = plain(words)
        self.column.addWidget(body)
        self.save.clicked.connect(self.accept)
        self.cancel.hide()
        self.finish()
        self.setMinimumWidth(420)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        handle = self.windowHandle()
        if event.button() == Qt.MouseButton.LeftButton and handle is not None:
            handle.startSystemMove()
        event.accept()


# -- running steps --


Step = Form | Choose | Confirm | ChooseFile


def step_dialog(
    step: Step,
    p: Palette,
    parent: QWidget | None,
    *,
    inline: bool = False,
    ask: Ask | None = None,
) -> QDialog | None:
    """The dialog that asks `step` (None: a list with nothing in it)."""
    if isinstance(step, ChooseFile):
        return file_dialog(step, parent)
    if isinstance(step, Form):
        return FieldsDialog(
            step.title,
            step.fields(),
            p,
            parent,
            validate=step.validate,
            live=step.live,
            save_label=step.save_label,
            inline=inline,
            ask=ask,
            picture=step.picture,
        )
    if isinstance(step, Choose):
        choices = step.choices()
        if not choices and step.others is None:
            return None
        return ChooseDialog(
            step.title,
            choices,
            p,
            parent,
            empty=step.empty,
            inline=inline,
            others=step.others,
            step=step,
        )
    return ConfirmDialog(
        step.question,
        p,
        parent,
        yes_label=step.yes_label,
        inline=inline,
        title=step.title,
    )


def answer(step: Step, dialog: QDialog) -> object:
    """Run `step`'s apply with what its (accepted) dialog holds: the next
    step, or what the steps end with."""
    if isinstance(step, Form):
        assert isinstance(dialog, FieldsDialog)
        return step.apply(dialog.values)
    if isinstance(step, Choose):
        assert isinstance(dialog, ChooseDialog)
        return step.apply(dialog.chosen)
    if isinstance(step, ChooseFile):
        assert isinstance(dialog, QFileDialog)
        return step.apply(Path(dialog.selectedFiles()[0]))
    return step.apply()


def file_dialog(step: ChooseFile, parent: QWidget | None) -> QFileDialog:
    """The system's Open window for a ChooseFile (its Save window for one
    that saves): files of its kind, in the folder it starts on."""
    kind = step.suffix.removeprefix(".").upper()
    patterns = " ".join(f"*{suffix}" for suffix in step.suffixes)
    dialog = QFileDialog(
        parent, plain(step.title), str(step.start), f"{kind} files ({patterns})"
    )
    if step.save:
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setDefaultSuffix(step.suffix.removeprefix("."))
        if step.start.suffix:
            dialog.selectFile(step.start.name)
    else:
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
    return dialog


def run_steps(
    step: object, p: Palette, parent: QWidget | None, ask: Ask
) -> tuple[bool, object]:
    """Run `step` and the steps it leads to, each as a window; whether
    every one was answered, and what the last led to (a Picked value, a
    Refuse...)."""
    while isinstance(step, Form | Choose | Confirm | ChooseFile | Act):
        if isinstance(step, Act):
            step = step.apply()
            continue
        dialog = step_dialog(step, p, parent, ask=ask)
        if dialog is None:
            assert isinstance(step, Choose)
            NoticeDialog(step.title, step.empty, p, parent).exec()
            return False, None
        if ask(dialog) != QDialog.DialogCode.Accepted:
            return False, None
        step = answer(step, dialog)
    return True, step
