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

from PySide6.QtCore import QByteArray, QEvent, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPaintEvent,
    QPen,
    QShowEvent,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
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
    FormCard,
    Picked,
    Refuse,
    filter_values,
    heading,
    passes,
)
from ..form_spec import DialogField, FieldError, ListEditor
from . import heraldry, snapping, sounds
from .frame import (
    APP_NAME,
    CLOSE,
    MAXIMISE,
    DragStrip,
    Grips,
    WindowButtons,
    native_frame_event,
)
from .markup_html import plain, to_html
from .ornaments import FleuronRule, InspectorFrame, corner_flourishes
from .paper import Paper, lift
from .themes import Palette
from .widgets import (
    ClickableCard,
    Inspector,
    ToggleSwitch,
    card_grid,
    filter_choice,
    serif,
    text,
)

#: Shows a step's dialog and waits: Accepted or Rejected. The window's
#: `ask`, which tests replace to answer without showing anything.
Ask = Callable[[QDialog], int]

#: Field kinds the dialog reads as typed text, parsed by form_spec.
_LINE_KINDS = {"text", "secret", "int", "optint", "optfloat"}


def _shown_text(value: object) -> str:
    return "" if value is None else str(value)


class _Page(Paper):
    """A dialog's sheet of paper, ruled round its edge, with a flourish in
    each corner."""

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QPen(QColor(self.p["rule"]), 1))
        painter.drawRect(QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5))
        corner_flourishes(painter, QRectF(self.rect()), self.p, 18)


