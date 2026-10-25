"""Study totals: Source Quality by source, the Advancement
Total and the xp a season gives.

    Advancement Total = Source Quality + Virtue bonuses - Flaw penalties
    Advancement Total x Virtues such as Linguist (x1.25, round up) or
                        Savantism (x0.5, round down)
    xp gained         = Advancement Total, then x Affinity (x1.5, round up),
                        and never past the source's Gain Limit

Source Quality: exposure 2; adventure 5-10 (the storyguide's); practice 4;
training the master's score + 3 (limit: his score); teaching the teacher's
Communication + Teaching + 3, +6 for one student, +3 for two (limit: his
score); a summa its Quality (limit: its Level); a tractatus its Quality;
raw vis a stress die + the aura's modifier, using ceil(Art / 5) pawns.
Each full month lost cuts the total by a third, the rest rounded up.

The Gift (DE pp. 204-205) takes 3 (6 for the Blatant Gift, none for the
Gentle Gift) off the Source Quality of a season being taught or trained,
whichever side is Gifted, when the other side is bothered by it: not when
the other has a Parma Magica, nor when the other is an unGifted
covenant-mate of a magus of the home covenant, whom covenfolk grow used to
(DE p. 186). Where both sides' Gifts bother the other, the larger counts.

No screen uses training_quality() yet: it is a rule for a screen still to
come, and only the tests call it.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from .. import book_kinds, catalog
from ..models import Book, Character
from . import animal_grogs, effects, lab_virtues, scores, xp
from . import creation_access as access
from .breakdown import Line
from .derived import wound_penalty
from .lab import ability_score
from .rounding import round_down, round_up

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Advancement, pp. "
    "375-379"
)
AFFINITY_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Four: Virtues and Flaws, Affinity with Art "
    "(x1.5, round up), p. 69"
)

EXPOSURE = 2
PRACTICE = 4
#: The Wound Penalty at which a season's study is halved (DE p. 405).
WOUNDED_STUDY = -3
WOUND_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 11: Combat and Injuries, Activities "
    "While Injured, p. 405"
)
#: The study kind of one subject's share of an Adventure, whose Virtues
#: (Independent Study's +3) were added to the season's Source Quality before
#: it was split (DE pp. 86, 377).
SPLIT_ADVENTURE = "adventure_share"


SUPERNATURAL_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long-Term Events, Learning "
    "Supernatural Abilities, p. 383"
)
#: The experience a first season in a Supernatural Ability must give (a
#: score of 1).
SUPERNATURAL_FIRST_XP = 5
#: What opened Arts take off at least (or the Arts' scores, if more).
OPENED_ARTS_PENALTY = 15


def supernatural_ability(name: str) -> bool:
    return any(
        a.category == "Supernatural" and a.name == name
        for a in catalog.load_ability_catalog()
    )


def learning_supernatural(student: Character, name: str) -> bool:
    """Whether `name` is a Supernatural Ability the student is learning
    for the first time (no experience in it yet)."""
    return supernatural_ability(name) and not any(
        a.name == name and a.xp > 0 for a in student.abilities
    )


def gifted(character: Character) -> bool:
    return character.type == "magus" or any(
        vf.vf_id in catalog.GIFT_IDS for vf in character.virtues_flaws
    )


GIFT_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Seven: Hermetic Magic, The Gift, "
    "pp. 204-205; Parma Magica, p. 169; Familiarity, p. 186"
)
GENTLE_GIFT = "vf_gentle_gift"
BLATANT_GIFT = "vf_blatant_gift"
PARMA_MAGICA = "Parma Magica"


def gift_social_penalty(character: Character) -> int:
    """What the character's Gift takes off social rolls and totals: 3, 6
    for the Blatant Gift, none for the Gentle Gift or no Gift (DE p. 204)."""
    ids = {vf.vf_id for vf in character.virtues_flaws}
    if GENTLE_GIFT in ids:
        return 0
    if BLATANT_GIFT in ids:
        return 6
    return 3 if gifted(character) else 0


def has_parma(character: Character) -> bool:
    """Whether a Parma Magica keeps others' Gifts from bothering the
    character: any character it protects is unaffected by the social
    penalties of other people's Gifts (DE p. 169)."""
    return ability_score(character, PARMA_MAGICA)[0] > 0


