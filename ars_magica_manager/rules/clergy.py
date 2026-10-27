"""A cleric's career: the grades of holy orders and their examinations,
what ordination brings, exorcism, the canon courts and petitioning the
Church.

Book pages (The Church; the Errata's only line on the book, Errata p. 78,
is about Templar Prestige, p. 125, and touches none of these):

- The grades and the Ordination Examination Total, Int + Church Lore or
  Civil and Canon Law + stress die against each grade's Ease Factor: The
  Church p. 33; ordination is a season, Source Quality 2 in the Ability.
- What an examination's result does, and one Faith Point however many
  grades: p. 34. A miss of exactly 6 isn't covered ("less than 6" passes,
  "more than 6" fails); the app passes it with the Reputation for
  ignorance, a house ruling filling the gap.
- Minor orders may marry; major orders are celibate: pp. 34-35. A priest
  must be freeborn, legitimate, sound of body and mind, educated and 25,
  each waived by a dispensation (a petition, EF 9), and needs a benefice
  or curacy free: p. 35.
- The Social Statuses: Clerk (DE p. 74; The Church p. 26) for minor orders,
  sub-deacons and deacons; Priest (DE p. 104; The Church p. 26), which a
  monk ordained priest takes instead of Religious (DE p. 106; The Church
  p. 26); Senior Clergy, a Major Virtue (DE p. 107; The Church pp. 25-26),
  for a bishop, who is elected, not examined (p. 33). A character holds
  two Social Statuses only where both say they are compatible, and the
  clergy's don't, so the new one replaces the old: ordination offers the
  swap and never keeps both (The Church pp. 25, 34; DE p. 63).
- Exorcism: at least one Confidence or Faith Point, +3 each; stress die +1
  for an ordained exorcist, +1 holy water, +1 a crucifix, against the
  Might the demon invested; a Divine power, so the aura counts as the
  Realm Interaction Table says (DE p. 411), and it must Penetrate the
  energumen's Magic Resistance: The Church p. 34.
- Canon courts, compurgation and the two days' travel: pp. 35-36; the
  punishments and Irregularity: p. 37; the kinds of case: pp. 37-38.
- Petitions, their modifiers and the argument roll (Int + Ability + stress
  die against 9): p. 46; the Ease Factors and the written and audience
  totals: p. 47; no die, one a season, who may grant it, the scribe, The
  Gift, and appeals: p. 48.
"""

from __future__ import annotations

import random
from collections.abc import Mapping
from dataclasses import dataclass

from .. import catalog
from ..models import (
    REALMS,
    Character,
    ChurchCareer,
    Ordination,
    Petition,
    Saga,
    ScoredTrait,
    VirtueFlawInstance,
)
from ..models.clergy import (
    ACCUSED,
    AUDIENCE,
    EXCOMMUNICATED,
    GOOD_STANDING,
    GUILTY,
    IRREGULAR,
)
from . import confidence, dice, realms
from .scores import ability_level
from .study import gift_social_penalty

SOURCE = (
    "The Church, Ordination pp. 33-35, Canon Law pp. 35-38, Petitioning the "
    "Church pp. 46-48; Ars Magica Definitive Edition, Clerk p. 74, Priest p. "
    "104, Religious p. 106, Senior Clergy p. 107, the Realm Interaction Table "
    "p. 411"
)
TC = "The Church"

CHURCH_LORE = "Church Lore"
CANON_LAW = "Civil and Canon Law"
#: The names Church Lore goes by on a sheet: the catalog's Organization
#: Lore, and the books' own name.
CHURCH_LORE_NAMES = ("Organization Lore: Church", "Church Lore")


@dataclass(frozen=True)
class Grade:
    """A grade of holy orders: the Ability its examination tests and the
    Ease Factor (0 for a bishop, who is elected), and whether it is a minor
    order (p. 33)."""

    name: str
    ability: str
    ease: int
    minor: bool


