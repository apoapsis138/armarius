"""Christian mysticism as plain rules: the contemplative and monistic
paths, the contemplative's Spiritual Paths to a Revelation, the monist's
Revelations from his Divine Ascents, and what True Faith brings as it
rises (The Church, Christian Mysticism, pp. 19-24, summarizing Realms of
Power: The Divine pp. 56-64).

- Both paths (TC p. 21): the mystic is aligned with the Divine; any
  Warping he undergoes is a Divine Ascent (rules.realm_warping), Divine
  Form for a contemplative, Divine Gloom for a monist (rules.divine_state).
  The two are usually incompatible: one path at a time.
- Contemplative mysticism (TC p. 21): a positive Pious trait, none of the
  sinful traits of Realms of Power: The Divine p. 40 (rules.holy_influence
  reads them), and an association with the Divine: True Faith, a Divine
  Supernatural Ability, or Warping Points from a Divine source. The
  Ascent comes at 2 Warping Points from one event.
- A Spiritual Path (TC p. 22): the Revelation sought sets the Path Total:
  15 a Minor Holy Method, Power or Supernatural Ability, 18 another Minor
  Virtue, 27 a Major Holy Method, Power or Supernatural Ability, 30 another
  Major Virtue. Quest Components worth at least the Path Total grant
  the Revelation; his Pious isn't taken off it (the book defines a Path
  Target, the Path Total less Pious, but never uses it): +1 a season serving
  the poor or the Church, or of personal devotion (one Devotion Point, and
  only exposure in Dominion Lore); +3 a season preaching the Gospel (once);
  +6 a minor pilgrimage for nothing else, a Vow (the Minor Flaw), or a
  quest set for it; +9 a season preaching to heretics, pagans or infidels,
  revealing error or corruption in the local church and seeing it put
  right, giving his wealth as alms (he loses Wealthy, or gains Poor), or
  a year at least on a Church-sanctioned crusade. A Supernatural Ability
  gained so starts at 1, with no penalty for his other Supernatural
  Abilities or Arts; True Faith is never a Revelation.
- Monistic mysticism (TC p. 23): Visions or True Faith, a positive Pious
  trait, an association with the Divine. The Ascent comes at a single
  Warping Point. A season practising a Holy Ability (a Method, Power or
  Divine Supernatural Ability) gives his Concentration in experience, not
  4. On an Ascent he may try to integrate a Revelation (TC p. 24):
  Intelligence + Concentration + stress die against his Warping Score +
  stress die (no botch). Failing, the Gloom comes as usual; succeeding, he
  also chooses one: lose no mundane experience to the Gloom; a Minor
  Virtue at 3 or more Warping Points, a Major one at 5 or more (the first
  Revelation is always Second Sight); at 7 or more, Dominion Lore in place
  of Magic Lore or Faerie Lore, a realm each time; or, both of those
  held, Infernal Lore.
- The Divine Gloom (TC p. 23; RoP: The Divine pp. 63-64): each time he
  gains Warping Points, as many experience points among Dominion Lore and
  his Holy Abilities, and as many lost from mundane Abilities, never
  Concentration; his Pious adds to overcoming Celestial Disorientation;
  he is a beacon to every being of the Invisible World.
- True Faith as it rises (TC p. 23): at 2, the Premonitions Virtue, and a
  Faith Point dispels any Magical or Infernal illusion or Faerie glamour;
  at 3, double Magic Resistance against Mentem and like powers, and +6 a
  Faith Point spent instead of +3; at 5, an Empyreal aura to Voice range,
  which he may temper. The Definitive Edition (p. 419) has Faith Points
  spent like Confidence (+3 each) and no thresholds; The Church's are
  kept as the further gifts of a high Score, and the +3 stays the DE's
  below Score 3.
- Taking the cross (TC p. 19): one temporary Faith Point
  (rules.pilgrimage.CRUSADER_FAITH).

The errata have nothing on these pages.

Records (no new saved field): the path is rules.divine_state's; a
Spiritual Path is a progress record of kind "spiritual path" named for
the Revelation (its target the Path Total, its points the Quest
Components), claimed by renaming its kind "spiritual path claimed"
(preaching's once on a path is found in the Diary); a monist's
Revelations finished records of kind "monistic revelation".

Pattern: plain functions over the character's records, the Quest
Components and Revelations rows of data; the seasons of a path are the
activity registry's Strategy (season_work.mysticism).
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import catalog
from ..models import Character, Progress, VirtueFlawDef
from . import divine_state as ds
from . import holy_influence
from . import hybrid_magic as hybrid
from . import pilgrimage as pil
from .scores import ability_level
from .theban_customs import pious

SOURCE = (
    "The Church, Christian Mysticism, pp. 19-24; Realms of Power: The Divine "
    "pp. 40, 63-64"
)
BOOK = "TC"

CONTEMPLATIVE, MONISTIC = ds.CONTEMPLATIVE, ds.MONISTIC
PATHS = ds.PATHS
DIVINE = "Divine"

SPIRITUAL_PATH = "spiritual path"
CLAIMED = "spiritual path claimed"
REVELATION = "monistic revelation"

TRUE_FAITH = "vf_true_faith"
VISIONS = "vf_visions"
SECOND_SIGHT = "vf_second_sight"
WEALTHY, POOR, VOW = "vf_wealthy", "vf_poor", "vf_vow"
CONCENTRATION = "Concentration"
DOMINION_LORE = "Dominion Lore"
#: The experience a season's practice usually gives (DE p. 377).
USUAL_PRACTICE = 4


# -- the path --


def path(character: Character) -> str:
    return ds.path(character)


def holy_abilities(character: Character) -> list[str]:
    """His Holy Abilities, held at 1 or more: the Divine traditions'
    Methods and Powers, and the Divine's Supernatural Abilities (Sense
    Holiness and Unholiness, and those Realms of Power: The Divine gives)."""
    methods, powers = hybrid.methods_and_powers(DIVINE)
    from_rop = {
        a.name
        for a in catalog.load_ability_catalog()
        if a.category == "Supernatural" and "RoP:D" in a.source.split("; ")
    }
    divine = {n for n, realm in hybrid.ABILITY_REALMS.items() if realm == DIVINE}
    holy = methods | powers | from_rop | divine
    return [a.name for a in character.abilities if a.level > 0 and a.name in holy]


def _has(character: Character, vf_id: str) -> bool:
    return any(vf.vf_id == vf_id for vf in character.virtues_flaws)


def divine_ties(character: Character) -> list[str]:
    """What associates him with the Divine (TC p. 21): True Faith, a holy
    Ability, Warping from a Divine source."""
    found: list[str] = []
    if _has(character, TRUE_FAITH):
        found.append("True Faith")
    found += holy_abilities(character)
    if character.aging.warping_realms.get(DIVINE, 0) > 0:
        found.append("Divine Warping")
    return found


def sins(character: Character) -> list[str]:
    """The sins his traits and Personality Flaws lean to (RoP: The Divine
    p. 40): each temper he stands below 0 in."""
    by_temper = {t.name: t.sin for t in holy_influence.TEMPERS}
    return [
        by_temper[name]
        for name, score in holy_influence.temper_scores(character).items()
        if score < 0
    ]


def path_problems(character: Character, chosen: str) -> list[str]:
    """Why he can't follow `chosen` now (none for following no path)."""
    if chosen not in PATHS:
        return []
    found: list[str] = []
    if character.animal is not None:
        return ["Only a person follows a mystic path."]
    if pious(character) <= 0:
        found.append("Both paths need a positive Pious trait (TC pp. 21, 23).")
    if not divine_ties(character):
        found.append(
            "He must be tied to the Divine: True Faith, a Divine Supernatural "
            "Ability, or Divine Warping (TC p. 21)."
        )
    if chosen == CONTEMPLATIVE and (leaning := sins(character)):
        found.append(
            "A contemplative has no sinful trait (RoP: The Divine p. 40): he "
            "leans to " + ", ".join(leaning) + "."
        )
    if chosen == MONISTIC and not (
        _has(character, VISIONS) or _has(character, TRUE_FAITH)
    ):
        found.append("A monist has the Visions Flaw or True Faith (TC p. 23).")
    held = path(character)
    if held and held != chosen and ds.ascents(character):
        found.append(
            f"He has ascended on {held.lower()}: its form stays for life "
            "(RoP: The Divine p. 63)."
        )
    return found


