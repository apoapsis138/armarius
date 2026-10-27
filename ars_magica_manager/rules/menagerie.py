"""A Menagerie of magical beasts (Hermetic Projects pp. 119-142; errata
pp. 81-82 reprints p. 123's insert without changing its rules).

- **Upkeep** (p. 123): a beast costs Inhabitants points as a horse (Size
  +3) costs 1: each Size smaller doubles how many cost 1 point (two Size
  +2, four Size +1, eight Size 0), each Size larger doubles the points
  (Size +4 costs 2, +5 4); a carnivore costs double (twelve wolves of Size
  0 cost 3).
- **Realia** (p. 123): a menagerie studied counts its breeds, not its
  beasts, as a tractatus's Quality, usually in Magic Lore; its collector
  cannot study it.
- **Acclimation** (p. 119; Realms of Power: Magic p. 53): a beast always
  within an aura keeps its Might only if the aura is at least its Might /
  5, rounded up (rules.magic_build.aura_needed). An enchanted brand that
  is always working may help (p. 130).
- **A young beast's Might** (p. 134): the grown beast's divided by the
  years it takes to grow (five for most), until it is grown. HP gives no
  rounding, so the default rounds down (DE p. 6), but a magical beast
  keeps at least 1.
- **Staff** (p. 136): a handler tends 10 domesticated herbivores for each
  point of Animal Handling; half as many carnivores, a fifth as many wild
  beasts.
- **Brands** (p. 130): a brand is a device of material 2, x2 for a palm's
  size, x3 a haunch, x4 the whole back.
- **Breeding Roll** (pp. 140-141, the optional rules): stress die +
  modifiers against 9. Adequate diet +1, inadequate -2; agreeable
  environment +1, unsatisfactory -2; an appropriate Hermetic spell +1 per
  2 magnitudes; carnivore -1, herbivore +1; the lead handler's Animal
  Handling / 5 and Magic Lore / 5, each rounded up; a magical creature -
  its Might in magnitudes; the only beast of its kind besides its mate
  -3 (a kind, such as lions or horses, of any breed: p. 131); similar animals near +1; tamed +3; aggressive - Ferocity. A botch:
  one of the pair escapes (one botch), is sterile (two), is hurt mating
  (three or more). Each young is male on an even simple die.
- **The offspring roll** (pp. 141-142): stress die + diet, environment, a
  spell +1 a magnitude and a ligature +1 to +3 (Art & Academe p. 68).
  For the best: a botch a Major Supernatural Flaw or Inferiority, 0 a
  Minor one, 1-3 weak (Stamina -1), 4-12 like its parents, 13-15 hardy
  (Stamina +1), 16-17 a Minor Supernatural Virtue or Quality, 18+ a Major
  one. For the beast: a botch dies in days, 0 weaker than its sire, 1-12
  like its sire, 13 like its dam (a daughter then gives +3 to her own
  crossbreeding), 14 its sire's with a Minor Virtue or Quality of its
  dam's, 15+ a Major one.
- **Birth** (p. 134; Art & Academe pp. 62-63): the dam rolls as for a
  Medium Wound every two hours (Size 0 or less; doubled for each Size
  above), a handler adding his Animal Handling; hatchlings roll Stamina +
  Survival + stress die against 9. The app notes it; it is played out.
- **Reputation** (p. 138): its owner's, built by experience points the
  storyguide awards (1 for ten visitors, a magnitude of a captured
  beast's Might, a year past the first, a beast sold)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction

from ..models import Character, Covenant, Saga
from ..models.character import Progress
from ..models.hermetic_projects import HermeticProject
from ..models.menagerie import (
    BEAST,
    BEST,
    CARNIVORE,
    FEMALE,
    HERBIVORE,
    MALE,
    MENAGERIE,
    TRANSFORMED,
    Beast,
)
from .creature_build import magnitude
from .magic_build import aura_needed
from .rounding import round_down, round_up
from .scores import ability_level

SOURCE = "Hermetic Projects, The Menagerie of Magical Beasts, pp. 119-142"
HP = "Hermetic Projects"
ANIMAL_HANDLING = "Animal Handling"
MAGIC_LORE = "Magic Lore"

#: A horse, the Size that costs 1 Inhabitants point (p. 123).
HORSE_SIZE = 3
#: Domesticated herbivores a handler tends per point of Animal Handling,
#: and how much harder carnivores and wild beasts are (p. 136).
TEND_PER_POINT = 10
CARNIVORE_LOAD = 2
WILD_LOAD = 5
#: A brand's material, and its size multiplier by where it is (p. 130).
BRAND_MATERIAL = 2
BRAND_SIZES: dict[str, int] = {"palm": 2, "haunch": 3, "back": 4}
#: The Breeding Roll's Ease Factor (p. 140).
BREEDING_EASE = 9
TAMED_BONUS = 3
ONLY_PAIR = -3
#: What a botched Breeding Roll does, by botches (p. 140).
BREEDING_BOTCHES: tuple[str, ...] = (
    "one of the pair escapes",
    "one of the pair is sterile",
    "one of the pair is hurt mating, or worse",
)
#: A crossbred dam like her own dam adds this to her crossbreeding
#: (p. 142).
CROSS_BONUS = 3
LIGATURE_CAP = 3


# -- the beasts ----------------------------------------------------------------


def is_young(beast: Beast, year: int) -> bool:
    """Whether a beast born in the menagerie is still growing."""
    return beast.born is not None and year - beast.born < max(1, beast.maturity)


def might_now(beast: Beast, year: int) -> int:
    """Its Magic Might this year: a young beast's is the grown Might
    divided by its years to grow, at least 1 (p. 134)."""
    if not is_young(beast, year) or beast.might <= 0:
        return beast.might
    return max(1, round_down(beast.might / max(1, beast.maturity)))


def might_magnitudes(might: int) -> int:
    """A Might in magnitudes (a fifth, rounded up); 0 for none."""
    return magnitude(might) if might > 0 else 0


def is_magical(beast: Beast) -> bool:
    """A beast with Magic Might (a Transformed Animal has none, p. 124)."""
    return beast.kind != TRANSFORMED and beast.might > 0


def inhabitant_points(beast: Beast) -> Fraction:
    """The Inhabitants points the row's beasts cost (p. 123)."""
    each = Fraction(2) ** (beast.size - HORSE_SIZE)
    if beast.diet == CARNIVORE:
        each *= 2
    return each * beast.count


