"""Labor and trade (City & Guild): what Labor Points are worth in money,
Labor Points from stories, and the investments a merchant makes with
his surplus.

- Income bands (p. 37): the frivolous spending money a business leaves a
  year, Trivial 10 pounds to Legendary 1,000, bought by the Social Status
  Virtue.
- Money (p. 40, as the Errata p. 56 corrects it): 9 Labor Points are
  worth about a quarter of a year's income: 2.5 pounds to a Trivial
  income ... 250 to a Legendary one. So a Labor Point is worth the year's
  income / 36, rounded to the nearest pound (Covenants p. 56). The table
  invests money into a business; Labor Points are not sold for money.
- A season's worth of Labor Points (p. 39): (primary Characteristic +
  Craft) or (Communication + Profession) x the Wealth Multiplier. A
  story gives a number of seasons' worth when its central issue is
  resolved (the guide on p. 39 and each story seed's own award, pp.
  111-133); fractions round down (DE p. 6).
- Investments for all merchants (pp. 110-114): charity, commodity
  speculation, drawings, introduction agent, marriage broker, legal
  action, foreseeing a boom; and by kind of merchant: smuggling (local
  carrier, p. 117), change of government and young talent (factor, pp.
  122, 128), a lavish party (capo, p. 129). The stories for each kind of
  merchant suit the richer kinds too (p. 111).
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Character, Investment
from . import supplement_work as sw
from .rounding import round_down, round_nearest, round_up
from .scores import ability_level

SOURCE = (
    "City & Guild, Chapter Two: Labor, pp. 37-40 (Errata p. 56); Chapter "
    "Seven: Trade, pp. 107-133"
)

# -- income bands and money -------------------------------------------------

#: Each band's yearly income in pounds (p. 37), poorest first.
BANDS: dict[str, int] = {
    "trivial": 10,
    "minor": 20,
    "lesser": 40,
    "typical": 100,
    "greater": 250,
    "legendary": 1000,
}
#: The bands each Social Status Virtue buys (p. 37), the first the
#: default. Merchant Venturer is the Merchant Adventurer Virtue; no
#: starting character has a Legendary income (p. 38).
STATUS_BANDS: dict[str, tuple[str, ...]] = {
    "vf_laborer": ("trivial",),
    "vf_journeyman": ("trivial",),
    "vf_craftsman": ("trivial", "minor"),
    "vf_guild_master": ("minor", "lesser"),
    "vf_merchant": ("minor", "lesser"),
    "vf_senior_master": ("lesser", "typical"),
    "vf_merchant_adventurer": ("typical",),
    "vf_factor": ("typical", "greater"),
    "vf_guild_dean": ("typical", "greater"),
    "vf_capo": ("greater",),
}
#: Labor Points worth a quarter of a year's income (Errata p. 56, for
#: City & Guild p. 40's "6 from a Poor person, 12 from an average...").
LP_PER_QUARTER = 9
QUARTERS = 4


def band_label(band: str) -> str:
    return f"{band.title()} ({BANDS[band]:,} pounds a year)" if band in BANDS else ""


def default_band(character: Character) -> str:
    """The band the Social Status Virtue buys first ("" with none)."""
    for vf in character.virtues_flaws:
        if vf.vf_id in STATUS_BANDS:
            return STATUS_BANDS[vf.vf_id][0]
    return ""


def band(character: Character) -> str:
    """The business's income band: as set, else the Social Status
    Virtue's."""
    return (
        character.income_band
        if character.income_band in BANDS
        else default_band(character)
    )


def lp_value(points: int, income_band: str) -> float:
    """What `points` Labor Points are worth in pounds to a business of
    `income_band`: 9 a quarter of its year's income."""
    return points * BANDS[income_band] / (QUARTERS * LP_PER_QUARTER)


def pounds_text(pounds: float) -> str:
    """A sum of money as the books round it: to the nearest pound
    (Covenants p. 56), or to the shilling under ten pounds (2.5 pounds)."""
    if abs(pounds) >= 10:
        return f"{round_nearest(pounds):,} pounds"
    shillings = round_nearest(pounds * 20)
    return f"{shillings / 20:g} pounds" if shillings else "less than a shilling"


