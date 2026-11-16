"""CHANGELOG.md read as features, editions and versions (changelog.py),
and the What's New page made from it."""

from __future__ import annotations

import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

from ars_magica_manager import ROOT, __version__
from ars_magica_manager import changelog as cl

SAMPLE = """# Changelog

What changed, by feature.

## Features

| Feature | What it is |
| --- | --- |
| Packs | The Tribunal packs |
| Help | Help and its guides |

## Editions

| Edition | Title | Finished in | What it brought |
| --- | --- | --- | --- |
| Packs I | The Rhine | 1.1.0 | The first pack |
| Help I | Guides | 1.2.0 | How-to guides |

## Major versions

| Major | Name | What it marked |
| --- | --- | --- |
| 1 | Creo | the first version |

## Milestones

| Milestone | Version | What it marked |
| --- | --- | --- |
| Incipit | 1.0.0 | the first version |

## 1.4.0 — 2026-10-19

### Packs

- **The Normandy pack.** Normandy as a pack.

## 1.3.1 — 2026-10-18

### Help

- **A typo.** Fixed.

## 1.2.0 — 2026-10-17

### Help

- **How-to guides.** Eight of them.

### Packs

- **A pack fix.** Mended.

## 1.1.0 — 2026-10-16

### Packs

- **The Rhine pack.** The first pack.
- A pack can be chosen in part: what to bring.

## 1.0.0 — 2026-10-15

### Help

Help begins.
"""


def _log() -> cl.Changelog:
    return cl.parse(SAMPLE)


def _edition(log: cl.Changelog, name: str) -> cl.Edition:
    return next(e for e in log.editions if e.name == name)


def test_each_version_is_read_with_its_features():
    log = _log()
    assert [v.number for v in log.versions] == [
        "1.4.0",
        "1.3.1",
        "1.2.0",
        "1.1.0",
        "1.0.0",
    ]
    assert [p.feature for p in log.versions[2].parts] == ["Help", "Packs"]
    assert (
        log.versions[0].parts[0].text == "- **The Normandy pack.** Normandy as a pack."
    )


def test_an_edition_holds_its_features_work_up_to_its_version():
    log = _log()
    assert [p.version for p in _edition(log, "Packs I").parts] == ["1.1.0"]
    assert [p.version for p in _edition(log, "Help I").work] == ["1.0.0", "1.2.0"]


def test_work_after_the_last_edition_is_the_next_edition_in_progress():
    log = _log()
    packs = _edition(log, "Packs II")
    assert packs.finished_in == "" and packs.heading == "Packs II, in progress"
    # Everything after Packs I was finished, its oldest first.
    assert [p.version for p in packs.parts] == ["1.2.0", "1.4.0"]


def test_bug_fixes_alone_after_the_last_edition_belong_to_it():
    log = _log()
    assert [p.version for p in _edition(log, "Help I").parts][-1] == "1.3.1"
    assert not any(e.name == "Help II" for e in log.editions)


def test_an_editions_span_counts_only_its_own_versions():
    help_i = _edition(_log(), "Help I")
    assert help_i.span() == "15 to 17 October 2026, versions 1.0.0 to 1.2.0"


def test_headlines_are_the_bold_lead_else_the_first_sentence():
    part = _edition(_log(), "Packs I").parts[0]
    assert part.headlines() == ["The Rhine pack", "A pack can be chosen in part"]
    assert cl.headline("- " + "word " * 30).endswith("…")


def test_roman_numerals_both_ways():
    for n in (1, 4, 9, 14, 40, 99):
        assert cl.roman(cl.numeral(n)) == n
    assert cl.numeral(14) == "XIV"


def test_the_release_name_is_the_major_versions_name():
    assert cl.release_name(SAMPLE, "1.4.0") == "Creo"
    assert cl.release_name(SAMPLE, "2.0.0") == ""
    assert cl.release_name("# Changelog\n\n## 1.0.0 — 2026-09-29\n", "1.0.0") == ""


def test_a_feature_heading_must_be_a_known_feature():
    with pytest.raises(cl.ChangelogError, match="unknown feature"):
        cl.parse(SAMPLE.replace("### Packs\n\n- **The Normandy", "### Pax\n\n- **N"))
    with pytest.raises(cl.ChangelogError, match="under no feature"):
        cl.parse(SAMPLE.replace("### Help\n\nHelp begins.", "Help begins."))


