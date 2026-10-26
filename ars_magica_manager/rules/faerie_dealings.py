"""Dealing with faeries: fable and creativity in the Faerie Realm, and the
Ars Fabulosa, the bargaining powers (Realms of Power: Faerie pp. 25-29,
131-134; Errata p. 68 corrects none of these pages, only the book's
contents, whose numbers are 2 short).

- **Fable** (p. 26): in the Faerie Realm a human who plays along with a
  story gains fable points. The first makes a fable score of 1; raising
  it further costs (the score + 1) points. A fable point spent adds the
  fable score to one roll. All of it is lost on leaving Faerie, so the
  app keeps none of it: the forms take the score as it stands.
- **An offer** (pp. 27-29): a character with an unspent fable point may
  bargain with the Faerie Realm itself to change one element of the
  story: Communication + Charm, a Profession or a Craft (any Ability the
  creativity fits, Errata p. 68 on p. 65) + the offer's, the promise's
  and the change's modifiers + a stress die, against an Ease Factor set
  by the threat the change overcomes (Trivial 6 to Overwhelming 18). It
  costs a fable point and a Long-Term Fatigue level whether or not it is
  accepted. Only the highest of a Virtue's bonus (Free Expression +3, a
  Puissant Ability's) and the goods' (+1 to +3) counts; Art & Academe's
  artistic Reputation (+1 a 3 or part) and a Faerie Patron's Might (+1 a
  5 or part) add to it. Elysium takes 6 off, unless the offer puts an
  Elysian story back on track, when the Ease Factor is 3 less.
- **The Ars Fabulosa** (pp. 131-134): Summoning (Presence), Bonding
  (Communication), Captivating (Perception) and Dismissing
  (Intelligence), each + the power + Faerie Rank + the aura + a stress
  die, for a Fatigue level (no Summoning without one). Each reaches at
  most 5 x all the applicable Sympathy Traits added together, negatives
  as positive (their absolute total; rules.faerie_rites.max_summoned_might).
  Penetration adds only the single highest applicable Trait; the book
  says "highest" without saying how a negative one ranks, so taking it by
  size is the app's reading. Summoning holds the faerie only when the
  total equals or beats its Might (equal is enough here, unlike
  Penetration), a random faerie called at large too; only one he has an
  Arcane Connection to must also be penetrated (p. 132; p. 133's sidebar
  spares a random one). Bonding and
  Captivating must exceed its Might and penetrate, the Might counting as
  the effect's level unless a Summoning holds it (level 0). Dismissing
  must exceed the level of the effect it ends, or the Might of a being
  it frees from an agreement, and penetrate the same way.
- **Sympathy** (pp. 103, 131-132): a 1 on the stress die gives each
  applicable Trait an experience point and each botch die's 0 takes one
  away, beyond the Warping limit; for a negative Trait the effects are
  reversed, so a 1 lessens its penalty and a botch deepens it: either
  way a 1 moves the value up and a botch down. A negative Trait rises
  for 10, 15, 20 xp from -1, -2, -3 (p. 103). Losing a point with none
  banked lowers the Trait a step, its points toward the next value then
  all but one banked: the book doesn't say, so that is the app's
  assumption. A bargain struck in a summoning gives an applicable Trait an
  experience point, none struck takes one; the bargain binds the faerie,
  and a summoner who breaks it gains a -3 Sympathy Trait. A deadlocked
  bargain is settled by a contested Communication + Bargain + Faerie
  Rank, a fitting Trait as Bargain's specialty if he chooses;
  Intelligence + Faerie Lore against 12 or more works out what an
  unknown faerie wants (p. 133), a simple die like any Ability roll. A
  Sympathy Trait used as a specialty on either roll makes it a stress
  die that can botch, a botch giving Warping Points (p. 102). The book
  gives no rule for a tie in the contest: the app's assumption is that a
  tie strikes no bargain.

Penetration follows the Definitive Edition: the Penetration Total must
be greater than the Magic Resistance (DE p. 221). Bonding's and
Captivating's examples (pp. 133-134) let a total that only equals it
through; the DE wins. A faerie's Magic Resistance is its Might.

Pattern: plain functions over the character's Traits and Abilities, the
tables as dicts.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..models import SEASONS, Character, ScoredTrait
from . import faerie_rites, faerie_sympathy, penetration, realms
from .breakdown import Breakdown, Line
from .lab import ability_score
from .rounding import round_up

SOURCE = (
    "Realms of Power: Faerie, Vitality and Fable, Creativity in the Faerie "
    "Realm, pp. 25-29; Ars Fabulosa, pp. 131-134; Errata p. 68"
)
FABLE_SOURCE = "Realms of Power: Faerie, Vitality and Fable in Faerie, p. 26"
OFFER_SOURCE = "Realms of Power: Faerie, Creativity in the Faerie Realm, pp. 27-29"
ARS_SOURCE = "Realms of Power: Faerie, Ars Fabulosa, pp. 131-134"
BARGAIN_SOURCE = "Realms of Power: Faerie, Summoning and Faerie Bargains, pp. 132-133"
DE_PENETRATION = "Ars Magica Definitive Edition, Penetration, p. 221"

FAERIE = "Faerie"

# -- fable (p. 26) --


def fable_points_to_raise(score: int) -> int:
    """The fable points that raise a fable score by one: the score + 1
    (the first point makes a score of 1)."""
    return max(0, score) + 1


def fable_from_points(points: int) -> tuple[int, int]:
    """(the fable score, the points left over) from `points` gained in
    one visit, all spent on the score."""
    score, left = 0, max(0, points)
    while left >= fable_points_to_raise(score):
        left -= fable_points_to_raise(score)
        score += 1
    return score, left


# -- an offer to the Faerie Realm (pp. 27-29) --

#: The threat a change overcomes -> the Ease Factor (p. 27).
THREATS: dict[str, int] = {
    "Trivial": 6,
    "Minor": 9,
    "Serious": 12,
    "Major": 15,
    "Overwhelming": 18,
}
#: What is offered with it -> its modifier (p. 28).
GOODS: dict[str, int] = {
    "Nothing more": 0,
    "Minor mortal goods (bread, beer, milk, cheese, wine)": 1,
    "Mortal crafts (clothes, tools, ornaments)": 2,
    "Something highly desirable (vis, a human child)": 3,
}
FREE_EXPRESSION = "vf_free_expression"
FREE_EXPRESSION_BONUS = 3
#: The promise of service -> its modifier (p. 28).
PROMISES: dict[str, int] = {
    "Mundane actions overcome the threat": -6,
    "A series of simple symbolic actions": -3,
    "A conventional story": 0,
    "A cunning plan likely to fail": 3,
}
#: The change asked for -> its modifier (pp. 28-29).
CHANGES: dict[str, int] = {
    "An object becomes a tool against the threat": 3,
    "The immediate environment gives an advantage": 0,
    "A faerie's attitude (Personality Traits by up to 3)": -3,
    "A faerie's mind, comprehensively (Traits by up to 5)": -6,
    "A faerie's motif, to a strongly related one": -3,
    "A faerie's motif, to a tenuously related one": -6,
}
#: Where the story is told (p. 27).
REALM, ELYSIUM, RESTORING = "realm", "elysium", "restoring"
PLACES: dict[str, str] = {
    REALM: "The Faerie Realm",
    ELYSIUM: "Elysium",
    RESTORING: "Elysium, putting its story back on track",
}
ELYSIUM_PENALTY = -6
RESTORING_EASE = -3
#: Art & Academe's bonuses: a point a 3 of artistic Reputation, a point a
#: 5 of a Faerie Patron's Might, or part of one (p. 28).
REPUTATION_STEP, PATRON_STEP = 3, 5
#: The Abilities an offer is usually made with (pp. 27, 65).
OFFER_ABILITIES = ("Charm", "Profession", "Craft", "Music")


def offer_abilities(character: Character) -> list[str]:
    """His Abilities an offer may use: Charm, a Profession, a Craft or
    Music; Charm alone when he has none of them (at 0)."""
    held = [
        a.name
        for a in character.abilities
        if a.name.split(":")[0].strip() in OFFER_ABILITIES
    ]
    return held or ["Charm"]


def offer_ease_factor(threat: str, place: str = REALM) -> int:
    """The Ease Factor for overcoming `threat`, 3 less when the offer
    restores an Elysian story (p. 27)."""
    ease = THREATS[threat]
    return ease + (RESTORING_EASE if place == RESTORING else 0)


def has_free_expression(character: Character) -> bool:
    return any(vf.vf_id == FREE_EXPRESSION for vf in character.virtues_flaws)


@dataclass(frozen=True)
class Offer:
    """What an offer adds: the goods, the promise and the change; Art &
    Academe's figures; the place; and a further fable point spent."""

    ability: str
    goods: str = "Nothing more"
    promise: str = "A conventional story"
    change: str = "The immediate environment gives an advantage"
    place: str = REALM
    artistic_reputation: int = 0
    patron_might: int = 0
    fable_score: int = 1
    spend_fable: bool = False


