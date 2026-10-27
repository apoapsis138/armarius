"""House-specific magic from Houses of Hermes beyond the Mastery
abilities (rules.house_mastery has those): House Mercere's Mutantum magic,
its Portals and the Cult of Heroes' rituals (True Lineages pp. 100-103,
the Virtues pp. 105-107), and House Tytalus's disguises and personae
(Societates pp. 87-90).

- **Mutantum spells** (True Lineages p. 101; Errata p. 46). A spell may be
  Boosted, Harnessed or Tethered, named after the semicolon of its level
  working ("Base 30, +1 Touch, +1 Diam; Tethered") or in a "Requires ...
  Magic or Mutantum Magic" line. Each quality needs its own Virtue
  (Boosted, Harnessed or Tethered Magic) or Mutantum Magic to learn or
  cast; Tamed Magic counts as Harnessed and Tethered Magic (p. 107).
  Inventing such a spell, or investing such an item effect, needs
  Mutantum Magic itself (pp. 101, 107).
- **Boosting** (p. 101, as the Errata replaces it; the Definitive
  Edition's Boosted Magic, pp. 72-73, says the same of any Formulaic
  spell): a pawn of vis a magnitude raises Range, Duration, Target or
  size, never lowers one, and goes past Formulaic limits (Year, Boundary)
  only for a Ritual; success, Fatigue and Penetration are reckoned at the
  spell's own level, with a botch die more a pawn.
- **Mercere's Portals** (pp. 100-101): a season's study of a Portal or
  its Lab Texts teaches the method; then two invested devices each instil
  Rego Terram 65 (Base 35, +4 Arcane Connection, +10 unlimited uses),
  each holding an Arcane Connection to the other, and a connecting
  ceremony with no roll joins them; once joined they can't be moved.
- **The Cult of Heroes' rituals** (p. 103): (Characteristic) of the
  Followers raises a Characteristic by one to no more than 0, of the
  Heroes by one to no more than +5. Mercury's Blessing is a Mercurian
  Ritual of Year Duration.
- **Disguises** (Societates p. 87): Intelligence + Guile + stress die
  against 9 + the Disguise Roll Modifiers, rolled by the storyguide;
  talking with someone is then Presence + Guile against his Intelligence
  + Folk Ken. Short-term disguises ignore The Gift; social rolls in one
  don't.
- **Deep cover** (pp. 87-90): a noteworthy act gives a Reputation of 1
  as the identity; it takes the Disguise roll's place and comes off its
  Ease Factor when the cover is questioned. A season living there earns 2
  xp in it, regular visits 1, a brief visit each season 2 a year, and
  each staged event or tie to the community 1; more than 2 a season
  arouses suspicion. A role needing a Minor Social Status Virtue brings a
  Minor Story Flaw's burden, a Major one a Major Story Flaw's and can't
  last; one needing other Virtues (Wealthy, Temporal Influence) can't be
  built. Among those he sees regularly the Reputation comes off The
  Gift's penalty. Unused for years equal to its score, it loses a point
  a year, and The Gift's penalty returns in full.
- **Persona** (Definitive Edition p. 169, the Ability; Societates pp.
  89-90): Stamina + Persona against 9, a round's concentration, to take
  an identity or return; an identity for each point; each persona starts
  with a Reputation of 1 and gains the xp put into Persona. The change
  shows as a Muto Corpus effect of level 10 (magnitude 2), a magnitude
  less for each sunrise or sunset since; for other purposes its level is
  5 x Persona.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field, replace

from ..models import COVER, PERSONA_KIND, Character, DeepCover, InstilledEffect, Spell
from . import house_discoveries, house_mastery, lab_virtues, spell_levels
from .breakdown import Breakdown, Line
from .lab import LabTotal
from .scores import ability_level
from .study import gift_social_penalty
from .xp import ABILITY_FACTOR, score_from_xp

TL = "Houses of Hermes: True Lineages"
SOC = "Houses of Hermes: Societates"
MUTANTUM_SOURCE = f"{TL}, Mutantum Magic and Mutantum Spells, p. 101; Errata p. 46"
PORTAL_SOURCE = f"{TL}, Mercere's Portals, pp. 100-101"
HEROES_SOURCE = f"{TL}, Other Spells, p. 103"
DISGUISE_SOURCE = f"{SOC}, Disguises and Personae, pp. 87-90"
PERSONA_SOURCE = (
    f"Ars Magica Definitive Edition, Persona, p. 169; {SOC}, Personae, pp. 89-90"
)
SOURCE = f"{MUTANTUM_SOURCE}; {PORTAL_SOURCE}; {HEROES_SOURCE}; {DISGUISE_SOURCE}"

# -- Mutantum magic --------------------------------------------------------

BOOSTED = "Boosted"
HARNESSED = "Harnessed"
TETHERED = "Tethered"
QUALITIES = (BOOSTED, HARNESSED, TETHERED)

BOOSTED_MAGIC = "vf_boosted_magic"
HARNESSED_MAGIC = "vf_harnessed_magic"
TETHERED_MAGIC = "vf_tethered_magic"
MUTANTUM_MAGIC = "vf_mutantum_magic"
TAMED_MAGIC = "vf_tamed_magic"

#: The Virtues that let a magus learn and cast a spell of each quality
#: (p. 101); Tamed Magic is Harnessed and Tethered Magic both (p. 107).
QUALITY_VIRTUES: dict[str, tuple[str, ...]] = {
    BOOSTED: (BOOSTED_MAGIC, MUTANTUM_MAGIC),
    HARNESSED: (HARNESSED_MAGIC, MUTANTUM_MAGIC, TAMED_MAGIC),
    TETHERED: (TETHERED_MAGIC, MUTANTUM_MAGIC, TAMED_MAGIC),
}
VIRTUE_NAMES: dict[str, str] = {
    BOOSTED: "Boosted Magic",
    HARNESSED: "Harnessed Magic",
    TETHERED: "Tethered Magic",
}

_WORKING = re.compile(r"\(([^()]*);\s*([A-Za-z ,]+)\)")
_REQUIRES = re.compile(r"Requires ([A-Za-z ,]+?) Magic or Mutantum Magic")


def qualities(description: str) -> tuple[str, ...]:
    """The Mutantum qualities a spell or effect's text names, in book
    order: those after the semicolon of its level working, and those its
    "Requires ... Magic or Mutantum Magic" line names."""
    words: set[str] = set()
    for match in _WORKING.finditer(description):
        words |= {w.strip().title() for w in match.group(2).split(",")}
    for match in _REQUIRES.finditer(description):
        words |= {w.title() for w in re.findall(r"[A-Za-z]+", match.group(1))}
    return tuple(q for q in QUALITIES if q in words)


def spell_qualities(spell: Spell) -> tuple[str, ...]:
    return qualities(spell.description)


def _ids(magus: Character) -> set[str]:
    return {vf.vf_id for vf in magus.virtues_flaws}


def missing_qualities(vf_ids: set[str], found: Iterable[str]) -> list[str]:
    """The qualities a magus with these Virtues can't manage."""
    return [q for q in found if not any(v in vf_ids for v in QUALITY_VIRTUES[q])]


