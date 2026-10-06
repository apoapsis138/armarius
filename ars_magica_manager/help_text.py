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