def lp_for_money(pounds: int, income_band: str) -> int:
    """The Labor Points `pounds` put into a business of `income_band`
    buy: the table read the other way, rounded down."""
    return round_down(pounds * QUARTERS * LP_PER_QUARTER / BANDS[income_band])


def value_line(character: Character) -> str:
    """What the character's Labor Points are worth to his business, or ""
    with no income band."""
    found = band(character)
    if not found:
        return ""
    return (
        f"Worth about {pounds_text(lp_value(character.labor_points, found))} to "
        f"a {found.title()} income: {LP_PER_QUARTER} Labor Points are a quarter "
        f"of its {BANDS[found]:,} pounds a year (City & Guild p. 40; Errata p. 56)"
    )


# -- a season's worth -------------------------------------------------------


def work_abilities(character: Character) -> list[str]:
    """The Craft and Profession Abilities the character works with."""
    return [
        a.name
        for a in character.abilities
        if a.name.startswith(("Craft", "Profession"))
    ]


def default_characteristic(ability: str) -> str:
    """Communication for a Profession, else the app's primary
    Characteristic for a Craft, Dexterity (as a working season counts)."""
    return "communication" if ability.startswith("Profession") else "dexterity"


def season_labor(character: Character, ability: str, characteristic: str) -> int:
    """A season's worth of Labor Points: (Characteristic + Ability) x the
    Wealth Multiplier (p. 39)."""
    value = getattr(character.characteristics, characteristic.lower(), 0)
    return max(
        0, (value + ability_level(character, ability)) * sw.multiplier(character)
    )


def seasons_text(seasons: float) -> str:
    whole, half = int(seasons), seasons - int(seasons) >= 0.5
    if not whole and not half:
        return "no Labor Points"
    words = f"{whole}{'½' if half else ''}" if whole else "½"
    return f"{words} season{'s' if seasons > 1 else ''}"


def worth_text(seasons: float) -> str:
    """ "½ season's worth", "2 seasons' worth"."""
    words = seasons_text(seasons)
    if seasons <= 0:
        return words
    return f"{words}'s worth" if seasons <= 1 else f"{words}' worth"


def award_points(season: int, seasons: float) -> int:
    """`seasons` seasons' worth of Labor Points, rounded down (DE p. 6)."""
    return round_down(season * seasons)


# -- the kinds of merchant --------------------------------------------------

URBAN, CARRIER, ADVENTURER, FACTOR, CAPO = (
    "urban merchant",
    "local carrier",
    "merchant adventurer",
    "factor",
    "capo",
)
#: Each kind's Social Status Multiplier for a charity's crowd (p. 110),
#: in ascending order of wealth (p. 107).
STATUS_MULTIPLIER: dict[str, int] = {
    URBAN: 1,
    CARRIER: 2,
    ADVENTURER: 3,
    FACTOR: 4,
    CAPO: 5,
}
_RANK = {kind: rank for rank, kind in enumerate(STATUS_MULTIPLIER)}
#: The kinds a Social Status Virtue makes a trader (pp. 107-109): the
#: Merchant Virtue suits urban merchants and local carriers; a Partner may
#: act in any role but capo, a Redcap in any (p. 108).
VIRTUE_KINDS: dict[str, tuple[str, ...]] = {
    "vf_merchant": (URBAN, CARRIER),
    "vf_merchant_adventurer": (ADVENTURER,),
    "vf_factor": (FACTOR,),
    "vf_capo": (CAPO,),
    "vf_partner": (URBAN, CARRIER, ADVENTURER, FACTOR),
    "vf_redcap": (URBAN, CARRIER, ADVENTURER, FACTOR, CAPO),
}


def merchant_kinds(character: Character) -> tuple[str, ...]:
    """The kinds of merchant the character's Social Status makes them
    (none for one who isn't a trader)."""
    found: list[str] = []
    for vf in character.virtues_flaws:
        for kind in VIRTUE_KINDS.get(vf.vf_id, ()):
            if kind not in found:
                found.append(kind)
    return tuple(sorted(found, key=_RANK.__getitem__))


def is_merchant(character: Character) -> bool:
    return bool(merchant_kinds(character))


