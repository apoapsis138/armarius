"""A written Handout read in the terminal: its text laid out under its
Stationery's name (handout_layout.Laid), the terminal's half of the
Bridge the desktop draws on paper.

Each block stands where the layout sets it (headings and centred lines
centred, right lines to the right); a heading is bold, an initial's
letter bold in the accent colour, a flourish a centred ornament and a
placed picture named in place. No tag is ever shown as typed."""

from __future__ import annotations

from typing import ClassVar

from rich.table import Table
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Label, Static

from ... import handout_layout as layout
from ... import handout_markup as hm
from ...forms.handouts import HANDOUTS_HELP
from ...handout_layout import Laid, Placed
from ...markup import escape
from .fields import ModalDialog

#: The ornament a flourish is read as.
FLOURISH = "~ ❧ ~"


def reading(block: Placed) -> str:
    """One laid-out block as the terminal shows it (markup)."""
    if block.kind == hm.HEADING:
        return f"[b]{block.text}[/]"
    if block.kind == hm.FLOURISH:
        return FLOURISH
    if block.kind == hm.PICTURE:
        return f"[i](picture {block.picture}: {escape(block.caption)})[/]"
    if block.kind == hm.INITIAL and block.initial:
        return f"[b $accent]{escape(block.initial)}[/]{block.text}"
    return block.text


def table(block: Placed) -> Table:
    """A laid-out table block as a Rich table: its first row the header,
    its cells' markup drawn as markup (it is already safe)."""
    header, *rows = block.rows or ((),)
    drawn = Table(expand=True, show_edge=False)
    for cell in header:
        drawn.add_column(Text.from_markup(cell), overflow="fold")
    for row in rows:
        drawn.add_row(*(Text.from_markup(cell) for cell in row))
    return drawn


class HandoutReading(ModalDialog[None]):
    """A laid-out Handout under its Stationery's name, scrolling when it
    is long, with Close."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Close")]

    DEFAULT_CSS = """
    HandoutReading {
        align: center middle;
    }

    #handout-reading {
        width: 76;
        max-width: 100%;
        height: auto;
        max-height: 100%;
        padding: 1 2;
    }

    #handout-stationery {
        width: 100%;
        text-align: center;
        color: $text-muted;
    }

    #handout-scroll {
        height: auto;
        max-height: 30;
        margin-top: 1;
    }

    .handout-block {
        width: 100%;
        height: auto;
        margin-bottom: 1;
    }

    .handout-centre {
        text-align: center;
    }

    .handout-right {
        text-align: right;
    }

    #handout-buttons {
        width: 100%;
        height: auto;
        align-horizontal: right;
    }
    """

    help_id = HANDOUTS_HELP

    def __init__(self, laid: Laid, help_id: str = "") -> None:
        """`help_id`: the page F1 opens, when not the Handouts' own (a
        catalog entry read in full)."""
        super().__init__()
        self.laid = laid
        if help_id:
            self.help_id = help_id

    def compose(self) -> ComposeResult:
        laid = self.laid
        with Vertical(id="handout-reading", classes="dialog-box"):
            yield Label(f"— {escape(laid.stationery.label)} —", id="handout-stationery")
            with VerticalScroll(id="handout-scroll"):
                title = escape(laid.title)
                if laid.stationery.title == layout.TITLE_DOCKET:
                    yield Static(
                        f"[i]{title}[/]", id="handout-title", classes="handout-block"
                    )
                else:
                    yield Static(
                        f"[b]{title}[/]",
                        id="handout-title",
                        classes="handout-block handout-centre",
                    )
                for block in laid.blocks:
                    if block.kind == hm.TABLE:
                        yield Static(
                            table(block), classes="handout-block handout-table"
                        )
                        continue
                    yield Static(
                        reading(block),
                        classes=f"handout-block handout-{block.align}",
                    )
            with Horizontal(id="handout-buttons"):
                yield Button("Close", id="btn-close", variant="primary")

    def on_mount(self) -> None:
        self.query_one("#btn-close", Button).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-close":
            event.stop()
            self.dismiss(None)
