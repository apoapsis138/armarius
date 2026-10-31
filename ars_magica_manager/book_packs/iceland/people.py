"""People and culture (Land of Fire & Ice ch. 3, pp. 20-33): how the
Icelanders live, their ranks, customs and money, the hreppar as a part
of society, the giant and troll clans, the landvaettir, and the book's
seeds as dormant stories.

The two creature blocks, Trolls (p. 30) and Giants (p. 31), are
converted by the pack's readings (see the package docstring): Might,
Characteristics, Size, body vis, combat totals, Soak and Might costs as
printed; the Might's Form is Corpus, the Art of the vis in their bodies,
this pack's reading. Fatigue keeps the printed number of levels. No
Confidence is printed and none is given, the blocks being kinds, not
persons.

The magic part holds the Galdramen Hreppur, the magicians and their
story seeds (pp. 27, 29); this part has the farmers' hreppar. Where the land part has made a place these records name,
they sit in it, found by name."""

from __future__ import annotations

from ...models import BodyVis, Neighbour
from ..builder import Builder, characteristics, dormant, paragraphs, wound_ranges

TROLL_FATIGUE = "OK, 0/0/0, -1, -3, -5, Unconscious"
GIANT_FATIGUE = "OK, 0/0/0/0, -1/-1/-1, -3/-3, -5, Unconscious"

PERSONAL = ("Personal", "Sun", "Individual")


def build(b: Builder) -> None:
    _society(b)
    _customs(b)
    _economy(b)
    _hreppar(b)
    _giants(b)
    _landvaettir(b)
    _creatures(b)
    _stories(b)


def _place(b: Builder, name: str) -> Neighbour | None:
    """The place another part made under this name, if any."""
    return next(
        (n for n in b.saga.neighbours if n.kind == "place" and n.name == name),
        None,
    )


# -- ranks --


def _society(b: Builder) -> None:
    b.faction(
        "The Icelanders",
        place=_place(b, "Iceland"),
        summary=paragraphs(
            "Iceland has no towns and no villages: nearly everyone lives on "
            "a farmstead. Cattle feed the household, sheep earn its trade, "
            "and the short, thick-coated Scandinavian horse is the only other "
            "beast kept in numbers. Hay is the great crop, for the stock "
            "cannot outlast the winter without it, and a poor hay harvest "
            "means real hardship. Only the richest land of the south and "
            "west tries barley, the summers are barely long enough, and most "
            "cereal comes in by ship, so strong drink is scarce.",
            "With trees gone and the volcanic rock too hard to dress, walls "
            "are of turf and enclosures stay small: a manured hayfield and a "
            "little special pasture before or around the house. The longhouse "
            "is turf too, long and narrow and a little broader at the middle, "
            "with its door under a small gable near one end of the front "
            "wall; grass climbs its sides until it seems part of the hill. "
            "Inside, broad benches line the walls and a long fire runs down "
            "the hall for heat and cooking, with little holes at the roof's "
            "foot for light and smoke. People sleep in the hall, the master "
            "often in a bed closet that locks. Beasts are housed apart.",
            "Ten adults and children is the usual farm; a poor tenant has "
            "room for his family and a couple of labourers; a godi or a rich "
            "farmer has a large building of several rooms, all on one level, "
            "that sleeps twenty or thirty. Only the most prosperous have a "
            "second farmhouse, the first usually being enlarged instead.",
            "Dress follows the mainland: a long shirt and trousers for men; "
            "for women a long shift, often pleated, under a front and back "
            "apron held by brooches below the shoulders. Cloth is the natural "
            "brown, black, grey or white of the wool. Dyed cloth shows wealth "
            "and comes out for the Althing, and the rich wear imported linen "
            "beneath.",
        ),
        rules=paragraphs(
            "Farmsteads in 1220, as printed: Eastern Quarter 1260, Southern "
            "1750, Western 1580, Northern 2140. The book totals these as "
            "4560, though they add to 6730. Population between 60 and 70 "
            "thousand, which at ten to a farm (p. 20) fits the 6730. Pp. 20-21, "
            "24.",
        ),
    )
    b.faction(
        "The Godar",
        place=_place(b, "Iceland"),
        decides="Their chieftaincies, the godord, each a legal entity within one "
        "of the thirteen districts.",
        summary=paragraphs(
            "The chieftains, the island's social elite; one is a godi. Each "
            "holds at least one godord, a chieftaincy that is property in law: "
            "it can be bought, sold, inherited or held by two or more men who "
            "split its duties. By 1220 most of the forty-eight are held by "
            "just five families.",
            "A godi is no feudal lord. He is the link between his thingmen and "
            "the law, sits on the law council (logretta) and names judges at "
            "assemblies. His thingmen often find it worth their while to bear "
            "arms for him but owe him nothing of the kind, and though a godord "
            "is no territory, men mostly choose a godi who lives close by.",
        ),
        rules="A woman may inherit a godord but not run it: she names a man to "
        "act for her, and can do well through him. Pp. 21, 23.",
    )
    b.faction(
        "The Baendur",
        place=_place(b, "Iceland"),
        summary=paragraphs(
            "The householders; one is a bondi. The household is the root of "
            "the whole society: usually one farmstead with its fields and "
            "cattle, a husband and wife, their employees, their children and "
            "their old or infirm kin. It often fills one valley, headland or "
            "mountainside, and the place often bears its founder's name. A "
            "large farm may hold several households, sometimes under one "
            "roof, and those with shares in a property may share the title.",
            "Every householder declares himself in thing with a godi of his "
            "own choosing. The tie is not feudal: it gives him a legal "
            "residence for the courts. Since everyone is in theory of some "
            "household, everyone belongs to a quarter and a district.",
        ),
        rules=paragraphs(
            "Owning land or milk animals makes a man a bondi; the bar is low, "
            "and a moderately prosperous tenant or hut man can form a "
            "household. A landowner must declare himself in thing even with "
            "no milk animals; a man with neither land nor milk animals "
            "belongs to the thing of the householder who takes him in (from "
            "Gragas).",
            "Richer baendur pay thing tax. Of those who pay it, a godi may "
            "require one in nine to go with him to the Althing; the rest pay "
            "for that retinue. Paying thing tax also gives full rights to sit "
            "on legal panels (p. 34) and full membership of the local "
            "hreppur. P. 21.",
        ),
    )
    b.faction(
        "Tenants",
        place=_place(b, "Iceland"),
        summary="Men who rent their land for a year at a time, taking it up or "
        "giving it up at the moving days. They count as baendur but may fall "
        "short of the thing tax.",
        rules="Moving days fall six weeks after the start of summer. Rent is at "
        "most a tenth of the land's value. The tenant must keep the land's "
        "value up, above all its full yield of hay. A landowner must keep a "
        "tenant who cannot feed his family until the next moving days. Pp. "
        "21-22.",
    )
    b.faction(
        "Hut Men",
        place=_place(b, "Iceland"),
        summary="Renters who do not farm: fishermen as a rule, or men of some "
        "other trade. Their living fails in famine even when they usually "
        "keep themselves, so they often move into the farmstead for the "
        "winter, and the landowner may ask for their labour in return.",
        rules="A landowner needs his local hreppur's leave for each hut man, so "
        "that he makes no more than he can support; without it both he and "
        "the hut man risk lesser outlawry. P. 22.",
    )
    b.faction(
        "Slaves",
        place=_place(b, "Iceland"),
        summary="Once common, captives of Irish, Scottish or Saxon stock and "
        "their children. By 1220 a slave is a rare sight, most likely brought "
        "from the mainland, where the trade goes on. Debt-slaves also exist, "
        "usually for a time only.",
        rules="P. 22.",
    )
    b.faction(
        "Freedmen",
        place=_place(b, "Iceland"),
        summary="Freed slaves, who stand as dependents of their former owners "
        "under a new contract. The children of freedmen are freeborn and owe "
        "nothing.",
        rules="The former owner must support a freedman who cannot support "
        "himself, inherits from one who dies with no heirs, and takes the "
        "blood money if one is killed. P. 22.",
    )


