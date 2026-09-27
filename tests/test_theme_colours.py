"""STORY-1003: every colour the app shows comes from the active theme, so
switching themes never leaves text unreadable. Markup and CSS use the
theme's variables ($text-error, $text-success, $text-muted, ...); named and
hex colours appear only in themes.py, where the palettes are defined."""

import re
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent.parent / "ars_magica_manager"

_NAMED = (
    r"red|green|blue|cyan|magenta|yellow|white|black|orange|purple|pink"
    r"|gr[ae]y\d*|bright_\w+|dark_\w+|light_\w+"
)
#: A named colour inside a markup tag: [red], [bold green], [on blue], [/cyan].
_MARKUP_COLOUR = re.compile(rf"\[/?(?:[a-z]+ )*(?:on )?(?:{_NAMED})\b[^\]]*\]")
#: A named colour as a CSS value: `color: red;`, `background: dark_blue`.
_CSS_COLOUR = re.compile(rf"\b(?:color|background|tint)\s*:\s*(?:{_NAMED})\b")
#: A hex or rgb() colour anywhere.
_LITERAL_COLOUR = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|\brgba?\(")


def _offences(pattern: re.Pattern[str]) -> list[str]:
    found = []
    for path in sorted(PACKAGE.rglob("*.py")):
        if path.name == "themes.py":
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if pattern.search(line):
                found.append(f"{path.relative_to(PACKAGE)}:{number}: {line.strip()}")
    return found


def test_markup_uses_no_named_colours():
    assert _offences(_MARKUP_COLOUR) == []


def test_css_uses_no_named_colours():
    assert _offences(_CSS_COLOUR) == []


def test_hex_and_rgb_colours_live_only_in_themes():
    assert _offences(_LITERAL_COLOUR) == []


def test_the_guard_patterns_catch_what_they_should():
    """The patterns above are only useful if they match the old style."""
    assert _MARKUP_COLOUR.search("[red]x[/]")
    assert _MARKUP_COLOUR.search("[bold green]x[/]")
    assert _MARKUP_COLOUR.search("[/cyan]")
    assert not _MARKUP_COLOUR.search("[$text-error]x[/]")
    assert not _MARKUP_COLOUR.search("[b]x[/b] [dim]y[/]")
    assert _CSS_COLOUR.search("color: red;")
    assert not _CSS_COLOUR.search("color: $text-muted;")
    assert _LITERAL_COLOUR.search('fill="#8B0000"')
