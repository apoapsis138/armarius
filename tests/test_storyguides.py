"""A storyguide for each story (ADR 0015): a record's own storyguide reads
it whole; any other storyguide, the host included, reads it as a player
would and can't change it; any storyguide takes a record with none, and
only its own storyguide releases it or hands it on."""

from __future__ import annotations

import copy
import json
from dataclasses import asdict

import pytest
from test_seat_view import LEAKS, hidden_saga

from ars_magica_manager import (
    ahead,
    attention,
    players,
    saga_index,
    seat,
    storyguides,
    transfer,
    viewing,
)
from ars_magica_manager.commands import Confirm, Form, Refuse
from ars_magica_manager.forms import saga_content as saga_forms
from ars_magica_manager.forms import secrets as secret_forms
from ars_magica_manager.models import Player, Saga
from ars_magica_manager.remote import audit
from ars_magica_manager.remote.audit import AuditLog, audit_path
from ars_magica_manager.saga_delta import DeltaRefused, fold, saga_delta
from ars_magica_manager.seat_view import seat_view


def _troupe() -> tuple[Saga, Player, Player]:
    """hidden_saga with two Storyguide-role Players, Bruno running every
    record that hides something, and Anna none."""
    saga = hidden_saga()
    anna = players.find(saga, "Anna")
    assert anna is not None
    anna.role = players.STORYGUIDE
    bruno = players.add(
        saga,
        {"name": "Bruno", "role": players.STORYGUIDE, "passcode": "x" * 14},
    )
    for record in (
        saga.covenants[0],
        saga.characters[0],
        saga.neighbour("drachenfels"),
        saga.neighbour("crown"),
        saga.neighbour("grove"),
    ):
        assert record is not None
        record.storyguide_id = bruno.id
    return saga, anna, bruno


def _leaks(text: str) -> list[str]:
    return [where for where, word in LEAKS.items() if word in text]


@pytest.fixture(autouse=True)
def _reset_viewer():
    yield
    viewing.use(viewing.STORYGUIDE_VIEWER)
    viewing.on_page(None)


def test_a_record_with_no_storyguide_is_everyones():
    saga = hidden_saga()
    assert not viewing.troupe_style(saga)
    assert viewing.reads_everything(viewing.STORYGUIDE_VIEWER, saga)
    copied = json.dumps(asdict(seat_view(saga, viewing.STORYGUIDE_VIEWER)))
    assert not set(LEAKS) - set(_leaks(copied))


def test_another_storyguides_records_leave_as_a_player_has_them():
    saga, anna, bruno = _troupe()
    host = json.dumps(asdict(seat_view(saga, viewing.STORYGUIDE_VIEWER)))
    assert _leaks(host) == []  # no all-seeing alpha
    hers = json.dumps(asdict(seat_view(saga, viewing.viewer_for(anna))))
    assert _leaks(hers) == []
    his = json.dumps(asdict(seat_view(saga, viewing.viewer_for(bruno))))
    assert not set(LEAKS) - set(_leaks(his))


def test_a_record_naming_someone_no_longer_a_storyguide_is_no_ones():
    saga, _anna, bruno = _troupe()
    bruno.role = players.PLAYER
    assert viewing.storyguide_of(saga.covenants[0], saga) == ""
    assert viewing.reads_everything(viewing.STORYGUIDE_VIEWER, saga)


def test_a_laboratory_and_familiar_are_their_characters():
    saga, _anna, bruno = _troupe()
    magus = saga.characters[0]
    for lab in saga.laboratories:
        if lab.owner_id == magus.id:
            assert viewing.storyguide_of(lab, saga) == bruno.id
    for familiar in saga.familiars:
        if familiar.character_id == magus.id:
            assert viewing.storyguide_of(familiar, saga) == bruno.id


