"""Pilgrimage: its Target Level, the Oppositional Elements a pilgrim must
overcome to reach it, and the aim it grants once reached.

- The aim sets the Target Level (The Church p. 16): 18 for a minor
  pilgrimage (a Minor Virtue, Divine Minor Supernatural Abilities among
  them; a Minor Flaw lost, or a Virtue; a negative Personality Trait
  removed; a penance met), 30 for a major one (a Major Virtue, Divine
  Methods and Powers among them; a Major Flaw lost; a miracle asked; self-
  initiation in Holy Magic, which needs True Faith; a penance met). A
  minor pilgrimage is a single season and story; a major one takes several.
  No pilgrimage grants or removes Hermetic Virtues and Flaws, nor
  background ones such as Privileged Upbringing and Educated: the app
  reads "background" as every Virtue that gives experience at creation
  (creation_access.VIRTUE_XP), the book naming only those two. A Divine
  Supernatural Ability gained this way starts at 1, without the Gift's
  penalty. The aim needs the troupe's agreement that it suits.
- A negative Personality Trait (p. 16) isn't defined there; p. 20 reads a
  trait opposed to a temper as that temper at minus its score. So the app
  offers a trait with a negative score, or one the sin table
  (rules.sin) reads as leaning toward a sin; any other is the troupe's
  call, outside the form.
- Oppositional Elements (pp. 16-18): each pilgrim must personally overcome
  elements whose values total at least the Target Level. Each season on
  pilgrimage is +3 (the season's own work, season_work.church); others are
  +3, +6, +9 or +12, as the table gives. Travel through a Christian land
  outside his homeland (+3) or through non-Christian or heretic lands (+6)
  counts once for the whole pilgrimage, only the higher. An element failed
  fails the aim, unless a later element he overcomes remedies it.
- He must avoid mortal sin on the road, and confess his venial sins on
  arrival (p. 18).
- Pilgrimage and Devotion (p. 19): a pilgrimage to a saint's shrine gives
  10 Devotion Points, +5 a further site of the saint's life visited, and up
  to 5 more for relics seen.
- Taking the Cross (p. 19): a crusader gains one temporary Faith Point and
  may lose a Social Status Flaw at the troupe's discretion.

Records: the pilgrimage itself is a Progress record (kind "pilgrimage",
its points the elements overcome); its story so far -- the travel element
counted and the failures not yet remedied -- is a second, finished record
of kind "pilgrimage_story" with the same name (its target the travel
value counted, its points the failures outstanding), and a claimed aim
renames the pilgrimage's kind to "pilgrimage_claimed" so it is claimed
once.

Pattern: functions over Progress records (the multi-season work's
record), the season itself the activity registry's Strategy.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .. import catalog
from ..models import (
    SUPERNATURAL_CATEGORIES,
    Ability,
    Character,
    Progress,
    ScoredTrait,
    VirtueFlawDef,
    VirtueFlawInstance,
)
from . import creation_access, sin
from .xp import xp_for_score

SOURCE = "The Church, Chapter 1: Faith, Pilgrimages, pp. 15-19"

KIND = "pilgrimage"
STORY_KIND = "pilgrimage_story"
CLAIMED_KIND = "pilgrimage_claimed"
MINOR, MAJOR = 18, 30
TARGETS = (MINOR, MAJOR)
#: Each season spent on pilgrimage (p. 17).
SEASON_VALUE = 3
#: Travel elements (p. 17): only the higher counts, once.
CHRISTIAN_ABROAD, HEATHEN_LANDS = "christian_abroad", "heathen_lands"
TRAVEL: dict[str, int] = {CHRISTIAN_ABROAD: 3, HEATHEN_LANDS: 6}

#: Pilgrimage and Devotion (p. 19).
SHRINE_DEVOTION = 10
SITE_DEVOTION = 5
MOST_RELIC_DEVOTION = 5
#: Taking the Cross (p. 19): temporary Faith Points.
CRUSADER_FAITH = 1

#: The Virtue and Flaw types a pilgrimage may grant or take away (p. 16).
LOSABLE_TYPES = ("Story", "General", "Social Status", "Supernatural", "Personality")
GAINABLE_TYPES = ("General", "Supernatural")
#: Background Virtues a pilgrimage neither grants nor removes (p. 16):
#: its two examples and every other Virtue giving experience at creation.
BACKGROUND = frozenset(
    {"vf_privileged_upbringing", "vf_educated", *creation_access.VIRTUE_XP}
)
#: The score a Divine Supernatural Ability gained by pilgrimage starts at.
GAINED_ABILITY_SCORE = 1
TRUE_FAITH = "vf_true_faith"


@dataclass(frozen=True)
class Element:
    key: str
    label: str
    value: int


#: The Oppositional Elements the book lists (p. 17), the seasons and travel
#: aside; "another trial" is any the storyguide designs at that value.
ELEMENTS: tuple[Element, ...] = (
    Element("disease", "Natural hazards such as virulent disease", 3),
    Element("temptation", "A temptation he is prone to succumb to", 3),
    Element("trial_3", "Another trial of faith and perseverance", 3),
    Element("bandits", "Dangerous mundane foes: bandits or robbers", 6),
    Element("enemies", "Dangerous foes who are religious or political enemies", 6),
    Element("storm", "Dangerous natural hazards: storms, avalanches, blizzards", 6),
    Element("trial_6", "Another trial of faith and perseverance", 6),
    Element("supernatural", "A dangerous supernatural encounter on the road", 9),
    Element("shipwreck", "A shipwreck", 9),
    Element("distraction", "Distractions that make abandoning it desirable", 9),
    Element("trial_9", "Another trial of faith and perseverance", 9),
    Element("demon", "Direct demonic opposition from an Infernal entity", 12),
)
ELEMENT_BY_KEY = {e.key: e for e in ELEMENTS}

#: The aims (p. 16), by key: (label, the Target Levels it is for).
GAIN_VIRTUE, LOSE_TRAIT, LOSE_VF, PENANCE, MIRACLE, HOLY_MAGIC = (
    "gain_virtue",
    "lose_trait",
    "lose_vf",
    "penance",
    "miracle",
    "holy_magic",
)
AIMS: dict[str, tuple[str, tuple[int, ...]]] = {
    GAIN_VIRTUE: ("Gain a Virtue", TARGETS),
    LOSE_VF: ("Lose a Flaw (or a Virtue)", TARGETS),
    LOSE_TRAIT: ("Remove a negative Personality Trait", (MINOR,)),
    PENANCE: ("Meet a penance", TARGETS),
    MIRACLE: ("Ask for a miracle", (MAJOR,)),
    HOLY_MAGIC: ("Self-initiate in Holy Magic", (MAJOR,)),
}


def tier(target: int) -> str:
    """The size of Virtue or Flaw a pilgrimage of this Target Level moves."""
    return "Major" if target >= MAJOR else "Minor"


def aims_for(target: int) -> list[tuple[str, str]]:
    """(label, key) of the aims a pilgrimage of this Target Level may have."""
    return [(label, key) for key, (label, levels) in AIMS.items() if target in levels]


def pilgrimages(character: Character) -> list[Progress]:
    """His pilgrimages under way or reached, not yet claimed."""
    return [p for p in character.progress if p.kind == KIND]


def find(character: Character, name: str) -> Progress | None:
    return next((p for p in pilgrimages(character) if p.name == name), None)


def story_of(character: Character, name: str) -> Progress | None:
    return next(
        (p for p in character.progress if p.kind == STORY_KIND and p.name == name),
        None,
    )


def _story(character: Character, name: str) -> Progress:
    found = story_of(character, name)
    if found is None:
        # Finished, so This Season's list of work under way leaves it out.
        found = Progress(STORY_KIND, name, done=True)
        character.progress.append(found)
    return found


def travel_counted(character: Character, name: str) -> int:
    """The travel element already counted for the pilgrimage (0, 3 or 6)."""
    found = story_of(character, name)
    return found.target if found is not None else 0


def failures(character: Character, name: str) -> int:
    """Elements failed and not yet remedied by a later one."""
    found = story_of(character, name)
    return found.points if found is not None else 0


def travel_gain(counted: int, travel: str) -> int:
    """What a travel element adds now: only the higher counts, once."""
    return max(0, TRAVEL[travel] - counted)


def element_value(key: str) -> int:
    if key in TRAVEL:
        return TRAVEL[key]
    return ELEMENT_BY_KEY[key].value


def element_label(key: str) -> str:
    if key == CHRISTIAN_ABROAD:
        return "Travel in a Christian land outside his homeland and native land"
    if key == HEATHEN_LANDS:
        return "Travel in non-Christian or heretic-controlled lands"
    return ELEMENT_BY_KEY[key].label


def overcome(record: Progress, character: Character, key: str) -> tuple[int, str]:
    """An element overcome: its points added to the pilgrimage, a failure
    remedied if any is outstanding. Returns (points added, what it did)."""
    story = _story(character, record.name)
    if key in TRAVEL:
        gained = travel_gain(story.target, key)
        story.target = max(story.target, TRAVEL[key])
    else:
        gained = ELEMENT_BY_KEY[key].value
    record.points += gained
    said = [f"+{gained}: {record.points} of {record.target}."]
    if story.points:
        story.points -= 1
        said.append("It remedies an element failed earlier.")
    if record.points >= record.target and not record.done:
        record.done = True
        said.append("The Target Level is reached.")
    return gained, " ".join(said)


def failed(character: Character, record: Progress) -> str:
    """An element failed: the aim fails unless a later element remedies it."""
    story = _story(character, record.name)
    story.points += 1
    return (
        "Failed: the pilgrimage's aim fails unless a later element he overcomes "
        f"remedies it ({story.points} outstanding)."
    )


def claim_problem(character: Character, record: Progress) -> str | None:
    """What stops claiming the aim (None when nothing does)."""
    if not record.done:
        return (
            f"{record.name} is at {record.points} of {record.target}: its "
            "Oppositional Elements must reach the Target Level first."
        )
    if failures(character, record.name):
        return (
            f"{record.name} has {failures(character, record.name)} element(s) "
            "failed and not remedied: the aim fails."
        )
    return None


def holy_magic_problem(character: Character) -> str | None:
    if not any(vf.vf_id == TRUE_FAITH for vf in character.virtues_flaws):
        return "Self-initiation in Holy Magic needs True Faith (TC p. 16)."
    return None


def gainable(
    character: Character, catalog: list[VirtueFlawDef], target: int
) -> list[VirtueFlawDef]:
    """Virtues a pilgrimage of this Target Level may grant him: General or
    Supernatural (Divine Supernatural Abilities, and at 30 Divine Methods
    and Powers, among them), of its size, never Hermetic, not a background
    one or one he holds."""
    held = {vf.vf_id for vf in character.virtues_flaws}
    size = tier(target)
    return [
        d
        for d in catalog
        if d.type == "Virtue"
        and d.category in GAINABLE_TYPES
        and d.tier == size
        and d.id not in BACKGROUND
        and d.id not in held
    ]


def losable(
    character: Character, by_id: Mapping[str, VirtueFlawDef], target: int
) -> list[VirtueFlawInstance]:
    """His Virtues and Flaws a pilgrimage of this Target Level may take
    away: Story, General, Social Status, Supernatural or Personality, of its
    size (never Hermetic, nor a background one)."""
    size = tier(target)
    found: list[VirtueFlawInstance] = []
    for instance in character.virtues_flaws:
        entry = by_id.get(instance.vf_id)
        if (
            entry is not None
            and entry.category in LOSABLE_TYPES
            and entry.tier == size
            and entry.id not in BACKGROUND
        ):
            found.append(instance)
    return found


def removable_traits(character: Character) -> list[ScoredTrait]:
    """His Personality Traits a minor pilgrimage may remove: one with a
    negative score, or one the sin table reads as leaning toward a sin."""
    found: list[ScoredTrait] = []
    for trait in character.personality_traits:
        leaning = sin.lean(trait.name)
        if trait.score < 0 or (leaning is not None and leaning[1] * trait.score > 0):
            found.append(trait)
    return found


def grant_ability(character: Character, virtue: VirtueFlawDef) -> Ability | None:
    """The Supernatural Ability a Virtue gained by pilgrimage grants (the
    Ability named for it), added at score 1 with no penalty for The Gift
    or his other Supernatural Abilities and Arts (p. 16). None when the
    Virtue grants no Ability or he already has it."""
    if virtue.category != "Supernatural":
        return None
    if any(a.name == virtue.name for a in character.abilities):
        return None
    entry = next(
        (
            a
            for a in catalog.load_ability_catalog()
            if a.name == virtue.name and a.category in SUPERNATURAL_CATEGORIES
        ),
        None,
    )
    if entry is None:
        return None
    table = creation_access.ability_xp_table(entry.name)
    ability = Ability(entry.name, entry.category, xp_table=table)
    ability.xp = xp_for_score(GAINED_ABILITY_SCORE, ability.factor)
    character.abilities.append(ability)
    return ability


def claim(record: Progress) -> None:
    """Mark the aim claimed, so it is claimed once."""
    record.kind = CLAIMED_KIND


def devotion_points(*, at_shrine: bool, other_sites: int = 0, relics: int = 0) -> int:
    """Devotion Points a pilgrimage gives in its saint's Devotion: 10 at the
    shrine, +5 a further site of the saint's life, up to 5 for relics."""
    if not at_shrine:
        return 0
    return (
        SHRINE_DEVOTION
        + SITE_DEVOTION * max(0, other_sites)
        + max(0, min(MOST_RELIC_DEVOTION, relics))
    )
