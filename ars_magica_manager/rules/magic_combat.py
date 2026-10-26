"""Magic in a fight: House Flambeau's schools of magical combat, indirect
spells that bypass Magic Resistance and must be aimed, and fighting
invisibly (Houses of Hermes: Societates pp. 25-33; DE pp. 221-223).

- **Schools of magical combat** (HoH:S pp. 25-30): six named approaches,
  each with the Virtue that suits it (the table on p. 26). A magus's
  school is his own choice; schools_for() lists those his Virtues suit.
  The Variant House Benefits option (p. 27) lets a Flambeau take one of
  the Ramius, Sebastian or Vilano Virtues in place of Puissant Ignem or
  Perdo.
- **Indirect spells** (DE pp. 221-223; HoH:S p. 30): a spell that moves
  or makes something mundane, which then harms the target, is not
  resisted, but must be aimed: Perception + Finesse + stress die, as an
  attack total, against the target's Defence (aimed spells are treated
  like missiles, HoH:S p. 32, so only a shield counts). +6 for each size
  step past a basic Individual. A hit does stress die + the spell's
  damage against Soak + stress die, with no Attack Advantage. Precise
  Casting adds +1 for each time it was taken and one botch die fewer, to
  a minimum of one (DE p. 226; HoH:S p. 34). Two stress rolls mean two chances to
  botch (p. 30). The 18 spells HoH:S p. 30 lists as indirect are here,
  each with the limit the book gives (the corpse spells only through a
  non-magical weapon; The Earth Split Asunder's fall but not its crush;
  the webs, oil, vines and coils hold and do no harm, so a Damage typed
  for them is refused), with the Invisible Sling of Vilano of its new
  spells (p. 38); any other is marked indirect when it is cast.
- **Spell Mastery** (DE pp. 225-226): a mastered spell's score adds to its
  Casting Score; the Penetration ability adds it to Penetration; the
  Magic Resistance ability doubles the target's Magic Resistance against
  the spell he has mastered (HoH:S p. 26 recommends it against the
  Founder's fire); similar spells (DE p. 226) are not matched here.
- **The Penetration multiplier** (DE pp. 219-220; HoH:S pp. 24, 27): an Arcane
  Connection adds by how long it lasts; with one, the target's name adds
  +1 and a symbolic representation +2.
- **Fighting invisibly** (HoH:S pp. 32-33, with the Errata p. 58): how
  clear the signs of an invisible fighter are sets his melee Attack,
  Defence and Stealth bonuses. He can't be struck, shot or targeted until
  located (a round's Perception + Awareness against his Dexterity +
  Stealth - Encumbrance + Stealth bonus), except by one he engages in
  melee, an area spell, or one cast through an Arcane Connection; Eye
  range works neither way. Against a foe who hasn't located him he goes
  first in the first round and adds +3 to his Attack. His weapon and his
  touch are magical, so Magic Resistance keeps them out (DE p. 223; HoH:S
  p. 32); only a non-magical weapon picked up after turning invisible
  gets through. Obvious signs set the bonuses and let observers locate
  him; they don't make the blow non-magical. He can't
  fight in a trained group; an untrained group gains a botch die for each
  invisible member; and allies can't defend him.

Pattern: plain rule functions and tables; rules.fight adds their terms to
its totals.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Character, Creature, KnownSpell, Spell
from . import casting
from .breakdown import Breakdown, Line
from .derived import carried_load, encumbrance, fatigue_penalty, wound_penalty
from .lab import ability_score

SOURCE = (
    "Houses of Hermes: Societates, House Flambeau, Schools of Magical Combat "
    "and Rules for Magical Combat, pp. 25-33"
)
SCHOOLS_SOURCE = "Houses of Hermes: Societates, Schools of Magical Combat, pp. 25-30"
INVISIBLE_SOURCE = (
    "Houses of Hermes: Societates, Fighting Invisibly, pp. 32-33; Errata p. 58"
)
AIMING_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 7: Hermetic Magic, Aiming, p. 223; "
    "Houses of Hermes: Societates, School of Vilano, p. 30"
)
MASTERY_SOURCE = casting.MASTERY_SOURCE
PRECISE_SOURCE = (
    "Ars Magica Definitive Edition, Precise Casting, p. 226; Houses of Hermes: "
    "Societates p. 34"
)

PUISSANT_ART = "vf_puissant_art"
PUISSANT_ABILITY = "vf_puissant_ability"
CAUTIOUS_WITH = "vf_cautious_with_ability"
WARRIOR = "vf_warrior"
MAJOR_FOCUS = "vf_major_magical_focus"
MINOR_FOCUS = "vf_minor_magical_focus"


@dataclass(frozen=True)
class Suit:
    """A Virtue a school recommends: its id, and the Art or Ability it
    must name ("" for any)."""

    vf_id: str
    names: str = ""


@dataclass(frozen=True)
class School:
    """A school of magical combat (HoH:S p. 26, Schools at a Glance)."""

    name: str
    description: str
    recommended: str
    suits: tuple[Suit, ...]


SCHOOLS: tuple[School, ...] = (
    School(
        "The Founder",
        "Attacks using fire",
        "Puissant Ignem",
        (Suit(PUISSANT_ART, "ignem"),),
    ),
    School(
        "Apromor",
        "Damaging the opponent directly with Perdo",
        "Puissant Perdo",
        (Suit(PUISSANT_ART, "perdo"),),
    ),
    School(
        "Boreas",
        "Direct attacks using cold",
        "Puissant Ignem or Puissant Perdo",
        (Suit(PUISSANT_ART, "ignem"), Suit(PUISSANT_ART, "perdo")),
    ),
    School(
        "Ramius",
        "Mundane attacks, magical defences",
        "Warrior",
        (Suit(WARRIOR),),
    ),
    School(
        "Sebastian",
        "Direct attacks using a Form other than Ignem",
        "Magical Focus",
        (Suit(MAJOR_FOCUS), Suit(MINOR_FOCUS)),
    ),
    School(
        "Vilano",
        "Aimed spells that bypass Magic Resistance",
        "Puissant Finesse or Cautious With Ability (Finesse)",
        (Suit(PUISSANT_ABILITY, "finesse"), Suit(CAUTIOUS_WITH, "finesse")),
    ),
)
#: The Variant House Benefits option: the schools whose recommended
#: Virtue a Flambeau may take in place of Puissant Ignem or Perdo (HoH:S
#: p. 27).
VARIANT_HOUSE_SCHOOLS = ("Ramius", "Sebastian", "Vilano")


def _has(character: Character, suit: Suit) -> bool:
    for vf in character.virtues_flaws:
        if vf.vf_id != suit.vf_id:
            continue
        if not suit.names:
            return True
        named = {str(v).strip().casefold() for v in vf.params.values()}
        if suit.names in named:
            return True
    return False


def schools_for(character: Character) -> list[School]:
    """The schools whose recommended Virtue the magus has (HoH:S p. 26):
    the ones his Gift suits, as Flambeau magi choose theirs (p. 25)."""
    return [s for s in SCHOOLS if any(_has(character, suit) for suit in s.suits)]


def schools_text(character: Character) -> str:
    """ "Suited to the Schools of the Founder and Boreas (HoH:S p. 26)", or
    "" when no school's Virtue is his."""
    names = [
        "the Founder" if s.name == "The Founder" else s.name
        for s in schools_for(character)
    ]
    if not names:
        return ""
    joined = (
        names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
    )
    word = "School" if len(names) == 1 else "Schools"
    return f"Suited to the {word} of {joined} (HoH:S p. 26)."


