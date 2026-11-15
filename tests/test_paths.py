"""Where the user's data is kept, and moving it out of the repo."""

import json

import pytest

from ars_magica_manager import paths


@pytest.fixture(autouse=True)
def no_folder_in_use(monkeypatch):
    """These tests work out the data folder from the environment and the
    location file, as the app does before it settles on one."""
    monkeypatch.setattr(paths, "_in_use", None)


#: The real default and old defaults (conftest points them at a temp
#: folder, and at none, for every test).
DEFAULT_DATA_DIR = paths.default_data_dir
OLD_DEFAULT_FOLDERS = paths.old_default_folders


@pytest.fixture
def no_choice(tmp_path, monkeypatch):
    """No environment variable and no location file: the default, with
    OneDrive at tmp_path/OneDrive (as on Windows) and the app data folder
    at tmp_path/AppData."""
    monkeypatch.delenv(paths.ENV_VAR, raising=False)
    for var in paths.ONEDRIVE_VARS:
        monkeypatch.delenv(var, raising=False)
    (tmp_path / "OneDrive").mkdir()
    monkeypatch.setenv("OneDrive", str(tmp_path / "OneDrive"))
    monkeypatch.setattr(paths, "LOCATION_FILE", tmp_path / "config" / "location.json")
    monkeypatch.setattr(
        paths, "OLD_LOCATION_FILE", tmp_path / "old_config" / "location.json"
    )
    monkeypatch.setattr(paths, "default_data_dir", DEFAULT_DATA_DIR)
    monkeypatch.setattr(paths, "old_default_folders", OLD_DEFAULT_FOLDERS)
    monkeypatch.setattr(
        paths.platformdirs,
        "user_data_dir",
        lambda name, **_: str(tmp_path / "AppData" / name),
    )
    return tmp_path


def test_the_data_folder_defaults_to_app_data_even_with_onedrive(no_choice):
    assert paths.data_dir() == no_choice / "AppData" / "Armarius"
    paths.keep_old_default_folder()  # no older folder: nothing recorded
    assert paths.source() == "default"
    assert not paths.LOCATION_FILE.exists()


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


def test_the_old_environment_variable_still_chooses_the_folder(no_choice, monkeypatch):
    monkeypatch.setenv(paths.OLD_ENV_VAR, str(no_choice / "FromOldEnv"))
    assert paths.data_dir() == no_choice / "FromOldEnv"
    assert (
        paths.source_text() == "set by the ARS_MAGICA_MANAGER_DATA environment variable"
    )
    # The new name wins when both are set.
    monkeypatch.setenv(paths.ENV_VAR, str(no_choice / "FromEnv"))
    assert paths.data_dir() == no_choice / "FromEnv"
    assert paths.source_text() == "set by the ARMARIUS_DATA environment variable"


def test_a_folder_chosen_under_the_old_name_is_still_used(no_choice):
    paths.OLD_LOCATION_FILE.parent.mkdir()
    paths.OLD_LOCATION_FILE.write_text(
        json.dumps({"data_dir": str(no_choice / "Chosen")}), encoding="utf-8"
    )
    assert paths.data_dir() == no_choice / "Chosen"
    assert paths.source() == "chosen"
    # Choosing again writes the new location file, which wins.
    paths.remember_data_dir(no_choice / "Again")
    assert paths.data_dir() == no_choice / "Again"


def _saga_folder(folder):
    """`folder`, made and holding a saga."""
    (folder / "sagas").mkdir(parents=True)
    (folder / "sagas" / "a.json").write_text("A", encoding="utf-8")
    return folder


def _kept(folder):
    """keep_old_default_folder() recorded `folder` as the chosen one, and
    left it where it was."""
    assert paths.source() == "chosen"
    assert paths.data_dir() == folder
    assert json.loads(paths.LOCATION_FILE.read_text(encoding="utf-8")) == {
        "data_dir": str(folder)
    }
    assert (folder / "sagas" / "a.json").read_text(encoding="utf-8") == "A"


def test_an_old_onedrive_armarius_folder_is_kept_as_chosen(no_choice, monkeypatch):
    old = _saga_folder(no_choice / "OneDrive" / "Armarius")
    paths.keep_old_default_folder()
    _kept(old)
    assert not (no_choice / "AppData" / "Armarius").exists()
    # Emptying it later doesn't send the user to the new default.
    monkeypatch.setattr(paths, "_in_use", None)
    (old / "sagas" / "a.json").unlink()
    paths.keep_old_default_folder()
    assert paths.source() == "chosen"
    assert paths.data_dir() == old


def test_an_old_onedrive_folder_keeps_its_old_name(no_choice):
    old = _saga_folder(no_choice / "OneDrive" / "Ars Magica Manager")
    paths.keep_old_default_folder()
    _kept(old)
    assert not (no_choice / "OneDrive" / "Armarius").exists()


