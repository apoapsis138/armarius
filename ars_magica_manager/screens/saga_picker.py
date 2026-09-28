"""The start screen: pick, create or delete a saga, or read About."""

from __future__ import annotations

from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Header,
    Label,
    ListItem,
    ListView,
    Markdown,
    Static,
)

from .. import ROOT, __version__, creation, storage
from ..markup import escape
from .fields import FieldsDialog, ModalDialog
from .forms import _saga_fields
from .prompts import ConfirmScreen
from .widgets import BottomBar
from .workspace import WorkspaceScreen

_SAGA_ITEM_ID_PREFIX = "saga-"
#: What loading a damaged or hand-edited saga file can raise.
_UNREADABLE = (OSError, ValueError, TypeError, KeyError)
#: The licences, credits and trademark notices the About dialog shows.
NOTICE_PATH = ROOT / "NOTICE.md"


class AboutScreen(ModalDialog[None]):
    """About this App: the version, and NOTICE.md (the program's licence,
    the Ars Magica Open License attribution, sources and trademarks).
    Escape or Close dismisses it."""

    DEFAULT_CSS = """
    AboutScreen {
        align: center middle;
    }

    #about-dialog {
        width: 84;
        max-width: 100%;
        height: 90%;
        border: round $accent;
        padding: 0 1;
        background: $surface;
    }

    #about-title {
        text-style: bold;
        margin: 1 1 0 1;
    }

    #about-scroll {
        width: 100%;
        height: 1fr;
    }

    #about-buttons {
        width: 100%;
        height: auto;
        align-horizontal: right;
    }
    """

    def compose(self) -> ComposeResult:
        try:
            notice = NOTICE_PATH.read_text(encoding="utf-8")
        except OSError:
            notice = "NOTICE.md is missing: see the repository for licences."
        with Vertical(id="about-dialog"):
            yield Label(f"Ars Magica Manager v{__version__}", id="about-title")
            with VerticalScroll(id="about-scroll"):
                yield Markdown(notice, id="about-notice", open_links=False)
            with Horizontal(id="about-buttons"):
                yield Button("Close", id="btn-close", variant="primary")

    def on_mount(self) -> None:
        self.query_one("#about-scroll", VerticalScroll).focus()

    def on_markdown_link_clicked(self, event: Markdown.LinkClicked) -> None:
        # Only web links: the relative ones (LICENSE) are files in the repo.
        if event.href.startswith(("http://", "https://")):
            self.app.open_url(event.href)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.action_cancel()


class SagaPickerScreen(Screen[None]):
    """Lists existing sagas; offers to create a new one or delete one."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("n", "create_saga", "New Saga"),
        ("A", "delete_saga", "Delete Saga"),
        Binding("delete", "delete_saga", "Delete Saga", show=False),
        ("q", "quit", "Quit"),
        # Shown at the footer's right end (BottomBar right_actions).
        ("question_mark", "about", "About this App"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            "Select a saga to open, press 'n' to create a new one, "
            "or 'A' to delete the highlighted one.",
            id="picker-hint",
        )
        yield ListView(id="saga-list")
        yield Static(f"[dim]Ars Magica Manager {__version__}[/]", id="picker-version")
        yield BottomBar(right_actions=["about"])

    async def on_mount(self) -> None:
        await self.refresh_list()

    async def refresh_list(self) -> None:
        list_view = self.query_one("#saga-list", ListView)
        # Must be awaited before re-adding items below, or a same-id item not
        # yet removed collides with its freshly-mounted replacement and
        # Textual raises DuplicateIds.
        await list_view.clear()

        saga_ids = storage.list_sagas()
        if not saga_ids:
            await list_view.append(
                ListItem(Label("No sagas yet -- press 'n' to create one."))
            )
            return

        items = []
        for saga_id in saga_ids:
            try:
                saga = storage.load_saga(saga_id)
            except _UNREADABLE:
                # Still listed, so it can be deleted (by id).
                summary = f"{escape(saga_id)}  —  [$text-error]can't be read[/]"
            else:
                summary = (
                    f"{escape(saga.name)}  —  "
                    f"Storyguide: {escape(saga.storyguide) or '(unset)'}"
                    f"  —  {saga.current_season} {saga.current_year}"
                )
            items.append(
                ListItem(Label(summary), id=f"{_SAGA_ITEM_ID_PREFIX}{saga_id}")
            )
        await list_view.extend(items)
        # append()/extend() don't set an initial highlight the way construction-time
        # children do, so keyboard/enter selection wouldn't work without this.
        list_view.index = 0

    def action_about(self) -> None:
        self.app.push_screen(AboutScreen())

    def action_create_saga(self) -> None:
        async def handle_result(values: dict[str, Any] | None) -> None:
            if values is not None:
                storage.save_saga(
                    creation.new_saga(
                        values["name"],
                        values["storyguide"],
                        values["description"],
                        values["year"],
                        values["season"],
                    )
                )
                await self.refresh_list()

        self.app.push_screen(
            FieldsDialog("Create a New Saga", _saga_fields(None), save_label="Create"),
            handle_result,
        )

    def action_delete_saga(self) -> None:
        """Delete the highlighted saga's file, after confirming: this is
        permanent, so the message says so and No is the default."""
        item = self.query_one("#saga-list", ListView).highlighted_child
        if (
            item is None
            or item.id is None
            or not item.id.startswith(_SAGA_ITEM_ID_PREFIX)
        ):
            self.notify("No saga to delete.")
            return
        saga_id = item.id.removeprefix(_SAGA_ITEM_ID_PREFIX)
        try:
            name = storage.load_saga(saga_id).name
        except _UNREADABLE:
            name = saga_id  # unreadable file: still let it be deleted by id

        async def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                storage.delete_saga(saga_id)
                list_view = self.query_one("#saga-list", ListView)
                index = list_view.index or 0
                await self.refresh_list()
                remaining = len(storage.list_sagas())
                if remaining:  # keep the highlight near where it was
                    list_view.index = min(index, remaining - 1)

        self.app.push_screen(
            ConfirmScreen(
                f"Delete the saga {escape(name)}?\n\n"
                "Everything in it (covenants, characters, laboratories, "
                "library) is deleted for good. This cannot be undone.",
                yes_label="Delete",
            ),
            handle_confirmed,
        )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id
        if item_id is None or not item_id.startswith(_SAGA_ITEM_ID_PREFIX):
            return
        saga_id = item_id.removeprefix(_SAGA_ITEM_ID_PREFIX)
        try:
            saga = storage.load_saga(saga_id)
        except _UNREADABLE as problem:
            self.notify(
                f"Couldn't open {escape(saga_id)}: {escape(str(problem))}",
                severity="error",
            )
            return
        self.app.push_screen(WorkspaceScreen(saga))
