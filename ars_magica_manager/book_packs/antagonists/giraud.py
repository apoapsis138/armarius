"""Baron Giraud Le Cornu (Antagonists pp. 24-36), in paraphrase.

The baron is a full character, with his household as sketches: the book
prints only their ages and traits. His barony, his unnamed overlord and his
keep are records, and the retainers and the agents are factions. His diary and
his false relics are items. The plots are one dormant threat, whose stages
come in the book's order, though it says the next step depends on what the
magi do. The book's court, treaty and Tribunal rules have no home in the app,
so they are the threat's secrets, cited by page.

The barony's name is this pack's label: the book names only the family."""

from __future__ import annotations

from ... import storage
from ...models import Book, Character, Neighbour
from ..builder import (
    Builder,
    StatBlock,
    characteristics,
    dormant,
    paragraphs,
    secrets,
)

BARON = "Baron Giraud Le Cornu"
HENRI = "Brother Henri Raoullin"
ANTAGONIST = BARON
TRACK = "A track"
S = Builder.stage

_BLOCK: StatBlock = {
    "characteristics": characteristics(1, 0, 2, 1, 1, 2, 1, 0),
    "size": 0,
    "confidence": (1, 3),
    "decrepitude": (0, 0),
    "virtues_flaws": [
        "Landed Noble",
        "Knight",
        "Wealthy",
        "Improved Characteristics",
        "Privileged Upbringing",
        ("Protection", {"protector": "the count"}),
        "Hatred (Major)",
        "Oath of Fealty",
        "Pious (Minor)",
    ],
    "traits": {
        "Hates Rebels": 6,
        "Brave": 3,
        "Pious": 3,
        "Calculating": 2,
        "Loyal": 2,
    },
    "reputations": {"Hates Rebels (local)": 2},
    "abilities": [
        ("Animal Handling", 3, "horses"),
        ("Area Lore: Own Barony", 4, "personalities"),
        ("Artes Liberales", 2, "arithmetic"),
        ("Bows", 3, "short bow"),
        ("Charm", 3, "first impressions"),
        ("Church Lore", 2, "relics"),
        ("Civil and Canon Law", 2, "property law"),
        ("Etiquette", 4, "court"),
        ("Folk Ken", 4, "nobles"),
        ("Living Language: French", 5, "Norman"),
        ("Great Weapon", 3, "long spear"),
        ("Hunt", 4, "wild boar"),
        ("Intrigue", 4, "alliances"),
        ("Dead Language: Latin", 3, "ecclesiastic"),
        ("Leadership", 5, "armies"),
        ("Organization Lore: Nobles", 4, "politics"),
        ("Ride", 4, "battle"),
        ("Single Weapon", 5, "long sword"),
        ("Theology", 1, "liturgy"),
    ],
    "notes": paragraphs(
        "Combat (Ant p. 25). Lance and Heater, mounted: Init 0, Attack +16, "
        "Defense +14, Damage +6. Long sword and Heater, mounted: Init 0, Attack "
        "+14, Defense +13, Damage +7. Long sword and Heater, dismounted: Init "
        "0, Attack +11, Defense +10, Damage +7. Long sword, dismounted: Init 0, "
        "Attack +11, Defense +7, Damage +7. Soak +11. Fatigue Levels: OK, 0, "
        "-1, -3, -5, Unconscious. Wound Penalties: -1 (1-5), -3 (6-10), -5 "
        "(11-15), Incapacitated (16-20), Dead (21+). Encumbrance 3 (4).",
        "Equipment: warhorse (courser), full chain mail, heater shield, lance, "
        "long sword, a diary, and several relics.",
        "Tall and fair, clean shaven, his hair cropped to sit under a helmet, "
        "with a keen and measuring look. His clothes are good and a little "
        "old-fashioned. He weighs his words, and speaks like a man used to "
        "being obeyed.",
        "He holds Hatred (Major) against rebels. The block prints Intrigue and "
        "Ride as 4 (5), so each has 5 xp beyond its score. In England, take "
        "Common Law in place of Civil and Canon Law (Ant p. 25). He has no "
        "supernatural powers and no Magic Resistance (Ant p. 27). If the magi "
        "are at odds with him for some years, his habits earn him a local "
        "Reputation as Eccentric, at a score the book does not print (Ant p. "
        "30).",
        "The name is Norman French and may be changed to suit the saga; his "
        "overlord is a count here, but takes whatever title suits the "
        "covenant's lands, and should not be a king or emperor (Ant p. 25). "
        "Lords of Men pp. 30-36 lists titles by region.",
    ),
}


