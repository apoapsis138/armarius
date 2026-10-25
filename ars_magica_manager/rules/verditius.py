"""Verditius Magic, the Outer Mystery of House Verditius (DE pp. 240-241):
a Verditius who crafts an item from raw materials in its first season of
enchantment gives it Verditius Runes and a mystical link to his Craft.

- Runes: his Philosophiae added to the item's Shape and Material bonuses
  for enchanting it, by anyone, the total still capped by Magic Theory. A
  later Verditius enchanter with a higher Philosophiae raises it.
- Craft: the maker (no one else) adds his current score in the Craft
  Ability he used to every Lab Total for enchanting the item.
- Opening: the maker opens it for his Craft score fewer pawns of Vim vis
  (his Finesse when he shaped it by magic alone), at least one, and it
  counts as opened in full.

A device records that its maker crafted it this way (`verditius_runes`)
and with which Craft Ability (`verditius_craft`; blank for shaping by
magic). Crafting that takes more than a season lengthens the first
season's work; that is the troupe's to track.

Hubris (DE pp. 241-242): the first Initiation into a Verditius Inner
Mystery gives the Minor Personality Flaw Hubris and the Trait at 1 (+1
more with Proud, +3 with Proud as a Major Flaw). It grows like an Ability,
from the experience its table awards (HUBRIS_XP): selling or making for
pay, winning the Contest, learning Inner Mysteries, vendettas. Its score
adds to the Lab Totals for a talisman, enchanting casting tools, binding
magical animals, automata and attuned items (rules.lab_virtues adds it).

Enchant Casting Tools (Minor House Inner Mystery, DE pp. 242-243): a
season's lab work enchants one casting tool, once, for a spell the magus
knows, finished in that season like a lesser enchanted device. Its Lab
Total is Technique + Form + Intelligence + Magic Theory + aura (the
spell's Arts' Lab Total) + Philosophiae + Hubris + the known spell's
magnitude + a Craft that makes the tools; it must be at least twice the
effect level: the spell's level plus each property's increase
(CASTING_TOOL_EFFECTS). It takes a pawn of the Technique's or Form's vis
per 10 levels of that, rounded up.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from ..models import Character, EnchantedDevice, Laboratory, Saga, Spell
from . import lab, lab_virtues, xp
from .breakdown import Breakdown, Line
from .casting import magnitude
from .rounding import round_up

SOURCE = "Ars Magica Definitive Edition, House Verditius, Verditius Magic, pp. 240-241"
VERDITIUS_MAGIC = "vf_verditius_magic"
PHILOSOPHIAE = "Philosophiae"
FINESSE = "Finesse"


def is_verditius(magus: Character | None) -> bool:
    return magus is not None and lab_virtues.has(magus, VERDITIUS_MAGIC)


def _score(magus: Character, ability: str) -> int:
    level, bonus = lab.ability_score(magus, ability)
    return level + bonus


def maker_of(saga: Saga, device: EnchantedDevice) -> Character | None:
    return next((c for c in saga.characters if c.id == device.maker_id), None)


def crafts_it(saga: Saga, magus: Character, device: EnchantedDevice) -> bool:
    """Whether `magus` is the Verditius who crafted `device` (or will, the
    season he first works on it)."""
    return (
        device.verditius_runes
        and is_verditius(magus)
        and device.maker_id in (None, magus.id)
    )


def rune_bonus(saga: Saga, magus: Character, device: EnchantedDevice) -> int:
    """The Verditius Runes' addition to each of the item's Shape and
    Material bonuses: the best Philosophiae of its Verditius maker and of
    `magus`, if he is a Verditius too."""
    if not device.verditius_runes:
        return 0
    makers = [m for m in (maker_of(saga, device), magus) if is_verditius(m)]
    return max((_score(m, PHILOSOPHIAE) for m in makers if m), default=0)


def craft_line(saga: Saga, magus: Character, device: EnchantedDevice) -> Line | None:
    """The maker's Craft score on a Lab Total for enchanting his item."""
    if not device.verditius_craft or not crafts_it(saga, magus, device):
        return None
    score = _score(magus, device.verditius_craft)
    if not score:
        return None
    return Line(
        f"{device.verditius_craft} (Verditius Magic)", amount=score, source=SOURCE
    )


def opening_discount(saga: Saga, magus: Character, device: EnchantedDevice) -> int:
    """The pawns the maker saves opening his item: his Craft score, or his
    Finesse when he shaped it by magic. Only in its first season."""
    if device.pawns_opened or not crafts_it(saga, magus, device):
        return 0
    return _score(magus, device.verditius_craft or FINESSE)


# -- Hubris -----------------------------------------------------------------

HUBRIS_SOURCE = lab_virtues.HUBRIS_SOURCE
HUBRIS = "Hubris"
PROUD_BONUS = {"vf_proud": 1, "vf_proud_major": 3}
#: Experience Points toward Hubris for each behaviour (DE p. 242). Selling
#: an automaton gives one a magnitude of its Might (AUTOMATON).
HUBRIS_XP: dict[str, int] = {
    "Selling (or making for pay) a charged item or an item of quality": 1,
    "Repairing or reforging an item for another, for pay": 1,
    "Selling (or making for another) a lesser enchanted device": 1,
    "Selling (or making for another) a greater enchanted device": 3,
    "Selling (or making for another) an attuned item": 6,
    "Winning the Contest, apprentices": 1,
    "Winning the Contest, journeymen": 3,
    "Winning the Contest, masters": 6,
    "Learning a new minor House Inner Mystery": 1,
    "Learning a new major House Inner Mystery": 3,
    "Declaring a vendetta": 1,
    "Winning a vendetta": 3,
}
AUTOMATON = "Selling an automaton (per magnitude of Might)"


