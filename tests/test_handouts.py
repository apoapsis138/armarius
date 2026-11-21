"""Written Handouts (handouts.py): the storyguide writes them ahead in a
Handouts list in Saga content, each a title, a Stationery, text in the
app's markup with the handout tags, up to four pictures, who found it,
where, and the Story it belongs to. Only the storyguide holds them until
they are Shown."""

from dataclasses import asdict
from pathlib import Path

import pytest

from ars_magica_manager import (
    commands,
    handouts,
    packs,
    section_verbs,
    transfer,
    viewing,
)
from ars_magica_manager.forms import handouts as handout_forms
from ars_magica_manager.models import (
    PROCLAMATION,
    STATIONERY,
    STORY_EVENT,
    VELLUM,
    AtlasMap,
    Character,
    Covenant,
    CovenantDiaryEntry,
    Handout,
    HandoutPicture,
    Neighbour,
    Player,
    Saga,
)
from ars_magica_manager.paths import HANDOUTS, MAPS, PORTRAITS
from ars_magica_manager.seat_view import seat_view
from ars_magica_manager.sections import HANDOUTS_SECTION


def _saga() -> Saga:
    """Aelfric of Fengheld, the Drachenfels (a Place), a map with a
    picture, and an open story, The Black Tower."""
    saga = Saga(id="s", name="Saga")
    saga.players = [Player("ana", "Ana"), Player("sg", "Sue", "storyguide")]
    saga.covenants = [Covenant(id="c", saga_id="s", name="Fengheld", played=True)]
    saga.characters = [
        Character(
            id="aelfric",
            name="Aelfric",
            type="magus",
            covenant_id="c",
            portrait="aelfric.png",
        )
    ]
    saga.neighbours = [
        Neighbour(id="drachen", name="The Drachenfels", kind="place", realm="Magic")
    ]
    saga.maps = [AtlasMap(id="m", name="The Rhine", picture="rhine.png")]
    saga.covenants[0].diary = [
        CovenantDiaryEntry(
            1220, name="The Black Tower", category=STORY_EVENT, status="Open"
        )
    ]
    return saga


def _ops(saga: Saga) -> commands.SectionOps:
    return section_verbs.ops_of(saga, saga)[HANDOUTS_SECTION]


def _fields(step: object) -> dict:
    assert isinstance(step, commands.Form)
    return {f.key: f for f in step.fields()}


def _values(step: object) -> dict:
    return {k: f.value for k, f in _fields(step).items() if f.kind != "info"}


def _problem(step: object, values: dict) -> str | None:
    assert isinstance(step, commands.Form)
    given = {**_values(step), **values}
    return step.validate(given) if step.validate else None


def _answer(step: object, values: dict) -> object:
    assert isinstance(step, commands.Form)
    given = {**_values(step), **values}
    problem = step.validate(given) if step.validate else None
    assert problem is None, problem
    return step.apply(given)


def _add(saga: Saga, **values: object) -> Handout:
    add = _ops(saga).add
    assert add is not None
    _answer(add(), {"title": "A letter", **values})
    return saga.handouts[-1]


# -- the record --


def test_the_saga_keeps_handouts_and_older_saves_load_with_none():
    saga = _saga()
    saga.handouts = [
        Handout(
            "h",
            title="A letter",
            stationery=PROCLAMATION,
            text="[heading] Hear ye",
            pictures=[HandoutPicture(MAPS, "rhine.png")],
            found_by_id="aelfric",
            place_id="drachen",
        )
    ]
    again = Saga.from_dict(asdict(saga))
    assert again.handouts == saga.handouts
    del_data = asdict(saga)
    del del_data["handouts"]
    assert Saga.from_dict(del_data).handouts == []


def test_there_are_three_stationeries():
    assert STATIONERY == ("vellum", "sealed letter", "proclamation")


# -- the form --