def test_the_host_reads_anothers_record_as_a_player_and_cant_change_it():
    saga, _anna, bruno = _troupe()
    covenant = saga.covenants[0]
    viewing.use(viewing.STORYGUIDE_VIEWER, saga)
    seat.sign_in(saga, None)
    assert not secret_forms.storyguides(covenant)
    assert not viewing.reads(saga.neighbour("grove"))
    assert not seat.may_change(saga, covenant)
    assert seat.may_change(saga, saga.covenants[1] if len(saga.covenants) > 1 else None)
    assert not seat.may_act(saga, None, "reveal_secret", covenant)
    assert seat.may_act(saga, None, "go_to", covenant)  # looking is anyone's
    # Bruno, in his storyguide role, reads and changes it.
    seat.sign_in(saga, bruno)
    assert secret_forms.storyguides(covenant)
    assert seat.may_change(saga, covenant)


def test_a_page_part_asks_about_the_page_being_drawn():
    saga, _anna, _bruno = _troupe()
    viewing.use(viewing.STORYGUIDE_VIEWER, saga)
    viewing.on_page(saga.covenants[0])
    assert not viewing.reads(part="section-secrets")
    viewing.on_page(None)
    assert viewing.reads(part="section-attention")


def test_find_ahead_and_needs_you_leave_out_anothers_secrets():
    saga, anna, _bruno = _troupe()
    viewing.use(viewing.viewer_for(anna), saga)
    found = json.dumps([str(e) for e in saga_index.entries(saga)])
    assert "LEAK-UNKNOWN" not in found and "LEAK-SECRET" not in found
    assert all("LEAK-STAGE" not in e.title for e in ahead.entries(saga))
    assert all(
        item.ref is None or viewing.ref_held(saga, item.ref)
        for item in attention.items(saga)
    )


def test_an_export_by_another_storyguide_carries_no_secrets_of_his():
    saga, anna, _bruno = _troupe()
    viewing.use(viewing.viewer_for(anna), saga)
    exported = json.dumps(transfer.export_saga_data(saga))
    assert _leaks(exported) == []


def test_playing_reads_as_a_player_and_switching_is_always_offered():
    saga, _anna, bruno = _troupe()
    seat.sign_in(saga, bruno, player_view=True)
    looking = viewing.current()
    assert not looking.is_storyguide and looking.storyguide_id == bruno.id
    assert not secret_forms.storyguides(saga.covenants[0])
    assert seat.may_act(saga, bruno, "player_view")


def test_a_remote_seat_leaves_advancing_to_the_host_while_another_runs_stories():
    saga, anna, _bruno = _troupe()
    remote = viewing.viewer_for(anna, hosts=False)
    viewing.use(remote, saga)
    assert not viewing.may_do(remote, "advance_season")
    viewing.use(viewing.viewer_for(anna), saga)  # on the host's computer
    assert viewing.may_do(viewing.current(), "advance_season")


# -- Its Storyguide --


def test_any_storyguide_takes_a_record_with_none():
    saga, anna, _bruno = _troupe()
    record = saga.neighbours[-1]
    record.storyguide_id = ""
    viewing.use(viewing.viewer_for(anna), saga)
    assert storyguides.offered(saga, record)
    form = storyguides.assign_form(saga, record)
    assert isinstance(form, Form)
    options = [key for _label, key in form.fields()[0].options]
    assert options == [anna.id]  # herself only: no taking for another
    form.apply({"storyguide": anna.id})
    assert record.storyguide_id == anna.id


def test_only_its_own_storyguide_releases_or_hands_it_on():
    saga, anna, bruno = _troupe()
    covenant = saga.covenants[0]
    viewing.use(viewing.viewer_for(anna), saga)
    assert not storyguides.offered(saga, covenant)
    assert isinstance(storyguides.assign_form(saga, covenant), Refuse)
    viewing.use(viewing.viewer_for(bruno), saga)
    form = storyguides.assign_form(saga, covenant)
    assert isinstance(form, Form)
    keys = {key for _label, key in form.fields()[0].options}
    assert keys == {bruno.id, anna.id, viewing.HOST}
    form.apply({"storyguide": anna.id})
    assert covenant.storyguide_id == anna.id


