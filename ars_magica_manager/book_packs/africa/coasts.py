"""Geography of North Africa: Coasts (BS&S pp. 40-65), in paraphrase.

The Maghreb and its bands, the old Roman provinces, the Atlantic coast and
Mogador, Pithecousa, the Rif, the Tell and its cities, the islands, Cyrenaica,
the Grand Plateau and the Atlas, with their books and vis in words on the place
or person, the printed creatures, and each story seed as a dormant threat.

The Marinids and the Almohad Caliphate as peoples belong to the book's first
chapter; here they appear as the Rif, the Almohad governors and the seeds. The
thieves' Virtues of pp. 52-53 are the catalog's and are cited, not added.
"""

from __future__ import annotations

from typing import Any

from ...models import BodyVis, Neighbour
from ..builder import (
    Builder,
    characteristics,
    dormant,
    paragraphs,
    vf_minor,
    vf_puissant,
)

REGION = "In the region"
FATIGUE = "OK, 0, -1, -3, -5, Unconscious"
BEAST_FATIGUE = "OK, 0/0, -1/-1, -3, -5, Unconscious"
ALMOHADS = "the Almohad Caliph"
MINOR_WEAKNESS = "Weakness (Minor)"


def _place(b: Builder, name: str, **kw: Any) -> Neighbour:
    """A place known in the region, this pack having no Tribunal."""
    kw.setdefault("known", REGION)
    return b.place(name, **kw)


def _seed(
    b: Builder,
    name: str,
    summary: str,
    place: Neighbour,
    *,
    secrets: str = "",
    antagonist: str = "",
    stages: list[dict[str, Any]] | None = None,
) -> Neighbour:
    """A story seed: a threat that waits until the storyguide begins it."""
    return dormant(
        b.threat(
            name,
            summary=summary,
            secrets=secrets,
            antagonist=antagonist,
            place=place,
            stages=stages,
        )
    )


def build(b: Builder) -> None:
    maghreb = _maghreb(b)
    _roman_provinces(b, maghreb)
    atlantic = _atlantic(b, maghreb)
    pithecousa = _pithecousa(b)
    rif = _rif(b, maghreb)
    caliph = _almohads(b)
    tell, cities = _tell(b, maghreb, caliph)
    _tell_towns(b, tell, cities, caliph)
    islands = _islands(b)
    cyrenaica = _cyrenaica(b)
    atlas = _plateau_and_atlas(b, maghreb, caliph)
    _muqadam(b, maghreb)
    _azru(b, atlas)
    _imghrawn(b, maghreb)
    _maghreb_stories(b, maghreb, atlantic, rif, cities)
    _monkey_stories(b, pithecousa)
    _empire_stories(b, cities)
    _cyrenaica_stories(b, cyrenaica, islands, maghreb, atlas)


# -- the land as a whole --


def _maghreb(b: Builder) -> Neighbour:
    return _place(
        b,
        "The Maghreb",
        summary=paragraphs(
            "North Africa lies in four bands, each with its own way of "
            "travelling. Along the shore ships are quickest: the Atlantic "
            "cities of Mauritania to the west, old Cyrenaica on the "
            "Mediterranean to the east. The great cities stand in the fertile "
            "Tell, the country of carts. South of it the High Plateau climbs "
            "to the Atlas, the country of horses, and beyond lies the Great "
            "Desert and its camels.",
            "The sea is the swiftest and the safest road, so much so that many "
            "Christian ports are nearer by ship than other African cities are "
            "by land. Open piracy is rare, since the rulers of the southern "
            "Iberian shore keep a strong fleet to protect the sea lanes; what "
            "piracy there is hides behind merchant houses and marginal men.",
            "Punic colonies came first, on rocky headlands above deep "
            "harbours; Rome broke Carthage in three wars and took them over, "
            "settling its veterans along the coast. Vandals, Belisarius and "
            "the Arabs followed, and ruins now lie from Sala Colonia on the "
            "Atlantic to Cyrenaica. Two Roman roads begin at Tangier: the "
            "Northern Road runs by the mountains to Carthage and along the "
            "shore to Alexandria, with branches to every villa and fort; the "
            "Western Road runs south past Ad Mercuri and the ruins of Augustus "
            "Zilil, then forks for Rabat and for Walili. Looters want dressed "
            "stone, not roads, so the roads survive.",
            "The Tarikh Ifriqiyya wal-Maghrib of Ibrahim ar-Raqiq, an 11th "
            "century Zirid courtier, is the respected history, kept in private "
            "libraries of merchants and nobles here and in al-Andalus: in "
            "Arabic, a summa on Area Lore: Maghreb (Level 4, Quality 10) with a "
            "tractatus on Area Lore: Great Desert (Quality 10). It reports the "
            "Fatimid caliph Isma'il al-Mansur's visit to the jedars of Jabal "
            "Lakhdar, and gives the true places of the thirteen great Berber "
            "tombs in the hills south of Tahert, though its interpreter's "
            "reading of their inscriptions is wrong (p. 42).",
        ),
        secrets=(
            "A large pack of bouda has come up from the south to strip the "
            "ruins (p. 42)."
        ),
    )


def _roman_provinces(b: Builder, maghreb: Neighbour) -> None:
    tingitana = _place(
        b,
        "Mauretania Tingitana",
        inside=maghreb,
        summary=(
            "The old Roman province of the far west. Many of its sites still "
            "have people in them, as Ceuta (the Roman military town of Septa) "
            "and Mlila on the coast, where the old buildings have mostly gone "
            "into new walls. Tangier and Walili are the largest survivors."
        ),
    )
    for name, text in (
        (
            "Lixus",
            "A Punic and Roman ruin, abandoned, its stone only partly robbed by "
            "the locals over the centuries and so still substantial.",
        ),
        (
            "Iulia Valentia Banasa",
            "An abandoned Roman town, partly scavenged, its ruins still substantial.",
        ),
    ):
        _place(b, name, inside=tingitana, summary=text, ruined=True, aura=0)
    for name, text in (
        (
            "Ceuta",
            "A coastal city, once the Roman military town of Septa, its old "
            "stone recycled into later building.",
        ),
        ("Mlila", "A coastal city still lived in, on a Punic and Roman site."),
    ):
        b.town(name, summary=text, place=tingitana)
    _place(
        b,
        "Mauretania Caesariensis",
        inside=maghreb,
        summary=(
            "The temperate hills and valleys later called the Tell, thick with "
            "Roman colonies: some eighteen follow the two forks of the "
            "Northern Road. Sharshal, Saldae, Tlemcen, Algiers, Djemila and "
            "Tifesh are among them."
        ),
    )
    _place(
        b,
        "Numidia",
        inside=maghreb,
        summary=(
            "The most thickly colonised land of the Phoenicians and Romans, "
            "mostly seized after Carthage fell and the rest annexed when its "
            "Berber client king died and civil war broke out. It covers the "
            "eastern Tell and Tunisia: Carthage, Constantine, Soussa, Bouna, "
            "Tbessa and the ruins of Lambaesis and Tamagudi."
        ),
    )


# -- the western coast --


def _atlantic(b: Builder, maghreb: Neighbour) -> dict[str, Neighbour]:
    coast = _place(
        b,
        "The Western Coast",
        inside=maghreb,
        summary=(
            "A temperate Atlantic shore of fertile plains and hills, dotted "
            "with cities from Anfa and Asfi to the twins Rabat and Sale, now "
            "and then scoured by biting sand-laden winds from the dunes to the "
            "east."
        ),
    )
    anfa = b.town(
        "Anfa",
        place=coast,
        ruler=ALMOHADS,
        summary=paragraphs(
            "A walled city with a deep harbour, set in green farmland under the "
            "tall minaret of its great mosque. A Carthaginian colony and then a "
            "Roman town, it is mostly Berber. From the seventh century to 1068 "
            "it refused the Caliphate as the Kingdom of Anfa, until the "
            "Almoravids besieged it and took it.",
            "Through all that time it has sheltered pirates who raid the "
            "Straits and the Mediterranean, yet it is a true port too, selling "
            "Saharan goods, grain and cloth to Seville, Genoa and other "
            "European cities. Foreigners find it cosmopolitan and tolerant, if "
            "not warm: some call it the secret door into the Maghreb, and the "
            "merchants who use it guard the secret.",
        ),
    )
    asfi = b.town(
        "Asfi",
        place=coast,
        ruler=ALMOHADS,
        summary=paragraphs(
            "An old Punic colony famed for fine pottery and rich fishing, and a "
            "trusted partner of Marrakesh. Its deep harbour is busy with "
            "trawlers and with merchantmen bringing Iberian luxuries and "
            "taking away exotic goods from beyond the Great Desert. The Sufi "
            "Abu Mohammed Salih keeps his ribat here.",
            "The town takes its name, it says, from early 11th century sailors "
            "of al-Andalus who strayed onto the Hesperides and took souvenirs; "
            "the islanders blindfolded them and set them adrift on a storm, "
            "cursed never to sail again from their next port. When they learned "
            "at Asfi how far they were from home, one cried out his regret, 'Wa "
            "asafi'. Al-Idrisi repeats the tale. Descendants of those sailors "
            "still own the relics and their accounts of the voyage, priceless "
            "to anyone seeking the way there.",
        ),
    )
    b.magus(
        "Abu Mohammed Salih (Al-Mighri)",
        covenant=None,
        house="",
        age=67,
        type="companion",
        traditions=["trad_sufis"],
        summary=(
            "A Sufi mystic of 67, beloved of Asfi's elders, with a ribat in the "
            "town and the beginnings of the Magiriyyun order. If history holds "
            "he has 14 years to live, teaching ascetics and writing the Bidayat "
            "al Mourid, on Tassawuf and on Sufi saints such as his teacher Abu "
            "Madyan."
        ),
    )
    _place(
        b,
        "Island of Mogador",
        inside=coast,
        aura=4,
        summary=paragraphs(
            "An uninhabited island, shunned for tales of a bloodthirsty "
            "monster. The Periplus of Hanno names it as the home of a sea snail "
            "whose crushed shell gives the rare dye of the purple stripe on "
            "senators' togas. Harvesters cross from Essaouira, and guard the "
            "foul-smelling secret of the dye.",
        ),
        secrets=(
            "A ruined cellar door in an overgrown Roman villa is the way into "
            "the regio."
        ),
        levels=[
            b.level(
                "The Villa of the Dye",
                4,
                enter="Through the ruined cellar door of the crumbling villa.",
                notes=(
                    "The villa as it stood at the height of the Empire, peopled "
                    "by descendants of the craftsmen and overseers who made the "
                    "dye for the Emperor. The book gives the regio no aura of "
                    "its own; the 4 is the island's."
                ),
            )
        ],
    )
    b.town(
        "Essaouira",
        place=coast,
        summary=(
            "A town across the bay from Mogador, home of the people who "
            "harvest the island's shells and keep the secret of the dye."
        ),
    )
    rabat = b.town(
        "Rabat",
        place=coast,
        ruler=ALMOHADS,
        summary=paragraphs(
            "The town on the south side of the mouth of the Bou Regreg, grown "
            "from the Almohads' fortress of Rabatu l-Fath, the Stronghold of "
            "Victory, their staging point for Iberia. Caliph al-Mansur made it "
            "his capital in 1190, finished its great walls and built widely "
            "until his death in 1199. His heir al-Nasir turned to the "
            "Reconquista and died in 1213, and the absent caliph Yusuf "
            "al-Mustansir leaves the region to a bureaucrat whose eyes are on "
            "Sale.",
            "The Kasbah, an enormous palace-fortress with its own mosque at "
            "the river mouth, has stood empty but for a few squatters since "
            "1199, and the aura of its mosque has faded.",
        ),
    )
    _place(
        b,
        "The Hassan Tower",
        inside=coast,
        realm="Divine",
        aura=4,
        summary=(
            "Al-Mansur's unfinished mosque at Rabat, meant to be the world's "
            "largest and to hold 20,000. Work stopped at his death. The tower "
            "stands 50 paces high, with ramps inside wide enough for a rider, "
            "among a forest of 200 columns under a cedar roof, and the locals "
            "pray here all the same."
        ),
    )
    _place(
        b,
        "Chellah",
        inside=coast,
        summary=(
            "A walled royal necropolis near Rabat, made by al-Mansur from an "
            "abandoned Phoenician town that had become the Roman Sala Colonia. "
            "Few people live near, and its walls keep out the sound of prayer. "
            "Rome sent its searchers for the Hesperides out from here."
        ),
        secrets=(
            "Little Divine aura troubles the place. Those who speak Aramaic may "
            "talk to Punic ghosts as if they had Dead Language: Punic at their "
            "score less 3 (below zero, not at all). Defixiones may lie in the "
            "abandoned Roman quarter."
        ),
    )
    sale = b.town(
        "Sale",
        place=coast,
        ruler=ALMOHADS,
        summary=(
            "Rabat's partner on the northern shore, walled and grown up over "
            "the last century with Rabat's rise. Rowboats ply the river at all "
            "hours, and a canal lets some boats sail straight into the Beb "
            "Mrisa souk. The region's administrator works from here."
        ),
    )
    return {
        "coast": coast,
        "anfa": anfa,
        "asfi": asfi,
        "rabat": rabat,
        "sale": sale,
    }


