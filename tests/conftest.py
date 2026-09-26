import pytest

from ars_magica_manager import settings, storage


@pytest.fixture(autouse=True)
def isolated_sagas_dir(tmp_path, monkeypatch):
    """Every test reads and writes sagas in its own temp dir, never
    data/sagas/ -- which also makes the suite safe to run in parallel."""
    monkeypatch.setattr(storage, "SAGAS_DIR", tmp_path)


@pytest.fixture(autouse=True)
def isolated_settings_path(tmp_path, monkeypatch):
    # A sibling dir, not tmp_path itself -- isolated_sagas_dir points
    # storage.SAGAS_DIR at tmp_path and globs it for "*.json".
    monkeypatch.setattr(
        settings, "SETTINGS_PATH", tmp_path / "config" / "app_settings.json"
    )
