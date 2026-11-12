"""Build the user-docs website (GitHub Pages) from the desktop's help.

    uv run --group site python tools/build_site.py           # build/site/
    uv run --group site python tools/build_site.py --serve   # preview it
    uv run python tools/build_site.py --no-build             # sources only

The site is the hand-written pages in `site/` (home, Install, FAQ) plus
one page for each page of the desktop's help, read through
`help_text.book(GUI)`, so text for the terminal only is already left out.
This module is an Adapter over the HelpBook, beside the terminal's and the
desktop's Help screens: the book stays as it is, and each reader turns it
into what it shows. Here a `help:` link becomes a link to the page (and
anchor) that topic is on, a `go:` link (which only means something inside
the app) becomes plain text (the app's own "Go there" is left out), and
every topic heading gets its id as an
anchor, so a link into the help reads the same on the site as in the app.

It writes the MkDocs sources into build/site-src/ (with a generated nav)
and, unless --no-build, runs MkDocs (the `site` dependency group) to make
build/site/.
"""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ars_magica_manager import ROOT, help_text
from ars_magica_manager.help_text import GUI, HelpBook, Page

#: The hand-written pages, styles and the base MkDocs settings.
SITE_DIR = ROOT / "site"
#: Where the MkDocs sources are gathered, and where the site is built.
BUILD_SRC = ROOT / "build" / "site-src"
BUILD_OUT = ROOT / "build" / "site"
#: The repository, for links to files the site doesn't carry.
REPO = "https://github.com/apoapsis138/armarius"
#: The fonts the site is set in (the app's own, under the SIL OFL).
FONTS = (
    "EBGaramond-wght.ttf",
    "EBGaramond-Italic-wght.ttf",
    "EBGaramond-OFL.txt",
    "Cinzel-wght.ttf",
    "Cinzel-OFL.txt",
    "UncialAntiqua-Regular.ttf",
    "UncialAntiqua-OFL.txt",
)
FONT_DIR = ROOT / "ars_magica_manager" / "style" / "assets" / "fonts"
SCREENSHOTS = ROOT / "docs" / "screenshots"

#: Each help file's part of the app, as the site's menu names it, in the
#: menu's order. A file not named here is listed after them by its name.
FILE_TITLES = {
    "workspace.md": "The workspace",
    "character.md": "Characters",
    "covenant.md": "Covenants",
    "laboratory.md": "Laboratories",
    "familiar.md": "Familiars",
    "processes.md": "Seasons and processes",
    "region.md": "The Region",
    "region-atlas.md": "The Atlas",
    "tribunal.md": "Tribunals",
    "conflicts.md": "Fights and sieges",
    "bestiary.md": "The Bestiary",
    "packs.md": "Sourcebook packs",
}
#: The guides the menu lists first; the rest follow in the help's order.
FIRST_GUIDES = ("guide-getting-started",)
#: Files whose pages the menu lists elsewhere (the guides, Keys).
UNLISTED_FILES = ("reference.md",)
#: The generated reference pages, by help id.
ABOUT_PATH = "about.md"
WHATS_NEW_PATH = "whats-new.md"

_HELP_LINK = re.compile(r"\[([^\]]*)\]\(help:([\w-]+)\)")
_GO_LINK = re.compile(r"\[([^\]]*)\]\(go:[\w-]+\)")
_GO_THERE = re.compile(r" ?\[Go there\]\(go:[\w-]+\)")
_HEADING = re.compile(r"^(#{1,3})\s+(.+?)\s*$")
#: A link to a file in the repository (NOTICE.md's LICENSE, say).
_REPO_LINK = re.compile(r"\]\((?!https?:|mailto:|#|help:|go:)([^)\s]+)\)")


@dataclass(frozen=True)
class SitePage:
    """One page of the site: where it goes under docs/, and its Markdown."""

    path: str
    title: str
    markdown: str


def parent_of(book: HelpBook, page: Page) -> str | None:
    """The level-1 page a level-2 page sits under (its sheet), if any."""
    if book.topics[page.id].level == 1:
        return None
    sheet = book.sheet_of(page.id)
    return sheet.id if sheet is not None else None


