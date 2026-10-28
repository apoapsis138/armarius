"""Open stories: the troupe's covenants' open Story Events, what each
concerns, the Region's list of them, the line in a character's
Connections, and growing one into a threat."""

from __future__ import annotations

from types import SimpleNamespace

from support import everything_saga

from ars_magica_manager import connections, open_stories, place_events, threats
from ars_magica_manager.forms import diary as diary_forms
from ars_magica_manager.forms import neighbour as neighbour_forms
from ars_magica_manager.models import STORY_EVENT, CovenantDiaryEntry
from ars_magica_manager.seasons import lab_apply
from ars_magica_manager.sections import REGION_STORIES_SECTION


def _saga():
    """The sample saga with two open stories in its troupe covenant's
    Diary: a salamander concerning Leandro, and one of the Region's."""
    saga = everything_saga()
    covenant = saga.covenants[0]
    covenant.played = True
    covenant.diary += [
        CovenantDiaryEntry(
            1220,
            "Summer",
            "A salamander in the lab",
            "It may want to become his familiar.",
            category=STORY_EVENT,
            status="Open",
            concerns="characters:mag1",
        ),
        CovenantDiaryEntry(
            1219,
            "Autumn",
            "Lights on the moor",
            category=STORY_EVENT,
            status="Open",
            concerns=open_stories.REGION,
        ),
        CovenantDiaryEntry(
            1219, "Winter", "Told already", category=STORY_EVENT, status="Resolved"
        ),
    ]
    return saga, covenant


def test_the_region_lists_the_open_stories_oldest_first():
    saga, covenant = _saga()
    rows = open_stories.grid(saga).rows
    names = [r[0] for r in rows]
    assert names.index("Lights on the moor") < names.index("A salamander in the lab")
    assert "Told already" not in names
    salamander = next(r for r in rows if r[0] == "A salamander in the lab")
    assert salamander[1:] == ["Leandro", covenant.name, "Summer 1220"]
    moor = next(r for r in rows if r[0] == "Lights on the moor")
    assert moor[1] == "The Region"


def test_a_story_of_a_covenant_the_troupe_doesnt_play_isnt_listed():
    saga, covenant = _saga()
    covenant.played = False
    assert open_stories.stories(saga) == []


def test_a_character_s_connections_name_his_open_stories():
    saga, covenant = _saga()
    leandro = saga.character("mag1")
    found = {f.label: f for f in connections.facts(saga, leandro)}
    fact = found["Open stories"]
    assert fact.value == f"A salamander in the lab ({covenant.name} Diary)"
    assert [r.id for r in fact.refs] == [covenant.id]
    alys = saga.character("comp1")
    assert "Open stories" not in {f.label for f in connections.facts(saga, alys)}


def test_the_concerns_field_offers_the_covenant_s_people_and_labs():
    saga, covenant = _saga()
    options = open_stories.concerns_options(saga, covenant)
    values = [v for _label, v in options]
    assert values[:2] == ["", open_stories.REGION]
    assert "characters:mag1" in values and "laboratories:lab1" in values


def test_editing_a_story_keeps_the_threat_it_grew_into():
    _unused, covenant = _saga()
    entry = covenant.diary[-3]
    entry.threat_id = "salamander"
    build = diary_forms.covenant_entry_from(covenant, entry)
    edited = build(
        {
            "year": 1220,
            "season": "Summer",
            "name": "A salamander in the lab",
            "category": STORY_EVENT,
            "status": "Open",
            "concerns": "characters:mag1",
        }
    )
    assert edited.threat_id == "salamander"
    assert edited.concerns == "characters:mag1"


def test_the_region_s_edit_opens_the_story_s_diary_entry():
    saga, _covenant = _saga()
    ops = neighbour_forms.region_ops(saga)[REGION_STORIES_SECTION]
    assert ops.add is None and ops.remove is None and ops.edit is not None
    form = ops.edit(0)
    values = {f.key: f.value for f in form.fields()}
    assert values["name"] == "Lights on the moor"
    assert values["concerns"] == open_stories.REGION


def test_growing_a_story_makes_a_threat_and_marks_it_grown():
    saga, covenant = _saga()
    row = next(
        i
        for i, s in enumerate(open_stories.stories(saga))
        if s.entry.name == "A salamander in the lab"
    )
    entry = open_stories.stories(saga)[row].entry
    form = open_stories.grow_form(saga, row)
    defaults = {f.key: f.value for f in form.fields()}
    assert defaults["name"] == "A salamander in the lab"
    form.apply(
        {
            "name": "The Salamander's Hunger",
            "antagonist": "A salamander",
            "moves": "A track",
            "dormant": "later",
        }
    )
    threat = saga.neighbour(entry.threat_id)
    assert threat is not None and threats.is_threat(threat)
    assert threat.name == "The Salamander's Hunger"
    assert threat.summary == "It may want to become his familiar."
    assert threats.moves(threat) == "A track" and threats.is_dormant(threat)
    assert threat.links[0].target_id == covenant.id
    assert entry.status == open_stories.GROWN
    assert "A salamander in the lab" not in [
        s.entry.name for s in open_stories.stories(saga)
    ]
    assert place_events.diary(threat)[-1]["text"].startswith(
        "The Salamander's Hunger: Grew from"
    )


def test_an_experiment_s_story_concerns_the_magus_and_a_disaster_s_the_covenant():
    saga, covenant = _saga()
    leandro = saga.character("mag1")
    lab = saga.laboratory("lab1")
    assert leandro is not None and lab is not None
    chart = SimpleNamespace(stories=["A salamander lingers", lab_apply.DISASTER_STORY])
    plan = SimpleNamespace(year=1220, season="Autumn")
    lab_apply._stories(saga, leandro, lab, plan, chart)  # type: ignore[arg-type]
    salamander, disaster = covenant.diary[-2:]
    assert salamander.concerns == "characters:mag1"
    assert disaster.concerns == ""
    assert open_stories.concerns_text(saga, covenant, disaster) == covenant.name
