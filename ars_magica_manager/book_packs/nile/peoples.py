"""The lands and peoples of the Nile, in paraphrase: Lands of the Nile
Chapter I (pp. 6-11), Chapter II (pp. 12-16), Chapter III, the Ethiopian
Bestiary (pp. 17-23), and Chapter IX, the Mythic Aithiopians (pp. 122-126).

The tribes' intrinsic Virtues and Flaws and kombè's rolls are in
rules/africa.py, so the records cite their pages. The Dhimmi Flaw and the
Knows People Virtue are in the catalog. The Great Hunger and the Hope are
book_packs.hunger's.

A Virtue the catalog lacks is left out of a creature's block and named in
its notes: Gluttonous, printed with no rules. By the errata (pp. 86-87)
Overrun, Trunk, Roll Attack (the book's Death Roll), Constriction and Swallow
Whole are Qualities, so they stand in the blocks and not among the powers.
Thick Scales, Thick Fur, Thick Feathers and Thick Skin are the catalog's
Thick Fur/Thick Scales; Sex Shift is its Gender Shift. Where the book gives
only changes to another block, the record holds what those changes state, and
its combat
figures are left for the storyguide."""

from __future__ import annotations

from typing import Any

from ...models import BodyVis, Creature, Neighbour
from ..builder import (
    Builder,
    StatBlock,
    characteristics,
    dormant,
    joined_lines,
    paragraphs,
    vf_great,
    vf_minor,
    vf_puissant,
)

SOURCE = "LotN"
FATIGUE = "OK, 0, -1, -3, -5, Unconscious"
EXTRA_FIRST = "OK, 0/0, -1, -3, -5, Unconscious"
EXTRA_TWO = "OK, 0/0, -1/-1, -3, -5, Unconscious"
EXTRA_THREE = "OK, 0/0, -1/-1, -3/-3, -5, Unconscious"
THICK = "Thick Fur/Thick Scales"
HORNS = "Large Horns/Antlers"
SURPRISE = (
    "If it takes its victim unawares it automatically wins Initiative and has "
    "+3 to Attack Totals in the first round."
)

#: The shamed, and what each needs: story openings of p. 14.
ASHAMED = (
    (
        "The Polo Party",
        "A nobleman's polo party rode down people in the market, and he needs "
        "every one of the injured found so that he can make amends.",
    ),
    (
        "The Heiress's Father",
        "An heiress's father died on a trading venture. She must find his "
        "remains so that he can be decently buried and his goods shared out "
        "among his heirs.",
    ),
    (
        "The Sunken Cargo",
        "A merchant's ship has gone down and his creditors are hounding him. "
        "He wants the magi to bring the cargo up from the sea bed.",
    ),
    (
        "The Sicilian Sailor",
        "A rich adulterer has talked a Sicilian sailor into taking the blame. "
        "Once the sailor has boasted of his conquests he must be smuggled out "
        "of town.",
    ),
    (
        "The Learned Excuse",
        "A noble drunkard needs a doctor of good standing to declare that "
        "sunstroke, not wine, was to blame for what he did. Is there such an "
        "expert to be found?",
    ),
)


def _times(entry: Any, count: int) -> list[Any]:
    """A Virtue or Quality a block takes `count` times."""
    return [entry] * count


def build(b: Builder) -> None:
    valley, slavelands = _lands(b)
    _peoples(b)
    _customs(b)
    _tribes(b, slavelands)
    _beasts(b, valley)
    _monkeys(b, valley)
    _templates(b, valley)
    _marvels(b, valley, slavelands)
    _stories(b, slavelands)


# -- the land --


def _lands(b: Builder) -> tuple[Neighbour, Neighbour]:
    valley = b.place(
        "The Nile Valley",
        summary=paragraphs(
            "The great river parts Africa from Asia, and Egypt, Nubia and, "
            "less so, Ethiopia are really the lands along its two banks. Men "
            "hold it to be the Gihon, one of the four rivers of Paradise; "
            "where it rises nobody knows, and scholars argue over it while "
            "expeditions go looking in Ethiopia Orientalis. Only a narrow "
            "fertile strip can be lived on, drowned each year from June to "
            "September under a rich black silt that comes of the rains in the "
            "Abyssinian Highlands. Palm gardens and orchards line the water, "
            "with broad fields behind them, then the desert. In much of Egypt "
            "and Nubia the river is the only water, and many years bring no "
            "rain at all.",
            "Visitors marvel at its plenty: pastures, groves, forests thick "
            "with beasts, swamps and reed beds. Yet the place feels endless. "
            "One day is much like the last, the length of the day barely "
            "changes, crops grow all year, and only the flood marks the "
            "turning of the year, chiefly in Lower Egypt. Upper and lower "
            "follow the river's flow: Lower Egypt is the Delta in the north, "
            "Upper Egypt lies around Qus, Lower Nubia runs from the first "
            "cataract to the third, and Upper Nubia south to the Abyssinian "
            "Highlands.",
            "Treasure is the land's great belief. Muslim scholars know that "
            "Herodotus lists more pharaohs than Scripture allows, and yet the "
            "tombs he names are where he says. Sufis and Christian mystics "
            "muse on this; most people hold that God filled Egypt with "
            "monuments to make men wiser, and that taking from them never "
            "lessens them. Every traveller on the Hajj through Egypt does well "
            "to see them. Every spot on the Nile is thought to hide a treasure, "
            "so firmly that the government licenses a guild of treasure "
            "hunters and takes a share, and in droughts has lived for decades "
            "on the tax. Where no treasure lies, a faerie may well put one "
            "there and help you find it, or help you suffer for failing to.",
            "The West knows little of it. Traders come for gold, spices, "
            "ointments, stones and silks, keep fondachi in Alexandria, and "
            "ignore the Pope's bans on selling wood and iron to Egypt, but few "
            "pass Cairo. The Great King of Makuria forbids foreign trade, so "
            "Nubia and Ethiopia are almost unknown in Europe. Egypt is thought "
            "a storehouse of old lore, and some in the Order wonder whether "
            "the secrets of the first magicians lie in its tombs.",
            "By the reckoning of the learned, the Earth was made 5278 years "
            "ago, in 4058 BC by Maimonides, and the Flood came 1656 years "
            "later, in 2402 BC. Misr son of Ham son of Noah was Egypt's first "
            "king, and his sons founded cities that still bear their names. "
            "Joseph was sold there in 1842 BC, and is said locally to have "
            "been a great magician, perhaps Imhotep himself. The Exodus "
            "followed in 1610 BC, and some say monument building slackened "
            "without the Jewish slaves. Pharaohs ruled for at most 2070 years, "
            "until Alexander took Egypt in 332 BC; the Ptolemies held it for "
            "302 years, to 30 BC, and the Muslims finished their conquest in "
            "641. Heliopolis, now a suburb of Cairo, is where Herodotus set "
            "the phoenix's death and rebirth.",
        ),
        secrets=paragraphs(
            "Themes for sagas (pp. 6-9), none excluding another. The Red and "
            "the Black: Africa is the battleground of the Great Hunger and "
            "the Hope, and these lands lie in the Black's stronghold. The Kom, "
            "a giant who was the Red's chief servant, was slain and seeks to "
            "remake itself (at Pakhoras). The Cult of Dedun serves the Red "
            "indirectly by gathering power from death and decay, seeking "
            "immortality through decrepitude. Wesir, the first human to learn "
            "how to become a Daimon, is now a mighty servant of the Black. The "
            "old rites of death cleansed favoured ghosts of the Red and raised "
            "them as Daimons, allies of the Black. Egypt just grows marvels: "
            "the superabundance of tombs is another face of the Black's "
            "fertility. Secrets and mysteries: the Red devours secrets, so some "
            "mysteries no longer have answers, and others never had any, being "
            "plain marvels of God; players must expect that. Endlessness: see "
            "above. The Black's servants include the lector priests who were "
            "the pharaohs' magicians.",
            "Why the Order might come here (pp. 127-128). The book puts no magi "
            "in these lands in 1220. A saga may loot the past with no neighbours "
            "and add other covenants later; a crusading or tired covenant may "
            "come to escape the Code or a Peripheral Code, until its actions "
            "bring magi from the Roman or Levant Tribunals; a covenant may join "
            "an existing Tribunal, if Redcaps or that Tribunal's members can "
            "reach it in good time and its Peripheral Code allows, or contest a "
            "border at Grand Tribunal, where no precedent yet exists, for vis or "
            "votes (Houses of Hermes: True Lineages p. 49; ArM5 p. 14). A Nile "
            "Tribunal needs at least twelve magi of four covenants and a "
            "Quaesitor, and a sponsor at the Grand Tribunal of 1228 or 1261. It "
            "must outlast the Fifth Crusade and, if history holds, the Seventh "
            "(1248 to 1254), against eremites, Moorish sahirs, treasure hunters "
            "and magi who want no new delegation.",
            "Every monument of medieval Africa stands in Mythic Africa, with "
            "many more. The book follows thirteenth-century folklore, not "
            "modern archaeology. Tombs hold bizarre traps, strange creatures "
            "and puzzles, because people then believed they did: it explained "
            "why the treasure was still there. Old Egyptian magic is far weaker "
            "in attack than Hermetic magic; its priest-magicians excelled at "
            "healing and at commanding spirits.",
            "Beasts of the valley with statistics elsewhere: the lion, in The "
            "Book of Mundane Beasts; a magical lion and the pard in Realms of "
            "Power: Magic pp. 60-61; other animals in Between Sand and Sea.",
        ),
    )
    b.place(
        "The Abyssinian Highlands",
        summary=(
            "The high country between Nubia and Ethiopia, also called the Land "
            "of Havilah. It takes in the Semien Mountains on the Ethiopian "
            "Empire's eastern border and Lake Tana with its many islands. "
            "Almost nothing else on the river's course rises so high, and its "
            "rains make the Nile's flood."
        ),
    )
    deserts = b.place(
        "The Deserts of the Nile",
        summary=(
            "Three deserts hem in these lands, most of them ergs, rolling "
            "dunes swept by the wind. Travellers fear sun and thirst, sands "
            "that swallow a man and his mount, brigands on the caravan roads, "
            "storms that choke them or flay them, and the jinn and demons "
            "that show them palm-shaded pools. The first long drink may prove "
            "to be a mouthful of sand."
        ),
        secrets=paragraphs(
            "Hazards (p. 10). Deprivation checks for lack of water come every "
            "4 hours here, and sun on bare skin does +1 non-combat damage "
            "(ArM5 pp. 180-181).",
            "Dry quicksand: the victim is under within two rounds, then "
            "suffocates unless rescued. In the first round a Strength or "
            "Quickness stress roll against 9 frees him; a botch traps his arms "
            "for the next round. After that his companions must save him, and "
            "if his arms are free he may help in the second round, taking 3 "
            "off any further Ease Factors he faces. Then he has gone under.",
            "Brigands usually leave a well-guarded caravan alone, unless "
            "desperate. Sandstorms and dust storms may be natural, made by "
            "sorcerers, elemental jinn, or even witches in disguise.",
        ),
    )
    b.place(
        "The Libyan Desert",
        summary="The vast desert on the western border of Egypt and Nubia.",
        inside=deserts,
    )
    b.place(
        "The Nubian Desert",
        summary=(
            "The desert between the Upper Nile and the Red Sea, home of the "
            "headless Blemmyae, whose five tribes alone know where the gold "
            "lies that once made Egypt rich."
        ),
        inside=deserts,
    )
    b.place(
        "The Danakil Desert",
        summary="The desert between the Nubian Kingdom of Atbara and Ethiopia.",
        inside=deserts,
    )
    slavelands = b.place(
        "The Slavelands",
        summary=paragraphs(
            "Nubians speak of the Slavelands as one country, but no such "
            "country exists. The captives sold to Egypt are taken from many "
            "separate places: some east of the Nile, some from the wilds "
            "between the Alodian city states, most from west and south-west "
            "of Upper Nubia. The name lets the Nubians think of free people "
            "as born slaves, and forget that they were once such a tribe "
            "themselves.",
            "Fetid swamps and dry grasslands feed the tribes who live here, "
            "and Egyptian and Nubian expeditions raid them for slaves and "
            "cattle. Most slaves sold in Qus and Cairo come from them.",
        ),
    )
    b.place(
        "The Land of Venom",
        summary=(
            "A great rich pasture south of Ethiopia with nobody in it, because "
            "of the scorpions and spiders whose bite kills swiftly. The "
            "Cynamolgi graze their herds beyond it."
        ),
        inside=slavelands,
    )
    return valley, slavelands


