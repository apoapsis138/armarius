"""Stats for a magus a book describes but prints no stat block for,
generated from a short profile read off the book's paragraph: which
Characteristics and Arts the magus leans to, the Virtues, Flaws and
Abilities the paragraph names, and an age where the book gives none.

The xp is the creation rules' own (rules.creation_xp, creation_later,
creation_magus): 75 xp of native language and 45 more in childhood,
15 a year of later life before apprenticeship, 240 xp and 120 spell
levels in apprenticeship, then 30 points a year past Gauntlet, shared
between Arts, Abilities and spell levels. Points go where the profile's
weights say, one level at a time to whatever buys the most weight for
its cost, so a magus's scores keep the shape of their interests. Spells
come from the catalog, in the Arts the magus favours, each no higher
than their Lab Total; the choice is seeded by the magus's id, so a pack
rebuilds the same.

Pattern: the generator is the Builder's director: it turns a profile
into the StatBlock that Builder.stats already reads, so a generated
magus and a printed one are filled the same way."""

from __future__ import annotations

import random
from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass, field
from functools import cache
from typing import Any

from .. import catalog, sourcebooks
from ..arts import ART_ABBREVIATIONS, ART_LOOKUP, ARTS, FORMS, TECHNIQUES
from ..models import FULL, Character, Spell
from ..packs import INFERRED
from ..rules import creation_access, creation_virtues, warping
from ..rules.creation_later import CHILDHOOD_ENDS, XP_A_YEAR
from ..rules.creation_magus import (
    APPRENTICESHIP_LEVELS,
    APPRENTICESHIP_XP,
    APPRENTICESHIP_YEARS,
    CREATION_AURA,
    POINTS_A_YEAR,
)
from ..rules.xp import ability_xp, art_xp
from .builder import Builder, StatBlock, _catalog_spells, _virtue_flaw

#: The Characteristics in the order a profile's leanings are filled from.
CHARACTERISTICS: tuple[str, ...] = (
    "intelligence",
    "stamina",
    "communication",
    "perception",
    "presence",
    "strength",
    "dexterity",
    "quickness",
)
_SHORT = {name[:3]: name for name in CHARACTERISTICS} | {"qik": "quickness"}
#: What the strong Characteristics get, in order, and the weak ones:
#: +3, +2, +1, +1 cost 11 and -1, -2 give back 4, the 7 points of
#: creation exactly.
STRONG = (3, 2, 1, 1)
WEAK = (-1, -2)

#: Where a magus's points past Gauntlet go: (Arts, Abilities, spells).
SHARES = (0.55, 0.30, 0.15)
#: The age apprenticeship starts when the magus is old enough.
APPRENTICED_AT = 10
LONGEVITY_FROM = 35
#: Warping Points a year under a longevity ritual and the magic round it.
WARPING_A_YEAR = 2

