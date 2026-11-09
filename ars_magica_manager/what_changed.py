"""What changed: a character between two saved copies, in plain words
("Creo 12 to 13", "Magic Theory 5 to 6", "learned Pilum of Fire").

A copy (`keep`) is the character as plain data, with the books and
enchanted items it held then, taken before a change: the season just
advanced (forms/advance.py keeps one for each player character before
playing the season out) or the evening just played (a Session marked
Played keeps one, sessions.py). `changes` reads a copy against the
character as it stands now.

What is worth saying: Arts and Abilities (their new scores), spells
learned or lost, Virtues and Flaws gained or lost, Warping, aging and
Decrepitude, wounds and Fatigue, Confidence, Personality Traits and
Reputations, raw vis, silver, and the books and enchanted items held.
Notes, plans and what a season's record already says (its xp) are left
out.

Pattern: Memento. The kept copy is the memento, made and stored by others
and only read here; the diff reads two of them."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict
from typing import Any

from . import catalog
from .models import Character, Saga
from .rules import xp as xp_rules
from .rules.enchantment import held_by

#: The keys a kept copy holds beside the character's own data.
HELD_BOOKS = "_held_books"
HELD_DEVICES = "_held_devices"


def keep(saga: Saga, character: Character) -> dict[str, Any]:
    """`character` as a copy to read later: its own data, with the titles
    of the books and the names of the enchanted items it holds. Its
    Secrets, notes and Diary are left out: nothing here reads them, and a
    copy kept on a Session reaches the players with the saga."""
    data = asdict(character)
    for private in ("secrets", "diary", "summary"):
        data.pop(private, None)
    data[HELD_BOOKS] = sorted(
        b.name
        for b in saga.books
        if b.owner_kind == "character" and b.owner_id == character.id
    )
    data[HELD_DEVICES] = sorted(
        d.name for d in held_by(saga, "character", character.id)
    )
    return data


def keep_all(saga: Saga, characters: list[Character]) -> dict[str, dict[str, Any]]:
    return {c.id: keep(saga, c) for c in characters}


def changes(saga: Saga, before: dict[str, Any], after: Character) -> list[str]:
    """What changed in `after` since the copy `before`, a line each."""
    old = Character.from_dict(
        {k: v for k, v in before.items() if not k.startswith("_")}
    )
    now = keep(saga, after)
    lines: list[str] = []
    for part in PARTS:
        lines.extend(part(saga, old, after))
    lines.extend(_held("book", before.get(HELD_BOOKS) or [], now[HELD_BOOKS]))
    lines.extend(_held("item", before.get(HELD_DEVICES) or [], now[HELD_DEVICES]))
    return lines


def _moved(name: str, old: int, new: int) -> list[str]:
    return [f"{name} {old} to {new}"] if old != new else []


def _arts(_saga: Saga, old: Character, new: Character) -> list[str]:
    lines = []
    for art in sorted({*old.arts, *new.arts}):
        was = old.arts.get(art)
        now = new.arts.get(art)
        before = xp_rules.score_from_xp(was.xp, xp_rules.ART_FACTOR) if was else 0
        after = xp_rules.score_from_xp(now.xp, xp_rules.ART_FACTOR) if now else 0
        lines.extend(_moved(art.title(), before, after))
    return lines


def _abilities(_saga: Saga, old: Character, new: Character) -> list[str]:
    was = {a.name: a.level for a in old.abilities}
    now = {a.name: a.level for a in new.abilities}
    lines = []
    for name in sorted({*was, *now}):
        lines.extend(_moved(name, was.get(name, 0), now.get(name, 0)))
    return lines


def _spell_names(saga: Saga, character: Character) -> set[str]:
    names = set()
    for known in character.spells_known:
        spell = catalog.find_spell(saga, known.spell_id)
        names.add(spell.name if spell is not None else known.spell_id)
    return names


def _spells(saga: Saga, old: Character, new: Character) -> list[str]:
    was, now = _spell_names(saga, old), _spell_names(saga, new)
    return [f"learned {n}" for n in sorted(now - was)] + [
        f"no longer knows {n}" for n in sorted(was - now)
    ]


def _virtues(_saga: Saga, old: Character, new: Character) -> list[str]:
    known = catalog.load_virtue_flaw_catalog_by_id()

    def named(character: Character) -> set[str]:
        return {catalog.describe_virtue_flaw(v, known) for v in character.virtues_flaws}

    was, now = named(old), named(new)
    return [f"gained {n}" for n in sorted(now - was)] + [
        f"lost {n}" for n in sorted(was - now)
    ]


def _aging(_saga: Saga, old: Character, new: Character) -> list[str]:
    a, b = old.aging, new.aging
    return [
        *_moved("Warping Score", a.warping_score, b.warping_score),
        *_moved("Warping Points", a.warping_points, b.warping_points),
        *_moved("Decrepitude", a.decrepitude, b.decrepitude),
    ]


def _health(_saga: Saga, old: Character, new: Character) -> list[str]:
    a, b = old.wounds, new.wounds
    lines = [
        *_moved("Light Wounds", a.light, b.light),
        *_moved("Medium Wounds", a.medium, b.medium),
        *_moved("Heavy Wounds", a.heavy, b.heavy),
    ]
    if old.fatigue_level != new.fatigue_level:
        lines.append(f"Fatigue {old.fatigue_level} to {new.fatigue_level}")
    lines.extend(
        _moved("Long-term Fatigue", old.long_term_fatigue, new.long_term_fatigue)
    )
    return lines


def _confidence(_saga: Saga, old: Character, new: Character) -> list[str]:
    a, b = old.background, new.background
    return [
        *_moved("Confidence", a.confidence_score, b.confidence_score),
        *_moved("Confidence Points", a.confidence_points, b.confidence_points),
    ]


def _traits(_saga: Saga, old: Character, new: Character) -> list[str]:
    lines = []
    for label, a, b in (
        ("", old.personality_traits, new.personality_traits),
        ("Reputation ", old.reputations, new.reputations),
    ):
        was = {t.name: t.score for t in a}
        now = {t.name: t.score for t in b}
        for name in sorted({*was, *now}):
            if name not in was:
                lines.append(f"new {label.lower()}{name} {now[name]:+d}".strip())
            elif name not in now:
                lines.append(f"lost {label.lower()}{name}".strip())
            elif was[name] != now[name]:
                lines.append(f"{label}{name} {was[name]:+d} to {now[name]:+d}")
    return lines


def _stores(_saga: Saga, old: Character, new: Character) -> list[str]:
    lines = []
    for art in sorted({*old.raw_vis, *new.raw_vis}):
        was, now = old.raw_vis.get(art, 0), new.raw_vis.get(art, 0)
        if was != now:
            lines.append(f"{art.title()} vis {was} to {now} pawns")
    lines.extend(_moved("Silver", old.silver, new.silver))
    return lines


def _held(kind: str, was: list[str], now: list[str]) -> list[str]:
    gone, came = sorted(set(was) - set(now)), sorted(set(now) - set(was))
    return [f"gained the {kind} {n}" for n in came] + [
        f"no longer holds the {kind} {n}" for n in gone
    ]


#: Each part of a character worth saying a change in, in the order said.
PARTS: tuple[Callable[[Saga, Character, Character], list[str]], ...] = (
    _arts,
    _abilities,
    _spells,
    _virtues,
    _aging,
    _health,
    _confidence,
    _traits,
    _stores,
)


def text(saga: Saga, before: dict[str, Any], after: Character) -> str:
    """The changes as one line ("Nothing changed." for none)."""
    lines = changes(saga, before, after)
    return "; ".join(lines) + "." if lines else "Nothing changed."