# -- the peoples --


def _peoples(b: Builder) -> None:
    b.faction(
        "The Copts",
        summary=paragraphs(
            "The first people of Egypt, descended from the pyramid builders: "
            "dark of hair and eye, olive of skin, like Jews and Syrians, "
            "though they admire paler skin and some whiten theirs with "
            "pigments and bleaches. Red hair means bad luck. The most learned "
            "are said to read the old writing freely, for hieroglyphs are "
            "only another way of writing their tongue's ancestor; some become "
            "healers, oracles and magicians by it, and others use it to serve "
            "the Divine.",
            "Copts are more curious about foreigners than Muslims are, and "
            "trade with them more: to know a stranger's needs is to know whom "
            "to send him to, and they approach his servants, since great men "
            "keep servants for such things. They forgive rudeness readily, "
            "being trained to it by Muslims who may berate them and in places "
            "spit on them, though an intermediary will still come to explain "
            "the fault so that the shame can be put right. Priests sway them "
            "more than clerics sway Muslims: faith marks them as a people and "
            "guards their standing as dhimmis, and a Christian priesthood is "
            "bound to its place as a Muslim teacher is not. Family counts for "
            "still more than among Muslims, and awkward matters stay within "
            "the community.",
            "They keep festivals at the tombs of local saints, where the "
            "world works otherwise. At the moolid of Sitt Dimiana no thief can "
            "steal, and any man who looks on a woman meaning her harm is "
            "wounded in the eyes or lower down. At the Festival of Saint "
            "George nobody can stay possessed. Muslims and Christians go to "
            "each other's festivals, and when the flood looks poor the Sultan "
            "orders joint processions.",
        ),
        rules=(
            "All the notes on Egyptian characters suit Copts, save those "
            "marked as Muslim (p. 16). Festival miracles never fail, not even "
            "for a clever sorcerer, though people have been tricked into "
            "possession just after the festival ends. Western theologians "
            "find such certainty troubling; Copts do not."
        ),
    )
    b.faction(
        "The Muslims of Egypt",
        summary=paragraphs(
            "Egypt fell to the Umayyad Caliphate in 639, and its people turned "
            "to Islam slowly over the centuries. They are now a blend of "
            "Copts who converted and Arabs who settled from the east, and "
            "their faith is less strict than that nearer Mecca or among the "
            "west African dynasties. Of all Muslim lands, religion weighs "
            "least here on those who do not share it.",
            "A good Muslim professes that there is no God but God and that "
            "Mohammed is His Prophet, before other Muslims, and follows the "
            "Qur'an and the sayings and deeds of the Prophet as jurists read "
            "them. He prays five times a day facing Mecca, between dawn and "
            "sunrise, after noon, in the afternoon, after sunset and after "
            "dusk, washing first; a mosque gives him water and a niche to "
            "face, and Friday noon is the great gathering. He gives alms, some "
            "rulers taxing for them. Egyptians hold that wealth does not "
            "reward virtue: Fate rules, and is not earned. He fasts, Ramadan "
            "above all, without even water, unless a child, old, pregnant, "
            "ill or travelling, and the evenings bring feasts hosted in turn. "
            "Pork and alcohol are shunned with more or less rigour. He goes "
            "to Mecca, and if he can Medina, once in his life, and comes back "
            "a Haji (a woman a Hajja), often in a green head covering; the "
            "poor visit nearer shrines, of which Cairo has many.",
        ),
        rules=(
            "The book's Islam is a simple guide for telling folktale stories, "
            "in which the rich and urban observe less strictly than the poor "
            "and rural (p. 12). For the Haj and shame, see Egyptian Manners."
        ),
    )
    b.faction(
        "The Dhimmis",
        summary=paragraphs(
            "Egypt surrendered to the Muslims rather than falling by force, "
            "and to a pious Muslim that bargain binds before God, so those "
            "non-Muslims allowed to stay fare better here than elsewhere, "
            "while they are useful. Most are Copts. Many Jews came from the "
            "Maghrib, among them the leader of a large community at Kairoun "
            "who fled a strict new dynasty. Some are freed slaves from the "
            "African interior, who should convert and often keep old ways "
            "besides. Few Zoroastrians live here.",
            "They pay a yearly tax, though those in Alexandria by old "
            "agreement give only a little to the poor. They may not hold "
            "office, yet a Muslim may hire one to do the work of his; a Muslim "
            "port inspector, say, often pays a Christian to do the inspecting. "
            "They may not hold army rank, save mercenary captains; may not "
            "proselytize, nor touch or marry Muslim women; carry no weapons, "
            "though a knife is a tool and a shopkeeper keeps something handy. "
            "They must not plot with the ruler's enemies, nor testify against "
            "Muslims, though a Muslim friend may speak for them. Religious "
            "symbols are banned, though clerical garb is not and some places "
            "make them wear a mark. Prayer, bells and lavish funerals may not "
            "disturb, except in places such as Coptic Old Cairo. New places of "
            "worship need leave, and the authorities let new churches count "
            "as revivals of old ones, even of villages lost to the sand. Pork "
            "and wine stay out of sight. They should not ride horses or "
            "camels; in the towns they ride and dismount to pass mosques and "
            "great houses, and a Muslim knows he has arrived when dhimmis "
            "begin dismounting at his door. They bear contempt quietly.",
            "Outside polite society, they may do what well-born Muslims may "
            "not. Trade abroad seems a little unsavoury, so Christian and "
            "Jewish merchants gather in the coastal cities, above all "
            "Alexandria, where taxes are lighter than for Muslims in Cairo, "
            "and sell to Europe, Sicily most of all. They lend at interest, "
            "and a dhimmi in the middle soaks up the sin when one Muslim lends "
            "to another. All Christians know a priest and all priests need "
            "wine, so many Muslims have a Christian supplier; most wine is "
            "imported, and nearly all the rest comes from monasteries.",
        ),
        rules=(
            "The Dhimmi Flaw, a Minor General Flaw, gives these duties (p. 13); "
            "custom softens many of them in Egypt. A character from Europe "
            "might take Outsider instead. City and Guild serves merchant "
            "characters."
        ),
    )
    b.faction(
        "The Sabeans",
        summary=(
            "They claim to be Sabeans, and so People of the Book, with "
            "communities across Egypt and a fire religion much like the "
            "Zoroastrians'. They stand out in Cairo, for they venerate the "
            "Keeper of the Dead at Giza (p. 13)."
        ),
    )
    b.faction(
        "The Nubians",
        summary=(
            "A black-skinned Christian people, descended from the Nobatae, a "
            "tribe who came into the Nile Valley about the fall of Kush, and "
            "much in debt to Greek culture. A unique treaty with Muslim Egypt, "
            "the baqt, keeps them safe from invasion for a yearly payment of "
            "slaves."
        ),
    )
    b.faction(
        "The Ethiopians",
        summary=(
            "Kin to the Nubians in looks, quite different in culture, and in "
            "their land since the dawn of time: the forebears of the Empire "
            "traded with the Greek cities, with Pharaonic Egypt and with Kush. "
            "South of the Empire lie sultanates of colonists from Yemen."
        ),
    )
    b.faction(
        "The Churches of the Nile",
        summary=paragraphs(
            "The Coptic Orthodox Church of Alexandria was founded by Saint "
            "Mark. It gave Christendom monasticism, and from its catechetical "
            "school came Origen, called the father of theology. It holds that "
            "after the Incarnation Christ has one nature, divine or a blend "
            "of divine and human, against the two natures upheld by Rome and "
            "Constantinople. When the Council of Chalcedon adopted that "
            "teaching in 451, Rome, Constantinople and Antioch agreed and "
            "Alexandria refused, so the Copts chose their own patriarch "
            "against the Melkite or Imperial one and were persecuted by the "
            "Byzantine governors. The Muslim conquest drove the Melkites out "
            "with the Greeks, and the Copts revived; six centuries of "
            "conversion have thinned them, but they remain a real presence.",
            "The Nubian Church shares communion with the Copts and takes its "
            "bishops from Alexandria. Makuria was first converted by Melkites, "
            "and a good minority there still keep the Greek rite under "
            "Constantinople. The Ethiopian Church believes as the Copts do, "
            "but stands outside their congregation.",
        ),
        realm="Divine",
    )
    b.faction(
        "The Tongues of the Nile",
        summary=paragraphs(
            "Egypt speaks Arabic in its Masri dialect; travellers from North "
            "Africa use Maghrebi and those of Arabia Khaliji, all in the one "
            "script. Coptic, written in Greek letters with a few added from "
            "Demotic, has been failing since the conquest, though a century "
            "ago the country people still spoke it. Boharic survives in Lower "
            "Egypt; Sahidic has died out save among clergy in Nubia. Siwa "
            "speaks Siwi, a dialect of the Berbers' Tamazight.",
            "The three Nubian kingdoms speak Nubian, written in an extended "
            "Coptic alphabet: Mahasi in Nobatia, Dongolawi in Makuria, Alwa in "
            "Alodia, Kenzi among the Banu al Kanz. Mahasi is close to becoming "
            "its own tongue. Masri is widely known in Nobatia, which trades "
            "with Egypt. The native clergy write and sing in Nubian Greek, "
            "which true Greeks think barbarous.",
            "The Ethiopian highlands speak Amharic, from Ge'ez: Agaw in Agaw "
            "and Shewa, Amhara in Bet Amhara, Tigray along the escarpment of "
            "Medri Bahri. The lowlanders of Medri Bahri speak Tigrinya, with "
            "its own dialect in the Dahlak Archipelago. Oromigna, from Nubian, "
            "is heard in the southern sultanates and among the pagan tribes "
            "toward the Torrid Zone. All three use the Ge'ez script. Medri "
            "Bahri's merchants use Khaliji for the Red Sea, Yemen and the "
            "sultanates of Adal, Ifat, Hadiya and Dewaro.",
            "The Blemmyae speak Beja, last child of Meroitic, and cannot write "
            "it, so Kushite monuments are closed to them. Each tribe of the "
            "Slavelands has its own tongue, but any one will make itself "
            "understood in the others. Slaves are taught Arabic by their "
            "Nubian masters to raise their price, and discouraged from their "
            "own speech.",
            "Dead tongues: Ancient Egyptian, written in hieroglyphs and later "
            "hieratic, which became Demotic, in use until Roman times, still "
            "known to scholars, and the parent of Coptic. Meroitic, the speech "
            "of Kush, unrelated to Egyptian or Nubian, with a hieroglyphic and "
            "an alphabetic script that hardly anyone now reads. Ge'ez, the old "
            "tongue of Axum, still the liturgy of the Ethiopian Church, written "
            "in two hundred syllabic characters.",
        ),
        rules=joined_lines(
            "Living languages and their dialects (pp. 10-11): Amharic (Agaw, "
            "Amhara, Tigray); Arabic (Masri, Khaliji, Maghrebi); Beja; Coptic "
            "(Boharic, Sahidic); Nubian (Alwa, Dongolawi, Kenzi, Mahasi); "
            "Oromigna; Romaic Greek (Nubian); Tamazight (Siwi); Tigrinya "
            "(Dahlak); the tribal tongues of the Mythic Aithiopians. A dialect "
            "is a specialty; the Educated or well travelled may have shed "
            "theirs for a standard one (ArM5 p. 66).",
            "Penalty to both speakers: same language, different dialects -1; "
            "Mahasi and any other Nubian dialect -2; Oromigna and any Nubian "
            "dialect -2; Amharic and Ge'ez -2; Beja and Meroitic -2; Ancient "
            "Egyptian and Demotic -2; Demotic and Coptic -2; any two Aithiopean "
            "languages -2.",
            "Seekers learn key hieroglyphs of warning and curse by rote: the "
            "gist of a text is an Intelligence + Profession: Seeker stress roll "
            "against 6 for common curses or 9 for typical texts. A botch is a "
            "tragic misreading.",
        ),
    )


