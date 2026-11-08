"""The desktop's Host for Players window: the one place the Storyguide
hosts the saga and manages who connects.

At the top, how players join: with Armarius on their own computers, over
the internet through the Storyguide's tunnel (Remote seats), or in a
browser or terminal on a private network. Under it, whether the saga is
hosted, with Host and Stop Hosting. For Remote seats it also shows the
host's six words, read aloud on the group's call, and three tabs: Requests
(Issue Invite, then Approve or Reject each device that redeems one), Seats
(Revoke, the idle-expiry setting, Rotate Host Key) and Log.

The window runs the core's commands (forms/remote_seats.py, forms/hosting.py)
and draws its rows; it decides nothing itself. It stays open beside the
game, without blocking it, and looks for new requests every few seconds
while it is shown. Nothing it does changes the saga file.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import (
    QGuiApplication,
    QHideEvent,
    QShowEvent,
    QTextOption,
)
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .. import hosting
from ..commands import Command, Empty, Finished, Picked, Refuse, drive
from ..forms import hosting as hosting_forms
from ..forms.remote_seats import IssuedInvite, SeatsDesk
from ..remote.identity import NoKeychainError
from ..remote.plan import RemotePlan
from . import sounds
from .forms import Ask, NoticeDialog, Sheet, ask_question
from .pictures import SERIF
from .themes import Palette, wash_style
from .widgets import (
    edit_button,
    fill_ledger,
    ledger_choice,
    ledger_table,
    serif,
    text,
)

TITLE = "Host for Players"
REMOTE, BROWSER = "remote", "browser"
#: How often the window looks for new requests while it is shown (ms).
REFRESH_EVERY = 2000
#: The narrowest the window may be drawn.
NARROWEST = 560


class ModeCard(QPushButton):
    """One way players join, as a card like the title page's ways on: its
    name over a line saying what it is. The chosen one is edged in the
    rubric colour and says "✓ Chosen", so it never rests on colour alone."""

    def __init__(self, name: str, detail: str, p: Palette) -> None:
        super().__init__()
        self.p = p
        self.setObjectName("modeCard")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAccessibleName(name)
        self.setFixedHeight(80)
        self.setStyleSheet(
            f"""
            QPushButton#modeCard {{
                background: {p["surface"]};
                border: 1px solid {p["accent"]};
                border-radius: 3px;
            }}
            QPushButton#modeCard:checked {{
                border: 2px solid {p["heading"]};
                background: {wash_style(p)};
            }}
            QPushButton#modeCard:hover, QPushButton#modeCard:focus {{
                border: 2px solid {p["accent"]};
            }}
            """
        )
        column = QVBoxLayout(self)
        column.setContentsMargins(12, 8, 12, 8)
        column.setSpacing(1)
        self.name = text(name, p["heading"], serif(14))
        # One line each (short enough at the narrowest window): a button
        # doesn't grow for a label that wraps.
        self.detail = text(detail, p["label"], serif(11.5, italic=True))
        self.mark = text("✓ Chosen", p["heading"], serif(11.5, bold=True))
        for label in (self.name, self.detail, self.mark):
            label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            column.addWidget(label)
        self.toggled.connect(self._marked)
        self._marked(False)

    def _marked(self, on: bool) -> None:
        self.mark.setVisible(on)


class InviteDialog(Sheet):
    """What Issue Invite ends with: the line to paste into a chat, with a
    Copy button, and the host's six words to read out. Shown once: the
    host keeps only a hash of the code."""

    def __init__(
        self, issued: IssuedInvite, p: Palette, parent: QWidget | None = None
    ) -> None:
        super().__init__(f"Invite for {issued.player}", p, "Done", parent)
        self.issued = issued
        self.column.addWidget(
            text(
                f"Send {issued.player} this line by chat or email. It works once, "
                f"on one device, until {issued.expires}. It is shown only now: "
                "copy it before you close this window.",
                p["foreground"],
                serif(13),
                wrap=True,
            )
        )
        line_row = QHBoxLayout()
        # Shown whole, wrapped anywhere, in plain letters: a code is read
        # character by character if it must be typed.
        self.line = QPlainTextEdit(issued.line)
        self.line.setReadOnly(True)
        # The app's style sheet sets every input in its display face, all
        # capitals; the code is set in the body's serif instead.
        self.line.setStyleSheet(f"font-family: '{SERIF}'; font-size: 13pt;")
        self.line.setWordWrapMode(QTextOption.WrapMode.WrapAnywhere)
        self.line.setFixedHeight(4 * self.line.fontMetrics().lineSpacing() + 12)
        line_row.addWidget(self.line, 1)
        self.copy = edit_button("Copy", p, self._copy, "export")
        line_row.addWidget(self.copy, 0, Qt.AlignmentFlag.AlignTop)
        self.column.addLayout(line_row)
        self.column.addWidget(
            text(
                "Then, on your voice call, read them these six words. Their app "
                "shows the same six before it asks for their passcode; if any "
                "word differs, the invite was changed on its way and they must "
                "not go on.",
                p["foreground"],
                serif(13),
                wrap=True,
            )
        )
        self.column.addWidget(_words_label(issued.host_words, p))
        self.save.clicked.connect(self.accept)
        self.cancel.hide()
        self.finish()
        self.setMinimumWidth(NARROWEST)

    def _copy(self) -> None:
        QGuiApplication.clipboard().setText(self.issued.line)
        self.copy.setText(" Copied")


def _words_label(words: str, p: Palette) -> QLabel:
    label = text(words, p["heading"], serif(17, bold=True))
    label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    return label


class HostingWindow(Sheet):
    """The Host for Players window (see the module's docstring)."""

    def __init__(
        self,
        desk: SeatsDesk,
        p: Palette,
        parent: QWidget | None = None,
        *,
        ask: Ask | None = None,
        changed: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(TITLE, p, "Close", parent)
        self.setModal(False)
        self.desk, self.p = desk, p
        self.ask: Ask = ask or (lambda dialog: dialog.exec())
        self.changed = changed or (lambda: None)
        self.column.addWidget(
            text("Players join with", p["label"], serif(12.5, italic=True))
        )
        self.modes = QButtonGroup(self)
        self.modes.setExclusive(True)
        self.remote_choice = ModeCard(
            "Remote seats", "Their own Armarius, over the internet", p
        )
        self.browser_choice = ModeCard(
            "Browser or terminal", "On your private network", p
        )
        cards = QHBoxLayout()
        cards.setSpacing(12)
        for choice in (self.remote_choice, self.browser_choice):
            self.modes.addButton(choice)
            cards.addWidget(choice, 1)
            choice.toggled.connect(lambda _on: self.refresh())
        self.column.addLayout(cards)
        status_row = QHBoxLayout()
        self.status = text("", p["foreground"], serif(13), wrap=True)
        status_row.addWidget(self.status, 1)
        self.start = edit_button("Host", p, self._host, "players")
        self.stop = edit_button("Stop Hosting", p, self._stop_hosting, "players")
        status_row.addWidget(self.start, 0, Qt.AlignmentFlag.AlignTop)
        status_row.addWidget(self.stop, 0, Qt.AlignmentFlag.AlignTop)
        self.column.addLayout(status_row)
        self.remote = self._remote_panel()
        self.column.addWidget(self.remote, 1)
        self.browser = self._browser_panel()
        self.column.addWidget(self.browser, 1)
        self.save.clicked.connect(self.close)
        self.cancel.hide()
        self.finish()
        self.setMinimumWidth(NARROWEST)
        self.resize(820, 680)
        plan = hosting.HOST.plan if hosting.HOST.running else None
        browser = plan is not None and not isinstance(plan, RemotePlan)
        (self.browser_choice if browser else self.remote_choice).setChecked(True)
        self.timer = QTimer(self)
        self.timer.setInterval(REFRESH_EVERY)
        self.timer.timeout.connect(self.refresh)
        self.refresh()

    # -- building --------------------------------------------------------------

    def _remote_panel(self) -> QWidget:
        p = self.p
        panel = QWidget()
        column = QVBoxLayout(panel)
        column.setContentsMargins(0, 6, 0, 0)
        column.setSpacing(6)
        self.words_lead = text(
            "Your host's six words, to read aloud on the call when a player "
            "first connects:",
            p["label"],
            serif(12.5, italic=True),
            wrap=True,
        )
        column.addWidget(self.words_lead)
        self.words = _words_label("", p)
        column.addWidget(self.words)
        self.pin = text("", p["dim"], serif(11), wrap=True)
        self.pin.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        column.addWidget(self.pin)
        self.tabs = QTabWidget()
        # The chosen tab in bold as well as underlined: marked by weight
        # and place, not by colour alone.
        self.tabs.setStyleSheet("QTabBar::tab:selected { font-weight: bold; }")
        self.tabs.addTab(self._requests_tab(), "Requests")
        self.tabs.addTab(self._seats_tab(), "Seats")
        self.tabs.addTab(self._log_tab(), "Log")
        column.addWidget(self.tabs, 1)
        return panel

    def _browser_panel(self) -> QWidget:
        """What the browser way is, in a few words, with room under it."""
        panel = QWidget()
        column = QVBoxLayout(panel)
        column.setContentsMargins(0, 6, 0, 0)
        column.addWidget(
            text(
                "Players open the saga in a web browser (or over SSH) on their "
                "own computers and sign in with the name and passcode you gave "
                "them on Saga Content's Players. Host on your private network's "
                "address (Tailscale or ZeroTier), never one the internet can "
                "reach. Invites and seats are for Remote seats only.",
                self.p["label"],
                serif(12.5, italic=True),
                wrap=True,
            )
        )
        column.addStretch(1)
        return panel

    def _buttons(self, *buttons: QPushButton) -> QHBoxLayout:
        row = QHBoxLayout()
        for button in buttons:
            row.addWidget(button)
        row.addStretch(1)
        return row

    def _requests_tab(self) -> QWidget:
        p = self.p
        tab = QWidget()
        column = QVBoxLayout(tab)
        self.issue = edit_button("Issue Invite", p, self._issue, "players")
        self.approve_button = edit_button("Approve", p, self._approve, "edit")
        self.reject_button = edit_button("Reject", p, self._reject, "delete")
        column.addLayout(
            self._buttons(self.issue, self.approve_button, self.reject_button)
        )
        self.requests = ledger_table(
            ["Player", "Device", "Its three words", "Asked"], p
        )
        column.addWidget(self.requests, 1)
        self.no_requests = text(
            "No device is waiting. When a player redeems an Invite, their "
            "device shows here: ask them to read you its three words, then "
            "Approve.",
            p["dim"],
            serif(12.5, italic=True),
            wrap=True,
        )
        column.addWidget(self.no_requests)
        return tab

    def _seats_tab(self) -> QWidget:
        p = self.p
        tab = QWidget()
        column = QVBoxLayout(tab)
        self.revoke = edit_button("Revoke", p, self._revoke, "delete")
        self.idle = edit_button("Idle Expiry", p, self._idle, "edit")
        self.rotate = edit_button("Rotate Host Key", p, self._rotate, "update")
        column.addLayout(self._buttons(self.revoke, self.idle, self.rotate))
        self.idle_line = text("", p["label"], serif(12.5, italic=True), wrap=True)
        column.addWidget(self.idle_line)
        self.seats = ledger_table(
            ["Player", "Device", "Words", "Last seen", "State"], p
        )
        self.live_seats: set[str] = set()
        self.seats.itemSelectionChanged.connect(self._seat_chosen)
        column.addWidget(self.seats, 1)
        return tab

    def _seat_chosen(self) -> None:
        """Revoke acts on a live seat only."""
        self.revoke.setEnabled(ledger_choice(self.seats) in self.live_seats)

    def _log_tab(self) -> QWidget:
        p = self.p
        tab = QWidget()
        column = QVBoxLayout(tab)
        row = QHBoxLayout()
        row.addWidget(text("Show", p["label"], serif(12.5, italic=True)))
        self.log_filter = QComboBox()
        self.log_filter.currentIndexChanged.connect(lambda _index: self._fill_log())
        row.addWidget(self.log_filter)
        row.addStretch(1)
        column.addLayout(row)
        self.log = ledger_table(["When", "What happened", "Player", "Device"], p)
        column.addWidget(self.log, 1)
        return tab

    # -- showing -----------------------------------------------------------------

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.timer.start()

    def hideEvent(self, event: QHideEvent) -> None:
        self.timer.stop()
        super().hideEvent(event)

    def mode(self) -> str:
        return REMOTE if self.remote_choice.isChecked() else BROWSER

    def refresh(self) -> None:
        """Draw the status and every list again from the files."""
        running = hosting.HOST.running
        remote = self.mode() == REMOTE
        for choice in (self.remote_choice, self.browser_choice):
            choice.setEnabled(not running)
        self.status.setText(_status())
        self.start.setVisible(not running)
        self.stop.setVisible(running)
        self.remote.setVisible(remote)
        self.browser.setVisible(not remote)
        if not remote:
            self.setWindowTitle(TITLE)
            return
        try:
            words, pin = self.desk.words()
        except NoKeychainError as error:
            self.words.setText("")
            self.pin.setText(str(error))
            self.tabs.setEnabled(False)
            return
        self.tabs.setEnabled(True)
        self.words.setText(words)
        self.pin.setText(f"Fingerprint: {pin}")
        requests = self.desk.requests()
        fill_ledger(
            self.requests,
            [(r.id, [r.player, r.device, r.words, r.asked]) for r in requests],
        )
        self.requests.setVisible(bool(requests))
        self.no_requests.setVisible(not requests)
        self.approve_button.setEnabled(bool(requests))
        self.reject_button.setEnabled(bool(requests))
        waiting = f" ({len(requests)} waiting)" if requests else ""
        self.setWindowTitle(TITLE + waiting)
        self.tabs.setTabText(0, "Requests" + waiting)
        seats = self.desk.seats()
        self.live_seats = {s.id for s in seats if s.live}
        fill_ledger(
            self.seats,
            [
                (s.id, [s.player, s.device, s.words, s.last_seen, s.state])
                for s in seats
            ],
        )
        self._seat_chosen()
        self.idle_line.setText(
            f"A seat nobody signs in from for {self.desk.idle_days()} days stops "
            "working."
        )
        self._fill_filter()
        self._fill_log()

    def _fill_filter(self) -> None:
        wanted = [("Everyone", ""), *self.desk.log_players()]
        have = [
            (self.log_filter.itemText(i), self.log_filter.itemData(i))
            for i in range(self.log_filter.count())
        ]
        if have == wanted:
            return
        chosen = self.log_filter.currentData()
        self.log_filter.blockSignals(True)
        self.log_filter.clear()
        for name, player_id in wanted:
            self.log_filter.addItem(name, player_id)
        index = self.log_filter.findData(chosen)
        self.log_filter.setCurrentIndex(max(index, 0))
        self.log_filter.blockSignals(False)

    def _fill_log(self) -> None:
        player_id = self.log_filter.currentData() or None
        rows = self.desk.log_rows(player_id)
        fill_ledger(
            self.log,
            [
                (str(i), [r.when, r.event, r.player, r.device])
                for i, r in enumerate(rows)
            ],
        )

    # -- acting --------------------------------------------------------------------

    def run(self, command: Command) -> None:
        """Run a command's steps, each as a window over this one; then show
        what it ended with and draw everything again."""
        outcome = drive(command, lambda q: ask_question(q, self.p, self, self.ask))
        if isinstance(outcome, Refuse | Empty):
            sounds.play("tock")
            self.tell(outcome.title, outcome.why)
        elif isinstance(outcome, Finished):
            end = outcome.end
            if isinstance(end, Picked) and isinstance(end.value, IssuedInvite):
                sounds.play("seal")
                self.ask(InviteDialog(end.value, self.p, self))
            elif isinstance(end, list) and end:
                sounds.play("quill")
                self.tell(TITLE, "\n".join(str(line) for line in end))
        self.refresh()
        self.changed()

    def tell(self, title: str, words: str) -> None:
        self.ask(NoticeDialog(title, words, self.p, self))

    def _host(self) -> None:
        if self.mode() == REMOTE:
            self.run(self.desk.host_form())
        else:
            self.run(hosting_forms.host_form())

    def _stop_hosting(self) -> None:
        self.run(hosting_forms.stop_hosting())

    def _issue(self) -> None:
        self.run(self.desk.issue_invite())

    def _approve(self) -> None:
        chosen = ledger_choice(self.requests)
        if chosen is not None:
            self.run(self.desk.approve(chosen))

    def _reject(self) -> None:
        chosen = ledger_choice(self.requests)
        if chosen is not None:
            self.run(self.desk.reject(chosen))

    def _revoke(self) -> None:
        chosen = ledger_choice(self.seats)
        if chosen is not None:
            self.run(self.desk.revoke(chosen))

    def _idle(self) -> None:
        self.run(self.desk.idle_form())

    def _rotate(self) -> None:
        self.run(self.desk.rotate())


def _status() -> str:
    """Whether and how the saga is hosted, in a line."""
    if not hosting.HOST.running:
        return "Not hosted."
    return hosting_forms.hosting_note()
