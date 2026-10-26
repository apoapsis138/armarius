"""The Goetic Arts' own totals and what they do (Realms of Power: The
Infernal, Chapter Eleven: Ars Goetia, pp. 114-119; Goetic Magic and
Goetic Mastery, p. 124). The Arts are Supernatural Powers opened at 0 and
advanced as Arts; each total uses Penetration x its multiplier, so it is
already its own Penetration.

- Summoning: stress die + Presence + Summoning + (Realm) Lore + aura +
  Penetration x multiplier (an Arcane Connection, for a demon its True
  Name). Scouring (calling whatever answers): (Area) Lore instead, and
  Penetration unmultiplied; it draws a spirit of about half the total's
  Might. Against the spirit's Might x 2 the spirit is held in the circle;
  reaching only its Might, it stays only while he concentrates. Summoning
  always costs a Fatigue level (pp. 114-115).
- Ablating: stress die + Stamina + Ablating + (Realm) Lore + aura +
  Penetration x multiplier; it must exceed the spirit's Might (twice its
  Might outside a circle). The margin comes off the spirit's Might (no
  more than its Might) and a fifth of it, rounded down, are Ablation
  Points to spend; he also gains as much Infernal Reputation experience
  and a Warping Point (pp. 115-117).
- Binding: stress die + Intelligence + Binding + ... must exceed the
  spirit's Might in a circle (twice outside one; a spirit that allows it
  needs only no botch, or outside a circle only its Might exceeded). A
  bound spirit lends its Might as Magic Resistance, holds Might x 5 spell
  levels (Might pawns of Vim vis to a Hermetic enchanter), stops its
  bearer's Aging rolls for a Warping Point a year (p. 117).
- Commanding: stress die + Communication + Commanding + ... with
  Binding's targets; a command holds until midday or midnight (pp.
  117-118).
- Against a demon, the sorcerer adds his own Hierarchy x 5 (his highest
  Infernal Reputation, p. 95) to his total, and the target level adds
  the demon's Hierarchy x 5 (p. 114); for Summoning that is twice the
  Might plus the demon's (p. 115), and the lower, concentrating
  threshold of its Might plus the demon's follows Ablation's wording
  (p. 116), the builder's reading of p. 115.
- A magus who holds a Goetic Art may use Rego for it and Vim for the
  Realm Lore (p. 124; rules.hybrid_magic.goetic_substitute). Goetic
  Mastery adds the fitting Goetic Art to the spell's Casting Total, and
  his Hierarchy x 5 to its Penetration against a demon, less the
  demon's Hierarchy x 5 (p. 124).

The spirit's Might is never known to the sheet: the form takes it.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Character
from . import hybrid_magic as hybrid
from . import penetration, realms
from .breakdown import Breakdown, Line
from .infernalists import hierarchy
from .rounding import round_down

SOURCE = "Realms of Power: The Infernal, Chapter Eleven: Ars Goetia, pp. 114-119"
MASTERY_SOURCE = "Realms of Power: The Infernal, Goetic Mastery, p. 124"

SUMMONING, ABLATING, BINDING, COMMANDING = hybrid.GOETIC_ARTS
#: Summoning a spirit at large, not a named one.
SCOURING = "Scouring"
#: What each Art adds, and what the Realm Lore stands for.
CHARACTERISTICS: dict[str, str] = {
    SUMMONING: "Presence",
    SCOURING: "Presence",
    ABLATING: "Stamina",
    BINDING: "Intelligence",
    COMMANDING: "Communication",
}
#: Summoning is a Magic or Faerie Power as well as an Infernal one; the
#: other three are always Infernal (p. 115).
SUMMONING_REALMS = (realms.HERMETIC, "Faerie", "Infernal")
HIERARCHY_STEP = 5
ABLATION_DIVISOR = 5
#: Spell levels a bound spirit holds, a point of its Might (p. 117).
LEVELS_PER_MIGHT = 5
#: The Goetic Mastery ability's name on a mastered spell (lower case).
GOETIC_MASTERY = "goetic mastery"

#: What Ablation Points may buy (pp. 116-117).
ABLATION_USES: dict[str, str] = {
    "Confidence": "as many Confidence Points (no more than Confidence Score x "
    "5), or experience in the Confidence Score",
    "Capability": "points on Characteristics, as at creation, no higher than "
    "the spirit's",
    "Health": "5 heals a Heavy Wound, 3 a Medium, 1 a Light or a long-term "
    "Fatigue level",
    "Immortality": "a Longevity bonus to Aging rolls until his next crisis",
    "Insight": "the spirit's thoughts and memories",
    "Knowledge": "5 xp a point in a fitting Art or Ability, to the spirit's "
    "score; it takes the season's study",
    "Might": "Infernal Might, no more than the spirit's old Might or "
    "Confidence Score x 5",
    "Power": "one of the spirit's Powers (a Virtue or Flaw without Might)",
    "Vis": "a pawn of Infernal vis a point (vis sordida or prava)",
}

#: The common commands (p. 118).
COMMANDS: dict[str, str] = {
    "Follow me": "travels behind him until discharged; no renewing",
    "Advise me": "answers truly, though it may mislead; then released",
    "Aid me": "raises one Characteristic, Ability or Art to its score",
    "Begone": "returns, and cannot take a physical form meanwhile",
    "Commune with me": "shares its memories and imagined futures",
    "Glorify me": "an Infernal Reputation of its Hierarchy for the command",
    "Heal me": "patches one wound until the command ends",
    "Journey": "travels where he names, if it can",
    "Perform for me": "uses its Powers or Abilities as directed",
    "Protect me": "its Might as his Magic Resistance, renewed twice a day",
    "Return peacefully": "returns, and cannot harm him unless summoned again",
    "Teach me": "teaches an Ability (a season of renewals: Teaching)",
}


def _score(character: Character, name: str) -> Line:
    """A Goetic Art or Realm Lore, or the Hermetic Art a magus may use."""
    instead = hybrid.goetic_substitute(character, name)
    if instead is not None:
        label, amount = instead
        return Line(label, amount=amount, source=hybrid.GOETIC_SOURCE)
    return Line(name, amount=hybrid.ability(character, name), source=SOURCE)


def holds_goetic_art(character: Character) -> bool:
    return any(a.name in hybrid.GOETIC_ARTS for a in character.abilities)


def goetic_arts(character: Character) -> list[str]:
    """The Goetic Arts the character holds (a score of 0 counts)."""
    return [
        g for g in hybrid.GOETIC_ARTS if any(a.name == g for a in character.abilities)
    ]


def power_realm(art: str, summoning_realm: str = "Infernal") -> str:
    """The realm the Art works as, for the aura."""
    return summoning_realm if art in (SUMMONING, SCOURING) else "Infernal"


def total(
    character: Character,
    art: str,
    *,
    lore: str = "Infernal Lore",
    aura: int = 0,
    aura_realm: str = realms.HERMETIC,
    arcane_connection: str | None = None,
    demon: bool = False,
    sacrifice: int = 0,
    summoning_realm: str = "Infernal",
) -> Breakdown:
    """The Art's total before the stress die, with its terms. Scouring
    uses Summoning with an Area Lore and Penetration unmultiplied."""
    if art not in CHARACTERISTICS:
        raise ValueError(f"Unknown Goetic Art {art!r}")
    characteristic = CHARACTERISTICS[art]
    lines = [
        Line(
            characteristic,
            amount=getattr(character.characteristics, characteristic.lower()),
            source=SOURCE,
        ),
        _score(character, SUMMONING if art == SCOURING else art),
        _score(character, lore),
        Line(
            f"Aura ({aura_realm} {aura})",
            amount=realms.aura_modifier(
                power_realm(art, summoning_realm), aura_realm, aura
            ),
            source=realms.SOURCE,
        ),
    ]
    connection = None if art == SCOURING else arcane_connection
    pen = penetration.penetration_bonus(character, arcane_connection=connection)
    lines.append(Line("Penetration x multiplier", amount=pen.total, source=SOURCE))
    if demon:
        lines.append(
            Line(
                "Hierarchy x 5 (against a demon)",
                amount=HIERARCHY_STEP * hierarchy(character),
                source=SOURCE,
            )
        )
    if sacrifice:
        lines.append(Line("Sacrifice", amount=sacrifice, source=SOURCE))
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def target_level(
    art: str,
    might: int,
    *,
    in_circle: bool = True,
    resists: bool = True,
    demon_hierarchy: int = 0,
) -> int:
    """What the total is measured against (pp. 115-118): for Summoning,
    twice the Might (holding the spirit in the circle); for the others the
    Might in a circle, twice it outside, or (Binding, Commanding) the Might
    outside a circle for a spirit that allows it; plus the demon's
    Hierarchy x 5."""
    if art in (SUMMONING, SCOURING):
        base = 2 * might
    elif in_circle or (art != ABLATING and not resists):
        base = might
    else:
        base = 2 * might
    return base + HIERARCHY_STEP * demon_hierarchy


@dataclass(frozen=True)
class Result:
    """What a Goetic total did: whether it worked, what it says, and for
    Ablating the Might taken and the Ablation Points."""

    worked: bool
    text: str
    might_taken: int = 0
    ablation_points: int = 0


def ablation(total_value: int, target: int, might: int) -> tuple[int, int]:
    """(Might taken from the spirit, Ablation Points): the margin over
    the target, no more than the Might, and a fifth of it, rounded down
    (p. 116)."""
    taken = max(0, min(total_value - target, might))
    return taken, round_down(taken / ABLATION_DIVISOR)


def outcome(
    art: str,
    total_value: int,
    might: int,
    *,
    in_circle: bool = True,
    resists: bool = True,
    demon_hierarchy: int = 0,
    botched: bool = False,
) -> Result:
    """What the total against the spirit does."""
    if botched:
        return Result(False, botch_text(art))
    level = target_level(
        art,
        might,
        in_circle=in_circle,
        resists=resists,
        demon_hierarchy=demon_hierarchy,
    )
    extra = HIERARCHY_STEP * demon_hierarchy
    if art in (SUMMONING, SCOURING):
        if total_value >= level:
            return Result(
                True,
                "Summoned and held in the circle until he dismisses it, or the "
                "next midday or midnight.",
            )
        if total_value >= might + extra:
            return Result(
                True,
                "Summoned, but it stays only while he concentrates; talking "
                "with it asks Stamina + Concentration rolls to keep the circle.",
            )
        return Result(False, "No spirit answers.")
    if art in (BINDING, COMMANDING) and not resists and in_circle:
        return Result(True, "It allows the effect: only a botch fails.")
    if total_value <= level:
        return Result(False, f"Short: the total must exceed {level}.")
    if art == ABLATING:
        taken, points = ablation(total_value, level, might)
        return Result(
            True,
            f"Its Might falls by {taken}; {points} Ablation Point(s), "
            f"{points} xp in an Infernal Reputation and a Warping Point.",
            taken,
            points,
        )
    if art == BINDING:
        return Result(
            True,
            f"Bound: its Might ({might}) as Magic Resistance to the bearer; an "
            f"object holds {LEVELS_PER_MIGHT * might} spell levels; no Aging "
            "rolls for the bearer, but a Warping Point a year.",
        )
    return Result(True, "It must obey one command, until midday or midnight.")


def botch_text(art: str) -> str:
    """What a botch may do (pp. 115-117)."""
    return {
        SUMMONING: "Botched: the wrong spirit, a demon in disguise, a flawed "
        "circle, or Warping Points and a Vituperation check.",
        SCOURING: "Botched: the wrong spirit, a demon in disguise, a flawed "
        "circle, or Warping Points and a Vituperation check.",
        ABLATING: "Botched: almost certainly Vituperation.",
        BINDING: "Botched: the spirit or the target harmed, or the spirit "
        "joined to something else.",
        COMMANDING: "Botched: the spirit freed, angered, or the sorcerer weakened.",
    }[art]


def scouring_might(total_value: int) -> int:
    """About the Might of the spirit a scouring draws: half the total."""
    return round_down(max(0, total_value) / 2)


# ---------------------------------------------------------------------------
# Goetic Mastery


def mastery_notes(
    character: Character, abilities: dict[str, int], score: int
) -> list[str]:
    """Goetic Mastery on a mastered spell that targets spirits (p. 124):
    the best Goetic Art to the Casting Total, and Hierarchy x 5 to its
    Penetration against a demon."""
    if not score or not abilities.get(GOETIC_MASTERY):
        return []
    held = [(hybrid.ability(character, g), g) for g in goetic_arts(character)]
    if not held:
        return ["Goetic Mastery needs a Goetic Art"]
    best, name = max(held)
    rank = hierarchy(character)
    return [
        f"Goetic Mastery: + the fitting Goetic Art (best {name} {best}) to "
        f"its Casting Total; against a demon +{HIERARCHY_STEP * rank} "
        "Penetration less the demon's Hierarchy x 5; it seems unholy"
    ]
