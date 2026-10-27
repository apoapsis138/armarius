"""Mythic Africa's rules: the Nubian Cult of Dedun and Corpse Magic, the
Ethiopian church and calendar, the Mythic Aithiopians (Lands of the Nile
pp. 95-126) and the Plinian monstrous races and the jnun (Between Sand and
Sea pp. 119-124), as plain rules.

- The Cult of Dedun (LotN pp. 97-102): rank needs (Altar Priest
  Organization Lore 1 and Meroitic 3; Temple Priest 3 and 4; Undying One
  Lore 5, Warping + Decrepitude 7+, Gifted, a Temple Priest with
  Enfeebled). Dedun's Blessing aligns a Magic aura to the dead: a
  ceremony each season for a year, then Int + Magic Lore + stress die
  against 9 + the aura, +1 for each earlier failed year (pooled across
  the priests who share the work); an aligned aura counts double for
  work with the dead, and adds twice its level to an Undying One's Magic
  Resistance. A Court's strength is the sum of each corpse's highest
  Reputation in life (at least 1; a king 7, a sub-king 5; a Divine burial
  -3, to no less than 0). Unnatural Vitality adds 3 x Decrepitude to
  Casting and Lab Totals and cancels as much of a penalty; above
  Decrepitude 4 stress brings no Crisis, and Crisis Totals take -3 (the
  errata, p. 87: she need not become bedridden and die at Decrepitude 5).
  An Undying One buys Might as an Art with the Court's strength as xp,
  and the Court stands for a Magic aura of strength / 10 (round up)
  against Acclimation (Realms of Power: Magic p. 53, rules.magic_build).
  Breaking the Adherent's Prohibition brings Dedun's Shadow: an aging
  Crisis, and Lame, Palsied Hands or Afflicted Tongue even if survived.
- Corpse Magic (LotN p. 102): Com + Corpse Magic + aura + stress die
  against 9 (speak), 12 (compel truth, or protect a corpse: later Corpse
  Magic on it adds the protector's score to its Ease Factors), 15
  (animate, in sight) or 18 (animate under mental control). Commands are
  Com + Leadership + stress die against 6 (a word), 9 (simple) or 12
  (complex); Leadership is capped by the corpse's language below 5;
  three failed commands lay it to rest until the moon rises. To leave the
  grave the Penetration Total must exceed the walking corpse's Might (9).
- Ethiopia (LotN pp. 108-114): the calendar as the book prints it (the
  Ethiopian year is the Julian year - 8 until Meskerem 1, August 30, then
  - 7) and its holidays; a church forest concentrates the Divine aura (one
  lower outside the forest, one higher in a lush one, p. 111); the Ark's
  and Solomon's ring's Faith Scores by who calls on them (p. 112); a Jew
  is an Outsider only as a blacksmith (p. 110). The Debterah are a
  tradition (data/tradition_catalog.json): a holy societas with Christian
  and Falasha Jewish members (p. 114), so a member's Theology is
  Christian or Judaism by his faith; Favored Abilities Adjuration,
  Blessing, Craft Amulets and Invocation (RoP:D pp. 34, 37, 48-50, 137).
- The scorpion fish's swallow (p. 97, a Quality by the errata, p. 87):
  stomach acid +9 a round, x4 when wholly immersed; a Str + Athletics
  brace against 6 / 9 / 12 makes it x3 / x2 / x1.
- The Mythic Aithiopians (pp. 122-126): each tribe's intrinsic Virtue and
  Flaw (as a Magic Human, a Minor Virtue Quality and a Minor Flaw
  Inferiority instead), Outsider in Nubia; kombè (Stamina against 12,
  charging an arrow Dex + Profession: Prepare Kombè against 6, which no
  one without the Ability can pass); the Acridophagi age from 15; the
  carnivorous bull's ambush.
- The Plinian races (BS&S pp. 119-124): their Magic Qualities and
  Inferiorities (net zero, Monstrous Appearance free), Might by role,
  their Social Status among humans, the anthropophagi's yearly feast, and
  which jnun Sihr commands (p. 123-125), with a jinni's Shapeshifter
  sizes.

The Definitive Edition wins where a book differs: an untrained Ability
rolls three extra botch dice (DE p. 157), as kombè's charging says.
Between Sand and Sea's Blemmya (Puissant Bargain) is the Libyan merchant;
Lands of the Nile's (Puissant Thrown Weapon, p. 96) the Nubian raider,
whose men also Age Quickly.

No screen uses these yet: they are the rules for the screens still to
come, and only the tests call them."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .magic_build import aura_needed
from .rounding import round_up
from .xp import ART_FACTOR, score_from_xp

SOURCE = (
    "Lands of the Nile, Chapter Seven: Nubia, pp. 95-102, Chapter Eight: "
    "Ethiopia, pp. 103-121, Chapter Nine: Mythic Aithiopians, pp. 122-126; "
    "Between Sand and Sea, The Monstrous Races of Africa and The Jnun, "
    "pp. 119-125; Errata pp. 86-87; Ars Magica Definitive Edition p. 157"
)

# -- the Cult of Dedun (LotN pp. 97-102) --

ADHERENT = "Adherent"
ALTAR_PRIEST = "Altar Priest"
TEMPLE_PRIEST = "Temple Priest"
UNDYING_ONE = "Undying One"
DEDUN_RANKS: tuple[str, ...] = (ADHERENT, ALTAR_PRIEST, TEMPLE_PRIEST, UNDYING_ONE)

#: Each rank's least Organization Lore: Cult of Dedun and Meroitic (pp. 99-100).
_RANK_SCORES: dict[str, tuple[int, int]] = {
    ADHERENT: (0, 0),
    ALTAR_PRIEST: (1, 3),
    TEMPLE_PRIEST: (3, 4),
    UNDYING_ONE: (5, 0),
}
#: Warping Score + Decrepitude Score an Undying One needs (p. 100).
UNDYING_WARPING_AND_DECREPITUDE = 7
#: Dedun's Blessing: Ease Factor 9 + the aura (p. 99).
BLESSING_BASE_EASE = 9
#: The Temple Priest's squalor (p. 99).
TEMPLE_PRIEST_LIVING_CONDITIONS = -3
#: Unnatural Vitality (p. 100): 3 x Decrepitude, Crisis Total -3, and no
#: Crisis from stress above Decrepitude 4.
VITALITY_MULTIPLE = 3
VITALITY_CRISIS = -3
VITALITY_NO_STRESS_CRISIS_ABOVE = 4
#: A Court's corpses (p. 100): a king's Reputation is at least 7, a
#: sub-king's or major noble's 5; a Divine burial takes 3 off.
KING_REPUTATION = 7
SUB_KING_REPUTATION = 5
DIVINE_BURIAL = -3
#: Dedun's Shadow leaves one of these even when the Crisis is survived (p. 98).
DEDUN_SHADOW_FLAWS: tuple[str, ...] = (
    "vf_lame",
    "vf_palsied_hands",
    "vf_afflicted_tongue",
)


def dedun_rank_problems(
    rank: str,
    *,
    organization_lore: int,
    meroitic: int = 0,
    warping: int = 0,
    decrepitude: int = 0,
    gifted: bool = False,
    temple_priest_with_enfeebled: bool = False,
) -> list[str]:
    """What keeps a cultist from a rank (pp. 99-101); empty when nothing
    does. Only Gifted Temple Priests with Enfeebled can become Undying."""
    if rank not in _RANK_SCORES:
        raise ValueError(f"Unknown Cult of Dedun rank {rank!r}; one of {DEDUN_RANKS}")
    lore, language = _RANK_SCORES[rank]
    found: list[str] = []
    if organization_lore < lore:
        found.append(
            f"Organization Lore: Cult of Dedun {lore} (has {organization_lore})"
        )
    if meroitic < language:
        found.append(f"Meroitic {language} (has {meroitic})")
    if rank == UNDYING_ONE:
        if warping + decrepitude < UNDYING_WARPING_AND_DECREPITUDE:
            found.append(
                f"Warping + Decrepitude {UNDYING_WARPING_AND_DECREPITUDE} "
                f"(has {warping + decrepitude})"
            )
        if not temple_priest_with_enfeebled:
            found.append("a Temple Priest's Initiation and its Enfeebled Ordeal")
        if not gifted:
            found.append("The Gift (the Script works only for the Gifted)")
    return found


def blessing_ease(aura: int) -> int:
    """Dedun's Blessing's Ease Factor to align a Magic aura (p. 99)."""
    return BLESSING_BASE_EASE + max(0, aura)


def blessing_total(
    intelligence: int, magic_lore: int, die: int, failed_years: Iterable[int] = ()
) -> int:
    """Int + Magic Lore + stress die, +1 for each year's failed roll; the
    priests sharing an aura add all their failures together (p. 99)."""
    return intelligence + magic_lore + die + sum(max(0, n) for n in failed_years)


def aligned_aura(aura: int, matches: bool) -> int:
    """An aura aligned to the dead counts double for what affects the dead
    (p. 99; Realms of Power: Magic p. 15)."""
    return aura * 2 if matches else aura


def undying_resistance_bonus(aura: int, aligned_to_the_dead: bool) -> int:
    """An Undying One counts as dead: twice an aligned aura to his Magic
    Resistance (p. 100)."""
    return 2 * max(0, aura) if aligned_to_the_dead else 0


def court_member(reputation: int, divine_burial: bool = False) -> int:
    """What one corpse adds to a Court: its highest Reputation in life, at
    least 1; a Divine burial takes 3 off, to no less than 0 (p. 100)."""
    if divine_burial:
        return max(0, reputation + DIVINE_BURIAL)
    return max(1, reputation)


def court_strength(members: Iterable[tuple[int, bool]]) -> int:
    """A Court's strength from its corpses' (Reputation, Divine burial)."""
    return sum(court_member(reputation, divine) for reputation, divine in members)


def court_aura(strength: int) -> int:
    """The Magic aura a Court stands for against an Undying One's
    Acclimation: a tenth of its strength or fraction (p. 100). It makes no
    aura."""
    return round_up(max(0, strength) / 10)


def undying_might(strength: int) -> int:
    """An Undying One's Might, bought as an Art with the Court's strength
    as xp (p. 101): 62 buys 10. It never rises after."""
    return score_from_xp(max(0, strength), ART_FACTOR)


def court_keeps_off_acclimation(strength: int, might: int) -> str:
    """How much of his time an Undying One must dwell among his Court
    (pp. 100-101 with Realms of Power: Magic p. 53)."""
    aura = court_aura(strength)
    always, half, frequent = aura_needed(might)
    if frequent is not None and aura >= frequent:
        return "visiting it often keeps Acclimation off"
    if half is not None and aura >= half:
        return "half his time among it keeps Acclimation off"
    if always is not None and aura >= always:
        return "only dwelling among it always keeps Acclimation off"
    return "the Court is too weak to keep Acclimation off"


def vitality_bonus(decrepitude: int) -> int:
    """Unnatural Vitality's bonus to Casting and Lab Totals (p. 100)."""
    return VITALITY_MULTIPLE * max(0, decrepitude)


