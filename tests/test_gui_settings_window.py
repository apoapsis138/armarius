"""The Settings window the title bar's gear opens (gui/settings_window.py):
the themes by group, applied when chosen, and the sounds and Reduce
Motion."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QComboBox

from ars_magica_manager import settings
from ars_magica_manager.gui import motion, pictures, sounds
from ars_magica_manager.gui.settings_window import SettingsWindow
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
def test_the_themes_are_offered_under_their_groups_scriptorum_first() -> None:
    window = SettingsWindow(SCRIPTORUM, THEMES[0], lambda _name: None)
    assert isinstance(window.themes, QComboBox)
    model = window.themes.model()
    names = window.names()
    headings = [
        model.index(i, 0).data() for i, name in enumerate(names) if name is None
    ]
    assert headings[0] == GROUPS[0] == "Scriptorum"
    assert headings == [g for g in GROUPS if any(t.group == g for t in THEMES)]
    themed = [name for name in names if name]
    assert themed[:2] == [SCRIPTORUM.name, SCRIPTORUM_DARK.name]
    assert sorted(themed) == sorted(theme.name for theme in THEMES)
    # Every theme's row has its sample and its few words; a heading can't
    # be chosen.
    for i, name in enumerate(names):
        index = model.index(i, 0)
        flags = index.flags()
        assert bool(name) == bool(flags & Qt.ItemFlag.ItemIsSelectable)
        if name:
            assert isinstance(index.data(Qt.ItemDataRole.DecorationRole), QPixmap)
            assert index.data(Qt.ItemDataRole.ToolTipRole)
    assert window.chosen() == SCRIPTORUM.name
    # No long list: the window is no taller than its few settings need.
    assert window.height() < 500
    window.close()


@pytest.mark.usefixtures("app")
def test_the_arrow_keys_step_through_the_themes_past_the_headings() -> None:
    """With the selector closed, Down applies the next theme and skips a
    group's heading; Up comes back."""
    chosen: list[str] = []
    window = SettingsWindow(SCRIPTORUM_DARK, THEMES[1], chosen.append)
    window.show()
    window.themes.setFocus()
    QTest.keyClick(window.themes, Qt.Key.Key_Down)
    # The next theme after Scriptorum Dark is the first True Lineage, past
    # its group's heading.
    first_house = next(t for t in THEMES if t.group == GROUPS[1])
    assert chosen == [first_house.name]
    assert window.chosen() == first_house.name
    QTest.keyClick(window.themes, Qt.Key.Key_Up)
    assert chosen[-1] == SCRIPTORUM_DARK.name
    window.close()


@pytest.mark.usefixtures("app")
def test_one_delegate_draws_a_themes_row_with_its_name_and_words() -> None:
    """The closed box draws the chosen theme's row as the list does: its
    sample and its name (Grab of the box, so nothing else is painted)."""
    window = SettingsWindow(SCRIPTORUM, THEMES[0], lambda _name: None)
    window.show()
    assert window.themes.itemDelegate() is window.themes.row
    picture = window.themes.grab().toImage()
    inked = sum(
        1
        for x in range(0, picture.width(), 2)
        for y in range(0, picture.height(), 2)
        if picture.pixelColor(x, y).name() == SCRIPTORUM["background"].lower()
    )
    # The sample's paper shows inside the box.
    assert inked > 50
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
