"""App updates: whether a newer Release of Armarius is out, and how each
front-end should tell of it (the App update notice).

This module is the one place that knows GitHub's API (a Facade, as
launch.py is for starting copies of the app): callers ask whether this copy
checks, run a check, and get back a Notice describing what to show (the
version, its date, the first lines of its notes, whether it brings
security fixes). Each front-end draws the Notice its own way (ADR 0001).

What a copy does is chosen by a small Strategy, `Copy`: a Build and a
checkout both check, but a checkout is updated with `git pull` rather than
from the Download page; a copy started with one of launch's words (the
hosts, a player's copy, admin) and a hosted player's copy never check.

The check sends one request, to GitHub's API, read-only, with the app's
version as its User-Agent and nothing else about the user. Release notes
come from the network, so they are untrusted: they are kept as plain
text, never drawn as HTML or markup, and a Release's address is used only
when it is on the app's own GitHub page.
"""

from __future__ import annotations

import json
import os
import re
import ssl
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Protocol

from . import FROZEN, __version__, settings

#: The latest Release, as GitHub's API describes it.
API_URL = "https://api.github.com/repos/apoapsis138/armarius/releases/latest"
#: The app's Releases on GitHub: where a newer one is downloaded.
RELEASES_URL = "https://github.com/apoapsis138/armarius/releases"
#: The latest Release's own page.
LATEST_URL = RELEASES_URL + "/latest"
#: How long a check waits for GitHub, in seconds.
TIMEOUT = 5.0
#: How often the check at start-up runs at most, in seconds.
INTERVAL = 24 * 3600.0

#: "off" here turns every check off, Check now included (the container
#: image sets it).
ENV_VAR = "ARMARIUS_UPDATES"
#: The settings: whether to check at start-up (on unless turned off), when
#: the last check was, the version skipped, and what the last check found.
CHECK = "update_check"
LAST_CHECK = "update_last_check"
SKIPPED = "update_skipped"
FOUND = "update_found"

#: The most of a Release's notes kept: more is cut off.
MAX_NOTES = 20_000
#: The most of one line of notes a notice shows.
MAX_LINE = 160

#: The kinds of notice.
UPDATE, SECURITY, MISMATCH = "update", "security", "mismatch"

Version = tuple[int, int, int]

_TAG = re.compile(r"v?(\d{1,4})\.(\d{1,4})\.(\d{1,6})")
_DATE = re.compile(r"(\d{4}-\d{2}-\d{2})")
#: A changelog bullet marked as a security fix: `- **Security:** ...`.
_SECURITY_MARKER = re.compile(r"^\s*[-*]\s+\*\*security:\*\*", re.IGNORECASE)
#: Characters a note never keeps: control characters other than newline and
#: tab, and the marks that reorder text on screen.
_UNSAFE = re.compile(
    "["
    + "".join(
        re.escape(chr(low)) + "-" + re.escape(chr(high))
        for low, high in (
            (0x00, 0x08),
            (0x0B, 0x1F),
            (0x7F, 0x9F),
            (0x200E, 0x200F),
            (0x202A, 0x202E),
            (0x2066, 0x2069),
        )
    )
    + "]"
)


def parse_version(text: object) -> Version | None:
    """`text` ("v4.13.1" or "4.13.1") as three whole numbers; None for
    anything else (a tag such as "v4.14.0-beta" included)."""
    if not isinstance(text, str):
        return None
    found = _TAG.fullmatch(text.strip())
    if found is None:
        return None
    major, minor, patch = (int(part) for part in found.groups())
    return major, minor, patch


def version_text(version: Version) -> str:
    return ".".join(str(part) for part in version)


def is_newer(theirs: str, ours: str = __version__) -> bool:
    """Whether version `theirs` is newer than `ours` (False when either
    isn't a version)."""
    a, b = parse_version(theirs), parse_version(ours)
    return a is not None and b is not None and a > b


# -- which copies check ------------------------------------------------------


class Copy(Protocol):
    """How this copy of the app treats App updates (Strategy)."""

    @property
    def checks(self) -> bool:
        """Whether it looks for App updates at all."""
        ...

    @property
    def download(self) -> str:
        """The label of the button that gets a newer version; "" for a
        copy updated another way (see `how_to_update`)."""
        ...

    @property
    def how_to_update(self) -> str:
        """One line on how this copy is updated."""
        ...


