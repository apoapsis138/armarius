"""Creation for a hedge tradition's member: the Tradition Training step.

A character who joins a tradition at creation (its catalog record's
`training`) takes its required Virtues, and, if Gifted, its Opening: the
tradition's Arts and Abilities at 0, and any Virtue it gives. The
apprenticeship the book gives (a vitki's 240 xp and 120 levels of rune
scripts, a folk witch's 200 xp, a gruagach's 160 xp and 80 spell levels)
is spent on the tradition's Arts and the Abilities open to the
character, changed by the Well-Trained and Poorly Trained Virtues, and
leaves the minimum scores the book sets.

Each tradition's rules are data on its catalog record, read by the
functions here, as a House's are (creation_virtues.house_benefit).

Rules: reference/rules-engine-reference.md §18, each Hedge Magic
tradition's Character Creation.
"""

from __future__ import annotations

from .. import catalog
from ..models import Ability, Character, Saga, TraditionDef
from . import creation_access as access
from .creation_base import CHARACTER_CHECKS, Check, Record, check
from .creation_character import THE_GIFT
from .creation_xp import entries, spent
from .scores import ability_level

SOURCE = (
    "Hedge Magic, Revised Edition, each tradition's Character Creation "
    "(https://www.redcap.org/page/Hedge_Magic_Revised_Edition_Open_Content)"
)
STEP = "training"


def tradition(character: Character) -> TraditionDef | None:
    """The tradition a non-magus is made a member of: their first."""
    if character.type == "magus":
        return None
    found = access.traditions_of(character)
    return found[0] if found else None


def gifted(character: Character) -> bool:
    return any(vf.vf_id == THE_GIFT for vf in character.virtues_flaws)


def _modifier(character: Character, t: TraditionDef, which: int) -> int:
    """The Well-Trained / Poorly Trained Virtues' change to the xp
    (which=0) or the spell levels (which=1), each instance counted."""
    return sum(
        t.training.modifiers[vf.vf_id][which]
        for vf in character.virtues_flaws
        if vf.vf_id in t.training.modifiers
    )


def xp_budget(character: Character) -> int:
    t = tradition(character)
    if t is None:
        return 0
    base = t.training.xp if gifted(character) else t.training.ungifted_xp
    return max(base + _modifier(character, t, 0), 0) if base else 0


def level_budget(character: Character) -> int:
    t = tradition(character)
    if t is None:
        return 0
    base = t.training.levels if gifted(character) else t.training.ungifted_levels
    return max(base + _modifier(character, t, 1), 0) if base else 0


def opening(character: Character) -> list[str]:
    """What a Gifted member's Opening gives at 0 (none when unGifted)."""
    t = tradition(character)
    return list(t.training.opening) if t is not None and gifted(character) else []


def unopened(character: Character) -> list[str]:
    """The Opening's Arts and Abilities the character doesn't have yet."""
    held = {a.name for a in character.abilities}
    return [name for name in opening(character) if name not in held]


def takes_training(record: Record) -> bool:
    """Whether the record goes through the Tradition Training step: a
    member with an apprenticeship or an Opening to take."""
    if not isinstance(record, Character):
        return False
    return bool(xp_budget(record) or level_budget(record) or opening(record))


def required_virtues(character: Character) -> list[str]:
    """The Virtues membership requires (catalog ids), and the Opening's
    free ones for a Gifted member who isn't a magus (a magus of House Ex
    Miscellanea takes his tradition's Virtues as the House's)."""
    found = access.traditions_of(character)
    t = found[0] if found else None
    if t is None:
        return []
    wanted = [*t.virtues, *([t.social_status] if t.social_status else [])]
    if gifted(character) and character.type != "magus":
        wanted += t.training.opening_virtues
    return list(dict.fromkeys(wanted))


def missing_virtues(character: Character) -> list[str]:
    held = {vf.vf_id for vf in character.virtues_flaws}
    return [vf_id for vf_id in required_virtues(character) if vf_id not in held]


def targets(character: Character) -> list[str]:
    """What the apprenticeship xp may buy: the tradition's Arts and
    Abilities it may learn, the minimums' Abilities, and the Abilities
    open to the character."""
    t = tradition(character)
    if t is None:
        return []
    own = [name for name in t.abilities if access.may_learn(character, name)]
    return list(
        dict.fromkeys(
            [*own, *t.training.minimums, *access.learnable_abilities(character)]
        )
    )


