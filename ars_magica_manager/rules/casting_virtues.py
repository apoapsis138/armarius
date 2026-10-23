"""Virtues and Flaws that change casting only in some circumstances, or in
a way the Casting Score can't hold. The app works out Casting Scores but
doesn't play a cast out, so these are the reminders shown with the scores,
and the vis a Ritual takes:

- Bonuses and penalties for the moment of casting: Special Circumstances
  (+3, and to Magic Resistance), Hermetic Geometry (The Mysteries: +3 for a
  circle or line), Potent Magic (+3, or +6 Major, in its field), Cyclic
  Magic (+3 / -3 in its time), Corrupted Arts and Corrupted Spells (+3
  selfish, -3 neutral or selfless; a spell's Penetration too), Blood Haze
  (-10 to Formulaic magic in combat), Environmental Magic Condition and Short-Ranged Magic (the total
  halved: the condition holding; not touching the target).
- Life Boost: +5 to a Formulaic or Ritual Casting Total for each extra
  Fatigue level spent.
- Spell Improvisation: + the magnitude of a similar Formulaic spell known
  to a Spontaneous Casting Total.
- Diedne Magic: a non-fatiguing Spontaneous spell may be divided by 2 with
  a stress die instead of by 5; a fatiguing one doubles the lower Art
  before dividing by 2.
- A Ritual's vis: one pawn a magnitude; half with Mercurian Magic (rounded
  down, at least one); a third again with Waster of Vis; none can be used
  with Rigid Magic, which rules Rituals out.
"""

from __future__ import annotations

from ..models import Character
from . import lab_virtues
from .rounding import round_down

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Four: Virtues and Flaws "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Four:"
    "_Virtues_and_Flaws)"
)

DIEDNE = "vf_diedne_magic"
SPELL_IMPROVISATION = "vf_spell_improvisation"
LIFE_BOOST = "vf_life_boost"
SPECIAL_CIRCUMSTANCES = "vf_special_circumstances"
HERMETIC_GEOMETRY = "vf_hermetic_geometry"
CORRUPTED_ARTS = "vf_corrupted_arts"
CORRUPTED_SPELLS = "vf_corrupted_spells"
BLOOD_HAZE = "vf_blood_haze"
MERCURIAN = "vf_mercurian_magic"
RIGID = "vf_rigid_magic"

LIFE_BOOST_PER_LEVEL = 5


def _params(magus: Character, vf_id: str, key: str) -> list[str]:
    return [
        vf.params.get(key, "")
        for vf in magus.virtues_flaws
        if vf.vf_id == vf_id and vf.params.get(key)
    ]


def _named(what: str, names: list[str]) -> str:
    return f"{what} ({', '.join(names)})" if names else what


def reminders(magus: Character) -> list[str]:
    """What the magus's Virtues and Flaws add when they apply at the moment
    of casting, a sentence each (plain text)."""
    has = lab_virtues.has
    found: list[str] = []
    if has(magus, SPECIAL_CIRCUMSTANCES):
        found.append(
            _named(
                "Special Circumstances",
                _params(magus, SPECIAL_CIRCUMSTANCES, "circumstance"),
            )
            + ": +3 to Casting Scores and Magic Resistance while they hold (once, "
            "however many apply)."
        )
    potent = lab_virtues.potent_bonus(magus)
    if potent:
        field = lab_virtues.potent_field(magus)
        found.append(
            _named("Potent Magic", [field] if field else [])
            + f": +{potent} to a spell in its field."
        )
    if has(magus, HERMETIC_GEOMETRY):
        found.append(
            "Hermetic Geometry: +3 casting a spell that traces a circle or line."
        )
    if has(magus, lab_virtues.CYCLIC_POSITIVE):
        found.append(
            _named("Cyclic Magic", _params(magus, lab_virtues.CYCLIC_POSITIVE, "cycle"))
            + ": +3 in its time."
        )
    if has(magus, lab_virtues.CYCLIC_NEGATIVE):
        found.append(
            _named(
                "Cyclic Magic (Flaw)",
                _params(magus, lab_virtues.CYCLIC_NEGATIVE, "cycle"),
            )
            + ": -3 in its time."
        )
    if has(magus, CORRUPTED_ARTS) or has(magus, CORRUPTED_SPELLS):
        which = "Corrupted Spells" if has(magus, CORRUPTED_SPELLS) else "Corrupted Arts"
        if has(magus, CORRUPTED_ARTS) and has(magus, CORRUPTED_SPELLS):
            which = "Corrupted Arts and Spells"
        found.append(
            f"{which}: +3 for a selfish or sinful casting, -3 for a neutral or "
            "selfless one"
            + (
                " (a corrupted spell's Penetration too)"
                if has(magus, CORRUPTED_SPELLS)
                else ""
            )
            + "."
        )
    if has(magus, BLOOD_HAZE):
        found.append("Blood Haze: -10 to Formulaic magic in a fight.")
    if has(magus, lab_virtues.CONDITION):
        found.append(
            _named(
                "Environmental Magic Condition",
                _params(magus, lab_virtues.CONDITION, "condition"),
            )
            + ": Casting Totals halved while it holds."
        )
    if has(magus, lab_virtues.SHORT_RANGED):
        found.append(
            "Short-Ranged Magic: Casting Totals halved unless touching the target."
        )
    if has(magus, LIFE_BOOST):
        found.append(
            f"Life Boost: +{LIFE_BOOST_PER_LEVEL} to a Formulaic or Ritual Casting "
            "Total for each extra Fatigue level spent (past the last, Soak 5 a "
            "level + stress die)."
        )
    if has(magus, SPELL_IMPROVISATION):
        found.append(
            "Spell Improvisation: a Spontaneous spell like a Formulaic one known "
            "adds that spell's magnitude."
        )
    return found


def diedne_spontaneous(magus: Character) -> bool:
    return lab_virtues.has(magus, DIEDNE)


def ritual_vis(magus: Character, magnitude_pawns: int) -> int | None:
    """The pawns a Ritual takes (`magnitude_pawns`: one a magnitude), or
    None when the magus can't cast one (Rigid Magic)."""
    if lab_virtues.has(magus, RIGID):
        return None
    pawns = magnitude_pawns
    if lab_virtues.has(magus, MERCURIAN):
        pawns = max(1, round_down(pawns / 2))
    if lab_virtues.has(magus, lab_virtues.WASTER):
        pawns = lab_virtues.with_waste(pawns)
    return pawns
