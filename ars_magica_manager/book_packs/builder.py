"""The Builder a book's module assembles its saga with: one method per
kind of record, each taking the facts a sourcebook gives in plain
arguments and returning the record, so a book's module reads as a list
of what the book says. The records are the app's own (a Tribunal, a
Covenant, a Character, a Neighbour of each kind, a Book), so the pack
is an ordinary export and the sheets show it like anything the user
typed.

A record's secrets go in its own `secrets` (each method's `secrets=`),
the Secrets chapter a player never sees. The few texts that are part of
another record (a regio level's notes, a case's charge, a Tribunal's
diary entry, a book's description) keep theirs at their end under a
"Secrets" heading (`secrets()` writes it)."""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import replace
from functools import cache
from typing import Any

from .. import catalog, sourcebooks, storage
from .. import tombs as tomb_rules
from ..arms import Arms
from ..arts import ART_LOOKUP
from ..atlas import Point, maps
from ..models import (
    ONCE,
    REPEATS,
    Ability,
    ArtScore,
    AtlasMap,
    BodyVis,
    Book,
    BoundBeing,
    CalendarEntry,
    Case,
    Character,
    Codex,
    Covenant,
    CovenantDiaryEntry,
    Creature,
    CreatureAttack,
    CreaturePower,
    EnchantedDevice,
    InstilledEffect,
    KnownSpell,
    LabCharacteristics,
    Laboratory,
    LabSpecialtyEntry,
    Link,
    MasteryAbility,
    NamedDescription,
    Neighbour,
    Pin,
    Possession,
    Ruling,
    Saga,
    ScoredTrait,
    Spell,
    TraditionEffect,
    Tribunal,
    TribunalDiaryEntry,
    VirtueFlawInstance,
    as_character_type,
)
from ..models.common import SEASONS, SECRETS_HEADING
from ..models.world import FULL, SKETCH
from ..places import RUINED
from ..references import KINDS
from ..rules import aging, mobile, warping
from ..rules import creation_access as access
from ..rules import egyptian_tombs as et
from ..rules.sites import PLACE, WATERS
from ..rules.xp import ability_xp, art_xp
from ..threats import DORMANT
from ..tombs import TombCurse, TombTrap, TombWard
from ..tribunal_packages import rhine as rhine_package

SECRETS = SECRETS_HEADING


def secrets(text: str, hidden: str) -> str:
    """`text` with `hidden` after it under the Secrets heading; `text`
    alone when there is nothing hidden."""
    if not hidden.strip():
        return text
    return f"{text.rstrip()}\n\n{SECRETS}\n{hidden.strip()}"


def paragraphs(*parts: str) -> str:
    """The parts as paragraphs, blank ones left out."""
    return "\n\n".join(p.strip() for p in parts if p.strip())


def joined_lines(*lines: str) -> str:
    """The lines as one text, one a line."""
    return "\n".join(lines)


def vf_art(name: str, art: str) -> tuple[str, dict[str, str]]:
    """A Virtue or Flaw taken for an Art ("Affinity with {art}")."""
    return (name, {"art": art})


def vf_ability(name: str, ability: str) -> tuple[str, dict[str, str]]:
    """A Virtue or Flaw taken for an Ability ("Affinity with {ability}")."""
    return (name, {"ability": ability})


def vf_focus(name: str, focus: str) -> tuple[str, dict[str, str]]:
    """A Virtue taken with a focus (a Magical Focus's)."""
    return (name, {"focus": focus})


def vf_puissant(ability: str) -> tuple[str, dict[str, str]]:
    return ("Puissant {ability}", {"ability": ability})


def vf_minor(virtue: str) -> tuple[str, dict[str, str]]:
    return ("Minor Virtue", {"virtue": virtue})


def vf_great(characteristic: str) -> tuple[str, dict[str, str]]:
    return ("Great {characteristic}", {"characteristic": characteristic})


def vf_ward(ward: str) -> tuple[str, dict[str, str]]:
    return ("Traditional Ward", {"ward": ward})


def _top_level_items(text: str) -> list[str]:
    """`text` split at the semicolons outside parentheses."""
    items, depth, start = [], 0, 0
    for at, char in enumerate(text):
        depth += {"(": 1, ")": -1}.get(char, 0)
        if char == ";" and depth == 0:
            items.append(text[start:at].strip())
            start = at + 1
    items.append(text[start:].strip())
    return [item for item in items if item]


def boons_hooks_from(what_matters: str) -> list[VirtueFlawInstance]:
    """The catalog Boons and Hooks a covenant's "Boon: ..." and "Hook:
    ..." lines name, each with the words in its brackets as its detail.
    A name the catalog has at both tiers is taken only when the line says
    which ("Poverty (Minor)"); one it lacks, or leaves in doubt, stays as
    words only."""
    by_name: dict[tuple[str, str], list[Any]] = {}
    for entry in catalog.load_covenant_boon_hook_catalog():
        by_name.setdefault((entry.type, entry.name.casefold()), []).append(entry)
    found: list[VirtueFlawInstance] = []
    for line in what_matters.splitlines():
        kind, _, rest = line.partition(": ")
        if kind not in ("Boon", "Hook"):
            continue
        for item in _top_level_items(rest):
            name, _, detail = item.partition(" (")
            detail = detail.rsplit(")", 1)[0] if detail else ""
            tier = ""
            if detail.split(")")[0] in ("Minor", "Major"):
                tier = detail.split(")")[0]
                detail = detail.partition("(")[2]
            entries = by_name.get((kind, name.strip().casefold()), [])
            if tier:
                entries = [e for e in entries if e.tier == tier]
            if len(entries) != 1:
                continue
            params = {"detail": detail.strip()} if detail.strip() else {}
            found.append(VirtueFlawInstance(entries[0].id, params=params))
    return found


def fill_boons_hooks(saga: Saga) -> None:
    """Each covenant with no Boons or Hooks recorded takes those its
    "Boon:" and "Hook:" lines name (boons_hooks_from)."""
    for covenant in saga.covenants:
        if not covenant.boons_hooks:
            covenant.boons_hooks = boons_hooks_from(covenant.what_matters)


