"""Raw vis across the saga: who holds what, moving it between
them, and where a covenant's vis store is kept.

A character and a laboratory each hold one pool of raw vis, pawns by Art
(`raw_vis`, which the season engine pays from and adds to). A covenant
holds named Raw Vis Stores on its Possessions tab (Possession, kind
"vis_store"), each of one Art. A move takes pawns of one Art from a pool or
a store and adds them to another holder: to a character's or laboratory's
pool, or to a covenant's first store of that Art (a new one if it has
none). Both sides get a Diary entry.

A covenant's vis store is kept somewhere: in the covenant itself, in one of
its laboratories, or with one of its characters -- a link
(`Possession.location_kind` / `location_id`), not free text. Older saves'
text is matched to a laboratory or character by name when they load
(models._link_vis_store_locations); unmatched text falls back to the
covenant and stays as the store's note on where exactly.

A store or source may hold a special kind of vis (`Possession.vis_kind`,
rules.vis_kinds): vis moved, harvested or added joins only a store of the
same kind (and Infernal mark), and season work pays from a covenant's
ordinary stores before its special ones, never from abstract faerie vis,
which holds no real vis (RoP: Faerie p. 19).
"""

from __future__ import annotations

from collections.abc import Iterator, MutableMapping
from dataclasses import dataclass

from .arts import ARTS
from .models import (
    Character,
    Covenant,
    CovenantDiaryEntry,
    DiaryEntry,
    Laboratory,
    Possession,
    Saga,
    SeasonPlan,
    new_instance_id,
)
from .rules import vis_kinds

Holder = Character | Laboratory | Covenant

COVENANT, LABORATORY, CHARACTER = "covenant", "laboratory", "character"
STORE = "vis_store"


def kind_of(holder: Holder) -> str:
    if isinstance(holder, Character):
        return CHARACTER
    if isinstance(holder, Laboratory):
        return LABORATORY
    return COVENANT


def find_holder(saga: Saga, kind: str, holder_id: str | None) -> Holder | None:
    if kind == CHARACTER:
        return saga.character(holder_id)
    if kind == LABORATORY:
        return saga.laboratory(holder_id)
    if kind == COVENANT:
        return saga.covenant(holder_id)
    return None


def _title(art: str) -> str:
    """The Art as the lists print it ("vim" -> "Vim")."""
    return next((a for a in ARTS if a.lower() == art.lower()), art.title())


def special_stores(
    saga: Saga, character: Character, arts: tuple[str, ...]
) -> list[Possession]:
    """The Raw Vis Stores of `character`'s covenant of any of `arts` that
    hold a special kind of vis (rules.vis_kinds), with pawns in them."""
    covenant = saga.covenant(character.covenant_id)
    if covenant is None:
        return []
    wanted = {a.lower() for a in arts}
    return [
        p
        for p in covenant.possessions
        if p.kind == STORE and p.vis_kind and p.art.lower() in wanted and p.pawns > 0
    ]


def casting_notes(
    saga: Saga, magus: Character, technique: str, form: str, cost: int = 0
) -> list[str]:
    """What the covenant's special stores of a spell's Arts change in
    casting it, a Ritual needing `cost` pawns (rules.vis_kinds)."""
    stores = special_stores(saga, magus, (technique, form))
    return vis_kinds.casting_notes(stores, technique, form, cost)


def kept_together(covenant: Covenant, store: Possession) -> int:
    """Pawns of the store's Art the covenant keeps in the same place as it
    (the same keeper and the same note on where exactly)."""
    where = (store.location_kind, store.location_id, store.location.strip().lower())
    return sum(
        p.pawns
        for p in covenant.possessions
        if p.kind == STORE
        and p.art.lower() == store.art.lower()
        and (p.location_kind, p.location_id, p.location.strip().lower()) == where
    )


def infernal_stores(
    saga: Saga, character: Character, arts: tuple[str, ...]
) -> list[Possession]:
    """The Raw Vis Stores of `character`'s covenant of any of `arts` that
    are marked Infernal vis (RoP: The Infernal pp. 18-19)."""
    covenant = saga.covenant(character.covenant_id)
    if covenant is None:
        return []
    wanted = {a.lower() for a in arts}
    return [
        p
        for p in covenant.possessions
        if p.kind == STORE and p.infernal and p.art.lower() in wanted and p.pawns > 0
    ]


# ------------------------------------------------------------- what's held


