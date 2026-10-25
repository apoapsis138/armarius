"""The Curious Common Magics: arcana known throughout the Order without
Initiation (The Mysteries Revised Edition, Chapter Two, pp. 25-36). The
Definitive Edition prints Performance Magic (p. 101); the rest are The
Mysteries'. Planetary Magic, Potent Magic and Withstand Casting are worked
out with the other lab and casting Virtues (rules.lab_virtues,
rules.casting).

- The Art of Memory (pp. 25-26): a memory palace of as many rooms as the
  score, five loci each. Memorizing: Intelligence + Art of Memory + stress
  die against 9 (a page, five minutes' talk), 12 (twelve pages, an hour)
  or 18 (a hundred pages, a day), +3 or +6 when technical. Without it:
  Intelligence alone, three extra botch dice, and the roll again to recall.
- Spell Binding (pp. 27-28): a container Ritual, Sustain a Spell of
  (Form), whose level is at least the bound spell's; the bound spell is
  neither a Ritual nor Momentary; a spirit of the magus's realm with Might
  at least the spell's level sustains it while trapped; a spell to free the
  spirit must exceed the container's level.
- Performance Magic (DE p. 101): the chosen Ability's performance replaces
  words, gestures or both; a Performance Duration spell needs
  Characteristic + Ability against 3 and no Concentration rolls; telling
  its Form is Perception + Awareness against 15 - magnitude, -3 if Hermetic
  words are heard, +3 if words and gestures are both mundane.
- Vulgar Alchemy (pp. 32-35): experimenting on a charged or lesser
  device, the Lab Total adds Magic Lore, and the Experimentation Bonus
  (simple die + risk) is shared out testing up to Magic Theory components:
  simple die + Perception + Magic Lore against 3 + 3 x the bonus proposed.
  Shape and material bonuses stay capped at Magic Theory. A tractatus may
  teach one if its Quality is at least twice the bonus."""

from __future__ import annotations

from ..models import Character
from .breakdown import Line
from .lab import ability_score
from .lab_virtues import has

SOURCE = (
    "The Mysteries Revised Edition, Chapter Two: Curious Common Magics, pp. 25-36; "
    "Ars Magica Definitive Edition, Performance Magic, p. 101"
)

ART_OF_MEMORY = "Art of Memory"
SPELL_BINDING = "vf_spell_binding"
PERFORMANCE_MAGIC = "vf_performance_magic"
VULGAR_ALCHEMY = "vf_vulgar_alchemy"

# -- the Art of Memory --

LOCI_A_ROOM = 5
#: Memorizing's Ease Factors, and what is added for technical matter.
MEMORIZE = {"average": 9, "hard": 12, "impressive": 18}
TECHNICAL = (3, 6)
#: Extra botch dice memorizing without the Ability.
UNTRAINED_BOTCH = 3


def memory_palace(score: int) -> tuple[int, int]:
    """Rooms and loci in a memory palace of Art of Memory `score`."""
    rooms = max(0, score)
    return rooms, LOCI_A_ROOM * rooms


def memorize_total(character: Character) -> tuple[int, int]:
    """Intelligence + Art of Memory, and the extra botch dice (three
    without the Ability, who must roll again to recall)."""
    score = sum(ability_score(character, ART_OF_MEMORY))
    intelligence = character.characteristics.intelligence
    if score <= 0:
        return intelligence, UNTRAINED_BOTCH
    return intelligence + score, 0


# -- Spell Binding --


def binding_problems(
    spell_level: int,
    container_level: int,
    spirit_might: int,
    *,
    ritual: bool = False,
    momentary: bool = False,
) -> list[str]:
    """Why a spell can't be bound so (none: it can)."""
    found = []
    if ritual or momentary:
        found.append("A bound spell can't be a Ritual or Momentary.")
    if container_level < spell_level:
        found.append(
            f"The container Ritual's level ({container_level}) must be at least "
            f"the spell's ({spell_level})."
        )
    if spirit_might < spell_level:
        found.append(
            f"The spirit's Might ({spirit_might}) must be at least the spell's "
            f"level ({spell_level})."
        )
    return found


def freeing_level(container_level: int) -> int:
    """The least level a spell commanding the spirit out must have."""
    return container_level + 1


# -- Performance Magic --

PERFORMANCE_EASE = 3
FORM_EASE = 15
#: Telling a performed spell's Form: the change to the Ease Factor.
FORM_HEARD_WORDS, FORM_ALL_MUNDANE = -3, 3


def form_ease(magnitude: int, *, hermetic_words: bool, hermetic_gestures: bool) -> int:
    """The Ease Factor to tell the Form of a spell cast with Performance
    Magic: 15 - magnitude, -3 if Hermetic words are heard, +3 if words and
    gestures are both mundane."""
    ease = FORM_EASE - magnitude
    if hermetic_words:
        ease += FORM_HEARD_WORDS
    elif not hermetic_gestures:
        ease += FORM_ALL_MUNDANE
    return ease


# -- Vulgar Alchemy --


def component_ease(bonus: int, story: int = 0) -> int:
    """Testing a component for `bonus`: 3 + 3 x bonus, less the
    storyguide's story factor (up to 5 either way)."""
    return 3 + 3 * bonus - max(-5, min(5, story))


def components_allowed(character: Character) -> int:
    """How many components a season's experiment may test: Magic Theory."""
    return max(0, sum(ability_score(character, "Magic Theory")))


def thesis_quality(bonus: int) -> int:
    """The least Quality a Magic Theory tractatus needs to teach a bonus."""
    return 2 * bonus


# -- for the sheet --


def reminders(magus: Character) -> list[str]:
    """A sentence (plain text) for each of these the magus has, when he
    casts."""
    found: list[str] = []
    if has(magus, PERFORMANCE_MAGIC):
        abilities = [
            str(vf.params.get("ability") or "")
            for vf in magus.virtues_flaws
            if vf.vf_id == PERFORMANCE_MAGIC
        ]
        named = ", ".join(a for a in abilities if a)
        found.append(
            f"Performance Magic{' (' + named + ')' if named else ''}: performing "
            "it replaces words, gestures or both; a Performance Duration spell "
            f"needs Characteristic + the Ability against {PERFORMANCE_EASE} and "
            "no Concentration rolls."
        )
    if has(magus, SPELL_BINDING):
        found.append(
            "Spell Binding: Sustain a Spell of (Form) at least the spell's level "
            "binds a non-Ritual, non-Momentary spell to a container; a spirit "
            "of Might at least its level, trapped inside, sustains it."
        )
    return found


def lab_lines(
    magus: Character, *, enchanting: bool, experimenting: bool
) -> tuple[list[Line], list[str]]:
    """Vulgar Alchemy's Magic Lore line and note for a season that
    experiments while enchanting (none otherwise)."""
    if not (has(magus, VULGAR_ALCHEMY) and enchanting and experimenting):
        return [], []
    lines = []
    lore = magic_lore(magus)
    if lore:
        lines.append(Line("Vulgar Alchemy (Magic Lore)", amount=lore, source=SOURCE))
    return lines, [
        "Vulgar Alchemy (charged or lesser devices only): share the "
        "Experimentation Bonus among up to "
        f"{components_allowed(magus)} components, each tested at simple die + "
        "Perception + Magic Lore against 3 + 3 x its bonus; found bonuses add, "
        "capped by Magic Theory."
    ]


def magic_lore(magus: Character) -> int:
    """What Vulgar Alchemy's Lab Total adds: Magic Lore."""
    return max(0, sum(ability_score(magus, "Magic Lore")))
