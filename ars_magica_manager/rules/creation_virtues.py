"""Creation checks for the Virtues and Flaws step: the point
budget by character type, the book's hard limits (musts) and its guidelines
(shoulds, shown as advice with how many too many or too few).

Rules: reference/rules-engine-reference.md §5 Point costs and general
limits; Budgets by character type; Types of Virtue and Flaw.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass

from .. import catalog
from ..models import Character, Saga, TraditionDef, VirtueFlawDef
from . import animal_grogs, realms, transylvania
from . import creation_access as access
from .creation_base import CHARACTER_CHECKS, Check, Record, check, judged
from .creation_character import THE_GIFT

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 4: Virtues and Flaws, Virtues and Flaws "
    "Rules and Guidelines, p. 63"
)
BUDGET_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Detailed Character "
    "Creation Summary, p. 44"
)
TAINTED_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 4: Virtues and Flaws, Types of Virtue and "
    "Flaw, p. 63"
)

HOUSE_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Hermetic Houses Summary, "
    "p. 46"
)
TRADITION_SOURCE = (
    "Hedge Magic, Revised Edition, each tradition's Character Creation, pp. 17-141"
)

MAX_FLAW_POINTS = 10
MAX_MINOR_FLAWS = 5
GROG_MAX_FLAW_POINTS = 3
#: A Mythic Companion's bought Virtue points (2 per Flaw point, at most 20)
#: plus the free Minor Virtue.
MYTHIC_MAX_VIRTUE_POINTS = 21
MAX_TAINTED = 5
MYTHIC_MAX_TAINTED_VIRTUES = 10
#: Only a companion may be Wealthy or Poor.
COMPANION_ONLY = ("vf_wealthy", "vf_poor")


@dataclass(frozen=True)
class VirtueFlawTally:
    """The points and counts the limits look at."""

    virtue_points: int
    flaw_points: int
    minor_flaws: int
    major_virtues: int
    major_flaws: int
    social_statuses: list[str]
    major_hermetic_virtues: int
    hermetic: int
    hermetic_flaws: int
    major_personality_flaws: int
    personality_flaws: int
    story_flaws: int
    tainted_virtue_points: int
    tainted_flaw_points: int
    #: Names taken more often than the book allows.
    repeated: list[str]


def tally(character: Character) -> VirtueFlawTally:
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    # An animal's free Flaws aren't counted, and its Major Personality
    # Flaws count as Minor.
    entries = [
        (vf, entry)
        for vf in character.virtues_flaws
        if vf.vf_id in by_id
        and (entry := animal_grogs.counted(character, by_id[vf.vf_id])) is not None
    ]

    def of(side: str, category: str | None = None, tier: str | None = None):
        return [
            e
            for _, e in entries
            if e.side == side
            and (category is None or category in (e.category, *e.extra_categories))
            and (tier is None or e.tier == tier)
        ]

    counts: dict[str, int] = {}
    per_param: dict[tuple[str, tuple[tuple[str, str], ...]], int] = {}
    for vf, _ in entries:
        counts[vf.vf_id] = counts.get(vf.vf_id, 0) + 1
        key = (vf.vf_id, tuple(sorted(vf.params.items())))
        per_param[key] = per_param.get(key, 0) + 1
    repeated = []
    for vf_id, count in counts.items():
        entry = by_id[vf_id]
        limit = entry.max_count if entry.repeatable else 1
        over = limit is not None and count > limit
        over_param = entry.max_per_parameter is not None and any(
            n > entry.max_per_parameter for (i, _), n in per_param.items() if i == vf_id
        )
        if over or over_param:
            repeated.append(entry.name)
    return VirtueFlawTally(
        virtue_points=int(sum(e.cost for e in of("Virtue"))),
        flaw_points=int(-sum(e.cost for e in of("Flaw"))),
        minor_flaws=len(of("Flaw", tier="Minor")),
        major_virtues=len(of("Virtue", tier="Major")),
        major_flaws=len(of("Flaw", tier="Major")),
        social_statuses=[
            e.name
            for _, e in entries
            if "Social Status" in (e.category, *e.extra_categories)
        ],
        major_hermetic_virtues=len(of("Virtue", "Hermetic", "Major")),
        # Those only the Gifted may take: Inoffensive to (Beings) and the
        # like are Hermetic or General.
        hermetic=sum(1 for _, e in entries if catalog.needs_the_gift(e)),
        hermetic_flaws=len(of("Flaw", "Hermetic")),
        major_personality_flaws=len(of("Flaw", "Personality", "Major")),
        personality_flaws=len(of("Flaw", "Personality")),
        story_flaws=len(of("Flaw", "Story")),
        tainted_virtue_points=int(sum(e.cost for e in of("Virtue", "Tainted"))),
        tainted_flaw_points=int(-sum(e.cost for e in of("Flaw", "Tainted"))),
        repeated=sorted(repeated),
    )


@dataclass(frozen=True)
class HouseBenefit:
    """What a magus's House gives free at creation. The free
    House Virtue is outside the Virtue/Flaw balance (HOUSE_SOURCE)."""

    #: The points of the free Virtue(s) the magus holds: outside the balance.
    virtue_points: int = 0
    #: Ex Miscellanea's compulsory Major Hermetic Flaw: it pays for nothing
    #: and is outside the Flaw caps.
    flaw_points: int = 0
    #: What was counted as free ("Puissant Magic Theory").
    held: tuple[str, ...] = ()
    #: What the House gives that the magus hasn't taken yet.
    missing: tuple[str, ...] = ()
    #: Indices into character.virtues_flaws of the entries counted above:
    #: the sheet leaves them out of its points, marked Free.
    free_indices: frozenset[int] = frozenset()
    #: Who gives it, for "free from ...".
    giver: str = "the House"


def held_option(character: Character, option: dict):
    """The character's Virtue matching a House's option (its vf_id and
    params), or None."""
    wanted = {k: str(v).lower() for k, v in (option.get("params") or {}).items()}
    return next(
        (
            vf
            for vf in character.virtues_flaws
            if vf.vf_id == option["vf_id"]
            and all(str(vf.params.get(k, "")).lower() == v for k, v in wanted.items())
        ),
        None,
    )


#: The Minor Virtues HoH: Societates p. 55 names as suiting Jerbiton's free
#: Virtue (it also names Enchanting Music, which the catalog lacks).
SUITED_MINOR: frozenset[str] = frozenset(
    {
        "vf_affinity_with_ability",
        "vf_apt_student",
        "vf_book_learner",
        "vf_cautious_with_ability",
        "vf_educated",
        "vf_free_expression",
        "vf_good_teacher",
        "vf_gossip",
        "vf_inspirational",
        "vf_learn_ability_from_mistakes",
        "vf_light_touch",
        "vf_long_winded",
        "vf_piercing_gaze",
        "vf_privileged_upbringing",
        "vf_protection",
        "vf_puissant_ability",
        "vf_social_contacts",
        "vf_temporal_influence",
        "vf_troupe_upbringing",
        "vf_true_love_pc",
        "vf_venus_blessing",
        "vf_well_traveled",
    }
)


def house_benefit(character: Character) -> HouseBenefit:
    """The free House Virtue a magus holds (or still has to take)."""
    if character.type != "magus":
        return HouseBenefit()
    house = catalog.load_house_catalog_by_id().get(character.hermetic.house or "")
    if house is None:
        return HouseBenefit()
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    entries = [
        (index, by_id[vf.vf_id])
        for index, vf in enumerate(character.virtues_flaws)
        if vf.vf_id in by_id
    ]

    def first(match: Callable[[VirtueFlawDef], bool]) -> int | None:
        """The index of the first entry `match` accepts, or None."""
        return next((index for index, e in entries if match(e)), None)

    if house.virtues:
        for option in house.virtues:
            instance = held_option(character, option)
            if instance is not None and option["vf_id"] in by_id:
                entry = by_id[option["vf_id"]]
                index = next(
                    i for i, vf in enumerate(character.virtues_flaws) if vf is instance
                )
                return HouseBenefit(
                    virtue_points=int(entry.cost),
                    held=(catalog.describe_virtue_flaw(instance, by_id),),
                    free_indices=frozenset({index}),
                )
        return HouseBenefit(missing=(house.benefit,))
    if house.free == "minor_virtue":
        # Jerbiton's: a Minor Virtue of scholarship, art or dealing with
        # people, so one of the suited ones counts first (HoH: Societates
        # p. 55).
        index = first(
            lambda e: e.side == "Virtue" and e.tier == "Minor" and e.id in SUITED_MINOR
        )
        if index is None:
            index = first(lambda e: e.side == "Virtue" and e.tier == "Minor")
        if index is not None:
            return HouseBenefit(
                virtue_points=1,
                held=("one Minor Virtue",),
                free_indices=frozenset({index}),
            )
        return HouseBenefit(missing=(house.benefit,))
    if house.free == "ex_miscellanea":

        def hermetic(entry: VirtueFlawDef) -> bool:
            return "Hermetic" in (entry.category, *entry.extra_categories)

        # The magus's Ex Miscellanea tradition names the three; any match
        # counts until he has one.
        own = house_tradition(character)
        named = own.virtues if own is not None else []
        points, flaw, held, missing, free = 0, 0, [], [], set()
        for side, tier, is_hermetic, what, label in (
            (
                "Virtue",
                "Minor",
                True,
                "a free Minor Hermetic Virtue",
                "a Minor Hermetic Virtue",
            ),
            (
                "Virtue",
                "Major",
                False,
                "a free Major non-Hermetic Virtue",
                "a Major non-Hermetic Virtue",
            ),
            (
                "Flaw",
                "Major",
                True,
                "the compulsory Major Hermetic Flaw",
                "the compulsory Major Hermetic Flaw",
            ),
        ):

            def fits(
                e: VirtueFlawDef,
                side: str = side,
                tier: str = tier,
                is_hermetic: bool = is_hermetic,
            ) -> bool:
                return e.side == side and e.tier == tier and hermetic(e) == is_hermetic

            wanted = next((v for v in named if v in by_id and fits(by_id[v])), None)
            if wanted is None:
                index = first(fits)
            else:
                index = first(lambda e, w=wanted: e.id == w)
            if index is not None:
                if side == "Flaw":
                    flaw = 3
                else:
                    points += 3 if tier == "Major" else 1
                held.append(label)
                free.add(index)
            elif wanted is not None and own is not None:
                name = re.sub(r"\{(\w+)\}", lambda m: m[1].title(), by_id[wanted].name)
                missing.append(f"{name} ({what}, from the {own.name})")
            else:
                missing.append(what)
        return HouseBenefit(points, flaw, tuple(held), tuple(missing), frozenset(free))
    return HouseBenefit()


def house_tradition(character: Character) -> TraditionDef | None:
    """The House Ex Miscellanea tradition a magus belongs to, or None."""
    if character.type != "magus":
        return None
    return next(
        (t for t in access.traditions_of(character) if t.hermetic == "house"), None
    )


def tradition_benefit(character: Character) -> HouseBenefit:
    """What a Gifted member's tradition gives free at creation: the
    Virtues its Opening gives (a learned magician's Entreat the Powers)
    and the Minor Virtues taken from the master (a vitki's one Minor
    Vitkar Virtue), all outside the Virtue/Flaw balance."""
    gifted = THE_GIFT in {vf.vf_id for vf in character.virtues_flaws}
    traditions = access.traditions_of(character) if gifted else []
    if character.type == "magus" or not traditions:
        return HouseBenefit(giver="the tradition")
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    entries = [
        (index, vf, by_id[vf.vf_id])
        for index, vf in enumerate(character.virtues_flaws)
        if vf.vf_id in by_id
    ]
    points, held, missing, free = 0, [], [], set()
    for training in (t.training for t in traditions):
        for vf_id in training.opening_virtues:
            index = next((i for i, vf, _ in entries if vf.vf_id == vf_id), None)
            name = by_id[vf_id].name if vf_id in by_id else vf_id
            if index is None:
                missing.append(name)
            elif index not in free:
                points += int(by_id[vf_id].cost)
                held.append(name)
                free.add(index)
        for _ in range(training.free_minor_virtues):
            index = next(
                (
                    i
                    for i, vf, e in entries
                    if e.side == "Virtue"
                    and e.tier == "Minor"
                    and training.free_category in (e.category, *e.extra_categories)
                    and i not in free
                ),
                None,
            )
            what = f"a Minor {training.free_category} Virtue from the master"
            if index is None:
                missing.append(what)
            else:
                points += 1
                held.append(what)
                free.add(index)
    return HouseBenefit(
        virtue_points=points,
        held=tuple(held),
        missing=tuple(missing),
        free_indices=frozenset(free),
        giver="the tradition",
    )


def animal_benefit(character: Character) -> HouseBenefit:
    """The Flaws an animal grog holds free: No Hands and Mute."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    free = {
        index
        for index, vf in enumerate(character.virtues_flaws)
        if animal_grogs.free_flaw(character, vf.vf_id)
    }
    held = tuple(
        by_id[vf.vf_id].name
        for index, vf in enumerate(character.virtues_flaws)
        if index in free and vf.vf_id in by_id
    )
    return HouseBenefit(
        held=held, free_indices=frozenset(free), giver="its animal form"
    )


