"""Scenes: the saga's library of reusable Scenes (a place and its aura,
the actors usually there, a story, a map, what to show, notes) and each
Session's uses of them, loaded in order, each with its own state and who
is present; what each state lets change; moving a Prepared use to
another Session."""

from dataclasses import asdict

from ars_magica_manager import (
    commands,
    deletion,
    record_links,
    references,
    scenes,
    section_verbs,
    viewing,
)
from ars_magica_manager.models import (
    STORY_EVENT,
    AtlasMap,
    Casting,
    Character,
    Covenant,
    CovenantDiaryEntry,
    Creature,
    Neighbour,
    Player,
    Saga,
    Scene,
    SceneUse,
    Session,
)
from ars_magica_manager.sections import SCENES_SECTION, SESSION_SCENES_SECTION


def _saga() -> Saga:
    """Ana plays Aelfric tonight; Gus the grog, a wolf and Count Otto are
    in the saga too. The Drachenfels is a Magic 3 place with a Faerie 5
    regio level; Fengheld a covenant with a Magic 4 aura."""
    saga = Saga(id="s", name="Saga")
    saga.players = [Player("ana", "Ana"), Player("sg", "Sue", "storyguide")]
    saga.covenants = [
        Covenant(id="c", saga_id="s", name="Fengheld", played=True, aura=4)
    ]
    saga.characters = [
        Character(id="aelfric", name="Aelfric", type="magus", covenant_id="c"),
        Character(id="gus", name="Gus", type="grog", covenant_id="c"),
    ]
    saga.creatures = [Creature(id="wolf", name="Grey Wolf")]
    saga.neighbours = [
        Neighbour(
            id="drachen",
            name="The Drachenfels",
            kind="place",
            realm="Magic",
            details={
                "aura": 3,
                "levels": [{"name": "The Vine Terraces", "realm": "Faerie", "aura": 5}],
            },
        ),
        Neighbour(id="otto", name="Count Otto", kind="lord"),
    ]
    saga.maps = [AtlasMap(id="m", name="The Rhine", picture="rhine.png")]
    saga.covenants[0].diary = [
        CovenantDiaryEntry(
            1220, name="The Black Tower", category=STORY_EVENT, status="Open"
        )
    ]
    tonight = Session(
        "tonight", real_date="2026-11-21", castings=[Casting("ana", "aelfric")]
    )
    saga.sessions = [tonight, Session("later", real_date="2026-12-05")]
    return saga


def _form_values(step: object) -> dict:
    assert isinstance(step, commands.Form)
    return {f.key: f.value for f in step.fields() if f.kind != "info"}


def _fields(step: object) -> dict:
    assert isinstance(step, commands.Form)
    return {f.key: f for f in step.fields()}


def _answer(step: object, values: dict) -> object:
    assert isinstance(step, commands.Form)
    given = _form_values(step)
    given.update(values)
    problem = step.validate(given) if step.validate else None
    assert problem is None, problem
    return step.apply(given)


def _library(saga: Saga) -> commands.SectionOps:
    return section_verbs.ops_of(saga, saga)[SCENES_SECTION]


def _uses(saga: Saga, session: Session) -> commands.SectionOps:
    return section_verbs.ops_of(saga, session)[SESSION_SCENES_SECTION]


def _add_scene(saga: Saga, **values: object) -> Scene:
    add = _library(saga).add
    assert add is not None
    _answer(add(), {"title": "The ford", **values})
    return saga.scenes[-1]


# -- the library --


def test_the_saga_and_a_session_keep_scenes_and_older_saves_load_with_none():
    saga = _saga()
    saga.scenes = [Scene("x", title="The ford", regulars=["characters:gus"])]
    saga.sessions[0].scenes = [SceneUse("u", scene_id="x", present=["creatures:wolf"])]
    again = Saga.from_dict(asdict(saga))
    assert again.scenes == saga.scenes
    assert again.sessions[0].scenes == saga.sessions[0].scenes
    assert Session.from_dict({"id": "old"}).scenes == []


def test_a_scene_at_a_typed_place_keeps_its_typed_aura():
    saga = _saga()
    scene = _add_scene(saga, where=None, place_name="A glade", aura=2, realm="Faerie")
    assert (scene.place_name, scene.aura, scene.realm) == ("A glade", 2, "Faerie")
    assert scenes.place_text(saga, scene) == "A glade"
    assert _library(saga).rows() == ["The ford"]


