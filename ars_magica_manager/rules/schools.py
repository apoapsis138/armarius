"""The Limits of Education (Art & Academe p. 79): a starting character
educated at a school other than a university may not raise its subjects
above what its masters know. Its major subjects are limited to the
school's limit, its minor ones to half of it (rounded up), and a subject
it doesn't teach can't be learned there at all. The school is named on the
character's Educated Virtue; with none named, no limit is set.

Only the subjects the table names are limited (Artes Liberales, Latin,
Greek, Hebrew, Theology, Canon and Civil Law, Philosophiae, Medicine):
an Academic Ability no school there teaches (Common Law, Art of Memory,
another learned tongue) is left to its own Virtue and the age cap. A
municipal school's "Medicine or Civil Law" is one major subject, the
student's choice, so the school is named with it.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Character
from .rounding import round_up

SOURCE = "Art & Academe, The Limits of Education, p. 79"
#: The Virtue that names the school, and its parameter.
EDUCATED = "vf_educated"
PARAM = "school"


@dataclass(frozen=True)
class School:
    limit: int
    major: frozenset[str]
    minor: frozenset[str]
    #: A Private Tutor teaches any Academic Ability as a minor subject.
    any_minor: bool = False


def _subjects(*names: str) -> frozenset[str]:
    return frozenset(names)


_BASICS = ("artes liberales", "latin")

#: The schools, by the name stored on the Virtue (lower case).
SCHOOLS: dict[str, School] = {
    "rural parish school": School(2, _subjects(*_BASICS), _subjects()),
    "urban parish school": School(3, _subjects(*_BASICS), _subjects("theology")),
    "cathedral school": School(
        6,
        _subjects(*_BASICS, "theology"),
        _subjects("canon law", "philosophiae"),
    ),
    "monastic school": School(
        4,
        _subjects(*_BASICS, "theology"),
        _subjects("medicine", "philosophiae"),
    ),
    "municipal school (italy), medicine": School(
        5,
        _subjects(*_BASICS, "medicine"),
        _subjects("philosophiae", "theology"),
    ),
    "municipal school (italy), civil law": School(
        5,
        _subjects(*_BASICS, "civil law"),
        _subjects("philosophiae", "theology"),
    ),
    "imperial school (spain)": School(
        5,
        _subjects(*_BASICS, "greek", "hebrew"),
        _subjects("medicine", "philosophiae"),
    ),
    "private tutor": School(6, _subjects(*_BASICS), _subjects(), any_minor=True),
    "royal court": School(
        4, _subjects(*_BASICS), _subjects("philosophiae", "theology")
    ),
}
NAMES: tuple[str, ...] = tuple(name.title() for name in SCHOOLS)
#: A school named before its major subject was chosen: read as the one of
#: its two subjects the character has learned more of.
MUNICIPAL = "municipal school (italy)"


def subjects_of(ability: str) -> frozenset[str]:
    """The table's subjects an Ability is (Civil and Canon Law is both
    laws), none when the table doesn't name it."""
    if ability == "Artes Liberales":
        return _subjects("artes liberales")
    if ability in ("Philosophiae", "Medicine"):
        return _subjects(ability.lower())
    if ability.startswith("Theology"):
        return _subjects("theology")
    if ability == "Civil and Canon Law":
        return _subjects("canon law", "civil law")
    language = ability.removeprefix("Dead Language: ")
    if language != ability and language in ("Latin", "Greek", "Hebrew"):
        return _subjects(language.lower())
    return _subjects()


def school_of(character: Character) -> School | None:
    """The school named on the character's Educated Virtue, or None."""
    for vf in character.virtues_flaws:
        if vf.vf_id == EDUCATED:
            name = str(vf.params.get(PARAM) or "").lower()
            if name == MUNICIPAL:
                name = f"{MUNICIPAL}, {_municipal_major(character)}"
            found = SCHOOLS.get(name)
            if found is not None:
                return found
    return None


def _municipal_major(character: Character) -> str:
    xp = {a.name: a.xp for a in character.abilities}
    if xp.get("Civil and Canon Law", 0) > xp.get("Medicine", 0):
        return "civil law"
    return "medicine"


def cap(character: Character, ability: str) -> int | None:
    """The highest score the character's school lets `ability` have at
    creation: its limit for a major subject, half (rounded up) for a minor
    one, 0 for one it doesn't teach; None when no school is named or the
    table doesn't name the subject."""
    school = school_of(character)
    subjects = subjects_of(ability)
    if school is None or not subjects:
        return None
    if subjects & school.major:
        return school.limit
    if subjects & school.minor or school.any_minor:
        return round_up(school.limit / 2)
    return 0