# -- indirect spells and aiming --


@dataclass(frozen=True)
class IndirectSpell:
    """A spell HoH:S names as at least partly effective without
    penetrating Magic Resistance: when it falls short (`limit`, "" for
    none), and whether it only holds or traps and does no harm itself."""

    name: str
    limit: str = ""
    harmless: bool = False


_CORPSE = (
    "it bypasses Magic Resistance only through a non-magical weapon the "
    "corpse wields; its unarmed attack is resisted (the whole corpse is "
    "under the spell)"
)
_HOLDS = "it surrounds and holds him in place; it does no harm itself"
_FLAME = (
    "the flame's motion is magical but the flame isn't: it stops as if it "
    "had touched him gently, but still burns him"
)
#: The 18 spells of the Definitive Edition HoH:S p. 30 lists as at least
#: partly effective without penetrating Magic Resistance, each with its
#: limit as the book gives it.
SOCIETATES_INDIRECT: tuple[IndirectSpell, ...] = (
    IndirectSpell("Weaver's Trap of Webs", _HOLDS, harmless=True),
    IndirectSpell(
        "Footsteps of Slippery Oil",
        "she can step in the magical oil, as she can walk a magical bridge; it "
        "does no harm itself",
        harmless=True,
    ),
    IndirectSpell(
        "Waves of Drowning and Smashing",
        "the wave can't harm her directly: it can capsize her boat or wash out "
        "the bridge she stands on",
    ),
    IndirectSpell(
        "Neptune's Wrath",
        "as Waves of Drowning and Smashing: it can't harm her directly, only "
        "capsize her boat or wash out her bridge, more destructively",
    ),
    IndirectSpell("Awaken the Slumbering Corpse", _CORPSE),
    IndirectSpell("Strings of the Unwilling Marionette", _CORPSE),
    IndirectSpell("The Walking Corpse", _CORPSE),
    IndirectSpell(
        "Trap of the Entwining Vines",
        "the vines surround her and keep her from moving about, without "
        "wholly immobilizing her; they do no harm themselves",
        harmless=True,
    ),
    IndirectSpell(
        "Tangle of Wood and Thorns",
        "completely effective: the wood immobilizes him without touching him "
        "(the storyguide may give a bonus to the Strength roll to escape)",
    ),
    IndirectSpell(
        "Coils of the Entangling Plants",
        "as Weaver's Trap of Webs: " + _HOLDS,
        harmless=True,
    ),
    IndirectSpell("Tremulous Vault of the Torch's Flame", _FLAME),
    IndirectSpell("Leap of the Fire", _FLAME),
    IndirectSpell("Pit of the Gaping Earth"),
    IndirectSpell(
        "Obliteration of the Metallic Barrier",
        "the shards are thrown as projectiles",
    ),
    IndirectSpell(
        "End of the Mighty Castle",
        "Magic Resistance doesn't stop non-magical stone falling",
    ),
    IndirectSpell(
        "Cascade of Rocks",
        "only on a steep hillside or at the foot of a cliff",
    ),
    IndirectSpell(
        "The Earth Split Asunder",
        "Magic Resistance doesn't stop his fall into the chasm, but it does "
        "stop his being crushed when it closes violently (closing slowly, it "
        "isn't resisted, and he can likely climb out)",
    ),
    IndirectSpell("Creeping Chasm"),
)
#: The new spells of HoH:S that are indirect too: the Invisible Sling of
#: Vilano, which p. 30 recommends for use anywhere (p. 38).
NEW_INDIRECT: tuple[IndirectSpell, ...] = (IndirectSpell("Invisible Sling of Vilano"),)
INDIRECT_SPELLS: dict[str, IndirectSpell] = {
    spell.name.casefold(): spell for spell in (*SOCIETATES_INDIRECT, *NEW_INDIRECT)
}
#: Each size step past a basic Individual adds +6 to the aiming roll.
AIM_PER_STEP = 6