def offer_total(character: Character, offer: Offer) -> Breakdown:
    """Communication + the Ability + the modifiers (pp. 27-28): the
    highest of a Virtue's bonus and the goods' counts once."""
    score, puissant = ability_score(character, offer.ability)
    source = OFFER_SOURCE
    lines = [
        Line(
            "Communication",
            amount=character.characteristics.communication,
            source=source,
        ),
        Line(offer.ability, amount=score, source=source),
    ]
    bonuses = [(GOODS[offer.goods], "Goods offered")]
    if puissant:
        bonuses.append((puissant, f"Puissant {offer.ability}"))
    if has_free_expression(character):
        bonuses.append((FREE_EXPRESSION_BONUS, "Free Expression"))
    best, label = max(bonuses)
    if best:
        lines.append(Line(f"{label} (the highest bonus)", amount=best, source=source))
    if offer.artistic_reputation > 0:
        lines.append(
            Line(
                "Artistic Reputation",
                amount=round_up(offer.artistic_reputation / REPUTATION_STEP),
                source=source,
            )
        )
    if offer.patron_might > 0:
        lines.append(
            Line(
                "A Faerie Patron's Might",
                amount=round_up(offer.patron_might / PATRON_STEP),
                source=source,
            )
        )
    lines.append(Line("Promise", amount=PROMISES[offer.promise], source=source))
    lines.append(Line("Change", amount=CHANGES[offer.change], source=source))
    if offer.place == ELYSIUM:
        lines.append(Line("Elysium", amount=ELYSIUM_PENALTY, source=source))
    if offer.spend_fable:
        lines.append(
            Line(
                "A further fable point",
                amount=max(0, offer.fable_score),
                source=FABLE_SOURCE,
            )
        )
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def offer_fable_cost(offer: Offer) -> int:
    """The fable points the offer spends: one, and one more for the
    bonus."""
    return 1 + (1 if offer.spend_fable else 0)