# -- Pithecousa --


def _pithecousa(b: Builder) -> Neighbour:
    island = _place(
        b,
        "Pithecousa, the Island of Monkeys",
        status="Rumoured",
        summary=paragraphs(
            "A legendary land of monkeys off the African coast, not to be "
            "confused with Ischia near Naples. Some place it among the "
            "Balearics or beside Gibraltar, some through the Pillars in the "
            "Atlantic, some in the Nile Delta. All of them may be right. The "
            "way is through unexpected patches of fog at sea.",
        ),
        secrets=paragraphs(
            "It lies in a regio with several entrances, all at sea in fog. "
            "Seeing through the boundary takes Ease Factor 15 (ArM5 p. 189); at "
            "certain times of year particular headings lead straight through "
            "without any special ability.",
            "The first enchantment, Penetration 0, turns every human and any "
            "other creature affected by Corpus who does not resist into a "
            "mundane monkey suited to its nature: warriors hamadryades, the "
            "clever callithrices, the agile cercopitheci. Intelligence, Virtues, "
            "Flaws and Abilities remain; clothes and gear do not change. A "
            "monkey character can talk with monkeys, and understand but not "
            "speak human tongues, so a magus casts only with quiet words (ArM5 "
            "p. 83). It lasts while on the island and causes Warping as a "
            "powerful mystical effect, and Flaws so gained are simian. Dispelling "
            "it is as a level 55 enchantment (about MuCo base 10, +1 Touch, +4 "
            "Until, +4 Boundary); a Bjornaer's Heartbeast Ability also ends it.",
            "The second, Penetration 50, keeps out anything in human shape: one "
            "it overcomes cannot leave the beach landward or affect anything "
            "beyond it, and is driven to the nearest beach if it takes human "
            "shape inland, even partly once the shape is recognisable. It is as "
            "a level 85 enchantment (about ReCo base 15, +1 Touch, +4 Until, +4 "
            "Boundary, +25 for Penetration). Magi who want to explore must "
            "probably suppress their Magic Resistance and accept the change. "
            "Both effects come from the island, by no known magic; the "
            "guidelines are only for investigating and dispelling them.",
        ),
        levels=[
            b.level(
                "The Island",
                5,
                see="A cone of an island in the fog, its slopes lush.",
                enter="Land on the beaches once the island is seen; EF 15.",
                notes=paragraphs(
                    "One steep mountain, five rivers cut deep ravines from "
                    "plentiful rain, thick forest of strange flowers and fruit, "
                    "bright birds, huge insects, lizards, frogs and fish. Hoofed "
                    "and clawed beasts other than monkeys are tiny: goats, lions "
                    "the size of house cats, elephants no bigger than pigs. None "
                    "threatens the monkeys. There are no snakes, the monkeys' old "
                    "enemies, hunted out long ago; any brought here meet fear "
                    "and violence.",
                    "Court lies in a bowl of date palms round a rock throne. "
                    "Lost or stolen goods tend to end up in the tribute pile "
                    "before it.",
                ),
            )
        ],
    )
    b.faction(
        "The Court of the King of Monkeys",
        place=island,
        realm="Magic",
        ruler="The King of Monkeys",
        summary=paragraphs(
            "Monkey society parodies the human kind. Noble sphinxes rule "
            "peasant satyri, upheld by a warrior caste of hamadryades; "
            "callithrices play clerks and scholars, and cercopitheci are "
            "specialists, entertainers and criminals. Most have Cunning and "
            "not Intelligence, so it is all pantomime: the scribe's marks mean "
            "nothing, the smith makes nothing.",
            "Visitors meet curiosity, except at the new moon, when the monkeys "
            "sink into gloom. They may also be set on by angry hamadryades, "
            "swept into a cercopithecus revel on fermented fruit, or tried by "
            "a court of sphinxes. All come in the end before the King, who has "
            "the satyrus's lack of tail, the sphinx's markings, the hamadryas's "
            "mane, the callithrix's beard and the cercopithecus's size.",
            "At each half moon he takes tribute of fruit, shells and bright "
            "stones. At each equinox tribute joins the Ceremony of the King's "
            "Urination: before the full court he passes water seven times, and "
            "all watch closely. It may be a kind of divination.",
        ),
        secrets=(
            "The King and his counsellors, drawn from all five kinds and more "
            "exotic ones, are Magic Animals. He and many of them have true "
            "Intelligence. He may have higher Might and further powers, as his "
            "storyguide chooses; the book prints no block for him."
        ),
    )
    b.creature(
        "Satyrus, an Ape",
        page="p. 46",
        source="BS&S",
        realm="Magic",
        might=7,
        form="Animal",
        size=-2,
        season="Spring",
        cunning=True,
        place=island,
        how_many="the monkeys of Pithecousa; mundane kin in North Africa's mountains",
        block={
            "characteristics": characteristics(2, 0, -3, 0, -4, 0, 2, 2),
            "virtues_flaws": [
                "Magic Animal",
                ("Learn {ability} From Mistakes", {"ability": "Athletics"}),
                ("Baneful Circumstances", {"circumstance": "new moon"}),
                ("Essential Virtue", {"trait": "Presence"}),
                "Gift of Speech",
                "Improved Abilities",
                "Improved Abilities",
                "Personal Power",
                "Personal Power",
                ("Essential Flaw", {"trait": "Perception"}),
                "Limited Speech",
                "Crafty",
                "Defensive Fighter",
                "Skilled Climber",
                "Timid",
            ],
            "abilities": [
                ("Athletics", 5, "climbing"),
                ("Awareness", 4, "predators"),
                ("Brawl", 3, "bite"),
                ("Stealth", 3, "hiding"),
                ("Survival", 3, "foraging"),
            ],
            "traits": {
                "Cheerful at Full Moon (Presence)*": 3,
                "Monkey*": 3,
                "Mischievous": 2,
                "Brave": -2,
                "Attentive at New Moon (Perception)*": -3,
            },
        },
        attacks=[
            b.attack("Bite", 2, 9, 7, -3),
            b.attack("Evasion", 2, None, 7, None),
        ],
        soak=1,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Ape the Beast",
                1,
                -1,
                "Animal",
                level=25,
                does="Takes on a minor natural ability or mundane Quality of an "
                "animal he sees, such as a frog's swimming, a cat's night "
                "vision, horns, spines or a bear's pelt, but no major change "
                "like wings. One at a time; a second replaces the first. It "
                "lasts indefinitely, but he loses a Might point each sunrise and "
                "sunset while he keeps it, regained in three hours or less in a "
                "Magic aura. MuAn 25 (Base 4, +2 Sun, +1 Part, +1 Constant "
                "effect, +1 can change ability possessed); Personal Power (25 "
                "levels, -2 Might cost).",
            ),
            b.power(
                "Mimic the Man",
                0,
                2,
                "Imaginem",
                level=3,
                does="Copies any sound exactly, even human speech, without "
                "understanding it. MuIm 3 (Base 1, +1 Conc, +1 Complexity); "
                "Personal Power (3 levels, -1 Might cost, +1 Init).",
            ),
        ],
        vis=[BodyVis(2, "Muto", "one pawn in each hand")],
        appearance=(
            "A tailless monkey of yellowish, gray or brown fur, paler beneath, "
            "with a darker face."
        ),
        notes=paragraphs(
            "Reputations: none. Gift of Thumbs (Minor Magical Quality): negates "
            "the Magic Animal's inherent No Hands, as Gift of Speech negates "
            "Mute. Not in the catalog.",
            "A mundane monkey: remove Magic Animal, Might, Magical Qualities and "
            "Inferiorities (with the Essential Traits and Powers) and vis, and "
            "lower Quickness by one. The satyrus (Simia in Latin) is the "
            "commonest kind and the only tailless one, and is found mundane "
            "through North Africa's mountains. The island may hold other exotic "
            "monkeys, such as tailless black-furred giants or tiny creatures "
            "with immense eyes.",
            "Cercopithecus: the smallest, a thief with a shaggy red-brown coat, "
            "long tail, white legs and underparts, a brighter red cap and black "
            "lines from face to ear. Also in Mauritania's scrubland, with "
            "gray-furred black-faced kin near the Torrid Zone. Size -4 (Str -8, "
            "Qik +4), add Minor Virtue (Light Touch), Minor Flaw (Carefree) and "
            "Fast Runner.",
            "Callithrix: black, with a long white beard, a shawl of white fur "
            "on the back and a white tail tuft, and no thumb. From the Horn of "
            "Africa, sometimes an Egyptian's pet. Size -3 (Str -6, Qik +3), add "
            "Minor Virtue (Perfect Balance) and Minor Flaw (Palsied Hands).",
            "Sphinx: docile, shaggy and long-tailed; males have a lion's mane "
            "and a red-striped, blue-muzzled, yellow-bearded face. From the "
            "Empire of Ghana, brought north by travellers. Add Minor Virtue "
            "(Inspirational) and Minor Flaw (Noncombatant).",
            "Hamadryas (or cynocephalus, not to be confused with the Magic "
            "Humans of that name): a fierce olive-brown, dog-faced monkey; "
            "males have a silver-gray cape and mane. From the eastern deserts "
            "and highlands. Add Minor Virtue (Berserk) and Minor Flaw "
            "(Oversensitive to Threats), drop Timid, and make Brave +2.",
        ),
    )
    return island


# -- the Rif --