def suits(kind: str, kinds: tuple[str, ...]) -> bool:
    """Whether what suits `kind` of merchant suits one of `kinds`: a
    poorer kind's stories suit the richer ones (p. 111)."""
    return kind == "" or any(_RANK[k] >= _RANK[kind] for k in kinds)


def earns_labor(character: Character) -> bool:
    """Whether the character works for Labor Points: a Craft or
    Profession, Labor Points already, or a trader's Social Status."""
    return bool(
        work_abilities(character) or character.labor_points or is_merchant(character)
    )


# -- Labor Points from stories ----------------------------------------------


@dataclass(frozen=True)
class StoryAward:
    """A story's award in seasons' worth of Labor Points: its key, what
    it is, the seasons, the page, and the kind of merchant it suits ("":
    any character who works, the guide's)."""

    key: str
    label: str
    seasons: float
    page: int
    kind: str = ""
    #: What else it does, for the troupe to apply.
    also: str = ""


_ALL = "all"
#: The guide (p. 39), then the story seeds' awards, by the kind of
#: merchant they suit ("all": every trader).
STORY_AWARDS: tuple[StoryAward, ...] = (
    StoryAward("subplot", "A subplot of a bigger story the magi deal with", 0.5, 39),
    StoryAward("danger", "Severe danger or hardship to finish the subplot", 1, 39),
    StoryAward("pivotal", "His subplot is pivotal to the main story's end", 1.5, 39),
    StoryAward("central", "He is the story's central character", 2, 39),
    StoryAward(
        "repercussions",
        "Failure would bring severe repercussions on his city or covenant",
        2.5,
        39,
    ),
    StoryAward("old_friend", "Saving the business of an old friend", 1, 39, _ALL),
    StoryAward(
        "archeology",
        "Archeological find",
        0.5,
        111,
        _ALL,
        "A failed attempt may give a poor Reputation.",
    ),
    StoryAward("boom_speculate", "Boom: speculating on it", 0.5, 111, _ALL),
    StoryAward("boom_industry", "Boom: entering the new industry", 1.5, 111, _ALL),
    StoryAward("crop_failure", "Crop failure: rescuing the town", 3, 112, _ALL),
    StoryAward("new_substitute", "New product: a substitute", 2, 112, _ALL),
    StoryAward(
        "new_industries", "New product: one that spawns industries", 4, 112, _ALL
    ),
    StoryAward(
        "new_fairs",
        "New product: in every fair of Europe",
        0,
        112,
        _ALL,
        "It promotes him to Wealthy, or, already Wealthy, to the average of "
        "the next Social Status: change his Virtues by hand.",
    ),
    StoryAward("hard_time", "Hard time: a friend rehabilitated", 1, 114, _ALL),
    StoryAward("legal_witness", "Legal action: the witness found", 1, 114, _ALL),
    StoryAward("legacy", "Legacy puzzle", 1.5, 114, _ALL),
    StoryAward("magical_item", "Magical item traced to its source", 1, 114, _ALL),
    StoryAward(
        "mania_weather",
        "Mania: weathering it",
        0.5,
        114,
        _ALL,
        "Refusing to take part in a mania earns a poor Reputation.",
    ),
    StoryAward(
        "mania_friends",
        "Mania: saving a large group of friends",
        1.5,
        114,
        _ALL,
        "An Unraveling Economy story often follows.",
    ),
    StoryAward("mania_timing", "Mania: buying early, selling in time", 1, 114, _ALL),
    StoryAward(
        "murder",
        "Murder of or by a benefactor",
        1.5,
        114,
        _ALL,
        "With the Heir Virtue it may raise his Social Status at once instead.",
    ),
    StoryAward("disaster", "Natural disaster: consortia formed", 1.5, 115, _ALL),
    StoryAward("prodigal", "The prodigal returns", 0, 115, _ALL),
    StoryAward("snub", "Public snub: a proportionate retaliation", 0.5, 115, _ALL),
    StoryAward("street_gang", "Street gang of children", 0.5, 115, _ALL),
    StoryAward("superior", "Superior going to pieces", 1, 115, _ALL),
    StoryAward("unraveling", "Unraveling economy", 1, 115, _ALL),
    StoryAward("abduction", "Abduction or elopement", 1, 116, CARRIER),
    StoryAward("rock", "Accident: a ship refloated", 1, 116, CARRIER),
    StoryAward("wagon", "Accident: an overturned wagon", 0.5, 116, CARRIER),
    StoryAward("holed", "Accident: a ship fatally holed", 1, 116, CARRIER),
    StoryAward("wreck", "Accident: a wreck salvaged", 1, 117, CARRIER),
    StoryAward("brigands", "Brigands", 1.5, 117, CARRIER),
    StoryAward("oasis", "Oasis", 1.5, 117, CARRIER),
    StoryAward(
        "smugglers_den",
        "Smuggling: a smugglers' den set up",
        1.5,
        117,
        CARRIER,
        "Smugglers have the Dark Secret Flaw and the Social Contacts Virtue.",
    ),
    StoryAward("stowaway", "Stowaway", 0.5, 117, CARRIER),
    StoryAward("the_dead", "Transporting the dead", 1, 117, CARRIER),
    StoryAward("vanished", "Vanished village", 1.5, 117, CARRIER),
    StoryAward("reprisal", "Writ of reprisal", 1, 118, CARRIER),
    StoryAward("loot", "Amphibious assault: loot and burn", 1, 119, ADVENTURER),
    StoryAward(
        "selective", "Amphibious assault: selective destruction", 1.5, 119, ADVENTURER
    ),
    StoryAward(
        "beachhead", "Amphibious assault: an invasion's beachhead", 2, 119, ADVENTURER
    ),
    StoryAward(
        "sailing_instructions",
        "Antique sailing instructions (½ to 1½: change the seasons)",
        1,
        119,
        ADVENTURER,
    ),
    StoryAward(
        "convoy",
        "Convoys and caravans: one led",
        1,
        119,
        ADVENTURER,
        "Success raises his Reputation; failure damages it.",
    ),
    StoryAward(
        "convoy_invested",
        "Convoys and caravans: a season leading them, invested",
        0.5,
        119,
        ADVENTURER,
    ),
    StoryAward(
        "customs_mission", "Customs agent: a mission played", 1, 120, ADVENTURER
    ),
    StoryAward(
        "customs_office",
        "Customs agent: a season in office, unplayed",
        0.5,
        120,
        ADVENTURER,
    ),
    StoryAward(
        "investors",
        "Finding investors: the sponsor impressed",
        1,
        120,
        ADVENTURER,
        "A new backer is needed each voyage until his Reputation is 3 or more.",
    ),
    StoryAward(
        "investors_invested", "Finding investors, invested", 0.5, 120, ADVENTURER
    ),
    StoryAward("pirate_lair", "Pirate hunting: the lair found", 1, 120, ADVENTURER),
    StoryAward(
        "pirate_nest", "Pirate hunting: the nest burned out", 1.5, 120, ADVENTURER
    ),
    StoryAward(
        "pirate_fleet", "Pirate hunting: in the fleet's assault", 1, 120, ADVENTURER
    ),
    StoryAward(
        "pirate_leader", "Pirate hunting: leading the fleet", 1.5, 120, ADVENTURER
    ),
    StoryAward("remittance", "Remittance shipment", 1, 120, ADVENTURER),
    StoryAward(
        "remittance_attacked", "Remittance shipment, attacked", 1.5, 120, ADVENTURER
    ),
    StoryAward("seeking", "Seeking things (a story or invested)", 0.5, 120, ADVENTURER),
    StoryAward(
        "blockade",
        "Blockade running",
        1.5,
        121,
        ADVENTURER,
        "A seasonal Dexterity + Profession roll against 15; failing, the "
        "blockaders know him and fight.",
    ),
    StoryAward(
        "blockade_invested",
        "Blockade running, invested",
        1,
        121,
        ADVENTURER,
        "A seasonal Dexterity + Profession roll against 15.",
    ),
    StoryAward(
        "government", "Change of government: an opponent won over", 1, 122, FACTOR
    ),
    StoryAward("rivals_held", "Foreign rivals held off", 2, 123, FACTOR),
    StoryAward(
        "rivals_partners", "Foreign rivals made junior partners", 1.5, 123, FACTOR
    ),
    StoryAward(
        "rivals_sold", "Foreign rivals: selling out comfortably", 1, 123, FACTOR
    ),
    StoryAward("wrecks", "Recovering wrecks", 1, 126, FACTOR),
    StoryAward(
        "repossess_merchant",
        "Repossession: from a merchant or craftsman",
        0.5,
        126,
        FACTOR,
    ),
    StoryAward(
        "repossess_guildsman", "Repossession: from a powerful guildsman", 1, 126, FACTOR
    ),
    StoryAward(
        "repossess_noble", "Repossession: from a priest or nobleman", 1.5, 126, FACTOR
    ),
    StoryAward(
        "repossess_guildsman_invested",
        "Repossession invested: from a powerful guildsman",
        0.5,
        126,
        FACTOR,
    ),
    StoryAward(
        "repossess_noble_invested",
        "Repossession invested: from a priest or nobleman",
        1,
        126,
        FACTOR,
    ),
    StoryAward("nobles", "Resisting nobles: a noble turned aside", 1, 126, FACTOR),
    StoryAward("withdrawal", "Withdrawal from a region", 1.5, 128, FACTOR),
    StoryAward(
        "young_talent",
        "Young talent recruited",
        1,
        128,
        FACTOR,
        "The recruit owes him a Favor.",
    ),
    StoryAward(
        "factor_cleanup", "Selecting factors: cleaning up after one", 1, 129, CAPO
    ),
    StoryAward(
        "factor_early",
        "Selecting factors: one dealt with in time",
        1.5,
        129,
        CAPO,
        "Only with the partners' support.",
    ),
    StoryAward("branch", "Founding a branch", 0.5, 130, CAPO),
)
STORY_BY_KEY = {award.key: award for award in STORY_AWARDS}
#: The seasons' worth a story can be changed to.
SEASON_CHOICES: tuple[float, ...] = (0.5, 1, 1.5, 2, 2.5, 3, 4)
_GROUPS = {
    "": "Guide",
    _ALL: "Any merchant",
    CARRIER: "Local carrier",
    ADVENTURER: "Merchant adventurer",
    FACTOR: "Factor",
    CAPO: "Capo",
}


