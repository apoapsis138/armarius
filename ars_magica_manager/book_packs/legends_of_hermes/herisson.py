"""The Magical Garden of Hérisson, Legends of Hermes chapter four (pp. 70-94),
as of 1220: Hérisson and his slayer as sketches, Hérisson's heirs and the
magi of Caerfloron, Richard Strabo in full, the buried field, Variña's Tomb,
Caerfloron and the Garden as places, the owl and the four great plants as
creatures, and the chapter's stories as dormant threats.

The book leaves the sites' locations to the storyguide, so they stay blank.
Caerfloron is a place, not a covenant, since this pack has no covenants; its
Aegis is in words. The Garden's treasures and laboratory are in words in its
Secrets, since a device or a Laboratory record needs an owning covenant.
Hermetic Viresculture (pp. 72-76) is in the app's rules and is only cited
here. The errata's correction to the tomb's map is followed: the regio
boundaries are the text's. The rest is a summary of the book, not its words.

Left out of the blocks, the catalog having no such entry, and named in each
record's notes:
Powers Inferiority. A Personality Flaw printed without a tier is taken as
Major where it heads the block's Flaws."""

from __future__ import annotations

from typing import Any

from ...models import BodyVis, Neighbour
from ..builder import (
    Builder,
    StatBlock,
    arts_from,
    characteristics,
    dormant,
    paragraphs,
    vf_art,
    vf_focus,
    vf_minor,
    vf_puissant,
)

SOURCE = "LoH"
BJORNAER = "house_bjornaer"
BONISAGUS = "house_bonisagus"
EX_MISCELLANEA = "house_ex_miscellanea"
HERBAM = "Herbam"
MAGIC = "Magic"
FATIGUE = "OK, 0, -1, -3, -5, Unconscious"
RUMOURED: dict[str, Any] = {"status": "Rumoured", "known": "In the Order"}
LOCAL: dict[str, Any] = {"status": "Rumoured", "known": "Locally"}
S = Builder.stage
#: A location the book leaves to the storyguide.
OPEN_SITE = "The book leaves where this lies to the storyguide."

HOMUNCULUS = (
    "A Homunculus Wizard of Realms of Power: Faerie chapter 5: a manikin made "
    "of a Mandrake of Virtue from Hérisson's Garden is the source of the "
    "wizard's magic, gained on one visit at the start of the career. The "
    "tradition gives Greater Immunity (Deprivation), Faerie Magic and the "
    "Homunculus Wizard Flaw, and all share Disfigured: a green tinge to skin "
    "and hair. No wounds or Fatigue from want of food, drink or air, but "
    "Long Term Fatigue returns only with rest and sustenance; the body runs "
    "on the vegetative spirit woken by daylight. Not of House Merinita, so "
    "barred from its Inner Mysteries (p. 83)."
)

STRABO: StatBlock = {
    "characteristics": characteristics(2, 2, -1, -1, -1, 2, 1, 0),
    "confidence": (1, 3),
    "decrepitude": (0, 0),
    "warping": (4, 18),
    "apparent_age": 40,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Flexible Formulaic Magic",
        "Adept Laboratory Student",
        vf_art("Affinity with {art}", HERBAM),
        "Social Contacts",
        "Gild Trained",
        "Inventive Genius",
        vf_focus("Minor Magical Focus", "vines"),
        vf_puissant("Magic Theory"),
        "Skilled Parens",
        "Dark Secret",
        "Driven (Major)",
        "Waster of Vis",
        "Reclusive",
    ],
    "traits": {"Ambitious": 5, "Ruthless": 3, "Reclusive": 2},
    "reputations": {"House Acclaim (Hermetic)": 2},
    "abilities": [
        ("Artes Liberales", 3, "rhetoric"),
        ("Concentration", 2, "Herbam"),
        ("Faerie Lore", 2, "wood faeries"),
        ("Finesse", 4, "Herbam"),
        ("Living Language: German", 5, "Swabian"),
        ("Guile", 2, "disguise"),
        ("Dead Language: Latin", 5, "Hermetic"),
        ("Living Language: Local", 4, "appropriate dialect"),
        ("Magic Lore", 2, "magical plants"),
        ("Magic Theory", 8, "original research"),
        ("Medicine", 5, "theriacs"),
        ("Organization Lore: Order of Hermes", 2, "Herbam specialists"),
        ("Parma Magica", 4, "Ignem"),
        ("Penetration", 3, "Herbam"),
        ("Philosophiae", 2, "exotic plants"),
        ("Profession: Apothecary", 4, "poisonous plants"),
        ("Profession: Scribe", 2, "summae"),
        ("Stealth", 2, "woodland"),
        ("Teaching", 2, "Herbam"),
    ],
    "arts": arts_from(
        "Cr 10, In 7, Mu 12, Pe 5, Re 8, An 5, Aq 5, Au 6, Co 12, He 14, Ig 5, "
        "Im 5, Me 5, Te 6, Vi 10"
    ),
    "spells": [
        ("Disguise of the New Visage", "MuCo", 10, 0),
        ("Shape of the Creeping Ivy", "MuCo(He)", 35, 0),
        ("Conjure the Sturdy Vine", "CrHe", 5, 0),
        ("The Giant's Beanstalk", "CrHe", 15, 0),
        ("The Chokeweed Incantation", "CrHe", 15, 0),
        ("Trap of the Entwining Vines", "CrHe", 15, 0),
        ("Wall of Thorns", "CrHe", 20, 0),
        ("The Envenomed Thorns", "CrHe", 25, 0),
        ("Intuition of the Forest", "InHe", 10, 0),
        ("Piercing Shaft of Wood", "MuHe(Re)", 10, 2),
        ("Transformation of the Thorny Staff", "MuHe", 10, 2),
        ("Coils of the Entangling Plants", "ReHe", 20, 0),
        ("Free the Crawling Vine", "ReHe", 20, 0),
        ("Lord of the Trees", "ReHe", 25, 0),
        ("The Treacherous Spear", "ReHe", 25, 0),
        ("Free the Striding Tree", "ReHe", 30, 0),
    ],
    "masteries": {
        "Piercing Shaft of Wood": ["Multiple Casting", "Penetration"],
        "Transformation of the Thorny Staff": ["Fast Casting", "Multiple Casting"],
    },
    "notes": paragraphs(
        "A man who looks to be in his middle years, dark-haired and "
        "weathered by the sun, with a fixed, hungry glint in the eye that "
        "unsettles people. He goes in a green cloak and a broad hat and "
        "never lays down his staff. Strabo is a name borrowed from a "
        "celebrated gardening monk, whose first name he sometimes uses as "
        "the alias Walahfrid. Sigil: the smell of damp earth. Twilight "
        "scars: arms like twisted roots; fruit does not spoil near him; he "
        "goes bald in winter.",
        "Combat: evasion Init 0, Attack n/a, Defense 0, Damage n/a. Soak +2. "
        "Fatigue OK, 0, -1, -3, -5, Unconscious. Wounds -1 (1-5), -3 (6-10), "
        "-5 (11-15), Incapacitated (16-20), Dead (21+). Teaching 2 has 5 "
        "more experience points. Puissant Magic Theory is starred in the "
        "block, with no note to say why.",
        "Talisman: a twisted, gnarled staff of ivy with leaves carved from "
        "six woods. Attunements: +3 affect living wood (wood), +3 Creo "
        "Herbam (almond). It holds two effects.",
        "The Nimble Vine, Cr(Re)He 35, Penetration 20, unlimited uses: a "
        "strong vine as supple as an arm, eight inches thick and up to 500 "
        "paces long, extending at a walking pace, that grips, fetches, "
        "strangles or wields a weapon at the wielder's word, on the wielder's "
        "Finesse in place of any Ability. It cannot be directed when the "
        "wielder cannot see its hand. (Base 1, +1 Touch, +1 Conc, +2 size, "
        "+1 requisite; +5 maintains concentration, +10 unlimited uses, +10 "
        "Penetration 20.)",
        "The Thrusting Root, Cr(Re)He 28, Penetration 20, 6/day: a spear-like "
        "ram shoots from the staff at anyone within 15 paces, for +10 damage. "
        "A Medium or worse wound pins the target, who cannot move but may "
        "attack the root. It can also batter doors and walls, forcing a "
        "Stress Check (City & Guild p. 77). (Base 1, +2 Voice, +1 Conc, +1 "
        "size, +1 requisite; +5 maintains concentration, +3 6/day, +10 "
        "Penetration 20.)",
        "Casting Scores as printed (* Minor Magical Focus, T talisman "
        "attunement): Disguise of the New Visage +26; Shape of the Creeping "
        "Ivy +38*; Conjure the Sturdy Vine +39*T; The Giant's Beanstalk "
        "+39*T; The Chokeweed Incantation +39*T; Trap of the Entwining Vines "
        "+39*T; Wall of Thorns +29T; The Envenomed Thorns +29T; Intuition of "
        "the Forest +23; Piercing Shaft of Wood +26; Transformation of the "
        "Thorny Staff +30; Coils of the Entangling Plants +24; Free the "
        "Crawling Vine +32*; Lord of the Trees +27T; The Treacherous Spear "
        "+24; Free the Striding Tree +27T.",
        "Disguise of the New Visage is a Personal variant at level 10, not "
        "the general level 15. Free the Striding Tree is printed so here; "
        "the Definitive Edition's spell is Freeing the Striding Tree.",
        "Presented as a magus of the Rhine, but any fitting character will "
        "serve, so long as he is no prominent figure of the characters' own "
        "Tribunal. Richard Caespuus of Durenmar (Guardians of the Forests p. "
        "58) suits, if the troupe accepts that whoever fills the part will "
        "likely face a Wizard's March. Built to test young magi; make him "
        "older for seasoned ones. He is a spy in plant form and a harasser, "
        "not a duellist (pp. 80-81).",
    ),
}


