"""Boost a Spell (More on Known Spells): a calculator for Boosted Magic
and Mutantum boosting. Choose a known spell the magus may boost, the
Range, Duration and Target it is raised to and how much larger it is; the
inspector gives the pawns of vis (one a magnitude), the botch dice they
add, and what stops it (DE pp. 72-73; Houses of Hermes: True Lineages pp.
101-103; Errata pp. 45-46). It changes nothing: the casting is at the
table, at the spell's own level."""

from __future__ import annotations

from typing import Any

from .. import catalog
from ..commands import Form, Refuse
from ..form_spec import DialogField
from ..markup import escape, problem
from ..models import Character, Saga, Spell
from ..rules import casting, house_magic, spell_levels

TITLE = "Boost a Spell"
#: Boost a Spell's own help page.
HELP_ID = "boost-spell"


def boostable(saga: Saga, magus: Character) -> list[Spell]:
    """The known spells the magus may boost."""
    found: list[Spell] = []
    for known in magus.spells_known:
        spell = catalog.find_spell(saga, known.spell_id)
        mastery = casting.mastery_counts(known.mastery_abilities)
        if spell is not None and house_magic.can_boost(magus, spell, mastery):
            found.append(spell)
    return found


def _options(steps: dict[str, int], now: str) -> list[tuple[str, str]]:
    """The parameters no lower than the spell's own, cheapest first."""
    floor = steps.get(now, 0)
    return [
        (name, name)
        for name, n in sorted(steps.items(), key=lambda x: x[1])
        if n >= floor
    ]


def fields(saga: Saga, magus: Character) -> list[DialogField]:
    spells = boostable(saga, magus)
    first = spells[0] if spells else None
    return [
        DialogField(
            "spell",
            "Spell",
            "select",
            first.id if first else None,
            options=[(f"{escape(s.name)} ({s.level})", s.id) for s in spells],
        ),
        DialogField(
            "range",
            "Range",
            "select",
            first.range if first else None,
            options=_options(spell_levels.RANGE_STEPS, ""),
        ),
        DialogField(
            "duration",
            "Duration",
            "select",
            first.duration if first else None,
            options=_options(spell_levels.DURATION_STEPS, ""),
        ),
        DialogField(
            "target",
            "Target",
            "select",
            first.target if first else None,
            options=_options(spell_levels.TARGET_STEPS, ""),
        ),
        DialogField(
            "size",
            "Larger by",
            "int",
            0,
            hint="Steps of size: a magnitude each, as the Target's size table.",
        ),
    ]


def live(saga: Saga, values: dict[str, Any]) -> str:
    spell = catalog.find_spell(saga, values.get("spell"))
    if spell is None:
        return "[dim]Choose the spell.[/]"
    found = house_magic.boost(
        spell,
        range_=values.get("range") or None,
        duration=values.get("duration") or None,
        target=values.get("target") or None,
        size=values.get("size") or 0,
    )
    lines = [
        f"[b]{escape(spell.name)}[/] [i]({escape(spell.range)}, "
        f"{escape(spell.duration)}, {escape(spell.target)}): cast, tiring and "
        f"penetrating at its own level, {spell.level} (DE p. 73).[/]",
        f"[$label]Pawns of vis[/] {found.pawns}  ·  "
        f"[$label]Botch dice[/] +{found.botch_dice}",
    ]
    lines += [problem(escape(p)) for p in found.problems]
    return "\n".join(lines)


def boost_form(saga: Saga, magus: Character) -> Form | Refuse:
    if not boostable(saga, magus):
        return Refuse(
            TITLE,
            f"{escape(magus.name)} knows no spell he may boost: that needs "
            "Boosted Magic (any Formulaic spell, DE p. 72), Boosted or "
            "Mutantum Magic for a Boosted spell, or Boosted Casting.",
        )
    return Form(
        f"{TITLE}: {escape(magus.name)}",
        lambda: fields(saga, magus),
        lambda _values: None,
        live=lambda values: live(saga, values),
        save_label="Done",
        cancel_label="Close",
        help_id=HELP_ID,
        inspector="The Boost",
    )