def gift_bothers(gifted_one: Character, other: Character) -> int:
    """What `gifted_one`'s Gift costs a season with `other`: none if the
    other has a Parma Magica (DE p. 169) or is an unGifted covenant-mate
    of a magus (covenfolk grow used to their own magi, DE p. 186). A
    protected Gifted character's Gift still bothers the unprotected."""
    penalty = gift_social_penalty(gifted_one)
    if not penalty or other.id == gifted_one.id or has_parma(other):
        return 0
    familiar = (
        gifted_one.type == "magus"
        and gifted_one.covenant_id is not None
        and other.covenant_id == gifted_one.covenant_id
        and not gifted(other)
    )
    return 0 if familiar else penalty


def gift_lines(teacher: Character, student: Character) -> list[Line]:
    """The Gift's lines on a season being taught or trained, as Source
    Quality adjustments: each side's Gift that bothers the other, so two
    unprotected Gifted characters both pay (DE pp. 169, 204)."""
    lines: list[Line] = []
    for whose, other in ((teacher, student), (student, teacher)):
        amount = gift_bothers(whose, other)
        if amount:
            gift = "Blatant Gift" if amount == 6 else "The Gift"
            lines.append(
                Line(f"{gift} ({whose.name})", amount=-amount, source=GIFT_SOURCE)
            )
    return lines


def supernatural_penalty(student: Character, name: str) -> int:
    """What a first season learning a Supernatural Ability takes off the
    Source Quality: the student's scores in his other Supernatural
    Abilities, and with his Arts opened, 15 or the sum of his Arts if more
    (DE p. 383)."""
    others = sum(
        a.level
        for a in student.abilities
        if a.name != name and supernatural_ability(a.name)
    )
    if student.type == "magus" or student.arts:
        arts = sum(art.level for art in student.arts.values())
        others += max(OPENED_ARTS_PENALTY, arts)
    return others


def season_bonus(student: Character, activity: str) -> int:
    """What the student's Virtues add to a season's Source Quality for
    `activity` (Independent Study: +3 to an Adventure)."""
    return int(
        effects.amount_total(
            effects.collect(
                [scores.character_source(student.virtues_flaws)],
                "study_total",
                activity=activity,
            )
        )
    )


def teacher_bonus(teacher: Character) -> int:
    """What the teacher's or master's Virtues add to the Source Quality of
    anyone who studies with him: Good Teacher +5 (DE p. 83)."""
    return int(
        effects.amount_total(
            effects.collect(
                [scores.character_source(teacher.virtues_flaws)],
                "teaching_source_quality",
            )
        )
    )


def training_quality(master: Character, ability: str) -> int:
    """A master's training: his score + 3, plus Virtues such as Good
    Teacher (+5)."""
    return sum(ability_score(master, ability)) + 3 + teacher_bonus(master)


def teaching_quality(teacher: Character, students: int = 1) -> int:
    """A teacher's Source Quality: Communication + Teaching + 3, +6 with one
    student, +3 with two, plus Virtues such as Good Teacher (+5)."""
    bonus = {1: 6, 2: 3}.get(students, 0)
    extra = teacher_bonus(teacher)
    return (
        teacher.characteristics.communication
        + sum(ability_score(teacher, "Teaching"))
        + 3
        + bonus
        + int(extra)
    )


def max_students(teacher: Character) -> int:
    """Teaching x 5 students at once (1 without Teaching)."""
    return max(1, 5 * sum(ability_score(teacher, "Teaching")))


