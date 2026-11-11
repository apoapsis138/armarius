"""The desktop main window: one page at a time, the way a book is read,
with a trail across the top back to the pages above it (Sagas, the saga,
the covenant, the character, their familiar) and a printer's headpiece
over every page.

The pages are the shelf of sagas, a saga's covenants, a covenant (its
people, laboratories and seasons), a laboratory, a character's sheet and a
familiar's. Where the
reader is is a list of places, the trail; the page shown is built from
the last one, so changing the theme just builds it again.

A sheet's Edit buttons open the same forms the terminal shows
(forms/character.py); saving one saves the saga, merged with whatever the
terminal app (or the hosted copies players use) saved meanwhile, so the
two are safe to run side by side.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import shiboken6
from PySide6.QtCore import QByteArray, QEvent, Qt, QTimer
from PySide6.QtGui import (
    QCloseEvent,
    QFont,
    QKeySequence,
    QShortcut,
    QShowEvent,
)
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .. import (
    catalog,
    help_text,
    hosting,
    hotkeys,
    joined_games,
    paths,
    presence,
    references,
    saga_index,
    seat,
    storage,
    stores,
    storyguides,
    title_page,
    undo_season,
    viewing,
)
from .. import familiars as fam
from .. import print_layout as pl
from ..actions import NodeKind
from ..commands import (
    Cancelled,
    ChooseFile,
    Command,
    Confirm,
    Empty,
    Go,
    Picked,
    Question,
    Refuse,
    Then,
    drive,
)
from ..forms import advance as advance_forms
from ..forms import creation as creation_forms
from ..forms import menu as menu_forms
from ..forms import printing as print_forms
from ..forms import saga as saga_forms
from ..joined_games import JoinedGame
from ..markup import escape
from ..models import (
    Character,
    Covenant,
    Familiar,
    Laboratory,
    Player,
    Saga,
    season_order,
)
from ..paths import APP_NAME
from ..saga_store import LocalStore, Refreshed, SagaStore
from ..sheets import laboratory as ls
from . import atlas as atlas_page
from . import (
    choices,
    joined,
    medallions,
    motion,
    pictures,
    print_sheet,
    printing,
    season_panel,
    sounds,
)
from .bestiary import CreaturePage
from .character_sheet import CharacterSheet
from .closing import confirm_close_while_hosting
from .note import NoteStrip

#: How often the window looks for another copy's save (ms), as the
#: terminal does; for a Joined game, how often it asks the host.
SHARED_TICK_MS = 2000
REMOTE_TICK_MS = 5000
from .conflicts import FightPage, SiegePage
from .covenant import CovenantPage
from .familiar import FamiliarPage
from .finder import FinderPanel, eye_icon, magnifier_icon
from .forms import ConfirmDialog, NoticeDialog, ask_question, run_steps
from .help import HelpPage

if TYPE_CHECKING:
    from ..remote.seat_session import SeatSession
    from .hosting import HostingWindow
from .icon import app_icon
from .laboratory import LaboratoryPage
from .manage import Moded, RecordControls
from .markup_html import plain
from .medallions import SeasonHeadpiece
from .menus import Placer
from .pages import JoinedShelf, SagaPage, SagaShelf
from .players_section import players_section
from .region import NeighbourPage
from .saga_content import SagaContentPage
from .season_panel import SeasonPanel
from .seasons import SeasonsPage
from .sessions_section import sessions_section
from .settings_window import SettingsWindow
from .stores import SPOT_LISTS, StorePage
from .style import gilding, snapping
from .style.frame import (
    MAXIMISE,
    BarRule,
    DragStrip,
    Grips,
    TopStrip,
    WindowButtons,
    native_frame_event,
)
from .style.paper import Paper
from .themes import (
    Palette,
    Theme,
    liveries,
    remember_theme,
    saved_theme,
    style_sheet,
)
from .title import TitleScreen
from .tribunal import TribunalPage
from .widgets import Codex
from .worksheet import WorksheetPage

(
    SHELF,
    SAGA,
    COVENANT,
    CHARACTER,
    LABORATORY,
    FAMILIAR,
    CONTENT,
    WORKSHEET,
    SEASONS,
    HELP,
    TRIBUNAL,
    NEIGHBOUR,
    CREATURE,
    FIGHT,
    SIEGE,
    ARMARIUM,
    CUSTODIA,
) = (
    "shelf",
    "saga",
    "covenant",
    "character",
    "laboratory",
    "familiar",
    "content",
    "worksheet",
    "seasons",
    "help",
    "tribunal",
    "neighbour",
    "creature",
    "fight",
    "siege",
    # The saga's stores: a Place's kind is the store's key (stores.STORES).
    stores.ARMARIUM,
    stores.CUSTODIA,
)


def dress_application(app: QApplication, p: Palette) -> None:
    """Give the whole app the theme `p`: its font, style sheet, gilding and
    choice marks (the window does it on every theme change; a probe that
    draws a window does it too, so its pictures match the app)."""
    app.setFont(QFont(pictures.UI, 10))
    app.setStyleSheet(style_sheet(p, pictures.SERIF))
    gilding.gild_application(app, p)
    choices.ink_choices(app, p)


#: Each page's help topic (help_text: a page's id), most specific first.
_HELP_IDS = {
    SHELF: ["saga-picker"],
    SAGA: ["saga", "workspace"],
    COVENANT: ["covenant"],
    CHARACTER: ["character"],
    LABORATORY: ["laboratory"],
    FAMILIAR: ["familiar"],
    CONTENT: ["saga-content"],
    WORKSHEET: ["creation-worksheet"],
    SEASONS: ["seasons", "advance-season", "season-summary"],
    TRIBUNAL: ["tribunal"],
    NEIGHBOUR: ["neighbour"],
    CREATURE: ["creature"],
    FIGHT: ["fights", "conflicts"],
    SIEGE: ["sieges", "conflicts"],
    ARMARIUM: [stores.ARMARIUM],
    CUSTODIA: [stores.CUSTODIA],
}

#: The prefix of each page's tab topics; a character's are the plain
#: "tab-" ones.
_TAB_PREFIX = {
    COVENANT: "tab-cov-",
    LABORATORY: "tab-lab-",
    FAMILIAR: "tab-fam-",
    CONTENT: "tab-content-",
    TRIBUNAL: "tab-trib-",
    NEIGHBOUR: "tab-nb-",
    CREATURE: "tab-cr-",
    SAGA: "saga-",
    CHARACTER: "tab-",
}
_OTHER_TABS = tuple(v for k, v in _TAB_PREFIX.items() if k != CHARACTER)

#: The chapters whose help is a tab named otherwise, by page and the
#: chapter's name (folded): the terminal's tabs are cut differently.
_CHAPTER_TABS = {
    (COVENANT, "people"): "tab-cov-inhabitants",
    (COVENANT, "covenfolk"): "tab-cov-inhabitants",
    (COVENANT, "treasury"): "tab-cov-economics",
    (LABORATORY, "specializations"): "tab-lab-attributes",
    (LABORATORY, "stores"): "tab-lab-inventory",
    (LABORATORY, "seasons"): "tab-lab-planning",
}


def _chapter_topic(kind: str, chapter: str) -> str | None:
    """The help topic (a tab's) of a page's chapter, by the chapter's
    name: _CHAPTER_TABS, else the page's tab whose title starts with it."""
    name = plain(chapter).strip().casefold()
    prefix = _TAB_PREFIX.get(kind)
    if not name or prefix is None:
        return None
    return _CHAPTER_TABS.get((kind, name)) or next(
        (
            topic.id
            for topic in help_text.book(help_text.GUI).topics.values()
            if topic.id.startswith(prefix)
            and (prefix != "tab-" or not topic.id.startswith(_OTHER_TABS))
            and topic.title.casefold().startswith(name)
        ),
        None,
    )


def _first_input(dialog: QDialog) -> QWidget | None:
    """The widget a step's typing starts in: a form's first field, a
    list's search, a question's Cancel."""
    inputs = getattr(dialog, "inputs", None)
    if inputs:
        return next(iter(inputs.values()))
    return getattr(dialog, "search", None) or getattr(dialog, "cancel", None)


def _title(command: Command) -> str:
    if isinstance(command, Confirm):
        return command.title or command.question
    return command.title


def _hidden_label(name: str) -> QLabel:
    label = QLabel()
    label.setAccessibleName(name)
    label.hide()
    return label


@dataclass(frozen=True)
class Place:
    """A page the reader has opened: what kind, and whose (a covenant's or
    a character's id; None for the saga's unassigned characters)."""

    kind: str
    id: str | None = None


#: The page that shows each kind of record a link can name
#: (references.KINDS).
_REF_PLACES: dict[str, str] = {
    "characters": CHARACTER,
    "covenants": COVENANT,
    "laboratories": LABORATORY,
    "familiars": FAMILIAR,
    "tribunals": TRIBUNAL,
    "neighbours": NEIGHBOUR,
    "creatures": CREATURE,
}

#: The chapter each page lists a Find Spot's records in, by the page's
#: Ref kind and the Spot's list.
SPOT_CHAPTERS: dict[tuple[str, str], str] = {
    ("covenants", saga_index.BOOKS): "Library",
    ("covenants", saga_index.DEVICES): "Inventory",
    ("laboratories", saga_index.BOOKS): "Stores",
    ("laboratories", saga_index.DEVICES): "Stores",
    ("characters", saga_index.BOOKS): "Inventory",
    ("characters", saga_index.DEVICES): "Inventory",
    ("characters", saga_index.SPELLS): "Hermetic Magic",
    **{(key, listed): stores.STORES[key].heading for key, listed in SPOT_LISTS.items()},
}


class MainWindow(QMainWindow):
    # A Joined game's talk with its host (joined.tick): set on the
    # instance as they change; these are where each starts.
    #: How many times the saga was saved (edited): a talk takes the host's
    #: snapshot only if none came since it began.
    edits: int = 0
    #: The talk under way in the background, if any.
    talk: joined.Talk | None = None
    #: Whether the host stopped answering (tried again each tick), and
    #: when it was last asked (time.monotonic).
    connection_lost: bool = False
    last_asked: float = 0.0
    #: This window's presence id, once a saga with players is open.
    _presence_id: str | None = None

    def __init__(self, saga_ids: list[str] | None = None) -> None:
        super().__init__()
        self.setWindowTitle("Armarius")
        self.setWindowIcon(app_icon())
        # The window draws its own title bar (frame.py).
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        #: The theme the desktop is drawn in (liveries.THEMES).
        self.theme: Theme = saved_theme()
        #: The palette pages are built in while one is printed.
        self._printing: Palette | None = None
        #: The palette the window is drawn in now.
        self._applied = self.theme.palette
        #: The Settings window, once opened.
        self._settings: SettingsWindow | None = None
        self.saga_ids = storage.list_sagas() if saga_ids is None else saga_ids
        self.saga: Saga | None = None
        #: The player seated at the open saga (seat.py); None is the
        #: storyguide's own window.
        self.player: Player | None = None
        self.trail: list[Place] = []
        #: The chapter each page was last left on, to open it there again
        #: (for this sitting only).
        self._chapters: dict[Place, str] = {}
        #: The row Find asked for on the page opening next: its chapter
        #: and where in it.
        self._spot: tuple[str, saga_index.Spot] | None = None
        #: Shows a step as a window and waits for it (a test answers it).
        self.ask: Callable[[QDialog], int] = self._present
        #: The step open now.
        self._open: QDialog | None = None
        #: The Host for Players window, once opened.
        self._hosting: HostingWindow | None = None
        self._help_from: QWidget | None = None
        #: The season just advanced, for the Seasons page to show first.
        self._played: advance_forms.Played | None = None

        bar = self._top_bar()

        self.sheet_area = QWidget()
        self.sheet_layout = QVBoxLayout(self.sheet_area)
        self.sheet_layout.setContentsMargins(0, 0, 0, 0)

        body = Paper(self.palette_)
        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(bar)
        self.headpiece = SeasonHeadpiece(self.palette_)
        layout.addWidget(self.headpiece)
        layout.addWidget(self.sheet_area, 1)
        #: The pages, and over them the title page while it is on show.
        self.stack = QStackedWidget()
        self.stack.addWidget(body)
        self.setCentralWidget(self.stack)
        self.title: TitleScreen | None = None
        self.grips = Grips(self)

        #: Where the saga on show loads and saves (ADR 0011): the data
        #: folder, or a Joined game's host.
        self.store: SagaStore = LocalStore()
        #: A Joined game's conversation with its host, while one is open.
        self.session: SeatSession | None = None
        #: A Joined game's changes not yet taken by the host.
        self.unsent = False
        #: A storyguide's switch to Playing (True) or their storyguide role
        #: (False) from a Joined game, for the host's log; None once sent.
        self.switched: bool | None = None
        #: What another copy of a hosted saga just saved, said at the foot.
        self.note = NoteStrip(self)
        #: Every few seconds, while the saga has players: pick up what
        #: another copy (a browser player, a Remote seat) saved.
        self.shared_timer = QTimer(self)
        self.shared_timer.setInterval(SHARED_TICK_MS)
        self.shared_timer.timeout.connect(self.shared_tick)
        self._unreadable = False

        self._apply_theme()
        if len(self.saga_ids) == 1:
            self.open_saga(self.saga_ids[0])
        else:
            self.go([Place(SHELF)])

    def _top_bar(self) -> QHBoxLayout:
        """The window's title bar: the trail on the left, the app's name
        in the middle (drag it to move the window), and Find, Help, a rule,
        the settings gear and the window's own buttons on the right.
        Advance Season is at the foot of each page's chapters
        (season_panel.py)."""
        self.crumbs = QHBoxLayout()
        self.crumbs.setSpacing(2)
        bar = QHBoxLayout()
        bar.setContentsMargins(12, 4, 8, 0)
        bar.addLayout(self.crumbs)
        bar.addWidget(self._here_label())
        self.drag = DragStrip(self, self.palette_, APP_NAME)
        bar.addWidget(self.drag, 1)
        bar.addWidget(self._find_button())
        #: Player view, while a saga is open: the saga as the players see
        #: it (viewing.py), said in words beside the eye while it is on.
        self.view_button = QPushButton()
        self.view_button.setFlat(True)
        self.view_button.setCheckable(True)
        self.view_button.setAccessibleName("Player view")
        self.view_button.clicked.connect(self.toggle_player_view)
        bar.addWidget(self.view_button)
        #: Play as, while a saga with players is open: the storyguide sits
        #: in a player's seat to see their desktop (choose_seat).
        self.seat_button = QPushButton()
        self.seat_button.setFlat(True)
        self.seat_button.setAccessibleName("Play as")
        self.seat_button.clicked.connect(self.choose_seat)
        bar.addWidget(self.seat_button)
        self.help = QPushButton("  Help")
        self.help.setFlat(True)
        self.help.setToolTip("Help on this page (? or F1)")
        self.help.clicked.connect(self.open_help)
        bar.addWidget(self.help)
        #: The finder dropped, while it is open.
        self.finder: FinderPanel | None = None
        #: Advance Season at the foot of the page's chapters, while shown.
        self.season_panel: SeasonPanel | None = None
        self._bind_hotkeys()
        #: Sets the settings gear apart from Help and Find.
        self.bar_rule = BarRule(self.palette_)
        bar.addWidget(self.bar_rule)
        #: The settings gear: it opens the Settings window (the theme,
        #: the sounds and Reduce Motion).
        self.settings = QPushButton()
        self.settings.setFlat(True)
        self.settings.setToolTip("Settings: theme, sounds and motion")
        self.settings.setAccessibleName("Settings")
        self.settings.clicked.connect(self.open_settings)
        bar.addWidget(self.settings)
        bar.addSpacing(10)
        self.controls = WindowButtons(self, self.palette_)
        bar.addWidget(self.controls, 0, Qt.AlignmentFlag.AlignTop)
        return bar

    def _bind_hotkeys(self) -> None:
        """The keys that work on every page (hotkeys.py): Help, Back, Quit
        and Find, each a shortcut on the whole window."""
        handlers: dict[str, Callable[[], object]] = {
            hotkeys.HELP: self._help_key,
            hotkeys.BACK: self.back,
            hotkeys.QUIT: self.close,
            hotkeys.FIND: self.open_finder,
        }
        for hotkey in hotkeys.HOTKEYS:
            act = handlers[hotkey.action]
            for key in hotkey.keys:
                # A sign typed with Shift (?) reaches Qt with Shift held on
                # some keyboards and platforms and not on others, so both
                # are bound; where both match, Qt calls it ambiguous.
                shifted = hotkeys.is_typed(key) and not key.isalnum()
                for sequence in (key, f"Shift+{key}") if shifted else (key,):
                    shortcut = QShortcut(QKeySequence(sequence), self)
                    for signal in (shortcut.activated, shortcut.activatedAmbiguously):
                        signal.connect(
                            lambda key=key, act=act: self._on_hotkey(key, act)
                        )

    def _on_hotkey(self, key: str, act: Callable[[], object]) -> None:
        """Do what `key` does, unless it is a typed key and something is
        being typed or a step is open (hotkeys.is_typed)."""
        if hotkeys.is_typed(key) and (self._typing() or self._step_open()):
            return
        act()

    def _typing(self) -> bool:
        """Whether the focus is in a field that takes typing."""
        focus = QApplication.focusWidget()
        if isinstance(focus, QComboBox):
            return focus.isEditable()
        return (
            isinstance(focus, QLineEdit | QTextEdit | QPlainTextEdit | QAbstractSpinBox)
            and not getattr(focus, "isReadOnly", lambda: False)()
        )

    def _step_open(self) -> bool:
        """Whether a step (a form, a list or a question) is open."""
        return self._open is not None and shiboken6.isValid(self._open)

    def _help_key(self) -> None:
        """? or F1: Help on the page on show; on the title page, its own
        way into Help."""
        if self.title is not None:
            self.leave_title(title_page.HELP)
        else:
            self.open_help()

    def back(self) -> None:
        """Esc: cancel the step open, else go back up the trail
        to the page above (from Help, the page it was opened on)."""
        if self.title is not None:
            return
        if self._step_open():
            assert self._open is not None
            self._open.reject()
        elif len(self.trail) > 1:
            self.go(self.trail[:-1])

    def showEvent(self, event: QShowEvent) -> None:
        snapping.make_snappable(self)
        super().showEvent(event)

    def nativeEvent(
        self, eventType: QByteArray | bytes | bytearray | memoryview, message: int
    ) -> tuple[bool, int]:
        """Windows Snap for the drawn title bar (snapping.py)."""
        result = native_frame_event(self, eventType, message)
        if result is not None:
            return True, result
        return super().nativeEvent(eventType, message)  # pyright: ignore[reportReturnType]

    def changeEvent(self, event: QEvent) -> None:
        """Maximise turns to restore (and back) as the window does."""
        if event.type() == QEvent.Type.WindowStateChange:
            snapping.make_snappable(self)
            self.controls.update()
            self.controls.buttons[MAXIMISE].update()
            self.controls.buttons[MAXIMISE].setToolTip(
                "Restore" if self.isMaximized() else "Maximise"
            )
        super().changeEvent(event)

    @property
    def palette_(self) -> Palette:
        """The theme, in the mode of the record on show: drafting vellum
        while it is In Creation (liveries.for_mode); parchment while a page
        is built for printing."""
        if self._printing is not None:
            return self._printing
        return liveries.for_mode(self.theme, self._drafting())

    def _drafting(self) -> bool:
        """Whether the page on show is a record In Creation, or its
        Creation Worksheet."""
        place = self.trail[-1] if self.trail else None
        if place is None or place.kind not in (
            CHARACTER,
            COVENANT,
            LABORATORY,
            WORKSHEET,
        ):
            return False
        record = self._creation_record(place.id)
        return record is not None and record.in_creation

    @property
    def character_id(self) -> str | None:
        place = self.trail[-1] if self.trail else None
        return place.id if place and place.kind == CHARACTER else None

    # Where to go

    # The title page

    def show_title(self) -> None:
        """Show the title page over the whole window, fading in."""
        page = title_page.title_page(
            self.saga_ids,
            joining=True,
            joined={g.saga_id: g.saga_name for g in joined_games.listed()},
        )
        self.title = TitleScreen(page, self.palette_, self.leave_title)
        TopStrip(self.title, self, self.palette_)
        self.stack.addWidget(self.title)
        self.stack.setCurrentWidget(self.title)
        self.title.setFocus()
        self.title.fade_in()

    def leave_title(self, key: str) -> None:
        """Go on from the title page by the way chosen (title_page.OPEN,
        SAGAS, NEW, JOIN, TUTORIAL or HELP). New Saga and Start a Tutorial go
        by the shelf, so cancelling its
        form leaves the shelf on show."""
        title, self.title = self.title, None
        if title is None:
            return
        self.stack.setCurrentIndex(0)
        self.stack.removeWidget(title)
        title.deleteLater()
        opening = title.page.saga_id if key == title_page.OPEN else None
        game = next((g for g in joined_games.listed() if g.saga_id == opening), None)
        if opening is not None and game is None:
            self.open_saga(opening)
            return
        self.saga_ids = storage.list_sagas()
        self.saga = None
        self.player = None
        self._use_viewer()
        self.go([Place(SHELF)])
        if game is not None:
            self.rejoin(game)  # a saga played from a seat: its passcode
        elif key == title_page.NEW:
            self.new_saga()
        elif key == title_page.TUTORIAL:
            self.start_tutorial()
        elif key == title_page.JOIN:
            self.join_game()
        elif key == title_page.HELP:
            self.open_help()

    # The shelf of sagas

    def _run_on_shelf(self, command: Command) -> tuple[bool, object]:
        """Run steps that act on the sagas themselves (saga_forms): they
        save what they change. Whether every step was answered, and what
        they ended with; a refusal is said and counts as unanswered."""
        self._place = None
        answered, end = run_steps(command, self.palette_, self, self.ask)
        if isinstance(end, Refuse):
            sounds.play("tock")
            self.tell(end.title, end.why)
            return False, end
        return answered, end

    def _shelf_again(self) -> None:
        """Read the sagas again and show the shelf."""
        self.end_joined()
        self.saga_ids = storage.list_sagas()
        self.saga = None
        self.player = None
        self._use_viewer()
        self.go([Place(SHELF)])

    def new_saga(self) -> None:
        """Create a New Saga and open it."""
        answered, end = self._run_on_shelf(saga_forms.new_saga_form())
        if answered and isinstance(end, Picked):
            self.saga_ids = storage.list_sagas()
            self.open_saga(end.value)

    def start_tutorial(self) -> None:
        """Start a Tutorial: a fresh copy of a walkthrough guide's saga,
        opened once it is made."""
        answered, end = self._run_on_shelf(saga_forms.tutorial_form())
        if answered and isinstance(end, Picked):
            self.saga_ids = storage.list_sagas()
            self.open_saga(end.value)

    def delete_saga(self, saga_id: str) -> None:
        """Delete a saga, after asking."""
        try:
            name = storage.load_saga(saga_id).name
        except OSError, ValueError:
            name = saga_id
        answered, _end = self._run_on_shelf(saga_forms.delete_saga(saga_id, name))
        if answered:
            self._shelf_again()

    def change_save_folder(self) -> None:
        """Choose another folder to keep the saves in (moving them there
        if asked), and read the sagas from it from now on."""
        refused = saga_forms.save_folder_refused()
        if refused:
            self.tell("Change Save Folder", refused)
            return
        current = paths.data_dir()
        chosen = self.choose_folder(current)
        if not chosen:
            return
        answered, end = self._run_on_shelf(
            saga_forms.save_folder_form(current, Path(chosen))
        )
        if answered and isinstance(end, list):
            self._shelf_again()
            self.tell("Change Save Folder", "\n".join(end))

    def choose_folder(self, start: Path) -> str:
        """The folder chosen in the system's folder dialog ("" for none).
        Tests replace it."""
        return QFileDialog.getExistingDirectory(
            self, "Choose the save folder", str(start)
        )

    def open_saga(self, saga_id: str) -> None:
        try:
            saga = storage.load_saga(saga_id)
        except (OSError, ValueError) as problem:
            self.tell("Can't Open the Saga", storage.unreadable_note(saga_id, problem))
            return
        self.end_joined()
        self.load(saga)
        note = storage.newer_save_note(saga)
        if note is not None:
            # Once the saga is on show (open_saga runs before the window does
            # when only one saga is on the shelf).
            QTimer.singleShot(0, lambda: self.tell("Saved by a newer Armarius", note))

    def load(self, saga: Saga, player: Player | None = None) -> None:
        """Open `saga` at its page of covenants, in Player view if it was
        left in it on this computer; read as `player` (a Joined game's
        Player), or as its storyguide."""
        self.saga = saga
        self.player = player
        if viewing.troupe_style(saga) and seat.runs_the_saga(player):
            # With a second storyguide every storyguide's window opens
            # Playing (ADR 0015).
            viewing.set_player_view(saga.id, True)
        self._use_viewer()
        # Its user-made entries join the shared catalogs, as in the terminal.
        catalog.use_saga(saga)
        title_page.remember_saga(saga.id)
        self.go([Place(SHELF), Place(SAGA)])
        self.shared_timer.setInterval(
            REMOTE_TICK_MS if self.store.remote else SHARED_TICK_MS
        )
        if saga.players or self.store.remote:
            self.shared_timer.start()
        else:
            self.shared_timer.stop()

    # -- Joined games (gui/joined.py) --

    def join_game(self) -> None:
        joined.join_game(self)

    def rejoin(self, game: JoinedGame) -> None:
        joined.rejoin(self, game)

    def leave_game(self, game: JoinedGame) -> None:
        joined.leave_game(self, game)

    def change_passcode(self, game: JoinedGame) -> None:
        joined.change_passcode(self, game)

    def end_joined(self) -> None:
        joined.end_joined(self)

    def reconnect(self) -> None:
        joined.reconnect(self)

    def shelf_again(self) -> None:
        self._shelf_again()

    def save_saga(self) -> None:
        """Save the saga where it came from (self.store). A Joined game's
        changes go to the host one record at a time; what the host refused
        is said, and the page shows the host's saga again."""
        saga = self.saga
        if saga is None:
            return
        self.edits += 1
        if self.store.remote:
            # Sent by the next tick, in the background: the window never
            # waits on the network.
            self.unsent = True
            if self.connection_lost:
                self.note.say(
                    "Not sent yet: the host can't be reached. It goes when the "
                    "connection is back.",
                    self.palette_,
                )
            return
        self.store.save(saga)

    def refused(self, refused: list[str]) -> None:
        """The host didn't take some of a Joined game's changes."""
        self.tell(
            "Not Saved",
            "The host didn't take your change to "
            + escape(", ".join(refused))
            + ": it isn't yours to change. The page shows the host's saga again.",
        )

    def unreadable(self, problem: Exception) -> None:
        """What another copy saved (or the host sent) can't be read: said
        once, the saga in hand kept."""
        if not self._unreadable:
            said = (
                f"{problem} Yours is kept."
                if self.store.remote
                else f"Another copy's save couldn't be read ({problem}); yours is kept."
            )
            self.note.say(said, self.palette_)
        self._unreadable = True

    def shared_tick(self) -> None:
        """Pick up another copy's save, as the terminal does: the page
        drawn again with a note saying who changed what. Waits while a
        form or question is open, so nothing being typed is touched. A
        Joined game's talk with its host runs in the background
        (joined.tick)."""
        if self.saga is None or self._step_open():
            return
        if self.store.remote:
            joined.tick(self)
            return
        self.pick_up()
        self._local_presence()

    def pick_up(self) -> None:
        """Bring in what another copy (or the host) saved, and say so."""
        saga = self.saga
        if saga is None:
            return
        # Read before the refresh, which may change this saga in place.
        season_was = (saga.current_year, saga.current_season)
        try:
            found = self.store.refresh(saga)
        except ValueError as problem:
            self.unreadable(problem)
            return
        except ConnectionError, TimeoutError:
            self.reconnect()
            return
        if found is not None:
            self.picked_up(found, season_was)

    def _find_button(self) -> QPushButton:
        """Find, while a saga is open: drops the finder (finder.py)."""
        self.find_button = QPushButton("  Find")
        self.find_button.setFlat(True)
        self.find_button.setToolTip("Find a record in the saga by name (Ctrl+F)")
        self.find_button.clicked.connect(self.open_finder)
        return self.find_button

    def _here_label(self) -> QLabel:
        """Who else has the record on show open, in a hosted saga
        (presence.py): beside the trail, a mark and their names."""
        self.here_label = _hidden_label("Also here")
        return self.here_label

    def open_record_key(self) -> str | None:
        """The record on show, as "characters:mag1" (presence.py), or None
        for a page that isn't one record's."""
        place = self.trail[-1] if self.trail else None
        if place is None or not place.id:
            return None
        kind = next((k for k, v in _REF_PLACES.items() if v == place.kind), None)
        return f"{kind}:{place.id}" if kind else None

    def also_here(self, record: str | None, others: Sequence[str]) -> None:
        """Show who else has `record` open, if it is still the one on show:
        a mark and the names beside the trail, never colour alone."""
        if record is None or record != self.open_record_key() or not others:
            self.here_label.hide()
            return
        names = ", ".join(others)
        verb = "is" if len(others) == 1 else "are"
        self.here_label.setText(f"  ◉ {escape(names)} {verb} also viewing")
        self.here_label.setStyleSheet(
            f"color:{self.palette_['heading']}; background:transparent;"
            "font-style:italic;"
        )
        self.here_label.show()

    def _local_presence(self) -> None:
        """While the saga has players, say which record this window has
        open, and show who else has it open, as the terminal does."""
        saga = self.saga
        if saga is None or not saga.players:
            return
        if self._presence_id is None:
            self._presence_id = f"desktop-{uuid.uuid4().hex}"
        record = self.open_record_key()
        presence.note(self._presence_id, saga.id, presence.label(self.player), record)
        self.also_here(record, presence.others_on(self._presence_id, saga.id, record))

    def picked_up(
        self, found: Refreshed, season_was: tuple[int, str] | None = None
    ) -> None:
        """Show what another copy (or the host) saved, and say so; the
        season's dial turns if it moved (`season_was`: the season before,
        for a saga the refresh changed in place)."""
        self._unreadable = False
        saga = self.saga
        if saga is None:
            return
        if season_was is None:
            season_was = (saga.current_year, saga.current_season)
        role_changed = False
        if found.saga is not saga:
            saga = self.saga = found.saga
            catalog.use_saga(saga)
            # A Joined game's reader as the host has them now: the host may
            # have made them a storyguide, or a player again.
            role_changed = joined.role_changed(self, saga)
            self._use_viewer()
        changed = found.changed
        who = saga.saved_by or "The storyguide"
        place = self.trail[-1] if self.trail else None
        open_record = self._shown_record(place)
        if place is not None and place.id and open_record is None:
            self.go(self._up_to(SAGA))
            self.note.say(f"{who} deleted what you had open.", self.palette_)
        else:
            self.redraw()
            names = {record_id for _kind, record_id in changed}
            if open_record is not None and open_record.id in names:
                self.note.say(
                    f"{who} changed {open_record.name}; reloaded.", self.palette_
                )
            else:
                self.note.say(f"Updated by {who}.", self.palette_)
        if (saga.current_year, saga.current_season) != season_was:
            # Another copy advanced (or undid) the season: the dial turns
            # here too.
            back = season_order(
                season=saga.current_season, year=saga.current_year
            ) < season_order(season=season_was[1], year=season_was[0])
            self.note.say(
                f"{who} undid {season_was[1]} {season_was[0]}: the saga is back "
                f"to {saga.current_season} {saga.current_year}."
                if back
                else f"{who} advanced the season to {saga.current_season} "
                f"{saga.current_year}.",
                self.palette_,
            )
            self._turn_the_dial(lambda: None)
        if role_changed:
            self.note.say(
                "The host made you a storyguide: you see the whole saga now."
                if joined.is_storyguide(self.player)
                else "The host made you a player again.",
                self.palette_,
            )

    def _shown_record(self, place: Place | None) -> Any:
        """The record a place shows, if it shows one and it is still there."""
        saga = self.saga
        if saga is None or place is None or not place.id:
            return None
        for records in (
            saga.characters,
            saga.covenants,
            saga.laboratories,
            saga.familiars,
            saga.tribunals,
            saga.neighbours,
            saga.creatures,
        ):
            found = next((r for r in records if r.id == place.id), None)
            if found is not None:
                return found
        return None

    def _use_viewer(self) -> None:
        """Seat whoever reads the saga open (seat.py): the storyguide, the
        table while Player view is on, or the player seated by Play as."""
        saga = self.saga
        if saga is None:
            seat.sign_out()
            return
        seat.sign_in(
            saga,
            self.player,
            player_view=viewing.player_view_on(saga.id),
            hosts=not self.store.remote,
            on_refused=lambda refused: self.tell(
                "Not saved",
                "Only the storyguide can change " + escape(", ".join(refused)) + ".",
            ),
        )

    def sit_as(self, player: Player | None) -> None:
        """Seat `player` at the open saga, or the storyguide again (None):
        the page on show is drawn again for its reader. A stand-in for
        signing in, which the storyguide uses to see a player's desktop."""
        if self.saga is None:
            return
        self.player = player
        self._use_viewer()
        if self.finder is not None and shiboken6.isValid(self.finder):
            self.finder.close()
        self.redraw()

    def choose_seat(self) -> None:
        """The title bar's Play as: a menu of the storyguide and each
        player."""
        saga = self.saga
        if saga is None:
            return
        menu = QMenu(self.seat_button)
        menu.addAction("Storyguide").triggered.connect(lambda: self.sit_as(None))
        for player in saga.players:
            if seat.runs_the_saga(player):
                continue
            menu.addAction(player.name).triggered.connect(
                lambda _checked=False, who=player: self.sit_as(who)
            )
        if self.player is not None:
            # Playing as a player, the host keeps hosting: Host for Players
            # stays one click away, and hosting goes on whoever sits here.
            menu.addSeparator()
            menu.addAction("Host for Players…").triggered.connect(self.open_hosting)
        menu.exec(self.seat_button.mapToGlobal(self.seat_button.rect().bottomLeft()))

    def _draw_seat_button(self) -> None:
        saga = self.saga
        has_players = saga is not None and any(
            not seat.runs_the_saga(p) for p in saga.players
        )
        # A Joined game's reader is the Player: no one else's seat to take.
        self.seat_button.setVisible(has_players and not self.store.remote)
        self.seat_button.setText(
            f"  Playing as {self.player.name}" if self.player is not None else ""
        )
        self.seat_button.setToolTip(
            "See the saga as this player does. Click to choose another seat."
            if self.player is not None
            else "Play as: see the saga from a player's seat"
        )

    def _draw_view_button(self) -> None:
        saga = self.saga
        if viewing.troupe_style(saga):
            # Among several storyguides the eye is the switch between
            # Playing and the storyguide's role (ADR 0015).
            playing = not viewing.current().is_storyguide
            self.view_button.setChecked(playing)
            self.view_button.setText("  Playing" if playing else "  Storyguide")
            self.view_button.setToolTip(
                "Playing: your characters as a player sees them. Click to "
                "switch to your storyguide role."
                if playing
                else "Your storyguide role: your stories and those with no "
                "storyguide, Secrets and all. Click to switch to Playing."
            )
            return
        on = viewing.current().kind == viewing.TABLE
        self.view_button.setChecked(on)
        self.view_button.setText("  Player view" if on else "")
        self.view_button.setToolTip(
            "Player view is on: the saga as the players see it. Click to see "
            "everything again."
            if on
            else "Player view: see the saga as the players do, for a screen they watch"
        )

    def toggle_player_view(self) -> None:
        """The eye in the title bar: Player view on or off, remembered for
        the saga, and the page on show drawn again for its reader."""
        saga = self.saga
        if saga is None:
            return
        playing = not viewing.player_view_on(saga.id)
        viewing.set_player_view(saga.id, playing)
        if self.store.remote:
            # Logged on the host with the next talk to it (gui/joined.py).
            self.switched = playing
        else:
            storyguides.log_switch(saga, self.player, playing=playing)
        self._use_viewer()
        if self.finder is not None and shiboken6.isValid(self.finder):
            self.finder.close()
        self.redraw()

    def open_covenant(self, covenant_id: str | None) -> None:
        self.go([*self._up_to(SAGA), Place(COVENANT, covenant_id)])

    def open_tribunal(self, tribunal_id: str) -> None:
        self.go([*self._up_to(SAGA), Place(TRIBUNAL, tribunal_id)])

    def open_neighbour(self, neighbour_id: str) -> None:
        self.go([*self._up_to(SAGA), Place(NEIGHBOUR, neighbour_id)])

    def open_creature(self, creature_id: str) -> None:
        self.go([*self._up_to(SAGA), Place(CREATURE, creature_id)])

    def open_fight(self, fight_id: str) -> None:
        self.go([*self._up_to(SAGA), Place(FIGHT, fight_id)])

    def open_siege(self, siege_id: str) -> None:
        self.go([*self._up_to(SAGA), Place(SIEGE, siege_id)])

    def show_character(self, character_id: str) -> None:
        """Open a character's sheet, below their covenant."""
        character = self.saga.character(character_id) if self.saga else None
        if character is None:
            return
        self.go(
            [
                Place(SHELF),
                Place(SAGA),
                Place(COVENANT, character.covenant_id),
                Place(CHARACTER, character_id),
            ]
        )

    def open_laboratory(self, lab_id: str) -> None:
        """Open a laboratory's page, below its covenant."""
        lab = self.saga.laboratory(lab_id) if self.saga else None
        if lab is None:
            return
        self.go(
            [
                Place(SHELF),
                Place(SAGA),
                Place(COVENANT, lab.covenant_id),
                Place(LABORATORY, lab_id),
            ]
        )

    def open_sanctum(self, character_id: str) -> None:
        """Open the magus's laboratory below their sheet, so Back returns
        to them; while they have none, create one first (it opens on its
        Creation Worksheet)."""
        saga = self.saga
        magus = saga.character(character_id) if saga else None
        if saga is None or magus is None:
            return
        lab = ls.sanctum(saga, magus)
        if lab is not None:
            self._visit(Place(LABORATORY, lab.id))
            return
        before = {lab.id for lab in saga.laboratories}

        def made() -> None:
            fresh = [lab.id for lab in saga.laboratories if lab.id not in before]
            if fresh:
                self._visit(Place(LABORATORY, fresh[-1]))
                self.go([*self.trail, Place(WORKSHEET, fresh[-1])])

        self.run(
            creation_forms.new_laboratory_form(saga, magus.covenant_id, magus.id),
            made,
        )

    def open_owner(self, lab_id: str) -> None:
        """Open the laboratory's owner below it, so Back returns to it."""
        saga = self.saga
        lab = saga.laboratory(lab_id) if saga else None
        magus = ls.owner(saga, lab) if saga and lab else None
        if magus is not None:
            self._visit(Place(CHARACTER, magus.id))

    def open_ref(self, found: references.Ref) -> None:
        """Open the record a link on a page names, below the page on show,
        so Back returns to it."""
        if found.kind in stores.STORES:
            # Find's book or device: the store, at its row.
            self.open_store(found.kind)
            return
        kind = _REF_PLACES.get(found.kind)
        if self.saga is None or kind is None:
            return
        if references.target(self.saga, found) is None:
            self.tell("Open", f"{escape(found.name)} is no longer in the saga.")
            return
        self._visit(Place(kind, found.id))

    def open_entry(self, entry: saga_index.Entry) -> None:
        """Open what Find chose: a book, device or spell on its holder's
        page, at its chapter with its row chosen."""
        spot = entry.spot
        chapter = SPOT_CHAPTERS.get((entry.ref.kind, spot.list)) if spot else None
        self._spot = (chapter, spot) if chapter is not None and spot else None
        self.open_ref(entry.ref)
        self._spot = None

    def open_finder(self) -> None:
        """Find (Ctrl+F, or the top bar's Find): drop the finder under the
        Find button, to open a record of the saga by name."""
        if self.saga is None or not self.find_button.isVisible() or self._step_open():
            return
        if self.finder is not None and shiboken6.isValid(self.finder):
            self.finder.close()
        self.finder = FinderPanel(self.saga, self.palette_, self.open_entry, self)
        self.finder.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.finder.drop_under(self.find_button)

    def _visit(self, place: Place) -> None:
        """Go to `place` below the page on show, or back to it if the
        trail already passes through it (from a sanctum to its magus and
        back again)."""
        if place in self.trail:
            self.go(self.trail[: self.trail.index(place) + 1])
        else:
            self.go([*self.trail, place])

    def open_content(self) -> None:
        """Open the saga's Saga Content, below the saga."""
        self.go([Place(SHELF), Place(SAGA), Place(CONTENT)])

    def open_store(self, key: str) -> None:
        """Open the Armarium or the Custodia Mirabilium (`key`, a
        stores.STORES key), below the saga."""
        self.go([Place(SHELF), Place(SAGA), Place(key)])

    def open_familiar(self, familiar_id: str) -> None:
        """Open a familiar's page, below its magus."""
        saga = self.saga
        familiar = self._familiar(familiar_id)
        if saga is None or familiar is None:
            return
        magus = fam.magus_of(saga, familiar)
        self.go(
            [
                Place(SHELF),
                Place(SAGA),
                Place(COVENANT, magus.covenant_id if magus else None),
                *([Place(CHARACTER, magus.id)] if magus else []),
                Place(FAMILIAR, familiar_id),
            ]
        )

    def open_help(self) -> None:
        """Open Help on the page on show, below it (the trail leads back
        to it)."""
        if self.trail and self.trail[-1].kind == HELP:
            return
        self.go([*self.trail, Place(HELP)])

    def _help_ids(self, place: Place, page: QWidget | None) -> list[str]:
        """The help topics for `place`: the tab for the chapter on show
        (_CHAPTER_TABS, else the one whose title starts with its name),
        then the page's."""
        ids = list(_HELP_IDS.get(place.kind, []))
        codex = getattr(page, "codex", None)
        item = codex.rail.currentItem() if codex is not None else None
        tab = _chapter_topic(place.kind, item.text()) if item is not None else None
        if tab is not None:
            ids.insert(0, tab)
        return ids

    def _help_places(self, place: Place, page: QWidget | None) -> dict[str, str]:
        """The chapters of `page` Help's Go there can open, by the help
        topic of each: its tab and the sections the help puts on it."""
        codex = getattr(page, "codex", None)
        if codex is None:
            return {}
        book = help_text.book(help_text.GUI)
        places: dict[str, str] = {}
        for name in codex.chapters():
            tab = _chapter_topic(place.kind, name)
            if tab is None or tab in places:
                continue
            for topic in book.topics.values():
                if topic.id == tab or topic.page == tab:
                    places[topic.id] = name
        return places

    def _go_there(self, chapter: str) -> None:
        """Help's Go there: back to the page below Help, at `chapter`."""
        below = self.trail[:-1]
        self._chapters[below[-1]] = chapter
        self.go(below)

    def open_seasons(self) -> None:
        """Open the saga's Seasons, below the saga."""
        self.go([Place(SHELF), Place(SAGA), Place(SEASONS)])

    def open_hosting(self) -> None:
        """Open the Host for Players window beside the page (or bring it
        forward): it stays open while the game goes on."""
        # start-up: Remote seats bring the network and keychain libraries,
        # about a third of the window's import time, loaded when first used.
        from ..forms.remote_seats import SeatsDesk
        from .hosting import HostingWindow  # start-up: as above

        saga = self.saga
        if saga is None:
            return
        old = self._hosting
        if old is not None and shiboken6.isValid(old):
            if old.desk.saga is saga and old.p == self.palette_:
                old.show()
                old.raise_()
                old.activateWindow()
                return
            # Drawn afresh in the theme on show now (the light or dark one).
            old.close()
        shown = self._hosting = HostingWindow(
            SeatsDesk(saga),
            self.palette_,
            self,
            ask=lambda dialog: self.ask(dialog),
            changed=self.redraw,
        )
        shown.show()
        shown.raise_()
        shown.activateWindow()

    def issue_invite(self, player_id: str) -> None:
        """Issue Invite for the player chosen on Saga Management's Players:
        Host for Players opens and shows the Invite (or why there can't be
        one)."""
        self.open_hosting()
        shown = self._hosting
        if shown is not None:
            shown.run(shown.desk.issue_invite(player_id))

    def closeEvent(self, event: QCloseEvent) -> None:
        """Closing while the saga is hosted asks first: it ends every
        player's connection. So does closing a Joined game with changes the
        host hasn't had yet."""
        if hosting.HOST.running and not confirm_close_while_hosting(
            self.palette_, self, self.ask
        ):
            event.ignore()
            return
        if self.unsent and not self._lose_unsent():
            event.ignore()
            return
        self.end_joined()
        self.shared_timer.stop()
        if self._presence_id is not None:
            presence.leave(self._presence_id)  # no longer "here" for others
        super().closeEvent(event)

    def _lose_unsent(self) -> bool:
        question = ConfirmDialog(
            "Some of your changes haven't reached the host yet: the connection "
            "is down. Close anyway and lose them?",
            self.palette_,
            self,
            yes_label="Close and Lose Them",
            title="Changes Not Sent",
        )
        return self.ask(question) == QDialog.DialogCode.Accepted

    def advance_season(self) -> None:
        """Advance the saga by one season (advance_forms), then show the
        season's results on the Seasons page when it did anything."""
        saga = self.saga
        if saga is None:
            return
        # A Joined game's host backs its own saga up when the advance
        # reaches it (saga_delta.py): nothing is written here.
        backup = None if self.store.remote else storage.backup_saga
        self.run(
            advance_forms.advance_season(saga, backup),
            ended=self._season_played,
        )

    def _season_played(self, end: object) -> None:
        if not isinstance(end, advance_forms.Played):
            self.redraw()
            return
        if end.results:
            self._played = end
            self.open_seasons()
            self._turn_the_dial(lambda: None)
            return
        self.redraw()
        self._turn_the_dial(lambda: self.tell("Advance Season", end.message))

    def _turn_the_dial(self, then: Callable[[], None]) -> None:
        """The season's dial in the middle of the window, turning to the
        new season (season_panel.py), then `then`; with no motion, only
        the seal's sound, then `then`."""
        saga = self.saga
        if saga is None:
            then()
            return
        if not motion.moving():
            sounds.play("seal")
            then()
            return
        season_panel.turn_the_dial(self.stack, saga, self.palette_, then)

    def _finished(self, record_id: str) -> None:
        """A record moved to In Play: leave its worksheet, and press a seal
        with its initial on its page."""
        record = self._creation_record(record_id)
        self._go_up()
        initial = (record.name.strip()[:1] if record is not None else "") or "A"
        motion.press_seal(
            self.stack,
            lambda g, c, r: medallions.member_seal(g, c, r, None, initial.upper()),
        )

    def open_worksheet(self, record_id: str) -> None:
        """Open the Creation Worksheet of a character, covenant or
        laboratory, below its page."""
        record = self._creation_record(record_id)
        if record is None:
            return
        if isinstance(record, Character):
            self.show_character(record_id)
        elif isinstance(record, Covenant):
            self.open_covenant(record_id)
        else:
            self.open_laboratory(record_id)
        self.go([*self.trail, Place(WORKSHEET, record_id)])

    def _creation_record(
        self, record_id: str | None
    ) -> Character | Covenant | Laboratory | None:
        saga = self.saga
        if saga is None:
            return None
        return (
            saga.character(record_id)
            or saga.covenant(record_id)
            or saga.laboratory(record_id)
        )

    def _up_to(self, kind: str) -> list[Place]:
        kinds = [place.kind for place in self.trail]
        return self.trail[: kinds.index(kind) + 1] if kind in kinds else [Place(kind)]

    def run(
        self,
        command: Command,
        then: Callable[[], None] | None = None,
        *,
        ended: Callable[[object], None] | None = None,
    ) -> None:
        """Run a button's steps (commands.py), each in its dialog; once
        the last is answered, save the saga and show the page again at the
        same chapter and place (or, given `then`, call it instead: a
        menu's New shows the new record; given `ended`, call it with what
        the steps ended with). Cancelling any step changes nothing. While
        a step is open, other steps wait: the open one is shown instead."""
        if self.saga is None:
            return
        if self._step_open():
            self._bring_forward()
            return
        title = _title(command)
        page = self.page()
        outcome = drive(command, self._answer)
        if isinstance(outcome, Cancelled):
            return
        if isinstance(outcome, Empty):
            self.tell(outcome.title, outcome.why)
            return
        if isinstance(outcome, Go):
            self.open_ref(outcome.ref)
            return
        if isinstance(outcome, Refuse):
            sounds.play("tock")
            self.tell(outcome.title, outcome.why)
            return
        self.save_saga()
        if isinstance(outcome, Then):
            # Kept and saved; the page is drawn again before the next step.
            self.redraw()
            self.run(outcome.step, then, ended=ended)
            return
        step = outcome.end
        if ended is not None:
            ended(step)
            return
        if isinstance(step, undo_season.Undone) and step.remote:
            # Done on the host: the next read brings the saga back, and the
            # dial turns then.
            self.last_asked = 0.0
            self.tell(undo_season.TITLE, step.message)
            return
        if isinstance(step, undo_season.Undone):
            # The season's dial turns back to the season the saga is in now.
            said = step.message
            self.redraw()
            self._turn_the_dial(lambda: self.tell(undo_season.TITLE, said))
            return
        sounds.play(self._saved_cue(page))
        if then is not None:
            then()
        else:
            self.redraw()
        if isinstance(step, list) and step:
            self.tell(title, "\n".join(step))

    def _saved_cue(self, page: QWidget | None) -> str:
        """The sound of a saved step: coins in a Treasury, else a quill."""
        codex = getattr(page, "codex", None)
        chapter = codex.rail.currentItem() if codex is not None else None
        return (
            "coins" if chapter is not None and chapter.text() == "Treasury" else "quill"
        )

    def _answer(self, question: Question) -> object:
        """Show one step as a window: its answer, or CANCELLED."""
        return ask_question(
            question, self.palette_, self, lambda shown: self.ask(shown)
        )

    def tell(self, title: str, words: str) -> None:
        """Show a message (markup): what a step refused, or the notes
        after it. Tests replace it to read the message instead."""
        NoticeDialog(title, words, self.palette_, self).exec()

    def _bring_forward(self) -> None:
        """Raise the step open again, its first field focused."""
        dialog = self._open
        assert dialog is not None
        dialog.raise_()
        dialog.activateWindow()
        first = _first_input(dialog)
        if first is not None:
            first.setFocus()

    def _present(self, dialog: QDialog) -> int:
        """Show a step as a window over the page and wait for it. While it
        is open, another button brings it forward (run)."""
        # A form's own picker opens over it: the form is open again after.
        under, self._open = self._open, dialog
        try:
            return dialog.exec()
        finally:
            self._open = under

    def redraw(self) -> None:
        """Build the page on show again, at the chapter and scroll place it
        was at."""
        codex = getattr(self.page(), "codex", None)
        chapter, scrolled = 0, 0
        if codex is not None:
            chapter = codex.rail.currentRow()
            area = codex.pages.currentWidget()
            if isinstance(area, QScrollArea):
                scrolled = area.verticalScrollBar().value()
        self.go(self.trail)
        codex = getattr(self.page(), "codex", None)
        if codex is not None:
            codex.rail.setCurrentRow(chapter)
            area = codex.pages.currentWidget()
            if isinstance(area, QScrollArea):
                body = area.widget()
                if body is not None:
                    body.adjustSize()
                area.verticalScrollBar().setValue(scrolled)

    def page(self) -> QWidget | None:
        """The page on show."""
        item = self.sheet_layout.itemAt(0)
        return item.widget() if item is not None else None

    def go(self, trail: list[Place]) -> None:
        """Show the last page of `trail`, with the trail above it. Leaving
        a page cancels a step open on it."""
        if self._open is not None and shiboken6.isValid(self._open):
            self._open.reject()
        #: The page Help is opened from, to find the chapter on show.
        self._help_from = self.page()
        if self.isVisible() and (not self.trail or self.trail[-1] != trail[-1]):
            # A longer page turned for another record or page.
            sounds.play("page-long")
        self._leave_chapter()
        self.trail = trail
        before = None
        if self.palette_ is not self._applied:
            # Into or out of a record In Creation: the colours change.
            if self.isVisible() and self.title is None:
                before = self.stack.grab()
            self._apply_theme()
        page = self._build(trail[-1])
        self._reopen_chapter(trail[-1], page)
        self._open_spot(page)
        self._show(page)
        self._draw_trail()
        self._draw_advance()
        if before is not None:
            motion.fade_from(self.stack, before, motion.MODE_FADE)

    # Drawing

    def _help_page(self) -> HelpPage:
        """Help on the page below it in the trail."""
        below = self.trail[-2] if len(self.trail) > 1 else Place(SHELF)
        return HelpPage(
            self.palette_,
            self._help_ids(below, self._help_from),
            self._name(below),
            self._help_places(below, self._help_from),
            self._go_there,
        )

    def _build(self, place: Place) -> QWidget:
        """The page of `place`, unless it shows a record whoever is looking
        may not read (viewing.py: Player view)."""
        record = self._place_record(place)
        if record is not None and not viewing.reads(record):
            return QLabel("The players don't know of this yet (Player view).")
        if self.saga is not None:
            # The page, and the chapters built as they are turned to, draw
            # no Add, Edit or Delete for a record the seat may not change.
            seat.show(self.saga, record)
        return self._build_page(place)

    def _shelf_page(self, p: Palette) -> QWidget:
        """The saga shelf: every saga that opens, and a word on those that
        don't."""
        sagas, unreadable = [], []
        for saga_id in self.saga_ids:
            try:
                sagas.append(storage.load_saga(saga_id))
            except (OSError, ValueError) as problem:
                unreadable.append(storage.unreadable_note(saga_id, problem))
        if unreadable:
            # Said once the shelf is on show; the rest are listed.
            said = "\n\n".join(unreadable)
            QTimer.singleShot(0, lambda: self.tell("A Saga Can't Be Opened", said))
        return SagaShelf(
            sagas,
            p,
            self.open_saga,
            self.new_saga,
            self.delete_saga,
            self.change_save_folder,
            str(paths.data_dir()),
            start_tutorial=self.start_tutorial,
            joined=JoinedShelf(
                joined_games.listed(),
                self.join_game,
                self.rejoin,
                self.leave_game,
                self.change_passcode,
            ),
        )

    def _build_page(self, place: Place) -> QWidget:
        p, saga = self.palette_, self.saga
        if place.kind == HELP:
            return self._help_page()
        if place.kind == SHELF or saga is None:
            return self._shelf_page(p)
        if place.kind == SAGA:
            return self._saga_page(saga, p)
        if place.kind == FIGHT:
            fight = next((f for f in saga.fights if f.id == place.id), None)
            if fight is None:
                return QLabel("No fight chosen.")
            return FightPage(saga, fight, p, self.run)
        if place.kind == SIEGE:
            siege = next((s for s in saga.sieges if s.id == place.id), None)
            if siege is None:
                return QLabel("No siege chosen.")
            return SiegePage(saga, siege, p, self.run)
        if place.kind == CONTENT:
            return SagaContentPage(saga, p, self.run)
        if place.kind in stores.STORES:
            return StorePage(saga, stores.STORES[place.kind], p, self.run)
        if place.kind == TRIBUNAL:
            tribunal = saga.tribunal(place.id)
            if tribunal is None:
                return QLabel("No Tribunal chosen.")
            return TribunalPage(saga, tribunal, p, self.run, self._controls())
        if place.kind == NEIGHBOUR:
            neighbour = saga.neighbour(place.id)
            if neighbour is None:
                return QLabel("No neighbour chosen.")
            return NeighbourPage(saga, neighbour, p, self.run, self._controls())
        if place.kind == CREATURE:
            creature = saga.creature(place.id)
            if creature is None:
                return QLabel("No creature chosen.")
            return CreaturePage(saga, creature, p, self.run, self._controls())
        if place.kind == SEASONS:
            played, self._played = self._played, None
            return SeasonsPage(saga, p, played, self.run)
        if place.kind == COVENANT:
            return CovenantPage(
                saga,
                place.id,
                p,
                self.show_character,
                self.open_laboratory,
                self.open_familiar,
                self.run,
                self._controls(),
                self._placer(),
            )
        if place.kind == LABORATORY:
            lab = saga.laboratory(place.id)
            if lab is None:
                return QLabel("No laboratory chosen.")
            return LaboratoryPage(
                saga,
                lab,
                p,
                self.run,
                self._controls(),
                self._placer(),
                open_owner=lambda: self.open_owner(lab.id),
            )
        if place.kind == FAMILIAR:
            familiar = self._familiar(place.id)
            if familiar is None:
                return QLabel("No familiar chosen.")
            return FamiliarPage(saga, familiar, p, self.run, self._controls())
        if place.kind == WORKSHEET:
            record = self._creation_record(place.id)
            if record is None:
                return QLabel("No record chosen.")
            return WorksheetPage(
                saga,
                record,
                p,
                self.run,
                played=lambda command: self.run(
                    command, lambda: self._finished(record.id)
                ),
            )
        character = saga.character(place.id)
        if character is None:
            return QLabel("No character chosen.")
        return CharacterSheet(
            saga,
            character,
            p,
            self.open_familiar,
            self.run,
            self._controls(),
            self._placer(),
            open_sanctum=lambda: self.open_sanctum(character.id),
        )

    def _place_record(self, place: Place) -> object | None:
        """The record a page of `place` shows, for those Reveal applies to."""
        saga = self.saga
        if saga is None or place.id is None:
            return None
        if place.kind == NEIGHBOUR:
            return saga.neighbour(place.id)
        if place.kind == CREATURE:
            return saga.creature(place.id)
        if place.kind == COVENANT:
            return saga.covenant(place.id)
        if place.kind == CHARACTER:
            return saga.character(place.id)
        if place.kind == WORKSHEET:
            # The worksheet changes its record: whoever may change that
            # record (a player their own character) gets its buttons.
            return self._creation_record(place.id)
        return None

    def _controls(self) -> RecordControls | None:
        """What the record's page needs to manage the record (manage.py):
        none for a page with no record to manage."""
        page = self.menu_page()
        if page is None or page.record_to_delete() is None:
            return None
        return RecordControls(
            page,
            self.run,
            self._go_up,
            self.toggle_mode,
            self.open_worksheet,
            self.print_pdf,
            self.show_on_map,
        )

    def show_on_map(self, kind: str, record_id: str) -> None:
        """Open the saga page's Atlas on the record's pin."""
        atlas_page.show_on_map(kind, record_id)
        self._chapters[Place(SAGA)] = "The Atlas"
        self.go([Place(SHELF), Place(SAGA)])

    def print_pdf(self) -> None:
        """Print the record on show to a PDF: its options first (the
        paper, and for a character's sheet the spells and background), then
        where to save it."""
        page = self.menu_page()
        record = page.record_to_delete() if page is not None else None
        if record is None:
            return
        name = record.name or "Untitled"
        folder = storage.exports_dir()
        folder.mkdir(parents=True, exist_ok=True)

        def where(options: pl.PrintOptions) -> ChooseFile:
            return ChooseFile(
                f"Print {escape(name)} to PDF",
                ".pdf",
                folder / f"{printing.file_stem(name)}.pdf",
                lambda path: self.print_to(path, name, options),
                save=True,
            )

        self.run(
            print_forms.print_form(where, sheet=isinstance(record, Character)), None
        )

    def print_to(
        self, path: Path, title: str, options: pl.PrintOptions = pl.DEFAULT_OPTIONS
    ) -> list[str]:
        """Print the record on show to the PDF at `path`; what it did, to
        tell. A character prints as a sheet laid out for paper
        (print_layout.py); other records print their page, drawn afresh in
        the parchment palette."""
        page = self.menu_page()
        record = page.record_to_delete() if page is not None else None
        if isinstance(record, Character) and self.saga is not None:
            doc = pl.document(self.saga, "character", record, options)
            pages = print_sheet.print_document(doc, path, options)
        else:
            self._printing = printing.PARCHMENT
            try:
                built = self._build(self.trail[-1])
            finally:
                self._printing = None
            pages = printing.print_page(
                built, path, title, printing.PARCHMENT, options.paper
            )
        return [f"{pages} page{'s' if pages != 1 else ''} saved to {path}."]

    def toggle_mode(self, record: Moded) -> None:
        """Move `record` between In Creation and In Play (the core asks
        first): into In Creation opens its Creation Worksheet; back to In
        Play shows its page."""

        def moved() -> None:
            if record.in_creation:
                self.open_worksheet(record.id)
            elif self.trail and self.trail[-1].kind == WORKSHEET:
                self._go_up()
            else:
                self.redraw()

        if self.saga is not None:
            self.run(menu_forms.toggle_mode(self.saga, record), moved)

    def _familiar(self, familiar_id: str | None) -> Familiar | None:
        saga = self.saga
        if saga is None:
            return None
        return next((f for f in saga.familiars if f.id == familiar_id), None)

    def _show(self, page: QWidget) -> None:
        layout = self.sheet_layout
        while layout.count():
            item = layout.takeAt(0)
            old = item.widget() if item is not None else None
            if old is not None:
                old.hide()
                old.deleteLater()
        layout.addWidget(page)

    def _name(self, place: Place) -> str:
        saga = self.saga
        if place.kind == SHELF:
            return "Sagas"
        if saga is None:
            return ""
        if place.kind == SAGA:
            return saga.name
        if place.kind == CONTENT:
            return "Saga Content"
        if place.kind in stores.STORES:
            return stores.STORES[place.kind].title
        if place.kind == SEASONS:
            return "Seasons"
        if place.kind == HELP:
            return "Help"
        if place.kind == COVENANT:
            covenant = saga.covenant(place.id)
            return covenant.name if covenant else "Unassigned"
        if place.kind == LABORATORY:
            lab = saga.laboratory(place.id)
            return lab.name if lab else ""
        if place.kind == FAMILIAR:
            familiar = self._familiar(place.id)
            return (familiar.name or "(unnamed)") if familiar else ""
        if place.kind == WORKSHEET:
            return "Creation Worksheet"
        if place.kind == TRIBUNAL:
            tribunal = saga.tribunal(place.id)
            return tribunal.name if tribunal else ""
        if place.kind == NEIGHBOUR:
            neighbour = saga.neighbour(place.id)
            return neighbour.name if neighbour else ""
        if place.kind == CREATURE:
            creature = saga.creature(place.id)
            return creature.name if creature else ""
        if place.kind == FIGHT:
            fight = next((f for f in saga.fights if f.id == place.id), None)
            return fight.name if fight else ""
        if place.kind == SIEGE:
            siege = next((s for s in saga.sieges if s.id == place.id), None)
            return siege.name if siege else ""
        character = saga.character(place.id)
        return character.name if character else ""

    def _draw_trail(self) -> None:
        while self.crumbs.count():
            item = self.crumbs.takeAt(0)
            old = item.widget() if item is not None else None
            if old is not None:
                old.hide()
                old.deleteLater()
        label = self.palette_["label"]
        for i, place in enumerate(self.trail):
            if i:
                arrow = QLabel("›")
                arrow.setStyleSheet(f"color:{label}; background:transparent")
                self.crumbs.addWidget(arrow)
            crumb = QPushButton(self._name(place))
            crumb.setObjectName("crumb")
            crumb.setFlat(True)
            last = i == len(self.trail) - 1
            crumb.setEnabled(not last)
            crumb.clicked.connect(
                lambda _checked=False, upto=i: self.go(self.trail[: upto + 1])
            )
            self.crumbs.addWidget(crumb)

    def menu_page(self) -> menu_forms.Page | None:
        """The page on show, as the actions it sets out see it."""
        saga = self.saga
        place = self.trail[-1] if self.trail else None
        if (
            saga is None
            or place is None
            or place.kind
            in (
                SHELF,
                WORKSHEET,
                SEASONS,
                HELP,
                FIGHT,
                SIEGE,
                ARMARIUM,
                CUSTODIA,
            )
        ):
            return None
        if place.kind == SAGA:
            return menu_forms.page_for(saga, NodeKind.SAGA)
        if place.kind == CONTENT:
            return menu_forms.page_for(saga, NodeKind.SAGA_CONTENT)
        if place.kind == COVENANT:
            if saga.covenant(place.id) is None:
                # The saga's unassigned characters and laboratories.
                return menu_forms.page_for(saga, NodeKind.CHARACTER_GROUP)
            return menu_forms.page_for(saga, NodeKind.COVENANT, covenant_id=place.id)
        if place.kind == CHARACTER:
            return menu_forms.page_for(saga, NodeKind.CHARACTER, character_id=place.id)
        if place.kind == TRIBUNAL:
            return menu_forms.page_for(saga, NodeKind.TRIBUNAL, tribunal_id=place.id)
        if place.kind == NEIGHBOUR:
            return menu_forms.page_for(saga, NodeKind.NEIGHBOUR, neighbour_id=place.id)
        if place.kind == CREATURE:
            return menu_forms.page_for(saga, NodeKind.CREATURE, creature_id=place.id)
        if place.kind == LABORATORY:
            return menu_forms.page_for(
                saga, NodeKind.LABORATORY, laboratory_id=place.id
            )
        return menu_forms.page_for(saga, NodeKind.FAMILIAR, familiar_id=place.id)

    def _draw_advance(self) -> None:
        """Find while a saga is open, and Advance Season at the foot of
        the chapters of the page on show, but not a Creation Worksheet's:
        a record is finished or left before the season ends."""
        saga = self.saga
        shown = saga is not None and bool(self.trail) and self.trail[-1].kind != SHELF
        self.find_button.setVisible(shown)
        # Player view is a storyguide's own screen: a player has no eye.
        self.view_button.setVisible(shown and seat.runs_the_saga(self.player))
        self._draw_view_button()
        self._draw_seat_button()
        if not shown:
            self.seat_button.setVisible(False)
        # The headpiece carries the present season while a saga's page is on show.
        self.headpiece.saga = saga if shown else None
        self.headpiece.update()
        codex = getattr(self.page(), "codex", None)
        if (
            saga is not None
            and shown
            and isinstance(codex, Codex)
            and self.trail[-1].kind != WORKSHEET
            and viewing.offers("advance_season")
        ):
            self.season_panel = SeasonPanel(saga, self.palette_, self.advance_season)
            codex.set_foot(self.season_panel)
        else:
            self.season_panel = None

    def _leave_chapter(self) -> None:
        """Note the chapter the page on show is at, to open it there again."""
        codex = getattr(self.page(), "codex", None)
        item = codex.rail.currentItem() if codex is not None else None
        if self.trail and item is not None:
            self._chapters[self.trail[-1]] = item.text()

    def _open_spot(self, page: QWidget) -> None:
        """Turn `page` to the chapter of the row Find asked for, and
        choose the row (Codex.choose_row)."""
        codex = getattr(page, "codex", None)
        if self._spot is None or not isinstance(codex, Codex):
            return
        chapter, spot = self._spot
        if chapter in codex.chapters():
            codex.open_chapter(chapter)
            codex.choose_row(spot.list, spot.record_id)

    def _reopen_chapter(self, place: Place, page: QWidget) -> None:
        """Turn `page`, before it is shown, to the chapter it was left at."""
        codex = getattr(page, "codex", None)
        name = self._chapters.get(place)
        if codex is not None and name in codex.chapters():
            codex.open_chapter(name)

    def _saga_page(self, saga: Saga, p: Palette) -> SagaPage:
        """The saga's own page, every card and button wired to the window."""
        return SagaPage(
            saga,
            p,
            self.open_covenant,
            open_content=self.open_content,
            open_store=self.open_store,
            open_seasons=self.open_seasons,
            placer=self._placer(),
            open_character=self.show_character,
            open_laboratory=self.open_laboratory,
            open_tribunal=self.open_tribunal,
            open_neighbour=self.open_neighbour,
            open_creature=self.open_creature,
            open_familiar=self.open_familiar,
            run=self.run,
            run_ended=lambda command, ended: self.run(command, ended=ended),
            open_fight=self.open_fight,
            open_siege=self.open_siege,
            open_hosting=self.open_hosting,
            sessions=lambda inspect: sessions_section(saga, p, self.run, inspect),
            players=lambda inspect: players_section(
                saga, p, self.run, inspect, self.issue_invite
            ),
        )

    def _placer(self) -> Placer:
        """What the page on show sets out itself (menu_forms.PLACES)."""
        return Placer(self.menu_page(), self.palette_, self.run, self._show_made)

    def _show_made(self, action: str, record_id: str) -> None:
        """Open the page of what a New entry made: its Creation Worksheet
        while it is In Creation."""
        record = self._creation_record(record_id)
        if action != "create_familiar" and record is not None and record.in_creation:
            self.open_worksheet(record_id)
        elif action == "create_covenant":
            self.open_covenant(record_id)
        elif action == "create_tribunal":
            self.open_tribunal(record_id)
        elif action == "create_neighbour":
            self.open_neighbour(record_id)
        elif action == "create_creature":
            self.open_creature(record_id)
        elif action == "create_character":
            self.show_character(record_id)
        elif action == "create_laboratory":
            self.open_laboratory(record_id)
        else:
            self.open_familiar(record_id)

    def _go_up(self) -> None:
        """Leave a deleted record's page for the one above it."""
        self.go(self.trail[:-1] or [Place(SHELF)])

    def crumb_names(self) -> list[str]:
        return [self._name(place) for place in self.trail]

    def choose_theme(self, name: str) -> None:
        """Draw the desktop in the theme called `name` and remember it;
        a name no theme has changes nothing."""
        theme = liveries.named(name)
        if theme is None or theme.name != name or theme is self.theme:
            return
        self.theme = theme
        remember_theme(theme)
        self._apply_theme()
        if self.trail:  # the pages' colours are drawn in
            self.go(self.trail)

    def open_settings(self) -> None:
        """Open the Settings window beside the page (or bring it forward):
        it stays open while the app is used."""
        old = self._settings
        if old is not None and shiboken6.isValid(old) and old.isVisible():
            old.raise_()
            old.activateWindow()
            return
        self._show_settings(None)

    def _show_settings(self, where: QWidget | None) -> None:
        """The Settings window, drawn in the theme on show, where `where`
        was (a window it replaces) or beside the page."""
        shown = self._settings = SettingsWindow(
            self.palette_, self.theme, self.choose_theme, self
        )
        if where is not None:
            shown.setGeometry(where.geometry())
        shown.show()
        shown.raise_()
        shown.activateWindow()

    def _apply_theme(self) -> None:
        p = self._applied = self.palette_
        body = self.stack.widget(0)
        if isinstance(body, Paper):
            body.p = p
            body.update()
        self.headpiece.p = p
        self.headpiece.update()
        self.drag.set_palette(p)
        self.bar_rule.set_palette(p)
        self.controls.set_palette(p)
        app = QApplication.instance()
        if isinstance(app, QApplication):
            dress_application(app, p)
        hosting_open = self._hosting
        if (
            hosting_open is not None
            and shiboken6.isValid(hosting_open)
            and hosting_open.isVisible()
            and hosting_open.p != p
        ):
            self.open_hosting()  # drawn again in the new theme
        settings_open = self._settings
        if (
            settings_open is not None
            and shiboken6.isValid(settings_open)
            and settings_open.isVisible()
            and settings_open.p != p
        ):
            # Drawn again in the new theme, where it was.
            settings_open.close()
            self._show_settings(settings_open)
        self.settings.setIcon(pictures.gear_icon(p["label"]))
        self.help.setIcon(pictures.icon("help", p["label"]))
        self.find_button.setIcon(magnifier_icon(p["label"]))
        self.view_button.setIcon(eye_icon(p["label"]))
        self.seat_button.setIcon(pictures.icon("players", p["label"]))
