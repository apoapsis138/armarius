"""Vis by the book: the kinds of raw vis beyond the ordinary, storing a
great deal of it in one place, and how magic creatures use vis and auras.

Raw vis is always of one Art, in matter that suits it; moving it to
another physical form in a laboratory changes the matter, never the Art
(DE pp. 212, 250). The supplements add kinds of vis, a plain
`Possession.vis_kind` on a Vis Source or Raw Vis Store (VIS_KINDS):

- Extraordinary vis (Realms of Power: Magic pp. 119-122) carries a power
  of the place that made it. Lesser enchantment vis works like a lesser
  enchantment (usually level 30 or less) without being used up; spell-like
  vis mimics a spell (usually level 60 or less) on its trigger and is used
  up when it works. Either can still be spent as ordinary vis, which ends
  the power; moving it to another form destroys the power. A guideline
  is a pawn for every 10 levels of its power (p. 120).
- Dedicated vis (pp. 122-123) is of one Technique and one Form together
  and can't be split. Used for that pair it is twice as effective: +4 a
  pawn in casting, each pawn counts as two toward a Ritual's or an
  enchantment's pawns, and its botch dice count double. With only one of
  the two Arts it is ordinary vis. Studied, each pawn counts as two toward
  the pawns needed; the Source Quality for both Arts is (stress die +
  aura) / 2, and the botch dice are twice its pawns (a magus may study
  ordinary vis with it, a pawn of dedicated for each ordinary pawn, at the
  same halved quality). Enchanted in its own form, it doubles the Shape
  and Material bonus (which may then pass Magic Theory), and its pawns
  count as already opened.
- Herbs and Objects of Virtue (pp. 124-128; formed stones are Objects of
  Virtue) hold 1 or 2 pawns. Anyone with Magic Lore may learn a Thing's
  powers (Intelligence + Magic Lore against 9) and Enrich it: a season,
  Enrichment Total Intelligence + Magic Lore + aura against 9. Enriched,
  it is no longer vis; carried by someone with no Magic Resistance it
  gives a Virtue (an Herb a Major Virtue with a Minor Flaw, lasting a year
  a pawn; an Object a Minor Virtue that lasts) and Warps as a constant
  effect of low power; an Aegis suppresses it. A magus benefits only
  from one he Enriched and made his talisman.
- Faerie vis (Realms of Power: Faerie pp. 18-19): encased (Magic vis
  under a faerie's glamour), anchored (the core of a faerie's body:
  harvesting it destroys the faerie, and a new one takes its role),
  accrued (left when faeries end their roles, may keep Pretenses),
  sleeping (a dormant glamour that may wake as a faerie) and abstract (a
  promise made solid: it holds no real vis, and magi can't use it). Magi
  don't usually tell faerie vis apart, so all but abstract vis serve as
  ordinary vis.

The trade value of extraordinary or dedicated vis is its Build Points /
5 ordinary pawns, and a new covenant pays for such a source (p. 124):
lesser enchantment 5 + 0-2 Build Points a magnitude of its power,
spell-like 5 + 1-3, dedicated 7.5, each a pawn a year; vis stocks a fifth
of the source's cost for every 5 pawns. The app takes the middle of each
range.

Vis storage (RoP: Magic pp. 123-124, the storyguide's option): enough
vis of one Art kept together causes spontaneous spells of that Art within
Voice range, of one magnitude at the least amount (a rook or two in a
low-vis saga, a queen in a high-vis one) and one more for each multiple
of it; or one harmless effect of the Art (STORAGE_EFFECTS).

Magic creatures (RoP: Magic p. 30): resting in a Magic aura, a character
with Magic Might regains its whole Might Pool in the time the chart gives
for aura - Might / 5 (0: 24 hours ... 9: 2 minutes), a point every that
time / Might. (The vis it eats against Acclimation, p. 54, is
rules.magic_build's.)

The Errata has no corrections to these pages (its Rosemary Sprig of Rego
Vis, RoP: Magic p. 121, is an example the app doesn't list).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .. import sourcebooks
from ..arts import TECHNIQUES
from ..models import Character, Possession, Saga
from ..models.holdings import VIS_KINDS
from .breakdown import Breakdown, Line
from .lab import ability_score
from .rounding import round_down, round_up

SOURCE = (
    "Realms of Power: Magic, Chapter Eight: Magic Things, Vis and Herbs and "
    "Objects of Virtue, pp. 119-128; Realms of Power: Faerie, Vis, pp. 18-19; "
    "Ars Magica Definitive Edition, Raw Vis and Vis Transfer, pp. 212, 250"
)
CREATURE_SOURCE = "Realms of Power: Magic, Auras and Might Recovery, p. 30"
MAGIC, FAERIE = "RoP:M", "RoP:F"

ORDINARY = ""
LESSER_ENCHANTMENT = "lesser_enchantment"
SPELL_LIKE = "spell_like"
DEDICATED = "dedicated"
HERB_OF_VIRTUE = "herb_of_virtue"
OBJECT_OF_VIRTUE = "object_of_virtue"
ENCASED = "encased"
ANCHOR = "anchor"
ACCRUED = "accrued"
SLEEPING = "sleeping"
ABSTRACT = "abstract"

EXTRAORDINARY = (LESSER_ENCHANTMENT, SPELL_LIKE)
THINGS = (HERB_OF_VIRTUE, OBJECT_OF_VIRTUE)


@dataclass(frozen=True)
class VisKind:
    key: str
    label: str
    #: The book it comes from (a sourcebooks abbreviation; "" the core book).
    book: str
    #: What it does, in a line, with its page.
    note: str
    #: Spent as vis or moved to another form, it loses what makes it special.
    special: bool = True
    #: A magus can spend it as vis at all.
    usable: bool = True
    #: Build Points a pawn a year of such a source, before its power
    #: (RoP: Magic p. 124), and the middle of the range added for each
    #: magnitude of its power.
    build_points: float = 5
    per_magnitude: float = 0


KINDS: tuple[VisKind, ...] = (
    VisKind(ORDINARY, "Ordinary vis", "", "Raw vis of its Art (DE p. 212).", False),
    VisKind(
        LESSER_ENCHANTMENT,
        "Extraordinary: lesser enchantment",
        MAGIC,
        "Works like a lesser enchantment without being used up; spending it "
        "as vis, or moving it to another form, ends the power (RoP: Magic "
        "pp. 119-120).",
        per_magnitude=1,
    ),
    VisKind(
        SPELL_LIKE,
        "Extraordinary: spell-like",
        MAGIC,
        "Mimics a spell when its trigger comes, and is used up when it "
        "works; spending it as vis, or moving it to another form, ends the "
        "power (RoP: Magic p. 121).",
        per_magnitude=2,
    ),
    VisKind(
        DEDICATED,
        "Dedicated",
        MAGIC,
        "Of one Technique and Form together, never split: for that pair "
        "+4 a pawn in casting, and each pawn counts as two toward a Ritual "
        "or enchantment and for botch dice; otherwise ordinary vis (RoP: "
        "Magic pp. 122-123).",
        build_points=7.5,
    ),
    VisKind(
        HERB_OF_VIRTUE,
        "Herb of Virtue",
        MAGIC,
        "Enriched (a season: Int + Magic Lore + aura of 9), it is no longer "
        "vis and gives its carrier a Major Virtue and a Minor Flaw for a "
        "year a pawn, if he has no Magic Resistance (RoP: Magic pp. 124-125).",
    ),
    VisKind(
        OBJECT_OF_VIRTUE,
        "Object of Virtue",
        MAGIC,
        "Enriched (a season: Int + Magic Lore + aura of 9), it is no longer "
        "vis and gives its carrier a lasting Minor Virtue, if he has no "
        "Magic Resistance; formed stones are such Objects (RoP: Magic pp. "
        "124-128).",
    ),
    VisKind(
        ENCASED,
        "Faerie: encased",
        FAERIE,
        "Magic vis a faerie has laid glamour over to claim it; spent as "
        "ordinary vis (RoP: Faerie p. 18).",
        False,
    ),
    VisKind(
        ANCHOR,
        "Faerie: anchor",
        FAERIE,
        "The anchor of a faerie's body: harvesting its vis destroys the "
        "faerie, and another takes its role (RoP: Faerie pp. 18-19).",
    ),
    VisKind(
        ACCRUED,
        "Faerie: accrued",
        FAERIE,
        "Left where faeries ended their roles; it may keep Pretenses a "
        "bearer can use, and a faerie given it may take up the old role "
        "(RoP: Faerie p. 19).",
    ),
    VisKind(
        SLEEPING,
        "Faerie: sleeping",
        FAERIE,
        "A dormant glamour: given vitality, it may wake as a faerie; "
        "Merinita magi pay well for it (RoP: Faerie p. 19).",
    ),
    VisKind(
        ABSTRACT,
        "Faerie: abstract",
        FAERIE,
        "A faerie's promise made solid: it holds no real vis, and magi "
        "can't use it as vis (RoP: Faerie p. 19).",
        usable=False,
        build_points=0,
    ),
)
BY_KEY: dict[str, VisKind] = {kind.key: kind for kind in KINDS}
assert tuple(BY_KEY) == VIS_KINDS, "rules.vis_kinds and models.VIS_KINDS disagree"


def kind_of(possession: Possession) -> VisKind:
    return BY_KEY[possession.vis_kind]


def kind_options(saga: Saga | None, keep: str = "") -> list[tuple[str, str]]:
    """The special kinds a vis form offers (blank is ordinary vis): those of
    the books the saga has in play, and the store's own `keep`."""
    books = sourcebooks.saga_books(saga)
    return [
        (kind.label, kind.key)
        for kind in KINDS
        if kind.key and (kind.key == keep or books is None or kind.book in books)
    ]


