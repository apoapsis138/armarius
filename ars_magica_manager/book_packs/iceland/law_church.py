"""Law and the Church in Iceland (Land of Fire & Ice pp. 34-44), in paraphrase.

The law is held by factions: the Law of Iceland itself (penalties, wergild,
procedure, settlement), the Spring and Fall Things, the Althing and its
Quarter Courts, Fifth Court, Law Council and Lawspeaker. The Althing's field,
Thingvoll, the four Quarters and the thirteen spring assembly sites are
places, the sites sitting in their Quarters.

The Church is the two dioceses, each a Bishop's cathedral in its town, the
schools at Skalholt, Holar and Oddi, the monasteries and the nunnery, and
three factions: the Church in Iceland (the conversion and its history), the
lay wardens and Bishop Gudmund's following. The book's Christian magicians
are described on their schools, in words; magic.py holds their tradition.

A place an earlier part already made is reused, by name, with these pages
added to its summary. The book's four story seeds are dormant threats."""

from __future__ import annotations

from typing import Any

from ...models import Neighbour
from ..builder import Builder, dormant, paragraphs

S = Builder.stage
MONASTERY = "Monastery or nunnery"
BENEDICTINE = "Benedictine"
AUGUSTINIAN = "Augustinian"
QUARTERS: dict[str, tuple[str, ...]] = {
    "Western Quarter": ("Thverar", "Thorsnes", "Thorskafjardar"),
    "Southern Quarter": ("Rangar", "Arnes", "Kjarlarnes"),
    "Eastern Quarter": ("Sunnudals", "Mula", "Skaftafells"),
    "Northern Quarter": ("Hunavatns", "Hegranes", "Vadla", "Thingeyjar"),
}


def _named(b: Builder, name: str) -> Neighbour | None:
    """The record of that name an earlier part made, if any."""
    return next((n for n in b.saga.neighbours if n.name == name), None)


def _place(b: Builder, name: str, summary: str, **kw: Any) -> Neighbour:
    """A mundane place, or an earlier part's place of that name with this
    summary added to it."""
    found = _named(b, name)
    if found is not None:
        found.summary = paragraphs(found.summary, summary)
        return found
    return b.place(name, summary=summary, realm="", **kw)


def build(b: Builder) -> None:
    sites = _quarters(b)
    thingvoll = _thingvoll(b)
    _law(b)
    _assemblies(b, sites, thingvoll)
    _old_faith(b)
    _church(b)
    skalholt, holar = _sees(b)
    _wardens(b)
    _gudmund(b, holar)
    _schools(b, skalholt, holar)
    nunnery = _monasteries(b, skalholt)
    _stories(b, skalholt, nunnery)


# -- the land as the law divides it --


def _quarters(b: Builder) -> list[Neighbour]:
    sites: list[Neighbour] = []
    for quarter, names in QUARTERS.items():
        count = len(names)
        holder = _place(
            b,
            quarter,
            f"One of the four Quarters that divide Iceland for the law, with "
            f"{count} districts, each holding its own spring assembly. It "
            "counts twelve chieftaincies today (LFI p. 34).",
        )
        for name in names:
            sites.append(
                _place(
                    b,
                    name,
                    f"The spring assembly site of a district of the {quarter}, "
                    "where its householders gather by the end of the fourth "
                    "week of summer (LFI p. 34).",
                    inside=holder,
                )
            )
    return sites


def _thingvoll(b: Builder) -> Neighbour:
    thingvoll = _place(
        b,
        "Thingvoll",
        paragraphs(
            "A place of great natural beauty with a large lake, where the "
            "river Axe runs through ravines and lava plains. For a fortnight "
            "each summer it holds the Althing and becomes the nearest thing "
            "Iceland has to a town: hundreds come, and with them traders, "
            "peddlers, brewers and people seeking a husband or a wife. "
            "Friendships and alliances are made and broken, stories told, "
            "news swapped and business done.",
            "The richer families keep turf booths here, roofed with "
            "homespun only while the meeting lasts; the rest pitch tents. "
            "There is a local church, where the bishops lead masses on the "
            "Althing's first Sunday (LFI p. 35).",
        ),
    )
    _place(
        b,
        "The Logberg (Law Rock)",
        "The rock at the Althing where the lawspeaker formally recites new "
        "laws. Anyone may stand on the grassy slope around it to offer "
        "corrections and argue points of law (LFI p. 36).",
        inside=thingvoll,
    )
    _place(
        b,
        "The Oxara",
        "It runs through the ravines and lava plains of Thingvoll (LFI p. 35).",
        inside=thingvoll,
    )
    return thingvoll