def upkeep(project: HermeticProject) -> int:
    """The menagerie's Inhabitants points: its beasts', the total rounded
    up (a pack's fractions share points, as twelve wolves cost 3)."""
    total = sum((inhabitant_points(b) for b in project.beasts), Fraction(0))
    # Halvings and doublings of 1 are exact as a float.
    return round_up(float(total))


def covenant_upkeep(covenant: Covenant) -> int:
    """The Inhabitants points of all the covenant's menageries."""
    return sum(upkeep(p) for p in covenant.hermetic_projects if p.kind == MENAGERIE)


def head_count(project: HermeticProject) -> int:
    return sum(b.count for b in project.beasts)


def handlers(saga: Saga, project: HermeticProject) -> list[Character]:
    found = [saga.character(i) for i in project.handler_ids]
    return [c for c in found if c is not None]


def can_tend(saga: Saga, project: HermeticProject) -> int:
    """How many domesticated herbivores its handlers can tend: 10 for each
    point of their Animal Handling (p. 136)."""
    return TEND_PER_POINT * sum(
        ability_level(c, ANIMAL_HANDLING) for c in handlers(saga, project)
    )


def tending_load(saga: Saga, beast: Beast) -> int:
    """The row's beasts as domesticated herbivores to tend: a carnivore
    counts 2, a wild beast 5 times as much (p. 136)."""
    load = beast.count
    if beast.diet == CARNIVORE:
        load *= CARNIVORE_LOAD
    if not is_tamed(saga, beast):
        load *= WILD_LOAD
    return load


def load(saga: Saga, project: HermeticProject) -> int:
    return sum(tending_load(saga, b) for b in project.beasts)


def acclimation(beast: Beast, aura: int, year: int) -> int | None:
    """The Magic aura a beast always within it needs to avoid Acclimation
    (RoP: Magic p. 53), when its own aura is weaker; None when it is
    strong enough or the beast has no Might. 0 when no aura will do."""
    if not is_magical(beast):
        return None
    always, _half, _frequent = aura_needed(might_now(beast, year))
    if always is None:
        return 0
    return always if aura < always else None


def breeds(project: HermeticProject) -> list[str]:
    """The menagerie's breeds of magical beast, each once (p. 123): a
    beast's breed, else its name."""
    seen: dict[str, str] = {}
    for beast in project.beasts:
        if is_magical(beast):
            name = (beast.breed or beast.name).strip()
            if name:
                seen.setdefault(name.casefold(), name)
    return list(seen.values())


def realia_quality(project: HermeticProject) -> int:
    """The menagerie studied as realia: a tractatus of Quality its breeds
    (p. 123)."""
    return len(breeds(project))