def vitality_penalty(penalty: int, decrepitude: int) -> int:
    """A negative modifier to magic (an aura's, say) after Unnatural
    Vitality cancels up to 3 x Decrepitude of it, to no less than 0."""
    if penalty >= 0:
        return penalty
    return min(0, penalty + vitality_bonus(decrepitude))


def vitality_stress_crisis(decrepitude: int) -> bool:
    """Whether stress still brings a Crisis roll: not above Decrepitude 4."""
    return decrepitude <= VITALITY_NO_STRESS_CRISIS_ABOVE


# -- Corpse Magic (LotN p. 102) --

#: The Casting Total's Ease Factors and what each buys.
CORPSE_MAGIC: tuple[tuple[int, str], ...] = (
    (9, "speak to the dead; it need not answer truly"),
    (
        12,
        "speak to it and compel the truth; or protect a corpse from more Corpse Magic",
    ),
    (15, "animate it, to follow orders while in sight; or take an animated corpse"),
    (18, "animate it under direct mental control, obeying out of sight"),
)
#: A command's Ease Factor, by how much it says.
COMMAND_EASE: dict[str, int] = {"word": 6, "simple": 9, "complex": 12}
#: Failed commands that lay a corpse to rest until the moon rises.
FAILED_COMMANDS = 3
#: A walking corpse's usual Magic Might.
WALKING_CORPSE_MIGHT = 9
#: A Language score below this caps Leadership in a command.
FLUENT = 5


