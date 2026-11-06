"""Pagan Monuments and the Magical Treasures of the Ancient Egyptians (Lands
of the Nile pp. 24-56), in paraphrase.

The monuments, the Field of Reeds and the lost treasures are places; the
Seekers' Guild, the monks and the old magicians factions; Gourneh a town and
Al-Quisir a monastery. The creatures with printed blocks are in the Bestiary,
and the book's story seeds are dormant threats. The book's example curses,
wards, talismans and traps are real records on four places of examples, and
Cleopatra's are on her tomb (Tomb tab); projectiles, pits and puzzles, whose
cost varies or which the troupe plays, stay as words, and so do heka and the
animated models, which are notes the app has no rule for (pp. 50-54). Rules the
app already holds (Lector Priests, Cult of Dedun, Murabitin, Blood of the Old
Gods) are cited by page."""

from __future__ import annotations

from typing import Any

from ...models import BodyVis
from ...rules import egyptian_tombs as et
from ...tombs import TombCurse, TombTrap, TombWard
from ..builder import (
    Builder,
    characteristics,
    dormant,
    paragraphs,
    vf_great,
    vf_minor,
    vf_puissant,
)

REGION = "In the region"
LOCAL = "Locally"
FATIGUE_NONE = "Never fatigued"
SKULL = "in the skull of a dog or hyena, found when the body crumbles at death"

#: Two records used twice: as the book's example and on Cleopatra's tomb.
FEAR_CURSE = TombCurse(
    name="I Shall Cast the Fear of Myself into Him",
    art="CrMe",
    level=25,
    rdt="Touch, Sun, Room",
    uses=1,
    excoriation="Overwhelming dread of the tomb or its occupant; victims must flee "
    "at once. (Base 4, +1 Touch, +2 Sun, +2 Room.)",
)
URAEUS = TombWard(
    name="The Destroying Uraeus",
    art="CrIg",
    level=20,
    uses="24/day",
    effect="A rearing cobra statue spews fire, +10 damage to one person passing "
    "without intoning the tomb owner's name. Unlike a Hermetic effect it can be "
    "dodged, by diving aside (p. 42). R: Voice, D: Mom, T: Ind (Base 5, +2 Voice; "
    "+5 24/day).",
    deactivation="Intone the name of the tomb's owner in passing",
)


def _times(entry: Any, count: int) -> list[Any]:
    """A Virtue or Quality taken `count` times."""
    return [entry] * count


def build(b: Builder) -> None:
    _guild(b)
    monuments = _monuments(b)
    reeds = _field_of_reeds(b, monuments)
    giza = _necropolises(b, monuments)
    _defenses(b, monuments)
    _ghost_kits(b, monuments)
    _lost_tombs(b, monuments)
    _cleopatra(b, monuments)
    _creatures(b, monuments, reeds, giza)
    _copts(b)
    _treasures(b, monuments)
    _seeds(b)


# -- the seekers --


def _guild(b: Builder) -> None:
    b.faction(
        "The Seekers' Guild (Al-Matalibeen)",
        faction="Gild",
        decides="An emir chosen by the sultan, often from his most powerful "
        "councillors, leads the guild. Its members elect a chairman, the Naqeeb "
        "al-Matalibeen, whom the emir must approve.",
        rules="Every tomb robber must belong. Membership costs a yearly fee and "
        "20% of all valuables found, paid to the sultan.",
        offers="The guildhall in Cairo and its library of seeker texts; training "
        "from older members; rumours of sites; for members of repute, teams of "
        "specialists to attempt sites that have beaten earlier parties.",
        summary=paragraphs(
            "Explorers have stripped riches from Egypt's monuments for longer "
            "than anyone remembers. Old adventurers write popular books, sold in "
            "most towns, or take apprentices who pay in advance; desperate men "
            "try their luck untrained; in some districts digging for treasure is "
            "a sport, and a plague to those who would keep the monuments whole.",
            "Centuries ago, in a time of drought or war, Egypt's impoverished "
            "rulers turned this trade into a guild. A man who gives steadily to "
            "the royal treasury has the ear of the emir, which brings humble folk "
            "close to the sultan's inner circle, and the emir or his allies may "
            "choose such men as agents.",
            "The guildhall's scrolls tell how to disarm tomb defences, give "
            "charms against curses and rote readings of the hieroglyphs that "
            "matter, and describe the usual decoys and hiding places. Other texts "
            "list sites, both cleared ones ready for new residents and ones not "
            "fully looted.",
            "Locals call hieroglyphs by many names: the Pen of Copts, of the "
            "Temples, of Talismans, of South Arabia, of Priests and of Hermes.",
        ),
        secrets=paragraphs(
            "Rules: the guild's knowledge is the Ability Profession: Seeker; its "
            "site lists are Area Lore (LotN p. 24). A government clerk must be "
            "present at any digging for treasure (p. 25).",
            "In a high-fantasy saga, members may hire magic items recovered from "
            "tombs, and the guild has supernatural allies or even mystical "
            "members (p. 24).",
            "The book compares the guild to the adventurers' guilds of other "
            "fantasy games: a familiar way in for new players (p. 24). The Seeker "
            "manuals describe more, and less, dangerous versions of every trap "
            "listed under the Traps of the Tombs (p. 43).",
        ),
    )
    b.town(
        "Gourneh",
        summary=paragraphs(
            "The village of the finest tomb thieves, at Luxor. Its people have "
            "looted tombs since antiquity, when they built them by day and "
            "emptied them by night. Grandparents teach the young to excavate, "
            "tunnel, bargain and disarm traps.",
            "Few of them fight well, so they hire mercenaries to face the "
            "guardians. When those die, as they often do, it counts as a mark of "
            "skill to bring back the corpses and the wages already paid.",
            "Poor men who cannot pay the guild's fee, and others who will not "
            "give the sultan a fifth, work outside it. Their black market twines "
            "with the lawful trade, and ships artefacts abroad, often to wealthy "
            "pilgrims.",
            "Gourneh families take work as labourers on lawful expeditions; once "
            "a dig is finished and likely to lie unwatched, the man summons his "
            "kin. They count themselves good Muslims and will not kill tomb "
            "guards, but will distract them or drug their food. Fiercely loyal to "
            "family and village, they could be fine allies to magi rich enough "
            "not to think of theft.",
        ),
    )


# -- the monuments --


def _monuments(b: Builder) -> Any:
    return b.place(
        "The Pagan Monuments of Egypt (Birbah)",
        known=REGION,
        aura=0,
        summary=paragraphs(
            "Egypt is famous for its monuments, and a local proverb holds that "
            "every place has its treasure. The dynasties were buried at different "
            "places along the river, and the order of the tombs puzzles even "
            "learned Egyptians; it is thought pious to study it, and some old "
            "Coptic monks may have unravelled it entirely.",
            "A tomb is a machine for keeping a ghost whole. At its least it has "
            "two rooms holding three parts. The mortuary chapel, the one room "
            "built for the living, is where priests and descendants leave "
            "offerings. It holds a statue of the dead, often striding out of a "
            "false door or seated in state. Later chapels shrink to a niche and a "
            "door that cannot open, or stand apart from the tomb. Later still, "
            "statues and then paintings of food replaced real food, and stelae "
            "outside the tomb order the gods to feed the dead whenever a "
            "passer-by reads them.",
            "The serdab is the ghost's private home, often buried in the masonry "
            "with no passage a man could use, and is filled with grave goods or "
            "their pictures. A linteled door facing west, the stele, opens the "
            "way to Duat. It may be only a carving, or tiny, or in the oldest "
            "tombs a slit a few inches wide; later ones bear the owner's name, "
            "then a biography and advice on the afterlife, even spells. Sometimes "
            "a tunnel a few inches across joins serdab and chapel, to let incense "
            "and sound through.",
            "Ghosts prefer a body, and animate statues that are good likenesses, "
            "flaws included: a courtier with the Dwarf Flaw is carved at his true "
            "height, with his crippled foot. Men have an older man's face over a "
            "young warrior's belly; women are younger and fair. There are spares, "
            "because robbers smash statues as a matter of course: it stops a ghost "
            "using them, and many are held with valuable copper clamps or hollow "
            "with treasure inside. The small servant statues, ushabtis or "
            "answerers, take a noble's turn at labour in the Field of Reeds, and "
            "they keep tomb machinery working.",
            "The sepulcher keeps the body, for the refreshment of the ba, the "
            "travelling soul, as the serdab refreshes the ka, the ghost. The "
            "corpse is prepared so the ba may know it, and is wrapped in talismans "
            "and coffins inscribed with words of power. The texts say the ba is "
            "judged by its sins, then journeys through fearful places to the "
            "abode of the solar gods seeking the khu, the Divine spark that left "
            "the body at death. If it succeeds, ka, ba and khu merge into an akh. "
            "Grave robbers prize the body itself for the mummia that preserves it, "
            "a bitumen valued as medicine.",
            "The earliest graves lay under mounds of soil or sand, and a warlord "
            "had to choose between a town, where people could watch his tomb, and "
            "the far desert. Limestone platforms, the mastabas, followed; then "
            "pyramids, jacketed in smooth stone or granite to hide the door. When "
            "the priests offered an afterlife to nobles, and in times of drought "
            "or invasion, smaller tombs were needed: black brick mastabas with a "
            "little pyramidion, a single sepulcher and a niche for a serdab, or "
            "tombs cut into limestone cliffs, with the sepulcher below the chapel "
            "at the foot of a shaft that could be filled with rubble.",
            "Seekers argue over what the tombs hold. Some say gold, jewels and "
            "medicines; others say only early tombs do, and later kings buried "
            "gilded wooden copies, since the likeness becomes real in the Field of "
            "Reeds. Three things are never replaced by likenesses: writing, "
            "favourite possessions, and what preserves the body. Oddly, no true "
            "crown of Egypt has ever been found in any tomb.",
            "Kanqahs, the schools of Egyptian mysticism, are often set in "
            "graveyards, and these have a Divine aura. Ancient temples may keep a "
            "weak Faerie aura from their pagan worship, if any remains.",
        ),
        secrets=paragraphs(
            "Auras (LotN pp. 31, 40): ancient tombs often have Magic auras, from "
            "their preternatural tether and fine sites. Each century a grave site "
            "was in use gives a tether of 1, to a maximum of 5; the aura equals "
            "the tether, may be raised by impressive natural features, and is "
            "often lower where the monuments have decayed. The stele is a vestige "
            "of the Magic Realm, usually aligned to Mentem, of a level equal to "
            "the tomb's aura. An intact mummy is an Arcane Connection for its ka, "
            "giving a Familiarity Bonus of 15 to the Vestige Travel Total; mortals "
            "using the vestige gain nothing. See Realms of Power: Magic pp. 8-10, "
            "20-24.",
            "Ka-work (pp. 27, 30): a ghost can manifest as part of its form "
            "anything in its grave goods or painted on its walls, if not stolen "
            "or defaced, and these things can affect mortals at its choice. "
            "Hermetic magic cannot sense the ba, perhaps because of the Limit of "
            "the Soul, or use the spells written to protect it. Hermetic magi may "
            "use the serdab tunnel with shapeshifting or Intellego; treasure "
            "guides leave it out, as it is no use to thieves.",
            "Carving equipment (p. 31): in a very few tombs the best grave goods "
            "are carving tools, with which a ghost makes likenesses that become "
            "real for it, including food, so it escapes the fate of the unfed. A "
            "rough carving of archers calls up faerie reinforcements. In later "
            "tombs a new object takes one round; in earlier ones, five minutes, "
            "as the carving must closely match known forms; in the earliest, a "
            "miniature statue, up to half an hour. Many tomb owners have a small "
            "servitor statue use the tools for them.",
            "Unfed spirits (p. 31) travel the roads scrounging what humans have "
            "thrown away, which spiritually gives it to the next finder. They hate "
            "this, and may plague people with ill luck until offered libations.",
            "Designing a tomb (pp. 40-44): a place marked as a tomb has a Tomb "
            "tab with the book's kinds, Build Points and costs; statistics are "
            "needed only for a tomb that will last in the saga. A library is "
            "usually wall inscriptions in Ancient "
            "Egyptian or Demotic, in hieroglyphs or hieratic: a history of the "
            "dead as Area Lore or Organization Lore, or spells as Magic Lore or "
            "Supernatural Abilities; a few hold scrolls in sealed jars. Specialists "
            "cost BP as usual; a tomb guardian costs its highest Martial Ability "
            "or Brawl; ghosts may be specialists or teachers.",
            "Vis and Boons (p. 44): vis left as grave goods is paid for as a vis "
            "stock if the tomb becomes a character's home, and helps an akh offset "
            "the penalty of high Might on Study Totals for Transformation. Tombs "
            "may also be vis sources, Corpus most often. The Boons and Hooks of "
            "ArM5 pp. 72-74 and Covenants pp. 6-27 mostly suit; Wealth means the "
            "grave goods are intact, perhaps Unknown to the tomb's residents. In "
            "Nubia every tomb should buy Seclusion, for fear of the dead.",
            "Dedun (p. 39): Temple Priests and Undying Ones of the Cult of Dedun "
            "use tombs as homes and temples, the font of power gained at Initiation "
            "as temple priest and the home of their ghoulish court; adherents "
            "gather there once a month. Detail the tomb's resources when a player "
            "character seeks that Initiation, or for an Undying One as villain or "
            "ally. Such a resident may hold altar priests and adherents as "
            "specialists (p. 42).",
            "The book offers both simple tombs and labyrinthine necropolises; "
            "treat simple ones as early, poor, or built after a long drought "
            "(p. 27).",
        ),
    )