def label(possession: Possession) -> str:
    """ "Dedicated (Creo Ignem)", "Herb of Virtue: Fennel", "" for ordinary."""
    kind = kind_of(possession)
    if not kind.key:
        return ""
    if kind.key == DEDICATED and possession.paired_art:
        return f"{kind.label} ({' '.join(dedicated_pair(possession))})"
    thing = THINGS_BY_ID.get(possession.virtue_thing)
    return f"{kind.label}: {thing.name}" if thing is not None else kind.label


def clean(values: dict[str, object]) -> dict[str, object]:
    """A vis form's values with the fields of other kinds cleared, so a
    store changed back to ordinary vis drops its pair or its Thing."""
    if "vis_kind" not in values:
        return values
    found = dict(values)
    kind = found.get("vis_kind") or ""
    found["vis_kind"] = kind
    found["paired_art"] = (found.get("paired_art") or "") if kind == DEDICATED else ""
    found["virtue_thing"] = (found.get("virtue_thing") or "") if kind in THINGS else ""
    if kind not in EXTRAORDINARY:
        found["effect_level"] = None
    return found


def problem(values: dict[str, object]) -> str | None:
    """What's wrong with a vis form's kind of vis, if anything."""
    kind = values.get("vis_kind") or ""
    art = str(values.get("art") or "")
    if kind == DEDICATED:
        other = str(values.get("paired_art") or "")
        if not other:
            return "Dedicated vis needs its other Art: a Technique and a Form."
        if art and (art in TECHNIQUES) == (other in TECHNIQUES):
            return "Dedicated vis is one Technique and one Form together."
    thing = THINGS_BY_ID.get(str(values.get("virtue_thing") or ""))
    if thing is not None and art and art != thing.art:
        return f"{thing.name} holds {thing.art} vis, not {art}."
    level = values.get("effect_level")
    if isinstance(level, int) and level < 1:
        return "The level of its power must be at least 1."
    return None


