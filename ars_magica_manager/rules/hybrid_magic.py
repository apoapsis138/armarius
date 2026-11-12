"""Hybrid magic: Hermetic magic that a magus's non-Hermetic magic changes.

A hybrid style is data (a Style) found from what the magus holds; the
Hermetic formulas ask this module what changes:

- Holy Magic (the Ability, or the Virtue that gives it): Holy Magic
  stands in for Magic Theory in the lab; an aura adds in Magic and Divine
  auras, half in Faerie ones, and takes nothing in Infernal ones; no
  Warping from living in a Magic or Divine aura.
- Chthonic Magic (the Virtue, or its Ability): Magic and Infernal auras
  both add; no Warping from living in either.
- Hermetic rites (a Faerie Method and Power): rituals from the faerie
  rite guidelines; a Ritual's aura may count from the Faerie column of
  the realm table when that is better than the Magic one.
- Faerie Magic (House Merinita's Virtue, or its Ability): attuned to
  Magic and Faerie auras, so the full aura adds in both, neither gives
  Warping, and neither adds botch dice (DE p. 236).
- Ars Notoria takes 3 a point off a Divine aura's penalty, after any
  Susceptibility doubles it (RoP:D p. 100; rules.learned_magic).

`attuned` says which realms' auras a character is at home in: the realms
their supernatural powers come from. Nobody gains Warping from living in
such an aura (DE p. 390).

A Ritual adds Method + Power instead of Artes Liberales + Philosophiae
when the magus has a Method and Power of his style's realm (holy for Holy
Magic, unholy for Chthonic Magic, faerie for Hermetic rites); the better
of the two is used, since the Method has to be performed. A magus holding
a Goetic Art may use Rego in its place and Vim in place of the target's
Realm Lore, when they are better.

A holy magus's Lab Total is halved when he works from a Hermetic Lab
Text, and his study total when he reads a Hermetic book on an Art or an
Arcane Ability (halves_hermetic_texts, hermetic_source, halves_study), as
a halving line in the total. A text is holy when its author is a holy
magus of the saga, or when it is marked so.

What the formulas can't apply (Holy Magic's words and gestures, Chthonic Magic's sinful acts,
the faerie rite parameters) is shown as the books word it.

Rules: Hybrid magic.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cache

from .. import catalog
from ..models import Book, Character, Saga
from . import creation_access as access
from . import learned_magic, realm_insight, realms, scores
from .rounding import round_down

FAERIE = "Faerie"
#: A Faerie Virtue or Flaw, by its catalog id (Faerie Blood, Faerie Sight,
#: Familiarity with the Fae...).
_FAERIE = re.compile(r"faerie|_fae$|_fae_")

SOURCE = (
    "Realms of Power: The Divine, Holy Magic, pp. 66-70; Realms of Power: The Infernal, "
    "Chthonic and Goetic Magic, pp. 123-124; Realms of Power: Faerie, Hermetic Rites, "
    "p. 121"
)
HOLY_SOURCE = "Realms of Power: The Divine, Holy Magic, pp. 66-70"
CHTHONIC_SOURCE = "Realms of Power: The Infernal, Chthonic Magic, pp. 123-124"
GOETIC_SOURCE = "Realms of Power: The Infernal, Goetic Magic, p. 124"
FAERIE_MAGIC_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Seven: Hermetic Magic, Merinita "
    "— Faerie Magic, p. 236"
)
ATTUNED_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Ten: Long-Term Events, Living in "
    "Strong Auras, p. 390"
)
RITES_SOURCE = "Realms of Power: Faerie, Hermetic Rites, p. 121"

#: The Goetic Arts Rego may stand in for.
GOETIC_ARTS = ("Summoning", "Ablating", "Binding", "Commanding")
#: The Realm Lores Vim may stand in for in a Goetic Art's total.
REALM_LORES = ("Magic Lore", "Faerie Lore", "Infernal Lore", "Dominion Lore")


@dataclass(frozen=True)
class Style:
    """One way a magus's magic is re-aligned or extended."""

    name: str
    #: The realm of the Methods and Powers his Rituals may add.
    realm: str
    source: str
    #: The Ability that stands in for Magic Theory in the lab ("": none).
    theory: str = ""
    #: Aura realm -> multiple of the aura, where it differs from Hermetic
    #: magic's.
    auras: tuple[tuple[str, float], ...] = ()
    #: Realms whose auras give him no Warping from living in them.
    no_warping: tuple[str, ...] = ()
    #: Realms whose auras add no botch dice to his magic.
    no_botch: tuple[str, ...] = ()
    #: What the formulas don't apply.
    notes: str = ""


