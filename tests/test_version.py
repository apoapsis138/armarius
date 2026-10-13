"""The app's version: one source (pyproject.toml), shown in the app and
recorded in every save."""

import json
import re
import tomllib

from support import screen_lines
from textual.widgets import Static

from ars_magica_manager import ROOT, __version__, storage
from ars_magica_manager.models import Saga
from ars_magica_manager.tui.app import ArsMagicaManagerApp


def test_the_version_comes_from_pyproject_and_is_major_minor_patch():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert __version__ == pyproject["project"]["version"]
    assert re.fullmatch(r"\d+\.\d+\.\d+", __version__)


def test_the_changelog_has_an_entry_for_this_version():
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## {__version__} " in changelog


def test_a_save_records_the_version_that_wrote_it():
    path = storage.save_saga(Saga(id="s", name="S"))
    assert json.loads(path.read_text(encoding="utf-8"))["app_version"] == __version__
    assert storage.load_saga("s").app_version == __version__


async def test_the_version_is_shown_in_the_header_and_on_the_saga_picker():
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.pause()
        assert app.title == f"Armarius v{__version__}"
        line = app.screen.query_one("#picker-version", Static)
        assert __version__ in str(line.render())
        assert line.region.height == 1 and line.region.bottom <= 44

        # The workspace's header keeps it, next to the saga and its date.
        storage.save_saga(Saga(id="s", name="S"))
        await app.screen.refresh_list()
        await pilot.press("enter")
        await pilot.pause()
        header = screen_lines(app)[0]
        assert f"Armarius v{__version__} — S | Spring 1220" in header