def same_kind(one: Possession, other: Possession) -> bool:
    """Whether vis of `one` may join `other`'s store: the same kind, pair,
    Thing and Infernal mark."""
    return (one.vis_kind, one.paired_art, one.virtue_thing, one.infernal) == (
        other.vis_kind,
        other.paired_art,
        other.virtue_thing,
        other.infernal,
    )


def copy_kind(source: Possession, target: Possession) -> Possession:
    """`target` given `source`'s kind of vis (and Infernal mark): a store
    made from its vis. Returns `target`."""
    target.vis_kind = source.vis_kind
    target.paired_art = source.paired_art
    target.virtue_thing = source.virtue_thing
    target.effect_level = source.effect_level
    target.infernal = source.infernal
    return target


# --------------------------------------------------------- dedicated vis


def dedicated_pair(possession: Possession) -> tuple[str, str]:
    """A dedicated pawn's Technique and Form, in that order."""
    arts = (possession.art.title(), possession.paired_art.title())
    return arts if arts[0] in TECHNIQUES else (arts[1], arts[0])


def dedicated_for(possession: Possession, technique: str, form: str) -> bool:
    """Whether `possession` is dedicated vis of exactly this Technique and
    Form, so twice as effective for it."""
    return possession.vis_kind == DEDICATED and dedicated_pair(possession) == (
        technique.title(),
        form.title(),
    )


