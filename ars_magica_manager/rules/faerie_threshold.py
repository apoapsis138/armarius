"""Into Faerie: finding a faerie regio's way in, and crossing the
Threshold into the Faerie Realm.

**Finding a regio entrance** (Realms of Power: Faerie p. 16). One with
Faerie Sight, Second Sight or Magic Sensitivity reads how to enter the
next level with Per + Awareness against 5 + twice the difference between
the two auras (the core rule, DE p. 421, which rules.senses keeps). One
who has found the entrance but not the action that opens it may guess it
from the local faeries' motif: Int + Faerie Lore against 15, or 3 when
the story has narrowed it to a choice (a horn or a sword). Others find it
by being let in, being told the action, following an Arcane Connection,
an Intellego Vim spell, or a True Love within. An entrance to Faerieland
from a faerie regio is a regio level of aura 10 (rules.otherworlds).

**The Threshold** (Realms of Power: Faerie pp. 20-24). To enter the
Faerie Realm, travelers gather Threshold points equal to its strength:
(13 - the aura modifier) x 3, the modifier being the local aura's on a
Faerie power (the realm table, DE pp. 410-411). In a Faerie regio the base aura's
modifier adds to the regio's when it is Faerie, and any other base aura
is ignored. Points come from the border crossed (3 / 6 / 9 / 12, +3 if
lost; a trod is at least Significant), the time (new moon 1, full moon
3, a locally kept pagan holiday 3, solstice 6, equinox 9), personal
change (only the best of the faerie Virtue and Flaw lines; an extreme
emotion 3 + its Trait, a Minor Personality Flaw counting +3 and a Major
+6), a work of art that commemorates Faerie (its Aesthetic Quality), a
Threshold faerie's Spirit Away (a Might Point a point, 3 a person to send
away; never the only source), and the Arcadian Travel charm (Ease Factor
18 to make; stress die + Per + the Ability + aura). A highly cognizant
faerie crossing has its Might's magnitude in points; a narrowly
cognizant one adds it when the conditions suit its role. A set of
circumstances is tried once; changed, it may be tried again at the next
moonrise. The Guardian of the Threshold then offers the choice: its
Faerie Might is at least the group's Threshold total, and Int + Faerie
Lore against 6 gives hints.

The book's own regio example says a Faerie regio of 5 over a Faerie aura
of 2 has a modifier of 7 "for a Threshold strength of 15"; its formula
gives 18, and the app follows the formula.

Pattern: plain functions over dict tables, one per kind of source.
"""

from __future__ import annotations

from collections.abc import Mapping

from ..models import Character, VirtueFlawDef
from .realms import aura_modifier, virtue_realm

SOURCE = "Realms of Power: Faerie, Getting to Faerie, pp. 20-24"
ENTRANCE_SOURCE = "Realms of Power: Faerie, Finding a Regio Entrance, p. 16"

#: Guessing an entrance's action: Int + Faerie Lore against these.
GUESS_EASE = 15
GUESS_EASE_NARROWED = 3
#: The Guardian's hints: Int + Faerie Lore against this.
GUARDIAN_HINT_EASE = 6
#: Making the Arcadian Travel charm: Dex or Com + Ability against this.
CHARM_EASE = 18
#: Might Points Spirit Away costs to send one person away from Faerie.
SEND_AWAY_COST = 3

#: Threshold points for the border crossed.
BORDERS: dict[str, int] = {
    "Insignificant (a road, stream or fence)": 3,
    "Minor (a crossroads, the edge of a wood, a city wall)": 6,
    "Significant (an oasis, the treeline, a trod)": 9,
    "Major (a significant border into a faerie regio)": 12,
}
#: Crossing a border while truly lost.
LOST = 3

#: Threshold points for the time.
TIMES: dict[str, int] = {
    "New moon": 1,
    "Full moon": 3,
    "Pagan holiday (kept locally)": 3,
    "Solstice": 6,
    "Equinox": 9,
}

#: Threshold points from Virtues and Flaws: only the best counts.
FAERIE_VIRTUES_MINOR, FAERIE_VIRTUES_MAJOR, FAERIE_FLAWS = 3, 9, 3

#: Threshold points for a life change.
LIFE_CHANGES: dict[str, int] = {
    "Minor (puberty, menopause)": 9,
    "Minor, with a celebration (a betrothal)": 12,
    "Major (a common law marriage, a birth)": 15,
    "Major, with a religious ceremony (a wedding, a baptism)": 18,
}

#: An extreme emotion: this + its Trait; a Personality Flaw counts as a
#: Trait of these.
EMOTION_BASE = 3
PERSONALITY_FLAW_TRAIT = {"Minor": 3, "Major": 6}