def page_paths(book: HelpBook) -> dict[str, str]:
    """Each help page's file under docs/: help/<page>/index.md, and a
    page under a sheet beside it, help/<sheet>/<page>.md."""
    paths: dict[str, str] = {}
    for page in book.pages.values():
        parent = parent_of(book, page)
        paths[page.id] = (
            f"help/{parent}/{page.id}.md" if parent else f"help/{page.id}/index.md"
        )
    return paths


def link_target(
    book: HelpBook, paths: dict[str, str], topic_id: str, from_path: str
) -> str | None:
    """Where a `help:` link to `topic_id` points from the page at
    `from_path`: a relative path, with the topic's anchor unless it is the
    page itself; None for a topic this book hasn't (one for the terminal
    only)."""
    if topic_id == help_text.ABOUT:
        target, anchor = ABOUT_PATH, ""
    elif topic_id == help_text.WHATS_NEW:
        target, anchor = WHATS_NEW_PATH, ""
    else:
        topic = book.topic(topic_id)
        if topic is None:
            return None
        target = paths[topic.page]
        anchor = "" if topic.id == topic.page else f"#{topic.id}"
    start = posixpath.dirname(from_path) or "."
    return posixpath.relpath(target, start) + anchor


def rewrite_links(
    text: str, book: HelpBook, paths: dict[str, str], from_path: str
) -> str:
    """`text` with its `help:` links pointing at the site's pages and its
    `go:` links made plain text."""

    def help_link(match: re.Match[str]) -> str:
        label, topic_id = match.group(1), match.group(2)
        target = link_target(book, paths, topic_id, from_path)
        return label if target is None else f"[{label}]({target})"

    text = _HELP_LINK.sub(help_link, text)
    # The app's own Go there button means nothing on the site: it goes,
    # with the space before it. Any other label stays, as plain text.
    text = _GO_THERE.sub("", text)
    return _GO_LINK.sub(lambda match: match.group(1), text)


def _anchored(text: str, topic_id: str, level: int) -> str:
    """A topic's Markdown with its heading at `level` and its id as the
    heading's anchor."""
    lines = text.splitlines()
    heading = _HEADING.match(lines[0]) if lines else None
    if heading is None:
        return text
    lines[0] = f"{'#' * level} {heading.group(2)} {{#{topic_id}}}"
    return "\n".join(lines)


def page_markdown(book: HelpBook, page: Page, paths: dict[str, str]) -> str:
    """A help page as a site page: its heading the page's title, each
    topic on it a section with its id as anchor, links rewritten."""
    parts: list[str] = []
    for topic_id in page.topics:
        topic = book.topics[topic_id]
        level = 1 if topic_id == page.id else 2
        parts.append(_anchored(topic.text, topic_id, level).strip())
    text = "\n\n".join(parts) + "\n"
    return rewrite_links(text, book, paths, paths[page.id])


def _repo_links(text: str) -> str:
    """Links to files in the repository made links to it on GitHub."""
    return _REPO_LINK.sub(lambda m: f"]({REPO}/blob/main/{m.group(1)})", text)


def export(book: HelpBook) -> list[SitePage]:
    """Every help page as a site page, then About and What's New."""
    paths = page_paths(book)
    pages = [
        SitePage(paths[page.id], page.title, page_markdown(book, page, paths))
        for page in book.pages.values()
    ]
    for path, title, text in (
        (ABOUT_PATH, "About", help_text.about_text()),
        (WHATS_NEW_PATH, "What's New", help_text.whats_new_text()),
    ):
        text = rewrite_links(_repo_links(text), book, paths, path)
        pages.append(SitePage(path, title, text))
    return pages


# -- the menu -----------------------------------------------------------------


