"""The Virtual Tabletop (Preview) setting (virtual_tabletop.py, ADR 0027):
off by default, remembered with the app's other settings."""

from __future__ import annotations

from ars_magica_manager import settings, virtual_tabletop


def test_the_preview_is_off_until_turned_on() -> None:
    assert virtual_tabletop.on() is False


def test_turning_the_preview_on_is_remembered_with_the_other_settings() -> None:
    settings.update_settings(theme="scriptorum")

    virtual_tabletop.set_on(True)

    assert virtual_tabletop.on() is True
    assert settings.load_settings()["theme"] == "scriptorum"
    virtual_tabletop.set_on(False)
    assert virtual_tabletop.on() is False


def test_a_setting_that_is_not_a_flag_reads_as_off() -> None:
    settings.update_settings(virtual_tabletop="yes")

    assert virtual_tabletop.on() is False