HOLY = Style(
    "Holy Magic",
    "Divine",
    HOLY_SOURCE,
    theory="Holy Magic",
    auras=(("Magic", 1), ("Divine", 1), ("Faerie", 0.5), ("Infernal", 0)),
    no_warping=("Magic", "Divine"),
    notes=(
        "Holy Magic replaces Magic Theory; every formulaic spell is "
        "reinvented with it, and Lab Totals are halved when learning from a "
        "Hermetic book or Lab Text. Without Hermetic words and gestures he "
        "casts at -15 unless simple die + Presence + Theology reaches 15 or "
        "he performs a holy Method. Rituals may spend long-term Fatigue as "
        "vis (3 pawns a level, an hour of prayer each). It fails when used "
        "to sin."
    ),
)
CHTHONIC = Style(
    "Chthonic Magic",
    "Infernal",
    CHTHONIC_SOURCE,
    auras=(("Magic", 1), ("Infernal", 1)),
    no_warping=("Magic", "Infernal"),
    notes=(
        "Infernal vis without ill effect; Chthonic Magic may replace Magic "
        "Theory in sinister lab work and adds to the Infernal vis limit. A "
        "sinful act while casting or in the lab adds his lowest Art twice "
        "(three times if already doubled). Active use makes the magic "
        "plainly Infernal and opens the Crossroads, Cursed, Forsaken and "
        "Passion parameters."
    ),
)
RITES = Style(
    "Hermetic rites",
    "Faerie",
    RITES_SOURCE,
    notes=(
        "Rituals may be designed from the faerie rite guidelines (the "
        "storyguide names the Technique and Form); they are not natural and "
        "fade at the end of their Duration. Magic or Faerie vis serves, and "
        "the aura counts from the Faerie or the Magic column."
    ),
)


FAERIE_MAGIC = Style(
    "Faerie Magic",
    "Faerie",
    FAERIE_MAGIC_SOURCE,
    auras=(("Faerie", 1),),
    no_warping=("Magic", "Faerie"),
    no_botch=("Magic", "Faerie"),
    notes=(
        "Attuned to Magic and Faerie auras: the full aura adds in both, "
        "neither gives Warping, and neither adds botch dice. His magic "
        "counts as a fay power, and opens the Mystery's special Ranges, "
        "Durations and Targets."
    ),
)

#: Supernatural Abilities whose realm isn't Magic, the realm most come
#: from (DE p. 411).
ABILITY_REALMS = {"Sense Holiness and Unholiness": "Divine"}


def _ids(character: Character) -> set[str]:
    return {vf.vf_id for vf in character.virtues_flaws}


def _holds(character: Character, name: str) -> bool:
    return any(a.name == name for a in character.abilities)


def ability(character: Character, name: str) -> int:
    """An Ability's score with its fixed bonus (Puissant), 0 if absent."""
    found = next((a for a in character.abilities if a.name == name), None)
    if found is None:
        return 0
    return found.level + scores.ability_bonus(character.virtues_flaws, name)[0]


def art(character: Character, name: str) -> int:
    """A Hermetic Art's score with its fixed bonus."""
    found = character.arts.get(name.lower())
    level = found.level if found else 0
    return level + scores.art_bonus(character.virtues_flaws, name)[0]