def _people(b: Builder) -> None:
    """Hérisson, his slayer, his heirs, and the magi of Caerfloron."""
    b.magus(
        "Hérisson of Bjornaer",
        covenant=None,
        house=BJORNAER,
        age=None,
        summary=paragraphs(
            "c. 857-1002. A magus of Clan Arelie whose heartbeast was the "
            "urchin, or hedgehog, and whose sigil ran to spines and thorns; "
            "a copper urchin was his voting sigil. He left his apprenticeship "
            "in 881 in Normandy and was at first an unremarkable worker of "
            "Herbam and magical agriculture. His House feared that mankind "
            "was killing Magic as forests fell, and some talked of culling "
            "the people; he held that Magic was boundless and went off to a "
            "backwater of his Tribunal to prove it.",
            "As the Order drifted toward the Schism he preached peace, "
            "offered his research to House Bonisagus and put his theories to "
            "convocations of House Diedne. Few believed he could grow vis. "
            "His House tired of him and distrusted his dealings; Gypaetus of "
            "Bjornaer accused him of betraying cult secrets and declared "
            "Wizard's War. Past a hundred years old and no fighter, he was "
            "dead within two days of the full moon. While the House sat out "
            "the Schism in its domus magna, the head of Clan Arelie studied "
            "his political writings, and by 1019 half the clans had declared "
            "for living alongside mankind: the Concordiarii, or Harmonists.",
            "What the Order Remembers (Intelligence + Order of Hermes Lore, "
            "simple roll; +1 for Bjornaer, +3 for Clan Arelie, the House's "
            "memory; a character recalls everything up to the Ease Factor "
            "reached, and some of it may be false; Introduction pp. 10-11).",
            "Ease Factor 0, Known by All: a magus of the ninth and tenth "
            "centuries; he built a magical Garden overflowing with vis, never "
            "yet found.",
            "Ease Factor 6, Widely Known: the Harmonists' founder, at least "
            "in name; a hedgehog heartbeast; he claimed he could grow all but "
            "limitless vis and was never taken seriously; he died in Wizard's "
            "War at the hands of his own House.",
            "Ease Factor 12, Uncommon Knowledge: Gypaetus of Bjornaer slew "
            "him; he quarrelled with his House and Primus, and was accused of "
            "showing House secrets to House Diedne.",
        ),
        secrets=paragraphs(
            "Ease Factor 18, Lost Secrets: he may descend from Myanar; some "
            "think his spirit lives on in his Garden; a copy of part of his "
            "research went to the Great Library at Durenmar.",
            "He was a theorist of the first rank who completed a Major "
            "Breakthrough, Hermetic Viresculture, and a Minor one extending "
            "it to Lesser Enchantment Vis (pp. 72-76). He was working toward "
            "making Lesser Enchantment Vis, and on the vis in gems and "
            "metals, when he died. He never made the method general.",
            "A Descendant of Myanar? (pp. 71-72) Tales give him Nature "
            "Mysteries like House Merinita's, and the Garden's sentient "
            "plants look like the work of Awakening Nature (Houses of Hermes: "
            "Mystery Cults p. 104). He may come of a follower of Myanar who "
            "fled to House Bjornaer when Quendalon became Primus. Magi who "
            "know the Nature Mysteries may ask whether he took Guardian of "
            "Nature and became a genius loci, his death a staged way out of "
            "the Order. If so he may haunt the Garden as its spirit, and if "
            "he belonged to a hidden Bjornaer cult his heirs may keep it "
            "still. The book does not settle any of this.",
        ),
    )
    b.magus(
        "Gypaetus of Bjornaer",
        covenant=None,
        house=BJORNAER,
        age=None,
        summary="Died 1035. A veteran hunter of Marched magi, who accused "
        "Hérisson of betraying cult secrets to magi hostile to the Order, "
        "declared Wizard's War and killed him within two days of the full "
        "moon. He left a single filia, Variña, whose line ended with her.",
        secrets="Hérisson's will left him the fruits of the research, by way "
        "of apology for the trouble of having to kill its discoverer. The "
        "copy buried in the field names him as heir; the notes themselves "
        "are not with it (p. 77).",
    )
    tasso = b.magus(
        "Tasso Agricola Areleins",
        covenant=None,
        house=BJORNAER,
        age=64,
        traits={"Badger": 4, "Cheerful": 2, "Just": 1, "Suspicious": -1},
        summary=paragraphs(
            "Eldest of the Sept of Hérisson and its Mystagogue, three "
            "generations from its founder, and a master of Terram. Black hair "
            "with a white stripe rising from each temple tells the badger he "
            "holds within. He goes in a peasant's smock, with a woven hat in "
            "the fields, and speaks like a peasant. Friendly and guileless, "
            "he is to be found working the land around his rural covenant, "
            "which stands apart from Order politics, and which he shares with "
            "one other of the sept. His aim is bigger harvests, so that fewer "
            "forests fall for fields.",
            "Age 64, apparent age 46. Gentle Gift; Study Bonus, which pays "
            "him for his labor with soil and crops (p. 78).",
        ),
        secrets="He holds a few of Hérisson's laboratory texts, out of order "
        "and in cipher. He has never made sense of them, and lets the "
        "characters copy them if they will share what they learn of his "
        "ancestor, since such news is status in his House. Richard Strabo "
        "has made a friend of him with gifts of farming spells and "
        "enchantments, and passes for a friend still; word of anyone asking "
        "after Hérisson soon reaches Strabo. The book prints no Characteristics "
        "or Arts for him.",
    )
    tasso.aging.apparent_age = 46
    b.magus(
        "Erica of Bjornaer",
        covenant=None,
        house=BJORNAER,
        age=None,
        summary="Tasso's filia, a mole in her heartbeast, and a prominent "
        "voice in Hermetic politics for living alongside mundanes and the "
        "Church. She dwells at a covenant near his. Asked about Hérisson, she "
        "will likely send the enquirer to Tasso, the sept's leader and heir "
        "to its founder's texts (pp. 72, 78-79).",
    )
    b.faction(
        "The Sept of Hérisson",
        summary="The descendants of Hérisson within Clan Arelie of House "
        "Bjornaer, who keep his name though their common ancestor is more "
        "recent. All hold to the Harmonist cause.",
        secrets="If Hérisson belonged to a hidden Mystery Cult within his "
        "House, his heirs may keep it still (p. 72).",
        ruler="Tasso Agricola Areleins",
    )
    b.magus(
        "Caerfloron",
        covenant=None,
        house=EX_MISCELLANEA,
        age=None,
        summary="Founder of the covenant that bears his name, a magus Ex "
        "Miscellanea of nearly 150 years with a passion for Herbam. He and "
        "his filii keep apart from the Order, content with its protection "
        "and with their right to be left alone.",
        secrets=paragraphs(
            "He is close to Final Twilight and will not risk his strongest "
            "spells. He enchanted the gate that leads into the Garden's regio "
            "(p. 83). The book prints no block for him or his filii.",
            HOMUNCULUS,
        ),
    )
    for name in ("Radix", "Surculus", "Folium", "Fructus"):
        b.magus(
            name,
            covenant=None,
            house=EX_MISCELLANEA,
            age=None,
            summary="One of the four filii of Caerfloron, living in a hut "
            "against the walls of their walled garden, and like the others "
            "devoted to Herbam.",
            secrets=HOMUNCULUS,
        )
    richard = b.magus(
        "Richard Strabo",
        covenant=None,
        house=BONISAGUS,
        age=58,
        summary="A researcher of House Bonisagus who won Acclaim young, then "
        "soured under the weight of it. Nothing of his has satisfied the "
        "House in over twenty years, and he has grown bitter and solitary, "
        "dropping hints of a secret project that will change Hermetic magic.",
        secrets=paragraphs(
            "Every line he tried came to nothing, until he found Hérisson's "
            "notes in a forgotten archive of Durenmar's library. He means to "
            "find the rest and pass the whole off as his own, and has staked "
            "his name on it. Discovery would finish him in his House, and he "
            "is unhinged enough to break the Code to prevent it. He corresponds "
            "under several aliases with Herbam experts across Mythic Europe, "
            "mining them for ideas, and cultivates Tasso as his sentinel. He "
            "has not thought of the tomb of the slayer's filia. See The "
            "Search for Hérisson's Garden.",
            "By trying to have a magus killed he breaks the Oath and forfeits "
            "the Code's protection (p. 83).",
        ),
    )
    b.stats(richard, STRABO, source=SOURCE)