#: Every magus's Abilities, by weight, beside the profile's own.
MAGUS_ABILITIES: dict[str, int] = {
    "Magic Theory": 4,
    "Parma Magica": 4,
    "Penetration": 3,
    "Concentration": 2,
    "Finesse": 2,
    "Dead Language: Latin": 2,
    "Code of Hermes": 2,
    "Magic Lore": 2,
    "Organization Lore: Order of Hermes": 1,
    "Artes Liberales": 1,
    "Awareness": 1,
    "Teaching": 1,
}
#: The Ability each House's free Virtue opens, and its weight.
HOUSE_ABILITIES: dict[str, dict[str, int]] = {
    "house_bjornaer": {"Heartbeast": 4},
    "house_criamon": {"Enigmatic Wisdom": 4},
    "house_merinita": {"Faerie Magic": 4, "Faerie Lore": 2},
    "house_guernicus": {"Code of Hermes": 3, "Folk Ken": 1},
    "house_tremere": {"Leadership": 1},
    "house_flambeau": {"Single Weapon": 1},
    "house_verditius": {"Craft: Goldsmith": 2},
    "house_jerbiton": {"Etiquette": 2, "Charm": 1},
    "house_bonisagus": {"Magic Theory": 2},
    "house_tytalus": {"Guile": 1, "Intrigue": 1},
    "house_mercere": {"Ride": 2, "Area Lore: Rhine Tribunal": 1},
}
#: Childhood's 45 xp, after the native language's 75.
CHILDHOOD = {"Awareness": 15, "Brawl": 15, "Athletics": 15}
#: An apprentice's must-haves, as scores, before the rest of the 240 xp
#: goes to Arts and the profile's Abilities.
APPRENTICE_MINIMUMS = {
    "Dead Language: Latin": 4,
    "Magic Theory": 3,
    "Parma Magica": 1,
    "Artes Liberales": 1,
    "Code of Hermes": 1,
    "Concentration": 1,
}
#: An Ability's specialty when the profile names none.
SPECIALTIES: dict[str, str] = {
    "Magic Theory": "spells",
    "Parma Magica": "Mentem",
    "Concentration": "spell concentration",
    "Code of Hermes": "the Peripheral Code",
    "Magic Lore": "regiones",
    "Organization Lore: Order of Hermes": "the Rhine Tribunal",
    "Artes Liberales": "logic",
    "Awareness": "alertness",
    "Teaching": "apprentices",
    "Athletics": "running",
    "Brawl": "dodging",
    "Heartbeast": "the beast's senses",
    "Enigmatic Wisdom": "the Enigma",
    "Faerie Magic": "glamour",
    "Faerie Lore": "the forest fae",
    "Folk Ken": "magi",
    "Leadership": "covenfolk",
    "Single Weapon": "sword",
    "Craft: Goldsmith": "jewellery",
    "Etiquette": "nobles",
    "Charm": "first impressions",
    "Guile": "lying to magi",
    "Intrigue": "Hermetic politics",
    "Ride": "long journeys",
    "Area Lore: Rhine Tribunal": "covenants",
    "Dead Language: Latin": "Hermetic usage",
    "Philosophiae": "natural philosophy",
    "Infernal Lore": "demons",
    "Dominion Lore": "relics",
    "Bargain": "vis",
    "Profession: Scribe": "copying",
    "Survival": "forests",
    "Animal Ken": "wild beasts",
    "Medicine": "diagnosis",
    "Chirurgy": "wounds",
    "Stealth": "woods",
    "Hunt": "tracking",
    "Carouse": "drinking",
    "Music": "singing",
}
#: The books a generated magus's spells come from: the core book, the
#: Houses of Hermes, the Order's own spell books and the pack's.
SPELL_BOOKS = {"DE", "MoH", "GotF", "HoH:TL", "HoH:S", "HoH:MC", "Covenants"}
#: How far a heavy weight pulls ahead: each Art's weight is raised to this
#: power before points are shared, so a favoured Art leads without
#: leaving the rest at nothing (and the same, gentler, for Abilities).
ART_SPREAD = 0.6
ABILITY_SPREAD = 0.8
#: The highest Art and Ability scores the generator buys, near the best
#: the Rhine's printed archmagi hold.
ART_CAP = 40
ABILITY_CAP = 10
MASTERY_ABILITIES = (
    "Fast Casting",
    "Penetration",
    "Quiet Casting",
    "Still Casting",
    "Multiple Casting",
)
#: The Tribunal each book's magi know, for the Area Lore and the
#: Organization Lore the tables above give as the Rhine's.
TRIBUNALS = {
    "GotF": "Rhine Tribunal",
    "L&L": "Normandy Tribunal",
    "F&F": "Provençal Tribunal",
    "TSE": "Theban Tribunal",
}
#: The language a book's magi learn their Art in, where it is not Latin.
HERMETIC_LANGUAGES = {"TSE": "Classical Greek"}
LATIN = "Dead Language: Latin"
RHINE_LORE = "Area Lore: Rhine Tribunal"