class _Sheet(QDialog):
    """A dialog on paper, as a window over the page: the app's title bar
    (frame.py, in place of the system's), its title over a hedera rule, a
    body, an error line and its buttons (Cancel, then the action)."""

    #: The title bar's buttons; a window that can maximise also resizes.
    controls: tuple[str, ...] = (MAXIMISE, CLOSE)

    def __init__(
        self,
        title: str,
        p: Palette,
        action: str,
        parent: QWidget | None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(plain(title))
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.p = p
        page = self.page = _Page(p)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(page)
        sheet = QVBoxLayout(page)
        sheet.setContentsMargins(0, 0, 0, 0)
        sheet.setSpacing(0)
        sheet.addLayout(self._title_bar())
        self.column = QVBoxLayout()
        self.column.setSpacing(8)
        self.column.setContentsMargins(26, 6, 26, 18)
        sheet.addLayout(self.column, 1)
        self.heading = text(plain(title), p["heading"], serif(17, bold=True))
        self.column.addWidget(self.heading)
        self.column.addWidget(FleuronRule(p))
        self.error = text("", p["text-error"], serif(12, italic=True), wrap=True)
        self.error.hide()
        self.cancel = QPushButton("Cancel")
        self.cancel.clicked.connect(self.reject)
        self.save = QPushButton(action)
        self.save.setDefault(True)
        self.ask: Ask = lambda dialog: dialog.exec()

    def unsaved(self) -> bool:
        """Whether leaving now would lose changes: a window that tracks
        them says so, and Cancel, the X and Esc then ask first."""
        return False

    def reject(self) -> None:
        if self.unsaved() and not self._discards():
            return
        super().reject()

    def _discards(self) -> bool:
        """Ask whether to leave without saving."""
        question = ConfirmDialog(
            "Leave without saving? Your changes won't be kept.",
            self.p,
            self,
            yes_label="Discard Changes",
            title="Unsaved Changes",
        )
        question.cancel.setText("Keep Editing")
        return self.ask(question) == QDialog.DialogCode.Accepted

    def _title_bar(self) -> QHBoxLayout:
        """The app's name in the middle (drag it to move the window) and
        the window's own buttons, as the main window has."""
        maximises = MAXIMISE in self.controls
        bar = QHBoxLayout()
        bar.setContentsMargins(12, 4, 8, 0)
        self.drag = DragStrip(self, self.p, APP_NAME, maximises)
        bar.addWidget(self.drag, 1)
        self.window_buttons = WindowButtons(self, self.p, kinds=self.controls)
        bar.addWidget(self.window_buttons, 0, Qt.AlignmentFlag.AlignTop)
        if maximises:
            self.grips = Grips(self)
        return bar

    def showEvent(self, event: QShowEvent) -> None:
        snapping.make_snappable(self)
        super().showEvent(event)

    def nativeEvent(
        self, eventType: QByteArray | bytes | bytearray | memoryview, message: int
    ) -> tuple[bool, int]:
        """Fills the screen's work area when maximised (snapping.py)."""
        result = native_frame_event(self, eventType, message)
        if result is not None:
            return True, result
        return super().nativeEvent(eventType, message)  # pyright: ignore[reportReturnType]

    def changeEvent(self, event: QEvent) -> None:
        """Maximise turns to restore (and back) as the window does."""
        if event.type() == QEvent.Type.WindowStateChange:
            snapping.make_snappable(self)
            if MAXIMISE in self.controls:
                button = self.window_buttons.buttons[MAXIMISE]
                button.update()
                button.setToolTip("Restore" if self.isMaximized() else "Maximise")
        super().changeEvent(event)

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


#: The widest a form opened as a window grows to fit its labels, and the
#: tallest it grows to fit its fields.
WIDEST_WINDOW, TALLEST_WINDOW = 1100, 820


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
        ask: Ask | None = None,
        picture: Callable[[dict[str, Any]], Any] | None = None,
        inspector: str = "",
        cancel_label: str = "Cancel",
    ) -> None:
        super().__init__(title, p, save_label, parent)
        self.cancel.setText(cancel_label)
        self.picture = picture
        self.fields = fields
        if ask is not None:
            self.ask = ask
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
        if inspector:
            under.addWidget(self._inspector(inspector), 1)
        else:
            under.addWidget(self.live_line, 1)
        self.column.addLayout(under)
        self.save.clicked.connect(self.try_save)
        self.finish()
        self._update_shown()
        self._size_window()
        #: What a window that keeps something opened with; a calculator's
        #: Close (any other label) has nothing to lose.
        self.cancels = cancel_label == "Cancel"
        self.opened_with = self._as_they_stand()

    def _size_window(self, *, grow: bool = False) -> None:
        """Wide enough for the longest label and its field
        beside it, and tall enough for every field and what is under
        them (a wrapped hint, the live line or gloss), up to TALLEST_WINDOW,
        past which the fields scroll. `grow`: never smaller than it is now,
        so a window widened by hand stays so, and kept on the screen."""
        area, body = self.area, self.body
        frame = 2 * area.frameWidth()
        scrollbar = area.verticalScrollBar().sizeHint().width()
        wide = body.sizeHint().width() + frame + scrollbar + 60
        width = min(max(700, wide), WIDEST_WINDOW)
        if grow:
            width = max(width, self.width())
        self.resize(width, self.height())
        self.column.activate()
        viewport = width - self.column.contentsMargins().left() * 2 - frame - scrollbar
        fields = (
            body.heightForWidth(viewport)
            if body.hasHeightForWidth()
            else body.sizeHint().height()
        )
        under = self.sizeHint().height() - area.sizeHint().height()
        tall = min(TALLEST_WINDOW, under + fields + frame + 8)
        if not grow:
            self.resize(width, tall)
        elif tall > self.height():
            self.resize(width, tall)
            screen = self.screen().availableGeometry()
            if self.isVisible() and self.frameGeometry().bottom() > screen.bottom():
                self.move(self.x(), max(screen.top(), screen.bottom() - self.height()))

    def _inspector(self, heading: str) -> InspectorFrame:
        """The live text boxed as a gloss at the foot of the page, under
        its heading."""
        panel = InspectorFrame(heading, self.p)
        box = QVBoxLayout(panel)
        box.setContentsMargins(InspectorFrame.MARGIN, 44, 20, 16)
        self.live_line.setFont(serif(13))
        box.addWidget(self.live_line)
        return panel

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
        def changed(*_args: object) -> None:
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

    def _as_they_stand(self) -> dict[str, Any]:
        return form_spec.current_values(self._readable(), self.read)

    def unsaved(self) -> bool:
        return self.cancels and self._as_they_stand() != self.opened_with

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
        if hasattr(self, "area"):
            # Fields shown as others are chosen (Lab Work's) need more room.
            self._size_window(grow=True)

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
        values = form_spec.current_values(self.form._readable(), self.form.read)
        step = form_spec.first_choice(self.spec, self.value, values)
        answered, result = self.form.run(step)
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
        others: Callable[[], list[Choice]] | None = None,
        step: Choose | None = None,
    ) -> None:
        super().__init__(title, p, "Choose", parent)
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


