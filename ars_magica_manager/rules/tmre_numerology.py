"""Arithmetic magic: Hermetic Numerology, Hermetic Geometry and Hermetic
Architecture, three Minor Mystery Virtues (The Mysteries Revised Edition,
Chapter Eleven, pp. 91-101). The errata has no correction for these pages
(its p. 62 note on Hermetic Numerology is layout only).

Hermetic Numerology (pp. 91-93):

- The Numerologist's Book: the magus's chosen great work, opened as an
  invested device and attuned at once (a seven-day distraction). A lesser
  book opens its parchment (8 pawns, Magic Theory 4) for a book bonus of
  +4, a greater one the whole book as a compound device (16 pawns, Magic
  Theory 8) for +8. The bonus is at most his Artes Liberales, and only the
  magus who opened and attuned it gains it. Consulted, it adds to Lab
  Totals for Numerology (Rotes included), Hermetic Geometry and Hermetic
  Architecture, and (an extra round, the book in hand) to a Rote's Casting
  Score.
- Rotes: little spells cast with no die and no Fatigue, as if with the
  Mastery abilities Quiet Casting and Still Casting.

      Rote Lab Total     = Technique + Form + Intelligence + Magic Theory
                           + Arithmetic (at most Magic Theory) + book bonus
                           + aura
      Highest Rote level = Rote Lab Total / 5, rounded up
      Rote Casting Score = Stamina + Technique + Form + Arithmetic
                           + book bonus + aura
      Rote Casting Total = Casting Score / 2, rounded up

  The Rote works when its Casting Total at least equals its level, and
  penetrates by Casting Total - level + Penetration bonus. A season's Lab
  Total invents several Rotes of one Technique and Form: each costs twice
  its level in points, or its level from a Lab Text.

Hermetic Geometry (pp. 93-97): +3 to the Casting Score of a spell tracing
a circle or line, and +3 more cast ceremonially in a regular figure (a
circle, a line, a regular room or structure). Line Range (as Sight)
needs Intelligence + Artes Liberales against the Distance Level (at least
9; paces counted as an Ability's experience), a round per 3 points of the
Ease Factor; a failure lands the Ease Factor times the shortfall in paces
away, a botch botches the spell. A perfect shape is Dexterity +
Profession: Scribe against 15 freehand, 6 with posts and string. Arcane
Ring is Ring + 1 magnitude.

Hermetic Architecture (pp. 97-101): a structure too big for a laboratory
is enchanted through identical component devices, one per point of its
Size multiplier, each opened for Material x Size spaces (the extended
Material and Size table: Size 5 a small room up to 10, wood x2, soft stone
x3, hard stone x4). The magus places them by Intelligence + Artes
Liberales (geometry) against 6 + Size (a failure costs a day to a month
to recompute and rework, and he tries again while time allows; a botch a
disaster unnoticed until too late), and
binds them with the Mystery ritual Bind the Mystical Structure (ReVi,
Arcane, Group): at least the highest component effect's level + 5, a
magnitude more for a Structure, two for a Boundary. Investigating a
component halves the Lab Total. Aura enchantments (Creo Vim) raise a
Magic aura by 1 to at most 1 (level 35) up to 9 (level 75).
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from ..arts import ART_ABBREVIATIONS, ART_LOOKUP, FORMS, TECHNIQUES
from ..models import Character, EnchantedDevice, Laboratory, Saga
from . import casting, enchantment, lab, lab_virtues
from . import hybrid_magic as hybrid
from .breakdown import Breakdown, Line
from .casting_virtues import ritual_vis
from .derived import fatigue_penalty, wound_penalty
from .realms import home_aura
from .rounding import round_down, round_up
from .xp import ABILITY_FACTOR, score_from_xp

SOURCE = "The Mysteries Revised Edition, Chapter Eleven: Arithmetic Magic, pp. 91-101"
NUMEROLOGY_SOURCE = "The Mysteries Revised Edition, Hermetic Numerology, pp. 91-93"
ROTE_SOURCE = "The Mysteries Revised Edition, Rotes, pp. 92-93"
GEOMETRY_SOURCE = "The Mysteries Revised Edition, Hermetic Geometry, pp. 93-97"
ARCHITECTURE_SOURCE = "The Mysteries Revised Edition, Hermetic Architecture, pp. 97-101"

NUMEROLOGY = "vf_hermetic_numerology"
GEOMETRY = "vf_hermetic_geometry"
ARCHITECTURE = "vf_hermetic_architecture"

#: The Ability arithmetic, geometry and the rest are Specialties of.
ARTES_LIBERALES = "Artes Liberales"
ARITHMETIC = "arithmetic"
GEOMETRY_SPECIALTY = "geometry"

# -- the Numerologist's Book (pp. 91-92) --------------------------------------

#: An enchanted device's `mystery_device`: a lesser or greater
#: Numerologist's Book, or a component of a Hermetic Architecture
#: structure.
LESSER_BOOK = "numerologist_lesser"
GREATER_BOOK = "numerologist_greater"
COMPONENT = "architecture_component"
MYSTERY_DEVICES: dict[str, str] = {
    LESSER_BOOK: "Lesser Numerologist's Book",
    GREATER_BOOK: "Greater Numerologist's Book",
    COMPONENT: "Hermetic Architecture component",
}
#: Each book: its bonus, the pawns opening it takes and the Magic Theory
#: it needs (p. 92).
BOOK_BONUS = {LESSER_BOOK: 4, GREATER_BOOK: 8}
BOOK_PAWNS = {LESSER_BOOK: 8, GREATER_BOOK: 16}
BOOK_THEORY = {LESSER_BOOK: 4, GREATER_BOOK: 8}
#: Attuning the book as it is opened: a seven-day distraction (p. 92).
ATTUNE_DAYS = 7


def _has(magus: Character, vf_id: str) -> bool:
    return lab_virtues.has(magus, vf_id)


def _specialty(magus: Character) -> str:
    ability = next((a for a in magus.abilities if a.name == ARTES_LIBERALES), None)
    return (ability.specialty or "").casefold() if ability else ""


def artes_liberales(magus: Character) -> int:
    """The magus's Artes Liberales, with any Puissant bonus: the score these
    Mysteries call Arithmetic and Geometry."""
    return sum(lab.ability_score(magus, ARTES_LIBERALES))


def roll_bonus(magus: Character, specialty: str) -> int:
    """Artes Liberales for a roll, +1 when its Specialty is `specialty`
    (a Specialty helps rolls only, DE p. 62)."""
    return artes_liberales(magus) + (1 if _specialty(magus) == specialty else 0)


def numerologist_book(saga: Saga, magus: Character) -> EnchantedDevice | None:
    """The best Numerologist's Book the magus opened and attuned himself
    and holds (only its maker gains its bonus; one consulted at a time),
    or None."""
    if not _has(magus, NUMEROLOGY):
        return None
    books = [
        d
        for d in saga.enchanted_devices
        if d.mystery_device in BOOK_BONUS
        and d.maker_id == magus.id
        and d.holder_id in (magus.id, magus.assigned_lab_id)
        and book_problem(saga, d) is None
    ]
    return max(books, key=lambda d: BOOK_BONUS[d.mystery_device], default=None)


def book_bonus(saga: Saga, magus: Character) -> int:
    """The Numerologist's book bonus: +4 or +8, at most Artes Liberales (0
    without a book)."""
    book = numerologist_book(saga, magus)
    if book is None:
        return 0
    return max(0, min(BOOK_BONUS[book.mystery_device], artes_liberales(magus)))


def book_line(saga: Saga, magus: Character) -> Line | None:
    """The book bonus as a Lab Total's or Casting Score's line (None
    without one)."""
    book = numerologist_book(saga, magus)
    bonus = book_bonus(saga, magus)
    if book is None or not bonus:
        return None
    full = BOOK_BONUS[book.mystery_device]
    capped = " (capped by Artes Liberales)" if bonus < full else ""
    return Line(
        f"Numerologist's Book: {book.name}{capped}",
        amount=bonus,
        source=NUMEROLOGY_SOURCE,
    )


def book_problem(saga: Saga, device: EnchantedDevice) -> str | None:
    """What is wrong with a device marked as a Numerologist's Book: its
    maker needs Hermetic Numerology and the Magic Theory to open it, and it
    must have been opened with the pawns it needs (None: nothing)."""
    kind = device.mystery_device
    if kind not in BOOK_BONUS:
        return None
    maker = saga.character(device.maker_id) if device.maker_id else None
    name = MYSTERY_DEVICES[kind]
    if maker is None:
        return f"A {name} works only for the magus who opened and attuned it."
    if not _has(maker, NUMEROLOGY):
        return f"{maker.name} needs Hermetic Numerology to attune a {name}."
    theory = hybrid.theory(maker)[1]
    if theory < BOOK_THEORY[kind]:
        return (
            f"A {name} needs Magic Theory {BOOK_THEORY[kind]} to open; "
            f"{maker.name} has {theory} (TMRE p. 92)."
        )
    if device.pawns_opened < BOOK_PAWNS[kind]:
        return (
            f"A {name} is opened with {BOOK_PAWNS[kind]} pawns of vis; "
            f"{device.name} has {device.pawns_opened} (TMRE p. 92)."
        )
    return None


def architecture_lines(
    saga: Saga, magus: Character, device: EnchantedDevice
) -> list[Line]:
    """What enchanting a Hermetic Architecture component adds to its Lab
    Total: the Numerologist's book bonus (p. 91)."""
    if device.mystery_device != COMPONENT or not _has(magus, ARCHITECTURE):
        return []
    line = book_line(saga, magus)
    return [line] if line is not None else []


