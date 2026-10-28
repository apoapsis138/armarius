"""Holy influence, tempers and schism (Realms of Power: The Divine, Holy
Influence, Tempers and Schism, pp. 38-41; Ceremony p. 36), and invoking
God's aid (p. 41).

- Holy influence (p. 38): a holy character inspires a Personality Trait
  in those he has spiritual authority over (a bishop's see, a parent's
  child, a host's guests), who must be willing. Personal influence is a
  season in their company, its trait lasting up to a year; ceremonial
  influence a short ceremony spending a Faith or Confidence Point (which
  adds nothing to the roll), its trait rarely lasting a week. Temporal
  Influence lets a character influence those under his temporal
  authority personally; Inspirational, anyone willing, ceremonially. A
  simple die + Presence + Leadership: 9 gives +1, 15 +2, 24 +3, the most.
  A ceremony may add a group's Ceremony (p. 36).
- A Personality Flaw counts as a +3 trait (Minor) or +6 (Major); a trait
  influenced against one never becomes permanent (p. 38).
- Tempering a Divine aura (p. 38): the same two ways, but on a stress die
  (a botch: Warping, Fatigue or a bad name). The temper is added to every
  roll in the aura that suits it and taken from every roll against it,
  and falls by 1 each day (ceremonial) or each season (personal). A holy
  character holds one temper at a time; a new one replaces his last.
- The seven tempers (pp. 39-40) each oppose a sin: Loyal and Proud, Calm
  and Wrathful, Kind and Envious, Brave and Slothful, Wise and Lustful,
  Strong and Greedy, Just and Avaricious; a trait may name its temper in
  brackets ("Dedicated +3 (Loyal)"), an opposing one counting as minus
  (Cruel +3 (Envious) is Kind -3). The Strong row's traits differ from
  RoP: The Infernal p. 21's (Selfless, Indulgent and Selfish here, Steady,
  Needy and Self-Indulgent there); both are read.
- Schism (p. 41): two leaders' tempers in one aura, so that an action may
  take a bonus and a penalty at once, cancelling out.
- Invoking God's aid (p. 41): a Confidence Point (a Faith Point with True
  Faith; no grog, nor one with Low Self-Esteem), a stress die +
  Communication + Dominion Lore: 9 gives +1, 15 +2, 24 +3, to rolls for
  that aim until one fails or the scene ends; a 0 rolls at least three
  botch dice.

Pattern: plain functions over the character and his traits, the mirror
of rules.sin's Infernal influence and tarnish; the tempers are rows of
data.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..models import Character, ScoredTrait
from . import sin
from .scores import ability_level

SOURCE = (
    "Realms of Power: The Divine, Holy Influence, Tempers and Schism, pp. "
    "38-41; Ceremony p. 36"
)

DIVINE = "Divine"
SEASON, CEREMONY = sin.SEASON, sin.CEREMONY
#: Holy influence's (and God's aid's) Ease Factors and what each gives.
INFLUENCE_TABLE: tuple[tuple[int, int], ...] = ((9, 1), (15, 2), (24, 3))
#: The least botch dice a 0 rolls when invoking God's aid (p. 41).
AID_BOTCH_DICE = 3
INSPIRATIONAL = sin.INSPIRATIONAL
TEMPORAL_INFLUENCE = "vf_temporal_influence"
LOW_SELF_ESTEEM = "vf_low_self_esteem"
TRUE_FAITH = "vf_true_faith"
#: Who the character's authority over the target is: spiritual, temporal
#: (Temporal Influence), or none.
SPIRITUAL, TEMPORAL, NONE = "spiritual", "temporal", "none"


@dataclass(frozen=True)
class Temper:
    """One of the seven holy tempers: the sin it opposes and the traits
    that lean toward it and away (p. 40)."""

    name: str
    sin: str
    positive: tuple[str, ...]
    negative: tuple[str, ...]


TEMPERS: tuple[Temper, ...] = (
    Temper(
        "Loyal",
        "Proud",
        ("Dedicated", "Faithful", "Humble", "Reliable", "Trusting"),
        ("Arrogant", "Haughty", "Rebellious", "Suspicious", "Vain"),
    ),
    Temper(
        "Calm",
        "Wrathful",
        ("Cheerful", "Hopeful", "Optimistic", "Patient", "Peaceful"),
        ("Angry", "Desperate", "Spiteful", "Vengeful", "Violent"),
    ),
    Temper(
        "Kind",
        "Envious",
        ("Charitable", "Compassionate", "Forgiving", "Generous", "Merciful"),
        ("Cruel", "Gossipy", "Gruff", "Jealous", "Meddlesome"),
    ),
    Temper(
        "Brave",
        "Slothful",
        ("Bold", "Courageous", "Determined", "Ready", "Zealous"),
        ("Cowardly", "Cynical", "Indecisive", "Lazy", "Shy"),
    ),
    Temper(
        "Wise",
        "Lustful",
        ("Careful", "Cautious", "Chaste", "Practical", "Prudent"),
        ("Fanatical", "Lecherous", "Naive", "Overconfident", "Reckless"),
    ),
    Temper(
        "Strong",
        "Greedy",
        ("Healthy", "Pious", "Selfless", "Temperate", "Vigilant"),
        ("Gluttonous", "Indulgent", "Selfish", "Sickly", "Weak"),
    ),
    Temper(
        "Just",
        "Avaricious",
        ("Even-handed", "Fair", "Honest", "Honorable", "Straightforward"),
        ("Ambitious", "Corrupt", "Cunning", "Devious", "Manipulative"),
    ),
)
TEMPER_NAMES = tuple(t.name for t in TEMPERS)


def _key(word: str) -> str:
    return word.strip().lower().replace(" ", "-")


def _lookup() -> dict[str, tuple[Temper, int]]:
    found: dict[str, tuple[Temper, int]] = {}
    for temper in TEMPERS:
        found[_key(temper.name)] = (temper, 1)
        found[_key(temper.sin)] = (temper, -1)
        for word in temper.positive:
            found[_key(word)] = (temper, 1)
        for word in temper.negative:
            found[_key(word)] = (temper, -1)
    return found


_WORDS = _lookup()


def temper_named(name: str) -> Temper | None:
    return next((t for t in TEMPERS if _key(t.name) == _key(name)), None)


def lean(name: str) -> tuple[Temper, int] | None:
    """The temper a trait leans to, and which way (+1 toward it, -1
    toward its sin): a temper or sin in brackets decides it, then the
    trait's first word on p. 40's table, then RoP: The Infernal's."""
    text = name.strip()
    if "(" in text and text.endswith(")"):
        head, _, inner = text[:-1].partition("(")
        named = _WORDS.get(_key(inner))
        if named is not None:
            temper, way = named
            own = _WORDS.get(_key(head))
            return temper, way if own is None or own[0] != temper else own[1]
        text = head
    words = text.split()
    if not words:
        return None
    found = _WORDS.get(_key(words[0])) or _WORDS.get(_key(text))
    if found is not None:
        return found
    other = sin.lean(text)
    if other is None:
        return None
    temper = next(t for t in TEMPERS if t.sin == other[0].name)
    return temper, -other[1]


