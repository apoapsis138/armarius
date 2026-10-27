"""The Hermetic spell-guideline catalog's entries
(spell_guideline_catalog.json): a supplement's guideline, its Arts and
base level, which the spell design form offers as a base level. The rules
that read them are in rules/spell_guidelines.py."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..arts import FORMS, TECHNIQUES
from .common import known_fields


@dataclass(frozen=True)
class SpellGuidelineDef:
    """One guideline: a short name, its Technique, Form and base level
    (for Personal, Momentary, Individual unless `summary` says
    otherwise), a one-line summary, the book (a sourcebooks abbreviation)
    and printed page, the Target a spell from it must have, if any, and
    the Definitive Edition's page where it prints the same guideline. A
    General guideline (`general`) has no level of its own (0): the spell's
    level is whatever the designer gives it."""

    id: str
    name: str
    technique: str
    form: str
    summary: str
    source: str
    page: int
    level: int = 0
    target: str = ""
    de_page: int | None = None
    general: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SpellGuidelineDef:
        """An entry of the catalog file; ValueError naming the entry when
        its Arts or level aren't a guideline's."""
        d = known_fields(cls, data)
        name = d.get("id", "?")
        if d.get("technique") not in TECHNIQUES or d.get("form") not in FORMS:
            raise ValueError(f"Spell guideline {name}: not a Technique and Form.")
        general = d.get("general", False)
        if not isinstance(general, bool):
            raise ValueError(f"Spell guideline {name}: general must be true or false.")
        level = d.get("level", 0 if general else None)
        if general and level != 0:
            raise ValueError(f"Spell guideline {name}: a General one has no level.")
        if not general and (
            not isinstance(level, int) or isinstance(level, bool) or level < 1
        ):
            raise ValueError(f"Spell guideline {name}: its level must be 1 or more.")
        for key in ("id", "name", "summary", "source"):
            if not isinstance(d.get(key), str) or not d[key]:
                raise ValueError(f"Spell guideline {name}: it needs its {key}.")
        if not isinstance(d.get("target", ""), str):
            raise ValueError(f"Spell guideline {name}: its target must be a name.")
        for key in ("page", "de_page"):
            page = d.get(key)
            if (page is not None or key == "page") and (
                not isinstance(page, int) or page < 1
            ):
                raise ValueError(f"Spell guideline {name}: {key} must be a page.")
        return cls(**d)
