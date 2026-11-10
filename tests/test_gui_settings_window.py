"""The Settings window the title bar's gear opens (gui/settings_window.py):
the themes by group, applied when chosen, and the sounds and Reduce
Motion."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from ars_magica_manager import settings
from ars_magica_manager.gui import motion, pictures, sounds
from ars_magica_manager.gui.settings_window import NAME_ROLE, SettingsWindow
from ars_magica_manager.gui.style.liveries import GROUPS, THEMES
from ars_magica_manager.gui.themes import SCRIPTORUM, SCRIPTORUM_DARK
from ars_magica_manager.gui.window import MainWindow


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert isinstance(application, QApplication)
    assert pictures.register_fonts() == []
    return application


@pytest.mark.usefixtures("app")
def test_the_gear_opens_the_settings_window_not_a_menu() -> None:
    window = MainWindow(saga_ids=[])
    assert window.settings.menu() is None
    window.settings.click()
    shown = window._settings
    assert isinstance(shown, SettingsWindow) and shown.isVisible()
    assert not shown.isModal()
    # A second click brings the same window forward.
    window.settings.click()
    assert window._settings is shown
    shown.close()
    window.close()


@pytest.mark.usefixtures("app")
def test_the_themes_are_listed_under_their_groups_scriptorum_first() -> None:
    window = SettingsWindow(SCRIPTORUM, THEMES[0], lambda _name: None)
    rows = [window.themes.item(i) for i in range(window.themes.count())]
    names = [row.data(NAME_ROLE) for row in rows]
    headings = [row.text() for row, name in zip(rows, names, strict=True) if not name]
    assert headings[0] == GROUPS[0] == "Scriptorum"
    assert headings == [g for g in GROUPS if any(t.group == g for t in THEMES)]
    themed = [name for name in names if name]
    assert themed[:2] == [SCRIPTORUM.name, SCRIPTORUM_DARK.name]
    assert sorted(themed) == sorted(theme.name for theme in THEMES)
    # Every theme's row has its sample; a heading can't be chosen.
    for row, name in zip(rows, names, strict=True):
        assert bool(name) == (not row.icon().isNull())
        assert bool(name) == (row.flags() != Qt.ItemFlag.NoItemFlags)
    assert window.chosen() == SCRIPTORUM.name
    window.close()


@pytest.mark.usefixtures("app")
def test_choosing_a_theme_applies_it_at_once_and_remembers_it() -> None:
    window = MainWindow(saga_ids=[])
    window.open_settings()
    first = window._settings
    assert first is not None
    first.pick(SCRIPTORUM_DARK.name)
    assert window.palette_ is SCRIPTORUM_DARK
    assert settings.load_settings()["desktop_theme"] == SCRIPTORUM_DARK.name
    # Still open, drawn again in the new theme with it chosen.
    shown = window._settings
    assert shown is not None and shown is not first and shown.isVisible()
    assert shown.p is SCRIPTORUM_DARK and shown.chosen() == SCRIPTORUM_DARK.name
    assert MainWindow(saga_ids=[]).palette_ is SCRIPTORUM_DARK
    shown.close()
    window.close()


@pytest.mark.usefixtures("app")
def test_an_unknown_theme_name_changes_nothing() -> None:
    window = MainWindow(saga_ids=[])
    window.choose_theme("No Such Theme")
    window.choose_theme(SCRIPTORUM.name + " Drafting")
    assert window.palette_ is SCRIPTORUM
    window.close()


@pytest.mark.usefixtures("app")
def test_the_settings_window_turns_the_sounds_on_and_off(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sounds, "play", lambda _name: None)
    monkeypatch.setattr(motion, "windows_animates", lambda: True)
    window = SettingsWindow(SCRIPTORUM, THEMES[0], lambda _name: None)
    was = sounds.enabled()
    assert window.sounds.isChecked() == was
    window.sounds.click()
    assert sounds.enabled() != was
    window.sounds.click()
    assert sounds.enabled() == was
    window.close()
