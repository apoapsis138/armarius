"""The one lookup every total uses (DESIGN.md section 5.1): collect every
Modifier of a type from the Virtues, Flaws, Boons and Hooks attached to the
records involved, then combine them with a base figure.

Each attached *instance* counts, so a repeatable entry taken twice applies
twice. An entry's effect is data on the catalog entry (`modifiers`); nothing
here looks an entry up by name or id to decide what it does.

How flat amounts and multipliers stack (settled in STORY-804): every flat
amount is added to the base first, then each multiplier multiplies that sum,
several multipliers multiplying together. This follows the Definitive
Edition's advancement pipeline, where the xp gained is the Advancement Total
(with its flat bonuses) "then modified by e.g. Affinity" (rules reference
section 10, Advancement Total and xp pipeline). Rounding a multiplied total
is left to the rule that owns it (Affinity rounds up; the default is down).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

from ..models import Modifier, VirtueFlawInstance
from .breakdown import Breakdown, Line


class _Entry(Protocol):
    """What a catalog entry needs for its effects to be collected: every
    catalog (character, laboratory, covenant) has these."""

    id: str
    name: str
    type: str
    modifiers: list[Modifier]


@dataclass(frozen=True)
class EffectSource:
    """One record's attached entries: its instances and the catalog they
    come from. `kind` names the record ("character", "laboratory",
    "covenant") for the breakdown."""

    kind: str
    instances: Sequence[VirtueFlawInstance]
    catalog: Mapping[str, Any]


@dataclass(frozen=True)
class Effect:
    """One modifier from one attached instance, with its target resolved
    from the instance's parameters ("{art}" -> "creo")."""

    kind: str
    entry: _Entry
    instance: VirtueFlawInstance
    modifier: Modifier
    target: str | None

    @property
    def is_negative_side(self) -> bool:
        """True for a Flaw, Inferiority or Hook (the entry's costly side)."""
        return self.entry.type in ("Flaw", "Inferiority", "Hook")


_PLACEHOLDER = re.compile(r"\{(\w+)\}")


def resolve_target(target: str | None, params: Mapping[str, str]) -> str | None:
    """A modifier's target with any "{param}" filled in from the instance's
    parameters; a placeholder the instance doesn't fill stays as written."""
    if target is None:
        return None
    return _PLACEHOLDER.sub(lambda m: params.get(m.group(1), m.group(0)), target)


def _same(a: str, b: str) -> bool:
    return a.strip().casefold() == b.strip().casefold()


def collect(
    sources: Iterable[EffectSource],
    applies_to: str,
    *,
    activity: str | None = None,
    target: str | None = None,
) -> list[Effect]:
    """Every modifier of type `applies_to` on the sources' attached
    instances, one per instance (effects of a repeated entry stack).

    Given an `activity`, modifiers for that activity and general ones (no
    activity) both count. Given a `target`, modifiers whose resolved target
    matches it (ignoring case) and untargeted ones both count. Without an
    `activity` or `target`, every modifier of the type counts."""
    found: list[Effect] = []
    for source in sources:
        for instance in source.instances:
            entry = source.catalog.get(instance.vf_id)
            if entry is None:
                continue
            for modifier in entry.modifiers:
                if modifier.applies_to != applies_to:
                    continue
                if activity is not None and modifier.activity not in (None, activity):
                    continue
                resolved = resolve_target(modifier.target, instance.params)
                if (
                    target is not None
                    and resolved is not None
                    and not _same(resolved, target)
                ):
                    continue
                found.append(Effect(source.kind, entry, instance, modifier, resolved))
    return found


def amount_total(effects: Iterable[Effect]) -> float:
    """The sum of the effects' flat amounts."""
    return sum(effect.modifier.amount or 0 for effect in effects)


def combine(
    base: float,
    effects: Iterable[Effect],
    *,
    base_label: str = "Base",
    base_source: str = "",
    rounding: Callable[[float], int] | None = None,
) -> Breakdown:
    """`base` with the effects applied: flat amounts added first, then the
    multipliers (see the module docstring), with a line for each term.
    `rounding` is applied to the result when the owning rule says how."""
    effects = list(effects)
    lines = [Line(base_label, amount=base, source=base_source)]
    total = base
    for effect in effects:
        if effect.modifier.amount is not None:
            total += effect.modifier.amount
            lines.append(
                Line(
                    effect.entry.name, amount=effect.modifier.amount, source=effect.kind
                )
            )
    for effect in effects:
        if effect.modifier.multiplier is not None:
            total *= effect.modifier.multiplier
            lines.append(
                Line(
                    effect.entry.name,
                    multiplier=effect.modifier.multiplier,
                    source=effect.kind,
                )
            )
    if rounding is not None:
        total = rounding(total)
    return Breakdown(total=total, lines=lines)
