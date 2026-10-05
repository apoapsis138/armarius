"""Where the user's data is kept, and moving it out of the repo (STORY-1127)."""

import json

import pytest

from ars_magica_manager import paths


@pytest.fixture
def no_choice(tmp_path, monkeypatch):
    """No environment variable and no location file: the default."""
    monkeypatch.delenv(paths.ENV_VAR, raising=False)
    monkeypatch.setattr(paths, "LOCATION_FILE", tmp_path / "config" / "location.json")
    monkeypatch.setattr(
        paths.platformdirs, "user_documents_dir", lambda: str(tmp_path / "Docs")
    )
    return tmp_path


def test_the_data_folder_defaults_to_documents(no_choice):
    assert paths.data_dir() == no_choice / "Docs" / "Ars Magica Manager"


def test_a_location_file_chooses_another_folder(no_choice):
    paths.LOCATION_FILE.parent.mkdir()
    paths.LOCATION_FILE.write_text(
        json.dumps({"data_dir": str(no_choice / "Elsewhere")}), encoding="utf-8"
    )
    assert paths.data_dir() == no_choice / "Elsewhere"


@pytest.mark.parametrize("text", ["{not json", "[]", '{"data_dir": ""}', "{}"])
def test_an_unusable_location_file_is_ignored(no_choice, text):
    paths.LOCATION_FILE.parent.mkdir()
    paths.LOCATION_FILE.write_text(text, encoding="utf-8")
    assert paths.data_dir() == paths.default_data_dir()


def test_the_environment_variable_wins(no_choice, monkeypatch):
    paths.LOCATION_FILE.parent.mkdir()
    paths.LOCATION_FILE.write_text('{"data_dir": "x"}', encoding="utf-8")
    monkeypatch.setenv(paths.ENV_VAR, str(no_choice / "FromEnv"))
    assert paths.data_dir() == no_choice / "FromEnv"


def _legacy(root):
    old = root / "repo_data"
    (old / "sagas" / "backups").mkdir(parents=True)
    (old / "sagas" / "a.json").write_text("A", encoding="utf-8")
    (old / "sagas" / ".gitkeep").write_text("", encoding="utf-8")
    (old / "sagas" / "backups" / "a.1.json").write_text("A1", encoding="utf-8")
    (old / "exports").mkdir()
    (old / "exports" / "c.amm.json").write_text("C", encoding="utf-8")
    (old / "app_settings.json").write_text("{}", encoding="utf-8")
    (old / "spell_catalog.json").write_text("[]", encoding="utf-8")
    return old


def test_the_repo_data_moves_once(tmp_path):
    old, new = _legacy(tmp_path), tmp_path / "new"
    notes = paths.move_legacy_data(old, new)
    assert notes == [
        "Moved sagas/a.json",
        "Moved sagas/backups/a.1.json",
        "Moved exports/c.amm.json",
        "Moved app_settings.json",
    ]
    assert (new / "sagas" / "a.json").read_text(encoding="utf-8") == "A"
    assert (new / "sagas" / "backups" / "a.1.json").exists()
    assert (new / "exports" / "c.amm.json").exists()
    assert (new / "app_settings.json").exists()
    # The catalogs and the repo's placeholder stay.
    assert (old / "spell_catalog.json").exists()
    assert (old / "sagas" / ".gitkeep").exists()
    assert not (old / "sagas" / "a.json").exists()
    assert paths.move_legacy_data(old, new) == []  # nothing left to move


def test_moving_never_overwrites_what_is_already_there(tmp_path):
    old, new = _legacy(tmp_path), tmp_path / "new"
    (new / "sagas").mkdir(parents=True)
    (new / "sagas" / "a.json").write_text("newer", encoding="utf-8")
    notes = paths.move_legacy_data(old, new)
    assert any(note.startswith("Left ") for note in notes)
    assert (new / "sagas" / "a.json").read_text(encoding="utf-8") == "newer"
    assert (old / "sagas" / "a.json").read_text(encoding="utf-8") == "A"


def test_nothing_moves_when_the_data_folder_is_the_repos(tmp_path):
    old = _legacy(tmp_path)
    assert paths.move_legacy_data(old, old) == []


async def test_the_app_says_what_moved_on_start():
    from ars_magica_manager.app import ArsMagicaManagerApp

    app = ArsMagicaManagerApp()
    app.startup_notes = ("Moved sagas/a.json",)
    async with app.run_test():
        shown = [(n.title, n.message) for n in app._notifications]
    assert len(shown) == 1
    assert shown[0][0].startswith("Your data moved to ")
    assert shown[0][1] == "Moved sagas/a.json"
