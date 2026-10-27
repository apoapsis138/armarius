"""Hermetic spirit magic and Hermetic theurgy (The Mysteries Revised
Edition, Chapter Eight pp. 64-74 and Chapter Nine pp. 75-88, with the
Errata's corrections to pp. 66, 77 and 78). Plain rules: the More
calculator (forms.tmre_spirits) asks for the spirit's figures, which the
sheet never knows.

Spirit magic (Chapter Eight):

- Hermetic Empowerment (pp. 64-66): a Ritual effect in a device is
  powered by a bound spirit, each use draining (Ritual level / 5, rounded
  up) points of Might Score for good. The spirit's Might x 2 must at
  least equal the Ritual's level (the Errata, p. 50, corrects p. 66 to
  the same: Might at least half the level). A Ritual effect is at least
  level 20. The Empowering Prison's base level must at least equal twice
  the Might of the spirit it holds.
- Spirit Familiar (pp. 66-69): Lab Total = Technique + Form + Int +
  Magic Theory + aura modifier (the worse of the magus's and the
  spirit's); bonding level = Might + 25 (spirits have no Size); vis, as
  for any familiar, a pawn per 5 points of the Lab Total (DE p. 275
  reads the same). The spirit's Int, Per and Com are bought with Might / 5
  pyramid points. The Hekate Cord adds its score to a Stamina roll for
  each Might point the familiar spends (1 to 5), and a Fatigue level gives
  the familiar the bond score in temporary Might.
- Inscription on the Soul (pp. 69-70): the body and spirit open with 15
  pawns and need Magic Theory 8. Blending with Substance: the item's
  highest bonus plus half the rest (rounded up), x 5, is the Rego Vim
  effect's level; a Warping Point, and a second at level 30 or more.
- Living Ghost (pp. 70-74): Bind the Living Ghost is level 30 + the levels
  added for the Haunt's Size; Transformation of the Living Ghost's level
  must at least equal the transformation limit (the best Technique +
  Form, a Magical Focus doubling the lower Art), and gives Might = its
  level - the Haunt's levels, no more than the limit. A familiar that
  joins him costs bond score / 5 pawns (rounded up). As a ghost, Ghostly
  Magic costs a Might point a magnitude, Ghostly Vis a point of Might
  Score a pawn; Might spent so is restored by opening unused talisman
  spaces and recasting the Transformation, to its cap.

Theurgy (Chapter Nine):

- Names of Power (pp. 76-78): a Name is a Muto Vim spell of level 5 x its
  bonus. Their bonuses together, in an Invoke spell, by Invocation Magic
  or from a Consummate Talisman, never exceed Magic Theory (combined too:
  Errata p. 50 on pp. 77-78).
- Theurgic Lab Total (p. 79) = Technique + Form + Int + Magic Theory +
  aura + (Realm) Lore + the Names' bonus.
- Invoke the Spirit of (spell) (pp. 78-80): the spirit's Might must at
  least equal the power's level and is the Invoke spell's base level;
  each level added for Penetration gives +2. The spirit's Casting Score
  is its Might + aura modifier, no die; it succeeds at (adjusted level -
  10) or more, the level moved by a magnitude when the magus varies it;
  Penetration = Casting Total - adjusted level + the Invoke spell's bonus.
- Invoke the Spirit of (Form) (p. 80): Casting Total = (Might + aura
  modifier) / 2, rounded up, as Spontaneous magic; Penetration = that -
  the effect's level.
- Invoke the Pact of (Daimon) (pp. 80-81): each casting that penetrates
  gathers (level - Might) summoning points; at its Might the Daimon sends
  an Aspect. Twice its Might summons it at once, the only way without
  Hermetic Theurgy. A Daimon familiar takes Might / 5 pawns (rounded up),
  and is likely to refuse a bond of Technique + Form under twice its
  Might (p. 82). A Daimon gains (pact level / 5, rounded up) Daimon
  Points when it is called (p. 85; p. 86 spends them).
- Ascendancy to the Hall of Heroes (pp. 82-86): the Ascendant Form's
  level at least equals the best Technique + Form, and 40; its level / 2
  is his Might. Each Transformation that penetrates gives (its level -
  the Form's) points, against the Form's level + 3 x the negative
  Characteristics' pyramid cost + 5 x Decrepitude + 5 x Flaw points when
  they exceed Virtue points (Major 3, Minor 1). Stamina against 9 or he
  passes out.
- Hermetic Synthemata (pp. 86-87): Synthemata of (X) at least the
  being's Might, adding its level to Penetration; the Lasting version's
  level - 5. Research: Muto + Vim + Int + (Realm) Lore + aura + bonuses
  (an Arcane Connection's multiplier), less the level and the name hiding
  (typically Might / 2) each season.
- Synthemata Magia (pp. 87-88): intuiting is a stress die + Per + (Realm)
  Lore + his aura modifier against Might + the spirit's aura modifier +
  name hiding; researching (a season) adds the aura and an Arcane
  Connection's multiplier against Might + name hiding. The Hedge Lord's
  Synthemata adds its level - 5 to his Casting Score against the being.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..arts import FORMS, TECHNIQUES
from ..models import Character
from . import lab, lab_virtues
from .creation_characteristics import cost as characteristic_cost
from .rounding import round_down, round_up

SOURCE = (
    "The Mysteries Revised Edition, Chapter Eight: Hermetic Spirit Magic, pp. 64-74"
)
THEURGY_SOURCE = (
    "The Mysteries Revised Edition, Chapter Nine: Hermetic Theurgy, pp. 75-88"
)
ERRATA_SOURCE = "Errata (Ars Magica 5th Edition), The Mysteries Revised Edition, p. 50"

# -- the Virtues these rules belong to --

HERMETIC_EMPOWERMENT = "vf_hermetic_empowerment"
SPIRIT_FAMILIAR = "vf_spirit_familiar"
INSCRIPTION_ON_THE_SOUL = "vf_inscription_on_the_soul"
LIVING_GHOST = "vf_living_ghost"
NAMES_OF_POWER = "vf_names_of_power"
INVOCATION_MAGIC = "vf_invocation_magic"
HERMETIC_THEURGY = "vf_hermetic_theurgy"
THEURGIC_SPIRIT_FAMILIAR = "vf_theurgic_spirit_familiar"
ASCENDANCY = "vf_ascendancy_to_the_hall_of_heroes"
HERMETIC_SYNTHEMATA = "vf_hermetic_synthemata"
SYNTHEMATA_MAGIA = "vf_synthemata_magia"
VIRTUES: tuple[str, ...] = (
    HERMETIC_EMPOWERMENT,
    SPIRIT_FAMILIAR,
    INSCRIPTION_ON_THE_SOUL,
    LIVING_GHOST,
    NAMES_OF_POWER,
    INVOCATION_MAGIC,
    HERMETIC_THEURGY,
    THEURGIC_SPIRIT_FAMILIAR,
    ASCENDANCY,
    HERMETIC_SYNTHEMATA,
    SYNTHEMATA_MAGIA,
)

#: A Ritual effect's least level (p. 65, after DE p. 114).
RITUAL_MINIMUM = 20
#: Might Score drained a use: a point per this many levels, rounded up.
DRAIN_DIVISOR = 5
SPIRIT_FAMILIAR_BASE = 25
#: Inscription on the Soul's opening (p. 69).
INSCRIPTION_PAWNS = 15
INSCRIPTION_MAGIC_THEORY = 8
#: A Blending with Substance effect this high is "high-power" (p. 70).
HIGH_POWER = 30
BIND_GHOST_BASE = 30
NAME_LEVEL_STEP = 5
#: Each level added to an Invoke spell for Penetration (p. 79).
PENETRATION_PER_LEVEL = 2
#: A spell spirit's casting succeeds this far under the level (p. 79).
SPELL_SPIRIT_MARGIN = 10
#: Varying the spell moves its level a magnitude (p. 79).
MAGNITUDE = 5
ASCENDANT_MINIMUM = 40
ASCENSION_STAMINA_EASE = 9
LASTING_SYNTHEMATA = 5
#: Might a Daimon spends for a Fatigue level (p. 86).
DAIMON_MIGHT_PER_FATIGUE = 5
#: Daimon Points for a point of Might Score, and x a Characteristic's
#: purchase cost for a point of it (p. 86).
DAIMON_POINTS_PER_MIGHT = 5
DAIMON_POINTS_PER_CHARACTERISTIC_COST = 10
#: The Hekate Cord's Might spent on one Stamina roll at most (p. 68).
HEKATE_MAX_MIGHT = 5


def held_virtues(character: Character) -> list[str]:
    """Which of these Mysteries' Virtues the character holds."""
    return [vf_id for vf_id in VIRTUES if lab_virtues.has(character, vf_id)]