def _field_of_reeds(b: Builder, monuments: Any) -> Any:
    return b.place(
        "The Field of Reeds",
        known=REGION,
        status="Rumoured",
        summary=paragraphs(
            "The afterlife of the Egyptians, in Duat, called by some the Fields "
            "of Turquoise. Its ghosts live in great comfort but cannot stay for "
            "ever: at least once a year each must return to the mortal world to "
            "be fed, and to remember who it was from the offerings and "
            "inscriptions left behind. One that fails loses its memories and "
            "becomes a mut, or fades altogether.",
            "It is called the ka of the Nile Delta: many islands, each the "
            "paradise of one ka, ruling as in life with the servants who followed "
            "him in death. Each island has a copy of its owner's stele. To walk "
            "another's island and leave by another's stele is possible, and a "
            "gross breach of manners.",
            "The common dead expected no more than to farm here for ever; to be "
            "anything else took burial rites only great wealth could buy.",
        ),
        secrets=paragraphs(
            "It lies in the Magic Realm, and most tombs' Magic auras ease the "
            "passage (LotN pp. 26, 32).",
            "Wesir (Osiris) rules it: a powerful Daimon and ally of the Black, "
            "whose ordeals set the pattern for other ka, and perhaps the first "
            "human to reach apotheosis as a Daimon. He opened the path hoping to "
            "recruit friends for the Black. Those who become akhu may join, but "
            "none are forced to fight the Red (pp. 32, 37). Whether stories of "
            "Wesir inspired the faerie god Osiris, or the reverse, nobody knows; "
            "a faerie copy of the Field of Reeds, in the Faerie Realm, is ruled "
            "by that god and peopled by faerie ka (p. 32).",
            "The ba is said to leave the boat of the sun god to visit its body "
            "(p. 30). Thoth judges those who would become akhu, and hearts heavy "
            "with evil feed the Devourer of Souls (p. 37). When the ba needs "
            "protection against the Great Serpents of the Hours it must have the "
            "true words (p. 32).",
        ),
        inside=monuments,
    )


def _necropolises(b: Builder, monuments: Any) -> Any:
    giza = b.place(
        "The Necropolis of Gizeh",
        known=REGION,
        inside=monuments,
        summary=paragraphs(
            "Of all the guardians of the great necropolises the most powerful "
            "is Gizeh's, the Father of Dread: the great effigy of Harmarchis, "
            "Horus at Dawn, which Greek scholars call the Sphinx. It faces the "
            "opposite way from the one Herodotus reports, and nobody recalls "
            "when it turned or why (p. 28).",
            "Between its forepaws lies a small Divine aura, from when Mary laid "
            "the infant Christ in the shade there while they rested (p. 28).",
        ),
        secrets="The Divine aura between its forepaws may be what has locked the "
        "Father of Dread in "
        "place: it no longer gives predictions or warns of grave worldly events, "
        "but it protects the tombs in a subtler way, drawing trespassers into "
        "Faerie (LotN p. 28). The aura's strength is not printed.",
    )
    b.place(
        "The Ramaseum",
        known=REGION,
        inside=monuments,
        summary="The tomb of Rameses II, the pharaoh of the Bible, adorned with "
        "colossal images of himself.",
        secrets="Most ghosts cannot possess statues far larger than they were in "
        "life, as these do not feel like true likenesses. Rameses, the very type of "
        "Pride, thought himself a giant bestriding the world, so might animate the "
        "vast images here. Other pharaohs who share his Personality Flaw might "
        "likewise manifest through huge statues (LotN p. 31).",
    )
    b.place(
        "The Secret Valley near Alexandria",
        known=LOCAL,
        status="Rumoured",
        inside=monuments,
        summary="A hidden valley of rock-cut tombs close to Alexandria. Each "
        "tomb's mortuary chapel stands apart on the banks of the Nile, to keep "
        "the valley's place secret.",
        secrets="The ghosts ride regularly to their chapels for offerings, or "
        "scrounge street rubbish if a chapel is destroyed or untended. Characters "
        "with Second Sight may follow them home; if spotted they are attacked, "
        "and on the Paths of the Dead the spectral weapons are entirely solid "
        "(LotN p. 31).",
    )
    b.place(
        "The House of Life",
        known=REGION,
        status="Rumoured",
        inside=monuments,
        summary="The temple of Thoth where Imhotep's healers trained, the first "
        "known library of magical books and the first hospital. Others like it "
        "followed, but no House of Life has ever been uncovered.",
        secrets="Its library, never found, is the greatest cache of alchemical "
        "texts (LotN pp. 39, 49).",
    )
    b.place(
        "The Treasure House of Qarun",
        known=REGION,
        status="Rumoured",
        inside=monuments,
        summary="Qarun, a man of Moses's time, grew so rich that a train of "
        "strong slaves was needed just to carry the keys to his treasure house. "
        "God, disgusted by his pride, thrust it deep into the sands, and nobody "
        "has found it since. The seekers love the tale: it was buried, but not by "
        "its owner's order, so its defences should be weak beside those of dead "
        "kings.",
        secrets="Where the keys lie is recorded somewhere in the guild's library. "
        "Characters with a clue find many eager young seekers, and many cynical "
        "old ones who chased it in their youth (LotN p. 25).",
    )
    b.place(
        "The Treasure House of Moses's Pharaoh",
        known=REGION,
        status="Rumoured",
        inside=monuments,
        summary="God played the same trick with the treasure house of the "
        "pharaoh of Moses. It too has never been found, though its exact place is "
        "known.",
        secrets="This may mean a Divine regio lies there (LotN p. 25).",
    )
    return giza