# -- the Ars Fabulosa (pp. 131-134) --

SUMMONING = "(Faerie) Summoning"
BONDING, CAPTIVATING, DISMISSING = "Bonding", "Captivating", "Dismissing"
#: Each power -> the Characteristic it adds.
POWERS: dict[str, str] = {
    SUMMONING: "Presence",
    BONDING: "Communication",
    CAPTIVATING: "Perception",
    DISMISSING: "Intelligence",
}
#: Dismissing's uses (p. 134).
CANCEL, END, RELEASE = "cancel", "end", "release"
DISMISSALS: dict[str, str] = {
    CANCEL: "Cancel an effect of a being's power",
    END: "End an effect on a being with Might",
    RELEASE: "Release a being from a supernatural agreement",
}
#: Each further effect dismissed in one round (p. 134).
MULTIPLE_PENALTY = -6
#: The Sympathy Trait a summoner who breaks a bargain gains (p. 132).
BROKEN_BARGAIN_TRAIT = -3
#: What working out an unknown faerie's wants needs, at least (p. 133).
WANTS_EASE = 12
#: The benefits a bond may give, one chosen as it is formed (p. 133).
BOND_BENEFITS = (
    "Share the faerie's Characteristics, Pretenses and senses",
    "Use the faerie's powers from its Might Points",
    "Hold one effect the bearer can cast, for both to use",
    "Immunity to Faerie-aura Warping, deprivation and Fatigue; Aging delayed",
)