# -- customs --


def _customs(b: Builder) -> None:
    b.faction(
        "Honour among the Icelanders",
        place=_place(b, "Iceland"),
        rules=paragraphs(
            "Whoever gives, in gifts or in injury, is paid back in kind. "
            "Hiding what you have done is contemptible.",
            "Hof and ohof: the magi of a Toframanna Saga gain greatly by "
            "showing hof and shunning ohof. Pp. 22-23.",
        ),
        summary=paragraphs(
            "Honour stands at the centre of Icelandic life, and the coming of "
            "Christianity has not moved it: godar, priests, rich and poor all "
            "weigh a person by it first, and piety comes a distant second. "
            "Meekly offering the other cheek is a foreign idea to most.",
            "A man's honour rests on his stock, his land and his lawsuits as "
            "much as on his weapons. A well-run farm, good marriages for his "
            "kin and skill at law all earn it. This is no knight's code: it "
            "allows for stratagem and a measure of deceit, and creeping up by "
            "night to burn a family in its house does not stain it, so long "
            "as the deed is owned.",
            "Rank makes honour delicate. A plain farmer knows where he stands "
            "beside a chieftain, and each knows how to treat the other; where "
            "dominance or equality is open to question, offence is hard to "
            "avoid.",
            "Icelanders prize moderation, hof: the just and temperate man "
            "tends to prosper in the sagas. Its opposite, ohof, is excess and "
            "unfair dealing that frightens enemies, allies and the man's own "
            "kin alike, and those who practise it rarely last before other "
            "leaders band against them.",
        ),
    )
    b.faction(
        "Kin, Fostering and Vinfengi",
        place=_place(b, "Iceland"),
        summary=paragraphs(
            "Kin come first in any need. But the island is small and its "
            "great folk much intermarried, so a man often finds close "
            "relations on the other side of a quarrel. Help usually comes "
            "from the side of the family, from brothers and cousins, and "
            "less from uncles and nephews.",
            "So Icelanders make kin of the spirit as well. Children are "
            "fostered in another household by agreement between the fathers. "
            "Men blend their blood in a rite to become foster-brothers, sworn "
            "brothers or oath brothers, and when vengeance is due such kin "
            "are often more to be relied on than those of blood. Vinfengi is "
            "a formal friendship that promises political and legal support, "
            "now or later.",
        ),
        rules="P. 23.",
    )
    b.faction(
        "The Women of Iceland",
        place=_place(b, "Iceland"),
        summary=paragraphs(
            "Icelandic women have a real say in their own lives: they may own "
            "property and lead households, and answer to outlawry for injury "
            "and killing. Much of their power is worked behind the scenes, in "
            "feuds they help end or help keep alight, shaming men into action "
            "with unpaid debts or cooling hotheads before a squabble turns to "
            "blood.",
            "Marriage offers pass between fathers or guardians, but the woman "
            "is normally asked, and a widow may refuse. The groom pays a bride "
            "price and her family gives a dowry, both hers, and in a divorce "
            "she takes both with any increase. Some women choose instead to "
            "be a frilla, the concubine of a man of rank, as a folk saying "
            "recommends over a bad marriage; many such matches exist because "
            "kinship forbids marriage. Both divorce and the frilla survive in "
            "1220 against Christian teaching.",
        ),
        rules="Women cannot act as advocates or sit on legal panels; a woman "
        "with a godord uses a male representative at the things. A betrothed "
        "couple must by law own at least 120 law ounces between them, perhaps "
        "twenty years' saving for a landless worker; the law means to keep "
        "children from being born destitute and is hard to enforce. P. 23.",
    )
    b.faction(
        "Poets and Saga-Tellers",
        place=_place(b, "Iceland"),
        summary=paragraphs(
            "Weather and the long winter nights keep people indoors, and they "
            "fill the time with an occasional board game, stories and verse. "
            "Reciting sagas is a respected skill, and a traveller with many "
            "of them, well told, is welcome anywhere.",
            "A good poet adds to his name. His verses lean on Norse myth and "
            "show his learning as well as his craft, and the great saga "
            "heroes were warrior poets, ready at any moment with something "
            "witty, flattering, insulting or obscure. A poem can win a place "
            "as a king's retainer, save a neck or start a feud. A proper "
            "Icelander facing death should find a verse or several, and a man "
            "speared through the heart may still spend his last breath on a "
            "jest.",
        ),
        rules="P. 24.",
    )
    b.faction(
        "Letters and Learning",
        place=_place(b, "Iceland"),
        summary=paragraphs(
            "Literacy came with Christianity. The new faith needed more "
            "teachers than it had, so many godar and baendur took orders and "
            "learned Latin and letters, or sent sons abroad who came home "
            "with Scripture, and these godi-priests founded schools that "
            "still stand in 1220. The most famous are at the homes of the "
            "Haukdaelir at Haukadalur and the Oddaverjar at Oddi.",
            "Good Latin and letters are now common among wealthy men's sons, "
            "and authors such as Snorri Sturluson have lately begun writing "
            "verse and prose on Norse and Icelandic tradition.",
        ),
        rules="P. 24.",
    )
    b.university(
        "The School at Haukadalur",
        school="School",
        place=_place(b, "Haukadalur"),
        summary="One of the two most famous schools in Iceland, kept at the home "
        "of the Haukdaelir. P. 24.",
    )


