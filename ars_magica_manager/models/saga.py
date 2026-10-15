"""The Saga, its players, and the helpers that work across records."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .books import Book, Codex
from .character import Character, LabTextAccess
from .common import known_fields
from .covenant import (
    BOON_HOOK_DESCRIPTION,
    BOON_HOOK_DETAIL,
    BOON_HOOK_UNKNOWN,
    Covenant,
)
from .definitions import CovenantBoonHookDef, LabVirtueFlawDef, VirtueFlawDef
from .devices import EnchantedDevice
from .familiar import Familiar
from .laboratory import Laboratory
from .seasons import LabProject, SeasonPlan, SeasonRecord
from .traits import Spell
from .tribunal import Tribunal


@dataclass
class Player:
    """Someone who can sign in to the saga from a browser: a
    name, a role (players.PLAYER or players.STORYGUIDE) and the passcode,
    kept only as a salted hash (players.hash_passcode)."""

    id: str
    name: str
    role: str = "player"
    passcode_hash: str = ""
    #: Whether this player may also change the covenants; a
    #: storyguide always may.
    covenant_rights: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Player:
        return cls(**known_fields(cls, data))


@dataclass
class SagaSource:
    """A source of the saga's own, cited by its user-made entries like a
    book (a house-rules list, a fan supplement): put in or out of play like
    one. Its abbreviation is what entries cite; see sourcebooks."""

    abbreviation: str
    title: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SagaSource:
        return cls(**known_fields(cls, data))


@dataclass
class Saga:
    id: str
    name: str
    storyguide: str = ""
    description: str = ""
    current_year: int = 1220
    current_season: str = "Spring"
    covenants: list[Covenant] = field(default_factory=list)
    #: The Tribunals of the saga's region; each covenant names its own.
    tribunals: list[Tribunal] = field(default_factory=list)
    characters: list[Character] = field(default_factory=list)
    laboratories: list[Laboratory] = field(default_factory=list)
    books: list[Book] = field(default_factory=list)
    #: The codices binding several books together (see Codex).
    codices: list[Codex] = field(default_factory=list)
    spells: list[Spell] = field(default_factory=list)
    familiars: list[Familiar] = field(default_factory=list)
    #: Every enchanted item in the saga, each shown on its holder's sheet.
    enchanted_devices: list[EnchantedDevice] = field(default_factory=list)
    #: The supplements and saga sources in play (sourcebooks.SUPPLEMENTS
    #: and `sources` abbreviations); None, the default and what older saves
    #: load as, means every book. The core book is always in play. See
    #: sourcebooks.
    books_in_play: list[str] | None = None
    #: The saga's own sources, which its user-made entries can cite.
    sources: list[SagaSource] = field(default_factory=list)
    #: Shared catalogs the saga doesn't offer at all (saga_catalogs keys):
    #: pickers list only the saga's own entries for them.
    hidden_catalogs: list[str] = field(default_factory=list)
    #: Single shared catalog entries the saga doesn't offer, by catalog
    #: (saga_catalogs keys) -- entry ids.
    hidden_entries: dict[str, list[str]] = field(default_factory=dict)
    #: The optional rules the troupe has turned on (rules.options keys);
    #: an option not listed is off, its default.
    rule_options: dict[str, bool] = field(default_factory=dict)
    #: Season plans not yet applied; a plan is removed when its
    #: season is applied.
    season_plans: list[SeasonPlan] = field(default_factory=list)
    #: Whether a record of each applied season is kept.
    keep_season_records: bool = True
    #: Those records, oldest first.
    season_records: list[SeasonRecord] = field(default_factory=list)
    #: Lab work in progress over several seasons.
    lab_projects: list[LabProject] = field(default_factory=list)
    #: User-made catalog entries: house rules and entries from
    #: books the shared catalogs don't carry -- character Virtues & Flaws,
    #: laboratory Virtues & Flaws, covenant Boons & Hooks. Text only: no
    #: effects the rules engine applies. See house_rules.py.
    custom_virtues_flaws: list[VirtueFlawDef] = field(default_factory=list)
    custom_lab_virtues_flaws: list[LabVirtueFlawDef] = field(default_factory=list)
    custom_boons_hooks: list[CovenantBoonHookDef] = field(default_factory=list)
    #: Who can sign in to the saga from a browser when it is hosted;
    #: the storyguide's own window needs no sign-in.
    players: list[Player] = field(default_factory=list)
    #: The app version that last saved this saga (storage.save_saga sets it;
    #: "" for a save older than versioning), for upgrading old saves later.
    app_version: str = ""
    #: Who last saved the saga (storage.save_saga sets it, from
    #: storage.saved_by): a signed-in player's name, else "" for the
    #: storyguide. Shown when another copy picks up the change.
    saved_by: str = ""

    def covenant(self, covenant_id: str | None) -> Covenant | None:
        """The covenant with this id, if there is one."""
        return next((c for c in self.covenants if c.id == covenant_id), None)

    def tribunal(self, tribunal_id: str | None) -> Tribunal | None:
        """The Tribunal with this id, if there is one."""
        return next((t for t in self.tribunals if t.id == tribunal_id), None)

    def character(self, character_id: str | None) -> Character | None:
        """The character with this id, if there is one."""
        return next((c for c in self.characters if c.id == character_id), None)

    def laboratory(self, laboratory_id: str | None) -> Laboratory | None:
        """The laboratory with this id, if there is one."""
        return next((lab for lab in self.laboratories if lab.id == laboratory_id), None)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Saga:
        d = dict(data)
        d["tribunals"] = [Tribunal.from_dict(t) for t in d.get("tribunals", [])]
        raw_covenants = [dict(c) for c in d.get("covenants", [])]
        _tribunals_from_names(raw_covenants, d["tribunals"])
        d["covenants"] = [Covenant.from_dict(c) for c in raw_covenants]
        d["characters"] = [Character.from_dict(c) for c in d.get("characters", [])]
        d["laboratories"] = [
            Laboratory.from_dict(lab) for lab in d.get("laboratories", [])
        ]
        d["familiars"] = [Familiar.from_dict(f) for f in d.get("familiars", [])]
        d["enchanted_devices"] = [
            EnchantedDevice.from_dict(e) for e in d.get("enchanted_devices", [])
        ]
        d["spells"] = [Spell.from_dict(s) for s in d.get("spells", [])]
        d["season_plans"] = [SeasonPlan.from_dict(p) for p in d.get("season_plans", [])]
        d["season_records"] = [
            SeasonRecord.from_dict(r) for r in d.get("season_records", [])
        ]
        d["lab_projects"] = [LabProject.from_dict(p) for p in d.get("lab_projects", [])]
        d["custom_virtues_flaws"] = [
            VirtueFlawDef.from_dict(e) for e in d.get("custom_virtues_flaws", [])
        ]
        d["custom_lab_virtues_flaws"] = [
            LabVirtueFlawDef.from_dict(e) for e in d.get("custom_lab_virtues_flaws", [])
        ]
        d["custom_boons_hooks"] = [
            CovenantBoonHookDef.from_dict(e) for e in d.get("custom_boons_hooks", [])
        ]
        d["players"] = [Player.from_dict(p) for p in d.get("players", [])]
        d["sources"] = [SagaSource.from_dict(s) for s in d.get("sources", [])]
        spell_names = {s.id: s.name for s in d["spells"]}
        d["books"] = [Book.from_dict(b, spell_names) for b in d.get("books", [])]
        d["codices"] = [Codex.from_dict(c) for c in d.get("codices", [])]
        # Older saves kept a Library record per covenant listing its book ids;
        # ownership now lives on the book itself.
        for library in d.pop("libraries", None) or []:
            ids = set(library.get("books") or [])
            for book in d["books"]:
                if book.id in ids and book.owner_kind is None:
                    book.owner_kind = "covenant"
                    book.owner_id = library.get("covenant_id")
        saga = cls(**known_fields(cls, d))
        _link_vis_store_locations(saga)
        _key_lab_text_access_by_author(saga)
        return saga


def _tribunals_from_names(
    covenants: list[dict[str, Any]], tribunals: list[Tribunal]
) -> None:
    """Older saves typed a covenant's Tribunal as text: each distinct name
    becomes a Tribunal record (the core rules, nothing else filled in) and
    the covenant points at it. Covenants that typed the same name, in any
    case, share one; a name matching a Tribunal already there joins it."""
    by_name = {t.name.strip().casefold(): t for t in tribunals}
    for covenant in covenants:
        name = (covenant.pop("tribunal", None) or "").strip()
        if not name or covenant.get("tribunal_id"):
            continue
        tribunal = by_name.get(name.casefold())
        if tribunal is None:
            taken = {t.id for t in tribunals}
            base = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "tribunal"
            ident, n = base, 2
            while ident in taken:
                ident, n = f"{base}_{n}", n + 1
            tribunal = Tribunal(id=ident, name=name)
            tribunals.append(tribunal)
            by_name[name.casefold()] = tribunal
        covenant["tribunal_id"] = tribunal.id


def _key_lab_text_access_by_author(saga: Saga) -> None:
    """Key who can read whose Lab Texts by the author's character id, not
    name (older saves used the name, which a rename broke): an
    entry, or a decoding under way, naming exactly one character of the
    saga moves to that character's id. Any other name stays as typed."""
    ids = {c.id for c in saga.characters}
    by_name: dict[str, list[str]] = {}
    for character in saga.characters:
        by_name.setdefault(character.name, []).append(character.id)

    def key(author: str) -> str:
        found = by_name.get(author, [])
        return found[0] if author not in ids and len(found) == 1 else author

    for character in saga.characters:
        moved: dict[str, LabTextAccess] = {}
        for author, access in character.lab_text_access.items():
            kept = moved.get(key(author))
            if kept is None or access.level > kept.level:
                moved[key(author)] = access
        character.lab_text_access = moved
    for project in saga.lab_projects:
        # A decoding under way: "decode:<reader id>:<author>".
        prefix, _, author = project.spell_id.rpartition(":")
        if prefix.startswith("decode:") and author:
            project.spell_id = f"{prefix}:{key(author)}"


