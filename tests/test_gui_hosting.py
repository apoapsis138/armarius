"""Hosting from the desktop: Host for Players and Stop Hosting in the saga
page's Saga Management start and stop the core's host (hosting.HOST)."""

from __future__ import annotations

import os
import socket
import urllib.request

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering
from PySide6.QtWidgets import QApplication, QLabel, QPushButton
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import hosting, storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.window import MainWindow


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


@pytest.fixture
def host(monkeypatch):
    monkeypatch.delenv(hosting.TRANSPORT_VAR, raising=False)
    monkeypatch.delenv(hosting.OLD_TRANSPORT_VAR, raising=False)
    fresh = hosting.Host()
    monkeypatch.setattr(hosting, "HOST", fresh)
    yield fresh
    fresh.stop()


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("localhost", 0))
        return probe.getsockname()[1]


def _management(window: MainWindow) -> dict[str, QPushButton]:
    page = window.page()
    assert page is not None
    page.codex.open_chapter("Saga Management")  # type: ignore[attr-defined]
    page = window.page()
    assert page is not None
    return {
        b.text().strip(): b
        for b in page.findChildren(QPushButton)
        if b.objectName() == "edit" and b.isVisibleTo(page)
    }


def _lines(window: MainWindow) -> list[str]:
    page = window.page()
    assert page is not None
    return [label.text() for label in page.findChildren(QLabel)]


def test_saga_management_hosts_the_saga_and_stops_hosting(app, host):
    saga = _sample_saga_with_covenant()
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.show()
    buttons = _management(window)
    assert "Host for Players" in buttons and "Stop Hosting" not in buttons

    port = _free_port()
    asked = answering(window, {"address": "localhost", "port": str(port)})
    buttons["Host for Players"].click()
    assert asked[0].windowTitle() == "Host for Players"
    assert host.running
    title, words = window.told[0]
    assert title == "Host for Players" and f"http://localhost:{port}" in words
    with urllib.request.urlopen(f"http://localhost:{port}", timeout=5) as reply:
        assert reply.status == 200

    # The page now offers Stop Hosting, beside where players reach it.
    buttons = _management(window)
    assert "Stop Hosting" in buttons and "Host for Players" not in buttons
    assert any(f"http://localhost:{port}" in line for line in _lines(window))

    answering(window, True)
    buttons["Stop Hosting"].click()
    assert not host.running
    assert "Host for Players" in _management(window)