def test_add_writes_a_handout_with_its_stationery_text_finder_place_and_story():
    saga = _saga()
    add = _ops(saga).add
    assert add is not None
    form = add()
    fields = _fields(form)
    assert list(fields) == [
        "title",
        "stationery",
        "text",
        "pictures",
        "found_by",
        "place",
        "story",
    ]
    assert fields["stationery"].value == VELLUM
    assert [v for _l, v in fields["found_by"].options] == ["aelfric"]
    assert [v for _l, v in fields["place"].options] == ["drachen"]
    assert [label for label, _v in fields["story"].options] == [
        "The Black Tower (Fengheld)"
    ]
    _answer(
        form,
        {
            "title": "The Count's Proclamation",
            "stationery": PROCLAMATION,
            "text": "[heading] Hear ye\nThe ford is closed.",
            "found_by": "aelfric",
            "place": "drachen",
            "story": fields["story"].options[0][1],
        },
    )
    (handout,) = saga.handouts
    assert handout.title == "The Count's Proclamation"
    assert handout.stationery == PROCLAMATION
    assert handout.text == "[heading] Hear ye\nThe ford is closed."
    assert (handout.found_by_id, handout.place_id) == ("aelfric", "drachen")
    assert handout.story_id == saga.covenants[0].diary[0].id != ""


def test_edit_opens_the_chosen_handout_as_it_is():
    saga = _saga()
    _add(saga, text="First words.")
    edit = _ops(saga).edit
    assert edit is not None
    form = edit(0)
    assert _values(form)["text"] == "First words."
    _answer(form, {"title": "A better letter"})
    assert saga.handouts[0].title == "A better letter"


def test_a_handout_needs_a_title():
    saga = _saga()
    add = _ops(saga).add
    assert add is not None
    assert _fields(add())["title"].required


def test_the_text_is_at_most_twenty_thousand_characters():
    saga = _saga()
    add = _ops(saga).add
    assert add is not None
    form = add()
    assert _problem(form, {"title": "x", "text": "a" * 20_000}) is None
    assert _problem(form, {"title": "x", "text": "a" * 20_001}) == (
        "A Handout's text is at most 20,000 characters (this is 20,001)."
    )


def test_the_text_keeps_the_character_rule():
    saga = _saga()
    add = _ops(saga).add
    assert add is not None
    problem = _problem(add(), {"title": "x", "text": "A seal \u200b here"})
    assert problem is not None and "U+200B" in problem
    problem = _problem(add(), {"title": f"A {chr(0x202E)} title", "text": ""})
    assert problem is not None and "U+202E" in problem


def test_a_handout_has_at_most_four_pictures():
    saga = _saga()
    add = _ops(saga).add
    assert add is not None
    form = add()
    four = [f"{MAPS}:{n}.png" for n in ("a", "b", "c", "d")]
    assert _problem(form, {"title": "x", "pictures": four}) is None
    assert _problem(form, {"title": "x", "pictures": [*four, f"{MAPS}:x.png"]}) == (
        "A Handout has at most 4 pictures."
    )


def test_pictures_come_from_those_in_the_saga():
    saga = _saga()
    saga.handouts = [Handout("old", pictures=[HandoutPicture(HANDOUTS, "seal.png")])]
    assert handouts.picture_choices(saga) == [
        ("The Rhine (map)", f"{MAPS}:rhine.png"),
        ("Aelfric (portrait)", f"{PORTRAITS}:aelfric.png"),
        ("seal.png (handout picture)", f"{HANDOUTS}:seal.png"),
    ]
    handout = _add(saga, pictures=[f"{MAPS}:rhine.png", f"{HANDOUTS}:seal.png"])
    assert handout.pictures == [
        HandoutPicture(MAPS, "rhine.png"),
        HandoutPicture(HANDOUTS, "seal.png"),
    ]


def test_a_new_picture_is_copied_into_the_handouts_folder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr("ars_magica_manager.paths.data_dir", lambda: tmp_path / "data")
    source = tmp_path / "seal.png"
    source.write_bytes(b"\x89PNG\r\n\x1a\n" + b"x" * 40)
    saga = _saga()
    handout = _add(saga, pictures=[handouts.new_picture_ref(source)])
    (picture,) = handout.pictures
    assert picture.folder == HANDOUTS and picture.name.endswith(".png")
    assert (tmp_path / "data" / HANDOUTS / picture.name).read_bytes() == (
        source.read_bytes()
    )