def temper_scores(character: Character) -> dict[str, int]:
    """Each temper the character's traits and Personality Flaws lean to
    or from, the opposite of rules.sin's scores (Dedicated +3 is Loyal
    +3, Cruel +3 is Kind -3; a Minor Flaw +3, a Major +6, p. 38)."""
    by_sin = {t.sin: t.name for t in TEMPERS}
    return {by_sin[name]: -score for name, score in sin.sin_scores(character).items()}


#: Virtues that give spiritual or temporal authority, or the reach to
#: influence the willing: clergy, monks, True Faith, Temporal Influence
#: and Inspirational (p. 38).
STANDING = frozenset(
    {
        "vf_brother_chaplain",
        "vf_clerk",
        "vf_eastern_priest",
        "vf_mazdean_priest",
        "vf_mendicant_friar",
        "vf_priest",
        "vf_senior_clergy",
        "vf_monastic_vows",
        "vf_monastic_vows_hermetic",
        TRUE_FAITH,
        TEMPORAL_INFLUENCE,
        INSPIRATIONAL,
    }
)


def has_standing(character: Character) -> bool:
    """One who might lead others to virtue: a holy Virtue or office above,
    or Dominion Lore."""
    return ability_level(character, "Dominion Lore") > 0 or any(
        vf.vf_id in STANDING for vf in character.virtues_flaws
    )


