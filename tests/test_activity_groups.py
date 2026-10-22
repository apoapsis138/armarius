"""Every seasonal activity's group (what the season is for), and the
activity picker the core builds from them: its Type and Book filters,
its headings and the character's recent activities."""

from __future__ import annotations

from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import commands
from ars_magica_manager.commands import Choice, Picked
from ars_magica_manager.forms import activity as activity_forms
from ars_magica_manager.models import DiaryEntry, SeasonPlan
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.rules import activity_groups as groups
from ars_magica_manager.rules import lab_seasons


def test_every_activity_belongs_to_a_group_of_its_kind():
    for activity in rules.ACTIVITIES.values():
        allowed = groups.LAB_GROUPS if activity.lab else groups.GROUPS
        assert activity.group in allowed, activity.key
    assert {a.group for a in rules.ACTIVITIES.values() if a.tradition} == {
        groups.TRADITION
    }


def test_a_filter_lets_through_only_the_entries_with_its_value():
    study = Choice("Practice", "practice", facets=(("Type", "Study"),))
    work = Choice("Work", "exposure", facets=(("Type", "Work & trade"),))
    assert commands.filter_values([work, study, work], "Type") == [
        "Work & trade",
        "Study",
    ]
    assert commands.passes(study, {"Type": "Study"})
    assert not commands.passes(work, {"Type": "Study"})
    assert commands.passes(work, {"Type": None})
    assert commands.facet(work, "Book") == ""


def _magus():
    saga = _sample_saga_with_covenant()
    magus = next(c for c in saga.characters if c.type == "magus")
    return saga, magus


def test_the_activity_picker_lists_activities_by_group_then_name():
    saga, magus = _magus()
    step = activity_forms.choose_activity(saga, magus)
    choices = step.choices()
    assert step.filters == (activity_forms.TYPE, activity_forms.BOOK)
    headings = list(dict.fromkeys(commands.heading(step, c) for c in choices))
    assert headings == [g for g in groups.GROUPS if g in headings]
    study = [c.value for c in choices if commands.heading(step, c) == groups.STUDY]
    labels = [rules.ACTIVITIES[k].label.lower() for k in study]
    assert labels == sorted(labels)
    # Only the lab work that takes over a laboratory is on the sheet, with
    # Order & covenant.
    lab_work = [c for c in choices if rules.ACTIVITIES[c.value].lab]
    assert [c.value for c in lab_work] == ["take_over_lab"]
    assert commands.heading(step, lab_work[0]) == groups.ORDER
    practice = next(c for c in choices if c.value == rules.PRACTICE)
    assert commands.facet(practice, activity_forms.BOOK) == activity_forms.CORE_BOOK
    assert step.apply("practice") == Picked("practice")


def test_activities_from_books_not_in_play_are_listed_only_when_asked():
    saga, magus = _magus()
    saga.books_in_play = []
    step = activity_forms.choose_activity(saga, magus)
    offered = {c.value for c in step.choices()}
    assert "study_realia" not in offered
    assert step.others is not None
    assert "study_realia" in {c.value for c in step.others()}


def test_the_lab_work_picker_lists_the_lab_work_under_its_own_groups():
    saga, magus = _magus()
    step = activity_forms.choose_activity(saga, magus, lab=True)
    choices = step.choices()
    assert {c.value for c in choices} == set(lab_seasons.LAB_ACTIVITIES)
    headings = list(dict.fromkeys(commands.heading(step, c) for c in choices))
    assert headings == list(groups.LAB_GROUPS)


def test_recent_activities_come_from_plans_and_the_diary_newest_first():
    saga, magus = _magus()
    magus.diary += [
        DiaryEntry(1218, "Summer", activity="Practice"),
        DiaryEntry(1219, "Autumn", activity="Read a book"),
        DiaryEntry(1219, "Winter", activity="Practice"),
    ]
    saga.season_plans.append(
        SeasonPlan(magus.id, saga.current_year, saga.current_season, rules.TEACH)
    )
    step = activity_forms.choose_activity(saga, magus)
    assert step.recent is not None
    assert [c.value for c in step.recent()] == [rules.TEACH, rules.PRACTICE, rules.READ]
