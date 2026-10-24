"""The integration breakthroughs the books name: Hermetic research goals
that fold a lost or living non-Hermetic tradition into Hermetic magic.

Each is a ready-made research goal (Breakthrough): its kind, the points
the book gives (the kind's usual target when it gives none), and what
reaching it grants. Points from insight and from stabilized Discoveries
add into the same goal (rules.experiment).

Rules: reference/rules-engine-reference.md §18, Ancient Magic:
integrating a lost tradition and the breakthroughs summary; Hedge Magic
RE's integrations whose Virtue is in the catalog; True Lineages' example
discoveries of House Bonisagus (its rule of thumb: 30 points for a Minor
Breakthrough, 45 for a Major).
"""

from __future__ import annotations

from dataclasses import dataclass

SOURCE = (
    "Ancient Magic, Introduction, The Breakthrough (p. 7); Hedge Magic, Revised "
    "Edition, The Integration Process (p. 14); Houses of Hermes: True Lineages, "
    "Bonisagus, Example Discoveries (p. 30)"
)
AM = "Ancient Magic"
HMRE = "Hedge Magic, Revised Edition"
TL = "Houses of Hermes: True Lineages"


@dataclass(frozen=True)
class Integration:
    name: str
    kind: str  # Minor / Major / Hermetic
    target: int
    gives: str
    book: str
    #: What reaching it grants (Breakthrough.grant_kind and grant).
    grant_kind: str = ""
    grant: str = ""

    @property
    def label(self) -> str:
        return f"{self.name} ({self.kind}, {self.target}; {self.book})"