#: The Ability types later life (before apprenticeship) may buy.
_LATER_LIFE = ("General", "Academic", "Martial")
#: The most copies of Affinity with (Art) or Puissant (Art) a magus holds.
ART_VIRTUE_COPIES = 2


@dataclass(frozen=True)
class Profile:
    """What the book's paragraph says of a magus, for the generator.

    `strong` and `weak` name Characteristics by their first three letters
    ("int sta"); the rest fill from CHARACTERISTICS. `arts` weighs Arts
    by their two letters ({"Re": 5, "Im": 5}); unnamed Arts weigh 1.
    `abilities` adds Abilities with weights, or (weight, specialty).
    `virtues` are the Virtues and Flaws the paragraph supports, as the
    Builder takes them; The Gift and the magus's rank are added, and any
    Virtue points the Flaws leave unspent go on the top Arts. `age` is
    used only when the book gives none; `native` is the magus's mother
    tongue; `hermetic` is the language they learnt the Art in, when it
    is not their book's (an incomer to the Theban Tribunal keeps Latin);
    `gifted` is False for an un-Gifted Redcap."""

    strong: str = "int sta"
    weak: str = ""
    arts: Mapping[str, int] = field(default_factory=dict)
    abilities: Mapping[str, int | tuple[int, str]] = field(default_factory=dict)
    virtues: Sequence[str | tuple[str, dict[str, str]]] = ()
    age: int | None = None
    native: str = "High German"
    hermetic: str = ""
    gifted: bool = True
    reputations: Mapping[str, int] = field(default_factory=dict)
    shares: tuple[float, float, float] = SHARES


@dataclass
class _Pool:
    """Scores bought one level at a time: each step goes to whatever buys
    the most weight for its xp."""

    weights: dict[str, float]
    cost: Any  # (name, next score) -> xp
    scores: dict[str, int] = field(default_factory=dict)
    #: The highest score a step may reach.
    cap: int = 99

    def spend(self, xp: float) -> float:
        while True:
            best, best_value, best_cost = None, 0.0, 0.0
            for name, weight in self.weights.items():
                if weight <= 0 or self.scores.get(name, 0) >= self.cap:
                    continue
                step = self.cost(name, self.scores.get(name, 0) + 1)
                if step <= xp and weight / step > best_value:
                    best, best_value, best_cost = name, weight / step, step
            if best is None:
                return xp
            self.scores[best] = self.scores.get(best, 0) + 1
            xp -= best_cost


def _ability_step(name: str, score: int, factor: float = 1.0) -> float:
    return (ability_xp(score) - ability_xp(score - 1)) / factor


def _art_step(score: int, factor: float = 1.0) -> float:
    return (art_xp(score) - art_xp(score - 1)) / factor


def characteristics(profile: Profile, greats: Mapping[str, int]) -> dict[str, int]:
    """Seven points by the profile's leanings, plus each Great copy's
    point."""
    strong = [_SHORT[word[:3].lower()] for word in profile.strong.split()]
    weak = [_SHORT[word[:3].lower()] for word in profile.weak.split()]
    rest = [c for c in CHARACTERISTICS if c not in strong and c not in weak]
    strong = (strong + rest)[: len(STRONG)]
    rest = [c for c in rest if c not in strong]
    weak = (weak + rest[::-1])[: len(WEAK)]
    scores: dict[str, int] = dict.fromkeys(CHARACTERISTICS, 0)
    scores.update(zip(strong, STRONG))
    scores.update(zip(weak, WEAK))
    for name, copies in greats.items():
        scores[name] += copies
    return scores


