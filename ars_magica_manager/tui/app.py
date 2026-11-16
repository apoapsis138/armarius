"""Textual app entry point. Screen flow lives in the screens package."""

from __future__ import annotations

from collections.abc import Iterable
from typing import ClassVar

from textual.app import App, SystemCommand
from textual.binding import Binding, BindingType
from textual.reactive import reactive
from textual.screen import Screen

from .. import __version__, hosting, paths, title_page, updates
from ..markup import escape
from ..models import Player
from ..settings import load_settings, update_settings
from .screens import SagaPickerScreen
from .screens.help import HelpScreen, help_context
from .screens.title import TitleScreen
from .screens.update import UpdateChecked, UpdateScreen
from .style import APP_CSS
from .themes import SCRIPTORUM, SCRIPTORUM_DARK, app_variable_defaults

#: Theme applied on first launch, or if a saved theme name is no longer registered.
DEFAULT_THEME = SCRIPTORUM.name


class ArsMagicaManagerApp(App[None]):
    """Armarius's TUI."""

    # In the title, not the sub-title: the workspace uses that for the saga
    # and its date (the Header shows "title — sub_title").
    TITLE = f"Armarius v{__version__}"
    BINDINGS: ClassVar[list[BindingType]] = [
        ("q", "quit", "Quit"),
        # Help: F1 anywhere, even in a dialog and while typing
        # (a modal screen's keys don't reach the app's unless they're
        # priority). ? is bound by the screens and ModalDialog, so a field
        # being typed in still gets it.
        Binding("f1", "help", "Help", show=False, priority=True),
    ]

    CSS = APP_CSS

    def get_theme_variable_defaults(self) -> dict[str, str]:
        """The app's own CSS variables (themes.py) for a theme that doesn't
        set them."""
        return app_variable_defaults(self.current_theme)

    def action_help(self) -> None:
        """Open Help on whatever has focus (never on top of Help)."""
        if isinstance(self.screen, HelpScreen):
            return
        self.push_screen(HelpScreen(help_context(self.screen_stack)))

    #: Lines to show once on start: what moving the user data from the repo's
    #: data/ folder did, or why the data folder couldn't be used (main.py).
    startup_notes: tuple[str, ...] = ()

    #: Who signed in to the saga open in this browser copy;
    #: None in the storyguide's own window, which never signs in, and
    #: whenever no saga is open.
    player: Player | None = None

    #: Open on the title page (main.py: only the storyguide's own window,
    #: not a player's hosted copy).
    show_title: bool = False

    #: How this copy treats App updates (main.py chooses; a copy built
    #: any other way, such as a test's, never checks).
    update_copy: updates.Copy = updates.Quiet()
    #: The App update notice to show (None for none): the title page's
    #: Update row, a saga's status line and the Update screen watch it.
    update_notice: reactive[updates.Notice | None] = reactive(None)
    #: What the last Check now found, in words.
    update_outcome: reactive[str] = reactive("")
    #: The status line that has shown the notice this sitting (its id):
    #: it is shown once, in the first saga opened.
    update_line_owner: int | None = None

    def refresh_update_notice(self) -> None:
        """Read the notice again from what the last check found."""
        self.update_notice = updates.notice(self.update_copy)

    def check_for_update(self, *, now_asked: bool = False) -> None:
        """Ask GitHub for the latest Release, in a thread of its own: at
        start-up only if a day has passed (silent if it fails); Check now
        whenever, saying what it found."""
        if not self.update_copy.checks:
            if now_asked:
                self.update_outcome = updates.outcome_text(updates.Result(False))
            return
        copy = self.update_copy

        def run() -> None:
            result = updates.check(copy, now_asked=now_asked)
            self.post_message(UpdateChecked(result, now_asked))

        self.run_worker(run, thread=True, exclusive=True, group="update-check")

    def on_update_checked(self, message: UpdateChecked) -> None:
        if message.now_asked:
            self.update_outcome = updates.outcome_text(message.result)
        if message.result.ran and not message.result.problem:
            self.refresh_update_notice()

    def action_open_update(self) -> None:
        """Open the Update screen (the title page's Update, or Update in
        the command list)."""
        if not isinstance(self.screen, UpdateScreen):
            self.push_screen(UpdateScreen())

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)
        if self.update_copy.checks:
            notice = self.update_notice
            yield SystemCommand(
                "Update",
                notice.headline if notice is not None else "Check for an App update",
                self.action_open_update,
            )

    def on_mount(self) -> None:
        # A hosted copy has no command palette (Ctrl+P): it is Textual's,
        # not the app's, and its theme choice would write the host's
        # settings for someone who hasn't signed in.
        self.use_command_palette = not hosting.is_hosted_copy()
        # Notes about the host's data folder are the storyguide's business:
        # a player's browser copy doesn't show them.
        if self.startup_notes and not self.is_web:
            self.notify(
                escape("\n".join(self.startup_notes)),
                title="Your data folder: " + escape(str(paths.data_dir())),
                timeout=30,
            )
        self.register_theme(SCRIPTORUM)
        self.register_theme(SCRIPTORUM_DARK)
        saved_theme = load_settings().get("theme")
        self.theme = (
            saved_theme
            if isinstance(saved_theme, str) and saved_theme in self.available_themes
            else DEFAULT_THEME
        )
        self.push_screen(SagaPickerScreen())
        if self.update_copy.checks:
            self.refresh_update_notice()
        if self.show_title:
            self.push_screen(TitleScreen(title_page.title_page()))
        self.check_for_update()

    def watch_theme(self, theme_name: str) -> None:
        # The settings are the storyguide's: only their own window saves
        # its theme there.
        if not hosting.is_hosted_copy():
            update_settings(theme=theme_name)