def threshold_strength(
    aura: int, realm: str, base_aura: int = 0, base_realm: str = ""
) -> int:
    """The Threshold points needed to enter the Faerie Realm from an aura:
    (13 - its modifier on a Faerie power) x 3. In a Faerie regio, a base
    Faerie aura's modifier adds to the regio's; another base aura doesn't
    count. Never below 0."""
    modifier = aura_modifier("Faerie", realm, max(0, aura))
    if realm == "Faerie" and base_realm == "Faerie":
        modifier += aura_modifier("Faerie", "Faerie", max(0, base_aura))
    return max(0, (13 - modifier) * 3)


def personal_points(
    *,
    minor_virtues: bool = False,
    major_virtues: bool = False,
    faerie_flaws: bool = False,
    emotion_trait: int | None = None,
    life_change: str = "",
) -> int:
    """A character's own Threshold points: the best of the faerie Virtue
    and Flaw lines, an extreme emotion (3 + its Trait; None for none), and
    a life change."""
    blood = max(
        FAERIE_VIRTUES_MAJOR if major_virtues else 0,
        FAERIE_VIRTUES_MINOR if minor_virtues else 0,
        FAERIE_FLAWS if faerie_flaws else 0,
    )
    emotion = EMOTION_BASE + max(0, emotion_trait) if emotion_trait is not None else 0
    return blood + emotion + LIFE_CHANGES.get(life_change, 0)


def faerie_blood(
    character: Character, catalog_by_id: Mapping[str, VirtueFlawDef]
) -> tuple[bool, bool, bool]:
    """Whether `character` has Minor faerie Virtues, Major ones, and faerie
    Flaws: the Virtues and Flaws of the Faerie realm (rules.realms)."""
    minor = major = flaws = False
    for instance in character.virtues_flaws:
        found = catalog_by_id.get(instance.vf_id)
        if found is None or virtue_realm(found.id, found.name) != "Faerie":
            continue
        if found.type == "Flaw":
            flaws = True
        elif found.type == "Virtue" and found.tier == "Major":
            major = True
        elif found.type == "Virtue":
            minor = True
    return minor, major, flaws


def character_points(
    character: Character,
    catalog_by_id: Mapping[str, VirtueFlawDef],
    *,
    emotion_trait: int | None = None,
    life_change: str = "",
) -> int:
    """A character's own Threshold points, their faerie Virtues and Flaws
    read from their sheet."""
    minor, major, flaws = faerie_blood(character, catalog_by_id)
    return personal_points(
        minor_virtues=minor,
        major_virtues=major,
        faerie_flaws=flaws,
        emotion_trait=emotion_trait,
        life_change=life_change,
    )


def threshold_points(
    *,
    border: str = "",
    lost: bool = False,
    time: str = "",
    personal: int = 0,
    art_quality: int = 0,
    spirit_away: int = 0,
    charm: int = 0,
    faerie_magnitude: int = 0,
) -> int:
    """The Threshold points a set of circumstances gathers. Spirit Away's
    points count only when something else gives some."""
    own = (
        BORDERS.get(border, 0)
        + (LOST if lost and border else 0)
        + TIMES.get(time, 0)
        + max(0, personal)
        + max(0, art_quality)
        + max(0, charm)
        + max(0, faerie_magnitude)
    )
    return own + max(0, spirit_away) if own else 0


def crosses(points: int, strength: int) -> bool:
    """Whether the Threshold comes: the points reach its strength."""
    return points >= strength


def guess_ease(narrowed: bool = False) -> int:
    """Guessing the action that opens a found entrance (Int + Faerie Lore)."""
    return GUESS_EASE_NARROWED if narrowed else GUESS_EASE


def guardian_might(threshold_total: int) -> int:
    """The least Faerie Might the Guardian of the Threshold has."""
    return max(0, threshold_total)


def charm_total(stress_die: int, perception: int, ability: int, aura: int) -> int:
    """The Arcadian Travel Total, the Threshold points a made charm gives."""
    return stress_die + perception + ability + aura


def spirit_away_cost(points: int = 0, sent_away: int = 0) -> int:
    """The Might Points Spirit Away spends: one a Threshold point, three a
    person sent back out of Faerie."""
    return max(0, points) + SEND_AWAY_COST * max(0, sent_away)


def strength_text(
    aura: int, realm: str, base_aura: int = 0, base_realm: str = ""
) -> str:
    """ "30 points", as a place's facts show a Threshold's strength."""
    strength = threshold_strength(aura, realm, base_aura, base_realm)
    return "open (0 points)" if strength == 0 else f"{strength} points"
