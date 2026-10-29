"""Creation checks for Finishing Touches: Personality Traits
(-3..+3; a grog needs Loyal, a warrior Brave), Reputations only from
Virtues and Flaws, Confidence (score 1 and 3 points for magi and
companions, none for grogs), and a Merinita magus's Warping Point when
nothing faerie touched him. The step's "Move to In Play" then shows the
review of every check.

Rules: reference/rules-engine-reference.md §2 Personality Traits;
Reputations; Confidence.
"""

from __future__ import annotations

import re

from .. import catalog
from ..models import Character, Saga
from . import creation_access as access
from .creation_base import CHARACTER_CHECKS, Check, Record, check, judged

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Personality Traits, p. "
    "28"
)
REPUTATION_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Reputations, p. 52"
)
CONFIDENCE_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Detailed Character "
    "Creation Summary, p. 44"
)

MERINITA_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Seven: Hermetic Magic, Merinita "
    "— Faerie Magic, p. 236"
)

TRAIT_LIMIT = 3
#: A Major Personality Flaw's matching Trait.
FLAW_TRAIT_LIMIT = 6
CONFIDENCE_SCORE, CONFIDENCE_POINTS = 1, 3
#: Virtues that change the starting Confidence: (score, points) added.
CONFIDENCE_VIRTUES: dict[str, tuple[int, int]] = {
    "vf_self_confident": (1, 2),
    "vf_improved_confidence": (1, 2),
    "vf_heroic_personality": (1, 2),
    "vf_low_self_esteem": (-CONFIDENCE_SCORE, -CONFIDENCE_POINTS),
}


def has_trait(character: Character, name: str) -> bool:
    return any(name.lower() in t.name.lower() for t in character.personality_traits)


CHURCH_UPBRINGING = "vf_church_upbringing"
CHURCH_XP = 25
CHURCH_SOURCE = "Ars Magica Definitive Edition, Church Upbringing, p. 122"


def church_xp(character: Character) -> int:
    """Creation xp spent on Church Upbringing's Abilities: Artes Liberales,
    Latin, Music, Organization Lore: Church and Theology (DE p. 122)."""
    return sum(
        entry.xp
        for entry in character.creation_xp
        if entry.target in ("Artes Liberales", "Dead Language: Latin", "Music")
        or entry.target.startswith(("Organization Lore: Church", "Theology"))
    )


def warrior(character: Character) -> bool:
    """A character with xp in a Martial Ability."""
    return any(
        access.ability_category(a.name) == access.MARTIAL and a.xp > 0
        for a in character.abilities
    )


def expected_confidence(character: Character) -> tuple[int, int]:
    """(score, points) the character should start with."""
    if character.type == "grog":
        return 0, 0
    score, points = CONFIDENCE_SCORE, CONFIDENCE_POINTS
    for vf in character.virtues_flaws:
        extra = CONFIDENCE_VIRTUES.get(vf.vf_id)
        if extra:
            score, points = score + extra[0], points + extra[1]
    return score, points


def touched_by_the_fay(character: Character) -> bool:
    """A Virtue or Flaw related to the fay, besides Faerie Magic itself:
    what qualifies a character for the Mystery (DE p. 236)."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    for vf in character.virtues_flaws:
        entry = by_id.get(vf.vf_id)
        name = entry.name if entry is not None else ""
        if vf.vf_id != "vf_faerie_magic" and re.search(r"\bFa(erie|e|y)\b", name):
            return True
    return False


def reputation_virtues(character: Character) -> list[str]:
    """The character's Virtues and Flaws whose text gives a Reputation."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    return [
        by_id[vf.vf_id].name
        for vf in character.virtues_flaws
        if vf.vf_id in by_id and re.search(r"Reputation", by_id[vf.vf_id].summary)
    ]


def _check(
    label: str, ok: bool, detail: str, source: str = SOURCE, *, advice: bool = False
):
    return judged("finish", label, ok, detail, source, advice=advice)


@check("finish", CHARACTER_CHECKS)
def finish_checks(saga: Saga, record: Record) -> list[Check]:
    assert isinstance(record, Character)
    character = record
    traits = character.personality_traits
    found = [
        _check(
            "A few Personality Traits",
            bool(traits),
            f"{len(traits)}" + ("" if traits else ", pick some (a third is suggested)"),
            advice=True,
        )
    ]
    for trait in traits:
        size = abs(trait.score)
        if size > FLAW_TRAIT_LIMIT:
            found.append(
                _check(f"{trait.name} from -3 to +3", False, f"{trait.score:+d}")
            )
        elif size > TRAIT_LIMIT:
            # Only a Major Personality Flaw's matching Trait goes past 3.
            found.append(
                _check(
                    f"{trait.name} past 3 only from a Personality Flaw",
                    False,
                    f"{trait.score:+d}",
                    advice=True,
                )
            )
    if character.type == "grog":
        found.append(
            _check(
                "A grog has Loyal",
                has_trait(character, "Loyal"),
                "taken" if has_trait(character, "Loyal") else "missing",
                advice=True,
            )
        )
    if warrior(character):
        found.append(
            _check(
                "A warrior has Brave",
                has_trait(character, "Brave"),
                "taken" if has_trait(character, "Brave") else "missing",
                advice=True,
            )
        )
    if any(vf.vf_id == CHURCH_UPBRINGING for vf in character.virtues_flaws):
        spent = church_xp(character)
        found.append(
            _check(
                f"Church Upbringing: {CHURCH_XP} xp on its Abilities",
                spent >= CHURCH_XP,
                f"{spent} xp",
                CHURCH_SOURCE,
                advice=True,
            )
        )
    if character.reputations:
        granted = reputation_virtues(character)
        found.append(
            _check(
                "Reputations come only from Virtues and Flaws",
                bool(granted),
                ", ".join(granted) or "no Virtue or Flaw gives one",
                REPUTATION_SOURCE,
                advice=True,
            )
        )
    if character.hermetic.house == "house_merinita" and not touched_by_the_fay(
        character
    ):
        warped = character.aging.warping_score > 0 or character.aging.warping_points > 0
        found.append(
            _check(
                "A Merinita untouched by the fay starts with a Warping Point",
                warped,
                "taken"
                if warped
                else "his parens gave him one (no faerie Virtue or Flaw)",
                MERINITA_SOURCE,
            )
        )
    score, points = expected_confidence(character)
    b = character.background
    label = (
        "A grog has no Confidence"
        if character.type == "grog"
        else f"Confidence Score {score}, {points} Confidence Points"
    )
    found.append(
        _check(
            label,
            (b.confidence_score, b.confidence_points) == (score, points),
            f"{b.confidence_score}, {b.confidence_points} points",
            CONFIDENCE_SOURCE,
        )
    )
    return found
