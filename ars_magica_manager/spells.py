"""Logic behind spells -- no UI in here.

Where a spell id resolves to (the shared catalog, the saga's own spells, a
magus's invented spells), the figures worked out from a spell (magnitude, the
"CrIg 20" shorthand, a Ritual's vis cost and casting time), and reading the
Range/Duration/Target notation the rulebook and the Grand Grimoire use.
"""

from __future__ import annotations

import math
import re

from . import catalog
from .models import (
    ART_ABBREVIATIONS,
    FORMS,
    SPELL_DURATIONS,
    SPELL_RANGES,
    SPELL_TARGETS,
    TECHNIQUES,
    Saga,
    Spell,
)

# ------------------------------------------------------------ where they live


def find_spell(saga: Saga, spell_id: str | None) -> Spell | None:
    """The spell with this id, wherever it lives: the shared catalog, then the
    saga's own spells, then any magus's invented spells."""
    if not spell_id:
        return None
    found = catalog.load_spell_catalog_by_id().get(spell_id)
    if found is not None:
        return found
    for spell in saga.spells:
        if spell.id == spell_id:
            return spell
    for character in saga.characters:
        for spell in character.invented_spells:
            if spell.id == spell_id:
                return spell
    return None


def all_spell_ids(saga: Saga) -> set[str]:
    """Every spell id in use, for generating a new unique one."""
    ids = set(catalog.load_spell_catalog_by_id())
    ids.update(s.id for s in saga.spells)
    ids.update(s.id for c in saga.characters for s in c.invented_spells)
    return ids


# ------------------------------------------------------------------ figures


def is_general(spell: Spell) -> bool:
    """A General-level spell has no fixed level; it's cast at any level."""
    return spell.level is None


def magnitude(spell: Spell) -> int | None:
    """Level / 5, rounded up (levels 1-5 are magnitude 1); None for a General
    spell, whose magnitude depends on the level it's cast at."""
    if spell.level is None:
        return None
    return max(1, math.ceil(spell.level / 5))


def shorthand(spell: Spell) -> str:
    """Standard Hermetic notation: "CrIg 20", "Mu(Re)Te 15", "ReCo(Me) 10",
    "ReVi Gen". A requisite Technique follows the Technique and a requisite
    Form follows the Form."""

    def abbr(art: str) -> str:
        return ART_ABBREVIATIONS.get(art, art[:2])

    technique_reqs = [r for r in spell.requisites if r in TECHNIQUES]
    form_reqs = [r for r in spell.requisites if r not in TECHNIQUES]

    def reqs(arts: list[str]) -> str:
        return f"({'/'.join(abbr(a) for a in arts)})" if arts else ""

    arts = (
        f"{abbr(spell.technique)}{reqs(technique_reqs)}"
        f"{abbr(spell.form)}{reqs(form_reqs)}"
    )
    return f"{arts} {'Gen' if spell.level is None else spell.level}"


def vis_cost(spell: Spell) -> int | None:
    """Pawns of vis a Ritual needs: one per magnitude (0 for a Formulaic
    spell; None for a General Ritual, which depends on the level cast)."""
    if not spell.ritual:
        return 0
    return magnitude(spell)


def casting_time(spell: Spell) -> str:
    """A Formulaic spell takes a round; a Ritual 15 minutes per magnitude."""
    if not spell.ritual:
        return "1 round"
    mag = magnitude(spell)
    if mag is None:
        return "15 minutes per magnitude"
    return f"{mag * 15} minutes"


# ------------------------------------------------- Range / Duration / Target

#: Abbreviations and variant spellings used by the rulebook and the Grand
#: Grimoire, mapped to the standard names (lower case keys).
_RANGE_NAMES = {r.lower(): r for r in SPELL_RANGES} | {
    "per": "Personal",
    "pers": "Personal",
    "arc": "Arcane Connection",
    "arcane": "Arcane Connection",
    "arcane connection": "Arcane Connection",
}
_DURATION_NAMES = {d.lower(): d for d in SPELL_DURATIONS} | {
    "mom": "Momentary",
    "conc": "Concentration",
    "diam": "Diameter",
    "spec": "Special",
    "special": "Special",
}
_TARGET_NAMES = {t.lower(): t for t in SPELL_TARGETS} | {
    "ind": "Individual",
    "indiv": "Individual",
    "bound": "Boundary",
    "str": "Structure",
    "spec": "Special",
    "special": "Special",
}


def _normalise(value: str, names: dict[str, str]) -> str:
    cleaned = value.strip().strip(".").strip()
    return names.get(cleaned.lower(), cleaned)


def normalise_range(value: str) -> str:
    return _normalise(value, _RANGE_NAMES)


def normalise_duration(value: str) -> str:
    return _normalise(value, _DURATION_NAMES)


def normalise_target(value: str) -> str:
    return _normalise(value, _TARGET_NAMES)


_ART_NAMES = {a.lower(): a for a in (*TECHNIQUES, *FORMS)} | {
    abbr.lower(): art for art, abbr in ART_ABBREVIATIONS.items()
}


def parse_requisites(text: str) -> list[str]:
    """The Arts named in a requisites list ("Rego", "Perdo, Corpus", "Au/Im"),
    in order; anything that isn't an Art is ignored."""
    found = []
    for token in re.split(r"[,;/&]|\band\b|\s+", text):
        art = _ART_NAMES.get(token.strip().strip(".").lower())
        if art and art not in found:
            found.append(art)
    return found


_RDT = re.compile(r"^\s*R:\s*(?P<r>[^,]+),\s*D:\s*(?P<d>[^,]+),\s*T:\s*(?P<rest>.+)$")
_REQUISITE = re.compile(r"\bReq(?:uisites?)?\s*:\s*(?P<arts>.*)$", re.IGNORECASE)


def parse_rdt(line: str) -> dict | None:
    """Read an "R: Voice, D: Mom, T: Ind, Ritual; Req: Rego" line into range,
    duration, target, ritual and requisites; None if it isn't one."""
    match = _RDT.match(line)
    if match is None:
        return None
    rest = match.group("rest")
    requisites: list[str] = []
    req = _REQUISITE.search(rest)
    if req is not None:
        requisites = parse_requisites(req.group("arts"))
        rest = rest[: req.start()]
    ritual = bool(re.search(r"\bRitual\b", rest, re.IGNORECASE))
    rest = re.sub(r"\bRitual\b", "", rest, flags=re.IGNORECASE)
    target = re.split(r"[,;]", rest)[0]
    return {
        "range": normalise_range(match.group("r")),
        "duration": normalise_duration(match.group("d")),
        "target": normalise_target(target),
        "ritual": ritual,
        "requisites": requisites,
    }
