"""The App update notice on the desktop (gui/updates.py): the title page's
line, the gear's badge, Settings' Update row, What's new in Help, and the
Version mismatch's Update."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from ars_magica_manager import settings, updates
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.help import HelpPage
from ars_magica_manager.gui.join import offers_update, reach_problem
from ars_magica_manager.gui.settings_window import SettingsWindow
from ars_magica_manager.gui.themes import SCRIPTORUM
from ars_magica_manager.gui.updates import UpdateNotices, UpdateRow
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.remote.client import VersionMismatch

NOTES = "### Pagina\n\n- **My sheet.** <b>bold</b> stays text.\n- Second.\n- Third."


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert isinstance(application, QApplication)
    assert pictures.register_fonts() == []
    return application


@pytest.fixture
def found(monkeypatch: pytest.MonkeyPatch) -> None:
    """A copy that checks, and a check that found 99.0.0 (newer than any
    running version)."""
    monkeypatch.delenv(updates.ENV_VAR, raising=False)
    remember("99.0.0", NOTES)


def remember(version: str, notes: str) -> None:
    settings.update_settings(
        **{
            updates.FOUND: {
                "version": version,
                "date": "2026-12-01",
                "notes": notes,
                "url": updates.LATEST_URL,
            }
        }
    )


def _titled() -> MainWindow:
    window = MainWindow(saga_ids=[])
    window.show_title()
    return window


@pytest.mark.usefixtures("app", "found")
def test_the_title_page_and_the_gear_show_the_notice() -> None:
    window = _titled()
    assert window.title is not None
    line = window.title.update_line
    assert not line.isHidden()
    assert line.words == "Armarius 99.0.0 is available"
    assert line.colour == window.palette_["accent"]
    assert "99.0.0 is available" in window.settings.toolTip()
    # The line opens Settings, its Update row at the top.
    line.open()
    shown = window._settings
    assert isinstance(shown, SettingsWindow) and shown.isVisible()
    row = shown.update_row
    assert isinstance(row, UpdateRow)
    assert row.headline.text() == "! Armarius 99.0.0 is available (2026-12-01)"
    assert row.lines.text() == "My sheet. <b>bold</b> stays text.\nSecond."
    assert not row.skip.isHidden()
    shown.close()
    window.close()


@pytest.mark.usefixtures("app", "found")
def test_skip_hides_the_line_and_the_badge_but_settings_shows_it_faintly() -> None:
    window = _titled()
    window.open_update_row()
    shown = window._settings
    assert shown is not None and isinstance(shown.update_row, UpdateRow)
    shown.update_row.skip.click()
    assert settings.load_settings()[updates.SKIPPED] == "99.0.0"
    assert window.title is not None and window.title.update_line.isHidden()
    assert window.settings.toolTip() == "Settings: theme, sounds and motion"
    assert shown.update_row.headline.text().endswith(", skipped")
    assert shown.update_row.skip.isHidden()
    shown.close()
    window.close()


@pytest.mark.usefixtures("app", "found")
def test_a_security_update_uses_the_warning_colour() -> None:
    remember("99.0.0", "### Sodales\n\n- **Security:** Closed.")
    window = _titled()
    assert window.title is not None
    line = window.title.update_line
    assert line.words == "Armarius 99.0.0 is available, with security fixes"
    assert line.colour == window.palette_["text-warning"]
    window.close()


@pytest.mark.usefixtures("app")
def test_with_checks_off_nothing_shows() -> None:
    remember("99.0.0", NOTES)  # the suite's ARMARIUS_UPDATES=off stands
    window = _titled()
    assert window.title is not None and window.title.update_line.isHidden()
    window.close()


@pytest.mark.usefixtures("app", "found")
def test_whats_new_shows_the_notes_in_help_as_plain_text() -> None:
    window = MainWindow(saga_ids=[])
    notice = window.update_notices.notice
    assert notice is not None
    window.show_update_notes(notice)
    page = window.page()
    assert isinstance(page, HelpPage)
    shown = page.shown_text()
    assert shown.startswith("Armarius 99.0.0")
    assert "<b>bold</b>" in shown  # never drawn as HTML
    assert "### Pagina" in shown  # nor as Markdown
    window.close()


@pytest.mark.usefixtures("app")
def test_check_now_asks_in_a_thread_and_says_what_it_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(updates.ENV_VAR, raising=False)

    def fetch(url: str, headers: object, timeout: float) -> bytes:
        raise OSError("network is down")

    notices = UpdateNotices(updates.Build(), fetch=fetch)
    said: list[str] = []
    notices.checked.connect(said.append)
    row = UpdateRow(SCRIPTORUM, notices, lambda _n: None, lambda _u: None)
    row.check_now.click()
    for _ in range(200):
        if said:
            break
        QTest.qWait(10)
    assert said == ["Couldn't reach GitHub: network is down."]
    assert row.outcome.text() == said[0]


@pytest.mark.usefixtures("app")
def test_a_copy_that_never_checks_says_so() -> None:
    notices = UpdateNotices(updates.Quiet())
    row = UpdateRow(SCRIPTORUM, notices, lambda _n: None, lambda _u: None)
    assert not row.check_now.isEnabled() and not row.check.isEnabled()
    assert "turned off" in row.outcome.text()


@pytest.mark.usefixtures("app")
def test_a_minor_mismatch_shows_in_the_notices_places() -> None:
    window = MainWindow(saga_ids=[])
    window.update_notices.set_mismatch(updates.mismatch("4.13.1", "4.14.0"))
    assert "haven't been tested together" in window.settings.toolTip()
    window.update_notices.set_mismatch(updates.mismatch("4.13.1", "5.0.0"))
    assert window.settings.toolTip() == "Settings: theme, sounds and motion"
    window.update_notices.set_mismatch(None)
    window.close()


def test_a_major_mismatch_offers_update_only_to_the_older(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(updates, "this_copy", lambda **_: updates.Build())
    older = VersionMismatch("4.13.1", "5.0.0")
    assert offers_update(older)
    assert "update this app" in reach_problem(older)
    newer = VersionMismatch("5.0.0", "4.13.1")
    assert not offers_update(newer)
    assert reach_problem(newer) == (
        "Your storyguide's Armarius is older (4.13.1). Ask them to update."
    )
    # A checkout has no Download page: it's told to pull main.
    monkeypatch.setattr(updates, "this_copy", lambda **_: updates.Checkout())
    assert not offers_update(older)
    assert "pull main" in reach_problem(older)
