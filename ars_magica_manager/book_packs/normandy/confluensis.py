"""Confluensis, the Praeco's covenant, as of spring 1220: its marsh site
in the Cotentin and the Orchard island, the covenant and its six living
magi, its library with the books it keeps for the Tribunal, its vis, the
chapter's saga seeds, and its Mercer House vassal Dragon's Rest on the
Seine, in paraphrase of The Lion and the Lily, chapter eleven. The book
prints no stat block for anyone here, so every magus gets a generated
profile."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...tribunal_packages.normandy import LIBRARY_HELD
from ..builder import joined_lines, paragraphs, titled, vf_ability, vf_art
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Covenant, Tribunal
    from ..builder import Builder
    from . import Normandy

# House ids, so a typo cannot slip into a record.
GUERNICUS = "house_guernicus"
JERBITON = "house_jerbiton"
MERCERE = "house_mercere"
TYTALUS = "house_tytalus"

# The lead line of a covenant's notes, before its secrets.
# Where the Tribunal's own books are kept.
HELD = LIBRARY_HELD


def build(normandy: Normandy) -> None:
    b = normandy.b
    tribunal = normandy.tribunal
    assert tribunal is not None
    _places(normandy, b)
    confluensis = _confluensis(normandy, b, tribunal)
    _magi(normandy, b, confluensis)
    _library(b, confluensis)
    _tribunal_library(b, confluensis)
    _vis(normandy, confluensis)
    _dragons_rest(normandy, b, tribunal)


# ------------------------------------------------------------------ places


def _places(normandy: Normandy, b: Builder) -> None:
    p = normandy.places
    p["cotentin_marshes"] = b.place(
        "The Cotentin marshes",
        inside=normandy.places.get("cotentin"),
        summary=(
            "More than 2,500 acres of brackish, untamed swamp that all but "
            "cut the Cotentin peninsula off from the rest of Normandy, so "
            "that people call it an island. With no good roads across, the "
            "peninsula is thinly peopled and holds no great lordships, and "
            "outsiders seldom bother with it. Confluensis lies hidden in "
            "the tidal reaches, where the rivers meet the sea; strangers "
            "crossing the fens risk the fen ague, a fever Hermetic magic "
            "can cure. The marsh's own aura is not given."
        ),
    )
    p["confluensis_site"] = b.place(
        "The Confluence",
        inside=p["cotentin_marshes"],
        status="Claimed",
        tethers="The tide, where fresh river water turns back the salt",
        summary="The site of Confluensis, in the swamp's tidal zone at the very "
        "middle of the band where the rivers' fresh, fertile water "
        "pushes back the barren salt. Under the covenant's raised "
        "floors creation and destruction wrestle with every tide, and "
        "on spring tides they spin up dancing whirlpools that the magi "
        "catch in enchanted nets for vis. The book calls the Magic "
        "aura powerful but gives no score. A ring of magical mist and "
        "contrary currents hides the place: the covenfolk learn the "
        "currents' usual pattern, which a device in the council "
        "chamber can change; the watch carry items that see through "
        "the mist and the turb captain one that thickens or thins it; "
        "and a ring of active defences, which the magi say they change "
        "often, lies beyond.",
        secrets=[
            titled(
                "Why the covenant is built on the tide",
                "One of Confluensis's founders had a flaw in her Gift that made "
                "building on the tide necessary; only a few magi know it.",
            ),
        ],
    )
    p["the_orchard"] = b.place(
        "The Orchard",
        inside=normandy.places.get("cotentin"),
        status="Claimed",
        summary=(
            "An island north-east of Coutances where many of Confluensis's "
            "covenfolk live, taken from a faerie court soon after the site "
            "was settled because of its aura and its vis. Its trees bear "
            "small, sour apples full of Intellego vis. Folk say that when "
            "a virgin peels one with her left hand the peel forms her "
            "future husband's initial, and its taste foretells how sweet "
            "the marriage will be, but the hedge wizards who knew the "
            "custom could not write it down and the magi will not waste "
            "the vis. The island's Faerie aura has slowly turned to Magic "
            "(its score is not given), though a weak Faerie aura returns "
            "at each solstice. The Orchard of Sour Apples, the vassal "
            "covenant whose site Confluensis took over in 1051, was named "
            "for it."
        ),
    )
    normandy.world["city_of_god"] = b.church(
        "The Hospitallers' City of God",
        church="Hospital",
        order="Knights Hospitaller",
        place=p["cotentin_marshes"],
        summary=(
            "A new Hospitaller settlement near Confluensis, meant to grow "
            "into a City of God: a perfect town ruled by the Church, where "
            "everyone is devout and sin does not happen. For now it is a "
            "grant of land and a hospital kept by three elderly knights "
            "of the Order. In effect a small monastery, it has a Dominion "
            "aura of 4. The knights often have True Faith or relics, are "
            "sworn to obey their Order's master, and are so pious that "
            "moving against them may draw demons to help in secret. Many "
            "such cities fail and end as homes for old crusaders, who "
            "could train grogs and may have fought djinn, demons and "
            "faeries. Confluensis wants it gone from the peninsula, but "
            "must set no precedent other covenants could abuse."
        ),
    )
    p["st_giles_statue"] = b.place(
        "The statue of St. Giles",
        inside=normandy.places.get("cotentin"),
        realm="Divine",
        known="Locally",
        summary=(
            "A statue of St. Giles in the Cotentin that local people use "
            "as a fertility charm. It has been given a large phallus, from "
            "which they shave slivers of wood for a healing drink, and "
            "they say the wood grows back by a miracle. That may be God "
            "at work in a way the Church does not teach, a demon or "
            "faerie using the statue, or a magical device. A phallic saint "
            "is heresy, and the Hospitallers nearby may call in the "
            "preaching friars if they hear of it. Its realm and aura are "
            "not given."
        ),
    )


# ------------------------------------------------------------- Confluensis


def _confluensis(normandy: Normandy, b: Builder, tribunal: Tribunal) -> Covenant:
    summary = paragraphs(
        "The Covenant of the Confluence is the largest Quaesitorial "
        "covenant in Normandy, home of the Tribunal's Praeco and its "
        "Presiding Quaesitor, hidden in the marshes of the Cotentin. Since "
        "the Tribunal is a turbulent one, its members are mostly "
        "investigators and hoplites. Its buildings stand on huge stone "
        "flowers, meant to show both growth and stability. It sits where "
        "fresh water meets salt, and its purpose is the same kind of "
        "balance: keeping the peace among the covenants of Normandy. To "
        "that end it keeps vassals: the lesser Guernicus covenants of the "
        "Tribunal (one of them two magi, a Quaesitor and a hoplite, whose "
        "site each saga places for itself), Cunfin in Champagne, and "
        "Dragon's Rest, a Mercer House on the Seine. It has just lost its "
        "leader, and whether it is still strong enough for its role is "
        "an open question.",
        "Guernicus himself ordered the covenant founded, in 810, to see "
        "Hermetic law kept at the Order's edges. It first stood in the "
        "lair of the dragon Gargouille, in the swamps between Rouen and "
        "the Seine's mouth, and in time took in a Mercer House. Diedne "
        "magi sacked it in the Schism War; three members who were away "
        "elsewhere in the Tribunal survived and rebuilt it. After the war "
        "the Primus of Guernicus enlarged it, and with ever more traffic "
        "on the Seine it grew too big to stay unnoticed. In 1051 it took "
        "over its own vassal, the Orchard of Sour Apples, in the "
        "Cotentin, absorbing its magi. The Mercere magi stayed behind as "
        "Dragon's Rest, keeping the old badge of a dragon spouting water; "
        "Confluensis took a stylised whirlpool. The two remain close, "
        "each using the other's laboratories and library. Confluensis has "
        "always served the Primus of Guernicus as the House's mustering "
        "point and supply base in a crisis, and it helped bring down "
        "Tasgillia, the diabolist Prima of Tytalus.",
        "Its central buildings were shaped by magic, whimsically, on "
        "platforms that are single pieces of stone grown into flowers, "
        "which makes some think Terram magi of House Guernicus's Terrae "
        "cult settled it. The rest look like dressed granite, like that "
        "of Mont St. Michel; some were built by masons and some only "
        "made to look that way. The Sundew carries most of them: five "
        "great pads, each ringed with stone globes joined to it by "
        "covered walkways, linked by stems to a six-storey stone spike "
        "with a lookout on top, which the magi have begun carving with "
        "the covenant's history in the manner of Trajan's column. The "
        "western pad holds the Great Hall, with dining and drill space "
        "below, stores and offices on a mezzanine, and a pulley that "
        "lifts cargo from the covenant's lighters; eighteen houses for "
        "guests and senior staff stand around it. Clockwise come the Pad "
        "of Gatherers (food: seafood and chestnuts, a mill, granary, "
        "brewery and bakery), the Pad of Crafters (potters using clays "
        "from all over the swamp, and paper made from papyrus reeds that "
        "Quaesitors brought in and spread by magic), the Pad of Parades "
        "(festivals, games, the Aegis rite and often the Tribunal "
        "itself), and the Furled Pad, too narrow to live on, where the "
        "boats moor.",
        "West of the Sundew the Bell Flower holds the magi's eight "
        "two-storey houses on its petals around an ornamental lake, with "
        "a stone disc on three stamens that is formally the council "
        "chamber but too awkward to reach without flying. South of it "
        "the square, three-storey Library Tower, the oldest building, "
        "rises straight from the ground, raised by a ritual meant for "
        "another site: its bottom floor is flooded and silting up, the "
        "second is the real council chamber, bridged to the Bell Flower, "
        "the top holds the library and the magical stores, and the roof "
        "serves sentries, ceremonies and the odd signal fire. A Mercere "
        "Portal to Dragon's Rest is here too.",
        "The covenfolk are the last of the Venelli, the Celtic tribe "
        "whose capital was Coutances, conquered and settled by Rome. Most "
        "entered the Order's service when the Normans burned their town "
        "in 998. Once pagans, whose last king took the boar as his sign, "
        "they lost their own magic first to Rome and then to House "
        "Guernicus, after a pagan sympathiser helped House Diedne in the "
        "Schism War. Today they live by serving the magi, trading at "
        "times in the ports of southern England, with no part left in "
        "Norman life. Their tongue is close enough to Breton to be "
        "understood but has its own accent and turns of phrase, and most "
        "also speak Norman French or English. Few have been soldiers, but "
        "they know the marsh well enough to be dangerous guerrillas. They "
        "wear bright woollens dyed with herbs and minerals, from wool "
        "bought in England, and have sometimes been taken for faeries.",
        "The Quaesitors here are known for deep knowledge of Hermetic law "
        "and for practical answers, and Presiding Quaesitors from here "
        "have been merciful when they could be and hard when they had "
        "to be. Renita of Bjornaer, Praeco and leader of the covenant, "
        "died last winter. Proctor, the ruthless Presiding Quaesitor, "
        "has taken over the covenant, but who will be Praeco is still "
        "open. Before her death Proctor, Jerome of Confluensis and Eloi "
        "of Cunfin were the three supports of her rule; the three now "
        "see themselves as what keeps the Tribunal from chaos. The "
        "covenant also houses the Traitor of House Tytalus, a volunteer "
        "exile from that House who is reckoned to have lost all its "
        "games and whose one duty is to start its quarrels again when "
        "they stall.",
    )
    what_matters = joined_lines(
        "Vis: whirlpools spun up by the spring tides beneath the covenant, caught in enchanted nets (seisin; Art and amount not given)",
        "Vis: Intellego in the sour apples of the Orchard island (seisin; amount not given)",
        "Vis: a tithe from Dragon's Rest of one pawn a year for each of its members",
        "Vis: Dragon's Rest and its other vassals tithe as their oaths require",
        "Library: the covenant's own library in the Library Tower, and the Library of the Tribunal, lent only as Tourney prizes",
        "Income: the Venelli covenfolk's crafts (pottery, papyrus paper, rope and flax) and trade with the southern English ports",
        "Income: great influence over the shipping companies that carry Paris's food down the Seine, and friends on the University of Paris's law faculty",
        "Boon: Difficult Access (the ring of mist and shifting currents)",
        "Boon: Defensive Environment (the tidal marsh, and a ring of active defences)",
        "Boon: Mystical Portal (the Mercere Portal to Dragon's Rest)",
        "Boon: Favors Owed (liege of Dragon's Rest, Cunfin and a small Guernicus covenant)",
        "Hook: Protector (owes its vassals support and protection under its oath)",
        "Hook: House Covenant (it serves the policies of the Primus of Guernicus)",
        "Hook: Hermetic Services (the Tribunal's Quaesitors, its law and its book store)",
        "Hook: Indigenes (the Venelli, last of a Celtic tribe)",
        "Tension: the Praeco is dead; the eldest magus would be Celeres of Cunfin, whom Proctor wants set aside",
        "Tension: Proctor's hatred of House Tytalus, with a Tytalus Traitor under his roof",
        "Tension: Cavillor advises the pro-Lotharingian faction, which Proctor will take as betrayal",
        "Tension: a Fengheld chapter house magus at Cherbourg takes vis Confluensis has always gathered",
        "Tension: the Hospitallers' City of God, with a Dominion aura of 4, on the peninsula",
    )
    sagas = joined_lines(
        "Sagas: eight starting points the book gives for a Confluensis saga.",
        "- The Praeco is Dead, Long Live the Praeco: the players work for "
        "Proctor, who cannot be seen to take sides, to settle the "
        "succession before the next Tribunal a little over a year away. "
        "Stellatus, the eldest, has left for Iberia; next come Celeres of "
        "Cunfin, then Somnifer of Lapis Crudus or Geirlaug of Montverte, "
        "each a problem. Proctor wants a Praeco he can trust or control; "
        "many would rather see his power checked.",
        "- Riches and Vis: as Confluensis's agents before the Grand "
        "Tribunal of 1228, the players fight the Lotharingian Tribunal, "
        "whose loss would leave Tytalus-held Brittany out-producing the "
        "rest of Normandy in vis; or they found the 'new law' there, a "
        "Quaesitorial covenant and Mercer House on a site Confluensis has "
        "already scouted.",
        "- The Haunted Woods of Broceliande: Confluensis backs a new "
        "covenant in Brittany against Tytalus influence; the players are "
        "its magi or its senior sponsors, and faeries and magi alike "
        "harry it, as they have every covenant tried there.",
        "- The Specter of Rome: the players keep the Order's uneasy peace "
        "with the Church as the Dominicans and the Papal letter of "
        "inquisition turn from the Cathars, which Jerome and Eloi fear "
        "will come north; troubleshooters or envoys, with enemies on both "
        "sides.",
        "- City of God: remove the Hospitallers' settlement from the "
        "Cotentin without breaking the Code or setting a precedent, or "
        "win over its old knights.",
        "- The Strange Saint of Cotentin: find out what makes the statue "
        "of St. Giles regrow its wood before the Hospitallers do.",
        "- The Chapter of Cherbourg: a Fengheld chapter house magus at "
        "Cherbourg counts as a cenobite under the Peripheral Code, seeks "
        "recognition, takes Confluensis's vis and may gain housemates; "
        "skilled magi might break her from Fengheld and bring her under a "
        "local liege.",
        "- Young and In Charge: the players take the places of some of "
        "the covenant's magi, serve Proctor for a while, then lose him to "
        "murder or a lab accident; his replacement, a respected Quaesitor "
        "new to Normandy, leans on them to run the House's business.",
    )
    seed = (
        "Story seed, the Bud and the Venelli: after a night of portents a "
        "huge stone bud rises from the swamp, and a boar-headed faerie "
        "says the covenant stands on an old pact between the marsh powers "
        "and the Venelli, which the magi must now keep. The Venelli once "
        "drowned captured kings, later a pig crowned king and trussed in "
        "a set way, shown on the coins of their last king, who hired "
        "Jersey mercenaries against Caesar. Leads run to Jersey (wreckers, "
        "ghosts and ghost-gathering faeries), the ship of drowned souls "
        "leaving Le Havre each All Hallows' Night, a coin-collecting "
        "Jerbiton magus, or a demon holding a coin. Drowning a royal pig "
        "might bring Rego or Animal vis, a valerian flower whose chambers "
        "heal, a vis-scenting gift for the Venelli's new king, boar "
        "skinchangers, the watery ghosts of past boar kings, or a white "
        "lady sent as the marsh's envoy."
    )
    hidden = [
        titled(
            "Why Confluensis is built on the tide",
            "One of the founders had a flaw in her Gift that made building on the "
            "tide necessary.",
        ),
        titled(
            "Jerome's troublesome heirs",
            "Jerome secretly saves 'troublesome heirs' from murder with Mentem magic "
            "and hides them in monasteries and covenants, very likely against the "
            "Code; Eloi of Cunfin is his chief partner, and Proctor does not know.",
        ),
        titled(
            "Valerian's familiar",
            "Valerian's familiar is a spirit beyond Hermetic binding, so he must "
            "belong to a Mystery Cult, probably the Guernicus Terrae cult.",
        ),
        titled(
            "Augustina's cabal",
            "Augustina belongs to the Cabal of Frankish Gold, which works for the "
            "Lotharingian Tribunal; she thinks it will fail but wants to see how the "
            "Order reacts.",
        ),
        titled(
            "The Traitor's key",
            "The Traitor's key is thought to weaken the defences of Fudarus, or "
            "perhaps by now to be only a symbol.",
        ),
        titled(
            "The stone flowers",
            "The stone flowers were not made by Terram magi: they belong to an older "
            "pact between the marsh's faerie powers and the Venelli.",
        ),
    ]
    confluensis = b.covenant(
        "Confluensis",
        tribunal=tribunal,
        founded=810,
        place=normandy.places["confluensis_site"],
        summary=summary,
        what_matters=what_matters,
        notes=paragraphs(sagas, seed),
        secrets=hidden,
        season="Autumn",
    )
    normandy.covenants["confluensis"] = confluensis
    return confluensis


def _magi(normandy: Normandy, b: Builder, confluensis: Covenant) -> None:
    m = normandy.magi
    m["proctor"] = b.magus(
        "Proctor",
        covenant=confluensis,
        house=GUERNICUS,
        age=93,
        summary=(
            "Presiding Quaesitor of the Normandy Tribunal for its last two "
            "meetings and, since Renita's death, acting leader of "
            "Confluensis. Against his House's custom of rotating the post, "
            "he seems unlikely to let anyone else be chosen next time; his "
            "filius Aristarcus would follow him. Tytalus diabolists killed "
            "his grandparens, and his parens passed on a hatred of that "
            "House, so he deeply mistrusts the Tribunal's Tytalus magi. A "
            "strict upholder of the Code and a firm Transitionalist, he may "
            "yet be driven to extreme measures by his suspicion. He looks "
            "about sixty: weathered face, leathery hands, pale skin, a "
            "white beard and no moustache, and a favourite slate-green robe "
            "fastened with two crossed pins shaped as swan feathers, one "
            "lead and one ivory. His familiar is a sacred ibis from his "
            "wandering youth. His talisman is a brass fool's bell that "
            "jingles in his pocket; he believes it one of the bells Richard "
            "the Devil wore doing penance in Rome, and it is enchanted "
            "against the Infernal. Those he distrusts are not told, and "
            "many think he carries it as a reminder not to act the fool."
        ),
        traits={"Ruthless": 3, "Strict": 2, "Distrustful": 2},
    )
    m["aristarcus"] = b.magus(
        "Aristarcus",
        covenant=confluensis,
        house=GUERNICUS,
        age=52,
        summary=(
            "Filius of Proctor and the Tribunal's usual prosecutor, with "
            "unrivalled rhetoric. He does not share his parens's distrust "
            "of House Tytalus and leans Traditionalist, but the two are "
            "frequent allies in their faith in the law. A strong longevity "
            "potion keeps him looking barely thirty. He wears his blond "
            "hair to the waist and dresses in Parisian noble fashion, short "
            "of the absurd; with his firm views on non-interference this "
            "has started talk of noble, perhaps Merovingian, blood, which "
            "he hears as a charge of bias, one of the few things that "
            "angers him. His familiar is a swan and his talisman a sword."
        ),
        traits={"Focused": 2, "Garrulous": 2, "Aloof": 1},
    )
    m["cavillor"] = b.magus(
        "Cavillor",
        covenant=confluensis,
        house=GUERNICUS,
        age=43,
        summary=(
            "A younger Transitionalist from the Roman Tribunal who usually "
            "defends magi accused before the Tribunal: less practised than "
            "Aristarcus, but earnest and dogged for what he thinks right. "
            "Some of the pro-Lotharingian magi now retain him as legal "
            "adviser, which Proctor is likely to take as a personal "
            "betrayal. Clean-shaven, grey-eyed and black-haired, with dark "
            "skin he puts down to partly Arab forebears, he dresses plainly "
            "in brown. He is married and wears a plain, unenchanted ring. "
            "His talisman is a six-ounce iron weight, a Carolingian "
            "standard for market weights; he has no familiar."
        ),
        traits={"Energetic": 3, "Optimistic": 2, "Trusting": 1},
    )
    m["valerian"] = b.magus(
        "Valerian",
        covenant=confluensis,
        house=GUERNICUS,
        age=78,
        summary="Chief hoplite and enforcer of the Tribunal, the general the "
        "Praeco would trust to plan a Wizard's March. A known master "
        "of Terram, he is said, like Adanos Lutorum of Exspectatio, to "
        "belong to the Guernicus Terrae cult. Slow, methodical and "
        "relentless in a hunt, with blunt, physical ideas of justice. "
        "Dark-haired and black-eyed, with perfect teeth, he never "
        "smiles beyond a quick sideways twitch of the mouth; he wears "
        "the covenant's slate-green cloth and, on great occasions, the "
        "Tribunal's crimson-and-grey swirled sash of a standing "
        "hoplite, edged with leopard fur for his rank. His talisman is "
        "a five-foot steel mason's crowbar he walks with. His familiar "
        "is an invisible spirit that can move dozens of things at once "
        "and seems to fly, and often wears a crow's shape to look less "
        "strange. The covenfolk like him, since he leaves their doings "
        "alone; he gardens, his tools and methods have eased the "
        "gatherers' work, and he mends their homes with rituals.",
        secrets=[
            titled(
                "Valerian's familiar",
                "No Hermetic magus could bind such a familiar: Valerian is a Mystery "
                "Cult initiate, and the crow form hides it.",
            ),
        ],
        traits={"Indifferent": 3, "Deliberate": 2, "Reliable": 2},
    )
    m["jerome"] = b.magus(
        "Jerome",
        covenant=confluensis,
        house=JERBITON,
        age=87,
        summary="The Tribunal's chief go-between with the nobles of France and "
        "Flanders, and one of the three who held up Renita's rule, "
        "with Proctor and his own former apprentice Eloi of Cunfin. "
        "Son of a minor noble, he was left to die by an uncle greedy "
        "for his inheritance, found by a Redcap and nursed back by the "
        "Jerbiton magus who took him as apprentice. He loves chess, "
        "plays it indifferently, keeps many boards in his laboratory "
        "and plays by letter with far better players, who like him "
        "because he never resigns; they have agreed one day to seek "
        "the magic chessboard among the Treasures of Britain. He "
        "dresses like a preaching friar rather than a lord, carries a "
        "wand, and has a bearded vulture for familiar, its breast "
        "turned moss green by what it eats in the swamp.",
        secrets=[
            titled(
                "Jerome's troublesome heirs",
                "Jerome saves 'troublesome heirs', children likely to be killed for "
                "their birthright, convinces everyone they are dead with Mentem magic "
                "and places them in monasteries or covenants; now and then one is "
                "Gifted, as Artorius was.",
            ),
            titled(
                "Jerome and the Code",
                "He knows saving the heirs is very likely a breach of the Code. "
                "Proctor does not know.",
            ),
            titled(
                "Eloi and the network",
                "Eloi is his chief partner, and anyone in the network has a dark "
                "secret but a strong ally in Jerome.",
            ),
            titled(
                "How old the network is",
                "Jerome's network may be old: William the Bastard vanished for eight "
                "years as a child.",
            ),
            titled(
                "Storyguide Notes",
                "Anyone in Jerome's network has the Dark Secret Flaw.",
            ),
        ],
        traits={"Caring": 3, "Friendly": 2, "Modest": 2},
    )
    m["augustina"] = b.magus(
        "Augustina",
        covenant=confluensis,
        house=TYTALUS,
        age=46,
        summary="The Traitor of House Tytalus, trained from early "
        "apprenticeship for the role by the mater of Buliste, the "
        "Prima, and as a hoplite mostly by the previous Traitor. A "
        "Traitor volunteers for exile from the House, counts as having "
        "lost every contest she was in, and is beneath any Tytalus's "
        "notice as a rival; her one duty is to stir the House's "
        "contests back to life when they stall, and since Tasgillia's "
        "fall she has carried a magical key as her badge of office. "
        "The first Traitor, Promethea filia Kalliste, sat out the war "
        "on Tasgillia to restore the House if it fell, and became a "
        "hoplite and then a Quaesitor; Guernicus sometimes chooses "
        "Traitors as Quaesitors, and otherwise accepts them as "
        "hoplites. Augustina has spent most of her life in Normandy "
        "advising her covenant's leader on Tytalus games; given "
        "Proctor's feelings, she gets the riskiest, least trusted "
        "assignments. Small and assertive, black-haired and blue-eyed, "
        "she often looks tired and happy at once. Her familiar is a "
        "small ape; her talisman is a locket on a ribbon or a dagger, "
        "nobody knows which, as one is always wound round the other.",
        secrets=[
            titled(
                "Augustina's cabal",
                "She is a member of the Cabal of Frankish Gold, which works for the "
                "Lotharingian Tribunal.",
            ),
            titled(
                "Why Augustina joined",
                "She expects the Lotharingian Tribunal to fail but holds that "
                "discontented magi should be able to leave a Tribunal, and wants to "
                "see how the Order answers.",
            ),
        ],
        traits={"Concerned About House Tytalus": 3, "Carefree": 1},
    )


def _library(b: Builder, confluensis: Covenant) -> None:
    b.book(
        confluensis,
        "The library of Confluensis",
        "Other",
        description=(
            "The covenant's own library, on the top floor of the Library "
            "Tower beside the magical stores; the book calls it beautiful "
            "but names none of its books. Under the oath with Dragon's "
            "Rest, Redcaps may study here, and Confluensis has let other "
            "members of Dragon's Rest study too. Expect strength in the "
            "Code of Hermes, Intellego and the Tribunal's records; the "
            "covenant makes its own papyrus paper. Its vassals' oath gives "
            "them the right to copy from it."
        ),
    )


def _tribunal_library(b: Builder, confluensis: Covenant) -> None:
    """The Library of the Tribunal: books owned in common, kept here and
    lent for seven years as Tourney prizes, and read by no one else."""

    def held(
        name: str,
        kind: str,
        author: str,
        note: str,
        *,
        art: str = "",
        ability: str = "",
        level: int | None = None,
        quality: int | None = None,
    ) -> None:
        b.book(
            confluensis,
            name,
            kind,
            author=author,
            description=f"{HELD}. {note}",
            art=art,
            ability=ability,
            level=level,
            quality=quality,
        )

    held(
        "The Babble Within Thought",
        "Art Summa",
        "Hicuccus of Criamon",
        "Worth 23 Build Points.",
        art="Mentem",
        level=12,
        quality=11,
    )
    held(
        "The Dismal Itch",
        "Art Summa",
        "Azenis of Tytalus",
        "Worth 21 Build Points.",
        art="Corpus",
        level=10,
        quality=11,
    )
    held(
        "De Lapii",
        "Art Summa",
        "Jeremias filius Guernicus",
        "A Branch of the Arts (Covenants); worth 31 Build Points.",
        art="Terram",
        level=17,
        quality=14,
    )
    held(
        "Insights from Twilight",
        "Ability Summa",
        "Perpauca of Bonisagus",
        "One of the books whose gift began the Library, declared its first "
        "tomes in 1081; worth 28 Build Points.",
        ability="Magic Theory",
        level=6,
        quality=11,
    )
    held(
        "Mirrors of the Soul",
        "Art Summa",
        "Perpauca of Bonisagus",
        "One of the Library's first tomes; worth 28 Build Points.",
        art="Imaginem",
        level=12,
        quality=16,
    )
    held(
        "The Mole's Work",
        "Lab Text",
        "Adanos Lutorum of Tytalus",
        "Laboratory texts for three spells: Rock of Viscid Clay, Earth That "
        "Breaks No More and The Forgiving Earth. Worth 11 Build Points.",
        art="Terram",
    )
    held(
        "The Peril of Phoebos",
        "Tractatus",
        "Perpauca of Bonisagus",
        "One of the Library's first tomes; worth 11 Build Points.",
        art="Ignem",
        quality=11,
    )
    held(
        "The Primal Power",
        "Art Summa",
        "Peter of Uist",
        "Worth 26 Build Points.",
        art="Aquam",
        level=9,
        quality=17,
    )
    held(
        "Research Notes on Aegis of the Hearth",
        "Tractatus",
        "Notatus and others",
        "A tractatus on Mastery of Aegis of the Hearth, with a laboratory "
        "text for a twentieth-level version of the spell bound in. Worth "
        "15 Build Points.",
        quality=11,
    )
    held(
        "Subtle Knives",
        "Ability Summa",
        "Jacinda of Flambeau",
        "Worth 23 Build Points.",
        ability="Penetration",
        level=5,
        quality=8,
    )
    held(
        "Unveiling the Tempest",
        "Art Summa",
        "Daniel Tonatris",
        "Worth 20 Build Points.",
        art="Auram",
        level=8,
        quality=12,
    )
    b.book(
        confluensis,
        "The Library of the Tribunal",
        "Other",
        description=(
            f"{HELD}. Begun when Perpauca of Bonisagus, a century and a half "
            "ago, tired of her covenant hoarding her books and wrote for "
            "the whole Tribunal instead; others followed her. Its list of "
            "books and authors is public. Since 1081 its books are Tourney "
            "prizes: the winner has sole use of one for seven years under "
            "a Cow and Calf Oath (copies belong to the Tribunal) and must "
            "return it in good order before the next Tribunal; no one else "
            "may read them. A magus who gives the Library an original book "
            "may claim, early in the next prize-giving, the lease of one "
            "worth as many Build Points, settling rival claims by "
            "certamen. A pamphlet on each spine gives readers' comments, "
            "enough to judge its Quality and Level. The books recorded "
            "here are only a sample of the collection."
        ),
    )


def _vis(normandy: Normandy, confluensis: Covenant) -> None:
    normandy.tenure(
        "The tidal whirlpools beneath Confluensis",
        confluensis,
        "seisin",
        notes=(
            "Spun up on spring tides where fresh water meets salt and "
            "caught in enchanted nets; Art and yield not given."
        ),
    )
    normandy.tenure(
        "The sour apples of the Orchard",
        confluensis,
        "seisin",
        notes="Intellego vis in the island's apples; yield not given.",
    )


# ----------------------------------------------------------- Dragon's Rest


def _dragons_rest(normandy: Normandy, b: Builder, tribunal: Tribunal) -> None:
    site = b.place(
        "The lair of the Gargouille",
        inside=normandy.places.get("seine_basin"),
        status="Claimed",
        summary=(
            "A drowned cavern in the estuary swamps near the Seine's mouth, "
            "where the river bends on its north bank, once the lair of the "
            "dragon Gargouille, which rose from the river in the seventh "
            "century spewing floods until St. Romanus of Rouen stopped it "
            "with the sign of the cross and a condemned prisoner dragged it "
            "to Rouen to burn. Confluensis stood here from 810 to 1051; "
            "raided a dozen times in a century, its magi grew skilled in "
            "battle magic, and much of the Order's early guessing about the "
            "Order of Odin came from contacts here. Dragon's Rest holds it "
            "now. Its aura is not given."
        ),
    )
    normandy.places["dragons_rest_site"] = site
    summary = paragraphs(
        "A Mercer House and vassal of Confluensis on the old site of its "
        "liege, around the drowned cavern of the dragon Gargouille in the "
        "estuary swamps on the Seine's north bank. When Confluensis moved "
        "to the Cotentin in 1051 its Mercere magi stayed, and kept the old "
        "badge of a dragon spouting a fountain of water. It is the hub of "
        "the Tribunal's Mercere Portals, with gates to Cunfin, Confluensis "
        "and Harco among others, and its laboratories are excellent; "
        "members of Confluensis use them, and its Redcaps use Confluensis's "
        "library.",
        "Its covenfolk are few and live by trade. Many descend from the man "
        "who helped kill Gargouille, and the prisoners the clergy of Rouen "
        "pardon each year in St. Romanus's memory often take service here. "
        "It is home to the Evangelium, the Redcap officer who carries the "
        "Tourney results to every covenant, now Myrina. In 1123 the "
        "Tribunal found Pandion of Flambeau guilty of taking twelve horses, "
        "one of them magical, from that Redcap, and so robbing Antonin of "
        "Dragon's Rest of part of his magical power. How many Redcaps live here is "
        "not given.",
        "Its oath to Confluensis is long-winded but fairly even-handed, "
        "since Guernicus and Mercere are on good terms; its terms are in the notes.",
    )
    oath = joined_lines(
        "Each comes to the other's aid when a member of either faces Wizard's War.",
        "Each votes with the other at Tribunal, granting that un-Gifted Redcaps are loath to vote.",
        "Each offers membership to the other's magi if their covenant is destroyed.",
        "Each passes on as fast as it can any news that bears on the other's fortunes, so far as the duties of Quaesitors and Redcaps allow.",
        "Their trading ventures avoid competing where possible and help each other in hard times.",
        "Dragon's Rest pays Confluensis a tithe of one pawn of vis a year for each member.",
        "Dragon's Rest hosts Confluensis's magi who want its laboratories; Confluensis hosts Redcaps who want its library.",
    )
    what_matters = joined_lines(
        "Vis: pays a tithe of one pawn a year per member to Confluensis",
        "Income: trade by its covenfolk and the Mercere network",
        "Laboratories: excellent, shared with Confluensis",
        "Boon: Mystical Portal (hub of the Tribunal's Mercere Portals: Cunfin, Confluensis, Harco and others)",
        "Boon: Powerful Ally (Confluensis, its liege)",
        "Hook: Mercer House",
        "Hook: Beholden (the oath of fealty to Confluensis)",
        "Hook: Legendary Site (the Gargouille's lair, remembered by the clergy of Rouen)",
        "Tension: Rouen's clergy keep the Gargouille's memory, and a mob led by the archbishop with St. Romanus's shrine could be roused against magi near the city",
    )
    notes = paragraphs(
        "The oath of fealty to Confluensis, in its own terms:\n" + oath,
        "Story seed, Gargouille: townsmen are found dead near the covenant "
        "and the magi are blamed; Archbishop Robert names them the new "
        "Gargouilles and marches on them with the condemned prisoners and "
        "the shrine of St. Romanus (Faith 5). Harming him could bring a "
        "crusade against the Order in Normandy, and the magi may have been "
        "framed.",
    )
    dragons_rest = b.covenant(
        "Dragon's Rest",
        tribunal=tribunal,
        founded=1051,
        place=site,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        oath=oath,
    )
    normandy.covenants["dragons_rest"] = dragons_rest
    normandy.magi["myrina"] = b.magus(
        "Myrina",
        covenant=dragons_rest,
        house=MERCERE,
        age=None,
        summary=(
            "Redcap of Dragon's Rest and the Tribunal's Evangelium, the "
            "officer, always a Redcap, who travels to every covenant to "
            "report the Tourney's results. The book says nothing more of "
            "her."
        ),
    )


# ------------------------------------------------------------------ stats

P = Profile
FRENCH = "French"
NORMANDY = "Area Lore: Normandy Tribunal"


#: Each magus's profile, by the key it has in normandy.magi.
PROFILES: dict[str, Profile] = {
    "proctor": P(
        strong="int per pre",
        native=FRENCH,
        arts={"In": 6, "Me": 5, "Re": 4, "Vi": 4, "Pe": 3, "Cr": 2},
        abilities={
            "Code of Hermes": (6, "Peripheral Code"),
            "Intrigue": (3, "Tribunal politics"),
            "Leadership": (3, "Quaesitors"),
            "Infernal Lore": (2, "diabolists"),
            NORMANDY: 3,
            "Animal Ken": (1, "ibis"),
        },
        virtues=[
            vf_ability("Puissant {ability}", "code of hermes"),
            "Hermetic Prestige",
            "Strong-Willed",
            "Hatred (Major)",
            "Proud (Minor)",
            "Dutybound",
        ],
        reputations={"Presiding Quaesitor (Hermetic)": 4},
    ),
    "aristarcus": P(
        strong="com int pre",
        native=FRENCH,
        arts={"In": 5, "Me": 5, "Cr": 3, "Co": 3},
        abilities={
            "Code of Hermes": (5, "prosecution"),
            "Civil and Canon Law": 2,
            "Etiquette": (2, "nobility"),
            "Intrigue": 2,
            NORMANDY: 2,
        },
        virtues=[
            "Gift of Speech",
            vf_ability("Affinity with {ability}", "code of hermes"),
            "Proud (Minor)",
            "Wrathful (Minor)",
        ],
        reputations={"Tribunal prosecutor (Hermetic)": 3},
    ),
    "cavillor": P(
        strong="com int sta",
        native="Italian",
        arts={"In": 5, "Me": 4, "Re": 3, "Te": 2},
        abilities={
            "Code of Hermes": (4, "defence"),
            "Civil and Canon Law": 2,
            "Folk Ken": 2,
            NORMANDY: 1,
            "Area Lore: Roman Tribunal": 2,
        },
        virtues=[
            "Self-Confident",
            "Tough",
            "Optimistic (Minor)",
            "Gullible",
        ],
    ),
    "valerian": P(
        strong="sta int str",
        native=FRENCH,
        arts={"Te": 8, "Re": 5, "Pe": 4, "Cr": 3, "Mu": 3, "In": 2, "Vi": 2},
        abilities={
            "Code of Hermes": 3,
            "Single Weapon": (3, "crowbar"),
            "Hunt": (3, "magi"),
            "Profession: Gardener": 2,
            "Leadership": (2, "hoplites"),
            NORMANDY: 3,
        },
        virtues=[
            vf_art("Affinity with {art}", "terram"),
            vf_art("Puissant {art}", "terram"),
            "Spirit Familiar",
            "Secretive",
            "Dutybound",
            "Driven (Minor)",
        ],
        reputations={"Chief hoplite of Normandy (Hermetic)": 4},
    ),
    "jerome": P(
        strong="pre com int",
        native=FRENCH,
        arts={"Me": 7, "Im": 4, "In": 4, "Cr": 3, "Re": 3, "An": 2},
        abilities={
            "Etiquette": (4, "nobility"),
            "Charm": (3, "nobles"),
            "Intrigue": (3, "French courts"),
            "Area Lore: France": 2,
            NORMANDY: 2,
            "Animal Ken": (1, "vultures"),
        },
        virtues=[
            "Gentle Gift",
            ("Social Contacts", {"group": "the nobility of France and Flanders"}),
            "Dark Secret",
            "Compassionate (Minor)",
            "Higher Purpose (Minor)",
        ],
        reputations={"Envoy to the nobility (Hermetic)": 3},
    ),
    "augustina": P(
        strong="pre int dex",
        native=FRENCH,
        arts={"Re": 5, "Pe": 4, "Me": 4, "Ig": 3, "In": 3},
        abilities={
            "Intrigue": (4, "House Tytalus"),
            "Guile": 3,
            "Single Weapon": (3, "dagger"),
            "Code of Hermes": 3,
            "Organization Lore: House Tytalus": 3,
            NORMANDY: 2,
        },
        virtues=[
            "Self-Confident",
            "Warrior",
            "Dutybound",
            "Outsider (Minor)",
            "Enemies",
        ],
        reputations={"The Traitor of House Tytalus (Hermetic)": 4},
    ),
    "myrina": P(
        gifted=False,
        age=40,
        strong="per com sta",
        native=FRENCH,
        abilities={
            "Ride": (3, "long journeys"),
            NORMANDY: (4, "covenants"),
            "Area Lore: Rhine Tribunal": 0,
            "Organization Lore: Order of Hermes": 3,
            "Code of Hermes": 2,
            "Dead Language: Latin": 3,
            "Folk Ken": 2,
            "Bargain": 2,
        },
        virtues=[
            "Redcap",
            "Dutybound",
            "Busybody",
            "Driven (Minor)",
        ],
        reputations={"Evangelium of the Tourney (Hermetic)": 3},
    ),
}

#: The apparent ages the book gives, which the magi's longevity keeps
#: below their years.
APPARENT_AGES: dict[str, int] = {
    "proctor": 60,
    "aristarcus": 32,
    "cavillor": 35,
    "valerian": 45,
    "jerome": 50,
    "augustina": 36,
}


def stats(normandy: Normandy) -> None:
    """Stat every magus of Confluensis and Dragon's Rest from a profile,
    since the book prints no stat block for any of them."""
    for key, profile in PROFILES.items():
        character = normandy.magi[key]
        apply(normandy.b, character, profile)
        if key in APPARENT_AGES:
            character.aging.apparent_age = APPARENT_AGES[key]
