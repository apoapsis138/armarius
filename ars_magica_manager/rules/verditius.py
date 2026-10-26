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

The Mystery Cult (Houses of Hermes: Mystery Cults pp. 116-123): the
Initiation Total is Presence + Verditius Cult Lore + the Script, with the
House's own Script components (VERDITIUS_COMPONENTS). The Outer Mystery is
given as the apprentice's Arts are opened (Target 15, Script +12, a
Mystagogue with Presence + Lore 3). An Initiate needs the Lore at 3 for a
Minor Inner Mystery and 5 for a Major one; the first Inner Mystery always
brings Hubris. The House's Ordeals may each be suffered once; Prone to
Chance and Averse to Risk exclude each other, and no one in the Primus's
line may Sever the Ties that Bind. The sample Scripts are the tradition
catalog's "trad_verditius_mysteries".

The Inner Mysteries' laboratory rules (pp. 123-135): Elder Runes (a
Technique's and a Form's rune doubles that Art enchanting the item, +5 to
each effect's level, +2 on the rune's own wood, a pawn of the Art's vis
each; the season's vis limit becomes Magic Theory x Philosophiae), Items of
Quality, Reforging, Automata, Bind Curse, Bind Magical Creatures and Item
Attunement (its capacity and Hubris on its Lab Totals). The Definitive
Edition (pp. 240-243) reprints Verditius Magic, Hubris and Enchant Casting
Tools; where they differ it wins (Enchant Casting Tools' Ordeal is Hubris
when it is the first Inner Mystery, DE p. 243).
"""

from __future__ import annotations

import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from ..arts import FORMS, TECHNIQUES
from ..models import (
    CHARGED,
    INVESTED,
    Character,
    EnchantedDevice,
    InstilledEffect,
    Laboratory,
    RefusedVendetta,
    Saga,
    ScoredTrait,
    Spell,
)
from . import confidence, dice, enchantment, lab, lab_virtues, mysteries, xp
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
HUBRIS_FLAW = lab_virtues.HUBRIS
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


# -- The Mystery Cult: Initiation (HoH:MC pp. 116-121) -------------------------

MC = "Houses of Hermes: Mystery Cults"
INITIATION_SOURCE = f"{MC}, Initiation into the Mysteries of Verditius, pp. 117-118"
ORDEALS_SOURCE = f"{MC}, Ordeals, pp. 120-121"
#: The cult's Lore, as the Ability catalog names it; the book's own name
#: and the older "House Verditius Lore" count too.
CULT_LORE = "Mystery Cult Lore: Verditius"
LORE_NAMES = (CULT_LORE, "Verditius Cult Lore", "House Verditius Lore")
#: The tradition catalog entry holding the House's sample Scripts.
CULT_TRADITION = "trad_verditius_mysteries"

#: The House's Script components and their bonuses (p. 117).
VERDITIUS_COMPONENTS: tuple[mysteries.Component, ...] = (
    mysteries.Component(
        "Travel to a Forge of Hephaestus, or a special place at a special time", 3
    ),
    mysteries.Component("A specific Quest (a lost Verditius item)", 3),
    mysteries.Component("A unique Quest (a legendary item lost since antiquity)", 6),
    mysteries.Component("Minor Ordeal", 3),
    mysteries.Component("Major Ordeal", 9),
    mysteries.Component("The Initiate sacrifices time serving the House", 1, once=True),
    mysteries.Component(
        "The Initiate sacrifices a lesser enchanted item (4th magnitude or more)",
        3,
        key="verditius_lesser_item",
    ),
    mysteries.Component(
        "The Initiate sacrifices a greater enchanted item (7th magnitude or more) "
        "or his talisman",
        6,
        key="verditius_greater_item",
    ),
    mysteries.Component("The Mystagogue sacrifices time (teaching or training)", 3),
    mysteries.Component(
        "The Mystagogue sacrifices wealth (a Mythic Pound per point of Hubris)",
        1,
        once=True,
        key="verditius_wealth",
    ),
    mysteries.Component(
        "The Outer Mystery taught as the Arts are opened", 6, key="verditius_outer"
    ),
)
#: The House's own components a Verditius Initiate's plan may list besides
#: the general ones (the others are the general ones under House names).
HOUSE_COMPONENTS: tuple[mysteries.Component, ...] = tuple(
    c for c in VERDITIUS_COMPONENTS if c.key
)

#: The Outer Mystery's Initiation (p. 118): its Target, its Script's bonus
#: (special place, both sacrifices of time, wealth, Arts opened at once)
#: and the Mystagogue's least Presence + Lore.
OUTER_TARGET = 15
OUTER_SCRIPT_BONUS = 12
OUTER_MYSTAGOGUE_LEAST = 3
#: The Lore a Mystagogue needs to open an apprentice's Arts as he
#: initiates him, and an Initiate's to be Initiated into a Minor or a Major
#: Inner Mystery (p. 118).
LORE_TO_OPEN_ARTS = 2
LORE_FOR_INNER: dict[str, int] = {"Minor": 3, "Major": 5}
#: The House's Inner Mysteries and their tiers (p. 123).
INNER_MYSTERIES: dict[str, str] = {
    ENCHANT_CASTING_TOOLS: "Minor",
    "vf_items_of_quality": "Minor",
    "vf_reforging_enchanted_items": "Minor",
    "vf_verditius_elder_runes": "Minor",
    "vf_automata": "Major",
    "vf_bind_curse": "Major",
    "vf_bind_magical_creatures": "Major",
    "vf_item_attunement": "Major",
}
#: Experience toward Hubris for learning an Inner Mystery, by tier.
INNER_HUBRIS_XP: dict[str, int] = {
    "Minor": HUBRIS_XP["Learning a new minor House Inner Mystery"],
    "Major": HUBRIS_XP["Learning a new major House Inner Mystery"],
}
#: The House's Ordeals (pp. 120-121), as the Flaws they give.
PRONE_TO_CHANCE = "vf_prone_to_chance"
AVERSE_TO_RISK = "vf_averse_to_risk"
SEVER_THE_TIES = ("vf_sever_the_ties_that_bind", "vf_sever_the_ties_that_bind_major")
SELF_MUTILATION = ("vf_lame", "vf_hobbled", "vf_crippled")
INCREASED_HUBRIS = "vf_increased_hubris"
ORDEALS: tuple[str, ...] = (
    *SEVER_THE_TIES,
    *SELF_MUTILATION,
    PRONE_TO_CHANCE,
    AVERSE_TO_RISK,
    INCREASED_HUBRIS,
)
PRIMOGENITURE = "vf_primogeniture_lineage"


def cult_lore(magus: Character) -> int:
    """The magus's Verditius Cult Lore (the best of its names)."""
    return max((_score(magus, name) for name in LORE_NAMES), default=0)