def leave_problem(character: Character) -> str | None:
    if path(character) and ds.ascents(character):
        return "His Ascent's form stays for life: the path can't be left."
    return None


# -- practice and the Divine Gloom --


def practice_xp(character: Character, ability: str) -> int:
    """A season's practice of `ability`: his Concentration for a monist
    practising a Holy Ability (TC p. 23), else 4."""
    if path(character) == MONISTIC and ability in holy_abilities(character):
        return max(USUAL_PRACTICE, ability_level(character, CONCENTRATION))
    return USUAL_PRACTICE


def gloom_lines(character: Character, points: int) -> list[str]:
    """What Warping Points do to one in the Divine Gloom (TC p. 23)."""
    if points <= 0 or not ds.divine_gloom(character):
        return []
    holy = ", ".join(holy_abilities(character)) or "his Holy Abilities"
    return [
        f"Divine Gloom: {points} experience point(s) among Dominion Lore and "
        f"{holy}, and {points} lost from mundane Abilities (never "
        "Concentration), as the player chooses (TC p. 23)."
    ]


def ascent_lines(character: Character, gloom_points: int = 0) -> list[str]:
    """What a mystic's Ascent brings, for the Diary; `gloom_points` the
    Warping Points the Gloom has not yet counted (all of them at the
    first Ascent, only the Ascent's own after)."""
    chosen = path(character)
    if chosen == CONTEMPLATIVE:
        return [
            "As a contemplative mystic his Ascent is the Divine Form (TC p. 21): "
            "his Warping Score adds to True Faith's Magic Resistance, Soak gains "
            "that Resistance / 5, Penetration his Warping Score + 5 x True Faith; "
            "an impious act botches with 3 x Warping Score more dice, a venial "
            "sin brings a Light wound and a mortal one a Medium, healed only "
            "naturally; and a Commanding Aura (Penetration 0, Voice)."
        ]
    if chosen == MONISTIC:
        return [
            "As a monistic mystic his Ascent is the Divine Gloom (TC p. 23). He "
            "may try to integrate a Revelation: More's Monistic Revelation "
            "(Intelligence + Concentration + stress die against his Warping "
            "Score + stress die, TC p. 24).",
            "Pious adds to overcoming Celestial Disorientation; he is a beacon to "
            "angels, demons, elementals and faeries.",
            *gloom_lines(character, gloom_points),
        ]
    return []