# -- the law --


def _law(b: Builder) -> None:
    b.custom(
        "The Law of Iceland",
        summary=paragraphs(
            "Iceland has no king; it has law. The first settlers, fleeing "
            "the feudal order growing on the mainland, framed it around the "
            "rights of free men, and the land itself kept any lord from "
            "holding wide territories, so wealth lay remarkably evenly. "
            "Slaves were freed and freedmen came to own land. That levelling "
            "is slowly and painfully coming undone in this century: the law "
            "was never able to restrain the storgodar, or later the bishops.",
            "Everyone belongs to the law through a thing attachment. A "
            "householder chooses a godi to be in thing with at the spring "
            "assembly, and those attached to the household follow that "
            "choice, so every person stands with one godi, in one district, "
            "in one Quarter (LFI p. 34).",
            "On paper the land looks punished at every turn: eating meat on "
            "a Friday can earn lesser outlawry, and tripping a man full "
            "outlawry. In truth most offences never reach a court. The one "
            "wronged lets the matter go or settles at once, because a suit "
            "is costly, slow, technical and often dangerous (LFI pp. 37-38).",
            "The laws are written now, in many books that may differ on the "
            "very detail a case turns on, for the law still bears the marks "
            "of its oral beginnings. The name Gragas (Grey Goose) belongs to "
            "two later manuscripts, and Icelanders of 1220 do not use it "
            "(LFI p. 36).",
            "Law reaches everyone. Even magi who shun their neighbours have "
            "companions and grogs to feed, and will buy from the farms "
            "nearby (LFI p. 39).",
        ),
        secrets=paragraphs(
            "Once the characters are known to exist, even with their "
            "covenant unfound, powerful bondi and godi may court them as "
            "allies, and others who feel threatened may plot against them. "
            "Either way, with Icelandic politics as turbulent as they are, "
            "the law will soon be involved (LFI p. 39).",
            "A godi can in practice dictate a panel of twelve, at some cost "
            "in respect, and so can shield a magician from an unjust "
            "prosecution for sorcery (LFI p. 38).",
        ),
        rules=paragraphs(
            "Penalties (LFI p. 37): only three exist, each fixed for its "
            "crime, and the court cannot vary them. No office enforces them: "
            "an unpaid fine needs a new case for non-payment (penalty: "
            "lesser outlawry), and after an outlawry the family must post a "
            "bounty or hunt the man themselves.",
            "Three-mark fine (24 law ounces): for petty offences such as "
            "unintended damage by cattle, small legal errors and minor "
            "religious breaches. Half goes to the prosecutor, half to the "
            "lawspeaker if present.",
            "Lesser outlawry: three years' banishment, usually for negligent "
            "damage above five law ounces and many religious matters, such "
            "as a priest forgetting the holy water for a baptism. The "
            "outlaw has three summers to find passage; the three years run "
            "from then, and he may return with full rights. A court of "
            "confiscation divides his property; if it strays from the law "
            "the case can be quashed and those responsible face lesser "
            "outlawry themselves.",
            "Full outlawry: for any assault that landed a blow, hurt or not, "
            "and for breaking judgment in a lesser outlawry case. The outlaw "
            "loses all property and all legal, family and Church rights, and "
            "the Church always excommunicates him. No one may lawfully help "
            "or even advise him, and anyone may kill him. Only surviving "
            "twenty years or killing three other outlaws wins a reprieve "
            "without the prosecutor's consent.",
            "Court of confiscation: two weeks after the thing that "
            "pronounces outlawry, at the convicted man's home, with twelve "
            "judges named by a local godi.",
            "Wergild (LFI p. 37): free man 120 law ounces, freedman 60, "
            "slave 12; a fraction for harm short of death, not only bodily. "
            "It is owed whether or not a suit is brought, unless the victim "
            "fell having forfeited immunity. If it goes unpaid, the victim's "
            "kin may forbid the attacker's kin from coming near them, who "
            "must then humbly keep out of their way.",
            "Principals and vengeance (LFI p. 38): every prosecution and "
            "defence needs a principal, who may hand the case to another at "
            "any point. A defence principal charged with violence is barred "
            "from things and must do so. Assault, injury, raids on property, "
            "insult by word or gesture and sexual offences against "
            "kinswomen give a right of vengeance: the aggressor loses "
            "immunity and may be killed or hurt without penalty, until the "
            "next Althing. Forfeit immunity is a common defence.",
            "Advocates (LFI p. 38): any slip, or possible slip, in a major "
            "case can spawn a new case. Handing a case to a godi is often "
            "very dear, but against a godi the only other course is to drop "
            "it. Skill at law can offset uneven support.",
            "Before court (LFI p. 38): the prosecutor publishes the charge "
            "before a panel of neighbours, then before them summons the "
            "defence principal and tells his witnesses to attend. A killer "
            "must publish the deed as his own within a set time and "
            "distance, though not before a panel; failing that it is "
            "murder, a shameful thing, and full outlawry. Where witnesses "
            "are lacking, or intent or state of mind is in question, a panel "
            "decides: a panel of neighbours (five or nine freemen, usually "
            "those living closest), or a panel of twelve (the local godi and "
            "eleven freemen of his assembly third), used for matters of "
            "great public interest such as sorcery, theft, murder and "
            "perjury.",
            "In court (LFI pp. 38-39): a principal brings at most ten men, "
            "and spectators stay beyond the boundary lines. Each litigant "
            "draws one lot for the order of cases, however many he has. The "
            "prosecutor names his witnesses, swears it is his case, recites "
            "his summons and presents his proof. Facts stated within a case "
            "may not conflict, and only a perjury judgment of the Fifth "
            "Court can amend them, for which the trial may be halted. "
            "Witnesses give one testimony, the majority prevailing, and "
            "dissenters are immune from perjury. The defence may challenge "
            "panel members (someone closer not called, kinship with the "
            "prosecutor, means, health), the prosecutor replacing them with "
            "the best qualified present; a wrong type of panel, or a "
            "witness on the same point, vetoes its verdict, for testimony "
            "outranks a panel. The defence then puts its case and the "
            "prosecutor may challenge likewise. One judge sums up each side.",
            "Settlement (LFI pp. 39-40): self-judgment, where the victim "
            "sets the terms, is the most honourable course, and abusing it "
            "costs reputation. Formal duels were outlawed in the eleventh "
            "century, though single combat quietly goes on. The summons is "
            "the first chance to settle, and refusing a generous offer "
            "weakens the prosecutor. Men of rank may call in an arbitrator, "
            "or a respected one may step in unasked; only overwhelming "
            "support then keeps a case alive. Arbitrators count the dead on "
            "each side, offset by rank and other injuries, and make up the "
            "difference with compensation on top of wergild. One who cannot "
            "pay suffers a banishment whose terms are entirely at the "
            "arbitrator's discretion.",
        ),
    )