def outer_mystery_problem(mystagogue: Character, opens_arts: bool = True) -> str:
    """What stops a master giving the Outer Mystery ("" if nothing): he
    needs Presence + Verditius Cult Lore 3, and the Lore at 2 to open the
    apprentice's Arts in the same season (pp. 117-118)."""
    lore = cult_lore(mystagogue)
    if mystagogue.characteristics.presence + lore < OUTER_MYSTAGOGUE_LEAST:
        return (
            f"{mystagogue.name}'s Presence + Verditius Cult Lore is below "
            f"{OUTER_MYSTAGOGUE_LEAST}: he can't give the Outer Mystery "
            f"({INITIATION_SOURCE})."
        )
    if opens_arts and lore < LORE_TO_OPEN_ARTS:
        return (
            f"{mystagogue.name} needs Verditius Cult Lore {LORE_TO_OPEN_ARTS} to "
            f"open an apprentice's Arts as he initiates him ({INITIATION_SOURCE})."
        )
    return ""


def outer_initiation_total(mystagogue: Character) -> Breakdown:
    """The Outer Mystery's Initiation Total: Presence + Lore + its Script's
    +12, against OUTER_TARGET."""
    lines = [
        Line(
            "Presence",
            amount=mystagogue.characteristics.presence,
            source=INITIATION_SOURCE,
        ),
        Line(
            "Verditius Cult Lore",
            amount=cult_lore(mystagogue),
            source=INITIATION_SOURCE,
        ),
        Line(
            "Script (special place, sacrifices, Arts opened)",
            amount=OUTER_SCRIPT_BONUS,
            source=INITIATION_SOURCE,
        ),
    ]
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def inner_mystery_problem(initiate: Character, vf_id: str) -> str:
    """What stops an Initiation into one of the House's Inner Mysteries
    ("" if nothing, or for any other Virtue): the Initiate must be a
    Verditius, with the Lore at 3 for a Minor one and 5 for a Major."""
    tier = INNER_MYSTERIES.get(vf_id)
    if tier is None:
        return ""
    if not is_verditius(initiate):
        return (
            f"{initiate.name} hasn't the Outer Mystery (Verditius Magic): only a "
            f"Verditius learns the House's Inner Mysteries ({INITIATION_SOURCE})."
        )
    needed = LORE_FOR_INNER[tier]
    if cult_lore(initiate) < needed:
        return (
            f"{initiate.name} needs Verditius Cult Lore {needed} to be Initiated "
            f"into a {tier} Inner Mystery ({INITIATION_SOURCE})."
        )
    return ""


def gives_hubris(initiate: Character, vf_id: str) -> bool:
    """Whether this Initiation is the magus's first into an Inner Mystery,
    whose Ordeal always gives the Minor Flaw Hubris (p. 118; DE p. 241)."""
    return vf_id in INNER_MYSTERIES and not lab_virtues.has(initiate, HUBRIS_FLAW)


def initiation_notes(initiate: Character, vf_id: str) -> list[str]:
    """What an Inner Mystery's Initiation adds besides its Virtue: Hubris
    with the first, and Hubris experience for every one."""
    tier = INNER_MYSTERIES.get(vf_id)
    if tier is None:
        return []
    notes: list[str] = []
    if gives_hubris(initiate, vf_id):
        notes.append(
            "The first Inner Mystery's Ordeal gives the Flaw Hubris, and sets the "
            f"Hubris Personality Trait to {starting_hubris(initiate)} "
            f"({HUBRIS_SOURCE})."
        )
    notes.append(
        f"Learning a {tier} Inner Mystery: {INNER_HUBRIS_XP[tier]} experience "
        f"toward Hubris ({HUBRIS_SOURCE})."
    )
    return notes


