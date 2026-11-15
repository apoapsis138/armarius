"""The guards in front of browser and SSH hosting: public addresses, who a
request is addressed to, the exports-only file chooser, and the sign-in's
waits and passcode length."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from textual.widgets import Button, Input, Static

from ars_magica_manager import hosted_signin, hosting, lockout, settings, storage
from ars_magica_manager import players as pl
from ars_magica_manager.models import Saga
from ars_magica_manager.remote.passcodes import RemotePasscodes, passcodes_path
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens.pickers import OUTSIDE_EXPORTS, CsvFilePickerScreen

LONG = "a long enough passcode"
SHORT = "rosemary"


@pytest.mark.parametrize(
    ("address", "public"),
    [
        ("8.8.8.8", True),
        ("0.0.0.0", True),
        ("::", True),
        ("", True),
        ("2001:4860:4860::8888", True),
        ("localhost", False),
        ("127.0.0.1", False),
        ("192.168.1.5", False),
        ("10.0.0.2", False),
        ("100.101.2.3", False),  # Tailscale
        ("fd00::5", False),
    ],
)
def test_public_addresses_are_told_apart(address: str, public: bool) -> None:
    assert hosting.is_public(address) is public


def test_a_name_is_looked_up_only_when_asked(monkeypatch: pytest.MonkeyPatch) -> None:
    def found(*_args: object) -> list[tuple[object, ...]]:
        return [(0, 0, 0, "", ("8.8.4.4", 0))]

    monkeypatch.setattr(hosting.socket, "getaddrinfo", found)
    assert hosting.is_public("my-pc.example")
    assert not hosting.is_public("my-pc.example", resolve=False)


def test_a_request_must_be_addressed_to_the_host() -> None:
    allowed = hosting.allowed_hosts("100.64.1.2", 8000)
    assert allowed == frozenset({"100.64.1.2:8000"})
    ok = hosting.request_allowed
    assert ok("100.64.1.2:8000", None, False, allowed)
    # DNS rebinding: a hostile name pointed at this computer.
    assert not ok("evil.example:8000", None, False, allowed)
    assert not ok(None, None, False, allowed)
    # The app's own connection only from the host's own page.
    assert ok("100.64.1.2:8000", "http://100.64.1.2:8000", True, allowed)
    assert not ok("100.64.1.2:8000", "http://evil.example", True, allowed)
    assert not ok("100.64.1.2:8000", None, True, allowed)
    assert not ok("100.64.1.2:8000", "null", True, allowed)


def test_localhost_answers_to_each_of_its_names() -> None:
    allowed = hosting.allowed_hosts("localhost", 8000)
    for name in ("localhost:8000", "127.0.0.1:8000", "[::1]:8000"):
        assert hosting.request_allowed(name, f"http://{name}", True, allowed)
    assert hosting.allowed_hosts("my-pc", 80) == frozenset({"my-pc", "my-pc:80"})


# -- the file chooser ---------------------------------------------------------


def test_the_storyguides_own_window_may_browse_anywhere(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(hosting.TRANSPORT_VAR, raising=False)
    monkeypatch.delenv(hosting.OLD_TRANSPORT_VAR, raising=False)
    assert hosting.confined_chooser() is None


def test_a_hosted_copys_chooser_keeps_to_the_exports_folder(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv(hosting.TRANSPORT_VAR, "web")
    confined = hosting.confined_chooser()
    assert confined is not None
    exports = storage.exports_dir().resolve()
    assert confined.root == exports and exports.is_dir()
    (exports / "Characters").mkdir()
    (exports / "Characters" / "ana.json").write_text("{}")
    outside = tmp_path / "secret.json"
    outside.write_text("{}")

    assert confined.start(tmp_path) == exports
    assert confined.start(exports / "Characters") == exports / "Characters"
    assert confined.up(exports) == exports
    assert confined.up(exports / "Characters") == exports
    assert confined.show(exports / "Characters" / "ana.json") == (
        "exports/Characters/ana.json"
    )
    assert confined.show(exports) == "exports"
    assert confined.find("exports/Characters/ana.json") == (
        exports / "Characters" / "ana.json"
    )
    assert confined.find("Characters") == exports / "Characters"
    assert confined.find("exports") == exports
    for escape in ("..", "exports/../..", str(outside), "../secret.json"):
        assert confined.find(escape) is None, escape
    drive = confined.find("C:/Windows")
    if sys.platform == "win32":
        assert drive is None
    else:  # "C:" is only a folder's name here, and it stays inside exports
        assert drive is None or drive.is_relative_to(exports)


async def test_the_terminal_chooser_shows_and_takes_only_the_exports_folder(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv(hosting.TRANSPORT_VAR, "web")
    confined = hosting.confined_chooser()
    assert confined is not None
    (confined.root / "ana.json").write_text("{}")
    outside = tmp_path / "secret.json"
    outside.write_text("{}")
    chosen: list[Path | None] = []
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = CsvFilePickerScreen(
            "Import", tmp_path, suffix=".json", confined=confined
        )
        app.push_screen(screen, chosen.append)
        await pilot.pause()
        path_box = screen.query_one("#picker-path", Input)
        assert path_box.value == "exports"  # never the host's own path
        screen.query_one("#btn-picker-up", Button).press()
        await pilot.pause()
        assert path_box.value == "exports"  # Up stops at the folder
        error = screen.query_one("#picker-error", Static)
        path_box.focus()
        for typed in (str(outside), "../secret.json"):
            path_box.value = typed
            await pilot.press("enter")
            await pilot.pause()
            assert OUTSIDE_EXPORTS in str(error.render())
        path_box.value = "exports/ana.json"
        await pilot.press("enter")
        await pilot.pause()
    assert chosen == [confined.root / "ana.json"]


# -- signing in ---------------------------------------------------------------


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def _saga(passcode: str = LONG) -> tuple[Saga, pl.Player]:
    saga = Saga(id="dammerstein", name="Dammerstein")
    player = pl.add(saga, {"name": "Ana", "role": pl.PLAYER, "passcode": passcode})
    storage.save_saga(saga)
    return saga, player


def _book(clock: Clock | None = None) -> hosted_signin.SignInBook:
    return hosted_signin.SignInBook(
        hosted_signin.book_path("Dammerstein"), clock or Clock()
    )


def test_wrong_passcodes_wait_as_a_remote_seats_do() -> None:
    saga, player = _saga()
    clock = Clock()
    book = _book(clock)
    for _ in range(lockout.FREE_FAILURES - 1):
        found = hosted_signin.attempt(book, saga, "Ana", "wrong")
        assert found.refused == hosted_signin.REFUSED
    found = hosted_signin.attempt(book, saga, "ana ", "wrong")  # same name
    assert found.refused == lockout.wait_text(int(lockout.LOCK_STEPS[0]))
    # Even the right passcode waits; another copy (a new book) sees it too.
    found = hosted_signin.attempt(_book(clock), saga, "Ana", LONG)
    assert found.player is None and "try again in" in found.refused
    clock.now += lockout.LOCK_STEPS[0]
    found = hosted_signin.attempt(book, saga, "Ana", LONG)
    assert found.player == player and not found.short
    # A right passcode clears the count.
    assert hosted_signin.attempt(book, saga, "Ana", "wrong").refused == (
        hosted_signin.REFUSED
    )


def test_a_made_up_name_waits_the_same() -> None:
    saga, _ = _saga()
    book = _book()
    for _ in range(lockout.FREE_FAILURES):
        found = hosted_signin.attempt(book, saga, "Nobody", "wrong")
    assert "try again in" in found.refused


def test_a_short_passcode_signs_in_once_more() -> None:
    saga, player = _saga(SHORT)
    book = _book()
    found = hosted_signin.attempt(book, saga, "Ana", SHORT)
    assert found.player == player and found.short and found.may_put_off
    book.spend_short(player)
    found = hosted_signin.attempt(book, saga, "Ana", SHORT)
    assert found.player is None and found.refused == hosted_signin.SHORT_SPENT
    # The storyguide sets a new one, even another short one: it starts afresh.
    pl.set_passcode(player, "thyme")
    storage.save_saga(saga)
    found = hosted_signin.attempt(book, saga, "Ana", "thyme")
    assert found.player == player and found.short


def test_a_new_passcode_is_saved_and_long_enough_for_a_remote_seat() -> None:
    saga, player = _saga(SHORT)
    assert hosted_signin.change_passcode(saga, player, "too short") == (
        pl.passcode_problem("too short")
    )
    assert hosted_signin.change_passcode(saga, player, LONG) is None
    saved = storage.load_saga(saga.id)
    assert pl.sign_in(saved, "Ana", LONG) is not None
    assert saved.saved_by == "Ana"
    assert RemotePasscodes(passcodes_path(saga.name)).allows(saved.players[0])
    found = hosted_signin.attempt(_book(), saved, "Ana", LONG)
    assert found.player is not None and not found.short


# -- a hosted copy and the host's settings ------------------------------------


async def test_a_hosted_copy_has_no_command_palette_and_writes_no_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(hosting.TRANSPORT_VAR, "web")
    before = settings.load_settings().get("theme")
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        assert not app.use_command_palette
        app.theme = "textual-dark"
        await pilot.pause()
    assert settings.load_settings().get("theme") == before


async def test_the_storyguides_window_keeps_its_palette_and_theme(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(hosting.TRANSPORT_VAR, raising=False)
    monkeypatch.delenv(hosting.OLD_TRANSPORT_VAR, raising=False)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        assert app.use_command_palette
        app.theme = "textual-dark"
        await pilot.pause()
    assert settings.load_settings().get("theme") == "textual-dark"