def characteristics(
    int_: int, per: int, pre: int, com: int, str_: int, sta: int, dex: int, qik: int
) -> dict[str, int]:
    """Characteristics in the book's order (Int or Cun, Per, Pre, Com, Str,
    Sta, Dex, Qik)."""
    return {
        "intelligence": int_,
        "perception": per,
        "presence": pre,
        "communication": com,
        "strength": str_,
        "stamina": sta,
        "dexterity": dex,
        "quickness": qik,
    }


def arts_from(printed: str) -> dict[str, int]:
    """The Arts of a stat block as a book prints them ("Cr 10, In 9, ..."),
    for its "arts"; a bonus after a score ("Pe 12+3") is the Puissant Art's
    and is left to the Virtue."""
    found = {}
    for entry in printed.replace(";", ",").split(","):
        abbreviation, score = entry.split()
        found[ART_LOOKUP[abbreviation.lower()]] = int(score.split("+")[0])
    return found


def add_possession(
    covenant: Covenant, kind: str, name: str, **fields: Any
) -> Possession:
    """A Possession of a covenant, of a kind of POSSESSION_KINDS."""
    possession = Possession(
        id=storage.generate_unique_id(name, [p.id for p in covenant.possessions]),
        kind=kind,
        name=name,
        **fields,
    )
    covenant.possessions.append(possession)
    return possession


def wound_ranges(size: int) -> str:
    """The wound ranges for a Size, as the book's blocks print them."""
    step = 5 + size
    return (
        f"Wound ranges: Light 1-{step}, Medium to {2 * step}, Heavy to "
        f"{3 * step}, Incapacitated to {4 * step}, Dead from {4 * step + 1}."
    )


def dormant(threat: Neighbour) -> Neighbour:
    """Mark a threat as not yet begun: More, Begin This Story starts it."""
    threat.details[DORMANT] = True
    return threat


#: The Divine aura over most of a town or city, and of a village (Definitive
#: Edition p. 418).
DIVINE_CITY_AURA, DIVINE_VILLAGE_AURA = 3, 2