def _customs(b: Builder) -> None:
    b.faction(
        "Egyptian Manners",
        summary=paragraphs(
            "Egyptians speak more formally than Europeans, even among friends "
            "and kin, though in the street they are surprisingly rude. Unsure "
            "of someone's standing, one says sidi to a man and lella to a "
            "woman, which grants higher rank, wealth, age or wisdom. It is "
            "dangerous to say it to a faerie or demon, for it gives them "
            "command. Any reasonable request must be met, and failure "
            "disgraces both sides, so requests go as opinions, suggestions, or "
            "gossip through a go-between. Asking for information counts, and "
            "a man who cannot answer loses face, as does the one who asked. "
            "Plans carry the words 'if God wills it', accepting fate; "
            "some say curses fall more easily on boasters.",
            "To be known as disreputable shames a whole family, which can "
            "repudiate its member as a last resort. People expect mistakes, "
            "and public atonement. The learned and rich command others and "
            "keep to their class: they do no labour, for to hire nobody is to "
            "fail the community. Men's dress is loose trousers, which alone "
            "mark a poor man, with a long robe, head covering, tough slippers "
            "and a jacket. Women before men outside the family cover hair, "
            "body and arms, in many styles. The rich wear brighter, finer "
            "cloth and larger ornaments, while all pilgrims wear plain white.",
            "Life is lived in company. To bathe or cook alone is to miss the "
            "news, and circumcisions, marriages and funerals are feasts held "
            "at home. A magus locked in his sanctum for months is thought "
            "shameful, mad, or seeking holiness. The Gift brings no shame of "
            "itself, but distrust soon brings bad Reputations that do.",
            "Women's quarters are haram, forbidden to outsiders: wives, "
            "relatives, children, concubines and servants live there, with "
            "rivalries the folktales love. Women meet at the baths, at chores "
            "and on rooftops, and not to gossip is odd and rude, which gives "
            "them much news. A man may have four wives if he can keep them "
            "and treat them equally, and as many concubines as he can pay for, "
            "though this is not pious. A slave who bears a Muslim's child goes "
            "free and must be kept, so marriage usually follows.",
        ),
        rules=paragraphs(
            "Boasting (p. 14): a character who omits 'if God wills it' gives "
            "anyone envying him +6 on Hex rolls to spoil what he spoke of; "
            "saying the phrase cancels the bonus.",
            "Shame (p. 15): a negative Local Reputation is bought down in the "
            "usual way, by building a rival Reputation (ArM5 p. 167), and here "
            "this is expected and right, not cynical. The Haj is a series of "
            "scenes giving Reputation experience against negative Reputations "
            "and a Haji +1 Reputation, with other benefits by what befalls. "
            "Shorter pilgrimages give less, which is why some are said to equal "
            "a fraction of Mecca. Religious insight from the Haj uses The "
            "Church pp. 15 ff., and is a separate process from the social one.",
            "Women in disguise (p. 15, as the errata corrects it): a woman "
            "passing as a man has Dark Secret if discovery would ruin her, "
            "Gender Nonconforming if discovery recurs but only inconveniences, "
            "or no Flaw if it is not to make stories. A woman travelling with "
            "a false husband has Dark Secret if exposure would endanger the "
            "troupe, otherwise no Flaw.",
            "Knows People (p. 13) is in the catalog.",
        ),
    )
    b.faction(
        "Words of the Nile",
        summary=joined_lines(
            "Akh: a new soul made when ba, ka and khu fuse; the akhu are "
            "Daimons of the Magic Realm.",
            "Ba: a dead person's travelling soul, ever seeking the khu.",
            "Baqt: the pact that protects Christian Nubia from Muslim Egypt.",
            "Cataract: a broad waterfall of the Nile, impassable by boat, some "
            "passed by carrying boats overland.",
            "Domestikos: one of the thirteen kings who owe fealty to the "
            "megabasilikos.",
            "Field of Reeds: a paradise in the Magic Realm where the ka live.",
            "Ka: a dead person's ghost, going between the mundane world and "
            "the Field of Reeds.",
            "Kentake: mother of a Kushite qore, sharing his power.",
            "Khu: the Divine soul, which flees the body at death.",
            "Megabasilikos: Great King, overall ruler of Makuria and Nobatia.",
            "Mut: a ghost with unfinished business, like a shade.",
            "Qore: a Kushite king; Alodia still uses the word.",
            "Sahir: a magician working by summoning jinn, of the Order of "
            "Suleiman (The Cradle and the Crescent).",
            "Serdab: the part of a tomb the ghost lives in while in the mundane world.",
            "Ushabti: a statue of a person or animal to serve the dead in the "
            "afterlife; Egyptian ghosts can possess them.",
            "Wadi: a seasonal stream or river.",
        ),
    )


