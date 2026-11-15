"""CHANGELOG.md read as features, editions and versions, and the What's
New page made from them.

The changelog is written as it always was, one version at a time, newest
first; each version's entries sit under a "### Feature" heading for the
feature they belong to. Its Features table names the features, its
Editions table the finished rounds of work on each ("Peregrinatio V",
finished in 2.102.0), its Major versions table the name of each major
version (the title page shows it), and its Milestones table the versions
that marked a moment of their own. An edition holds its feature's work up to the version it was
finished in; work after a feature's last edition is that feature's next
edition, in progress, while later bug-fix versions alone count as smaller
changes to the last one.

Work done since the last release sits above the newest version under an
"## Unreleased" heading, held to the same "### Feature" rule; a release
renames it to the version's heading. What's New shows it first, as
Unreleased (in development), and leaves it out of the editions and the
Chronicle, which hold only released versions.

The tree is a Composite (a feature holds editions, an edition holds the
parts of versions), and the page's three parts (Latest, the features, the
Chronicle) are three plain functions walking it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date

#: A version's heading: "## 2.102.0 — 2026-10-19".
_VERSION = re.compile(r"^## (\d+\.\d+\.\d+) — (\d{4}-\d{2}-\d{2})\s*$")
#: The heading of the work done since the last release, above the newest
#: version; a release renames it to the version's heading.
UNRELEASED = "Unreleased"
UNRELEASED_HEADING = f"## {UNRELEASED}"
#: An edition's name: the feature, then its number in Roman numerals.
_EDITION = re.compile(r"^(.+) ([IVXLC]+)$")
_ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}

#: How many editions the Latest part shows.
LATEST = 3
#: How many of a version's headlines its Chronicle line names.
HEADLINES = 3


def version_key(number: str) -> tuple[int, ...]:
    return tuple(int(part) for part in number.split("."))


def roman(numeral: str) -> int:
    total = 0
    for this, after in zip(numeral, numeral[1:] + " "):
        value = _ROMAN[this]
        total += -value if after != " " and _ROMAN[after] > value else value
    return total


def numeral(number: int) -> str:
    out = ""
    for value, letters in (
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ):  # fmt: skip
        while number >= value:
            out += letters
            number -= value
    return out


def long_date(day: str) -> str:
    """ "2026-10-19" as "19 October 2026"."""
    d = date.fromisoformat(day)
    return f"{d.day} {d:%B %Y}"


@dataclass(frozen=True)
class Part:
    """What one version changed in one feature: its Markdown entries."""

    version: str
    date: str
    feature: str
    text: str

    @property
    def is_fix(self) -> bool:
        """A bug-fix (PATCH) version's part."""
        return version_key(self.version)[2] != 0

    def entries(self) -> list[list[str]]:
        """Its entries: each top-level bullet's lines (a paragraph before
        the first bullet goes with it)."""
        blocks: list[list[str]] = [[]]
        for line in self.text.splitlines():
            if line.startswith("- ") and any(b.startswith("- ") for b in blocks[-1]):
                blocks.append([])
            blocks[-1].append(line)
        return [b for b in blocks if any(line.strip() for line in b)]

    def headlines(self) -> list[str]:
        """Each entry's lead: its bold opening, else its first sentence."""
        return [
            headline(" ".join(line for line in block if line.strip()))
            for block in self.entries()
        ]

    def tagged(self) -> str:
        """Its entries with the version after each one's own text."""
        out: list[str] = []
        for block in self.entries():
            lines = list(block)
            while not lines[-1].strip():
                lines.pop()
            nested = next(
                (n for n, line in enumerate(lines) if line.startswith("  - ")),
                len(lines),
            )
            own = max(n for n in range(nested) if lines[n].strip())
            lines[own] += f" ({self.version})"
            out += lines
        return "\n".join(out)


