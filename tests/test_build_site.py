"""The user-docs website's exporter (tools/build_site.py): the help's links
rewritten for the site, and only the desktop's help on it."""

from __future__ import annotations

import posixpath
import re
from pathlib import Path

import build_site

from ars_magica_manager import help_text
from ars_magica_manager.help_text import GUI, TUI

HELP = """\
# Character sheet
<!-- help: character -->

The sheet. See [Lab Totals](help:tab-lab-totals) and [its section](help:section-x).

<!-- tui -->
Press `e` to edit the chosen row.
<!-- /tui -->
<!-- gui -->
Click **Edit** on the chosen row.
<!-- /gui -->

### A section
<!-- help: section-x -->

Back to [the sheet](help:character), to [a terminal page](help:term-only), to
[a tradition](help:tab-trad-galdor) and [About](help:about).
Open it here. [Go there](go:section-x)
And [the tab](go:tab-lab-totals) itself.

## Lab Totals tab
<!-- help: tab-lab-totals -->

The totals.

# Tradition
<!-- help: tradition-chapter -->

Every tradition's chapter.

# Terminal only
<!-- help: term-only; tui -->

Only in the terminal.
"""


def _book(tmp_path: Path, front_end: str = GUI) -> help_text.HelpBook:
    (tmp_path / "sheet.md").write_text(HELP, encoding="utf-8")
    return help_text.load(front_end, tmp_path)


def _pages(book: help_text.HelpBook) -> dict[str, str]:
    return {page.path: page.markdown for page in build_site.export(book)}


def test_pages_go_under_their_sheet(tmp_path: Path) -> None:
    paths = build_site.page_paths(_book(tmp_path))
    assert paths == {
        "character": "help/character/index.md",
        "tab-lab-totals": "help/character/tab-lab-totals.md",
        "tradition-chapter": "help/tradition-chapter/index.md",
    }


def test_help_links_point_at_the_page_and_anchor(tmp_path: Path) -> None:
    sheet = _pages(_book(tmp_path))["help/character/index.md"]
    # A topic on another page: its page, from beside it.
    assert "[Lab Totals](tab-lab-totals.md)" in sheet
    # A topic on this page: its anchor.
    assert "[its section](index.md#section-x)" in sheet
    # The page itself: no anchor.
    assert "[the sheet](index.md)" in sheet
    # A sheet id that shares its topic links to the shared one.
    assert "[a tradition](../tradition-chapter/index.md)" in sheet
    # About is a page of the site's own.
    assert "[About](../../about.md)" in sheet


def test_topic_headings_carry_their_ids(tmp_path: Path) -> None:
    pages = _pages(_book(tmp_path))
    sheet = pages["help/character/index.md"]
    assert sheet.startswith("# Character sheet {#character}\n")
    assert "\n## A section {#section-x}\n" in sheet
    # A page under a sheet is a page of its own, its title the heading.
    assert pages["help/character/tab-lab-totals.md"].startswith(
        "# Lab Totals tab {#tab-lab-totals}\n"
    )


def test_go_links_become_plain_text(tmp_path: Path) -> None:
    sheet = _pages(_book(tmp_path))["help/character/index.md"]
    assert "go:" not in sheet
    # The app's Go there button is left out, its space with it.
    assert "Open it here.\n" in sheet
    assert "Go there" not in sheet
    # Any other label stays as words.
    assert "And the tab itself." in sheet


def test_only_the_desktops_help_is_on_the_site(tmp_path: Path) -> None:
    pages = _pages(_book(tmp_path))
    sheet = pages["help/character/index.md"]
    assert "Click **Edit** on the chosen row." in sheet
    assert "Press `e`" not in sheet
    assert "<!--" not in sheet
    # A page for the terminal only gets no page, and a link to it is words.
    assert not any("term-only" in path for path in pages)
    assert "to a terminal page, to" in sheet


def test_the_terminal_book_would_keep_its_own(tmp_path: Path) -> None:
    """The filtering is the book's: read for the terminal, the same
    exporter keeps the terminal's text, so the site's choice is GUI."""
    sheet = _pages(_book(tmp_path, TUI))["help/character/index.md"]
    assert "Press `e`" in sheet
    assert "Click **Edit**" not in sheet


def test_every_link_in_the_real_help_lands_on_a_page() -> None:
    """The app's own help, exported: no `help:` or `go:` link is left, and
    every link to another page names a page the site has."""
    pages = _pages(help_text.book(GUI))
    hand_written = {"index.md", "install.md", "faq.md"}
    known = set(pages) | hand_written
    unknown: list[str] = []
    for path, markdown in pages.items():
        assert "](help:" not in markdown and "](go:" not in markdown, path
        for target in re.findall(r"\]\(([^)\s#]+\.md)(?:#[\w-]+)?\)", markdown):
            landed = posixpath.normpath(posixpath.join(posixpath.dirname(path), target))
            if landed not in known:
                unknown.append(f"{path} -> {target}")
    assert not unknown, "\n".join(unknown)


def test_the_menu_lists_every_page() -> None:
    book = help_text.book(GUI)
    nav = build_site.nav_yaml(book)
    paths = build_site.page_paths(book)
    missing = [path for path in paths.values() if f" {path}" not in nav]
    assert not missing, missing
    # Getting started leads the guides.
    guides = nav.split("  - How-to guides:\n", 1)[1]
    assert guides.splitlines()[0].endswith(paths["guide-getting-started"])