# -- the Mythic Aithiopians --


def _tribes(b: Builder, slavelands: Neighbour) -> None:
    b.faction(
        "The Mythic Aithiopes",
        summary=paragraphs(
            "The Aithiopes, 'burnt faces', are not the Ethiopians, though kin "
            "to them and to the Nubians, whose black skin and hair they share. "
            "Their many tribes live south-east of Nubia and east of Ethiopia, "
            "each with its own tongue, and were first written of in travelogs "
            "like that of Diodorus Siculus. The names the Greeks gave them are "
            "still used by the Nubians.",
            "No missionary of any Divine faith has reached them, and most men "
            "would call them pagan, yet they believe in one Creator whose "
            "perfect world was spoiled by the first man and woman. They have "
            "no church or holy men, and appease or avoid the nature spirits "
            "cast out of Eden with that first couple.",
        ),
        rules=(
            "As characters (p. 122): Outsider applies automatically in Nubia, "
            "and in Arab lands they are likely taken for runaway slaves. Each "
            "tribe's intrinsic Virtue and Flaw come on top of the normal "
            "allotment. Or play one as a Magic Human (Realms of Power: Magic p. "
            "32), the pair becoming a Minor Virtue Quality and a Minor Flaw "
            "Inferiority, perhaps with Inferiorities to cancel the immunity to "
            "aging and deprivation. The storyguide may treat their religion as "
            "Divine. These tribes are mythic, not the real peoples of East "
            "Africa."
        ),
        place=slavelands,
    )
    tribes = (
        (
            "The Icthyophagi",
            paragraphs(
                "The fish eaters of the Red Sea coast live deep in the ravines, "
                "under arches of giant sea creatures' ribs woven with seaweed. "
                "When strong tides flood the shore the women and children throw "
                "small fish onto land, while the men band together against the "
                "large ones with goat horns and jagged rocks. The catch is "
                "pounded into bricks on cliff tops where the sun heats the "
                "rock red hot.",
                "They drink only every fifth day, trekking inland to the "
                "Blemmyae's waterholes to bloat themselves and lie gasping. They "
                "raise children in common with no families, and are famous for "
                "enduring pain. Their dried fish is foul, but light, nourishing "
                "and never spoils.",
            ),
            "p. 123: Enduring Constitution; Weakness (drinking water). High "
            "Survival and Swim. A month of fish bricks is one Load.",
        ),
        (
            "The Chelonophagi",
            "Icthyophagi of the low Red Sea islands, which have no soil or "
            "fresh water, the outer ones breaking the waves so that the inner "
            "lie calm. The turtle eaters swim out to giant turtles sleeping at "
            "the surface, some as big as boats, flip them, tow them ashore and "
            "bake them in the sun. The upper shells become skiffs for trips to "
            "the mainland for water.",
            "",
        ),
        (
            "The Rhizophagi",
            paragraphs(
                "The root eaters live in the marshes of the White Nile, digging "
                "out reed roots, pulping them and drying the balls in the sun. "
                "They live at peace with each other but are at war with the "
                "lions who come from the desert for the cool. They make no "
                "weapons. At the rising of Sirius, though, swarms of mosquitoes "
                "and flies descend, the people ward them off with marsh plants, "
                "and the lions flee, stung and terrified by the hum.",
                "Taught at their mothers' knees, they are fine apothecaries and "
                "herb doctors, said never to sicken and to live very long. They "
                "make kombè for the Cynegi, in exchange for skins, and its "
                "antidote. At Egyptian markets a Rhizophagus is a prize, docile "
                "and skilled. The buyer should beware: he is also an expert "
                "poisoner.",
            ),
            "p. 123: Herbalism (Art & Academe p. 55); Noncombatant. Good "
            "Profession: Apothecary and Chirurgy; some have Mythic Herbalism.",
        ),
        (
            "The Hylophagi",
            paragraphs(
                "Small, nimble, tailed and pale-furred, they live near the "
                "Rhizophagi, eating fruit in its season and otherwise chewing "
                "the tips of branches high in the trees. They leap from tree to "
                "tree like birds and never seem hurt in falling. They fight for "
                "certain trees with clubs and tear their victims apart. They "
                "dress in leaves or bark tied with vines; they make no tools, "
                "and simple made things baffle them.",
                "Some live in vast hollow trees that hold a whole village, the "
                "leaves giving water and the fruit luring game. They are thought "
                "not worth importing, but some Nubian kings keep one as a "
                "gardener, tending the plants with teeth and nails. At home they "
                "sometimes live among the mouthless Astomi or the ear-winged "
                "Panotii.",
            ),
            "p. 124: intelligent monkeys, not humans: the Baboon block with "
            "Perfect Balance and Primitive Equipment. A village tree has about "
            "the inside of a Mystic Tower and could found an unusual covenant, "
            "from a seed grown by magic or a grown tree moved with Free the "
            "Striding Tree (ArM5 p. 139); Hylophagi make expert covenfolk for "
            "it.",
        ),
        (
            "The Cynegi",
            paragraphs(
                "The Hunters of the inland country, unfit for farming, sleep in "
                "trees to escape the beasts and go by day to waterholes to kill. "
                "They use fire-hardened clubs, bows and bone-bladed spears, and "
                "wear a little leather, which is also their money: the more "
                "dangerous the beast, the more its hide is worth.",
                "The Elephant Hunters are a western band. One grips the beast's "
                "tail, plants his feet on its thighs and hacks at the hind legs "
                "with an axe; when it falls the others rush in to cut meat, "
                "often before it is dead.",
            ),
            "p. 124: Puissant Hunt; Reckless. Profession: Prepare Kombè and the "
            "venom's rolls are on that page.",
        ),
        (
            "The Struthophagi",
            "The bird eaters live south and west of the Cynegi, small and "
            "tireless. Their homes overflow with fine baskets, furniture made "
            "with no saw or joint, painted pottery and great gardens, and they "
            "resent sleep for wasting time. They keep ostriches for meat, "
            "leather and riding, and the feathers are among Nubia's chief "
            "exports to Egypt. Legend says the ostrich was first given fire and "
            "hid it under its wing. The first Struthophagus persuaded it that "
            "it could fly, took the fire when its wings opened, and repenting "
            "vowed to look after it. A peaceful folk, they suffer badly from "
            "slavers.",
            "p. 124: Puissant Ride; Small Frame. Prized as light cavalry, their "
            "ostriches hurling stones while they throw spears.",
        ),
        (
            "The Acridophagi",
            paragraphs(
                "The locust eaters live on the desert's edge near the "
                "Struthophagi, leaner and darker than other men. In spring the "
                "desert breeds swarms of locusts. The tribe drive them into "
                "ravines with fire, kill them with smoke, and salt them to last "
                "the year, growing no crops and keeping no stock.",
                "They die young, and forty is a great age. Winged lice breed in "
                "their flesh as they age: first itching, then a thin acrid "
                "discharge, then the vermin bore out and pour away, each taking "
                "a morsel until nothing is left. Other peoples' flesh does not "
                "tempt them.",
            ),
            "p. 125: Greater Immunity to Thirst; Greater Malediction, which "
            "starts Aging rolls at 15. Nothing, even magic, cures or keeps out "
            "the lice.",
        ),
        (
            "The Cynamolgi",
            paragraphs(
                "Tall bearded herdsmen beyond the Land of Venom, whose savage "
                "dog packs keep lions, leopards and hyenas off their cattle. "
                "Everyone covets the cattle, and Nubian slavers come for them, "
                "but seldom take the men, who are too much trouble.",
                "A boy is suckled by a bitch and his milk-mates begin his pack. "
                "Only the man who raised the dogs can go near them. When he "
                "dies they must be killed and buried with him, or they turn wild "
                "and become the very predators they guarded against. They are "
                "solemn, slow to weigh a matter, decisive once it is weighed, "
                "and fierce in war.",
            ),
            "p. 125: Puissant Animal Handling; Compulsion (protect his pack). "
            "He leads his dogs as a trained group with Animal Handling for "
            "Leadership, and rarely has an Animal Companion Flaw.",
        ),
        (
            "The Megabari",
            paragraphs(
                "Also called Trogodytes, they live east of the Cynamolgi and "
                "south of the Ethiopians, nomads with sheep, goats and cattle "
                "who follow the rains. They wear only loin skins and carry round "
                "oxhide shields, spears and bows, and their champions have huge "
                "iron-knobbed clubs.",
                "Each band's tyrant owns the two pairs of beasts, bull and cow, "
                "ram and sheep, that it calls Father and Mother. When one dies "
                "its mate is killed and a new pair chosen, whose owner is "
                "tyrant-in-waiting; when the old tyrant loses the other pair, the "
                "new man rules, adopted by a second pair.",
                "Women hold power and no man dares strike one. Only the tyrant "
                "has a wife; other women lie with whom they choose, and if his "
                "wife chooses a man he owes the tyrant a set number of sheep. In "
                "the rains they drink blood and milk left to seethe together. In "
                "the dry they fall back on the marshes and fight for the grass, "
                "first with stones, then with arrows, and so well that many "
                "die in moments. The women usually end it, running in to shield "
                "their sons. Some say their magicians make the carnivorous bull "
                "as vengeance on slavers.",
            ),
            "p. 126: men Puissant Bows and Prohibition (harming women); women "
            "Temporal Influence and Sensitive (to disrespect).",
        ),
    )
    for name, summary, rules in tribes:
        b.faction(name, summary=summary, rules=rules, place=slavelands)