def build(b: Builder) -> None:
    baron = _baron(b)
    overlord, barony, keep = _lands(b, baron)
    people = _household(b, baron)
    _retainers(b, baron, barony, people)
    _agents(b)
    _items(b, baron, keep)
    _story(b, baron, overlord, barony)


def _baron(b: Builder) -> Character:
    baron = b.magus(
        BARON,
        covenant=None,
        house="",
        age=35,
        type="companion",
        summary=paragraphs(
            "A young baron and a rising man at his count's court, praised for "
            "loyalty, courage, courtesy, initiative and a shrewd head, and "
            "known among his peers as learned, a good negotiator and "
            "resourceful in battle. He rides out eagerly against anyone who "
            "defies the count.",
            "All the region knows how he came by his lands: when his father "
            "rose against the count, Giraud pretended to stand with him and "
            "then delivered him up. Some call that a ruthless grab for favor, "
            "others a knight's duty to his liege over his kin.",
        ),
        secrets=paragraphs(
            "He does not want the covenant's land or wealth, nor even its "
            "allegiance to himself. He wants the magi to be law-abiding as he "
            "understands it, which means sworn to some mundane lord, and so "
            "in breach of the Code of Hermes. In his view anyone who owes "
            "fealty to no one is a king, the Pope or a rebel (Ant pp. 26-27).",
            "The more he learns of magic, the more he fears it: magi could "
            "seize his liege's mind or appear at his bedside with a knife. "
            "Unless they are bound into the web of allegiance that holds "
            "nobles in check, they threaten him, his family and his lord "
            "(Ant p. 27; Lords of Men pp. 42-43 says why the feudal order "
            "survives them).",
            "He expects to be bewitched or killed, so his wife, his confessor "
            "and his brother know all his plans and any of them could take "
            "up the campaign. His sons join that circle when they reach 21 "
            "(Ant p. 29).",
            "He would balk at a pact with demons, but only if he knew them "
            "for what they were (Ant p. 30).",
        ),
    )
    b.stats(baron, _BLOCK, source="Ant")
    for ability in baron.abilities:
        if ability.name in ("Intrigue", "Ride"):
            ability.xp += 5
    return baron