def _defenses(b: Builder, monuments: Any) -> None:
    """The book's example curses, wards, talismans and traps, each on a
    place of examples: they are real records, but belong to no one tomb."""
    b.tomb(
        b.place(
            "Curses of the Tombs",
            known=REGION,
            inside=monuments,
            summary="Most tombs have at least one curse, and some carry long "
            "maledictions promising many horrors to any who defile them. Lector "
            "priests laid them with magic now forgotten, writing them in a "
            "prominent place, usually in hieroglyphs, sometimes in Demotic. Each "
            "names a condition, such as defacing the inscription, breaking the "
            "seal, entering impure or disturbing the king, then one or more "
            "punishments.",
            secrets="How literally a condition is taken is left to the storyguide; "
            "it need not be one a Hermetic device could detect (LotN pp. 34, 40). "
            "All are 1/day, Pen 0, R: Touch, T: Room unless noted, and their levels "
            "serve for breaking them as well as for Build Points (p. 41).",
        ),
        kind=et.EXAMPLES.key,
        curses=[
            TombCurse(
                name="A Crocodile Shall Be Against Him in Water, a Snake on Land",
                kind=et.GREATER,
                art="ReAn",
                level=45,
                rdt="Touch, Special, Room",
                uses=1,
                excoriation="Spend more than a night near water and a large "
                "crocodile comes; more than a night far from it, a venomous "
                "snake. Each is an ordinary beast bar its arrival; kill it and "
                "another comes. (Base 30, +1 Touch, +2 Room.)",
            ),
            TombCurse(
                name="He Shall Be Destroyed by Sekhmet",
                art="CrIg",
                level=25,
                rdt="Touch, Mom, Room",
                uses=1,
                excoriation="Arrows of fire hit each target automatically for +15 "
                "damage. (Base 10, +1 Touch, +2 Room.)",
            ),
            TombCurse(
                name="He Shall Capsize and Drown at Sea",
                kind=et.GREATER,
                art="ReAq",
                level=45,
                rdt="Touch, Special, Room",
                uses=1,
                excoriation="Any boat the victim boards sinks; in more than a foot "
                "of water he cannot keep his head above the surface, and drowns. "
                "(Base 30, +1 Touch, +2 Room.)",
            ),
            TombCurse(
                name="He Shall Have No Successors",
                art="PeCo",
                level=35,
                rdt="Touch, Special, Room",
                uses=1,
                excoriation="Destroys the organs of generation. Other readings "
                "might drive off apprentices or proteges, as a Lesser Malediction. "
                "(Base 20, +1 Touch, +2 Room.)",
            ),
            TombCurse(
                name="He Shall Meet Death by a Disease that No Doctor can Diagnose",
                art="PeCo",
                level=35,
                rdt="Touch, Mom, Room",
                uses=1,
                excoriation="A major disease (Disease Penalty -5); mundane medicine "
                "does not help Recovery rolls, only magic. (Base 20, +1 Touch, "
                "+2 Room.)",
            ),
            TombCurse(
                name="He Shall Not Reach his Home, nor Embrace his Children",
                kind=et.LESSER,
                art="CrMe",
                level=25,
                rdt="Touch, Special, Room",
                uses=1,
                excoriation="As the No Sense of Direction Flaw; in the desert it "
                "can kill. (Base 10, +1 Touch, +2 Room.)",
            ),
            FEAR_CURSE,
            TombCurse(
                name="I Shall Wring his Neck Like a Bird",
                art="PeCo",
                level=55,
                rdt="Touch, Sun, Room",
                uses=1,
                excoriation="Spectral hands choke everyone affected; use air "
                "deprivation (ArM5 p. 180) until cancelled or all are dead. "
                "Another may cut a hole lower in the neck: Dex + Chirurgy stress "
                "roll against 9, which leaves the Mute Flaw either way, and a "
                "botch kills. A victim who escapes the room and makes a "
                "Deprivation roll breaks the curse. (Base 30, +1 Touch, +2 Sun, "
                "+2 Room.)",
            ),
            TombCurse(
                name="The Hollow Promise of a Swift Death",
                art="CrVi",
                level=9,
                rdt="Per, Sun, Ind",
                uses=2,
                excoriation="No curse at all, and a constant effect: magical "
                "detection sees a 30th-level curse. It may be made at other "
                "levels: a magnitude up or down in the base effect appears as "
                "two up or down. (Base 3 taint with magic, +2 Sun; +3 "
                "environmental trigger, +1 2/day.)",
            ),
        ],
    )
    b.tomb(
        b.place(
            "Wards of the Tombs",
            known=REGION,
            inside=monuments,
            summary="The favourite wards of Egypt hide a tomb from sight or nudge "
            "people gently away. The books of treasure hunters are full of ways "
            "round them: stand on a certain rock at dawn, say, wearing a headdress "
            "of red feathers. Against the strongest such tricks fail.",
            secrets="Wards (LotN pp. 35, 40). Most have a way to deactivate them "
            "for a while, and they are likelier than other talismans to have "
            "Penetration, since they are aimed at spirits. Books on bypassing the "
            "strongest are Initiation Scripts for Mystery Virtues, which may open "
            "a single site or, unknown to the reader, many: some grant Second "
            "Sight and teach regio crossing, others give resistance to talismans "
            "of one substance or school. A ward repels rather than harms, as when "
            "sand is about to turn to glass and seal the tomb, or an illusion has "
            "a flaw.",
        ),
        kind=et.EXAMPLES.key,
        wards=[
            TombWard(
                name="Nothing But Sky and Sand",
                kind=et.WARD,
                art="MuIm",
                level=39,
                uses="constant",
                effect="The structure seems a sand dune in every way. R: Touch, D: "
                "Sun, T: Str (Base 5, +1 Touch, +2 Sun, +3 Structure; +3 "
                "environmental trigger, +1 2/day). Avoided, for instance, by "
                "spotting a stray shadow or working out the stars that reveal it. "
                "It may fail from one angle or under sprinkled water (p. 42).",
            ),
            TombWard(
                name="Turn the Interloper",
                kind=et.WARD,
                art="ReCo",
                level=30,
                uses="unlimited",
                effect="Spins anyone who triggers it, usually at a doorway, through "
                "180 degrees (Base 10, +2 Voice; +10 unlimited uses). Avoided by "
                "bracing against it.",
            ),
            TombWard(
                name="A Sovereign Ward Against Robbers",
                kind=et.WARD,
                art="ReCo",
                level=49,
                uses="constant",
                effect="Humans can hardly enter and cannot harm the structure from "
                "outside (Base 15, +1 Touch, +2 Sun, +3 Structure; +3 environmental "
                "trigger, +1 2/day). Overcome by forcing through, or throwing a "
                "stone to dislodge the amulet behind it.",
            ),
        ],
    )
    b.tomb(
        b.place(
            "Talismans of the Tombs",
            known=REGION,
            inside=monuments,
            summary="A talisman here is a small magic item set off by an expected "
            "act: step through a door and the lintel pours fire on your head. "
            "Most work on the gross elements rather than on emotion or luck. Their "
            "makers could not resist their own work, so built in a way to put each "
            "to sleep. Egyptian combat magic was poor, and Moses's contest with "
            "the pharaoh's magicians was a sort of primitive certamen, but their "
            "lasting curses, talismans and wards were sometimes exceptional, and "
            "always made of opulent materials.",
            secrets="Talismans (LotN pp. 33-35, 41-42). Ancient Egyptians had no "
            "general Magic Resistance, so talismans aimed at people mostly have no "
            "Penetration: even young magi ignore them, but grogs and equipment do "
            "not. A particular spell effect usually renders one inert until "
            "sunset; in a laboratory a magus finds which, by trial or as with a "
            "magic item's triggers (ArM5 p. 100). Design them by the Hermetic item "
            "rules, or Learned Magic with the provisos of Chapter 5; few relied on "
            "one-use seals or temporary amulets. Though costed as Hermetic "
            "effects, they need not obey Hermetic limits. Left in a strong aura, "
            "enchantments take Warping.",
        ),
        kind=et.EXAMPLES.key,
        wards=[
            TombWard(
                name="Apedemak's Strength",
                art="MuTe(Re)",
                level=40,
                uses="unlimited",
                effect="Animates a huge lion statue, which obeys one spoken order. "
                "Warped, it needs a Com + Leadership roll against 9 to override its "
                "last order: attack all who cross the threshold. Dogged, nearly "
                "indestructible, an unskilled fighter; to hide or run from it is "
                "the roll against its Ease Factor. R: Per, D: Conc, T: Ind (Base 5, "
                "+1 Conc, +1 stone, +1 size, +1 requisite; +5 maintains "
                "concentration, +10 unlimited).",
            ),
            URAEUS,
            TombWard(
                name="On The Presentation of Face of Lost Companions",
                kind=et.NO_OBSTACLE,
                art="CrIm(In)",
                level=15,
                uses="1/day",
                effect="After a fatal trap, an ochre-red image of the dead person's "
                "face comes out of a wall nearby. One known version shouts a "
                "warning in an old tongue against disturbing kings. Sinister "
                "versions enslave the ghost as a guardian. R: Touch, D: Conc, T: "
                "Ind (Base 2, +1 Touch, +1 Conc, +1 legible words and moving image, "
                "+1 requisite; +5 maintain concentration).",
            ),
            TombWard(
                name="On Lowering the Waters",
                art="ReAq",
                level=28,
                penetration=16,
                uses="1/day",
                effect="Many tombs hold living water that strains to drown "
                "intruders. It is in effect a Might 15 water elemental (Realms of "
                "Power: Magic), and this talisman wakes and commands it; it may be "
                "tricked with a new command. R: Touch, D: Sun, T: Ind (Base 5, +1 "
                "Touch, +2 Sun; +8 Penetration 16).",
            ),
        ],
    )
    b.tomb(
        b.place(
            "Traps of the Tombs",
            known=REGION,
            inside=monuments,
            summary=paragraphs(
                "The plainest defence is to bar the way. Iron was rare, so passages "
                "are choked with rubble, or in rich tombs with granite blocks so "
                "hard the manuals say to quarry round them through the limestone. "
                "Pits deter entry, and sloping passages may be filled with sand and "
                "lime, soaked until it sets into a rough cement.",
                "Architects hide entrances behind stone jackets, leave unfinished "
                "chambers to send robbers home, and put a false wall or floor "
                "before the sealed way to the true rooms. Bronze clockwork, hidden "
                "in walls, floors, statues or arks, reloads projectiles, resets "
                "itself, moves great objects and answers to pressure plates and "
                "levers.",
                "Some rooms can only be passed by a puzzle, a lock and trap in one, "
                "built to shut out those without leisure or letters: moves of a "
                "board game, or hieroglyphs touched in order, with a sign or riddle "
                "somewhere before the door. The favourite game was senet, played no "
                "more in Mythic Africa; many seekers report rooms themed on "
                "backgammon, though those who know its history doubt it, and some "
                "suspect faeries.",
            ),
            secrets=paragraphs(
                "Spells that detect metal find mechanisms, and destroying one can "
                "seize the trap (LotN p. 32).",
                "Puzzles: Hermetic magi can subvert them, say with Rego from "
                "outside the door. A dedicated magus might collect accounts to "
                "deduce senet's rules, or some ghosts know the game. As a minigame, "
                "play a real historical game; with combat-minded troupes put the "
                "characters on the board to fight the pieces; let magic cheat "
                "(p. 33).",
                "Projectiles, cost varies: if not escaped that round, stress die + "
                "weapon Damage (ArM5 p. 177), soaked. Several projectiles are "
                "rolled and added; machines add +1 to +5 by human Strength "
                "equivalent. Many are poisoned (p. 180).",
                "Pits, cost varies: falling damage (ArM5 p. 181), plus the nearest "
                "weapon's Damage for a dangerous floor: a 20-foot pit of sharp "
                "stakes is stress die + 20 + 5, against stress die + Soak. An "
                "architect's aim may add more.",
            ),
        ),
        kind=et.EXAMPLES.key,
        traps=[
            TombTrap(
                name="Labyrinth",
                harm="scare",
                ease=6,
                roll="Int + Concentration",
                text="A maze of tunnels and identical passages. Retracing steps "
                "takes three times as long as going in.",
            ),
            TombTrap(
                name="Prison Room",
                harm="minor",
                ease=6,
                roll="Per + Awareness",
                once=True,
                text="A dead-end chamber with treasure or inscriptions. The roll "
                "hears the mechanism in the delay; otherwise a door too heavy to "
                "lift drops. The treasure is painted wood, the inscriptions "
                "nonsense or taunts.",
            ),
            TombTrap(
                name="Rock Fall",
                harm="minor",
                ease=9,
                roll="Qik + Athletics - Encumbrance",
                text="Boulders roll on those climbing a slope: stress roll or +10 "
                "damage. Impact as ArM5 p. 181. Larger falls cost more: an "
                "avalanche +24 and perhaps suffocation (p. 180); rocks outweighing "
                "a character +21; about his weight +18; smaller, about +1 per 10 "
                "pounds. Spiked balls do more, sand, bones or the bodies of those "
                "left with the horses less.",
            ),
            TombTrap(
                name="Medicinal Powders",
                harm="serious",
                ease=9,
                roll="Sta",
                text="Fine poison in a sealed room, stirred by the door and by "
                "movement. It sears and disfigures, a Medium Wound, unless the "
                "roll is made. Others cost Fatigue, blind, paralyse, or burn.",
            ),
            TombTrap(
                name="Head Wires",
                harm="minor",
                ease=15,
                roll="Per + Awareness",
                text="Neck-high wires, +9 damage that most armour does not stop.",
            ),
            TombTrap(
                name="Head Wires behind a Pit",
                harm="fatal",
                ease=15,
                roll="Per + Awareness",
                text="Strung behind an obvious pit, so a jumper hits them: +18 "
                "damage that most armour does not stop.",
            ),
            TombTrap(
                name="Dead Drop",
                harm="fatal",
                ease=12,
                roll="Per + Awareness",
                text="A slightly less worn paving stone opens on a ten-pace fall "
                "to stone, +30 damage.",
            ),
        ],
    )


def _ghost_kits(b: Builder, monuments: Any) -> None:
    b.place(
        "Ghosts of the Tombs",
        known=REGION,
        inside=monuments,
        summary=paragraphs(
            "Each tomb has a principal ka, the one it was built for, and perhaps "
            "the ghosts of those buried to guard or serve him. Muslim writers "
            "think of the ka as the body's ghostly double. They are resilient, "
            "well-found and dangerous, unlike Western spectres: transparent but "
            "fully coloured, the mightier the more solid. Other guardians are "
            "faeries, called up by long-dead lector priests or bound by talismans, "
            "still feeding on the stories told of them.",
            "Akhu are the final state of the greatest dead, formed from ba, ka "
            "and khu. They need no food or prayer and no longer need a tomb, "
            "though some enjoy the access it gives. Imhotep is thought to have "
            "taken two thousand years to finish the change, which is not usual. "
            "Each is unique, many can take an animal shape, and all texts agree "
            "they can have children. Their names, placed at chapels and on "
            "monuments, feed them whenever read.",
            "A just pharaoh kept the world in balance, so the floods came and "
            "food was plenty, and could enrich or ruin men by decree. All were "
            "thought to command spirits, though often by asking a divine patron "
            "to punish the disobedient. Some had strange powers from their lives: "
            "one, it seems, could slow time around him, so that his companions "
            "aged less and spells took longer to run out.",
        ),
        secrets=paragraphs(
            "Quick ghost (LotN pp. 35-36). Take a mortal; Magic Might 5 to 25; "
            "Characteristics as in life, and it cannot fail Fatigue rolls. Remove "
            "Virtues and Flaws of social role or body, which need not balance. "
            "Most take Magical Monster, some Magical Friend; add Magic Spirit. "
            "Abilities stay, many useless. Intangible and unharmed by weapons or "
            "fire; Protection and Soak work against magic; vulnerable to Mentem. "
            "Add a +3 trait tied to mortal business. Few have Donning the "
            "Corporeal Veil (5 points, material until released, gear too). A new "
            "power is based on a Hermetic spell, at 1 Might per 5 levels, or per "
            "10 for one that affects only itself, Init Qik - magnitude/2. Vis, "
            "usually Mentem, equals Might/5.",
            "Possess Statue (Minor Power): 3 points, Init Qik -3, Terram or "
            "Herbam. Steps into and animates a statue at Range Personal, one at a "
            "time. Improved Powers often cuts the cost to 0. The statue's physical "
            "attacks must Penetrate. Wooden: ReHe 25 (Base 10, +2 Sun, +1 "
            "constant). Stone: ReTe 25 (Base 3, +2 Sun, +1 stone, +1 constant, "
            "+2 intricacy). Metal: ReTe 30 (Base 3, +2 Sun, +2 metal, +1 "
            "constant, +2 intricacy).",
            "Quick animated statue (p. 36). As above with Might 5 to 25 (a "
            "possessing ghost's own Might). Rarely not life-size: -2 Str and +1 "
            "Qik per Size lost, the reverse per Size gained. Remove social "
            "Virtues; add Magical Monster and Magic Thing. Soak: wood +9; ceramic, "
            "soft stone or soft metal +15; hard stone +18; hard metal +21. Armour "
            "adds nothing unless harder than the statue. To destroy the face, "
            "announce it and inflict a Medium Wound; that drives the ghost out. "
            "Weapons of stone or bronze -1 damage; gilded wood in place of metal "
            "-2; alchemically hardened bronze as steel. Fists and kicks +1 for "
            "wood or stone, +2 for metal; brawling weapons unadjusted. Boost "
            "combat with Qualities as the story needs. Vis, usually the "
            "material's Form, is Might/5. Al-jazari, the automatons, use these "
            "rules on any reworked monster, and have no Might.",
            "Royal ghosts (pp. 36-37): most dynasties claimed a faerie god "
            "invested the pharaoh when he begot his heir, giving the Major Blood "
            "of the Old Gods; other descendants have the Minor (Virtue, p. 36; "
            "Sympathy Trait usually Royalty, or a god's purview). The Ptolemies "
            "built their own god, Serapis, an ally but no ancestor. Longer rites "
            "and coffin texts allow Transformation after death (Realms of Power: "
            "Magic p. 52), and tombs were sometimes stocked with vis for it.",
            "Akhu (p. 37; The Mysteries: Revised Edition pp. 82-86): a Daimon, an "
            "indestructible being acting through a self-sustaining Aspect. Build "
            "as Magic Spirits: Might 20 for a noble with the simplest coffin "
            "texts, up to 60 for the greatest pharaohs, the longer to finish the "
            "greater the Might. They have virtuous traits. All have long since "
            "gained all they can from readers of their names, so are Winter "
            "creatures, and may be summoned by name or relics. Offspring may have "
            "Mythic or Magical Blood.",
        ),
    )