def allowed(character: Character, target: str) -> bool:
    t = tradition(character)
    return t is not None and (
        target in t.training.minimums or access.may_learn(character, target)
    )


def arts_spent(character: Character) -> int:
    """The apprenticeship xp spent on the tradition's own Arts (its
    Abilities with a role: Techniques, Forms, runes...)."""
    t = tradition(character)
    if t is None:
        return 0
    arts = {
        name
        for name in t.abilities
        if (entry := access.ability_def(name)) is not None and entry.role
    }
    return sum(x.xp for x in entries(character, STEP) if x.target in arts)


def open_tradition(character: Character) -> list[str]:
    """Give the character the Opening's Arts and Abilities at 0 (each on
    its own xp table); returns their names."""
    added = unopened(character)
    for name in added:
        character.abilities.append(opened_ability(name))
    return added


def opened_ability(name: str) -> Ability:
    """An Art or Ability an Opening gives, at 0, with its catalog
    category and xp table."""
    entry = access.ability_def(name)
    return Ability(
        name=name,
        category=entry.category if entry is not None else "General",
        xp=0,
        xp_table=access.ability_xp_table(name),
    )


def _check(
    label: str, ok: bool, detail: str, *, advice: bool = False, step: str = STEP
) -> Check:
    status = "pass" if ok else ("advice" if advice else "warn")
    return Check(step, label, status, detail, SOURCE)


@check("concept", CHARACTER_CHECKS)
def tradition_concept_checks(saga: Saga, record: Record) -> list[Check]:
    """A member has The Gift if the tradition needs it (none if it
    allows none), and the Virtues membership requires."""
    assert isinstance(record, Character)
    t = tradition(record)
    if t is None:
        return []
    found = []
    rule = t.training.gift
    if rule != "optional":
        found.append(
            _check(
                f"A {t.name} member has "
                + ("The Gift" if rule == "required" else "no Gift"),
                gifted(record) == (rule == "required"),
                "Gifted" if gifted(record) else "unGifted",
                step="concept",
            )
        )
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    missing = [by_id[v].name if v in by_id else v for v in missing_virtues(record)]
    found.append(
        _check(
            "The tradition's Virtues taken",
            not missing,
            ", ".join(missing) or "all taken",
            step="concept",
        )
    )
    return found


def _budget_checks(character: Character) -> list[Check]:
    budget = xp_budget(character)
    if not budget:
        return []
    used = spent(character, STEP)
    found = [
        _check(
            f"Apprenticeship xp: {budget}",
            used <= budget,
            f"{used} spent" + (f", {used - budget} too many" if used > budget else ""),
        )
    ]
    if used < budget:
        found.append(
            _check(
                "Apprenticeship xp spent",
                False,
                f"{budget - used} unspent",
                advice=True,
            )
        )
    wrong = sorted(
        {x.target for x in entries(character, STEP) if not allowed(character, x.target)}
    )
    if wrong:
        found.append(
            _check(
                "Only the tradition's Arts and open Abilities", False, ", ".join(wrong)
            )
        )
    return found


@check(STEP, CHARACTER_CHECKS)
def training_checks(saga: Saga, record: Record) -> list[Check]:
    assert isinstance(record, Character)
    character = record
    t = tradition(character)
    if t is None:
        return []
    found = _budget_checks(character)
    if t.training.arts_xp and xp_budget(character):
        used = arts_spent(character)
        found.append(
            _check(
                f"At least {t.training.arts_xp} xp on the tradition's Arts",
                used >= t.training.arts_xp,
                f"{used}",
            )
        )
    if gifted(character):
        left = unopened(character)
        if t.training.opening:
            found.append(
                _check(
                    "The Opening's Arts and Abilities given",
                    not left,
                    ", ".join(left) or "all given",
                )
            )
        for name, least in t.training.minimums.items():
            level = ability_level(character, name)
            found.append(_check(f"{name} at least {least}", level >= least, f"{level}"))
    if t.training.art_cap:
        over = [
            f"{a.name} {a.level}"
            for a in character.abilities
            if a.name in t.abilities
            and a.xp_table == "art"
            and a.level > t.training.art_cap
        ]
        found.append(
            _check(
                f"No Art above {t.training.art_cap} at creation",
                not over,
                ", ".join(over) or "none above",
            )
        )
    return found