# -- the economy --


def _economy(b: Builder) -> None:
    b.faction(
        "Homespun and the Three Ounces",
        place=_place(b, "Iceland"),
        summary=paragraphs(
            "Silver is scarce, so Icelanders trade in standard lengths of "
            "homespun, the woollen cloth they wear and sail under at home and "
            "abroad. Its quality and width are fixed: a bolt is two ells wide, "
            "and twelve ells of homespun means a sheet two ells across and "
            "twelve long.",
            "Wool in bulk, homespun, skins and dairy goods buy the imports. "
            "White falcons, bears, sulphur and walrus ivory go abroad as well, "
            "in small amounts. Rents and debts are mostly settled with the "
            "wool and dairy work of the household.",
        ),
        rules=paragraphs(
            "An ell is about 49 cm. The law ounce, the national rate for fines, "
            "is 6 ells. The standard ounce, the district rate for trade, rent "
            "and tithes, is 4 ells. The silver ounce, the international rate, "
            "is the true weight of silver. Eight ounces of any kind make one "
            "mark of that kind.",
            "The law council sets the law ounce's silver value each year; in "
            "1220 it is one-sixth of a silver ounce. So a silver ounce is "
            "worth 6 law ounces, 9 standard ounces or 36 ells, and a standard "
            "ounce is worth two-thirds of a law ounce. Prices are set in "
            "standard ounces at the spring things, district by district. Pp. "
            "24-25.",
        ),
    )
    b.faction(
        "Farm, Shore and Larder",
        place=_place(b, "Iceland"),
        summary=paragraphs(
            "In summer the farmers of a region share common land and highland "
            "pasture. Lambs and gelded rams go up to the highest grazing, while "
            "ewes and cows stay on the lower land by the dairies. Ewes left "
            "unmilked grow more and better wool, the cash crop, so the dairies "
            "run mostly on cow's milk, making butter, cheese and above all "
            "skyr, a thick curd that keeps through winter in great wooden vats "
            "half sunk in the ground. Grazing is largely held in common; what "
            "separates one farm from another is how much hay it makes and how "
            "well its farmer judges the stock it can carry.",
            "The commons give landless men a chance to rise. Seals are widely "
            "hunted, and a stranded whale, with its mountain of meat and "
            "blubber, can start a bitter dispute. Whale keeps fermenting in "
            "purpose-built pits. Blubber serves for frying where butter is "
            "short, for proofing leather and, from seals, for caulking boats; "
            "seal and shark oil burn in the lamps.",
            "Trout and char run all year and salmon in season, and may be "
            "smoked. Cod dries on open racks in the arctic wind, cheap work for "
            "one fisherman, and dried and smoked fish sell in quantity at home, "
            "above all in the fasts. Most meat is boiled and steeped in vats "
            "of sour whey; this surr can be eaten from the barrel. There are "
            "sausages of meat, suet, liver and blood. Salt is short, so butter "
            "is left to ferment sour and keeps a long time. Edible lichen "
            "stands in for meal, birds and their eggs are taken, and dried "
            "dung is the ordinary fuel.",
        ),
        rules="Pp. 25-26.",
    )
    b.faction(
        "Roads and Travellers",
        place=_place(b, "Iceland"),
        summary=paragraphs(
            "The descendants of famous seamen now have few ships, for want of "
            "wood. Horse paths reach almost every part of the land, and goods "
            "go by the tough native packhorses over steep and stony ways.",
            "Travellers usually sleep and eat at farms along the road. "
            "Hospitality marks an honourable man, and little is asked of a "
            "guest beyond good manners, a small gift, and his tales and gossip.",
        ),
        rules="A householder is bound by law to shelter only those on religious "
        "or legal errands, such as taking a child to baptism or going to thing "
        "for a case. Pointless wandering is illegal: an able-bodied man who "
        "does it is a tramp, and the penalty is lesser outlawry. The physically "
        "or mentally disabled are exempt, and a district usually shares their "
        "care by special arrangement. P. 26.",
    )
    b.faction(
        "Trade, Gifts and Raids",
        place=_place(b, "Iceland"),
        summary=paragraphs(
            "Iceland has no standing marketplace. Markets gather when there is "
            "cause: the things are yearly meetings where shoemakers, "
            "swordsmiths and the like ply their crafts, each bishop's see "
            "holds a fair on certain feast days, and locals flock to a trading "
            "ship to buy its goods and deal with each other. A fishing station "
            "comes nearest to a lasting market, but sells only fish.",
            "Prices differ from district to district, so a peddler can live "
            "by carrying goods between them and now and then saves enough for "
            "a farm of his own, but petty trading is despised and his low "
            "standing follows him. Long-distance trade is another matter: a "
            "man may buy much from a ship and sell it on at a profit with no "
            "shame, given capital and connections.",
            "Between near equals, exchange is one more move in the game of "
            "honour. The gift is its finest form, since it leaves the receiver "
            "to choose what comes back and when. Refusing a gift, or returning "
            "one at once, may show distrust or hostility; waiting too long may "
            "show resentment; and never answering may mean utter contempt or "
            "an admission of lasting superiority, as the case may be.",
            "A failed bargain may turn into a raid, the open taking of goods. "
            "Theft, the secret taking, is deeply dishonourable, and a serious "
            "lawsuit follows if it comes to light. A wasted journey is a bitter "
            "humiliation, and such an insult rarely goes unanswered, though "
            "most deals proposed between men of rank are well received and a "
            "trip to arrange a marriage is seldom thought hostile.",
        ),
        rules="Raiders are under forfeit immunity (p. 38): the defender may kill "
        "or hurt them without legal consequence, or may honourably stand aside "
        "and sue, so that the raider pays in the end at a price third parties "
        "set. Land, marriage and dowry deals are formalised by a witnessed "
        "handshake, the handsal. Pp. 26-27.",
    )