def _lost_tombs(b: Builder, monuments: Any) -> None:
    saqqara = b.place(
        "The Tomb of Imhotep",
        known=REGION,
        status="Rumoured",
        inside=monuments,
        summary="Probably at Saqqara. Imhotep, priest of Thoth under Djoser, "
        "the first king with a pyramid, is said to have invented architecture and "
        "medicine; the column and lintel come from his designs. Classical sources "
        "mention his tomb, but it has never been traced. He took every scroll he "
        "owned to the grave.",
        secrets=paragraphs(
            "Its defences and writings would settle the Order's old dispute "
            "whether modern magic outstrips the ancient. Some magi hold that "
            "Bonisagus built on earlier traditions and that Original Research has "
            "gone further; others that the world declines from golden ages, and "
            "that research mostly fits old wisdom into Hermetic Theory (LotN p. "
            "39).",
            "Coptic magicians think Imhotep took great pains to leave no trace. "
            "Some magi think he was also Asclepius and Hermes Trismegistus, and "
            "hope those names lead to it; others dispute this.",
        ),
    )
    imhotep = b.magus(
        "Imhotep",
        covenant=None,
        house="",
        age=None,
        type="mythic companion",
        summary="Priest of Thoth in the reign of Djoser, inventor of architecture "
        "and medicine, whose healers trained in the House of Life. Thought to have "
        "needed two thousand years to become an akh (LotN pp. 37, 39).",
    )
    b.link(imhotep, "buried at", saqqara)
    antonius_tomb = b.place(
        "The Tomb of Marcus Antonius",
        known=REGION,
        status="Rumoured",
        inside=monuments,
        summary="Probably near Alexandria. The Romans never found it, for all "
        "their searching and the thousands who saw the funeral or helped to "
        "build it. Cleopatra meant to lie here beside him.",
        secrets=paragraphs(
            "Cleopatra had at least two tombs made; this was the intended one, "
            "far closer to Alexandria than her final rest (LotN p. 39).",
            "Hermetic magi want her resting places for Cleopatra's Book, and "
            "because some say the fire at the Great Library covered the hiding "
            "of its books from Rome, with the 200,000 books of Pergamon that "
            "Antonius took by force as a wedding gift for her.",
        ),
    )
    antonius = b.magus(
        "Marcus Antonius",
        covenant=None,
        house="",
        age=None,
        type="mythic companion",
        summary="Roman lover of Cleopatra, and the only Roman known to have had "
        "Egyptian burial rites. As governor of Italy for Julius Caesar he knew "
        "the Order of Mercury, and may offer insight into its magic (LotN pp. "
        "39-40).",
    )
    b.link(antonius, "buried at", antonius_tomb)
    b.magus(
        "Caesarion",
        covenant=None,
        house="",
        age=None,
        type="mythic companion",
        summary="Son of Cleopatra and Antonius, says the book, and perhaps the "
        "forefather of a secret society built on Egyptian rites (LotN p. 40).",
    )


def _cleopatra(b: Builder, monuments: Any) -> None:
    tomb = b.place(
        "The Tomb of Queen Cleopatra",
        known=REGION,
        status="Rumoured",
        realm="Magic",
        aura=6,
        inside=monuments,
        summary="The prize of every treasure hunter: the resting place of "
        "Cleopatra VII, last pharaoh of Egypt. Hunters have sought it high and "
        "low, and many plundered pyramids have been claimed for it. The Romans "
        "never recovered her wealth, and it is believed to lie with her.",
        levels=[
            b.level(
                "The pool's regio",
                3,
                "Faerie",
                enter="Open on the eve of the anniversary of Cleopatra's death, "
                "12 August; at other times a Regio Sight roll against 23 (ArM5 "
                "p. 189).",
                notes="Each year on that night hordes of asps with a small Faerie "
                "Might pour out to fight the mongooses. What lies within is left "
                "to the storyguide.",
            )
        ],
        secrets=paragraphs(
            "It is no pyramid but a walled compound at Taposiris Magna, a lonely "
            "bay west of Alexandria, far from any trade route. A handful know the "
            "place, among them the jinniyya Nahrou, whose Might shielded her from "
            "the concealing enchantment (LotN p. 44).",
            "The Garden: fifteen-foot walls with one great pylon gate, carved "
            "with Isis and with cows, cats, lionesses, vultures and hippopotamuses "
            "for the goddesses. Inside is a temple of Isis and a rich garden of "
            "food and medicinal herbs, dates, bananas and other fruit, feeding "
            "families of mongooses. Warping has made some of these Magic Animals, "
            "who rule the rival clans like royalty. The pool at the centre is the "
            "regio's entrance. The asps' bodies are vis, usually eaten quickly by "
            "the magical mongooses for Transformation.",
            "The Temple: its roof rests on columns carved as four handmaidens, "
            "each face many times repeated. Walls hold spells of midwifery and "
            "healing in Koine Greek and Ancient Egyptian, some studied as texts on "
            "the Arts of Learned Magicians, though not quite the same Arts; "
            "Quality is what a 13th-century magician can draw from them. Two "
            "statues of Sekhmet, bows drawn, each loose a fiery arrow a round at "
            "anyone in the temple unless Cleopatra's name is intoned. Four "
            "priestess handmaidens died to guard her, and their ghosts haunt the "
            "place, sorceresses in healing, in destruction, in transformation and "
            "in control and enchantment.",
            "The Tomb: an inclined passage from the temple levels off, with the "
            "soporific trap, then turns at the pit. The burial chamber, directly "
            "under the temple's statue of Isis, has a cursed door. The body lies "
            "under a net of pure gold, in a painted wooden coffin shaped like the "
            "queen, in a gold sarcophagus, in a stone sepulcher, ringed by four "
            "goddess statues with heads of vulture, lioness, crocodile and asp. A "
            "hidden way in the rear wall leads by a short corridor to a second, "
            "cursed door and the treasury of Ptolemaic Egypt: over ten thousand "
            "Mythic Pounds of gold, gems and ivory, a legendary source of income.",
            "Library: later history of Roman Egypt, summa on Area Lore: Egypt, "
            "Koine Greek, Level 5, Quality 9. Medicinal herbs, tractatus on "
            "Medicine, Demotic, Quality 10. Healing spells, tractatus on the "
            "Learned Magician Form Salutem, Demotic, Quality 11. Magical wards, "
            "summa on the Learned Magician Technique Tueor, Demotic, Level 10, "
            "Quality 7. Eight formulae for pharmaceutical theriacs, Demotic, 5 BP "
            "each (Art & Academe p. 77). Creation myth, tractatus on Faerie Lore, "
            "Demotic, Quality 7. Handmaidens' diaries on crumbling papyrus: three "
            "tractatus on Charm, Etiquette and Intrigue, Koine Greek, Quality 5.",
            "Specialists: four ghostly priestesses, each with the equivalent of "
            "one Hermetic Technique at 20; five mongoose monarchs, Leadership 5.",
            "Vis sources, a year: 5 Animal (slain asps), 2 Aquam (the pool), 3 "
            "Herbam (exotic fruit), 1 Ignem (a potsherd exposed to a Destroying "
            "Uraeus), 3 Terram (an item worth at least 10 Mythic Pounds left a "
            "year in the treasure chamber). Vis stocks: 10 Creo (unguents, pastes, "
            "medicines), 5 Imaginem (cosmetics, perfumes), 30 Terram (gold objects "
            "in the treasure room).",
        ),
    )
    _cleopatra_tomb(b, tomb)
    queen = b.magus(
        "Cleopatra",
        covenant=None,
        house="",
        age=None,
        type="mythic companion",
        summary="Last queen of Egypt, Cleopatra VII Thea Philopator. Mythic "
        "Egyptians dismiss the Roman tales as her foes' lies: to them she was a "
        "just and wise ruler, a peer in the salons of her wisest subjects, and the "
        "author of a book of alchemy gathering her forebears' wisdom and her own "
        "medicine. She believed herself a reincarnation of Isis, and allied with "
        "Marcus Antonius against Octavian. She died by a sacred asp, some say a "
        "suicide in captivity, and her body was stolen for burial (LotN pp. 39, "
        "44).",
        secrets="The youngest possible akh, she may not have finished the change. "
        "Her ka may seek Hermetic aid to clear her ba's path, which disposes her "
        "well to magi; if so she is a remarkable communicator, and could be a "
        "peerless teacher of Egyptian mysteries. Cleopatra's Book is said to be "
        "the height of alchemy, and no Egyptian library admits to a copy.",
    )
    b.link(queen, "buried at", tomb)
    nahrou = b.magus(
        "Nahrou",
        covenant=None,
        house="",
        age=None,
        type="mythic companion",
        summary="A jinniyya.",
        secrets="One of the few who know where Cleopatra's tomb lies; her Magic "
        "Might protected her from its concealing enchantment (LotN p. 44).",
    )
    b.link(nahrou, "knows of", tomb)


def _cleopatra_tomb(b: Builder, tomb: Any) -> None:
    """The book's details of her tomb (LotN p. 46). She was the last pharaoh,
    and its 484 Build Points fit only a major monarch's 500; the fear curse
    follows the rule for its level, so the curses come to 42."""
    latin = "Anyone speaking Latin in the burial chamber"
    b.tomb(
        tomb,
        kind="major_monarch",
        boons="Wealth (Resources, Major); Aura, Seclusion, Vivid Environment "
        "(Site, Minor); Edifice (Fortifications, Minor)",
        hooks="Regio (Site, Major); Crumbling (Fortifications, Minor); Guardians, "
        "Legendary Site (Surroundings, Minor); Dwindling Resources (Resources, "
        "Minor)",
        hook_points=7,
        other="library 141, specialists 105, vis sources 70, vis stocks 9",
        other_bp=325,
        curses=[
            TombCurse(
                name="The Romans' Curse: boils",
                art="PeCo",
                level=20,
                rdt="Touch, Room",
                uses=1,
                condition=latin,
                excoriation="Boils that leave those who seek to disturb her "
                "hideous, but do no harm (Base 5, +1 Touch, +2 Room).",
            ),
            TombCurse(
                name="The Romans' Curse: sickness",
                kind=et.LESSER,
                art="PeCo",
                level=25,
                rdt="Touch, Special, Room",
                uses=1,
                condition=latin,
                excoriation="As the Fragile Constitution Flaw: a sickness no "
                "medicine helps.",
            ),
            TombCurse(
                name="The Romans' Curse: no children",
                art="PeCo",
                level=35,
                rdt="Touch, Special, Room",
                uses=1,
                condition=latin,
                excoriation="As He Shall Have No Successors.",
            ),
            {
                **FEAR_CURSE,
                "condition": "Anyone who breaks the clay seal on the treasure chamber",
            },
        ],
        wards=[
            TombWard(
                name="The Shrouded Oasis",
                kind=et.WARD,
                art="Non-Hermetic",
                level=50,
                effect="On the compound walls, as The Shrouded Glen (ArM5 p. 152). "
                "With Penetration 0 it only repels mundane hunters. A magus "
                "researching a breakthrough in enchanting Ritual effects can draw "
                "insight from it.",
            ),
            TombWard(
                name="First Statue of Sekhmet",
                art="CrIg",
                level=20,
                uses="24/day",
                effect="As a Destroying Uraeus: bow drawn, it looses a fiery arrow "
                "a round at anyone in the temple.",
                deactivation="Intone Cleopatra's name",
            ),
            TombWard(
                name="Second Statue of Sekhmet",
                art="CrIg",
                level=20,
                uses="24/day",
                effect="As a Destroying Uraeus: bow drawn, it looses a fiery arrow "
                "a round at anyone in the temple.",
                deactivation="Intone Cleopatra's name",
            ),
            TombWard(
                name="The Djet",
                kind=et.NO_OBSTACLE,
                art="Non-Hermetic",
                level=100,
                effect="A twenty-foot statue of Osiris in thirty fitted pieces of "
                "green stone: with burning incense in its hand it answers one "
                "question from each person, who must truly want the answer for "
                "himself. It knows only what some dead person knew, so nothing of "
                "the future, and answers at random otherwise. It lies scattered "
                "through the complex, one piece missing and unaccounted for; "
                "assembling it takes skill, and instructions are in hieroglyphs "
                "on the statue.",
            ),
        ],
        traps=[
            TombTrap(
                name="The Soporific Corridor",
                harm="serious",
                ease=9,
                roll="Sta",
                text="Two stone doors close off a stretch of corridor; opening "
                "them brings a faint floral smell and dust eddying in the light. "
                "All within must make the roll or sleep for as many minutes as "
                "they failed by, while immune mongooses swarm through ground-level "
                "holes to eat them: a Light Wound each, worse by a step every two "
                "minutes.",
            ),
            TombTrap(
                name="The Covered Pit",
                harm="serious",
                further_bp=et.HARMS["minor"].build_points,
                ease=12,
                roll="Dex + Athletics - Encumbrance",
                spot=15,
                text="Before the burial chamber door: safe at first, but walking on "
                "it arms it, taking about a minute. Per + Awareness at +3 to the "
                "Ease Factor hears the arming; the roll leaps clear when cautious, "
                "harder for those fleeing the fear curse. Twelve feet deep with "
                "spikes: +12 from the fall, +8 from each of up to four spikes "
                "(simple die 1-2 none, 3-4 one, 5-6 two, 7-8 three, 9-10 four).",
            ),
            TombTrap(
                name="The Sand of the Treasure Chamber",
                harm="scare",
                ease=15,
                roll="Per + Awareness",
                once=True,
                text="Stepping on the threshold sends tons of sand from the roof, "
                "to bury the treasure; it can be outrun by those not yet inside.",
            ),
        ],
    )


# -- the Bestiary --


