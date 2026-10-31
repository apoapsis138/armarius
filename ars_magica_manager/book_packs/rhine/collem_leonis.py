"""Collem Leonis, a Second Spring covenant of the Rhine Tribunal in the
Sauerland, as of 1220, in paraphrase of Through the Aegis, chapter six:
the covenant, its five magi, its companions and grogs, its charter,
laboratories, devices, library, Lab Texts and vis, the Hidden Resources
its young magi have yet to find, its regiones of Jotunheim and Midgard,
and the lindorm that waits behind the portals.

Stat blocks are the book's; the rest is a summary, not its words. The
lost books stay in the covenant's library, each saying it is lost, with
where it lies under its Secrets heading."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...models import CharterClause
from ...models.books import TEXT_SPELL
from ...models.world import FULL
from ...tribunal_packages import rhine as rhine_package
from ..builder import (
    Builder,
    StatBlock,
    add_possession,
    arts_from,
    boons_hooks_from,
    characteristics,
    joined_lines,
    paragraphs,
    secrets,
    vf_ability,
    vf_art,
    vf_focus,
    vf_puissant,
)

if TYPE_CHECKING:
    from ...models import Covenant, Neighbour
    from . import Rhine

SOURCE = "TtA"
NAME = "Collem Leonis"
BONISAGUS = "house_bonisagus"
BJORNAER = "house_bjornaer"
FLAMBEAU = "house_flambeau"
TREMERE = "house_tremere"

JOURNEYMAN = "Journeyman (Rhine Tribunal)"
MASTER = "Master (Rhine Tribunal)"


def _gild_trained(gild: str) -> tuple[str, dict[str, str]]:
    return ("{gild} Trained", {"gild": f"{gild} Gild"})


def _deficient_form(form: str) -> tuple[str, dict[str, str]]:
    return ("Deficient Form", {"form": form})


def _deficient_technique(art: str) -> tuple[str, dict[str, str]]:
    return ("Deficient Technique", {"art": art})


FERRA: StatBlock = {
    "characteristics": characteristics(3, -2, 0, 0, 0, 2, 0, 1),
    "aging_points": {"intelligence": 3, "stamina": 2, "quickness": 1},
    "confidence": (1, 3),
    "decrepitude": (1, 1),
    "warping": (8, 19),
    "apparent_age": 67,
    "virtues_flaws": [
        "The Gift",
        MASTER,
        "Elemental Magic",
        vf_art("Affinity with {art}", "Mentem"),
        vf_art("Affinity with {art}", "Terram"),
        "Book Learner",
        ("Deft Form", {"form": "Terram"}),
        "Inventive Genius",
        vf_focus("Minor Magical Focus", "ghosts"),
        _gild_trained("Oak"),
        vf_puissant("Magic Theory"),
        vf_art("Puissant {art}", "Terram"),
        "Skilled Parens",
        ("Special Circumstances", {"circumstance": "in the presence of ghosts"}),
        "Ambitious (Major)",
        "Chaotic Magic",
        "Twilight Prone",
        ("Weak Magic Resistance", {"detail": "when not standing on a solid surface"}),
        "Susceptibility to Divine Power",
    ],
    "traits": {"Ambitious": 4, "Advisory": 3, "Tidy": 1, "Intervening": -2},
    "reputations": {"House Bonisagus Acclaim": 3, "Master of Ghosts": 2},
    "abilities": [
        ("Area Lore: Sauerland", 2, "history"),
        ("Artes Liberales", 4, "arithmetic"),
        ("Awareness", 3, "searching"),
        ("Charm", 4, "magi"),
        ("Code of Hermes", 3, "certamen law"),
        ("Concentration", 5, "spells"),
        ("Etiquette", 3, "hermetic"),
        ("Finesse", 3, "Terram"),
        ("Folk Ken", 3, "magi"),
        ("Guile", 2, "lying to underlings"),
        ("Living Language: High German", 5, "giving orders"),
        ("Intrigue", 3, "Hermetic politics"),
        ("Dead Language: Latin", 5, "Hermetic terms"),
        ("Leadership", 3, "running institutions"),
        ("Magic Theory", 8, "Creo"),
        ("Organization Lore: Durenmar", 2, "library"),
        ("Organization Lore: Collem Leonis", 3, "history"),
        ("Organization Lore: Order of Hermes", 5, "necromancers"),
        ("Parma Magica", 5, "Mentem"),
        ("Penetration", 4, "Mentem"),
        ("Philosophiae", 3, "metaphysics"),
        ("Profession: Scribe", 4, "lab texts"),
        ("Teaching", 5, "necromancy"),
    ],
    "arts": arts_from(
        "Cr 8, In 8, Mu 9, Pe 18, Re 14, An 6, Aq 8, Au 10, Co 10, He 6, Ig 10, "
        "Im 6, Me 24, Te 15+3, Vi 10"
    ),
    "spells": [
        ("Wreaths of Foul Smoke", "CrAu", 10, 0),
        ("Charge of the Angry Winds", "CrAu", 15, 0),
        ("Circling Winds of Protection", "CrAu", 20, 0),
        ("Wings of the Soaring Wind", "CrAu", 30, 2),
        ("Sailor's Foretaste of the Morrow", "InAu", 20, 0),
        ("Rain of Stones", "MuAu(Te)", 20, 0),
        ("The Leap of Homecoming", "ReCo", 35, 0),
        ("Pilum of Fire", "CrIg", 20, 2),
        ("Soothe the Raging Flames", "PeIg", 20, 0),
        ("The Call to Slumber", "ReMe", 10, 4),
        ("Coerce the Spirits of the Night", "ReMe", 20, 3),
        ("Incantation of Summoning the Dead", "ReMe", 40, 3),
        ("Voices from Hollow Spaces", "ReMe", 25, 4),
        ("Lay to Rest the Haunting Spirit", "PeMe", 5, 5),
        ("Probe for Pure Silver", "InTe", 4, 0),
        ("The Miner's Keen Eye", "InTe", 20, 0),
        ("Seal the Earth", "CrTe", 15, 0),
        ("Rock of Viscid Clay", "MuTe", 15, 0),
        ("Earth that Breaks No More", "MuTe", 20, 0),
        ("Pit of the Gaping Earth", "PeTe", 15, 0),
        ("The Earth's Carbuncle", "ReTe(Mu)", 15, 0),
        ("The Unseen Porter", "ReTe", 10, 0),
        ("Day of Communion", "MuVi", 20, 0),
        ("Aegis of the Hearth", "ReVi", 20, 0),
    ],
    "masteries": {
        "Wings of the Soaring Wind": ["Fast Casting", "Imperturbable Casting"],
        "Pilum of Fire": ["Multiple Casting", "Penetration"],
        "The Call to Slumber": [
            "Fast Casting",
            "Magic Resistance",
            "Multiple Casting",
            "Penetration",
        ],
        "Coerce the Spirits of the Night": [
            "Imperturbable Casting",
            "Lab Mastery",
            "Penetration",
        ],
        "Incantation of Summoning the Dead": [
            "Imperturbable Casting",
            "Learn from Mistakes",
            "Penetration",
        ],
        "Voices from Hollow Spaces": [
            "Ceremonial Casting",
            "Imperturbable Casting",
            "Learn from Mistakes",
            "Penetration",
        ],
        "Lay to Rest the Haunting Spirit": [
            "Fast Casting",
            "Imperturbable Casting",
            "Multiple Casting",
            "Penetration",
            "Quick Casting",
        ],
    },
    "notes": paragraphs(
        "A kind, pale face under a wrinkled forehead, neat short hair going "
        "from grey to white, thick eyebrows, and eyes clouding with cataracts "
        "that still flash at a new idea; her back has begun to bend. She "
        "wears thick woollen robes and carries a walking stick, parchment, "
        "inkwell and quill.",
        "Gauntleted in 1137; Longevity Ritual of level 50 since 1147. Twilight "
        "gave her Affinity with Mentem, the focus on ghosts, Special "
        "Circumstances and Twilight Prone, so her Virtues and Flaws do not "
        "balance. Twilight scars: her magic drives vermin from hiding; a dry "
        "smell of iron; flames burn brighter and bluer near her; her "
        "reflection shows ghosts hovering over her; thin black swirling "
        "lines cover her left arm; her hair stays short and neatly groomed; "
        "foreign objects float to the top of any liquid she holds.",
        "Combat: dodge Init +1, Defense +1. Soak +2. Encumbrance 0.",
        "Casting Totals as printed: her ghost spells (Coerce the Spirits of "
        "the Night +57, Summoning the Dead +57, Voices from Hollow Spaces "
        "+58, Lay to Rest +67) include the focus. The book lists Sailor's "
        "Foretaste of the Morrow at level 20, where the Definitive Edition "
        "has 15.",
        "The Dominator of Ghosts, her own and not the covenant's: an "
        "invested yew staff set with pieces of human skull and a green "
        "turquoise, opened with 15 pawns, 5 used. Coerce the Spirits of the "
        "Night (ReMe 44, Pen 30, 12 a day, the item keeping concentration), "
        "worked by pointing it, twisting it clockwise and speaking the words "
        "of domination.",
    ),
}

BALIANA: StatBlock = {
    "characteristics": characteristics(2, 1, 1, 1, -1, 1, 0, 1),
    "confidence": (1, 3),
    "apparent_age": 26,
    "virtues_flaws": [
        "The Gift",
        JOURNEYMAN,
        "Comprehend Magic",
        "Flexible Formulaic Magic",
        _gild_trained("Ash"),
        ("Inoffensive to {being}", {"being": "Magic Aligned Beings"}),
        vf_puissant("Intrigue"),
        "Skilled Parens",
        "Well-Traveled",
        _deficient_technique("Muto"),
        "Proud (Major)",
        _deficient_form("Terram"),
        ("Deleterious Circumstances", {"detail": "when submerged"}),
        "Fostered Apprentice",
        "Generous (Minor)",
    ],
    "traits": {"Proud": 6, "Generous": 3},
    "abilities": [
        ("Area Lore: Norway", 1, "hedge traditions"),
        ("Area Lore: Rhine", 3, "history"),
        ("Artes Liberales", 2, "logic"),
        ("Awareness", 3, "alertness"),
        ("Charm", 3, "debate"),
        ("Comprehend Magic", 4, "Nordic"),
        ("Folk Ken", 3, "men"),
        ("Guile", 3, "complex lies"),
        ("Living Language: High German", 5, "dialects"),
        ("Intrigue", 3, "plotting"),
        ("Dead Language: Latin", 5, "scribe"),
        ("Magic Theory", 4, "investigating"),
        ("Organization Lore: Durenmar", 2, "politics"),
        ("Organization Lore: Order of Hermes", 4, "personalities"),
        ("Parma Magica", 1, "Mentem"),
        ("Philosophiae", 2, "ceremonial magic"),
        ("Profession: Scribe", 2, "copying"),
        ("Teaching", 2, "magical subjects"),
    ],
    "arts": arts_from(
        "Cr 6, In 6, Mu 0, Pe 6, Re 6, An 0, Aq 0, Au 5, Co 5, He 0, Ig 0, Im "
        "5, Me 0, Te 0, Vi 6"
    ),
    "spells": [
        ("Air's Ghostly Form", "CrAu", 5, 0),
        ("Chamber of Spring Breezes", "CrAu", 5, 0),
        ("Charge of the Angry Winds", "CrAu", 15, 0),
        ("Circling Winds of Protection", "CrAu", 20, 0),
        ("Ward Against Rain", "ReAu", 10, 0),
        ("Bind Wound", "CrCo", 10, 0),
        ("Physician's Eye", "InCo", 5, 0),
        ("Curse of the Unruly Tongue", "ReCo", 5, 0),
        ("Spasms of the Uncontrolled Hand", "ReCo", 5, 0),
        ("Gift of the Frog's Legs", "ReCo", 15, 0),
        ("Phantasm of the Talking Head", "CrIm", 10, 0),
        ("Prying Eyes", "InIm", 5, 0),
        ("An Ear for Distant Bells", "InIm", 15, 0),
        ("The Call to Slumber", "ReMe", 10, 0),
        ("Unseen Arm", "ReTe", 5, 0),
        ("Scales of the Magical Weight", "InVi", 5, 0),
        ("Sense the Nature of Vis", "InVi", 5, 0),
    ],
    "notes": paragraphs(
        "A slender, healthy young woman with thick curly chestnut hair to "
        "her shoulders and dark blue eyes that seem almost purple at times. "
        "On the road she wears good worn travelling clothes and a heavy "
        "hooded cloak; in a covenant, a formal robe open over an elegant "
        "gown, with the Circlet of the Governor. Gauntleted in 1218.",
        "Combat: dodge Init +1, Defense +1. Soak +1. Encumbrance 0.",
    ),
}

TIBERIUS: StatBlock = {
    "characteristics": characteristics(1, 2, 1, -2, 1, 2, 2, 1),
    "confidence": (2, 5),
    "apparent_age": 30,
    "virtues_flaws": [
        "The Gift",
        JOURNEYMAN,
        "Gentle Gift",
        vf_ability("Affinity with {ability}", "Parma Magica"),
        _gild_trained("Ash"),
        vf_ability("Cautious with {ability}", "Great Weapon"),
        "Improved Characteristics",
        "Privileged Upbringing",
        vf_art("Puissant {art}", "Perdo"),
        "Self-Confident",
        "Warrior",
        "Black Sheep",
        _deficient_technique("Intellego"),
        "Short-Ranged Magic",
        _deficient_form("Ignem"),
    ],
    "traits": {"Brave": 3, "Pious": 2, "Honorable": 2},
    "abilities": [
        ("Animal Handling", 1, "horses"),
        ("Area Lore: Westphalia", 2, "nobles"),
        ("Artes Liberales", 1, "grammar"),
        ("Athletics", 2, "jumping"),
        ("Awareness", 3, "combat"),
        ("Brawl", 4, "dodge"),
        ("Carouse", 2, "drinking"),
        ("Code of Hermes", 1, "Wizard's March"),
        ("Concentration", 2, "combat"),
        ("Etiquette", 3, "knightly"),
        ("Great Weapon", 4, "longspear"),
        ("Living Language: High German", 5, "nobility"),
        ("Hunt", 2, "predators"),
        ("Dead Language: Latin", 4, "clerical"),
        ("Leadership", 1, "grogs"),
        ("Magic Theory", 3, "inventing spells"),
        ("Organization Lore: Collem Leonis", 2, "Flambeau"),
        ("Organization Lore: Order of Hermes", 2, "Flambeau"),
        ("Organization Lore: Rhineland Nobility", 2, "county of Mark"),
        ("Parma Magica", 2, "Mentem"),
        ("Ride", 3, "combat"),
        ("Single Weapon", 3, "longsword"),
        ("Stealth", 2, "stalking"),
        ("Survival", 2, "forest"),
    ],
    "arts": arts_from(
        "Cr 5, In 0, Mu 5, Pe 10+3, Re 5, An 5, Aq 0, Au 5, Co 5, He 5, Ig 0, "
        "Im 5, Me 0, Te 10, Vi 0"
    ),
    "spells": [
        ("Doublet of Impenetrable Silk", "MuAn", 14, 2),
        ("Circle of Beast Warding", "ReAn", 5, 0),
        ("Ward Against the Beasts of Legend", "ReAn", 5, 1),
        ("Air's Ghostly Form", "CrAu", 5, 0),
        ("Chamber of Spring Breezes", "CrAu", 5, 0),
        ("Charge of the Angry Winds", "CrAu", 15, 0),
        ("The Many-Hued Conflagration", "MuIg", 5, 0),
        ("Bind Wound", "CrCo", 10, 0),
        ("Wizard's Sidestep", "ReIm", 10, 0),
        ("Edge of the Razor", "MuTe", 20, 2),
        ("Rusted Decay of Ten-Score Years", "PeTe", 10, 0),
        ("Pit of the Gaping Earth", "PeTe", 15, 2),
    ],
    "masteries": {
        "Doublet of Impenetrable Silk": ["Quiet Casting", "Still Casting"],
        "Ward Against the Beasts of Legend": ["Lab Mastery"],
        "Edge of the Razor": ["Quiet Casting", "Still Casting"],
        "Pit of the Gaping Earth": ["Quiet Casting", "Still Casting"],
    },
    "notes": paragraphs(
        "Lean and fit, with a charming unscarred face and red-blond hair "
        "cut short as a knight keeps it under a helmet. Fine breeches and "
        "tunic, full leather scale, longsword, dagger, and the Spear of the "
        "Armiger. Gauntleted in 1214.",
        "Combat: dodge Init 0, Defense +6; dagger Init 0, Attack +8, Defense "
        "+5, Damage +4; longspear Init +2, Attack +10, Defense +7, Damage "
        "+8; fist Init 0, Attack +6, Defense +5, Damage +1; kick Init -1, "
        "Attack +6, Defense +4, Damage +4; longsword Init +1, Attack +9, "
        "Defense +6, Damage +7. Soak +7, or +10 under Doublet of Impenetrable "
        "Silk. Encumbrance 2 (3).",
        "The book lists Doublet of Impenetrable Silk at level 14, where the "
        "Definitive Edition has 15.",
    ),
}

FREKI: StatBlock = {
    "characteristics": characteristics(1, 3, 0, -1, 0, 1, 0, 0),
    "confidence": (1, 3),
    "warping": (2, 10),
    "apparent_age": 30,
    "virtues_flaws": [
        "The Gift",
        JOURNEYMAN,
        ("Ways of the {land}", {"land": "Forest"}),
        ("Deft Form", {"form": "Vim"}),
        "Free Study",
        _gild_trained("Hawthorn"),
        ("Heartbeast", {"detail": "wolf"}),
        "Independent Study",
        ("Inoffensive to {being}", {"being": "Animals"}),
        vf_focus("Minor Magical Focus", "sensing magical power"),
        ("Personal Vis Source", {"detail": "1 pawn of Vim a season, from her teeth"}),
        ("Special Circumstances", {"circumstance": "when in wolf form"}),
        "Study Bonus",
        "Unbound Tongue",
        _deficient_technique("Creo"),
        "Tormenting Master",
        ("Driven (Minor)", {"detail": "surpass her master"}),
        ("Higher Purpose (Minor)", {"detail": "teach shapeshifters the right way"}),
        ("Lesser Malediction", {"detail": "the curse of the wolf"}),
        "Poor Student",
        ("Warped Magic", {"detail": "the odor of wolf"}),
    ],
    "traits": {"Callous": 3, "Driven": 3, "Wolf": 3, "Curious": 1, "Pious": -3},
    "abilities": [
        ("Area Lore: Norway", 2, "wild places"),
        ("Area Lore: Rügen", 2, "hunting grounds"),
        ("Area Lore: Sauerland", 2, "wild places"),
        ("Artes Liberales", 1, "writing systems"),
        ("Concentration", 2, "withstand pain"),
        ("Dead Language: Gothic", 1, "deciphering"),
        ("Heartbeast", 4, "changing into wolf"),
        ("Dead Language: Latin", 4, "Hermetic terms"),
        ("Magic Lore", 1, "magical traditions"),
        ("Magic Theory", 3, "Vim"),
        ("Organization Lore: Bjornaer", 2, "ancestors"),
        ("Organization Lore: Collem Leonis", 3, "Bjornaer"),
        ("Organization Lore: Order of Hermes", 3, "Bjornaer"),
        ("Parma Magica", 2, "Animal"),
        ("Penetration", 2, "Vim"),
        ("Profession: Storyteller", 2, "ancestral stories"),
        ("Survival", 2, "forest"),
        ("Living Language: West Norse", 5, "dialects"),
    ],
    "arts": arts_from(
        "Cr 0, In 12, Mu 6, Pe 5, Re 5, An 0, Aq 0, Au 0, Co 5, He 5, Ig 0, Im "
        "5, Me 0, Te 2, Vi 12"
    ),
    "spells": [
        ("Shiver of the Lycanthrope", "InAn", 10, 0),
        ("Intuition of the Forest", "InHe", 10, 0),
        ("Shriek of the Impending Shafts", "InHe", 15, 0),
        ("Wizard's Sidestep", "ReIm", 10, 0),
        ("Sense the Nature of Vis", "InVi", 5, 0),
        ("Piercing the Magical Veil", "InVi", 20, 0),
        ("Scent of the Gift", "InVi", 25, 0),
        ("Scent of Active Magics", "InVi", 30, 0),
    ],
    "notes": paragraphs(
        "A mane of sandy hair slicked back, a strong jaw, and either a "
        "contemplative silence with the odd hungry glance or a wolfish grin "
        "of sharp teeth. Loose, simple clothes and the Mask of the Predator. "
        "Gauntleted in 1214. Twilight gave her Deft Vim, Special "
        "Circumstances and Warped Magic, so her Virtues and Flaws do not "
        "balance. Twilight scars: claw-like toenails; she growls without "
        "meaning to when angry; meeting her eye may spook or freeze a "
        "non-predatory animal. The curse of the wolf halves her Casting "
        "Totals and Magic Resistance in human form, not her Lab Totals.",
        "Combat: dodge Init 0, Defense 0. Soak +1. Encumbrance 0.",
        "In wolf form (Size -1, Houses of Hermes: Mystery Cults p. 23): Int "
        "+1, Per +3, Pre 0, Com 0, Str -1, Sta +3, Dex +2, Qik +2. Bite Init "
        "+2, Attack +11, Defense +9, Damage 0. Soak +4. She gains Long-Winded "
        "and Sharp Ears, and uses Athletics 5 (distance runner), Awareness 3 "
        "(smell), Brawl 5 (bite), Hunt 4 (track by smell) and Survival 3 "
        "(winter) in place of her General Abilities. Fatigue OK, 0/0, -1/-1, "
        "-3, -5, Unconscious. Wounds -1 (1-4), -3 (5-8), -5 (9-12), "
        "Incapacitated (13-16), Dead (17+).",
        "The block calls her Virtue Way of the Forest, here Ways of the Forest.",
    ),
}

JULIA: StatBlock = {
    "characteristics": characteristics(1, 1, 2, 1, 0, 0, 0, 1),
    "confidence": (1, 3),
    "apparent_age": 26,
    "virtues_flaws": [
        "The Gift",
        JOURNEYMAN,
        "Gentle Gift",
        _gild_trained("Apple"),
        ("Deft Form", {"form": "Mentem"}),
        "Good Teacher",
        vf_focus("Minor Magical Focus", "certamen"),
        "Skilled Parens",
        vf_puissant("Charm"),
        "Social Contacts",
        "Temporal Influence",
        _deficient_technique("Intellego"),
        "Difficult Longevity Ritual",
        "Ambitious (Minor)",
        "Avaricious (Minor)",
        "Close Family Ties",
        "Susceptibility to Faerie Power",
    ],
    "traits": {"Ambitious": 3, "Avaricious": 3, "Loyal to House Tremere": 3},
    "abilities": [
        ("Area Lore: Dortmund", 2, "local businesses"),
        ("Artes Liberales", 2, "arithmetic"),
        ("Awareness", 2, "searching"),
        ("Bargain", 2, "metal wares"),
        ("Brawl", 2, "dagger"),
        ("Charm", 3, "forming connections"),
        ("Church Lore", 1, "appointing clergy"),
        ("Concentration", 1, "spells"),
        ("Etiquette", 2, "merchants"),
        ("Finesse", 2, "details"),
        ("Folk Ken", 2, "townsfolk"),
        ("Guile", 2, "web of lies"),
        ("Living Language: High German", 5, "Westphalian"),
        ("Intrigue", 2, "alliances"),
        ("Dead Language: Latin", 5, "Hermetic"),
        ("Leadership", 1, "merchant"),
        ("Magic Theory", 3, "Rego"),
        ("Organization Lore: Order of Hermes", 1, "politics"),
        ("Organization Lore: Rhineland trading guilds", 2, "politics"),
        ("Parma Magica", 1, "Mentem"),
        ("Profession: Merchant", 3, "import"),
        ("Swim", 1, "staying afloat"),
        ("Teaching", 1, "magi"),
    ],
    "arts": arts_from(
        "Cr 5, In 0, Mu 4, Pe 5, Re 5, An 0, Aq 0, Au 0, Co 0, He 0, Ig 0, Im "
        "5, Me 11, Te 0, Vi 0"
    ),
    "spells": [
        ("Aura of Ennobled Presence", "MuIm", 10, 0),
        ("Panic of the Trembling Heart", "CrMe", 15, 0),
        ("Gossip of the Marketplace", "CrMe(Re)", 25, 0),
        ("Recollection of Memories Never Quite Lived", "MuMe", 4, 0),
        ("The Blinded Sentry", "PeMe", 5, 0),
        ("Tip of the Tongue", "PeMe", 5, 0),
        ("Calm the Motion of the Heart", "PeMe", 15, 0),
        ("Loss of But a Moment's Memory", "PeMe", 15, 0),
        ("The Call to Slumber", "ReMe", 10, 0),
        ("Snap of Awakening", "ReMe", 10, 0),
        ("Confusion of the Numbed Will", "ReMe", 15, 0),
        ("Aura of Rightful Authority", "ReMe", 20, 0),
        ("Palm of Flame", "CrIg", 5, 0),
        ("Unraveling the Fabric of Mentem", "PeVi", 1, 0),
    ],
    "notes": paragraphs(
        "Slightly built, which her well-cut clothes hide, with a charming "
        "face framed by dark blonde, slightly curly hair. Formal clothes and "
        "finery fit for a successful merchant, and the Clasp of the "
        "Ambassador. Gauntleted in 1219.",
        "Combat: dodge Init +1, Defense +3; fist Init +1, Attack +2, Defense "
        "+3, Damage 0; kick Init 0, Attack +2, Defense +2, Damage +3. Soak 0. "
        "Encumbrance 0.",
        "Gossip of the Marketplace: the spell list and its level "
        "calculation give level 25, its heading 20 (it compels the target to "
        "pass on an implanted piece of news).",
    ),
}

ERICH: StatBlock = {
    "characteristics": characteristics(0, 2, 0, 1, -1, 0, 3, 1),
    "confidence": (1, 3),
    "apparent_age": 21,
    "virtues_flaws": [
        "Outcast",
        ("Strong Faerie Blood", {"detail": "goblin"}),
        vf_ability("Affinity with {ability}", "Stealth"),
        "Improved Characteristics",
        "Keen Vision",
        vf_ability("Learn {ability} From Mistakes", "Stealth"),
        vf_puissant("Stealth"),
        "Second Sight",
        ("Dark Secret", {"detail": "spy for a diabolist"}),
        "Meddler (Major)",
        "Judged Unfairly",
    ],
    "traits": {"Meddler": 6, "Curious": 3, "Jealous": 2, "Greedy": 1},
    "abilities": [
        ("Area Lore: Dortmund", 3, "people of importance"),
        ("Athletics", 4, "climbing"),
        ("Awareness", 4, "secretive people"),
        ("Bargain", 3, "selling secrets"),
        ("Brawl", 2, "dodge"),
        ("Charm", 2, "learning secrets"),
        ("Faerie Lore", 1, "urban faeries"),
        ("Folk Ken", 2, "secretive people"),
        ("Guile", 2, "learning secrets"),
        ("Living Language: High German", 5, "being polite"),
        ("Second Sight", 1, "faeries"),
        ("Stealth", 4, "hiding"),
    ],
    "notes": paragraphs(
        "Skin of a green-grey tint, features too sharp to be wholly human, "
        "and eyes with a faint yellow glow in the dark, all hidden behind a "
        "heavy hooded cloak and discreet clothes. Strong Goblin Blood, as "
        "the book names it, gives +1 to stealth rolls, outside the scores "
        "here, and his Second Sight.",
        "Combat: dodge Init +1, Defense +4; dagger Init +1, Attack +7, "
        "Defense +3, Damage +2. Soak 0. Encumbrance 0.",
    ),
}

PAUL: StatBlock = {
    "characteristics": characteristics(-1, 2, 0, -1, 1, 2, 1, 1),
    "apparent_age": 32,
    "virtues_flaws": [
        "Turb Trained",
        "Enduring Constitution",
        ("Keen Vision", {"detail": "printed as Keen Eyes"}),
        "Carefree",
        "Lingering Injury",
        "No Sense of Direction",
    ],
    "traits": {"Carefree": 3, "Brave": 2, "Curious": -2},
    "abilities": [
        ("Area Lore: Sauerland", 3, "geography"),
        ("Awareness", 5, "keeping watch"),
        ("Athletics", 3, "running"),
        ("Brawl", 4, "dodge"),
        ("Carouse", 3, "merrymaking"),
        ("Chirurgy", 2, "binding wounds"),
        ("Concentration", 5, "staying awake"),
        ("Living Language: High German", 5, "common tongue"),
        ("Dead Language: Latin", 3, "Hermetic usage"),
        ("Organization Lore: Collem Leonis", 2, "turb"),
        ("Ride", 4, "long distance"),
        ("Single Weapon", 4, "short spear"),
    ],
    "notes": paragraphs(
        "A nondescript grog in a faded green tunic bearing the covenant's "
        "symbol, fit, perceptive and disciplined; his left arm is often "
        "bandaged or in a sling, so he does most things one-handed.",
        "Combat: dodge Init +1, Defense +6; dagger Init +1, Attack +7, "
        "Defense +5, Damage +4; fist Init +1, Attack +5, Defense +4, Damage "
        "+4; short spear Init +2, Attack +8, Defense +6, Damage +6. Soak +3, "
        "in quilted armor. Encumbrance 1 (2).",
    ),
}

MAGI = (
    (
        "ferra",
        "Ferra of Bonisagus",
        BONISAGUS,
        109,
        FERRA,
        "Master of House Bonisagus, of the Oak Gild, the last of the old "
        "generation and a Hermetic descendant of the founder Amadeus. An "
        "elementalist of Terram who once drew ore from the mine for the "
        "covenant, she came through Twilight after Twilight into the study "
        "of ghosts, and her divided career won less acclaim than she was "
        "due. A seven-year Twilight killed her owl familiar and destroyed "
        "her talisman. As the eldest she holds the Seat of the Elder, but "
        "uses none of its powers: she sits listening, offers advice of "
        "varied use, fears Final Twilight and calmly prepares for her end. "
        "Her memory fails, and she takes the young magi for someone called "
        "Heinrich.",
        "No one has learned who Heinrich was, or whether he ever lived; yet "
        "her sanctum marker bears his name, and she remembers him borrowing "
        "good books.",
    ),
    (
        "baliana",
        "Baliana of Bonisagus",
        BONISAGUS,
        26,
        BALIANA,
        "Journeyman of House Bonisagus, of the Ash Gild, and holder of the "
        "Seat of the Governor. Filia of Marcellus, a descendant of the "
        "founder Briana, who travels the north recording non-Hermetic magic "
        "and taught her Comprehend Magic, a Pralix gift he brought into his "
        "line at some cost in reputation. She trained at Collem Leonis, at "
        "Durenmar, and on the roads of the Rhine and southern Norway, and "
        "was fostered for a time by Occultes. She studies the portals, "
        "wants the rune alphabet, and means to build a broad repertoire and "
        "Vim for her travels, working with Pancrestis of Heorot.",
        "She joined the Ash Gild, odd for her House, to please her mentors "
        "and learn what it knows of the Order of Odin, which Occultes means "
        "to find, understand, and perhaps fight. The project is young and "
        "kept secret from Durenmar.",
    ),
    (
        "freki",
        "Freki of Bjornaer",
        BJORNAER,
        30,
        FREKI,
        "Journeyman of House Bjornaer, of the Hawthorn Gild and Clan Arelie, "
        "with a wolf heartbeast, and holder of the Seat of the Predator: "
        "she watches the domain and tracks on the hunts. A Norwegian child "
        "who likely wandered through a portal, she was found at seven by "
        "her mater Oda, of the line of the founder Wolfgang, and attended "
        "the Gathering of 1203 after four years of apprenticeship. Oda "
        "drove her into risks and many Twilights. She spends most of her "
        "time as a wolf, and would surpass Oda, not by fighting but as the "
        "leading authority on telling shapeshifters who must be destroyed "
        "from hedge traditions the House could take in. She seeks the "
        "Order of Odin beside Baliana.",
        "",
    ),
    (
        "tiberius",
        "Tiberius of Flambeau",
        FLAMBEAU,
        30,
        TIBERIUS,
        "Journeyman of House Flambeau, of the Ash Gild, and holder of the "
        "Seat of the Armiger: he commands the defenses and the turb, and "
        "plays the knight in charge of the count's hunt. Born Meitzler of "
        "Soest, youngest son of Freiherr Reinhart I, he was taken from a "
        "monastery's future by his pater Scipio, who renamed him; his "
        "family cast him off and its enemies take it out on him. Of the "
        "knightly school of Ramius, with a line that recruits nobles' "
        "lesser sons for arms and a Gentle Gift, he likes a fair fight and "
        "protects the weak and the Order.",
        "He is the father of Erika, Johanna's daughter, and the rumour is "
        "true. He thinks she may be Gifted but has not had Freki check: "
        "the Rhine says a journeyman may not train her, his line takes "
        "younger noble sons, not bastard daughters, and she may not want it.",
    ),
    (
        "julia",
        "Julia of Tremere",
        TREMERE,
        26,
        JULIA,
        "Journeyman of House Tremere, of the Apple Gild, and holder of the "
        "Seat of the Ambassador. An orphan found by her pater Renardus and "
        "raised as a merchant's child in a Dortmund house he owned, she has "
        "taken his place in its trade and guilds since he retired to "
        "Coeris, though being a woman makes that hard, and she wonders if "
        "magic might make her a man to the eye. Her foster father Frederick "
        "sells and exports what her foster brother Armund brings in. She "
        "serves her House as assessor of local transport and provisions, "
        "lectures her sodales on discretion, and buys news from Erich the "
        "spy. Stentorius of Fengheld holds her sigil.",
        "",
    ),
)

PEOPLE = (
    (
        "johanna",
        "Johanna the Autocrat",
        "companion",
        31,
        "Steward, chamberlain and manager of the covenant, a lesser noble's "
        "daughter from near Dortmund, taught by a tutor from the cathedral "
        "school. She ran here at 15 after meeting Scipio, was placed under "
        "the autocrat Joachim, and had his office thrust on her when he "
        "vanished. Erika is her daughter; no one has confirmed the father. "
        "Stats: the Female Scholar template (ArM5 p. 22) aged 31, with "
        "Profession: Chamberlain 4 (inspire loyalty), Profession: Steward 4 "
        "(mediating), Area Lore: Sauerland 4 (geography), Organization Lore: "
        "Collem Leonis 4 (history), and 130 more experience as you choose, "
        "as on Order of Hermes Lore, Realm Lores or Code of Hermes.",
    ),
    (
        "francois",
        "Francois the Grog Captain",
        "grog",
        20,
        "A greatswordman brought from Normandy by Tiberius a few years ago, "
        "still poor at the language, made captain for want of anyone else "
        "and leading the turb reluctantly. Stats: the Specialist template "
        "(ArM5 p. 21), Great Weapon (greatsword) for Single Weapon, "
        "Leadership for Bargain, High German 3 (grogs), aged to 20.",
    ),
    (
        "geri",
        "Geri the Hunter",
        "grog",
        None,
        "A quiet, sullen local lad with a dark view of life, who keeps his "
        "Second Sight mostly hidden. Stats: the Hunter template (ArM5 p. "
        "21), with Afflicted Tongue and Second Sight, aged at least a year "
        "to raise it.",
    ),
    (
        "erika",
        "Erika",
        "grog",
        13,
        "Johanna's feisty, red-headed daughter, who likes fighting and has "
        "a flair for it, the latest possible recruit to the turb. She "
        "trains at arms with Tiberius, has little Latin, and shares her "
        "mother's taste for freedom and equality.",
    ),
    (
        "otto",
        "Otto",
        "grog",
        None,
        "Ferra's personal servant, Intelligence +2, who keeps her laboratory clean.",
    ),
)

#: type, name, author, subject, level, quality, what it is.
LIBRARY = (
    (
        "Summa",
        "The Urban Landscape",
        "Tacitus of Tremere",
        "Area Lore: Dortmund",
        2,
        9,
        "",
    ),
    (
        "Summa",
        "Elias' Primer on Sauerland",
        "Elias of Jerbiton",
        "Area Lore: Sauerland",
        2,
        9,
        "",
    ),
    (
        "Summa",
        "Elias' Primer on the Order",
        "Elias of Jerbiton",
        "Organization Lore: Order of Hermes",
        3,
        9,
        "",
    ),
    (
        "Summa",
        "Collem Leonis Rolls",
        "Various Autocrats",
        "Profession: Autocrat",
        4,
        6,
        "",
    ),
    (
        "Tractatus",
        "Collem Leonis Chronicles, volume I",
        "Various Autocrats",
        "Organization Lore: Collem Leonis",
        None,
        6,
        "",
    ),
    (
        "Tractatus",
        "Collem Leonis Chronicles, volume II",
        "Various Autocrats",
        "Organization Lore: Collem Leonis",
        None,
        6,
        "",
    ),
    (
        "Summa",
        "Portae Septentrionem",
        "Various authors",
        "Area Lore: Collem Leonis Portals",
        8,
        5,
        "Centuries of records of every opening: times, places, what came "
        "through, what was done, with maps and failed grand theories. It "
        "serves both prediction and study.",
    ),
    ("Tractatus", "Blessed Growth", "Petrus of Bonisagus", "Creo", None, 10, ""),
    ("Tractatus", "Oculus Tertius", "Irina of Guernicus", "Intellego", None, 9, ""),
    (
        "Tractatus",
        "Nature's Mutable Qualities",
        "Diviana of Merinita",
        "Muto",
        None,
        9,
        "",
    ),
    ("Tractatus", "Weaken and Decay", "Scipio of Flambeau", "Perdo", None, 9, ""),
    ("Tractatus", "Hierarchy", "Vries of Tremere", "Rego", None, 11, ""),
    ("Tractatus", "Domination", "Vries of Tremere", "Rego", None, 11, ""),
    (
        "Tractatus",
        "Nobility Among Beasts",
        "Adler of Bjornaer",
        "Animal",
        None,
        9,
        "",
    ),
    ("Tractatus", "Nature of the Rhine", "Adler of Bjornaer", "Aquam", None, 9, ""),
    ("Tractatus", "Life Giving Rain", "Adler of Bjornaer", "Auram", None, 9, ""),
    (
        "Tractatus",
        "Sanguine Humours",
        "Maximillian ex Miscellanea",
        "Corpus",
        None,
        8,
        "",
    ),
    (
        "Tractatus",
        "Melancholic Humours",
        "Maximillian ex Miscellanea",
        "Corpus",
        None,
        8,
        "",
    ),
    (
        "Tractatus",
        "Entangling with Thorns",
        "Scipio of Flambeau",
        "Herbam",
        None,
        9,
        "",
    ),
    ("Tractatus", "Living Wood", "Adler of Bjornaer", "Herbam", None, 9, ""),
    ("Tractatus", "The Hot and the Bright", "Ardor of Flambeau", "Ignem", None, 9, ""),
    ("Tractatus", "The Cold and Dark", "Ardor of Flambeau", "Ignem", None, 9, ""),
    (
        "Tractatus",
        "Whispering Winds",
        "Briana of Bonisagus",
        "Imaginem",
        None,
        12,
        "",
    ),
    ("Tractatus", "Prying Eyes", "Briana of Bonisagus", "Imaginem", None, 12, ""),
    ("Tractatus", "Spirits of the Void", "Vesta of Tremere", "Mentem", None, 10, ""),
    (
        "Tractatus",
        "The Subtle Art of Manipulation",
        "Vesta of Tremere",
        "Mentem",
        None,
        10,
        "",
    ),
    ("Tractatus", "Dirt", "Ferra of Bonisagus", "Terram", None, 6, ""),
    ("Tractatus", "Rock", "Ferra of Bonisagus", "Terram", None, 6, ""),
    ("Tractatus", "Iron", "Ferra of Bonisagus", "Terram", None, 6, ""),
    ("Tractatus", "Silver", "Ferra of Bonisagus", "Terram", None, 6, ""),
    ("Tractatus", "The Intangible Art", "Vries of Tremere", "Vim", None, 11, ""),
)

#: The Hidden Resources' books, as LIBRARY: (type, name, author, subject,
#: level, quality).
NURSERY = (
    ("Summa", "Apprentice's Guide", "", "Magic Theory", 4, 12),
    ("Summa", "Growth and Repair", "", "Creo", 5, 15),
    ("Summa", "Perception", "", "Intellego", 5, 15),
    ("Summa", "Metamorphosis", "", "Muto", 6, 14),
    ("Summa", "Decay and Destruction", "", "Perdo", 5, 15),
    ("Summa", "Movements by Magic", "", "Rego", 5, 15),
    ("Summa", "Flowing Waters", "", "Aquam", 6, 21),
    ("Summa", "Blowing Winds", "", "Auram", 5, 17),
    ("Summa", "Beasts of the Black Forest", "", "Animal", 6, 21),
    ("Summa", "The Heart and the Hand", "", "Corpus", 6, 16),
    ("Summa", "Of Root, Trunk, and Branch", "", "Herbam", 5, 15),
    ("Summa", "Flames", "", "Ignem", 5, 15),
    ("Summa", "That Which is Seen or Heard", "", "Imaginem", 6, 15),
    ("Summa", "In the Mind of the Magus", "", "Mentem", 5, 12),
    ("Summa", "Two Feet on the Ground", "", "Terram", 6, 18),
    ("Summa", "This Intangible Art", "", "Vim", 6, 15),
)
CACHE = (
    ("Summa", "Pagan Nordic Beliefs", "Amadeus of Bonisagus", "Faerie Lore", 5, 14),
    ("Summa", "Of Details and Speed", "Tacitus of Tremere", "Finesse", 4, 12),
    ("Summa", "Beasts of Nordic Myths", "Amadeus of Bonisagus", "Magic Lore", 5, 14),
    (
        "Tractatus",
        "The Theories of Bonisagus",
        "Amadeus of Bonisagus",
        "Magic Theory",
        None,
        14,
    ),
    (
        "Tractatus",
        "On the Subject of Labwork",
        "Amadeus of Bonisagus",
        "Magic Theory",
        None,
        14,
    ),
    (
        "Tractatus",
        "Mercurian Influences on Hermetic Theory",
        "Amadeus of Bonisagus",
        "Magic Theory",
        None,
        14,
    ),
    (
        "Tractatus",
        "Integration of Exotic Magic",
        "Amadeus of Bonisagus",
        "Magic Theory",
        None,
        14,
    ),
    ("Summa", "The Arcane Hammer", "Pamprepius of Flambeau", "Penetration", 5, 11),
    (
        "Summa",
        "Sharpening of the Senses",
        "Amadeus of Bonisagus",
        "Intellego",
        12,
        14,
    ),
    ("Summa", "The Art of Motion", "Maximus of Bonisagus", "Rego", 14, 12),
    ("Summa", "Might of Aeolus Unleashed", "Stratos of Tremere", "Auram", 13, 15),
    ("Summa", "The Ghostly Art", "Thuwald the Bold", "Mentem", 16, 13),
    ("Summa", "Wealth of the Deep", "Manlius of Tytalus", "Terram", 17, 13),
    ("Summa", "The Purest of all Arts", "Augusta of Bonisagus", "Vim", 14, 16),
    ("Summa", "Howls from the Deep", "", "Goetic Summoning", 15, 15),
    ("Summa", "Shackles in the Dark", "", "Goetic Binding", 15, 15),
)
BOOKCASE = (
    (
        "Summa",
        "Scourge of the Infernal",
        "Helveticus of Flambeau",
        "Spell Mastery: Demon's Eternal Oblivion 15",
        3,
        15,
    ),
    (
        "Summa",
        "Flambeau's Legacy",
        "Maris of Flambeau",
        "Spell Mastery: Pilum of Fire",
        4,
        16,
    ),
    (
        "Summa",
        "A Transparent State",
        "Manlius of Tytalus",
        "Spell Mastery: Veil of Invisibility",
        2,
        15,
    ),
    (
        "Tractatus",
        "Arcane Travel",
        "Amadeus of Bonisagus",
        "Spell Mastery: Piercing the Magical Veil",
        None,
        14,
    ),
    (
        "Tractatus",
        "Fortress of the Home",
        "Amadeus of Bonisagus",
        "Spell Mastery: Aegis of the Hearth 20",
        None,
        14,
    ),
)

#: The spell, its technique, form and level, and any words.
LAB_TEXTS = (
    ("Ward Against Beasts of Legend", "Rego", "Animal", 15, ""),
    ("Bind Wound", "Creo", "Corpus", 10, ""),
    (
        "Circle of Recovery",
        "Creo",
        "Corpus",
        20,
        "R: Touch, D: Ring, T: Circle. Those who stay in the circle for the "
        "whole recovery time have +12 to Recovery Rolls. (Base 5, +1 Touch, "
        "+2 Ring.)",
    ),
    (
        "Enter the Domain of Eir",
        "Creo",
        "Corpus",
        30,
        "Ritual. R: Touch, D: Mom, T: Circle. Named for the Norse goddess of "
        "healing: all within improve every wound one step, so Light wounds "
        "go. Guideline from Houses of Hermes: Societates p. 100. (Base 25, "
        "+1 Touch.)",
    ),
    ("Whispers through the Black Gate", "Intellego", "Corpus", 15, "Mentem requisite."),
    ("The Inexorable Search", "Intellego", "Corpus", 20, ""),
    ("Eyes of the Cat", "Muto", "Corpus", 5, ""),
    ("Invocation of Weariness", "Perdo", "Corpus", 20, ""),
    ("Pilum of Fire", "Creo", "Ignem", 20, ""),
    ("Aura of Ennobled Presence", "Muto", "Imaginem", 10, ""),
    ("Perception of the Conflicting Motives", "Intellego", "Mentem", 15, ""),
    ("Frosty Breath of the Spoken Lie", "Intellego", "Mentem", 20, ""),
    ("Posing the Silent Question", "Intellego", "Mentem", 20, ""),
    ("Thoughts Within Babble", "Intellego", "Mentem", 25, ""),
    ("Scent of Peaceful Slumber", "Rego", "Mentem", 20, ""),
    ("Piercing the Faerie Veil", "Intellego", "Vim", 20, ""),
    ("Piercing the Magical Veil", "Intellego", "Vim", 20, ""),
    (
        "Day of Communion",
        "Muto",
        "Vim",
        20,
        "R: Voice, D: Sun, T: Group. Wizard's Communion (ArM5 p. 160) at a "
        "longer duration, since a Muto Vim spell must last the whole casting "
        "of its ritual. Each caster adds his spell's level less two "
        "magnitudes, and the sum must exceed twice the ritual's level; one "
        "magus may join for each magnitude of the ritual, so it is little "
        "use below level 20. Most useful for an Aegis of the Hearth.",
    ),
    ("Gather the Essence of the Beast", "Rego", "Vim", 15, ""),
    ("Aegis of the Hearth", "Rego", "Vim", 20, "Ritual."),
)

ARTS = {
    "Creo", "Intellego", "Muto", "Perdo", "Rego", "Animal", "Aquam", "Auram",
    "Corpus", "Herbam", "Ignem", "Imaginem", "Mentem", "Terram", "Vim",
}  # fmt: skip

#: Section, then the clause. Numbers run on through the charter.
CHARTER = (
    (
        "Membership",
        "Three ranks: haeres, prospectus and visitator. Apprentices have no "
        "rank and follow their parens as a courtesy.",
    ),
    (
        "Membership",
        "Haeres was the founders' rank, since extended to mature magi the "
        "council finds worthy; the haeres form the ruling council.",
    ),
    (
        "Membership",
        "A prospectus is a younger resident not yet proven, or a haeres "
        "demoted; once a cycle she may ask to be raised to haeres.",
    ),
    (
        "Membership",
        "A visitator is a short-term resident who does not qualify as a "
        "peregrinator under the Peripheral Code.",
    ),
    (
        "Method of Governance",
        "The haeres alone vote on covenant matters, including promoting, "
        "demoting and accepting members.",
    ),
    (
        "Method of Governance",
        "Five seats are held for a cycle: Elder, Governor, Armiger, Predator "
        "and Diplomat. Any member may nominate; the Elder sets a test between "
        "rivals. No magus ordinarily holds two seats, and the Elder holds "
        "an unfilled seat and may delegate it.",
    ),
    (
        "Method of Governance",
        "The Elder is the senior haeres: she moderates, calls the vote, "
        "has the discussion recorded in the chronicle, must always vote, "
        "and breaks ties.",
    ),
    (
        "Method of Governance",
        "The Governor runs the daily business and bears the Circlet; the "
        "Armiger is the ablest in combat and defends the covenant, bearing "
        "the Spear; the Predator has the sharpest senses and local "
        "knowledge and watches the domain, bearing the Mask; the Diplomat "
        "handles relations, above all mundane, bearing the Clasp.",
    ),
    (
        "Method of Governance",
        "Issues pass by majority, one vote to a haeres, blank votes allowed "
        "unless noted; two thirds of the haeres make a quorum; charter "
        "changes need a two-thirds majority (an amendment of its first year).",
    ),
    (
        "Method of Governance",
        "The council meets on the morning of the first day of each season. "
        "Any haeres may call an emergency meeting with due warning, and may "
        "later ask for a re-vote if the warning was too short.",
    ),
    (
        "Method of Governance",
        "A cycle is eight seasons, counted from spring 858; spring 1220 "
        "opens one. Its first meeting assesses the services and conduct of "
        "the cycle before.",
    ),
    (
        "Member Rights",
        "Prospecti's use of library and laboratories is settled case by case; "
        "visitators' by agreement on joining, under the Peripheral Code; "
        "apprentices share their parens' rights.",
    ),
    (
        "Member Rights",
        "A haeres with no service in the last cycle may only borrow books "
        "no privileged magus wants; a privileged magus claims one book a "
        "season. No prospectus has the library without a service or an "
        "equal gift.",
    ),
    (
        "Member Rights",
        "A laboratory once granted can be withdrawn only by dismissal, but "
        "only a privileged magus has its running paid from the coffers.",
    ),
    (
        "Member Obligations",
        "A service is a season writing a book, enchanting a device, or "
        "finding or securing a vis source, all given to the covenant, or "
        "any long or dangerous task; the council may vote on its validity. "
        "A seat is not itself a service. Services earn privileges in the "
        "next cycle only.",
    ),
    (
        "Covenant Resources",
        "Each cycle's vis income, after fixed costs (Aegis of the Hearth, "
        "commissioned devices, healing, Longevity Rituals), is divided in "
        "shares: two to a haeres, a half more to the Elder, a half to a "
        "prospectus; each extra service earns a further share, or a half for "
        "a prospectus. Any remainder is carried over.",
    ),
    (
        "Covenant Resources",
        "Books or vis a magus finds are his own, and giving them is a "
        "service. A vis source found in the domain goes to the covenant, the "
        "finder keeping its first year's harvest; the council decides what "
        "the domain covers. One found elsewhere stays his to protect.",
    ),
    (
        "Censure",
        "A vote of censure demotes a haeres to prospectus, who may petition "
        "after a full cycle; it dismisses a prospectus or visitator, who has "
        "one season to clear out and may not enter the domain for five years.",
    ),
    (
        "Censure",
        "No haeres may be demoted in her absence unless told a season ahead, "
        "or unless every effort was made to tell her.",
    ),
    (
        "Censure",
        "Peregrinatores are protected by the Laws of Hospitality and the "
        "Peripheral Code and cannot be dismissed.",
    ),
)
PERIPHERAL_CHARTER = (
    "Only members of House Bjornaer may visit the ancestral sites of the tallest hill.",
    "No lion or other large feline may be hunted without a resident Bjornaer "
    "magus's express leave.",
    "The two sexes are wholly equal: no post is closed to women, nor the "
    "vote. It does not say magi only, so it binds everyone.",
    "Covenfolk have time off for local holidays, as the Autocrat rules, with "
    "no more than twenty spared at once.",
    "No fiery animals in the library, nor any open flame.",
    "Any animated dead sent on errands must be managed by someone able to "
    "control them, and a council member may refuse their help.",
)

#: name, what it does: the devices known to the magi.
DEVICES = (
    (
        "Clasp of the Ambassador",
        "A silver cloak clasp with a rotating violet amethyst, made by "
        "Tacitus of Tremere in the 870s; the badge of the Seat. Opened with "
        "15 pawns, 6 used. Aura of Beguiling Appearance (MuIm 15, 12 a day, "
        "R: Touch, D: Sun, T: Ind): +3 to win trust and make friends, The "
        "Gift still applying; turn the amethyst clockwise. Aura of Equality "
        "(ReMe 40, Pen 32, 12 a day, R: Eye, D: Sun, T: Ind): the target "
        "accepts the wearer as an equal and will treat; Tacitus reckoned it "
        "could reach an archbishop in his cathedral; meet the eye, bow "
        "slightly and speak the greeting. 22 Build Points.",
    ),
    (
        "Spear of the Armiger",
        "A heavy longspear of ash banded in bronze, once the talisman of "
        "Pamprepius of Flambeau, whose attunements and personal effects are "
        "dead. Opened with 24 pawns: 10 on the useless effects, 8 on those "
        "below, 6 free. Blunt the Viper's Fangs (PeAn 40, Pen 20, 24 a day, "
        "R: Voice, to Size +7): swing it and say the word. Invocation of "
        "Weariness (PeCo 40, Pen 20, 24 a day, R: Voice, to Size +4): stab "
        "and say the word. Its bearers speak softly, by a tradition of "
        "even odds. 32 Build Points.",
    ),
    (
        "Mask of the Predator",
        "A terrifying wolf-skull mask inlaid with occult symbols in silver, "
        "made by Wolfgang of Bjornaer for his filia Ulvisa. Opened with 15 "
        "pawns, 8 used. Immediate Sense of What Treads the Surface (InTe 30, "
        "unlimited, R: Touch, D: Mom, T: Part): rough mass, speed and "
        "direction of all that touches the ground within 1000 paces; close "
        "your eyes and put its ear to the ground. Eyes of the Bat (InAu 34, "
        "12 a day, R: Touch, D: Sun, T: Hearing, item maintains "
        "concentration): close your eyes and tilt your head once each way. "
        "Past wearers made spells to meld it to their bodies through a "
        "change of shape, but none has enchanted that in. 26 Build Points.",
    ),
    (
        "Circlet of the Governor",
        "A gold circlet made by Amadeus of Bonisagus for his amica Briana, "
        "with a fixed Arcane Connection to the council chamber's fireplace, "
        "though any Connection serves. Opened with 20 pawns, 4 used. "
        "Summoning the Distant Image (InIm 30, 24 a day, R: Arc, D: Conc, "
        "T: Ind): touch it with both hands, arms crossed; alone it may be "
        "scrying if a magus is there. Phantasm of the Talking Head (CrIm 25, "
        "24 a day, R: Arc, D: Conc, T: Ind): one hand at the forehead, one "
        "at the back. 22 Build Points.",
    ),
    (
        "Woodshed of Plenty",
        "Made by Adler of Bjornaer, who grieved at the logging. CrHe 30, "
        "unlimited, R: Touch, D: Moon, T: Group: opening and closing the "
        "door fills it with ten cubic paces of fireplace logs, which vanish "
        "at the moon's end, so wood is bartered in small amounts. Adler "
        "wrote a savage flogging for any who use it before it is empty. "
        "Saves three laborers (Covenants pp. 56-71). 12 Build Points.",
    ),
)

SIGHT_OF_PORTALS = (
    "Prediction: a stress roll of Int + Area Lore: Collem Leonis Portals "
    "against 15 gives the direction or that no portal will open; 18 a "
    "single valley, hill or lake, the realm and the kind of event; 21 the "
    "exact place, the creature and how to meet it. Modifiers: -3 for 10 "
    "days or less; +1 a month; +3 a season; -3 for more than half the time "
    "in the library; +1 for the covenant's references; +1 for each scout of "
    "score 5 or more; +3 once for Premonitions in the field; +3 for this "
    "season, 0 for next, -3 for further ahead. Premonitions use the same "
    "Ease Factors with no modifiers. No one at the covenant yet knows "
    "enough to try."
)


def build(rhine: Rhine) -> None:
    b = rhine.b
    places = _places(rhine)
    covenant = _covenant(rhine, places["site"])
    rhine.covenants["collem_leonis"] = covenant
    covenant.boons_hooks = boons_hooks_from(covenant.what_matters)
    rhine.places["collem_leonis_site"] = places["site"]
    _people(rhine, covenant)
    _world(rhine, covenant)
    _laboratories(rhine, covenant)
    _devices(covenant)
    _library(b, covenant)
    _vis(covenant)
    _hidden(b, covenant)
    _charter(covenant)
    _history(b, covenant)
    _creatures(b, covenant, places)


def stats(rhine: Rhine) -> None:
    """After the gilds exist: the stat blocks, each magus's gild, and the
    sigil Julia's exarch holds."""
    b, tribunal = rhine.b, rhine.tribunal
    assert tribunal is not None
    for key, _name, _house, _age, block, _summary, _secrets in MAGI:
        b.stats(rhine.magi[key], block, source=SOURCE)
    b.stats(rhine.magi["erich"], ERICH, source=SOURCE)
    b.stats(rhine.magi["paul"], PAUL, source=SOURCE)
    gilds = rhine_package.gilds(tribunal)
    for key, tree in (
        ("ferra", "Oak"),
        ("baliana", "Ash"),
        ("tiberius", "Ash"),
        ("freki", "Hawthorn"),
        ("julia", "Apple"),
    ):
        gild = next(g for g in gilds if g["name"].startswith(tree))
        rhine_package.join(tribunal, rhine.magi[key].id, gild)
    held = rhine_package.sigil_held_by(tribunal)
    held[rhine.magi["julia"].id] = rhine.magi["stentorius"].id
    fengheld = rhine.magi["stentorius"].covenant_id
    if fengheld is not None:
        tribunal.proxies[fengheld] = tribunal.proxies.get(fengheld, 0) + 1
    b.ruling(
        tribunal,
        "The right of veto",
        780,
        "Existing covenants may veto the founding of a new covenant; a single "
        "veto is enough to stop it.",
    )
    sauerland = rhine.places["sauerland"]
    sauerland.summary = sauerland.summary.replace(
        "Rugged, inhospitable uplands south of Paderborn bordering Thuringia.",
        "Forested hills in the hinterland of Dortmund, in the county of Mark.",
    )


