"""What keeps the Chronicle pane fed: the host's Chronicle file watched
for a Remote seat's writes, or at a seat, the entries its host sends
handed from the connection's thread to the window's; a damaged Chronicle
said once; and the Table the pane and the forms act at. The window makes
one call when it draws (`draw`), and one on its tick (`refresh`).

Pattern: Mediator between the window, the pane and where the Chronicle
comes from, as joined.py is for a Joined game's talk with its host."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QFileSystemWatcher, QObject, Signal

from .. import at_table, chronicle, virtual_tabletop
from ..markup import escape
from ..models import Saga, Session
from .chronicle_pane import ChroniclePane, remembered_collapsed

if TYPE_CHECKING:
    # The seat's connection libraries stay unloaded until a game is joined.
    from ..remote.seat_session import SeatSession

#: Says something to the user: a title and the words.
Tell = Callable[[str, str], None]


class _SeatEvents(QObject):
    """Hands a Chronicle entry from a Remote seat's connection thread to
    the window's (a queued signal)."""

    arrived = Signal(str, object, int)


class ChronicleWiring(QObject):
    """Feeds `pane` while a Session is under way, and shows or hides
    `show_button` (the window's Chronicle button) with it."""

    def __init__(
        self,
        pane: ChroniclePane,
        show_button: Callable[[bool], None],
        tell: Tell,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self.pane, self._show_button, self._tell = pane, show_button, tell
        #: The Chronicle file found damaged, said once.
        self._damaged: Path | None = None
        #: Watches the host's Chronicle file, so a Remote seat's roll (the
        #: listener, another process, writes it) shows at once.
        self.watch = QFileSystemWatcher(self)
        self.watch.fileChanged.connect(self._changed)
        #: At a Remote seat: what the host sent of the Chronicle, in memory
        #: only.
        self.seat_held: chronicle.SeatChronicle | None = None
        self._events = _SeatEvents(self)
        self._events.arrived.connect(self._seat_entry)
        #: The Session already Under way when the saga was opened: its pane
        #: comes back as it was left; one begun since opens.
        self.under_way_at_open: str | None = None

    def opened(self, saga: Saga) -> None:
        """A saga was opened: note the Session already under way."""
        found = chronicle.under_way(saga)
        self.under_way_at_open = found.id if found is not None else None

    def left_game(self) -> None:
        """A Joined game ended: its Chronicle was held in memory only."""
        self.seat_held = None

    def draw(self, saga: Saga | None, seat: SeatSession | None, player_id: str) -> None:
        """The pane and its button for `saga`: at a Remote seat (`seat`,
        signed in as `player_id`), fed by its host, else on the host's own
        computer while the Virtual Tabletop preview is on. A Session newly
        begun opens the pane; after a restart it comes back as it was
        left."""
        if saga is not None and seat is not None:
            self._draw_seat(saga, seat, player_id)
            return
        at_table.use_seat(None)
        session = (
            chronicle.under_way(saga)
            if saga is not None and virtual_tabletop.on()
            else None
        )
        self._show_button(session is not None)
        if saga is None or session is None:
            self.pane.detach()
            self._watch(None)
            return
        try:
            book = chronicle.read(saga, session)
        except ValueError as problem:
            # A damaged Chronicle hides the pane, said once; the page works.
            self._hide_damaged(chronicle.path_of(saga, session), problem)
            return
        fresh = self.pane.book is not book
        self.pane.attach(saga, session, book, chronicle.here())
        self._watch(book.path)
        if fresh:
            begun_now = session.id != self.under_way_at_open
            self.pane.set_collapsed(False if begun_now else remembered_collapsed())
            # Opened once on Begin; from then on as it was left.
            self.under_way_at_open = session.id

    def refresh(self) -> None:
        """Catch up with what the seat listener wrote (the watcher's
        fallback); a file found damaged hides the pane, said once."""
        book = self.pane.book
        if not isinstance(book, chronicle.Chronicle):
            return
        try:
            book.refresh()
        except ValueError as problem:
            self._watch(None)
            self._hide_damaged(book.path, problem)

    def _hide_damaged(self, path: Path, problem: ValueError) -> None:
        self.pane.detach()
        self._show_button(False)
        if self._damaged != path:
            self._damaged = path
            self._tell("Chronicle", escape(str(problem)))

    def _watch(self, path: Path | None) -> None:
        """Watch the host's Chronicle file at `path` (None: none)."""
        watched = self.watch.files()
        if path is not None and str(path) in watched:
            return
        if watched:
            self.watch.removePaths(watched)
        if path is not None and path.is_file():
            self.watch.addPath(str(path))

    def _changed(self, path: str) -> None:
        """The Chronicle file grew (a Remote seat's roll): catch up."""
        self.refresh()
        if path not in self.watch.files() and Path(path).is_file():
            self.watch.addPath(path)  # replaced, not just grown

    def _draw_seat(self, saga: Saga, seat: SeatSession, player_id: str) -> None:
        """At a Remote seat: the pane while the host's Session is under
        way, fed by the Chronicle's events connection; no setting needed
        here (the host turned the preview on)."""
        session = chronicle.under_way(saga)
        self._show_button(session is not None)
        if session is None:
            self.pane.detach()
            at_table.use_seat(None)
            return
        held = self._held(seat, session)
        fresh = self.pane.book is not held
        table = seat.table(held)
        self.pane.attach(saga, session, held, player_id, table)
        at_table.use_seat(table)
        if fresh:
            self.pane.set_collapsed(remembered_collapsed())

    def _held(self, seat: SeatSession, session: Session) -> chronicle.SeatChronicle:
        """The seat's Chronicle, its events connection followed once."""
        held = self.seat_held
        if held is None:
            held = self.seat_held = chronicle.SeatChronicle()
            events = self._events
            # Deliveries are marked with the Chronicle they're for: one
            # still on its way from a game since left is dropped.
            mark = id(held)

            def deliver(session_id: str, entry: chronicle.Entry) -> None:
                events.arrived.emit(session_id, entry, mark)

            seat.follow_chronicle(deliver, lambda: (held.session_id, held.last))
        elif held.session_id and held.session_id != session.id:
            held.clear()  # the host began another Session
        return held

    def _seat_entry(self, session_id: str, entry: chronicle.Entry, mark: int) -> None:
        """An entry the host sent, handed to this thread."""
        held = self.seat_held
        if held is not None and id(held) == mark:
            held.take(session_id, entry)