@dataclass(frozen=True)
class Held:
    """Pawns of one Art a holder has: a pool's entry, or a covenant's store."""

    art: str  # as ARTS spells it
    pawns: int
    #: The covenant's store (None for a character's or laboratory's pool).
    store: Possession | None = None

    @property
    def label(self) -> str:
        """ "Vim: 3 pawn(s)", with the store's name (and its kind of vis)
        for a covenant's."""
        text = f"{self.art}: {self.pawns} pawn(s)"
        if self.store is None:
            return text
        kind = vis_kinds.label(self.store)
        return f"{self.store.name} ({text}{', ' + kind if kind else ''})"


def held(holder: Holder) -> list[Held]:
    """Everything the holder has that could be moved, in list order."""
    if isinstance(holder, Covenant):
        # Every store, so the indexes are the Raw Vis Stores list's rows'.
        return [
            Held(_title(p.art), p.pawns, p)
            for p in holder.possessions
            if p.kind == STORE
        ]
    # Every entry, so the indexes are the sheet's rows' (sorted(raw_vis)).
    return [Held(_title(art), pawns) for art, pawns in sorted(holder.raw_vis.items())]


# ------------------------------------------------------------------ moving


def _credit(
    holder: Holder, art: str, pawns: int, like: Possession | None = None
) -> None:
    """Add `pawns` of `art` to the holder: to a covenant's first store of
    that Art of the same kind of vis as `like` (ordinary when None), or a
    new one."""
    if isinstance(holder, Covenant):
        plain = Possession(id="", kind=STORE)
        model = like if like is not None else plain
        store = next(
            (s for s in _stores(holder, art) if vis_kinds.same_kind(s, model)), None
        )
        if store is None:
            special = like is not None and bool(like.vis_kind)
            name = like.name if special and like is not None else f"{_title(art)} vis"
            store = vis_kinds.copy_kind(
                model,
                Possession(
                    id=f"vis_{new_instance_id()}",
                    kind=STORE,
                    name=name,
                    art=_title(art),
                    pawns=0,
                    location_kind=COVENANT,
                    location_id=holder.id,
                    physical_form=like.physical_form if special and like else "",
                ),
            )
            holder.possessions.append(store)
        store.pawns += pawns
        return
    key = art.lower()
    holder.raw_vis[key] = holder.raw_vis.get(key, 0) + pawns


def _stores(covenant: Covenant, art: str) -> list[Possession]:
    return [
        p
        for p in covenant.possessions
        if p.kind == STORE and p.art.lower() == art.lower()
    ]


def _spendable(covenant: Covenant, art: str) -> list[Possession]:
    """The stores of `art` season work may pay from: ordinary vis first,
    then the special kinds, never vis that holds none (abstract)."""
    stores = [s for s in _stores(covenant, art) if vis_kinds.kind_of(s).usable]
    return sorted(stores, key=lambda s: vis_kinds.kind_of(s).special)


class StorePool(MutableMapping[str, int]):
    """A covenant's Raw Vis Stores seen as a pool, pawns by Art (lower-case
    keys) -- what a character's or laboratory's `raw_vis` is -- so season
    work can pay from them. Lowering an Art takes pawns from its
    stores in order, removing the emptied; raising it adds to the first (a
    new one if there is none). Every change is entered in the covenant's
    Diary as `who`'s. Only vis a magus can spend counts: ordinary stores
    pay first, then the special kinds; abstract faerie vis never."""

    def __init__(self, saga: Saga, covenant: Covenant, who: str) -> None:
        self.saga, self.covenant, self.who = saga, covenant, who

    def __getitem__(self, art: str) -> int:
        # 0 for an Art with no store, as the season engine reads a pool
        # back after emptying it.
        return sum(p.pawns for p in _spendable(self.covenant, art))

    def __setitem__(self, art: str, pawns: int) -> None:
        change = pawns - self[art]
        if change > 0:
            _credit(self.covenant, art, change)
        elif change < 0:
            left = -change
            for store in _spendable(self.covenant, art):
                taken = min(left, store.pawns)
                store.pawns -= taken
                left -= taken
                if store.pawns <= 0:
                    self.covenant.possessions.remove(store)
                if not left:
                    break
        if change:
            verb = "added" if change > 0 else "used"
            count = abs(change)
            _record(
                self.saga,
                self.covenant,
                f"{self.who} {verb} {count} pawn{'s' if count != 1 else ''} of "
                f"{_title(art)} vis",
                art,
                change,
            )

    def __delitem__(self, art: str) -> None:
        self[art] = 0

    def __iter__(self) -> Iterator[str]:
        seen: list[str] = []
        for p in self.covenant.possessions:
            if (
                p.kind == STORE
                and vis_kinds.kind_of(p).usable
                and p.art.lower() not in seen
            ):
                seen.append(p.art.lower())
        return iter(seen)

    def __len__(self) -> int:
        return sum(1 for _ in self)