# -- the hreppar --


def _hreppar(b: Builder) -> None:
    b.faction(
        "The Hreppar",
        place=_place(b, "Iceland"),
        decides="A committee of five.",
        summary=paragraphs(
            "Every farmer belongs to a hreppur, a local cooperative with fixed "
            "bounds and no tie to the godar. It insures its members and looks "
            "after the poor who have no one legally bound to keep them, "
            "meeting at least three times a year to gather and share out "
            "tithes and other gifts for the poor.",
            "The old, the infirm and the mentally disabled are lodged with one "
            "household for a set term, then passed to another, so the burden "
            "falls on all the members by their wealth.",
        ),
        rules="A member who loses over a quarter of his herds to disease may "
        "recover half the loss, and half the value of fire damage to his home, "
        "at most three times in a lifetime. The other members fund it, each up "
        "to 1/120 of his total wealth; if that falls short, claims shrink in "
        "proportion. Full membership goes with paying thing tax (p. 21), and "
        "the hreppur licenses hut men (p. 22). The magicians keep a hreppur of "
        "their own on this model, the Galdramen Hreppur. P. 27.",
    )


# -- giants --


def _giants(b: Builder) -> None:
    home = _place(b, "Iceland")
    b.faction(
        "The Children of Ymir",
        realm="Magic",
        place=home,
        summary=paragraphs(
            "Giant and troll clans fell back to Iceland as men pressed into "
            "Scandinavia, and stayed when men followed, having nowhere further "
            "to go. They live in remote places of strong magic aura, many of "
            "them regiones or otherwise hard to reach, mostly in small "
            "families of one parent, often alone, and children.",
            "All descend from Ymir, the first frost-giant, whom Odin and his "
            "brothers slew to make the world. From his arms came a noble "
            "brood, friendly to gods and men, the primal powers: Mimir, Odin's "
            "friend and teacher; Bestla, Odin's mother; Natt, giantess of the "
            "Night; and the three Norns. From his feet came a foul and "
            "misshapen brood, sworn enemies of gods and men, most of them "
            "drowned when Ymir's blood flooded Jotenheim at his death.",
            "Christian Norsemen use troll and giant for the same thing. The "
            "learned draw a line: giants proper, the jotnar (one is a jotunn), "
            "are mighty in magic, often of the first brood and the true "
            "image of their race, while trolls are a fallen form, smaller, "
            "cave-dwelling, slow and man-eating, mostly of the second brood, "
            "their bodies showing how far they have sunk. The race divides "
            "into clans and families, and trolls and their ancestral clans "
            "commonly disown one another.",
            "Some giants shelter travellers, who in such remote parts are "
            "mostly outlaws, and a number of Icelandic trollsynir (p. 51) come "
            "of bored, lonely daughters of such hosts and an occasional "
            "outlaw. Most giants have no love for humans, but few ever meet "
            "one, for men in their right minds stay out of the ice and fire "
            "where giants live.",
        ),
        rules="No more than four hundred giants in Iceland in 1220. Pp. 29-31.",
    )
    clans = (
        (
            "The Clan of Hrym",
            "The Frost giants under Hrym, the largest clan. Frost was the power "
            "pagan Norsemen feared most and felt closest. They are implacable "
            "and tireless in their aims, often the wisest of giants, and man's "
            "greatest foes.",
            "Wise, Vengeful, Hateful",
            "Pp. 30-31.",
        ),
        (
            "The Clan of Thrym",
            "The Noise giants or Storm giants, the gale's shriek and the "
            "thunderclap, who blast crops and waste the ground. The most violent "
            "of giants, they revel in destruction at every chance, are slow "
            "of wit and easily fooled.",
            "Violent, Gullible, Greedy",
            "P. 31.",
        ),
        (
            "The Clan of Geirrod",
            "The Fire giants, wildfire in the woods and the lightning's stroke; "
            "the most hotheaded of giants, yet often the cleverest.",
            "Sly, Quick-Tempered, Meticulous",
            "P. 31.",
        ),
        (
            "The Clan of Gymir",
            "The Sea giants, the whirlpool and the storm-wave. Aegir and his "
            "dreadful wife Ran, its best known, were once worshipped as gods. "
            "They are the most changeable of giants, famous for their "
            "hospitality and not at all for courage.",
            "Fickle, Hospitable, Cowardly",
            "P. 31.",
        ),
        (
            "The Clan of Bergelmir",
            "The Rock giants, who cause avalanches and earthquakes: one of the "
            "oldest lines and the most degenerate, many having lost their "
            "magic and grown more trollish with the centuries. Often slow "
            "but brave, and proud to the point of stupidity.",
            "Proud, Slow Witted, Boastful",
            "Pp. 31-32.",
        ),
    )
    for name, words, traits, pages in clans:
        b.faction(
            name,
            realm="Magic",
            place=home,
            summary=words,
            rules=f"Typical personality traits: {traits}. {pages}",
        )
    b.faction(
        "The Children of Surt",
        realm="Magic",
        place=home,
        ruler="Surt",
        summary="Fire beings apart from Geirrod's clan, living in the world's "
        "hottest places, foes of gods and men, the very sign of volcanoes and "
        "lava flows. Surt, who leads them, will burn the world when Ragnarok "
        "is over.",
        rules="P. 32.",
    )
    b.faction(
        "The Etin Brides",
        realm="Magic",
        place=home,
        summary="Giantesses on friendly terms with gods and men, from any of the "
        "five clans, though their brothers and sisters may hate mankind. "
        "Several Norse kings and heroes had one for a blood-mother or "
        "foster-mother.",
        rules="Likely the mothers or grandmothers of any player character "
        "trollsynir. P. 32.",
    )


