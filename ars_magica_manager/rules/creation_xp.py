"""Creation xp, step by step (STORY-1306 to 1308): what each step's xp may
buy and how much there is, and the checks on what the character spent
(Character.creation_xp, which the worksheet also adds to the Abilities).

- Early Childhood: 75 xp in the Native Language and 45 xp over a fixed
  list (§3 Early childhood experience).

Rules: reference/rules-engine-reference.md §3.
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import sourcebooks
from ..arts import ARTS
from ..models import Character, CreationXp, Saga
from .creation_base import CHARACTER_CHECKS, Check, Record, check

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Early Childhood "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Three:"
    "_Characters#Early_Childhood)"
)
SAMPLE_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Sample "
    "Childhoods (https://www.redcap.org/page/Ars_Magica_Definitive_Edition,"
    "_Chapter_Three:_Characters#Sample_Childhoods)"
)

NATIVE = "native"
NATIVE_XP = 75
CHILDHOOD_XP = 45
LIVING_LANGUAGE = "Living Language: "
AREA_LORE = "Area Lore: "
JUDAIC_LORE = "Judaic Lore"

#: What the 45 childhood xp may buy: exact names, and name prefixes for an
#: Ability family (a second Living Language, any Area Lore).
CHILDHOOD_ABILITIES: tuple[str, ...] = (
    "Athletics",
    "Awareness",
    "Brawl",
    "Charm",
    "Folk Ken",
    "Guile",
    "Stealth",
    "Survival",
    "Swim",
    # For a Jewish character.
    "Judaic Lore",
)
CHILDHOOD_FAMILIES: tuple[str, ...] = (AREA_LORE, LIVING_LANGUAGE)


@dataclass(frozen=True)
class Childhood:
    """A sample childhood: the 45 xp, as (Ability, xp). "{area}" and
    "{language}" are filled in when it's applied."""

    name: str
    xp: tuple[tuple[str, int], ...]
    #: The book it's from (sourcebooks), when not the core book.
    book: str = "DE"


#: The DE sample childhoods, then the Grogs and Apprentices ones (each 45
#: xp on top of the Native Language, except where marked).
CHILDHOODS: tuple[Childhood, ...] = (
    Childhood("Athletic", (("Athletics", 15), ("Brawl", 15), ("Swim", 15))),
    Childhood(
        "Exploring",
        (
            ("Area Lore: {area}", 15),
            ("Athletics", 5),
            ("Awareness", 5),
            ("Stealth", 5),
            ("Survival", 15),
        ),
    ),
    Childhood("Mischievous", (("Brawl", 15), ("Guile", 15), ("Stealth", 15))),
    Childhood("Social", (("Charm", 15), ("Folk Ken", 15), ("Guile", 15))),
    Childhood(
        "Traveling",
        (
            ("Area Lore: {area}", 5),
            ("Area Lore: {second_area}", 5),
            ("Folk Ken", 15),
            ("Living Language: {language}", 5),
            ("Survival", 15),
        ),
    ),
    Childhood(
        "Border",
        (
            ("Area Lore: {area}", 5),
            ("Area Lore: {second_area}", 5),
            ("Folk Ken", 5),
            ("Living Language: {language}", 30),
        ),
        "App",
    ),
    Childhood(
        "Fighting",
        (("Awareness", 5), ("Athletics", 5), ("Brawl", 30), ("Guile", 5)),
        "App",
    ),
    Childhood("Shy", (("Awareness", 15), ("Stealth", 30)), "App"),
    Childhood(
        "Wilderness",
        (("Athletics", 5), ("Awareness", 5), ("Survival", 30), ("Swim", 5)),
        "App",
    ),
)


def childhoods_in_play(saga: Saga) -> list[Childhood]:
    books = sourcebooks.saga_books(saga)
    return [c for c in CHILDHOODS if sourcebooks.in_play(c.book, books)]


