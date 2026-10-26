"""Apotropaic spells, the demon-hunter's Vim magic, and the Mastery that
goes with them (Realms of Power: The Infernal, Chapter Twelve: Black
Magic, Apotropaic Spells and Guidelines, pp. 121-123; Errata p. 56; the
Definitive Edition's Perdo Vim guidelines, p. 369, and Demon's Eternal
Oblivion, p. 370).

What each spell does at its level, for a known spell's details:

- Demon's Eternal Oblivion (PeVi General): the demon loses Might Score
  equal to the level (DE p. 370).
- Fanning the Infernal Flames (CrVi General) restores a demon's Might
  Pool by the spell's level - 10, to its Might Score; The Wicked Jar
  (MuVi General) binds a demon of Might up to the level - 10 into a
  sealed jar (pp. 121-122). The guideline box's "level + 10" (p. 121) is
  on the base effect's level: both spells are base +2 Voice +2 Sun, four
  magnitudes, so base + 10 is the full level - 10.
- Bind the Devil's Hands (PeVi General, Room): maleficia's Casting
  Totals in the room fall by level - 15, and a demon's Powers cost
  (magnitude - 3) more Might.
- Early Punishment for the Sinful Witch (Pe(Mu)Vi(Ig) General, errata
  p. 56): destroys an Infernal effect on an infernalist of level equal to
  or lower than half the spell's level + 5 + a stress die (no botch);
  its flames do half the destroyed
  effect's level in damage. A Power without a level counts 5 x its
  Ability score or 5 x the Might spent.
- Exorcise the Filthy Spirit (PeVi General): the possessing demon's
  Possession Might Pool loses the level less its Might; at 0 it leaves.
- Lash of the Chastened Servant: PeVi 5 by the errata, 5 Might Points.
- Adjuration of the Hell-Sworn Spirit: ReVi 35 by the errata (Base 15,
  +4 Arcane), a demon of Might up to 35, by its True Name.
- Cleanse the Verminous Vis (ReVi 15): vis prava becomes sordida,
  sordida infesta, and only infesta becomes clean.
- Command the Vile Spirit (ReVi 20): Communication + Leadership + his
  Hierarchy less the demon's sets how well it obeys.
- The Rego Vim guidelines: level 5 commands a demon; summoning is level
  15 (the errata's change to the General guideline).

Apotropaic Mastery (p. 122-123): adds Mastery Score x Hierarchy to the
level of effect of a mastered spell that acts on Infernal Might directly
(Demon's Eternal Oblivion, Circular Ward Against Demons; not Aegis of
the Hearth).
"""

from __future__ import annotations

from collections.abc import Callable

from .rounding import round_down

SOURCE = (
    "Realms of Power: The Infernal, Apotropaic Spells, pp. 121-123; Errata p. 56; "
    "Ars Magica Definitive Edition, Perdo Vim, pp. 369-370"
)
MASTERY_SOURCE = "Realms of Power: The Infernal, Apotropaic Mastery, pp. 122-123"

#: The Mastery ability's name on a mastered spell (lower case).
APOTROPAIC_MASTERY = "apotropaic mastery"
#: The spells Apotropaic Mastery may be taken for: they act on Infernal
#: Might directly.
INFERNAL_MIGHT_SPELLS = frozenset(
    {
        "Demon's Eternal Oblivion",
        "Circular Ward Against Demons",
        "Fanning the Infernal Flames",
        "The Wicked Jar",
        "Exorcise the Filthy Spirit",
        "Lash of the Chastened Servant",
    }
)
#: Errata p. 56: the Rego Vim guidelines for demons.
COMMAND_GUIDELINE = 5
SUMMON_GUIDELINE = 15
#: Bind the Devil's Hands: its Room spell's offsets (p. 122).
HANDS_TOTAL_OFFSET = 15
HANDS_MIGHT_OFFSET = 3
#: Fanning the Infernal Flames and The Wicked Jar: the spell's level less
#: this (pp. 121-122).
FLAMES_OFFSET = 10
#: Early Punishment's levels added to half the spell's level (p. 122,
#: errata p. 56).
PUNISHMENT_ADDS = 5
#: Cleanse the Verminous Vis: what each kind becomes (p. 122).
CLEANSED: dict[str, str] = {
    "vis prava": "vis sordida",
    "vis sordida": "vis infesta",
    "vis infesta": "clean vis",
}


def might_pool_change(level: int) -> int:
    """Fanning the Infernal Flames: the Might Pool it restores, the
    spell's level - 10 (p. 121)."""
    return max(0, level - FLAMES_OFFSET)