def _rif(b: Builder, maghreb: Neighbour) -> dict[str, Neighbour]:
    rif = _place(
        b,
        "The Rif",
        inside=maghreb,
        summary=paragraphs(
            "The one great exception to the bands of the Maghreb: a triangular "
            "spike of mountains rising to meet Europe at the strait of "
            "Gibraltar. The Marinids, a Berber tribe opposed to the Almohads of "
            "Marrakesh, hold it, raid Almohad lands from it, and make trade "
            "with Spain and rule of it harder.",
            "Almohad loyalists paint the Marinids as barbarians, which may be unfair.",
        ),
        secrets=paragraphs(
            "The troupe chooses what the Marinids are: a rampaging horde like "
            "the Mongols, or, as in history, future conquerors of the western "
            "Maghreb who spare Fez and bring a new age of art and learning.",
            "Their weakness: the dynasty holds together only while it raids and "
            "grows. When plunder or conquest stops, each warlord looks to "
            "swallow his cousins and their followers. Stalling their advance "
            "forces a civil war that leaves them united but far smaller (p. "
            "49).",
        ),
    )
    tangier = b.town(
        "Tangier",
        place=rif,
        summary=paragraphs(
            "A modest port under the Phoenicians and Romans, grown under the "
            "Caliphate into a rough, busy crossroads of Iberia, Europe, the "
            "Mediterranean and the desert caravans, with a navy of sixty "
            "ships. It sells wool, hides, fruit, honey and wax. St. Francis has "
            "called it a city of madness and illusions.",
            "Its name is that of Tinjis, goddess or giantess, who married "
            "Heracles on his way to his labours and bore the first king, the "
            "giant Sophox. His barrow is still pointed out in the city, and many "
            "Berber chiefs claim descent from him. Giant Blood and Great "
            "Strength do turn up here, in a people who reward victors.",
            "The Periplus of Hanno, in Classic Greek from the lost Punic, is a "
            "very rare book kept in private collections here and in Alexandria, "
            "Rome and Constantinople: a tractatus on Area Lore: Beyond the "
            "Pillars of Heracles (Quality 6) and one on Magic Lore (Quality 6). "
            "It follows Hanno's sixty ships out past the Pillars, west for 35 "
            "days and then south, into thirst, heat, great hairy men and fire "
            "running into the sea (p. 44).",
        ),
    )
    _place(
        b,
        "Tumulus of Antaeus",
        inside=rif,
        summary=paragraphs(
            "South of Tangier, before the mountains, the lonely grave of "
            "Antaeus, titan or giant, rises five paces inside a ring of 175 "
            "lesser menhirs. He was once king here, and many local kings have "
            "claimed his blood. The Roman Quintus Sertorius is said to have dug "
            "it open and found huge bones, made offerings, sealed it again and "
            "paid for epics in its honour. Juba II, the learned client-king, "
            "traced his line to Heracles and Tinjis, Antaeus's consort. If the "
            "legends hold, Antaeus was the child of a Magical creature and a "
            "Faerie.",
            "Lucan's Pharsalia, Book IV (Latin) tells of Heracles's victory "
            "through a Libyan's words to the Roman Curio: tractatus on Area "
            "Lore: Maghreb (Quality 6) and on Magic Lore (Quality 6), hard to "
            "find, in heirloom collections in Italy, Iberia and Constantinople "
            "(p. 50).",
            "Of Kings and Giants, Antaeus' Bloodline (Major or Minor Supernatural "
            "Virtue, p. 50, not in the catalog): ages as Faerie Blood (Minor) or "
            "Strong Faerie Blood (Major). Minor gives one of +1 Strength (to at "
            "most +3), +1 Brawl or +1 Soak. Major gives all three, plus Large "
            "and Magic Sensitivity, and the Major Flaw Greater Malediction (must "
            "be touching the ground): off the ground the bonuses go and Soak "
            "falls by 2, though the size remains. The player chooses a Magic or "
            "Faerie alignment for good.",
        ),
    )
    _place(
        b,
        "Cave of Heracles",
        inside=rif,
        realm="Faerie",
        aura=4,
        summary=(
            "South of Tangier, the cave where the hero slept on his way to the "
            "Eleventh Labour, to kill the dragon and take the Apples of the "
            "Hesperides."
        ),
    )
    walili = _place(
        b,
        "Walili",
        inside=rif,
        aura=3,
        summary=(
            "Once Volubilis, a provincial capital amid fertile plains, and the "
            "capital claimed by the Berber king Juba II, where Latin lived on "
            "until the Caliphate came in 790. The best Roman stonework of the "
            "region survives here. When the aqueduct failed the people moved to "
            "a wadi nearby and the old city became their cemetery. Mosaics and "
            "statues stand yet, with the decumanus maximus, basilica, forum and "
            "Caracalla's arch."
        ),
    )
    return {"rif": rif, "tangier": tangier, "walili": walili}


# -- the Almohad empire --


def _almohads(b: Builder) -> Neighbour | None:
    """The Almohad governors, under the Caliph the peoples part made, when
    it has run."""
    caliph = next((n for n in b.saga.neighbours if n.name == "Almohad Caliph"), None)
    for name, text in (
        ("Ab Muammad Abd al-Wahid bin Yusef", "Governor of Sijilmassa."),
        ("Yusef ibn Ali", "Governor of Tinmal."),
        ("Abdul-Wahid", "Viceroy of Ifriqiya."),
        ("Abu Zayd bin Yujjan", "Governor of Tlemcen, which rules Tahert."),
        ("Abu Zakariya", "Governor of Fez."),
    ):
        b.lord(
            name,
            title="",
            answers_to=caliph,
            summary=(
                f"{text} He still accepts the Caliph's suzerainty, in an "
                "increasingly nominal way. No governor wants to be first to "
                "break away while the Almohads might have one good battle left, "
                "nor to spend his best men saving them. Whoever lets someone "
                "else exhaust himself destroying them may be free, or rule "
                "Marrakesh."
            ),
        )
    return caliph


def _tell(
    b: Builder, maghreb: Neighbour, caliph: Neighbour | None
) -> tuple[Neighbour, dict[str, Neighbour]]:
    tell = _place(
        b,
        "The Tell",
        inside=maghreb,
        summary=paragraphs(
            "The fertile strip of the north, called Massyli, Carthage, Africa, "
            "Ifriqiya, Tunis and now Tunisia as its lords changed, reaching "
            "from the far west to Tripoli. Here are grand Marrakesh, busy Fes, "
            "Tunis on the site of Carthage, holy Kairouan and lively Tripoli. "
            "Pirates work the coast from Mahdia, Sfax and the empty wharves of "
            "Girba.",
            "Wheeled carts go by land here behind horses, donkeys, oxen or "
            "camels; donkeys and horses are quicker than oxen but haul less. In "
            "mountain and desert wheels are worse than useless.",
        ),
    )
    marrakesh = b.town(
        "Marrakesh",
        place=tell,
        answers_to=caliph,
        ruler=ALMOHADS,
        summary=paragraphs(
            "The Red City, named for its ochre earth and pink stone, the "
            "largest in the region and capital of the Almohads, founded at the "
            "foot of the Atlas by the sultan Abu Bakr in 1062. Its heart is the "
            "great souk of the Djemaa El Fna: desert baubles, Christian and "
            "southern slaves, gold, salt, and a few faeries among the sellers, "
            "players and street urchins. The Kasbah overlooks it, ringed by a "
            "hospice, mosques, the palace, parade grounds and a garden. Nineteen "
            "gates admit the caravans.",
            "Sufis shelter in the hillside caves and come in on Fridays for "
            "prayer. Since the 1180s, when al-Mansur began the Koutoubia Mosque "
            "and renewed the Kasbah, they have been welcome, and booksellers "
            "crowd round the mosque.",
            "It is the richest city of the Maghreb, all gardens, running water "
            "and shade, and the one with the deepest shadows. The empire is "
            "crumbling; some settle scores, some enjoy what is left. Thieves "
            "here are skilled by birth, assassins by training. Its name, from "
            "'to cross over' or 'to hide', honours a watchful fortress say the "
            "scholars, and say the locals, the horse thieves who raided the "
            "old camp.",
            "The ruler is a boy of seventeen who cannot lead his nobles; his "
            "close kin rule what he still truly holds and feud without end, and "
            "distant governors own him less each year. The empire has been "
            "failing since Las Navas de Tolosa (Al-Uqab) in 1212, which cost "
            "over 100,000 men, mostly African loyalists, and the revenue of most "
            "of Iberia. Worse came nearer home, latest in 1217 outside Fes, "
            "where only ignorance of siege work kept the Marinids from the "
            "second city. The governors of al-Andalus and Majorca may have "
            "designs on the title of Caliph, and might carry power across the "
            "Strait.",
        ),
        secrets=(
            "Thieves of Marrakesh take Virtues that suit them only if they use "
            "those Abilities often (pp. 52-53): Affinity, Cautious with or "
            "Puissant in Athletics, Awareness, Legerdemain or Stealth, Intuition, "
            "Keen Vision, Light Touch, Perfect Balance, Premonitions, Ways of "
            "the Town, and the catalog's All According to Plan, Falls Like a "
            "Cat, Indescribable Face, Just an Instant, Finding Hidden Loot, Rat "
            "Up a Drainpipe, Schooled in Crime, See in Darkness (the book's "
            "Sees in the Dark) and Skilled Smuggler. Childhoods raised by "
            "thieves (p. 53, each with Native Language 5): burglar, Awareness, "
            "Bargain, Stealth 2; grifter, Charm, Guile, Legerdemain 2; lookout, "
            "Awareness, Legerdemain, Stealth 2; runner, Area Lore, Athletics, "
            "Legerdemain 2."
        ),
    )
    b.faction(
        "The Sons of Sasan",
        place=marrakesh,
        summary=paragraphs(
            "The Banu Sasan of Arabic folklore: a hidden tribe of bandits, "
            "thieves, murderers and prostitutes, sprung from the evil retinue "
            "of a Persian prince who lost his kingdom. Each city is said to have "
            "a Beggar King, and they are said to share tainted blood, school one "
            "another's children and keep unhallowed places for dark rites.",
            "Most criminals claim to belong. All in the Maghreb know the argot, "
            "the monogat Bani Sasan: Arabic full of Persian and Kurdish loans, "
            "which marks a speaker's class and carries basic private meanings, "
            "and which outsiders know at once for something odd.",
        ),
        rules=(
            "A character with a criminal background and Arabic 3 or more speaks "
            "the argot (p. 53). How close the family truly is varies by saga."
        ),
    )
    fes = b.town(
        "Fes",
        place=tell,
        answers_to=caliph,
        ruler="Abu Zakariya, governor",
        summary=paragraphs(
            "The empire's second city, for centuries its imperial capital, "
            "revived by refugees from Iberia. Even its labourers quote the "
            "Prophet to one another. Green is everywhere, with deep blue tiles "
            "set in geometry that shines as the sun crosses them.",
            "For all its age it is fragile: nomads nearly took it three years "
            "ago, and the last nomads to raid North Africa pulled down every "
            "city and aqueduct. Its faith keeps it from the sordid fatalism of "
            "other towns. The Almohads have settled many Christians and some "
            "Jews here, and the new quarter of strange music, ideas and food is "
            "what the city's rich do instead of bars and brothels.",
            "Outside the city a fig tree fruits out of season, some figs white, "
            "some black. The black raise tender horns on the eater's brow "
            "(Monstrous Appearance), which hurt terribly if struck; the white "
            "remove them. A leper is said to have won a Sultan of Fes's daughter "
            "so, tricking the ruler into the black figs and curing him in a "
            "foreign magician's dress. Hermetic listeners may wonder if he was "
            "a magus, and where he lies. The figs hold Muto vis (p. 54).",
        ),
    )
    b.university(
        "Al-Kairouine Madrasa",
        place=fes,
        school="University",
        summary=paragraphs(
            "In the eighth century one of two heiress sisters from Kairouan "
            "built a mosque in Fes, and fellow emigrants endowed it so well "
            "that a school opened. It now draws students from the Arabic world "
            "and the small communities of the Christian Mediterranean. Theology "
            "and Islamic law are the core, with the Artes Liberales and practical "
            "subjects for many. The master sits in a chair and students gather "
            "round. Some say a few teachers are astrologers, or magical.",
            "Subsidies have paid for students in good times; now they need "
            "work. All are literate and at home in mundane society, many have "
            "useful Area Lores, and some have a Realm Lore, usually Divine. "
            "Hermetic covenants could use them. Art and Academe's university "
            "hooks suit this place.",
        ),
    )
    tunis = b.town(
        "Tunis",
        place=tell,
        answers_to=caliph,
        ruler="The Hafsid family, for the Almohads",
        summary=paragraphs(
            "The Maghreb's largest port, a centre of trade and naval power for "
            "the Almohads, whose fleet has weakened with the loss of al-Andalus. "
            "It stands strikingly white under the sun, its doors ultramarine, "
            "facing a lake and living by the sea. Round the central mosque lie "
            "the markets of perfume to the north, cloth to the west, wool to "
            "the south, and dried fruit and books to the east. Others ring "
            "outward, fouler with each circle.",
            "Sailors, the navy and the water colour everything here. It needs "
            "wheat from Sicily and sells desert goods to Italy.",
        ),
    )
    tripoli = b.town(
        "Tripoli",
        place=tell,
        answers_to=caliph,
        ruler="An Almohad governor",
        summary=paragraphs(
            "The gateway to the Great Desert, chief port of the gold and slave "
            "trade in the eastern Maghreb: Carthaginian Oea, which took in two "
            "neighbours and with them the name of three cities. It depends on "
            "dhimmi trade even for its bread, and is the friendliest port to "
            "dhimmis. Its navy is weak and its farmland poor.",
            "It is laid out as a Roman would know it, two great roads crossing "
            "to make four quarters, with a mosque and fortress at the centre. "
            "Most of it is yellow sandstone, some pink, the fortress red.",
            "Phoenicians, Greeks, Egyptians, Romans, Arabs, Normans and Berbers "
            "have each left a layer, and most western schools of magic had time "
            "to plant colonies, perhaps even druids and Odinites. Seekers find "
            "the remains of each mystical occupation, and people here have "
            "links to the ruins and relics of earlier rulers.",
        ),
    )
    return tell, {
        "marrakesh": marrakesh,
        "fes": fes,
        "tunis": tunis,
        "tripoli": tripoli,
    }