# -- the Bestiary --


def _beasts(b: Builder, valley: Neighbour) -> None:
    b.creature(
        "Hippopotamus",
        page="p. 18",
        source=SOURCE,
        size=4,
        cunning=True,
        confidence=(1, 3),
        block={
            "characteristics": characteristics(-1, 0, -4, -5, 8, 3, 1, -4),
            "virtues_flaws": [
                "Ferocity",
                "Obese",
                "Poor Eyesight",
                "Aggressive",
                "Amphibious",
                "Extra Natural Weapons",
                "Herd Animal",
                "Large Teeth",
                "Overrun",
                "Tough Hide",
            ],
            "abilities": [
                ("Awareness", 3, "interlopers"),
                ("Athletics", 4, "running"),
                ("Brawl", 5, "tusks"),
                ("Survival", 3, "rivers"),
                ("Swim", 4, "rivers"),
            ],
            "traits": {"Bad Tempered": 3, "Territorial": 2},
        },
        attacks=[b.attack("Bite", -4, 10, 4, 13), b.attack("Stomp", -5, 9, 0, 11)],
        soak=6,
        fatigue_levels=FATIGUE,
        appearance=(
            "A huge pig-like beast with a wide mouth of long, peg-like tusks, "
            "five feet at the shoulder, up to twelve feet long, over 5000 "
            "pounds."
        ),
        notes=paragraphs(
            "Dozing in the mud it looks gentle, but it is fierce, territorial "
            "and shares the river with nobody. It gives way only to boats "
            "larger than itself, and overturns smaller ones by rising under "
            "them. By night it grazes on land, and people die when it thinks "
            "its way back to the water is cut off. It walks backwards into "
            "fields to fool trackers.",
            "Ferocity applies against those in its way. Natural weapons: "
            "Stomp Init -1, Atk +3, Def -1, Dam +3; Tusks Init 0, Atk +4, Def "
            "+2, Dam +5.",
            "Overrun is the errata's reading (p. 86).",
        ),
        place=valley,
    )
    b.creature(
        "Catoblepas",
        page="p. 19",
        source=SOURCE,
        realm="Magic",
        might=12,
        form="Animal",
        season="Spring",
        size=2,
        cunning=True,
        block={
            "characteristics": characteristics(-2, 0, -4, -4, 5, 5, 0, -1),
            "virtues_flaws": [
                "Magic Animal",
                "Magical Monster",
                ("Greater Immunity", {"hazard": "wood"}),
                ("Greater Immunity", {"hazard": "metal"}),
                vf_great("Stamina"),
                vf_great("Stamina"),
                "Strong-Willed",
                "Enfeebled",
                "Depressed",
                "Hunchback",
                "Infamous",
                HORNS,
                THICK,
                "Tough Hide",
                "Greater Power",
                *_times("Improved Might", 4),
                "Improved Powers",
                "Improved Soak",
                *_times("Lesser Power", 2),
                "Susceptible to Deprivation",
            ],
            "abilities": [
                ("Area Lore: Home", 3, "grazing"),
                ("Athletics", 3, "charging"),
                ("Awareness", 3, "hunters"),
                ("Brawl", 3, "horns"),
            ],
            "traits": {"Melancholy": 3, "Passive": 2, "Ponderous": 2},
            "reputations": {"Deadly (local)": 4},
        },
        attacks=[b.attack("Horns", 1, 7, 5, 8)],
        soak=12,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Gaze of Death",
                2,
                -5,
                "Corpus",
                rtd=("Eye", "", ""),
                level=40,
                does="Corpus and Animal. Anyone who meets its eyes when it has "
                "raised its head falls dead; lifting the head takes a round. "
                "PeCo(An) 40 (Base 30, +1 Eye, +1 requisite), a Greater Power "
                "(40 levels, -2 Might cost).",
            ),
            b.power(
                "Noxious Breath",
                0,
                -7,
                "Herbam",
                rtd=("Voice", "", "Group"),
                level=15,
                does="Plants it breathes on turn poisonous to people and animals "
                "and streak with black. An eater rolls Stamina stress against 9 "
                "or takes a Light Wound and is violently ill for a day; a botch "
                "makes it Medium. Medicine, not Chirurgy, treats it. PeHe 15 "
                "(Base 3, +2 Voice, +2 Group), a Lesser Power (15 levels, -3 "
                "Might cost with 5 mastery points from Improved Powers).",
            ),
            b.power(
                "Paralyzing Stench",
                0,
                -9,
                "Corpus",
                rtd=("", "Concentration", "Scent"),
                level=25,
                does="Corpus and Animal. It breathes out a foul choking cloud, "
                "and in the next round any human or animal within 3 paces who "
                "can smell it loses all bodily movement until it stops huffing "
                "or moves off. ReCo(An) 25 (Base 5, +1 Conc, +2 Scent, +1 "
                "requisite), a Lesser Power (25 levels, -2 Might cost and +2 "
                "Init with 20 mastery points from Improved Powers).",
            ),
        ],
        vis=[BodyVis(3, "Perdo", "in its eyes")],
        appearance=(
            "A bull-sized beast whose huge head hangs low, its great bloodshot "
            "eyes half hidden by a shaggy reddish mane. Horns sweep down above "
            "the eyes; overlapping black scales cover it; its tail is white "
            "like a horse's."
        ),
        notes=paragraphs(
            "It lives on the upper Nile in Alodia and Ethiopia, and in the "
            "Slavelands, rumour says, in great migrating herds. A placid, "
            "slow grazer, it staggers a few paces and must eat and rest, a "
            "great nuisance on good pasture. The first sign of one may be a "
            "crop gone poisonous overnight. Its huge eyes are hard to avoid, "
            "even in combat, though the gaze has weak Penetration. Metal and "
            "wood do not harm its scales.",
            "Natural weapon: Large Horns Init +2, Atk +3, Def +2, Dam +3.",
        ),
        place=valley,
    )
    b.creature(
        "Crocodile",
        page="p. 19",
        source=SOURCE,
        size=3,
        cunning=True,
        confidence=(1, 3),
        block={
            "characteristics": characteristics(1, 0, -2, -5, 6, 2, 1, 1),
            "virtues_flaws": [
                vf_great("Quickness"),
                "Ferocity",
                "Improved Abilities",
                "Tough",
                "Enemies",
                "Infamous",
                "Aggressive",
                "Ambush Predator",
                "Amphibious",
                "Camouflage",
                "Crushing Jaws",
                "Roll Attack",
                THICK,
                "Tough Hide",
            ],
            "abilities": [
                ("Athletics", 2, "short sprints and lunges"),
                ("Awareness", 3, "food"),
                ("Brawl", 5, "in water"),
                ("Hunt", 4, "prey"),
                ("Stealth", 4, "stalking prey"),
                ("Survival", 3, "river"),
                ("Swim", 2, "rivers"),
            ],
            "traits": {"Phlegmatic": 3, "Patient": 3},
            "reputations": {"Killer (local)": 4},
        },
        attacks=[b.attack("Bite", 2, 10, 7, 12)],
        soak=12,
        fatigue_levels=FATIGUE,
        appearance=(
            "Fifteen to eighteen feet of thick scales, in yellows, greens and "
            "browns that hide it perfectly in water or out. Its name is said "
            "to come from the yellow of the crocus."
        ),
        notes=paragraphs(
            "The corkendrile is the feared killer of the Nile and its "
            "tributaries. It dreads the mongoose, which finds its nest to kill "
            "the young and will even crawl down its throat. These figures are "
            "for fifteen feet; thirty-foot (Size +5) or larger beasts are "
            "reported. This is tougher than the crocodile of Magi of Hermes p. "
            "11.",
            "Ferocity applies in ambush. Natural weapon: Init 0, Atk +4, Def "
            "+1, Dam +3, before Crushing Jaws (p. 22). Its scales count as "
            "Protection 5 besides its Virtues and Qualities. Roll Attack is "
            "the book's Death Roll (errata p. 87).",
            "It holds its breath half an hour moderately active, two hours "
            "inactive. +3 to Stealth when still or slow in water. " + SURPRISE,
        ),
        place=valley,
    )
    elephant_block: StatBlock = {
        "characteristics": characteristics(1, 1, 1, -5, 12, 3, 0, -3),
        "virtues_flaws": [
            "Improved Characteristics",
            "Ferocity",
            "Tough",
            "Fear",
            "Aggressive",
            "Amphibious",
            "Crafty",
            "Defensive Fighter",
            "Extra Natural Weapons",
            "Grapple",
            "Herd Animal",
            *_times("Imposing Appearance", 2),
            HORNS,
            "Overrun",
            "Sharp Ears",
            THICK,
            "Tough Hide",
            "Trunk",
        ],
        "abilities": [
            ("Athletics", 3, "running"),
            ("Awareness", 3, "food"),
            ("Brawl", 5, "tusks"),
            ("Leadership", 5, "elephants"),
            ("Survival", 3, "forests or plains"),
            ("Swim", 4, "rivers"),
        ],
        "traits": {"Lustful": -3, "Wise": 2},
    }
    attacks = [
        b.attack("Tusks", -3, 12, 6, 15),
        b.attack("Stomp", -3, 8, 2, 15),
        b.attack("Trunk (grapple)", -2, 5, 2, None),
    ]
    elephant_weapons = (
        "Natural weapons: Stomp Init -1, Atk +3, Def -1, Dam +3; Tusks Init 0, Atk "
        "+6, Def +4, Dam +3; the trunk only grapples. "
        "Ferocity defends its family; Fear is of a pig's squeal. Excellent "
        "hearing and a sense of vibration through the trunk give +3 on rolls of "
        "hearing."
    )
    b.creature(
        "Elephant",
        page="p. 20",
        source=SOURCE,
        size=5,
        cunning=True,
        confidence=(1, 3),
        block=elephant_block,
        attacks=attacks,
        soak=10,
        fatigue_levels=EXTRA_FIRST,
        appearance=(
            "The African elephant stands up to 12 feet, 22 feet long, up to "
            "14,000 pounds. These are the fiercer male's figures; a female can "
            "weigh half as much, with small, useless tusks."
        ),
        notes=paragraphs(
            "Once down an elephant cannot get up, so it sleeps leaning on a "
            "tree, and hunters cut part way through its favourite. Dragons and "
            "great serpents by the Nile prey on it, yet a pig's squeal terrifies "
            "it. It has no wish to mate: the pair must eat of one mandragora "
            "root. A cow carries two years and bears one calf, and an elephant "
            "may live three hundred years.",
            elephant_weapons,
            "Only the herd leader has Leadership, and the Pack/Herd Leader "
            "Quality rather than Herd Animal. The errata (p. 87) give Com -5/-4* "
            "and do not explain the asterisk. Reading it as the book's own "
            "footnote, 'herd leader only' (p. 20), Com is -5 and herd leaders "
            "have -4; this is an inference, not a printed rule.",
            "Female: Size +4, -2 Strength, +1 Quickness; no Aggressive, Extra "
            "Natural Weapons or Large Horns (Tusks) Qualities and no Ferocity; "
            "Brawl 4 (dodge); no Tusk attack; Communication -5.",
        ),
        place=valley,
    )
    old_man = dict(elephant_block)
    old_man["characteristics"] = characteristics(2, 1, 1, -4, 12, 3, 0, -3)
    old_man["virtues_flaws"] = [
        "Magic Animal",
        *elephant_block["virtues_flaws"],
        "Greater Power",
        "Gift of Speech",
        *_times("Improved Abilities", 3),
        "Improved Characteristics",
        vf_minor("Arcane Lore"),
        vf_minor("Educated"),
        vf_minor("Well Traveled"),
    ]
    old_man["abilities"] = [
        ("Area Lore: Nubia", 6, "inhabitants"),
        ("Area Lore: Slavelands", 5, "landscape"),
        ("Artes Liberales", 3, "debate"),
        ("Athletics", 3, "running"),
        ("Awareness", 3, "food"),
        ("Brawl", 5, "tusks"),
        ("Chirurgy", 5, "spear wounds"),
        ("Dominion Lore", 3, "saints"),
        ("Faerie Lore", 6, "legends"),
        ("Infernal Lore", 3, "wilderness demons"),
        ("Leadership", 5, "elephants"),
        ("Living Language: Cynegi", 5, "eavesdropping"),
        ("Living Language: Nubian", 3, "debate"),
        ("Magic Lore", 5, "creatures"),
        ("Medicine", 4, "healing diseases"),
        ("Philosophiae", 5, "metaphysics"),
        ("Profession: Apothecary", 4, "healing herbs"),
        ("Survival", 3, "forests or plains"),
        ("Swim", 4, "rivers"),
    ]
    b.creature(
        "The Old Man of the Forest",
        page="p. 20",
        source=SOURCE,
        realm="Magic",
        might=11,
        form="Animal",
        season="Autumn",
        size=5,
        confidence=(1, 3),
        block=old_man,
        attacks=attacks,
        soak=10,
        fatigue_levels=EXTRA_FIRST,
        powers=[
            b.power(
                "Invisibility of the Standing Elephant",
                0,
                -5,
                "Imaginem",
                rtd=("", "Sun", ""),
                level=25,
                does="He cannot be seen while he stands still, and shows himself "
                "whenever he moves. PeIm 25 (Base 4, +2 Sun, +2 Size, +1 "
                "constant effect), a Greater Power (25 levels, -3 Might cost, +2 "
                "Init).",
            ),
        ],
        appearance=(
            "Very old, his skin more wrinkled than any elephant's and hanging "
            "from a thin frame, with immense tusks that touch the ground and "
            "curl up at the tips."
        ),
        notes=paragraphs(
            "Elephants grow wiser with age, until they are sages of all that "
            "is under the sun, and tribesmen say such a one can vanish at will. "
            "He reasons as a man does and is a Magic Animal, otherwise an "
            "elephant.",
            elephant_weapons,
        ),
    )
    b.creature(
        "Mongoose",
        page="p. 21",
        source=SOURCE,
        size=-4,
        cunning=True,
        confidence=(1, 3),
        block={
            "characteristics": characteristics(1, 0, -2, -5, -5, 2, 1, 4),
            "virtues_flaws": [
                "Berserk",
                "Ferocity",
                ("Immune to {source} (Minor)", {"source": "venom"}),
                "Improved Characteristics",
                "Reckless (Minor)",
                "Crafty",
                "Pursuit Predator",
                "Skilled Climber",
                "Tireless",
            ],
            "abilities": [
                ("Athletics", 3, "chasing"),
                ("Awareness", 3, "rodents"),
                ("Brawl", 3, "bite"),
                ("Hunt", 4, "snakes"),
                ("Survival", 3, "riverbanks"),
            ],
            "traits": {"Fearless": 5, "Curious": 3},
        },
        attacks=[b.attack("Teeth", 4, 8, 9, -4)],
        soak=3,
        fatigue_levels=EXTRA_THREE,
        appearance=(
            "A long animal of grizzled gray fur with a black tuft on its tail, "
            "about 3.5 feet nose to tail, eight pounds."
        ),
        notes=paragraphs(
            "The ichneumon, bane of all snakes. Egyptians welcome it in houses "
            "and grain stores, where it kills mice, rats and every reptile, and "
            "it flies at any asp and fights until the snake is dead. Pliny says "
            "it rolls in mud that dries like stone against the fangs. One kind, "
            "the enhydrus, hates crocodiles: it waits for one to sleep "
            "open-mouthed, crawls in, and eats its way out.",
            "Ferocity is against serpents; the book names its Immunity without "
            "a tier. Natural weapon: Init 0, Atk +3, Def +1, Dam +1. +3 to "
            "climbing. Dried mud gives +5 Protection, takes at least three "
            "hours to dry, and loses 1 every three rounds of combat. An enhydrus "
            "inside a crocodile faces zero Defense and Soak Total.",
        ),
        place=valley,
    )
    b.creature(
        "Hyena",
        page="p. 22",
        source=SOURCE,
        size=-1,
        cunning=True,
        confidence=(0, 0),
        block=_hyena(),
        attacks=[b.attack("Bite", 2, 9, 7, 5), b.attack("Dodge", 2, None, 5, None)],
        soak=3,
        fatigue_levels=EXTRA_FIRST,
        appearance=(
            "The striped hyena has a massive torso and short hind legs that "
            "slope its back, a short muzzle on a large head, and a long, thick, "
            "stiff neck."
        ),
        notes=paragraphs(
            "The dhubba lives across the Levant, North Africa, Iraq, Persia and "
            "beyond. It can be tamed like a dog, even running in a pack if "
            "raised with hounds; though not sacred in ancient Egypt, it hunted "
            "desert game there. Greater African beasts (Size +1) are often "
            "ridden by jinn or witches, and ghuls often take its shape.",
            "Natural weapon: Init 0, Atk +4, Def +1, Dam +3, raised to +6 by "
            "Crushing Jaws (p. 22), already in the Bite line.",
        ),
        place=valley,
    )
    b.creature(
        "Ostrich, African",
        page="p. 23",
        source=SOURCE,
        size=1,
        cunning=True,
        confidence=(0, 0),
        block={
            "characteristics": characteristics(-2, 2, -1, -2, 2, 2, 2, 2),
            "virtues_flaws": [
                "Improved Characteristics",
                "Keen Vision",
                "Perfect Balance",
                "Sharp Ears (Minor)",
                "Fragile Constitution",
                "Camouflage",
                "Defensive Fighter",
                "Fast Runner",
                "Hardy",
                "Herd Animal",
                "Keen Eyesight",
                THICK,
            ],
            "abilities": [
                ("Athletics", 3, "running"),
                ("Awareness", 4, "predators"),
                ("Brawl", 4, "dodging"),
                ("Survival", 5, "home terrain"),
                ("Thrown Weapon", 4, "stones"),
            ],
        },
        attacks=[
            b.attack("Dodge", 3, None, 5, None),
            b.attack("Kick (as hoof)", 4, 8, 6, 2),
            b.attack("Thrown Stone", -1, 8, 7, 6),
        ],
        soak=4,
        fatigue_levels=EXTRA_FIRST,
        appearance=(
            "A large bird with long neck and legs and huge eyes. Males are "
            "black with white tail plumes and wing fringes, females a duller "
            "gray."
        ),
        notes=paragraphs(
            "Common in Nubia and Ethiopia, with a smaller kind in North Africa, "
            "Egypt and Arabia. Valued for feathers, leather and eggs, less for "
            "meat, they roam the semi-arid plains in great flocks and avoid the "
            "deep desert. Nobles love to hunt them. They hide their heads in "
            "bushes when threatened, but can be trained out of it and ridden by "
            "light riders. The African bird hurls stones with its feet, hard "
            "and straight.",
            "The block's Thick Feathers are the catalog's Thick Fur/Thick "
            "Scales. Natural weapon: kick Init +2, Atk +2, Def +0, Dam +0. "
            "Stones count as a sling with range increment 15 paces. +3 to "
            "running.",
        ),
        place=valley,
    )
    b.creature(
        "Elephant-Eating Serpent",
        page="p. 23",
        source=SOURCE,
        size=4,
        cunning=True,
        block={
            "characteristics": characteristics(0, -2, -6, -6, 8, 2, 2, 0),
            "virtues_flaws": [
                vf_great("Quickness"),
                "Improved Characteristics",
                "Poor Eyesight",
                "Aggressive",
                "Ambush Predator",
                "Camouflage",
                "Constriction",
                "Grapple",
                "Keen Sense of Smell",
                "Slippery",
                "Swallow Whole",
                "Tireless",
            ],
            "abilities": [
                ("Awareness", 2, "avoiding being trodden on"),
                ("Brawl", 5, "grapple"),
                ("Hunt", 4, "elephants"),
                ("Stealth", 4, "among rocks"),
                ("Survival", 3, "ravines"),
                ("Swim", 3, "rivers"),
            ],
            "traits": {"Dispassionate": 3},
        },
        attacks=[b.attack("Bite", 0, 10, 6, 9), b.attack("Grapple", 0, 8, 12, None)],
        soak=3,
        fatigue_levels=EXTRA_TWO,
        appearance=(
            "Over 45 feet long and nearly two feet through at the thickest, "
            "mottled brown with swirls of olive, black and yellow."
        ),
        notes=paragraphs(
            "They lie in ravines at the foot of hills and deep caves, and "
            "gather to feed at rivers where elephants come. Several often "
            "attack one elephant as an untrained group; all may grapple, but "
            "only one can constrict. They take other prey gladly. One lassoes "
            "the legs in a knot of its tail, then smothers the beast, spending "
            "a Fatigue level on its first bite and another when it throws its "
            "coils. It takes hours to work a dead creature of up to Size +5 "
            "into its jaws.",
            "Constriction takes a victim of Size +5 or less; Swallow Whole takes "
            "prey of Size -1 or less alive. Prey not first subdued by "
            "Constriction can struggle, still constricted (errata p. 87: both "
            "are Qualities).",
            "The Grapple's Defense includes +6 for Slippery. Natural weapon: "
            "Init 0, Atk +3, Def +1, Dam +1. " + SURPRISE + " +3 to Stealth when "
            "still, and +3 to Perception by smell.",
        ),
        place=valley,
    )


