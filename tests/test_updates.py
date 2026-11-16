"""App updates (updates.py): reading a Release's version, which copies
check, the day's limit, skipping, security fixes, failures, and the
Version mismatch messages for Remote seats."""

from __future__ import annotations

import json
import urllib.error
from collections.abc import Mapping

import pytest

import main
from ars_magica_manager import ROOT, settings, updates
from ars_magica_manager.remote.devices import DeviceBook
from ars_magica_manager.remote.protocol import HELLO, Session

DAY = updates.INTERVAL
#: A mark that reverses the text after it on screen.
RTL_OVERRIDE = chr(0x202E)


def _answer(
    tag: str = "v9.1.0", body: str = "### Pagina\n\n- **New.** Things."
) -> bytes:
    return json.dumps(
        {
            "tag_name": tag,
            "published_at": "2026-12-01T10:00:00Z",
            "body": body,
            "html_url": f"{updates.RELEASES_URL}/tag/{tag}",
        }
    ).encode()


class Fake:
    """GitHub, as a test answers it: counts the requests and what they sent."""

    def __init__(self, answer: bytes = b"", error: Exception | None = None) -> None:
        self.answer = answer or _answer()
        self.error = error
        self.asked: list[tuple[str, dict[str, str], float]] = []

    def __call__(self, url: str, headers: Mapping[str, str], timeout: float) -> bytes:
        self.asked.append((url, dict(headers), timeout))
        if self.error is not None:
            raise self.error
        return self.answer


@pytest.fixture
def checking(monkeypatch: pytest.MonkeyPatch) -> updates.Copy:
    """A copy that checks: the suite turns checks off everywhere else."""
    monkeypatch.delenv(updates.ENV_VAR, raising=False)
    return updates.Build()


# -- versions --


@pytest.mark.parametrize(
    ("text", "version"),
    [
        ("v4.13.1", (4, 13, 1)),
        ("4.14.0", (4, 14, 0)),
        (" v10.0.12 ", (10, 0, 12)),
        ("v4.14", None),
        ("v4.14.0-beta", None),
        ("latest", None),
        ("", None),
        (None, None),
        (4, None),
    ],
)
def test_a_tag_is_read_as_three_whole_numbers_or_not_at_all(
    text: object, version: tuple[int, int, int] | None
) -> None:
    assert updates.parse_version(text) == version


def test_newer_compares_each_number_not_the_text() -> None:
    assert updates.is_newer("4.13.10", "4.13.9")
    assert updates.is_newer("5.0.0", "4.99.99")
    assert not updates.is_newer("4.13.1", "4.13.1")
    assert not updates.is_newer("4.12.0", "4.13.0")
    assert not updates.is_newer("rubbish", "4.13.0")


# -- which copies check --


def test_builds_and_checkouts_check_and_differ_in_how_they_update() -> None:
    build = updates.this_copy(frozen=True, env={})
    checkout = updates.this_copy(frozen=False, env={})
    assert build.checks and checkout.checks
    assert build.download == "Download page"
    assert not checkout.download and "pull main" in checkout.how_to_update


@pytest.mark.parametrize(
    "kind", [{"by_word": True}, {"hosted": True}, {"env": {"ARMARIUS_UPDATES": "off"}}]
)
def test_hosts_players_copies_and_the_switch_never_check(
    kind: dict[str, object],
) -> None:
    options: dict[str, object] = {"frozen": True, "env": {}} | kind
    copy = updates.this_copy(**options)  # type: ignore[arg-type]
    assert not copy.checks
    fake = Fake()
    assert updates.check(copy, now_asked=True, fetch=fake) == updates.Result(False)
    assert fake.asked == []


def test_the_launch_words_play_copy_is_quiet(monkeypatch: pytest.MonkeyPatch) -> None:
    """main.py's `play` word (a player's copy a host runs) starts the
    terminal app as a copy that never checks."""
    seen: list[bool] = []
    monkeypatch.setattr(main, "main", lambda *, by_word=False: seen.append(by_word))
    main.WORDS["play"]([])
    assert seen == [True]


def test_the_container_image_turns_checks_off() -> None:
    dockerfile = (ROOT / "deploy" / "Dockerfile").read_text(encoding="utf-8")
    assert "ARMARIUS_UPDATES=off" in dockerfile


# -- the check --


def test_the_check_sends_only_the_version(checking: updates.Copy) -> None:
    fake = Fake()
    updates.check(checking, now_asked=True, fetch=fake)
    url, headers, timeout = fake.asked[0]
    assert url == updates.API_URL
    assert headers["User-Agent"] == f"Armarius/{updates.__version__}"
    assert set(headers) == {"User-Agent", "Accept"}
    assert timeout == 5.0


