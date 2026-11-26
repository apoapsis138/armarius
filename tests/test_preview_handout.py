"""Preview a written Handout from the Handouts list (forms/handouts.py):
the storyguide reads a saved Handout on its Stationery without opening
Edit, in the window a player's shown copy opens in; its pictures come from
the saga's own files, a missing one a placeholder naming it. Previewing
shows it to no one and writes nothing."""

from __future__ import annotations

import copy
from typing import cast

import pytest
from test_shows import PICTURE, _begun

from ars_magica_manager import (
    chronicle,
    handout_markup,
    handouts,
    paths,
    shows,
    viewing,
    virtual_tabletop,
)
from ars_magica_manager.actions import ActionFacts
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import handouts as handout_forms
from ars_magica_manager.forms import more
from ars_magica_manager.forms.more import rules as more_rules
from ars_magica_manager.models import PROCLAMATION, Handout, HandoutPicture, Saga
from ars_magica_manager.sections import HANDOUTS_SECTION

LETTER = "[heading] To the Covenant\n[initial] Greetings.\n[picture 1]\n[picture 2]"


def _letter(saga: Saga) -> Handout:
    """A proclamation placing the Rhine map and a picture not on this
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
    handouts.choose_story(saga, "")
    return letter


def _preview(saga: Saga) -> Form:
    form = handout_forms.preview_handout(saga, 0)
    assert isinstance(form, Form)
    return form


def test_preview_lays_the_handout_on_its_stationery_with_the_sagas_pictures() -> None:
    saga, _session, _book = _begun()
    _letter(saga)

    reading = _preview(saga).reading

    assert reading is not None
    assert reading.laid.title == "The Count's Letter"
    assert reading.laid.stationery.name == PROCLAMATION
    assert reading.pictures == (PICTURE, None)
    kinds = [b.kind for b in reading.laid.blocks]
    assert kinds == [
        handout_markup.HEADING,
        handout_markup.INITIAL,
        handout_markup.PICTURE,
        handout_markup.PICTURE,
    ]


def test_each_picture_is_named_so_a_missing_one_says_which() -> None:
    saga, _session, _book = _begun()
    letter = _letter(saga)

    reading = _preview(saga).reading

    assert reading is not None
    captions = [b.caption for b in reading.laid.blocks if b.picture]
    assert captions == [handouts.picture_name(saga, p) for p in letter.pictures]
    assert captions[1] and "shown with it" not in captions


def test_each_picture_keeps_its_place_as_a_show_numbers_it() -> None:
    """A picture the app can't read still holds its place, so [picture 2]
    is the same picture in the Preview as in the players' copy."""
    saga, _session, _book = _begun()
    letter = _letter(saga)
    letter.pictures = [HandoutPicture("nowhere", "x.png"), letter.pictures[0]]

    reading = _preview(saga).reading

    assert reading is not None
    assert reading.pictures == (None, PICTURE)
    assert [b.picture for b in reading.laid.blocks if b.picture] == [1, 2]


def test_a_picture_too_large_to_show_is_a_placeholder_as_in_a_show() -> None:
    saga, _session, _book = _begun()
    _letter(saga)
    big = b"\0" * (shows.PICTURE_CAP + 1)

    reading = handouts.preview_reading(saga, saga.handouts[0], lambda _f, _n: big)

    assert reading.pictures == (None, None)


def test_its_pictures_come_from_the_source_given() -> None:
    saga = Saga(id="quiet", name="Quiet")
    letter = _letter(saga)
    asked: list[tuple[str, str]] = []

    def source(folder: str, name: str) -> bytes | None:
        asked.append((folder, name))
        return PICTURE

    reading = handouts.preview_reading(saga, letter, source)

    assert reading.pictures == (PICTURE, PICTURE)
    assert asked == [(p.folder, p.name) for p in letter.pictures]


def test_previewing_writes_nothing_to_the_saga_chronicle_or_handout() -> None:
    saga, _session, book = _begun()
    letter = _letter(saga)
    before, entries = copy.deepcopy(saga), len(book.entries)

    form = _preview(saga)
    form.apply({})

    book.refresh()
    assert len(book.entries) == entries
    assert saga == before and letter == before.handouts[0]
    assert form.save_label == "Close"
    assert form.help_id == HANDOUTS_SECTION


def test_it_works_with_no_session_under_way() -> None:
    saga = Saga(id="quiet", name="Quiet")
    _letter(saga)

    assert chronicle.under_way(saga) is None
    assert _preview(saga).reading is not None


def test_preview_needs_a_handout_chosen() -> None:
    saga = Saga(id="quiet", name="Quiet")
    _letter(saga)

    assert isinstance(handout_forms.preview_handout(saga, None), Refuse)
    assert isinstance(handout_forms.preview_handout(saga, 3), Refuse)


class _Facts:
    """What the Preview rule asks of the facts: the saga, and the row."""

    def __init__(self, saga: Saga, row: int | None) -> None:
        self.saga, self.row = saga, row

    def chosen_row(self, _section: str) -> int | None:
        return self.row


@pytest.mark.parametrize("on", [True, False])
def test_preview_is_offered_on_a_chosen_handout_tabletop_or_not(on: bool) -> None:
    virtual_tabletop.set_on(on)
    saga = Saga(id="quiet", name="Quiet")
    _letter(saga)
    facts = cast(ActionFacts, _Facts(saga, 0))

    assert more_rules.previews_handout(facts, HANDOUTS_SECTION)
    assert not more_rules.previews_handout(facts, "section-players")
    unchosen = cast(ActionFacts, _Facts(saga, None))
    assert not more_rules.previews_handout(unchosen, HANDOUTS_SECTION)


def test_preview_is_one_more_entry_on_the_handouts_list_beside_show() -> None:
    entry = more.REGISTRY["preview_handout"]

    assert entry.section == HANDOUTS_SECTION and not entry.on_page
    assert entry.label == "Preview"
    assert more.REFRESH["preview_handout"].saves is False


def test_a_player_is_never_offered_preview() -> None:
    assert "preview_handout" in viewing.STORYGUIDE_ONLY_ACTIONS