def _tell_towns(
    b: Builder,
    tell: Neighbour,
    cities: dict[str, Neighbour],
    caliph: Neighbour | None,
) -> None:
    for name, text in (
        ("Mahdia", "A harbour of the Tell coast from which pirates operate."),
        ("Sfax", "A harbour of the Tell coast from which pirates operate."),
        (
            "Sharshal",
            "Roman Caesarea, a busy port joined to the old Northern Road by a "
            "branch, most of its Roman stone reused.",
        ),
        (
            "En Nassria",
            "Roman Saldae, a busy port joined to the Northern Road by a branch, "
            "most of its Roman stone reused.",
        ),
        (
            "Algiers",
            "Icosium, founded it is said by twenty companions of Heracles, "
            "Phoenician, then Roman, now the seat of a kasbah. White buildings "
            "run down to the shore behind a high wall built largely of old "
            "Imperial stone when the Arabs renewed the site in 942. Roman "
            "cemeteries lie in the sea-cliffs to the west.",
        ),
        (
            "Qusantina",
            "Constantine, which held off the Visigoths but fell to the Arabs in "
            "the seventh century: the City of Bridges, on a high plateau within "
            "the cave-riddled gorge of the Rhumel, crossed by several bridges "
            "and a treacherous natural arch. Its prosperous market deals with "
            "Pisa, Genoa and Venice.",
        ),
        (
            "Soussa",
            "Hadrumetum, founded by the Phoenicians in 1100 BC, an ally of Rome "
            "in the Third Punic War and one of its chief towns in Africa, until "
            "Oqba Ibn Nafi's army razed it. The rebuilt town hides the old one: "
            "mosaics of Virgil, strange beasts and Hellenistic gods survive, "
            "and Roman and Christian catacombs run beneath the streets.",
        ),
        (
            "Bouna",
            "Bouna Al Haditha, the new town the Arabs built a league north of "
            "old Hippo Regius in the ninth century.",
        ),
        (
            "Tbessa",
            "Roman Theveste, within a Byzantine wall of thirteen square towers, "
            "with an amphitheatre, a nearly whole Temple of Minerva and the "
            "remains of the basilica of St. Crispinus, with its chapels, "
            "baptism urns, catacombs and gardens.",
        ),
    ):
        b.town(name, place=tell, summary=text)
    tlemcen = b.town(
        "Tlemcen",
        place=tell,
        answers_to=caliph,
        ruler="Abu Zayd bin Yujjan, governor",
        summary=(
            "Once the fort of Pomeria, now a rich end of the desert caravan "
            "routes, run by families such as the al Makkari. Nearly all its "
            "Roman stone has gone into its buildings and protective wall."
        ),
    )
    b.town(
        "Tahert",
        place=tell,
        answers_to=tlemcen,
        ruler="The Governor of Tlemcen",
        summary=(
            "A thinly peopled end of the slave trade in a high central pass, "
            "better known for the ruined stone tombs called jedars to the "
            "south. Few remain of its Jewish community, and it never recovered "
            "from the Fatimid conquest of 933."
        ),
    )
    b.town(
        "Kairouan",
        place=tell,
        summary=paragraphs(
            "The fourth holy city of Islam, large parts of it closed to "
            "non-Muslims on pain of death. Its mosque, among the oldest and the "
            "largest in North Africa, is thought the model for all those of the "
            "region and draws pilgrims and students. No city of the Maghreb has "
            "a higher Dominion aura, though the book gives no figure.",
            "The sack of 1057 ended its fame for learning and as a court of the "
            "Jewish exilarchs; the Jews have mostly gone to Egypt and the "
            "scholars to Tunis, and rebuilding is unfinished. Libraries lost in "
            "the flight may lie in the ruins.",
        ),
    )
    for name, kw in (
        (
            "Djemila",
            {
                "aura": 3,
                "summary": "Spectacular ruins where two rivers meet: arches, "
                "half-standing basilicas, two fora, houses, temples and a fine "
                "amphitheatre. It could house a covenant.",
            },
        ),
        (
            "Tifesh",
            {
                "aura": 3,
                "summary": "A forgotten mountain fortress with outer walls 3 "
                "paces thick and three crumbling basilicas. It could house a "
                "covenant.",
            },
        ),
        (
            "Tiddis",
            {
                "aura": 0,
                "summary": "Hilltop ruins near Qusantina: an entry arch, paved "
                "streets, cisterns, a small forum and a Mithraeum with a Magic "
                "aura of 3. An excellent site for a starting covenant.",
            },
        ),
        (
            "Hippo Regius",
            {
                "aura": 0,
                "summary": "A Phoenician colony of the 12th century BC near the "
                "mouth of the Ubus, called 'of the King' for the Numidian "
                "pyramid tombs there, and St. Augustine's bishopric in his later "
                "years. Synods here helped settle the books of the New "
                "Testament. Arabs took it in 698 and left it in the ninth "
                "century; Africa's largest theatre remains.",
            },
        ),
        (
            "Lambaesis",
            {
                "aura": 4,
                "summary": "An empty legionary town on the military road south, "
                "with triumphal arches, undisturbed graves, dry aqueducts and "
                "the bones of temples to Aesculapius, Minerva, Jupiter and Juno, "
                "where the aura centres. No Christian inscription exists here. "
                "A column bears the whole of Hadrian's address to the Legio III "
                "Augusta.",
            },
        ),
        (
            "Tamagudi",
            {
                "aura": 0,
                "summary": "Seven leagues west of Lambaesis, the best preserved "
                "ruins in Numidia, similar in kind. Hermetic wizards might make "
                "it habitable with some effort.",
            },
        ),
    ):
        _place(b, name, inside=tell, ruined=True, **kw)
    _place(
        b,
        "Basilica of St. Augustine",
        inside=tell,
        realm="Divine",
        aura=3,
        ruined=True,
        summary=(
            "The mostly destroyed church in the ruins of Hippo. Under the "
            "rubble of the altar lies a saint's relic of 3 Faith Points."
        ),
    )
    cities["catacombs"] = _place(
        b,
        "The Catacombs of Soussa",
        inside=tell,
        aura=4,
        summary=(
            "Some reaches of the Roman and Christian catacombs under Soussa "
            "strangely keep a Magic aura of 4."
        ),
        secrets=(
            "A Virgilian cabal left texts and works here when the Arabs came, "
            "and never returned."
        ),
    )
    _place(
        b,
        "Mouth of the Bagradas",
        inside=tell,
        status="Rumoured",
        summary=(
            "A river mouth just over twenty miles north of Tunis, where a "
            "Roman general of the First Punic War fought a serpent for hours "
            "with all his men and engines. Its skin, sent to Rome, measured 120 "
            "feet."
        ),
        secrets=(
            "Magical creatures rest in auras larger than themselves, so a site "
            "of aura 3 or more, big enough for laboratories, must lie here "
            "(p. 55)."
        ),
    )
    _place(
        b,
        "Wadi of the Molting Beetles",
        inside=tell,
        summary=(
            "A hidden canyon a day east of Marrakesh, where scarab beetles of "
            "Virtue gather to shed their skins in the sun. The sparkling indigo "
            "husks dye the brightest Tuareg veils, and the nomads who gather "
            "them prize them."
        ),
        secrets=(
            "Gathered in late summer after the sirocco, the husks give four "
            "pawns of Muto and Imaginem vis (p. 54). Taking the vis ruins them "
            "for dye, so a magus must come to terms with the tribe, which guides "
            "southbound caravans and keeps grudges for generations."
        ),
    )


# -- the islands --


