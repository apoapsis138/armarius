"""The admin word: the host's chores from a plain terminal, run through the
same commands as the Host for Players window, with nothing over the wire."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pytest
from admin_support import FakeConsole, ok, refused

from ars_magica_manager import admin, launch, storage
from ars_magica_manager import players as pl
from ars_magica_manager.models import Saga
from ars_magica_manager.remote import identity as ident
from ars_magica_manager.remote.audit import AuditLog, audit_path
from ars_magica_manager.remote.devices import DeviceBook, devices_path
from ars_magica_manager.remote.invites import (
    INVITE_PREFIX,
    InviteBook,
    book_path,
    decode_invite,
)
from ars_magica_manager.remote.passcodes import passcodes_path
from ars_magica_manager.remote.plan import identity_name, last_plan

PASSCODE = "grey owl over the mill"
SECRET = "ab" * 16


@pytest.fixture
def saga() -> Saga:
    saga = Saga(id="dammerstein", name="Dammerstein")
    pl.add(saga, {"name": "Ana", "role": pl.PLAYER})
    pl.add(saga, {"name": "Bruno", "role": pl.STORYGUIDE})
    storage.save_saga(saga)
    return saga


def ready_for_invites(saga: Saga) -> None:
    """Ana's passcode set through admin, and the tunnel address known."""
    ok(["players", "set-passcode", "Ana"], FakeConsole(secrets=[PASSCODE, PASSCODE]))
    ok(["tunnel", "--url", "https://saga.example.com"])


def pending_request(saga: Saga) -> str:
    book = InviteBook(book_path(saga.name), log=AuditLog(audit_path(saga.name)))
    return book.redeem(book.issue(saga.players[0].id), "Ana's laptop", SECRET).id


# -- the word and choosing a saga -------------------------------------------------


def test_admin_is_one_of_the_words() -> None:
    assert launch.ADMIN in launch.WORDS
    assert launch.command(launch.ADMIN, "sagas")[-2:] == [
        "ars_magica_manager.admin",
        "sagas",
    ]


def test_the_only_saga_is_taken_without_asking(saga: Saga) -> None:
    assert admin.saga_id_for(None) == "dammerstein"
    assert admin.saga_id_for("DAMMERSTEIN") == "dammerstein"  # by name
    storage.save_saga(Saga(id="other", name="Other"))
    with pytest.raises(admin.AdminError, match="--saga"):
        admin.saga_id_for(None)
    with pytest.raises(admin.AdminError, match="no saga 'nowhere'"):
        admin.saga_id_for("nowhere")


def test_the_container_names_its_saga(
    saga: Saga, monkeypatch: pytest.MonkeyPatch
) -> None:
    storage.save_saga(Saga(id="other", name="Other"))
    monkeypatch.setenv(admin.SAGA_VARIABLE, "other")
    assert admin.saga_id_for(None) == "other"


def test_sagas_lists_ids_and_names(saga: Saga) -> None:
    assert "dammerstein  Dammerstein" in ok(["sagas"]).text


# -- players -------------------------------------------------------------------


def test_players_list_says_who_may_have_a_seat(saga: Saga) -> None:
    text = ok(["players", "list"]).text
    assert "Ana  (Player)  no Remote seat: has no passcode yet" in text
    assert "Bruno  (Storyguide)" in text


def test_set_passcode_is_asked_twice_and_hidden(saga: Saga) -> None:
    console = ok(
        ["players", "set-passcode", "ana"], FakeConsole(secrets=[PASSCODE, PASSCODE])
    )
    player = storage.load_saga("dammerstein").players[0]
    assert pl.passcode_matches(player, PASSCODE)
    assert "may have a Remote seat" in ok(["players", "list"]).text
    assert PASSCODE not in console.text


def test_a_short_or_mistyped_passcode_changes_nothing(saga: Saga) -> None:
    short = refused(["players", "set-passcode", "Ana"], FakeConsole(secrets=["short"]))
    assert f"at least {pl.MIN_PASSCODE}" in short
    differ = refused(
        ["players", "set-passcode", "Ana"],
        FakeConsole(secrets=[PASSCODE, PASSCODE + "!"]),
    )
    assert "differ" in differ
    assert not storage.load_saga("dammerstein").players[0].passcode_hash