class Builder:
    """A saga under construction, as of a year and season."""

    def __init__(
        self,
        name: str,
        year: int = 1220,
        season: str = "Spring",
        source: str = "",
        known: str = "In the Tribunal",
    ) -> None:
        #: The book's abbreviation (sourcebooks.SOURCEBOOKS), for the
        #: spells its stat blocks add.
        self.source = source
        #: How widely a place is known when `place()` is not told: a
        #: region pack, with no Tribunal, says "In the region".
        self.known = known
        self.saga = Saga(
            id=storage.generate_unique_id(name, []),
            name=name,
            current_year=year,
            current_season=season,
        )
        self.year = year
        #: Each generated magus's sketch, by id, as the book gives them
        #: (book_packs.generated): the pack offers it in place of the
        #: generated stats.
        #: A magus printed at several ages: {character id: [{"label", "age",
        #: "character"}]} (packs.VARIANTS).
        self.variants: dict[str, list[dict[str, Any]]] = {}
        #: {character id: the covenant the book ties them to} (packs.HOMES).
        self.homes: dict[str, str] = {}
        #: {character id: the sketch a Tribunal pack has} (packs.REPLACES).
        self.replaces: dict[str, str] = {}
        self.sketches: dict[str, Character] = {}

    # -- ids --

    def _covenant_id(self, name: str) -> str:
        return storage.generate_unique_id(name, [c.id for c in self.saga.covenants])

    def _character_id(self, name: str) -> str:
        return storage.generate_unique_id(name, [c.id for c in self.saga.characters])

    def _neighbour_id(self, name: str) -> str:
        return storage.generate_unique_id(name, [n.id for n in self.saga.neighbours])

    def _creature_id(self, name: str) -> str:
        return storage.generate_unique_id(name, [c.id for c in self.saga.creatures])

    def _book_id(self, name: str) -> str:
        return storage.generate_unique_id(name, [b.id for b in self.saga.books])

    # -- the Tribunal --

    def tribunal(
        self,
        name: str,
        *,
        package: str,
        summary: str,
        meets_every: int,
        next_year: int,
        next_season: str,
        meeting_place: str,
        covenants_total: int | None = None,
        magi_total: int | None = None,
        secrets: str = "",
    ) -> Tribunal:
        tribunal = Tribunal(
            id=storage.generate_unique_id(name, [t.id for t in self.saga.tribunals]),
            name=name,
            summary=summary,
            package=package,
            meets_every=meets_every,
            next_year=next_year,
            next_season=next_season,
            meeting_place=meeting_place,
            covenants_total=covenants_total,
            magi_total=magi_total,
            secrets=secrets,
        )
        self.saga.tribunals.append(tribunal)
        return tribunal

    # -- the Atlas --

    def atlas_map(
        self,
        name: str,
        *,
        tribunal: Tribunal | None = None,
        picture: str = "",
        width: int = 3,
        height: int = 2,
        credit: str = "",
        scale_bar: Sequence[float] = (),
        scale_miles: float = 0.0,
    ) -> AtlasMap:
        """A map of `tribunal` (the saga's own, for a region with none):
        `picture` a file in data/packs/maps/, or none for a placeholder in
        the shape `width` by `height`."""
        made = AtlasMap(
            id=storage.generate_unique_id(name, [m.id for m, _t in maps(self.saga)]),
            name=name,
            picture=picture,
            width=width,
            height=height,
            credit=credit,
            scale_bar=list(scale_bar),
            scale_miles=scale_miles,
        )
        (tribunal.maps if tribunal is not None else self.saga.maps).append(made)
        return made

    def pin(
        self, atlas_map: AtlasMap, record: Covenant | Neighbour | Creature, at: Point
    ) -> Pin:
        """The pack's pin for `record` on `atlas_map`, `at` (x, y) as
        fractions of the map's width and height."""
        kind = KINDS[type(record)]
        made = Pin(atlas_map.id, kind, record.id, at[0], at[1], from_pack=True)
        self.saga.pins.append(made)
        return made

    def gild(
        self,
        tribunal: Tribunal,
        name: str,
        agenda: str,
        members: list[Covenant],
        *,
        leaders: list[Character],
        magi: list[Character],
    ) -> dict[str, Any]:
        """A Rhine gild: its agenda, its leaders, the magi the book says
        belong to it (each in one gild only), and the covenants most of
        whose magi belong to it."""
        gild: dict[str, Any] = {
            "name": name,
            "agenda": agenda,
            "leader_ids": [c.id for c in leaders],
            "magi": [],
            "members": [c.id for c in members],
        }
        rhine_package.gilds(tribunal).append(gild)
        for magus in magi:
            rhine_package.join(tribunal, magus.id, gild)
        return gild

    def ruling(
        self, tribunal: Tribunal, title: str, year: int | None, says: str
    ) -> Ruling:
        ruling = Ruling(title=title, year=year, says=says)
        tribunal.rulings.append(ruling)
        return ruling

    def case(
        self,
        tribunal: Tribunal,
        title: str,
        *,
        kind: str = "charge",
        brought_by: str = "",
        against: str = "",
        charge: str = "",
        filed_year: int | None = None,
        filed_season: str = "",
        notice_given: bool = False,
        evidence: str = "",
    ) -> Case:
        case = Case(
            title=title,
            kind=kind,
            brought_by=brought_by,
            against=against,
            charge=charge,
            filed_year=filed_year,
            filed_season=filed_season,
            notice_given=notice_given,
            evidence=evidence,
        )
        tribunal.cases.append(case)
        return case

    def event(
        self,
        tribunal: Tribunal,
        year: int,
        title: str,
        details: str = "",
        season: str = "",
    ) -> TribunalDiaryEntry:
        entry = TribunalDiaryEntry(
            year=year, season=season, title=title, details=details
        )
        tribunal.diary.append(entry)
        return entry

    # -- history outside a Tribunal --

    def chronicle(
        self,
        covenant: Covenant,
        year: int,
        title: str,
        details: str = "",
        season: str = "Spring",
        category: str = "",
    ) -> CovenantDiaryEntry:
        """A line of a covenant's own Diary: the history a pack with no
        Tribunal keeps there, where a Tribunal's book would use `event`."""
        if season not in SEASONS:
            raise ValueError(f"Unknown season {season!r}; must be one of {SEASONS}")
        entry = CovenantDiaryEntry(
            year=year, season=season, name=title, details=details, category=category
        )
        covenant.diary.append(entry)
        return entry

    def calendar(
        self,
        title: str,
        year: int,
        season: str = "Spring",
        *,
        repeats: str = ONCE,
        every: int | None = None,
        note: str = "",
        covenant: Covenant | None = None,
    ) -> CalendarEntry:
        """An entry in the saga's calendar, for Ahead: something coming in
        the pack's year or later (a yearly council, say), for one covenant
        or, with none, the whole saga."""
        if season not in SEASONS:
            raise ValueError(f"Unknown season {season!r}; must be one of {SEASONS}")
        if repeats not in REPEATS:
            raise ValueError(f"Unknown repeats {repeats!r}; must be one of {REPEATS}")
        entry = CalendarEntry(
            title=title,
            year=year,
            season=season,
            repeats=repeats,
            every=every,
            note=note,
            covenant_id=covenant.id if covenant is not None else None,
        )
        self.saga.calendar.append(entry)
        return entry

    # -- covenants and their people --

    def covenant(
        self,
        name: str,
        *,
        tribunal: Tribunal | None = None,
        founded: int | None,
        summary: str,
        what_matters: str = "",
        notes: str = "",
        place: Neighbour | None = None,
        level: int = 0,
        aura: int = 0,
        realm: str = "Magic",
        unnamed_magi: int = 0,
        detail: str = SKETCH,
        season: str = "Summer",
        arms: Arms | None = None,
        liege: Covenant | None = None,
        oath: str = "",
        aegis: int = 0,
        secrets: str = "",
    ) -> Covenant:
        """A covenant of the book's Tribunal, not played, or with no
        `tribunal` one outside every Tribunal, on no Tribunal's roster: its
        aura is the one typed here, or its place's when it sits in one; `liege` is the
        covenant it is sworn to, with the oath's duties in `oath`; `aegis`
        is the level of its Aegis of the Hearth, where the book gives one."""
        covenant = Covenant(
            id=self._covenant_id(name),
            saga_id=self.saga.id,
            name=name,
            notes=notes,
            aura=aura,
            aura_realm=realm,
            tribunal_id=tribunal.id if tribunal is not None else None,
            year_founded=founded,
            covenant_season=season,
            detail=detail,
            summary=summary,
            played=False,
            unnamed_magi=unnamed_magi,
            what_matters=what_matters,
            arms=arms.to_dict() if arms else {},
            liege_id=liege.id if liege is not None else None,
            oath=oath,
            aegis_of_the_hearth=aegis,
            secrets=secrets,
        )
        if place is not None:
            covenant.place_id, covenant.place_level = place.id, level
        self.saga.covenants.append(covenant)
        return covenant

    def magus(
        self,
        name: str,
        *,
        covenant: Covenant | None,
        house: str,
        age: int | None,
        summary: str,
        traits: dict[str, int] | None = None,
        detail: str = SKETCH,
        type: str = "magus",
        traditions: list[str] | None = None,
        secrets: str = "",
    ) -> Character:
        """A magus the book names, as a sketch: House, age as of the
        pack's year, a paragraph, and personality traits where given. Any
        other character too, by its `type`; `traditions` are the hedge
        traditions it belongs to (tradition catalog ids), each giving it
        that tradition's chapter."""
        character = Character(
            id=self._character_id(name),
            name=name,
            type=as_character_type(type),
            covenant_id=covenant.id if covenant else None,
            detail=detail,
            summary=summary,
            secrets=secrets,
            traditions=list(traditions or []),
        )
        character.hermetic.house = house
        if age is not None:
            character.background.year_born = self.year - age
        character.personality_traits = [
            ScoredTrait(name=trait, score=score)
            for trait, score in (traits or {}).items()
        ]
        self.saga.characters.append(character)
        return character

    def book(
        self,
        owner: Covenant,
        name: str,
        type: str,
        *,
        art: str = "",
        ability: str = "",
        level: int | None = None,
        quality: int | None = None,
        language: str = "Latin",
        author: str = "",
        description: str = "",
    ) -> Book:
        """A book of a covenant's library, as a Book record owned by it."""
        book = Book(
            id=self._book_id(name),
            name=name,
            type=type,
            language=language,
            author=author,
            owner_kind="covenant",
            owner_id=owner.id,
            description=description,
            subject_kind="Art" if art else ("Ability" if ability else ""),
            art=art,
            ability=ability,
            level=level,
            quality=quality,
        )
        self.saga.books.append(book)
        return book

    def codex(
        self, name: str, books: list[Book], *, encyclopedia: bool = False
    ) -> Codex:
        """`books` bound into one tome; an encyclopedia also aids research
        like a library of its own (Art & Academe)."""
        codex = Codex(
            id=storage.generate_unique_id(name, [c.id for c in self.saga.codices]),
            name=name,
            encyclopedia=encyclopedia,
        )
        self.saga.codices.append(codex)
        for book in books:
            book.codex_id = codex.id
        return codex

    def device(
        self,
        holder: Covenant,
        name: str,
        *,
        description: str,
        effects: list[InstilledEffect],
    ) -> EnchantedDevice:
        """An invested device a covenant holds, with the effects the book
        prints (each effect's level before the item's modifications)."""
        device = EnchantedDevice(
            id=storage.generate_unique_id(
                name, [d.id for d in self.saga.enchanted_devices]
            ),
            name=name,
            description=description,
            holder_kind="covenant",
            holder_id=holder.id,
        )
        for number, effect in enumerate(effects, 1):
            effect.id = f"{device.id}-{number}"
            device.effects.append(effect)
        self.saga.enchanted_devices.append(device)
        return device

    def tablet(self, owner: Covenant, spell_id: str, *, description: str) -> Book:
        """A Casting Tablet of a catalog spell, kept in a covenant's
        library (Covenants pp. 89-90)."""
        spell = catalog.load_spell_catalog_by_id()[spell_id]
        book = self.book(owner, spell.name, "Casting Tablet", description=description)
        book.spell_id, book.spell_name, book.level = spell.id, spell.name, spell.level
        return book

    def laboratory(
        self,
        covenant: Covenant,
        name: str,
        *,
        owner: Character | None = None,
        characteristics: dict[str, int],
        specializations: dict[str, int],
        source: str,
        rooms: dict[str, str] | None = None,
    ) -> Laboratory:
        """A laboratory of `covenant` as the book prints it: its
        Characteristics and Specializations at the book's totals, kept as
        entered values, with its Virtues and Flaws named only in words (a
        room of the laboratory, as `rooms` gives them), so nothing is
        counted twice."""
        lab = Laboratory(
            id=storage.generate_unique_id(name, [x.id for x in self.saga.laboratories]),
            covenant_id=covenant.id,
            name=name,
            owner_id=owner.id if owner is not None else None,
            characteristics=LabCharacteristics(**characteristics),
            specialties=[
                LabSpecialtyEntry(specialization, points, source)
                for specialization, points in specializations.items()
            ],
            rooms=[
                NamedDescription(room, words) for room, words in (rooms or {}).items()
            ],
        )
        self.saga.laboratories.append(lab)
        return lab

    # -- the world --

    def neighbour(
        self,
        kind: str,
        name: str,
        *,
        summary: str,
        details: dict[str, Any] | None = None,
        ruler: str = "",
        answers_to: Neighbour | None = None,
        realm: str = "",
        place: Neighbour | None = None,
        level: int = 0,
        detail: str = SKETCH,
        arms: Arms | None = None,
        secrets: str = "",
    ) -> Neighbour:
        neighbour = Neighbour(
            id=self._neighbour_id(name),
            name=name,
            kind=kind,
            summary=summary,
            detail=detail,
            ruler=ruler,
            answers_to=answers_to.id if answers_to else None,
            realm=realm,
            details=dict(details or {}),
            arms=arms.to_dict() if arms else {},
            secrets=secrets,
        )
        if place is not None:
            neighbour.place_id, neighbour.place_level = place.id, level
        self.saga.neighbours.append(neighbour)
        return neighbour

    def place(
        self,
        name: str,
        *,
        summary: str,
        secrets: str = "",
        inside: Neighbour | None = None,
        level: int = 0,
        realm: str = "Magic",
        aura: int = 0,
        status: str = "Known",
        known: str | None = None,
        tethers: str = "",
        levels: list[dict[str, Any]] | None = None,
        detail: str = SKETCH,
        ruined: bool = False,
    ) -> Neighbour:
        """A forest, a site or a regio: its surface aura in `realm`, and
        its regio levels as `level(...)` entries, each with its own aura.
        `known` is how widely it is known, the Builder's `known` unless
        given. `ruined` marks a fallen covenant's site."""
        found = self.neighbour(
            PLACE,
            name,
            summary=summary,
            secrets=secrets,
            realm=realm,
            place=inside,
            level=level,
            detail=detail,
            details={
                "aura": aura,
                "tethers": tethers,
                "status": status,
                "known": self.known if known is None else known,
                "levels": list(levels or []),
            },
        )
        if ruined:
            found.details[RUINED] = True
        return found

    @staticmethod
    def level(
        name: str,
        aura: int,
        realm: str = "Magic",
        *,
        see: str = "",
        enter: str = "",
        notes: str = "",
    ) -> dict[str, Any]:
        """One regio level of a place, for `place(levels=[...])`."""
        return {
            "name": name,
            "realm": realm,
            "aura": aura,
            "see": see,
            "enter": enter,
            "notes": notes,
        }

    @staticmethod
    def tomb(
        place: Neighbour,
        *,
        kind: str = et.DEFAULT_KIND,
        boons: str = "",
        hooks: str = "",
        hook_points: int = 0,
        other: str = "",
        other_bp: int = 0,
        curses: Sequence[TombCurse] = (),
        wards: Sequence[TombWard] = (),
        traps: Sequence[TombTrap] = (),
    ) -> Neighbour:
        """Marks `place` a tomb (Lands of the Nile pp. 40-46) and gives it
        the curses, talismans, wards and traps the book prints, each
        checked by the rules the Tomb tab's forms use. Other resources
        are what the book prints for the library, specialists and vis."""
        for curse in curses:
            problem = et.curse_problem(
                curse.get("kind") or et.EFFECT, curse.get("level") or 0
            )
            if problem is not None:
                raise ValueError(f"{place.name}, {curse['name']}: {problem}")
        for trap in traps:
            if tomb_rules.trap_points(trap) == 0:
                raise ValueError(f"{place.name}, {trap['name']}: no such harm or ease.")
        place.details.update(
            {
                tomb_rules.TOMB: True,
                "tomb_kind": kind,
                "tomb_boons": boons,
                "tomb_hooks": hooks,
                "tomb_hook_points": hook_points,
                "tomb_other": other,
                "tomb_other_bp": other_bp,
                tomb_rules.CURSES: [dict(c) for c in curses],
                tomb_rules.WARDS: [dict(w) for w in wards],
                tomb_rules.TRAPS: [dict(t) for t in traps],
            }
        )
        return place

    def town(
        self,
        name: str,
        *,
        summary: str,
        secrets: str = "",
        charter: str = "",
        population: int | None = None,
        council: int | None = None,
        ruler: str = "",
        answers_to: Neighbour | None = None,
        place: Neighbour | None = None,
        arms: Arms | None = None,
    ) -> Neighbour:
        return self.neighbour(
            "town",
            name,
            summary=summary,
            secrets=secrets,
            ruler=ruler,
            answers_to=answers_to,
            place=place,
            arms=arms,
            details={"charter": charter, "population": population, "council": council},
        )

    def harbour(self, town: Neighbour, *, aura: int = DIVINE_CITY_AURA) -> Neighbour:
        """A Place for ships at `town`, beside it in its region, which the
        town links to: a stop must be a Place, and none can sit in a Town."""
        harbour = self.named_port(
            town.name,
            inside=self.saga.neighbour(town.place_id),
            summary=f"The harbour of the town of {town.name}.",
            aura=aura,
        )
        self.link(town, "places", harbour, "Its harbour")
        return harbour

    def named_port(
        self,
        name: str,
        *,
        inside: Neighbour | None,
        summary: str,
        aura: int = DIVINE_CITY_AURA,
    ) -> Neighbour:
        """A harbour Place, with its own Divine aura."""
        harbour = self.place(
            f"The harbour of {name}",
            inside=inside,
            summary=summary,
            realm="Divine",
            aura=aura,
        )
        harbour.details[WATERS] = mobile.PORT
        return harbour

    def lord(
        self,
        name: str,
        *,
        summary: str,
        secrets: str = "",
        title: str = "landed",
        wealth: str = "Average",
        manors: int = 1,
        seat: str = "",
        ruler: str = "",
        answers_to: Neighbour | None = None,
        place: Neighbour | None = None,
        arms: Arms | None = None,
    ) -> Neighbour:
        return self.neighbour(
            "lord",
            name,
            summary=summary,
            secrets=secrets,
            ruler=ruler,
            answers_to=answers_to,
            place=place,
            arms=arms,
            details={"title": title, "wealth": wealth, "manors": manors, "seat": seat},
        )

    def church(
        self,
        name: str,
        *,
        summary: str,
        secrets: str = "",
        church: str = "Parish church",
        order: str = "",
        ruler: str = "",
        answers_to: Neighbour | None = None,
        place: Neighbour | None = None,
        arms: Arms | None = None,
        founded: int | None = None,
    ) -> Neighbour:
        return self.neighbour(
            "church",
            name,
            summary=summary,
            secrets=secrets,
            ruler=ruler,
            answers_to=answers_to,
            place=place,
            arms=arms,
            realm="Divine",
            details={"church": church, "order": order, "founded": founded},
        )

    def university(
        self,
        name: str,
        *,
        summary: str,
        secrets: str = "",
        school: str = "Cathedral school",
        ruler: str = "",
        answers_to: Neighbour | None = None,
        place: Neighbour | None = None,
    ) -> Neighbour:
        return self.neighbour(
            "university",
            name,
            summary=summary,
            secrets=secrets,
            ruler=ruler,
            answers_to=answers_to,
            place=place,
            details={"school": school},
        )

    def faction(
        self,
        name: str,
        *,
        summary: str,
        secrets: str = "",
        faction: str = "Other",
        decides: str = "",
        members: int | None = None,
        rules: str = "",
        wants: str = "",
        offers: str = "",
        ruler: str = "",
        realm: str = "",
        place: Neighbour | None = None,
        arms: Arms | None = None,
        tradition: str = "",
    ) -> Neighbour:
        return self.neighbour(
            "faction",
            name,
            summary=summary,
            secrets=secrets,
            ruler=ruler,
            realm=realm,
            place=place,
            arms=arms,
            details={
                "faction": faction,
                "decides": decides,
                "members": members,
                "rules": rules,
                "wants": wants,
                "offers": offers,
                # A hedge coven's tradition record, when it has one.
                **({"tradition": tradition} if tradition else {}),
            },
        )

    def custom(
        self,
        name: str,
        *,
        summary: str,
        secrets: str = "",
        rules: str = "",
        decides: str = "",
        wants: str = "",
        offers: str = "",
        ruler: str = "",
        realm: str = "",
        place: Neighbour | None = None,
    ) -> Neighbour:
        """A custom: a land's way of life, its law or its lore (customs.py).
        How those who keep it decide, when the book says, goes with its
        rules."""
        decided = f"Decided by: {decides}." if decides else ""
        return self.neighbour(
            "custom",
            name,
            summary=summary,
            secrets=secrets,
            ruler=ruler,
            realm=realm,
            place=place,
            details={
                "rules": paragraphs(*(p for p in (rules, decided) if p)),
                "wants": wants,
                "offers": offers,
            },
        )

    def threat(
        self,
        name: str,
        *,
        summary: str,
        secrets: str = "",
        antagonist: str = "",
        moves: str = "A track",
        position: int = 0,
        stages: list[dict[str, Any]] | None = None,
        realm: str = "",
        place: Neighbour | None = None,
    ) -> Neighbour:
        return self.neighbour(
            "threat",
            name,
            summary=summary,
            secrets=secrets,
            realm=realm,
            place=place,
            details={
                "antagonist": antagonist,
                "moves": moves,
                "position": position,
                "stages": list(stages or []),
            },
        )

    @staticmethod
    def stage(
        title: str,
        *,
        year: int | None = None,
        season: str = "",
        at: int | None = None,
        clues: str = "",
        ignored: str = "",
        stopped: str = "",
        turned: str = "",
    ) -> dict[str, Any]:
        """One stage of a threat, for `threat(stages=[...])`: when it
        comes (a date, or a number on the track), the clues before it,
        and what follows if it is ignored, stopped or turned."""
        return {
            "title": title,
            "year": year,
            "season": season,
            "at": at,
            "clues": clues,
            "ignored": ignored,
            "stopped": stopped,
            "turned": turned,
        }

    def absorb(self, keep: str, drop: str, *, kind: str = PLACE) -> None:
        """Merge two parts' records of one thing, both of `kind` (a place
        unless it says otherwise): `drop`'s words go on `keep`, whatever
        sat in it or pointed at it moves there, and it goes. With the same
        name twice, the later record is the one dropped."""
        records = [n for n in self.saga.neighbours if n.kind == kind]
        kept = next(n for n in records if n.name == keep)
        gone = next(n for n in reversed(records) if n.name == drop and n is not kept)
        kept.summary = paragraphs(kept.summary, gone.summary)
        kept.secrets = paragraphs(kept.secrets, gone.secrets).strip()
        for record in self.saga.neighbours:
            if record.answers_to == gone.id:
                record.answers_to = kept.id
        for record in (*self.saga.neighbours, *self.saga.creatures):
            if record.place_id == gone.id:
                record.place_id = kept.id
        for record in (*self.saga.neighbours, *self.saga.creatures):
            for link in record.links:
                if link.target_id == gone.id:
                    link.target_id = kept.id
        self.saga.neighbours.remove(gone)

    # -- the Bestiary --

    def creature(
        self,
        name: str,
        *,
        page: str,
        realm: str = "",
        might: int = 0,
        form: str = "",
        size: int = 0,
        block: StatBlock | None = None,
        season: str = "",
        attacks: list[CreatureAttack] | None = None,
        soak: int = 0,
        fatigue_levels: str = "",
        powers: list[CreaturePower] | None = None,
        vis: list[BodyVis] | None = None,
        equipment: str = "",
        appearance: str = "",
        notes: str = "",
        how_many: str = "",
        place: Neighbour | None = None,
        level: int = 0,
        cunning: bool = False,
        age: str = "",
        confidence: tuple[int, int] | None = None,
        encumbrance: str = "",
        tires: bool = True,
        can_be_wounded: bool = True,
        order: str = "",
        hierarchy: int | None = None,
        weakness: str = "",
        secrets: str = "",
        source: str = "",
    ) -> Creature:
        """A creature's stat block as the book prints it: its realm, Might
        and Form, Size, and the rest in `block`'s notation
        ("characteristics", "virtues_flaws" (its Qualities and
        Inferiorities too), "abilities", "traits", "reputations"), its
        attacks and powers (`attack()`, `power()`), and the vis in its
        body; `how_many` makes it a kind that comes in numbers. `page` is
        where in the pack's book it is printed, or in `source` (a
        sourcebook's abbreviation) when another book prints it. `cunning` marks an animal
        mind (its "intelligence" is Cunning), `confidence` is (Score,
        Points), and `order`, `hierarchy` and `weakness` are a demon's."""
        block = block or {}
        creature = Creature(
            id=self._creature_id(name),
            name=name,
            many=bool(how_many),
            how_many=how_many,
            realm=realm,
            might=might if realm else 0,
            might_form=form if realm else "",
            size=size,
            season=season,
            attacks=list(attacks or []),
            soak=soak,
            fatigue_levels=fatigue_levels,
            powers=list(powers or []),
            vis=list(vis or []),
            equipment=equipment,
            appearance=appearance,
            notes=notes,
            source=f"{sourcebooks.title_of(source or self.source)} {page}",
            detail=FULL,
            cunning=cunning,
            age=age,
            confidence_score=confidence[0] if confidence else None,
            confidence_points=confidence[1] if confidence else 0,
            encumbrance=encumbrance,
            tires=tires,
            can_be_wounded=can_be_wounded,
            order=order,
            hierarchy=hierarchy,
            weakness=weakness,
            secrets=secrets,
        )
        creature.characteristics = replace(
            creature.characteristics, **block.get("characteristics", {})
        )
        creature.virtues_flaws = [
            _virtue_flaw(entry) for entry in block.get("virtues_flaws", [])
        ]
        creature.abilities = [
            _ability(ability, score, specialty)
            for ability, score, specialty in block.get("abilities", [])
        ]
        creature.personality_traits = [
            ScoredTrait(n, s) for n, s in block.get("traits", {}).items()
        ]
        creature.reputations = [
            ScoredTrait(n, s) for n, s in block.get("reputations", {}).items()
        ]
        if place is not None:
            creature.place_id, creature.place_level = place.id, level
        self.saga.creatures.append(creature)
        return creature

    @staticmethod
    def attack(
        name: str, init: int, attack: int | None, defense: int, damage: int | None
    ) -> CreatureAttack:
        """One line of a creature's Combat: its totals as printed (None
        for one the book gives as n/a)."""
        return CreatureAttack(name, init, attack, defense, damage)

    @staticmethod
    def power(
        name: str,
        might_cost: int,
        init: int,
        form: str,
        *,
        rtd: tuple[str, str, str] = ("", "", ""),
        level: int | None = None,
        penetration_bonus: int = 0,
        does: str = "",
    ) -> CreaturePower:
        """One of a creature's Powers: its Might cost, Init and Form, its
        Range, Duration and Target, the level of the effect it matches,
        and what it does, in the pack's own words."""
        reach, duration, target = rtd
        return CreaturePower(
            name,
            might_cost=might_cost,
            init=init,
            form=form,
            range=reach,
            duration=duration,
            target=target,
            level=level,
            penetration_bonus=penetration_bonus,
            description=does,
        )

    @staticmethod
    def effect(
        name: str,
        *,
        kind: str = "spell",
        rule: str = "",
        uses: list[str] | None = None,
        level: int = 0,
        parameters: str = "",
        charges: int = 0,
        notes: str = "",
        tradition: str = "",
    ) -> TraditionEffect:
        """One of a stat block's tradition effects or items, for
        `stats(block={"effects": [...]})`: the casting rule it uses (by
        the tradition's name for it), the Arts or Abilities it uses, its
        level, and its Range, Duration and Target or what it does."""
        return TraditionEffect(
            name=name,
            tradition=tradition,
            kind=kind,
            rule=rule,
            uses=list(uses or []),
            level=level,
            parameters=parameters,
            charges=charges,
            notes=notes,
        )

    @staticmethod
    def bound_being(
        name: str,
        *,
        kind: str,
        creature: Creature | None = None,
        bonus: int = 0,
        applies_to: str = "",
        notes: str = "",
        tradition: str = "",
    ) -> BoundBeing:
        """A being bound to the character, for `stats(block={"bound_beings":
        [...]})`: its bond (the tradition's name for it), the Bestiary
        record it is, and the bonus the bond gives, if any."""
        return BoundBeing(
            name=name,
            tradition=tradition,
            kind=kind,
            creature_id=creature.id if creature is not None else "",
            bonus=bonus,
            applies_to=applies_to,
            notes=notes,
        )

    @staticmethod
    def link(record: Any, kind: str, target: Any, note: str = "") -> Link:
        """A link from `record` to `target` (a saga record), with a note."""
        link = Link(kind=kind, target_id=target.id, note=note)
        record.links.append(link)
        return link

    def stats(
        self, character: Character, block: StatBlock, *, source: str = ""
    ) -> Character:
        """Fill `character` from a stat block the book prints, in the
        book's notation (scores, not xp), and make it a full character.
        `source` is the abbreviation of the book that prints the block,
        when it is not the pack's own: its printing of a spell is taken
        first, and a spell it adds cites it.
        A Virtue or Flaw given by name is matched to the catalog; a spell
        the catalog lacks becomes one of the character's own, at the
        level and Arts the book gives; whatever has no place on the sheet
        (equipment, Twilight Scars, a familiar) goes to its biography."""
        c = character
        c.detail = FULL
        c.characteristics = replace(
            c.characteristics, **block.get("characteristics", {})
        )
        c.aging.aging_points = dict(block.get("aging_points", {}))
        c.background.size = block.get("size", 0)
        c.background.confidence_score, c.background.confidence_points = block.get(
            "confidence", (0, 0)
        )
        score, past = block.get("decrepitude", (0, 0))
        c.aging.decrepitude = score
        c.aging.decrepitude_points = aging.points_for_score(score) + past
        if "apparent_age" in block:
            c.aging.apparent_age = block["apparent_age"]
        warp, warp_points = block.get("warping", (0, 0))
        warping.set_total(c, warping.points_for(warp) + warp_points)
        c.virtues_flaws = [
            _virtue_flaw(entry) for entry in block.get("virtues_flaws", [])
        ]
        c.abilities = [
            _ability(name, score, specialty)
            for name, score, specialty in block.get("abilities", [])
        ]
        spare = block.get("spare_xp", {})
        for ability in c.abilities:
            ability.xp += spare.get(ability.name, 0)
        # The hedge traditions the character belongs to (catalog ids); a
        # block that names none keeps those the sketch gave.
        if "traditions" in block:
            c.traditions = list(block["traditions"])
        # Its traditions' effects and items, and the beings bound to it;
        # one that names no tradition is of the character's first.
        first = c.traditions[0] if c.traditions else ""
        if "effects" in block:
            c.tradition_effects = [
                e if e.tradition else replace(e, tradition=first)
                for e in block["effects"]
            ]
        if "bound_beings" in block:
            c.bound_beings = [
                b if b.tradition else replace(b, tradition=first)
                for b in block["bound_beings"]
            ]
        spare_art = block.get("spare_art_xp", {})
        c.arts = {
            art.lower(): ArtScore(xp=art_xp(score) + spare_art.get(art, 0))
            for art, score in block.get("arts", {}).items()
        }
        if "traits" in block:
            c.personality_traits = [
                ScoredTrait(n, s) for n, s in block["traits"].items()
            ]
        c.reputations = [
            ScoredTrait(n, s) for n, s in block.get("reputations", {}).items()
        ]
        c.spells_known = [
            self._known_spell(c, entry, source or self.source)
            for entry in block.get("spells", [])
        ]
        designs = block.get("spell_designs", {})
        for spell in c.invented_spells:
            design = designs.get(spell.name)
            if design is not None:
                spell.level, spell.range, spell.duration, spell.target = design[:4]
                spell.description = f"{spell.description} ({design[4]})"
        masteries = block.get("masteries", {})
        for (name, *_), known in zip(block.get("spells", []), c.spells_known):
            known.mastery_abilities = [
                MasteryAbility(m) for m in masteries.get(name, ())
            ]
        if block.get("notes"):
            c.description.biography = block["notes"]
        return c

    @staticmethod
    def _known_spell(
        character: Character, entry: tuple[str, str, int | None, int], source: str
    ) -> KnownSpell:
        name, arts, level, mastery = entry
        printings = _catalog_spells().get(_spell_key(name), [])
        found = next(
            (s for s in printings if s.source == source),
            printings[0] if printings else None,
        )
        short = arts.split("(")[0].strip()
        if (
            found is not None
            and source in OWN_PRINTINGS
            and found.source != source
            and (
                (level is not None and found.level not in (None, level))
                or found.technique != ART_LOOKUP[short[:2].lower()]
                or found.form != ART_LOOKUP[short[2:4].lower()]
            )
        ):
            found = None
        if found is None:
            requisites = (
                [a.strip() for a in arts.split("(")[1].rstrip(")").split(",")]
                if "(" in arts
                else []
            )
            spell = Spell(
                id=storage.generate_unique_id(
                    f"spell {name}", [s.id for s in character.invented_spells]
                ),
                name=name,
                technique=ART_LOOKUP[short[:2].lower()],
                form=ART_LOOKUP[short[2:4].lower()],
                level=level,
                requisites=[ART_LOOKUP[r[:2].lower()] for r in requisites],
                source=source,
                description=f"From the stat block in {sourcebooks.title_of(source)}.",
            )
            character.invented_spells.append(spell)
            found = spell
        return KnownSpell(
            found.id, mastery_score=mastery, mastery_xp=ability_xp(mastery)
        )


