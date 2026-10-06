"""The start screen: pick, create or delete a saga, or open Help (which
holds About). In a browser copy of a hosted app it only opens
sagas, each after signing in."""

from __future__ import annotations

from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.screen import Screen
from textual.widgets import (
    Header,
    Label,
    ListItem,
    ListView,
    Static,
)

from .. import __version__, creation, storage
from ..markup import escape, problem
from ..models import Player
from .fields import FieldsDialog
from .forms import _saga_fields
from .help import HelpContext, HelpScreen, shown_keys
from .prompts import ConfirmScreen, _sign_in_dialog
from .widgets import BottomBar
from .workspace import WorkspaceScreen

_SAGA_ITEM_ID_PREFIX = "saga-"
#: What loading a damaged or hand-edited saga file can raise.
_UNREADABLE = (OSError, ValueError, TypeError, KeyError)


class SagaPickerScreen(Screen[None]):
    """Lists existing sagas; offers to create a new one or delete one."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("n", "create_saga", "New Saga"),
        ("d", "delete_saga", "Delete Saga"),
        Binding("delete", "delete_saga", "Delete Saga", show=False),
        ("q", "quit", "Quit"),
        # Shown at the footer's right end (BottomBar right_actions).
        ("question_mark", "help", "Help"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            "Select a saga to open and sign in."
            if self.app.is_web
            else "Select a saga to open, press 'n' to create a new one, "
            "or 'd' to delete the highlighted one.",
            id="picker-hint",
        )
        yield ListView(id="saga-list")
        yield Static(f"[dim]Ars Magica Manager {__version__}[/]", id="picker-version")
        yield BottomBar(right_actions=["help"])

    async def on_mount(self) -> None:
        await self.refresh_list()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        # Players in a browser open sagas; only the storyguide's own window
        # makes or deletes them.
        return not (action in ("create_saga", "delete_saga") and self.app.is_web)

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
                summary = f"{escape(saga_id)}  —  {problem("can't be read")}"
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

    def action_help(self) -> None:
        self.app.push_screen(HelpScreen(self.help_context()))

    def help_context(self) -> HelpContext:
        """Help on the saga picker: its page; About is under REFERENCE."""
        return HelpContext(["saga-picker"], "Saga picker", shown_keys(self, ("help",)))

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
        if not self.app.is_web:
            self.app.push_screen(WorkspaceScreen(saga))
            return
        if not saga.players:
            self.notify(
                f"No one can sign in to {escape(saga.name)} yet: the storyguide "
                "adds players on its Players node.",
                severity="warning",
            )
            return

        def signed_in(player: Player | None) -> None:
            if player is not None:
                self._set_player(player)
                self.app.push_screen(WorkspaceScreen(saga))

        self.app.push_screen(_sign_in_dialog(saga), signed_in)

    def _set_player(self, player: Player | None) -> None:
        """Record who is signed in on the app (ArsMagicaManagerApp.player)."""
        self.app.player = player  # type: ignore[attr-defined]