def art_total(character: Character, art: str) -> int:
    """An Art's score with its Puissant bonus."""
    score, bonus = lab.art_score(character, art)
    return score + bonus


def _ability(character: Character, name: str) -> int:
    score, bonus = lab.ability_score(character, name)
    return score + bonus


def magic_theory(character: Character) -> int:
    return _ability(character, "Magic Theory")


# ---------------------------------------------------------------------------
# Hermetic Empowerment


def might_drained(ritual_level: int) -> int:
    """Might Score a use of a Ritual effect drains: level / 5, rounded up
    (p. 65)."""
    return round_up(max(RITUAL_MINIMUM, ritual_level) / DRAIN_DIVISOR)


def can_power(might: int, ritual_level: int) -> bool:
    """A spirit powers a Ritual effect while its Might x 2 at least equals
    the level (p. 65; Errata p. 50 on p. 66)."""
    return 2 * might >= max(RITUAL_MINIMUM, ritual_level)


def prison_level(might: int) -> int:
    """An Empowering Prison's least base level for a spirit of this Might
    (p. 66)."""
    return 2 * might


def prison_holds(base_level: int) -> int:
    """The greatest Might a Prison of this base level can hold."""
    return round_down(base_level / 2)


@dataclass(frozen=True)
class Drain:
    """One use of a Ritual effect from a bound spirit: whether it worked
    and the Might Score left."""

    level: int
    powered: bool
    might_left: int