def learn_problem(magus: Character, spell: Spell, *, inventing: bool = False) -> str:
    """Why the magus can't learn (or, `inventing`, invent) a Mutantum
    spell; "" when he can. A magus who can't manage one of its qualities
    can't learn it (p. 101); only Mutantum Magic invents them (p. 107)."""
    found = spell_qualities(spell)
    if not found:
        return ""
    ids = _ids(magus)
    if inventing and MUTANTUM_MAGIC not in ids:
        return (
            f"{magus.name} can't invent {spell.name}: a {', '.join(found)} "
            f"spell is invented only with Mutantum Magic ({TL} pp. 101, 107)."
        )
    missing = missing_qualities(ids, found)
    if not missing:
        return ""
    needs = " and ".join(VIRTUE_NAMES[q] for q in missing)
    return (
        f"{magus.name} can't learn {spell.name}: it is "
        f"{', '.join(missing)}, which needs {needs} or Mutantum Magic "
        f"({MUTANTUM_SOURCE})."
    )


def effect_problems(
    magus: Character, effect: InstilledEffect | None, *, invested: bool = True
) -> list[str]:
    """Why the magus can't instil an effect: a Boosted, Harnessed or
    Tethered effect needs Mutantum Magic (p. 101), and a Mercere's Portal
    needs its method and its own shape (pp. 100-101)."""
    if effect is None:
        return []
    found: list[str] = []
    named = qualities(effect.description)
    if named and not lab_virtues.has(magus, MUTANTUM_MAGIC):
        found.append(
            f"{effect.name or 'This effect'} is {', '.join(named)}: only a "
            f"magus with Mutantum Magic invests such effects ({MUTANTUM_SOURCE})."
        )
    if is_portal(effect):
        found += portal_problems(magus, effect, invested=invested)
    return found


