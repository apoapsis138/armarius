"""The land of the Rhine Tribunal: its six regions, the forests, mountains,
lakes, ruins, caves, sacred sites and regiones of chapters 4 to 10 of
Guardians of the Forests, and the sites of its covenants, each a Place the
other parts of the pack set their records in.

The Rhine Gorge's own places (chapter 12) are made by gorge.py, which also
makes the Westerwald; towns, lords, churches and people are made by the
world parts. A place's summary names the creatures and spirits that live
there with their realm and Might, and a regio level's notes what is found
on that level. Secrets sit at the end of a summary or a level's notes under
the Secrets heading."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..builder import Builder, paragraphs, secrets

if TYPE_CHECKING:
    from ...models import Neighbour
    from . import Rhine

RUMOURED = {"status": "Rumoured", "known": "Locally"}
KNOWN_TRIBUNAL = {"status": "Known", "known": "In the Tribunal"}
KNOWN_REGION = {"status": "Known", "known": "In the region"}
KNOWN_LOCALLY = {"status": "Known", "known": "Locally"}
KNOWN_ORDER = {"status": "Known", "known": "In the Order"}


def _add(rhine: Rhine, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and store it under `key` for the other parts."""
    place = rhine.b.place(name, **kw)
    rhine.places[key] = place
    return place


def build(rhine: Rhine) -> None:
    _regions(rhine)
    _hercynian(rhine)
    _rhine_valley(rhine)
    _black_forest(rhine)
    _lowlands(rhine)
    _central(rhine)
    _east(rhine)
    _bohemia(rhine)


# -- the six regions --


