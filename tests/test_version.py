"""The app's version: one source (pyproject.toml), shown in the app and
recorded in every save."""

import json
import re
import tomllib

from textual.widgets import Static

from ars_magica_manager import ROOT, __version__, storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import Saga


def test_the_version_comes_from_pyproject_and_is_0_minor_patch():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert __version__ == pyproject["project"]["version"]
    assert re.fullmatch(r"0\.\d+\.\d+", __version__)


def test_the_changelog_has_an_entry_for_this_version():
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## {__version__} " in changelog


def test_a_save_records_the_version_that_wrote_it():
    path = storage.save_saga(Saga(id="s", name="S"))
    assert json.loads(path.read_text(encoding="utf-8"))["app_version"] == __version__
    assert storage.load_saga("s").app_version == __version__


def test_a_save_from_before_versioning_still_loads():
    path = storage.save_saga(Saga(id="s", name="S"))
    data = json.loads(path.read_text(encoding="utf-8"))
    del data["app_version"]
    path.write_text(json.dumps(data), encoding="utf-8")
    assert storage.load_saga("s").app_version == ""


async def test_the_version_is_shown_in_the_header_and_on_the_saga_picker():
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        assert app.title == f"Ars Magica Manager v{__version__}"
        line = app.screen.query_one("#picker-version", Static)
        assert __version__ in str(line.render())
        assert line.region.height == 1 and line.region.bottom <= 23

        # The workspace's header keeps it, next to the saga and its date.
        storage.save_saga(Saga(id="s", name="S"))
        await app.screen.refresh_list()
        await pilot.press("enter")
        await pilot.pause()
        header = " ".join(s.text for s in app.screen._compositor.render_strips()[:1])
        assert f"Ars Magica Manager v{__version__} — S | Spring 1220" in header