def _link_vis_store_locations(saga: Saga) -> None:
    """Give every covenant Raw Vis Store a real place it is kept
    (older saves only had free text): the laboratory or character
    of the covenant that the text names, else the covenant itself, with the
    text left as the store's note on where exactly."""
    for covenant in saga.covenants:
        places: list[tuple[str, str, str]] = [
            ("laboratory", lab.id, lab.name)
            for lab in saga.laboratories
            if lab.covenant_id == covenant.id
        ] + [
            ("character", c.id, c.name)
            for c in saga.characters
            if c.covenant_id == covenant.id
        ]
        for store in covenant.possessions:
            if store.kind != "vis_store" or store.location_kind:
                continue
            text = store.location.strip().lower()
            match = next(
                (p for p in places if text and p[2].strip().lower() == text), None
            )
            if match is not None:
                store.location_kind, store.location_id = match[0], match[1]
                store.location = ""
            else:
                store.location_kind, store.location_id = "covenant", covenant.id


def assign_laboratory(saga: Saga, character: Character, new_lab_id: str | None) -> None:
    """Give `character` the laboratory `new_lab_id` (or none), keeping
    Character.assigned_lab_id and Laboratory.owner_id in sync from both
    directions: the character's old lab (if any) is freed, and if the new lab
    already had a different owner, that character is unassigned too, so a lab
    never has an owner who doesn't point back at it or vice versa."""
    old_lab = saga.laboratory(character.assigned_lab_id)
    if old_lab is not None:
        old_lab.owner_id = None

    character.assigned_lab_id = new_lab_id
    if new_lab_id is None:
        return

    new_lab = next(lab for lab in saga.laboratories if lab.id == new_lab_id)
    previous_owner = saga.character(new_lab.owner_id)
    if previous_owner is not None:
        previous_owner.assigned_lab_id = None
    new_lab.owner_id = character.id


