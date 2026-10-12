"""The app's text markup as Qt rich text (HTML).

The shared core writes its text in a small markup (markup.py): [b] bold,
[i] italic, [dim], a theme colour such as [$label] or [$text-error], or
several at once ([i $label]), each closed by [/], [/b] or [/i]; "\\[" is
a literal bracket. This turns that into the HTML subset a QLabel shows,
taking the colours from the palette.
"""

from __future__ import annotations

import html
import re

from .themes import Palette

_TAG = re.compile(r"(?<!\\)\[(/?)([^\[\]\n]*)\]")


def _open(spec: str, palette: Palette) -> tuple[str, str]:
    """The HTML opening and closing tags for one markup tag's styles."""
    styles: list[str] = []
    for word in spec.split():
        if word == "b":
            styles.append("font-weight:600")
        elif word == "i":
            styles.append("font-style:italic")
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
    return body.replace("\n", "<br>")


def _looks_like_markup(spec: str) -> bool:
    return all(
        word in ("b", "i", "dim") or word.startswith("$") for word in spec.split()
    )


def plain(text: str) -> str:
    """`text` without its markup, for a list row."""
    return _TAG.sub("", text).replace("\\[", "[")
