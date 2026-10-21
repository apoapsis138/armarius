"""The Divine and Infernal landscape of the Hibernian Tribunal, as of
1220, in paraphrase of The Contested Isle chapters twelve and thirteen:
the four archbishops, with the Irish and the Anglo-Irish Churches in
their notes (the paruchia and the comarba, confession and the sins no
penance can mend, the manaim, the Dublin council of 1186 and the bar on
Irish bishops the Pope struck down in 1220), the Waterford–Lismore
quarrel in Cashel's; the Céli Dé as a faction; and the Infernal: the
Cailleacha Phiseogach as a faction, Inis Doney with its nine Tartaran
regiones, Inis Saimera and Partholon's cup, and the Druim Leatan ridge.

The province parts own the places their chapters describe; `finish`
adds this part's detail to them: Mellifont's revolt (meath), Magh
Slécht (ulster), Dún Bhun na Gaillimhe and the Druim Leatan priory
(connacht), Vigil's drowned library (ulster), the Gaileoin's
infernalists in the Fir Bolg's notes (otherworld), and the Divine and
Infernal of the whole island in places["ireland"]'s (tribunal). Any of
them still missing is made here instead, so a stub elsewhere loses
nothing. The saints, the Harvest Thief, the Sluagh and Temoneth are the
Bestiary's.

Keys: world["armagh"], ["cashel"], ["dublin_see"], ["tuam"],
["celi_de"], ["cailleacha"]; places["inis_doney"], ["inis_doney_path"],
["inis_saimera"], ["druim_leatan"]; and world["mellifont"],
places["magh_slecht"], ["dun_gaillimhe"], world["druim_leatan_priory"]
when this part had to make them."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..builder import paragraphs

if TYPE_CHECKING:
    from ...models import Neighbour
    from . import Hibernia

KNOWN: dict[str, Any] = {"status": "Known", "known": "In the Tribunal"}
LOCAL: dict[str, Any] = {"status": "Rumoured", "known": "Locally"}

#: Each archbishop's province part (its place key) and the name of its
#: seat, if the province part made the seat as a record.
SEES: dict[str, tuple[str, tuple[str, ...]]] = {
    "armagh": ("ulster", ("Armagh",)),
    "cashel": ("munster", ("Cashel", "The Rock of Cashel", "Rock of Cashel")),
    "dublin_see": ("leinster", ("Dublin",)),
    "tuam": ("connacht", ("Tuam",)),
}


def build(hibernia: Hibernia) -> None:
    _archbishops(hibernia)
    _celi_de(hibernia)
    _cailleacha(hibernia)
    _infernal_places(hibernia)


# ------------------------------------------------------------ helpers


def _append(record: Neighbour, text: str, hidden: str = "") -> None:
    """Add `text` to the summary of a record another part made, and
    `hidden` at the end of its secrets."""
    record.summary = paragraphs(record.summary, text)
    record.secrets = paragraphs(record.secrets, hidden)


def _find(hibernia: Hibernia, *names: str, contains: str = "") -> Neighbour | None:
    """The first neighbour any part made with one of `names`, or whose
    name holds `contains` (case aside)."""
    neighbours = hibernia.b.saga.neighbours
    for name in names:
        found = next((n for n in neighbours if n.name == name), None)
        if found is not None:
            return found
    if contains:
        key = contains.casefold()
        return next((n for n in neighbours if key in n.name.casefold()), None)
    return None


def _place_in(record: Neighbour, place: Neighbour | None) -> None:
    if place is not None and record.place_id is None:
        record.place_id = place.id


# ------------------------------------------------------------ archbishops


IRISH_CHURCH = paragraphs(
    "The two Churches. By 1220 nearly everyone in Ireland accepts that "
    "the island has two Churches, both obedient to Rome and both parts "
    "of the one Western Church: the Irish Church of the native "
    "tradition, and the Anglo-Irish Church that looks to the English "
    "king and the English bishops. They fight over discipline and "
    "organisation, never doctrine, and each tries to put its own men "
    "into every vacant see; the papacy even files their letters as if "
    "they came from two nations, and now and then sends a legate to one "
    "and not the other. The Irish Church is itself split between a "
    "reform party, strongest among the bishops, which has pulled it "
    "toward the customs of the rest of Christendom, and traditionalists, "
    "mostly abbots of the old houses, who hold to the rule of monasteries "
    "founded by the apostolic saints. It runs on charters, bargains and "
    "particular arrangements rather than a grand structure: if a saint "
    "of old granted devils their due or faeries a place to dance, that "
    "grant can still stand. What little unity it has grows from its "
    "anger at the English churchmen taking over its hierarchy.",
    "Paruchia and comarba. A paruchia is not a parish but a family of "
    "monasteries, often far apart, owing allegiance to their founder's "
    "house, much as Normandy's vassal covenants owe their liege. Its head "
    "is the comarba, the abbot who succeeds the founding saint (the abbot "
    "of Columba's chief house is styled comarba Colum Cille). Reformers "
    "of the eleventh and twelfth centuries replaced this with dioceses "
    "of joined-up territory; bishops now hold the upper hand, though "
    "most traditionalists still follow the comarba, and in the last half "
    "century nearly the whole island has fallen to the diocesan party. "
    "Bishops grab at neighbouring sees as lords grab land: once for clan "
    "politics or the quarrel of reformers and traditionalists, now "
    "mostly as the Anglo-Irish Church reaches for the whole island.",
    "Confession and the sins beyond penance. Irish writers have produced "
    "so many penitentials that the whole Church respects their skill. "
    "The Irish hold confession strictly private between priest and "
    "sinner, and to betray it is held by many to be past forgiving. "
    "Saint Maelrúain of Tallaght's Rule names four sins no penance can "
    "answer in Ireland: lying with the dead, lying with one's sister or "
    "daughter, a priest or bishop falling into sin, and revealing a "
    "confession. The guilty can be excommunicated, refused the "
    "sacrament and driven into exile, and to traditionalists any sin "
    "repeated after penance is just as final. Reformers allow steep "
    "penances to the truly contrite and forgive a cleric's venial sins; "
    "the English allow penance broadly, think the Irish view dubious, "
    "and try and defrock any priest caught in these sins. A monk who "
    "sheds blood is usually sent into exile as his penance, as Columba "
    "was.",
    "Monks, manaim and schools. Most Irish priests are monks, and secular "
    "clergy are few, though the dioceses and the English (training "
    "priests at Dublin) are making more. The monasteries teach the eldest "
    "children of their neighbours, the poorest and even daughters, so "
    "Ireland has a broad literate class and many Irish characters take "
    "the Educated Virtue. Round many houses lives a village of manaim, "
    "lay brothers of the local sept who keep the devotions but marry, "
    "raise families and fight for the house; some become priests or "
    "bishops. Some priests marry or keep concubines and pass on their "
    "office, so a few sees are all but hereditary. Reformers and English "
    "alike call this abuse; even Laurence O'Toole, the reforming "
    "archbishop of Dublin who sought peace with the English, put up "
    "with it, and to shore up the Irish Church against the English he "
    "consecrated several Uí Conchobhair bishops late in the last "
    "century. Reformers want monks freed of sept loyalties; the "
    "Anglo-Irish want the monasteries remade in the continental orders' "
    "pattern.",
)

ANGLO_IRISH_CHURCH = paragraphs(
    "The Anglo-Irish Church. English churchmen condemn Irish reformers "
    "and traditionalists alike and want the Church in Ireland run as "
    "England's is. Under Prince John it became policy, later confirmed "
    "by a decree of Henry II, that no Irish-born man should be a bishop "
    "and that cathedral chapters must take the king's nominee instead of "
    "electing their own; even loyal Giraldus Cambrensis found the same "
    "wall in Wales. This is the reform party's deepest grievance. "
    "Henry II had a synod held at Cashel soon after he landed in 1171, "
    "which mostly served the reformers; the provincial council at Dublin "
    "that John called in 1186 showed how far the English meant to go: "
    "stone altars for wooden ones, new church furnishings, every "
    "cemetery blessed by a bishop before use, no Mass in private chapels "
    "without the priest's and bishop's leave, strict celibacy, only aged "
    "women or kin as a priest's servants, marriage reformed and "
    "concubinage frowned on (no concubine's son to be a priest), tithes "
    "enforced, laymen barred from taking dues or hospitality from "
    "churches by custom, and no Christian burial for hired archers. "
    "These bound only Leinster, Meath and later English Ulster, but "
    "were felt everywhere.",
    "Behind it lies politics: Pope Adrian's letter Laudabiliter "
    "licensed the English conquest so that the Irish Church's faults "
    "could be put right, so to admit the Irish Church is in good order "
    "is to undercut the Crown's title to Ireland. The Anglo-Irish follow "
    "the Archbishop of Dublin, and call Irish resistance to reform "
    "rebellion against Henry III in disguise. Now the Pope has upheld "
    "the right of Irishmen to be bishops at home and rebuked the "
    "English, and the quarrelling Irish Church has begun to close ranks "
    "against them.",
    "Petitioning the Pope. Both Churches have a long habit of taking "
    "disputes to Rome, whose word is final until the next appeal "
    "overturns it; a journey to Rome on such an errand makes a good "
    "story, and The Church (page 46) has rules for petitions.",
)

WATERFORD_LISMORE = paragraphs(
    "The Waterford–Lismore quarrel, the pattern of the age. The "
    "Anglo-Irish Bishop of Waterford set out to swallow Lismore: his "
    "knights took its cathedral and drove out Bishop Felix, who came "
    "back when that bishop died in 1199. King John's next man at "
    "Waterford, Robert, won the papal legate's union of the two sees and "
    "Felix retired, but Lismore's chapter defied the legate and chose "
    "Malachy, whom Robert's men seized and jailed. Malachy escaped to "
    "Rome; Innocent III restored the see, and in 1204 Malachy came home "
    "to find Robert dead. John's Welsh appointee David drove him out "
    "again; a second journey to Rome won him confirmation and men to see "
    "it done, and he returned in 1207 to find David murdered. Robert II, "
    "consecrated to Waterford only in 1210, again took Malachy by force; "
    "the Archbishop of Cashel had him restored, but armed men dragged "
    "him from the altar during Mass, with Robert present, and he was "
    "cruelly tortured. Robert was tried, yet nobody dared convict a "
    "favourite of the king. Malachy, freed, barely escaped killers at "
    "his own church door. Both sides petitioned the Pope, who put Malachy "
    "back in Lismore; with John dead, Waterford lost its backing, and "
    "both bishops still hold their sees in 1220 in an uneasy quiet.",
)


def _archbishops(hibernia: Hibernia) -> None:
    b = hibernia.b
    w = hibernia.world
    w["armagh"] = b.church(
        "Archdiocese of Armagh",
        church="Archbishop's cathedral",
        summary=paragraphs(
            "Irish Church. The see Saint Patrick founded, which many "
            "count the first church of Ireland; by old right its "
            "archbishop is primate of all the island, a claim the "
            "Archbishop of Dublin now openly disputes (Cashel's claim is "
            "the lesser one). Its province takes in the northern sees, "
            "and Triburnia (Kilmore) in Bréifne too, though Bréifne is "
            "subject to Connacht, a sore point with Tuam ever since. The "
            "archbishop keeps a fine library, where Oswald of Elk's Run "
            "copied many texts and learned the Ars Notoria. The book "
            "does not name the archbishop of 1220.",
            "Saint Malachy (Máel Máedóc) was archbishop from 1132 and "
            "drove the twelfth century's reform of the Irish Church; "
            "chapter twelve has him hold the see until his death in "
            "1148, but chapter nine and the record agree he resigned it "
            "in 1137 for the see of Down, and the pack follows them. "
            "Long before, an abbot of Armagh, Dub-dá-Lethe, went into "
            "Connacht to end twenty years of war within the Uí Briúin by "
            "casting out the demons that drove both sides.",
            IRISH_CHURCH,
        ),
    )
    w["cashel"] = b.church(
        "Archdiocese of Cashel",
        church="Archbishop's cathedral",
        summary=paragraphs(
            "Irish Church. The archbishop of Munster, on the Rock of "
            "Cashel, given to the Church by the Uí Briain so the "
            "Eoghanachta kings could never win back their old seat. Its "
            "claim to primacy is weaker than Armagh's or Dublin's. Henry "
            "II's synod of 1171 met here. In 1219 the archbishop went to "
            "Rome to plead for the Irish clergy against the bar on Irish "
            "bishops, and in August 1220 he came back with the Pope's "
            "answer: the policy is against Rome's will and must end at "
            "once. Word has not yet reached Dublin. The book does not "
            "name him.",
            WATERFORD_LISMORE,
        ),
    )
    w["dublin_see"] = b.church(
        "Archdiocese of Dublin",
        church="Archbishop's cathedral",
        ruler="Archbishop Henry de Londres",
        summary=paragraphs(
            "Anglo-Irish Church. The see of the English, held since "
            "the conquest by Englishmen (John Comyns after Laurence "
            "O'Toole, now Henry de Londres, who is also the king's "
            "viceroy). Its two cathedrals are Christchurch, the "
            "Norse foundation that once looked to Canterbury rather "
            "than Armagh, and the new Saint Patrick's. The "
            "archbishop leads the Anglo-Irish Church, trains "
            "secular priests for it, and claims for Dublin the "
            "primacy of Ireland over Armagh's ancient right and "
            "Cashel's lesser one, a claim that has at last turned "
            "even the Irish reformers against him. His rule against "
            "Irish-born bishops has been condemned by the Pope, "
            "though the news has not yet reached him. He has also "
            "vowed to put out Saint Brigid's undying fire at "
            "Kildare to prove it a superstition.",
            ANGLO_IRISH_CHURCH,
        ),
        secrets="When the Pope's ruling arrives from Cashel, the archbishop "
        "must either yield or find another road; a man who dared to "
        "burn his own tenants' deeds is unlikely to bow quietly.",
    )
    w["tuam"] = b.church(
        "Archdiocese of Tuam",
        church="Archbishop's cathedral",
        summary=paragraphs(
            "Irish Church. The archbishop of Connacht, whose province "
            "matches the kingdom and props up its crown: eight sees, "
            "Killala and Achonry in the north, Mayo, Tuam and Elphin "
            "across the middle, Annaghdown, Cill Mhic Dhuach and "
            "Clonfert in the south. Bréifne's see of Triburnia was put "
            "under Armagh instead, which Tuam has resented ever since. "
            "Tuam itself is a fading town: its cathedral burned in 1184 "
            "and has not been rebuilt, so the archbishop has no "
            "cathedral, though markets and fairs keep the town rich. "
            "The book does not name him. A town left rich but without "
            "its rulers, it suggests, is the kind the Infernal tempts.",
        ),
    )


# ------------------------------------------------------------ the Céli Dé


def _celi_de(hibernia: Hibernia) -> None:
    b = hibernia.b
    hibernia.world["celi_de"] = b.faction(
        "The Céli Dé",
        tradition="trad_celi_de",
        faction="Other",
        realm="Divine",
        rules=(
            "Not an order but a way of life under the Rule of Saint "
            "Maelrúain of Tallaght: two seasons a year of study, two of "
            "devotion and work; a strict diet and fasts; prayer standing "
            "with arms spread as on the cross; no self-scourging; "
            "confession to a fellow Céli Dé, the soul brother. Lay "
            "members may marry but keep the hours. A Céli Dé may be "
            "Poor but never Wealthy."
        ),
        wants="To keep their houses and customs out of the regular orders",
        offers="Miracles, learning and fine scribes; a soul brother's counsel",
        summary=paragraphs(
            "The Culdees to the English: ascetic Irish monks and devout "
            "laymen who split the year between their monastery and a "
            "hermit's cell, coming back to the community for saints' "
            "days and shared rites, and walking weekly to Mass at their "
            "abbey or a nearby church. Many work miracles; many are "
            "scribes and scholars. The last century's reforms have "
            "folded many into the regular orders, and others now live "
            "as manaim or married laymen, still keeping the old "
            "devotions. Reform has left few in Leinster and Munster; "
            "they hold on in the north and on the islands, a small "
            "tradition now. The Irish Church looks on them kindly, "
            "though reformers would turn their houses into ordinary "
            "ones of another order, which traditionalists resist; the "
            "English distrust their irregular ways and want them "
            "absorbed, though they leave devout lay members alone. Their "
            "practice of confessing to one another is dying out.",
            "They are loosely tied to the Coill Trí, which accepts some "
            "as members: they sit in the Túath Rónáin, though they "
            "mistrust its Cistercian ceannaire. Each judges a wizard by "
            "whether he uses his power for God or himself, and few "
            "Coill Trí care to quarrel with them. Three Gifted Céli Dé "
            "are magi of Ex Miscellanea at the Paruchia of Nerius.",
            "In play: a Céli Dé is a Companion or Mythic Companion with "
            "the Vows Flaw (even manaim vow to keep the hours), Purity "
            "and Transcendence unless he has True Faith, and the free "
            "Minor Virtue Educated; Ceremony does not suit them. Their "
            "Favoured Abilities are Invocation, Intervention, Purity and "
            "Transcendence, and one with True Faith learns them without "
            "the Virtues from the day of his vows (Realms of Power: The "
            "Divine).",
        ),
    )


# ------------------------------------------------------------ the witches


def _cailleacha(hibernia: Hibernia) -> None:
    b = hibernia.b
    hibernia.world["cailleacha"] = b.faction(
        "The Cailleacha Phiseogach",
        tradition="trad_cailleach_phiseogach",
        faction="Hedge coven",
        realm="Infernal",
        members=12,
        rules=(
            "Always women; each works alone, taking one apprentice, a "
            "girl stolen from her family and broken, who stays until her "
            "mistress dies. Each serves a lord in return for shelter and "
            "riches, and names her price for every service."
        ),
        wants="Sanctuary and wealth from the lords they serve",
        offers="Secrets of a patron's enemies, curses, spying, prophecy",
        summary=paragraphs(
            "Infernal witches dressed as wise women, who counsel the "
            "sons of the Irish clans; barely a dozen in all Ireland. "
            "Their maleficia bargain with and command supernatural "
            "beings, curse foes, watch from afar and look into past "
            "and future; they often call up spirits and creatures of "
            "the Magic and Faerie realms and bind them to a task, for "
            "their power is Infernal but their knowledge spans every "
            "realm. A Chailleach's place in her lord's household is "
            "respected but fragile, resting on what she can learn "
            "and give. They feed their magic with sacrifice and with "
            "profaning holy things.",
            "The Coill Trí know of them but rarely meet them and "
            "count them no great danger; some druids even seek one "
            "out for a service or a secret beyond their own powers.",
            "In play: a Chailleach is a Diabolist made as a Mythic "
            "Companion (Realms of Power: The Infernal, chapter ten): "
            "the Diabolist Special Virtue and the Wise One status "
            "free, then 10 points of Flaws for 20 of Virtues, half of "
            "them Infernal Supernatural Virtues, including Diablerie "
            "and Incantation. Often taken: Premonitions, Protection, "
            "Phantasm, Malediction, Infernal Heirloom and Mentored by "
            "Demons, with the Flaws Witch Marks, Tainted with Evil, "
            "Demonic Familiar and Social Handicap. The app has no "
            "record for the tradition, so it is sketched here.",
        ),
        secrets="Their lords rarely know what they harbour, and a "
        "Chailleach's counsel is the kind of quiet goad the demons of "
        "Hibernia prefer to open war.",
    )


# ------------------------------------------------------------ Infernal places


def _infernal_places(hibernia: Hibernia) -> None:
    b = hibernia.b
    p = hibernia.places
    p["inis_doney"] = b.place(
        "Inis Doney",
        realm="Divine",
        aura=5,
        summary=paragraphs(
            "A small island on Lough Erne whose finely built church "
            "carries a strong Divine aura (the book gives no number; 5 "
            "is the pack's): angels are said to come to it for their "
            "own Mass, and many local saints favour it. Most of the "
            "island is peaceful. But past the church a stony track runs "
            "down to a barren, hushed and cold place that no angel or "
            "saint can be made to look upon: the Dark Path, a road the "
            "Dominion never touches.",
        ),
        **KNOWN,
    )
    p["inis_doney_path"] = b.place(
        "The Dark Path of Inis Doney",
        inside=p["inis_doney"],
        realm="Infernal",
        aura=1,
        levels=[
            b.level(
                f"The Dark Path, descent {n}",
                n + 1,
                "Infernal",
                notes=(
                    "The last descent: the very brink of Hell."
                    if n == 9
                    else "A step further down toward Hell."
                ),
            )
            for n in range(1, 10)
        ],
        summary=paragraphs(
            "The barren ground beyond Inis Doney's church, an Infernal "
            "aura of 1 that is the mundane level of nine Tartaran "
            "regiones (see page 16 of Realms of Power: The Infernal), each a "
            "point stronger than the one above it as the track goes "
            "down. Whoever walks it to the edge of Hell and comes back "
            "to the church is free of demons for life: none may tempt "
            "him, possess him or stay beneath his roof.",
        ),
        **LOCAL,
    )
    p["inis_saimera"] = b.place(
        "Inis Saimera",
        realm="Infernal",
        summary=paragraphs(
            "An island where, somewhere underground, lies the Cup of "
            "Partholon: a horn of red gold worked with the tale of "
            "Partholon's voyage to Ireland. Partholon's wife Delgnat "
            "betrayed him with the servant Topa, and a demon let him "
            "taste their guilt on a cup they had shared; he had Topa "
            "killed, and so adultery and jealousy came to Ireland. A "
            "magus hunting a cathach may well go looking for so old "
            "a symbol of the island. The book gives no aura and does "
            "not say where the island is; the pack puts it in "
            "Ulster, at the mouth of the Erne.",
        ),
        secrets="The cup is an Infernal relic of betrayal. Anyone who sees it "
        "gains Envious +3 (Penetration 15) and the urge to betray "
        "whoever owns it and take it for himself.",
        **LOCAL,
    )
    ridge = _find(hibernia, contains="Druim Leatan")
    if ridge is not None and ridge.kind == "place":
        _append(ridge, DRUIM_LEATAN)
        p["druim_leatan"] = ridge
        return
    p["druim_leatan"] = b.place(
        "The Druim Leatan ridge",
        realm="Infernal",
        aura=4,
        summary=DRUIM_LEATAN,
        **LOCAL,
    )


DRUIM_LEATAN = (
    "The ridge dividing the Uí Ruairc from the Uí Raghallaigh in "
    "Bréifne, a few miles east of Magh Slécht. Its land carries a "
    "malevolent Infernal aura that now and then rises as high as 4 (the "
    "pack records the peak), and its demons egg both clans on to raid "
    "and avenge in equal measure. The priory on the ridge has a Dominion "
    "aura of 6, but as the mark of the boundary it is sacked and damaged "
    "again and again."
)


# ------------------------------------------------------------ finish


def finish(hibernia: Hibernia) -> None:
    """Seat each archbishop in his province, link the Céli Dé and the
    Mellifont revolt, and add this part's detail to the places and
    factions other parts made, making any still missing."""
    _seat_archbishops(hibernia)
    _link_celi_de(hibernia)
    _mellifont(hibernia)
    _place_infernal(hibernia)
    _magh_slecht(hibernia)
    _druim_leatan_priory(hibernia)
    _gaillimhe(hibernia)
    _gaileoin(hibernia)
    _vigil_library(hibernia)
    _ireland(hibernia)


def _seat_archbishops(hibernia: Hibernia) -> None:
    b = hibernia.b
    for key, (province, seats) in SEES.items():
        see = hibernia.world[key]
        _place_in(see, hibernia.places.get(province))
        seat = _find(hibernia, *seats)
        if seat is not None and seat is not see:
            b.link(see, "places", seat, "Its seat")
    viceroy = hibernia.world.get("viceroy")
    if viceroy is not None:
        b.link(
            hibernia.world["dublin_see"],
            "places",
            viceroy,
            "Its archbishop is the king's viceroy",
        )
    for found in list(b.saga.neighbours):
        if found.kind == "church" and (
            "Lismore" in found.name or "Waterford" in found.name
        ):
            _append(
                found,
                "Party to the Waterford–Lismore quarrel; see the "
                "Archdiocese of Cashel.",
            )
            b.link(found, "places", hibernia.world["cashel"], "The quarrel")


def _link_celi_de(hibernia: Hibernia) -> None:
    b = hibernia.b
    celi_de = hibernia.world["celi_de"]
    _place_in(celi_de, hibernia.places.get("ireland"))
    _place_in(hibernia.world["cailleacha"], hibernia.places.get("ireland"))
    paruchia = hibernia.covenants.get("paruchia")
    if paruchia is not None:
        b.link(celi_de, "covenants", paruchia, "Its Hermetic members")
    for key, note in (
        ("fedelmid", "Hermetic Céli Dé; comarba Nerius"),
        ("indrechtach", "Hermetic Céli Dé"),
    ):
        magus = hibernia.magi.get(key)
        if magus is not None:
            b.link(celi_de, "characters", magus, note)
    coill_tri = hibernia.world.get("coill_tri") or _find(
        hibernia, "The Coill Trí", "Coill Trí"
    )
    if coill_tri is not None:
        b.link(celi_de, "places", coill_tri, "Some sit in the Túath Rónáin")


def _mellifont(hibernia: Hibernia) -> None:
    b = hibernia.b
    revolt = (
        "Irish Church. In the quarrel of the two Churches the revolt "
        "stands for more than monastic discipline: since the invasion "
        "the Irish monks and the English Cistercians have pulled apart, "
        "and the Irish daughter houses that back the abbot are also "
        "backing an Irish house against an order the English favour."
    )
    found = next(
        (n for n in b.saga.neighbours if n.kind == "church" and "Mellifont" in n.name),
        None,
    )
    if found is not None:
        _append(found, revolt)
        mellifont = found
    else:
        mellifont = b.church(
            "Mellifont Abbey",
            church="Monastery or nunnery",
            order="Cistercian",
            founded=1140,
            place=hibernia.places.get("meath"),
            summary=paragraphs(
                "The greatest Cistercian house in Ireland, near "
                "Drogheda, founded by Saint Malachy in 1140 on land "
                "from the King of Meath; mother of Bective, "
                "Baltinglass and two dozen more. A hundred monks and "
                "three hundred lay brothers. Its first abbot, Saint "
                "Christian, worked with the reformers to bring in the "
                "dioceses, yet its abbots grew as mighty as any "
                "comarba: in 1154 a synod here unseated the King of "
                "Meath for his brother.",
                "The Conspiracy of Mellifont: rumours of corruption "
                "and debauchery reached Cîteaux, and in 1216 its "
                "visitors found the gates barred against them. The "
                "general chapter deposed Abbot Thomas in 1217, but he "
                "still rules, backed by his monks and the daughter "
                "houses, and Cîteaux, perhaps the Pope too, is "
                "readying a deputation to restore order.",
                revolt,
            ),
            secrets="The cause may be Irish against English, plain "
            "laxity, or something darker: the abbey's nine granges "
            "on the Brú na Bóinne sit among ancient sídhe and "
            "ráths, and the monks may have dug up an old secret "
            "(The Church, page 94, suggests an Infernal cause).",
        )
        hibernia.world["mellifont"] = mellifont
    b.link(
        mellifont, "places", hibernia.world["armagh"], "Founded by its old archbishop"
    )


def _place_infernal(hibernia: Hibernia) -> None:
    p = hibernia.places
    lough_erne = _find(hibernia, "Lough Erne", "Lower Lough Erne")
    _place_in(p["inis_doney"], lough_erne or p.get("ulster"))
    _place_in(p["inis_saimera"], p.get("ulster"))
    breifne = _find(hibernia, "Bréifne", "The Kingdom of Bréifne", "West Bréifne")
    if breifne is not None and breifne.kind == "place":
        _place_in(p["druim_leatan"], breifne)
    _place_in(p["druim_leatan"], p.get("connacht"))


MAGH_SLECHT = paragraphs(
    "The Infernal chapter tells it otherwise. A huge standing stone "
    "shaped as the god Crom Cruach and plated in beaten gold once rose "
    "among the drumlins of this plain in north-east Connacht, and here "
    "alone in Ireland the old people offered human sacrifice for mild "
    "winters and good harvests. Demons have always lived here, drawing "
    "men to the plain to shed one another's blood. Patrick drove the "
    "demon Crom Cruach deep under the earth and the sacrifices ended, "
    "but not the slaughter: the Diedne destroyed the surviving druids "
    "of the Masraige here in her pogrom, the Uí Raghallaigh fought the "
    "Uí Conchobhair and the Uí Ruairc here, and magi spilled one "
    "another's blood here in the Schism War. It is still thought a key "
    "to the land; if the saga follows history, the Uí Raghallaigh and "
    "the Uí Ruairc meet here again in 1256, and Bréifne is split between "
    "them. That chapter gives it a malevolent Infernal aura of 5, as one "
    "of the battlefields whose patron demons send dreams of victory to "
    "lure armies back; the Ulster chapter gives Faerie 3. The storyguide "
    "picks one, or keeps both: the faerie Crom Dubh mimicking the demon "
    "who truly haunts the plain.",
)


def _magh_slecht(hibernia: Hibernia) -> None:
    found = _find(hibernia, "Magh Sléacht", "Magh Slécht", contains="Magh Sl")
    if found is not None:
        _append(found, MAGH_SLECHT)
        return
    hibernia.places["magh_slecht"] = hibernia.b.place(
        "Magh Slécht",
        inside=hibernia.places.get("connacht"),
        realm="Infernal",
        aura=5,
        summary=MAGH_SLECHT,
        **KNOWN,
    )


def _druim_leatan_priory(hibernia: Hibernia) -> None:
    b = hibernia.b
    ridge = hibernia.places["druim_leatan"]
    text = (
        "Its Dominion aura is 6, higher than a priory's usual 5, but the "
        "ridge around it is malevolently Infernal (up to 4), and the "
        "demons there make the priory, as the boundary's mark, the "
        "first thing each side burns."
    )
    found = next(
        (
            n
            for n in b.saga.neighbours
            if n.kind == "church" and "Druim Leatan" in n.name
        ),
        None,
    )
    if found is not None:
        _append(found, text)
        _place_in(found, ridge)
        return
    hibernia.world["druim_leatan_priory"] = b.church(
        "Druim Leatan Priory",
        church="Monastery or nunnery",
        place=ridge,
        summary=paragraphs(
            "Irish Church (the book does not say; the pack assumes it, "
            "in Gaelic Bréifne). The priory on the ridge between the Uí "
            "Ruairc and the Uí Raghallaigh, which marks the boundary "
            "between them; if the saga follows history, it marks the "
            "line when Bréifne is split in 1256.",
            text,
        ),
    )


GAILLIMHE = (
    "The Infernal has its hand in the fort's failings: a naval base big "
    "ships cannot use, a stronghold that cannot be resupplied under "
    "siege, a garrison too far from the people to shield them from "
    "Munster raiders. Rebuilt and wrecked over and over, it gives its "
    "defenders false hope and its attackers easy prey, and its "
    "assailants are helped by demons whether they want it or not: "
    "bowstrings snap, walls weaken, and a safe way through the marsh "
    "shows itself, so that defence is futile and cruelty and despair "
    "grow. If the saga follows history, it is besieged again and again "
    "in the 1230s as the Normans push into Connacht; unless the "
    "Infernal is fought alongside them, it will go on falling."
)


def _gaillimhe(hibernia: Hibernia) -> None:
    found = _find(hibernia, "Dún Bhun na Gaillimhe", contains="Bhun na Gaillimhe")
    if found is not None:
        _append(found, GAILLIMHE)
        return
    hibernia.places["dun_gaillimhe"] = hibernia.b.place(
        "Dún Bhun na Gaillimhe",
        inside=hibernia.places.get("connacht"),
        realm="Infernal",
        aura=1,
        summary=paragraphs(
            "The Connachta fort at the mouth of the Corrib (the "
            "Gaillimhe). The book gives it Infernal influence but no "
            "aura; 1 is the pack's.",
            GAILLIMHE,
        ),
        **KNOWN,
    )


def _gaileoin(hibernia: Hibernia) -> None:
    fir_bolg = hibernia.world.get("fir_bolg") or _find(
        hibernia, "The Fir Bolg", "Fir Bolg"
    )
    if fir_bolg is None:
        return
    _append(
        fir_bolg,
        "",
        "The Gaileoin's infernalists work as the demons of Hibernia "
        "like best: not on the king himself but through those around "
        "him, by obsession and quiet counsel, so the feeble royal line "
        "seems to rule while others steer it. Their people's idleness "
        "and casual sins are the slow corruption the Infernal chapter "
        "describes, not open devil-worship. A Chailleach Phiseogach "
        "might make them allies; the walk of Inis Doney's Dark "
        "Path would free a Gaileoin king from any demon riding him.",
    )


def _vigil_library(hibernia: Hibernia) -> None:
    vigil = hibernia.covenants.get("vigil")
    if vigil is None:
        return
    vigil.notes = paragraphs(
        vigil.notes,
        "The drowned library, from the Infernal chapter: casting "
        "tablets and laboratory texts against Infernal sickness and "
        "foul weather, from the years when Vigil watched the north for "
        "demon-sent hardship and fought the demons behind it. The "
        "Infernal has lain quiet long enough for Vigil to sink into "
        "idleness, and the texts lie untouched in the flooded vaults "
        "under the lost fortress. Hermetic annals mention them, so a "
        "covenant struck by an Infernal winter or plague may come to "
        "Vigil asking for them.",
    )


DIVINE_IRELAND = paragraphs(
    "The Divine in Ireland. A land haunted by angels and shaped by "
    "saints, thick with monasteries and hermits' cells; its people are "
    "devout and call on Heaven often, but treat religion practically, "
    "unlike the English churchmen now ruling much of it (see the four "
    "archdioceses for the two Churches). Over a hundred saints are "
    "honoured here; Patrick, Brigid and Columba are the island's "
    "patrons, and any Irish character may call on them and the Virgin. "
    "Irish saints take a close interest in magicians, so the Meddlesome "
    "Saint Hook (Covenants, page 23) suits a Hibernian covenant well. "
    "The old Irish church bells, shaped like hollow pears with the "
    "clapper inside, are rare now; where one is rung it drives ghosts "
    "from all within earshot, as Ward Against Spirits 15 with "
    "Penetration 15 at Voice range, measured by the bell's sound.",
)

INFERNAL_IRELAND = paragraphs(
    "The Infernal in Ireland. Evil here hides in men's hearts and "
    "deeds: temptation, obsession and possession. It came early, with "
    "Partholon's jealousy (see Inis Saimera), then plague, which killed "
    "Partholon and his people save Tuan, then war, with Nemed's "
    "victories over the Fomórach paid for in his wife and sons; plague "
    "took him, the Fomórach enslaved his people for 207 years, and when "
    "they fled, a Fomórach flood left only thirty alive.",
    "How the demons work. They prefer to stay unseen and unheard, from "
    "cunning and cowardice rather than wisdom: anything that shows "
    "itself and boasts of serving Hell is probably not a demon. Two "
    "ways are favoured: crush a man until only the dark road is left, "
    "or feed his envy and obsession until he damns himself. Love, land "
    "and rank drive men to evil, so the demons give to those who have "
    "and take from those who have little. In the clans' wars they use "
    "Obsession on claimants and Possession on their advisers, rarely "
    "Envisioning, lest the dreams betray them. Plagues and famines among "
    "beasts and farmers are a favourite tool, often sparing a church "
    "or covenant so the starving neighbours learn to hate it; churches "
    "have been plundered for it, and covenants are wise to find the "
    "source before the hungry come for their stores. Winter is the "
    "dangerous season. By Patrick's miracle no demon in Ireland may "
    "take a serpent's shape; one that can coagulate must take another "
    "form or stay unseen. Fictiles (Realms of Power: The Infernal, page "
    "69) abound, and lesser demons rule storm, flood, fire, sickness, "
    "famine and even gates that come unlatched at night. Hedge "
    "traditions fight plague too, above all in Connacht, where the "
    "Order is absent.",
    "Their powers, beside Obsession and Possession: Winter's Chill (2 "
    "points, Init Qik -2, Auram), used daily over all the demon sees, "
    "so that anyone with Living Conditions of 0 or less makes a daily "
    "Deprivation check (ArM5 page 180) and loses a Long-Term Fatigue "
    "level for each failure; The Plague of Ages (Corpus, Init Qik "
    "-20, 10 points), the Curse of the Unportended Plague (ArM5 page 133) "
    "on a town or village, costing the demon 10 Might that comes back "
    "at a point a season spent wholly in an Infernal aura; and A Death "
    "in the Night (Animal or Corpus, Init Qik -4, 4 points), which kills "
    "one person or beast after the demon enters its dreams by "
    "Envisioning, usually to rid the true target of a calming friend.",
    "Devils of folklore are mostly faeries in a devil's part, or ghosts; "
    "as continental doctrine calls faeries fallen angels, more of them "
    "now play road-haunting imps, with another faerie nearby as priest "
    "or wise woman to let the traveller renew his faith, and they "
    "draw vitality from both parts. Folk charms work against demons "
    "with an Abhorrent Material or Circumstance, Compulsiveness or "
    "Protected Group weakness, and against faeries playing demons: a "
    "candle burning in the field all night keeps the cattle safe; a "
    "hagstone in the stable or over a cradle stops horses or a child "
    "being stolen and blocks Envisioning; a house shut tight bars a "
    "demon that must come by an open door or window; a branch of elder "
    "holds a demon all night counting its thorns and berries; and a "
    "pouch of salt makes a demon spend its maker's Intelligence + "
    "(Infernal or Divine) Lore in Might before it can begin to "
    "possess the wearer.",
    "Infernal places are of three kinds: battlefields soaked in "
    "slaughter, whose malevolent auras cover the whole plain where blood "
    "fell, hold demons as worms in the soil, and have patron demons "
    "that lure enemies back with dreams of victory (Magh Slécht, Druim "
    "Leatan, Dún Bhun na Gaillimhe); auras born of human corruption; and "
    "places where Hell itself touches the world (Inis Doney).",
)


def _ireland(hibernia: Hibernia) -> None:
    ireland = hibernia.places.get("ireland")
    if ireland is None:
        return
    _append(
        ireland,
        paragraphs(DIVINE_IRELAND, INFERNAL_IRELAND),
        "It is not recorded what turned Vigil's Merinita against the "
        "Diedne long ago; those who know how demons work may guess.",
    )
