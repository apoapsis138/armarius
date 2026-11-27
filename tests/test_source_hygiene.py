"""The repo's files stay clean of two things no reviewer should have to spot
by eye: invisible characters, and story numbers in the code.

- No tracked text file holds a NUL byte, a zero-width character, a
  byte-order mark, a soft hyphen, a line or paragraph separator, or a
  bidirectional control (the "Trojan Source" characters): a copy-paste or a
  botched rewrite can slip one in, and it is invisible in a diff.
- Story and feature numbers (STORY-n, FEAT-nn) belong in commit messages and
  pull requests, not in the code, the workflows or changelog fragments
  (CONTRIBUTING.md, "Code rules"): the code states the rule plainly. Test
  files that still carry one are listed below, and that list only shrinks.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: The text files to read; anything else tracked (images, fonts, PDFs) is skipped.
TEXT_SUFFIXES = {
    ".py", ".md", ".toml", ".yml", ".yaml", ".json", ".txt", ".css", ".tcss",
    ".jinja", ".spec", ".bat", ".cfg", ".ini", ".sh", ".ps1",
}  # fmt: skip

_INVISIBLE_CODES = (
    0x0000, 0x00AD, 0x200B, 0x200C, 0x200D, 0x2028, 0x2029, 0x2060, 0xFEFF,
    *range(0x202A, 0x202F), *range(0x2066, 0x206A),
)  # fmt: skip
INVISIBLE = re.compile("[" + "".join(map(chr, _INVISIBLE_CODES)) + "]")
STORY_NUMBER = re.compile(r"\b(?:STORY|FEAT)-\d+")

#: Where a story number may not go: code, workflows and changelog fragments.
NUMBER_FREE = re.compile(r"\.py$|^\.github/.*\.ya?ml$|^changelog\.d/.*\.md$")

#: Files that need a story number for good: their sample text names one.
NEEDS_A_NUMBER = {"tests/test_check_pr_body.py"}

#: Test files whose comments or docstrings still name a story. Remove a file
#: once it's clean; nothing new joins the list.
STILL_NUMBERED: set[str] = {
    "tests/test_acclaim.py",
    "tests/test_agents_tab.py",
    "tests/test_aging.py",
    "tests/test_apothecary.py",
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


def _tracked_text() -> dict[str, str]:
    """Each tracked text file's name and contents (undecodable bytes shown
    as replacement characters, so one bad file is named, not fatal)."""
    names = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.split("\0")
    texts = {}
    for name in names:
        path = ROOT / name
        if name and path.suffix in TEXT_SUFFIXES and path.is_file():
            texts[name] = path.read_bytes().decode("utf-8", errors="replace")
    return texts


def test_no_invisible_characters():
    found = [
        f"{name}:{number} U+{ord(match.group()):04X}"
        for name, text in _tracked_text().items()
        for number, line in enumerate(text.splitlines(), 1)
        for match in INVISIBLE.finditer(line)
    ]
    assert not found, "invisible characters (delete them):\n" + "\n".join(found)


def test_story_numbers_stay_out_of_the_code():
    numbered = {
        name
        for name, text in _tracked_text().items()
        if NUMBER_FREE.search(name) and STORY_NUMBER.search(text)
    }
    new = sorted(numbered - STILL_NUMBERED - NEEDS_A_NUMBER)
    assert not new, (
        "story numbers in code (state the rule instead; the number goes in the"
        " commit message):\n" + "\n".join(new)
    )
    clean = sorted(STILL_NUMBERED - numbered)
    assert not clean, "now clean, take off STILL_NUMBERED:\n" + "\n".join(clean)


def test_the_checks_catch_what_they_look_for():
    assert INVISIBLE.search("a" + chr(0x200B) + "b")
    assert INVISIBLE.search(chr(0x202E) + "x")  # right-to-left override
    assert not INVISIBLE.search("plain text, ‘quotes’, é and — dashes")
    assert STORY_NUMBER.search("see STORY" + "-2348")
    assert STORY_NUMBER.search("FEAT" + "-16's")
    assert not STORY_NUMBER.search("STORY_CHECK and FEATURES-1")
    assert NUMBER_FREE.search("main.py") and NUMBER_FREE.search(
        ".github/workflows/x.yml"
    )
    assert NUMBER_FREE.search("changelog.d/a.glossa.md")
    assert not NUMBER_FREE.search("CHANGELOG.md")
