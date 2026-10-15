"""Which test files are screen tests: the slow tier, marked `ui` by
tests/conftest.py and left out of a slice's run by slice_tests.py."""

from __future__ import annotations

from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent.parent / "tests"

# A screen test drives the Textual app with Pilot or builds the desktop's
# Qt widgets.
_SCREEN_TEST_SIGNS = ("run_test(", "PySide6", "gui_steps")

_screen_files: dict[Path, bool] = {}


def is_screen_test_file(path: Path) -> bool:
    if path not in _screen_files:
        text = path.read_text(encoding="utf-8")
        _screen_files[path] = any(sign in text for sign in _SCREEN_TEST_SIGNS)
    return _screen_files[path]


def test_files() -> list[Path]:
    return sorted(TESTS_DIR.glob("test_*.py"))
