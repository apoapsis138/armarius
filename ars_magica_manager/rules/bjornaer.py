"""House Bjornaer's Mysteries: the heartbeast, the House Mysteries and the
Inner Mysteries of the inner heartbeast (Houses of Hermes: Mystery Cults
pp. 18-33; the Definitive Edition's Outer Mystery, pp. 233-235, wins
where they differ).

The heartbeast (DE pp. 233-234; HoH:MC pp. 18-24):

- Its temperament: sanguine (birds), choleric (active land animals,
  nearly all predators), melancholic (slow or docile land animals),
  phlegmatic (all that crawl or swim), pure or aspected by another
  (TEMPERAMENTS, EXAMPLE_HEARTBEASTS; pp. 19-21). Sanguine opposes
  melancholic, choleric opposes phlegmatic (p. 26).
- Its choice: no domesticated beast, nothing with a Might score, nothing
  inanimate; smaller than Size -7 only by the storyguide, with Dwarf;
  larger than +3 only by the storyguide, with Giant Blood at least; one
  of Size -5 or less may be taken a Size larger as a noble specimen
  (pp. 20-21).
- Changing form takes no roll unless something stops it: a shapechanging
  spell, or magic that suppresses the magus's (an Aegis), needs Stamina +
  Heartbeast against 3 + the magic's magnitude, and a success dispels the
  shapechange (DE p. 234; p. 22). The Definitive Edition's change "takes
  only a moment" and a Bjornaer in heartbeast form may cast at -15 (no
  words or gestures, DE p. 234); HoH:MC's full round and "cannot make the
  gestures" (pp. 22-24) give way to it.
- Ringing the Changes (p. 23, with the Errata p. 54): each Characteristic
  but Intelligence is the lower of the two when both are negative, the
  higher when both are positive, else their sum; the magus keeps his
  Intelligence (a lycanthrope takes the beast's Cunning).
- A Bjornaer cannot bind a familiar (DE p. 234). At Final Twilight he
  becomes his heartbeast; with an Inner Mystery, a Great Beast with Magic
  Might 5 x Heartbeast (p. 24).

Initiation (pp. 25-30): the Ritual of Twelve Years gives the Heartbeast
(Target 15, Script +6 + the witnesses' temperaments, +1 for each that
shares the probationer's and -1 for each opposed, the Mystagogue among
them); it fails for one who has ever bound a familiar, even one since
dead (p. 24: a familiar bound now, a familiar season in his Diary, or the
plan's tick for one the app can't see), and losing the
ability to bind one counts as a Minor Ordeal for later Initiations when
it comes after character creation (p. 26). Clan Ilfetu Initiates the
House Mysteries (Secret Name, Theriomorphy, Sensory Magic); a Clan
Mystery's Mystagogue needs Presence + House Bjornaer Lore 8. The Inner
Heartbeast needs the Lore at 5 and a Great Beast as Mystagogue (Presence
+2, Lore 8, knowing the Mystery): Target 21, Script +13 (Sacrifice of
time +1, Quest +3, a Major Hermetic or Supernatural Flaw as the Ordeal
+9); a known shapechanger's Ordeal must be the loss of his Skinchanger or
Shapeshifter (p. 17).

Refinements (pp. 32-33): self-Initiated with the embryonic Script (+7: a
season at an ancestor site +3, vis eaten at a pawn per three points of
the Ease Factor and a Warping Point +1, the Virtue only in the inner
heartbeast's form +3), +3 more where the inner heartbeast resonates, and
the storyguide's -5 to +5 sympathy for any component added (REFINEMENTS).

Sensory Magic (pp. 27-28): Heartbeast adds to the Lab Total inventing a
spell with a Sensory Target, or an Intellego spell granting a magical
sense (sensory_line).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from ..models import Character, Characteristics, Saga, Spell, SpellDesign
from . import lab_virtues
from .breakdown import Breakdown, Line
from .lab import ability_score
from .rounding import round_up

MC = "Houses of Hermes: Mystery Cults"
SOURCE = "Ars Magica Definitive Edition, Bjornaer: The Heartbeast, pp. 233-234"
HEARTBEAST_SOURCE = f"{MC}, The Heartbeast, pp. 18-24"
TEMPERAMENT_SOURCE = f"{MC}, Heartbeast Temperaments, pp. 19-21"
CHANGES_SOURCE = f"{MC}, Statistics of Shapechangers, p. 23 (Errata p. 54)"
INITIATION_SOURCE = f"{MC}, The Mysteries of House Bjornaer, pp. 24-28"
INNER_SOURCE = f"{MC}, Initiating the Mysteries of the Inner Heartbeast, pp. 28-32"
REFINEMENT_SOURCE = f"{MC}, Refining the Inner Heartbeast, pp. 32-33"
SENSORY_SOURCE = f"{MC}, Sensory Magic, pp. 27-28"

HEARTBEAST = "vf_heartbeast"
ABILITY = "Heartbeast"
SECRET_NAME = "vf_secret_name"
THERIOMORPHY = "vf_theriomorphy"
SENSORY_MAGIC = "vf_sensory_magic"
EPITOME = "vf_mystery_of_the_epitome"
CHIMERA = "vf_mystery_of_the_chimera"
ANIMA = "vf_mystery_of_the_anima"
CLAN_ILFETU = "vf_clan_ilfetu"
SHAPECHANGERS = ("vf_skinchanger", "vf_shapeshifter")
#: Other Houses' Outer Mysteries: an Initiate of one is refused (p. 18).
OTHER_HOUSE_MYSTERIES = ("vf_verditius_magic", "vf_the_enigma", "vf_faerie_magic")

#: The House's Lore, as the Ability catalog names it; the book's "House
#: Bjornaer Lore" (HoH:MC pp. 28, 30; Errata p. 54) and "Bjornaer Lore"
#: count too, in the Initiation Total as everywhere else.
CULT_LORE = "Mystery Cult Lore: Bjornaer"
LORE_NAMES = (CULT_LORE, "House Bjornaer Lore", "Bjornaer Lore")
#: The tradition catalog entry holding the House's Scripts.
CULT_TRADITION = "trad_bjornaer_mysteries"

# -- Temperaments (pp. 19-21) ---------------------------------------------------

SANGUINE, CHOLERIC = "sanguine", "choleric"
MELANCHOLIC, PHLEGMATIC = "melancholic", "phlegmatic"
TEMPERAMENTS = (SANGUINE, CHOLERIC, MELANCHOLIC, PHLEGMATIC)
#: The temperament each opposes (p. 26).
OPPOSED: dict[str, str] = {
    SANGUINE: MELANCHOLIC,
    MELANCHOLIC: SANGUINE,
    CHOLERIC: PHLEGMATIC,
    PHLEGMATIC: CHOLERIC,
}


def _group(temperament: str, aspect: str, *beasts: str) -> dict[str, tuple[str, str]]:
    return {beast: (temperament, aspect) for beast in beasts}


#: The book's example heartbeasts (the diagram, p. 21): beast ->
#: (temperament, aspect; "" when pure).
EXAMPLE_HEARTBEASTS: dict[str, tuple[str, str]] = {
    **_group(SANGUINE, "", "bat", "crow", "cuckoo", "dove", "goose", "magpie"),
    **_group(SANGUINE, "", "owl", "partridge"),
    **_group(SANGUINE, CHOLERIC, "falcon", "eagle", "osprey"),
    **_group(SANGUINE, PHLEGMATIC, "stork", "heron", "swan"),
    **_group(CHOLERIC, "", "dog", "gazelle", "monkey", "deer", "lion", "lynx"),
    **_group(CHOLERIC, "", "wolf"),
    **_group(CHOLERIC, SANGUINE, "cat", "weasel", "fox"),
    **_group(CHOLERIC, MELANCHOLIC, "horse", "stag"),
    **_group(MELANCHOLIC, "", "antelope", "ibex", "wild ass", "badger", "moose"),
    **_group(MELANCHOLIC, "", "goat", "hedgehog", "mole", "rat"),
    **_group(MELANCHOLIC, CHOLERIC, "bear", "boar", "bull"),
    **_group(MELANCHOLIC, PHLEGMATIC, "wild sheep", "hare"),
    **_group(PHLEGMATIC, "", "octopus", "dolphin", "eel", "frog", "pike"),
    **_group(PHLEGMATIC, "", "salmon", "shark", "salamander"),
    **_group(PHLEGMATIC, SANGUINE, "lizard", "asp", "grass snake"),
    **_group(PHLEGMATIC, MELANCHOLIC, "otter", "beaver", "seal"),
}


def temperament_of(beast: str) -> tuple[str, str] | None:
    """A heartbeast's (temperament, aspect) when the book names the beast
    (a leading "the" and a plural "s" are ignored); None otherwise."""
    name = beast.strip().lower().removeprefix("the ").strip()
    for key in (name, name.removesuffix("s")):
        if key in EXAMPLE_HEARTBEASTS:
            return EXAMPLE_HEARTBEASTS[key]
    return None


def heartbeast_of(magus: Character) -> str:
    """The magus's heartbeast as his sheet names it: the Heartbeast
    Ability's specialty, less a leading "changing into a" ("" if none)."""
    ability = next((a for a in magus.abilities if a.name == ABILITY), None)
    text = ((ability.specialty if ability is not None else "") or "").strip()
    for prefix in ("changing into an ", "changing into a ", "changing into "):
        if text.lower().startswith(prefix):
            return text[len(prefix) :].strip()
    return text