def stories_for(character: Character) -> list[StoryAward]:
    """The awards that suit the character: the guide's for anyone, the
    merchants' by their kind (and the poorer kinds')."""
    kinds = merchant_kinds(character)
    return [
        award
        for award in STORY_AWARDS
        if award.kind == ""
        or (kinds and (award.kind == _ALL or suits(award.kind, kinds)))
    ]


def story_label(award: StoryAward) -> str:
    return (
        f"{_GROUPS[award.kind]}: {award.label} ({seasons_text(award.seasons)}, "
        f"p. {award.page})"
    )


# -- investments ------------------------------------------------------------

CHARITY, SPECULATION, END = "charity", "speculation", "end"
DRAWINGS, INTRODUCTION, MARRIAGE = "drawings", "introduction", "marriage"
LEGAL, BOOM, MONEY = "legal", "boom", "money"
SMUGGLING, SPONSOR = "smuggling", "sponsor"
GOVERNMENT, TALENT, PARTY = "government", "talent", "party"


@dataclass(frozen=True)
class InvestmentKind:
    key: str
    label: str
    page: int
    #: The kind of merchant it suits ("all": any trader; "": anyone who
    #: works for Labor Points).
    kind: str = _ALL


INVESTMENTS: tuple[InvestmentKind, ...] = (
    InvestmentKind(MONEY, "Put money into the business", 40, ""),
    InvestmentKind(CHARITY, "Charity", 110),
    InvestmentKind(SPECULATION, "Commodity speculation", 110),
    InvestmentKind(END, "End an investment (a speculation's back)", 110),
    InvestmentKind(DRAWINGS, "Drawings: sumptuous items", 111),
    InvestmentKind(INTRODUCTION, "Introduction agent", 111),
    InvestmentKind(MARRIAGE, "Marriage broker", 111),
    InvestmentKind(LEGAL, "Legal action", 114),
    InvestmentKind(BOOM, "Foreseeing a boom", 111),
    InvestmentKind(SMUGGLING, "A season smuggling", 117, CARRIER),
    InvestmentKind(SPONSOR, "Sponsoring smugglers", 117, CARRIER),
    InvestmentKind(GOVERNMENT, "Change of government", 122, FACTOR),
    InvestmentKind(TALENT, "Young talent", 128, FACTOR),
    InvestmentKind(PARTY, "A lavish party", 129, CAPO),
)
INVESTMENT_BY_KEY = {kind.key: kind for kind in INVESTMENTS}
#: What an introduction costs and pays back, in seasons' worth, and when
#: (p. 111); a marriage's cost and how long its Social Contacts last.
INTRODUCTION_COST, INTRODUCTION_RETURN, INTRODUCTION_YEARS = 2, 3, 2
MARRIAGE_COST, MARRIAGE_YEARS = 2, 3
#: A speculation pays 1 Labor Point a year for each 10 (p. 110).
SPECULATION_PER = 10
#: Legal action: half a season's worth a suit, and the roll's modifiers
#: for a true, false or outlandish suit (p. 114).
LEGAL_COST = 0.5
SUIT_MODIFIERS: dict[str, int] = {"true": 3, "": 0, "false": -3, "outlandish": -6}
#: Foreseeing a boom (pp. 111-112): seasons back for each one set aside.
BOOM_PREPARED, BOOM_EARLY = 18, 15
BOOM_LOSS = 6
#: A lavish party: a Favor for each 5 points, rounded up (p. 129); young
#: talent's for each 10 Labor Points (p. 128).
PARTY_PER_FAVOR, TALENT_PER_FAVOR = 5, 10