#: A paragraph saying where a record's vis and books are: what the troupe
#: finds out in play, not what a description says.
HOLDINGS = re.compile(r"(Vis|Books?|Library)\b[^.:\n]{0,24}:")


def _split_holdings(text: str) -> tuple[str, list[str]]:
    lines = text.split("\n")
    held = [line for line in lines if HOLDINGS.match(line)]
    kept = "\n".join(line for line in lines if not HOLDINGS.match(line))
    return re.sub(r"\n{3,}", "\n\n", kept).strip(), held


def hide_holdings(saga: Saga) -> None:
    """Move each record's vis and books out of its public text into its
    secrets."""
    public = (
        (saga.neighbours, "summary"),
        (saga.covenants, "what_matters"),
        (saga.creatures, "notes"),
    )
    for records, name in public:
        for record in records:
            kept, held = _split_holdings(getattr(record, name))
            if held:
                setattr(record, name, kept)
                record.secrets = paragraphs(record.secrets, *held).strip()


#: Books whose stat blocks keep a spell at its printed level and Arts as
#: the magus's own spell, where the catalog's spell of that name differs.
OWN_PRINTINGS = ("TtA", "MoH", "LoH")

#: A stat block as a book prints it, in the book's scores:
#: "characteristics" {name: score}, "aging_points" {name: points} (the
#: book's "(n)" after a score), "size", "confidence", "decrepitude" and
#: "warping" as (score, points), "apparent_age", "virtues_flaws" [name or
#: (name, {param: value}); "Name (Minor)" picks a tier the catalog has
#: both of], "abilities" [(name, score, specialty)], "arts" {art: score},
#: "spare_xp" and "spare_art_xp" {name: xp past the score}, "spell_designs"
#: {spell name: (level, Range, Duration, Target, the working)},
#: "traits" and "reputations" {name: score}, "spells" [(name, "CrIg" or
#: "CrIg(Co)", level, mastery)] (the pack's own book's printing first),
#: "masteries" {spell name: [Mastery Ability names]}, "traditions"
#: [tradition catalog ids], "effects" [Builder.effect(...)],
#: "bound_beings" [Builder.bound_being(...)], "notes" (words).
StatBlock = dict[str, Any]