def _plain(name: str) -> str:
    return name.replace("’", "'").strip().casefold()


def indirect_spell(spell: Spell | None) -> IndirectSpell | None:
    """The entry for a spell HoH:S names as indirect (None for another)."""
    return None if spell is None else INDIRECT_SPELLS.get(_plain(spell.name))


def is_indirect(spell: Spell | None) -> bool:
    """Whether HoH:S names the spell as indirect (p. 30, or its new
    spells, p. 38)."""
    return indirect_spell(spell) is not None


def indirect_note(spell: Spell | None) -> str:
    """The inspector's line on a named indirect spell's limit ("" for none)."""
    entry = indirect_spell(spell)
    if entry is None or not entry.limit:
        return ""
    return f"{entry.name} is only partly indirect: {entry.limit} (HoH:S p. 30)."


def aiming(magus: Character, *, precise: int = 0, steps: int = 0) -> Breakdown:
    """An aiming roll before the die: Perception + Finesse, with the
    Wound, Fatigue and Finesse penalties (casting.aiming_base), +1 for
    each Precise Casting and +6 for each size step past a basic
    Individual (DE pp. 223, 226)."""
    base = casting.aiming_base(magus)
    lines = [Line("Perception + Finesse", amount=base, source=AIMING_SOURCE)]
    if precise:
        lines.append(Line("Precise Casting", amount=precise, source=PRECISE_SOURCE))
    if steps > 0:
        lines.append(
            Line(
                f"Larger than a basic Individual ({steps} step(s))",
                amount=AIM_PER_STEP * steps,
                source=AIMING_SOURCE,
            )
        )
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def aim_botch_dice(precise: int = 0) -> int:
    """The aiming roll's botch dice: one, less one for each Precise
    Casting, to a minimum of one (DE p. 226)."""
    return max(1, 1 - precise)