def influence_total(character: Character, group: int = 0) -> int:
    """Presence + Leadership, and a ceremony's group modifier, before the
    die (pp. 36, 38)."""
    return sin.influence_total(character) + group


def influence_value(total: int) -> int:
    """The trait or temper a total gives: +1 at 9, +2 at 15, +3 at 24; 0
    below 9 (p. 38)."""
    found = 0
    for ease, value in INFLUENCE_TABLE:
        if total >= ease:
            found = value
    return found


def _has(character: Character, vf_id: str) -> bool:
    return any(vf.vf_id == vf_id for vf in character.virtues_flaws)


def point_to_spend(character: Character) -> str:
    """The point a ceremony (or God's aid) spends: a Faith Point with
    True Faith and one left, else a Confidence Point; "" with neither."""
    if (
        _has(character, TRUE_FAITH)
        and character.background.true_faith_score > 0
        and character.background.faith_points > 0
    ):
        return "Faith"
    if character.background.confidence_points > 0:
        return "Confidence"
    return ""


def may_influence(character: Character, authority: str, method: str) -> str:
    """Why the influence is out of reach, or "" when it isn't (p. 38):
    spiritual authority; temporal authority only personally, with
    Temporal Influence; anyone willing only ceremonially, with
    Inspirational; a ceremony needs a point to spend."""
    if method == CEREMONY and not point_to_spend(character):
        return "A ceremony spends a Faith or Confidence Point, and he has none."
    if authority == SPIRITUAL:
        return ""
    if authority == TEMPORAL:
        if method == SEASON and _has(character, TEMPORAL_INFLUENCE):
            return ""
        return (
            "Temporal authority serves only personal influence, with "
            "Temporal Influence (p. 38)."
        )
    if method == CEREMONY and _has(character, INSPIRATIONAL):
        return ""
    return (
        "Holy influence needs spiritual authority over them; without it only "
        "one with Inspirational, by a ceremony (p. 38)."
    )


def lasts(method: str, *, temper: bool) -> str:
    """How long an influenced trait, or a temper, lasts (p. 38)."""
    if temper:
        return (
            "falls by 1 at the end of each day"
            if method == CEREMONY
            else "falls by 1 at the end of each season"
        )
    return (
        "rarely lasts more than a week" if method == CEREMONY else "lasts up to a year"
    )


def temper_after(value: int, steps: int) -> int:
    """A temper's value after `steps` days (ceremonial) or seasons
    (personal): 1 less each, to 0 (p. 38)."""
    return max(0, value - max(0, steps))


def roll_modifier(
    tempers: Sequence[ScoredTrait], helps: Sequence[str], hinders: Sequence[str] = ()
) -> int:
    """What the aura's tempers do to a roll: each temper the action suits
    adds its value, each it runs against takes it away; two leaders'
    tempers may cancel out, in schism (pp. 38, 41)."""
    total = 0
    for t in tempers:
        if t.name in helps:
            total += t.score
        if t.name in hinders:
            total -= t.score
    return total


def in_schism(tempers: Sequence[ScoredTrait]) -> bool:
    """An aura holding more than one temper, invoked by different
    leaders, is in schism (p. 41)."""
    return len({t.name for t in tempers if t.score}) > 1


def may_invoke_aid(character: Character) -> str:
    """Why God's aid can't be invoked, or "": a grog, or one with Low
    Self-Esteem, can't spend Confidence; True Faith spends Faith
    instead (p. 41)."""
    faithful = _has(character, TRUE_FAITH) and character.background.faith_points > 0
    if faithful:
        return ""
    if character.type == "grog" or _has(character, LOW_SELF_ESTEEM):
        return "Only one who can spend a Confidence Point (or a Faith Point) asks God's aid."
    if character.background.confidence_points < 1:
        return "Asking God's aid spends a Confidence Point, and he has none."
    return ""


def aid_total(character: Character) -> int:
    """Communication + Dominion Lore, before the stress die (p. 41)."""
    return character.characteristics.communication + ability_level(
        character, "Dominion Lore"
    )


def aid_bonus(total: int) -> int:
    """The bonus God's aid gives: +1 at 9, +2 at 15, +3 at 24 (p. 41)."""
    return influence_value(total)