# -- Spiritual Paths (the contemplative's) --


@dataclass(frozen=True)
class Revelation:
    key: str
    label: str
    total: int
    tier: str
    holy: bool


REVELATIONS: dict[str, Revelation] = {
    r.key: r
    for r in (
        Revelation(
            "minor_holy",
            "A Minor Holy Method, Power or Supernatural Ability",
            15,
            "Minor",
            True,
        ),
        Revelation("minor_virtue", "Another Minor Virtue", 18, "Minor", False),
        Revelation(
            "major_holy",
            "A Major Holy Method, Power or Supernatural Ability",
            27,
            "Major",
            True,
        ),
        Revelation("major_virtue", "Another Major Virtue", 30, "Major", False),
    )
}


def revelations(
    character: Character, defs: list[VirtueFlawDef], key: str
) -> list[VirtueFlawDef]:
    """The Virtues a Revelation of this kind may be: Supernatural for a
    holy one (its Ability starts at 1), General for another, of its size;
    never True Faith, one he holds, Hermetic or a background Virtue."""
    revelation = REVELATIONS[key]
    size = pil.MINOR if revelation.tier == "Minor" else pil.MAJOR
    wanted = "Supernatural" if revelation.holy else "General"
    return [
        d
        for d in pil.gainable(character, defs, size)
        if d.category == wanted and d.id != TRUE_FAITH
    ]