def _places(b: Builder) -> tuple[Neighbour, Neighbour]:
    """The buried field, the tomb, Caerfloron and the Garden; returns the
    tomb and the Garden, where creatures live."""
    b.place(
        "The Field of Copper Urchins",
        summary="A patch of foreign plants set out in sixteen neat rows, in "
        "a field with nothing else to remark on: no ruin, no legend, only a "
        "faint magic in the ground. In the North they might be rice or orange "
        "trees, in the South carrots or turnips.",
        secrets=paragraphs(
            OPEN_SITE + " It lies near the characters' covenant, whose vis "
            "source it may long have been, or it is won in another story; a "
            "weak Magic aura, with no figure given.",
            "Each plant usually bears one offspring holding vis, which grows "
            "into the next generation. Now and then one bears two: one may be "
            "taken as vis, while the other grows on. The second pawn glows "
            "brighter under Sense the Nature of Vis, and only it will grow. "
            "In a typical year the sixteen yield two pawns to spare.",
            "Buried here are tiny copper urchins stamped with Hermetic sigils "
            "and a chest, turned up by the plough or by magic, holding "
            "Hérisson's will. It leaves the fruits of his research to Gypaetus "
            "as amends for the bother of killing its discoverer. The notes "
            "are not there. A Redcap or a keeper of Tribunal records can tell "
            "that Hérisson once claimed this source and that the urchin was "
            "his voting sigil, with as much of his story as fits (p. 77).",
        ),
        **LOCAL,
    )
    tomb = b.place(
        "Variña's Tomb",
        summary="A lone tower clinging to a mountainside, the sanctum of a "
        "Bjornaer maga of the last century. Its ground floor holds only rubbish, "
        "and a huge white owl nests on its roof.",
        secrets=paragraphs(
            "High in the Pyrenees, or another fitting range. Finding it may "
            "be a story of its own, or the Redcaps may simply have it on "
            "record. Each storey lies in a different layer of a regio, so the "
            "plain tower hides most of what it holds. The map on pp. 79-80 "
            "has its regio boundaries wrong; the text is followed here "
            "(errata p. 78).",
            "The owl has lined her nest with parchment from the library, and "
            "many of Variña's texts are gone. The storyguide decides how "
            "much survives, mostly on Auram. Sorted and restored, Hérisson's "
            "notes among the wreck give nothing toward Viresculture, but his "
            "diary speaks of a garden like Paradise that is to be his new "
            "laboratory once his equipment is moved, and it says plainly "
            "where the Garden is.",
            "Intelligence + Area Lore or Order of Hermes Lore then tells a "
            "little of that place, chiefly that Caerfloron lies very near: "
            "Ease Factor 9 in the same Tribunal, up to 18 across Mythic "
            "Europe (pp. 80-81).",
        ),
        levels=[
            b.level(
                "The ground floor",
                1,
                see="The ground floor of the plain tower, following its outer "
                "wall exactly. Deserted, with only rubbish.",
            ),
            b.level(
                "The hidden cleft",
                2,
                see="A sliver of regio a few feet across, floor to ceiling "
                "between one of the ground-floor columns and the outer wall.",
                notes="Without finding this there is no way on to the third layer.",
            ),
            b.level(
                "The sepulcher",
                3,
                see="Follows the perimeter of the tower walls on both "
                "storeys. An immense stone tomb, with an effigy of enchanted "
                "ice under a lasting illusion of the beauty she was.",
                notes="The tomb may hold a number of magic items of air "
                "magic, her specialty; the book names none.",
            ),
            b.level(
                "The second cleft",
                4,
                see="Another narrow cylinder of regio, in an innocent corner "
                "of the upper storey.",
            ),
            b.level(
                "The upper chamber",
                5,
                see="The upper storey alone, with her laboratory and library.",
            ),
        ],
        **LOCAL,
    )
    b.place(
        "Caerfloron",
        aura=3,
        summary="A hortus conclusus: a high-walled garden with a separate "
        "hut against the wall for each of its five magi, far from the "
        "Order's affairs. The nearest neighbour of a place it does not "
        "speak of.",
        secrets=paragraphs(
            OPEN_SITE + " A covenant by the book, of Caerfloron and his four "
            "filii, with an Aegis of the Hearth of level 20, a weak one; its "
            "founding by the Garden is no chance. It has no record as a "
            "covenant since this pack keeps none.",
            "Its magi know enough of the Order to fear Wizard's War and not "
            "enough to see when the forms were not kept, and they fight by "
            "trapping a foe and then making him harmless. They know exactly "
            "where the regio opens, and Caerfloron has made a gate that "
            "passes its boundary. Each is sworn to enter the Garden but once, "
            "and will not say why. Others may use it on one condition, given "
            "before they will show the way: their apprentices may go in at "
            "the start of training. They will not explain that either; each "
            "goes to fetch the mandrake that makes a wizard (p. 83).",
        ),
        **LOCAL,
    )
    garden = b.place(
        "Hérisson's Garden",
        summary=paragraphs(
            "A paradise close on two miles across, laid out in rings: "
            "parkland outermost, then flowery meads, then herb, flower and "
            "vegetable gardens, a wooded pleasaunce within, and at the heart "
            "a stew, a fish-pond with four streams running to and from it "
            "like spokes. The streams make a moat that wanders among the "
            "plots under little stone bridges. The ground rolls in hillocks "
            "and dells, so the plan is not plain; from high up, streams and "
            "hedgerows draw a Hermetic sanctum mark.",
            "Fine weather runs finer here and storms are hushed. Fruit hangs "
            "out of season, and no bird or insect sounds, which makes a walk "
            "through all that green strangely quiet.",
        ),
        secrets=paragraphs(
            OPEN_SITE + " It needs untamed wilderness in a wet temperate "
            "Tribunal, or can be recast as a lush oasis in a southern one. "
            "Place it near the covenant if it is to stay in the saga, or "
            "anywhere if it will be left behind. Caerfloron is close by "
            "(pp. 80-81).",
            "The plants. Since Hérisson died the strong aura has twisted the "
            "Awakened plants, and they have split into three tribes, each "
            "led by a plant that can set its subjects walking. Each leader "
            "alone knows where a third of the lore is kept, so nothing can be "
            "safely studied until the feud ends. Curtilagium, the kitchen "
            "garden, led by Malus: food and medicine plants such as plum, "
            "medlar, apricot, apple, orange, leek, carrot, vervain, rosemary, "
            "fennel, alexanders and angelica; they fear humans as predators, "
            "and are uneasy allies of the Venenarium. Venenarium, the poison "
            "garden, led by Mandragora: yew, henbane, foxglove, hellebore, "
            "dodder, aconite and many toadstools, with thistles, brambles, "
            "holly and hawthorn. Hortulus, the little garden, led by Linum: "
            "plants of use and of beauty, such as oak, ash, hazel, pine, rue, "
            "hemp, lily, loosestrife, buttercup and mistletoe; they fawn on "
            "mankind. See The Battle of the Trees. Mundane plants act only "
            "when their leader animates them, with Cunning. The leaders "
            "understand speech only by Converse with Plant and Tree (InHe "
            "25) or the like; Intuition of the Forest (InHe 10) gives their "
            "moods. They are obstacles or allies more than foes; to harden "
            "them make them Summer (240 more experience points) or add 5 to "
            "10 Might with matching Qualities (pp. 84-86).",
            "Warping (p. 88). Perennials of five years or more have a Minor "
            "Flaw from warping, and most trees, past 75, have two Minor Flaws "
            "and a Minor Virtue: most often (Form) Monstrosity, or Offensive "
            "to Animals, Warped Senses or a Personality Flaw. Cinnamon trees "
            "may flare at a loud noise; Wrathful brambles wound the more; a "
            "rose with Lesser Malediction may blanch in shadow. Plants of "
            "his magic bear his spines and thorns.",
            "Enchantments (pp. 88-89), living plants made magic items, which "
            "stops their ageing. Bloodthorn, CrCo 15, Pen 0, charged, R Touch "
            "D Moon T Ind: a blackthorn whose sloes give +6 to Wound Recovery "
            "rolls for a Moon; 4 charges left. (Base 3, +1 Touch, +3 Moon.) "
            "Fruitful Medlar, CrHe 9, Pen 0, constant, R Per D Sun T Part: a "
            "Lesser Enchantment; a small tree bearing ten times the fruit in "
            "season. (Base 1, +2 Sun, +1 Part, +1 size; +1 2/day, +3 "
            "environmental trigger.) False Mandrake, PeCo 25, Pen 0, 3/day, R "
            "Voice D Mom T Group: a white bryony Prepared with 4 pawns, a "
            "small wooden object; touched, it shrieks and deafens all who "
            "hear, healing as a Light Wound. (Base 5, +2 Voice, +2 Group; +2 "
            "3/day.) Traveling Thistle, CrVi 14, Pen 0, constant, R Per D Mom "
            "T Ind (the level sum uses Sun, p. 88): a faint taint of magic that its seedlings inherit but do "
            "not pass on; the key to self-replicating vis. (Base 3, +2 Sun, "
            "+1 inherited; +1 2/day, +3 environmental trigger.) Creeping "
            "Buttercup, ReVi 20, Pen 0, 1/day, R Per D Mom T Part: holds a "
            "pawn of Herbam vis and once in its life may pass it to a seed, "
            "whose plant has the same power. (Base 10, +1 Part, +1 special "
            "effect.) Everlasting Orpine: an orpine with a red stem and "
            "pinkish-red crown, Prepared with 6 pawns of Vim vis, a Medium "
            "wooden object; living, but stopped and sterile; an Insight worth "
            "2 Breakthrough points. Ever-Flowering Bramble, CrHe 33, Pen 0, "
            "1/day, R Per D Sun T Ind: a blackberry seed grows, fruits, seeds "
            "and dies in a day, and its seed does so the next, giving a "
            "handful of good fruit; leave one berry or it ends. (Base 15, +2 "
            "Sun, +1 special effect; +3 environmental trigger.) Hazel of Many "
            "Tools, ReHe 5, Pen 0, charged, R Per D Mom T Ind: name a tool "
            "and a twig takes its shape to be broken off; Intelligence + "
            "Finesse, Ease Factor 9, for standard quality; craft magic, 10 "
            "charges left. (Base 5, Covenants p. 51.)",
            "Stirpes (p. 89), invigoration exhausted, each bearing a single "
            "magical offspring a generation, itself a Stirps: Adder's Tongue "
            "(Perdo, in the curled central leaf); Alexanders (Herbam, in the "
            "stems); Ever-Burning Fire (Ignem, flames in the Fennel of "
            "Herbam Vis, derived from a fire elemental); Harebell (Animal, "
            "the furred flower); Pasternack, a purple carrot (Aquam, in the "
            "roots); Selfheal (Creo); Silverweed (Terram, leaves of real "
            "silver). One pawn each. Several uninvigorated, immortal "
            "cultivars grow here too.",
            "Lesser Enchantment Vis (p. 89), Stirpes likewise exhausted; to "
            "Invigorate them needs Hérisson's Minor Breakthrough again. Daisy "
            "of Intellego Vis, InHe 40, Pen 16, 3/day, R Touch D Conc T Ind: "
            "the toucher converses with plants as Converse with Plant and "
            "Tree, Penetrating any Resistance of the plant. (Base 15, +1 "
            "Touch, +1 Conc; +5 maintains concentration, +2 3/day, +8 "
            "Penetration 16.) Mistletoe Sprig of Herbam Vis: Realms of Power: "
            "Magic p. 121. Stinking Hellebore of Rego Vis, ReCo 25, Pen 0, "
            "unlimited, R Touch D Diam T Ind: touching its fleshy green "
            "flowers paralyzes for two minutes; p. 87 calls it of Corpus Vis. (Base 5, +1 Touch, +1 Diam; "
            "+10 unlimited uses.) Honeysuckle of Mentem Vis, ReMe 24, Pen 0, "
            "constant, R Per D Sun T Scent: a vine of hooked yellow flowers; "
            "as Confusion of the Numbed Will on all who smell it, about 6 "
            "paces out. (Base 4, +2 Sun, +2 Scent; +1 2/day, +3 environmental "
            "trigger.) Fennel of Herbam Vis, Re(Cr)Ig(He) 24, Pen 0, constant, "
            "R Per D Sun T Ind: +5 Soak against fire, whose damage heals at "
            "once; it hosts the Ever-Burning Fire. (Base 4, +2 Sun, +2 "
            "requisites; +1 2/day, +3 environmental trigger.)",
            "Enriched Herbs of Virtue (pp. 89-90; Realms of Power: Magic p. "
            "124), preserved until used. Henbane of Virtue: a pawn of Perdo "
            "vis. Three Enriched capsules lie by the stem; a capsule steeped "
            "in scorpion venom and three crushed owl skulls under Saturn "
            "ascendant, then swallowed after a season, gives Lesser Immunity "
            "to Poison and numbs a sense or limb (simple die: 1-2 Afflicted "
            "Tongue, 3-4 Poor Eyesight, 5-6 Poor Hearing, 7-8 Missing Hand, "
            "9-10 Lame), for a year. Wild Teasel of Virtue: two pawns of "
            "Corpus in the juice; fed to a pregnant dog, her litter's "
            "milk-teeth ground into wine give Puissant Brawl, Tough, Berserk "
            "and Wrathful for a year or until the drinker tastes valerian "
            "juice. Valerian of Virtue: two pawns of Creo in the root; "
            "sliced with silver on a night Venus shows, bathed in horse urine "
            "each Friday and ground between amber, it gives Rapid "
            "Convalescence, Enduring Constitution, Reserves of Strength and a "
            "Code of Honor for a year or until the drinker tastes teasel "
            "milk.",
            "Wrestling in the Herb Garden (p. 90). Teasel and valerian grow "
            "thick on either side of a sward, split by a thin line of grass. "
            "Touch a patch and the urge to fight whoever explores the other "
            "takes hold; one champion is picked for each. Teasel's fights "
            "dirty, for many small wounds; valerian's grapples and pins. "
            "Whoever beats the teasel's man gets a draft of Enriched Teasel "
            "Milk, and whoever beats the valerian's a sip of Enriched Valerian "
            "Juice.",
            "Wonders (p. 91), among over fifty fine or unique species. The "
            "Vegetable Lamb: four feet tall, each stem tipped with a tiny "
            "woolly lamb that grazes around the plant, then, the grass gone, "
            "dwindles to a ball of wool. A cinnamon grove, pungent and apt "
            "to ignite. A child of the Drudenbaum of Harberg (Guardians of "
            "the Forests p. 89) that yields no vis. Perhaps Soqotran totem "
            "trees (Rival Magic): cinnabar, olibanum, myrrh and aloe. Add "
            "more with Realms of Power: Magic.",
            "Rediscovery (pp. 91-92). Hérisson went by Original Research, 45 "
            "Breakthrough points for the Major and 30 for the Minor. A magus "
            "here need not: his inventions serve as sources of Insight "
            "(Ancient Magic p. 8, Hedge Magic p. 14), and duplicating an "
            "effect earns points equal to its magnitude. His living "
            "enchantments are read by Investigating in the laboratory in "
            "place of Intelligence + Magic Theory. So are his Stirpes, each "
            "as an enchantment of level 15, the Insight being a version of "
            "Gather the Essence of the Beast: 3 points the first time and 1 "
            "for each later version. Other plants of the Garden use Ancient "
            "Magic's process, and the Minor Breakthrough must draw on these, "
            "after Viresculture itself is regained. At the storyguide's "
            "option Lab Texts of his creations lie here (p. 92), giving their "
            "magnitude once studied by recreating the experiment (True "
            "Lineages p. 29): a tree with a page on each leaf, to be put in "
            "order; a fruit written on its seeds.",
            "Study (p. 92). Realia for Herbam (Covenants p. 102), Source "
            "Quality 6, six times in all. For one who has Hermetic "
            "Viresculture the Stirpes are realia of it, Quality 4, four "
            "times.",
            "Laboratory (pp. 92-94). The Garden is a working Hermetic "
            "laboratory; adapt it as Taking Over a Laboratory (Covenants p. "
            "118). Hérisson lived there as a beast, so a tenant needs a hut. "
            "Virtues: Natural Environment (Major, Structure); Lesser Feature, "
            "the spring that aids vis extraction (Minor, Structure); Specimens "
            "x3 and Superior Decorations (Minor, Outfitting; no extra Upkeep, "
            "being alive); Spacious (Minor, Structure); Vis Source (Minor, "
            "Supernatural); Idyllic Surroundings (Free, Structure); "
            "Inexhaustible Supplies (Free, Supernatural); Regio (Free, "
            "Supernatural). Flaws: Outdoors (Major, Structure); Chaotic and "
            "Living (Minor, Supernatural); Disorganized (Free, Structure). "
            "Characteristics: Size +10 (+5), Refinement 0, General Quality "
            "-1, Upkeep -1, Safety -5, Warping +6, Health 0, Aesthetics +6. "
            "Specializations: Vis Extraction +3, Experimentation +2, Herbam "
            "+10, Imaginem +1, Muto +2. Traits: Growing +3, Curious +2, "
            "Exotic +1.",
            "Its tools grow: gourds for flasks, fungi for bowls, branches "
            "over rocks for benches, birch-bark for paper, the Ever-Burning "
            "Tree for fire (so p. 93; p. 89 has the Ever-Burning Fire), the brook for water. When planning a season "
            "roll a simple die: under the Warping Characteristic the means "
            "are to hand; otherwise choose another activity. Add 2 in winter. "
            "A truce with the plants adds Lesser Horde (Supernatural, no "
            "Upkeep): +1 General Quality, Safety and Aesthetics, +1 in Perdo "
            "(Venenarium), Creo (Curtilagium) or Rego (Hortulus). A tribe "
            "made an enemy adds Gremlins: -3 Safety, +1 Warping, -1 "
            "Aesthetics, +1 Experimentation, +1 in that same Art.",
        ),
        levels=[
            b.level(
                "The Garden",
                6,
                enter="Through the entrance only the magi of Caerfloron can "
                "show, by the gate Caerfloron enchanted.",
                see="See the place's description.",
                notes="Magic aura 6 aligned to Herbam: the modifier counts "
                "double with the Art of Herbam, and creatures of Herbam Might "
                "pay 1 less Might for powers (Realms of Power: Magic p. 16). "
                "The aura counts, with its alignment, in the plants' "
                "Penetration and Magic Resistance. Two of the stone bridges "
                "are enchantments, one keeping the water moving and one "
                "keeping it clean.",
            ),
        ],
        **RUMOURED,
    )
    return tomb, garden