GRADES: tuple[Grade, ...] = (
    Grade("Doorkeeper", CHURCH_LORE, 3, True),
    Grade("Lector", CHURCH_LORE, 6, True),
    Grade("Exorcist", CANON_LAW, 3, True),
    Grade("Acolyte", CANON_LAW, 6, True),
    Grade("Sub-deacon", CHURCH_LORE, 9, False),
    Grade("Deacon", CANON_LAW, 9, False),
    Grade("Priest", CHURCH_LORE, 12, False),
    Grade("Bishop", "", 0, False),
)
BY_NAME: dict[str, Grade] = {g.name: g for g in GRADES}
NAMES: tuple[str, ...] = tuple(g.name for g in GRADES)
EXORCIST, PRIEST, BISHOP = "Exorcist", "Priest", "Bishop"

STANDING_LABELS: dict[str, str] = {
    GOOD_STANDING: "In good standing",
    IRREGULAR: "Irregular",
    EXCOMMUNICATED: "Excommunicated",
}

# -- the grades --


def church_lore(character: Character) -> int:
    """His Church Lore, under either name."""
    return max(ability_level(character, name) for name in CHURCH_LORE_NAMES)


def score_in(character: Character, ability: str) -> int:
    """His score in the Ability an examination tests."""
    if ability == CHURCH_LORE:
        return church_lore(character)
    return ability_level(character, ability)


def rank(grade: str) -> int:
    """The grade's place on the ladder, -1 for a layman (or an unknown
    grade)."""
    return NAMES.index(grade) if grade in NAMES else -1


def next_grade(career: ChurchCareer) -> Grade | None:
    """The grade he would be examined for next (None past Priest: a bishop
    is elected)."""
    following = rank(career.grade) + 1
    if following >= len(GRADES) or GRADES[following].name == BISHOP:
        return None
    return GRADES[following]


def examinable(career: ChurchCareer) -> tuple[Grade, ...]:
    """The grades above his that an examination can bring (not Bishop)."""
    return tuple(g for g in GRADES[rank(career.grade) + 1 :] if g.name != BISHOP)


def in_orders(career: ChurchCareer) -> bool:
    return career.grade in BY_NAME


def is_minor(grade: str) -> bool:
    found = BY_NAME.get(grade)
    return found is not None and found.minor


def orders_words(grade: str) -> str:
    """ "minor orders" or "major orders" ("" for a layman)."""
    if grade not in BY_NAME:
        return ""
    return "minor orders" if is_minor(grade) else "major orders"


def faith_points_from_orders(career: ChurchCareer) -> int:
    """The Faith Points his ordinations brought: one each (p. 34)."""
    return sum(1 for o in career.ordinations if ordained(o.result))


def has_church_tab(character: Character) -> bool:
    """Whether the sheet shows the Church tab: only for a character with a
    grade, a petition or a canon case."""
    c = character.church
    return in_orders(c) or bool(c.petitions) or bool(c.cases) or bool(c.ordinations)


def may_use_faith_points(career: ChurchCareer) -> bool:
    """An Irregular cleric can't use Faith Points until he confesses
    (p. 37)."""
    return career.standing != IRREGULAR


# -- the examination --

#: An examination's result: its label, whether he is ordained, and the
#: Reputation step it brings (+1 knowledgeable, -1 ignorant).
LEARNED = "learned"
ORDAINED = "ordained"
IGNORANT = "ignorant"
FAILED = "failed"
BOTCHED = "botched"
ELECTED = "elected"
RECORDED = "recorded"
EXAM_RESULTS: dict[str, tuple[str, bool, int]] = {
    LEARNED: ("Ordained, +1 Reputation", True, 1),
    ORDAINED: ("Ordained", True, 0),
    IGNORANT: ("Passed, -1 Reputation", True, -1),
    FAILED: ("Not ordained", False, 0),
    BOTCHED: ("Botched", False, 0),
    ELECTED: ("Elected", True, 0),
    RECORDED: ("Ordained (recorded)", True, 0),
}
#: A miss by this much or less still passes (a house ruling for exactly 6).
PASSING_MISS = 6
#: The Ease Factor of an appeal, a dispensation, or leave to sit again
#: after a botch: all petitions at 9 (pp. 34-35, 47).
APPEAL_EASE = 9


def ordained(result: str) -> bool:
    return EXAM_RESULTS.get(result, ("", False, 0))[1]


def result_label(result: str) -> str:
    return EXAM_RESULTS.get(result, (result, False, 0))[0]