def investments_for(character: Character) -> list[InvestmentKind]:
    kinds = merchant_kinds(character)
    return [
        k
        for k in INVESTMENTS
        if k.kind == "" or (kinds and (k.kind == _ALL or suits(k.kind, kinds)))
    ]


def speculation_return(points: int) -> int:
    return points // SPECULATION_PER


def speculation_guards(points: int, season: int) -> int:
    """One guard for each half-season's worth invested (p. 110)."""
    half = season // 2
    return points // half if half > 0 else 0


def drawings_cost(items: int, wealth_multiplier: int) -> int:
    """Each sumptuous item of hand-tool size costs 1 x the Wealth
    Multiplier (p. 111)."""
    return items * wealth_multiplier


def charity_xp(given: int, season: int) -> int:
    """The Reputation experience all the Labor Points given are worth: 1
    for each season's worth (p. 110), trickled in over the years."""
    return given // season if season > 0 else 0


def crowd(communication: int, leadership: int, reputation: int, kind: str) -> int:
    """How many the charity's people send at short notice: (Communication
    + Leadership) x the charity's Reputation x the Social Status
    Multiplier; twice as many with a week's notice (p. 110)."""
    return max(0, (communication + leadership) * reputation * STATUS_MULTIPLIER[kind])


def gave_lately(record: Investment, year: int, wealth_multiplier: int) -> bool:
    """Whether a charity had at least 1 x the Wealth Multiplier in the past
    year: the last gift, made this year or last."""
    return record.year >= year - 1 and record.returns >= wealth_multiplier


