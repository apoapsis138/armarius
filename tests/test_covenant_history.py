"""A covenant's History tab: its timeline gathered from the covenant's
Diary, its places' and their records' diaries and Ahead, merged and in
order; its eras; and leaving an entry out and putting it back."""

from __future__ import annotations

from support import everything_saga

from ars_magica_manager.commands import Confirm, Form
from ars_magica_manager.forms import covenant_history as ch
from ars_magica_manager.manors import manors_of
from ars_magica_manager.models import (
    EVERY,
    STORY_EVENT,
    CalendarEntry,
    Covenant,
    CovenantDiaryEntry,
    Neighbour,
)
from ars_magica_manager.sections import (
    ERAS_SECTION,
    HISTORY_SECTION,
    HISTORY_VIEW_SECTION,
)


def _saga():
    """The sample saga's first covenant, founded 1115 at the Stone House,
    with the Cave inside it and the Founders placed there."""
    saga = everything_saga()
    covenant = saga.covenants[0]
    covenant.year_founded = 1115
    covenant.place_id = "stone_house"
    covenant.diary = [
        CovenantDiaryEntry(1220, "Spring", "The pact, unpaid", category=STORY_EVENT),
        CovenantDiaryEntry(1200, "Autumn", "Trust breaks"),
    ]
    saga.neighbours += [
        Neighbour(
            "stone_house",
            "The Stone House",
            kind="place",
            details={"diary": [{"year": 74, "season": "", "text": "The tower rises"}]},
        ),
        Neighbour(
            "cave",
            "The Cave",
            kind="place",
            place_id="stone_house",
            details={
                "diary": [
                    {"year": 1211, "season": "Winter", "text": "The last night"},
                    {"year": None, "season": "", "text": "Once, long ago"},
                ]
            },
        ),
        Neighbour(
            "founders",
            "The Founders",
            place_id="stone_house",
            details={
                "diary": [
                    {"year": 1211, "season": "Winter", "text": "The last night"},
                    {"year": 1115, "season": "Summer", "text": "The five come"},
                ]
            },
        ),
        Neighbour(
            "elsewhere",
            "Elsewhere",
            details={"diary": [{"year": 1190, "season": "", "text": "Not ours"}]},
        ),
    ]
    saga.calendar = [
        CalendarEntry("The scout comes", 1220, "Autumn", covenant_id=covenant.id),
        CalendarEntry(
            "Harvest", 1220, "Summer", repeats=EVERY, every=1, covenant_id=covenant.id
        ),
    ]
    saga.current_year, saga.current_season = 1220, "Spring"
    return saga, covenant


def _texts(saga, covenant: Covenant) -> list[str]:
    return [r.text for r in ch.rows(saga, covenant)]


def test_the_history_gathers_every_diary_oldest_first():
    saga, covenant = _saga()
    assert _texts(saga, covenant) == [
        "Once, long ago",
        "The tower rises",
        "The five come",
        "Trust breaks",
        "The last night",
        "The pact, unpaid",
        "The scout comes",
    ]


def test_the_same_date_and_words_are_one_row_naming_both_records():
    saga, covenant = _saga()
    night = next(r for r in ch.rows(saga, covenant) if r.text == "The last night")
    assert [s.label for s in night.sources] == ["The Cave", "The Founders"]


def test_without_eras_it_is_told_before_and_after_the_founding():
    saga, covenant = _saga()
    names = [
        name for name, _years, row in ch.shown(saga, covenant).lines if row is None
    ]
    assert names == [ch.BEFORE, ch.SINCE, ch.NOW, ch.UNDATED]


def test_its_own_eras_split_the_years_and_now_comes_last():
    saga, covenant = _saga()
    ch.eras(covenant).extend(
        [{"name": "The breaking", "year": 1200}, {"name": "The Founders", "year": 1115}]
    )
    lines = ch.shown(saga, covenant).lines
    groups: dict[str, list[str]] = {}
    current = ""
    for name, years, row in lines:
        if row is None:
            current = f"{name} {years}".strip()
            groups[current] = []
        else:
            groups[current].append(row.text)
    assert groups == {
        "Earlier": ["The tower rises"],
        "The Founders 1115-1199": ["The five come"],
        "The breaking from 1200": ["Trust breaks", "The last night"],
        "Now and ahead from Spring 1220": ["The pact, unpaid", "The scout comes"],
        "Undated": ["Once, long ago"],
    }