def _assemblies(b: Builder, sites: list[Neighbour], thingvoll: Neighbour) -> None:
    spring = b.faction(
        "The Spring Things",
        faction="Council or assembly",
        summary=paragraphs(
            "The local assembly (varthing) of each of Iceland's thirteen districts, "
            "held by the end of the fourth week of summer, mostly for cases "
            "between people of the same district. Every householder (bondi) "
            "must attend, in person or by proxy (LFI pp. 34-35).",
            "Each district has three chieftaincies. There were once twelve "
            "districts and nine chieftaincies to a Quarter, until the north "
            "demanded a fourth district; three more chieftaincies were "
            "added to the others to keep the balance, so each Quarter now "
            "has twelve. Only the original nine are called full and ancient.",
        ),
        rules=paragraphs(
            "Only godar of full and ancient chieftaincies preside in the "
            "eastern, southern and western Quarters (LFI p. 34).",
            "Court of prosecution (LFI pp. 35-36): opens the "
            "assembly. 36 judges, twelve named by each godi from his "
            "thingmen. A verdict needs 31 to agree; failing that, the case "
            "goes to the matching Quarter Court. Godar cannot sit as judges "
            "and are free to fight cases and broker settlements.",
            "Court of payments (LFI p. 35): opens four days later. Debts are "
            "settled and goods valued, and it sets local measures such as "
            "the silver value of the standard ounce and the prices of "
            "cloth, fish and livestock.",
        ),
    )
    for site in sites:
        b.link(spring, "places", site, "A spring assembly site")
    althing = b.faction(
        "The Althing",
        faction="Council or assembly",
        summary=paragraphs(
            "The General Assembly, held at Thingvoll once ten weeks of "
            "summer have passed and lasting at least two weeks. It is the "
            "great social event of the year as well as the seat of the law.",
            "The allsherjargodi, the supreme chieftain, opens it. The title "
            "goes with the hereditary chieftaincy of Thorstein Ingolfsson, "
            "son of Iceland's first settler; for all its grandeur it brings "
            "no privilege beyond these duties (LFI p. 35).",
        ),
        place=thingvoll,
        rules=paragraphs(
            "All godar and the lawspeaker must be present on the opening "
            "day. Each godi should bring at least one in nine of his "
            "thingmen, or be fined (LFI p. 35).",
            "The calendar (LFI pp. 35-36): Thursday evening, the "
            "allsherjargodi hallows the site and sets the boundaries of the "
            "assembly's sections. Friday, judges are appointed. Saturday, "
            "either side in a case may challenge or dismiss nominees. "
            "Sunday, the bishops lead masses. Monday, the courts convene "
            "for nine days, ending on a Wednesday. Last comes the session "
            "of the law council, then the weapon-taking.",
            "Weapons may not be carried once the Althing is convened: they "
            "stay at the booth or campsite until the weapon-taking, when "
            "people pack for home (LFI p. 36).",
        ),
    )
    b.faction(
        "The Quarter Courts",
        faction="Council or assembly",
        summary="The judicial arm of the Althing: one court for each Quarter, "
        "hearing what the spring courts could not decide (LFI p. 36).",
        place=thingvoll,
        members=36,
        rules="Each holder of a full and ancient godord names one thingman to "
        "each court, so each has 36 judges. As in the varthing, a verdict "
        "must be all but unanimous: 31 of 36 (LFI pp. 36, 39). A divided "
        "judgment goes to the next court up, usually the Fifth Court.",
    )
    b.faction(
        "The Fifth Court",
        faction="Council or assembly",
        summary="The highest court, hearing divided judgments from the "
        "Quarter Courts and abuses of procedure itself, such as perjury and "
        "bribery (LFI p. 36).",
        place=thingvoll,
        members=48,
        rules="All the godar name one judge each, making 48; the accused and "
        "the plaintiff each dismiss six for every dispute, leaving 36. A "
        "simple majority decides. A tie goes to the prosecution, except in a "
        "case sent up from a divided Quarter Court, when lots are drawn. "
        "Procedure otherwise follows the lower courts (LFI pp. 36, 39). The "
        "book dates its founding to 1004 here and to 1005 in its timeline "
        "(LFI p. 17).",
    )
    b.faction(
        "The Law Council (Logretta)",
        faction="Council or assembly",
        summary="The legislative arm of the Althing. Here the chieftains "
        "review old laws and make new ones, approve out-of-court settlements, "
        "decide disagreements over the law and grant exemptions from it. Its "
        "session is the Althing's last official business (LFI pp. 35-36).",
        place=thingvoll,
        members=50,
        decides="The 48 godar and two bishops, with the lawspeaker in the "
        "chair and holding the casting vote.",
        rules="Every free man may attend, but only godar and bishops may "
        "speak; all 48 godar and both bishops must attend. Each godi has two "
        "advisers. They sit on three concentric rings of benches, the godar "
        "in the middle, the advisers on the inner and outer. The council "
        "elects the lawspeaker, and may ask him to recite any part of the law "
        "it needs (LFI p. 36).",
    )
    b.faction(
        "The Lawspeaker",
        faction="Council or assembly",
        summary=paragraphs(
            "The only paid office in Iceland, held for three years by "
            "election of the law council. He chairs the council, recites "
            "new laws at the Logberg, announces licences for mitigation of "
            "penalty and settles the legal calendar for the coming year. "
            "Before the laws were written he recited a third of them in each "
            "year of his term; now he need recite only those made or "
            "repealed that year (LFI pp. 35-36).",
            "In 1220 the office is held by Teit Thorvaldsson the Priest. "
            "Snorri Sturluson, back from Norway this year, has let it be "
            "known that he will seek re-election in 1222 (LFI p. 36).",
        ),
        ruler="Teit Thorvaldsson the Priest",
        place=thingvoll,
        rules="Stipend of 40 law ounces a year, plus half the fines levied at "
        "the Althing and at his own spring assembly. He holds the council's "
        "casting vote. Each godi, or two of his advisers, must attend the "
        "recital. At a lapse of memory or a hard point he consults at least "
        "five legal experts (LFI p. 36).",
    )
    fall = b.faction(
        "The Fall Things",
        faction="Council or assembly",
        summary="The least formal of the three great assemblies, held when "
        "eight weeks of summer remain and lasting no more than two days. It "
        "tells the people what happened at the Althing: the new laws, "
        "official pronouncements such as outlawries, and next year's "
        "calendar (LFI pp. 36-37).",
        rules="No court is appointed.",
    )
    b.link(althing, "places", fall, "Reports the Althing to the districts")