def _places(rhine: Rhine) -> dict[str, Neighbour]:
    b = rhine.b
    sauerland = rhine.places["sauerland"]
    site = b.place(
        "The hill of Collem Leonis",
        inside=sauerland,
        aura=5,
        detail=FULL,
        summary=paragraphs(
            "A low hill between steep forested slopes, ringed by an earthen "
            "dyke some 200 feet across and a neglected palisade, its one gap "
            "facing the path to the nearest village, its gate long since "
            "broken up for timber. A manor hall of great stone blocks under "
            "slate stands in a yard of cobble, gravel and puddles where "
            "chickens and pigs wander.",
            "Below the hill the Magic aura fades, and most of the surrounding "
            "land has a Faerie aura of 1, save small pockets of Magic where "
            "the vis sources lie. Its strength is unbroken wild forest, "
            "untouched by mundanes for centuries.",
        ),
    )
    jotunheim = b.place(
        "Jotunheim",
        inside=sauerland,
        detail=FULL,
        tethers=(
            "The uncontrolled portals while open; the hill of Eisenhöhe, by "
            "a route that opens under stars that come round about every ten "
            "years. Exits lead to empty parts of Norway; the way back to "
            "Sauerland exists only while a portal is open."
        ),
        summary=paragraphs(
            "The Magical regio behind the portals, named from the Norse "
            "myths. Both levels are aligned with chaos (RoP: Magic pp. "
            "15-16): extra botch dice equal to half the aura, which no "
            "Hermetic means reduces, and a pawn of fitting vis for each zero "
            "on a magical botch check. Transportation magic works, and "
            "carries out through an open portal. The sun's speed varies, and "
            "maps go stale.",
            "Those who cross the difficult ground may say the levels are one, "
            "the aura only varying from place to place; the old magi "
            "argued it both ways. The giants call themselves Jotunn; many "
            "know runic magic and their leaders are Vitkar (Hedge Magic, "
            "Revised Edition, pp. 120-141). Whether this is truly Jotunheim "
            "no one has cause to doubt.",
            "Things that have come through: gigantic clever wolves in a "
            "hard winter; boars of stone that track vis plants and fungus by "
            "smell; faeries posing as Norse gods who meddle in village "
            "farming, marriage and war. Monsters have made hunts for the "
            "count, and vis comes this way, but too irregularly to count "
            "on. An open portal is a misplaced terrain feature or plant in a "
            "vague shimmer, showing what lies beyond; it may grow from a "
            "point of light over days or open at once, within a few days' "
            "trek of the covenant, and is best seen at dusk and dawn.",
            SIGHT_OF_PORTALS,
        ),
        levels=[
            b.level(
                "The lower level",
                3,
                see=(
                    "Primordial wilderness of mountains, forests, valleys, "
                    "rivers and fjords, with huge and remarkable wolves, "
                    "bears, boars, foxes, hawks, ravens, wild bulls and "
                    "horses, some giant, some gifted or clever, and the odd "
                    "Norse dragon or lindorm."
                ),
                enter=(
                    "By an open portal or Eisenhöhe, always to a pass in an "
                    "immense range under perpetual storm clouds, near the "
                    "level's centre."
                ),
            ),
            b.level(
                "The higher level",
                8,
                see=(
                    "It rings the lower level: east, up sheer cliffs, the "
                    "storm giants; north, snow and ice and the mountain "
                    "giants, with no known ruler, perhaps toward Niflheim; "
                    "south, a sun-baked broken land of fire giants, perhaps "
                    "toward Muspelheim; west, fjords and an endless sea "
                    "that has driven back every scout."
                ),
                enter="By braving the difficult terrain, a few days' trek from the portal.",
            ),
        ],
    )
    midgard = b.place(
        "Midgard",
        inside=sauerland,
        realm="Faerie",
        aura=1,
        detail=FULL,
        tethers=(
            "Enter if led by an inhabitant, by sensing the boundaries, or "
            "by circling Eisenhöhe clockwise under a rainbow. An opened "
            "portal goes both ways. Otherwise only the faerie gods give leave "
            "to go, once their story ends; no one has found a place to "
            "leave by magic."
        ),
        summary=paragraphs(
            "The Faerie regio behind the portals, a copy of Norse life of "
            "centuries past on one great shifting island in a vast ocean, "
            "with viking strongholds on its rivers and coasts. Incognizant "
            "faeries play farmers, kings, beasts and monsters, sailing to "
            "raid each spring and coming home fewer; time passes so fast "
            "that a year outside sees a son king in his father's place. "
            "Whether the raiders reach anywhere is unknown.",
            "Cognizant faeries play the Norse gods, visiting when mundanes "
            "have been lured in to play heroes, and now and then staging a "
            "war march or monstrous invasion in the mortal world. Elven "
            "maidens, dwarf smiths and toll-taking trolls set challenges and "
            "feed on the answers; stronger faeries seize lesser ones' "
            "stories.",
        ),
        levels=[
            b.level(
                "Midgard",
                6,
                "Faerie",
                see="Hills, forests, pastures and fields in constant flux.",
            )
        ],
    )
    eisenhohe = b.place(
        "Eisenhöhe and the mine",
        inside=sauerland,
        detail=FULL,
        summary=(
            "The highest hill of the district. Halfway up, a shaft slick with wear "
            "and seeping water drops to the mine's antechamber, with "
            "man-sized passages along the veins beyond. The hills hold iron, "
            "coal, lime, silver, bronze, tin and lead in moderate amounts; "
            "the mine is disused but for its vis, and all the covenfolk know "
            "tales of its kobold."
        ),
    )
    tree_house = b.place(
        "The Tree House",
        inside=sauerland,
        aura=0,
        status="Rumoured",
        known="",
        detail=FULL,
        summary=(
            "The chronicles record a remote laboratory of the Bjornaer magus "
            "Holzstein somewhere in the hills, and its general whereabouts, "
            "but not how to get in."
        ),
        secrets=(
            "A small Magical regio with a huge magical oak as its tether, "
            "where Holzstein of the second generation built his sanctum, in "
            "and around the tree. Agnes the wood spirit guards it, and the "
            "Man in the Woods stands near. His filii retreated to Crintera "
            "at the Schism War and it has been forgotten since. Research "
            "beating Ease Factor 15 hints at an allied spirit."
        ),
        levels=[b.level("Holzstein's regio", 5)],
    )
    man = b.place(
        "The Man in the Woods",
        inside=tree_house,
        level=1,
        status="Rumoured",
        known="",
        summary=(
            "The chronicles name it as the covenant's only Corpus vis source, "
            "lost with Holzstein's laboratory."
        ),
        secrets=(
            "A yew grown into a man's shape: two trunks for legs, tangled "
            "branches for a body, a snapped stump with a face, long arms with "
            "talons. Golden resin from its cracks yields 2 pawns of Corpus "
            "vis at each season's end. 40 Build Points."
        ),
    )
    living_wood = b.place(
        "The Portal of Living Wood",
        inside=sauerland,
        status="Rumoured",
        known="",
        summary="A faint path winding through the wooded hills.",
        secrets=(
            "A new source of Vim: the path ends where two trees with "
            "entwined branches form a portal across it, though no regio "
            "entrance. Their hardening sap gives 7 pawns each autumn. A magus "
            "searching the woods with Intellego Vim finds it easily. 35 "
            "Build Points."
        ),
    )
    return {
        "site": site,
        "jotunheim": jotunheim,
        "midgard": midgard,
        "eisenhohe": eisenhohe,
        "tree_house": tree_house,
        "man_in_the_woods": man,
        "portal_of_living_wood": living_wood,
    }