def rank(summary: str, age: int, source: str = "GotF") -> str:
    """The Rhine rank the paragraph opens with ("Archmage of House...");
    a magus of another Tribunal's book is a plain Hermetic Magus."""
    if source != "GotF":
        return "Hermetic Magus"
    first = summary.split(maxsplit=1)[0].rstrip(",") if summary else ""
    if first.startswith("Archmag"):
        return "Archmage (Rhine Tribunal)"
    if first == "Master":
        return "Master (Rhine Tribunal)"
    if first == "Journeyman" or first == "Newly":
        return "Journeyman (Rhine Tribunal)"
    return "Hermetic Magus"


def _params(entries, name: str, key: str) -> list[str]:
    return [
        e[1][key].lower()
        for e in entries
        if not isinstance(e, str) and e[0] == name and key in e[1]
    ]


def virtues(
    character: Character,
    profile: Profile,
    top_arts: Sequence[str],
    top_abilities: Sequence[str],
    age: int,
    source: str = "GotF",
) -> list[Any]:
    """The Gift, the rank, the House Virtue when the profile leaves it
    out, the profile's own, and Affinities and Puissances on the top Arts
    and Abilities for any points the Flaws leave unspent."""
    house = catalog.load_house_catalog_by_id().get(character.hermetic.house or "")
    entries: list[Any] = []
    if profile.gifted:
        entries.append("The Gift")
    entries.append(rank(character.summary, age, source))
    entries.extend(profile.virtues)
    by_id = _virtue_defs()
    if house and house.virtues and profile.gifted:
        held = {_key(e) for e in entries}
        options = [
            (by_id[o["vf_id"]].name, {k: str(v) for k, v in o["params"].items()})
            for o in house.virtues
        ]
        if not any(_key(o) in held for o in options):
            entries.insert(2, options[0])
    balance = _balance(character, entries)
    if balance < 0:
        raise ValueError(f"{character.name}'s Virtues outweigh the Flaws")
    fillers = [
        *(("Affinity with {art}", "art", a.lower()) for a in top_arts),
        *(("Puissant {art}", "art", a.lower()) for a in top_arts),
        *(("Affinity with {ability}", "ability", a.lower()) for a in top_abilities),
        *(("Puissant {ability}", "ability", a.lower()) for a in top_abilities),
    ]
    for name, key, value in fillers:
        if balance <= 0:
            break
        copies = _params(entries, name, key)
        if value in copies or (key == "art" and len(copies) >= ART_VIRTUE_COPIES):
            continue
        entries.append((name, {key: value}))
        balance -= 1
    return entries


def _key(entry: Any) -> tuple[str, tuple[tuple[str, str], ...]]:
    name, params = (entry, {}) if isinstance(entry, str) else entry
    return name, tuple(sorted((k, str(v).lower()) for k, v in params.items()))


@cache
def _virtue_defs() -> dict[str, Any]:
    return {v.id: v for v in catalog.load_virtue_flaw_catalog()}


def _balance(character: Character, entries: Sequence[Any]) -> int:
    """The Virtue points the Flaws still allow (negative: too many)."""
    probe = Character(id="probe", name="probe", type="magus")
    probe.hermetic.house = character.hermetic.house
    probe.virtues_flaws = [_virtue_flaw(e) for e in entries]
    found = creation_virtues.tally(probe)
    allowed, _ = creation_virtues.virtue_allowance(probe, found.flaw_points)
    if found.flaw_points > creation_virtues.MAX_FLAW_POINTS:
        raise ValueError(f"{character.name} has more than 10 points of Flaws")
    return allowed - found.virtue_points


def _arts_weights(profile: Profile) -> dict[str, float]:
    weights = dict.fromkeys(ARTS, 1.0)
    for short, weight in profile.arts.items():
        weights[ART_LOOKUP[short.lower()]] = float(weight)
    return weights


def _weight(given: int | tuple[int, str]) -> int:
    return given[0] if isinstance(given, tuple) else given


def _factor(entries: Sequence[Any], name: str, key: str, target: str) -> float:
    return 1.5 if target.lower() in _params(entries, name, key) else 1.0