def headline(entry: str) -> str:
    text = " ".join(entry.removeprefix("- ").split())
    bold = re.match(r"\*\*(.+?)\*\*", text)
    if bold:
        lead = bold.group(1)
    else:
        text = text.replace("**", "").replace("`", "")
        lead, *rest = re.split(r"(?<=[^.][.:])\s", text, maxsplit=1)
        if rest and lead.endswith(":") and len(lead.split()) <= 3:
            # "Behind the scenes: the forms...", "Fixed: ...": what follows.
            lead = re.split(r"(?<=[^.][.:])\s", rest[0], maxsplit=1)[0]
            lead = lead[:1].upper() + lead[1:]
    lead = lead.rstrip(".:")
    if len(lead) > 70:
        lead = lead[:70].rsplit(" ", 1)[0].rstrip(",;:") + "…"
    return lead


@dataclass(frozen=True)
class Version:
    number: str
    date: str
    parts: tuple[Part, ...]


@dataclass(frozen=True)
class Feature:
    name: str
    about: str


@dataclass(frozen=True)
class Major:
    """A major version's name: 2 is "2.x"."""

    number: int
    name: str
    marked: str


@dataclass(frozen=True)
class Milestone:
    name: str
    version: str
    marked: str


@dataclass
class Edition:
    """A round of work on one feature: finished in a version, or (when
    `finished_in` is "") still in progress."""

    feature: str
    number: int
    title: str = ""
    finished_in: str = ""
    brought: str = ""
    parts: list[Part] = field(default_factory=list)

    @property
    def name(self) -> str:
        return f"{self.feature} {numeral(self.number)}"

    @property
    def heading(self) -> str:
        if not self.finished_in:
            return f"{self.name}, in progress"
        return f"{self.name}: {self.title}" if self.title else self.name

    @property
    def work(self) -> list[Part]:
        """Its parts that are not later fixes (its own versions)."""
        own = [
            p
            for p in self.parts
            if not self.finished_in
            or version_key(p.version) <= version_key(self.finished_in)
        ]
        return own or self.parts

    @property
    def first(self) -> Part:
        return min(self.work, key=lambda p: version_key(p.version))

    @property
    def last(self) -> Part:
        return max(self.work, key=lambda p: version_key(p.version))

    def span(self) -> str:
        """ "17 to 18 October 2026, versions 2.97.0 to 2.99.0"."""
        first, last = self.first, self.last
        days = long_date(first.date)
        if first.date != last.date:
            a, b = date.fromisoformat(first.date), date.fromisoformat(last.date)
            if (a.year, a.month) == (b.year, b.month):
                days = f"{a.day} to {long_date(last.date)}"
            else:
                days = f"{long_date(first.date)} to {long_date(last.date)}"
        if first.version == last.version:
            return f"{days}, version {first.version}"
        return f"{days}, versions {first.version} to {last.version}"


@dataclass
class Changelog:
    intro: str
    #: The preamble's other paragraphs: what the names and numbers mean.
    about: str
    features: list[Feature]
    editions: list[Edition]
    milestones: list[Milestone]
    versions: list[Version]
    majors: list[Major] = field(default_factory=list)
    #: What is done but not yet in a release, by feature: kept out of the
    #: editions and the Chronicle, which hold only released versions.
    unreleased: list[Part] = field(default_factory=list)

    def feature_editions(self, feature: str) -> list[Edition]:
        return [e for e in self.editions if e.feature == feature]

    def edition_of(self, part: Part) -> Edition:
        for edition in self.editions:
            if part in edition.parts:
                return edition
        raise LookupError(part)

    def major(self, number: int) -> Major | None:
        return next((m for m in self.majors if m.number == number), None)


class ChangelogError(ValueError):
    pass


def _table(section: str) -> list[list[str]]:
    rows = []
    for line in section.splitlines():
        if line.startswith("|") and not re.match(r"^\|\s*-", line):
            rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    return rows[1:]  # without the header row


def _sections(text: str) -> dict[str, str]:
    """The preamble's "## Title" sections, by title."""
    out: dict[str, str] = {}
    for chunk in re.split(r"^## ", text, flags=re.MULTILINE)[1:]:
        title, _, body = chunk.partition("\n")
        out[title.strip()] = body
    return out


def _parts(number: str, day: str, lines: list[str], known: set[str]) -> list[Part]:
    """One section's entries, by the "### Feature" heading each sits under."""
    parts: list[Part] = []
    feature, body = "", []
    for line in [*lines, "### "]:
        if line.startswith("### "):
            if feature:
                parts.append(Part(number, day, feature, "\n".join(body).strip()))
            elif "\n".join(body).strip():
                raise ChangelogError(f"{number} has entries under no feature")
            feature, body = line[4:].strip(), []
            if feature and feature not in known:
                raise ChangelogError(f"{number}: unknown feature {feature!r}")
        else:
            body.append(line)
    return parts


