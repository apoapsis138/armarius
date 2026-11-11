"""The title page the storyguide's window opens on (title_page.TitlePage),
in front of the saga picker: the name in block letters, the tagline, and
the ways on, chosen with the arrow keys and Enter."""

from __future__ import annotations

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Footer, OptionList, Static
from textual.widgets.option_list import Option

from ... import title_page as tp
from ...markup import escape
from .help import HelpContext, HelpScreen, shown_keys
from .saga_picker import SagaPickerScreen

#: Block letters four rows high, for the name.
_LETTERS = {
    "A": [" ▄██▄ ", "██  ██", "██████", "██  ██"],
    "I": ["██", "██", "██", "██"],
    "M": ["██▄ ▄██", "██ ▀ ██", "██   ██", "██   ██"],
    "R": ["█████▄", "██  ██", "█████▀", "██ ▀█▄"],
    "S": ["▄█████", "██▄▄▄ ", " ▀▀▀██", "█████▀"],
    "U": ["██  ██", "██  ██", "██  ██", "▀████▀"],
}


def banner(word: str) -> str:
    """`word` in block letters (only the letters of Armarius have them)."""
    letters = [_LETTERS[c] for c in word.upper()]
    return "\n".join("  ".join(letter[row] for letter in letters) for row in range(4))


def _options(choices: tuple[tp.TitleChoice, ...]) -> list[Option]:
    """Each way on as a row: its name, then where it goes."""
    return [
        Option(f"  {choice.label:<14}{escape(choice.detail)}", id=choice.key)
        for choice in choices
    ]


class TitleScreen(Screen[None]):
    """The title page over the saga picker: Enter takes the way on
    highlighted (the saga opened last, else every saga); Learn lists
    Tutorials and General Help, with Back."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("q", "quit", "Quit"),
        ("question_mark", "help", "Help"),
    ]

    DEFAULT_CSS = """
    TitleScreen {
        align: center middle;
    }

    TitleScreen #title-page {
        width: 84;
        height: auto;
        border: double $accent;
        padding: 1 4;
        background: $surface;
    }

    TitleScreen .title-line {
        width: 100%;
        text-align: center;
    }

    TitleScreen #title-ornament, TitleScreen #title-tail {
        color: $accent;
    }

    TitleScreen #title-name {
        color: $primary;
        text-style: bold;
        margin: 1 0 0 0;
    }

    TitleScreen #title-tagline {
        color: $secondary;
        text-style: italic;
        margin: 1 0;
    }

    TitleScreen #title-choices {
        width: 46;
        height: auto;
        border: none;
        background: $surface;
        margin: 1 0 0 0;
    }

    TitleScreen #title-hint, TitleScreen #title-edition {
        color: $text-muted;
        margin: 1 0 0 0;
    }
    """

    def __init__(self, page: tp.TitlePage) -> None:
        super().__init__()
        self.page = page

    def compose(self) -> ComposeResult:
        page = self.page
        with Vertical(id="title-page"):
            yield Static(
                "☙ ─────────────── ❦ ─────────────── ❧",
                id="title-ornament",
                classes="title-line",
            )
            yield Static(banner(page.name), id="title-name", classes="title-line")
            yield Static(
                f"~ {escape(page.tagline)} ~", id="title-tagline", classes="title-line"
            )
            with Center():
                yield OptionList(*_options(page.choices), id="title-choices")
            yield Static("Enter chooses", id="title-hint", classes="title-line")
            yield Static("─────── ❦ ───────", id="title-tail", classes="title-line")
            yield Static(escape(page.edition), id="title-edition", classes="title-line")
        yield Footer()

    def on_mount(self) -> None:
        choices = self.query_one(OptionList)
        choices.highlighted = 0
        choices.focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        event.stop()
        key = event.option.id or tp.SAGAS
        if key == tp.LEARN:
            self.show_choices((*tp.LEARN_CHOICE.then, tp.BACK_CHOICE))
        elif key == tp.BACK_CHOICE.key:
            self.show_choices(self.page.choices)
        else:
            self.choose(key)

    def show_choices(self, choices: tuple[tp.TitleChoice, ...]) -> None:
        """List `choices` in place of those on show (Learn's own, with
        Back to the page's), the first highlighted."""
        listed = self.query_one(OptionList)
        listed.clear_options()
        listed.add_options(_options(choices))
        listed.highlighted = 0

    def choose(self, key: str) -> None:
        """Leave the title page for the saga picker, then take the way on
        `key` from there."""
        self.app.pop_screen()
        picker = self.app.screen
        if not isinstance(picker, SagaPickerScreen):
            return
        if key == tp.OPEN and self.page.saga_id is not None:
            picker.open_saga(self.page.saga_id)
        elif key == tp.NEW:
            picker.action_create_saga()
        elif key == tp.TUTORIAL:
            picker.start_tutorial()
        elif key == tp.HELP:
            picker.action_help()

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen(self.help_context()))

    def help_context(self) -> HelpContext:
        return HelpContext(["title-page"], "Title page", shown_keys(self, ("help",)))
