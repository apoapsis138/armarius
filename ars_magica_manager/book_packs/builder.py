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

from dataclasses import replace
from functools import cache
from typing import Any

from .. import catalog, sourcebooks, storage
from ..ahead import ONCE, REPEATS
from ..arms import Arms
from ..arts import ART_LOOKUP
from ..models import (
    Ability,
    ArtScore,
    BodyVis,
    Book,
    BoundBeing,
    CalendarEntry,
    Case,
    Character,
    Covenant,
    CovenantDiaryEntry,
    Creature,
    CreatureAttack,
    CreaturePower,
    KnownSpell,
    Link,
    MasteryAbility,
    Neighbour,
    Ruling,
    Saga,
    ScoredTrait,
    Spell,
    TraditionEffect,
    Tribunal,
    TribunalDiaryEntry,
    VirtueFlawInstance,
)
from ..models.common import SEASONS, SECRETS_HEADING
from ..models.world import FULL, SKETCH
from ..places import PLACE, RUINED
from ..rules import aging, warping
from ..rules import creation_access as access
from ..rules.xp import ability_xp, art_xp
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

    def gild(
        self, tribunal: Tribunal, name: str, dues: str, members: list[Covenant]
    ) -> dict[str, Any]:
        """A Rhine gild: its member covenants are the ones whose magi
        mostly belong to it, as the gilds are kept by covenant."""
        gild = {"name": name, "members": [c.id for c in members], "dues": dues}
        rhine_package.gilds(tribunal).append(gild)
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
            type=type,  # type: ignore[arg-type]
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
        c.arts = {
            art.lower(): ArtScore(xp=art_xp(score))
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
        if found is None:
            requisites = (
                [a.strip() for a in arts.split("(")[1].rstrip(")").split(",")]
                if "(" in arts
                else []
            )
            short = arts.split("(")[0].strip()
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


#: A stat block as a book prints it, in the book's scores:
#: "characteristics" {name: score}, "aging_points" {name: points} (the
#: book's "(n)" after a score), "size", "confidence", "decrepitude" and
#: "warping" as (score, points), "apparent_age", "virtues_flaws" [name or
#: (name, {param: value}); "Name (Minor)" picks a tier the catalog has
#: both of], "abilities" [(name, score, specialty)], "arts" {art: score},
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
