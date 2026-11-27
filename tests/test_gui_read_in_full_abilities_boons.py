"""The desktop's Read in full on long Abilities and Boons and Hooks: the
inspector's button under a long one's summary opens it on vellum, a short
one has none, and the Add Ability and Add Boon pickers have the button
under their preview, on for a long entry."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QPushButton, QWidget

from ars_magica_manager import catalog, commands
from ars_magica_manager.forms import covenant as covenant_forms
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.covenant import CovenantPage
from ars_magica_manager.gui.forms import ChooseDialog, step_dialog
from ars_magica_manager.gui.handout_page import HandoutWindow
from ars_magica_manager.gui.themes import SCRIPTORUM
from ars_magica_manager.gui.widgets import ClickableCard
from ars_magica_manager.models import (
    Ability,
    Character,
    Covenant,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.section_verbs import ABILITIES_SECTION, ops_of

LONG_ABILITY = "ab_hex"
SHORT_ABILITY = "ab_athletics"
LONG_BOON = "covbh_boon_minor_chase"
SHORT_BOON = "covbh_boon_minor_wealth"
LONG_HOOK = "covbh_hook_minor_infants"


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert isinstance(application, QApplication)
    assert pictures.register_fonts() == []
    return application


def _read_buttons(inspector: QWidget) -> list[QPushButton]:
    return [
        b
        for b in inspector.findChildren(QPushButton)
        if b.text().strip() == "Read in full"
    ]


def _opened(form: commands.Command) -> HandoutWindow:
    assert isinstance(form, commands.Form)
    window = step_dialog(form, SCRIPTORUM, None)
    assert isinstance(window, HandoutWindow)
    return window


def _ability(ability_id: str) -> Ability:
    entry = catalog.load_ability_catalog_by_id()[ability_id]
    return Ability(name=entry.name, category=entry.category, xp=5)


def _sheet(ran: list[commands.Command]) -> CharacterSheet:
    witch = Character(
        id="m",
        name="Agnes",
        type="companion",
        abilities=[_ability(SHORT_ABILITY), _ability(LONG_ABILITY)],
    )
    saga = Saga(id="s", name="Saga", characters=[witch])
    sheet = CharacterSheet(saga, witch, SCRIPTORUM, run=ran.append)
    sheet.open_chapter("Abilities")
    return sheet


@pytest.mark.usefixtures("app")
def test_a_long_abilitys_inspector_opens_it_in_full() -> None:
    ran: list[commands.Command] = []
    sheet = _sheet(ran)
    sheet.ability_table.on_choose(1)
    [button] = _read_buttons(sheet.inspector)

    button.click()

    [form] = ran
    window = _opened(form)
    assert window.page.laid.title == "Hex"
    window.close()


@pytest.mark.usefixtures("app")
def test_a_short_abilitys_inspector_has_no_read_in_full() -> None:
    sheet = _sheet([])
    sheet.ability_table.on_choose(0)

    assert _read_buttons(sheet.inspector) == []


def _covenant_page(ran: list[commands.Command]) -> CovenantPage:
    covenant = Covenant(id="c", saga_id="s", name="Keep")
    covenant.boons_hooks = [
        VirtueFlawInstance(vf_id=SHORT_BOON),
        VirtueFlawInstance(vf_id=LONG_HOOK),
        VirtueFlawInstance(vf_id=LONG_BOON),
    ]
    saga = Saga(id="s", name="Saga", covenants=[covenant])
    page = CovenantPage(
        saga, "c", SCRIPTORUM, lambda _id: None, lambda _id: None, run=ran.append
    )
    page.codex.open_chapter("Overview")
    return page


def _click_card(page: CovenantPage, name: str) -> None:
    for card in page.findChildren(ClickableCard):
        words = " ".join(
            label.text() for label in card.findChildren(type(page.inspector.title))
        )
        if name in words and card.clicked is not None:
            card.clicked()
            return
    raise AssertionError(f"no card for {name}")


@pytest.mark.usefixtures("app")
def test_a_long_boons_inspector_opens_it_in_full() -> None:
    ran: list[commands.Command] = []
    page = _covenant_page(ran)
    _click_card(page, "Chase")
    [button] = _read_buttons(page.inspector)

    button.click()

    [form] = ran
    window = _opened(form)
    assert window.page.laid.title == "Chase"
    window.close()


@pytest.mark.usefixtures("app")
def test_a_long_hooks_inspector_opens_it_in_full() -> None:
    ran: list[commands.Command] = []
    page = _covenant_page(ran)
    _click_card(page, "Infants")
    [button] = _read_buttons(page.inspector)

    button.click()

    [form] = ran
    window = _opened(form)
    assert window.page.laid.title == "Infants"
    window.close()


@pytest.mark.usefixtures("app")
def test_a_short_boons_inspector_has_no_read_in_full() -> None:
    page = _covenant_page([])
    _click_card(page, "Wealth")

    assert _read_buttons(page.inspector) == []


def _picker(step: commands.Command | None) -> ChooseDialog:
    assert isinstance(step, commands.Choose)
    dialog = step_dialog(step, SCRIPTORUM, None)
    assert isinstance(dialog, ChooseDialog)
    return dialog


@pytest.mark.usefixtures("app")
def test_the_add_ability_pickers_read_in_full_opens_a_long_entry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    opened: list[HandoutWindow] = []
    monkeypatch.setattr(HandoutWindow, "exec", lambda self: opened.append(self) or 0)
    witch = Character(id="m", name="Agnes", type="companion")
    saga = Saga(id="s", name="Saga", characters=[witch])
    add = ops_of(saga, witch)[ABILITIES_SECTION].add
    assert add is not None
    dialog = _picker(add())
    dialog.search.setText("Athletics")
    short_enabled = dialog.read_button.isEnabled()
    dialog.search.setText("Hex")

    dialog.choose("Hex  [Supernatural]")
    dialog.read_button.click()

    [window] = opened
    assert window.page.laid.title == "Hex"
    assert not short_enabled
    assert dialog.search.text() == "Hex" and not dialog.result()
    dialog.close()


@pytest.mark.usefixtures("app")
def test_the_add_boon_pickers_read_in_full_opens_a_long_entry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    opened: list[HandoutWindow] = []
    monkeypatch.setattr(HandoutWindow, "exec", lambda self: opened.append(self) or 0)
    covenant = Covenant(id="c", saga_id="s", name="Keep")
    saga = Saga(id="s", name="Saga", covenants=[covenant])
    dialog = _picker(covenant_forms.add_boon_hook(saga, covenant, "Boon"))
    dialog.search.setText("Chase")
    [chase] = [label for label in dialog.shown() if label.startswith("Chase ")]
    dialog.choose(chase)

    assert dialog.read_button.isEnabled()
    dialog.read_button.click()

    [window] = opened
    assert window.page.laid.title == "Chase"
    dialog.close()
