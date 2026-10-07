"""Study totals: Source Quality by source, the Advancement
Total and the xp a season gives.

    Advancement Total = Source Quality + Virtue bonuses - Flaw penalties
    xp gained         = Advancement Total, then x Affinity (x1.5, round up),
                        and never past the source's Gain Limit

Source Quality: exposure 2; adventure 5-10 (the storyguide's); practice 4;
training the master's score + 3 (limit: his score); teaching the teacher's
Communication + Teaching + 3, +6 for one student, +3 for two (limit: his
score); a summa its Quality (limit: its Level); a tractatus its Quality;
raw vis a stress die + the aura's modifier, using ceil(Art / 5) pawns.
Each full month lost cuts the total by a third, the rest rounded up.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..models import Book, Character
from . import effects, scores, xp
from .breakdown import Line
from .lab import ability_score
from .rounding import round_up

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Advancement "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Ten:"
    "_Long-Term_Events#Advancement)"
)
AFFINITY_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Four: Virtues and Flaws, Affinity "
    "with Art (x1.5, round up) "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Four:"
    "_Virtues_and_Flaws#Affinity_with_Art)"
)

EXPOSURE = 2
PRACTICE = 4


def training_quality(master: Character, ability: str) -> int:
    """A master's training: his score + 3."""
    return sum(ability_score(master, ability)) + 3


def teaching_quality(teacher: Character, students: int = 1) -> int:
    """A teacher's Source Quality: Communication + Teaching + 3, +6 with one
    student, +3 with two, plus Virtues such as Good Teacher (+5)."""
    bonus = {1: 6, 2: 3}.get(students, 0)
    extra = effects.amount_total(
        effects.collect(
            [scores.character_source(teacher.virtues_flaws)], "teaching_source_quality"
        )
    )
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


def season_of_study(
    student: Character,
    subject: str,
    source_quality: int,
    *,
    activity: str,
    is_art: bool,
    gain_limit: int | None = None,
    months_lost: int = 0,
) -> StudyResult:
    """One season studying `subject` (an Art or Ability name) from a source
    of `source_quality`, for `activity` (a study_total activity)."""
    lines = [Line("Source Quality", amount=source_quality, source=SOURCE)]
    source = scores.character_source(student.virtues_flaws)
    for effect in effects.collect([source], "study_total", activity=activity):
        lines.append(
            Line(
                effect.entry.name,
                amount=effect.modifier.amount or 0,
                source="character",
            )
        )
    total = int(sum(line.amount or 0 for line in lines))
    if activity in ("teaching", "reading"):
        total = max(total, 1)  # Poor Student can't take it below 1
    notes: list[str] = []
    if months_lost:
        reduced = after_distraction(total, months_lost)
        lines.append(
            Line(f"{months_lost} month(s) lost", amount=reduced - total, source=SOURCE)
        )
        total = reduced
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
        factor = xp.ART_FACTOR if is_art else xp.ABILITY_FACTOR
        current = _current_xp(student, subject, is_art)
        ceiling = xp.xp_for_score(gain_limit, factor)
        room = max(0, ceiling - current)
        if gained_xp > room:
            notes.append(
                f"Capped at score {gain_limit}: {room} xp of {gained_xp} count."
            )
            gained_xp = room
    return StudyResult(advancement_total=total, xp=gained_xp, lines=lines, notes=notes)


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
    (a palimpsest's text, see books.effective_quality)."""
    if book.quality is None or book.type not in (
        "Art Summa",
        "Ability Summa",
        "Tractatus",
    ):
        return None
    is_art = book.type == "Art Summa" or (
        book.type == "Tractatus" and book.subject_kind == "Art"
    )
    subject = book.art.title() if is_art else book.ability
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
