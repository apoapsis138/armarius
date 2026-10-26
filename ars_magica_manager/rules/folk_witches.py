"""The folk witches' kitchen, potions, Witch Moon and covens (Hedge Magic,
Revised Edition, Chapter Three: Folk Witches, pp. 33-54). Their casting
is the catalog's "Folk witch powers" rule (rules.hedge_casting); this
module holds the totals that are more than a casting rule.

The kitchen (pp. 38-42):

    Lab Total = the power's Ability + Int + Folk Witch Magic Theory + aura
                (no power for vis extraction or fixing an Arcane
                Connection; Expert Potion Brewer counts the power twice
                for a brew, p. 35)

- Brew Potency is the brew's Lab Total, + 1 for each witch helping at a
  sabbat (up to the Magic aura there, pp. 45-46). A dose drunk casts the
  effect with Brew Potency + a stress die against its Ease Factor, with
  no Penetration bonus and no aura; the potion must penetrate the
  drinker's Magic Resistance.
- A brew makes Folk Witch Magic Theory doses (+ a Lab Text's level), for
  a pawn of the power's Form each plus the effect's own cost, paid once.
  A season's vis is at most twice Folk Witch Magic Theory (four times
  with Concentrated Potions, p. 35).
- A potion that grants a power gives it at Brew Potency / 5, rounded up,
  for Brew Potency days (Animal Ken, Second Sight, Shapeshifter), one
  search (Dowsing) or one flight (Flight). To a magus a potion is an
  effect of magnitude Brew Potency / 5 (p. 42).
- Vis extraction: a tenth of the Lab Total (no power), rounded up, in
  pawns of Vim. Fixing an Arcane Connection: its lifetime steps up once
  along hours, days, weeks, months, years, decades (DE p. 219), to the
  Lab Total (no power) in the next unit, for a pawn of Vim.
- A kitchen takes 2 seasons and Folk Witch Magic Theory 3 to set up; a
  season and both Theories at 3 converts a Hermetic laboratory. With
  Covenants' laboratory rules it is 3 sizes larger than a Hermetic
  laboratory of its floor (p. 39).

The Witch Moon (pp. 42-43): each month, Stamina - Warping Score + a
stress die against 6 ends it; more months than her Warping Score make
the experience a bad one.

Covens (pp. 46-50): built as a covenant; each Initiation Script costs its
bonus in Build Points, and the coven's power level is set by its points.

Rounding where the book gives none is down (DE p. 6): the potion's
magnitude to a magus.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Character, Saga, TraditionDef
from . import hedge_casting as hc
from . import realms
from .lab_virtues import has
from .rounding import round_down, round_up

SOURCE = "Hedge Magic, Revised Edition, Folk Witches, pp. 33-54"
KITCHEN_SOURCE = "Hedge Magic, Revised Edition, Witch's Kitchen, pp. 38-42"
MOON_SOURCE = "Hedge Magic, Revised Edition, The Witch Moon, pp. 42-43"
COVEN_SOURCE = "Hedge Magic, Revised Edition, Covens, pp. 43-50"

TRADITION_ID = "trad_folk_witches"
THEORY = "Folk Witch Magic Theory"
LAB_RULE = "Folk witch Lab Total"
#: The kitchen's Lab Total with no power in it (vis, Arcane Connections).
PLAIN_LAB_RULE = "Folk witch Lab Total (no power)"

CONCENTRATED_POTIONS = "vf_concentrated_potions"
EXPERT_BREWER = "vf_expert_potion_brewer"
LIFE_LINKED = "vf_life_linked_folk_witch_magic"
PAINLESS_MOON = "vf_painless_moon"
HARSH_MOON = "vf_harsh_moon"
PRIMITIVE = "vf_primitive_tradition"

#: The Form of each power, which its potions and boosts spend (pp. 37-38);
#: Cursing's and Dowsing's depend on the curse or the thing sought.
POWER_FORMS: dict[str, str] = {
    "Animal Ken": "Animal",
    "Cursing": "Corpus, Mentem or Animal (by the curse)",
    "Dowsing": "the target's (Animal, Corpus, Vim...)",
    "Flight": "Auram",
    "Healing": "Corpus",
    "Second Sight": "Vim",
    "Shapeshifter": "Animal",
}
#: How each power is worked (p. 37): Incantation, Potion or Fetish.
POWER_METHODS: dict[str, tuple[str, ...]] = {
    "Animal Ken": ("Incantation", "Potion"),
    "Cursing": ("Fetish", "Potion"),
    "Dowsing": ("Fetish", "Potion"),
    "Flight": ("Fetish", "Potion"),
    "Healing": ("Incantation", "Potion"),
    "Second Sight": ("Incantation", "Potion"),
    "Shapeshifter": ("Fetish", "Potion"),
}
#: What a potion of each power grants, and for how long (p. 41).
POTION_LASTS: dict[str, str] = {
    "Animal Ken": "days",
    "Dowsing": "one search",
    "Flight": "one flight",
    "Second Sight": "days",
    "Shapeshifter": "days",
}
#: Healing's Ease Factors and their vis (p. 38): Ease Factor -> (the
#: wound and its pawns of Corpus, the Fatigue level and its pawns).
HEALING: dict[int, tuple[str, int, str, int]] = {
    6: ("Light Wound", 3, "Winded", 1),
    9: ("Medium Wound", 4, "Weary", 2),
    12: ("Heavy Wound", 5, "Tired", 3),
    15: ("Incapacitating Wound", 6, "Dazed", 4),
}
#: The fetishes a season in the kitchen enchants, and the vis each takes
#: (p. 40); a curse fabric needs an Arcane Connection instead.
FETISH_VIS: dict[str, str] = {
    "Dowsing": "Intellego",
    "Flight": "Auram",
    "Shapeshifter": "Animal",
}

INCANTATION_RECALL_EASE = 6
MARK_EASE = 9
MARK_TRADITION_EASE = 6
INVESTIGATE_EASE = 9
FLIGHT_EASE = 9
FAMILIAR_TRANCE_EASE = 6
TRANCE_BREAK_EASE = 9
FAMILIAR_DOWSING_EASE = 9
KITCHEN_SEASONS = 2
KITCHEN_THEORY = 3
CONVERT_SEASONS = 1
CONVERT_THEORY = 3
#: A kitchen is this many steps up Covenants' laboratory Size scale.
KITCHEN_SIZE_STEP = 3
MOON_EASE = 6
#: Life-Linked Folk Witch Magic: Casting Total per Fatigue level (p. 35).
LIFE_LINKED_BONUS = 5


def theory(character: Character) -> int:
    return hc.score(character, THEORY)


# ---------------------------------------------------------------------------
# Powers


def flight_combat_bonus(flight: int, *, opponent_flies: bool) -> int:
    """What a flying witch adds to her Attack and Defense Totals: her
    Flight score, unless her opponent can fly too (p. 38)."""
    return 0 if opponent_flies else flight


def flight_fatigue(*, fetish: bool, botches: int = 0) -> int:
    """Long-Term Fatigue levels a flight costs: one by fetish (even when
    the roll fails), none by potion, and one more for each botch (p. 38)."""
    return (1 if fetish else 0) + max(botches, 0)


def life_linked_bonus(character: Character, fatigue_levels: int) -> int:
    """+5 to a Casting Total a Fatigue level spent, with Life-Linked Folk
    Witch Magic (p. 35); 0 without it."""
    if not has(character, LIFE_LINKED):
        return 0
    return LIFE_LINKED_BONUS * max(fatigue_levels, 0)


def healing_vis(ease: int, *, fatigue: bool = False) -> int:
    """Pawns of Corpus vis a healing of `ease` costs (Animal vis on her
    familiar), a wound or a Fatigue level (p. 38)."""
    if ease not in HEALING:
        raise ValueError(f"No healing has Ease Factor {ease}; one of {list(HEALING)}")
    _, wound_vis, _, fatigue_vis = HEALING[ease]
    return fatigue_vis if fatigue else wound_vis


def mark_ease(*, which_witch: bool) -> int:
    """Perception + Organization Lore: Folk Witches against 9 knows whose
    mark an effect bears, against 6 only that a folk witch cast it (p. 37)."""
    return MARK_EASE if which_witch else MARK_TRADITION_EASE


# ---------------------------------------------------------------------------
# The kitchen


def plain_lab_total(
    character: Character,
    tradition: TraditionDef,
    *,
    aura: int = 0,
    aura_realm: str = realms.HERMETIC,
) -> int:
    """Int + Folk Witch Magic Theory + aura: the kitchen's Lab Total with
    no power in it (p. 38)."""
    value = character.characteristics.intelligence + theory(character)
    return value + hc.aura_modifier(tradition, aura, aura_realm)


def power_lab_total(
    character: Character,
    tradition: TraditionDef,
    power: str,
    *,
    aura: int = 0,
    aura_realm: str = realms.HERMETIC,
    brewing: bool = False,
) -> int:
    """A power's Lab Total: the power's score + Int + Folk Witch Magic
    Theory + aura, the power counted twice for a brew with Expert Potion
    Brewer (p. 35)."""
    times = 2 if brewing and has(character, EXPERT_BREWER) else 1
    return times * hc.score(character, power) + plain_lab_total(
        character, tradition, aura=aura, aura_realm=aura_realm
    )


def vis_limit(character: Character) -> int:
    """Pawns of vis she may use on a season's lab work: twice her Folk
    Witch Magic Theory, four times for a brew with Concentrated Potions
    (pp. 35, 39)."""
    times = 4 if has(character, CONCENTRATED_POTIONS) else 2
    return times * theory(character)


@dataclass(frozen=True)
class Brew:
    """A season's brew: its Brew Potency, the doses it can make, the vis
    they cost, and the most the season's vis allows."""

    potency: int
    doses: int
    vis: int
    vis_limit: int

    @property
    def affordable(self) -> int:
        """Doses the season's vis allows (all of them when it is enough):
        a pawn a dose once the effect's own cost is paid."""
        return max(min(self.doses, self.vis_limit - (self.vis - self.doses)), 0)


