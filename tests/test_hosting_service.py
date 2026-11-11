"""The core's hosting service (hosting.HOST) and the Host for Players and
Stop Hosting forms both front-ends draw from it."""

from __future__ import annotations

import socket
import urllib.error
import urllib.request

import pytest

from ars_magica_manager import hosting, settings
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.commands import Confirm, Form, Refuse
from ars_magica_manager.forms import hosting as hosting_forms
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.models import Saga
from ars_magica_manager.tui import serve


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("localhost", 0))
        return probe.getsockname()[1]


@pytest.fixture
def host(monkeypatch):
    """A fresh host for the test, stopped after it."""
    monkeypatch.delenv(hosting.TRANSPORT_VAR, raising=False)
    monkeypatch.delenv(hosting.OLD_TRANSPORT_VAR, raising=False)
    fresh = hosting.Host()
    monkeypatch.setattr(hosting, "HOST", fresh)
    yield fresh
    fresh.stop()


def _values(port: int, **more) -> dict:
    return {"address": hosting.LOCALHOST, "port": port, "ssh": False} | more


def test_a_plan_says_where_players_reach_it():
    plan = hosting.Plan("100.64.1.2", 8001, 2222)
    assert plan.browser_url() == "http://100.64.1.2:8001"
    assert plan.ssh_command() == "ssh -p 2222 player@100.64.1.2"
    assert plan.arguments() == [
        "--host",
        "100.64.1.2",
        "--port",
        "8001",
        "--ssh-port",
        "2222",
    ]
    assert hosting.Plan().arguments() == ["--host", "localhost", "--port", "8000"]


def test_addresses_are_labelled_by_the_network_they_are_on():
    assert hosting.address_label("100.101.2.3") == "100.101.2.3 (Tailscale)"
    assert hosting.address_label("192.168.1.5") == "192.168.1.5 (a private network)"
    assert "don't" in hosting.address_label("8.8.8.8")
    assert "this computer only" in hosting.address_label("localhost")


def test_the_form_refuses_ports_that_clash_or_dont_exist(host):
    form = hosting_forms.host_form()
    assert form.validate is not None
    assert form.validate(_values(8000, ssh=True, ssh_port=8000)) is not None
    assert form.validate(_values(70000)) is not None
    assert form.validate(_values(8000, address=hosting_forms.OTHER)) is not None
    assert form.validate(_values(8000, ssh=True, ssh_port=2222)) is None
    assert form.live is not None
    assert "ssh -p 2222 player@localhost" in form.live(
        _values(8000, ssh=True, ssh_port=2222)
    )


def test_host_for_players_starts_the_host_and_stop_hosting_ends_it(host):
    saga = Saga(id="test", name="Test")
    page = menu_forms.Page(saga, NodeKind.SAGA)
    assert menu_forms.placed(page, "Saga Management")[-1].action == "host_saga"
    port = _free_port()
    form = menu_forms.command(page, "host_saga")
    assert isinstance(form, Form)
    said = form.apply(_values(port))
    assert host.running, said
    assert f"http://localhost:{port}" in said[0]
    with urllib.request.urlopen(f"http://localhost:{port}", timeout=5) as page_:
        assert b"Armarius" in page_.read()
    # A request addressed to another name (DNS rebinding) gets nothing.
    rebound = urllib.request.Request(
        f"http://localhost:{port}", headers={"Host": f"evil.example:{port}"}
    )
    with pytest.raises(urllib.error.HTTPError) as refused:
        urllib.request.urlopen(rebound, timeout=5)
    assert refused.value.code == 403
    # Saga Management now offers Stop Hosting, saying where it is hosted.
    actions = [i.action for i in menu_forms.placed(page, "Saga Management")]
    assert "stop_hosting" in actions and "host_saga" not in actions
    assert f"localhost:{port}" in menu_forms.management_note("stop_hosting")
    # Where it was hosted is remembered for next time.
    assert settings.load_settings()["hosting"]["port"] == port
    assert hosting.last_plan().port == port

    stop = menu_forms.command(page, "stop_hosting")
    assert isinstance(stop, Confirm)
    stop.apply()
    assert not host.running
    with pytest.raises(OSError):
        urllib.request.urlopen(f"http://localhost:{port}", timeout=2)


def test_a_port_in_use_is_refused_before_anything_starts(host):
    with socket.socket() as taken:
        taken.bind(("localhost", 0))
        taken.listen()
        port = taken.getsockname()[1]
        said = hosting_forms.host_form().apply(_values(port))
    assert isinstance(said, Refuse)
    assert f"Port {port} is in use" in said.why
    assert not host.running


def test_a_public_address_is_refused_unless_the_storyguide_insists(host):
    form = hosting_forms.host_form()
    public = _values(_free_port(), address="8.8.8.8")
    said = form.apply(public)
    assert isinstance(said, Refuse)
    assert "reachable from the internet" in said.why
    assert not host.running
    # The box to insist shows only for such an address (or one typed in).
    box = next(f for f in form.fields() if f.key == "public_ok")
    assert box.show_if is not None
    assert box.show_if(public)
    assert box.show_if(_values(8000, address=hosting_forms.OTHER))
    assert not box.show_if(_values(8000))
    assert not box.show_if(_values(8000, address="100.64.1.2"))
    # Insisting gets past the guard (here, to the address this computer
    # hasn't got) and tells the server so; it is never remembered.
    said = form.apply(public | {"public_ok": True})
    assert isinstance(said, Refuse)
    assert "reachable from the internet" not in said.why
    plan = hosting_forms.plan_of(public | {"public_ok": True})
    assert plan.arguments()[-1] == hosting.ALLOW_PUBLIC
    assert hosting_forms.plan_of(_values(8000, public_ok=True)).public_ok is False


def test_the_server_refuses_a_public_address_itself():
    with pytest.raises(SystemExit) as refused:
        serve.main(["--host", "0.0.0.0"])
    assert hosting.ALLOW_PUBLIC in str(refused.value)


def test_a_players_copy_never_hosts(host, monkeypatch):
    monkeypatch.setenv(hosting.TRANSPORT_VAR, "web")
    page = menu_forms.Page(Saga(id="test", name="Test"), NodeKind.SAGA)
    actions = [i.action for i in menu_forms.placed(page, "Saga Management")]
    assert "host_saga" not in actions
    assert host.start(hosting.Plan(port=_free_port())) is not None
