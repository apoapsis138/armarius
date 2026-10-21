"""Chained previews: a season ahead is worked out from the saga as the
seasons planned before it leave it (the Seasons Ahead, the laboratory's
Planning tab, the Plan Season preview), a die not yet rolled counts as
gaining nothing, and the real saga is never changed."""

from __future__ import annotations

from dataclasses import asdict

from support import strip_markup
from test_lab_seasons import _plan as _lab_plan
from test_lab_seasons import _saga as _lab_saga

from ars_magica_manager import saga_overview as ov
from ars_magica_manager import seasons
from ars_magica_manager.forms import season as season_forms
from ars_magica_manager.models import Book, SeasonPlan, XpAllocation
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.seasons import projection as ahead


def _saga():
    saga = _lab_saga()
    saga.books.append(
        Book(
            "summa",
            "On Fire",
            "Art Summa",
            owner_kind="covenant",
            owner_id="cov",
            art="Ignem",
            level=10,
            quality=15,
        )
    )
    return saga


def _practice(season: str):
    """Reading the Ignem summa: 15 xp a season."""
    return SeasonPlan("m", 1220, season, rules.READ, book_id="summa")


def test_a_later_season_counts_the_gains_before_it():
    saga = _saga()
    seasons.set_plan(saga, _practice("Spring"))
    seasons.set_plan(saga, _practice("Summer"))
    spring = ahead.projection(saga).outcome("m", "Spring", 1220)
    summer = ahead.projection(saga).outcome("m", "Summer", 1220)
    assert spring is not None and summer is not None
    assert summer.gains[0].before == spring.gains[0].after
    info = seasons.ahead_info(saga, saga.characters[0], 0)
    assert f"{spring.gains[0].after} -> {summer.gains[0].after} xp" in info
    assert "as the seasons planned before it will leave them" in info


def test_the_real_saga_is_left_as_it_was():
    saga = _saga()
    seasons.set_plan(saga, _practice("Spring"))
    seasons.set_plan(saga, _practice("Summer"))
    before = asdict(saga)
    ahead.projection(saga).outcome("m", "Autumn", 1220)
    assert asdict(saga) == before


def test_a_higher_art_raises_a_later_lab_total():
    saga = _saga()
    seasons.set_plan(saga, _practice("Spring"))
    seasons.plan_lab_work(saga, _lab_plan("bolt", season="Summer"))
    found = ahead.projection(saga).work("m", "Summer", 1220)
    assert found is not None
    _, work = found
    # Ignem 5 -> 7 after the Spring's 15 xp: the CrIg Lab Total 15 -> 17.
    assert work is not None and int(work.lab_total.total) == 17
    lab = saga.laboratories[0]
    rows = seasons.lab_queue(saga, lab)
    summer = next(r for r in rows if r.season == "Summer")
    assert summer.work is not None and int(summer.work.lab_total.total) == 17


def test_an_invention_carries_its_points_season_to_season():
    saga = _saga()
    seasons.plan_lab_work(saga, _lab_plan("bolt"))
    rows = seasons.lab_queue(saga, saga.laboratories[0])
    assert rows[0].work is not None and rows[0].work.points_after == 10
    assert rows[0].work.finished


def test_an_unrolled_die_counts_as_nothing_gained():
    saga = _saga()
    magus = saga.characters[0]
    magus.raw_vis = {"ignem": 5}
    seasons.set_plan(
        saga,
        SeasonPlan(
            "m",
            1220,
            "Spring",
            rules.VIS_STUDY,
            allocations=[XpAllocation("art:ignem")],
        ),
    )
    seasons.set_plan(saga, _practice("Summer"))
    summer = ahead.projection(saga).outcome("m", "Summer", 1220)
    assert summer is not None
    assert summer.gains[0].before == magus.arts["ignem"].xp
    info = seasons.ahead_info(saga, magus, 0)
    assert "Counts nothing gained from Study from vis (Spring 1220)" in info


def test_the_projection_is_kept_while_the_saga_is_unchanged():
    saga = _saga()
    first = ahead.projection(saga)
    assert ahead.projection(saga) is first
    seasons.set_plan(saga, _practice("Spring"))
    assert ahead.projection(saga) is not first


def test_plan_season_previews_a_season_ahead_after_the_ones_before():
    saga = _saga()
    magus = saga.characters[0]
    seasons.set_plan(saga, _practice("Spring"))
    form = season_forms.plan_season(saga, magus, when=("Summer", 1220))
    values = {f.key: f.value for f in form.fields() if f.kind != "info"}
    values.update(activity=rules.READ, book_id="summa")
    assert form.live is not None
    after_spring = magus.arts["ignem"].xp + 15
    assert f"{after_spring} -> {after_spring + 15} xp" in form.live(values)


def test_the_calendar_gives_each_planned_season_its_result():
    saga = _saga()
    magus = saga.characters[0]
    seasons.set_plan(saga, _practice("Spring"))
    seasons.set_plan(saga, _practice("Summer"))
    rows = dict(ov.calendar(saga, magus))
    spring, summer = rows[1220][0], rows[1220][1]
    assert spring is not None and summer is not None
    assert spring.result == "Ignem 7 (+15 xp)"
    assert summer.result == "Ignem 9 (+15 xp)"
    text = ov.calendar_text(saga, magus)
    assert "Ignem 9 (+15 xp)" in text
    assert max(len(line) for line in strip_markup(text).splitlines()) <= 76
