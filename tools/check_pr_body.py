"""Check a pull request's description: the template's headings, each filled
in, and wording that describes the change rather than who made it.

    uv run python tools/check_pr_body.py [BODY.md]   (stdin when no file)

Exits 1 and prints one line per problem:

- a missing heading of `.github/pull_request_template.md`, or a section left
  empty (write "None" or "n/a" where it doesn't apply); a section's text
  may sit under a subheading of its own;
- first-person narration (I, I'm, I've, I'd, I'll, me, my; not "I/O", nor
  "Me", Mentem's abbreviation);
- an attribution line (one starting Co-Authored-By: or "Generated with"),
  even inside code;
- a gendered pronoun, as tests/test_neutral_pronouns.py finds them in
  screen text, but for Herbam written as an Art ("(He)", "He 15");
- a term listed in the BLOCKED_TERMS environment variable (comma
  separated), outside code;
- a name listed in the BLOCKED_NAMES environment variable (comma
  separated), anywhere.

A blocked term or name is matched as a whole word or phrase, ignoring
case, and the problem gives its place in its list, never the word itself:
the lists are kept as repository secrets.

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

# "I" but not "I/O"; "me" and "my" but not "Me", Mentem's abbreviation.
_FIRST_PERSON = re.compile(
    r"(?<![\w'’])I(?:['’](?:m|ve|d|ll))?(?![\w'’/])|\b(?:me|my|My)\b"
)
_ATTRIBUTION = re.compile(r"^\W*(?:co-authored-by:|generated with\b)", re.IGNORECASE)
#: Herbam's abbreviation, written as an Art is: "(He)" or "He 15".
_HERBAM = re.compile(r"\(He\)|\bHe(?=\s*\d)")
_HEADING = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_CLOSING_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*$")
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
            closing = _CLOSING_FENCE.match(line)
            if (
                closing
                and closing.group(1)[0] == fence[0]
                and len(closing.group(1)) >= len(fence)
            ):
                fence = ""
            yield number, line, True
        elif opening:
            fence = opening.group(1)
            yield number, line, True
        else:
            yield number, line, False


def _sections(body: str) -> dict[str, list[str]]:
    """Each heading's lines, up to the next heading of its own level or
    higher, subheadings and their text included."""
    sections: dict[str, list[str]] = {}
    open_sections: list[tuple[int, list[str]]] = []
    for _, line, in_code in _lines(body):
        heading = None if in_code else _HEADING.match(line)
        if heading:
            level = len(heading.group(1))
            open_sections = [(lv, ls) for lv, ls in open_sections if lv < level]
            for _, lines in open_sections:
                lines.append(line)
            open_sections.append(
                (level, sections.setdefault(heading.group(2).strip(), []))
            )
        else:
            for _, lines in open_sections:
                lines.append(line)
    return sections


def _heading_problems(body: str) -> Iterator[str]:
    sections = _sections(body)
    for heading in REQUIRED_HEADINGS:
        if heading not in sections:
            yield f"missing heading: {heading}"
        elif heading not in CONTAINERS and not any(
            s.strip() and not _HEADING.match(s) for s in sections[heading]
        ):
            yield f"empty section: {heading} (write None or n/a if it doesn't apply)"


def _listed(words: Sequence[str]) -> list[tuple[int, re.Pattern[str]]]:
    """Each listed word or phrase with its place in the list, as a
    case-blind whole-word pattern."""
    return [
        (place, re.compile(rf"(?<!\w){re.escape(word.strip())}(?!\w)", re.IGNORECASE))
        for place, word in enumerate(words, 1)
        if word.strip()
    ]


def _wording_problems(body: str, blocked_terms: Sequence[str]) -> Iterator[str]:
    terms = _listed(blocked_terms)
    for number, raw, in_code in _lines(body):
        if in_code:
            continue
        line = _CODE_SPAN.sub(" ", raw)
        for place, term in terms:
            if term.search(line):
                yield f"line {number}: blocked term #{place} from BLOCKED_TERMS"
        if line.lstrip().startswith(">"):
            continue
        unquoted = _HERBAM.sub(" ", _QUOTED.sub(" ", line))
        for match in _FIRST_PERSON.finditer(unquoted):
            yield (
                f"line {number}: first person: {match.group(0)!r}"
                " (describe the change, not who made it)"
            )
        for match in PRONOUN.finditer(unquoted):
            yield f"line {number}: gendered pronoun: {match.group(0)!r} (write they/their)"


def _anywhere_problems(body: str, blocked_names: Sequence[str]) -> Iterator[str]:
    """Attribution lines and blocked names, looked for in code and comments too."""
    names = _listed(blocked_names)
    for number, line in enumerate(body.splitlines(), 1):
        if _ATTRIBUTION.search(line):
            yield f"line {number}: attribution line"
        for place, name in names:
            if name.search(line):
                yield f"line {number}: blocked name #{place} from BLOCKED_NAMES"


def problems(
    body: str, blocked_names: Sequence[str] = (), blocked_terms: Sequence[str] = ()
) -> list[str]:
    """Every problem with a pull request description, in a stable order."""
    return [
        *_heading_problems(body),
        *_wording_problems(body, blocked_terms),
        *_anywhere_problems(body, blocked_names),
    ]


def main(argv: Sequence[str]) -> int:
    if len(argv) > 1:
        body = Path(argv[1]).read_text(encoding="utf-8")
    else:
        body = sys.stdin.buffer.read().decode("utf-8")
    found = problems(
        body,
        os.environ.get("BLOCKED_NAMES", "").split(","),
        os.environ.get("BLOCKED_TERMS", "").split(","),
    )
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