@dataclass(frozen=True)
class Build:
    """A Build, downloaded from the Releases page: it checks, and offers
    the Download page."""

    checks: bool = True
    download: str = "Download page"
    how_to_update: str = (
        "Download the new version's zip from its Release page and unzip it "
        "beside this one."
    )


@dataclass(frozen=True)
class Checkout:
    """A copy run from a git checkout: it checks, and is updated by pulling
    main."""

    checks: bool = True
    download: str = ""
    how_to_update: str = (
        "This copy runs from the source: pull main (git pull) in its folder "
        "to update it."
    )


@dataclass(frozen=True)
class Quiet:
    """A copy that never checks: a host, a player's copy a host runs, the
    admin word, or any copy while ARMARIUS_UPDATES is off."""

    checks: bool = False
    download: str = ""
    how_to_update: str = ""


def turned_off(env: Mapping[str, str] | None = None) -> bool:
    """Whether ARMARIUS_UPDATES turns every check off."""
    env = os.environ if env is None else env
    return env.get(ENV_VAR, "").strip().lower() == "off"


def this_copy(
    *,
    by_word: bool = False,
    hosted: bool = False,
    frozen: bool = FROZEN,
    env: Mapping[str, str] | None = None,
) -> Copy:
    """How this copy treats App updates: Quiet when it was started with one
    of launch's words (`by_word`), is a player's copy a host runs
    (`hosted`), or ARMARIUS_UPDATES is off; else a Build or a checkout."""
    if by_word or hosted or turned_off(env):
        return Quiet()
    return Build() if frozen else Checkout()


# -- the settings ------------------------------------------------------------


def check_at_start() -> bool:
    """The setting "Check for updates when Armarius starts" (on unless
    turned off)."""
    return settings.load_settings().get(CHECK) is not False


def set_check_at_start(on: bool) -> None:
    settings.update_settings(**{CHECK: bool(on)})


def due(now: float, last: object) -> bool:
    """Whether the check at start-up should run: no check yet, or the last
    one at least INTERVAL ago (or, by a clock set back, in the future)."""
    if not isinstance(last, int | float) or isinstance(last, bool):
        return True
    return not 0 <= now - last < INTERVAL


def skip(version: str) -> None:
    """Skip the App update to `version`: its notice is hidden until a newer
    Release (a security App update can't be skipped)."""
    settings.update_settings(**{SKIPPED: version})


# -- a Release ---------------------------------------------------------------


def plain(text: object, limit: int = MAX_NOTES) -> str:
    """`text` from the network as plain text: line ends made "\\n", every
    control or reordering character taken out, cut at `limit`."""
    if not isinstance(text, str):
        return ""
    text = _UNSAFE.sub("", text.replace("\r\n", "\n").replace("\r", "\n"))
    return text[:limit].strip()


def has_security_marker(notes: str) -> bool:
    """Whether the notes (a version's section of the changelog) have a
    bullet marked as a security fix: one that starts `**Security:**`,
    under any feature's heading."""
    return any(_SECURITY_MARKER.match(line) for line in notes.splitlines())


@dataclass(frozen=True)
class Release:
    """The latest Release, as checked: its version, when it was published
    (YYYY-MM-DD, or ""), its notes as plain text, and its page."""

    version: str
    date: str = ""
    notes: str = ""
    url: str = LATEST_URL

    @property
    def security(self) -> bool:
        return has_security_marker(self.notes)

    def as_setting(self) -> dict[str, str]:
        return {
            "version": self.version,
            "date": self.date,
            "notes": self.notes,
            "url": self.url,
        }


def release_from(data: object) -> Release | None:
    """The Release GitHub's API describes in `data` (its JSON, read), or
    None when its tag isn't a version vX.Y.Z. Every field is checked and
    made plain; an address off the app's Releases page is replaced by the
    Releases page."""
    if not isinstance(data, dict):
        return None
    version = parse_version(data.get("tag_name"))
    if version is None:
        return None
    published = data.get("published_at")
    date = _DATE.match(published) if isinstance(published, str) else None
    url = data.get("html_url")
    if not isinstance(url, str) or not url.startswith(RELEASES_URL + "/"):
        url = LATEST_URL
    return Release(
        version_text(version),
        date.group(1) if date else "",
        plain(data.get("body")),
        url,
    )