def _covenant(rhine: Rhine, site: Neighbour) -> Covenant:
    b, tribunal = rhine.b, rhine.tribunal
    assert tribunal is not None
    return b.covenant(
        NAME,
        tribunal=tribunal,
        founded=865,
        season="Spring",
        detail=FULL,
        aura=5,
        place=site,
        summary=paragraphs(
            "A Second Spring covenant in the forested hills of the Sauerland, "
            "not far from Dortmund and Cologne, whose symbol is a yellow "
            "lion on a black two-topped mountain. Founded in 865, the eighth "
            "of the new Rhine Tribunal, it is one of only four of those "
            "eight still standing. Its hall was built by magi drawn here by "
            "a Great Beast, a lion, and held in law as a count's hunting "
            "lodge. From afar it looks grand; closer, the small windows "
            "have been cut wide, doors knocked through, balconies hung, and "
            "shacks have sprouted from the walls in no order.",
            "The ground floor divides at the great stair: kitchen, servants' "
            "quarters and stores to the left, library, scriptorium and the "
            "dining hall that serves as council chamber to the right. "
            "Laboratories and sancta fill the upper floors, many of them "
            "empty. The workshops to the left stand mostly idle, and those "
            "to the right, once vellum makers' and binders', are silent; "
            "the yard that rang with the armorer's hammer now sounds like a "
            "sleepy hamlet.",
            "Four young magi and one old maga live here among a handful "
            "of loyal folk: a grog and two servants for each magus, with "
            "five fighting grogs, some huntsmen, and teamsters, stablehands, "
            "maids and kitchen staff. Julia's foster parents count among "
            "the servants, in Dortmund. They live by hunting, gathering "
            "and logging, trading the surplus to the nearby village for "
            "produce; ten Mythic Pounds of silver sit in the coffers, and "
            "the hills could feed three times as many as they do.",
        ),
        what_matters=joined_lines(
            "Build Points: 650 known + 1000 hidden (devices 114+22, "
            "laboratories 20+110, Lab Texts 72, library 324+793, money 1, "
            "specialists 17, vis sources 95+75, vis stocks 5)",
            "Boon: Tame Nobleman (Herr Vorderhagen, vassal of the Count of "
            "Mark and formal lord of the lands)",
            "Boon: Hidden Resources (first of four, 1000 Build Points in "
            "all); Hidden Resources; Hidden Resources; Hidden Resources",
            "Boon: Manor House (the manor hall)",
            "Boon: Aura (Minor) (first of two: Magic 5); Aura (Minor)",
            "Boon: Strong Community (covenfolk here for generations, hard "
            "for outsiders to suborn)",
            "Boon: Chase (hunting, gathering and logging in the Count's "
            "hunting grounds, so long as Vorderhagen stays friendly)",
            "Hook: City (Dortmund's growth, guilds and goods; Julia risks "
            "charges of meddling)",
            "Hook: Mundane Politics (the Counts of Mark and Berg both know "
            "the magi and would use them)",
            "Hook: Uncontrolled Portal (first of two); Uncontrolled Portal",
            "Hook: Rights and Customs (old feast days, some leaving no one at work)",
            "Hook: Suffrage (Briana wrote women's equal rights into the charter)",
            "Hook: Vis Salary (the twice-yearly grant is earned by services)",
            "Council 1220: Ferra the Elder, Baliana the Governor, Tiberius "
            "the Armiger, Freki the Predator, Julia the Ambassador",
            "Allies: Herr Vorderhagen; at Durenmar Baliana's mentor Occultes "
            "and pater Marcellus, who winters there, and Philippus Niger of "
            "the Ash Gild, each of whom will want something back; Pancrestis "
            "of Heorot; Freki's clan at Crintera",
            "Rivals: Fengheld, wary of the old covenant's return, with "
            "its chapter house in Cologne and an eye on Dortmund, though "
            "Julia has ties through Stentorius; Freki's mater Oda at Crintera",
            "Neutral: no significant links to Oculus Septentrionalis, "
            "Waddenzee or Triamore in 1220, and the covenant has never used "
            "its veto on a new foundation; Heorot needs it in 1221",
        ),
        notes=paragraphs(
            "Story seeds. The Winter Litter: a whole litter of albino stoats "
            "in the snow, hunted by a crafty snow leopard from the portal "
            "that lays false trails; only Bjornaer leave lets it be hunted. "
            "The Mischievous Kobold: respected with food and asking, he only "
            "plays; slighted, he leads miners astray, steals tools or "
            "brings down the rock. Impossible Thefts: a visitor knows his "
            "plate, sold to him and stolen back overnight, before the armoire "
            "was found. A Simple Request: Vorderhagen would borrow the "
            "silverware for a week for the count's visit. Agents "
            "Provocateurs: mercenaries of the archbishop raid Mark from a "
            "camp in Berg. The Church Lands: to end a war, Adolph may cede a "
            "wild valley due south of the covenant for an abbey, through "
            "the archbishop's man Max von Beiderbecke, while Dortmund bids "
            "for it. The Enemy of My Enemy: Erich learns Count Frederick of "
            "Isenberg, tied to the Cologne diabolists, plots against the "
            "archbishop. Old Alliances: a Redcap's letter calls in forgotten "
            "pacts, from Urgen, Prima Falke or Waddenzee, who found a "
            "creature on the Norwegian coast. The Army of King Gorm: a "
            "faerie lord arrives through the portal to honour a pact of a "
            "year and a day, and assumes the archbishop is the enemy. The "
            "Ravens Fly Again: ravens over the woods toward Dortmund mark "
            "a lindorm's birth, as they did for the one Scipio went to stop.",
            "Storylines. Rebuilding: recover the lost resources, sell wood "
            "from the Woodshed and metal from the mine, and mind Dortmund's "
            "guilds. Counts and Bishops: the struggle of Mark and Cologne, "
            "with the Code ever near; the archbishop does not at first know "
            "of the lodge, and Adolph keeps the wizards in reserve. Reforging "
            "Relations: the Tribunals of 1221 and before 1228, Murion's "
            "wish to act against the Order of Odin, Daria la Gris's "
            "Lotharingian Tribunal, and the Harmonist and Wilderist rift. "
            "The Portals: save the great events until the covenant is "
            "strong; Scipio's sacrifice has bought decades.",
            "If the saga follows history: Adolph loses his northern lands "
            "between Dortmund and Soest to Engelbert until reconciled with "
            "the next archbishop, inherits from Frederick of Isenberg, and "
            "dies in 1249; Duke Henry III of Limburg is followed by Waleran "
            "III in 1221, and Henry IV takes Berg in 1225 and Limburg in "
            "1226; Engelbert is murdered by his cousin Frederick in 1225 and "
            "Heinrich I von Mullnarken follows; Cologne becomes a Free "
            "Imperial City in 1288.",
            "Ferra suits the troupe as a lightly used adviser; the four young "
            "magi suit players. Elsewhere: the covenant could move to any "
            "frontier Tribunal, which voids the gild Virtues. As a "
            "background covenant it offers trade, diplomacy and old lore.",
        ),
        secrets=paragraphs(
            "Hidden Resources. Searching takes a month with the chronicles, "
            "rolls and maps: a stress roll of Int + Organization Lore: Collem "
            "Leonis against 12, +3 for a whole season, leads to one of these "
            "stories: Franka's Hermetic Nursery, Joachim's Stolen Cache, the "
            "Tree House, the Armoire of Excess, the Portal of Living Wood "
            "and A Missing Bookcase.",
            "Apprentice's Lofty Cave. Franka of Bjornaer made off with the "
            "introductory books about 1195, on a preliminary leave from the "
            "council, meaning them for Bjornaer apprentices of owl heartbeast "
            "like her own. They lie wrapped in cloth and leather in a dry "
            "cave on a Bjornaer-only peak, whose mouth is the size of a large "
            "bird and reached only by flying. Authors' names have been "
            "removed; some may be Diedne. Adler watches the peak.",
            "Sins of the Predecessor. Joachim, tempted by a minor demon that "
            "breeds discontent with superiors, studied Goetic arts, stole "
            "books to sell to the merchant Ruprecht of Lübeck, and hid them "
            "in a cave in 1208. Repenting, he tried to bind the demon in a "
            "gold ring; it killed him, and his corpse still grips it, the "
            "ring's Magic Resistance guarding it from notice. Someone finds "
            "the ring while hunting and the demon goads him to dreadful "
            "acts; the trail leads to the cave, the books and Ruprecht's "
            "letters. The bound demon can use its powers and talk from the "
            "ring, but cannot leave it.",
            "The Dark Magus. Ruprecht was Imanitos Mendax of Jerbiton, here "
            "taken as a dark magus (Guardians of the Forests pp. 72-74), who "
            "corrupted Joachim and never got the books. He bullied Erich "
            "into spying, gave it up, and bides his time in a new guise in "
            "Dortmund and Cologne. Erich's Second Sight saw through his "
            "Imaginem disguise and would know him.",
            "Lost Laboratory. Agnes first dissuades intruders without harming "
            "them, and is easily won with courtesy; otherwise the vis is hard "
            "to take and the laboratory unusable.",
            "A Missing Bookcase. Ferra had grogs move a cabinet of spell "
            "mastery texts to a storeroom, forgot it in Twilight, and crates "
            "have buried it since. The rolls mention the move; only a search "
            "of the covenant finds it. A fire a decade ago ruined most other "
            "Lab Texts and mastery books.",
            "The kobold and Scipio: the kobold's story is under the "
            "creature; Scipio's fate is unknown.",
        ),
    )