def _creatures(b: Builder, tomb: Neighbour, garden: Neighbour) -> None:
    """The owl of the tomb and the great plants of the Garden."""
    b.creature(
        "Variña",
        page="p. 78",
        realm=MAGIC,
        might=35,
        form="Auram",
        size=2,
        season="Summer",
        cunning=True,
        confidence=(2, 6),
        place=tomb,
        block={
            "characteristics": characteristics(0, 3, -1, -2, 4, 2, 5, 0),
            "virtues_flaws": [
                "Thick Fur/Thick Scales",
                "Magic Animal",
                "Magical Monster",
                ("Ways of the {land}", {"land": "Mountain"}),
                "Improved Characteristics",
                "Large",
                vf_puissant("Stealth"),
                "Proud (Major)",
                "Focus Power",
                "Gigantic",
                "Gigantic",
                "Improved Attack",
                "Improved Defense",
                "Improved Initiative",
                "Improved Powers",
                "Improved Soak",
                "Improved Soak",
                "Improved Soak",
                vf_minor("Great Dexterity"),
                vf_minor("Great Dexterity"),
                vf_minor("Improved Characteristics"),
                vf_minor("Tough"),
                "Accomplished Flyer",
                "Aggressive",
                "Ambush Predator",
                "Large Claws",
                "Sharp Ears",
            ],
            "abilities": [
                ("Awareness", 4, "prey"),
                ("Athletics", 5, "flying"),
                ("Brawl", 5, "claws"),
                ("Hunt", 4, "prey"),
                ("Stealth", 5, "from sky"),
                ("Survival", 3, "mountains"),
            ],
            "traits": {"Owl": 5, "Vain": 4, "Territorial": 3},
        },
        attacks=[b.attack("Large Claws", 6, 21, 13, 9)],
        soak=12,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Winter's Queen",
                1,
                -1,
                "Variable",
                level=30,
                does="1 to 6 points, Init is minus the Might cost, form "
                "variable. Duplicates any spell of snow, ice or cold of level "
                "30 or less, at 1 Might per magnitude. A Focus Power: 5 "
                "mastery points raise the maximum level.",
            ),
        ],
        vis=[BodyVis(7, "Auram", "feathers")],
        appearance="A huge white owl speckled with black, with startling emerald eyes.",
        notes=paragraphs(
            "Filia of Gypaetus, who trained no apprentice and ended his line "
            "when she entered Final Twilight. A worker of air magics who built "
            "her sanctum high on a mountain. Her Inner Heartbeast is a Snowy "
            "Owl of Virtue, nesting on the tower roof.",
            "Wound Penalties as printed: -1 (1-8), -3 (9-16), -5 (17-24), "
            "Incapacitated (25-32), Dead (33+). Init, Attack and Defense "
            "include Ways of the Mountain. Thick Feathers, her block's Mundane "
            "Quality, is entered as Thick Fur/Thick Scales. Owl and Vain are starred "
            "traits. Proud has no printed tier.",
            "She strikes from ambush: unseen and winning Initiative, +3 to "
            "her first Attack; still first in the order afterward, she can "
            "fly out of reach. To come round again, roll new Initiatives.",
            "Heartbeast Ability 7 at Final Twilight gave Might 35. Up to 15 "
            "points of Magical Qualities are left for the storyguide "
            "(Realms of Power: Magic p. 36). She will hardly consent to be a "
            "familiar. She need not be slain, but must be got past to enter "
            "the tower (p. 78).",
        ),
    )
    b.creature(
        "Linum",
        page="p. 84",
        realm=MAGIC,
        might=15,
        form=HERBAM,
        size=-2,
        season="Spring",
        place=garden,
        level=1,
        block={
            "characteristics": characteristics(1, 0, 0, 2, -3, 1, 0, 3),
            "virtues_flaws": [
                "Magic Thing",
                "Magical Champion",
                "Entrancement",
                "Arcane Lore",
                "Gossip",
                ("Voice of the {land}", {"land": "Garden"}),
                "Compassionate (Major)",
                ("Anchored to the {land}", {"land": "Garden"}),
                "Fragile Constitution",
                "Motion Sickness",
                "Noncombatant",
                "Greater Power",
                "Ritual Power",
                "Ritual Power",
                ("Improved {characteristic}", {"characteristic": "Strength"}),
                ("Improved {characteristic}", {"characteristic": "Strength"}),
                "Improved Might",
                "Improved Might",
                "Improved Might",
                "Improved Might",
                "Improved Might",
                "Limited Movement",
                "Reduced Fatigue",
                "Reduced Fatigue",
                "Reduced Soak",
            ],
            "abilities": [
                ("Brawl", 3, "dodge"),
                ("Charm", 1, "obsequious"),
                ("Entrancement", 4, "keeping peace"),
                ("Leadership", 1, "herbs"),
                ("Mastery of Rally the Wooden Troops", 3, "flowers"),
                ("Penetration", 4, "Entrancement"),
            ],
            "traits": {"Caring": 6, "Peaceful": 3, "Flax": 2},
        },
        attacks=[b.attack("Dodge", 3, None, 7, None)],
        soak=-1,
        fatigue_levels="OK, -3, -5, Unconscious",
        powers=[
            b.power(
                "Rally the Wooden Troops",
                2,
                -1,
                HERBAM,
                does="As Malus's power, but only for the Hortulus tribe.",
            ),
            b.power(
                "Healing",
                2,
                -7,
                "Corpus",
                does="The target's worst wound improves by one level at once. "
                "The points come from Might Score, not the pool (Realms of "
                "Power: Magic p. 39). Ritual Power x2.",
            ),
        ],
        vis=[BodyVis(2, HERBAM, "seeds")],
        appearance="A mass of thin stems some four feet high, with small "
        "narrow leaves and bright blue, five-petaled flowers.",
        notes=paragraphs(
            "Leader of the Hortulus, honored for mercy and wisdom. Rooted "
            "deep, it can barely move unaided, and hates being moved: it "
            "turns sick and cannot use any power.",
            "Wound Penalties as printed: -1 (1-3), -3 (4-6), -5 (7-9), "
            "Incapacitated (10-12), Dead (13+). Flax is a starred trait.",
            "Within the Garden each power costs 1 less Might, and the aura "
            "adds to Penetration and Magic Resistance.",
        ),
    )
    b.creature(
        "Mandragora",
        page="p. 85",
        realm=MAGIC,
        might=10,
        form=HERBAM,
        size=-6,
        season="Spring",
        place=garden,
        level=1,
        block={
            "characteristics": characteristics(1, 0, -3, 0, -10, 3, 0, 6),
            "virtues_flaws": [
                "Magic Thing",
                "Magical Champion",
                "Hex",
                "Arcane Lore",
                vf_puissant("Penetration"),
                ("Voice of the {land}", {"land": "Garden"}),
                "Hatred (Major)",
                "Reduced Power",
                ("Anchored to the {land}", {"land": "Garden"}),
                "Infamous",
                "Tainted with Evil",
                "Weak Characteristics",
                "Greater Power",
                "Greater Power",
                "Greater Power",
                "Improved Abilities",
                "Improved Abilities",
                "Improved Powers",
                "Limited Gestures",
            ],
            "abilities": [
                ("Brawl", 3, "dodging"),
                ("Hex", 4, "illness"),
                ("Leadership", 3, "poisonous plants"),
                ("Magic Lore", 1, "poisonous plants"),
                ("Mastery of Rally the Wooden Troops", 4, "toadstools"),
                ("Penetration", 4, "scream"),
                ("Profession: Apothecary", 4, "poisons"),
            ],
            "traits": {"Spiteful": 6, "Mandrake": 3, "Reclusive": 3},
            "reputations": {"Deadly (Local)": 4},
        },
        attacks=[b.attack("Dodge", 6, None, 10, None)],
        soak=2,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Deadly Scream",
                3,
                6,
                "Corpus",
                level=50,
                does="Corpus or Animal. Deadly to all who hear it; deafness "
                "is a sound defense. Unlike a Mandrake of Virtue it can do "
                "this at any time. PeCo(An) 50 (Base 30, +3 Sound, +1 Animal "
                "requisite): Greater Power (50 levels), Improved Powers (5 "
                "mastery points, +3 Init, -2 Might cost).",
            ),
            b.power(
                "Rally the Wooden Troops",
                2,
                2,
                HERBAM,
                does="As Malus's power, but only for the Venenarium tribe.",
            ),
            b.power(
                "Unwholesome Lust",
                1,
                4,
                "Mentem",
                rtd=("Voice", "Sun", ""),
                level=20,
                does="The target burns with lust for someone the plant picks "
                "as it acts, and can do nothing but pursue them until it "
                "ends. CrMe 20 (Base 4, +2 Voice, +2 Sun): Greater Power (20 "
                "levels, -5 for Reduced Powers, -1 Might cost).",
            ),
        ],
        vis=[BodyVis(2, "Corpus", "root")],
        appearance="Above ground, a low cluster of long tapering leaves. "
        "The root is six inches of fleshy, five-lobed body, roughly a little "
        "man, with a hint of a face among the wrinkles of the top lobe and "
        "flabby, fingerless arms that cannot grip.",
        notes=paragraphs(
            "The evil genius of the Venenarium, hating all that breathes. It "
            "works through dupes and hides that it is the source of trouble. "
            "A stronger, moving kin of the Mandrake of Virtue (Realms of "
            "Power: Magic). Called Mandragora and also Mandrake on p. 85.",
            "Hex 4 and Magic Lore 1 each have 5 more experience points. "
            "Wound Penalties as printed: -1 (1), -3 (2), -5 (3), "
            "Incapacitated (4), Dead (5+). Spiteful and Mandrake are starred "
            "traits.",
            "Within the Garden each power costs 1 less Might, and the aura "
            "adds to Penetration and Magic Resistance.",
        ),
    )
    b.creature(
        "Malus",
        page="p. 86",
        realm=MAGIC,
        might=10,
        form=HERBAM,
        size=3,
        season="Spring",
        place=garden,
        level=1,
        block={
            "characteristics": characteristics(0, 0, 0, 0, 7, 3, 0, -1),
            "virtues_flaws": [
                "Magic Thing",
                "Magical Champion",
                ("Greater Immunity", {"hazard": "edged weapons"}),
                "Improved Characteristics",
                "Tough",
                ("Voice of the {land}", {"land": "Garden"}),
                "Overconfident (Major)",
                ("Anchored to the {land}", {"land": "Garden"}),
                ("Baneful Circumstances", {"circumstance": "fire"}),
                "Clumsy",
                "Weak-Willed",
                "Greater Power",
                "Greater Power",
                "Improved Damage",
                "Improved Soak",
                "Improved Soak",
                "Improved Soak",
            ],
            "abilities": [
                ("Brawl", 4, "branch"),
                ("Intrigue", 1, "woodland politics"),
                ("Leadership", 2, "trees"),
                ("Mastery of Rally the Wooden Troops", 4, "fruit trees"),
            ],
            "traits": {
                "Reckless": 6,
                "Crab Apple": 3,
                "Paranoid": 3,
                "Brave": -1,
            },
        },
        attacks=[b.attack("Branch", 9, 9, 6, 12)],
        soak=12,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Rally the Wooden Troops",
                2,
                -5,
                HERBAM,
                level=35,
                does="Sets nearby trees and plants walking; in this Garden "
                "they also gain Cunning 0. Up to 10 Groups of Herbam: 10,000 "
                "herbs (Size -6), 100 bushes (Size 0), 10 small trees (Size "
                "+3) or one 25-foot tree (Size +6). May fire as many times a "
                "round as the Mastery Ability, paying Might each time. Malus "
                "can move only Curtilagium plants. ReHe 35 (Base 5, +1 "
                "Touch, +2 Sun, +2 Group, +1 Size): Greater Power (35 levels, "
                "-2 Might cost, Multicast mastery power).",
            ),
            b.power(
                "Creeping Chasm",
                4,
                -2,
                "Terram",
                level=35,
                does="Thrusts its roots deep and duplicates the spell of the "
                "same name. ReTe 35: Greater Power (35 levels, +3 Init).",
            ),
        ],
        vis=[BodyVis(2, HERBAM, "apples")],
        appearance="A small tree about twelve feet tall, gnarled and spiny, "
        "with dark green leaves, near-black bark and bright red, longish "
        "apples.",
        notes=paragraphs(
            "Leader of the Curtilagium, by sheer faith in its immunity to "
            "axes and blades.",
            "Wound Penalties as printed: -1 (1-8), -3 (9-16), -5 (17-24), "
            "Incapacitated (25-32), Dead (33+). Crab Apple is a starred trait.",
            "Within the Garden each power costs 1 less Might, and the aura "
            "adds to Penetration and Magic Resistance.",
        ),
        secrets="Its powers fail it near fire, and it keeps well away from any flame.",
    )
    b.creature(
        "Dodder",
        page="pp. 90-91",
        realm=MAGIC,
        might=25,
        form=HERBAM,
        size=0,
        season="Summer",
        confidence=(1, 3),
        place=garden,
        level=1,
        block={
            "characteristics": characteristics(1, 0, 0, -3, 7, 4, 2, 2),
            "virtues_flaws": [
                "Magic Thing",
                "Magical Monster",
                ("Great {characteristic}", {"characteristic": "Strength"}),
                ("Great {characteristic}", {"characteristic": "Strength"}),
                ("Great {characteristic}", {"characteristic": "Stamina"}),
                "Tough",
                "Infamous",
                "Poor Hearing",
                "Greater Power",
                "Greater Power",
                "Improved Might",
                "Improved Might",
                "Improved Might",
                "Improved Might",
                "Improved Might",
                "Improved Soak",
                "Improved Soak",
                "Lesser Power",
                vf_minor("Improved Characteristics"),
                vf_minor("Improved Characteristics"),
                vf_minor("Puissant Brawl"),
                "Monstrous Appearance",
            ],
            "abilities": [
                ("Athletics", 5, "chase"),
                ("Brawl", 8, "grapple"),
                ("Leadership", 3, "own limbs"),
                ("Stealth", 5, "undergrowth"),
            ],
            "traits": {"Murderous": 4, "Brave": 3, "Dodder": 3},
            "reputations": {"Assassin (Local)": 4},
        },
        attacks=[b.attack("Grapple", 2, 13, 13, 7)],
        soak=13,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Sprout Limbs",
                0,
                -1,
                HERBAM,
                level=10,
                does="Weaves up to eight limbs from its tendrils, and may be "
                "treated as a trained group of four, adding +12 to Attack or "
                "Defense. Every two limbs strangling shrink the group by one. "
                "Cr(Re)He 10 (Base 1, +2 Sun, +2 Group, +1 requisite): Lesser "
                "Power (10 levels, -2 Might cost, +1 Init).",
            ),
            b.power(
                "Strangle the Life",
                0,
                2,
                "Corpus",
                level=30,
                does="Fingers of wire close on the throat and drain life. "
                "Each round the victim makes a Deprivation roll against an "
                "Ease Factor of Dodder's Strength roll. Up to eight at once, "
                "a limb each. To escape, beat its Grapple Attack with your "
                "own. PeCo 30 (Base 10, +1 Touch, +1 Conc, +2 Group): Greater "
                "Power (30 levels, -2 Might cost, +2 Init).",
            ),
            b.power(
                "Wear Corpse",
                1,
                -2,
                "Corpus",
                level=35,
                does="Worms into a human corpse of Size -1 to +1, moves it, "
                "and keeps it from decay. It can use its other powers inside, "
                "but cannot heal the corpse, or pass as human for long. "
                "Re(Cr)Co 35 (Base 10, +1 Touch, +2 Sun, +1 constant, +1 "
                "requisite): Greater Power (35 levels, -3 Might cost).",
            ),
        ],
        vis=[BodyVis(5, "Perdo", "tendrils")],
        appearance="At rest, a tangle of yellow and red tendrils in the "
        "grass and round other plants, with clusters of pale pink, bell-like "
        "flowers. Roused, a writhing, roughly man-shaped mass, with limbs "
        "of many fingers.",
        notes=paragraphs(
            "A parasite that strangles other plants and now more than plants. "
            "It waits in the grass, engulfs its prey and sucks the life out "
            "of it. It neither speaks nor answers to any speech, yet hunts "
            "with a sly, baleful mind. Mandragora has a small control over it.",
            "Wound Penalties as printed: -1 (1-5), -3 (6-10), -5 (11-15), "
            "Incapacitated (16-20), Dead (21+). Brawl 8+2 with Puissant Brawl. "
            "Dodder is a starred trait.",
            "Within the Garden each power costs 1 less Might, and the aura "
            "adds to Penetration and Magic Resistance.",
        ),
    )