def _remembered() -> Release | None:
    """What the last check found, as the settings keep it."""
    kept = settings.load_settings().get(FOUND)
    if not isinstance(kept, dict):
        return None
    return release_from(
        {
            "tag_name": kept.get("version"),
            "published_at": kept.get("date"),
            "body": kept.get("notes"),
            "html_url": kept.get("url"),
        }
    )


# -- the check ---------------------------------------------------------------

#: Ask `url` with `headers`, waiting at most `timeout` seconds: the answer's
#: bytes. URLError or OSError when it can't (tests pass their own).
Fetch = Callable[[str, Mapping[str, str], float], bytes]


def _fetch(url: str, headers: Mapping[str, str], timeout: float) -> bytes:
    """GET `url` over HTTPS, checked against the system's certificates."""
    request = urllib.request.Request(url, headers=dict(headers), method="GET")
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=timeout, context=context) as answer:
        return answer.read(1_000_000)


def headers(version: str = __version__) -> dict[str, str]:
    """What the check sends: the app's version, and the kind of answer it
    reads. Nothing else about the user."""
    return {
        "User-Agent": f"Armarius/{version}",
        "Accept": "application/vnd.github+json",
    }


class CheckFailed(Exception):
    """GitHub couldn't be reached, or didn't answer as expected: the reason."""


