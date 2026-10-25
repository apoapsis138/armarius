"""The Ranges, Durations and Targets a magus may give a spell they invent.

Every magus has the standard ones. Beyond them, each parameter has to be
opened to the magus by something (reference/spell-parameters.md):

- a Virtue or Mystery that grants it (spell_levels.EXTRA_PARAMETERS);
- a research goal they reached that grants it ("Parameter": "Range:
  Horizon (as Sight)", or the name of one the app knows);
- a spell they know that uses one no Virtue is needed for: a Minor
  Breakthrough's parameter is learned with the Lab Text of a spell that
  uses it (True Lineages, Breakthroughs in Play).

The saga's optional rule "any_spell_parameter" puts Other... back in the
Invent Spell form: any parameter, its magnitudes typed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from . import catalog
from .models import Character, Saga
from .rules import options, spell_levels
from .rules.spell_levels import ExtraParameter

KINDS: tuple[str, ...] = ("range", "duration", "target")

_STANDARD = {
    "range": spell_levels.RANGE_STEPS,
    "duration": spell_levels.DURATION_STEPS,
    "target": spell_levels.TARGET_STEPS,
}

_GRANT = re.compile(
    r"^\s*(?P<kind>range|duration|target)\s*:\s*(?P<name>.+?)"
    r"(?:\s*\(\s*as\s+(?P<as>[^)+]+?)\s*(?:\+\s*(?P<plus>\d+))?\s*\))?\s*$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Opened:
    """An extra parameter open to a magus, and what opened it."""

    parameter: ExtraParameter
    why: str

    @property
    def steps(self) -> int:
        return _STANDARD[self.parameter.kind][self.parameter.costs_as] + (
            self.parameter.plus
        )


def parse_grant(text: str) -> list[ExtraParameter]:
    """The parameters a research goal's grant names: "Kind: Name", a
    parameter the app knows (or a family of them: "Duration: Event"), or
    one of the troupe's own with what it costs as ("Range: Horizon (as
    Sight)", "+n" for more). Nothing when it names neither."""
    found = _GRANT.match(text or "")
    if found is None:
        return []
    kind = found["kind"].lower()
    name = found["name"].strip()
    known = [
        e
        for e in spell_levels.EXTRA_PARAMETERS
        if e.kind == kind and name.lower() in (e.name.lower(), e.family.lower())
    ]
    if known:
        return known
    costs_as = next(
        (s for s in _STANDARD[kind] if s.lower() == (found["as"] or "").lower()),
        None,
    )
    if costs_as is None or name in _STANDARD[kind]:
        return []
    return [ExtraParameter(kind, name, costs_as, (), plus=int(found["plus"] or 0))]


def _known_spells(saga: Saga, magus: Character):
    for known in magus.spells_known:
        spell = catalog.find_spell(saga, known.spell_id)
        if spell is not None:
            yield spell
    yield from magus.invented_spells


def opened(saga: Saga, magus: Character) -> list[Opened]:
    """Every extra parameter open to the magus, the first reason found for
    each."""
    vf_ids = spell_levels.opening_ids(
        {vf.vf_id for vf in magus.virtues_flaws},
        learned_road=magus.hermetic.road_magic,
    )
    found: dict[tuple[str, str], Opened] = {}

    def add(parameter: ExtraParameter, why: str) -> None:
        found.setdefault((parameter.kind, parameter.name), Opened(parameter, why))

    for e in spell_levels.EXTRA_PARAMETERS:
        if any(v in vf_ids for v in e.granted_by):
            add(e, "a Virtue")
    for goal in magus.breakthroughs:
        if goal.reached and goal.grant_kind == "Parameter":
            for e in parse_grant(goal.grant):
                add(e, f"the breakthrough {goal.name}")
    for spell in _known_spells(saga, magus):
        for kind in KINDS:
            e = spell_levels.extra(kind, getattr(spell, kind))
            if e is not None and not e.granted_by:
                add(e, f"the spell {spell.name}")
    return list(found.values())


def available(saga: Saga, magus: Character, kind: str) -> list[Opened]:
    """The extra `kind` parameters open to the magus."""
    return [o for o in opened(saga, magus) if o.parameter.kind == kind]


def any_allowed(saga: Saga) -> bool:
    """Whether the troupe lets a spell have any parameter (Other...)."""
    return options.is_on(saga, options.ANY_SPELL_PARAMETER)