def _creatures(b: Builder, monuments: Any, reeds: Any, giza: Any) -> None:
    b.creature(
        "Canocephalus Decapitator",
        page="p. 27",
        realm="Faerie",
        might=25,
        form="Animal",
        size=2,
        cunning=True,
        tires=False,
        fatigue_levels=FATIGUE_NONE,
        how_many="Often in pairs; a pack may gather to defend a graveyard",
        place=monuments,
        block={
            "characteristics": characteristics(5, 3, 0, 0, 7, 0, 2, 3),
            "virtues_flaws": [
                *_times("Greater Power", 2),
                "Huge",
                "Feast of the Dead",
                "Hybrid Form",
                *_times("Improved Initiative", 2),
                "Incognizant",
                (
                    "Traditional Ward",
                    {"ward": "removal of the medallions"},
                ),
            ],
            "abilities": [
                ("Athletics", 5, "chasing"),
                ("Awareness", 5, "intruders"),
                ("Brawl", 5, "knives"),
                ("Hunt", 5, "in graveyards"),
            ],
            "traits": {"Hates defilers": 5},
            "reputations": {"Homicidally Territorial (General)": 5},
        },
        attacks=[
            b.attack("2 knives", 5, 11, 8, 12),
            b.attack("Bite", 7, 8, 7, 8),
        ],
        soak=6,
        powers=[
            b.power(
                "Chilling Howl",
                4,
                1,
                "Corpus",
                rtd=("Voice", "Sun", "Group"),
                does="Paralyses completely all who hear its war cry, like a "
                "wolf's howl, a hyena's mocking laugh or a setbeast's chitter by "
                "various reports. (Base 5, +2 Voice, +2 Sun, +2 Group.)",
            ),
            b.power(
                "Damaging Effect",
                2,
                -2,
                "By weapon",
                rtd=("", "Diameter", "Part"),
                does="Makes all its weapons exceptionally sharp for two minutes: "
                "Damage +5. (Base 5, +1 Part, +1 Diameter; base below the "
                "Hermetic level, as Realms of Power: Faerie p. 58.)",
            ),
            b.power(
                "Decapitate",
                4,
                -2,
                "Corpus",
                rtd=("Touch", "", ""),
                does="Cleanly removes the head of a victim struck in combat. "
                "(Base 40 instant death, +1 Touch, 5 levels on cost.)",
            ),
        ],
        vis=[BodyVis(5, "", SKULL)],
        equipment="Knives of obsidian or alchemically toughened bronze; light "
        "Egyptian armour (boots, pectoral, greaves) or clothes, jewellery.",
        appearance="A medieval reading of seals of Anubis: a fit warrior with a "
        "savage jackal's head, among the corpses of his beheaded enemies.",
        notes=paragraphs(
            "The spirits that frighten most people off tomb robbing. They guard a "
            "whole graveyard, not one tomb, and grow more active at night. Powerful "
            "magic in the graveyard may draw them to the tomb door, to ambush "
            "characters coming out. A pack fights as a trained group.",
            "Sta is printed as Tireless, and Com as n/a; both are left at 0 here. "
            "Combat damage excludes the +5 of Damaging Effect. The knives use "
            "shortsword statistics for smaller users but remain Brawling weapons "
            "in these huge hands. Its Abilities are the book's Pretenses (Realms "
            "of Power: Faerie).",
            "Wound Penalties: -1 (1-7), -3 (8-14), -5 (15-21), Incapacitated "
            "(22-28), Dead (29+).",
            "Greater Powers are Chilling Laugh or Howl, Damaging Effect, and "
            "Decapitate. Its Feast of the Dead recovers 2 Might when it inflicts "
            "a Heavy Wound or greater.",
        ),
    )
    b.creature(
        "The Father of Dread",
        page="p. 28",
        realm="Faerie",
        might=65,
        form="Animal",
        size=10,
        cunning=True,
        place=giza,
        block={
            "characteristics": characteristics(3, 2, -3, -3, 26, 3, 2, -9),
            "virtues_flaws": [
                "Ferocity",
                "Huge",
                ("Immune to {source} (Major)", {"source": "Fire"}),
                ("Sovereign Ward", {"ward": "The Divine"}),
                "Hybrid Form",
                ("Personal Power", {"power": "Extend Glamour"}),
                "Time or Place of Power",
                "Incognizant",
            ],
            "abilities": [
                ("Athletics", 5, "pouncing"),
                ("Awareness", 5, "victims"),
                ("Brawl", 9, "claws"),
                ("Hunt", 5, "people"),
            ],
            "traits": {"Ferocity": 5, "Guardian of the dead": 5},
            "reputations": {"Almost forgotten god (scholars)": 2},
        },
        attacks=[
            b.attack("2 Large Claws", -9, 17, 4, 27),
            b.attack("Bite", -9, 14, 1, 24),
        ],
        soak=8,
        powers=[
            b.power(
                "Chilling Howl",
                4,
                -13,
                "Animal",
                rtd=("Voice", "Sun", "Group"),
                does="Paralyses completely all who hear its hunting roar, like a "
                "tremendous lion's, deep enough to rattle the bones. (Base 5, +2 "
                "Voice, +2 Sun, +2 Group.)",
            ),
            b.power(
                "Spirit Away",
                0,
                0,
                "Vim",
                does="Variable Might, Init n/a. See Realms of Power: Faerie ch. 2: "
                "sweeps mortals into Faerie, more easily as they transgress sacred "
                "or moral bounds. Its lands there look much like Giza at dawn, "
                "where it hunts and eats its victims. It has +10 Might in Faerie.",
            ),
            b.power(
                "Extend Glamour",
                0,
                0,
                "Mentem",
                does="Constant. A God of Dawn: in Faerie it may make it dawn at "
                "will, gaining 10 Might, and uses cascading dawns to strip away "
                "effects that end at dawn: magi must let Parma Magica fail or "
                "spend each round on the ritual. It also tells it where its quarry "
                "is. It must penetrate, but few can resist its Might.",
            ),
        ],
        vis=[BodyVis(13, "", "the skull of a pharaoh built into it")],
        appearance="Once acted by possessing the great statue at Giza: a vast lion "
        "with a man's head in a headdress, 75 feet tall. In Faerie it is less "
        "weathered, and keeps the ceremonial beard the mundane statue has lost.",
        notes=paragraphs(
            "Each great necropolis has a protective spirit of great power that "
            "rarely acts; magi casting in the graveyard might wake one. This is "
            "the mightiest. It is not designed as a player character. Spirit "
            "Away's and Extend Glamour's costs are recorded as 0 here; see each "
            "power.",
            "Combat Attack and Defense exclude the Ferocity bonus. Time of Power "
            "adds 10 Might while the Sun touches the horizon.",
            "Wound Penalties, adjusted for stone and Size: -1 (1-21), -3 (22-32), "
            "-5 (33-43), Incapacitated (44-54), Dead (55+). Its Abilities are "
            "Pretenses.",
        ),
    )
    b.creature(
        "The Mut",
        page="p. 28",
        realm="Magic",
        might=6,
        form="Mentem",
        size=0,
        season="Summer",
        tires=False,
        fatigue_levels=FATIGUE_NONE,
        how_many="Many",
        place=monuments,
        block={
            "characteristics": characteristics(0, 1, 0, 0, 1, 1, 0, 1),
            "virtues_flaws": [
                "Magic Spirit",
                ("Lesser Power", {"power": "Ghost Touch"}),
                ("Cautious with {ability}", {"ability": "Profession"}),
                "Magical Monster",
                ("Greater Power", {"power": "Possession"}),
                ("Lesser Power", {"power": "Cause Mastitis"}),
                ("Lesser Power", {"power": "Eidolon"}),
                ("Lesser Power", {"power": "Dream Manipulation"}),
            ],
            "abilities": [
                ("Area Lore: grave site", 4, "stories about the dead"),
                ("Athletics", 4, "running"),
                ("Awareness", 4, "living things"),
                ("Profession: varies", 6, "varies"),
            ],
            "traits": {"Ghost": 3, "Jealous of the Living": 2},
        },
        attacks=[
            b.attack("Brawl", 1, 5, 6, 3),
            b.attack("Agricultural or craft tool", 2, 8, 6, 6),
        ],
        soak=1,
        powers=[
            b.power(
                "Cause Mastitis",
                2,
                -3,
                "Corpus",
                rtd=("Touch", "Sun", ""),
                does="Stops mothers making milk for their babies. (ReCo 3, the "
                "symptoms of a minor illness, Art & Academe p. 57, +1 Touch, +2 "
                "Sun; Realms of Power: Magic p. 102.)",
            ),
            b.power(
                "Dream Manipulation",
                1,
                1,
                "Mentem",
                does="Enters a victim's dreams, and though it cannot change them "
                "at once, can darken them and add frights. (After the weaker "
                "Envisioning, Realms of Power: The Infernal p. 32.)",
            ),
            b.power(
                "Ghost Touch",
                0,
                0,
                "Terram",
                level=25,
                does="Variable cost, Init Qik - Might spent. Moves objects not "
                "held or fastened: 5 pounds for 1 point, doubled per extra point. "
                "Hurled, it uses Thrown Weapon, damage +5 per point. With a Martial "
                "Ability it may fight through the power, on its own Abilities and "
                "Characteristics; physical attacks must Penetrate. It lasts until "
                "the object is dropped. (Focus power, ReTe25, Realms of Power: "
                "Magic p. 102.)",
            ),
            b.power(
                "Lesser Eidolon",
                3,
                -5,
                "Imaginem",
                level=15,
                does="An immaterial illusory form to deal with mortals, lasting "
                "until no longer needed: a see-through image of the person at "
                "their best, so a man has a wise old face and a twenty-year-old's "
                "belly. (CrIm15: Base 2, +1 Touch, +2 Conc, +2 move at command, "
                "1 intricacy; redesigned from Realms of Power: Magic p. 102.)",
            ),
            b.power(
                "Possession",
                1,
                3,
                "Mentem",
                does="1 or more points. If it penetrates, the mut directly "
                "controls the victim. A supernatural power of the host, spells "
                "included, costs 1 Might per magnitude. An act against the host's "
                "nature means beating her Personality Trait roll with a stress die "
                "+ Might spent; the storyguide may modify the trait (Entrancement, "
                "ArM5 p. 65). Both costs apply if both are true. Under direct "
                "control she has the mut's Magic Resistance but is stopped by "
                "wards that would stop it; acting freely she has neither. (Realms "
                "of Power: Faerie p. 71.)",
            ),
        ],
        vis=[BodyVis(2, "Mentem", "a prized possession")],
        equipment="Clothes and grave goods. The ghost's weapon reappears in its "
        "hand when needed. Some soldier ghosts wear armour.",
        appearance="Ghostly doubles of humans, see-through but coloured.",
        notes=paragraphs(
            "Spirits unable to pass on, for a burial done wrongly or for unfinished "
            "business; akin to shades (Realms of Power: Magic p. 115). Unlike ka "
            "they do not remember who they are and cannot reach the Field of "
            "Reeds, and with no tomb they roam the mundane world, jealous of the "
            "living, harming pregnant women and newborns above all. That focus is "
            "faerie-like, so some are likely faerie impostors; it may also reflect "
            "the worth of children in old Egypt, where a childless man was soon "
            "forgotten, the most final death.",
            "Sorcerers used them against enemies: a victim's hair tied to a dead "
            "man's and both to a dead hawk brought nightmares, possession and "
            "madness, and the hawk, sign of Horus, made it hard to dispel with "
            "Egyptian incantations. The old spell to dismiss one, The Making of an "
            "Akh, forces it to the Magic Realm; oddly for a banishing, in time a "
            "former mut may return to its family as an akh and aid them.",
            "Personality traits vary, but include Ghost +3 and Jealous of the "
            "Living +2 or more. Size 0, but immaterial; Soak +1 when material. "
            "Sta is Tireless. Abilities besides those above: one of Brawl 6 (club), "
            "Great Weapon 6 (large rural implement), or Single Weapon 5 (spear) "
            "with Thrown Weapon 3 (throwing stick, as a stone). Attacks are one "
            "or the other. Ghost Touch's variable cost is recorded as 0.",
            "Wound Penalties: -1 (1-5), -3 (6-10), -5 (11-15), Incapacitated "
            "(16-20), Dead (21+).",
        ),
    )
    b.creature(
        "Ka of a Tomb Robber",
        page="p. 34",
        realm="Magic",
        might=15,
        form="Mentem",
        size=0,
        tires=False,
        fatigue_levels=FATIGUE_NONE,
        place=monuments,
        block={
            "characteristics": characteristics(0, 1, 0, 1, -1, 0, 4, 4),
            "virtues_flaws": [
                "Magic Spirit",
                "Magical Monster",
                vf_great("Dexterity"),
                vf_great("Quickness"),
                *_times("Improved Characteristics", 2),
                "Light Touch",
                "Perfect Balance",
                vf_puissant("Legerdemain"),
                vf_puissant("Stealth"),
                "Avaricious (Major)",
                "Dark Secret",
                ("Ability Block", {"detail": "Illiterate"}),
                "Compulsion (Minor)",
                *_times("Improved Damage", 2),
                "Improved Powers",
                *_times("Lesser Power", 2),
                "Personal Power",
            ],
            "abilities": [
                ("Legerdemain", 5, "picking pockets"),
                ("Stealth", 5, "being quiet"),
            ],
            "traits": {
                "Avaricious": 3,
                "Defend the Tomb": 3,
                "Daring": 2,
                "Sociable": 2,
            },
        },
        attacks=[b.attack("Fist", 4, 7, 7, 5)],
        soak=0,
        powers=[
            b.power(
                "Possess statue",
                0,
                3,
                "Terram",
                level=25,
                does="Takes a statue of itself as a body. (ReTe 25; Personal "
                "Power, 25 levels, -3 Might cost, +2 Init from Improved Powers.)",
            ),
            b.power(
                "Thief after death",
                1,
                0,
                "Terram",
                level=10,
                does="Carries material objects in his hands. (Base 3, +1 Touch, "
                "+1 Conc; Lesser Power, 10 levels, -1 Might cost.)",
            ),
            b.power(
                "Strangler",
                0,
                0,
                "Corpus",
                level=15,
                does="Chokes a victim with his hands, costing a Fatigue level. "
                "(PeCo 15: Base 10, +1 Touch; Lesser Power, 15 levels, -3 Might "
                "cost, +1 Init.)",
            ),
        ],
        vis=[BodyVis(3, "Mentem", "hand")],
        appearance="The ghost of a young tomb robber, killed by the guardians "
        "of the dead.",
        notes=paragraphs(
            "An example reworking the Rogue (ArM5 p. 23), whose Abilities it has; "
            "only the two above are printed here. Damage includes +6 Increased "
            "Damage, entered as Improved Damage.",
            "The tomb's owner shamed him further by carving a tiny soapstone "
            "ushabti and forcing him to animate it. In it: Str -9, Qik +8, Size "
            "-4, Increased Damage x2; Fist Init +8, Attack +7, Defense +11, Damage "
            "-2 (with the +6); Soak +15 (soft stone); Wound Penalties -1 (1), -3 "
            "(2), -5 (3), Incapacitated (4), Dead (5+).",
            "Wound Penalties as a ka: -1 (1-5), -3 (6-10), -5 (11-15), "
            "Incapacitated (16-20), Dead (21+).",
        ),
    )
    b.creature(
        "Animated Statue of a Minor Palace Guard",
        page="p. 34",
        realm="Magic",
        might=10,
        form="Mentem",
        size=0,
        tires=False,
        fatigue_levels=FATIGUE_NONE,
        place=monuments,
        block={
            "characteristics": characteristics(0, 1, -1, -1, 0, 1, 2, 2),
            "virtues_flaws": [
                "Magic Thing",
                "Magical Monster",
                "Warrior",
                "Weakness (Minor)",
                *_times("Improved Initiative", 2),
                *_times("Improved Attack", 2),
                *_times("Improved Damage", 4),
                *_times("Personal Power", 2),
            ],
            "traits": {
                "Defend the Tomb": 3,
                "Loyal": 3,
                "Cheeky": 2,
                "Brave": 1,
            },
        },
        attacks=[
            b.attack("Axe and Large Shield", 1, 17, 14, 12),
            b.attack("Kick", -1, 8, 5, 11),
        ],
        soak=21,
        powers=[
            b.power(
                "Possess statue",
                0,
                0,
                "Terram",
                level=30,
                does="ReTe30; Personal Powers x2 (30 levels, -3 Might cost, +1 Init).",
            ),
        ],
        vis=[BodyVis(2, "Mentem", "axe")],
        equipment="Axe; breastplate (Egyptians did not use full scale armour).",
        appearance="The ghost of an older soldier, in a statue with his face.",
        notes=paragraphs(
            "An example reworking the Grizzled Veteran (ArM5 p. 21), whose "
            "Abilities it has, unsuitable ones such as Order of Hermes Lore "
            "adjusted. The ghost stays in the statue always. His Weakness, "
            "talking back to superiors, is printed with no tier and entered "
            "Minor. In play describe a kopesh, a curved sword, and a large hide "
            "shield. Soak is a hardened bronze statue's.",
            "Wound Penalties: -1 (1-5), -3 (6-10), -5 (11-15), Incapacitated "
            "(16-20), Dead (21+).",
        ),
    )
    b.creature(
        "Sethos",
        page="p. 37",
        realm="Magic",
        might=50,
        form="Mentem",
        size=0,
        confidence=(5, 5),
        tires=False,
        fatigue_levels="Supernaturally Tireless (innate to Aspects)",
        place=reeds,
        block={
            "characteristics": characteristics(5, 5, 3, 4, 2, 1, 2, 2),
            "virtues_flaws": [
                "Magic Human",
                "Daimon",
                ("Transformed {being}", {"being": "Spirit"}),
                "Wealthy",
                "Inspirational",
                "Self-Confident",
                "Well-Traveled",
                *_times(("Focus Power", {"power": "Lord of the Black"}), 2),
                *_times(("Focus Power", {"power": "Lord of the Red"}), 2),
                ("Greater Power", {"power": "Aid of the Gods"}),
                ("Major Virtue", {"virtue": "Way of the Black"}),
                ("Major Virtue", {"virtue": "Not Monstrous"}),
                *_times("Improved Attack", 2),
                *_times("Improved Damage", 2),
                *_times("Improved Initiative", 2),
                *_times(vf_minor("Faerie Sympathy"), 2),
                vf_minor("Gentle Air"),
                *_times(vf_minor("Great Communication"), 2),
                *_times(vf_minor("Great Perception"), 2),
                *_times(vf_minor("Great Intelligence"), 2),
                *_times(vf_minor("Improved Characteristics"), 8),
                vf_minor("Perfect Eye for Antiquities"),
                vf_minor("Puissant Charm"),
                vf_minor("Puissant Leadership"),
                vf_minor("Social Contacts (Coptic priests)"),
                vf_minor("Social Contacts (Criminals)"),
                vf_minor("Tomb Regio Network"),
                vf_minor("Tough"),
                ("Personal Power", {"power": "Immateriality"}),
                ("Personal Power", {"power": "Invisibility"}),
                ("Personal Power", {"power": "Soundless Motion"}),
            ],
            "abilities": [
                ("Dead Language: Ancient Egyptian", 5, "orders"),
                ("Living Language: Arabic", 5, "to common people"),
                ("Area Lore: Egypt", 3, "Delta region"),
                ("Artes Liberales", 3, "hieroglyphs"),
                ("Athletics", 3, "noble sports"),
                ("Awareness", 5, "names"),
                ("Bargain", 3, "criminals"),
                ("Bows", 3, "short bow"),
                ("Brawl", 3, "defensive"),
                ("Carouse", 3, "noblemen"),
                ("Charm", 5, "common people"),
                ("Living Language: Coptic", 5, "to priests"),
                ("Dominion Lore", 3, "Coptic"),
                ("Etiquette", 3, "religious"),
                ("Faerie Lore", 5, "Egyptian deities"),
                ("Folk Ken", 4, "Egyptians"),
                ("Guile", 5, "people who think he is a priest"),
                ("Infernal Lore", 3, "Egyptian"),
                ("Intrigue", 5, "noblemen"),
                ("Leadership", 5, "commoners"),
                ("Legerdemain", 3, "forgery"),
                ("Magic Lore", 5, "Daimons"),
                ("Penetration", 5, "Animal"),
                ("Profession: kingship", 5, "ceremonies"),
                ("Ride", 3, "charioteering"),
                ("Single Weapon", 5, "Mace"),
                ("Stealth", 3, "burglary"),
                ("Swim", 2, "pretending to need to breathe"),
            ],
            "traits": {"Akh": 5, "Dislikes warriors": 3, "Curious": 2},
            "reputations": {"Obscure Early King (Local)": 2},
        },
        attacks=[
            b.attack("Mace and Shield", 9, 12, 11, 16),
            b.attack("Bow", 1, 8, 4, 8),
        ],
        soak=11,
        powers=[
            b.power(
                "Aid of the Gods",
                5,
                -3,
                "Animal",
                rtd=("", "Sun", "Group"),
                does="Creates a swarm of 60,000 mice under his complete control. "
                "(Base 15, +2 Sun, +2 Group, +1 control as a Rego requisite, +2 "
                "mice can turn immaterial to pass barriers, as Muto Mentem "
                "requisites.)",
            ),
            b.power(
                "Immateriality",
                4,
                -2,
                "Corpus",
                rtd=("", "Sun", ""),
                level=40,
                does="Immaterial until sunrise or nightfall. (Base 30, +2 Sun.)",
            ),
            b.power(
                "Invisibility",
                1,
                0,
                "Corpus",
                rtd=("Personal", "Sun", ""),
                level=15,
                does="A personal Veil of Invisibility, ArM5 p. 146. (Base 4, +2 "
                "Sun, +1 moving image, 5 levels spent to reduce cost.)",
            ),
            b.power(
                "Lord of the Black",
                0,
                -8,
                "Aquam",
                does="Variable cost: duplicates non-ritual Creo or Rego spells of "
                "the Magic of the Black (fresh water, rain, fertile earth and "
                "the like), at 1 Might per Hermetic magnitude.",
            ),
            b.power(
                "Lord of the Red",
                0,
                -8,
                "Aquam",
                does="Variable cost: duplicates non-ritual Creo or Rego spells of "
                "the Magic of the Red (barren Terram, parching winds and the "
                "like), at 1 Might per Hermetic magnitude.",
            ),
            b.power(
                "Silent Motion",
                0,
                0,
                "Imaginem",
                level=10,
                does="Constant: he moves without sound. (Base 3, +2 Sun, +1 "
                "constant, 5 levels spent to reduce cost.)",
            ),
        ],
        vis=[
            BodyVis(
                10, "Rego", "a small mouse statuette found implausibly in the brain"
            )
        ],
        equipment="Palace in the Field of Reeds, mace, robes, vast amounts of "
        "money. Sometimes a full suit of heavy armour.",
        appearance="A middle-aged man free of all infirmity, dressed as the "
        "people about him, often as a priest.",
        notes=paragraphs(
            "An early king who took the warrior caste's crop lands. When they "
            "refused to muster against an invader he led peasants and shopkeepers "
            "instead; the night before battle mice poured through the sleeping "
            "enemy camp, gnawing bowstrings, eating provisions and fouling water. "
            "He raised statues of himself holding a mouse, inscribed with a "
            "warning to fear the gods. Herodotus tells his life.",
            "He now travels and studies at whim, knows Pharaonic Egypt is gone, "
            "and keeps its dignity, often posing as a Coptic priest. He opposes "
            "those who despoil monuments other than tombs, but prefers not to "
            "fight directly: subtle, patient, a spy, he raises natural-seeming "
            "obstacles. He could be an ally or a parent.",
            "This block is an Aspect: any change short of death is undone within "
            "a day, and if killed a new one can be made. Originally priest then "
            "king, he has Abilities usually needing Virtues. Wealthy here means "
            "richer than most kings, and no season need go to the business. He "
            "has also appeared as a mouse Aspect, still 50 Might, putting more "
            "Qualities into combat, hiding in Aid of the Gods' swarm as a small, "
            "comic and lethal storm.",
            "Rules notes. Mace totals include +6 Improved Initiative, +4 Improved "
            "Attack and +6 Improved Damage. He keeps the mace hooked invisibly on "
            "his belt. Soak is 8 +3 Tough. Egyptians seldom wear armour, but he "
            "is immune to heat and fatigue and likes annoying warriors. Charm and "
            "Leadership are 5+2. Akhu have bones of iron (Tough). Lord of the "
            "Black and Red have variable costs, recorded as 0. The Black means "
            "the fertile land by the Nile.",
            "Not Monstrous: Magic Humans usually are, but mummification preserves "
            "his looks. Perfect Eye for Antiquities (City and Guild p. 109): he "
            "always knows what an antiquity is, if it is genuine and its worth. "
            "Tomb Regio Network: he can enter the Field of Reeds by the stele in "
            "any tomb and leave by any, and enter by some places sacred to the "
            "Osirian Trinity. Way of the Black is printed with no description.",
            "Wound Penalties: -1 (1-5), -3 (6-10), -5 (11-15), Incapacitated "
            "(16-20), Dispelled (21+).",
        ),
    )