def _ability(name: str, score: int, specialty: str) -> Ability:
    """An Ability at the score a block prints: a hedge Art or an
    Accelerated Ability (its catalog entry's xp table) is priced on the
    Art table, every other on the Ability table."""
    table = access.ability_xp_table(name)
    return Ability(
        name=name,
        category=access.ability_category(name),
        xp=art_xp(score) if table == "art" else ability_xp(score),
        xp_table=table,
        specialty=specialty or None,
    )


def _spell_key(name: str) -> str:
    return "".join(ch for ch in name.casefold().replace("’", "'") if ch.isalnum())


@cache
def _catalog_spells() -> dict[str, list[Spell]]:
    """The catalog's printings of each spell, by name: books share some
    names, and a pack takes its own book's printing first."""
    found: dict[str, list[Spell]] = {}
    for spell in catalog.load_spell_catalog():
        found.setdefault(_spell_key(spell.name), []).append(spell)
    return found


@cache
def _virtues_by_name() -> dict[str, str]:
    """Each Virtue and Flaw by its name, and by its name and tier
    ("Ambitious (Minor)"), for the names the catalog has at both tiers."""
    entries = catalog.load_virtue_flaw_catalog()
    by_tier = {_spell_key(f"{v.name} ({v.tier})"): v.id for v in entries}
    return by_tier | {_spell_key(v.name): v.id for v in entries}


def _virtue_flaw(entry: str | tuple[str, dict[str, str]]) -> VirtueFlawInstance:
    """A Virtue or Flaw the book names, as the catalog's own; a name the
    catalog lacks fails the build, so a typo can't slip into a pack."""
    name, params = (entry, {}) if isinstance(entry, str) else entry
    vf_id = _virtues_by_name().get(_spell_key(name))
    if vf_id is None:
        raise KeyError(f"No Virtue or Flaw named {name!r} in the catalog")
    return VirtueFlawInstance(vf_id, params=dict(params))


#: The block notation's readers, for stat blocks kept as data (the
#: Bestiary's catalog of the book's creatures).
ability_from_block = _ability
virtue_flaw_from_block = _virtue_flaw
