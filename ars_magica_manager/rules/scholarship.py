"""Scholars (Art & Academe, Chapter Six: Institutional Education, pp.
79-89, and Chapter Seven: Universities, pp. 102-104), as plain rules:
schools and what they teach, getting into one, teaching and clerkly
posts, the Academic Reputation's experience, and translating.

- Schools (p. 79): each teaches its major subjects up to its teacher's
  score (a student's limit at creation) and its minor ones to half that,
  rounded up; attending any needs Educated. INSTITUTIONS is the table.
- Getting in (pp. 81-86): the parent's (or his own) Presence + Bargain,
  Charm or Guile (Intrigue too for a cathedral) + a stress die against
  ENTRY_EASE; a cathedral takes off the highest Bad Reputation; a
  wealthy family's gift +1 to +3. Failure may try again next year; a
  botch, never with that teacher. A year costs FEES Mythic Pounds.
- A teaching or clerkly post (p. 89): a season looking, then Presence +
  the post's Ability + the highest Good Academic Reputation - the highest
  Bad one + 1 for a Minor Social Status Virtue or a General Virtue of
  education or privilege (3 for a Major Social Status Virtue; one bonus
  only) + a stress die against POST_EASE. Failure wastes the season; a
  botch also costs a Medium Wound or a Bad Reputation. A magister's or
  doctor's chair needs the licence; a monastic school's, a monk.
- A cathedral teacher's students (p. 84): a simple die for each point of
  Presence + the highest Good Academic Reputation; one more die each time
  that Reputation rises. A teacher teaches five times his Teaching (p. 86).
- Academic Reputation (p. 103): a Good one rises by 1 xp for each deed of
  GOOD_DEEDS; a Bad one by BAD_DEEDS' amounts. Hermetic Arts earn none.
  Disputing or writing against another faith earns double (p. 88).
- Translating (p. 87): both languages at 5 and Artes Liberales 2 (1
  between languages of one alphabet); the translation loses a Quality
  point for the languages (none with both at 6) and one for the culture
  (none with the source culture's Area Lore at 3, which the plan says);
  a Hermetic text translated by a magus loses only the first.
- Lecture commentaries (p. 102): a season editing one adds 1 Quality
  and the writer's Virtues; they don't count against his tractatus, at
  most his score in the Ability of them, and two earn an Academic
  Reputation xp.

The errata (pp. 12, 61) correct nothing on these pages.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Character, ScoredTrait
from . import confidence, reputations
from .rounding import round_up
from .scores import ability_level

SOURCE = (
    "Art & Academe, Chapter Six: Institutional Education, pp. 79-89; Chapter "
    "Seven: Universities, Lecture Commentaries and Academic Reputations, pp. "
    "102-103"
)
EDUCATED = "vf_educated"


@dataclass(frozen=True)
class Institution:
    label: str
    limit: int
    major: tuple[str, ...]
    minor: tuple[str, ...] = ()
    #: Any Academic Ability as a minor subject (a private tutor).
    any_minor: bool = False


#: The Limits of Education table (p. 79).
INSTITUTIONS: dict[str, Institution] = {
    "rural_parish": Institution("Rural parish school", 2, ("Artes Liberales", "Latin")),
    "urban_parish": Institution(
        "Urban parish school", 3, ("Artes Liberales", "Latin"), ("Theology",)
    ),
    "cathedral": Institution(
        "Cathedral school",
        6,
        ("Artes Liberales", "Latin", "Theology"),
        ("Canon Law", "Philosophiae"),
    ),
    "monastic": Institution(
        "Monastic school",
        4,
        ("Artes Liberales", "Latin", "Theology"),
        ("Medicine", "Philosophiae"),
    ),
    "municipal": Institution(
        "Municipal school (Italy)",
        5,
        ("Artes Liberales", "Latin", "Philosophiae", "Theology"),
        ("Medicine", "Civil Law"),
    ),
    "imperial": Institution(
        "Imperial school (Spain)",
        5,
        ("Artes Liberales", "Latin", "Medicine", "Philosophiae"),
        ("Greek", "Hebrew"),
    ),
    "tutor": Institution(
        "Private tutor", 6, ("Artes Liberales", "Latin"), any_minor=True
    ),
    "court": Institution(
        "Royal court", 4, ("Artes Liberales", "Latin"), ("Philosophiae", "Theology")
    ),
}

#: Getting in (pp. 81-87): school -> (Ease Factor, the Abilities the roll
#: may use, whether the highest Bad Reputation is taken off).
_PERSUADE = ("Bargain", "Charm", "Guile")
ENTRY: dict[str, tuple[str, int, tuple[str, ...], bool]] = {
    "rural_parish": ("A rural parish school", 6, _PERSUADE, False),
    "urban_parish": ("An urban parish school", 9, _PERSUADE, False),
    "cathedral": ("A cathedral school", 12, (*_PERSUADE, "Intrigue"), True),
    "monastic": ("A monastic school", 9, (*_PERSUADE, "Intrigue"), True),
    "urban_citizen": ("An urban school, a citizen", 9, (*_PERSUADE, "Intrigue"), True),
    "urban_foreigner": (
        "An urban school, a foreigner",
        12,
        (*_PERSUADE, "Intrigue"),
        True,
    ),
}
#: A year's fees in Mythic Pounds (pp. 81, 84, 87): (least, most).
FEES: dict[str, tuple[float, float]] = {
    "rural_parish": (0.1, 0.1),
    "urban_parish": (0.2, 0.2),
    "cathedral": (1, 1),
    "monastic": (0, 0),
    "urban_citizen": (0.25, 1 / 3),
    "urban_foreigner": (0.25, 1 / 3),
}
GIFT_BONUS_MAX = 3

#: Gaining a clerkly position (p. 89): post -> (label, Ease Factor, the
#: Abilities that suit it, what it needs besides).
POSTS: dict[str, tuple[str, int, tuple[str, ...], str]] = {
    "jurist": ("A secular jurist", 12, ("Civil and Canon Law", "Civil Law"), ""),
    "copyist": ("A copyist", 12, ("Profession: Scribe",), ""),
    "school_teacher": (
        "A municipal or royal court teacher",
        15,
        ("Teaching",),
        "",
    ),
    "monastic_teacher": (
        "A monastic school's teacher",
        15,
        ("Teaching",),
        "monk",
    ),
    "cathedral_teacher": (
        "A cathedral school's teacher",
        18,
        ("Artes Liberales", "Philosophiae", "Theology"),
        "",
    ),
    "magister": (
        "A magister in artibus",
        18,
        ("Artes Liberales",),
        "licence",
    ),
    "doctor": (
        "A doctor of a faculty",
        18,
        ("Theology", "Medicine", "Civil and Canon Law", "Philosophiae"),
        "licence",
    ),
}
MINOR_STATUS_BONUS = 1
MAJOR_STATUS_BONUS = 3
#: General Virtues that stand for education, privilege or prestige.
PRESTIGE_VIRTUES = frozenset(
    {"vf_educated", "vf_privileged_upbringing", "vf_famous", "vf_wealthy"}
)
LICENCES = frozenset({"vf_magister_in_artibus"})
MONASTIC = frozenset({"vf_monastic_vows", "vf_mendicant_friar"})
STUDENTS_PER_TEACHING = 5

#: Deeds that earn a Good Academic Reputation 1 xp (p. 103).
GOOD_DEEDS: dict[str, str] = {
    "summa": "Wrote a summa at half the Ability's score",
    "tractatus": "Wrote a tractatus",
    "two_commentaries": "Two lecture commentaries made",
    "translation": "Translated an academic text into Latin",
    "raised": "Raised Artes Liberales, Philosophiae, Theology or Law",
    "gloss": "Glossed a text a school teaches",
    "accepted": "Accepted by a school or master as a student",
    "teaching_post": "Gained a teaching position",
    "church_post": "Gained an ecclesiastical post",
    "notable": "Something academic the troupe finds notable",
}
#: Deeds that earn a Bad Academic Reputation xp (p. 103).
BAD_DEEDS: dict[str, tuple[str, int]] = {
    "forced_out": ("Forced to leave an academic post", 5),
    "no_summa": ("No summa in five years", 5),
    "no_tractatus": ("No tractatus or commentary in two years", 1),
    "lost_benefice": ("Lost a clerical benefice or prebend", 5),
    "lost_position": ("Lost a clerical position", 10),
    "immoral": ("Caught in immoral activities (at least)", 5),
    "stagnated": ("A year with no Good Academic Reputation xp", 1),
}
#: Disputing or writing against another faith doubles what it earns.
INTERFAITH_MULTIPLE = 2
ACADEMIC_SUBJECTS = (
    "Artes Liberales",
    "Philosophiae",
    "Theology",
    "Civil and Canon Law",
    "Canon Law",
    "Civil Law",
)

#: A new Good or Bad Academic Reputation's name when he has none.
DEFAULT_GOOD = "Learned Scholar"
DEFAULT_BAD = "Idle Scholar"

#: Translating (p. 87).
TRANSLATE_LANGUAGE = 5
ELEGANT_LANGUAGE = 6
TRANSLATE_ARTES = 2
SAME_ALPHABET_ARTES = 1
CULTURE_LORE = 3
#: Languages not written in the Latin alphabet, by their script.
SCRIPTS: dict[str, str] = {
    "greek": "Greek",
    "arabic": "Arabic",
    "hebrew": "Hebrew",
    "aramaic": "Hebrew",
    "syriac": "Syriac",
    "persian": "Arabic",
    "coptic": "Greek",
    "armenian": "Armenian",
    "georgian": "Georgian",
    "church slavonic": "Cyrillic",
    "russian": "Cyrillic",
}


def limit(institution: str, ability: str) -> int:
    """How high a school takes a student in `ability` (0: not taught)."""
    school = INSTITUTIONS[institution]
    base = ability.split(":")[0].strip()
    if base in school.major or ability in school.major:
        return school.limit
    if base in school.minor or ability in school.minor or school.any_minor:
        return round_up(school.limit / 2)
    return 0


def limit_lines(institution: str) -> list[str]:
    school = INSTITUTIONS[institution]
    lines = [f"{', '.join(school.major)} to {school.limit}"]
    if school.minor or school.any_minor:
        minor = "any Academic Ability" if school.any_minor else ", ".join(school.minor)
        lines.append(f"{minor} to {round_up(school.limit / 2)}")
    return lines


def highest_bad(character: Character) -> int:
    """The highest Bad Reputation's score, of any kind."""
    return max(
        (abs(r.score) for r in reputations.bad(character.reputations)), default=0
    )