# -- the Copts and the treasures --


def _copts(b: Builder) -> None:
    b.faction(
        "The Coptic Monks and Their Libraries",
        faction="Religious community",
        realm="Divine",
        summary=paragraphs(
            "Copts speak a descendant of the old Egyptian tongue, their priests a "
            "purer liturgical form. Most literate Copts can read Egyptian texts of "
            "the Ptolemies' time, in Greek letters, and scholars can read "
            "hieroglyphs, even in the oldest tombs. They seem to do little with "
            "this, because most scholars are monks.",
            "The monasteries hold libraries of secret old knowledge. The monks can "
            "read the old spells but rarely use them: prayer is simpler, in the end "
            "stronger, and imperils no soul. They do not want to order gods about "
            "or dig for gold. Yet they hold powerful magic items, found when "
            "churches rise on old sites or given by believers; they are faithful "
            "and peaceful, but they have seen pogroms, and keep tricks for defence.",
            "Egyptian magicians wonder what they want. They do not seem to use "
            "magic texts, so why collect them, and if the aim is safety, why not "
            "burn them? Many monasteries have Nilometers, for taxes they say, but "
            "their old religious role makes others suspicious.",
        ),
        offers="Spoken Coptic is easy to learn from the many Copts glad to teach "
        "it, in Mediterranean ports and on pilgrimage in the Holy Land, and some "
        "monks have written grammars for Arabic speakers. To read hieroglyphs one "
        "must find a skilled, probably ancient monk and persuade him to teach.",
        secrets=paragraphs(
            "A few Copts practise Egyptian magic with saints or the Holy Family in "
            "the gods' places; these are Holy Magicians (Realms of Power: The "
            "Divine) (LotN p. 47).",
            "They want to keep the writings of those who commanded spirits from "
            "undeserving hands (p. 56).",
        ),
    )
    b.church(
        "Al-Quisir",
        church="Monastery",
        order="Coptic",
        summary="The most famous Coptic monastery library near Cairo, on the "
        "Maqatam Mountain near Tura.",
    )
    b.faction(
        "Coptic Alchemists",
        faction="Hedge coven",
        summary=paragraphs(
            "Whether the most studious monks or the sultan's personal alchemists "
            "are the world's best is disputed; each side names the other, citing "
            "the thousands of books the rival can reach.",
            "Egyptian alchemy is practical and mechanical, grown from generations "
            "of magical medicine. Hermetic alchemy's goal of immortality makes no "
            "sense to these men: the faithful live for ever anyway, in greater "
            "bliss, so the Great Elixir is all but worthless to the devout.",
        ),
        secrets="Hermetic magi may compare them to the Learned Magicians of "
        "Europe, who have one excellent book of Egyptian formulae. Medicines found "
        "in tombs can be designed as single-use Hermetic items (LotN pp. 47, 49). "
        "The Black calls on Coptic alchemists in its war with the Red (p. 57).",
    )
    b.faction(
        "The Sufis of the Enigma",
        faction="Faith or sect",
        realm="Divine",
        summary="A school of sufis in Egypt devoted to calligraphy and the "
        "beauty of the unread: they meditate on texts they cannot read, and "
        "find enlightenment in the attempt. They also study alchemy, only for "
        "substances that alter mood and body and so ease meditation and the "
        "channelling of the Divine.",
        secrets="They hold the Wisdom from Ignorance Virtue (LotN p. 49; DE p. 116). "
        "The book gives this school no name; the record's name is descriptive.",
    )