def test_set_role(saga: Saga) -> None:
    ok(["players", "set-role", "Ana", "storyguide"])
    assert storage.load_saga("dammerstein").players[0].role == pl.STORYGUIDE
    assert "A role is one of" in refused(["players", "set-role", "Ana", "king"])
    assert "No player is called 'Zed'" in refused(
        ["players", "set-role", "Zed", "player"]
    )


def test_making_a_seated_player_a_storyguide_asks_first(saga: Saga) -> None:
    devices = DeviceBook(devices_path(saga.name))
    book = InviteBook(book_path(saga.name))
    request = book.approve(pending_request(saga))
    devices.enrol(request)
    console = FakeConsole(answers=["no"])
    assert "Nothing was changed" in refused(
        ["players", "set-role", "Ana", "storyguide"], console
    )
    assert "see everything in the saga" in console.text
    assert storage.load_saga("dammerstein").players[0].role == pl.PLAYER
    ok(["players", "set-role", "Ana", "storyguide"], FakeConsole(answers=["yes"]))
    assert storage.load_saga("dammerstein").players[0].role == pl.STORYGUIDE


# -- the tunnel, Invites and requests ---------------------------------------------------


def test_tunnel_is_checked_and_remembered(saga: Saga) -> None:
    assert "https address" in refused(["tunnel", "--url", "http://saga.example.com"])
    assert "1024 to 65535" in refused(
        ["tunnel", "--url", "https://a.example", "--port", "80"]
    )
    ok(["tunnel", "--url", "https://saga.example.com/", "--tunnel", "other"])
    plan = last_plan("dammerstein", "Dammerstein")
    assert (plan.public_url, plan.tunnel) == ("https://saga.example.com", "other")
    assert "Tunnel address: https://saga.example.com" in ok(["tunnel"]).text


def test_an_invite_needs_the_tunnel_address_first(saga: Saga) -> None:
    ok(["players", "set-passcode", "Ana"], FakeConsole(secrets=[PASSCODE, PASSCODE]))
    assert "tunnel's address" in refused(["invites", "issue", "Ana"])


def test_issue_prints_the_invite_and_the_words(saga: Saga) -> None:
    ready_for_invites(saga)
    text = ok(["invites", "issue", "Ana"]).text
    line = next(row for row in text.splitlines() if row.startswith(INVITE_PREFIX))
    invite = decode_invite(line)
    pin = ident.load_or_create(ident.KeychainStore(), identity_name("dammerstein")).pin
    assert invite.url == "wss://saga.example.com/remote" and invite.pin == pin
    assert ok(["words"]).printed[1] in text  # the same six words


def test_a_player_without_a_long_passcode_gets_no_invite(saga: Saga) -> None:
    ok(["tunnel", "--url", "https://saga.example.com"])
    assert "No player can sign in" in refused(["invites", "issue", "Ana"])


def test_pending_approve_and_reject(saga: Saga) -> None:
    first = pending_request(saga)
    text = ok(["invites", "pending"]).text
    assert "A seat for Ana, from Ana's laptop" in text
    # The command to type is printed whole, with the short id.
    assert f"To approve: python main.py admin approve {first[:8]}" in text
    assert f"To turn down: python main.py admin reject {first[:8]}" in text
    ok(["approve", first[:8], "--yes"])
    assert "Nothing is waiting" in ok(["invites", "pending"]).text
    second = InviteBook(book_path(saga.name)).redeem(
        InviteBook(book_path(saga.name)).issue(saga.players[0].id), "Phone", "cd" * 16
    )
    console = FakeConsole(answers=["yes"])
    ok(["reject", second.id], console)
    assert "Rejected" in console.text
    assert "no request" in refused(["approve", "zzz", "--yes"])


