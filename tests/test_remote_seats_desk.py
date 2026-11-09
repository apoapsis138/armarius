"""The Storyguide's Remote seats commands and rows (forms/remote_seats.py):
Issue Invite, approving and rejecting, revoking, rotating the host key, the
idle-expiry setting, the log, and the Host for Remote Seats form."""

from __future__ import annotations

import pytest

from ars_magica_manager import players
from ars_magica_manager.commands import Confirm, Form, Picked, Refuse
from ars_magica_manager.forms import remote_seats as rs
from ars_magica_manager.models import Saga
from ars_magica_manager.remote import audit
from ars_magica_manager.remote.client import new_device_secret
from ars_magica_manager.remote.identity import MemoryStore
from ars_magica_manager.remote.invites import decode_invite
from ars_magica_manager.remote.plan import RemotePlan, last_plan, plan_path
from ars_magica_manager.remote.words import host_words, two_lines

LONG = "a passcode long enough"


class Clock:
    def __init__(self) -> None:
        self.now = 1_800_000_000.0

    def __call__(self) -> float:
        return self.now


@pytest.fixture
def desk() -> rs.SeatsDesk:
    saga = Saga(id="s", name="S")
    desk = rs.SeatsDesk(saga, MemoryStore(), Clock())
    for name, passcode in (("Anna", LONG), ("Bruno", "short")):
        player = players.add(saga, {"name": name, "passcode": passcode})
        desk.passcodes().note(player, passcode)
    players.add(saga, {"name": "Sg", "passcode": LONG, "role": players.STORYGUIDE})
    RemotePlan("s", "S", "https://saga.example.com").remember()
    return desk


def _redeem(desk: rs.SeatsDesk, name: str = "Anna") -> str:
    """A player's device redeems an Invite (as the listener would)."""
    player = players.find(desk.saga, name)
    assert player is not None
    book = desk.invites()
    return book.redeem(
        book.issue(player.id), f"{name}'s laptop", new_device_secret()
    ).id


def _enrol(desk: rs.SeatsDesk) -> str:
    request = desk.invites().approve(_redeem(desk))
    desk.devices().enrol(request)
    return request.id


def test_players_are_listed_with_whether_they_can_use_a_remote_seat(
    desk: rs.SeatsDesk,
) -> None:
    from ars_magica_manager.sheets.saga_content import players_table

    table = players_table(desk.saga, seats=True)
    assert table.columns[-1] == "Remote seat"
    rows = {row[0]: row for row in table.rows}
    assert rows["Anna"][-1] == "✓ Ready"
    assert rows["Bruno"][-1].startswith("✗")
    assert rows["Sg"][1] == "Storyguide"
    assert "Remote seat" not in players_table(desk.saga).columns  # the terminal's


def test_a_chosen_player_can_be_invited_at_once(desk: rs.SeatsDesk) -> None:
    anna = players.find(desk.saga, "Anna")
    assert anna is not None
    invite = desk.issue_invite(anna.id)
    assert isinstance(invite, Form)
    assert {f.key: f for f in invite.fields()}["player"].value == anna.id


def test_an_invite_needs_the_tunnel_address_first(desk: rs.SeatsDesk) -> None:
    desk.saga.name = "Elsewhere"  # no plan remembered for this name
    refused = desk.issue_invite()
    assert isinstance(refused, Refuse) and "tunnel" in refused.why


def test_issue_invite_offers_only_players_whose_passcode_is_long_enough(
    desk: rs.SeatsDesk,
) -> None:
    form = desk.issue_invite()
    assert isinstance(form, Form)
    fields = {f.key: f for f in form.fields()}
    assert [label for label, _ in fields["player"].options] == ["Anna"]
    assert "Bruno" in str(fields["_unable"].value)
    picked = form.apply({"player": fields["player"].value})
    assert isinstance(picked, Picked) and isinstance(picked.value, rs.IssuedInvite)
    issued = picked.value
    parts = decode_invite(issued.line)
    identity = desk.identity()
    assert parts.url == "wss://saga.example.com/remote"
    assert parts.pin == identity.pin
    assert issued.host_words == two_lines(host_words(identity.pin))
    assert issued.player == "Anna" and issued.expires == rs.when(
        Clock().now + 24 * 3600
    )
    # The code works at the listener, for Anna.
    anna = players.find(desk.saga, "Anna")
    request = desk.invites().redeem(parts.code, "laptop", new_device_secret())
    assert anna is not None and request.player_id == anna.id


