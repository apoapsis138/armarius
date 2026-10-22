"""Churches, faiths and the military orders of the Levant in 1220
(ch04, ch05, ch07), in paraphrase.

The nine military orders are factions (L19): the Knights Templar, the
Knights Hospitaller and the Teutonic Knights, each with its great
castles as places (the book names none: Chastel Pèlerin and Tortosa,
Krak des Chevaliers and Marqab, and Montfort are history's, at an
assumed Divine 3), and the six lesser orders, of which the book gives
only names and St Lazarus's leper knights; the Templar-sorcerer reading
is in the Templars' secrets.

Church records: the legate Pelagius, with the Crusade's claims (L18);
the Latin Patriarch of Jerusalem (at Acre) and of Antioch, and the
Latin Archbishop of Nicosia; the Carmelites on Mount Carmel and St
Catherine's on Mount Sinai (places.py's places); one record for the head in the
Levant of each eastern church (Melkite, Jacobite, Coptic, Ethiopian,
Armenian, Georgian, Maronite, and the Church of the East, which the
Cradle pack does not make). The Head of John the Baptist is in
places.py's Umayyad Mosque (places["umayyad_mosque"]); the True Cross
(7 Faith Points, in Muslim hands since Hattin) is in the legate's and
the patriarch's summaries (L15). Mount Carmel is made here only if
places.py has not made it.

Factions with no tradition but the Karaites' (Q2): the Rabbinites, the
Karaites (trad_karaites), the Druze (with their scripture, L9), the
Nusayris and the Twelvers; the Fatimid Isma'ilis and the Qarmatians, the
other Shi'i branches, are in the Druze's and the Twelvers' summaries.

Each record sits in a region or town of places.py's, set again in
finish when places.py made it late; finish also links the orders to
their castles and to Acre.

Keys: world["templars"], ["hospitallers"], ["teutonic_knights"],
["order_trinity"], ["order_sword"], ["order_holy_spirit"],
["order_st_lawrence"], ["order_st_thomas"], ["order_st_lazarus"],
["pelagius"], ["patriarch_jerusalem"], ["patriarch_antioch"],
["archbishop_nicosia"], ["carmelites"], ["st_catherines"], ["melkites"],
["jacobites"], ["copts"], ["ethiopians"], ["armenian_church"],
["georgian_church"], ["maronites"], ["church_of_the_east"],
["rabbinites"], ["karaites"], ["druze"],
["nusayris"], ["twelvers"]; places["chastel_pelerin"], ["tortosa"],
["krak_des_chevaliers"], ["marqab"], ["montfort"], ["mount_carmel"]."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...places import PLACE
from ..builder import paragraphs

if TYPE_CHECKING:
    from ...models import Neighbour
    from . import Levant

ARCHBISHOP = "Archbishop's cathedral"
MONASTERY = "Monastery or nunnery"

#: Where each of this part's world records sits: (key, "places" or
#: "world", key of the region or town, which places.py makes).
SITES: tuple[tuple[str, str, str], ...] = (
    ("templars", "world", "acre"),
    ("hospitallers", "world", "acre"),
    ("teutonic_knights", "world", "acre"),
    ("order_trinity", "places", "jerusalem_kingdom"),
    ("order_sword", "places", "jerusalem_kingdom"),
    ("order_holy_spirit", "places", "jerusalem_kingdom"),
    ("order_st_lawrence", "places", "jerusalem_kingdom"),
    ("order_st_thomas", "world", "acre"),
    ("order_st_lazarus", "world", "acre"),
    ("pelagius", "world", "damietta"),
    ("patriarch_jerusalem", "world", "acre"),
    ("patriarch_antioch", "world", "antioch_city"),
    ("archbishop_nicosia", "world", "nicosia"),
    ("carmelites", "places", "mount_carmel"),
    ("st_catherines", "places", "sinai"),
    ("melkites", "places", "levant"),
    ("jacobites", "places", "syria"),
    ("copts", "world", "cairo"),
    ("ethiopians", "world", "jerusalem"),
    ("armenian_church", "places", "lesser_armenia"),
    ("georgian_church", "places", "georgia"),
    ("maronites", "places", "lebanon"),
    ("church_of_the_east", "world", "baghdad"),
    ("rabbinites", "places", "levant"),
    ("karaites", "places", "levant"),
    ("druze", "places", "lebanon"),
    ("nusayris", "places", "syria"),
    ("twelvers", "places", "levant"),
)

#: The castles of the three great orders: (key, name, region, order, summary).
CASTLES: tuple[tuple[str, str, str, str, str], ...] = (
    (
        "chastel_pelerin",
        "Chastel Pèlerin",
        "jerusalem_kingdom",
        "templars",
        "The Pilgrims' Castle at 'Atlit, on a headland south of Haifa, "
        "which the Templars began building in 1218 with crusaders' help "
        "and are still raising: a sea-girt fortress meant to replace "
        "the castles lost after Hattin. The book does not name it; it "
        "is history's.",
    ),
    (
        "tortosa",
        "Tortosa",
        "tripoli_county",
        "templars",
        "The Templars' coastal stronghold in the County of Tripoli, "
        "with its keep by the sea and its old cathedral of Our Lady. The "
        "book does not name it; it is history's.",
    ),
    (
        "krak_des_chevaliers",
        "Krak des Chevaliers",
        "tripoli_county",
        "hospitallers",
        "The Hospitallers' great castle on its ridge above the gap "
        "between Tripoli and Homs, held since 1142 and the strongest in "
        "the Latin East. The book does not name it; it is history's.",
    ),
    (
        "marqab",
        "Marqab",
        "antioch",
        "hospitallers",
        "The Hospitallers' black basalt castle above the coast road "
        "near Valania, theirs since 1186; the book has it the last of "
        "their great strongholds to fall, to Qalawun in May 1285.",
    ),
    (
        "montfort",
        "Montfort",
        "jerusalem_kingdom",
        "teutonic_knights",
        "A hill castle in Galilee, north-east of Acre, which the "
        "Teutonic Knights buy in 1220 to make their own seat. The book "
        "does not name it; it is history's.",
    ),
)


def build(levant: Levant) -> None:
    _military_orders(levant)
    _castles(levant)
    _latin_church(levant)
    _eastern_churches(levant)
    _faiths(levant)


def _where(levant: Levant, key: str) -> Neighbour | None:
    kind, found = next((k, w) for r, k, w in SITES if r == key)
    return (levant.places if kind == "places" else levant.world).get(found)


def _site(levant: Levant, key: str, name: str, **kw: Any) -> Neighbour:
    """The place `name` if another part made it already, else a new one."""
    found = next(
        (n for n in levant.b.saga.neighbours if n.name == name and n.kind == PLACE),
        None,
    )
    if found is None:
        found = levant.b.place(name, **kw)
    levant.places[key] = found
    return found


# -- the military orders --


ORDERS_SUMMARY = paragraphs(
    "The military orders. Brotherhoods of warrior-monks, sworn to "
    "poverty, chastity and obedience and to their order's Rule, who "
    "answer in matters of religion only to the Pope, which sets them at "
    "odds with the local clergy. Popes have heaped privileges on them, "
    "lords in Europe have given them land to pay for the war, and in "
    "the East the crown and nobles, short of men and money, have handed "
    "them castle after castle. Their wealth has paid for houses that "
    "recruit for them, their brethren are the core of every Latin army, "
    "their masters are men of state, and the Templars and Hospitallers "
    "now bank for the kings of Jerusalem. They are not the king's "
    "vassals and owe him only the loyalty of the Latin states' "
    "defenders, which does not always mean following his policy.",
    "In play: a knight brother takes the Definitive Edition's Brother "
    "Knight, a sergeant Brother Sergeant, a priest Brother Chaplain; "
    "Templars wear a red cross on white, Hospitallers a white cross on "
    "black, Teutonic Knights a black cross on white, and the lesser "
    "orders their own marks. The book's Turcopole, a light horseman of "
    "an order, is nearest Brother Sergeant.",
)


def _military_orders(levant: Levant) -> None:
    b, w = levant.b, levant.world
    w["templars"] = b.faction(
        "The Knights Templar",
        faction="Other",
        decides="Its leader",
        ruler="Grand Master Peter de Montaigu",
        place=_where(levant, "templars"),
        summary=paragraphs(
            "The Order of the Temple, the first of the military orders: a "
            "few knights who banded together about 1118 to guard the "
            "pilgrim roads to Jerusalem, were given part of the Temple "
            "enclosure by the king and the patriarch, and took their "
            "name from it. Their life as warrior-monks was set down about "
            "1128 and made a Rule in 1129, and their task soon grew from "
            "the roads to the defence of the whole Latin East. Since "
            "Jerusalem fell their headquarters has been Acre; they hold "
            "Tortosa and are building the Pilgrims' Castle at 'Atlit. "
            "Grand Master Peter de Montaigu leads them; his brother "
            "Guerin leads the Hospitallers.",
            ORDERS_SUMMARY,
            "If history runs on: the three great orders withdraw to "
            "Cyprus when the Latin states fall in 1291 and are blamed "
            "for the loss. Philip IV of France has the Templars of France "
            "arrested in October 1307 for heresy, obscene rites and idol "
            "worship; many confess under torture, the Pope takes over the "
            "inquiry, fifty-four are burnt at Paris in 1310, the order "
            "is suppressed in 1312 and much of its land goes to the "
            "Hospitallers, and in March 1314 Grand Master Jacques de "
            "Molay and Geoffroi de Charney are burnt.",
        ),
        secrets=paragraphs(
            "Whether the Templars were guilty is not known, and the book "
            "offers a troupe the darker reading: Templars who really are "
            "diabolists or sorcerers with real power. With their houses "
            "and wealth across Europe and the Levant they would be a "
            "rival to the Order itself, and if their power is Infernal, "
            "Hermetic magic cannot see through the deceptions that hide "
            "it, so only mundane digging will find them out.",
        ),
    )
    w["hospitallers"] = b.faction(
        "The Knights Hospitaller",
        faction="Other",
        decides="Its leader",
        ruler="Grand Master Guerin de Montaigu",
        place=_where(levant, "hospitallers"),
        summary=paragraphs(
            "The Knights of St John, brothers of the Hospital "
            "of St John of Jerusalem: a brotherhood founded in the tenth "
            "century to run a hospital for the sick of Jerusalem, which "
            "took up arms in the twelfth and by its middle was the "
            "second military order of the Latin East. Its headquarters "
            "was in Jerusalem, and is now at Acre; Krak des Chevaliers "
            "and Marqab are its great castles. Grand Master Guerin de "
            "Montaigu leads it.",
            "If history runs on: it outlives the Templars, takes Rhodes "
            "from the Byzantines in 1310 and crusades from the island "
            "into the sixteenth century.",
        ),
    )
    w["teutonic_knights"] = b.faction(
        "The Teutonic Knights",
        faction="Other",
        decides="Its leader",
        ruler="Grand Master Hermann von Salza",
        place=_where(levant, "teutonic_knights"),
        summary=paragraphs(
            "The Order of St Mary of the Teutons, the youngest of the "
            "three great orders. It traces itself to a German hospice in "
            "Jerusalem of the early 1100s, lost when the city fell in "
            "1187, and to a field hospital German crusaders made at Acre "
            "from their ships' sails and timbers in the Third Crusade, "
            "which Clement III approved in 1191 and Celestine III "
            "privileged in 1196; it became a military order the next "
            "year, and Innocent III confirmed it in 1199. It has grown "
            "fast, with houses across Europe and its heart in Germany, "
            "whence its interest in the Slav lands; it will never be a "
            "great force in the Levant. Grand Master Hermann von Salza "
            "leads it from Acre.",
            "If history runs on: it moves its headquarters to Marienburg "
            "in Prussia in 1309 and turns to eastern Europe.",
        ),
    )
    lesser = (
        ("order_trinity", "The Order of the Trinity", ""),
        ("order_sword", "The Order of the Sword", ""),
        ("order_holy_spirit", "The Order of the Holy Spirit", ""),
        ("order_st_lawrence", "The Order of St Lawrence", ""),
        (
            "order_st_thomas",
            "The Order of St Thomas of Acre",
            "Its house is at Acre. ",
        ),
    )
    for key, name, more in lesser:
        w[key] = b.faction(
            name,
            faction="Other",
            decides="Its leader",
            place=_where(levant, key),
            summary=f"{more}One of the lesser military orders of the Latin "
            "East, founded in the twelfth century or later. The book names "
            "it among them and says no more.",
        )
    w["order_st_lazarus"] = b.faction(
        "The Order of St Lazarus",
        faction="Other",
        decides="Its leader",
        place=_where(levant, "order_st_lazarus"),
        summary="The Order of Leper Knights: monks who kept a leper hospital "
        "in Jerusalem early in the twelfth century and had become a "
        "military order by its middle, now at Acre. It is said that its "
        "master and its knights must all be lepers themselves.",
    )


def _castles(levant: Levant) -> None:
    for key, name, region, _order, summary in CASTLES:
        _site(
            levant,
            key,
            name,
            inside=levant.places.get(region),
            realm="Divine",
            aura=3,
            summary=paragraphs(
                summary,
                "The book gives it no aura; a castle of an order of "
                "monks, with its chapel, is taken as Divine 3.",
            ),
        )


# -- the Latin Church --


def _latin_church(levant: Levant) -> None:
    b, w = levant.b, levant.world
    w["pelagius"] = b.church(
        "The Papal Legate",
        church="Bishop's cathedral",
        ruler="Cardinal Pelagius of Albano",
        place=_where(levant, "pelagius"),
        summary=paragraphs(
            "Pelagius, cardinal bishop of Albano, the Pope's legate with "
            "the Fifth Crusade, who leads it from Damietta. He holds that "
            "every land the Crusade wins in Egypt belongs to the Church, "
            "not to the Kingdom of Jerusalem, and he and John of Brienne "
            "quarrel over that and over who commands. He refused "
            "al-Kamil's offer of all the old Latin lands west of the "
            "Jordan, with the True Cross given back, for the Crusade's "
            "leaving Egypt.",
            "The True Cross. The fragment Arnulf of Chocques, the first "
            "Latin patriarch, found buried in the Holy Sepulchre's atrium "
            "in 1099 went into battle with the crusaders until Salah "
            "al-Din took it at Hattin in 1187; it has been in Muslim "
            "hands ever since, perhaps in the Ayyubid sultan's palace in "
            "Egypt. For a Christian it is a relic of 7 Faith Points; for "
            "anyone else it is wood.",
            "If history runs on: the quarrel stalls the Crusade in 1220; "
            "in 1221 the Nile flood traps the host outside al-Kamil's "
            "camp at al-Mansura, and Pelagius buys its way out of Egypt "
            "with an eight-year truce.",
        ),
    )
    w["patriarch_jerusalem"] = b.church(
        "The Latin Patriarch of Jerusalem",
        church=ARCHBISHOP,
        ruler="Ralph of Merencourt, Patriarch",
        place=_where(levant, "patriarch_jerusalem"),
        summary=paragraphs(
            "The head of the Latin Church in the Kingdom of Jerusalem, "
            "over its archbishops and bishops, who has sat at Acre since "
            "the Muslims retook the Holy City. The book names no patriarch; "
            "history has Ralph of Merencourt. With the Patriarch of "
            "Antioch he heads the Latin Church on the coast. Early on the "
            "clergy tried to master the kings and failed; now the crown "
            "mostly controls the clergy, the king choosing the patriarch "
            "and bishops of his realm. The Church may not hold fiefs, yet "
            "it has been given much property, and from that it owes the "
            "royal host its contingents.",
            "Most monks in the Levant, nearly all of them in houses "
            "founded since the crusaders came, are Benedictines; there "
            "are hermits besides, and pilgrims, Christian and Jewish, "
            "still go up to Jerusalem each year, as the Muslims allow. "
            "Before the Latins lost the city the patriarch lit the Holy "
            "Fire on Easter Eve; the senior priest present does it now. "
            "The True Cross, the kingdom's holiest relic, lost at "
            "Hattin, is in the legate's summary.",
        ),
    )
    w["patriarch_antioch"] = b.church(
        "The Latin Patriarch of Antioch",
        church=ARCHBISHOP,
        ruler="Rainier, Patriarch",
        place=_where(levant, "patriarch_antioch"),
        summary="The head of the Latin Church in the Principality of "
        "Antioch and the County of Tripoli, in the city where St Peter "
        "founded his first see. The book names no patriarch; history has "
        "Rainier, from 1219.",
    )
    w["archbishop_nicosia"] = b.church(
        "The Latin Archbishop of Nicosia",
        church=ARCHBISHOP,
        ruler="Eustorge of Montaigu, Archbishop",
        place=_where(levant, "archbishop_nicosia"),
        summary="The head of the Latin Church on Cyprus, an archbishop and "
        "not a patriarch, at the royal capital, where the Latins have "
        "raised the great cathedral of St Sophia in the city's heart. "
        "The king strictly keeps the Church from holding fiefs. The book "
        "names no archbishop; history has Eustorge of Montaigu, from "
        "1217.",
    )
    carmel = _site(
        levant,
        "mount_carmel",
        "Mount Carmel",
        inside=levant.places.get("jerusalem_kingdom"),
        realm="Divine",
        aura=3,
        summary="The ridge above Haifa where Elijah called down fire on "
        "the priests of Baal, its slopes home now to the hermits of the "
        "new Carmelite order. The book gives no aura; Divine 3 is "
        "assumed for a holy mountain of hermits.",
    )
    w["carmelites"] = b.church(
        "The Carmelites of Mount Carmel",
        church=MONASTERY,
        order="Carmelite",
        place=carmel,
        summary="A new order of hermits, few but notable, living on the "
        "slopes of Mount Carmel by a hard rule the Latin Patriarch wrote "
        "for them (history names him Albert, about 1209).",
    )
    sinai = levant.places.get("mount_sinai") or next(
        (n for n in b.saga.neighbours if n.name == "Mount Sinai" and n.kind == PLACE),
        None,
    )
    w["st_catherines"] = b.church(
        "St Catherine's Monastery",
        church=MONASTERY,
        order="Greek Orthodox",
        place=sinai or _where(levant, "st_catherines"),
        summary="At the foot of Mount Sinai, a house of Greek Orthodox "
        "monks founded by the Emperor Justinian in the sixth century; "
        "the monks trace it back to a little chapel the Empress Helena "
        "built in the fourth beside the burning bush from which God "
        "spoke to Moses. It is named for St Catherine, martyred at "
        "Alexandria, whose body Greek monks found close by some three "
        "centuries after her death.",
    )


# -- the eastern churches --


EASTERN: tuple[tuple[str, str, str], ...] = (
    (
        "melkites",
        "The Melkite Church",
        "The Greek Orthodox of the Levant, called Melkites, who kept "
        "communion with Constantinople when the Council of Chalcedon in "
        "451 defined Christ as one Person in two natures, human and "
        "divine. They stood first among Christians while the Byzantines "
        "ruled; the Latins have pushed their clergy aside and held them "
        "down hard, but they are still found everywhere in the Levant. "
        "The book names none of their patriarchs.",
    ),
    (
        "jacobites",
        "The Jacobite Church",
        "The Syrian Orthodox, named for their founder Jacob Baradaeus: "
        "Monophysites, who rejected Chalcedon and hold that Christ has a "
        "single nature, most often both human and divine. They live "
        "mostly in Syria and the Holy Land. The book names none of their "
        "patriarchs.",
    ),
    (
        "copts",
        "The Coptic Church",
        "The greatest church of Egypt, Monophysite like the Jacobites, "
        "and since rejecting Chalcedon ever more cut off from the rest "
        "of Christendom. Its patriarch of Alexandria sits at Cairo; "
        "history has the see empty from 1216 to 1235, which the book "
        "does not mention.",
    ),
    (
        "ethiopians",
        "The Ethiopian Church",
        "The church of the Christian kingdom of Ethiopia, founded in "
        "the fourth century and Monophysite, cut off from other "
        "Christians since the Muslims took Egypt. Some Ethiopians still "
        "come north on pilgrimage to Jerusalem and the holy places, and "
        "a few of its monks keep a house there; its head is in "
        "Ethiopia. Beyond Ethiopia, travellers say, lies the Ring of "
        "Fire, where the air burns and the sea boils, and past it a land "
        "of wonders under the good Christian king Prester John.",
    ),
    (
        "armenian_church",
        "The Armenian Church",
        "The national church of both Armenias, Christian since the "
        "fourth century, which rejected Chalcedon and went its own way. "
        "It is said to be Monophysite but has never joined the other "
        "Monophysite churches in full communion. In Lesser Armenia it is "
        "the rulers' faith; in Greater Armenia the rulers are Muslims. "
        "The book names neither its catholicos nor his seat.",
    ),
    (
        "georgian_church",
        "The Georgian Church",
        "The national church of Georgia, Christian since the fourth "
        "century: once under the patriarch of Antioch, it has governed "
        "itself since the eighth, and answers to neither Pope nor "
        "Emperor. The book names none of its heads.",
    ),
    (
        "maronites",
        "The Maronite Church",
        "The Syrian Christians of the Lebanon who would not accept the "
        "Council of Constantinople's ruling of 681 that Christ has two "
        "wills, divine and human, and kept apart until they united with "
        "the Latin Church in 1182. They take their name from Maro, a "
        "saint of the fifth century. Since the union they have nearly "
        "the Latins' standing in the Latin states, and a Maronite is "
        "made as a Latin character, though usually with Arabic as his "
        "first tongue and without the subject peoples' lower status. "
        "The book names none of their patriarchs.",
    ),
    (
        "church_of_the_east",
        "The Church of the East",
        "The Nestorians, strongest in Iraq and Persia: outside the "
        "Roman and Byzantine empires, they had no part in the great "
        "councils and are of two minds about Chalcedon, since they "
        "understand Christ's Person differently, stressing his true "
        "humanity and the reality of his moral choices. Its catholicos "
        "sits at Baghdad. The book names none of its heads.",
    ),
)

EASTERN_NOTE = (
    "The native Christians under Latin rule are subject peoples, ranked "
    "below every Latin (the Maronites alone excepted); under Muslim rule "
    "they are dhimmis."
)


def _eastern_churches(levant: Levant) -> None:
    b, w = levant.b, levant.world
    for key, name, summary in EASTERN:
        w[key] = b.church(
            name,
            church=ARCHBISHOP,
            place=_where(levant, key),
            summary=paragraphs(summary, EASTERN_NOTE),
        )


# -- other faiths --


def _faiths(levant: Levant) -> None:
    b, w = levant.b, levant.world
    w["rabbinites"] = b.faction(
        "The Rabbinites",
        faction="Other",
        place=_where(levant, "rabbinites"),
        summary="The Jews who follow the rabbis and the Talmud, the "
        "larger of the Levant's two Jewish communities, found in every "
        "town of note and a subject people under Latin and Muslim rulers "
        "alike. Kabbalah (Fourth Edition) says more of them; Jewish "
        "characters may use its guidelines.",
    )
    w["karaites"] = b.faction(
        "The Karaites",
        faction="Other",
        tradition="trad_karaites",
        place=_where(levant, "karaites"),
        summary="The Jews who hold to Scripture alone and reject the "
        "rabbis' oral law, the second of the Levant's two Jewish "
        "communities. Kabbalah (Fourth Edition) says more of them; their "
        "magi are Realms of Power: The Divine's Karaites.",
    )
    w["druze"] = b.faction(
        "The Druze",
        faction="Other",
        place=_where(levant, "druze"),
        rules="Their doctrine is kept secret from outsiders.",
        summary=paragraphs(
            "Isma'ili extremists who took the sixth Fatimid caliph, "
            "al-Hakim (996 to 1021), whom others thought mad, for a "
            "manifestation of God, led by Hamza ibn 'Ali. When al-Hakim "
            "vanished in 1021 Hamza said he had withdrawn to test the "
            "faithful; Hamza vanished soon after, and al-Muqtana led "
            "them. Their scripture, the Rasa'il al-Hikma, the Epistles of "
            "Wisdom, is Hamza's and al-Muqtana's letters, and they await "
            "the return of both. The Fatimids disowned them and hunted "
            "them in Cairo, but survivors fled to the Lebanon mountains, "
            "where they live still, so secretive that little more is "
            "known of their faith. Their name comes from al-Darazi, "
            "another of the sect's early men.",
            "The Fatimids were the other branch of the Isma'ilis: they "
            "held that each prophet's outward teaching hides one inner "
            "truth, a God past knowing from whom the world came by "
            "emanation; their rulers claimed to be both imams and "
            "caliphs but left the people Sunni. They ruled Egypt from 969 "
            "until Salah al-Din ended them in 1171. Some say a Fatimid "
            "escaped him.",
        ),
    )
    w["nusayris"] = b.faction(
        "The Nusayris",
        faction="Other",
        place=_where(levant, "nusayris"),
        summary="A splinter of the Twelvers, also called 'Alawis for "
        "their devotion to 'Ali, whose teaching the rest of the Twelvers "
        "rejected. They date from 859 and Muhammad ibn Nusayr al-Numayri, "
        "who called himself the bab, the gate, to the imam. They teach "
        "that a spirit stands just below the ineffable God, whose "
        "emanations reach down rank by rank into the world to lead "
        "fallen souls out of their bodies to heaven, and read the "
        "Qur'an as an initiation into devotion to 'Ali. They live in the "
        "Bahra' mountains of northern Syria.",
    )
    w["twelvers"] = b.faction(
        "The Twelvers",
        faction="Other",
        place=_where(levant, "twelvers"),
        summary=paragraphs(
            "The Ithna'ashari or Imami Shi'a, the largest Shi'i branch, "
            "many of the Bedouin among them. They follow twelve imams "
            "from 'Ali down through his house. The eleventh, al-Hasan "
            "al-'Askari, died in 874, and his son Muhammad al-Mahdi went "
            "into the lesser occultation, speaking through four envoys in "
            "turn, until the last of them said on his deathbed in 941 "
            "that the imam had entered the greater occultation, to last "
            "until he comes back as the mahdi at the end of time. Until "
            "then he is with his people but silent, and several duties, "
            "the lesser jihad among them, are suspended.",
            "Shi'i law. The Shi'is differ from the Sunnis mostly in "
            "putting the imams' teaching, handed down by their jurists, "
            "first: they allow temporary marriage and have their own "
            "rules of divorce and inheritance, and for most of them the "
            "lesser jihad waits on the rightful imam, now hidden. Five "
            "Shi'i branches matter in the Levant: the Twelvers, the "
            "Nusayris, the Fatimid Isma'ilis, the Druze and the Nizaris; "
            "the Qarmatians, the other early Isma'ili movement, were "
            "revolutionaries of Kufa.",
        ),
    )


# -- after every part has built --


def _place_in(record: Neighbour | None, place: Neighbour | None) -> None:
    if record is not None and place is not None and record.place_id is None:
        record.place_id = place.id


def finish(levant: Levant) -> None:
    b, w, p = levant.b, levant.world, levant.places
    for key, *_ in SITES:
        _place_in(w[key], _where(levant, key))
    sinai = p.get("mount_sinai") or next(
        (n for n in b.saga.neighbours if n.name == "Mount Sinai" and n.kind == PLACE),
        None,
    )
    st_catherines = w["st_catherines"]
    if sinai is not None and st_catherines.place_id != sinai.id:
        st_catherines.place_id = sinai.id
    for key, _name, region, order, _summary in CASTLES:
        castle = p[key]
        _place_in(castle, p.get(region))
        b.link(w[order], "places", castle, "Its castle")
    _place_in(p["mount_carmel"], p.get("jerusalem_kingdom"))
    crusade = w.get("fifth_crusade")
    if crusade is not None:
        b.link(w["pelagius"], "places", crusade, "Leads it as the Pope's legate")
    king = w.get("jerusalem_king")
    if king is not None:
        b.link(w["pelagius"], "places", king, "Quarrels with John of Brienne")
        b.link(
            w["patriarch_jerusalem"], "places", king, "The king chooses the patriarch"
        )
    nizaris = w.get("syrian_nizaris")
    if nizaris is not None:
        b.link(w["twelvers"], "places", nizaris, "Another Shi'i branch")
    b.link(w["twelvers"], "places", w["nusayris"], "Their splinter")
    b.link(w["twelvers"], "places", w["druze"], "Another Shi'i branch")
    bedouin = w.get("bedouin")
    if bedouin is not None:
        b.link(w["twelvers"], "places", bedouin, "Many are Twelvers")