def test_turning_down_the_question_changes_nothing(saga: Saga) -> None:
    request = pending_request(saga)
    assert "Nothing was changed" in refused(
        ["approve", request], FakeConsole(answers=["n"])
    )
    assert "Nothing was changed" in refused(["approve", request])  # no answer at all
    assert request[:8] in ok(["invites", "pending"]).text


def test_short_ids_grow_until_unique() -> None:
    found = admin.short_ids(["abcdefgh1", "abcdefgh2", "zzzzzzzzzz", "reset:12345678x"])
    assert found == {
        "abcdefgh1": "abcdefgh1",
        "abcdefgh2": "abcdefgh2",
        "zzzzzzzzzz": "zzzzzzzz",
        "reset:12345678x": "reset:12345678",
    }


def test_inside_the_container_the_docker_command_is_printed(
    saga: Saga, monkeypatch: pytest.MonkeyPatch
) -> None:
    real = Path.exists
    monkeypatch.setattr(
        Path, "exists", lambda p: str(p) == str(Path("/.dockerenv")) or real(p)
    )
    request = pending_request(saga)
    assert (
        f"docker exec -it armarius python main.py admin approve {request[:8]}"
        in ok(["invites", "pending"]).text
    )


# -- seats, the Log, the key ---------------------------------------------------------


def test_devices_list_and_revoke(saga: Saga) -> None:
    devices = DeviceBook(devices_path(saga.name))
    devices.enrol(InviteBook(book_path(saga.name)).approve(pending_request(saga)))
    (device,) = devices.devices()
    listed = ok(["devices", "list"]).text
    assert "Ana on Ana's laptop" in listed
    assert f"To revoke: python main.py admin devices revoke {device.id[:8]}" in listed
    ok(["devices", "revoke", device.id, "--yes"])
    assert not DeviceBook(devices_path(saga.name)).is_live(device.id)
    assert "no live seat" in refused(["devices", "revoke", device.id, "--yes"])


def test_the_log_newest_first_and_by_player(saga: Saga) -> None:
    pending_request(saga)
    text = ok(["log"]).text.splitlines()
    assert "Invite redeemed  Ana" in text[0]
    assert "Invite issued  Ana" in text[1]
    assert ok(["log", "--player", "Bruno"]).text == "The Log is empty."
    assert len(ok(["log", "--limit", "1"]).printed) == 1


def test_rotate_key_ends_every_seat_and_says_to_restart(saga: Saga) -> None:
    devices = DeviceBook(devices_path(saga.name))
    devices.enrol(InviteBook(book_path(saga.name)).approve(pending_request(saga)))
    store = ident.KeychainStore()
    old = ident.load_or_create(store, identity_name("dammerstein")).pin
    text = ok(["rotate-key", "--yes"]).text
    assert ident.load_or_create(store, identity_name("dammerstein")).pin != old
    assert not any(not d.ended for d in DeviceBook(devices_path(saga.name)).devices())
    assert "Restart the listener" in text
    assert any(
        e.event == "host_key_rotated" for e in AuditLog(audit_path(saga.name)).entries()
    )