def held_powers(character: Character) -> list[str]:
    """The Ars Fabulosa he holds (a score of 0 counts), in the book's
    order."""
    names = {a.name for a in character.abilities}
    return [power for power in POWERS if power in names]


def bargains(character: Character) -> bool:
    """Whether he holds any of the Ars Fabulosa."""
    return bool(held_powers(character))


def faerie_rank(character: Character) -> int:
    """His Faerie Rank, 0 with no lasting Sympathy Traits (p. 103)."""
    return faerie_sympathy.faerie_rank(character.personality_traits) or 0


def might_limit(applicable: Sequence[ScoredTrait]) -> int:
    """The highest Might (or effect level) the applicable Traits reach:
    5 x their sizes added up (pp. 131-134)."""
    return faerie_rites.max_summoned_might(faerie_rites.sympathy_points(applicable))


def best_trait(applicable: Sequence[ScoredTrait]) -> int:
    """The highest applicable Sympathy Trait by its size, for Penetration
    (pp. 132-134): the single highest, unlike might_limit's sum."""
    # The book says only "highest applicable Sympathy Trait"; ranking a
    # negative one by its size is the app's reading.
    return max((abs(t.score) for t in applicable), default=0)


def power_total(
    character: Character,
    power: str,
    *,
    aura: int = 0,
    aura_realm: str = realms.HERMETIC,
    dismissed: int = 1,
) -> Breakdown:
    """The power's total before the die: the Characteristic + the power +
    Faerie Rank + the aura; Dismissing several effects in a round takes 6
    off for each beyond the first."""
    score, puissant = ability_score(character, power)
    characteristic = POWERS[power]
    lines = [
        Line(power, amount=score + puissant, source=ARS_SOURCE),
        Line(
            characteristic,
            amount=getattr(character.characteristics, characteristic.lower()),
            source=ARS_SOURCE,
        ),
        Line("Faerie Rank", amount=faerie_rank(character), source=ARS_SOURCE),
        Line(
            f"Aura ({aura_realm} {aura})",
            amount=realms.aura_modifier(FAERIE, aura_realm, aura),
            source=realms.SOURCE,
        ),
    ]
    if power == DISMISSING and dismissed > 1:
        lines.append(
            Line(
                f"{dismissed} effects this round",
                amount=MULTIPLE_PENALTY * (dismissed - 1),
                source=ARS_SOURCE,
            )
        )
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def penetration_bonus(
    character: Character,
    applicable: Sequence[ScoredTrait],
    arcane_connection: str | None = None,
) -> Breakdown:
    """His Penetration bonus (an Arcane Connection multiplies it) + the
    highest applicable Sympathy Trait (p. 132)."""
    base = penetration.penetration_bonus(character, arcane_connection=arcane_connection)
    trait = best_trait(applicable)
    lines = [*base.lines]
    if trait:
        lines.append(
            Line("Highest applicable Sympathy Trait", amount=trait, source=ARS_SOURCE)
        )
    return Breakdown(total=base.total + trait, lines=lines)


@dataclass(frozen=True)
class Target:
    """What a use of a power works against: the being's Might (its Magic
    Resistance), the level of an effect Dismissing ends, whether a
    Summoning holds the being, and an Arcane Connection to it."""

    power: str
    might: int
    effect_level: int = 0
    dismissal: str = CANCEL
    held: bool = False
    connected: bool = False


def target_score(target: Target) -> int:
    """What the total is measured against: the Might, or for Dismissing an
    effect, the effect's level (pp. 132-134)."""
    if target.power == DISMISSING and target.dismissal != RELEASE:
        return target.effect_level
    return target.might