def latest(fetch: Fetch | None = None) -> Release | None:
    """The latest Release, asked of GitHub (or of `fetch`, a test's); None
    when its tag isn't a version. CheckFailed with the reason when GitHub
    can't be reached or its answer can't be read."""
    try:
        raw = (fetch or _fetch)(API_URL, headers(), TIMEOUT)
    except urllib.error.HTTPError as exc:
        raise CheckFailed(f"GitHub answered {exc.code} {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise CheckFailed(str(exc.reason)) from exc
    except TimeoutError as exc:
        raise CheckFailed("GitHub didn't answer in time") from exc
    except OSError as exc:
        raise CheckFailed(str(exc) or type(exc).__name__) from exc
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise CheckFailed("GitHub's answer couldn't be read") from exc
    return release_from(data)


@dataclass(frozen=True)
class Result:
    """What a check came to: whether it ran, the Release it found (None
    when none could be read), and why GitHub couldn't be reached ("" when
    it could)."""

    ran: bool
    release: Release | None = None
    problem: str = ""


def check(
    copy: Copy,
    *,
    now_asked: bool = False,
    fetch: Fetch | None = None,
    clock: Callable[[], float] = time.time,
) -> Result:
    """Look for an App update, as `copy` allows. At start-up
    (`now_asked` False) it runs only when the setting is on and the last
    check was at least a day ago; Check now (`now_asked`) runs whenever
    the copy checks at all. A check that finds a Release remembers it and
    when it ran; one that fails remembers nothing, so the next start tries
    again."""
    if not copy.checks:
        return Result(False)
    if not now_asked and (
        not check_at_start()
        or not due(clock(), settings.load_settings().get(LAST_CHECK))
    ):
        return Result(False)
    try:
        release = latest(fetch)
    except CheckFailed as exc:
        return Result(True, problem=str(exc))
    changes: dict[str, object] = {LAST_CHECK: clock()}
    if release is not None:
        changes[FOUND] = release.as_setting()
    settings.update_settings(**changes)
    return Result(True, release)


def outcome_text(result: Result, running: str = __version__) -> str:
    """What Check now says about `result`."""
    if not result.ran:
        return "Checking for updates is turned off on this computer."
    if result.problem:
        return f"Couldn't reach GitHub: {result.problem}."
    if result.release is None:
        return "GitHub's latest Release has no version this app can read."
    if is_newer(result.release.version, running):
        return f"Armarius {result.release.version} is available."
    return f"You have the latest version, Armarius {running}."


# -- the notice --------------------------------------------------------------


@dataclass(frozen=True)
class Notice:
    """An App update notice, or a Version mismatch's, as a front-end shows
    it: the title page's line and the gear's badge (unless `skipped`), and
    Settings' Update row (always, faintly when skipped).

    `headline` is the short line ("Armarius 4.14.0 is available");
    `lines` the first lines of the notes; `notes` all of them, plain text;
    `remote` a line for a new major version (players by Remote seat must
    move too); `download` the button that gets it ("" for none) and
    `how_to_update` the line saying how, for a copy with no button."""

    kind: str
    version: str
    headline: str
    date: str = ""
    lines: tuple[str, ...] = ()
    notes: str = ""
    url: str = LATEST_URL
    remote: str = ""
    skipped: bool = False
    download: str = ""
    how_to_update: str = ""

    @property
    def security(self) -> bool:
        return self.kind == SECURITY

    @property
    def can_skip(self) -> bool:
        return self.kind == UPDATE

    @property
    def shown(self) -> bool:
        """Whether the title page and the gear show it (not skipped)."""
        return not self.skipped


def first_lines(notes: str, count: int = 2) -> tuple[str, ...]:
    """The first `count` lines of `notes` worth showing: no headings, and a
    list item's "- " and bold marks taken off, each cut short."""
    found: list[str] = []
    for raw in notes.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        line = line.removeprefix("- ").removeprefix("* ").replace("**", "")
        if len(line) > MAX_LINE:
            line = line[: MAX_LINE - 1].rstrip() + "…"
        found.append(line)
        if len(found) == count:
            break
    return tuple(found)


def notice_for(
    release: Release | None,
    copy: Copy,
    *,
    running: str = __version__,
    skipped: object = None,
) -> Notice | None:
    """The App update notice for `release` in this copy; None when there is
    nothing to say (no Release, the copy doesn't check, or this version is
    as new or newer)."""
    if release is None or not copy.checks or not is_newer(release.version, running):
        return None
    security = release.security
    headline = f"Armarius {release.version} is available" + (
        ", with security fixes" if security else ""
    )
    theirs, ours = parse_version(release.version), parse_version(running)
    remote = (
        f"Players who join by Remote seat must move to Armarius {release.version} "
        "too: a seat needs the host's major version."
        if theirs and ours and theirs[0] > ours[0]
        else ""
    )
    return Notice(
        SECURITY if security else UPDATE,
        release.version,
        headline,
        release.date,
        first_lines(release.notes),
        release.notes,
        release.url,
        remote,
        skipped=not security and skipped == release.version,
        download=copy.download,
        how_to_update=copy.how_to_update,
    )


def notice(copy: Copy, running: str = __version__) -> Notice | None:
    """The App update notice to show now, from what the last check found;
    None when the check is off or nothing newer was found."""
    if not copy.checks or not check_at_start():
        return None
    kept = settings.load_settings()
    return notice_for(_remembered(), copy, running=running, skipped=kept.get(SKIPPED))


# -- a Version mismatch (Remote seats) ------------------------------------------


@dataclass(frozen=True)
class Mismatch:
    """This app's version and a host's differ. `major` when the first
    number differs (joining is refused); `older` when this app is the
    older one, and so may offer to update."""

    ours: str
    theirs: str
    major: bool
    older: bool

    @property
    def message(self) -> str:
        if self.major and self.older:
            return (
                f"The host runs Armarius {self.theirs} and you run {self.ours}: "
                "update this app to the host's major version to join."
            )
        if self.major:
            return (
                f"Your storyguide's Armarius is older ({self.theirs}). "
                "Ask them to update."
            )
        return (
            f"Your host runs Armarius {self.theirs}, and you run {self.ours}. "
            "You can play, but these versions haven't been tested together, "
            "so some things may behave oddly."
        )

    @property
    def offers_update(self) -> bool:
        return self.older


def mismatch(ours: str, theirs: str) -> Mismatch | None:
    """The Version mismatch between this app (`ours`) and a host
    (`theirs`); None when they match or either isn't a version."""
    a, b = parse_version(ours), parse_version(theirs)
    if a is None or b is None or a == b:
        return None
    return Mismatch(version_text(a), version_text(b), a[0] != b[0], a < b)


def mismatch_notice(found: Mismatch, copy: Copy) -> Notice:
    """A minor Version mismatch, as a notice in the App update notice's
    places (title page line, gear badge, Settings' Update row), with
    Update (the Download page) when this app is the older one."""
    return Notice(
        MISMATCH,
        found.theirs,
        found.message,
        url=LATEST_URL,
        download="Update" if copy.download and found.offers_update else "",
        how_to_update=copy.how_to_update if found.offers_update else "",
    )


def seat_note(seat_version: str, ours: str = __version__) -> str:
    """Beside a Remote seat on the storyguide's Players: its app's version
    when it differs from this one ("" when it matches or isn't known)."""
    if mismatch(ours, seat_version) is None:
        return ""
    return f"{seat_version}, not tested with yours"
