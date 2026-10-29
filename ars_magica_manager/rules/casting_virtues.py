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

import re
from collections.abc import Callable

from ..arts import ART_ABBREVIATIONS, FORMS, TECHNIQUES
from ..models import Character
from . import (
    bjornaer,
    breakthroughs_moh,
    common_magics,
    fenicil,
    house_discoveries,
    house_magic,
    lab_virtues,
)
from .rounding import round_down

SOURCE = "Ars Magica Definitive Edition, Chapter 4: Virtues and Flaws, pp. 91-152"

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
FOCI = (
    "vf_major_magical_focus",
    "vf_major_magical_focus_sign_planet",
    "vf_minor_magical_focus",
    "vf_minor_magical_focus_house",
)
DELETERIOUS = "vf_deleterious_circumstances"
CHOREOGRAPHY = "vf_mystical_choreography"
DREAM_MAGIC = "vf_dream_magic"
HERMETIC_SACRIFICE = "vf_hermetic_sacrifice"

LIFE_BOOST_PER_LEVEL = 5


def _params(magus: Character, vf_id: str, key: str) -> list[str]:
    return [
        vf.params.get(key, "")
        for vf in magus.virtues_flaws
        if vf.vf_id == vf_id and vf.params.get(key)
    ]


def _named(what: str, names: list[str]) -> str:
    return f"{what} ({', '.join(names)})" if names else what


