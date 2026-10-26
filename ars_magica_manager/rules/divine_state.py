"""What Divine favour a character holds right now, read from his records:
a mystic's path and the form his Divine Ascent takes, and a Church
office's Commanding Aura withdrawn. Kept apart from rules.mysticism, and
importing only the models, so the sheet's Soak and Magic Resistance
(rules.derived, rules.penetration) can read it.

- A mystic's path (The Church pp. 20-24): contemplative mysticism always
  ascends to the Divine Form, monistic mysticism to the Divine Gloom; a
  monist tests for the Ascent at a single Warping Point (p. 23), a
  contemplative at 2 (p. 21). Once a Divine Form Ascent has happened
  (p. 21, summarizing Realms of Power: The Divine p. 64): the Warping
  Score adds to True Faith's Magic Resistance; physical Soak gains that
  Magic Resistance / 5, or the Warping Score / 5 without True Faith; a
  Penetration bonus of the Warping Score + 5 x True Faith; 3 x the
  Warping Score extra botch dice on any impious act; a Light wound for a
  venial sin, a Medium one for a mortal sin, healed only naturally; and a
  continual Commanding Aura (Penetration 0, Voice).
- The Commanding Aura withdrawn (DE p. 74; p. 420; Antagonists p. 38): a
  legatus missus who delays or strays from his mission loses it until he
  has done penance; one excommunicated by God's will loses an office's
  Magic Resistance and Soak until penance.

Records (no new saved field): the path is a finished progress record of
kind "mystic path" (its points the Ascents undergone on it), finished so
the Planning tab's work in hand leaves it out; the aura withdrawn a
finished record of kind "commanding aura withdrawn".
"""

from __future__ import annotations

from ..models import Character, Progress

SOURCE = (
    "The Church, Christian Mysticism, pp. 20-24; Realms of Power: The Divine, "
    "Divine Form and Divine Gloom, pp. 63-64; DE pp. 74, 420; Antagonists p. 38"
)

PATH_KIND = "mystic path"
CONTEMPLATIVE = "Contemplative mysticism"
MONISTIC = "Monistic mysticism"
PATHS = (CONTEMPLATIVE, MONISTIC)
#: The form of Divine Ascent each path always takes (pp. 21, 23).
FORMS = {CONTEMPLATIVE: "Divine Form", MONISTIC: "Divine Gloom"}
#: The Warping Points from one event that test for the Ascent (pp. 21, 23).
TRIGGERS = {CONTEMPLATIVE: 2, MONISTIC: 1}
#: The usual trigger: 2 or more points at once (RoP: The Divine p. 63).
USUAL_TRIGGER = 2
#: Divine Form: botch dice for each Warping Score on an impious act.
IMPIOUS_BOTCH_PER_WARPING = 3
#: Divine Form: Penetration for each point of True Faith.
PENETRATION_PER_FAITH = 5
#: True Faith's Magic Resistance per point of its Score (DE p. 419).
FAITH_RESISTANCE = 10

AURA_WITHDRAWN = "commanding aura withdrawn"


def path_record(character: Character) -> Progress | None:
    return next((p for p in character.progress if p.kind == PATH_KIND), None)


def path(character: Character) -> str:
    """The mystic path he follows ("" for none)."""
    record = path_record(character)
    return record.name if record is not None and record.name in PATHS else ""


def set_path(character: Character, chosen: str) -> None:
    """Follow `chosen` ("" to follow none)."""
    character.progress[:] = [p for p in character.progress if p.kind != PATH_KIND]
    if chosen in PATHS:
        character.progress.append(Progress(PATH_KIND, chosen, done=True))


def ascents(character: Character) -> int:
    """The Divine Ascents he has undergone on his path."""
    record = path_record(character)
    return record.points if record is not None else 0


def note_ascent(character: Character) -> None:
    record = path_record(character)
    if record is not None:
        record.points += 1


def ascent_form(character: Character) -> str:
    """The Ascent's form his path gives ("" off a path)."""
    return FORMS.get(path(character), "")


def trigger(character: Character) -> int:
    """The Warping Points from one event that test him for the Ascent."""
    return TRIGGERS.get(path(character), USUAL_TRIGGER)


def divine_form(character: Character) -> bool:
    """A contemplative who has undergone his Divine Form."""
    return path(character) == CONTEMPLATIVE and ascents(character) > 0


def divine_gloom(character: Character) -> bool:
    """A monist who has undergone his Divine Gloom."""
    return path(character) == MONISTIC and ascents(character) > 0


def form_resistance(character: Character) -> int:
    """What the Divine Form adds to True Faith's Magic Resistance: the
    Warping Score, with a True Faith Score (p. 21)."""
    if not divine_form(character) or character.background.true_faith_score <= 0:
        return 0
    return max(0, character.aging.warping_score)


def form_soak(character: Character) -> int:
    """The Divine Form's Soak: True Faith's Magic Resistance (with the
    Warping Score) / 5, or the Warping Score / 5 without it (p. 21),
    rounded down."""
    if not divine_form(character):
        return 0
    faith = character.background.true_faith_score
    warping = max(0, character.aging.warping_score)
    if faith > 0:
        return (FAITH_RESISTANCE * faith + warping) // 5
    return warping // 5


def form_penetration(character: Character) -> int:
    """The Divine Form's Penetration bonus: Warping Score + 5 x True Faith."""
    if not divine_form(character):
        return 0
    return max(0, character.aging.warping_score) + PENETRATION_PER_FAITH * max(
        0, character.background.true_faith_score
    )


def impious_botch_dice(character: Character) -> int:
    """Extra botch dice on an impious act in the Divine Form."""
    if not divine_form(character):
        return 0
    return IMPIOUS_BOTCH_PER_WARPING * max(0, character.aging.warping_score)


# -- the Commanding Aura withdrawn --


def aura_withdrawn(character: Character) -> bool:
    return any(p.kind == AURA_WITHDRAWN for p in character.progress)


def set_aura_withdrawn(character: Character, withdrawn: bool, why: str = "") -> None:
    character.progress[:] = [p for p in character.progress if p.kind != AURA_WITHDRAWN]
    if withdrawn:
        character.progress.append(
            Progress(AURA_WITHDRAWN, why.strip() or "Withdrawn", done=True)
        )
