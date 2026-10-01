import pytest

from ars_magica_manager import catalog, settings, storage


@pytest.fixture(autouse=True)
def isolated_sagas_dir(tmp_path, monkeypatch):
    """Every test reads and writes sagas in its own temp dir, never
    data/sagas/ -- which also makes the suite safe to run in parallel."""
    monkeypatch.setattr(storage, "SAGAS_DIR", tmp_path)
    # Exports ('x' on a sheet, STORY-109) go to a temp folder too.
    monkeypatch.setattr(storage, "EXPORTS_DIR", tmp_path / "exports")


@pytest.fixture(autouse=True)
def isolated_settings_path(tmp_path, monkeypatch):
    # A sibling dir, not tmp_path itself -- isolated_sagas_dir points
    # storage.SAGAS_DIR at tmp_path and globs it for "*.json".
    monkeypatch.setattr(
        settings, "SETTINGS_PATH", tmp_path / "config" / "app_settings.json"
    )


@pytest.fixture(autouse=True)
def no_saga_entries_in_the_catalogs():
    """A saga's user-made entries join the shared catalogs while it is the
    one in use (catalog.use_saga, STORY-708): start and end each test with
    none, so one test's saga doesn't show in another's pickers."""
    catalog.use_saga(None)
    yield
    catalog.use_saga(None)