def dedicated_pawns_to_pay(cost: int) -> int:
    """Pawns of matching dedicated vis that pay a Ritual's or enchantment's
    `cost` alone: each counts as two."""
    return round_up(max(0, cost) / 2)


def dedicated_study_quality(die: int, aura: int) -> int:
    """The Source Quality, for each of its two Arts, of a season studying
    dedicated vis (with or without ordinary vis beside it): (stress die +
    aura) / 2."""
    return round_down((die + aura) / 2)


def dedicated_study_botch_dice(pawns: int) -> int:
    return 2 * max(0, pawns)


def dedicated_study_problem(dedicated: int, ordinary: int) -> str | None:
    """Ordinary vis studied with dedicated needs a dedicated pawn each."""
    if ordinary > dedicated:
        return (
            f"{ordinary} ordinary pawn(s) need as many dedicated: only "
            f"{dedicated} (RoP: Magic p. 123)."
        )
    return None


def dedicated_shape_bonus(bonus: int) -> int:
    """A Shape and Material bonus from dedicated vis's own form, doubled; it
    may pass the enchanter's Magic Theory (the bonus before doubling may
    not)."""
    return 2 * bonus


# ----------------------------------------------------------- what it's worth


def build_points_per_pawn(possession: Possession) -> float:
    """Build Points of a pawn a year from a source of this vis, taking the
    middle of the book's range for an extraordinary power (RoP: Magic p.
    124; ordinary vis 5)."""
    kind = kind_of(possession)
    magnitudes = round_up((possession.effect_level or 0) / 5)
    return kind.build_points + kind.per_magnitude * magnitudes


def source_build_points(possession: Possession) -> int:
    return round_up(build_points_per_pawn(possession) * max(0, possession.pawns))


def stock_build_points(possession: Possession) -> int:
    """A vis stock's: a fifth of its source's cost for every 5 pawns."""
    return round_up(
        max(0, possession.pawns) / 5 * build_points_per_pawn(possession) / 5
    )


def trade_value(possession: Possession) -> float:
    """Ordinary pawns a pawn of it is worth in trade: Build Points / 5."""
    return build_points_per_pawn(possession) / 5


def suggested_pawns(level: int) -> int:
    """Pawns an extraordinary object usually holds: one for every 10 levels
    of its power (RoP: Magic p. 120)."""
    return max(1, round_up(level / 10))


# --------------------------------------------------------- Things of Virtue


