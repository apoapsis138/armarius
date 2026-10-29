"""Creation checks from Virtues and Flaws the other steps don't hold
(DE Chapter Four): Warped by Magic's five Warping Points, Academic
Abilities needing a written language at 3, Mastered Spells' 50 xp of
Mastery, Savantism's favoured Ability, Nephilim's two Great
Characteristics, a Devil Child's three free Virtue points, Jerbiton's
free Virtue, the Gifted non-magus's training Virtues, and the young
character's Size.
"""

from __future__ import annotations

from ..models import Character, Saga
from . import creation_access as access
from . import enchantment, powers
from .creation_base import CHARACTER_CHECKS, Check, Record, check, judged

SOURCE = "Ars Magica Definitive Edition, Chapter Four: Virtues and Flaws, pp. 56-158"

WARPED_BY_MAGIC = "vf_warped_by_magic"
WARPED_POINTS = 5
MASTERED_SPELLS = "vf_mastered_spells"
MASTERED_XP = 50
#: The written languages an Academic Ability needs at 3 (DE p. 158).
WRITTEN = (
    "Dead Language: Latin",
    "Dead Language: Greek",
    "Living Language: Greek",
    "Dead Language: Hebrew",
    "Living Language: Hebrew",
    "Living Language: Arabic",
)
ACADEMIC_LANGUAGE = 3
NEPHILIM = "vf_nephilim"
GREAT = "vf_great_characteristic"
#: The Hermetic Virtues and Flaws of background or training, which a
#: Gifted non-magus shouldn't take (DE p. 64): a judgement, so advice.
TRAINING_VIRTUES = (
    "vf_skilled_parens",  # p. 108
    "vf_mastered_spells",  # p. 96
    "vf_weak_parens",  # p. 152
    "vf_infamous_master",  # p. 134
    "vf_hermetic_prestige",  # p. 85
    "vf_tormenting_master",  # p. 146
    # A House's Outer Mystery or membership (pp. 74, 78, 79, 85, 114).
    "vf_heartbeast",
    "vf_the_enigma",
    "vf_faerie_magic",
    "vf_verditius_magic",
    "vf_clan_ilfetu",
    "vf_guest_of_house_criamon",
    # A lineage's traditions (pp. 76, 98).
    "vf_diedne_magic",
    "vf_mercurian_magic",
    # How the Parma was taught (pp. 130, 145).
    "vf_flawed_parma_magica",
    "vf_stockade_parma_magica",
)


def _check(
    label: str, ok: bool, detail: str, page: int, *, advice: bool = False
) -> Check:
    return judged(
        "finish",
        label,
        ok,
        detail,
        f"{SOURCE.rsplit(', pp.', 1)[0]}, p. {page}",
        advice=advice,
    )


def _has(character: Character, vf_id: str) -> int:
    return sum(1 for vf in character.virtues_flaws if vf.vf_id == vf_id)


def _score(character: Character, name: str) -> int:
    return next((a.level for a in character.abilities if a.name == name), 0)


@check("finish", CHARACTER_CHECKS)
def rest_checks(saga: Saga, record: Record) -> list[Check]:
    assert isinstance(record, Character)
    c = record
    found: list[Check] = []
    if _has(c, WARPED_BY_MAGIC):
        points = c.aging.warping_points
        found.append(
            _check(
                f"Warped by Magic: {WARPED_POINTS} Warping Points and a Minor Flaw",
                points >= WARPED_POINTS or c.aging.warping_score >= 1,
                f"{points} points, score {c.aging.warping_score}",
                151,
                advice=True,
            )
        )
    academic = [
        a.name
        for a in c.abilities
        if a.level > 0 and access.ability_category(a.name) == access.ACADEMIC
    ]
    if academic and not any(_score(c, w) >= ACADEMIC_LANGUAGE for w in WRITTEN):
        found.append(
            _check(
                "Academic Abilities need Latin, Greek, Hebrew or Arabic at 3",
                False,
                ", ".join(academic),
                158,
                advice=True,
            )
        )
    copies = _has(c, MASTERED_SPELLS)
    if copies:
        spent = sum(k.mastery_xp for k in c.spells_known)
        allowed = MASTERED_XP * copies
        found.append(
            _check(
                f"Mastered Spells: {allowed} xp of Spell Mastery",
                spent <= allowed or _has(c, "vf_flawless_magic") > 0,
                f"{spent} spent",
                96,
                advice=True,
            )
        )
    favoured = access.savant_ability(c)
    if favoured is not None:
        found.append(
            _check(
                "Savantism names its favoured Ability",
                bool(favoured),
                favoured or "not named",
                143,
            )
        )
    if _has(c, NEPHILIM):
        greats = {
            str(vf.params.get("characteristic") or "").casefold()
            for vf in c.virtues_flaws
            if vf.vf_id == GREAT
        }
        found.append(
            _check(
                "Nephilim take Great Stamina and Great Strength",
                {"stamina", "strength"} <= greats,
                ", ".join(sorted(g for g in greats if g)) or "neither",
                58,
            )
        )
    if access.gifted_non_magus(c):
        trained = [vf.vf_id for vf in c.virtues_flaws if vf.vf_id in TRAINING_VIRTUES]
        if trained:
            found.append(
                _check(
                    "A Gifted non-magus takes only intrinsic Hermetic Virtues",
                    False,
                    ", ".join(trained),
                    64,
                    advice=True,
                )
            )
    found += [
        _check("Powers within their Virtues", False, x, 81) for x in powers.problems(c)
    ]
    found += [
        _check("Items within their Virtues", False, x, 97)
        for x in powers.item_problems(c, _items(saga, c))
    ]
    return found


def _items(saga: Saga | None, c: Character) -> list[tuple[str, list[int], str]]:
    if saga is None:
        return []
    return [
        (d.granted_by, [enchantment.modified_level(d, e) for e in d.effects], d.type)
        for d in saga.enchanted_devices
        if d.holder_kind == "character" and d.holder_id == c.id
    ]
