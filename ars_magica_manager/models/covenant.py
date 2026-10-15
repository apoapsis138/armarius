"""The Covenant and its diary."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..arts import ART_BY_NAME
from .character import ScoredTrait
from .common import known_fields
from .holdings import Economics, Inhabitant, Loyalty, Population, Possession
from .traits import VirtueFlawInstance
from .world import FULL, Attitude, Favour, Link

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
)
#: The category whose entries have a Status, a linked Boon/Hook and a
#: Revisit year.
STORY_EVENT = "Story Event"
#: A Story Event's Status.
STORY_EVENT_STATUSES: tuple[str, ...] = ("Open", "Resolved")


@dataclass
class CovenantDiaryEntry:
    """One entry on the covenant's Diary tab: what happened and
    when, with optional amounts. Only `loyalty` changes the sheet (it adds
    into the Loyalty block's Actions and Events); pounds and vis are a
    record. `status`, `boon_hook_id` (a VirtueFlawInstance.id among the
    covenant's Boons/Hooks) and `revisit_year` are for Story Events;
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
    #: The Tribunal it belongs to (Saga.tribunals), if any.
    tribunal_id: str | None = None
    year_founded: int | None = None
    aegis_of_the_hearth: int = 0
    aegis_penetration: int = 0
    living_conditions_magi: int = 0
    living_conditions_mundane: int = 0
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
    #: Covenant Reputations: a name and a score from -3 to +3 (the range is
    #: enforced by the edit dialog, not here).
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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Covenant:
        d = dict(data)
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
        d["attitudes"] = [Attitude.from_dict(a) for a in d.get("attitudes", [])]
        d["favours"] = [Favour(**known_fields(Favour, f)) for f in d.get("favours", [])]
        d["links"] = [Link(**known_fields(Link, x)) for x in d.get("links", [])]
        d["inhabitants"] = [
            Inhabitant(**known_fields(Inhabitant, i)) for i in d.get("inhabitants", [])
        ]
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
