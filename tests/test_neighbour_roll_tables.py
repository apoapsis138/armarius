"""Roll tables on a threat, a faction and a lord: the place's Roll Tables
tab, kept the same way, and a threat's roll leaving its clock alone."""

from __future__ import annotations

import copy
import random
from pathlib import Path

import pytest
from support import everything_saga

from ars_magica_manager import (
    actions,
    lords,
    neighbours,
    packs,
    place_events,
    threats,
    transfer,
)
from ars_magica_manager.commands import Confirm
from ars_magica_manager.models import Neighbour, Saga
from ars_magica_manager.sections import TABLES_SECTION

ROWS = "1-5: Riders on the road\n6+: A letter under the door\nbotch: Silence"


def _neighbour(saga: Saga, key: str) -> Neighbour:
    return next(n for n in saga.neighbours if n.id == key)


def _with_table(record: Neighbour) -> None:
    record.details["tables"] = [
        {"name": "This season", "die": "Simple die", "rows": ROWS}
    ]


@pytest.mark.parametrize("key", ["crown", "coven", "gottfried"])
def test_threats_factions_and_lords_take_the_roll_tables_tab(key: str):
    saga = everything_saga()
    record = _neighbour(saga, key)
    tabs = neighbours.kind_of(record).more
    titles = [t.title for t in tabs]
    assert "Roll Tables" in titles
    # The tables come just before the Diary, as a place's do.
    assert titles.index("Roll Tables") + 1 == titles.index("Diary")
    tab = next(t for t in tabs if t.title == "Roll Tables")
    assert [entry.section_id for entry in tab.lists] == [TABLES_SECTION]
    _with_table(record)
    before = len(place_events.diary(record))
    command = place_events.roll_table(saga, record, 0, random.Random(3))
    assert isinstance(command, Confirm)
    command.apply()
    assert len(place_events.diary(record)) == before + 1
    entry = place_events.diary(record)[-1]
    assert entry["text"].startswith("This season: rolled ")
    assert entry["season"] == saga.current_season
    assert record.details["tables"][0]["last"].startswith("Spring 1220: ")


def test_a_lords_roll_tables_sit_beside_his_diary_after_standing():
    assert lords.TABLES_TAB.after_standing and lords.DIARY_TAB.after_standing
    assert lords.TABLES_TAB.lists == place_events.TABLES_TAB.lists
    assert not place_events.TABLES_TAB.after_standing


def test_a_threats_roll_colours_its_stage_and_never_moves_its_clock():
    saga = everything_saga()
    threat = _neighbour(saga, "crown")
    threat.details["moves"] = "A track"
    threat.details["position"] = 1
    for at, stage in enumerate(threats.stages(threat), start=1):
        stage["at"] = at
    _with_table(threat)
    reached = threats.reached(saga, threat).current
    assert reached is not None
    kept = copy.deepcopy(
        {k: v for k, v in threat.details.items() if k not in ("tables", "diary")}
    )
    clock = threats.clock(saga, threat)
    for seed in range(20):
        command = place_events.roll_table(saga, threat, 0, random.Random(seed))
        assert isinstance(command, Confirm)
        assert "the threat's clock doesn't move" in command.question
        command.apply()
    assert threats.clock(saga, threat) == clock
    assert threats.reached(saga, threat).current == reached
    assert {
        k: v for k, v in threat.details.items() if k not in ("tables", "diary")
    } == kept
    assert place_events.diary(threat)[-1]["text"].endswith(f"(at {reached['title']})")


def test_a_faction_or_lord_roll_names_no_stage():
    saga = everything_saga()
    coven = _neighbour(saga, "coven")
    _with_table(coven)
    command = place_events.roll_table(saga, coven, 0, random.Random(1))
    assert isinstance(command, Confirm)
    assert "clock" not in command.question
    command.apply()
    assert "(at " not in place_events.diary(coven)[-1]["text"]


def test_a_storyguides_note_closes_a_row_and_nowhere_else():
    split = place_events.split_note
    assert split("The letters curse. (SG: False: they honour Abnoba.)") == (
        "The letters curse.",
        "False: they honour Abnoba.",
    )
    assert split("A hare") == ("A hare", "")
    assert split("(SG: Only for you)") == ("", "Only for you")
    mid = "A (SG: not a note) sign on the door"
    assert split(mid) == (mid, "")
    assert place_events.player_text("Wolves (SG: they are Hugo's)") == "Wolves"


def test_a_rows_note_is_kept_apart_and_a_botch_row_takes_one():
    rows = place_events.parse_rows(
        "1-3: Nothing\n"
        "4+: The letters on the walls curse whoever reads them. "
        "(SG: False: they honour Abnoba.)\n"
        "botch: The mist closes (SG: the faerie is watching)"
    )
    assert rows is not None
    plain, cursed, botch = rows
    assert (plain.result, plain.note) == ("Nothing", "")
    assert cursed.result == "The letters on the walls curse whoever reads them."
    assert cursed.note == "False: they honour Abnoba."
    assert botch.botch and botch.result == "The mist closes"
    assert botch.note == "the faerie is watching"