@cache
def methods_and_powers(realm: str) -> tuple[frozenset[str], frozenset[str]]:
    """The Methods and Powers of a realm: the Techniques and Forms of the
    Method-and-Power castings of that realm's traditions."""
    methods: set[str] = set()
    powers: set[str] = set()
    for t in catalog.load_tradition_catalog():
        if t.realm != realm:
            continue
        for rule in t.casting:
            if rule.kind == "art_pair" and rule.techniques and rule.forms:
                methods.update(rule.techniques)
                powers.update(rule.forms)
    return frozenset(methods), frozenset(powers)


def _has_pair(character: Character, realm: str) -> bool:
    methods, powers = methods_and_powers(realm)
    return any(_holds(character, m) for m in methods) and any(
        _holds(character, p) for p in powers
    )


def styles(character: Character) -> list[Style]:
    """The hybrid styles a magus works in (none for anyone else)."""
    if character.type != "magus":
        return []
    ids = _ids(character)
    found = []
    if "vf_holy_magic" in ids or _holds(character, "Holy Magic"):
        found.append(HOLY)
    if "vf_chthonic_magic" in ids or _holds(character, "Chthonic Magic"):
        found.append(CHTHONIC)
    if "vf_faerie_magic" in ids or _holds(character, "Faerie Magic"):
        found.append(FAERIE_MAGIC)
    if _has_pair(character, "Faerie"):
        found.append(RITES)
    return found


# ---------------------------------------------------------------------------
# What changes in the Hermetic formulas


def halves_hermetic_texts(magus: Character) -> bool:
    """Whether his Lab Totals are halved when he learns from a Hermetic
    Lab Text: a holy magus's are, always (RoP: The Divine p. 67)."""
    return HOLY in styles(magus)


def any_holy_magus(saga: Saga) -> bool:
    """Whether any magus of the saga practises Holy Magic."""
    return any(HOLY in styles(c) for c in saga.characters if c.type == "magus")


def hermetic_source(saga: Saga, book: Book) -> bool:
    """Whether a book or Lab Text is Hermetic, which halves what a holy
    magus learns from it (RoP: The Divine p. 67): it is, unless it is
    marked holy or its author is a holy magus of the saga."""
    if book.holy:
        return False
    author = saga.character(book.author_id)
    return author is None or HOLY not in styles(author)


def halves_study(magus: Character, book: Book | None, hermetic: bool) -> bool:
    """Whether a season reading `book` is halved: a holy magus learning
    magic (an Art, or an Arcane Ability) from a Hermetic book (RoP: The
    Divine p. 67, "Hermetic study totals halved")."""
    if book is None or not hermetic or not halves_hermetic_texts(magus):
        return False
    if book.type == "Art Summa" or book.subject_kind == "Art":
        return True
    return bool(book.ability) and access.ability_category(book.ability) == "Arcane"


def chthonic_theory(magus: Character) -> int:
    """How much more a chthonic magus's Chthonic Magic is than his Magic
    Theory, when it stands in for it in lab work on a dark or sinister
    effect (RoP: The Infernal p. 123); 0 for anyone else."""
    if CHTHONIC not in styles(magus):
        return 0
    return max(0, ability(magus, "Chthonic Magic") - ability(magus, "Magic Theory"))


def infernal_vis_limit(magus: Character) -> int:
    """What a chthonic magus adds, as Chthonic Magic, to the pawns of
    Infernal vis he may use at once (RoP: The Infernal p. 123)."""
    return ability(magus, "Chthonic Magic") if CHTHONIC in styles(magus) else 0


def ignores_infernal_vis(magus: Character | None) -> bool:
    """Whether Infernal vis carries no extra peril for him: a chthonic
    magus uses it without its ill effects (RoP: The Infernal p. 123)."""
    return magus is not None and CHTHONIC in styles(magus)


def theory(magus: Character) -> tuple[str, int]:
    """The Ability his lab work uses for Magic Theory, and its score."""
    for style in styles(magus):
        if style.theory:
            return f"{style.theory} (for Magic Theory)", ability(magus, style.theory)
    return "Magic Theory", ability(magus, "Magic Theory")


