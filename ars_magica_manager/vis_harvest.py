"""Gathering a vis source's yield: the season's own harvest, and Harvest
Vis by Hand, a saga setting under which someone has to go and gather it.

Whether a source could be harvested by hand now is one rule, a
Specification: each of its checks is a test of the saga and the source,
with the reason it gives when the test fails. The Harvest action, its
greyed button's tooltip and the season's play all ask it, so they can't
disagree.
"""

from __future__ import annotations

from collections.abc import Callable

from .covenants import contested_now
from .models import Covenant, CovenantDiaryEntry, Possession, Saga, new_instance_id
from .rules import vis_kinds

SOURCE = (
    "A vis source gives a set number of pawns every year, to be gathered, "
    "sometimes only by one who can detect vis or by a spell (Definitive "
    "Edition p. 422); harvesting vis sources is a covenant's most basic "
    "obligation on its members, which may be handed to the covenfolk "
    "(Covenants p. 35), and council meetings assign who collects from each "
    "(Covenants p. 31); each source has a time of harvest (Covenants p. 137, "
    "the Vis Record Sheet), and collecting after the first time needs no "
    "story (Covenants p. 72), so it costs no season; a contested resource "
    "gives nothing until a story secures it (Definitive Edition p. 181). No "
    "book says what becomes of vis left ungathered: here it is lost for the "
    "year, as many sources exist only at a moment (Definitive Edition p. 422)."
)

#: Who harvested, when nobody named went: the covenant's servants.
COVENFOLK = "The covenfolk"

#: The Diary entry a harvest writes starts with this, by hand or not.
HARVESTED = "Vis harvested: "

#: A check of the rule: whether it holds, and why not when it doesn't.
Check = tuple[Callable[[Saga, Possession], bool], Callable[[Saga, Possession], str]]

#: Whether the source is one to gather by hand this season, once a year.
DUE: tuple[Check, ...] = (
    (
        lambda saga, _source: saga.harvest_vis_by_hand,
        lambda _saga, _source: (
            "Harvest Vis by Hand is off: the season's play gathers it."
        ),
    ),
    (
        lambda _saga, source: bool(source.art) and source.pawns > 0,
        lambda _saga, _source: "It has no Art or pawns to harvest.",
    ),
    (
        lambda saga, source: source.season == saga.current_season,
        lambda saga, source: (
            f"It is harvested in {source.season or 'no season'}; it is "
            f"{saga.current_season} now."
        ),
    ),
    (
        lambda saga, source: source.harvested_year != saga.current_year,
        lambda saga, _source: f"Already harvested in {saga.current_year}.",
    ),
)

#: A contested source gives nothing until it is settled (DE p. 181).
SETTLED: Check = (
    lambda saga, source: not contested_now(source, saga.current_year),
    lambda _saga, _source: "Contested and unsettled: Settle it first.",
)

#: "Could be harvested now", in the order its reasons are given.
HARVESTABLE_NOW: tuple[Check, ...] = (*DUE, SETTLED)


def refusal(saga: Saga, source: Possession, *, settling: bool = False) -> str:
    """Why `source` can't be harvested by hand now ("" when it can): the
    reason of the first check of HARVESTABLE_NOW it fails. `settling`: it
    is being secured this season (Advance Season's Contested Resources),
    so being contested doesn't count."""
    for holds, reason in DUE if settling else HARVESTABLE_NOW:
        if not holds(saga, source):
            return reason(saga, source)
    return ""


def harvestable(saga: Saga, source: Possession, *, settling: bool = False) -> bool:
    """Whether `source` could be harvested by hand now."""
    return refusal(saga, source, settling=settling) == ""


def add_vis(covenant: Covenant, source: Possession, pawns: int) -> None:
    """`pawns` of the source's vis into the covenant's first store of its
    Art and kind of vis (and Infernal mark), or a new one."""
    if pawns <= 0:
        return
    art = source.art
    store = next(
        (
            p
            for p in covenant.possessions
            if p.kind == "vis_store"
            and p.art.lower() == art.lower()
            and vis_kinds.same_kind(p, source)
        ),
        None,
    )
    if store is not None:
        store.pawns += pawns
        return
    special = bool(source.vis_kind)
    store = Possession(
        id=f"vis_{new_instance_id()}",
        kind="vis_store",
        name=(source.name or f"{art} vis") if special else f"{art} vis",
        art=art,
        pawns=pawns,
        location_kind="covenant",
        location_id=covenant.id,
        physical_form=source.physical_form if special else "",
    )
    covenant.possessions.append(vis_kinds.copy_kind(source, store))


def harvest(
    saga: Saga,
    covenant: Covenant,
    source: Possession,
    pawns: int,
    harvester: str = COVENFOLK,
    note: str = "",
) -> CovenantDiaryEntry:
    """Gather `pawns` of the source's vis this season: into the stores,
    the source marked harvested this year, and one entry in the covenant
    Diary naming `harvester` (a name, or COVENFOLK). It costs nobody a
    season (Covenants p. 72)."""
    add_vis(covenant, source, pawns)
    source.harvested_year = saga.current_year
    told = (
        f"{harvester} gathered {pawns} pawn(s) of {source.art} vis into the vis stores."
    )
    entry = CovenantDiaryEntry(
        saga.current_year,
        saga.current_season,
        f"{HARVESTED}{source.name or source.art}",
        " ".join(part for part in (told, note.strip()) if part),
        category="Covenant Season",
        vis_pawns=pawns,
        vis_art=source.art,
    )
    covenant.diary.append(entry)
    return entry


def harvested_this_season(saga: Saga, covenant: Covenant) -> list[CovenantDiaryEntry]:
    """The covenant's harvests written this season, in the Diary's order."""
    return [
        e
        for e in covenant.diary
        if e.year == saga.current_year
        and e.season == saga.current_season
        and e.name.startswith(HARVESTED)
        and e.vis_art
    ]