# -- the Church --


def _old_faith(b: Builder) -> None:
    b.faction(
        "The Aesir (The Old Religion)",
        faction="Faith or sect",
        summary=paragraphs(
            "Until the end of the first millennium most Icelanders were "
            "pagans, honouring the Norse gods and goddesses together called "
            "the Aesir: above all Thor, god of farmers and seafarers, and "
            "also Frey, god of fertility. Even the sons of the few Christian "
            "settlers took up these ways (LFI p. 41).",
            "Icelanders still recite the myths with pride, take personal "
            "belief lightly and are often of two minds about the old faith. "
            "Above all, its ideals of honour and vengeance still rule "
            "Icelandic life at every level (LFI p. 42).",
        ),
    )


def _church(b: Builder) -> None:
    b.faction(
        "The Church in Iceland",
        faction="Religious community",
        summary=paragraphs(
            "Iceland took the faith by a settlement at law. Pressure from "
            "the mainland began in 980 and came to a head under King Olaf "
            "Tryggvasson (995-1000). His first envoy, the Icelander Stefnir "
            "Thorgilsson, wrecked sanctuaries so zealously that he was "
            "outlawed and driven off. The priest Thangbrand then won over "
            "several prominent men in three years and killed three poets "
            "who mocked him, but left in 999 with most Icelanders still "
            "pagan. Olaf closed his ports to Icelanders and took the "
            "kinsmen of leading pagans hostage in Norway, threatening to "
            "maim or kill them.",
            "At the next Althing the parties skirmished and civil war drew "
            "near until mediators put the matter to arbitration. Both sides "
            "accepted Godi Thorgeir Thorkelsson, a pagan with strong "
            "Christian kin. He lay under his cloak for part of a day and a "
            "night, and bound both sides to his ruling before giving it: all "
            "should be Christian and be baptized, while the exposure of "
            "infants and the eating of horseflesh stayed lawful, and private "
            "sacrifice was tolerated unless witnessed, when it was lesser "
            "outlawry. These allowances were dropped a few years later. So "
            "in the summer of 1000 the whole country converted, almost "
            "without blood (LFI pp. 41-42).",
            "Iceland then fell under the archbishop of Hamburg-Bremen and "
            "was largely neglected. Few foreign priests and wandering "
            "missionary bishops came, so farmers built churches at their own "
            "expense, and many godar traded their pagan role for the "
            "priesthood and served in them. The Church grew into the secular "
            "law, its wealth and power run by laymen (LFI p. 42).",
            "The first native bishop, Isleif Gizursson (born about 1006), "
            "won little respect, competing with missionary bishops of the "
            "Armenian and Eastern Churches. His eldest son Gizur Isleifsson "
            "took pledges from all the chieftains to accept his ordinances, "
            "was consecrated in 1082, introduced the tithe in 1096 and gave "
            "the see a fixed seat by willing it his farm at Skalholt. A "
            "second see followed at Holar, and in 1106 the archbishop of "
            "Lund consecrated Jon Ogmundarson to it (LFI p. 43).",
            "Reform came late. Thorlak Thorhallsson of Skalholt (1178-93) was "
            "the first bishop to try enforcing Church discipline, and in "
            "1190 the archbishop wrote forbidding the ordination of godar. "
            "When Thorlak moved against the wardens, Jon Loftsson refused "
            "the archbishop's message and rallied them against him (LFI "
            "p. 43).",
            "In 1220 priests of every rank still live much as laymen: they "
            "marry, keep concubines, inherit, prosecute cases, bear arms and "
            "join in feuds and blood vengeance. Orders forbid them weapons "
            "and all lawsuits save those of the defenceless, and are "
            "ignored. Godar are no longer ordained and few remain priests, "
            "but most Church property stays firmly with the lay wardens "
            "(LFI p. 43).",
        ),
        rules=paragraphs(
            "Knowing the Pater noster and Credo by heart is required of "
            "anyone able to learn them; wilful failure is lesser outlawry, "
            "and the bishop decides who prosecutes (LFI p. 42).",
            "The tithe, from 1096, is a 1% property tax split into four: "
            "bishop, parish church, priest and paupers (LFI pp. 42-43).",
            "Both bishops sit in the law council (LFI p. 36).",
        ),
    )


