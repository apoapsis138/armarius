"""Invites: one-time, short-lived, hashed on the host, approved by the Storyguide."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ars_magica_manager import players
from ars_magica_manager.models import Saga
from ars_magica_manager.remote import invites
from ars_magica_manager.remote.invites import (
    APPROVED,
    PENDING,
    REJECTED,
    InviteBook,
    InviteError,
)
from ars_magica_manager.remote.words import (
    DEVICE_WORDS,
    HOST_WORDS,
    device_words,
    host_words,
    two_lines,
    wordlist,
    words_from_digest,
)

SECRET = "ab" * 16


class Clock:
    def __init__(self) -> None:
        self.now = 1_000_000.0

    def __call__(self) -> float:
        return self.now


@pytest.fixture
def clock() -> Clock:
    return Clock()


@pytest.fixture
def book(tmp_path: Path, clock: Clock) -> InviteBook:
    return InviteBook(tmp_path / "invites.json", clock)


def test_an_invite_is_redeemed_once(book: InviteBook) -> None:
    code = book.issue("p1")
    request = book.redeem(code, "Anna's laptop", SECRET)
    assert request.player_id == "p1" and request.state == PENDING
    with pytest.raises(InviteError, match="already used"):
        book.redeem(code, "another", "cd" * 16)


def test_a_code_is_read_however_it_is_pasted(book: InviteBook) -> None:
    code = book.issue("p1")
    messy = " " + code.replace("-", " ").lower() + "\n"
    assert book.redeem(messy, "laptop", SECRET).player_id == "p1"


def test_an_invite_expires_after_a_day(book: InviteBook, clock: Clock) -> None:
    code = book.issue("p1")
    clock.now += invites.INVITE_TTL + 1
    with pytest.raises(InviteError, match="expired"):
        book.redeem(code, "laptop", SECRET)


def test_a_guessed_code_is_refused(book: InviteBook) -> None:
    book.issue("p1")
    for guess in ("AAAA-AAAA", "", invites.new_code(), "x" * 200):
        with pytest.raises(InviteError):
            book.redeem(guess, "laptop", SECRET)


@pytest.mark.parametrize("secret", ["", "short", "ab" * 17 + "!", "é" * 32, "a" * 65])
def test_a_badly_shaped_secret_is_refused_and_the_invite_kept(
    book: InviteBook, secret: str
) -> None:
    code = book.issue("p1")
    with pytest.raises(InviteError, match="secret"):
        book.redeem(code, "laptop", secret)
    assert book.redeem(code, "laptop", SECRET).state == PENDING  # still good


def test_the_same_secret_cannot_make_two_requests(book: InviteBook) -> None:
    book.redeem(book.issue("p1"), "a", SECRET)
    with pytest.raises(InviteError, match="secret already used"):
        book.redeem(book.issue("p2"), "b", SECRET)


def test_the_host_keeps_only_hashes(book: InviteBook, tmp_path: Path) -> None:
    code = book.issue("p1")
    book.redeem(code, "laptop", SECRET)
    text = (tmp_path / "invites.json").read_text(encoding="utf-8")
    assert code not in text and code.replace("-", "") not in text
    assert SECRET not in text


def test_the_storyguide_approves_what_is_pending(book: InviteBook) -> None:
    request = book.redeem(book.issue("p1"), "laptop", SECRET)
    assert [r.id for r in book.pending()] == [request.id]
    assert book.approve(request.id).state == APPROVED
    assert book.pending() == []
    assert book.status(SECRET).state == APPROVED


def test_the_storyguide_rejects(book: InviteBook) -> None:
    request = book.redeem(book.issue("p1"), "laptop", SECRET)
    book.reject(request.id)
    assert book.status(SECRET).state == REJECTED


def test_a_decision_is_made_once(book: InviteBook) -> None:
    request = book.redeem(book.issue("p1"), "laptop", SECRET)
    book.approve(request.id)
    for decide in (book.approve, book.reject):
        with pytest.raises(InviteError):
            decide(request.id)
    with pytest.raises(InviteError):
        book.approve("no such request")


def test_a_request_the_storyguide_never_answered_lapses(
    book: InviteBook, clock: Clock
) -> None:
    request = book.redeem(book.issue("p1"), "laptop", SECRET)
    clock.now += invites.REQUEST_TTL + 1
    assert book.pending() == []
    with pytest.raises(InviteError, match="lapsed"):
        book.status(SECRET)
    with pytest.raises(InviteError):
        book.approve(request.id)


def test_a_wrong_secret_learns_nothing(book: InviteBook) -> None:
    book.redeem(book.issue("p1"), "laptop", SECRET)
    with pytest.raises(InviteError):
        book.status("cd" * 16)


def test_the_book_survives_a_restart(tmp_path: Path, clock: Clock) -> None:
    first = InviteBook(tmp_path / "b.json", clock)
    code = first.issue("p1")
    again = InviteBook(tmp_path / "b.json", clock)
    assert again.redeem(code, "laptop", SECRET).player_id == "p1"
    assert InviteBook(tmp_path / "b.json", clock).status(SECRET).state == PENDING


def test_a_damaged_book_is_reported(tmp_path: Path) -> None:
    path = tmp_path / "b.json"
    for text in ("not json", "[]", json.dumps({"invites": {"x": 1}, "requests": {}})):
        path.write_text(text, encoding="utf-8")
        with pytest.raises(ValueError, match="cannot be read"):
            InviteBook(path)


def test_old_decided_requests_are_forgotten(tmp_path: Path, clock: Clock) -> None:
    book = InviteBook(tmp_path / "b.json", clock)
    request = book.redeem(book.issue("p1"), "laptop", SECRET)
    book.approve(request.id)
    clock.now += invites.DECIDED_KEEP + 1
    book.issue("p2")  # any change saves, and prunes
    with pytest.raises(InviteError):
        book.status(SECRET)


def test_the_book_lives_in_the_data_folder_not_the_saga() -> None:
    path = invites.book_path("My Saga/../x")
    assert path.parent.name == "remote" and path.name == "My_Saga____x-invites.json"


def test_players_and_storyguides_can_be_invited(tmp_path: Path) -> None:
    saga = Saga(id="s", name="S")
    anna = players.add(saga, {"name": "Anna", "role": players.PLAYER, "passcode": "p"})
    players.add(saga, {"name": "GM", "role": players.STORYGUIDE, "passcode": "p"})
    book = InviteBook(tmp_path / "invites.json")
    assert book.issue(anna.id)
    assert invites.issue_for(book, saga, "GM")
    with pytest.raises(ValueError, match="not a Player"):
        invites.issue_for(book, saga, "Nobody")


def test_the_invite_text_round_trips_and_is_one_pasteable_line() -> None:
    pin = "ab" * 32
    text = invites.encode_invite("wss://game.example.com/remote", pin, "ABCD-EFGH")
    assert "\n" not in text and " " not in text and "?" not in text and "/" not in text
    parts = invites.decode_invite("  " + text[:20] + "\n" + text[20:] + " ")
    assert (parts.url, parts.pin, parts.code) == (
        "wss://game.example.com/remote",
        pin,
        "ABCDEFGH",
    )


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "hello",
        "ARM2.AA.bb.cc",
        "ARM1.!!!.00.00",
        "ARM1." + "a" * 5 + "." + "ab" * 32 + ".CODE",
    ],
)
def test_text_that_is_not_an_invite_is_refused(bad: str) -> None:
    with pytest.raises(ValueError):
        invites.decode_invite(bad)


@pytest.mark.parametrize(
    "url",
    [
        "http://game.example.com/remote",
        "wss:///remote",
        "wss://game.example.com/remote?token=x",
        "wss://user@game.example.com/remote",
        "wss://game.example.com/remote#x",
        "wss://" + "a" * 400,
    ],
)
def test_an_invite_naming_an_unsafe_address_is_refused(url: str) -> None:
    with pytest.raises(ValueError):
        invites.decode_invite(invites.encode_invite(url, "ab" * 32, "CODE"))


def test_the_word_list_is_the_2048_expected() -> None:
    words = wordlist()
    assert len(words) == 2048 and words[0] == "abandon" and words[-1] == "zoo"


def test_words_follow_the_hash() -> None:
    zero = "0" * 64
    assert words_from_digest(zero, 3) == ("abandon",) * 3
    top = "f" * 64
    assert words_from_digest(top, 2) == ("zoo", "zoo")
    # Eleven bits each, in order: 0x001 then 0x7ff.
    assert words_from_digest("001" + "f" * 61, 1)[0] == wordlist()[0]
    assert words_from_digest("0" * 3 + "f" * 61, 2)[0] == wordlist()[0]
    with pytest.raises(ValueError):
        words_from_digest(zero, 0)
    with pytest.raises(ValueError):
        words_from_digest(zero, 24)


def test_the_host_has_six_words_and_a_device_three() -> None:
    pin = "ab" * 32
    assert len(host_words(pin)) == HOST_WORDS == 6
    assert host_words(pin.upper()) == host_words(pin)  # however it was pasted
    assert len(device_words(SECRET)) == DEVICE_WORDS == 3
    assert device_words(SECRET) == device_words(SECRET)
    assert device_words(SECRET) != device_words("cd" * 16)


def test_words_are_laid_out_three_to_a_line() -> None:
    assert two_lines(("a", "b", "c", "d", "e", "f")) == "a b c\nd e f"