def _main_stories(b: Builder, garden: Neighbour) -> None:
    """The adventure, in the book's order."""
    dormant(
        b.threat(
            "The Search for Hérisson's Garden",
            place=garden,
            realm=MAGIC,
            antagonist="Richard Strabo of Bonisagus",
            summary="Spiny plants full of vis keep turning up around the "
            "covenant, and a buried will points to the lost research of a "
            "legendary magus. Someone else wants it badly.",
            secrets=paragraphs(
                "In Search of Eden (pp. 76-83). Reaching the Garden lets the "
                "characters rebuild Hermetic Viresculture by Insights, far "
                "quicker and safer than Original Research. Strabo needs the "
                "same notes, so he stays ahead of them until unmasked. He "
                "does not want the magi killed at first, only what they "
                "carry.",
            ),
            stages=[
                S(
                    "Foreshadowing",
                    at=1,
                    clues="Now and then, among unrelated stories, magical "
                    "plants turn up in one region as stray pawns of vis, "
                    "perhaps Spell-Like or Lesser Enchantment Vis: escapees "
                    "from his early research, bristling with his spines and "
                    "thorns. See The Basilisk Rose and A Gruit Local Custom.",
                ),
                S(
                    "The buried will",
                    at=2,
                    clues="The field's foreign plants in their neat rows, "
                    "copper urchins, and a chest with Hérisson's will. A "
                    "Redcap or Tribunal archivist supplies his story. Two "
                    "trails follow: his heirs, and his slayer's line.",
                ),
                S(
                    "Hérisson's descendants",
                    at=3,
                    clues="Tasso Agricola tells the legend and offers copies "
                    "of his ciphered texts for a share of what is found. "
                    "Records show Gypaetus died in 1035, leaving only Variña.",
                    ignored="Strabo soon hears from Tasso of the characters' "
                    "interest, and may have them attacked before they have "
                    "learned anything.",
                ),
                S(
                    "Variña's Tomb",
                    at=4,
                    clues="The tower's nested regio, the owl, and the "
                    "parchment in her nest, with the Garden's location in "
                    "Hérisson's diary.",
                ),
                S(
                    "The ambush",
                    at=5,
                    clues="By now Strabo knows the magi and their home. "
                    "Local ruffians fall on them on the road and take what "
                    "they can to a distant tavern, where Strabo pays them "
                    "with poison after he has the goods.",
                    ignored="He may flood the covenant with quick-growing ivy "
                    "while, as one strand of it, he searches the magi's "
                    "belongings; or just follow them and race ahead to "
                    "Caerfloron once he sees the way they go.",
                ),
                S(
                    "Caerfloron",
                    at=6,
                    clues="The five magi meet the characters with open "
                    "hostility or an outright assault of Herbam magic: Strabo "
                    "has told them a Wizard's War is coming. Warned in time, "
                    "he has even served a false declaration, disguised as a "
                    "local Redcap by Disguise of the New Visage, without "
                    "knowing the Garden lies here if he has not seen the "
                    "notes.",
                    stopped="Neither side knows why the other is fighting, "
                    "so a parley can show the lie. Strabo flees and is "
                    "outside the Code, liable to a Wizard's March. Caerfloron "
                    "makes amends by showing the way in, once promised the "
                    "right to send apprentices in.",
                ),
                S(
                    "Into the Garden",
                    at=7,
                    clues="The gate opens on the regio, and the feud of the "
                    "plants begins. See The Battle of the Trees.",
                ),
            ],
        )
    )
    dormant(
        b.threat(
            "The Battle of the Trees",
            place=garden,
            realm=MAGIC,
            antagonist="Mandragora of the Venenarium",
            summary="The arrival of strangers sets the old feud of the "
            "Garden's plants alight, and something is watching them from the "
            "grass.",
            secrets=paragraphs(
                "Pp. 86-87. The Garden cannot be properly explored until the "
                "tribes make peace; the plants vital to the research belong "
                "to all three, and each leader's help is needed. Do not show "
                "the tribes merely as monsters to kill. Mandragora feeds "
                "Malus's fear; while it does, there can be no peace with the "
                "Curtilagium, and attacks by both tribes go on at random. "
                "The book gives no set way to end the feud. Finding the "
                "Mistletoe of Herbam Vis early gives a feel for the plants.",
                "The cruelest trick: kill a grog in secret and send Dodder "
                "in the corpse to walk among his friends.",
            ),
            stages=[
                S(
                    "Watched",
                    at=1,
                    clues="Curtilagium and Hortulus observe the strangers. "
                    "Only Magic Sensitivity may catch beings with Might "
                    "among the Garden's general magic. Eating the fruit and "
                    "gathering vis rouses the Curtilagium.",
                ),
                S(
                    "The night camp",
                    at=2,
                    clues="A fire brings Malus's hardwoods trampling through "
                    "the camp. Mandragora rings it in the night with a hedge "
                    "of bramble and hawthorn, as Wall of Thorns. Afterward "
                    "toadstools line the paths and crowd each resting place, "
                    "and the silence presses in.",
                ),
                S(
                    "The buttercup path",
                    at=3,
                    clues="On the second day a path of creeping buttercup "
                    "appears where none was and leads to Linum's meadow. It "
                    "needs magic to be understood; it points those without "
                    "any to a Daisy of Intellego Vis. It welcomes them, "
                    "excuses the Curtilagium as fearful, urges them to "
                    "convince Malus, and will not mention the Venenarium.",
                ),
                S(
                    "The orchard",
                    at=4,
                    clues="Linum can direct them to Malus, but Mandragora has "
                    "convinced it they mean to destroy the Garden. Mandragora "
                    "sends animated Stinking Hellebore to paralyze them; "
                    "Malus binds them in honeysuckle and ivy, as Trap of the "
                    "Entwining Vines; failing that, it thickens the "
                    "undergrowth to shield itself.",
                ),
                S(
                    "The source of the poison",
                    at=5,
                    clues="If they find Mandragora out it sends Dodder "
                    "against the strongest of them, and keeps its Deadly "
                    "Scream until it is in direct peril; that is deadly to "
                    "those without Magic Resistance, and readily answered "
                    "by those with it.",
                    stopped="A truce opens the lore of all three tribes and "
                    "gives the laboratory its Lesser Horde.",
                    turned="A tribe made an enemy brings Gremlins on the laboratory.",
                ),
            ],
        )
    )


