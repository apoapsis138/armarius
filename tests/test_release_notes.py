"""tools/release_notes.py: a release's notes from its CHANGELOG.md section."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from ars_magica_manager import ROOT, __version__

_spec = importlib.util.spec_from_file_location(
    "release_notes", ROOT / "tools" / "release_notes.py"
)
assert _spec and _spec.loader
release_notes = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(release_notes)

SAMPLE = """# Changelog

## Unreleased

### Help

- Not out yet.

## 1.2.0 — 2026-10-17

### Help

- **How-to guides.** Eight of them.

### Packs

- **A pack fix.** Mended.

## 1.1.0 — 2026-10-16

### Packs

- **The Rhine pack.**
"""


def test_the_notes_are_the_versions_section_without_its_heading():
    text = release_notes.notes(SAMPLE, "1.2.0")
    assert text.startswith("### Help\n\n- **How-to guides.**")
    assert text.endswith("- **A pack fix.** Mended.\n")
    assert "1.1.0" not in text and "Not out yet" not in text


def test_the_last_section_runs_to_the_end():
    assert (
        release_notes.notes(SAMPLE, "1.1.0") == "### Packs\n\n- **The Rhine pack.**\n"
    )


def test_a_missing_version_fails():
    with pytest.raises(LookupError, match="no '## 1.3.0"):
        release_notes.notes(SAMPLE, "1.3.0")
    # A version number is matched whole, not as a prefix of another.
    with pytest.raises(LookupError):
        release_notes.notes(SAMPLE, "1.2")


def test_the_real_changelog_has_notes_for_this_version(tmp_path: Path):
    out = tmp_path / "notes.md"
    assert release_notes.main([__version__, "--out", str(out)]) == 0
    assert out.read_text(encoding="utf-8").startswith("### ")
    assert release_notes.main(["0.0.99", "--out", str(out)]) == 1