INTEGRATIONS: tuple[Integration, ...] = (
    Integration(
        "Hermetic magic in another language",
        "Minor",
        15,
        "Spells cast in a language other than Latin.",
        AM,
    ),
    Integration(
        "Canaanite Magic",
        "Major",
        45,
        "The Veil of Death range, an Arcane Connection to all the dead and a "
        "+4 Penetration multiplier against them.",
        AM,
        "Virtue",
        "vf_canaanite_magic",
    ),
    Integration(
        "Duration Event",
        "Minor",
        30,
        "A Ritual held until a trigger: +1 magnitude over the Duration of what "
        "it then does.",
        AM,
        "Parameter",
        "Duration: Event",
    ),
    Integration(
        "Range Unlimited",
        "Hermetic",
        60,
        "A Ritual range reaching any target through sympathy alone: Arcane "
        "Connection + 2 magnitudes.",
        AM,
        "Parameter",
        "Range: Unlimited",
    ),
    Integration(
        "Fertility Lore",
        "Minor",
        15,
        "The Arcane Ability Fertility Lore.",
        AM,
        "Ability",
        "Fertility Lore",
    ),
    Integration(
        "Fertility Ritual Magic",
        "Major",
        35,
        "The Fertility Ritual.",
        AM,
        "Virtue",
        "vf_fertility_ritual_magic",
    ),
    Integration(
        "Grigori Legacy",
        "Major",
        45,
        "One Secret of the Grigori made Hermetic, its taint removed "
        "(a breakthrough for each Secret).",
        AM,
        "Virtue",
        "vf_grigori_legacy",
    ),
    Integration("Limit of Vis", "Hermetic", 60, "Any vis may be used for any Art.", AM),
    Integration(
        "Mutable Device",
        "Major",
        45,
        "Enchanted effects that can be swapped for others of the same Arts "
        "(a second 45 points drops the Virtue).",
        AM,
        "Virtue",
        "vf_craft_mutable_device",
    ),
    Integration(
        "Awakened Device",
        "Major",
        45,
        "Devices awakened as magical beings (30 points once Mutable Device is "
        "reached).",
        AM,
        "Virtue",
        "vf_awaken_device",
    ),
    Integration(
        "Vis-less devices",
        "Hermetic",
        60,
        "Breaks the Lesser Limit of Creation: devices made without vis.",
        AM,
    ),
    Integration(
        "Duration 19 Years",
        "Minor",
        30,
        "A duration of nineteen years, Year + 1 magnitude.",
        AM,
        "Parameter",
        "Duration: 19 Years",
    ),
    Integration(
        "Spirit travel",
        "Minor",
        35,
        "The Hyperborean hymnists' spirit travel.",
        AM,
    ),
    Integration(
        "Vis-less permanent magic",
        "Hermetic",
        70,
        "Permanent effects without vis.",
        AM,
    ),
    Integration(
        "Vis-less enchantment",
        "Hermetic",
        65,
        "Enchanting at two Warping Points a pawn instead of vis.",
        AM,
    ),
    Integration(
        "No shape, material or size limits",
        "Hermetic",
        60,
        "Removes the enchantment limits of shape, material and size.",
        AM,
    ),
    Integration(
        "Ritual effects in enchantment",
        "Hermetic",
        65,
        "Ritual effects in enchanted items.",
        AM,
    ),
    Integration(
        "19-Year Aegis", "Major", 45, "The Aegis of the Hearth at 19 Years.", AM
    ),
    Integration(
        "Hermetic Rune Magic",
        "Major",
        45,
        "The Rune duration and Inscription target; natural effects without vis.",
        AM,
        "Virtue",
        "vf_hermetic_rune_magic",
    ),
    Integration(
        "Subtle Opening",
        "Major",
        30,
        "Opening apprentices so that Supernatural Abilities cost them no Arts penalty.",
        HMRE,
        "Virtue",
        "vf_subtle_opening",
    ),
    Integration(
        "Quick Charged Items",
        "Major",
        40,
        "Single-charge items in an hour per magnitude.",
        HMRE,
        "Virtue",
        "vf_quick_charged_items",
    ),
    Integration(
        "Arma Magica: Parma Ablativa",
        "Major",
        45,
        "A fold of the Parma Magica: Double Parma Magica, worn down by each Penetration it stops.",
        TL,
    ),
    Integration(
        "Arma Magica: Parma Absorbea",
        "Major",
        45,
        "A fold of the Parma Magica: Half Parma Magica; a resisted spell's Penetration feeds the next spell.",
        TL,
    ),
    Integration(
        "Arma Magica: Parma Condensa",
        "Major",
        45,
        "A fold of the Parma Magica: Double Parma Magica against one Form, half against the rest.",
        TL,
    ),
    Integration(
        "Arma Magica: Parma Custodia",
        "Major",
        45,
        "A fold of the Parma Magica: Twice Parma Magica added to Defense, no Magic Resistance.",
        TL,
    ),
    Integration(
        "Arma Magica: Parma Repercussa",
        "Major",
        45,
        "A fold of the Parma Magica: Half Parma Magica; a spell it stops is reflected at a target.",
        TL,
    ),
    Integration(
        "Arma Magica: Parma Restricta",
        "Major",
        45,
        "A fold of the Parma Magica: Parma Magica - 3, wrapped around another to hold their magic in.",
        TL,
    ),
    Integration(
        "Parmulae",
        "Minor",
        30,
        "Lesser enchanted 'little shields' giving Magic Resistance 30 for a year.",
        TL,
    ),
    Integration(
        "Figurine Magic",
        "Major",
        45,
        "Wax and wooden figurines holding a Virtue or a Hermetic spell for "
        "their recipient.",
        TL,
        "Virtue",
        "vf_figurine_magic",
    ),
    Integration(
        "Realm-aligned spells",
        "Minor",
        30,
        "Spells untouched by the aura of the Realm they are aligned to.",
        TL,
    ),
    Integration(
        "Realm-aligned mastery",
        "Minor",
        30,
        "Realm alignment as a special ability of a mastered spell.",
        TL,
    ),
)

BY_NAME: dict[str, Integration] = {i.name: i for i in INTEGRATIONS}
