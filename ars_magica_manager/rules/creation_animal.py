"""Creation checks for an animal grog (rules.animal_grogs): its kind and
Language, the Virtues and Flaws every animal has, its Size, the 120 xp
of pre-adult life with the animal Language at 2, Restricted Learning's
five Abilities, and what a human Language or Animal Ken may reach.
Every check here is for an animal only.

Rules: Grogs, Chapter 7, Horses & Hounds (animal_grogs.SOURCE).
"""

from __future__ import annotations

from .. import catalog
from ..models import Character, Saga
from . import animal_aging
from . import animal_grogs as ag
from . import creation_access as access
from .creation_access import OPENS
from .creation_base import CHARACTER_CHECKS, Check, Record, check
from .creation_character import age
from .derived import size

SOURCE = ag.SOURCE


def _check(
    step: str,
    label: str,
    ok: bool,
    detail: str,
    source: str = ag.SOURCE,
    *,
    advice: bool = False,
) -> Check:
    status = "pass" if ok else ("advice" if advice else "warn")
    return Check(step, label, status, detail, source)


def _animal(record: Record) -> Character | None:
    if isinstance(record, Character) and record.animal is not None:
        return record
    return None


@check("concept", CHARACTER_CHECKS)
def animal_concept(saga: Saga, record: Record) -> list[Check]:
    character = _animal(record)
    if character is None or character.animal is None:
        return []
    animal = character.animal
    kind = ag.kind_of(character)
    found = [
        _check(
            "concept",
            "An animal is a grog",
            character.type == "grog",
            character.type,
        ),
        _check(
            "concept",
            "A kind of beast",
            kind is not None,
            ag.describe(animal) if kind is not None else f"unknown: {animal.kind}",
        ),
        _check(
            "concept",
            "The kind's own Language is named",
            bool(animal.language),
            animal.language or "none",
            ag.LANGUAGE_SOURCE,
        ),
    ]
    total = int(size(character).total)
    low, high = ag.SIZE_RANGE
    found.append(
        _check(
            "concept",
            f"Size from {low} to {high:+d}",
            low <= total <= high,
            f"{total:+d}",
            ag.SIZE_SOURCE,
            advice=True,
        )
    )
    years = age(saga, character)
    grown = ag.grown(character)
    if years is not None and grown is not None and years < grown:
        found.append(
            _check(
                "concept",
                f"Grown (from {grown})",
                False,
                f"{years}: younger than its 120 xp of pre-adult life",
                animal_aging.SOURCE,
                advice=True,
            )
        )
    return found


@check("virtues_flaws", CHARACTER_CHECKS)
def animal_virtues(saga: Saga, record: Record) -> list[Check]:
    character = _animal(record)
    if character is None:
        return []
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    ids = [vf.vf_id for vf in character.virtues_flaws]
    found = [
        _check(
            "virtues_flaws",
            "An animal takes Restricted Learning",
            ag.RESTRICTED_LEARNING in ids,
            "taken" if ag.RESTRICTED_LEARNING in ids else "missing",
        )
    ]
    missing = [by_id[f].name for f in ag.FREE_FLAWS if f not in ids and f in by_id]
    found.append(
        _check(
            "virtues_flaws",
            "No Hands and Mute, held free",
            not missing,
            ", ".join(missing) + " missing" if missing else "taken",
            advice=True,
        )
    )
    statuses = [
        by_id[vf_id]
        for vf_id in ids
        if vf_id in by_id
        and "Social Status" in (by_id[vf_id].category, *by_id[vf_id].extra_categories)
    ]
    wrong = [e.name for e in statuses if e.id not in ag.STATUSES]
    found.append(
        _check(
            "virtues_flaws",
            "Domestic Animal, Wanderer or Companion Animal",
            bool(statuses) and not wrong,
            ", ".join(wrong) or ", ".join(e.name for e in statuses) or "none",
        )
    )

    society = [
        by_id[vf_id].name
        for vf_id in ids
        if vf_id in by_id
        and "Social Status"
        not in (by_id[vf_id].category, *by_id[vf_id].extra_categories)
        and ag.about_society(by_id[vf_id], OPENS)
    ]
    if society:
        found.append(
            _check(
                "virtues_flaws",
                "Nothing about human society",
                False,
                ", ".join(society),
            )
        )
    return found