@dataclass
class Boost:
    """Boosting a spell: the pawns it takes, the botch dice it adds, and
    what stops it."""

    pawns: int = 0
    botch_dice: int = 0
    problems: list[str] = field(default_factory=list)


def boost(
    spell: Spell,
    *,
    range_: str | None = None,
    duration: str | None = None,
    target: str | None = None,
    size: int = 0,
) -> Boost:
    """Boosting `spell` to the given Range, Duration and Target (None keeps
    one) and `size` steps larger: a pawn a magnitude, a botch die a pawn;
    no parameter lowered, and Year or Boundary (or any parameter that
    makes a Ritual) only for a Ritual (p. 101; Errata pp. 45-46; DE pp.
    72-73)."""
    result = Boost()
    if size < 0:
        result.problems.append("Boosting never makes a spell smaller.")
    pawns = max(0, size)
    for kind, now, wanted in (
        ("range", spell.range, range_),
        ("duration", spell.duration, duration),
        ("target", spell.target, target),
    ):
        if wanted is None or wanted == now:
            continue
        before = spell_levels.steps_of(kind, now)
        after = spell_levels.steps_of(kind, wanted)
        if before is None or after is None:
            result.problems.append(f"The app doesn't know {kind} {now} or {wanted}.")
            continue
        if after < before:
            result.problems.append(f"Boosting never lowers its {kind.title()}.")
            continue
        if spell_levels.needs_ritual(kind, wanted) and not spell.ritual:
            result.problems.append(
                f"{wanted} {kind.title()} is past Formulaic magic: only a "
                "Ritual is boosted to it."
            )
            continue
        pawns += after - before
    result.pawns = pawns
    result.botch_dice = pawns
    return result


def can_boost(
    magus: Character, spell: Spell, mastery_abilities: Mapping[str, int] | None = None
) -> bool:
    """Whether the magus may boost the spell: a Boosted spell with Boosted
    or Mutantum Magic, any Formulaic spell with Boosted Magic (DE p. 72),
    or one mastered with Boosted Casting (p. 99)."""
    ids = _ids(magus)
    if (mastery_abilities or {}).get(house_mastery.BOOSTED):
        return True
    if BOOSTED in spell_qualities(spell):
        return bool(ids & {BOOSTED_MAGIC, MUTANTUM_MAGIC})
    return BOOSTED_MAGIC in ids and not spell.ritual and spell.level is not None


_QUALITY_TEXT = {
    BOOSTED: (
        "Boosted: a pawn of vis a magnitude raises its Range, Duration, "
        "Target or size, a botch die more each; it is cast, tires and "
        "penetrates at its own level, and reaches Year or Boundary only as "
        "a Ritual"
    ),
    HARNESSED: (
        "Harnessed: the caster ends it at will by concentrating, as long as "
        "casting it, at any distance"
    ),
    TETHERED: (
        "Tethered: its control may pass to another within range, who is "
        "then its caster, or to an object that casts it on a fit target in "
        "range, for its duration"
    ),
}