def starting_hubris(magus: Character) -> int:
    """The Hubris score the first Inner Mystery's Ordeal gives: 1, +1 with
    Proud, +3 with Proud as a Major Flaw (DE p. 241)."""
    return 1 + max(
        (PROUD_BONUS.get(vf.vf_id, 0) for vf in magus.virtues_flaws), default=0
    )


def hubris_xp(behaviour: str, might_magnitude: int = 0) -> int:
    """The experience a behaviour adds to Hubris (ValueError for one not on
    the table)."""
    if behaviour == AUTOMATON:
        return max(0, might_magnitude)
    if behaviour not in HUBRIS_XP:
        raise ValueError(f"{behaviour!r} isn't on the Hubris table.")
    return HUBRIS_XP[behaviour]


def hubris_score(total_xp: int, start: int = 1) -> int:
    """The Hubris score `total_xp` experience gives one who started at
    `start`: it grows like an Ability from there (DE p. 241)."""
    return xp.score_from_xp(xp.ability_xp(start) + total_xp, xp.ABILITY_FACTOR)


def hubris_of(magus: Character) -> int:
    """The magus's Hubris Personality Trait (0 without one)."""
    return next((t.score for t in magus.personality_traits if t.name == HUBRIS), 0)


# -- Enchant Casting Tools ----------------------------------------------------

CASTING_TOOLS_SOURCE = (
    "Ars Magica Definitive Edition, House Verditius, Enchant Casting Tools, pp. 242-243"
)
ENCHANT_CASTING_TOOLS = "vf_enchant_casting_tools"
#: A casting tool's property -> what each one adds to the effect level. A
#: bonus to the casting roll adds its own size; Multiple Casting's each
#: further spell adds 2 more; Quiet Casting taken twice casts silently.
CASTING_TOOL_EFFECTS: dict[str, int] = {
    "Fast Casting": 2,
    "Multiple Casting": 2,
    "Quiet Casting": 2,
    "Summon casting tool": 10,
    "Dismiss casting tool": 10,
}
#: The properties that may be taken more than once.
REPEATABLE = ("Multiple Casting", "Quiet Casting")
MAX_QUIET = 2


def casting_tool_level(
    spell_level: int, properties: Mapping[str, int], casting_bonus: int = 0
) -> int:
    """The effect level of a casting tool for a spell of `spell_level`:
    each property (name -> times taken) adds its increase, and a bonus to
    the casting roll adds itself. ValueError for an unknown property or one
    taken more often than it may be."""
    level = spell_level + max(0, casting_bonus)
    for name, times in properties.items():
        if name not in CASTING_TOOL_EFFECTS:
            raise ValueError(f"{name!r} isn't a casting tool property.")
        if times < 0 or (times > 1 and name not in REPEATABLE):
            raise ValueError(f"{name} can be taken only once.")
        if name == "Quiet Casting" and times > MAX_QUIET:
            raise ValueError("Quiet Casting can be taken at most twice.")
        level += CASTING_TOOL_EFFECTS[name] * times
    return level


def casting_tool_total(
    saga: Saga,
    magus: Character,
    spell: Spell,
    laboratory: Laboratory,
    *,
    craft: str = "",
) -> Breakdown:
    """The Lab Total for enchanting a casting tool for `spell`: the
    spell's Arts' Lab Total + Philosophiae + Hubris + the spell's magnitude
    + `craft`, a Craft that makes the tools (DE p. 243)."""
    total = lab.lab_total(saga, magus, spell.technique, spell.form, laboratory)
    added = [
        Line(
            PHILOSOPHIAE,
            amount=_score(magus, PHILOSOPHIAE),
            source=CASTING_TOOLS_SOURCE,
        )
    ]
    hubris = hubris_of(magus)
    if hubris:
        added.append(Line(HUBRIS, amount=hubris, source=CASTING_TOOLS_SOURCE))
    added.append(
        Line(
            f"Knows {spell.name} (its magnitude)",
            amount=magnitude(spell.level or 0),
            source=CASTING_TOOLS_SOURCE,
        )
    )
    if craft and _score(magus, craft):
        added.append(
            Line(craft, amount=_score(magus, craft), source=CASTING_TOOLS_SOURCE)
        )
    return Breakdown(
        total=int(total.total) + sum(line.amount or 0 for line in added),
        lines=[*total.lines, *added],
    )


def casting_tool_vis(effect_level: int) -> int:
    """Pawns of the Technique's or Form's vis: one per 10 levels, rounded up."""
    return max(1, round_up(effect_level / 10))


def casting_tool_problems(
    magus: Character, spell: Spell, total: int, effect_level: int
) -> list[str]:
    """What stops the enchantment: the Mystery, knowing the spell, and a
    Lab Total of at least twice the effect level."""
    found: list[str] = []
    if not lab_virtues.has(magus, ENCHANT_CASTING_TOOLS):
        found.append(f"{magus.name} hasn't been Initiated into Enchant Casting Tools.")
    if not any(k.spell_id == spell.id for k in magus.spells_known):
        found.append(f"{magus.name} doesn't know {spell.name}.")
    if total < 2 * effect_level:
        found.append(
            f"Lab Total {total} is below twice the effect level, {2 * effect_level}."
        )
    return found


def properties_text(properties: Sequence[tuple[str, int]]) -> str:
    """The properties as a line: "Fast Casting, Quiet Casting x2"."""
    return ", ".join(
        name if times == 1 else f"{name} x{times}"
        for name, times in properties
        if times
    )
