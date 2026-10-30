"""Conflicts on the desktop: the saga page's chapter of fight and siege
cards, each opening its drawn page, the pages' buttons running the
core's commands, and the six sets of season medallions in both themes."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPointF
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QApplication, QLabel, QPushButton
from support import everything_saga

from ars_magica_manager import battles, conflicts, fights, medallions, sieges, storage
from ars_magica_manager.commands import Form
from ars_magica_manager.gui import medallions as drawn
from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.conflicts import FightPage, SiegeBody, SiegePage
from ars_magica_manager.gui.editing import place_for
from ars_magica_manager.gui.themes import PALETTES
from ars_magica_manager.gui.widgets import ClickableCard
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import SEASONS, Saga, Siege, SiegeEvent


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    assert pictures.register_fonts() == []
    return application


def _defaults(form: Form) -> dict:
    return {f.key: f.value for f in form.fields() if f.kind != "info"}


def _saga() -> Saga:
    saga = everything_saga()
    add = fights.ops(saga).add
    assert add is not None
    made = add()
    assert isinstance(made, Form)
    made.apply(
        {
            **_defaults(made),
            "name": "The Fray at Testford",
            "first": "Ours",
            "second": "Theirs",
        }
    )
    fight = saga.fights[0]
    joining = fights.add_combatant(saga, fight)
    assert isinstance(joining, Form)
    for side, name in (("0", "Grog"), ("1", "Bandit")):
        joining.apply(
            {
                "side": side,
                "kind": "",
                "name": name,
                "count": 2,
                "init": 1,
                "attack": 7,
                "defence": 5,
                "damage": 5,
                "soak": 3,
                "size": 0,
            }
        )
    siege = sieges.ops(saga).add
    assert siege is not None
    form = siege()
    assert isinstance(form, Form)
    form.apply(
        {
            **_defaults(form),
            "name": "The Siege of Testburg",
            "miners": 1,
            "engine_Trebuchet": 2,
        }
    )
    return saga


def _window() -> tuple[MainWindow, Saga]:
    saga = _saga()
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.show()
    assert window.saga is not None
    return window, window.saga


def _words(widget) -> str:
    return " ".join(label.text() for label in widget.findChildren(QLabel))


def _button(page, words: str) -> QPushButton:
    return next(b for b in page.findChildren(QPushButton) if b.text().strip() == words)


def test_the_conflicts_chapter_opens_a_fight_and_a_siege(app):
    window, _ = _window()
    ran: list = []
    window.run = lambda command, *a, **k: ran.append(command)  # type: ignore[method-assign]
    window.go(window.trail)
    page = window.page()
    assert page is not None
    page.codex.open_chapter("Conflicts")  # type: ignore[attr-defined]
    adds = [b for b in page.findChildren(QPushButton) if b.text().strip() == "Add"]
    for add in adds:
        add.click()
    assert [c.title for c in ran] == ["Add a Battle", "Add a Fight", "Add a Siege"]
    [card] = [
        c
        for c in page.findChildren(ClickableCard)
        if "The Fray at Testford" in _words(c)
    ]
    card.clicked()
    assert isinstance(window.page(), FightPage)
    assert window.crumb_names()[-1] == "The Fray at Testford"
    # A fight's and a siege's steps open as windows over the page.
    assert place_for(None, window.page()) is None
    window.go(window.trail[:2])
    page = window.page()
    assert page is not None
    page.codex.open_chapter("Conflicts")  # type: ignore[attr-defined]
    [card] = [
        c
        for c in page.findChildren(ClickableCard)
        if "The Siege of Testburg" in _words(c)
    ]
    card.clicked()
    assert isinstance(window.page(), SiegePage)
    assert window.crumb_names()[-1] == "The Siege of Testburg"
    assert place_for(None, window.page()) is None
    assert window.menu_page() is None


def test_the_pages_buttons_run_the_commands(app, monkeypatch):
    window, saga = _window()
    asked: list[tuple[str, int | None]] = []
    monkeypatch.setattr(
        conflicts, "command", lambda _saga, action, row: asked.append((action, row))
    )
    window.run = lambda command, *a, **k: None  # type: ignore[method-assign]
    window.open_fight(saga.fights[0].id)
    page = window.page()
    assert isinstance(page, FightPage)
    page.grab()  # the leaf paints with its blows and seals
    for words in (
        "Next Blow",
        "Next Round",
        "Restart",
        "Add Combatant",
        "Edit Combatant",
        "Remove Combatant",
        "Form a Group",
        "Break up a Group",
    ):
        _button(page, words).click()
    assert asked == [
        (action, 0)
        for action in (
            "next_blow",
            "next_round",
            "restart_fight",
            "add_combatant",
            "edit_combatant",
            "remove_combatant",
            "form_group",
            "break_group",
        )
    ]
    window.open_siege(saga.sieges[0].id)
    page = window.page()
    assert isinstance(page, SiegePage)
    page.grab()
    _button(page, "Next Siege Event").click()
    assert asked[-1] == ("next_siege_event", 0)


def test_every_set_of_medallions_paints_in_both_themes(app):
    image = QImage(160, 160, QImage.Format.Format_ARGB32)
    for p in PALETTES:
        for key in medallions.KEYS:
            for season in SEASONS:
                image.fill(0)
                painter = QPainter(image)
                drawn.paint(
                    painter, key, QPointF(80, 80), 40, season, 1221, p, now=True
                )
                painter.end()
                assert image.pixelColor(80, 80).alpha() > 0, (key, season)
    assert set(drawn.PAINTERS) == set(medallions.KEYS)


def test_a_battle_card_plays_edits_and_deletes(app, monkeypatch):
    window, saga = _window()
    asked: list[tuple[str, int | None]] = []
    monkeypatch.setattr(
        conflicts, "command", lambda _saga, action, row: asked.append((action, row))
    )
    ran: list = []
    window.run = lambda command, *a, **k: ran.append(command)  # type: ignore[method-assign]
    window.go(window.trail)
    page = window.page()
    assert page is not None
    page.codex.open_chapter("Conflicts")  # type: ignore[attr-defined]
    titles = [label.text() for label in page.findChildren(QLabel)]
    assert titles.index(battles.title(saga)) < titles.index(fights.title(saga))
    assert saga.battles, "the sample saga fights a battle"
    _button(page, "Battle Event").click()
    assert asked == [("conflict_battle_event", 0)]
    _button(page, "Edit").click()
    _button(page, "Delete").click()
    assert [type(c).__name__ for c in ran[-2:]] == ["Form", "Confirm"]


def test_a_siege_between_lords_names_and_flies_their_arms(app):
    from ars_magica_manager.gui.region import NeighbourPage

    saga = _saga()
    gottfried = saga.neighbour("gottfried")
    assert gottfried is not None
    siege = saga.sieges[-1]
    siege.castle, siege.besieger, siege.holder = "", "", ""
    siege.besieger_id = gottfried.id
    assert sieges.besieger_name(saga, siege) == gottfried.name
    page = SiegePage(saga, siege, PALETTES[0], lambda _command: None)
    page.grab()  # the shields and the names paint from the linked lord
    fief = NeighbourPage(saga, gottfried, PALETTES[0])
    titles = [label.text() for label in fief.findChildren(QLabel)]
    assert any(t.startswith("Sieges (") for t in titles)


# -- the siege page's chronicle --


def test_the_siege_chronicle_shows_every_event_and_wraps_long_lines(app):
    siege = Siege(
        "S",
        events=[
            SiegeEvent(7 * n, "Keep the stockade", f"Event {n}") for n in range(12)
        ],
    )
    siege.events.append(
        SiegeEvent(90, "Escalade", "The besiegers win a foothold " * 20, ["a " * 200])
    )
    body = SiegeBody(Saga(id="s", name="S", sieges=[siege]), siege, PALETTES[0])
    rows = body._chronicle_rows(980)
    words = [text for _, text, _ in rows]
    assert words[0] == "Day 0: Event 0" and "Day 77: Event 11" in words
    assert sum(1 for _, _, opens in rows if opens) == 13
    assert len(rows) > 13 + 2  # the long event and its working wrap
    short = body._height(1000)
    body.resize(1000, short)
    assert body.minimumHeight() >= short
    siege.events.append(SiegeEvent(97, "Keep the stockade", "One more"))
    assert body._height(1000) > short