def cast_problem(magus: Character, spell: Spell) -> str:
    """Why the magus can't cast a Mutantum spell he knows ("" when he
    can): only one with the Virtue for each quality casts it (p. 101)."""
    missing = missing_qualities(_ids(magus), spell_qualities(spell))
    if not missing:
        return ""
    return (
        f"{magus.name} can't cast it: {', '.join(missing)} needs "
        + " or ".join(VIRTUE_NAMES[q] for q in missing)
        + f" or Mutantum Magic ({TL} p. 101)."
    )


def spell_lines(spell: Spell) -> list[str]:
    """Plain-text lines for a known spell's casting details: what its
    Mutantum qualities do, and what a Cult of Heroes ritual does."""
    found: list[str] = []
    named = spell_qualities(spell)
    if named:
        found.append(
            "Mutantum spell: "
            + "; ".join(_QUALITY_TEXT[q] for q in named)
            + f" ({TL} p. 101)."
        )
    ritual = HEROES_RITUALS.get(spell.id)
    if ritual is not None:
        found.append(
            f"Raises one {ritual.kind} Characteristic by 1, to no more than "
            f"{ritual.cap:+d} ({TL} p. 103)."
        )
    if spell.id == MERCURYS_BLESSING:
        found.append(
            "A Mercurian Ritual: for a year, children conceived and born to "
            f"the subject are likelier to have The Gift or heroic gifts ({TL} "
            "p. 103)."
        )
    return found


def reminders(magus: Character) -> list[str]:
    """Mutantum and Tamed Magic's casting reminders (plain text)."""
    found: list[str] = []
    if lab_virtues.has(magus, MUTANTUM_MAGIC):
        found.append(
            "Mutantum Magic: he invents Formulaic spells and invested items "
            "that are Boosted, Harnessed or Tethered, and learns and casts "
            f"them all ({TL} pp. 101, 107)."
        )
    if lab_virtues.has(magus, TAMED_MAGIC):
        found.append(
            "Tamed Magic: any of his Spontaneous or Formulaic spells, or item "
            "effects he activates, may be harnessed or tethered; they aren't "
            f"Arcane Connections to him and don't end when he dies ({TL} p. 107)."
        )
    return found


# -- Mercere's Portals -----------------------------------------------------

PORTAL = "Mercere's Portal"
PORTAL_TECHNIQUE = "Rego"
PORTAL_FORM = "Terram"
PORTAL_BASE = 35
PORTAL_RANGE_MAGNITUDES = 4
PORTAL_UNLIMITED_USES = 10
PORTAL_LEVEL = PORTAL_BASE + 5 * PORTAL_RANGE_MAGNITUDES + PORTAL_UNLIMITED_USES


def portal_level() -> Breakdown:
    """The effect each of a Portal's archways instils (p. 100)."""
    lines = [
        Line("Base", amount=PORTAL_BASE, source=PORTAL_SOURCE),
        Line(
            "Arcane Connection Range (+4 magnitudes)",
            amount=5 * PORTAL_RANGE_MAGNITUDES,
            source=PORTAL_SOURCE,
        ),
        Line("Unlimited uses", amount=PORTAL_UNLIMITED_USES, source=PORTAL_SOURCE),
    ]
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def is_portal(effect: InstilledEffect) -> bool:
    return PORTAL.casefold() in effect.name.casefold().replace("’", "'")


def knows_portals(magus: Character) -> bool:
    """Whether the magus has learned the method: recorded, like a House's
    discoveries, as a reached research goal named for it."""
    return house_discoveries.knows(magus, PORTAL)


