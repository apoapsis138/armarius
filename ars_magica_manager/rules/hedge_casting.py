"""Casting totals, Penetration and Magical Defenses for the non-Hermetic
traditions.

A tradition's ways of casting are data on its catalog record
(TraditionDef.casting, each a CastingRule), so one set of functions
works every tradition out:

    Casting Score = the scores the kind uses + Characteristic
                    + any added Abilities + the aura's modifier
                    + vis (per pawn)
    Casting Total = (Casting Score + die) / divisor, rounded down

- Kinds (KINDS, a Strategy registry): an art_pair adds a Technique and
  a Form, an ability kind one Ability, a rune kind the lowest rune the
  script uses.
- The total is rolled against the effect's level or Ease Factor; up to
  `failure_margin` short it still works, for a Fatigue level, and further
  short it fails (with the Fatigue still spent when there is a margin).
- An Ability whose magnitude is its score casts as a spell of 5 x score.
- Penetration Total = Casting Total + Penetration bonus - level, as for
  Hermetic magic.
- The aura's modifier is the realm table's for the tradition's realm.
- A magus may use Rego for a Goetic Art and Vim for the Realm Lore in a
  Goetic Art's total, when they are better (rules.hybrid_magic).

Magical Defenses: each of the tradition's Arts or Abilities may give one,
against its specialty. The bonus is a hedge Art's score / 5 (round up)
or a Supernatural Ability's score; Greater Magical Defenses doubles it,
No Magical Defenses takes them all. They never add up: only the best one
against an effect applies.

Rules: reference/rules-engine-reference.md §18 (Generic Supernatural
Ability casting, Limits of Magic and Magical Defenses, each tradition's
Casting), §3 (Ceremony).

No screen uses best_defense(), ability_effect_level(), group_bonus(),
leaderless_modifier() yet: they are the rules for screens still to come, and
only the tests call them.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from ..models import CastingRule, Character, DispelRule, GroupCasting, TraditionDef
from . import hybrid_magic as hybrid
from . import penetration, realms
from .breakdown import Breakdown, Line
from .creation_access import ability_def
from .lab import ability_score
from .rounding import round_down, round_up

SOURCE = (
    "Hedge Magic, Revised Edition, Chapter One: Introduction "
    "(https://www.redcap.org/page/Hedge_Magic_Revised_Edition_Open_Content"
    "#Magic_Defenses)"
)
CEREMONY_SOURCE = (
    "Realms of Power: The Divine, Ceremony "
    "(https://www.redcap.org/page/Realms_of_Power:_The_Divine_Open_Content"
    "#CEREMONY*)"
)

GREATER_DEFENSES = "vf_greater_magical_defenses"
NO_DEFENSES = "vf_no_magical_defenses"
THE_GIFT = "vf_the_gift"

#: What each Magical Defense does, B being the bonus.
DEFENSE_EFFECTS: dict[str, str] = {
    "Accelerated Expiry": (
        "spells on them end early, Diameter by B rounds, Sun by B hours, "
        "Moon by B days, Year by B weeks (never below the next shorter "
        "duration)"
    ),
    "Alacritous Fortune": "+B to Defense against aimed spells",
    "Confounding Magics": "+B to the caster's Concentration Ease Factor",
    "Immovable Object": (
        "each round, Strength + B - the effect's magnitude + a simple die "
        "against 9 resists control"
    ),
    "Magical Fortitude": "+B to Soak against damaging effects",
    "Strength of Form": (
        "Stamina + B + a simple die against 9 returns them to their own form"
    ),
}


def score(character: Character, name: str) -> int:
    """An Art's or Ability's score with its fixed bonus (Puissant)."""
    base, bonus = ability_score(character, name)
    return base + bonus


def holds(character: Character, name: str) -> bool:
    """Whether the character has the Art or Ability (a score of 0 counts)."""
    return any(a.name == name for a in character.abilities)


def gifted(character: Character) -> bool:
    return any(vf.vf_id == THE_GIFT for vf in character.virtues_flaws)


def _role(tradition: TraditionDef, role: str) -> list[str]:
    found = []
    for name in tradition.abilities:
        entry = ability_def(name)
        if entry is not None and entry.role == role:
            found.append(name)
    return found


def techniques(tradition: TraditionDef, rule: CastingRule) -> list[str]:
    return rule.techniques or _role(tradition, "Technique")


def forms(tradition: TraditionDef, rule: CastingRule) -> list[str]:
    return rule.forms or _role(tradition, "Form")


def rule_scores(tradition: TraditionDef, rule: CastingRule) -> list[str]:
    """The Abilities an ability kind casts with, or the runes."""
    if rule.scores:
        return list(rule.scores)
    if rule.kind == "rune":
        return _role(tradition, "Rune")
    return list(tradition.favored)


# ---------------------------------------------------------------------------
# What the character can cast: one Strategy per kind


@dataclass(frozen=True)
class Casting:
    """One thing the character can cast with a rule: its label ("Give
    Curse", "Healing", "Fehu") and the Arts or Abilities it adds."""

    label: str
    uses: tuple[str, ...]


def _art_pairs(
    character: Character, tradition: TraditionDef, rule: CastingRule
) -> list[Casting]:
    """Every Technique + Form pair whose two Arts the character has."""
    return [
        Casting(f"{short_name(t)} {short_name(f)}", (t, f))
        for t in techniques(tradition, rule)
        if holds(character, t)
        for f in forms(tradition, rule)
        if holds(character, f)
    ]


def _abilities(
    character: Character, tradition: TraditionDef, rule: CastingRule
) -> list[Casting]:
    return [
        Casting(name, (name,))
        for name in rule_scores(tradition, rule)
        if holds(character, name)
    ]


#: Strategy registry: kind -> what the character can cast with it.
KINDS: dict[str, Callable[[Character, TraditionDef, CastingRule], list[Casting]]] = {
    "art_pair": _art_pairs,
    "ability": _abilities,
    # A rune script uses the lowest of its runes; each held rune is the
    # most a script of it alone can use.
    "rune": _abilities,
}


def castings(
    character: Character, tradition: TraditionDef, rule: CastingRule
) -> list[Casting]:
    return KINDS[rule.kind](character, tradition, rule)


def short_name(name: str) -> str:
    """An Art's name without its tradition's prefix ("Gruagach Give" ->
    "Give", "Elementalist Air" -> "Air")."""
    for prefix in ("Gruagach ", "Elementalist "):
        if name.startswith(prefix):
            return name.removeprefix(prefix)
    return name


# ---------------------------------------------------------------------------
# Scores and totals


def characteristic_for(rule: CastingRule, uses: Sequence[str]) -> str:
    """The Characteristic a casting adds: the rule's, or the one named for
    the first Art or Ability it uses."""
    for name in uses:
        if name in rule.characteristics:
            return rule.characteristics[name]
    return rule.characteristic


def aura_modifier(tradition: TraditionDef, aura: int, aura_realm: str) -> int:
    return realms.aura_modifier(tradition.realm, aura_realm, aura)


def casting_score(
    character: Character,
    tradition: TraditionDef,
    rule: CastingRule,
    uses: Sequence[str],
    *,
    aura: int = 0,
    aura_realm: str = realms.HERMETIC,
    vis_pawns: int = 0,
) -> Breakdown:
    """The Casting Score (or a lab rule's Lab Total), with its terms. A
    rune script counts only the lowest of its runes; a bound being adds
    its bond's bonus to the totals it applies to."""
    lines: list[Line] = []
    if rule.kind == "rune":
        low = min(uses, key=lambda name: score(character, name))
        label = low if len(uses) == 1 else f"{low} (lowest rune)"
        lines.append(Line(label, amount=score(character, low), source=SOURCE))
    else:
        for name in uses:
            lines.append(_used(character, name))
    characteristic = characteristic_for(rule, uses)
    if characteristic:
        value = getattr(character.characteristics, characteristic.lower(), 0)
        lines.append(Line(characteristic, amount=value, source=SOURCE))
    for name in rule.adds:
        lines.append(Line(name, amount=score(character, name), source=SOURCE))
    if rule.best_of:
        found = [_used(character, name) for name in rule.best_of]
        lines.append(max(found, key=lambda line: line.amount or 0))
    lines.append(
        Line(
            f"Aura ({aura_realm} {aura})",
            amount=aura_modifier(tradition, aura, aura_realm),
            source=realms.SOURCE,
        )
    )
    applies = "lab" if rule.lab else "casting"
    for being in character.bound_beings:
        if being.tradition == tradition.id and being.applies_to == applies:
            lines.append(
                Line(f"{being.name} (bound)", amount=being.bonus, source=SOURCE)
            )
    if vis_pawns:
        lines.append(
            Line(
                f"{vis_pawns} pawns of vis",
                amount=rule.vis_per_pawn * vis_pawns,
                source=SOURCE,
            )
        )
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def _used(character: Character, name: str) -> Line:
    """An Art or Ability a casting adds, or the Hermetic Art a magus may
    use in its place (Rego for a Goetic Art, Vim for a Realm Lore)."""
    own = Line(name, amount=score(character, name), source=SOURCE)
    instead = hybrid.goetic_substitute(character, name)
    if instead is None:
        return own
    label, amount = instead
    return Line(label, amount=amount, source=hybrid.GOETIC_SOURCE)


def casting_total(rule: CastingRule, casting_score: int, die: int = 0) -> int:
    """(Casting Score + die) / divisor, rounded down; a lab rule adds no
    die."""
    if rule.lab or rule.die == "none":
        die = 0
    return round_down((casting_score + die) / rule.divisor)


@dataclass(frozen=True)
class Outcome:
    works: bool
    #: Whether it costs a Fatigue level (its own cost aside).
    fatigue: bool


def outcome(rule: CastingRule, total: int, level: int) -> Outcome:
    """Whether a total casts an effect of `level` (or Ease Factor)."""
    short = level - total
    if short <= 0:
        return Outcome(True, False)
    if rule.failure_margin:
        return Outcome(short <= rule.failure_margin, True)
    return Outcome(False, False)


def equivalent_level(rule: CastingRule, uses_score: int) -> int | None:
    """The level a Supernatural Ability's effect counts as (5 x score),
    or None when the effect has its own level."""
    return 5 * uses_score if rule.magnitude_is_score else None


def vis_cap(
    character: Character,
    tradition: TraditionDef,
    rule: CastingRule,
    uses: Sequence[str],
) -> int:
    """The most pawns of vis one casting may use: each Art's score added
    up (the Hermetic rule), the score used, or the sum of the tradition's
    Forms. 0 when it can't use vis (an unGifted member, where the rule
    says so)."""
    if rule.vis_cap == "none" or (not rule.ungifted_vis and not gifted(character)):
        return 0
    if rule.vis_cap == "forms":
        return sum(score(character, f) for f in forms(tradition, rule))
    values = [score(character, name) for name in uses]
    if rule.vis_cap == "score":
        return min(values) if rule.kind == "rune" else max(values)
    return sum(values)


def penetration_bonus(character: Character) -> int:
    """The Penetration bonus with no Arcane Connection."""
    return int(penetration.penetration_bonus(character).total)


def penetration_total(
    character: Character, casting_total: int, level: int, bonus: int
) -> int:
    return penetration.penetration_total(
        casting_total, bonus, level, character.virtues_flaws
    )


# ---------------------------------------------------------------------------
# Magical Defenses


@dataclass(frozen=True)
class DefenseRow:
    """A Magical Defense the character has: the Art or Ability giving it,
    the kind, what it works against, and its bonus."""

    source: str
    kind: str
    against: str
    bonus: int

    @property
    def effect(self) -> str:
        return DEFENSE_EFFECTS[self.kind].replace("B", str(self.bonus))


def defense_bonus(character: Character, name: str) -> int:
    """A hedge Art's score / 5 (round up), or a Supernatural Ability's
    score."""
    value = score(character, name)
    entry = ability_def(name)
    if entry is not None and entry.category == "Hedge Art":
        return round_up(value / 5)
    return value


def magical_defenses(character: Character, tradition: TraditionDef) -> list[DefenseRow]:
    """The tradition's Magical Defenses the character has: one per Art or
    Ability they hold, doubled by Greater Magical Defenses, none with No
    Magical Defenses."""
    held = {vf.vf_id for vf in character.virtues_flaws}
    if NO_DEFENSES in held:
        return []
    factor = 2 if GREATER_DEFENSES in held else 1
    return [
        DefenseRow(name, d.kind, d.against, factor * defense_bonus(character, name))
        for name, d in tradition.defenses.items()
        if holds(character, name)
    ]


def best_defense(rows: Sequence[DefenseRow], kind: str) -> DefenseRow | None:
    """The best of one kind (defenses never add up)."""
    found = [r for r in rows if r.kind == kind]
    return max(found, key=lambda r: r.bonus) if found else None


# ---------------------------------------------------------------------------
# Active dispelling and group casting


def dispel_needs(rule: DispelRule, effect_level: int) -> int:
    """What the dispelling must reach to end an effect of `effect_level`."""
    return rule.multiple * effect_level


def dispels(rule: DispelRule, total: int, effect_level: int) -> bool:
    return total >= dispel_needs(rule, effect_level)


def ability_effect_level(ability_score: int) -> int:
    """A Supernatural Ability's effect counts as a spell of 5 x its score
    when something dispels it."""
    return 5 * ability_score


def most_helpers(
    group: GroupCasting, *, aura: int = 0, leader_ceremony: int = 0
) -> int:
    """How many helpers count: the aura's strength, the leader's Ceremony,
    or a fixed number."""
    if group.most == "aura":
        return max(aura, 0)
    if group.most == "Ceremony":
        return max(leader_ceremony, 0)
    return int(group.most)


def group_bonus(
    group: GroupCasting,
    helpers: Sequence[int],
    *,
    aura: int = 0,
    leader_ceremony: int = 0,
) -> int:
    """What the helpers add to the focus's total. With Ceremony each
    counted helper adds their own Characteristic + score (`helpers`, best
    first); with a number, each adds that number."""
    counted = sorted(helpers, reverse=True)[
        : most_helpers(group, aura=aura, leader_ceremony=leader_ceremony)
    ]
    if group.helper == "Ceremony":
        return sum(counted)
    return int(group.helper) * len(counted)


def leaderless_modifier(ceremony_scores: Sequence[int]) -> int:
    """Ceremony without a leader: the sum of everyone's Ceremony less the
    number taking part (it may be negative)."""
    return sum(ceremony_scores) - len(ceremony_scores)
