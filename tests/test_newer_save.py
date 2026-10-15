"""Opening a saga saved by a newer version of the app: what this copy
doesn't know of it survives its saves, and whoever opens it is told."""

from __future__ import annotations

import json

import pytest
from support import everything_saga, wait_until

from ars_magica_manager import __version__, storage
from ars_magica_manager.models import Saga

NEWER = "99.0.0"


def _write(saga_id: str, data: dict) -> None:
    storage.SAGAS_DIR.mkdir(parents=True, exist_ok=True)
    storage.saga_path(saga_id).write_text(json.dumps(data), encoding="utf-8")


def _file(saga_id: str) -> dict:
    return json.loads(storage.saga_path(saga_id).read_text(encoding="utf-8"))


def _from_newer_app(version: str = NEWER) -> dict:
    """A save as a later app might write it: a new list, and a new field on
    a covenant and on a character."""
    storage.save_saga(everything_saga())
    data = _file("test_saga")
    data["app_version"] = version
    data["gazetteer"] = [{"id": "inn1", "name": "The Swan"}]
    data["covenants"][0]["arms"] = {"field": "azure"}
    data["characters"][0]["detail"] = "sketch"
    storage._last_seen.clear()
    _write("test_saga", data)
    return data


@pytest.mark.parametrize(
    ("version", "newer"),
    [
        ("99.0.0", True),
        ("2.999.0", True),
        (__version__, False),
        ("0.1.0", False),
        ("", False),
        ("not a version", False),
        (None, False),
    ],
)
def test_is_newer_version(version, newer):
    assert storage.is_newer_version(version) is newer


def test_a_newer_saves_unknown_data_survives_a_save():
    _from_newer_app()
    saga = storage.load_saga("test_saga")
    saga.name = "Renamed"
    storage.save_saga(saga)

    data = _file("test_saga")
    assert data["name"] == "Renamed"
    assert data["gazetteer"] == [{"id": "inn1", "name": "The Swan"}]
    assert data["covenants"][0]["arms"] == {"field": "azure"}
    assert data["characters"][0]["detail"] == "sketch"
    # Still marked as the newer app's, so it keeps them in its turn.
    assert data["app_version"] == NEWER


def test_a_record_deleted_here_takes_its_unknown_data_with_it():
    _from_newer_app()
    saga = storage.load_saga("test_saga")
    gone = saga.characters.pop(0).id
    storage.save_saga(saga)
    assert gone not in [c["id"] for c in _file("test_saga")["characters"]]


def test_an_older_saves_stale_keys_are_still_dropped():
    storage.save_saga(everything_saga())
    data = _file("test_saga")
    data["app_version"] = "0.1.0"
    data["retired_field"] = 1
    storage._last_seen.clear()
    _write("test_saga", data)

    storage.save_saga(storage.load_saga("test_saga"))
    data = _file("test_saga")
    assert "retired_field" not in data
    assert data["app_version"] == __version__


def test_the_backup_keeps_a_newer_saves_data():
    _from_newer_app()
    storage.backup_saga(storage.load_saga("test_saga"))
    backup = json.loads(storage.backup_path("test_saga").read_text(encoding="utf-8"))
    assert backup["gazetteer"] == [{"id": "inn1", "name": "The Swan"}]


def test_reloading_a_newer_copys_save_keeps_its_data():
    storage.save_saga(everything_saga())
    saga = storage.load_saga("test_saga")
    data = _from_newer_app()
    data["name"] = "Saved by the newer copy"
    _write("test_saga", data)

    assert storage.reload_into(saga) is not None
    assert saga.name == "Saved by the newer copy"
    saga.characters[0].name = "Changed here"
    storage.save_saga(saga)
    on_disk = _file("test_saga")
    assert on_disk["gazetteer"] == [{"id": "inn1", "name": "The Swan"}]
    assert on_disk["characters"][0]["detail"] == "sketch"
    assert on_disk["characters"][0]["name"] == "Changed here"


def test_the_note_names_both_versions():
    assert storage.newer_save_note(Saga(id="s", name="S")) is None
    note = storage.newer_save_note(Saga(id="s", name="S", app_version=NEWER))
    assert note is not None
    assert NEWER in note and __version__ in note


async def test_the_terminal_warns_on_opening_a_newer_save():
    from ars_magica_manager.tui.app import ArsMagicaManagerApp
    from ars_magica_manager.tui.screens import WorkspaceScreen

    _from_newer_app()
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await app.push_screen(WorkspaceScreen(storage.load_saga("test_saga")))
        assert await wait_until(
            pilot, lambda: any(NEWER in n.message for n in app._notifications)
        )


def test_the_desktop_warns_on_opening_a_newer_save():
    pytest.importorskip("PySide6")
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from ars_magica_manager.gui.window import MainWindow

    application = QApplication.instance() or QApplication([])
    _from_newer_app()
    window = MainWindow(saga_ids=[])
    told: list[tuple[str, str]] = []
    window.tell = lambda title, words: told.append((title, words))  # type: ignore[method-assign]
    window.open_saga("test_saga")
    application.processEvents()
    assert len(told) == 1 and NEWER in told[0][1]
