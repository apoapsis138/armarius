"""What closing the desktop app asks first."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QWidget

from .. import hosting
from .forms import Ask, ConfirmDialog
from .themes import Palette


def confirm_close_while_hosting(p: Palette, parent: QWidget, ask: Ask) -> bool:
    """Whether to close the app while it hosts: asked first, since closing
    ends every player's connection. True when nothing is hosted."""
    if not hosting.HOST.running:
        return True
    question = ConfirmDialog(
        "The saga is hosted. Closing the app stops hosting, and every player's "
        "connection ends at once; what they saved is kept.",
        p,
        parent,
        yes_label="Close and Stop Hosting",
        title="Stop Hosting?",
    )
    return ask(question) == QDialog.DialogCode.Accepted