def royal_benefit(character: Character) -> HouseBenefit:
    """A crowned king of Slavic, Magyar or Vlach blood holds Shapeshifter
    free (Against the Dark p. 122)."""
    index = transylvania.royal_shapeshifter_index(character)
    if index is None:
        return HouseBenefit(giver="his crown")
    entry = catalog.load_virtue_flaw_catalog_by_id()[transylvania.SHAPESHIFTER]
    return HouseBenefit(
        virtue_points=int(entry.cost),
        held=(entry.name,),
        free_indices=frozenset({index}),
        giver="his crown",
    )


def _with_crown(benefit: HouseBenefit, character: Character) -> HouseBenefit:
    """`benefit` with a crowned king's free Shapeshifter added."""
    crown = royal_benefit(character)
    if not crown.free_indices:
        return benefit
    if not benefit.free_indices and not benefit.missing:
        return crown
    return HouseBenefit(
        virtue_points=benefit.virtue_points + crown.virtue_points,
        flaw_points=benefit.flaw_points,
        held=benefit.held + crown.held,
        missing=benefit.missing,
        free_indices=benefit.free_indices | crown.free_indices,
        giver=f"{benefit.giver} and {crown.giver}",
    )


def free_benefit(character: Character) -> HouseBenefit:
    """The Virtues a character has free at creation, outside the
    balance: a magus's from the House, a hedge wizard's from the
    tradition, a crowned Slavic, Magyar or Vlach king's Shapeshifter;
    the Flaws an animal holds free."""
    if character.type == "magus":
        return house_benefit(character)
    if animal_grogs.is_animal(character):
        return animal_benefit(character)
    return _with_crown(tradition_benefit(character), character)