@dataclass(frozen=True)
class ThingOfVirtue:
    id: str
    name: str
    kind: str  # HERB_OF_VIRTUE or OBJECT_OF_VIRTUE
    art: str
    pawns: int
    #: What Enriching it gives (and costs) its bearer, in brief.
    virtue: str
    #: Its Shape and Material bonuses, as the book's tables give them.
    bonus: str = ""
    page: int = 0
    formed_stone: bool = False


H, O = HERB_OF_VIRTUE, OBJECT_OF_VIRTUE
THINGS_OF_VIRTUE: tuple[ThingOfVirtue, ...] = (
    ThingOfVirtue(
        "centaury", "Centaury", H, "Rego", 2,
        "flight for the drinker and up to 12 others (Greater Power); "
        "Necessary Condition: drunk",
        "+3 flight", 125,
    ),
    ThingOfVirtue(
        "cinquefoil", "Cinquefoil", H, "Mentem", 1, "Inspirational",
        "+3 leadership, +1 Rego Mentem", 125,
    ),
    ThingOfVirtue(
        "fennel", "Fennel", H, "Vim", 2,
        "a wand that drives off evil spirits (Greater Power); must stay "
        "Continent",
        "+5 repel ghosts, +5 repel evil spirits, +2 dreams", 126,
    ),
    ThingOfVirtue(
        "mistletoe", "Mistletoe", H, "Intellego", 2,
        "Divination & Augury; Fragile Constitution",
        "+7 divination", 126,
    ),
    ThingOfVirtue(
        "pennyroyal", "Pennyroyal", H, "Corpus", 1,
        "Greater Purifying Touch (by the ruling star); a Delusion",
        "+3 healing", 126,
    ),
    ThingOfVirtue(
        "periwinkle", "Periwinkle", H, "Mentem", 1, "Venus's Blessing; Reckless",
        "+3 love, +1 loyalty or affection", 126,
    ),
    ThingOfVirtue(
        "amethyst", "Amethyst", O, "Mentem", 1,
        "Lesser Immunity (drunkenness)", page=127,
    ),
    ThingOfVirtue(
        "bloodstone", "Bloodstone", O, "Creo", 1,
        "Rapid Convalescence, resting in bed", page=127,
    ),
    ThingOfVirtue(
        "bufonite", "Bufonite (Toad Stone)", O, "Intellego", 2,
        "detect poison (Lesser Power)", "+3 detect poison", 127,
    ),
    ThingOfVirtue(
        "opal", "Opal", O, "Terram", 2,
        "Sure Traveler; a minor Personality Flaw", page=127,
    ),
    ThingOfVirtue("sapphire", "Sapphire", O, "Intellego", 1, "Intuition", page=127),
    ThingOfVirtue("clam_shell", "Clam Shell", O, "Terram", 1, "Tough", page=127),
    ThingOfVirtue(
        "emerald", "Emerald", O, "Animal", 2, "Animal Ken, with serpents only",
        page=127,
    ),
    ThingOfVirtue(
        "jet", "Jet", O, "Perdo", 1, "Puissant Stealth, while no one else sees it",
        page=127,
    ),
    ThingOfVirtue("topaz", "Topaz", O, "Mentem", 1, "Puissant Leadership", page=127),
    ThingOfVirtue(
        "clach_crubain", "Clach Crubain", O, "Perdo", 1,
        "Lesser Immunity (arthritis)", "+2 arthritis", 127, True,
    ),
    ThingOfVirtue(
        "ovum_anguinum", "Ovum Anguinum (Serpent's Egg)", O, "Creo", 2,
        "Improved Characteristics (Stamina +2), or Improved Communication, "
        "or Tough",
        "+2 versus infection and poison, +2 legal arguments, +2 resist injury",
        127, True,
    ),
    ThingOfVirtue(
        "thunderbolt", "Thunderbolt", O, "Auram", 1,
        "Ward against Demons of the Air of Might 10 or less (Greater Power); "
        "held in the hand",
        "+3 lightning, +2 Auram, +4 protection from demons", 128, True,
    ),
    ThingOfVirtue(
        "cornu_ammonis", "Cornu Ammonis (Horn of Ammon)", O, "Intellego", 2,
        "Visions, in dreams", "+3 affect visions, dreams", 128, True,
    ),
    ThingOfVirtue(
        "glossopetrae", "Glossopetrae (Stone Adder's Tongue)", O, "Aquam", 1,
        "antidote to liquid poisons (Lesser Power)", "+5 resist snake venom",
        128, True,
    ),
    ThingOfVirtue(
        "fairy_loaves", "Fairy Loaves", O, "Muto", 1,
        "keeps milk fresh (Lesser Power)", "+4 keep milk fresh", 128, True,
    ),
)  # fmt: skip
THINGS_BY_ID: dict[str, ThingOfVirtue] = {t.id: t for t in THINGS_OF_VIRTUE}