def ordeal_problem(initiate: Character, flaw_id: str) -> str:
    """What the House's rules forbid of an Ordeal ("" if nothing): each
    may be suffered once, Prone to Chance and Averse to Risk exclude each
    other, and one in the Primus's line may not Sever the Ties that Bind."""
    if flaw_id not in ORDEALS:
        return ""
    held = {vf.vf_id for vf in initiate.virtues_flaws}
    if flaw_id in held or (flaw_id in SEVER_THE_TIES and held & set(SEVER_THE_TIES)):
        return (
            f"{initiate.name} has suffered that Ordeal already: each may be "
            f"suffered once ({ORDEALS_SOURCE})."
        )
    if {flaw_id, *held} >= {PRONE_TO_CHANCE, AVERSE_TO_RISK}:
        return (
            "Prone to Chance and Averse to Risk can't both be suffered "
            f"({ORDEALS_SOURCE})."
        )
    if flaw_id in SEVER_THE_TIES and PRIMOGENITURE in held:
        return (
            f"{initiate.name} is in the Primus's line and may not Sever the Ties "
            f"that Bind ({ORDEALS_SOURCE})."
        )
    return ""


# -- Verditius Elder Runes (pp. 127-128) ---------------------------------------

ELDER_RUNES_SOURCE = enchantment.ELDER_RUNES_SOURCE
ELDER_RUNES = "vf_verditius_elder_runes"
#: Art -> (the rune's meaning, its tree). Only twelve Arts have runes.
ELDER_RUNE_TABLE: dict[str, tuple[str, str]] = {
    "Creo": ("Health", "birch"),
    "Intellego": ("Sight", "yew"),
    "Perdo": ("Pain", "pine"),
    "Rego": ("Ice", "alder"),
    "Animal": ("Cattle", "elder"),
    "Aquam": ("Water", "willow"),
    "Auram": ("Hail", "ash"),
    "Corpus": ("Man", "holly"),
    "Herbam": ("Harvest", "apple"),
    "Ignem": ("Sun", "juniper"),
    "Mentem": ("Loyalty", "oak"),
    "Vim": ("Ogre", "hawthorn"),
}
#: The Lab Total bonus for a rune on its own tree's wood.
TREE_BONUS = 2


def elder_rune_problems(magus: Character, device: EnchantedDevice) -> list[str]:
    """What is wrong with the elder runes on `device` as `magus` opens it:
    he must know the Mystery; only an invested device takes them, at most
    one Technique's and one Form's, each an Art that has a rune."""
    runes = list(device.elder_runes)
    if not runes:
        return []
    found: list[str] = []
    if not lab_virtues.has(magus, ELDER_RUNES):
        found.append(f"{magus.name} hasn't been Initiated into Verditius Elder Runes.")
    if device.type != INVESTED:
        found.append(
            "Elder runes are inscribed as a device is opened: only a greater "
            "enchanted item, an attuned item or a talisman bears them."
        )
    unknown = [art for art in runes if art not in ELDER_RUNE_TABLE]
    if unknown:
        found.append(f"No elder rune is adapted to {', '.join(unknown)}.")
    if (
        len(runes) > 2
        or sum(art in TECHNIQUES for art in runes) > 1
        or sum(art in FORMS for art in runes) > 1
    ):
        found.append(
            "A device takes at most two elder runes: a Technique's and a Form's."
        )
    return found


def rune_vis(device: EnchantedDevice) -> dict[str, int]:
    """The vis inscribing the runes takes: a pawn of each rune's Art."""
    cost: dict[str, int] = {}
    for art in enchantment.elder_runes(device):
        cost[art] = cost.get(art, 0) + 1
    return cost


def _on_its_tree(device: EnchantedDevice, tree: str) -> bool:
    words = " ".join(
        [device.name, device.description, *(c.description for c in device.components)]
    ).lower()
    return tree in words.replace(",", " ").split()


def elder_rune_lines(
    magus: Character, device: EnchantedDevice, effect: InstilledEffect
) -> list[Line]:
    """The runes on a Lab Total for instilling `effect`: each rune of the
    effect's Technique or Form adds that Art again (doubling it, like a
    Magical Focus), and +2 when the device is of the rune's tree, for a
    magus who knows the Mystery."""
    if not lab_virtues.has(magus, ELDER_RUNES):
        return []
    lines: list[Line] = []
    for art in enchantment.elder_runes(device):
        if art in (effect.technique, effect.form):
            lines.append(
                Line(
                    f"Elder rune doubles {art}",
                    amount=sum(lab.art_score(magus, art)),
                    source=ELDER_RUNES_SOURCE,
                )
            )
        tree = ELDER_RUNE_TABLE.get(art, ("", ""))[1]
        if tree and _on_its_tree(device, tree):
            lines.append(
                Line(
                    f"Elder rune on {tree} wood",
                    amount=TREE_BONUS,
                    source=ELDER_RUNES_SOURCE,
                )
            )
    return lines