def test_an_old_app_data_folder_keeps_its_old_name(no_choice):
    old = _saga_folder(no_choice / "AppData" / "Ars Magica Manager")
    paths.keep_old_default_folder()
    _kept(old)
    assert not (no_choice / "AppData" / "Armarius").exists()


def test_the_most_recent_old_default_wins(no_choice):
    newest = _saga_folder(no_choice / "OneDrive" / "Armarius")
    _saga_folder(no_choice / "OneDrive" / "Ars Magica Manager")
    _saga_folder(no_choice / "AppData" / "Ars Magica Manager")
    paths.keep_old_default_folder()
    _kept(newest)


def test_an_existing_app_data_default_records_nothing(no_choice):
    _saga_folder(no_choice / "OneDrive" / "Armarius")
    (no_choice / "AppData" / "Armarius").mkdir(parents=True)
    paths.keep_old_default_folder()
    assert paths.source() == "default"
    assert not paths.LOCATION_FILE.exists()
    assert paths.data_dir() == no_choice / "AppData" / "Armarius"


def test_a_chosen_folder_records_nothing(no_choice, monkeypatch):
    _saga_folder(no_choice / "OneDrive" / "Armarius")
    monkeypatch.setenv(paths.ENV_VAR, str(no_choice / "FromEnv"))
    paths.keep_old_default_folder()
    assert not paths.LOCATION_FILE.exists()
    assert paths.data_dir() == no_choice / "FromEnv"
    monkeypatch.delenv(paths.ENV_VAR)
    paths.remember_data_dir(no_choice / "Chosen")
    monkeypatch.setattr(paths, "_in_use", None)
    paths.keep_old_default_folder()
    assert paths.data_dir() == no_choice / "Chosen"


def test_onedrive_set_to_a_missing_folder_is_ignored(no_choice, monkeypatch):
    monkeypatch.setenv("OneDrive", str(no_choice / "missing"))  # not a folder
    assert paths.old_default_folders() == [no_choice / "AppData" / "Ars Magica Manager"]
    paths.keep_old_default_folder()
    assert paths.source() == "default"
    assert paths.data_dir() == no_choice / "AppData" / "Armarius"


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
    from ars_magica_manager.tui.app import ArsMagicaManagerApp

    app = ArsMagicaManagerApp()
    app.startup_notes = ("Moved sagas/a.json",)
    async with app.run_test():
        shown = [(n.title, n.message) for n in app._notifications]
    assert len(shown) == 1
    assert shown[0][0].startswith("Your data folder: ")
    assert shown[0][1] == "Moved sagas/a.json"


@pytest.fixture
def blocked(no_choice, monkeypatch):
    """The default app data folder can't be written to (as Controlled
    folder access does to Documents); every other folder can."""
    real = paths.writable
    blocked_folder = no_choice / "AppData" / "Armarius"
    monkeypatch.setattr(
        paths,
        "writable",
        lambda folder: folder != blocked_folder and real(folder),
    )
    yield no_choice
    monkeypatch.setattr(paths, "_fallback", None)


def test_an_unwritable_data_folder_falls_back_to_the_saves_in_the_repo(blocked):
    old = _legacy(blocked)
    problem = paths.settle_data_dir(old)
    assert paths.data_dir() == old
    assert problem is not None and "Controlled folder access" in problem
    assert str(old) in problem
    assert paths.move_legacy_data(old) == []  # nothing moves
    assert (old / "sagas" / "a.json").exists()


def test_with_no_saves_in_the_repo_it_falls_back_to_app_data(blocked):
    # The fallback is the app data folder, which is now the default too:
    # the app says it can't be used, and goes on with it.
    problem = paths.settle_data_dir(blocked / "empty_repo_data")
    assert paths.data_dir() == blocked / "AppData" / "Armarius"
    assert problem is not None


def test_a_writable_data_folder_needs_no_fallback(no_choice):
    assert paths.settle_data_dir(no_choice / "repo") is None
    assert paths.data_dir() == paths.default_data_dir()
    assert paths.default_data_dir().is_dir()
    assert list(paths.default_data_dir().iterdir()) == []  # the probe is gone


def test_a_file_that_cannot_move_is_left_in_place(tmp_path, monkeypatch):
    old, new = _legacy(tmp_path), tmp_path / "new"
    real_move = paths.shutil.move

    def move(source, target):
        if source.name == "a.json":
            raise PermissionError("in use")
        return real_move(source, target)

    monkeypatch.setattr(paths.shutil, "move", move)
    notes = paths.move_legacy_data(old, new)
    assert "Couldn't move sagas/a.json: in use" in notes
    assert "Moved app_settings.json" in notes
    assert (old / "sagas" / "a.json").exists()
