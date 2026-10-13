"""Answering the desktop's dialogs in tests, without showing them.

`answering(window, ...)` makes the window's `ask` answer each dialog it
opens, in turn, and records them:

- a FieldsDialog: a dict of field key -> what to type (a string, or a
  select's value, or a bool for a check), then Save;
- a ChooseDialog: the label of the entry to choose;
- a ConfirmDialog: True (yes) or False;
- None (any dialog): cancel.

A dialog that refuses its answer (a form with a bad entry) is recorded
with its error and counts as cancelled.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QDialog, QPushButton, QWidget

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
                dialog.set_value(key, value)
            dialog.try_save()
        elif isinstance(dialog, ChooseDialog):
            dialog.choose(answer)
            dialog.try_save()
        elif isinstance(dialog, ConfirmDialog):
            return (
                QDialog.DialogCode.Accepted if answer else QDialog.DialogCode.Rejected
            )
        return dialog.result()

    window.ask = ask
    return asked


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
