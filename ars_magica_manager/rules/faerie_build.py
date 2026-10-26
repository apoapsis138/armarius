"""A faerie built by the book (Realms of Power: Faerie, Chapter Three, pp.
45-64): its Might from its Virtues, not from Quality points as a magic
creature's, and the choices every faerie makes.

- Faerie Might starts at 5; Increased Faerie Might adds 5 (Minor) or 15
  (Major), and may be taken again; Decreased Might leaves 1 (pp. 46-47).
  Time or Place of Power adds 10 at its time or place.
- Every faerie has a physical form (Faerie Beast, Humanoid Faerie, Hybrid
  Form), a level of cognizance (Incognizant, Narrowly or Highly
  Cognizant), a Social Interaction Virtue or Flaw, and a taboo
  (Traditional or Sovereign Ward) (pp. 46, 50-52).
- No faerie has The Gift, a Hermetic Virtue or Flaw, a Social Status
  Virtue or a Confidence Score; at most three Minor Personality Flaws and
  one Major (p. 54).
- A faerie made as a player character has Pretense points of 15 x (the
  magi's average age - 5) + 120, the 15 being 20 when Pretentious, 25
  Ostentatious and 10 Aloof, 50 fewer for each Freshly Sprung (pp. 46,
  63-64).

- Every faerie plays a role in the stories it takes part in, and wants a
  story to play it in: the dramatis personae are the Hero, the Villain,
  the Donor, the Helper, the Princess, the Task-Setter and the False Hero
  (Chapter Seven, pp. 140-142; any story element can take one, p. 40). A
  faerie keeps its role and the story it wants as a note; how faerie
  stories are built from such elements (pp. 31-44) is the storyguide's.

The book's own faeries, and any a story needs, needn't balance (p. 45), so
these are advice, never refusals.
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import catalog
from ..models import Creature

SOURCE = (
    "Realms of Power: Faerie, Chapter Three: Faerie Characters, pp. 45-64; "
    "Story Elements p. 40; Dramatis Personae pp. 140-142"
)

FAERIE = "Faerie"
BASE_MIGHT = 5
DECREASED_MIGHT = 1
INCREASED = {"vf_increased_faerie_might": 5, "vf_increased_faerie_might_major": 15}
DECREASED = "vf_decreased_might"
TIME_OR_PLACE = "vf_time_or_place_of_power"
TIME_OR_PLACE_MIGHT = 10

#: The choices every faerie makes, each from these (pp. 46, 50-52).
REQUIRED: tuple[tuple[str, tuple[str, ...], int], ...] = (
    (
        "a physical form",
        ("vf_faerie_beast", "vf_humanoid_faerie", "vf_hybrid_form"),
        50,
    ),
    (
        "a level of cognizance",
        ("vf_incognizant", "vf_narrowly_cognizant", "vf_highly_cognizant"),
        52,
    ),
    (
        "a Social Interaction Virtue or Flaw",
        (
            "vf_passes_for_human",
            "vf_positive_folktales",
            "vf_infiltrator",
            "vf_infiltrator_major",
            "vf_monstrous_appearance",
            "vf_negative_reaction",
        ),
        51,
    ),
    ("a taboo", ("vf_traditional_ward", "vf_sovereign_ward"), 52),
)
THE_GIFT = "vf_the_gift"
MOST_MINOR_PERSONALITY, MOST_MAJOR_PERSONALITY = 3, 1

#: The Pretense multiplier of a faerie made as a player character, and
#: what changes it (pp. 46, 63-64).
PRETENSE_MULTIPLIER = 15
MULTIPLIERS = {"vf_pretentious": 20, "vf_ostentatious": 25, "vf_aloof": 10}
FRESHLY_SPRUNG, FRESHLY_SPRUNG_POINTS = "vf_freshly_sprung", 50
PRETENSE_BASE = 120


#: The dramatis personae a faerie may play, each in a line (pp. 140-142).
ROLES: dict[str, str] = {
    "Hero": "sets off on adventure, seeking a prize or forced to by the villain",
    "Villain": "opposes the hero again and again, to a struggle or a pursuit",
    "Donor": "grants the hero a magical gift, not always willingly",
    "Helper": "always well inclined, helps the hero at the right moment",
    "Princess": "the object of the quest, or a prize won along the way",
    "Task-Setter": "sets the hero challenges to win the princess",
    "False Hero": "claims the hero's deeds, unmasked in the nick of time",
}
ROLES_PAGES = "pp. 140-142"


@dataclass(frozen=True)
class FaerieMight:
    """A faerie's Might as its Virtues make it, and how."""

    might: int
    parts: tuple[str, ...]


def is_faerie(creature: Creature) -> bool:
    return creature.realm == FAERIE