def corpse_magic_total(communication: int, score: int, aura: int, die: int) -> int:
    """Com + Corpse Magic + aura modifier + stress die."""
    return communication + score + aura + die


def corpse_magic_outcome(total: int, protection: int = 0) -> str:
    """The most a Corpse Magic total does; a corpse protected by Corpse
    Magic adds the protector's score to every Ease Factor. Empty when it
    does nothing."""
    done = ""
    for ease, outcome in CORPSE_MAGIC:
        if total >= ease + max(0, protection):
            done = outcome
    return done


def command_total(
    communication: int, leadership: int, language: int, die: int
) -> int | None:
    """Com + Leadership + stress die, Leadership capped by the corpse's
    language below fluency (5); None when the caster doesn't speak it."""
    if language <= 0:
        return None
    if language < FLUENT:
        leadership = min(leadership, language)
    return communication + leadership + die


def corpse_leaves_grave(penetration: int, might: int = WALKING_CORPSE_MIGHT) -> bool:
    """A corpse rises from its grave only when the Penetration Total
    exceeds its Might; otherwise it stays in the earth."""
    return penetration > might


# -- Ethiopia (LotN pp. 108-117) --

#: The Ethiopian months and their Julian start (month, day), and in a
#: Julian leap year where it differs, as the book's table prints them (p. 108).
ETHIOPIAN_MONTHS: tuple[tuple[str, tuple[int, int], tuple[int, int]], ...] = (
    ("Meskerem", (8, 30), (8, 30)),
    ("Taqamt", (9, 29), (9, 29)),
    ("Hadar", (10, 29), (10, 29)),
    ("Tahśaś", (11, 28), (11, 28)),
    ("Tarr", (12, 28), (12, 28)),
    ("Yekatit", (1, 27), (1, 27)),
    ("Megabit", (2, 26), (2, 26)),
    ("Miyazya", (3, 29), (3, 28)),
    ("Ganbot", (4, 28), (4, 27)),
    ("Säne", (5, 28), (5, 27)),
    ("Hamle", (6, 27), (6, 26)),
    ("Nehase", (7, 27), (7, 26)),
    ("Pagume", (8, 26), (8, 25)),
)
#: The first month (Yekatit) that begins in the next Julian year.
_NEW_JULIAN_YEAR = 5
_MONTH_DAYS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