def reaches(target: Target, total: int) -> bool:
    """Whether the total is enough: Summoning equals the Might, the
    others exceed what they work against (pp. 132-134)."""
    needed = target_score(target)
    return total >= needed if target.power == SUMMONING else total > needed


def needs_penetration(target: Target) -> bool:
    """Whether the effect must penetrate: always, but for Summoning only
    a faerie he has an Arcane Connection to (pp. 132-133)."""
    return target.power != SUMMONING or target.connected


def penetration_level(target: Target) -> int:
    """The level taken off the Penetration Total: 0 for a being a
    Summoning holds, else what the total works against (pp. 133-134)."""
    if target.held and target.power != SUMMONING:
        return 0
    return target_score(target)


def penetration_needed(target: Target, bonus: int) -> int:
    """The least total that penetrates: Magic Resistance (the Might) + 1
    + the level, less the Penetration bonus (DE p. 221)."""
    return target.might + 1 + penetration_level(target) - bonus


def total_needed(target: Target, bonus: int) -> int:
    """The least total that works and, where it must, penetrates."""
    least = target_score(target) + (0 if target.power == SUMMONING else 1)
    if needs_penetration(target):
        least = max(least, penetration_needed(target, bonus))
    return least


def botch_dice(character: Character, aura: int, aura_realm: str) -> int:
    """One, the aura's of another realm, and the worst negative Sympathy
    Trait's (pp. 102, DE p. 227)."""
    return (
        1
        + realms.extra_botch_dice(FAERIE, aura_realm, aura)
        + faerie_sympathy.extra_botch_dice(character.personality_traits)
    )


@dataclass(frozen=True)
class Outcome:
    """What a roll did: whether it worked and penetrated, in words."""

    worked: bool
    penetrated: bool | None
    text: str


def outcome(
    target: Target, total: int, bonus: int, *, botched: bool = False
) -> Outcome:
    """What a total does against the target (pp. 132-134)."""
    pen = total + bonus - penetration_level(target)
    penetrated = (
        penetration.penetrates(pen, target.might) if needs_penetration(target) else None
    )
    worked = not botched and reaches(target, total) and penetrated is not False
    power = target.power
    if power == SUMMONING:
        if botched:
            text = (
                "Botched: a faerie comes all the same, hostile, unbound by any "
                "bargain, more or less powerful than meant, or not a faerie at all."
            )
        elif worked:
            text = (
                "A faerie comes and is held: it must attend and listen, and he "
                "is warded against its attacks and powers until either ends "
                "the summoning."
            )
        elif penetrated is False:
            text = (
                "It failed to penetrate: the faerie may ignore the summons, "
                "and one that comes is free of it."
            )
        else:
            text = (
                "A faerie comes but is not held: it may ignore him, attack him "
                "or leave at will, and he can't send it away."
            )
        return Outcome(worked, penetrated, text)
    if botched:
        return Outcome(False, penetrated, f"Botched: the {power} fails.")
    if not worked:
        why = (
            "it failed to penetrate"
            if penetrated is False and reaches(target, total)
            else f"the total must exceed {target_score(target)}"
        )
        return Outcome(False, penetrated, f"The {power} fails: {why}.")
    done = {
        BONDING: (
            "The bond is made, an Arcane Connection between the faerie and its "
            "bearer; one benefit is chosen now. A new bond ends the old."
        ),
        CAPTIVATING: (
            "He and the faerie change places; each keeps his Personality "
            "Traits and Confidence, and he his Sympathy Traits. His body gains "
            "a Warping Point a season and one a year; both are immune to "
            "Faerie Calling meanwhile."
        ),
        DISMISSING: {
            CANCEL: "The effect is cancelled.",
            END: "The effect on the being ends.",
            RELEASE: (
                "The being is freed from the agreement; he takes the debt "
                "upon himself, losing no Sympathy, though the faerie may "
                "resent it."
            ),
        }[target.dismissal],
    }[power]
    return Outcome(True, penetrated, done)


def captivating_warping(seasons: int) -> int:
    """The Warping Points his body gains while a faerie wears it: one a
    season and one more a year (p. 134)."""
    seasons = max(0, seasons)
    return seasons + seasons // len(SEASONS)


