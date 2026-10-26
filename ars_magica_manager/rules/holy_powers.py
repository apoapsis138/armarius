"""Holy Methods and Powers (Realms of Power: The Divine, Miraculous
Effects, pp. 46-56; Errata pp. 48-49).

- A holy effect pairs a Method with a Power: a simple die + the Method's
  Characteristic + Method + Power + the aura against the effect's level
  (p. 46). Invocation (Communication) costs a Confidence Point; Meditation
  (Intelligence) is an absorbing, calming activity; Purity (Stamina) a
  fast or vigil, usually long-term Fatigue (pp. 46-47). Holy Music
  (Presence) is a kind of Meditation (p. 49).
- Each Power works only with some Methods (p. 48): Adjuration and Cursing
  with Invocation or Purity, Blessing with Invocation or Meditation,
  Intervention and Transcendence with Meditation or Purity, Understanding
  with Meditation alone, Wonders with Invocation alone.
- Levels (p. 48): the Powers' guidelines (catalog data, data/power_
  guidelines.json, each labelled with the Method it is for; the Errata
  turns every "(level - X)" into "(level + X)" but Blessing's capped
  bonuses) and the Hermetic Ranges, Durations and Targets; what a
  Hermetic ritual would need, a Boundary, a Year or permanence, adds 4
  magnitudes more, which the shared parameters build into Year and
  Boundary (rules.hedge_effects works the level out). A holy connection
  stands in for an Arcane Connection.
- A shortfall is a tragedy of hubris (p. 46): Minor 1-10 short, Major
  11-20, Ultimate 21 or more; True Faith x 10 may stand in for the total
  when judging it. A Blessing that lasts gives a Warping Point a year
  (p. 49).

Pattern: plain functions over a tradition's effect, beside rules.
faerie_rites; the data is the catalog's.
"""

from __future__ import annotations

import re

from ..models import Character, TraditionDef, TraditionEffect

SOURCE = "Realms of Power: The Divine, Miraculous Effects, pp. 46-56; Errata pp. 48-49"

DIVINE = "Divine"
INVOCATION, MEDITATION, PURITY = "Invocation", "Meditation", "Purity"
#: Each Method and the Characteristic it adds (pp. 46-47).
METHODS: dict[str, str] = {
    INVOCATION: "Communication",
    MEDITATION: "Intelligence",
    PURITY: "Stamina",
}
#: Traditions' own Methods and the Method each is a kind of (Holy Music,
#: p. 49; Dream Interpretation, a form of Meditation, Errata p. 49).
VARIANTS: dict[str, str] = {
    "Holy Music": MEDITATION,
    "Dream Interpretation": MEDITATION,
}
#: The Methods each Power works with (p. 48).
COMBINATIONS: dict[str, tuple[str, ...]] = {
    "Adjuration": (INVOCATION, PURITY),
    "Blessing": (INVOCATION, MEDITATION),
    "Cursing": (INVOCATION, PURITY),
    "Intervention": (MEDITATION, PURITY),
    "Transcendence": (MEDITATION, PURITY),
    "Understanding": (MEDITATION,),
    "Wonders": (INVOCATION,),
}
#: How short of the level each tragedy of hubris begins (p. 46).
TRAGEDIES: tuple[tuple[int, str], ...] = (
    (21, "an Ultimate tragedy"),
    (11, "a Major tragedy"),
    (1, "a Minor tragedy"),
)
FAITH_STANDS_IN = 10
#: A ritual's surcharge for a holy effect, in magnitudes (p. 48).
RITUAL_MAGNITUDES = 4


def method_of(name: str) -> str:
    """The Method a Method Ability is (Holy Music is Meditation), or ""."""
    if name in METHODS:
        return name
    return VARIANTS.get(name, "")


def works_with(power: str, method: str) -> bool:
    """Whether the Method can call the Power (p. 48)."""
    return method_of(method) in COMBINATIONS.get(power, ())


def tragedy(total: int, level: int, faith: int = 0) -> str:
    """The tragedy of hubris a total short of the level brings, True
    Faith x 10 standing in when higher ("" when none; p. 46). A total of
    15 against level 30 is a Major tragedy; with Faith 2 a Minor one, with
    Faith 3 none."""
    short = level - max(total, FAITH_STANDS_IN * max(0, faith))
    return next((name for least, name in TRAGEDIES if short >= least), "")


_LABELLED = re.compile(r"\((Invocation|Meditation|Purity)\)\s*$")


def guideline_method(effect_guideline: str) -> str:
    """The Method a guideline's label names ("(Purity)"), or ""."""
    found = _LABELLED.search(effect_guideline)
    return found.group(1) if found else ""


def is_holy_effect(tradition: TraditionDef, effect: TraditionEffect) -> bool:
    return tradition.realm == DIVINE and any(u in COMBINATIONS for u in effect.uses)


def effect_notes(
    character: Character, tradition: TraditionDef, effect: TraditionEffect
) -> list[str]:
    """What a holy effect's Method and Power ask beyond its level: whether
    they combine, the guideline's own Method, the tragedy its shortfall
    risks and what True Faith spares (advice)."""
    if not is_holy_effect(tradition, effect):
        return []
    power = next(u for u in effect.uses if u in COMBINATIONS)
    method = next((u for u in effect.uses if method_of(u)), "")
    found: list[str] = []
    if method and not works_with(power, method):
        allowed = " or ".join(COMBINATIONS[power])
        found.append(f"{power} works with {allowed}, not {method} (RoP: Divine p. 48)")
    wanted = guideline_method(effect.guideline)
    if method and wanted and method_of(method) != wanted:
        found.append(f"its guideline is for {wanted} (p. 48)")
    faith = character.background.true_faith_score
    line = (
        "short of its level, a tragedy of hubris: Minor 1-10, Major 11-20, Ultimate 21+"
    )
    if faith > 0:
        line += f"; his True Faith stands in as {FAITH_STANDS_IN * faith}"
    found.append(line + " (p. 46)")
    if power == "Blessing" and effect.duration == "Year":
        found.append("one always under a Blessing gains a Warping Point a year (p. 49)")
    return found
