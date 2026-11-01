"""Textual app entry point. Screen flow lives in the screens package."""

from __future__ import annotations

from typing import ClassVar

from textual.app import App
from textual.binding import Binding, BindingType

from .. import __version__, paths, title_page
from ..markup import escape
from ..models import Player
from ..settings import load_settings, update_settings
from .screens import SagaPickerScreen
from .screens.help import HelpScreen, help_context
from .screens.title import TitleScreen
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

    def on_mount(self) -> None:
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
        if self.show_title:
            self.push_screen(TitleScreen(title_page.title_page()))

    def watch_theme(self, theme_name: str) -> None:
        update_settings(theme=theme_name)