def deflect_total(character: Character, applicable: Sequence[ScoredTrait]) -> int:
    """Quickness + Finesse, + the highest applicable Trait if he has
    Finesse, to deflect a power before it acts (p. 134)."""
    score, puissant = ability_score(character, "Finesse")
    held = any(a.name == "Finesse" for a in character.abilities)
    return (
        character.characteristics.quickness
        + score
        + puissant
        + (best_trait(applicable) if held else 0)
    )


# -- a Sympathy Trait's experience (pp. 103, 131-132) --


def trait_experience(
    trait: ScoredTrait, xp: int, warping_score: int, *, limited: bool
) -> int:
    """Move a Sympathy Trait `xp` experience points toward a higher value
    (negative xp toward a lower one), keeping the points toward its next
    value on the trait; a raise stops at the Warping limit when `limited`
    (p. 103). Returns the change in its value."""
    before = trait.score
    trait.deeds += xp
    # Losing a point with none banked lowers the Trait a step: the book
    # says nothing of it, so this is the app's assumption.
    while trait.deeds < 0:
        trait.score -= 1
        trait.deeds += faerie_sympathy.xp_to_raise(trait.score)
    while trait.deeds >= faerie_sympathy.xp_to_raise(trait.score) and (
        not limited or faerie_sympathy.can_raise(trait.score, warping_score)
    ):
        trait.deeds -= faerie_sympathy.xp_to_raise(trait.score)
        trait.score += 1
    return trait.score - before


def die_experience(first_face: int, botches: int) -> int:
    """The experience a roll gives each applicable Trait toward a higher
    value: +1 for a 1 on the stress die, -1 for each botch die's 0 (pp.
    103, 131; for a negative Trait the same moves lessen and worsen the
    penalty)."""
    if botches:
        return -botches
    return 1 if first_face == 1 else 0


def experience_line(trait: ScoredTrait, xp: int, change: int) -> str:
    """A line for the Diary: what `xp` did to the Trait."""
    moved = f"{'+' if xp > 0 else ''}{xp} xp"
    after = (
        f", now {trait.score:+d}"
        if change
        else f", {trait.deeds} of {faerie_sympathy.xp_to_raise(trait.score)} "
        "toward the next value"
    )
    return f"{trait.name} {moved}{after}."


def break_bargain(character: Character, name: str) -> ScoredTrait:
    """A summoner breaks a bargain made in a summoning: he gains a -3
    Sympathy Trait fitting the faerie (p. 132)."""
    trait = ScoredTrait(name, BROKEN_BARGAIN_TRAIT, type=faerie_sympathy.SYMPATHY)
    character.personality_traits.append(trait)
    return trait


def specialty(applicable: Sequence[ScoredTrait]) -> int:
    """The best applicable positive Trait, used as an Ability's specialty
    in place of its +1; the Traits don't add together (p. 102)."""
    return max((t.score for t in applicable if t.score > 0), default=0)


def bargain_total(character: Character, applicable: Sequence[ScoredTrait] = ()) -> int:
    """Communication + Bargain + Faerie Rank, the best applicable positive
    Trait as Bargain's specialty when one is given (p. 133; p. 102)."""
    score, puissant = ability_score(character, "Bargain")
    return (
        character.characteristics.communication
        + score
        + puissant
        + faerie_rank(character)
        + specialty(applicable)
    )


def wants_total(character: Character, applicable: Sequence[ScoredTrait] = ()) -> int:
    """Intelligence + Faerie Lore, to work out what a faerie wants
    (p. 133), the best applicable positive Trait as its specialty when one
    is given (p. 102)."""
    score, puissant = ability_score(character, "Faerie Lore")
    return (
        character.characteristics.intelligence
        + score
        + puissant
        + specialty(applicable)
    )


def specialty_botch_dice(character: Character) -> int:
    """A roll with a Sympathy Trait as its specialty is a stress die: one
    botch die and the worst negative Sympathy Trait's (p. 102)."""
    return 1 + faerie_sympathy.extra_botch_dice(character.personality_traits)