def test_with_no_long_passcode_nobody_is_offered(desk: rs.SeatsDesk) -> None:
    anna = players.find(desk.saga, "Anna")
    assert anna is not None
    players.set_passcode(anna, LONG)  # changed elsewhere: a fresh salt, not noted
    refused = desk.issue_invite()
    assert isinstance(refused, Refuse) and "Anna" in refused.why


def test_approving_asks_about_the_three_words_first(desk: rs.SeatsDesk) -> None:
    request_id = _redeem(desk)
    [row] = desk.requests()
    assert (row.player, row.device) == ("Anna", "Anna's laptop")
    confirm = desk.approve(request_id)
    assert isinstance(confirm, Confirm) and row.words in confirm.question
    assert confirm.yes_label == "Approve"
    confirm.apply()
    assert desk.requests() == []
    assert desk.invites().pending() == []
    # Asked again, it is no longer waiting.
    assert isinstance(desk.approve(request_id), Refuse)


def test_rejecting_spends_the_invite(desk: rs.SeatsDesk) -> None:
    request_id = _redeem(desk)
    confirm = desk.reject(request_id)
    assert isinstance(confirm, Confirm) and confirm.yes_label == "Reject"
    confirm.apply()
    assert desk.requests() == []
    events = [e.event for e in desk.log().entries()]
    assert audit.REQUEST_REJECTED in events


def test_revoking_ends_a_seat(desk: rs.SeatsDesk) -> None:
    device_id = _enrol(desk)
    [seat] = desk.seats()
    assert seat.live and seat.player == "Anna" and seat.state.startswith("Expires")
    confirm = desk.revoke(device_id)
    assert isinstance(confirm, Confirm)
    confirm.apply()
    [seat] = desk.seats()
    assert not seat.live and seat.state.startswith("Revoked")
    assert isinstance(desk.revoke(device_id), Refuse)


def test_rotating_the_key_ends_every_invite_and_seat(desk: rs.SeatsDesk) -> None:
    _enrol(desk)
    waiting = _redeem(desk)
    old = desk.identity().pin
    confirm = desk.rotate()
    assert isinstance(confirm, Confirm)
    said = confirm.apply()
    assert desk.identity().pin != old
    assert all(not s.live for s in desk.seats())
    assert desk.requests() == [] and waiting
    assert "new Invite" in said[0]
    assert audit.HOST_KEY_ROTATED in [e.event for e in desk.log().entries()]


def test_the_idle_expiry_is_set_per_saga(desk: rs.SeatsDesk) -> None:
    form = desk.idle_form()
    assert form.validate is not None
    assert form.validate({"days": 0}) is not None
    assert form.validate({"days": 30}) is None
    form.apply({"days": 30})
    assert desk.idle_days() == 30


def test_the_log_is_newest_first_and_narrows_to_a_player(desk: rs.SeatsDesk) -> None:
    _enrol(desk)
    _redeem(desk, "Bruno")  # Bruno's invite, though he can't sign in yet
    rows = desk.log_rows()
    assert rows[0].event == "Invite redeemed" and rows[0].player == "Bruno"
    anna = players.find(desk.saga, "Anna")
    assert anna is not None
    assert {r.player for r in desk.log_rows(anna.id)} == {"Anna"}
    assert ("Anna", anna.id) in desk.log_players()
    # Storyguides too: they can have seats now.
    assert "Sg" in [name for name, _ in desk.log_players()]


def test_the_host_form_checks_the_address_and_says_where_to_point_the_tunnel(
    desk: rs.SeatsDesk,
) -> None:
    form = desk.host_form()
    assert form.validate is not None and form.live is not None
    good = {
        "public_url": "https://saga.example.com",
        "port": 8790,
        "tunnel": "cloudflare",
    }
    assert form.validate(good) is None
    assert form.validate(good | {"public_url": "http://saga.example.com"}) is not None
    assert (
        form.validate(good | {"public_url": "https://x.com/remote?code=1"}) is not None
    )
    assert form.validate(good | {"port": 80}) is not None
    live = form.live(good)
    assert "http://localhost:8790" in live and "wss://saga.example.com/remote" in live


@pytest.mark.usefixtures("desk")
def test_a_damaged_plan_file_gives_the_defaults() -> None:
    plan_path("S").write_text('{"port": "x", "tunnel": "nope"}', encoding="utf-8")
    plan = last_plan("s", "S")
    assert (plan.public_url, plan.port, plan.tunnel) == ("", 8790, "cloudflare")