# -- Spell Mastery in a fight --


def known_spell(character: Character | None, spell_id: str) -> KnownSpell | None:
    """The character's record of a spell he knows, Mastery and all."""
    if character is None:
        return None
    return next((k for k in character.spells_known if k.spell_id == spell_id), None)


def mastery_abilities(known: KnownSpell | None) -> dict[str, int]:
    return casting.mastery_counts(known.mastery_abilities) if known else {}


def penetration_mastery(known: KnownSpell | None) -> int:
    """The Mastery score Penetration Mastery adds to Penetration (DE p.
    226): 0 without the ability."""
    if known is None or not mastery_abilities(known).get(casting.PENETRATION_MASTERY):
        return 0
    return known.mastery_score


def resists_doubly(target: Character | None, spell_id: str) -> bool:
    """Whether the target has mastered this spell with the Magic
    Resistance ability, which doubles his Magic Resistance against it (DE
    p. 226; HoH:S p. 26)."""
    known = known_spell(target, spell_id)
    return bool(
        known is not None
        and known.mastery_score
        and mastery_abilities(known).get(casting.RESISTANCE_MASTERY)
    )


#: The sympathetic connections the Enhancing Spell Penetration sidebar
#: names (HoH:S p. 27; DE p. 220): each needs an Arcane Connection
#: (DE p. 219).
NAME_SYMPATHY = "Target's nickname or birth name"
SYMBOL_SYMPATHY = "Symbolic representation"


# -- fighting invisibly --


@dataclass(frozen=True)
class Clarity:
    """How clear an invisible fighter's signs are, and what that gives him
    (HoH:S p. 33, Effects of Invisibility)."""

    key: str
    label: str
    examples: str
    attack: int
    defence: int
    stealth: int
    #: Observers locate him without a roll (the table's *).
    seen: bool = False
    #: No visual detection at all: only by sound (the Errata's **).
    unseeable: bool = False


