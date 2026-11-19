"""The Chronicle pane wired to where its entries come from (STORY-2289 with
STORY-2288): the host's pane catching up with what the seat listener writes
(a file watcher, the window's tick as a fallback), a seat's pane fed by its
events connection and rolling through the host, and a failing subscriber
never leaving a roll half-written."""

from __future__ import annotations

import asyncio
import os
import random
import time
from pathlib import Path

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from fake_table import FakeTable
from PySide6.QtWidgets import QApplication
from test_remote_events import PASSCODE, Table

from ars_magica_manager import chronicle, commands, storage, viewing, virtual_tabletop
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.chronicle_pane import ChroniclePane, DiceRow
from ars_magica_manager.gui.themes import SCRIPTORUM
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import Casting, Character, Player, Saga, Session
from ars_magica_manager.remote.host import PATH
from ars_magica_manager.remote.seat_session import SeatSession

HOST = viewing.HOST


class Faces(random.Random):
    def __init__(self, *faces: int) -> None:
        super().__init__()
        self.faces = list(faces)

    def randrange(self, *_args: object, **_kwargs: object) -> int:  # type: ignore[override]
        return self.faces.pop(0)


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert isinstance(application, QApplication)
    assert pictures.register_fonts() == []
    return application


def _saga() -> Saga:
    saga = Saga(id="fengheld", name="Fengheld")
    saga.players = [Player("ana", "Ana")]
    saga.characters = [Character(id="aelfric", name="Aelfric", type="magus")]
    saga.sessions = [
        Session("s1", castings=[Casting(player_id="ana", character_id="aelfric")])
    ]
    return saga


def _until(app: QApplication, done: object, seconds: float = 5.0) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        app.processEvents()
        if callable(done) and done():
            return True
        time.sleep(0.02)
    return False


# -- a subscriber that fails --


def test_a_failing_subscriber_never_leaves_a_blind_roll_half_written() -> None:
    saga = _saga()
    session = saga.sessions[0]
    book = chronicle.begin(saga, session, by=HOST)

    def fails(_entry: chronicle.Entry) -> None:
        raise RuntimeError("a pane gone wrong")

    book.subscribe(fails)
    request = chronicle.RollRequest(character_id="aelfric", visibility=chronicle.BLIND)
    with pytest.raises(RuntimeError):
        chronicle.free_roll(book, saga, session, request, by=HOST, rng=Faces(5))

    on_file = chronicle.Chronicle(book.path, [])
    on_file.refresh()
    assert [e.kind for e in on_file.entries] == ["begin", "roll", "rolled"]


# -- the host's pane and the listener's writes --


@pytest.mark.usefixtures("app")
def test_the_hosts_pane_shows_a_seat_roll_as_the_file_grows(app: QApplication) -> None:
    virtual_tabletop.set_on(True)
    saga = _saga()
    chronicle.begin(saga, saga.sessions[0], by=HOST)
    storage.save_saga(saga)
    chronicle.forget_open()
    window = MainWindow(saga_ids=[saga.id])
    assert window.saga is not None
    session = window.saga.sessions[0]
    listener = chronicle.Chronicle(chronicle.path_of(window.saga, session), [])

    listener.add("note", "ana", chronicle.table(), {})  # the other process

    assert _until(app, lambda: len(window.chronicle_pane.lines()) == 2)
    window.close()


@pytest.mark.usefixtures("app")
def test_the_windows_tick_catches_up_too(app: QApplication) -> None:
    virtual_tabletop.set_on(True)
    saga = _saga()
    chronicle.begin(saga, saga.sessions[0], by=HOST)
    storage.save_saga(saga)
    chronicle.forget_open()
    window = MainWindow(saga_ids=[saga.id])
    assert window.saga is not None
    window.chronicle_watch.removePaths(window.chronicle_watch.files())
    session = window.saga.sessions[0]
    chronicle.Chronicle(chronicle.path_of(window.saga, session), []).add(
        "note", "ana", chronicle.table(), {}
    )

    window.shared_tick()

    assert len(window.chronicle_pane.lines()) == 2
    window.close()


# -- a seat's pane --


