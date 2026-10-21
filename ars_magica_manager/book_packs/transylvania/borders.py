"""Transylvania and its border peoples, as of 1220: the voivodeship and
the Vlach lands round the Carpathians, the Cumans, the Szeklers and the
Pechenegs, the Teutonic Knights in the Burzenland with their five
castles, the Saxons and their seven towns, the Cult of Zalmoxis, the
Bran Pass, Alba Iulia and Câmpulung; the oppida Lycaneon (House
Tremere's first domus magna, with the Portal to Harco and the
manufactory) and the Scholomance (the school in a storm regio), and
their magi; Ludmilla and Sebastian of the Scholomance as companions; in
paraphrase of Against the Dark chapter six.

The hedge traditions (storm wizards, folk witches, taltós, Cuman
shamans) are traditions.py's and are only named here; the dragons, the
white wolves and the faerie queens are the Bestiary's, named in the
places they haunt; the zenodochium in the Bran Pass is fortresses.py's.
Keys: the region is places["transylvania"], with places["maramures"],
["carpathians"], ["burzenland"], ["szeklerland"], ["cumania"],
["bran_pass"], ["lycaneon_mountain"] and ["scholomance_valley"]; the
lords are world["voivode"], world["campulung_voivode"] and
world["burzenland"]; the factions world["teutonic_knights"],
["saxons"], ["szeklers"], ["pechenegs"], ["cumans"], ["vlachs"],
["brodnici"] and ["zalmoxis_cult"]."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...arms import Arms
from ...models.world import FULL
from ..builder import Builder, paragraphs
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Neighbour, Tribunal
    from . import Transylvania

BJORNAER = "house_bjornaer"
EX_MISC = "house_ex_miscellanea"
TREMERE = "house_tremere"
VERDITIUS = "house_verditius"

#: The lead line of an oppidum's notes, before its secrets.
KNOWN_ORDER: dict[str, Any] = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL: dict[str, Any] = {"status": "Known", "known": "In the Tribunal"}
KNOWN_REGION: dict[str, Any] = {"status": "Known", "known": "In the region"}
KNOWN_LOCALLY: dict[str, Any] = {"status": "Known", "known": "Locally"}
RUMOURED: dict[str, Any] = {"status": "Rumoured", "known": "Locally"}

#: The Teutonic Knights' black cross on white.
TEUTONIC_ARMS = Arms("Argent", charge="Cross", charge_tincture="Sable")


def _lines(*lines: str) -> str:
    """The lines as one text, one entry a line."""
    return "\n".join(lines)


def _add(transylvania: Transylvania, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and store it under `key` for the other parts."""
    place = transylvania.b.place(name, **kw)
    transylvania.places[key] = place
    return place


def build(transylvania: Transylvania) -> None:
    b = transylvania.b
    tribunal = transylvania.tribunal
    if tribunal is None:
        tribunal = next(iter(b.saga.tribunals), None)
    assert tribunal is not None, "tribunal.py builds the Tribunal first"
    _region(transylvania)
    _places(transylvania)
    _lycaneon(transylvania, b, tribunal)
    _scholomance(transylvania, b, tribunal)
    _lords(transylvania, b)
    _towns(transylvania, b)
    _factions(transylvania, b)


# ------------------------------------------------------------- the region


def _region(transylvania: Transylvania) -> None:
    _add(
        transylvania,
        "transylvania",
        "Transylvania",
        inside=transylvania.places.get("hungary"),
        summary=paragraphs(
            "The land beyond the forest: a high plateau, on average some "
            "twelve hundred feet up, north and west of the Carpathians, "
            "which bend through the country like a reversed L. It is the "
            "eastern edge of the Kingdom of Hungary, governed for the king "
            "by a voivode, a prince appointed for a few years at a time, "
            "from Alba Iulia. South of the mountains more Vlach country "
            "runs down to the Danube, and east of them, past the Milcov "
            "and below the Cheremosh, hills fall away to plains and the "
            "Black Sea. The Romans called the whole of it Dacia.",
            "Its peoples are many. The Vlachs, who call themselves rumân, "
            "are the oldest; the Hungarian kings have planted others as "
            "guards and settlers: Szeklers and Pechenegs at the passes, "
            "Saxons in seven walled towns, and lately the Teutonic Knights "
            "in the Burzenland, all set against the Cumans who roam "
            "beyond the eastern mountains. Hungarians, Slavs and "
            "Bulgarians live here too.",
            "Hermetically it is the heart of House Tremere's Tribunal: "
            "Lycaneon, the Founder's first domus magna, lies in the "
            "mountains of Maramures in the north, Coeris nearby, and the "
            "Scholomance hides in a storm regio south of Hermannstadt. "
            "Dragons are common enough in the Carpathians to be only an "
            "uncommon sight.",
            "Vis here (each in its place): the Furus brook at Ikafalva "
            "(Aquam, which the Scholomance gathers).",
        ),
        **KNOWN_ORDER,
    )