CLARITIES: tuple[Clarity, ...] = (
    Clarity("obvious", "Obvious", "a visible sword, mud, wading", 1, 3, 3, seen=True),
    Clarity("clear", "Clear", "a shadow in sunlight, footprints in sand", 3, 3, 3),
    Clarity(
        "indistinct", "Indistinct", "a shadow on a cloudy day, packed earth", 3, 6, 6
    ),
    Clarity("faint", "Faint", "a shadow in moonlight, cobblestones", 6, 9, 9),
    Clarity(
        "none",
        "No signs",
        "no visual cues; found by sound alone",
        9,
        9,
        12,
        unseeable=True,
    ),
)
CLARITY_BY_KEY = {c.key: c for c in CLARITIES}
#: An invisible fighter's surprise attack: +3 to Attack (HoH:S p. 32).
SURPRISE_ATTACK = 3
#: Ranges and targets that reach an invisible fighter unlocated: an area
#: spell, or one cast through an Arcane Connection (HoH:S p. 32).
ARCANE_RANGE = "Arcane Connection"
EYE_RANGE = "Eye"
AREA_TARGETS = frozenset({"group", "room", "structure", "boundary"})


def clarity(key: str) -> Clarity | None:
    """The clarity of an invisible fighter's signs ("" visible: None)."""
    return CLARITY_BY_KEY.get(key)


def reaches_unlocated(range_: str, target: str) -> bool:
    """Whether a spell of this Range and Target reaches an invisible
    fighter nobody has located: an area spell does, and so does one cast
    through an Arcane Connection (HoH:S p. 32)."""
    return range_ == ARCANE_RANGE or target.strip().casefold() in AREA_TARGETS


def _level(holder: Character | Creature, name: str) -> int:
    if isinstance(holder, Character):
        return sum(ability_score(holder, name))
    return next((a.level for a in holder.abilities if a.name == name), 0)


def _penalty(holder: Character | Creature) -> int:
    return wound_penalty(holder.wounds, holder.virtues_flaws) + fatigue_penalty(
        holder.fatigue_level, holder.virtues_flaws
    )


def locate_base(holder: Character | Creature | None) -> Breakdown:
    """A round's search for an invisible fighter, before the stress die:
    Perception + Awareness, with the Wound and Fatigue penalties (HoH:S p.
    32). A typed fighter has no Perception or Awareness here: 0."""
    if holder is None:
        return Breakdown(total=0, lines=[])
    lines = [
        Line("Perception", amount=holder.characteristics.perception, source=SOURCE),
        Line("Awareness", amount=_level(holder, "Awareness"), source=INVISIBLE_SOURCE),
    ]
    penalty = _penalty(holder)
    if penalty:
        lines.append(Line("Wounds and fatigue", amount=penalty, source=SOURCE))
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def hide_base(holder: Character | Creature | None, signs: Clarity) -> Breakdown:
    """An invisible fighter's roll against being located, before the
    stress die: Dexterity + Stealth - Encumbrance + the Stealth bonus for
    his signs (HoH:S p. 32)."""
    lines: list[Line] = []
    if isinstance(holder, Character):
        enc = encumbrance(
            carried_load(holder.inventory), holder.characteristics.strength
        )
        lines += [
            Line("Dexterity", amount=holder.characteristics.dexterity, source=SOURCE),
            Line("Stealth", amount=_level(holder, "Stealth"), source=SOURCE),
        ]
        if enc:
            lines.append(Line("Encumbrance", amount=-enc, source=INVISIBLE_SOURCE))
    elif holder is not None:
        lines += [
            Line("Dexterity", amount=holder.characteristics.dexterity, source=SOURCE),
            Line("Stealth", amount=_level(holder, "Stealth"), source=SOURCE),
        ]
    lines.append(
        Line(
            f"Invisible ({signs.label})", amount=signs.stealth, source=INVISIBLE_SOURCE
        )
    )
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def group_botch_dice(invisible_members: int) -> int:
    """The extra botch dice a group rolls for its invisible members: one
    each (HoH:S p. 33, with the Errata's "untrained"). A group with an
    invisible member can't fight as a trained one, so this is always an
    untrained group's."""
    return max(0, invisible_members)