def _lands(b: Builder, baron: Character) -> tuple[Neighbour, Neighbour, Neighbour]:
    overlord = b.lord(
        "The Baron's Overlord",
        title="count",
        manors=0,
        summary=paragraphs(
            "The great lord whose favored vassal Baron Le Cornu is, a count "
            "here but an earl or duke in other lands: the Count of Champagne "
            "in the Normandy Tribunal, the Earl of Chester in Cheshire, and "
            "so on. He can raise an army of thousands if he must, and the "
            "baron and his family can shelter at his court.",
        ),
        secrets=paragraphs(
            "He expects the baron to handle his own troubles, since the baron "
            "holds his place by being useful. He cares far less about the "
            "magi: the Order has never overthrown a count, and one covenant's "
            "land and soldiers would mean little to him. He has more to gain "
            "from their friendship than to lose by leaving them be, as the "
            "baron knows, and that restrains the baron (Ant p. 26).",
            "He can defuse a quarrel, sending emissaries to broker a truce if "
            "raids break out, or to tell over-aggressive magi to stand down "
            "or meet his army. He values the baron and his knights above "
            "anything the covenant has, and will order an end to a futile war "
            "(Ant pp. 26, 34). Keep him from being drawn in too far: he is "
            "too strong for most covenants to resist (Ant p. 26).",
        ),
    )
    keep = b.place(
        "Le Cornu's Keep",
        realm="",
        summary=paragraphs(
            "The baron's tower keep, on the richest of his manors, about ten "
            "miles and half a day's ride from the covenant. A chapel stands "
            "beside it, and a permanent guard of dismounted men-at-arms "
            "holds it.",
        ),
        secrets=paragraphs(
            "Once he knows wizards can fly or turn into birds, the baron "
            "keeps his chamber shuttered tight, hangs bells on the doors of "
            "sensitive rooms, and orders patrols at random hours of the "
            "night. His people demand a password before any unusual order, "
            "and watch for anyone acting out of place, since magic can change "
            "a face. They avoid the eyes of magi, on account of Entrancement "
            "(ArM5 p. 65), and take suspected wizards blindfolded and gagged "
            "to the dungeon (Ant p. 30).",
            "These measures are guesswork with gaps. He knows little of "
            "Arcane Connections and takes no care over a shed hair or a "
            "favorite cloak (Ant p. 30). All this makes it somewhat hard to "
            "slip a magical spy inside (Ant p. 31).",
        ),
    )
    barony = b.lord(
        "The Barony of Le Cornu",
        title="baron",
        wealth="Wealthy",
        manors=10,
        seat=keep.name,
        ruler=BARON,
        answers_to=overlord,
        summary=paragraphs(
            "A minor barony of about ten manors, won by the young Giraud "
            "as his reward when his father's rising was put down. They were "
            "gathered one at a time, so they lie scattered: at least one "
            "borders the covenant, and others may be days away. Vassal "
            "knights run most of them. It has good woodland, and may hold a "
            "mill, a bridge, a road or a market.",
            "The baron spends about half his time at his keep; the rest goes "
            "on visiting his manors and attending his lord's court. A "
            "steward travels among the estates in his absence, and if he "
            "died before his eldest son came of age, his brother Sir Artur "
            "would rule as steward.",
        ),
        secrets=paragraphs(
            "The father was dispossessed or killed, as suits the saga. The "
            "manors by the covenant came with the barony, or later as a "
            "spur to continued loyalty (Ant p. 24).",
            "The baron may own the main road to the covenant, and the land "
            "under some of its vis sources (Ant p. 27).",
        ),
    )
    b.link(barony, "characters", baron, "Its lord")
    b.link(keep, "characters", baron, "His seat")
    return overlord, barony, keep