def _people(rhine: Rhine, covenant: Covenant) -> None:
    b = rhine.b
    for key, name, house, age, _block, summary, hidden in MAGI:
        rhine.magi[key] = b.magus(
            name,
            covenant=covenant,
            house=house,
            age=age,
            summary=summary,
            secrets=hidden,
        )
    for key, name, kind, age, summary in PEOPLE:
        rhine.magi[key] = b.magus(
            name, covenant=covenant, house="", age=age, summary=summary, type=kind
        )
    rhine.magi["erich"] = b.magus(
        "Erich the Spy",
        covenant=covenant,
        house="",
        age=21,
        type="companion",
        summary=(
            "A goblin-blooded freelance spy of Dortmund who sells secrets "
            "from concealment, and most of his work to Renardus and now "
            "Julia, who buys his news regularly. He avoids Cologne."
        ),
        secrets=(
            "In Cologne his Second Sight showed him an invisible man and led "
            "him to a coven of diabolists, some of them powerful; he fled in "
            "terror and keeps it quiet for fear of being sent back. Ruprecht, "
            "a merchant of that coven, later cowed him into spying on the "
            "magi. He told nothing of worth, and Ruprecht stopped coming, "
            "but he lives in dread of his return."
        ),
    )
    rhine.magi["paul"] = b.magus(
        "Paul the Spearman",
        covenant=covenant,
        house="",
        age=32,
        type="grog",
        summary=(
            "The seasoned sentry of the turb, always on watch when something "
            "strange happens and always along on the memorable expeditions."
        ),
    )