def _sees(b: Builder) -> tuple[Neighbour, Neighbour]:
    skalholt = b.town(
        "Skalholt",
        summary="The seat of the southern see, in the south-west, on the farm "
        "Bishop Gizur Isleifsson willed to the Church. Eighty people live "
        "here around the wooden cathedral (LFI pp. 42-44).",
        population=80,
        ruler="Bishop Magnus Gizurarson",
    )
    holar = b.town(
        "Holar",
        summary="The seat of the northern see, the second in Iceland, with "
        "its cathedral school (LFI pp. 42-43).",
        ruler="Bishop Gudmund Arason",
    )
    b.church(
        "Diocese of Skalholt",
        church="Bishop's cathedral",
        place=skalholt,
        ruler="Bishop Magnus Gizurarson",
        summary=paragraphs(
            "A wooden cathedral almost 50 paces long, seat of a diocese of "
            "220 churches and 290 priests. Bishop Magnus Gizurarson lives "
            "here in relative quiet (LFI p. 44).",
            "The Southern Bishopric, all the island beyond the Northern "
            "Bishopric's bounds (LFI p. 10).",
            "After Bishop Thorlak died in 1193 the chieftains took care to "
            "choose men to their liking: Pall Jonsson, and on his death in "
            "1211 Magnus, elected by the godar (LFI p. 43).",
        ),
    )
    b.church(
        "Diocese of Holar",
        church="Bishop's cathedral",
        place=holar,
        ruler="Bishop Gudmund Arason",
        summary=paragraphs(
            "The northern diocese, of 108 parish churches and 136 priests. "
            "Its first bishop, Jon Ogmundarson, was consecrated in 1106 "
            "(LFI p. 43).",
            "The Northern Bishopric, the middle of the north coast and the "
            "land behind it (LFI p. 10).",
            "When the see fell vacant in 1201 the chieftain Kolbeinn Tumason "
            "arranged the election of an illegitimate relative of his wife, "
            "Gudmund Arason. Gudmund was known for his miracles but thought "
            "unfit to run a great institution, and Kolbeinn meant to rule "
            "through him. He misjudged: they fell out over alms to the poor "
            "and over jurisdiction in cases against clergy, each ignoring "
            "the other's rulings, while outlaws took refuge and "
            "excommunications went unheeded. Gudmund gathered unruly men "
            "and violence followed, until in 1208 a thrown stone killed "
            "Kolbeinn.",
            "The chieftains then allied, and from 1209 blocked Gudmund's "
            "reforms, often by force. Summoned to Norway by the archbishop "
            "in 1214, he found little support there. Since returning in 1218 "
            "he has given up the claim to wider judicial power and stands "
            "instead as champion of the poor, giving most of the diocese's "
            "income to charity when he can (LFI p. 43).",
        ),
    )
    return skalholt, holar