def brand_material(where: str) -> int:
    """A brand's material score, 2 x its size (p. 130); 0 for an unknown
    place."""
    return BRAND_MATERIAL * BRAND_SIZES.get(where, 0)


# -- taming --------------------------------------------------------------------


def taming_record(saga: Saga, beast: Beast) -> Progress | None:
    """The tamer's progress toward taming the beast (kept by name, as a
    taming season keeps it)."""
    tamer = saga.character(beast.tamer_id) if beast.tamer_id else None
    if tamer is None:
        return None
    return next(
        (p for p in tamer.progress if p.kind == "taming" and p.name == beast.name),
        None,
    )


def is_tamed(saga: Saga, beast: Beast) -> bool:
    """Tamed by hand, or by a finished taming of its tamer's."""
    if beast.tamed:
        return True
    record = taming_record(saga, beast)
    return record is not None and record.done


def taming_might(beast: Beast, year: int) -> int:
    """The points that tame it: its Might now, at least 1 (DE p. 384); a
    young beast is the easier to tame (p. 134)."""
    return max(1, might_now(beast, year))


@dataclass(frozen=True)
class State:
    """A beast's state in a word or two, and the theme colour that tones
    it."""

    words: str
    tone: str


def state(saga: Saga, beast: Beast, year: int) -> State:
    """Tamed, Taming (its points so far), Young or Wild."""
    young = is_young(beast, year)
    if is_tamed(saga, beast):
        return State("Tamed, young" if young else "Tamed", "text-success")
    record = taming_record(saga, beast)
    if record is not None and record.points:
        return State(
            f"Taming: {record.points} of {taming_might(beast, year)}", "text-warning"
        )
    if young:
        return State("Young", "text-success")
    return State("Wild", "text-warning")


# -- breeding ------------------------------------------------------------------


@dataclass(frozen=True)
class Conditions:
    """What the storyguide judges of a season's breeding (p. 140): the
    diet and the environment (+1, 0 or -2 each), an appropriate spell's
    magnitudes, similar animals near, the pair the only ones of their
    kind, a ligature (+1 to +3, the offspring roll only), the lead
    handler."""

    diet: int = 0
    environment: int = 0
    spell: int = 0
    similar: bool = False
    only_pair: bool = False
    ligature: int = 0
    handler: Character | None = None


def animal_of(beast: Beast) -> str:
    """A beast's kind of animal, to compare (p. 131: a kind, such as lions
    or horses, holds several breeds): its animal, else its breed, else its
    name."""
    return (beast.animal or beast.breed or beast.name).strip().casefold()


def only_of_kind(project: HermeticProject, sire: Beast, dam: Beast) -> bool:
    """Whether the pair are the only beasts of their kind in the
    menagerie, of any breed (p. 141), counting each row's beasts."""
    kind = animal_of(sire)
    others = sum(
        b.count for b in project.beasts if animal_of(b) == kind and b not in (sire, dam)
    )
    rows = [b for b in (sire, dam) if b.count > 1]
    return not others and not rows