def _islands(b: Builder) -> dict[str, Neighbour]:
    djerba = _place(
        b,
        "Djerba",
        summary=paragraphs(
            "A low, temperate island, one of the few off this coast, lived on "
            "since the Phoenicians, who called it Meninx, and briefly taken by "
            "Roger of Sicily in the early 12th century. Here lived the "
            "lotus-eaters of Odysseus's tale. Villages cover it, joined by good "
            "Roman roads; people weave, farm, press olives and make ceramics. "
            "Thorny lotus shrubs grow everywhere, with sweet berries eaten fresh "
            "or dried or made into liquor.",
            "An enclave of Ibadi Muslims in Ajim, like those of Ghardaia, shun "
            "outsiders and pray in underground mosques.",
            "South of Girba, in one of the villages, the mosque empties by dusk "
            "for fear of the capricious jinn who come at evening with their "
            "lovely wives.",
        ),
        secrets=paragraphs(
            "The Lotophagi withdrew long ago into isolated regiones marked by "
            "clusters of lotus shrubs, avoid the islanders, and come out rarely "
            "to gather Lotus Fruit of Virtue on the Summer Solstice.",
            "In a secluded gully on a nearly inaccessible shore grows an "
            "untended copse of Lotus of Virtue, the narcotic fruit that held "
            "Odysseus's crew. Berries picked on the morning of the summer "
            "solstice give three pawns of Herbam and three of Mentem vis. Three "
            "seeds exposed only to full moonlight for a year and then sealed in "
            "an amulet give the wearer Clear Thinker (p. 57).",
        ),
    )
    for name, text in (
        (
            "Girba",
            "A ghost town on the north shore, its walls in good repair, visited "
            "only by pirates and pedlars who trade with Midoun's people.",
        ),
        ("Midoun", "A large village of Djerba that trades at empty Girba."),
        (
            "El Kantara",
            "Ancient Meninx Proper, at a southern corner of Djerba, with a Roman "
            "bridge to the mainland. A very few craftsmen here know the secret "
            "of the purple murex dye, found only here and on Mogador.",
        ),
        ("Ajim", "The Roman town of Tipasa, at Djerba's other southern corner."),
        (
            "Hara Seghira",
            "A village a league south of Girba where a large Jewish community "
            "has lived since before the fall of the Second Temple.",
        ),
    ):
        b.town(name, place=djerba, summary=text)
    _place(
        b,
        "The Ghriba Synagogue",
        inside=djerba,
        realm="Divine",
        aura=5,
        summary=(
            "The centre of Hara Seghira, built with stones from Temple Mount, "
            "and a pilgrimage for Kabbalists and those keeping Lag BaOmer."
        ),
    )
    malta = _place(
        b,
        "Malta",
        summary=paragraphs(
            "Three islands now held by the Hohenstaufen of the Holy Roman "
            "Empire: largely a fortified garrison, given over to its own "
            "defence after being emptied and resettled by Arabs and joined to "
            "Sicily. Phoenicians, Romans, Vandals, Arabs and Normans have all "
            "held it. Dolmens and deep cart ruts in the stone recall the "
            "one-eyed, tusked cyclopskin giants, whose bones sometimes appear "
            "after a flood or earthquake.",
            "Paul of Tarsus was wrecked here in 59 AD and in three months "
            "healed the sick and founded the Christian community.",
        ),
    )
    b.town("Mdina", place=malta, summary="The capital of Malta.")
    b.town("Ir-Rabat", place=malta, summary="A village beside Mdina.")
    for name, text in (
        (
            "Cathedral of Mdina",
            "Dedicated to St. Paul, and much repaired after neglect under Muslim rule.",
        ),
        (
            "Catacombs of Ir-Rabat",
            "Where the early Christians held their secret Mass.",
        ),
    ):
        _place(b, name, inside=malta, realm="Divine", aura=5, summary=text)
    _place(
        b,
        "Ghar Dalam",
        inside=malta,
        summary="A cave of Malta running deep into the rock.",
        secrets=(
            "The cyclopskin retreated to regiones here, and may be at war "
            "beneath the island."
        ),
        levels=[
            b.level(
                "Subterranean Vaults of the Cyclopskin",
                0,
                enter=(
                    "When the night of the winter solstice falls on a new moon, "
                    "go deep without any light."
                ),
                notes="The book gives no aura.",
            )
        ],
    )
    _place(
        b,
        "Caves of Comino",
        inside=malta,
        aura=4,
        summary=(
            "The smallest island, with a few farmers and shepherds, its sheer "
            "limestone cliffs riddled with caves where pirates sometimes hide "
            "before an ambush, until the sorcerer Kerrew routs them."
        ),
    )
    b.magus(
        "Kerrew",
        covenant=None,
        house="",
        age=None,
        type="companion",
        summary=(
            "A pious sorcerer who lives in Comino's caves and has a magic cloak "
            "that lets him fly, on which he sometimes goes to Malta for long "
            "stays."
        ),
    )
    gozo = _place(
        b,
        "Gozo",
        inside=malta,
        summary=(
            "The second island, said to be the home of the nymph Calypso, "
            "daughter of Atlas, who kept Odysseus seven years and bore him "
            "Nausinous, Nausithous and a daughter. His blood still shows in "
            "Blessing of Venus or Great Presence among its women, and at least "
            "one magus from here claimed descent and could call up Aura of "
            "Rightful Authority."
        ),
    )
    _place(
        b,
        "Ggantija",
        inside=gozo,
        aura=4,
        summary=(
            "A huge clover-shaped stone complex within a boundary wall, with a "
            "stone circle nearby, built by a giantess of Calypso's titan kin. "
            "She has not been seen in living memory; some say she sleeps in a "
            "cave near by, waiting for her lover."
        ),
    )
    return {"djerba": djerba, "malta": malta}


# -- Cyrenaica --


def _cyrenaica(b: Builder) -> dict[str, Neighbour]:
    cyrenaica = _place(
        b,
        "Cyrenaica",
        summary=paragraphs(
            "The eastern coast, settled by Greek refugees from Thera on the "
            "plains below the Jebel Akhdar: the Pentapolis, small city-states "
            "led at first by Cyrene. It borders the Libyan deserts and has few "
            "cities, but many forts and nearly 2000 fortified farms of the "
            "Legio III Augusta. The Limes Tripolitana lasted in some form until "
            "the Banu Hilal overran it in the 11th century, and within decades "
            "the sand had most of it.",
            "After the Arabs came in 643 it became al-Maghrib al Adna, the "
            "Nearest West, and it is now a backwater. Though Muslim, its people "
            "keep the Greek settlers' stories, and its supernatural fauna and "
            "flora are nearer to Greece's than the Arabic or Berber desert's, "
            "so magi from Europe find it oddly familiar.",
            "Outside every Tribunal and far from any great Islamic town, the "
            "hills would suit a Spring covenant of Theban magi, though the "
            "Children of Olympos (The Sundered Eagle pp. 125-127) lately tried "
            "and failed in mysterious circumstances.",
            "Silphium, the herb of Cyrene's coins, was the region's fortune and "
            "is thought extinct since Nero ate the last stalk. Lesser asafoetida "
            "(tyib, devil's dung) stands in for it in the kitchen, and some magi "
            "think silphium merely its Virtuous form. A bag of the resin at the "
            "neck is a Traditional Ward for some lesser Faerie jinn; it can "
            "replace myrrh, with Shape and Material bonus: protect against evil "
            "spirits +3 (p. 62).",
        ),
        secrets=(
            "Silphium of Virtue survives only in a few lost Magic regiones in "
            "the coastal mountains. Enriched by cutting the stem and sealing "
            "the faintly scented resin in a jar of pine nuts for a season, then "
            "eating one nut a day, it wards against poison as Greater Immunity "
            "for a year, with infertility as Lesser Malediction for as long. "
            "Unenriched, its heart-shaped seeds hold 2 pawns of extraordinary "
            "Corpus vis, or serve as a finite-use Lesser Enchantment, Silphium "
            "Seeds of Corpus Vis (PeCo 15; R: Touch, D: Mom, T: Unborn Child; "
            "Base 5, +1 Touch, +1 Part), which ends a pregnancy, with a Stamina "
            "stress roll against 6 after the first month or a Medium Wound. It "
            "derives from Black Anne's Kiss (Ancient Magic pp. 54-56), and "
            "study may give Insight into that magic (pp. 62-63)."
        ),
    )
    b.town(
        "Barce",
        place=cyrenaica,
        ruler="Ayyubid Sultan of Egypt",
        summary=(
            "A small inland town, first capital of Barqah under the Fatimids, "
            "now ruled by the distant Ayyubid sultans of Egypt."
        ),
    )
    b.town(
        "Sidi Rafaa",
        place=cyrenaica,
        summary=(
            "A village port on the site of Greek Balagrae, named for the "
            "Prophet's Companion Ruwaifi bin Thabit al-Ansari, entombed here."
        ),
    )
    apollonia = _place(
        b,
        "Apollonia",
        inside=cyrenaica,
        ruined=True,
        summary=(
            "Cyrene's port, 8 miles to the north and some 20 miles from Sidi "
            "Rafaa on the old coast road: renamed Sozusa for Apollon Soter, "
            "nominally Christian by the fifth century, with abandoned churches "
            "inside crumbling walls. The land has sunk and much is under water. "
            "Only a small village marks the stop on the road from Alexandria to "
            "Leptis Magna, but the Genoese have lately set up a small outpost "
            "and are building up trade. Of three islets, the largest held the "
            "Theran shipyards and the smallest ended the western mole."
        ),
    )
    pharos = _place(
        b,
        "The Pharos of Apollonia",
        inside=apollonia,
        aura=3,
        ruined=True,
        summary=(
            "The ruin of an ancient lighthouse on the third islet just outside "
            "the harbour."
        ),
        secrets=(
            "Inside are a makeshift Hermetic laboratory, a shattered oversized "
            "glass lens, a freshly slain man and signs of a fight with a great "
            "sea creature."
        ),
    )
    cyrene = _place(
        b,
        "The Ruins of Cyrene",
        inside=cyrenaica,
        realm="Faerie",
        aura=3,
        ruined=True,
        summary=(
            "Rome's metropolis and regional capital until Diocletian favoured "
            "Ptolemais late in the third century. People and governor moved to "
            "the coast, a garrison lingered in the forum-fort, and no civilians "
            "have been recorded here since the Arabs passed in the seventh "
            "century. A temple of the Faerie god Zeus lies by the ruined circus, "
            "and there are shrines of Demeter and Dionysos within the walls. "
            "The Olympian temples hold Faerie auras of 4."
        ),
    )
    _place(
        b,
        "Sacred Spring of Kura",
        inside=cyrene,
        aura=5,
        summary=(
            "The spring near the Temple of Apollon, sacred to the water nymph "
            "Kura, once worshipped by Cyrene's citizens. Its rivulet joins the "
            "river that runs through the necropolis to the sea."
        ),
        secrets=(
            "Kura is an unfettered Magic spirit, a nereid and genius loci who "
            "remembers true silphium and the groves above the city. She cannot "
            "leave her precinct. Sacrifice or a restored shrine will win her "
            "help, and she may use Zeynab as intermediary through a Spiritual "
            "Pact, taking her as Spirit Votary (Realms of Power: Magic pp. "
            "88-89). She might be patron of a Theban-style covenant (The "
            "Sundered Eagle pp. 30-31) but mistrusts Hermetics after hostile "
            "Berber and Arab wizards; her price includes veneration, perhaps a "
            "magus's Spiritual Pact and a promise to restore her public worship, "
            "which risks the Code."
        ),
        levels=[
            b.level(
                "Kura's Regio",
                5,
                enter=(
                    "Follow the rivulet from the sacred spring upstream from "
                    "where it joins the river."
                ),
                notes=(
                    "The book gives the regio no aura of its own; the 5 is the "
                    "spring's grounds, which lead to it."
                ),
            )
        ],
    )
    b.magus(
        "Zeynab",
        covenant=None,
        house="",
        age=None,
        type="companion",
        summary=(
            "Youngest daughter of the headman of the village by Cyrene, the "
            "only person who knows the nymph Kura still lives. She stumbled "
            "into the regio last spring and now visits often."
        ),
    )
    _place(
        b,
        "Myrtoessa, the Hill of Myrtles",
        inside=cyrene,
        summary=(
            "The hill over Cyrene where Apollon seduced Kura. A grove of Myrtles "
            "of Virtue grows on its northern slopes."
        ),
    )
    leptis = _place(
        b,
        "Leptis Magna",
        inside=cyrenaica,
        ruined=True,
        summary=(
            "The finest ruins in Africa, raised by its son the Emperor Septimius "
            "Severus: nearly perfect arches, a largely whole basilica, a broad "
            "theatre and forum, a harbour guarded by a Byzantine wall and a "
            "lighthouse still looking out to sea. Many buildings lie half under "
            "the preserving sand, which ate the farmland, so only caravans camp "
            "here now."
        ),
    )
    _place(
        b,
        "Temple of Serapis",
        inside=leptis,
        aura=2,
        summary="A seaside temple in the ruins of Leptis Magna.",
    )
    _place(
        b,
        "The Jebel Akhdar",
        inside=cyrenaica,
        summary=(
            "The Green Mountain, a forested coastal plateau riddled with wadis, "
            "rivers and springs, among the wettest lands of North Africa. Muslim "
            "villages lie scattered through it, but its groves hold nymphs and "
            "fauns more than the ghul and jnun of Libya's deserts. Myrtle and "
            "herbs abound, and Bees of Virtue, fed in the hills' many Magic "
            "auras, make honey of varied magical powers."
        ),
    )
    _place(
        b,
        "The Altars of the Philaeni",
        inside=cyrenaica,
        aura=2,
        summary=(
            "Two heaps of broken stone on a hillock above the easternmost point "
            "of the Gulf of Syrtis, once the border of Carthage and the Greek "
            "colonies and later of the two halves of the Empire. Here two "
            "Philaenus brothers, Carthaginian runners accused of cheating in the "
            "race that was to fix the border, are said to have offered to be "
            "buried alive."
        ),
        secrets=(
            "The Philaeni are inseparable daimonic Heroes with pooled Magic "
            "Might 35, summoned only by a joint theurgic rite of two wizards "
            "using Wizard's Communion. Once they gave swiftness to legions on "
            "their stretch of road; they can also grant duplication of a "
            "recently cast spell, enforce truth, and curse oathbreakers. The "
            "contemporary Cult of Mercury (The Mysteries: Revised Edition pp. "
            "114-117) sometimes holds initiations here."
        ),
        levels=[
            b.level(
                "The Twin Pillars",
                4,
                enter="A Key to the Mystic Veil set in the northern pile of stone.",
                notes=(
                    "Twin pillars with blood-stained altars, turned from a "
                    "Carthaginian to a Mercurian site after Carthage fell."
                ),
            )
        ],
    )
    _place(
        b,
        "Siwa",
        summary=(
            "A large oasis in a long depression at the north-west edge of the "
            "Great Sand Sea, the old border of Libya and Egypt. As Ammonium it "
            "held the oracle of Ammon, equated with Zeus and consulted by "
            "Hercules, Perseus and Alexander. Tracks run to the coast at Sallum "
            "and Matruh, north-east to Cairo, and south-west to the Tuareg "
            "outpost of Ghat."
        ),
    )
    return {
        "cyrenaica": cyrenaica,
        "cyrene": cyrene,
        "pharos": pharos,
    }


