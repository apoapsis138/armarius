"""The desktop's Read in full: a long Virtue's inspector shows its summary
and a Read in full button under it, which opens the whole entry on vellum
in the window a shown Handout opens in; a short one has no button. The Add
Virtue picker has the button under its preview, on for a long entry."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QPushButton

from ars_magica_manager import commands
from ars_magica_manager.forms import virtue as virtue_forms
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.forms import ChooseDialog, step_dialog
from ars_magica_manager.gui.handout_page import HandoutWindow
from ars_magica_manager.gui.themes import SCRIPTORUM
from ars_magica_manager.gui.widgets import ClickableCard
from ars_magica_manager.models import Character, Saga, VirtueFlawInstance

LONG_VF = "vf_verditius_elder_runes"
SHORT_VF = "vf_ablating"


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert isinstance(application, QApplication)
    assert pictures.register_fonts() == []
    return application


def _sheet(vf_id: str, ran: list[commands.Command]) -> CharacterSheet:
    magus = Character(
        id="m",
        name="Magus",
        type="magus",
        virtues_flaws=[VirtueFlawInstance(vf_id=vf_id)],
    )
    saga = Saga(id="s", name="Saga", characters=[magus])
    sheet = CharacterSheet(saga, magus, SCRIPTORUM, run=ran.append)
    sheet.open_chapter("Virtues & Flaws")
    return sheet


def _choose_card(sheet: CharacterSheet, name: str) -> None:
    for card in sheet.findChildren(ClickableCard):
        if name in " ".join(
            label.text() for label in card.findChildren(type(sheet.inspector.title))
        ):
            assert card.clicked is not None
            card.clicked()
            return
    raise AssertionError(f"no card for {name}")


def _read_button(sheet: CharacterSheet) -> list[QPushButton]:
    return [
        b
        for b in sheet.inspector.findChildren(QPushButton)
        if b.text().strip() == "Read in full"
    ]


@pytest.mark.usefixtures("app")
def test_a_long_virtues_inspector_opens_it_in_full_on_vellum() -> None:
    ran: list[commands.Command] = []
    sheet = _sheet(LONG_VF, ran)
    _choose_card(sheet, "Verditius Elder Runes")
    [button] = _read_button(sheet)

    button.click()

    [form] = ran
    assert isinstance(form, commands.Form)
    window = step_dialog(form, SCRIPTORUM, None)
    assert isinstance(window, HandoutWindow)
    assert window.page.laid.title == "Verditius Elder Runes"
    assert window.windowTitle() == "Verditius Elder Runes (Minor Virtue)"
    window.close()


@pytest.mark.usefixtures("app")
def test_a_short_virtues_inspector_has_no_read_in_full() -> None:
    sheet = _sheet(SHORT_VF, [])
    _choose_card(sheet, "Ablating")

    assert _read_button(sheet) == []


def _add_virtue_dialog() -> ChooseDialog:
    magus = Character(id="m", name="Magus", type="magus")
    saga = Saga(id="s", name="Saga", characters=[magus])
    ops = virtue_forms.virtue_flaw_ops(saga, magus, "Virtue")
    assert ops.add is not None
    step = ops.add()
    assert isinstance(step, commands.Choose)
    dialog = step_dialog(step, SCRIPTORUM, None)
    assert isinstance(dialog, ChooseDialog)
    return dialog


@pytest.mark.usefixtures("app")
def test_the_pickers_read_in_full_opens_a_long_entry_and_keeps_the_picker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    opened: list[HandoutWindow] = []
    monkeypatch.setattr(HandoutWindow, "exec", lambda self: opened.append(self) or 0)
    dialog = _add_virtue_dialog()
    dialog.search.setText("Elder Runes")

    assert dialog.read_button.isEnabled()
    dialog.read_button.click()

    [window] = opened
    assert window.page.laid.title == "Verditius Elder Runes"
    assert dialog.search.text() == "Elder Runes" and not dialog.result()
    dialog.close()


@pytest.mark.usefixtures("app")
def test_the_pickers_read_in_full_is_off_on_a_short_entry() -> None:
    dialog = _add_virtue_dialog()
    dialog.search.setText("Ablating")

    assert not dialog.read_button.isEnabled()
    dialog.close()