def legal_result(mine: int, theirs: int, suit: str) -> bool:
    """Whether his representative's Intelligence + Civil or Canon Law roll,
    with the suit's modifier, beats the opponent's (p. 114). A tie wins
    nothing."""
    return mine + SUIT_MODIFIERS.get(suit, 0) > theirs


def boom_return(total: int, set_aside: int, botched: bool) -> tuple[int, str]:
    """What foreseeing a boom gives back for the Labor Points set aside,
    and what it means (pp. 111-112): 18 or more, two seasons' for each
    one; 15 to 17, one and a half; 7 to 14, nothing gained; 6 or less, 2
    of every 10 lost; a botch, the business destroyed."""
    if botched:
        return set_aside, (
            "A botch: his business is destroyed (the troupe decides what is left)."
        )
    if total >= BOOM_PREPARED:
        return set_aside * 2, "Prepared years ahead: two seasons back for each one."
    if total >= BOOM_EARLY:
        return round_down(set_aside * 1.5), (
            "In at the start: a season and a half back for each one, this one year."
        )
    if total > BOOM_LOSS:
        return set_aside, "No advantage."
    return set_aside - round_down(set_aside * 2 / 10), "2 of every 10 lost."


def favors(points: int, per: int) -> int:
    return round_up(points / per) if points > 0 else 0


