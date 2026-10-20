"""A tradition's own Warping, in place of Wizard's Twilight
(TraditionDef.warping), and the beings its members bind
(Character.bound_beings).

No hedge tradition goes into Twilight, and none gains Warping Points from
living in a strong magic aura (an Ex Miscellanea tradition's members are
Hermetic magi, and do); each tradition's chapter says what its
Gifted members suffer instead. Most of these are rolls the troupe makes
when they happen, shown as the book words them. An elementalist's is
worked out: a Personality Trait for each Elementalist Form he holds,

    Trait = Warping Score + Form / 5 (rounded up)

which acts as a Minor Personality Flaw from +3, a Major one from +6, and
takes the character out of the player's hands at +10.

Rules: Hedge Magic RE, Introduction (Warping) and each tradition's
chapter (Elemental Warping, the Witch Moon, Transformation, Intervention
and Abduction, Nátt-thel; the folk witch's familiar, the gruagach's
fetch).
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import BoundBeing, Character, TraditionDef
from . import hedge_casting as hc

SOURCE = (
    "Hedge Magic, Revised Edition "
    "(https://www.redcap.org/page/Hedge_Magic_Revised_Edition_Open_Content)"
)

#: The Social Status of a tradition whose members are Hermetic magi (an
#: Ex Miscellanea tradition): they suffer Twilight as any magus does.
HERMETIC_MAGUS = "vf_hermetic_magus"

#: Each Elementalist Form's temperament.
TEMPERAMENTS: dict[str, str] = {
    "Elementalist Fire": "Choleric",
    "Elementalist Earth": "Melancholic",
    "Elementalist Water": "Phlegmatic",
    "Elementalist Air": "Sanguine",
}
MINOR_AT = 3
MAJOR_AT = 6
MAD_AT = 10


@dataclass(frozen=True)
class ElementalTrait:
    trait: str
    form: str
    form_score: int
    value: int

    @property
    def effect(self) -> str:
        if self.value >= MAD_AT:
            return "the storyguide controls the character wherever it applies"
        if self.value >= MAJOR_AT:
            return "acts as a Major Personality Flaw"
        if self.value >= MINOR_AT:
            return "acts as a Minor Personality Flaw"
        return ""


def elemental_traits(character: Character) -> list[ElementalTrait]:
    """The elementalist's Trait for each Elementalist Form he holds."""
    warping = character.aging.warping_score
    found = []
    for form, trait in TEMPERAMENTS.items():
        if not hc.holds(character, form):
            continue
        score = hc.score(character, form)
        found.append(ElementalTrait(trait, form, score, warping + -(-score // 5)))
    return found


def bound(character: Character, tradition_id: str) -> list[tuple[int, BoundBeing]]:
    """The beings bound to the character by the tradition, each with its
    index into character.bound_beings."""
    return [
        (i, b)
        for i, b in enumerate(character.bound_beings)
        if b.tradition == tradition_id
    ]


def pool_key(tradition: TraditionDef, pool: str) -> str:
    """A pool's key in Character.tradition_pools: two traditions may name
    a pool alike."""
    return f"{tradition.id}:{pool}"


def pool_points(character: Character, tradition: TraditionDef, pool: str) -> int:
    return character.tradition_pools.get(pool_key(tradition, pool), 0)