def _world(rhine: Rhine, covenant: Covenant) -> None:
    b, w = rhine.b, rhine.world
    lowlands = rhine.places["lowlands"]
    w["dortmund"].summary = paragraphs(
        w["dortmund"].summary,
        "Rebuilt after a great fire in 1152 and swollen by Frederick "
        "Barbarossa's long stay, it became a Free Imperial City in 1220, its "
        "trade and craft guilds now a power in the land. The Tremere of "
        "Collem Leonis have traded here since the covenant's founding, and "
        "evil tongues say they helped it rise.",
    )
    mark = b.lord(
        "Adolph I, Count of Mark",
        title="count",
        manors=0,
        place=lowlands,
        summary=(
            "One of Westphalia's most influential lords, of a house split "
            "from Berg as Berg-Althena and renamed Mark in 1202, and a leader "
            "of the opposition to Archbishop Engelbert, his cousin. He knows "
            "his vassal harbours wizards in useless, dangerous hills, likes "
            "it so, and supposes he can call on them for a hard hunt or "
            "counsel. Having granted Dortmund its charter, he has much to "
            "lose near it."
        ),
    )
    vorderhagen = b.lord(
        "Herr Vorderhagen",
        manors=0,
        seat="Micklingshaus",
        answers_to=mark,
        place=rhine.places["sauerland"],
        summary=(
            "A vassal knight of the Count of Mark, whose manor in the village "
            "of Micklingshaus lies outside the wild hills, and the formal "
            "lord of Collem Leonis, his family holding the lands for two "
            "generations."
        ),
        secrets=(
            "The Flambeau and Tremere of the covenant have made his family "
            "their puppet over generations. He is a willing ally, since the "
            "wizards help keep his unhereditary lands in the family, but "
            "secretly fears them and keeps a little distance, which suits "
            "them."
        ),
    )
    reinhart = b.lord(
        "Reinhart II, Freiherr of Soest",
        manors=0,
        answers_to=mark,
        place=lowlands,
        summary=(
            "Tiberius's elder brother, lately heir to Reinhart I, with lands "
            "at the east of Mark against the bishoprics of Münster and "
            "Paderborn, a reluctant supporter of the count. He will not speak "
            "to his black-sheep brother, so his enemies strike at Tiberius "
            "without fear."
        ),
    )
    b.link(reinhart, "characters", rhine.magi["tiberius"], "his younger brother")
    julich = b.lord(
        "William IV, Count of Jülich",
        title="count",
        manors=0,
        place=rhine.places["rhine_valley"],
        summary=(
            "Son of William III and Mathilda of Limburg, whose family ties "
            "bind his county to Limburg against the archbishop of Cologne."
        ),
    )
    coven = b.faction(
        "The Cologne coven",
        realm="Infernal",
        place=rhine.places["rhine_valley"],
        summary="A secret circle in Cologne, known to few.",
        secrets=(
            "A coven of diabolists, some of them men of power, whom Erich "
            "stumbled on a few years ago; Ruprecht, that is Imanitos Mendax, "
            "takes part in its rites, and Count Frederick of Isenberg is "
            "tied to it."
        ),
    )
    for record, note in (
        (w["archbishop_of_cologne"], "enemy of the count of Mark"),
        (mark, "liege of Herr Vorderhagen"),
        (vorderhagen, "the covenant's formal lord"),
        (julich, "ally of Mark's cause"),
        (w["dukes_of_limburg"], "at odds with the archbishop"),
        (w["dortmund"], "Julia's townhouse and business"),
        (coven, "unknown to the magi"),
    ):
        b.link(covenant, "places", record, note)


