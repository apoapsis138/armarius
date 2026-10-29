"""Mundane England and Wales in 1220 (ch04-ch09, ch11; S15, S16): the king
and the triumvirate, Llywelyn and the king of Scots, the great nobles,
Nicola de Hay and Falkes de Bréauté, the bishops, the great abbeys, the
towns with their mayors, the two universities and the Jews of England.

The king is named as the Normandy pack names him, "Henry III of England",
so the two packs share him. The sheriffs and royal justices are a list in
the king's notes, not records (S15). The bishops' sees are Divine 5 as
cathedrals, the abbeys 5 as major monasteries, and the towns Divine 3
over most of them (DE p. 418)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..builder import paragraphs

if TYPE_CHECKING:
    from ...models import Neighbour
    from ..records import Records

SHERIFFS = (
    "Sheriffs in 1220 (p. 107): Bedfordshire, Buckinghamshire, "
    "Cambridgeshire, Huntingdonshire, Northamptonshire, Oxfordshire and "
    "Rutland, Falkes de Bréauté; Berkshire, Richard fitz Regis; Cheshire and "
    "County Durham, palatinates of the earl of Chester and the bishop of "
    "Durham; Cornwall, Henry fitz Count; Cumberland and Westmoreland, Robert "
    "de Vieuxpont; Derbyshire and Nottinghamshire, Philip Mark; Devon, Robert "
    "de Courtenay; Dorset and Somerset, Peter de Maulay; Essex and "
    "Hertfordshire, Aimery de St. Amand; Gloucestershire, Ralph Musard; "
    "Hampshire, Peter des Roches; Herefordshire, Walter de Lacy; Kent, Norfolk "
    "and Suffolk, Hubert de Burgh; Lancashire, Shropshire and Staffordshire, "
    "Ranulf earl of Chester; Leicestershire and Warwickshire, William de "
    "Cantilupe; Lincolnshire (contested by Nicola de Hay) and Wiltshire, "
    "William Longespee earl of Salisbury; Middlesex, none, governed by the "
    "court; Northumberland, Philip of Oldcoates; Surrey, William de Warenne; "
    "Sussex, Matthew fitz Herbert; Worcestershire, William de Beauchamp; "
    "Yorkshire, Geoffrey de Neville."
)
JUSTICES = (
    "The royal court: the King's Bench sits at Westminster under its senior "
    "justice Martin of Pattishall, and the eyre goes round the shires since "
    "1218; the justices in 1220 include John of Guestling, Ralf Hareng, "
    "Thomas of Heydon, Robert of Lexington and Stephen of Segrave. The "
    "Exchequer, under the treasurer Eustace de Faukenberg, sits at Michaelmas "
    "and in March; the Chancery is headed by the chancellor Richard de Marsh, "
    "but there is no Great Seal while the king is a minor, and the "
    "vice-chancellor Ralph de Neville does its work."
)


def build(records: Records) -> None:
    _crown(records)
    _nobles(records)
    _church(records)
    _towns(records)
    _factions(records)


def _crown(records: Records) -> None:
    b, w, p = records.b, records.world, records.places
    england = p["england"]
    w["king"] = b.lord(
        "Henry III of England",
        title="duke",
        wealth="Wealthy",
        manors=0,
        seat="Westminster",
        place=england,
        summary=paragraphs(
            "Born 1 October 1207 and king since 18 October 1216, aged twelve: "
            "too young to rule, so power lies with the triumvirate of the "
            "legate Pandulf, Peter des Roches and Hubert de Burgh. He may claim "
            "his majority in as few as three years, and men jockey for his "
            "favour. Des Roches, his guardian, has made him pious, devoted to "
            "Saint Edward the Confessor, respectful of his father's memory and "
            "sure that a king's will is law, and given him a love of hunting "
            "and luxury. A handsome boy, always kingly dressed and guarded, "
            "rarely without one of the triumvirs.",
            "Royal authority is weak: sheriffs and castellans hold that they "
            "cannot be removed until he comes of age and keep the shires' "
            "revenue; nobles keep royal manors given them by John or taken in "
            "the war; the treaty with Louis owes 10,000 marks and the return "
            "of lands nobody will give back; and his strongest officers, the "
            "earls of Chester, Salisbury and Derby and Falkes de Bréauté, obey "
            "only what suits them. The Church is wholly on his side. Abroad, "
            "Llywelyn acknowledges him and ignores him, Alexander II of Scots "
            "wants the northern counties Louis promised him, the justiciar of "
            "Ireland will not come to account, and the truce in Poitou is "
            "about to run out; his mother, Queen Isabella, countess of "
            "Angoulême and wife of Hugh de Lusignan, threatens to withdraw her "
            "support.",
            SHERIFFS,
            JUSTICES,
        ),
    )
    w["hubert_de_burgh"] = b.lord(
        "Hubert de Burgh",
        title="landed",
        wealth="Wealthy",
        manors=0,
        seat="Dover",
        answers_to=w["king"],
        place=england,
        summary="Justiciar since 1215, who runs the kingdom's finance, justice "
        "and patronage and is fast becoming its real power: nephew of Henry "
        "II's steward, keeper of Arthur of Brittany (whom, rumour says, he "
        "refused John's order to kill), defender of Chinon and of Dover "
        "against Louis, and victor over Eustace the Monk's fleet off Sandwich, "
        "which ended the war. Very loyal to the king, but building wealth of "
        "his own; he remembers John. Rival of the earl of Chester.",
    )
    w["llywelyn"] = b.lord(
        "Llywelyn ab Iorwerth, Prince of Gwynedd",
        title="duke",
        wealth="Wealthy",
        manors=0,
        seat="Aberffraw",
        place=p["wales"],
        summary="Llywelyn the Great, Prince of Gwynedd since 1194, married to "
        "Joan, John's daughter, who swore fealty in 1218. In the war he took "
        "south Wales, but for the Marshal lands in the far south-west and "
        "south-east, and now disposes of the principality as he wishes, at "
        "constant low war with the Marcher barons and refusing royal judgement. "
        "The Prince of Gwynedd has set a court date to examine Gwrhyr of Cad "
        "Gadu, the island's seemingly immortal owner.",
    )
    w["alexander"] = b.lord(
        "Alexander II, King of Scots",
        title="duke",
        wealth="Wealthy",
        manors=0,
        place=england,
        summary="Fought on Louis's side in the war, and presses for the "
        "treaties of 1209 and 1212 to be reconsidered; Louis promised him the "
        "three northern counties, and he may try to take them. He holds the "
        "English earldoms of Cambridge, Northampton and Huntingdon through his "
        "cousin John, his vassal, and Fotheringhay castle, which William "
        "Marshal the Younger will not give up to him.",
    )


#: The great nobles (p. 90), with the book's notes: (key, name, title,
#: region, summary).
NOBLES: tuple[tuple[str, str, str, str, str], ...] = (
    (
        "chester",
        "Ranulf de Blundeville, Earl of Chester",
        "count",
        "england",
        "Earl since 1180 and palatine, holding Cheshire with the king's own authority; absent on Crusade (at Damietta in 1219) and returning; sheriff of Lancashire, Shropshire and Staffordshire even in his absence. A rival of Hubert de Burgh.",
    ),
    (
        "arundel",
        "William de Albini, Earl of Arundel",
        "count",
        "england",
        "Absent on Crusade.",
    ),
    (
        "beauchamp",
        "William de Beauchamp of Bedford",
        "baron",
        "england",
        "A great baron, sheriff of Worcestershire.",
    ),
    (
        "warwick",
        "Henry de Beaumont, Earl of Warwick",
        "count",
        "england",
        "One of the great nobles.",
    ),
    (
        "norfolk",
        "Roger Bigod, Earl of Norfolk",
        "count",
        "england",
        "One of the great nobles.",
    ),
    (
        "hereford",
        "Humphrey de Bohun, Earl of Hereford",
        "count",
        "england",
        "One of the great nobles, and a Marcher lord.",
    ),
    (
        "gloucester",
        "Gilbert de Clare, Earl of Hertford and Gloucester",
        "count",
        "england",
        "One of the great nobles.",
    ),
    (
        "coleville",
        "Henry de Coleville of Bytham",
        "baron",
        "england",
        "One of the great nobles.",
    ),
    (
        "derby",
        "William de Ferrers, Earl of Derby",
        "count",
        "england",
        "Absent on Crusade, and one of the strong royal officers who obey the government only when it suits them.",
    ),
    (
        "aumale",
        "William de Fors, Count of Aumale",
        "count",
        "england",
        "His county is in Normandy, seized by Philip of France, so he keeps the title without the land. He holds the royal castle of Rockingham against the government's demands.",
    ),
    (
        "lacy",
        "Walter de Lacy of Ewias Lacy and Meath",
        "baron",
        "england",
        "A great baron of England and Ireland, sheriff of Herefordshire.",
    ),
    (
        "salisbury",
        "William Longespee, Earl of Salisbury",
        "count",
        "england",
        "A bastard of Henry II, sheriff of Wiltshire and of Lincolnshire, which Nicola de Hay contests: he seized Lincoln castle in 1219, she won it back with Falkes de Bréauté's help, and he tries to recover it by bribery or force.",
    ),
    (
        "essex",
        "William de Mandeville, Earl of Essex",
        "count",
        "england",
        "One of the great nobles.",
    ),
    (
        "winchester",
        "Roger de Quency, Earl of Winchester",
        "count",
        "england",
        "One of the great nobles.",
    ),
    (
        "devon",
        "Baldwin de Redvers, Earl of Devon",
        "count",
        "england",
        "Two years old; his county is ruled for him by Falkes de Bréauté, to the fury of Robert de Courtenay, the sheriff of Devon.",
    ),
    (
        "oxford",
        "Robert de Vere, Earl of Oxford",
        "count",
        "england",
        "One of the great nobles.",
    ),
    (
        "vieuxpont",
        "Robert de Vieuxpont, Lord of Westmoreland",
        "baron",
        "england",
        "Lord and sheriff of Westmoreland and Cumberland.",
    ),
    (
        "surrey",
        "William de Warenne, Earl of Surrey",
        "count",
        "england",
        "Sheriff of Surrey; Earl Warenne holds Stamford's great fair.",
    ),
    (
        "braose",
        "Reginald de Braose",
        "baron",
        "wales",
        "A Marcher lord whose main holdings are in Wales.",
    ),
    (
        "pembroke",
        "William Marshal the Younger, Earl of Pembroke",
        "count",
        "wales",
        "Son of the great William Marshal (died 14 May 1219, buried in the Temple church in London). He holds Fotheringhay castle against royal orders to give it to the king of Scots, and sues Falkes de Bréauté for four manors he says were granted only at his pleasure.",
    ),
    (
        "monmouth",
        "John of Monmouth",
        "baron",
        "wales",
        "A Marcher lord whose main holdings are in Wales.",
    ),
    (
        "mortimer",
        "Hugh de Mortimer of Wigmore",
        "baron",
        "wales",
        "A Marcher lord whose main holdings are in Wales.",
    ),
    (
        "nicola_de_hay",
        "Nicola de Hay",
        "landed",
        "england",
        "Hereditary constable of Lincoln castle and, arguably, rightful sheriff of Lincolnshire, in her early sixties, in dispute with the earl of Salisbury over both; Falkes de Bréauté is her ally.",
    ),
    (
        "falkes",
        "Falkes de Bréauté",
        "landed",
        "england",
        'Son of an unmarried Norman peasant and perhaps the most powerful man in England, "more a king than the king": a brave, skilled and ruthless soldier who served John loyally, sheriff of seven counties in the middle of the country, married to Margaret, widow of the earl of Albemarle and daughter of the earl of Devon, holding a dozen castles, and guardian since 1217 of the young earl of Devon. He refuses to give up any charge until the king is of age. The Church hates him: he rode into St Albans, killed a fleeing monk and took a hundred pounds from the abbot, then, after a dream, was beaten before the monks and begged forgiveness, and kept the money.',
    ),
)


def _nobles(records: Records) -> None:
    b, w, p = records.b, records.world, records.places
    for key, name, title, region, summary in NOBLES:
        w[key] = b.lord(
            name,
            title=title,
            wealth="Wealthy",
            manors=0,
            answers_to=w["king"],
            place=p[region],
            summary=summary,
        )


#: (key, name, kind, ruler, region, summary)
SEES: tuple[tuple[str, str, str, str, str, str], ...] = (
    (
        "canterbury",
        "The Archbishop of Canterbury",
        "Archbishop's cathedral",
        "Stephen Langton",
        "england",
        "Stephen Langton, born about 1165, archbishop since 1207: he cured a demoniac on the road to Rome, leads the inquiry into Hugh of Lincoln's sainthood, crowned Henry III again in May 1220, and wants the legate's authority ended. His see, worth over £2000 a year, is quarrelling with York over the archbishop's cross. Christ Church, the cathedral priory, is finishing Becket's shrine.",
    ),
    (
        "york",
        "The Archbishop of York",
        "Archbishop's cathedral",
        "Walter de Grey",
        "england",
        "Walter de Grey, elected 1215, at odds with Langton over the right to carry his cross.",
    ),
    (
        "durham",
        "The Bishop of Durham",
        "Bishop's cathedral",
        "Richard Marsh",
        "england",
        "Richard Marsh, bishop since 1217 and the king's chancellor, palatine lord of County Durham with the king's own authority, quarrelling with his monks and rumoured to worship the Devil. Saint Cuthbert's shrine is one of the four great pilgrimages; the see is worth over £2000.",
    ),
    (
        "winchester_see",
        "The Bishop of Winchester",
        "Bishop's cathedral",
        "Peter des Roches",
        "england",
        "Peter des Roches, born 1168, bishop since 1205, of Tours: John's loyal servant, guardian and tutor of the king, one of the triumvirate and sheriff of Hampshire, the richest see in England (over £3500 a year). Warrior, patron of scholars, scornful of Magna Carta, he led troops at Lincoln; unpopular, and lately pushed aside by his fellow triumvirs.",
    ),
    (
        "bath",
        "The Bishop of Bath and Wells",
        "Bishop's cathedral",
        "Jocelyn of Wells",
        "england",
        "Jocelyn of Wells, brother of Hugh of Lincoln.",
    ),
    (
        "chichester",
        "The Bishop of Chichester",
        "Bishop's cathedral",
        "Ralph Wareham",
        "england",
        "A bishop of 1220.",
    ),
    (
        "lichfield",
        "The Bishop of Coventry and Lichfield",
        "Bishop's cathedral",
        "William of Cornhill",
        "england",
        "A bishop of 1220.",
    ),
    (
        "ely",
        "The Bishop of Ely",
        "Bishop's cathedral",
        "John de Fountains",
        "england",
        "John de Fountains, once abbot of Fountains. Saint Etheldreda's shrine is one of the four great pilgrimages; the see is worth over £2000.",
    ),
    (
        "exeter_see",
        "The Bishop of Exeter",
        "Bishop's cathedral",
        "Simon of Apulia",
        "england",
        "A bishop of 1220.",
    ),
    (
        "hereford_see",
        "The Bishop of Hereford",
        "Bishop's cathedral",
        "Hugh Foliot",
        "england",
        "Hugh Foliot, bishop since 1219, whose official is Master Robert Grosseteste.",
    ),
    (
        "lincoln_see",
        "The Bishop of Lincoln",
        "Bishop's cathedral",
        "Hugh of Wells",
        "england",
        "Hugh of Wells, brother of Jocelyn of Bath. His minster has been rebuilt since 1192 by Saint Hugh, now considered for canonisation.",
    ),
    (
        "london_see",
        "The Bishop of London",
        "Bishop's cathedral",
        "William de St Mere Eglise",
        "england",
        "His cathedral is St Paul's.",
    ),
    (
        "norwich",
        "The Bishop of Norwich",
        "Bishop's cathedral",
        "Pandulf",
        "england",
        "Pandulf, the papal legate, elected in 1214 but not consecrated, which would put him under Canterbury.",
    ),
    (
        "rochester",
        "The Bishop of Rochester",
        "Bishop's cathedral",
        "Benedict of Sawston",
        "england",
        "The poorest see, about £200 a year.",
    ),
    (
        "salisbury_see",
        "The Bishop of Salisbury",
        "Bishop's cathedral",
        "Richard le Poore",
        "england",
        "A bishop of 1220.",
    ),
    (
        "worcester",
        "The Bishop of Worcester",
        "Bishop's cathedral",
        "William of Blois",
        "england",
        "A bishop of 1220.",
    ),
    (
        "carlisle",
        "The Bishop of Carlisle",
        "Bishop's cathedral",
        "Hugh of Beaulieu",
        "england",
        "A bishop of 1220.",
    ),
    (
        "st_asaph",
        "The Bishop of St Asaph",
        "Bishop's cathedral",
        "Renier",
        "wales",
        "A Welsh bishop of 1220.",
    ),
    (
        "bangor",
        "The Bishop of Bangor",
        "Bishop's cathedral",
        "Cadwgan",
        "wales",
        "A Welsh bishop of 1220.",
    ),
    (
        "st_davids",
        "The Bishop of St David's",
        "Bishop's cathedral",
        "Iorwerth",
        "wales",
        "A Welsh bishop of 1220; Gerald of Wales campaigns to make the see an archbishopric.",
    ),
    (
        "llandaff",
        "The Bishop of Llandaff",
        "Bishop's cathedral",
        "William",
        "wales",
        "A Welsh bishop of 1220.",
    ),
    (
        "legate",
        "The Papal Legate",
        "Large urban church",
        "Pandulf",
        "england",
        "Pandulf, an Italian of the Papal Curia, legate since 1218 and in theory the most powerful man in England, since the Pope is the king's overlord. He stood up to John over the interdict in 1211, took his surrender in 1213, and has made many of the reconciliations since the war; loyal to the throne, an able diplomat, greedy for his followers and high-handed. Peter's Pence is paid through him.",
    ),
)

#: (key, name, region, founded, summary)
ABBEYS: tuple[tuple[str, str, str, int | None, str], ...] = (
    (
        "glastonbury",
        "Glastonbury Abbey",
        "england",
        None,
        "The oldest and richest monastery in England, on the Isle of Avalon, where Arthur's grave was found in 1190 and Joseph of Arimathea is said to have come. Saint Collen faced Gwynn ab Nudd's faerie castle on the Tor, and Saint Dunstan seized the Devil by the nose. It burned in 1184; its union with Bath, from 1195, was dissolved by Honorius III in 1219, and Abbot William of St Vigor may wear the mitre.",
    ),
    (
        "bury",
        "The Abbey of Bury St Edmunds",
        "england",
        633,
        "Founded in 633, with Saint Edmund's shrine, one of the four great pilgrimages; exempt, its abbot rules the town and West Suffolk. Abbot Hugh was elected in 1215, settled at Runnymede; the spire fell in 1210.",
    ),
    (
        "fountains",
        "Fountains Abbey",
        "england",
        1132,
        "A Cistercian abbey founded in 1132 by monks from York, about 120 monks and 400 lay brothers, under its new abbot John of Kent; its last abbot is now bishop of Ely, and it has a daughter house at Lysa in Norway.",
    ),
    (
        "st_albans",
        "The Abbey of St Albans",
        "england",
        None,
        "A great Benedictine house whose art is famous: Walter of Colchester designs Becket's shrine. Falkes de Bréauté violated its sanctuary and kept the hundred pounds he took.",
    ),
    (
        "christ_church",
        "Christ Church, Canterbury",
        "england",
        None,
        "The cathedral priory of Canterbury, whose shrine of Saint Thomas is nearly done for his translation: the greatest pilgrimage in England.",
    ),
    (
        "st_augustines",
        "The Abbey of St Augustine, Canterbury",
        "england",
        None,
        "A Benedictine abbey with the relics of Saint Augustine.",
    ),
)


def _church(records: Records) -> None:
    b, w, p = records.b, records.world, records.places
    for key, name, kind, ruler, region, summary in SEES:
        w[key] = b.church(
            name, church=kind, ruler=ruler, place=p[region], summary=summary
        )
    for key, name, region, founded, summary in ABBEYS:
        w[key] = b.church(
            name,
            church="Monastery or nunnery",
            order="Benedictine" if key != "fountains" else "Cistercian",
            founded=founded,
            place=p[region],
            summary=summary,
        )


#: (key, name, population, ruler key, summary)
TOWNS: tuple[tuple[str, str, int | None, str, str], ...] = (
    (
        "london",
        "London",
        20000,
        "king",
        "About 20,000 people under the mayor Serlo le Mercer and twenty-four aldermen; some 120 parish churches, St Paul's, the Tower and the Templars' house; five mercantile gilds and the great families, Fitz Ailwin, Fitz Alulf, Viel and Eswy. Richard Renger, alderman of Bridge ward and sheriff, is likely the next mayor.",
    ),
    (
        "bristol",
        "Bristol",
        5000,
        "king",
        "About 5,000 people, with a mayor, a royal castle and the trade with Ireland.",
    ),
    (
        "cambridge",
        "Cambridge",
        None,
        "king",
        "A borough since 1207, with the Midsummer Fair of the Barnwell canons (22-25 June) and Stourbridge Fair (24-31 August), St Radegund's nunnery and the hospital of St John. Its university, since 1209, has about a hundred students, at least three of them natural magicians, thanks to Schola Pythagoranis at the edge of town.",
    ),
    (
        "canterbury_town",
        "Canterbury",
        6000,
        "king",
        "About 6,000 people, with six aldermen and portreeves and a gild merchant; Christ Church and St Augustine's, St Gregory's priory and St John's hospital, a royal castle (the sheriff of Kent's) and a second mint.",
    ),
    (
        "chester",
        "Chester",
        2000,
        "chester",
        "About 2,000 people in the earl's palatinate, with a mayor, St Werburgh's abbey (1092) and St John's. South of the river a shrine of Minerva is carved in the rock, left unharmed: a pagan site.",
    ),
    (
        "durham_town",
        "Durham",
        None,
        "durham",
        "Saint Cuthbert's cathedral and shrine and the castle, four boroughs and the barony of Elvet, under the palatine bishop.",
    ),
    (
        "exeter",
        "Exeter",
        None,
        "exeter_see",
        "A cathedral city with the mayor William Derling and eighteen churches in a single parish; the earl of Devon holds the docks, and the Exe bridge, the Gervase family's work, is unfinished.",
    ),
    (
        "lincoln",
        "Lincoln",
        None,
        "lincoln_see",
        "Its castle held by Nicola de Hay, its minster rebuilt by Saint Hugh, its mayor Peter Bridge and gild alderman John de Holm; sacked in 1217 after the battle.",
    ),
    (
        "oxford_town",
        "Oxford",
        None,
        "king",
        "A university town under the chancellor Geoffrey de Lucy, dispersed in 1209 and settled again in 1214 by Cardinal Nicholas; St Frideswide's priory, Oseney abbey and the collegiate church of St George in the castle.",
    ),
    (
        "winchester_town",
        "Winchester",
        8000,
        "winchester_see",
        "About 8,000 people under the mayor Elias Westman; the royal castle and the bishop's Wolvesey, St Swithun's cathedral priory, Hyde Abbey (burned in 1141), St Mary's nunnery and St John's hospital, and the bishop's St Giles's Fair. The court often sits here.",
    ),
    (
        "york_town",
        "York",
        8000,
        "york",
        "About 8,000 people, a borough since 1212 with a mayor and craft gilds; St Mary's Abbey under Robert of Longchamp, Holy Trinity priory, St Leonard's hospital, St Clement's nunnery and the Gilbertines of St Andrew's (1202), and the archbishop's fair (31 July-2 August). Its Jews were massacred in 1190.",
    ),
)


def _towns(records: Records) -> None:
    b, w, p = records.b, records.world, records.places
    for key, name, population, ruler, summary in TOWNS:
        lord: Neighbour | None = w.get(ruler)
        w[key] = b.town(
            name,
            population=population,
            answers_to=lord,
            place=p["england"],
            summary=paragraphs(summary, "Divine 3 over most of it (DE p. 418)."),
        )
    w["oxford_university"] = b.university(
        "The University of Oxford",
        school="University",
        place=w["oxford_town"],
        summary="Dispersed by the suspendium of 1209 and settled in 1214 by "
        "the legate Cardinal Nicholas, under its chancellor Geoffrey de Lucy.",
    )
    w["cambridge_university"] = b.university(
        "The University of Cambridge",
        school="University",
        place=w["cambridge"],
        summary="Drawn to Cambridge from Oxford in 1209 by Schola "
        "Pythagoranis's magi and kept there after 1215: about a hundred "
        "students, three of them at least natural magicians.",
    )


def _factions(records: Records) -> None:
    b, w, p = records.b, records.world, records.places
    w["triumvirate"] = b.faction(
        "The Triumvirate",
        faction="Other",
        decides="A council",
        members=3,
        place=p["england"],
        summary="The three who rule for the boy king since William Marshal "
        "died in 1219: Pandulf the legate, who leads and consults; Peter des "
        "Roches, bishop of Winchester, the king's guardian, now pushed aside; "
        "and Hubert de Burgh the justiciar, who holds the machinery of "
        "government and grows stronger.",
    )
    w["jews"] = b.faction(
        "The Jews of England",
        faction="Other",
        place=p["england"],
        summary="The king's Jews, under the archpresbyter Josce fil' Isaac of "
        "London: among them Rabbi Menahem of London, Rabbi Yom-Tob of Oxford "
        "and his son Moses, Rabbi Meir and Isaac of Norwich (fined 10,000 "
        "marks), Josce and Elias of Lincoln, and Chera Pinche of Winchester "
        "with her husband Isaac. Berechiah ben Natronai haNakdan of Oxford is a "
        "natural magician who may approach the Order. The Jews of York were "
        "massacred in 1190.",
    )


def finish(records: Records) -> None:
    w, m = records.world, records.magi
    for faction, key, note in (("jews", "berechiah", "A natural magician"),):
        if faction in w and key in m:
            records.b.link(w[faction], "characters", m[key], note)
    hereford, grosseteste = w.get("hereford_see"), m.get("grosseteste")
    if hereford is not None and grosseteste is not None:
        records.b.link(grosseteste, "neighbours", hereford, "The bishop he serves")