def _places(transylvania: Transylvania) -> None:
    region = transylvania.places["transylvania"]
    _add(
        transylvania,
        "maramures",
        "Maramures",
        inside=region,
        summary=paragraphs(
            "The northern uplands of the Tribunal, high peaks round "
            "valleys cool in winter and oddly warm in summer. The terrain "
            "kept the Romans out, so the old Dacian rites lasted here "
            "longer than anywhere else in Hungary. Gold, silver, copper, "
            "lead, zinc and salt lie in its mountains, which is what drew "
            "Tremere to found Lycaneon here; Coeris lies in the same "
            "country.",
            "The wolves of these mountains say their forebears were men "
            "who worshipped pagan gods in wolf shape.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        transylvania,
        "carpathians",
        "The Carpathian Mountains",
        inside=region,
        summary=paragraphs(
            "The great range that bends round Transylvania, crossed by a "
            "handful of passes the Hungarian kings guard with settled "
            "peoples. Dragons live here in such numbers that they are "
            "merely uncommon; the local dragon king, Aževastjepan, a "
            "seven-headed zmaj, holds his realm to the Pax Draconis without "
            "mercy and has banished the aždaje from it, with mixed success "
            "(see the Bestiary). No magus has met him and not even other "
            "dragons know his lair, though they speak of him with awe.",
            "Some of the Tribunal's mountain lakes cast up flotsam and "
            "bones that suggest hidden passages to a sea, the Black, the "
            "Adriatic, or, some say, the Baltic.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        transylvania,
        "kogaionon",
        "Kogaionon",
        inside=transylvania.places["carpathians"],
        summary=(
            "A mountain the Geto-Dacians held holy, its exact place now "
            "uncertain. The Cult of Zalmoxis says its founder spent three "
            "years in a hidden cave near the summit before coming back to "
            "teach his people magic and the soul's immortality; others "
            "say he died there and rose again."
        ),
        **RUMOURED,
    )
    _add(
        transylvania,
        "sasar",
        "The Sasar, River of the Ladies",
        inside=transylvania.places["maramures"],
        realm="Faerie",
        summary=(
            "The river below Lycaneon's mountain, from which the oppidum "
            "draws its water through tunnels underground. Its local name "
            "may recall the nymphs said to live deep in every stream that "
            "ends in the Danube, the handmaidens of the goddess Danu (the "
            "book gives no aura)."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        transylvania,
        "korosfo",
        "Körösfö",
        inside=region,
        realm="Infernal",
        summary=paragraphs(
            "Fields where a rich mining town once stood. Its people grew "
            "so wealthy their children never learned to work or keep the "
            "Sabbath; they gave up the church for feasting, and at last "
            "chose it as the only hall big enough for a dance, without "
            "noticing the day was Good Friday. At the first step God sank "
            "the whole town into the earth. It carries an Infernal aura "
            "(the book gives no strength), and the damned are sometimes "
            "heard crying out under the fields.",
            "Now and then a peasant turns up the great gold cross from the "
            "church spire, cannot scratch any gold off it, hides it while "
            "he fetches help and tools, and never finds it again. Perhaps "
            "God lets it surface so the virtuous can redeem the lost town; "
            "perhaps it is only a warning about unearned gold. Every ingot "
            "in Lycaneon's vault is stamped with the town's name, and "
            "visitors who ask are told why.",
        ),
        **KNOWN_LOCALLY,
    )
    burzenland = _add(
        transylvania,
        "burzenland",
        "The Burzenland",
        inside=region,
        summary=paragraphs(
            "The south-eastern corner of the Saxon country, inside the "
            "Carpathian ring, granted by Andrew II to the Teutonic Knights "
            "in 1211 to hold the passes against the Cumans. The Order "
            "judges its own people here and may found markets. In nine "
            "years it has raised several forts and is finishing five "
            "castles, Kronstadt in the middle and the other four about "
            "twenty miles apart round it, as bases for pushing into the "
            "Cuman lands, with Saxon settlers to feed them.",
            "Under a holier Order (an optional take on the knights) the "
            "land they conquer carries a Dominion aura of Brave temper.",
        ),
        **KNOWN_REGION,
    )
    for key, name, where in (
        ("marienburg", "Marienburg", "one of the four outer castles"),
        ("kronstadt_castle", "Kronstadt Castle", "the central castle of the five"),
        ("rosenau", "Rosenau", "one of the four outer castles"),
        ("schwarzenburg", "Schwarzenburg", "one of the four outer castles"),
        ("kreuzburg", "Kreuzburg", "one of the four outer castles"),
    ):
        _add(
            transylvania,
            key,
            name,
            inside=burzenland,
            realm="Divine",
            summary=(
                f"A Teutonic castle in the Burzenland, {where}, still "
                "being finished in 1220. With its fellows it anchors the "
                "Order's grip on the land and its advance on the Cumans "
                "(the book gives no aura)."
            ),
            **KNOWN_REGION,
        )
    _add(
        transylvania,
        "bran_pass",
        "The Bran Pass",
        inside=region,
        summary=paragraphs(
            "The old, busy road through the southern Carpathians from "
            "Câmpulung to Kronstadt. Fortifying it has just begun: the "
            "leading voivode of Transylvania has a plain stone castle at "
            "its northern mouth, the Teutonic Knights two wooden ones "
            "along it, and the voivode of Câmpulung means to build at the "
            "southern end and hopes the Saxons will help. Whoever closes "
            "the pass could cut the southern plains off from Hungary and "
            "throw off his overlord, so any Tremere can see war coming; "
            "the House may be drawn in by any party, or may quietly wear "
            "all of them down to keep things as they are.",
            "House Tremere has a zenodochium on a clifftop at the "
            "southern end (see the zenodochia). A band of southern "
            "knights has lately moved into it and preys on the traffic; "
            "their leader, a distant kinsman of the royal house, dreams "
            "of raising the Vlachs against the king. The elders want it "
            "back, a fitting test for young magi: kill them all and hide "
            "it, at the risk of royal notice, or find a quieter way.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        transylvania,
        "ikafalva",
        "Ikafalva and the Furus",
        inside=transylvania.places["carpathians"],
        summary=paragraphs(
            "A small Vlach village behind the Priest's Mountain, with the "
            "brook called the Furus running past it. Magyar legend says a "
            "mighty Magyar warrior, sworn to the goddess Furuzsina, won "
            "this land for his tribe and died in the last battle, and the "
            "spring rose where his blood fell; the neighbours believe the "
            "villagers are uncommonly strong from drinking it.",
            "Vis: a pawn of Aquam can be drawn from the source under each "
            "full moon. It is easy to gather, and the Scholomance sends "
            "its older Gifted pupils to do it, except when the Vlachs and "
            "the Hungarian clans to the west, who both claim the brook, "
            "are fighting over it: then children may be caught in a "
            "skirmish and need rescuing.",
        ),
        **KNOWN_LOCALLY,
    )
    szeklerland = _add(
        transylvania,
        "szeklerland",
        "The Szekler Land",
        inside=region,
        summary=paragraphs(
            "The eastern edge of Hungary, where the kings have moved the "
            "Szekler tribes, a few at a time, to face the Cuman raiders; "
            "the Szeklers once lived further south, in what is now the "
            "Burzenland. Their count usually rules from near Miercurea "
            "Ciuc. Giants live here under a king of their own, and the "
            "faeries under two queens: the good Firtos and the evil "
            "Tartos (see the Bestiary).",
            "Should the Szeklers ever face destruction, the ghosts of "
            "Attila's army rise from the grave to defend them.",
        ),
        **KNOWN_REGION,
    )
    _add(
        transylvania,
        "balbona_palace",
        "The Palace of Balbona",
        inside=szeklerland,
        summary=(
            "Each new giant king of the Szekler land builds himself a new "
            "palace and leaves his predecessor's empty, so several old "
            "giant palaces stand in the region. The best known was "
            "Balbona's, who called his giants to council with huge golden "
            "bells. They were buried deep when he died, yet on feast days "
            "they still ring underground and shake the earth, harmlessly."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        transylvania,
        "firtos_palace",
        "The Golden Palace of Firtos",
        inside=szeklerland,
        realm="Faerie",
        summary=(
            "The palace of gold of Firtos, queen of the good faeries of "
            "the Szekler land (the book gives no aura)."
        ),
        **RUMOURED,
    )
    _add(
        transylvania,
        "tartos_palace",
        "The Palace of Tartos",
        inside=szeklerland,
        realm="Faerie",
        summary=(
            "The hall of Tartos, queen of the evil faeries of the Szekler "
            "land, lit by three diamonds as big as a man's head hanging on "
            "golden chains. Her hoard holds gold bars, golden lions with "
            "carbuncle eyes, a golden hen with her chicks, and golden "
            "casks of coin (the book gives no aura)."
        ),
        **RUMOURED,
    )
    _add(
        transylvania,
        "cumania",
        "Cumania",
        inside=region,
        summary=(
            "The steppe and hills beyond the eastern Carpathians, where "
            "the Cuman tribes graze their herds; once the Pechenegs' west. "
            "There are no towns, which makes the land easy to seize and "
            "hard to keep: an expelled tribe, helped by its neighbours, "
            "wears any invader down and returns. In summer the Cumans "
            "draw back to their camps south of the mountains to tend "
            "their stock."
        ),
        **KNOWN_REGION,
    )


# --------------------------------------------------------------- Lycaneon


def _lycaneon(transylvania: Transylvania, b: Builder, tribunal: Tribunal) -> None:
    site = _add(
        transylvania,
        "lycaneon_mountain",
        "The Mountain of Lycaneon",
        inside=transylvania.places["maramures"],
        aura=9,
        summary=paragraphs(
            "A forested peak among high, steep mountains above a valley "
            "in Maramures, hollowed out by Terram magic into sixteen "
            "square levels, each a little wider than the one above, "
            "linked by five shafts (one in the middle, and one from each "
            "corner of the ninth level) that are crossed by flying "
            "devices, the plainest being wooden pallets the covenfolk "
            "ride with their loads; stairs and trapdoors are rarely used. "
            "The endless-seeming maze of passages is a deliberate "
            "confusion for outsiders. Tunnels run down to the Sasar for "
            "water.",
            "On the summit, wreathed in storm cloud, stand six strong "
            "basalt buildings joined in a hexagon, Romanesque work of "
            "Tremere's own design, with a curved tower at each corner, so "
            "that the whole looks like an enormous black crown; a broad "
            "dark road lined with golden imperial statues leads to its "
            "great doors.",
            "Its Magic aura reaches 9 in places, but those parts warp, "
            "and with room to spare they are mostly left empty. The white "
            "wolves of the mountain, its old guardians, give the place "
            "its name (see the Bestiary).",
        ),
        **KNOWN_ORDER,
    )
    summary = paragraphs(
        "House Tremere's first domus magna, which the Founder meant as a "
        "throne to rule the world from and which never was one: since "
        "the Sundering, when Tremere moved his seat to Coeris, it has "
        "been the House's manufactory, and one of the Order's greatest. "
        "It holds the Tribunal's Mercere Portal to Harco, so it is the "
        "natural staging post for forces sent to other Tribunals.",
        "It is busiest when war threatens or the House's stores must be "
        "rebuilt after one: it was enlarged and filled for decades after "
        "the Schism War, and readied nearly a year before the Corruption "
        "of Tytalus came out at Tribunal. In peace it holds eight magi; "
        "in 1220 it has fourteen, against room for thirty-two, because "
        "the Fourth Crusade has weakened the Theban rivals and some "
        "magi who would serve as hoplites at Seuthopolis are working "
        "here on the Prima's projects. Three are Verditius (two lately "
        "hired; the Tremere usually keep one, as Verditius magi chafe at "
        "each other) and two are Bonisagus using spare laboratories for "
        "original research, who will teach the Tremere any useful "
        "breakthrough.",
        "Its long-standing members are informal with one another, by "
        "Tremere standards: their work is shared, not competitive, and "
        "among the senior Tremere not secret, which suits frank talk "
        "about costly, dangerous research. Many Tremere come for a "
        "season or more to use its laboratories for a big project.",
        "Archmagus Albertus, the Praeco, runs its work: he assigns "
        "projects, sees them done, and deals with magi who want to "
        "commission, buy or borrow an item.",
    )
    what_matters = _lines(
        "Portal: the Tribunal's Mercere Portal, to Harco, in a hall with an eighteen-foot statue of Tremere bearing a golden eagle on his wrist",
        "Manufactory: makes and stores House Tremere's strategic reserve of magic and mundane goods; heavy work by enchanted tools, finishing by mundane craftsmen",
        "Stores: caverns of arrows, rooms of swords and other war goods, kept from decay in Circle wards",
        "Laboratories: 32, of varied specialities, with space for many more sancta; most stand idle in 1220",
        "Treasury: over 4,000 tons of gold, and double that weight in silver, in a cavern below, nearly useless since spending much of it ruins its worth",
        "Library: none described; its leader holds one of the twelve copies of the Book of Legacies",
        "Defences: the gold statues of Tremere are magic items that fight for the place and attack anyone who tries to carry them off",
        "Boon: Mystical Portal (the Mercere Portal to Harco)",
        "Boon: Aura (Magic, up to 9 in places)",
        "Boon: Magical Fortress (the hollowed mountain and the crown of towers)",
        "Boon: Literate Covenfolk (Latin-speaking, numerate villagers of the old miners' stock)",
        "Hook: House Covenant (House Tremere's manufactory and refuge)",
        "Hook: Hermetic Services (items made to order for the House and its clients)",
        "Tension: Albertus is a favourite target for archmage challengers",
    )
    notes = paragraphs(
        "Gold is worth little. Grogs with magic tools mined the mountain's "
        "gold out in the oppidum's first decades. The Tremere learned by "
        "owning more of it than anyone that gold is only worth what you "
        "can spend, and few in Mythic Europe can pay a high price for it; "
        "silver spends more easily but floods an economy (as happened "
        "lately in Stonehenge), and ruin breeds poverty, and poverty "
        "diabolism, so the House now urges laws limiting how much wealth "
        "magi may make. Gold is soft and heavy, poor stuff for "
        "enchantment; silver at least tempts or repels local faeries, so "
        "it can be traded for vis or made into weapons. Few other Houses "
        "see it, but the mines ended Tremere's hunger for territory: land "
        "is worth only the work of its people, so the House grows by "
        "having more magi doing what it wants.",
        "Look and feel. Tremere designed it before Gothic building, so "
        "its grandeur is in texture, ornament and size: walls carved with "
        "battle scenes, his sayings and Roman motifs, and gold everywhere, "
        "which modern Tremere think vulgar. None of his statues is life "
        "size: in the Grand Refectory a twelve-foot Tremere rests his hand "
        "on a cowed golden dragon. Renovation has never been a priority.",
        "The people. The covenfolk and the little towns around descend "
        "from the miners Tremere brought; generations under the House "
        "have made them unlike any other folk. They speak a Latin "
        "dialect, mostly read and write, and reckon like merchants. Each "
        "village elects three leaders, who meet in a council they call a "
        "Tribunal over borders, trade and crime, and women often lead. "
        "Their fighters are mountain skirmishers with bow, axe and short "
        "sword, retired grogs settle among them, and the descendants of "
        "the specialists keep their crafts, so many curious wares are "
        "made here, which Redcaps carry round the Tribunal.",
        "The wolves. Tremere took the mountain's lead wolf as his "
        "familiar, and many of his line seek a white wolf in turn; the "
        "House's pack loyalty and shared rearing of the young may have "
        "come to him through that bond. The wolves say they descend from "
        "men changed in a rite and left in wolf shape when the Oracles "
        "fell silent. Now and then a cub is born a throwback, human on "
        "summer's first night, its midpoint and its last; trained, such "
        "children master the change and serve the House. Wolves who wed "
        "humans have children more given than most to nightwalking in "
        "wolf shape.",
        "A refuge. Its oversized plan is a relic of the Schism War: it "
        "was rebuilt to take the flood of refugees had Diedne won the "
        "west, so that magi with no taste for war could still serve it, "
        "and every magus on the Tremere side knew a fallen covenant could "
        "flee through a Portal to Harco and on to Lycaneon. The House "
        "holds that refugees seldom solve the crisis that cost them their "
        "home. A troupe that loses its covenant can retreat here, rebuild "
        "over years, and go back to retake it.",
        "The book gives no founding year (the Founder's own time) and no "
        "season. Nine of the fourteen magi are unnamed.",
    )
    hidden = _lines(
        "Providing solutions: a magus pays Lycaneon to fix a setback, and the troupe must study it and design (and build or commission) the item that solves it; the problem may not be what it seems, the device may misbehave, or the client may not pay. Sample commissions: a weapon made of cabbages; swallowable items that make the carrier vomit them up later, on command, past faerie guards; a way to smuggle a stolen Gifted baby past city guards; a use for a mine that oozes custard; a weapon against demons that fear their own reflections; a better river toll than a chain.",
        "A rapid response force: the Prima sends a team of military specialists, publicly, through the Harco network to help covenants in other Tribunals fight; between missions they rest and refit here, and the foes (faeries of many kinds, little demons that merge into big ones, fringe traditions, vast beasts, entrenched hedge wizards, corrupt magi, or raiders who claim to be Diedne) turn out to share one master.",
        "Lycaneon was fully mobilised almost a year before the Corruption of Tytalus was announced, which suggests House Tremere knew the war was coming.",
    )
    lycaneon = b.covenant(
        "Lycaneon",
        tribunal=tribunal,
        founded=None,
        place=site,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        secrets=hidden,
        unnamed_magi=9,
        detail=FULL,
        season="Autumn",
    )
    transylvania.covenants["lycaneon"] = lycaneon
    b.book(
        lycaneon,
        "The books of Lycaneon",
        "Other",
        description=(
            "The book names no library at Lycaneon; the oppidum's "
            "strength is its laboratories. Its leader keeps one of the "
            "twelve secret copies of the Book of Legacies (see Coeris), "
            "the white register of every item the House controls."
        ),
    )
    m = transylvania.magi
    p = transylvania.privileges
    m["albertus"] = b.magus(
        "Albertus",
        covenant=lycaneon,
        house=TREMERE,
        age=58,
        summary=paragraphs(
            "Archmagus and Praeco of Transylvania, chosen by vote with "
            "the Prima's blessing, and the magus who runs Lycaneon's "
            "work: he hands out projects, keeps them to time, commissions "
            "pieces from skilled item-makers, and is the one to see about "
            "buying or borrowing an item. An engineer by training and a "
            "Rego specialist who also favours Terram and Vim, he follows "
            "who is in the Tribunal and what they do, because building "
            "teams is his great talent.",
            "One of the Order's youngest archmagi, he is a magnet for "
            "challengers, and his known Rego bent makes him weak at "
            "certamen. Expecting to lose challenges fast, he set his "
            "challenge as the most useful item given to House Tremere "
            "after three years' work: it puts off Verditius magi loath to "
            "part with their best, it cannot be finished in one Tribunal, "
            "the House gains a fine item even if he loses, and only a few "
            "Tremere know the whole reserve, so a rival's powerful piece "
            "may duplicate something the House already owns. He has "
            "faced one challenge and won.",
            "He has no plan yet to seek the Prima's seat, though he "
            "expects to want it one day. As Primus he would build a "
            "network of hidden roads, coaching houses and hospitals "
            "across the Tribunal, commission spells across the Order, "
            "send Redcaps to scout and magi to clear routes, invite the "
            "best item-crafters to work, perhaps sponsor a prize at the "
            "Verdi contest, and keep the House's engineers busy for "
            "years.",
        ),
        traits={"Likes tinkering with machines": 3, "Humorous": 2},
    )
    p["albertus"] = ("cives", "")
    m["arhmina"] = b.magus(
        "Arhmina",
        covenant=lycaneon,
        house=EX_MISC,
        age=31,
        summary=paragraphs(
            "A young Moorish sorceress from Iberia, a colona, who favours "
            "Rego and Vim. She came to Lycaneon to help House Tremere "
            "devise counterspells to her own tradition, for reasons she "
            "keeps to herself; gossip says a rival who wanted to marry "
            "her beat her in a run of magical duels, and she wants "
            "shelter first and revenge later. Her pay is a fine longevity "
            "ritual, good study books and items made to hurt that rival, "
            "and if she proves useful, Tremere help when she goes home to "
            "face him.",
            "She means to stay no more than ten years, and to use them: "
            "raising her Arts, learning the strange spirits of the dark "
            "mountains, visiting Constantinople, maybe going on to Mecca. "
            "She works closely with Clement, and travellers may meet her "
            "on the road.",
        ),
        traits={"Prone to wander": 3, "Patiently vengeful": 2},
    )
    p["arhmina"] = ("coloniae", "")
    m["clement"] = b.magus(
        "Clement",
        covenant=lycaneon,
        house=TREMERE,
        age=45,
        summary=paragraphs(
            "A middle-aged Tremere, trained first as a magical spy, who "
            "specialises in Mentem spells for battle and is a "
            "necromancer; he favours Rego, Perdo, Mentem and Vim. He was "
            "called back to Lycaneon for the Prima's plan to carry the "
            "House's power into the Levant, and is researching how to "
            "sway the minds of the spirits Arab sorcerers draw on.",
            "He wants to meet Muslim magicians to find more simple wards "
            "against such spirits, works closely with Arhmina, and spends "
            "time in the Muslim towns the King of Hungary founded for his "
            "officials, where folk magicians driven out of the Levant "
            "will happily work for Christians. His spells so far use two "
            "ideas: the spirits shun the name of God as Muslims say it, "
            "which strong Creo Imaginem can carry far, and many djinn are "
            "said to be of smokeless fire, so bitter cold outside their "
            "Magic Resistance may hurt them. He is no hand at that second "
            "kind of magic and would welcome a partner who is.",
        ),
        traits={"Likes commanding battles": 3, "Loves chess": 2},
    )
    p["clement"] = ("cives", "")
    m["phillip"] = b.magus(
        "Phillip",
        covenant=lycaneon,
        house=TREMERE,
        age=32,
        summary=paragraphs(
            "A young Herbam specialist known for spells that build and "
            "keep siege engines, who favours Muto, Rego, Herbam and "
            "Terram. He is testing, with scale models in big tanks in his "
            "huge laboratory, which magically made woods best suit "
            "magical shipbuilding: not a new question, but he is "
            "painfully thorough. Samples of rare wood are precious to "
            "him, since studying one makes the species easier to copy by "
            "magic. His findings will go to the group of Tremere working "
            "to make ships a reliable platform for magi in battle.",
            "He holds an arcane connection to Leviathan, the House's "
            "mothballed Adriatic naval base, and would move there if a "
            "sea war came; with his skill and its yards, the House would "
            "lack crews, not hulls. He is often at Shrouded Bay working "
            "on the Tremere and Mercere fleets. He dreams of a naval base "
            "in the Hungarian mountains, reached through the passages he "
            "believes join the Tribunal's lakes to the sea, and would "
            "lead an expedition into one if he could.",
        ),
        traits={"Fascinated by rare woods": 3, "Enjoys shipbuilding": 2},
    )
    p["phillip"] = ("cives", "")
    m["zalmoxis"] = b.magus(
        "Zalmoxis",
        covenant=lycaneon,
        house=VERDITIUS,
        age=70,
        summary=paragraphs(
            "Archmagus, a hospes, the senior Verditius in the Tribunal, "
            "who has worked at Lycaneon for more than forty years. He "
            "specialises in Corpus, above all healing on the battlefield "
            "and curing disease, and in longevity potions and rituals. "
            "He bears a local pagan god's name but has nothing to do with "
            "the old cult.",
            "The Tremere need him: their focus on certamen leaves none of "
            "them with a magical focus fit for longevity work, so they buy "
            "the lesser rituals from young Verditius and the best from "
            "Corpus experts in other Tribunals for their senior magi. "
            "The House always keeps at least one such expert close, so "
            "that in an Order-wide crisis it can still train healers and "
            "extenders of life.",
        ),
        traits={"Vain": 2},
    )
    p["zalmoxis"] = ("hospites", "")


# ------------------------------------------------------------ Scholomance


def _scholomance(transylvania: Transylvania, b: Builder, tribunal: Tribunal) -> None:
    valley = _add(
        transylvania,
        "scholomance_valley",
        "The Valley of the Scholomance",
        inside=transylvania.places["carpathians"],
        aura=3,
        levels=[
            b.level(
                "The Scholomance",
                5,
                see="Only in a violent storm, when lightning plays about the crags",
                enter="Open to anyone while the storm lasts; it vanishes as readily as it appears",
                notes=(
                    "The tower stands on a cliff above a little-used "
                    "pass. Now and then it appears elsewhere, mostly in "
                    "the Tribunal's mountains but once in a desert "
                    "sandstorm; the headmaster can steer its showings in "
                    "the valley, but not its rare far wanderings."
                ),
            ),
        ],
        summary=paragraphs(
            "A lonely valley high in the Carpathians south of "
            "Hermannstadt, holding only a small lake with no name, "
            "glassy on still days and mirroring the whole sky, and a "
            "Magic aura of 3. Travellers' tales tell of a castle over "
            "a high pass that shows only in the heart of a storm and "
            "is gone when the storm-tossed seek shelter there; locals "
            "nod and call it the Scholomance.",
            "Storm wizards (see the hedge traditions) have twice "
            "banded together to storm the tower, using their "
            "powers to stop it slipping back into its regio, and were "
            "beaten off both times; they spoke only of taking back "
            "something they had lost.",
        ),
        secrets="There may be a second, deeper level of the regio known only "
        "to the headmaster; this has never been confirmed or denied. "
        "Whether the storm wizards want the tower or something hidden "
        "in it is unknown.",
        **RUMOURED,
    )
    summary = paragraphs(
        "The Devil's School of legend, whispered of from the Balkans to "
        "Byzantium and the Emperor's court: ten chosen students learn "
        "nature's secrets, the speech of beasts and every spell from the "
        "Devil himself for seven years, and one is never seen again. In "
        "truth it is an oppidum running a school for agents, companions "
        "and apprentices, in a squat, ivy-grown tower inside a storm "
        "regio.",
        "Jeremiah of Tremere first broke the regio's secret and entered "
        "the tower in 1095; Coeris claimed it thirty years later as a "
        "mansio for the Redcaps of the northern Tribunal, soon trained "
        "Redcaps there, and then mundanes House Tremere had an eye on. "
        "Laniena began as part of it before moving away.",
        "It takes ten pupils at once, for seven years: mundane scholars "
        "who heard of it through a former pupil and were invited (picked "
        "for their use to House Tremere as agents, contacts or "
        "companions; nobles, bishops and kings are rumoured among the "
        "old boys), children of the Mercere families bound to be "
        "Redcaps, who compete hard for places, and at least one Gifted "
        "youth or an apprentice whose master wanted him more broadly "
        "taught (the master then usually joins the oppidum for the "
        "class). A Gifted pupil called away is replaced, usually by a "
        "Mercere child who has followed the course since missing a "
        "place, who starts behind and has something to prove.",
        "Teaching leans to Magic, Faerie and even Infernal Lore, rare "
        "tongues such as Arabic and Hebrew, astrology, alchemy and "
        "pharmacy; pupils with an aptitude learn Penetration and Finesse "
        "and, when a teacher is at hand, Supernatural Abilities, and "
        "even Order of Hermes Lore is taught, so the House controls what "
        "mundanes know of it. Each pupil copies texts and writes a summa "
        "or three tractatus. Old classmates often stay in touch for "
        "decades. No pupil is taken by the Devil; the legend likely "
        "comes from those who vanish into apprenticeships. Past "
        "headmasters wiped mundane pupils' memories and laid false "
        "trails, but the present policy is to make friends for the "
        "Order, so the school's ties are not advertised but not denied.",
    )
    what_matters = _lines(
        "Vis: the Furus brook at Ikafalva, a pawn of Aquam each full moon, gathered by the older Gifted pupils",
        "School: ten pupils for seven years; magi teach a season a year in return for the library, and extend their Parma over their pupils",
        "Library: on the second floor, mundane and occult learning and an unmatched collection on non-Hermetic magic, but nothing on the Arts or the Order",
        "Library: on the guarded third floor, the oppidum's Hermetic texts",
        "Laboratories: four sancta for resident magi; four guest rooms for visiting tutors, who share one large laboratory booked by the season",
        "Stores: cellars kept fresh by enchantment; a wagon train of supplies comes once a year, with Redcaps bringing extras",
        "Covenfolk: three soldiers only; servants who must treat every pupil as deaf and mute",
        "Boon: Aura (Magic 5 in the regio)",
        "Boon: Difficult Access (the tower shows only in storms)",
        "Hook: Erratically Mobile (the tower wanders, sometimes far away)",
        "Hook: Infamous (the Devil's School)",
        "Tension: a papal legate lodged with the Teutonic Knights is gathering a case against it",
        "Tension: storm wizards have twice tried to seize the tower",
        "Tension: Simium writes to Polyaigos of the Theban Tribunal about an exchange of pupils, which old enmity blocks",
    )
    notes = paragraphs(
        "The tower. The ground floor has the servants' and pupils' "
        "rooms, kitchens, workshops, a dining hall and Redcap guest "
        "rooms; the second, a lecture hall, small galleries and "
        "scriptoria; the third, up one always-guarded stair, the "
        "headmaster's office, the sancta, the guest rooms, the shared "
        "laboratory and the Hermetic library. Enchantments in the "
        "corridors and some rooms garble speech so it cannot be "
        "understood, and those in most study rooms blur writing for "
        "anyone but the one person touching it, so pupils cannot easily "
        "learn what others study. Neither is foolproof, but both add to "
        "the mystery.",
        "The masters. Mature Tremere are often posted here before taking "
        "an apprentice. A magus with an apprentice at the school must "
        "teach another pupil too. Teaching is mostly one to one, or a "
        "small group when the masters are few. The school prefers magi "
        "with a taste for occult lore, natural philosophy or the liberal arts, "
        "or who hold a Supernatural Ability. One resident lately left "
        "for a distant Tribunal, so a sancta stands empty. Non-Hermetic "
        "tutors, the school's companions, teach beside them.",
        "For players: the school explains Virtues such as Educated, "
        "Arcane Lore, Privileged Upbringing or Skilled Parens, and a "
        "saga can start with the player characters as classmates, before "
        "or just after the Opening of the Arts, with the other pupils as "
        "companions.",
        "Founded as the Coeris mansio about 1125 (the tower was entered "
        "in 1095); the book gives no season. One of the three magi is "
        "unnamed.",
    )
    hidden = _lines(
        "The specialist: a character with a Supernatural Ability is asked to teach it to a troubled boy; every earlier teacher of his died horribly, in ways linked to that Ability and beyond what a child could do.",
        "A snake in the classroom: a pupil gets past the third floor's guards and vanishes with several key texts, among them a summa on the Parma Magica; he belongs to another tradition, and the school's future may hang on catching him before the book reaches his fellows.",
        "A shadow on the mind: a former pupil dreams of dread and bloody claws, and finds that he and all his classmates have lost the same season at the school; the masters erased it for a reason.",
        "A friend in need: an old classmate accused of a Hermetic crime in another Tribunal asks a character of standing for an alibi to buy time.",
        "Sebastian's name echoes the dragon king Aževastjepan's; see Sebastian.",
    )
    scholomance = b.covenant(
        "The Scholomance",
        tribunal=tribunal,
        founded=1125,
        place=valley,
        level=1,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        secrets=hidden,
        unnamed_magi=1,
        detail=FULL,
        season="Summer",
    )
    transylvania.covenants["scholomance"] = scholomance
    b.book(
        scholomance,
        "The library of the Scholomance",
        "Other",
        description=(
            "No books are named. Two collections: on the second floor a "
            "broad library of mundane and esoteric learning, the best "
            "anywhere on magic outside the Order's, swelled by the "
            "copies and treatises each pupil must make, with nothing on "
            "the Hermetic Arts or the Order; on the guarded third floor "
            "the oppidum's Hermetic texts, among them Simium's many "
            "primers. The House hopes the hedge-magic books may one day "
            "help Hermetic magic grow."
        ),
    )
    m = transylvania.magi
    p = transylvania.privileges
    m["simium"] = b.magus(
        "Simium Arileins",
        covenant=scholomance,
        house=BJORNAER,
        age=78,
        summary=paragraphs(
            "The school's eldest magus and its headmaster, known across "
            "the Order as a historian and philosopher and a tireless "
            "author of beginners' texts on many subjects, the Arts among "
            "them, found as far off as Stonehenge and Iberia, though "
            "mostly fit only for young magi. He looks fifty-eight.",
            "Years at the lectern have bent his back, and his small dark "
            "eyes blink constantly; he dresses in plain black robes and a "
            "black skullcap. His heartbeast is a raven bigger than a man, "
            "through the Mystery of the Inner Heartbeast, and his flights "
            "over the mountains have bred local tales of a demon bird "
            "that can carry off a grown man.",
        ),
        traits={"Raven": 3, "Stern": 3, "Talkative": -2},
    )
    p["simium"] = ("cives", "Headmaster of the Scholomance")
    m["andrew"] = b.magus(
        "Andrew Melanchthon",
        covenant=scholomance,
        house=TREMERE,
        age=49,
        summary=paragraphs(
            "A Tremere who left the Rhine Tribunal after loud public "
            "quarrels with a leading Bonisagus branded him an empiricist "
            "and an atheist and ended any hope of office there. The "
            "charge of atheism is unjust: like most Tremere he is "
            "impious, not godless; his real offence was saying aloud that "
            "God is no loving father. He looks thirty-six.",
            "The Scholomance lets him teach his own course: moral "
            "philosophy and rhetoric from texts the establishment calls "
            "heretical or blasphemous. He dreams of pupils carrying his "
            "humanist programme into Europe's universities and courts.",
        ),
        traits={"Dedicated": 3, "Hopeful": 2, "Naïve": 1},
    )
    p["andrew"] = ("cives", "")
    m["sebastian"] = b.magus(
        "Sebastian",
        covenant=scholomance,
        house="",
        age=None,
        type="companion",
        summary=paragraphs(
            "The tower's caretaker and a tutor, a riddle: he was its "
            "only inhabitant when Jeremiah of Tremere first got in, "
            "in 1095, and has not visibly aged since. He looks an "
            "ordinary man in his forties. Most magi think him some "
            "kind of magic kin, but those rude enough to probe him "
            "with magic found nothing, not even a Might score, and "
            "the headmaster works to keep the resulting suspicion in "
            "check. He tells each headmaster his secret, or part of "
            "it, helps run the school, knows the tower and its regio "
            "better than anyone, and has helped headmasters master it "
            "in hard times.",
            "Friendly but close, he enjoys knowing more than others, "
            "except when he teaches philosophy, the liberal arts, dead "
            "languages and forgotten lore, which he loves.",
            "Some magi have noticed that his name is close to that of "
            "the dragon king Aževastjepan; nobody has confronted him, "
            "but they tread warily round him.",
        ),
        secrets="Sebastian may be Aževastjepan himself, the seven-headed "
        "dragon king of the Carpathians, in human guise.",
    )
    m["ludmilla"] = b.magus(
        "Ludmilla",
        covenant=scholomance,
        house="",
        age=None,
        type="companion",
        summary=paragraphs(
            "A Romanian strigoica, a witch: a Gifted folk witch (see "
            "the hedge traditions) with the Entrancement Ability, in "
            "her middle fifties, slim, her beauty fading; she hides "
            "her hands, which are knotted and swollen at the "
            "knuckles. She teaches pupils the Supernatural Abilities "
            "she shares with them, for free use of the oppidum's "
            "books.",
            "She also uses the school to spot recruits for the coven "
            "she leads. The masters politely look away, because she "
            "has sometimes Initiated an unGifted Tremere agent trained "
            "there into one of her tradition's Abilities. People "
            "suspect her of being a nightwalker, which she denies.",
        ),
        secrets="She is a nightwalker. When she walks, her phantasticum is a "
        "white moth with a lovely young girl's face.",
    )


# ------------------------------------------------------------- the world


def _lords(transylvania: Transylvania, b: Builder) -> None:
    w = transylvania.world
    p = transylvania.places
    w["voivode"] = b.lord(
        "The Voivode of Transylvania",
        title="count",
        wealth="Wealthy",
        seat="Alba Iulia",
        place=p["transylvania"],
        summary=paragraphs(
            "The king's governor of Transylvania, a prince in all but "
            "name, appointed from a line of voivodes who each hold the "
            "post only a few years; the book does not name the present "
            "one. He rules from Alba Iulia as the King of Hungary's "
            "vassal. The leading voivode has built a stone castle at the "
            "northern mouth of the Bran Pass, and a firm border there "
            "could tempt him toward independence. He might ask magi to "
            "help destroy a Teutonic castle.",
        ),
    )
    w["campulung_voivode"] = b.lord(
        "The Voivode of Câmpulung",
        title="count",
        seat="Câmpulung",
        place=p["transylvania"],
        summary=(
            "The strongest Vlach lord south of the Carpathians, vassal "
            "of a greater neighbour, ruling from Câmpulung. He plans a "
            "fortress at the southern end of the Bran Pass and hopes his "
            "Saxon neighbours will help build it; he might ask magi too. "
            "Closing the pass would loosen the southern plains from "
            "Hungary."
        ),
    )
    w["burzenland"] = b.lord(
        "The Burzenland",
        title="baron",
        wealth="Wealthy",
        seat="Kronstadt",
        ruler="Brother Theoderich",
        place=p["burzenland"],
        arms=TEUTONIC_ARMS,
        summary=paragraphs(
            "The Teutonic Knights' land in Transylvania, granted by "
            "Andrew II in 1211, just after he agreed a match between his "
            "daughter and the son of Hermann of Thuringia. The king gave "
            "the territory and freedom from taxes and dues, but kept the "
            "right to mint coin and half of all gold and silver mined; in "
            "return the knights guard the Carpathian passes against the "
            "Cumans. The Order may hold its own courts and found markets "
            "here.",
            "Brother Theoderich, master of the mission, runs it almost "
            "alone, since the hochmeister divides his time between the "
            "Holy Land and Egypt. Fast expansion, Theoderich's want of "
            "tact and the envy of the Hungarian lords make an explosive "
            "mix; the knights have already offended the local bishop by "
            "denying his rights in the Burzenland, and they court the "
            "pope to slip free of the Hungarian crown.",
        ),
    )


def _towns(transylvania: Transylvania, b: Builder) -> None:
    w = transylvania.world
    p = transylvania.places
    king_voivode = w["voivode"]

    def town(key: str, name: str, summary: str, **kw: Any) -> None:
        w[key] = b.town(name, summary=summary, **kw)

    town(
        "alba_iulia",
        "Alba Iulia",
        "The White Castle, capital of Transylvania and seat of its "
        "voivode, the King of Hungary's vassal. It stands on the "
        "foundations of Apulum, one of the largest cities of Roman "
        "Dacia.",
        charter="Noble lord",
        answers_to=king_voivode,
        place=p["transylvania"],
    )
    town(
        "campulung",
        "Câmpulung",
        "The chief town south of the mountains, on the remains of a "
        "Roman colony, fifteen miles below the Bran Pass; seat of the "
        "voivode of Câmpulung.",
        charter="Noble lord",
        answers_to=w["campulung_voivode"],
        place=p["transylvania"],
    )
    town(
        "lycaneon_villages",
        "The Villages of Lycaneon",
        "The small towns round Lycaneon, peopled by descendants of the "
        "miners Tremere brought, retired grogs and the heirs of the "
        "oppidum's craftsmen. They speak a Latin dialect, mostly read and "
        "write, and reckon like merchants; each elects three leaders to a "
        "council they call a Tribunal, which settles borders, trade and "
        "crime, and women often lead. Their warriors are mountain "
        "skirmishers with bows, axes and short swords, and their odd "
        "wares go round the Tribunal with the Redcaps.",
        charter="Commune",
        place=p["maramures"],
    )
    saxon = (
        "one of the seven fortified towns of the Transylvanian Saxons "
        "that give Siebenbürgen its name"
    )
    for key, name, extra in (
        ("bistritz", "Bistritz", ""),
        (
            "hermannstadt",
            "Hermannstadt",
            " The Scholomance's valley lies in the mountains to the south.",
        ),
        ("klausenburg", "Klausenburg", ""),
        (
            "kronstadt",
            "Kronstadt",
            " It lies in the Burzenland, round the central castle of the "
            "Teutonic Knights, and at the northern end of the Bran Pass.",
        ),
        ("mediasch", "Mediasch", ""),
        ("muhlbach", "Mühlbach", ""),
        ("schassburg", "Schässburg", ""),
    ):
        inside = p["burzenland"] if key == "kronstadt" else p["transylvania"]
        town(
            key,
            name,
            f"{name}, {saxon}: German settlers living by their own laws as "
            f"royal guests, who farm, raise stock and work mines.{extra}",
            charter="Commune",
            place=inside,
        )


def _factions(transylvania: Transylvania, b: Builder) -> None:
    w = transylvania.world
    p = transylvania.places
    w["teutonic_knights"] = b.faction(
        "The Teutonic Knights",
        faction="Other",
        decides="Its leader",
        ruler="Brother Theoderich",
        realm="Divine",
        place=p["burzenland"],
        arms=TEUTONIC_ARMS,
        wants="The Burzenland free of Hungary under the pope, and a road of forts down the Danube to the Black Sea",
        offers="Knights and garrisons against the Cumans; a hand of friendship, not always sincere",
        summary=paragraphs(
            "Formally the Hospital Order of St Mary of the Germans in "
            "Jerusalem, youngest of the military orders: founded at "
            "the siege of Acre after Barbarossa's death, when "
            "crusaders from Bremen and Lübeck set up a hospital for "
            "sick Germans the Hospitallers neglected, approved by "
            "Celestine III and given a military charter in 1198. Its "
            "head, the hochmeister, is elected for life by the "
            "general chapter; Hermann von Salza has held the post "
            "since 1210, travelling as diplomat and inspector with a "
            "council of the masters, the treasurer, the grand "
            "commander and the marshal. In 1220 it has its seat at "
            "Acre and just two missions, in the Empire and in "
            "Transylvania, where Brother Theoderich is master.",
            "Its rule, the customs, is written in German: poverty, "
            "chastity and obedience, the canonical hours, priestly "
            "dress under a white mantle with a black cross, no rowdy "
            "feasts and no women. Punishment runs from the whip and "
            "short rations to years in chains; cowardice before the "
            "enemy, desertion to the infidel and sodomy mean "
            "expulsion or death. Each knight has ten graymantles, "
            "half-brothers of common birth, as squires and sergeants. "
            "Knights are noble, some from the Empire's serf-knights "
            "and poor; many carry relics, often in their sword hilts, "
            "and study Theology, Church Lore and Dominion Lore beside "
            "arms (Brother Chaplain, Brother Knight and Brother "
            "Sergeant are their Virtues: black cross on green, white "
            "and grey).",
            "The Order and House Tremere want much the same, a "
            "self-ruling state for mankind's good under their own "
            "guidance. The knights mean to push down the Danube from "
            "the Burzenland to the Black Sea with garrisoned forts "
            "and reopen the land road to Constantinople. The pope has "
            "charged them to hunt heresy and diabolism, so the "
            "Tremere fear they would call the Order of Hermes heretic "
            "or pagan, and the House forbids Tribunal magi any formal "
            "contact; the knights will not stay ignorant long. The "
            "hochmeister seeks the Scholomance but has found only the "
            "same tale told again and thinks it a legend; a papal "
            "legate, sent by Honorius III to look into it, lodges "
            "with the knights.",
            "Story: a hedge wizard with a grudge against the Order is "
            "taken by a Teutonic garrison and tells them all he knows "
            "of magi. When the garrison starts marking Hermetic "
            "targets, the troupe must decide how much to reveal, "
            "which the Tremere ban on contact forbids, or whether to "
            "wipe out the garrison and leave no witness.",
        ),
        secrets=paragraphs(
            "Two optional Orders. A holier one fights for the "
            "Dominion: its conquests carry a Brave Dominion aura, it "
            "sends preachers among the Cumans before its armies, and "
            "an inner circle of Divine wonder-workers uses "
            "Invocation, Blessing and Cursing and senses holiness. "
            "Their Blessing of the relic (Invocation 30) lends one "
            "relic's Magic Resistance and its scourge of demons to up "
            "to ten men who keep together, for a Sabbath.",
            "A profane one serves infernal masters, wants power over "
            "land more than pagan blood, and hoards occult lore, "
            "capturing shamans, witches and taltós; many of its "
            "leaders are goetic sorcerers and the rest diabolists, "
            "and it rules the common folk through fear, possession "
            "and blackmail. Its favoured knights carry great swords "
            "with a bound demon that whispers in their dreams, and "
            "that can trade a blow's damage for an Incapacitating "
            "wound that heals the wielder's own worst wound, three "
            "times a day (Consumption 37).",
            "If history runs its course, Andrew II (home from "
            "crusade since 1218) is forced to grant the Golden Bull "
            "in 1222 but will not take the Burzenland back; in 1225 "
            "Hermann von Salza puts it under the Holy See, and the "
            "king drives the knights out by force when they refuse "
            "to go. The Cumans then pour through the weakened "
            "defences.",
        ),
    )
    w["saxons"] = b.faction(
        "The Transylvanian Saxons",
        faction="Other",
        place=p["transylvania"],
        wants="Land, markets and their own law",
        offers="Grain, wool, meat, metal and miners; help building castles",
        summary=paragraphs(
            "German settlers, mostly from Saxony, who began coming in "
            "the middle of the last century and came in numbers under "
            "the Teutonic Knights, who need their grain, wool and meat "
            "to stand on their own. They mine gold and silver for the "
            "knights (half goes to the crown) and iron, which they trade "
            "or smelt. Like the Szeklers they are free royal guests "
            "(hospites in Hungarian law, not the Hermetic privilege), "
            "outside the counts' reach, and a tax on them yields a share "
            "of the king's income.",
            "Their land, wider than the knights' own, they call "
            "Siebenbürgen after its seven chief walled towns: Hermannstadt, "
            "Kronstadt, Bistritz, Klausenburg, Schässburg, Mediasch and "
            "Mühlbach; the Burzenland is only its south-eastern corner.",
        ),
    )
    w["szeklers"] = b.faction(
        "The Szeklers",
        faction="Other",
        decides="Its leader",
        ruler="The count of the Szeklers",
        place=p["szeklerland"],
        wants="Their freedom and common lands kept",
        offers="Horse archers, light cavalry and infantry for the king",
        summary=paragraphs(
            "Frontier guards, as their name says, and by their own "
            "account the remnant of Attila's Huns, left by his son to "
            "hold a foothold for the Huns' return; they allied with the "
            "Magyars, who claimed the same descent, and now speak "
            "Hungarian but remain a class apart. Six tribes of four "
            "branches each, every branch owing a hundred horsemen in "
            "war; pasture and plough land belong to the branch, and who "
            "uses which field each year is settled by shooting arrows. "
            "Branch war leaders and officers form the upper class over "
            "farmers and herdsmen, and to Hungarian eyes they all answer "
            "to a count near Miercurea Ciuc, though it is less simple "
            "than that.",
            "They lead the king's army out and guard its rear coming "
            "home, more of them if he leads in person, but do not fight "
            "to the north or west, sending hired men instead. In return "
            "all are free and untaxed, though each household gives the "
            "king a branded ox when he is crowned, weds or has an heir. "
            "Their light horse archers suit Cuman raiders better than "
            "Byzantines. They are reputed the fiercest fighters in the "
            "Tribunal, with a tradition of taltós who led them in war "
            "(see the hedge traditions). Lately a mysterious preacher "
            "has stirred them to turn on their neighbours, and Vlachs "
            "say a taltós has won back his tradition's power and is "
            "gathering lesser taltós into an empire.",
        ),
    )
    w["pechenegs"] = b.faction(
        "The Pechenegs",
        faction="Other",
        place=p["carpathians"],
        offers="Warriors for the king and for the oppida",
        summary=(
            "Once a loose league of nomad warriors ruling the west of "
            "what is now Cumania. Beaten by the Byzantines and robbed of "
            "their lands, they became Christian and the Hungarian kings "
            "settled them in the southern Carpathians, where they now "
            "guard the passes once held against them, as royal guests in "
            "Hungarian law. They speak Oghuz. Many of their warriors "
            "took service with magi when they lost their lands, and "
            "their shamans entered House Tremere's service then too (see "
            "the hedge traditions)."
        ),
    )
    w["cumans"] = b.faction(
        "The Cumans",
        faction="Other",
        place=p["cumania"],
        wants="Grazing, plunder and pay",
        offers="Mercenary horsemen",
        summary=paragraphs(
            "The Kipchaks: nomads who took the lands east of the "
            "Carpathians in the eleventh century, a confederation "
            "stretching deep into Asia with no single leader, its tribes "
            "raiding, settling, trading and treating with outsiders on "
            "their own account. Most are Turkic or Alan; most still "
            "roam, though some farm. They speak Kipchak. Fear of them "
            "made the kings move Szekler tribes to the passes and bring "
            "in the Teutonic Knights, and the kings use the threat of "
            "them, or of a Cuman marriage, to wring favours from the "
            "pope.",
            "They are kin to Bulgaria's Asen rulers, sheltered and armed "
            "the rebellion against Byzantium, and still serve Bulgaria as "
            "mercenaries; their summer withdrawal to tend their herds "
            "shapes Bulgarian campaigning. In battle they strike lightly "
            "armoured, feign flight again and again, then turn with a "
            "roar and swords drawn. Their religion is Tengrist, worship "
            "of a creator sky god; their shamans scry, rule the weather, "
            "heal fast and travel swiftly (see the hedge traditions). "
            "None seem as strong as Bulgaria's old shamans; some Tremere "
            "think something besides the Church destroyed those, others "
            "that strong Cuman shamans simply stay out of border wars.",
            "If history runs on, the Mongols break them at the Kalka in "
            "1223; twenty thousand families settle in Hungary as "
            "Christians sworn to fight the Mongols, others vanish into "
            "the Golden Horde, and more flee to Nicaea's service.",
        ),
    )
    w["vlachs"] = b.faction(
        "The Vlachs",
        faction="Other",
        place=p["transylvania"],
        wants="Their land and their ways, under whatever ruler",
        offers="Shepherds, farmers, local knowledge and boyar war bands",
        summary=paragraphs(
            "The native people north of the Danube, rumân or roman in "
            "their own tongue, heirs of the Getae and the Dacians "
            "Romanised under Rome and left behind as farmers and "
            "shepherds when Rome withdrew in 275. Visigoths, Huns, Gepids "
            "and Avars drove them into the wilds; Slavs, Magyars and "
            "Pechenegs came and settled beside them, each leaving only a "
            "mark. They bend to foreign rule and endure.",
            "Their nobles, the boyars, take the titles jupan, cneaz or "
            "voievod, each equal to a duke, and live with war bands among "
            "villages of bound peasants. Free peasants form obote, "
            "self-governing communes with elected officers and common "
            "land, paying tribute to the Hungarian crown and free to move "
            "away; communes outnumber boyar villages, more so in the "
            "east. They were Christian early, by legend through the "
            "Apostle Andrew in the Dobrogea, and their bishops look to "
            "Rome, not Constantinople.",
            "Their folk witches, the vrajitoarele, belong to the Magic "
            "realm, not the Infernal (see the hedge traditions).",
        ),
    )
    w["brodnici"] = b.faction(
        "The Brodnici",
        faction="Other",
        place=p["cumania"],
        summary=(
            "A people of mixed Vlach and Slav stock, the main group in "
            "the lands east of the Carpathians, which have no city of "
            "their own and are far more independent than the western "
            "Vlach lands. They owe allegiance to Suzdal; the other groups "
            "there serve stronger Vlach and Transylvanian voivodes, and "
            "the region is not united."
        ),
    )
    w["zalmoxis_cult"] = b.faction(
        "The Cult of Zalmoxis",
        faction="Other",
        decides="Its leader",
        realm="Magic",
        place=p["maramures"],
        wants="Its god's return",
        summary=paragraphs(
            "The secret faith of the old Geto-Dacian elite, who worshipped "
            "the one god Zalmoxis before Christ; driven underground and "
            "into the mountains as others converted, it survives among "
            "rich, proud, stubborn families as a mystery cult whose rites "
            "only a few see. Its tale makes Zalmoxis a pupil of "
            "Pythagoras on Samos who learned of immortality and rebirth "
            "in Egypt, then spent three years in a cave on Kogaionon and "
            "came back to teach (or died and rose again). Herodotus and "
            "Plato call him a man and Christian writers a fraud, but that "
            "they all tell the story at all is unsettling. Every five "
            "years the cult sends him a messenger by throwing a man onto "
            "a spear point: if he dies the god has accepted him.",
            "Princes and priests suspect it lives on in several Vlach "
            "lands. In the mountains south of Maramures several groups "
            "follow vrajitoarele, Vlach folk witches of the Magic realm. "
            "One Gifted leader is slowly drawing the others to him, "
            "against the distrust his Gift stirs, and on learning that a "
            "wizard of the hollow mountain nearby is called Zalmoxis he "
            "proclaims the god risen again and imprisoned by the other "
            "wizards. Lycaneon's magi know nothing of it.",
        ),
    )


# ------------------------------------------------------------- finishing


def _lord_named(transylvania: Transylvania, *words: str) -> Neighbour | None:
    """The lord another part made whose name holds all `words`."""
    for neighbour in transylvania.b.saga.neighbours:
        if neighbour.kind == "lord" and all(
            word.casefold() in neighbour.name.casefold() for word in words
        ):
            return neighbour
    return None


def finish(transylvania: Transylvania) -> None:
    """Put Transylvania inside Hungary and tie the voivode and the
    Burzenland to the king, once hungary.py has made them."""
    region = transylvania.places["transylvania"]
    hungary = transylvania.places.get("hungary")
    if hungary is not None and not region.place_id:
        region.place_id = hungary.id
    king = _lord_named(transylvania, "Andrew") or _lord_named(transylvania, "Hungary")
    if king is None:
        return
    for key in ("voivode", "burzenland"):
        transylvania.world[key].answers_to = king.id


# --------------------------------------------------------------- stats

P = Profile
ROMANIAN = "Romanian"


def _art(name: str, art: str) -> tuple[str, dict[str, str]]:
    return (name, {"art": art})


#: Each magus the chapter sketches without a stat block, by character key.
PROFILES: dict[str, Profile] = {
    "albertus": P(
        strong="int dex pre",
        weak="com",
        arts={"Re": 10, "Te": 7, "Vi": 6, "Cr": 3, "Mu": 3},
        abilities={
            "Magic Theory": (6, "enchanted devices"),
            "Leadership": (4, "teams of magi"),
            "Craft: Engineer": (4, "machines"),
            "Bargain": (3, "magic items"),
            "Organization Lore: Order of Hermes": (3, "who is where"),
            "Code of Hermes": 3,
        },
        virtues=[
            "Inventive Genius",
            _art("Affinity with {art}", "rego"),
            "Dutybound",
            "Busybody",
        ],
        native=ROMANIAN,
    ),
    "arhmina": P(
        strong="int pre sta",
        weak="com",
        arts={"Re": 8, "Vi": 8, "Me": 3, "In": 3},
        abilities={
            "Magic Lore": (4, "spirits"),
            "Penetration": (3, "Vim"),
            "Area Lore: Iberia": 2,
        },
        virtues=["Educated (Islamic)", "Wanderlust", "Hatred (Minor)"],
        native="Arabic",
    ),
    "clement": P(
        strong="int pre sta",
        arts={"Me": 9, "Re": 6, "Pe": 6, "Vi": 5, "Im": 3, "Cr": 3},
        abilities={
            "Magic Lore": (3, "spirits"),
            "Leadership": (3, "battles"),
            "Stealth": (2, "towns"),
            "Guile": (2, "spying"),
            "Living Language: Arabic": 2,
        },
        virtues=[
            _art("Affinity with {art}", "mentem"),
            ("Minor Magical Focus", {"focus": "ghosts"}),
            "Driven (Minor)",
            "Obsessed (Minor)",
        ],
        native=ROMANIAN,
    ),
    "phillip": P(
        strong="int dex per",
        arts={"He": 9, "Mu": 6, "Re": 6, "Te": 5, "Cr": 3},
        abilities={
            "Craft: Shipwright": (4, "warships"),
            "Craft: Engineer": (3, "siege engines"),
            "Magic Theory": (4, "Herbam"),
            "Profession: Sailor": 1,
        },
        virtues=[
            _art("Affinity with {art}", "herbam"),
            "Obsessed (Minor)",
        ],
        native=ROMANIAN,
    ),
    "zalmoxis": P(
        strong="int dex sta",
        arts={"Cr": 9, "Co": 9, "Re": 4, "Vi": 4, "He": 3},
        abilities={
            "Medicine": (6, "longevity"),
            "Chirurgy": (4, "battle wounds"),
            "Magic Theory": (6, "longevity rituals"),
            "Teaching": (3, "healers"),
        },
        virtues=[
            ("Minor Magical Focus", {"focus": "longevity rituals"}),
            "Proud (Minor)",
        ],
        native=ROMANIAN,
    ),
    "simium": P(
        strong="int com per",
        weak="str dex",
        arts={"An": 7, "Mu": 6, "In": 6, "Co": 4, "Me": 4},
        abilities={
            "Teaching": (6, "novices"),
            "Artes Liberales": (5, "history"),
            "Philosophiae": (5, "moral philosophy"),
            "Profession: Scribe": (4, "primers"),
            "Area Lore: Carpathians": 3,
        },
        virtues=["Good Teacher", "Hunchback", "Poor Eyesight"],
        native=ROMANIAN,
    ),
    "andrew": P(
        strong="com int pre",
        arts={"Me": 7, "In": 5, "Re": 5, "Cr": 4, "Im": 4},
        abilities={
            "Philosophiae": (5, "moral philosophy"),
            "Artes Liberales": (5, "rhetoric"),
            "Teaching": (4, "rhetoric"),
            "Area Lore: Rhine Tribunal": 2,
        },
        virtues=["Good Teacher", "Optimistic (Minor)", "Infamous"],
        native="High German",
    ),
}

#: The ages the book says these magi look.
APPARENT_AGES = {"simium": 58, "andrew": 36}


def stats(transylvania: Transylvania) -> None:
    """Generated stats for the magi of Lycaneon and the Scholomance, none
    of whom has a printed stat block."""
    b = transylvania.b
    for key, profile in PROFILES.items():
        apply(b, transylvania.magi[key], profile)
    for key, apparent in APPARENT_AGES.items():
        transylvania.magi[key].aging.apparent_age = apparent
