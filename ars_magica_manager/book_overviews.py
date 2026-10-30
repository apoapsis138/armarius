"""A short overview of each sourcebook, for Saga Content's Books chapter:
what it is about and what it gives a troupe, summarized in our own words
from the book. A book not in the library has none."""

from __future__ import annotations

#: What a book without an overview says.
NONE_YET = "No overview yet."

#: Abbreviation (sourcebooks.SOURCEBOOKS) -> its overview.
OVERVIEWS: dict[str, str] = {
    "DE": (
        "The complete core rulebook, revising and expanding Fifth Edition. It "
        "covers the Order of Hermes, character creation for magi, companions "
        "and grogs, covenants, Hermetic magic, the laboratory, spells, the "
        "realms, a bestiary and Mythic Europe. A troupe needs nothing else to "
        "run a saga."
    ),
    "A&A": (
        "A guide to learning and the arts in thirteenth-century Mythic Europe: "
        "the liberal arts, philosophy, medicine, schools and universities. "
        "Troupes get rules and ideas for scholar, healer, artist and performer "
        "companions, plus experimental philosophy, formal debate and tracking "
        "an artist's rising fame."
    ),
    "AM": (
        "Nine lost magical traditions, from the Language of Adam and curse "
        "tablets to Hyperborean hymns and runes. Each chapter offers legends, "
        "story hooks and sites for the quest, plus rules for folding the "
        "discovery into Hermetic theory through breakthroughs. Many of these "
        "secrets stretch or break the limits of magic."
    ),
    "App": (
        "A short book on childhood, following a character from birth to the end"
        " of apprenticeship, Gifted or not. It offers rules for creating young "
        "characters, opening Arts, teaching, low-level spells for children, and"
        " the Gauntlet, along with advice for telling stories about children "
        "and failed apprentices."
    ),
    "AtD": (
        "The Transylvanian Tribunal, where House Tremere runs a disciplined, "
        "interdependent Order from oppida rather than Western-style covenants, "
        "and magic is lawful. It surveys the Hungarians, Bulgarians, Slavs and "
        "border peoples, and supplies dragons, giants, vampires, storm wizards "
        "and vampire hunters, plus advice on horror stories."
    ),
    "B&S": (
        "The Levant Tribunal in 1220, from Egypt to Asia Minor (a Fourth "
        "Edition book). It covers the region's history, the Latin states, the "
        "Hermetic covenants and mythic sites, and gives much of its space to "
        "Islam, with rules for Muslim characters and Middle Eastern magic."
    ),
    "BS&S": (
        "North Africa from the Atlantic to the Siwa Oasis, excluding Egypt and "
        "Ethiopia, built on the themes of wonder and hunger. With no covenants "
        "established there, it suits expeditions or African sagas. Troupes get "
        "Berber, Arab and Tuareg cultures, desert trade routes, settut amulet "
        "magic, minor traditions, monstrous races and jnun."
    ),
    "C&G": (
        "Life in towns: charters, governance, crime, disease, labor, guilds and"
        " craft. Rules cover workshops and making goods, including wondrous "
        "items, while travel, ship combat, fairs, markets and trade complete "
        "the picture. Troupes can play craftsmen and merchants of every scale, "
        "and see how far magi may meddle in commerce."
    ),
    "Cal": (
        "A classic adventure, revised for Fifth Edition, in which characters "
        "explore the ruins of a covenant destroyed fifty years ago and uncover "
        "why it fell. Part mystery, part dungeon, it can be placed anywhere in "
        "Mythic Europe, runs about five sessions, and may seed a whole saga."
    ),
    "Covenants": (
        "An expansion of covenant design and upkeep, with nearly 200 Boons and "
        "Hooks to steer a saga's stories. It also covers governance and "
        "charters, covenfolk, finances and vis sources, then turns to "
        "libraries, book production, sancta and personalized laboratories, with"
        " record sheets for tracking it all."
    ),
    "D&B": (
        "The Novgorod Tribunal, a Fourth Edition book on Poland and Russia: a "
        "vast, young, thinly settled Tribunal torn by conflict. It details "
        "Slavic society, magic, faeries and old gods, the Hermetic covenants "
        "and the Bjornaer split, with the Mongol invasions looming, plus "
        "shamans and advice for sagas set there."
    ),
    "DI": (
        "Four long campaigns that each bring the end of Mythic Europe: a "
        "doomsday cult within the Order, an endless Fimbulwinter, a pestilence "
        "devouring the Magic Realm, and the freed titans. Each begins inside "
        "ordinary play and grows over many game years, giving a troupe a "
        "climactic finale for a saga."
    ),
    "F&F": (
        "The Provençal Tribunal, covering the Languedoc, Gascony, the Pyrenees "
        "and Arelat. Troubadours, heresy and the Albigensian Crusade tear at "
        "the region as House Flambeau's old dominance fades. Troupes get "
        "regional history, Hermetic culture, Basque folklore creatures and "
        "mythic sites, plus the lost covenant of Val-Negra."
    ),
    "GGHS": (
        "A single reference gathering every Hermetic spell from 42 Fifth "
        "Edition books, arranged by Art and level, with each entry naming its "
        "source and errata applied through August 2021. An alphabetical index "
        "helps troupes look up spells without leafing through the line. Non-"
        "Hermetic spells and creature powers are left out."
    ),
    "GotF": (
        "The Rhine Tribunal in 1220: the oldest and largest in the Order, home "
        "to Durenmar and other ancient forest covenants, now stagnant and "
        "squabbling. It surveys German history, Tribunal customs, the forests "
        "and each region, and offers saga plans, including the full Curse of "
        "the Rhine Gorge."
    ),
    "Grogs": (
        "A book devoted to covenfolk, from soldiers to craftsmen and scholars. "
        "The first half covers grogs in the covenant, on their own, and in "
        "stories alongside magi, with quick ways to create and maintain them. "
        "The second half supplies many character concepts, new Virtues and "
        "Flaws, and story ideas."
    ),
    "HMRE": (
        "Six hedge-wizard traditions still active in 1220 that draw on the "
        "Magic realm: elementalists, folk witches, gruagachan, learned "
        "magicians, nightwalkers and vitkir. A troupe gets rules for playing or"
        " facing them, plus ways for hedge lore to feed Hermetic research or "
        "for a convert to enter the Order through House Ex Miscellanea."
    ),
    "HoH:MC": (
        "Covers Houses Bjornaer, Criamon, Merinita and Verditius, the Order's "
        "mystery-cult Houses. Each gets its history, customs and inner secrets,"
        " with initiation scripts and new Virtues and Flaws, so a troupe can "
        "play out the heartbeast, the Criamon Paths, Arcadian and faerie lore, "
        "and Verditius enchantment."
    ),
    "HoH:S": (
        "The closing volume of its series, on Houses Flambeau, Jerbiton, "
        "Tytalus and Ex Miscellanea. Troupes get schools of magical combat and "
        "Wizard's War, the magic of perception and illusion, intrigue with "
        "disguises and agents, formal debate, and eight Ex Miscellanea "
        "traditions complete with their non-Hermetic powers."
    ),
    "HoH:TL": (
        "Details Houses Bonisagus, Guernicus, Mercere and Tremere. A troupe "
        "gets original-research rules that any magus can use, the Code of "
        "Hermes and Tribunal procedure with advice on running a Quaesitor, the "
        "Redcaps' many trades and Mercere's portals, and Tremere's structure "
        "and styles of certamen."
    ),
    "Hooks": (
        "Eight short scenarios, each meant for about one session, that draw a "
        "covenant towards the material of another Fifth Edition supplement, "
        "from a faerie abduction to a dispute over the Code. None needs its "
        "target book; a troupe can play them as one-offs or sample a kind of "
        "story before expanding it."
    ),
    "HP": (
        "Six grand undertakings needing only core Hermetic magic: a covenant "
        "inside a volcano, a tower aimed at Heaven, an enchanted shipyard, "
        "unseen attacks for Wizard's War, immortality and a menagerie of "
        "beasts. Each supplies spells, devices and laboratory totals to follow "
        "across a career, plus advice on designing a troupe's own project."
    ),
    "HtM": (
        "A Fourth Edition sourcebook on England and Wales around 1220 and the "
        "magi of the Stonehenge Tribunal. It has no game statistics, so players"
        " can read it too: history, peasants, towns, Church, nobility, law, "
        "Hermetic politics and genuine medieval legends, offering background "
        "and story ideas rather than a ready-made saga."
    ),
    "L&L": (
        "A setting book for the Normandy Tribunal in 1220, spanning northern "
        "France from Brittany to Burgundy. It gives the regions and towns, "
        "fifteen covenants, the feudal bonds between covenants, the Hermetic "
        "tourney and the Tytalus presence here, along with saga plans, some "
        "built around the covenant of Confluensis."
    ),
    "LoH": (
        "Five legendary magi of the Order's past, each told in full with a "
        "legacy still waiting to be found: Conciatta's research into Divine "
        "auras, Fortunata's island of spirits, Hérisson's garden, Hermanus's "
        "vanished laboratory and Thomae's flying castle. Each chapter frames "
        "stories of rediscovery and lists what magi remember, true or false."
    ),
    "LotN": (
        "The Nile valley in the thirteenth century, from Egypt through Nubia to"
        " Ethiopia, shown as its own people believed it to be. A troupe gets "
        "Egyptian characters, an Ethiopian bestiary, pagan monuments and "
        "ancient treasures, the struggle of the Red and the Black, and covenant"
        " sites for sagas of tombs and lost secrets."
    ),
    "LoM": (
        "The warrior nobility of Mythic Europe: how careers rise under a lord, "
        "what titles are worth, and how nobles pass their leisure. Rules for "
        "manorial fiefs, peasant life, massed battles and sieges, single combat"
        " and arms suit realistic, romantic or political sagas, or a noble who "
        "serves a covenant."
    ),
    "ML": (
        "Ten self-contained supernatural sites across Mythic Europe, among them"
        " Bath, the Farne Islands, Saint Patrick's Purgatory, a fallen temple "
        "of Mercury and a faerie toy fair. Each is detailed with several ways "
        "into a saga and reasons to return, and could serve as a one-off visit "
        "or a covenant's home."
    ),
    # Not in the library, so nothing to summarize.
    "MC": "",
    "MoH": (
        "Fifteen unusual magi from eight Houses, each given full statistics at "
        "Gauntlet and at fifteen-year steps afterwards. A troupe can use them "
        "as ready-made player or supporting characters at many levels of power,"
        " or take their new spells and enchanted items for its own saga as lab "
        "texts or inventions."
    ),
    "RM": (
        "Four magical traditions strong enough to challenge the Order of "
        "Hermes: the Amazons, the Augustan Brotherhood, the Muspelli and the "
        "Sorcerers of Soqotra. Alongside each tradition's magic and culture, it"
        " sets out common rules for non-Hermetic magic, giving a troupe rivals "
        "to fight, outmanoeuvre or study for Hermetic research."
    ),
    "RoP:D": (
        "The Divine realm in full: the Dominion and holy auras, angels, saints,"
        " relics, miracles and True Faith, with Christianity, Islam and Judaism"
        " each set out through history, beliefs and characters. Troupes get "
        "holy traditions, character templates and Holy Magic, whether the "
        "Divine stays in the background or becomes a saga's focus."
    ),
    "RoP:F": (
        "A guide to Faerie, the realm that feeds on human belief and takes its "
        "shape from stories. It covers the realm and its places, rules for "
        "designing and playing faerie characters, a bestiary, mortals touched "
        "by faerie power, faerie wizardry, and advice on telling faerie tales."
    ),
    "RoP:I": (
        "Evil laid out for play: sin and temptation, infernal auras, and the "
        "ranks of demons, with sample fiends as corrupters, deceivers and "
        "destroyers. Storyguides gain antagonists and ways to darken a saga; "
        "players gain rules for tainted characters, infernalists, diabolic "
        "powers, goetic summoning and traditions dealing with Hell."
    ),
    "RoP:M": (
        "The realm magi know best: auras, regiones, vis and the Magic Realm "
        "itself, built on the idea that magic draws things toward their ideal "
        "form. Troupes get rules for magical characters and many examples of "
        "animals, humans, spirits and things shaped by magic, with an appendix "
        "of mundane beasts."
    ),
    "SiS": (
        "A short Fourth Edition download extending Blood and Sand, the Levant "
        "Tribunal book. It adds rules for Hermetic magi who work Islamic ideas "
        "into their magic, statistics for magi of the Levant's covenants, and a"
        " potent talisman taken from the Arabian Nights."
    ),
    "SoI": (
        "Fourth Edition sourcebook for the Greater Alps, whose covenants keep a"
        " long peace through trading services and enforcing Hermetic law "
        "strictly. It details those covenants, their magi and Roman-flavoured "
        "customs, plus regional geography and history, with ways to fit new "
        "magi in and space for a troupe's own covenant."
    ),
    "TC": (
        "A portrait of the Western Church in 1220, from parish and diocese to "
        "monastic rule, women, the corrupt, the Templars and the Franciscans. "
        "It helps a troupe make clergy into a covenant's allies, rivals or "
        "troubles, and leaves each saga to decide how much the Church knows of "
        "the Order."
    ),
    "TC&TC": (
        "Setting guide to the Mythic Middle East beyond the Levant: Arabia, "
        "Mesopotamia, Persia and the Silk Road. Covering the Order of Suleiman,"
        " the jinn and Mythic Zoroastrianism, it offers exotic characters, non-"
        "Hermetic allies or foes, a story arc abroad, or a whole saga with or "
        "without Hermetic magi."
    ),
    "TCI": (
        "Mythic Ireland in 1220, where Irish kings and English lords raid each "
        "other and quarrelsome magi share the island with stubborn hedge "
        "wizards. Province by province it presents covenants, factions and the "
        "four realms' landscapes, inviting a troupe to drive, temper or resist "
        "the Tribunal's coming upheaval."
    ),
    "TME": (
        "Three ways for magi to remake the world: joining medieval society as a"
        " Fourth Estate, raising an island realm from the sea, or spreading "
        "enchantments as a kind of technology. It offers rules for politics and"
        " invention, story seeds and advice for the long sagas such change "
        "demands."
    ),
    "TMRE": (
        "The secret magics Mystery Cults teach across House lines, with "
        "initiation rules and storyguide advice. Troupes gain paths such as "
        "alchemy, astrology, divination, spirit magic, theurgy, arithmetic "
        "magic, dream magic and Mercurian magic, along with sample cults that "
        "make useful patrons or rivals, and notes on immortal magi."
    ),
    "ToME": (
        "Nine short adventures covering demons, faeries, magic and everyday "
        "trouble. They include contests in Ulster, a light-hearted voyage, a "
        "village murder mystery, a noble widow's legal battle and a family "
        "feud, so a troupe can pick stories to suit magi, companions or "
        "sometimes grogs."
    ),
    "ToP": (
        "Five stand-alone adventures for powerful magi some fifty or sixty "
        "years past apprenticeship, with their advanced companions and grogs. "
        "They range from a contested papal election to the lost City of Brass "
        "and the pirate Eustace, and can be strung together into a saga of "
        "spectacular deeds."
    ),
    "TSE": (
        "Sourcebook for the Theban Tribunal in 1220: Greece, the Aegean "
        "islands, Constantinople and Anatolia after the sack of 1204. Vis is "
        "plentiful and Hermetic society unusually egalitarian. It presents "
        "covenants, magi, Greek culture and legends, and each realm's "
        "landscape, leaving room for a troupe's own covenants."
    ),
    "TtA": (
        "Five fully detailed covenants, one for each stage of a covenant's "
        "life, from a Spring fleet at sea to a Second Spring rebuilding in the "
        "Rhine. Each comes with magi, covenfolk, vis, books and story threads, "
        "ready as a player covenant, a neighbour, or a model for your own."
    ),
    "TTT": (
        "Five story cycles, each of three linked adventures set years apart, so"
        " they can unfold across a saga with troupe members taking turns as "
        "storyguide. Demons, revenants, Church intrigue, noble secrets and old "
        "Hermetic betrayals feature, and early choices return as later "
        "consequences."
    ),
}


def overview(book: str) -> str:
    return OVERVIEWS.get(book) or NONE_YET