# -- the plateau and the mountains --


def _plateau_and_atlas(
    b: Builder, maghreb: Neighbour, caliph: Neighbour | None
) -> Neighbour:
    plateau = _place(
        b,
        "The Grand Plateau",
        inside=maghreb,
        summary=(
            "Foothills and highlands along the Atlas, fertile enough in places "
            "for large towns, but mostly grazed by nomad flocks. Near as it is "
            "to the Tell, its roads are poor outside a few trade routes, and "
            "people have given up wheels; they keep clear tracks for riders and "
            "herds. This is the country for the sort of tale told of remote "
            "rural Europe."
        ),
    )
    b.town(
        "Sijilmasa",
        place=plateau,
        answers_to=caliph,
        ruler="Ab Muammad Abd al-Wahid bin Yusef, governor",
        summary=paragraphs(
            "The western gate of the desert trade, the last cosmopolitan stop "
            "before the oasis towns, and the home of the world's finest dates. "
            "Its stone-faced brick walls and all its grandeur are decaying, "
            "like a city that was vastly rich a century ago with nothing spent "
            "since. Nomads raid it in hard times, and its rulers plot rebellion "
            "in easy ones.",
            "An Almohad army took it last century and a governor holds it, for "
            "the empire must have the desert's money, and the people loathe "
            "them for it. The Jewish community is gone, fled or killed in a "
            "pogrom driven by fanaticism or, more likely, money. Tall wheels "
            "lift water from the Ziz for gardens and for the bathhouse of the "
            "largest mosque, where Sufis talk philosophy. The Almohads watch "
            "for popular Sufis, and founded many madrasas. With its stone "
            "mosque, those give the city a Divine aura of 4.",
        ),
    )
    return _place(
        b,
        "The Atlas Mountains",
        inside=maghreb,
        summary=(
            "To North Africans what the forest is to Europeans: the blank space "
            "where a story can always be found. It lies almost beyond the law, "
            "a refuge for exiled princes, resting bandits and heretical sects, "
            "with faerie towns, magical caves, ascetics' houses, diabolists' "
            "meeting places, wizards' towers and forgotten kings' tombs. It "
            "was perhaps the Titans' fortress against the Olympians, and may "
            "shelter the last of the coastal peoples who fled Rome, Greece or "
            "Arabia. The range seems endless, and past its sudden southern drop "
            "lies the Great Desert."
        ),
    )


def _muqadam(b: Builder, maghreb: Neighbour) -> None:
    b.creature(
        "Muqadam, the Barbary Lion of Virtue",
        page="pp. 60-61",
        source="BS&S",
        realm="Magic",
        might=40,
        form="Animal",
        size=3,
        season="Winter",
        confidence=(2, 6),
        place=maghreb,
        block={
            "characteristics": characteristics(1, 0, 0, -4, 8, 3, 2, 0),
            "virtues_flaws": [
                "Magic Animal",
                "Magical Master",
                ("Essential Virtue (Major)", {"trait": "Brave"}),
                "Improved Characteristics",
                "Improved Characteristics",
                "Piercing Gaze",
                vf_puissant("Brawl"),
                "Second Sight",
                "Self-Confident",
                "Tough",
                "Wilderness Sense",
                "Difficult Underlings",
                "Fury",
                "Proud (Major)",
                "Infamous",
                MINOR_WEAKNESS,
                "Gigantic",
                "Greater Power",
                ("Major Virtue", {"virtue": "Magical Master"}),
                "Ritual Power",
                "Ritual Power",
                "Gift of Speech",
                "Improved Abilities",
                "Improved Initiative",
                *["Improved Might"] * 7,
                *["Improved Powers"] * 3,
                "Improved Soak",
                *["Lesser Power"] * 3,
                "Personal Power",
                "Personal Power",
                "Susceptible to Deprivation",
            ],
            "abilities": [
                ("Animal Ken", 5, "felines"),
                ("Area Lore: Maghreb", 4, "auras"),
                ("Area Lore: Great Desert", 4, "auras"),
                ("Athletics", 5, "pouncing"),
                ("Awareness", 4, "prey"),
                ("Bargain", 4, "setting terms"),
                ("Brawl", 7, "claws"),
                ("Concentration", 3, "Trackless Step"),
                ("Dead Language: Latin", 2, "conversation"),
                ("Etiquette", 4, "Beasts of Virtue"),
                ("Folk Ken", 3, "first impressions"),
                ("Guile", 5, "misleading"),
                ("Hunt", 5, "gazelle"),
                ("Leadership", 6, "felines"),
                ("Living Language: Arabic", 4, "greetings"),
                ("Living Language: Berber", 4, "greetings"),
                ("Organization Lore: Berber Tribes", 3, "travel routes"),
                ("Penetration", 4, "Animal"),
                ("Second Sight", 4, "invisible things"),
                ("Stealth", 5, "stalking"),
                ("Survival", 5, "deserts"),
                ("Wilderness Sense", 4, "hazards"),
            ],
            "traits": {"Brave*": 6, "Proud": 6, "Fierce": 3, "Lion*": 3},
            "reputations": {"Fearsome (local)": 4},
        },
        attacks=[
            b.attack("Claws", 3, 17, 13, 12),
            b.attack("Bite", 0, 15, 10, 11),
        ],
        soak=10,
        fatigue_levels=BEAST_FATIGUE,
        encumbrance="0 (0)",
        powers=[
            b.power(
                "Know Thy Subject's State",
                4,
                -14,
                "Animal",
                rtd=("Arc", "Mom", "Boundary"),
                level=35,
                penetration_bonus=15,
                does="With a moment's concentration he learns the physical state "
                "of any Beast of Virtue whose token he holds. InAn 35 (Base 3, "
                "+4 Arc, +4 Boundary); Ritual Power x2. Might spent so is "
                "recovered only by resting in a Magic aura of 4 or higher.",
            ),
            b.power(
                "Routing Bellow",
                0,
                -3,
                "Animal or Mentem",
                rtd=("Voice", "Diam", "Sound"),
                level=30,
                does="A roar that makes men and beasts who hear it flee in fear. "
                "ReAn(Me) 30 (Base 5, +1 Diam, +3 Sound, +1 Mentem requisite); "
                "Greater Power (30 levels, -3 Might cost, +5xp Penetration).",
            ),
            b.power(
                "Circle of Beast Warding",
                4,
                -8,
                "Animal",
                rtd=("Touch", "Ring", "Circle"),
                level=20,
                does="A ring traced in the earth that no mundane beast of Size "
                "+4 or less may cross; he thinks it unsporting for hunting. ReAn "
                "20 (Base 2, +1 Touch, +2 Ring, +3 Size); Lesser Power (20 "
                "levels, +5xp Penetration).",
            ),
            b.power(
                "Cowing Snarl",
                0,
                0,
                "Animal or Mentem",
                rtd=("Eye", "Diam", "Individual (Size +3)"),
                level=25,
                does="A man or beast of his size or less, caught by his gaze, "
                "kneels in fear. ReAn 25 (Base 4, +1 Eye, +1 Diam, +2 Size, +1 "
                "Mentem requisite); Lesser Power (25 levels), Improved Powers x3 "
                "(-5 Might cost, +10 Initiative).",
            ),
            b.power(
                "Trackless Step",
                2,
                -4,
                "Terram",
                rtd=("Touch", "Conc", "Individual"),
                level=10,
                does="His sweeping tail erases his tracks as he walks. ReTe 10 "
                "(Base 4, +1 Touch, +1 Conc); Lesser Power (10 levels, +15xp "
                "Concentration).",
            ),
            b.power(
                "Hunter's Pounce",
                3,
                -3,
                "Animal",
                rtd=("Pers", "Mom", "Individual (+3 Size)"),
                level=25,
                does="Leaps up to 50 paces. ReAn 25 (Base 15, +2 Size); Personal "
                "Power (25 levels).",
            ),
            b.power(
                "Sleep with Eyes Open",
                1,
                -2,
                "Animal",
                rtd=("Per", "Sun", "Individual (+3 Size)"),
                level=20,
                does="He sleeps with open eyes and is hard to surprise. ReAn 20 "
                "(Base 4, +2 Sun, +2 Size); Personal Power (20 levels, -1 Might "
                "cost).",
            ),
        ],
        vis=[BodyVis(8, "Animal", "in his mane")],
        appearance=(
            "A great tawny lion near the size of a moose or aurochs, with huge "
            "paws, carefully sharpened dark claws and a mane hung with small "
            "objects. His tail swishes when he is irritated, and lying down his "
            "left rear foot twitches. His flanks are scarred and a small notch "
            "marks his right ear."
        ),
        notes=paragraphs(
            "Natural weapons: Large claws Init 0, Atk +5, Def +3, Dam +4; Large "
            "teeth Init 0, Atk +4, Def +1, Dam +3. Hide Protection +2. Flaw "
            "details: Fury (lion captors), Weakness (surrendering foes).",
            "The greatest of the Barbary lions, who exists to hunt and rule the "
            "beasts of the Maghreb. His roaming court holds lesser Lions of "
            "Virtue (Realms of Power: Magic p. 60), Bears, Jackals and Leopards "
            "of Virtue, with Foxes and Griffon Vultures as heralds and spies, "
            "and Gazelles and Antelope as messengers. The tokens in his mane are "
            "Arcane Connections to his vassals, tied there by his valet, Srba, "
            "a Barbary Ape of Virtue. He favours the Vultures over the Foxes and "
            "the Antelope over the Gazelles, counts the Leopards his peers, "
            "dislikes the Jackals' attitude but values their work, and finds the "
            "Bears enigmatic and erratic.",
            "He distrusts humans, remembering Rome's capture of Barbary lions "
            "for the arena, and hunts small parties, scattering them and taking "
            "their mounts; only if attacked does he strike people, often enough "
            "that the tribes avoid parts of the Great Desert in spring and "
            "autumn. Since two of his cubs were taken, anyone seen holding a "
            "captive lion in the sands forfeits his life. Otherwise he behaves "
            "as Pentule, the Lion of Virtue (Realms of Power: Magic p. 60).",
        ),
    )