def test_choosing_a_place_level_or_covenant_fills_in_its_aura_and_realm():
    saga = _saga()
    add = _library(saga).add
    assert add is not None
    where = _fields(add())["where"]
    assert where.fills is not None
    assert where.fills({"where": "place:drachen"}) == {"aura": 3, "realm": "Magic"}
    assert where.fills({"where": "place:drachen@1"}) == {"aura": 5, "realm": "Faerie"}
    assert where.fills({"where": "covenant:c"}) == {"aura": 4, "realm": "Magic"}


def test_a_scene_at_a_place_level_is_named_by_it_and_keeps_a_changed_aura():
    saga = _saga()
    scene = _add_scene(saga, where="place:drachen@1", aura=6)
    assert (scene.place_id, scene.place_level, scene.covenant_id) == ("drachen", 1, "")
    assert scene.aura == 6
    assert scenes.place_text(saga, scene) == (
        "The Drachenfels, Level 1: The Vine Terraces"
    )


def test_regulars_are_actors_characters_creatures_and_lords():
    saga = _saga()
    add = _library(saga).add
    assert add is not None
    regulars = _fields(add())["regulars"]
    assert regulars.items is not None
    choose = regulars.items.entry(None)
    assert isinstance(choose, commands.Choose)
    assert [c.value for c in choose.choices()] == [
        "characters:aelfric",
        "characters:gus",
        "creatures:wolf",
        "neighbours:otto",
    ]
    scene = _add_scene(saga, regulars=["characters:gus", "creatures:wolf"])
    assert scenes.actor_names(saga, scene.regulars) == ["Gus", "Grey Wolf"]


def test_a_scene_takes_a_story_a_map_and_what_to_show():
    saga = _saga()
    add = _library(saga).add
    assert add is not None
    fields = _fields(add())
    [(_label, story)] = fields["story"].options
    assert [v for _label, v in fields["picture"].options] == ["rhine.png"]
    to_show = fields["to_show"].items
    assert to_show is not None
    choose = to_show.entry(None)
    assert isinstance(choose, commands.Choose)
    offered = {c.value for c in choose.choices()}
    assert {"maps:m", "neighbours:otto", "covenants:c"} <= offered
    scene = _add_scene(
        saga, story=story, picture="rhine.png", to_show=["maps:m", "neighbours:otto"]
    )
    entry = saga.covenants[0].diary[0]
    assert entry.id and scene.story_id == entry.id
    assert scene.picture == "rhine.png"
    assert scene.to_show == ["maps:m", "neighbours:otto"]
    assert (record_links.MAPS, "rhine.png") in record_links.pictures(saga)


def test_deleting_a_record_forgets_it_in_the_scenes():
    saga = _saga()
    saga.scenes = [
        Scene(
            "a",
            title="Hill",
            place_id="drachen",
            place_level=1,
            regulars=["characters:gus", "creatures:wolf"],
            to_show=["neighbours:otto"],
        ),
        Scene("b", title="Home", covenant_id="c"),
    ]
    saga.sessions[0].scenes = [
        SceneUse("u", scene_id="a", present=["characters:gus", "characters:aelfric"])
    ]
    deletion.delete_character(saga, saga.characters[1])
    assert saga.scenes[0].regulars == ["creatures:wolf"]
    assert saga.sessions[0].scenes[0].present == ["characters:aelfric"]
    record_links.forget(saga, record_links.NEIGHBOURS, saga.neighbours[1])
    assert saga.scenes[0].to_show == []
    record_links.forget(saga, record_links.NEIGHBOURS, saga.neighbours[0])
    assert (saga.scenes[0].place_id, saga.scenes[0].place_level) == (None, 0)
    record_links.forget(saga, record_links.COVENANTS, saga.covenants[0])
    assert saga.scenes[1].covenant_id == ""


def test_deleting_a_scene_takes_out_its_planned_uses_but_not_one_played():
    saga = _saga()
    saga.scenes = [Scene("a", title="The ford"), Scene("b", title="The tower")]
    tonight, later = saga.sessions
    tonight.scenes = [SceneUse("u1", scene_id="a"), SceneUse("u2", scene_id="b")]
    later.scenes = [SceneUse("u3", scene_id="a")]
    remove = _library(saga).remove
    assert remove is not None
    step = remove(0)
    assert isinstance(step, commands.Confirm)
    assert "2 Sessions" in step.question
    step.apply()
    assert [s.id for s in saga.scenes] == ["b"]
    assert [u.id for u in tonight.scenes] == ["u2"] and later.scenes == []
    tonight.scenes[0].state = scenes.ENDED
    assert isinstance(remove(0), commands.Refuse)


