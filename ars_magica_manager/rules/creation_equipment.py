"""Two pieces of advice the book's creation summary gives that the steps
didn't: every Ability but Spell Mastery has a specialization (DE p. 157),
and the character's equipment comes last (DE p. 44, step 11). Both are
advice (☞), never a broken must: a troupe may leave them for later."""

from __future__ import annotations

from ..models import Character, Saga
from . import creation_access as access
from .creation_base import CHARACTER_CHECKS, Check, Record, check
from .creation_xp import entries, is_art

SPECIALTY_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 5: Abilities, Specializations, p. 157"
)
EQUIPMENT_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 3: Characters, Detailed Character "
    "Creation Summary, p. 44"
)
SOURCE = f"{SPECIALTY_SOURCE}; {EQUIPMENT_SOURCE}"
#: The worksheet steps that spend xp on Abilities.
XP_STEPS = ("childhood", "later_life", "training", "apprenticeship", "gauntlet")
#: The one Ability the book gives no specialization.
NO_SPECIALTY = "Spell Mastery"


def unspecialized(character: Character, step: str) -> list[str]:
    """The Abilities bought on `step` whose score has no specialty yet; a
    hedge tradition's Arts (an Ability with a role) are left out, as the
    Hermetic Arts are."""
    bought = {x.target for x in entries(character, step)}
    return sorted(
        a.name
        for a in character.abilities
        if a.name in bought
        and not is_art(a.name)
        and not _tradition_art(a.name)
        and not a.name.startswith(NO_SPECIALTY)
        and not (a.specialty or "").strip()
    )


def _tradition_art(name: str) -> bool:
    entry = access.ability_def(name)
    return entry is not None and bool(entry.role)


def _specialty_check(saga: Saga, record: Record, step: str) -> list[Check]:
    if not isinstance(record, Character):
        return []
    if not entries(record, step):
        return []
    missing = unspecialized(record, step)
    return [
        Check(
            step,
            "Each Ability has a specialty",
            "advice" if missing else "pass",
            ", ".join(missing) if missing else "all have one",
            SPECIALTY_SOURCE,
        )
    ]


def _register(step: str) -> None:
    @check(step, CHARACTER_CHECKS)
    def specialties(saga: Saga, record: Record) -> list[Check]:
        return _specialty_check(saga, record, step)


for _step in XP_STEPS:
    _register(_step)


@check("equipment", CHARACTER_CHECKS)
def equipment_checks(saga: Saga, record: Record) -> list[Check]:
    assert isinstance(record, Character)
    held = len(record.inventory)
    return [
        Check(
            "equipment",
            "Equipment recorded",
            "pass" if held else "advice",
            f"{held} item{'' if held == 1 else 's'}"
            if held
            else "none yet: add what they carry (weapons, armor, tools)",
            EQUIPMENT_SOURCE,
        )
    ]