@dataclass(frozen=True)
class Component:
    key: str
    label: str
    value: int
    season: bool = False
    once: bool = False


COMPONENTS: dict[str, Component] = {
    c.key: c
    for c in (
        Component("service", "A season serving the poor or the Church", 1, True),
        Component(
            "devotion",
            "A season of personal devotion (one Devotion Point)",
            1,
            True,
        ),
        Component("preaching", "A season preaching the Gospel", 3, True, True),
        Component(
            "pilgrimage",
            "A minor pilgrimage to a fitting shrine, for nothing else",
            6,
        ),
        Component("vow", "A Vow (the Minor Flaw)", 6),
        Component("quest", "A quest set for the path", 6),
        Component(
            "infidels",
            "A season preaching to heretics, pagans or infidels",
            9,
            True,
        ),
        Component(
            "error",
            "Error, heresy or corruption revealed and put right",
            9,
        ),
        Component(
            "alms",
            "His wealth given as alms (loses Wealthy, or gains Poor)",
            9,
        ),
        Component(
            "crusade",
            "A year or more on a Church-sanctioned crusade",
            9,
        ),
    )
}
#: The components worked a season at a time (season_work.mysticism).
SEASON_COMPONENTS = tuple(c.key for c in COMPONENTS.values() if c.season)
#: The components kept with More's Spiritual Path.
STORY_COMPONENTS = tuple(c.key for c in COMPONENTS.values() if not c.season)


def spiritual_paths(character: Character) -> list[Progress]:
    """His Spiritual Paths not yet claimed, finished or not."""
    return [p for p in character.progress if p.kind == SPIRITUAL_PATH]


def find_path(character: Character, name: str) -> Progress | None:
    return next((p for p in spiritual_paths(character) if p.name == name), None)


def begin_problem(character: Character, name: str) -> str | None:
    if path(character) != CONTEMPLATIVE:
        return "Only a contemplative mystic walks a Spiritual Path (TC p. 22)."
    if not name.strip():
        return "Choose the Revelation."
    if name.strip().casefold() == "true faith":
        return "True Faith is never a Revelation (TC p. 22)."
    if find_path(character, name.strip()) is not None:
        return f"His path to {name.strip()} is already under way."
    return None


def begin(character: Character, name: str, key: str) -> Progress:
    record = Progress(SPIRITUAL_PATH, name.strip(), REVELATIONS[key].total)
    character.progress.append(record)
    return record


def counted_line(record_name: str) -> str:
    """The words a season's Diary entry says a component in, so a
    once-only one can be found again: "on the path to (Revelation):"."""
    return f"on the path to {record_name}:"


def component_problem(
    character: Character, record: Progress | None, key: str
) -> str | None:
    if record is None:
        return "Choose the Spiritual Path."
    if record.done:
        return "That path is walked: claim its Revelation."
    component = COMPONENTS.get(key)
    if component is None:
        return "Choose the Quest Component."
    if key == "alms" and _has(character, POOR) and not _has(character, WEALTHY):
        return "He is Poor already: he has no wealth to give."
    return None


def count(record: Progress, key: str) -> int:
    """Count a component on the path: its value, the path finished when
    it reaches its target. Returns the value counted."""
    component = COMPONENTS[key]
    record.points += component.value
    if record.target and record.points >= record.target:
        record.done = True
    return component.value


def claim_problem(record: Progress | None) -> str | None:
    if record is None:
        return "Choose the Spiritual Path."
    if record.points < record.target:
        return (
            f"{record.points} of {record.target}: more Quest Components first "
            "(TC p. 22)."
        )
    return None


def claim(record: Progress) -> None:
    record.kind = CLAIMED
    record.done = True


# -- the monist's Revelations (TC p. 24) --