class CardsDialog(_Sheet):
    """A form's check fields as `cards` (commands.FormCard) beside an
    inspector: each card's switch sets its field, and clicking a card shows
    it in the inspector, with a switch of its own. `values` holds what it
    saved, after exec() returns Accepted, as FieldsDialog's does."""

    def __init__(
        self,
        title: str,
        fields: list[DialogField],
        cards: list[FormCard],
        lead: str,
        p: Palette,
        parent: QWidget | None = None,
        *,
        save_label: str = "Save",
        cancel_label: str = "Cancel",
        ask: Ask | None = None,
    ) -> None:
        super().__init__(title, p, save_label, parent)
        self.cancel.setText(cancel_label)
        if ask is not None:
            self.ask = ask
        self.values: dict[str, Any] = {f.key: bool(f.value) for f in fields}
        self.opened_with = dict(self.values)
        #: The card in the inspector, by its title.
        self.chosen = ""
        self.switches: dict[str, ToggleSwitch] = {}
        self.cards = {card.title: self._card(card) for card in cards}
        self.column.addWidget(text(lead, p["label"], serif(12, italic=True), wrap=True))
        self.inspector = Inspector(p)
        self.inspector.setFixedWidth(400)
        # A character with many interests scrolls them, beside the inspector.
        listed = QWidget()
        grid = QVBoxLayout(listed)
        grid.setContentsMargins(0, 0, 8, 0)
        grid.addWidget(card_grid(list(self.cards.values()), 2))
        grid.addStretch(1)
        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setWidget(listed)
        area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        body = QHBoxLayout()
        body.setSpacing(14)
        body.addWidget(area, 1)
        body.addWidget(self.inspector)
        self.column.addLayout(body, 1)
        self.save.clicked.connect(self.accept)
        self.finish()
        self.resize(WIDEST_WINDOW + 100, TALLEST_WINDOW)
        self.choose(cards[0])

    def unsaved(self) -> bool:
        return self.values != self.opened_with

    def _on(self, card: FormCard) -> bool:
        """Whether `card` shows as on: a card that isn't usable never does,
        though its field keeps its value."""
        return card.usable and self.values.get(card.key, True)

    def _switch(self, card: FormCard) -> QWidget:
        """`card`'s switch, or the words that stand for one on a card that
        can't change."""
        if card.fixed:
            return text(card.fixed, self.p["label"], serif(11, italic=True))
        switch = ToggleSwitch(self._on(card), self.p, lambda: self._toggle(card))
        switch.setEnabled(card.usable)
        return switch

    def _card(self, card: FormCard) -> ClickableCard:
        p = self.p
        drawn = ClickableCard(
            p, pad=8, edge=p["text-success"] if self._on(card) else p["dim"]
        )
        drawn.column.setSpacing(2)
        top = QHBoxLayout()
        top.addWidget(text(card.title, p["foreground"], serif(12.5, bold=True)), 1)
        switch = self._switch(card)
        if isinstance(switch, ToggleSwitch):
            self.switches[card.title] = switch
        top.addWidget(switch)
        drawn.column.addLayout(top)
        drawn.column.addWidget(
            text(card.summary, p["foreground"], serif(11.5), wrap=True)
        )
        drawn.column.addWidget(
            text(card.count, p["label"], serif(11, italic=True), wrap=True)
        )
        drawn.column.addStretch(1)
        drawn.clicked = lambda: self.choose(card)
        if not self._on(card):
            self._shade(drawn, False)
        return drawn

    def _shade(self, drawn: ClickableCard, on: bool) -> None:
        """A card off is faded in place of the lift's shadow: a card has
        one effect."""
        if on:
            lift(drawn, self.p)
            return
        faded = QGraphicsOpacityEffect(drawn)
        faded.setOpacity(0.5)
        drawn.setGraphicsEffect(faded)

    def _toggle(self, card: FormCard) -> None:
        """Flip `card`'s field, and both of its switches to match."""
        self.values[card.key] = not self.values[card.key]
        on = self._on(card)
        drawn = self.cards[card.title]
        drawn.set_edge(self.p["text-success" if on else "dim"])
        self._shade(drawn, on)
        self.switches[card.title].setChecked(on)
        action = self.inspector.action
        if self.chosen == card.title and isinstance(action, ToggleSwitch):
            action.setChecked(on)

    def choose(self, card: FormCard) -> None:
        """Show `card` in the inspector and outline it."""
        self.chosen = card.title
        for title, drawn in self.cards.items():
            drawn.set_chosen(title == card.title)
        self.inspector.show_item(
            card.title, card.count, card.detail, None, self._switch(card)
        )