def thing_options(kind: str) -> list[tuple[str, str]]:
    """The Things of Virtue of `kind` a form offers, by name."""
    return [
        (f"{t.name} ({t.pawns} {t.art})", t.id)
        for t in THINGS_OF_VIRTUE
        if t.kind == kind
    ]


def thing_text(thing: ThingOfVirtue) -> str:
    """ "Enriched: Intuition; Shape and Material +3 detect poison (RoP:
    Magic p. 127)"."""
    bonus = f"; Shape and Material {thing.bonus}" if thing.bonus else ""
    stone = ", a formed stone" if thing.formed_stone else ""
    return f"Enriched: {thing.virtue}{bonus}{stone} (RoP: Magic p. {thing.page})"


ENRICHMENT_LEVEL = 9
LORE_EASE = 9
MAGIC_LORE = "Magic Lore"


def enrichment_total(character: Character, aura: int) -> Breakdown:
    """Intelligence + Magic Lore + aura, against ENRICHMENT_LEVEL for a
    season's Enrichment (RoP: Magic p. 125)."""
    score, bonus = ability_score(character, MAGIC_LORE)
    lines = [
        Line(
            "Intelligence",
            amount=character.characteristics.intelligence,
            source=SOURCE,
        ),
        Line(MAGIC_LORE, amount=score + bonus, source=SOURCE),
        Line("Aura", amount=aura, source=SOURCE),
    ]
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def enrichment_herb_years(pawns: int) -> int:
    """How long an Enriched Herb of Virtue keeps its power: a year a pawn."""
    return max(1, pawns)


# ---------------------------------------------------------------- storage

LOW_VIS_LEAST = 10  # a rook
HIGH_VIS_LEAST = 100  # a queen

STORAGE_EFFECTS: dict[str, str] = {
    "Animal": "vermin appear, animals grow other beasts' parts, or vermin die",
    "Aquam": "everything is damp with dew, or water there is pure",
    "Auram": "fog, showers and sudden winds",
    "Corpus": "small cuts and bruises heal, hair grows fast",
    "Herbam": "old wood sprouts leaves, weeds push through the floor",
    "Ignem": "smoke and summer heat; tinder may catch fire",
    "Imaginem": "food tastes better, colours and sounds are keener",
    "Mentem": "moods run high, and hidden thoughts are heard aloud",
    "Terram": "cracked pots mend, rusted blades are keen again",
    "Vim": "things there act as if under Shell of False Determination; "
    "creatures who stay take The Phantom Gift",
    "Creo": "worn things become as new, food keeps",
    "Intellego": "+3 to Perception rolls there",
    "Muto": "colours and sounds keep changing",
    "Perdo": "wood rots, food spoils and metal rusts",
    "Rego": "+1 to resist Personality Traits",
}