@dataclass(frozen=True)
class Holiday:
    name: str
    month: str
    day: int
    #: The Julian date the book gives beside it (month, day).
    julian: tuple[int, int]
    note: str = ""


#: The major holidays (pp. 110, 114), with the book's Julian dates.
HOLIDAYS: tuple[Holiday, ...] = (
    Holiday(
        "Enkutatash", "Meskerem", 1, (8, 30), "New Year: the Queen of Sheba's return."
    ),
    Holiday(
        "Maskal",
        "Meskerem",
        17,
        (9, 15),
        "The True Cross found: the soot cross on the forehead gives a Faith "
        "Point until washed off or used.",
    ),
    Holiday("Axum Tsion", "Hadar", 20, (11, 18), "The Ark's arrival in Ethiopia."),
    Holiday("Kulubi Gabriel", "Tahśaś", 18, (12, 16), "The Archangel Gabriel's feast."),
    Holiday("Gena", "Tahśaś", 28, (12, 25), "Christmas."),
    Holiday("Timket", "Tarr", 10, (1, 6), "Epiphany, three days."),
    Holiday("Faseka", "Miyazya", 2, (3, 27), "Easter in 1220; it moves."),
    Holiday("Saint Yared", "Ganbot", 11, (5, 8), "May 8 or 9."),
)


def _julian_leap(year: int) -> bool:
    return year % 4 == 0


def _ordinal(year: int, month: int, day: int) -> int:
    """Days since a fixed Julian epoch, for counting between dates."""
    days = 365 * year + (year - 1) // 4 + day
    for m in range(1, month):
        days += _MONTH_DAYS[m - 1] + (1 if m == 2 and _julian_leap(year) else 0)
    return days