def test_the_page_has_latest_then_each_feature_then_the_chronicle():
    page = cl.whats_new(SAMPLE)
    headings = [line for line in page.splitlines() if line.startswith("## ")]
    # Packs did the most recent work, so it comes first.
    assert headings == ["## Latest", "## Packs", "## Help", "## Chronicle"]
    latest = page.split("## Latest", 1)[1].split("\n## ", 1)[0]
    assert latest.index("**Packs II**, in progress") < latest.index(
        "**Help I: Guides**"
    )
    assert "The Normandy pack; A pack fix." in latest
    # A feature's newest edition in full, each entry with its version;
    # its earlier ones by their headlines.
    assert "- **A typo.** Fixed. (1.3.1)" in page
    assert "- The Rhine pack (1.1.0)\n- A pack can be chosen in part (1.1.0)" in page


PLAIN = SAMPLE.replace(
    "| Feature | What it is |\n| --- | --- |\n| Packs | The Tribunal packs |\n"
    "| Help | Help and its guides |",
    "| Feature | Plain name | What it is |\n| --- | --- | --- |\n"
    "| Packs | Sourcebook packs | The Tribunal packs |\n"
    "| Help | Help | Help and its guides |",
)


def test_a_plain_name_comes_first_wherever_the_page_names_a_feature():
    log = cl.parse(PLAIN)
    assert cl.parse(SAMPLE).feature("Packs").plain == ""
    assert log.feature("Packs").label == "Sourcebook packs (Packs)"
    # A plain name the same as the feature's own isn't said twice.
    assert log.feature("Help").label == "Help"
    page = cl.whats_new(PLAIN)
    headings = [line for line in page.splitlines() if line.startswith("## ")]
    assert headings == [
        "## Latest",
        "## Sourcebook packs (Packs)",
        "## Help",
        "## Chronicle",
    ]
    assert "### Sourcebook packs I: The Rhine" in page
    assert "**Sourcebook packs II**, in progress" in page
    assert "- **1.1.0** · Sourcebook packs I · The Rhine pack;" in page
    # Its editions keep their own names, for the Editions table.
    assert _edition(log, "Packs I").heading == "Packs I: The Rhine"


def test_the_chronicle_has_a_line_per_version_under_its_day():
    chronicle = cl.chronicle_text(_log())
    assert chronicle.index(
        "### Version 1.x: Creo\n\nThe first version."
    ) < chronicle.index("#### 19 October 2026")
    assert "#### 16 October 2026\n\n- **1.1.0** · Packs I · The Rhine pack;" in (
        chronicle
    )
    assert "- **1.2.0** · Help I, Packs II · How-to guides; A pack fix" in chronicle
    assert "- **1.0.0** · Help I · *Incipit: the first version.* Help begins" in (
        chronicle
    )


def test_an_unreleased_section_is_refused():
    # Unreleased work waits in changelog.d/ fragments until a release.
    pending = "## Unreleased\n\n### Help\n\n- **A new guide.** Written.\n\n"
    with pytest.raises(cl.ChangelogError, match="changelog.d"):
        cl.parse(SAMPLE.replace("## 1.4.0", pending + "## 1.4.0", 1))


def test_entries_above_the_newest_version_are_refused():
    # What a merge once left: a feature's entries under the towncrier
    # marker, with no version heading over them.
    stray = (
        "<!-- towncrier release notes start -->\n\n### Scriptorum\n\n"
        "- **Closing a window while it fills in.** No longer crashes.\n\n"
    )
    with pytest.raises(cl.ChangelogError, match="under no version"):
        cl.parse(SAMPLE.replace("## 1.4.0", stray + "## 1.4.0", 1))


def test_the_page_shows_released_versions_only():
    page = cl.whats_new(SAMPLE)
    headings = [line for line in page.splitlines() if line.startswith("## ")]
    assert headings[0] == "## Latest"
    assert "Unreleased" not in page


def test_a_short_label_before_a_colon_gives_way_to_what_follows():
    entry = "- Behind the scenes: the forms are split. More."
    assert cl.headline(entry) == "The forms are split"


# -- the real changelog --


def _real() -> cl.Changelog:
    return cl.parse((ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))


def test_the_changelog_reads_and_has_this_version():
    # The newest version is the one pyproject.toml names.
    log = _real()
    assert log.versions[0].number == __version__


def test_every_edition_is_finished_in_a_version_of_its_own_feature():
    log = _real()
    worked = {(p.feature, p.version) for v in log.versions for p in v.parts}
    for edition in log.editions:
        if edition.finished_in:
            assert (edition.feature, edition.finished_in) in worked, edition.name


def test_each_features_editions_are_numbered_from_one_in_order():
    log = _real()
    for feature in log.features:
        editions = log.feature_editions(feature.name)
        assert [e.number for e in editions] == list(range(1, len(editions) + 1))
        finished = [cl.version_key(e.finished_in) for e in editions if e.finished_in]
        assert finished == sorted(finished), feature.name