DEVIL_CHILD, DEVIL_CHILD_POINTS = "vf_devil_child", 3


def virtue_allowance(character: Character, flaw_points: int) -> tuple[int, int]:
    """The (fewest, most) Virtue points the character's Flaw points allow:
    equal for most; a magus adds the free House Virtue held (and Ex
    Miscellanea's compulsory Flaw pays for nothing); a Mythic Companion
    gets 2 per Flaw point plus the free Minor Virtue, up to 21 (fewer is
    allowed, just unspent)."""
    if character.type == "magus":
        house = house_benefit(character)
        points = flaw_points - house.flaw_points + house.virtue_points
        return points, points
    if character.type == "mythic companion":
        # A Devil Child takes three more Virtue points free, to balance
        # Tragic Life (DE p. 56).
        devil = DEVIL_CHILD_POINTS * any(
            vf.vf_id == DEVIL_CHILD for vf in character.virtues_flaws
        )
        return 0, min(2 * flaw_points + 1, MYTHIC_MAX_VIRTUE_POINTS) + devil
    points = (
        flaw_points
        + tradition_benefit(character).virtue_points
        + royal_benefit(character).virtue_points
    )
    return points, points


def max_flaw_points(character: Character) -> int:
    return GROG_MAX_FLAW_POINTS if character.type == "grog" else MAX_FLAW_POINTS