@pytest.mark.usefixtures("app")
def test_a_seats_pane_shows_what_its_host_sent_and_rolls_through_it() -> None:
    saga = _saga()
    session = saga.sessions[0]
    held = chronicle.SeatChronicle()
    table = FakeTable(held=held)
    ran: list[commands.Command] = []

    pane = ChroniclePane(SCRIPTORUM, ran.append)
    pane.attach(saga, session, held, "ana", table)
    held.take("s1", chronicle.Entry(1, "", "begin", HOST, chronicle.table()))
    held.take(
        "s1",
        chronicle.Entry(
            2,
            "",
            chronicle.ROLLED,
            HOST,
            chronicle.Audience(chronicle.CHOSEN),  # the Players chosen never travel
            {"roll": 1, "for": "Notice", "character_name": "Aelfric"},
        ),
    )

    assert pane.lines()[-1] == "Aelfric (Notice): the storyguide rolled."
    pane.roll_button.click()
    form = ran[-1]
    assert isinstance(form, commands.Form)
    form.apply({f.key: f.value for f in form.fields()})
    assert table.rolled and table.rolled[0].character_id == "aelfric"


@pytest.mark.usefixtures("app")
def test_a_seat_never_offers_strike() -> None:
    """Strike is the host's: its computer keeps the Chronicle."""
    saga = _saga()
    saga.sessions[0].storyguide_id = "ana"
    held = chronicle.SeatChronicle()
    pane = ChroniclePane(SCRIPTORUM, lambda _c: None)
    pane.attach(saga, saga.sessions[0], held, "ana", FakeTable(held=held))

    held.take(
        "s1",
        chronicle.Entry(
            1,
            "",
            chronicle.ROLL,
            "ana",
            chronicle.table(),
            {
                "stress": True,
                "faces": [5],
                "botch_faces": [],
                "die": 5,
                "modifier": 0,
                "total": 5,
                "botches": 0,
                "ease_factor": None,
                "for": "",
                "character_id": "",
                "character_name": "",
            },
        ),
    )

    dice = pane.card_list()[-1].findChild(DiceRow, "dice")
    assert isinstance(dice, DiceRow) and not dice.can_strike


# -- a seat's connection, over a real one --


async def test_a_seat_session_follows_the_chronicle_and_rolls() -> None:
    table = Table()
    table.port = await table.host.start()
    try:
        async with await table.seat("Anna"):
            pass  # approved, and its credential kept
        seat = SeatSession(
            f"ws://127.0.0.1:{table.port}{PATH}", table.pin, table.vaults["Anna"]
        )
        await asyncio.to_thread(seat.connect)
        await asyncio.to_thread(seat.sign_in, PASSCODE)
        held = chronicle.SeatChronicle()
        got: list[tuple[str, chronicle.Entry]] = []
        seat.follow_chronicle(
            lambda s, e: got.append((s, e)), lambda: (held.session_id, held.last)
        )
        refused = await asyncio.to_thread(
            seat.roll, chronicle.RollRequest(character_id="aelfric")
        )
        deadline = time.monotonic() + 5
        while len(got) < 2 and time.monotonic() < deadline:
            await asyncio.sleep(0.05)
        await asyncio.to_thread(seat.close)
    finally:
        await table.host.stop()

    assert refused is None
    assert [e.kind for _s, e in got] == ["begin", "roll"]


# -- found in review of the wiring --


@pytest.mark.usefixtures("app")
def test_a_new_session_at_a_seat_clears_the_last_ones_cards() -> None:
    saga = _saga()
    held = chronicle.SeatChronicle()
    pane = ChroniclePane(SCRIPTORUM, lambda _c: None)
    pane.attach(saga, saga.sessions[0], held, "ana", FakeTable(held=held))
    held.take("s1", chronicle.Entry(1, "", "begin", HOST, chronicle.table()))
    held.take("s1", chronicle.Entry(2, "", "end", HOST, chronicle.table()))

    held.take("s2", chronicle.Entry(1, "", "begin", HOST, chronicle.table()))

    assert pane.lines() == ["Session begun."]


def test_refresh_reads_the_file_only_when_it_has_grown(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    saga = _saga()
    book = chronicle.begin(saga, saga.sessions[0], by=HOST)
    book.refresh()
    reads: list[bool] = []
    real = chronicle._load

    def counted(path: Path, *, mend: bool = False) -> list[chronicle.Entry]:
        reads.append(mend)
        return real(path, mend=mend)

    monkeypatch.setattr(chronicle, "_load", counted)

    assert book.refresh() == []
    assert reads == []
