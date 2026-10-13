"""Choosing where the saves are kept, from the saga picker."""

import json

from support import screen_lines, strip_markup, wait_until
from textual.widgets import Button, Checkbox, Static

from ars_magica_manager import paths, settings, storage
from ars_magica_manager.models import Saga
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import SagaPickerScreen
from ars_magica_manager.tui.screens.fields import FieldsDialog


def _user_data(folder):
    """A saga, its backup, an export, the settings and a presence mark in
    `folder`."""
    storage.use_data_dir(folder)
    storage.save_saga(Saga(id="mythic", name="Mythic", current_year=1220))
    (folder / paths.SAGAS / "backups" / "mythic").mkdir(parents=True)
    (folder / paths.SAGAS / "backups" / "mythic" / "1.json").write_text("{}")
    (folder / paths.EXPORTS).mkdir()
    (folder / paths.EXPORTS / "magus.json").write_text("{}")
    settings.update_settings(theme="scriptorum")
    (folder / paths.SAGAS / ".presence").mkdir()
    (folder / paths.SAGAS / ".presence" / "x").write_text("")


def test_moving_the_saves_never_overwrites_and_leaves_hidden_files(tmp_path):
    old, new = tmp_path / "old", tmp_path / "new"
    _user_data(old)
    (new / paths.EXPORTS).mkdir(parents=True)
    (new / paths.EXPORTS / "magus.json").write_text("theirs")
    notes = paths.move_user_data(old, new)
    assert (new / paths.SAGAS / "mythic.json").is_file()
    assert (new / paths.SAGAS / "backups" / "mythic" / "1.json").is_file()
    assert (new / paths.SETTINGS).is_file()
    assert (new / paths.EXPORTS / "magus.json").read_text() == "theirs"
    assert (old / paths.EXPORTS / "magus.json").is_file()
    assert (old / paths.SAGAS / ".presence" / "x").is_file()
    assert any(note.startswith("Left exports/magus.json") for note in notes)


def test_a_chosen_folder_is_remembered(tmp_path):
    assert paths.source() == "default"
    paths.remember_data_dir(tmp_path / "chosen")
    assert json.loads(paths.LOCATION_FILE.read_text()) == {
        "data_dir": str(tmp_path / "chosen")
    }
    assert (paths.data_dir(), paths.source()) == (tmp_path / "chosen", "chosen")


async def _open_form(pilot, app) -> FieldsDialog:
    await pilot.press("m")
    await pilot.press("f")
    assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
    return app.screen  # type: ignore[return-value]


async def _save(pilot, dialog, folder) -> None:
    dialog._picked["folder"] = folder
    next(b for b in dialog.query(Button) if b.id == "btn-save").press()
    await pilot.pause()


async def test_the_picker_moves_the_saves_and_reads_the_new_folder(tmp_path):
    old, new = paths.data_dir(), tmp_path / "Elsewhere"
    _user_data(old)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.pause()
        folder_line = app.screen.query_one("#picker-folder", Static)
        assert f"Save folder: {old} (the default)" in strip_markup(
            str(folder_line.render())
        )
        dialog = await _open_form(pilot, app)
        text = "\n".join(screen_lines(app))
        assert "Controlled folder access" in text
        # Not a folder the app can save in: a file stands in the way.
        (tmp_path / "blocker").write_text("")
        await _save(pilot, dialog, tmp_path / "blocker" / "saves")
        assert app.screen is dialog
        assert "can't save in" in "\n".join(screen_lines(app))
        await _save(pilot, dialog, new)
        assert await wait_until(pilot, lambda: isinstance(app.screen, SagaPickerScreen))
        assert await wait_until(
            pilot, lambda: "(chosen in the app)" in str(folder_line.render())
        )
        assert "Mythic" in "\n".join(screen_lines(app))
    assert (new / paths.SAGAS / "mythic.json").is_file()
    assert not (old / paths.SAGAS / "mythic.json").exists()
    assert paths.data_dir() == new
    assert storage.SAGAS_DIR == new / paths.SAGAS
    assert settings.SETTINGS_PATH == new / paths.SETTINGS


async def test_the_folder_can_change_without_moving_the_saves(tmp_path):
    old, new = paths.data_dir(), tmp_path / "Empty"
    _user_data(old)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        dialog = await _open_form(pilot, app)
        dialog.query_one(Checkbox).value = False
        await _save(pilot, dialog, new)
        assert await wait_until(
            pilot, lambda: "No sagas yet" in "\n".join(screen_lines(app))
        )
    assert (old / paths.SAGAS / "mythic.json").is_file()


async def test_a_folder_set_by_the_environment_isnt_changed_here(tmp_path, monkeypatch):
    monkeypatch.setenv(paths.ENV_VAR, str(tmp_path / "FromEnv"))
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.pause()
        assert "ARMARIUS_DATA" in str(
            app.screen.query_one("#picker-folder", Static).render()
        )
        await pilot.press("m")
        await pilot.press("f")
        await pilot.pause()
        assert isinstance(app.screen, SagaPickerScreen)
