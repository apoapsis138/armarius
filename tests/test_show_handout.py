"""Showing a written Handout (shows.py, forms/show.py): each Show freezes
a copy of its title, Stationery, text and pictures; editing the Handout
later changes no copy; a reader draws the copy only through the tag
parser; it is a "written" Handout in each Player's list, never opened as
a live record."""

from __future__ import annotations

from typing import cast

import pytest
from test_shows import PICTURE, _begun, _show

from ars_magica_manager import (
    chronicle,
    handout_arrangement,
    handout_layout,
    handout_list,
    handouts,
    paths,
    shows,
    viewing,
    virtual_tabletop,
)
from ars_magica_manager.actions import ActionFacts
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.form_spec import DialogField
from ars_magica_manager.forms import more, player_handouts
from ars_magica_manager.forms import show as show_forms
from ars_magica_manager.forms.more import rules as more_rules
from ars_magica_manager.models import (
    PROCLAMATION,
    VELLUM,
    Handout,
    HandoutPicture,
    Saga,
    Session,
)
from ars_magica_manager.sections import HANDOUTS_SECTION

HOST = viewing.HOST
LETTER = "[heading] To the Covenant\n[initial] Greetings, friends.\n[picture 1]"


def _letter(saga: Saga) -> Handout:
    """A proclamation with the Rhine map and a picture not on this
    computer."""
    letter = Handout(
        "letter",
        "The Count's Letter",
        stationery=PROCLAMATION,
        text=LETTER,
        pictures=[
            HandoutPicture(paths.MAPS, "rhine.png"),
            HandoutPicture(paths.HANDOUTS, "gone.png"),
        ],
    )
    saga.handouts = [letter]
    return letter


def _shown_letter(
    to: tuple[str, ...] = (),
) -> tuple[Saga, Session, chronicle.Chronicle, Handout, chronicle.Entry]:
    saga, session, book = _begun()
    letter = _letter(saga)
    entry = _show(
        book, saga, session, chronicle.ShowCall("A letter", handout="letter", to=to)
    )
    return saga, session, book, letter, entry


# -- the frozen copy --


def test_a_shown_handouts_copy_is_frozen_when_it_is_shown() -> None:
    saga, _session, _book, letter, entry = _shown_letter()
    letter.text, letter.stationery, letter.title = "Changed", VELLUM, "New title"
    (paths.data_dir() / paths.MAPS / "rhine.png").write_bytes(b"changed since")

    copy = shows.opened(saga.id, entry)

    assert copy.written and copy.stationery == PROCLAMATION
    assert copy.text == LETTER
    assert copy.pictures == (PICTURE, None)


def test_its_entry_names_the_handout_and_its_pictures_named_for_the_show() -> None:
    _saga, _session, _book, _letter, entry = _shown_letter()
    show_id = str(entry.body["show"])

    assert entry.body["handout"] == "letter"
    assert entry.body["ref"] == [] and entry.body["picture"] == ""
    assert entry.body["pictures"] == [f"{show_id}-1.png"]


def test_only_a_player_shown_may_fetch_its_pictures() -> None:
    saga, _session, _book, _letter, entry = _shown_letter(to=("ben",))
    [name] = entry.body["pictures"]

    assert shows.shows_picture(saga, name, "ben")
    assert not shows.shows_picture(saga, name, "ana")
    assert not shows.shows_picture(saga, f"{entry.body['show']}-2.png", "ben")


def test_a_handout_not_in_the_saga_or_with_a_record_too_isnt_shown() -> None:
    saga, session, _book = _begun()
    _letter(saga)
    why = shows.why_not_show

    assert why(saga, session, chronicle.ShowCall("T", handout="nope"), HOST) == (
        "Choose a record or picture to show."
    )
    both = chronicle.ShowCall("T", picture=("maps", "rhine.png"), handout="letter")
    assert why(saga, session, both, HOST) is not None
    assert why(saga, session, chronicle.ShowCall("T", handout="letter"), HOST) is None


def test_a_copy_with_a_stationery_the_app_doesnt_know_is_vellum() -> None:
    copy = shows.from_copy({"title": "T", "stationery": "papyrus", "text": "x"})

    assert copy.written and copy.stationery == VELLUM
    assert not shows.from_copy({"title": "T", "text": "x"}).written


def test_a_copys_pictures_are_bare_file_names_or_none() -> None:
    data = {"pictures": ["a-1.png", "../secret.png", 3, "", "b-2.png", "c", "d"]}

    assert shows.copy_pictures(data) == ["a-1.png", "", "", ""]
    assert shows.copy_pictures({"pictures": "a.png"}) == []


# -- reading the copy --


def _info(form: Form) -> str:
    [field] = cast(list[DialogField], form.fields())
    return str(field.value)


def test_the_copy_is_read_through_the_tag_parser_only() -> None:
    shown = shows.Shown(
        "T",
        "[heading] Hail\n[script] alert(1)\n<img src=http://x>\n[picture 2]",
        stationery=PROCLAMATION,
        pictures=(None,),
    )

    words = _info(show_forms.copy_form(shown))

    assert words.startswith("[$label]Stationery:[/] Proclamation")
    assert "[b]Hail[/]" in words and "[heading]" not in words
    assert "\\[script] alert(1)" in words
    assert "<img src=http://x>" in words
    assert "\\[picture 2]" in words  # it has only one picture


def test_a_copys_picture_is_named_by_its_place_alone() -> None:
    shown = shows.Shown("T", "[picture 1]", stationery=VELLUM, pictures=(None,))

    assert "(picture 1)" in _info(show_forms.copy_form(shown))


