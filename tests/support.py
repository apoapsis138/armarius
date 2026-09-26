"""Helpers shared by several test modules (fixtures live in conftest.py)."""

import re


def strip_markup(markup: str) -> str:
    """`markup` with simple tags like [b], [dim] and [/] removed -- enough to
    check the words and column alignment of a panel's text."""
    return re.sub(r"\[/?[a-z]*\]", "", markup)