def assign_laboratory_owner(
    saga: Saga, lab: Laboratory, new_owner_id: str | None
) -> None:
    """Owner reassignment from the laboratory's side -- the inverse of
    assign_laboratory(), with the same two-way sync."""
    if new_owner_id is None:
        if lab.owner_id is not None:
            old_owner = saga.character(lab.owner_id)
            if old_owner is not None:
                old_owner.assigned_lab_id = None
            lab.owner_id = None
        return
    new_owner = next(c for c in saga.characters if c.id == new_owner_id)
    assign_laboratory(saga, new_owner, lab.id)


def add_raw_vis(pool: dict[str, int], art: str, pawns: int) -> None:
    """Add `pawns` of `art` to a Raw Vis pool (merging with any already held)."""
    pool[art] = pool.get(art, 0) + pawns


def replace_raw_vis(pool: dict[str, int], old_art: str, art: str, pawns: int) -> None:
    """Replace the `old_art` entry of a Raw Vis pool with `pawns` of `art`;
    re-pointing it at an Art already held merges the pawns into it."""
    del pool[old_art]
    add_raw_vis(pool, art, pawns)


def boon_hook_params(
    detail: str,
    description: str,
    base: dict[str, str] | None = None,
    *,
    unknown: bool = False,
) -> dict[str, str]:
    """The `params` of a covenant Boon/Hook: `base` (any keys we don't own)
    plus the detail and description, each stored only when non-empty, and
    the Unknown mark when `unknown`."""
    params = {
        k: v
        for k, v in (base or {}).items()
        if k not in (BOON_HOOK_DETAIL, BOON_HOOK_DESCRIPTION, BOON_HOOK_UNKNOWN)
    }
    if detail.strip():
        params[BOON_HOOK_DETAIL] = detail.strip()
    if description.strip():
        params[BOON_HOOK_DESCRIPTION] = description.strip()
    if unknown:
        params[BOON_HOOK_UNKNOWN] = "yes"
    return params