def might_from_virtues(creature: Creature) -> FaerieMight:
    """Faerie Might by the Virtues and Flaws (pp. 46-47)."""
    ids = [vf.vf_id for vf in creature.virtues_flaws]
    if DECREASED in ids:
        return FaerieMight(DECREASED_MIGHT, ("Decreased Might 1",))
    parts = [f"base {BASE_MIGHT}"]
    might = BASE_MIGHT
    for vf_id in ids:
        if vf_id in INCREASED:
            might += INCREASED[vf_id]
            tier = "Major" if INCREASED[vf_id] > 5 else "Minor"
            parts.append(f"Increased Faerie Might ({tier}) +{INCREASED[vf_id]}")
    return FaerieMight(might, tuple(parts))


def pretense_points(creature: Creature, magi_age: int) -> int:
    """A faerie player character's Pretense points (pp. 46, 63-64)."""
    ids = [vf.vf_id for vf in creature.virtues_flaws]
    multiplier = next(
        (MULTIPLIERS[v] for v in ids if v in MULTIPLIERS), PRETENSE_MULTIPLIER
    )
    sprung = ids.count(FRESHLY_SPRUNG) * FRESHLY_SPRUNG_POINTS
    return multiplier * (magi_age - 5) + PRETENSE_BASE - sprung


#: What the sheet says of a faerie built by the book with no role noted.
NO_ROLE = (
    "not noted: a faerie plays a role (Hero, Villain, Donor, Helper, "
    "Princess, Task-Setter or False Hero) and wants a story to play it in"
)


def role_text(creature: Creature) -> str:
    """A faerie's role and the story it wants, as the sheet gives them; a
    reminder for a faerie built by the book with neither; "" for another
    faerie with neither, or a creature of another realm."""
    if not is_faerie(creature):
        return ""
    role = creature.faerie_role
    parts = [f"{role}: {ROLES[role]}" if role in ROLES else role]
    if creature.faerie_story:
        parts.append(f"wants {creature.faerie_story}")
    text = "; ".join(p for p in parts if p)
    if not text and built_by_the_book(creature):
        text = NO_ROLE
    return f"{text} (RoP: Faerie {ROLES_PAGES})" if text else ""


def built_by_the_book(creature: Creature) -> bool:
    """A faerie being built by Realms of Power: Faerie: one with a form or a
    Might Virtue of its design. The Definitive Edition's
    faeries, and the Tribunal books', are written another way and aren't
    checked against it."""
    marks = {*INCREASED, DECREASED, *REQUIRED[0][1]}
    return is_faerie(creature) and any(
        vf.vf_id in marks for vf in creature.virtues_flaws
    )


def problems(creature: Creature) -> list[str]:
    """What a faerie built by the book would have that this one lacks, or
    has that a faerie can't (advice: the book's faeries needn't balance)."""
    if not built_by_the_book(creature):
        return []
    by_id = {e.id: e for e in catalog.load_virtue_flaw_catalog()}
    ids = [vf.vf_id for vf in creature.virtues_flaws]
    found: list[str] = []
    missing = [
        f"{what} (p. {page})"
        for what, options, page in REQUIRED
        if not any(v in options for v in ids)
    ]
    if missing:
        found.append("A faerie built by the book has " + ", ".join(missing) + ".")
    built = might_from_virtues(creature)
    if built.might != creature.might:
        found.append(
            f"Its Virtues make a Faerie Might of {built.might} "
            f"({', '.join(built.parts)}), not {creature.might} (pp. 46-47)."
        )
    if THE_GIFT in ids:
        found.append("A faerie can't have The Gift (p. 54).")
    hermetic = sorted(
        {by_id[v].name for v in ids if v in by_id and by_id[v].category == "Hermetic"}
    )
    if hermetic:
        found.append(
            f"A faerie has no Hermetic Virtues or Flaws: {', '.join(hermetic)} (p. 54)."
        )
    status = sorted(
        {
            by_id[v].name
            for v in ids
            if v in by_id and by_id[v].category == "Social Status"
        }
    )
    if status:
        found.append(
            f"A faerie has no Social Status Virtues (it takes Infiltrator): "
            f"{', '.join(status)} (p. 54)."
        )
    if creature.confidence_score is not None:
        found.append("A faerie has no Confidence Score (p. 54).")
    personality = [
        by_id[v].tier
        for v in ids
        if v in by_id and by_id[v].category == "Personality" and by_id[v].type == "Flaw"
    ]
    if (
        personality.count("Minor") > MOST_MINOR_PERSONALITY
        or personality.count("Major") > MOST_MAJOR_PERSONALITY
    ):
        found.append(
            "A faerie has at most three Minor Personality Flaws and one Major (p. 54)."
        )
    if TIME_OR_PLACE in ids:
        found.append(
            f"Time or Place of Power: Might {creature.might + TIME_OR_PLACE_MIGHT} "
            "at its time or place (p. 47)."
        )
    return found