def max_minor_flaws(character: Character) -> int:
    return GROG_MAX_FLAW_POINTS if character.type == "grog" else MAX_MINOR_FLAWS


def _check(
    label: str, ok: bool, detail: str, source: str = SOURCE, *, advice: bool = False
) -> Check:
    return judged("virtues_flaws", label, ok, detail, source, advice=advice)


def _count(count: int, limit: int) -> str:
    """ "3", or "3, 1 too many"."""
    return f"{count}" + (f", {count - limit} too many" if count > limit else "")


@check("virtues_flaws", CHARACTER_CHECKS)
def virtue_flaw_checks(saga: Saga, record: Record) -> list[Check]:
    assert isinstance(record, Character)
    t = tally(record)
    return [
        *_budget_checks(record, t),
        *_flaw_limit_checks(record, t),
        *_social_status_checks(record, t),
        *_gift_checks(record, t),
        *_personality_and_taint_checks(record, t),
        *_advice_checks(record, t),
        *_exclusion_checks(record),
        *_requirement_checks(record),
        *_realm_checks(record),
    ]


#: Virtues that need one of these others, as their descriptions say.
NEEDS_ONE_OF: dict[str, tuple[tuple[str, ...], str]] = {
    "vf_r_astradh": (
        ("vf_fury", "vf_wrathful_major"),
        "The Contested Isle, Ríastradh, p. 120",
    ),
}