def _academic(character: Character) -> list[ScoredTrait]:
    return [r for r in character.reputations if reputations.is_academic(r)]


def highest_good_academic(character: Character) -> int:
    return max((r.score for r in reputations.good(_academic(character))), default=0)


def highest_bad_academic(character: Character) -> int:
    """The highest Bad Academic Reputation's score: a roll subtracts it
    as it adds the highest Good one (pp. 89, 100)."""
    return max((abs(r.score) for r in reputations.bad(_academic(character))), default=0)


def entry_total(character: Character, school: str, ability: str, gift: int = 0) -> int:
    """Presence + the Ability (+ a gift, - the highest Bad Reputation where
    the school takes it off)."""
    _label, _ease, _abilities, bad = ENTRY[school]
    total = (
        character.characteristics.presence
        + ability_level(character, ability)
        + max(0, min(GIFT_BONUS_MAX, gift))
    )
    return total - (highest_bad(character) if bad else 0)


def status_bonus(character: Character, categories: dict[str, tuple[str, str]]) -> int:
    """+3 for a Major Social Status Virtue, else +1 for a Minor one or a
    General Virtue of education or privilege; `categories` maps a Virtue's
    id to its (category, tier)."""
    best = 0
    for vf in character.virtues_flaws:
        category, tier = categories.get(vf.vf_id, ("", ""))
        if category == "Social Status" and tier == "Major":
            return MAJOR_STATUS_BONUS
        if (category == "Social Status" and tier == "Minor") or (
            vf.vf_id in PRESTIGE_VIRTUES
        ):
            best = MINOR_STATUS_BONUS
    return best