def _wardens(b: Builder) -> None:
    b.faction(
        "The Lay Wardens",
        faction="Religious community",
        summary=paragraphs(
            "Godar and well-off farmers who hold Church property. A family "
            "grants land in a saint's name and keeps control of it by "
            "serving as warden, and donations to the church pass through "
            "its hands, so that this control is worth a great deal "
            "(LFI p. 42).",
            "Led by Jon Loftsson, they turned back Bishop Thorlak's attempt "
            "to take control from them, armed though he was with the "
            "archbishop's letter (LFI p. 43).",
        ),
        rules="A warden receives two of the tithe's four parts, the church's "
        "and the priest's, keeps any profit, and is personally exempt from "
        "the tithe (LFI p. 43).",
    )


def _gudmund(b: Builder, holar: Neighbour) -> None:
    reykjadal = _place(
        b,
        "Reykjadal",
        "The region of the northern diocese where Bishop Gudmund's company "
        "now wanders, and where its farmers are running out of patience "
        "(LFI pp. 43-44).",
    )
    following = b.faction(
        "Bishop Gudmund's Following",
        faction="Religious community",
        summary="Bishop Gudmund Arason lives in poverty among clergy, armed "
        "men, vagrants, beggars and thieves. He keeps 120 followers moving "
        "about Reykjadal, demanding hospitality from the local farmers "
        "(LFI pp. 43-44).",
        ruler="Bishop Gudmund Arason",
        members=120,
        place=reykjadal,
    )
    b.link(following, "places", holar, "The bishop's see")