def _laboratories(rhine: Rhine, covenant: Covenant) -> None:
    b = rhine.b
    b.laboratory(
        covenant,
        "Ferra's laboratory",
        owner=rhine.magi["ferra"],
        characteristics={
            "general_quality": 2,
            "safety": -1,
            "health": -1,
            "refinement": 3,
            "upkeep": 4,
            "aesthetics": 5,
        },
        specializations={
            "Texts": 1,
            "Creo": 1,
            "Rego": 7,
            "Imaginem": 1,
            "Mentem": 6,
        },
        source="Through the Aegis p. 146",
        rooms={
            "The upper floor": (
                "Reshaped by her Terram magic. Virtues: Greater Feature "
                "(Summoning Circle), Greater Expansion, Living Quarters, "
                "Specimens (bound ghosts), Superior Construction, Superior "
                "Lighting, Highly Organized, Servant (Otto, Int +2), Spotless. "
                "Flaws: Greater Focus (summoning circle), Missing Equipment, "
                "No Stores, Undecorated. No Binding Familiar or Experimentation "
                "for want of equipment. Marker: Heinrich."
            )
        },
    )
    for key in ("baliana", "freki", "tiberius", "julia"):
        magus = rhine.magi[key]
        b.laboratory(
            covenant,
            f"{magus.name}'s laboratory",
            owner=magus,
            characteristics={},
            specializations={},
            source="Through the Aegis p. 146",
            rooms={"The upper floor": "A standard laboratory, not yet personalized."},
        )
    for number in (1, 2, 3):
        b.laboratory(
            covenant,
            f"Unmaintained laboratory {number}",
            characteristics={
                "general_quality": -1,
                "safety": -2,
                "health": -3,
                "upkeep": -5,
                "aesthetics": -5,
            },
            specializations={},
            source="Through the Aegis p. 146",
            rooms={
                "The upper floor": (
                    "Fitted out for guests, a century neglected and full of "
                    "refuse. Virtues and Flaws: Hovel, Missing Equipment (x3), "
                    "Missing Sanctum Marker. No Inventing Spells, Enchanting "
                    "Devices, Binding Familiars or Extracting Vis."
                )
            },
        )