# -- in each Player's list --


def test_it_is_a_written_handout_in_the_list_and_filters_as_written() -> None:
    saga, _session, _book, _letter, _entry = _shown_letter(to=("ana",))

    [kept] = handout_list.of_player(saga, "ana")

    assert (kept.key, kept.kind) == ("handout:letter", handout_list.WRITTEN)
    [shown] = handout_arrangement.arranged([kept], handout_arrangement.Arrangement())
    facets = dict(player_handouts._facets(shown))  # pyright: ignore[reportPrivateUsage]
    assert facets["Kind"] == "Written"


def test_its_words_are_searched_without_its_tags() -> None:
    saga, _session, _book, _letter, _entry = _shown_letter(to=("ana",))

    assert handout_list.matching(saga, "ana", "greetings") == {"handout:letter"}
    assert handout_list.matching(saga, "ana", "heading") == set()


def test_no_live_record_is_offered_for_a_written_handout() -> None:
    saga, _session, _book, _letter, entry = _shown_letter()

    assert show_forms.live_record(saga, entry, HOST) is None


# -- Show from the Handouts list --


def test_show_from_the_list_starts_on_the_chosen_handout() -> None:
    saga, _session, _book = _begun()
    _letter(saga)
    handouts.choose_story(saga, "")

    form = show_forms.show_handout(saga, 0)

    assert isinstance(form, Form)
    fields = {f.key: f for f in cast(list[DialogField], form.fields())}
    assert fields["what"].value == "handout:letter"
    assert fields["title"].value == "The Count's Letter"
    assert ("Handout: The Count's Letter", "handout:letter") in fields["what"].options


def test_a_show_warns_the_storyguide_of_a_picture_it_cant_copy() -> None:
    """The letter's second picture isn't on this computer: the Show is
    made, and the storyguide told which picture each copy lacks."""
    saga, session, book = _begun()
    _letter(saga)
    form = show_forms.show_here(saga, session, saga.handouts[0])
    assert isinstance(form, Form)

    said = form.apply({"what": "handout:letter", "title": "A letter", "to": []})

    book.refresh()
    assert book.entries[-1].body["handout"] == "letter"
    assert said == [
        "Shown, but Picture 2 (gone.png) isn't on this computer or is too large "
        "to show: each copy has a blank box in its place."
    ]
    assert shows.missing_pictures(saga, "letter") == [2]


def test_a_show_of_a_handout_whose_pictures_are_all_here_says_nothing() -> None:
    saga, session, _book = _begun()
    _letter(saga).pictures.pop()
    form = show_forms.show_here(saga, session, saga.handouts[0])
    assert isinstance(form, Form)

    assert form.apply({"what": "handout:letter", "title": "A", "to": []}) == []


def test_an_untitled_handouts_show_is_titled_untitled_and_may_be_made() -> None:
    saga, session, _book = _begun()
    _letter(saga).title = ""

    form = show_forms.show_handout(saga, 0)

    assert isinstance(form, Form)
    fields = {f.key: f for f in cast(list[DialogField], form.fields())}
    assert fields["title"].value == show_forms.UNTITLED
    values = {"what": "handout:letter", "title": show_forms.UNTITLED, "to": []}
    assert form.validate is not None and form.validate(values) is None
    del session


def test_show_from_the_list_redraws_what_also_reveal_changes() -> None:
    """The form opened from a Handout may show a record instead, and Also
    reveal changes that record: the tree is redrawn, as Show's is."""
    entry = more.REGISTRY["show_handout"]
    assert entry.refresh == more.REGISTRY["show_at_session"].refresh


def test_the_copy_is_laid_out_for_each_front_end_naming_no_file() -> None:
    shown = shows.Shown(
        "A letter", LETTER + "\n[script] x", stationery=PROCLAMATION, pictures=(None,)
    )

    reading = show_forms.copy_form(shown).reading

    assert reading is not None and reading.pictures == (None,)
    assert reading.laid.stationery.name == PROCLAMATION
    [picture] = [b for b in reading.laid.blocks if b.kind == "picture"]
    assert picture.caption == handout_layout.COPY_CAPTION
    assert all("[heading]" not in b.text for b in reading.laid.blocks)
    assert show_forms.copy_form(shows.Shown("Hilda", "words")).reading is None


def test_show_from_the_list_needs_a_row_and_a_session_under_way() -> None:
    saga, session, _book = _begun()
    _letter(saga)

    assert isinstance(show_forms.show_handout(saga, None), Refuse)
    assert isinstance(show_forms.show_handout(saga, 5), Refuse)
    session.under_way = False
    assert show_forms.why_not_handout(saga, 0) == "No Session is under way."


class _Facts:
    """What the Show rule asks of the facts: the saga, and the row chosen."""

    def __init__(self, saga: Saga, row: int | None) -> None:
        self.saga, self.row = saga, row

    def chosen_row(self, _section: str) -> int | None:
        return self.row


@pytest.mark.parametrize("on", [True, False])
def test_show_is_offered_on_a_chosen_handout_while_the_tabletop_is_on(
    on: bool,
) -> None:
    saga, _session, _book = _begun()
    _letter(saga)
    virtual_tabletop.set_on(on)
    facts = cast(ActionFacts, _Facts(saga, 0))

    assert more_rules.shows_handout(facts, HANDOUTS_SECTION) is on
    assert not more_rules.shows_handout(facts, "section-players")
    assert not more_rules.shows_handout(
        cast(ActionFacts, _Facts(saga, None)), HANDOUTS_SECTION
    )