def exam_result(total: int, ease: int, *, botched: bool = False) -> str:
    """What an Examination Total brings against the grade's Ease Factor
    (p. 34): more than double, ordained and known for it; meeting it,
    ordained; missing by 6 or less, passed but known for ignorance; by 7 or
    more, not ordained; a botch, barred until a petition."""
    if botched:
        return BOTCHED
    if total > 2 * ease:
        return LEARNED
    if total >= ease:
        return ORDAINED
    if ease - total <= PASSING_MISS:
        return IGNORANT
    return FAILED


@dataclass(frozen=True)
class ExamTerms:
    """The Examination Total before the die: the grade, the Ability, his
    Intelligence and score."""

    grade: Grade
    intelligence: int
    score: int

    @property
    def base(self) -> int:
        return self.intelligence + self.score


def exam_terms(character: Character, grade: Grade) -> ExamTerms:
    return ExamTerms(
        grade,
        character.characteristics.intelligence,
        score_in(character, grade.ability),
    )


def examine(
    saga: Saga | None,
    character: Character,
    grade: Grade,
    rng: random.Random,
    *,
    season: str = "",
    year: int | None = None,
) -> Ordination:
    """Sit the grade's examination: the roll and its result, as a record."""
    die = dice.stress_die(rng, saga=saga)
    return examine_with(
        character,
        grade,
        0 if die.botched else die.value,
        botched=die.botched,
        season=season,
        year=year,
    )


def examine_with(
    character: Character,
    grade: Grade,
    die: int,
    *,
    botched: bool = False,
    season: str = "",
    year: int | None = None,
) -> Ordination:
    """The grade's examination with the die rolled at the table."""
    terms = exam_terms(character, grade)
    record = Ordination(
        grade.name,
        season=season,
        year=year,
        ability=grade.ability,
        intelligence=terms.intelligence,
        score=terms.score,
        die=0 if botched else max(0, die),
        botched=botched,
        ease=grade.ease,
    )
    record.result = exam_result(record.total, grade.ease, botched=botched)
    return record


# -- what ordination brings --

CLERK = "vf_clerk"
PRIEST_STATUS = "vf_priest"
RELIGIOUS = "vf_religious"
SENIOR_CLERGY = "vf_senior_clergy"
MENDICANT_FRIAR = "vf_mendicant_friar"
SOCIAL_STATUS = "Social Status"


def social_statuses(character: Character) -> list[VirtueFlawInstance]:
    """His Social Status Virtues and Flaws."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    return [
        vf
        for vf in character.virtues_flaws
        if (found := by_id.get(vf.vf_id)) is not None
        and found.category == SOCIAL_STATUS
    ]


def _held(character: Character, vf_id: str) -> VirtueFlawInstance | None:
    return next((vf for vf in character.virtues_flaws if vf.vf_id == vf_id), None)


@dataclass(frozen=True)
class StatusChange:
    """What ordination does to the Social Status: the statuses taken away
    and the one given in their place (None: none), or why it is left
    alone. A character holds one Social Status unless both say they are
    compatible, and the clergy's don't, so the new one always replaces
    the old (The Church pp. 25, 34; DE p. 63)."""

    remove: tuple[str, ...] = ()
    add: str | None = None
    warning: str = ""

    @property
    def swaps(self) -> bool:
        """It takes away a status he holds: the swap ordination offers."""
        return bool(self.remove) and self.add is not None


#: The clergy's own statuses, which the minor orders leave alone.
CLERICAL = frozenset({CLERK, PRIEST_STATUS, RELIGIOUS, SENIOR_CLERGY, MENDICANT_FRIAR})


def status_change(character: Character, grade: str) -> StatusChange:
    """The Social Status ordination to `grade` gives (pp. 25-26, 34), in
    place of every other he holds: Doorkeeper to Deacon give Clerk to
    someone with no clergy status; Priest replaces Clerk, Religious, a
    Mendicant Friar's or a lay status. A bishop's Senior Clergy is a Major
    Virtue, so its swap is left to the troupe on Virtues & Flaws."""
    statuses = [vf.vf_id for vf in social_statuses(character)]
    if grade == BISHOP:
        if SENIOR_CLERGY in statuses:
            return StatusChange()
        return StatusChange(
            warning="A bishop takes the Senior Clergy Social Status, a Major "
            "Virtue, in place of his own: swap it on Virtues & Flaws "
            "(DE p. 107; The Church pp. 25-26)."
        )
    if grade == PRIEST:
        if PRIEST_STATUS in statuses or SENIOR_CLERGY in statuses:
            return StatusChange()
        return StatusChange(remove=tuple(statuses), add=PRIEST_STATUS)
    if grade not in BY_NAME or CLERICAL.intersection(statuses):
        return StatusChange()
    return StatusChange(remove=tuple(statuses), add=CLERK)


def swap_names(change: StatusChange) -> tuple[str, str]:
    """The swap's names: the statuses given up ("Covenfolk") and the new."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    old = " and ".join(_vf_name(by_id, vf_id) for vf_id in change.remove)
    return old, _vf_name(by_id, change.add) if change.add is not None else ""