def portal_problems(
    magus: Character, effect: InstilledEffect, *, invested: bool = True
) -> list[str]:
    """What stops a magus instilling a Mercere's Portal archway."""
    found: list[str] = []
    if not invested:
        found.append(f"A {PORTAL}'s archways are invested devices ({PORTAL_SOURCE}).")
    if not knows_portals(magus):
        found.append(
            f"{magus.name} hasn't learned the method of {PORTAL}s: a season "
            "studying a Portal or its Lab Texts teaches it (record it as a "
            f"reached research goal named {PORTAL}) ({PORTAL_SOURCE})."
        )
    if (effect.technique, effect.form) != (PORTAL_TECHNIQUE, PORTAL_FORM):
        found.append(f"A {PORTAL}'s archway instils a Rego Terram effect.")
    if effect.level and effect.level != PORTAL_LEVEL:
        found.append(
            f"A {PORTAL}'s archway instils level {PORTAL_LEVEL} (Base 35, +4 "
            "Arcane Connection, +10 unlimited uses)."
        )
    return found


PORTAL_NOTE = (
    f"{PORTAL}: two invested archways, each holding an Arcane Connection to "
    "the other, joined by a connecting ceremony (like Hermes' Portal, no "
    "roll) performed at both at once; they work only once joined, and "
    f"moving one then destroys it ({PORTAL_SOURCE})."
)


def with_portal_note(effect: InstilledEffect, total: LabTotal) -> LabTotal:
    """A Lab Total instilling a Portal, with what the archways need."""
    if not is_portal(effect):
        return total
    return replace(total, notes=[*(total.notes or []), PORTAL_NOTE])


# -- the Cult of Heroes' rituals -------------------------------------------


@dataclass(frozen=True)
class HeroesRitual:
    kind: str  # "physical" or "mental"
    cap: int


PHYSICAL = ("strength", "stamina", "dexterity", "quickness")
MENTAL = ("intelligence", "perception", "presence", "communication")
FOLLOWERS_CAP = 0
HEROES_CAP = 5
HEROES_RITUALS: dict[str, HeroesRitual] = {
    "spell_physical_characteristic_of_the_followers": HeroesRitual(
        "physical", FOLLOWERS_CAP
    ),
    "spell_physical_characteristic_of_the_heroes": HeroesRitual("physical", HEROES_CAP),
    "spell_mental_characteristic_of_the_followers": HeroesRitual(
        "mental", FOLLOWERS_CAP
    ),
    "spell_mental_characteristic_of_the_heroes": HeroesRitual("mental", HEROES_CAP),
}
MERCURYS_BLESSING = "spell_mercury_s_blessing"


def heroes_ritual(spell_id: str, characteristic: str, score: int) -> tuple[int, str]:
    """The Characteristic's new score after the ritual, and why it can't
    be raised ("" when it is)."""
    ritual = HEROES_RITUALS.get(spell_id)
    if ritual is None:
        raise ValueError(f"{spell_id!r} isn't one of the Cult of Heroes' rituals.")
    allowed = PHYSICAL if ritual.kind == "physical" else MENTAL
    if characteristic.lower() not in allowed:
        return score, f"It raises a {ritual.kind} Characteristic, not {characteristic}."
    if score >= ritual.cap:
        return score, (
            f"It raises a Characteristic to no more than {ritual.cap:+d} "
            f"({HEROES_SOURCE})."
        )
    return score + 1, ""


# -- disguises and deep cover (Societates pp. 87-90) -----------------------

DISGUISE_EASE = 9
#: The Disguise Roll Modifiers (p. 87): use all that apply.
DISGUISE_MODIFIERS: dict[str, int] = {
    "Change social status": 3,
    "Minor alteration in physical appearance": 1,
    "Major alteration in physical appearance": 3,
    "Change sex": 6,
    "Minimal preparation": 3,
    "No preparation": 6,
}


