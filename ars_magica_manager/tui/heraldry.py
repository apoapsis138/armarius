"""Arms in the terminal: the shield drawn in half-blocks, two square
pixels a character (the upper one the character's colour, the lower its
background), from the shield's pixels (arms.pixels)."""

from __future__ import annotations

import re
import textwrap

from ..arms import Arms, pixels
from .themes import TINCTURES

#: How many pixels wide the shield is drawn: 18 columns by 11 lines.
WIDTH = 18


def _cell(top: str | None, bottom: str | None) -> str:
    if top is None and bottom is None:
        return " "
    if top is None:
        return f"[{TINCTURES[bottom]}]▄[/]" if bottom else " "
    if bottom is None:
        return f"[{TINCTURES[top]}]▀[/]"
    return f"[{TINCTURES[top]} on {TINCTURES[bottom]}]▀[/]"


def half_blocks(arms: Arms, width: int = WIDTH) -> list[str]:
    """The shield as markup lines, `width` characters wide."""
    grid = pixels(arms, width)
    if len(grid) % 2:
        grid.append([None] * width)
    return [
        "".join(_cell(top, bottom) for top, bottom in zip(grid[r], grid[r + 1]))
        for r in range(0, len(grid), 2)
    ]


#: A line wholly in one style: "[b]words[/]".
_STYLED = re.compile(r"^(\[[^\]]+\])(.*)\[/\]$")


def _wrapped(line: str, width: int) -> list[str]:
    """A markup line cut to `width`, each piece keeping the line's style
    when the whole line has one."""
    styled = _STYLED.match(line)
    style, words = (styled.group(1), styled.group(2)) if styled else ("", line)
    pieces = textwrap.wrap(words, width) or [""]
    return [f"{style}{piece}[/]" if style else piece for piece in pieces]


def beside(arms: Arms | None, text: str, gap: int = 3, width: int = 44) -> str:
    """The shield with `text` (markup lines, cut to `width`) beside it,
    from its second line; `text` alone with no arms."""
    if arms is None:
        return text
    shield = half_blocks(arms)
    words = [piece for line in text.split("\n") for piece in _wrapped(line, width)]
    lines = []
    for i, row in enumerate(shield):
        said = words[i - 1] if 1 <= i <= len(words) else ""
        lines.append(f"{row}{' ' * gap}{said}" if said else row)
    lines.extend(words[len(shield) - 1 :])
    return "\n".join(lines)
