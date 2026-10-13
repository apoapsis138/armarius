"""Answering the desktop's dialogs in tests, without showing them.

`answering(window, ...)` makes the window's `ask` answer each dialog it
opens, in turn, and records them:

- a FieldsDialog: a dict of field key -> what to type (a string, or a
  select's value, or a bool for a check, or a picker's value), then Save;
  a callable instead (`pick`, `list_add`, `list_edit(row)`,
  `list_delete(row)`) acts on the field as clicking it does, its own
  steps answered by the answers that follow;
- a ChooseDialog: the label of the entry to choose (`everything(label)`
  ticks Show everything first);
- a ConfirmDialog: True (yes) or False;
- a ChooseFile's Open window (QFileDialog): the path of the file;
- None (any dialog): cancel.

A dialog that refuses its answer (a form with a bad entry) is recorded
with its error and counts as cancelled. A message the window shows (a
refusal, the notes after a step) goes to `window.told` as (title, words).
"""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QDialog, QFileDialog, QPushButton, QWidget

from ars_magica_manager.gui.forms import ChooseDialog, ConfirmDialog, FieldsDialog


def answering(window: Any, *answers: Any) -> list[QDialog]:
    """Answer the next dialogs `window` opens with `answers`; the dialogs
    asked, appended as they open."""
    asked: list[QDialog] = []
    queue = list(answers)

    def ask(dialog: QDialog) -> int:
        asked.append(dialog)
        if not queue:
            raise AssertionError(f"Unexpected dialog: {dialog.windowTitle()}")
        answer = queue.pop(0)
        if answer is None:
            return QDialog.DialogCode.Rejected
        if isinstance(dialog, FieldsDialog):
            for key, value in answer.items():
                if callable(value):
                    value(dialog, key)
                else:
                    dialog.set_value(key, value)
            dialog.try_save()
        elif isinstance(dialog, ChooseDialog):
            if callable(answer):
                answer(dialog)
            else:
                dialog.choose(answer)
            dialog.try_save()
        elif isinstance(dialog, ConfirmDialog):
            return (
                QDialog.DialogCode.Accepted if answer else QDialog.DialogCode.Rejected
            )
        elif isinstance(dialog, QFileDialog):
            dialog.selectFile(str(answer))
            return QDialog.DialogCode.Accepted
        return dialog.result()

    window.ask = ask
    window.told = []
    window.tell = lambda title, words: window.told.append((title, words))
    return asked


def everything(label: str):
    """Tick a list's Show everything, then choose `label`."""

    def act(dialog: ChooseDialog) -> None:
        dialog.everything.setChecked(True)
        dialog.choose(label)

    return act


def pick(form: FieldsDialog, key: str) -> None:
    """Run a picker field's chooser."""
    form.pick(key)


def _list_button(words: str, row: int | None = None):
    def act(form: FieldsDialog, key: str) -> None:
        field = form.inputs[key]
        if row is not None:
            field.choose(row)  # type: ignore[attr-defined]
        field.buttons[words].click()  # type: ignore[attr-defined]

    return act


#: Add an entry to a list field.
list_add = _list_button("Add")


def list_edit(row: int):
    """Edit a list field's entry `row`."""
    return _list_button("Edit", row)


def list_delete(row: int):
    """Delete a list field's entry `row`."""
    return _list_button("Delete", row)


def buttons(page: QWidget, words: str) -> list[QPushButton]:
    """The page's section buttons called `words` (Add, Edit, Delete...),
    in page order."""
    return [
        b
        for b in page.findChildren(QPushButton)
        if b.objectName() == "edit" and b.text().strip() == words
    ]


def section_buttons(page: QWidget, title: str) -> dict[str, QPushButton]:
    """The buttons beside the section titled `title` (its title's text,
    any count in brackets left off), by their words."""
    from PySide6.QtWidgets import QLabel

    for label in page.findChildren(QLabel):
        if label.text().split(" (")[0] != title:
            continue
        box = label.parentWidget()
        holder = box.parentWidget() if box is not None else None
        if holder is None:
            continue
        found = {
            b.text().strip(): b
            for b in holder.findChildren(QPushButton)
            if b.objectName() == "edit" and b.parentWidget() is holder
        }
        if found:
            return found
    raise AssertionError(f"No section {title!r} with buttons")
