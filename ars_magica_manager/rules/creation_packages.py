"""Grogs training packages: a quick build for Later Life when
the Grogs book is in play. A package gives fixed xp for 3 or 5 years of
the character's life; the years left over are bought at the usual xp a
year. Wealthy characters take 3/4 of the package years in age, Poor ones
1.5 times; an Affinity with an Ability adds half again to the package's
xp in it. No more than 15 years in one package, a package marked
(Academic), (Arcane) or (Martial) needs a Virtue opening that type, and
Failed Apprentice needs that Virtue.

The worksheet records a package's xp as "package" entries whose note names
the package, its length and which time it was taken ("Soldier:5:1").

Rules: reference/rules-engine-reference.md §3 Training packages (Grogs).
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import catalog, sourcebooks
from ..models import Character, Saga
from . import creation_access as access
from .creation_base import CHARACTER_CHECKS, Check, Record, check
from .creation_character import later_life_years
from .creation_xp import entries
from .rounding import round_up

SOURCE = "Grogs, Chapter 5, Training Packages, p. 67"

MAX_YEARS_IN_ONE = 15
_LATIN = "Dead Language: Latin"
_AREA = "Area Lore: {area}"
_ORG = "Organization Lore: {organization}"
_CHURCH = "Organization Lore: Church"
_OOH = "Organization Lore: Order of Hermes"


@dataclass(frozen=True)
class Package:
    name: str
    #: The Ability type it needs a Virtue for ("" for none).
    needs: str
    five: tuple[tuple[str, int], ...] = ()
    three: tuple[tuple[str, int], ...] = ()
    #: The Virtue a character must have to take it ("" for none).
    virtue: str = ""
    #: What the 5- and 3-year packages give besides xp, for the label.
    extra: tuple[str, str] = ("", "")


#: The Grogs book's career and background packages. Where the book offers
#: a choice ("Carouse or Etiquette") the first is used; change it after.
PACKAGES: tuple[Package, ...] = (
    Package(
        "Advocate",
        "Academic",
        (
            ("Civil and Canon Law", 40),
            ("Leadership", 5),
            ("Artes Liberales", 15),
            (_LATIN, 15),
        ),
        (
            ("Civil and Canon Law", 30),
            ("Leadership", 5),
            ("Artes Liberales", 5),
            (_LATIN, 5),
        ),
    ),
    Package(
        "Animal Trainer",
        "",
        (("Animal Handling", 30), ("Profession: Animal Trainer", 30), ("Ride", 15)),
        (("Animal Handling", 30), ("Ride", 15)),
    ),
    Package(
        "Apothecary",
        "",
        ((_AREA, 15), ("Chirurgy", 20), ("Profession: Apothecary", 40)),
        ((_AREA, 5), ("Chirurgy", 10), ("Profession: Apothecary", 30)),
    ),
    Package(
        "Archer",
        "Martial",
        (("Awareness", 20), ("Bows", 40), ("Concentration", 15)),
        (("Awareness", 15), ("Bows", 30)),
    ),
    Package(
        "Churchman",
        "Academic",
        (
            ("Artes Liberales", 10),
            (_CHURCH, 30),
            (_LATIN, 5),
            ("Civil and Canon Law", 30),
        ),
        (("Artes Liberales", 5), (_CHURCH, 20), ("Civil and Canon Law", 20)),
    ),
    Package(
        "Conman",
        "",
        (("Charm", 15), ("Guile", 30), ("Intrigue", 30)),
        (("Charm", 15), ("Guile", 15), ("Intrigue", 15)),
    ),
    Package(
        "Courtier",
        "",
        (("Charm", 15), ("Etiquette", 30), ("Folk Ken", 15), ("Intrigue", 15)),
        (("Charm", 5), ("Etiquette", 30), ("Folk Ken", 5), ("Intrigue", 5)),
    ),
    Package(
        "Craftsman",
        "",
        (
            ("Bargain", 10),
            ("Craft: {craft}", 25),
            ("Craft: {second_craft}", 15),
            ("Organization Lore: Guild", 15),
            ("Folk Ken", 10),
        ),
        (
            ("Bargain", 10),
            ("Craft: {craft}", 15),
            ("Craft: {second_craft}", 10),
            ("Organization Lore: Guild", 5),
            ("Folk Ken", 5),
        ),
    ),
    Package(
        "Cultist",
        "Arcane",
        (("Guile", 15), ("Infernal Lore", 50), ("Stealth", 10)),
        (("Guile", 15), ("Infernal Lore", 30)),
    ),
    Package(
        "Cunning Man",
        "Arcane",
        three=((_AREA, 10), ("Bargain", 5), ("Faerie Lore", 30)),
    ),
    Package("Cutter", "", three=(("Chirurgy", 40), ("Folk Ken", 5))),
    Package(
        "Failed Apprentice",
        "",
        (
            ("Artes Liberales", 5),
            ("Code of Hermes", 5),
            ("Concentration", 5),
            ("Finesse", 5),
            (_LATIN, 10),
            ("Magic Theory", 25),
            (_OOH, 15),
            ("Penetration", 5),
        ),
        (
            ("Concentration", 5),
            (_LATIN, 10),
            ("Magic Theory", 20),
            (_OOH, 5),
            ("Penetration", 5),
        ),
        virtue="vf_failed_apprentice",
    ),
    Package(
        "Farmer",
        "",
        (
            ("Animal Handling", 15),
            (_AREA, 15),
            ("Folk Ken", 5),
            ("Profession: Farmer", 40),
        ),
        (("Animal Handling", 10), ("Folk Ken", 5), ("Profession: Farmer", 30)),
    ),
    Package(
        "Fisherman",
        "",
        (
            (_AREA, 15),
            ("Profession: Fisherman", 30),
            ("Survival", 15),
            ("Swim", 15),
        ),
        ((_AREA, 5), ("Profession: Fisherman", 20), ("Survival", 5), ("Swim", 15)),
    ),
    Package(
        "Footpad",
        "",
        (("Athletics", 15), ("Guile", 15), ("Legerdemain", 15), ("Stealth", 30)),
        (("Athletics", 5), ("Guile", 5), ("Legerdemain", 15), ("Stealth", 20)),
    ),
    Package(
        "Harlot",
        "",
        (("Charm", 30), ("Carouse", 30), (_ORG, 15)),
        (("Charm", 20), ("Carouse", 20), (_ORG, 5)),
    ),
    Package(
        "Herbwife",
        "",
        (
            (_AREA, 10),
            ("Chirurgy", 30),
            ("Folk Ken", 5),
            ("Profession: Apothecary", 30),
        ),
        ((_AREA, 5), ("Chirurgy", 30), ("Profession: Apothecary", 10)),
    ),
    Package(
        "Javeliner",
        "Martial",
        (("Athletics", 20), ("Awareness", 15), ("Thrown Weapon", 40)),
        (("Athletics", 10), ("Awareness", 5), ("Thrown Weapon", 30)),
    ),
    Package(
        "Laborer",
        "",
        (("Athletics", 20), ("Brawl", 15), ("Profession: Laborer", 40)),
        (("Athletics", 10), ("Brawl", 5), ("Profession: Laborer", 30)),
    ),
    Package(
        "Lay Brother",
        "",
        ((_CHURCH, 50), ("Folk Ken", 10), ("Profession: {profession}", 15)),
        ((_CHURCH, 30), ("Profession: {profession}", 15)),
    ),
    Package(
        "Magician",
        "Arcane",
        (("Concentration", 15), ("Magic Lore", 30), ("Penetration", 30)),
        (("Concentration", 15), ("Magic Lore", 15), ("Penetration", 15)),
    ),
    Package(
        "Minstrel",
        "",
        (("Carouse", 15), ("Charm", 5), ("Folk Ken", 5), ("Music", 50)),
        (("Carouse", 15), ("Music", 30)),
    ),
    Package(
        "Mystic",
        "Arcane",
        (("Concentration", 20), (_CHURCH, 5), ("Dominion Lore", 30), ("Survival", 20)),
        (("Concentration", 10), ("Dominion Lore", 20), ("Survival", 15)),
    ),
    Package(
        "Natural Philosopher",
        "Academic",
        (("Philosophiae", 40),),
        (("Philosophiae", 30),),
        extra=("7 formulae", "3 formulae"),
    ),
    Package(
        "Pikeman",
        "Martial",
        (("Athletics", 20), ("Awareness", 15), ("Great Weapon", 40)),
        (("Athletics", 10), ("Awareness", 5), ("Great Weapon", 30)),
    ),
    Package(
        "Physician",
        "Academic",
        (("Folk Ken", 15), ("Medicine", 40), ("Profession: Apothecary", 20)),
        (("Folk Ken", 5), ("Medicine", 30), ("Profession: Apothecary", 10)),
    ),
    Package(
        "Public Official",
        "",
        ((_AREA, 15), ("Intrigue", 15), ("Leadership", 15), (_ORG, 30)),
        ((_AREA, 10), ("Intrigue", 10), ("Leadership", 10), (_ORG, 15)),
    ),
    Package(
        "Sailor",
        "",
        (
            (_AREA, 15),
            ("Area Lore: {second_area}", 10),
            ("Profession: Sailor", 30),
            ("Survival", 5),
            ("Swim", 15),
        ),
        ((_AREA, 5), ("Profession: Sailor", 20), ("Survival", 5), ("Swim", 15)),
    ),
    Package(
        "Scout",
        "",
        ((_AREA, 15), ("Awareness", 30), ("Stealth", 30)),
        ((_AREA, 15), ("Awareness", 15), ("Stealth", 15)),
    ),
    Package(
        "Scribe",
        "Academic",
        (("Artes Liberales", 20), (_LATIN, 15), ("Profession: Scribe", 40)),
        (("Artes Liberales", 10), (_LATIN, 10), ("Profession: Scribe", 25)),
    ),
    Package(
        "Sentry",
        "Martial",
        (("Awareness", 30), ("Concentration", 15), ("Single Weapon", 30)),
        (("Awareness", 20), ("Concentration", 5), ("Single Weapon", 20)),
    ),
    Package(
        "Servant",
        "",
        (("Folk Ken", 15), (_ORG, 20), ("Profession: Servant", 40)),
        (("Folk Ken", 10), (_ORG, 5), ("Profession: Servant", 30)),
    ),
    Package(
        "Soldier",
        "Martial",
        (("Athletics", 15), ("Brawl", 20), ("Single Weapon", 40)),
        (("Athletics", 5), ("Brawl", 10), ("Single Weapon", 30)),
    ),
    Package(
        "Storyteller",
        "",
        (
            ("Guile", 15),
            ("Carouse", 5),
            ("Folk Ken", 5),
            ("Profession: Storyteller", 50),
        ),
        (("Guile", 15), ("Profession: Storyteller", 30)),
    ),
    Package(
        "Student (cathedral school)",
        "Academic",
        (
            ("Artes Liberales", 15),
            (_LATIN, 30),
            ("Theology: Christian", 15),
            ("Civil and Canon Law", 15),
        ),
    ),
    Package(
        "Student (monastic school)",
        "Academic",
        (
            ("Artes Liberales", 15),
            (_LATIN, 30),
            ("Theology: Christian", 15),
            ("Medicine", 15),
        ),
    ),
    Package(
        "Student (private tutor or university)",
        "Academic",
        (
            ("Artes Liberales", 15),
            (_LATIN, 30),
            ("{academic_ability}", 30),
        ),
    ),
    Package(
        "Student (parish school)",
        "Academic",
        three=(("Artes Liberales", 15), (_LATIN, 30)),
    ),
    Package(
        "Teacher",
        "Academic",
        (
            ("Artes Liberales", 15),
            ("Folk Ken", 5),
            ("Living Language: {language}", 15),
            ("Teaching", 40),
        ),
    ),
    Package(
        "Tinker",
        "",
        (
            (_AREA, 15),
            ("Area Lore: {second_area}", 15),
            ("Bargain", 15),
            ("Craft: {craft}", 15),
            ("Survival", 15),
        ),
        ((_AREA, 15), ("Craft: {craft}", 15), ("Survival", 15)),
    ),
    Package(
        "Theologian",
        "Academic",
        (
            ("Civil and Canon Law", 15),
            (_CHURCH, 15),
            (_LATIN, 5),
            ("Theology: Christian", 40),
        ),
        (
            ("Civil and Canon Law", 5),
            (_CHURCH, 5),
            (_LATIN, 5),
            ("Theology: Christian", 30),
        ),
    ),
    Package(
        "Trader",
        "",
        (("Bargain", 30), ("Folk Ken", 15), ("Profession: Merchant", 30)),
        (("Bargain", 20), ("Folk Ken", 5), ("Profession: Merchant", 20)),
    ),
    Package(
        "Tumbler",
        "",
        (("Athletics", 50), ("Carouse", 10), ("Legerdemain", 15)),
        (("Athletics", 30), ("Carouse", 5), ("Legerdemain", 10)),
    ),
    Package(
        "Woodsman",
        "",
        ((_AREA, 15), ("Hunt", 30), ("Stealth", 15), ("Survival", 15)),
        ((_AREA, 5), ("Hunt", 20), ("Stealth", 5), ("Survival", 15)),
    ),
    # Background (non-career) packages: three years each.
    Package(
        "Athlete", "", three=(("Athletics", 30), ("Brawl", 5), ("Ride", 5), ("Swim", 5))
    ),
    Package("Brawler", "", three=(("Athletics", 15), ("Brawl", 30))),
    Package(
        "Charmer",
        "",
        three=(("Charm", 30), ("Folk Ken", 5), ("Guile", 5), ("Intrigue", 5)),
    ),
    Package(
        "Covenfolk",
        "",
        three=(
            (_AREA, 5),
            ("Area Lore: Covenant", 20),
            (_LATIN, 15),
            (_OOH, 5),
        ),
    ),
    Package("Forager", "", three=((_AREA, 15), ("Hunt", 15), ("Survival", 15))),
    Package("Leader", "", three=(("Folk Ken", 10), ("Charm", 5), ("Leadership", 30))),
    Package("Local", "", three=((_AREA, 15), ("Folk Ken", 15), (_ORG, 15))),
    Package("Rider", "", three=(("Animal Handling", 15), ("Ride", 30))),
    Package(
        "Trainer",
        "",
        three=(
            ("Folk Ken", 5),
            ("Living Language: {language}", 5),
            ("Leadership", 5),
            ("Teaching", 30),
        ),
    ),
    Package(
        "Wastrel",
        "",
        three=(("Brawl", 5), ("Carouse", 30), ("Folk Ken", 5), ("Guile", 5)),
    ),
)


def offered(saga: Saga, character: Character) -> bool:
    """Packages are offered to grogs and companions, and a magus's years
    before apprenticeship, when the Grogs book is in play; never to an
    animal grog, whose Abilities are too few for them."""
    if character.animal is not None:
        return False
    return sourcebooks.in_play("Grogs", sourcebooks.saga_books(saga))


@dataclass(frozen=True)
class Taken:
    """A package taken: its name, length and which time (a note's parts)."""

    name: str
    years: int
    time: int

    @property
    def note(self) -> str:
        return f"{self.name}:{self.years}:{self.time}"

    @staticmethod
    def parse(note: str) -> Taken:
        name, years, time = note.rsplit(":", 2)
        return Taken(name, int(years), int(time))


def taken(character: Character) -> list[Taken]:
    """Every package the character has taken, in order."""
    seen: dict[str, Taken] = {}
    for entry in entries(character, "package"):
        seen.setdefault(entry.note, Taken.parse(entry.note))
    return list(seen.values())


def age_multiplier(character: Character) -> float:
    """How many years of age a package year takes: Wealthy 3/4, Poor 1.5."""
    ids = {vf.vf_id for vf in character.virtues_flaws}
    if "vf_wealthy" in ids:
        return 0.75
    if "vf_poor" in ids:
        return 1.5
    return 1.0


def years_used(character: Character) -> int:
    """The Later Life years the packages take (rounded up)."""
    total = sum(t.years for t in taken(character))
    return round_up(total * age_multiplier(character))


def package_xp(package: Package, years: int) -> list[tuple[str, int]]:
    """The package's xp for its `years` (an Affinity's half again is added
    as the xp is spent, like any creation xp)."""
    return list(package.five if years == 5 else package.three)


def package_label(package: Package, years: int) -> str:
    """ "Soldier (Martial), 5 years: Athletics 15, Brawl 20, Single Weapon 40"."""
    rows = package.five if years == 5 else package.three
    needs = f" ({package.needs})" if package.needs else ""
    parts = [f"{name.replace('{', '(').replace('}', ')')} {xp}" for name, xp in rows]
    extra = package.extra[0 if years == 5 else 1]
    if extra:
        parts.append(extra)
    return f"{package.name}{needs}, {years} years: {', '.join(parts)}"


def next_time(character: Character, name: str) -> int:
    return 1 + sum(1 for t in taken(character) if t.name == name)


def _check(label: str, ok: bool, detail: str) -> Check:
    return Check("later_life", label, "pass" if ok else "warn", detail, SOURCE)


@check("later_life", CHARACTER_CHECKS)
def package_checks(saga: Saga, record: Record) -> list[Check]:
    assert isinstance(record, Character)
    character = record
    found_taken = taken(character)
    if not found_taken:
        return []
    years = later_life_years(saga, character)
    used = years_used(character)
    found = [
        _check(
            "Training packages fit in Later Life",
            used <= years,
            f"{used} of {years} years",
        )
    ]
    by_name = {p.name: p for p in PACKAGES}
    totals: dict[str, int] = {}
    for t in found_taken:
        totals[t.name] = totals.get(t.name, 0) + t.years
    for name, total in totals.items():
        if total > MAX_YEARS_IN_ONE:
            found.append(
                _check(
                    f"At most {MAX_YEARS_IN_ONE} years in {name}",
                    False,
                    f"{total} years",
                )
            )
        package = by_name.get(name)
        if package is not None and package.virtue:
            held = any(vf.vf_id == package.virtue for vf in character.virtues_flaws)
            virtue = catalog.load_virtue_flaw_catalog_by_id()[package.virtue].name
            found.append(
                _check(
                    f"{name} needs the {virtue} Virtue",
                    held,
                    "taken" if held else "not taken",
                )
            )
        if package is not None and package.needs:
            ok = package.needs in access.opened_types(character)
            found.append(
                _check(
                    f"{name} needs a Virtue opening {package.needs} Abilities",
                    ok,
                    "opened" if ok else "not opened",
                )
            )
    return found
