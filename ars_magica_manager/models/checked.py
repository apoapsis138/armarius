"""Checks for values read from a saved record: a whole number, one of a
few words, a piece of text. Each raises ValueError naming the record, so a
bad save is reported when it is loaded rather than when a sheet shows it.

Shared by the Hermetic Projects' records (models.hermetic_projects) and
the Menagerie's (models.menagerie), which the projects' record holds."""

from __future__ import annotations

from typing import Any


def whole(value: Any, what: str, least: int | None = 0) -> int:
    """`value` as a whole number of at least `least` (None: any)."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{what} should be a whole number, not {value!r}.")
    if least is not None and value < least:
        raise ValueError(f"{what} should be at least {least}, not {value}.")
    return value


def one_of(value: Any, allowed: tuple[str, ...], what: str) -> str:
    """`value` as one of the words `allowed`."""
    text = str(value)
    if text not in allowed:
        raise ValueError(f"{what}: {text!r} is not one of {', '.join(allowed)}.")
    return text


def text(value: Any, what: str) -> str:
    """`value` as text ("" for none)."""
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"{what} should be text, not {value!r}.")
    return value