def _treasures(b: Builder, monuments: Any) -> None:
    treasures = b.place(
        "The Magical Treasures of the Ancient Egyptians",
        known=REGION,
        inside=monuments,
        summary=paragraphs(
            "So many ruins stand in Egypt, and grave robbing pays so well, that "
            "magic items of every kind turn up. Thousands of small ones are for "
            "sale at any time in the country's markets, to those who know whom to "
            "ask. Temples are so many and so various that a magus of 1220 could "
            "hardly exhaust them.",
            "The ancients knew a force in all things and called it heka, which also "
            "meant a written spell. They found it in rare and strange things: "
            "resin for preserving, gold to hold it in amulets, iron, then scarce, "
            "for harming demons, and deformed things, which is why robbers find "
            "jars of pickled two-tailed lizards, and throw them away.",
            "Most Egyptian religion was not about death. The Osirian hero cult, "
            "which built the great tombs, was an odd and exclusive thing even "
            "then: the oldest akhu claim kin with Osiris before his ascent, and "
            "only later were the richest nobles and merchants let in. Its "
            "artefacts survive best simply because they lay in graves.",
            "The most common magicians were priests of small local spirits, much "
            "like the village witch or blacksmith of Christian Europe: not always "
            "Gifted, and of little power. Theirs is the only ancient Egyptian "
            "magic alive in 1220, renamed and aligned with Islam.",
        ),
        secrets=paragraphs(
            "Heka is what Hermetic magi call vis (LotN p. 50). The tomb chapter "
            "assumes Magic-aligned practitioners; this one has Faerie-aligned "
            "priests served by Magic-aligned artisans. Use either as suits the "
            "story (p. 48). Troupes may let tombs give Guaranteed Insight into "
            "almost anything, or hold that Mercurian magic took in the Egyptian "
            "so fully that little new remains (p. 49). A parallel to nearly every "
            "magical tradition can be found in the ruins, even to troll-blooded "
            "magi, among the servants of old desert spirits (p. 47).",
            "Local priests (p. 54): faerie-aided Murabits (see the Murabitin) may "
            "claim to venerate saints' bones but serve faeries of strong local "
            "stories. Design remnants with Virtues like Faerie Friend, as Faerie "
            "Doctors (Realms of Power: Faerie p. 118), Faerie Wizards in Weal "
            "(p. 129) or Faerie Bargainers in Bonding (p. 132). Their grave goods "
            "suit Mystery Quests; their ghosts may act as mystagogues, fading "
            "once they have saved their priesthood from extinction.",
        ),
    )
    b.place(
        "Books of the Lector Priests",
        known=REGION,
        inside=treasures,
        summary=paragraphs(
            "The lectors, or readers, performed the rites in the sacred books. "
            "Most knew few, for a god could be asked only certain things, at "
            "certain times, by people strictly prepared. Chief lectors were the "
            "librarians, keeping the books of rare and emergency rites; their "
            "title is the old word for any strong magician, and a ghost asked "
            "about magicians will mean them. The pharaoh, high priest of Egypt, "
            "appointed them. Each temple's book holds closely related effects, "
            "some just one.",
            "Rites call for purity: shaving all hair, smoke bathing, natron "
            "mouthwash, gods drawn on the skin, new linen, abstinence; a space "
            "cleansed with incense, drawings or Nile water; things never used "
            "before, or dear reusable ones such as ivory wands and god-masks. "
            "Many spells are said four times. Some speak in code: the heart of a "
            "baboon is oil of lilies, Ethiopian soil is crocodile dung, the semen "
            "of Amun a kind of houseleek.",
        ),
        secrets=paragraphs(
            "See the Lector Priests tradition. Usually Faerie Rite Wizards "
            "(Realms of Power: Faerie ch. 6), with Evocation p. 122, Grant p. 127, "
            "Weal p. 128, Ware p. 128 and Woe p. 130 popular, and always "
            "Ceremony (p. 115) (LotN p. 48).",
            "Reading them (pp. 49-51). A magus usually cannot perform one; a "
            "character with the Faerie Method can make a Hermetic equivalent "
            "(Realms of Power: Faerie p. 121), so Merinita are sought. Ceremony "
            "must be followed exactly, perhaps Com + Leadership against 3 + 1 per "
            "follower. Then Com + Coptic against 3 + 1 per 5 levels, higher for "
            "symbolic language. A botch may misfire or bring a faerie's "
            "persecution.",
            "Why rites fail: most need a powerful Faerie aura, as the god's "
            "presence was assumed; the Silencing of the Oracles voided foretelling; "
            "gods grow old and die; the rubric was left out as known to all; or "
            "no faerie nearby wants the role or notices.",
            "Without Realms of Power: Faerie (p. 51): Range, Target and Duration "
            "are fixed. After preparation and the Com + Coptic roll, Casting total "
            "is Sta + closest Form + closest Technique + Aura + stress die, less "
            "spell level: 0 or more, cast, -1 Fatigue; -1 to -10, cast, -2; -11 to "
            "-20, cast, -3; -21 to -30, cast, -4 and a Warping point; -31 or "
            "less, not cast, -5, Warping equal to magnitude, and Twilight check "
            "if over 2. A book is a set of scrolls, one effect each, treated as "
            "casting tablets (Covenants).",
            "Apparently unGifted: Egyptian accounts show no social effect of the "
            "Gift in lectors (p. 50); see the story of that name.",
            "Those who threatened the gods (pp. 53-55): lectors, toward gods they "
            "did not serve, and rogues used a harsher Enchantment Rite, threatening "
            "to destroy the faerie and the world, usually with a faerie ally and a "
            "gate to Arcadia for escape. One such threat promises to turn the world "
            "over and drag up the afterlife: really a bargain offered to a second "
            "god, whose presence with the first weakens the world, touches Duat "
            "and allows Spiriting Away; Hermetic magi think the magician's unspoken "
            "wishes settle it. The Sun is said to have stood still for three days, "
            "beyond any but the Divine, so faeries faked or planted the memory. "
            "Their writings are scripts that Enchant; threat scripts that add a "
            "bonus to one Rite's casting total; and Initiation texts for Special "
            "Circumstances, Puissant Enchantment or Magical Focus.",
        ),
    )
    b.place(
        "Transitory Magic Items",
        known=REGION,
        inside=treasures,
        summary=paragraphs(
            "Faerie-aligned magicians made things for a single use, not truly "
            "enchanted, often for one named user. Most temporary amulets are small "
            "painted linen bags of magic ingredients, medicinal or protecting "
            "against spirits, for childbirth or for fortune in war; skilled robbers "
            "can judge them by contents and writing. Many hold unclean things to "
            "scare spirits: preserved dog, dung, menstrual blood. Underworld "
            "demons live backward, mouths and anuses reversed; honey is bitter to "
            "them, and garlic drives them off by the sound of its name and the "
            "look of its cloves.",
            "Popular amulets guarded against disease from the dead, demons or "
            "gods; spells of demons posing as foreign sorcerers; quarrying "
            "accidents; drowning and boat accidents; crocodiles; and death in "
            "battle.",
            "Seals hold a spell until broken, touched, moved or lit. Some wizards "
            "carried ivory staves ending in hands, to touch things easily. "
            "Temporary potions were water or beer poured over a statue holding a "
            "faerie, above all the cippuses of Horus, or over words cut in a bowl.",
            "The priests also trapped spirits in boxes, generally Apep's kin, who "
            "are said to get out, or the sun could not be reborn. Today's Muslim "
            "peasants dig up the boxes, and nearby faeries take the part of "
            "trapped djinn or efreets.",
            "Some magicians made things from models. A magician-prince sailed up "
            "the Nile with a wax boat and crew; another left a wax crocodile with "
            "his steward, which dragged his wife's lover from a lake, and dragged "
            "him back from the afterlife for the pharaoh's questions, and away "
            "again.",
        ),
        secrets=paragraphs(
            "Temporary amulets (LotN p. 51) are objects under a spell of the Until "
            "Duration, available only to Faerie Magicians, lasting until worn and "
            "discarded. Unlike modern ones they outlive their maker, perhaps being "
            "made by faeries, or mocked up just before their finders come.",
            "Seals (p. 52) work much like Watching Wards. The ivory hands were "
            "talismans in some cults, a way to extend Touch in others, and in "
            "others a symbolic hand for the god.",
            "Statues and potions (pp. 51-52): Merinita argue the statue is not "
            "magic. Water on a cippus is an open offer: a faerie that makes it "
            "medicine feeds on the family's fear and worship. If none takes it the "
            "sufferer gets water, and his death is blamed on hidden sin. Dying "
            "stories may be rekindled by dreams or a talking statue. Some bowls "
            "still work if faeries know the deal; others are only ceremonial "
            "casting at Touch and need a Gifted user.",
            "Models (p. 54): grave goods still work when found: a faerie enters "
            "the model and aids the user, gaining vitality. With Realms of Power: "
            "Faerie, a faerie of the large form with a shapeshifting power; with "
            "core rules, an item with a shapeshifting effect.",
            "Faeries in boxes (p. 55): they are no longer inside. Characters who "
            "know the old tales may tempt a faerie back into the role of Apep's "
            "servant. Use the animal-headed demons, or any dragon's statistics.",
            "Unusual amulets (p. 54). Ib Scarab: made to let the dead lie to the "
            "gods at judgement, it replaces the heart, so works at Personal Range; "
            "lost, it is an Arcane Connection to its owner. Seals with royal names: "
            "a dead pharaoh's name has a little Magic Resistance, perhaps 5, so "
            "wearers hope curses that catch it are deflected. It protects only "
            "itself, so a curse that would drown a man through his boat's "
            "capsizing fails, while a scorpion's sting does not. Folk magicians "
            "know this. The royal ring is a shen, a rope laid in a protective "
            "circle; cartouche is a later word and unknown in Mythic Africa.",
        ),
    )
    b.place(
        "Animated Statues",
        known=REGION,
        inside=treasures,
        summary=paragraphs(
            "Classical writers tell of Egypt's strange art of bringing temple "
            "statues to life. Two events destroyed most of them. The Romans, "
            "invading in 30 BC, knew they could banish gods by smashing images. "
            "Then when Christ fled to Egypt in 2 AD some writings say the earth "
            "shook and all the statues fell, though the Father of Dread plainly "
            "survived; perhaps only those then inhabited fell.",
            "Others wore out with moving, for they do not heal; and healers "
            "could pass a person's injuries to a holy statue, moving the god to a "
            "new one when it was too hurt to hold him. When the art was lost, "
            "many old statues were spent that way.",
            "Some priests consecrated statues for themselves, and in death took "
            "prayers to the gods in return for offerings. Guards and spies might "
            "be given statues likewise.",
        ),
        secrets=paragraphs(
            "To secular magi, it means persuading a faerie to enter a statue and "
            "stay, feeding on those it touches and their worship; the statue is "
            "only matter it wears (LotN p. 52). Player characters can banish a "
            "faerie god by defacing its image. Ruined statues that held faeries "
            "often contain vis (p. 54).",
            "Statue Consecration Mystery (pp. 52-53): lost to humans, but findable "
            "in an intact temple library, or from faeries. Great temples followed "
            "written steps; small sects were guided by a faerie. Such statues may "
            "attract demons seeking to replace the faerie, or Divine wrath. A few "
            "chief lectors made new rituals: a convincing narrative on which a "
            "faerie may feed, by Com + Folk Ken against 18. The texts are "
            "choreographies that aid the roll, as does a Faerie aura or rites by "
            "other priests.",
            "Tongue magic (p. 52), in rare texts: The Drawing of Maat: a skilled "
            "portrait of the Goddess of Truth on the tongue stops the character "
            "lying or saying false words, and any weaker god must forgive "
            "mispronunciation. Whoever discovers it can make a tiny possessing "
            "faerie that corrects a magus's words, reducing botches, which may "
            "alter his personality.",
            "Saliva and breath: spells work more easily on those spat or breathed "
            "on. Treat as Personal range but without circumventing Magic "
            "Resistance. People shielded themselves accordingly, and some faeries "
            "still use shared fluid or breath as Arcane Connections. It would ease "
            "some Spontaneous spells. Nobody bottled them to delay a spell.",
        ),
    )
    b.place(
        "Magical Craftwork",
        known=REGION,
        inside=treasures,
        summary=paragraphs(
            "A caste of crafters served the temple priests, making amulets, which "
            "protect the wearer; talismans, which ease his life; and curses, which "
            "hurt another. Greek and Roman writers noted their skill, and it was a "
            "great export in Ptolemaic times. Robbers often recover their work, "
            "sold through the guild or the black market, and their writings can be "
            "read by those who know Coptic.",
            "Colours matter. Black is the colour of magic, and green is widely "
            "used. Blue invokes gods. Yellow, orange and some reds are one colour "
            "to an Egyptian magician, and best for fire. Red is for evil: the "
            "names of Apep and Seth are always written in it, and spells to "
            "summon Seth's servants. Red stone amulets ward against them, and "
            "curses too are red.",
            "The commonest amulet shape is a precious-metal copy of a linen bag. "
            "Others show a thing whose virtue the wearer borrows. Most bear the "
            "Wedjat eye, and many name Thoth, the Lord of Amulets.",
            "The dead were thought to be like birds in some way, so people went to "
            "their graves with bird-snaring weapons against demons on the road: "
            "most often a throwing stick, and sometimes nets.",
        ),
        secrets=paragraphs(
            "One Egyptian craft book, circulated in Europe, created the Learned "
            "Magician tradition (Hedge Magic: Revised Edition). Its protection, "
            "assistance and harm Techniques and Luck, Magic and Health Forms "
            "simulate much Egyptian work, but priesthoods had other Arts. Egyptian "
            "magic had no fixed Ranges, Targets and Durations and no Difficult "
            "Arts, relics of that single book. Spirit aid from the four realms "
            "came more easily. Assume very high casting and laboratory totals. "
            "Without that book, design amulets as Hermetic items (LotN p. 55).",
            "Grave weapons: the throwing stick has an effect like Faerie's Eternal "
            "Oblivion; nets have ReVi effects that hold demons, so victims may "
            "flee or stab them.",
        ),
    )
    b.place(
        "Contained Spirits",
        known=REGION,
        inside=treasures,
        summary="The most lasting relics of those who commanded spirits, wizards "
        "scarcer and stronger than the Keepers of the Books, who used their "
        "standing with mighty faeries to bully lesser spirits. They left "
        "creatures shut in mystic containers, able to speak with whoever holds "
        "them. A bargain with one binds, but only as to the words. Most are found "
        "in tombs, though in old times most were buried in sacred precincts, for "
        "the gods to watch.",
        secrets=paragraphs(
            "Their magic resembles spirit masters', and they are an ancestral "
            "tradition of the sihr (The Cradle and the Crescent; a Hermetic "
            "variant in Houses of Hermes: Societates). Their writings, using the "
            "Magic Realm, suit Hermetic adaptation best: Insight and Mystery "
            "Initiations, prized by sahirs too (LotN p. 56).",
            "A grateful spirit may forgo harm, and can be made a permanent ally by "
            "favours like Ordeals (The Mysteries), without Occult Lore. Most "
            "resent it. For a faerie, some magi advise instant, unconditional "
            "freedom: a gift many must repay with one worth as much, though the "
            "gift may cause trouble. A magical creature need give nothing, and "
            "may attack.",
            "True names: Egyptians were casual with them. Tombs list the ka names "
            "of owner and servants, so that a dead man need not call his "
            "table-steward like a lost dog; a true name is also called a ka name "
            "or ren. Shabtis answered the owner's name for him, avoiding labour "
            "and turning aside curses laid through it.",
        ),
    )
    b.place(
        "The Book of Thoth",
        known=REGION,
        status="Rumoured",
        inside=treasures,
        summary="All authorities agree the mightiest magicians of Egyptian "
        "folklore are the few who read the Book of Thoth, which holds every "
        "spell of the first great magician.",
        secrets="Any character who finds it may read it, and can then cast almost "
        "any Hermetic spell's equivalent without effort. Within one day he dies "
        "or fades into Twilight; he cannot stay. The Book is then hidden again by "
        "forces reaching from deep in the Magic Realm (LotN p. 56).",
    )