HEARTBEAST = "vf_heartbeast"
VERDITIUS_MAGIC = "vf_verditius_magic"


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
            "Hermetic Geometry: +3 casting a spell that traces a circle or line, "
            "+3 more cast ceremonially in a regular figure (TMRE p. 94)."
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
    if has(magus, SPELL_IMPROVISATION) or has(magus, FAERIE_RAISED):
        found.append(
            "Spell Improvisation: a Spontaneous spell like a Formulaic one known "
            "adds that spell's magnitude."
        )
    foci = [
        str(vf.params.get("focus") or vf.params.get("house") or "")
        for vf in magus.virtues_flaws
        if vf.vf_id in FOCI
    ]
    if foci:
        found.append(
            _named("Magical Focus", [f for f in foci if f])
            + ": the lower Art counts twice for a spell in its field (DE p. 94)."
        )
    if has(magus, DELETERIOUS):
        found.append(
            _named(
                "Deleterious Circumstances",
                _params(magus, DELETERIOUS, "circumstance"),
            )
            + ": every magic total but Magic Resistance halved while they hold "
            "(DE p. 125)."
        )
    if has(magus, CHOREOGRAPHY):
        found.append(
            "Mystical Choreography: ceremonial casting takes five minutes a "
            "magnitude, one in any prepared space (DE p. 99)."
        )
    if has(magus, HEARTBEAST):
        found.append(
            "Heartbeast: in animal form a spell is cast with no words or "
            "gestures, normally -15 (DE p. 234)."
        )
    if has(magus, VERDITIUS_MAGIC):
        found.append(
            "Verditius Magic: Formulaic and Ritual spells need his casting "
            "tools; Spontaneous spells don't (DE p. 241)."
        )
    # Dream magic and Hermetic sacrifice (The Mysteries Revised Edition).
    if has(magus, DREAM_MAGIC):
        found.append(
            "Dream Magic: in a dream his spirit casts every spell as Imaginem "
            "(Technique + Imaginem), resists with Imaginem and Parma, feels no "
            "Fatigue, and works Dream rituals spontaneously with dream vis; "
            "More's Dream Working rolls it (TMRE pp. 103-106)."
        )
    if has(magus, HERMETIC_SACRIFICE):
        found.append(
            "Hermetic Sacrifice: a pure beast offered on a deity's altar stands "
            "in for 1 (a lamb) to 6 (a lion) pawns of a Ritual summoning that "
            "deity there (TMRE p. 117)."
        )
    found += [note(magus) for vf_id, note in NOTES.items() if has(magus, vf_id)]
    found += common_magics.reminders(magus)
    found += house_discoveries.reminders(magus)
    found += fenicil.reminders(magus)
    # House Bjornaer's form-changing rolls follow the breakthroughs', then
    # House Mercere's Mutantum and Tamed Magic.
    found += (
        breakthroughs_moh.reminders(magus)
        + bjornaer.reminders(magus)
        + house_magic.reminders(magus)
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


# -- the rest of the casting Virtues and Flaws (DE pp. 70-145) --

BOOSTED = "vf_boosted_magic"
FLEXIBLE = "vf_flexible_formulaic_magic"
ATLANTEAN = "vf_atlantean_magic"
ENDURING = "vf_enduring_magic"
EXOTIC = "vf_exotic_casting"
FAERIE_RAISED = "vf_faerie_raised_magic"
HARNESSED = "vf_harnessed_magic"
TETHERED = "vf_tethered_magic"
LIFE_LINKED = "vf_life_linked_spontaneous_magic"
IMBUED = "vf_imbued_with_the_spirit_of_form"
PAINFUL = "vf_painful_magic"
SLOW_CASTER = "vf_slow_caster"
SHORT_LIVED = "vf_short_lived_magic"
INCOMPATIBLE = "vf_incompatible_arts"
CLUMSY_MAGIC = "vf_clumsy_magic"
INCONSTANT = "vf_inconstant_magic"
FAERIE_MAGIC = "vf_faerie_magic"
SPELL_TIMING = "vf_spell_timing"
SECRET_NAME = "vf_secret_name"
#: The Flaws that take 3 off every Finesse roll, aiming included (DE pp.
#: 122, 134).
FINESSE_FLAWS = (CLUMSY_MAGIC, INCONSTANT)
FINESSE_PENALTY = -3


def finesse_penalty(magus: Character) -> int:
    """What Clumsy Magic and Inconstant Magic take off a Finesse roll, -3
    each (DE pp. 122, 134)."""
    return FINESSE_PENALTY * sum(
        1 for vf in magus.virtues_flaws if vf.vf_id in FINESSE_FLAWS
    )


_ART_WORDS = {
    **{a.casefold(): a for a in (*TECHNIQUES, *FORMS)},
    **{abbr.casefold(): art for art, abbr in ART_ABBREVIATIONS.items()},
}


def incompatible_pairs(magus: Character) -> set[frozenset[str]]:
    """The Technique and Form pairs Incompatible Arts rules out, read from
    each instance's Arts ("Intellego Herbam, Intellego Animal", or "InHe,
    InAn")."""
    pairs: set[frozenset[str]] = set()
    for text in _params(magus, INCOMPATIBLE, "arts"):
        for chunk in re.split(r"[,;/]| and ", text):
            words = re.findall(r"[A-Za-z]+", chunk)
            arts = [
                _ART_WORDS[w.casefold()] for w in words if w.casefold() in _ART_WORDS
            ]
            if not arts and len(chunk.strip()) == 4:
                arts = [
                    _ART_WORDS.get(chunk.strip()[:2].casefold(), ""),
                    _ART_WORDS.get(chunk.strip()[2:].casefold(), ""),
                ]
            techniques = [a for a in arts if a in TECHNIQUES]
            forms = [a for a in arts if a in FORMS]
            if techniques and forms:
                pairs.add(frozenset((techniques[0], forms[0])))
    return pairs


def incompatible(
    magus: Character, technique: str, form: str, requisites: tuple[str, ...] = ()
) -> bool:
    """Whether Incompatible Arts forbids a spell of these Arts: the pair may
    not be used together even as requisites (DE p. 134)."""
    pairs = incompatible_pairs(magus)
    if not pairs:
        return False
    arts = {technique, form, *requisites}
    return any(pair <= arts for pair in pairs)


def life_linked(magus: Character) -> bool:
    return lab_virtues.has(magus, LIFE_LINKED)


def painful(magus: Character) -> bool:
    return lab_virtues.has(magus, PAINFUL)


def life_linked_cost(level: int, total: int) -> int:
    """The Fatigue levels a Life-Linked Spontaneous spell costs past the
    usual one: one for each five points, or part, it falls short of the
    level declared (DE p. 91)."""
    short = level - total
    return 0 if short <= 0 else -(-short // 5)


def _imbued(magus: Character) -> str:
    forms = _params(magus, IMBUED, "form")
    return _named("Imbued with the Spirit of (Form)", forms) + (
        ": Long-Term Fatigue levels may stand in for that Form's vis, one a "
        "pawn, in casting and in the lab (not in study) (DE p. 85)."
    )


def _incompatible(magus: Character) -> str:
    pairs = sorted(
        " ".join(sorted(p, key=lambda a: a in FORMS)) for p in incompatible_pairs(magus)
    )
    return _named("Incompatible Arts", pairs) + (
        ": those Arts can't be used together, even as requisites (DE p. 134)."
    )


#: The casting reminder for each Virtue and Flaw that changes a cast in a
#: way the Casting Score can't hold (Strategy: one entry each, read by
#: reminders()).
NOTES: dict[str, Callable[[Character], str]] = {
    BOOSTED: lambda _m: (
        "Boosted Magic: a pawn of vis per magnitude raises a Formulaic spell's "
        "Range, Duration, Target or size one step, each adding a botch die; "
        "the casting is reckoned at the spell's own level (DE pp. 72-73)."
    ),
    FLEXIBLE: lambda _m: (
        "Flexible Formulaic Magic: raise or lower one of Range, Duration, "
        "Target or size one step, the casting level a magnitude with it, or "
        "swap one for another at the same level; success, Fatigue and "
        "Penetration use the new level (not Rituals) (DE p. 81)."
    ),
    ATLANTEAN: lambda _m: (
        "Atlantean Magic: Range Water-way (as Sight), Duration Storm (as "
        "Concentration) and Target Body-of-water (as Structure) (DE pp. 70-71)."
    ),
    ENDURING: lambda _m: (
        "Enduring Magic: the storyguide multiplies a spell's duration by a "
        "simple die (not Concentration, Momentary, Ring or Rituals) (DE p. 78)."
    ),
    EXOTIC: lambda _m: (
        "Exotic Casting: others tell his spell's Form only against an Ease "
        "Factor of 15, the magnitude not subtracted (DE p. 78)."
    ),
    FAERIE_RAISED: lambda _m: (
        "Faerie-Raised Magic: xp from Exposure, Adventure and Practice may "
        "invent a spell he saw mimicked (Technique + Form + Int + Magic Theory "
        "at least level - 10; magnitude + 4 xp, a third less for a similar "
        "spell) (DE pp. 79-80)."
    ),
    HARNESSED: lambda _m: (
        "Harnessed Magic: he may end any of his spells or items by "
        "concentrating, at any distance; they all end when he dies (DE p. 85)."
    ),
    TETHERED: lambda _m: (
        "Tethered Magic: control of a non-Ritual spell may pass to another or "
        "to an object; his spells and items' effects are Arcane Connections "
        "to him (DE p. 113)."
    ),
    LIFE_LINKED: lambda _m: (
        "Life-Linked Spontaneous Magic: declare the level (Penetration "
        "included) and cast fatiguing; a Fatigue level more for each 5 short, "
        "and past the last, a wound (DE p. 91)."
    ),
    IMBUED: _imbued,
    PAINFUL: lambda _m: (
        "Painful Magic: each spell cast brings a level of pain, a Fatigue "
        "penalty recovered as Fatigue (DE p. 140)."
    ),
    SLOW_CASTER: lambda _m: (
        "Slow Caster: Formulaic and Spontaneous spells take two rounds, a "
        "fast-cast one (or a Mastered spell fast-cast) one (DE p. 145)."
    ),
    SHORT_LIVED: lambda _m: (
        "Short-Lived Magic: Year lasts a Moon, Moon to the next sunrise or "
        "sunset, Sun only Diameter (DE p. 144)."
    ),
    INCOMPATIBLE: _incompatible,
    FAERIE_MAGIC: lambda _m: (
        "Faerie Magic: a Bargain spell is cast on one who has just made a "
        "bargain with him, its Penetration Total doubled, and takes effect "
        "when the bargain is broken; Until (Condition) ends with its condition, "
        "his Twilight, or his or the target's death (DE p. 237)."
    ),
    SPELL_TIMING: lambda _m: (
        "Spell Timing: a Held, Midday/Midnight or Season spell's effect and "
        "Penetration are worked out when it is released; an If (Condition) "
        "spell lapses untriggered after a year, or with his Twilight or death; "
        "a recurring spell ends before it starts again (DE pp. 239-240)."
    ),
    SECRET_NAME: lambda _m: (
        "Secret Name: no sympathetic connection works against him, and his "
        "Arcane Connections from before the Initiation have expired; one who "
        "knows the secret name doesn't subtract the spell's level from the "
        "Penetration Total against him (DE p. 235)."
    ),
    CLUMSY_MAGIC: lambda _m: (
        "Clumsy Magic: -3 to Finesse rolls, and an aiming roll of 0 is a "
        "botch (DE p. 122)."
    ),
    INCONSTANT: lambda _m: (
        "Inconstant Magic: -3 to Finesse rolls; concentration and aimed "
        "spells answer slowly, triggered ones take two minutes, and his "
        "constant items lapse at sunrise and sunset (DE p. 134)."
    ),
}