def _requirement_checks(character: Character) -> list[Check]:
    """A failed check for each Virtue taken without one it needs."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    ids = {vf.vf_id for vf in character.virtues_flaws}
    found = []
    for vf_id, (needs, source) in NEEDS_ONE_OF.items():
        if vf_id in ids and not ids & set(needs):
            name = by_id[vf_id].name if vf_id in by_id else vf_id
            wanted = " or ".join(by_id[n].name if n in by_id else n for n in needs)
            found.append(
                _check(f"{name} needs {wanted}", False, "neither taken", source)
            )
    return found


#: Virtues that give a character a Might score, and its realm: such a
#: character is a member of that realm and takes no Virtue that affiliates
#: them with another (RoP: The Infernal p. 84).
MIGHT_VIRTUES: dict[str, str] = {"vf_demonic_blood": "Infernal"}
#: Virtues that affiliate a character with a realm whatever their category.
AFFILIATING: dict[str, str] = {
    THE_GIFT: "Magic",
    "vf_true_faith": "Divine",
    "vf_blood_of_the_nephilim": "Divine",
}
MIGHT_SOURCE = "Realms of Power: The Infernal, Characters with Might Scores, p. 84"


def _realm_checks(character: Character) -> list[Check]:
    """A character with a Might score takes no Virtue of another realm:
    The Gift, True Faith, Faerie Blood, or a Supernatural Virtue of
    another realm, one that names none being Magic (DE p. 64; none when
    no Virtue gives a Might)."""
    ids = [vf.vf_id for vf in character.virtues_flaws]
    realm = next((MIGHT_VIRTUES[v] for v in ids if v in MIGHT_VIRTUES), "")
    if not realm:
        return []
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    clash: list[str] = []
    for vf_id in dict.fromkeys(ids):
        entry = by_id.get(vf_id)
        if entry is None or vf_id in MIGHT_VIRTUES:
            continue
        if vf_id in AFFILIATING:
            other = AFFILIATING[vf_id]
        elif entry.type == "Virtue" and "Supernatural" in (
            entry.category,
            *entry.extra_categories,
        ):
            other = realms.virtue_realm(
                vf_id, entry.name, tainted="Tainted" in entry.extra_categories
            )
        else:
            continue
        if other != realm:
            clash.append(f"{entry.name} ({other})")
    return [
        _check(
            f"With {realm} Might, no Virtue of another realm",
            not clash,
            ", ".join(clash) or "none",
            MIGHT_SOURCE,
        )
    ]


#: Virtues that can't be taken with others, as their descriptions say.
EXCLUDES: dict[str, tuple[tuple[str, ...], str]] = {
    "vf_demonic_blood": (
        ("vf_unaging", "vf_age_quickly"),
        "Ars Magica Definitive Edition, Demonic Blood, p. 76",
    ),
    "vf_giant_blood": (
        ("vf_large", "vf_small_frame", "vf_dwarf"),
        "Ars Magica Definitive Edition, Giant Blood, p. 83",
    ),
}


def _exclusion_checks(character: Character) -> list[Check]:
    """A failed check for each pair the descriptions forbid (none when
    there is no such pair)."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    ids = {vf.vf_id for vf in character.virtues_flaws}
    found = []
    for vf_id, (others, source) in EXCLUDES.items():
        clash = [
            by_id[o].name for o in others if vf_id in ids and o in ids and o in by_id
        ]
        if clash:
            name = by_id[vf_id].name if vf_id in by_id else vf_id
            found.append(
                _check(
                    f"{name} can't be taken with {', '.join(clash)}",
                    False,
                    "both taken",
                    source,
                )
            )
    return found