def _azru(b: Builder, atlas: Neighbour) -> None:
    b.creature(
        "Azru, the Atlas Bear of Virtue",
        page="p. 64",
        source="BS&S",
        realm="Magic",
        might=25,
        form="Animal",
        size=2,
        season="Autumn",
        confidence=(1, 3),
        place=atlas,
        block={
            "characteristics": characteristics(1, 0, 0, -5, 6, 4, 2, 0),
            "virtues_flaws": [
                "Magic Animal",
                "Magical Champion",
                ("Essential Virtue (Major)", {"trait": "Brave"}),
                "Ferocity",
                "Improved Characteristics",
                "Improved Characteristics",
                "Tough",
                "Wilderness Sense",
                ("Essential Flaw (Major)", {"trait": "Slothful"}),
                ("Anchored to the {land}", {"land": "Mountains (Atlas)"}),
                "Greedy (Minor)",
                "Reclusive",
                MINOR_WEAKNESS,
                "Greater Power",
                "Gift of Speech",
                "Improved Damage",
                "Improved Initiative",
                *["Improved Might"] * 7,
                "Improved Powers",
                "Improved Soak",
                "Improved Soak",
                "Lesser Power",
                vf_minor("Magical Champion"),
                vf_minor("Puissant Brawl"),
                vf_minor("Puissant Hunt"),
                vf_minor("Wilderness Sense"),
                "Susceptible to Deprivation",
                "Aggressive",
                "Extra Natural Weapons",
                "Fast Runner",
                "Grapple",
                "Pursuit Predator",
                "Hardy",
                "Imposing Appearance",
                "Large Claws",
                "Tough Hide",
            ],
            "abilities": [
                ("Area Lore: Maghreb", 5, "mountains"),
                ("Athletics", 4, "sprinting"),
                ("Awareness", 4, "prey"),
                ("Brawl", 7, "claws"),
                ("Etiquette", 3, "Beasts of Virtue"),
                ("Guile", 3, "lying"),
                ("Hunt", 5, "boar"),
                ("Living Language: Arabic", 4, "conversation"),
                ("Living Language: Berber", 4, "conversation"),
                ("Organization Lore: Berber Tribes", 1, "campsites"),
                ("Penetration", 2, "Mentem effects"),
                ("Survival", 5, "foraging"),
                ("Swim", 3, "against the current"),
                ("Wilderness Sense", 4, "finding oases"),
            ],
            "traits": {"Brave*": 6, "Slothful*": 6, "Bear*": 3, "Aggressive": 2},
            "reputations": {"Ferocious (local)": 2},
        },
        attacks=[
            b.attack("Claws", 3, 17, 13, 13),
            b.attack("Teeth", 0, 12, 10, 7),
            b.attack("Grapple", 0, 11, 9, None),
        ],
        soak=13,
        fatigue_levels=BEAST_FATIGUE,
        encumbrance="0 (0)",
        powers=[
            b.power(
                "Terrible Roar",
                0,
                -3,
                "Animal or Mentem",
                rtd=("Voice", "Diam", "Sound"),
                level=30,
                does="A roar that freezes men and beasts who hear it, trembling "
                "with fear. ReAn(Me) 30 (Base 5, +1 Diam, +3 Sound, +1 Mentem "
                "requisite); Greater Power (30 levels, -3 Might cost, +5xp "
                "Penetration).",
            ),
            b.power(
                "Thunderous Swipe",
                0,
                -10,
                "Animal or Corpus",
                rtd=("Touch", "Mom", "Individual (Size +2)"),
                level=25,
                does="A blow that throws anything up to his own size 5 paces; "
                "Dex against Ease Factor 12 to stay standing. Thrown straight up "
                "or into something hard, the target takes falling damage (+1 per "
                "2 feet, +7 at most). It may join a claw attack. ReAn 25 (Base "
                "10, +1 Touch, +1 Size, +1 Corpus requisite); Lesser Power (25 "
                "levels), Improved Powers (-5 Might cost).",
            ),
        ],
        vis=[BodyVis(5, "Animal", "in his claws")],
        appearance=(
            "A large shaggy bear of up to fifty stone (700 pounds), over seven "
            "feet tall upright, with a coat from light brown or yellowish to "
            "black, most often medium brown, big claws and a deep, echoing roar."
        ),
        notes=paragraphs(
            "Natural weapons: Large Claws Init 0, Atk +5, Def +3, Dam +4; Teeth "
            "Init 0, Atk +3, Def +1, Dam +1. Hide and fur Protection +3. Flaw "
            "details: Weakness (sweet foods); Extra Natural Weapons (bite); "
            "Improved Damage and Improved Initiative (claws).",
            "Once hunted for the arena, Africa's only native bear ranges from "
            "Marrakesh to Tripoli in its mountains and their surrounds: mundane "
            "ones brownish black with a reddish-orange belly, no white on the "
            "short muzzle, stout and strong-clawed, hunting wadi and brush and "
            "always seeking a beehive.",
            "Enrichment: wrap the Bear's claws in its hide round a dry river "
            "rock from a wadi in its hunting grounds and leave them 20 days in "
            "the sun. The fetish grants Tough.",
        ),
    )


def _imghrawn(b: Builder, maghreb: Neighbour) -> None:
    b.creature(
        "Imghrawn, Scion of Antaeus",
        page="p. 49",
        source="BS&S",
        realm="Magic",
        might=20,
        form="Ignem",
        size=4,
        season="Summer",
        confidence=(1, 3),
        place=maghreb,
        block={
            "characteristics": characteristics(0, 1, 0, -2, 10, 3, 3, -2),
            "virtues_flaws": [
                "Magical Monster",
                "Improved Characteristics",
                "Intuition",
                "Magic Human",
                "Keen Vision",
                vf_puissant("Brawl"),
                "Sharp Ears",
                "Tough",
                "Warrior",
                ("Baneful Circumstances", {"circumstance": "not touching the ground"}),
                "Fury",
                "Overconfident",
                "Proud (Minor)",
                MINOR_WEAKNESS,
                "Gigantic",
                "Gigantic",
                "Gigantic",
                "Improved Abilities",
                "Improved Damage",
                "Improved Damage",
                "Improved Powers",
                *["Improved Soak"] * 4,
                vf_minor("Improved Characteristics"),
                vf_minor("Improved Characteristics"),
                "Personal Power",
                "Personal Power",
                "Monstrous Appearance",
                ("Minor Flaw", {"flaw": "Slow Power"}),
                "Susceptible to Deprivation",
            ],
            "abilities": [
                ("Area Lore: Maghreb", 3, "kings"),
                ("Awareness", 4, "spotting travelers"),
                ("Brawl", 5, "grapple"),
                ("Guile", 3, "concealing intent"),
                ("Great Weapon", 4, "cudgel"),
                ("Living Language: Arabic", 4, "threats"),
                ("Stealth", 5, "remaining unseen"),
                ("Survival", 4, "finding oases"),
                ("Thrown Weapon", 4, "stone"),
            ],
            "traits": {
                "Proud": 3,
                "Devoted": 2,
                "Gluttonous": 3,
                "Greedy": 2,
                "Violent": 2,
            },
        },
        attacks=[
            b.attack("Dodge", 0, None, 1, None),
            b.attack("Fist", -2, 8, 8, 16),
            b.attack("Kick", -1, 9, 8, 13),
            b.attack("Cudgel", -1, 12, 9, 17),
            b.attack("Thrown Stone", -2, 9, 8, 15),
        ],
        soak=16,
        fatigue_levels=FATIGUE,
        encumbrance="0",
        equipment="Acacia wood cudgel, sack of salt, gold, trinkets",
        powers=[
            b.power(
                "Mien of Man or Massif",
                0,
                -5,
                "Imaginem",
                level=25,
                does="He looks and sounds like a Size 0 man. MuIm 25 (Base 2, +4 "
                "size, +2 Sun, +1 Moving Image); Improved Powers: -3 Might cost.",
            ),
            b.power(
                "Friend of the Desert",
                1,
                -5,
                "Ignem",
                does="He ignores heat and fire damage of +15 or less. ReIg (Base "
                "4, +2 for +15 or less, +2 Sun, +1 size; the book gives no "
                "total); Improved Powers: -2 Might cost; Slow Power.",
            ),
        ],
        vis=[BodyVis(4, "Ignem", "in his heart")],
        appearance=(
            "Nearly three times a man's height (14 ft, 2775 lbs), fearsome and "
            "strangely handsome, thick and curly of beard, strong of nose, with "
            "bright calculating black eyes. He wears Berber robes, with skulls in "
            "swaths of indigo at his waist, and carries a huge acacia cudgel "
            "studded with green-white desert glass. A miserable camel bears his "
            "hoard, and now and then he leads a chain of slaves, usually to "
            "trade for baubles, sometimes to eat."
        ),
        notes=paragraphs(
            "Reputations: none. Flaw details: Fury (disrespecting his bloodline), "
            "Weakness (must meet a declared challenge); Improved Damage (Fist) "
            "x2; Personal Power (Friend of the Desert, Mien of Man or Massif).",
        ),
    )


# -- the story seeds --


def _maghreb_stories(
    b: Builder,
    maghreb: Neighbour,
    atlantic: dict[str, Neighbour],
    rif: dict[str, Neighbour],
    cities: dict[str, Neighbour],
) -> None:
    coast, anfa = atlantic["coast"], atlantic["anfa"]
    _seed(
        b,
        "The Merchant House",
        paragraphs(
            "A merchant house turns to piracy on the side: a hand-picked, silent "
            "crew takes a ship now and then, kills or sells the witnesses far "
            "away, and sends prize or cargo on through foreign ports. Then a "
            "vessel vanishes with an important passenger, a redcap, noble or "
            "merchant prince, or with the characters' own supplies, and they are "
            "asked to find out what happened (p. 40).",
        ),
        coast,
    )
    _seed(
        b,
        "Robbing the Ifranj",
        "Raiders stuff their holds with fighters for few supplies, which far "
        "Christian voyages do not allow, yet robbing the Ifranj wins them "
        "respect and perhaps formal standing if war comes. The characters may "
        "sail as raiders or as pirate hunters (p. 40).",
        coast,
    )
    _seed(
        b,
        "Making It Personal",
        "The last scion of a destroyed noble house flees to sea, or is sold "
        "there, and leads pirates against those he blames. He spares pilgrims "
        "and has beautiful manners, and leaves the emir of Seville's interests "
        "alone, so the costly navy stays home. The characters may ally with "
        "him, aid his victims, or act for the true scion, now an apprentice or "
        "companion, who wants to know who uses his name (p. 40).",
        coast,
    )
    _seed(
        b,
        "Mercenary Pirates",
        "No Muslim noble hires pirates, officially, but before a local war each "
        "side wants the other's trade cut, and servants quietly hire merchants, "
        "dhimmis, foreign Christians or magi. Characters offered the work know "
        "war is near, and can use the confusion to settle scores and gain "
        "resources (pp. 40-41).",
        coast,
    )
    _seed(
        b,
        "Imperial Legacies",
        "Why did the Romans leave so many of these sites so suddenly at the end "
        "of the third century, when the Berbers had never driven them out in a "
        "thousand years? Roman ghosts might tell of Mercurian wizards who "
        "disturbed the Great Hunger; priests' scrolls and fragments of the road "
        "magic may lie in hidden refuges (p. 42).",
        maghreb,
        secrets="A large pack of bouda is moving in from the south to pick the "
        "region clean.",
    )
    _seed(
        b,
        "A Pirate Crown",
        "After 150 years the pirates of Anfa still hope to be free of their "
        "Almoravid suzerain, and quietly undermine the governor meanwhile. A "
        "Tytalus may take up their cause, or a rival may expose it to draw "
        "a foe into the open (p. 42).",
        anfa,
    )
    _seed(
        b,
        "Punic Ghosts and Roman Ruins",
        "Magi call up the dead at Chellah, where few will question digging, and "
        "Roman ghosts might know the way to the Hesperides. Then a curious youth "
        "or a grave robber tells the powers in Sale. Can the magi contain it "
        "(p. 44)?",
        coast,
    )
    _seed(
        b,
        "Tabula Non Rasa",
        "A copper slate of Punic text turns up, perhaps Hanno's lost tablet from "
        "the sack of Carthage, with clues to avoid his hazards and find the "
        "Hesperides, the Tin Islands or some other famous place: a resource "
        "uncontested, for those who dare the unknown (p. 44).",
        rif["tangier"],
    )
    _seed(
        b,
        "The Roads of Rome",
        "A Bonisagus seeking the secrets of the Cult of Mercury asks the "
        "characters' help to study North Africa's Roman roads, some still whole "
        "in empty lands. Digging them up draws noblemen, whom he is quite unable "
        "to handle (p. 50).",
        maghreb,
    )
    _seed(
        b,
        "The Takers of Taxes",
        "Rulers tax merchants at each border, and a greedy collector is a sign "
        "of a corrupt lord; decent men taunt, fool and harass such people, and "
        "the poor make heroes of those who do. Good for companions and grogs, "
        "and a way to meet allies and enemies who remember it when the covenant "
        "later seeks hard-to-find goods (p. 50).",
        maghreb,
    )
    _seed(
        b,
        "A Claim to the Throne",
        "Imghrawn thinks a swath of the Maghreb his birthright and that, like "
        "Antaeus, he must raise a temple of his foes' skulls. He starts with a "
        "fortified ksour and oasis near the covenant, which supplies its dates "
        "and livestock. Rescue the people, or back him and draw the governor's "
        "men and tax collectors into a very strange war (p. 50).",
        maghreb,
        antagonist="Imghrawn, Scion of Antaeus",
    )
    _seed(
        b,
        "The Pavilion with Three Items",
        paragraphs(
            "A captured thief offers a true tale for his freedom: in Marrakesh, "
            "in the garden of three brothers, stands a pavilion their dying "
            "father forbade them. It holds a sheepskin rug, a cap and a hashish "
            "pipe, all magical (p. 52).",
        ),
        cities["marrakesh"],
        secrets=paragraphs(
            "The sheepskin carries whoever sits on it, and itself, in a blink to "
            "any place asked, even unseen or conditional ('wherever the man who "
            "stole my trousers has gone').",
            "The cap makes the wearer and what he wears or holds invisible, but "
            "not mounts or objects like statues; he can still be heard, or "
            "smelled by dogs.",
            "The pipe turns exhaled smoke to small gold ingots, without limit "
            "while there is hashish, but the smoker is out of his mind and "
            "under the storyguide's control, usually to his humiliation, and "
            "often with the other two items. That is why the merchant forbade "
            "the pavilion.",
        ),
    )