def post_total(character: Character, ability: str, bonus: int) -> int:
    """Presence + Ability + highest Good Academic Reputation - highest Bad
    Academic Reputation + the Virtue's bonus."""
    return (
        character.characteristics.presence
        + ability_level(character, ability)
        + highest_good_academic(character)
        - highest_bad_academic(character)
        + bonus
    )


def post_problem(character: Character, post: str) -> str | None:
    label, _ease, _abilities, needs = POSTS[post]
    ids = {vf.vf_id for vf in character.virtues_flaws}
    if needs == "licence" and not ids & LICENCES:
        return f"{label}'s chair needs the licence (Magister in Artibus)."
    if needs == "monk" and not ids & MONASTIC:
        return f"{label}'s post goes only to a monk (A&A p. 89)."
    return None


def student_dice(character: Character) -> int:
    """A cathedral teacher's students: this many simple dice."""
    return max(0, character.characteristics.presence + highest_good_academic(character))


def students_taught(character: Character) -> int:
    return STUDENTS_PER_TEACHING * ability_level(character, "Teaching")


# -- Academic Reputation xp ---------------------------------------------------


def _choose(character: Character, bad: bool, name: str) -> ScoredTrait:
    """The Academic Reputation xp goes to: the one of that side named,
    else his highest of that side (one still at 0 included), else a new
    one at 0. A Good and a Bad one are separate entries (p. 103)."""
    pool = [r for r in _academic(character) if reputations.is_bad(r) == bad]
    if name:
        found = next((r for r in pool if r.name.casefold() == name.casefold()), None)
        if found is not None:
            return found
    elif pool:
        return max(pool, key=lambda r: abs(r.score))
    new = ScoredTrait(
        name or (DEFAULT_BAD if bad else DEFAULT_GOOD),
        0,
        type=reputations.ACADEMIC,
        bad=bad,
    )
    character.reputations.append(new)
    return new


