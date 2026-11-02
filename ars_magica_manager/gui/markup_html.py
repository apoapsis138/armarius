"""The app's text markup as Qt rich text (HTML).

The shared core writes its text in a small markup (markup.py): [b] bold,
[i] italic, [s] struck through, [dim], a theme colour such as [$label] or
[$text-error], or several at once ([i $label]), each closed by [/], [/b],
[/i] or [/s]; "\\[" is a literal bracket. This turns that into the HTML
subset a QLabel shows, taking the colours from the palette. A bulleted or
numbered line (markup.LIST_LINE) hangs: its wrapped lines start under its
words, not under the bullet.
"""

from __future__ import annotations

import html
import re

from ..markup import BULLET, LIST_LINE
from .themes import Palette

_TAG = re.compile(r"(?<!\\)\[(/?)([^\[\]\n]*)\]")


def _open(spec: str, palette: Palette) -> tuple[str, str]:
    """The HTML opening and closing tags for one markup tag's styles."""
    styles: list[str] = []
    for word in spec.split():
        if word == "b":
            # 700, not 600: rich text sets the bundled serif, a variable
            # font, in its regular weight at 600.
            styles.append("font-weight:700")
        elif word == "i":
            styles.append("font-style:italic")
        elif word == "s":
            styles.append("text-decoration:line-through")
        elif word == "dim":
            styles.append(f"color:{palette['dim']}")
        elif word.startswith("$") and word[1:] in palette.colours:
            styles.append(f"color:{palette[word[1:]]}")
    return f'<span style="{";".join(styles)}">', "</span>"


def to_html(text: str, palette: Palette, *, pre: bool = False) -> str:
    """`text` (app markup) as HTML. Lines break where the text does;
    `pre` also keeps runs of spaces, for the core's aligned columns."""
    out: list[str] = []
    closers: list[str] = []
    position = 0
    for match in _TAG.finditer(text):
        out.append(html.escape(text[position : match.start()]))
        position = match.end()
        closing, spec = match.group(1), match.group(2)
        if closing:
            if closers:
                out.append(closers.pop())
        elif _looks_like_markup(spec):
            opener, closer = _open(spec, palette)
            out.append(opener)
            closers.append(closer)
        else:  # not markup the core writes: show it as written
            out.append(html.escape(match.group(0)))
    out.append(html.escape(text[position:]))
    out.extend(reversed(closers))
    body = "".join(out).replace("\\[", "[")
    if pre:
        return f'<div style="white-space:pre-wrap">{body}</div>'
    if any(LIST_LINE.match(plain(line)) for line in text.split("\n")):
        return _hanging(body)
    return body.replace("\n", "<br>")


#: How far each level of a nested list (two spaces before its marker)
#: sits in, in pixels.
_NEST = 22

_LEADING_TAGS = re.compile(r"^((?:<span[^>]*>)*)")


def _hanging(body: str) -> str:
    """`body` (HTML, a line per line of text) as one block per line, each
    list line a two-cell row (its bullet or number, then its words) so its
    wrapped lines line up under its words."""
    blocks: list[str] = []
    for line in body.split("\n"):
        words = _LEADING_TAGS.sub("", line, count=1)
        tags = line[: len(line) - len(words)]
        found = LIST_LINE.match(html.unescape(words))
        if found:
            depth = len(found.group(1).expandtabs(4)) // 2
            marker = found.group(2)
            rest = words[len(html.escape(found.group(0))) :]
            blocks.append(
                '<table cellspacing="0" cellpadding="0" '
                f'style="margin-left:{depth * _NEST}px"><tr>'
                f'<td width="{_marker_width(marker)}">{marker}</td>'
                f"<td>{tags}{rest}</td></tr></table>"
            )
        else:
            blocks.append(f'<p style="margin:0">{line or "&nbsp;"}</p>')
    return "".join(blocks)


def _marker_width(marker: str) -> int:
    """The width, in pixels, of a list line's bullet or number cell: one
    width for every number up to 99, so a list's words line up."""
    return 18 if marker == BULLET else 30


def _looks_like_markup(spec: str) -> bool:
    return all(
        word in ("b", "i", "s", "dim") or word.startswith("$") for word in spec.split()
    )


def plain(text: str) -> str:
    """`text` without its markup, for a list row."""
    return _TAG.sub("", text).replace("\\[", "[")


def struck(text: str) -> bool:
    """Whether a table cell's markup strikes its words through."""
    return any(
        not match.group(1)
        and _looks_like_markup(match.group(2))
        and "s" in match.group(2).split()
        for match in _TAG.finditer(text)
    )


def cell_style(text: str, palette: Palette) -> tuple[str, str | None, bool, bool]:
    """A table cell's markup as its plain words, and the colour (None: the
    table's own), boldness and italics its tags ask for anywhere in it: a
    cell is drawn in one style."""
    colour, bold, italic = None, False, False
    for match in _TAG.finditer(text):
        if match.group(1) or not _looks_like_markup(match.group(2)):
            continue
        for word in match.group(2).split():
            if word == "b":
                bold = True
            elif word == "i":
                italic = True
            elif word == "dim":
                colour = colour or palette["dim"]
            elif word.startswith("$") and word[1:] in palette.colours:
                colour = colour or palette[word[1:]]
    return plain(text), colour, bold, italic