def _household(b: Builder, baron: Character) -> dict[str, Character]:
    eloise = b.magus(
        "Lady Éloise Le Cornu",
        covenant=None,
        house="",
        age=27,
        type="companion",
        traits={"Loyal to Baron": 2, "Headstrong": 2},
        summary=paragraphs(
            "The baron's wife, a capable manager who runs the barony in his "
            "long absences at court or at war. She sits in most of his "
            "councils and negotiations. She decides quickly, seldom thinks "
            "again, and does not take advice.",
        ),
        secrets=paragraphs(
            "She is unsure of herself in her duties and hides it behind a "
            "show of authority. Facing the magi while he is away, she starts "
            "out harder and less patient than he is (Ant pp. 25-26).",
            "She knows all his plans, and is his likeliest choice to run his "
            "network of agents (Ant p. 29). With her or his confessor he "
            "arranges secret meetings with the covenant's malcontents (Ant "
            "p. 29).",
            "If the saga runs for several years she grows used to authority: "
            "she loses Headstrong and gains Innovative +1 (Ant p. 26).",
        ),
    )
    henri = b.magus(
        HENRI,
        covenant=None,
        house="",
        age=46,
        type="companion",
        traits={"Loyal to Baron": 3, "Pious": 3, "Analytical": 2},
        summary=paragraphs(
            "The baron's chaplain, confessor, clerk and legal adviser, with "
            "some training in the law. He picks his words with care and "
            "always has the right proverb from Scripture. He steadies his "
            "lord, and he may come to the covenant under a white flag to "
            "ease a quarrel.",
        ),
        secrets=paragraphs(
            "He willingly helps with the baron's intrigues, and knows all "
            "his plans. He wants to learn all he can of the magi: first that "
            "they are neither diabolists nor heretics, then that they do not "
            "ill-use Christians. His hand shows in any terms the baron "
            "offers, and he judges whether the magi have satisfied the "
            "baron that their powers are not Infernal (Ant pp. 26, 29, 35).",
        ),
    )
    artur = b.magus(
        "Sir Artur Le Cornu",
        covenant=None,
        house="",
        age=31,
        type="companion",
        traits={"Brave": 3, "Loyal to Baron": 2, "Pragmatic": 1},
        summary=paragraphs(
            "The baron's younger brother and one of his vassal knights, "
            "cut from the same cloth: the stronger man, but the slower. He "
            "cannot read or write and has less intrigue and courtly grace, "
            "yet he is less ruled by his passions. He would rule as steward "
            "if the baron died before his heir came of age.",
        ),
        secrets=paragraphs(
            "He has come to accept the betrayal of their father as right for "
            "the realm, but doubts he could have done it himself. He knows "
            "all his brother's plans (Ant pp. 26, 29).",
            "If he takes over the barony he soon learns intrigue and becomes "
            "nearly as dangerous. He is readier than his brother to hire "
            "hedge wizards against the magi and less willing to heed Brother "
            "Raoullin (Ant p. 26).",
        ),
    )
    bertrand = b.magus(
        "Bertrand Gallain",
        covenant=None,
        house="",
        age=26,
        type="companion",
        traits={"Decisive": 2, "Brave": 1, "Loyal to Baron": 1},
        summary=paragraphs(
            "One of the baron's two household squires and his herald, "
            "better fitted for diplomacy than for battle, though he hopes "
            "for knighthood. A younger son of a poor knight, he dresses "
            "finely and judges everyone at first sight, as he expects to be "
            "judged.",
        ),
        secrets=paragraphs(
            "He puts on airs to hide his humble start. He is loyal at bottom, "
            "but his taste for luxury and rank leaves him open to bribes and "
            "flattery (Ant p. 26).",
            "A magus without the Gentle Gift who meets him is reported to the "
            "baron as a wicked, untrustworthy sort (Ant p. 27).",
        ),
    )
    for person, note in (
        (eloise, "His wife"),
        (henri, "His confessor"),
        (artur, "His younger brother and vassal"),
        (bertrand, "His squire and herald"),
    ):
        b.link(person, "characters", baron, note)
    return {"eloise": eloise, "henri": henri, "artur": artur, "bertrand": bertrand}


def _retainers(
    b: Builder,
    baron: Character,
    barony: Neighbour,
    people: dict[str, Character],
) -> None:
    household = b.faction(
        "The Le Cornu Family",
        faction="Family",
        decides="Its leader",
        ruler=BARON,
        summary=paragraphs(
            "The baron, Lady Éloise and their four children, two sons and "
            "two daughters, all under ten, with the baron's brother Sir "
            "Artur. They can take refuge at the count's court.",
        ),
        secrets=(
            "The sons are 9 and 6 when the conflict starts, and enter the "
            "circle of trust at 21 (Ant p. 29). The children are not named."
        ),
    )
    b.link(household, "characters", baron, "Its head")
    b.link(household, "characters", people["eloise"], "His wife")
    b.link(household, "characters", people["artur"], "His brother")
    retainers = b.faction(
        "The Baron's Retainers",
        decides="Its leader",
        ruler=BARON,
        summary=paragraphs(
            "The men who serve Baron Le Cornu: a mesnie of three household "
            "knights; nine vassal knights, Sir Artur among them; two "
            "household squires, one of them Bertrand Gallain; another fifteen "
            "mounted men-at-arms, counting all his knights' squires; twelve "
            "dismounted men-at-arms who guard the castle; and about fifty "
            "half-trained peasant levies for emergencies. A confessor and a "
            "steward complete the household.",
        ),
        rules=paragraphs(
            "The household knights use the Knight companion template (ArM5 p. "
            "23), without the Relic Virtue or the Overconfident Flaw. The "
            "castle guard use the Standard Soldier grog template (ArM5 p. 22) "
            "(Ant p. 24).",
        ),
        secrets=(
            "In open war he holds at least half his knights at home and "
            "raids with a dozen riders: himself, three knights and eight "
            "men-at-arms (Ant p. 31). His men soon weary of guard duty, so a "
            "guard is only ever a short-term measure (Ant p. 27)."
        ),
    )
    b.link(retainers, "characters", people["artur"], "A vassal knight")
    b.link(retainers, "characters", people["bertrand"], "A household squire")
    b.link(retainers, "characters", people["henri"], "Confessor and chaplain")


