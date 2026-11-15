"""The App update notice in the terminal: the Update screen (the title
page's Update row and the command list's Update open it), its What's new
page, and the short line a saga's status row shows once.

The app holds the notice (`update_notice`, set when a check's
UpdateChecked message arrives from its thread); the title page, the line
and this screen each watch it, so all three change together. The core
(updates.py) decides what to say. Release notes are untrusted text, so
everything here shows them as plain text, never as markup.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, cast

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.widgets import Button, Checkbox, Static

from ... import __version__, updates
from ...markup import escape
from .fields import ModalDialog

if TYPE_CHECKING:
    from ..app import ArsMagicaManagerApp

#: The help page for the Update screen.
HELP_ID = "update-screen"


class UpdateChecked(Message):
    """A check for an App update has ended (posted from its thread to the
    app): what it found, and whether Check now asked for it."""

    def __init__(self, result: updates.Result, now_asked: bool) -> None:
        super().__init__()
        self.result = result
        self.now_asked = now_asked


def _app(screen_app: object) -> ArsMagicaManagerApp:
    return cast("ArsMagicaManagerApp", screen_app)


def short_line(notice: updates.Notice) -> str:
    """The line a saga's status row shows (markup): the headline in the
    accent, or the warning colour for security fixes."""
    colour = "$text-warning" if notice.kind != updates.UPDATE else "$accent"
    return f"[{colour}]! {escape(notice.headline)}[/] · Ctrl+P Update"


class UpdateLine(Static):
    """The short line in a saga's status row, beside the theme's name:
    shown once, in the first saga opened while a notice waits."""

    DEFAULT_CSS = """
    UpdateLine {
        width: auto;
        height: 1;
        padding: 0 1;
        display: none;
    }
    """

    def on_mount(self) -> None:
        self.watch(self.app, "update_notice", self._show, init=True)

    def _show(self, notice: updates.Notice | None) -> None:
        app = _app(self.app)
        mine = app.update_line_owner in (None, id(self))
        if notice is None or not notice.shown or not mine:
            self.display = False
            return
        app.update_line_owner = id(self)
        self.update(short_line(notice))
        self.display = True


class NotesScreen(ModalDialog[None]):
    """What's new: an App update's whole notes, as plain text."""

    help_id = HELP_ID

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Close")]

    DEFAULT_CSS = """
    NotesScreen {
        align: center middle;
    }

    NotesScreen #notes-box {
        width: 100;
        max-width: 100%;
        height: 90%;
        padding: 1 2;
    }

    NotesScreen #notes-text {
        height: 1fr;
    }
    """

    def __init__(self, notice: updates.Notice) -> None:
        super().__init__()
        self.notice = notice

    def compose(self) -> ComposeResult:
        with Vertical(id="notes-box", classes="dialog-box"):
            yield Static(
                f"What's new in Armarius {self.notice.version}",
                classes="dialog-title",
                markup=False,
            )
            with VerticalScroll(id="notes-text"):
                yield Static(self.notice.notes, markup=False, id="notes-body")
            yield Static("Esc closes", markup=False)


class UpdateScreen(ModalDialog[None]):
    """The Update screen: the App update (its version and date, the first
    lines of its notes) with What's new, Download page and Skip this
    version, then the setting to check at start-up and Check now. The
    terminal has no Settings window, so the setting lives here; the desktop
    shares it."""

    help_id = HELP_ID

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Close")]

    DEFAULT_CSS = """
    UpdateScreen {
        align: center middle;
    }

    UpdateScreen #update-box {
        width: 84;
        max-width: 100%;
        height: auto;
        padding: 1 2;
    }

    UpdateScreen #update-buttons, UpdateScreen #update-check-row {
        width: auto;
        height: auto;
        margin: 1 0 0 0;
    }

    UpdateScreen Button {
        margin: 0 1 0 0;
    }

    UpdateScreen .update-faint {
        color: $text-muted;
    }

    UpdateScreen #update-outcome {
        margin: 1 0 0 0;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        # Kept, not queried: the notice may arrive before they are mounted.
        self.headline = Static("", id="update-headline")
        self.lines = Static("", id="update-lines", markup=False)
        self.extra = Static("", id="update-extra", markup=False, classes="update-faint")
        self.whats_new = Button("What's new", id="update-whats-new")
        self.download = Button("Download page", id="update-download")
        self.skip = Button("Skip this version", id="update-skip")
        self.outcome = Static("", id="update-outcome", markup=False)

    def compose(self) -> ComposeResult:
        copy = _app(self.app).update_copy
        with Vertical(id="update-box", classes="dialog-box"):
            yield Static("Update", classes="dialog-title")
            yield self.headline
            yield self.lines
            yield self.extra
            with Horizontal(id="update-buttons"):
                yield self.whats_new
                yield self.download
                yield self.skip
            yield Checkbox(
                "Check for updates when Armarius starts",
                updates.check_at_start(),
                id="update-check",
                disabled=not copy.checks,
            )
            yield Static(
                "It asks GitHub for the latest Release, sending only this "
                "app's version.",
                classes="update-faint",
                markup=False,
            )
            with Horizontal(id="update-check-row"):
                yield Button(
                    "Check now", id="update-check-now", disabled=not copy.checks
                )
            if not copy.checks:
                self.outcome.update(updates.outcome_text(updates.Result(False)))
            yield self.outcome

    def on_mount(self) -> None:
        self.watch(self.app, "update_notice", self._show, init=True)
        self.watch(self.app, "update_outcome", self.outcome.update, init=False)

    def _show(self, notice: updates.Notice | None) -> None:
        headline, lines, extra = self.headline, self.lines, self.extra
        whats_new, download, skip = self.whats_new, self.download, self.skip
        if notice is None:
            headline.update(escape(f"Armarius {__version__} is the version you have."))
            for widget in (lines, extra, whats_new, download, skip):
                widget.display = False
            return
        dated = f" ({notice.date})" if notice.date else ""
        if notice.skipped:
            headline.update(
                f"[$text-muted]! {escape(notice.headline)}{dated}, skipped[/]"
            )
        else:
            colour = "$text-warning" if notice.kind != updates.UPDATE else "$accent"
            headline.update(
                f"[bold {colour}]! {escape(notice.headline)}[/]{escape(dated)}"
            )
        lines.update("\n".join(notice.lines))
        lines.display = bool(notice.lines)
        more = [notice.remote] if notice.remote else []
        if not notice.download and notice.how_to_update:
            more.append(notice.how_to_update)
        extra.update("\n".join(more))
        extra.display = bool(more)
        whats_new.display = bool(notice.notes)
        download.label = notice.download or "Download page"
        download.display = bool(notice.download)
        skip.display = notice.can_skip and not notice.skipped

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        app = _app(self.app)
        notice = app.update_notice
        if event.button.id == "update-whats-new" and notice is not None:
            self.app.push_screen(NotesScreen(notice))
        elif event.button.id == "update-download" and notice is not None:
            self.app.open_url(notice.url)
        elif event.button.id == "update-skip" and notice is not None:
            updates.skip(notice.version)
            app.refresh_update_notice()
        elif event.button.id == "update-check-now":
            self.outcome.update("Checking…")
            app.check_for_update(now_asked=True)

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        event.stop()
        updates.set_check_at_start(event.value)
        _app(self.app).refresh_update_notice()