def _side_stories(b: Builder, garden: Neighbour) -> None:
    """The foreshadowing stories and the chapter's story seeds."""
    dormant(
        b.threat(
            "The Basilisk Rose",
            realm=MAGIC,
            antagonist="A noble with a poisoner's secret",
            summary="An important noble's daughter is sick with something no "
            "physician can name. Her one comfort is the scent of a gray and "
            "pink rose found only in her garden, of which a fresh bloom is "
            "brought to her each day.",
            secrets=paragraphs(
                "A Wreath of Pale Flowers (pp. 76-77). The rose is an escaped "
                "cultivar of Hérisson, one of his few destructive ones, with "
                "Perdo vis in it. Its roots taint her water, and its blossoms "
                "ease the poison, so uprooting it surely kills her.",
                "Her father planted the rose in a nearby town some years ago "
                "to rid himself of opponents by a false plague, then felled "
                "it, not knowing a seed had reached his daughter's garden. "
                "No one has connected the plague with the rose. Who gave him "
                "the plant is left open: a demon tempting him to murder, a "
                "magus with a grudge against the town, or a faerie hoping to "
                "gain vitality as the girl's rescuer.",
            ),
        )
    )
    dormant(
        b.threat(
            "A Gruit Local Custom",
            realm=MAGIC,
            antagonist="Village pride",
            summary="Each year a village the covenant trades with holds a "
            "contest for best brew, between the delicate ale of the Marianne "
            "Sisters, loved by the women, and the heavy acorn and bog-myrtle "
            "beer of Lorris Taverner, loved by the men. Both keep their "
            "recipes close, and passions run high. The magi are asked to "
            "judge.",
            secrets=paragraphs(
                "P. 77. Both drinks carry a faint taint of magic. The elder "
                "Marianne sister is Touched by Magic (City & Guild p. 71) and "
                "flavors her gruit with hyssop grown in a Magic aura. Lorris "
                "has no magic, but owns one of Hérisson's oaks: its acorns, "
                "known by the spines on their cups, hold at least a pawn of "
                "Imaginem vis, more in a good year.",
            ),
            stages=[
                S(
                    "The verdict",
                    at=1,
                    clues="The whole village holds its breath; its pride "
                    "and output hang on it.",
                    turned="For the ale: the men turn hostile, and the "
                    "women's cottage industries gain. For the beer: crops "
                    "get a small boost for the year, and the women turn "
                    "sullen and bad-mouth the characters.",
                    stopped="Meddling with either brewing earns the enmity "
                    "of the whole village.",
                ),
            ],
        )
    )
    dormant(
        b.threat(
            "A Dangerous Tithe",
            realm="Divine",
            antagonist="The local priest",
            summary="Grain does not grow unseen. The local priest has noticed "
            "that the covenant farms, and comes for a tenth of whatever God "
            "gives increase, with a reeve to see he is not cheated.",
            secrets="P. 76. A story seed of a covenant using Hermetic "
            "Viresculture. The tithe in theory covers vis, so the characters "
            "must give up vis whose magic they would not put in anyone's "
            "hands, least of all the Church's.",
        )
    )
    dormant(
        b.threat(
            "Like Nothing I've Ever Tasted",
            realm=MAGIC,
            antagonist="A hungry peasant",
            summary="Something has been eating from the covenant's strange "
            "field, or its livestock has been poached.",
            secrets="P. 76. A story seed of a covenant using Hermetic "
            "Viresculture. A peasant eats a crop or beast of Lesser "
            "Enchantment Vis and gains its effect, perhaps for good, at the "
            "cost of Warping. He must be found before he tells others and "
            "they all come for the precious Stirpes.",
        )
    )
    dormant(
        b.threat(
            "A Burning Desire",
            place=garden,
            realm=MAGIC,
            antagonist="A dying phoenix",
            summary="A phoenix near the end of its life comes to the Garden "
            "seeking a cinnamon tree for its last nest.",
            secrets="P. 93. It builds a nest of cinnamon boughs for the rising "
            "sun to light, and a chick is reborn in the ashes. A magus "
            "wanting a rare familiar may bargain for the chick. The price is "
            "the death of a far-off king with a taste for exotic birds. To "
            "ignore the deal after the parent dies, or put it off, invokes "
            "the phoenix's death-curse.",
        )
    )
    dormant(
        b.threat(
            "The Kidnapped Totems",
            place=garden,
            realm=MAGIC,
            antagonist="The Soqotran sorcerers",
            summary="After centuries of searching, a delegation of foreign "
            "sorcerers forces its way into the Garden.",
            secrets="P. 93; Rival Magic chapter 3. Hérisson stole the "
            "Soqotrans' totem plants, a theft like kidnapping a loved one, "
            "that has cost generations of would-be sorcerers their power. One "
            "from each tribe comes to take back the trees and punish the "
            "thief. They will take Hermetic magi in the Garden for his heirs, "
            "since they use his magic, and vent their fury on them before "
            "they go.",
        )
    )


def build(b: Builder) -> None:
    _people(b)
    tomb, garden = _places(b)
    _creatures(b, tomb, garden)
    _main_stories(b, garden)
    _side_stories(b, garden)
