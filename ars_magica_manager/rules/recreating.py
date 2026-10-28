"""Recreating a flawed creation (Ars Magica Definitive Edition, Chapter 8:
Laboratory, Arcane Experimentation, p. 274; Errata p. 6).

A creation an experiment left flawed or hard to use may be lived with or
recreated by the normal laboratory rules, in another season and with no
need to experiment again. The magus's Magic Theory score at the time of the
experiment is added to the Lab Total, so Magic Theory counts twice.

- Spells and item effects: the recreation is a new creation. A flawed item
  effect stays in its device and keeps its space (pp. 274-275); a flawed
  Arcane Discovery item's vis is lost (p. 279). Both versions of a spell
  stay known, since a magus "may accumulate many usable versions of the
  same spell" (p. 279); Advance Season offers to retire the flawed one.
- A Longevity Ritual: a second ritual overrides the flawed one, taking
  another season (p. 275). That paragraph is silent on the bonus; the p. 274
  rule covers any creation the chart flawed, so it applies.

The player decides whether a creation is flawed: any creation of the
magus's own carrying an experimental effect may be chosen, its chart
results shown beside it. A record is only kept for a side effect, a
modified effect or a creation changed, never for no extraordinary effects
or a Discovery.

The rules don't say whose season counts for an experiment over several
seasons: the app takes the last, and the recreation must come after it.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..models import Character, ExperimentalEffect, Saga, SeasonPlan
from ..models.seasons import season_order
from . import enchant_seasons as es
from . import enchantment, lab_seasons

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Arcane "
    "Experimentation, Extraordinary Results, p. 274"
)
VIS_LOST = (
    "A flawed item from Arcane Discovery loses all the vis used in its first "
    "experiment (Ars Magica Definitive Edition, Arcane Discovery, p. 279); "
    "the recreation pays vis as usual."
)

SPELL, EFFECT, LONGEVITY = "spell", "effect", "longevity"
#: The lab work that recreates each kind of creation.
KIND_OF: dict[str, str] = {
    lab_seasons.INVENT: SPELL,
    es.INSTIL: EFFECT,
    es.LESSER_WORK: EFFECT,
    es.CHARGED_WORK: EFFECT,
    lab_seasons.LONGEVITY: LONGEVITY,
}


@dataclass(frozen=True)
class Flawed:
    """A creation of the magus's that an experiment changed: `key` is
    "<kind>:<id>" (a spell's or an effect's id, a Longevity Ritual's
    subject), `theory` the Magic Theory of its last experimental season
    (None when the record is from before the app kept it)."""

    key: str
    kind: str
    name: str
    results: tuple[str, ...]
    year: int
    season: str
    theory: int | None

    @property
    def label(self) -> str:
        """ "Ward of Iron: Side effect: major flaw (Magic Theory 5, Summer
        1220)"."""
        then = (
            f"Magic Theory {self.theory}"
            if self.theory is not None
            else ("Magic Theory not recorded")
        )
        results = "; ".join(r for r in self.results if r) or "experimental effect"
        return f"{self.name}: {results} ({then}, {self.season} {self.year})"


def _last(effects: Sequence[ExperimentalEffect]) -> ExperimentalEffect | None:
    """The record of the latest season among `effects` (records with no
    season count as the earliest)."""
    dated = [e for e in effects if e.year is not None]
    if not dated:
        return effects[-1] if effects else None
    return max(dated, key=lambda e: season_order(season=e.season, year=e.year or 0))


def _flawed(
    key: str, kind: str, name: str, effects: Sequence[ExperimentalEffect]
) -> Flawed | None:
    last = _last(effects)
    if last is None:
        return None
    return Flawed(
        key=key,
        kind=kind,
        name=name,
        results=tuple(e.label for e in effects),
        year=last.year or 0,
        season=last.season,
        theory=last.magic_theory,
    )


def flawed_creations(saga: Saga, magus: Character, kind: str) -> list[Flawed]:
    """The magus's own creations of `kind` an experiment changed."""
    found: list[Flawed | None] = []
    if kind == SPELL:
        known = {k.spell_id for k in magus.spells_known}
        found = [
            _flawed(f"{SPELL}:{s.id}", SPELL, s.name, s.experimental_effects)
            for s in magus.invented_spells
            if s.experimental_effects and s.id in known
        ]
    elif kind == EFFECT:
        found = [
            _flawed(
                f"{EFFECT}:{e.id}",
                EFFECT,
                f"{d.name}: {enchantment.effect_name(e)}",
                e.experimental_effects,
            )
            for d in saga.enchanted_devices
            for e in d.effects
            if e.experimental_effects and e.instilled_by == magus.id
        ]
    elif kind == LONGEVITY:
        found = [
            _flawed(
                f"{LONGEVITY}:{c.id}",
                LONGEVITY,
                f"{c.name}'s Longevity Ritual",
                c.aging.longevity_effects,
            )
            for c in saga.characters
            if c.aging.longevity_effects and c.aging.longevity_by == magus.name
        ]
    return [f for f in found if f is not None]


def recreatable(
    saga: Saga, magus: Character, activity: str, year: int, season: str
) -> list[Flawed]:
    """The creations the magus may recreate with `activity` in `season`
    `year`: those whose last experimental season came before it."""
    kind = KIND_OF.get(activity)
    if kind is None:
        return []
    now = season_order(season=season, year=year)
    return [
        f
        for f in flawed_creations(saga, magus, kind)
        if season_order(season=f.season, year=f.year) < now
    ]


def find(saga: Saga, magus: Character, key: str) -> Flawed | None:
    """The magus's flawed creation `key` ("<kind>:<id>"), if it is still
    there."""
    kind = key.partition(":")[0]
    return next((f for f in flawed_creations(saga, magus, kind) if f.key == key), None)


def problem(magus: Character, plan: SeasonPlan) -> str | None:
    """Why the plan can't recreate what it names: a second Longevity Ritual
    overrides only its own subject's ritual."""
    kind, _, ident = plan.recreating.partition(":")
    if kind == LONGEVITY and ident != (plan.subject_id or magus.id):
        return "Recreate the Longevity Ritual of the ritual's subject."
    return None
