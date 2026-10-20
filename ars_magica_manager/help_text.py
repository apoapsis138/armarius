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

The terminal and the desktop are drawn differently, so some help is for one
of them only. A topic for one front-end names it after its id, and a page's
topics go with it:

    # The workspace
    <!-- help: workspace; gui -->

The same id may then be used once for each front-end, so the page a screen
opens Help on is the one that describes it. Lines for one front-end inside
a topic that is for both sit between markers on lines of their own:

    <!-- tui -->
    `e` edits the chosen row.
    <!-- /tui -->

Each front-end reads its own book (`book(TUI)`, `book(GUI)`): what is for
the other is left out, so it is neither listed, shown nor found.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from . import ROOT, __version__, changelog

#: Where the help files live.
HELP_DIR = Path(__file__).parent / "help"

_HEADING = re.compile(r"^(#{1,3})\s+(.+?)\s*$")
_ID = re.compile(r"^<!--\s*help:\s*([\w-]+)\s*(?:;\s*(\w+)\s*)?-->\s*$")
_ONLY = re.compile(r"^<!--\s*(/?)(\w+)\s*-->\s*$")
_ANY_ONLY = re.compile(r"<!--\s*/?(?:tui|gui)\s*-->")

#: The front-ends, as the help files name them: the terminal (Textual)
#: and the desktop (PySide6).
TUI = "tui"
GUI = "gui"
FRONT_ENDS = (TUI, GUI)
_LINK = re.compile(r"\]\(help:([\w-]+)\)")
#: The topic every tradition chapter shares (see shared_topic).
TRADITION_CHAPTER = "tradition-chapter"


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
    #: The front-end it is for (TUI or GUI); None for both.
    front_end: str | None = None


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


#: Sheet ids made per catalog entry, which share one topic: each
#: tradition's chapter (traditions.TAB_PREFIX, SECTION_PREFIX).
SHARED_TOPICS: dict[str, str] = {
    "tab-trad-": TRADITION_CHAPTER,
    "section-trad-": TRADITION_CHAPTER,
}


def shared_topic(topic_id: str) -> str:
    """The topic a sheet id is explained under: its own, or the one it
    shares with others of its kind."""
    for prefix, shared in SHARED_TOPICS.items():
        if topic_id.startswith(prefix):
            return shared
    return topic_id


@dataclass
class HelpBook:
    """Every topic and page, in file order."""

    topics: dict[str, Topic]
    pages: dict[str, Page]

    def topic(self, topic_id: str) -> Topic | None:
        return self.topics.get(shared_topic(topic_id))

    def page_for(self, topic_id: str) -> Page | None:
        """The page a topic is shown on."""
        topic = self.topics.get(topic_id)
        return self.pages.get(topic.page) if topic is not None else None

    def first(self, topic_ids: list[str]) -> Topic | None:
        """The first of `topic_ids` the help has (most specific first)."""
        for topic_id in map(shared_topic, topic_ids):
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


def _for(name: str, front_end: str | None) -> str | None:
    """`front_end`, checked: None (for both) or one of FRONT_ENDS."""
    if front_end is not None and front_end not in FRONT_ENDS:
        raise HelpError(
            f"{name}: {front_end!r} is not a front-end ({', '.join(FRONT_ENDS)})"
        )
    return front_end


def _lines_for(name: str, text: str, front_end: str) -> list[str]:
    """`text`'s lines with those for another front-end left out (and the
    markers around them)."""
    kept: list[str] = []
    inside: str | None = None
    for line in text.splitlines():
        marker = _ONLY.match(line)
        if marker is not None and marker.group(2) in FRONT_ENDS:
            closing, which = marker.group(1) == "/", marker.group(2)
            if closing != (inside is not None) or (closing and which != inside):
                raise HelpError(f"{name}: {line.strip()!r} doesn't match")
            inside = None if closing else which
            continue
        if _ANY_ONLY.search(line):
            raise HelpError(
                f"{name}: {line.strip()[:40]!r}: a marker goes on a line of its own"
            )
        if inside is not None and _HEADING.match(line):
            raise HelpError(
                f"{name}: heading {line!r} inside <!-- {inside} -->: give the "
                "topic its front-end instead"
            )
        if inside is None or inside == front_end:
            kept.append(line)
    if inside is not None:
        raise HelpError(f"{name}: <!-- {inside} --> is never closed")
    return kept


def parse(name: str, text: str, front_end: str) -> list[Topic]:
    """The topics in one help file for `front_end`, in order."""
    _for(name, front_end)
    lines = _lines_for(name, text, front_end)
    topics: list[Topic] = []
    page_id: str | None = None
    page_for: str | None = None
    current: tuple[str, str, int, str | None, list[str]] | None = None

    def close() -> None:
        if current is not None:
            topic_id, title, level, only, body = current
            if only in (None, front_end):
                topics.append(
                    Topic(
                        topic_id,
                        title,
                        level,
                        page_id or topic_id,
                        name,
                        "\n".join(body).strip() + "\n",
                        only,
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
                current[4].append(line)
            index += 1
            continue
        found = _ID.match(lines[index + 1]) if index + 1 < len(lines) else None
        if found is None:
            raise HelpError(f"{name}: heading {line!r} has no help id after it")
        close()
        level = len(heading.group(1))
        topic_id = found.group(1)
        only = _for(name, found.group(2))
        if level < 3:
            page_id, page_for = topic_id, only
        elif page_id is None:
            raise HelpError(f"{name}: {line!r} comes before any page")
        elif page_for is not None:
            if only not in (None, page_for):
                raise HelpError(
                    f"{name}: {line!r} is for {only}, its page for {page_for}"
                )
            only = page_for
        current = (topic_id, heading.group(2), level, only, [line])
        index += 2
    close()
    return topics


def load(front_end: str, folder: Path = HELP_DIR) -> HelpBook:
    """Read every help file in `folder` (by name), as `front_end` shows
    it."""
    topics: dict[str, Topic] = {}
    for path in sorted(folder.glob("*.md")):
        if path.name.casefold() == "readme.md":
            continue
        for topic in parse(path.name, path.read_text(encoding="utf-8"), front_end):
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
def book(front_end: str) -> HelpBook:
    """The app's help as `front_end` shows it, read once."""
    return load(front_end)


# -- what Help lists and shows (both front-ends) --

#: The About page: the version and NOTICE.md (licences, credits).
ABOUT = "about"
#: What's New: CHANGELOG.md by feature and edition, then every version.
WHATS_NEW = "whats-new"
#: The pages under REFERENCE, after the generated About and What's New.
REFERENCE = ("keys",)
#: How-to guides are the pages whose id starts with this.
GUIDE_PREFIX = "guide-"


def is_guide(topic_id: str) -> bool:
    return topic_id.startswith(GUIDE_PREFIX)


def whats_new_text() -> str:
    """The What's New page: CHANGELOG.md's latest editions, each feature
    with its editions, and the Chronicle of every version."""
    try:
        text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    except OSError:
        return "# What's New\n\nCHANGELOG.md is missing: see the repository."
    return changelog.whats_new(text)


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