# -- landvaettir --


def _landvaettir(b: Builder) -> None:
    home = _place(b, "Iceland")
    b.faction(
        "The Landvaettir",
        realm="Faerie",
        place=home,
        summary=paragraphs(
            "Landvaettir (one is a landvaett) is the catch-all word for the "
            "host of spirits of Iceland, which swarmed with them before people "
            "came. The first Norse settlers took care to unship the dragon "
            "prows of their longships before nearing land, so as not to "
            "frighten them. When temples rose, some spirits grew close to the "
            "gods worshipped there, and so to the worshippers, and the "
            "Islendinga Saga tells of the great harm they did when Christians "
            "destroyed those temples.",
            "There are four broad kinds: the true landvaettir, the alfar, the "
            "husvaettir and the yarthkin.",
        ),
        rules=paragraphs(
            "Landvaettir partake of both Magic and Faerie: those closest to "
            "mankind are nearest the fay, and those who kept apart as pure "
            "spirits of nature nearest the Magic Realm. For realm interaction "
            "treat them all as using Faerie power, except in magical auras, "
            "where they count as magical creatures; both sorts are therefore "
            "met in the magical auras that dot the land.",
            "The few faerie auras are mostly heathen temple sites the Dominion "
            "has not taken, which also draw landvaettir, chiefly those who "
            "served there. All Icelandic spirits are by nature invisible and "
            "insubstantial; some can become visible, or material, not always "
            "both at once. Pp. 32-33.",
        ),
    )
    b.faction(
        "The True Landvaettir",
        realm="Magic",
        place=home,
        summary="Creatures of pure magic in Iceland's wildest places, the most "
        "remote and least fathomable of its spirits, capable of good and ill, "
        "and mostly happy to keep away from people. To the Second Sight they "
        "usually look like animals, the strongest like dragons and other "
        "fantastic beasts.",
        rules="They are the chief source of galdramen's magic (ch. 6). Their "
        "Might counts as ten points higher against a faerie-affecting spell. "
        "P. 33.",
    )
    b.faction(
        "The Fylgjur",
        realm="Magic",
        place=home,
        summary=paragraphs(
            "Spirits (one is a fylgja) that attach themselves to particular "
            "people, close kin to the old Norse idea of the soul, and passed "
            "down from an ancestor like any other trait. Most are invisible "
            "and immaterial; those who can see them speak of animal shapes "
            "and sometimes giants. A seithkona's is most often a falcon, cat "
            "or hare, the beasts of the goddess Freyja. Heroes of legend had "
            "strong ones that could appear and fight, and magicians are known "
            "for theirs.",
            "A fylgja warns by a dream of an animal that hints at the danger, "
            "by an unseen daytime appearance in a scene that mirrors it, or by "
            "getting under its ward's feet, so that a stumble for no reason may "
            "be a warning. That is usually all it can do in the physical world.",
        ),
        rules=paragraphs(
            "Usually Magic Might about 10, with few powers and little reach "
            "into the physical world. Icelanders with the Premonitions Talent, "
            "as all galdramen have, get their premonitions from it. Premonitions "
            "is common among Icelanders, and fylgjur take special offence at "
            "malign magic on their wards or families, so such magic hardly ever "
            "passes unnoticed and unrecognised.",
            "They count among the true landvaettir, so their Might is ten "
            "points higher against a faerie-affecting spell. Pp. 32-33.",
        ),
    )
    b.faction(
        "Hamingja",
        realm="Magic",
        place=home,
        summary="Fylgjur so devoted that they take human form, often giants or "
        "warrior-women.",
        rules="Best represented by the Guardian Angel or Ghostly Warder Virtue. P. 32.",
    )
    b.faction(
        "The Alfar",
        realm="Faerie",
        place=home,
        summary="Alfar (one is an alf) are the spirits who have had most to do "
        "with people, above all in the pagan temples, and many still serve "
        "the deities they knew before Iceland turned Christian. House Merinita "
        "will find them familiar, for they are much like the sidhe. Thor, "
        "Frey, Baldur and Odin were the four best loved gods of heathen "
        "Iceland, and each has his alfar.",
        rules="P. 33.",
    )
    for name, words in (
        (
            "The Alfar of Thor",
            "Fiercely protective of people against trolls and giants. They "
            "show themselves to warn communities of raids, and may even help "
            "drive the danger off if well treated.",
        ),
        (
            "The Alfar of Frey",
            "Concerned with the fertility of land and livestock and the health "
            "of all living things.",
        ),
        (
            "The Alfar of Baldur",
            "Followers of the god of peace, the gentlest and kindest of their "
            "race, who have been known to heal those in great need.",
        ),
        (
            "The Alfar of Odin",
            "The most warlike of their race, bloodthirsty yet at heart "
            "benevolent, and hard for many people to deal with.",
        ),
    ):
        b.faction(name, realm="Faerie", place=home, summary=words, rules="P. 33.")
    b.faction(
        "The Husvaettir",
        realm="Faerie",
        place=home,
        summary="House-spirits, close allies of the alfar and much like the "
        "brownies and other low faeries of the mainland. They often live in "
        "rocks near a settlement and, for gifts of food, help with chores, "
        "drive off vermin and are a blessing to the family. Slighted, they "
        "have driven families out of their homes with spite and noise.",
        rules="P. 33.",
    )
    b.faction(
        "The Yarthkin",
        realm="Magic",
        place=home,
        summary="Spirits of any of the other kinds whose growing dislike of "
        "people has turned them towards malice. They are found all over "
        "Iceland, most of all near giants and trolls.",
        rules="Summoned when galdramen sing curse-songs and disease-songs. Their "
        "Might counts as ten points higher against a faerie-affecting spell. "
        "P. 33.",
    )
    b.faction(
        "The Tramar",
        realm="Magic",
        place=home,
        summary="Yarthkin who are spirits of evil magic.",
        rules="P. 33.",
    )
    b.faction(
        "The Kveldrida",
        realm="Magic",
        place=home,
        summary="Yarthkin who are spirits of sickness, often seen as old women "
        "riding three-legged horses.",
        rules="P. 33.",
    )