def apply_status(character: Character, change: StatusChange) -> None:
    for vf_id in change.remove:
        found = _held(character, vf_id)
        if found is not None:
            character.virtues_flaws.remove(found)
    if change.add is not None and _held(character, change.add) is None:
        character.virtues_flaws.append(VirtueFlawInstance(change.add))


def reputation_name(ability: str) -> str:
    return f"Learned in {ability}"


def _level_xp(level: int) -> int:
    return confidence.XP_PER_LEVEL * level * (level + 1) // 2


def shift_reputation(character: Character, ability: str, step: int) -> ScoredTrait:
    """A Reputation of 1 for knowing (step +1) or not knowing (-1) the
    Ability, or a Reputation experience point toward it on one he has
    (p. 34; DE p. 387): kept as one Ecclesiastical Reputation, positive for
    learning, negative for ignorance."""
    name = reputation_name(ability)
    found = next(
        (r for r in character.reputations if r.name.casefold() == name.casefold()),
        None,
    )
    if found is None:
        found = ScoredTrait(name, step, type="Ecclesiastical")
        character.reputations.append(found)
        return found
    sign = -1 if found.score < 0 else 1
    signed = sign * (_level_xp(abs(found.score)) + found.deeds) + step
    level = 0
    while _level_xp(level + 1) <= abs(signed):
        level += 1
    found.score = level if signed >= 0 else -level
    found.deeds = abs(signed) - _level_xp(level)
    return found


def ordain(character: Character, record: Ordination, *, swap: bool = True) -> list[str]:
    """Keep an examination's record and do what it brings: the grade, a
    Faith Point, the Social Status and the Reputation; a botch bars him.
    `swap` False declines the offered swap of Social Status: his own is
    left for the troupe to change by hand. Returns what changed, for the
    Diary."""
    career = character.church
    career.ordinations.append(record)
    said: list[str] = []
    if record.result == BOTCHED:
        career.barred = True
        return [
            f"Botched the examination for {record.grade}: he may sit it again only "
            f"once a petition (EF {APPEAL_EASE}) allows it ({TC} p. 34)."
        ]
    if not ordained(record.result):
        return [
            f"Not ordained {record.grade}: he may appeal (a petition, EF "
            f"{APPEAL_EASE}) or sit it again another season ({TC} p. 34)."
        ]
    career.grade = record.grade
    career.barred = False
    character.background.faith_points += 1
    said.append(f"Ordained {record.grade}: a Faith Point.")
    change = status_change(character, record.grade)
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    if change.swaps and not swap:
        old, new = swap_names(change)
        said.append(
            f"Social Status left as {old}: swap it for {new} on Virtues & "
            f"Flaws, one status only ({TC} pp. 25, 34)."
        )
    elif change.add is not None:
        apply_status(character, change)
        said.append(f"Social Status: {_vf_name(by_id, change.add)}.")
    if change.warning:
        said.append(change.warning)
    step = EXAM_RESULTS[record.result][2]
    if step and record.ability:
        found = shift_reputation(character, record.ability, step)
        said.append(f"Reputation: {found.name} {found.score:+d}.")
    if not is_minor(record.grade) and record.grade in BY_NAME:
        said.append("A major order: celibate from now on.")
    return said


