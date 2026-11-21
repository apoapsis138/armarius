"""Set Scene and End Scene's core (forms/scene_verbs.py): what may be set,
where the form starts, handing the call to the Table, and who is offered
the More actions."""

from __future__ import annotations

from fake_table import FakeTable
from test_scene_play import HOST, _begun, _set

from ars_magica_manager import (
    chronicle,
    commands,
    references,
    scene_play,
    scenes,
    virtual_tabletop,
)
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.forms import more
from ars_magica_manager.forms import page as page_forms
from ars_magica_manager.forms import scene_verbs as scene_forms
from ars_magica_manager.sections import SESSION_INFO_SECTION
from ars_magica_manager.where import Where


def _values(form: commands.Form, **given: object) -> dict[str, object]:
    values = {f.key: f.value for f in form.fields() if f.kind != "info"}
    values.update(given)
    return values


def _options(form: commands.Form) -> list[str]:
    field = next(f for f in form.fields() if f.key == "scene")
    return [value for _label, value in field.options]


def test_the_form_starts_on_the_next_prepared_scene_and_hands_it_to_the_table() -> None:
    saga, session, book = _begun()
    _set(book, saga, session, "u-hill")
    table = FakeTable()
    form = scene_forms.set_form(saga, session, HOST, table, book)
    values = _values(form, tell_aura=True)

    assert _options(form) == ["u-ford", "u-home"]  # not the one playing
    assert values["scene"] == "u-home"
    assert form.validate is not None and form.validate(values) is None
    form.apply(values)
    assert table.scenes_set == [chronicle.SceneCall("u-home", tell_aura=True)]


def test_a_played_scene_is_offered_to_set_again() -> None:
    saga, session, book = _begun()
    _set(book, saga, session, "u-ford")
    _set(book, saga, session, "u-hill")
    form = scene_forms.set_form(saga, session, HOST, FakeTable(), book)
    labels = [label for label, _v in next(f for f in form.fields()).options]
    assert any("set it again" in label for label in labels)


def test_the_form_tells_the_storyguide_the_aura_it_would_tell() -> None:
    saga, session, book = _begun()
    form = scene_forms.set_form(saga, session, HOST, FakeTable(), book)
    assert form.live is not None
    assert form.live({"scene": "u-ford"}) == "Its aura: Faerie 2"


def test_a_player_is_refused_and_the_table_is_never_asked() -> None:
    saga, session, book = _begun()
    table = FakeTable()
    form = scene_forms.set_form(saga, session, "ana", table, book)
    assert form.validate is not None
    assert form.validate(_values(form)) == "Only the Session's storyguide sets a Scene."


def test_set_scene_says_why_there_is_nothing_to_set() -> None:
    saga, session, book = _begun()
    uses = session.scenes
    session.scenes = []
    assert scene_forms.why_not_set_here(saga, session) == (
        "Load a Scene into the Session first."
    )
    session.scenes = uses[:1]
    _set(book, saga, session, "u-ford")
    assert scene_forms.why_not_set_here(saga, session) == (
        "The only Scene left to set is playing: load another."
    )
    saga.scenes = saga.scenes[1:]
    assert "deleted from the library" in str(
        scene_forms.why_not_set_here(saga, session)
    )


def test_end_scene_asks_first_then_ends_the_one_playing() -> None:
    saga, session, book = _begun()
    assert isinstance(scene_forms.end_here(saga, session), commands.Refuse)
    _set(book, saga, session, "u-ford")
    step = scene_forms.end_here(saga, session)
    assert isinstance(step, commands.Confirm)
    assert "The ford" in step.question
    step.apply()
    assert scene_play.playing(session, book) is None


def test_now_playing_names_the_scene_and_links_a_place_the_reader_may_open() -> None:
    saga, session, book = _begun()
    assert scene_forms.now_playing(saga, session, "ana", book) is None
    _set(book, saga, session, "u-home")
    found = scene_forms.now_playing(saga, session, "ana", book)
    assert found is not None
    assert (found.title, found.place) == ("Home", "Fengheld")
    assert found.place_link == references.Ref("covenants", "c", "Fengheld")
    assert not found.runs and found.to_show == ()
    _set(book, saga, session, "u-hill")  # a place the players don't know
    hill = scene_forms.now_playing(saga, session, "ana", book)
    assert hill is not None and hill.place_link is None
    scene_play.end_scene(book, saga, session, by=HOST)
    assert scene_forms.now_playing(saga, session, "ana", book) is None


def test_now_playing_offers_the_storyguide_a_show_for_each_thing_to_show() -> None:
    saga, session, book = _begun()
    saga.scenes[0].to_show = ["maps:m", "characters:aelfric", "neighbours:drachen"]
    _set(book, saga, session, "u-ford")
    found = scene_forms.now_playing(saga, session, HOST, book)
    assert found is not None and found.runs
    assert found.to_show == (
        ("The Rhine", ("maps", "rhine.png")),
        ("Aelfric", references.Ref("characters", "aelfric", "Aelfric")),
    )  # a Place has no page to copy yet


def test_the_more_actions_are_offered_as_the_scene_stands() -> None:
    saga, session, book = _begun()
    virtual_tabletop.set_on(True)

    def offered() -> set[str]:
        page = page_forms.page_at(
            saga, Where(NodeKind.SESSION, session.id), section=SESSION_INFO_SECTION
        )
        return {a for a in ("set_scene", "end_scene") if more.available(a, page)}

    assert offered() == {"set_scene"}
    _set(book, saga, session, "u-ford")
    assert offered() == {"set_scene", "end_scene"}
    for use in ("u-hill", "u-home"):
        _set(book, saga, session, use)
    scene_play.end_scene(book, saga, session, by=HOST)
    assert scenes.state(session, session.scenes[2], scene_play.now(session, book)) == (
        scenes.ENDED
    )
    assert offered() == {"set_scene"}