def _schools(b: Builder, skalholt: Neighbour, holar: Neighbour) -> None:
    oddi = _place(
        b,
        "Oddi",
        "The seat of the school founded by Saemundur Sigfusson (LFI p. 42).",
    )
    b.university(
        "The School at Oddi",
        place=oddi,
        summary="Founded by Saemundur Sigfusson (1056-1133), who was sent "
        "abroad as a youth to further his training as a priest, learned "
        "Natural Magic in France, and came home to be consulted on many "
        "matters. His son Eyjolf became its headmaster. Saemundur joined the "
        "learned art to the song magic of the Icelandic galdor: where "
        "natural magicians usually work their will directly, his spells "
        "conjured an airy spirit to do the deed. Many Icelandic magicians "
        "took up this theurgy, though its roots are heathen (LFI p. 42).",
    )
    b.university(
        "Skalholt Cathedral School",
        place=skalholt,
        summary="One of the two cathedral schools, each with its centre for "
        "the study of magic. Its magicians are priests, often indiscreet, "
        "whose office puts them beyond reproach; they are credited with "
        "prophecy through astronomy. Fewer than two dozen schooled "
        "galdramen exist at any one time, between the schools. Skalholt's "
        "name is unstained: its members use their art only for the good of "
        "their flock (LFI p. 42).",
        secrets="It seeks a breakthrough to match the feats of Iceland's "
        "pagan magicians, as Holar does (LFI p. 42).",
    )
    b.university(
        "Holar Cathedral School",
        place=holar,
        summary="The northern of the two cathedral schools, each with its "
        "centre for the study of magic. Its magicians are priests, often "
        "indiscreet, whose office puts them beyond reproach; they are "
        "credited with prophecy through astronomy (LFI p. 42).",
        secrets="The two schools have drifted apart, and Holar has grown "
        "darker: it is whispered that it uses magic to enslave true demons. "
        "It too seeks a breakthrough to match the feats of Iceland's pagan "
        "magicians (LFI p. 42).",
    )