def _hyena() -> StatBlock:
    return {
        "characteristics": characteristics(1, 2, -4, -1, -1, 2, 1, 2),
        "virtues_flaws": [
            "Improved Characteristics",
            "Keen Vision",
            vf_puissant("Guile"),
            ("Social Handicap", {"detail": "unpleasant odour"}),
            "Nocturnal",
            "Crafty",
            "Keen Eyesight",
            "Large Teeth",
            "Mimicry",
            "Pursuit Predator",
            THICK,
        ],
        "abilities": [
            ("Athletics", 3, "running"),
            ("Awareness", 3, "food"),
            ("Brawl", 3, "bite"),
            ("Guile", 1, "feign dead"),
            ("Hunt", 4, "tracking"),
            ("Survival", 3, "desert"),
        ],
        "traits": {"Cowardly": 3, "Sly": 2},
        "reputations": {"Treacherous (local)": 2},
    }


def _baboon_block() -> StatBlock:
    return {
        "characteristics": characteristics(2, 0, -2, 0, -4, 0, 2, 1),
        "virtues_flaws": [
            "Berserk",
            ("Learn {ability} From Mistakes", {"ability": "Athletics"}),
            "Oversensitive (Minor)",
            "Short Attention Span",
            "Aggressive",
            "Ambush Predator",
            "Crafty",
            "Pack Animal",
            "Skilled Climber",
            "Vocal",
        ],
        "abilities": [
            ("Athletics", 3, "climbing"),
            ("Awareness", 3, "food"),
            ("Brawl", 5, "bite"),
            ("Hunt", 4, "prey"),
            ("Stealth", 4, "stalking prey"),
            ("Survival", 3, "savannah"),
        ],
        "traits": {"Mischievous": 2, "Brave": 2},
    }


