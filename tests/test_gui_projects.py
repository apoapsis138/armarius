"""The desktop covenant's Projects chapter (Hermetic Projects): shown only
once a project is begun (Begin Project, on the Attributes chapter), after
Manors; the tower's facts, its works and craft devices as ledger
entries, and Stress Check and Conjure Levels as the tower's buttons
(answered without showing the dialogs, gui_steps.answering)."""

from __future__ import annotations

import html
import os
import re

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, section_buttons
from PySide6.QtWidgets import QApplication, QLabel
from test_hermetic_projects import tower_saga

from ars_magica_manager import storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.covenant import CovenantPage
from ars_magica_manager.gui.forms import FieldsDialog
from ars_magica_manager.gui.window import MainWindow


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _window(with_project: bool = True) -> tuple[MainWindow, str]:
    saga = tower_saga()
    if not with_project:
        saga.covenants[0].hermetic_projects = []
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.open_covenant("dam")
    return window, saga.id


def _page(window: MainWindow, chapter: str) -> CovenantPage:
    page = window.page()
    assert isinstance(page, CovenantPage)
    page.codex.open_chapter(chapter)
    return page


def _words(widget) -> str:
    return "\n".join(
        html.unescape(re.sub(r"<[^>]+>", "", label.text()))
        for label in widget.findChildren(QLabel)
    )


def test_the_chapter_shows_once_a_project_is_begun(app):
    window, saga_id = _window(with_project=False)
    page = _page(window, "Attributes")
    assert "Projects" not in page.chapters()
    asked = answering(window, {"name": "The Spire"})
    section_buttons(page, "The Covenant")["Begin Project"].click()
    assert [type(d) for d in asked] == [FieldsDialog]
    assert [
        p.name for p in storage.load_saga(saga_id).covenants[0].hermetic_projects
    ] == ["The Spire"]
    chapters = window.page().chapters()
    assert chapters.index("Projects") == chapters.index("Manors") + 1


def test_the_tower_its_works_and_devices(app):
    window, _ = _window()
    page = _page(window, "Projects")
    chapter = page.codex.chapter(page.codex.chapters().index("Projects"))
    words = _words(chapter)
    assert "Hermetic Projects (1)" in words
    assert "280 ft (14 levels)" in words
    assert "Works (3)" in words and "Craft Devices (+2, at most +6)" in words
    buttons = section_buttons(page, "The Schattenbach Spire: Great Tower")
    assert list(buttons) == ["Edit Project", "Stress Check", "Conjure Levels"]


def test_a_stress_check_from_the_desktop_is_kept_in_the_works(app):
    window, saga_id = _window()
    page = _page(window, "Projects")
    asked = answering(window, {"severity": -1})
    section_buttons(page, "The Schattenbach Spire: Great Tower")["Stress Check"].click()
    assert [type(d) for d in asked] == [FieldsDialog]
    project = storage.load_saga(saga_id).covenants[0].hermetic_projects[0]
    assert project.works[-1].kind == "stress"