# -- Rotes (pp. 92-93) -------------------------------------------------------

#: A Progress record of a Rote the magus knows: its name, then its Arts
#: and level, "Ignite the Tinder (CrIg 10)".
ROTE_KIND = "rote"
_ROTE_NAME = re.compile(r"^(?P<name>.*) \((?P<arts>[A-Za-z]{4}) (?P<level>\d+)\)$")
#: One Rote typed on a plan: "Name: level", "(text)" after it when it is
#: invented from a Lab Text.
_ROTE_ENTRY = re.compile(
    r"^(?P<name>.*?)\s*:\s*(?P<level>\d+)\s*(?P<text>\(\s*(lab\s+)?text\s*\))?$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Rote:
    name: str
    technique: str
    form: str
    level: int
    from_text: bool = False

    @property
    def arts(self) -> str:
        return ART_ABBREVIATIONS[self.technique] + ART_ABBREVIATIONS[self.form]

    @property
    def record_name(self) -> str:
        return f"{self.name} ({self.arts} {self.level})"


def parse_rotes(text: str, technique: str, form: str) -> list[Rote] | None:
    """The Rotes typed on a plan ("Name: level; Name: level (text)"), all of
    `technique` and `form`; None when one can't be read."""
    found: list[Rote] = []
    for part in re.split(r"[;\n]", text or ""):
        entry = part.strip()
        if not entry:
            continue
        match = _ROTE_ENTRY.match(entry)
        if match is None or not match.group("name").strip():
            return None
        found.append(
            Rote(
                match.group("name").strip(),
                technique,
                form,
                int(match.group("level")),
                from_text=match.group("text") is not None,
            )
        )
    return found


def rotes_known(magus: Character) -> list[Rote]:
    """The Rotes the magus has invented (his finished Rote records)."""
    found: list[Rote] = []
    for record in magus.progress:
        if record.kind != ROTE_KIND or not record.done:
            continue
        match = _ROTE_NAME.match(record.name)
        if match is None:
            continue
        arts = match.group("arts").casefold()
        technique = ART_LOOKUP.get(arts[:2], "")
        form = ART_LOOKUP.get(arts[2:], "")
        if technique in TECHNIQUES and form in FORMS:
            found.append(
                Rote(match.group("name"), technique, form, int(match.group("level")))
            )
    return found


def _arithmetic_line(magus: Character) -> Line:
    theory = hybrid.theory(magus)[1]
    score = artes_liberales(magus)
    capped = min(score, theory)
    label = "Arithmetic (Artes Liberales)" + (
        f" ({score}, capped by Magic Theory)" if capped < score else ""
    )
    return Line(label, amount=capped, source=ROTE_SOURCE)


def rote_lab_total(
    saga: Saga,
    magus: Character,
    technique: str,
    form: str,
    laboratory: Laboratory,
    *,
    book: bool = True,
    days_missed: int = 0,
) -> lab.LabTotal:
    """The Rote Lab Total: the lab's Lab Total for `technique` + `form`
    (inventing spells) with Arithmetic, at most Magic Theory, and the
    Numerologist's book bonus when the `book` is consulted."""
    total = lab.lab_total(
        saga,
        magus,
        technique,
        form,
        laboratory,
        activity="invent_spells",
        days_missed=days_missed,
    )
    extra = [_arithmetic_line(magus)]
    line = book_line(saga, magus) if book else None
    if line is not None:
        extra.append(line)
    return lab.with_lines(total, extra)


def max_rote_level(lab_total: int) -> int:
    """The highest level of Rote a Rote Lab Total designs: a fifth of it,
    rounded up (none below 1)."""
    return max(0, round_up(lab_total / 5))


def rote_points(rote: Rote) -> int:
    """The Lab Total points inventing a Rote takes: twice its level, or its
    level from a Lab Text (p. 93)."""
    return rote.level if rote.from_text else 2 * rote.level


def rotes_problem(lab_total: int, rotes: Sequence[Rote]) -> str | None:
    """Why these Rotes can't all be invented in one season with this Rote
    Lab Total (None: they can)."""
    if not rotes:
        return "Type the Rotes invented: Name: level; Name: level (text)."
    top = max_rote_level(lab_total)
    high = [r for r in rotes if r.level > top or r.level < 1]
    if high:
        names = ", ".join(r.name for r in high)
        return (
            f"A Rote Lab Total of {lab_total} designs Rotes of level 1 to {top}: "
            f"{names} can't be (TMRE p. 92)."
        )
    points = sum(rote_points(r) for r in rotes)
    if points > lab_total:
        return (
            f"These Rotes take {points} points (twice each level, the level "
            f"from a Lab Text); the Rote Lab Total is {lab_total} (TMRE p. 93)."
        )
    return None


def rote_casting_score(
    saga: Saga,
    magus: Character,
    technique: str,
    form: str,
    *,
    aura: int | None = None,
    aura_realm: str = "",
    book: bool = False,
) -> Breakdown:
    """The Rote Casting Score: Stamina + Technique + Form + Arithmetic +
    the aura, + the book bonus when the `book` is consulted (an extra
    round), less Wounds and Fatigue as every total. The aura is the
    magus's home aura unless one is given."""
    if aura is None:
        aura, aura_realm = home_aura(saga, magus)
    lines = [
        Line("Stamina", amount=magus.characteristics.stamina, source=ROTE_SOURCE),
        Line(
            technique, amount=sum(lab.art_score(magus, technique)), source=ROTE_SOURCE
        ),
        Line(form, amount=sum(lab.art_score(magus, form)), source=ROTE_SOURCE),
        Line(
            "Arithmetic (Artes Liberales)",
            amount=artes_liberales(magus),
            source=ROTE_SOURCE,
        ),
    ]
    label, amount = hybrid.aura_label(magus, aura_realm or "Magic", aura, casting=True)
    lines.append(Line(label, amount=amount, source=ROTE_SOURCE))
    wounded = wound_penalty(magus.wounds, magus.virtues_flaws)
    if wounded:
        lines.append(Line("Wounds", amount=wounded, source=casting.SOURCE))
    tired = fatigue_penalty(magus.fatigue_level, magus.virtues_flaws)
    if tired:
        lines.append(Line("Fatigue", amount=tired, source=casting.SOURCE))
    line = book_line(saga, magus) if book else None
    if line is not None:
        lines.append(line)
    return Breakdown(total=sum(x.amount or 0 for x in lines), lines=lines)


def rote_casting_total(score: float) -> int:
    """A Rote's Casting Total: half the Casting Score, rounded up, with no
    die."""
    return round_up(score / 2)


def rote_works(casting_total: int, level: int) -> bool:
    """A Rote is invoked when its Casting Total at least equals its level."""
    return casting_total >= level


def rote_penetration(casting_total: int, level: int, penetration_bonus: int = 0) -> int:
    """A Rote's Penetration Total: Casting Total - level + the Penetration
    bonus (p. 93)."""
    return casting_total - level + penetration_bonus


# -- Hermetic Geometry (pp. 93-97) ---------------------------------------------

#: Casting a spell that traces a circle or line, and one cast ceremonially
#: in a regular figure (cumulative), p. 94.
CIRCLE_BONUS = 3
FIGURE_BONUS = 3
LINE_MINIMUM_EASE = 9
ROUNDS_PER_EASE = 3
#: Drawing a perfect shape: Dexterity + Profession: Scribe (p. 94).
PERFECT_FREEHAND = 15
PERFECT_WITH_TOOLS = 6
#: Arcane Ring Duration: Ring + 1 magnitude (p. 96).
ARCANE_RING_MAGNITUDES = 1


def geometry_bonus(magus: Character, *, traces: bool, regular_figure: bool) -> int:
    """Hermetic Geometry's addition to a Casting Score: +3 for a spell
    tracing a circle or line, +3 more cast ceremonially in a regular figure
    (a circle, line, regular room or structure)."""
    if not _has(magus, GEOMETRY):
        return 0
    return (CIRCLE_BONUS if traces else 0) + (FIGURE_BONUS if regular_figure else 0)


def distance_level(paces: int) -> int:
    """A line's Distance Level: its length in paces counted as experience
    toward an Ability's score (200 paces is level 8), p. 95."""
    return score_from_xp(max(0, paces), ABILITY_FACTOR)


def line_ease(paces: int) -> int:
    """The Ease Factor of a Line Range calculation: the Distance Level, at
    least 9."""
    return max(LINE_MINIMUM_EASE, distance_level(paces))


def line_rounds(ease_factor: int) -> int:
    """The rounds the calculation and its scribing take: one per 3 points of
    Ease Factor or part."""
    return round_up(ease_factor / ROUNDS_PER_EASE)


def line_miss(ease_factor: int, roll_total: int) -> int:
    """How many paces from the point meant a failed (unbotched) Line
    calculation lands: the Ease Factor times the shortfall (0 on a
    success)."""
    return ease_factor * max(0, ease_factor - roll_total)


def perfect_shape_ease(*, with_tools: bool) -> int:
    """Drawing a perfect shape: 6 with posts and string, 15 freehand."""
    return PERFECT_WITH_TOOLS if with_tools else PERFECT_FREEHAND


# -- Hermetic Architecture (pp. 97-101) ---------------------------------------

#: The extended Material and Size table's materials (p. 97).
MATERIALS: dict[str, int] = {"wood": 2, "soft stone": 3, "hard stone": 4}
#: Size multiplier -> what it covers (p. 97).
SIZES: dict[int, str] = {
    5: "huge: a small room, 3 paces by 3",
    6: "a Room (huge x 10)",
    7: "a Structure, 30 paces by 30 (huge x 100... x 1,000)",
    8: "a Boundary, 100 paces by 100 (Structure x 10)",
    9: "Boundary x 10 (Structure x 100)",
    10: "Boundary x 100 (Structure x 1,000)",
}
PLACEMENT_EASE_BASE = 6
#: Recomputing the components' places after a failed placement roll: a
#: day (repositioning posts in a field) to a month (carving new niches),
#: with no limit on the tries but time (p. 98). A month when the plan
#: doesn't say.
REWORK_DAYS_LEAST, REWORK_DAYS_MOST = 1, 30
REWORK_DAYS_DEFAULT = REWORK_DAYS_MOST
#: Bind the Mystical Structure: 5 levels over the highest component effect
#: (p. 98).
BIND_MARGIN = 5
#: Magnitudes the binding ritual adds over its Group Target for each Size
#: multiplier: a Room is a Group's size, a Structure one more, a Boundary
#: two (pp. 98-100); larger ones a magnitude each tenfold.
_BIND_MAGNITUDES = {5: 0, 6: 0, 7: 1, 8: 2, 9: 3, 10: 4}
#: Creo Vim aura guidelines: +1 to at most 1 is level 35, each point of
#: the maximum 5 more, to 9 (p. 100).
AURA_GUIDELINE_BASE = 30
AURA_MAXIMUM = 9


def structure_spaces(material: str, size: int) -> int:
    """The enchantment spaces each component must open: the structure's
    material times its Size multiplier (a ten-floor hard-stone tower: 4 x 7
    = 28)."""
    if material not in MATERIALS:
        raise ValueError(f"No architectural material {material!r}.")
    if size not in SIZES:
        raise ValueError(f"No Size multiplier {size} on the extended table.")
    return MATERIALS[material] * size


def components_needed(size: int) -> int:
    """The identical component devices: one per point of Size multiplier."""
    return size


def placement_ease(size: int) -> int:
    """Placing the components: Intelligence + Artes Liberales (geometry)
    against 6 + Size multiplier."""
    return PLACEMENT_EASE_BASE + size


def bind_level(highest_effect_level: int, size: int) -> int:
    """Bind the Mystical Structure's least level: the highest component
    effect's level + 5, a magnitude more for each step past a Group's size
    (a level 50 tower: 60)."""
    if size not in _BIND_MAGNITUDES:
        raise ValueError(f"No Size multiplier {size} on the extended table.")
    return max(0, highest_effect_level) + BIND_MARGIN + 5 * _BIND_MAGNITUDES[size]


def bind_vis(magus: Character, level: int) -> int | None:
    """The Vim vis the binding ritual takes: a pawn a magnitude, as any
    Ritual (None when the magus can't cast Rituals)."""
    return ritual_vis(magus, casting.magnitude(level))


def bind_casting_score(saga: Saga, magus: Character) -> Breakdown:
    """The binding ritual's Casting Score: a Rego Vim Ritual in the magus's
    home aura."""
    aura, realm = home_aura(saga, magus)
    return casting.casting_score(
        magus, "Rego", "Vim", aura=aura, aura_realm=realm, ritual=True
    )


def investigation_total(lab_total: int) -> int:
    """Investigating one component: the Lab Total halved (rounded down), as
    the whole structure isn't there (p. 99)."""
    return round_down(lab_total / 2)


def aura_guideline(maximum: int) -> int:
    """The Creo Vim level raising a Magic aura by 1 to at most `maximum`
    (1-9): 35 to 75 (p. 100)."""
    if not 1 <= maximum <= AURA_MAXIMUM:
        raise ValueError(
            "An aura is raised to at most 1 to 9 by Hermetic Architecture."
        )
    return AURA_GUIDELINE_BASE + 5 * maximum


def component_problem(
    saga: Saga, device: EnchantedDevice, material: str, size: int
) -> str | None:
    """Why a component can't hold its share of a structure of `material`
    and Size multiplier `size`: its capacity must reach the structure's
    spaces (None: it can, or its capacity isn't known)."""
    needed = structure_spaces(material, size)
    room = enchantment.capacity(saga, device)
    if room is not None and room < needed:
        return (
            f"{device.name} holds {room} pawns; a component of {SIZES[size]} "
            f"of {material} needs {needed} (TMRE p. 98)."
        )
    return None


def reminders(saga: Saga | None, magus: Character) -> list[str]:
    """The casting panel's reminders for these Mysteries (plain text)."""
    found: list[str] = []
    if _has(magus, NUMEROLOGY):
        bonus = book_bonus(saga, magus) if saga is not None else 0
        book = f"; his book adds +{bonus} consulted (an extra round)" if bonus else ""
        known = rotes_known(magus)
        rotes = (
            " Rotes known: "
            + ", ".join(f"{r.name} ({r.arts} {r.level})" for r in known)
            + "."
            if known
            else ""
        )
        found.append(
            "Hermetic Numerology: a Rote is cast with no die or Fatigue, quietly "
            "and still: Casting Total = (Stamina + Technique + Form + Artes "
            f"Liberales + aura) / 2, rounded up{book} (TMRE p. 92)." + rotes
        )
    if _has(magus, ARCHITECTURE):
        found.append(
            "Hermetic Architecture: a structure's components are bound by Bind "
            "the Mystical Structure (ReVi Ritual, the highest effect's level + 5, "
            "+1 magnitude for a Structure, +2 for a Boundary) (TMRE p. 98)."
        )
    return found
