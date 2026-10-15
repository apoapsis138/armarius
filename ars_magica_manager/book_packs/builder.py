"""The Builder a book's module assembles its saga with: one method per
kind of record, each taking the facts a sourcebook gives in plain
arguments and returning the record, so a book's module reads as a list
of what the book says. The records are the app's own (a Tribunal, a
Covenant, a Character, a Neighbour of each kind, a Book), so the pack
is an ordinary export and the sheets show it like anything the user
typed.

Secrets go at the end of a summary or a covenant's notes under a
"Secrets" heading (`secrets()` writes it), where the storyguide finds
them and a player sheet need not show them."""

from __future__ import annotations

from dataclasses import replace
from functools import cache
from typing import Any

from .. import catalog, sourcebooks, storage
from ..arms import Arms
from ..arts import ART_LOOKUP
from ..models import (
    Ability,
    ArtScore,
    Book,
    Case,
    Character,
    Covenant,
    KnownSpell,
    Link,
    MasteryAbility,
    Neighbour,
    Ruling,
    Saga,
    ScoredTrait,
    Spell,
    Tribunal,
    TribunalDiaryEntry,
    VirtueFlawInstance,
)
from ..models.world import FULL, SKETCH
from ..places import PLACE
from ..rules import aging, warping
from ..rules import creation_access as access
from ..rules.xp import ability_xp, art_xp
from ..tribunal_packages import rhine as rhine_package

SECRETS = "Secrets"


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
        self, name: str, year: int = 1220, season: str = "Spring", source: str = ""
    ) -> None:
        #: The book's abbreviation (sourcebooks.SOURCEBOOKS), for the
        #: spells its stat blocks add.
        self.source = source
        self.saga = Saga(
            id=storage.generate_unique_id(name, []),
            name=name,
            current_year=year,
            current_season=season,
        )
        self.year = year

    # -- ids --

    def _covenant_id(self, name: str) -> str:
        return storage.generate_unique_id(name, [c.id for c in self.saga.covenants])

    def _character_id(self, name: str) -> str:
        return storage.generate_unique_id(name, [c.id for c in self.saga.characters])

    def _neighbour_id(self, name: str) -> str:
        return storage.generate_unique_id(name, [n.id for n in self.saga.neighbours])

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

    # -- covenants and their people --

    def covenant(
        self,
        name: str,
        *,
        tribunal: Tribunal,
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
    ) -> Covenant:
        """A covenant of the book's Tribunal, not played: its aura is the
        one typed here, or its place's when it sits in one."""
        covenant = Covenant(
            id=self._covenant_id(name),
            saga_id=self.saga.id,
            name=name,
            notes=notes,
            aura=aura,
            aura_realm=realm,
            tribunal_id=tribunal.id,
            year_founded=founded,
            covenant_season=season,
            detail=detail,
            summary=summary,
            played=False,
            unnamed_magi=unnamed_magi,
            what_matters=what_matters,
            arms=arms.to_dict() if arms else {},
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
    ) -> Character:
        """A magus the book names, as a sketch: House, age as of the
        pack's year, a paragraph, and personality traits where given."""
        character = Character(
            id=self._character_id(name),
            name=name,
            type=type,  # type: ignore[arg-type]
            covenant_id=covenant.id if covenant else None,
            detail=detail,
            summary=summary,
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
        inside: Neighbour | None = None,
        level: int = 0,
        realm: str = "Magic",
        aura: int = 0,
        status: str = "Known",
        known: str = "In the Tribunal",
        tethers: str = "",
        levels: list[dict[str, Any]] | None = None,
        detail: str = SKETCH,
    ) -> Neighbour:
        """A forest, a site or a regio: its surface aura in `realm`, and
        its regio levels as `level(...)` entries, each with its own aura."""
        return self.neighbour(
            PLACE,
            name,
            summary=summary,
            realm=realm,
            place=inside,
            level=level,
            detail=detail,
            details={
                "aura": aura,
                "tethers": tethers,
                "status": status,
                "known": known,
                "levels": list(levels or []),
            },
        )

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
        school: str = "Cathedral school",
        ruler: str = "",
        answers_to: Neighbour | None = None,
        place: Neighbour | None = None,
    ) -> Neighbour:
        return self.neighbour(
            "university",
            name,
            summary=summary,
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
    ) -> Neighbour:
        return self.neighbour(
            "faction",
            name,
            summary=summary,
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
            },
        )

    def threat(
        self,
        name: str,
        *,
        summary: str,
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

    @staticmethod
    def link(record: Any, kind: str, target: Any, note: str = "") -> Link:
        """A link from `record` to `target` (a saga record), with a note."""
        link = Link(kind=kind, target_id=target.id, note=note)
        record.links.append(link)
        return link

    def stats(self, character: Character, block: StatBlock) -> Character:
        """Fill `character` from a stat block the book prints, in the
        book's notation (scores, not xp), and make it a full character.
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
            Ability(
                name=name,
                category=access.ability_category(name),
                xp=ability_xp(score),
                specialty=specialty or None,
            )
            for name, score, specialty in block.get("abilities", [])
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
            self._known_spell(c, entry) for entry in block.get("spells", [])
        ]
        masteries = block.get("masteries", {})
        for (name, *_), known in zip(block.get("spells", []), c.spells_known):
            known.mastery_abilities = [
                MasteryAbility(m) for m in masteries.get(name, ())
            ]
        if block.get("notes"):
            c.description.biography = block["notes"]
        return c

    def _known_spell(
        self, character: Character, entry: tuple[str, str, int | None, int]
    ) -> KnownSpell:
        name, arts, level, mastery = entry
        printings = _catalog_spells().get(_spell_key(name), [])
        found = next(
            (s for s in printings if s.source == self.source),
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
                source=self.source,
                description=f"From the stat block in {sourcebooks.title_of(self.source)}.",
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
#: "masteries" {spell name: [Mastery Ability names]}, "notes" (words).
StatBlock = dict[str, Any]


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