def apply(b: Builder, character: Character, profile: Profile) -> None:
    """Stat a magus the book only sketches: keep the sketch on the
    Builder (a pack lets the user import it instead), fill the stats from
    the profile, and say on the sheet that they are inferred. An age the
    book leaves out is the one assumed, and the sheet says so too."""
    if character.type != "magus" or character.detail == FULL:
        return
    b.sketches[character.id] = deepcopy(character)
    block, age = stat_block(character, profile, b.year, b.source)
    assumed = character.background.year_born is None
    b.stats(character, block)
    if assumed:
        character.background.year_born = b.year - age
    character.description.biography = note(b.source, age if assumed else None)


def note(source: str, assumed_age: int | None = None) -> str:
    """The Biography of a generated magus: whose stats they are not."""
    words = (
        f"{sourcebooks.title_of(source)} prints no stat block for this magus. "
        f"{INFERRED} The storyguide may change them freely."
    )
    if assumed_age is not None:
        words += (
            f" The book gives no age: {assumed_age} is assumed from the magus's rank."
        )
    return words


@dataclass(frozen=True)
class _Local:
    """The book's own Tribunal and Hermetic language, put in place of the
    Rhine's and Latin in the tables above."""

    language: str
    tribunal: str

    def name(self, ability: str) -> str:
        if ability == LATIN:
            return f"Dead Language: {self.language}"
        if ability == RHINE_LORE:
            return f"Area Lore: {self.tribunal}"
        return ability

    def specialty(self, ability: str) -> str:
        if ability == f"Dead Language: {self.language}":
            return SPECIALTIES[LATIN]
        if ability == f"Area Lore: {self.tribunal}":
            return SPECIALTIES[RHINE_LORE]
        found = SPECIALTIES.get(ability, "")
        return f"the {self.tribunal}" if found == "the Rhine Tribunal" else found


def _local(profile: Profile, source: str) -> _Local:
    language = profile.hermetic or HERMETIC_LANGUAGES.get(source, "Latin")
    return _Local(language, TRIBUNALS.get(source, "Rhine Tribunal"))


def _ability_weights(
    character: Character, profile: Profile, ranked: Sequence[str], local: _Local
) -> tuple[dict[str, float], dict[str, str]]:
    """Every magus's Abilities, the House's and the profile's (which
    replace a weight given before), and the profile's specialties."""
    weights: dict[str, float] = {}
    specialties: dict[str, str] = {f"Living Language: {profile.native}": "eloquence"}
    given = [MAGUS_ABILITIES] if profile.gifted else []
    given.append(HOUSE_ABILITIES.get(character.hermetic.house or "", {}))
    for source in given:
        for name, weight in source.items():
            name = local.name(name)
            weights[name] = weights.get(name, 0) + weight
    for name, entry in profile.abilities.items():
        weight, specialty = entry if isinstance(entry, tuple) else (entry, "")
        weights[name] = weight
        if specialty:
            specialties[name] = specialty
    specialties.setdefault("Penetration", next(a for a in ranked if a in FORMS))
    specialties.setdefault("Finesse", next(a for a in ranked if a in TECHNIQUES))
    return weights, specialties