def _agents(b: Builder) -> None:
    b.faction(
        "Folk Who Deal With the Covenant",
        decides="Its leader",
        summary=(
            "Farmers, artisans and others who deal with the covenant, with "
            "nothing to show that anything ties them together."
        ),
        secrets=paragraphs(
            "A network of spies and informers gathered as relations sour, "
            "run for the baron by one of his inner circle, probably his "
            "wife. It starts with people loosely tied to the covenant, such "
            "as farmers and artisans who deliver there, and with anyone who "
            "bears it a grudge: thwarted apprentices, evicted tenants, rival "
            "magi, cheated merchants. Later it seeks covenfolk or grogs open "
            "to bribery or extortion, such as those with poor relatives or a "
            "weakness for drink or dice (Ant pp. 28-29).",
            "Each agent reports small things, and over time the baron "
            "assembles a surprisingly full account of the covenant: its "
            "defenses, members, quarrels, income and spending (Ant p. 29). "
            "The storyguide need only keep a list of how many there are and "
            "roughly where (Ant p. 29).",
            "Those inside the covenant are the easiest to expose, with "
            "Intellego Mentem spells, and the hardest to replace, but random "
            "checks hurt morale and may drive the unhappy to him; under the "
            "loyalty rules of Covenants, a magical questioning is probably a "
            "minor humiliation. Those outside are hard to trace. An exposed "
            "agent can be turned, fed false news, bribed, frightened or "
            "avoided, and a thorough covenant can destroy the network, over "
            "many stories (Ant pp. 31-32). The baron may also try to recruit "
            "a player's own grog or companion (Ant p. 32).",
        ),
        rules=paragraphs(
            "One season for the first three agents, all outside the covenant. "
            "After that, one season for each outsider, two or more for a "
            "lowly covenfolk, and more than two for anyone of higher "
            "importance (Ant p. 29). The agency rules of Houses of Hermes: "
            "Societates pp. 140-144 can guide who he recruits, and serve "
            "players who want agents of their own (Ant p. 28).",
        ),
    )


def _items(b: Builder, baron: Character, keep: Neighbour) -> None:
    chapel = b.church(
        "The Keep's Chapel",
        church="Chapel",
        ruler=HENRI,
        place=keep,
        summary=(
            "The castle chapel beside the baron's keep, served by Brother "
            "Henri Raoullin."
        ),
        secrets=(
            "The baron's diary lies hidden under the altar, where he wrongly "
            "believes no magic can find it (Ant p. 29)."
        ),
    )
    diary = Book(
        id=storage.generate_unique_id(
            "The Baron's Diary", [x.id for x in b.saga.books]
        ),
        name="The Baron's Diary",
        type="Other",
        author=BARON,
        owner_kind="character",
        owner_id=baron.id,
        description=secrets(
            "A private journal in the baron's own hand.",
            "Hidden under the altar of the keep's chapel. It holds "
            "every report from his spies and grows into a full profile of "
            "the covenant: its people, defenses, floor plan, visitors and "
            "income. He adds all he can learn of the magi's magic: their vis "
            "sources as far as he knows them, each magus's spells seen cast, "
            "their Wizard's Sigils, and his guesses at how to break or avoid "
            "a spell. Most of it is guesswork or misunderstanding, but about "
            "a quarter is true, enough to make him dangerous (Ant p. 29).",
        ),
    )
    b.saga.books.append(diary)
    b.link(chapel, "books", diary, "Hidden under the altar")
    relics = b.place(
        "The Baron's Relics",
        realm="",
        inside=keep,
        summary=(
            "A rich and growing collection of relics, some carried on the "
            "baron's person. Every stranger at his court must touch or kiss "
            "one before he will see them."
        ),
        secrets=(
            "All of them are fakes. He has come to believe the touch of a "
            "relic dispels any magic, and spends much time and money on them. "
            "This and his other odd habits give him a local Reputation as "
            "Eccentric within a few years (Ant p. 30). His Church Lore "
            "specialty is relics, for all the good it does him (Ant p. 25)."
        ),
    )
    b.link(relics, "characters", baron, "His collection")


