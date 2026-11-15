"""My sheet on the desktop: the Playing and seat buttons' name opens the
reader's own sheet below the page on show (a jump, marked ↪ on the trail)
and c goes there and back; and the last crumb's ▾, the switcher, opens
another person, laboratory or covenant at the same level."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDialog, QLabel, QPushButton

from ars_magica_manager import players, seat, storage
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.character_sheet import CharacterSheet
from ars_magica_manager.gui.finder import FILTER_FROM, SwitcherPanel
from ars_magica_manager.gui.help import HelpPage
from ars_magica_manager.gui.seat_chip import cut
from ars_magica_manager.gui.tribunal import TribunalPage
from ars_magica_manager.gui.window import CHARACTER, MainWindow, Place
from ars_magica_manager.models import (
    Character,
    Covenant,
    Familiar,
    Laboratory,
    Player,
    Saga,
    Tribunal,
)


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


@pytest.fixture(autouse=True)
def _empty_seat():
    yield
    seat.sign_out()


def _saga() -> Saga:
    ana = Player(id="ana", name="Ana", role=players.PLAYER)
    ben = Player(id="ben", name="Ben", role=players.PLAYER)
    aurelia = Character(id="mag1", name="Aurelia", type="magus", covenant_id="home")
    aurelia.background.player_ids = ["ana"]
    aurelia.assigned_lab_id = "lab1"
    leandro = Character(id="mag2", name="Leandro", type="magus", covenant_id="home")
    leandro.background.player_ids = ["ben"]
    bertolf = Character(id="grog1", name="Bertolf", type="grog", covenant_id="home")
    bertolf.background.everyone_plays = True
    return Saga(
        id="my_sheet_saga",
        name="My Sheet Saga",
        covenants=[Covenant(id="home", saga_id="my_sheet_saga", name="Fengheld")],
        characters=[aurelia, leandro, bertolf],
        laboratories=[
            Laboratory(
                id="lab1", covenant_id="home", name="North Tower", owner_id="mag1"
            )
        ],
        familiars=[Familiar(id="fam1", character_id="mag1", name="Corax")],
        tribunals=[Tribunal(id="rhine", name="Rhine")],
        players=[ana, ben],
    )


def _window(app, saga: Saga | None = None) -> MainWindow:
    saga = saga or _saga()
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.show()
    window.activateWindow()
    QTest.qWaitForWindowActive(window)
    return window


def _seated(app, saga: Saga | None = None) -> MainWindow:
    """The storyguide sitting in Ana's seat (Play as)."""
    window = _window(app, saga)
    assert window.saga is not None
    window.sit_as(window.saga.players[0])
    return window


def _press_c(window: MainWindow) -> None:
    """c, with the focus on no field (a page may put it in one)."""
    window.setFocus()
    QTest.keyClick(window, Qt.Key.Key_C)


def _trail(window: MainWindow) -> str:
    """The trail as drawn: each crumb and the mark between crumbs."""
    words = []
    for n in range(window.crumbs.count()):
        item = window.crumbs.itemAt(n)
        shown = item.widget() if item is not None else None
        if isinstance(shown, QPushButton | QLabel):
            words.append(shown.text())
    return " ".join(words)


def _chapter(window: MainWindow) -> str:
    return window._chapter_on_show() or ""


def _at_the_meeting(window: MainWindow) -> list[Place]:
    window.open_tribunal("rhine")
    page = window.page()
    assert isinstance(page, TribunalPage)
    page.codex.open_chapter("Meeting")
    return list(window.trail)


# -- the jump and the way back --


def test_c_jumps_to_my_sheet_below_the_page_and_back_to_its_chapter(app):
    window = _seated(app)
    origin = _at_the_meeting(window)
    _press_c(window)
    assert isinstance(window.page(), CharacterSheet)
    assert window.trail == [*origin, Place(CHARACTER, "mag1")]
    assert "Rhine ↪ Aurelia" in _trail(window)
    _press_c(window)  # c again: back
    assert window.trail == origin
    assert isinstance(window.page(), TribunalPage)
    assert _chapter(window) == "Meeting"
    assert "↪" not in _trail(window)
    window.close()


def test_esc_and_the_previous_crumb_go_back_to_the_chapter(app):
    window = _seated(app)
    origin = _at_the_meeting(window)
    _press_c(window)
    QTest.keyClick(QApplication.focusWidget() or window, Qt.Key.Key_Escape)
    assert window.trail == origin and _chapter(window) == "Meeting"
    _press_c(window)
    crumbs = [window.crumbs.itemAt(n).widget() for n in range(window.crumbs.count())]  # type: ignore[union-attr]
    rhine = next(
        b for b in crumbs if isinstance(b, QPushButton) and b.text() == "Rhine"
    )
    rhine.click()
    assert window.trail == origin and _chapter(window) == "Meeting"
    window.close()