def brew(
    character: Character,
    tradition: TraditionDef,
    power: str,
    *,
    aura: int = 0,
    aura_realm: str = realms.HERMETIC,
    effect_vis: int = 0,
    lab_text_level: int = 0,
    sabbat_helpers: int = 0,
    sabbat_aura: int = 0,
    sabbat_realm: str = realms.HERMETIC,
) -> Brew:
    """What a season's brew of `power` makes (pp. 40, 45): Brew Potency
    is the power's Lab Total, + 1 a witch helping at a sabbat (each with
    the power, up to the Magic aura at the sabbat); Folk Witch Magic
    Theory doses + a Lab Text's level, at a pawn each + `effect_vis`
    (Healing's cost, paid once)."""
    potency = power_lab_total(
        character, tradition, power, aura=aura, aura_realm=aura_realm, brewing=True
    )
    if sabbat_helpers > 0:
        for group in tradition.groups:
            if "Brew Potency" in group.applies_to:
                potency += hc.group_bonus(
                    group,
                    [0] * sabbat_helpers,
                    aura=sabbat_aura,
                    aura_realm=sabbat_realm,
                )
                break
    doses = theory(character) + max(lab_text_level, 0)
    return Brew(potency, doses, doses + max(effect_vis, 0), vis_limit(character))