def parse(text: str) -> Changelog:
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if _VERSION.match(line)]
    if not starts:
        raise ChangelogError("no versions")
    pending = [i for i, line in enumerate(lines) if line.strip() == UNRELEASED_HEADING]
    if len(pending) > 1:
        raise ChangelogError("more than one Unreleased section")
    if pending and pending[0] > starts[0]:
        raise ChangelogError("Unreleased must come before the newest version")
    if pending and any(
        line.startswith("## ") for line in lines[pending[0] + 1 : starts[0]]
    ):
        raise ChangelogError("Unreleased must come just before the newest version")
    top = pending[0] if pending else starts[0]
    preamble = "\n".join(lines[1:top])  # after "# Changelog"
    sections = _sections(preamble)
    intro, _, about = preamble.split("\n## ", 1)[0].strip().partition("\n\n")
    features = [Feature(name, about) for name, about in _table(sections["Features"])]
    known = {f.name for f in features}
    unreleased = (
        _parts(UNRELEASED, "", lines[pending[0] + 1 : starts[0]], known)
        if pending
        else []
    )

    versions: list[Version] = []
    for n, start in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        match = _VERSION.match(lines[start])
        assert match
        number, day = match.groups()
        parts = _parts(number, day, lines[start + 1 : end], known)
        if not parts:
            raise ChangelogError(f"{number} names no feature")
        versions.append(Version(number, day, tuple(parts)))

    editions: list[Edition] = []
    for name, title, finished_in, brought in _table(sections["Editions"]):
        match = _EDITION.match(name)
        if not match or match.group(1) not in known:
            raise ChangelogError(f"edition {name!r} names no feature")
        editions.append(
            Edition(match.group(1), roman(match.group(2)), title, finished_in, brought)
        )
    milestones = [Milestone(*row) for row in _table(sections["Milestones"])]
    majors = [
        Major(int(number), name, marked)
        for number, name, marked in _table(sections.get("Major versions", ""))
    ]
    log = Changelog(
        intro, about.strip(), features, editions, milestones, versions, majors,
        unreleased,
    )  # fmt: skip
    _assign(log)
    return log


def _assign(log: Changelog) -> None:
    """Give each version's parts to their editions, oldest first, and add
    each feature's edition in progress where it has one."""
    parts = sorted(
        (p for v in log.versions for p in v.parts), key=lambda p: version_key(p.version)
    )
    for feature in log.features:
        finished = sorted(
            log.feature_editions(feature.name), key=lambda e: version_key(e.finished_in)
        )
        mine = [p for p in parts if p.feature == feature.name]
        after: list[Part] = []
        for part in mine:
            home = next(
                (
                    e
                    for e in finished
                    if version_key(part.version) <= version_key(e.finished_in)
                ),
                None,
            )
            if home is None:
                after.append(part)
            else:
                home.parts.append(part)
        if not after:
            continue
        if finished and all(p.is_fix for p in after):
            finished[-1].parts.extend(after)
        else:
            number = finished[-1].number + 1 if finished else 1
            log.editions.append(Edition(feature.name, number, parts=after))
    log.editions.sort(key=lambda e: (e.feature, e.number))


# -- the page --


def _sentence(text: str) -> str:
    return text if text.endswith((".", "!", "?")) else f"{text}."


def _recency(log: Changelog, feature: str, parts: list[Part]) -> tuple:
    """How recent `parts` (one feature's) are: the newest version, then
    the feature's place among that version's headings."""
    newest = max(parts, key=lambda p: version_key(p.version)).version
    version = next(v for v in log.versions if v.number == newest)
    order = [p.feature for p in version.parts]
    return (version_key(newest), -order.index(feature))


