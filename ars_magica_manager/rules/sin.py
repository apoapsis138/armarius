"""Sin, sinful Personality Traits, redemption, infernal influence,
tarnish and Confidence gained through sin (Realms of Power: The Infernal,
Chapter Two: Sin and Temptation, pp. 20-24), worked out over the
character's own Personality Traits and Personality Flaws: nothing new is
kept on the character.

- Sin (p. 20): helping the Infernal against the Divine, or a selfish
  act that does not serve God. Venial sins are light; mortal sins mark
  the soul (the seven deadly sins, killing, lying, stealing,
  blaspheming). A deed forced by a supernatural power is no sin; using
  an Infernal Power, even unknowingly, always is (pp. 20-22).
- Sinful traits (p. 21): each of the seven deadly sins has an opposing
  virtue and five related traits on either side. A trait may name its
  sin in brackets ("Cruel +3 (Envious)"); an opposing trait counts as
  the sin at minus its score (Dedicated +3 is Proud -3). For these rules
  a Minor Personality Flaw is a +3 trait and a Major one +6 (p. 24). A
  Flaw counts when its name is on the table, or is one of p. 17's
  sinful Flaws: Hatred is Wrathful (Lecherous is on the table), and
  Delusion, Obsessed, Compulsion and Weak-Willed count only when their
  detail names a sin or its trait in brackets ("Obsessed (Greedy)").
  p. 17 names those Flaws without a sin, so the mapping is a judgement
  call.
- Redemption (p. 22): sincere repentance at a holy place removes the
  mark of sin, however deep; Christians confess and do penance, Muslims
  and Jews fast in atonement. Absolution also costs a False Power Flaw
  and the Virtue it changes (p. 89), and the False Gift with every
  Supernatural Ability learned through it, Arts included (p. 124).
- Infernal influence (p. 23): personal (a season in company) or
  ceremonial (a short ceremony, a Confidence Point, Infernal Lore 1+);
  simple die + Presence + Leadership on the table 9/12/15/18/21/24 gives
  a trait of +1 to +6. Only the willing are influenced; strangers only by
  one with Inspirational. Personal traits last up to a year, ceremonial
  ones about a week.
- Tarnish (p. 24): an Infernal aura given a sinful trait, by the same
  two kinds of influence but with a stress die (a botch: Warping Points
  or Fatigue). It adds to similar traits of everyone inside, takes from
  opposing ones, and is gained as a trait by anyone with neither. Only
  the strongest tarnish counts; a ceremonial one fades by 1 each morning,
  a personal one each season's end.
- Confidence through sin (p. 24): with a trait for the sin, a season of
  indulging it at every chance (alongside other work) or a short
  ceremony of a ritualized sin (and an Infernal Warping Point) gives a
  Confidence Point. A trait of +3 or less needs only venial sins; more
  usually needs a mortal sin. Without a Confidence Score the points may
  still be spent (influence, tarnish, or with the storyguide's leave +1
  a point to a fitting roll, no more than the trait's score).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .. import catalog
from ..models import Character, ScoredTrait
from .scores import ability_level

SOURCE = "Realms of Power: The Infernal, Chapter Two: Sin and Temptation, pp. 20-24"
REDEMPTION_SOURCE = (
    "Realms of Power: The Infernal, Redemption, p. 22; False Power, p. 89; "
    "False Magic, p. 124"
)


@dataclass(frozen=True)
class Sin:
    """One deadly sin, the virtue it opposes, and the traits that lean
    each way (RoP: The Infernal p. 21)."""

    name: str
    virtue: str
    sinful: tuple[str, ...]
    virtuous: tuple[str, ...]


SINS: tuple[Sin, ...] = (
    Sin(
        "Proud",
        "Loyal",
        ("Arrogant", "Haughty", "Rebellious", "Suspicious", "Vain"),
        ("Dedicated", "Faithful", "Humble", "Reliable", "Trusting"),
    ),
    Sin(
        "Wrathful",
        "Calm",
        ("Angry", "Desperate", "Spiteful", "Vengeful", "Violent"),
        ("Cheerful", "Hopeful", "Optimistic", "Patient", "Peaceful"),
    ),
    Sin(
        "Envious",
        "Kind",
        ("Cruel", "Gossipy", "Gruff", "Jealous", "Meddlesome"),
        ("Charitable", "Compassionate", "Forgiving", "Generous", "Merciful"),
    ),
    Sin(
        "Slothful",
        "Brave",
        ("Cowardly", "Cynical", "Indecisive", "Lazy", "Shy"),
        ("Bold", "Courageous", "Determined", "Ready", "Zealous"),
    ),
    Sin(
        "Lustful",
        "Wise",
        ("Fanatical", "Lecherous", "Naive", "Overconfident", "Reckless"),
        ("Careful", "Cautious", "Chaste", "Practical", "Prudent"),
    ),
    Sin(
        "Greedy",
        "Strong",
        ("Gluttonous", "Needy", "Self-Indulgent", "Sickly", "Weak"),
        ("Healthy", "Pious", "Steady", "Temperate", "Vigilant"),
    ),
    Sin(
        "Avaricious",
        "Just",
        ("Ambitious", "Corrupt", "Cunning", "Devious", "Manipulative"),
        ("Even-handed", "Fair", "Honest", "Honorable", "Straightforward"),
    ),
)

#: A Personality Flaw as a trait score (p. 24).
MINOR_FLAW_SCORE = 3
MAJOR_FLAW_SCORE = 6
#: The highest trait a venial sin feeds; above it a mortal sin is needed.
VENIAL_UP_TO = 3
VENIAL, MORTAL = "venial", "mortal"
#: The two ways to gain Confidence through sin, and to influence.
SEASON, CEREMONY = "season", "ceremony"
METHODS: dict[str, str] = {
    SEASON: "A season indulging it at every chance",
    CEREMONY: "A short ceremony of a ritualized sin",
}
#: Warping Points a ceremony of a ritualized sin gives (p. 24).
CEREMONY_WARPING = 1
#: Infernal Lore a ceremonial influence needs (p. 23).
CEREMONY_LORE = 1
#: Infernal influence's Ease Factors and the trait each gives (p. 23).
INFLUENCE_TABLE: tuple[tuple[int, int], ...] = (
    (9, 1),
    (12, 2),
    (15, 3),
    (18, 4),
    (21, 5),
    (24, 6),
)
#: p. 17's sinful Flaws that are not on the p. 21 table, by the sin each
#: leans to (a judgement call: p. 17 names them without a sin).
FLAW_SINS: dict[str, str] = {"Hatred": "Wrathful"}
#: p. 17's Flaws that lean to whichever sin their detail names in brackets.
DETAIL_FLAWS = frozenset({"Delusion", "Obsessed", "Compulsion", "Weak-Willed"})
#: The Virtue or Flaw parameter that holds such a Flaw's detail.
DETAIL_PARAM = "detail"
INSPIRATIONAL = "vf_inspirational"
FALSE_GIFT = "vf_the_false_gift"
FALSE_POWER = "vf_false_power"


def _key(word: str) -> str:
    return word.strip().lower().replace("ï", "i").replace(" ", "-")


def _lookup() -> dict[str, tuple[Sin, int]]:
    found: dict[str, tuple[Sin, int]] = {}
    for sin in SINS:
        found[_key(sin.name)] = (sin, 1)
        found[_key(sin.virtue)] = (sin, -1)
        for word in sin.sinful:
            found[_key(word)] = (sin, 1)
        for word in sin.virtuous:
            found[_key(word)] = (sin, -1)
    return found


_WORDS = _lookup()


def sin_named(name: str) -> Sin | None:
    """The sin of that name ("Proud"), or None."""
    return next((s for s in SINS if _key(s.name) == _key(name)), None)


def lean(name: str) -> tuple[Sin, int] | None:
    """The sin a trait's name leans toward, and which way: +1 toward the
    sin, -1 toward its virtue. A sin or virtue in brackets ("Cruel
    (Envious)") decides it; otherwise the trait's first word, matched on
    the table. None for a trait the table doesn't cover ("Likes figs")."""
    text = name.strip()
    if "(" in text and text.endswith(")"):
        head, _, inner = text[:-1].partition("(")
        named = _WORDS.get(_key(inner))
        if named is not None:
            sin, way = named
            own = _WORDS.get(_key(head))
            # "Dedicated (Loyal)": the virtue named; the trait follows it.
            return sin, way if own is None or own[0] != sin else own[1]
        text = head
    words = text.split()
    if not words:
        return None
    return _WORDS.get(_key(words[0])) or _WORDS.get(_key(text))


@dataclass(frozen=True)
class SinfulTrait:
    """A trait or Personality Flaw read as a sin: its label, the sin, and
    its score toward that sin (negative for a virtuous one)."""

    label: str
    sin: str
    score: int
    flaw: bool = False

    @property
    def shown(self) -> str:
        """ "Cruel (Envious) +3", or "Lecherous (Lustful +3)" when the
        label doesn't name its sin."""
        if self.sin.lower() in self.label.lower():
            return f"{self.label} {self.score:+d}"
        return f"{self.label} ({self.sin} {self.score:+d})"


def _bracketed(text: str) -> tuple[Sin, int] | None:
    """The sin or trait named in brackets in `text` ("Gold (Greedy)"), the
    innermost and last first."""
    for inner in reversed(re.findall(r"\(([^()]+)\)", text)):
        named = _WORDS.get(_key(inner))
        if named is not None:
            return named
    return None


def flaw_lean(name: str, detail: str = "") -> tuple[Sin, int] | None:
    """The sin a Personality Flaw leans toward: a Flaw named on the table
    (the whole name, so Weak Personality is not Weak), Hatred as Wrathful,
    or for Delusion, Obsessed, Compulsion and Weak-Willed the sin or trait
    its detail names in brackets."""
    if name in DETAIL_FLAWS:
        return _bracketed(f"({detail})")
    if name in FLAW_SINS:
        found = sin_named(FLAW_SINS[name])
        return None if found is None else (found, 1)
    return _WORDS.get(_key(name))


def _flaw_traits(character: Character) -> list[SinfulTrait]:
    defs = catalog.load_virtue_flaw_catalog_by_id()
    found: list[SinfulTrait] = []
    for vf in character.virtues_flaws:
        definition = defs.get(vf.vf_id)
        if definition is None or definition.category != "Personality":
            continue
        leaning = flaw_lean(definition.name, vf.params.get(DETAIL_PARAM, ""))
        if leaning is None:
            continue
        sin, way = leaning
        size = MAJOR_FLAW_SCORE if definition.tier == "Major" else MINOR_FLAW_SCORE
        detail = vf.params.get(DETAIL_PARAM, "").strip()
        named = f"{definition.name} ({detail.title()})" if detail else definition.name
        found.append(
            SinfulTrait(
                f"{named} ({definition.tier} Flaw)",
                sin.name,
                way * size,
                True,
            )
        )
    return found


def leanings(character: Character) -> list[SinfulTrait]:
    """Every Personality Trait and Personality Flaw the table reads as a
    sin or its virtue."""
    found: list[SinfulTrait] = []
    for trait in character.personality_traits:
        leaning = lean(trait.name)
        if leaning is not None:
            sin, way = leaning
            found.append(SinfulTrait(trait.name, sin.name, way * trait.score))
    return found + _flaw_traits(character)


def sinful_traits(character: Character) -> list[SinfulTrait]:
    """The traits and Flaws that give a penchant for a sin (a positive
    score toward it), strongest first."""
    return sorted(
        (t for t in leanings(character) if t.score > 0),
        key=lambda t: (-t.score, t.label),
    )


def sin_scores(character: Character) -> dict[str, int]:
    """Each sin the character leans to or from: the strongest pull toward
    it, or the strongest pull away when nothing pulls toward it."""
    toward: dict[str, int] = {}
    away: dict[str, int] = {}
    for trait in leanings(character):
        if trait.score > 0:
            toward[trait.sin] = max(toward.get(trait.sin, 0), trait.score)
        elif trait.score < 0:
            away[trait.sin] = min(away.get(trait.sin, 0), trait.score)
    return {
        sin.name: toward.get(sin.name) or away[sin.name]
        for sin in SINS
        if sin.name in toward or sin.name in away
    }


def sin_needed(score: int) -> str:
    """The grade of sin that feeds a trait of `score` (p. 24): venial for
    +3 or less, mortal above that."""
    return VENIAL if score <= VENIAL_UP_TO else MORTAL


def has_confidence_score(character: Character) -> bool:
    return character.background.confidence_score > 0


def spend_cap(trait_score: int) -> int:
    """The most Confidence Points one without a Confidence Score may
    spend on one roll tied to a trait: its score (p. 24)."""
    return max(0, trait_score)


def confidence_through_sin(method: str) -> tuple[int, int]:
    """(Confidence Points, Warping Points) a season's indulgence or a
    ceremony of ritualized sin gives (p. 24)."""
    if method not in METHODS:
        raise ValueError(f"Unknown way to sin: {method!r}")
    return 1, CEREMONY_WARPING if method == CEREMONY else 0


def gain_text(trait: SinfulTrait, method: str) -> list[str]:
    """What gaining Confidence through the trait's sin asks and gives."""
    points, warping = confidence_through_sin(method)
    grade = sin_needed(trait.score)
    lines = [
        f"{trait.shown} is fed by a {grade} sin"
        + (
            " (above +3 the act must be more depraved)."
            if grade == MORTAL
            else " (+3 or less)."
        )
    ]
    if method == SEASON:
        lines.append(
            "Indulging it at every chance this season, alongside other work: "
            f"+{points} Confidence Point at the season's end."
        )
    else:
        lines.append(
            f"A short ceremony of a ritualized sin: +{points} Confidence Point and "
            f"+{warping} Infernal Warping Point."
        )
    return lines


# ---------------------------------------------------------------------------
# Infernal influence and tarnish


def influence_total(character: Character) -> int:
    """Presence + Leadership, before the die (p. 23)."""
    return character.characteristics.presence + ability_level(character, "Leadership")


def influence_trait(total: int) -> int:
    """The trait an influence (or tarnish) total gives: +1 at 9 up to +6
    at 24; 0 below 9 (p. 23)."""
    found = 0
    for ease, value in INFLUENCE_TABLE:
        if total >= ease:
            found = value
    return found


def may_influence_ceremonially(character: Character) -> str:
    """Why a ceremonial influence is out of reach, or "" when it isn't:
    Infernal Lore 1 and a Confidence Point to spend (p. 23)."""
    if ability_level(character, "Infernal Lore") < CEREMONY_LORE:
        return "A ceremony needs Infernal Lore 1."
    if character.background.confidence_points < 1:
        return "A ceremony costs a Confidence Point, and he has none."
    return ""


def may_influence_strangers(character: Character) -> bool:
    """Only one with Inspirational influences strangers (p. 23)."""
    return any(vf.vf_id == INSPIRATIONAL for vf in character.virtues_flaws)


def lasts(method: str, *, tarnish: bool) -> str:
    """How long an influence's trait, or a tarnish, lasts (pp. 23-24)."""
    if tarnish:
        return (
            "falls by 1 each morning"
            if method == CEREMONY
            else "falls by 1 at the end of each season"
        )
    return "fades within about a week" if method == CEREMONY else "lingers up to a year"


def tarnish_after(value: int, steps: int) -> int:
    """A tarnish's value after `steps` mornings (ceremonial) or seasons
    (personal): one less each (p. 24)."""
    if value >= 0:
        return max(0, value - max(0, steps))
    return min(0, value + max(0, steps))


def strongest_tarnish(tarnishes: list[ScoredTrait]) -> ScoredTrait | None:
    """An aura holds one tarnish: the strongest (p. 24)."""
    return max(tarnishes, key=lambda t: abs(t.score), default=None)


def under_tarnish(traits: list[ScoredTrait], tarnish: ScoredTrait) -> list[ScoredTrait]:
    """A character's traits while inside an aura with `tarnish` (p. 24):
    it is added to similar traits and taken from opposing ones; with
    neither, it is gained as a trait. The character's own list is left
    alone."""
    leaning = lean(tarnish.name)
    shown: list[ScoredTrait] = []
    touched = False
    for trait in traits:
        own = lean(trait.name)
        if leaning is not None and own is not None and own[0] == leaning[0]:
            same = own[1] == leaning[1]
            shown.append(
                ScoredTrait(
                    trait.name,
                    trait.score + (tarnish.score if same else -tarnish.score),
                )
            )
            touched = True
        elif _key(trait.name) == _key(tarnish.name):
            shown.append(ScoredTrait(trait.name, trait.score + tarnish.score))
            touched = True
        else:
            shown.append(ScoredTrait(trait.name, trait.score))
    if not touched:
        shown.append(ScoredTrait(tarnish.name, tarnish.score))
    return shown


# ---------------------------------------------------------------------------
# Redemption


def absolution_costs(character: Character) -> list[str]:
    """What sincere repentance and absolution would take from the
    character, besides the mark of sin (pp. 22, 89, 124)."""
    costs: list[str] = []
    if any(vf.vf_id == FALSE_GIFT for vf in character.virtues_flaws):
        costs.append(
            "The False Gift: he loses The Gift and every Supernatural Ability "
            "learned with it, the Hermetic Arts included (p. 124)."
        )
    for vf in character.virtues_flaws:
        if vf.vf_id == FALSE_POWER:
            named = str(vf.params.get("virtue") or "") or "the Virtue it changes"
            costs.append(f"False Power: the Flaw goes, and {named} with it (p. 89).")
    return costs


def redemption_lines(character: Character) -> list[str]:
    """Redemption, worked out for the character (p. 22)."""
    lines = [
        "Repentance removes the mark of sin at any time, however deep: "
        "confession and penance for a Christian, a fast of atonement for a "
        "Muslim or Jew (p. 22)."
    ]
    lines += absolution_costs(character)
    return lines