def test_a_scenes_kinds_are_the_pages_and_rulers_the_saga_knows():
    """record_links sits below references, so it lists the kinds again:
    they must stay the same."""
    assert set(record_links.ACTORS) == set(references.RULER_KINDS)
    assert set(record_links.SHOWABLE) == {
        *references.KINDS.values(),
        record_links.MAPS_KIND,
    }


# -- loading Scenes into a Session --


def test_loading_a_scene_puts_tonights_cast_and_its_regulars_there():
    saga = _saga()
    saga.scenes = [Scene("a", title="Market day", regulars=["characters:gus"])]
    session = saga.sessions[0]
    add = _uses(saga, session).add
    assert add is not None
    choose = add()
    assert isinstance(choose, commands.Choose)
    assert [c.value for c in choose.choices()] == [scenes.NEW_SCENE, "a"]
    choose.apply("a")
    [use] = session.scenes
    assert (use.scene_id, use.state) == ("a", scenes.PREPARED)
    assert use.present == ["characters:aelfric", "characters:gus"]
    assert _uses(saga, session).rows() == ["Market day"]


def test_a_new_scene_made_on_the_session_joins_the_library_and_is_loaded():
    saga = _saga()
    session = saga.sessions[0]
    add = _uses(saga, session).add
    assert add is not None
    choose = add()
    assert isinstance(choose, commands.Choose)
    form = choose.apply(scenes.NEW_SCENE)
    _answer(form, {"title": "A glade", "where": None, "place_name": "A glade"})
    [scene] = saga.scenes
    [use] = session.scenes
    assert use.scene_id == scene.id and scene.title == "A glade"


def test_the_same_scene_can_be_loaded_into_many_sessions_and_twice_in_one():
    saga = _saga()
    saga.scenes = [Scene("cov", title="Covenant business")]
    tonight, later = saga.sessions
    for session in (tonight, tonight, later):
        add = _uses(saga, session).add
        assert add is not None
        choose = add()
        assert isinstance(choose, commands.Choose)
        choose.apply("cov")
    assert [u.scene_id for u in tonight.scenes] == ["cov", "cov"]
    assert len({u.id for u in tonight.scenes}) == 2
    assert [u.scene_id for u in later.scenes] == ["cov"]


def test_editing_a_use_changes_who_is_present_this_time():
    saga = _saga()
    saga.scenes = [Scene("a", title="The ford")]
    session = saga.sessions[0]
    session.scenes = [SceneUse("u", scene_id="a", present=["characters:aelfric"])]
    edit = _uses(saga, session).edit
    assert edit is not None
    form = edit(0)
    fields = _fields(form)
    assert fields["present_aelfric"].value is True
    assert fields["also_present"].value == []
    _answer(form, {"present_aelfric": False, "also_present": ["creatures:wolf"]})
    assert session.scenes[0].present == ["creatures:wolf"]


def test_comes_after_puts_a_prepared_use_in_its_place():
    saga = _saga()
    saga.scenes = [Scene("a", title="A"), Scene("b", title="B"), Scene("c", title="C")]
    session = saga.sessions[0]
    session.scenes = [SceneUse(x, scene_id=x) for x in ("a", "b", "c")]
    edit = _uses(saga, session).edit
    assert edit is not None
    assert _fields(edit(2))["after"].value == "b"
    _answer(edit(2), {"after": ""})
    assert [u.scene_id for u in session.scenes] == ["c", "a", "b"]


def test_edit_moves_a_prepared_use_to_another_planned_session():
    saga = _saga()
    saga.scenes = [Scene("a", title="The ford"), Scene("l", title="Already there")]
    tonight, later = saga.sessions
    saga.sessions.append(Session("past", played=True))
    later.scenes = [SceneUse("ul", scene_id="l")]
    tonight.scenes = [SceneUse("ua", scene_id="a")]
    edit = _uses(saga, tonight).edit
    assert edit is not None
    form = edit(0)
    assert [v for _l, v in _fields(form)["session"].options] == ["tonight", "later"]
    _answer(form, {"session": "later"})
    assert tonight.scenes == []
    assert [u.id for u in later.scenes] == ["ul", "ua"]


def test_a_playing_use_cannot_move_or_be_taken_out_but_who_is_there_can_change():
    saga = _saga()
    saga.scenes = [Scene("a", title="The ford")]
    session = saga.sessions[0]
    session.scenes = [SceneUse("u", scene_id="a", state=scenes.PLAYING)]
    ops = _uses(saga, session)
    assert ops.edit is not None and ops.remove is not None
    fields = _fields(ops.edit(0))
    assert "session" not in fields and "after" not in fields
    assert "also_present" in fields
    assert isinstance(ops.remove(0), commands.Refuse)