# -- the story seeds --


def _seeds(b: Builder) -> None:
    seed = _seed_maker(b)
    seed(
        "The Treasure of Qarun",
        "Young seekers chase Qarun's lost treasure house, and the keys' place is "
        "written somewhere in the guild's library.",
        "See the place for what is printed (LotN p. 25).",
        at="The Treasure House of Qarun",
    )
    seed(
        "The Ramaseum",
        "Colossal images of Rameses II may be statues that his ghost, for all "
        "their size, can animate.",
        "See the place; other proud pharaohs may do likewise (LotN p. 31).",
        at="The Ramaseum",
    )
    seed(
        "Following the Dead",
        "Ghosts ride between the Nile bank and a hidden valley near Alexandria.",
        "Second Sight may let characters follow them home; see the place (LotN p. 31).",
        at="The Secret Valley near Alexandria",
    )
    seed(
        "The Search for Imhotep's Tomb",
        "Hermetic wizards want this tomb, arguably the first of the Egyptian "
        "kind, to end the dispute over ancient and modern magic.",
        "See the place (LotN pp. 37-39).",
        at="The Tomb of Imhotep",
    )
    seed(
        "The Search for Antonius's Tomb",
        "Hermetic wizards want this tomb, arguably the last of the Egyptian "
        "kind, for Cleopatra's Book and the lost libraries.",
        "See the place, and Cleopatra (LotN pp. 37-40).",
        at="The Tomb of Marcus Antonius",
    )
    seed(
        "Conman",
        "A rich man begs the covenant's help. A poor acquaintance showed him gold "
        "amulets from a find, took much money for supplies and labourers against "
        "half the treasure, and vanished.",
        "He is too embarrassed to go to the authorities. Having social standing, "
        "he might become an ally, pawn or front man (LotN p. 25).",
    )
    seed(
        "The Destructive Jest",
        "A forged old document says a treasure lies under the covenant. Gangs "
        "creep in to dig the cellars, neighbours tunnel, mobs storm the gates, and "
        "passers-by strike the walls with picks, hoping for a hollow.",
        "An enemy forged it. The trick is old and famous among the ruling class, "
        "so its author is hard to trace; the characters may hunt the forger "
        "(LotN p. 25).",
    )
    seed(
        "Government Agent",
        "A government clerk must attend any digging for treasure. One who has "
        "angered a nobleman is sent with the characters to a tomb known to be "
        "deadly.",
        "He is terrified and unskilled; they must keep him alive (LotN p. 25).",
    )
    seed(
        "Monastery or Mosque",
        "An old scroll gives the place of a temple listed nowhere else, and so "
        "likely undisturbed; but a monastery or mosque has been built over it.",
        "Either its keepers welcome the characters, wanting the temple's "
        "troublesome beings destroyed; or they ban them, and the characters must "
        "sneak in, tunnel from nearby, or discredit the keeper for a more "
        "pliable one (LotN p. 25).",
    )
    seed(
        "Naqeeb Al-Matalibeen",
        "Famous adventurers are useful to any candidate for chairman of the "
        "Seekers' Guild. Elections are usually civil, but sometimes rivals thin "
        "the field by assassination, with strange poisons, old magic items and "
        "death-traps.",
        "A player character who wins commands all the guild's resources, if he "
        "can keep the emir ignorant. A covenant secretly ruling the guild is a "
        "saga seed (LotN p. 25).",
    )
    seed(
        "Roman Notes",
        "Many Egyptians believe the Romans hid treasure as they withdrew, noted "
        "the caches, and took Coptic, Greek and Chaldean treasure books to the "
        "cathedral of Constantinople. Crusaders sacked it in 1204, and most Arabs "
        "who know this think the Franks now hold the notes.",
        "Common folk might aid the new owners for a share; officials want to "
        "steal the books for the realm and for the thief's own safety. Characters "
        "who make gold by magic may be taken for the keepers, winning peasants and "
        "merchants but offending nobles (LotN p. 25).",
    )
    seed(
        "Medallion Removal",
        "Many graveyard statues wear medallions showing a decapitator among "
        "bound, beheaded victims, and the same design seals tomb doors.",
        "Without these seals the decapitators hardly attack; near them, night is "
        "far deadlier. A robber may come by day, when they are less active, to "
        "remove or deface them unseen by the human watchers (LotN p. 28).",
    )
    seed(
        "The Mut for the Archmage",
        "An archmage who will not leave his concerns in Italy offers to pay anyone "
        "who can capture a mut.",
        "He may lend a mirror that captures ghosts to those who cannot make such "
        "a spell or item. He thinks the Faerie and Magic realms had not yet "
        "parted when the mut were made. How will they know a mut from a recent "
        "ghost or faerie impostor? (LotN p. 29.)",
    )
    seed(
        "The Colour of Ghosts",
        "Necromancers may notice the mut are never black like the ghosts of "
        "Greek and Roman sources, nor white like those of Mythic Europe.",
        "House Criamon says the shift came when the Axis Magica moved to the Cave "
        "of Twisting Shadows, and notes the ghosts older than Criamon there are "
        "all black. If so, what cataclysm drained the colour from the Classical "
        "world's ghosts? An ancient sorcerer's mut may know (LotN p. 29).",
    )
    seed(
        "Apparently UnGifted Magicians",
        "The mightiest Faerie Wizards are always Gifted, yet Egyptian accounts "
        "show no social effect of the Gift among lectors, only among followers "
        "of dark gods.",
        paragraphs(
            "Possible reasons (LotN p. 50). Faeries Stripped of Volition: the "
            "Egyptians may have made their gods machines, so a priest was anyone "
            "in the right robe; some may still be stuck in statues. Engineered "
            "Emotions: the right attention in a heightened state might win a "
            "mystical effect; such ecstatic cults were known, and forbidden "
            "darker rites called up things beyond Duat, dark faeries or demons, "
            "for anyone who repeats them.",
            "A Source for the Gentle Gift: a Mystery Initiation may have given it "
            "to pharaonic priests; the ghosts of priests or the site could allow "
            "self-Initiation, and Jerbiton and Mercere might back it. If it "
            "spreads, offer a new Virtue to those who already took it. A Caste of "
            "Servants: true wizards may have cast through mortal proxies, whose "
            "symbols of office allow casting at a distance. Mystery Initiations: "
            "priests may have earned powers by Ordeals, known to faeries, the "
            "dead or old inscriptions.",
        ),
    )
    arc = b.threat(
        "The Coptic Saga Arc",
        summary="The monks gather magic texts and terrible weapons and keep "
        "Nilometers, and nobody knows why.",
        secrets="In this arc the Copts are allies of the Black, using their powers "
        "and items against servants of the Red (LotN p. 49).",
        antagonist="Servants of the Red",
        stages=[
            b.stage(
                "Serving the Black",
                at=1,
                clues="Monks give quests, rest under the Dominion, healing or "
                "training to characters who aid the Black.",
            ),
            b.stage(
                "The Relics of Saint Simon",
                at=2,
                clues="The characters carry the relics of Saint Simon the "
                "Shoemaker, famed for miraculously moving a mountain, to the Red's "
                "stronghold, a mountain in the heart of the Sahara.",
                stopped="They move the Red's home to the depths of the sea, "
                "swinging the war decisively toward the Black.",
            ),
        ],
    )
    dormant(arc)


def _seed_maker(b: Builder) -> Any:
    """A maker of one-line story seeds: dormant threats with no stages."""

    def seed(name: str, summary: str, secrets: str, at: str = "") -> None:
        place = next((n for n in b.saga.neighbours if n.name == at), None)
        dormant(b.threat(name, summary=summary, secrets=secrets, place=place))

    return seed
