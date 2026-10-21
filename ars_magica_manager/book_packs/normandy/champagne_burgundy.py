"""Champagne and Burgundy, as of spring 1220: the fair country of the
upper Seine and the pilgrim duchy of the great monasteries, with their
sites and regiones; the covenants of Cunfin (magi and Cistercian monks
in one valley, the Tribunal's Mercer House and Celeres's Grail library)
and Atramentum Renatus; the Count of Champagne and the Duke of Burgundy,
the fair towns, the abbeys of Clairvaux, Citeaux and Cluny, and the
factions about them, in paraphrase of The Lion and the Lily chapter
nine. The covenants' lieges are set by the Tribunal part; the region's
ruined covenants (Bibracte, Lixivia, Moles Magna) are its too."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...arms import Arms
from ..builder import Builder, StatBlock, paragraphs
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Covenant, Neighbour, Tribunal
    from . import Normandy

# House ids, so a typo cannot slip into a record.
BJORNAER = "house_bjornaer"
BONISAGUS = "house_bonisagus"
EX_MISC = "house_ex_miscellanea"
JERBITON = "house_jerbiton"
MERCERE = "house_mercere"
TYTALUS = "house_tytalus"

# The lead line of a covenant's notes, before its secrets.
KNOWN_ORDER: dict[str, Any] = {"status": "Known", "known": "In the Tribunal"}


def _lines(*lines: str) -> str:
    """The lines as one text, one hook or secret a line."""
    return "\n".join(lines)


def _add(normandy: Normandy, key: str, name: str, **kw) -> Neighbour:
    place = normandy.b.place(name, **kw)
    normandy.places[key] = place
    return place


def build(normandy: Normandy) -> None:
    b = normandy.b
    tribunal = normandy.tribunal
    assert tribunal is not None
    _places(normandy)
    _cunfin(normandy, b, tribunal)
    _atramentum_renatus(normandy, b, tribunal)
    _lords(normandy, b)
    _towns(normandy, b)
    _churches(normandy, b)
    _factions(normandy, b)
    _vis(normandy)


# ---------------------------------------------------------------- places


def _places(normandy: Normandy) -> None:
    champagne = _add(
        normandy,
        "champagne",
        "Champagne",
        summary=paragraphs(
            "The Romans' Campania, the land of plains: rolling, rich farm "
            "country between the upper Seine in the south and the wooded "
            "heights of the Ardennes and the Argonne to the north and east. "
            "Apart from the swamp of St. Gond, the great forest of Orient "
            "and a few lesser woods it is all good tillage, and it is known "
            "for a red wine with a faint sparkle.",
            "Its wealth and fame in 1220 come from the cycle of trade fairs "
            "at Provins, Troyes, Lagny and Bar-sur-Aube, where the goods of "
            "the north and the Mediterranean change hands. A century of "
            "Cistercian houses founded by St. Bernard has filled it with "
            "busy monks and their cottage trades.",
            "The great road the Romans built from Lyon to Boulogne runs "
            "through it, and with it the Redcaps' route between the Rhine, "
            "the Greater Alps and Rome; the Mercer House at Cunfin sits on "
            "that road, close to the fairs, where Redcaps quietly pitch "
            "their own trading tents. The Church is strong here and "
            "covenants are few.",
        ),
        **KNOWN_ORDER,
    )
    burgundy = _add(
        normandy,
        "burgundy",
        "Burgundy",
        summary=paragraphs(
            "The south-eastern corner of the Tribunal and the old heartland "
            "of the Gauls, thick with their hill-towns and with Roman "
            "ruins. The duchy dates from the partition of Charlemagne's "
            "empire at Verdun in 843, when the north-western part of the "
            "old Burgundian kingdom fell to Charles the Bald; in the "
            "eleventh century Henry I of France gave it to his brother "
            "Robert, whose junior Capetian line has stayed loyal to the "
            "crown and, through crusading in Iberia, is kin to the royal "
            "houses of Castile and Portugal.",
            "Where Champagne lives by trade, Burgundy lives by pilgrims, and "
            "the Church is mightier here than anywhere: Cluny and Citeaux, "
            "the mother houses of their orders, Vezelay with the relics of "
            "St. Mary Magdalene, and Pontigny, Molesme, St. Seine, St. "
            "Benigne and Fontenay besides, with Clairvaux on the northern "
            "edge. The monks' vineyards make Burgundy one of the great wine "
            "lands of Europe.",
            "The duchy is not the larger kingdom of Burgundy (Arelat) to its "
            "south-east, which is shared between the Greater Alps and "
            "Provencal Tribunals.",
        ),
        **KNOWN_ORDER,
    )

    # -- Champagne --
    _add(
        normandy,
        "orient_forest",
        "The Forest of Orient",
        inside=champagne,
        realm="Magic",
        summary=(
            "The largest forest of Champagne, an island of woodland among "
            "the plains east of Troyes. The book names it but gives it no "
            "aura or inhabitants."
        ),
        **KNOWN_ORDER,
    )
    _add(
        normandy,
        "st_gond",
        "The Swamp of St. Gond",
        inside=champagne,
        realm="Magic",
        summary=(
            "The one stretch of Champagne that is not good farmland, a "
            "wide marsh south of Chalons. The book names it without "
            "detail."
        ),
        **KNOWN_ORDER,
    )
    _add(
        normandy,
        "chalons_meadow",
        "The Bishop's Meadow at Chalons",
        inside=champagne,
        realm="Divine",
        summary=paragraphs(
            "A broad, quiet riverside meadow just south of Chalons, part of "
            "the bishop's estate and lightly grazed by sheep. St. Bernard "
            "and Pope Eugene III both preached here.",
            "Travellers of every sort now treat it as a lucky and handy "
            "place to meet, and not all of their business is pious: a "
            "natural spot for a rendezvous, a hand-over or an ambush on "
            "the road between the fairs and the north.",
        ),
        **KNOWN_ORDER,
    )
    fields = _add(
        normandy,
        "catalaunian_fields",
        "The Catalaunian Fields",
        inside=champagne,
        realm="Infernal",
        aura=3,
        summary=paragraphs(
            "About a dozen miles from Chalons lies the field where, in "
            "451, the Roman general Aetius with Theoderic's Visigoths "
            "and the Franks of the sorcerer-king Merovech turned back "
            "Attila and his Ostrogoth allies at midsummer, after the "
            "Huns had sacked Reims and besieged Orleans. Theoderic fell; "
            "Attila escaped to his camp and away. More than forty "
            "thousand died, and an old chronicle tells of a brook "
            "swollen with blood that the wounded drank from.",
            "Today it is empty scrub and fallow, walked by a few thin "
            "sheep and grimy peasants, under a Malevolent Infernal aura "
            "of 3. A dark stream runs below the ridge in the middle of "
            "the field. On the night of the summer solstice, the "
            "battle's anniversary, it runs red, and the cries of dying "
            "men and horses are heard; whoever climbs the stream that "
            "night enters an Infernal regio where the ghosts of both "
            "armies fight forever, driven on by demons, among heaps of "
            "the dead and dying. A magus who braves it may harvest a "
            "great deal of Perdo and Corpus vis; the book gives no "
            "tenure for it.",
        ),
        secrets="Some of the Perdo and Corpus vis gathered in the regio carries "
        "an Infernal taint, and nothing marks which.",
        levels=[
            Builder.level(
                "The Endless Battle",
                0,
                "Infernal",
                enter=(
                    "Climb the blood-red stream below the central ridge on "
                    "the night of the summer solstice."
                ),
                notes=(
                    "The shades of Huns, Goths, Romans and Franks fight on, "
                    "goaded by warrior demons; Perdo and Corpus vis in "
                    "quantity, some of it tainted. Its aura is not given."
                ),
            )
        ],
        **KNOWN_ORDER,
    )
    _add(
        normandy,
        "attilas_camp",
        "Attila's Camp",
        inside=fields,
        realm="Infernal",
        summary=(
            "A few miles east of the battlefield, the overgrown remains of "
            "the camp where Attila's household guard held out after the "
            "battle, still ringed by a low wall."
        ),
        **KNOWN_ORDER,
    )
    _add(
        normandy,
        "caesar_tower",
        "The Caesar Tower",
        inside=champagne,
        realm="",
        summary=(
            "The great square watchtower and prison crowning the "
            "fortifications of Provins's upper town, beside the counts' "
            "hilltop castle. Folk say Julius Caesar himself raised it."
        ),
        **KNOWN_ORDER,
    )

    # -- Cunfin --
    cunfin = _add(
        normandy,
        "cunfin_site",
        "The Valley of Cunfin",
        inside=champagne,
        realm="Divine",
        summary=paragraphs(
            "A deep, well-watered valley in Champagne holding the "
            "village of Cunfin and its Cistercian abbey: plain buildings "
            "with almost no ornament, one low tower, undivided windows "
            "of clear glass and wooden crosses. The monks keep a "
            "Dominion whose temper Eloi's holy power has made Calm. The "
            "Dominion's strength is not given.",
            "Over the abbey and its surroundings lies a Magic regio of a "
            "single level, unseen by most of the mundane folk. It was "
            "once a ruined Roman fort; Celeres has rebuilt it as a "
            "miniature castle with pennons flying, and most of the "
            "covenant's members live there. Anyone carrying a charm cut "
            "from the fort's stones can pass in. How a Magic regio "
            "survives inside so strong a Divine aura is unknown, and "
            "several Bonisagus magi have studied it.",
        ),
        secrets="Rumour, perhaps true, says the abbey was founded in 1136 by "
        "Valoran, a pupil of St. Nerius; Eloi believes Valoran was "
        "Angelus's parens.",
        levels=[
            Builder.level(
                "Celeres's Castle",
                0,
                "Magic",
                see="A miniature castle where the Roman fort stood.",
                enter="Carry a charm made from the old fort's stones.",
                notes=(
                    "The covenant proper; its aura is not given. Eloi lives "
                    "mostly at the abbey and Angelus in his cave."
                ),
            )
        ],
        **KNOWN_ORDER,
    )
    _add(
        normandy,
        "angelus_cave",
        "Angelus's Cave",
        inside=cunfin,
        realm="Divine",
        summary=(
            "A small cave in the hills a stone's throw above the abbey of "
            "Cunfin, where the hermit Angelus has lived alone in prayer for "
            "decades. The monks know a holy hermit dwells there and count "
            "themselves blessed."
        ),
        **KNOWN_ORDER,
    )

    # -- Burgundy --
    _add(
        normandy,
        "morvan",
        "The Morvan",
        inside=burgundy,
        realm="Faerie",
        summary=paragraphs(
            "Burgundy's only real wilderness, the Black Mountain of its "
            "Celtic name: a basalt upland a little above the country round "
            "it, often lost in rain, snow or mist, its rivers quick to rise "
            "in sudden spate. Oak, hornbeam and beech cover most of it, with "
            "conifers on the high rocky slopes. It is poor, rolling land "
            "without fields or vines, and the few peasants who scratch a "
            "living there are shunned by their neighbours.",
            "Magi know of several vis sources in the Morvan, most of them "
            "disputed, for dark faeries haunt its lakes, streams and woods. "
            "Its aura is not given. The ruins of Bibracte lie on Mont "
            "Beauvray in the south, near Autun, and Moles Magna once stood "
            "on its edge.",
        ),
        **KNOWN_ORDER,
    )
    alesia = _add(
        normandy,
        "mont_auxois",
        "Mont Auxois (Alesia)",
        inside=burgundy,
        realm="Magic",
        summary=paragraphs(
            "A peak of about 1,300 feet a short way north-east of the "
            "Morvan and some six miles south of Fontenay abbey, crowned by "
            "the ruins of Alesia, the Gallo-Roman hill-fort where Caesar's "
            "siege forced Vercingetorix to surrender; he was taken to Rome "
            "in chains and strangled years later.",
            "Among the empty ruins are old bronze forges and an underground "
            "temple to the Gallic mother goddesses, the Matres. The hilltop "
            "keeps a Magic aura (strength not given) and could suit a new "
            "covenant, though the ghosts of the pagan dead haunt it.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        normandy,
        "fountain_st_reina",
        "The Fountain of St. Reina",
        inside=alesia,
        realm="Divine",
        summary=(
            "On the south-western edge of Mont Auxois, under a Divine aura, "
            "a spring rose where the young Christian Reina was beheaded for "
            "refusing to marry Olibrius, Roman governor of Alesia. Its water "
            "was said to heal, and drew pilgrims for a while before it was "
            "forgotten; the old fountain hides among trees beside a ruined "
            "Merovingian chapel to the saint."
        ),
        **KNOWN_ORDER,
    )
    _add(
        normandy,
        "cave_of_sabinus",
        "The Cave of Sabinus",
        inside=burgundy,
        realm="Magic",
        summary=paragraphs(
            "A hidden cave some ten miles south of Langres, beside the "
            "forest spring where the Marne begins, home to a powerful genius "
            "loci. Sabinus, a chieftain of the Lingones who rebelled at "
            "Langres after Nero's death in 70 AD, fled here and bargained "
            "for the spirit's protection; it hid him for nine years before "
            "it wearied of him, and he was found and taken to Rome to die.",
            "Aquam vis can be drawn from the spring if the spirit allows. "
            "Because the spirit is so hard to please, the Tribunal counts "
            "the source a luctatio, open to any magus who dares.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        normandy,
        "temple_of_janus",
        "The Temple of Janus at Autun",
        inside=burgundy,
        realm="Magic",
        summary=(
            "The remains of a Roman temple to Janus, the god with two faces "
            "who rules gates and doorways, of beginnings and endings, in a meadow "
            "across the Arroux outside Autun. No aura is given."
        ),
        **KNOWN_ORDER,
    )
    _add(
        normandy,
        "autun_pyramid",
        "The Pyramid of Autun",
        inside=burgundy,
        realm="Magic",
        summary=(
            "A strange ruined pyramid some fifty feet high standing in the "
            "fields about a mile south-east of Autun cathedral, most likely "
            "the tomb of some forgotten Roman notable. No aura is given."
        ),
        **KNOWN_ORDER,
    )
    normandy.places["atramentum_renatus_site"] = normandy.b.place(
        "Atramentum Renatus",
        inside=burgundy,
        realm="Magic",
        summary=(
            "The site of the covenant Atramentum Renatus in Burgundy, built "
            "about a vis source that was once a legacy of Fudarus. The book "
            "does not say where in the duchy it lies, nor its aura; its "
            "magi's interest in Bibracte suggests the Morvan's edge."
        ),
        **KNOWN_ORDER,
    )


# ---------------------------------------------------------------- Cunfin


def _cunfin(normandy: Normandy, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "A covenant of magi sharing a Champagne valley with a Cistercian "
        "abbey of the same name, which keeps the Order in touch with the "
        "Church's affairs. It is a vassal of Confluensis, recognised by the "
        "Tribunal of 1192 though magi lived on the site long before; Eloi "
        "of Jerbiton founded it with the backing of his parens Jerome. The "
        "Presiding Quaesitor worries about trouble with the mundanes, but "
        "the covenant's ties to the Church have served the Order well.",
        "When the old Mercer House at Tours fell to raiders in 1197, "
        "Confluensis seized on Florum's weakness and proposed Cunfin as the "
        "new one, close to the fairs, and paid for a Mercere Portal; the "
        "Redcaps agreed, handing Confluensis and its vassals a hold on "
        "Redcap services that its rivals noticed. A small band of Redcaps "
        "now lives here, the portal leads to Dragon's Rest, and from "
        "Cunfin they organise, with Confluensis, the temporary Mercer "
        "Houses at the Champagne fairs. The monks hold hospitality a holy "
        "duty and are used to travellers coming and going.",
        "In 1199 the ancient, eccentric Celeres of Bonisagus arrived, "
        "declaring Cunfin the castle from which he and his knights would "
        "seek the Grail. Many took it as proof he was mad, but he has made "
        "himself the heart of the place: his rebuilt castle stands in the "
        "regio over the abbey, his Grail library draws scholars from across "
        "the Order, and every visitor has a story about his hospitality.",
        "Cunfin's purpose is to stand between the Order and the Church. "
        "Eloi is the abbey's prior, Brother Eligius, with great sway over "
        "the monks and their abbot; the monks put his wonders down to "
        "holiness. All the magi but Angelus have the Gentle Gift. Abbot "
        "Martin, the cellarer and a few brothers know the truth and support "
        "the magi; the rest of the monks have met the magi without knowing "
        "what they are.",
    )
    what_matters = _lines(
        "Vis: none is named in the book",
        "Library: Celeres's Grail library, said to hold every book written on the Grail and many on Arthur and Merlin",
        "Income: the Tribunal's Mercer House, and the Redcaps' trade at the temporary Mercer Houses of the Champagne fairs",
        "Mundane: the Cistercian abbey of Cunfin, its prior a magus and its abbot an ally; Eloi's contacts reach the whole Cistercian Order",
        "Mundane: a Mercere Portal to Dragon's Rest, paid for by Confluensis",
        "Boon: Mercer House; Hook: a Divine aura round a Magic regio",
        "Tourney: Eloi, Celeres and the Redcap Renaud have won the hastiludium three times running",
        "Tension: the Presiding Quaesitor fears the covenant will embroil the Order with the mundanes",
        "Tension: Florum and others resent Confluensis's grip on the Redcaps since the Mercer House moved here",
        "Tension: Celeres is the Tribunal's eldest magus now Renita is dead and Stellatus gone to Iberia, so first in line for Praeco; Proctor would set him aside",
        "Tension: Hervé holds the post at the fairs that Renaud wanted, and resents his foster brother",
        "Tension: the new Dominican Order's hunt for heretics; Eloi fears the inquisitors will turn north once the Cathars are done",
        "Hook: everything rests on Eloi; without him the arrangement would fall apart",
    )
    hidden = _lines(
        "The abbot knows what Eloi and the magi are and shares their aims.",
        "Jerome of Confluensis secretly saves troublesome heirs marked for death, convincing the world they are dead and hiding them in monasteries and covenants; Eloi is his chief partner, and Artorius was one such child. It is very likely a breach of the Code.",
        "The covenant may not survive the Church's growing hostility even with Eloi (The Specter of Rome).",
    )
    cunfin = b.covenant(
        "Cunfin",
        tribunal=tribunal,
        founded=1192,
        place=normandy.places["cunfin_site"],
        level=1,
        summary=summary,
        what_matters=what_matters,
        secrets=hidden,
        unnamed_magi=0,
        season="Summer",
    )
    normandy.covenants["cunfin"] = cunfin
    _cunfin_magi(normandy, b, cunfin)
    _grail_library(b, cunfin)


def _cunfin_magi(normandy: Normandy, b: Builder, cunfin: Covenant) -> None:
    m = normandy.magi
    m["eloi"] = b.magus(
        "Eloi",
        covenant=cunfin,
        house=JERBITON,
        age=62,
        traits={"Pious": 3, "Diplomatic": 3, "Forgiving": 1},
        summary=paragraphs(
            "Founder of Cunfin and the man who holds it together, "
            "looking about fifty-two. To the monks he is Brother "
            "Eligius, their prior, loved for his devotion and sought for "
            "his wise counsel; to the magi he is a magus deeply anxious "
            "about the Order's standing with the Church. He sees himself "
            "as a follower of St. Nerius, bridging the Magic and the "
            "Divine, and his charm and faith bind the covenant's "
            "quarrelsome members together.",
            "A younger son of minor nobles meant for the priesthood, he "
            "was found by Jerome of Jerbiton and trained as a magus "
            "instead, serving Jerome usefully at Confluensis but never "
            "reconciling his Gift with his wish to serve God. Meeting "
            "Angelus in 1191 showed him a way: he joined the abbey, "
            "founded the covenant with Jerome's blessing, and was soon "
            "elected prior. He uses Holy Influence to calm the Dominion "
            "about the abbey.",
            "Close to the Priory of St. Nerius without belonging to it, "
            "he wants Nerius recognised by the Latin Church, but above "
            "all wants peace between Order and Church, and uses his "
            "weight in the Cistercian Order to head off quarrels between "
            "magi and clergy. With Jerome and Proctor he was one of the "
            "three pillars of the late Praeco's Tribunal, its link to "
            "the Church. His present worry is the new Dominicans and "
            "their zeal against heresy.",
        ),
        secrets="He is Jerome's chief partner in hiding rescued heirs, which "
        "is very likely a breach of the Code; it brought Artorius to "
        "Cunfin.",
    )
    m["angelus"] = b.magus(
        "Angelus",
        covenant=cunfin,
        house=EX_MISC,
        age=97,
        traits={"Calm": 2, "Merciful": 2},
        summary=paragraphs(
            "A holy hermit of House Ex Miscellanea who looks about "
            "seventy-five and lives alone in a cave above the abbey, "
            "contemplating God. The Order's only record of him is from "
            "the Tribunal of 1144, where he appeared once and then "
            "dropped out of sight; he had not left his cave for decades "
            "when Eloi found him in 1191, told him of St. Nerius and "
            "showed him the abbey and its regio. At the next Tribunal "
            "Cunfin was recognised with the two of them as founders.",
            "He holds that Magic flows from the Divine and that Twilight "
            "is a glimpse of the face of God: a blessing God gives, but "
            "one it is sinful to seek, since only God judges who is "
            "worthy. He takes little part in the covenant's affairs, "
            "though Eloi and even Celeres come to him for counsel. He "
            "alone of Cunfin's magi lacks the Gentle Gift.",
        ),
        secrets="He will not speak of his lineage; Eloi believes his parens was "
        "Valoran, filius of St. Nerius himself.",
    )
    m["celeres"] = b.magus(
        "Celeres",
        covenant=cunfin,
        house=BONISAGUS,
        age=150,
        traits={"Forceful": 3, "Charming": 2, "Absent-minded": 2},
        summary=paragraphs(
            "A magus of House Bonisagus perhaps a hundred and fifty years "
            "old (the book is not sure) and looking a hundred: since Renita's "
            "death and Stellatus's departure for Iberia, the eldest magus of "
            "the Tribunal and so first in line to be Praeco, to the dismay "
            "of Confluensis, whose magi fear his eccentricity and his hold "
            "over Cunfin's Redcaps.",
            "Late in the twelfth century he found a copy of Chretien's "
            "Perceval and was seized by the riddle of the Grail. He gathered "
            "every book on Arthur, the Round Table and the Grail he could, "
            "and when he heard of Cunfin, with its monks and holy hermit, it "
            "seemed a page from the romances: he came at once in 1199 and "
            "talked Eloi into admitting him. He rebuilt the regio as a "
            "castle and calls the Redcaps his knights, who bring him every "
            "rumour of the Grail.",
            "No longer hoping to find it, he now thinks the Grail may be "
            "beyond finding, and wants instead to understand it and share "
            "what he learns. He is writing a great Grail cycle on its "
            "spiritual meaning, coloured by Cistercian thought, and hopes "
            "his last apprentice Artorius will finish it if he cannot. Many "
            "doubt his wits; no one doubts his scholarship. He has the "
            "Gentle Gift, a playful humour, and is one of the covenant's "
            "champion hastiludium team.",
        ),
    )
    m["herve"] = b.magus(
        "Hervé filius Évrard",
        covenant=cunfin,
        house=MERCERE,
        age=35,
        traits={"Driven": 3, "Jealous": 2},
        summary=paragraphs(
            "Hervé le Brun, a Redcap of the Founder's blood and son of "
            "Évrard de Tours: a stocky man with dark brown hair and olive "
            "skin who looks like his father and dresses, as he does, in "
            "plain town clothes. His soothing manner hides a calculating, "
            "driven mind.",
            "He has always felt his father favoured his foster brother "
            "Renaud, an un-blooded foundling Évrard knew would face "
            "obstacles in the House. At the University of Paris, where "
            "Renaud breezed through his studies on wit and wine while Hervé "
            "fought with a Latin he never mastered, and where Renaud joined "
            "the Goliards without losing his father's support, Hervé vowed "
            "to outdo him.",
            "No scholar, he is a shrewd judge of people and a fine "
            "negotiator who always comes away from the fairs with a profit. "
            "He now runs the temporary Mercer House at the Champagne fairs, "
            "the post Renaud wanted, but his father has still not given him "
            "the recognition he craves, and he has his eye on higher places "
            "in House Mercere.",
        ),
    )
    m["artorius"] = b.magus(
        "Artorius filius Celeres",
        covenant=cunfin,
        house=BONISAGUS,
        age=33,
        traits={"Loyal": 2, "Regal": 2},
        summary=paragraphs(
            "A magus of House Bonisagus newly through his Gauntlet. "
            "Eloi brought him to Cunfin as an orphan of sixteen, meaning "
            "to train him as his own successor, but Celeres announced he "
            "needed a squire and claimed the boy as his own apprentice. "
            "At his Gauntlet, his knighting as Celeres puts it, his "
            "parens named him after the legendary king of Britain. He "
            "has the Gentle Gift; his plans are his own.",
        ),
        secrets="He is one of the heirs Jerome saved from death for their "
        "birthright and hid with Eloi's help; whose heir he is, the book "
        "does not say.",
    )
    m["evrard"] = b.magus(
        "Évrard de Tours",
        covenant=cunfin,
        house=MERCERE,
        age=87,
        traits={"Stubborn": 2, "Grumpy": 2},
        summary=paragraphs(
            "Redcap of House Mercere and the Tribunal's senior Redcap, the "
            "only one at Cunfin who served at the old Mercer House in Tours. "
            "He moved the House to Cunfin, rebuilt its network and trained "
            "its Redcaps, and now wants to retire: his only duty is to watch "
            "over the Mercere Portal to Dragon's Rest. He looks under fifty, "
            "having begun a longevity ritual late in life.",
            "He trained both Cunfin's other Redcaps, his son Hervé and the "
            "foundling Renaud, and passed his post at the fairs to Hervé. "
            "After so long in a monastery he finds Celeres's playful humour "
            "a relief and spends much time with him.",
        ),
    )
    m["renaud"] = b.magus(
        "Renaud Fouinon",
        covenant=cunfin,
        house=MERCERE,
        age=None,
        summary=paragraphs(
            "Redcap of House Mercere, a foundling Eloi brought to the "
            "covenant, trained by Évrard and raised as Hervé's foster "
            "brother. Naturally clever, he drank and slept his way through "
            "the University of Paris and joined the Goliards, which most "
            "likely cost him the post at the Champagne fairs that went to "
            "Hervé. He now roams France enjoying himself, and is proud to "
            "be one of Cunfin's hastiludium team with Celeres and Eloi, "
            "which has won three times running.",
        ),
    )


def _grail_library(b: Builder, cunfin: Covenant) -> None:
    b.book(
        cunfin,
        "The Grail Library",
        "Other",
        description=(
            "Celeres's collection on the Grail, Arthur and Merlin, said to "
            "hold every book written on the Grail. Few Arthurian works exist "
            "in 1220, and the library sorts them into folk tales (mostly "
            "Celeres's own transcriptions, in the tale's own tongue with a "
            "Latin translation and commentary), Latin British histories, "
            "and French romances, his favourites. Magi travel to consult "
            "it, and Celeres welcomes the company. His own Grail cycle, "
            "unfinished, is kept here too."
        ),
    )
    b.book(
        cunfin,
        "Legends of Brittany",
        "Ability Summa",
        ability="Faerie Lore",
        level=3,
        quality=5,
        author="Celeres of Bonisagus",
        description=(
            "A thick book of tales Celeres took down from Breton "
            "storytellers, describing many Breton places tied to Arthur and "
            "usually to faeries: Arthur's fight with a giant on Mont St. "
            "Michel and Merlin's vanishing into Broceliande among them."
        ),
    )
    b.book(
        cunfin,
        "Arthur Among the Britons",
        "Tractatus",
        ability="Area Lore: Britain",
        quality=5,
        author="Celeres of Bonisagus",
        description=(
            "Welsh tales touching Arthur, among them Culhwch and Olwen, "
            "where Arthur's knights win a string of treasures so Culhwch may "
            "marry, and the Welsh Triads of things told in threes, with "
            "passages from the bard Taliesin."
        ),
    )
    b.book(
        cunfin,
        "The Llancarfan Saints' Lives",
        "Tractatus",
        ability="Dominion Lore",
        quality=6,
        author="Monks of Llancarfan (twelfth century)",
        description=(
            "Lives of Welsh saints that mention Arthur: Cadoc, Padarn, "
            "Carannog and, most often, Gildas. They link the folk tales to "
            "the histories."
        ),
    )
    b.book(
        cunfin,
        "History of the Britons",
        "Tractatus",
        ability="Area Lore: Britain",
        quality=5,
        author="Nennius",
        description=(
            "An eighth-century British monk's gathering of whatever he "
            "could find on Britain's past, from its founding by Brutus, "
            "great-grandson of Aeneas; the oldest account of Arthur's life."
        ),
    )
    b.book(
        cunfin,
        "History of the Kings of Britain",
        "Tractatus",
        ability="Area Lore: Britain",
        quality=9,
        author="Geoffrey of Monmouth",
        description=(
            "A twelfth-century cleric's great expansion of Nennius, centred "
            "on Arthur's deeds and including the Prophecies of Merlin; it "
            "ends with Arthur gravely wounded by his nephew Mordred and "
            "carried to Avalon to be healed."
        ),
    )
    b.book(
        cunfin,
        "The Lais of Marie de France",
        "Tractatus",
        ability="Charm",
        quality=5,
        language="French",
        author="Marie de France",
        description=(
            "Songs of love and chivalry by a poet of the court of Marie of "
            "Champagne, Eleanor of Aquitaine's daughter. Many began as "
            "Breton tales, and their popularity paved the way for the "
            "romance."
        ),
    )
    b.book(
        cunfin,
        "Arthurian Romances",
        "Tractatus",
        ability="Etiquette",
        quality=6,
        language="French",
        author="Chretien de Troyes",
        description=(
            "Chretien's four great Arthurian poems, Erec and Enide, Cliges, "
            "Yvain and Lancelot, on courtly love and the ideals of "
            "chivalry."
        ),
    )
    b.book(
        cunfin,
        "Perceval",
        "Tractatus",
        ability="Dominion Lore",
        quality=6,
        language="French",
        author="Chretien de Troyes",
        description=(
            "The unfinished tale of an innocent boy who blunders into "
            "knighthood, and the first work to mention the Grail: at a "
            "strange castle he sees it but fails to ask about it, leaving "
            "the wounded Fisher King unhealed, and sets out to make amends. "
            "Chretien died before revealing the Grail's secret, and four "
            "later writers have offered endings."
        ),
    )
    b.book(
        cunfin,
        "Joseph d'Arimathie",
        "Tractatus",
        ability="Dominion Lore",
        quality=5,
        language="French",
        author="Robert de Boron",
        description=(
            "Also called the Romance of the Grail: the Grail is the dish of "
            "the Last Supper in which Joseph of Arimathea caught Christ's "
            "blood, carried after the Resurrection to England and guarded "
            "by Joseph's kin down to Perceval. Robert is the first to call "
            "it the Holy Grail."
        ),
    )
    b.book(
        cunfin,
        "Parsifal",
        "Tractatus",
        ability="Magic Lore",
        quality=5,
        language="High German",
        author="Wolfram von Eschenbach",
        description=(
            "A German retelling of Perceval that goes its own way: Wolfram's "
            "Grail is a stone linked to the heavens, kept in the castle of "
            "Munsalvaesche by an order of guardians he calls templeisen (not "
            "the Knights Templar), and the poem is rich in alchemy, "
            "astrology and Arabic learning."
        ),
    )
    b.book(
        cunfin,
        "Minor works of the Grail Library",
        "Other",
        description=(
            "Lesser texts beside the major ones: the Book of Taliesin and "
            "the Lives of St. Efflam and St. Illtud among the folk tales; "
            "the Annals of Wales, Concerning the Ruin of Britain and the "
            "Life of Merlin among the histories; and the Roman de Brut, the "
            "continuations of Perceval and Perlesvaus among the romances."
        ),
    )


# ---------------------------------------------------------- Atramentum Renatus


def _atramentum_renatus(normandy: Normandy, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "A young covenant in Burgundy, vassal of Exspectatio and through it "
        "bound to Fudarus. In 1200 Helios of Tytalus and Gulo Midusulfis of "
        "Bjornaer founded a vassal of Fudarus in the Arree Mountains of "
        "Brittany and named it Atramentum, ink, after a sodalis who died in "
        "the founding. A year later five of Fudarus's magi, leaving their "
        "own covenant over the feud of its Primi, threw the two young "
        "founders out and took the site as Exspectatio. By way of "
        "amends Exspectatio gave them the means to start again in Burgundy, "
        "about a vis source that had been a legacy of Fudarus, and they "
        "called the new covenant Atramentum Renatus, ink reborn.",
        "Iacula of Bonisagus and Philip of Ex Miscellanea have since joined "
        "them. Like the other vassals of Fudarus's line, the covenant is "
        "bound by a hard oath of obligation and must compete hard at the "
        "Tourney to pay its feudal debts, in return for Fudarus's generous "
        "political support.",
    )
    what_matters = _lines(
        "Vis: the source about which the covenant was built, formerly a legacy of Fudarus (Art and amount not given)",
        "Library: no books are named",
        "Oath: a harsh contract of obligation to Exspectatio and Fudarus, paid partly from Tourney winnings",
        "Tension: Helios's theurgy probes whether Bibracte raised the spirit of Vercingetorix; Philip fears it is angering the ghosts",
        "Tension: a Quaesitor is looking into reports of a savage wild beast near the covenant, and whether Gulo broke the Code",
        "Tension: the founders were evicted from their first covenant by their liege's own magi",
        "Hook: Iacula's new projectile spells have great martial potential",
    )
    hidden = _lines(
        "Whether the ravaging beast is Gulo in his heartbeast's shape, and whether he harmed mundanes by it, is the Quaesitor's open question.",
        "Cynics say Helios and Gulo were duped into preparing Atramentum's site for the elder Tytali of Exspectatio.",
    )
    renatus = b.covenant(
        "Atramentum Renatus",
        tribunal=tribunal,
        founded=1201,
        place=normandy.places["atramentum_renatus_site"],
        summary=summary,
        what_matters=what_matters,
        secrets=hidden,
        unnamed_magi=0,
        season="Spring",
    )
    normandy.covenants["atramentum_renatus"] = renatus
    m = normandy.magi
    m["helios"] = b.magus(
        "Helios filius Kybella",
        covenant=renatus,
        house=TYTALUS,
        age=None,
        summary=paragraphs(
            "A theurgist of House Tytalus and co-founder of both Atramentum "
            "and Atramentum Renatus. He is fascinated by the schemes of the "
            "fallen Diedne covenant of Bibracte and its cult of "
            "Vercingetorix, and is trying to learn whether its magi "
            "succeeded in raising the hero's spirit.",
        ),
    )
    m["gulo"] = b.magus(
        "Gulo Midusulfis",
        covenant=renatus,
        house=BJORNAER,
        age=None,
        summary=paragraphs(
            "A magus of House Bjornaer and co-founder of Atramentum and "
            "Atramentum Renatus. A Quaesitor wants to know whether the "
            "reports of a wild beast ravaging the country round the "
            "covenant mean that Gulo has broken the Code.",
        ),
    )
    m["iacula"] = b.magus(
        "Iacula",
        covenant=renatus,
        house=BONISAGUS,
        age=None,
        summary=paragraphs(
            "A maga of House Bonisagus who joined Atramentum Renatus after "
            "its founding. She is absorbed in the study of how thrown and "
            "shot things fly, and her research has produced several spells "
            "with great martial potential.",
        ),
    )
    m["philip"] = b.magus(
        "Philip",
        covenant=renatus,
        house=EX_MISC,
        age=None,
        summary=paragraphs(
            "A magus of House Ex Miscellanea and one of the Donatores, a "
            "tradition that seeks to lay the restless dead to rest. Lately "
            "of Requies Aeterna, he has only just joined Atramentum Renatus. "
            "He shares Helios's interest in Bibracte but fears his "
            "colleague's work is stirring its ghosts to anger.",
        ),
    )
    b.book(
        renatus,
        "Library of Atramentum Renatus",
        "Other",
        description=(
            "The book names none of the covenant's books. A young, "
            "hard-pressed covenant whose resources came from Exspectatio "
            "would have a modest collection; Helios's notes on Bibracte and "
            "theurgy and Iacula's work on projectiles are its likeliest "
            "treasures."
        ),
    )


# ---------------------------------------------------------- the mundane world


def _king(normandy: Normandy) -> Neighbour | None:
    """The King of France, if the Ile de France part has made him."""
    for key in ("king_of_france", "philip_augustus", "king"):
        if key in normandy.world:
            return normandy.world[key]
    return None


def _lords(normandy: Normandy, b: Builder) -> None:
    w = normandy.world
    king = _king(normandy)
    w["count_of_champagne"] = b.lord(
        "Count of Champagne",
        title="count",
        wealth="Wealthy",
        seat="Provins",
        ruler="Theobald IV (regent: Blanca of Navarre)",
        answers_to=king,
        place=normandy.places["champagne"],
        arms=Arms("Azure", charge="Bend", charge_tincture="Argent"),
        summary=paragraphs(
            "Theobald IV, a charming young count of nineteen, holds many "
            "lesser counties and baronies in Champagne and is overlord of "
            "Blois and Chartres in the Ile de France and Auxerre in "
            "Burgundy. His mother, Blanca of Navarre, loyal to King Philip, "
            "rules as regent. He cares little for hunting or building "
            "castles; he is a gifted young poet and musician who loves books "
            "and travel, and his romantic, wandering ways so trouble his "
            "mother that she is already arranging a political marriage for "
            "him. His court spends long seasons at Provins, which is "
            "becoming a home of the arts under him.",
            "If history holds, he comes of age in 1222 and his early reign "
            "is troubled by money, politics and three marriages, until in "
            "1235 he inherits Navarre through his mother, daughter of King "
            "Sancho VI. He will be remembered as one of the finest "
            "troubadours of his age, the Chansonnier, and will bring Syrian "
            "roses to Provins.",
            "His arms are azure, a bend argent with potent cotises or; the "
            "shield here shows the bend alone.",
        ),
    )
    w["duke_of_burgundy"] = b.lord(
        "Duke of Burgundy",
        title="duke",
        wealth="Wealthy",
        seat="Dijon",
        ruler="Hugh IV (regent: Alice de Vergy)",
        answers_to=king,
        place=normandy.places["burgundy"],
        arms=Arms("Or", division="Bendy", second="Azure"),
        summary=paragraphs(
            "Hugh IV, the Capetian Duke of Burgundy, is only eight; his "
            "mother Alice de Vergy rules as regent and, like Champagne's "
            "regent, is loyal to the French crown. The dukes descend from "
            "Robert, brother of King Henry I, to whom the duchy was granted "
            "in the eleventh century, and are kin to the kings of Castile "
            "and Portugal. Robert I moved the ducal seat from Autun to "
            "Dijon in 1051; the dukes are now buried at Citeaux, not Autun, "
            "and hold the walled hill-town of Avallon as a stronghold.",
            "Their arms are bendy or and azure, a bordure gules; the shield "
            "here shows the bendy field without the border.",
        ),
    )


def _towns(normandy: Normandy, b: Builder) -> None:
    w = normandy.world
    champagne = normandy.places["champagne"]
    burgundy = normandy.places["burgundy"]
    count = w["count_of_champagne"]
    duke = w["duke_of_burgundy"]
    w["chalons"] = b.town(
        "Chalons-en-Champagne",
        charter="Church",
        ruler="The Bishop of Chalons",
        place=champagne,
        summary=paragraphs(
            "An ancient city on the Marne where the roads from the fairs "
            "head north to Reims, Picardy and Flanders; Roman Catalaunum. "
            "It matters more to the Church than to trade: its bishops take "
            "part in the coronations at nearby Reims, and two great "
            "churches dominate it.",
            "The basilica of Notre-Dame stands on the pilgrim road south "
            "through Burgundy to Compostela and draws pilgrims of its own, "
            "for shepherds found a statue of the Virgin there in a burning "
            "bush. Newly built Notre-Dame-en-Vaux, a collegiate church, has "
            "the pointed vaults of the new French style and two Romanesque "
            "towers, and a famous arcaded cloister of sixty column-statues "
            "of prophets and saints. The bishop's meadow lies just south of "
            "the city, and the Catalaunian Fields a dozen miles out.",
        ),
    )
    w["provins"] = b.town(
        "Provins",
        charter="Noble lord",
        ruler="The Count of Champagne",
        answers_to=count,
        place=champagne,
        summary=paragraphs(
            "One of Champagne's chief cities, grown rich under Count Henry "
            "I in the later twelfth century. It holds two fairs a year, from "
            "May to June in the upper town and from September to October in "
            "the lower, when it swells into a vast market of southern and "
            "northern visitors: merchants, innkeepers and moneychangers, "
            "with many clothmakers, dyers and weavers and a sizeable Jewish "
            "community. Count Theobald's court stays here for long spells.",
            "The lower town grew round a Benedictine priory of the eleventh "
            "century, built where St. Ayoul's relics were found by a miracle; "
            "the upper town round the counts' hilltop castle, crowned by the "
            "Caesar Tower.",
        ),
    )
    w["troyes"] = b.town(
        "Troyes",
        charter="Noble lord",
        ruler="The Count of Champagne",
        answers_to=count,
        place=champagne,
        summary=paragraphs(
            "Champagne's other great fair town, with two fairs a year (late "
            "June to early August, and November to mid-December), older "
            "than Provins and built on a Gaulish fortress. Its early bishop "
            "St. Lupus saved it from Attila by giving himself as a hostage "
            "and came home only after long captivity. The fairs' weight is "
            "such that Troyes has set its own measure, the Troy ounce.",
            "It has two quarters, the cathedral district, which has hosted "
            "great Church councils, and the commercial quarter round the "
            "old castle where the fairs are held. Henry I the Liberal "
            "founded thirteen churches and thirteen hospitals here. The poet "
            "Chretien de Troyes lived here for much of his life, and the "
            "great Jewish commentator Rashi (1040 to 1105) was born and "
            "taught here. If history holds, Jacques Pantaleon, a local "
            "cobbler's son, will become Pope Urban IV in some forty years.",
        ),
    )
    w["lagny"] = b.town(
        "Lagny",
        charter="Noble lord",
        answers_to=count,
        place=champagne,
        summary=(
            "A Champagne town holding one of the six great fairs of the "
            "cycle; the book gives no more."
        ),
    )
    w["bar_sur_aube"] = b.town(
        "Bar-sur-Aube",
        charter="Noble lord",
        answers_to=count,
        place=champagne,
        summary=(
            "A Champagne town holding one of the six great fairs of the "
            "cycle. Clairvaux abbey keeps a townhouse here."
        ),
    )
    w["auxerre"] = b.town(
        "Auxerre",
        charter="Noble lord",
        ruler="The Count of Auxerre, under the Count of Champagne",
        answers_to=count,
        place=burgundy,
        summary=paragraphs(
            "Roman Autessiodurum on the road from Lyon to Boulogne, a holy "
            "place since the fifth century, when St. Germanus was its "
            "bishop: a proud, worldly nobleman and governor of Gaul whom "
            "bishop St. Amator turned to prayer by burning his hunting "
            "trophies and tonsuring him against his will. Its school was "
            "famous under the Carolingians; the town has declined since, "
            "though the Pope named it a Holy City in the twelfth century.",
            "Its oldest house is the Benedictine abbey of St. Germanus, and "
            "the new cathedral of St. Etienne, begun in 1215, is still "
            "little more than a building site.",
        ),
    )
    w["avallon"] = b.town(
        "Avallon",
        charter="Noble lord",
        ruler="The Duke of Burgundy",
        answers_to=duke,
        place=burgundy,
        summary=(
            "A walled town on a granite hilltop over terraced slopes above "
            "the Cousin, on the site of the Roman citadel of Aballo. Sacked "
            "by the Goths, fortified after raids by Moors and Normans, it "
            "is now a formidable stronghold of the dukes that has seen off "
            "more than one siege. Pilgrims come to its church of St. "
            "Lazarus, a little over a century old, for a piece of the "
            "saint's skull that protects against leprosy."
        ),
    )
    w["vezelay_town"] = b.town(
        "Vezelay",
        charter="Church",
        ruler="The Abbot of Vezelay",
        place=burgundy,
        summary=(
            "A thriving town in the valley below the hilltop abbey of St. "
            "Mary Magdalene, on the edge of the Morvan above the valley of "
            "the Cure, living off the steady stream of pilgrims; one of the "
            "great roads to Compostela begins here. In 1096 its peasants "
            "rose against the abbot's taxes for a new church and killed "
            "him."
        ),
    )
    w["autun"] = b.town(
        "Autun",
        charter="Church",
        ruler="The Bishop of Autun",
        place=burgundy,
        summary=paragraphs(
            "Roman Augustodunum, after Lyon the greatest Roman city of Gaul, "
            "on the main road from Lyon to Boulogne, with the most complete "
            "Roman remains in the Tribunal. It became one of the earliest "
            "bishoprics in France and hosted Church councils, one of which "
            "regulated the Benedictines in the seventh century. It has "
            "faded since the dukes moved to Dijon.",
            "Two Roman gates still serve, St. Andrew's in the east and the "
            "Porta Senonica over the Arroux to the north; the vast Roman "
            "theatre, which held twelve thousand, is quarried for stone. "
            "Miles of ramparts and aqueducts surround the walls, with the "
            "temple of Janus across the river and a ruined pyramid in the "
            "fields to the south-east.",
        ),
    )
    w["langres"] = b.town(
        "Langres",
        charter="Church",
        ruler="The Bishop of Langres",
        place=burgundy,
        summary=(
            "A walled hill-town, the northern gate of Burgundy, named for "
            "the Lingones whose capital it was; as Roman Andemantunum it "
            "stood where twelve roads met. Its influential bishops rule it "
            "now. St. Didier, an early bishop, was beheaded defending it "
            "against barbarians, picked up his head and rode away; a chapel "
            "marks where he finally died. The Cave of Sabinus lies ten "
            "miles south."
        ),
    )
    w["dijon"] = b.town(
        "Dijon",
        charter="Noble lord",
        ruler="The Duke of Burgundy",
        answers_to=duke,
        place=burgundy,
        summary=(
            "The ducal seat since 1051 and now Burgundy's largest town, fat "
            "on the court: a centre of art and trade full of poets, "
            "craftsmen and visiting minor nobles with their hangers-on. A "
            "riot and fire in 1137 burned nearly all of it; Duke Hugh II "
            "rebuilt it with wider walls and a grand palace. In 1220 the "
            "foundations of a great new church in the French style were "
            "lately laid. St. Benignus's abbey church keeps the "
            "tomb of its founding patron saint."
        ),
    )
    w["cluny_town"] = b.town(
        "Cluny",
        charter="Church",
        ruler="The Abbot of Cluny",
        place=burgundy,
        summary=(
            "A large, wealthy town beside the great abbey, there mostly to "
            "supply the monks with the luxuries they want: jewellers, "
            "goldsmiths and other fine craftsmen, with a steady flow of "
            "visitors besides."
        ),
    )


def _churches(normandy: Normandy, b: Builder) -> None:
    w = normandy.world
    champagne = normandy.places["champagne"]
    burgundy = normandy.places["burgundy"]
    w["bishop_of_chalons"] = b.church(
        "Bishop of Chalons",
        church="Bishop's cathedral",
        order="secular clergy",
        place=champagne,
        summary=(
            "Lord of Chalons and a part of every coronation at Reims. The "
            "city's great churches are the pilgrim basilica of Notre-Dame, "
            "on the road to Compostela where a statue of the Virgin was "
            "found in a burning bush, and the new collegiate church of "
            "Notre-Dame-en-Vaux with its cloister of sixty statue-columns. "
            "The bishop owns the meadow south of the city where St. Bernard "
            "and Pope Eugene III preached."
        ),
    )
    w["st_ayoul"] = b.church(
        "Priory of St. Ayoul",
        church="Monastery or nunnery",
        order="Benedictine",
        place=champagne,
        summary=(
            "The eleventh-century Benedictine priory at the heart of "
            "Provins's lower town, where the relics of St. Ayoul were "
            "miraculously discovered."
        ),
    )
    w["bishop_of_troyes"] = b.church(
        "Bishop of Troyes",
        church="Bishop's cathedral",
        order="secular clergy",
        place=champagne,
        summary=(
            "The see of St. Lupus, who saved Troyes from Attila. Its "
            "cathedral quarter has hosted important Church councils in "
            "past centuries."
        ),
    )
    w["clairvaux"] = b.church(
        "Clairvaux Abbey",
        church="Monastery or nunnery",
        order="Cistercian",
        founded=1115,
        place=champagne,
        summary=paragraphs(
            "The clear valley, founded by St. Bernard in 1115, is among the "
            "greatest and most influential Cistercian houses in France, on "
            "the northern edge of Burgundy. Austere quadrangles of lodgings "
            "and workshops sit inside a strong wall with watchtowers; its "
            "300-foot church, a Latin cross, has no stained glass, carving "
            "or steeple. Gardens, orchards, a spring and carefully kept "
            "fishponds fill the precinct. The whole abbey has a Divine aura "
            "of 6.",
            "It is the model for many other Cistercian houses. Its workshop "
            "turns out a great many manuscripts, it has lately built an "
            "iron-smelting forge at Wassy, and it keeps a townhouse at "
            "Bar-sur-Aube. Eugene III, who became pope in 1145, had been a "
            "monk here.",
            "St. Bernard (1090 to 1153), a nobleman's son who entered "
            "Citeaux at twenty-one and founded Clairvaux at twenty-five, "
            "kept his monks on boiled vegetables, water and bare pallets; "
            "that they survived seemed a miracle, and the hard life drew "
            "followers. He rose to lead the Church of his day, preached the "
            "Second Crusade at Vezelay in 1146, prosecuted Abelard for "
            "heresy, and is the patron saint of farms and farmhands.",
        ),
    )
    w["cunfin_abbey"] = b.church(
        "Abbey of Cunfin",
        church="Monastery or nunnery",
        order="Cistercian",
        ruler="Abbot Martin",
        place=normandy.places["cunfin_site"],
        summary=paragraphs(
            "A plain Cistercian abbey in a deep valley of Champagne, "
            "close to the fair roads, whose monks keep open house for "
            "the many travellers. Its prior, Brother Eligius, is "
            "revered for his piety and wisdom, and the monks believe "
            "the holy hermit in the hills above blesses them twice "
            "over. Its abbot, Martin, is a man in middle age with "
            "considerable influence in the Cistercian Order.",
        ),
        secrets="Brother Eligius is Eloi of Jerbiton, and the abbey shares its "
        "valley with the covenant of Cunfin. Martin, the cellarer and a "
        "few brothers know and help the magi, and Martin uses his "
        "influence in the Order on their behalf.",
    )
    w["st_germanus_auxerre"] = b.church(
        "Abbey of St. Germanus, Auxerre",
        church="Monastery or nunnery",
        order="Benedictine",
        place=burgundy,
        summary=(
            "Auxerre's oldest house, a Benedictine abbey founded in the "
            "sixth century by Clotilda, wife of King Clovis. Beneath it a "
            "great Carolingian crypt painted with magnificent frescoes holds "
            "St. Germanus's tomb, a place of pilgrimage."
        ),
    )
    w["st_lazarus_avallon"] = b.church(
        "Church of St. Lazarus, Avallon",
        church="Large urban church",
        place=burgundy,
        summary=(
            "Avallon's pilgrim church, just over a hundred years old, "
            "keeping a piece of St. Lazarus's skull, a relic that grants "
            "divine protection against leprosy."
        ),
    )
    w["vezelay"] = b.church(
        "Abbey of Vezelay",
        church="Monastery or nunnery",
        order="Benedictine",
        place=burgundy,
        summary=paragraphs(
            "The Benedictine abbey keeping the relics of St. Mary "
            "Magdalene, Burgundy's greatest pilgrimage since the "
            "eleventh century and the start of a main road to "
            "Compostela. St. Bernard preached the Second Crusade here, "
            "Philip II and Richard the Lionheart met here before the "
            "Third, and the exiled Thomas Becket excommunicated Henry "
            "II's supporters here in 1166.",
            "Founded by Gerard de Roussillon and destroyed by the "
            "Normans in the ninth century, it was rebuilt on a hilltop "
            "on the edge of the Morvan. Its history is chequered: "
            "peasants killed the abbot over taxes for a larger church "
            "in 1096, and in 1120 the new church burned on the feast of "
            "the great pilgrimage, 22 July, with a thousand pilgrims "
            "inside. The Basilica of St. Mary Magdalene has since been "
            "rebuilt.",
        ),
        secrets="The relics' origin is unclear: one story says St. Badilo "
        "brought them from the Holy Land in the ninth century, another "
        "that the saint's tomb was found at St. Maximin in Provence, "
        "identified by a carving of the anointing at Bethany. The monks "
        "do not doubt them.",
    )
    w["bishop_of_autun"] = b.church(
        "Bishop of Autun (Cathedral of St. Lazarus)",
        church="Bishop's cathedral",
        order="secular clergy",
        place=burgundy,
        summary=(
            "One of the oldest sees of France. The cathedral of St. "
            "Lazarus at the south of the city keeps that saint's relics, "
            "brought from Provence in the tenth century by Gerard de "
            "Roussillon in a failed bid to rival Vezelay. It is the dukes' "
            "chapel, and the episcopal palace beside it was their seat "
            "before Dijon; the dukes were buried here until Citeaux."
        ),
    )
    w["bishop_of_langres"] = b.church(
        "Bishop of Langres",
        church="Bishop's cathedral",
        order="secular clergy",
        place=burgundy,
        summary=(
            "The bishops who now rule Langres, heirs of the martyr St. "
            "Didier, whose chapel marks where he died after riding off "
            "with his head in his hands."
        ),
    )
    w["st_benignus"] = b.church(
        "Abbey of St. Benignus, Dijon",
        church="Monastery or nunnery",
        order="Benedictine",
        place=burgundy,
        summary=(
            "The abbey church in Dijon whose crypt holds the tomb of St. "
            "Benignus, founder and patron of the city."
        ),
    )
    w["citeaux"] = b.church(
        "Citeaux Abbey",
        church="Monastery or nunnery",
        order="Cistercian",
        founded=1098,
        place=burgundy,
        summary=paragraphs(
            "The mother house of the Cistercians, founded in 1098 by Robert "
            "of Molesme, who left his lax abbey with twenty monks for a "
            "dreadful reedy swamp a dozen miles south of Dijon; the reeds "
            "gave the abbey its name. The monks drained it through great "
            "hardship, and under St. Bernard it flourished; it now mothers "
            "more than five hundred Cistercian houses across Europe.",
            "For all its sprawl of buildings it keeps its austerity, "
            "discipline and manual labour. Its great church, finished in "
            "1193, is the new burial place of the dukes of Burgundy. Since "
            "1147 the attached house of La Trappe has kept its monks in "
            "solemn contemplation.",
        ),
    )
    w["cluny"] = b.church(
        "Cluny Abbey",
        church="Monastery or nunnery",
        order="Cluniac",
        founded=910,
        place=burgundy,
        summary=paragraphs(
            "Founded in 910 by William I of Aquitaine, the most "
            "powerful monastery there has ever been: mother of a "
            "thousand Cluniac houses whose priors meet here every year, "
            "its abbot answering to the Pope alone. Closely tied to the "
            "papacy since the Gregorian reforms, it has given the "
            "Church several popes; Urban II called it the light of the "
            "world, and St. Bernard asked whether the light needed a "
            "golden candlestick. A little waned by the Cistercians' "
            "rise, it still arguably rivals Rome and leads western "
            "monasticism.",
            "It is everything Citeaux is not: wealth and splendour, "
            "with abbots who live like kings. Its abbey church of Sts. "
            "Peter and Paul, built under St. Hugh and Peter the "
            "Venerable, is the largest building in Christendom, nearly "
            "600 feet long with two transepts, four aisles and five "
            "belfries, lavishly adorned. Its library is among the "
            "richest in Europe, and the abbots keep a fine townhouse in "
            "Paris. Its Divine aura is strong (strength not given).",
        ),
        secrets="Optionally, dark powers may be working Cluny's slow "
        "corruption through the monks' love of luxury: servants of the "
        "Devil hidden in its hierarchy, Infernal auras pocketed inside "
        "the Divine one, or places where the Divine aura is weaker than "
        "it should be.",
    )
    w["pontigny"] = b.church(
        "Pontigny Abbey",
        church="Monastery or nunnery",
        order="Cistercian",
        place=burgundy,
        summary=(
            "A notable Burgundian abbey where Thomas Becket spent part of "
            "his exile from England."
        ),
    )
    w["fontenay"] = b.church(
        "Fontenay Abbey",
        church="Monastery or nunnery",
        order="Cistercian",
        place=burgundy,
        summary=(
            "A notable Burgundian abbey some six miles north of Mont "
            "Auxois and the ruins of Alesia."
        ),
    )
    w["molesme"] = b.church(
        "Molesme Abbey",
        church="Monastery or nunnery",
        order="Benedictine",
        place=burgundy,
        summary=(
            "The Benedictine abbey whose laxity drove its abbot Robert to "
            "leave with twenty monks in 1098 and found Citeaux."
        ),
    )


def _factions(normandy: Normandy, b: Builder) -> None:
    w = normandy.world
    champagne = normandy.places["champagne"]
    w["champagne_fairs"] = b.faction(
        "The Merchants of the Champagne Fairs",
        faction="Gild",
        decides="A council",
        wants="Safe roads, fair dealing and the count's protection for the fair cycle.",
        offers="Goods from Constantinople to Scotland, credit, and news from every road.",
        place=champagne,
        summary=paragraphs(
            "The six great fairs of the Champagne cycle (Provins and Troyes "
            "hold two apiece, Lagny and Bar-sur-Aube one each), with lesser "
            "fairs in other towns, are among the main meeting places of "
            "northern and southern trade: Flemish wool against Eastern "
            "spices and luxuries, with merchants from as far as "
            "Constantinople and Scotland. Their weight gave Troyes its own "
            "measure, the Troy ounce.",
        ),
    )
    w["fair_mercer_houses"] = b.faction(
        "The Temporary Mercer Houses of the Fairs",
        faction="Other",
        decides="Its leader",
        ruler="Hervé filius Évrard",
        wants="Profit, news and the Redcaps' standing at the fairs.",
        offers="Vis, books and Hermetic goods for sale, letters carried and news traded.",
        place=champagne,
        summary=paragraphs(
            "At most of the Champagne fairs Redcaps, organised mostly from "
            "Confluensis and Cunfin, put up temporary Mercer Houses, "
            "quietly trading vis, books and other Hermetic goods and "
            "swapping news and messages. Hervé le Brun of Cunfin has taken "
            "over their running from his father Évrard, a post his foster "
            "brother Renaud wanted.",
        ),
    )
    w["jews_of_troyes"] = b.faction(
        "The Jews of Troyes",
        faction="Family",
        decides="A council",
        ruler="",
        wants="The counts' continued protection.",
        offers="Learning, and copies of Rashi's commentaries.",
        place=champagne,
        summary=paragraphs(
            "A Jewish community settled at Troyes in the eleventh century "
            "under the counts' protection; there is another sizeable one at "
            "Provins. Its most famous son is Rabbi Shlomo Yitzhaki, Rashi "
            "(1040 to 1105), who studied at Worms and Mainz, came home at "
            "twenty-five, and wrote the great commentaries on the Tanakh "
            "and the Talmud, weaving literal reading with allegory and "
            "symbol. Copies are found in Troyes and other leading Jewish "
            "communities; each commentary is a Theology (Judaism) "
            "tractatus of Quality 13.",
        ),
    )
    w["priory_of_st_nerius"] = b.faction(
        "The Priory of St. Nerius",
        tradition="trad_priory_of_saint_nerius",
        faction="Other",
        realm="Divine",
        wants="St. Nerius recognised as a saint by the Latin Church.",
        offers="A bridge between the Magic and the Divine.",
        summary=(
            "Followers of St. Nerius, a holy man who reconciled Magic and "
            "the Divine, who seek his recognition by the Latin Church. Eloi "
            "of Cunfin is close to them without being a member, and rumour "
            "says Cunfin abbey was founded in 1136 by Valoran, Nerius's "
            "pupil. Realms of Power: The Divine describes them."
        ),
    )


def _vis(normandy: Normandy) -> None:
    """The vis sources the chapter places under the Perthean Compact."""
    normandy.tenure(
        "Cave of Sabinus: Aquam vis from the source of the Marne, by the "
        "genius loci's leave",
        None,
        "luctatio",
        notes=(
            "The spirit of the spring is notoriously hard to please, so the "
            "Tribunal leaves the source to any magus who dares."
        ),
    )
    normandy.tenure(
        "Atramentum Renatus: the source the covenant was built about",
        normandy.covenants["atramentum_renatus"],
        "seisin",
        notes=(
            "Formerly a legacy of Fudarus; Exspectatio gave it to Helios "
            "and Gulo as amends in 1201, and the covenant now stands by it. "
            "Its Art and yield are not given."
        ),
    )


# ---------------------------------------------------------------- stats


def _art(name: str, art: str) -> tuple[str, dict[str, str]]:
    return (name, {"art": art})


P = Profile
FRENCH = "French"

#: Each magus's generated-stats profile, by their key in `normandy.magi`.
PROFILES: dict[str, Profile] = {
    "eloi": P(
        strong="pre com",
        arts={"Me": 5, "Re": 3, "In": 3, "Cr": 2, "Co": 2},
        abilities={
            "Dominion Lore": (4, "the Cistercians"),
            "Charm": (3, "monks"),
            "Etiquette": (3, "the Church"),
            "Leadership": (2, "monks"),
            "Theology": 2,
            "Intrigue": (2, "Church politics"),
        },
        virtues=[
            "Gentle Gift",
            ("Social Contacts", {"group": "the Cistercian Order"}),
            "Pious (Major)",
            "Dark Secret",
        ],
        native=FRENCH,
    ),
    "angelus": P(
        strong="per int",
        weak="pre",
        arts={"Me": 4, "In": 4, "Vi": 3, "Cr": 2, "Te": 2},
        abilities={
            "Dominion Lore": (4, "saints"),
            "Theology": 3,
            "Magic Lore": (2, "regiones"),
            "Survival": 1,
        },
        virtues=[
            "Sense Holiness and Unholiness",
            "Pious (Major)",
            "Reclusive",
        ],
        native=FRENCH,
    ),
    "celeres": P(
        strong="int pre com",
        arts={"In": 5, "Me": 4, "Im": 3, "Cr": 3, "Re": 3, "Vi": 3},
        abilities={
            "Area Lore: Britain": (3, "Arthurian sites"),
            "Faerie Lore": (3, "Breton tales"),
            "Dominion Lore": (2, "the Grail"),
            "Living Language: Breton": 3,
            "Living Language: Welsh": 2,
            "Profession: Scribe": 3,
            "Charm": 2,
        },
        virtues=[
            "Gentle Gift",
            "Well-Traveled",
            "Obsessed (Major)",
            "Poor Memory",
        ],
        native=FRENCH,
    ),
    "artorius": P(
        strong="pre str",
        arts={"Cr": 3, "Re": 3, "Im": 2, "Ig": 2},
        abilities={
            "Single Weapon": (2, "sword"),
            "Ride": 2,
            "Etiquette": (2, "nobles"),
            "Leadership": 1,
            "Area Lore: Britain": 1,
        },
        virtues=[
            "Gentle Gift",
            "Dutybound",
            "Proud (Minor)",
            "Orphan",
            "Covenant Upbringing",
        ],
        native=FRENCH,
    ),
    "evrard": P(
        gifted=False,
        strong="sta per",
        native=FRENCH,
        abilities={
            "Ride": (4, "long journeys"),
            "Area Lore: Normandy Tribunal": (4, "covenants"),
            "Organization Lore: Order of Hermes": (4, "Redcaps"),
            "Dead Language: Latin": 4,
            "Bargain": 3,
            "Folk Ken": 3,
            "Code of Hermes": 3,
            "Leadership": 2,
        },
        virtues=[
            "Redcap",
            "Well-Traveled",
            "Proud (Minor)",
            "Dutybound",
            "Wrathful (Minor)",
            "Poor Hearing",
        ],
    ),
    "renaud": P(
        gifted=False,
        age=33,
        strong="int com",
        native=FRENCH,
        abilities={
            "Carouse": (4, "drinking"),
            "Music": (3, "singing"),
            "Dead Language: Latin": 5,
            "Artes Liberales": 3,
            "Ride": 3,
            "Area Lore: Normandy Tribunal": 2,
            "Organization Lore: Order of Hermes": 2,
        },
        virtues=[
            "Redcap",
            "Clear Thinker",
            "Carefree",
            "Rebellious (Minor)",
            "Lecherous (Minor)",
            "Reckless (Minor)",
        ],
    ),
    "helios": P(
        age=38,
        strong="int pre",
        arts={"Vi": 5, "Me": 4, "Co": 3, "In": 3, "Re": 2},
        abilities={
            "Magic Lore": (3, "spirits"),
            "Intrigue": 2,
            "Area Lore: Burgundy": 2,
        },
        virtues=[
            "Hermetic Theurgy",
            "Reckless (Minor)",
        ],
        native="Breton",
    ),
    "gulo": P(
        age=37,
        strong="sta str",
        arts={"An": 5, "Mu": 4, "Co": 3, "Re": 2},
        abilities={
            "Heartbeast": (4, "the wolverine"),
            "Survival": (2, "forests"),
            "Hunt": 2,
            "Animal Ken": 1,
        },
        virtues=[
            "Wilderness Sense",
            "Wrathful (Minor)",
        ],
        native="Breton",
    ),
    "iacula": P(
        age=40,
        strong="int dex",
        arts={"Re": 6, "Te": 4, "Ig": 3, "Cr": 2},
        abilities={
            "Finesse": (4, "aiming"),
            "Magic Theory": (4, "inventing spells"),
            "Penetration": 3,
        },
        virtues=[
            "Inventive Genius",
            _art("Affinity with {art}", "rego"),
            "Obsessed (Minor)",
            "Weak Parens",
        ],
        native="Italian",
    ),
    "philip": P(
        age=45,
        strong="per pre",
        arts={"Me": 5, "Pe": 4, "Re": 3, "In": 3, "Co": 2},
        abilities={
            "Magic Lore": (3, "ghosts"),
            "Dominion Lore": 2,
            "Folk Ken": 2,
        },
        virtues=[
            "Second Sight",
            "Compassionate (Minor)",
        ],
        native=FRENCH,
    ),
}

#: The apparent ages the book gives, which the generator leaves alone.
APPARENT = {"eloi": 52, "angelus": 75, "celeres": 100, "artorius": 33, "evrard": 49}

HERVE: StatBlock = {
    "characteristics": {
        "intelligence": 0,
        "perception": 2,
        "presence": 2,
        "communication": 1,
        "strength": 0,
        "stamina": 0,
        "dexterity": 0,
        "quickness": 0,
    },
    "size": 0,
    "confidence": (1, 3),
    "decrepitude": (0, 0),
    "warping": (0, 0),
    "apparent_age": 35,
    "virtues_flaws": [
        "Redcap",
        "Clear Thinker",
        "Educated",
        "Gossip",
        "Piercing Gaze",
        ("Social Contacts", {"group": "merchants"}),
        "Ambitious (Major)",
        "Busybody",
        "Envious (Minor)",
    ],
    "traits": {"Driven": 3, "Jealous": 2},
    "reputations": {"Capable (Hermetic)": 3, "Gossip (Hermetic)": 3},
    "abilities": [
        ("Bargain", 5, "appraisal"),
        ("Brawl", 2, "dodging"),
        ("Charm", 5, "building trust"),
        ("Code of Hermes", 3, "political intrigue"),
        ("Etiquette", 3, "merchants"),
        ("Area Lore: France", 3, "trade routes"),
        ("Living Language: French", 5, "mercantile"),
        ("Folk Ken", 5, "merchants"),
        ("Guile", 2, "redirection of blame"),
        ("Intrigue", 5, "gossip"),
        ("Dead Language: Latin", 5, "academic usage"),
        ("Organization Lore: Order of Hermes", 4, "politics"),
    ],
    "notes": (
        "Equipment: a set of enchanted devices for a trading Redcap, with "
        "the effects Scales of the Magical Weight (InVi 5), Sense the "
        "Nature of Vis (InVi 5), Posing the Silent Question (InMe 20) and "
        "Trust of the Childlike Faith (PeMe 10), each at Penetration 0 "
        "with 24 uses a day. Combat: dodging, Initiative 0, Defense +3; "
        "Soak +0. Encumbrance 0."
    ),
}


def stats(normandy: Normandy) -> None:
    """Hervé's printed stat block, then generated stats for every other
    magus of the region, with the apparent ages the book gives."""
    b = normandy.b
    b.stats(normandy.magi["herve"], HERVE)
    for key, profile in PROFILES.items():
        apply(b, normandy.magi[key], profile)
    for key, apparent in APPARENT.items():
        normandy.magi[key].aging.apparent_age = apparent