def vis_pawns(art_score: int) -> int:
    """Pawns a season of vis study consumes: ceil(Art / 5), at least 1."""
    return max(1, round_up(art_score / 5))


def season_vis_pawns(student: Character, art_score: int) -> int:
    """The pawns `student` uses in a season of vis study: vis_pawns, a
    third more with Waster of Vis (a quarter of those used is wasted)."""
    pawns = vis_pawns(art_score)
    if lab_virtues.has(student, lab_virtues.WASTER):
        return lab_virtues.with_waste(pawns)
    return pawns


def after_distraction(total: int, months_lost: int) -> int:
    """What's left after full months lost: a third less per month, the
    remainder rounded up (16, one month lost -> 11)."""
    months = max(0, min(months_lost, 3))
    return round_up(total * (3 - months) / 3)


@dataclass
class StudyResult:
    """A season's study: the Advancement Total, the xp it gives, and why."""

    advancement_total: int
    xp: int
    lines: list[Line] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


NEPHILIM = "vf_blood_of_the_nephilim"
NEPHILIM_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Four: Blood of the Nephilim, p. 72"
)
#: The least a season's Advancement Total falls to for Blood of the
#: Nephilim.
NEPHILIM_FLOOR = 1


def nephilim_penalty(student: Character, age: int | None) -> int:
    """What Blood of the Nephilim takes from every Advancement Total once
    the character has a Decrepitude Point: age / 10, rounded down (DE p.
    72); 0 for anyone else, or with the age unknown."""
    if age is None or student.aging.decrepitude_points <= 0:
        return 0
    if not any(vf.vf_id == NEPHILIM for vf in student.virtues_flaws):
        return 0
    return round_down(age / 10)


def season_of_study(
    student: Character,
    subject: str,
    source_quality: int,
    *,
    activity: str,
    is_art: bool,
    gain_limit: int | None = None,
    months_lost: int = 0,
    mastery: bool = False,
    bonuses: Sequence[Line] = (),
    age: int | None = None,
) -> StudyResult:
    """One season studying `subject` (an Art or Ability name, or a spell's
    id for its Mastery, `mastery`) from a source of `source_quality`, for
    `activity` (a study_total activity); `bonuses` add to the Source
    Quality (Study Bonus's +2); `age`, when known, is read by Blood of the
    Nephilim. An animal grog learns a human Language at
    its own Source Quality, and never raises its kind's Language
    (rules.animal_grogs)."""
    if not is_art and animal_grogs.own_language(student, subject):
        line = Line("An animal's own Language", amount=0, source=animal_grogs.SOURCE)
        return StudyResult(
            advancement_total=0,
            xp=0,
            lines=[line],
            notes=[f"{subject} stays at {animal_grogs.LANGUAGE_SCORE}."],
        )
    own = None if is_art else animal_grogs.language_quality(student, subject)
    if own is not None:
        lines = [
            Line(
                "Source Quality (an animal: 4 + Cunning)",
                amount=own,
                source=animal_grogs.LANGUAGE_SOURCE,
            )
        ]
    else:
        lines = [Line("Source Quality", amount=source_quality, source=SOURCE)]
    lines += bonuses
    source = scores.character_source(student.virtues_flaws)
    for effect in effects.collect([source], "study_total", activity=activity):
        lines.append(
            Line(
                effect.entry.name,
                amount=effect.amount or 0,
                source="character",
            )
        )
    total = max(0, int(sum(line.amount or 0 for line in lines)))
    if activity in ("teaching", "reading"):
        total = max(total, 1)  # Poor Student can't take it below 1
    slowed = nephilim_penalty(student, age)
    if slowed and total > NEPHILIM_FLOOR:
        lowered = max(NEPHILIM_FLOOR, total - slowed)
        lines.append(
            Line(
                "Blood of the Nephilim (age / 10)",
                amount=lowered - total,
                source=NEPHILIM_SOURCE,
            )
        )
        total = lowered
    notes: list[str] = []
    if months_lost:
        reduced = after_distraction(total, months_lost)
        lines.append(
            Line(f"{months_lost} month(s) lost", amount=reduced - total, source=SOURCE)
        )
        total = reduced
    if wound_penalty(student.wounds, student.virtues_flaws) <= WOUNDED_STUDY:
        # Wounded at -3 to -5: the Advancement Total halved, before
        # Affinity and the Gain Limit (DE p. 405).
        halved = round_down(total / 2)
        lines.append(
            Line("Wounded (-3 to -5)", amount=halved - total, source=WOUND_SOURCE)
        )
        total = halved
    total = _multiplied(
        source, total, lines, f"Mastery: {subject}" if mastery else subject
    )
    gained: float = total
    kind = "art_xp_gain" if is_art else "ability_xp_gain"
    for effect in effects.collect([source], kind, target=subject):
        if effect.target is not None and effect.modifier.multiplier:
            gained *= effect.modifier.multiplier
            lines.append(
                Line(
                    effect.entry.name,
                    multiplier=effect.modifier.multiplier,
                    source=AFFINITY_SOURCE,
                )
            )
    gained_xp = round_up(gained)
    if gain_limit is not None:
        factor = xp.ART_FACTOR if is_art else access.ability_factor(subject)
        current = _current_xp(student, subject, is_art)
        ceiling = xp.xp_for_score(gain_limit, factor)
        room = max(0, ceiling - current)
        if gained_xp > room:
            notes.append(
                f"Capped at score {gain_limit}: {room} xp of {gained_xp} count."
            )
            gained_xp = room
    return StudyResult(advancement_total=total, xp=gained_xp, lines=lines, notes=notes)


