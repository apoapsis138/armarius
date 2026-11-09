"""Who else has a record open, on the desktop (presence.py): the storyguide's
window notes its own record and shows who else is on it, beside the trail,
with a mark and names; and a Remote seat's "here" names only records the
seat may read."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from ars_magica_manager import players, presence, storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import Character, Saga
from ars_magica_manager.remote.protocol import Refused, Session
from ars_magica_manager.remote.records import SeatSnapshots, records_specs


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application  # pyright: ignore[reportReturnType]


def _saga() -> Saga:
    saga = Saga(
        id="shared",
        name="Shared",
        characters=[
            Character(id="mag1", name="Leandro", type="magus"),
            Character(id="npc1", name="Hidden", type="companion", known=False),
        ],
    )
    anna = players.add(saga, {"name": "Anna", "passcode": "a long enough passcode"})
    saga.characters[0].background.player_ids = [anna.id]
    storage.save_saga(saga)
    return saga


@pytest.mark.usefixtures("app")
def test_the_window_shows_who_else_has_the_record_open() -> None:
    saga = _saga()
    main = MainWindow(saga_ids=[saga.id])
    main.show()
    main.show_character("mag1")
    assert main.open_record_key() == "characters:mag1"
    presence.note("browser-1", saga.id, "Anna", "characters:mag1")
    presence.note("seat-2", saga.id, "Bruno (storyguide)", "characters:mag1")
    main.shared_tick()
    assert main.here_label.isVisibleTo(main)
    assert (
        main.here_label.text().strip() == "◉ Anna, Bruno (storyguide) are also viewing"
    )
    presence.leave("seat-2")
    presence.leave("browser-1")
    main.shared_tick()
    assert not main.here_label.isVisibleTo(main)
    main.close()


def test_a_seat_is_told_who_else_is_here_only_for_records_it_may_read() -> None:
    saga = _saga()
    anna = players.find(saga, "Anna")
    assert anna is not None
    snapshots = SeatSnapshots(saga.id)
    [_snapshot, _picture, here] = records_specs(snapshots, lambda folder, name: None)
    session = Session(label="c1", player_id=anna.id)
    presence.note("storyguide", saga.id, "", "characters:mag1")
    presence.note("storyguide-2", saga.id, "", "characters:npc1")
    reply = here.handler(session, {"record": "characters:mag1"})
    assert reply.body["others"] == "The storyguide"
    # A record the seat can't read names no one, and isn't noted.
    reply = here.handler(session, {"record": "characters:npc1"})
    assert reply.body["others"] == ""
    assert presence.others_on("storyguide-2", saga.id, "characters:npc1") == []
    with pytest.raises(Refused):
        here.handler(Session(label="c2", player_id="gone"), {"record": ""})