def _entry(book: HelpBook, paths: dict[str, str], page: Page, indent: str) -> str:
    """A page's line in the menu, with the pages under it when it has
    any (its own page then opens the section)."""
    children = [
        p
        for p in book.pages.values()
        if p is not page and parent_of(book, p) == page.id
    ]
    title = json.dumps(page.title)
    if not children:
        return f"{indent}- {title}: {paths[page.id]}"
    lines = [f"{indent}- {title}:", f"{indent}  - {paths[page.id]}"]
    lines += [
        f"{indent}  - {json.dumps(child.title)}: {paths[child.id]}"
        for child in children
    ]
    return "\n".join(lines)


def nav_yaml(book: HelpBook) -> str:
    """The site's menu as MkDocs YAML: the hand-written pages, the how-to
    guides, each part of the app's help, then the reference pages."""
    paths = page_paths(book)
    tops = [
        p
        for p in book.pages.values()
        if parent_of(book, p) is None and p.id not in help_text.REFERENCE
    ]
    lines = [
        "nav:",
        "  - Home: index.md",
        "  - Install: install.md",
        "  - FAQ and troubleshooting: faq.md",
        "  - How-to guides:",
    ]
    guides = [p for p in tops if help_text.is_guide(p.id)]
    guides.sort(key=lambda p: p.id not in FIRST_GUIDES)
    lines += [_entry(book, paths, p, "    ") for p in guides]
    lines.append("  - Help:")
    files = list(FILE_TITLES) + sorted(
        {p.file for p in tops} - set(FILE_TITLES) - set(UNLISTED_FILES)
    )
    for name in files:
        in_file = [p for p in tops if p.file == name and not help_text.is_guide(p.id)]
        if not in_file:
            continue
        title = FILE_TITLES.get(name, Path(name).stem.replace("-", " ").capitalize())
        lines.append(f"    - {json.dumps(title)}:")
        lines += [_entry(book, paths, p, "      ") for p in in_file]
    lines.append("  - Reference:")
    lines += [
        f"    - {json.dumps(book.pages[ref].title)}: {paths[ref]}"
        for ref in help_text.REFERENCE
        if ref in book.pages
    ]
    lines += [
        f'    - "What\'s New": {WHATS_NEW_PATH}',
        f"    - About: {ABOUT_PATH}",
    ]
    return "\n".join(lines) + "\n"


# -- building -----------------------------------------------------------------


def write_sources(book: HelpBook, dest: Path = BUILD_SRC) -> Path:
    """Gather the MkDocs sources in `dest`: the hand-written pages, the
    help's pages, the screenshots and fonts, and mkdocs.yml with its menu.
    Returns the mkdocs.yml written."""
    if dest.exists():
        shutil.rmtree(dest)
    docs = dest / "docs"
    shutil.copytree(SITE_DIR / "docs", docs)
    for page in export(book):
        target = docs / page.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(page.markdown, encoding="utf-8")
    shutil.copytree(SCREENSHOTS, docs / "assets" / "screenshots")
    fonts = docs / "assets" / "fonts"
    fonts.mkdir(parents=True)
    for name in FONTS:
        shutil.copy2(FONT_DIR / name, fonts / name)
    config = dest / "mkdocs.yml"
    base = (SITE_DIR / "mkdocs.yml").read_text(encoding="utf-8")
    config.write_text(
        f"{base.rstrip()}\n\ndocs_dir: docs\n\n{nav_yaml(book)}", encoding="utf-8"
    )
    return config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the user-docs website from the desktop's help."
    )
    parser.add_argument(
        "--no-build", action="store_true", help="only write the MkDocs sources"
    )
    parser.add_argument(
        "--serve", action="store_true", help="preview the site (mkdocs serve)"
    )
    args = parser.parse_args(argv)
    config = write_sources(help_text.book(GUI))
    print(f"Sources written to {config.parent}")
    if args.no_build:
        return 0
    if args.serve:
        command = ["serve", "-f", str(config)]
    else:
        command = ["build", "--strict", "-f", str(config), "-d", str(BUILD_OUT)]
    return subprocess.call([sys.executable, "-m", "mkdocs", *command])


if __name__ == "__main__":
    raise SystemExit(main())
