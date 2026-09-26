from ars_magica_manager import settings


def test_load_settings_missing_file_returns_empty_dict(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "SETTINGS_PATH", tmp_path / "app_settings.json")
    assert settings.load_settings() == {}


def test_save_and_load_settings_round_trip(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "SETTINGS_PATH", tmp_path / "app_settings.json")

    settings.save_settings({"theme": "scriptorum-dark"})

    assert settings.load_settings() == {"theme": "scriptorum-dark"}
