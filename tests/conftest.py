import pytest

from ars_magica_manager import catalog, paths, settings, storage


@pytest.fixture(autouse=True)
def isolated_sagas_dir(tmp_path, monkeypatch):
    """Every test reads and writes sagas in its own temp dir, never
    data/sagas/ -- which also makes the suite safe to run in parallel."""
    monkeypatch.setattr(storage, "SAGAS_DIR", tmp_path)
    # Exports ('x' on a sheet) go to a temp folder too.
    monkeypatch.setattr(storage, "EXPORTS_DIR", tmp_path / "exports")
    # And portraits chosen for a character.
    monkeypatch.setattr(storage, "PORTRAITS_DIR", tmp_path / "portraits")
    # What this "copy" of the app last saw of each saga.
    monkeypatch.setattr(storage, "_last_seen", {})


@pytest.fixture(autouse=True)
def isolated_settings_path(tmp_path, monkeypatch):
    # A sibling dir, not tmp_path itself -- isolated_sagas_dir points
    # storage.SAGAS_DIR at tmp_path and globs it for "*.json".
    monkeypatch.setattr(
        settings, "SETTINGS_PATH", tmp_path / "config" / "app_settings.json"
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