def _multiplied(
    source: effects.EffectSource, total: int, lines: list[Line], target: str
) -> int:
    """The Advancement Total with its advancement_total multipliers: all of
    them multiply together, then a total raised rounds up (Linguist: "a
    quarter, rounded up") and one lowered rounds down (the default)."""
    factor = 1.0
    for effect in effects.collect([source], "advancement_total", target=target):
        if effect.modifier.multiplier is None:
            continue
        factor *= effect.modifier.multiplier
        lines.append(
            Line(
                effect.entry.name,
                multiplier=effect.modifier.multiplier,
                source="character",
            )
        )
    if factor == 1:
        return total
    return round_up(total * factor) if factor > 1 else round_down(total * factor)


def _current_xp(student: Character, subject: str, is_art: bool) -> int:
    if is_art:
        score = student.arts.get(subject.lower())
        return score.xp if score else 0
    ability = next((a for a in student.abilities if a.name == subject), None)
    return ability.xp if ability else 0


def reading(
    student: Character, book: Book, quality: int | None = None
) -> StudyResult | None:
    """A season reading a summa or tractatus (None for other books, or one
    without a Quality). A summa can't take the reader past its Level.
    `quality`, when given, is what the book is read at instead of its own
    (a palimpsest's text, see library.effective_quality)."""
    if book.quality is None or book.type not in (
        "Art Summa",
        "Ability Summa",
        "Tractatus",
    ):
        return None
    if book.type.endswith("Summa") and book.level is None:
        return None  # its Level is still to be set
    is_art = book.type == "Art Summa" or (
        book.type == "Tractatus" and book.subject_kind == "Art"
    )
    subject = book.art.title() if is_art else book.ability
    if book.ability.startswith(book_kinds.MASTERY_PREFIX):
        return None  # a spell's Mastery: the reading season works it out
    if not subject or (is_art and student.type != "magus"):
        return None  # only the Gifted study the Arts
    limit = book.level if book.type.endswith("Summa") else None
    return season_of_study(
        student,
        subject,
        book.quality if quality is None else quality,
        activity="reading",
        is_art=is_art,
        gain_limit=limit,
    )