def ethiopian_date(year: int, month: int, day: int) -> tuple[int, str, int]:
    """A Julian date as (Ethiopian year, month, day), by the book's table:
    1 January 1220 is Tarr 5, 1212 (p. 110)."""
    first = year if (month, day) >= ETHIOPIAN_MONTHS[0][1] else year - 1
    date = _ordinal(year, month, day)
    found = ETHIOPIAN_MONTHS[0][0], 1
    for index, (name, start, leap_start) in enumerate(ETHIOPIAN_MONTHS):
        on = first if index < _NEW_JULIAN_YEAR else first + 1
        m, d = leap_start if _julian_leap(on) else start
        begins = _ordinal(on, m, d)
        if begins <= date:
            found = name, date - begins + 1
    return first - 7, found[0], found[1]


def church_forest_aura(
    aura: int, *, has_forest: bool, in_forest: bool = True, lush: bool = False
) -> int:
    """A church's Divine aura where its sacred forest gathers it: one lower
    outside the forest, one higher inside a lush one (p. 111)."""
    if not has_forest:
        return aura
    if not in_forest:
        return max(0, aura - 1)
    return aura + 1 if lush else aura


#: Who calls on them, and the Faith Score the Ark of the Covenant and
#: Menelik's ring of Solomon have for them (p. 112).
ARK_FAITH: dict[str, int] = {"ethiopian": 10, "other christian": 7, "muslim": 7}
RING_FAITH: dict[str, int] = {"ethiopian": 7, "jewish": 7, "other christian": 5}


def relic_faith(relic: str, believer: str) -> int | None:
    """The Ark's or the ring's Faith Score for an Ethiopian (Christian or
    Falasha), a Jew, another Christian or a Muslim; None where the book
    gives none. The ring adds it to a Solomonic or Ars Notoria total."""
    table = {"ark": ARK_FAITH, "ring": RING_FAITH}.get(relic)
    if table is None:
        raise ValueError(f"Unknown relic {relic!r}; 'ark' or 'ring'")
    return table.get(believer)


def ethiopian_outsider(jewish: bool, blacksmith: bool) -> bool:
    """Being a Jew in Ethiopia is no Outsider Flaw unless he is also a
    blacksmith, whom the bouda tales taint (p. 110)."""
    return jewish and blacksmith


#: Books the chapter describes: title, kind, subject, level, Quality.
ETHIOPIAN_TEXTS: tuple[tuple[str, str, str, int, int], ...] = (
    ("The Periplus of the Erythean Sea", "tractatus", "Area Lore: Ethiopia", 0, 5),
    (
        "The Periplus of the Erythean Sea",
        "tractatus",
        "Area Lore: Erythean Sea Coast",
        0,
        5,
    ),
    ("The Periplus of the Erythean Sea", "tractatus", "Area Lore: Red Sea Coast", 0, 5),
    ("The Periplus of the Erythean Sea", "tractatus", "Magic Lore", 0, 5),
    ("The Books of Saint Yared", "summa", "Organization Lore: Ethiopian Church", 5, 8),
    ("Ezana's Stone", "tractatus", "a language it bears, or Area Lore: Ethiopia", 0, 5),
)


# -- the scorpion fish (LotN p. 97; Errata p. 87) --

#: Stomach acid a round, and the brace roll's Ease Factors and multiples.
ACID_DAMAGE = 9
_BRACE: tuple[tuple[int, int], ...] = ((12, 1), (9, 2), (6, 3))
FULL_IMMERSION = 4
#: Rounds from being swallowed to the stomach; the largest Size swallowed.
ROUNDS_TO_STOMACH = 3
SWALLOW_SIZE = 0


def acid_damage(brace: int | None = None) -> int:
    """The acid's damage this round: +36 wholly immersed, less for a Str +
    Athletics brace roll of 6 (x3), 9 (x2) or 12 (a splash)."""
    if brace is not None:
        for ease, multiple in _BRACE:
            if brace >= ease:
                return ACID_DAMAGE * multiple
    return ACID_DAMAGE * FULL_IMMERSION


# -- the Mythic Aithiopians (LotN pp. 122-126) --


