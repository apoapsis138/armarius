"""The import screens: choosing what to import, a duplicate book, and the
spell import helper."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Label, OptionList, Static
from textual.widgets.option_list import Option

from ... import spells as spl
from ...markup import escape, problem
from ..fields import ModalDialog

#: What the saga's Import Data dialog offers: (key, label, works yet?). The
#: ones that don't work yet are listed greyed out, as what's planned.
IMPORT_KINDS: tuple[tuple[str, str, bool], ...] = (
    # An export made from More on its sheet: one entry per kind.
    ("characters", "Characters", True),
    ("covenants", "Covenants", True),
    ("laboratories", "Laboratories", True),
    ("books", "Books", True),
    ("spells", "Spells", True),
)


#: The kind the dialog opens on.
IMPORT_DEFAULT = "books"


class ImportScreen(ModalDialog[str | None]):
    """Choose what to import into the saga. Kinds that can't be imported yet
    are shown greyed out and can't be chosen. Dismisses with the chosen
    IMPORT_KINDS key, or None if cancelled."""

    help_id = "import-data"

    DEFAULT_CSS = """
    ImportScreen {
        align: center middle;
    }

    #import-dialog {
        width: 50;
        max-width: 100%;
        height: auto;
        padding: 1 2;
    }

    #import-hint {
        color: $text-muted;
        height: auto;
        margin-bottom: 1;
    }

    #import-list {
        height: auto;
    }

    #import-buttons {
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="import-dialog", classes="dialog-box"):
            yield Label("Import Data", id="import-title", classes="dialog-title")
            yield Static("What would you like to import?", id="import-hint")
            yield OptionList(id="import-list", compact=True)
            with Horizontal(id="import-buttons"):
                yield Button("Cancel", id="btn-import-cancel")

    def on_mount(self) -> None:
        options = self.query_one("#import-list", OptionList)
        options.add_options(
            Option(label, id=key)
            if works
            else Option(f"{label}  (not available yet)", id=key, disabled=True)
            for key, label, works in IMPORT_KINDS
        )
        options.highlighted = next(
            i for i, k in enumerate(IMPORT_KINDS) if k[0] == IMPORT_DEFAULT
        )
        options.focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        event.stop()
        self.dismiss(event.option.id)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(None)


class DuplicateBookScreen(ModalDialog[str]):
    """Asked during an import for a book whose name is already taken.
    Dismisses with "duplicate", "duplicate_all", "skip" or "skip_all" (the
    "_all" answers apply to every later duplicate of the same import). Skip
    is focused, and Escape skips, so a stray key never adds a copy."""

    #: Escape skips (ModalDialog's cancel).
    CANCEL_RESULT: ClassVar[str] = "skip"

    BINDINGS: ClassVar[list[BindingType]] = [
        ("d", "choose('duplicate')", "Duplicate"),
        ("D", "choose('duplicate_all')", "Duplicate All"),
        ("s", "choose('skip')", "Skip"),
        ("S", "choose('skip_all')", "Skip All"),
    ]

    DEFAULT_CSS = """
    DuplicateBookScreen {
        align: center middle;
    }

    #duplicate-dialog {
        width: 72;
        max-width: 100%;
        height: auto;
        padding: 1 2;
    }

    #duplicate-message {
        height: auto;
        margin-bottom: 1;
    }

    #duplicate-buttons {
        width: 100%;
        height: auto;
    }

    #duplicate-buttons Button {
        margin-right: 1;
    }
    """

    #: (answer, button label), in button order.
    CHOICES: ClassVar[tuple[tuple[str, str], ...]] = (
        ("duplicate", "Duplicate"),
        ("duplicate_all", "Duplicate All"),
        ("skip", "Skip"),
        ("skip_all", "Skip All"),
    )

    def __init__(self, name: str, remaining: int, *, noun: str = "book") -> None:
        super().__init__()
        self.book_name = name
        self.remaining = remaining
        self.noun = noun

    def compose(self) -> ComposeResult:
        more = (
            f"\n[dim]{self.remaining} more duplicate(s) after this one.[/]"
            if self.remaining
            else ""
        )
        with Vertical(id="duplicate-dialog", classes="dialog-box"):
            yield Static(
                f"A {self.noun} named [b]{escape(self.book_name)}[/] is already "
                f"in the saga. Add this one as well?{more}",
                id="duplicate-message",
            )
            with Horizontal(id="duplicate-buttons"):
                for answer, label in self.CHOICES:
                    yield Button(label, id=f"btn-{answer.replace('_', '-')}")

    def on_mount(self) -> None:
        self.query_one("#btn-skip", Button).focus()

    def action_choose(self, answer: str) -> None:
        self.dismiss(answer)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        self.dismiss((event.button.id or "btn-skip")[len("btn-") :].replace("-", "_"))