def test_a_picture_ref_that_isnt_a_picture_is_dropped():
    saga = _saga()
    handout = _add(
        saga,
        pictures=[f"{MAPS}:rhine.png", "sagas:x.png", f"{MAPS}:../up.png", "junk"],
    )
    assert handout.pictures == [HandoutPicture(MAPS, "rhine.png")]


# -- the list --


def test_delete_asks_first_and_takes_it_out():
    saga = _saga()
    _add(saga, title="A letter")
    remove = _ops(saga).remove
    assert remove is not None
    step = remove(0)
    assert isinstance(step, commands.Confirm)
    assert step.question == "Delete the Handout A letter?"
    step.apply()
    assert saga.handouts == []


def test_rows_name_each_handout_and_its_stationery():
    saga = _saga()
    _add(saga, title="A letter", stationery="sealed letter")
    assert _ops(saga).rows() == ["A letter (sealed letter)"]


def test_the_list_can_be_narrowed_to_one_story():
    saga = _saga()
    story = _fields(_ops(saga).add())["story"].options[0][1]  # type: ignore[misc]
    _add(saga, title="Of the tower", story=story)
    _add(saga, title="Of nothing")
    story_id = saga.handouts[0].story_id
    assert [h.title for h in handouts.listed(saga)] == ["Of the tower", "Of nothing"]
    assert [h.title for h in handouts.listed(saga, story_id)] == ["Of the tower"]
    assert handouts.story_filters(saga) == [("The Black Tower", story_id)]


def _two_stories(saga: Saga) -> str:
    """Of the tower, then Of nothing: the Black Tower's id."""
    story = _fields(_ops(saga).add())["story"].options[0][1]  # type: ignore[misc]
    _add(saga, title="Of nothing")
    _add(saga, title="Of the tower", story=story)
    return saga.handouts[1].story_id


def test_the_list_its_title_and_its_verbs_follow_the_chosen_story():
    saga = _saga()
    story_id = _two_stories(saga)
    handouts.choose_story(saga, "")
    assert handouts.title(saga) == "Handouts (2)"
    handouts.choose_story(saga, story_id)
    try:
        assert handouts.current_story(saga) == story_id
        assert [h.title for h in handouts.shown(saga)] == ["Of the tower"]
        assert handouts.title(saga) == "Handouts (1 of 2)"
        ops = _ops(saga)
        assert ops.rows() == ["Of the tower (vellum)"]
        assert ops.edit is not None and ops.remove is not None
        assert "Of the tower" in _fields(ops.edit(0))["title"].value  # type: ignore[operator]
        step = ops.remove(0)
        assert isinstance(step, commands.Confirm)
        assert step.question == "Delete the Handout Of the tower?"
    finally:
        handouts.choose_story(saga, "")


def test_a_story_since_gone_no_longer_narrows_the_list():
    saga = _saga()
    story_id = _two_stories(saga)
    handouts.choose_story(saga, story_id)
    saga.covenants[0].diary = []
    assert handouts.current_story(saga) == ""
    assert len(handouts.shown(saga)) == 2


def test_the_filter_form_offers_the_handouts_stories():
    saga = _saga()
    story_id = _two_stories(saga)
    form = handout_forms.filter_form(saga)
    (field,) = form.fields()
    assert field.options == [("The Black Tower", story_id)] and field.allow_blank
    try:
        form.apply({"story": story_id})
        assert handouts.current_story(saga) == story_id
        form.apply({"story": None})
        assert handouts.current_story(saga) == ""
    finally:
        handouts.choose_story(saga, "")


def test_the_detail_shows_the_text_under_its_stationery_and_names_pictures():
    saga = _saga()
    handout = _add(
        saga,
        title="A letter",
        stationery="sealed letter",
        text="[heading] To Aelfric\n[picture 1]\nCome **at once**.",
        pictures=[f"{MAPS}:rhine.png"],
        found_by="aelfric",
        place="drachen",
    )
    detail = handouts.detail(saga, handout)
    assert detail.splitlines()[:4] == [
        "[b]A letter[/]",
        "[$label]Stationery:[/] Sealed letter",
        "[$label]Found by:[/] Aelfric, at The Drachenfels",
        "[$label]Pictures:[/] 1. The Rhine (map)",
    ]
    assert "[b]To Aelfric[/]\n(picture 1: The Rhine)\nCome [b]at once[/b]." in detail


