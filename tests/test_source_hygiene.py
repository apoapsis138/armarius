"""The source files stay clean of two things no reviewer should have to spot
by eye: invisible characters, and story numbers in the code.

- No source or doc file holds a NUL byte, a zero-width character or a
  byte-order mark: a copy-paste or a botched rewrite can slip one in, and it
  is invisible in a diff.
- Story and feature numbers (STORY-n, FEAT-nn) belong in commit messages and
  pull requests, not in comments or docstrings (CONTRIBUTING.md, "Code
  rules"): the code states the rule plainly. The app and tools have none; the
  test files that still do are listed below, and the list only shrinks.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Where the source and the contributor docs live.
SOURCE_DIRS = ("ars_magica_manager", "tools", "tests", "docs", "changelog.d")
ROOT_DOCS = ("README.md", "CONTRIBUTING.md", "DESIGN.md", "GLOSSARY.md", "SECURITY.md")
SUFFIXES = {".py", ".md", ".toml", ".yml", ".yaml", ".json"}

INVISIBLE = re.compile(
    "[" + "".join(map(chr, (0x0, 0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF))) + "]"
)
STORY_NUMBER = re.compile(r"\b(?:STORY|FEAT)-\d+")

#: Test files whose comments or docstrings still name a story. Remove a file
#: once it's clean; nothing new joins the list. (test_check_pr_body.py
#: needs one: its sample pull request description names its story.)
STILL_NUMBERED: set[str] = {
    "tests/test_acclaim.py",
    "tests/test_agents_tab.py",
    "tests/test_aging.py",
    "tests/test_apothecary.py",
    "tests/test_check_pr_body.py",
    "tests/test_chronicle_wiring.py",
    "tests/test_city_guild_outcomes.py",
    "tests/test_dice_text.py",
    "tests/test_entered_dice_sieges_agents.py",
    "tests/test_experiment.py",
    "tests/test_fights.py",
    "tests/test_fights_entered_dice.py",
    "tests/test_galdor.py",
    "tests/test_guide_bugs.py",
    "tests/test_hermetic_projects.py",
    "tests/test_hostile_files.py",
    "tests/test_lab_families.py",
    "tests/test_menu_items.py",
    "tests/test_mystic_paths.py",
    "tests/test_record_links.py",
    "tests/test_remote_records.py",
    "tests/test_research.py",
    "tests/test_sieges.py",
    "tests/test_spells.py",
    "tests/test_story_check.py",
    "tests/test_table_roll_sorting.py",
    "tests/test_table_rolls.py",
    "tests/test_tmre_dreams.py",
    "tests/test_warping.py",
}


def _files() -> Iterator[Path]:
    for name in ROOT_DOCS:
        if (ROOT / name).is_file():
            yield ROOT / name
    for folder in SOURCE_DIRS:
        for path in sorted((ROOT / folder).rglob("*")):
            if (
                path.is_file()
                and path.suffix in SUFFIXES
                and "__pycache__" not in path.parts
            ):
                yield path


def _name(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def test_no_invisible_characters():
    found = []
    for path in _files():
        text = path.read_bytes().decode("utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), 1):
            match = INVISIBLE.search(line)
            if match:
                found.append(f"{_name(path)}:{number} U+{ord(match.group()):04X}")
    assert not found, "invisible characters (delete them):\n" + "\n".join(found)


def test_story_numbers_stay_out_of_the_code():
    numbered = {
        _name(path)
        for folder in ("ars_magica_manager", "tools", "tests")
        for path in (ROOT / folder).rglob("*.py")
        if STORY_NUMBER.search(path.read_text(encoding="utf-8"))
    }
    new = sorted(numbered - STILL_NUMBERED)
    assert not new, (
        "story numbers in code (state the rule instead; the number goes in the"
        " commit message):\n" + "\n".join(new)
    )
    clean = sorted(STILL_NUMBERED - numbered)
    assert not clean, "now clean, take off STILL_NUMBERED:\n" + "\n".join(clean)


def test_the_checks_catch_what_they_look_for():
    assert INVISIBLE.search("a" + chr(0x200B) + "b") and INVISIBLE.search(
        chr(0xFEFF) + "x"
    )
    assert not INVISIBLE.search("plain text, ‘quotes’ and é")
    assert STORY_NUMBER.search("see STORY" + "-2348") and STORY_NUMBER.search(
        "FEAT" + "-16's"
    )
    assert not STORY_NUMBER.search("STORY_CHECK and FEATURES-1")