def _roll_one(rows: str, die: str = "d10") -> tuple[Confirm, Neighbour]:
    saga = everything_saga()
    record = _neighbour(saga, "coven")
    record.details["tables"] = [{"name": "Rumours", "die": die, "rows": rows}]
    command = place_events.roll_table(saga, record, 0, random.Random(0))
    assert isinstance(command, Confirm)
    return command, record


def test_the_roll_shows_the_note_and_the_diary_leaves_it_out():
    command, record = _roll_one("1-10: The letters curse. (SG: False: Abnoba.)")
    assert "(SG: False: Abnoba.)" in command.question
    assert "The letters curse." in command.question
    command.apply()
    text = place_events.diary(record)[-1].get("text", "")
    assert text.endswith(", The letters curse.")
    assert "SG" not in text and "Abnoba" not in text
    assert "Abnoba" not in record.details["tables"][0]["last"]


def test_a_row_without_a_note_rolls_as_before():
    command, record = _roll_one("1-10: A hare")
    assert "(SG:" not in command.question
    command.apply()
    text = place_events.diary(record)[-1].get("text", "")
    assert text.startswith("Rumours: rolled ") and text.endswith(", A hare")


def test_a_botch_rows_note_shows_on_the_roll_only():
    rows = "0+: Nothing\nbotch: Fire in the mill (SG: Hugo set it)"
    for seed in range(400):
        saga = everything_saga()
        record = _neighbour(saga, "coven")
        record.details["tables"] = [
            {"name": "Rumours", "die": "Stress die", "rows": rows}
        ]
        command = place_events.roll_table(saga, record, 0, random.Random(seed))
        assert isinstance(command, Confirm)
        if "a botch" in command.question:
            break
    else:
        pytest.fail("no botch in 400 rolls")
    assert "(SG: Hugo set it)" in command.question
    command.apply()
    text = place_events.diary(record)[-1].get("text", "")
    assert text.endswith("rolled a botch, Fire in the mill")


def test_a_row_that_is_only_a_note_writes_just_the_roll():
    command, record = _roll_one("1-10: (SG: nothing they notice)")
    assert "(SG: nothing they notice)" in command.question
    command.apply()
    text = place_events.diary(record)[-1].get("text", "")
    assert text.startswith("Rumours: rolled ") and "notice" not in text
    assert not text.endswith(", ")


def test_mores_roll_follows_the_section_not_the_kind():
    assert actions.MORE_SECTIONS["roll_table"] == TABLES_SECTION


RUMOURS = [
    {"name": "Rumours: the miller", "die": "d6", "rows": "1-3: Wolves\n4+: A stranger"},
    {"name": "Rumours: the priest", "die": "d10", "rows": "1-10: A sin confessed"},
    {"name": "Rumours: the reeve", "die": "Stress die", "rows": "0+: Tax\nbotch: Fire"},
]


@pytest.mark.parametrize("key", ["crown", "coven", "gottfried"])
def test_several_tables_are_listed_and_each_rolls_its_own(key: str):
    saga = everything_saga()
    record = _neighbour(saga, key)
    record.details["tables"] = copy.deepcopy(RUMOURS)
    grid = place_events.tables_grid(saga, record)
    assert [row[0] for row in grid.rows] == [t["name"] for t in RUMOURS]
    assert place_events.tables_title(saga, record) == "Roll Tables (3)"
    for index in (2, 0, 1):
        command = place_events.roll_table(saga, record, index, random.Random(index))
        assert isinstance(command, Confirm)
        command.apply()
    written = [e.get("text", "") for e in place_events.diary(record)[-3:]]
    assert [w.split(":")[0] + ":" + w.split(":")[1] for w in written] == [
        "Rumours: the reeve",
        "Rumours: the miller",
        "Rumours: the priest",
    ]
    assert "A sin confessed" in written[2]
    assert all(t.get("last") for t in record.details["tables"])


def test_tables_of_a_threat_faction_and_lord_survive_export_and_import(tmp_path: Path):
    saga = everything_saga()
    chosen = [_neighbour(saga, key) for key in ("crown", "coven", "gottfried")]
    for record in chosen:
        record.details["tables"] = copy.deepcopy(RUMOURS)
    path = packs.write(
        tmp_path / "rumours.json", packs.pack_data(saga, "Rumours", [], [], chosen)
    )
    data = transfer.read(path)
    target = Saga(id="dst", name="Target")
    transfer.apply(target, transfer.plan_import(target, data))
    for record in chosen:
        landed = next(n for n in target.neighbours if n.name == record.name)
        assert landed.kind == record.kind
        assert landed.details["tables"] == RUMOURS
        command = place_events.roll_table(target, landed, 1, random.Random(0))
        assert isinstance(command, Confirm)
        command.apply()
        assert (
            place_events.diary(landed)[-1]
            .get("text", "")
            .startswith("Rumours: the priest: rolled ")
        )