def _budget_checks(character: Character, t: VirtueFlawTally) -> list[Check]:
    """Virtue points against Flaw points, and the House's free Virtue or
    compulsory Flaw."""
    fewest, most = virtue_allowance(character, t.flaw_points)
    if character.type == "mythic companion":
        found = [
            _check(
                "Virtue points: 2 per Flaw point, plus the free Minor",
                t.virtue_points <= most,
                f"{t.virtue_points} of {most}",
                BUDGET_SOURCE,
            )
        ]
        if t.virtue_points < most:
            found.append(
                _check(
                    "Virtue points spent",
                    False,
                    f"{most - t.virtue_points} unspent",
                    BUDGET_SOURCE,
                    advice=True,
                )
            )
        return found
    house = free_benefit(character)
    free = f" (free from {house.giver}: {', '.join(house.held)})" if house.held else ""
    found = [
        _check(
            "Virtue points balance Flaw points",
            fewest <= t.virtue_points <= most,
            f"{t.virtue_points} Virtue, {t.flaw_points} Flaw points" + free,
            BUDGET_SOURCE,
        )
    ]
    for what in house.missing:
        compulsory = what.startswith("the compulsory")
        found.append(
            _check(
                "Ex Miscellanea's compulsory Flaw is taken"
                if compulsory
                else f"{house.giver[0].upper()}{house.giver[1:]}'s free Virtue is taken",
                False,
                what,
                HOUSE_SOURCE if character.type == "magus" else TRADITION_SOURCE,
                advice=not compulsory,
            )
        )
    return found


def _flaw_limit_checks(character: Character, t: VirtueFlawTally) -> list[Check]:
    """How many Flaw points and Minor Flaws; a grog's no Majors."""
    # Ex Miscellanea's compulsory Flaw is on top of the normal allowance.
    counted_flaws = t.flaw_points - house_benefit(character).flaw_points
    most_points = max_flaw_points(character)
    most_minor = max_minor_flaws(character)
    found = [
        _check(
            f"At most {most_points} Flaw points",
            counted_flaws <= most_points,
            _count(counted_flaws, most_points),
        ),
        _check(
            f"At most {most_minor} Minor Flaws",
            t.minor_flaws <= most_minor,
            _count(t.minor_flaws, most_minor),
        ),
    ]
    if character.type == "grog":
        majors = t.major_virtues + t.major_flaws
        found.append(
            _check(
                "A grog takes no Major Virtues or Flaws",
                majors == 0,
                _count(majors, 0),
                BUDGET_SOURCE,
            )
        )
    return found