KEEP_MUNDANE = "keep_mundane"
MINOR_VIRTUE = "minor_virtue"
MAJOR_VIRTUE = "major_virtue"
REALM_LORE = "realm_lore"
INFERNAL_LORE = "infernal_lore"
#: Each Revelation's choice: (label, the Warping Points it needs).
INTEGRATIONS: dict[str, tuple[str, int]] = {
    KEEP_MUNDANE: ("Lose no mundane experience to the Gloom", 0),
    MINOR_VIRTUE: ("A Minor Virtue (3 or more Warping Points)", 3),
    MAJOR_VIRTUE: ("A Major Virtue (5 or more Warping Points)", 5),
    REALM_LORE: ("Dominion Lore for Magic or Faerie Lore (7 or more)", 7),
    INFERNAL_LORE: ("Dominion Lore for Infernal Lore (after both)", 7),
}
LORE_REALMS = ("Magic", "Faerie")


def revelations_had(character: Character) -> list[str]:
    return [p.name for p in character.progress if p.kind == REVELATION]


def lore_realms(character: Character) -> list[str]:
    """The realms whose Lore his Dominion Lore stands in for."""
    return [
        name.removesuffix(" Lore")
        for name in revelations_had(character)
        if name.endswith(" Lore")
    ]


def integration_total(character: Character) -> int:
    """Intelligence + Concentration, before the stress die."""
    return character.characteristics.intelligence + ability_level(
        character, CONCENTRATION
    )


def integration_problem(
    character: Character, choice: str, points: int, realm: str = ""
) -> str | None:
    """Why the choice isn't open to him after an Ascent of `points`."""
    if path(character) != MONISTIC:
        return "Only a monistic mystic integrates a Revelation (TC p. 24)."
    if not ds.ascents(character):
        return "He integrates a Revelation on a Divine Ascent: he has had none."
    label, needed = INTEGRATIONS.get(choice, ("", 0))
    if not label:
        return "Choose what the Revelation brings."
    if points < needed:
        return f"{label.split(' (')[0]} needs {needed} or more Warping Points."
    held = lore_realms(character)
    if choice == REALM_LORE:
        if realm not in LORE_REALMS:
            return "Choose Magic or Faerie."
        if realm in held:
            return f"His Dominion Lore already serves for {realm} Lore."
    if choice == INFERNAL_LORE:
        if not all(r in held for r in LORE_REALMS):
            return "First both Magic and Faerie (TC p. 24)."
        if "Infernal" in held:
            return "His Dominion Lore already serves for Infernal Lore."
    return None


def first_revelation(character: Character) -> bool:
    """Whether the next Virtue he gains this way is his first (always
    Second Sight)."""
    return not any(not n.endswith(" Lore") for n in revelations_had(character))


def note_revelation(character: Character, name: str) -> None:
    character.progress.append(Progress(REVELATION, name, done=True))


# -- True Faith as it rises (TC p. 23) --

#: What each True Faith Score brings, beyond the DE's (TC p. 23).
FAITH_GIFTS: dict[int, str] = {
    2: (
        "the Premonitions Virtue; a Faith Point dispels any Magical or "
        "Infernal illusion or Faerie glamour, whatever its level"
    ),
    3: (
        "double Magic Resistance against Mentem spells and like powers; +6 "
        "for each Faith Point spent, not +3"
    ),
    5: "an Empyreal aura to Voice range, which he may temper",
}
PREMONITIONS = "vf_premonitions"
#: What a Faith Point adds to a roll, below Score 3 and from it.
FAITH_POINT_BONUS, HIGH_FAITH_POINT_BONUS, HIGH_FAITH_AT = 3, 6, 3


def faith_gifts(score: int) -> list[str]:
    return [f"True Faith {n}: {what}" for n, what in FAITH_GIFTS.items() if score >= n]


def faith_point_bonus(score: int) -> int:
    return HIGH_FAITH_POINT_BONUS if score >= HIGH_FAITH_AT else FAITH_POINT_BONUS
