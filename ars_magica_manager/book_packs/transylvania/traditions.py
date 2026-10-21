"""The hedge traditions of the Transylvanian Tribunal, as of 1220, in
paraphrase of Against the Dark chapter nine, with what chapters three,
five, six and eight add about the same folk: the storm wizards, the
Fectores and the Hunters' Arts, the hunters marked by their birth
(sabotnici, glogove, the taltós and the kresnici), the hunters born of
vampires (dhampiri, vampirdzhia and the lampijeroviki of Sanžak), the
wolf brotherhoods, the folk witches and the strigoi vii, and the Cuman
and Pecheneg shamans, each as a faction naming the tradition record its
members are played from (the wolf brotherhoods and the Pechenegs have
none); one storm wizards' ice cave as a place; and Thietmar the storm
wizard and Tibor of Borša the dhampir as companions with their printed
stats.

Laniena, its magi, Murat of Terezin and Bendis the Fector are the
Hungary part's; Ludmilla is the borders part's; Zuban the four-eyed dog
is the Bestiary's. `finish` places each faction in its region and links
the named people the other parts made, looked up by name.
Keys: world["storm_wizards"], ["fectores"], ["sabotnici"], ["glogove"],
["taltos"], ["kresnici"], ["dhampiri"], ["lampijeroviki"],
["wolf_brotherhoods"], ["folk_witches"], ["strigoi_vii"],
["cuman_shamans"], ["pecheneg_shamans"]; places["ice_cave"]; and
magi["thietmar"], ["tibor"] (companions, not magi)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..builder import StatBlock, paragraphs

if TYPE_CHECKING:
    from ...models import Character
    from . import Transylvania

SKETCHED = (
    "A member is played from the tradition record the faction names: "
    "its powers are summarised here, and what the record only notes is "
    "in Against the Dark (chapter nine) and Hedge Magic Revised Edition."
)
#: For a group no tradition record covers.
UNRECORDED = (
    "No tradition record covers them: their powers are summarised here, "
    "and a member who needs them is played from Against the Dark "
    "(chapter nine) and Hedge Magic Revised Edition."
)

KNOWN_TRIBUNAL: dict[str, Any] = {"status": "Known", "known": "In the Tribunal"}
RUMOURED: dict[str, Any] = {"status": "Rumoured", "known": "Locally"}

#: Each faction's region, by its key: the region part's place key.
REGIONS: dict[str, str] = {
    "storm_wizards": "transylvania",
    "fectores": "hungary",
    "sabotnici": "bulgaria",
    "glogove": "slavs",
    "taltos": "hungary",
    "kresnici": "slavs",
    "dhampiri": "transylvania",
    "lampijeroviki": "slavs",
    "wolf_brotherhoods": "transylvania",
    "folk_witches": "transylvania",
    "strigoi_vii": "transylvania",
    "cuman_shamans": "transylvania",
    "pecheneg_shamans": "transylvania",
}


def build(transylvania: Transylvania) -> None:
    _storm_wizards(transylvania)
    _hunters(transylvania)
    _witches(transylvania)
    _shamans(transylvania)
    _companions(transylvania)


# ------------------------------------------------------------ storm wizards


def _storm_wizards(transylvania: Transylvania) -> None:
    b = transylvania.b
    w = transylvania.world
    w["storm_wizards"] = b.faction(
        "The Storm Wizards",
        tradition="trad_storm_wizards",
        faction="Hedge coven",
        realm="Magic",
        rules=(
            "Every one is Gifted, nearly every one a man; each lives alone "
            "in a cave high above the snow. An apprentice ends his "
            "training by hunting down a true giant and eating its heart."
        ),
        wants="Their ice sites kept secret; giants hunted; to be let alone",
        offers="Storms moved away from a village, for gifts of food left out",
        summary=paragraphs(
            "A lonely, ancient Gifted tradition found only in "
            "Transylvania. Mountain villagers have long exposed "
            "unwanted babies (the deformed, the seemingly mad, the "
            "children of incest) on the bare slopes to rid themselves "
            "of whatever curse they feared; nearly all die, but the "
            "few with The Gift are carried off by bearded giants "
            "striding above the storm clouds, and so the storm wizards "
            "find their apprentices and open their Gift. The grown "
            "wizards are huge, bearded and solitary.",
            "Magi know only that they raise and steer storms and are "
            "said to number fewer than six; peasants blame every storm "
            "on them, and since a called storm looks wholly natural, "
            "nobody can be sure there are not many more. Being Gifted, "
            "they fall under Join or Die, but they are so rare and "
            "seem so harmless that hardly any magus has found out. "
            "Some joined House Ex Miscellanea in the Schism War and "
            "fought beside the Tremere, a service the Order has "
            "forgotten; no text on their powers is known to survive. "
            "Their aims, if they have any, are unknown.",
            "Twice they have banded together to storm the Scholomance's "
            "tower, holding it out of its regio, and twice been driven "
            "off; they talk of taking back something they lost. A "
            "Transylvanian tale of a dragon-riding weather wizard, the "
            "tenth scholar the Devil keeps from the Scholomance, may "
            "owe something to them. Thietmar is one of them.",
            "Story seeds: travellers caught in a mountain storm see, "
            "by the lightning, a giant fleeing bolts that keep finding "
            "him, and must choose whether to help the giant or the "
            "young wizard whose initiation they have walked into; or "
            "they find an ice cave carved with runes and full of Auram "
            "vis, and with it the wizards who harvest it.",
            SKETCHED,
            "Their magic: three Supernatural Abilities, Storm Calling "
            "(Communication + ability: raise a storm, local, "
            "provincial or national, lasting from a Diameter to a "
            "Moon, for 1, 2 or 4 pawns of Auram vis, or move any "
            "storm without cost, even against the wind or indoors), "
            "Storm Riding (Perception + ability: see from, travel to, "
            "or send a touched person to any point of a storm in "
            "sight) and Storm Fighting (buffets, deluge, hail, "
            "erosion that topples a building, and lightning at +20), "
            "with the Arcane Ability Organization Lore: Storm Wizards "
            "and Penetration. Once raised a storm is natural, so it "
            "needs no Penetration and crosses an Aegis. In a season "
            "of ice harvesting a wizard gathers (Int + Organization "
            "Lore + aura) / 3 pawns of Auram vis as ice that never "
            "melts, at sites he keeps secret. A wizard who takes two "
            "or more Warping Points at once, or reaches a new Warping "
            "Score, may become a storm for a Moon (Strength + stress "
            "die against 3 + Warping Score), and dies if he cannot "
            "gather himself again before it blows out. The Heart of "
            "the Storm initiation (Ease Factor 21, script bonus +15: "
            "the giant's heart as a Quest, the Feud with the giants' "
            "tribe as a Major Ordeal) gives Giant Blood, free to a "
            "storm wizard. The Virtues Storm Calling, Storm Riding "
            "and Storm Fighting and the Social Status Storm Wizard are "
            "in the catalog.",
        ),
        secrets="The Tremere may be burying what they know of the storm "
        "wizards on purpose: their powers baffled the Diedne in the "
        "Schism War, and the House may want that surprise kept for "
        "the next war.",
    )
    transylvania.places["ice_cave"] = b.place(
        "A storm wizards' ice cave",
        realm="Magic",
        summary=paragraphs(
            "A cave high in the Carpathians whose frozen walls are cut "
            "with strange runes and pictures of shadowy giants walking "
            "over stormy peaks: one of the sites where the storm wizards "
            "harvest their ice, which they guard as their deepest secret. "
            "Its Magic aura is strong (the book gives no number); where "
            "it lies is left to the storyguide.",
            "Vis: Auram, soaked into the ice of the walls, drawn out with "
            "a spell like Gather the Essence of the Beast (amount not "
            "given). Magi who use it will have to share or fight for it "
            "with the storm wizards, who are angry at first but may be "
            "talked round to trade or alliance.",
        ),
        **RUMOURED,
    )


# ------------------------------------------------------------ the hunters


def _hunters(transylvania: Transylvania) -> None:
    b = transylvania.b
    w = transylvania.world
    w["fectores"] = b.faction(
        "The Fectores",
        tradition="trad_fectores",
        faction="Hedge coven",
        decides="Its leader",
        ruler="The magi of Laniena, for House Tremere",
        realm="Magic",
        rules=(
            "Gifted hunters trained at Laniena for five years in the "
            "Hunters' Arts; most then join House Ex Miscellanea as Gifted "
            "companions and learn the Parma Magica, but owe their loyalty "
            "to House Tremere. No dhampir may be given Hermetic training."
        ),
        wants="Vampires and other supernatural threats destroyed",
        offers="Trained hunters, Hermetic or not, on the Tribunal's front line",
        summary=paragraphs(
            "House Tremere's corps of monster hunters, named from "
            "interfectores, slayers. A century ago the vampire of a "
            "dead dhampir magus was trying to fill the House with "
            "vampires; the famed hunter Murat of Terezin came to "
            "Coeris and with Radomir of Tremere cleared every one "
            "out. Murat joined House Ex Miscellanea, and the two used "
            "a hoard of initiation scripts, a Gnostic's notes on a "
            "taltós clan he had spied on, to learn how to open a "
            "Gifted person to the Hunters' Arts. Laniena, by the "
            "Aggtelek caves, trains them (see the Hungary chapter).",
            "Two in three of the Gifted children Laniena finds are "
            "trained as Fectores: peasants, soldiers and dhampirs "
            "with no taste for fifteen years of books, three of them "
            "made in the time one apprentice takes. The other third "
            "become Hermetic Fectores, magi Ex Miscellanea who also "
            "hold one Practice Art. Those who prove untrustworthy "
            "never swear the Oath and are spent where the danger is "
            "worst. Some magi call the training a deprivation of "
            "magical power, since the trainees could have learnt the "
            "Hermetic Arts; Laniena answers that they are not yet "
            "members of the Order, and the Tribunal, which is to say "
            "House Tremere, lets it go on. Bendis is the best of the "
            "non-Hermetic Fectores.",
            SKETCHED,
            "The Hunters' Arts, the scattered remnant of the old "
            "taltós magic: three Practice Arts like Techniques, Scry, "
            "Ban and Slay (each a Major Supernatural Virtue), joined "
            "with Foe Arts like narrow Forms (Minor Virtues; the "
            "first Practice Art brings one free). All are Difficult "
            "Arts, raised on the Ability table; against a mortal foe "
            "with no Might every level is 10 higher. Scry forges a "
            "lasting bond to a foe (Per + Scry + Foe + aura) that "
            "gives its direction, then its smells, sounds or sight, "
            "and a sympathetic bonus; a botch ties the foe to the "
            "scryer. Ban makes amulets lasting a Sun from twelve "
            "hours' work, one soaking up wounds from the foe and one "
            "cutting short its powers, and staked hawthorn wards "
            "that lower the Might of a foe inside for three days. "
            "Slay charges a new weapon in a day's chanting; each true "
            "fact about the foe lowers the level by 5 and each false "
            "one raises it, and a hit that penetrates leaves the foe "
            "Incapacitated, after which the weapon is spent. A Fector "
            "has The Gift, the free Fector Social Status, Second "
            "Sight, all three Practice Arts and three Foe Arts, 120 "
            "experience points from training, and no magical "
            "defence but Ban; the Fectores know the Foes Vampire, "
            "Werewolf, Ghost, Nightwalker and Witch. Hermetic "
            "Fectores take a Practice Art as their Major non-Hermetic "
            "Virtue, a Minor Magical Focus against their foe, and "
            "Weak Spontaneous Magic. The Virtues Fector, Scry Art, "
            "Ban Art, Slay Art and the Foe Art are in the catalog.",
        ),
        secrets="Murat of Terezin was a dhampir and rose as a vampire when "
        "he died: he is now a kukudhi living far from Laniena with "
        "his fourth mortal wife and has fathered over twenty dhampir "
        "children. Only Murat the Younger knows, and lets him be for "
        "the hunters his children make.",
    )
    w["sabotnici"] = b.faction(
        "The Sabotnici",
        tradition="trad_hunters",
        faction="Other",
        realm="Magic",
        rules="None: a sabotnik is made by the day of his birth, not by any school",
        offers="Finding vampires, and safety from their direct powers",
        summary=paragraphs(
            "Those born on a Saturday, a day many vampires cannot go out "
            "on or harm anyone born on: such a vampire's direct powers do "
            "not touch them. The Bulgarians call them sabotnici, the rest "
            "of the Balkans vaperari, the Greeks alaphroiskiotoi. A child "
            "born in the Unclean Days between Christmas and Epiphany, or "
            "in the Wolf Holiday of November, is a sabotnik too, but "
            "will rise as a vampire after death; the Wolf Holiday's "
            "children often turn into wolves and become pricolici when "
            "they die.",
            "Not every sabotnik hunts. Many sense the unseen, and can "
            "find a vampire even when it has no body, or tell a magician "
            "or witch. Most who gain powers are men; the few women are "
            "stronger, and read dreams. Dogs can be sabotnici too, the "
            "four-eyed dogs with a black mark over each eye: Zuban is "
            "one (see the Bestiary). Looking through the sleeve of a "
            "sabotnik's shirt shows whether a corpse is a vampire, "
            "though the vampire may strike whoever is looking.",
            SKETCHED,
            "A sabotnik should take Second Sight, perhaps Magic "
            "Sensitivity, and a woman Dream Interpretation; one who hunts "
            "most likely knows the Scry Art. In a team of hunters they "
            "research the foe, gather its connections and track it.",
        ),
    )
    w["glogove"] = b.faction(
        "The Glogove",
        tradition="trad_hunters",
        faction="Other",
        realm="Magic",
        rules="None: a glog is marked at birth (feet first, with teeth, or red-haired)",
        offers="Protection from vampires, and their destruction",
        summary=paragraphs(
            "Hunters marked at birth across the Balkans: born feet first, "
            "with teeth, or with red hair. They take their name from glog, "
            "the black hawthorn, a strong defence against vampires, and "
            "carve staves and swords from it, mostly to guard rather than "
            "to strike. Where a sabotnik finds vampires, a glog shields "
            "people from them and sometimes kills them. Glogove are hot-"
            "tempered and quarrelsome, often in trouble with their "
            "neighbours, and usually strong and athletic.",
            "Black hawthorn grows slowly and twists, too crooked for "
            "planks; as a material it gives +7 to protect from vampires, "
            "+4 to protect from evil and +4 to prevent disease. Laniena "
            "has grown a hedge of it around its houses.",
            SKETCHED,
            "A glog should take Second Sight and often Warrior, an "
            "Affinity or Puissant Single Weapon, and too often Wrathful "
            "or Fury; a trained one knows the Ban or Slay Art. In a "
            "team they fight the foe hand to hand and ward the ground "
            "and their allies.",
        ),
    )
    w["taltos"] = b.faction(
        "The Taltós",
        tradition="trad_nightwalkers",
        faction="Hedge coven",
        realm="Magic",
        rules=(
            "Marked at birth by a caul or extra fingers or toes; at seven "
            "the child dreams of an elder taltós in beast shape and must "
            "beat it in a fight to be initiated."
        ),
        wants="Their villages kept safe from evil creatures by night",
        summary=paragraphs(
            "Hungarian magicians born to fight evil. A taltós who wins "
            "the childhood dream-fight becomes a nightwalker, one of a "
            "band whose spirits go out while they sleep to fight evil "
            "things and keep their villages safe. Among the Székely they were "
            "shape-changing shamans who led their warriors to war.",
            "More than a thousand years ago the taltós were a mighty "
            "tradition of the Balkans, the wise men of the Huns, with "
            "powers from shapeshifting and spirit-walking to potions and "
            "vampire slaying. Quarrelsome, and made worse by The Gift, "
            "they split into factions as their tribes went to war; one "
            "side turned its vampire-killing magic on rival taltós, the "
            "other copied it, and within a few years they had all but "
            "wiped each other out. Today's taltós keep only scraps, and "
            "the Hunters' Arts descend from the same wreck.",
            SKETCHED,
            "The taltós are Nightwalkers (Hedge Magic Revised Edition, "
            "the Nightwalker chapter), and may have other powers; one "
            "who knows the Hunters' Arts most likely has Scry or Ban. "
            "In a team of hunters they ward the ground and their allies.",
        ),
    )
    w["kresnici"] = b.faction(
        "The Kresnici",
        tradition="trad_nightwalkers",
        faction="Hedge coven",
        realm="Magic",
        rules="Born with a clear or white caul",
        wants="Crops and herds kept fertile; the kudlaci beaten",
        summary=paragraphs(
            "The Balkan counterpart of the taltós, strongest in Serbia "
            "and Slovenia. A kresnik, born with a clear or white caul, "
            "has powers that bring fertility. Their sworn enemies are "
            "the kudlaci, sorcerers and vampires born with a red or "
            "black caul who kill livestock and drain the crops; the "
            "kresnici fight them in their phantasm form by night, and a "
            "kudlak who dies becomes a vampire (see the Bestiary).",
            SKETCHED,
            "The kresnici are Nightwalkers (Hedge Magic Revised Edition, "
            "the Nightwalker chapter); one who knows the Hunters' Arts "
            "most likely has Scry or Ban.",
        ),
    )
    w["dhampiri"] = b.faction(
        "The Dhampiri and Vampirdzhia",
        tradition="trad_hunters",
        faction="Other",
        realm="Faerie",
        rules=(
            "A dhampir's fee is fixed by custom and never haggled down; "
            "each arranges, usually with his son, for his own corpse to "
            "be destroyed before it can rise."
        ),
        offers="Vampire slaying, for a fee",
        summary=paragraphs(
            "Hunters born of vampires. A risen vampire often goes first "
            "to its old home and, if its widow is there, gets a child on "
            "her; that child grows up to hunt its kind. Across most of "
            "the Tribunal it is a dhampir (feminine dhampiresa); some are "
            "legends, like Obrad of Niš, priest and dhampir, and Murat of "
            "Terezin, who killed more than two hundred vampires. A "
            "dhampir earns fame, a fee and gifts of beasts, clothes and "
            "food from grateful villages, but hides that he will rise as "
            "a vampire himself when he dies.",
            "A vampire's son is a vampirdzhi in Bulgaria and a "
            "vampijerovik elsewhere in the Balkans (lampijerovik in "
            "Bosnia and Albania); vampires' daughters become witches "
            "instead. A vampirdzhi hunts because he must, with no lore "
            "of his own unless he finds a gift or a teacher, and an "
            "untaught one may not know that he too will rise, so the "
            "curse runs on down a family.",
            "House Tremere forbids its magi to take a dhampir as an "
            "apprentice, after dead dhampir magi let vampires into the "
            "House.",
            SKETCHED,
            "Such a hunter takes the Dhampir Virtue (in the catalog: "
            "Second Sight free, sight in darkness, aging from 50 at -3, "
            "+1 Faerie Lore, rising as a vampire unless the rites are "
            "done), most likely the Slay Art if trained, and Enemy or "
            "Plagued by Supernatural Entity for the parent vampire. In a "
            "team they fight the foe hand to hand. Tibor of Borša is "
            "one.",
        ),
    )
    w["lampijeroviki"] = b.faction(
        "The Lampijeroviki of Sanžak",
        tradition="trad_hunters",
        faction="Family",
        realm="Faerie",
        offers="Vampire hunting for hire, and training in it",
        summary=paragraphs(
            "A whole district of the Sanžak in Serbia peopled by "
            "lampijeroviki, the sons of one vampire's line. They have "
            "made their prey their trade: they know vampires better than "
            "anyone, and hire out as hunters and teachers.",
            "Each of them will rise as a vampire unless the rites are "
            "done on his body.",
            SKETCHED,
        ),
    )
    w["wolf_brotherhoods"] = b.faction(
        "The Wolf Brotherhoods",
        faction="Hedge coven",
        decides="A council",
        realm="Magic",
        rules="Secret; its members are varcolaci who change into wolves",
        wants="Their communities kept safe from vampires",
        summary=paragraphs(
            "Varcolaci (Slavs say vukodlaci or kudlaci) are living men "
            "who take wolf shape, born to it with a red or black caul, "
            "feet first or with teeth, or turned by magic; some become "
            "other beasts. All are distrusted and all rise as bestial "
            "vampires when they die, good or bad. Some band into secret "
            "wolf brotherhoods that guard their people and hunt "
            "vampires, the wolf being the vampire's old enemy; others "
            "kill cattle, steal milk and blight herds, and are said to "
            "eat the moon in eclipses. The mischievous kudlaci are "
            "nightwalkers, fought by the kresnici.",
            "Story seed: House Bjornaer hates brotherhoods of "
            "shapeshifters, which look to it like the Infernal cult it "
            "fears, and may order a Bjornaer magus to root one out, "
            "though the brotherhood is all that keeps a strigoi viu's "
            "vampires off the village.",
            UNRECORDED,
            "A varcolac takes Shapeshifter if born to it or Skinchanger "
            "if he learned it, perhaps Lycanthrope and Animal Ken.",
        ),
    )


# ------------------------------------------------------------ the witches


def _witches(transylvania: Transylvania) -> None:
    b = transylvania.b
    w = transylvania.world
    w["folk_witches"] = b.faction(
        "The Folk Witches",
        tradition="trad_folk_witches",
        faction="Hedge coven",
        decides="Its leader",
        realm="Magic",
        wants="To be left alone, and new recruits",
        summary=paragraphs(
            "Folk witches (Hedge Magic Revised Edition, chapter three) "
            "are common in the Tribunal, drawn, like many lesser "
            "traditions, by Hungary's old law that witches do not exist "
            "and so may not be tried; the Tribunal itself polices hedge "
            "wizards instead, and most keep their heads down. In the "
            "southern mountains around Maramures the Vlach vrajitoarele "
            "lead the scattered cults of Zalmoxis; their powers belong to "
            "the Magic realm, with no Infernal taint. Ludmilla, a "
            "Romanian strigoica who tutors at the Scholomance, leads a "
            "coven and recruits for it among the school's pupils.",
            "Their lore has a use for magi: witches break fevers with a "
            "potion of roof tar from the four corner houses of a "
            "village, and on Saint John's Eve that tar holds a little "
            "Creo vis (see the Slav lands).",
            SKETCHED,
        ),
    )
    w["strigoi_vii"] = b.faction(
        "The Strigoi Vii",
        tradition="trad_nightwalkers",
        faction="Hedge coven",
        decides="A council",
        rules="Only women; a girl may learn the craft by joining a coven",
        wants="The heart-blood of the young; command of the dead vampires",
        summary=paragraphs(
            "Living vampires: Romanian strigoi vii (strigoi viu, "
            "feminine strigoica), the vjestitze of the Balkans. They are "
            "human witches, not faeries, and need no blood to live, "
            "though they drink it. By night one leaves her body as an "
            "owl, a black hen, a moth or a fly and feeds on the "
            "heart-blood of sleepers, most often children. They gather "
            "in covens of women, and folk say they rule the dead "
            "vampires, meeting them at district boundaries to plan the "
            "year's harm. When one dies, powerful vampiric faeries "
            "gather.",
            SKETCHED,
            "They are Nightwalkers (Hedge Magic Revised Edition, chapter "
            "six) and may have more: Infernal witches with maleficia or "
            "Goetic Arts to rule the dead, or faerie wizards using the "
            "Ars Fabulosa to call and bind vampires.",
        ),
    )


# ------------------------------------------------------------ the shamans


def _shamans(transylvania: Transylvania) -> None:
    b = transylvania.b
    w = transylvania.world
    w["cuman_shamans"] = b.faction(
        "The Cuman Shamans",
        tradition="trad_nightwalkers",
        faction="Hedge coven",
        realm="Magic",
        summary=paragraphs(
            "The magicians of the Tengrist Cumans, who worship a sky god "
            "as creator. Their powers resemble the taltós's: scrying, "
            "weather-working, quick healing and fast travel. None seem as "
            "strong as the Bulgar shamans were before Christianity; some "
            "Tremere think something else destroyed those, others that "
            "the Cumans' strongest shamans simply stay out of the border "
            "wars.",
            SKETCHED,
        ),
    )
    w["pecheneg_shamans"] = b.faction(
        "The Pecheneg Shamans",
        faction="Hedge coven",
        decides="Its leader",
        ruler="House Tremere",
        realm="Magic",
        summary=paragraphs(
            "When the Byzantines took the Pechenegs' lands and the "
            "Hungarian kings settled them in the southern Carpathians, "
            "their shamans went into House Tremere's service with many "
            "of their warriors. They count as hospites.",
            UNRECORDED,
        ),
    )


# ------------------------------------------------------------ the companions


def _companions(transylvania: Transylvania) -> None:
    b = transylvania.b
    m = transylvania.magi
    m["thietmar"] = b.magus(
        "Thietmar",
        covenant=None,
        house="",
        age=37,
        type="companion",
        summary=paragraphs(
            "A storm wizard: a tall, timid giant of a man hidden behind "
            "a wild beard, in stinking, badly cured furs and hides "
            "hung with ice. He lives in a cave above the snow and is "
            "known for it in the valleys below. He and the villagers at "
            "the mountain's foot fear and mistrust each other, and have "
            "worked out a round of paths and caches by which they leave "
            "him food and he turns storms away from their homes, so "
            "that neither ever has to meet the other.",
        ),
        traits={"Reclusive": 3, "Persistent": 2},
    )
    m["tibor"] = b.magus(
        "Tibor of Borša",
        covenant=None,
        house="",
        age=25,
        type="companion",
        summary=paragraphs(
            "A dhampir vampire hunter, plain-looking in a peasant's "
            "smock and leather vambraces, his hauberk kept for "
            "trouble, a cloth tied over an empty eye socket and a "
            "spear carved from one piece of wood in his hand.",
            "His father came home from a war unlooked for, and only "
            "later did his mother learn her husband had fallen in "
            "battle a month before. At eleven Tibor left the "
            "Transylvanian grain-lands to hunt that vampire down and "
            "has been a merciless hunter since. A few years ago he "
            "found it at last; it took his eye and left him for "
            "dead. The nearby village mourned him, and, not knowing "
            "the proper rites, thought nothing strange when his "
            "corpse came back to haunt them. Now one rumour says he "
            "is dead and another that he hunts vampires, and he must "
            "live with both.",
        ),
        secrets="The thing that came back was not Tibor: his father's "
        "vampire took his shape, and it still follows him.",
        traits={"Brave": 3, "Implacable": 3, "Uncompromising": 2},
    )


# ------------------------------------------------------------ finish


def finish(transylvania: Transylvania) -> None:
    """Put each faction in its region and link the named people other
    parts made, looked up by name."""
    b = transylvania.b
    w = transylvania.world
    places = transylvania.places
    for key, region in REGIONS.items():
        place = places.get(region)
        if place is not None:
            w[key].place_id = place.id
    region = places.get("transylvania")
    if region is not None:
        places["ice_cave"].place_id = region.id

    b.link(
        w["storm_wizards"],
        "characters",
        transylvania.magi["thietmar"],
        "A storm wizard",
    )
    b.link(w["dhampiri"], "characters", transylvania.magi["tibor"], "A dhampir hunter")
    laniena = transylvania.covenants.get("laniena")
    if laniena is not None:
        b.link(w["fectores"], "covenants", laniena, "Trains them")
    for key, note in (
        ("lexander", "Drills the Fectores"),
        ("murat", "Teaches them the Ban Art; Hermetic Fector"),
    ):
        magus = transylvania.magi.get(key)
        if magus is not None:
            b.link(w["fectores"], "characters", magus, note)
    for faction, name, note in (
        ("fectores", "Bendis", "The ablest non-Hermetic Fector"),
        ("folk_witches", "Ludmilla", "Leads a coven"),
    ):
        person = _named(transylvania, name)
        if person is not None:
            b.link(w[faction], "characters", person, note)
    scholomance = transylvania.covenants.get("scholomance")
    if scholomance is not None:
        b.link(w["storm_wizards"], "covenants", scholomance, "Twice attacked its tower")


def _named(transylvania: Transylvania, name: str) -> Character | None:
    return next(
        (c for c in transylvania.b.saga.characters if c.name.startswith(name)), None
    )


# ------------------------------------------------------------ stats


THIETMAR: StatBlock = {
    "characteristics": {
        "intelligence": 0,
        "perception": 1,
        "presence": 0,
        "communication": 0,
        "strength": 3,
        "stamina": 3,
        "dexterity": 0,
        "quickness": 0,
    },
    "size": 2,
    "confidence": (1, 3),
    "decrepitude": (0, 0),
    "warping": (0, 4),
    "apparent_age": 37,
    "traditions": ["trad_storm_wizards"],
    "virtues_flaws": [
        "The Gift",
        "Storm Wizard",
        "Giant Blood",
        "Personal Vis Source",
        ("Puissant {ability}", {"ability": "Storm Calling"}),
        "Tough",
        "Feud",
        "Reclusive",
        "Visions",
        "Weird Magic",
    ],
    "traits": {"Reclusive": 3, "Persistent": 2},
    "reputations": {"Storm wizard of the high caves (Local)": 4},
    "abilities": [
        ("Area Lore: Mountain", 4, "magical sites"),
        ("Athletics", 2, "running"),
        ("Awareness", 2, "ambush"),
        ("Brawl", 2, "fist"),
        ("Folk Ken", 1, "storm wizards"),
        ("Hunt", 2, "giants"),
        ("Living Language: Native tongue", 5, "peasant speech"),
        ("Organization Lore: Storm Wizards", 5, "ice harvesting"),
        ("Penetration", 2, "Storm Fighting"),
        ("Stealth", 3, "forest"),
        ("Storm Calling", 5, "storm moving"),
        ("Storm Fighting", 5, "attacking giants"),
        ("Storm Riding", 5, "travelling (self)"),
        ("Survival", 4, "mountains"),
        ("Swim", 2, "rivers"),
    ],
    "arts": {},
    "spells": [],
    "notes": paragraphs(
        "Stat block printed in Against the Dark (chapter nine), a storm "
        "wizard built as a Gifted hedge wizard. Age 37 (apparent 37). "
        "Soak +7 (Tough, Stamina and his hide clothes). Combat: dodge "
        "Init 0, Defense +2; fist (Init 0) Atk +3, Def +3, Dam +3; knife "
        "(Init 0) Atk +3, Def +2, Dam +5.",
        "Equipment: warm furs and hides, a knife, and a satchel of magic "
        "ice worth 6 pawns of Auram vis.",
        "His Personal Vis Source is an ice cave; his Feud is with a tribe "
        "of giants, taken on in the Heart of the Storm initiation that "
        "gave him Giant Blood. His Storm Calling is 5, +2 for Puissant. "
        "The book does not name his native language.",
        "Hedge powers: Storm Calling raises a storm (Communication + "
        "Storm Calling + stress die against the storm's size and "
        "duration, paid in Auram vis) or moves any storm; Storm Riding "
        "sees from or travels to any point of a storm he can see; Storm "
        "Fighting attacks anyone within it with buffets, deluge, hail, "
        "erosion or lightning. Each season of ice harvesting yields "
        "(Int + Organization Lore + aura) / 3 pawns of Auram vis. He "
        "risks the storm trance when he gains Warping (see the Storm "
        "Wizards faction).",
    ),
}

TIBOR: StatBlock = {
    "characteristics": {
        "intelligence": 1,
        "perception": 0,
        "presence": 0,
        "communication": -2,
        "strength": 2,
        "stamina": 2,
        "dexterity": 2,
        "quickness": 0,
    },
    "size": 0,
    "confidence": (1, 3),
    "decrepitude": (0, 0),
    "warping": (0, 0),
    "apparent_age": 25,
    "traditions": ["trad_hunters"],
    "virtues_flaws": [
        "Wanderer",
        "Dhampir",
        "Slay Art",
        "Arcane Lore",
        "Famous",
        "Second Sight",
        "Tough",
        "Warrior",
        "Driven (Major)",
        "Mistaken Identity",
        "Faerie Antipathy (Minor)",
        "Infamous",
        "Missing Eye",
        "Reclusive",
    ],
    "traits": {
        "Brave": 3,
        "Implacable": 3,
        "Uncompromising": 2,
        "Crossroads (Sympathy)": -1,
    },
    "reputations": {"Dead (Local)": 4, "Vampire Hunter (Local)": 4},
    "abilities": [
        ("Area Lore: Transylvania", 3, "graveyards"),
        ("Athletics", 2, "chasing"),
        ("Awareness", 3, "searching"),
        ("Bargain", 2, "food"),
        ("Brawl", 3, "fist"),
        ("Craft: Green Wood", 2, "spears"),
        ("Faerie Lore", 4, "vampires"),
        ("Folk Ken", 3, "divining motives"),
        ("Hunt", 3, "two-legged prey"),
        ("Penetration", 2, "Slay Art"),
        ("Ride", 1, "mules"),
        ("Second Sight", 3, "vampires"),
        ("Single Weapon", 5, "short spear"),
        ("Slay", 5, ""),
        ("Foe: Vampire", 0, ""),
        ("Survival", 2, "scrounging from farmland"),
        ("Swim", 1, "fast-flowing water"),
        ("Living Language: Vlach", 5, "Romanian"),
    ],
    "arts": {},
    "spells": [],
    "notes": paragraphs(
        "Stat block printed in Against the Dark (chapter nine). Age 25 "
        "(apparent 25). Soak +9. Encumbrance -1 (3). Combat: short spear "
        "and buckler (Init +1) Atk +10, Def +6, Dam +7; fist (Init -1) "
        "Atk +6, Def +3, Dam +2.",
        "Equipment: metal-reinforced leather armour, a short spear, a "
        "round shield, and several spare spears of black hawthorn.",
        "Second Sight comes free with Dhampir, which also gives the +1 "
        "to his Faerie Lore (printed 4+1). His Faerie Antipathy is the "
        "Sympathy Trait Crossroads -1: at a crossroads every Ability "
        "roll he makes is at -1.",
        "Hedge powers: the Hunters' Arts Slay 5 and Vampire 0 (the Foe "
        "Art free with his first Practice Art), in his Hunters chapter. "
        "With them he charges a new "
        "weapon in a day's chanting to kill one particular vampire "
        "(Dex + Slay + Vampire + aura + stress die against a level of "
        "25, less 5 for each true fact he has learnt about it and more "
        "for each false one); a hit that penetrates leaves it "
        "Incapacitated.",
    ),
}


def stats(transylvania: Transylvania) -> None:
    """Thietmar's and Tibor's stats, entered as the book prints them."""
    b = transylvania.b
    b.stats(transylvania.magi["thietmar"], THIETMAR)
    b.stats(transylvania.magi["tibor"], TIBOR)