def _vf_name(by_id: Mapping[str, object], vf_id: str) -> str:
    found = by_id.get(vf_id)
    return str(getattr(found, "name", vf_id))


# -- toward the priesthood --

#: The Flaws that may bar "sound of body and mind" (p. 35 names the
#: missing limbs and poor eyesight; the rest are the troupe's to judge).
UNSOUND = frozenset(
    {
        "vf_dwarf",
        "vf_lame",
        "vf_crippled",
        "vf_blind",
        "vf_missing_eye",
        "vf_missing_hand",
        "vf_no_hands",
        "vf_deaf",
        "vf_poor_eyesight",
        "vf_simple_minded",
    }
)
ILLEGITIMATE = frozenset({"vf_bastard"})
UNFREE = frozenset({"vf_slave"})
PRIEST_AGE = 25


@dataclass(frozen=True)
class Requirement:
    """One of a priest's requirements: what it is, and whether he meets it
    (None: the sheet can't say)."""

    label: str
    met: bool | None
    why: str = ""


def priest_requirements(
    saga: Saga, character: Character, age: int | None
) -> list[Requirement]:
    """What stands between him and the priesthood (p. 35): each one he
    fails needs a dispensation, a petition at EF 9. Warned, never blocked."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    held = {vf.vf_id for vf in character.virtues_flaws}
    found = [
        Requirement(
            f"{PRIEST_AGE} years old" if age is None else f"{age} years old",
            None if age is None else age >= PRIEST_AGE,
            "" if age is None else f"{PRIEST_AGE} needed",
        ),
        Requirement("freeborn", not (held & UNFREE)),
        Requirement(
            "legitimate",
            not (held & ILLEGITIMATE),
            ", ".join(_vf_name(by_id, x) for x in sorted(held & ILLEGITIMATE)),
        ),
        Requirement(
            "sound of body and mind",
            not (held & UNSOUND),
            ", ".join(_vf_name(by_id, x) for x in sorted(held & UNSOUND)),
        ),
        Requirement(
            "a benefice or curacy",
            True if character.church.benefice.strip() else None,
        ),
    ]
    return found


# -- exorcism --

EXORCIST_BONUS = 1
HOLY_WATER = 1
CRUCIFIX = 1
POINT_BONUS = 3


def exorcism_bonus(
    grade: str,
    points: int,
    *,
    holy_water: bool,
    crucifix: bool,
    aura_realm: str,
    aura: int,
) -> tuple[int, list[str]]:
    """The Exorcism Total before the die, and its terms (p. 34): +3 per
    Confidence or Faith Point (at least one), +1 for an ordained exorcist
    (every grade from Exorcist up has been ordained one), +1 holy water,
    +1 a crucifix, and the aura as it changes a Divine power."""
    points = max(1, points)
    terms = [f"{points} Point{'s' if points != 1 else ''} +{POINT_BONUS * points}"]
    total = POINT_BONUS * points
    if rank(grade) >= rank(EXORCIST) and grade in BY_NAME:
        terms.append(f"ordained exorcist +{EXORCIST_BONUS}")
        total += EXORCIST_BONUS
    if holy_water:
        terms.append(f"holy water +{HOLY_WATER}")
        total += HOLY_WATER
    if crucifix:
        terms.append(f"a crucifix +{CRUCIFIX}")
        total += CRUCIFIX
    if aura_realm in REALMS and aura:
        change = realms.aura_modifier("Divine", aura_realm, aura)
        if change:
            terms.append(f"{aura_realm} aura {change:+d}")
            total += change
    return total, terms


# -- the canon courts --

COURTS: tuple[str, ...] = (
    "The archdeacon's",
    "The rural dean's",
    "The parish priest's",
    "The bishop's (appeal)",
    "The papal curia",
)
#: The kinds of case a canon court hears (pp. 37-38).
CHARGES: tuple[str, ...] = (
    "Shedding of blood",
    "Marriage and sexual crimes",
    "Sanctuary broken",
    "Simony",
    "Usury",
    "Wills",
    "Upkeep of the church",
    "Religious practices",
    "Tithes",
    "Slander",
    "Sorcery and witchcraft",
    "Other",
)
EXCOMMUNICATION = "Excommunication"
#: The punishments a canon court gives, and what each does (p. 37).
PUNISHMENTS: dict[str, str] = {
    "Monition": "An official warning, usually for a first offence.",
    "Public penance": "Penance before the congregation; failing it brings a fine.",
    "A fine": "Paid to the Church, or to the one sinned against; imposed when "
    "penance isn't done.",
    "Imprisonment in a monastery": "In a monastery or nunnery; seldom secure.",
    "Benefice suspended": "For a time or for good, usually after a monition.",
    EXCOMMUNICATION: "No sacrament but penance, no burial in consecrated "
    "ground; a clergyman loses his shield from secular justice. Lifted by "
    "confession, repentance and penance.",
}


def case_standing(career: ChurchCareer) -> str:
    """The standing his cases leave him: Excommunicated while a guilty
    verdict against him carries it; otherwise what is recorded."""
    for case in career.cases:
        if (
            case.role == ACCUSED
            and case.verdict == GUILTY
            and case.punishment == EXCOMMUNICATION
        ):
            return EXCOMMUNICATED
    return career.standing


# -- petitions --

#: The book's example petitions and their Ease Factors (p. 47).
EXAMPLES: tuple[tuple[str, int], ...] = (
    ("A marriage blessing", 3),
    ("Access to the parish crypt or library", 6),
    ("A priest to travel two days for last rites", 6),
    ("A letter of safe passage for pilgrims", 6),
    ("Access to the cathedral library", 9),
    ("Appeal an ordination exam", 9),
    ("A dispensation for a grade", 9),
    ("Leave to sit an examination again", 9),
    ("Appoint him to a vacant benefice", 9),
    ("Excommunicate a freeman or minor cleric", 9),
    ("License of absence from a benefice", 9),
    ("Establish a chapel", 9),
    ("Exhume a corpse", 9),
    ("Excommunicate a magus or a priest", 12),
    ("Move a church", 12),
    ("Rent land to a Hermetic covenant", 12),
    ("Consecrate a parish church", 15),
    ("Excommunicate a nobleman", 15),
    ("Interdict a town", 15),
    ("Appeal the election of a bishop", 18),
    ("Establish a monastery", 18),
    ("Create a diocese, crown a king, excommunicate a bishop", 21),
    ("Change canon law, interdict a kingdom", 24),
    ("Declare a saint", 30),
    ("Call a crusade or found an order", 42),
)
EXAMPLE_EASE: dict[str, int] = dict(EXAMPLES)

#: Support from the clergy and from laymen: the highest of each counts,
#: once (p. 46).
CLERGY_SUPPORT: tuple[tuple[str, int], ...] = (
    ("None", 0),
    ("A priest or deacon (+1)", 1),
    ("A senior clergyman: bishop, abbot, archdeacon (+3)", 3),
    ("An archbishop or higher (+6)", 6),
)
LAY_SUPPORT: tuple[tuple[str, int], ...] = (
    ("None", 0),
    ("A knight (+1)", 1),
    ("A nobleman: baron, count (+3)", 3),
    ("A king, duke, earl or emperor (+6)", 6),
)
TESTIMONY, EVIDENCE, VISION, MIRACLE = 1, 1, 3, 6
#: The arguments a petition may put, each +1 to +3 if its roll succeeds.
ARGUMENTS: tuple[str, ...] = (CANON_LAW, "Artes Liberales", "Intrigue")
ARGUMENT_MAX = 3
DONATION_MAX = 3
ARGUMENT_EASE = 9
#: Who may grant a petition, by its Ease Factor (p. 48).
PRIEST_GRANTS = 6
BISHOP_GRANTS = 15
APPEAL_MARGIN = 3
LATE_APPEAL = 3


def argument_counts(petition: Petition, ability: str) -> int:
    """What an argument adds: its bonus if its roll reached 9, minus it if
    the roll botched, nothing otherwise (or while not rolled)."""
    bonus = min(ARGUMENT_MAX, max(0, petition.arguments.get(ability, 0)))
    if not bonus:
        return 0
    if ability in petition.argument_botches:
        return -bonus
    rolled = petition.argument_rolls.get(ability)
    return bonus if rolled is not None and rolled >= ARGUMENT_EASE else 0


def roll_arguments(
    saga: Saga | None, character: Character, petition: Petition, rng: random.Random
) -> None:
    """Roll each argument put: Int + the Ability + stress die against 9."""
    petition.argument_rolls, petition.argument_botches = {}, []
    for ability, bonus in petition.arguments.items():
        if bonus <= 0:
            continue
        die = dice.stress_die(rng, saga=saga)
        base = character.characteristics.intelligence + ability_level(
            character, ability
        )
        if die.botched:
            petition.argument_botches.append(ability)
            petition.argument_rolls[ability] = min(0, base)
        else:
            petition.argument_rolls[ability] = base + die.value


def petition_terms(petition: Petition) -> list[tuple[str, int]]:
    """Each term of the Petition Total, in the book's order (pp. 46-48)."""
    written = petition.method != AUDIENCE
    if written and petition.scribe_total is not None:
        terms = [
            (
                f"{petition.scribe or 'the scribe'}'s Communication + Church Lore",
                petition.scribe_total,
            )
        ]
    else:
        terms = [
            ("Communication" if written else "Presence", petition.characteristic),
            ("Church Lore", petition.lore),
        ]
    if not written and petition.gift:
        terms.append(("The Gift", -petition.gift))
    for flag, words, value in (
        (petition.testimony, "testimony", TESTIMONY),
        (petition.evidence, "magical evidence", EVIDENCE),
        (petition.vision, "a holy vision", VISION),
        (petition.miracle, "miracles", MIRACLE),
    ):
        if flag:
            terms.append((words, value))
    if petition.clergy:
        terms.append(("clergy support", petition.clergy))
    if petition.lay:
        terms.append(("lay support", petition.lay))
    if petition.donation:
        terms.append(("a donation", min(DONATION_MAX, max(0, petition.donation))))
    for ability in ARGUMENTS:
        if petition.arguments.get(ability):
            terms.append((f"{ability} argument", argument_counts(petition, ability)))
    if petition.reputation:
        terms.append(("Reputation with the Church", petition.reputation))
    if petition.spells:
        terms.append(("spells", petition.spells))
    if petition.appeal and petition.late:
        terms.append(("a later season", -LATE_APPEAL))
    return terms


