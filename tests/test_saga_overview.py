"""The saga, covenant and season pages' figures (saga_overview), without a
front-end."""

from __future__ import annotations

from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import saga_overview as ov
from ars_magica_manager.models import Character, DiaryEntry, SeasonPlan


def test_a_covenant_card_counts_its_people_and_laboratories():
    saga = _sample_saga_with_covenant()
    saga.characters.append(Character("g1", "Hilde", "grog", "cov1"))
    saga.characters.append(Character("x1", "Wanderer", "companion"))
    cards = ov.covenant_cards(saga)
    facts = {f.label: f.value for f in cards[0].facts}
    assert (facts["Magi"], facts["Grogs"], facts["Laboratories"]) == ("1", "1", "1")
    # The unassigned have their own headings on the saga page.
    assert [c.name for c in cards] == ["Test Covenant"]


def test_people_are_grouped_magi_first_and_empty_groups_left_out():
    saga = _sample_saga_with_covenant()
    saga.characters.append(Character("g1", "Hilde", "grog", "cov1"))
    groups = ov.people_groups(saga, "cov1")
    assert [title for title, _ in groups] == ["Magi", "Grogs"]
    every = ov.people_groups(saga, "cov1", every=True)
    assert [title for title, _ in every] == ["Magi", "Companions", "Grogs"]
    assert [ov.NEW_PERSON[title] for title, _ in every] == [
        ("magus", "New Magus"),
        ("companion", "New Companion"),
        ("grog", "New Grog"),
    ]


def test_every_activity_has_a_kind_and_lab_work_is_laboratory():
    assert ov.activity_kind("invent_spell") == ov.LAB
    assert ov.activity_kind("read") == ov.STUDY
    assert ov.activity_kind("write_summa") == ov.WRITING
    assert ov.activity_kind("exposure") == ov.WORK
    assert ov.activity_kind("adventure") == ov.ADVENTURE
    assert ov.activity_kind("no_such_thing") == ov.OTHER


def test_the_timeline_puts_the_diary_and_plans_in_their_seasons():
    saga = _sample_saga_with_covenant()  # Spring 1220
    character = saga.characters[0]
    character.diary.append(DiaryEntry(1219, "Winter", "", "Notes", "Read a book"))
    saga.season_plans.append(SeasonPlan(character.id, 1220, "Spring", "invent_spell"))
    line = ov.timeline(saga, [character])
    assert line.columns[line.current] == ("Spring", 1220)
    seasons = line.rows[0][2]
    assert seasons[line.current - 1] == ov.Season(
        ov.STUDY, "Read a book", "Notes", False
    )
    assert seasons[line.current].planned
    assert line.columns[-1] == ("Spring", 1221)  # four seasons ahead


def test_the_calendar_has_a_row_per_year_newest_first():
    saga = _sample_saga_with_covenant()
    character = saga.characters[0]
    character.diary.append(DiaryEntry(1218, "Summer", "", "", "Adventure"))
    rows = ov.calendar(saga, character)
    assert [year for year, _ in rows] == [1220, 1219, 1218]
    assert rows[2][1][1] is not None and rows[2][1][1].kind == ov.ADVENTURE


def test_a_laboratorys_seasons_are_its_diary_and_the_plans_made_in_it():
    saga = _sample_saga_with_covenant()  # Spring 1220
    lab = saga.laboratories[0]
    lab.diary.append(DiaryEntry(1219, "Autumn", "", "", "Invent a spell"))
    plan = SeasonPlan(saga.characters[0].id, 1220, "Summer", "invent_spell")
    plan.lab_id = lab.id
    saga.season_plans.append(plan)
    rows = ov.calendar_rows(saga, ov.lab_seasons(saga, lab))
    assert [year for year, _ in rows] == [1220, 1219]
    planned, written = rows[0][1][1], rows[1][1][2]
    assert planned is not None and planned.planned and planned.detail == "Leandro"
    assert written is not None and written.kind == ov.LAB
