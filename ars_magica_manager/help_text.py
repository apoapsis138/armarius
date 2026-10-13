"""The help text: Markdown files in the help/ folder, read into
topics the Help screen shows.

Each file holds pages. A level-1 or level-2 heading starts a page; a level-3
heading is a topic on the page above it (a section of a sheet, a part of a
dialog). The line right after a heading names the topic's id:

    ## Hermetic Magic tab
    <!-- help: tab-hermetic -->

The ids are the sheet's own: a tab's or section's widget id, a tree node's
page (`character`, `spells`...) or a dialog's `help_id`. A link to another
topic is written `[Lab Totals](help:tab-lab-totals)`. The comment lines don't
show on screen or on GitHub, so the files read as plain Markdown there too.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from . import ROOT, __version__

#: Where the help files live.
HELP_DIR = Path(__file__).parent / "help"

_HEADING = re.compile(r"^(#{1,3})\s+(.+?)\s*$")
_ID = re.compile(r"^<!--\s*help:\s*([\w-]+)\s*-->\s*$")
_LINK = re.compile(r"\]\(help:([\w-]+)\)")


@dataclass(frozen=True)
class Topic:
    """One heading of the help: a page (level 1 or 2) or a topic on one
    (level 3)."""

    id: str
    title: str
    level: int
    #: The id of the page it's shown on: its own for a page.
    page: str
    #: The file it comes from, for messages.
    file: str
    #: Its heading and body as Markdown (without the id line).
    text: str


@dataclass(frozen=True)
class Page:
    """What the Help screen shows at once: a page's heading and body plus
    the topics on it."""

    id: str
    title: str
    file: str
    text: str
    #: The ids of the topics on the page, in order.
    topics: tuple[str, ...]


class HelpError(ValueError):
    """A help file is malformed: a heading without an id, or an id used
    twice."""


@dataclass
class HelpBook:
    """Every topic and page, in file order."""

    topics: dict[str, Topic]
    pages: dict[str, Page]

    def topic(self, topic_id: str) -> Topic | None:
        return self.topics.get(topic_id)

    def page_for(self, topic_id: str) -> Page | None:
        """The page a topic is shown on."""
        topic = self.topics.get(topic_id)
        return self.pages.get(topic.page) if topic is not None else None

    def first(self, topic_ids: list[str]) -> Topic | None:
        """The first of `topic_ids` the help has (most specific first)."""
        for topic_id in topic_ids:
            if topic_id in self.topics:
                return self.topics[topic_id]
        return None

    def search(self, query: str) -> list[Topic]:
        """Topics whose title, then whose text, mentions `query` (any case);
        every topic for a blank query."""
        words = query.casefold().split()
        if not words:
            return list(self.topics.values())

        def has(text: str) -> bool:
            folded = text.casefold()
            return all(word in folded for word in words)

        by_title = [t for t in self.topics.values() if has(t.title)]
        by_text = [t for t in self.topics.values() if t not in by_title and has(t.text)]
        return by_title + by_text

    def links(self) -> dict[str, set[str]]:
        """The topics each page links to (`help:` links)."""
        return {page.id: set(_LINK.findall(page.text)) for page in self.pages.values()}


def display_text(text: str) -> str:
    """`text` as the Help screen shows it: without the id lines."""
    return "\n".join(line for line in text.splitlines() if not _ID.match(line))


def parse(name: str, text: str) -> list[Topic]:
    """The topics in one help file, in order."""
    lines = text.splitlines()
    topics: list[Topic] = []
    page_id: str | None = None
    current: tuple[str, str, int, list[str]] | None = None

    def close() -> None:
        if current is not None:
            topic_id, title, level, body = current
            topics.append(
                Topic(
                    topic_id,
                    title,
                    level,
                    page_id or topic_id,
                    name,
                    "\n".join(body).strip() + "\n",
                )
            )

    index = 0
    while index < len(lines):
        line = lines[index]
        heading = _HEADING.match(line)
        if heading is None:
            if current is None:
                if line.strip():
                    raise HelpError(f"{name}: text before the first heading")
            else:
                current[3].append(line)
            index += 1
            continue
        found = _ID.match(lines[index + 1]) if index + 1 < len(lines) else None
        if found is None:
            raise HelpError(f"{name}: heading {line!r} has no help id after it")
        close()
        level = len(heading.group(1))
        topic_id = found.group(1)
        if level < 3:
            page_id = topic_id
        elif page_id is None:
            raise HelpError(f"{name}: {line!r} comes before any page")
        current = (topic_id, heading.group(2), level, [line])
        index += 2
    close()
    return topics


def load(folder: Path = HELP_DIR) -> HelpBook:
    """Read every help file in `folder` (by name)."""
    topics: dict[str, Topic] = {}
    for path in sorted(folder.glob("*.md")):
        if path.name.casefold() == "readme.md":
            continue
        for topic in parse(path.name, path.read_text(encoding="utf-8")):
            if topic.id in topics:
                raise HelpError(
                    f"{path.name}: help id {topic.id!r} is also in "
                    f"{topics[topic.id].file}"
                )
            topics[topic.id] = topic
    pages: dict[str, Page] = {}
    for topic in topics.values():
        if topic.level < 3:
            on_page = [t for t in topics.values() if t.page == topic.id]
            pages[topic.id] = Page(
                topic.id,
                topic.title,
                topic.file,
                "\n".join(t.text for t in on_page),
                tuple(t.id for t in on_page),
            )
    return HelpBook(topics, pages)


@cache
def book() -> HelpBook:
    """The app's help, read once."""
    return load()