def drain_uses(might: int, levels: Sequence[int]) -> list[Drain]:
    """Each use in turn: a use the spirit can't power fails and drains
    nothing (p. 66)."""
    uses = []
    for level in levels:
        if can_power(might, level):
            might -= might_drained(level)
            uses.append(Drain(level, True, might))
        else:
            uses.append(Drain(level, False, might))
    return uses


# ---------------------------------------------------------------------------
# Spirit Familiar


def spirit_familiar_level(might: int) -> int:
    """The bonding level: Might + 25 (p. 67)."""
    return SPIRIT_FAMILIAR_BASE + might


def bonding_aura(magus_modifier: int, spirit_modifier: int) -> int:
    """The worse of the two aura modifiers (p. 67)."""
    return min(magus_modifier, spirit_modifier)


def spirit_familiar_total(
    character: Character, technique: str, form: str, aura_modifier: int
) -> int:
    """Technique + Form + Intelligence + Magic Theory + aura modifier."""
    return (
        art_total(character, technique)
        + art_total(character, form)
        + character.characteristics.intelligence
        + magic_theory(character)
        + aura_modifier
    )


def bonding_vis(lab_total: int) -> int:
    """A pawn per 5 points of the Lab Total or fraction (p. 67; DE p. 275)."""
    return round_up(max(0, lab_total) / 5)


def familiar_pyramid_points(might: int) -> int:
    """Points to buy the spirit's Int, Per and Com: Might / 5 (p. 69)."""
    return round_down(max(0, might) / 5)


def hekate_bonus(hekate_cord: int, might_spent: int) -> int:
    """The Hekate Cord on a Stamina roll: its score for each Might point
    the familiar spends, 1 to 5 (p. 68)."""
    return hekate_cord * max(0, min(might_spent, HEKATE_MAX_MIGHT))


def daimon_familiar_vis(might: int) -> int:
    """A Daimon familiar's sacrifice: Might / 5 pawns, rounded up (p. 82)."""
    return round_up(max(0, might) / 5)


def daimon_rejects(technique_form: int, might: int) -> bool:
    """The rule of thumb: a bond of Technique + Form under twice its Might
    looks unworthy (p. 82)."""
    return technique_form < 2 * might


# ---------------------------------------------------------------------------
# Inscription on the Soul


def blending_level(bonuses: Sequence[int]) -> int:
    """Blending with Substance: (highest + the rest / 2, rounded up) x 5
    (p. 70)."""
    if not bonuses:
        return 0
    ordered = sorted(bonuses, reverse=True)
    return 5 * (ordered[0] + round_up(sum(ordered[1:]) / 2))


def blending_warping(level: int) -> int:
    """A Warping Point, and a second for a high-power effect (p. 70)."""
    return 2 if level >= HIGH_POWER else 1


# ---------------------------------------------------------------------------
# The best Arts (Living Ghost, Ascendancy)