def _social_status_checks(character: Character, t: VirtueFlawTally) -> list[Check]:
    statuses = t.social_statuses
    found = [_check("A Social Status", bool(statuses), ", ".join(statuses) or "none")]
    if len(statuses) > 1:
        # More are allowed only where their descriptions say they fit
        # together; a grog has exactly one.
        found.append(
            _check(
                "One Social Status, unless they fit together",
                False,
                f"{len(statuses)} taken",
                advice=character.type != "grog",
            )
        )
    return found


def _gift_checks(character: Character, t: VirtueFlawTally) -> list[Check]:
    """Hermetic Virtues and Flaws, The Gift, and the companions-only ones."""
    ids = [vf.vf_id for vf in character.virtues_flaws]
    found = [
        _check(
            "At most 1 Major Hermetic Virtue",
            t.major_hermetic_virtues <= 1,
            _count(t.major_hermetic_virtues, 1),
            BUDGET_SOURCE,
        )
    ]
    gifted = THE_GIFT in ids
    if character.type != "magus" and t.hermetic and not gifted:
        found.append(
            _check(
                "Hermetic Virtues and Flaws need The Gift",
                False,
                f"{t.hermetic} taken",
                TAINTED_SOURCE,
            )
        )
    if character.type == "grog" and gifted:
        found.append(
            _check("A grog never has The Gift", False, "The Gift taken", BUDGET_SOURCE)
        )
    only = [vf_id for vf_id in ids if vf_id in COMPANION_ONLY]
    if only and character.type not in ("companion", "mythic companion"):
        by_id = catalog.load_virtue_flaw_catalog_by_id()
        found.append(
            _check(
                "Wealthy and Poor are for companions",
                False,
                ", ".join(by_id[vf_id].name for vf_id in only),
                BUDGET_SOURCE,
            )
        )
    return found


def _personality_and_taint_checks(
    character: Character, t: VirtueFlawTally
) -> list[Check]:
    """Major Personality Flaws, Tainted Virtues and Flaws, and repeats."""
    found = [
        _check(
            "At most 1 Major Personality Flaw",
            t.major_personality_flaws <= 1,
            _count(t.major_personality_flaws, 1),
        )
    ]
    if t.tainted_virtue_points or t.tainted_flaw_points:
        limit = (
            MYTHIC_MAX_TAINTED_VIRTUES
            if character.type == "mythic companion"
            else MAX_TAINTED
        )
        found.append(
            _check(
                f"Tainted Virtues at most {limit} points",
                t.tainted_virtue_points <= limit,
                _count(t.tainted_virtue_points, limit),
                TAINTED_SOURCE,
            )
        )
        found.append(
            _check(
                f"Tainted Flaws at most {MAX_TAINTED} points",
                t.tainted_flaw_points <= MAX_TAINTED,
                _count(t.tainted_flaw_points, MAX_TAINTED),
                TAINTED_SOURCE,
            )
        )
    if t.repeated:
        found.append(
            _check("Each taken only as often as allowed", False, ", ".join(t.repeated))
        )
    return found


def _advice_checks(character: Character, t: VirtueFlawTally) -> list[Check]:
    """The book's "should"s: advice, never a must."""
    grog = character.type == "grog"
    found: list[Check] = []
    if character.type == "magus":
        found.append(
            _check(
                "A magus should have a Hermetic Flaw",
                t.hermetic_flaws >= 1,
                f"{t.hermetic_flaws}" + ("" if t.hermetic_flaws else ", 1 too few"),
                BUDGET_SOURCE,
                advice=True,
            )
        )
    limit = 0 if grog else 1
    found.append(
        _check(
            "A grog should have no Story Flaws" if grog else "At most 1 Story Flaw",
            t.story_flaws <= limit,
            _count(t.story_flaws, limit),
            advice=True,
        )
    )
    limit = 1 if grog else 2
    found.append(
        _check(
            f"At most {limit} Personality Flaw{'s' if limit > 1 else ''}",
            t.personality_flaws <= limit,
            _count(t.personality_flaws, limit),
            advice=True,
        )
    )
    return found