def storage_magnitude(pawns: int, least: int) -> int:
    """The magnitude of the spontaneous spells `pawns` of one Art kept
    together cause, with `least` the saga's smallest amount: 1 at that,
    one more for each multiple (0 below it)."""
    return max(0, pawns) // least


def storage_note(art: str, pawns: int) -> str:
    """What `pawns` of `art` vis kept together may do, at the storyguide's
    option ("" below a rook)."""
    low = storage_magnitude(pawns, LOW_VIS_LEAST)
    if not low:
        return ""
    high = storage_magnitude(pawns, HIGH_VIS_LEAST)
    levels = f"spontaneous {art} spells of level {5 * low} or less within Voice"
    high_text = (
        f"level {5 * high} in a high-vis saga" if high else "none in a high-vis saga"
    )
    harmless = STORAGE_EFFECTS.get(art.title(), "")
    effect = f"; or simply: {harmless}" if harmless else ""
    return (
        f"{pawns} pawns together, at the storyguide's option: {levels} in a "
        f"low-vis saga ({high_text}){effect} (RoP: Magic pp. 123-124)."
    )


# -------------------------------------------------- magic creatures and vis

#: Minutes to regain the whole Might Pool, by aura - Might / 5 (0 to 9).
RECOVERY_MINUTES: tuple[int, ...] = (1440, 720, 360, 180, 90, 45, 22, 10, 5, 2)


def might_recovery(aura: int, might: int) -> tuple[int, float] | None:
    """Resting in a Magic aura of `aura`, the minutes a Might `might`
    character takes to regain its whole Pool, and to regain a point (None
    when the chart doesn't reach: the aura is too weak for its Might). The
    book doesn't round aura - Might / 5; the app rounds it down."""
    if might <= 0:
        return None
    subtotal = round_down(aura - might / 5)
    if subtotal < 0:
        return None
    whole = RECOVERY_MINUTES[min(subtotal, len(RECOVERY_MINUTES) - 1)]
    return whole, whole / might


def _duration(minutes: float) -> str:
    """ "12 hours", "1 hour 12 minutes", "45 minutes", "under a minute"."""
    whole = round(minutes)
    if whole < 1:
        return "under a minute"
    hours, left = divmod(whole, 60)
    parts = []
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if left:
        parts.append(f"{left} minute{'s' if left != 1 else ''}")
    return " ".join(parts)


def recovery_text(aura: int, might: int) -> str:
    """ "All its Might in 12 hours' rest, a point every 1 hour 12 minutes",
    or "" when the aura is too weak for its Might."""
    found = might_recovery(aura, might)
    if found is None:
        return ""
    whole, point = found
    return (
        f"Resting in its Magic aura {aura}: all its Might in {_duration(whole)}, "
        f"a point every {_duration(point)} (RoP: Magic p. 30)"
    )


# ------------------------------------------------- vis in use (casting)


def casting_notes(
    stores: Sequence[Possession], technique: str, form: str, cost: int = 0
) -> list[str]:
    """What the special stores of a spell's Arts change in casting it (a
    Ritual needing `cost` pawns)."""
    notes: list[str] = []
    for store in stores:
        kind = kind_of(store)
        name = store.name or store.art
        if not kind.usable:
            notes.append(f"{name}: {kind.label.lower()} vis can't be spent.")
        elif dedicated_for(store, technique, form):
            pays = (
                f" ({dedicated_pawns_to_pay(cost)} of its pawns pay this Ritual's "
                f"{cost})"
                if cost
                else ""
            )
            notes.append(
                f"{name}: dedicated {technique} {form} vis, +4 a pawn, each pawn "
                f"counting as two toward a Ritual's pawns{pays} and for botch "
                "dice (RoP: Magic p. 122)."
            )
        elif kind.key == ANCHOR:
            notes.append(
                f"{name}: spending it destroys its faerie (RoP: Faerie p. 18)."
            )
        elif kind.special and kind.key != DEDICATED:
            notes.append(f"{name}: spending it as vis ends its power ({kind.label}).")
    return notes
