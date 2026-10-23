"""Virtues and Flaws that change a season of study in ways a number on the
Advancement Total can't say: experience shared with other subjects, a
bonus or a refusal that depends on where the season is spent, subjects a
character can't learn, and a year's subjects that can't be raised twice.
Multipliers and flat bonuses are catalog data (rules.study); these are
the effects with a shape of their own, each a function keyed by its
Virtue's id.

- Secondary Insight: a season studying a Technique from a book, a teacher
  or raw vis gives 1 xp in each of 4 Forms; a Form, 1 xp in each of 2
  Techniques. The player chooses them (the plan's `insight_arts`; the
  lowest-scored when none are named); no Affinity multiplies them.
- Elemental Magic: a source dedicated to Aquam, Auram, Ignem or Terram
  gives half its Source Quality (rounded up) in each of the other three.
- Hermetic Sorcery (Realms of Power: The Infernal): studying a Goetic Art
  gives half as many xp in Rego; a supernatural Lore, half as many in Vim.
- Magian Lineage (Major): three connected Arcane or Supernatural
  Abilities; a source dedicated to one gives half its Source Quality
  (rounded up) in each of the other two, lost for a Supernatural Ability
  the character can't yet use.
- Study Bonus: +2 to a text's Quality or the vis die studying an Art in
  the presence of its substance (the plan's `art_present`). Study
  Requirement: Arts can't be studied from books or vis without it.
- Ability Block: the Abilities it names (or their category) can't be
  learned. Restricted Learning: only its five Abilities (and a Virtue's
  Supernatural ones) take experience, except from Teaching or Training.
- Master of None: an Advancement Total's xp can't go into a subject
  already raised by one this year; it is lost. Experience shared by the
  Virtues above is unaffected.

The "Source Quality" the shared experience halves is the season's
Advancement Total for its subject, so a Virtue such as Book Learner (a
text read three Quality higher) counts.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from ..arts import ART_BY_NAME, ARTS, FORMS, TECHNIQUES
from ..models import SUPERNATURAL_CATEGORIES, Character, VirtueFlawInstance
from . import creation_access as access
from .animal_grogs import restricted_choices
from .breakdown import Line
from .rounding import round_down, round_up

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Four: Virtues and Flaws "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Four:"
    "_Virtues_and_Flaws)"
)
SORCERY_SOURCE = "Realms of Power: The Infernal, Chapter 8: Goetic Sorcery"

SECONDARY_INSIGHT = "vf_secondary_insight"
ELEMENTAL_MAGIC = "vf_elemental_magic"
HERMETIC_SORCERY = "vf_hermetic_sorcery"
MAGIAN_LINEAGE = "vf_magian_lineage_major"
STUDY_BONUS = "vf_study_bonus"
STUDY_REQUIREMENT = "vf_study_requirement"
ABILITY_BLOCK = "vf_ability_block"
RESTRICTED_LEARNING = "vf_restricted_learning"
MASTER_OF_NONE = "vf_master_of_none"

#: The rules.study activities (study_total's) of a season from a book, a
#: teacher or raw vis: Secondary Insight's and Elemental Magic's sources.
BOOK_TEACHER_VIS: tuple[str, ...] = ("reading", "teaching", "vis_study")
#: Every activity that studies one subject (not Exposure or an Adventure,
#: split among several): a source "dedicated" to it.
DEDICATED: tuple[str, ...] = (*BOOK_TEACHER_VIS, "training", "practice")
#: Activities exempt from Restricted Learning.
FROM_OTHERS: tuple[str, ...] = ("teaching", "training")

STUDY_BONUS_AMOUNT = 2
#: Secondary Insight's bonus Arts: Forms for a Technique, Techniques for a Form.
INSIGHT_COUNT = {"Technique": 4, "Form": 2}
ELEMENTS: tuple[str, ...] = ("Aquam", "Auram", "Ignem", "Terram")
GOETIC_ARTS: tuple[str, ...] = ("Ablating", "Binding", "Commanding", "Summoning")
SUPERNATURAL_LORES: tuple[str, ...] = (
    "Dominion Lore",
    "Faerie Lore",
    "Infernal Lore",
    "Magic Lore",
)


def instance(character: Character, vf_id: str) -> VirtueFlawInstance | None:
    return next((vf for vf in character.virtues_flaws if vf.vf_id == vf_id), None)


def has(character: Character, vf_id: str) -> bool:
    return instance(character, vf_id) is not None


def _names(text: str) -> list[str]:
    """A parameter listing names, split on commas or semicolons."""
    return [n.strip() for n in text.replace(";", ",").split(",") if n.strip()]


# -- where the season is spent: Study Bonus and Study Requirement ------------


def needs_presence(character: Character) -> bool:
    """Whether the plan form asks if the Art's substance is present."""
    return has(character, STUDY_BONUS) or has(character, STUDY_REQUIREMENT)