def covenant_pool(
    saga: Saga, covenant_id: str | None, who: str
) -> MutableMapping[str, int]:
    """The vis stores of the covenant `covenant_id` as a pool (nothing, with
    no such covenant)."""
    covenant = saga.covenant(covenant_id)
    return StorePool(saga, covenant, who) if covenant is not None else {}


def season_pool(
    saga: Saga, character: Character, plan: SeasonPlan
) -> MutableMapping[str, int]:
    """The raw vis a season plan (not a laboratory plan) draws on, by its
    `vis_from`: the character's own, their laboratory's, or their
    covenant's vis stores."""
    if plan.vis_from == LABORATORY:
        lab = saga.laboratory(character.assigned_lab_id)
        return lab.raw_vis if lab is not None else {}
    if plan.vis_from == COVENANT:
        return covenant_pool(saga, character.covenant_id, character.name)
    return character.raw_vis


def payer(character: Character, plan: SeasonPlan) -> str:
    """Whose raw vis a plan's `vis_from` names, for a message."""
    if plan.vis_from == COVENANT:
        return "the covenant's"
    if plan.vis_from == LABORATORY:
        return "the laboratory's"
    return f"{character.name}'s"


def pay(pool: MutableMapping[str, int], cost: dict[str, int]) -> None:
    """Take `cost` (Art -> pawns) out of `pool`, dropping emptied Arts."""
    for art, pawns in cost.items():
        key = art.lower()
        pool[key] = max(0, pool.get(key, 0) - pawns)
        if not pool[key]:
            del pool[key]


def _debit(holder: Holder, what: Held, pawns: int) -> None:
    if what.store is not None:
        assert isinstance(holder, Covenant)
        what.store.pawns -= pawns
        if what.store.pawns <= 0:
            # An emptied store is gone, like a pool's emptied Art.
            holder.possessions.remove(what.store)
        return
    assert not isinstance(holder, Covenant)
    key = what.art.lower()
    left = holder.raw_vis.get(key, 0) - pawns
    if left > 0:
        holder.raw_vis[key] = left
    else:
        holder.raw_vis.pop(key, None)


def _record(saga: Saga, holder: Holder, text: str, art: str, pawns: int) -> None:
    """The move's Diary entry on one side (`pawns` signed: + gained)."""
    if isinstance(holder, Covenant):
        holder.diary.append(
            CovenantDiaryEntry(
                year=saga.current_year,
                season=saga.current_season,
                name=text,
                category="Vis",
                vis_pawns=pawns,
                vis_art=_title(art),
            )
        )
    else:
        holder.diary.append(
            DiaryEntry(year=saga.current_year, season=saga.current_season, name=text)
        )


def move(
    saga: Saga, source: Holder, what: Held, pawns: int, destination: Holder
) -> None:
    """Take `pawns` of `what` from `source` and give them to `destination`,
    writing a Diary entry on both sides."""
    _debit(source, what, pawns)
    _credit(destination, what.art, pawns, what.store)
    amount = f"{pawns} pawn{'s' if pawns != 1 else ''} of {what.art} vis"
    kind = vis_kinds.label(what.store) if what.store is not None else ""
    if kind:
        amount += f" ({kind})"
    _record(saga, source, f"Moved {amount} to {destination.name}", what.art, -pawns)
    _record(saga, destination, f"Received {amount} from {source.name}", what.art, pawns)


# ----------------------------------------------- where a store is kept


def location_options(saga: Saga, covenant: Covenant) -> list[tuple[str, str]]:
    """Where a covenant's vis store can be kept, as (label, "kind:id"): the
    covenant itself, its laboratories, its characters."""
    options = [(f"{covenant.name} (the covenant)", f"{COVENANT}:{covenant.id}")]
    options += [
        (f"Laboratory: {lab.name}", f"{LABORATORY}:{lab.id}")
        for lab in saga.laboratories
        if lab.covenant_id == covenant.id
    ]
    options += [
        (f"With {c.name}", f"{CHARACTER}:{c.id}")
        for c in saga.characters
        if c.covenant_id == covenant.id
    ]
    return options


def location_value(covenant: Covenant, store: Possession | None) -> str:
    """The store's location as a form value; a new store's is its covenant."""
    if store is None or not store.location_kind or not store.location_id:
        return f"{COVENANT}:{covenant.id}"
    return f"{store.location_kind}:{store.location_id}"


def location_label(saga: Saga, covenant: Covenant, store: Possession) -> str:
    """Where the store is kept, by name (the covenant if the link is gone)."""
    place = find_holder(saga, store.location_kind, store.location_id)
    if place is None or place is covenant:
        return covenant.name
    if isinstance(place, Laboratory):
        return f"Laboratory: {place.name}"
    return f"With {place.name}"