@dataclass(frozen=True)
class Kindred:
    """A people's intrinsic Virtues and Flaws or Magic Qualities and
    Inferiorities, each (catalog id, detail), and what else the book says."""

    key: str
    name: str
    virtues: tuple[tuple[str, str], ...]
    flaws: tuple[tuple[str, str], ...]
    page: int
    notes: str = ""


#: Each tribe's intrinsic Virtue and Flaw, beyond the normal allotment.
AITHIOPES: tuple[Kindred, ...] = (
    Kindred(
        "icthyophagi",
        "Icthyophagus (fish eater)",
        (("vf_enduring_constitution", ""),),
        (("vf_weakness", "drinking water"),),
        123,
        "High Survival and Swim; a month of their dried fish bricks is one Load.",
    ),
    Kindred(
        "rhizophagi",
        "Rhizophagus (root eater)",
        (("vf_herbalism", ""),),
        (("vf_noncombatant", ""),),
        123,
        "Profession: Apothecary and Chirurgy; expert poisoners, makers of kombè "
        "and its antidote; some have Mythic Herbalism.",
    ),
    Kindred(
        "cynegi",
        "Cynegus (hunter)",
        (("vf_puissant_ability", "Hunt"),),
        (("vf_reckless", ""),),
        124,
        "Profession: Prepare Kombè charges an arrow with the venom.",
    ),
    Kindred(
        "struthophagi",
        "Struthophagus (bird eater)",
        (("vf_puissant_ability", "Ride"),),
        (("vf_small_frame", ""),),
        124,
        "Light cavalry on ostriches, which hurl stones as their riders throw spears.",
    ),
    Kindred(
        "acridophagi",
        "Acridophagus (locust eater)",
        (("vf_greater_immunity", "thirst"),),
        (("vf_greater_malediction", "winged lice"),),
        125,
        "The lice curse starts Aging rolls at 15; no magic cures or wards it.",
    ),
    Kindred(
        "cynamolgi",
        "Cynamolgus",
        (("vf_puissant_ability", "Animal Handling"),),
        (("vf_compulsion", "protect his pack"),),
        125,
        "Leads a trained group of his dogs with Animal Handling in place of "
        "Leadership; rarely has an Animal Companion.",
    ),
    Kindred(
        "megabari_men",
        "Megabarus (man)",
        (("vf_puissant_ability", "Bows"),),
        (("vf_prohibition", "harming women"),),
        126,
    ),
    Kindred(
        "megabari_women",
        "Megabarus (woman)",
        (("vf_temporal_influence", ""),),
        (("vf_oversensitive", "to disrespect"),),
        126,
        "The book names the Flaw Sensitive.",
    ),
)
#: Hylophagi are intelligent monkeys, not men: the Bestiary's baboon with
#: these added (p. 124).
HYLOPHAGUS: tuple[tuple[str, str], ...] = (
    ("vf_perfect_balance", ""),
    ("vf_primitive_equipment", ""),
)
#: As a Magic Human, the extra Virtue and Flaw become these (p. 122).
AITHIOPE_AS_MAGIC_HUMAN: tuple[str, str] = ("vf_minor_virtue", "vf_minor_flaw")
#: Kombè (p. 124): resisting it, and charging an arrow with it.
KOMBE_RESIST_EASE = 12
KOMBE_CHARGE_EASE = 6
UNTRAINED_BOTCH_DICE = 3
#: Minutes until a victim is immobile, and until he cannot breathe.
KOMBE_IMMOBILE_MINUTES = 5
KOMBE_SUFFOCATES_MINUTES = 10
#: The Acridophagus curse's first Aging roll (p. 125).
ACRIDOPHAGUS_AGING_FROM = 15


def kindred(key: str) -> Kindred:
    for found in AITHIOPES + PLINIAN_RACES:
        if found.key == key:
            return found
    raise LookupError(f"No Aithiopian tribe or Plinian race {key!r}")


def kombe_charged(dexterity: int, prepare_kombe: int, die: int) -> bool:
    """Whether a shot arrow carried its kombè: Dex + Profession: Prepare
    Kombè + die against 6. Without the Ability it never does (the roll is
    still made for a botch, with three extra botch dice)."""
    if prepare_kombe <= 0:
        return False
    return dexterity + prepare_kombe + die >= KOMBE_CHARGE_EASE


