"""Africa and Its People (BS&S ch. 1, pp. 6-39), in paraphrase: the land as
the book first draws it, its history, the living powers, the Berbers,
Arabs and Tuareg, the Banu Khalida and their Twelve Cities, two people
with stat blocks, the Jealous Wife, and the chapter's story seeds.

The cities, the coast and the deep desert are told at length in the
chapters after this one, so the desert's mountains and oases are words
here. The Great Hunger, the Hope and the Pact of 1225 are hunger.py's. The
Almohad caliph is this part's, and the sultan of Egypt is east.py's shared
record. Hidden facts and everything for the storyguide alone are under
secrets=."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...models import BodyVis
from ..builder import Builder, characteristics, dormant, paragraphs, wound_ranges
from ..east import al_kamil

if TYPE_CHECKING:
    from ...models import Neighbour


def build(b: Builder) -> None:
    africa = _land(b)
    caliph, sultan = _rulers(b, africa)
    _history(b)
    _peoples(b, caliph)
    _customs(b)
    tuareg = _tuareg(b)
    twelve = _banu_khalida(b)
    _people_with_stats(b)
    _jealous_wife(b)
    _seeds(b, africa, tuareg, twelve, sultan)


# -- the land --


def _land(b: Builder) -> Neighbour:
    africa = b.place(
        "Mythic Africa",
        summary=paragraphs(
            "The third of the world's three continents, lying between the "
            "Mediterranean and the Great Ocean, with the Nile on its east and "
            "the Atlantic on its west. It takes its name from the Roman "
            "province, which the Arabs still call Ifriqiyeh; Arab writers call "
            "the land Bilad al-Barbar or al-Maghrib, 'the West', and Europeans "
            "still draw Gaetula at its heart and Ethiopia beyond. The strip "
            "between desert and sea looks barely fit to live in, yet some of "
            "the widest-ruling dynasties the world has known began here.",
            "To a European it is a land of wonder: in the markets of Marrakesh "
            "spices lie in open heaps beside cloth of impossible colour, "
            "blemmyae trade raw gold from camels guarded by huge black-furred "
            "dog-heads, and at the desert's edge the heat is a smith's forge. "
            "Small raiders ride ostriches, Tuareg ride out of a mirage and are "
            "gone, and in the deep sands travellers tell of ancient cities, "
            "the congresses of demons and talk with angels. It is also a land "
            "of hunger: the spirit at the desert's centre would dry every "
            "oasis and grind the mountains to dust, and only what has been "
            "raised against it has stopped it. Egypt called on the black "
            "earth, Carthage paid its gods for protection, and some think the "
            "Hunger moved Rome to destroy them and left it needing a protector "
            "of its own. Today the Dominion, Christian and then Muslim, makes "
            "a thin firm wall. "
            "Those who live here hardly notice either theme; a stranger "
            "notices both.",
            "The time of legends gave the land the giant Antaios (Antaeus to "
            "the Romans, Anti to the Berbers), who raised a temple to his "
            "father Poseidon out of the skulls of those he beat at wrestling "
            "and drew his strength from his mother the earth, until Herakles, "
            "on the way to the Apples of the Hesperides, held him off the "
            "ground and crushed his ribs. By Antaios's wife Tinjis, Herakles "
            "fathered Sufax, mythic ancestor of the Berbers, who built Tangier "
            "in his mother's name and took up the giant's guardianship of the "
            "country.",
            "Dido the Phoenician founded Carthage in 814 BC, and at its height "
            "its trade ran from the Gulf of Sidra to the Atlantic with colonies "
            "in Spain, Sicily, Sardinia and Corsica, while Greeks held the "
            "coast of Cyrenaica and Tripolitania and Berber kingdoms, Numidia "
            "and Mauritania the greatest, traded with it. In the Second Punic "
            "War the Numidian kings took opposite sides: Suphax of the western "
            "Masaesyli for Rome and Gala of the eastern Massylii for Carthage, "
            "until Gala's heir Massinissa, seeing who was winning, went over to "
            "Rome and Suphax allied with Hasdrubal, Hannibal's brother. Rome "
            "razed Carthage in 146 BC, salted its fields and made the Province "
            "of Africa; Massinissa received Numidia. His grandson Jugurtha "
            "fought Rome from 112 BC until Mauritania helped capture him in "
            "104 BC. Claudius split Mauritania into Caesariensis and Tingitana.",
            "The Roman provinces grew rich and Latin-speaking, and Christianity "
            "gave them Tertullian, Cyprian and Augustine, then, as Rome faded, "
            "Arianism, Pelagianism, Donatism and Montanism. The tribes of the "
            "interior paid tribute, sent auxiliaries and otherwise lived as "
            "before. The Vandals raided Tingitana in 422; invited in under "
            "Gaiseric by the Comes Africae to be penned there, they refused all "
            "control and the provinces were lost until Belisarius retook "
            "Africa for Byzantium in 522. Byzantium held only the coastal "
            "towns, playing chiefs against each other, while the Luwata in the "
            "east, the Sanhaja in the west and centre and the Zenata in the "
            "south and south-west held the rest.",
            "Umayyad raiders reached Cyrenaica in 642 and were bribed away. "
            "'Uqbah ibn Nafi returned in 670, founded al-Qayrawan and carried "
            "Arab rule across the Maghreb until the chief Kusayla slew him in "
            "683. Under Kusayla and then the Kahina the Berbers held twenty "
            "years, and Umayyad wizards found their spirits deserting them "
            "before Berber magic. The Arabs won at last by buying tribes with "
            "land and reward, finishing the resistance in 711, and the mostly "
            "Berber army of Tariq ibn Ziyad went on to take Visigothic Hispania. "
            "By 720 the wazirs were fighting a magical war in Africa against "
            "their own rebellious jinn, whom Berber magic had goaded, and were "
            "driven back east. Umayyad governors enforced Arab rule by "
            "discrimination and slavery; in 739 the Berbers rose, united under "
            "Kharijite Islam, and with a revolt in Egypt and the caliph's death "
            "the Umayyad dynasty fell.",
            "Most of the north now belongs to the Almohad confederation. Africa "
            "is not a land of feudal states with fixed borders: each village "
            "belongs to a tribe, and tribal leaders form confederations that "
            "raise or uphold a dynasty. Monstrous races such as the headless "
            "blemmyae, dog-faced cynocephali and child-sized tripithami mostly "
            "keep apart from people, save in the great cities, but meeting them "
            "is not rare. The Latin Church has almost no presence: no abbeys, "
            "most Christians in Tunis and a very small enclave at Kairouan, "
            "while mosques are everywhere and the call to prayer marks how far "
            "a Divine aura runs. The Genoese guard a busy trade with ports on "
            "both sides of the Pillars of Hercules. Sicily's west is still held "
            "by a Muslim warlord in 1220, and if history holds Frederick II "
            "begins his campaigns against him in 1221.",
        ),
        secrets=paragraphs(
            "Why no covenants (pp. 8-11). Any of these may be true in a saga: "
            "the pact of 925, which questionable covenants may have broken; "
            "the early Order's heart being the Black Forest and not Rome, so "
            "young magi found sites nearer home; Muslim Sicily and Castille "
            "having once stood between the core Tribunals and the Maghreb; "
            "the desert uprisings of uncompromising nomad Muslims, unbribable "
            "and seemingly Divinely protected, who wreck irrigation and ruin "
            "agrarian lands. The book details no failed covenants, but a "
            "troupe may add them.",
            "What Africa offers magi: rival-free vis and resources, troubled "
            "only by Moorish or Berber settlements and local sorcerers; no "
            "vote, no Tribunal approval, no Peripheral Code on vis sites, and "
            "little fear of a charge of mundane interference, though acts that "
            "spill over the Mediterranean can still bring charges in Europe. "
            "Against that: isolation from news and help, native distrust of "
            "foreigners, and no safe assumption that magic is superior, since "
            "a campaign of conquest may unite sahirs, murabitin, the Tuareg "
            "and the Wind Spirits. Weak Divine reach and thin population make "
            "Magic sites easy to find, and nothing stops magi evicting a "
            "weaker sorcerer, genius loci or faerie. Muslim magi avoid the "
            "strife of the Iberian or Levant Tribunals. Exiles from the Order "
            "may hide here, near enough to keep ties that may also betray them.",
            "Logistics (pp. 11-12): a magus must belong to one Tribunal, and "
            "one may refuse an African covenant, or several may fight to claim "
            "it; Houses Mercere and Guernicus may object to the journeys, and "
            "a covenant may need an enchantment for redcaps or even a Mercere "
            "Portal. Hermetic settlement is left undefined, and later books "
            "assume none. Options for any city: a Mercere trading house with "
            "wharf and warehouse, keeping magic quiet; Jerbiton scholars at the "
            "madrasas, a loose network anxious about coming civil war; "
            "Criamon's small Sufi membership, welcoming to those learning "
            "Enigmatic Wisdom; or Tremere spies, African-looking magi raised "
            "from Gifted children Mercere gathered at the Primus's request a "
            "few decades ago.",
            "Languages (pp. 18-19). Living: Arabic (Andalusi, Classical, Derija; "
            "Derija is the common speech, Classical the tongue of scholarship "
            "and the Qur'an, and reading the Qur'an needs Artes Liberales 1 and "
            "Arabic (Classical) 3; dhimmis from Iberia often speak Andalusi); "
            "Tamazight (Tarifit in the Maghreb and Rif, Kabyle, Tashelhiyt in "
            "the central highlands, Zenaga in south-west Mauritania, Tamahak "
            "among the Tuareg, Siwi at Siwah alone); Lingua Franca or Sabir "
            "(Western, Eastern), the commonest tongue of visiting Europeans; "
            "Punic (Khalidan). Dead: East German (Gothic, Vandalic), Greek "
            "(Classical), Latin (Classical), Libyan, Punic (Carthaginian, "
            "Phoenician). Scholars and travellers often lose their dialect for "
            "a standard specialty. Northern Arabic and Tamazight use Arabic "
            "script, the Tuareg and southern Berbers Tifinagh, Khalidan a "
            "Phoenician variant, the Germans Gothic. Penalties to both speakers: "
            "dialects of one language -1; northern Tamazight with Tamahak -2; "
            "any Tamazight with Punic (Khalidan) -3; Punic with Libyan -2. "
            "Others are mutually unintelligible. Almoravid and Almohad warriors "
            "and clerics often have only Arabic (Classical) 3.",
            "Pronunciation and Tamazight plurals are on p. 19; Arabic "
            "pronunciation is in Realms of Power: The Divine p. 107. Art & "
            "Academe p. 28 discusses the shape of the world.",
        ),
    )
    regions = (
        (
            "Mauritania (Al-Maghrib al-Aqsa)",
            "The Farthest West, on the Atlantic: mostly coastal desert whose "
            "plants drink the fogs off the cool sea, which lets people live "
            "south of the Tropic of Cancer. The Adrar highlands wall it from "
            "the furnace of the inland desert.",
        ),
        (
            "Numidia (Al-Maghrib al-Awsat)",
            "The Middle West, the most thickly peopled land in Africa after "
            "Egypt, with a Mediterranean coast sheltered by the Atlas, which "
            "is not one range but several: the Tell Atlas by the sea, and the "
            "Anti-Atlas, High Atlas and Saharan Atlas to the south, with crops "
            "and pasture between.",
        ),
        (
            "Cyrenaica and Tripolitania (Al-Maghrib al-Adna)",
            "The Nearest West: Cyrenaica next to Egypt, and Tripolitania round "
            "the Gulf of Sidra north of the Libyan Desert. Few live here, "
            "mostly the nomad Banu Sulaym.",
        ),
    )
    numidia = None
    for name, summary in regions:
        region = b.place(name, inside=africa, summary=summary)
        if "Numidia" in name:
            numidia = region
    for name, summary in (
        (
            "Er Rif",
            "The mountains between the Middle Atlas and the Straits of "
            "Gibraltar, held by the Marinids.",
        ),
        ("The Tell Plateau", "The high plateau south of the Tell Atlas."),
        (
            "Ifriqiyeh",
            "The old Roman Province of Africa, among the Aures Mountains, "
            "ruled for the Almohads by Hafsid governors.",
        ),
        (
            "Badja",
            "A town near Tunis with a stone engraving of the seven Dii Mauri "
            "on a bench above the Latin words salutares, immortales and "
            "augusti: Bonchar at the centre with his staff, their lord; on his "
            "right Vihina of home and childbirth with an infant at her feet, "
            "then Macurgum of health with scroll and serpent staff; on his left "
            "Varsissima of secrets, then Matilam presiding over a boar's "
            "sacrifice; and at the ends Macurtan of the waters with a bucket "
            "and Iunam of the moon.",
        ),
    ):
        b.place(name, inside=numidia, summary=summary)
    desert = b.place(
        "The Great Desert (As-Sahra al-Kubra)",
        inside=africa,
        summary=paragraphs(
            "Gaetula on the maps, and most of the continent. Westerners think "
            "it one sheet of sand, but that is true only of the ergs, or sand "
            "seas, which nobody lives in; most of it is the stony reg and the "
            "rock plateaus called hamada, with salt flats in the lee of "
            "mountains.",
            "At its centre stand the Ahaggar (idurar n Ahaggar), with the "
            "eroded 'rock forests' of the Tassili n Ajjer on their north-east "
            "and the Adagh and the triangular Air massif to the south. Tuat, "
            "south-east of the Tademait, is a string of small oases along a dry "
            "wadi, an important road. Tanezrouft, the Land of Thirst, west of "
            "the Ahaggar and south of Tuat, has no oasis at all: dark sandstone "
            "hills and canyons of 250 to 500 paces between dune fields, the "
            "rock scoured into perfect concentric circles and ellipses.",
        ),
    )
    for name, summary in (
        ("The Grand Erg", "The sand sea south of the Atlas Mountains."),
        (
            "Erg Chech and El Djouf",
            "The vast sand seas east of Mauritania.",
        ),
        (
            "The Tademait Plateau",
            "A hamada south of the Grand Erg, flat beyond compare and truly "
            "empty: no hills, villages or beasts, not even pebbles, only dust "
            "and the odd bush that eyes are glad to see. It ends at mountains "
            "to the south-west and Tuat to the south-east. It is known as a "
            "haunt of jnun, and its emptiness has driven men mad.",
        ),
        (
            "The Libyan Desert",
            "South and east of Cyrenaica, largely filled by the Great Sand "
            "Sea, with the Ubari and Murzuq ergs at its south-west.",
        ),
        (
            "Al-Haruj al-Aswad",
            "A plateau of black rock rising from the sand of the Murzuq Desert, "
            "crowned with volcanic craters.",
        ),
        (
            "The Tibesti Mountains",
            "The highest mountains of the desert, beyond the Great Sand Sea on "
            "the border of the torrid zone; Emi Koussi tops eleven thousand "
            "feet. In the local dialect the name means the Mountains of Hunger.",
        ),
    ):
        b.place(name, inside=desert, summary=summary)
    b.place(
        "The Torrid Zone",
        inside=africa,
        summary=paragraphs(
            "The belt about the equator where the sun comes closest and burns "
            "the land, and at whose heart the Great Ocean must lie, known by "
            "logic and not by sight. Christian and Arab scholars agree it is "
            "impassable and lifeless and that Africa ends north of it; how far "
            "north it reaches is argued, though most say no further than the "
            "Tropic of Cancer. Some speak of a 'ring of fire', but it mostly "
            "comes on as a worsening of the desert, with no known water at "
            "all. Those who have returned from its fringes tell of fabulous "
            "lands. Logic also requires a twin habitable zone beyond the "
            "equator, for ever out of reach, which some think the place of "
            "the Magic Realm.",
            "Beyond the desert the maps set Aethiopia on the equatorial ocean: "
            "Aethiopia Orientalis south of Egypt and Aethiopia Occidentalis "
            "south of Mauritania. Most of the black-skinned people known to "
            "the north are Ethiopians of the zone's fringes.",
        ),
        secrets=paragraphs(
            "Deprivation rolls for thirst come every two hours (see Hazards of "
            "the Great Desert), and sun on bare skin does +5 non-combat damage "
            "as often. Patches that give life may lie in Magic or Faerie auras "
            "or regiones joined to the desert's regio network; desert dwellers "
            "are likely to know them. A storyguide may keep the south beyond "
            "the desert habitable, or in regiones.",
            "If the troupe wants it impassable, it can be a Divine edict: the "
            "heat, coming from the superlunar sun, lies past Hermetic magic, "
            "grows until it beats any defence, foils magic spectacularly and "
            "may be patrolled by angels. Research on the Limit of the Lunar "
            "Sphere may profit here. Ideas for what lies within: a city of "
            "refugees from Carthage under a college of priestesses; Prester "
            "John's peaceful empire; grasslands and jungles whose nomads herd "
            "for sphinxes; a river of gems and vis through black ravines that "
            "trap the ghosts of those who die there; the true home of the "
            "Sudanese in Aethiopia Occidentalis. Whether Aethiopia is the torrid "
            "zone is for the saga.",
        ),
    )
    return africa


# -- the rulers --


def _rulers(b: Builder, africa: Neighbour) -> tuple[Neighbour, Neighbour]:
    caliph = b.lord(
        "Almohad Caliph",
        title="",
        wealth="Wealthy",
        seat="Marrakesh",
        ruler="Yusuf al-Mustansir",
        place=africa,
        summary=paragraphs(
            "Yusuf al-Mustansir, also called Yusef II, Caliph of Morocco, was "
            "ten when his father died in 1213 and is seventeen now; the regency "
            "council set up then still largely rules for him. The Almohads, "
            "al-Muwahhidun or 'the monotheists', are Berbers of Masmuda "
            "leadership and hold the confederation to which most of the north "
            "belongs, in Africa and al-Andalus.",
            "Ibn Tumart of the Masmuda studied in Granada and Baghdad and "
            "taught the strict unity of God, denying that God's attributes "
            "exist apart from Him. He came home in 1117, agitated against the "
            "Almoravids, built a fortress at Tinmel in the High Atlas and "
            "raided the Marrakesh road to Sijilmasa for eight years. His first "
            "true battle, the siege of Marrakesh in 1130, was a disaster, and "
            "he died months later, which only heartened his followers. Abd "
            "al-Mu'min drove out the Almoravids, reached Egypt's border by "
            "1147, and took al-Andalus between 1147 and 1173.",
            "Early in 1220 he took the advice of his sahir vizier and beheaded "
            "most of the Franciscan friars sent to preach on this coast. The "
            "Marinids beat his armies in the Rif in 1217 and have not been "
            "dislodged, and he has fortified his Iberian cities against them. "
            "If history holds, the last synagogue in Marrakesh closes in 1224.",
        ),
    )
    b.magus(
        "Abu Sa'id Uthman ibn Jam'i",
        covenant=None,
        house="",
        age=None,
        type="companion",
        summary="The caliph's sahir vizier, on whose advice the friars were "
        "beheaded in the first weeks of 1220. Princess Sancha of Alenquer "
        "hints at a great reward for proof of his death.",
    )
    b.magus(
        "Princess Sancha of Alenquer",
        covenant=None,
        house="",
        age=None,
        type="companion",
        summary="A Portuguese princess who befriended St. Francis's friars on "
        "their way to Morocco and saw their deaths in a vision at prayer. She "
        "offers a reward for their remains.",
    )
    sultan = al_kamil(b)
    b.lord(
        "Ayyubid Rulers of Cyrenaica",
        title="",
        wealth="Average",
        answers_to=sultan,
        summary="The Kurdish rulers the Ayyubid sultanate, founded by Saladin, "
        "sets over the cities of Cyrenaica, upheld by Bedouin and Turkish "
        "troops. The sultanate holds Egypt, Cyrenaica, Tripolitania and much "
        "of Arabia, and governs this region from Tripoli.",
    )
    return caliph, sultan


# -- the dead dynasties --


def _history(b: Builder) -> None:
    for name, summary in (
        (
            "The Rustamids",
            "A Kharijite dynasty of Tahart, risen from the Banu Ifran under "
            "the Kahina. Abdul-Rustam ibn Rustam, of Persian descent, set up a "
            "theocracy of elected imams over Ibadite Berber tribes, honest, "
            "pious, friends of astronomy, mathematics and theology. They kept "
            "no reliable army, and the Fatimids' champion Abu 'Abdulla crushed "
            "them.",
        ),
        (
            "The Banu Midrar",
            "The Kharijite rulers of Sijilmasa, a cosmopolitan city of Sanhaja, "
            "Jews, Andalusians, Berbers and Arabs, with coal-black men, "
            "dog-heads and other wonders. Tolerant and peaceable to all save "
            "the Idrisids to the north, they fell to Abu 'Abdulla.",
        ),
        (
            "The Idrisids",
            "The Sunni Arab dynasty of Fes, which had fought beside the Shi'ites "
            "against the Abbasids. Having little Berber support, they made the "
            "north-west mostly Arab, to this day. They never conquered the "
            "Barghawata.",
        ),
        (
            "The Barghawata Confederation",
            "An Atlantic Berber confederation whose early ruler claimed to be a "
            "prophet, wrote a holy book in Berber and converted his people to "
            "his own faith. The Almoravids stamped out the heresy.",
        ),
        (
            "The Aghlabids",
            "The caliph's embassy at Qayrawan under Ibrahim ibn al-Aghlab, "
            "which came to rule as a dynasty. Abu 'Abdulla beat them again and "
            "again from 903 to 909.",
        ),
        (
            "The Fatimids",
            "Abu 'Abdulla, a Yemeni Isma'ili missionary, won over the Kutuma "
            "and conquered Kairouan, Ifriqiyeh, Tahart and Sijilmasa. In 909 "
            "the Isma'ili leader 'Ubaydalla Sa'id came and took the dynasty "
            "from him, and within two years had him and his family murdered. "
            "They persuaded the Kutuma settuten to turn on Abbasid sahirs, whom "
            "they drove from Africa by disrupting magic, banishing spirits and "
            "stirring rebellion among bound jinn: Africa is still hostile to "
            "the Order of Suleiman. They took Egypt by 969, founded Cairo and "
            "left the Maghreb. Caliph al-Mustansir then loosed the Bani Hilal "
            "on the rebellious Zirids.",
        ),
        (
            "The Zirids",
            "The family of Buluggin ibn Ziri, a Sanhaja Berber made governor of "
            "the Maghreb by the Fatimids, whose rule became a dynasty. When "
            "they rebelled, the Bani Hilal overran them and the emir fell back "
            "from Qayrawan to Mahdia on the coast.",
        ),
        (
            "The Hammadids",
            "A Sanhaja dynasty, badly weakened by the coming of the Banu Hilal.",
        ),
        (
            "The Almoravids",
            "Al-Murabitun, from the zealot Abdallah ibn Yasin of the Gazzula, "
            "whose orthodoxy failed among his own people. Yahya ibn Umar of the "
            "Lamtuna invited him to preach, wanting the Sanhaja reunited, and "
            "together from the early 1050s they took the Maghreb: Sijilmasa in "
            "1054, and by 1062 Yusuf ibn Tashfin had founded Marrakesh and "
            "spread over the Atlas. Invited to al-Andalus in 1086 against the "
            "king of Leon and Castile, he saw the princes' disunity, returned, "
            "and by 1094 held all Muslim Iberia but Zaragoza. His son Ali ibn "
            "Yusuf, raised in luxury, lost ground to Christians and Almohads; "
            "four years after Ali's death in 1143 Marrakesh fell and the "
            "dynasty ended.",
        ),
    ):
        b.faction(name, summary=summary, faction="Dynasty")


# -- Berbers and Arabs --


def _peoples(b: Builder, caliph: Neighbour) -> None:
    b.faction(
        "The Berbers (Imazighen)",
        place=None,
        summary=paragraphs(
            "The first people of Africa, who call themselves Imazighen (one "
            "Amazigh), 'free men'; the Romans said Mazices or Mauri, whence "
            "Europe's 'Moor' for Berber and Arab alike. Phoenicians, Romans, "
            "Visigoths, Greeks and Arabs have all come, and Berbers remain the "
            "dominant culture, a Berber dynasty ruling most of the Maghreb. "
            "They are a Mediterranean folk with olive skin weathered by desert "
            "wind, dark-haired, sometimes auburn or blond. Men wear the "
            "hooded wool tajellabiyt, with an asilham cloak at night or in the "
            "mountains. Women wear the white haik and tahruyt headscarf, drawn "
            "across the face before strange men so that only the right eye "
            "shows, with an indigo set embroidered for ceremony.",
            "Women's tattoos are thought to add beauty, and pass from mother to "
            "daughter, allowed by local custom despite the Hadith. Green siyala "
            "mark the face, neck and chest: a line from lip to chin at marriage "
            "that grows crosses and palm fronds for children and family events, "
            "and dotted 'ant-tracks' round the eyes. Ahadjam on the body, worn "
            "by both sexes, ward infertility on the back, wake the senses on "
            "the breast, turn the evil eye at wrist and ankle and keep off jnun "
            "at hand and foot. A neggafa paints festive tawzayt in henna, "
            "saffron or black harquus, and some ngagef put power in them.",
            "Their society is in name leaderless, joined by resistance to "
            "central rule. Houses are of equal size, milk is shameful to buy "
            "and surplus is given and not sold. Men have everything outdoors: "
            "herding sheep and goats, metalwork, butchery, market and the grain "
            "store, where no woman should be seen. The wife or mother of the "
            "eldest male rules the house, and women hold weaving, dyeing, "
            "pottery, baskets, food and even carpentry, and teach each other "
            "letters at the loom, so a wife is likelier literate than her "
            "husband. Monogamy is the norm. They are freer with women than "
            "Arabs are, yet the fountain is as forbidden to men as the grain "
            "store to women.",
            "A village or thaddart climbs a hilltop in steps to the minaret, or "
            "is dug into caves in the Atlas; old families live on top, new "
            "arrivals below, from 50 houses to 1500 near trade roads. In towns "
            "men hold the vaulted streets and women the roofs above, crossing "
            "gaps by leap, ladder and bridge. Houses of two or three storeys "
            "keep beasts below, windows only high up and a roof terrace; three "
            "or four share a courtyard, and these make a ward or thakherroubt "
            "with its own cemetery, threshing room and grain store. Outsiders "
            "live at the edge. Each ward's tajmait, chaired by an elected amin, "
            "judges public matters and fines men who fail to attend; its worst "
            "sentence is that nobody speak to the offender. The ward's most "
            "learned women form the tala at the fountain: they tend the dead, "
            "act on anonymous denunciations over private conduct, and enforce "
            "penance through their sons and husbands.",
            "Two to eight or more villages make a tribe or 'arsh. Trees and "
            "irrigated plots are private, rain-fed plough land the village's, "
            "pasture the tribe's, which also terraces land and digs channels "
            "together. Members trade among themselves; Berbers hold no markets, "
            "though men go to those outside and peddlers are borne. Tribes may "
            "join a thaqbilt, and the three such great confederations are the "
            "Zenata, Masmuda and Sanhaja.",
            "Coastal Arabs think them superstitious. Most are in name Ibadi "
            "Muslims, little given to persecuting anyone, and much pagan custom "
            "lingers, above all inland; Christians survive on the coast of the "
            "Tell. Villages hold one faith or another, the settuten, pagan "
            "nearly always, being tolerated for their service up to a point. "
            "Pagans honour Tafuyt the harsh sun, Ayyur the moon and sacrifices, "
            "bull-headed Gurzil of war, Anzar of rain, Dunnit of fertility and "
            "death (Tanit at Carthage, Neith in Egypt), and local gods such as "
            "Baccax of caves and Lilleu of a river. Their dead are gods too: "
            "they swear with a hand on a tomb and sleep in it for dreams. "
            "Householders lead the village's rites and chief women the "
            "family's. Remote villages still leave small gifts in cave shrines "
            "for the Dii Mauri, more to placate them than to worship.",
            "In the beginning a man and a woman lived in the dark Netherworld, "
            "and she was the Yemma-t n Dunnit, the First Mother of the World, a "
            "great witch whose hundred children climbed to the light. She made "
            "sun, moon, stars, beasts and plants, and having no more to make, "
            "made destruction: eclipses, discord, death, gossip and lies. The "
            "porcupine bears the splinters of her spindle and the tortoise was "
            "a calf crushed in her millstones. Ayyur the moon is her son and "
            "Tafuyt the sun her daughter. Against her stands Awettuf the "
            "ant, husband of Tafuyt, who taught people to use what she made, to "
            "grow grain and bake, to sacrifice, and got the wild bulls to serve.",
            "The Kahina (al-Kahinat, 'the seeress'), born Dihya, took up the "
            "resistance in the 680s, drove the Arabs from Ifriqiyeh and kept "
            "them besieged in Cyrenaica for five years while she wasted the "
            "land, losing the oasis folk's love. Her adopted son betrayed her, "
            "and she died sword in hand in 703, aged 127, having foreseen "
            "enough to save her line: her sons turned Muslim and led the Berber "
            "army into Iberia. An idol of Gurzil from Jugurtha's day went into "
            "every battle with her, and some think her a settut.",
        ),
        secrets=paragraphs(
            "Most Berber gods belong to the Faerie Realm. Whether the Dii Mauri "
            "still hear, or lie smothered by the Divine, is left open. The "
            "settuten, dedicated to the god of sacrifices, are the nearest "
            "thing to a priesthood (ch. 4). Traditional ahadjam forms are in "
            "the Tattoo Magicians section, pp. 93-95.",
            "Names (p. 21): most Berbers follow the Muslim pattern with Berber "
            "isms; traditional men are 'name ag name', women go by one name or "
            "a Tamazight laqab. Lists of men's and women's isms are on p. 21.",
        ),
        decides="Each ward's tajmait, under its amin; confederations meet in need",
        rules="Kharijism (p. 29): the earliest sect, who left Ali over "
        "arbitration, hold that major sin ends one's Islam, that any "
        "irreproachable believer may be caliph and any bad one deposed, that "
        "jihad is a sixth pillar, and that all believers are equal. It is "
        "extinct here but lives on in the gentler Ibadis, who reject violent "
        "rebellion: their Mashayekh elect and may remove an absolute Imam, and "
        "the 'Azzaba lead religious orders. Ibadism opposes Sufism but accepts "
        "the baraka of great leaders.",
    )
    b.place(
        "The Netherworld",
        realm="Faerie",
        summary=paragraphs(
            "The invisible shadow world under ours, its mirror: mountains are "
            "pits, ravines are cliffs and rivers run across the sky. Black "
            "sheep eat coal and black goats give black milk. When it is night "
            "above it is day below, for Tafuyt retreats there, and a moonless "
            "sky means Ayyur is visiting his mother. It holds the dead, hideous "
            "giants such as the teryelen ogresses, and dwarfs who swarm like "
            "their ant kin.",
            "Pagans say people were born there, climbed out by a hole and go "
            "back at death, not quite cut off. Tombs, wells, caves and iron "
            "gates built by jnun join the two worlds, and snakes carry "
            "messages, so one treats them with respect lest they speak ill of "
            "one to one's ancestors.",
        ),
        secrets="It is part of the Faerie Realm, and parts of it lie in Faerie "
        "regiones, which are easier to visit.",
    )
    for name, summary, ruler in (
        (
            "The Masmuda",
            "Berber confederation about Fes and Rabat, the western Atlas and "
            "Sijilmasa. Ibn Tumart was one, and they dominate the Almohad "
            "hierarchy.",
            "",
        ),
        (
            "The Sanhaja",
            "Berber confederation in two parts: the east on the Tademait and "
            "Ahaggar, and the west in Mauritania, from the Anti-Atlas down to "
            "the edge of the torrid zone. The Almoravids, Zirids and Hammadids "
            "grew from them. Allies of the Fatimids of old, and rivals of the "
            "Zenata.",
            "",
        ),
        (
            "The Zenata",
            "Berber confederation through the Tell and northern Numidia, once "
            "allied to the Caliphate of Cordoba, and rivals of the Sanhaja.",
            "",
        ),
        (
            "The Marinids",
            "The Ayt Mrin (Arabic Banu Marin), a Zenata dynasty at war with "
            "the Almohads from the start. In 1217 they won a decisive victory "
            "in the Rif, though it cost them their leader Abd al-Haqq. His son "
            "holds Er-Rif and looks to spread further, and Almohad "
            "counterattacks have failed.",
            "Uthman ibn Abd",
        ),
        (
            "The Banu Zayan",
            "The Abd al-Wadids, a Zenata tribe gathering power in Tlemcen.",
            "",
        ),
        (
            "The Hafsids",
            "A Masmuda dynasty whose governors hold Ifriqiyeh for the Almohads. "
            "If history holds, the governor of Tunisia seizes the city in 1228 "
            "and takes the title of emir (p. 134).",
            "",
        ),
    ):
        b.faction(name, summary=summary, ruler=ruler, faction="Tribe")
    for name, parent, summary in (
        ("The Barghwata", "Masmuda", "A Masmuda subtribe."),
        ("The Ghomara", "Masmuda", "A Masmuda subtribe."),
        ("The Doukkala", "Masmuda", "A Masmuda subtribe."),
        ("The Hintata", "Masmuda", "A Masmuda subtribe."),
        (
            "The Kutama",
            "Sanhaja",
            "An eastern Sanhaja tribe (also Kutuma), the Fatimids' first allies.",
        ),
        ("The Gazzula", "Sanhaja", "Western Sanhaja of the Anti-Atlas."),
        ("The Lamta", "Sanhaja", "Western Sanhaja of the Anti-Atlas."),
        ("The Massufa", "Sanhaja", "Western Sanhaja south of the Anti-Atlas."),
        (
            "The Lamtuna",
            "Sanhaja",
            "Western Sanhaja south of the Anti-Atlas, whose chief raised the "
            "Almoravids.",
        ),
        ("The Banu Warith", "Sanhaja", "Western Sanhaja south of the Anti-Atlas."),
        (
            "The Gudala",
            "Sanhaja",
            "The southernmost Sanhaja, on the edge of the torrid zone.",
        ),
    ):
        b.faction(name, summary=summary, faction="Tribe", decides=f"Of the {parent}")
    b.faction(
        "The Banu Hilal",
        faction="Tribe",
        summary=paragraphs(
            "Bedouin clans (Bani Hilal, 'children of the crescent moon'), grown "
            "in Egypt from other nomads and peasants fleeing debt into an "
            "anarchic quarter-million with 50,000 young warriors. Caliph "
            "al-Mustansir, advised to spend them on the rebel Zirids, offered "
            "them governorships, and in 1051 they moved west, some staying in "
            "Cyrenaica. Wanting grazing and not towns, leaderless and untaxable, "
            "they destroyed the town life of the interior at a stroke. The "
            "steppe and Atlas plateaus went from Tamazight farming to Arabic "
            "herding and Sunni Islam, and the north became a patchwork of "
            "Berber lords and Arab clan chiefs.",
        ),
    )
    b.faction(
        "The Maqil",
        faction="Tribe",
        summary="Yemeni allies of the Banu Hilal, whose chief subtribe, the "
        "Banu Hassan, names the Hassaniya Arabic. They settled in the far west "
        "beyond the High Atlas; some stayed in Ifriqiyeh with their sahirs, "
        "now advisers to the Banu Hilal.",
    )
    b.faction(
        "The Banu Sulaym",
        faction="Tribe",
        summary="Nomads from Nejd and Hejaz who followed the Banu Hilal west. "
        "The Banu Hebib settled in Cyrenaica; the 'Awf, Debbab and Zegb in "
        "Tripolitania and the Libyan Desert's fringes, where a century of "
        "feuding left the Debbab on top.",
    )
    b.link(
        caliph,
        "places",
        b.saga.neighbours[-1],
        "Nomads of Cyrenaica and Tripolitania, which the Ayyubids control (p. 19)",
    )


# -- how to live among them --


def _customs(b: Builder) -> None:
    b.faction(
        "The Maghrebi Arabs",
        faction="People",
        summary=paragraphs(
            "The most numerous people of the north. The first Arabs, Umayyads "
            "of the eighth century, built cities and made a town-dwelling upper "
            "class over rural Berbers on the coast; the Banu Hilal came in the "
            "eleventh, and the Almoravids put Berbers on top. Almost all are "
            "Muslim, and the further west and the poorer or more nomadic, the "
            "stricter, Marrakesh excepted. They make the five duties public: "
            "the profession of faith, prayer five times a day towards Mecca, "
            "above all Friday noon, alms, which none here think the poor don't "
            "deserve, the Ramadan fast, which spares children, the old, the "
            "pregnant, the ill and travellers, and pilgrimage. Pork, alcohol "
            "and garlic are shunned, some more strictly than others. A "
            "returning Hajj or "
            "Hajja may wear a green head covering; three pilgrimages to "
            "Kairouan count as one to Mecca for the poor.",
            "Baraka here is fortune, set before birth and not earned: the "
            "fortunate are skilful, lucky and happy, and it rubs off on those "
            "near them. Thankful for it, many turn devout. Saints' fortune "
            "stays in their relics and in the tomb, also called a murabit, "
            "which each family visits yearly or expects spirits or faeries to "
            "torment it. Outsiders and strict Muslims fear these intercessors "
            "are demons.",
            "Shame is public knowledge of a wrong, not the wrong: a sin with no "
            "witness brings none. So a Muslim here seeks to wipe out a bad "
            "name before his family repudiates him, and his neighbours accept "
            "this; the Hajj is the finest way. Speech is formal even among "
            "friends, using sidi or lella as courtesy, though in the street "
            "anybody may be jostled. One never asks outright, since refusal "
            "costs both sides face, and that covers questions; a reasonable "
            "request must be met. One says 'if God wills' of the future, and "
            "never boasts of coming luck, which invites the evil eye.",
            "The educated and wealthy must command others and do no labour: "
            "not to employ people fails the community. Men wear loose trousers, "
            "a hooded robe and a head covering that shows origin, with slippers "
            "and a jacket; women cover body, arms and hair with a pinned cloth "
            "and scarf, and Berber women are brighter and bolder. Wealth shows "
            "in colour, embroidery and jewels, and pilgrims all wear plain "
            "white.",
            "Life is lived in company to keep up one's network: washing, cooking "
            "and every task done with others, gifts unopened before the giver, "
            "and circumcisions, weddings and funerals held at home. Magi who "
            "shut themselves away must be holy, shameful or mad, and to live "
            "apart from family and unmarried seems tragic. Lunch is the big "
            "meal, of spiced shared dishes, dates, flatbread with aniseed and "
            "couscous, eaten with the right hand. In the Tell the fashion is "
            "for carousing on the diwan in bright robes and perfumed beards, "
            "with wine, date wine and slave-songstresses open to negotiation, "
            "which holy men dislike. Men meet at the Roman-style baths, and "
            "sport outside the walls: archery, fencing, racing, javelins, polo "
            "and a mallet game, hunting and falconry, the falconer cutting the "
            "prey's throat so that the law allows it to be eaten.",
            "Public life is men's. High-born women are unreachable to unrelated "
            "men, so female agents hear what men cannot at the baths and on "
            "rooftops, and may pass as boys. A married woman travels more "
            "easily. A man may have four wives if he treats them equally; "
            "kings ignore the rule, concubines do not count, and some nobles "
            "marry and divorce by the minute, which most scholars condemn. "
            "Arab tales are full of jealous wives.",
        ),
        rules=paragraphs(
            "Reputations: a negative local Reputation is removed by building a "
            "rival one until it equals the first, then spending experience "
            "against the first (ArM5 p. 167). The Haj, as a series of scenes, "
            "erodes bad Reputations and gives Haji +1; shorter pilgrimages give "
            "less, which is what 'three pilgrimages equal one' means. For its "
            "religious side use The Church pp. 15-19. Shame removal is social, "
            "not supernatural.",
            "The Gift breeds distrust, so magi easily gain shameful Reputations. "
            "Speaking of coming good fortune gives +3 to Hex rolls by those "
            "who envy the speaker. Fortune is no Virtue, and Hermetic magic "
            "cannot detect it; player characters who are wealthy, lucky or "
            "skilled have it. Maintaining the network is pushing up bond scores "
            "under the agency rules of Houses of Hermes: Societates pp. 140-144. "
            "A woman passing as a boy may take Dark Secret, or nothing if the "
            "troupe wants no stories from it.",
            "Local saints may be of any Realm: a fortunate but unholy 'saint' "
            "is a Magic spirit of place or a faerie. Observing a sect's rites "
            "or the tomb's aura may show which, though Infernal murabits mask "
            "themselves. Murabitin rules are in ch. 4.",
            "Muslim names (p. 20) join an ism, nasab (ibn, bint; Berber ag), "
            "kunya (abu, umm), laqab and nisba: Saladin's breaks down there. "
            "Lists of isms, laqabs and nisbas are on pp. 20-21.",
        ),
    )
    b.faction(
        "The Dhimmis",
        faction="People",
        summary=paragraphs(
            "Christians and Jews, suffered if they do their duties and provoke "
            "nobody, and treated worse the further west one goes. They pay a "
            "yearly tax, and may not hold office or army rank, preach, touch "
            "Muslim women, bear arms, plot, testify against Muslims, wear "
            "religious signs, pray or toll loudly or hold lavish funerals, "
            "build or repair places of worship unpermitted, eat pork or drink "
            "in public, hide any badge they must wear, ride horse or camel, or "
            "resent contempt. Jews fare particularly badly: the golden age of "
            "the last century is over here, with exceptions in some cities.",
            "Christians work chiefly as guards and merchants. Lords hire younger "
            "sons of European houses, free of local obligations, cut off from "
            "home and bound by favour and sometimes conversion or concubinage; "
            "the ban on arms is waived for them. Merchants keep enclaves in "
            "coastal cities, may not trade through the Straits, and sell much "
            "to Sicily. Barred from much else, Christians take the jobs Jews "
            "take in Europe: moneylending, with the same contempt, and "
            "smuggling drink, mostly date wine, since every Christian knows "
            "someone who knows the priest's vintner.",
        ),
        rules="The Dhimmi Minor General Flaw reflects this; those not resident "
        "may use Outsider instead.",
    )


# -- the Tuareg --


def _tuareg(b: Builder) -> Neighbour:
    tuareg = b.faction(
        "The Tuareg",
        faction="People",
        summary=paragraphs(
            "Nomads who share the Berbers' origin and know the Great Desert "
            "better than anyone, centred on the Ahaggar and Air massifs (their "
            "Atakor and Ayar). Arabs say the name means 'abandoned by god' "
            "(one Targui); they call themselves Kel Tagelmoust, People of the "
            "Veil, or Kel Tamahak, and all speak Tamahak. An Arab proverb "
            "counts them with the scorpion as the desert's only enemies.",
            "To them the word for 'he is free' also means 'he pillages'. A "
            "ghefara, or paid pardon, protects a merchant only as far as that "
            "band's land. Only camels, clothing, slaves and weapons have real "
            "worth; men show rank by layers of exotic cloth, however hot. They "
            "live on sheep's and camels' milk with foraged roots, and nobles "
            "demand mouna, or tribute, from any they think inferior, which is "
            "everyone not a noble Targui.",
            "The drum group or tewsit gathers at the amghar's ettebel; tribes "
            "(tawsheten) form a Kel under an amenoukal, respected as judge and "
            "safely ignored. Raiding bands of one or two dozen ride camels with "
            "lance and takouba, some with a settut in disguise, and the best "
            "leaders vanish through hidden regiones. Women and children are "
            "left unharmed and provisioned; slaves and goods go.",
            "The imajeghen (one amajegh) are nobles who lead raids. Below them "
            "the imghad (one amghid) fight and herd, and whole tribes such as "
            "the Kel Ulli, 'the goat people', are of this class. The ineslemen, "
            "descended from marabouts, mediate feuds. The eklan, black-skinned "
            "serfs like the Haratan of the north, farm the nobles' plots, and "
            "the true slaves are the abid. The inenden are pariah wandering "
            "craftsmen, thought to be of Jewish origin, with a magic of their "
            "own.",
            "Women go unveiled, speak their minds, may hold chief places in "
            "counsel, and pass noble rank through the mother, for 'the stomach "
            "holds the child'. A wife may have male friends visit while her "
            "husband raids, though seldom more. They are tall, elegant, finely "
            "braceleted, carelessly dressed and better schooled, handing on "
            "Tifinagh, written in any direction, and singing to the anzad and "
            "tende.",
            "Men take the tagelmoust (Arabic litham, also tamelghoust), an "
            "indigo veil of Sudanese cloth, at eighteen from an ineslemen, and "
            "by twenty-five never remove it, even to eat. Its hue marks kin, "
            "its folds rank, and small shifts mood; Arabs say it hides their "
            "ugliness. Those who have made the hajj alone go without. Indigo, "
            "known to the Romans as indicum, must come from far beyond the "
            "desert. Their dress, cross-marked gazelle shields and long swords "
            "lead some Arab writers to call them Nasara al-Sahra, Nazarenes of "
            "the Desert. Few men are lettered. In the eleventh century one "
            "inenden joined House Ex Miscellanea, his line later lost in a "
            "small Muslim lineage of House Verditius, and one Suleimani sahir "
            "claims part-Tuareg blood.",
        ),
        rules=paragraphs(
            "Rank: amajegh as Knight or Emir with a hunting and travel focus, "
            "bound by a code like Dutybound; amghar as Landed Noble or Muslim "
            "Muqta'; amenoukal as Great Noble (Lords of Men p. 31), the Kel "
            "Ahaggar's equal to a duke. Common noble traits: Fury, Obsession "
            "(appearance), Overconfident, Oversensitive, Piercing Gaze, Proud, "
            "Self-Confident, Social Handicap, Strong-Willed, Wrathful. Ineslemen "
            "is a Minor Social Status Virtue (p. 34) with free Noncombatant, and "
            "inenden have Outcast. Ineslemen lack Dream Interpretation and "
            "Create Vis, may take Purity, Adjuration or Wonders, and may hide "
            "other Realms behind false baraka.",
            "The veil (p. 31) carries a hedge enchantment: ReAu 25, Duration "
            "Sun, 2 uses a day, against sandstorms, and once a day a Ward "
            "against Spirits of the Desert, Penetration 5 to 20 by rank. "
            "Wearers take Vow (constantly wear litham veil); hajis exchange it "
            "for Pious, and magicians who drop the veil for Judged Unfairly. "
            "It gives at least 2 Warping Points a year: from the eighth year "
            "Short Attention Span or Poor Concentration (Realms of Power: Magic "
            "p. 50), Warping 3 at forty and 5 at fifty, faster in strong "
            "auras. Warping 2 Short Attention Span or Poor Concentration; 3 "
            "Disfigured (deep indigo skin); 5 a Minor Supernatural Virtue "
            "(Desert Regio Network, Dowsing (water), Lesser Immunity: Thirst, "
            "Second Sight or Wilderness Sense); 6 Wanderlust; 7 Magical Air; 8 "
            "Blatant Magical Air. Most blame settut curses and buy stronger "
            "veils and amulets, which worsens it. Male asseher, imhergi, "
            "ineslemen and ineden avoid these effects but Warp faster.",
            "Tuareg magic is mostly women's; settuten are rarer here than among "
            "other Berbers. See ch. 4.",
        ),
        secrets="Elder men, driven apart by Warping, wander into the deep "
        "desert, where some bargain with the Hunger for release and become "
        "Spirit Votaries with Servant of the Desert, or Dessicated Men, undead "
        "Magic Humans with Might.",
    )
    for name, summary in (
        ("Kel Ajjer", "Near the oasis of Ghat and the Tassili n Ajjer plateau."),
        (
            "Kel Ahaggar",
            "The overlord confederation of the Ahaggar, whose amenoukal has a "
            "duke's power, though at the edges of Tuareg lands it is largely "
            "nominal.",
        ),
        ("Kel Ayr", "Masters of the Air massif."),
        ("Kel Owey", "Roam the south-eastern mountains and the Fezzan road."),
        ("Kel Ifoghas", "Settled round the Adrar Ifoghas massif."),
        ("Kel Ataram", "The western Iwellemmeden confederation, far south."),
        ("Kel Denneg", "The eastern Iwellemmeden confederation, far south."),
        ("Kel Geres", "A confederation of the far south."),
        ("Kel Ulli", "The goat people, a tribe of the imghad caste."),
    ):
        b.faction(
            name,
            summary=summary,
            faction="Tribe",
            secrets="Whether the far southern tribes are humans, Magic-kin, "
            "Magic Humans or faeries playing raiders is uncertain."
            if name in ("Kel Ataram", "Kel Denneg", "Kel Geres")
            else "",
        )
    return tuareg


# -- the Banu Khalida --


def _banu_khalida(b: Builder) -> Neighbour:
    b.faction(
        "The Banu Khalida",
        faction="People",
        summary=paragraphs(
            "The people of the Twelve Cities, on twelve oases in the far south "
            "of Mauritania, deeper into the torrid zone than anyone, with "
            "gold beyond counting, well-watered fields and mild air in the "
            "midst of the blast. These are the sinister Moors of the Song of "
            "Roland. They claim Khalid ibn Yazid, adopted son of the Kahina, "
            "an Arab who gave up Islam to live, feigned paganism, delivered his "
            "foster brothers to the invaders, and came back a Muslim leading "
            "Berbers into Iberia. His sons fled Roncevaux alive, held land as "
            "viceroys in al-Andalus and survived among the taifa princes by "
            "keeping them at odds. The Almoravids ended that game, and the "
            "whole people went back to the bled es-Siba, 'the land of "
            "dissidence', beyond their reach.",
            "The ruling Hassane descend from Khalid. The clerical Zawiya serve "
            "and pay them; the Znaga labour, including mraguen fishermen, "
            "mallemin smiths and igawen poets, pay tribute and bear no arms. "
            "These three are the bidan, 'white', of mostly Zenata stock in the "
            "lower two. Below are the Haratan, freed slaves who fill the army "
            "and offices, and the 'Abid, slaves: every bidan household has one "
            "at least, and rich Hassane hundreds. Colour is no sure sign: "
            "recognised children of slaves are ebony-skinned bidan, and "
            "northern captives are pale slaves.",
            "Their tongue, once a secret Punic of the taifa days, now mixed with "
            "Arabic and Tamazight, is written in a Phoenician variant; the "
            "Zawiya and many Hassane also learn Arabic, and Znaga traders some "
            "Tamazight. Their piety is private, their mosques plain, their "
            "practice nearest Khariji to the scholar's eye. Their emirs fight "
            "not for land or wealth but to spend their champions abroad on "
            "trade roads and nomads.",
        ),
        secrets=paragraphs(
            "They worship the Unholy Trinity. The Zawiya and most Hassane know "
            "these are demons and believe, after five centuries, that they hold "
            "the upper hand; the Znaga and slaves mostly do not know. The upper "
            "ranks are goetic sorcerers, usually by pact, as the Gift is no "
            "commoner than in Europe. Hassane Summon and Ablate for life, "
            "healing and strength, so a duel goes to the greater demon. Zawiya "
            "Command demons to build roads and houses, and Bind Aerial Powers "
            "into stone pylons that cool the cities and bring rain. Almost "
            "yearly a demon breaks loose. Hell lets them be: with no Divine "
            "faith to reach, every one of them can fall, and the emirs play the "
            "Three against each other.",
            "Characters: Hassane, Knight or Emir, or Landed Noble or Muqta', "
            "the great ones Diabolist Mythic Companions; Zawiya, Priest or "
            "'Alim with Commanding and Binding; Znaga, any Free status; "
            "Haratan, the Freed Slave Flaw (p. 37) with Warrior or Educated; "
            "'Abid, the 'Abid Flaw. See Realms of Power: The Infernal ch. 11 "
            "and Realms of Power: The Divine pp. 114-115. Names: Abisme, "
            "Alphaien, Burdel, Canabeus, Chernubles, Corsablix, Esperveres, "
            "Eudropin, Faldrun, Gemalfin, Guarlan, Jouna, Malduit, Marcule, "
            "Priamon, Timozel.",
        ),
    )
    b.faction(
        "The Unholy Trinity",
        faction="False gods",
        realm="Infernal",
        summary="The three gods Europeans think Muslims worship, Mahound, "
        "Termagant and Apollyon, a mistake born partly of early meetings with "
        "the Banu Khalida.",
        secrets=paragraphs(
            "Demons of the Order of False Gods (Realms of Power: The Infernal "
            "p. 37) who sow hate between Christian and Muslim anywhere from "
            "Africa to the Middle East, in whatever form suits the listener, "
            "high in Hell and able to feign patience.",
            "Mahound: a parody of a prophet in green silk and gold, leering, "
            "with immense ears. It seeks apostasy, sends missionaries north "
            "and watches visitors to the Cities.",
            "Termagant: a wrinkled hag with bulging eyes, spitting venom and "
            "clawing at eyes with jagged nails. It wants blood, drives the "
            "Hassane to pointless violence, teaches contempt for slaves and "
            "seeks more of them.",
            "Apollyon: a hunchbacked, ugly blond parody of Apollo in a "
            "dripping, acid, oversized gold cloak, whose lyre jangles the "
            "senses to stillness. It is greed: it brings gold, always stolen "
            "from elsewhere, to lure merchants and sends them home corrupted.",
        ),
    )
    twelve = b.place(
        "The Twelve Cities",
        summary=paragraphs(
            "Twelve oasis cities in a stony desert, a day apart on paved roads, "
            "each of sun-baked red clay about a central plaza, with millet, "
            "dates and forage in the fields. Each has three to six extended "
            "families each of Hassane and Zawiya, a dozen of Znaga, five "
            "hundred Haratan, a quarter to a half of them soldiers, and maybe "
            "two thousand 'Abid. One Hassane family dominates, and its head is "
            "the city's absolute emir.",
            "The cities are named for the twelve peers of King Marsile.",
        ),
        secrets="A council of twelve emirs and the senior Zawiyas balance the "
        "Three. The demon-bound pylons keep the climate.",
    )
    for name in (
        "Aelroth",
        "Balaguer",
        "Chernubles",
        "Corsalis",
        "Escremiz",
        "Estorgans",
        "Estramariz",
        "Falsaron",
        "Malprimis",
        "Margariz",
        "Moraine",
        "Turgis",
    ):
        b.town(
            name,
            place=twelve,
            summary="One of the Twelve Cities of the Banu Khalida, under its emir.",
            secrets="Its emir has been corrupted by Baal-Peor."
            if name == "Malprimis"
            else "",
        )
    return twelve


# -- people with stat blocks --


def _people_with_stats(b: Builder) -> None:
    aljilani = b.magus(
        "Aljilani ag Ibrahim",
        covenant=None,
        house="",
        age=37,
        type="companion",
        summary="A Targui amajegh, a noble of the Ahaggar who leads raiders on "
        "camels, known locally as merciless, with a veil worn so long that "
        "his skin has gone indigo.",
    )
    b.stats(
        aljilani,
        {
            "characteristics": characteristics(0, 1, -1, 0, 1, 2, 1, 0),
            "size": 0,
            "apparent_age": 37,
            "decrepitude": (0, 0),
            "warping": (3, 8),
            "confidence": (2, 5),
            "virtues_flaws": [
                "Knight",
                "Inspirational",
                "Lightning Reflexes",
                "Long-Winded",
                "Self-Confident",
                "Tough",
                "Strong-Willed",
                "Proud (Major)",
                "Infamous",
                "Poor Hearing",
                ("Oversensitive (Minor)", {"detail": "shown lack of respect"}),
                ("Vow (Minor)", {"detail": "constantly wear litham veil"}),
                ("{land} Regio Network", {"land": "Desert"}),
                "Disfigured",
                "Short Attention Span",
            ],
            "abilities": [
                ("Animal Handling", 2, "camels"),
                ("Living Language: Arabic", 3, "demands"),
                ("Area Lore: Ahaggar", 2, "history"),
                ("Athletics", 2, "leap"),
                ("Awareness", 2, "ambushes"),
                ("Bargain", 3, "beg food"),
                ("Brawl", 2, "kick from horseback"),
                ("Etiquette", 2, "Tuareg"),
                ("Folk Ken", 1, "soldiers"),
                ("Great Weapon", 4, "lance"),
                ("Guile", 2, "spot lies"),
                ("Hunt", 2, "gazelle"),
                ("Intrigue", 2, "alliances"),
                ("Leadership", 2, "rallying troops"),
                ("Ride", 4, "battle"),
                ("Single Weapon", 5, "long sword & shield"),
                ("Stealth", 2, "ambushes"),
                ("Survival", 3, "Desert"),
                ("Living Language: Tamazight", 5, "Tamahak"),
            ],
            "traits": {"Arrogant": 3, "Proud": 3, "Oversensitive": 3},
            "reputations": {"Merciless raider (local)": 2},
            "notes": paragraphs(
                "Printed as a starting companion who needs 2 more Minor Virtues "
                "to balance, and may take one more if he takes another Minor "
                "Flaw. His Knight Virtue is printed as Amghar (Knight). Desert "
                "Regio Network, Disfigured (indigo skin) and Short Attention "
                "Span come from Warping (BS&S p. 33).",
                "Combat: Fist Init +0, Atk +3, Def +2, Dam +1. Kick (mounted) "
                "Init -1, Atk +7, Def +5, Dam +4. Takoba & Aghar Init +2, Atk "
                "+11, Def +10, Dam +7. Takoba & Aghar (mounted) Init +2, Atk "
                "+14, Def +13, Dam +7. Allagh (lance, mounted) Init +2, Atk "
                "+13, Def +8, Dam +6. Soak +14 (Stamina, Tough, full chain). "
                "Encumbrance 3 (9). Wounds -1 (1-5), -3 (6-10), -5 (11-15), "
                "Incapacitated (16-20), Dead (21+).",
                "Veil powers: Brave the Sandstorm, ReAu 25, Init 0, Personal, "
                "Sun, 2 uses a day, repels the breeze that carries the dust. "
                "Ward Against the Kel Asuf, ReVi 15, Init 0, Personal, Sun, 2 "
                "uses a day, Penetration +10, repels minor Faerie spirits of "
                "the deserts.",
                "Equipment: full chain, aghar (gazelle-hide heater shield), "
                "litham veil, takoba, allagh, wooden camel saddle enchanted by "
                "an inenden (+3 to Ride for a scene or three minutes), jeweled "
                "amulet enchanted by an inenden witch (Wilderness Sense 3, "
                "desert).",
            ),
        },
    )
    jurfaret = b.magus(
        "Jurfaret",
        covenant=None,
        house="",
        age=26,
        type="companion",
        summary="A young Hassane of the Banu Khalida seeking fame as a warrior: "
        "nearly seven feet tall, ebony-skinned and shaven, his face painted "
        "with red ochre for battle, in a chain shirt under a black djebellah. "
        "He cannot leave a jar, door, shutter or chest open.",
        secrets="He preys on the ghosts of those he beats, Ablating experience, "
        "Confidence, Characteristics or healing from them, fifteen victories "
        "so far, gaining Warping and Infernal Reputation, and tainting his "
        "Abilities. The remnants hang at the edge of his sight, which is why "
        "he closes every place a spirit might hide. A demon is bound in his "
        "great sword.",
    )
    b.stats(
        jurfaret,
        {
            "characteristics": characteristics(0, -2, 2, 1, 2, 2, 2, 2),
            "size": 0,
            "apparent_age": 26,
            "decrepitude": (0, 0),
            "warping": (2, 0),
            "confidence": (1, 5),
            "virtues_flaws": [
                "Knight",
                "Summoning",
                "Ablating",
                "Arcane Lore",
                "Infernal Heirloom",
                "Large",
                "Protection",
                "Overconfident (Major)",
                "Supernatural Nuisance",
                ("Compulsion (Minor)", {"detail": "to close things"}),
                "Corrupted Abilities",
                "Mentor",
                "Poor Hearing",
                "Tainted With Evil",
            ],
            "abilities": [
                ("Area Lore: Twelve Cities", 2, "worthy opponents"),
                ("Athletics", 1, "leaping"),
                ("Brawl", 4, "gauntlet"),
                ("Folk Ken", 2, "opponents"),
                ("Great Weapon", 5, "greatsword"),
                ("Guile", 3, "misdirection"),
                ("Infernal Lore", 4, "Ablating"),
                ("Leadership", 1, "Haratan"),
                ("Living Language: Punic", 5, "Khalidan"),
                ("Organization Lore: Hassane", 2, "Estorgans"),
                ("Penetration", 2, "Ablating"),
                ("Single Weapon", 4, "long sword"),
                ("Stealth", 1, "ambushes"),
                ("Summoning", 10, ""),
                ("Ablating", 9, ""),
            ],
            "traits": {"Impetuous": 3, "Cutthroat": 2, "Refined": 1},
            "reputations": {"Ruthless Warrior (Infernal)": 2},
            "notes": paragraphs(
                "Natural Characteristics before Ablating: Com 0, Sta +1, Qik 0. "
                "Corrupted Abilities comes from Warping and marks Leadership "
                "and Single Weapon (+3 for sinful uses, -3 for virtuous). "
                "Rules for Summoning and Ablating are in Realms of Power: The "
                "Infernal pp. 114-117.",
                "Combat: Greatsword Init +4, Atk +12, Def +10, Dam +11. "
                "Longsword & Round Shield Init +5, Atk +11, Def +10, Dam +8. "
                "Gauntlet Init +2, Atk +7, Def +8, Dam +4. Soak +8. Encumbrance "
                "1 (3). Wounds -1 (1-6), -3 (7-12), -5 (13-18), Incapacitated "
                "(19-24), Dead (25+); Size is printed 0, though Large and these "
                "ranges are those of Size +1.",
                "Infernal Vitality, 0 points, Init +4, Corpus: wounding with "
                "the great sword reduces his overall Wound Penalty by as much "
                "(a Medium Wound by 3), never past zero, while his opponent "
                "lives. Penetration base 0, plus his own Penetration; blood "
                "makes an easy Arcane Connection. Equivalent to a level 25 "
                "effect.",
                "Equipment: partial chain, infernal heirloom in the shape of a "
                "great sword.",
            ),
        },
    )


def _jealous_wife(b: Builder) -> None:
    b.creature(
        "The Jealous Wife",
        page="pp. 25-26",
        realm="Faerie",
        might=15,
        form="Mentem",
        size=0,
        block={
            "characteristics": characteristics(1, 1, 0, 1, 0, 0, 0, 0),
            "virtues_flaws": ["Incognizant"],
            "abilities": [("Intrigue", 5, "servants")],
            "traits": {"Jealous": 3, "Vengeful": 3},
        },
        attacks=[b.attack("Fingernails", 1, 3, 1, 0)],
        soak=0,
        fatigue_levels="OK, 0, -1, -3, -5, Unconscious",
        powers=[
            b.power(
                "Possession",
                1,
                2,
                "Mentem",
                does="For 1 or more points, if it penetrates, the victim is "
                "possessed and under her direct control. Using the host's "
                "magic costs 1 Might per magnitude; a questionable act against "
                "the host's nature needs a stress die + Might spent over the "
                "host's Personality Trait roll (see Entrancement, ArM5 p. 65, "
                "for modifiers), and both costs apply together. Under her "
                "direct control the host has her Magic Resistance and is "
                "stopped by wards against her; acting freely, the host has "
                "neither. The costs follow Realms of Power: Magic, not "
                "Hermetic magic.",
            )
        ],
        vis=[BodyVis(3, "Mentem", "in the fingernails of the possession victim")],
        equipment="Someone else's body and all her goods.",
        appearance="She has no body of her own. Faerie Sight, or Second Sight "
        "outside a body, shows a furious face floating like a mask before the "
        "victim's head.",
        notes=paragraphs(
            "This faerie possesses a woman who falls from her husband's favour "
            "when another wife has good fortune, and so cannot live in a house "
            "where wives are treated alike. She sometimes poisons and sometimes "
            "seems unable to, which may mean there are several. Choosing not "
            "to kill, she keeps raising and lowering wives in the husband's "
            "eyes, possessing each in turn. Her traits are appearances: she "
            "has lost nothing herself, and chooses women with cause and acts "
            "as she thinks would be interesting.",
            "Printed Virtues and Flaws: Focus Faerie Powers (Possession), 2 x "
            "Increased Might, Loosely Material (as a Minor Virtue, forms only "
            "by possession); Incognizant. Her Strength, Stamina, Dexterity, "
            "Quickness and Size, and her fingernail attack, are the host's. "
            "Her Pretenses are Intrigue 5 (servants), and she may use the "
            "host's Abilities. The book prints her OK to Unconscious ladder "
            "under Wound Penalties. Not suited to be a player character.",
            wound_ranges(0),
        ),
    )


# -- story seeds --


def _seeds(
    b: Builder,
    africa: Neighbour,
    tuareg: Neighbour,
    twelve: Neighbour,
    sultan: Neighbour,
) -> None:
    for name, summary, where, antagonist in (
        (
            "The Kahina's Legacy",
            "Relics of the Kahina's war, her sword, veil or jewels, may lie in "
            "the Atlas caves, hidden from the conquerors. A magus who shows "
            "them and claims her descent would meet less opposition and might "
            "unite the quarrelsome tribes. Might her secrets open older magic?",
            africa,
            "",
        ),
        (
            "Muting the Muezzin",
            "A town's call to prayer is eroding the covenant's Magic aura. An "
            "item that keeps the song inside the oasis would be a large "
            "enchantment, to be hidden inside the Divine aura. If the Divine "
            "retreats, what comes in its place? Perhaps something Infernal.",
            africa,
            "",
        ),
        (
            "Seizing the Sahir's Bounty",
            "St. Francis sent friars to this coast in 1219, and in the first "
            "weeks of 1220 the caliph beheaded most of them on the word of his "
            "vizier. Princess Sancha of Alenquer rewards the return of their "
            "remains and suggests a great reward for proof of ibn Jam'i's death.",
            africa,
            "Abu Sa'id Uthman ibn Jam'i",
        ),
        (
            "Hunting the Hunted",
            "Magi hunt a renegade to his stronghold in the Maghreb and find it "
            "a fine site, but the local tribes, genius loci and jinn all had "
            "bargains or grudges with him, and now take the magi for his heirs.",
            africa,
            "",
        ),
        (
            "Waging War",
            "The covenant's work threatens to make an Order of Atlas against "
            "the Order of Hermes. Trianoma envoys urge it to stop, Hoplites "
            "work indirectly against its resources, House Flambeau is split "
            "over a second front to the Reconquista, Castra Solis may help or "
            "hinder, and native sorcerers gather for a clash that will reshape "
            "the Maghreb.",
            africa,
            "",
        ),
        (
            "Lost Sodales",
            "The magi are sent to find what happened to an earlier covenant, "
            "funded by senior covenants for an important task. Tuareg, fouled "
            "water from Wind spirits, a pack of bouda within, or Infernal "
            "seduction? Survivors may be deep in the desert or on the streets "
            "of Marrakesh, and the trail runs from Rabat to Taghaza to Bilma "
            "to the ruins of Cyrene.",
            africa,
            "",
        ),
        (
            "The Lonely Lighthouse",
            "An elder Verditius, a Hermetic Architect, keeps his sanctum in the "
            "lighthouse of half-buried Leptis Magna. The characters' seniors "
            "bought his work with five years of theirs, clearing sand and "
            "repairing his grounds under a list of tasks and rules. How do the "
            "neighbours take them, and what enemies did the old man make?",
            africa,
            "",
        ),
        (
            "Mysterious Sources",
            "Magi of a Mystery Cult such as the Neo-Mercurians or Mithraists are "
            "chartered to find its relics and lost shrines in the Roman ruins, "
            "and must thrive to rise. A rival cult such as the Disciples of the "
            "Worm sets up nearby to plunder them.",
            africa,
            "",
        ),
        (
            "Seekers of Lost Magics",
            "Seekers come to unbury Carthage's magic for House Bonisagus, and "
            "may also find Garamantian remains or Berber traditions, the "
            "settuten's among them, fit for Hermetic Theory.",
            africa,
            "",
        ),
        (
            "The Golden Idol of Gurzil",
            "Khalid ibn Yazid stole the Kahina's idol before her last battle, "
            "and his descendants had to leave it in al-Andalus. A disreputable "
            "merchant sells its whereabouts to the characters and to a faction "
            "of the Banu Khalida. If they win the race, the Almohads may suffer.",
            africa,
            "The Banu Khalida",
        ),
        (
            "The Chameleon",
            "A lady whose husband visits prostitutes offers a jewel for a dead "
            "chameleon, whose bones in his food will, by Tunisian folk magic, "
            "turn his desire home. It is nearly invisible and its bite is "
            "venomous. What might that venom do besides?",
            africa,
            "",
        ),
        (
            "The Christians of the Desert",
            "Characters hear of the Nasara al-Sahra and seek them as Prester "
            "John's people. The Tuareg will rob and beat them unless paid in "
            "camels, slaves or clothing. Will they be stranded in the sand?",
            tuareg,
            "",
        ),
        (
            "The Deep Tuareg",
            "Elder Tuareg, cast out by Warping, go deep into the desert and "
            "bargain with the Hunger to be free of it.",
            tuareg,
            "",
        ),
        (
            "Indigo Dye",
            "Indigo is a treasure in the desert, and magi can make its colour "
            "easily: they may meddle in the dye trade from as far as Europe, or "
            "bring cloth to win Tuareg allies.",
            tuareg,
            "",
        ),
        (
            "A Lost Treasure Returns",
            "A possession the characters lost years ago turns up with a local "
            "notable, honestly bought. The chain of trades leads to the Twelve "
            "Cities, where it was stolen by demonic wealth-summoning.",
            twelve,
            "",
        ),
        (
            "Slave Revolt",
            "An Ibadi imam from the north has been quietly teaching Islam to "
            "the 'Abid of several cities. An escaped slave asks the characters "
            "to free his kinsman.",
            twelve,
            "",
        ),
        (
            "Invasion",
            "Three emirs, urged on by Termagant, plan war on the Almohads and "
            "send sorcery-enhanced spies north to find weaknesses or make them.",
            twelve,
            "Termagant",
        ),
        (
            "The Fourth Estate",
            "The emir of Malprimis serves a fourth False God, Baal-Peor, Lord "
            "of Filth (Realms of Power: The Infernal pp. 50-51). The Three, "
            "through Zawiya go-betweens, steer outsiders into exposing him.",
            twelve,
            "Baal-Peor",
        ),
        (
            "Twice-Won Gold",
            "To keep Hassane busy, Khalida sell gold to foreign merchants with "
            "Haratan guards under one scion, then send another as 'bandits' to "
            "win it back. Characters in the caravan may ruin the game.",
            twelve,
            "",
        ),
    ):
        dormant(b.threat(name, summary=summary, place=where, antagonist=antagonist))
    b.link(sultan, "places", africa, "Holds Cyrenaica and Tripolitania")