def presence_lines(
    character: Character, activity: str, is_art: bool, present: bool
) -> list[Line]:
    """Study Bonus's +2, studying an Art from a book or raw vis with its
    substance present."""
    if not (present and is_art and activity in ("reading", "vis_study")):
        return []
    if not has(character, STUDY_BONUS):
        return []
    return [Line("Study Bonus (the Art present)", STUDY_BONUS_AMOUNT, source=SOURCE)]


def presence_problems(
    character: Character, activity: str, is_art: bool, present: bool
) -> list[str]:
    """Study Requirement: an Art from a book or vis only in its presence."""
    if present or not is_art or activity not in ("reading", "vis_study"):
        return []
    if not has(character, STUDY_REQUIREMENT):
        return []
    return [
        f"{character.name} has Study Requirement: an Art is studied from books "
        "or vis only in the presence of its substance (tick The Art is present)."
    ]


# -- what a character can't learn: Ability Block, Restricted Learning --------


def _blocked(character: Character, ability: str) -> bool:
    found = instance(character, ABILITY_BLOCK)
    if found is None:
        return False
    named = {n.casefold() for n in _names(found.params.get("abilities", ""))}
    category = (access.ability_category(ability) or "").casefold()
    plain = ability.split(":")[0].strip().casefold()
    return bool(named & {ability.casefold(), plain, category, f"{category} abilities"})


def restricted_to(character: Character) -> set[str] | None:
    """The Abilities Restricted Learning lets a character raise on their
    own: its five (as named, else those creation xp went on, else those
    they have) and a Virtue's Supernatural Abilities; None without it."""
    found = instance(character, RESTRICTED_LEARNING)
    if found is None:
        return None
    chosen = _names(found.params.get("chosen", ""))
    if not chosen:
        chosen = restricted_choices(
            character, [x.target for x in character.creation_xp]
        )
    if not chosen:
        chosen = [a.name for a in character.abilities]
    return {n.casefold() for n in chosen} | {
        n.casefold() for n in access.granted_supernatural(character)
    }


def learning_problems(
    character: Character, abilities: Sequence[str], activity: str
) -> list[str]:
    """Why `character` can't gain experience in these Abilities this way."""
    found: list[str] = []
    allowed = None if activity in FROM_OTHERS else restricted_to(character)
    for name in abilities:
        if _blocked(character, name):
            found.append(f"{character.name}'s Ability Block rules out learning {name}.")
        elif allowed is not None and name.casefold() not in allowed:
            found.append(
                f"{character.name}'s Restricted Learning: {name} isn't one of "
                "their five Abilities; it can only be taught or trained."
            )
    return found


# -- experience shared with other subjects -----------------------------------


@dataclass(frozen=True)
class Shared:
    """Experience a Virtue gives another subject ("art:Auram")."""

    subject: str
    xp: int
    via: str
    note: str = ""


@dataclass(frozen=True)
class Studied:
    """The season the experience is shared from."""

    character: Character
    kind: str  # "art" or "ability"
    name: str
    activity: str  # a rules.study activity
    advancement_total: int
    xp: int
    #: Secondary Insight's chosen Arts (the plan's insight_arts).
    insight_arts: Sequence[str] = ()


def _art_xp(character: Character, art: str) -> int:
    score = character.arts.get(art.lower())
    return score.xp if score else 0


def insight_pool(art: str) -> tuple[tuple[str, ...], int, str]:
    """The Arts Secondary Insight may raise studying `art`, how many, and
    what they are called: 4 Forms for a Technique, 2 Techniques for a Form."""
    if art in TECHNIQUES:
        return FORMS, INSIGHT_COUNT["Technique"], "Forms"
    return TECHNIQUES, INSIGHT_COUNT["Form"], "Techniques"