class ConfirmDialog(_Sheet):
    """A yes-or-no question; Accepted means yes."""

    controls = (CLOSE,)

    def __init__(
        self,
        question: str,
        p: Palette,
        parent: QWidget | None = None,
        *,
        yes_label: str = "Delete",
        title: str = "",
    ) -> None:
        super().__init__(title or "Are you sure?", p, yes_label, parent)
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
        self.resize(460, 200)


#: The longest notice title kept on one line.
NOTICE_TITLE_WIDTH = 32
#: The longest line of a notice's title set without wrapping.
NOTICE_LINE_WIDTH = 40


def notice_title(title: str) -> str:
    """A notice's title as it is set: one longer than NOTICE_TITLE_WIDTH
    breaks after its action ("Next Siege Event:" over "The Siege of Burg
    Falkenstein")."""
    action, colon, rest = title.partition(": ")
    if not colon or len(title) <= NOTICE_TITLE_WIDTH:
        return title
    return f"{action}:\n{rest}"


class NoticeDialog(_Sheet):
    """A message on paper with an OK button: what a step refused, or the
    notes after it."""

    controls = (CLOSE,)

    def __init__(
        self, title: str, words: str, p: Palette, parent: QWidget | None = None
    ) -> None:
        super().__init__(title, p, "OK", parent)
        # A long title ("Spend Agency Experience: Sir Konrad von Elster")
        # breaks after its action, so the name stays whole on the line
        # below, and wraps rather than being cut off at the paper's edge.
        heading = notice_title(plain(title))
        self.heading.setText(heading)
        # Wrapping a short title leaves a gap under it, so only a line
        # still too long after the break wraps.
        self.heading.setWordWrap(
            any(len(line) > NOTICE_LINE_WIDTH for line in heading.split("\n"))
        )
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


# -- running steps --


Step = Form | Choose | Confirm | ChooseFile


def step_dialog(
    step: Step,
    p: Palette,
    parent: QWidget | None,
    *,
    ask: Ask | None = None,
) -> QDialog | None:
    """The dialog that asks `step` (None: a list with nothing in it)."""
    if isinstance(step, ChooseFile):
        return file_dialog(step, parent)
    if isinstance(step, Form) and step.cards is not None:
        return CardsDialog(
            step.title,
            step.fields(),
            step.cards(),
            step.cards_lead,
            p,
            parent,
            save_label=step.save_label,
            cancel_label=step.cancel_label,
            ask=ask,
        )
    if isinstance(step, Form):
        return FieldsDialog(
            step.title,
            step.fields(),
            p,
            parent,
            validate=step.validate,
            live=step.live,
            save_label=step.save_label,
            ask=ask,
            picture=step.picture,
            inspector=step.inspector,
            cancel_label=step.cancel_label,
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
            others=step.others,
            step=step,
        )
    return ConfirmDialog(
        step.question,
        p,
        parent,
        yes_label=step.yes_label,
        title=step.title,
    )


def answer(step: Step, dialog: QDialog) -> object:
    """Run `step`'s apply with what its (accepted) dialog holds: the next
    step, or what the steps end with."""
    if isinstance(step, Form):
        assert isinstance(dialog, FieldsDialog | CardsDialog)
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