def test_c_does_nothing_while_typing_or_with_a_step_open(app):
    window = _seated(app)
    window.open_help()
    page = window.page()
    assert isinstance(page, HelpPage)
    page.filter.setFocus()
    QTest.keyClick(page.filter, Qt.Key.Key_C)
    assert isinstance(window.page(), HelpPage)
    assert page.filter.text() == "c"
    window.open_tribunal("rhine")
    step = QDialog(window)
    window._open = step
    window.setFocus()
    _press_c(window)
    assert isinstance(window.page(), TribunalPage)
    window._open = None
    step.deleteLater()
    window.close()


def test_c_does_nothing_in_the_storyguide_role_or_a_solo_saga(app):
    window = _window(app)  # the storyguide's own window
    window.open_tribunal("rhine")
    before = list(window.trail)
    _press_c(window)
    assert window.trail == before
    window.close()
    solo = _saga()
    solo.players = []
    window = _window(app, solo)
    window.open_tribunal("rhine")
    before = list(window.trail)
    _press_c(window)
    assert window.trail == before
    assert window.seat_button.isHidden()
    window.close()


def test_from_her_familiar_or_lab_my_sheet_steps_back_up(app):
    window = _seated(app)
    window.open_familiar("fam1")
    sheet = Place(CHARACTER, "mag1")
    depth = window.trail.index(sheet) + 1
    window.seat_button.part.click()  # the name opens My sheet
    assert window.trail[-1] == sheet and len(window.trail) == depth
    assert "↪" not in _trail(window)
    window.open_sanctum("mag1")
    assert window.trail[-1].kind == "laboratory"
    _press_c(window)
    assert window.trail[-1] == sheet and len(window.trail) == depth
    window.close()


# -- the button --


def test_playing_as_a_player_splits_the_seat_button(app):
    window = _window(app)
    assert not window.seat_button.is_split()
    window.sit_as(window.saga.players[0])  # type: ignore[union-attr]
    chip = window.seat_button
    assert chip.is_split() and not chip.arrow.isHidden()
    assert chip.text().strip() == "Playing as Ana"
    assert "Aurelia" in chip.toolTip()
    names = [a.text() for a in window.seat_menu().actions()]
    # Her characters first (her own, then everyone's), then the seats.
    assert names[: names.index("Storyguide")] == [
        "Your Characters",
        "Aurelia",
        "Bertolf",
        "",
    ]
    window.close()


def _troupe(saga: Saga, plays: str) -> Saga:
    """`saga` with a second storyguide, Sam, who plays `plays`."""
    sam = Player(id="sam", name="Sam", role=players.STORYGUIDE)
    saga.players.append(sam)
    for character in saga.characters:
        character.background.player_ids = ["sam"] if character.id == plays else []
        character.background.everyone_plays = False
    return saga


def test_playing_shows_your_characters_name_cut_short(app):
    saga = _troupe(_saga(), "mag1")
    saga.characters[0].name = "Aurelia filia Tytalus of Fengheld"
    window = _window(app, saga)
    window.load(saga, saga.players[-1])  # Sam's window: Playing
    chip = window.view_button
    assert chip.is_split()
    assert chip.text().strip() == cut("Aurelia filia Tytalus of Fengheld")
    assert chip.text().strip() == "Aurelia filia T…"
    assert "Aurelia filia Tytalus of Fengheld" in chip.toolTip()
    names = [a.text() for a in window.view_menu().actions()]
    assert names[-1] == "Switch to Storyguide"
    assert "Aurelia filia Tytalus of Fengheld" in names
    chip.part.click()
    assert window.trail[-1] == Place(CHARACTER, "mag1")
    window.close()


def test_playing_with_no_characters_reads_playing(app):
    saga = _troupe(_saga(), "nobody")
    window = _window(app, saga)
    window.load(saga, saga.players[-1])
    assert not window.view_button.is_split()
    assert window.view_button.text().strip() == "Playing"
    before = list(window.trail)
    _press_c(window)
    assert window.trail == before
    window.close()


def test_the_menu_opens_another_of_your_characters_and_remembers_it(app):
    window = _seated(app)
    menu = window.seat_menu()
    next(a for a in menu.actions() if a.text() == "Bertolf").trigger()
    assert window.trail[-1] == Place(CHARACTER, "grog1")
    assert "Bertolf" in window.seat_button.toolTip()
    window.open_tribunal("rhine")
    _press_c(window)
    assert window.trail[-1] == Place(CHARACTER, "grog1")
    window.close()


# -- the switcher --