def _secondary_insight(season: Studied) -> list[Shared]:
    if season.kind != "art" or season.activity not in BOOK_TEACHER_VIS:
        return []
    pool, count, side = insight_pool(season.name)
    chosen = [
        ART_BY_NAME[a.lower()]
        for a in season.insight_arts
        if a.lower() in ART_BY_NAME and ART_BY_NAME[a.lower()] in pool
    ]
    chosen = list(dict.fromkeys(chosen))[:count]
    picked = ""
    if len(chosen) < count:
        rest = sorted(
            (a for a in pool if a not in chosen),
            key=lambda a: (_art_xp(season.character, a), ARTS.index(a)),
        )
        chosen += rest[: count - len(chosen)]
        picked = f" (the lowest {side}: name others on the plan)"
    return [
        Shared(f"art:{art}", 1, "Secondary Insight", picked if n == 0 else "")
        for n, art in enumerate(chosen)
    ]


def _elemental_magic(season: Studied) -> list[Shared]:
    if season.kind != "art" or season.name not in ELEMENTS:
        return []
    if season.activity not in BOOK_TEACHER_VIS:
        return []
    half = round_up(season.advancement_total / 2)
    return [
        Shared(f"art:{art}", half, "Elemental Magic")
        for art in ELEMENTS
        if art != season.name
    ]


def _hermetic_sorcery(season: Studied) -> list[Shared]:
    if season.kind != "ability" or season.character.type != "magus":
        return []
    if season.activity not in DEDICATED:
        return []
    if season.name in GOETIC_ARTS:
        art = "Rego"
    elif season.name in SUPERNATURAL_LORES:
        art = "Vim"
    else:
        return []
    half = round_down(season.xp / 2)
    return [Shared(f"art:{art}", half, "Hermetic Sorcery")] if half else []


def _magian_lineage(season: Studied) -> list[Shared]:
    found = instance(season.character, MAGIAN_LINEAGE)
    if found is None or season.kind != "ability":
        return []
    if season.activity not in DEDICATED:
        return []
    connected = _names(found.params.get("connected", ""))
    if season.name.casefold() not in {n.casefold() for n in connected}:
        return []
    half = round_up(season.advancement_total / 2)
    shared: list[Shared] = []
    for name in connected:
        if name.casefold() == season.name.casefold():
            continue
        if not _may_use(season.character, name):
            shared.append(
                Shared(
                    f"ability:{name}",
                    0,
                    "Magian Lineage",
                    f" {half} xp lost: not yet able to use {name}.",
                )
            )
            continue
        shared.append(Shared(f"ability:{name}", half, "Magian Lineage"))
    return shared


def _may_use(character: Character, name: str) -> bool:
    """A Supernatural Ability takes experience only once the character has
    access to it (a Virtue, or the Ability already); other Abilities may
    be begun."""
    if access.ability_category(name) not in SUPERNATURAL_CATEGORIES:
        return True
    return any(a.name.casefold() == name.casefold() for a in character.abilities) or (
        name in access.granted_supernatural(character)
    )


#: Each Virtue that shares a season's experience, and how (Strategy, as a
#: dict of functions).
SHARING: dict[str, Callable[[Studied], list[Shared]]] = {
    SECONDARY_INSIGHT: _secondary_insight,
    ELEMENTAL_MAGIC: _elemental_magic,
    HERMETIC_SORCERY: _hermetic_sorcery,
    MAGIAN_LINEAGE: _magian_lineage,
}


def shared(season: Studied) -> list[Shared]:
    """Every subject the character's Virtues share this season's study with."""
    found: list[Shared] = []
    for vf_id, share in SHARING.items():
        if has(season.character, vf_id):
            found += share(season)
    return found


def shows_insight(character: Character) -> bool:
    """Whether the plan form asks which Arts Secondary Insight raises."""
    return has(character, SECONDARY_INSIGHT)


# -- Master of None -----------------------------------------------------------


def raised_this_year(character: Character, year: int) -> set[str]:
    """Subjects an Advancement Total has raised this year (Master of None)."""
    return {s for s, y in character.advanced.items() if y == year}


def record_raised(character: Character, subjects: Sequence[str], year: int) -> None:
    """Note the subjects an applied season's Advancement Totals raised, for
    a character with Master of None."""
    if not has(character, MASTER_OF_NONE):
        return
    for subject in subjects:
        character.advanced[subject] = year