# -- what Help lists and shows (both front-ends) --

#: The About page: the version and NOTICE.md (licences, credits).
ABOUT = "about"
#: What's New: CHANGELOG.md, every version with its release name.
WHATS_NEW = "whats-new"
#: The pages under REFERENCE, after the generated About and What's New.
REFERENCE = ("keys",)
#: How-to guides are the pages whose id starts with this.
GUIDE_PREFIX = "guide-"


def is_guide(topic_id: str) -> bool:
    return topic_id.startswith(GUIDE_PREFIX)


def whats_new_text() -> str:
    """The What's New page: CHANGELOG.md under a title of its own."""
    try:
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    except OSError:
        return "# What's New\n\nCHANGELOG.md is missing: see the repository."
    _, _, body = changelog.partition("\n")  # its own "# Changelog" title
    return f"# What's New\n{body}"


def about_text() -> str:
    """The About page: the version, then NOTICE.md."""
    try:
        notice = (ROOT / "NOTICE.md").read_text(encoding="utf-8")
    except OSError:
        notice = "NOTICE.md is missing: see the repository for licences."
    return f"# Armarius v{__version__}\n\nA saga manager for Ars Magica.\n\n{notice}"


def page_text(help_book: HelpBook, topic_id: str) -> tuple[str, str] | None:
    """The page `topic_id` is on, as Help shows it: its id and Markdown
    (About and What's New made here); None for a topic the help hasn't."""
    if topic_id == ABOUT:
        return ABOUT, about_text()
    if topic_id == WHATS_NEW:
        return WHATS_NEW, whats_new_text()
    page = help_book.page_for(topic_id)
    if page is None:
        return None
    return page.id, display_text(page.text)


@dataclass(frozen=True)
class Entry:
    """One topic as Help lists it: under a group (`group`: "here",
    "guide", "ref", "all" or "found"), indented one step for a page under
    another."""

    group: str
    id: str
    title: str
    indent: int = 0


def contents(
    help_book: HelpBook, here: list[str], query: str = ""
) -> list[tuple[str, list[Entry]]]:
    """Help's topic list as (heading, entries) groups: with a `query`,
    the topics found; otherwise THIS SCREEN (`here`, the topics for where
    Help was opened, most specific first), HOW-TO GUIDES, REFERENCE and
    ALL PAGES."""
    if query.strip():
        found = help_book.search(query)
        return [
            (f"FOUND ({len(found)})", [Entry("found", t.id, t.title) for t in found])
        ]
    groups: list[tuple[str, list[Entry]]] = []
    shown = [t for t in dict.fromkeys(here) if t in help_book.topics]
    if shown:
        groups.append(
            (
                "THIS SCREEN",
                [Entry("here", t, help_book.topics[t].title) for t in shown],
            )
        )
    guides = [p for p in help_book.pages.values() if is_guide(p.id)]
    if guides:
        groups.append(
            ("HOW-TO GUIDES", [Entry("guide", p.id, p.title) for p in guides])
        )
    groups.append(
        (
            "REFERENCE",
            [
                Entry("ref", ABOUT, "About this App"),
                Entry("ref", WHATS_NEW, "What's New"),
                *(
                    Entry("ref", t, help_book.topics[t].title)
                    for t in REFERENCE
                    if t in help_book.topics
                ),
            ],
        )
    )
    groups.append(
        (
            "ALL PAGES",
            [
                Entry(
                    "all",
                    p.id,
                    p.title,
                    1 if help_book.topics[p.id].level == 2 else 0,
                )
                for p in help_book.pages.values()
                if p.id not in REFERENCE and not is_guide(p.id)
            ],
        )
    )
    return groups