def temperament_line(magus: Character) -> str:
    """The magus's heartbeast and its temperament, when the book's
    diagram names the beast ("" otherwise)."""
    beast = heartbeast_of(magus)
    found = temperament_of(beast) if beast else None
    if found is None:
        return ""
    temperament, aspect = found
    aspected = f", {aspect}-aspected" if aspect else ""
    return (
        f"Heartbeast: {beast}, {temperament}{aspected}; opposed to "
        f"{OPPOSED[temperament]} heartbeasts (HoH:MC pp. 19-21, 26)."
    )


# -- Choosing the heartbeast (pp. 20-21) -----------------------------------------

#: The Size range of an ordinary heartbeast: below it needs the storyguide
#: and Dwarf; above it the storyguide, and Giant Blood at least.
SMALLEST, LARGEST = -7, 3
#: A heartbeast of this Size or smaller may be one Size larger.
NOBLE_SIZE = -5
DWARF = "vf_dwarf"
GIANT_BLOOD = "vf_giant_blood"


def heartbeast_size(natural: int, noble: bool = False) -> int:
    """The heartbeast's Size: its species', or one more for a noble
    specimen of a species of Size -5 or less (p. 21)."""
    return natural + 1 if noble and natural <= NOBLE_SIZE else natural


def choice_problems(
    natural_size: int,
    *,
    noble: bool = False,
    domesticated: bool = False,
    might: bool = False,
    inanimate: bool = False,
    vf_ids: frozenset[str] = frozenset(),
) -> list[str]:
    """What the book says against a heartbeast (pp. 20-21): the kinds never
    allowed, and the Sizes that need the storyguide's leave."""
    found: list[str] = []
    if domesticated:
        found.append("Only wild beasts: no domesticated animal is a heartbeast.")
    if might:
        found.append("Only natural creatures: nothing with a Might score.")
    if inanimate:
        found.append("Nothing inanimate is a heartbeast: it has no spirit.")
    size = heartbeast_size(natural_size, noble)
    if size < SMALLEST:
        found.append(
            f"Size {size} is smaller than a weasel: only with the storyguide's "
            "leave, and the Dwarf Flaw is then obligatory"
            + ("." if DWARF in vf_ids else " (the magus lacks it).")
        )
    if size > LARGEST:
        found.append(
            f"Size {size} is larger than an aurochs: only with the storyguide's "
            "leave, and Giant Blood at the least"
            + ("." if GIANT_BLOOD in vf_ids else " (the magus lacks it).")
        )
    if noble and natural_size > NOBLE_SIZE:
        found.append(
            f"Only a heartbeast of Size {NOBLE_SIZE} or less may be a Size larger."
        )
    return found