def add_academic_xp(character: Character, xp: int, name: str = "") -> ScoredTrait:
    """Add `xp` to a Good Academic Reputation (a negative `xp` to a Bad
    one, a separate entry with its own positive score, p. 103). Returns
    it."""
    bad = xp < 0
    reputation = _choose(character, bad, name)
    reputation.bad = bad
    confidence.add_deeds(reputation, abs(xp))
    return reputation


# -- translating ----------------------------------------------------------------


def script(language: str) -> str:
    return SCRIPTS.get(language.strip().casefold(), "Latin")


def translation_artes(source: str, target: str) -> int:
    """The Artes Liberales a translation needs: 2, or 1 between languages
    written in one alphabet."""
    return SAME_ALPHABET_ARTES if script(source) == script(target) else TRANSLATE_ARTES


def translation_loss(
    source_score: int, target_score: int, hermetic_by_magus: bool, culture_lore: bool
) -> int:
    """The Quality a translation loses: 1 for the languages unless both
    are at 6, and 1 for the culture unless he knows the source culture's
    (Area) Lore at 3. A Hermetic text translated by a magus never loses
    the culture's point (p. 87)."""
    language = 0 if min(source_score, target_score) >= ELEGANT_LANGUAGE else 1
    culture = 0 if hermetic_by_magus or culture_lore else 1
    return language + culture
