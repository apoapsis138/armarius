"""Hungary, the north of the Transylvanian Tribunal, as of 1220: the
kingdom (places["hungary"]) with its counties, barons and peoples, the
Holy Crown as the Divine power that guarantees the magi their own law,
and King Coloman's law that there are no witches; the oppidum of
Laniena at the Aggtelek caves (Baradla, Dobsinska and Ochtinska), its
two magi and the Fectores it trains, with the secret of Murat of
Terezin; the thermal lake of Gyogy-to; King Andrew II, the palatine and
the barons; the archbishops of Esztergom and Kalocsa, the bishops of
Veszprém, Pécs and Oradea, the chapter of Székesfehérvár and
Pannonhalma; and the three court cities, Esztergom with the Order's
mansio, the Estate of the Wizards, Székesfehérvár and Veszprém with its
college. In paraphrase of Against the Dark chapter three (and chapter
one for Gyogy-to).

Keys: the region is places["hungary"]; the caves are
places["aggtelek"], ["baradla"], ["dobsinska"] and ["ochtinska"]; the
lake is places["gyogy_to"]; the mansio is places["estate_of_wizards"].
Laniena is covenants["laniena"], its magi magi["lexander"] and
magi["murat"]; Bendis, its chief Fector, is magi["bendis"], a companion.
Murat of Terezin, the elder, died and rose as a kukudhi vampire, so he
is no living magus: he is told in Laniena's notes, under Secrets, and
his kind is the Bestiary's."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...models.world import FULL
from ..builder import paragraphs
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Neighbour, Tribunal
    from ..builder import Builder
    from . import Transylvania

EX_MISC = "house_ex_miscellanea"
TREMERE = "house_tremere"

#: The lead line of an oppidum's notes, before its secrets.
KNOWN_ORDER: dict[str, Any] = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL: dict[str, Any] = {"status": "Known", "known": "In the Tribunal"}
KNOWN_REGION: dict[str, Any] = {"status": "Known", "known": "In the region"}
KNOWN_LOCALLY: dict[str, Any] = {"status": "Known", "known": "Locally"}


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
    _laniena(transylvania, b, tribunal)
    _lords(transylvania, b)
    _churches(transylvania, b)
    _towns(transylvania, b)
    _factions(transylvania, b)


# ------------------------------------------------------------- the region


def _region(transylvania: Transylvania) -> None:
    _add(
        transylvania,
        "hungary",
        "Hungary",
        summary=paragraphs(
            "The Magyar kingdom that holds the north of the Tribunal. "
            "Even beyond its borders, nobles of Hungarian blood and "
            "Hungarian quarters in the larger towns are common. King "
            "Andrew II rules it from a triangle of three court cities, "
            "Esztergom, Székesfehérvár and Veszprém, between which his "
            "court travels.",
            "The royal lands are cut into 72 counties (megye), each run "
            "from a fortified town of earth banks, ditch and timber wall "
            "by a count (ispán) the king appoints; most counts hold "
            "several and send deputies, the curial counts, to the rest. "
            "A count lives on peasant rents and a third of his county's "
            "taxes, tolls and fines, and ranks with a bishop. Private "
            "castles are against the law and stone ones almost unknown. "
            "Frontier counts guard marches of log and earth barriers, "
            "with an empty border zone beyond, watched by Szekler and "
            "Pecheneg horse archers. The fringes have no counties: a "
            "voivode governs Transylvania, a ban governs Croatia, and the "
            "Dalmatian cities rule themselves by treaty with the Crown.",
            "Andrew's 'new institutions' set twenty barons, chosen from "
            "the high nobility, above the counts: first the palatine, the "
            "judge royal, the ban of Croatia and the voivode of "
            "Transylvania, then the queen's and the chamber's masters, "
            "then the masters of horse, table and cup. He has given them "
            "huge royal estates, to arm them like western knights say his "
            "friends, to buy them and pay his crusade debts say his foes; "
            "since Hungarian land owes neither service nor tax, the gift "
            "goes further than any in France or Germany. Foreign "
            "settlements outside the counts' reach and the new class of "
            "freed royal servants have both cut into the counts' power.",
            "Hungarians are reserved, courteous and stiff about the "
            "precedence birth gives them; they put the family name first "
            "and never talk of money, though no other subject is "
            "forbidden. Serfs are chattels; most free men are still "
            "bound to fight or work for a lord, and only the gentry and "
            "foreigners enjoy 'golden freedom'. Castle folk, castle "
            "warriors, the half-free royal serfs (udvornici) and the "
            "villages that owe the court one fixed trade or good "
            "(conditionarii) fill out the ranks, and hospites, guests such "
            "as the Saxons and Szeklers, live under their own laws. Any "
            "landholder counts as noble, and the gentry claim descent from "
            "108 pagan chieftains of the conquest; the question of who is "
            "noble is still open, and the Golden Bull of 1222 may settle "
            "it on land, which would make most magi nobles without any "
            "oath. Villages are small and shifting, famine is almost "
            "unknown (the Quaesitors once checked for Hermetic meddling), "
            "and wheat is cheap.",
            "The king's wealth rivals any in Christendom: if Andrew is as "
            "rich as his grandfather Béla, a third of it comes from "
            "reminting the coin each year at the one royal mint in "
            "Esztergom, the rest from tolls, the counties' taxes, the salt "
            "monopoly, the Saxons, the counts' yearly gift and the "
            "Slavonians. All mines are his, and he takes a tenth of the "
            "gold panned in Transylvania. Making metal or coin by magic "
            "robs that revenue and could bring a royal army down on an "
            "oppidum; the Order would not protect the culprit.",
            "The Holy Crown. Hungarians hold that their crown, kept at "
            "Székesfehérvár, is a living Divine being linking God and man, "
            "ruling the land for the Virgin Mary, to whom Saint Stephen "
            "gave it; the kingdom is its body, all Hungarians are equal "
            "beneath it, and even a king may be lawfully resisted if he "
            "gives land to foreigners, meddles with others' land, brings "
            "in new kinds of justice, tramples the rights of natives or "
            "foreigners, or fails to defend the faith. Magi who stand "
            "against corrupt nobles have sometimes been helped by "
            "miracles. It is the Crown, not the king, that guarantees the "
            "magi their right to be judged by the Code; it intervenes "
            "rarely, but far more readily than any mortal king, and the "
            "Order dare not fail to police its own.",
            "No witches. King Coloman the Learned decreed in the eleventh "
            "century that witches do not exist and none may be tried; the "
            "Quaesitors found no magus behind it. The Order's magic counts "
            "in law as the custom of an ancient people, so magi keep their "
            "own laws and judges, as Saxons, crusading orders and "
            "Pechenegs do. The great nobles know of magi and bring "
            "complaints to Redcap envoys in discreet town mansiones, but "
            "do not tell a magus from a village cunning man, so the "
            "Tribunal polices hedge wizards too; a hedge wizard in deep "
            "trouble may claim trial under the Ancient Custom, though the "
            "Code punishes harder than any Hungarian court.",
            "The Church came with Saint Stephen as a tool of royal power "
            "and has stamped out paganism except among the Cumans. Every "
            "ten villages must build and furnish a church; laws on "
            "Christian conduct are harsh (talking in church earns a "
            "whipping), church lands are under royal protection, but "
            "paganism now draws only a fast, and Jews and Muslims serve "
            "the king in coinage and the treasury unhindered. Orthodox "
            "Romanians pay a sheep tax, the fiftieth, instead of tithe.",
            "Vis (each in its place): Gyogy-to (Ignem and Aquam), and "
            "Laniena's Aggtelek caves: Baradla (Imaginem and Muto), "
            "Dobsinska (Ignem) and Ochtinska (Rego).",
        ),
        **KNOWN_ORDER,
    )


# ---------------------------------------------------------------- places


def _places(transylvania: Transylvania) -> None:
    region = transylvania.places["hungary"]
    _add(
        transylvania,
        "gyogy_to",
        "Gyogy-to",
        inside=region,
        summary=paragraphs(
            "The biggest warm lake in Europe, beside Hévíz in the west of "
            "the kingdom. It yields both Ignem and Aquam vis, and as far as "
            "anyone knows, unlike many hot springs, it has no tie to Hell. "
            "There are traces of magic worked here by Romans and peoples "
            "before them. It lies just far enough from the Redcaps' road "
            "to Histria that no mansio stands here. A good site for a new "
            "oppidum; the book gives no aura.",
        ),
        **KNOWN_TRIBUNAL,
    )
    aggtelek = _add(
        transylvania,
        "aggtelek",
        "The Aggtelek Caves",
        inside=region,
        summary=paragraphs(
            "A cluster of limestone caves in the hills of northern Hungary, "
            "beautiful beyond words, many of them with a Magic aura. "
            "Laniena stands at the mouth of the greatest, Baradla, and "
            "gathers vis from three of them. Some passages are thought to "
            "join one cave to another.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        transylvania,
        "baradla",
        "Baradla Cave",
        inside=aggtelek,
        aura=5,
        summary=paragraphs(
            "The largest and grandest of the Aggtelek caves, with the "
            "strongest aura of them, Magic 5: more than sixteen miles of "
            "winding galleries, dead ends and hidden chambers, crowded "
            "with columns, flowstone and dripstone streaked red, green and "
            "violet, some of it slumped as though the rock had softened "
            "like candle wax. Imaginem and Muto vis are both found here "
            "(Laniena's).",
            "Only Lexander has explored it at length, and not all of it; "
            "he has warded every entrance he knows, because he turns "
            "vampires, werewolves and other captured horrors loose in the "
            "maze and sends his pupils after them.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        transylvania,
        "dobsinska",
        "Dobsinska Cave",
        inside=aggtelek,
        summary=(
            "A cave further north, entered by a single sheer shaft the "
            "locals call the studena diera, the cold hole, for the cave is "
            "full of ice even at midsummer; few will climb down for fear "
            "of freezing in its depths. Laniena gathers Ignem vis here. "
            "The book gives its aura no number."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        transylvania,
        "ochtinska",
        "Ochtinska Cave",
        inside=aggtelek,
        summary=(
            "One of the smallest caves and one of the strangest: its roof "
            "and walls sprout the 'flowers of iron', white tufts of stony "
            "needles like sea urchins. They are Rego vis, and also lesser "
            "enchantment vis that gives whoever bears one a personal Ward "
            "Against Faeries of the Earth (level 10, Penetration 10). "
            "Laniena's. The book gives its aura no number."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        transylvania,
        "estate_of_wizards",
        "The Estate of the Wizards",
        inside=region,
        summary=paragraphs(
            "A mansio in Esztergom kept by House Mercere where travelling "
            "magi may stay: a graceful three-storey house like a Roman "
            "villa, older than any record, which its people say once "
            "stood outside the town; the city has grown round it, and it "
            "now sits in a ring of formal gardens. Nobles who have a "
            "grievance against magi bring it here, and when the king's "
            "judges and the magi's servants dispute who should try a "
            "case, they argue it out here. That magi deal with mundanes "
            "through servants is an old right the Holy Crown protects. "
            "Other mansiones, public and private, are scattered about the "
            "Tribunal.",
        ),
        **KNOWN_ORDER,
    )


# ---------------------------------------------------------------- Laniena


def _laniena(transylvania: Transylvania, b: Builder, tribunal: Tribunal) -> None:
    baradla = transylvania.places["baradla"]
    summary = paragraphs(
        "The 'slaughterhouse': an oppidum at the mouth of Baradla Cave, "
        "the largest of the Aggtelek caves in northern Hungary, whose "
        "business is training the Fectores, House Tremere's hunters of "
        "supernatural foes, who use non-Hermetic Hunters' Arts drawn from "
        "the native magic of the Balkans. House Tremere counts the "
        "experiment a success. It began as part of the Scholomance and "
        "moved here when it became an oppidum of its own.",
        "A few solid houses lean against a tall half-moon wall across "
        "the cave mouth, and a dense hedge of black hawthorn, grown on "
        "purpose, rings the homes of the magi and covenfolk. Inside are "
        "an arena, smithies and carpenters' shops, a chirurgeon and an "
        "apothecary's laboratory.",
        "Two of every three Gifted youngsters found or sent here are "
        "trained as Fectores, five years under a Fector with Scry, Ban "
        "and Slay and three Foe Arts, and then join the Order as Gifted "
        "companions of House Ex Miscellanea; the other third become "
        "Murat's Hermetic apprentices, Hermetic Fectores. House Tremere "
        "forbids Hermetic training for dhampirs, who may still become "
        "Fectores. Trainees who prove unreliable never swear the Oath or "
        "learn Parma, and are spent on the most dangerous fronts. The "
        "Fectores serve House Tremere first, which makes some magi "
        "wonder what they are really for.",
        "Its two magi are the filii of its two founders and, unlike "
        "them, are always at odds. Anyone keen on the Hunters' Arts is "
        "welcome to join.",
    )
    what_matters = _lines(
        "Vis: Baradla Cave, Imaginem and Muto",
        "Vis: Dobsinska Cave, Ignem",
        "Vis: Ochtinska Cave, Rego (the flowers of iron, also lesser enchantment vis)",
        "Library: Murat of Terezin's initiation scripts for the Hunters' Arts, which Murat the Younger keeps from Lexander",
        "Services: trained Fectores for House Tremere, three in the time one apprentice takes",
        "Boon: Hedge Tradition (the Fectores)",
        "Boon: Veteran Fighters (elite warriors trained to fight under a Fector)",
        "Hook: Superiors (House Tremere, on whose sufferance it exists)",
        "Hook: Hermetic Politics (whether training Gifted children outside the Order is lawful)",
        "Hook: Dark Secret (Murat of Terezin's undeath)",
        "Tension: Lexander against Murat the Younger, over the scripts and the training",
    )
    notes = paragraphs(
        "History. About a century ago a dead magus's vampire hunted out "
        "dhampirs, saw them schooled as hunters, then slew them so they "
        "would rise as vampires; House Tremere has suffered vampire infiltration after a "
        "dhampir magus's death more than once, and now forbids its magi "
        "to take dhampir apprentices. The famous hunter Murat of Terezin "
        "came to Coeris then, and with Radomir of Tremere cleared the "
        "House of every vampire, Murat killing the nest's master himself. "
        "The two asked the Tribunal for an oppidum to train hunters, and "
        "once Murat had joined House Ex Miscellanea the Praeco agreed.",
        "The founders. Murat brought initiation scripts set down by a "
        "Gnostic scholar who had spied on a taltós clan for months; after "
        "years of trials he and Radomir learnt to Open a Gifted person to "
        "the Hunters' Arts. Radomir named them interfectores, slayers, "
        "soon shortened to Fectores. Radomir, a gifted young idealist, "
        "studied the necromancers called the Disciples of the Worm, whom "
        "he took for heirs of the Dacian necromancers who served "
        "Tremere, and his lore of ghosts and the walking dead fitted "
        "Murat's lore of vampires. Murat had found that the Arts work "
        "on more than vampires. Murat of Terezin trained three "
        "apprentices, the first Hermetic Fectores, a new societas of "
        "House Ex Miscellanea; the youngest, also named Murat, lives here.",
        "The law. Some magi say training a Gifted child as a Fector "
        "makes a delinquent master, since the child is kept from the "
        "Hermetic Arts. Laniena answers that trainees are not yet of the "
        "Order, so the Code does not protect them, and that each is "
        "offered the Order's protection as soon as trained, as Join or "
        "Die demands. The Tribunal, that is House Tremere, lets it go on, "
        "but could at any time accuse it of the High Crime of "
        "robbing a magus of his power.",
        "Hermetic Fectores take one Practice Art as their free Major "
        "non-Hermetic Virtue with its Foe Art, a Minor Magical Focus in "
        "harming one kind of creature as their free Minor Hermetic Virtue, "
        "and Weak Spontaneous Magic as their Major Hermetic Flaw. The "
        "Foe Arts the Fectores hold so far are five: Vampire, Werewolf, "
        "Ghost, Nightwalker and Witch. Murat's scripts can Open the "
        "Hunters' Arts or teach a new Foe Art, but hold nothing for the "
        "Practice Arts alone, so no unGifted Fector can be trained.",
        "Covenfolk: a band of elite warriors trained to fight under a "
        "Fector's command; Bendis is the ablest of the non-Hermetic "
        "Fectores. The book gives no founding year (soon after the purge "
        "of about a century ago) and no season.",
        "Story seeds: a character may be one of Murat of Terezin's "
        "children, doomed to slay her own father; and if Lexander learns "
        "that Murat the Younger has let a vampire live, House Tremere's "
        "anger could fall on the whole oppidum.",
    )
    hidden = _lines(
        "Murat of Terezin was secretly a dhampir himself. On his death he rose as a vampire, and has lasted long enough to become a kukudhi, a vampire that passes as human (see the Bestiary). He lives far from Laniena with his fourth mortal wife and has fathered more than twenty children, every one a dhampir.",
        "Only Murat the Younger knows. He lets the vampire be, because it gives the Fectores a steady stream of Faerie-blooded hunters and has given at least one Gifted child.",
    )
    laniena = b.covenant(
        "Laniena",
        tribunal=tribunal,
        founded=None,
        place=baradla,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        secrets=hidden,
        detail=FULL,
        season="Summer",
    )
    transylvania.covenants["laniena"] = laniena
    b.book(
        laniena,
        "The library of Laniena",
        "Other",
        language="Latin",
        description=(
            "No books are named. Its treasure is Murat of Terezin's store "
            "of initiation scripts for the Hunters' Arts, taken from a "
            "Gnostic scholar's record of a taltós clan, which Murat the "
            "Younger keeps to himself; the oppidum also keeps lore of "
            "vampires, ghosts and the walking dead from its founders."
        ),
    )
    m = transylvania.magi
    m["lexander"] = b.magus(
        "Lexander",
        covenant=laniena,
        house=TREMERE,
        age=63,
        summary=paragraphs(
            "Radomir's filius, looking forty-one, and a cives (of "
            "Coeris). He believes Laniena exists to train soldiers for "
            "House Tremere, and wants the Hunters' Arts stretched to every "
            "supernatural enemy the Order might face, but has neither the "
            "skill nor the knowledge to do it, so he nags Murat the "
            "Younger to; he has more than once floated 'Hermetic magus' "
            "as a Foe Art for hunting the Marched. Murat will not let him "
            "see his pater's scripts, so every recruit must pass through "
            "Murat's hands.",
            "He drills the Fectores without end against both steel and "
            "spells, catching monsters and setting them loose in the "
            "caves for his pupils to hunt, often at mortal risk. A master "
            "of Rego, above all with Vim, Corpus and Animal.",
        ),
        traits={"Argumentative": 3, "Brave": 2, "Harsh Task Master": 2},
    )
    m["murat"] = b.magus(
        "Murat the Younger",
        covenant=laniena,
        house=EX_MISC,
        age=52,
        summary=paragraphs(
            "A Hermetic Fector, the youngest of Murat of Terezin's three "
            "apprentices, who took his master's name at his Gauntlet; he "
            "looks forty-two. A hospes (of Diodorus), whose own agreement "
            "lets him take apprentices without the Praeco's leave, so that "
            "he trains as many as he can for the Tremere war machine.",
            "He is fascinated by the hunters of each region and often "
            "travels to chase word of a new way to fight vampires or ward "
            "off witches. He teaches his pupils the Ban Art above all, to "
            "give them a chance of living through Lexander's exercises, "
            "which only angers Lexander more. He holds his pater's "
            "initiation scripts.",
        ),
        traits={"Thirsty for Knowledge": 3, "Passive-Aggressive": 2, "Friendly": 1},
    )
    m["bendis"] = b.magus(
        "Bendis",
        covenant=laniena,
        house="",
        age=None,
        type="companion",
        summary=paragraphs(
            "The ablest of Laniena's non-Hermetic Fectores, named for the "
            "great mother goddess of the old Thracians: a warrior and a "
            "hedge wizard at once, in leather armour, with a bow and "
            "arrows made for killing vampires. She is a born leader and "
            "commands her own chosen band, trained in arms and in lore. "
            "The book prints no stats for her.",
        ),
    )
    b.link(
        m["lexander"],
        "characters",
        m["murat"],
        "Sodalis and constant rival; wants Murat's scripts",
    )
    p = transylvania.privileges
    p["lexander"] = ("cives", "")
    p["murat"] = ("hospites", "")
    # Laniena has one cives and one hospes: even numbers of each, so by
    # the Tribunal's rule it has two aediles.
    transylvania.aediles["laniena"] = ["lexander", "murat"]


# ------------------------------------------------------------ the world


def _lords(transylvania: Transylvania, b: Builder) -> None:
    w = transylvania.world
    region = transylvania.places["hungary"]
    w["hungary_kingdom"] = b.lord(
        "Kingdom of Hungary",
        title="duke",
        wealth="Wealthy",
        manors=72,
        seat="Esztergom",
        ruler="King Andrew II",
        place=region,
        summary=paragraphs(
            "King Andrew (Endre, Andreas) II of the house of Árpád, who "
            "came home from the Fifth Crusade in 1218 deep in debt after "
            "raising the biggest crusading army ever seen. He is pushing "
            "through his 'new institutions', handing royal land and power "
            "to a new rank of barons to make the realm stronger in war; "
            "the reform is half done and may prove a mistake, and the old "
            "nobility resents both the barons and the king's freed royal "
            "servants. He farms out offices for cash and is thinking of "
            "auctioning the mint itself.",
            "The king's own lands, the largest in the kingdom, are blocks "
            "of villages around royal manors (curtes), much of them "
            "royal forest kept by villages of foresters under a "
            "procurator. Unlike his nobles, the king does not split his "
            "lands among his sons. He is crowned by the Archbishop of "
            "Esztergom, at Székesfehérvár. The Church scolds him for his "
            "tolerance of Muslims, pagans and Jews. If history runs its "
            "course, his nobles force the Golden Bull on him in 1222.",
        ),
    )
    w["palatine"] = b.lord(
        "The Palatine of Hungary",
        title="count",
        wealth="Wealthy",
        answers_to=w["hungary_kingdom"],
        place=region,
        summary=(
            "First of the king's twenty barons, ranking with the judge "
            "royal, the ban of Croatia and the voivode of Transylvania "
            "above the rest. Barons are drawn from the high nobility and "
            "each holds at least one county; the king can remove one from "
            "office only by giving him something as rich. The book does "
            "not name the palatine."
        ),
    )


def _churches(transylvania: Transylvania, b: Builder) -> None:
    w = transylvania.world
    region = transylvania.places["hungary"]
    w["archbishop_esztergom"] = b.church(
        "Archbishopric of Esztergom",
        church="Archbishop's cathedral",
        place=region,
        summary=(
            "Head of the Hungarian Church, enthroned in the basilica of "
            "Saint Adalbert, who baptised the royal house, on the crown "
            "of Esztergom's castle hill. He alone may crown the king. In "
            "name the Church stands with the Crown; in truth it is loudly "
            "critical of the king's leniency to Muslims, pagans and Jews, "
            "and the royal palace next door keeps the quarrel quiet. A "
            "Count of the Mint who keeps the Muslim minters would clash "
            "with him. The archbishopric is among the Church's richest "
            "landholders, and the bishops of the realm answer to it or to "
            "Kalocsa. Magi value the bishops of Veszprém as a weight "
            "against him."
        ),
    )
    w["archbishop_kalocsa"] = b.church(
        "Archbishopric of Kalocsa",
        church="Archbishop's cathedral",
        answers_to=w["archbishop_esztergom"],
        place=region,
        summary=(
            "The second of Hungary's two archbishoprics, junior to "
            "Esztergom; part of the realm's bishops answer to it. With "
            "Esztergom it holds the largest church lands in the kingdom, "
            "and in theory it is a close ally of the king."
        ),
    )
    w["bishop_veszprem"] = b.church(
        "Bishopric of Veszprém",
        church="Bishop's cathedral",
        answers_to=w["archbishop_esztergom"],
        place=region,
        summary=(
            "The first bishopric of Hungary, founded by Saint Stephen. Its "
            "bishop has the old right to crown the queen; when another "
            "bishop crowned the present queen, the quarrel split the "
            "Hungarian Church until the Pope stepped in and confirmed "
            "Veszprém's right. Pannonhalma nearby is older and richer, so "
            "this is the poorest and weakest of the ancient sees, and its "
            "bishops usually stand close to the Order, which values them "
            "as a counterweight to the Archbishop of Esztergom."
        ),
    )
    w["bishop_pecs"] = b.church(
        "Bishopric of Pécs",
        church="Bishop's cathedral",
        answers_to=w["archbishop_esztergom"],
        place=region,
        summary=(
            "One of the two bishoprics, with Oradea, whose lands are "
            "among the largest the Church holds in Hungary after the two "
            "archbishoprics."
        ),
    )
    w["bishop_oradea"] = b.church(
        "Bishopric of Oradea",
        church="Bishop's cathedral",
        answers_to=w["archbishop_esztergom"],
        place=region,
        summary=(
            "A great landholding see (the book's Ordea), which keeps the "
            "Divine Dexter, Saint Stephen's mummified right hand, one of "
            "the kingdom's holiest relics."
        ),
    )
    w["chapter_szekesfehervar"] = b.church(
        "The Cathedral Chapter of Székesfehérvár",
        church="Bishop's cathedral",
        answers_to=w["archbishop_esztergom"],
        place=region,
        summary=(
            "The richest and mightiest cathedral chapter in Hungary, in "
            "Saint Stephen's basilica. It guards the Holy Crown, a living "
            "Divine being, and the tombs of the kings. Its provost ranks "
            "with a count, and archdeacons run each of its counties for "
            "him."
        ),
    )
    w["pannonhalma"] = b.church(
        "The Abbey of Pannonhalma",
        church="Monastery or nunnery",
        order="Benedictine",
        answers_to=w["archbishop_esztergom"],
        place=region,
        summary=(
            "The biggest and wealthiest monastery in Hungary, a "
            "Benedictine house older than the see of Veszprém nearby and "
            "the mother house of many others; in 1200 it ruled 2,200 "
            "households. Its wealth is one reason Veszprém is poor."
        ),
    )


def _towns(transylvania: Transylvania, b: Builder) -> None:
    w = transylvania.world
    region = transylvania.places["hungary"]
    kingdom = w["hungary_kingdom"]
    w["esztergom"] = b.town(
        "Esztergom",
        population=11000,
        charter="Noble lord",
        ruler="King Andrew II",
        answers_to=kingdom,
        place=region,
        summary=paragraphs(
            "The capital and biggest city of Hungary (the book's "
            "Esztergorm), an old camp of the Romans, of Attila and of the "
            "first Magyar king, where the roads to Kiev, Constantinople "
            "and Regensburg meet. The castle hill above the river holds "
            "the royal palace, built by western masons a few decades ago "
            "and the wonder of the realm, where foreign kings are always "
            "received, on the site of Saint Stephen's birthplace, so he "
            "is thought to watch closely over his heirs here; and the "
            "archbishop's basilica of Saint Adalbert. About 11,000 live in "
            "the town below, many of them foreign: craftsmen the king has "
            "hired and merchants, since the law makes every foreign trader "
            "offer his goods here first.",
            "The Order's mansio, the Estate of the Wizards, stands here "
            "amid its gardens. Here too is the realm's only mint, whose "
            "Khwarezmian minters (the kaliz) are sharp at spotting false "
            "coin: magi who make coins of created silver are likelier to "
            "be caught here than in any other Tribunal.",
            "Story seeds: the king, drowning in crusade debt, auctions the "
            "office of Count of the Mint each year, and magi could buy it "
            "openly or through a front, lawfully under the Code, though "
            "they must then hunt forgers and tax the miners; if they do "
            "not, a syndicate backed by Venetian bankers wins it, perhaps "
            "with House Mercere's domus magna behind it, and later the "
            "king splits the right among new mints at Csanád, Szerem, Buda "
            "and Zagreb. A faerie forger strikes coins bearing magi's "
            "sigils and oppida's marks. A royal coin inspector vanishes, "
            "perhaps tortured for his tests for forgery, and oppida race to "
            "find him for the king's favour or his secrets.",
        ),
    )
    w["szekesfehervar"] = b.town(
        "Székesfehérvár",
        charter="Noble lord",
        ruler="King Andrew II",
        answers_to=kingdom,
        place=region,
        summary=(
            "A city ringed by marsh, fortified by the first Magyar king, "
            "where Saint Stephen built a basilica and set a bishop; it has "
            "grown into the realm's centre of church learning, full of "
            "monasteries and churches and the largest cathedral school in "
            "the kingdom. Not the capital, but the city of ceremony: kings "
            "are always crowned here and, if they can be, buried here; "
            "pilgrimages begin here, the nobles meet here in their diets, "
            "and the regalia, the Holy Crown above all, are kept here, "
            "while the treasury proper is at Esztergom."
        ),
    )
    w["veszprem"] = b.town(
        "Veszprém",
        charter="Church",
        answers_to=w["bishop_veszprem"],
        place=region,
        summary=(
            "The smallest of the three court cities, its castle older than "
            "the Magyar conquest; Saint Stephen's queen loved it, and he "
            "founded Hungary's first bishopric here. It is home to the "
            "college that trains the king's diplomats, whose library is "
            "one of the best in the land. If the Dragon War comes, "
            "dragons may try to burn it."
        ),
    )
    w["veszprem_college"] = b.university(
        "The College of Veszprém",
        school="Cathedral school",
        answers_to=w["bishop_veszprem"],
        place=region,
        summary=(
            "Where royal envoys learn their trade: the liberal arts and "
            "law are taught. With Mostre's school in Bosnia it is the "
            "nearest thing the Tribunal has to a university. Its library, "
            "among Hungary's finest, has served more than one magus, by "
            "lucky browsing or quiet borrowing."
        ),
    )
    w["szekesfehervar_school"] = b.university(
        "The Cathedral School of Székesfehérvár",
        school="Cathedral school",
        answers_to=w["chapter_szekesfehervar"],
        place=region,
        summary="The largest cathedral school in the kingdom.",
    )


def _factions(transylvania: Transylvania, b: Builder) -> None:
    w = transylvania.world
    region = transylvania.places["hungary"]
    w["hungarian_barons"] = b.faction(
        "The Barons of Hungary",
        faction="Other",
        decides="Its leader",
        members=20,
        ruler="King Andrew II",
        place=region,
        wants="Royal land, office and precedence; the old nobility wants them curbed",
        offers="Armed retinues in the western style",
        summary=(
            "The twenty great officers of Andrew's new institutions, "
            "ranked by their titles above the counts and enriched with "
            "vast royal estates. The old counts and the gentry resent "
            "them, and the strain between old nobles and the king's newly "
            "freed men is growing; the quarrel may end in the Golden Bull."
        ),
    )
    w["kaliz"] = b.faction(
        "The Kaliz",
        faction="Gild",
        decides="A council",
        place=region,
        wants="To keep the mint and the king's favour",
        offers="Skill at minting and at catching forgers",
        summary=(
            "The king's minters, all Khwarezmian Muslims (Hungarians call "
            "every minter kaliz), with some thirty villages of Turks and "
            "many Jews in royal service in trade, coinage and the "
            "treasury; the Lateran Council's rules against them are not "
            "enforced. The Church dislikes them, and magi who stamped "
            "coin by magic and let them go might please the archbishop."
        ),
    )


# --------------------------------------------------------------- stats

P = Profile
HUNGARIAN = "Hungarian"


def _art(name: str, art: str) -> tuple[str, dict[str, str]]:
    return (name, {"art": art})


#: Each magus the chapter sketches without a stat block, by key.
PROFILES: dict[str, Profile] = {
    "lexander": P(
        strong="sta str int",
        weak="com pre",
        arts={"Re": 9, "Vi": 6, "Co": 6, "An": 6, "In": 3},
        abilities={
            "Leadership": (5, "training"),
            "Magic Lore": (4, "creatures"),
            "Single Weapon": (3, "sword"),
            "Hunt": (3, "monsters"),
            "Area Lore: Aggtelek Caves": 3,
            "Athletics": 2,
        },
        virtues=[
            _art("Affinity with {art}", "rego"),
            "Driven (Minor)",
            "Wrathful (Minor)",
        ],
        native=HUNGARIAN,
    ),
    "murat": P(
        strong="int per com",
        arts={"In": 6, "Pe": 5, "Co": 5, "Vi": 5, "Re": 4},
        abilities={
            "Magic Lore": (4, "hunters"),
            "Faerie Lore": (4, "vampires"),
            "Teaching": (4, "Fectores"),
            "Folk Ken": 2,
        },
        virtues=[
            "Ban Art",
            ("{foe} Art", {"foe": "vampire"}),
            ("Minor Magical Focus", {"focus": "harming vampires"}),
            "Weak Spontaneous Magic",
            "Driven (Minor)",
            "Dark Secret",
        ],
        native=HUNGARIAN,
    ),
}


def stats(transylvania: Transylvania) -> None:
    """Generated stats for Laniena's two magi, neither of whom has a
    printed stat block."""
    b = transylvania.b
    for key, profile in PROFILES.items():
        apply(b, transylvania.magi[key], profile)