# -- Changing form (DE p. 234; pp. 22, 27, 32) ------------------------------------

#: Resisting a shapechange, or magic suppressing his own: this + magnitude.
RESIST_BASE = 3
#: Theriomorphy's roll (p. 27) and the change to the inner heartbeast (p. 32).
THERIOMORPHY_EASE = 9
INNER_EASE = 9


def resist_ease(magnitude: int) -> int:
    """The Ease Factor to take either natural form against a shapechanging
    spell, or against magic suppressing his (an Aegis): 3 + its magnitude
    (DE p. 234; p. 22)."""
    return RESIST_BASE + max(0, magnitude)


def heartbeast_score(magus: Character) -> int:
    level, bonus = ability_score(magus, ABILITY)
    return level + bonus


def change_total(magus: Character) -> Breakdown:
    """Stamina + Heartbeast, the roll's total before the die."""
    lines = [
        Line("Stamina", amount=magus.characteristics.stamina, source=SOURCE),
        Line(ABILITY, amount=heartbeast_score(magus), source=SOURCE),
    ]
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


# -- Ringing the Changes (p. 23, Errata p. 54) --------------------------------------

#: The Characteristics combined (Intelligence is the magus's own).
COMBINED = (
    "perception",
    "presence",
    "communication",
    "strength",
    "stamina",
    "dexterity",
    "quickness",
)


def combine(human: int, beast: int) -> int:
    """One Characteristic in animal form: the lower when both are negative,
    the higher when both are positive, else their sum (p. 23)."""
    if human < 0 and beast < 0:
        return min(human, beast)
    if human > 0 and beast > 0:
        return max(human, beast)
    return human + beast


def animal_characteristics(
    human: Characteristics, beast: Mapping[str, int], *, lycanthrope: bool = False
) -> dict[str, int]:
    """The magus's Characteristics in his animal form, from his own and the
    species' (`beast`, keyed by Characteristic, "cunning" for its Cunning):
    the magus keeps his Intelligence, a lycanthrope takes the beast's
    Cunning (p. 23)."""
    found = {
        name: combine(getattr(human, name), beast.get(name, 0)) for name in COMBINED
    }
    if lycanthrope:
        found["cunning"] = beast.get("cunning", 0)
    else:
        found["intelligence"] = human.intelligence
    return found


# -- The Inner Mysteries (pp. 28-32) ------------------------------------------------