def _monkey_stories(b: Builder, pithecousa: Neighbour) -> None:
    _seed(
        b,
        "The Monkey's Fist",
        "Among treasure the characters find a sphere of golden cord, a 'monkey's "
        "fist', with the legend of Pithecousa written on it and a minor Hermetic "
        "enchantment. Those who know the Order may think of Verecunda, a "
        "Verditius of Favonius (The Sundered Eagle p. 83), expert in knots, whose "
        "familiar is a monkey (p. 47).",
        pithecousa,
        secrets="Verecunda made it for the King of Monkeys in payment for her "
        "familiar. A treacherous servant stole it years ago and has become "
        "formidable. He needs it to return and challenge the King, and will "
        "pose as a helper to get it.",
        antagonist="The King's treacherous servant",
    )
    _seed(
        b,
        "A Familiar Ape",
        "A magus who takes a monkey familiar from the island without the King's "
        "leave suffers Supernatural Nuisance as subjects come to fetch it back. "
        "If he asks, the King sets a test. Monkey mothers bear twins, love one "
        "and carry the hated one on the back, dropping the loved one to climb "
        "when chased, and the hated twin is often the Magic Animal. He must "
        "catch the mother and take the hated twin with no magic, harming no "
        "monkey (p. 47).",
        pithecousa,
    )
    _seed(
        b,
        "False Embassy",
        "The characters arrive for the Ceremony of the King's Urination, ideally "
        "with gifts, and meet the Embassy from Furthest Hind, exotic monkeys "
        "eager for their friendship (p. 47).",
        pithecousa,
        secrets="They are shapechanged serpents sent by the King of Punt, the "
        "Egyptian name for Soqotra (Rival Magic ch. 5), to kill the King of "
        "Monkeys. Punt's mighty serpent king has further plans.",
        antagonist="The King of Punt",
    )
    _seed(
        b,
        "The Descent of Man",
        "The island's change works rather like the heartbeast, and a heartbeast "
        "form avoids it, so it may be an Ancestor Site of House Bjornaer (Houses "
        "of Hermes: Mystery Cults p. 25). The Ritual of Twelve Years at the "
        "King's court might yield apprentices with exotic African heartbeasts, "
        "but the King will object, and the characters may be sent to win him "
        "over or evict him (p. 47).",
        pithecousa,
    )


def _empire_stories(b: Builder, cities: dict[str, Neighbour]) -> None:
    marrakesh, tunis = cities["marrakesh"], cities["tunis"]
    _seed(
        b,
        "A New Ruler",
        "A cousin of the ruler, in Marrakesh or a prisoner in Christian lands "
        "since Las Navas de Tolosa, asks the characters to clear his way: kill "
        "rival claimants unblamed, place their own appointees, and hold the "
        "empire together long enough for him to repay them (p. 51).",
        marrakesh,
    )
    _seed(
        b,
        "Aiding a Governor",
        "With no clear successor, magi can serve a governor without open war: "
        "spying, sabotage, improving his economy, striking at weak moments, and "
        "finish with friends in the new capital of North Africa (p. 51).",
        marrakesh,
    )
    _seed(
        b,
        "Invited In",
        "Desperate for their economy, the Almohads settle Christians and some "
        "Jews in Fes and seek treaties with Christian kings. A cousin of the "
        "ruler sends a redcap to say dhimmi magi would be welcome in Fes's "
        "foreign quarters. Skilled diplomats could win the right to settle "
        "elsewhere and money besides, more if they reclaim places like the Rif "
        "(pp. 51-52).",
        cities["fes"],
    )
    _seed(
        b,
        "Revenge Against the Order",
        "House Flambeau hints it had a hand, perhaps with God's, in Las Navas de "
        "Tolosa, where up to 150,000 Muslims fell against some 2,000 Christians, "
        "mostly of fighting Orders it finds inconvenient. Whether or not it did, "
        "Hermetics in Morocco stand in the lands of men who want revenge; those "
        "who claim the Order find allies among the empire's gnawing enemies "
        "(p. 52).",
        marrakesh,
    )
    _seed(
        b,
        "Rebellious Governor",
        "If history holds the governor of Tunis rebels most successfully. The "
        "Hafsids must keep several things going their way, and magi backing them "
        "will be busy (p. 55).",
        tunis,
        antagonist="The Hafsids",
        stages=[
            b.stage(
                "The Almohad Navy",
                at=1,
                clues="Its sailors are also a great force of light infantry.",
                ignored="No rebellion is possible while its captains stay loyal.",
                stopped="Captains die or are lured away: ambush on land is easy "
                "but suspicious; defeat at sea is harder but easier to hide.",
            ),
            b.stage(
                "Trade with Italy",
                at=2,
                clues="Desert goods pay for armies; Tunis eats Sicilian wheat.",
                ignored="A year's disruption ends the attempt: the people "
                "starve, riot and follow anyone who can feed them.",
                stopped="Travel to the sources, clear supply, deal with the "
                "Italians; in history their embassies come soon after 1220.",
            ),
            b.stage(
                "Conquer Tripoli",
                at=3,
                clues="Weak navy, poor hinterland, more reliant on wheat than Tunis.",
                stopped="A six month blockade may starve out its Almohad "
                "governor; holding it needs a trustworthy governor and diplomacy "
                "or war with the desert tribes.",
            ),
        ],
    )
    _seed(
        b,
        "The Serpent of Bagradas River",
        "Stories of the great serpent lead magi seeking a covenant site to the "
        "river mouth north of Tunis, where they may meet lesser serpents, the "
        "ghosts of Roman soldiers, or their reanimated bodies (p. 55).",
        tunis,
    )
    _seed(
        b,
        "Lost Virgilian Magics",
        "Notes point to Soussa, whose mosaics and auras hint at an unknown cabal "
        "of Virgilian sorcerers of Hadrumetum who hid texts and works in the "
        "catacombs from the Arabs. Someone else is searching too: sahirs, "
        "infernalists, renegades or the Augustan Brotherhood (p. 56).",
        cities["catacombs"],
    )


def _cyrenaica_stories(
    b: Builder,
    cyrenaica: dict[str, Neighbour],
    islands: dict[str, Neighbour],
    maghreb: Neighbour,
    atlas: Neighbour,
) -> None:
    region = cyrenaica["cyrenaica"]
    _seed(
        b,
        "To Claim a Wife",
        "Any man who survives a night with the jinn of the mosque south of Girba "
        "may take one of their wives. Tasks vary: strength, riddles, finding a "
        "misplaced thing, a story they have not heard. Failures serve them seven "
        "years. The wives, jinn or human slaves, stay beautiful even after they "
        "leave (p. 57).",
        islands["djerba"],
    )
    _seed(
        b,
        "Cyclopskin Handiwork",
        "Earthquakes shake Malta, and some blame the cyclopskin at war under the "
        "ground. Can the giants be convinced to stop before the cities fall "
        "(p. 58)?",
        islands["malta"],
    )
    _seed(
        b,
        "The Remains of the Day",
        "The pharos of Apollonia holds a wrecked laboratory and a fresh corpse "
        "(p. 59).",
        cyrenaica["pharos"],
        secrets=paragraphs(
            "The dead man is Diurnum Lumen of Flambeau, left behind from a "
            "Jerbiton-led Theban settlement abandoned under ten years ago. He "
            "was rebuilding the pharos to recover the Lineage of Abydaros, a lost "
            "African mystery cult of Apollo with powers from sunlight.",
            "His killer may be Glaucus, a murderous Makhai (the Theban Muspelli "
            "of Rival Magic), who serves the sea Titan Okeanos and his monsters "
            "and has moved on. Magi who settle here may rebuild the experiments "
            "and invite his return.",
        ),
        antagonist="Glaucus",
    )
    _seed(
        b,
        "An Acquired Menagerie",
        "Norman knights and a powerful Jerbiton magus track Muqadam, meaning to "
        "put him in the Tower of London's menagerie, where he would likely die "
        "of shame. Do the characters help him quietly and win his respect, or "
        "side with the Jerbiton (p. 61)?",
        maghreb,
    )
    _seed(
        b,
        "The Rogue Vassal",
        "A Lion of Virtue, Syyd, is killing every man he can find at the edge of "
        "the Great Desert. Will the magi ask Muqadam to give him up, or find a "
        "way to take Syyd's arcane connection from him (p. 61)?",
        maghreb,
        secrets="A demon has preyed on Syyd's solitude and led him step by step "
        "to feel justified in killing.",
        antagonist="Syyd",
    )
    _seed(
        b,
        "When Shallots Will Simply Not Suffice",
        "A Gastronomer, hoping to host the Millenial Feast of 1248, secretly "
        "wants true silphium. He may be the head cook of Valnastium, a "
        "food-minded magus of Normandy or the hedge magician Gervais d'Avignon; "
        "all three may hire rival teams, or the same people (p. 63).",
        region,
    )
    _seed(
        b,
        "End of the Line",
        "Silphium could shake the feudal order: lords depend on serfs' children, "
        "the Church calls contraception sin, and meddling magi could end noble "
        "lines, with no sigil to trace. Tremere may act to stop its recovery, "
        "hoard it, or bargain with Mercere (p. 63).",
        region,
    )
    _seed(
        b,
        "Uninvited Guest",
        "A Bear of Virtue, driven out by newly arrived Tuareg, has made a den of "
        "a vital cache or vis site. Can the Tuareg or the Bear move? She is "
        "about to bear cubs (p. 64).",
        atlas,
    )
    _seed(
        b,
        "Lost Legacy",
        "A Bjornaer seeks a beast of Virtue to learn of pre-Hermetic "
        "shapeshifters through the shared Vandal past. Gothic lineages and "
        "hidden clans may roam the Maghreb, unwittingly awaiting reunion or "
        "confrontation with the Bjornaer (p. 64).",
        atlas,
    )
