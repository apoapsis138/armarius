"""The desktop's written Handouts: Saga Content's Handouts chapter, its
table narrowed to one Story by the choice above it (handouts.py), and a
Handout drawn on its Stationery (gui/handout_page.py), as the Handout
form's Preview opens it."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_steps import assert_framed
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor, QFontMetricsF, QPixmap
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QLabel,
    QPushButton,
    QTableView,
    QWidget,
)

from ars_magica_manager import handout_layout as layout
from ars_magica_manager import handouts
from ars_magica_manager.commands import Form
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.forms import FieldsDialog, step_dialog
from ars_magica_manager.gui.handout_page import (
    PAGE_WIDTH,
    Banner,
    HandoutPage,
    HandoutWindow,
)
from ars_magica_manager.gui.saga_content import SagaContentPage
from ars_magica_manager.gui.style.illumination import IlluminatedInitial
from ars_magica_manager.gui.style.window_frame import Window
from ars_magica_manager.gui.themes import SCRIPTORUM, SCRIPTORUM_DARK, Palette
from ars_magica_manager.models import (
    PROCLAMATION,
    STATIONERY,
    STORY_EVENT,
    VELLUM,
    Covenant,
    CovenantDiaryEntry,
    Handout,
    Saga,
)


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert isinstance(application, QApplication)
    assert pictures.register_fonts() == []
    return application


def _saga() -> Saga:
    saga = Saga(id="handout-gui", name="Fengheld")
    saga.covenants = [Covenant(id="c", saga_id=saga.id, name="Fengheld")]
    saga.covenants[0].diary = [
        CovenantDiaryEntry(
            1220, name="The Black Tower", category=STORY_EVENT, status="Open", id="st1"
        )
    ]
    saga.handouts = [
        Handout("h1", title="Of nothing"),
        Handout("h2", title="Of the tower", story_id="st1"),
    ]
    return saga


def _titles(page: SagaContentPage) -> list[str]:
    """The Handouts table's titles (the table whose second column is the
    Stationery)."""
    found = []
    for view in page.findChildren(QTableView):
        model = view.model()
        if model.headerData(1, Qt.Orientation.Horizontal) != "Stationery":
            continue
        found += [model.index(row, 0).data() for row in range(model.rowCount())]
    return found


def test_the_story_choice_narrows_the_handouts_table(app: QApplication) -> None:
    saga = _saga()
    page = SagaContentPage(saga, SCRIPTORUM)
    page.codex.open_chapter("Handouts")
    assert _titles(page) == ["Of nothing", "Of the tower"]
    (choice,) = [
        c for c in page.findChildren(QComboBox) if c.itemText(0) == "Every story"
    ]
    try:
        choice.setCurrentIndex(choice.findData("st1"))
        assert handouts.current_story(saga) == "st1"
        assert _titles(page) == ["Of the tower"]
        choice.setCurrentIndex(0)
        assert _titles(page) == ["Of nothing", "Of the tower"]
    finally:
        handouts.choose_story(saga, "")


TEXT = (
    "[heading] A Proclamation\n"
    "[centre] By order of the Count\n"
    "[right] Given at Cologne\n"
    "[initial] Know all men that the ford is closed.\n"
    "\n"
    "Plain words, **bold** and *italic*.\n"
    "\n"
    "[flourish]\n"
    "[picture 1]\n"
    "[picture 2]"
)


@pytest.mark.parametrize("stationery", STATIONERY)
def test_each_stationery_draws_each_tag_s_block(
    app: QApplication, stationery: str
) -> None:
    picture = QPixmap(40, 30)
    picture.fill(QColor("navy"))
    laid = layout.lay_out("The ford", stationery, TEXT, ["Map", "Lost seal"])
    page = HandoutPage(laid, [picture, None])
    assert [type(w).__name__ for w in page.drawn] == [
        "QLabel",
        "QLabel",
        "QLabel",
        "QWidget",  # the illuminated initial beside its paragraph
        "QLabel",
        "ShortRule",
        "QLabel",  # the picture
        "_Placeholder",  # the one this computer hasn't got
    ]
    initial = page.findChild(IlluminatedInitial, "handout-initial")
    assert initial is not None and initial.letter == "K"
    assert page.drawn[6].pixmap().width() == 40
    assert page.drawn[7].text() == "Picture 2: Lost seal"
    assert page.height() >= PAGE_WIDTH * laid.stationery.aspect
    drawn = page.grab()
    assert not drawn.isNull() and drawn.width() == PAGE_WIDTH


def test_the_window_s_title_keeps_bracketed_words(app: QApplication) -> None:
    laid = layout.lay_out("Writ of the [Tower] Guard", VELLUM, "")
    assert (
        HandoutWindow(laid, SCRIPTORUM).windowTitle()
        == "Writ of the [Tower] Guard (Vellum)"
    )


@pytest.mark.parametrize(
    "palette", [SCRIPTORUM, SCRIPTORUM_DARK], ids=["light", "dark"]
)
def test_the_window_s_margin_is_the_theme_s_paper(
    app: QApplication, palette: Palette
) -> None:
    laid = layout.lay_out("The ford", VELLUM, "Words.")
    window = HandoutWindow(laid, palette)
    bare = Window("The ford (Vellum)", palette, None)
    window.show()
    bare.show()
    bare.resize(window.size())
    # What lies round and behind the Handout's page: only the window's paper.
    window.handout.hide()
    app.processEvents()
    where = QPoint(window.width() // 2, window.height() // 2)
    seen = window.grab().toImage().pixelColor(where)
    try:
        assert seen == bare.grab().toImage().pixelColor(where)
    finally:
        window.close()
        bare.close()


def test_a_title_that_looks_like_html_is_drawn_as_written(app: QApplication) -> None:
    for stationery in STATIONERY:
        page = HandoutPage(layout.lay_out("Letter <to the Abbot>", stationery, ""))
        title = page.findChild(QWidget, "handout-title")
        assert title is not None, stationery
        if isinstance(title, QLabel):
            assert title.textFormat() == Qt.TextFormat.PlainText, stationery
            assert "<to the Abbot>" in title.text(), stationery
        assert "&lt;to the Abbot&gt;" in title.toolTip() or not title.toolTip()


def test_a_long_handout_runs_the_page_on_and_keeps_every_line(
    app: QApplication,
) -> None:
    words = " ".join(["Know all men by these presents that the ford is closed."] * 60)
    page = HandoutPage(layout.lay_out("Long", VELLUM, f"{words}\n\nThe end."))
    page.resize(PAGE_WIDTH, page.minimumHeight())
    layout_ = page.layout()
    assert layout_ is not None
    layout_.setGeometry(page.rect())
    margin = layout_.contentsMargins().bottom()
    for block in page.drawn:
        assert block.height() >= block.heightForWidth(block.width())
    assert page.drawn[-1].geometry().bottom() <= page.height() - margin


def test_a_long_proclamation_title_wraps_inside_the_measure(
    app: QApplication,
) -> None:
    title = "By Order of His Grace the Archbishop of Cologne Concerning the Ford at Fengheld"
    page = HandoutPage(layout.lay_out(title, PROCLAMATION, ""))
    banner = page.findChild(Banner, "handout-title")
    assert isinstance(banner, Banner)
    lines = banner.lines
    assert len(lines) > 1
    assert " ".join(lines) == title
    metrics = QFontMetricsF(banner.font_)
    assert all(metrics.horizontalAdvance(line) <= page.measure for line in lines)


def _clicked(button: QPushButton) -> None:
    QTest.mouseClick(button, Qt.MouseButton.LeftButton)


def test_the_handout_form_s_preview_button_draws_it_unsaved(
    app: QApplication,
) -> None:
    """From Saga Content's Handouts: choose a Handout, click Edit, change
    its text and Stationery, click Preview. The window draws the form's
    values on their Stationery, and the Handout is unchanged."""
    saga = _saga()
    asked: list[QDialog] = []
    forms_opened: list[FieldsDialog] = []

    def ask(dialog: QDialog) -> int:
        asked.append(dialog)
        return QDialog.DialogCode.Rejected

    def run(command: object) -> None:
        assert isinstance(command, Form)
        dialog = step_dialog(command, SCRIPTORUM, None, ask=ask)
        assert isinstance(dialog, FieldsDialog)
        forms_opened.append(dialog)

    page = SagaContentPage(saga, SCRIPTORUM, run)
    page.codex.open_chapter("Handouts")
    (table,) = [
        v
        for v in page.findChildren(QTableView)
        if v.model().headerData(1, Qt.Orientation.Horizontal) == "Stationery"
    ]
    table.selectRow(1)
    (write,) = [
        b
        for b in page.findChildren(QPushButton)
        if b.text().strip() == "Write a Handout"
    ]
    row = write.parentWidget()
    assert row is not None
    (edit,) = [b for b in row.findChildren(QPushButton) if b.text().strip() == "Edit"]
    _clicked(edit)
    (form,) = forms_opened
    form.set_value("text", "[heading] Hear ye\n[initial] Let it be known.")
    form.set_value("stationery", PROCLAMATION)
    preview = form.findChild(QPushButton, "preview")
    assert preview is not None and preview.text() == "Preview"
    _clicked(preview)
    (window,) = asked
    assert isinstance(window, HandoutWindow)
    assert_framed(window)
    shown = window.handout.laid
    assert shown.title == "Of the tower"
    assert shown.stationery.name == PROCLAMATION
    assert [b.kind for b in shown.blocks] == ["heading", "initial"]
    assert window.windowTitle() == "Of the tower (A proclamation)"
    assert (saga.handouts[1].text, saga.handouts[1].stationery) == ("", "vellum")
