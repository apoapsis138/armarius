"""STORY-1003: every colour the app shows comes from the active theme, so
switching themes never leaves text unreadable. Markup and CSS use the
theme's variables ($text-error, $text-success, $text-muted, ...); named and
hex colours appear only in themes.py, where the palettes are defined."""

import re
from pathlib import Path

from rich.color import ANSI_COLOR_NAMES
from textual.color import Color, ColorParseError

PACKAGE = Path(__file__).resolve().parent.parent / "ars_magica_manager"

#: A markup tag: [red], [bold green], [on blue], [/cyan] -- not an escaped
#: "\[" and not a nested bracket.
_TAG = re.compile(r"(?<!\\)\[/?([^\[\]\n]+)\]")
#: A CSS property value: `color: red;`, `background: dodgerblue`.
_CSS_VALUE = re.compile(r"\b(?:color|background|tint|border[a-z-]*)\s*:\s*([^;\n]+)")
#: A hex or rgb() colour anywhere.
_LITERAL_COLOUR = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|\brgba?\(")


def _is_colour(word: str) -> bool:
    """A fixed colour: anything Textual or Rich reads as one (red,
    dodgerblue, bright_red...) -- never a $theme variable, nor
    `transparent` (no colour at all)."""
    word = word.strip().lower()
    if not word or word.startswith("$") or word == "transparent":
        return False
    if word in ANSI_COLOR_NAMES:
        return True
    try:
        Color.parse(word)
    except ColorParseError:
        return False
    return True


def _names_a_colour(text: str) -> bool:
    return any(_is_colour(word) for word in re.split(r"[\s,]+", text))


def _source_lines():
    for path in sorted(PACKAGE.rglob("*.py")):
        if path.name == "themes.py":
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            yield f"{path.relative_to(PACKAGE)}:{number}: {line.strip()}", line


def test_markup_uses_no_named_colours():
    offences = [
        where
        for where, line in _source_lines()
        if any(_names_a_colour(tag) for tag in _TAG.findall(line))
    ]
    assert offences == []


def test_css_uses_no_named_colours():
    offences = [
        where
        for where, line in _source_lines()
        if any(_names_a_colour(value) for value in _CSS_VALUE.findall(line))
    ]
    assert offences == []


def test_hex_and_rgb_colours_live_only_in_themes():
    offences = [
        where for where, line in _source_lines() if _LITERAL_COLOUR.search(line)
    ]
    assert offences == []


def test_the_guard_catches_what_it_should():
    """The checks above are only useful if they catch the old style."""
    for tag in ("red", "bold green", "on blue", "dodgerblue", "b bright_red"):
        assert _names_a_colour(tag), tag
    for tag in ("$text-error", "b", "dim", "bold $text-success", "{colour}", "Vault"):
        assert not _names_a_colour(tag), tag
    assert _TAG.findall("[/cyan]") == ["cyan"]
    assert _TAG.findall(r"\[Tower] Lab") == []
    assert _names_a_colour(_CSS_VALUE.findall("color: red;")[0])
    assert not _names_a_colour(_CSS_VALUE.findall("color: $text-muted;")[0])
    assert not _names_a_colour(_CSS_VALUE.findall("border: round $accent;")[0])
    assert _LITERAL_COLOUR.search('fill="#8B0000"')