def test_delete_leaves_an_entry_out_hidden_and_shown_it_can_be_put_back():
    saga, covenant = _saga()
    ops = ch.covenant_ops(saga, covenant)[HISTORY_SECTION]
    key = next(
        i
        for i, r in enumerate(ch.shown(saga, covenant).rows)
        if r.text == "Trust breaks"
    )
    step = ops.remove(key)
    assert isinstance(step, Confirm)
    step.apply()
    assert covenant.history["left_out"] == ["1200|Autumn|Trust breaks"]
    # It stays where it is written, and is hidden from the history...
    assert any(e.name == "Trust breaks" for e in covenant.diary)
    assert "Trust breaks" not in [r.text for r in ch.shown(saga, covenant).rows]
    # ...until the Left Out block shows it, last, under Left out.
    ops = ch.covenant_ops(saga, covenant)
    shows = ops[HISTORY_VIEW_SECTION].edit(0)
    assert isinstance(shows, Form)
    shows.apply({"show_left_out": True})
    ops = ops[HISTORY_SECTION]
    name, _years, _row = [
        line for line in ch.shown(saga, covenant).lines if line[2] is None
    ][-1]
    assert name == ch.LEFT_OUT
    again = ch.shown(saga, covenant).rows.index(
        next(r for r in ch.shown(saga, covenant).rows if r.text == "Trust breaks")
    )
    ops.remove(again).apply()
    assert covenant.history["left_out"] == []


def test_edit_opens_the_entry_where_it_is_written():
    saga, covenant = _saga()
    ops = ch.covenant_ops(saga, covenant)[HISTORY_SECTION]
    rows = ch.shown(saga, covenant).rows
    by_text = {r.text: i for i, r in enumerate(rows)}
    assert isinstance(ops.edit(by_text["Trust breaks"]), Form)
    assert ops.edit(by_text["The scout comes"]).title == "Edit a Calendar Entry"
    assert isinstance(ops.edit(by_text["The five come"]), Form)


def test_an_era_needs_a_year_no_other_era_begins_in():
    saga, covenant = _saga()
    ops = ch.covenant_ops(saga, covenant)[ERAS_SECTION]
    add = ops.add()
    assert isinstance(add, Form)
    add.apply({"name": "The Founders", "year": 1115})
    assert covenant.history["eras"] == [{"name": "The Founders", "year": 1115}]
    again = ops.add()
    assert again.validate is not None
    assert again.validate({"name": "Another", "year": 1115}) == (
        "An era already begins in 1115."
    )


def test_a_saved_history_loads_and_a_bad_one_is_reported():
    data = {"id": "c", "saga_id": "s", "name": "C"}
    assert Covenant.from_dict(data).history == {}
    loaded = Covenant.from_dict(
        {**data, "history": {"eras": [{"name": "A", "year": 1100}], "left_out": ["k"]}}
    )
    assert loaded.history == {"eras": [{"name": "A", "year": 1100}], "left_out": ["k"]}
    try:
        Covenant.from_dict({**data, "history": {"eras": [{"name": "A"}]}})
    except ValueError as error:
        assert "era without a year" in str(error)
    else:
        raise AssertionError("an era without a year should be reported")


def test_the_tab_lists_its_sections():
    saga, covenant = _saga()
    holder = manors_of(covenant)
    assert ch.history_title(saga, holder) == "History (7)"
    assert "7 entries from 5 records" in ch.history_header(saga, holder)
    assert [part.section_id for part in ch.TAB.parts()] == [
        HISTORY_SECTION,
        HISTORY_VIEW_SECTION,
        ERAS_SECTION,
    ]


def test_the_source_filter_hides_a_records_entries_unless_another_keeps_them():
    saga, covenant = _saga()
    holder = manors_of(covenant)
    chips = ch.history_toggles(saga, holder)
    assert [c.label for c in chips] == [
        f"{covenant.name}'s Diary",
        "The Cave",
        "The Stone House",
        "The Founders",
        "Ahead",
    ]
    assert all(c.on for c in chips)
    next(c for c in chips if c.label == "The Cave").flip()
    assert covenant.history["hidden_sources"] == ["place:cave"]
    texts = [r.text for r in ch.shown(saga, covenant).rows]
    # The Founders keep the last night too, so it stays; Once, long ago goes.
    assert "The last night" in texts
    assert "Once, long ago" not in texts
    assert "not showing The Cave" in ch.history_header(saga, holder)
    # The terminal's form sets the same, a tick per record.
    form = ch.edit_view(saga, holder)
    assert isinstance(form, Form)
    ticks = {f.label: f.value for f in form.fields()}
    assert ticks["Entries of The Cave"] is False
    form.apply({"show_left_out": False, "from_1": True, "from_3": False})
    assert covenant.history["hidden_sources"] == ["place:founders"]