def _devices(covenant: Covenant) -> None:
    for name, words in DEVICES:
        add_possession(covenant, "item", name, description=words)
    add_possession(
        covenant,
        "property",
        "Julia's townhouse",
        location="Dortmund",
        inhabitants="Julia and her foster parents",
        description=(
            "An old, well-kept house, an unofficial site of the covenant. "
            "Frederick's shop fills the ground floor, its front room a "
            "living space by night, with kitchen and stair behind, a "
            "cellar and a back shed; Julia's stylish reception chamber is "
            "upstairs. She has books brought here to study, and has thought "
            "of moving her laboratory, which might look like a chapter house."
        ),
    )


def _book(
    b: Builder,
    covenant: Covenant,
    entry: tuple[str, str, str, str, int | None, int],
    words: str,
) -> None:
    kind, name, author, subject, level, quality = entry
    art, ability = (subject, "") if subject in ARTS else ("", subject)
    b.book(
        covenant,
        name,
        kind,
        art=art,
        ability=ability,
        level=level,
        quality=quality,
        author=author,
        description=words,
    )


def _library(b: Builder, covenant: Covenant) -> None:
    for kind, name, author, subject, level, quality, words in LIBRARY:
        _book(b, covenant, (kind, name, author, subject, level, quality), words)
    for name, technique, form, level, words in LAB_TEXTS:
        book = b.book(
            covenant, f"Lab Text: {name}", "Lab Text", level=level, description=words
        )
        book.text_kind, book.spell_name = TEXT_SPELL, name
        book.technique, book.form = technique, form


def _vis(covenant: Covenant) -> None:
    for name, art, pawns, season, words in (
        (
            "Silver Spring",
            "Vim",
            8,
            "Spring",
            "On the first day of spring a snowmelt stream runs silver; caught "
            "before it touches the ground over a day, the trickle holds the "
            "vis. Marked with the covenant's symbol and registered, as are "
            "all its sources.",
        ),
        (
            "Albino Stoat",
            "Animal",
            4,
            "Autumn",
            "A half-tame family of stoats always has one albino in a litter, "
            "which grows into a blood rage and raids the chicken coop. Killed "
            "with the skin unbroken and drained, its blood holds the vis, "
            "which appears only as the rage nears. No one has tried to catch "
            "or breed it.",
        ),
        (
            "Blue Stones of the Mine",
            "Terram",
            7,
            "Summer",
            "Dark blue specks on the mine walls swell to fist-sized bulbs and "
            "fall like ripe fruit; left a few days they melt to a purple "
            "stain. Gathering is easy, but the records warn of the kobold.",
        ),
    ):
        add_possession(
            covenant,
            "vis_source",
            name,
            art=art,
            pawns=pawns,
            season=season,
            description=words,
        )
    add_possession(
        covenant,
        "vis_store",
        "The vault's Vim",
        art="Vim",
        pawns=15,
        physical_form="silver liquid",
        description=(
            "The vault's table gives 15 pawns and 5 Build Points overall; the "
            "text beside it says 25."
        ),
    )
    add_possession(
        covenant,
        "vis_store",
        "The vault's Terram",
        art="Terram",
        pawns=10,
        physical_form="blue stones",
    )


def _hidden(b: Builder, covenant: Covenant) -> None:
    lost = "Lost from the library; it is not at hand in 1220."
    for entry in NURSERY:
        _book(
            b,
            covenant,
            entry,
            secrets(
                f"{lost} Its author's name has been removed.",
                "In Franka's cave on the Bjornaer peak (Hidden Resources: "
                "Franka's Hermetic Nursery).",
            ),
        )
    for entry in CACHE:
        _book(
            b,
            covenant,
            entry,
            secrets(
                lost,
                "In Joachim's cave, stolen in 1208 (Hidden Resources: "
                "Joachim's Stolen Cache). The Goetic texts were his own; "
                "Goetic Arts are Accelerated Abilities (RoP: The Infernal "
                "pp. 114-119, 126).",
            ),
        )
    for entry in BOOKCASE:
        _book(
            b,
            covenant,
            entry,
            secrets(
                lost,
                "In a cabinet buried behind crates in a storeroom (Hidden "
                "Resources: A Missing Bookcase).",
            ),
        )
    b.laboratory(
        covenant,
        "Holzstein's laboratory",
        characteristics={
            "size": 3,
            "general_quality": -3,
            "safety": 1,
            "health": 1,
            "upkeep": -1,
            "warping": 1,
            "aesthetics": 2,
        },
        specializations={"Perdo": 3, "Rego": 1, "Herbam": 11},
        source="Through the Aegis p. 156",
        rooms={
            "Inside the oak": secrets(
                "Lost since the Schism War, and no one's now.",
                "Built in a magical oak, its regio giving extra room. Virtues: "
                "Greater Feature (tree), Lesser Guardian (Agnes), Pot Plants, "
                "Spacious, Idyllic Surroundings, Dedicated Building, Regio. "
                "Flaws: Greater Focus (tree), Decaying, Dirty, Infested, "
                "Missing Equipment (Texts), Missing Ingredients (Ignem, "
                "Terram). Lab Totals with Ignem and Terram are halved, and no "
                "work on Texts is possible. No names on its marker. 110 Build "
                "Points.",
            )
        },
    )
    add_possession(
        covenant,
        "item",
        "A carved walnut armoire",
        description=secrets(
            "A large, flawless, intricately carved cabinet with one door "
            "jammed shut, used to store things; no servant now knows what it "
            "was for.",
            "The Armoire of Excess, invested by Amadeus of Bonisagus, opened "
            "with 10 pawns, 6 used. Silverware of the Wastrel (CrTe 53, 6 a "
            "day, R: Touch, D: Sun, T: Group): twist both handles and open "
            "both doors together for a banquet service for 50, which "
            "vanishes at sunset. Something is stuck in a door, and it no "
            "longer works. Records name it, and Intellego Vim finds it "
            "fastest. Saves two laborers. 22 Build Points.",
        ),
    )