def _monkey(
    b: Builder,
    valley: Neighbour,
    name: str,
    size: int,
    swaps: dict[str, Any],
    extra: list[Any],
    strength: int,
    quickness: int,
    presence: int,
    stealth: int,
    appearance: str,
    notes: str,
) -> Creature:
    """A monkey the book gives as changes to the baboon."""
    block = _baboon_block()
    block["characteristics"] = characteristics(
        2, 0, presence, 0, strength, 0, 2, quickness
    )
    block["virtues_flaws"] = [
        swaps.get(entry, entry) if isinstance(entry, str) else entry
        for entry in block["virtues_flaws"]
    ] + extra
    block["abilities"] = [
        (ability, stealth if ability == "Stealth" else score, specialty)
        for ability, score, specialty in block["abilities"]
    ]
    return b.creature(
        name,
        page="p. 22",
        source=SOURCE,
        size=size,
        cunning=True,
        block=block,
        appearance=appearance,
        notes=paragraphs(
            notes,
            "Combat figures follow the baboon's, adjusted for Size. Troop "
            "leaders have Com +1, inferred as for the baboon.",
        ),
        place=valley,
    )


def _monkeys(b: Builder, valley: Neighbour) -> None:
    b.creature(
        "Baboon",
        page="p. 22",
        source=SOURCE,
        size=-2,
        cunning=True,
        block=_baboon_block(),
        attacks=[b.attack("Bite", 2, 11, 9, -3), b.attack("Evasion", 2, None, 9, None)],
        soak=1,
        fatigue_levels=FATIGUE,
        appearance=(
            "A fierce dog-faced monkey, olive brown; the males have a silvery "
            "gray cape and mane."
        ),
        notes=paragraphs(
            "The hamadryas or cynocephalus, 'dog head', most aggressive of "
            "African monkeys and the chief of the region's many kinds. All "
            "monkeys fight as a trained group when threatened; only baboons "
            "attack so, and even hunt that way. A monkey always bears twins, "
            "hugging the one she loves and leaving the other to ride on her "
            "back, but she drops the loved one to escape a predator.",
            "Oversensitive is to threats. Pack leaders also have Pack/Herd "
            "Leader. Characteristics, Qualities and Abilities follow the errata "
            "(p. 87), whose list drops the book's Leadership 5 (monkeys) for "
            "troop leaders. It gives Com 0/+1* and does not explain the "
            "asterisk. Reading it as the book's own footnote, 'troop leaders "
            "only' (p. 22), Com is 0 and troop leaders have +1; this is an "
            "inference, not a printed rule. Natural weapon: Init +1, Atk +3, "
            "Def +2, Dam +1.",
        ),
        place=valley,
    )
    _monkey(
        b,
        valley,
        "Cercopithecus",
        -4,
        {"Berserk": "Light Touch", "Oversensitive (Minor)": "Carefree"},
        ["Fast Runner", "Timid"],
        -8,
        4,
        -3,
        4,
        "The smallest monkey, shaggy and reddish brown with a long tail, white "
        "legs and belly, a brighter red cap and black lines from face to ear. "
        "Gray, black-faced ones live in forests near the Torrid Zone.",
        "An incorrigible thief. Its changes (Size -4, Str -8, Qik +4, Timid "
        "taking 1 from Presence, Stealth 4) are the book's.",
    )
    _monkey(
        b,
        valley,
        "Callithrix",
        -3,
        {"Berserk": "Perfect Balance", "Oversensitive (Minor)": "Palsied Hands"},
        [],
        -6,
        3,
        -2,
        4,
        "A black monkey with a long white beard, a long shawl of white fur over "
        "its back and a white tuft on its tail.",
        "It has no thumb, hence Palsied Hands. Native to the Horn of Africa, "
        "and sometimes an Egyptian's pet.",
    )
    _monkey(
        b,
        valley,
        "Sphinx (monkey)",
        -2,
        {"Berserk": "Piercing Gaze", "Oversensitive (Minor)": "Noncombatant"},
        [],
        -4,
        1,
        -2,
        4,
        "A docile, shaggy beast with a long tail. The male has a lion-like mane "
        "and a bright face: red stripe, blue muzzle and yellow beard.",
        "Native to the far south, sometimes found in Ethiopia and beyond.",
    )