def latest_text(log: Changelog) -> str:
    editions = sorted(
        (e for e in log.editions if e.parts),
        key=lambda e: _recency(log, e.feature, e.work),
        reverse=True,
    )
    out = ["## Latest", ""]
    for edition in editions[:LATEST]:
        if edition.finished_in:
            when = long_date(edition.last.date)
            out.append(f"- **{edition.heading}**, {when}. {_sentence(edition.brought)}")
        else:
            since = long_date(edition.first.date)
            # Newest first, as many as a version's Chronicle line names.
            news = [h for p in reversed(edition.work) for h in p.headlines()]
            text = "; ".join(news[:HEADLINES])
            if len(news) > HEADLINES:
                text += f"; and {len(news) - HEADLINES} more"
            out.append(
                f"- **{edition.name}**, in progress since {since}. {_sentence(text)}"
            )
    return "\n".join(out) + "\n"


def feature_text(log: Changelog, feature: Feature) -> str:
    """A feature with its editions, oldest first: its newest edition with
    every entry in full, the earlier ones by their entries' headlines."""
    out = [f"## {feature.name}", "", _sentence(feature.about), ""]
    editions = [
        e
        for e in sorted(log.feature_editions(feature.name), key=lambda e: e.number)
        if e.parts
    ]
    for edition in editions:
        out += [f"### {edition.heading}", ""]
        about = f"{_sentence(edition.brought)} " if edition.brought else ""
        out += [f"{about}{_sentence(edition.span())}", ""]
        if edition is editions[-1]:
            out += [part.tagged() for part in edition.parts]
        else:
            out += [
                f"- {h} ({part.version})"
                for part in edition.parts
                for h in part.headlines()
            ]
        out.append("")
    return "\n".join(out)


def features_text(log: Changelog) -> str:
    def recency(feature: Feature) -> tuple:
        parts = [p for e in log.feature_editions(feature.name) for p in e.parts]
        own = [p for p in parts if not p.is_fix] or parts
        return _recency(log, feature.name, own)

    shown = [f for f in log.features if log.feature_editions(f.name)]
    return "\n".join(
        feature_text(log, f) for f in sorted(shown, key=recency, reverse=True)
    )


def chronicle_text(log: Changelog) -> str:
    marks = {m.version: m for m in log.milestones}
    out = ["## Chronicle", "", "Every version, newest first, by the day it came."]
    day, major = "", -1
    for version in log.versions:
        number = version_key(version.number)[0]
        if number != major:
            major, named = number, log.major(number)
            title = f"{named.name} ({number}.x)" if named else f"Version {number}.x"
            out += ["", f"### {title}", ""]
            if named:
                out += [_sentence(named.marked[:1].upper() + named.marked[1:])]
            day = ""
        if version.date != day:
            day = version.date
            out += ["", f"#### {long_date(day)}", ""]
        names = []
        for part in version.parts:
            name = log.edition_of(part).name
            if name not in names:
                names.append(name)
        headlines = [h for p in version.parts for h in p.headlines()]
        what = "; ".join(headlines[:HEADLINES])
        if len(headlines) > HEADLINES:
            what += f"; and {len(headlines) - HEADLINES} more"
        mark = marks.get(version.number)
        if mark:
            what = f"*{mark.name}: {mark.marked}.* {what}"
        out.append(f"- **{version.number}** · {', '.join(names)} · {what}")
    return "\n".join(out) + "\n"


def unreleased_text(log: Changelog) -> str:
    """The work not yet in a release, by feature ("" when there is none)."""
    if not log.unreleased:
        return ""
    out = [
        f"## {UNRELEASED} (in development)",
        "",
        "Done since the last release, and coming in the next one.",
    ]
    for part in log.unreleased:
        out += ["", f"### {part.feature}", "", part.text]
    return "\n".join(out) + "\n"


def whats_new(text: str) -> str:
    """The What's New page for the changelog `text`."""
    log = parse(text)
    return "\n".join(
        [
            "# What's New",
            "",
            log.intro,
            "",
            unreleased_text(log),
            latest_text(log),
            features_text(log),
            chronicle_text(log),
            f"## The names and numbers\n\n{log.about}\n" if log.about else "",
        ]
    )


def release_name(text: str, version: str) -> str:
    """The name of `version`'s major version ("" if it has none)."""
    try:
        named = parse(text).major(version_key(version)[0])
    except ChangelogError, KeyError, ValueError:
        return ""
    return named.name if named else ""