def test_the_check_at_start_runs_once_a_day(checking: updates.Copy) -> None:
    fake = Fake()
    now = 1_000_000.0
    assert updates.check(checking, fetch=fake, clock=lambda: now).ran
    assert not updates.check(checking, fetch=fake, clock=lambda: now + DAY - 1).ran
    assert updates.check(checking, fetch=fake, clock=lambda: now + DAY).ran
    assert len(fake.asked) == 2
    # Check now ignores the day's limit.
    assert updates.check(
        checking, now_asked=True, fetch=fake, clock=lambda: now + DAY
    ).ran


def test_a_clock_set_back_checks_again() -> None:
    assert updates.due(100.0, 100.0 + DAY)
    assert updates.due(0.0, None)
    assert updates.due(0.0, "yesterday")


def test_the_setting_turns_the_check_at_start_off_but_not_check_now(
    checking: updates.Copy,
) -> None:
    assert updates.check_at_start()
    updates.set_check_at_start(False)
    fake = Fake()
    assert not updates.check(checking, fetch=fake).ran
    assert updates.check(checking, now_asked=True, fetch=fake).ran
    # Off shows nothing, whatever was found.
    assert updates.notice(checking, running="4.13.1") is None


@pytest.mark.parametrize(
    ("error", "said"),
    [
        (urllib.error.URLError("no route to host"), "no route to host"),
        (TimeoutError(), "didn't answer in time"),
        (
            urllib.error.HTTPError(
                updates.API_URL, 403, "rate limit exceeded", {}, None
            ),  # type: ignore[arg-type]
            "403",
        ),
        (OSError("network is down"), "network is down"),
    ],
)
def test_a_failed_check_says_why_and_remembers_nothing(
    checking: updates.Copy, error: Exception, said: str
) -> None:
    result = updates.check(checking, now_asked=True, fetch=Fake(error=error))
    assert result.ran and said in result.problem
    assert updates.outcome_text(result).startswith("Couldn't reach GitHub: ")
    kept = settings.load_settings()
    assert updates.LAST_CHECK not in kept and updates.FOUND not in kept


def test_an_unreadable_answer_is_a_failure(checking: updates.Copy) -> None:
    result = updates.check(checking, now_asked=True, fetch=Fake(answer=b"<html>"))
    assert "couldn't be read" in result.problem


def test_a_tag_that_isnt_a_version_is_ignored(checking: updates.Copy) -> None:
    result = updates.check(checking, now_asked=True, fetch=Fake(_answer("nightly")))
    assert result.ran and result.release is None
    assert updates.notice(checking, running="4.13.1") is None


def test_check_now_says_what_it_found(checking: updates.Copy) -> None:
    found = updates.check(checking, now_asked=True, fetch=Fake(_answer("v9.1.0")))
    assert updates.outcome_text(found, "4.13.1") == "Armarius 9.1.0 is available."
    assert "latest version" in updates.outcome_text(found, "9.1.0")
    assert "turned off" in updates.outcome_text(updates.Result(False))


# -- the notice --


def test_a_newer_release_is_noticed_with_its_first_lines(
    checking: updates.Copy,
) -> None:
    body = "### Pagina\n\n- **My sheet.** Opens your sheet.\n- **The trail.** Lists.\n- Third."
    updates.check(checking, now_asked=True, fetch=Fake(_answer("v4.14.0", body)))
    notice = updates.notice(checking, running="4.13.1")
    assert notice is not None
    assert notice.headline == "Armarius 4.14.0 is available"
    assert notice.date == "2026-12-01"
    assert notice.lines == ("My sheet. Opens your sheet.", "The trail. Lists.")
    assert notice.kind == updates.UPDATE and notice.can_skip and notice.shown
    assert not notice.remote  # the same major version
    assert notice.download == "Download page"


def test_nothing_is_noticed_when_this_version_is_as_new_or_newer(
    checking: updates.Copy,
) -> None:
    updates.check(checking, now_asked=True, fetch=Fake(_answer("v4.14.0")))
    assert updates.notice(checking, running="4.14.0") is None
    assert updates.notice(checking, running="4.15.0") is None


def test_a_skipped_version_is_hidden_until_a_newer_one(checking: updates.Copy) -> None:
    updates.check(checking, now_asked=True, fetch=Fake(_answer("v4.14.0")))
    updates.skip("4.14.0")
    notice = updates.notice(checking, running="4.13.1")
    assert notice is not None and notice.skipped and not notice.shown
    updates.check(checking, now_asked=True, fetch=Fake(_answer("v4.15.0")))
    newer = updates.notice(checking, running="4.13.1")
    assert newer is not None and newer.shown


def test_a_security_update_stands_out_and_cannot_be_skipped(
    checking: updates.Copy,
) -> None:
    body = "### Sodales\n\n- Fixes.\n- **Security:** A hole closed."
    updates.check(checking, now_asked=True, fetch=Fake(_answer("v4.14.0", body)))
    updates.skip("4.14.0")
    notice = updates.notice(checking, running="4.13.1")
    assert notice is not None
    assert notice.kind == updates.SECURITY and notice.security
    assert notice.headline == "Armarius 4.14.0 is available, with security fixes"
    assert not notice.can_skip and notice.shown


