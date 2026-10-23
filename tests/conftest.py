import os
import sys

import pytest
from tiers import is_screen_test_file

from ars_magica_manager import catalog, neighbour_filter, paths, storage

# The desktop version's sounds stay silent under test (gui/sounds.py).
os.environ["ARMARIUS_SOUNDS"] = "off"


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "ui: a screen test (Textual Pilot or Qt), marked automatically; "
        "-m 'not ui' runs the fast tier",
    )


def pytest_collection_modifyitems(config, items):
    for item in items:
        if is_screen_test_file(item.path):
            item.add_marker(pytest.mark.ui)


@pytest.fixture(autouse=True)
def isolated_sagas_dir(tmp_path, monkeypatch):
    """Every test reads and writes sagas in its own temp dir, never
    data/sagas/ -- which also makes the suite safe to run in parallel."""
    # The data folder in use is the test's temp dir: its sagas, exports
    # ('x' on a sheet), portraits and settings all go there.
    monkeypatch.setattr(paths, "_in_use", tmp_path)
    # What this "copy" of the app last saw of each saga.
    monkeypatch.setattr(storage, "_last_seen", {})
    # And how each saga's Region lists are filtered.
    monkeypatch.setattr(neighbour_filter, "_CURRENT", {})


@pytest.fixture(autouse=True)
def isolated_location_file(tmp_path, monkeypatch):
    """Choosing a save folder writes location.json and moves the saves out
    of the data folder: both in a temp dir, never the user's own; and no
    folder chosen by the environment (under the app's new name or its old
    one)."""
    monkeypatch.setattr(paths, "LOCATION_FILE", tmp_path / "config" / "location.json")
    monkeypatch.setattr(
        paths, "OLD_LOCATION_FILE", tmp_path / "old_config" / "location.json"
    )
    monkeypatch.setattr(paths, "default_data_dir", lambda: tmp_path / "data")
    monkeypatch.setattr(paths, "old_default_data_dir", lambda: tmp_path / "old_data")
    monkeypatch.setattr(paths, "_fallback", None)
    monkeypatch.delenv(paths.ENV_VAR, raising=False)
    monkeypatch.delenv(paths.OLD_ENV_VAR, raising=False)


@pytest.fixture(autouse=True)
def no_saga_entries_in_the_catalogs():
    """A saga's user-made entries join the shared catalogs while it is the
    one in use (catalog.use_saga): start and end each test with
    none, so one test's saga doesn't show in another's pickers."""
    catalog.use_saga(None)
    yield
    catalog.use_saga(None)


@pytest.fixture(autouse=True)
def close_qt_windows():
    """Close and delete every top-level Qt window a test left open. The
    QApplication lives for the whole process, so without this each test's
    windows stay alive and every later test in that process gets slower."""
    yield
    if "PySide6.QtWidgets" not in sys.modules:
        return
    from PySide6.QtCore import QCoreApplication, QEvent
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        return
    for window in QApplication.topLevelWidgets():
        window.close()
        window.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()
