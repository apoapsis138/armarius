"""The start screen: pick, create or delete a saga, change the save
folder, or open Help (which holds About). In a browser copy of a hosted
app it only opens sagas, each after signing in."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, cast

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

from ... import __version__, hosted_signin, paths, storage, title_page
from ...forms import saga as saga_forms
from ...markup import escape, problem
from ...models import Player
from .fields import FieldsDialog
from .forms import _saga_fields, _save_folder_dialog
from .help import HelpContext, HelpScreen, shown_keys
from .prompts import (
    ConfirmScreen,
    MenuScreen,
    _new_passcode_dialog,
    _sign_in_dialog,
)
from .widgets import BottomBar
from .workspace import WorkspaceScreen

if TYPE_CHECKING:
    from ..app import ArsMagicaManagerApp

_SAGA_ITEM_ID_PREFIX = "saga-"
#: What loading a damaged or hand-edited saga file can raise.
#: A saga file that can't be read: shapes.py names a field of the wrong
#: shape as ValueError.
_UNREADABLE = (OSError, ValueError, KeyError)


class SagaPickerScreen(Screen[None]):
    """Lists existing sagas; offers to create a new one or delete one."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("n", "create_saga", "New Saga"),
        ("d", "delete_saga", "Delete Saga"),
        Binding("delete", "delete_saga", "Delete Saga", show=False),
        ("m", "more", "More"),
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
        yield Static(self._folder_text(), id="picker-folder")
        yield Static(
            f"[dim]Armarius {__version__}, a saga manager for Ars Magica[/]",
            id="picker-version",
        )
        yield BottomBar(right_actions=["help"])

    async def on_mount(self) -> None:
        await self.refresh_list()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        # Players in a browser open sagas; only the storyguide's own window
        # makes or deletes them, or moves the saves.
        return not (
            action in ("create_saga", "delete_saga", "more") and self.app.is_web
        )

    def _folder_text(self) -> str:
        """Which folder the sagas are read from, and what chose it (not in
        a player's browser: the host's folders are the storyguide's
        business)."""
        if self.app.is_web:
            return ""
        return (
            f"[dim]Save folder: {escape(str(paths.data_dir()))} "
            f"({paths.source_text()})[/]"
        )

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
                saga_forms.create_saga(values)
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

    def action_more(self) -> None:
        def chosen(key: str | None) -> None:
            if key == "save_folder":
                self.change_save_folder()

        self.app.push_screen(
            MenuScreen("More", [("f", "save_folder", "Change save folder")]), chosen
        )

    def change_save_folder(self) -> None:
        """Choose another save folder, moving the saves there if asked,
        and read the sagas from it from now on."""
        if paths.source() == "env":
            self.notify(
                f"The save folder is set by {paths.env_var()}: unset it to "
                "choose one here.",
                severity="warning",
            )
            return
        old = paths.data_dir()

        async def handle_result(result: tuple[Path, bool] | None) -> None:
            if result is None:
                return
            folder, move = result
            notes = paths.move_user_data(old, folder) if move else []
            paths.remember_data_dir(folder)
            self.query_one("#picker-folder", Static).update(self._folder_text())
            await self.refresh_list()
            moved = sum(1 for note in notes if note.startswith("Moved"))
            left = [note for note in notes if not note.startswith("Moved")]
            self.notify(
                escape(
                    "\n".join(
                        [f"Moved {moved} file(s)." if move else "Nothing moved."] + left
                    )
                ),
                title="Save folder: " + escape(str(folder)),
                severity="warning" if left else "information",
                timeout=15,
            )

        self.app.push_screen(_save_folder_dialog(old), handle_result)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id
        if item_id is None or not item_id.startswith(_SAGA_ITEM_ID_PREFIX):
            return
        self.open_saga(item_id.removeprefix(_SAGA_ITEM_ID_PREFIX))

    def open_saga(self, saga_id: str) -> None:
        """Open the saga `saga_id` in the workspace (in a player's browser,
        once they have signed in)."""
        try:
            saga = storage.load_saga(saga_id)
        except _UNREADABLE as problem:
            self.notify(
                escape(storage.unreadable_note(saga_id, problem)),
                severity="error",
                timeout=20,
            )
            return
        if not self.app.is_web:
            title_page.remember_saga(saga.id)
            self.app.push_screen(WorkspaceScreen(saga))
            return
        if not saga.players:
            self.notify(
                f"No one can sign in to {escape(saga.name)} yet: the storyguide "
                "adds players on its Saga Content Players tab.",
                severity="warning",
            )
            return

        def go_in(player: Player) -> None:
            self._set_player(player)
            self.app.push_screen(WorkspaceScreen(saga))

        def signed_in(outcome: hosted_signin.Outcome | None) -> None:
            if outcome is None or outcome.player is None:
                return
            player = outcome.player
            if not outcome.short:
                go_in(player)
                return
            # A passcode shorter than the rule allows: a new one, or (this
            # once) Not Now.
            put_off = outcome.may_put_off

            def renewed(saved: bool | None) -> None:
                if saved:
                    self.notify("Your new passcode is saved.")
                    go_in(player)
                elif put_off:
                    hosted_signin.SignInBook(
                        hosted_signin.book_path(saga.name)
                    ).spend_short(player)
                    self.notify(
                        "Signed in with your short passcode for the last time: "
                        "choose a new one next time.",
                        severity="warning",
                    )
                    go_in(player)

            self.app.push_screen(
                _new_passcode_dialog(saga, player, may_put_off=put_off), renewed
            )

        self.app.push_screen(_sign_in_dialog(saga), signed_in)

    def _set_player(self, player: Player | None) -> None:
        """Record who is signed in on the app (ArsMagicaManagerApp.player)."""
        cast("ArsMagicaManagerApp", self.app).player = player
