"""The battle transformations of the Irish heroes (The Contested Isle,
Fomóir Blood and Battle Transformations, pp. 119-121): the Ríastradh, the
hero's light, and the fomóir and Fir Bolg blood they come from.

- Fomóir blood may show as a deformity (Aquam Monstrosity, Disfigured,
  Hunchback, Obese, or a Monstrous Appearance), often brings Giant Blood or
  Reserves of Strength, and only one of fomóir descent has the Ríastradh
  (p. 119). The Fir Bolg have Magical Blood (Human); only their royal
  caste, marked by Gentleman/woman, is free of deformity (p. 120).
- Ríastradh (Major, Supernatural) needs the Fury Story Flaw or the Major
  Wrathful Flaw. Riled, the character resists it on Stamina +
  Concentration against 6 + his Angry (or like) trait, 1 more each round
  the cause lasts. The form has three free Qualities, and one more for
  each Inferiority (each taken once): Huge (Size +2, Str +4, Qik -2),
  Large (Size +1, Str +2, Qik -1), Improved Soak (+3), Improved Initiative
  (+3 with a weapon), Improved Attack (+2 with a weapon); Deaf, Monstrous
  Appearance, Bloodlust, Reduced Defense (-3). A change of Size sheds all
  armor; no Fatigue penalties until Unconscious, when it ends (pp.
  120-121).
- Lúan láith (Minor, Supernatural): fighting on his own, allied groups
  +3 to Brave and Morale checks, enemy groups -3 (p. 121).
"""

from __future__ import annotations

SOURCE = "The Contested Isle, Fomóir Blood and Battle Transformations, pp. 119-121"

RIASTRADH = "vf_r_astradh"
LUAN_LAITH = "vf_l_an_l_ith"
#: The Flaws the Ríastradh needs one of (p. 120).
RIASTRADH_NEEDS = ("vf_fury", "vf_wrathful_major")
RESIST_EASE = 6
FREE_QUALITIES = 3

#: Each Quality of the fomóir form: (Size, Strength, Quickness, Soak,
#: Initiative, Attack) and whether it may be taken again.
QUALITIES: dict[str, tuple[tuple[int, int, int, int, int, int], bool]] = {
    "Huge": ((2, 4, -2, 0, 0, 0), False),
    "Large": ((1, 2, -1, 0, 0, 0), False),
    "Improved Soak": ((0, 0, 0, 3, 0, 0), True),
    "Improved Initiative": ((0, 0, 0, 0, 3, 0), True),
    "Improved Attack": ((0, 0, 0, 0, 0, 2), True),
}
INFERIORITIES = ("Deaf", "Monstrous Appearance", "Bloodlust", "Reduced Defense")
REDUCED_DEFENSE = -3
LUAN_BONUS = 3


def resist_ease(angry: int, rounds: int = 0) -> int:
    """The Ease Factor to hold off the Ríastradh: 6 + the Angry trait, 1
    more for each round the cause has lasted (p. 120)."""
    return RESIST_EASE + angry + max(0, rounds)


def selections(inferiorities: int) -> int:
    """The Qualities the fomóir form may have (p. 120)."""
    return FREE_QUALITIES + max(0, min(inferiorities, len(INFERIORITIES)))


def form_totals(chosen: list[str]) -> dict[str, int]:
    """What the chosen Qualities and Inferiorities change, summed."""
    keys: tuple[str, ...] = (
        "size",
        "strength",
        "quickness",
        "soak",
        "initiative",
        "attack",
    )
    totals: dict[str, int] = dict.fromkeys(keys, 0)
    for name in chosen:
        if name in QUALITIES:
            for key, amount in zip(keys, QUALITIES[name][0], strict=True):
                totals[key] += amount
    totals["defense"] = REDUCED_DEFENSE if "Reduced Defense" in chosen else 0
    return totals


RIASTRADH_TEXT = (
    "Riled, resist on Sta + Concentration against 6 + his Angry trait, 1 "
    "more each round; the form has 3 Qualities (Huge, Large, Improved Soak, "
    "Initiative or Attack) and one more for each Inferiority (Deaf, "
    "Monstrous Appearance, Bloodlust, Reduced Defense). A change of Size "
    "sheds armor; no Fatigue penalties until Unconscious, when it ends. "
    "Needs Fury or Wrathful (Major) (The Contested Isle pp. 120-121)."
)
LUAN_TEXT = (
    f"Fighting on his own, allied groups +{LUAN_BONUS} to Brave and Morale "
    f"checks, enemy groups -{LUAN_BONUS} (The Contested Isle p. 121)."
)
