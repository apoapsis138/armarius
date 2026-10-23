"""Which test files are screen tests: the slow tier, marked `ui` by
tests/conftest.py and left out of a slice's run by slice_tests.py."""

from __future__ import annotations

import re
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent.parent / "tests"

# A screen test drives the Textual app with Pilot or builds the desktop's
# Qt widgets, itself or through a shared driver (the dialog contracts'
# run_contract). It imports PySide6, not merely names it: the core-boundary
# check names it as a library the core may not import.
_SCREEN_TEST_SIGNS = re.compile(
    r"run_test\(|^\s*(?:from|import) PySide6\b|gui_steps|run_contract\(",
    re.MULTILINE,
)

_screen_files: dict[Path, bool] = {}


def is_screen_test_file(path: Path) -> bool:
    if path not in _screen_files:
        text = path.read_text(encoding="utf-8")
        _screen_files[path] = _SCREEN_TEST_SIGNS.search(text) is not None
    return _screen_files[path]


def test_files() -> list[Path]:
    return sorted(TESTS_DIR.glob("test_*.py"))