# -- the creature blocks --


def _creatures(b: Builder) -> None:
    b.creature(
        "Troll",
        page="p. 30",
        realm="Magic",
        might=20,
        form="Corpus",
        size=2,
        how_many="Many, in the mountains and caves",
        block={
            "characteristics": characteristics(-3, -1, -2, -2, 6, 4, -1, -2),
            "abilities": [
                ("Shapeshifter", 5, ""),
                ("Living Language: Jotunn", 5, ""),
            ],
            "traits": {"Aggressive": 2, "Territorial": 2},
        },
        attacks=[
            b.attack("Brawl (fist)", 4, 4, 1, 8),
            b.attack("Club", 6, 6, 4, 13),
            b.attack("Rock", 7, 4, 0, 10),
        ],
        soak=15,
        fatigue_levels=TROLL_FATIGUE,
        powers=[
            b.power(
                "Shapeshift",
                1,
                -3,
                "Corpus",
                rtd=PERSONAL,
                does="Every troll changes shape as if with the Shapeshift Talent "
                "at 5; the book gives +7 on the roll, from Intelligence -3 and "
                "Speak Jotunn 5. Each change costs 1 Might; going back to troll "
                "form costs none.",
            ),
            b.power(
                "Curse",
                2,
                -4,
                "Vim",
                does="CrVi. Most trolls can curse an opponent, few with any "
                "cunning, as if with the Curse Talent at 7; the book gives +9 "
                "on the roll, from Intelligence -3 and Speak Jotunn 5.",
            ),
            b.power(
                "Hex",
                0,
                -2,
                "Vim",
                does="CrVi. Anyone fighting a troll has exceedingly bad luck: "
                "a stress die botches on a 0 or a 2, twice the chance, and "
                "always with two extra botch dice.",
            ),
            b.power(
                "Gift of the Magic Arts",
                1,
                -3,
                "Vim",
                does="About one troll in 100, usually female and with "
                "Intelligence +1. Though they do not study the Hermetic Arts, "
                "they can approximate any Hermetic spell for 1 Might per 5 "
                "levels (the cost shown), up to level 25. Groups can share the "
                "Might of a higher spell, taking about a minute per 5 levels "
                "to cast it.",
            ),
        ],
        vis=[BodyVis(5, "Corpus", "in the body; more if particularly powerful")],
        appearance="Six to ten feet tall, broad in the shoulder and hairless, "
        "with huge hands and deeply carved faces; brown or grey skin with the "
        "feel of weathered rock. Not all are monstrous, and some can pass for "
        "tall humans.",
        notes=paragraphs(
            "Trolls live underground in deep caves or tunnels of their own "
            "digging, and count a whole mountain range as home. They are known "
            "as stupid and hostile, and are easily fooled if a trickster lives "
            "long enough to speak to one. Farmers near a troll may find it "
            "guarding them as part of its territory, while travellers get "
            "volleys of stones from the heights.",
            "The book disagrees with itself: p. 30 has trolls that help nearby "
            "farmers and some that can pass for tall humans, and p. 31 says "
            "trolls are always hostile to humans. Both are kept; the storyguide "
            "chooses.",
            wound_ranges(2),
            "Converted: combat totals and Soak as printed, the old Fatigue "
            "column (+9) left out; a Rock has no Defense (n/a), shown as 0. The "
            "book prints no combat Abilities. Fatigue as printed, four levels at "
            "0 or better. Speak Jotunn 5 is read from the powers. Might Form "
            "Corpus is this pack's reading, from the body vis. P. 30.",
        ),
    )
    b.creature(
        "Giant",
        page="p. 31",
        realm="Magic",
        might=30,
        form="Corpus",
        size=6,
        how_many="No more than four hundred in Iceland in 1220",
        block={
            "characteristics": characteristics(0, 6, -4, 0, 15, 20, -1, -1),
            "abilities": [
                ("Living Language: Jotunn", 5, ""),
            ],
        },
        attacks=[
            b.attack("Brawl (fist)", 6, 4, -2, 21),
            b.attack("Club", 10, 8, 4, 31),
            b.attack("Boulder", -1, 10, 0, 45),
        ],
        soak=26,
        fatigue_levels=GIANT_FATIGUE,
        vis=[BodyVis(12, "Corpus", "in the body")],
        notes=paragraphs(
            "Boulders: a hit kills most targets of human size. The boulder may "
            "roll, skip, sink or shatter, by the surface it lands on and the "
            "storyguide's choice. An attack that misses by 3 or less is a "
            'grazing blow of "only" +15 damage.',
            "Magical Abilities: many giants have strong magic and may be "
            "treated as trollsynir (ch. 6), with Magic Might 30 or their "
            "resistance as trollsynir (p. 53), whichever is higher. Even those "
            "who have not developed it often have the Jotunn Affinity of their "
            "clan, and most can Shapeshift. Curse, Svonhverfing and Transform "
            "also suit them. All speak the magical language Jotunn as natives, "
            "and those who specialise in magic have high Potency scores.",
            "Personality traits as for the clan.",
            wound_ranges(6),
            "Converted: combat totals and Soak as printed, the old Fatigue "
            "column (+25) left out; Soak 26 is before armor, and a Boulder has "
            "no Defense (n/a), shown as 0. The book prints no combat Abilities. "
            "Native Jotunn taken as 5. Might Form Corpus is this pack's reading, "
            "from the body vis. P. 31.",
        ),
    )