def _story(
    b: Builder, baron: Character, overlord: Neighbour, barony: Neighbour
) -> None:
    threat = dormant(
        b.threat(
            "The Baron and the Covenant",
            antagonist=ANTAGONIST,
            moves=TRACK,
            summary=(
                "A new lord holds the manor next door, and he has begun "
                "asking who the covenant's liege is and by what right it "
                "keeps armed men."
            ),
            secrets=paragraphs(
                "By fair means or foul, the baron means to end the magi's "
                "independence and bring them to swear fealty, which the Code "
                "forbids. He knows he cannot beat a typical covenant by "
                "force, and the Code lets magi defend themselves against "
                "mundanes (HoH:TL p. 51), so he uses carrot and stick. Lean "
                "too far toward him and the magi risk a charge of meddling "
                "with mundanes; rebuff him too often and he turns to "
                "harassment. Either way there are stories (Ant p. 27). The "
                "stages are the book's plots in its order; pick those that "
                "fit, as his next step depends on what the magi do.",
                "A vis source on his land counts as the Contested Resources "
                "Hook: reveal a Hidden Hook as this, or add a new one with a "
                "new Boon to balance it, or give the covenant a new resource "
                "worth the same build points (Ant p. 28).",
                "Jurisdiction (Ant pp. 32-33). The baron's own court hears "
                "small cases such as trespass, so he both sues and judges. "
                "He takes that seriously, and strong evidence can win there "
                "as anywhere. If the players find that unfair, say such cases "
                "go to his overlord's court here. Land, economic privileges "
                "and capital crimes go to royal court, and stealing "
                "livestock or poaching big game can mean death. A Church "
                "court hears clergy, and most inheritance and contract "
                "cases. Secular courts are described in Lords of Men pp. "
                "80-82, Church courts in The Church pp. 35-36.",
                "Arguing a case (Ant pp. 32-34). The Gift sets any secular "
                "court against magi, who may earn a bad local Reputation by "
                "appearing, Gentle Gift aside. No one is presumed innocent or "
                "protected against incriminating himself; testimony counts "
                "more than things. Character witnesses matter, and in a "
                "canon court enough clergy clear the accused outright "
                "(compurgation). Eyewitnesses weigh heavily, but alternative "
                "explanations can answer them. Land cases turn on long "
                "possession, and parish records are the best proof. Benefit "
                "of clergy is open: rule that magi do not count unless "
                "ordained, or leave it unsettled and make a story of it.",
                "Stolen vis (Ant p. 34). If the vis is in something of value, "
                "a jewel or a large beast, the court tries an ordinary theft. "
                "If it is in something cheap, the baron cannot show its worth "
                "without a magus to testify, so the verdict is trespass; but "
                "he persuades the court that taking the same thing again "
                "proves its value, and any repeat is serious burglary.",
                "Land verdicts (Ant p. 34). A covenant with the Autocephalous "
                "Boon (Covenants p. 20) wins outright. Otherwise it must "
                "settle by owning the count as lord and taking a charter, or "
                "argue in royal court, where a win gives it that Boon. If it "
                "loses, the land reverts to the count, and after a week the "
                "baron comes with armed men to clear the squatters.",
                "Ending the fighting (Ant p. 34). A couple of raids beaten "
                "off, a manor sacked, or two or three knights killed or badly "
                "hurt make him ask for a truce; a captured knight or adviser "
                "brings a truce and a ransom. Too great a show of force "
                "drives him to a last decisive battle.",
                "His demands, most important first (Ant p. 35): no attacks on "
                "the count or his vassals and no spells on them unasked, "
                "self-defense excepted; proof the magi's powers are not "
                "Infernal, such as taking confession and communion; magical "
                "service to his liege, which breaks the Code and which he "
                "can be argued out of; respect for his bounds, with nothing "
                "taken unpaid, vis included, and he prefers payment in "
                "enchantments or spells; obedience to mundane law, handing "
                "over the accused and answering lawsuits, the court being "
                "negotiable; a share of income from anything they cannot "
                "prove is theirs; the count's leave to keep men-at-arms, or "
                "disarm; and scutage, which he will waive to gain a higher "
                "demand. If they agree to all, he has no more quarrel.",
                "What the count grants in return, most valuable first (Ant p. "
                "35): recognition that the covenant owns its land and "
                "resources, its serfs included; a charter making it an "
                "independent legal body; leave for an armed garrison; "
                "exemption from military service and scutage; exclusive "
                "rights to vis on the baron's lands; leave to clear "
                "wasteland; leave to hunt magical beasts; and exemption from "
                "some taxes and fines. A settlement with the count is final.",
            ),
            stages=[
                S(
                    "A Squire Comes Calling",
                    at=1,
                    clues="Bertrand Gallain arrives to meet the new neighbors, "
                    "asking who their liege is and why they keep armed men.",
                    ignored="Careless answers tell the baron what disturbs "
                    "him: Gifted magi look like villains, admitted magic "
                    "suggests heresy, and a castle or grogs without leave from "
                    "a high lord upset him greatly. He asks to visit, and "
                    "either way starts seeking agents (Ant p. 27).",
                    turned="If he visits, he is plainly suspicious, and "
                    "presses to know who gave them the right to their home "
                    "and their soldiers.",
                ),
                S(
                    "A Letter About Trespass",
                    at=2,
                    clues="Covenant folk are seen on his land, armed or not, "
                    "and a written warning arrives (Ant p. 27).",
                    ignored="If they keep coming, for vis or anything else, "
                    "he forbids it, has them watched, and then sets a guard "
                    "or goes to law. A spy may tail them; he won't know what "
                    "vis is, but sees it matters, and bargains with it (Ant "
                    "pp. 27-28).",
                ),
                S(
                    "Favors and Gifts",
                    at=3,
                    clues="While relations are good he sends fine gifts, such "
                    "as dishes, garments, hounds and horses, and hints that "
                    "enchanted gifts would be a fitting return (Ant p. 27).",
                    ignored="He is insulted if none come, and offended if "
                    "refused a favor such as battle magic before his lord's "
                    "war.",
                    turned="He cannot detect magic, so a placebo will do for "
                    "a while. In time he asks for what cannot be faked: "
                    "saving his crops from blight, or magic to hunt down "
                    "rebels.",
                ),
                S(
                    "Closed Roads",
                    at=4,
                    clues="At odds with the covenant, he bars it from his "
                    "woods, mills, bridges, roads and markets. That may mean "
                    "the main way in, and vis sources on his land (Ant p. 27).",
                ),
                S(
                    "A Summons",
                    at=5,
                    clues="A lawsuit: use only one or two, as repeated suits "
                    "grow dull (Ant p. 28).",
                    ignored="Trespass carries a small fine. What matters is "
                    "answering: defying the summons angers him into a new "
                    "plot.",
                    stopped="If they come to court he relaxes somewhat, win "
                    "or lose, for they have shown respect for mundane "
                    "authority.",
                    turned="Removing something valuable makes it burglary, "
                    "perhaps a hanging matter, in royal court a few seasons "
                    "off. A challenge to the covenant's title must be brought "
                    "by the count, unless a tame noble holds it, but the "
                    "baron argues it himself, even against an allod. If his "
                    "case is strong he offers to settle, with extra demands "
                    "(Ant pp. 28, 34).",
                ),
                S(
                    "Eyes and Ears",
                    at=6,
                    clues="Delivery men ask too many questions, and shadowy "
                    "figures are seen near restricted parts of the covenant "
                    "(Ant pp. 28-29, 32).",
                    stopped="Exposing agents is among the best ways to halt "
                    "him, though he can replace them.",
                ),
                S(
                    "Friends Turned Away",
                    at=7,
                    clues="Friends of the covenant grow cold. He beats his own "
                    "villeins for visiting, sends squires or knights to "
                    "frighten the lower orders, and threatens to boycott "
                    "merchants. Priests and abbots hear that magi are wicked, "
                    "with bribes or veiled threats and the risk of a bad "
                    "Reputation or the bishop's displeasure (Ant p. 29).",
                    ignored="The covenant weakens and may seek a new mundane "
                    "patron, as he hopes: his overlord.",
                    stopped="A story can win a friend back, such as grogs "
                    "scaring off a bullying squire.",
                ),
                S(
                    "Sowing Discord",
                    at=8,
                    clues="His wife or confessor meets a malcontent in "
                    "secret, listing the magi's failings and praising the "
                    "peace to be had (Ant pp. 29-30).",
                    ignored="Unless the troupe wants treachery, he should "
                    "fail at real infighting: at worst he gains a few agents "
                    "or some deserters.",
                ),
                S(
                    "Old Enemies at the Keep",
                    at=9,
                    clues="Hedge wizards the magi insulted, or a suspicious "
                    "clergyman, are summoned to his keep and given a "
                    "sympathetic ear. Foes the covenant thought beaten may "
                    "return, and in a high fantasy saga he may pact with "
                    "faeries or magical beasts (Ant p. 30).",
                ),
                S(
                    "The Burglar",
                    at=10,
                    clues="After a defeat by the magi, or if he suspects "
                    "witchcraft, he seeks a specialist. That may take seasons "
                    "or years, and may mean forgiving a crime. Agents inside "
                    "let him in, keep watch and aid his escape (Ant p. 30).",
                    ignored="He takes something small, such as a lab text or "
                    "charged item, not a high summa or an invested device, "
                    "and rushes it to the baron.",
                    stopped="Give the players a chance to catch him: a good "
                    "story for grogs.",
                ),
                S(
                    "Held for Ransom",
                    at=11,
                    clues="If the covenant breaks into his keep, fights his "
                    "men or threatens him, he hears from agents where its "
                    "members will be and has knights lay an ambush to take "
                    "prisoners, not to kill. A character accused of a serious "
                    "crime may be held for trial (Ant pp. 30-31).",
                    turned="He frees prisoners for restitution or a formal "
                    "agreement. Coin alone will not do; a promise must come "
                    "with it.",
                ),
                S(
                    "Torch and Sword",
                    at=12,
                    clues="He or his successor attacks if his life is "
                    "threatened, or he dies or falls under a spell without "
                    "explanation; his advisers need no proof (Ant p. 31).",
                    ignored="He fortifies the near manors and raids. His "
                    "first targets are vis sources he knows of, then wooden "
                    "bridges and mills, then property, and he kills or drives "
                    "off farmers and laborers. Expect lasting financial harm.",
                    stopped="See Ending the fighting in the secrets.",
                ),
                S(
                    "Terms, and the Tribunal's Answer",
                    at=13,
                    clues="Peace comes by capitulation, relocation or treaty "
                    "(Ant pp. 34-35).",
                    ignored="Swearing fealty to the count ends the quarrel "
                    "and may win an ally, but breaks the Peripheral Code in "
                    "every Tribunal, since it is a pledge of personal service "
                    "like a court wizard's. It must then be kept secret from "
                    "other magi. A companion made a figurehead vassal will not "
                    "fool him (Ant p. 34).",
                    stopped="Moving the covenant is extreme and lets him win, "
                    "but a change of setting can suit a troupe (Ant pp. 34-35).",
                    turned="A treaty that stops short of personal service, "
                    "beginning perhaps with non-aggression and growing as "
                    "disputes arise. It then raises questions at Tribunal: "
                    "who owns vis on his land, whether the covenant could "
                    "give it away or bind other magi, whether it should have "
                    "been ratified, whether the magi have become court "
                    "wizards, and how far magi must obey mundane law. Rulings "
                    "may be narrow or sweeping, reach the Grand Tribunal, or "
                    "assert that magi may only be tried in Hermetic courts "
                    "(Ant pp. 35-36; HoH:TL p. 51; in Normandy, The Lion and "
                    "the Lily pp. 24-25).",
                ),
            ],
        )
    )
    b.link(threat, "characters", baron, "Drives it")
    b.link(threat, "places", barony, "His lands")
    b.link(threat, "places", overlord, "May step in")
