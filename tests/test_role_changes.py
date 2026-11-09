"""The host gives a Player the Storyguide role and takes it back (ADR
0014): promoting someone whose devices have seats asks first, naming them,
and the Log notes the change."""

from __future__ import annotations

from typing import Any

from ars_magica_manager import players, storage
from ars_magica_manager.commands import Confirm, Form
from ars_magica_manager.forms.saga_content import player_form
from ars_magica_manager.models import Saga
from ars_magica_manager.remote import audit
from ars_magica_manager.remote.audit import AuditLog, audit_path
from ars_magica_manager.remote.devices import DeviceBook, devices_path
from ars_magica_manager.remote.invites import Request


def _saga_with_a_seat() -> tuple[Saga, players.Player]:
    saga = Saga(id="s", name="S")
    anna = players.add(
        saga, {"name": "Anna", "role": players.PLAYER, "passcode": "p" * 14}
    )
    storage.save_saga(saga)
    request = Request(
        id="r1",
        player_id=anna.id,
        device="Anna's laptop",
        words="a b c",
        created=1.0,
    )
    DeviceBook(devices_path(saga.name)).enrol(request)
    return saga, anna


def _values(name: str, role: str) -> dict[str, Any]:
    return {"name": name, "role": role, "passcode": "", "covenant_rights": False}


def test_promoting_a_seated_player_asks_first_naming_their_devices() -> None:
    saga, anna = _saga_with_a_seat()
    form = player_form(saga, anna)
    assert isinstance(form, Form)
    asked = form.apply(_values("Anna", players.STORYGUIDE))
    assert isinstance(asked, Confirm)
    assert "Anna's laptop" in asked.question
    assert anna.role == players.PLAYER  # nothing changed until Yes
    asked.apply()
    assert anna.role == players.STORYGUIDE
    events = [e.event for e in AuditLog(audit_path(saga.name)).entries()]
    assert audit.ROLE_CHANGED in events


def test_a_player_with_no_seat_is_promoted_at_once() -> None:
    saga = Saga(id="s2", name="S2")
    bruno = players.add(
        saga, {"name": "Bruno", "role": players.PLAYER, "passcode": "p" * 14}
    )
    assert player_form(saga, bruno).apply(_values("Bruno", players.STORYGUIDE)) is None
    assert bruno.role == players.STORYGUIDE
