"""Check a pull request's description: the template's headings, each filled
in, and wording that describes the change rather than who made it.

    uv run python tools/check_pr_body.py [BODY.md]   (stdin when no file)

Exits 1 and prints one line per problem:

- a missing heading of `.github/pull_request_template.md`, or a section left
  empty (write "None" or "n/a" where it doesn't apply);
- first-person narration (I, I'm, I've, I'd, I'll, me, my);
- a tool or agent name (Claude, Claude Code, agent, subagent, Remote
  Control, tool call, skill invocation). `agent` is matched in lower case
  only, so the app's Agents can be named;
- an attribution line (Co-Authored-By, "Generated with", a claude.ai/code
  link, an Anthropic noreply address), even inside code;
- a gendered pronoun, as tests/test_neutral_pronouns.py finds them in
  screen text;
- a name listed in the BLOCKED_NAMES environment variable (comma
  separated), anywhere. The problem gives the name's place in the list,
  never the name.

Code spans and blocks are left out of the wording checks; quoted text (a
`>` line or a "double-quoted" span, such as a book's words) is left out of
the first-person and pronoun checks. HTML comments are left out of every
check but the attribution and name ones.
"""

from __future__ import annotations

import os
import re
import sys
from collections.abc import Iterator, Sequence
from pathlib import Path

#: The template's headings, in order. A container heading holds only
#: subheadings, so it may have no text of its own.
REQUIRED_HEADINGS: tuple[str, ...] = (
    "Summary",
    "Evidence",
    "Merge Danger",
    "Armarius",
    "Story",
    "Pattern",
    "Rules",
    "Help",
    "Changelog",
    "Checks",
)
CONTAINERS = frozenset({"Armarius"})

#: The same words tests/test_neutral_pronouns.py looks for in screen text.
PRONOUN = re.compile(r"\b(he|him|his|she|her|hers|himself|herself)\b", re.IGNORECASE)

_FIRST_PERSON = re.compile(
    r"(?<![\w'’])I(?:['’](?:m|ve|d|ll))?(?![\w'’])|\b(?i:me|my)\b"
)
_TOOL_NAMES = re.compile(
    r"\b(?:(?i:claude code|claude|tool calls?|skill invocations?)|Remote Control"
    r"|(?:sub)?agents?|Subagents?)\b"
)
_ATTRIBUTION = re.compile(
    r"co-authored-by:|generated with|claude\.ai/code|noreply@anthropic\.com",
    re.IGNORECASE,
)
_HEADING = re.compile(r"^ {0,3}#{1,6}[ \t]+(.+?)[ \t]*#*[ \t]*$")
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_CODE_SPAN = re.compile(r"(`+).+?\1")
_QUOTED = re.compile(r'"[^"\n]*"|“[^”\n]*”')
_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def _blank(match: re.Match[str]) -> str:
    """The match with every character but newlines turned into spaces."""
    return re.sub(r"[^\n]", " ", match.group(0))


def _lines(body: str) -> Iterator[tuple[int, str, bool]]:
    """(line number, line, inside a code block) for each line, with HTML
    comments blanked."""
    fence = ""
    for number, line in enumerate(_COMMENT.sub(_blank, body).splitlines(), 1):
        opening = _FENCE.match(line)
        if fence:
            if (
                opening
                and opening.group(1)[0] == fence[0]
                and len(opening.group(1)) >= len(fence)
            ):
                fence = ""
            yield number, line, True
        elif opening:
            fence = opening.group(1)
            yield number, line, True
        else:
            yield number, line, False


def _sections(body: str) -> dict[str, list[str]]:
    """Each heading's lines, up to the next heading of any level."""
    sections: dict[str, list[str]] = {}
    current: list[str] | None = None
    for _, line, in_code in _lines(body):
        heading = None if in_code else _HEADING.match(line)
        if heading:
            current = sections.setdefault(heading.group(1).strip(), [])
        elif current is not None:
            current.append(line)
    return sections


def _heading_problems(body: str) -> Iterator[str]:
    sections = _sections(body)
    for heading in REQUIRED_HEADINGS:
        if heading not in sections:
            yield f"missing heading: {heading}"
        elif heading not in CONTAINERS and not any(
            s.strip() for s in sections[heading]
        ):
            yield f"empty section: {heading} (write None or n/a if it doesn't apply)"


def _wording_problems(body: str) -> Iterator[str]:
    for number, raw, in_code in _lines(body):
        if in_code or _HEADING.match(raw):
            continue
        line = _CODE_SPAN.sub(" ", raw)
        for match in _TOOL_NAMES.finditer(line):
            yield f"line {number}: tool or agent name: {match.group(0)!r}"
        if line.lstrip().startswith(">"):
            continue
        unquoted = _QUOTED.sub(" ", line)
        for match in _FIRST_PERSON.finditer(unquoted):
            yield (
                f"line {number}: first person: {match.group(0)!r}"
                " (describe the change, not who made it)"
            )
        for match in PRONOUN.finditer(unquoted):
            yield f"line {number}: gendered pronoun: {match.group(0)!r} (write they/their)"


def _raw_problems(body: str, blocked_names: Sequence[str]) -> Iterator[str]:
    names = [
        (place, re.compile(rf"(?<!\w){re.escape(name.strip())}(?!\w)", re.IGNORECASE))
        for place, name in enumerate(blocked_names, 1)
        if name.strip()
    ]
    for number, line in enumerate(body.splitlines(), 1):
        if _ATTRIBUTION.search(line):
            yield f"line {number}: attribution line (the repo has its own statement on AI use)"
        for place, name in names:
            if name.search(line):
                yield f"line {number}: blocked name #{place} from BLOCKED_NAMES"


def problems(body: str, blocked_names: Sequence[str] = ()) -> list[str]:
    """Every problem with a pull request description, in a stable order."""
    return [
        *_heading_problems(body),
        *_wording_problems(body),
        *_raw_problems(body, blocked_names),
    ]


def main(argv: Sequence[str]) -> int:
    if len(argv) > 1:
        body = Path(argv[1]).read_text(encoding="utf-8")
    else:
        body = sys.stdin.buffer.read().decode("utf-8")
    blocked = os.environ.get("BLOCKED_NAMES", "").split(",")
    found = problems(body, blocked)
    for problem in found:
        print(problem)
    if found:
        print(
            f"{len(found)} problem(s); see CONTRIBUTING.md, 'Writing a pull request'."
        )
        return 1
    print("The pull request description passes.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
