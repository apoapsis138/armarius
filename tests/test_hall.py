"""The grand hall: the seats of a meeting, covenant by covenant, each
seat's side as the vote goes, where the seats sit in the hemicycle, and
the opening card; and the desktop drawing them."""

from __future__ import annotations

import itertools
import math
import os

import pytest
from support import everything_saga

from ars_magica_manager import hall, meeting
from ars_magica_manager.arms import Arms


def _held(saga):
    rhine = saga.tribunal("rhine")
    assert rhine is not None
    opening = meeting.hold(saga, rhine)
    opening.apply({f.key: f.value for f in opening.fields() if f.kind != "info"})
    return rhine


def test_every_vote_in_the_hall_has_a_seat():
    saga = everything_saga()
    rhine = _held(saga)
    benches = hall.benches(saga, rhine, rhine.meeting, None)
    assert [b.covenant.name for b in benches] == ["Keep", "Fengheld"]
    seats = sum(len(b.seats) for b in benches)
    assert seats == meeting.hall(saga, rhine, rhine.meeting)[0]
    # A proxy's seat is marked, and every seat is undecided with no case.
    assert any(s.proxy for b in benches for s in b.seats)
    assert {s.side for b in benches for s in b.seats} == {meeting.UNDECIDED}


def test_seats_take_the_side_their_votes_went():
    saga = everything_saga()
    rhine = _held(saga)
    case = rhine.cases[0]
    leaning = {"cov1": meeting.AGAINST, "cov_sketch": meeting.FOR}
    rhine.meeting.setdefault("votes", {})[case.id] = {"leanings": leaning}
    benches = hall.benches(saga, rhine, rhine.meeting, case)
    expected = meeting.tally(saga, rhine, rhine.meeting, case)
    assert hall.tally_so_far(benches) == expected
    # Calling the vote: before the first covenant is called, nothing is
    # decided; after it, its seats are.
    none_yet = hall.benches(saga, rhine, rhine.meeting, case, called=0)
    assert not any(b.called for b in none_yet)
    assert hall.tally_so_far(none_yet)[:2] == (0, 0)
    first = hall.benches(saga, rhine, rhine.meeting, case, called=1)
    assert first[0].called and not first[1].called
    assert hall.tally_so_far(first)[1] == len(first[0].seats)


def test_the_seats_fill_the_hemicycle_from_left_to_right():
    for count in (1, 5, 23, 84):
        places = hall.seat_places(count)
        assert len(places) == count
        angles = [a for a, _r in places]
        assert all(a >= b - 1e-9 for a, b in itertools.pairwise(angles))
        assert all(0 < a < math.pi for a in angles)
        assert all(hall.INNER <= r <= hall.OUTER for _a, r in places)
    assert hall.rows_for(84) > hall.rows_for(5)


def test_the_opening_card():
    assert hall.roman(1228) == "MCCXXVIII"
    assert hall.roman(1194) == "MCXCIV"
    saga = everything_saga()
    keep = saga.covenant("cov1")
    assert keep is not None
    keep.arms = Arms("Azure", charge="Tower").to_dict()
    rhine = _held(saga)
    card = hall.opening_card(saga, rhine)
    assert card.anno == "Anno Domini MCCXXVIII"
    assert card.title == "The Rhine Tribunal"
    assert card.opened == "is opened at Durenmar"
    assert [name for name, _arms in card.arms] == ["Keep"]
    assert card.numbers.startswith("2 covenants · ")
    assert card.numbers.endswith("Severinus presiding")


def test_the_desktop_draws_the_hall_and_plays_the_opening_card():
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication, QWidget

    from ars_magica_manager.gui.hall import GrandHall, OpeningCard
    from ars_magica_manager.gui.themes import PALETTES

    app = QApplication.instance() or QApplication([])
    saga = everything_saga()
    rhine = _held(saga)
    drawn = GrandHall(saga, rhine, rhine.cases[0], PALETTES[0])
    drawn.resize(800, 560)
    assert not drawn.grab().isNull()
    drawn.call_the_vote()
    assert drawn.called == 0
    assert drawn.calling().startswith("Calling Keep")
    for _ in range(3):
        drawn._call_next()
    assert drawn.called is None and not drawn.timer.isActive()
    window = QWidget()
    window.resize(1000, 700)
    window.show()
    card = OpeningCard(window, hall.opening_card(saga, rhine), PALETTES[0])
    card.play()
    app.processEvents()
    assert card.isVisible() and card.geometry() == window.rect()
    card.close()
    assert not card.isVisible()


def test_closing_the_opening_card_opens_the_step_that_follows():
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication, QWidget

    from ars_magica_manager.gui.hall import OpeningCard
    from ars_magica_manager.gui.themes import PALETTES

    app = QApplication.instance() or QApplication([])
    saga = everything_saga()
    rhine = _held(saga)
    window = QWidget()
    window.resize(1000, 700)
    window.show()
    opened: list[str] = []
    card = OpeningCard(
        window,
        hall.opening_card(saga, rhine),
        PALETTES[0],
        lambda: opened.append("next"),
    )
    card.play()
    app.processEvents()
    assert opened == []
    card.close()
    for _ in range(5):
        app.processEvents()
    assert opened == ["next"]
