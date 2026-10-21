"""Creation xp, step by step: what each step's xp may
buy and how much there is, and the checks on what the character spent
(Character.creation_xp, which the worksheet also adds to the Abilities).

- Early Childhood: 75 xp in the Native Language and 45 xp over a fixed
  list (§3 Early childhood experience). Covenant Upbringing adds Latin
  and Order of Hermes Lore to the list (the Grogs Covenant-bred
  childhood); Feral Upbringing has no Language and 120 xp over what the
  wilds teach (DE: no Language score; Grogs: the Feral childhood).

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
FERAL_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Four: Virtues and Flaws, Feral "
    "Upbringing (https://www.redcap.org/page/Ars_Magica_Definitive_Edition,"
    "_Chapter_Four:_Virtues_and_Flaws#Feral_Upbringing)"
)
SAMPLE_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Sample "
    "Childhoods (https://www.redcap.org/page/Ars_Magica_Definitive_Edition,"
    "_Chapter_Three:_Characters#Sample_Childhoods)"
)

NATIVE = "native"
NATIVE_XP = 75
CHILDHOOD_XP = 45
#: A feral child learns no Language, and spends what would have gone into
#: it on the wilds.
FERAL_CHILDHOOD_XP = 120
COVENANT_UPBRINGING = "vf_covenant_upbringing"
FERAL_UPBRINGING = "vf_feral_upbringing"
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
#: What an Upbringing adds to the childhood Abilities.
UPBRINGING_ABILITIES: dict[str, tuple[str, ...]] = {
    COVENANT_UPBRINGING: (
        "Dead Language: Latin",
        "Organization Lore: Order of Hermes",
    ),
    FERAL_UPBRINGING: ("Animal Handling", "Hunt"),
}


@dataclass(frozen=True)
class Childhood:
    """A sample childhood: the 45 xp, as (Ability, xp). "{area}" and
    "{language}" are filled in when it's applied."""

    name: str
    xp: tuple[tuple[str, int], ...]
    #: The book it's from (sourcebooks), when not the core book.
    book: str = "DE"
    #: The Virtue or Flaw a character needs to take it ("" for none).
    needs: str = ""


#: The DE sample childhoods, then the Grogs and Apprentices ones (each 45
#: xp on top of the Native Language, except Feral's 120 with none).
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
    Childhood(
        "Covenant-bred",
        (
            ("Athletics", 5),
            ("Area Lore: Covenant", 15),
            ("Folk Ken", 5),
            ("Dead Language: Latin", 15),
            ("Organization Lore: Order of Hermes", 5),
        ),
        "Grogs",
        COVENANT_UPBRINGING,
    ),
    Childhood(
        "Feral",
        (
            ("Animal Handling", 5),
            ("Area Lore: {area}", 15),
            ("Athletics", 15),
            ("Awareness", 15),
            ("Brawl", 15),
            ("Hunt", 15),
            ("Stealth", 5),
            ("Survival", 30),
            ("Swim", 5),
        ),
        "Grogs",
        FERAL_UPBRINGING,
    ),
)


def _held(character: Character | None, vf_id: str) -> bool:
    return character is not None and any(
        vf.vf_id == vf_id for vf in character.virtues_flaws
    )


def childhoods_in_play(
    saga: Saga, character: Character | None = None
) -> list[Childhood]:
    """The sample childhoods from the books in play; with `character`,
    only those it may take (an Upbringing's own childhood needs it)."""
    books = sourcebooks.saga_books(saga)
    return [
        c
        for c in CHILDHOODS
        if sourcebooks.in_play(c.book, books)
        and (character is None or not c.needs or _held(character, c.needs))
    ]


def feral(character: Character) -> bool:
    return _held(character, FERAL_UPBRINGING)


def childhood_xp(character: Character) -> int:
    """The childhood xp besides the Native Language: Feral's 120 has none."""
    return FERAL_CHILDHOOD_XP if feral(character) else CHILDHOOD_XP


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


def _upbringing_abilities(character: Character | None) -> list[str]:
    return [
        name
        for vf_id, names in UPBRINGING_ABILITIES.items()
        if _held(character, vf_id)
        for name in names
    ]


def childhood_targets(character: Character | None = None) -> list[str]:
    """What the worksheet offers for the childhood xp: a feral child no
    Language, an Upbringing's own Abilities added."""
    language = (
        []
        if character is not None and feral(character)
        else ["Living Language: {language}"]
    )
    return [
        *CHILDHOOD_ABILITIES,
        *_upbringing_abilities(character),
        "Area Lore: {region}",
        *language,
    ]


def entries(character: Character, step: str) -> list[CreationXp]:
    return [x for x in character.creation_xp if x.step == step]


def spent(character: Character, step: str, *, note: str | None = None) -> int:
    return sum(x.xp for x in entries(character, step) if note is None or x.note == note)


def is_art(target: str) -> bool:
    return target in ARTS


def childhood_allows(target: str, character: Character | None = None) -> bool:
    if (
        character is not None
        and feral(character)
        and target.startswith(LIVING_LANGUAGE)
    ):
        return False
    return (
        target in CHILDHOOD_ABILITIES
        or target in _upbringing_abilities(character)
        or target.startswith(CHILDHOOD_FAMILIES)
    )


def _check(
    label: str, ok: bool, detail: str, *, advice: bool = False, source: str = SOURCE
) -> Check:
    status = "pass" if ok else ("advice" if advice else "warn")
    return Check("childhood", label, status, detail, source)


@check("childhood", CHARACTER_CHECKS)
def childhood_checks(saga: Saga, record: Record) -> list[Check]:
    assert isinstance(record, Character)
    character = record
    natives = [x for x in entries(character, "childhood") if x.note == NATIVE]
    others = [x for x in entries(character, "childhood") if x.note != NATIVE]
    if feral(character):
        found = [
            _check(
                "No Language (Feral Upbringing)",
                not natives,
                natives[0].target if natives else "none",
                source=FERAL_SOURCE,
            )
        ]
    else:
        found = [
            _check(
                f"{NATIVE_XP} xp in the Native Language",
                len(natives) == 1 and natives[0].xp == NATIVE_XP,
                natives[0].target if len(natives) == 1 else f"{len(natives)} set",
            )
        ]
    budget = childhood_xp(character)
    total = sum(x.xp for x in others)
    found.append(
        _check(
            f"At most {budget} more xp",
            total <= budget,
            f"{total} spent"
            + (f", {total - budget} too many" if total > budget else ""),
        )
    )
    if total < budget:
        found.append(
            _check(
                "Childhood xp spent",
                False,
                f"{budget - total} unspent",
                advice=True,
            )
        )
    wrong = sorted(
        {x.target for x in others if not childhood_allows(x.target, character)}
    )
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