def test_not_offered_without_a_second_storyguide():
    saga = hidden_saga()
    viewing.use(viewing.STORYGUIDE_VIEWER, saga)
    assert not storyguides.offered(saga, saga.covenants[0])


def test_deleting_or_demoting_a_storyguide_frees_their_records_after_a_warning():
    saga, _anna, bruno = _troupe()
    step = saga_forms.delete_player(saga, bruno)
    assert isinstance(step, Confirm)
    assert saga.covenants[0].name in step.question
    step.apply()
    assert saga.covenants[0].storyguide_id == ""

    saga, _anna, bruno = _troupe()
    form = saga_forms.player_form(saga, bruno)
    values = {"name": bruno.name, "role": players.PLAYER, "passcode": ""}
    asked = form.apply(values)
    assert isinstance(asked, Confirm) and "every storyguide" in asked.question
    asked.apply()
    assert saga.covenants[0].storyguide_id == ""


# -- a storyguide's whole-saga save --


def _changed(saga: Saga, viewer: viewing.Viewer, change) -> tuple[dict, dict]:
    base = asdict(seat_view(saga, viewer))
    now = copy.deepcopy(base)
    change(now)
    return saga_delta(base, now)


def test_a_save_changing_anothers_record_is_refused():
    saga, anna, _bruno = _troupe()

    def rename(now: dict) -> None:
        now["covenants"][0]["name"] = "Taken"

    with pytest.raises(DeltaRefused):
        fold(saga, *_changed(saga, viewing.viewer_for(anna), rename), by=anna.id)


def test_a_save_keeps_what_was_hidden_from_the_storyguide():
    saga, anna, bruno = _troupe()
    # Anna's own covenant holds a Diary line about Bruno's unknown grove.
    covenant = saga.covenants[0]
    covenant.storyguide_id = anna.id
    saga.neighbour("grove").storyguide_id = bruno.id  # type: ignore[union-attr]

    def rename(now: dict) -> None:
        now["covenants"][0]["name"] = "Renamed"

    folded = fold(saga, *_changed(saga, viewing.viewer_for(anna), rename), by=anna.id)
    kept = folded.saga.covenants[0]
    assert kept.name == "Renamed"
    assert any(e.name == "LEAK-COVDIARY" for e in kept.diary)


def test_a_save_takes_a_record_for_its_storyguide_but_never_for_another():
    saga, anna, bruno = _troupe()
    saga.neighbours[-2].storyguide_id = ""
    index = len(saga.neighbours) - 2

    def take(who: str):
        def change(now: dict) -> None:
            for record in now["neighbours"]:
                if record["id"] == saga.neighbours[index].id:
                    record["storyguide_id"] = who

        return change

    viewer = viewing.viewer_for(anna)
    with pytest.raises(DeltaRefused):
        fold(saga, *_changed(saga, viewer, take(bruno.id)), by=anna.id)
    folded = fold(saga, *_changed(saga, viewer, take(anna.id)), by=anna.id)
    assert folded.saga.neighbours[index].storyguide_id == anna.id


# -- the switch, logged --


def test_the_hosts_switch_is_logged_with_a_second_storyguide():
    saga, _anna, bruno = _troupe()
    storyguides.log_switch(saga, None, playing=True)
    storyguides.log_switch(saga, bruno, playing=False)
    events = [(e.event, e.player_id) for e in AuditLog(audit_path(saga.name)).entries()]
    assert events == [
        (audit.SWITCHED_TO_PLAYING, ""),
        (audit.SWITCHED_TO_STORYGUIDE, bruno.id),
    ]


def test_no_switch_is_logged_with_one_storyguide():
    saga = hidden_saga()
    storyguides.log_switch(saga, None, playing=True)
    assert AuditLog(audit_path(saga.name)).entries() == []
