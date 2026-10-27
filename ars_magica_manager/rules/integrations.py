"""The integration breakthroughs the books name: Hermetic research goals
that fold a lost or living non-Hermetic tradition into Hermetic magic.

Each is a ready-made research goal (Breakthrough): its kind, the points
the book gives (the kind's usual target when it gives none), and what
reaching it grants. Points from insight and from stabilized Discoveries
add into the same goal (rules.experiment).

Rules: reference/rules-engine-reference.md §18, Ancient Magic:
integrating a lost tradition and the breakthroughs summary; Hedge Magic
RE's integrations whose Virtue is in the catalog; True Lineages' example
discoveries of House Bonisagus. A breakthrough's size is the Definitive
Edition's: about 30 points for a Minor, 45 for a Major, 60 for a Hermetic
(DE, Arcane Discovery: The Breakthrough, p. 277; True Lineages p. 28 gives
the same rule of thumb).
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import catalog

SOURCE = (
    "Ancient Magic, Introduction, The Breakthrough (p. 7); Hedge Magic, Revised "
    "Edition, The Integration Process (p. 14); Houses of Hermes: True Lineages, "
    "Bonisagus, Example Discoveries (pp. 30-34); Magi of Hermes, Aurulentus "
    "(p. 20) and Marcus (pp. 82-83); Legends of Hermes, Hérisson (pp. 72-73); "
    "The Cradle and the Crescent, Integration (pp. 44-45)"
)
AM = "Ancient Magic"
HMRE = "Hedge Magic, Revised Edition"
TL = "Houses of Hermes: True Lineages"
MOH = "Magi of Hermes"
LOH = "Legends of Hermes"
TCTC = "The Cradle and the Crescent"
ML = "Mythic Locations"


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
    #: What the magus can then do, where the app works it out
    #: (rules.house_discoveries, casting_virtues' reminders).
    learned: str = ""

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
        "Aetheric Magic",
        "Hermetic",
        100,
        "The Major Hermetic Virtue Aetheric Magic and the Art Aether at 13 "
        "(9 xp toward 14); at least 20 of the points must come from each "
        "Technique's projects (Dies Irae pp. 38-39).",
        "Dies Irae",
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
        learned="Double Parma, worn down by each Penetration it stops; one of as many folds as Parma Magica.",
    ),
    Integration(
        "Arma Magica: Parma Absorbea",
        "Major",
        45,
        "A fold of the Parma Magica: Half Parma Magica; a resisted spell's Penetration feeds the next spell.",
        TL,
        learned="Half Parma; a stopped spell's Penetration may feed the next spell; one of as many folds as Parma Magica.",
    ),
    Integration(
        "Arma Magica: Parma Condensa",
        "Major",
        45,
        "A fold of the Parma Magica: Double Parma Magica against one Form, half against the rest.",
        TL,
        learned="Double Parma against one Form, half against the rest; one of as many folds as Parma Magica.",
    ),
    Integration(
        "Arma Magica: Parma Custodia",
        "Major",
        45,
        "A fold of the Parma Magica: Twice Parma Magica added to Defense, no Magic Resistance.",
        TL,
        learned="Twice Parma added to Defense, no Parma resistance; one of as many folds as Parma Magica.",
    ),
    Integration(
        "Arma Magica: Parma Repercussa",
        "Major",
        45,
        "A fold of the Parma Magica: Half Parma Magica; a spell it stops is reflected at a target.",
        TL,
        learned="Half Parma; a stopped spell is turned at a target; one of as many folds as Parma Magica.",
    ),
    Integration(
        "Arma Magica: Parma Restricta",
        "Major",
        45,
        "A fold of the Parma Magica: Parma Magica - 3, wrapped around another to hold their magic in.",
        TL,
        learned="Parma - 3 wrapped round someone touched, holding their magic in; one of as many folds as Parma Magica.",
    ),
    Integration(
        "Parmulae",
        "Minor",
        30,
        "Lesser enchanted 'little shields' giving Magic Resistance 30 for a year.",
        TL,
        learned="Parmulae: a level 44 lesser device, Magic Resistance 30 for a year, 5 pawns.",
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
        learned="Realm-aligned spells: invented with Magic Theory capped by the Realm Lore; the casting notes give the aligned table.",
    ),
    Integration(
        "Realm-aligned mastery",
        "Minor",
        30,
        "Realm alignment as a special ability of a mastered spell.",
        TL,
        learned="Realm alignment as a Mastery special ability.",
    ),
    # Magi of Hermes and Legends of Hermes: the breakthroughs their magi
    # reached (rules.breakthroughs_moh, rules.viresculture). The books give
    # no points; each takes its kind's usual target.
    Integration(
        "Fertile Longevity Ritual",
        "Minor",
        30,
        "Longevity Rituals that leave their subject fertile (Aurulentus' "
        "breakthrough, p. 20).",
        MOH,
        learned="Longevity Rituals that leave their subject fertile, where "
        "every other leaves him sterile (DE p. 261).",
    ),
    Integration(
        "Hermetic Metamorphosis",
        "Major",
        45,
        "The Minor Hermetic Virtue Hermetic Metamorphosis: organs grafted onto "
        "an animal by a ritual only its holder can cast (Marcus' research, "
        "pp. 82-83).",
        MOH,
        "Virtue",
        "vf_hermetic_metamorphosis",
        learned="Harmonic Metamorphosis of the Beast; its surgery is Dexterity + "
        "Chirurgy against 9, +3 for an organ added, +3 to give a Virtue. "
        "Human recipients need a further breakthrough.",
    ),
    Integration(
        "Hermetic Viresculture",
        "Major",
        45,
        "The Supernatural Ability Hermetic Viresculture: Stirpes of "
        "self-reproducing vis bred from magical creatures and plants "
        "(Hérisson's breakthrough, pp. 72-75).",
        LOH,
        "Ability",
        "Hermetic Viresculture",
        learned="Vitalize and Invigorate Stirpes as lab seasons; tend at most "
        "the score in Stirpes, 12 Labor Points a year each.",
    ),
    Integration(
        "Viresculture of Lesser Enchantment Vis",
        "Minor",
        30,
        "Living Lesser Enchantment Vis made a Stirps, its effect's level "
        "standing for Magic Might (Hérisson's second breakthrough, p. 73).",
        LOH,
        learned="Builds on Hermetic Viresculture: Lesser Enchantment Vis may be "
        "Vitalized at its effect's level; its power is lost if transferred out.",
    ),
    # The Cradle and the Crescent, Integration (pp. 44-45): Solomonic magic
    # folded into Hermetic magic. The book gives no points; each takes its
    # kind's usual target. The sahirs' own are in rules.learned_magic.
    Integration(
        "Hermetic True Names",
        "Minor",
        30,
        "An Arcane Connection made a permanent part of a formulaic spell: no "
        "object needed, and the permanent Connection's Penetration multiplier "
        "(The Cradle and the Crescent pp. 44-45).",
        TCTC,
        learned="Spells with a built-in Arcane Connection, at the Indefinitely "
        "multiplier (+4); the spell and its Connection can be taught or put in "
        "a lab text.",
    ),
    Integration(
        "Scientates Suleimanis",
        "Hermetic",
        60,
        "The Major Hermetic Virtue Scientates Suleimanis: Rego spells on the "
        "non-Ritual Solomonic guidelines, as craft magic (pp. 44-45).",
        TCTC,
        "Virtue",
        "vf_scientates_suleimanis",
        learned="Any Solomonic formulaic spell as Rego with the target's Form, "
        "even those past the Limit of Energy.",
    ),
    Integration(
        "Hermetic Realm Initiation",
        "Hermetic",
        60,
        "The Major Hermetic Virtue Hermetic Realm Initiation: initiating "
        "others as sahirs do, by a Rego Vim Lab Total (pp. 44-45).",
        TCTC,
        "Virtue",
        "vf_hermetic_realm_initiation",
        learned="Initiation into Virtues by a spirit's journey to the Magic "
        "Realm: Rego Vim Lab Total for Solomonic Travel, Magic Theory for Magic "
        "Lore; vis, the spirit's Might and the student's Warping as the sahirs'.",
    ),
    # Mythic Locations, The Temple of Mercury (pp. 100-101): the guidelines
    # behind the recovered Mercurian rituals (rules.mythic_locations). The
    # book gives the points; the kind follows the Definitive Edition's
    # sizes, about 30 Minor, 45 Major, 60 Hermetic (DE, Arcane Discovery:
    # The Breakthrough, p. 277; True Lineages p. 28 gives the same). A
    # guideline grants nothing the app tracks: the troupe adds the spells
    # it allows.
    Integration(
        "Mercurian aura creation",
        "Minor",
        30,
        "A CrVi 50 Ritual guideline creating a Magic aura of 1 (Touch, "
        "Momentary, Room base; Room, Structure or Boundary only) "
        "(Mythic Locations p. 100).",
        ML,
    ),
    Integration(
        "Mercurian aura raising",
        "Minor",
        30,
        "A CrVi 55 Ritual guideline raising a Magic aura by 1 to at most 2, "
        "each further magnitude one higher, never past 10 (Mythic Locations "
        "p. 100).",
        ML,
    ),
    Integration(
        "Mercurian regio entrance",
        "Minor",
        30,
        "A Cr(Re)Vi 20 guideline opening an entrance into a Magic regio, cast "
        "at a boundary the caster senses (Mythic Locations p. 100).",
        ML,
    ),
    Integration(
        "Mercurian Magic",
        "Major",
        45,
        "The Mercurian rituals integrated into the Major Hermetic Virtue "
        "Mercurian Magic (Mythic Locations p. 100).",
        ML,
        "Virtue",
        "vf_mercurian_magic",
    ),
    Integration(
        "Wizard's Initiation repaired",
        "Hermetic",
        60,
        "A CrVi(Co) 75 Ritual guideline giving a human, Individual target The "
        "Gift: the Mercurian ritual mended for the Age of Pisces (Mythic "
        "Locations p. 101).",
        ML,
    ),
)


# -- Ancient Magic's catalog: the Breakthroughs its chapters add ----------


def _from_ancient_magic_catalog() -> tuple[Integration, ...]:
    """The Breakthroughs ancient_magic_catalog.json describes that the list
    above doesn't (a note with a kind of its own)."""
    return tuple(
        Integration(
            note.name,
            note.kind,
            note.target,
            note.gives,
            AM,
            note.grant_kind,
            note.grant,
            note.learned,
        )
        for chapter in catalog.load_ancient_magic_catalog()
        for note in chapter.integrations
        if note.kind
    )


INTEGRATIONS = (*INTEGRATIONS, *_from_ancient_magic_catalog())

BY_NAME: dict[str, Integration] = {i.name: i for i in INTEGRATIONS}