def _templates(b: Builder, valley: Neighbour) -> None:
    b.creature(
        "Asp",
        page="p. 17",
        source=SOURCE,
        size=-3,
        cunning=True,
        appearance=(
            "The aspis or cobra grows to ten feet and spreads a dreadful hood "
            "from the sides of its head."
        ),
        notes=paragraphs(
            "So potent is its venom that it travels with its mouth open, and "
            "the steam wilts plants nearby. Music is its weakness: seeing an "
            "instrument it presses one ear to the ground and plugs the other "
            "with its tail.",
            "Build on the adder (The Book of Mundane Beasts, or the Appendix of "
            "Realms of Power: Magic): Size -3, +2 to Strength and Damage, -1 to "
            "Quickness, Initiative and Defense. Enchanting Music charms it with "
            "no roll. Venom: Stamina against 9 or an Incapacitating Wound, "
            "needing Medicine rather than Chirurgy.",
        ),
        place=valley,
    )
    crocotta = _hyena()
    crocotta["characteristics"] = characteristics(2, 2, -4, -1, 4, 2, 1, 3)
    crocotta["virtues_flaws"] = [
        *crocotta["virtues_flaws"],
        "Gender Shift",
        "Improved Characteristics",
        "Tough",
        "Tainted With Evil",
        ("Greater Immunity", {"hazard": "steel"}),
        "Aggressive",
        "Tough Hide",
    ]
    crocotta["abilities"] = [
        ("Brawl", 5, "bite") if name == "Brawl" else (name, score, specialty)
        for name, score, specialty in crocotta["abilities"]
    ] + [("Living Language: Arabic", 3, "mimicry")]
    crocotta["traits"] = {"Fierce": 3, "Sly": 2}
    b.creature(
        "Hyena of Virtue",
        page="p. 18",
        source=SOURCE,
        size=1,
        block=crocotta,
        appearance=(
            "A great spotted hyena with a cackle like human laughter, larger "
            "and stronger than its striped cousins."
        ),
        notes=paragraphs(
            "The crocotta or kynolykos, 'dog-wolf', of Ethiopia, believed born "
            "of hyena and lion. It mimics speech to trick people, and steel "
            "does not harm it. Many can enthrall victims. Some strike dogs "
            "dumb when their shadow falls on them, and can paralyse any "
            "creature they look at three times.",
            "Size is at least +1. Its speech equals Arabic 3. Combat figures "
            "follow the hyena's, adjusted. Entrancement, for those who have it, "
            "is not in this block. Sex Shift is the catalog's Gender Shift.",
            "Charms: a stone from its body, enriched, gives its wearer on the "
            "upper arm protection (Personal Power: Ward Against Faeries of the "
            "Desert), or sight of the future (Premonitions and/or Visions). "
            "Some cultures say its eyes do the same. A Persian charm of its "
            "genitalia and anus gives Venus' Blessing.",
        ),
        place=valley,
    )
    b.creature(
        "Ethiopian Pegasus",
        page="p. 21",
        source=SOURCE,
        appearance="A winged horse with a pair of long horns on its head.",
        notes=paragraphs(
            "Pliny's Pegasus Aethiopicum, perhaps descended from the horse "
            "Bellerophon rode, child of Medusa and Poseidon, conceived in "
            "Athena's Libyan temple and born when Perseus beheaded her. As "
            "Perseus flew to save Andromeda from the dragon Ceto, more drops "
            "fell on the sand and bred more pegasi.",
            "Otherwise as a courser (The Book of Mundane Beasts, or Realms of "
            "Power: Magic p. 142). Horns: Init +2, Atk +3, Def +2, Dam +3.",
        ),
        place=valley,
    )


def _marvels(b: Builder, valley: Neighbour, slavelands: Neighbour) -> None:
    b.creature(
        "Carnivorous Bull",
        page="p. 126",
        source=SOURCE,
        realm="Magic",
        might=10,
        form="Animal",
        season="Summer",
        size=2,
        cunning=True,
        confidence=(1, 3),
        block={
            "characteristics": characteristics(1, 0, -4, -4, 5, 3, 0, 0),
            "virtues_flaws": [
                "Ferocity",
                vf_puissant("Brawl"),
                "Tough",
                "Greater Power",
                ("Improved Attack", {"weapon": "horns"}),
                ("Improved Damage", {"weapon": "horns"}),
                "Improved Powers",
                *_times("Improved Soak", 2),
                *_times(vf_minor("Improved Abilities"), 2),
                vf_minor("Lesser Immunity (piercing weapons)"),
                "Aggressive",
                "Ambush Predator",
                "Fast Runner",
                HORNS,
                "Tough Hide",
            ],
            "abilities": [
                ("Athletics", 4, "charging"),
                ("Awareness", 3, "prey"),
                ("Brawl", 5, "horns"),
                ("Guile", 4, "pretending to be a normal cow"),
                ("Hunt", 4, "cows"),
                ("Stealth", 5, "stalking prey"),
                ("Survival", 3, "plains"),
            ],
            "traits": {"Hungry": 5, "Bull": 3, "Sly": 2},
        },
        attacks=[b.attack("Horns", 2, 13, 8, 11), b.attack("Teeth", 0, 11, 8, 8)],
        soak=12,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Calm the Lowing Herd",
                2,
                -2,
                "Animal",
                rtd=("Voice", "Sun", "Group"),
                level=45,
                does="Keeps the animals round it calm and quiet while it kills, "
                "up to 50 cows or the like. ReAn 45 (Base 10, +2 Voice, +2 Sun, "
                "+2 Group, +1 Size), a Greater Power (45 levels, -3 Might cost, "
                "+3 Init with Improved Powers).",
            ),
        ],
        appearance=(
            "A massive red bull, whose mouth opens over 100 degrees, right back "
            "to the ears, enough to take a cow's head whole, though this is "
            "hard to see when shut. Its horns swivel like ears or hold rigid, "
            "and its eyes glow at night. A careful watcher might see the odd "
            "twitch of a horn, or that it never eats grass."
        ),
        notes=paragraphs(
            "Bred in the land of the Megabari and sometimes brought back by "
            "Nubians with captured stock. It has the prowess of a lion, the "
            "speed of a horse and the might of a bull. It slips into a large "
            "herd and picks off cows one by one, leaving not a bone, hide, horn "
            "or hoof, and takes dogs and herdsmen who come too close. It needs "
            "no food, being a creature of magic; its nature drives it.",
            "Also has the Flaw Gluttonous. Bull is its Essential Trait. Its "
            "Ferocity is in charging. Natural weapons: Large Horns Init +2, Atk "
            "+3, Def +2, Dam +3; Large Teeth Init 0, Atk +4, Def +1, Dam +3. "
            "Brawl has its Puissant bonus of +2 on top. Until its nature is "
            "spotted it automatically wins Initiative in the first round and "
            "has +3 to Attack Totals for that round only. +3 to running.",
        ),
        place=slavelands,
    )
    b.creature(
        "Hylophagus",
        page="p. 124",
        source=SOURCE,
        size=-2,
        block={
            **_baboon_block(),
            "virtues_flaws": [
                *_baboon_block()["virtues_flaws"],
                "Perfect Balance",
                "Primitive Equipment",
            ],
        },
        appearance="A small, nimble, tailed person in pale fur, dressed in leaves.",
        notes=(
            "An intelligent monkey: the baboon's block with Perfect Balance and "
            "Primitive Equipment (Grogs p. 83), which limits it to the simplest "
            "tools and Inexpensive arms and armour. See The Hylophagi. Combat "
            "figures follow the baboon's."
        ),
        place=slavelands,
    )


# -- the stories --


def _stories(b: Builder, slavelands: Neighbour) -> None:
    for name, summary in ASHAMED:
        dormant(b.threat(name, summary=summary))
    dormant(
        b.threat(
            "Coastal Raiders",
            summary=(
                "A tribe of Icthyophagi have tamed one of the great sea-eels of "
                "the Red Sea and are raiding merchant ships with it, very unlike "
                "that peaceful people."
            ),
            secrets="Who is really directing the tribe is left open.",
            antagonist="The Icthyophagi",
        )
    )
    dormant(
        b.threat(
            "Tribal Medicine",
            summary=(
                "A king's daughter lies ill with a disease nothing can cure. "
                "Rumour tells of a Rhizophagus healer of remarkable powers, and "
                "the characters are asked, or tempted by the reward, to find a "
                "cure."
            ),
            place=slavelands,
        )
    )
    dormant(
        b.threat(
            "The Far-Away Tree",
            summary=(
                "A tribe of Hylophagi live in a magically awakened village-tree "
                "that once wandered their own lands. Now it has turned toward "
                "the Nile Valley. Its rubbery bark and fibrous wood shrug off "
                "most weapons, it stamps flat houses and armies alike, and "
                "the tribe in its branches have clubs and rocks. The locals turn "
                "to the magi."
            ),
            secrets=(
                "If the characters cannot attack it directly, they should learn "
                "why the tree has turned north: perhaps the tribe's new "
                "witch-doctor."
            ),
            antagonist="The village-tree and its Hylophagi",
            place=slavelands,
        )
    )
    dormant(
        b.threat(
            "Famine of Ages",
            summary=(
                "Acridophagi come into the Nile Valley seeking help and meet "
                "contempt. The characters may yet listen to them."
            ),
            secrets=(
                "Long ago a sorcerer bound a famine demon into an Acridophagus "
                "child, inking the bindings on his skin. The boy lived as a "
                "king, safe from harm: at his death the winged lice would each "
                "carry off a piece of the demon and destroy it. Now the tribe "
                "fear the sorcerer was corrupt, and that when the man soon dies "
                "the demon will be multiplied and borne to the ends of the "
                "earth. The answer may lie in finding the sorcerer, surely very "
                "powerful by now, or be as simple as killing the vessel."
            ),
            antagonist="A famine demon",
            realm="Infernal",
        )
    )
    dormant(
        b.threat(
            "The Gamekeeper Turned Poacher",
            summary=(
                "A bouda plagues the district around a covenant, and even a "
                "magus cannot kill what he cannot find. A Cynamolgus might be "
                "the answer, and a wanderer cut off from his homeland is rumoured "
                "to be nearby."
            ),
            secrets=(
                "His price is steep, and when the work is done he may prove more "
                "trouble than the bouda was."
            ),
        )
    )
    dormant(
        b.threat(
            "The Man-Eating Cow",
            summary=(
                "All through Nubia cattle are dying mysteriously. Most just "
                "vanish, though now and then a skin or a bloodless body turns "
                "up. Magic is suspected, and the characters may fall under "
                "suspicion themselves."
            ),
            secrets=(
                "Every lost cow came from Megabari lands: stolen spoils among "
                "which came carnivorous bulls, now loose in the herds of Makuria."
            ),
            antagonist="Carnivorous bulls",
        )
    )
