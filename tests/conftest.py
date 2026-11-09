import os
import sys

import pytest
from tiers import is_screen_test_file

from ars_magica_manager import (
    catalog,
    neighbour_filter,
    paths,
    seat,
    storage,
    viewing,
)

# The desktop version's sounds stay silent under test (gui/sounds.py).
os.environ["ARMARIUS_SOUNDS"] = "off"
# ...and still: every movement ends at once (gui/motion.py).
os.environ["ARMARIUS_MOTION"] = "off"


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
    # And who is reading: the storyguide, unless a test says otherwise.
    monkeypatch.setattr(viewing, "_in_use", viewing.STORYGUIDE_VIEWER)
    monkeypatch.setattr(viewing, "_saga", None)
    # And no one seated (seat.py): a player's window seats its player for
    # the whole process, whose guard would then check the next test's saves.
    monkeypatch.setattr(storage, "guard", None)
    monkeypatch.setattr(storage, "saved_by", "")
    monkeypatch.setattr(seat, "_on_show", None)


#: How long a window may wait for an answer in a test before it gives up
#: (ms). A test answers at once (a timer, or `ask` replaced), so a window
#: still waiting is one no test will answer: without this the test, and its
#: worker, would wait forever.
MODAL_WAIT_MS = 5000


@pytest.fixture(autouse=True)
def windows_never_wait_forever(monkeypatch):
    """A Qt window that waits for an answer gives up after MODAL_WAIT_MS
    and fails the test, naming the window."""
    if "PySide6.QtWidgets" not in sys.modules:
        yield
        return
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QDialog

    real = QDialog.exec
    stuck: list[str] = []

    def bounded(dialog: QDialog) -> int:
        def give_up() -> None:
            stuck.append(dialog.windowTitle() or type(dialog).__name__)
            dialog.done(QDialog.DialogCode.Rejected)  # done: no "are you sure?"

        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(give_up)
        timer.start(MODAL_WAIT_MS)
        try:
            return real(dialog)
        finally:
            timer.stop()

    monkeypatch.setattr(QDialog, "exec", bounded)
    yield
    if stuck:
        pytest.fail(
            "A window waited for an answer no test gave: "
            + ", ".join(repr(title) for title in stuck)
        )


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
        # A form left with changes would otherwise stop to ask.
        if hasattr(window, "unsaved"):
            window.unsaved = lambda: False
        # So would a joined saga's window holding changes not yet sent.
        if hasattr(window, "unsent"):
            window.unsent = False
        window.close()
        window.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()