def best_combination(character: Character, *, focus: bool = False) -> tuple[int, str]:
    """The best Technique + Form (Puissant Arts in), and which; a Magical
    Focus doubles the lower of the two (DE p. 241)."""
    best, named = 0, ""
    for technique in TECHNIQUES:
        for form in FORMS:
            te, fo = art_total(character, technique), art_total(character, form)
            total = te + fo + (min(te, fo) if focus else 0)
            if total > best:
                best, named = total, f"{technique} {form}"
    return best, named


# ---------------------------------------------------------------------------
# Living Ghost


def bind_ghost_level(size_levels: int) -> int:
    """Bind the Living Ghost: 30 + the levels added for the Haunt (p. 71)."""
    return BIND_GHOST_BASE + max(0, size_levels)


def ghost_might(ritual_level: int, size_levels: int, limit: int) -> int:
    """The Living Ghost's Might: the Transformation's level less the
    Haunt's levels, no more than the limit (p. 71)."""
    return max(0, min(ritual_level - size_levels, limit))


def ghost_problems(ritual_level: int, size_levels: int, limit: int) -> list[str]:
    said = []
    if ritual_level < limit:
        said.append(
            f"The Transformation must be at least level {limit}, his "
            "transformation limit."
        )
    if ritual_level - size_levels <= 0:
        said.append("The Haunt takes every level: no Might would be left.")
    return said


def familiar_joins_vis(bond_score: int) -> int:
    """A familiar sharing his Ordeal: bond score / 5 pawns, rounded up
    (pp. 73, 84)."""
    return round_up(max(0, bond_score) / 5)


def restored_might(current: int, spaces: int, cap: int) -> int:
    """Recasting the Transformation over unused talisman spaces: a point
    of Might Score a space, to the Ritual's cap (p. 74)."""
    return min(current + max(0, spaces), cap)


# ---------------------------------------------------------------------------
# Names of Power


def name_level(bonus: int) -> int:
    """A Name of Power spell's level: 5 x its bonus (p. 76)."""
    return NAME_LEVEL_STEP * bonus


def names_bonus(bonuses: Sequence[int], magic_theory_score: int) -> int:
    """The Names' bonuses together, no more than Magic Theory (pp. 76-78;
    Errata p. 50)."""
    return max(0, min(sum(bonuses), magic_theory_score))


def theurgic_lab_total(
    character: Character,
    technique: str,
    form: str,
    *,
    lore: str,
    aura_modifier: int,
    names: int = 0,
) -> int:
    """Technique + Form + Int + Magic Theory + aura + (Realm) Lore + the
    Names' bonus (limited by Magic Theory) (p. 79)."""
    return (
        art_total(character, technique)
        + art_total(character, form)
        + character.characteristics.intelligence
        + magic_theory(character)
        + aura_modifier
        + _ability(character, lore)
        + min(max(0, names), magic_theory(character))
    )


# ---------------------------------------------------------------------------
# Invoking spirits


def invoke_level(
    might: int, duration_levels: int = 0, penetration_levels: int = 0
) -> int:
    """An Invoke spell's level: the spirit's Might, plus what Duration and
    Penetration add (pp. 79-80)."""
    return might + max(0, duration_levels) + max(0, penetration_levels)


def invoke_penetration_bonus(penetration_levels: int) -> int:
    return PENETRATION_PER_LEVEL * max(0, penetration_levels)


@dataclass(frozen=True)
class SpiritCasting:
    """What an invoked spirit's power does: its Casting Total, the level it
    casts at, whether it works, and its Penetration."""

    casting_total: int
    level: int
    succeeds: bool
    penetration: int


def spell_spirit(
    might: int,
    power_level: int,
    aura_modifier: int,
    *,
    step: int = 0,
    penetration_levels: int = 0,
) -> SpiritCasting:
    """Invoke the Spirit of (spell): Might + aura, no die; it casts the
    power, moved a magnitude up or down by `step` (p. 79)."""
    total = might + aura_modifier
    level = max(0, power_level + MAGNITUDE * max(-1, min(step, 1)))
    return SpiritCasting(
        total,
        level,
        total >= level - SPELL_SPIRIT_MARGIN,
        total - level + invoke_penetration_bonus(penetration_levels),
    )


def spell_spirit_problem(might: int, power_level: int) -> str:
    if might < power_level:
        return (
            f"The spirit's Might ({might}) must at least equal the power's "
            f"level ({power_level})."
        )
    return ""