def aura_modifier(
    magus: Character, aura_realm: str, aura: int, *, casting: bool = False
) -> tuple[int, str]:
    """What an aura adds to his Hermetic magic, and the style that changes
    it ("" when none does). With several, the best applies. Under True
    Understanding of the Realms a penalty is worked from the aura less his
    Lore of its realm; a bonus keeps the whole aura (Legends of Hermes p.
    15). Ars Notoria eases a Divine aura's penalty only on `casting` (RoP:
    The Divine p. 100), not on Lab Totals or Penetration."""
    best, why = _aura_modifier(magus, aura_realm, aura, casting=casting)
    lessened = realm_insight.effective_aura(magus, aura_realm, aura)
    if best < 0 and lessened < aura:
        found, _ = _aura_modifier(magus, aura_realm, lessened, casting=casting)
        if found > best:
            best, why = found, "True Understanding of the Realms"
    return best, why


def _aura_modifier(
    magus: Character, aura_realm: str, aura: int, *, casting: bool = False
) -> tuple[int, str]:
    best = realms.aura_modifier(realms.HERMETIC, aura_realm, aura)
    why = ""
    for style in styles(magus):
        for realm, multiple in style.auras:
            if realm == aura_realm:
                amount = round_down(multiple * aura)
                if amount > best:
                    best, why = amount, style.name
    if aura_realm == DIVINE and best < 0 and divine_susceptible(magus):
        best, why = 2 * best, "Susceptibility to Divine Power"
    if casting and aura_realm == DIVINE and best < 0:
        # Ars Notoria takes 3 a point off the penalty on casting other
        # magic in a Divine aura (RoP: The Divine p. 100).
        relieved = learned_magic.divine_aura_relief(magus, best)
        if relieved > best:
            why = f"{why}, Ars Notoria" if why else "Ars Notoria"
            best = relieved
    return best, why


DIVINE = "Divine"
#: Twice a Divine aura's penalties to his magic (DE p. 146).
DIVINE_SUSCEPTIBILITY = "vf_susceptibility_to_divine_power"


def divine_susceptible(magus: Character) -> bool:
    return any(vf.vf_id == DIVINE_SUSCEPTIBILITY for vf in magus.virtues_flaws)


def aura_label(
    magus: Character,
    aura_realm: str,
    aura: int,
    *,
    ritual: bool = False,
    casting: bool = False,
) -> tuple[str, int]:
    """The aura line of a Casting Score or Lab Total: its label and amount.
    A Ritual of a magus who works Hermetic rites may count the aura from the
    Faerie column instead of the Magic one, when that is better (RoP:
    Faerie p. 121). `casting` marks a Casting Score, the only total Ars
    Notoria eases (RoP: The Divine p. 100)."""
    amount, why = aura_modifier(magus, aura_realm, aura, casting=casting)
    if ritual and RITES in styles(magus):
        faerie = realms.aura_modifier(FAERIE, aura_realm, aura)
        if faerie > amount:
            amount, why = faerie, "Hermetic rites, the Faerie column"
    label = f"Aura ({aura_realm} {aura})"
    return (f"{label}, {why}" if why else label), amount


def attuned(character: Character) -> frozenset[str]:
    """The realms whose auras the character is at home in: those their
    supernatural powers come from. Magic for anyone opened to the Hermetic
    Arts or holding a supernatural Ability (most are Magical); a hybrid
    style's realms; each hedge tradition's realm; Magic and Faerie for
    Yatu Magic (The Cradle and the Crescent pp. 30-31)."""
    found: set[str] = set()
    if character.type == "magus" or any(a.xp > 0 for a in character.arts.values()):
        found.add(realms.HERMETIC)
    for style in styles(character):
        found.update(style.no_warping)
    if realms.YATU_MAGIC in _ids(character):
        found.update((realms.HERMETIC, realms.FAERIE))
    for ability_ in character.abilities:
        if ability_.level > 0 and _supernatural(ability_.name):
            found.add(ABILITY_REALMS.get(ability_.name, realms.HERMETIC))
    traditions = catalog.load_tradition_catalog_by_id()
    for tradition_id in character.traditions:
        tradition = traditions.get(tradition_id)
        if tradition is not None and tradition.realm:
            found.add(tradition.realm)
    # A Faerie Virtue or Flaw: no Warping from a Faerie aura (Realms of
    # Power: Faerie p. 111), read from the Virtue's own name.
    if any(_FAERIE.search(vf.vf_id) for vf in character.virtues_flaws):
        found.add(FAERIE)
    return frozenset(found)


