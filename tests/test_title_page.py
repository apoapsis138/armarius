"""The title page the app opens on: what it offers (title_page.py), and
the terminal's title screen in front of the saga picker."""

from __future__ import annotations

from support import everything_saga, screen_lines, wait_until

from ars_magica_manager import __version__, settings, storage
from ars_magica_manager import title_page as tp
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import WorkspaceScreen
from ars_magica_manager.tui.screens.fields import FieldsDialog
from ars_magica_manager.tui.screens.help import HelpScreen
from ars_magica_manager.tui.screens.saga_picker import SagaPickerScreen
from ars_magica_manager.tui.screens.title import TitleScreen, banner

CHANGELOG = """# Changelog

## Features

| Feature | What it is |
| --- | --- |
| Illuminatio | The desktop version |

## Editions

| Edition | Title | Finished in | What it brought |
| --- | --- | --- | --- |
| Illuminatio I | The desktop | 2.52.0 | The desktop |
| Illuminatio II | Prima Littera | 2.53.0 | The title page |

## Major versions

| Major | Name | What it marked |
| --- | --- | --- |
| 2 | Rego | creation by the book |

## Milestones

| Milestone | Version | What it marked |
| --- | --- | --- |

## 2.53.1 — 2026-10-20

### Illuminatio

- A fix.

## 2.53.0 — 2026-10-19

### Illuminatio

- The title page.

## 2.52.0 — 2026-10-13

### Illuminatio

- The desktop.
"""


def _keys(page: tp.TitlePage) -> list[str]:
    return [choice.key for choice in page.choices]


def test_the_release_name_is_the_major_versions_name(monkeypatch):
    # The sample changelog's versions are 2.x: name this one of them.
    monkeypatch.setattr(tp, "__version__", "2.53.1")
    assert tp.release_name(CHANGELOG) == "Rego"
    assert tp.release_name("# Changelog\n\n## 1.0.0 — 2026-09-29\n") == ""


def test_the_page_names_the_app_its_version_and_release():
    page = tp.title_page([])
    assert (page.name, page.tagline) == ("Armarius", "A saga manager for Ars Magica")
    assert page.edition.startswith(f"Version {__version__} · ")
    assert page.edition.endswith("for Ars Magica Fifth Edition")


def test_with_no_sagas_it_offers_to_begin_one():
    page = tp.title_page([])
    assert _keys(page) == [tp.SAGAS, tp.NEW, tp.HELP]
    assert page.choices[0].detail == "None saved yet"
    assert page.choices[1].label == "New Saga"
    assert page.saga_id is None


def test_a_front_end_that_joins_offers_join_a_saga_in_new_sagas_place():
    page = tp.title_page([], joining=True)
    assert _keys(page) == [tp.SAGAS, tp.JOIN, tp.HELP]
    assert page.choices[1].label == "Join a Saga"


def test_open_saga_opens_the_saga_opened_last():
    first, second = everything_saga(), everything_saga()
    second.id, second.name = "second", "The Second Saga"
    storage.save_saga(first)
    storage.save_saga(second)
    ids = storage.list_sagas()
    assert tp.title_page(ids).saga_id is None  # two sagas, none opened yet
    tp.remember_saga("second")
    page = tp.title_page(ids)
    assert _keys(page) == [tp.OPEN, tp.SAGAS, tp.NEW, tp.HELP]
    assert page.saga_id == "second"
    assert page.choices[0].detail == "The Second Saga"


def test_the_only_saga_is_offered_and_a_deleted_one_is_not():
    saga = everything_saga()
    storage.save_saga(saga)
    assert tp.title_page([saga.id]).saga_id == saga.id
    settings.update_settings(last_saga="gone")
    assert tp.title_page([saga.id]).saga_id == saga.id
    assert tp.title_page([]).saga_id is None


def test_banner_spells_the_name_in_four_rows():
    rows = banner("Armarius").splitlines()
    assert len(rows) == 4
    assert len({len(row) for row in rows}) == 1


async def test_the_terminal_opens_on_the_title_page_and_goes_on_to_the_picker():
    app = ArsMagicaManagerApp()
    app.show_title = True
    async with app.run_test(size=(120, 45)) as pilot:
        assert await wait_until(pilot, lambda: isinstance(app.screen, TitleScreen))
        text = "\n".join(screen_lines(app))
        assert "A saga manager for Ars Magica" in text
        assert "All Sagas" in text and "Open Saga" not in text
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: isinstance(app.screen, SagaPickerScreen))


async def test_enter_on_the_title_page_opens_the_saga_opened_last():
    saga = everything_saga()
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    app.show_title = True
    async with app.run_test(size=(120, 45)) as pilot:
        assert await wait_until(pilot, lambda: isinstance(app.screen, TitleScreen))
        assert saga.name in "\n".join(screen_lines(app))
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
    assert settings.load_settings()[tp.LAST_SAGA] == saga.id


async def test_help_from_the_title_page():
    app = ArsMagicaManagerApp()
    app.show_title = True
    async with app.run_test(size=(120, 45)) as pilot:
        assert await wait_until(pilot, lambda: isinstance(app.screen, TitleScreen))
        await pilot.press("question_mark")
        assert await wait_until(pilot, lambda: isinstance(app.screen, HelpScreen))
        assert await wait_until(pilot, lambda: app.screen.topic_id == "title-page")


async def test_the_title_pages_help_choice_opens_help_over_the_picker():
    app = ArsMagicaManagerApp()
    app.show_title = True
    async with app.run_test(size=(120, 45)) as pilot:
        assert await wait_until(pilot, lambda: isinstance(app.screen, TitleScreen))
        await pilot.press("down", "down", "enter")  # All Sagas, New Saga, Help
        assert await wait_until(pilot, lambda: isinstance(app.screen, HelpScreen))
        assert isinstance(app.screen_stack[-2], SagaPickerScreen)


async def test_the_title_pages_new_saga_opens_the_new_saga_form_over_the_picker():
    app = ArsMagicaManagerApp()
    app.show_title = True
    async with app.run_test(size=(120, 45)) as pilot:
        assert await wait_until(pilot, lambda: isinstance(app.screen, TitleScreen))
        await pilot.press("down", "enter")  # All Sagas, then New Saga
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        assert "Create a New Saga" in "\n".join(screen_lines(app))
        assert isinstance(app.screen_stack[-2], SagaPickerScreen)
        await pilot.press("escape")
        assert await wait_until(pilot, lambda: isinstance(app.screen, SagaPickerScreen))