def form_spirit(might: int, aura_modifier: int, effect_level: int) -> SpiritCasting:
    """Invoke the Spirit of (Form): (Might + aura) / 2, rounded up, as a
    Spontaneous casting (p. 80)."""
    total = round_up((might + aura_modifier) / 2)
    return SpiritCasting(
        total, effect_level, total >= effect_level, total - effect_level
    )


@dataclass(frozen=True)
class Pact:
    """Invoke the Pact of (Daimon): points a casting, the castings needed,
    and whether one is enough."""

    points: int
    castings: int | None
    at_once: bool


def daimon_pact(level: int, might: int, gathered: int = 0) -> Pact:
    """Each penetrating casting gathers level - Might; the Aspect comes at
    the Daimon's Might in points; twice its Might calls it at once (p. 81)."""
    points = max(0, level - might)
    needed = max(0, might - gathered)
    castings = None if points <= 0 else round_up(needed / points)
    return Pact(points, castings, level >= 2 * might)


def daimon_points(level: int) -> int:
    """The Daimon's gain when called: the pact's level / 5, rounded up
    (p. 85)."""
    return round_up(max(0, level) / 5)


# ---------------------------------------------------------------------------
# Ascendancy to the Hall of Heroes


def ascendant_minimum(best: int) -> int:
    """The Ascendant Form's least level: his best Arts' total, and 40."""
    return max(best, ASCENDANT_MINIMUM)


def ascended_might(ascendant_level: int) -> int:
    """His Might as a Daimon: the Ascendant Form's level / 2 (p. 84)."""
    return round_down(ascendant_level / 2)


def negative_characteristics_cost(character: Character) -> int:
    """The pyramid cost of his negative Characteristics, positives ignored."""
    values = vars(character.characteristics).values()
    return sum(-characteristic_cost(v) for v in values if isinstance(v, int) and v < 0)


def transformation_needed(
    ascendant_level: int,
    negative_cost: int,
    decrepitude: int,
    virtue_points: int,
    flaw_points: int,
) -> int:
    """The Form's level + 3 x the negative Characteristics' cost + 5 x
    Decrepitude + 5 x the Flaw points when they exceed the Virtues'
    (p. 84)."""
    excessive = 5 * flaw_points if flaw_points > virtue_points else 0
    return ascendant_level + 3 * negative_cost + 5 * decrepitude + excessive


def transformation_points(transformation_level: int, ascendant_level: int) -> int:
    """A penetrating Transformation's points: its level less the Form's;
    it must exceed the Form's level (p. 84)."""
    return max(0, transformation_level - ascendant_level)


def ceremonies(needed: int, gathered: int, points: int) -> int | None:
    if points <= 0:
        return None
    return round_up(max(0, needed - gathered) / points)


# ---------------------------------------------------------------------------
# Synthemata


def typical_name_hiding(might: int) -> int:
    """A spirit that hides its name: about Might / 2 (p. 87)."""
    return round_down(max(0, might) / 2)


def synthemata_penetration(level: int, *, lasting: bool = False) -> int:
    """What a Synthemata spell adds to Penetration against its being: its
    level, or level - 5 for the Lasting version (p. 86)."""
    return max(0, level - (LASTING_SYNTHEMATA if lasting else 0))


def synthemata_least_level(might: int, *, lasting: bool = False) -> int:
    return might + (LASTING_SYNTHEMATA if lasting else 0)


def synthemata_lab_total(
    character: Character, *, lore: str, aura_modifier: int, bonuses: int = 0
) -> int:
    """Muto + Vim + Int + (Realm) Lore + aura + bonuses (p. 87)."""
    return (
        art_total(character, "Muto")
        + art_total(character, "Vim")
        + character.characteristics.intelligence
        + _ability(character, lore)
        + aura_modifier
        + bonuses
    )


def synthemata_points(lab_total: int, level: int, name_hiding: int) -> int:
    """Points a season: Lab Total - level - name hiding (p. 87)."""
    return max(0, lab_total - level - name_hiding)


def intuit_total(character: Character, lore: str, aura_modifier: int) -> int:
    """Synthemata Magia: Per + (Realm) Lore + his aura modifier (p. 88)."""
    return (
        character.characteristics.perception + _ability(character, lore) + aura_modifier
    )


def intuit_ease(might: int, spirit_aura_modifier: int, name_hiding: int) -> int:
    return might + spirit_aura_modifier + name_hiding


def hedge_lord_bonus(level: int) -> int:
    """The Hedge Lord's Synthemata: its level - 5 to his Casting Score
    against the being (p. 88)."""
    return max(0, level - LASTING_SYNTHEMATA)
