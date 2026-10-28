"""The desktop covenant's Attributes and Charter chapters: the charter's
seals, its clauses under their sections, the chosen clause in the
inspector, and Break a Clause greyed out on a broken one (answered without
showing the dialogs, gui_steps.answering)."""

from __future__ import annotations

import html
import os
import re

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import answering, section_buttons
from PySide6.QtWidgets import QApplication, QLabel
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.charter import ClauseEntry, SealCell
from ars_magica_manager.gui.covenant import CovenantPage
from ars_magica_manager.gui.forms import FieldsDialog
from ars_magica_manager.gui.markup_html import plain
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import (
    CLAUSE_BROKEN,
    Character,
    CharterClause,
    CharterSeal,
)


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _window() -> tuple[MainWindow, str]:
    saga = _sample_saga_with_covenant()
    saga.characters.append(
        Character(id="oda", name="Brother Oda", type="magus", covenant_id="cov1")
    )
    charter = saga.covenants[0].charter_of_covenant
    charter.name = "The Keep's Accord"
    charter.preamble = "We swear to hold the Keep together."
    charter.clauses = [
        CharterClause("1", "All vis is shared.", 1200, "Spring", "Member Rights"),
        CharterClause(
            "2",
            "Nothing goes to the Tribunal.",
            1200,
            "Spring",
            "Oath of Covenant",
            status=CLAUSE_BROKEN,
            since_year=1210,
            note="Letters to Durenmar.",
        ),
    ]
    charter.seals = [CharterSeal("char1", 1200, "Spring")]
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.open_covenant("cov1")
    return window, saga.id


def _page(window: MainWindow) -> CovenantPage:
    page = window.page()
    assert isinstance(page, CovenantPage)
    page.codex.open_chapter("Charter")
    return page


def _chapter(page: CovenantPage, name: str):
    return page.codex.chapter(page.codex.chapters().index(name))


def _words(widget) -> str:
    """Every label's words under `widget`, tags left out."""
    return "\n".join(
        html.unescape(re.sub(r"<[^>]+>", "", label.text()))
        for label in widget.findChildren(QLabel)
    )


def test_attributes_comes_first_and_the_charter_after_it(app):
    window, _ = _window()
    page = _page(window)
    assert page.codex.chapters()[:3] == ["Attributes", "Charter", "People"]
    assert "Boons" in _words(_chapter(page, "Attributes"))
    assert "Clauses" not in _words(_chapter(page, "Attributes"))


def test_the_charter_shows_its_seals_preamble_and_clauses(app):
    window, _ = _window()
    page = _page(window)
    chapter = _chapter(page, "Charter")
    seals = chapter.findChildren(SealCell)
    assert [(s.shown.character.id, s.shown.seal is not None) for s in seals] == [
        ("char1", True),
        ("oda", False),
    ]
    words = _words(chapter)
    assert "The Keep's Accord" in words
    assert "Clauses (1 in force of 2)" in words
    # Grouped by section, in the book's order: the Oath before Member Rights.
    assert words.index("Oath of Covenant") < words.index("Member Rights")
    assert "Broken, 1210: Letters to Durenmar." in words


def test_a_chosen_clause_shows_in_the_inspector_and_break_follows_it(app):
    window, _ = _window()
    page = _page(window)
    entries = _chapter(page, "Charter").findChildren(ClauseEntry)
    buttons = section_buttons(page, "Clauses")
    assert list(buttons) == [
        "Add",
        "Edit",
        "Delete",
        "Break a Clause",
        "Censure",
        "Charge at Tribunal",
    ]
    entries[0].clicked()  # the Oath's clause, broken
    assert page.inspector.title.text() == "Clause 2"
    assert "Covenants p. 35" in plain(page.inspector.body.text())
    assert not buttons["Break a Clause"].isEnabled()
    assert buttons["Censure"].isEnabled()
    # Not notarized, and its Tribunal makes no sworn charter law.
    assert not buttons["Charge at Tribunal"].isEnabled()
    entries[1].clicked()
    assert page.inspector.title.text() == "Clause 1"
    assert buttons["Break a Clause"].isEnabled()
    assert not buttons["Censure"].isEnabled()


def test_break_a_clause_and_seal_the_charter(app):
    window, saga_id = _window()
    page = _page(window)
    _chapter(page, "Charter").findChildren(ClauseEntry)[1].clicked()
    asked = answering(window, {"note": "Leandro kept the Vim vis."})
    section_buttons(page, "Clauses")["Break a Clause"].click()
    assert [type(d) for d in asked] == [FieldsDialog]
    clause = storage.load_saga(saga_id).covenants[0].charter_of_covenant.clauses[0]
    assert (clause.status, clause.note) == (CLAUSE_BROKEN, "Leandro kept the Vim vis.")
    page = _page(window)
    asked = answering(window, {"sealed_oda": True, "year_oda": 1215})
    section_buttons(page, "The Keep's Accord")["Seal the Charter"].click()
    seals = storage.load_saga(saga_id).covenants[0].charter_of_covenant.seals
    assert [(s.character_id, s.year) for s in seals] == [
        ("char1", 1200),
        ("oda", 1215),
    ]


def test_use_a_template_draws_the_charter_of_arae_flaviae(app):
    window, saga_id = _window()
    page = _page(window)
    buttons = section_buttons(page, "The Keep's Accord")
    assert "Use a Template" in buttons and "Save as Template" in buttons
    # The saga keeps none of its own yet, and no one is expelled.
    assert "Forget a Template" not in buttons and "End Membership" not in buttons
    answering(window, {"template": "arae_flaviae"})
    buttons["Use a Template"].click()
    charter = storage.load_saga(saga_id).covenants[0].charter_of_covenant
    assert charter.template == "arae_flaviae" and len(charter.clauses) == 25
    assert "At once: The Charter of Arae Flaviae, unaltered" in _words(
        _chapter(_page(window), "Charter")
    )
