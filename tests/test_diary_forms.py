"""A Diary's Add, Edit and Delete without a front-end: a character's or
laboratory's (DiaryEntry) and a covenant's (CovenantDiaryEntry)."""

from __future__ import annotations

from typing import Any

from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import commands, diary_forms, form_spec
from ars_magica_manager.models import (
    STORY_EVENT,
    CovenantDiaryEntry,
    DiaryEntry,
    VirtueFlawInstance,
)


def _answer(form: Any, typed: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    assert isinstance(form, commands.Form)
    fields = form.fields()
    raw = {f.key: f.value for f in fields} | typed
    shown = [f for f in fields if f.kind != "info" and form_spec.shown(f, raw)]
    values = form_spec.result(shown, lambda f: raw[f.key])
    return values, form.validate(values) if form.validate else None


def test_a_laboratorys_diary_entries_are_added_edited_and_deleted():
    saga = _sample_saga_with_covenant()
    lab = saga.laboratories[0]
    ops = diary_forms.entry_ops(saga, lab.diary)
    assert ops.add and ops.edit and ops.remove
    form = ops.add()
    assert form.title == "Add a Diary Entry"
    fields = {f.key: f for f in form.fields()}
    assert fields["year"].value == saga.current_year
    assert fields["season"].value == saga.current_season
    values, _ = _answer(form, {"name": "Pilum of Fire", "activity": None})
    form.apply(values)
    assert lab.diary == [
        DiaryEntry(
            year=saga.current_year,
            season=saga.current_season,
            activity="",
            name="Pilum of Fire",
        )
    ]
    edit = ops.edit(0)
    assert edit.title == "Edit a Diary Entry"
    edit.apply(_answer(edit, {"details": "It *worked*."})[0])
    assert lab.diary[0].details == "It *worked*."
    confirm = ops.remove(0)
    assert confirm.question == "Delete Pilum of Fire?"
    confirm.apply()
    assert lab.diary == []


def test_a_characters_diary_offers_the_seasonal_activities():
    saga = _sample_saga_with_covenant()
    character = saga.characters[0]
    ops = diary_forms.entry_ops(
        saga, character.diary, diary_forms.character_activities()
    )
    assert ops.add is not None
    activity = next(f for f in ops.add().fields() if f.key == "activity")
    assert [label for label, _ in activity.options] == (
        diary_forms.character_activities()
    )


def test_a_covenant_story_event_links_a_boon_and_counts_its_points():
    saga = _sample_saga_with_covenant()
    covenant = saga.covenants[0]
    covenant.boons_hooks.append(
        VirtueFlawInstance("covbh_boon_minor_hidden_resources", id="bh1")
    )
    ops = diary_forms.covenant_diary_ops(saga, covenant)
    assert ops.add is not None and ops.edit is not None
    form = ops.add()
    fields = {f.key: f for f in form.fields()}
    assert ("Hidden Resources (Boon)", "bh1") in fields["boon_hook_id"].options
    values, _ = _answer(form, {"name": "Bought a mill", "pounds": "-12"})
    assert "status" not in values  # not a Story Event
    form.apply(values)
    assert covenant.diary[0].pounds == -12
    _values, problem = _answer(
        ops.add(),
        {
            "name": "A hoard",
            "category": STORY_EVENT,
            "boon_hook_id": "bh1",
            "status": "Resolved",
            "build_points": "400",
        },
    )
    assert problem == "Only 250 of this Boon's 250 Build Points are left."
    story = ops.add()
    values, problem = _answer(
        story,
        {
            "name": "A hoard",
            "category": STORY_EVENT,
            "boon_hook_id": "bh1",
            "build_points": "100",
        },
    )
    assert problem is None
    story.apply(values)
    entry = covenant.diary[1]
    assert isinstance(entry, CovenantDiaryEntry)
    assert (entry.status, entry.build_points) == ("Open", 100)
    # Edit and Delete take the entry's index in the diary itself.
    edit = ops.edit(1)
    edit.apply(_answer(edit, {"status": "Resolved"})[0])
    assert covenant.diary[1].status == "Resolved"
    ops.remove(0).apply()
    assert [e.name for e in covenant.diary] == ["A hoard"]
