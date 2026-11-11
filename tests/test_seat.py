"""The seat: who is sitting at this copy, what they may do, what a save keeps."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from ars_magica_manager import players, seat, section_verbs, storage, viewing
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.models import Character, Player, Saga


@pytest.fixture(autouse=True)
def _empty_seat() -> Iterator[None]:
    yield
    seat.sign_out()


def _troupe() -> tuple[Saga, Player, Player, Character, Character]:
    saga = Saga(id="s", name="S")
    ana = Player(id="p1", name="Ana", role=players.PLAYER)
    ben = Player(id="p2", name="Ben", role=players.PLAYER)
    saga.players = [ana, ben]
    mine = Character(id="c1", name="Mine", type="magus")
    theirs = Character(id="c2", name="Theirs", type="magus")
    mine.background.player_ids = [ana.id]
    theirs.background.player_ids = [ben.id]
    saga.characters = [mine, theirs]
    return saga, ana, ben, mine, theirs


def test_the_storyguide_may_do_anything() -> None:
    saga, _, _, _, theirs = _troupe()
    assert seat.may_act(saga, None, "advance_season", theirs)
    assert seat.runs_the_saga(None)


def test_a_player_changes_only_their_own_and_never_what_is_barred() -> None:
    saga, ana, _, mine, theirs = _troupe()
    seat.sign_in(saga, ana)
    assert seat.may_act(saga, ana, "edit", mine)
    assert not seat.may_act(saga, ana, "edit", theirs)
    assert not seat.may_act(saga, ana, "advance_season", mine)
    assert not seat.may_act(saga, ana, "roll_table", mine)


def test_a_player_may_look_at_any_record() -> None:
    saga, ana, _, _, theirs = _troupe()
    seat.sign_in(saga, ana)
    assert seat.may_act(saga, ana, "find", theirs)
    assert seat.may_act(saga, ana, "export_record", theirs)


def test_signing_in_seats_the_viewer_the_guard_and_the_saver() -> None:
    saga, ana, _, _, _ = _troupe()
    seat.sign_in(saga, ana)
    assert viewing.current().kind == viewing.PLAYER
    assert storage.guard is not None
    assert storage.saved_by == "Ana"
    seat.sign_out()
    assert viewing.current().is_storyguide
    assert storage.guard is None
    assert storage.saved_by == ""


def test_the_storyguides_seat_has_no_guard() -> None:
    saga, _, _, _, _ = _troupe()
    seat.sign_in(saga, None)
    assert storage.guard is None
    guide = Player(id="g", name="Gus", role=players.STORYGUIDE)
    seat.sign_in(saga, guide)
    assert storage.guard is None
    assert storage.saved_by == "Gus"


def _page(saga: Saga, character_id: str) -> menu_forms.Page:
    return menu_forms.page_for(saga, NodeKind.CHARACTER, character_id=character_id)


def test_a_players_menus_leave_off_what_is_barred() -> None:
    saga, ana, _, _, _ = _troupe()
    page = _page(saga, "c1")
    guide = {i.action for i in menu_forms.more_items(page)} | {
        i.action for i in menu_forms.new_items(page)
    }
    assert guide & viewing.PLAYER_BARRED_ACTIONS  # the storyguide is offered them
    seat.sign_in(saga, ana)
    seen = {i.action for i in menu_forms.more_items(page)} | {
        i.action for i in menu_forms.new_items(page)
    }
    assert not seen & viewing.PLAYER_BARRED_ACTIONS
    assert not {i.action for i in menu_forms.manage_items(page)} & {"update_record"}


def test_another_players_page_offers_only_looking() -> None:
    saga, ana, _, _, _ = _troupe()
    seat.sign_in(saga, ana)
    page = _page(saga, "c2")  # Ben's
    offered = (
        {i.action for i in menu_forms.more_items(page)}
        | {i.action for i in menu_forms.new_items(page)}
        | {i.action for i in menu_forms.manage_items(page)}
    )
    # Looking, and making a character of their own.
    assert offered <= viewing.LOOKING_ACTIONS | viewing.PLAYER_MAKES_ACTIONS
    assert menu_forms.deletes(page) is None


def test_a_players_own_page_offers_more_than_looking() -> None:
    saga, ana, _, _, _ = _troupe()
    seat.sign_in(saga, ana)
    offered = {i.action for i in menu_forms.more_items(_page(saga, "c1"))}
    assert offered - viewing.LOOKING_ACTIONS


def test_section_buttons_follow_who_may_change_the_record() -> None:
    saga, ana, _, mine, theirs = _troupe()
    assert section_verbs.ops_of(saga, theirs)  # the storyguide's
    seat.sign_in(saga, ana)
    assert section_verbs.ops_of(saga, mine)
    read_only = section_verbs.ops_of(saga, theirs)
    assert read_only  # the sections stay, so a sheet can list their rows
    assert all(
        ops.add is None and ops.edit is None and ops.remove is None
        for ops in read_only.values()
    )


def test_a_save_for_another_saver_leaves_this_copys_reader_alone() -> None:
    saga, ana, _, _, _ = _troupe()
    storage.save_saga(saga)
    seat.sign_in(saga, ana)
    year = saga.current_year
    saga.current_year = year + 1
    storage.save_saga(saga, storage.Saver("Host's listener"))
    saved = storage.load_saga(saga.id)
    assert saved.current_year == year + 1  # not taken back by Ana's guard
    assert saved.saved_by == "Host's listener"
    assert storage.guard is not None and storage.saved_by == "Ana"


def test_the_guard_takes_back_a_change_and_says_so() -> None:
    saga, ana, _, _, _ = _troupe()
    told: list[list[str]] = []
    seat.sign_in(saga, ana, on_refused=told.append)
    assert storage.guard is not None
    kept, refused = storage.guard({"current_year": 1220}, {"current_year": 1221})
    assert kept["current_year"] == 1220
    assert refused == ["current_year"]
    assert told == [["current_year"]]
