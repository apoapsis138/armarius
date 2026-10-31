"""Magi of Hermes, chapters six to ten: Julia Textrix of Ex Miscellanea,
Lambert of Merinita, Maris of Tytalus, Marcus Tauros of Criamon and
Persephone of Tytalus, with Tetrix and Kore in their blocks' notes.

Each magus has one table of Abilities (a score for each printing, None
where the printing lacks it) and a list of spells that grows by printing,
so what changes between ages can be read off in one place. A spell's
casting total is the app's to work out, so it is not kept; experience
printed past a score has no place in a block and goes in its notes.

Ariadne's Thread, which the book gives Marcus, is left out as the errata
(page 12) deletes it."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ..builder import (
    StatBlock,
    arts_from,
    characteristics,
    joined_lines,
    paragraphs,
    vf_art,
    vf_puissant,
)
from . import Magus, Printing

N = None

SpellRow = tuple[str, str, int]


def _abilities(table: Sequence[tuple[Any, ...]], column: int) -> list[Any]:
    """A printing's Abilities from a table of (name, specialty, score at
    each printing), leaving out those it lacks."""
    return [
        (row[0], row[column + 2], row[1])
        for row in table
        if row[column + 2] is not None
    ]


def _spells(rows: Sequence[SpellRow], masteries: Mapping[str, str]) -> StatBlock:
    """The "spells" and "masteries" of a block; every spell these magi
    master, they master to 1 in a single Mastery Ability."""
    return {
        "spells": [
            (name, arts, level, 1 if name in masteries else 0)
            for name, arts, level in rows
        ],
        "masteries": {
            name: [masteries[name]] for name, _, _ in rows if name in masteries
        },
    }


def _spell_notes(rows: Sequence[SpellRow], rules: Mapping[str, str]) -> str:
    """The rules of the new spells among `rows`, one to a line."""
    return joined_lines(
        *(f"{name}: {rules[name]}" for name, _, _ in rows if name in rules)
    )


# ---------------------------------------------------------------- Julia

JULIA_ABILITIES: tuple[tuple[Any, ...], ...] = (
    ("Artes Liberales", "grammar", 2, 2, 2, 2),
    ("Awareness", "faerie trickery", 1, 1, 2, 2),
    ("Bargain", "prices", N, N, 1, 1),
    ("Craft: Linen", "clothes", 3, 4, 4, 4),
    ("Craft: Wool", "felt", 1, 4, 4, 5),
    ("Concentration", "Herbam", 1, 2, 2, 2),
    ("Faerie Lore", "spiders", 1, 1, 3, 3),
    ("Finesse", "craft magic", 3, 4, 5, 6),
    ("Folk Ken", "craftsmen", 2, 2, 2, 2),
    ("Dead Language: Latin", "Hermetic", 4, 4, 4, 4),
    ("Magic Theory", "craft magic", 4, 5, 6, 6),
    ("Living Language: Low German", "Flemish", 5, 5, 5, 5),
    ("Parma Magica", "faerie powers", 1, 2, 3, 4),
    ("Penetration", "Animal", 1, 2, 2, 3),
    ("Profession: Dyer", "reds", 1, 2, 2, 2),
    ("Second Sight", "faerie glamour", 2, 2, 3, 3),
    ("Teaching", "crafts", N, N, N, 3),
)

JULIA_VIRTUES: list[Any] = [
    "The Gift",
    "Hermetic Magus",
    "Craft Magic",
    ("Strong Faerie Blood", {"blood": "Spinnen"}),
    vf_art("Affinity with {art}", "Rego"),
    "Enduring Magic",
    "Harnessed Magic",
    ("Lesser Immunity", {"hazard": "poison"}),
    ("Minor Magical Focus", {"focus": "clothing"}),
    vf_puissant("Finesse"),
    "Second Sight",
    "Side Effect",
    "Spell Foci",
]
JULIA_FLAWS: list[Any] = [
    "Difficult Longevity Ritual",
    "Meddler (Major)",
    "Supernatural Nuisance",
    "Weak Spontaneous Magic",
    ("Fear", {"detail": "spiders"}),
]

JULIA_SPELLS_0: tuple[SpellRow, ...] = (
    ("Doublet of Impenetrable Silk", "MuAn", 15),
    ("Decay Fur and Hide", "PeAn", 10),
    ("Circle of Beast Warding", "ReAn", 5),
    ("Cloak of the Duck's Feathers", "ReAq", 5),
    ("Bind Wound", "CrCo", 10),
    ("Conjure the Sturdy Vine", "CrHe", 5),
    ("Trap of the Entwining Vines", "CrHe", 15),
    ("Piercing Shaft of Wood", "MuHe(Re)", 10),
    ("Curse of the Rotted Wood", "PeHe", 5),
    ("Ward Against the Faeries of the Wood", "ReHe", 20),
    ("Unseen Porter", "ReTe", 10),
    ("Unraveling the Fabric of Herbam", "PeVi", 10),
)
JULIA_SPELLS_15 = (
    *JULIA_SPELLS_0,
    ("Madder, Woad, and Weld", "MuAn(He)", 20),
    ("The Unraveled Seam", "PeAn(He)", 5),
    ("The Wizard's Spindle", "ReAn", 4),
    ("Dressing the Human Form in Wool", "ReAn", 5),
    ("Ward Against Faeries Which Creep and Crawl", "ReAn", 20),
    ("Sealing the Lips", "MuCo", 10),
    ("Clothe the Naked Form", "CrHe", 10),
    ("The Clothier's Craft Done in an Instant", "ReHe", 4),
    ("The Mended Tear", "ReHe", 5),
)
JULIA_SPELLS_30 = (
    *JULIA_SPELLS_15,
    ("Shearing the Unseen Sheep", "CrAn", 20),
    ("The Unraveled Clothes", "PeAn(He)", 15),
    ("Weaver's Trap of Threads", "CrHe", 20),
    ("Tangle of Wood and Thorns", "ReHe", 15),
    ("The Animate Attire", "ReHe", 20),
)
JULIA_SPELLS_45 = (
    *JULIA_SPELLS_30,
    ("Sturdy Mantle of the Traveler", "CrAn", 30),
    ("Cloak of Nessus", "MuAn", 35),
    ("Constraint of the Strangling Vestments", "ReAn", 35),
    ("The Travelers' Fortress of Cloth", "CrHe", 20),
    ("Embroidering the Wizard's Robes", "ReHe", 20),
)
JULIA_MASTERIES = {
    "Doublet of Impenetrable Silk": "Fast Casting",
    "Ward Against Faeries Which Creep and Crawl": "Penetration",
}

JULIA_RULES = {
    "Madder, Woad, and Weld": (
        "Touch, Month, Group. Dyes up to ten skeins of wool or five bolts of "
        "wool, cotton or linen any single hue chosen at casting; the cloth "
        "goes back to undyed when the spell ends. (Base 1, +1 Touch, +3 "
        "Month, +2 Group, +1 requisite)"
    ),
    "The Unraveled Seam": (
        "Touch, Momentary, Part. Rots a thread of animal or plant origin so "
        "that the cloth it holds parts; it can be sewn again, so the garment "
        "counts as damaged, not destroyed. (Base 2, +1 Touch, +1 Part, +1 "
        "requisite)"
    ),
    "The Wizard's Spindle": (
        "Touch, Momentary, Group. Cleans, cards and spins up to ten fleeces "
        "in a round; Finesse Ease Factor 12, or the wool is a useless "
        "tangle. (Base 1, +1 Touch, +2 Group)"
    ),
    "Dressing the Human Form in Wool": (
        "Touch, Momentary, Individual; the spell lists printed level 15, which "
        "the errata corrects to 5. Makes one woollen garment from fleece (Finesse "
        "Ease Factor 12) or spun wool (9); finer work raises it, failure "
        "leaves a mess, and a new colour needs dye. Her usual way of "
        "tailoring her magical cloth. Uses the level 3 Rego Animal guideline "
        "from Covenants page 50. (Base 2, +1 Touch, +1 complexity)"
    ),
    "Ward Against Faeries Which Creep and Crawl": (
        "Touch, Ring, Circle. Keeps out faerie animals of Might up to the "
        "spell's level. She casts it nightly with Circle of Beast Warding, "
        "sweeping the ground first so no spider is shut in with her."
    ),
    "Sealing the Lips": (
        "Voice, Sun, Individual; the new-spells section makes it ReCo, the "
        "spell lists MuCo. The target cannot speak, and looks to have his "
        "lips stitched, though that is only for show. (Base 2, +2 Voice, +2 "
        "Sun)"
    ),
    "Clothe the Naked Form": (
        "Touch, Sun, Individual. Creates one garment of linen or cotton, "
        "mostly underclothes; Finesse Ease Factor 6 for standard quality, 9 "
        "to choose the dye's brightness and regional style. For when she has "
        "no cloth by her. (Base 1, +1 Touch, +2 Sun, +2 treated and "
        "processed)"
    ),
    "The Clothier's Craft Done in an Instant": (
        "Touch, Momentary, Individual. Forms linen or cotton cloth into a "
        "garment; Finesse Ease Factor 9 for standard quality, as a day's "
        "work done at once, or the cloth is scraps. Working from raw fibre "
        "would need the level 5 guideline (Covenants page 51), which her "
        "Faerie Blood makes needless. (Base 3, +1 Touch)"
    ),
    "The Mended Tear": (
        "Touch, Momentary, Part. A thread laid over a rent stitches it "
        "neatly; Finesse Ease Factor 6. (Base 3, +1 Touch, +1 Part)"
    ),
    "Shearing the Unseen Sheep": (
        "Touch, Sun, Individual. Creates a fleece, the raw stuff she then "
        "turns into clothing by Rego craft magic. (Base 5, +1 Touch, +2 Sun)"
    ),
    "The Unraveled Clothes": (
        "Voice, Momentary, Group. All stitches of thread or leather come "
        "undone and the victim is left naked; leather armour falls apart, "
        "and metal armour loses its padding, giving -3 to physical actions "
        "and half Protection until replaced. The clothes can be repaired. "
        "(Base 2, +2 Voice, +2 Group, +1 requisite)"
    ),
    "Weaver's Trap of Threads": (
        "Voice, Sun, Group. A net of thick thread fills 5 paces by 5 by 6 "
        "feet, or hangs as a wall from supports; Strength stress roll Ease "
        "Factor 9 to get free, or an outsider with a blade takes three "
        "rounds. Fire is very effective but burns those caught; the net is "
        "not sticky. Her loathing of spiders made this a weaker answer to "
        "Weaver's Trap of Webs. (Base 2, +2 Voice, +2 Sun, +2 Group)"
    ),
    "The Animate Attire": (
        "Voice, Concentration, Individual. One garment writhes at the "
        "caster's direction: -3 to all actions and 3 extra botch dice. Best "
        "on linen underclothes. (Base 5, +2 Voice, +1 Conc)"
    ),
    "Sturdy Mantle of the Traveler": (
        "Touch, Sun, Individual. Creates a gardcorps of supple oiled "
        "leather; Finesse Ease Factor 6 for a waterproof robe of standard "
        "quality, 9 to choose its colour and regional style. (Base 5, +1 "
        "Touch, +2 Sun, +2 treated and processed)"
    ),
    "Cloak of Nessus": (
        "Voice, Diameter, Part. A garment partly turns to poison: Stamina "
        "Ease Factor 9 each round in contact or a Light Wound. Two "
        "magnitudes come from the poison's strength, with no Aquam requisite "
        "as it is of animal origin. (Base 5, +2 Voice, +1 Diam, +1 Part, +2 "
        "poison)"
    ),
    "Constraint of the Strangling Vestments": (
        "Voice, Diameter, Group. Clothes of wool, leather and fur pin the "
        "wearer and choke him: a Deprivation roll (ArM5 pages 180-181) every "
        "30 seconds, or 5 combat rounds. Reasons from the Rego Herbam "
        "guidelines. (Base 10, +2 Voice, +1 Diam, +2 Group)"
    ),
    "The Travelers' Fortress of Cloth": (
        "Touch, Sun, Group. A canvas tent for ten rises from the vegetation; "
        "Finesse Ease Factor 6 or it leaks and smells musty, 9 for a superior "
        "pavilion. (Base 1, +1 Touch, +2 Sun, +2 Group, +2 treated and "
        "finished)"
    ),
    "Embroidering the Wizard's Robes": (
        "Touch, Momentary, Individual. Thread follows her finger into the "
        "cloth; Finesse Ease Factor 9 for simple designs, 12 for intricate, "
        "or a tangle to unpick. She often signs her work with it. (Base 15, "
        "+1 Touch)"
    ),
}

JULIA_LOOK = (
    "A plain, dumpy woman, hunched from the loom, her hands forever stained "
    "with dye. Wiry black hair sparsely covers her whole body, and her "
    "irises are as black as her pupils, which unsettles people."
)
JULIA_DRESS_YOUNG = (
    "She wears a craftswoman's plain browns, with a rich blue kerchief "
    "tying back her hair."
)
JULIA_DRESS_OLD = (
    "With her trade grown, she dresses well to suit her clients, in fabrics "
    "of her own invention and dyes of her own recipes, to show off her wares."
)
JULIA_SIGIL = (
    "Casting sigil: a thread-like weave. Voting sigil: an embroidered swatch of cloth."
)
JULIA_MAGIC = (
    "Her Side Effect makes every spell fade slowly instead of ending: hardly "
    "noticeable at Momentary or Diameter, about an hour at Sun, a day at "
    "Moon or Year. Enduring Magic stretches this too, so a spell that has "
    "lasted four Moons takes four days to fade. Rego craft magic is in "
    "Covenants page 49, Craft Magic in Houses of Hermes: Societates pages "
    "131-132. Her Faerie Blood turns her own body weight of raw fibre into "
    "cloth each day."
)
JULIA_COMBAT = "Combat: dodge Init 0, Defense 0. Soak +2. Encumbrance 0."
JULIA_COMBAT_BONDED = (
    "Combat: dodge Init 0, Defense 0. Soak +4, with the Bronze Cord. Encumbrance 0."
)
JULIA_TETRIX = paragraphs(
    "Familiar: Tetrix the Blackcock, a male black grouse with black plumage, "
    "red wattles, white wing-bars and a lyre-shaped tail, about four feet "
    "tall when upright. She chose him for the pun of textrix on tetrix, and "
    "found a fierce hunter of spiders. Magic Might 12 (Animal), Summer. Int "
    "-3, Per +2, Pre -1, Com -2, Str -3, Sta +3, Dex 0, Qik +2. Size -2. "
    "Confidence 1 (3). Virtues and Flaws: Magic Animal; Gossip, Student of "
    "Faerie; True Friend (familiar bond); Clumsy, Non-Combatant. Magical "
    "Qualities: Greater Power, No Fatigue; Gift of Speech, Improved "
    "Abilities (twice), Improved Defense, Improved Soak. Qualities: "
    "Camouflage, Ambush Predator, Hardy. Traits: Brave +3, Loyal to Julia "
    "+3, Inquisitive +1, Grouse (essential) +3. Beak Init +2, Attack +7, "
    "Defense +7, Damage -2; dodge Init +5, Defense +7. Soak +7, with the "
    "Bronze Cord. Wounds -1 (1-3), -3 (4-6), -5 (7-9), Incapacitated "
    "(10-12), Dead (13+). Abilities: Athletics 3 (flying), Awareness 4 "
    "(food), Brawl 4 (dodging), Faerie Lore 3 (faerie animals), Hunt 4 "
    "(spiders), Low German 3 (Flemish), Magic Theory 2 (enchantment), Music "
    "2 (grouse-songs), Penetration 2 (Stand Your Ground), Stealth 4 "
    "(stalking insects), Survival 5 (moorland). Vis: 3 pawns, in feathers. "
    "He gets +3 to Stealth when still, and +3 to Attack in the first round "
    "against insects unaware of him.",
    "Tetrix's powers. No Fatigue (0 points, constant): no Fatigue levels, "
    "no sleep, no unconsciousness. Stand Your Ground (2 points, Init +4, "
    "Corpus or Animal): rearing up freezes a person or animal while he "
    "confronts her, or for another point until he leaves her presence "
    "(ReCo(An) 20; Base 5, +1 Eye, +1 Conc, +1 requisite; Greater Power "
    "gives 30 levels, +4 Init, +10 Penetration).",
    "Familiar bond, Rego Animal Lab Total 38: Gold Cord +2, Silver Cord +1, "
    "Bronze Cord +2. Snap of Awakening (ReMe 7, Pen 0, 3/day, Touch, "
    "Momentary, Individual): Tetrix wakes her at once, and as he never "
    "sleeps he always keeps watch (Base 4, +1 Touch; +2 3/day). Silent "
    "Speech (CrMe 15, Pen 0, unlimited, Touch, Momentary, Individual): two "
    "effects letting them share words, images and emotions each way (Base "
    "4, +1 Touch; +10 unlimited). He was made by the rules of Realms of "
    "Power: Magic, chapter 4.",
)
JULIA_LOOM = (
    "Loom of the Kabouters: a beautiful vertical loom all of carved elm, "
    "without a metal part, its only other pieces removable stone weights. "
    "Named for the small Flemish urban faeries. Opened with ten pawns of Vim "
    "vis; six spaces are free. Loom of Elfin Proportions (MuHe 23, Pen 0, "
    "6/day, Personal, Concentration, Individual): shrinks it to a tenth in "
    "each dimension, from six feet to seven inches, and she keeps it in a "
    "box in that state; built on Object of Increased Size with a magnitude "
    "more (Base 4, +1 Conc, +1 size, +1 complexity; +5 maintains, +3 6/day). "
    "Panorama of the Heinzelmannchen (ReAn 10, Pen 0, 1/day, Touch, "
    "Momentary, Group): weaves wool into a described tapestry up to one "
    "hundred square paces, very quickly, Finesse Ease Factor 12 for a simple "
    "scene and more for complex ones (Base 1, +1 Touch, +2 Group, +1 size, "
    "+1 intricacy)."
)
JULIA_SHEARS_FIRST = (
    "Talisman, Forfex Princeps: clothier's shears two feet long, of iron "
    "inlaid with gold, copper and lead filigree, opened with ten pawns of "
    "Vim vis. Attunements: +2 shaping fabric (shears), +7 harm or repel "
    "faeries (iron), +4 deftness (copper), +4 wards (lead). Sever Wood and "
    "Bone (PeAn(He) 12, Pen 0, 3/day, Touch, Momentary, Individual): cuts "
    "any animal or plant stuff the blades close on, mostly bone or wood "
    "(Base 4, +1 Touch, +1 requisite; +2 3/day)."
)
JULIA_SHEARS_LATER = (
    "The talisman also holds, and now has no space left: Snip the Thread of "
    "a Faerie's Might (PeVi 25, Pen 20, 24/day, Voice, Momentary, "
    "Individual), which on penetrating costs a faerie 10 Might (Base 0, +2 "
    "Voice; +10 Pen 30, +5 24/day). Gather the Connection (ReCo(An) 30, Pen "
    "10, 1/day, Voice, Momentary, Individual): snips a lock of hair to her "
    "hand, noticed on Perception + Awareness Ease Factor 9; useful for "
    "Arcane Connections but risky if the target is a magus, and needing no "
    "Perdo requisite as it copies cutting hair (Base 15, +2 Voice; +5 Pen "
    "10). Sunder Stone (PeTe 12, Pen 0, 3/day, Touch, Momentary, "
    "Individual): cuts any metal, glass or stone the blades close on (Base "
    "3, +1 Touch, +2 metal; +2 3/day)."
)
JULIA_BROOCH = (
    "The Fruit of the Loom: a plain brooch of twisted copper wire in a warp "
    "and weft pattern under a cast copper apple, opened with five pawns of "
    "Vim vis, three in use. The Everchanging Garments (MuAn(He) 28, Pen 0, "
    "6/day, Touch, Concentration, Group): remakes the clothes it is pinned "
    "to, animal stuffs staying animal and plant staying plant, keeping "
    "their dye; Finesse Ease Factor 6 for a simple change, higher for great "
    "improvements; lasts until cancelled, with brief concentration at "
    "sunrise or sunset (Base 3, +1 Touch, +1 Conc, +2 Group, +1 requisite; "
    "+5 maintains, +3 6/day)."
)
JULIA_CLOTH = (
    "Magical cloth: she makes these charged items by Craft Magic, using her "
    "Casting Total, in days rather than a season, one sheet a day with "
    "usually one charge a sheet, and one effect only to a piece. She "
    "triggers them once the cloth is a garment, and Enduring Magic often "
    "lengthens them. For example, a Casting Total of 23 gives four sheets "
    "of the first below in four days. Iridescence of the Mallard's Head "
    "(MuIm 4, Personal, Month, Individual): dull green cloth turns "
    "iridescent, then reverts (Base 1, +3 Month). Staunch the Bloody Wound "
    "(CrCo 10, Touch, Month, Individual): bandages give +3 to Wound Recovery "
    "(Base 2, +1 Touch, +3 Month). Scintillation of the Phoenix (CrIg 10, "
    "Personal, Month, Individual): orange-yellow cloth glows and flickers "
    "like torchlight, liked by Flambeau for Tribunal robes (Base 3, +3 "
    "Month). Constrain the Shrewish Wife (MuMe 15, Touch, Moon, Individual): "
    "the wearer grows considerate of loved ones (Base 3, +1 Touch, +3 Moon). "
    "Curb the Straying Husband (MuMe 15, Touch, Moon, Individual): the "
    "wearer grows temperate, shunning drink, violence and philandering "
    "(Base 3, +1 Touch, +3 Moon). Cloth of Unicorn Hair (level 20, Touch, "
    "Sun, Individual): immunity to poison, a work of Craft Magic and so "
    "rolled as Dexterity + Craft, not cast; made rarely, and not truly of "
    "unicorn hair whatever she tells clients (Base 5, +1 Touch, +2 Sun). All "
    "are Pen 0."
)


def _julia(column: int, arts: str, age: int, notes: str, **extra: Any) -> Printing:
    rows = (JULIA_SPELLS_0, JULIA_SPELLS_15, JULIA_SPELLS_30, JULIA_SPELLS_45)[column]
    bonded = column >= 2
    block: StatBlock = {
        "characteristics": characteristics(1, -2, 0, 0, 0, 2, 3, 0),
        "confidence": (1, 3),
        "virtues_flaws": [
            *JULIA_VIRTUES,
            *([("True Friend", {"detail": "Tetrix"})] if bonded else []),
            *JULIA_FLAWS,
        ],
        "traits": {
            "Busybody": 3,
            **({"Loyal to Tetrix": 3} if bonded else {}),
            "Industrious": 2,
            "Brave": -2,
        },
        "abilities": _abilities(JULIA_ABILITIES, column),
        "arts": arts_from(arts),
        **_spells(rows, JULIA_MASTERIES),
        "notes": paragraphs(notes, _spell_notes(rows, JULIA_RULES)),
        **extra,
    }
    label = ("Gauntlet", "+15", "+30", "+45")[column]
    return Printing(label, age, block)


JULIA = Magus(
    name="Julia of Ex Miscellanea",
    house="house_ex_miscellanea",
    summary=paragraphs(
        "A weaver of the Rusticani tradition (Houses of Hermes: Societates "
        "pages 130-133), who joins mundane craft to magic. She was born at "
        "Florum in the Normandy Tribunal (The Lion and the Lily page 96), of "
        "the de Spinnen family, whose blood comes from a faerie spider. "
        "Meeting that ancestor as a child left her terrified of him and of "
        "all spiders, so she would not train at Florum and was apprenticed "
        "to an associate of the covenant who taught her magical weaving.",
        "A loner with no covenant, she sells her magical cloth to the rich: "
        "colours and effects no dye can give. She sells mostly through a "
        "middleman who cheats her badly, which she accepts because it keeps "
        "Quaesitores from looking at her. As the cloth's charges fade the "
        "customers return. Barred from society by her Gift, she follows it "
        "keenly through her vendor's gossip, and sometimes weaves impulses "
        "into fabric meant to better its wearer's life.",
        "The spider prince resents being rejected and regularly sends his "
        "many-legged servants to torment her.",
    ),
    printings=(
        _julia(
            0,
            "Cr 7, In 3, Mu 4, Pe 3, Re 9, An 5, Aq 1, Au 1, Co 2, He 7, Ig 1, "
            "Im 2, Me 1, Te 1, Vi 3",
            26,
            paragraphs(
                f"{JULIA_LOOK} {JULIA_DRESS_YOUNG}",
                JULIA_SIGIL,
                JULIA_COMBAT,
                JULIA_MAGIC,
                JULIA_CLOTH,
            ),
            apparent_age=26,
        ),
        _julia(
            1,
            "Cr 8, In 4, Mu 7, Pe 3, Re 14, An 10, Aq 2, Au 1, Co 5, He 10, "
            "Ig 1, Im 3, Me 5, Te 5, Vi 6",
            41,
            paragraphs(
                f"{JULIA_LOOK} {JULIA_DRESS_OLD}",
                JULIA_SIGIL,
                "Twilight scars: her arms are permanently dyed blue; loose "
                "fibres braid or knot themselves near her.",
                JULIA_COMBAT,
                "Last 15 years: invented 93 levels of spells and made no "
                "magical items, as Craft Magic copies simple effects in "
                "days; 197 xp in Arts and 160 in Abilities.",
                JULIA_MAGIC,
                JULIA_CLOTH,
            ),
            apparent_age=41,
            warping=(2, 13),
        ),
        _julia(
            2,
            "Cr 8, In 4, Mu 10, Pe 5, Re 15, An 12, Aq 3, Au 3, Co 8, He 10, "
            "Ig 4, Im 5, Me 7, Te 5, Vi 8",
            56,
            paragraphs(
                f"{JULIA_LOOK} {JULIA_DRESS_OLD}",
                JULIA_SIGIL,
                "Twilight scars: her arms are permanently dyed blue; loose "
                "fibres braid or knot themselves near her; she has a "
                "constant musky smell.",
                JULIA_COMBAT_BONDED,
                "Last 15 years: invented 90 levels of spells; found and "
                "bonded Tetrix and enchanted Snap of Awakening (2 seasons); "
                "made her paltry Longevity Ritual (1 season), an embroidered "
                "pouch at her neck, -4 to Aging rolls with an extra pawn of "
                "vis; opened the Loom and instilled both effects (4 "
                "seasons); made and attuned the shears and instilled Sever "
                "Wood and Bone (3 seasons). She began training an apprentice "
                "who helped with these (2 seasons). 145 xp in Arts and 125 "
                "in Abilities. She has 1 xp past her Vim score.",
                JULIA_MAGIC,
                JULIA_TETRIX,
                JULIA_SHEARS_FIRST,
                JULIA_LOOM,
                JULIA_CLOTH,
            ),
            apparent_age=50,
            warping=(3, 15),
        ),
        _julia(
            3,
            "Cr 9, In 6, Mu 10, Pe 5, Re 17, An 13, Aq 5, Au 5, Co 8, He 11, "
            "Ig 5, Im 5, Me 7, Te 8, Vi 8",
            71,
            paragraphs(
                f"{JULIA_LOOK} {JULIA_DRESS_OLD}",
                JULIA_SIGIL,
                "Twilight scars: her arms are permanently dyed blue; loose "
                "fibres braid or knot themselves near her; she has a "
                "constant musky smell; her canine teeth have grown long and "
                "glossy black; she can change the colour of her eyes by "
                "concentrating.",
                JULIA_COMBAT_BONDED,
                "Last 15 years: invented 5 spells in 10 seasons, her Arts "
                "now being high enough for the seasonal method; 13 seasons "
                "teaching her apprentice; two more effects in the familiar "
                "bond (2 seasons); three more in her talisman (4 seasons); "
                "two seasons on the brooch Fruit of the Loom. 110 xp in Arts "
                "and 120 in Abilities. She has 1 xp past her Vim score.",
                JULIA_MAGIC,
                JULIA_TETRIX,
                f"{JULIA_SHEARS_FIRST} {JULIA_SHEARS_LATER}",
                JULIA_LOOM,
                JULIA_BROOCH,
                JULIA_CLOTH,
            ),
            aging_points={"perception": 1, "dexterity": 1},
            apparent_age=57,
            decrepitude=(0, 2),
            warping=(5, 10),
        ),
    ),
)


# -------------------------------------------------------------- Lambert

LAMBERT_ABILITIES: tuple[tuple[Any, ...], ...] = (
    ("Area Lore: Brittany", "geography", 2, 2, 2, 2),
    ("Area Lore: Normandy", "politics", 2, 2, 2, 2),
    ("Artes Liberales", "arithmetic", 2, 2, 2, 2),
    ("Bargain", "with faeries", 2, 4, 5, 5),
    ("Carouse", "games of chance", 2, 2, 2, 2),
    ("Charm", "first impressions", 2, 2, 2, 2),
    ("Dominion Lore", "Divine creatures", N, N, 1, 1),
    ("Etiquette", "church", 2, 2, 2, 2),
    ("Faerie Lore", "bargaining with faeries", 3, 3, 3, 3),
    ("Faerie Magic", "Charm creation", N, 2, 3, 3),
    ("Folk Ken", "townsfolk", 2, 2, 2, 2),
    ("Living Language: French", "Lorain", 5, 5, 5, 5),
    ("Guile", "fast talk", 2, 2, 2, 2),
    ("Infernal Lore", "demons", N, N, 1, 1),
    ("Intrigue", "rumor mongering", 2, 2, 2, 2),
    ("Dead Language: Latin", "Hermetic use", 5, 5, 5, 5),
    ("Leadership", "inspiration", 2, 2, 2, 2),
    ("Living Language: Low German", "Flemish", 2, 2, 2, 2),
    ("Magic Lore", "creatures", N, N, 1, 1),
    ("Magic Theory", "inventing spells", 4, 5, 6, 5),
    ("Organization Lore: House Merinita", "Wayfarers", N, 1, 2, 2),
    ("Living Language: Occitan", "Provencal", 2, 2, 2, 2),
    ("Organization Lore: Order of Hermes", "politics", 1, 1, 1, 1),
    ("Parma Magica", "Mentem", 1, 4, 4, 4),
    ("Philosophiae", "ritual magic", 2, 2, 2, 2),
    ("Profession: Merchant", "commodity speculation", 2, 2, 2, 2),
    ("Profession: Storyteller", "faerie tales", N, 3, 3, 3),
    ("Ride", "speed", 2, 2, 2, 2),
    ("Teaching", "merchants", N, N, 2, 2),
)

LAMBERT_START: list[Any] = [
    "The Gift",
    "Hermetic Magus",
    vf_art("Affinity with {art}", "Mentem"),
]
LAMBERT_SHARED: list[Any] = [
    ("Faerie Blood", {"blood": "Sidhe"}),
    "Faerie Magic",
    vf_art("Puissant {art}", "Mentem"),
    "Self-Confident",
    "Skilled Parens",
]
LAMBERT_INCOMPATIBLE = (
    "Incompatible Arts",
    {"arts": "Rego Imaginem and Rego Mentem"},
)
LAMBERT_COMPULSION = ("Compulsion (Minor)", {"detail": "haggling and negotiation"})
LAMBERT_VF_0: list[Any] = [
    *LAMBERT_START,
    *LAMBERT_SHARED,
    ("Social Contacts", {"group": "family business connections"}),
    "Quiet Magic",
    "Dependent",
    "Busybody",
    LAMBERT_COMPULSION,
    LAMBERT_INCOMPATIBLE,
    "Unimaginative Learner",
]
LAMBERT_VF_LATER: list[Any] = [
    *LAMBERT_START,
    "Arcadian Travel",
    *LAMBERT_SHARED,
    "Social Contacts",
    "Quiet Magic",
    ("Enemies", {"detail": "faerie merchants"}),
    "Busybody",
    LAMBERT_COMPULSION,
    ("Fear", {"detail": "swine"}),
    LAMBERT_INCOMPATIBLE,
    "Unimaginative Learner",
    "Weak Magic",
]

LAMBERT_SPELLS_0: tuple[SpellRow, ...] = (
    ("Soothing Voice of the Stableman", "ReAn", 15),
    ("Patch of Drought", "PeAq", 10),
    ("Frosty Breath of the Spoken Lie", "InMe", 20),
    ("Posing the Silent Question", "InMe", 20),
    ("Tread of Fellow Travelers", "InMe", 30),
    ("Blissful Messenger", "MuMe", 30),
    ("Calm Mind of Resolute Behavior", "PeMe", 20),
    ("Unseen Arm", "ReTe", 5),
)
LAMBERT_SPELLS_15 = (
    *LAMBERT_SPELLS_0,
    ("The Inexorable Search", "InCo", 20),
    ("Pull of Blood", "InCo", 20),
    ("Scent of Loose Purses", "InMe", 30),
    ("Stench of Hate", "InMe", 30),
    ("Piercing the Faerie Veil", "InVi", 20),
)
LAMBERT_SPELLS_30 = (
    *LAMBERT_SPELLS_15,
    ("Memory of the Distant Dream", "CrMe", 20),
    ("Thoughts Within Babble", "InMe", 25),
    ("Familial Secrets", "InMe", 35),
    ("Opinions of the Masses", "InMe", 35),
    ("Oath Breaker's Confession", "InMe", 40),
    ("Confusion of the Numbed Will", "PeMe", 15),
    ("Loss of But a Moment's Memory", "PeMe", 15),
    ("Mind Cleansed of Treachery", "PeMe", 45),
)
LAMBERT_SPELLS_45 = (
    *LAMBERT_SPELLS_30,
    ("Opening the Tome of the Animal's Mind", "InAn", 25),
    ("Intuition of the Forest", "InHe", 10),
    ("Converse with Plant and Tree", "InHe", 25),
    ("Family Gathering", "MuMe(In)", 45),
    ("Missive of Memory", "CrMe", 40),
    ("Blindness of Involuntary Obstinacy", "PeMe", 40),
    ("Wrappings of Metaphysical Iron", "ReVi", 20),
)

LAMBERT_RULES = {
    "Soothing Voice of the Stableman": (
        "Voice, Sun, Individual. Plants in an animal's mind that the caster "
        "is a safe friend. It cannot lift the unease of The Gift, but a "
        "beast cannot tie that unease to the caster; mounts stay skittish, "
        "with Ease Factors 3 higher and extra botch dice where mood matters, "
        "and the Blatant Gift sends them into a frenzy. Animals Warped by it "
        "turn belligerent and frightened. (Base 2, +2 Voice, +2 Sun, +1 size)"
    ),
    "Patch of Drought": (
        "Voice, Momentary, Individual. Destroys the water in a puddle or "
        "patch of mud up to 20 paces across, speeding carts on wet roads. "
        "(Base 4, +2 Voice)"
    ),
    "Pull of Blood": (
        "Touch, Momentary, Bloodline, Faerie. Gives the direction and "
        "distance of each living descendant of the target; he uses it on "
        "himself to keep track of his family. (Base 4, +1 Touch, +3 "
        "Bloodline)"
    ),
    "Missive of Memory": (
        "Arcane Connection, Moon, Individual. Creates a whole memory that "
        "lasts until the spell ends; what the target dwelt on he may still "
        "recall, and it can be detected as false on Intelligence Ease Factor "
        "9. Long or detailed memories take the magus as long to prepare as "
        "they last. He writes to distant associates this way, though not to "
        "magi, using impossible recent memories to catch their notice. Made "
        "not to Warp his second daughter. (Base 5, +4 Arcane Connection, +3 "
        "Moon)"
    ),
    "Blissful Messenger": (
        "Touch, Until, Individual, Faerie, Ritual. Replaces memory of an "
        "event with memory of another; it ends when the target speaks of it "
        "to a chosen person, who must figure in the altered memory. A Tytalus "
        "maga arranged for him to learn it as an apprentice to serve her "
        "agents. Vis and distrust of the Gifted keep it rare. (Base 5, +1 "
        "Touch, +4 Until)"
    ),
    "Scent of Loose Purses": (
        "Touch, Sun, Smell. The target smells desire and interest in minds "
        "nearby, stronger as they are stronger. Lambert uses it to train his "
        "family and staff to read people, pairing them to learn the cues "
        "without magic. (Base 5, +1 Touch, +2 Sun, +2 Smell)"
    ),
    "Stench of Hate": (
        "Touch, Sun, Smell. As Scent of Loose Purses, for antipathy, dislike "
        "and hate. (Base 5, +1 Touch, +2 Sun, +2 Smell)"
    ),
    "Tread of Fellow Travelers": (
        "Road, Diameter, Group, Faerie. Gives the number, consciousness, "
        "direction and distance of the nearest group of minds on his road, "
        "one way. Merinitae use such spells to sense targets for other "
        "Road-range magic, which the law of Arcane Connections otherwise "
        "bars. (Base 5, +2 Road, +1 Diameter, +2 Group)"
    ),
    "Familial Secrets": (
        "Touch, Momentary, Bloodline, Faerie (level and Range by the errata). He learns what each "
        "descendant believes the answer to a question to be, as Posing the "
        "Silent Question, with no Arcane Connection. To tell whose answer is "
        "whose, Perception + Awareness Ease Factor 3 + number of descendants, "
        "more if some are unfamiliar. Made not to Warp his bloodline. (Base "
        "15, +1 Touch, +3 Bloodline)"
    ),
    "Oath Breaker's Confession": (
        "Eye, Bargain and Momentary, Individual, Faerie. The new-spells "
        "section gives level 35, the spell lists 40. Cast on striking a "
        "bargain; if the target breaks it within a year he knows at once, "
        "and why and how she thinks she broke it. (Base 15, +1 Eye, +3 "
        "Momentary and Bargain)"
    ),
    "Opinions of the Masses": (
        "Personal, Concentration, Hearing. Each mind met answers a chosen "
        "question in a voice he hears, clear if it has dwelt on the matter, "
        "whispering if not, silent if it never has or resists; he has heard "
        "spirits and unseen creatures so. Crowds raise Ease Factors for "
        "listening. (Base 15, +1 Conc, +3 Hearing)"
    ),
    "Family Gathering": (
        "Touch, Concentration, Bloodline, Faerie (level and Range by the "
        "errata). The spell list prints Cr(In)Me, the new-spells section "
        "Mu(In)Me, which is kept here. He and his descendants "
        "seem to sit together round a table in a large room marked by his "
        "sigil, and can speak; the asleep dream it and remember it as a "
        "dream. They perceive nothing around them while it lasts, though "
        "they can still move, which is dangerous. Replaced a taxing use of "
        "Familial Secrets with a spontaneous Words of the Unbroken Silence. "
        "Made not to Warp his bloodline. (Base 15, +1 Touch, +1 Conc, +3 "
        "Bloodline, +1 requisite)"
    ),
    "Calm Mind of Resolute Behavior": (
        "Personal, Diameter, Individual. Banishes all emotion: appeals to "
        "feeling fail and no Personality Trait rolls can be made, though "
        "goals and memories stay. His mater thought it vital for dealing "
        "with faeries; he uses it to weigh large choices, dislikes it, and "
        "fears botching Perdo Mentem on himself. (Base 15, +1 Diameter)"
    ),
    "Blindness of Involuntary Obstinacy": (
        "Sight, Concentration, Group. The targets cannot perceive a chosen "
        "thing or person: the senses work but the common sense will not "
        "take it in. He often names himself. (Base 10, +3 Sight, +1 Conc, +2 "
        "Group)"
    ),
    "Mind Cleansed of Treachery": (
        "Eye, Bargain and Momentary, Individual, Faerie. Cast on striking a "
        "bargain; if the target breaks it within a year his memory is "
        "destroyed, losing all ideas, identity, and every Academic, Arcane, "
        "Martial and Supernatural Ability and Art. General Abilities stay, "
        "as do remembered faces and places, without meaning. Traded from a "
        "Merinita for the Lab Text of Oath Breaker's Confession. (Base 25, "
        "+1 Eye, +3 Momentary and Bargain)"
    ),
    "Wrappings of Metaphysical Iron": (
        "Touch, Sun, Individual; level as the guideline, written Gen. Wards "
        "an object from faeries and faerie magic up to the spell's level, "
        "if it penetrates. From notes of a Merinita with Spell Potency, so "
        "he must wrap an iron chain around the item at casting, for a "
        "Potency Bonus of +7. Faeries mind it on goods he brings, but hate "
        "it on things native to their home. (Base effect, no modifier Ring "
        "to Sun)"
    ),
}

LAMBERT_LOOK = (
    "Tall, thin and dark-haired, with a solemn look that makes him seem "
    "sadder than he acts, he usually dresses as a successful merchant. His "
    "easy smile is plainly practised, but its warmth goes a good way to "
    "offset The Gift."
)
LAMBERT_LOOK_LATER = LAMBERT_LOOK.replace(
    "dark-haired,", "dark-haired, greying at the temples,"
)
LAMBERT_SIGIL = (
    "Casting sigil: coins, worked subtly into what he makes, and clinking "
    "in the footsteps of creatures he enchants. Voting sigil: a wooden dowel "
    "carved as a caduceus, which he likes to turn into talk of Mercury's "
    "tie to trade."
)
LAMBERT_COMBAT = (
    "Combat: fist Init -1, Attack -1, Defense -1, Damage 0; dodge Init -1, "
    "Defense -1. Soak +1. Encumbrance 0."
)
LAMBERT_ARCADIA = (
    "Arcadian Travel: initiated through the Wayfarers by the script on page "
    "80 of Houses of Hermes: Mystery Cults. His Ordeal took him from Bayeux "
    "cathedral to a faerie regio in the forested hills of Bayeux County, "
    "pursued by faerie boars; it gave him the Virtue and Fear (swine), and "
    "the cathedral is a permanent Arcane Connection to him. He makes charms "
    "with Profession: Storyteller, writing sections of his stories on paper "
    "as the charm's objects."
)
LAMBERT_TABLET = (
    "Casting tablet of Locked Storehouse (Covenants page 89), a spell he "
    "does not know: MuHe(Te) 45, Touch, Year +1, Structure, Ritual, Faerie. "
    "It turns a building and contents into a buried rock of hard igneous "
    "stone of about the same mass, for a year and a day; animal stuffs need "
    "an Animal requisite or the spell fails. The contents age but do not "
    "otherwise decay. The tablet calls for three pawns of Muto vis and six "
    "of Terram. (Base 4, +1 Touch, +4 Year+1, +3 Structure, +1 complexity)"
)
LAMBERT_COINS = (
    "Coins of Loose-Tongued Patrons: two silver coins with a crown on one "
    "side and Mercere on the other, each a lesser enchanted device of three "
    "pawns, got by trade and often held by his family, who value the honest "
    "feedback (though much use could Warp them). Blessing of Enthusiastic "
    "Patrons, on the Coin of Enthusiastic Patrons (Mercere laughing), and "
    "Curse of Petulant Customers, on the Coin of Petulant Customers (Mercere "
    "grimacing): ReMe 25, Pen 0, 1/day, Touch, Sun, Room; touched to a "
    "wall, they make those inside dwell on merchandise's good points (-6 to "
    "purchasers' Bargain rolls) or its faults (+6) (Base 10, +1 Touch, +2 "
    "Room)."
)
LAMBERT_DOORFRAME = (
    "Doorframe of the Wary Steward: he made this invested device to pay for "
    "the Coins and never keeps one, but has its Lab Texts to sell. Maple "
    "and hazel, built into a covenant, with a small bell on a nail in a "
    "hollow at the top; opened with eight pawns, four in use. Its power "
    "(InMe 35, Pen 0, Special, Momentary, Individual) shakes the frame and "
    "rings the bell if a creature passing believes it means the residents "
    "harm; animals are unaffected, and the Limit of the Infernal applies "
    "(Base 15, +1 Touch equivalent, +1 non-standard range, +10 unlimited)."
)
LAMBERT_CHEST = (
    "Granary Chest: a large oak chest with simple brass fittings, two and a "
    "half feet by a foot and a half by a foot and a half, invested with "
    "eight pawns for the wood. Convenient Warehouse (MuHe 34, Pen 0, "
    "constant, Touch, Day, Room): plant matter wholly inside shrinks to "
    "a grain of wheat until taken out; long storage can Warp it, and his "
    "family keeps things in bags coloured by contents to find them (Base 3, "
    "+2 Day, +2 Room, +2 excessive size, with Touch by the errata; +1 twice a day, +3 environmental). "
    "Carpentry of Brass (MuHe(Te) 10, Pen 0, 1/day, Personal, Sun, "
    "Individual): rapped seven times, the wood turns to brass (Base 4, +2 "
    "Sun). Charm Versus Dampness (ReAq 14, Pen 0, constant, Touch, Sun, "
    "Room): slowly moves liquids out and stops seepage, though not pouring "
    "(Base 1, +1 Touch, +2 Sun, +2 Room; +1 2/day, +3 environmental)."
)
LAMBERT_TOKEN = (
    "Token of the Harvest Evening: a lesser device, a small wooden "
    "hourglass the size of a chess piece, inlaid with sulfur, usually kept "
    "in the Granary Chest. Freshness of the Harvest Evening (CrHe 14, Pen "
    "0, constant, Touch, Day, Room): plant matter in the room does not rot "
    "while both stay, though long keeping Warps it (Base 1, +1 Touch, +2 "
    "Sun, +2 Room; +1 two a day, +3 environmental)."
)


def _lambert(
    column: int,
    age: int,
    arts: str,
    reckless: int,
    notes: str,
    **extra: Any,
) -> Printing:
    rows = (
        LAMBERT_SPELLS_0,
        LAMBERT_SPELLS_15,
        LAMBERT_SPELLS_30,
        LAMBERT_SPELLS_45,
    )[column]
    block: StatBlock = {
        "confidence": (2, 5),
        "virtues_flaws": LAMBERT_VF_LATER if column else LAMBERT_VF_0,
        "traits": {"Assiduous": 2, "Brave": -1, "Reckless": reckless},
        "abilities": _abilities(LAMBERT_ABILITIES, column),
        "arts": arts_from(arts),
        **_spells(rows, {}),
        "notes": paragraphs(notes, _spell_notes(rows, LAMBERT_RULES)),
        **extra,
    }
    label = ("Gauntlet", "+15", "+30", "+45")[column]
    return Printing(label, age, block)


LAMBERT = Magus(
    name="Lambert of Merinita",
    house="house_merinita",
    summary=paragraphs(
        "Born to a merchant family, Lambert loved haggling from childhood, "
        "but his Gift undid his charm and enthusiasm. He stayed close to "
        "his family all through his apprenticeship, marrying and fathering "
        "children before it ended, and providing for them has shaped his "
        "life. The family buys goods and carries them to where they sell at "
        "a profit; his magic finds the best buys and moves them safely and "
        "fast. His magic centres on Mentem, Faerie Magic and the family's "
        "trade.",
        "He must haggle whenever he can, with mixed results. Mortals and "
        "faeries who deal with him often suspect they were cheated without "
        "knowing why, but magi are shielded from his Gift, so striking "
        "deals with the Order delights him.",
        "As he ages he hands the face-to-face trade to his children, for "
        "fear of the charge of interfering with mundanes, and takes his "
        "bargaining to the fay in faerie auras and regiones, which earns him "
        "the enmity of a powerful group of faerie merchants. By his last "
        "printing he lives among children, grandchildren and "
        "great-grandchildren, his passion given to studying faeries.",
    ),
    printings=(
        _lambert(
            0,
            31,
            "Cr 1, In 5, Mu 5, Pe 3, Re 4, An 4, Aq 2, Au 0, Co 0, He 0, Ig 0, "
            "Im 0, Me 11+3, Te 0, Vi 0",
            -3,
            paragraphs(
                LAMBERT_LOOK,
                LAMBERT_SIGIL,
                LAMBERT_COMBAT,
                "No vis, no equipment. Fresh from apprenticeship, he divides "
                "his time between merchant adventuring and being an "
                "itinerant magus, often using the generous hospitality of "
                "the Rhine Tribunal, and much of it goes to providing for "
                "his wife and children. He has 1 xp past his Aquam score.",
            ),
            characteristics=characteristics(1, 1, 3, 2, 0, 1, -1, -1),
            apparent_age=31,
        ),
        _lambert(
            1,
            46,
            "Cr 6, In 8, Mu 5, Pe 4, Re 4, An 7, Aq 4, Au 0, Co 5, He 0, Ig 0, "
            "Im 6, Me 18+3, Te 0, Vi 6",
            -1,
            paragraphs(
                LAMBERT_LOOK_LATER,
                LAMBERT_SIGIL,
                LAMBERT_COMBAT,
                "Vis: 5 pawns of Herbam, as berries whose smell draws horses.",
                "Last 15 years: his children can fend for themselves and he "
                "has some grandchildren. One season each on Piercing the "
                "Faerie Veil and The Inexorable Search, from Lab Texts; "
                "three on Pull of Blood, with unusual schedules and "
                "experimentation; four on Scent of Loose Purses; three on "
                "Stench of Hate; one copying Lab Texts to pay for his "
                "casting tablet; three serving House Merinita and the "
                "Wayfarers for his Initiation. 135 xp in Abilities and 195 "
                "in Arts, with 39 more from his Affinity. He has 3 xp past "
                "his Intellego score and 11 past Mentem.",
                LAMBERT_ARCADIA,
                LAMBERT_TABLET,
            ),
            characteristics=characteristics(1, 1, 3, 2, 0, 1, -1, -2),
            aging_points={"presence": 1, "quickness": 1},
            apparent_age=46,
            decrepitude=(0, 3),
            warping=(3, 0),
            reputations={
                "Compulsive dealmaker (Tribunal)": 1,
                "Dangerous Bargainer (local faeries)": 2,
            },
        ),
        _lambert(
            2,
            61,
            "Cr 6, In 12, Mu 5, Pe 6, Re 7, An 7, Aq 5, Au 5, Co 6, He 5, Ig 5, "
            "Im 6, Me 22+3, Te 5, Vi 6",
            1,
            paragraphs(
                LAMBERT_LOOK_LATER,
                LAMBERT_SIGIL,
                LAMBERT_COMBAT,
                "Vis: 4 pawns of Herbam in a wooden ring; 5 of Intellego in "
                "bottles of water from a reflecting pool, which keeps the "
                "moon's reflection wherever it goes.",
                "Last 15 years: he runs the family business and spends much "
                "time with his grandchildren. At 47 he got a longevity "
                "ritual from a fellow magus in a deal costing two seasons, "
                "one assisting and one paying with his influence and wealth. "
                "One season upgraded his laboratory with the Highly "
                "Organized Virtue and an orb as a lesser feature (Covenants "
                "chapter 9). One season each inventing Memory of the "
                "Distant Dream, Confusion of the Numbed Will and Loss of But "
                "a Moment's Memory; two each on Familial Secrets (with help in the lab, by the errata), Oath "
                "Breaker's Confession and Opinions of the Masses; one each "
                "learning Mind Cleansed of Treachery and Thoughts Within "
                "Babble from Lab Texts; three on the Doorframe; three "
                "wholly with family. 110 xp in Abilities and 190 in Arts, "
                "with 25 more in Mentem from his Affinity. He has 2 xp past "
                "his Corpus score and 13 past Mentem.",
                LAMBERT_ARCADIA,
                LAMBERT_TABLET,
                LAMBERT_COINS,
                LAMBERT_DOORFRAME,
            ),
            characteristics=characteristics(1, 1, 3, 2, 0, 1, -1, -2),
            aging_points={"presence": 1, "communication": 1},
            apparent_age=47,
            decrepitude=(0, 3),
            warping=(4, 10),
            reputations={
                "Overly Concerned with Mundanes (Quaesitors)": 1,
                "Compulsive dealmaker (Tribunal)": 1,
                "Dangerous Bargainer (local faeries)": 2,
            },
        ),
        _lambert(
            3,
            76,
            "Cr 10, In 12, Mu 12, Pe 10, Re 11, An 7, Aq 5, Au 5, Co 6, He 13, "
            "Ig 5, Im 6, Me 25+3, Te 5, Vi 7",
            2,
            paragraphs(
                LAMBERT_LOOK_LATER,
                LAMBERT_SIGIL,
                "Twilight scar: those near him do not lose focus from "
                "tiredness and cannot nod off unintentionally.",
                LAMBERT_COMBAT,
                "Vis: 2 pawns of Herbam in a wooden ring; 6 of Intellego in "
                "small reflective coins; 4 of Mentem as bottles of "
                "faerie-made wine.",
                "Last 15 years: no longer active in the business, he gives "
                "himself to faeries and regiones, losing two seasons "
                "exploring them. Five seasons on Blindness of Involuntary "
                "Obstinacy; four each on Family Gathering (with help in the lab, by the errata) and Missive of "
                "Memory; one each on Converse with Plant and Tree, Opening "
                "the Tome of the Animal's Mind and Wrappings of Metaphysical "
                "Iron from Lab Texts; one opening the Granary Chest, two on "
                "Convenient Warehouse, one on Carpentry of Brass, one on "
                "Charm Versus Dampness; one on the Token of the Harvest "
                "Evening. 270 xp in Arts, with 23 more in Mentem from his "
                "Affinity. He has 2 xp past his Corpus score and 10 past "
                "Mentem.",
                "He also owns the Ring of the Cold Iron Mind, which the book "
                "lists but does not describe.",
                LAMBERT_ARCADIA,
                LAMBERT_TABLET,
                LAMBERT_COINS,
                LAMBERT_DOORFRAME,
                LAMBERT_CHEST,
                LAMBERT_TOKEN,
            ),
            characteristics=characteristics(1, 1, 3, 2, 0, 1, -1, -2),
            aging_points={"presence": 1},
            apparent_age=49,
            decrepitude=(0, 3),
            warping=(5, 15),
            reputations={
                "Overly Concerned with Mundanes (Quaesitors)": 1,
                "Compulsive dealmaker (Tribunal)": 1,
                "Dangerous Bargainer (local faeries)": 2,
                "Skilled in Mentem (Tribunal)": 2,
            },
        ),
    ),
)


# ---------------------------------------------------------------- Maris

MARIS_ABILITIES: tuple[tuple[Any, ...], ...] = (
    ("Area Lore: Scandinavia", "Baltic Sea", 1, 1, 2, 2, 2),
    ("Artes Liberales", "astronomy", 2, 2, 2, 2, 2),
    ("Athletics", "climbing", 1, 1, 2, 2, 2),
    ("Awareness", "notice", 1, 1, 2, 2, 3),
    ("Chirurgy", "first aid", 1, 1, 1, 1, 1),
    ("Code of Hermes", "technicalities", 1, 1, 1, 1, 1),
    ("Concentration", "spell concentration", 2, 2, 2, 3, 3),
    ("Etiquette", "Hermetic", 1, 1, 1, 1, 1),
    ("Finesse", "precision", 2, 2, 4, 3, 3),
    ("Fishing", "trap fishing", 2, 2, 2, 2, 3),
    ("Great Weapon", "harpoon", 1, 1, 2, 2, 2),
    ("Dead Language: Latin", "writing", 4, 4, 4, 4, 4),
    ("Magic Lore", "creatures", 1, 1, 2, 2, 2),
    ("Magic Theory", "enchanting items", 4, 4, 5, 6, 6),
    ("Navigation", "sea", 1, 1, 2, 2, 2),
    ("Living Language: Norse", "nautical terms", 5, 5, 5, 5, 5),
    ("Organization Lore: Order of Hermes", "history", 1, 1, 1, 1, 1),
    ("Organization Lore: Order of Odin", "history", 1, 1, 1, 1, 1),
    ("Parma Magica", "Aquam", 2, 2, 2, 2, 2),
    ("Penetration", "Rego", 2, 2, 2, 2, 3),
    ("Philosophiae", "natural", 1, 1, 2, 1, 2),
    ("Profession: Sailor", "storms", 2, 2, 2, 3, 3),
    ("Survival", "winter", 2, 2, 2, 3, 3),
    ("Swim", "diving", 2, 2, 2, 2, 3),
    ("Organization Lore: House Tytalus", "philosophies", 1, 1, 1, 1, 1),
)

MARIS_VF: list[Any] = [
    "The Gift",
    "Hermetic Magus",
    "Flawless Magic",
    vf_art("Affinity with {art}", "Creo"),
    vf_art("Affinity with {art}", "Rego"),
    "Arcane Lore",
    "Cautious Sorcerer",
    "Free Study",
    "Self-Confident",
    "Skilled Parens",
    "Study Bonus",
    "Plagued by Supernatural Entity",
    "Weak Spontaneous Magic",
    ("Cyclic Magic (Negative)", {"cycle": "during low tide"}),
    ("Fear", {"detail": "Twilight"}),
    ("Infamous", {"detail": "mad"}),
    ("Vow (Minor)", {"detail": "Independence"}),
]

MARIS_SPELLS_0: tuple[SpellRow, ...] = (
    ("Soothe the Ferocious Bear", "ReAn", 10),
    ("Eyes of the Cat", "MuCo(An)", 5),
    ("Comfort the Drenched Caster", "PeAq", 5),
    ("Cloak of the Duck's Feathers", "ReAq", 5),
    ("Air's Ghostly Form", "CrAu", 5),
    ("Wind at the Back", "ReAu", 5),
    ("Bind Wound", "CrCo", 10),
    ("In Christ's Footsteps", "ReCo", 5),
    ("Conjure the Sturdy Vine", "CrHe", 5),
    ("Probe Nature's Hidden Lore", "InHe", 4),
    ("Hunt for the Wild Herb", "InHe", 5),
    ("Palm of Flame", "CrIg", 5),
    ("Repel Winter's Clutches", "CrIg", 5),
    ("Lamp Without Flame", "CrIg", 10),
    ("Prying Eyes", "InIm", 5),
    ("Taste of the Spices and Herbs", "MuIm", 5),
    ("Eyes of the Eons", "InTe", 10),
    ("Supple Iron and Rigid Rope", "MuTe", 10),
    ("The Invisible Glass Worker", "ReTe", 4),
    ("The Unseen Porter", "ReTe", 10),
    ("Sense of Magical Power", "InVi", 2),
    ("Scales of the Magical Weight", "InVi", 5),
    ("Sense the Nature of Vis", "InVi", 5),
)
MARIS_SPELLS_15 = (*MARIS_SPELLS_0, ("Physician's Eye", "InCo", 5))
MARIS_SPELLS_45 = (
    *(s for s in MARIS_SPELLS_0 if s[0] != "Bind Wound"),
    ("Securing the Harvest", "ReAn", 4),
    ("Sense the Tide's Boundaries", "InAq", 25),
    ("Grow the Bountiful Feast", "CrHe", 4),
    ("Plant the Bountiful Feast", "CrHe", 20),
    ("Form the Hermetic Boundary", "CrTe", 25),
)
MARIS_SPELLS_60 = (
    *MARIS_SPELLS_45,
    ("Bind Wound", "CrCo", 10),
    ("Captured by Höðr's Shackles", "ReAq", 20),
    ("Swallowed by the Mist", "ReAu", 20),
)
#: Every spell Maris knows he has mastered to 1: in Quiet Casting but these.
MARIS_MASTERIES = {
    "Cloak of the Duck's Feathers": "Silent Casting",
    "Air's Ghostly Form": "Fast Casting",
    "Wind at the Back": "Multiple Casting",
    "Bind Wound": "Multiple Casting",
    "In Christ's Footsteps": "Fast Casting",
    "Conjure the Sturdy Vine": "Multiple Casting",
    "The Invisible Glass Worker": "Multiple Casting",
    "Physician's Eye": "Fast Casting",
    "Swallowed by the Mist": "Fast Casting",
}

MARIS_RULES = {
    "Securing the Harvest": (
        "Touch, Ring, Circle. Keeps mundane pests from food growing inside "
        "the circle; if it is bypassed, he knows something more interesting "
        "than vermin has called. (Base 1, +1 Touch, +2 Ring)"
    ),
    "Sense the Tide's Boundaries": (
        "Touch, Sun, Individual. Like Eyes of the Bat, sensing displaced "
        "water, so it works in depths where no light reaches. (Base 4, +1 "
        "Touch, +2 Sun, +2 Size)"
    ),
    "Captured by Höðr's Shackles": (
        "Sight, Momentary, Part (Range and Duration by the errata). Encases a submerged target in thick ice, without "
        "creating any, as the water must already surround it. He floats "
        "valuables up with it; against a foe it suffocates and does +3 "
        "damage a round from cold. (Base 3, +3 Sight, +1 Part, +1 size)"
    ),
    "Swallowed by the Mist": (
        "Voice, Momentary, Part. The spell lists it as ReAu, the new-spells "
        "section as ReAq. A section of water turns to mist: swimmers and "
        "ships drop to the bottom and the sea crashes in over them. "
        "Perception + Finesse Ease Factor 9 to aim, 6 for a target smaller "
        "than a rowboat. Onlookers see a cloud, and the ship gone. (Base 3, "
        "+2 Voice, +1 Part, +2 Size)"
    ),
    "Grow the Bountiful Feast": (
        "Touch, Ring, Circle. Plants inside mature at the normal pace but "
        "crop as richly and finely as they can. (Base 1, +1 Touch, +2 Ring)"
    ),
    "Plant the Bountiful Feast": (
        "Touch, Momentary, Group, Ritual. Creates mature food plants that "
        "still need time to crop; his version makes Irish moss. (Base 1, +1 "
        "Touch, +2 Group, +1 Size, ritual)"
    ),
    "Repel Winter's Clutches": (
        "Touch, Concentration, Individual. Warms the target from within, to "
        "defrost a thing or save a freezing person; +5 to Medicine rolls "
        "for hypothermia. (Base 3, +1 Touch, +1 Conc)"
    ),
    "Form the Hermetic Boundary": (
        "Touch, Moon, Individual. Raises a level stone circle nine paces "
        "across, a foot high and some inches thick; he bases his underwater "
        "gardens on these. (Base 3, +1 Touch, +3 Moon, +2 Size)"
    ),
}

MARIS_LOOK = (
    "A gruff, weathered man of Nordic stock, kept practical, with uncut "
    "hair and often a month or more of beard."
)
MARIS_LOOK_SEA = (
    "Long dives leave him smelling of salt and the sea, with seaweed and "
    "debris about him. Life at sea keeps him far stronger than most magi, "
    "and with his Norse build he looks imposing through a morning fog."
)
MARIS_SIGIL = (
    "Casting sigil: he seizes unseen threads between himself and the target "
    "and weaves them into the effect. Voting token: a snowflake bound in a "
    "spiral."
)
MARIS_COMBAT = (
    "Combat: dodge Init +1, Defense +3; fist Init +1, Attack +2, Defense "
    "+2, Damage +1; kick Init 0, Attack +2, Defense +1, Damage +4; harpoon "
    "Init +3, Attack +5, Defense +3, Damage +8. Soak +2. Encumbrance 0."
)
MARIS_SLVOLDER = (
    "Slvolder and Ormurin Langi: the ballad tells of King Olaf Tryggvason, "
    "who forced Christianity on Norway, and whose flagship the Long Serpent "
    "was doomed by Eirikr Hakonarson in the third attack of a great battle, "
    "said to be in the Oresund Straight near the lost isle of Slvolder; he "
    "and his crew leapt overboard. Maris found it in a storm his magic "
    "could not touch. It lies in a misty magical regio that opens only for "
    "one truly in peril of being lost at sea, and no other way in is known. "
    "He keeps a permanent lab there. So he returns only when failing "
    "against Natura; each return teaches him a lesson and gives the means "
    "to answer it. The day he can no longer reach it, he will hold his vow "
    "fulfilled."
)
MARIS_SEA = (
    "Voices in the Ocean: unaided, no words and only subtle gestures can be "
    "used to cast underwater, at the normal penalties. Voice-range spells "
    "cast submerged reach only targets in or touching the surface of the "
    "water. After each 10 meters of descent, a character loses a tenth of "
    "his depth minus Soak (armour not counted) in Fatigue Levels: at 50 "
    "meters with Soak 3, two levels, and three more on going ten deeper."
)
MARIS_ITEMS = paragraphs(
    "Items he has designed; the book does not date them. All are Pen 0; "
    "below, 2/day, sun stands for +1 2/day and +3 for a trigger at sunrise "
    "and sunset. Ever-Tempting Trap, tailored to a prey, his for "
    "cod: +5 to fishing. Sight of Wounded Prey (CrIm 14, constant, Touch, "
    "Sun, Individual): an illusion of bait, seen and smelled (Base 3, +1 "
    "Touch, +2 Sun; 2/day, sun).",
    "Eyeglass of Nereus, a rusty eyepiece. True Sight of the Air (InAu 25, "
    "24/day, Touch, Conc, Vision; Base 1, +1 Touch, +1 Conc, +4 Vision; +5 "
    "24/day, +5 maintains). Eyes of the Eagle (InIm 35, 24/day, Touch, "
    "Conc, Vision; Base 3, +1 Touch, +1 Conc, +4 Vision; +5 24/day, +5 "
    "maintains).",
    "Foul Weather's Bane, a cloak: +5 Soak against exposure, and neither "
    "freezes nor gathers ice. Cloak of the Duck's Feathers (ReAq 9, "
    "constant, Touch, Sun, Individual; Base 2, +2 Sun, +1 Touch; 2/day, "
    "sun). Comfort the Weary Traveler (CrIg 9, constant, Touch, Sun, "
    "Individual): warmth against the worst winter (same build).",
    "Gorget of Salty Breath, for working normally underwater. Lungs of the "
    "Fish (MuAq(Au) 24, constant, Touch, Sun, Part; Base 4, +1 Touch, +2 "
    "Sun, +1 Part; 2/day, sun), which gives too little air to speak spells. "
    "Surviving the Deep (MuCo 30, 1/day, Touch, Sun, Individual): body "
    "resists the deep, +3 Soak (Base 15, +1 Touch, +2 Sun). The Kraken's "
    "Song (MuIm 8, constant, Touch, Sun, Individual): voice becomes a loud "
    "high click that carries Voice-range spells through water (Base 1, +1 "
    "Touch, +2 Sun; 2/day, sun).",
    "The Nailed Down Chamber Pot, nailed to the deck. Remove the Unsightly "
    "Mess (PeCo(Aq) 20, unlimited, Touch, Momentary, Individual; Base 4, +1 "
    "Touch, +1 requisite; +10 unlimited).",
    "Neptune's Anchors, small weights on a long rope trailed behind the "
    "ship, which draws taut toward magical sites; Intelligence + Navigation "
    "Ease Factor 9 fixes a site well enough to dive. Guide the Seeker (ReHe "
    "16, constant, Personal, Momentary, Individual; Base 3; +3 linked, +10 "
    "unlimited). Seek the Enchanted Waters (InVi 19, constant, Vision, Sun, "
    "Individual): finds nearby vis (Base 1, +4 Vision, +2 Sun; 2/day, sun).",
    "Naiad's Cask. Cleanse Gaia's Tears (PeTe(Aq) 20, 24/day, Touch, "
    "Momentary, Individual): destroys all salt, leaving other impurities "
    "(Base 3, +1 Touch, +2 Mineral, +1 complex; +5 24/day).",
    "Roll of Endless Rope, a vine on a spindle that gives ten feet a tug; "
    "it may be cut off as long as five feet stay coiled. Rigging of it "
    "needs replacing each duration. Concoct Cordage (CrHe 15, unlimited, "
    "Touch, Moon, Individual; Base 1, +1 Touch, +3 Moon; +10 unlimited).",
    "Shroud of the Healed Body, bearing the cross of St. John. Hospitaller's "
    "Vigil (CrCo 24, constant, Touch, Sun, Individual): worn for a wound or "
    "sickness's duration, +12 to recovery (Base 5, +1 Touch, +2 Sun; 2/day, "
    "sun).",
    "Tryggvason's Chart, a circle of cured leather on the navigation "
    "console with a weighted line trailed astern, showing the sea around "
    "in real time: +5 Navigation for one who knows its notation. Reveal the "
    "Ocean's Secrets (InAq 19, constant, Touch, Sun, Part): motion, speed "
    "and bounds of the ocean up to 1500 feet all round (Base 3, +1 Touch, "
    "+2 Sun, +1 Part, +2 Size, +1 complexity; 2/day, sun). Visualize the "
    "Water's Flow (CrIm 11, constant, Touch, Sun, Individual): draws that as "
    "a map in his own notation (Base 1, +1 Touch, +2 Sun; 2/day, sun, +3 "
    "linked).",
)
MARIS_TALISMAN = paragraphs(
    "Talisman, the Paregro Mare: a ship of his own building, mixing Knarr "
    "and Buss, with a longship's oars she is not built to use, a lower deck in place of a shallow draft, single-masted, with about 30 tons of cargo, up to "
    "10 knots at best, and a cramped sanctum below. He has nearly lived "
    "aboard since leaving the Novgorod Tribunal. Attunements: +4 affect "
    "currents, +4 affect dead wood, +4 Aquam, +4 banish weather, +4 create "
    "or control winds, +7 protection from storms.",
    "Its effects, all Pen 0. Save Our Ship (PeAq 27, 3/day, Touch, "
    "Momentary, Room): all water in the hold is destroyed, liquids stored "
    "there too, and everything left slightly dry (Base 10, +1 Touch, +2 "
    "Room; +2 3/day). Eye of the Storm (ReAq 8, constant, Personal, Sun, "
    "Individual): waves part round her, so rough seas add nothing to "
    "sailing Ease Factors, though strong winds do, and she is very hard to "
    "swamp (Base 2, +2 Sun; +1 2/day, +3 sun). Ward the Drowning Waves "
    "(ReAq 33, 6/day, Touch, Conc, Room): clears water from the lower hold "
    "and keeps it out long enough for repairs (Base 5, +1 Touch, +1 Conc, "
    "+2 Room; +3 6/day, +5 maintains). Control the Reckless Vessel "
    "(ReAq(Au) 35, 24/day, Touch, Conc, Individual): wind and currents "
    "drive her, holding heading and speed while he is elsewhere, sailing "
    "without him on deck, and holding station with the rudder raised, even "
    "where too deep to anchor; +7 to sailing checks (Base 4, +1 Touch, +1 "
    "Conc, +2 Size, +1 requisite; +5 24/day, +5 maintains). Hull of "
    "Unbreakable Iron (MuHe(Te) 24, constant, Personal, Sun, Individual): "
    "metal-hard hull, immune to ramming; a captain who rams wrecks himself "
    "if he fails the contested Int + Profession by more than his Profession "
    "(Base 4, +2 Sun, +2 Size; +1 2/day, +3 sun). Helios' Companionship "
    "(CrIg 29, constant, Touch, Sun, Group, by the errata): torchlight and summer warmth "
    "below, which by Covenants pages 118-119 gives the lab Magical Lighting "
    "and Magical Heating (Superior) as free Virtues (printed Base 3, +2 Sun, +2 "
    "Room, +1 heat; +1 2/day, +3 sun, before the errata's changes).",
)


def _maris(
    column: int,
    age: int,
    apparent: int,
    arts: str,
    warping: tuple[int, int],
    notes: str,
    **extra: Any,
) -> Printing:
    rows = (
        MARIS_SPELLS_0,
        MARIS_SPELLS_15,
        MARIS_SPELLS_15,
        MARIS_SPELLS_45,
        MARIS_SPELLS_60,
    )[column]
    masteries = {n: MARIS_MASTERIES.get(n, "Quiet Casting") for n, _, _ in rows}
    block: StatBlock = {
        "characteristics": characteristics(1, 1, 0, -1, 1, 2, 1, 1),
        "confidence": (2, 5),
        "apparent_age": apparent,
        "warping": warping,
        "virtues_flaws": MARIS_VF,
        "traits": {"Careful": 3, "Determined": 2, "Disciplined": 1, "Brave": 1},
        "reputations": {"Dedicated (Tytalus)": 1, "Insane": 4},
        "abilities": _abilities(MARIS_ABILITIES, column),
        "arts": arts_from(arts),
        **_spells(rows, masteries),
        "notes": paragraphs(notes, _spell_notes(rows, MARIS_RULES)),
        **extra,
    }
    label = ("Gauntlet", "+15", "+30", "+45", "+60")[column]
    return Printing(label, age, block)


MARIS = Magus(
    name="Maris of Tytalus",
    house="house_tytalus",
    summary=paragraphs(
        "A Calliclean Tytalus who thought the Order's covenants and their "
        "help, meant or not, spoiled the great conflict. Wanting a rival "
        "tougher and less fickle than Nomos, he left it for Natura, vowing "
        "to take no aid from anyone until he has mastered her. He lives "
        "alone on the Baltic in his ship, the Paregro Mare, with no friend "
        "or teacher. Ashore on his island sanctuary of Slvolder in the "
        "Oresund Straight he works in his lab, finding ways to ease life "
        "at sea and meet what Natura sends; at sea he gathers supplies, "
        "tends underwater gardens, and trawls for ancient magical sites "
        "lost beneath the waves where others cannot or will not go.",
        "One storm, seemingly with a life of its own, wrecks each of his "
        "plans: it strands him on Slvolder, nearly drowns him in a vortex "
        "until helpful merfolk save him, and later capsizes the Paregro "
        "Mare. In his last printing he sets out on the first day of the new "
        "year 1300 swearing never to return, and the Order loses him.",
    ),
    printings=(
        _maris(
            0,
            25,
            25,
            "Cr 10, In 5, Mu 5, Pe 5, Re 5, An 5, Aq 5, Au 5, Co 1, He 5, Ig 5, "
            "Im 1, Me 1, Te 1, Vi 1",
            (0, 1),
            paragraphs(
                MARIS_LOOK,
                MARIS_SIGIL,
                MARIS_COMBAT,
                "Equipment: seafaring gear, and tools for repairs and fishing.",
            ),
        ),
        _maris(
            1,
            40,
            36,
            "Cr 20, In 8, Mu 10, Pe 7, Re 20, An 5, Aq 10, Au 10, Co 6, He 5, "
            "Ig 5, Im 4, Me 2, Te 5, Vi 5",
            (3, 5),
            paragraphs(
                f"{MARIS_LOOK} {MARIS_LOOK_SEA}",
                MARIS_SIGIL,
                MARIS_COMBAT,
                "Last 15 years: he left covenant life after five years, "
                "spent five alone at sea until a horrendous storm beached "
                "the Paregro Mare and washed him ashore on Slvolder near "
                "death, and lived there five more until ready to tempt "
                "Natura again. There he made a longevity ritual, score 8. "
                "Time on the ship counts as exposure and practice, time on "
                "the island as lab work and study of vis.",
                MARIS_SLVOLDER,
                MARIS_SEA,
                MARIS_TALISMAN,
                MARIS_ITEMS,
            ),
        ),
        _maris(
            2,
            55,
            45,
            "Cr 20, In 12, Mu 20, Pe 12, Re 20, An 5, Aq 10, Au 10, Co 11, "
            "He 12, Ig 5, Im 4, Me 2, Te 11, Vi 5",
            (4, 11),
            paragraphs(
                "Life at sea keeps him far stronger than most magi.",
                "Twilight scar: his hair is slightly animate and wriggles by itself.",
                MARIS_SIGIL,
                MARIS_COMBAT,
                "Last 15 years: a decade at sea perfecting his hunt for "
                "treasures the deep has claimed, until a storm drew him and "
                "the ship into a huge vortex and helpful merfolk saved them. "
                "Back on Slvolder he went on working to beat Natura's every "
                "challenge. Ten years of experience at sea, five on the "
                "island.",
                MARIS_SLVOLDER,
                MARIS_SEA,
                MARIS_TALISMAN,
                MARIS_ITEMS,
            ),
            decrepitude=(0, 0),
        ),
        _maris(
            3,
            70,
            59,
            "Cr 20, In 13, Mu 20, Pe 12, Re 20, An 6, Aq 10, Au 10, Co 11, "
            "He 14, Ig 6, Im 9, Me 2, Te 12, Vi 6",
            (6, 10),
            paragraphs(
                "He smells constantly of salt and the sea, with seaweed and "
                "debris about him.",
                "Twilight scars: his hair is slightly animate and wriggles "
                "by itself; his shadows fall toward the light, not away.",
                MARIS_SIGIL,
                MARIS_COMBAT,
                "Last 15 years: a huge wave capsized the Paregro Mare and "
                "spilled her supplies, and he drifted injured and unfed for "
                "nearly a week until he beached on Slvolder. Furious, he "
                "spent a decade there, swearing that next time he left he "
                "would never return. Five years of experience aboard, ten "
                "on the island.",
                MARIS_SLVOLDER,
                MARIS_SEA,
                MARIS_TALISMAN,
                MARIS_ITEMS,
            ),
            decrepitude=(0, 1),
        ),
        _maris(
            4,
            85,
            63,
            "Cr 20, In 17, Mu 20, Pe 15, Re 20, An 7, Aq 15, Au 15, Co 15, "
            "He 14, Ig 6, Im 15, Me 2, Te 13, Vi 8",
            (8, 17),
            paragraphs(
                "Age is beginning to tell: he looks a little thin, and the "
                "years at sea have weathered his skin almost to stony shore.",
                "Twilight scars: his hair is slightly animate and wriggles "
                "by itself; his shadows fall toward the light, not away; a "
                "salt crust slowly forms on his skin.",
                MARIS_SIGIL,
                MARIS_COMBAT,
                "Last 15 years: scornful and angry after his last meeting "
                "with Natura, and after his longest stay on the island, he "
                "set out swearing never to return. With the Paregro Mare he "
                "seeded underwater gardens for food, and forged new items "
                "and invented spells. He set sail from Slvolder on the "
                "first day of the new year 1300, and no one has sighted his "
                "ship since.",
                MARIS_SLVOLDER,
                MARIS_SEA,
                MARIS_TALISMAN,
                MARIS_ITEMS,
            ),
            decrepitude=(0, 2),
        ),
    ),
)


# --------------------------------------------------------------- Marcus

MARCUS_ABILITIES: tuple[tuple[Any, ...], ...] = (
    ("Animal Ken", "cattle", 1, 2, 2, 2),
    ("Artes Liberales", "logical traps", 2, 2, 2, 2),
    ("Athletics", "escape", 1, 1, 1, 1),
    ("Awareness", "ambushes", 1, 1, 1, 2),
    ("Brawl", "dodge", N, 1, 1, 1),
    ("Chirurgy", "internal surgery", 2, 2, 3, 3),
    ("Area Lore: Crete", "ruins", 2, 2, 2, 2),
    ("Enigmatic Wisdom", "mazes", 1, 3, 4, 5),
    ("Finesse", "Animal", 1, 1, 1, 2),
    ("Living Language: Greek", "Cretan", 5, 5, 5, 5),
    ("Organization Lore: House Criamon", "Corpus experts", 1, 3, 5, 5),
    ("Dead Language: Latin", "Hermetic", 4, 4, 4, 4),
    ("Magic Lore", "hybrid beasts", 1, 1, 2, 2),
    ("Magic Theory", "original research", 4, 5, 5, 6),
    ("Parma Magica", "Corpus", 1, 2, 3, 4),
    ("Penetration", "Animal", 1, 1, 1, 3),
    ("Philosophiae", "animals", N, 2, 2, 2),
    ("Stealth", "avoiding pursuers", 1, 1, 1, 1),
    ("Survival", "barren lands", 2, 2, 2, 2),
)

MARCUS_MAJOR_VIRTUES: list[Any] = [
    "The Gift",
    "Hermetic Magus",
    "Giant Blood",
    ("Major Magical Focus", {"focus": "organs"}),
]
MARCUS_MINOR_VIRTUES: list[Any] = [
    vf_art("Affinity with {art}", "Animal"),
    "Animal Ken",
    "The Enigma",
    "Improved Characteristics",
    "Inventive Genius",
]
MARCUS_BLOCK = ("Ability Block", {"abilities": "Martial Abilities"})
MARCUS_TEASING = ("Oversensitive (Minor)", {"detail": "teasing"})
MARCUS_VF_0: list[Any] = [
    *MARCUS_MAJOR_VIRTUES,
    *MARCUS_MINOR_VIRTUES,
    "Driven (Major)",
    "Low Self-Esteem",
    MARCUS_BLOCK,
    MARCUS_TEASING,
    "Poor Eyesight",
    "Warped Magic",
]
MARCUS_VF_15: list[Any] = [
    *MARCUS_MAJOR_VIRTUES,
    "Station of Differentiation of Seeming",
    "Station of True Sight",
    *MARCUS_MINOR_VIRTUES,
    ("Disfigured", {"detail": "labyrinth stigmata"}),
    "Driven (Major)",
    "Low Self-Esteem",
    MARCUS_BLOCK,
    MARCUS_TEASING,
    "Poor Eyesight",
    ("Vow (Minor)", {"detail": "live aptly"}),
    "Warped Magic",
]
MARCUS_VF_30: list[Any] = [
    *MARCUS_MAJOR_VIRTUES,
    "Station of Differentiation of Seeming",
    "Station of True Sight",
    "Station of Vivid Memories from Objects",
    *MARCUS_MINOR_VIRTUES,
    ("Disfigured", {"detail": "labyrinth stigmata"}),
    "Driven (Major)",
    "Pious (Major)",
    "Low Self-Esteem",
    MARCUS_BLOCK,
    MARCUS_TEASING,
    "Poor Eyesight",
    "Warped Magic",
]

MARCUS_SPELLS_0: tuple[SpellRow, ...] = (
    ("True Rest of the Injured Brute", "CrAn", 20),
    ("Beast of Outlandish Size", "MuAn", 15),
    ("Growth of Creeping Things", "MuAn", 15),
    ("Transformation of the Ravenous Beast to the Torpid Toad", "MuAn", 25),
    ("Decay Fur and Hide", "PeAn", 10),
    ("Bind Wound", "CrCo", 10),
    ("Eyes of the Cat", "MuCo(An)", 5),
    ("Arm of the Infant", "MuCo", 20),
)
MARCUS_SPELLS_15 = (
    *MARCUS_SPELLS_0,
    ("Worm of the Soil", "CrAn", 20),
    ("Flight Perfected", "CrAn", 25),
    ("Flight Divorced", "CrAn", 30),
    ("Soothe the Ferocious Boar", "ReAn", 10),
    ("Bushy Tail of the Branch-Dancer", "MuCo(An)", 5),
    ("Sure-Footedness of the Crag-Leaper", "MuCo(An)", 5),
    ("Webbed Toes of the Pond-Dweller", "MuCo(An)", 5),
    ("Kiss of the Enigma", "CrVi", 15),
)
MARCUS_SPELLS_30 = (
    *MARCUS_SPELLS_15,
    ("Strength Extinguished", "CrAn", 30),
    ("Strength Renewed", "CrAn", 35),
    ("The Beast Remade", "MuAn(Co)", 25),
    ("Blunt the Viper's Fangs", "PeAn", 15),
    ("Slime of the Muck-Dweller", "MuCo(An)", 5),
    ("Spirit of the Bull of Minos", "MuCo(An)", 20),
    ("Prying Eyes", "InIm", 5),
)
MARCUS_SPELLS_45 = (
    *MARCUS_SPELLS_30,
    ("The Wizard's Mount", "CrAn", 35),
    ("Touch of the Wild", "MuAn", 20),
    ("Icarus' Folly", "MuAn", 40),
    ("A Limb Bereft", "CrCo(Re)", 30),
    ("Eyes from the Wizard Torn", "MuCo(In,Re,Im)", 15),
    ("Gift of the Minotaur", "MuCo(An)", 30),
    ("The Griffin Reborn", "MuAn", 35),
    ("Stillness of the Dead", "ReCo(An)", 25),
)

MARCUS_RULES = {
    "Worm of the Soil": (
        "Touch, Sun, Individual. Creates a beetle; every invertebrate counts "
        "as a worm in Mythic Europe. No breakthrough. (Base 5, +1 Touch, +2 "
        "Sun)"
    ),
    "Flight Perfected": (
        "Touch, Sun, Individual. Creates a dove in the hands, a normal bird "
        "for the duration. No breakthrough. (Base 10, +1 Touch, +2 Sun)"
    ),
    "Flight Divorced": (
        "Touch, Sun, Part. Creates a joined pair of living bird wings, "
        "flapping at random, having no mind or senses; loose indoors they "
        "give -3 to rolls needing concentration and an extra botch die. "
        "Gave a breakthrough in the first of two seasons. (Base 10, +1 "
        "Touch, +2 Sun, +1 Part)"
    ),
    "Strength Extinguished": (
        "Touch, Sun, Part. Creates a bull's heart. No breakthrough. (Base "
        "10, +1 Touch, +2 Sun, +1 Part)"
    ),
    "Strength Renewed": (
        "Touch, Sun, Part. Creates a bull's heart that beats strongly. "
        "Three seasons gave a breakthrough, and experimentation left a "
        "flaw: it beats only in light, faintly in shadow and like a drum in "
        "full sun. (Base 15, +1 Touch, +2 Sun, +1 Part)"
    ),
    "Touch of the Wild": (
        "Touch, Moon, Individual. An animal goes feral, shedding training "
        "and domestication: larger though usually not in Size, longer "
        "haired, fiercer in horn, tooth and claw, and often plain brown or "
        "grey. No breakthrough. (Base 4, +1 Touch, +3 Moon)"
    ),
    "The Griffin Reborn": (
        "Touch, Moon, Pair, Ritual. Swaps the heads of two animals; the "
        "surgery does no harm if cast rightly. With a Corpus requisite one "
        "may be human. At the end he can restore them if both are there, "
        "else both die. From an insight into Minoan magic; Pair counts as "
        "Group, and a Hermetic version would be Part on one creature. (Base "
        "5, +1 Touch, +3 Moon, +2 Pair)"
    ),
    "Icarus' Folly": (
        "Touch, Sun, Individual. An animal grows wings, learning flight in "
        "a few tries. An experimental flaw: each hour roll a simple die, "
        "and on hours passed or less the spell ends early, which killed "
        "his first subjects. The second season gave a breakthrough. (Base "
        "25, +1 Touch, +2 Sun)"
    ),
    "A Limb Bereft": (
        "Touch, Sun, Part. Creates a living human leg that hops, needing "
        "Rego for motion as animal organs do not, and tends to kick what it "
        "nears: if not attacked, its target takes -3 to all rolls and 2 "
        "extra botch dice. No breakthrough. (Base 5, +1 Touch, +2 Sun, +1 "
        "Part, +1 requisite) The leg: Size -3; kick Init -1, Attack +0, "
        "Defense -1, Damage +3; Soak +0; wounds -1 (1-2), -3 (3-4), -5 "
        "(5-6), Incapacitated (7-8), Dead (9+)."
    ),
    "Eyes from the Wizard Torn": (
        "Personal, Concentration, Part. His eyes come out and fly to a place "
        "and send back what they see, and return at the end; a macabre "
        "turn on Image from the Wizard Torn and Prying Eyes. The Rego "
        "requisite adds no magnitude. No breakthrough. (Base 3, +1 Conc, +1 "
        "Part, +1 Intellego requisite, +1 Imaginem requisite)"
    ),
    "Spirit of the Bull of Minos": (
        "Touch, Year, Individual, Ritual. The target's heart is swapped for "
        "a bull's, harmlessly if cast rightly, granting Reserves of Strength. "
        "At the year's end he can restore a well-kept heart; otherwise the "
        "target dies. From an Insight (Ancient Magic pages 8-9) after he "
        "read a sacrificial knife's memories under Knossos, left by the "
        "Minoan Cult of the Bull. (Base 2, +1 Touch, +4 Year; level 20 as a "
        "ritual)"
    ),
    "Kiss of the Enigma": (
        "Touch, Momentary, Individual. The target takes two Warping Points, "
        "and a magus checks for Twilight. Meant to bring out monstrous "
        "traits in caged animals, with random results. Invented three times "
        "before a breakthrough; the two earlier versions had Side Effects, "
        "changing hair colour and making skin transparent. (Base 10, +1 "
        "Touch)"
    ),
    "Bushy Tail of the Branch-Dancer": (
        "Touch, Sun, Individual. A squirrel's tail: +3 to keep balance. "
        "(Base 2, +1 Touch, +2 Sun, requisite free)"
    ),
    "Slime of the Muck-Dweller": (
        "Touch, Sun, Individual. An eel's slimy skin: +6 Defense against "
        "grappling. (Base 2, +1 Touch, +2 Sun, requisite free)"
    ),
    "Sure-Footedness of the Crag-Leaper": (
        "Touch, Sun, Individual. A mountain goat's hooves: +3 on steep "
        "climbs and descents. (Base 2, +1 Touch, +2 Sun, requisite free)"
    ),
    "Webbed Toes of the Pond-Dweller": (
        "Touch, Sun, Individual. A frog's feet: +3 to swim in still or slow "
        "water. (Base 2, +1 Touch, +2 Sun, requisite free)"
    ),
    "Gift of the Minotaur": (
        "Touch, Sun, Part. The target gets a bull's head; he can speak, but "
        "the voice changes. Horns use Brawl: Init +2, Attack +3, Defense "
        "+2, Damage +3. (Base 10, +1 Touch, +2 Sun, +1 Part)"
    ),
    "Stillness of the Dead": (
        "Touch, Sun, Individual. Holds a human or animal wholly immobile, "
        "made for the subjects of his body-swapping rituals. (Base 5, +1 "
        "Touch, +2 Sun, +1 requisite)"
    ),
}

MARCUS_LOOK = (
    "Massive: eight feet tall and broad with it, in simple clothes, "
    "shoulders hunched in a vain try at hiding his size. Olive skin, black "
    "hair, and a beard trimmed close to the jaw, with no moustache."
)
MARCUS_STIGMA = (
    "The stigmata of the Path of Seeming show as an interlocking labyrinth "
    "round his forehead, which shifts as he does magic, as if tracing his "
    "way through the maze."
)
MARCUS_SIGIL = (
    "Casting sigil: horns, usually in shadow or as a ghostly image. Voting "
    "sigil: a bronze bull's head."
)
MARCUS_WARPED = (
    "Warped Magic: his organs glow through his skin as he casts, by the "
    "spell's Form: Animal and Auram the liver; Aquam and Imaginem the brain; "
    "Corpus and Vim the heart; Herbam and Terram the spleen; Ignem and "
    "Mentem the gallbladder."
)
MARCUS_RESEARCH = paragraphs(
    "Original Research (Houses of Hermes: True Lineages pages 26-30): he "
    "seeks a Major Breakthrough into a Hermetic Virtue, Hermetic "
    "Metamorphosis, believing the Counter-Cyclical Alam (Houses of Hermes: "
    "Mystery Cults page 47), the mirror of our world across the Wheel of "
    "Time, moves from chaos toward harmony: first lone organs, then "
    "creatures, then chimeras, and at last all life combined. He holds the "
    "chimeric beasts of antiquity to be more harmonious than those of today "
    "and wants to remake them, which Hermetic magic forbids. The Wizard's "
    "Mount, Prying Eyes and The Beast Remade he also invented, gaining 5 "
    "points from the last.",
)
MARCUS_VIRTUE = paragraphs(
    "Likely result, not yet real: Hermetic Metamorphosis (Minor, "
    "Supernatural and Hermetic), once integrated into theory and taught by "
    "a source of at least 5 xp in a season. Organs from another animal or "
    "from a Momentary Creo Animal ritual can be grafted to an animal; "
    "giving a human an animal organ needs a further breakthrough; it is not "
    "known whether results breed true.",
    "Its ritual, Harmonic Metamorphosis of the Beast (Cr(Mu)An 35, Touch, "
    "Momentary, Individual, Ritual; Base 25, +1 Touch, +1 requisite): "
    "recipient and any donor animal immobilized, the caster moves a "
    "functional organ across, resizing and joining it. A replacement swaps "
    "organs; the old one may go to the donor for a second surgery roll. A "
    "transposed organ is an addition, and kills the donor. A graft may be "
    "anatomical, giving an ability or Quality (Houses of Hermes: Mystery "
    "Cults pages 40-43), or give a bodily General Virtue, the donor taking "
    "Enfeebled if it lives. Dexterity + Chirurgy Ease Factor 9, +3 if "
    "transposed, +3 if a Virtue passes. On failure the animal soon dies; on "
    "a botch a dreadful monster results. Swapping lion and eagle heads, the "
    "eagle's head on the lion needs 12 for Keen Vision, the lion's on the "
    "eagle 9, and that bird is Enfeebled.",
)
MARCUS_LABYRINTH = (
    "The Labyrinth of the Open Mind: his laboratory floor, of pale and "
    "dark-stained wood in a labyrinth, furniture and tools set at mystic "
    "points, each path a different effect (Covenants page 121). Opened with "
    "10 pawns of Vim vis, three effects using 9. All Pen 0. Path to "
    "Serendipitous Discovery (CrVi 24, constant, Touch, Sun, Room): taints "
    "the sanctum, +2 lab specialization in Experimentation but Warping "
    "Score +1 (Base 3, +1 Touch, +2 Sun, +2 Room; +1 2/day, +3 "
    "environmental). Path to Enlightened Operations (ReAn 20, unlimited, "
    "Touch, Conc, Room): items of animal stuff float where released, "
    "drifting into propitious order, General Quality +1 (Base 1, +1 Touch, "
    "+1 Conc, +2 Room; +10 unlimited, +5 maintains). Path of Shadows "
    "Beneath the Skin (InCo(An) 40, 1/day, Touch, Conc, Vision): a magical "
    "sense of internal organs, +2 lab specialization in Corpus and in "
    "Animal (Base 5, +1 Conc, +4 Vision, +1 requisite; +5 maintains)."
)
MARCUS_JARS = (
    "Canopic Jars: four alabaster figures 18 inches tall with hawk, lion, "
    "baboon and human heads as lids, after the Egyptian jars; lesser "
    "enchantments, made two to a season, to keep the hearts of his subjects. "
    "Halt Corruption's Work (CrCo 9, Pen 0, constant, Touch, Sun, "
    "Individual): an organ inside does not rot (Base 2, +1 Touch, +2 Sun; "
    "+1 2/day, +3 environmental)."
)
MARCUS_MARK = (
    "The Mark of Protection: a tattoo of the sun in glory over his whole "
    "abdomen, invested with 6 pawns (material 2, multiplier 3 for size; "
    "Houses of Hermes: Mystery Cults page 51). Its purple murex ink and "
    "crushed shells give +2 Shape and Material for protection. Resilience "
    "of Theseus (MuCo 39, Pen 0, constant, Touch, Sun, Individual): +4 "
    "Soak, but by an experimental flaw only while the tattoo is uncovered "
    "(Base 20, +1 Touch, +2 Sun; +1 2/day, +3 environmental)."
)
MARCUS_MARK_ERRATA = (
    "The season he believes he put a second effect, Ariadne's Thread, into "
    "the Mark was, by the errata, spent partying: the effect does not work "
    "and was never made."
)
MARCUS_STAFF = paragraphs(
    "Talisman, Bucephalos (ox-faced): a four-foot staff of linden three "
    "inches thick, like a walking stick to him, its head a bull of glossy "
    "magnetite with topaz eyes. Opened with 12 pawns of Vim vis, three "
    "effects using 9. Attunements: +3 Animal (magnetite), +2 protection "
    "against weapons (linden), +4 control things at a distance (staff).",
    "Mastering the Unruly Beast (ReAn 33, Pen 16, 1/day, Touch, Conc, "
    "Individual): as the spell; point the head and slowly lower it (Base "
    "15, +1 Touch, +1 Sun; +8 Penetration, the book's breakdown naming Sun "
    "where the heading says Conc). Punishment of Midas (MuCo(An) 40, Pen 0, "
    "1/day, Voice, Sun, Group): point and circle with the command word; up "
    "to ten people, or one target several times if fewer, each have a limb "
    "changed. Limb on a simple die: 1-2 head, 3-6 arm, 7-10 leg, odd left, "
    "even right. Animal: 1 goat, 2 pig, 3 hare, 4 chicken or donkey (the "
    "book prints 4 twice), 5 dog, 6 lizard, 7 toad, 8 cow, 9 rat, 10 "
    "beetle. Limbs fit the old size; a hand drops what it holds, a leg no "
    "longer fits its shoe, and a transformed head cannot speak but keeps "
    "its wits. The chicken is an experimental quirk (Base 10, +2 Voice, +2 "
    "Sun, +2 Group). Return to the Earth (MuTe 20, Pen 10, 24/day, Voice, "
    "Momentary, Individual): jab the butt and speak; a one-handed metal or "
    "stone object is sand for a moment, which ruins most weapons, though "
    "left undisturbed it is whole again (Base 2, +2 Voice, +2 metal; +5 "
    "Penetration, +5 24/day).",
)


def _marcus(
    column: int,
    age: int,
    apparent: int,
    arts: str,
    warping: tuple[int, int],
    vf: list[Any],
    notes: str,
) -> Printing:
    rows = (
        MARCUS_SPELLS_0,
        MARCUS_SPELLS_15,
        MARCUS_SPELLS_30,
        MARCUS_SPELLS_45,
    )[column]
    block: StatBlock = {
        "characteristics": characteristics(3, 2, 0, -1, 3, 3, -2, -1),
        "size": 2,
        "apparent_age": apparent,
        "warping": warping,
        "virtues_flaws": vf,
        "traits": {
            "Brave": 3,
            "Obsessed": 3,
            "Angry": 2,
            **({} if column else {"Outgoing": -2}),
        },
        "abilities": _abilities(MARCUS_ABILITIES, column),
        "arts": arts_from(arts),
        **_spells(rows, {}),
        "notes": paragraphs(notes, _spell_notes(rows, MARCUS_RULES)),
    }
    label = ("Gauntlet", "+15", "+30", "+45")[column]
    return Printing(label, age, block)


MARCUS_COMBAT = "Combat: dodge Init -1, Defense +1. Soak +3. Encumbrance 0."
MARCUS_COMBAT_MARK = (
    "Combat: dodge Init -1, Defense +1. Soak +7 with the Mark of Protection "
    "on his belly exposed. Encumbrance 0."
)

MARCUS = Magus(
    name="Marcus of Criamon",
    house="house_criamon",
    sketch="Marcus Tauros",
    summary=paragraphs(
        "A giant-blooded Criamon who wants to make living beings by "
        "combining existing creatures, the minotaur above all. His size "
        "shames him: cruelly teased as a child, he was deeply grateful to "
        "the master who took him from those who feared his Gift and showed "
        "him how to better himself, and he still grows angry when anyone "
        "mentions his height, however kindly. That master, an anatomist, "
        "taught him the body and fostered his gift with its organs.",
        "Initiated into House Criamon's mysteries, he saw a past life as a "
        "Minoan priest on Crete who made the minotaur from a man and a "
        "sacred bull. If he can repeat that across the Wheel of Time, he "
        "believes, he can mend what he hates in his body and mind; "
        "finishing the work would likely lift his Low Self-Esteem and give "
        "him a Confidence Score of 1. The obsession has cost him the usual "
        "marks of Hermetic maturity: no familiar, no apprentice, and no "
        "talisman until forty years a magus.",
        "He digs at the ruined palace of Knossos, whose catacombs held "
        "objects of the Minoan Cult of the Bull, and by his last printing "
        "stands on the edge of his breakthrough.",
    ),
    printings=(
        _marcus(
            0,
            24,
            24,
            "Cr 8, In 0, Mu 8, Pe 0, Re 0, An 10, Aq 0, Au 0, Co 8, He 0, Ig 0, "
            "Im 0, Me 0, Te 0, Vi 0",
            (0, 0),
            MARCUS_VF_0,
            paragraphs(
                MARCUS_LOOK,
                MARCUS_SIGIL,
                MARCUS_WARPED,
                "Combat: dodge Init -1, Defense -1. Soak +3. Equipment: "
                "peasant clothing. Encumbrance 0.",
                MARCUS_RESEARCH,
            ),
        ),
        _marcus(
            1,
            39,
            35,
            "Cr 10, In 4, Mu 10, Pe 3, Re 3, An 13, Aq 3, Au 0, Co 9, He 0, "
            "Ig 0, Im 0, Me 4, Te 0, Vi 6",
            (2, 4),
            MARCUS_VF_15,
            paragraphs(
                f"{MARCUS_LOOK} {MARCUS_STIGMA}",
                MARCUS_SIGIL,
                MARCUS_WARPED,
                "Twilight scars: his shadow has horns; the third and fourth "
                "fingers of each hand have fused.",
                f"{MARCUS_COMBAT} Equipment: peasant clothing.",
                "Last 15 years: three years past his Gauntlet he was "
                "initiated onto the Path of Seeming (Houses of Hermes: "
                "Mystery Cults pages 64-67), and eight years later reached "
                "the second Station, True Sight, each taking a season. He "
                "made his longevity ritual, a tattoo over his heart; spent "
                "two seasons stabilizing his Original Research (9 "
                "breakthrough points these years); and prepared his lab "
                "floor and invested one effect, two seasons. 145 levels of "
                "spells invented or learned, 115 xp in Abilities and 130 in "
                "Arts.",
                MARCUS_RESEARCH,
                MARCUS_LABYRINTH,
            ),
        ),
        _marcus(
            2,
            54,
            38,
            "Cr 11, In 6, Mu 11, Pe 4, Re 5, An 15, Aq 3, Au 3, Co 11, He 3, "
            "Ig 3, Im 5, Me 4, Te 3, Vi 8",
            (3, 10),
            MARCUS_VF_30,
            paragraphs(
                f"{MARCUS_LOOK} {MARCUS_STIGMA}",
                MARCUS_SIGIL,
                MARCUS_WARPED,
                "Twilight scars: his shadow has horns; the third and fourth "
                "fingers of each hand have fused; he leaves cloven "
                "footprints; his Gift draws flies, not repels them.",
                f"{MARCUS_COMBAT_MARK} Equipment: peasant clothing, Canopic "
                "Jars, Mark of Protection.",
                "Last 15 years: initiated into the third Station of the Path "
                "of Seeming (a season); two seasons on four Canopic Jars; "
                "three enchanting the abdomen tattoo; one on the second lab "
                "effect; two investigating the Minoan labyrinth at Knossos, "
                "with insight into its ancient magic; two stabilizing his "
                "research, now 25 breakthrough points in all. 135 levels of "
                "spells invented or learned, 105 xp in Abilities and 140 in "
                "Arts.",
                MARCUS_RESEARCH,
                MARCUS_LABYRINTH,
                MARCUS_JARS,
                MARCUS_MARK,
            ),
        ),
        _marcus(
            3,
            69,
            43,
            "Cr 12, In 6, Mu 13, Pe 5, Re 8, An 16, Aq 5, Au 5, Co 13, He 4, "
            "Ig 5, Im 6, Me 5, Te 5, Vi 8",
            (4, 13),
            MARCUS_VF_30,
            paragraphs(
                f"{MARCUS_LOOK} {MARCUS_STIGMA} His strong longevity ritual "
                "keeps him looking in his early forties though he is nearly "
                "seventy, and he carries a bull-headed walking stick, his "
                "talisman, as large as a staff to most.",
                MARCUS_SIGIL,
                MARCUS_WARPED,
                "Twilight scars: his shadow has horns; the third and fourth "
                "fingers of each hand have fused; he leaves cloven "
                "footprints; his Gift draws flies, not repels them; when he "
                "feels strongly, all within seven paces must roll a suitable "
                "Personality Trait at Ease Factor 6 or feel the same; he "
                "sneezes sparks near magic, which does not let him detect "
                "it, though the second Station usually does.",
                f"{MARCUS_COMBAT_MARK} Equipment: peasant clothing, Canopic "
                "Jars, Mark of Protection, Bucephalos.",
                "Last 15 years: a season on what he took for a second effect "
                "in the Mark; two seasons on a third effect in the "
                "Labyrinth; seven preparing, attuning and investing three "
                "effects in his talisman; one stabilizing a breakthrough. "
                "His Arts now use the seasonal method: 230 levels in 13 "
                "seasons, and 41 breakthrough points in all, on the verge of "
                "completing his research. 120 xp in Abilities and 140 in "
                "Arts.",
                MARCUS_RESEARCH,
                MARCUS_VIRTUE,
                MARCUS_LABYRINTH,
                MARCUS_JARS,
                f"{MARCUS_MARK} {MARCUS_MARK_ERRATA}",
                MARCUS_STAFF,
            ),
        ),
    ),
)


# ----------------------------------------------------------- Persephone

PERSEPHONE_ABILITIES: tuple[tuple[Any, ...], ...] = (
    ("Artes Liberales", "logic", 2, 2, 3, 3),
    ("Charm", "elders", 1, 2, 2, 2),
    ("Concentration", "jostled", 1, 1, 1, 2),
    ("Finesse", "Imaginem", 1, 2, 2, 3),
    ("Folk Ken", "nobles", N, 1, 1, 2),
    ("Living Language: French", "Norman", 5, 5, 5, 5),
    ("Guile", "disguise", 2, 2, 3, 3),
    ("Intrigue", "Hermetic", N, 2, 2, 2),
    ("Dead Language: Latin", "arguing", 4, 4, 4, 4),
    ("Magic Theory", "enchanting jewelry", 4, 5, 6, 6),
    ("Organization Lore: Order of Hermes", "House Tytalus", 1, 1, 2, 2),
    ("Parma Magica", "Corpus", 1, 2, 3, 4),
    ("Penetration", "Mentem", 1, 3, 3, 4),
    ("Philosophiae", "Tytalan philosophy", 1, 3, 3, 3),
    ("Stealth", "towns", N, 1, 1, 2),
    ("Teaching", "Arts", N, 1, 2, 2),
)


def _persephone_vf(driven: str) -> list[Any]:
    return [
        "The Gift",
        "Hermetic Magus",
        "Secondary Insight",
        vf_art("Affinity with {art}", "Muto"),
        "Improved Characteristics",
        vf_art("Puissant {art}", "Mentem"),
        "Quiet Magic",
        "Self-Confident",
        "Social Contacts",
        ("Special Circumstances", {"circumstance": "when sister is near"}),
        "Subtle Magic",
        ("Deficient Technique", {"technique": "Creo"}),
        ("Driven (Major)", {"detail": driven}),
        ("True Love (Major)", {"detail": "sister"}),
        ("Fear", {"detail": "fire"}),
    ]


PERSEPHONE_SPELLS_0: tuple[SpellRow, ...] = (
    ("Disguise of the New Visage", "MuCo", 15),
    ("Dance of the Staves", "ReHe", 5),
    ("Prying Eyes", "InIm", 5),
    ("Recollection of Memories Never Quite Lived", "MuMe", 4),
    ("Sight of the Transparent Motive", "InMe", 10),
    ("Tip of the Tongue", "PeMe", 5),
    ("Trust of Childlike Faith", "PeMe", 10),
    ("The Call to Slumber", "ReMe", 10),
    ("Confusion of the Numbed Will", "ReMe", 15),
    ("Object of Increased Size", "MuTe", 15),
    ("Wielding the Invisible Sling", "ReTe", 10),
    ("Shroud Magic", "MuVi", 15),
)
PERSEPHONE_SPELLS_15 = (
    *PERSEPHONE_SPELLS_0,
    ("Voice of the Leucrota", "MuIm", 4),
    ("Aura of Childlike Innocence", "MuIm", 10),
    ("My Old and Dear Friend", "MuMe", 20),
    ("I Was Never Here", "PeMe", 5),
    ("Opening the Intangible Tunnel", "ReVi", 20),
)
PERSEPHONE_SPELLS_30 = (
    *PERSEPHONE_SPELLS_15,
    ("Remake the Tailor's Craft", "MuAn", 15),
    ("Trigger the Distant Power", "CrIm", 5),
    ("Summoning the Distant Image", "InIm", 25),
    ("The Factor's Roll Call", "InMe", 20),
    ("Funding the Blackmailer's Purse", "InMe", 30),
)
PERSEPHONE_SPELLS_45 = (
    *PERSEPHONE_SPELLS_30,
    ("Catching the Eye", "CrMe", 15),
    ("Music of the Unwanted Attention", "InMe", 25),
    ("Short Step of the Ghost", "MuTe(Au)", 25),
    ("Invisible Hand of the Thief", "ReTe", 20),
)
PERSEPHONE_MASTERIES_0: dict[str, str] = {}
PERSEPHONE_MASTERIES = {
    "My Old and Dear Friend": "Quiet Casting",
    "Confusion of the Numbed Will": "Fast Casting",
}

PERSEPHONE_RULES = {
    "Remake the Tailor's Craft": (
        "Touch, Sun, Group. Reshapes a set of mostly animal-stuff clothes, "
        "keeping substance and colour, though the number of garments may "
        "change; Intelligence + Finesse Ease Factor 6, 9 if very different. "
        "Plant parts need a Herbam requisite, purely plant clothes cannot "
        "be changed, and fastenings stay. (Base 2, +1 Touch, +2 Sun, +2 "
        "Group)"
    ),
    "Trigger the Distant Power": (
        "Arcane Connection, Momentary, Individual. Sounds a chosen noise, "
        "never a voice or words, near what she has a connection to; she "
        "sets off charged items held by agents with a whine, buzz or "
        "chirrup that passes for an insect. (Base 1, +4 Arc)"
    ),
    "Voice of the Leucrota": (
        "Touch, Sun, Individual. Changes the voice wholly, to a known "
        "person's, an accent heard, or just a different one, without "
        "granting languages; Intelligence + Finesse Ease Factor 6 for an "
        "accent, 9 for a voice. She uses it to humiliate those she beats at "
        "certamen. (Base 1, +1 Touch, +2 Sun)"
    ),
    "Aura of Childlike Innocence": (
        "Touch, Sun, Individual. As Aura of Ennobled Presence, for seeming "
        "guileless: +3 to deflect suspicion or convince of innocence, though "
        "to those feeling the Gift it reads as sanctimony (first printed in "
        "Houses of Hermes: Societates page 96). (Base 3, +1 Touch, +2 Sun)"
    ),
    "Catching the Eye": (
        "Sight, Momentary, Individual. Draws the target's eye, to follow "
        "with a Range: Eye spell, which suits her Quiet and Subtle Magic "
        "better than Voice. (Base 4, +3 Sight)"
    ),
    "The Factor's Roll Call": (
        "Eye, Momentary, Individual. Shows if the target ever heard a given "
        "word. Her factors say an obscure one, usually shibboleth, to "
        "recruits, so she can tell her agents and whether she has been "
        "exposed. (Base 15, +1 Eye)"
    ),
    "Music of the Unwanted Attention": (
        "Personal, Momentary, Hearing. Anyone now actively aware of her "
        "sounds as a chime, each their own tone, with no more detail; it "
        "searches the common sense (Art & Academe page 33) for her image. "
        "(Base 10, +3 Hearing)"
    ),
    "Funding the Blackmailer's Purse": (
        "Eye, Momentary, Individual. Given some hint of its subject, reveals "
        "a deep secret in full; it cannot fish at random. If a grog flinches "
        "at a word, the spell can show the old theft behind it and where the "
        "loot lies. (Base 25, +1 Eye)"
    ),
    "My Old and Dear Friend": (
        "Eye, Sun, Individual. The target recalls her doing him a major "
        "recent favour, in a guise she picks, and cannot be talked out of "
        "it until the spell ends, when he sees the deception. (Base 4, +1 "
        "Eye, +2 Sun, +1 complexity)"
    ),
    "I Was Never Here": (
        "Eye, Momentary, Individual. The target forgets meeting her, if any "
        "contact was brief, trivial and within a day: an overt spell or a "
        "gate let pass, but not who stabbed him. (Base 4, +1 Eye)"
    ),
    "Short Step of the Ghost": (
        "Touch, Momentary, Part. A door-sized part of a wall up to a foot "
        "thick turns for a moment as permeable as mist, then solidifies, "
        "without harm to the wall. (Base 10, +1 Touch, +1 Part, +1 affect "
        "stone)"
    ),
    "Invisible Hand of the Thief": (
        "Voice, Momentary, Individual. Brings a visible object within range "
        "instantly to her hand, even held or worn. Other materials may need "
        "requisites, and an item under Magic Resistance needs Penetration. "
        "Instant transport follows the Rego Corpus steps. (Base 4, +2 "
        "Voice, +1 restrained, +1 for 50 paces)"
    ),
}

PERSEPHONE_GUIDELINE = (
    "New Terram guideline, ReTe level 4: move a target instantly up to five "
    "paces; +1 magnitude for 50 paces, +2 for 500, +3 for a league, +4 for "
    "seven leagues, +5 to a place with an Arcane Connection."
)
PERSEPHONE_LOOK_HAIR = (
    "She keeps her long russet hair unbound and uncovered, as unmarried "
    "women do, and dresses simply, in a woollen dress and kirtle with a "
    "leather bodice."
)
PERSEPHONE_LOOK_COIF = (
    "She keeps her long russet hair in a crespine, a net fixed to the back "
    "of her coif, and dresses simply, in a woollen dress and kirtle with a "
    "leather bodice."
)
PERSEPHONE_SIGIL = (
    "Casting sigil: doubling; targets sometimes bear a ghostly after-effect, "
    "shadow or echo. Voting sigil: a silver bracelet set with an onyx."
)
PERSEPHONE_COMBAT = "Combat: dodge Init 0, Defense 0. Soak +1. Encumbrance 0."
PERSEPHONE_COINS = (
    "Coin of Mirth: charged items in the form of a low coin of the realm, "
    "passed to unknowing dupes for street food or trinkets and set off "
    "together with Trigger the Distant Power; two or three people bursting "
    "out laughing cover her vulgar magic. Touch of Hilarity (CrMe 10, Pen "
    "0, charged, Touch, Diameter, Individual), usually triggered by a "
    "chuckling sound (Base 4, +1 Touch, +1 Diam)."
)
PERSEPHONE_BRACELET = (
    "Bracelet of Clandestine Insignificance: a simple silver bangle, a "
    "lesser enchantment of two pawns. Hiding in Plain Sight (MuIm 14, Pen 0, "
    "24/day, Touch, Conc, Individual): species shed turn anamorphic, so "
    "while the wearer acts harmlessly and draws no notice, attention glides "
    "off her; speaking to someone ends it for them. The viewer rolls "
    "Perception -3 (two senses) against a die + his Inattentive or similar "
    "Trait + the wielder's Perception + her Finesse, and must beat it by 3 "
    "to see through it (Houses of Hermes: Societates pages 65-66). She "
    "avoids wearing it near magi, who could charge her with scrying (Base "
    "2, +1 Touch, +1 Conc; +5 maintains, +5 24/day)."
)
PERSEPHONE_SIGNET = paragraphs(
    "Signet of Hallam: a gold ring with an onyx seal, opened with 12 pawns, "
    "11 of effects in the end. It disguises the wearer as Lord Richard of "
    "Hallam, once a close friend of her covenant, whose sudden death would "
    "have lost it an ally; after covering his absence she made the ring so "
    "anyone could play him. Rubbed with the words vir Hallamus or mulier "
    "Hallamae (the second for women, adding the last change), each effect "
    "starts in turn, one a round. All Touch, Pen 0, and cancellable at "
    "will.",
    "Face of Lord Richard (MuCo 16, 2/day, Conc, Part): black hair, green "
    "eyes, clean shaven, like Disguise of the New Visage (Base 3, +1 Touch, "
    "+1 Conc, +1 Part; +1 2/day, +5 maintains). Voice of Lord Richard (MuIm "
    "9, 2/day, Conc, Individual): deep, with a distinct Norman accent, like "
    "Voice of the Leucrota (Base 1, +1 Touch, +1 Conc; +1 2/day, +5 "
    "maintains). Clothes of Lord Richard (MuAn(He) 16, 2/day, Conc, Group): "
    "black wool doublet and hose worked with red, white linen shirt, riding "
    "boots and cape, felt hat with a red feather, gloves, like Remake the "
    "Tailor's Craft (Base 2, +1 Touch, +1 Conc, +2 Group; +1 2/day, +5 "
    "maintains). Body of the Virile Male (MuCo 11, 2/day, Conc, Individual): "
    "male form only, with mulier Hallamae (Base 3, +1 Touch, +1 Conc; +1 "
    "2/day, +5 maintains). Masking the Odor of Magic (PeVi 34, constant, "
    "Sun, Group): hides the ring's effects from Intellego Vim up to level "
    "30 and Magic Sensitivity below 6, added after a churchman with that "
    "Ability made trouble (Base effect 5, +1 Touch, +2 Sun, +2 Group; +1 "
    "2/day, +3 environmental).",
)
PERSEPHONE_AMULET = (
    "Pigeon Amulet: a brass coin stamped with a bird and holed for a thong, "
    "made as a pair from one batch; she keeps one half, neatly labelled on "
    "her wall, as an Arcane Connection to the other for years, and gives "
    "the charged half to possible agents or skilled operatives. Take Me "
    "Home (ReMe 25, Pen 0, charged, Touch, Moon, Individual): a nagging urge "
    "to go to a place set at making, which in about a week usually moves "
    "them; typically triggered by a bee's buzz through Trigger the Distant "
    "Power (Base 5, +1 Touch, +3 Moon)."
)
PERSEPHONE_TALISMAN = paragraphs(
    "Talisman, Amor Sororis: a plain gold ring wound with seven of Kore's "
    "hairs, a fixed Arcane Connection, opened with 10 pawns, with one "
    "pawn's space left. Attunements: +4 transform self, +4 protect self, "
    "+4 nobility. All Pen 0.",
    "Repulse the Unwanted Attention (ReCo 30, 24/day, Personal, Conc, "
    "Individual): a ward against those without Magic Resistance; crowds "
    "part and blows go wide, though missiles do not; palm held out (Base "
    "15, +1 Conc; +5 maintains, +5 24/day). Watchful Eye of the Caring "
    "Sister (InCo 25, unlimited, Arc, Momentary, Individual): general health "
    "of one she has a connection to; ring turned three times clockwise "
    "(Base 4, +4 Arc; +10 unlimited). Opening the Intangible Tunnel (ReVi "
    "25, 1/day, Arc, Conc, Individual): as the spell, with the ring holding "
    "the concentration, spells up to level 20 going through, usually to "
    "Kore; ring moved from the left ring finger to the middle finger (Base "
    "effect, +4 Arc, +1 Conc; +5 maintains).",
    "Fides Sororis, its twin of the same gold, wound with seven of her "
    "hairs, opened with 10 pawns, 5 used, given to Kore. Repulse the "
    "Unwanted Attention (ReCo 35, Pen 0, 24/day, Touch, Conc, Individual), "
    "as hers at Touch (Base 15, +1 Touch, +1 Conc; +5 maintains, +5 24/day). "
    "Adopt the Sister's Face (MuCo(Vi) 25, Pen 0, 24/day, Touch, Conc, "
    "Part): kissing it gives Persephone's present face, by the hair; the "
    "Vim taint seems to show The Gift to magical investigation, and the "
    "wearer has the Magical Air Flaw meanwhile (Base 3, +1 Touch, +1 Conc, "
    "+1 Part, +1 requisite; +5 maintains, +5 24/day).",
)
KORE_BASE = paragraphs(
    "Companion: Kore (Marie-Philipe), her elder sister, an inch taller and "
    "as russet-haired, burned down the left of her body so that her face "
    "sets in a sneer. Her hands shake, so she crosses them tightly on her "
    "chest, and she goes in a hooded dark wool cloak. Int +3, Per 0, Pre "
    "+3, Com -3, Str +1, Sta +1, Dex -1, Qik 0. Size 0. Confidence 1 (3). "
    "Virtues and Flaws: Wise One; Entrancement, Hex (Realms of Power: The "
    "Infernal page 85); Arcane Lore, Strong Willed, True Love (sister); "
    "Enemy, Hatred; Disfigured, Offensive to Animals, Palsied Hands, "
    "Reclusive. Traits: Wrathful +3, Ruthless +3, Devoted to Sister +2, "
    "Secretive +1. Knife Init 0, Attack +4, Defense +4, Damage +3. Soak +1.",
)
KORE_0 = (
    "Kore at Persephone's Gauntlet: age 24 (24), Decrepitude 0, Warping 0. "
    "Artes Liberales 2 (grammar), Brawl 3 (knife), Chirurgy 2 (on sister), "
    "Entrancement 4 (men), Folk Ken 2 (magi), French 5 (Norman), Guile 2 "
    "(to magi), Hex 4 (sudden fires), Infernal Lore 3 (curses), Latin 3 "
    "(Hermetic), Leadership 2 (agents), Magic Lore 3 (fire spirits), Magic "
    "Theory 3 (spells), Order of Hermes Lore 2 (local tribunal), Penetration "
    "2 (Hex), Profession: Apothecary 3 (poisons), Stealth 1 (avoiding "
    "attention). No equipment."
)
KORE_15 = (
    "Kore +15: age 39 (38), Decrepitude 0, Warping 1 (4), adds Compulsion "
    "(hand washing) from Warping. Artes Liberales 2 (grammar), Awareness 2 "
    "(people hiding), Brawl 4 (knife), Chirurgy 2 (on sister), Entrancement "
    "5 (men), Folk Ken 2 (magi), French 5 (Norman), Guile 3 (to magi), Hex "
    "5 (sudden fires), Infernal Lore 4 (curses), Intrigue 2 (magi), Latin 3 "
    "(10) (Hermetic), Leadership 3 (agents), Magic Lore 4 (fire spirits), "
    "Magic Theory 3 (spells), Order of Hermes Lore 2 (local tribunal), "
    "Penetration 3 (Hex), Profession: Apothecary 4 (poisons), Stealth 3 "
    "(avoiding attention)."
)
KORE_30 = (
    "Kore +30: age 54 (51), Pre +3 (2), Str +1 (1), Dex -1 (1), Decrepitude "
    "0 (4), Warping 2 (6), Compulsion (hand washing) from Warping. Area "
    "Lore 1 (around covenant), Artes Liberales 2 (grammar), Awareness 2 "
    "(people hiding), Brawl 4 (knife), Chirurgy 3 (on sister), Church Lore "
    "1 (corrupt priests), Entrancement 5 (5) (men), Folk Ken 3 (magi), "
    "French 5 (Norman), Guile 4 (to magi), Hex 7 (sudden fires), Infernal "
    "Lore 4 (curses), Intrigue 3 (magi), Latin 4 (Hermetic), Leadership 4 "
    "(agents), Magic Lore 4 (fire spirits), Magic Theory 3 (spells), Order "
    "of Hermes Lore 3 (local tribunal), Penetration 4 (Hex), Profession: "
    "Apothecary 4 (poisons), Stealth 3 (avoiding attention)."
)
KORE_45 = (
    "Kore +45: age 69 (62), Int +3 (2), Per -1 (1), Pre +3 (2), Str +1 (1), "
    "Dex -2, Decrepitude 1 (4), Warping 3 (3), from Warping Compulsion "
    "(hand washing) and Lesser Malediction (plants wither near her). Area "
    "Lore 2 (around covenant), Artes Liberales 3 (grammar), Awareness 2 "
    "(people hiding), Brawl 4 (knife), Chirurgy 3 (on sister), Church Lore "
    "2 (corrupt priests), Entrancement 7 (men), Folk Ken 3 (magi), French 5 "
    "(Norman), Guile 4 (to magi), Hex 8 (sudden fires), Infernal Lore 5 "
    "(curses), Intrigue 4 (magi), Latin 4 (Hermetic), Leadership 4 (agents), "
    "Magic Lore 5 (fire spirits), Magic Theory 4 (spells), Order of Hermes "
    "Lore 3 (local tribunal), Penetration 4 (Hex), Profession: Apothecary 4 "
    "(poisons), Stealth 3 (avoiding attention)."
)


def _persephone(
    column: int,
    age: int,
    apparent: int,
    arts: str,
    notes: str,
    **extra: Any,
) -> Printing:
    rows = (
        PERSEPHONE_SPELLS_0,
        PERSEPHONE_SPELLS_15,
        PERSEPHONE_SPELLS_30,
        PERSEPHONE_SPELLS_45,
    )[column]
    block: StatBlock = {
        "apparent_age": apparent,
        "traits": {"Devoted to Sister": 3, "Vengeful": 3, "Flirt": 1},
        "abilities": _abilities(PERSEPHONE_ABILITIES, column),
        "arts": arts_from(arts),
        **_spells(rows, PERSEPHONE_MASTERIES if column else PERSEPHONE_MASTERIES_0),
        "notes": paragraphs(notes, _spell_notes(rows, PERSEPHONE_RULES)),
        **extra,
    }
    label = ("Gauntlet", "+15", "+30", "+45")[column]
    return Printing(label, age, block)


PERSEPHONE = Magus(
    name="Persephone of Tytalus",
    house="house_tytalus",
    summary=paragraphs(
        "Marie-Helene and her elder sister Marie-Philipe came from a "
        "village near a covenant. A Tytalus magus took the younger as "
        "apprentice and refused the other, who had only a latent knack and "
        "no Gift. Soon a terrible fire struck the family home and scarred "
        "Marie-Philipe; Marie-Helene, sure her master set it to rid her of "
        "a distraction, hid her sister, slipping out by night with food and "
        "lessons, though the elder could work no spell. At her Gauntlet she "
        "took the name Persephone of Tytalus, and her sister Kore. They "
        "swore a fiery end for him: plain revenge, nothing to do with the "
        "House's beloved rivals. Kore keeps to the shadows nearby, hiding "
        "her face.",
        "Persephone runs a network of agents who mostly do not know whom "
        "they serve, reached through go-betweens or in disguise. They are "
        "chiefly spies, whose reports Kore sifts. Her spells and "
        "enchantments serve the network, and her plans have drifted from "
        "revenge to general meddling in her Tribunal's politics. Her "
        "covenant goes on impersonating the dead Lord Richard of Hallam with "
        "her ring, which it uses only to protect its interests; she is less "
        "careful when she wears the disguise. His widow Joanna knows and is "
        "glad, preferring it to the dull second husband her family would "
        "find her.",
        "She rarely keeps an agent long for fear of double agents (Houses "
        "of Hermes: Societates pages 140-144). Typical ones, each with the "
        "Trait that binds them: Macco, a novice scribe at a rival covenant "
        "(Fear of Discovery +1); Sir Stephene, a wealthy knight and secret "
        "lycanthrope promised a cure (Hopeful of a Cure +3); Pierre, a "
        "journeyman with a guildmaster as mentor in a distant shoemakers' "
        "guild (Ambitious +1); Jack, a well-travelled peddler of penny "
        "cures full of local gossip (Avaricious +1); Claude, the sisters' "
        "cousin, a nobleman's trusted man-at-arms who can lend his men "
        "(Loyal to Sisters +3); Sister Maurisse, a mendicant nun who thinks "
        "the sisters need protection (Pity +2).",
    ),
    secrets=(
        "Kore hates the pater more fiercely than Persephone does: Persephone's "
        "resentment is considered, Kore's visceral. Thinking her sister "
        "distracted by being a maga, she has taken up the vendetta herself. "
        "Without Persephone's knowledge, mundane agents, sometimes with "
        "stolen magical devices, watch him always; she has struck at him in "
        "secret with Hex, and holds one of his lesser enchantments, knowing "
        "it to be an Arcane Connection. She covers her tracks with great "
        "care, knowing the danger to her sister, who can truthfully tell "
        "Quaesitores she knows nothing."
    ),
    printings=(
        _persephone(
            0,
            21,
            21,
            "Cr 0, In 6, Mu 8, Pe 2, Re 4, An 2, Aq 1, Au 2, Co 3, He 2, Ig 2, "
            "Im 4, Me 7+3, Te 5, Vi 3",
            paragraphs(
                f"A pretty young girl with a beguiling smile. {PERSEPHONE_LOOK_HAIR}",
                PERSEPHONE_SIGIL,
                PERSEPHONE_COMBAT,
                f"{KORE_BASE}\n\n{KORE_0}",
            ),
            characteristics=characteristics(2, -1, 3, 2, -1, 1, -1, 0),
            confidence=(2, 6),
            virtues_flaws=_persephone_vf("defeat master"),
        ),
        _persephone(
            1,
            36,
            36,
            "Cr 4, In 8, Mu 12, Pe 7, Re 8, An 6, Aq 3, Au 5, Co 5, He 5, Ig 4, "
            "Im 7, Me 10+3, Te 8, Vi 7",
            paragraphs(
                f"A beautiful mature woman with a beguiling smile. "
                f"{PERSEPHONE_LOOK_HAIR}",
                PERSEPHONE_SIGIL,
                "Twilight scar: her eyes shine faintly green in the dark.",
                f"{PERSEPHONE_COMBAT} Equipment: Coins of Mirth (0 to 13, as "
                "she has handed them out), Bracelet of Clandestine "
                "Insignificance.",
                "Last 15 years: six Coins of Mirth at first, seven more from "
                "the Lab Text; a season on the Bracelet; then she opened the "
                "Signet of Hallam and instilled its first effect, in "
                "exchange for which her covenant made longevity rituals for "
                "her and Kore. 159 xp in Abilities, 59 levels of spells, and "
                "192 xp in Arts; Secondary Insight, taking source quality "
                "8, adds 40 in Forms and 26 in Techniques. She has 3 xp past "
                "her Auram score, 10 past Magic Theory and 4 past Parma "
                "Magica.",
                PERSEPHONE_COINS,
                PERSEPHONE_BRACELET,
                PERSEPHONE_SIGNET,
                f"{KORE_BASE}\n\n{KORE_15}",
            ),
            characteristics=characteristics(2, -1, 3, 2, -1, 1, -1, 0),
            confidence=(2, 6),
            warping=(2, 13),
            virtues_flaws=_persephone_vf("best master"),
        ),
        _persephone(
            2,
            51,
            40,
            "Cr 5, In 10, Mu 14, Pe 10, Re 10, An 7, Aq 5, Au 8, Co 6, He 6, "
            "Ig 5, Im 9, Me 12+3, Te 10, Vi 8",
            paragraphs(
                f"A beautiful mature woman with a beguiling smile. "
                f"{PERSEPHONE_LOOK_COIF}",
                PERSEPHONE_SIGIL,
                "Twilight scars: her eyes shine faintly green in the dark; "
                "her clothes darken through the day and lighten by night; "
                "all ale within 3 paces turns to water.",
                f"{PERSEPHONE_COMBAT} Equipment: Coins of Mirth (0 to 13), "
                "Bracelet of Clandestine Insignificance, Pigeon Amulets (0 "
                "to 2).",
                "Her Warping Score is printed 3 (45), and points past 3 "
                "cannot pass 19, so the sheet holds 3 (15): the book's 45 "
                "reads as her total.",
                "Last 15 years: three seasons on three more Signet effects; "
                "two Pigeon Amulets; she began an apprentice, four seasons "
                "so far. 71 xp in Abilities, 95 levels of spells, 224 xp in "
                "Arts; Secondary Insight adds 32 in Forms and 26 in "
                "Techniques. She has 5 xp past her Muto score and 5 past "
                "Imaginem.",
                PERSEPHONE_COINS,
                PERSEPHONE_BRACELET,
                PERSEPHONE_SIGNET,
                PERSEPHONE_AMULET,
                f"{KORE_BASE}\n\n{KORE_30}",
            ),
            characteristics=characteristics(2, -1, 3, 2, -1, 1, -1, -1),
            aging_points={"presence": 1, "strength": 1, "dexterity": 1},
            confidence=(2, 6),
            decrepitude=(0, 4),
            warping=(3, 15),
            virtues_flaws=_persephone_vf("best master"),
        ),
        _persephone(
            3,
            66,
            52,
            "Cr 5, In 10, Mu 16, Pe 11, Re 12, An 8, Aq 6, Au 9, Co 9, He 7, "
            "Ig 5, Im 11, Me 13+3, Te 11, Vi 9",
            paragraphs(
                f"A beautiful older woman with a beguiling smile. "
                f"{PERSEPHONE_LOOK_COIF}",
                PERSEPHONE_SIGIL,
                "Twilight scars: her eyes shine faintly green in the dark; "
                "her clothes darken through the day and lighten by night; "
                "all ale within 3 paces turns to water; her hair ripples "
                "like water; her fingers spark when she casts.",
                f"{PERSEPHONE_COMBAT} Equipment: Coins of Mirth (0 to 13), "
                "Bracelet of Clandestine Insignificance, Pigeon Amulets (0 "
                "to 10), Amor Sororis.",
                "Her Warping Score is printed 4 (70), and points past 4 "
                "cannot pass 24, so the sheet holds 4 (20): the book's 70 "
                "reads as her total.",
                "Last 15 years: 11 seasons finishing her apprentice; the "
                "last Signet effect; eight more Pigeon Amulets from her "
                "text; five seasons on her talisman; three on a twinned "
                "item for Kore. 85 levels of spells, four seasons in all "
                "with her Arts so advanced, and a season on Invisible Hand "
                "of the Thief from a bought text. 85 xp in Abilities, 165 in "
                "Arts; Secondary Insight adds 24 in Forms and 22 in "
                "Techniques. She has 2 xp past her Perdo score.",
                PERSEPHONE_COINS,
                PERSEPHONE_BRACELET,
                PERSEPHONE_SIGNET,
                PERSEPHONE_AMULET,
                PERSEPHONE_TALISMAN,
                PERSEPHONE_GUIDELINE,
                f"{KORE_BASE}\n\n{KORE_45}",
            ),
            characteristics=characteristics(2, -1, 3, 2, -1, 1, -1, -1),
            aging_points={
                "presence": 1,
                "communication": 1,
                "strength": 1,
                "dexterity": 1,
            },
            confidence=(3, 9),
            decrepitude=(1, 0),
            warping=(4, 20),
            virtues_flaws=_persephone_vf("best master"),
        ),
    ),
)

MAGI: tuple[Magus, ...] = (JULIA, LAMBERT, MARIS, MARCUS, PERSEPHONE)