def disguise_total(character: Character) -> Breakdown:
    """Intelligence + Guile, before the stress die (p. 87)."""
    lines = [
        Line(
            "Intelligence",
            amount=character.characteristics.intelligence,
            source=DISGUISE_SOURCE,
        ),
        Line("Guile", amount=ability_level(character, "Guile"), source=DISGUISE_SOURCE),
    ]
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def disguise_ease(modifiers: Iterable[str], cover_reputation: int = 0) -> Breakdown:
    """The Disguise roll's Ease Factor: 9 + each modifier that applies,
    less a deep cover's Reputation when the cover is questioned (pp.
    87-88). ValueError for a modifier not on the table."""
    lines = [Line("Disguise", amount=DISGUISE_EASE, source=DISGUISE_SOURCE)]
    for name in modifiers:
        if name not in DISGUISE_MODIFIERS:
            raise ValueError(f"{name!r} isn't a Disguise Roll Modifier.")
        lines.append(
            Line(name, amount=DISGUISE_MODIFIERS[name], source=DISGUISE_SOURCE)
        )
    if cover_reputation > 0:
        lines.append(
            Line(
                "Deep cover Reputation",
                amount=-cover_reputation,
                source=DISGUISE_SOURCE,
            )
        )
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def deceive_total(character: Character) -> Breakdown:
    """Presence + Guile to fool someone talked with in disguise, against
    his Intelligence + Folk Ken (p. 87). It is a social roll, so The
    Gift's penalty counts."""
    lines = [
        Line(
            "Presence",
            amount=character.characteristics.presence,
            source=DISGUISE_SOURCE,
        ),
        Line("Guile", amount=ability_level(character, "Guile"), source=DISGUISE_SOURCE),
    ]
    gift = gift_social_penalty(character)
    if gift:
        lines.append(Line("The Gift", amount=-gift, source=DISGUISE_SOURCE))
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def see_through_total(character: Character) -> Breakdown:
    """Intelligence + Folk Ken, against a disguised talker (p. 87)."""
    lines = [
        Line(
            "Intelligence",
            amount=character.characteristics.intelligence,
            source=DISGUISE_SOURCE,
        ),
        Line(
            "Folk Ken",
            amount=ability_level(character, "Folk Ken"),
            source=DISGUISE_SOURCE,
        ),
    ]
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


COVER_START = 1
#: Reputation xp a season in the cover's community (pp. 88-89).
COVER_XP: dict[str, int] = {"lives there": 2, "visits regularly": 1, "away": 0}
#: A brief visit every season earns 2 xp a year.
BRIEF_VISITS_XP_A_YEAR = 2
#: More than this a season arouses suspicion.
COVER_SUSPICION = 2


def cover_xp(contact: str, events: int = 0) -> tuple[int, bool]:
    """A season's Reputation xp for a deep cover, and whether it arouses
    suspicion (more than 2 a season): `contact` from COVER_XP, plus 1 for
    each staged event or tie to the community (marriage, children, an
    office). ValueError for another contact."""
    if contact not in COVER_XP:
        raise ValueError(f"{contact!r} isn't a way of keeping a cover.")
    xp = COVER_XP[contact] + max(0, events)
    return xp, xp > COVER_SUSPICION


#: A persona's Reputation xp when it is made: a score of 1 (p. 90).
PERSONA_START_XP = 5


def persona_xp(character: Character) -> int:
    """The xp in the character's Persona Ability."""
    return next((a.xp for a in character.abilities if a.name == PERSONA), 0)


def cover_reputation_xp(cover: DeepCover, character: Character | None = None) -> int:
    """A cover's Reputation xp; a persona's also has every xp put into the
    Persona Ability since it was made (p. 90)."""
    if cover.kind != PERSONA_KIND or character is None:
        return cover.reputation_xp
    return cover.reputation_xp + max(0, persona_xp(character) - cover.persona_from_xp)


def cover_reputation(cover: DeepCover, character: Character | None = None) -> int:
    """A cover's or persona's Reputation score, from its xp (it rises as an
    Ability does, pp. 88, 90)."""
    return score_from_xp(cover_reputation_xp(cover, character), ABILITY_FACTOR)


