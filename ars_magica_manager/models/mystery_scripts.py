"""A Mystery Initiation Script written out as its components (The
Mysteries Revised Edition pp. 15-16): what an Initiation plan lists."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .common import known_fields


@dataclass
class ScriptPart:
    """One component of an Initiation's Script: its key in the components
    table (rules.mysteries.COMPONENTS, or a House's own), its size for one
    the troupe sizes (a great sacrifice +3 to +6, sympathy -5 to +5; the
    table's own bonus counts for the rest) and what it is ("the head of the
    Minotaur")."""

    key: str
    bonus: int = 0
    note: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScriptPart:
        d = known_fields(cls, data)
        bonus = d.get("bonus") or 0
        if isinstance(bonus, bool) or not isinstance(bonus, (int, str)):
            raise ValueError(f"A Script component's bonus {bonus!r} isn't a number.")
        try:
            d["bonus"] = int(bonus)
        except ValueError:
            raise ValueError(
                f"A Script component's bonus {bonus!r} isn't a whole number."
            ) from None
        d["key"] = str(d.get("key") or "")
        d["note"] = str(d.get("note") or "")
        return cls(**d)