def _regions(rhine: Rhine) -> None:
    _add(
        rhine,
        "rhine_valley",
        "The Rhine Valley and Lorraine",
        summary=paragraphs(
            "The river country from Basel, where the Rhine turns north and ships "
            "begin to sail it, down past Strassburg, Speyer, Worms and Mainz to "
            "Cologne and the marshy delta about Utrecht and Deventer, together "
            "with the lands west of it: the Vosges, Upper Lorraine round Metz, "
            "Toul and Verdun, and Lower Lorraine with Aachen, Liege and the "
            "Ardennes on the Tribunal's western fringe.",
            "This is the oldest settled part of Germany, built on Roman colonies "
            "and legionary camps, and the Church is strongest here: the cathedral "
            "of Mainz has a Divine aura of 7 as a Holy See, those of Speyer, "
            "Worms, Trier, Aachen and Cologne 6, and most cities 3. Trade along "
            "the river makes its archbishops rich and its cities large; the Jewish "
            "communities of Mainz, Speyer and Worms are the greatest in Germany.",
            "The Middle Rhine between Mainz and Koblenz, the Mosel and the Lahn "
            "belong to the Rhine Gorge and its curse, which the saga chapter "
            "describes.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        rhine,
        "black_forest",
        "The Black Forest",
        realm="Faerie",
        aura=3,
        summary=paragraphs(
            "The largest forest of western Europe fills the south-west of the "
            "Tribunal: over a hundred miles north to south and up to forty "
            "across, all hills under an unbroken canopy, with the Rhine plain to "
            "the west and the Neckar and the Swabian uplands to the east. Oak and "
            "beech grow on the lower slopes and fringes; in the centre and on the "
            "heights the fir stands so thick that no sunlight reaches the floor. "
            "There are no clearings, little level ground, a few villages at the "
            "edges and about a dozen monasteries drawn by the seclusion.",
            "A Faerie aura of 3 lies over the whole forest, broken only by the "
            "Divine islands of its monasteries and a few Magic sites: Durenmar, "
            "the Fane of the Founders and the Glade of the Seven Waterfalls. "
            "Bears, boars and deer share it with stranger beasts; bockmen, goblins "
            "and giant bats hunt by night, villagers who go too deep vanish, and "
            "the few folk living inside are said to be half fay. Only the old "
            "Roman road crosses it; anywhere else is weeks on foot.",
            "The forest was once the south-western part of the Hercynian Forest, "
            "cut off when the Romans built the limes, and its spirit split with "
            "it. The Cult of Mercury bound the greater part by its own oath-magic "
            "into what is now the Fane of the Founders, and the peaceful remnant "
            "withdrew to the Glade; a rebellious splinter fled south, dwindled, "
            "and regrew on mortal fear as the dark faerie King of the Black "
            "Mountain (Faerie, Might 60), who now rules every dark court of the "
            "forest. Since Durenmar's condemnation in 1151 the forest has been a "
            "hazard to magi, and no peace with the fay was ever made. The Swabian "
            "lands east of the forest, the Jura and the sources of the Danube, "
            "belong to this region too.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        rhine,
        "lowlands",
        "The Lowlands",
        summary=paragraphs(
            "The northern third of Germany, flat and much alike from end to end: "
            "from the North Sea eastward the Frisian islands and the Wadden Sea, "
            "then swamp and moor, then some two hundred miles of farmland with "
            "prosperous cities and few forests, reaching Saxony, Westphalia, "
            "Holstein and the Baltic coast about Lübeck.",
            "Its cities are ruled by trade rather than by princes. The southern "
            "ones were founded by Charlemagne after he conquered the Saxons or "
            "grew from missionary bishoprics; the northern ports are newer, rich, "
            "and reaching for Free Imperial status, though Holstein and Pomerania "
            "lie for the moment under King Valdemar II of Denmark.",
            "Magi here feel themselves on a Hermetic frontier: most know of some "
            "Scandinavian wizard beyond the border, Lübeck is the Redcaps' usual "
            "stop toward Novgorod, and the Divine auras run a little weaker toward "
            "the Baltic than in the Rhineland.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        rhine,
        "central",
        "Central Germany",
        summary=paragraphs(
            "The heart of Germany and of the Empire: from the Harz on the edge of "
            "Saxony down through Thuringia and Franconia to the Danube, and the "
            "smaller part of Bavaria north of the river that was never Roman and "
            "belongs to the Rhine Tribunal (the Danube cities, Regensburg chief "
            "among them, are claimed by the Greater Alps).",
            "Rolling hills, rocky isolated wildernesses and countless magic and "
            "faerie forests of every size, only moderately peopled. Its cities are "
            "younger than the Roman ones of the Rhine but weigh heavily in trade "
            "and imperial politics, and its courts and cathedrals have grown a "
            "distinctly German culture: the Wartburg's minnesänger, Nuremberg's "
            "imperial castle, the great abbeys of Fulda and Hersfeld.",
            "Fengheld, the Tribunal's largest covenant, sits in the eastern Harz, "
            "and the Harz, the Kyffhäuser and the Thuringian Forest hold some of "
            "the strongest spirits of the old Hercynian Forest.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        rhine,
        "east",
        "The Eastern Marches",
        summary=paragraphs(
            "The lands between the Elbe and the Oder: lakes and forest, thinly "
            "settled, with the reputation of a home of werewolves, witches and "
            "giants and the decaying temples of the Slavic gods. Christianity came "
            "in the tenth century from the frontier bishoprics of Magdeburg and "
            "Merseburg; since then war and peace with the Slavs have alternated, "
            "German settlers have poured in, and German speech now prevails.",
            "Meissen in the south-west is wholly German, Lusatia in the south-east "
            "mostly Sorbian, and Rügen and Pomerania in the north a mixture under "
            "Danish overlords. Land is so plentiful that the local rulers seldom "
            "quarrel with one another. Nearly every pagan or magical site of the "
            "southern Marches has been destroyed; more survive in Pomerania.",
            "Apart from Crintera the Order has little presence here, but the Rhine "
            "Tribunal claims the Marches firmly, disputes its eastern border with "
            "the Novgorod Tribunal, and would gladly push further into Polish "
            "lands. The Baltic freezes for months every winter and must be thawed "
            "each spring by a ritual cast at Arkona.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        rhine,
        "bohemia",
        "Bohemia and Moravia",
        summary=paragraphs(
            "The Tribunal's south-east: the subject kingdom of Bohemia and its "
            "March of Moravia, broad half-wooded plains along the upper Elbe and "
            "its tributaries, ringed and divided by long wooded mountain chains. "
            "There are no great cities, only modest towns thinly spread, and in "
            "1220 the only notable ones lie about and north of Prague.",
            "The Premyslid dynasty, descended from the legendary Czech, has ruled "
            "since the eighth century; Christianity came in the ninth with St "
            "Methodius and took generations to root. Barbarossa raised the duchy "
            "to a kingdom a generation ago, and King Otakar reigns now as a "
            "semi-independent tributary of the Empire. Farming, hunting, mining, "
            "glass, brewing and horse-breeding are its trades.",
            "Moravia is the Empire's easternmost reach, bordering Hungary and the "
            "Transylvanian Tribunal, whose influence, especially House Tremere's, "
            "the magi here feel often. Irencillia, the domus magna of Merinita, "
            "hides in the Bohemian Forest, and Roznov holds the Carpathian border.",
        ),
        **KNOWN_ORDER,
    )


# -- the Hercynian Forest and the Seasonal Courts --


def _hercynian(rhine: Rhine) -> None:
    hercynian = _add(
        rhine,
        "hercynian_forest",
        "The Hercynian Forest",
        summary=paragraphs(
            "The primeval oak forest the Romans found beyond the Alps, nine days "
            "wide and of a length nobody knew, covering all of Germania. It had a "
            "single vast spirit of the Magic realm (Magic, Might not given), a "
            "reflection of the Ideal Forest that some magi call Eden. The rituals "
            "of the Cult of Mercury, who guided the legions in building the limes "
            "and its magically linked roads, and later St Boniface's felling of "
            "the Donar Oak in the eighth century, shattered that spirit into the "
            "genii loci of today's forests.",
            "Each fragment met one of four fates: survival as a Magic forest (the "
            "Teutoburger Forest, the Drudenbaum, the Romowe oak), dissolution into "
            "a mundane wood (the Hertogenwald), replacement by a being of another "
            "realm, usually Faerie (the Black Forest, the Ash of Nortorf, the "
            "Donar Oak), or alliance with a faerie (the Four Seasonal Courts). The "
            "forests have hardly shrunk since Charlemagne's day and resist "
            "clearance as if by will. Each still holds a direct link to the Magic "
            "realm, the primal power that drew the Cult of Mercury and Bonisagus "
            "himself, and the paths through the forest that House Bjornaer and "
            "some Merinita can show lead to it.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        rhine,
        "seasonal_courts",
        "The Four Seasonal Courts",
        inside=hercynian,
        realm="Faerie",
        aura=3,
        summary=paragraphs(
            "Four linked faerie forests, Holly, Alder, Oak and Willow, that the "
            "storyguide places where the saga needs them, ideally in a ring at the "
            "cardinal points about the player covenant; the names are conveniences, "
            "not true names. They are four fragments of one spirit, perhaps once "
            "as strong as the Black Forest's, each too weak to live alone and each "
            "allied with or possessing a faerie lord. The aura of each is Faerie, "
            "rising to 3 across the whole wood at its court's solstice or equinox "
            "and shrinking month by month to nearly nothing at the opposite "
            "season; patches of Magic aura linger in the Oak Forest, and every "
            "ruler has the Regio power (levels not given).",
            "King Holly (Faerie, Might 40, pool 20 to 50; north, winter; "
            "Tyrannical +3, Cold-hearted +2) rules a court of ice and frost "
            "faeries from a holly grove by an iron will and a detailed law; the "
            "spirit forcibly possessed a rebellious winter faerie. The Alder Prince "
            "(Faerie, Might 40; west, spring; Compassionate +3, Secretive +2) is "
            "red-hued, shy and benign, keeps a shrouded court in a serene vale and "
            "rules many holzfrauen. King Oak (Faerie, Might 40; south, summer; "
            "Regal +3, Generous +2) holds court under a great oak as a generous "
            "host whose honour is touchy and who takes words literally, so a slip "
            "binds a guest in an enforced contract. The Willow Maiden (Faerie, "
            "Might 40; east, autumn; Manipulative +3, Uncaring +2) seems generous "
            "but every gift has a hidden price; she has slipped the spirit's pact "
            "and all but owns her wood, and is obsessed with the Alder Prince.",
            "The courts are bound in a yearly drama of stolen power in which the "
            "coming season's court raids the reigning one: in December Holly at "
            "full strength slays Oak, who is reborn in his forest; in March Alder "
            "heals the Willow Maiden's malice with love and she flees home; in June "
            "Oak captures Holly and imprisons him in the heart of the Holly Forest; "
            "in September the Willow Maiden weds and drowns the Alder Prince in her "
            "river. Each ruler keeps Might 40 for resistance and Penetration all "
            "year while its pool swings by five a month. Summer against Winter is "
            "open war; Spring against Autumn is subtle politics and should pay "
            "better, and vis is the obvious wage for taking a side.",
        ),
        **RUMOURED,
    )


# -- chapter 5: the Rhine, Lorraine and the Vosges --


def _rhine_valley(rhine: Rhine) -> None:
    region = rhine.places["rhine_valley"]
    _add(
        rhine,
        "triamore_site",
        "The castle of Triamore",
        inside=region,
        aura=2,
        summary=(
            "A castle and manorial estate on the river Meuse at the edge of the "
            "Ardennes, in Lower Lorraine on the western fringe of the Tribunal, "
            "with Liege and Verdun the nearest towns of note. The Magic aura is 2. "
            "Redcaps bound between the Rhine and Normandy Tribunals make it, with "
            "Verdun, their usual meeting point."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "rhinefalls",
        "The Rhinefalls",
        inside=region,
        aura=2,
        tethers="The Spirit of the Rhine pinned beneath the rock",
        levels=[
            Builder.level(
                "The lower levels of the rock",
                0,
                enter="Climbing alone cannot enter the regio; powerful magic is needed",
                notes=secrets(
                    "Several levels rise with the climb; their auras are not given.",
                    "Schwall of Bjornaer, an elderly Wilderist of the Hawthorn Gild "
                    "formerly of Rheinstein, keeps a hidden sanctum here. His "
                    "heartbeast is believed a fish, he can also become a mass of "
                    "water, and his many Twilight Scars leave him always wet. He has "
                    "completed several Quests for the Rhine spirit.",
                ),
            ),
            Builder.level(
                "The elemental summit",
                0,
                enter="Powerful magic; no climb reaches it",
                notes=(
                    "A turbulent realm of raw elemental water (aura not given). The "
                    "Rhinegold and the other treasures hurled into the falls over "
                    "the centuries may lie here."
                ),
            ),
        ],
        summary=paragraphs(
            "The greatest falls of Europe, five hundred feet wide and eighty "
            "high, on the Upper Rhine below Constance near the south-eastern "
            "edge of the Black Forest. In their midst stands a rock island "
            "taller than the falls with a copse on top; it can be reached only "
            "by boat from downstream (Profession: Boating against 9) and climbed "
            "only on slippery rock (Athletics against 12), and the summit is a "
            "deafening place of raw elemental power. The island's Magic aura is "
            "2, rising to 4 at the summit, and a regio of several levels climbs "
            "from it.",
            "Under the rock lies the Spirit of the Rhine (Magic, Might not "
            "given), a river elemental pinned there long ago when the "
            "Nibelungs, dwarves and giants tamed the wild river; it is said to "
            "guard the Rhinegold in revenge. Those who climb the rock and hurl "
            "valuables into the maelstrom find the smashed fragments washed up "
            "downstream later, each worth a pawn of Aquam vis; it is never "
            "found by accident.",
        ),
        secrets="Schwall's final Quest is to free the Rhine elemental and merge his "
        "mind with it, a kind of immortality before Final Twilight takes him; "
        "the floods that would wreck shipping, towns and cities along the whole "
        "river are to him a welcome bonus. The early signs are disturbances on "
        "the river. The Tribunal would March anyone involved, but he expects "
        "to be beyond its reach.",
        **RUMOURED,
    )
    _add(
        rhine,
        "mount_saint_odile",
        "Mount Saint Odile",
        inside=region,
        realm="Divine",
        aura=4,
        summary=(
            "The Hohenburg, a convent two and a half thousand feet up in the "
            "northern Vosges on the Alsace side, founded by St Odile, who was born "
            "blind and given sight at her baptism by her uncle St Erhard; a rock "
            "opened to hide her from her father Duke Adalric, who afterwards gave "
            "her the castle. Small chapels, Odile's crypt and an ancient Merovingian "
            "cemetery stand on the summit. Below the convent the spring she struck "
            "with her cane cures the sick, above all diseases of the eye, and has a "
            "Divine aura of 4 (the convent's own is not given). She died in 720 and "
            "pilgrims have come ever since."
        ),
        **KNOWN_REGION,
    )
    _add(
        rhine,
        "thann_chapel",
        "Thann Chapel",
        inside=region,
        realm="Divine",
        aura=3,
        tethers="The rooted staff of Bishop Theobald's servant beneath the altar",
        summary="A chapel of 1161 in the southern Vosges about a dozen miles west of "
        "Mulhouse, built over the staff of the servant of Bishop Theobald of "
        "Gubbio, who had hidden his dead master's ring and thumb inside it; the "
        "staff rooted itself in the fir forest under three lights and could not "
        "be moved. The lord of the nearby Engelburg raised the chapel, a village "
        "grew about it, and the Engelburg peasants ceremonially burn three fir "
        "trees before it each summer. Its Divine aura is 3 and it draws pilgrims.",
        secrets="The Vosges once had a secretive fir spirit like the Black Forest's. "
        "Villages, monasteries and felling wore it down, and the planting of "
        "the holy staff extinguished it, which is why no continuous Vosges "
        "forest remains. If the staff were removed it might be the one artefact "
        "able to counter the spirit of the Black Forest.",
        **KNOWN_REGION,
    )
    _add(
        rhine,
        "sanctuary_of_hercules",
        "The Sanctuary of Hercules",
        inside=region,
        aura=3,
        summary=(
            "A hidden cave on the isolated western slopes of the Vosges where three "
            "spring-fed pools lie in a Magic aura of 3. The Gauls kept it as a shrine "
            "to Ogmios, god of strength, eloquence and poetry; the Romans recast him "
            "as Hercules and built a Greek-columned shrine. Grateful petitioners left "
            "altar stones in a ring about the pools, and they stand there still for "
            "whoever finds the place."
        ),
        **RUMOURED,
    )
    _add(
        rhine,
        "andresina",
        "Andresina",
        inside=region,
        aura=2,
        summary=(
            "An abandoned Roman city in Upper Lorraine, two dozen miles south-west "
            "of Toul, built round a great temple of Apollo and its sacred pool, fed "
            "by miles of piping; the emperors Caracalla and Constantine both visited. "
            "The temple ruins, a half-oval amphitheatre, a crumbling basilica with a "
            "mosaic floor, underground chambers and an old rampart remain, with a "
            "small village beside it. The Magic aura is 2 and would likely rise if "
            "the temple were restored; the book suggests it as a covenant site."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        rhine,
        "vosges",
        "The Vosges Mountains",
        inside=region,
        summary="The range on the west bank of the Upper Rhine facing the Black Forest, "
        "as high as it and fir-clad on the upper slopes, but not wholly forested: "
        "villages lie among the hills. The southern peaks are rounded granite, "
        "the northern hills red sandstone. Many springs, some of them hot, feed "
        "the tributaries of the Mosel, and the storks that arrive each spring "
        "are thought lucky. The mountains have no general aura; Mount Saint "
        "Odile, Thann Chapel and the Sanctuary of Hercules are its sites.",
        secrets="The fir spirit of the Vosges is extinct, put out by the holy staff at "
        "Thann.",
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "burg_trifels",
        "Burg Trifels",
        inside=region,
        summary=(
            "An eleventh-century Hohenstaufen fortress on the crag of the Sonnenberg "
            "at the edge of the Palatinate Forest, twenty miles west of Speyer, and "
            "Barbarossa's favourite castle; it has never been taken. Henry VI held "
            "Richard the Lionheart prisoner here in 1193 for a ransom of 150,000 "
            "marks. It has a large dungeon and one of the Empire's greatest "
            "treasuries. Its aura is not given."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "schwanenburg",
        "The Schwanenburg",
        inside=region,
        summary=(
            "The Swan Castle on its steep hill over Cleves on the Lower Rhine, named "
            "for Lohengrin, the Knight of the Swan, who came in a barge drawn by a "
            "swan to defeat Telramund for the widowed Duchess Elsa of Brabant, "
            "married her on condition she never ask his name, and left when she "
            "did, as Wolfram von Eschenbach tells in Parzival. The lords of Cleves "
            "bear a swan in their arms. Its aura is not given."
        ),
        **KNOWN_REGION,
    )
    _add(
        rhine,
        "hertogenwald",
        "The Hertogenwald",
        inside=region,
        summary=(
            "A forest south of Aachen in Lower Lorraine, and the book's example of "
            "a Hercynian fragment that dissolved: farmland and the strong Divine "
            "aura of Aachen drained its spirit away, and it is now a mundane wood "
            "with no aura at all."
        ),
        **KNOWN_REGION,
    )
    _add(
        rhine,
        "heiliger_sand",
        "Heiliger Sand",
        inside=region,
        summary=(
            "The vast and ancient Jewish cemetery just outside the west walls of "
            "Worms, elaborate in its stones, overgrown and deserted except at the "
            "newest plots, since the dead are left in peace. Its aura is not given."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        rhine,
        "fengheld_rheingasse",
        "Rheingasse",
        inside=region,
        summary=(
            "Fengheld's chapter house in the centre of Cologne, a city house in the "
            "Rheingasse near the market, where two Gentle-Gifted magi of the Apple "
            "Gild very ably arrange the covenant's supplies and its dealings with "
            "the mundane world. Its aura is not given."
        ),
        **KNOWN_TRIBUNAL,
    )


# -- chapter 6: the Black Forest and Swabia --


def _black_forest(rhine: Rhine) -> None:
    forest = rhine.places["black_forest"]
    _add(
        rhine,
        "durenmar_site",
        "The valley of Durenmar",
        inside=forest,
        aura=7,
        summary=paragraphs(
            "A steep-sided hidden valley some fifteen miles inside the northern "
            "Black Forest, about fifteen miles south of Hirsau monastery, with "
            "Baden to the north-west. A guard post lower down is enchanted to "
            "hide the three-mile track up to it, and the covenant's towers stand "
            "below the surrounding treeline. The clearing on the valley floor, "
            "split by a stream and unfortified, has a Magic aura of 7 and is "
            "protected by the strongest Aegis of the Hearth in the Order; the "
            "Cult of Mercury's temple stood here before Bonisagus came in 754. "
            "Caves of unknown extent run under the north cliffs, with wild "
            "rumours of enslaved gnomes mining gems.",
            "Covenfolk born in the aura all carry Warping, and their longevity "
            "is unexplained. A lone fir near the Great Library, the Black Fir, is "
            "tolerated for the Perdo vis of its cones; the great vine on the "
            "Tower of Bonisagus yields Intellego vis in its sap.",
        ),
        secrets="The Black Fir was planted over a century ago by the King of the Black "
        "Mountain at the edge of the Aegis after his direct attacks failed; when "
        "the magi found it gave vis they moved the Aegis boundary to take it in, "
        "breaching their own defence. It creeps about six inches a year toward "
        "the Tower of Bonisagus, and nobody alive remembers it being young. What "
        "happens when it reaches the tower or the vine is unknown but likely "
        "severe.",
        **KNOWN_ORDER,
    )
    _add(
        rhine,
        "dankmar_site",
        "The hollow of Dankmar",
        inside=forest,
        realm="Faerie",
        aura=5,
        summary=(
            "The dampest and darkest part of the Black Forest, about forty miles "
            "south-west of Durenmar and a few miles south of the Black Forest Road, "
            "where the fir stands so thick that noon is dusk, only fungi grow on the "
            "poisoned carpet of needles and only ravens call. The Faerie aura is 5. "
            "A circular palisade of split logs encloses wooden huts and four stone "
            "towers whose cellars join caves beneath, fir and yew lean over the "
            "walls, and every wooden thing glows with phosphorescent bracket fungi "
            "day and night. For at least a mile about it a version of The Shrouded "
            "Glen (level 40, Penetration 20) turns travellers away in nameless dread, "
            "and bockmen (Faerie, Might 20) patrol the surroundings by pact with "
            "Orphedra."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "black_forest_road",
        "The Black Forest Road",
        inside=forest,
        tethers="The Mercurian milestones that ward off the forest's faeries",
        summary=(
            "The only road across the forest, from Offenburg up the Kinzig valley to "
            "Rottweil, built in the first century under Vespasian by the Eighth "
            "Legion under Cornelius Clemens to shorten the way from Strassburg to "
            "Augsburg. Mercurian priests raised magical milestones along it that "
            "still ward off the forest's supernatural denizens, so wise travellers "
            "camp beside them. The paving is weathered and overgrown but it remains "
            "the one way to bring a cart through; the central stretch of nearly "
            "thirty miles between Gengenbach monastery and the village of "
            "Waldmoessingen on its ruined Roman fort has no human dwelling and takes "
            "two days, so one night in the forest cannot be avoided. Bockmen (Faerie, "
            "Might 20) lurk along it, and Dankmar lies a few miles to the south. Its "
            "own aura is not given; the forest's Faerie 3 lies over it."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "feldberg",
        "The Feldberg and the Hoellental",
        inside=forest,
        realm="Faerie",
        aura=3,
        tethers="The great dark fir on the summit, King Fir",
        levels=[
            Builder.level(
                "The Hoellental",
                3,
                "Faerie",
                notes=(
                    "Hell Valley, a haunted winding valley climbing from the centre "
                    "of the forest, the only way to the mountain; the lowest of the "
                    "regio's several levels, whose auras run from 3 to 8."
                ),
            ),
            Builder.level(
                "The Black Mountain",
                8,
                "Faerie",
                notes=(
                    "The bare summit with its one great dark fir, King Fir: no mortal "
                    "who sees it ever leaves the forest. Beneath lies a vast dungeon "
                    "where hundreds of enslaved humans who strayed too deep toil "
                    "without end."
                ),
            ),
        ],
        summary="The highest peak of the southern Black Forest, reached only through the "
        "Hoellental, and the seat of the King of the Black Mountain, King Fir "
        "(Faerie, Might 60; Malicious +5, Secretive +3, Vengeful +3), pictured as "
        "a huge black-cloaked man with a terrible face. He commands the weather, "
        "grants flaws such as depression, fear, lameness and loss of direction, "
        "possesses, shrouds and holds a regio of several levels with Faerie auras "
        "from 3 to 8; victory and virtue he grants very rarely. He is the dread "
        "and undisputed ruler of every dark faerie court in the forest, and his "
        "influence covers all of it. Monasteries inside the forest suffer his "
        "attacks: vanishing monks, blight, landslides and earthquakes.",
        secrets="His dominion cannot reach the Glade of the Seven Waterfalls or the Fane "
        "of the Founders; lacking the original spirit's nature, they are "
        "unknowable to him. He craves revenge on those who bound the old spirit "
        "and wants to be whole again, so he seeks Durenmar's destruction: were "
        "it to fall, the rite of the Fane would lapse and the bound spirit would "
        "be his to dominate and absorb. The raid of 1085 was his, and its "
        "captives never returned; the Black Fir at Durenmar is his centuries-long "
        "plan.",
        **RUMOURED,
    )
    _add(
        rhine,
        "glade_of_seven_waterfalls",
        "The Glade of the Seven Waterfalls",
        inside=forest,
        tethers="The Spirit of the Glade, the peaceful remnant of the forest's spirit",
        levels=[
            Builder.level(
                f"The {ordinal} waterfall",
                0,
                enter="Complete the Quest the Spirit of the Glade sets for this fall",
                notes=(
                    "A new level of understanding of the Forest, won by the Quest "
                    "that let the climber pass this waterfall (aura not given)."
                    + (
                        " The top level gives a complete and harmonious understanding."
                        if ordinal == "seventh"
                        else ""
                    )
                ),
            )
            for ordinal in (
                "first",
                "second",
                "third",
                "fourth",
                "fifth",
                "sixth",
                "seventh",
            )
        ],
        summary=(
            "At the exact centre of the Black Forest, in a place nobody has found "
            "or admitted finding, a stream falls through a precipitous valley over "
            "seven waterfalls, and the one way up is a narrow path beside the water "
            "through hazel and beech. The regio has seven levels, one for each fall, "
            "and the Spirit of the Glade (Magic, Might 80; Enigmatic +4, Wise +3), "
            "the peaceful female remnant of the forest's original genius locus, lets "
            "a climber past each fall only after a Quest; she guides, swears oaths, "
            "shrouds and grants clear thought. Each ascent brings a deeper "
            "understanding of the Forest and the top a complete one, at the price "
            "of escalating Sacrifices such as parts of one's Hermetic magic. The "
            "Hercynian lineage of Bonisagus held it the place the Mercurian priests "
            "and Bonisagus sought; some prophesy godlike power for a destined finder, "
            "others guess the spirit has faded and been replaced by a powerful maga "
            "in Final Twilight, perhaps the Founder Merinita. The bell of St Georgen "
            "was carried here, and the forest took its revenge on the monastery. The "
            "aura is not given."
        ),
        **RUMOURED,
    )
    _add(
        rhine,
        "fane_of_the_founders",
        "The Fane of the Founders",
        inside=forest,
        aura=6,
        tethers="The twelve-sided stone slab and the spirit bound in it",
        summary="A quiet glade not far from Durenmar, its whereabouts hidden by powerful "
        "magic, with a twelve-sided stone slab at its centre and a Magic aura of "
        "6. Here the Oath of the Founders was composed and sworn, and every seven "
        "years during the Rhine Tribunal twelve magi, one of each House, come "
        "secretly to renew the Founders' vows in a rite believed to preserve the "
        "Order; they leave with vis as their reward, and the place encourages "
        "clear and calm thought. Only the Primi and their chosen know it exists, "
        "though most Durenmar magi know of it, and all who have sought it have "
        "failed. It is older than the Order: many truces were made here, among "
        "them one between Germanic chiefs and a Roman general that fixed the "
        "Empire's northern limit. The rite was skipped only at the Tribunals of "
        "997, 1004 and 1011 and resumed in 1018 with an Ex Miscellanea magus in "
        "Diedne's place. Rumour says the attendees met Hermes himself, or a "
        "powerful faerie posing as him who extracted a terrible service from the "
        "Founders.",
        secrets="The Fane is an artefact into which the Cult of Mercury bound much of the "
        "Black Forest's original magical essence by a great ritual. It behaves as "
        "a spirit of Magic Might 60 with limited forest powers: it produces vis, "
        "shrouds, swears oaths and grants clear thought for a time. The rite "
        "must be renewed regularly or the spirit escapes the stone, which the "
        "King of the Black Mountain hopes for so that he may seize it.",
        **RUMOURED,
    )
    _add(
        rhine,
        "mummel_lake",
        "Mummel Lake",
        inside=forest,
        realm="Faerie",
        summary=(
            "An enchanted and isolated lake deep under the mountains near Seebach. "
            "A Nixe (Faerie, Might not given), a water-nymph, lives in it and now "
            "and then visits the nearby settlements to bewitch a young man with her "
            "beauty; she must return every night, and the jealous elemental spirits "
            "of the lake (realm and Might not given) kill any mortal who follows her "
            "home. Its aura is not given."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        rhine,
        "source_of_the_danube",
        "The Source of the Danube",
        inside=forest,
        realm="Faerie",
        aura=3,
        tethers="Danu, the river's spirit",
        levels=[
            Builder.level(
                "The true bottom",
                10,
                "Faerie",
                notes=(
                    "The top level of the regio, where the pool's real floor lies, "
                    "and a gateway into Arcadia that feeds the river. The levels "
                    "between are not given."
                ),
            ),
        ],
        summary=(
            "In the eastern Black Forest an enchanted spring runs from a crack in "
            "the rock into a small pool, deceptively deep, which is the source of "
            "the Danube. The Faerie aura is 3 about the pool and 5 within the water. "
            "Unlike the Rhine's, the river's spirit is a faerie: Danu (Faerie, Might "
            "not given), once a goddess of countless peoples before Rome, whose power "
            "fades elsewhere but is strong here. The pool seems bottomless because of "
            "the regio; at its top level, with Faerie aura 10, lies the true bottom "
            "and a gateway into Arcadia. Vast Aquam vis could be taken here, at the "
            "near-certain cost of Danu's anger."
        ),
        **KNOWN_LOCALLY,
    )
    jura = _add(
        rhine,
        "swabian_jura",
        "The Swabian Jura",
        inside=forest,
        summary=(
            "Harsh limestone hills between the valleys of the Danube and the Neckar, "
            "east of the Black Forest, whose defensible peaks the Hohenzollerns and "
            "other local lords have forted. They are riddled with stalactite grottos "
            "such as the Nebelhoehle, the Misty Cave. On the south side near "
            "Zweifalten monastery the Wimsener Hoehle swallows the river Ach, a "
            "Danube tributary, which runs underground for a couple of miles through "
            "a tunnel that can partly be navigated by boat. The aura is not given."
        ),
        **KNOWN_REGION,
    )
    _add(
        rhine,
        "blautopf",
        "The Blautopf",
        inside=jura,
        realm="Faerie",
        aura=2,
        summary=(
            "A large round pool of startling deep blue at the southern edge of the "
            "Swabian Jura beside Kloster Blaubeuren, the source of the little river "
            "Blau, with a Faerie aura of 2. It is the home of the Schoene Lau "
            "(Faerie, Might not given), a beautiful, reclusive, long-haired water "
            "maiden with webbed feet, banished here by her husband, a faerie king of "
            "the Black Sea, because she cannot laugh: the future holds no surprise "
            "for her. Those who come for wisdom, Blaubeuren's monks among them, bring "
            "a modest gift and she foretells their future; her predictions always "
            "come true and seldom bring the happiness hoped for. Whoever makes her "
            "laugh breaks the curse and earns her eternal gratitude."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        rhine,
        "the_limes",
        "The Limes",
        inside=forest,
        summary=(
            "The Roman frontier fortifications of the first century, whose ramparts, "
            "forts and temples lie in ruins along their whole route past Gmuend and "
            "through the Odenwald, the Swabian Forest and the Swabian Jura. The Cult "
            "of Mercury guided the legions in building it and its magically linked "
            "roads, and its building first split the Black Forest and its spirit "
            "from the Hercynian Forest. Its aura is not given."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "kaiserberge",
        "The Kaiserberge",
        inside=forest,
        summary=(
            "Three round wooded hills south of Gmuend in the Stauferland, each "
            "topped by a castle: the Hohenstaufen to the west, the lowest and "
            "grandest, ancestral seat of the imperial dynasty; the Hohenrechberg; and "
            "the Stuifen to the east, the highest. The Stauferland about them is the "
            "rolling country between the Swabian Forest and the Swabian Jura, named "
            "for the Hohenstaufens. The aura is not given."
        ),
        **KNOWN_REGION,
    )


# -- chapter 7: the Lowlands --


def _lowlands(rhine: Rhine) -> None:
    region = rhine.places["lowlands"]
    _add(
        rhine,
        "waddenzee_site",
        "Terschelling",
        inside=region,
        aura=3,
        summary=(
            "A deserted, weather-beaten island of the Frisian chain on the Wadden "
            "Sea, the shallow water the sandy islands enclose, shared by the pirate "
            "magi of Waddenzee and many thousands of seabirds whose noise in spring "
            "and summer has earned it a name for haunting, which the magi encourage; "
            "they have driven off every other settler. The Magic aura is 3 over the "
            "covenant building and a few hundred paces about it. A long, low "
            "Danish-style long-house sunk partly into the ground houses the "
            "covenfolk, four separate magus buildings join its walls by sunken "
            "covered walkways, and there is a harbour for the covenant's five ships."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "pirates_graveyards",
        "The Pirates' Graveyards",
        inside=region,
        summary="Dozens of graves marked with standing stones and boulders on a low "
        "ridge some fifty feet above the swamp in Drenthe, a couple of dozen "
        "miles up the river Ems from its estuary; they are the only stones in "
        "Friesland. The pirates of Frisia, Waddenzee's among them, bury their "
        "dead here, and the place is haunted. Lucas von Beck of Waddenzee takes "
        "vis and corpses from it for his necromancy. The aura is not given and "
        "its realm is uncertain.",
        secrets="The power here may be Infernal rather than Magic; Lucas has barely "
        "considered it.",
        **RUMOURED,
    )
    _add(
        rhine,
        "haithabu",
        "Haithabu",
        inside=region,
        summary=(
            "The old Viking trading city a few miles from the fishing town of "
            "Schleswig on the Schlei fjord, founded at the start of the ninth "
            "century where the land crossing between Baltic and North Sea is "
            "shortest. Only earth ramparts and burial mounds remain, and, the locals "
            "say, ghosts. The aura is not given."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        rhine,
        "ash_of_nortorf",
        "The Ash of Nortorf",
        inside=region,
        realm="Infernal",
        tethers="The ash seedling itself",
        summary=(
            "A small ash seedling in the churchyard of the little town of Nortorf in "
            "Holstein, where the roads to Schleswig, Lübeck and Hamburg meet. Every "
            "New Year's Night a white rider on a white horse cuts it down while a "
            "black rider on a black horse tries and fails to stop him. The prophecy "
            "says that one day the black rider will win, the shoot will grow into a "
            "tree, and once it is big enough to tether a horse under, a king will come with a "
            "great army; while his horse stands under the tree he cannot be beaten "
            "and gains fell powers. The tree's spirit (Infernal, Might 15, potentially "
            "60; Ambitious +2) grants victory and the virtues of entrancement, "
            "inspiration and toughness; the white horseman is Divine and the black "
            "an Infernal agent. Agents of the black rider may tell magi of the ash as "
            "a future vis source and not of the prophecy, hoping they will guard it "
            "on New Year's Night: if the Divine rider is driven off or killed he "
            "never returns. The aura is not given."
        ),
        **RUMOURED,
    )
    _add(
        rhine,
        "giants_grave",
        "The Giant's Grave",
        inside=region,
        summary=(
            "A rectangular bed of stones forty yards by ten in the Everstorf Forest "
            "north of Schwerin in Mecklenburg, near Naschendorf. The farmers of the "
            "village found a cattle-stealing, crop-trampling giant asleep, rolled him "
            "into a huge grave and buried him; his wife dragged stone blocks in her "
            "apron to cover it so he could not escape, and he suffocated while she "
            "was never seen again. The aura is not given."
        ),
        **KNOWN_LOCALLY,
    )
    teutoburger = _add(
        rhine,
        "teutoburger_forest",
        "The Teutoburger Forest",
        inside=region,
        tethers="The ring of ancient trees about the great clearing",
        levels=[
            Builder.level(
                "The legionaries' camp",
                0,
                notes=(
                    "The top level of the regio (its levels are not numbered and "
                    "their auras not given): a fortified Roman camp in the clearing "
                    "where the surviving legionaries of Hermann's battle still live, "
                    "kept from aging and from leaving, free to hunt and forage, "
                    "heavily Warped and reverent of the trees."
                ),
            ),
        ],
        summary=(
            "Forested hills in Westphalia where Hermann's Germans destroyed the Roman "
            "legions in the first century and Charlemagne fought in the late eighth, "
            "the beachhead of every conqueror and so a wilderness with strong "
            "guardians, one of the last on the northern lowlands. At its heart a "
            "great clearing is ringed by ancient trees of different kinds that "
            "together are the forest's spirit (Magic, Might 50; Patient +3, "
            "Unforgiving +1), which grants simple-mindedness and victory, shrouds, "
            "holds a regio and keeps the legionaries in stasis. The surviving Romans "
            "withdrew into the forest after the battle and vanished; they are "
            "trapped in the regio's top level and would make loyal, well-trained "
            "grogs for anyone who bargained their release with the trees, unless a "
            "renegade magus or hedge wizard hidden in the forest already uses them as "
            "his turb. The Externsteine stand on its south-eastern edge. The aura is "
            "not given."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "externsteine",
        "The Externsteine",
        inside=teutoburger,
        realm="Divine",
        aura=4,
        summary=(
            "Thirteen jumbled sandstone rocks, some over a hundred feet tall, in a "
            "large clearing on the south-eastern edge of the Teutoburger Forest near "
            "Paderborn, with a Divine aura of 4. Once a pagan site, its caves were "
            "consecrated as a chapel in 1115; a carving of the Descent from the Cross "
            "stands at the foot of one rock, and inside another a bare upper chapel "
            "has a window that catches the sunrise of the summer solstice. It is "
            "enigmatically peaceful and home to a handful of ascetic hermits."
        ),
        **KNOWN_REGION,
    )
    _add(
        rhine,
        "teufelsmoor",
        "The Teufelsmoor",
        inside=region,
        summary=(
            "A vast swampy waste of dark peat for miles north-east of Bremen, bare "
            "of grass and trees, always misted and foul-smelling; strange shapes and "
            "lights move in it at night. The locals think it cursed and keep away, "
            "though peasants cut peat at its edge for fuel. The book suggests it as "
            "an unpleasant but workable covenant site. The aura is not given."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        rhine,
        "luneburg_heath",
        "The Lüneburg Heath",
        inside=region,
        summary=(
            "A sprawling open heath south of Lüneburg with small woods, a few "
            "villagers and shepherds tending Heidschnucken, the goat-like sheep "
            "descended from Corsican mouflon brought here about two hundred years "
            "ago. The aura is not given."
        ),
        **KNOWN_REGION,
    )
    _add(
        rhine,
        "teufelskuche",
        "The Teufelsküche",
        inside=region,
        tethers="The ancient altar of Woden at the circle's centre",
        summary=(
            "A forgotten circle of round stones about an ancient altar deep in the "
            "Haldensleben Forest north-west of Magdeburg, where Woden was worshipped: "
            "tall red-bearded priests in long white cloaks came in the hour before "
            "dawn with men in skins and other dark shapes, slaughtered a sacrifice "
            "and burned its vitals to greet the day. The missionaries who purged the "
            "cult named it the Devil's Kitchen; whether any priest of Woden survives "
            "is the storyguide's choice. The Wild Hunt, the troupe of storm and "
            "winter faeries led by the Wild Huntsman (Faerie, Might 50) with its "
            "Horsemen (Faerie, Might 20 each) and Hounds (Faerie, Might 10 each), "
            "rises from here on stormy winter nights, so winter is a bad time to "
            "visit. The aura is not given."
        ),
        **RUMOURED,
    )
    _add(
        rhine,
        "northern_swamps",
        "The northern swamps",
        inside=region,
        summary=(
            "The bogs and marshes of northern Germany generally, the haunt of the "
            "Boglin (Magic, Might 25; Greedy +5, Reclusive +2, Guileful +1): a "
            "carapaced sac of a body the size of three men with eight slimy "
            "dark-brown tentacles twelve feet long and a toothy maw, lying under "
            "murky water and betrayed only by a foul stench and a faint murmuring. "
            "It chokes prey with a cloud of stinking gas, paralyses it with venomous "
            "barbs, drags it to the maw in three rounds and regrows a lost tentacle "
            "each season it hibernates; it is blind, gluttonous and a cunning hunter. "
            "Its tentacles hold a pawn of Animal vis each and its brain six of Perdo. "
            "The aura is not given."
        ),
        **RUMOURED,
    )
    _add(
        rhine,
        "munsterland",
        "The Münsterland",
        inside=region,
        summary=(
            "The flat, highly fertile plain of Westphalia round Münster, the "
            "prosperous market city founded as a monastery in 805 to convert the "
            "Saxons. The aura is not given."
        ),
        **KNOWN_REGION,
    )
    _add(
        rhine,
        "heorot_site",
        "Heorot on Zealand",
        summary=(
            "The site of the hall of Hrothgar, the legendary king of the Danes, on "
            "the island of Zealand in the kingdom of Denmark, where Beowulf fought "
            "Grendel; Rügen lies not far across the water. Zealand is by tradition "
            "Novgorod Tribunal territory, but no covenant of the Order has lasted in "
            "Norse lands long enough to attend a Tribunal, so the claim is a grey "
            "area the new covenant of Heorot means to exploit. The kin of Grendel "
            "(trolls; realm and Might not given) still haunt the island's bogs and "
            "have killed fourteen of the covenant's grogs and taken its leader's left "
            "arm. The aura is not given."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "fengheld_cherbourg",
        "Fengheld House",
        summary=(
            "Fengheld's most remote chapter house, a single fortified townhouse in "
            "the city of Cherbourg in Normandy, outside the Rhine Tribunal "
            "altogether, owned by Sir Jozef of Poznan, a crusader of Polish birth. "
            "It runs a small trading business with England and France. Its aura is "
            "not given."
        ),
        **KNOWN_TRIBUNAL,
    )


# -- chapter 8: the Harz, Thuringia, Franconia and Bavaria --


def _central(rhine: Rhine) -> None:
    region = rhine.places["central"]
    harz = _add(
        rhine,
        "harz",
        "The Harz Mountains",
        inside=region,
        summary=(
            "Germany's northernmost range, fifty miles of high granite hills on the "
            "edge of Saxony, a desolate wilderness ringed by the civilised Saxon "
            "towns. Wind off the northern plain, rain and fog prevail, and low cloud "
            "hides the peaks and cuts them off from the lowlands; the lower slopes "
            "are gloomy forest with strange hidden rocks, whispering streams, lakes "
            "and caves. A small number of secretive dwarf-like folk live here: "
            "Gübich (Faerie, Might not given), morose, dwelling in mossy caves, who "
            "calls up rain and storms, leads travellers astray, claims to be king of "
            "the dwarves and may be the dwarf king of the Rumaquelle tale; and "
            "Kröpel (Faerie, Might not given), good-natured, who roams widely hidden "
            "under his hat of fog. The witches of the Harz gather on its peaks. The "
            "range has no aura as a whole; Fengheld lies in its eastern hills."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "fengheld_site",
        "The hill of Fengheld",
        inside=harz,
        aura=5,
        summary=(
            "A remote hilltop in the eastern Harz, "
            "on the border country of Saxony and Thuringia, with a Magic aura of 5 "
            "on the summit. Vineyards and orchards cover the south slope, grain and "
            "root crops the valley floor, and sheep and goats the rest of the hill, "
            "feeding well over two hundred people; an immense curtain wall rings a "
            "summit complex of about twenty buildings, a tower for each resident "
            "magus, an elaborate guest house, a huge meeting hall and quarters for "
            "covenfolk and grogs, with outlying hamlets below. Weather magic keeps "
            "the sun, the rain and a strategic fog over it, and the local nobility "
            "has somehow never noticed the scale of what grows here."
        ),
        **KNOWN_ORDER,
    )
    _add(
        rhine,
        "rammelsberg",
        "The Rammelsberg silver mines",
        inside=harz,
        realm="Faerie",
        summary=(
            "Germany's largest silver mines, by Goslar on the northern edge of the "
            "Harz and a prized imperial asset, which are slowly flooding and failing "
            "because spiteful gnomes (Faerie, Might not given) have diverted an "
            "underground river into them. Whoever drove off the gnomes and drained "
            "the mines would be richly rewarded by the emperor. The aura is not given."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "rumaquelle",
        "The Rumaquelle",
        inside=harz,
        summary=(
            "A hidden spring of distinctive green water on the forested southern "
            "slopes of the Harz near the Römerstein castle. Romer, a young giant of "
            "the Römerstein, secretly married Ruma, daughter of the dwarf king, his "
            "father's sworn enemy; when a son was born the king found them out, "
            "cursed them, killed the child and shut Ruma in a cave. Her mother having "
            "been a mermaid, she turned herself into a stream and searched the "
            "underground passages for years until she surfaced beyond the dwarves' "
            "realm, and the spring is her outlet. Romer (giant; realm and Might not "
            "given) and Ruma (water spirit; realm and Might not given) are said still "
            "to meet here, and the spring may be a door to the dwarf king's realm. "
            "The aura is not given."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        rhine,
        "brocken",
        "The Brocken",
        inside=harz,
        realm="Faerie",
        aura=4,
        tethers="The Witches' Altar and Walpurga's yearly rite",
        summary=(
            "The highest peak of the Harz at 3,750 feet and one of the most potent "
            "supernatural sites in Germany. Its bare summit is crowned by a heap of "
            "huge granite blocks, the Witches' Altar, with a Faerie aura of 4; the "
            "lower slopes have 2, and both double on Walpurgis Night. Every 30 April "
            "the goddess Walpurga (Faerie, Seelie, Might 50), lady of summer and "
            "growth and Queen of the Holzfrauen, wholly kind to mankind, summons the "
            "summer's spirits to overcome winter's, and the Wild Hunt loses its "
            "battle with her airy elementals about the Altar; witches from miles "
            "around climb the slopes that night trailed by dozens of villagers who "
            "keep the old ways, light fires and sing to forgotten gods, and only the "
            "strongest approach the Altar. For the nine days before, Walpurga "
            "wanders the Harz as the humble wood-wife Frau Holle on a rickety wagon, "
            "hunted by the Wild Hunt, asking villagers for help and checking their "
            "housekeeping, and rewards those who shelter her with gold; at the summit "
            "she sheds her rags and stands in a white cloak and crown, shoes of fire, "
            "with a spindle and a three-cornered mirror that shows the future. The "
            "Brocken is a witches' meeting place all year and magi know it as a good "
            "place to find an apprentice. The Magic Fountain nearby gives visions to "
            "those who drink, and the Sorcerer's Flower, a pale violet anemone of the "
            "slopes, is reputed vis."
        ),
        **KNOWN_TRIBUNAL,
    )
    hexentanzplatz = _add(
        rhine,
        "hexentanzplatz",
        "The Hexentanzplatz",
        inside=harz,
        realm="Faerie",
        aura=2,
        summary=(
            "The Witches' Dancing Ground, a rocky crag in the north-eastern Harz a "
            "dozen miles east of the Brocken, climbed by a flight of ancient steps to "
            "a weathered summit with a Faerie aura of 2. The witches of the Harz meet "
            "here every April to hold their council before going on to the Brocken. "
            "The Rosstrappe faces it across a ravine."
        ),
        **KNOWN_REGION,
    )
    _add(
        rhine,
        "rosstrappe",
        "The Rosstrappe",
        inside=hexentanzplatz,
        summary=(
            "A great rock on the lower slope directly across the ravine from the "
            "Hexentanzplatz, bearing a huge hoofprint. Princess Brunhilde, fleeing "
            "the lustful knight Bodo, spurred her horse across the chasm to the "
            "Hexentanzplatz; a witch nearby turned Bodo into a dog and he fell into "
            "the gorge. Some say a hound (realm and Might not given) still lives by "
            "the stream at the bottom, guarding Brunhilde's crown, which fell from "
            "her head in the leap. The aura is not given."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        rhine,
        "bears_cave",
        "The Bears' Cave",
        inside=harz,
        aura=3,
        summary="A hidden primeval cave on the slopes of the northern Harz with a Magic "
        "aura of 3, its floor strewn with the arranged bones, teeth and scraps of "
        "hide of bears far larger and fiercer than any known today, which can be "
        "harvested for Animal vis (amount not given).",
        secrets="The cave is the secret retreat and private vis source of an ancient "
        "line of bear-heartbeast Bjornaer descending from the Founder herself, "
        "whose two living members are Archmage Urgen of Crintera and his filia "
        "Odorpes of Fengheld's Lusatia chapter. Each visits now and then and "
        "would be furious to find anyone else harvesting their vis.",
        **RUMOURED,
    )
    kyffhauser = _add(
        rhine,
        "kyffhauser",
        "The Kyffhäuser Mountains",
        inside=region,
        summary=(
            "A double line of hills on Thuringia's northern border with Saxony, said "
            "in legend to hold the sleeping bodies of famous kings, above all "
            "Frederick Barbarossa. Fengheld's chapter Turris Acontiarum stands among "
            "them and the Apple of the Kyffhäuser at the foot of their tallest peak. "
            "The aura is not given."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "apple_of_the_kyffhauser",
        "The Apple of the Kyffhäuser",
        inside=kyffhauser,
        tethers="The withered apple tree",
        summary=(
            "A withered apple tree at the foot of the tallest peak of the "
            "Kyffhäuser, guarded by men-at-arms. Whichever prince hangs his shield on "
            "it becomes lord of all the West; whoever fails must guard the tree for "
            "ever as one of its warriors. Three successful challengers, Clovis, "
            "Charlemagne and Barbarossa, each cut it down to stop imitators, but it "
            "always regrows in full leaf and then withers as their fortunes fade; it "
            "last bore fruit in Barbarossa's reign. When it next comes into leaf a "
            "terrible battle begins, and when it fruits the king hangs his shield, "
            "all men rally to it and the wicked are rooted out. The tree's spirit "
            "(Magic, Might 70; Regal +4, Peaceful -1) grants victory to whoever hangs "
            "a shield, keeps its men-at-arms unaging, heals wounds and possesses "
            "anyone who fails against the guards (their number and Might not given). "
            "The Mongol Khan may one day hear of it and come to hang his shield. The "
            "aura is not given."
        ),
        **RUMOURED,
    )
    _add(
        rhine,
        "fengheld_kyffhauser",
        "Turris Acontiarum",
        inside=kyffhauser,
        summary=(
            "Fengheld's chapter house in the Kyffhäuser Mountains on the border of "
            "Saxony and Thuringia: a solitary tower where one magus studies the stars "
            "with a single mute companion. Its aura is not given."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "wartburg",
        "The Wartburg",
        inside=region,
        summary=(
            "The ancestral castle of the landgraves of Thuringia near Eisenach, "
            "founded in 1067 by Count Louis I, whose walls have never been breached. "
            "Since Landgrave Hermann I it has been a famous court of literature and "
            "music in the French courtly fashion, holding lavish festivals that draw "
            "minnesänger and noble guests from afar; at the Sängerkrieg of 1204 "
            "Walther von der Vogelweide defeated Wolfram von Eschenbach, Henry von "
            "Ofterdingen and every other rival. The aura is not given."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "rothaargebirge",
        "The Rothaargebirge",
        inside=region,
        summary=(
            "The Red Hair Mountains, heavily wooded highlands of western Thuringia, "
            "named either for the autumn colour of their trees or for the strange "
            "and fierce folk who live there, whom the book does not describe. The "
            "aura is not given."
        ),
        **KNOWN_REGION,
    )
    _add(
        rhine,
        "sauerland",
        "The Sauerland",
        inside=region,
        summary=(
            "Rugged, inhospitable uplands south of Paderborn bordering Thuringia. "
            "The Dragon of the Sauerland (realm and Might not given) lives here, and "
            "the second Quest of the Path of Energy is to conquer it and eat its "
            "heart. The aura is not given."
        ),
        **KNOWN_REGION,
    )
    _add(
        rhine,
        "goldene_aue",
        "The Goldene Aue",
        inside=region,
        summary=(
            "The Golden Meadow, a fertile plain of eastern Thuringia north of the "
            "river Saale. The aura is not given."
        ),
        **KNOWN_REGION,
    )
    _add(
        rhine,
        "riesenstein",
        "The Riesenstein",
        inside=region,
        realm="Infernal",
        summary=(
            "The Giant's Stone, standing alone in a field near Züschen a little north "
            "of Fritzlar. The Devil, watching from the mountaintop as the pious "
            "villagers of Neueburg built a church and refused his temptations, hurled "
            "a great stone at them; it caught on his sleeve and fell short, and he "
            "wept tears of blood on it that left three red stains. Every All Hallows' "
            "Eve the tears run from the stains again, and they are Ignem vis (amount "
            "not given). The aura is not given."
        ),
        **KNOWN_LOCALLY,
    )
    thuringian = _add(
        rhine,
        "thuringian_forest",
        "The Thuringian Forest",
        inside=region,
        summary=(
            "One of the largest forests left in Germany, nearly a hundred miles long "
            "along the border of Thuringia and Franconia and about thirty wide, over "
            "low mountains whose rounded summits form a continuous ridge. Pine and "
            "fir cover it, and its deep valleys hide lovely glens and clearings. It is "
            "the traditional divide between north and south Germany: dialect, custom "
            "and dress change sharply from one side to the other. Kleon of Criamon "
            "walked the Path of Warping here and is probably lost to Twilight. The "
            "aura is not given."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "feengrotten",
        "The Feengrotten",
        inside=thuringian,
        aura=1,
        summary=(
            "The Faerie Grottoes at the eastern edge of the Thuringian Forest, with a "
            "Magic aura of 1: hidden caves reached by slippery descents past "
            "underground streams and stalactite chambers, opening into central "
            "crystal caverns where coloured lights dance over the walls. The passages "
            "seem to shift, and scrambling through them coats the explorer in "
            "glittering dust. Whoever is genuinely lost for days finds on emerging "
            "that the dust is Imaginem vis, more for more days lost; whoever tries to "
            "get lost on purpose finds only dust."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        rhine,
        "donar_oak",
        "The Donar Oak",
        inside=thuringian,
        realm="Divine",
        tethers="The regrown stump of Thunor's oak with its cross",
        summary=(
            "The remains of the great oak sacred to Thunor in a hidden glade at "
            "Geismar in the Thuringian wilderness near Fritzlar, once the focus of "
            "the pagan power of the whole Hercynian Forest. In the eighth century "
            "Boniface made a shallow cut in its trunk before scornful heathens; a "
            "great wind shattered it into four pieces, the heathens converted, he "
            "built an oratory to St Peter from the wood, and the old forest's power "
            "broke into the smaller forests of today. The stump bears a simple cross "
            "at its centre and has regrown in several offshoots, which stand for the "
            "Hercynian Forest's rebirth as many woods. The glade is utterly serene "
            "and every wild beast turns docile in it; some believe it a gate to Eden. "
            "Its spirit (Divine, Might 40; Peaceful +5, Wild -3) heals and rarely "
            "grants virtues. The acorns are Creo vis (amount not given): an animal "
            "that eats one may be tamed, and a forest in which one is planted and "
            "grown to maturity may be tamed. The glade's location is legendary and "
            "its aura not given."
        ),
        **RUMOURED,
    )
    _add(
        rhine,
        "taunus",
        "The Taunus",
        inside=region,
        summary=(
            "A forested ridge north of Frankfurt between the Main and the Lahn; the "
            "book says nothing more of it. The aura is not given."
        ),
        **KNOWN_REGION,
    )
    _add(
        rhine,
        "vogelsberg_and_rhon",
        "The Vogelsberg and the Rhön",
        inside=region,
        summary=(
            "The two ranges flanking Fulda's long valley: the Vogelsberg to the west, "
            "a bright and airy wooded region about the conical peak of the Taufstein, "
            "and the Rhön to the east, an impenetrable and secretive wilderness of "
            "which the book says nothing further. The aura is not given."
        ),
        **KNOWN_REGION,
    )
    _add(
        rhine,
        "odenwald",
        "The Odenwald",
        inside=region,
        realm="Faerie",
        summary=(
            "A forest of Franconia on the right bank of the Rhine south of Frankfurt, "
            "fifty miles long, which blooms earliest and most spectacularly of all "
            "German forests: its carpet of lilies and the blossom of its many fruit "
            "trees announce spring to the whole land. The book proposes it as the "
            "seat of the Court of the Alder Prince, with the Willow Maiden's court in "
            "the Swabian Forest nearby. The old Roman military road, the Strata "
            "Montana, runs north to south through it and is now the busy Bergstrasse "
            "to Frankfurt; bandits lurk on the swampy, deserted east bank of the Rhine "
            "along the forest's western edge, and fortified way-stations are being "
            "built along the road against them. The aura is not given."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "stromberg",
        "The Stromberg",
        inside=region,
        summary=(
            "Gentle fertile hills south of Wimpfen between the Odenwald and the Black "
            "Forest where grapes have been grown for centuries. The aura is not given."
        ),
        **KNOWN_REGION,
    )
    _add(
        rhine,
        "linden_of_neustadt",
        "The Linden of Neustadt",
        inside=region,
        tethers="The great lime tree in the town",
        summary="The great lime tree of Neustadt an der grossen Linden in Franconia, "
        "whose spirit (Magic, Might 30; Protective +6), uniquely among forest "
        "spirits, has adopted the people of the town as the inhabitants of its "
        "realm; it grants victory, berserk fury and toughness to the town's "
        "defenders. Having a town for its heart has weakened the spirit, but the "
        "townsfolk have become very reluctant to clear or exploit the woods. "
        "During a siege the tree's wide branches were ruined and were afterwards "
        "propped on stone columns and monuments carved with the arms of the "
        "princes and nobles who fought there. The prophecy says that when the "
        "tree dies the town loses its freedom; though an important trading post, "
        "Neustadt has resisted growth and stays a quiet backwater. A magpie has "
        "nested in the Linden and is slowly killing it, and every attempt to "
        "drive it off has failed. The aura is not given.",
        secrets="The magpie is a Bjornaer magus in heartbeast form. What has he foreseen "
        "that makes him destroy the tree?",
        **KNOWN_REGION,
    )
    _add(
        rhine,
        "drudenbaum",
        "The Harberg and the Drudenbaum",
        inside=region,
        tethers="Whichever tree of the Harberg Forest the spirit possesses",
        summary="The Harberg mountain and its forest overlook Nuremberg, and legend puts "
        "on its top a tree called the Drudenbaum, so named because wizards meet "
        "beneath it. Its glossy leaves shed golden drops now and then, milk oozes "
        "from its roots, a dragon guards a treasure under it, and a great black "
        "bird perched in its crown claps its wings to raise a storm whenever "
        "someone tries to take the treasure; whoever drinks a cup of the golden "
        "liquid becomes a sorcerer. The golden drops are Creo vis and the milk "
        "Vim vis (amounts not given). The spirit (Magic, Might 30; Mysterious +3) "
        "grants magic sensitivity and second sight and possesses. Magi, hedge "
        "wizards and stranger beasts all hunt the tree. The aura is not given.",
        secrets="The dragon and the treasure are myth; the rest is true. The Drudenbaum "
        "is no real species: when the spirit possesses any tree of its domain, "
        "that tree takes on the Drudenbaum's look and vis for a time, and the "
        "black bird settling in its topmost branches marks the possession, so the "
        "tree keeps moving about the Harberg Forest.",
        **RUMOURED,
    )
    _add(
        rhine,
        "fichtelgebirge",
        "The Luisenburg and the Fichtelgebirge",
        inside=region,
        summary=(
            "East of Bamberg the Luisenburg is a region of countless huge, bizarrely "
            "weathered granite blocks scattered at random for miles; beyond it rise "
            "the Fichtelgebirge, the Spruce Mountains, a forbidding empty land of "
            "rock-strewn hills, moorland and forest. The wood-spirit Katzenveit "
            "(Faerie, Might not given) is named here. The aura is not given."
        ),
        **KNOWN_REGION,
    )
    _add(
        rhine,
        "danube",
        "The Danube",
        inside=region,
        summary=(
            "Already a great river where it crosses Bavaria, two hundred miles from "
            "its source in the Black Forest. Only the smaller, thinly peopled part of "
            "Bavaria north of the river, never Roman, belongs to the Rhine Tribunal; "
            "the Danube cities, chiefly Regensburg, and all the land south of the "
            "river are claimed by the Greater Alps Tribunal. The aura is not given."
        ),
        **KNOWN_TRIBUNAL,
    )


# -- chapter 9: the Eastern Marches --


def _east(rhine: Rhine) -> None:
    region = rhine.places["east"]
    rugen = _add(
        rhine,
        "rugen",
        "Rügen",
        inside=region,
        summary=(
            "Germany's largest island, about twenty miles across in the Baltic: "
            "mostly low grassland and heath with long beaches and marshy inlets, the "
            "Jasmund and Mönchgut peninsulas hillier and partly wooded, Wittow to the "
            "north windswept. The Stubnitz Forest on Jasmund, the largest wood, ends "
            "at the chalk cliffs of the Stubbenkammer and hides Crintera. Hedinsey, a "
            "narrow ten-mile island to the west, is deserted heath named for a "
            "Norwegian king who fought a battle there for his bride. Bergen, founded "
            "by the Danes, is the only town; farmsteads lie in the west, fishing "
            "hamlets in the east, and there is no real port; monks have only just "
            "begun farming Mönchgut. The islanders are mostly Slavic, Christianity is "
            "new and brought by the Danish king, and the Danes have requisitioned "
            "every horse. In the wild places the Forest Brothers Rugevit, Porevit "
            "and Porenitz, gods of rowan, beech and larch (Faerie, Might not given), "
            "are still worshipped by their few remaining priests, the volkhvy, who "
            "are welcome in Stubnitz and bury their dead at the Ziegensteine. A "
            "church is planned at Sagard, five miles from Crintera. The aura is not "
            "given."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "crintera_site",
        "The Stubnitz regio",
        inside=rugen,
        tethers="The Animal Powers who ruled the forest before the Bjornaer came",
        levels=[
            Builder.level(
                "The first level",
                1,
                enter=(
                    "A Corpus effect at each boundary draws the crosser's heartbeast "
                    "forward; here it gives a Personality Trait of the beast. Parma "
                    "usually resists, but resisting is thought rude; Bjornaer shrug "
                    "the change off with a Heartbeast roll"
                ),
                notes=(
                    "Six roundhouses, the homes of the six clans, and the covenfolk's "
                    "magically hidden hut clusters, which spill onto the mundane "
                    "forest too."
                ),
            ),
            Builder.level(
                "The second level",
                3,
                enter="The second boundary brings a minor physical change toward the beast",
                notes="The clans' six barracks and the training ground.",
            ),
            Builder.level(
                "The third level",
                5,
                enter="The third boundary brings another minor physical change",
                notes=(
                    "Six roundhouses; visiting Bjornaer build their temporary sancta "
                    "here and may stay for years as guests."
                ),
            ),
            Builder.level(
                "The fourth level",
                8,
                enter=(
                    "The fourth boundary brings the last change; one who has crossed "
                    "all four is visibly a quarter to a third animal"
                ),
                notes=secrets(
                    "The sancta of the six Elders of House Bjornaer, in six "
                    "roundhouses.",
                    "The fetishes of the Animal Powers stand here: a wooden squirrel "
                    "on a stump, a stone otter in cattails, a woven-rush snake in a "
                    "hollow of a boulder, a clay wolf with teeth of shell, stone birds "
                    "in willow saplings ringed with feathered thongs, every animal "
                    "represented and only a few visible from any one point. They are "
                    "truly ancient and said to hold primordial nature spirits; "
                    "touching one's own gives a deep sense of connection, and those "
                    "who resisted the regio's changes, or approach another's fetish, "
                    "feel compelled not to touch. Covenfolk leave offerings at the "
                    "fetish of their heartbeast.",
                ),
            ),
        ],
        summary="Deep in the Stubnitz Forest on the Jasmund peninsula of Rügen, five "
        "miles from Sagard, a Magic regio of four levels with auras of 1, 3, 5 "
        "and 8 holds Crintera, the domus magna of House Bjornaer; the mundane "
        "level looks like virgin forest and its aura is not given. The forest is "
        "strongly aligned to the Animal Powers, the entities who ruled here "
        "before the Bjornaer came, and religion of any kind is banned inside the "
        "regio in their honour. One route, the Watching Path, leads through "
        "Stubnitz; its start is marked by two mossy, crumbling stones in a glade "
        "near the forest's edge, known to Redcaps and Bjornaer, and every visitor "
        "is watched by covenfolk and animal allies. Every visitor, magus or "
        "mundane, should be given a heartbeast that fits his character before he "
        "crosses the boundaries. Locals shun the forest with tales of animal "
        "attacks, shadow-monsters and witches, which the covenant encourages.",
        secrets="The pristine look of Stubnitz is a deception; the forest is full of "
        "hidden covenfolk settlements.",
        **KNOWN_ORDER,
    )
    _add(
        rhine,
        "arkona",
        "Arkona",
        inside=rugen,
        realm="Faerie",
        aura=2,
        tethers="Centuries of worship of Svantovit, now fading",
        summary="The ruined Slavic fortress-temple on the cliffs of Kap Arkona, the "
        "northernmost point of Rügen on the Wittow peninsula, once among the "
        "holiest pagan sites of the Baltic and dedicated to the four-faced sun "
        "and war god Svantovit (Faerie, Might not given), who opposes the Queen "
        "of Winter (realm and Might not given). Bishop Absolon of Roskilde "
        "destroyed it in 1169, and a Faerie aura of 2 remains of centuries of "
        "worship. Each early spring Falke, Prima of Bjornaer, and the magi of "
        "Crintera cast the ritual that thaws the Baltic here, Appease the Queen "
        "of Winter, with a bonus of 10 to the Casting Total from the god's "
        "presence; she learned it with help from the volkhvy of Arkona and a lab "
        "text at Crintera. Two priests of Svantovit remain, a very old man "
        "trying to pass on all he knows and his grandson, who has seen no power "
        "and follows only from family duty, scraping a living on Wittow. A white "
        "horse, of which the Danes have left none on the island, is needed for "
        "the Great Ritual to the god; whoever brought one might rekindle the old "
        "priest's link to Svantovit and make a zealous pagan messiah of the "
        "grandson.",
        secrets="The two priests have laboriously moved the surviving upper half of "
        "Svantovit's statue from Arkona into a well-hidden shrine: four faces "
        "looking four ways, a bull's horn in its right hand and the god's huge "
        "sword laid before it; looters took the jewelled saddle and bridle.",
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "konigstuhl",
        "The Königstuhl",
        inside=rugen,
        summary=(
            "The King's Seat, a chalk cliff rising over 380 feet from the sea beside "
            "the Stubbenkammer cliffs on the north-east shore of Jasmund. Whoever "
            "climbs it from the sea becomes king of Rügen and sits on the stone "
            "throne at the top. In 1168 Valdemar I secretly made the climb before "
            "taking the island, was seen at the top by islanders and acknowledged as "
            "rightful ruler, which is said to be why the conquest went easily; "
            "whether Valdemar II has climbed it is not known, and islanders who want "
            "the Danes gone have tried and failed, as did the Horse Elder of Crintera "
            "before Istvan Padas, who fell to his death halfway up. Whether the seat "
            "confers a Divine right or a pagan or faerie power is the storyguide's "
            "choice; cheating with magic is certain to fail. The aura is not given."
        ),
        **KNOWN_REGION,
    )
    _add(
        rhine,
        "hertha_lake",
        "Hertha Lake",
        inside=rugen,
        realm="Faerie",
        tethers="The goddess Hertha's yearly bathing",
        summary=(
            "A small dark lake, partly covered in lilies, hidden in the Stubnitz "
            "Forest a short walk from Crintera. Every May Eve the goddess Hertha "
            "(Faerie, Might not given but powerful) bathes here and afterwards "
            "drowns one of the mortals gathered to watch; her priestess marks the "
            "victim, who alone of those present does not know his fate, and the "
            "ghosts of earlier victims (realm and Might not given) gather on the "
            "shore. In return she grants good harvests to farmers who sprinkle the "
            "corners of their fields with water taken from the lake after she has "
            "bathed. Zora, the darkly beautiful faerie-blooded priestess who leads "
            "her small priesthood, is the lover of Istvan Padas of Crintera and "
            "backs his Wilderist cause; Crintera protects the priestesses from "
            "discovery, and Zora gives the covenant Creo vis each year from the "
            "goddess's presence and never chooses her victim from its covenfolk. The "
            "aura is not given."
        ),
        **RUMOURED,
    )
    _add(
        rhine,
        "ziegensteine",
        "The Ziegensteine",
        inside=rugen,
        realm="Faerie",
        tethers="The great barrow under the oak",
        summary="The Goats' Stones, a cluster of ancient graves and megaliths in the "
        "woodland near the Mönchgut peninsula, the most prominent a barrow of two "
        "great slabs on uprights beneath a giant oak. The volkhvy of the Forest "
        "Brothers bury devout believers here; the great barrow itself is empty. "
        "Only a volkhv can open the gate it holds, and they often let Bjornaer "
        "magi use it because of Crintera's friendship, which makes it useful for "
        "contact between the Rhine and Novgorod Tribunals. The aura is not given.",
        secrets="The barrow is a pre-Hermetic supernatural gateway, one end of a faerie "
        "trod through a particularly dark and frightening region of Arcadia whose "
        "far end comes out near the covenant of Pripet Major in the Novgorod "
        "Tribunal. Nobody at the Russian end can open it, so it works one way "
        "only.",
        **RUMOURED,
    )
    _add(
        rhine,
        "buskam",
        "The Buskam",
        inside=rugen,
        summary=(
            "The god's stone, the largest of Rügen's findlinge, the out-of-place "
            "boulders of foreign rock that dot the island: a huge ball of stone "
            "half-submerged in the sea just off the Mönchgut peninsula, which the "
            "Slavic islanders still worship now and then. The findlinge were left by "
            "giants, the only remains of an epic battle centuries ago in which the "
            "giants of Rügen were driven out to Pomerania. The aura is not given."
        ),
        **KNOWN_LOCALLY,
    )
    pomerania = _add(
        rhine,
        "pomerania",
        "Pomerania",
        inside=region,
        summary=(
            "A thinly peopled Slavic land between the Baltic and Poland, bordering "
            "the Novgorod Tribunal, whose towns cluster on the coast and the rivers "
            "away from the primal forests inland. It has been part of the Empire only "
            "since 1181, when Barbarossa made Bogislaw a duke; German settlers are "
            "increasing, and the Church is weak here, unlike the rest of Germany, "
            "though the Knights of the Sword are founding Christian towns and "
            "monasteries and hunting pagan remnants in the forests. The giants "
            "banished from Rügen came here, and the Pomeranian Forest is the reputed "
            "stronghold of witches and werewolves. The aura is not given."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "romowe",
        "Romowe and the Holm Oak",
        inside=pomerania,
        tethers="The fire of fallen branches that must never go out",
        summary=(
            "A sacred grove in the northern Pomeranian Forest, a wood of pine, fir, "
            "holly and evergreen oak that spills into Poland and stays dark and green "
            "all year, where every local knows not to break a twig or kill a beast. "
            "At its centre a huge holm oak hangs with cloth ribbons and talismans, "
            "and a small band of foresters keeps a fire of fallen branches burning "
            "beneath it that must never go out. This is no pagan revival: the fire "
            "imprisons the malevolent spirit of Romowe (Magic, Might 45, now 30 while "
            "entrapped; Domineering +3, Cruel +1), which grants depression to anyone "
            "who breaks a branch or kills an animal and possesses anyone who takes a "
            "branch. The last time it was free it possessed a man who violated the "
            "grove and ruled the region as a tyrant until St Adalbert of Prague "
            "defeated it, forced it back into the oak and lit the fire. A magus who "
            "took a bough for a talisman would carry much of the spirit away with "
            "him. The aura is not given."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        rhine,
        "rethra",
        "Rethra",
        inside=pomerania,
        ruined=True,
        realm="Faerie",
        aura=4,
        tethers="The Oracle of Radegast",
        summary=(
            "Once a great Slavic fortress-temple to rival Arkona: a triangular "
            "citadel about the great Oracle of the god Radegast, each wall painted "
            "with old gods and holding a gate, two onto the forest and one onto a "
            "holy lake. For centuries it was also a covenant of Slavic magus-priests, "
            "which sank into deep Winter for a century or more as the forest folk "
            "abandoned the old faith; about twenty years ago the Knights of the Sword "
            "desecrated and plundered the crumbling temple, and with no word from its "
            "magi for decades the Tribunal of 1207 declared the covenant abolished. "
            "The Faerie aura is 4. The nobles of Mecklenburg still come secretly to "
            "honour Radegast though his priests are dead and would resent plunderers. "
            "The ruin may be haunted by the ghosts of its magi or shelter an ancient "
            "one on the edge of Final Twilight, and the Oracle may yield Intellego "
            "vis."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "brandenburg_march",
        "The Margravate of Brandenburg",
        inside=region,
        summary=(
            "Low-lying land on the east bank of the Elbe, founded as a march in 1150 "
            "by Albert the Bear, a Saxon who took the title of margrave after his "
            "campaigns against the Wends, and ruled since by his Ascanian descendants. "
            "Its people are a thorough mixture of Germans and Wends; it is mostly "
            "forest, slowly being cleared for farms. The aura is not given."
        ),
        **KNOWN_TRIBUNAL,
    )
    meissen = _add(
        rhine,
        "meissen_march",
        "The Margravate of Meissen",
        inside=region,
        summary=(
            "Moderately peopled rolling land bounded to the south by the Thuringian "
            "Forest and the Ore Mountains and to the north by the Elbe and the Saale, "
            "the most civilised part of the Marches and yet a political, commercial "
            "and ecclesiastical backwater, fully German and ruled by the Wettin "
            "dynasty since 1089. It has had no Hermetic covenant since Sirmium, which "
            "the invading Magyars destroyed in the tenth century; the magical sites "
            "and vis sources the Order knew here perished with it, and none are now "
            "known. The aura is not given."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "bastei",
        "The Bastei",
        inside=meissen,
        summary=(
            "Spectacular limestone cliffs and pinnacles, some a thousand feet high, "
            "above the Elbe upstream of Meissen near the Ore Mountains; the hilly "
            "country here and southern Lusatia to the east hold many such dramatic "
            "rock formations. The aura is not given."
        ),
        **KNOWN_REGION,
    )
    _add(
        rhine,
        "ore_mountains",
        "The Ore Mountains",
        inside=region,
        summary=(
            "The Erzgebirge, a bleak unsettled range of evergreen forest between "
            "Meissen and Bohemia, adjoining the Spruce Mountains of Franconia; the "
            "Elbe cuts through its eastern end, the main link between Meissen and "
            "Bohemia. Silver and tin have lately been found, and mining towns have "
            "sprung up, the largest Freiberg, founded in 1186; a twelfth-century "
            "imperial decree lets anyone prospect here and keep the proceeds. The "
            "aura is not given."
        ),
        **KNOWN_TRIBUNAL,
    )
    lusatia = _add(
        rhine,
        "lusatia_march",
        "The Margravate of Lusatia",
        inside=region,
        summary=(
            "Luzica, east of the Elbe bordering Silesia: mostly forest wilderness, "
            "sparsely settled and entirely by Sorbs, ruled for generations by the "
            "margraves of Meissen. Bautzen is the only place with real German "
            "influence, and the Knights of the Sword keep a large fortification there "
            "for the slaves they ship to the Prague market. The aura is not given."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "fengheld_lusatia",
        "Lusatia chapter",
        inside=lusatia,
        summary=(
            "Fengheld's newest chapter house, an idyllic riverside site on a bend of "
            "the river Spree in the March of Lusatia, only ten miles from the agreed "
            "border with the Novgorod Tribunal; its founding caused the most recent "
            "boundary dispute between the two Tribunals. One maga lives here, mostly "
            "as a bear. Its aura is not given."
        ),
        **KNOWN_TRIBUNAL,
    )


# -- chapter 10: Bohemia and Moravia --


def _bohemia(rhine: Rhine) -> None:
    region = rhine.places["bohemia"]
    _add(
        rhine,
        "vysehrad",
        "Vysehrad Rock",
        inside=region,
        summary=(
            "A hilltop just south of Prague where, in the eighth century, the Gifted "
            "princess Libuse, granddaughter of Czech, came after her father Krok died "
            "without a male heir and the Czechs agreed to accept whoever she chose as "
            "husband. Her vision here foretold a farmer ploughing with two oxen at a "
            "particular spot on the river Belina beyond the hills: Premysl, who "
            "became her husband and founded the ruling dynasty. A small settlement "
            "and Prague's second castle stand here now. The aura is not given."
        ),
        **KNOWN_REGION,
    )
    _add(
        rhine,
        "boii_springs",
        "The Boii Springs",
        inside=region,
        summary=(
            "Twelve hot mineral springs in the hills of western Bohemia beside the "
            "remains of a Celtic settlement, the largest a geyser forty feet high, "
            "pouring out so much hot water that the river Tepla runs warm for miles. "
            "Drinking the water cures ailments of the stomach. They are named for the "
            "Celtic Boii, from whom Bohemia takes its name. The aura is not given."
        ),
        **KNOWN_REGION,
    )
    _add(
        rhine,
        "mount_blanik",
        "Mount Blanik",
        inside=region,
        realm="Divine",
        tethers="The sleeping army of St Wenceslaus",
        levels=[
            Builder.level(
                "The hall of the sleeping knights",
                0,
                "Divine",
                notes=(
                    "A vast pillared underground hall (the regio's level and aura are "
                    "not given). Weapons and armour hang on the columns, hundreds of "
                    "horses stand asleep along one side, and their owners, the Knights "
                    "of Blanik (Divine, Might not given), sit at stone tables in "
                    "stone chairs."
                ),
            ),
        ],
        summary=(
            "A mountain of Bohemia covered by a Divine regio whose strength is not "
            "given. Where springs rise on its slopes an arch-shaped opening leads to a "
            "vast pillared hall underground where the Knights of Blanik, the sleeping "
            "army of St Wenceslaus (Divine, Might not given), sit at stone tables "
            "with their horses asleep beside them and their arms hung on the columns. "
            "Wenceslaus, Bohemia's patron and former duke, was murdered by his pagan "
            "brother Boleslav in the early tenth century; the prophecy says that in "
            "the Czechs' direst need he will rise, take the legendary sword of "
            "Bruncvik and come to Blanik to wake his army."
        ),
        **RUMOURED,
    )
    bohemian_forest = _add(
        rhine,
        "bohemian_forest",
        "The Bohemian Forest",
        inside=region,
        summary=(
            "The mountain spine along Bohemia's border, a forest nearly as large as "
            "the Black Forest and kept free of people by its harsh climate and its "
            "many peat bogs, swamps and marshes. The north is open beech woodland; on "
            "the lower mountain slopes beech and chestnut give way to birch and "
            "evergreens; the south, in the rain-shadow of the Alps, holds most of the "
            "standing water, with willow and alder among the pines and stunted "
            "rotting trees that give it a sinister air; the drier western mountains "
            "carry ordinary woodland and then pine and fir higher up. Lynx, wolves "
            "and deer live here, and giants (realm and Might not given) haunt it. "
            "The forest's powers and personality are left to the storyguide and its "
            "aura is not given."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "irencillia_site",
        "The woods of Irencillia",
        inside=bohemian_forest,
        realm="Faerie",
        aura=1,
        levels=[
            Builder.level(
                "The fragmented regiones",
                6,
                "Faerie",
                see=(
                    "Each entrance is marked with a symbol, a badger's head, a "
                    "crescent moon and the like, whose meaning outsiders do not grasp"
                ),
                notes=(
                    "Scattered patches of high aura, most of the magi's sancta among "
                    "them, each a small regio of its own; the aura within runs up to "
                    "6, and the levels are not numbered."
                ),
            ),
        ],
        summary="Beech and oak woodland in the northern Bohemian Forest where it meets "
        "the Bohemian plain, near the Maddenhofen Woods, with fallow deer, boar, "
        "lynx and bears common and few wolves, where the domus magna of House "
        "Merinita hides. The Faerie aura is highly patchy: at least 1 everywhere "
        "within the boundary, up to 6 where the sancta are sited, and odd spots "
        "run high (a covered walkway to the kitchens is Faerie 4 along its "
        "length); some high patches lie in small fragmented regiones with marked "
        "entrances. The theory is that the scattered aura and regiones are the "
        "fallout of a vast magical outpouring, the war between Quendalon and "
        "Myanar. The covenant appears differently to every visitor according to "
        "expectation, a faerie castle of living wood, a foresters' hamlet, a "
        "wooded hill with a trilithon over a labyrinth, a gully of caves, and "
        "those who do not know of it see only open woodland and wander through "
        "unknowingly; common to every view are an enclosing boundary, one "
        "gateway, and over it the inscription said to be Merinita's last words "
        "before she vanished in 785. Pieces taken out of the aura turn to dust, "
        "dry leaves and twigs at sunrise or sunset, and no usable map can be "
        "made. The surrounding land is kept wild by the covenant's meddling.",
        secrets="Irencillia was never Merinita's home. Her true first domus magna, the "
        "temple of Diana of which she was the last Roman priestess, is lost and "
        "its name forgotten.",
        **KNOWN_ORDER,
    )
    _add(
        rhine,
        "obri_hrad",
        "Obri Hrad",
        inside=bohemian_forest,
        aura=3,
        summary=(
            "The Giants' Castle, the remains of a primeval Celtic hill-fort on a "
            "hilltop above the river Losenice at the southern edge of the Bohemian "
            "Forest, strewn with great broken rocks the giants gathered. Its Magic "
            "aura of 3 makes it a possible covenant site, though the forest's giants "
            "(realm and Might not given) may still come by."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        rhine,
        "maddenhofen_woods",
        "The Maddenhofen Woods",
        inside=bohemian_forest,
        realm="Faerie",
        tethers="The faerie who grants the Heart's Desire",
        summary=(
            "House Merinita's name for a stretch of woods on the north-western fringe "
            "of the Bohemian Forest near Irencillia, which the covenant guards closely "
            "though it apparently takes no vis from them. Here the Founder Tytalus "
            "vanished in 807, declaring he would confront the Queen of all the Fae. "
            "The Merinita scoff at such a Queen, yet a powerful faerie (Faerie, Might "
            "not given) does live here who grants a petitioner's Heart's Desire in "
            "exchange for a task to be done afterwards, and nobody has ever completed "
            "one. The woods have a Stasis power, and Tytalus himself may be preserved "
            "within them. The aura is not given."
        ),
        **RUMOURED,
    )
    moravia = _add(
        rhine,
        "moravia",
        "The Margravate of Moravia",
        inside=region,
        summary=(
            "Bohemia's eastern March, bordered to the east by the Carpathians and "
            "Hungary, and so by the Transylvanian Tribunal; the river Morava runs "
            "through it to join the Danube in Austria. Its margrave is usually the "
            "Bohemian king's son or brother. It was part of Poland under Boleslaus I "
            "from 999 and has been part of Bohemia since 1019. Brünn is its seat, "
            "where the stuffed carcass of the dragon a travelling butcher killed with "
            "a hide full of unslaked lime hangs in the town hall. The aura is not "
            "given."
        ),
        **KNOWN_TRIBUNAL,
    )
    roznov = _add(
        rhine,
        "roznov_site",
        "The valley of Roznov",
        inside=moravia,
        aura=4,
        summary="A valley at the edge of the Carpathians on the Hungarian border in the "
        "extreme east of Moravia, under Mount Radhost, whose summit stands 3,700 "
        "feet high; a Magic aura of 4 covers the whole valley. A fort and village "
        "at the foot of the mountain control the single pass and trail up, and "
        "two-thirds of the way up a small twin-towered castle inside a curtain "
        "wall can be seen only from its own valley.",
        secrets="Castle and fort are linked by tunnels through the mountain.",
        **KNOWN_TRIBUNAL,
    )
    _add(
        rhine,
        "radhost_temple",
        "The temple on Mount Radhost",
        inside=roznov,
        aura=6,
        tethers="Radegast, whose sacred mountain this has always been",
        summary="A crude stone temple on the summit of Mount Radhost with a Magic aura of "
        "6. The mountain has always been sacred to Radegast, the Slavic god of "
        "chieftainship and war, fertility and harvest, and every summer solstice "
        "the whole covenant of Roznov and its village climb to celebrate him here "
        "with orgiastic drinking and debauchery, from which dozens of pawns of "
        "vis are harvested.",
        secrets="A few celebrants are quietly seized each year and sacrificed inside the "
        "temple, seen only by the high priest Igor Rastvan's most loyal servants; "
        "the victims usually come from the covenant's slaves, their blood yields "
        "Corpus vis and fuels the harvest. It is never discussed, though most "
        "covenfolk guess why people vanish each summer, and some supernatural "
        "agency seems to keep it secret from the Tremere of the fort.",
        **KNOWN_LOCALLY,
    )
