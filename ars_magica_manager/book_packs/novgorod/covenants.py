"""The four covenants The Dragon and the Bear describes (ch05), rebuilt
rather than converted (N7): each keeps the book's site, season, founding,
aura, members, library summae, vis store and supply, allies and items,
drops the Fourth Edition point totals, and takes Boons and Hooks from the
Covenants catalog as lines in what_matters. The two covenants the book
leaves blank (p. 109) are counted on the roster, not made.

Keys: covenants["three_lakes"] (on places["three_lakes_site"]),
["thousand_caves"] (["thousand_caves_site"]), ["pripet_maior"]
(["pripet_island"]) and ["leczyca"] (["leczyca_ridge"]).

The magi (N6): the members the book lists, Barchek Ocowski, the unGifted
Redcap, among them; Yannes Kolski, vanished in 1216, belongs to no
covenant now (magi["yannes"]). Stolitzya the Swimmer is a creature of the
marsh, not a member (N8; bestiary.py). Ages the book gives are kept; the
rest are assumed in stats_magi.py's profiles. The apprentices (Mina,
Ratibor, Dankya, Kassim and Janek) and the girl Stenya are named in their
masters' and covenant's summaries. Magi are sketches here; stats_magi.py
converts the nine printed blocks and generates everyone else's.

Volkhvy (N11): Rehamchi and Lelya Danichev are magi of Ex Miscellanea
who also belong to the Volkhvy tradition (trad_volkhvy, Realms of Power:
Faerie)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...models.world import FULL
from ..builder import joined_lines, paragraphs, titled

if TYPE_CHECKING:
    from ...models import Character, Covenant, Tribunal
    from ..records import Records

GUERNICUS = "house_guernicus"
JERBITON = "house_jerbiton"
EX_MISC = "house_ex_miscellanea"
BJORNAER = "house_bjornaer"
MERCERE = "house_mercere"
MERINITA = "house_merinita"
VERDITIUS = "house_verditius"
BONISAGUS = "house_bonisagus"
FLAMBEAU = "house_flambeau"
TREMERE = "house_tremere"
CRIAMON = "house_criamon"
VOLKHVY = "trad_volkhvy"

#: (key, name, House, age the book gives or None, summary).
Member = tuple[str, str, str, int | None, str]


def build(records: Records) -> None:
    tribunal = records.tribunal
    if tribunal is None:
        return
    _three_lakes(records, tribunal)
    _thousand_caves(records, tribunal)
    _pripet_maior(records, tribunal)
    _leczyca(records, tribunal)
    records.magi["yannes"] = records.b.magus(
        "Yannes Kolski",
        covenant=None,
        house=CRIAMON,
        age=127,
        summary=YANNES,
    )


def _members(
    records: Records,
    covenant: Covenant,
    members: tuple[Member, ...],
    traditions: dict[str, list[str]] | None = None,
) -> None:
    for key, name, house, age, summary in members:
        character: Character = records.b.magus(
            name,
            covenant=covenant,
            house=house,
            age=age,
            summary=summary,
            traditions=(traditions or {}).get(key),
        )
        records.magi[key] = character


# ----------------------------------------------------------- Three Lakes


def _three_lakes(records: Records, tribunal: Tribunal) -> None:
    b = records.b
    covenant = b.covenant(
        "Three Lakes",
        tribunal=tribunal,
        founded=1012,
        place=records.places["three_lakes_site"],
        aura=4,
        season="Autumn",
        detail=FULL,
        aegis=35,
        summary=paragraphs(
            "The guiding covenant of the Tribunal, where it meets: its "
            "political heavyweights shore up Leczyca in Poland, its "
            "Quaesitores turn back the Rhine's and Transylvania's claims, "
            "and it keeps the Tribunal's Redcaps. Its device is a golden "
            "sunburst in a triangle of three blue ovals.",
            "To its neighbours it is the home of a prosperous trading "
            "family, the Beslavichi: old Yury Beslav the patriarch and his "
            "son Georgi, who runs the trade, both Gently Gifted Jerbiton "
            "magi. Reindeer herds, sleds and carts carry its trade across "
            "north Russia and the Baltic, and it has grown rich and well "
            "connected by it.",
            "A wooden stockade holds three parts: the Trade Yard of "
            "warehouses, reindeer stables and sled yard; the High House "
            "with its Great Hall, for specialists, favoured grogs and "
            "guests; and the stone Keep above, with the library, treasury "
            "and the magi's quarters. A Hermes Portal joins it to Leczyca.",
            "Customs. Its magi have three grades: Juniors, probationers who "
            "surrender their sigils and have no voice; Specialists, full "
            "members who give up voting and office for research, owing a "
            "season a year of teaching or writing; and Seniors, who carry "
            "the covenant's duties and alone vote. Up to three magi are "
            "away at a time.",
            "Late Autumn. At its bicentenary in 1212 the magi found no "
            "apprentice had passed a Gauntlet there in thirty-five years; "
            "Boris, at seventy-six, is the youngest by fifteen. Four "
            "apprentices have been taken since and are trained by the "
            "covenant together, all year round: Mina Dankovna (Yury's), "
            "Ratibor Peslav (Zashya's), Dankya Yostovna (Susan's) and Kassim "
            "ibn Fadal of Great Bulgar (Olga's). On Thousand Caves the "
            "covenant is divided, excited and afraid at once.",
        ),
        what_matters=joined_lines(
            "Vis stores: 300 pawns (Animal 30, Aquam 30, Auram 20, Corpus 10, Creo 20, Herbam 45, Ignem 20, Imaginem 15, Intellego 10, Mentem 30, Muto 5, Perdo 10, Rego 5, Terram 40, Vim 10)",
            "Vis: 50 pawns a year (Animal 5, Aquam 8, Auram 4, Corpus 4, Herbam 15, Mentem 4, Terram 10)",
            "Income: 700 silver pennies a year above its costs; supplies worth 7,000 a year",
            "Library: spells of about 3,000 levels, most in InMe, ReMe and MuCo; Aegis 35. Summae: Animal L16 Q8, Herbam L18 Q8, Intellego L20 Q9, Mentem L23 Q9, Rego L19 Q10, the rest about L15 Q7. Mundane: Hermetic Law L6 Q7, travellers' tales, Nordic lore, maps of the north and the Baltic, merchant law, Russian chronicles and the Tribunal's records",
            "Covenfolk: 10 magi, 40 specialists, 100 grogs, 50 herders, drovers, trappers and servants",
            "Enchantments: the Hermes Portal to Leczyca; ten sleds with runners of Veneer of Smooth Riding; twenty swords and spears for favoured grogs (Edge of the Razor); the Eye of Magic, a great faceted crystal Nicollo and Pavel made over three years to study cryptic magics and watch for magic coming near",
            "Laboratories: good throughout (+1)",
            "Allies: Leczyca. Contacts: six merchants in north Russia and the Baltic",
            "Enemies: trade rivals in Novgorod; a minor Rhine covenant and a minor Transylvanian one",
            "Reputations: good neighbours to local peasants and lords; suspect to the local clergy; formidable in the Order",
            "Boon: Mystical Portal (the Hermes Portal to Leczyca)",
            "Boon: Secondary Income (the Beslavichi's trade)",
            "Boon: Prestige (the Tribunal's guiding covenant)",
            "Boon: Informants (merchant agents across the north)",
            "Hook: Hermetic Politics (the Tribunal's quarrels come to its council)",
            "Hook: Hermetic Services (the Quaesitores and the Redcaps)",
            "Hook: Mundane Politics (the Royal Embargo and Novgorod's princes)",
            "Hook: Infants (four apprentices trained together)",
        ),
        secrets=[
            titled(
                "Zashya Miyovna's secret",
                "Zashya Miyovna has a daughter by a Rurikid prince, and her "
                "granddaughter is Nastassia Baramov of Thousand Caves.",
            ),
        ],
    )
    records.covenants["three_lakes"] = covenant
    _members(records, covenant, THREE_LAKES)


THREE_LAKES: tuple[Member, ...] = (
    (
        "andrei",
        "Andrei Soitkchin",
        GUERNICUS,
        122,
        "Senior, chief Quaesitor of the Tribunal and chairman of Three "
        "Lakes' council, who sees that its magi keep its detailed charter "
        "and the Code. Patient, scrupulous, severe and famed for humourless "
        "impartiality. His first task is to discipline Pripet Maior for its "
        "raid, which is proving all but impossible. He specializes in "
        "truth, lie-detection and compulsion, and escapes trouble by "
        "invisibility, teleportation and mind domination.",
    ),
    (
        "pavel",
        "Pavel Chedyav",
        GUERNICUS,
        None,
        "Senior, the junior Quaesitor and Andrei's evident successor, "
        "which pleases him. An ingenious magus and a fine laboratory "
        "worker, he sees the Thousand Caves debate as an intellectual "
        "puzzle. He came from Leczyca about fifty years ago, leans to "
        "Poland, wants the Polish realm reunited and the Tribunal moved out "
        "of Russia, and resents the Royal Embargo though he keeps it. He "
        "helped Nicollo make the Eye of Magic.",
    ),
    (
        "yury",
        "Yury Beslav",
        JERBITON,
        117,
        "Senior and the covenant's public face, patriarch of the "
        "Beslavichi: a traditional Jerbiton in district politics, trade "
        "and the patronage of artists, a part he has played so long it is "
        "no act. He shaped the Royal Embargo after finding that no "
        "friendship with a prince stays small. His magic works only in the "
        "company of two or more people, so he keeps grogs in his "
        "laboratory and scribes at his secret meetings. Apprentice: Mina "
        "Dankovna.",
    ),
    (
        "georgi",
        "Georgi Yurivich",
        JERBITON,
        None,
        "Senior, Yury's son, apprentice and heir, with magic much like "
        "his father's. For thirty years he has run the trading journeys, "
        "often in Ladoga and Novgorod or on the northern trails meeting "
        "agents and informants. He found and named the Valley of a "
        "Thousand Caves more than forty years ago and led Malincka there "
        "in 1182; she is his friend, and her work now troubles him. Having "
        "aged too little for the mundanes who know him, he wears an "
        "enhanced Disguise of the New Visage and turns awkward questions "
        "aside with Mentem.",
    ),
    (
        "batiba",
        "Batiba an Khatiba",
        EX_MISC,
        None,
        "Senior, the one member who is not a Hermetic magus: a Cuman "
        "shaman who worships his ancestors and the spirits of earth and "
        "sky, brought from the steppe by Georgi about fifty years ago and "
        "joined to the Order as a hedge wizard. The Quaesitores made him "
        "their authority on pagan matters and a pillar of the "
        "delegation. He is enthusiastic for Thousand Caves, which is "
        "nearer the society he knows than the Order is, and longs to spread "
        "word of it among Ex Miscellanea; so far he has been restrained, "
        "just.",
    ),
    (
        "zashya",
        "Zashya Miyovna",
        BJORNAER,
        119,
        "Senior and the Tribunal's senior Bjornaer, with a swan "
        "heart-beast; gentle, conciliatory and romantic, wooed by magi and "
        "mundanes alike. On the delegation she tried to reconcile her "
        "House, and was preached at by Thousand Caves and threatened by "
        "Pripet Maior, above all by Miya Cossuri, her mother and parens. "
        "Her complaint at Crintera in 1218 came to nothing. She "
        "specializes in weather and animals. Apprentice: Ratibor Peslav.",
    ),
    (
        "susan",
        "Susan of Wicklow",
        MERCERE,
        None,
        "Senior and chief Redcap of the Tribunal, that rare thing a "
        "Gifted Mercere, of the line of Patrick of Dunderry, whose Russian "
        "students died out sixty years ago. One of the age's great "
        "travellers: she went with Sadko the merchant in the 1160s and "
        "1170s, later with Georgi into the east, from Sweden to "
        "Constantinople. Every year she makes a full circuit of the "
        "covenants without the portal, to keep it hidden, coming home by "
        "the Leap of Homecoming. Apolitical, proud of the Redcaps. She "
        "says she saw Stolitzya about fifteen years ago. Apprentice: Dankya "
        "Yostovna.",
    ),
    (
        "olga",
        "Olga Deiaslavl",
        MERINITA,
        None,
        "Specialist, wholly taken up with the Slavic faeries; it is "
        "doubtful whether her loyalty is to the covenant or to them, and "
        "she is the likeliest to leave, by Twilight, age or Arcadia. A "
        "famous teacher, generous on Faerie Lore and Etiquette, her summae "
        "and questions the library's pride, but secretive about her "
        "spells. Rumour says she has solved faerie time, can wipe away "
        "fatigue, and siphons Might from friendly faeries. She is "
        "dismissive of Thousand Caves. Apprentice: Kassim ibn Fadal.",
    ),
    (
        "boris",
        "Boris Davidovich",
        BJORNAER,
        76,
        "Specialist, the youngest magus, Zashya's filius, with a bear "
        "heart-beast; a bad Twilight twenty years ago left him huge and "
        "covered in wiry brown hair. He believes animals have legends that "
        "may hold the wisdom of the world before man, has sought beast "
        "lords in Arcadia and griffins, chimeras, pegasi and unicorns in "
        "the wild, and records all he finds. He would not join the "
        "delegation, though he went with Zashya to Crintera.",
    ),
    (
        "nicollo",
        "Nicollo Parelli",
        VERDITIUS,
        None,
        "Specialist, brought from the Roman Tribunal nearly seventy-five "
        "years ago when the council wanted a Verditius; fat, easygoing and "
        "fond of his comforts, famed for ingenious laboratory work, and "
        "able to lure even proud Pavel into assisting him. Untested in "
        "violence or politics, he is beginning to feel he must speak: "
        "drawn to Thousand Caves' experiment, yet in sympathy with the "
        "vis-hungry western Tribunals. He made Andrei's cloak and Zashya's.",
    ),
)


# --------------------------------------------------------- Thousand Caves


def _thousand_caves(records: Records, tribunal: Tribunal) -> None:
    b = records.b
    covenant = b.covenant(
        "Thousand Caves",
        tribunal=tribunal,
        founded=1185,
        place=records.places["thousand_caves_site"],
        aura=6,
        realm="Faerie",
        season="Summer",
        detail=FULL,
        aegis=35,
        summary=paragraphs(
            "A covenant in the caves of a gorge on the western Urals, its "
            "device a labyrinth, and the head of a small confederation of "
            "pagan tribes: the valley folk farm, herd, hunt and fish, while "
            "bands in the forests about live by hunting, trapping and "
            "slash-and-burn, using almost no metal and killing nothing "
            "needlessly. The magi are the clan's acknowledged leaders and "
            "have deepened the old Slavic bonds with the local beasts and "
            "faeries, so that the covenant is ringed by friends. Its "
            "people live with late iron-age tools; a good sword is a great "
            "prize.",
            "Heart-beasts. Nearly thirty of its folk have avian "
            "heart-beasts and thirty more other beasts, which the Bjornaer "
            "think the strong Slavic aura has quickened; Nastassia has led "
            "the search for them.",
            "The great work. The covenant admits Volkhvy, affiliated to "
            "Ex Miscellanea and taught Hermetic magic, and follows "
            "Malincka's reasoning that tempering an aura needs three "
            "things: a Hermetic Great Ritual, which she is making; the "
            "willing part of many mundanes, which its people will give; "
            "and a great faerie 'divinity' to bless it. For thirty years "
            "the magi have preached a revived cult of Hermes, with "
            "festivals and rites and idols in the Great Cavern's sanctum, "
            "hoping to bring Hermes back as that god. Lately there are "
            "surges of magic and ecstatic dreams, and a Gifted girl, Stenya "
            "Vassanovna, Lelya's stepdaughter, says she talks with Lord "
            "Hermes and preaches him persuasively.",
            "The book leaves open whether Malincka succeeds (p. 120): "
            "reconciliation of the two magics; success with a Hermes who "
            "has his own agenda; a partial success that splits the "
            "Tribunal; the Slavic gods roused against her; a demon in the "
            "god's place; Mongol shamans who destroy the covenant after "
            "1223; or a religion Hermetic theory can never grasp.",
        ),
        what_matters=joined_lines(
            "Vis stores: 150 pawns (Animal 25, Aquam 20, Auram 15, Corpus 10, Herbam 20, Imaginem 15, Intellego 5, Mentem 5, Terram 20, Vim 15)",
            "Vis: 60 pawns a year (Animal 10, Aquam 5, Auram 6, Corpus 5, Herbam 7, Imaginem 5, Intellego 5, Mentem 5, Terram 6, Vim 6)",
            "Income: 700 silver pennies a year in debt, for parchment, glass and ink",
            "Library: spells of about 1,200 levels (CrVi, InVi, MuVi; Malincka's aura spells, Nastassia's shapechanging, Nastassia's and Yakim's CrIg, Basyl's faerie CrIm and ReIm); Aegis 35. Summae of every Art at L5 Q5; Malincka's four tractatus (Vim Q5 and Q6, Intellego Q7 and Q5). Mundane: Legend Lore (Slavic) L8 Q6, Legend Lore (Greek) L5 Q5, Magic Theory L7 Q5; Volkhv ritual, folklore and magic; a copy of the Yannes Discourse",
            "Covenfolk: 8 magi and 175 tribesfolk; room for 200",
            "Enchantments: a Cloak of Feathers; two Fire Javelins (as Pilum of Fire)",
            "Laboratories: six poor (-1), one good (+2)",
            "Allies: the local villages, faeries and animals",
            "Enemies: Pripet Maior",
            "Reputations: formidable and benevolent to the local villages; radical among the Tribunal's covenants",
            "Boon: Hedge Tradition (the Volkhvy)",
            "Boon: Mystical Allies (the faeries and beasts about the valley)",
            "Boon: Loyal Covenfolk (the tribes)",
            "Boon: Natural Fortress (caves reached by ledge, ladder or wing)",
            "Hook: Pagans (a revived cult of Hermes)",
            "Hook: Faerie Aura (Slavic Faerie 6)",
            "Hook: Rival (Pripet Maior)",
            "Hook: Indigenes (a confederation of tribes)",
        ),
    )
    records.covenants["thousand_caves"] = covenant
    _members(
        records,
        covenant,
        THOUSAND_CAVES,
        traditions={"rehamchi": [VOLKHVY], "lelya": [VOLKHVY]},
    )


THOUSAND_CAVES: tuple[Member, ...] = (
    (
        "malincka",
        "Malincka Capcek",
        BONISAGUS,
        70,
        "The covenant's ideological leader, a Hungarian Bonisagus. Thirty-"
        "five years ago, in a Twilight while watching a Great Ritual, she "
        "saw why four centuries of Hermetic attempts on auras failed: the "
        "power needs magical ritual, a fount of faerie power and, she "
        "believes, mundane people to channel it. Her aims: a Hermetic "
        "Great Ritual that tempers auras; an aura that gives magi what a "
        "Slavic aura gives Volkhvy, and at last one aura for both; Volkhv "
        "Disciplines broadened like Arts with quick formulaic forms; and "
        "the force behind domestic magic, for her own covenfolk. Her "
        "aura-making and aura-reading spells are her own. Compassionate, "
        "impetuous, proud of her House.",
    ),
    (
        "nastassia",
        "Nastassia Baramov",
        BJORNAER,
        54,
        "'The Firebird', Malincka's second, with the force of character "
        "her leader lacks: a Bjornaer with an eagle heart-beast and a rare "
        "bent for Ignem, obsessed since childhood with the Firebird, whose "
        "lore she has hunted far and toward whose form her own spells "
        "reshape her eagle. She shocked Pripet Maior at her Gauntlet at "
        "Three Lakes, the day before Thousand Caves was chartered, by "
        "showing a heart-beast limned in flame. The most serious of the "
        "magi in the worship of Hermes and a devotee of Khors, leader of "
        "the search for heart-beasts among the tribes. Yakim is her lover. "
        "Casimi Ljech nearly killed her in 1217. She does not know who her "
        "grandmother is.",
    ),
    (
        "rehamchi",
        "Rehamchi Danichev",
        EX_MISC,
        71,
        "The valley's senior Volkhv, a priest of Khors, who leads every "
        "rite but the new ones and privately counts himself the "
        "community's real leader, teaching the magi the truth about the "
        "world. He has learned enough Latin and theory to be a magus of "
        "Ex Miscellanea. A new god is a foolish idea, he thinks, which the "
        "gods will find amusing; yet Nastassia found his swallow "
        "heart-beast, and Stenya's preaching has begun to convince him. He "
        "may seek a great Prophecy.",
    ),
    (
        "lelya",
        "Lelya Danichev",
        EX_MISC,
        None,
        "Rehamchi's daughter, a Volkhv raised among the magi, firmer in "
        "Hermetic method than her father and keener on Malincka's "
        "project; stepmother to Stenya. Impatient to make her mark, she "
        "will move at the next meeting that the Tribunal condemn the "
        "Order's attitude to the Volkhvy, and wants revenge for the raid: "
        "she has practised certamen for three years to force a formal "
        "apology from Pripet Maior.",
    ),
    (
        "basyl",
        "Basyl Karrimichi",
        MERINITA,
        None,
        "A frivolous prankster with many faerie friends, who will not "
        "take research or study seriously; the least use to Malincka. Only "
        "his visions sober him: intense and exhausting, they strike at the "
        "peak or trough of his seasonally cycling magic, and for five "
        "years they have shown the coming of Hermes, so baroque that no "
        "one can read them.",
    ),
    (
        "otto",
        "Otto Rattstein",
        BJORNAER,
        None,
        "An enigma: an elderly Bjornaer of the lynx, once of standing at "
        "Crintera, who arrived a little over ten years ago and was "
        "admitted though suspected of being a spy. He lives among the "
        "camps and villages and takes no part in the research or the "
        "preaching. In 1214 he made the Tribunal give Malincka a hearing "
        "without endorsing her; in 1217 he held the Great Cavern and drove "
        "off Casimi Ljech, yet he would not lay charges at Crintera. He "
        "defends his sodales' rights but will not punish Bjornaer.",
    ),
    (
        "yakim",
        "Yakim ibn Rassur",
        FLAMBEAU,
        None,
        "Born in Great Bulgar, sold to Greek merchants as a child and "
        "found Gifted in Constantinople by a notoriously cruel Theban "
        "Flambeau, whose welts he still bears. After his Gauntlet he fled, "
        "rode a year with the Cumans, and in Great Bulgar spent six years "
        "studying theology, medicine and philosophy with the scholar "
        "Haroun Hashemi, recovering his youthful zest. He met Malincka in "
        "1209 and joined in 1211; outgoing and genial, he is her chief "
        "theoretical partner. Nastassia's lover; she is sure he has a "
        "deeply buried heart-beast.",
    ),
    (
        "narina",
        "Narina Cheminov",
        BJORNAER,
        None,
        "Stolen at six by her parens, a very old Bjornaer of the horse who "
        "lived his last twenty-five years as a hermit in the Urals, and "
        "taught by him from fifteen; her Hermetic magic is eccentric, poor "
        "at Penetration, Finesse and certamen, strong in animals, the "
        "wild and healing. She could not read Latin when she came ten "
        "years ago and still finds communal life hard. Friend of every "
        "local animal, she hates Pripet Maior above all for the raid's "
        "harm to them.",
    ),
)


# ----------------------------------------------------------- Pripet Maior


def _pripet_maior(records: Records, tribunal: Tribunal) -> None:
    b = records.b
    covenant = b.covenant(
        "Pripet Maior",
        tribunal=tribunal,
        founded=993,
        place=records.places["pripet_island"],
        aura=6,
        season="Winter",
        detail=FULL,
        aegis=40,
        summary=paragraphs(
            "The oldest covenant of the Tribunal, founded by Transylvania "
            "and home of House Bjornaer's strongest bond in the east: twice "
            "a refuge for Grand Silesia's magi, many of whom stayed. Its "
            "device is a house on stilts above a reed bed. In its Autumn, "
            "about 1110 to 1165, it was second only to Crintera in the "
            "House, and its Roslav Lavickovich was Primus for almost thirty "
            "years from 1147. Crintera would still help it in a crisis.",
            "Now it is in Late Winter. Its founders are dead or lost to "
            "Final Twilight; its five magi, most of them Stolitzya's old "
            "apprentices, range from old and feeble to one step from Final "
            "Twilight, sinking into their beasts and into senility. No "
            "apprentice in eighty-five years, no new member in seventy. "
            "They have given up scholarship and curiosity and spend their "
            "lore on defending the marsh. Three or four still attend the "
            "Tribunal, whose meetings they gave up to Three Lakes forty "
            "years ago.",
            "The island's living palaces rot. Supplies came from the marsh "
            "and the rest was bought; now the magi and covenfolk steal what "
            "they need, and the vis harvests dwindle because no one makes "
            "the effort. Beasts and faeries shun the covenant, the marsh "
            "peasants fear and hate it, and much of the trappers', "
            "iron-dredgers' and fishers' misfortune is indeed its doing. The "
            "Boyar Mikhail of Turov means to dig canals, drain the land, and "
            "deal firmly with whoever objects.",
        ),
        what_matters=joined_lines(
            "Vis stores: 400 pawns (Animal 40, Aquam 50, Auram 10, Corpus 10, Creo 45, Herbam 5, Ignem 10, Imaginem 10, Intellego 15, Mentem 15, Muto 45, Perdo 25, Rego 10, Terram 40, Vim 25)",
            "Vis: 30 pawns a year (Animal 3, Aquam 7, Creo 5, Herbam 7, Muto 5, Terram 3), once far more",
            "Income: 350 silver pennies a year in debt; 3,500 owed",
            "Library: spells of about 1,200 levels (MuCo; weather in CrAu, MuAu, ReAu; plants in CrHe, MuHe, ReHe); Aegis 40, its causeway tied to it. Summae: Animal L28 Q11, Corpus L24 Q9, Herbam L20 Q10, Muto L27 Q12; the rest damp and neglected, about L4 Q3. Mundane: over a hundred books of natural philosophy and the liberal arts, all spoilt",
            "Covenfolk: 5 magi, 10 specialists, 25 grogs; room for twice as many",
            "Enchantments: a chalice of pure water; two Feather Cloaks; a swamp skimmer boat",
            "Laboratories: six, all poor (-1)",
            "Allies: Crintera",
            "Enemies: Thousand Caves; the local nobles and peasants",
            "Reputations: venerable in the Tribunal and House Bjornaer; decaying in the Order; evil to the local peasants",
            "Boon: Island (the causeway the Aegis raises)",
            "Boon: Hidden Resources (a store of 400 pawns)",
            "Hook: Crumbling (the living palaces rot)",
            "Hook: Dwindling Resource (vis no one harvests)",
            "Hook: Unhealthy Environment (insects, fever and damp)",
            "Hook: Rival (Thousand Caves)",
            "Hook: Infamous (to the marsh's peasants)",
        ),
        secrets=[
            titled(
                "Miya Cossuri's great-granddaughter",
                "Miya Cossuri does not know that Nastassia Baramov of "
                "Thousand Caves, whom the covenant loathes, is her own "
                "great-granddaughter.",
            ),
        ],
    )
    records.covenants["pripet_maior"] = covenant
    _members(records, covenant, PRIPET_MAIOR)


PRIPET_MAIOR: tuple[Member, ...] = (
    (
        "yellina",
        "Yellina Ozwry",
        BJORNAER,
        139,
        "The covenant's leader, which means only that she is the most "
        "lucid of its magi; otter heart-beast. Deaf these five years, she "
        "reads lips with a small spell. She is ever surer that her parens "
        "Roslav Lavickovich, dead nearly fifty years, still watches over "
        "them from Crintera. Stubbornly conservative, she would avoid a "
        "fight herself but sees nothing wrong in attacking mundanes, and "
        "thinks Thousand Caves a hideous betrayal. Close to Final "
        "Twilight, with magic gone chaotic, she is wary with it.",
    ),
    (
        "vlachs",
        "Vlachs von Hasstein",
        BJORNAER,
        None,
        "An osprey, who came from Bavaria nearly a century ago and joined "
        "Pripet after his Gauntlet at Crintera, when it was at its "
        "height. His memory of the present fails, and a dozen times a day "
        "he sees the covenant 'suddenly' in ruins, which can bring on "
        "fits. A watchful, aggressive sentinel, he strikes interlopers as "
        "an Avenging osprey or with storms, and steals what the covenant "
        "needs from distant towns, shrunk by magic. A bad Twilight took "
        "his Gentle Gift; he now disturbs the beasts he loves, and it "
        "eats at him.",
    ),
    (
        "casimi",
        "Casimi Ljech",
        BJORNAER,
        152,
        "The most plainly dangerous: a big, blustering Pole whose water-ox "
        "heart-beast leaves him almost no reason, and who shifts without "
        "warning between his forms and may stick in one. His longevity "
        "potion failed three years ago and he cannot brew another; he "
        "ages and has a few years left, and his next Twilight will be his "
        "last. He led the raid of 1217 and almost killed Nastassia, and "
        "ignores every summons from Three Lakes and Crintera. He prowls "
        "the marsh as an ox, terrorizing villagers and fighting its beasts "
        "and faeries, magic resistant and very strong: a Twilight made his "
        "Form of the Avenging Beast permanent. About a year younger than "
        "Miya.",
    ),
    (
        "miya",
        "Miya Cossuri",
        BJORNAER,
        153,
        "A heron, and by a year the eldest magus of the Tribunal, so its "
        "Praeco by the rule (the book names none). Her mind is sounder than "
        "Casimi's but her body fails; she rarely leaves her reed palace, "
        "the soundest building on the island, and spends her waning power "
        "on it. It is a menagerie of waterfowl, beaver, otter, snake, "
        "lizard and water-deer, none caged, kept at peace by her great "
        "ReAn spell; the beasts, larger and cleverer after generations "
        "there, will defend her. A sweet, ancient lady without malice, "
        "lost in the world beyond her marsh, and the likeliest host for a "
        "Redcap. Zashya Miyovna's mother and parens.",
    ),
    (
        "lev",
        "Lev Deniki",
        BJORNAER,
        None,
        "A water serpent, and the deadliest of them behind a pleasant, "
        "moderate mask. Mounting paranoia makes the whole world a threat; "
        "he talks with every visitor and ambushes any he judges dangerous "
        "as they leave the marsh. At heart a coward: hard resistance makes "
        "him flee, and cornered he is easily cowed.",
    ),
)


# --------------------------------------------------------------- Leczyca


def _leczyca(records: Records, tribunal: Tribunal) -> None:
    b = records.b
    covenant = b.covenant(
        "Leczyca",
        tribunal=tribunal,
        founded=1052,
        place=records.places["leczyca_ridge"],
        aura=4,
        season="Autumn",
        detail=FULL,
        aegis=30,
        summary=paragraphs(
            "A strong, well-built castle on its ridge, with a large outer "
            "bailey, stables and a tilting run; its device is a quill, "
            "point up, with a sword's hilt. Founded by Grand Silesia's "
            "survivors, it is the Tribunal's only covenant in Poland and "
            "the most at odds with the older Tribunals.",
            "Its powerful turb is trained to harry Rhine interlopers, and "
            "it is always ready for siege: it has outlasted more than one "
            "Wizard's War. Its outlook is Poland's toward the Germans: it "
            "was the Germans who betrayed the Order in the Schism War and "
            "squandered their vis, yet they call innocent Leczyca "
            "treacherous. The quarrel came with Grand Silesia's desertion "
            "of the Rhine, and Durenmar has never forgiven it: at every "
            "Grand Tribunal it moves to reassess the eastern border. "
            "Crintera and Irencillia have made their peace. Three Lakes "
            "counts Leczyca its first line of defence and keeps the Hermes "
            "Portal open to it.",
            "Indifferent to Thousand Caves, Leczyca most resents the Royal "
            "Embargo: it feels for the Polish nobles, and about 1190 paid a "
            "heavy fine for helping Silesian nobles against German raids. "
            "Merchant contacts bring it news of roads and armies and a "
            "share in their ventures. Its argumentative magi are held "
            "together by the enemy outside. Kasina and Frania released "
            "their last apprentices two years ago; Ruprecht's apprentice "
            "Janek is the only one there now. The Yannes Discourse is kept "
            "in its library.",
        ),
        what_matters=joined_lines(
            "Vis stores: 200 pawns (Animal 5, Aquam 10, Auram 10, Corpus 15, Creo 10, Herbam 15, Ignem 15, Imaginem 5, Intellego 20, Mentem 15, Muto 5, Perdo 20, Rego 20, Terram 25, Vim 10)",
            "Vis: 60 pawns a year (Auram 4, Corpus 6, Herbam 6, Ignem 6, Intellego 6, Mentem 6, Perdo 8, Rego 8, Terram 10)",
            "Income: 700 silver pennies a year above its costs; 3,500 in hand",
            "Library: spells of about 2,700 levels, mostly destructive and defensive (CrAu, CrIg, PeMe, MuMe, PeCo, MuCo, ReTe, PeTe); Aegis 30. Summae: Creo L17 Q6, Auram L19 Q9, Ignem L16 Q7, Mentem L20 Q10, Perdo L21 Q8, Terram L18 Q8, the rest about L12 Q6, with tractatus on its magi's specialties. Mundane: Civil and Canon Law L8 Q7, Polish chronicles and papal rulings on German-Polish disputes; the Yannes Discourse",
            "Covenfolk: 7 magi, 20 specialists, 100 grogs, 50 covenfolk; room for 8 magi and 150 grogs",
            "Enchantments: the Hermes Portal to Three Lakes; twenty swords and lances of Edge of the Razor",
            "Laboratories: five ordinary, two good (+2)",
            "Allies: Three Lakes, for about twelve weeks a year. Contacts: four merchants",
            "Enemies: Durenmar and lesser Rhine covenants",
            "Reputations: treacherous in the Rhine Tribunal",
            "Boon: Courtyard Castle (concentric walls, gatehouse, watchtower and keep)",
            "Boon: Veteran Fighters (a turb trained against the Rhine)",
            "Boon: Cavalry (its stud, stables and tilting yard)",
            "Boon: Mystical Portal (the Hermes Portal to Three Lakes)",
            "Hook: Tribunal Border (the Rhine claims Poland)",
            "Hook: Rival (Durenmar)",
            "Hook: Fractured Council (argumentative equals)",
            "Hook: Mundane Politics (the Polish nobles and the Embargo)",
        ),
    )
    records.covenants["leczyca"] = covenant
    _members(records, covenant, LECZYCA)


LECZYCA: tuple[Member, ...] = (
    (
        "stanis",
        "Stanis Chechenko",
        JERBITON,
        101,
        "The public leader, a Jerbiton at ease among mundanes and fond of "
        "aristocratic society, a lutist famous among the Polish nobles and "
        "the Count of Leczyca's protégé; but one argumentative equal among "
        "many, often embarrassed when the others will not back his "
        "dealings, and harried by the Tremere. He keeps Leczyca's links "
        "strong, visits the courts of lesser nobles (keeping, it seems, "
        "the ruling on royalty), guides its merchant ventures, and longs to "
        "matter in the Order, writing tirelessly to undermine the Rhine. "
        "Some say Leczyca owes its freedom to its walls, not to him. He "
        "fears cats.",
    ),
    (
        "kasina",
        "Kasina Popovich",
        MERINITA,
        None,
        "One of Gifted twins whose magic is bound together: at a hundred "
        "paces apart it is as normal, and it strengthens as they come "
        "closer and weakens as they part, by about a point in twenty paces "
        "up to five, a Virtue and Flaw together like Cyclic Magic; they "
        "have even had the same Twilights at once. Kasina's magic is wild "
        "and spontaneous and formulaic magic hard for her. Flamboyant, fey "
        "and a wicked practical joker, she outrages staid magi and "
        "applauds Thousand Caves; she cares for faerie and for her sister. "
        "She favours the bow.",
    ),
    (
        "frania",
        "Frania Popovich",
        TREMERE,
        None,
        "Kasina's twin and opposite: a reserved, dignified, forthright "
        "Tremere who respects rank, rules and planning, a student of human "
        "law who fights close when she must, and cannot cast spontaneous "
        "magic. She backs Stanis except when trying to take his place, "
        "keeps Ruprecht in check, and tries to bring order to the "
        "covenant. She long ago reclaimed her sigil. No one has yet beaten "
        "her at certamen.",
    ),
    (
        "tomaszi",
        "Tomaszi Klimowicz",
        VERDITIUS,
        133,
        "The eldest at Leczyca, who claims authority by it without real "
        "ambition. An artisan and enchanter who arms his sodales and the "
        "grogs, and one of the makers of the Hermes Portal. In youth he "
        "made ornaments and insignia for the Polish royal house, and wept "
        "a week when the Order destroyed them and all memory of them. "
        "Irritable and bent by his years in the laboratory, still joyful "
        "in making, he goes to Verdi every few years for the contests.",
    ),
    (
        "ruprecht",
        "Ruprecht de Solange",
        TREMERE,
        69,
        "The covenant's baby, a French noble who came forty years ago to "
        "harden his will. He idealizes the knight, leads the turb, and "
        "enjoys Leczyca's friction, yet chafes that he cannot impose "
        "order; the first step is beating Frania at certamen, which he "
        "has not managed. He reclaimed his sigil fifteen years ago. "
        "Apprentice: Janek.",
    ),
    (
        "sanya",
        "Sanya Tianowicz",
        BJORNAER,
        None,
        "The covenant's one Bjornaer, a badger, 'recommended' by "
        "Crintera's elders fifty years ago: Leczyca feels surer of "
        "Crintera with a Bjornaer in residence, though she seems unaware "
        "of it. Stable, steadfast in a fight, loyal and resolute, a "
        "badger in her home's defence; she joins no faction and cares for "
        "the local animals and the covenant's horses.",
    ),
    (
        "barchek",
        "Barchek Ocowski",
        MERCERE,
        None,
        "The Tribunal's other Redcap, unGifted, who relies on devices the "
        "Leczycan magi made for him. His routes run west: several Rhine "
        "covenants a year (with challenges or rebukes), the "
        "Transylvanian covenants of the northern Carpathians, and once a "
        "year Rome, with messages for Verdi and complaints for Magvillus. "
        "A lean, spry man of peasant stock, funny and tireless, who melts "
        "into any stream of travellers.",
    ),
)


YANNES = paragraphs(
    "The Mad Magus of the East, a Criamon of Leczyca and master of the "
    "Enigma, prone all his life to prophetic visions and small Twilights. "
    "In 1206, at 113, he spent two weeks or more in Twilight prophesying; "
    "Leczyca's notes of it, the Yannes Discourse, are an apocalyptic "
    "morass of verse, cipher, tongues he did not know, and pages where "
    "the scribes could only write 'screaming'. One passage is widely "
    "known: a black serpent born in the northern fells that breaks the "
    "wall of Cathay, burns the Muslims' lands and turns toward him as he "
    "flies up, a dove, into Heaven.",
    "He never cast a spell again, but recovered enough to walk and talk, "
    "and for ten years went from covenant to covenant, and to the "
    "Cumans, reciting that passage with fits, weeping and howling. In "
    "1214 the Quaesitores were asked whether he had passed into Final "
    "Twilight and should be restrained; before they decided he vanished, "
    "in 1216, near Vladimir-in-Suzdalia, after a disruptive visit to "
    "Thousand Caves. His chair at Leczyca stands empty.",
)