INNER_MYSTERIES: dict[str, str] = {
    EPITOME: "Mystery of the Epitome",
    CHIMERA: "Mystery of the Chimera",
    ANIMA: "Mystery of the Anima",
}
#: The Lore a magus needs to seek the Inner Heartbeast (p. 28), and the
#: Great Beast's scores as Mystagogue (p. 30).
INNER_LORE_LEAST = 5
GREAT_BEAST_PRESENCE = 2
GREAT_BEAST_LORE = 8
#: The Adventure experience the Great Beast's trials must earn (p. 30).
QUEST_XP = 10
#: The Epitome's raise to one Characteristic: the inner heartbeast's over
#: the species', and the human form's (p. 30). The app follows the rule
#: text: the outer heartbeast changes only through the human form's +1,
#: combined as on p. 23, so the book's example ends with an outer
#: Perception of +2 (the eagle's base, and +1 above where it started) and
#: an inner +5. Errata p. 54 gives the outer heartbeast +5, but that is the
#: inner figure and contradicts the rule; Through the Aegis p. 14 (Hilde
#: Oddfish: Strength +7 outer, +10 inner) applies the rule as written.
EPITOME_BEAST, EPITOME_HUMAN = 3, 1
#: The Chimera's Minor Virtue by the heartbeast's temperament (p. 32).
CHIMERA_VIRTUE: dict[str, str] = {
    SANGUINE: "vf_lightning_reflexes",
    CHOLERIC: "vf_reserves_of_strength",
    MELANCHOLIC: "vf_lesser_immunity",
    PHLEGMATIC: "vf_intuition",
}
#: The Anima's elements and the Form that then affects him (p. 32);
#: other elements are built on these.
ANIMA_FORMS: dict[str, str] = {
    "stone": "Terram",
    "earth": "Terram",
    "air": "Auram",
    "fire": "Ignem",
    "water": "Aquam",
}
#: A Mythic Feat's cost in Confidence Points (p. 31).
MYTHIC_FEAT_COST = 1


def has(magus: Character, vf_id: str) -> bool:
    return lab_virtues.has(magus, vf_id)


def is_bjornaer(magus: Character) -> bool:
    return has(magus, HEARTBEAST)


def inner_heartbeast(magus: Character) -> str:
    """The Inner Mystery the magus holds ("" for none)."""
    return next((vf for vf in INNER_MYSTERIES if has(magus, vf)), "")


def cult_lore(magus: Character) -> int:
    """The magus's House Bjornaer Lore (the best of its names)."""
    best = 0
    for name in LORE_NAMES:
        level, bonus = ability_score(magus, name)
        best = max(best, level + bonus)
    return best


def epitome_characteristic(species: int, human: int) -> tuple[int, int]:
    """The Epitome's raised Characteristic: the inner heartbeast's (the
    species' + 3, the magus's own ignored) and the human form's (+1)
    (p. 30). The outer heartbeast's follows from the new human score as
    usual (combine), as the rule text says; the Errata's (p. 54) reworded
    example is not followed (see EPITOME_BEAST)."""
    return species + EPITOME_BEAST, human + EPITOME_HUMAN


def chimera_size(outer: int, added: int) -> int:
    """A chimera's Size: a Size above the outer heartbeast's, or the added
    creature's when that is larger (p. 31)."""
    return max(outer + 1, added)


def great_beast_might(magus: Character) -> int:
    """The Magic Might of the Great Beast a magus becomes at Final Twilight:
    5 x Heartbeast with any Inner Mystery, else none (he becomes a
    mundane beast) (p. 24)."""
    return 5 * heartbeast_score(magus) if inner_heartbeast(magus) else 0


# -- Refinements (pp. 32-33) ----------------------------------------------------------


@dataclass(frozen=True)
class Refinement:
    """A Refinement of the inner heartbeast: its Ease Factor, the step
    each earlier one of its kind adds, the vis eaten for it ("" for the
    Form of the power), and the Inner Mystery that resonates with it."""

    key: str
    name: str
    ease: int
    vis: str
    resonant: str
    step: int = 0