def potion_lab_text_level(character: Character) -> int:
    """A literate witch's potion Lab Text has her Folk Witch Magic Theory
    as its level (p. 40)."""
    return theory(character)


def potion_casting_total(potency: int, die: int) -> int:
    """A dose drunk: Brew Potency + a stress die; no aura (p. 40)."""
    return potency + die


def potion_penetration(potency: int, die: int, ease: int) -> int:
    """A dose's Penetration: its Casting Total - the Ease Factor, with no
    Penetration bonus from drinker or brewer (p. 40)."""
    return potion_casting_total(potency, die) - ease


def potion_works(potency: int, die: int, ease: int, resistance: int | None) -> bool:
    """Whether a dose takes effect: its total reaches the Ease Factor and
    penetrates the drinker's Magic Resistance (None: he has none, or
    lowers it)."""
    if potion_casting_total(potency, die) < ease:
        return False
    penetration = potion_penetration(potency, die, ease)
    return resistance is None or penetration > resistance


def potion_score(potency: int) -> int:
    """The power's score a potion grants: Brew Potency / 5, rounded up
    (p. 41)."""
    return round_up(max(potency, 0) / 5)


def potion_days(potency: int) -> int:
    """Days an Animal Ken, Second Sight or Shapeshifter potion lasts: the
    Brew Potency (p. 41)."""
    return max(potency, 0)


