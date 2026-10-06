"""Where the user's data is kept, and moving it out of the repo."""

import json

import pytest

from ars_magica_manager import paths


@pytest.fixture
def no_choice(tmp_path, monkeypatch):
    """No environment variable and no location file: the default, with
    OneDrive at tmp_path/OneDrive (as on Windows)."""
    monkeypatch.delenv(paths.ENV_VAR, raising=False)
    for var in paths.ONEDRIVE_VARS:
        monkeypatch.delenv(var, raising=False)
    (tmp_path / "OneDrive").mkdir()
    monkeypatch.setenv("OneDrive", str(tmp_path / "OneDrive"))
    monkeypatch.setattr(paths, "LOCATION_FILE", tmp_path / "config" / "location.json")
    monkeypatch.setattr(
        paths.platformdirs, "user_data_dir", lambda *a, **k: str(tmp_path / "AppData")
    )
    return tmp_path


def test_the_data_folder_defaults_to_the_top_of_onedrive(no_choice):
    assert paths.data_dir() == no_choice / "OneDrive" / "Ars Magica Manager"


def test_onedrive_is_found_wherever_it_is(no_choice, monkeypatch):
    # OneDrive can be at D:\OneDrive, for one.
    (no_choice / "D" / "OneDrive").mkdir(parents=True)
    monkeypatch.delenv("OneDrive")
    monkeypatch.setenv("OneDriveConsumer", str(no_choice / "D" / "OneDrive"))
    assert paths.data_dir() == no_choice / "D" / "OneDrive" / "Ars Magica Manager"


def test_without_onedrive_the_data_folder_is_the_app_data_folder(
    no_choice, monkeypatch
):
    monkeypatch.delenv("OneDrive")
    assert paths.data_dir() == no_choice / "AppData"
    monkeypatch.setenv("OneDrive", str(no_choice / "missing"))  # not a folder
    assert paths.data_dir() == no_choice / "AppData"


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
    assert shown[0][0].startswith("Your data folder: ")
    assert shown[0][1] == "Moved sagas/a.json"


@pytest.fixture
def blocked(no_choice, monkeypatch):
    """The OneDrive folder can't be written to (as Controlled folder access
    does to Documents); every other folder can."""
    real = paths.writable
    monkeypatch.setattr(
        paths,
        "writable",
        lambda folder: "OneDrive" not in folder.parts and real(folder),
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
    problem = paths.settle_data_dir(blocked / "empty_repo_data")
    assert paths.data_dir() == blocked / "AppData"
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
