import pytest

from ars_magica_manager import settings


def test_load_settings_missing_file_returns_empty_dict(tmp_path, monkeypatch):
    assert settings.load_settings() == {}


def test_save_and_load_settings_round_trip(tmp_path, monkeypatch):

    settings.save_settings({"theme": "scriptorum-dark"})

    assert settings.load_settings() == {"theme": "scriptorum-dark"}


def test_update_settings_keeps_the_other_keys(tmp_path, monkeypatch):
    settings.save_settings({"theme": "scriptorum", "other": 1})

    settings.update_settings(theme="scriptorum-dark")

    assert settings.load_settings() == {"theme": "scriptorum-dark", "other": 1}


@pytest.mark.parametrize("text", ["{not json", "[1, 2]", "", "\x00\xff"])
def test_an_unreadable_settings_file_counts_as_no_settings(tmp_path, monkeypatch, text):
    """A damaged settings file must not stop the app starting."""
    path = tmp_path / "app_settings.json"
    assert settings.settings_path() == path
    path.write_text(text, encoding="utf-8")

    assert settings.load_settings() == {}

    settings.update_settings(theme="scriptorum-dark")
    assert settings.load_settings() == {"theme": "scriptorum-dark"}


def test_saving_settings_leaves_no_temp_file(tmp_path, monkeypatch):
    settings.save_settings({"theme": "scriptorum"})
    settings.save_settings({"theme": "scriptorum-dark"})
    assert [p.name for p in tmp_path.iterdir()] == ["app_settings.json"]
