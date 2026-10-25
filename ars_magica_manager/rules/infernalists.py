"""What every infernalist shares (Realms of Power: The Infernal, Chapter
Nine: Infernal Characters, Infernalists, pp. 94-96): a Hierarchy score,
Vituperation in place of Wizard's Twilight, sacrifice and profaning.

- Hierarchy: the highest of a character's Infernal Reputations (p. 95).
- Vituperation, when an infernalist gains 2 or more Warping Points at once
  or fails to control Infernal power: Stamina + Concentration +
  Confidence Score + stress die against Warping Score + the points gained
  + Hierarchy + the local aura + stress die (no botch). Failing, he is
  torn away for as long as Twilight would last (DE's Twilight duration
  table), then makes an Aging roll adding his Warping Score; afterward his
  Confidence Score rises by 1 if below his Warping Score or Decrepitude,
  and he gains as many Confidence Points as Warping Points, unless the
  avoidance roll botched (p. 95).
- Sacrifice adds to an infernalist's effect total: an effigy of the
  target +2, an animal +4, a black animal +6, a human +8, an innocent +10;
  about an hour more to the ritual (p. 95).
- Profaning a holy thing costs a Confidence Point and makes a pawn of
  Infernal vis (usually vis infesta); a relic needs a Confidence Score
  above its Faith score, and costs no point (p. 96).
"""

from __future__ import annotations

from ..models import Character
from .scores import ability_level

SOURCE = (
    "Realms of Power: The Infernal, Chapter Nine: Infernal Characters, "
    "Infernalists, pp. 94-96"
)

INFERNAL = "Infernal"
VITUPERATION = "Vituperation"
#: Warping Points at once that call for the roll.
VITUPERATION_AT = 2

#: Each kind of sacrifice and its bonus to the effect total (p. 95).
SACRIFICES: dict[str, int] = {
    "an effigy of the target": 2,
    "an animal": 4,
    "a black animal": 6,
    "a human": 8,
    "an innocent human": 10,
}


def hierarchy(character: Character) -> int:
    """The highest of the character's Infernal Reputations (p. 95)."""
    return max(
        (r.score for r in character.reputations if r.type == INFERNAL), default=0
    )


def avoid_total(character: Character) -> int:
    """Stamina + Concentration + Confidence Score, before the stress die."""
    return (
        character.characteristics.stamina
        + ability_level(character, "Concentration")
        + character.background.confidence_score
    )


def against_total(character: Character, points: int, aura: int) -> int:
    """Warping Score + points gained + Hierarchy + aura, before the stress
    die (no botch)."""
    return character.aging.warping_score + points + hierarchy(character) + aura


def confidence_after(
    character: Character, points: int, *, botched: bool
) -> tuple[int, int]:
    """The Confidence Score rise and Confidence Points a Vituperation gives
    (p. 95)."""
    a = character.aging
    rise = (
        1
        if character.background.confidence_score < max(a.warping_score, a.decrepitude)
        else 0
    )
    return rise, 0 if botched else points


def vituperation_text(character: Character, aura: int) -> str:
    """The rolls a Vituperation calls for, worked out for the character in
    the `aura` he lives in (the local aura counts, p. 95)."""
    rise, _ = confidence_after(character, 0, botched=False)
    after = "his Confidence Score rises by 1" if rise else "his Confidence Score stays"
    return (
        f"On {VITUPERATION_AT}+ Warping Points at once: {avoid_total(character)} "
        f"+ stress die against {against_total(character, 0, aura)} (with his "
        f"home aura {aura}; use the aura where it happens) + the points "
        "+ stress die (no botch). Failing: lost for a Twilight's "
        "duration, then an Aging roll adding his Warping Score "
        f"({character.aging.warping_score}); {after}, and he gains a "
        "Confidence Point a Warping Point unless he botched (RoP: The "
        "Infernal p. 95)."
    )


def sacrifice_text() -> str:
    return (
        "Sacrifice: "
        + ", ".join(f"{what} +{bonus}" for what, bonus in SACRIFICES.items())
        + ", about an hour more (p. 95). Profaning a holy thing: a "
        "Confidence Point for a pawn of Infernal vis; a relic, a Confidence "
        "Score above its Faith score (p. 96)."
    )
