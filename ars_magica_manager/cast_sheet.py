"""The cast at a glance: one line of figures for each character of a
Session's or a chapter's cast, for the storyguide's side of the table:
Initiative, Attack and Defence with their readiest weapon (bare hands if
none), Soak, Magic Resistance (a magus with Parma Magica, against his
weakest Form), Wounds, Fatigue and Confidence, then each one's
Personality Traits and chosen spells (those mastered, and those marked
Favourite on Known Spells).

print_layout.cast_document lays it out for paper in the Scriptorum style;
`text` is the same for a window.

Pattern: Composite, as rules.fight.Unit treats a group of fighters as
one: the cast is read as one whole, each member answering the same
questions."""

from __future__ import annotations

from dataclasses import dataclass

from . import catalog, sessions
from .arts import FORMS
from .markup import escape
from .models import Character, Saga
from .rules import combat, derived, penetration, study
from .rules.fight import bare_hands

#: The figures' column titles, in order.
COLUMNS = ("Init", "Atk", "Dfn", "Soak", "MR", "Wounds", "Fatigue", "Conf")


@dataclass(frozen=True)
class CastRow:
    """One of the cast: their name and weapon, the figures in COLUMNS'
    order, their traits and chosen spells (plain text)."""

    name: str
    weapon: str
    figures: tuple[str, ...]
    traits: str
    spells: str


def _signed(n: int) -> str:
    return f"{n:+d}"


def _weapon(character: Character) -> tuple[str, combat.CombatTotals]:
    weapons = [i for i in character.inventory if i.kind == "weapon"]
    weapon = weapons[0] if weapons else bare_hands()
    return weapon.name, combat.combat_totals(character, weapon)


def _resistance(character: Character) -> str:
    if not study.has_parma(character):
        return "-"
    worst = min(
        int(penetration.magic_resistance(character, form.title()).total)
        for form in FORMS
    )
    return str(worst)


def _wounds(character: Character) -> str:
    w = character.wounds
    if w.dead:
        return "Dead"
    if w.incapacitated:
        return "Incapacitated"
    penalty = derived.wound_penalty(w, character.virtues_flaws)
    return _signed(penalty) if penalty else "Unhurt"


def chosen_spells(saga: Saga, character: Character) -> list[str]:
    """The spells the cast sheet shows: mastered, or marked Favourite."""
    found = []
    for known in character.spells_known:
        if known.mastery_score <= 0 and not known.favourite:
            continue
        spell = catalog.find_spell(saga, known.spell_id)
        name = spell.name if spell is not None else known.spell_id
        if known.mastery_score > 0:
            name += f" (Mastery {known.mastery_score})"
        found.append(name)
    return found


def row(saga: Saga, character: Character) -> CastRow:
    weapon, totals = _weapon(character)
    attack = "-" if totals.attack is None else _signed(int(totals.attack.total))
    confidence = character.background
    return CastRow(
        character.name,
        weapon,
        (
            _signed(int(totals.initiative.total)),
            attack,
            _signed(int(totals.defence.total)),
            _signed(int(derived.soak(character).total)),
            _resistance(character),
            _wounds(character),
            character.fatigue_level.title(),
            f"{confidence.confidence_score} ({confidence.confidence_points})",
        ),
        ", ".join(f"{t.name} {t.score:+d}" for t in character.personality_traits),
        "; ".join(chosen_spells(saga, character)),
    )


def rows(saga: Saga, cast: list[Character]) -> list[CastRow]:
    return [row(saga, c) for c in cast]


def session_cast(saga: Saga, session_id: str | None = None) -> list[Character]:
    """Who plays at a Session (the next planned one by default, else the
    last played), in the order cast."""
    session = next((s for s in saga.sessions if s.id == session_id), None)
    session = session or sessions.next_planned(saga) or sessions.last_played(saga)
    if session is None:
        return []
    found = (saga.character(c.character_id) for c in session.castings)
    return [c for c in found if c is not None]


def text(saga: Saga, cast: list[Character]) -> str:
    """The cast at a glance for a window (markup)."""
    if not cast:
        return "No one is cast yet: who played whom is set on the Session."
    lines = []
    for found in rows(saga, cast):
        figures = ", ".join(f"{t} {v}" for t, v in zip(COLUMNS, found.figures))
        lines.append(f"[b]{escape(found.name)}[/] ({escape(found.weapon)}): {figures}")
        if found.traits:
            lines.append(f"  Traits: {escape(found.traits)}")
        if found.spells:
            lines.append(f"  Spells: {escape(found.spells)}")
    return "\n".join(lines)