def kombe_resisted(stamina_roll: int) -> bool:
    """A victim's Stamina roll against 12; failing, he is immobile in five
    minutes and suffocates from ten (Deprivation rolls, DE)."""
    return stamina_roll >= KOMBE_RESIST_EASE


def carnivorous_bull_ambush(spotted: bool) -> tuple[bool, int]:
    """Unspotted, the carnivorous bull wins the first round's initiative
    and +3 to its Attack that round (p. 126)."""
    return (False, 0) if spotted else (True, 3)


# -- the Plinian races (BS&S pp. 119-124; LotN p. 96) --

PLINIAN_RACES: tuple[Kindred, ...] = (
    Kindred(
        "anthropophagus",
        "Anthropophagus (man-eater)",
        (("vf_improved_attack", "bite"), ("vf_improved_damage_quality", "bite, x2")),
        (("vf_major_flaw", "Greater Malediction: the yearly feast"),),
        120,
        "Tusks Init 0, Attack +6, Defense +2, Damage +11. Never tolerated in "
        "human settlements.",
    ),
    Kindred(
        "astomus",
        "Astomus (mouthless)",
        (
            ("vf_minor_virtue", "Enchanting Music"),
            ("vf_minor_virtue", "Puissant Music"),
            ("vf_personal_power_quality", "The Tongueless Voice"),
        ),
        (
            ("vf_minor_flaw", "Fragile Constitution"),
            ("vf_minor_flaw", "Warped Senses: Sensitive Smell"),
            ("vf_reduced_fatigue", ""),
        ),
        120,
        "No need to breathe, eat or drink; a foul odor can incapacitate one.",
    ),
    Kindred(
        "blemmya",
        "Blemmya (Libyan)",
        (("vf_minor_virtue", "Puissant Bargain"), ("vf_minor_virtue", "Tough")),
        (("vf_minor_flaw", "Hunchback"), ("vf_minor_flaw", "Poor Hearing")),
        121,
        "Merchants who lead camel trains; cannot use large shields, and wear "
        "armor only with eye holes.",
    ),
    Kindred(
        "nubian_blemmya",
        "Blemmya (Nubian)",
        (("vf_minor_virtue", "Puissant Thrown Weapon"), ("vf_minor_virtue", "Tough")),
        (("vf_minor_flaw", "Hunchback"), ("vf_minor_flaw", "Poor Hearing")),
        96,
        "Lands of the Nile: men also have Major Flaw (Age Quickly); women do "
        "not age. Mounted skirmishers with slings.",
    ),
    Kindred(
        "cynocephalus",
        "Cynocephalus (dog-head)",
        (("vf_gigantic", ""), ("vf_minor_virtue", "Sharp Ears")),
        (
            ("vf_major_flaw", "Age Quickly"),
            ("vf_susceptible_to_deprivation_inferiority", ""),
        ),
        121,
        "+3 to rolls by scent, tracking included; often Afflicted Tongue.",
    ),
    Kindred(
        "maritimus",
        "Maritimus",
        (
            ("vf_lesser_power_quality", "x2"),
            ("vf_minor_virtue", "Keen Vision"),
            ("vf_minor_virtue", "Sense Holiness and Unholiness"),
        ),
        (
            ("vf_major_flaw", "Age Quickly"),
            ("vf_susceptible_to_deprivation_inferiority", ""),
        ),
        122,
        "A second pair of eyes; expert archers, nearly all Christian. Double "
        "Sighted is a Personal Power.",
    ),
    Kindred(
        "panotius",
        "Panotius (all-ear)",
        (
            ("vf_improved_abilities", ""),
            ("vf_improved_fatigue", ""),
            ("vf_minor_virtue", "Sharp Ears"),
            ("vf_personal_power_quality", "Auricular Flight"),
        ),
        (
            ("vf_major_flaw", "Age Quickly"),
            ("vf_susceptible_to_deprivation_inferiority", ""),
        ),
        122,
        "Flies on its ears (a Fatigue level, then Sta + Concentration against 6 "
        "each minute); most are Noncombatants.",
    ),
    Kindred(
        "tripithamus",
        "Tripithamus (pygmy)",
        (
            ("vf_greater_power_quality", "The Sun's Glance, Breath and Shout"),
            ("vf_form_resistance", "Ignem"),
            ("vf_improved_damage_quality", "x2, the copper sword"),
            ("vf_improved_initiative_quality", "the copper sword"),
        ),
        (
            ("vf_miniature", ""),
            ("vf_major_flaw", "Age Quickly"),
            ("vf_minor_flaw", "Small Frame"),
        ),
        122,
        "Size -3; a warrior's copper sword is a short sword at +3 Initiative and "
        "+6 Damage that flames only in a tripithamus's hand.",
    ),
    Kindred(
        "troglodyte",
        "Troglodyte (hole-creeper)",
        (
            ("vf_major_virtue", "Greater Power: Eyes of the Bat"),
            ("vf_minor_virtue", "Great Quickness, x2"),
        ),
        (
            ("vf_major_flaw", "Mute"),
            ("vf_minor_flaw", "Warped Senses: Sensitive Sight"),
            ("vf_minor_flaw", "Small Frame"),
        ),
        124,
        "Cannot bear bright light; hate snakes.",
    ),
)
#: Magic Might by the character's role (BS&S p. 120); most are Spring.
PLINIAN_MIGHT: dict[str, tuple[int, int]] = {"grog": (0, 5), "companion": (5, 15)}