def _charter(covenant: Covenant) -> None:
    charter = covenant.charter_of_covenant
    charter.name = "The Charter of Collem Leonis"
    charter.preamble = (
        "Drawn up thoroughly at the founding and unchanged since its first "
        "decade, its hierarchy now seems archaic for five magi, but must "
        "still be followed. Services count for more than age, which matters "
        "for only one seat. The Peripheral Charter gathers council rulings, "
        "reasons unstated, and holds that they are not to be questioned."
    )
    charter.clauses = [
        CharterClause(number=str(number), text=text, section=section)
        for number, (section, text) in enumerate(CHARTER, 1)
    ] + [
        CharterClause(number=f"Peripheral {number}", text=text)
        for number, text in enumerate(PERIPHERAL_CHARTER, 1)
    ]


def _history(b: Builder, covenant: Covenant) -> None:
    for year, title, details in (
        (
            858,
            "The first cycle begins",
            "Wolfgang and Adler of Bjornaer, led here by a Great Beast lion "
            "in the late 850s, find beasts foreign to Germany tied to "
            "regiones that open at random.",
        ),
        (
            865,
            "Collem Leonis founded",
            "With Tacitus of Tremere and Pamprepius of Flambeau, unopposed. "
            "Those two win the land's Waldgraf and Herr Reginald over: the "
            "hills become his hunting grounds and the keep his lodge. "
            "Amadeus and Briana of Bonisagus soon join, counted as founders.",
        ),
        (
            1000,
            "Autumn and the Schism War",
            "The Bjornaer withdraw to Crintera, the Flambeau go to war and "
            "not all return. Fewer magi, each stronger.",
        ),
        (
            1152,
            "Dortmund rebuilt",
            "From the 1150s the Tremere settle at Dortmund, which grows after "
            "its great fire and Barbarossa's stay.",
        ),
        (
            1195,
            "Winter",
            "About now the library's introductory books go missing. Toward "
            "the century's end outsiders see Winter come; magi drift away, "
            "and the last agree to train one generation of apprentices and "
            "hand it over.",
        ),
        (
            1208,
            "Joachim vanishes",
            "The autocrat disappears with books and magical resources, and "
            "Johanna takes his office.",
        ),
        (
            1214,
            "Scipio's last stand",
            "With a known lindorm grown large enough to attack, Scipio enters "
            "the portal once Tiberius has sworn, and is never seen again; "
            "no attack comes. Oda retires to Crintera, Marcellus takes to "
            "the roads and winters at Durenmar, Renardus goes to Coeris "
            "once Julia swears in 1219, and Ferra stays as adviser.",
        ),
    ):
        b.chronicle(covenant, year, title, details)


def _creatures(b: Builder, covenant: Covenant, places: dict[str, Neighbour]) -> None:
    lindorm = b.creature(
        "Lindorm of Jotunheim",
        page="p. 159",
        source=SOURCE,
        realm="Magic",
        might=30,
        form="Animal",
        size=13,
        place=places["jotunheim"],
        block={
            "characteristics": characteristics(-1, -1, -6, -6, 22, 2, 1, -12),
            "virtues_flaws": [
                "Magic Animal",
                "Magical Monster",
                *["Improved Characteristics"] * 6,
                *["Gigantic"] * 12,
                *["Greater Power"] * 4,
                "Monstrous Appearance",
                *["Reduced Might"] * 4,
            ],
            "abilities": [
                ("Awareness", 5, "hearing"),
                ("Brawl", 6, "bite"),
                ("Penetration", 5, "blood"),
                ("Survival", 3, "forest"),
                ("Swim", 4, "speed"),
            ],
            "traits": {"Lindorm": 3, "Hungry for Magic": 3, "Angry": 3},
            "reputations": {"Lethal and venomous (local, in Nordic cultures only)": 5},
        },
        attacks=[
            b.attack("Grapple", -12, 13, -4, 22),
            b.attack("Large Teeth", -12, 18, -4, 25),
        ],
        soak=17,
        fatigue_levels="OK, 0, 0, 0, -1, -3, -5, Unconscious",
        powers=[
            b.power(
                "Blood of Venom",
                0,
                0,
                "Animal",
                level=50,
                does="Always on. Its blood turns corrosive as it leaves the "
                "body: whoever deals a Medium or worse wound rolls Qik - Enc "
                "against 9, 12 for Heavy, 15 for Incapacitating or worse; "
                "those near roll against 9. Failure takes +25 damage, repeated "
                "each round at -1 damage and -1 Protection until the roll is "
                "0, the armor or poison is off, or two minutes pass.",
            ),
            b.power(
                "Breath of Venom",
                1,
                -14,
                "Aquam",
                level=70,
                does="In place of a bite, spews venom on a target within 15 "
                "paces: it hits automatically and does +25 if it Penetrates, "
                "and may splash others for +12 unless they make Qik - Enc "
                "against 9.",
            ),
            b.power(
                "Magical Senses",
                0,
                0,
                "Vim",
                level=80,
                does="Always on. Smells auras, vis, enchanted devices, "
                "creatures with Might and the Gifted within a mile, and is "
                "drawn to consume, rest, fight or seize.",
            ),
        ],
        vis=None,
        appearance=(
            "A vast serpent, some 10 feet thick and almost 400 long, with "
            "angry red eyes, teeth like greatswords, dark spiny ridges, "
            "bright green scales and a wrinkled bilious belly."
        ),
        notes=paragraphs(
            "Magic Animal, Magical Monster; Improved Characteristics (x6); "
            "Poor Communication (x2), Poor Presence. Qualities also: Reduced "
            "Communication, Reduced Presence, Minor Flaw (Poor Presence). "
            "Mundane Qualities: Grapple, Keen Sense of Smell, Large Teeth, "
            "Loathsome Appearance, Spiny, Tough Hide, Thick Scales, Sharp "
            "Ears, Slippery, Venomous. Brawl has +2 from Puissance. Wounds "
            "-1 (1-18), -3 (19-36), -5 (37-54), Incapacitated (55-72), Dead "
            "(73+).",
            "Constriction, not magical: it grapples and constricts targets "
            "up to a total Size of +7, who suffer air Deprivation; those of "
            "Size +2 or less it rolls under its body. Scales, not magical: "
            "Soak +17 normally; +10 against blows at the belly (Finesse or "
            "Athletics against 12 suggested); +25 fortified, good against "
            "massed arrows. Venomous, not magical: a bite whose Attack "
            "Advantage beats the target's Protection adds a Light wound, as "
            "does any combat botch in melee, on a spine.",
            "Vis: 4 pawns of Perdo in the heart, 2 of Animal in the body, and "
            "whatever it has eaten in its stomach.",
        ),
        secrets=(
            "Ravens over the woods mark its birth from the earth, and their "
            "flight shows its path. It stops to eat vis and burrows to "
            "digest it, sometimes for months, growing all the while."
        ),
    )
    b.link(covenant, "creatures", lindorm, "behind the portals")
    agnes = b.creature(
        "Agnes",
        page="p. 156",
        source=SOURCE,
        realm="Magic",
        might=10,
        form="Herbam",
        size=-1,
        age="Not applicable (15)",
        confidence=(1, 3),
        encumbrance="0 (0)",
        place=places["tree_house"],
        level=1,
        block={
            "characteristics": characteristics(0, 3, 0, 1, -1, 3, 0, 0),
            "virtues_flaws": [
                "Magic Spirit",
                ("Greater Immunity", {"detail": "Perdo Vim"}),
                ("Ways of the {land}", {"land": "Forest"}),
                "Improved Characteristics",
                "Tough",
                "Unaffected by The Gift",
                ("Bound to {realm}", {"realm": "Magic"}),
                "Magical Air",
                ("Ability Block", {"detail": "Logic"}),
                ("Ability Block", {"detail": "Martial"}),
                ("Anchored to the {land}", {"land": "Forest"}),
                "Generous (Minor)",
                "Incomprehensible",
                "Small Frame",
                ("Focus Power", {"focus": "Crafter of Herbam"}),
                ("Focus Power", {"focus": "Master of Herbam"}),
                "Greater Power",
                "Improved Powers",
            ],
            "abilities": [
                ("Area Lore: Sauerland", 3, "geography"),
                ("Awareness", 3, "searching"),
                ("Concentration", 3, "spirit powers"),
                ("Finesse", 4, "Herbam"),
                ("Forest Lore", 3, "native forest"),
                ("Living Language: High German", 5, "magi"),
                ("Dead Language: Latin", 1, "Hermetic"),
                ("Leadership", 2, "inspiration"),
                ("Magic Lore", 2, "creatures"),
                ("Organization Lore: Collem Leonis", 3, "history"),
                ("Penetration", 4, "Herbam"),
                ("Stealth", 5, "natural areas"),
            ],
            "traits": {
                "Generous": 3,
                "Forest Lover": 3,
                "Whimsical": 2,
                "Brave": -1,
            },
        },
        attacks=[b.attack("Dodge", 0, None, 0, None)],
        soak=6,
        fatigue_levels="OK, 0, -1, -3, -5, Unconscious",
        powers=[
            b.power(
                "Donning the Corporeal Veil",
                0,
                -1,
                "Herbam",
                does="A body of wood, tough as old oak and supple as flesh, "
                "with sap for blood. It is renewed each sunrise and sunset, "
                "ages and hungers, and is remade at least monthly to stay "
                "young; if it is killed she is destroyed, but she can dissolve "
                "it at will. RoP: Magic pp. 38-39, 102.",
            ),
            b.power(
                "Crafter of Herbam",
                1,
                1,
                "Herbam",
                does="1 point a magnitude, Init 1 - magnitude: any Creo Herbam "
                "effect to level 25.",
            ),
            b.power(
                "Master of Herbam",
                1,
                0,
                "Herbam",
                does="1 point a magnitude, Init - magnitude: any Rego or Muto "
                "Herbam effect to level 20.",
            ),
        ],
        equipment=(
            "A simple dress in the forest's present colours, a woven leather "
            "belt, a bronze sickle."
        ),
        appearance=(
            "A healthy young woman with golden almond eyes and dark curly "
            "hair with oak leaves growing in it."
        ),
        notes=(
            "A minor forest spirit, lonely since the sanctum fell empty, "
            "who has kept it adequately. Wounds -1 (1-4), -3 (5-8), -5 (9-12), "
            "Incapacitated (13-16), Dead (17+). Vis: 2 pawns of Herbam in the "
            "leaves of her hair."
        ),
        secrets=(
            "Bound by her own will to Holzstein's laboratory. Suspicious of "
            "intruders, but with respect and kindness she will gladly bond "
            "with a new master."
        ),
    )
    b.link(covenant, "creatures", agnes, "guardian of the lost laboratory")
    kobold = b.creature(
        "The kobold of the mine",
        page="p. 155",
        source=SOURCE,
        place=places["eisenhohe"],
        notes=(
            "The book gives no statistics or realm, and calls him old. Treated with "
            "respect and small gifts he merely moves things and makes noises "
            "in the dark, and may answer a sincere plea; abused, he leads "
            "men into dangerous tunnels by illusions, steals their gear, or "
            "weakens the rock. Many a vis harvest has met him."
        ),
    )
    b.link(covenant, "creatures", kobold, "in the mine")
    adler = b.creature(
        "Adler",
        page="p. 155",
        source=SOURCE,
        realm="Magic",
        might=30,
        size=-1,
        block={"characteristics": {"perception": 5}},
        cunning=True,
        notes=(
            "The book gives Size -1, Perception +5 and Might 30 only, with "
            "only Cunning, and refers to the Eagle of Virtue (Houses of "
            "Hermes: Mystery Cults p. 41)."
        ),
        appearance="A very large, near-perfect eagle.",
        secrets=(
            "The founding maga, who took her eagle heartbeast as a Great "
            "Beast at her Final Twilight, and watches the peak where "
            "Franka's books lie. She hinders climbers, the non-Bjornaer most, "
            "with her powers, and stays hidden unless a Bjornaer seeks her "
            "with respect."
        ),
    )
    b.link(covenant, "creatures", adler, "watcher of the Bjornaer peak")
    gorm = b.creature(
        "Gorm",
        page="p. 158",
        source=SOURCE,
        realm="Faerie",
        place=places["midgard"],
        notes=(
            "A powerful faerie lord who plays a king of the northmen; the "
            "book gives no statistics. He knows the current politics but "
            "nothing of magi, and takes any magus to speak for Collem Leonis. "
            "He can reshape his host's look and wear any heraldry. Diplomacy "
            "may turn him to subtler help."
        ),
    )
    b.link(covenant, "creatures", gorm, "owed a forgotten pact")
