"""The Covenant and its diary."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypedDict

from ..arts import ART_BY_NAME
from .common import SEASONS, known_fields, move_secrets
from .hermetic_projects import HermeticProject, projects_from
from .holdings import Arrival, Economics, Inhabitant, Loyalty, Population, Possession
from .land_shaping import LandProject
from .stops import CovenantStop, RouteStop, route_from, stops_from
from .traits import ScoredTrait, VirtueFlawInstance
from .world import FULL, Attitude, Favour, Link, read_standing

#: A Covenant Diary entry's categories, in the spec's order.
COVENANT_DIARY_CATEGORIES: tuple[str, ...] = (
    "Improvements",
    "Purchases & Sales",
    "Vis",
    "Library",
    "Inhabitants",
    "Membership",
    "Council",
    "Laboratories",
    "Loyalty Event",
    "Year-end Accounts",
    "Defence & Magic",
    "Politics",
    "Favours",
    "Covenant Season",
    "Story Event",
    "Chapter",
)
#: The category whose entries have a Status, a linked Boon/Hook and a
#: Revisit year.
STORY_EVENT = "Story Event"
#: The category of a chapter: what the troupe did when it took up a
#: story (its `story_id`) or a threat (its `threat_id`).
CHAPTER = "Chapter"
#: A Story Event's Status: still to be told, told, or grown into a
#: threat of the Region (open_stories).
STORY_EVENT_STATUSES: tuple[str, ...] = ("Open", "Resolved", "Grown into a threat")


def _inhabitant_from_dict(data: dict[str, Any]) -> Inhabitant:
    """An inhabitant line, its arrivals made records."""
    d = known_fields(Inhabitant, data)
    d["arrivals"] = [Arrival(**known_fields(Arrival, a)) for a in d.get("arrivals", [])]
    return Inhabitant(**d)


@dataclass
class CovenantDiaryEntry:
    """One entry on the covenant's Diary tab: what happened and
    when, with optional amounts. Only `loyalty` changes the sheet (it adds
    into the Loyalty block's Actions and Events); pounds and vis are a
    record. `status`, `boon_hook_id` (a VirtueFlawInstance.id among the
    covenant's Boons/Hooks) and `revisit_year` are for Story Events, as
    are `concerns` (what the story is about: "" the covenant, "region",
    or "characters:<id>" / "laboratories:<id>") and `threat_id` (the
    threat it grew into). `id` names a story once it has a chapter; a
    Chapter's `story_id` is its story's id, or its `threat_id` the threat
    it took up;
    `build_points` for a Story Event linked to a Hidden Resources Boon: the
    points of that Boon's pool it unlocked."""

    year: int
    season: str = "Spring"  # one of SEASONS
    name: str = ""
    details: str = ""
    category: str = ""  # one of COVENANT_DIARY_CATEGORIES, or ""
    pounds: float | None = None  # + received, - spent
    vis_pawns: int | None = None  # + gained, - spent
    vis_art: str = ""  # one of ARTS, or ""
    loyalty: int | None = None
    status: str = ""  # Story Events: one of STORY_EVENT_STATUSES
    boon_hook_id: str | None = None
    revisit_year: int | None = None
    build_points: int | None = None
    concerns: str = ""
    threat_id: str | None = None
    id: str = ""
    story_id: str = ""


class HistoryEra(TypedDict):
    """An era of a covenant's History tab: its name and the year it
    begins; it runs to the next era's."""

    name: str
    year: int


def history_from(data: object, covenant: str) -> dict[str, Any]:
    """A covenant's saved History settings, checked: `eras` (HistoryEra
    dicts), `left_out` (the keys of entries left out) and `show_left_out`
    (whether they are listed) and `hidden_sources` (the records whose
    entries it hides)."""
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"{covenant!r}'s history should be a mapping, not {data!r}.")
    eras: list[HistoryEra] = []
    for era in data.get("eras") or []:
        if not isinstance(era, dict) or not isinstance(era.get("year"), int):
            raise ValueError(
                f"{covenant!r}'s history has an era without a year: {era!r}."
            )
        eras.append(HistoryEra(name=str(era.get("name") or ""), year=era["year"]))
    left_out = data.get("left_out") or []
    if not isinstance(left_out, list):
        raise ValueError(
            f"{covenant!r}'s history should list what is left out, not {left_out!r}."
        )
    found: dict[str, Any] = {}
    if eras:
        found["eras"] = eras
    if left_out:
        found["left_out"] = [str(key) for key in left_out]
    if data.get("show_left_out"):
        found["show_left_out"] = True
    hidden = data.get("hidden_sources") or []
    if not isinstance(hidden, list):
        raise ValueError(
            f"{covenant!r}'s history should list the records it hides, not {hidden!r}."
        )
    if hidden:
        found["hidden_sources"] = [str(key) for key in hidden]
    return found


#: A charter clause's status (Covenants p. 35: only breaking the charter
#: is censured). An amended clause keeps a note of what changed; the
#: earlier wording is not kept.
CLAUSE_IN_FORCE, CLAUSE_AMENDED, CLAUSE_BROKEN = "In force", "Amended", "Broken"
CLAUSE_STATUSES: tuple[str, ...] = (CLAUSE_IN_FORCE, CLAUSE_AMENDED, CLAUSE_BROKEN)

#: The sections of a Charter of Covenant, in the book's order (Covenants
#: pp. 33-35). A clause may name one; the list groups clauses under them.
CHARTER_SECTIONS: tuple[str, ...] = (
    "Oath of Covenant",
    "Membership",
    "Method of Governance",
    "Covenant Resources",
    "Member Rights",
    "Member Obligations",
    "Censure",
)


def _optional_year(value: Any, what: str) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{what}: the year should be a number, not {value!r}.")
    return value


def _season(value: Any, what: str) -> str:
    season = str(value or "")
    if season and season not in SEASONS:
        raise ValueError(f"{what}: {season!r} is not a season.")
    return season


#: What a covenant does to a member who broke its charter (Covenants pp.
#: 35-36): withhold privileges until he makes amends, lower his standing
#: (the Charter of Arae Flaviae's censure, p. 128), or expel him.
CENSURE_WITHHELD = "Privileges withheld"
CENSURE_LOWERED = "Standing lowered"
CENSURE_EXPELLED = "Expelled"
CENSURES: tuple[str, ...] = (CENSURE_WITHHELD, CENSURE_LOWERED, CENSURE_EXPELLED)

#: What a covenant may withhold (Covenants pp. 34-36). The laboratory and
#: food, drink and shelter are on shaky ground (PERSONAL_PRIVILEGES).
PRIVILEGES: tuple[str, ...] = (
    "Library",
    "Magical items",
    "Vis share",
    "Money",
    "Vote",
    "Laboratory",
    "Food, drink and shelter",
)
#: Privileges most Tribunals take for a magus's own: denying them may break
#: the Oath of Hermes (Covenants p. 36).
PERSONAL_PRIVILEGES: tuple[str, ...] = ("Laboratory", "Food, drink and shelter")


@dataclass
class Censure:
    """What the covenant did about a broken clause: whom it censured
    (a character id), how, which privileges it withholds, when, until
    when, a note, and the Tribunal case it was charged in ("" for none)."""

    character_id: str
    penalty: str = CENSURE_WITHHELD
    withheld: list[str] = field(default_factory=list)
    year: int | None = None
    season: str = ""
    until_year: int | None = None
    until_season: str = ""
    note: str = ""
    case_id: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Censure:
        d = dict(data)
        what = "A censure under a covenant's charter"
        if not d.get("character_id"):
            raise ValueError(f"{what} names no magus.")
        if d.get("penalty", CENSURE_WITHHELD) not in CENSURES:
            raise ValueError(f"{what}: {d.get('penalty')!r} is not a penalty.")
        withheld = d.get("withheld") or []
        if not isinstance(withheld, list) or any(w not in PRIVILEGES for w in withheld):
            raise ValueError(f"{what}: {withheld!r} are not privileges.")
        d["year"] = _optional_year(d.get("year"), what)
        d["until_year"] = _optional_year(d.get("until_year"), what)
        d["season"] = _season(d.get("season"), what)
        d["until_season"] = _season(d.get("until_season"), what)
        return cls(**known_fields(cls, d))


@dataclass
class CharterClause:
    """One clause of a covenant's charter, kept like a diary line: its
    number or title, its words, when it was agreed, the charter section it
    sits in ("" for none), and its status, with the season, year and a
    note for an amended or broken one."""

    number: str
    text: str = ""
    year: int | None = None
    season: str = ""
    section: str = ""
    status: str = CLAUSE_IN_FORCE
    since_year: int | None = None
    since_season: str = ""
    note: str = ""
    #: What the covenant did about it, once broken (None: nothing yet).
    censure: Censure | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CharterClause:
        d = dict(data)
        what = f"Charter clause {d.get('number')!r}"
        status = d.get("status") or CLAUSE_IN_FORCE
        if status not in CLAUSE_STATUSES:
            raise ValueError(f"{what}: {status!r} is not a clause's status.")
        d["status"] = status
        d["number"] = str(d.get("number") or "")
        d["year"] = _optional_year(d.get("year"), what)
        d["since_year"] = _optional_year(d.get("since_year"), what)
        d["season"] = _season(d.get("season"), what)
        d["since_season"] = _season(d.get("since_season"), what)
        if d.get("censure"):
            d["censure"] = Censure.from_dict(d["censure"])
        else:
            d["censure"] = None
        return cls(**known_fields(cls, d))


#: A sealed magus's standing under the charter (Covenants p. 33: full and
#: associate members, and a period of servitude; the Charter of Arae
#: Flaviae's probationary members and Protected Guests, pp. 126-128), or
#: Expelled, whose seal stays on the charter, struck.
STANDING_FULL = "Full member"
STANDING_ASSOCIATE = "Associate member"
STANDING_PROBATION = "Probationary member"
STANDING_GUEST = "Protected Guest"
STANDING_EXPELLED = "Expelled"
STANDINGS: tuple[str, ...] = (
    STANDING_FULL,
    STANDING_ASSOCIATE,
    STANDING_PROBATION,
    STANDING_GUEST,
    STANDING_EXPELLED,
)


@dataclass
class CharterSeal:
    """A magus's seal on the charter (Covenants p. 33: the members' seals
    or signatures affixed to it), when he sealed it, and his standing:
    a probationary member's probation ends in `until_*`; an expelled
    magus's seal stays, with when he was expelled in `until_*`. Older
    saves load as full members."""

    character_id: str
    year: int | None = None
    season: str = ""
    standing: str = STANDING_FULL
    until_year: int | None = None
    until_season: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CharterSeal:
        d = dict(data)
        what = "A seal on a covenant's charter"
        if not d.get("character_id"):
            raise ValueError(f"{what} names no magus.")
        d["standing"] = d.get("standing") or STANDING_FULL
        if d["standing"] not in STANDINGS:
            raise ValueError(f"{what}: {d['standing']!r} is not a standing.")
        d["year"] = _optional_year(d.get("year"), what)
        d["season"] = _season(d.get("season"), what)
        d["until_year"] = _optional_year(d.get("until_year"), what)
        d["until_season"] = _season(d.get("until_season"), what)
        return cls(**known_fields(cls, d))


@dataclass
class CovenantCharter:
    """The covenant's Charter of Covenant (Covenants pp. 32-36): its name,
    preamble (the oath, or what the charter is for), when it was sworn,
    its Official Seal (`ratified`: whether a Quaesitor notarized it, then
    who and when, p. 36), whether its Tribunal's reviewers passed it
    (Thebes's Conciliatory Board), its clauses and the members' seals.
    `template` is the template it was drawn from ("" for none);
    `probation_seasons` how long a probationary member serves (None: the
    charter sets no term). Not the Chartered Town Boon's town charter,
    which is Covenant.charter."""

    name: str = ""
    preamble: str = ""
    year: int | None = None
    season: str = ""
    ratified: bool = False
    notarized_by: str = ""
    notarized_year: int | None = None
    notarized_season: str = ""
    reviewed: bool = False
    template: str = ""
    probation_seasons: int | None = None
    clauses: list[CharterClause] = field(default_factory=list)
    seals: list[CharterSeal] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CovenantCharter:
        if not isinstance(data, dict):
            raise ValueError(
                f"A covenant's Charter of Covenant should be a mapping, not {data!r}."
            )
        d = dict(data)
        what = f"The charter {d.get('name')!r}"
        d["year"] = _optional_year(d.get("year"), what)
        d["season"] = _season(d.get("season"), what)
        d["ratified"] = bool(d.get("ratified"))
        d["reviewed"] = bool(d.get("reviewed"))
        d["notarized_year"] = _optional_year(d.get("notarized_year"), what)
        d["notarized_season"] = _season(d.get("notarized_season"), what)
        probation = d.get("probation_seasons")
        if probation is not None and (
            isinstance(probation, bool)
            or not isinstance(probation, int)
            or probation < 1
        ):
            raise ValueError(f"{what}: a probation of {probation!r} seasons.")
        d["clauses"] = [CharterClause.from_dict(c) for c in d.get("clauses") or []]
        d["seals"] = [CharterSeal.from_dict(s) for s in d.get("seals") or []]
        return cls(**known_fields(cls, d))


@dataclass
class CharterTemplate:
    """A charter to start a covenant's own from (charter_templates.py):
    the book's (the Charter of Arae Flaviae) or one the troupe saved. Its
    name, preamble and clauses' words may hold {covenant}, {tribunal} and
    {year}. `tribunal` is the Tribunal package it suits ("" for any);
    `ratified_unaltered`, whether Quaesitores ratify it at once while it is
    used as it stands (Covenants p. 33)."""

    id: str
    name: str
    tribunal: str = ""
    source: str = ""
    charter_name: str = ""
    preamble: str = ""
    probation_seasons: int | None = None
    ratified_unaltered: bool = False
    clauses: list[CharterClause] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CharterTemplate:
        d = dict(data)
        if not d.get("id") or not d.get("name"):
            raise ValueError(f"A charter template needs an id and a name: {data!r}.")
        d["ratified_unaltered"] = bool(d.get("ratified_unaltered"))
        d["clauses"] = [CharterClause.from_dict(c) for c in d.get("clauses") or []]
        return cls(**known_fields(cls, d))


@dataclass
class Covenant:
    id: str
    saga_id: str
    name: str
    notes: str = ""
    aura: int = 0  # inherited by all of the covenant's laboratories
    #: Which realm the aura belongs to (REALMS); older saves load as Magic.
    aura_realm: str = "Magic"
    #: The place it is in and which level (places.py). While it is
    #: placed, its aura comes from the place, and the aura typed on it is
    #: kept in own_aura and own_realm until it is moved out.
    place_id: str | None = None
    place_level: int = 0
    own_aura: int | None = None
    own_realm: str = ""
    #: Whether it is at a Place of its own, where its Boons and Hooks act on
    #: the aura: its home, or a Place travelling with it (places.sync).
    aura_boons_apply: bool = True
    #: The Tribunal it belongs to (Saga.tribunals), if any.
    tribunal_id: str | None = None
    #: The covenant it is vassal to (vassals.py), and the oath's duties.
    liege_id: str | None = None
    oath: str = ""
    year_founded: int | None = None
    aegis_of_the_hearth: int = 0
    aegis_penetration: int = 0
    #: Living Conditions typed for the magi and for everyone else; None
    #: follows the covenant's season (rules.living.season_living).
    living_conditions_magi: int | None = None
    living_conditions_mundane: int | None = None
    #: The covenant's life stage (ArM5 Chapter 6, "Covenant Seasons") -- one
    #: of SEASONS. Not the calendar season, which lives on the Saga.
    covenant_season: str = "Spring"
    #: The book's base covenant it was started from (covenant_templates
    #: BASE_BY_KEY: "weak", "medium", "powerful"), or "".
    base_covenant: str = ""
    #: Pounds its unspent Build Points became on moving to In Play
    #: (creation_covenant.convert_remaining), so they stay spent if it moves
    #: back to In Creation.
    converted_pounds: int = 0
    #: Boons and Hooks attached to this covenant, resolved against the
    #: covenant Boon/Hook catalog (vf_id holds the catalog id).
    #: An optional free-text descriptor lives in `params["detail"]` (which
    #: Edifice, which resource...), blank by default -- see BOON_HOOK_DETAIL.
    boons_hooks: list[VirtueFlawInstance] = field(default_factory=list)
    #: Covenant Reputations: a name and a score, with no cap (DE p. 28).
    reputations: list[ScoredTrait] = field(default_factory=list)
    #: The Inhabitants tab (see Inhabitant, Loyalty and Population).
    inhabitants: list[Inhabitant] = field(default_factory=list)
    loyalty: Loyalty = field(default_factory=Loyalty)
    population: Population = field(default_factory=Population)
    #: The Possessions tab (see Possession).
    possessions: list[Possession] = field(default_factory=list)
    #: The Economics tab (see Economics).
    economics: Economics = field(default_factory=Economics)
    #: The Diary tab (see CovenantDiaryEntry), in the order entered.
    diary: list[CovenantDiaryEntry] = field(default_factory=list)
    #: The Power Level chosen at creation: one of POWER_LEVELS,
    #: or "" before one is chosen.
    power_level: str = ""
    #: The Build Points the storyguide gives it, within the Power Level's
    #: range: what its starting resources are bought with (None: not set).
    build_points_budget: int | None = None
    #: Magi who go without a laboratory at creation, each refunding 50
    #: Build Points. Only this refunds: a magus whose lab
    #: isn't entered still has the free one.
    magi_without_lab: int = 0
    #: What its Build Points were spent on when it moved to In Play, by
    #: Build-tab row; None for a covenant still In Creation,
    #: or one in play since before this was recorded.
    initial_build_points: dict[str, int] | None = None
    #: Being created by the book: the creation checks run and
    #: the Creation Worksheet is offered. New records start In Creation;
    #: older saves load In Play (False).
    in_creation: bool = False
    #: The library's research bonus per subject (an Art or Ability name ->
    #: 1-5, book_value.RESEARCH_LEVELS), as the troupe judges its
    #: collection; a subject not listed has none.
    library_research: dict[str, int] = field(default_factory=dict)
    #: Subjects the library has a group of pictorial works on (Covenants,
    #: Other Opus Types): each raises research on it one level, for 10
    #: Build Points at creation.
    pictorial_works: list[str] = field(default_factory=list)
    #: How much of the covenant is written down (world.DETAIL_LEVELS).
    #: Older saves load as Full.
    detail: str = FULL
    #: A paragraph about the covenant in the saga.
    summary: str = ""
    #: A player covenant: one the troupe plays, which other records'
    #: attitudes point at. Sketch covenants are not; older saves are.
    played: bool = True
    #: Its attitude toward each player covenant (none for those it has no
    #: settled view of).
    attitudes: list[Attitude] = field(default_factory=list)
    favours: list[Favour] = field(default_factory=list)
    links: list[Link] = field(default_factory=list)
    #: Magi of a sketch covenant who are counted but never named: each has
    #: a Tribunal vote, as its named magi do.
    unnamed_magi: int = 0
    #: A sketch covenant's What Matters: one short entry a line (its vis,
    #: library, Boons and Hooks), each optionally "Label: what".
    what_matters: str = ""
    #: Its arms (arms.Arms.to_dict); empty for none.
    arms: dict[str, str] = field(default_factory=dict)
    #: Its own town charter, for the Chartered Town Boon: its lords and
    #: terms, kept as a town neighbour keeps them (town_charter.py); empty
    #: for none.
    charter: dict[str, Any] = field(default_factory=dict)
    #: Its manors, kennels, mews and stables, and which sources of income
    #: they describe, kept as a lord neighbour keeps them (manors.py);
    #: empty for none.
    manors: dict[str, Any] = field(default_factory=dict)
    #: The interests turned off (deeds.COVENANT_INTERESTS); none by default.
    interests_off: list[str] = field(default_factory=list)
    #: Its Charter of Covenant: the magi's oath, clauses and seals
    #: (covenant_charter.py); empty for none. Older saves load without one.
    charter_of_covenant: CovenantCharter = field(default_factory=CovenantCharter)
    #: What only the storyguide should read: the record's Secrets
    #: chapter, hidden from players signed in to a hosted copy.
    secrets: str = ""
    # Hermetic Projects (Hermetic Projects pp. 36-41): the great works it
    # has begun, and the one its Projects tab shows ("" for the first).
    hermetic_projects: list[HermeticProject] = field(default_factory=list)
    project_shown: str = ""
    # Shaping the land (Transforming Mythic Europe pp. 54-77): the islands
    # it is raising by magic. Older saves load with none.
    land_projects: list[LandProject] = field(default_factory=list)
    #: Its History tab's own settings (covenant_history.py): the eras it
    #: is told in, and the entries left out of it. Older saves load with
    #: none.
    history: dict[str, Any] = field(default_factory=dict)
    #: Where it has been, by date: the latest stop not after the saga's
    #: date is where it is now (rules.mobile). `place_id` stays its own
    #: Place, a fixed home or a Place that travels with it. Older saves
    #: load with none, and stay where they are.
    stops: list[CovenantStop] = field(default_factory=list)
    #: Where it means to go: `route_at` is the leg it goes to next, and a
    #: `circuit` goes back to the first after the last.
    route: list[RouteStop] = field(default_factory=list)
    route_at: int = 0
    circuit: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Covenant:
        # Older saves kept secrets under a heading in the notes or summary.
        d = move_secrets(dict(data), "notes", "summary")
        # Living Conditions used to start at 0 and stay there unless typed;
        # a 0 now follows the covenant's season, as the book's table does.
        for key in ("living_conditions_magi", "living_conditions_mundane"):
            if d.get(key) == 0:
                d[key] = None
        d["economics"] = Economics.from_dict(d.get("economics") or {})
        d["boons_hooks"] = [
            VirtueFlawInstance(**known_fields(VirtueFlawInstance, bh))
            for bh in d.get("boons_hooks", [])
        ]
        # Diary Story Events link to a Boon/Hook by its instance id.
        # The same ids every load, like a laboratory's Virtues.
        for i, bh in enumerate(d["boons_hooks"]):
            bh.id = bh.id or f"{d.get('id', '')}-bh{i}"
        d["diary"] = [
            CovenantDiaryEntry(**known_fields(CovenantDiaryEntry, e))
            for e in d.get("diary", [])
        ]
        d["reputations"] = [
            ScoredTrait(**known_fields(ScoredTrait, r))
            for r in d.get("reputations", [])
        ]
        read_standing(d)
        d["links"] = [Link(**known_fields(Link, x)) for x in d.get("links", [])]
        charter = d.get("charter") or {}
        if not isinstance(charter, dict):
            raise ValueError(
                f"A covenant's charter should be a mapping, not {charter!r}."
            )
        d["charter"] = dict(charter)
        d["charter_of_covenant"] = CovenantCharter.from_dict(
            d.get("charter_of_covenant") or {}
        )
        held = d.get("manors") or {}
        if not isinstance(held, dict):
            raise ValueError(f"A covenant's manors should be a mapping, not {held!r}.")
        d["manors"] = dict(held)
        off = d.get("interests_off") or []
        if not isinstance(off, list) or not all(isinstance(x, str) for x in off):
            raise ValueError(
                f"{d.get('name') or 'A covenant'}: interests_off must be a list "
                "of interest names."
            )
        d["interests_off"] = off
        d["inhabitants"] = [_inhabitant_from_dict(i) for i in d.get("inhabitants", [])]
        d["loyalty"] = Loyalty(**known_fields(Loyalty, d.get("loyalty") or {}))
        d["population"] = Population(
            **known_fields(Population, d.get("population") or {})
        )
        d["possessions"] = [
            Possession(**known_fields(Possession, p)) for p in d.get("possessions", [])
        ]
        # Older saves kept a bare Art -> pawns `vis_stock`; those are now Raw Vis
        # stores on the Possessions tab (and the key is no longer saved).
        stock = d.pop("vis_stock", None) or {}
        if stock:
            for art, pawns in stock.items():
                art_name = ART_BY_NAME.get(str(art).lower(), str(art))
                d["possessions"].append(
                    Possession(
                        id=f"vis_store_{art_name.lower()}",
                        kind="vis_store",
                        name=f"{art_name} Vis",
                        art=art_name,
                        pawns=int(pawns),
                    )
                )
        # Hermetic Projects.
        d["hermetic_projects"] = projects_from(
            d.get("hermetic_projects"), str(d.get("name") or d.get("id") or "")
        )
        d["project_shown"] = str(d.get("project_shown") or "")
        # Shaping the land.
        land = d.get("land_projects") or []
        if not isinstance(land, list):
            raise ValueError(
                f"{d.get('name')!r}'s land projects should be a list, not {land!r}."
            )
        d["land_projects"] = [LandProject.from_dict(p) for p in land]
        d["history"] = history_from(d.get("history"), str(d.get("name") or ""))
        owner = str(d.get("name") or d.get("id") or "a covenant")
        d["stops"] = stops_from(d.get("stops"), owner)
        d["route"] = route_from(d.get("route"), owner)
        return cls(**known_fields(cls, d))  # drops the retired `library_id`


#: The `VirtueFlawInstance.params` key holding a covenant Boon/Hook's
#: optional descriptor.
BOON_HOOK_DETAIL = "detail"

#: The `params` key holding the user's own multi-line description of an
#: attached Boon/Hook (what the Hidden Resources actually contain...), shown
#: in the details panel ahead of the official rules text.
BOON_HOOK_DESCRIPTION = "description"

#: The `params` key marking an attached Minor Hook as Unknown ("yes"): one
#: player storyguides it without the others knowing, and it counts as a
#: Major Hook for balancing (Covenants). Only honoured for catalog entries
#: marked `unknown` -- see covenants.boon_hook_is_unknown().
BOON_HOOK_UNKNOWN = "unknown"

#: The `params` key holding the id of the vis or income source a Contested,
#: Indiscreet or Dwindling Resource Hook is about (see
#: covenants.RESOURCE_HOOKS).
BOON_HOOK_RESOURCE = "resource"

#: The `params` key holding the id of the Covenant Situation a Boon/Hook
#: came with (covenants.situation_instances), so choosing another
#: Situation can replace it.
BOON_HOOK_SITUATION = "situation"