def test_only_a_bullet_marked_security_counts() -> None:
    assert updates.has_security_marker("- **Security:** A hole closed.")
    assert updates.has_security_marker("### Sodales\n\n  * **security:** fixed")
    assert not updates.has_security_marker("### Security\n\n- Closed.")
    assert not updates.has_security_marker("- **Security review.** Done.")
    assert not updates.has_security_marker("Security: mentioned in text")


def test_a_new_major_version_tells_of_remote_seats(checking: updates.Copy) -> None:
    updates.check(checking, now_asked=True, fetch=Fake(_answer("v5.0.0")))
    notice = updates.notice(checking, running="4.13.1")
    assert notice is not None and "Remote seat" in notice.remote


def test_a_checkout_offers_pull_main_not_the_download_page(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(updates.ENV_VAR, raising=False)
    copy = updates.Checkout()
    updates.check(copy, now_asked=True, fetch=Fake(_answer("v9.0.0")))
    notice = updates.notice(copy, running="4.13.1")
    assert notice is not None and not notice.download
    assert "pull main" in notice.how_to_update


def test_release_notes_are_kept_as_plain_text_and_the_page_on_github() -> None:
    release = updates.release_from(
        {
            "tag_name": "v4.14.0",
            "published_at": "not a date",
            "body": "<script>x</script>\r\nline\x00\x1b[31m"
            + RTL_OVERRIDE
            + "evil"
            + "a" * 30_000,
            "html_url": "https://evil.example/release",
        }
    )
    assert release is not None
    assert release.url == updates.LATEST_URL
    assert release.date == ""
    assert "\x00" not in release.notes and "\x1b" not in release.notes
    assert RTL_OVERRIDE not in release.notes and "\r" not in release.notes
    # Kept as text: drawing it is the front-end's business, as plain text.
    assert release.notes.startswith("<script>x</script>\nline")
    assert len(release.notes) <= updates.MAX_NOTES


def test_damaged_settings_show_nothing(checking: updates.Copy) -> None:
    settings.update_settings(**{updates.FOUND: "not a dict"})
    assert updates.notice(checking) is None
    settings.update_settings(**{updates.FOUND: {"version": 7}})
    assert updates.notice(checking) is None


# -- Version mismatch --


def test_the_same_version_is_no_mismatch() -> None:
    assert updates.mismatch("4.13.1", "4.13.1") is None
    assert updates.mismatch("4.13.1", "") is None


def test_a_major_mismatch_when_this_app_is_older_offers_update() -> None:
    found = updates.mismatch("4.13.1", "5.0.0")
    assert found is not None and found.major and found.older and found.offers_update
    assert "update this app" in found.message


def test_a_major_mismatch_when_the_host_is_older_asks_them_to_update() -> None:
    found = updates.mismatch("5.0.0", "4.13.1")
    assert found is not None and found.major and not found.offers_update
    assert found.message == (
        "Your storyguide's Armarius is older (4.13.1). Ask them to update."
    )


@pytest.mark.parametrize(
    ("ours", "theirs"), [("4.13.1", "4.14.0"), ("4.13.1", "4.13.0")]
)
def test_a_minor_mismatch_lets_you_play_untested(ours: str, theirs: str) -> None:
    found = updates.mismatch(ours, theirs)
    assert found is not None and not found.major
    assert found.message == (
        f"Your host runs Armarius {theirs}, and you run {ours}. You can play, "
        "but these versions haven't been tested together, so some things may "
        "behave oddly."
    )
    notice = updates.mismatch_notice(found, updates.Build())
    assert notice.kind == updates.MISMATCH and notice.shown and not notice.can_skip
    assert notice.download == ("Update" if found.older else "")


def test_the_storyguide_sees_a_seats_other_version() -> None:
    assert updates.seat_note("4.13.0", "4.13.1") == "4.13.0, not tested with yours"
    assert updates.seat_note("4.13.1", "4.13.1") == ""
    assert updates.seat_note("", "4.13.1") == ""


def test_the_host_keeps_a_seats_version_on_its_connection_and_device(tmp_path) -> None:
    session = Session()
    HELLO.handler(session, {"protocol": 1, "app": "4.12.0"})
    assert session.app_version == "4.12.0"
    book = DeviceBook(tmp_path / "devices.json")

    class Asked:
        id, player_id, device, words = "dev1", "anna", "Laptop", "a b c"

    book.enrol(Asked())  # type: ignore[arg-type]
    device = book.get("dev1")
    assert device is not None
    book.signed_in(device, session.app_version)
    assert book.seat_versions() == {"anna": "4.12.0"}
    # The file keeps it for the storyguide's window, which reads it apart.
    assert DeviceBook(tmp_path / "devices.json").seat_versions() == {"anna": "4.12.0"}