def stat_block(
    character: Character, profile: Profile, year: int, source: str = ""
) -> tuple[StatBlock, int]:
    """The magus's stat block, and the age it was built for."""
    rng = random.Random(character.id)
    born = character.background.year_born
    age = year - born if born is not None else (profile.age or 50)
    art_weights = _arts_weights(profile)
    ranked = sorted(ARTS, key=lambda a: -art_weights[a])
    top_arts = ranked[:4]
    named = sorted(profile.abilities, key=lambda n: -_weight(profile.abilities[n]))
    top_abilities = [*named, "Magic Theory", "Parma Magica", "Penetration"]
    entries = virtues(character, profile, top_arts, top_abilities[:4], age, source)
    greats: dict[str, int] = {}
    for name in _params(entries, "Great {characteristic}", "characteristic"):
        greats[name] = greats.get(name, 0) + 1

    start = max(CHILDHOOD_ENDS, min(APPRENTICED_AT, age - APPRENTICESHIP_YEARS))
    gauntlet = start + APPRENTICESHIP_YEARS
    years_past = max(0, age - gauntlet)
    points = years_past * POINTS_A_YEAR
    arts_share, abilities_share, spells_share = profile.shares
    if not profile.gifted:
        arts_share, abilities_share, spells_share = 0.0, 1.0, 0.0

    local = _local(profile, source)
    ability_weights, specialties = _ability_weights(character, profile, ranked, local)

    def ability_cost(name: str, score: int) -> float:
        return _ability_step(
            name, score, _factor(entries, "Affinity with {ability}", "ability", name)
        )

    def art_cost(art: str, score: int) -> float:
        return _art_step(score, _factor(entries, "Affinity with {art}", "art", art))

    native = f"Living Language: {profile.native}"
    spread = {n: w**ABILITY_SPREAD for n, w in ability_weights.items()}
    abilities = _Pool(spread, ability_cost, {native: 5}, ABILITY_CAP)
    for name, xp in CHILDHOOD.items():
        abilities.scores[name] = max(abilities.scores.get(name, 0), _score(xp))
    later = (start - CHILDHOOD_ENDS) * XP_A_YEAR
    mundane = _Pool(
        {
            n: w
            for n, w in spread.items()
            if creation_access.ability_category(n) in _LATER_LIFE
        },
        ability_cost,
        abilities.scores,
        ABILITY_CAP,
    )
    mundane.spend(later)
    arts = _Pool(
        {a: w**ART_SPREAD for a, w in art_weights.items()}, art_cost, cap=ART_CAP
    )
    spell_levels = _apprenticeship(profile, abilities, arts, local)
    left = arts.spend(points * arts_share)
    left = abilities.spend(points * abilities_share + left)
    spell_levels += points * spells_share + left

    chars = characteristics(profile, greats)
    spells = (
        _spells(
            rng,
            arts.scores,
            art_weights,
            chars["intelligence"],
            abilities.scores,
            spell_levels,
            years_past,
            source,
        )
        if profile.gifted
        else []
    )
    block: StatBlock = {
        "characteristics": chars,
        "confidence": (1 + min(2, years_past // 40), 3 + 2 * min(2, years_past // 40)),
        "virtues_flaws": entries,
        "abilities": [
            (name, score, specialties.get(name, local.specialty(name)))
            for name, score in sorted(abilities.scores.items())
            if score > 0
        ],
        "arts": {art: arts.scores.get(art, 0) for art in ARTS}
        if profile.gifted
        else {},
        "reputations": dict(profile.reputations),
        "spells": [(s.name, _arts(s), s.level, mastery) for s, mastery, _ in spells],
        "masteries": {s.name: list(found) for s, _, found in spells if found},
        **_aging(age, profile.gifted, gauntlet),
    }
    return block, age


def _apprenticeship(
    profile: Profile, abilities: _Pool, arts: _Pool, local: _Local
) -> float:
    """Spend apprenticeship's 240 xp, the must-have Abilities first, and
    return the spell levels it gives (none to an un-Gifted Redcap, whose
    xp all goes on Abilities)."""
    if not profile.gifted:
        abilities.spend(APPRENTICESHIP_XP)
        return 0.0
    xp = float(APPRENTICESHIP_XP)
    for name, score in APPRENTICE_MINIMUMS.items():
        name = local.name(name)
        while abilities.scores.get(name, 0) < score:
            xp -= abilities.cost(name, abilities.scores.get(name, 0) + 1)
            abilities.scores[name] = abilities.scores.get(name, 0) + 1
    arts.spend(xp)
    return float(APPRENTICESHIP_LEVELS)


def _score(xp: int) -> int:
    score = 0
    while ability_xp(score + 1) <= xp:
        score += 1
    return score


def _aging(age: int, gifted: bool, gauntlet: int) -> dict[str, Any]:
    """Decrepitude, Aging Points and Warping for a magus of `age` who took
    a longevity ritual at 35 (or at Gauntlet, if later)."""
    over = max(0, age - LONGEVITY_FROM)
    decrepitude = 0 if age < 70 else 1 if age < 100 else 2 if age < 130 else 3
    total = decrepitude * 2 + over // 20
    order = ("stamina", "strength", "dexterity", "quickness", "perception")
    points: dict[str, int] = {}
    for i in range(total):
        points[order[i % len(order)]] = points.get(order[i % len(order)], 0) + 1
    ritual = max(0, age - max(LONGEVITY_FROM, gauntlet)) if gifted else 0
    warp = ritual * WARPING_A_YEAR
    score = warping.score_for(warp)
    return {
        "aging_points": points,
        "decrepitude": (decrepitude, 0),
        "warping": (score, warp - warping.points_for(score)),
    }


def _arts(spell: Spell) -> str:
    short = ART_ABBREVIATIONS[spell.technique] + ART_ABBREVIATIONS[spell.form]
    if spell.requisites:
        short += "(" + ", ".join(ART_ABBREVIATIONS[r] for r in spell.requisites) + ")"
    return short


@cache
def _catalog(source: str) -> tuple[Spell, ...]:
    """Each formulaic spell of the core books, in the printing the Builder
    will take for the pack's book (its own first), when that printing
    gives a level."""
    found = []
    for printings in _catalog_spells().values():
        spell = next((s for s in printings if s.source == source), printings[0])
        if (
            spell.level
            and spell.source in SPELL_BOOKS
            and spell.technique in TECHNIQUES
            and spell.form in FORMS
        ):
            found.append(spell)
    return tuple(found)


def _spells(
    rng: random.Random,
    arts: Mapping[str, int],
    weights: Mapping[str, float],
    intelligence: int,
    abilities: Mapping[str, int],
    levels: float,
    years_past: int,
    source: str,
) -> list[tuple[Spell, int, tuple[str, ...]]]:
    """Spells to `levels` in total, in the magus's favoured Arts first,
    each within the Lab Total of its lowest Art (aura 3)."""
    theory = abilities.get("Magic Theory", 0)

    def cap(spell: Spell) -> int:
        art = min(arts.get(a, 0) for a in (spell.technique, *spell.requisites))
        form = min(arts.get(a, 0) for a in (spell.form, *spell.requisites))
        return art + form + intelligence + theory + CREATION_AURA

    def liking(spell: Spell) -> float:
        return weights[spell.technique] * weights[spell.form]

    candidates = [s for s in _catalog(source) if s.level and s.level <= cap(s)]
    rng.shuffle(candidates)
    candidates.sort(key=liking, reverse=True)
    chosen: list[Spell] = []
    pairs: set[tuple[str, str]] = set()
    left = levels
    # The best-liked spell of each Art pair first, then round again.
    for _ in range(4):
        for spell in candidates:
            pair = (spell.technique, spell.form)
            level = spell.level or 0
            if spell in chosen or pair in pairs or level > left:
                continue
            if liking(spell) < 2 and len(chosen) >= 6:
                continue
            chosen.append(spell)
            pairs.add(pair)
            left -= level
        pairs.clear()
    chosen.sort(
        key=lambda s: (TECHNIQUES.index(s.technique), FORMS.index(s.form), s.level or 0)
    )
    signature = sorted(chosen, key=lambda s: (-liking(s), -(s.level or 0)))[
        : min(3, years_past // 15)
    ]
    mastery = 1 + min(2, years_past // 40)
    return [
        (
            s,
            mastery if s in signature else 0,
            tuple(rng.sample(MASTERY_ABILITIES, mastery)) if s in signature else (),
        )
        for s in chosen
    ]