class SpellImportHelperScreen(ModalDialog[str | None]):
    """What a spell CSV looks like, with a way to save an example to start
    from. Dismisses with "choose" to go on to picking the file, or None."""

    help_id = "import-spells"

    DEFAULT_CSS = """
    SpellImportHelperScreen {
        align: center middle;
    }

    #spell-import-dialog {
        width: 96;
        max-width: 100%;
        height: auto;
        max-height: 100%;
        padding: 1 2;
    }

    #spell-import-body {
        height: auto;
        max-height: 30;
    }

    #spell-import-status {
        height: auto;
        margin-top: 1;
    }

    #spell-import-buttons {
        width: 100%;
        height: auto;
        margin-top: 1;
    }

    #spell-import-buttons Button {
        margin-right: 1;
    }
    """

    def __init__(self, folder: Path) -> None:
        super().__init__()
        self.folder = folder

    def compose(self) -> ComposeResult:
        columns = "\n".join(
            f"  [b]{name}[/]: {escape(meaning)}"
            for name, meaning in spl.CSV_COLUMN_HELP
        )
        example = escape(spl.EXAMPLE_CSV.splitlines()[1])
        with Vertical(id="spell-import-dialog", classes="dialog-box"):
            yield Label(
                "Import Spells", id="spell-import-title", classes="dialog-title"
            )
            with VerticalScroll(id="spell-import-body"):
                yield Static(
                    "Spells are imported from a CSV file with a header row into the "
                    "saga's own spells. Columns, in any order and any case:\n\n"
                    f"{columns}\n\n[b]An example row:[/]\n  [dim]{example}[/]",
                    id="spell-import-help",
                )
            yield Static("", id="spell-import-status")
            with Horizontal(id="spell-import-buttons"):
                yield Button(
                    "Choose CSV file...",
                    id="btn-spell-import-choose",
                    variant="success",
                )
                yield Button("Save example CSV", id="btn-spell-import-example")
                yield Button("Cancel", id="btn-spell-import-cancel")

    def on_mount(self) -> None:
        self._fit()
        self.query_one("#btn-spell-import-choose", Button).focus()

    def on_resize(self) -> None:
        self._fit()

    def _fit(self) -> None:
        """The help scrolls, so the buttons stay on screen however short the
        terminal is."""
        self.query_one("#spell-import-body").styles.max_height = max(
            4, min(30, self.size.height - 12)
        )

    def _save_example(self) -> None:
        target = self.folder / "spells_example.csv"
        n = 2
        while target.exists():
            target = self.folder / f"spells_example_{n}.csv"
            n += 1
        status = self.query_one("#spell-import-status", Static)
        try:
            target.write_text(spl.EXAMPLE_CSV, encoding="utf-8")
        except OSError as error:
            status.update(problem(f"Couldn't save the example: {escape(str(error))}"))
            return
        status.update(
            f"Saved [b]{escape(target.name)}[/] in {escape(str(self.folder))}. "
            "Edit it, then choose it to import."
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if event.button.id == "btn-spell-import-choose":
            self.dismiss("choose")
        elif event.button.id == "btn-spell-import-example":
            self._save_example()
        else:
            self.dismiss(None)