def keep_covers(character: Character) -> list[str]:
    """A season's Reputation xp for each deep cover kept up (at Advance),
    and a note when one rises suspiciously fast (p. 89)."""
    told: list[str] = []
    for cover in character.covers:
        if cover.kind != COVER or cover.last_used is not None:
            continue
        xp, suspicious = cover_xp(cover.contact)
        if not xp:
            continue
        cover.reputation_xp += xp
        told.append(
            f"Cover {cover.name}: +{xp} Reputation xp ({cover_reputation(cover)})"
            + (", suspiciously fast" if suspicious else "")
            + "."
        )
    return told


def cover_burden(status_tier: str | None, other_virtues: bool = False) -> str:
    """What keeping a cover role costs (p. 88): `status_tier` is the tier
    of the Social Status Virtue the role would need ("Minor", "Major" or
    None); `other_virtues` that it needs others (Wealthy, Temporal
    Influence)."""
    if other_virtues:
        return "impossible: a role needing Virtues beyond Social Status can't be built"
    if status_tier == "Major":
        return "a Major Story Flaw's attention, and not tenable for long"
    if status_tier == "Minor":
        return "a Minor Story Flaw's obligations, with minor benefits"
    return "nothing beyond keeping it up"


def cover_gift_penalty(gift_penalty: int, cover_reputation: int) -> int:
    """The Gift's social penalty with those the cover sees regularly: less
    its Reputation, never below 0 (p. 89). Strangers take the full one."""
    return max(0, gift_penalty - max(0, cover_reputation))


def dormant_reputation(score: int, years_unused: int) -> int:
    """A cover's Reputation after years without use: it keeps its score
    for as many years as the score, then loses a point a year (p. 90)."""
    return max(0, score - max(0, years_unused - score))


def gift_returns(score: int, years_unused: int) -> bool:
    """Whether The Gift's penalty is back in full when the cover is used
    again (after its dormancy period, p. 90)."""
    return years_unused >= score


# -- Persona ----------------------------------------------------------------

PERSONA = "Persona"
PERSONA_EASE = 9
PERSONA_TRACE_LEVEL = 10
PERSONA_REPUTATION = 1


def persona_total(character: Character) -> Breakdown:
    """Stamina + Persona, against 9 to take an identity or return (DE p.
    169)."""
    lines = [
        Line(
            "Stamina", amount=character.characteristics.stamina, source=PERSONA_SOURCE
        ),
        Line(PERSONA, amount=ability_level(character, PERSONA), source=PERSONA_SOURCE),
    ]
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def persona_trace_magnitude(sun_changes: int) -> int:
    """The magnitude the change shows as (Muto Corpus 10 at the moment),
    a magnitude less each sunrise or sunset since; below 0 only powerful
    Intellego Vim finds it (Societates p. 90)."""
    return PERSONA_TRACE_LEVEL // 5 - max(0, sun_changes)


def persona_spell_level(score: int) -> int:
    """The spell level a persona counts as for other magic (Sight of the
    True Form, Wind of Mundane Silence): 5 x Persona (p. 90)."""
    return 5 * max(0, score)


def ability_text(name: str, score: int) -> str:
    """What the Abilities details add for Guile and Persona ("" for any
    other)."""
    if name == "Guile":
        return (
            "Disguise: Intelligence + Guile + stress die against 9, +3 a change "
            "of social status, +1 / +3 a minor / major change of appearance, +6 "
            "a change of sex, +3 / +6 for minimal / no preparation; then "
            "Presence + Guile against the other's Intelligence + Folk Ken to "
            "talk with someone (Houses of Hermes: Societates p. 87)."
        )
    if name == PERSONA:
        count = max(0, score)
        identities = "an identity" if count == 1 else f"{count} identities"
        return (
            f"Persona {count}: {identities}. Stamina + Persona against 9, a round "
            "of concentration, to take one or return. Each persona has a "
            "Reputation from 1, gaining the xp put into Persona. The change "
            "shows as a Muto Corpus 10 effect, a magnitude less each sunrise "
            f"or sunset; to other magic it is level {persona_spell_level(count)} "
            "(DE p. 169; Houses of Hermes: Societates pp. 89-90)."
        )
    return ""