REFINEMENTS: dict[str, Refinement] = {
    r.key: r
    for r in (
        Refinement("size", "Changing Size", 18, "Muto", CHIMERA, step=3),
        Refinement(
            "characteristic", "Increasing a Characteristic", 18, "Creo", EPITOME, 3
        ),
        Refinement("quality", "Acquiring a Quality", 15, "Animal", CHIMERA),
        Refinement("minor_virtue", "Acquiring a Minor Virtue", 18, "Vim", EPITOME),
        Refinement("major_virtue", "Acquiring a Major Virtue", 30, "Vim", EPITOME),
        Refinement("minor_power", "Acquiring a Minor Power", 21, "", ANIMA),
        Refinement("major_power", "Acquiring a Major Power", 30, "", ANIMA),
    )
}
#: The Virtues the inner heartbeast may acquire (p. 33); the storyguide
#: may extend the lists.
MINOR_VIRTUES = (
    "vf_enduring_constitution",
    "vf_keen_sense_of_smell",
    "vf_keen_vision",
    "vf_lesser_immunity",
    "vf_lightning_reflexes",
    "vf_long_winded",
    "vf_magic_sensitivity",
    "vf_perfect_balance",
    "vf_piercing_gaze",
    "vf_rapid_convalescence",
    "vf_reserves_of_strength",
    "vf_second_sight",
    "vf_sharp_ears",
    "vf_tough",
    "vf_wilderness_sense",
)
MAJOR_VIRTUES = ("vf_greater_immunity", "vf_ways_of_the_land")
#: The embryonic Script (p. 32): an ancestor site +3, vis eaten and a
#: Warping Point +1, the Virtue only in the inner heartbeast's form +3; the
#: inner heartbeast's resonance +3; the storyguide's sympathy for an added
#: component -5 to +5 (p. 33).
EMBRYONIC_PARTS: tuple[tuple[str, int], ...] = (
    ("A season at an ancestor site", 3),
    ("Vis eaten, a Warping Point", 1),
    ("Used only in the inner heartbeast's form", 3),
)
EMBRYONIC_BONUS = sum(bonus for _, bonus in EMBRYONIC_PARTS)
RESONANT_BONUS = 3
SYMPATHY_RANGE = (-5, 5)
REFINEMENT_WARPING = 1


def refinement_ease(key: str, earlier: int = 0) -> int:
    """A Refinement's Ease Factor: its own, + 3 for each earlier increase
    of the same Size or Characteristic (p. 33)."""
    found = REFINEMENTS[key]
    return found.ease + found.step * max(0, earlier)


def refinement_vis(ease: int) -> int:
    """The pawns eaten: one per three points of the Ease Factor, a part
    counting whole (p. 32)."""
    return round_up(ease / 3)


def resonant_bonus(magus: Character, key: str) -> int:
    """+3 when the magus's inner heartbeast resonates with the Refinement
    (p. 32)."""
    found = REFINEMENTS.get(key)
    return RESONANT_BONUS if found and inner_heartbeast(magus) == found.resonant else 0


def embryonic_script(magus: Character, key: str, sympathy: int = 0) -> Breakdown:
    """The embryonic Script's bonus for a Refinement: +7, the resonance,
    and the storyguide's sympathy for an added component (-5 to +5)."""
    lines = [
        Line(name, amount=bonus, source=REFINEMENT_SOURCE)
        for name, bonus in EMBRYONIC_PARTS
    ]
    if resonant := resonant_bonus(magus, key):
        lines.append(
            Line(
                f"Resonance ({INNER_MYSTERIES[inner_heartbeast(magus)]})",
                amount=resonant,
                source=REFINEMENT_SOURCE,
            )
        )
    least, most = SYMPATHY_RANGE
    if sympathy:
        lines.append(
            Line(
                "Sympathy (storyguide)",
                amount=max(least, min(most, sympathy)),
                source=REFINEMENT_SOURCE,
            )
        )
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def power_problems(
    key: str, effect_level: int, lab_total: int, *, constant: bool = False
) -> list[str]:
    """What stops a Power's Refinement (p. 33): the Lab Total in its Arts
    must exceed the effect's level, and a Major Power is never constant."""
    found: list[str] = []
    if key not in ("minor_power", "major_power"):
        return found
    if lab_total <= effect_level:
        found.append(
            f"The Lab Total {lab_total} must exceed the Power's level "
            f"{effect_level}: its formulation is beyond him."
        )
    if key == "major_power" and constant:
        found.append("A Major Power can't have a constant effect.")
    return found


# -- Initiation (pp. 24-30) -------------------------------------------------------------

TWELVE_YEARS = "The Ritual of Twelve Years"
SECRET_NAME_SCRIPT = "Secret Name"
THERIOMORPHY_SCRIPT = "Theriomorphy"
SENSORY_SCRIPT = "Sensory Magic"
TRIAL, DEED, OATH = (
    "Clan Mystery: The Trial of (Name)",
    "Clan Mystery: The Deed of (Name)",
    "Clan Mystery: The Oath of (Name)",
)
TRIAL_MAJOR = "Clan Mystery: The Trial of (Name), with a Major Ordeal"
INNER_SCRIPT = "The Mystery of the Inner Heartbeast"
REFINEMENT_PREFIX = "Refinement: "
#: The Ritual of Twelve Years' Script bonus, before the witnesses (p. 26).
TWELVE_YEARS_BONUS = 6
#: A Clan Mystery's Mystagogue's least Presence + House Bjornaer Lore (p. 25).
CLAN_MYSTAGOGUE_LEAST = 8
HOUSE_SCRIPTS = (TWELVE_YEARS, SECRET_NAME_SCRIPT, THERIOMORPHY_SCRIPT, SENSORY_SCRIPT)
CLAN_SCRIPTS = (TRIAL, TRIAL_MAJOR, DEED, OATH)
#: The House's Mysteries by Virtue: the House Mysteries need the Heartbeast
#: (all but Secret Name, which any with Magic Resistance may take).
NEEDS_HEARTBEAST = (THERIOMORPHY, SENSORY_MAGIC, *INNER_MYSTERIES)