def potion_magnitude(potency: int) -> int:
    """The magnitude a potion shows to a magus's Intellego Vim: Brew
    Potency / 5 (p. 42)."""
    return round_down(max(potency, 0) / 5)


def investigation_total(character: Character, die: int) -> int:
    """Int + Folk Witch Magic Theory + a stress die, against 9, reveals a
    potion's Brew Potency and effect (p. 42)."""
    return character.characteristics.intelligence + theory(character) + die


def extracted_vis(plain_total: int) -> int:
    """Pawns of Vim a season's extraction gives: a tenth of the Lab Total
    with no power, rounded up (p. 39)."""
    return round_up(max(plain_total, 0) / 10)


#: An Arcane Connection's lifetimes, each a step up from the last (p. 39;
#: DE p. 219). Hours to days is a step, and the ladder tops out at decades:
#: "Indefinite" is the laboratory's fixed connections, not this step.
CONNECTION_STEPS = ("hours", "days", "weeks", "months", "years", "decades")


def fixed_connection(lifetime: str, plain_total: int) -> str:
    """A season fixing an Arcane Connection that lasts `lifetime` (hours,
    days... years): it then lasts the Lab Total with no power, as a number
    of the next unit up, counted from the season's end, for a pawn of Vim
    (p. 39). One lasting decades has no step left."""
    if lifetime not in CONNECTION_STEPS[:-1]:
        raise ValueError(
            f"Unknown lifetime {lifetime!r}; one of {CONNECTION_STEPS[:-1]}"
        )
    unit = CONNECTION_STEPS[CONNECTION_STEPS.index(lifetime) + 1]
    return f"{max(plain_total, 0)} {unit}"


def can_set_up_kitchen(character: Character) -> bool:
    """Two seasons set up a kitchen, with Folk Witch Magic Theory 3 (p. 39)."""
    return theory(character) >= KITCHEN_THEORY


def can_convert_laboratory(character: Character) -> bool:
    """A season turns a Hermetic laboratory into a kitchen, or back, with
    Folk Witch Magic Theory and Magic Theory both at 3 (p. 39)."""
    return (
        theory(character) >= CONVERT_THEORY
        and hc.score(character, "Magic Theory") >= CONVERT_THEORY
    )


def kitchen_size(hermetic_size: int) -> int:
    """A kitchen's Size on Covenants' laboratory scale: 3 more than a
    Hermetic laboratory of the same floor (p. 39)."""
    return hermetic_size + KITCHEN_SIZE_STEP


def familiar_binding_total(size: int, magic_might: int) -> int:
    """The Binding Total her Animal Ken Lab Total must exceed: 10 + the
    animal's Size + its Magic Might (p. 42)."""
    return 10 + size + max(magic_might, 0)


