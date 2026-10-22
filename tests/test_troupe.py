"""The Troupe's core (troupe.py): who the player characters are, and the
stars a reader keeps in this computer's settings, filed by saga."""

from __future__ import annotations

from ars_magica_manager import settings, troupe
from ars_magica_manager.models import Character, Covenant, Neighbour, Saga
from ars_magica_manager.troupe import Bookmark


def _saga() -> Saga:
    """Two covenants, the troupe's listed second; three players' characters
    (one in each covenant and one in none) and one nobody plays."""
    home = Covenant(id="home", saga_id="s", name="Fengheld", played=True)
    rival = Covenant(id="rival", saga_id="s", name="Durenmar", played=False)
    people = [
        Character(id="npc", name="Gunther", type="grog", covenant_id="home"),
        Character(id="pc2", name="Aurelia", type="magus", covenant_id="rival"),
        Character(id="pc1", name="Leandro", type="magus", covenant_id="home"),
        Character(id="pc3", name="Wandering Tom", type="companion"),
    ]
    for character, player in zip(people[1:], ("Hedda", "Sam", "Kim"), strict=True):
        character.background.player = player
    return Saga(
        id="s",
        name="Saga",
        covenants=[rival, home],
        characters=people,
        neighbours=[Neighbour(id="n1", name="The Bishop")],
    )


def test_player_characters_are_grouped_troupe_covenant_first():
    groups = troupe.player_characters(_saga())
    assert [
        (cov.name if cov else None, [c.name for c in people]) for cov, people in groups
    ] == [
        ("Fengheld", ["Leandro"]),
        ("Durenmar", ["Aurelia"]),
        (None, ["Wandering Tom"]),
    ]


def test_a_signed_in_player_makes_a_player_character_too():
    saga = _saga()
    saga.characters[0].background.player_id = "p1"
    names = [c.name for _, people in troupe.player_characters(saga) for c in people]
    assert "Gunther" in names


def test_the_troupe_covenants_are_the_played_ones():
    assert [c.name for c in troupe.troupe_covenants(_saga())] == ["Fengheld"]


def test_a_bookmark_goes_in_and_out_and_is_kept_by_saga():
    troupe.set_bookmarked("s", "neighbour", "n1", True)
    troupe.set_bookmarked("other", "creature", "c1", True)
    troupe.set_bookmarked("s", "neighbour", "n1", True)  # already in: once
    assert troupe.is_bookmarked("s", "neighbour", "n1")
    assert troupe.bookmarks("other") == [Bookmark("creature", "c1")]
    assert settings.load_settings()[troupe.BOOKMARKS] == {
        "s": [["neighbour", "n1"]],
        "other": [["creature", "c1"]],
    }
    troupe.set_bookmarked("s", "neighbour", "n1", False)
    assert troupe.bookmarks("s") == []
    assert settings.load_settings()[troupe.BOOKMARKS] == {"other": [["creature", "c1"]]}


def test_bookmarks_keep_the_other_settings():
    settings.update_settings(theme="dark")
    troupe.set_bookmarked("s", "covenant", "rival", True)
    assert settings.load_settings()["theme"] == "dark"


def test_a_damaged_bookmark_entry_is_left_out():
    settings.update_settings(
        bookmarks={"s": [["neighbour", "n1"], ["dragon", "x"], "junk", ["covenant", 3]]}
    )
    assert troupe.bookmarks("s") == [Bookmark("neighbour", "n1")]
    settings.update_settings(bookmarks="junk")
    assert troupe.bookmarks("s") == []


def test_other_bookmarks_leave_out_what_the_troupe_shows_and_what_is_gone():
    saga = _saga()
    for kind, record_id in (
        ("character", "pc1"),  # a player character: shown already
        ("covenant", "home"),  # a troupe covenant: shown already
        ("neighbour", "gone"),  # no longer in the saga
        ("neighbour", "n1"),
        ("character", "npc"),
        ("covenant", "rival"),
    ):
        troupe.set_bookmarked("s", kind, record_id, True)
    assert [
        (kind, [r.name for r in records])  # type: ignore[attr-defined]
        for kind, records in troupe.other_bookmarks(saga)
    ] == [
        ("character", ["Gunther"]),
        ("covenant", ["Durenmar"]),
        ("neighbour", ["The Bishop"]),
    ]