def test_an_ended_use_keeps_who_was_there_but_its_notes_can_change():
    saga = _saga()
    saga.scenes = [Scene("a", title="The ford")]
    session = saga.sessions[0]
    session.scenes = [
        SceneUse("u", scene_id="a", state=scenes.ENDED, present=["characters:gus"])
    ]
    ops = _uses(saga, session)
    assert ops.edit is not None and ops.remove is not None
    form = ops.edit(0)
    assert set(_form_values(form)) == {"notes"}
    _answer(form, {"notes": "They crossed at dawn."})
    assert session.scenes[0].notes == "They crossed at dawn."
    assert session.scenes[0].present == ["characters:gus"]
    assert isinstance(ops.remove(0), commands.Refuse)


def test_the_scenes_are_the_storyguides_alone():
    saga = _saga()
    assert viewing.reads(part=SCENES_SECTION)
    viewing.use(viewing.TABLE_VIEWER, saga)
    for part in (
        "tab-content-scenes",
        SCENES_SECTION,
        "tab-session-scenes",
        SESSION_SCENES_SECTION,
    ):
        assert not viewing.reads(part=part), part


def test_a_played_sessions_scenes_count_as_ended():
    saga = _saga()
    saga.scenes = [Scene("a", title="The ford")]
    session = saga.sessions[0]
    session.played = True
    session.scenes = [SceneUse("u", scene_id="a", present=["characters:gus"])]
    use = session.scenes[0]
    assert scenes.state_label(session, use) == "Ended"
    ops = _uses(saga, session)
    assert ops.edit is not None and ops.remove is not None
    assert set(_form_values(ops.edit(0))) == {"notes"}
    assert isinstance(ops.remove(0), commands.Refuse)
    remove = _library(saga).remove
    assert remove is not None
    assert isinstance(remove(0), commands.Refuse)


def test_a_played_scene_keeps_who_was_there_after_a_character_is_deleted():
    saga = _saga()
    saga.scenes = [Scene("a", title="The ford")]
    played, planned = saga.sessions
    for session in (played, planned):
        add = _uses(saga, session).add
        assert add is not None
        choose = add()
        assert isinstance(choose, commands.Choose)
        choose.apply("a")
        edit = _uses(saga, session).edit
        assert edit is not None
        _answer(edit(0), {"also_present": ["characters:gus"]})
    played.played = True
    deletion.delete_character(saga, saga.characters[1])
    assert "characters:gus" in played.scenes[0].present
    assert scenes.actor_names(saga, played.scenes[0].present, played.scenes[0]) == [
        "Aelfric",
        "Gus",
    ]
    assert "characters:gus" not in planned.scenes[0].present


def test_a_lunar_aura_fills_in_its_realm_and_no_realm_reads_as_none():
    saga = _saga()
    saga.neighbours[0].details["aura"] = 4
    saga.neighbours[0].realm = "Lunar"
    add = _library(saga).add
    assert add is not None
    fields = _fields(add())
    assert fields["where"].fills is not None
    filled = fields["where"].fills({"where": "place:drachen"})
    assert filled == {"aura": 4, "realm": "Lunar"}
    assert "Lunar" in [v for _l, v in fields["realm"].options]
    assert scenes.aura_text(Scene("x", aura=2)) == "2, no realm"
    assert scenes.aura_text(Scene("x")) == "none"


def test_a_use_in_a_session_not_planned_names_its_session_and_a_move_goes_last():
    saga = _saga()
    saga.scenes = [Scene("a", title="A"), Scene("b", title="B")]
    tonight, later = saga.sessions
    tonight.under_way = True
    later.scenes = [SceneUse("l", scene_id="b")]
    tonight.scenes = [SceneUse("u", scene_id="a")]
    edit = _uses(saga, tonight).edit
    assert edit is not None
    options = _fields(edit(0))["session"].options
    assert [v for _l, v in options] == ["tonight", "later"]
    _answer(edit(0), {"session": "later", "after": ""})
    assert [u.id for u in later.scenes] == ["l", "u"]


def test_taking_out_a_prepared_use_asks_first_and_keeps_the_scene():
    saga = _saga()
    saga.scenes = [Scene("a", title="The ford")]
    session = saga.sessions[0]
    session.scenes = [SceneUse("u", scene_id="a")]
    remove = _uses(saga, session).remove
    assert remove is not None
    step = remove(0)
    assert isinstance(step, commands.Confirm)
    step.apply()
    assert session.scenes == [] and [s.id for s in saga.scenes] == ["a"]