def binds_familiar(lab_total: int, size: int, magic_might: int) -> bool:
    return lab_total > familiar_binding_total(size, magic_might)


def familiar_lab_bonus(intelligence: int, familiar_theory: int) -> int:
    """What a familiar adds to her Lab Totals: its Intelligence + its Folk
    Witch Magic Theory (p. 42)."""
    return intelligence + familiar_theory


# ---------------------------------------------------------------------------
# The Witch Moon


def moon_total(character: Character, die: int) -> int:
    """Stamina - Warping Score + a stress die, against 6, ends the month's
    Witch Moon; wound penalties don't count (p. 43)."""
    return character.characteristics.stamina - character.aging.warping_score + die


def moon_ends(character: Character, die: int) -> bool:
    return moon_total(character, die) >= MOON_EASE


def moon_wound(character: Character) -> str:
    """The fever's wound each month: Medium, Heavy with Harsh Moon, none
    with Painless Moon (pp. 35, 42)."""
    if has(character, PAINLESS_MOON):
        return ""
    return "Heavy" if has(character, HARSH_MOON) else "Medium"


def moon_experience(months: int, warping_score: int) -> str:
    """ "good" when she recovered within as many months as her Warping
    Score, else "bad" (p. 43)."""
    return "bad" if months > warping_score else "good"


def moon_xp_gained(months: int) -> int:
    """Increased Knowledge: 5 xp a month in a Supernatural Ability or Folk
    Witch Magic Theory (p. 43)."""
    return 5 * max(months, 0)


def moon_xp_lost(warping_points: int) -> int:
    """Lost Knowledge: 2 xp a Warping Point the Moon gave (p. 43)."""
    return 2 * max(warping_points, 0)


# ---------------------------------------------------------------------------
# Covens


#: A coven's power level by its Build Points (p. 46): the least of each.
COVEN_POWER: tuple[tuple[int, str], ...] = (
    (600, "Legendary"),
    (300, "High"),
    (150, "Medium"),
    (0, "Low"),
)
#: A coven's one site has a Magic aura of 3 unless bought up; each further
#: site's aura is bought, a Minor Boon a point from 0 (p. 46).
COVEN_SITE_AURA = 3


def coven_power(build_points: int) -> str:
    for least, level in COVEN_POWER:
        if build_points >= least:
            return level
    return "Low"


def script_build_points(script_bonus: int) -> int:
    """An Initiation Script costs the coven its bonus in Build Points
    (p. 46)."""
    return max(script_bonus, 0)


# ---------------------------------------------------------------------------
# What a season in the kitchen yields (tradition_totals.SEASON_YIELDS)


def brew_yields(saga: Saga, character: Character, total: int) -> list[str]:
    """A brew season's Brew Potency, doses and vis limit."""
    lines = [
        f"Brew Potency {total}"
        + (
            " (Expert Potion Brewer: the power counts twice)"
            if has(character, EXPERT_BREWER)
            else ""
        )
        + f"; a dose casts at {total} + a stress die, no aura or Penetration "
        "bonus.",
        f"{theory(character)} doses (+ a Lab Text's level), a pawn of the "
        f"power's Form each + the effect's own vis; at most "
        f"{vis_limit(character)} pawns this season.",
        f"A potion that grants a power gives it at {potion_score(total)}, "
        f"for {potion_days(total)} days (one search for Dowsing, one flight "
        "for Flight).",
    ]
    if has(character, PRIMITIVE):
        lines.append("Primitive Tradition: she can't brew potions.")
    return lines


def extraction_yields(saga: Saga, character: Character, total: int) -> list[str]:
    return [f"{extracted_vis(total)} pawns of Vim vis from the aura."]


def connection_yields(saga: Saga, character: Character, total: int) -> list[str]:
    return [
        f"One Arcane Connection lasts {total} of its next unit up (weeks to "
        "months, months to years), from the season's end; a pawn of Vim."
    ]