def _monasteries(b: Builder, skalholt: Neighbour) -> Neighbour:
    common = (
        "Like all Iceland's houses it is tiny, poor and hard put to make ends "
        "meet, with scribes who both copy and write (LFI p. 44)."
    )
    for name, order, founded in (
        ("Thingeyrar", BENEDICTINE, 1112),
        ("Munkathvera", BENEDICTINE, 1155),
        ("Thykkvibaer", AUGUSTINIAN, 1168),
        ("Kirkjubaer", BENEDICTINE, 1186),
    ):
        house = _place(b, name, f"Home of a small {order} monastery (LFI p. 44).")
        b.church(
            f"{name} Monastery",
            church=MONASTERY,
            order=order,
            founded=founded,
            place=house,
            summary=paragraphs(
                f"A {order} house founded in {founded}, a centre of learning "
                "and instruction. Icelandic monasteries seldom hold more than "
                "ten monks, and are often set up with the help of a godi or "
                "bondi who then retires to them.",
                common,
            ),
        )
    _place(
        b,
        "Videy",
        "The site of a planned Augustinian monastery, not yet built (LFI p. 44).",
        secrets="The map (p. 10) marks it as a monastery already.",
    )
    helgafell = _place(
        b,
        "Helgafell",
        "On the Snaefellsnes peninsula, with a small monastery.",
        inside=_named(b, "Western Quarter"),
    )
    b.church(
        "Helgafell Monastery",
        church=MONASTERY,
        place=helgafell,
        summary="A small house on the Snaefellsnes peninsula.",
        secrets="Printed only on the map (p. 10). The list of houses on p. 44 "
        "leaves it out, and no order or date is given.",
    )
    return b.church(
        "Kirkjubaer Nunnery",
        church=MONASTERY,
        founded=1186,
        place=_named(b, "Kirkjubaer"),
        ruler="The Abbess of Kirkjubaer",
        summary="The nunnery at Kirkjubaer, founded in 1186 and home to seven "
        "nuns under an Abbess. It is nearly self-sufficient, yet in financial "
        "trouble and under the control of Skalholt (LFI p. 44).",
    )


# -- stories --


def _stories(b: Builder, skalholt: Neighbour, nunnery: Neighbour) -> None:
    dormant(
        b.threat(
            "The Outlaw's Son",
            summary="A man the covenant cannot do without proves to be the "
            "son of an outlaw, a vargdropi ('wolf-droppings'), which by law "
            "leaves him as exposed as his father. The father killed a man "
            "and his kin paid no blood money, so the dead man's sons want "
            "his blood too (LFI p. 39).",
            secrets="The safest road is to have a court rule on his status "
            "and, with luck, declare him free. That takes careful politics, "
            "for he has enemies well placed.",
            antagonist="The sons of the murdered man",
        )
    )
    dormant(
        b.threat(
            "Outlawing a Powerful Enemy",
            summary="An outlaw may be killed by anyone, so the surest answer "
            "to a mighty foe is to have him outlawed. But a powerful man has "
            "powerful friends even when the facts are against him, and in "
            "Iceland power means a deep hand in politics (LFI p. 39).",
        )
    )
    dormant(
        b.threat(
            "A Covenant Needs Land",
            summary="A covenant is a household, and in Iceland no household "
            "can appear from nowhere and claim land. All usable farmland has "
            "an owner whose family lives by it and will not gladly sell. "
            "Tenancy is demeaning and open to the landlord's demands; being "
            "a bondi is hard to reach, best done by inheriting, and brings "
            "many obligations (LFI p. 39).",
        )
    )
    dormant(
        b.threat(
            "The Nuns of Kirkjubaer",
            summary="The nuns must find enough to live on or Skalholt will "
            "disband them, and word of rich foreign scholars has reached "
            "them (LFI p. 44).",
            antagonist="Skalholt",
            place=nunnery,
            stages=[
                S(
                    "The Abbess petitions the covenant",
                    at=1,
                    clues="She journeys to the magi herself to ask for aid.",
                    ignored="Skalholt disbands the nuns.",
                    stopped="A gift is easily borne by the covenant, wins much "
                    "good will and eases fear of the foreign magicians.",
                ),
                S(
                    "The monasteries come asking",
                    at=2,
                    clues="Only if the covenant was too generous to the nuns.",
                ),
            ],
        )
    )
    b.link(nunnery, "places", skalholt, "Under its control")