def script_name(script_key: str) -> str:
    """The Script's name when a plan's hedge Script is one of the House's
    ("" otherwise)."""
    tradition, _, name = script_key.partition("/")
    return name if tradition == CULT_TRADITION else ""


def refinement_key(script_key: str) -> str:
    """The Refinement a House Script Initiates ("" for none)."""
    name = script_name(script_key)
    if not name.startswith(REFINEMENT_PREFIX):
        return ""
    wanted = name.removeprefix(REFINEMENT_PREFIX)
    return next((r.key for r in REFINEMENTS.values() if r.name == wanted), "")


def knows_by_rule(script_key: str) -> bool:
    """Whether the Script's Ease Factor is its Target as printed: the Great
    Beast knows the Inner Mystery sought (p. 30), and a Refinement's Ease
    Factor is its own (p. 33)."""
    return script_name(script_key) == INNER_SCRIPT or bool(refinement_key(script_key))


def stand_in(
    initiate: Character, mystagogue: Character, script_key: str
) -> tuple[int, int] | None:
    """The Great Beast's Presence and Lore, standing in as Mystagogue when
    the Inner Heartbeast's Initiation names no other (p. 30); None
    otherwise."""
    if mystagogue is initiate and script_name(script_key) == INNER_SCRIPT:
        return GREAT_BEAST_PRESENCE, GREAT_BEAST_LORE
    return None


def script_extra(initiate: Character, script_key: str) -> int:
    """What a House Script adds beyond its printed bonus: a Refinement's
    resonance with the inner heartbeast (p. 32)."""
    key = refinement_key(script_key)
    return resonant_bonus(initiate, key) if key else 0


def participation(temperament: str, witnesses: list[str]) -> int:
    """The Ritual of Twelve Years' Participation Modifier: +1 for each
    witness (the Mystagogue included) whose heartbeast shares the
    probationer's temperament, -1 for each opposed (p. 26)."""
    opposed = OPPOSED.get(temperament, "")
    return sum(1 for w in witnesses if w == temperament) - sum(
        1 for w in witnesses if w == opposed
    )


def twelve_years_total(mystagogue: Character, participation_modifier: int) -> Breakdown:
    """The Ritual of Twelve Years' Initiation Total: Presence + House
    Bjornaer Lore + 6 + the Participation Modifier, against 15 (p. 26)."""
    lines = [
        Line(
            "Presence",
            amount=mystagogue.characteristics.presence,
            source=INITIATION_SOURCE,
        ),
        Line(CULT_LORE, amount=cult_lore(mystagogue), source=INITIATION_SOURCE),
        Line(
            "Script (ancestor site, the familiar forgone)",
            amount=TWELVE_YEARS_BONUS,
            source=INITIATION_SOURCE,
        ),
    ]
    if participation_modifier:
        lines.append(
            Line(
                "Participation Modifier",
                amount=participation_modifier,
                source=INITIATION_SOURCE,
            )
        )
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def gives_heartbeast(vf_id: str, script_key: str) -> bool:
    return vf_id == HEARTBEAST or script_name(script_key) == TWELVE_YEARS


def seeks_inner(vf_id: str, script_key: str) -> bool:
    return vf_id in INNER_MYSTERIES or script_name(script_key) == INNER_SCRIPT


#: A character's Diary activities that show he has bound a familiar:
#: binding or strengthening one, and empowering its bond (the season
#: labels of rules.activities' bind_familiar and empower_bond).
FAMILIAR_DIARY = ("Bind or strengthen a familiar", "Empower the familiar's bond")


def familiar_bound(saga: Saga, magus: Character, ever_bound: bool = False) -> str:
    """How the app knows the magus has ever bound a familiar ("" when it
    doesn't): one bound to him now, a familiar season in his Diary (a
    familiar released or dead is no longer in the saga), or the plan's
    `ever_bound` tick for one the app can't see (HoH:MC p. 24)."""
    if saga.familiar_of(magus.id) is not None:
        return "has bound a familiar"
    entry = next((e for e in magus.diary if e.activity in FAMILIAR_DIARY), None)
    if entry is not None:
        return f"bound a familiar ({entry.season} {entry.year}, in his Diary)"
    return "has bound a familiar before" if ever_bound else ""