@cache
def _supernatural_names() -> frozenset[str]:
    return frozenset(
        a.name
        for a in catalog.load_ability_catalog()
        if a.category == "Supernatural" and a not in catalog.saga_abilities()
    )


def _supernatural(name: str) -> bool:
    """Whether `name` is a Supernatural Ability: the catalog's (cached), or
    one of the saga in use's own."""
    return name in _supernatural_names() or any(
        a.name == name and a.category == "Supernatural"
        for a in catalog.saga_abilities()
    )


def warps_from_aura(character: Character, aura_realm: str) -> bool:
    """Whether living in an aura of this realm gives the character Warping
    Points: not if their supernatural powers come from its realm (DE p.
    390)."""
    return aura_realm not in attuned(character)


def foreign_botch_dice(
    magus: Character, aura_realm: str, aura: int, *, in_regio: bool = False
) -> int:
    """The extra botch dice an aura adds to his Hermetic magic: one a point
    of a foreign aura, two in a foreign regio level (DE p. 411); none in an
    aura a style attunes him to; fewer by his Lore of its realm under True
    Understanding of the Realms (Legends of Hermes p. 15)."""
    if any(aura_realm in s.no_botch for s in styles(magus)):
        return 0
    aura = realm_insight.effective_aura(magus, aura_realm, aura)
    dice = realms.extra_botch_dice(realms.HERMETIC, aura_realm, aura, in_regio=in_regio)
    # Susceptibility to Divine Power doubles them in a Divine aura (DE p. 146).
    return 2 * dice if aura_realm == DIVINE and divine_susceptible(magus) else dice


@dataclass(frozen=True)
class RitualPair:
    method: str
    power: str
    total: int
    style: Style


def ritual_pair(magus: Character) -> RitualPair | None:
    """His best Method + Power for a Ritual, among his styles' realms."""
    best: RitualPair | None = None
    for style in styles(magus):
        methods, powers = methods_and_powers(style.realm)
        held_m = [m for m in sorted(methods) if _holds(magus, m)]
        held_p = [p for p in sorted(powers) if _holds(magus, p)]
        if not held_m or not held_p:
            continue
        m = max(held_m, key=lambda n: ability(magus, n))
        p = max(held_p, key=lambda n: ability(magus, n))
        total = ability(magus, m) + ability(magus, p)
        if best is None or total > best.total:
            best = RitualPair(m, p, total, style)
    return best


def goetic_substitute(character: Character, name: str) -> tuple[str, int] | None:
    """Rego standing in for a Goetic Art, or Vim for a Realm Lore, when a
    magus holding a Goetic Art scores better with it: its label and score."""
    if character.type != "magus":
        return None
    if name in GOETIC_ARTS:
        own, rego = ability(character, name), art(character, "Rego")
        return (f"Rego (for {name})", rego) if rego > own else None
    if name in REALM_LORES and any(_holds(character, g) for g in GOETIC_ARTS):
        own, vim = ability(character, name), art(character, "Vim")
        return (f"Vim (for {name})", vim) if vim > own else None
    return None


def summary(magus: Character) -> list[str]:
    """A line for each style, for the sheet: what it changes."""
    lines = []
    for style in styles(magus):
        lines.append(f"{style.name}: {style.notes}")
    pair = ritual_pair(magus)
    if pair is not None:
        lines.append(
            f"Rituals may add {pair.method} + {pair.power} ({pair.total}) "
            f"instead of Artes Liberales + Philosophiae ({pair.style.name})."
        )
    if magus.type == "magus" and any(_holds(magus, g) for g in GOETIC_ARTS):
        lines.append(
            "Goetic magic: Rego may stand in for a Goetic Art and Vim for the "
            "Realm Lore; a Summoner may bond a spirit as familiar with a "
            "Goetic Art for the Technique."
        )
    return lines