def smuggling_season(character: Character) -> int:
    """A season smuggling: (Intelligence + Intrigue) x the Wealth
    Multiplier (p. 117)."""
    return max(
        0,
        (character.characteristics.intelligence + ability_level(character, "Intrigue"))
        * sw.multiplier(character),
    )


def government_points(character: Character) -> int:
    """Change of government, invested: (Communication + Intrigue) x the
    Wealth Multiplier (p. 122)."""
    return max(
        0,
        (character.characteristics.communication + ability_level(character, "Intrigue"))
        * sw.multiplier(character),
    )


def talent_points(character: Character) -> int:
    """Young talent, invested: (Communication + Leadership) x the Wealth
    Multiplier (p. 128)."""
    return max(
        0,
        (
            character.characteristics.communication
            + ability_level(character, "Leadership")
        )
        * sw.multiplier(character),
    )


def party_total(
    die: int, characteristic: int, ability: int, pounds: int, intrigue: int
) -> int:
    """A lavish party: die + Characteristic + the theme's Ability + a
    point a pound spent, at most his Intrigue (p. 129)."""
    return die + characteristic + ability + min(max(0, pounds), max(0, intrigue))


def area_lore(character: Character) -> int:
    return max(
        (a.level for a in character.abilities if a.name.startswith("Area Lore")),
        default=0,
    )


# -- each year --------------------------------------------------------------


def year_returns(character: Character, year: int) -> list[tuple[str, int]]:
    """What the open investments give in Winter of `year`, with what
    gives it: each speculation 1 a year for each 10, a sponsor of smugglers
    his season's worth, from the year after each began; an introduction
    its three seasons' worth in its second year, closing it. A marriage
    broker's Social Contacts end in their third year (0 Labor Points)."""
    found: list[tuple[str, int]] = []
    kept: list[Investment] = []
    for record in character.investments:
        named = f" ({record.name})" if record.name else ""
        if record.kind == SPECULATION and year > record.year:
            found.append((f"Speculation{named}", speculation_return(record.lp)))
        elif record.kind == SPONSOR and year > record.year:
            found.append((f"Sponsoring smugglers{named}", record.returns))
        elif record.kind == INTRODUCTION and year >= (record.due_year or year):
            found.append((f"Introduction{named}", record.returns))
            continue
        elif record.kind == MARRIAGE and year >= (record.due_year or year):
            found.append((f"Marriage brokered{named}: its Social Contacts end", 0))
            continue
        kept.append(record)
    character.investments = kept
    return found


def investment_lines(character: Character, year: int) -> list[str]:
    """The Planning tab's lines on the open investments."""
    wm = sw.multiplier(character)
    lines: list[str] = []
    for record in character.investments:
        named = f" ({record.name})" if record.name else ""
        if record.kind == SPECULATION:
            lines.append(
                f"Speculation{named}: {record.lp} Labor Points, "
                f"+{speculation_return(record.lp)} a year"
            )
        elif record.kind == SPONSOR:
            lines.append(f"Sponsoring smugglers{named}: +{record.returns} a year")
        elif record.kind == INTRODUCTION:
            lines.append(
                f"Introduction{named}: {record.returns} back in Winter "
                f"{record.due_year}; the junior merchant owes a Favor until then"
            )
        elif record.kind == MARRIAGE:
            lines.append(
                f"Marriage brokered{named}: Social Contacts until Winter "
                f"{record.due_year}"
            )
        elif record.kind == CHARITY:
            lines.append(_charity_line(character, record, year, wm))
    return lines


def _charity_line(character: Character, record: Investment, year: int, wm: int) -> str:
    named = f" ({record.name})" if record.name else ""
    text = f"Charity{named}: {record.lp} Labor Points given"
    kinds = merchant_kinds(character)
    reputation = next(
        (r for r in character.reputations if r.name == record.reputation), None
    )
    kind = record.merchant if record.merchant in STATUS_MULTIPLIER else ""
    kind = kind or (kinds[0] if kinds else "")
    if not gave_lately(record, year, wm) or reputation is None or not kind:
        return text + f"; a crowd needs {wm} given in the past year"
    called = crowd(
        character.characteristics.communication,
        ability_level(character, "Leadership"),
        reputation.score,
        kind,
    )
    return text + f"; a crowd of {called} at short notice, {called * 2} with a week's"
