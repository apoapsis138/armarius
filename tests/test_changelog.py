"""CHANGELOG.md read as features, editions and versions (changelog.py),
and the What's New page made from it."""

from __future__ import annotations

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


def test_the_chronicle_has_a_line_per_version_under_its_day():
    chronicle = cl.chronicle_text(_log())
    assert chronicle.index("### Creo (1.x)\n\nThe first version.") < chronicle.index(
        "#### 19 October 2026"
    )
    assert "#### 16 October 2026\n\n- **1.1.0** · Packs I · The Rhine pack;" in (
        chronicle
    )
    assert "- **1.2.0** · Help I, Packs II · How-to guides; A pack fix" in chronicle
    assert "- **1.0.0** · Help I · *Incipit: the first version.* Help begins" in (
        chronicle
    )


def test_a_short_label_before_a_colon_gives_way_to_what_follows():
    entry = "- Behind the scenes: the forms are split. More."
    assert cl.headline(entry) == "The forms are split"


# -- the real changelog --


def _real() -> cl.Changelog:
    return cl.parse((ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))


def test_the_changelog_reads_and_has_this_version():
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