def mystery_problem(
    saga: Saga,
    initiate: Character,
    vf_id: str,
    script_key: str,
    *,
    ever_bound: bool = False,
) -> str:
    """What the House's rules say stops an Initiation ("" if nothing).
    `ever_bound`: the plan says the Initiate has bound a familiar the app
    can't see."""
    if gives_heartbeast(vf_id, script_key):
        if is_bjornaer(initiate):
            return (
                f"{initiate.name} has the Heartbeast already: the Ritual of "
                f"Twelve Years is never repeated ({INITIATION_SOURCE})."
            )
        bound = familiar_bound(saga, initiate, ever_bound)
        if bound:
            return (
                f"{initiate.name} {bound}: the Ritual of Twelve Years fails for "
                f"one who has ever bound a familiar, even one since dead (DE p. "
                f"234; {MC} pp. 18, 24)."
            )
        other = [vf for vf in OTHER_HOUSE_MYSTERIES if has(initiate, vf)]
        if other:
            return (
                f"{initiate.name} is an Initiate of another House's Mystery: the "
                f"House refuses him ({MC} p. 18)."
            )
        return ""
    if (vf_id in NEEDS_HEARTBEAST or seeks_inner(vf_id, script_key)) and not (
        is_bjornaer(initiate)
    ):
        return (
            f"{initiate.name} hasn't the Heartbeast: only a Bjornaer learns "
            f"the House's Mysteries ({INITIATION_SOURCE})."
        )
    if seeks_inner(vf_id, script_key):
        held = inner_heartbeast(initiate)
        if held:
            return (
                f"{initiate.name} has an inner heartbeast already "
                f"({INNER_MYSTERIES[held]}): a magus has one ({INNER_SOURCE})."
            )
        if cult_lore(initiate) < INNER_LORE_LEAST:
            return (
                f"{initiate.name} needs {CULT_LORE} {INNER_LORE_LEAST} to seek "
                f"the Inner Heartbeast ({INNER_SOURCE})."
            )
    if refinement_key(script_key) and not inner_heartbeast(initiate):
        return (
            f"{initiate.name} has no inner heartbeast to refine ({REFINEMENT_SOURCE})."
        )
    return ""


def mystagogue_problem(
    initiate: Character, mystagogue: Character, script_key: str, reduction: int = 0
) -> str:
    """Who may lead a House Script ("" if he may): Clan Ilfetu the House
    Mysteries (p. 25); a Clan Mystery's Mystagogue needs Presence + Lore 8,
    less the Initiate's past Ordeal's reduction (p. 25); a Refinement the
    magus himself (p. 32). None but a Refinement and the Inner Heartbeast
    (whose Great Beast stands in) is self-initiated."""
    name = script_name(script_key)
    if not name:
        return ""
    if refinement_key(script_key):
        if mystagogue is not initiate:
            return (
                "A Refinement is the magus's own work: he Initiates himself "
                f"({REFINEMENT_SOURCE})."
            )
        return ""
    if name == INNER_SCRIPT:
        return ""
    if mystagogue is initiate:
        return f"{name} needs a Mystagogue: choose one ({INITIATION_SOURCE})."
    if name in HOUSE_SCRIPTS and not has(mystagogue, CLAN_ILFETU):
        return (
            f"{mystagogue.name} isn't of Clan Ilfetu, who Initiate the House "
            f"Mysteries ({INITIATION_SOURCE})."
        )
    if name in CLAN_SCRIPTS:
        least = CLAN_MYSTAGOGUE_LEAST - max(0, reduction)
        if mystagogue.characteristics.presence + cult_lore(mystagogue) < least:
            return (
                f"{mystagogue.name}'s Presence + {CULT_LORE} is below {least}: "
                f"he can't Initiate a Clan Mystery ({INITIATION_SOURCE})."
            )
    return ""


def ordeal_problem(
    initiate: Character,
    vf_id: str,
    script_key: str,
    gained: tuple[str, str, str] | None,
    lost_id: str,
) -> str:
    """The Inner Heartbeast's Ordeal ("" if it will do): a Major Hermetic or
    Supernatural Flaw (p. 30; `gained`: the Flaw's id, tier and category),
    or for a known shapechanger the loss of his Skinchanger or Shapeshifter
    (p. 17)."""
    if not seeks_inner(vf_id, script_key):
        return ""
    held = [vf for vf in SHAPECHANGERS if has(initiate, vf)]
    if held:
        if lost_id in held:
            return ""
        return (
            f"{initiate.name} can change shape: the ancestors reject him unless "
            f"the Ordeal takes his Skinchanger or Shapeshifter ({MC} p. 17)."
        )
    if gained is None:
        return (
            "The Inner Heartbeast's Ordeal is a Major Hermetic or Supernatural "
            f"Flaw: choose it ({INNER_SOURCE})."
        )
    _, tier, category = gained
    if tier != "Major" or category not in ("Hermetic", "Supernatural"):
        return (
            "The Inner Heartbeast's Ordeal is a Major Hermetic or Supernatural "
            f"Flaw ({INNER_SOURCE})."
        )
    return ""


