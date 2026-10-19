"""Set Up Research Library: the covenant library's research bonuses, a
subject at a time, each step showing the books that back it and the
bonuses chosen so far; nothing changes until the last step."""

from __future__ import annotations

import os

import pytest
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import books as bk
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import library as library_forms


def _empty_library():
    saga = _sample_saga_with_covenant()
    saga.books = []
    return saga, saga.covenants[0]


def _library():
    saga, covenant = _empty_library()
    for name, kind, subject, level, quality in (
        ("Flames Unbound", "Art Summa", "Ignem", 12, 10),
        ("On Fire's Nature", "Tractatus", "Ignem", None, 8),
        ("The Wide World", "Ability Summa", "Area Lore: Iberia", 4, 9),
    ):
        book = bk.add_book(saga, name, kind)
        book.owner_kind, book.owner_id = "covenant", covenant.id
        book.quality, book.level = quality, level
        if kind == "Tractatus":
            book.subject_kind, book.art = "Art", subject
        elif kind == "Art Summa":
            book.art = subject
        else:
            book.ability = subject
    return saga, covenant


def _values(form: Form, **chosen):
    return {f.key: chosen.get(f.key, f.value) for f in form.fields()}


def _info(form: Form, key: str) -> str:
    return str(next(f.value for f in form.fields() if f.key == key))


def test_each_subject_is_a_step_showing_its_books_and_the_bonuses_so_far():
    saga, covenant = _library()
    first = library_forms.research_walkthrough(saga, covenant)
    assert isinstance(first, Form)
    assert first.title == "Research Library (1 of 2): Ignem"
    assert first.save_label == "Next"
    books = _info(first, "_books")
    assert "Flames Unbound · Art Summa · Level 12 · Quality 10" in books
    assert "On Fire's Nature" in books
    assert first.live is not None
    assert first.live(_values(first, level="2", pictorial=True)).endswith("+3[/]")
    second = first.apply(_values(first, level="2", pictorial=True))
    assert isinstance(second, Form)
    assert second.title.startswith("Research Library (2 of 2)")
    assert second.save_label == "Finish"
    assert _info(second, "_so_far") == "Ignem +3"
    # Nothing is saved before the last step.
    assert covenant.library_research == {}
    assert second.apply(_values(second, level="1")) is None
    assert covenant.library_research == {"Ignem": 2, "Area Lore: Iberia": 1}
    assert covenant.pictorial_works == ["Ignem"]


def test_a_library_without_summae_or_tractatus_is_refused():
    found = library_forms.research_walkthrough(*_empty_library())
    assert isinstance(found, Refuse)


def test_the_desktop_library_button_walks_the_subjects(tmp_path):
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from gui_steps import answering, section_buttons
    from PySide6.QtWidgets import QApplication

    from ars_magica_manager import sourcebooks, storage
    from ars_magica_manager.gui.window import MainWindow

    QApplication.instance() or QApplication([])
    saga, covenant = _library()
    if not sourcebooks.in_play("Covenants", sourcebooks.saga_books(saga)):
        pytest.skip("the sample saga leaves Covenants out of play")
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.open_covenant(covenant.id)
    window.page().codex.open_chapter("Library")
    asked = answering(window, {"level": "3"}, {"level": "1", "pictorial": True})
    section_buttons(window.page(), "Library")["Set Up Research Library"].click()
    assert asked[0].windowTitle().startswith("Research Library (1 of 2)")
    saved = storage.load_saga(saga.id).covenants[0]
    assert saved.library_research == {"Ignem": 3, "Area Lore: Iberia": 1}
    assert saved.pictorial_works == ["Area Lore: Iberia"]