# -- the seeds --


def _stories(b: Builder) -> None:
    dormant(
        b.threat(
            "A Matter of Honour",
            antagonist="A rival who declares Wizard's War on a young covenant",
            summary="A story seed. A magus's Icelandic apprentice has finished "
            "training and accepted a place at a distant spring covenant, which "
            "angers a local rival. P. 22.",
            stages=[
                b.stage(
                    "The filius's letter",
                    at=1,
                    clues="The rival declares Wizard's War on the young magi. "
                    "The filius writes to his parens that he will not be driven "
                    "off, and asks for help negotiating a settlement.",
                ),
                b.stage(
                    "The Redcap's news",
                    at=2,
                    clues="The Redcap bringing the letter also reports that the "
                    "covenant has been annihilated.",
                    ignored="The filius goes unavenged.",
                ),
            ],
        )
    )
    dormant(
        b.threat(
            "The Neighbour Whose Harvest Never Fails",
            antagonist="A greedy neighbour and whoever blesses his land",
            realm="Magic",
            summary="A story seed. A neighbour of the covenant has good "
            "harvests in the worst weather and has grown rich, asking silver, "
            "almost unobtainable in Iceland, for his grain and meat. Perhaps a "
            "witch charmed his fields with magical stones buried at the "
            "boundaries; perhaps he is a friend of the landvaettir. P. 26.",
            stages=[
                b.stage(
                    "The price in silver",
                    at=1,
                    clues="The neighbour prospers and demands silver.",
                ),
                b.stage(
                    "The crops fail",
                    at=2,
                    clues="His greed has upset his benefactor, whoever that is, "
                    "and his crops suddenly fail.",
                ),
            ],
        )
    )
    dormant(
        b.threat(
            "The Lean Year",
            antagonist="Hunger",
            summary="A story seed. Some years even the best farmers cannot feed "
            "their households. When it strikes the magi, will they let people "
            "starve, and if not, how can they make it up when most of the "
            "island is likely as short as they are? P. 26.",
        )
    )
    dormant(
        b.threat(
            "The Sheep in the Canyon",
            antagonist="A giant ten times the height of a man",
            realm="Magic",
            summary="A story seed. The covenant's livestock goes missing, always "
            "in one canyon deep in the mountains. The shepherds find a giant is "
            "taking them, and he seems beyond defeating. Bargaining may be the "
            "only way, once someone is found who speaks the giants' language. "
            "P. 26.",
        )
    )
    dormant(
        b.threat(
            "Money for Nothing",
            antagonist="The magi's own conjured silver, and King Hakon",
            summary="Storyguide advice from the book, kept as a story. Iceland's "
            "economy is tiny beside the mainland's, and Hermetic magic makes "
            "precious metal easily. Storyguides should weigh what conjured "
            "wealth would do, and may wish to discourage it. P. 25.",
            stages=[
                b.stage(
                    "Silver loses its value",
                    at=1,
                    clues="New silver is noticed almost at once and quickly "
                    "cheapens in local exchange, leaving it good only for "
                    "trade with Norwegian merchants.",
                ),
                b.stage(
                    "The merchants notice",
                    at=2,
                    clues="Merchants soon see how much silver Icelanders hold. "
                    "More ships come, which helps Iceland.",
                ),
                b.stage(
                    "Rumours reach King Hakon",
                    at=3,
                    clues="Talk of silver mines sharpens King Hakon's wish for "
                    "overlordship.",
                ),
            ],
        )
    )
    dormant(
        b.threat(
            "Between Magic and Faerie",
            antagonist="A question of metaphysics",
            realm="Faerie",
            summary="A story seed. Merinita magi may be fascinated by landvaettir, "
            "which unlike mainland faeries are as at home in magical auras as "
            "in faerie ones. What that means could take a lifetime to work "
            "out. P. 33.",
        )
    )