def initiation_notes(initiate: Character, vf_id: str, script_key: str) -> list[str]:
    """What an Initiation's season notes besides its Total."""
    notes: list[str] = []
    name = script_name(script_key)
    if name == TWELVE_YEARS:
        notes.append(
            "The Ritual of Twelve Years: add the Participation Modifier as the "
            "plan's other modifier, +1 for each witness (the Mystagogue "
            "included) sharing the probationer's temperament, -1 for each "
            f"opposed ({INITIATION_SOURCE})."
        )
    if name == INNER_SCRIPT:
        notes.append(
            f"The Great Beast's trials must earn {QUEST_XP} Adventure experience, "
            "spent contemplating them rather than on Abilities; the Ordeal is "
            f"the Great Beast's choice of Flaw ({INNER_SOURCE})."
        )
    key = refinement_key(script_key)
    if key:
        found = REFINEMENTS[key]
        ease = found.ease
        vis = found.vis or "the Power's Form"
        step = (
            f" Each earlier increase adds {found.step} to the Ease Factor: take "
            f"{found.step} each from the plan's other modifier."
            if found.step
            else ""
        )
        notes.append(
            f"{found.name}: eat {refinement_vis(ease)} pawns of {vis} vis (one "
            f"per three points of the Ease Factor) and gain {REFINEMENT_WARPING} "
            "Warping Point; it changes only the inner heartbeast, so note it on "
            f"the sheet by hand.{step} ({REFINEMENT_SOURCE})"
        )
    if gives_heartbeast(vf_id, script_key) and not vf_id:
        notes.append("Choose Heartbeast as the Virtue initiated so it is added.")
    return notes


def outcome(initiate: Character, vf_id: str, script_key: str) -> tuple[int, str, str]:
    """What a successful Initiation gives besides its Virtue: the
    experience in Heartbeast (5, its score 1, for the Ritual of Twelve
    Years when he has none), the Ordeal it counts as ("Minor": the familiar
    forgone, after character creation, p. 26) and a note."""
    if not gives_heartbeast(vf_id, script_key):
        return 0, "", ""
    xp = 0 if heartbeast_score(initiate) else 5
    return (
        xp,
        "Minor",
        "The probationer takes his heartbeast's shape at once and gains "
        f"Heartbeast 1; the familiar forgone counts as a Minor Ordeal "
        f"({INITIATION_SOURCE}).",
    )


# -- Sensory Magic in the lab (p. 28) -----------------------------------------------------

SENSORY_TARGETS = ("Flavor", "Texture", "Scent", "Sound", "Spectacle")
#: The Targets of the magical senses (DE pp. 113-114).
SENSE_TARGETS = ("Taste", "Touch", "Smell", "Hearing", "Vision")


def sensory_line(magus: Character, spell: Spell | SpellDesign | None) -> Line | None:
    """Heartbeast on the Lab Total of a Sensory Magic initiate inventing a
    spell with a Sensory Target, or an Intellego spell of a magical sense
    (p. 28)."""
    if spell is None or not has(magus, SENSORY_MAGIC):
        return None
    sensory = spell.target in SENSORY_TARGETS
    sense = spell.technique.lower().startswith("in") and spell.target in SENSE_TARGETS
    score = heartbeast_score(magus)
    if not (sensory or sense) or not score:
        return None
    return Line(f"{ABILITY} (Sensory Magic)", amount=score, source=SENSORY_SOURCE)


# -- Reminders -----------------------------------------------------------------------------


def reminders(magus: Character) -> list[str]:
    """The House's form-changing rolls, for the sheet's reminders."""
    if not is_bjornaer(magus):
        return []
    total = int(change_total(magus).total)
    found = [
        f"Heartbeast: Stamina + Heartbeast ({total}) against 3 + the magnitude "
        "to change form despite a shapechange or an Aegis, dispelling the "
        "shapechange (DE p. 234)."
    ]
    if line := temperament_line(magus):
        found.append(line)
    if has(magus, THERIOMORPHY):
        found.append(
            f"Theriomorphy: Stamina + Heartbeast ({total}) against "
            f"{THERIOMORPHY_EASE}, a round, to give the human form one of the "
            "heartbeast's Qualities or Virtues (and back); not hidden, and a "
            f"constant mystical effect for Warping ({MC} p. 27)."
        )
    held = inner_heartbeast(magus)
    if held:
        found.append(
            f"{INNER_MYSTERIES[held]}: from the outer heartbeast, Stamina + "
            f"Heartbeast ({total}) against {INNER_EASE}, a round defending only, "
            f"to take the inner heartbeast; back needs no roll ({MC} p. 32). At "
            f"Final Twilight a Great Beast of Magic Might {great_beast_might(magus)} "
            f"({MC} p. 24)."
        )
    return found