def enchanting_vis_limit(magus: Character) -> int:
    """The most vis the magus may use in a season enchanting a device:
    twice Magic Theory, or with Elder Runes Magic Theory x Philosophiae in
    its place, even when that is less (HoH:MC pp. 126, 128: the limit
    "becomes" it)."""
    usual = lab.vis_limit(magus)
    if not lab_virtues.has(magus, ELDER_RUNES):
        return usual
    return (usual // 2) * _score(magus, PHILOSOPHIAE)


def vis_limit_text(magus: Character) -> str:
    """How the season's vis limit was reached, for a message."""
    if lab_virtues.has(magus, ELDER_RUNES):
        return "Magic Theory x Philosophiae, with Elder Runes"
    return "twice Magic Theory"


# -- Items of the Major Mysteries: Hubris on their Lab Totals -------------------

ATTUNEMENT_SOURCE = f"{MC}, Item Attunement, p. 135"
AUTOMATA_SOURCE = f"{MC}, Automata, pp. 128-131"
ITEM_ATTUNEMENT = "vf_item_attunement"
AUTOMATA = "vf_automata"
#: The Mystery each kind of item needs.
ITEM_MYSTERY = {enchantment.ATTUNED: ITEM_ATTUNEMENT, enchantment.AUTOMATON: AUTOMATA}


def hubris_item_line(magus: Character, device: EnchantedDevice) -> Line | None:
    """Hubris on every Lab Total for enchanting an attuned item or an
    automaton, for its Verditius maker (pp. 129, 135; DE p. 241)."""
    if device.verditius_item not in ITEM_MYSTERY or device.maker_id not in (
        None,
        magus.id,
    ):
        return None
    hubris = hubris_of(magus)
    if not hubris or not lab_virtues.has(magus, lab_virtues.HUBRIS):
        return None
    source = (
        ATTUNEMENT_SOURCE
        if device.verditius_item == enchantment.ATTUNED
        else AUTOMATA_SOURCE
    )
    return Line(HUBRIS, amount=hubris, source=source)


def mystery_lines(
    magus: Character, device: EnchantedDevice, effect: InstilledEffect
) -> list[Line]:
    """Every Verditius Inner Mystery line on a Lab Total for instilling
    `effect` in `device`."""
    lines = elder_rune_lines(magus, device, effect)
    hubris = hubris_item_line(magus, device)
    if hubris is not None:
        lines.append(hubris)
    return lines


def item_problems(
    magus: Character, device: EnchantedDevice, effect: InstilledEffect | None = None
) -> list[str]:
    """What the Major Mysteries' items forbid: the maker must know the
    Mystery; an automaton is never a talisman nor holds a power that
    maintains concentration (pp. 129-130)."""
    kind = device.verditius_item
    if kind not in ITEM_MYSTERY:
        return []
    found: list[str] = []
    if device.type != INVESTED:
        found.append(f"An {kind} item is a greater enchanted item (invested).")
    if device.maker_id in (None, magus.id) and not lab_virtues.has(
        magus, ITEM_MYSTERY[kind]
    ):
        mystery = "Item Attunement" if kind == enchantment.ATTUNED else "Automata"
        found.append(f"{magus.name} hasn't been Initiated into {mystery}.")
    if kind == enchantment.AUTOMATON:
        if device.talisman:
            found.append("An automaton can't be a talisman.")
        if effect is not None and effect.maintains_concentration:
            found.append(
                "An automaton can't maintain concentration: its powers can't "
                "have that modification."
            )
    return found


# -- Items of Quality (pp. 124-125) --------------------------------------------

QUALITY_SOURCE = f"{MC}, Items of Quality, pp. 124-125"
ITEMS_OF_QUALITY = "vf_items_of_quality"
#: A season and a pawn of Vim vis make one, whatever the Lab Total; its
#: magic shows to an investigation as a Lab Total of 10.
QUALITY_VIS = 1
QUALITY_INVESTIGATION = 10


def item_of_quality_bonus(magus: Character, shape_material_bonus: int) -> int:
    """The bonus an item of quality gives its user's rolls: the one Shape
    and Material bonus drawn out, at most the maker's Philosophiae."""
    return max(0, min(shape_material_bonus, _score(magus, PHILOSOPHIAE)))


# -- Reforging Enchanted Items (pp. 125-127) -----------------------------------

REFORGING_SOURCE = f"{MC}, Reforging Enchanted Items, pp. 125-127"
#: An investigation told the item's true properties adds 20.
TOLD_PROPERTIES = 20
REFORGED, UNCHANGED, FLAWED, DESTROYED = "reforged", "unchanged", "flawed", "destroyed"


def repair_ease(creator_philosophiae: int = 0) -> int:
    """The Dexterity + Craft Ease Factor to mend an item physically: 9, +
    its Verditius maker's Philosophiae when he made it."""
    return 9 + max(0, creator_philosophiae)


def reforge_result(roll: int, levels: Sequence[int], botched: bool = False) -> str:
    """Reforging a finished device: a Rego Vim Lab Total + stress die
    (`roll`) against each power's level, weakest first. At or above them
    all it is reforged; short of one, unchanged, or flawed (losing its
    strongest enchantment) when short by more than ten; a botch destroys
    it."""
    if botched:
        return DESTROYED
    for level in sorted(levels):
        if roll < level:
            return FLAWED if level - roll > 10 else UNCHANGED
    return REFORGED


def reforged(philosophiae: int) -> tuple[int, int, int]:
    """What a reforging takes and gives: (pawns of Vim vis, more pawns the
    device holds, the levels each power counts for at the next reforging),
    all from the reforger's Philosophiae."""
    return philosophiae, philosophiae, 5 * philosophiae


def reforge_opened_target(pawns_to_open: int) -> int:
    """Reforging a device opened but not yet enchanted: five times the
    pawns it took to open."""
    return 5 * pawns_to_open


def smelting_limit(magus: Character) -> int:
    """The most pawns smelting can draw from an item: Magic Theory x 2, or
    x Philosophiae with Elder Runes."""
    theory = _score(magus, "Magic Theory")
    if lab_virtues.has(magus, ELDER_RUNES):
        return theory * _score(magus, PHILOSOPHIAE)
    return theory * 2


def smelted(magus: Character, pawns: int) -> int:
    """The pawns smelting gives of the `pawns` used to instil an item's
    powers: one in ten is lost (at least one), and no more than the limit."""
    if pawns <= 0:
        return 0
    lost = max(1, round_up(pawns / 10))
    return max(0, min(smelting_limit(magus), pawns - lost))


# -- Automata (pp. 128-131) ----------------------------------------------------

CRAFT_AUTOMATA = "Craft Automata"
#: "Cease", the command that stops a power, adds 3 to its level; an
#: Ability instilled is base 25 for a score of 1, a magnitude per point
#: more; Tie the Threads that Bind must be at least the Might + 15.
CEASE_LEVELS = 3
ABILITY_POWER_BASE = 25
TIE_THE_THREADS_MARGIN = 15


def automaton_might(size: int, material_base_points: int) -> int:
    """An automaton's Magic Might (and Magic Resistance, the pawns that
    prepare it and the most it holds): 10 + Size + the material's base
    points."""
    return 10 + size + material_base_points


def construct_total(magus: Character, failed_seasons: int = 0) -> Breakdown:
    """Building the figure: Intelligence + Craft Automata (+ Philosophiae
    for a Verditius's runes) + a season's +1 for each failure, before the
    stress die, against the automaton's Might."""
    lines = [
        Line(
            "Intelligence",
            amount=magus.characteristics.intelligence,
            source=AUTOMATA_SOURCE,
        ),
        Line(
            CRAFT_AUTOMATA,
            amount=_score(magus, CRAFT_AUTOMATA),
            source=AUTOMATA_SOURCE,
        ),
    ]
    if is_verditius(magus) and _score(magus, PHILOSOPHIAE):
        lines.append(
            Line(
                "Verditius runes (Philosophiae)",
                amount=_score(magus, PHILOSOPHIAE),
                source=AUTOMATA_SOURCE,
            )
        )
    if failed_seasons > 0:
        lines.append(
            Line("Seasons failed", amount=failed_seasons, source=AUTOMATA_SOURCE)
        )
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def construct_cost(might: int, pawn_price: int, failed_seasons: int = 0) -> int:
    """The Mythic Pounds the figure costs: the price of a pawn of vis x its
    Might, and a pawn's price more for each attempt after a failure."""
    return pawn_price * (might + max(0, failed_seasons))


def ability_power_level(score: int) -> int:
    """The level of a power giving an automaton an Ability at `score`."""
    return ABILITY_POWER_BASE + 5 * max(0, score - 1)


def tie_the_threads_level(might: int) -> int:
    """The least level of the Tie the Threads that Bind that completes it."""
    return might + TIE_THE_THREADS_MARGIN


def maintenance(might: int, die: int, botches: int = 0) -> int:
    """The automaton's Might after the yearly stress die: unchanged at or
    above it, 1 less below it, 5 less for each botch."""
    if botches:
        return max(0, might - 5 * botches)
    return might if die >= might else max(0, might - 1)


def wear_penalty(original_might: int, might: int) -> int:
    """Its Ability rolls' penalty: -1 for every 2 points of Might lost."""
    return -(max(0, original_might - might) // 2)


def spot_repair_ease(original_might: int) -> int:
    """Intelligence + Craft Automata + stress die against 6 + the magnitude
    of its original Might; a success restores a point, in that many days."""
    return 6 + round_up(original_might / 5)


def season_repair_needed(might: int, powers: int) -> int:
    """The least Lab Total (Rego + its Form, Mentem requisite) that mends
    all its damage in a season: above Might + the powers instilled."""
    return might + powers + 1


# -- Item Attunement (p. 135) --------------------------------------------------


def sever_ease(capacity: int) -> int:
    """Severing the attuned item from its maker: his Perdo Vim Lab Total +
    a stress die against 10 + the pawns it holds."""
    return 10 + capacity


def covet_device(seasons_held: int, device_covet: int) -> int:
    """The bearer's Covet Device Personality Trait: an experience point a
    season, growing like an Ability, at most the device's own (its maker's
    Hubris at its creation)."""
    return min(device_covet, xp.score_from_xp(seasons_held, xp.ABILITY_FACTOR))


# -- Bind Magical Creatures (pp. 134-135) --------------------------------------

BINDING_SOURCE = f"{MC}, Bind Magical Creatures, pp. 134-135"
BIND_MAGICAL_CREATURES = "vf_bind_magical_creatures"


def binding_total(saga: Saga, magus: Character, laboratory: Laboratory) -> Breakdown:
    """The Rego Vim Lab Total + Hubris that drains or binds a magical
    creature (the creature's own Art is its requisite, the troupe's to
    apply: the lower of it and the total's Arts)."""
    total = lab.lab_total(saga, magus, "Rego", "Vim", laboratory)
    added: list[Line] = []
    hubris = hubris_of(magus)
    if hubris:
        added.append(Line(HUBRIS, amount=hubris, source=BINDING_SOURCE))
    return Breakdown(
        total=int(total.total) + sum(line.amount or 0 for line in added),
        lines=[*total.lines, *added],
    )


def drained_pawns(total: int, might: int) -> int:
    """The pawns drained from a creature to enchant with: a point of the
    total above its Might each, at most its Might."""
    return max(0, min(might, total - might))


def bind_power(total: int, might: int, penetration: int = 0) -> list[str]:
    """Binding one of a creature's powers to the Gift: what the total
    allows ([] if it falls short of twice the Might): fewer words or
    gestures at twice Might + 5 and + 10, Penetration at twice Might +
    it."""
    if total < 2 * might:
        return []
    allowed = ["The power is bound."]
    if total >= 2 * (might + 10):
        allowed.append("It needs neither words nor gestures.")
    elif total >= 2 * (might + 5):
        allowed.append("It needs words or gestures, not both.")
    if penetration and total >= 2 * (might + penetration):
        allowed.append(f"It has Penetration {penetration}.")
    return allowed


def bind_power_vis(might: int) -> int:
    """Pawns of the creature's Art's vis to bind a power: half its Might."""
    return round_up(might / 2)


# -- Bind Curse (pp. 131-133) ----------------------------------------------------

CURSE_SOURCE = f"{MC}, Bind Curse, pp. 131-133"
BIND_CURSE = "vf_bind_curse"
CURSE_BASE: dict[str, int] = {"Minor": 25, "Major": 50}
#: A trigger on a magical event adds 3; one after so many uses of another
#: power, 6.
CONDITIONAL_TRIGGER, COUNTED_TRIGGER = 3, 6


def curse_level(tier: str, magnitudes: int = 0, trigger: str = "") -> int:
    """A Curse's level: its base, + 5 a magnitude of Range or Target, + its
    trigger ("conditional" or "counted")."""
    level = CURSE_BASE[tier] + 5 * max(0, magnitudes)
    if trigger == "conditional":
        level += CONDITIONAL_TRIGGER
    elif trigger == "counted":
        level += COUNTED_TRIGGER
    return level


def curse_duration(tier: str, magic_theory: int) -> str:
    """How long a Curse lasts: its maker's Magic Theory, in seasons for a
    Minor one and years for a Major."""
    unit = "seasons" if tier == "Minor" else "years"
    return f"{magic_theory} {unit}"


# -- Forge-companions (HoH:MC pp. 113-114) ------------------------------------

FORGE_SOURCE = f"{MC}, Gauntleted Magus, pp. 113-114"
FORGE_COMPANION = "vf_forge_companion"
#: A forge-companion adds +1 to the Lab Total for every 5 points of the
#: Craft his master uses this season.
FORGE_CRAFT_STEP = 5


def forge_companion_lines(
    magus: Character, companions: Sequence[Character], craft: str
) -> tuple[list[Line], list[str]]:
    """The forge-companions' help on a Verditius's Lab Total: each adds +1
    per 5 points of `craft`, the Craft the magus uses this season (one
    without it adds nothing), and he may have as many as his Leadership (an
    apprentice is no forge-companion and doesn't count). The lines, and
    notes on what doesn't count."""
    lines: list[Line] = []
    notes: list[str] = []
    most = max(0, _score(magus, "Leadership"))
    if len(companions) > most:
        notes.append(
            f"{magus.name} may have {most} forge-companions (his Leadership); "
            f"only the first {most} help ({FORGE_SOURCE})."
        )
    for companion in companions[:most]:
        bonus = _score(companion, craft) // FORGE_CRAFT_STEP if craft else 0
        if not bonus:
            notes.append(
                f"{companion.name} adds nothing: a forge-companion helps with "
                f"{craft or 'the Craft his master uses'} at 5 or more."
            )
            continue
        lines.append(
            Line(
                f"{companion.name} (forge-companion)",
                amount=bonus,
                source=FORGE_SOURCE,
            )
        )
    return lines, notes


# -- Prices for enchantments (HoH:MC pp. 114-115) -----------------------------

PRICES_SOURCE = f"{MC}, Prices for Enchantments, pp. 114-115"
#: To another magus: twice the vis the item takes, besides that vis (the
#: Elder Runes example, p. 128: 18 pawns and the 9 it took, 27 in all).
PRICE_FACTOR = 2
#: To a mundane buyer: 15 Mythic Pounds for each pawn of the item's vis
#: cost, the Primus's fixed price (p. 114; p. 115 puts it as one and a half
#: times a "standard" saga's 10 Pounds a pawn; the Automata example,
#: p. 132: 22 pawns for 330 Pounds).
MUNDANE_POUNDS_PER_PAWN = 15


def device_vis(saga: Saga, device: EnchantedDevice) -> int:
    """The pawns making the device took: what opening it cost (less its
    Verditius maker's Craft, at least one) and every effect's vis, elder
    runes' included; a charged item takes none."""
    if device.type == CHARGED:
        return 0
    opened = device.pawns_opened if device.type == INVESTED else 0
    maker = maker_of(saga, device)
    if opened and device.verditius_runes and maker is not None and is_verditius(maker):
        opened = max(1, opened - _score(maker, device.verditius_craft or FINESSE))
    return opened + enchantment.pawns_used(device)


def house_fee(vis: int) -> int:
    """The pawns the House charges a magus for the work, besides the vis
    the item takes."""
    return PRICE_FACTOR * max(0, vis)


def mundane_price(vis: int) -> int:
    """The Mythic Pounds the House asks of a mundane buyer for an item
    whose vis cost is `vis` pawns."""
    return MUNDANE_POUNDS_PER_PAWN * max(0, vis)


def sale_hubris_xp(device: EnchantedDevice) -> int:
    """The Hubris experience selling the device (or making it for another,
    for pay) brings its maker: 1 for a charged or lesser one, 3 for a
    greater, 6 for an attuned item, a magnitude of Might for an automaton
    (its Might typed as its Capacity; DE p. 242)."""
    if device.verditius_item == enchantment.AUTOMATON:
        return hubris_xp(AUTOMATON, round_up((device.capacity_override or 0) / 5))
    if device.verditius_item == enchantment.ATTUNED:
        return HUBRIS_XP["Selling (or making for another) an attuned item"]
    if device.type == INVESTED:
        return HUBRIS_XP["Selling (or making for another) a greater enchanted device"]
    if device.type == CHARGED:
        return HUBRIS_XP[
            "Selling (or making for pay) a charged item or an item of quality"
        ]
    return HUBRIS_XP["Selling (or making for another) a lesser enchanted device"]


def price_lines(saga: Saga, device: EnchantedDevice) -> list[str]:
    """The House's price for a device a Verditius crafted, and the Hubris
    experience selling it brings (plain text)."""
    vis = device_vis(saga, device)
    xp_text = f"selling it brings its maker {sale_hubris_xp(device)} Hubris experience"
    if not vis:
        return [
            "House price: it takes no vis, so the price to a magus is twice the "
            "vis its maker could have extracted in the seasons it took (work it "
            "out from his Vim extraction Lab Total); to a mundane buyer, "
            f"{MUNDANE_POUNDS_PER_PAWN} Mythic Pounds a pawn of that vis; "
            f"{xp_text} ({PRICES_SOURCE})."
        ]
    fee = house_fee(vis)
    line = (
        f"House price: {fee} pawns besides the {vis} it takes ({fee + vis} in "
        f"all) to a magus; {mundane_price(vis)} Mythic Pounds to a mundane buyer"
    )
    if device.verditius_item == enchantment.AUTOMATON:
        line += ", with its construction"
    return [f"{line}; {xp_text} ({PRICES_SOURCE})."]


# -- Hubris as it grows (HoH:MC pp. 115, 119-121; DE pp. 241-242) -------------

VENDETTA_SOURCE = f"{MC}, Vendettas, pp. 115-116; Hubris, p. 120; DE p. 242"
#: Refusing a vendetta: the House Reputation, and a point of Hubris lost.
DISHONORABLE = ("Dishonorable", 4)
HOUSE_REACH = "House Verditius"


def hubris_trait(magus: Character) -> ScoredTrait | None:
    return next((t for t in magus.personality_traits if t.name == HUBRIS), None)


def xp_to_next_hubris(magus: Character) -> int:
    """The experience Hubris needs for its next point (the Increased Hubris
    Ordeal gives just that, p. 121): 5 x the next score, less what is
    already toward it."""
    trait = hubris_trait(magus)
    score = trait.score if trait else 0
    return xp.ABILITY_FACTOR * (score + 1) - (trait.deeds if trait else 0)


def gain_hubris(magus: Character, experience: int, start: int = 0) -> str:
    """Add Hubris experience (kept toward the next point, as an Ability
    grows), making the trait at `start` first when he has none and `start`
    is given (the first Inner Mystery's). What it did, as a line."""
    trait = hubris_trait(magus)
    if trait is None:
        if not start:
            return ""
        trait = ScoredTrait(HUBRIS, start)
        magus.personality_traits.append(trait)
    before = trait.score
    confidence.add_deeds(trait, experience)
    if trait.score == before:
        return (
            f"Hubris {trait.score}: +{experience} experience "
            f"({trait.deeds} toward the next point)."
        )
    return f"Hubris {before} -> {trait.score} (+{experience} experience)."


def apply_hubris(
    magus: Character, start: int, experience: int, rises: int
) -> list[str]:
    """An Initiation's Hubris kept on the sheet: the trait made at `start`
    (the first Inner Mystery's), its `experience` (1 or 3 for learning an
    Inner Mystery), then enough for one more point for each Increased
    Hubris Ordeal (p. 121), and any refused vendetta it makes good. What
    it did, as lines."""
    said: list[str] = []
    if start and hubris_trait(magus) is None:
        said.append(gain_hubris(magus, 0, start))
    if experience and hubris_trait(magus) is not None:
        said.append(gain_hubris(magus, experience))
    for _ in range(max(0, rises)):
        if hubris_trait(magus) is None:
            magus.personality_traits.append(ScoredTrait(HUBRIS, 0))
        said.append(gain_hubris(magus, xp_to_next_hubris(magus)))
    said += settle_vendettas(magus)
    return [line for line in said if line]


def refuse_vendetta(magus: Character, refused: str = "") -> list[str]:
    """Refusing a vendetta `refused` declared: the House Reputation
    Dishonorable 4, and enough experience lost to lower Hubris by one point
    (to the experience of the score below, Hubris building as an Ability,
    p. 119). The refusal is kept until he regains the score and wages a
    vendetta on the magus refused, which loses the Reputation (p. 115)."""
    said: list[str] = []
    trait = hubris_trait(magus)
    before = trait.score if trait is not None else 0
    if trait is not None and trait.score > 0:
        trait.score -= 1
        trait.deeds = 0
        said.append(f"Hubris falls to {trait.score}.")
    magus.refused_vendettas.append(RefusedVendetta(refused.strip(), before))
    name, score = DISHONORABLE
    held = next((r for r in magus.reputations if r.name == name), None)
    if held is None:
        magus.reputations.append(
            ScoredTrait(name, score, type="Hermetic", reach=HOUSE_REACH)
        )
    else:
        held.score = max(held.score, score)
    said.append(f"Reputation {name} {score} in {HOUSE_REACH} ({VENDETTA_SOURCE}).")
    return said


def refusal_lines(magus: Character) -> list[str]:
    """What each refused vendetta still needs before the Reputation goes:
    the Hubris score to regain, and the vendetta to wage."""
    own = hubris_of(magus)
    lines: list[str] = []
    for refusal in magus.refused_vendettas:
        needs: list[str] = []
        if own < refusal.hubris:
            needs.append(f"Hubris back to {refusal.hubris} (now {own})")
        if not refusal.waged:
            needs.append("a vendetta waged on him")
        who = refusal.magus or "the magus refused"
        lines.append(f"Refused {who}: needs {' and '.join(needs) or 'nothing'}.")
    return lines


def wage_refused_vendetta(magus: Character, refused: str) -> list[str]:
    """Waging a vendetta on a magus he once refused: kept on the refusal,
    then whatever it makes good settled (p. 115)."""
    refusal = next(
        (r for r in magus.refused_vendettas if r.magus == refused and not r.waged),
        None,
    )
    if refusal is None:
        raise LookupError(f"{magus.name} has no refused vendetta with {refused!r}.")
    refusal.waged = True
    return [
        f"Wages a vendetta on {refused or 'the magus refused'}.",
        *settle_vendettas(magus),
    ]


def settle_vendettas(magus: Character) -> list[str]:
    """Drop each refusal made good (the Hubris score regained and the
    vendetta waged); with none left, the Reputation Dishonorable goes
    (p. 115). What it did, as lines."""
    own = hubris_of(magus)
    left = [r for r in magus.refused_vendettas if not (r.waged and own >= r.hubris)]
    if len(left) == len(magus.refused_vendettas):
        return []
    magus.refused_vendettas = left
    if left:
        return ["A refused vendetta made good; others remain."]
    name, _ = DISHONORABLE
    magus.reputations = [
        r for r in magus.reputations if not (r.name == name and r.reach == HOUSE_REACH)
    ]
    return [f"Reputation {name} lost in {HOUSE_REACH} ({VENDETTA_SOURCE})."]


def vendetta_ease(own_hubris: int, challenger_hubris: int) -> int:
    """Resisting a declared vendetta: the Ease Factor is both magi's Hubris."""
    return max(0, own_hubris) + max(0, challenger_hubris)


def resist_vendetta(
    rng: random.Random,
    resisting: int,
    own_hubris: int,
    challenger_hubris: int,
    saga: Saga | None = None,
) -> tuple[bool, str]:
    """A Personality Trait set against Hubris (or Intelligence, without
    one) + a stress die against both magi's Hubris: whether the maga
    resists, and the roll as a line."""
    die = dice.stress_die(rng, 1, saga=saga)
    total = resisting + die.value
    ease = vendetta_ease(own_hubris, challenger_hubris)
    held = not die.botched and total >= ease
    rolled = "botched" if die.botched else str(total)
    return held, (
        f"Resisting the vendetta: {rolled} against {ease}: "
        + ("resisted." if held else "drawn into it.")
    )


# -- Confraternities (HoH:MC pp. 121-123) --------------------------------------

CONFRATERNITY_SOURCE = f"{MC}, Confraternities, pp. 121-123"


@dataclass(frozen=True)
class Confraternity:
    """A confraternity: its Crafts, the Mystery (and Flaw) it Initiates its
    members into, and its path through the House's Mysteries."""

    name: str
    crafts: tuple[str, ...]
    mystery: str
    flaw: str
    path: tuple[str, ...]


CONFRATERNITIES: tuple[Confraternity, ...] = (
    Confraternity(
        "Roland",
        ("Blacksmith",),
        "Minor Magical Focus (Swords)",
        "",
        (
            "Minor Magical Focus (Swords)",
            "Reforging Enchanted Items",
            "Items of Quality",
            "Verditius Elder Runes",
            "Item Attunement",
        ),
    ),
    Confraternity(
        "Balento",
        ("Woodcarver",),
        "Affinity with Ignem",
        "Deficient Form (Aquam)",
        (
            "Affinity with Ignem",
            "Enchant Casting Tools",
            "Verditius Elder Runes",
            "Bind Magical Creatures",
        ),
    ),
    Confraternity(
        "Irene",
        ("Sculptor", "Painter"),
        "Puissant Imaginem or Puissant Mentem",
        "Slow Caster",
        ("Puissant Imaginem or Puissant Mentem", "Verditius Elder Runes", "Automata"),
    ),
    Confraternity(
        "Himinis",
        (),
        "Minor Magical Focus (Wooden Wands)",
        "Envious",
        (
            "Minor Magical Focus (Wooden Wands)",
            "Verditius Elder Runes",
            "Item Attunement",
            "Bind Curse",
        ),
    ),
)


def confraternity_of(script_name: str) -> Confraternity | None:
    """The confraternity whose Script `script_name` is ("Confraternity of
    Roland: ...")."""
    return next(
        (
            c
            for c in CONFRATERNITIES
            if script_name.startswith(f"Confraternity of {c.name}")
        ),
        None,
    )


def confraternity_note(script_name: str) -> str:
    """What a confraternity's Script adds to the season's note: the
    Mystery and Flaw it Initiates its members into, its Crafts and its
    path."""
    found = confraternity_of(script_name)
    if found is None:
        return ""
    flaw = f" with the Flaw {found.flaw}" if found.flaw else ""
    crafts = (
        f"; its members have Craft: {' or '.join(found.crafts)}" if found.crafts else ""
    )
    return (
        f"The Confraternity of {found.name} Initiates its members into "
        f"{found.mystery}{flaw}{crafts}; its path after the Outer Mystery: "
        f"{', '.join(found.path)} ({CONFRATERNITY_SOURCE})."
    )