@check("characteristics", CHARACTER_CHECKS)
def animal_characteristics(saga: Saga, record: Record) -> list[Check]:
    character = _animal(record)
    if character is None:
        return []
    total = int(size(character).total)
    if not total:
        return []
    return [
        _check(
            "characteristics",
            "Size added after the points",
            True,
            f"Strength {2 * total:+d}, Quickness {-total:+d} (Size {total:+d})",
            ag.SIZE_SOURCE,
        )
    ]


def _youth_entries(character: Character):
    return [x for x in character.creation_xp if x.step == "youth"]


@check("youth", CHARACTER_CHECKS)
def animal_youth(saga: Saga, record: Record) -> list[Check]:
    character = _animal(record)
    if character is None or character.animal is None:
        return []
    language = character.animal.language
    entries = _youth_entries(character)
    own = [x for x in entries if x.note == ag.LANGUAGE_NOTE]
    others = [x for x in entries if x.note != ag.LANGUAGE_NOTE]
    found = [
        _check(
            "youth",
            f"The animal Language at {ag.LANGUAGE_SCORE}",
            len(own) == 1 and own[0].xp == ag.LANGUAGE_XP and own[0].target == language,
            f"{own[0].target} ({own[0].xp} xp)" if len(own) == 1 else f"{len(own)} set",
            ag.LANGUAGE_SOURCE,
        )
    ]
    total = sum(x.xp for x in others)
    found.append(
        _check(
            "youth",
            f"At most {ag.YOUTH_XP} xp of pre-adult life",
            total <= ag.YOUTH_XP,
            f"{total} spent"
            + (f", {total - ag.YOUTH_XP} too many" if total > ag.YOUTH_XP else ""),
        )
    )
    if total < ag.YOUTH_XP:
        found.append(
            _check(
                "youth",
                "Pre-adult xp spent",
                False,
                f"{ag.YOUTH_XP - total} unspent",
                advice=True,
            )
        )
    raised = [x for x in others if ag.own_language(character, x.target)]
    if raised:
        found.append(
            _check(
                "youth",
                f"{language} is never raised",
                False,
                f"{sum(x.xp for x in raised)} xp spent on it",
                ag.LANGUAGE_SOURCE,
            )
        )
    return found


@check("later_life", CHARACTER_CHECKS)
def animal_later_life(saga: Saga, record: Record) -> list[Check]:
    character = _animal(record)
    if character is None or character.animal is None:
        return []
    targets = [
        x.target
        for x in character.creation_xp
        if x.step in ("youth", "later_life", "virtue")
    ]
    chosen = access.restricted_choices(character, targets)
    found = []
    if any(vf.vf_id == ag.RESTRICTED_LEARNING for vf in character.virtues_flaws):
        found.append(
            _check(
                "later_life",
                f"xp on at most {ag.RESTRICTED_ABILITIES} Abilities "
                "(Restricted Learning)",
                len(chosen) <= ag.RESTRICTED_ABILITIES,
                f"{len(chosen)}: {', '.join(chosen)}" if chosen else "none yet",
            )
        )
    raised = [
        x.xp
        for x in character.creation_xp
        if x.step in ("later_life", "virtue") and ag.own_language(character, x.target)
    ]
    if raised:
        found.append(
            _check(
                "later_life",
                f"{character.animal.language} is never raised",
                False,
                f"{sum(raised)} xp spent on it",
                ag.LANGUAGE_SOURCE,
            )
        )
    levels = {a.name: a.level for a in character.abilities}
    ken = levels.get(ag.ANIMAL_KEN)
    own = levels.get(character.animal.language, 0)
    if ken is not None:
        found.append(
            _check(
                "later_life",
                f"Animal Ken no higher than {character.animal.language or 'its Language'}",
                ken <= own,
                f"Animal Ken {ken}, {character.animal.language or 'Language'} {own}",
                ag.SOURCE,
            )
        )
    return found