def childhood_label(childhood: Childhood) -> str:
    """ "Athletic: Athletics 15, Brawl 15, Swim 15"."""
    parts = ", ".join(
        f"{name.replace('{', '(').replace('}', ')')} {xp}" for name, xp in childhood.xp
    )
    return f"{childhood.name}: {parts}"


XpRows = tuple[tuple[str, int], ...]


def template_blanks(rows: XpRows) -> list[str]:
    """The names a set of (Ability, xp) asks for ("area", "language"), in
    order: the blanks in "Area Lore: {area}"."""
    blanks: list[str] = []
    for name, _ in rows:
        if "{" in name:
            blank = name.split("{", 1)[1].rstrip("}")
            if blank not in blanks:
                blanks.append(blank)
    return blanks


def fill_template(rows: XpRows, values: dict[str, str]) -> list[tuple[str, int]]:
    """(Ability, xp) with the blanks filled from `values`."""
    filled = []
    for name, xp in rows:
        for blank, value in values.items():
            name = name.replace("{" + blank + "}", value.strip())
        filled.append((name, xp))
    return filled


def childhood_blanks(childhood: Childhood) -> list[str]:
    return template_blanks(childhood.xp)


def fill_childhood(
    childhood: Childhood, values: dict[str, str]
) -> list[tuple[str, int]]:
    return fill_template(childhood.xp, values)


def childhood_targets() -> list[str]:
    """What the worksheet offers for the 45 childhood xp."""
    return [*CHILDHOOD_ABILITIES, "Area Lore: {region}", "Living Language: {language}"]


def entries(character: Character, step: str) -> list[CreationXp]:
    return [x for x in character.creation_xp if x.step == step]


def spent(character: Character, step: str, *, note: str | None = None) -> int:
    return sum(x.xp for x in entries(character, step) if note is None or x.note == note)


def is_art(target: str) -> bool:
    return target in ARTS


def childhood_allows(target: str) -> bool:
    return target in CHILDHOOD_ABILITIES or target.startswith(CHILDHOOD_FAMILIES)


def _check(label: str, ok: bool, detail: str, *, advice: bool = False) -> Check:
    status = "pass" if ok else ("advice" if advice else "warn")
    return Check("childhood", label, status, detail, SOURCE)


@check("childhood", CHARACTER_CHECKS)
def childhood_checks(saga: Saga, record: Record) -> list[Check]:
    assert isinstance(record, Character)
    character = record
    natives = [x for x in entries(character, "childhood") if x.note == NATIVE]
    others = [x for x in entries(character, "childhood") if x.note != NATIVE]
    found = [
        _check(
            f"{NATIVE_XP} xp in the Native Language",
            len(natives) == 1 and natives[0].xp == NATIVE_XP,
            natives[0].target if len(natives) == 1 else f"{len(natives)} set",
        )
    ]
    total = sum(x.xp for x in others)
    found.append(
        _check(
            f"At most {CHILDHOOD_XP} more xp",
            total <= CHILDHOOD_XP,
            f"{total} spent"
            + (f", {total - CHILDHOOD_XP} too many" if total > CHILDHOOD_XP else ""),
        )
    )
    if total < CHILDHOOD_XP:
        found.append(
            _check(
                "Childhood xp spent",
                False,
                f"{CHILDHOOD_XP - total} unspent",
                advice=True,
            )
        )
    wrong = sorted({x.target for x in others if not childhood_allows(x.target)})
    if wrong:
        found.append(_check("Only the childhood Abilities", False, ", ".join(wrong)))
    if any(x.target == JUDAIC_LORE for x in others):
        # Not enforced (the app doesn't know who is Jewish): a reminder.
        found.append(
            _check(
                "Judaic Lore is for Jewish characters, unless the storyguide approves",
                False,
                "Judaic Lore taken",
                advice=True,
            )
        )
    languages = {x.target for x in others if x.target.startswith(LIVING_LANGUAGE)} - {
        x.target for x in natives
    }
    if len(languages) > 1:
        found.append(
            _check(
                "One second Living Language",
                False,
                f"{len(languages)}: " + ", ".join(sorted(languages)),
            )
        )
    return found
