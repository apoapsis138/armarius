"""The desktop picks up another copy's save (a browser player, a Remote
seat), as the terminal does: the page drawn again, with a note saying who
changed what, but not while a form is open."""

from __future__ import annotations

import json
import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QDialog

from ars_magica_manager import players, storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import Character, Saga


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application  # pyright: ignore[reportReturnType]


def _window() -> tuple[MainWindow, Saga]:
    saga = Saga(
        id="shared",
        name="Shared",
        characters=[Character(id="mag1", name="Leandro", type="magus")],
    )
    players.add(saga, {"name": "Anna", "passcode": "a long enough passcode"})
    storage.save_saga(saga)
    main = MainWindow(saga_ids=[saga.id])
    main.show()
    assert main.saga is not None and main.shared_timer.isActive()
    main.show_character("mag1")
    return main, main.saga


def _saved_elsewhere(saga_id: str, name: str) -> None:
    """Another copy saves: Anna renames the magus."""
    path = storage.saga_path(saga_id)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["characters"][0]["name"] = name
    data["saved_by"] = "Anna"
    path.write_text(json.dumps(data), encoding="utf-8")


@pytest.mark.usefixtures("app")
def test_another_copys_save_is_picked_up_with_a_note() -> None:
    main, saga = _window()
    _saved_elsewhere(saga.id, "Leandro the Bold")
    main.shared_tick()
    assert saga.characters[0].name == "Leandro the Bold"
    assert main.note.isVisible()
    assert main.note.text() == "Anna changed Leandro the Bold; reloaded."


@pytest.mark.usefixtures("app")
def test_a_season_advanced_elsewhere_turns_the_dial_here(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    main, saga = _window()
    turned: list[bool] = []
    monkeypatch.setattr(main, "_turn_the_dial", lambda then: turned.append(True))
    path = storage.saga_path(saga.id)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["current_season"] = "Summer"
    data["saved_by"] = "Hedda"
    path.write_text(json.dumps(data), encoding="utf-8")
    main.shared_tick()
    assert turned == [True]
    assert (
        main.note.text() == f"Hedda advanced the season to Summer {saga.current_year}."
    )
    _saved_elsewhere(saga.id, "Leandro the Bold")  # no new season: no dial
    main.shared_tick()
    assert turned == [True]


@pytest.mark.usefixtures("app")
def test_nothing_is_picked_up_while_a_form_is_open() -> None:
    main, saga = _window()
    main._open = QDialog(main)  # a form open over the page
    _saved_elsewhere(saga.id, "Leandro the Bold")
    main.shared_tick()
    assert saga.characters[0].name == "Leandro"
    main._open = None
    main.shared_tick()
    assert saga.characters[0].name == "Leandro the Bold"