def test_a_finder_or_place_since_deleted_is_named_as_kept():
    saga = _saga()
    handout = Handout("h", title="x", found_by="Brother Anselm", place_name="Ford")
    assert "Found by:[/] Brother Anselm, at Ford" in handouts.detail(saga, handout)


# -- exports and Content packs --


def _written(saga: Saga) -> Handout:
    """A letter Aelfric found at the Drachenfels, of The Black Tower."""
    story = _fields(_ops(saga).add())["story"].options[0][1]  # type: ignore[misc]
    return _add(
        saga,
        title="A letter",
        text="[heading] To Aelfric",
        pictures=[f"{MAPS}:rhine.png"],
        found_by="aelfric",
        place="drachen",
        story=story,
    )


def test_a_whole_saga_export_carries_its_handouts():
    saga = _saga()
    written = _written(saga)
    target = Saga(id="dst", name="Target")
    plan = transfer.plan_import(target, transfer.export_saga_data(saga))
    assert "  1 written Handout" in transfer.preview(plan)
    transfer.apply(target, plan)
    (imported,) = target.handouts
    assert (imported.title, imported.text) == ("A letter", "[heading] To Aelfric")
    assert imported.pictures == [HandoutPicture(MAPS, "rhine.png")]
    assert handouts.finder_name(target, imported) == "Aelfric"
    assert target.character(imported.found_by_id) is not None
    assert handouts.place_name(target, imported) == "The Drachenfels"
    assert imported.story_id == written.story_id


def test_a_handout_whose_finder_or_story_isnt_here_keeps_their_names_only():
    saga = _saga()
    _written(saga)
    data = transfer.export_saga_data(saga)
    data["saga"]["characters"] = []
    data["saga"]["neighbours"] = []
    data["saga"]["covenants"][0]["diary"] = []
    data["links"][transfer.CHARACTER] = {"aelfric": "Aelfric"}
    target = Saga(id="dst", name="Target")
    transfer.apply(target, transfer.plan_import(target, data))
    (imported,) = target.handouts
    assert (imported.found_by_id, imported.found_by) == ("", "Aelfric")
    assert imported.place_id == ""
    assert imported.story_id == ""


def test_a_pack_takes_the_handouts_of_what_it_takes_once():
    saga = _saga()
    _written(saga)
    saga.handouts.append(Handout("stray", title="Of nowhere"))
    data = packs.pack_data(saga, "Fengheld", [], [saga.covenants[0]], [])
    assert [h["title"] for h in data["saga"]["handouts"]] == ["A letter"]
    assert "1 written Handout" in packs.summary(data)
    bare = packs.pack_data(
        saga, "Fengheld", [], [saga.covenants[0]], [], with_handouts=False
    )
    assert bare["saga"]["handouts"] == []
    target = Saga(id="dst", name="Target")
    transfer.apply(target, transfer.plan_import(target, data))
    again = transfer.plan_import(target, data)
    assert "Handout A letter: already here" in again.skipped
    transfer.apply(target, again)
    assert [h.title for h in target.handouts] == ["A letter"]


def test_a_handouts_own_pictures_travel_with_an_export():
    saga = _saga()
    saga.handouts = [Handout("h", pictures=[HandoutPicture(HANDOUTS, "seal.png")])]
    assert (HANDOUTS, "seal.png") in transfer.pictures_named(
        transfer.export_saga_data(saga)
    )


# -- who may hold them --


def test_handouts_are_the_storyguides_until_shown():
    assert "section-handouts" in viewing.STORYGUIDE_ONLY
    assert "tab-content-handouts" in viewing.STORYGUIDE_ONLY


def test_a_players_seat_is_sent_no_handout_but_the_storyguides_is():
    saga = _saga()
    saga.handouts = [Handout("h", title="Secret letter")]
    ana = saga.players[0]
    assert seat_view(saga, viewing.viewer_for(ana, hosts=False)).handouts == []
    assert seat_view(saga, viewing.STORYGUIDE_VIEWER).handouts == saga.handouts