def oblivion(level: int) -> int:
    """Demon's Eternal Oblivion: Might Score lost (DE p. 370)."""
    return level


def jar_holds(level: int) -> int:
    """The Wicked Jar: the most Might a demon it binds may have, the
    spell's level - 10 (p. 122)."""
    return max(0, level - FLAMES_OFFSET)


def devils_hands(level: int) -> tuple[int, int]:
    """Bind the Devil's Hands: (maleficia's Casting Total penalty, extra
    Might a demon's Power costs)."""
    return (
        max(0, level - HANDS_TOTAL_OFFSET),
        max(0, round_down(level / 5) - HANDS_MIGHT_OFFSET),
    )


def punishment_reach(level: int, die: int) -> int:
    """Early Punishment: the highest effect level it destroys, half the
    spell's level + 5 + the stress die (no botch).

    A judgement call: the errata (p. 56) puts "half" before "this spell's
    level" and ends in an ellipsis, so the literal reading halves the
    spell's level alone, not the whole sum."""
    return round_down(level / 2) + PUNISHMENT_ADDS + die


def punishment_damage(effect_level: int) -> int:
    """The white flames' damage: half the destroyed effect's level."""
    return round_down(effect_level / 2)


def power_level(*, ability_score: int = 0, might_spent: int = 0) -> int:
    """A levelless Infernal Power's effective level: 5 x its Ability
    score, or 5 x the Might spent."""
    return 5 * max(ability_score, might_spent)


def exorcism(level: int, demon_might: int) -> int:
    """Exorcise the Filthy Spirit: Possession Might Pool lost."""
    return max(0, level - demon_might)


def mastery_bonus(mastery_score: int, hierarchy_score: int) -> int:
    """Apotropaic Mastery: added to the mastered spell's level of effect."""
    return max(0, mastery_score) * max(0, hierarchy_score)


def _say(level: int) -> dict[str, Callable[[], str]]:
    hands = devils_hands(level)
    return {
        "Demon's Eternal Oblivion": lambda: (
            f"a demon it penetrates loses {oblivion(level)} Might Score"
        ),
        "Fanning the Infernal Flames": lambda: (
            f"restores {might_pool_change(level)} to a demon's Might Pool, "
            "no higher than its Might Score"
        ),
        "The Wicked Jar": lambda: (
            f"binds a demon of Might {jar_holds(level)} or less into a sealed vessel"
        ),
        "Bind the Devil's Hands": lambda: (
            f"maleficia's Casting Totals in the room -{hands[0]}; a demon's "
            f"Powers cost {hands[1]} more Might"
        ),
        "Early Punishment for the Sinful Witch": lambda: (
            "destroys an Infernal effect on an infernalist of level up to "
            f"{round_down(level / 2)} + {PUNISHMENT_ADDS} + a stress die (no "
            "botch); the flames do "
            "half its level in damage"
        ),
        "Exorcise the Filthy Spirit": lambda: (
            f"the possessing demon's Possession Might Pool loses {level} less its Might"
        ),
        "Lash of the Chastened Servant": lambda: "a demon loses 5 Might Points",
        "Adjuration of the Hell-Sworn Spirit": lambda: (
            f"summons a demon of Might {level} or less by its True Name"
        ),
        "Cleanse the Verminous Vis": lambda: (
            "vis prava becomes sordida, sordida infesta, infesta clean; it "
            "still rolls Infernal vis's botch dice"
        ),
        "Command the Vile Spirit": lambda: (
            "Communication + Leadership + his Hierarchy, less the demon's, sets "
            "how well it obeys"
        ),
    }


def effect_line(
    name: str,
    level: int | None,
    *,
    mastery_score: int = 0,
    apotropaic_mastery: bool = False,
    hierarchy_score: int = 0,
) -> str:
    """What an apotropaic spell does at its level, "" for any other spell
    or a General one with no level yet. Apotropaic Mastery raises the
    level of effect of a spell on Infernal Might."""
    if level is None:
        return ""
    bonus = 0
    if apotropaic_mastery and name in INFERNAL_MIGHT_SPELLS:
        bonus = mastery_bonus(mastery_score, hierarchy_score)
    said = _say(level + bonus).get(name)
    if said is None:
        return ""
    text = said()
    if bonus:
        text += f" (Apotropaic Mastery +{bonus} to its level of effect)"
    return f"Apotropaic: {text} (RoP: The Infernal pp. 121-122)."