def petition_total(petition: Petition) -> int:
    """The Petition Total: no die is rolled (p. 48)."""
    return sum(value for _words, value in petition_terms(petition))


def petition_ease(petition: Petition) -> int:
    """The Ease Factor: an appeal's is the original total + 3."""
    if petition.appeal and petition.original is not None:
        return petition.original + APPEAL_MARGIN
    return petition.ease


def decider(ease: int) -> str:
    """Who may grant it (p. 48)."""
    if ease <= PRIEST_GRANTS:
        return "the local priest"
    if ease <= BISHOP_GRANTS:
        return "the bishop"
    return "the papal curia"


GRANTED = "Granted"
REFUSED = "Refused"
COMPROMISE = "A compromise"
OVERTURNED = "Overturned"
NOT_MADE = "Not yet made"


def petition_result(petition: Petition) -> str:
    """Granted or refused; an appeal overturns, wins a compromise (above the
    original total - 3) or fails (p. 48)."""
    if not petition.made:
        return NOT_MADE
    total = petition_total(petition)
    if petition.appeal and petition.original is not None:
        if total >= petition.original + APPEAL_MARGIN:
            return OVERTURNED
        if total > petition.original - APPEAL_MARGIN:
            return COMPROMISE
        return REFUSED
    return GRANTED if total >= petition.ease else REFUSED


def petitioner_terms(character: Character, method: str) -> tuple[int, int, int]:
    """His Characteristic, Church Lore and The Gift's penalty for a
    petition made `method`'s way (The Gift only in an audience)."""
    ch = character.characteristics
    written = method != AUDIENCE
    return (
        ch.communication if written else ch.presence,
        church_lore(character),
        0 if written else gift_social_penalty(character),
    )


def petitions_this_season(career: ChurchCareer, season: str, year: int) -> int:
    """Petitions made this season: usually one only (p. 48)."""
    return sum(
        1 for p in career.petitions if p.made and p.season == season and p.year == year
    )