def test_every_milestone_is_a_version():
    log = _real()
    numbers = {v.number for v in log.versions}
    assert all(m.version in numbers for m in log.milestones)


def test_every_major_version_has_a_name():
    log = _real()
    numbers = {cl.version_key(v.number)[0] for v in log.versions}
    assert all(log.major(n) for n in numbers)


# -- the fragments (changelog.d/), built into a version at a release --

FRAGMENTS = ROOT / "changelog.d"
#: The files in changelog.d/ that aren't fragments.
NOT_FRAGMENTS = {"README.md", "template.md.jinja"}
#: A fragment: "<slug>.<feature type>.md", the slug in lowercase words.
_FRAGMENT_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.([a-z]+)\.md$")
#: The most words a fragment may have: one entry, not an essay.
MOST_WORDS = 40


def _towncrier() -> dict:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return pyproject["tool"]["towncrier"]


def _types() -> dict[str, str]:
    """Each fragment type's key (its directory), and the feature it names."""
    return {t["directory"]: t["name"] for t in _towncrier()["type"]}


def _fragments() -> list[Path]:
    return sorted(
        p for p in FRAGMENTS.iterdir() if p.is_file() and p.name not in NOT_FRAGMENTS
    )


def test_each_feature_has_a_fragment_type_in_the_tables_order():
    assert list(_types().values()) == [f.name for f in _real().features]
    assert sorted(_towncrier()["ignore"]) == sorted(NOT_FRAGMENTS)


def test_the_start_marker_sits_just_above_the_newest_version():
    lines = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8").splitlines()
    marker = lines.index(_towncrier()["start_string"].strip())
    newest = next(i for i, line in enumerate(lines) if line.startswith("## "))
    later = [line for line in lines[marker + 1 :] if line.strip()]
    assert later[0] == f"## {_real().versions[0].number} — {_real().versions[0].date}"
    assert newest < marker  # the preamble's sections come first


@pytest.mark.parametrize("path", _fragments(), ids=lambda p: p.name)
def test_every_fragment_is_one_short_entry_for_a_known_feature(path: Path):
    match = _FRAGMENT_NAME.match(path.name)
    assert match, f"{path.name}: name it <slug>.<feature>.md"
    assert match.group(1) in _types(), f"{path.name}: no feature {match.group(1)!r}"
    text = path.read_text(encoding="utf-8").strip()
    # One paragraph, the bullet and heading left to the release's template.
    assert text and "\n\n" not in text, f"{path.name}: one paragraph"
    assert not text.startswith(("- ", "* ", "#")), f"{path.name}: no bullet or heading"
    # A bold headline, then plain English, ending as a sentence does.
    assert re.match(r"^\*\*[^*]+[.?!:]\*\* \S", text), (
        f"{path.name}: **Headline.** first"
    )
    assert text.endswith((".", ")", "?", "!")), f"{path.name}: end with a full stop"
    words = len(text.split())
    assert words <= MOST_WORDS, f"{path.name}: {words} words, at most {MOST_WORDS}"


def _release_notes():
    spec = importlib.util.spec_from_file_location(
        "release_notes", ROOT / "tools" / "release_notes.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a_release_built_from_the_fragments_reads_back(tmp_path: Path):
    """towncrier, run as a release runs it, writes a section What's New,
    the release notes and the site read: every feature's fragment under
    its feature, in the table's order, above the newest version."""
    for name in ("pyproject.toml", "CHANGELOG.md"):
        shutil.copy(ROOT / name, tmp_path / name)
    shutil.copytree(FRAGMENTS, tmp_path / "changelog.d")
    for key, feature in _types().items():
        (tmp_path / "changelog.d" / f"sample.{key}.md").write_text(
            f"**A {feature} sample.** Built for the test.\n", encoding="utf-8"
        )
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    subprocess.run(
        [sys.executable, "-m", "towncrier", "build", "--keep"]
        + ["--version", "99.0.0", "--date", "2099-01-01"]
        + ["--config", str(tmp_path / "pyproject.toml"), "--dir", str(tmp_path)],
        check=True,
        capture_output=True,
        env=env,
    )
    built = (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8")
    log = cl.parse(built)
    newest, before = log.versions[0], _real().versions[0]
    assert (newest.number, newest.date) == ("99.0.0", "2099-01-01")
    assert log.versions[1].number == before.number
    assert [p.feature for p in newest.parts] == [f.name for f in log.features]
    for part in newest.parts:
        assert f"- **A {part.feature} sample.** Built for the test." in part.text
    assert "- **99.0.0** · " in cl.whats_new(built)
    notes = _release_notes().notes(built, "99.0.0")
    assert "Built for the test." in notes and "## " + before.number not in notes
