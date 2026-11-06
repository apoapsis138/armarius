"""The Saga, its players, and the helpers that work across records."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from .atlas import AtlasMap, Pin
from .books import Book, Codex
from .character import Character, LabTextAccess
from .common import known_fields
from .conflicts import Battle, Fight, Siege, battle_from_lord
from .covenant import (
    BOON_HOOK_DESCRIPTION,
    BOON_HOOK_DETAIL,
    BOON_HOOK_UNKNOWN,
    CharterTemplate,
    Covenant,
)
from .creature import Creature
from .definitions import (
    AbilityDef,
    CovenantBoonHookDef,
    LabVirtueFlawDef,
    VirtueFlawDef,
)
from .devices import EnchantedDevice
from .familiar import Familiar
from .goods import GoodDef, GoodPurity
from .laboratory import Laboratory
from .marriage import Marriage
from .mystery_cults import MysteryCult
from .seasons import CalendarEntry, LabProject, SeasonPlan, SeasonRecord, WorldTurn
from .traits import Spell
from .tribunal import Tribunal
from .world import Neighbour


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


def _rosters_from_older_saves(neighbours: list[Neighbour]) -> None:
    """Older saves made a faction that belonged to another (a court's
    courtiers) answer to it: each becomes an entry of the other's roster
    (memberships.py), and answers to no one. A faction that has a roster
    already was moved before. Its links stay links: they name many ties
    besides membership ("their dread ruler", "twice attacked its tower")."""
    for faction in neighbours:
        if faction.kind != "faction" or "roster" in faction.details:
            continue
        roster: list[dict[str, str]] = []
        for other in neighbours:
            if other.kind == "faction" and other.answers_to == faction.id:
                roster.append({"who": f"neighbours:{other.id}", "role": ""})
                other.answers_to = None
        faction.details["roster"] = roster


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
    #: The lords, towns, churches, universities, factions and threats of
    #: the region (neighbours.py).
    neighbours: list[Neighbour] = field(default_factory=list)
    characters: list[Character] = field(default_factory=list)
    laboratories: list[Laboratory] = field(default_factory=list)
    books: list[Book] = field(default_factory=list)
    #: The codices binding several books together (see Codex).
    codices: list[Codex] = field(default_factory=list)
    spells: list[Spell] = field(default_factory=list)
    familiars: list[Familiar] = field(default_factory=list)
    #: The Bestiary: the saga's creatures (creatures.py).
    creatures: list[Creature] = field(default_factory=list)
    #: Every enchanted item in the saga, each shown on its holder's sheet.
    enchanted_devices: list[EnchantedDevice] = field(default_factory=list)
    #: The supplements and saga sources in play (sourcebooks.SUPPLEMENTS
    #: and `sources` abbreviations); None, the default and what older saves
    #: load as, means every book. The core book is always in play. See
    #: sourcebooks.
    books_in_play: list[str] | None = None
    #: The supplements turned on, by book: each overwrites the Tribunal
    #: packs it touches, now and when they are imported later.
    overlays: list[str] = field(default_factory=list)
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
    #: The non-Hermetic traditions the troupe has turned off
    #: (tradition_catalog.json ids): every other one is offered while its
    #: book is in play, so a book put in play brings its traditions on.
    traditions_off: list[str] = field(default_factory=list)
    #: Season plans not yet applied; a plan is removed when its
    #: season is applied.
    season_plans: list[SeasonPlan] = field(default_factory=list)
    #: Whether a record of each applied season is kept.
    keep_season_records: bool = True
    #: What a character with nothing planned does when the season is
    #: advanced, by kind (seasons.defaults: "exposure" or "nothing"), and
    #: whether Advance Season names the non-player characters among them.
    unplanned_magi: str = "exposure"
    unplanned_companions: str = "exposure"
    unplanned_grogs: str = "exposure"
    notify_npc_unplanned: bool = False
    #: Those records, oldest first.
    season_records: list[SeasonRecord] = field(default_factory=list)
    #: How many years Ahead looks (0: to the next Tribunal); see ahead.
    ahead_span: int = 2
    #: Which of Ahead's entries the terminal shows (ahead.SHOWS).
    ahead_show: str = "Everything"
    #: The storyguide's own entries in the saga's calendar, for Ahead.
    calendar: list[CalendarEntry] = field(default_factory=list)
    #: The saga's battles, fights and sieges, its Conflicts (battles.py,
    #: fights.py, sieges.py).
    battles: list[Battle] = field(default_factory=list)
    fights: list[Fight] = field(default_factory=list)
    sieges: list[Siege] = field(default_factory=list)
    #: The set of season medallions the desktop draws (medallions.SETS).
    medallions: str = "stained_glass"
    #: Each yearly step's entry (world_turns.py), oldest first.
    world_turns: list[WorldTurn] = field(default_factory=list)
    #: The outcomes a Tribunal's rulings are written from, each
    #: {"name", "text"} with {blanks} (ruling_templates.py); None, what
    #: older saves load as, means the app's own.
    ruling_templates: list[dict[str, str]] | None = None
    #: The charters the troupe saved to start covenants' own from
    #: (charter_templates.py), beside the book's.
    charter_templates: list[CharterTemplate] = field(default_factory=list)
    #: Lab work in progress over several seasons.
    lab_projects: list[LabProject] = field(default_factory=list)
    #: User-made catalog entries: house rules and entries from
    #: books the shared catalogs don't carry -- character Virtues & Flaws,
    #: laboratory Virtues & Flaws, covenant Boons & Hooks. Text only: no
    #: effects the rules engine applies. See house_rules.py.
    custom_virtues_flaws: list[VirtueFlawDef] = field(default_factory=list)
    custom_lab_virtues_flaws: list[LabVirtueFlawDef] = field(default_factory=list)
    custom_boons_hooks: list[CovenantBoonHookDef] = field(default_factory=list)
    #: The saga's own goods, beside the Goods catalog's (goods.py), and the
    #: purities it adds to goods priced by purity.
    custom_goods: list[GoodDef] = field(default_factory=list)
    good_purities: list[GoodPurity] = field(default_factory=list)
    #: The saga's own Abilities (own_abilities.py), beside the Ability
    #: catalog's: a Supernatural Ability the troupe designs (Houses of
    #: Hermes: Societates pp. 103-106).
    custom_abilities: list[AbilityDef] = field(default_factory=list)
    #: The saga's own Mystery Cults (mystery_cults.py), offered beside the
    #: tradition catalog's: their Lore, degrees and Initiation Scripts (The
    #: Mysteries Revised Edition pp. 13-19).
    custom_cults: list[MysteryCult] = field(default_factory=list)
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
    #: The saga's marriages and betrothals (marriages.py), each shown on
    #: the page of every house it joins.
    marriages: list[Marriage] = field(default_factory=list)
    #: The Atlas (atlas.py): the maps that belong to no Tribunal, and the
    #: pins on every map, the pack's and the troupe's. Older saves load
    #: without.
    maps: list[AtlasMap] = field(default_factory=list)
    pins: list[Pin] = field(default_factory=list)

    def covenant(self, covenant_id: str | None) -> Covenant | None:
        """The covenant with this id, if there is one."""
        return next((c for c in self.covenants if c.id == covenant_id), None)

    def tribunal(self, tribunal_id: str | None) -> Tribunal | None:
        """The Tribunal with this id, if there is one."""
        return next((t for t in self.tribunals if t.id == tribunal_id), None)

    def neighbour(self, neighbour_id: str | None) -> Neighbour | None:
        """The neighbour with this id, if there is one."""
        return next((n for n in self.neighbours if n.id == neighbour_id), None)

    def creature(self, creature_id: str | None) -> Creature | None:
        """The creature with this id, if there is one."""
        return next((c for c in self.creatures if c.id == creature_id), None)

    def character(self, character_id: str | None) -> Character | None:
        """The character with this id, if there is one."""
        return next((c for c in self.characters if c.id == character_id), None)

    def laboratory(self, laboratory_id: str | None) -> Laboratory | None:
        """The laboratory with this id, if there is one."""
        return next((lab for lab in self.laboratories if lab.id == laboratory_id), None)

    def familiar_of(self, character_id: str) -> Familiar | None:
        """The one Familiar bound to `character_id`, if any."""
        return next((f for f in self.familiars if f.character_id == character_id), None)

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], *, lab_feature_names: Mapping[str, str] | None = None
    ) -> Saga:
        """`lab_feature_names` names an older save's free-text laboratory
        Features (Laboratory.from_dict)."""
        d = dict(data)
        d["tribunals"] = [Tribunal.from_dict(t) for t in d.get("tribunals", [])]
        d["neighbours"] = [Neighbour.from_dict(n) for n in d.get("neighbours", [])]
        raw_covenants = [dict(c) for c in d.get("covenants", [])]
        _tribunals_from_names(raw_covenants, d["tribunals"])
        d["covenants"] = [Covenant.from_dict(c) for c in raw_covenants]
        d["characters"] = [Character.from_dict(c) for c in d.get("characters", [])]
        d["laboratories"] = [
            Laboratory.from_dict(lab, lab_feature_names)
            for lab in d.get("laboratories", [])
        ]
        d["familiars"] = [Familiar.from_dict(f) for f in d.get("familiars", [])]
        d["creatures"] = [Creature.from_dict(c) for c in d.get("creatures", [])]
        d["enchanted_devices"] = [
            EnchantedDevice.from_dict(e) for e in d.get("enchanted_devices", [])
        ]
        d["spells"] = [Spell.from_dict(s) for s in d.get("spells", [])]
        d["season_plans"] = [SeasonPlan.from_dict(p) for p in d.get("season_plans", [])]
        d["season_records"] = [
            SeasonRecord.from_dict(r) for r in d.get("season_records", [])
        ]
        d["calendar"] = [CalendarEntry.from_dict(e) for e in d.get("calendar", [])]
        d["fights"] = [Fight.from_dict(f) for f in d.get("fights", [])]
        d["battles"] = [Battle.from_dict(b) for b in d.get("battles", [])]
        # Older saves kept each battle in its lord's details.
        for neighbour in d["neighbours"]:
            old = neighbour.details.pop("battles", None) or []
            for index, entry in enumerate(old):
                d["battles"].append(battle_from_lord(neighbour.id, index, entry))
        _rosters_from_older_saves(d["neighbours"])
        d["sieges"] = [Siege.from_dict(s) for s in d.get("sieges", [])]
        d["world_turns"] = [WorldTurn.from_dict(t) for t in d.get("world_turns", [])]
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
        d["charter_templates"] = [
            CharterTemplate.from_dict(c) for c in d.get("charter_templates", [])
        ]
        d["custom_goods"] = [GoodDef.from_dict(g) for g in d.get("custom_goods", [])]
        d["good_purities"] = [
            GoodPurity.from_dict(p) for p in d.get("good_purities", [])
        ]
        d["custom_abilities"] = [
            AbilityDef.from_dict(a) for a in d.get("custom_abilities", [])
        ]
        d["custom_cults"] = [
            MysteryCult.from_dict(c) for c in d.get("custom_cults", [])
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
        # The saga's marriages.
        d["marriages"] = [Marriage.from_dict(m) for m in d.get("marriages") or []]
        d["maps"] = [AtlasMap.from_dict(m) for m in d.get("maps") or []]
        d["pins"] = [Pin.from_dict(pin) for pin in d.get("pins") or []]
        # Older saves listed the traditions turned on, each off until
        # turned on; they move to the default, every one on.
        d.pop("traditions", None)
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