def test_the_last_crumb_of_a_person_lab_or_covenant_has_a_switcher(app):
    window = _window(app)
    for opens, has in (
        (lambda: window.show_character("mag1"), True),
        (lambda: window.open_laboratory("lab1"), True),
        (lambda: window.open_covenant("home"), True),
        (lambda: window.open_tribunal("rhine"), False),
        (lambda: window.go(window._up_to("saga")), False),
    ):
        opens()
        assert (window.crumb_switch is not None) is has, window.trail[-1]
    window.close()


def test_switching_keeps_the_chapter_or_falls_back(app):
    window = _window(app)
    window.show_character("mag1")
    page = window.page()
    assert isinstance(page, CharacterSheet)
    page.open_chapter("Abilities")
    above = window.trail[:-1]
    window.switch_to("mag2")
    assert window.trail == [*above, Place(CHARACTER, "mag2")]
    assert _chapter(window) == "Abilities"
    # A grog has no Hermetic Magic: where they were last left instead.
    grog = Place(CHARACTER, "grog1")
    window._chapters[grog] = "Description"
    page = window.page()
    assert isinstance(page, CharacterSheet)
    page.open_chapter("Hermetic Magic")
    window.switch_to("grog1")
    assert window.trail[-1] == grog
    assert _chapter(window) == "Description"
    assert window._chapters[grog] == "Description"
    window.close()


def test_switching_after_a_jump_keeps_where_it_jumped_from(app):
    window = _seated(app)
    origin = _at_the_meeting(window)
    _press_c(window)
    window.switch_to("mag2")
    assert window.trail == [*origin, Place(CHARACTER, "mag2")]
    assert "Rhine ↪ Leandro" in _trail(window)
    window.close()


def _crowded() -> Saga:
    saga = _saga()
    saga.characters += [
        Character(id=f"g{n}", name=f"Grog {n:02}", type="grog", covenant_id="home")
        for n in range(1, FILTER_FROM + 1)
    ]
    return saga


def test_the_switcher_lists_the_covenants_people_by_group(app):
    window = _window(app)
    window.show_character("mag1")
    assert window.crumb_switch is not None
    window.crumb_switch.click()
    panel = window.switcher
    assert isinstance(panel, SwitcherPanel) and panel.isVisible()
    assert panel.field is None  # a short list: no filter
    assert panel.headings() == ["Magi", "Grogs"]
    assert panel.shown() == ["Aurelia", "Leandro", "Bertolf"]
    assert panel.chosen() == "Aurelia"  # the one on show, marked
    target = panel.matches
    QTest.keyClick(target, Qt.Key.Key_Down)
    QTest.keyClick(target, Qt.Key.Key_Down)
    QTest.keyClick(target, Qt.Key.Key_Down)  # stays on the last
    assert panel.chosen() == "Bertolf"
    QTest.keyClick(target, Qt.Key.Key_Up)
    QTest.keyClick(target, Qt.Key.Key_Return)
    assert window.trail[-1] == Place(CHARACTER, "mag2")
    window.close()


def test_a_long_list_has_a_filter_and_esc_closes_it(app):
    window = _window(app, _crowded())
    window.show_character("mag1")
    assert window.crumb_switch is not None
    window.crumb_switch.click()
    panel = window.switcher
    assert isinstance(panel, SwitcherPanel) and panel.field is not None
    assert len(panel.shown()) == FILTER_FROM + 3
    QTest.keyClicks(panel.field, "grog 1")
    assert panel.shown() == [f"Grog {n}" for n in range(10, FILTER_FROM + 1)]
    assert panel.headings() == ["Grogs"]
    QTest.keyClick(panel.field, Qt.Key.Key_Down)
    assert panel.chosen() == "Grog 11"
    QTest.keyClick(panel.field, Qt.Key.Key_Escape)
    assert not panel.isVisible()
    assert window.trail[-1] == Place(CHARACTER, "mag1")
    window.crumb_switch.click()
    panel = window.switcher
    assert isinstance(panel, SwitcherPanel) and panel.field is not None
    QTest.keyClicks(panel.field, "grog 03")
    QTest.keyClick(panel.field, Qt.Key.Key_Enter)
    assert window.trail[-1] == Place(CHARACTER, "g3")
    window.close()


def test_the_switcher_leaves_out_what_a_seat_cannot_read(app):
    saga = _saga()
    hidden = Character(id="npc", name="Hidden Grog", type="grog", covenant_id="home")
    hidden.known = False
    saga.characters.append(hidden)
    window = _window(app, saga)
    window.show_character("mag1")
    assert window.crumb_switch is not None
    window.crumb_switch.click()
    assert window.switcher is not None
    assert "Hidden Grog" in window.switcher.shown()
    window.switcher.close()
    window.sit_as(saga.players[0])
    window.show_character("mag1")
    assert window.crumb_switch is not None
    window.crumb_switch.click()
    assert window.switcher is not None
    assert "Hidden Grog" not in window.switcher.shown()
    window.close()