def test_the_key_store_setting_is_followed(
    saga: Saga, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The host key comes from key_files.key_store, so a wrong setting is
    refused plainly rather than the keychain used instead."""
    monkeypatch.setenv("ARMARIUS_KEYSTORE", "files")
    assert "doesn't know" in refused(["rotate-key", "--yes"])
    assert "doesn't know" in refused(["words"])


# -- bringing a saga in, deleting one ----------------------------------------------


def _saga_file(tmp_path_factory: pytest.TempPathFactory, data: object) -> Path:
    path = tmp_path_factory.mktemp("incoming") / "saga.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_import_brings_a_saga_in(tmp_path_factory: pytest.TempPathFactory) -> None:
    saga = Saga(id="rhine", name="The Rhine")
    pl.add(saga, {"name": "Ana", "role": pl.PLAYER, "passcode": PASSCODE})
    path = _saga_file(tmp_path_factory, asdict(saga))
    assert "issue every player a new Invite" in ok(["saga", "import", str(path)]).text
    assert storage.load_saga("rhine").players[0].name == "Ana"
    assert "already here" in refused(["saga", "import", str(path)])
    # Without the old host's records, the passcode must be set again here.
    assert "no Remote seat" in ok(["players", "list"]).text


def _moving_saga() -> Saga:
    """A saga with Ana (passcode set on the old host) and Bruno (changed
    since the old host noted it)."""
    saga = Saga(id="rhine", name="The Rhine")
    for name in ("Ana", "Bruno", "Cora"):
        pl.add(saga, {"name": name, "role": pl.PLAYER, "passcode": PASSCODE})
    return saga


def _notes_file(tmp_path_factory: pytest.TempPathFactory, saga: Saga) -> Path:
    """The old host's records: Ana's matches; Bruno's was for an older
    passcode; Cora has none; and one for a player no longer in the saga."""
    ana, bruno, _cora = saga.players
    salts = {
        ana.id: pl.stored_parts(ana.passcode_hash)[0].hex(),
        bruno.id: "00" * 16,
        "gone": "11" * 16,
    }
    path = tmp_path_factory.mktemp("old-host") / "The_Rhine-passcodes.json"
    path.write_text(json.dumps({"salts": salts}), encoding="utf-8")
    return path


def test_import_carries_over_matching_passcode_records(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    saga = _moving_saga()
    path = _saga_file(tmp_path_factory, asdict(saga))
    notes = _notes_file(tmp_path_factory, saga)
    text = ok(["saga", "import", str(path), "--passcodes", str(notes)]).text
    assert "Passcodes carried over for: Ana." in text
    listed = ok(["players", "list"]).text.splitlines()
    assert "may have a Remote seat" in listed[0]  # Ana keeps hers
    assert "no Remote seat" in listed[1] and "no Remote seat" in listed[2]
    stored = json.loads(passcodes_path("The Rhine").read_text(encoding="utf-8"))
    assert set(stored["salts"]) == {saga.players[0].id}


def test_a_bad_passcodes_file_changes_nothing(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    path = _saga_file(tmp_path_factory, asdict(_moving_saga()))
    bad = tmp_path_factory.mktemp("bad") / "p.json"
    bad.write_text(json.dumps({"salts": {"x": 5}}), encoding="utf-8")
    assert "isn't a passcodes file" in refused(
        ["saga", "import", str(path), "--passcodes", str(bad)]
    )
    assert "Can't read" in refused(
        ["saga", "import", str(path), "--passcodes", "missing.json"]
    )
    assert storage.list_sagas() == []


def test_import_refuses_what_isnt_a_saga(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    assert "isn't a saga" in refused(
        ["saga", "import", str(_saga_file(tmp_path_factory, [1]))]
    )
    assert "isn't a saga" in refused(
        ["saga", "import", str(_saga_file(tmp_path_factory, {"name": 5}))]
    )
    assert "Can't read" in refused(["saga", "import", "no-such-file.json"])
    assert storage.list_sagas() == []


def test_import_refuses_an_id_that_is_a_path(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    data = asdict(Saga(id="../escape", name="Escape"))
    assert "safe id" in refused(
        ["saga", "import", str(_saga_file(tmp_path_factory, data))]
    )
    assert storage.list_sagas() == []


def test_delete_needs_the_saga_typed(saga: Saga) -> None:
    assert "nothing was deleted" in refused(
        ["saga", "delete"], FakeConsole(answers=["dammerstein"])
    )
    assert "nothing was deleted" in refused(["saga", "delete"])  # no answer
    assert storage.list_sagas() == ["dammerstein"]
    ok(
        ["saga", "delete", "--saga", "dammerstein"],
        FakeConsole(answers=["Dammerstein"]),
    )
    assert storage.list_sagas() == []


def test_nothing_goes_over_the_wire() -> None:
    """The admin word reads and writes files on this computer: it imports
    no network library."""
    source = Path(admin.__file__).read_text(encoding="utf-8")
    for name in ("aiohttp", "asyncssh", "socket", "urllib.request", "websockets"):
        assert f"import {name}" not in source and f"from {name}" not in source
