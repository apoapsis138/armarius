"""Ahead: what is coming, asked of every part of the saga; its span,
its filters, a covenant's own view, and the storyguide's calendar."""

from __future__ import annotations

from support import everything_saga

from ars_magica_manager import ahead
from ars_magica_manager.commands import Confirm, Form, Refuse
from ars_magica_manager.forms import ahead as ahead_forms
from ars_magica_manager.models import EVERY, YEARLY, CalendarEntry, season_order


def _titles(found):
    return [(e.season, e.year, e.title) for e in found]


def test_each_source_says_what_is_coming_in_the_span():
    saga = everything_saga()
    found = _titles(ahead.entries(saga))
    assert ("Summer", 1220, "The Drachenfels: Level 2 opens") in found
    assert ("Summer", 1221, "The Drachenfels: Level 2 opens") in found
    # The threat's clock: one of its three stages has come.
    assert ("Winter", 1220, "■□□ The Hollow Crown: The ford floods") in found
    assert ("Winter", 1220, "The world turns: the yearly step") in found
    assert ("Winter", 1221, "The world turns: the yearly step") in found
    fair = [t for t in found if "fair" in t[2]]
    assert [(s, y) for s, y, _ in fair] == [("Autumn", 1220), ("Autumn", 1221)]
    # Two years from Spring 1220: nothing from 1222 on.
    assert all(year <= 1221 for _s, year, _t in found)
    assert found == sorted(found, key=lambda t: season_order(season=t[0], year=t[1]))


def test_the_span_is_kept_with_the_saga():
    saga = everything_saga()
    assert ahead.span_text(saga) == "2 years (to Winter 1221)"
    saga.ahead_span = 1
    assert ahead.span_text(saga) == "1 year (to Winter 1220)"
    assert all(e.year == 1220 for e in ahead.entries(saga))
    saga.ahead_span = 0
    assert ahead.span_text(saga).startswith("To the next Tribunal (")
    assert ahead.next_tribunal_text(saga) in ahead.span_text(saga)
    form = ahead_forms.looking_form(saga)
    values = {f.key: f.value for f in form.fields()}
    values.update(span="3", show=ahead.PLACES)
    form.apply(values)
    assert (saga.ahead_span, saga.ahead_show) == (3, ahead.PLACES)
    assert {e.show for e in ahead.shown(saga)} == {ahead.PLACES}


def test_a_calendar_entry_comes_once_or_again():
    saga = everything_saga()
    saga.calendar = [
        CalendarEntry("Vis lease ends", 1221, "Spring"),
        CalendarEntry("Midsummer rites", 1219, "Summer", repeats=YEARLY),
        CalendarEntry("The comet", 1218, "Autumn", repeats=EVERY, every=3),
    ]
    found = _titles(e for e in ahead.entries(saga) if e.show == ahead.CALENDAR)
    assert found == [
        ("Summer", 1220, "Midsummer rites"),
        ("Spring", 1221, "Vis lease ends"),
        ("Summer", 1221, "Midsummer rites"),
        ("Autumn", 1221, "The comet"),
    ]


def test_a_covenant_sees_what_concerns_it():
    saga = everything_saga()
    covenant = saga.covenants[0]
    saga.calendar = [
        CalendarEntry("Keep's feast", 1220, "Summer", covenant_id="cov1"),
        CalendarEntry("Another's feast", 1220, "Summer", covenant_id="other"),
    ]
    titles = [e.title for e in ahead.shown(saga, covenant)]
    assert "Keep's feast" in titles and "Another's feast" not in titles
    assert any("fair" in t for t in titles)
    assert "The world turns: the yearly step" not in titles
    assert ahead.title(saga, covenant) == "Ahead for Keep: 2 years"


def test_only_your_own_entries_are_edited_here():
    saga = everything_saga()
    ops = ahead_forms.ahead_ops(saga)
    assert ops.add is not None and ops.edit is not None and ops.remove is not None
    form = ops.add()
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    values.update(title="Elsbeth returns", year=1221, season="Summer")
    form.apply(values)
    assert saga.calendar[-1].title == "Elsbeth returns"
    rows = ops.rows()
    mine = rows.index("Elsbeth returns")
    worked_out = rows.index("The world turns: the yearly step")
    refused = ops.edit(worked_out)
    assert isinstance(refused, Refuse) and "change it there" in refused.why
    assert isinstance(ops.remove(worked_out), Refuse)
    edit = ops.edit(mine)
    assert isinstance(edit, Form)
    values = {f.key: f.value for f in edit.fields()}
    values.update(repeats=EVERY, every=None)
    assert edit.validate is not None and edit.validate(values)
    confirm = ops.remove(mine)
    assert isinstance(confirm, Confirm)
    confirm.apply()
    assert "Elsbeth returns" not in ops.rows()


def test_a_new_source_registers_itself():
    saga = everything_saga()

    def omens(_saga, start, stop):
        year, season = ahead._from_order(start)
        return [ahead.Entry(year, season, "An omen", ahead.EVERYTHING, "the stars")]

    ahead.register(omens)
    try:
        assert ahead.due_now(saga) >= 1
        assert "An omen" in [e.title for e in ahead.entries(saga)]
    finally:
        ahead.SOURCES.remove(omens)