def breeding_modifiers(
    saga: Saga, sire: Beast, dam: Beast, conditions: Conditions, year: int
) -> list[tuple[str, int]]:
    """The Breeding Roll's modifiers, each with its words (pp. 140-141)."""
    mods: list[tuple[str, int]] = []
    if conditions.diet:
        mods.append(
            (
                "adequate diet" if conditions.diet > 0 else "inadequate diet",
                conditions.diet,
            )
        )
    if conditions.environment:
        mods.append(
            (
                "agreeable environment"
                if conditions.environment > 0
                else "unsatisfactory environment",
                conditions.environment,
            )
        )
    if conditions.spell // 2:
        mods.append(("a Hermetic spell", conditions.spell // 2))
    if CARNIVORE in (sire.diet, dam.diet):
        mods.append(("carnivore", -1))
    else:
        mods.append(("herbivore", 1))
    if conditions.handler is not None:
        name = conditions.handler.name
        handling = ability_level(conditions.handler, ANIMAL_HANDLING)
        lore = ability_level(conditions.handler, MAGIC_LORE)
        if handling:
            mods.append(
                (f"{name}'s Animal Handling {handling} / 5", round_up(handling / 5))
            )
        if lore:
            mods.append((f"{name}'s Magic Lore {lore} / 5", round_up(lore / 5)))
    might = max(might_now(sire, year), might_now(dam, year))
    if might > 0:
        mods.append((f"magical, Might {might}", -might_magnitudes(might)))
    if conditions.only_pair:
        mods.append(("the only pair of its kind", ONLY_PAIR))
    if conditions.similar:
        mods.append(("similar animals near", 1))
    if is_tamed(saga, sire) and is_tamed(saga, dam):
        mods.append(("tamed", TAMED_BONUS))
    ferocity = max(sire.ferocity, dam.ferocity)
    if ferocity:
        mods.append((f"aggressive, Ferocity {ferocity}", -ferocity))
    return mods


def breeding_botch(botches: int) -> str:
    """What a botched Breeding Roll does (p. 140)."""
    return BREEDING_BOTCHES[min(max(botches, 1), len(BREEDING_BOTCHES)) - 1]


def offspring_modifiers(
    dam: Beast, aim: str, conditions: Conditions
) -> list[tuple[str, int]]:
    """The offspring roll's modifiers, of the dam's gestation (p. 142)."""
    mods: list[tuple[str, int]] = []
    if conditions.diet:
        mods.append(("diet", conditions.diet))
    if conditions.environment:
        mods.append(("environment", conditions.environment))
    if conditions.spell:
        mods.append(("a Hermetic spell", conditions.spell))
    ligature = max(0, min(LIGATURE_CAP, conditions.ligature))
    if ligature:
        mods.append(("a ligature", ligature))
    if aim == BEAST and dam.cross_bonus:
        mods.append((f"{dam.name}, a crossbred dam", CROSS_BONUS))
    return mods


@dataclass(frozen=True)
class Inherited:
    """What the offspring roll gives the young: its words, its tone, the
    Stamina change, and whether the young dies or (for the beast)
    resembles its dam."""

    words: str
    tone: str = "label"
    stamina: int = 0
    dies: bool = False
    like_dam: bool = False


def for_the_best(total: int, botched: bool) -> Inherited:
    """Breeding for the best (p. 141)."""
    if botched:
        return Inherited(
            "a Major Supernatural Flaw or Magical Inferiority", "text-error"
        )
    if total <= 0:
        return Inherited(
            "a Minor Supernatural Flaw or Magical Inferiority", "text-warning"
        )
    if total <= 3:
        return Inherited("weak (Stamina -1)", "text-warning", stamina=-1)
    if total <= 12:
        return Inherited("like its parents")
    if total <= 15:
        return Inherited("exceptionally hardy (Stamina +1)", "text-success", stamina=1)
    if total <= 17:
        return Inherited(
            "a Minor Supernatural Virtue or Magical Quality", "text-success"
        )
    return Inherited("a Major Supernatural Virtue or Magical Quality", "text-success")


def for_the_beast(total: int, botched: bool) -> Inherited:
    """Breeding for the beast (p. 142)."""
    if botched:
        return Inherited("dies days after its birth", "text-error", dies=True)
    if total <= 0:
        return Inherited(
            "weaker than its sire (less Stamina, or a power costing more)",
            "text-warning",
        )
    if total <= 12:
        return Inherited("like its sire")
    if total == 13:
        return Inherited(
            "like its dam (a daughter gives +3 to her own crossbreeding)",
            "text-success",
            like_dam=True,
        )
    if total == 14:
        return Inherited(
            "like its sire, with a Minor Virtue or Quality of its dam's",
            "text-success",
        )
    return Inherited(
        "like its sire, with a Major Virtue or Quality of its dam's", "text-success"
    )


def inherited(aim: str, total: int, botched: bool) -> Inherited | None:
    if aim == BEST:
        return for_the_best(total, botched)
    if aim == BEAST:
        return for_the_beast(total, botched)
    return None


def young_sex(die: int) -> str:
    """A young's sex: male on an even simple die (p. 140)."""
    return MALE if die % 2 == 0 else FEMALE


def total_of(mods: Sequence[tuple[str, int]]) -> int:
    return sum(n for _words, n in mods)


def birth_interval(size: int) -> int:
    """Hours between the dam's recovery rolls in labour: 2 for Size 0 or
    less, doubled for each Size above (p. 134)."""
    return 2 * 2 ** max(0, size)


def is_herbivore(beast: Beast) -> bool:
    return beast.diet == HERBIVORE


# -- the owner's Reputation (p. 138) -------------------------------------------

#: The book's suggested awards, which the storyguide fine-tunes: a point for
#: ten visitors, a magnitude of a captured beast's Might, a year past the
#: first, a beast sold to another magus.
VISITORS_PER_POINT = 10


def reputation_award(
    visitors: int, mights: Sequence[int], another_year: bool, sold: int
) -> int:
    """The year's Reputation experience for the menagerie's owner."""
    captured = sum(magnitude(m) for m in mights if m > 0)
    return (
        max(0, visitors) // VISITORS_PER_POINT
        + captured
        + (1 if another_year else 0)
        + max(0, sold)
    )