def plinian_social_status(
    *,
    tribelands: bool = False,
    other_region: bool = False,
    unknown_or_hostile: bool = False,
    long_association: bool = False,
) -> str:
    """The Social Status a Plinian race member has among humans (BS&S p.
    120): any in his tribelands; an Outsider (Major) where his race is
    unknown or hostile; an Outcast when visiting another region or living
    in a town, unless his family's long association there allows a Free
    Social Status Virtue."""
    if tribelands:
        return "any Social Status"
    if unknown_or_hostile:
        return "vf_outsider_major"
    if other_region or not long_association:
        return "vf_outcast"
    return "a Free Social Status Virtue"


#: The anthropophagi's yearly feast (BS&S p. 119): one corpse feeds five;
#: a transformed human grows Disfigured after 5 feasts and must leave
#: human society after 15.
FEAST_EATERS_PER_CORPSE = 5
FEASTS_TO_DISFIGURED = 5
FEASTS_TO_LEAVE = 15


def corpses_for_feast(eaters: int) -> int:
    return round_up(max(0, eaters) / FEAST_EATERS_PER_CORPSE)


def qualities_after_missed_feasts(qualities: int, missed_years: int) -> int:
    """Without the yearly feast an anthropophagus loses a Magic Quality a
    year, until he is an ordinary mortal."""
    return max(0, qualities - max(0, missed_years))


def transformed_anthropophagus(feasts: int) -> str:
    """What a human who shares the feast (Transformed Human with Greater
    Malediction) has become after so many feasts."""
    if feasts >= FEASTS_TO_LEAVE:
        return "monstrous: he must leave human society for his new kin"
    if feasts >= FEASTS_TO_DISFIGURED:
        return "Disfigured"
    return "still human in looks"


# -- the jnun (BS&S pp. 123-125) --

#: Each kind of African jnun, and whether it is a true jinni whom Sihr
#: affects (and a sahir may summon).
JNUN: dict[str, bool] = {
    "wild jinn": True,
    "shayatin": True,
    "leriah": False,
    "lesser afarta": False,
    "greater afarta": False,
    "baharia": False,
}


def affected_by_sihr(kind: str) -> bool:
    if kind not in JNUN:
        raise ValueError(f"Unknown kind of jnun {kind!r}; one of {sorted(JNUN)}")
    return JNUN[kind]


def shapeshifter_sizes(size: int, shapeshifter: int) -> tuple[int, int]:
    """The smallest and largest Size a jinni's Donning the Corporeal Veil
    with Shapeshifter takes: base - twice the score to base + the score;
    it has as many forms as the score (p. 123)."""
    score = max(0, shapeshifter)
    return size - 2 * score, size + score
