"""The covenants of the western and northern Rhine, as of spring 1220:
Durenmar and Dankmar in the Black Forest, Triamore on the Meuse,
Waddenzee on Terschelling, Oculus Septentrionalis in Lübeck and
Fengheld in the Harz with its chapter houses -- each with its magi, its
notable covenfolk and its library, in paraphrase of Guardians of the
Forests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..builder import paragraphs, secrets

if TYPE_CHECKING:
    from ...models import Covenant, Tribunal
    from ..builder import Builder
    from . import Rhine

# House ids, so a typo cannot slip into a record.
BJORNAER = "house_bjornaer"
BONISAGUS = "house_bonisagus"
CRIAMON = "house_criamon"
EX_MISC = "house_ex_miscellanea"
FLAMBEAU = "house_flambeau"
GUERNICUS = "house_guernicus"
JERBITON = "house_jerbiton"
MERCERE = "house_mercere"
MERINITA = "house_merinita"
TREMERE = "house_tremere"
TYTALUS = "house_tytalus"
VERDITIUS = "house_verditius"

# The lead line of a covenant's notes, before its secrets.
STORYGUIDE = "What the players do not know."


def _lines(*lines: str) -> str:
    """The lines as one text, one hook or secret a line."""
    return "\n".join(lines)


def build(rhine: Rhine) -> None:
    b = rhine.b
    tribunal = rhine.tribunal
    assert tribunal is not None
    _durenmar(rhine, b, tribunal)
    _dankmar(rhine, b, tribunal)
    _triamore(rhine, b, tribunal)
    _waddenzee(rhine, b, tribunal)
    _oculus(rhine, b, tribunal)
    _fengheld(rhine, b, tribunal)


# ---------------------------------------------------------------- Durenmar


def _durenmar(rhine: Rhine, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "Domus magna of House Bonisagus and the oldest covenant in the "
        "Order, Durenmar fills a hidden, steep-sided valley some fifteen "
        "miles inside the northern Black Forest, about fifteen miles south "
        "of Hirsau monastery, with Baden to the north-west. Here Bonisagus "
        "settled at a ruined Roman temple around 754, here the Order was "
        "founded and its first Tribunal held in 767, and here the Rhine "
        "Tribunal and the Grand Tribunal still meet, on the Tribunal Field "
        "by the Forum of Hermes. The Tower of Bonisagus holds the Great "
        "Library, the largest Hermetic collection anywhere, and most "
        "Bonisagus magi visit at least once in their lives.",
        "The covenant thinks of itself as the political and traditional "
        "heart of the Order and is still greatly respected through its "
        "House, but its power is quietly ebbing both in the Rhine and "
        "beyond it. Its magi look inward, absorbed in research while the "
        "fabric of the place crumbles: an Autumn covenant forever on the "
        "edge of Winter, a place of quiet study rather than intrigue, "
        "while Fengheld has grown into the Tribunal's largest and arguably "
        "strongest covenant. The decline is traced to the Schism War, the "
        "failure of House Bonisagus's diplomacy and the exile of the "
        "Hercynian lineage whose Waldherz chapter had kept peace with the "
        "forest fay; since then Durenmar has been ignorant of the faerie "
        "woods about it, and no peace was ever made.",
        "Murion's faction, which now leads, holds that Hermetic theory is "
        "to be kept pure of inferior hedge magic and is intolerant of hedge "
        "wizards and outsiders; the library's texts on such things are "
        "locked away for House elders alone. Critics say this deepens the "
        "stagnation and that Murion directs research instead of guiding "
        "it; an outward-looking minority gathered round Occultes wants "
        "exotic techniques brought in. A Magic aura of 7 lies over the "
        "clearing, defended by an Aegis of the Hearth of very high "
        "magnitude, devised after the faerie raid of 1085. The clearing is "
        "split by a stream and has no walls; the magi's sancta stand on "
        "the south bank, forbidden to all but a few trusted servants, and "
        "magic items heat, light and clean the towers and carry up the "
        "meals. A hidden guard post down the valley conceals the "
        "three-mile track in, and unexplored caves run under the north "
        "cliffs.",
        "The covenant is led by the Prima of House Bonisagus, who holds "
        "the sigil of Bonisagus and is thereby Praeco of the Rhine "
        "Tribunal. Its offices are the Colens Arcanorum (the librarian), "
        "the Tenens Occultorum, and two honorary posts the Primus fills by "
        "invitation: the Protector, traditionally a Flambeau master or "
        "archmage who sees to the covenant's defence, and the Artificer, "
        "traditionally a Verditius who crafts items for its glory. A "
        "Guernicus is always in residence, a Gifted Mercere oversees the "
        "Mercer House in the basement of the Tower of Trianoma, and at "
        "least one guest magus from every gild is kept in residence. "
        "Retired former members may still vote by proxy sigil at covenant "
        "meetings. There are no chapter houses at present. Three towers "
        "dominate the clearing: the Tower of Bonisagus, enchanted against "
        "all decay of its books and wound about by a huge ancient magical "
        "vine said to be Merinita's gift; the Tower of Notatus, conjured by "
        "the first Primus, which houses most of the Bonisagus magi, "
        "Murion's sanctum on its top two floors and two excellent shared "
        "labs in its basement; and the shorter, crooked Tower of Trianoma, "
        "its top two floors lost to a forgotten accident, home to the "
        "Trianoma lineage and the non-Bonisagus members. Lesser buildings "
        "include the mill and guard tower where the turb greets visitors "
        "and rings a bell for a magus, the standing stone of Notatus where "
        "guests are welcomed and given their Aegis token, Verditius' Forge "
        "half-buried under a grassy bank, the Protector's Watchtower on "
        "the cliffs amid blasted ground, the overgrown ruin called "
        "Seneca's Folly, and a hunters' lodge at the top of the clearing.",
        "Up to six peregrinatores lodge here at a time, from a long "
        "waiting list; magi accept almost any terms for access to the "
        "library, and a guest is usually asked to give two seasons of gild "
        "training to a Rhine apprentice, while the Bonisagus members share "
        "out the extra season of training owed to every Rhine apprentice. "
        "The covenfolk are quiet and peculiar, keep to themselves and have "
        "little to do with the magi; born in the aura, all carry Warping "
        "and live unusually long, and remnants of an old nature cult "
        "linger in their beliefs, with no church. A small band of expert "
        "huntsmen forays into the woods for vis and game. Redcaps run "
        "south to the Greater Alps and to Harco by the Rorschach chapter "
        "on Lake Constance, the Copper Rooster inn at Basel and the "
        "friendly covenant Sinews of Knowledge, or directly by the Mercere "
        "Portal to Harco.",
    )
    what_matters = _lines(
        "Vis: Intellego from the golden-green sap of the great vine on the Tower of Bonisagus (amount not given)",
        "Vis: Perdo from the pine cones of the Black Fir, gathered yearly (amount not given)",
        "Vis: Vim from Petrus Virilis's seed",
        "Vis: several kinds cultivated among the exotic plants of Ricardus Caespuus's glass Herbam laboratory",
        "Vis: the hot springs of upper Baden (Magic 2), which Durenmar owns Hermetically",
        "Vis: the huntsmen's forays into the nearby woods",
        "Income: lab rental, 5 or more pawns a season for a shared basement lab in the Tower of Notatus, 2 pawns for a guest lab across the river",
        "Income: dwindling; barred from faerie sites since 1151, and several magical sites were lost to Zaehringen settlement in the early 12th century",
        "Mundane: Durenmar ignores mundane politics; Hirsau monastery, fifteen miles north, spreads rumours of a hidden city of sorcerers",
        "Mundane: speculation that Durenmar patronised, or withered, the Zaehringens of Baden is thought unlikely",
        "Tension: Dankmar is the old enemy; in 1081 Durenmar accused it of league with the fay and lost, in 1151 Dankmar had Durenmar fined a rook of vis to every covenant and barred from faerie sites for fourteen years",
        "Tension: the 1085 raid of the King of the Black Mountain killed or carried off several Bonisagus magi and many covenfolk; none came back",
        "Tension: Murion's purists against Occultes's inclusive faction, which a sizeable minority of the House would rather see as Primus",
        "Tension: Fengheld and its allies oppose Philippus Niger at every turn; the Ash Gild's war on the Norse wizards has Murion's quiet favour",
        "Tension: no research breakthrough in decades, promising magi leaving, elders lost to age and Final Twilight",
        "Tension: Petrus Virilis's programme of Gifted children, and the young magae writing to him",
        "Tension: the Fane of the Founders, where twelve magi renew the Founders' vows every seventh year during the Tribunal; most Durenmar magi know of it, none has found it",
        "Hook: the library is unhelpful about exotic and non-Hermetic lore; obscure lab notes and old books hint at forgotten artifacts; magi from distant Tribunals pass through",
    )
    hidden = _lines(
        "The Black Fir near the Great Library is the King of the Black Mountain's slow revenge: planted at the Aegis's edge over a century ago after his direct attacks failed, it was taken inside the Aegis when the magi found its cones gave vis, and so breached their own defence. It creeps about six inches a year toward the Tower of Bonisagus; what happens when it reaches the tower or the vine is unknown but likely severe. The magi think it immemorial.",
        "Murion sends her raven familiar Kolkrabus to spy on Dankmar and others she counts enemies, against the Code.",
        "Vis donations are quietly accepted in place of a contribution to the library and prop up the dwindling vis income; this is never admitted.",
        "Occultes knows the restricted texts and has copied or moved the most interesting into his own sanctum, passing them to allies whose research they suit.",
        "Petrus Virilis means to invent a longevity ritual that would probably leave him infertile; Murion would be furious.",
        "The Fane of the Founders is an artifact into which the Cult of Mercury bound much of the Black Forest's original magical essence (treated as Magic Might 60); if Durenmar fell and the rite lapsed, the King of the Black Mountain hopes to seize that spirit.",
    )
    durenmar = b.covenant(
        "Durenmar",
        tribunal=tribunal,
        founded=767,
        place=rhine.places.get("durenmar_site"),
        summary=summary,
        what_matters=what_matters,
        notes=secrets(STORYGUIDE, hidden),
        aura=7,
        unnamed_magi=4,
        season="Autumn",
    )
    rhine.covenants["durenmar"] = durenmar
    _durenmar_magi(rhine, b, durenmar)
    _durenmar_library(b, durenmar)


def _durenmar_magi(rhine: Rhine, b: Builder, durenmar: Covenant) -> None:
    m = rhine.magi
    m["murion"] = b.magus(
        "Murion",
        covenant=durenmar,
        house=BONISAGUS,
        age=98,
        summary=secrets(
            "Archmage, Prima of House Bonisagus, leader of Durenmar, leader "
            "of the Oak Gild and, as holder of Bonisagus's sigil, Praeco of "
            "the Rhine Tribunal: the most politically powerful maga in the "
            "Tribunal. Haughty and overbearing, she wants Durenmar and the "
            "Rhine restored to the first place in the Order, and so quietly "
            "favours the Ash Gild's war on the Norse wizards, which would "
            "draw mighty magi and loot to the Rhine. Brilliant in every Art, "
            "above all Rego and Imaginem; she wears a great cloak of white "
            "feathers enchanted with illusions, and there are theories about "
            "whom she has impersonated in it. Her familiar is the raven "
            "Kolkrabus.",
            "She sends Kolkrabus to spy on Dankmar and on others she takes "
            "for enemies, in breach of the Code.",
        ),
        traits={
            "Loyal to Personal Agenda": 3,
            "Judgmental": 2,
            "Loyal to House Bonisagus": 2,
        },
    )
    m["andrus"] = b.magus(
        "Andrus",
        covenant=durenmar,
        house=BONISAGUS,
        age=61,
        summary=(
            "Master of House Bonisagus, Colens Arcanorum and librarian of "
            "the Great Library, Murion's first filius, about forty years past "
            "his Gauntlet. Thin and balding with a perceptive, commanding "
            "stare, he decides who may use the library and which gifts it "
            "accepts, so he is unwise to annoy. His duties keep him at the "
            "covenant and away from his own research. Many see him as "
            "Murion's puppet; rumour says he is preparing to challenge for "
            "Archmage within ten years."
        ),
        traits={"Busy": 3, "Modest": 1, "Strong-Willed": -1},
    )
    m["tandaline"] = b.magus(
        "Tandaline",
        covenant=durenmar,
        house=BONISAGUS,
        age=78,
        summary=(
            "Master of House Bonisagus, of the Trianoma lineage, Murion's "
            "closest confidante and her appointed Tenens Occultorum. Pale "
            "and slender, with eyes that shift colour hypnotically; a master "
            "of Muto and Auram for decades, she studies the air by turning "
            "herself into vapour. Politically Murion's ally, yet respected "
            "as a free thinker in her own right; she writes to many "
            "Bonisagus magi and uses those connections to punish anyone "
            "reported to have abused one of the House. Her apprentice is "
            "Petrus Virilis's Gifted son."
        ),
        traits={"Opaque": 3, "Blase": 1, "Sympathetic": 1},
    )
    m["caecilius"] = b.magus(
        "Caecilius",
        covenant=durenmar,
        house=BONISAGUS,
        age=160,
        summary=(
            "Archmage of House Bonisagus, the most venerable magus of "
            "Durenmar, senior Quaesitor of the Rhine Tribunal and the "
            "greatest living exponent of Intellego. Appointed Quaesitor long "
            "ago, it is said unwillingly and out of duty when the Tribunal's "
            "Quaesitorial presence was thin; his research extends the "
            "investigative rituals of House Guernicus. Reluctant and slow to "
            "act, with ever more frequent Twilight episodes, he is "
            "nonetheless a brilliant investigator with a spotless record "
            "who has solved many Hermetic crimes, and he adjudicates at "
            "Tribunal. His familiar is a silver-coated wolf."
        ),
        traits={"Diligent": 3, "Touchy": 2, "Indolent": 1},
    )
    m["occultes"] = b.magus(
        "Occultes",
        covenant=durenmar,
        house=BONISAGUS,
        age=72,
        summary=secrets(
            "Master of House Bonisagus, leader of the Linden Gild and "
            "figurehead of Durenmar's outward-looking faction, which would "
            "admit exotic magic; a sizeable minority of the House would "
            "rather have him as Primus. A colourful man who researches "
            "manuscripts and items of every kind, has made a small golem "
            "that serves in his lab, enchanted many texts and quills, and "
            "collects news of artifacts and strange practices from far "
            "away. He was librarian until the former Primus Avarret removed "
            "him. Murion tolerates and watches him, judging his ambitions "
            "modest and fearing a schism in the House if she moved against "
            "him.",
            "He knows the restricted texts and has quietly copied or moved "
            "the most interesting into his own sanctum, passing them to "
            "close allies whose research they suit.",
        ),
        traits={"Friendly": 3, "Inquisitive": 2, "Showy": 1},
    )
    m["ricardus_caespuus"] = b.magus(
        "Ricardus Caespuus",
        covenant=durenmar,
        house=BONISAGUS,
        age=56,
        summary=(
            "Master of House Bonisagus, a recluse whose sanctum on the "
            "covenant's southern edge is a great building walled almost "
            "entirely in glass, thousands of lead-framed panes on timber "
            "beams, unlike anything else in the century. Inside is a "
            "Herbam laboratory full of exotic plants from which he "
            "cultivates several kinds of vis, much as others extract it. "
            "Earnest and friendly but understood by nobody; Murion's circle "
            "rate him little better than a hedge wizard and bear with him "
            "for his harvests and his steady gifts to the stores."
        ),
        traits={"Reclusive": 3, "Artistic": 2, "Intense": 1},
    )
    m["petrus_virilis"] = b.magus(
        "Petrus Virilis",
        covenant=durenmar,
        house=BONISAGUS,
        age=32,
        summary=secrets(
            "Journeyman of House Bonisagus, an otherwise mediocre magus "
            "whose seed is Vim vis, whether by faerie gift or through the "
            "obsessive research into fertility and the Gift of his "
            "liberal-minded mater Susanna, now in Final Twilight. Tandaline "
            "talked him into an experiment that fathered a Gifted son on a "
            "serving maid, now her apprentice, and on Murion's orders he "
            "has fathered four more, all Gifted, and all sons when born at "
            "Durenmar because of Philippus Niger's Twilight scar. Averse to "
            "sex and ill at ease with women, he would keep his vis to "
            "himself, but the covenant deems his talent too valuable; "
            "interested young magae write to him.",
            "He plans to invent a longevity ritual that would probably "
            "leave him infertile; Murion would be furious. A maga wanting a "
            "Gifted child must offer more than seduction; he might instead "
            "fall for a peasant girl and plan a wedding in a nearby town.",
        ),
        traits={"Shy": 3, "Rebellious": 1, "Trusting": -2},
    )
    m["winfrida"] = b.magus(
        "Winfrida",
        covenant=durenmar,
        house=GUERNICUS,
        age=27,
        summary=(
            "Journeyman of House Guernicus and Quaesitor, young, "
            "inexperienced and timid, admitted some years ago because a "
            "Guernicus must always be at Durenmar; she passed her Gauntlet "
            "in the Greater Alps. She would secretly rather live the "
            "research life of a Bonisagus. She and Tabanus may be the only "
            "two Guernicus in the Rhine; Murion is grooming and "
            "indoctrinating her, confusing her loyalties, and Tabanus "
            "thinks her weak."
        ),
        traits={"Yearning for a Better Life": 2, "Self-Confident": -1, "Forceful": -2},
    )
    m["philippus_niger"] = b.magus(
        "Philippus Niger",
        covenant=durenmar,
        house=FLAMBEAU,
        age=125,
        summary=(
            "Archmage of House Flambeau, of the Apromor lineage, leading "
            "figure of the Ash Gild and Protector of Durenmar, chosen by "
            "Murion, whose political ally he is. Called the Black: a "
            "smallish, well-built, cool and reserved man who looks ninety, "
            "somewhat deaf, bowed and creaky, in a black hooded cloak over "
            "darkest grey with a serrated dagger of human bone, his "
            "talisman, always at his belt. He has spent his life defending "
            "the Order against non-Hermetic wizards and is the Order's "
            "foremost master of Perdo; now, with Final Twilight near, he "
            "turns to politics, driving the Ash Gild's push for war on the "
            "Norse wizards beyond the Baltic and pressing Oculus "
            "Septentrionalis to investigate harder and to open a Mercere "
            "Portal to Durenmar, which would wound Fengheld. Most of "
            "Fengheld and its allies oppose him and several hedge wizards "
            "want him dead; he lives in the Watchtower on the cliffs, "
            "built apart so that his familiar Sordus, a basilisk whose gaze "
            "kills and whose presence withers plants and fouls water, "
            "should not blight the valley. His Twilight scars are many: he "
            "seems to grow when angry, his shadow moves on its own, flames "
            "dim when he enters, wine sours near him, black animals follow "
            "him, and only sons are born where he has lived a year. He has "
            "trained four apprentices and made the Wizard's Bridle, which "
            "binds a magus's words and gestures, and the Subtle Chain, a "
            "silver loop that lays six wards at once."
        ),
        traits={
            "Alarmist": 3,
            "Condescending": 3,
            "Obsessive": 2,
            "Cool-Tempered": -1,
            "Cheerful": -3,
        },
    )
    m["gudrun_tigurina"] = b.magus(
        "Gudrun Tigurina",
        covenant=durenmar,
        house=VERDITIUS,
        age=None,
        summary=(
            "Master of House Verditius and Artificer of Durenmar, the "
            "honorary post that crafts items for the covenant's glory. She "
            "lives in Verditius' Forge, the half-buried laboratory the "
            "Founder built when he came to study with Bonisagus."
        ),
    )
    m["xavier"] = b.magus(
        "Xavier",
        covenant=durenmar,
        house=MERCERE,
        age=None,
        summary=(
            "Master of House Mercere, the only Gifted Mercere in the Rhine "
            "and the Tribunal's archivist. He oversees the Mercer House in "
            "the basement of the Tower of Trianoma, which serves the "
            "southern Tribunal, and is content that Horst of Fengheld "
            "leads the Rhine's Redcaps from the other Mercer House."
        ),
    )
    m["sula"] = b.magus(
        "Sula",
        covenant=durenmar,
        house="",
        age=None,
        summary=(
            "Autocrat of Durenmar: a wrinkled, gentle woman past ninety and "
            "still hale, who arranges lodging for guests and places "
            "visitors with uncanny ease."
        ),
        type="companion",
    )


def _durenmar_library(b: Builder, durenmar: Covenant) -> None:
    rules = (
        "The Great Library fills the Tower of Bonisagus, which is "
        "enchanted against all decay of its books; a magus's familiarity "
        "with it is his Durenmar Lore. House Bonisagus swore to share it, "
        "so any magus may study here, but Durenmar adds that those who "
        "study must also give: each contribution the librarian accepts (a "
        "summa, a tractatus, a new spell, even a copy or a subtle variant, "
        "though low summae and common spells are refused as glutted) earns "
        "two free seasons of study, more for a weighty gift, and a season "
        "spent copying earns one season, which is how apprentices pay "
        "their way. Lab notes and Tribunal records may be consulted "
        "without contributing. Bonisagus magi and members study freely and "
        "indefinitely, and a Bonisagus who writes up his work here has met "
        "the Oath's duty to share. Rank decides a clash over a book, "
        "Bonisagus and members winning at equal rank, otherwise certamen; "
        "a few popular tomes have second copies. Nothing leaves the tower "
        "or is copied without the librarian's leave, though members may "
        "take Lab Texts to their labs; copies may be ordered by Redcap "
        "with vis for the scribing but come notoriously slowly, and the "
        "greatest summae are traded only with the most trusted, if ever. "
        "About a dozen magi study here in any season."
    )
    b.book(
        durenmar,
        "The Great Library of Durenmar",
        "Other",
        description=rules,
    )
    # First floor: the scriptorium.
    b.book(
        durenmar,
        "Mundane books of the scriptorium",
        "Other",
        description=(
            "First floor of the Tower of Bonisagus, where scribing, binding "
            "and copying are done with materials provided: an eclectic "
            "collection of mostly ancient mundane books from far places."
        ),
    )
    b.book(
        durenmar,
        "Lab notes of dead magi",
        "Other",
        description=(
            "First floor: endless lab notes of obscure, forgotten and "
            "unfinished research by magi long dead. Finding notes that bear "
            "on a project takes a season and a roll of Intelligence and "
            "Magic Theory; a named author's notes turn up within days "
            "unless they are restricted. Consulting them needs no "
            "contribution."
        ),
    )
    b.book(
        durenmar,
        "Records of the Rhine and Grand Tribunals",
        "Other",
        description=(
            "First floor: the complete records of every Rhine Tribunal and "
            "Grand Tribunal since the founding of the Order. A season "
            "extracts everything on a narrow subject, a covenant or a "
            "magus without a roll; a single entry takes a daily roll of "
            "Intelligence and Order of Hermes Lore, harder by one each "
            "day. Open to all without contribution."
        ),
    )
    b.book(
        durenmar,
        "House Bonisagus Folios",
        "Other",
        description=(
            "First floor: the Folios of House Bonisagus back to its first discourses."
        ),
    )
    # Second floor: Lab Texts.
    b.book(
        durenmar,
        "Lab Texts of the standard spells",
        "Lab Text",
        description=(
            "Second floor: copies of nearly every standard spell of the "
            "Order, many of which became standard by being written up "
            "here. Finding one is a stress roll against 3, or 6 for a "
            "particular version of a general spell up to level 40; a "
            "failure means someone of higher rank has it this season, a "
            "botch that it is not here, and an exact match a certamen "
            "with an equal."
        ),
    )
    b.book(
        durenmar,
        "Lab Texts of unique spells",
        "Lab Text",
        description=(
            "Second floor: many unique spells. A non-standard spell is "
            "found on a roll against 6 to 21, depending on its rarity; a "
            "failure means it is not here, a botch that a flawed text "
            "exists."
        ),
    )
    b.book(
        durenmar,
        "Lab Texts of enchanted devices",
        "Lab Text",
        description=(
            "Second floor: many enchanted devices. A similar enchantment "
            "is found on a roll against 6 to 21; beating that by six or "
            "more finds the exact effect."
        ),
    )
    b.book(
        durenmar,
        "Replenishing the Fount of the Magus",
        "Lab Text",
        level=30,
        description=(
            "A Creo Corpus ritual of the thirtieth level held in the Great "
            "Library; nobody has ever cast it successfully."
        ),
    )
    b.book(
        durenmar,
        "Tractatus on Spell Mastery",
        "Tractatus",
        description=(
            "Second floor: many tractatus on the mastery of spells. Each "
            "full six by which a spell is found beyond its ease factor "
            "turns up one Mastery tractatus, of Quality a simple die plus "
            "two."
        ),
    )
    # Third floor: tractatus and summae.
    b.book(
        durenmar,
        "Tractatus on the Arts",
        "Tractatus",
        description=(
            "Third floor: dozens of tractatus on each Art, typically of "
            "Quality 3 to 9 and at most about 12 (a simple die plus two, "
            "with Durenmar Lore added at a cumulative penalty of one for "
            "each earlier use in that Art; capped at 12, never above 14)."
        ),
    )
    b.book(
        durenmar,
        "Tractatus on Magic Theory and the Arcane Abilities",
        "Tractatus",
        ability="Magic Theory",
        description=(
            "Third floor: several hundred tractatus on Abilities, chiefly "
            "Magic Theory, and on the other Arcane Abilities."
        ),
    )
    b.book(
        durenmar,
        "Principia Magica",
        "Ability Summa",
        ability="Magic Theory",
        author="Bonisagus",
        description=(
            "Bonisagus's own authority on Magic Theory; the third floor "
            "holds three copies. Level and Quality not given."
        ),
    )
    b.book(
        durenmar,
        "Summae on the Arts",
        "Art Summa",
        description=(
            "Third floor: over a hundred summae, many in several volumes, "
            "with at least one outstanding high-level, high-Quality summa "
            "in every Art and a summa of at least level 17 in each of the "
            "fifteen; only a couple of dozen Art summae reach level 15 and "
            "levels above 20 are almost unheard of. Low summae run Quality "
            "6 to 15 (at most about 24), high ones 6 to 9 (at most about "
            "12). Availability is a simple die plus 10 against the level "
            "wanted (plus 3 for masters, Bonisagus and members, plus 6 for "
            "archmagi, never above 20); an exact match means certamen. "
            "Quality is a simple die plus 5 and Durenmar Lore at the usual "
            "penalty, capped at 30 minus the level or at 24, whichever is "
            "lower, and never above 28."
        ),
    )
    b.book(
        durenmar,
        "Summae on the Arcane Abilities",
        "Ability Summa",
        description=(
            "Third floor: summae on the Arcane Abilities. Availability is a "
            "simple die alone against the level wanted; an exact match "
            "means certamen. Quality as for the Art summae."
        ),
    )
    # Upper floors and basement.
    b.book(
        durenmar,
        "The librarian's restricted collection",
        "Other",
        description=(
            "Sixth and seventh floors, the librarian's sanctum, entered by "
            "invitation only: miscellaneous magical books and the lab notes "
            "on exotic theories and hedge traditions, heavily restricted "
            "under the present leadership and read only by House elders. "
            "The fourth and fifth floors between hold two cramped labs "
            "each, fitted so they work without penalty and always in "
            "demand."
        ),
    )
    b.book(
        durenmar,
        "Originals of the most precious tomes",
        "Other",
        description=(
            "The basement, behind a great enchanted iron trapdoor: the "
            "originals of the most precious tomes, of which only copies "
            "are read upstairs, with Durenmar's vis stores and countless "
            "items and relics including possessions of the Founders."
        ),
    )


# ---------------------------------------------------------------- Dankmar


def _dankmar(rhine: Rhine, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "A small Winter covenant in the dampest, darkest part of the Black "
        "Forest, about forty miles south-west of Durenmar and a few miles "
        "south of the Black Forest Road, founded in 1052 by Aschlaranda, "
        "cast out of Durenmar and House Bonisagus, with her apprentice "
        "Schadrit, and named in mockery of the Order's birthplace to "
        "oppose Durenmar in all things. The firs grow so thick that it is "
        "dusk at noon; only fungi live on the poisoned carpet of needles "
        "and only ravens call.",
        "A round palisade of split logs encloses wooden huts and four "
        "two-storey stone towers, the sancta of its four magae, which run "
        "down into linked caves reached only through the towers. Fir and "
        "yew lean over the walls and every wooden thing glows day and "
        "night with phosphorescent bracket fungi. The Faerie aura is 5, "
        "and Orphedra's version of the Shrouded Glen (level 40, "
        "Penetration 20, with her darkness sigil) hides the place for at "
        "least a mile, turning travellers away in nameless dread; those "
        "whose Magic Resistance holds feel nothing. Ancient Schadrit "
        "broods at the centre and her descendants do her bidding.",
        "Dankmar keeps a careful working relationship, never an alliance, "
        "with the most malign dark fae of the deep forest, the formless "
        "beings of darkness and fear that resent mankind, and this has "
        "let it outlast Durenmar's hostility and the emperor's clearing of "
        "the forests. Its covenfolk are wholly bewitched by Jiphella: "
        "fanatically loyal, worshipping the magae as gods and ready to die "
        "at a word, but slack-witted, unable to think for themselves and "
        "needing to be told to eat each day. There are no consortes.",
    )
    what_matters = _lines(
        "Vis: not given",
        "Income: not given",
        "Mundane: hostile to the emperor's deforestation; mundanes who feel the Shrouded Glen never return",
        "Tension: Durenmar accused Dankmar at the Tribunal of 1081 of secret league with the fay, and proved nothing; in 1151 Dankmar prosecuted Durenmar for plundering faerie sites and won, with the rare joint backing of the Hawthorn and Elder Gilds",
        "Tension: the destruction of St Georgen monastery in 1208 is widely blamed on Dankmar; at the Tribunal of 1214 Jiphella, its sole delegate, denied it, and with no mundane witness and the Guardians of the Forests ruling to shelter under, a close vote refused an investigation",
        "Tension: Murion's raven Kolkrabus spies on the covenant",
        "Faerie: Orphedra has a pact with the local bockmen to patrol the woods around the covenant",
        "Hook: a cautionary example of what magical domination of mundanes comes to",
    )
    hidden = (
        "The book suspects but never states Dankmar's hand in the "
        "destruction of St Georgen, whose monks were found hanging dead in "
        "strange dark vines."
    )
    dankmar = b.covenant(
        "Dankmar",
        tribunal=tribunal,
        founded=1052,
        place=rhine.places.get("dankmar_site"),
        summary=summary,
        what_matters=what_matters,
        notes=secrets(STORYGUIDE, hidden),
        aura=5,
        realm="Faerie",
        unnamed_magi=0,
        season="Winter",
    )
    rhine.covenants["dankmar"] = dankmar
    m = rhine.magi
    m["schadrit"] = b.magus(
        "Schadrit",
        covenant=dankmar,
        house=EX_MISC,
        age=160,
        summary=(
            "Master of House Ex Miscellanea, co-founder and iron-handed "
            "ruler of Dankmar. Trained as a Bonisagus apprentice at "
            "Durenmar under Aschlaranda, expelled with her mistress a year "
            "before her Gauntlet and finished outside the House. A withered "
            "hag in a voluminous hooded black robe, her face a mass of "
            "wrinkles about a long mole-covered nose; her longevity ritual "
            "kept her alive but not her looks. An expert in Faerie Magic, "
            "taught by Orphedra, and perhaps its only practitioner outside "
            "House Merinita; malicious to the point of evil."
        ),
        traits={"Malicious": 5, "Vengeful": 4, "Callous": 3},
    )
    m["orphedra"] = b.magus(
        "Orphedra",
        covenant=dankmar,
        house=MERINITA,
        age=139,
        summary=(
            "Master of House Merinita and the covenant's link to the forest "
            "fae. Apprenticed at Irencillia a hundred and twenty years ago, "
            "she found it stifling and sought the primeval dark instead. "
            "Stick-thin, hair in a tight bun, angular, with unnaturally "
            "smooth skin and an air that makes the covenfolk's skin crawl. "
            "She revels in Faerie Magic, which she taught Schadrit, leans "
            "to the dark fae, works in illusion, cold, darkness and fear, "
            "cast the covenant's Shrouded Glen, and has a deal with the "
            "local bockmen to patrol its surroundings."
        ),
        traits={"Cruel": 3, "Frightening": 3, "Optimistic": -2},
    )
    m["jiphella"] = b.magus(
        "Jiphella",
        covenant=dankmar,
        house=EX_MISC,
        age=73,
        summary=(
            "Master of House Ex Miscellanea and master of Mentem, "
            "Schadrit's own daughter, conceived under a dark faerie charm "
            "long after her mother's longevity ritual, trained by her and "
            "wholly cowed by her. Immense and bloated, with lank greasy "
            "grey hair and a sickly orange left eye with a blood-red iris "
            "that bewitches with a glance; most of the covenfolk are under "
            "her spell and worship her. She was Dankmar's only delegate at "
            "the Tribunal of 1214, where she denied any part in St "
            "Georgen's fall."
        ),
        traits={"Crude": 3, "Domineering": 3, "Moody": 2},
    )
    m["larinda"] = b.magus(
        "Larinda",
        covenant=dankmar,
        house=EX_MISC,
        age=20,
        summary=(
            "Journeyman of House Ex Miscellanea, Jiphella's daughter and "
            "filia, conceived under the same charm. Pretty and sunny "
            "despite a cruel mother and a domineering grandmother, whom she "
            "obeys out of family duty. Her affinities are for the natural "
            "world, Animal, Herbam, Aquam and Auram, and she is becoming an "
            "expert brewer of potions. The rest of her traits are lost in "
            "the source."
        ),
        traits={"Passionate": 2},
    )


# ---------------------------------------------------------------- Triamore


def _triamore(rhine: Rhine, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "A castle and manorial estate on the Meuse at the edge of the "
        "Ardennes in Lower Lorraine, on the western fringe of the Rhine "
        "Tribunal, with Liege and Verdun the nearest towns; Verdun and "
        "Triamore are where the Redcaps of the Rhine and Normandy usually "
        "meet. A comfortable covenant of reasonable magi with a Magic aura "
        "of 2 and a famous library, to which guests are expected to add a "
        "book.",
        "Triamore has long been tangled in the politics of its "
        "neighbourhood, for which the local Quaesitores have repeatedly "
        "sought to censure it; only the shrewd dealing of its princeps, "
        "Daria la Gris, has held them off. Recent deaths and Twilights "
        "have left it magically and politically weak and pushed to the "
        "margins, so Daria recruits by welcoming peregrinatores and "
        "visiting magi, though the tales of trouble keep numbers low.",
        "As co-leader of the Apple Gild she backs the proposed Lotharingian "
        "Tribunal, which would free the covenant's mundane dealings and "
        "turn it from a border minnow into the hub of a new Tribunal; to "
        "that end she cultivates friendships with several Normandy "
        "covenants. Both its Tremere sigils are held by Stentorius of "
        "Fengheld, the Tremere exarch of the Rhine.",
    )
    what_matters = _lines(
        "Vis: not given",
        "Income: a manorial estate (details not given)",
        "Mundane: deep in local politics, details not given; Redcaps pass through on the road between the Rhine and Normandy",
        "Tension: the Lotharingian motion, which would make Triamore the centre of a new Tribunal",
        "Tension: Quaesitorial scrutiny of its mundane entanglements, fended off so far by Daria",
        "Tension: vacancies after recent deaths and Twilights, an open door for new magi or a sign of something sinister",
        "Hook: the library draws visitors, who are expected to contribute a book",
        "Allies: several Normandy covenants, cultivated by Daria",
    )
    hidden = (
        "The Quaesitores have long wished to censure the covenant for its "
        "mundane dealings. The cause of the recent deaths is not stated."
    )
    triamore = b.covenant(
        "Triamore",
        tribunal=tribunal,
        founded=1151,
        place=rhine.places.get("triamore_site"),
        summary=summary,
        what_matters=what_matters,
        notes=secrets(STORYGUIDE, hidden),
        aura=2,
    )
    rhine.covenants["triamore"] = triamore
    m = rhine.magi
    m["daria_la_gris"] = b.magus(
        "Daria la Gris",
        covenant=triamore,
        house=TREMERE,
        age=67,
        summary=(
            "Master of House Tremere, co-leader of the Apple Gild and "
            "princeps of Triamore. Stern, uncompromising and politic, she "
            "has kept the Quaesitores at bay and champions the Lotharingian "
            "Tribunal, courting the covenants of Normandy. She has trained "
            "two apprentices."
        ),
        traits={"Sophisticated": 2, "Studious": 1, "Frivolous": -3},
    )
    m["remi_of_museau"] = b.magus(
        "Remi of Museau",
        covenant=triamore,
        house=JERBITON,
        age=48,
        summary=(
            "Master of House Jerbiton, a friendly, effusive polymath: "
            "scholar, fighter, hunter, musician and poet, mostly without "
            "recourse to magic, though he knows many useful spells."
        ),
        traits={"Unpretentious": 3, "Worldly": 3, "Cheerful": 2},
    )
    m["sicero"] = b.magus(
        "Sicero",
        covenant=triamore,
        house=TREMERE,
        age=23,
        summary=(
            "Journeyman of House Tremere, newly Gauntleted filius of "
            "Goliard, a famed maga of Stonehenge, and admitted on her "
            "recommendation. He has yet to prove himself."
        ),
        traits={"Keen to Impress": 2, "Confident": 1, "Quiet": 1},
    )
    b.book(
        triamore,
        "Triamore's library",
        "Other",
        description=(
            "A famous library, smaller than Durenmar's but a draw in its "
            "own right; no titles are given. Visiting magi are generally "
            "required to contribute a book."
        ),
    )


# --------------------------------------------------------------- Waddenzee


def _waddenzee(rhine: Rhine, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "A Spring covenant of pirate magi on a deserted stretch of the "
        "Frisian island of Terschelling, on the Wadden Sea, preying on the "
        "shipping of the North Sea, skirting the Code of Hermes and "
        "breaking mundane law every day. It was founded in 1165 as "
        "Terschelling by Axior of Flambeau, a dissident of Oculus "
        "Septentrionalis, who died in a magical accident within twenty "
        "years. Hygwald Veritas and Eric Ribecus arrived in 1200 and by "
        "1207 announced that they were the only magi left, renamed the "
        "covenant Waddenzee, a claim to the whole sea, and changed its "
        "charter and symbol, to uproar at Tribunal; a Quaesitorial inquiry "
        "found no wrongdoing and a vote to treat it as a new covenant "
        "needing the Tribunal's leave failed thanks to the Oak and Ash "
        "Gilds.",
        "About twenty years ago Hygwald and Eric killed a pirate chief and "
        "took his three ships and crews; the covenant now sails five "
        "magically enhanced ships, the flagship Nebelkönigin among them, "
        "taken from Oculus Septentrionalis while she carried a great cargo "
        "of vis and magical books with no magus aboard. It stays within "
        "the letter of the Code by leaving no witnesses. Only the failure "
        "of the coastal nobles to act together has saved it, and an "
        "understanding with Fengheld restrains Oculus Septentrionalis "
        "from moving against it.",
        "A Magic aura of 3 covers the covenant building and a few hundred "
        "paces round it: a long, low Danish-style long-house sunk partly "
        "into the ground for the covenfolk, with four separate buildings "
        "for the magi joined to the middle of each wall by sunken covered "
        "walkways, each holding a magus, his lab, one or two consortes and "
        "some warriors, and a harbour. The magi foster the island's "
        "reputation for haunting, in truth the din of thousands of "
        "seabirds in spring and summer, and have driven off other "
        "settlers. The turb of nearly two hundred pirates and hangers-on "
        "from all over Europe is probably the Rhine's largest; about half "
        "are at sea at any time in two ships and most of the rest are "
        "drunk, but they obey the magi and their deputies.",
    )
    what_matters = _lines(
        "Vis: rich, but mostly other people's, taken as plunder",
        "Vis: Lucas von Beck harvests vis at the Pirates' Graveyards in Drenthe, where the Frisian pirates bury their dead",
        "Income: piracy on the North Sea with five enchanted ships",
        "Mundane: outlaws to the local nobility, who cannot unite against them",
        "Tension: enemies of Oculus Septentrionalis, which waits for one misstep",
        "Tension: the Quaesitores have warned the covenant repeatedly that it walks a fine line, will get no Tribunal support if the mundane authorities move, and that each pirate magus would likely face charges of High Crimes",
        "Tension: Eric Ribecus's younger cousin Estrid Danesson of Oculus Septentrionalis is his bitter enemy",
        "Allies: a mutual understanding with Fengheld; the Oak and Ash Gilds backed it in the 1207 vote",
        "Hook: a generation hence the Hanseatic League will build bigger ships, sail in convoy and hire soldiers against pirates; with Oculus Septentrionalis at its head an assault on Waddenzee is plausible, but the League is more than twenty years off",
        "Hook: the stolen Hermetic books may have been placed in the pirates' hands and tainted; Lucas may be using infernal lore in his necromancy without knowing it, and only Hachim may have the wisdom to resist",
    )
    hidden = _lines(
        "Imanitos Mendax of Oculus Septentrionalis feeds Eric advance word of that covenant's ship movements for a share of the plunder, and the Waddenzee magi are party to it; the messages may travel by Astasians, tiny messenger demons taken for airy spirits.",
        "The power of the Pirates' Graveyards may be Infernal rather than Magic; Lucas has barely considered it.",
    )
    waddenzee = b.covenant(
        "Waddenzee",
        tribunal=tribunal,
        founded=1165,
        place=rhine.places.get("waddenzee_site"),
        summary=summary,
        what_matters=what_matters,
        notes=secrets(STORYGUIDE, hidden),
        aura=3,
        unnamed_magi=0,
        season="Spring",
    )
    rhine.covenants["waddenzee"] = waddenzee
    m = rhine.magi
    m["hygwald_veritas"] = b.magus(
        "Hygwald Veritas",
        covenant=waddenzee,
        house=TREMERE,
        age=48,
        summary=(
            "Journeyman of House Tremere and devious co-founder of "
            "Waddenzee, an Englishman trained at Blackthorn in Stonehenge. "
            "Scrupulously honest with Quaesitores, whom he secretly longs to "
            "join, and arrogant to everyone else, he lies, cheats and steals "
            "whenever it serves. Well groomed, looking in his late "
            "thirties, dressed to show his wealth; a Mentem specialist, "
            "above all Rego Mentem, who leans heavily on Aura of Rightful "
            "Authority."
        ),
        traits={"Arrogant": 3, "Honest to Quaesitors": 3, "Respect for Authority": -3},
    )
    m["eric_ribecus"] = b.magus(
        "Eric Ribecus",
        covenant=waddenzee,
        house=TYTALUS,
        age=52,
        summary=(
            "Journeyman of House Tytalus, co-founder of Waddenzee and its "
            "most committed pirate: a black-haired Dane from Ribe, dashing, "
            "charming and extroverted, with a swollen opinion of himself, "
            "who looks far younger than he is thanks to illusions and a "
            "good longevity ritual. A generalist favouring Aquam and Auram, "
            "he fights beside his men with a magical sword; his familiar is "
            "Aegir, a long-tailed skua. His younger cousin Estrid Danesson "
            "of Oculus Septentrionalis is his bitter enemy."
        ),
        traits={"Reckless": 6, "Wry Humor": 4, "Passive": -4},
    )
    m["lucas_von_beck"] = b.magus(
        "Lucas von Beck",
        covenant=waddenzee,
        house=FLAMBEAU,
        age=45,
        summary=(
            "Journeyman of House Flambeau, son of a German altgraf whose "
            "family believes him dead; he keeps a nobleman's habits. Very "
            "tall and stocky, always in black, and since a Twilight his "
            "clothes fall to pieces when he casts too much. A short-tempered "
            "expert in Perdo who kills troublesome mundanes with Perdo "
            "Corpus; he has lately taken up necromancy, using the pirates' "
            "victims and the Pirates' Graveyards."
        ),
        traits={"Aggressive": 3, "Morbid": 2, "Blunt": 1},
    )
    m["hachim_al_khalejj"] = b.magus(
        "Hachim al'Khalejj",
        covenant=waddenzee,
        house=CRIAMON,
        age=36,
        summary=(
            "Journeyman of House Criamon, a quiet, naive Muslim, filius of "
            "Hassan El-Megrayhi of Fengheld, who fell in with the pirates by "
            "chance. His astrology helps plan their raids. He dresses in "
            "stolen cream and blue silks and walks with a limp."
        ),
        traits={"Secretive": 3, "Devout Muslim": 2, "Introverted": 2},
    )
    m["aethelbald"] = b.magus(
        "Aethelbald",
        covenant=waddenzee,
        house="",
        age=None,
        summary=(
            "A deputy of the magi who claims to be the Saxon heir to the English crown."
        ),
        type="companion",
    )
    m["bjorn_ironside"] = b.magus(
        "Bjorn Ironside",
        covenant=waddenzee,
        house="",
        age=None,
        summary="Ship's master of the Nebelkönigin, Waddenzee's stolen flagship.",
        type="companion",
    )
    m["calum"] = b.magus(
        "Calum",
        covenant=waddenzee,
        house="",
        age=None,
        summary="A lapsed priest who gives the pirates a heretical spiritual ministry.",
        type="companion",
    )
    m["aelfhere"] = b.magus(
        "Aelfhere",
        covenant=waddenzee,
        house="",
        age=None,
        summary=secrets(
            "A Frisian shipwright of near-magical skill who keeps the "
            "covenant's five ships at sea.",
            "He secretly corresponds with Marcus Navicularius of Oculus "
            "Septentrionalis.",
        ),
        type="companion",
    )
    b.book(
        waddenzee,
        "Waddenzee's library",
        "Other",
        description=(
            "Poor: a few books following the interests of the present "
            "magi; no titles are given."
        ),
    )
    b.book(
        waddenzee,
        "The Nebelkönigin's stolen books",
        "Other",
        description=(
            "The Hermetic books taken with the Nebelkönigin from Oculus "
            "Septentrionalis; their contents are not given. They may have "
            "been engineered into the pirates' hands and tainted."
        ),
    )


# ------------------------------------------------------ Oculus Septentrionalis


def _oculus(rhine: Rhine, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "The Eye of the North, a Summer covenant mostly of House Jerbiton "
        "spread through the city of Lübeck in Holstein, on the Baltic, in "
        "townhouses, warehouses, a shipyard and a fleet. The Tribunal "
        "created it by charter in 1144, at the Ash Gild's urging, to "
        "learn about the Norse wizards, ruling that a covenant needed no "
        "site at its founding, only magi bound by a charter. Its first "
        "magi did nothing for two decades, were fined three pawns each in "
        "1158 and ordered to find a site, and three of them settled in "
        "Lübeck around 1160 while Axior left to found Terschelling.",
        "It abandoned the Ash mission for peaceful contact and trade with "
        "the magical folk of the north, two of whom have married its magi, "
        "and became a principal proponent of the Apple Gild. Hermetically "
        "weak and aloof from Tribunal politics, it is immensely rich and "
        "woven into the city as merchants, scholars and craftsmen; the "
        "burghers do not know them for wizards, and its wealth may exceed "
        "that of all the other Rhine covenants together. Lübeck has an "
        "ordinary Divine aura and the covenant no Magic aura of its own. "
        "The Quaesitores wrote into its charter that it may admit only "
        "magi with the Gentle Gift.",
        "Its magi seldom raise the Parma daily or cast where they can be "
        "seen, though most have some discreet magic; they meet rarely, so "
        "their politics are gossipy and conspiratorial. Discreet visitors "
        "are welcome and indiscreet ones asked to leave. There is room for "
        "one or two more magi, Jerbiton, Apple Gild or Redcaps with the "
        "Gentle Gift and a mundane trade, and two seldom-used peregrinator "
        "labs above the Novgorod Inn. There is no turb, only a handful of "
        "mercenaries guarding the businesses, whose staff blur with the "
        "covenant's many servants and two scribes. Lübeck is the usual "
        "stop for Redcaps bound for Novgorod, a few weeks away by sea, and "
        "the covenant keeps a contact at the trading counter Lübeck's "
        "merchants have run there since 1205. Theoderich of Jerbiton "
        "recently left to help found Heorot in Denmark and remains "
        "friendly.",
    )
    what_matters = _lines(
        "Vis: chronically short; a few sources, all far from Lübeck around the Baltic, gathered by Estrid Danesson",
        "Vis: Boris of Novgorod buys Novgorod vis cheaply",
        "Income: trade, shipbuilding and the businesses of its magi; perhaps the richest covenant in the Rhine",
        "Mundane: integrated among Lübeck's burghers as merchants, scholars and craftsmen; a contact at the Novgorod counter; Henri de Tours is likely to be at the heart of the coming Hanse",
        "Tension: Waddenzee has taken several of its ships and cargoes, the Nebelkönigin among them; the covenant wants the pirates ended by Tribunal ruling or a secretly provoked mundane army, but has no proof and fears Quaesitorial scrutiny of its own mundane dealings",
        "Tension: the Quaesitores forbade the trading venture the Nebelkönigin carried, so the ship cannot legally be recovered",
        "Tension: Crintera suspects it of aiding the Danish invasion of Rügen; Urgen killed its leader Prudentum in Wizard's War in 1179, and since Falke's moderate leadership the two covenants ignore each other",
        "Tension: Philippus Niger presses it to investigate the Norse wizards harder and to open a Mercere Portal to Durenmar",
        "Hook: Henri de Tours may negotiate the treaty of Lübeck and Hamburg of 1241 or become Älderman; the League may be the covenant's own idea, and growing wealth brings Quaesitorial risk and the temptation to bribe at Tribunal",
        "Hook: Marcus Navicularius is designing the Baltic cog, round, flat-bottomed, with a centre rudder and one square sail, carrying hundreds of tons of Novgorod timber, which the Hanse will adopt by mid-century",
    )
    hidden = _lines(
        "The covenant holds three Verditius magestones, given secretly in 1144, each giving a Magic aura of 3 over a large room; they are shared so each magus has a Magic-aura lab for up to two seasons a year. Only Durenmar's senior magi also know. Imanitos might swap them for infernally tainted copies to breed greed in the labs.",
        "Imanitos Mendax betrays the covenant to Waddenzee, selling its ship movements for a share of the loot; discovery would mean expulsion and undying enmity. He may also be a diabolist of a hidden dark Jerbiton lineage serving the demon Radegast, corrupting Lübeck's notables through the Goldenes Kalb and posing as Radegast's prophet to the Mecklenburg family, with low-Might demons for messengers, thieves, spies and seducers.",
        "A secret deal with Fengheld: a rook of vis a year in exchange for a huge yearly shipment of luxuries and over a hundred pounds of silver.",
    )
    oculus = b.covenant(
        "Oculus Septentrionalis",
        tribunal=tribunal,
        founded=1144,
        summary=summary,
        what_matters=what_matters,
        notes=secrets(STORYGUIDE, hidden),
        aura=0,
        realm="Divine",
        unnamed_magi=0,
        season="Summer",
    )
    rhine.covenants["oculus"] = oculus
    m = rhine.magi
    m["henri_de_tours"] = b.magus(
        "Henri de Tours",
        covenant=oculus,
        house=JERBITON,
        age=66,
        summary=(
            "Master of House Jerbiton, of the Apple Gild, and disceptator "
            "of Oculus Septentrionalis as its oldest remaining member. "
            "Corpulent, sociable and splendidly dressed, probably Lübeck's "
            "richest merchant and among the richest commoners in Germany, "
            "a respected administrator and diplomat who was apprenticed in "
            "Normandy and joined soon after the founding; he means his "
            "family to become a dynasty leading the covenant. A Mentem "
            "master who uses high-magnitude Mentem for subtlety, never "
            "force. His townhouse on the Holstenstrasse has shop and "
            "offices below, library and scriptorium above, then meeting "
            "rooms, dining hall and guest chambers, then the family's "
            "quarters, with three labs at the top for himself, Brunhilda "
            "and Gunhilda."
        ),
        traits={"Ambitious": 3, "Diplomatic": 3, "Scheming": 2},
    )
    m["gunhilda_henrasdottir"] = b.magus(
        "Gunhilda Henrasdottir",
        covenant=oculus,
        house=JERBITON,
        age=31,
        summary=(
            "Journeyman of House Jerbiton and of the Apple Gild, Henri's "
            "daughter and filia. Plump and over-sheltered, she specialises "
            "in housecraft and is married to Estrid Danesson."
        ),
        traits={"Loyal to Family": 3, "Compassionate": 1, "Independent": -2},
    )
    m["estrid_danesson"] = b.magus(
        "Estrid Danesson",
        covenant=oculus,
        house=EX_MISC,
        age=36,
        summary=(
            "Journeyman of House Ex Miscellanea and of the Apple Gild, a "
            "recent recruit and the second Scandinavian wizard the covenant "
            "has taken in. A man of Ribe who joined the Order late as a "
            "hedge wizard of sailing and weather, a flamboyant rogue whose "
            "sanctum and lab are aboard his ship; he gathers the covenant's "
            "vis around the Baltic and is married to Gunhilda. He is the "
            "younger cousin and bitter enemy of Eric Ribecus of Waddenzee; "
            "they have fought at sea, though no Wizard's War has been "
            "declared."
        ),
        traits={"Extroverted": 2, "Energetic": 1, "Conciliatory": -3},
    )
    m["marcus_navicularius"] = b.magus(
        "Marcus Navicularius",
        covenant=oculus,
        house=VERDITIUS,
        age=58,
        summary=secrets(
            "Master of House Verditius and of the Apple Gild, Lübeck's "
            "foremost shipwright: large and stern, with iron-grey hair and "
            "beard, owner of a shipyard that is also his workshop and lab, "
            "staffed by skilled craftsmen. A Terram master whose enchanting "
            "suits very large things such as ships and cannot work on "
            "anything smaller than a sword; he sells magical ships to "
            "covenants for vis and lost the Nebelkönigin to Waddenzee. He "
            "is designing the Baltic cog the Hanse will adopt.",
            "He secretly corresponds with Aelfhere, Waddenzee's shipwright.",
        ),
        traits={"Proud of his Abilities": 3, "Skillful": 1, "Friendly": -2},
    )
    m["imanitos_mendax"] = b.magus(
        "Imanitos Mendax",
        covenant=oculus,
        house=JERBITON,
        age=55,
        summary=secrets(
            "Master of House Jerbiton, lately so by the approval of three "
            "Fengheld magi, Apple Gild trained, Gauntleted at twenty-two "
            "after an apprenticeship at Doissetep in Provence. Tall, lean "
            "and handsome, black-haired and blue-eyed, in fashionable blue "
            "or black, with a serpent-and-ruby ring he means for his "
            "talisman; a vanity longevity ritual keeps him looking "
            "thirty-nine. He poses as owner of the upmarket tavern Goldenes "
            "Kalb, above which a discreet brothel for rich clients is helped "
            "along by wine that heightens lust, and his third trade is the "
            "blackmail and extortion of citizens and magi. His focus is "
            "Mentem, with competent Imaginem for disguises; his Twilight "
            "has left him a hidden forked tongue, a compelling voice and a "
            "faint smell of funerary incense. His covenant-mates find him "
            "useful despite his morals; his sanctum on the top floors of "
            "his townhouse is secret and magically guarded.",
            "He sells Oculus Septentrionalis's ship movements to Eric "
            "Ribecus of Waddenzee for a share of the plunder. Optionally a "
            "diabolist of a hidden dark Jerbiton lineage, servant of the "
            "demon Radegast, corrupting Lübeck's notables through the "
            "Goldenes Kalb and posing as Radegast's prophet to the "
            "Mecklenburgs; he might swap the covenant's magestones for "
            "tainted copies.",
        ),
        traits={"Lustful": 3, "Scheming": 2, "Brave": -1},
    )
    m["carolus"] = b.magus(
        "Carolus",
        covenant=oculus,
        house=JERBITON,
        age=35,
        summary=(
            "Journeyman of House Jerbiton and of the Apple Gild, well "
            "meaning and scatterbrained, who poses as an eccentric scholar "
            "tutoring the citizens. A naive visit to Crintera to mend "
            "relations went wrong when Caprea of Bjornaer, a guest there, "
            "blinded his raven familiar as a spy; the real spy was "
            "Kolkrabus, Murion's familiar."
        ),
        traits={"Analytical": 2, "Idealistic": 1, "Organized": -3},
    )
    m["boris_of_novgorod"] = b.magus(
        "Boris of Novgorod",
        covenant=oculus,
        house=MERCERE,
        age=37,
        summary=(
            "Journeyman Redcap of House Mercere, not of the Apple Gild, a "
            "well-travelled, shrew-like Russian posing as an itinerant "
            "merchant who serves the northern Rhine and Novgorod. He owns "
            "the new Novgorod Inn at the north end of town, popular with "
            "Redcaps and Russian merchants, and hopes for Master rank "
            "within a couple of years so that it may become a Mercer "
            "House. He sells trinkets, trades books, items and vis, and "
            "gets Novgorod vis cheaply."
        ),
        traits={"Indolent": 2, "Avaricious": 1, "Talkative": 1},
    )
    m["brunhilda"] = b.magus(
        "Brunhilda",
        covenant=oculus,
        house="",
        age=None,
        summary=(
            "Henri's Swedish wife of more than thirty years, a seeress in "
            "the Norse manner who sends her spirit out in animal form while "
            "in trance. Not Gifted enough for the Order but treated as an "
            "equal by the magi; she runs the covenant's daily affairs more "
            "than Henri does, and her divination guides his luck in trade."
        ),
        type="companion",
    )
    m["matilda"] = b.magus(
        "Matilda",
        covenant=oculus,
        house="",
        age=None,
        summary=(
            "Gunhilda's elder, un-Gifted sister, autocrat of the covenant "
            "and Henri's housekeeper."
        ),
        type="companion",
    )
    b.book(
        oculus,
        "Oculus Septentrionalis's library",
        "Other",
        description=(
            "Good-sized but below Fengheld's or Triamore's and far below "
            "Durenmar's, kept in Henri's townhouse on the Holstenstrasse. "
            "Mostly mundane books; its best Hermetic texts are in Rego, "
            "Mentem, Imaginem and Corpus. No titles or levels are given."
        ),
    )


# ---------------------------------------------------------------- Fengheld


def _fengheld(rhine: Rhine, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "The largest covenant of the Rhine in land, people and magi, "
        "twenty-three of them with about a dozen at the main site, and the "
        "most diverse, with no House or gild dominant: an Autumn covenant "
        "in a sprawling hilltop fortress in a lonely spot among the hills "
        "of the eastern Harz, on the borders of Saxony and Thuringia, with "
        "a Magic aura of 5 on the hilltop and half a dozen chapter houses "
        "across northern mainland Europe. It presents itself as the "
        "Tribunal's neutral peacemaker and often arbitrates between "
        "covenants; both the Apple and the Linden Gilds were founded by "
        "its members.",
        "Founded in 1039 by Flambeau and Tremere veterans home from the "
        "Schism War in Stonehenge and Normandy, approved readily as a quiet "
        "retreat for ageing war heroes away from mundanes, it became "
        "instead the base from which its political Tremere, with the "
        "Transylvanian Tribunal, served Emperor Henry III's conquests of "
        "Bohemia, Poland and Hungary and seized many vis sites. When the "
        "main site filled, the Tribunal blocked its daughter covenants of "
        "young Tremere, so it founded chapter houses instead, citing "
        "Greater Alps practice and trusting its martial strength to hold "
        "several sites. Every chapter magus accepts Fengheld's charter, a "
        "ruling on Fengheld binds the chapters and the reverse, and most "
        "chapters have a local charter too. Ties with Transylvania have "
        "lately loosened and it is no longer seen as a Tremere covenant.",
        "Its hierarchy is rigid: the Archmage Stentorius; eight masters, "
        "five at the main site (Eule, Horst, Peter von Würzburg, Dorana, "
        "Indulius) and three in chapters (Clemens, Hassan El-Megrayhi, "
        "Wilhelm Weiss); then fourteen journeymen, the six at the main "
        "site ranking a little above the eight in chapters. Of the eleven "
        "chapter magi six are detailed in five chapters and five are left "
        "to the storyguide, as is the site of the biggest chapter, run by "
        "Clemens filius Stentorius, which could sit near the player "
        "covenant; or the player magi could themselves be a chapter under "
        "Fengheld's seniors.",
        "An immense curtain wall rings a summit of some twenty buildings: "
        "a tower for every resident magus, an elaborate guest house, a "
        "huge meeting hall and housing for covenfolk and grogs, with "
        "outlying hamlets. Vineyards and orchards cover the south slope, "
        "grain and roots the valley floor, sheep and goats the rest, "
        "feeding well over two hundred people: about fifty soldiers, "
        "fifteen companions and nearly ten dozen smiths, glassblowers, "
        "parchment-makers, scribes, huntsmen, herders and serfs, each "
        "hierarchy ending in a magus. Eight guest labs at the main site "
        "and at least one at most chapters make it a famed host of "
        "peregrinatores, with up to six Redcaps present at a time. It is "
        "rich in minor enchanted items and raw vis.",
        "Fengheld holds one of the Rhine's two Mercer Houses and its "
        "senior Redcap, and is the busier of the two for its central "
        "position and its generosity: Redcaps serving the north, Boris of "
        "Novgorod among them, meet those serving the south here at agreed "
        "times, and Redcaps from other Tribunals who will not cross the "
        "Black Forest come here instead of Durenmar. This near-monopoly of "
        "the Order's news serves Fengheld well.",
    )
    what_matters = _lines(
        "Vis: about two dozen sites, some hundreds of miles away, many seized in the eastern conquests of the 11th century; none is named",
        "Vis: a rook a year goes to Oculus Septentrionalis (secretly) for luxuries and silver",
        "Income: a vast farming estate, Peter von Würzburg's wines, and the trade of the Rheingasse and Cherbourg chapters",
        "Mundane: the local nobility has somehow never noticed the scale of the estate, and nobody has openly accused Fengheld of magic to keep it so; Peter's wines are prized by the nobles of southern Saxony and Thuringia",
        "Mundane: the Rheingasse chapter in Cologne manages supplies and contacts; Fengheld House in Cherbourg trades with England and France",
        "Votes: more than forty Tribunal votes, nearly a quarter of the whole, though seldom cast as a bloc; Stentorius holds about three-fifths of the Rhine's Tremere sigils",
        "Tension: the more paranoid magi of the Tribunal suspect a hidden agenda behind the neutrality",
        "Tension: Fengheld and its allies oppose Philippus Niger of Durenmar at every turn; Dorana urges Stentorius to contest Murion's leadership of the Oak Gild and Occultes to contest her Primacy, while the familiars Oswald and Kolkrabus feud over the gild",
        "Tension: a planned chapter at Durenmar, Rudolph of Bonisagus's idea, is backed cautiously and doubted by some seniors",
        "Tension: the Lusatia chapter, ten miles from the agreed Novgorod border, caused the latest boundary dispute with that Tribunal; Odorpes has been accused at Tribunal more than once of neglecting her duties",
        "Allies: a mutual understanding with Waddenzee; Hassan El-Megrayhi is parens of Hachim of Waddenzee, and Imanitos Mendax of Oculus Septentrionalis won his Master rank here",
        "Hook: the library is vast but weighted to low-level books, so Fengheld-trained magi are generalists; specialists are invited as guests to improve it",
        "Hook: Balastor means to return others to a feral state whether they consent or not",
    )
    hidden = _lines(
        "Fengheld's real policy is to keep every other covenant so tangled in politics that nobody notices its own growing power; it has worked so far, and its vote bloc is the Tribunal's largest.",
        "Eule has passed into Final Twilight, and her celebrated wisdom is her filius Günther Lupus's fraud.",
        "The Bears' Cave in the northern Harz is the private vis source of a hidden lineage of bear-heartbeast Bjornaer descending from the Founder: Urgen of Crintera and his filia Odorpes of the Lusatia chapter.",
    )
    fengheld = b.covenant(
        "Fengheld",
        tribunal=tribunal,
        founded=1039,
        place=rhine.places.get("fengheld_site"),
        summary=summary,
        what_matters=what_matters,
        notes=secrets(STORYGUIDE, hidden),
        aura=5,
        unnamed_magi=7,
        season="Autumn",
    )
    rhine.covenants["fengheld"] = fengheld
    _fengheld_magi(rhine, b, fengheld)
    _fengheld_chapters(rhine, b, fengheld)
    b.book(
        fengheld,
        "Fengheld's library",
        "Other",
        description=(
            "Vast, but dominated by lower-level books than a covenant of "
            "this size should hold, so that Fengheld-trained magi are "
            "generalists; the covenant makes up for it by hosting "
            "specialist guests. No titles or levels are given."
        ),
    )
    b.book(
        fengheld,
        "Horst's books",
        "Other",
        author="Horst",
        description=(
            "Horst of Mercere's famed, prolific, high-quality books on a "
            "great range of mundane subjects and on Magic Theory, the "
            "backbone of most Rhine apprenticeships and a mainstay of the "
            "library. No titles or levels are given."
        ),
    )


def _fengheld_magi(rhine: Rhine, b: Builder, fengheld: Covenant) -> None:
    m = rhine.magi
    m["stentorius"] = b.magus(
        "Stentorius",
        covenant=fengheld,
        house=TREMERE,
        age=107,
        summary=(
            "Archmage of House Tremere, leader of the Oak Gild, "
            "authoritarian princeps of Fengheld and Tremere exarch of the "
            "Rhine, holding about three-fifths of the Tribunal's Tremere "
            "sigils, his filius's and the two Tremere of Triamore among "
            "them, while Severicus of Roznov holds the rest. Large and "
            "ageing well nearly a century past his Gauntlet, with a bushy "
            "iron-grey beard to his chest and a craggy nose; a famed master "
            "of Rego, able with most Forms, in showy deep-crimson robes "
            "covered in the symbols of Rego, the Forms and his House. His "
            "familiar of more than fifty years is Oswald, a hugely arrogant "
            "large grey cat in a jewelled gold pendant holding several uses "
            "of Aura of Rightful Authority among other effects, who believes "
            "he rules Fengheld if not the Tribunal; Murion's raven "
            "Kolkrabus taunts him at Durenmar for usurping her place at the "
            "head of the Oak Gild."
        ),
        traits={"Proud": 3, "Stickler for Rules": 2, "Forgiving": -3},
    )
    m["horst"] = b.magus(
        "Horst",
        covenant=fengheld,
        house=MERCERE,
        age=68,
        summary=(
            "Master of House Mercere, an un-Gifted Redcap, senior Redcap of "
            "the Rhine Tribunal and master of Fengheld's Mercer House, where "
            "many Redcaps rest between journeys. A famous and prolific "
            "author of high-quality books on a huge range of mundane "
            "subjects and on Magic Theory, the backbone of most Rhine "
            "apprenticeships; corpulent, with a near-encyclopaedic memory "
            "consulted at Tribunal on obscure points of Hermetic law. "
            "Wholly apolitical, so his knowledge of the Order's business is "
            "of no political use to Fengheld. He wrote the visitor's "
            "account of Durenmar."
        ),
        traits={"Widely-Read": 3, "Fascinating": 2, "Political": -3},
    )
    m["eule"] = b.magus(
        "Eule",
        covenant=fengheld,
        house=BJORNAER,
        age=160,
        summary=secrets(
            "Master of House Bjornaer with the honorary rank of Quaesitor "
            "from House Guernicus, retired from official duty; for many "
            "years she was the Rhine's only senior Quaesitor. Owl "
            "heartbeast, and with Caecilius of Durenmar and Schadrit of "
            "Dankmar one of the oldest magi in the Tribunal. Magi still "
            "come to her for her celebrated advice.",
            "Only her filius Günther Lupus suspects that she has passed "
            "into Final Twilight: she has not taken human shape for years "
            "and has not spoken for longer. Her wisdom is a fraud. An item "
            "hidden in the floor of her audience room casts a low-level, "
            "very high Penetration Perdo Mentem effect that calms the mind "
            "and strips emotion, Günther translates her hoots with a few "
            "leading prompts, and the calmed petitioners find their own "
            "answers and thank Eule.",
        ),
        traits={"Owlish": 6, "Apathetic": 3, "Wise": 3},
    )
    m["peter_von_wurzburg"] = b.magus(
        "Peter von Würzburg",
        covenant=fengheld,
        house=VERDITIUS,
        age=62,
        summary=(
            "Master of House Verditius, a celebrated vintner and "
            "grape-grower within the Order and among the nobles of southern "
            "Saxony and Thuringia. Minor enchanted items let the vines on "
            "Fengheld's south slope thrive this far north, and he turns "
            "special varieties into wines that are Charged Items; his "
            "squirrel familiar is as industrious as he is, and the two are "
            "seen tying vines, testing the sweetness and fertilising. "
            "Usually the first magus a visitor meets, out among the grapes; "
            "he oversees the head vintner, the orchard keeper and the farm "
            "foreman."
        ),
        traits={"Charming": 3, "Generous": 2, "Industrious": 2},
    )
    m["dorana"] = b.magus(
        "Dorana",
        covenant=fengheld,
        house=BONISAGUS,
        age=76,
        summary=(
            "Master of House Bonisagus, the leading maga in the Rhine of "
            "the lineage of Irmele filia Trianoma. Decades as a "
            "peregrinator before she settled at Fengheld taught her nearly "
            "every covenant and many magi of the Tribunal in detail; she "
            "argues for reason and peace in Fengheld's dealings and usually "
            "wins. She detests her Prima, Murion, pressing Stentorius to "
            "contest the Oak Gild and her close ally Occultes of Durenmar "
            "to contest the Primacy. A weather specialist, she manages the "
            "sun, rain and visitor-deterring fog that Fengheld's farms and "
            "privacy depend on; her latest apprentice Felecia has just "
            "passed her Gauntlet and gone travelling."
        ),
        traits={"Hedonistic": 2, "Peaceful": 1, "Secretive": -2},
    )
    m["indulius"] = b.magus(
        "Indulius",
        covenant=fengheld,
        house=FLAMBEAU,
        age=None,
        summary=(
            "Master of House Flambeau and a feared hoplite, who hunts "
            "oath-breakers in an odd but effective pairing with Günther "
            "Lupus."
        ),
    )
    m["gunther_lupus"] = b.magus(
        "Günther Lupus",
        covenant=fengheld,
        house=BJORNAER,
        age=None,
        summary=secrets(
            "Magus of House Bjornaer (rank not given), Eule's filius, wolf "
            "heartbeast. He hunts oath-breakers with Indulius and attends "
            "his ancient parens.",
            "He is the author of the Eule fraud, keeping up the myth of her "
            "wisdom with a hidden Perdo Mentem item and his own translation "
            "of her hoots.",
        ),
    )
    m["balastor"] = b.magus(
        "Balastor",
        covenant=fengheld,
        house=CRIAMON,
        age=26,
        summary=(
            "Journeyman of House Criamon whose philosophy matches the "
            "Hawthorn Gild. Born feral, he had a powerful vital spirit his "
            "master saw fade as he learned speech and human ways, and he "
            "now means to return himself, and others whether they consent "
            "or not, to that primal state, holding that enlightenment "
            "demands casting off the mundane. His magic releases suppressed "
            "emotion and behaviour, and a Warped Magic flaw gives his face a "
            "savage cast when he casts; a puckish troublemaker who loves "
            "humbling self-important mundanes."
        ),
        traits={"Feral": 3, "Mischievous": 3, "Contempt for Humanity": 2},
    )
    m["beechleaf"] = b.magus(
        "Beechleaf",
        covenant=fengheld,
        house=MERINITA,
        age=20,
        summary=(
            "Journeyman of House Merinita, fresh-faced, apprenticed at "
            "Irencillia by the Primus Handri and newly offered a place at "
            "Fengheld's main site, which makes him uneasy because he cannot "
            "see the political reason for it. Raised by a dryad, he "
            "understands faeries far better than people; his skin is "
            "faintly green and his bronze hair stirs in a wind nobody else "
            "feels."
        ),
        traits={"Otherworldly": 2, "Suspicious": 2, "Naive": 1},
    )
    m["rudolph"] = b.magus(
        "Rudolph",
        covenant=fengheld,
        house=BONISAGUS,
        age=None,
        summary=(
            "Magus of House Bonisagus (rank not given) and author of the "
            "plan to plant a Fengheld chapter inside Durenmar itself, which "
            "Fengheld backs cautiously and some of its seniors doubt. His "
            "membership of Fengheld is implied rather than stated."
        ),
    )


def _fengheld_chapters(rhine: Rhine, b: Builder, fengheld: Covenant) -> None:
    m = rhine.magi
    m["clemens"] = b.magus(
        "Clemens",
        covenant=fengheld,
        house=TREMERE,
        age=None,
        summary=(
            "Master of House Tremere, filius of Stentorius and Fengheld's "
            "most senior master, who runs its biggest chapter house. Where "
            "that chapter lies is left to the storyguide, perhaps near the "
            "player covenant; nothing else is given of him."
        ),
    )
    m["marguerite"] = b.magus(
        "Marguerite",
        covenant=fengheld,
        house=FLAMBEAU,
        age=None,
        summary=(
            "Maga of House Flambeau (rank not given) who lives at Fengheld "
            "House, the covenant's most remote chapter: a simple fortified "
            "townhouse in Cherbourg in Normandy, outside the Rhine, owned by "
            "Sir Jozef of Poznan, a Polish-born crusader, and running a "
            "small trade with England and France. Stunningly beautiful and "
            "every bit as rude, she holds mundanes beneath her and never "
            "passes up a cutting remark."
        ),
    )
    m["wilhelm_weiss"] = b.magus(
        "Wilhelm Weiss",
        covenant=fengheld,
        house=JERBITON,
        age=None,
        summary=(
            "Master of House Jerbiton and co-leader of the Apple Gild, who "
            "lives at the Rheingasse chapter in the centre of Cologne, where "
            "he and Garrinchus, both Gentle-Gifted, arrange Fengheld's "
            "supplies and mundane contacts very ably. He poses as a wealthy "
            "merchant."
        ),
    )
    m["garrinchus"] = b.magus(
        "Garrinchus",
        covenant=fengheld,
        house=EX_MISC,
        age=None,
        summary=(
            "Newly Gauntleted journeyman of House Ex Miscellanea and of the "
            "Apple Gild, living at the Rheingasse chapter in Cologne with "
            "Wilhelm Weiss, where the two Gentle-Gifted magi see to "
            "Fengheld's supplies and contacts. His master was a recognised "
            "expert in physick."
        ),
    )
    m["hassan_el_megrayhi"] = b.magus(
        "Hassan El-Megrayhi",
        covenant=fengheld,
        house=CRIAMON,
        age=None,
        summary=(
            "Master of House Criamon and astronomer, who lives at Turris "
            "Acontiarum, a solitary tower in the Kyffhäuser Mountains on "
            "the Saxon-Thuringian border, studying the stars with a single "
            "mute companion. He is parens of Hachim al'Khalejj of "
            "Waddenzee."
        ),
    )
    m["odorpes"] = b.magus(
        "Odorpes",
        covenant=fengheld,
        house=BJORNAER,
        age=None,
        summary=secrets(
            "Maga of House Bjornaer (rank not given), filia of Urgen, "
            "Archmage of Crintera, and sole inhabitant of the Lusatia "
            "chapter, an idyllic house on a bend of the Spree in the March "
            "of Lusatia only ten miles from the agreed Novgorod border, "
            "whose founding caused the latest boundary dispute between the "
            "two Tribunals. Bear heartbeast, in which she spends most of "
            "her time, hibernating all winter; a poor member, accused by "
            "Fengheld at Tribunal more than once of neglecting her duties, "
            "but never punished hard for fear of her aggressive, powerful "
            "parens.",
            "She and Urgen are the two living magi of a hidden lineage of "
            "bear-heartbeast Bjornaer descending from the Founder herself; "
            "they harvest the Bears' Cave in the northern Harz.",
        ),
    )
