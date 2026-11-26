"""tools/check_pr_body.py: a pull request's description follows the template
and reads as a description of the change, not a report from whoever made it."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


check = _load("check_pr_body", ROOT / "tools" / "check_pr_body.py")

GOOD = """## Summary

The Hubris Trait gains experience by itself when a magus's pride wins a roll.

```mermaid
flowchart LR
  roll --> hubris --> experience
```

## Evidence

Before: the Trait never moved. After: a won Hubris roll adds one point.

## Merge Danger

Two-way door: the rule is one function, easily reverted. Blast radius: the
character sheet's Personality section.

## Armarius

### Story

STORY-2492

### Pattern

None: a plain function.

### Rules

ArM5 p. 19 (Hubris); errata p. 2.

### Help

`help/character.md`, the Personality section.

### Changelog

`changelog.d/hubris-sympathy-experience.pagina.md`

### Checks

`tools/story_check.py --full`: 9,812 passed.
"""


def _problems(body: str, blocked: tuple[str, ...] = ()) -> list[str]:
    return check.problems(body, blocked)


def _with(extra: str) -> str:
    return GOOD.replace("## Evidence\n", f"## Evidence\n\n{extra}\n", 1)


def test_a_good_body_passes():
    assert _problems(GOOD) == []


def test_the_template_itself_has_every_heading():
    template = (ROOT / ".github" / "pull_request_template.md").read_text(
        encoding="utf-8"
    )
    missing = [p for p in _problems(template) if "missing heading" in p]
    assert missing == []


@pytest.mark.parametrize("heading", check.REQUIRED_HEADINGS)
def test_each_missing_heading_is_named(heading: str):
    body = "\n".join(
        line for line in GOOD.splitlines() if line.lstrip("#").strip() != heading
    )
    assert any(f"missing heading: {heading}" in p for p in _problems(body))


def test_an_empty_section_is_named_but_none_is_fine():
    empty = GOOD.replace("None: a plain function.", "")
    assert any("empty section: Pattern" in p for p in _problems(empty))
    for word in ("None", "n/a", "N/A"):
        assert _problems(GOOD.replace("None: a plain function.", word)) == []


@pytest.mark.parametrize(
    "sentence",
    [
        "I fixed the roll.",
        "I'm sure it works.",
        "I've added a test.",
        "I'd merge it first.",
        "I'll follow up.",
        "Tell me if it breaks.",
        "My test covers it.",
    ],
)
def test_first_person_narration_fails(sentence: str):
    found = _problems(_with(sentence))
    assert found and all("first person" in p for p in found)


@pytest.mark.parametrize(
    "text",
    [
        "`I` is the index.",
        "```\nI ran it\n```",
        "> I am the storyguide's note, quoted.",
        'The button says "Tell me more".',
        "Item, image, mythic: no whole-word hits.",
    ],
)
def test_first_person_inside_code_or_quotes_passes(text: str):
    assert _problems(_with(text)) == []


@pytest.mark.parametrize(
    "sentence",
    [
        "Claude wrote this.",
        "Made with Claude Code.",
        "The agent checked the diff.",
        "A subagent reviewed it.",
        "Run over Remote Control.",
        "One tool call was slow.",
        "After a skill invocation the tests passed.",
    ],
)
def test_agent_and_tool_names_fail(sentence: str):
    found = _problems(_with(sentence))
    assert found and all("tool or agent name" in p for p in found)


def test_names_inside_code_and_the_agents_feature_pass():
    assert _problems(_with("The `agent` field, and `claude.yml`.")) == []
    assert _problems(_with("Agents can now be tamed from the More menu.")) == []


@pytest.mark.parametrize(
    "line",
    [
        "Co-Authored-By: Someone <x@example.com>",
        "Generated with a tool",
        "Session: https://claude.ai/code/session_1",
        "<noreply@anthropic.com>",
    ],
)
def test_attribution_lines_fail_even_in_code(line: str):
    found = _problems(_with(f"```\n{line}\n```"))
    assert any("attribution" in p for p in found)


@pytest.mark.parametrize("sentence", ["The magus loses his Gift.", "She rolls."])
def test_gendered_pronouns_fail(sentence: str):
    found = _problems(_with(sentence))
    assert found and all("pronoun" in p for p in found)


def test_pronouns_in_quoted_book_text_and_code_pass():
    assert _problems(_with('> "He who holds the vis" (ArM5 p. 1)')) == []
    assert _problems(_with('The book says "her familiar" here.')) == []
    assert _problems(_with("`CrHe` and `his_gift` stay.")) == []


def test_the_pronoun_list_is_the_screen_texts_list():
    screen = _load("test_neutral_pronouns", ROOT / "tests" / "test_neutral_pronouns.py")
    assert check.PRONOUN.pattern == screen.PRONOUN.pattern
    assert check.PRONOUN.flags == screen.PRONOUN.flags


def test_a_blocked_name_fails_anywhere_without_printing_it():
    found = _problems(_with("```\nThanks, Zephyrine.\n```"), ("Quill", " zephyrine "))
    assert len(found) == 1
    assert "blocked name" in found[0]
    assert "zephyrine" not in found[0].lower()


def test_a_blocked_name_is_a_whole_word():
    assert _problems(_with("Quillon guards."), ("Quill",)) == []


def test_problems_name_their_line():
    found = _problems(_with("I fixed it."))
    line = GOOD.splitlines().index("## Evidence") + 3
    assert found == [
        f"line {line}: first person: 'I' (describe the change, not who made it)"
    ]


def _run(body: str, env_names: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "tools" / "check_pr_body.py")],
        input=body,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "BLOCKED_NAMES": env_names},
        check=False,
    )


def test_the_script_reads_stdin_and_the_env():
    assert _run(GOOD).returncode == 0
    bad = _run(_with("Thanks, Zephyrine."), "Quill,Zephyrine")
    assert bad.returncode == 1
    assert "blocked name" in bad.stdout
    assert "Zephyrine" not in bad.stdout + bad.stderr


def test_the_script_reads_a_file(tmp_path: Path):
    path = tmp_path / "body.md"
    path.write_text(_with("I fixed it."), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "check_pr_body.py"), str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 1
    assert "first person" in result.stdout
