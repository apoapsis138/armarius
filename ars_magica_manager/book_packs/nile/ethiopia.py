"""Ethiopia (LotN ch. 8) and the three potential covenant sites of the Nile
(LotN ch. 10), in paraphrase.

The region is the place "Ethiopia", with its four kingdoms, the sultanates
on its borders, and their towns, churches and rulers inside. The covenant
sites stay places: Siwa Oasis, Ikhmindi and the village south of Adulis,
each with its Boons, Hooks, resources, vis and story themes in its secrets
and its named people as characters. Siwa and Ikhmindi use a place of the
same name when an earlier part has made one. The book's stories and story
seeds are dormant threats, and a book or vis source with no covenant to
hold it is told in the record of its place or keeper."""

from __future__ import annotations

from typing import Any

from ...models import BodyVis, Character, Neighbour
from ..builder import (
    Builder,
    Secrets,
    characteristics,
    dormant,
    more_secrets,
    paragraphs,
    titled,
    vf_puissant,
    vf_ward,
)

SOURCE = "LotN"
S = Builder.stage
DIVINE = "Divine"
FATIGUE = "OK, 0, -1, -3, -5, Unconscious"
Places = dict[str, Neighbour]


def build(b: Builder) -> None:
    p: Places = {}
    _region(b, p)
    _medri_bahri(b, p)
    _axum(b, p)
    _bet_amhara(b, p)
    _roha(b, p)
    _agaw(b, p)
    _shewa(b, p)
    _southern_sultanates(b, p)
    w = _rulers(b, p)
    _people(b, p, w)
    _society(b, p)
    _creatures(b, p)
    _siwa(b, p)
    _ikhmindi(b, p)
    _adulis(b, p)
    _ethiopian_stories(b, p)
    _roha_stories(b, p)
    _succession_stories(b, p)
    _site_stories(b, p)
    _adulis_stories(b, p)


def _seed(
    b: Builder,
    name: str,
    place: Neighbour,
    summary: str,
    *,
    secrets: Secrets = "",
    antagonist: str = "",
    realm: str = "",
    moves: str = "A track",
    stages: list[dict[str, Any]] | None = None,
) -> Neighbour:
    """A story or story seed of the book, not yet begun."""
    return dormant(
        b.threat(
            name,
            place=place,
            summary=summary,
            secrets=secrets,
            antagonist=antagonist,
            realm=realm,
            moves=moves,
            stages=stages,
        )
    )


def _existing(b: Builder, name: str) -> Neighbour | None:
    """The place another part has already made under this name."""
    return next(
        (n for n in b.saga.neighbours if n.kind == "place" and n.name == name), None
    )


def _site(
    b: Builder, name: str, *, summary: str, secrets: Secrets, aura: int, within: str
) -> Neighbour:
    """A covenant site: the place an earlier part made, its text added, or a
    new place inside the region it lies in, when that exists."""
    found = _existing(b, name)
    if found is None:
        return b.place(
            name,
            summary=summary,
            secrets=secrets,
            aura=aura,
            inside=_existing(b, within),
        )
    found.summary = paragraphs(found.summary, summary)
    found.secrets = more_secrets(found.secrets, secrets)
    return found


# -- the land and its kingdoms --


def _region(b: Builder, p: Places) -> None:
    p["ethiopia"] = b.place(
        "Ethiopia",
        realm=DIVINE,
        summary=paragraphs(
            "Punt to the ancient Egyptians, who thought it the home of the gods "
            "and the Sun's resting place, then the Empire of Axum, Ethiopia in "
            "1220 is a Christian empire of smaller kingdoms under one emperor, "
            "cut off from Europe by hostile tribes and Muslim tributaries. "
            "Agaw, Bet Amhara, Medri Bahri and Shewa are its core. Dahlak holds "
            "the islands off the coast, Muslim merchants and corsairs hold the "
            "Red Sea, pagans and Blemmyae fill the north and west, and the "
            "sultans of Adal, Dewaro, Hadiya and Ifat line the south. Beyond "
            "them lie sweltering jungle and the Torrid Zone (Art & Academe p. "
            "27, BS&S pp. 13-14).",
            "The empire runs from the Semien Mountains and the Takkaze in the "
            "west to the Blemmyae hills in the north, the Ganale and Wabe "
            "Shebele rivers in the south, and the Danakil desert and the "
            "Bab-al-Mandab in the east. The cliffs and salt flats of the Great "
            "Rift Valley part highland from lowland. It is not the land of the "
            "Mythic Aithiopes, though in antiquity the two may have been one "
            "realm. Greek writers placed it beyond Nubia and gave it King "
            "Cepheus and Queen Cassiopeia, of the Perseus story.",
            "Axum grew as Rome declined, trading with Rome, Persia and southern "
            "Arabia. When Kush fell its armies crushed the Blemmyae at Meroe, "
            "and in 525 Emperor Kaleb's generals took the Jewish city-states of "
            "South Arabia. For 250 years its emperors struck gold, silver and "
            "copper coin. Islam closed the Red Sea and Constantinople to it; "
            "the sultan of Cairo charged a fee before a new abuna could be "
            "sent; Southern Arabia, Nubia, Adal, Ifat and Yemen broke away; and "
            "the last coins bear Emperor Armah's name, in 614. In 960 the "
            "Jewish queen Gudit, called Isat or 'Fire', burned the churches and "
            "left a patchwork of small hereditary fiefs. For nearly two hundred "
            "years only the Church held any wide authority.",
            "In 1137 Takla Heymanot beat Gudit's heirs and claimed Axum's "
            "inheritance for the Zagwe dynasty. Five brothers and sons ruled "
            "in order after him, Kedus Harbe from 1180, and revived the custom "
            "of shutting up young heirs on a mountain. Lalibela's reign now "
            "turns isolated fiefs into something like one state. Records are "
            "so thin that borders, rulers and great men are mostly guesswork, "
            "free for the storyguide to shape.",
            "Lord and commoner live much alike, on grain, vegetables, hunting "
            "and livestock (cattle, donkeys, goats, chickens, camels). "
            "Communities store surplus against famine and the emperor's "
            "wandering court; few merchants exist without a lord's backing. "
            "Agaw, Amhara, Tigray and Tigrinya dialects mark the only ethnic "
            "lines, forgotten at any outside threat. Lowlanders wear loose "
            "cotton, linen or silk, the bright woven shemma, shawls, sandals; "
            "highlanders wool, skin and fur, heavy vests and boots, the men "
            "trousers and long thin sticks. Men favour round flat caps and "
            "short hair, seldom a beard; women wear their hair long or in "
            "small braids. Faces mix African, Mediterranean and South Arabian "
            "features, light to dark.",
            "No one eats pork or shellfish. Wat, a thick stew of meat and "
            "vegetables, is served on injera, sour teff flatbread, in place of "
            "plates, and only the right hand touches food. People drink "
            "katikala from millet, tela beer and tej, a honey wine. Coffee is "
            "known in Agaw and Shewa, whose warriors march on balls of ground "
            "bunn in lard or butter; a few Sufi sects near Harar praise it. A "
            "minority keep several wives, whatever the Coptic Church's letters "
            "say, and answer for every child they father.",
            "Highland and Red Sea lowland are two cultures. The plateau has "
            "many climates, with dry alpine country and hard water; the Tigray-"
            "speaking lowlanders live by the sea in constant heat. They raid "
            "each other's herds and feud over land. Farmers grow teff above "
            "all, with millet, barley, carrots, lettuce and onions. Ethiopia "
            "trades north and west with Nubia, and little by sea, for Asir and "
            "Yemen wink at piracy. It sells skins, spices, elephants, ivory and "
            "pagan slaves, to Nubians and to the markets of Harar and Dahlak. "
            "Gold comes from the southwest, the west and the escarpment; salt "
            "from the Rift is valuable enough to pass as money in places.",
            "Sheer slopes, few fords and no reliable bridges make land travel "
            "slow, and landing places are too scarce for much river traffic. "
            "Horses, camels and donkeys cope; anyone who can goes by sea. "
            "Beyond the old gods Astar and Mahrem, whose shrines Christianity "
            "razed or converted, no pagan community is tolerated. Tribes beyond "
            "the Takkaze and south of Damot raid for captives; enslaved pagans "
            "live like animals, standing decrees in Agaw and Shewa let anyone "
            "kill them, and the Church does not try to convert them.",
            "Baboon troupes of five to 250 and hyena packs of four to twenty "
            "are common. Elephants and the serpents that eat them, gazelles, "
            "hippopotamuses, leopards, lions, antelope, rhinoceroses and zebras "
            "thrive; giraffes and flying foxes live in the south, painted dogs "
            "and pangolins near the Semiens. Traders take hides and live "
            "beasts.",
            "The Periplus of the Erythean Sea, known in Latin and in the "
            "Classical Greek of Arrian of Nicomedia, charts this sea's ports in "
            "66 short chapters. It tells of Azania near the Torrid Zone, a "
            "kingdom far to the east, the heirs of Alexander in their "
            "fortresses, and the Pyralaoi or 'Fire-people', with Arab slaves "
            "for clerks; of strong iron, pearls as big as a fist, lakkos "
            "chromatinos, spikenard and bdellium. Copies are rare, mostly in "
            "private hands at Alexandria, Constantinople and Jerusalem.",
        ),
        secrets=[
            titled(
                "The Periplus",
                "The Periplus is a tractatus in Latin or Classical Greek on each "
                "of Area Lore: Ethiopia, Area Lore: Erythean Sea Coast, Area "
                "Lore: Red Sea Coast and Magic Lore, Quality 5 (p. 107).",
            ),
            titled(
                "Ethiopian arms",
                "Infantry bear sword, shield and an 8-foot spear, thrown about "
                "twenty-five paces; cavalry wear heavy mail, most others the "
                "equal of quilted armor; the Amharic word for 'spear' and 'war' "
                "is the same. Militias have a shield and a dagger or spear (p. "
                "110).",
            ),
            titled(
                "Storyguide Notes",
                "A Jew or Falasha is unusual but not an Outsider unless also a "
                "blacksmith (p. 110). A large polygamous family might take Close "
                "Family Ties (p. 109).",
            ),
        ],
    )
    p["red_sea_stands"] = b.place(
        "The Bleeding Trees of the Red Sea Coast",
        inside=p["ethiopia"],
        summary=(
            "Small, jealously hidden stands of frankincense and myrrh grow "
            "along Ethiopia's Red Sea coast, and their keepers cut long wounds "
            "in the thorny trunks to gather the dried resin, as in Yemen and "
            "Asir. The jaculi that nest in such trees in Arabia are not found "
            "here, so some think the trees were planted. If they were brought "
            "from Yemen or Soqotra, no one tends them now. Yemeni merchants may "
            "be spoiling them to protect their own trade."
        ),
        secrets=[
            titled(
                "Storyguide Notes",
                "The jaculi are in The Cradle and the Crescent pp. 116-118, "
                "Soqotra in Rival Magic p. 110 (p. 113).",
            ),
        ],
    )
    p["mountains_of_the_moon"] = b.place(
        "The Mountains of the Moon",
        inside=p["ethiopia"],
        status="Rumoured",
        summary=(
            "Vast, towering peaks past the southern jungles, which Herodotus "
            "gave as the Torrid Zone's border."
        ),
    )
    p["semiens"] = b.place(
        "The Semien Mountains",
        inside=p["ethiopia"],
        summary=(
            "The high range between Bet Amhara and Agaw, cut by the Blue Nile. "
            "Painted dogs and pangolins live here. Somewhere in them is the "
            "cave where Saint Yared spent his last years, still undiscovered."
        ),
    )


def _medri_bahri(b: Builder, p: Places) -> None:
    kingdom = p["medri_bahri"] = b.place(
        "Medri Bahri",
        realm=DIVINE,
        inside=p["ethiopia"],
        summary=(
            "The northern coastal kingdom, of Upper and Lower Bur along the "
            "shore, Eritrea to the north and Tigre in the middle: most of "
            "Ethiopia's lowlands, hot, humid and full of mangroves, with "
            "farmers and fishermen, rising to the plateau as far as the "
            "Takkaze. Its ruler, the bahri negus, ranks second only to the "
            "emperor. Rectangular cut-stone churches are commonest here."
        ),
    )
    p["bab"] = b.place(
        "Bab-al-Mandab",
        inside=kingdom,
        summary=(
            "The strait between Ethiopia and Yemen, held by Yemen's Muslim "
            "navies, friends of the sultan of Adal."
        ),
        secrets=[
            titled(
                "Storyguide Notes",
                "Passing the Bab-al-Mandab requires a story, as with the straits "
                "of Gibraltar (p. 114).",
            ),
        ],
    )
    p["danakil"] = b.place(
        "The Danakil Desert",
        inside=kingdom,
        summary=(
            "Scorched salt flats on the south side of the Bab-al-Mandab, "
            "dividing Medri Bahri from Bet Amhara. Small communities hack out "
            "slabs of salt, and long camel caravans carry this 'white gold' to "
            "Adulis, Debarwa and Zeila."
        ),
    )
    b.place(
        "Erta Ale",
        inside=p["danakil"],
        summary=(
            "'Smoking Mountain', an active cone of black basalt in a hollow of "
            "the Danakil, its pit holding a lake of molten rock that spits "
            "burning debris or spills over the rim. Its low bare slopes grow "
            "almost nothing. A fiery, capricious ifrit jinni lives here."
        ),
        secrets=[
            titled(
                "Storyguide Notes",
                "Erta Ale is an ideal site for the volcano magic of Hermetic "
                "Projects (p. 115).",
            ),
        ],
    )
    p["adulis_town"] = b.town(
        "Adulis",
        place=kingdom,
        summary=(
            "The old port of Axum, sacked in the eighth century when Yemen "
            "occupied the Dahlak islands to punish piracy, and never truly "
            "recovered. Once a great trading port, it sees far fewer merchants "
            "now, though caravans from Nubia and Egypt and ships of the Red Sea "
            "still end here. Bishop and governor both live here; the bishop's "
            "large Byzantine church stands in the northern quarter. It keeps a "
            "large slave market. Teachers of Amharic, Arabic, Ge'ez and Artes "
            "Liberales are easy to find."
        ),
    )
    p["debarwa"] = b.town(
        "Debarwa",
        population=6000,
        place=kingdom,
        summary=(
            "Capital of Tigre and of all Medri Bahri, on the Mereb river some "
            "twenty miles from the plateau's edge. The bahri negus lives here, "
            "grown rich on the copper, gold and iron mines of the escarpment, "
            "the coast roads and a large Saturday market, and his army is "
            "strong and well equipped. Bouda faeries roam its roads and wild "
            "forests, driving those they meet to lust and murder, so hyenas "
            "are hated here. He pays a bounty on live hyenas, hoping to catch "
            "the faeries."
        ),
        secrets=[
            titled(
                "The hyena bounty",
                "The negus's bounty on live hyenas is unlikely to work (p. 115).",
            ),
        ],
    )
    p["massawa"] = b.town(
        "Massawa",
        ruler="Sheikh Hanafi",
        place=kingdom,
        summary=(
            "A trade port on two islands and the shore, fifteen leagues "
            "northwest of Adulis, which rose after Adulis fell. Sheikh Hanafi, "
            "a Muslim sworn to the bahri negus, has built a mosque of carved "
            "white coral on the larger island, sends missionaries into "
            "Ethiopia, and brought shipwrights from Yemen and the Hijaz to grow "
            "his fleet. His captains carry Mecca-bound pilgrims free."
        ),
    )
    p["negash"] = b.town(
        "Negash",
        place=kingdom,
        summary=(
            "A modest hamlet of Christians and Muslims on the road from Axum "
            "to Zeila, some thirty leagues east southeast of Axum. It has a "
            "small stone mosque and the tomb of Emperor Armah, called here "
            "Ashama ibn Abjar al-Najashi, who sheltered the Prophet's daughter. "
            "Devout Muslims come as pilgrims, and the neighbours leave them in "
            "peace by old custom."
        ),
    )
    b.place(
        "The Tomb of Armah",
        realm=DIVINE,
        aura=4,
        inside=p["negash"],
        summary="The grave of the emperor who gave refuge to the first Muslims.",
    )
    b.church(
        "Abba Garima Monastery",
        church="Monastery",
        place=kingdom,
        summary=(
            "Built north of Adwa by Abba Garima of the Nine Saints. They say a "
            "nearby spring rose where he spat on the stones, and that its water "
            "grants long life."
        ),
    )
    b.church(
        "The Church of Kulubi",
        place=p["ethiopia"],
        summary=(
            "A pilgrimage church on the Feast of the Angel Gabriel, Tahsas 18 or "
            "December 16, when clergy baptize children born by the archangel's "
            "help, who are often named for him."
        ),
    )
    b.church(
        "Bi'isa Monastery",
        church="Monastery",
        place=kingdom,
        summary=(
            "The northernmost of the Nine Saints' houses, built by Abba Alef on "
            "the south bank of the Mareb."
        ),
    )


def _axum(b: Builder, p: Places) -> None:
    kingdom = p["bet_amhara"] = b.place(
        "Bet Amhara",
        realm=DIVINE,
        inside=p["ethiopia"],
        summary=(
            "The rich, fertile breadbasket of the empire and the old heart of "
            "Axum, running from the Semiens across the plateau into the Rift. "
            "Lesser realms make it up: Wag guarding the north against the "
            "Blemmyae, Begemder and Falasha, Lasta and the lands of Amhara. The "
            "Jamma parts it from Shewa, the Abbay from Agaw and the Takkaze "
            "from Medri Bahri. Its lords above all hold the Kebra Negast true. "
            "Round timber churches are common here."
        ),
    )
    axum = p["axum"] = b.town(
        "Axum",
        population=4000,
        place=kingdom,
        summary=paragraphs(
            "The old imperial capital, almost 4,000 strong, a religious centre "
            "where emperors are crowned, proud of its past. When he visits, "
            "the emperor leaves his tents for two stone palaces of the old "
            "days: Ta'akha Maryam, 120 by 80 meters with 50 rooms, and smaller "
            "Dungur, called Queen Makkeda's home.",
            "A low wall sets off the necropolis and its thirteen monoliths, "
            "among them the three great stelae, taller than any Egyptian "
            "obelisk. Ezana's Stone stands here, repeating one message in "
            "Ge'ez, Classical Greek and Ancient Sabaean: King Ezana's deeds and "
            "his conversion by Saint Frumentius. North of town, Gudit's Field "
            "is a pasture of old tombs and man-high stelae, near the rock-cut "
            "reservoir called Sheba's Bath. On a small hill Abba Pantelewon and "
            "Abba Liqanos's monastery, a pagan temple nearly 750 years ago, is "
            "still at work.",
        ),
        secrets=[
            titled(
                "Studying Ezana's Stone",
                "Knowing one of its languages, a reader may study Ezana's Stone "
                "for a season as a Quality 5 tractatus on one of the other two, "
                "or on Area Lore: Ethiopia (p. 116).",
            ),
            titled(
                "Ancient Sabaean elsewhere",
                "Ancient Sabaean is also found at Petra, at Yeha and in Yemen and "
                "'Asir (p. 116).",
            ),
        ],
    )
    p["maryam_tsion"] = b.church(
        "Church of Maryam Tsion",
        church="Cathedral",
        place=axum,
        summary=(
            "Built in the fifth century within a thick, lush forest, this "
            "church is said to hold the Ark of the Covenant in its sanctuary, "
            "brought here from Tana Qirqos. Pilgrims come on Axum Tsion, Hadar "
            "20 or November 18, and many go on to Roha."
        ),
        secrets=[
            titled(
                "The way to Prester John's kingdom",
                "Prester John does not rule Ethiopia, but anyone leaving the "
                "Church of Maryam Tsion at sunrise on Easter morning may enter a "
                "Faerie regio much like his lost kingdom (p. 120).",
            ),
            titled(
                "Storyguide Notes",
                "The Divine aura here depends on whether Axum truly holds the Ark "
                "(p. 116). The Ark has Faith Score 10, 10 Faith Points and Divine "
                "Might 100 for any Ethiopian, Falasha or Christian; for other "
                "Christians and all Muslims its Faith Score is 7 (RoP:D p. 44; p. "
                "112).",
            ),
        ],
    )
    b.place(
        "The Kingdom Beyond Maryam Tsion",
        realm="Faerie",
        inside=p["maryam_tsion"],
        status="Rumoured",
        known="Locally",
        summary=(
            "A pleasant, vivid land whose people look like whoever has entered "
            "it. They say a wise Christian king rules them, and that the law "
            "forbids them to name him."
        ),
        secrets=[
            titled(
                "The way into the kingdom",
                "The Kingdom Beyond Maryam Tsion is a Faerie regio entered on "
                "leaving the church at sunrise on Easter morning (p. 120).",
            ),
            titled(
                "Sleeping in the kingdom",
                "Whoever sleeps in the Kingdom Beyond Maryam Tsion wakes in the "
                "church of his baptism or in Maryam Tsion, which makes exploring "
                "it hard (p. 120).",
            ),
        ],
    )
    b.place(
        "The Hidden Palace of the Great Stelae",
        realm="Faerie",
        inside=axum,
        status="Rumoured",
        known="Locally",
        summary=(
            "The hawilti, begun in the worship of Mahrem and Astar, were carved "
            "with doors and windows as houses for dead kings, with vaults below "
            "where the living honoured them. Ezana raised the last just before "
            "his conversion and never entered it."
        ),
        secrets=[
            titled(
                "The afterlife regio",
                "Nobles and priests who knew the way once passed the false doors "
                "of the great stelae into an afterlife regio. It was submerged "
                "under the Divine aura, not destroyed, and its secret died with "
                "the priesthood.",
            ),
            titled(
                "The winter solstice",
                "On the night of the winter solstice the Divine sinks enough for "
                "Faerie to show and entry to the hidden palace is easier.",
            ),
            titled(
                "The ghosts of the old kings",
                "Inside the hidden palace is a vast palace of gold and ivory "
                "scented with myrrh, where ghosts of the old kings lounge, "
                "speaking Ge'ez and fluent Latin. They might describe the Roman "
                "trade, teach Ge'ez or reveal lost pagan and magical sites (p. "
                "107).",
            ),
        ],
    )
    b.place(
        "The Stone Lion and the Quarry",
        inside=axum,
        known="Locally",
        summary=(
            "A league west of Axum, in dry scrub by the quarries of the great "
            "stelae, a rock bears the life-size etching of a lioness in "
            "mid-stride. Legend says Gabriel threw her against it so hard that "
            "only the mark remained. The quarry's trenches look cut like meat, "
            "and three half-worked stelae lie half in the ground. Locals guard "
            "both and answer defacement with force."
        ),
        secrets=[
            titled(
                "Vis of the stone lioness",
                "An animal corpse laid at the lioness's feet on the night before "
                "the first day of spring, and kept from scavengers until dawn, "
                "yields 5 pawns of Animal vis in some part of it (p. 117).",
            ),
            titled(
                "Vis of the partial stelae",
                "Chips from the partial stelae gathered at noon on Timket hold 5 "
                "pawns of Rego and 5 of Vim (p. 117).",
            ),
        ],
    )


def _bet_amhara(b: Builder, p: Places) -> None:
    kingdom = p["bet_amhara"]
    b.place(
        "Amba Geshen",
        inside=kingdom,
        summary=(
            "A roughly cross-shaped hilltop of wild cedars and a spring pool, "
            "once an Axumite fortress and treasury, then a prison for imperial "
            "heirs from the third Zagwe emperor on. Lalibela ended that, "
            "vowing no more sons of Zagwe would wait here for an emperor's "
            "death, and raised the church of Egzyabeher Ab, 'God the Father', "
            "on the southern edge. It is a fortified treasury again, its long "
            "narrow halls housing guards and stores. A single-file path, the "
            "Macaraquer, reaches the gatehouse; cattle and timber are hauled up "
            "by rope. Goats and oxen live above, and escaped monkeys and "
            "rabbits raid the gardens until they reach the pot."
        ),
    )
    b.church(
        "Debre Damo",
        church="Monastery",
        place=kingdom,
        summary=(
            "Abuna Aragawi of the Nine Saints founded this house of about 100 "
            "monks on a mountain plateau once held by a serpent cult. Tradition "
            "and the carvings of its cut-stone church say a giant serpent "
            "carried him up the cliff in its coils, under the fiery sword of "
            "Gabriel, set him on a stone and left; its cult turned Christian. "
            "Everyone arriving kisses that stone. The way up is an 80-foot "
            "braided leather rope, with a basket for the old and infirm, and "
            "it has kept the monks safe for over 700 years. Up top are the "
            "church, curiously forestless, with a great store of illuminated "
            "manuscripts, nearly two dozen shared houses with gardens, a pen of "
            "cattle and rabbits and six stone cisterns. Kedus Harbe retired "
            "here, and heirs were once held here."
        ),
        secrets=[
            titled(
                "Storyguide Notes",
                "The whole community of Debre Damo has a Dominion aura of 3 (p. 117).",
            ),
        ],
    )
    hayq = p["hayq"] = b.place(
        "Lake Hayq",
        inside=kingdom,
        summary=(
            "A large, deep lake in southeastern Amhara, of bony catfish and "
            "hippopotamuses, with lemons and oranges on the shore and a small "
            "Muslim fishing village. Tradition says God raised it to drown a "
            "haughty young princess and her train for insulting a pregnant "
            "woman; the woman's seat and the village behind her became an "
            "island."
        ),
    )
    b.church(
        "Istifanos Monastery",
        church="Monastery",
        place=hayq,
        summary=(
            "On the western shore; emperors have long kept their letters, "
            "documents and land grants here."
        ),
    )
    b.place(
        "The Island Shrine of Lake Hayq",
        realm=DIVINE,
        aura=4,
        inside=hayq,
        summary="A small shrine on the island where the wronged woman sat.",
    )
    b.place(
        "The Empty Palace of Lake Hayq",
        aura=3,
        inside=hayq,
        summary=(
            "A large stone palace across the lake from the monastery, built by "
            "a forgotten Axumite emperor. No one lives in it or takes its "
            "stones. A melancholy Axumite princess haunts it."
        ),
    )
    b.town(
        "Yeha",
        population=200,
        place=kingdom,
        summary=(
            "A village of about two hundred, with a Falasha blacksmith, a "
            "potter and a weaver, in the lush plain of an easily defended vale "
            "held sacred even before the Nine Saints. Abba Aftse's monastery "
            "here failed."
        ),
    )
    b.place(
        "The Temple of Yeha",
        aura=3,
        inside=kingdom,
        summary=(
            "A crumbling temple on a high outcrop a third of a mile from any "
            "other building. Faded graffiti suggest a later church or "
            "monastery, before the roof fell; walls and square pillars bear "
            "Sabaean carving. A ruined shrine stands at the foot of a natural "
            "stone stair, and three rock-cut tombs sink into the slope to the "
            "south."
        ),
    )
    p["zeila"] = b.town(
        "Zeila",
        place=kingdom,
        summary=(
            "A walled port of polished white coral just beyond the "
            "Bab-al-Mandab, a rich meeting of Ethiopia, Yemen and the wider "
            "seas. Its governor keeps a strong army and shifts between the "
            "sultan of Adal and the ras of Amhara. Merchants press him toward "
            "the sultan, for easier passage through the strait and more power "
            "of their own. An imam from Harar has lately converted him to "
            "Islam. Its mosque was built by the Prophet's companions, exiles "
            "of 613."
        ),
        secrets=[
            titled(
                "Storyguide Notes", "Zeila's mosque has a Divine aura of 5 (p. 117)."
            ),
        ],
    )


def _roha(b: Builder, p: Places) -> None:
    roha = p["roha"] = b.place(
        "Roha",
        realm=DIVINE,
        aura=7,
        inside=p["bet_amhara"],
        summary=paragraphs(
            "A modest-looking village of mud-brick and red stone in dry, rocky "
            "country, the emperor's birthplace and official capital of the "
            "empire. Sunk beneath it, reached by tunnels, are its eleven "
            "churches, each cut from one stone between 1188 and 1200: a "
            "symbolic Jerusalem, for those Saladin's conquest shut out, with a "
            "channel called the River Jordan, a small stone cross at the place "
            "of Christ's baptism, and a Mount of Olives above. Angels are said "
            "to have helped build it.",
            "North of the Jordan stand Bet Denagel, Bet Golgotha Mikael, Bet "
            "Maryam, Bet Maskal and Bet Medhani Alem; south of it Bet Abba "
            "Libanos, Bet Amanuel, Bet Gabriel Raphael, Bet Lehem and Bet "
            "Qeddus Mercoreus. Bet Giorgys stands alone, joined to the rest by "
            "trenches. Bet Golgotha holds copies of Christ's tomb, Adam's tomb "
            "and the crib of the nativity.",
        ),
        secrets=[
            titled(
                "Storyguide Notes",
                "The whole complex has a Dominion aura of 7 (p. 117). A framework "
                "for pilgrimage (p. 118): a season walking the tunnels, praying "
                "at each church, fasting and defeating the trials of demons in "
                "possessed locals or of bouda faeries calling temptation from the "
                "rims completes a pilgrimage story (The Church pp. 16-19).",
            ),
        ],
    )
    p["roha_town"] = b.town(
        "The Village of Roha",
        place=roha,
        summary=(
            "Small clusters of houses around the tunnels, in the Lasta country. "
            "The Ethiopian capital in name; the emperor's true seat is his "
            "travelling camp."
        ),
    )


def _agaw(b: Builder, p: Places) -> None:
    kingdom = p["agaw"] = b.place(
        "Agaw",
        realm=DIVINE,
        inside=p["ethiopia"],
        summary=(
            "The realm of the negus of Agaw: Agaw proper on the west shore of "
            "Lake Tana up to the Semiens, Gojjam south of the lake, and Damot "
            "in the far south, beyond which the Jamma parts it from pagan "
            "tribes. Good rain, clear water and rich soil make it the province "
            "that suffers least in famine. Its warriors are famously fierce; "
            "an old emperor raised a monument to how hard it was to subdue. "
            "The Zagwe dynasty was forged in its hills, and Na'akueto La'ab of "
            "Gojjam, next in line to the empire, is its true power."
        ),
    )
    tana = p["tana"] = b.place(
        "Lake Tana",
        inside=kingdom,
        summary=(
            "Fifty-two miles long and forty wide, bigger than any lake in "
            "Mythic Europe and mostly over 40 feet deep, fed by the Gumara, the "
            "Lesser Abbay and the Reb. Sixteen of its islands are settled, "
            "seven with fishing villages and nine with monasteries of timber "
            "or Axumite stone. Dek, the largest, is ten miles across with three "
            "villages and two churches. On holy Daga, just southeast of it, "
            "the monks bar women and livestock. Solomon's ring, Menelik's, is "
            "said to be hidden on one of these isles, the place long lost."
        ),
        secrets=[
            titled(
                "Solomon's ring",
                "Solomon's ring is a relic. Where it lies is unknown (p. 112).",
            ),
            titled(
                "Storyguide Notes",
                "The ring is a relic of Faith Score 7 for Jews, Falasha and "
                "Ethiopian Christians, 5 for other Christians. It adds its Faith "
                "Score to a Solomonic practitioner's casting total (Cradle & "
                "Crescent pp. 33-37) or an Ars Notoria recitation (RoP:D p. 98), "
                "and a Gifted student may study it as a Quality 5 tractatus on "
                "Ars Notoria.",
            ),
        ],
    )
    b.place(
        "Tana Qirqos",
        realm=DIVINE,
        aura=4,
        inside=tana,
        summary=(
            "An island near the Gumara's mouth where tradition says the Ark "
            "rested before going to Axum. The ruins of a large temple stand on "
            "it."
        ),
        secrets=[
            titled(
                "The temple's proportions",
                "Anyone with Judaic Lore who studies the ruins on Tana Qirqos for "
                "a season finds they follow the proportions of Solomon's temple "
                "(p. 119).",
            ),
        ],
    )
    p["blue_nile"] = b.place(
        "The Blue Nile",
        inside=kingdom,
        summary=(
            "The River Abbay leaves Lake Tana over a fall and cuts through the "
            "Semiens, carrying the silt that feeds Egypt. There are few easy "
            "crossings and no stone bridges, and the rains cut off Agaw and "
            "Gojjam until the flood falls."
        ),
    )
    b.place(
        "Tis Abbay",
        inside=p["blue_nile"],
        summary=(
            "The 'Smoking Waters', the fall where the Blue Nile begins. Rich "
            "plants grow in its mist."
        ),
        secrets=[
            titled(
                "Vis in the mist",
                "As the flood first starts, mist caught at Tis Abbay at sunrise "
                "yields 3 pawns each of Aquam, Creo, Imaginem and Perdo (p. 117).",
            ),
            titled(
                "The flora of Tis Abbay",
                "Unharvested, the mist of Tis Abbay feeds the flora; Plants and "
                "Beasts of Virtue are common (p. 117).",
            ),
        ],
    )


def _shewa(b: Builder, p: Places) -> None:
    kingdom = p["shewa"] = b.place(
        "Shewa",
        realm=DIVINE,
        inside=p["ethiopia"],
        summary=(
            "The southern highland kingdom: Shewa proper in the north, Bale in "
            "the southeast and Fetegar in the southwest, the last two wetter "
            "and more forested thanks to the Wabe Shebile on the border. All "
            "three fight pagans to the southwest and sultanates to the south. "
            "Its negus rests on a cluster of very old towns on ridges about "
            "five leagues long, 3500 to 4000 feet above the Rift."
        ),
    )
    b.town(
        "Asbari",
        place=kingdom,
        summary=(
            "A town on a rocky spur at a high cliff's edge, often raided by "
            "pagans. Houses and workshops surround a large walled church on a "
            "small hill, which doubles as a redoubt; hundreds of rock-cut "
            "tombs cover the north slope. A straight wall two paces high and "
            "thick shuts the town off from the plateau, and a half-mile road "
            "winds from it to the gate between terraced farms."
        ),
    )
    b.place(
        "The Terraces of Asbari",
        aura=2,
        inside=kingdom,
        summary="Three terraces deep along the road to Asbari's gate, growing "
        "many sorts of plant.",
        secrets=[
            titled(
                "The terraces' plants",
                "The Terraces of Asbari grow various Plants of Virtue (p. 120).",
            ),
        ],
    )
    masal = p["masal"] = b.town(
        "Masal",
        place=kingdom,
        summary=(
            "Three neighbouring walled hilltops between Asbari and Nora, each "
            "with a church and about five hundred people, known for good "
            "pottery and razor-sharp obsidian tools and arrowheads. Near each "
            "lies a vast ancient cemetery of nameless tombs, many with Axumite "
            "decoration. A great obelisk carved with medallions of Solomon's "
            "star bears vague Ge'ez lines hinting at a royal tomb."
        ),
    )
    b.place(
        "The Caves Under the Masal Obelisk",
        aura=3,
        inside=masal,
        known="Locally",
        summary=(
            "The obelisk marks a way into caverns deep in the earth, some with "
            "signs of old habitation."
        ),
        secrets=[
            titled(
                "The wizard's tomb",
                "The Masal Obelisk marks the tomb of an Axumite Falasha wizard "
                "who helped found these towns (p. 121).",
            ),
            titled(
                "Vis in the frost",
                "Frost on the Masal Obelisk's shaded side on the first day of "
                "Passover holds 4 pawns of Rego (p. 121).",
            ),
            titled(
                "Vis in the obsidian seam",
                "In old sampling pits of an abandoned, brittle obsidian seam "
                "under the Masal Obelisk, chips gathered once a year yield 3 "
                "pawns of Terram and 3 of Ignem (p. 121).",
            ),
        ],
    )
    b.town(
        "Nora",
        population=3500,
        place=kingdom,
        summary=(
            "A dense city of walls on a rocky outcrop, about 3,500 strong, the "
            "seat of the negus of Shewa, though he is usually away hunting "
            "pagans and raiders. Elders and priests built its rising patchwork "
            "of homes, gardens and courtyards. The stone wall follows the "
            "mountain, the streets climb in stages along walls, and 30-foot "
            "round towers guard the way. Inside are ornamental tiles and packed "
            "rectangular houses. The main church, an Axumite building behind "
            "15-foot walls, has a lush forest only 10 feet deep and 20 tall. "
            "Outside, a mound of raw stone holds hundreds of carved tombs."
        ),
        secrets=[
            titled(
                "Storyguide Notes", "Nora's church has a Dominion aura of 3 (p. 120)."
            ),
        ],
    )


def _southern_sultanates(b: Builder, p: Places) -> None:
    p["dahlak"] = b.place(
        "The Sultanate of Dahlak",
        realm=DIVINE,
        aura=3,
        inside=p["ethiopia"],
        summary=(
            "Four large islands and 200 small ones just off Adulis, the "
            "Periplus's Alalaois, home to about 2000 people. The sultan lives "
            "on Dahlak Kebir in a village of cut stone and coral, and grows "
            "rich on water, his channels filling cisterns for passing ships. "
            "Nahaleg lives by fishing, Nakura by pearls and tortoise shell; "
            "the wealthy make beaded glass and trade hides and spices. Some "
            "3,000 to 4,000 slaves a year pass through its markets. Yemen "
            "occupied it in the early eighth century to punish its pirates, "
            "and used one island, 'The Isle of Thorns', as a prison. The "
            "people turned Muslim, and missionaries start from here. The sultan "
            "pays Ethiopia tribute, is independent in name, and loves the "
            "elephants of the nearby coast. He wants a herd of his own."
        ),
        secrets=[
            titled(
                "Dahlak's main mosque",
                "The main mosque of Dahlak is a converted Axumite church (p. 121).",
            ),
            titled(
                "Storyguide Notes",
                "The Divine aura of 3 covers the whole of the islands (p. 121).",
            ),
        ],
    )
    for key, name, text in (
        (
            "hadiya",
            "The Sultanate of Hadiya",
            "West of Shewa, bounded north by the Abbay: small fertile hills of "
            "fruit, grain and good pasture for horses and elephants, with thick "
            "jungle in the south, eight days' journey long and nine across. Its "
            "people use pieces of iron as money and pay tribute in ivory and "
            "exotic skins.",
        ),
        (
            "dewaro",
            "The Sultanate of Dewaro",
            "Between Hadiya and Ifat, below the strong Christian kingdom of "
            "Bale. Rather than clear their jungle hills, its men raid south for "
            "elephants and slaves. The sultan prefers infantry, mostly veterans.",
        ),
        (
            "ifat",
            "The Sultanate of Ifat",
            "Ten days' journey long and six across, bounded by the Awash, "
            "growing hotter and more forested southward. Dunya-huz, a man of "
            "Zeila, rules it with strong cavalry, and raises his son Umar "
            "Walashma to dream of a greater Ifat uniting Dewaro and Adal.",
        ),
        (
            "adal",
            "The Sultanate of Adal",
            "The largest of them, from the Awash across the Rift into the "
            "Danakil and to the Red Sea, dry and growing drier eastward. Clerics "
            "from Yemen have made its people the most devout of the sultanates, "
            "and its priests preach against the tribute and for war on Ethiopia. "
            "It courts Zeila, and an imam of its capital, Harar, converted "
            "Zeila's governor. Harar has a slave market, and Sufi sects nearby "
            "praise coffee.",
        ),
    ):
        p[key] = b.place(name, inside=p["ethiopia"], realm=DIVINE, summary=text)


def _rulers(b: Builder, p: Places) -> dict[str, Neighbour]:
    w: dict[str, Neighbour] = {}
    w["emperor"] = b.lord(
        "Negusa Negast of Ethiopia",
        title="",
        wealth="Wealthy",
        seat="Roha",
        ruler="Lalibela",
        place=p["ethiopia"],
        summary=paragraphs(
            "Gabril Mesqa Lalibela, king of kings, negus of Bet Amhara, ras of "
            "Lasta and bitwoded of Axum, in full Moa Anbessa Ze Imnegede "
            "Yehuda, Atse Lalibela, Negusa Negast, Seyoume Igziabeher. To the "
            "sultanates he is also Negus Tsion. He is addressed Girmawi or "
            "Janhoy, and his household is the Getochu.",
            "Born at Roha, named for the bees that swarmed at his birth, he "
            "survived his half-sister's poison, went to Jerusalem instead of "
            "exile and, at Alexandria in 1187, saw in a vision Saladin's "
            "conquest and God's command to rule and build a new Jerusalem. "
            "Kedus Harbe gave way that year, saying angels had told him to. "
            "The emperor never speaks in public. He holds his lords to him by "
            "travelling among them with his tent camp and armed retinue, the "
            "real seat of power; many nobles think him weak.",
        ),
    )
    emperor = w["emperor"]
    w["bahri"] = b.lord(
        "Bahri Negus of Medri Bahri",
        title="",
        wealth="Wealthy",
        seat="Debarwa",
        answers_to=emperor,
        place=p["debarwa"],
        summary="Second man of Ethiopia, rich in mines, trade and soldiers.",
    )
    b.lord(
        "Sheikh of Massawa",
        title="",
        seat="Massawa",
        ruler="Sheikh Hanafi",
        answers_to=w["bahri"],
        place=p["massawa"],
        summary="Sheikh Hanafi, a rich Muslim merchant lord sworn to the bahri "
        "negus; see Massawa.",
    )
    w["adulis"] = b.lord(
        "Governor of Adulis",
        title="",
        seat="Adulis",
        answers_to=w["bahri"],
        place=p["adulis_town"],
        summary=(
            "Keeps some three hundred men, about fifty cavalry and three small "
            "ships, which clear small threats from the district. The bishop "
            "leads him easily."
        ),
    )
    b.lord(
        "Governor of Zeila",
        title="",
        seat="Zeila",
        place=p["zeila"],
        summary="A convert to Islam, caught between sultan and emperor; see Zeila.",
    )
    b.lord(
        "Negus of Shewa",
        title="",
        seat="Nora",
        answers_to=emperor,
        place=p["shewa"],
        summary="Spends most of his time abroad hunting pagans and raiders.",
    )
    b.lord(
        "Negus of Agaw",
        title="",
        answers_to=emperor,
        place=p["agaw"],
        summary="Rules Agaw, Damot and Gojjam, overshadowed by the ras of Gojjam.",
    )
    b.lord(
        "Ras of Gojjam",
        title="",
        ruler="Na'akueto La'ab",
        answers_to=emperor,
        place=p["agaw"],
        summary=(
            "Na'akueto La'ab, the emperor's scheming cousin, freed from Debra "
            "Damo as a mercy. To show his loyalty he built two fine churches in "
            "Lasta, Wagra Sehin, 'among celestials', and Ashetan Maryem, 'among "
            "terrestrials'. Many nobles suspect him of waiting for his moment."
        ),
    )
    for key, name, ruler in (
        ("dahlak", "Sultan of Dahlak", ""),
        ("adal", "Sultan of Adal", ""),
        ("dewaro", "Sultan of Dewaro", ""),
        ("hadiya", "Sultan of Hadiya", ""),
        ("ifat", "Sultan of Ifat", "Dunya-huz"),
    ):
        b.lord(
            name,
            title="",
            ruler=ruler,
            answers_to=emperor,
            place=p[key],
            summary="A Muslim ruler who pays the negus a grudging tribute.",
        )
    return w


def _sketch(
    b: Builder, name: str, summary: str, age: int | None = None, secrets: Secrets = ""
) -> Character:
    return b.magus(
        name,
        covenant=None,
        house="",
        age=age,
        summary=summary,
        type="companion",
        secrets=secrets,
    )


def _people(b: Builder, p: Places, w: dict[str, Neighbour]) -> None:
    _sketch(
        b,
        "Kedus Harbe",
        "Emperor from 1180 and Lalibela's elder brother, thought to have "
        "wanted him dead. He abdicated in 1187 and retired to Debra Damo.",
    )
    _sketch(
        b,
        "Masqal Kibra",
        "Lalibela's empress. In 1190 she persuaded Abuna Mikael to make her "
        "brother Hirun a bishop. Her title is Nigeste Negast.",
    )
    _sketch(
        b,
        "Hirun",
        "Masqal Kibra's brother, bishop of Axum and Lasta since 1190. His "
        "schemes drove Abuna Mikael back to Egypt and brought the patriarch "
        "himself to Ethiopia in 1210.",
    )
    _sketch(
        b,
        "Abuna Yeshaq",
        "The pious head of the Ethiopian Church since 1210, in good health.",
    )
    _sketch(
        b,
        "Yetbarak",
        "Lalibela's son, spared imprisonment at Debra Damo.",
        13,
    )
    _sketch(
        b,
        "Umar Walashma",
        "Son of Dunya-huz of Ifat, raised for a greater, united Ifat.",
    )
    _sketch(
        b,
        "Sheikh Hussein",
        "A devout, peaceful imam who walks among the pagan tribes on Adal's "
        "southern border, slowly gathering a following.",
    )
    _sketch(
        b,
        "Takle Haymanot",
        "A boy of Shewa, son of the priest Sagaz Ab and Egzi'e Haraya, promised "
        "to God before his birth and learning scripture from his father.",
        5,
        [
            titled(
                "The archangel's watch",
                "Archangel Michael watches him (RoP:D p. 30; p. 121).",
            ),
            titled(
                "Storyguide Notes",
                "If history holds he will be one of Ethiopia's great saints, "
                "renewing the faith in the north, and abuna at 69 in 1284 (p. "
                "121).",
            ),
        ],
    )
    _sketch(
        b,
        "Cyril ibn Laqlaq",
        "The man in Egypt certain he will be next patriarch of Alexandria. "
        "Deadlock keeps the seat vacant, and he still sends letters south twice "
        "a year to keep watch on Axum.",
        secrets=[
            titled(
                "Storyguide Notes",
                "If history holds he wins in 1235 as Cyril III (p. 111).",
            ),
        ],
    )


def _society(b: Builder, p: Places) -> None:
    b.faction(
        "The Ethiopian Church",
        faction="Religious community",
        ruler="Abuna Yeshaq",
        realm=DIVINE,
        place=p["ethiopia"],
        summary=paragraphs(
            "Two brothers of Tyre, Edesius and Frumentius, enslaved at the "
            "Axumite court, taught Prince Ezana; Frumentius, consecrated by "
            "Athanasius, baptized him and became first abuna, Abba Salama, "
            "'Father of Peace', and Kesate Birhan, 'Revealer of Light', and "
            "died in 386 (feast August 1). After Chalcedon came the Nine Saints "
            "(Abbas Aftse, Alef, Aragawi, Garima, Guba, Liqanos, Pantelewon, "
            "Sehma and Yem'ata), monophysites who spread the Rule of Pachomius "
            "and the monastic life.",
            "It is monophysite, like Nubia and the Copts, with Christ's human "
            "nature 'dissolved like a drop of honey in the sea'. Believers "
            "pray to God and to the Kidusan, angels and saints who carry "
            "prayers up and do God's will. What is holy is not the building "
            "but the tabot, a consecrated copy of the Ark, usually of Moses' "
            "tablets and not a relic, dedicated to a saint, kept where only "
            "priests go and paraded on holy days. Its liturgy is in Ge'ez.",
            "Only three kinds of church are allowed: cave or hypogeum churches, "
            "mostly of the bad years between Axum and the Zagwe; rectangular "
            "cut stone; and the newer round timber. Stone and timber churches "
            "must keep a thick forest around them, which carries prayers to "
            "Heaven. The abuna, always an Egyptian named by the Coptic "
            "patriarch for life, often arrives knowing neither Amharic nor "
            "Ge'ez and feeling exiled. He names bishops, who name priests and "
            "some debterah. The emperor pays the sultan of Cairo before a new "
            "abuna can be anointed.",
            "The year starts on August 30 with twelve 30-day months in Ge'ez "
            "(Meskerem, Taqamt, Hadar, Tahsas, Tarr, Yekatit, Megabit, Miyazya, "
            "Ganbot, Sane, Hamle, Nehase) and Pagume, five or six added days. "
            "By the Julian calendar they start August 30, September 29, October "
            "29, November 28, December 28, January 27, February 26, March 29, "
            "April 28, May 28, June 27, July 27 and August 26, Miyazya and those "
            "after it a day earlier in a leap year such as 1220 (p. 108). "
            "The four-year cycle is named for John, Mark, Matthew and Luke, "
            "Luke's being the leap year, and the count of years runs eight "
            "behind Europe until the new year, then seven: January 1, 1220 is "
            "Tarr 5, 1212. Feasts are Enkutatash (August 30, Sheba's return), "
            "Maskal (17 Meskerem or September 15, the True Cross, with a "
            "daisy-decked bonfire), Kulubi Gabriel (Tahsas 18 or December 16), "
            "Gena (Tahsas 28 or December 25), Timket (Tarr 10 or January 6, "
            "three days with the tsellats paraded on Ketera), Faseka (in 1220, "
            "Miyazya 2 or March 27) and Axum Tsion (Hadar 20 or November 18).",
        ),
        rules=paragraphs(
            "In a town with a church forest the Divine aura gathers in the "
            "forest, leaving the land outside one lower, even around a church "
            "in mid-town; a particularly lush forest usually raises the aura "
            "one above the standard (RoP:D p. 10). The tabot focuses the aura "
            "and keeps it when carried out of the forest, for as long as it "
            "was in the aura (p. 111).",
            "Soot from the Maskal fire, marked on the forehead, grants a "
            "temporary Faith Point lasting until it is washed off or spent (p. "
            "110). Spells with Year durations follow the solstices and are "
            "unaffected by this calendar (p. 108).",
        ),
    )
    b.faction(
        "The Debterah",
        faction="Religious community",
        realm=DIVINE,
        place=p["ethiopia"],
        summary=paragraphs(
            "Saint Yared of Axum, taught by his uncle Gidewon, three divine "
            "birds and Abuna Aragawi, made the zema chant of the Ethiopian "
            "Church. An emperor, rapt, once dropped his spear on Yared's foot "
            "and neither noticed until the song ended; offered any reward, "
            "Yared asked for solitude and went to the Semiens. His feast is 11 "
            "Ganbot, May 8 or 9.",
            "Debterah (singular debtera), lay deacons of Christian and Falasha "
            "communities, sing, teach noble children, make protective amulets, "
            "cast horoscopes and drive out evil spirits by The Magic Star "
            "Book, handed down from teacher to student. Falasha kahens often "
            "become debterah before they are confirmed as rabbis.",
            "Yared's five volumes are The Books of Digua and Tsome Digua, The "
            "Book of Meraf, The Book of Mewasit and The Book of Zimare.",
        ),
        rules=paragraphs(
            "A holy societas (p. 114). Favored Abilities: Adjuration, Blessing, "
            "Craft Amulets, Invocation (RoP:D pp. 34, 37, 48-50, 137). Without "
            "that book: Clerk or Educated, Enchanting Music, and Sense "
            "Holiness/Unholiness or Wise One; suggested Abilities Artes "
            "Liberales (astronomy), Chirurgy, Organization Lore: Ethiopian "
            "Church, Medicine, Music, Teaching and Theology, with Divine and "
            "Infernal Lore for a Wise One, who can exorcise only through "
            "ceremonies and the auras of tabot and forest.",
            "Yared's books together are a summa of Organization Lore: Ethiopian "
            "Church, Level 5, Quality 8.",
        ),
    )
    b.faction(
        "The Beta Israel",
        faction="People or tribe",
        realm=DIVINE,
        place=p["bet_amhara"],
        summary=paragraphs(
            "The 'children of Israel', called Falasha, are a distinct Jewish "
            "people who marry among themselves, chiefly in the Falasha "
            "province of Bet Amhara and in Agaw and Gojjam. Gudit's fierce army "
            "came from them, but a century of Zagwe rule has eased that and "
            "many serve the emperor loyally. Christian neighbours help with "
            "burials, since Falasha may not handle corpses.",
            "The Kebra Negast, 117 chapters in Ge'ez, tells how Solomon "
            "seduced Makkeda, queen of Sheba, how their son Menelik came north "
            "and proved himself with Solomon's ring, and how the firstborn sons "
            "sent home with him stole the Ark, which carried them miraculously "
            "to Ethiopia. Menelik became the first negusa negast, and those "
            "sons the Falasha. The Ethiopian nobility believe every word, and "
            "it helps protect them.",
        ),
    )
    b.faction(
        "The Mesafint",
        faction="Family",
        place=p["ethiopia"],
        summary=paragraphs(
            "The nobility of Ethiopia, in descending order: negus, a high king "
            "made only by the emperor; ras, the highest noble rank, used by "
            "lesser kings and minor princes; bitwoded, like a duke; dejazmach, "
            "'gatekeeper', a count; fitawrari, 'leader of the vanguard', a "
            "baron; gerazmach and kenyazmach, equal older titles for favoured "
            "commanders, often given in pairs; balambaras, a local governor; "
            "ato, 'sir', woizero for a woman. Noble children are lij, a noble's "
            "wife emebet hoy.",
            "A title passes to surviving brothers first, each in turn, then to "
            "the eldest ruler's first son. Some nobles try to get round this.",
            "The emperor's court, the makwanet, includes two Afe Negus, the "
            "'Mouth of the King', who speak as him; the Blattengeta, master of "
            "the retinue; the Blatta, pages; the Enderase, 'Regent', a title "
            "also used by his envoys; two Lique Mekwas, who dress as him and "
            "ride into battle beside him as decoys; and the Tsehafi Tezaz, "
            "'Minister of the Pen', keeper of the great seal, of records, laws "
            "and treaties. The consort is respectfully Itege.",
        ),
    )


def _creatures(b: Builder, p: Places) -> None:
    b.creature(
        "Bouda Hyena-spirit",
        page="p. 109",
        realm="Faerie",
        might=10,
        form="Mentem",
        confidence=(0, 0),
        place=p["debarwa"],
        block={
            "characteristics": characteristics(1, 2, -4, -1, 0, 2, 1, 2),
            "virtues_flaws": [
                "Faerie Beast",
                "Faerie Sight",
                "Faerie Speech",
                "Feast of the Dead",
                "Improved Characteristics",
                "Increased Faerie Might (Minor)",
                "Lesser Power",
                "Lesser Power",
                "Personal Power",
                "Monstrous Appearance",
                "Incognizant",
                "Nocturnal",
                "Role Requires Suffering",
                ("Negative Reaction", {"detail": "unpleasant odor"}),
                "Susceptible to Deprivation",
                vf_ward("Folk Charms"),
                "Crafty",
                "Crushing Jaws",
                "Keen Eyesight",
                "Large Teeth",
                "Mimicry",
                "Pursuit Predator",
                "Thick Fur/Thick Scales",
            ],
            "abilities": [
                ("Animal Handling", 3, "hyenas"),
                ("Area Lore: Ethiopia", 4, "highland grazing pastures"),
                ("Athletics", 3, "running"),
                ("Awareness", 3, "food"),
                ("Brawl", 5, "bite"),
                ("Faerie Speech", 5, "lying"),
                ("Guile", 4, "feign dead"),
                ("Hunt", 4, "tracking"),
                ("Survival", 3, "desert"),
            ],
            "traits": {"Cowardly": 3, "Sly": 2},
            "reputations": {"Corpse-eating (regional)": 3, "Treacherous (local)": 2},
        },
        attacks=[
            Builder.attack("Bite", 2, 9, 7, 6),
            Builder.attack("Dodge", 2, None, 5, None),
        ],
        soak=3,
        fatigue_levels="OK, 0/0, -1, -3, -5, Unconscious",
        encumbrance="0 (0)",
        powers=[
            Builder.power(
                "Enthralling Sound",
                2,
                -10,
                "Mentem",
                rtd=("Voice", "Sun", "Group"),
                level=30,
                does="Stirs an emotion in all who hear it, commonly fear, lust or "
                "wrath, or deepens one already felt. A stress roll on a fitting "
                "Personality Trait against Ease Factor 9 overcomes it. CrMe 30 "
                "(Base 4, +2 Voice, +2 Sun, +2 Group); Lesser Power x2 (50 levels, "
                "-4 Might points).",
            ),
            Builder.power(
                "Skin of Man or Beast",
                1,
                0,
                "Animal",
                rtd=("Personal", "Sun", "Individual"),
                level=20,
                does="Takes the form of a man or woman of the area. MuAn 20 (Base "
                "10, +2 Sun); Personal Power (20 levels, -1 Might point).",
            ),
        ],
        vis=[BodyVis(2, "Mentem", "in its tongue")],
        appearance=(
            "A striped hyena, deep in the chest with short hind legs and a "
            "sloping back, a big short-muzzled head on a thick stiff neck. It "
            "often makes its eyes glow red."
        ),
        notes=paragraphs(
            "Ethiopians say hereditary blacksmiths turn into hyenas and dig up "
            "Christian dead at midnight. Unlike the shapeshifting bouda of the "
            "Maghreb (BS&S), the bouda here are hyena-spirits that possess "
            "people and drive them to lust, murder or rage; debterah make "
            "amulets against them. They may be faeries harvesting vitality, or "
            "weak tempter demons.",
            "A hyena's bite is Init 0, Atk +4, Def +1, Dam +3, and Crushing "
            "Jaws raises the damage bonus to +6, which is the +6 shown. As a "
            "companion it must swap Incognizant "
            "for Narrowly or Highly Cognizant and take another Flaw, such as a "
            "Personality Flaw.",
        ),
    )
    b.creature(
        "The Dragon Ceto",
        page="p. 105",
        realm="Faerie",
        might=45,
        form="Aquam",
        size=10,
        tires=False,
        place=p["ethiopia"],
        block={
            "characteristics": characteristics(0, -2, -6, -6, 21, 2, 2, -10),
            "virtues_flaws": [
                *["Huge"] * 5,
                *["Increased Faerie Might (Major)"] * 3,
                "Faerie Beast",
                "Faerie Sight",
                "Faerie Speech",
                "Feast of the Fae",
                "Highly Cognizant",
                "Improved Characteristics",
                *["Lesser Power"] * 4,
                *["Personal Power"] * 2,
                "Monstrous Appearance",
                "Might Recovery Requires Vitality",
                "Role Requires Suffering",
                "Susceptible to Deprivation",
                vf_ward("Payment: those who pay the sacrifice"),
            ],
            "abilities": [
                ("Area Lore: Red Sea Coasts", 3, "Ports"),
                ("Awareness", 3, "prey"),
                ("Brawl", 7, "crushing"),
                ("Faerie Speech", 5, "sounding intimidating"),
                ("Folk Ken", 1, "human prey"),
                ("Hunt", 4, "people"),
                ("Stealth", 3, "stalking prey"),
            ],
            "traits": {"Destructive": 3, "Inquisitive": 3, "Dragon": 3},
            "reputations": {
                "Ravenous destroyer of the coasts (Greece)": 3,
                "Massive Sea Serpent (local)": 2,
            },
        },
        attacks=[
            Builder.attack("Claws", -1, 11, 10, 24),
            Builder.attack("Fangs", -10, 14, -5, 22),
        ],
        soak=16,
        encumbrance="0 (0)",
        powers=[
            Builder.power(
                "Corrosive Odor",
                5,
                0,
                "Auram",
                level=25,
                does="Constant: +5 Damage to anyone within one pace. MuAu 25 (Base "
                "5, +1 Part, +2 Sun, +1 Constant); Lesser Power (25 levels). No "
                "Initiative is printed.",
            ),
            Builder.power(
                "Venomous Bite (non-magical)",
                0,
                0,
                "",
                does="Compare its attack advantage to the target's armor "
                "Protection, not Soak. If it exceeds that, add adder venom (ArM5 p. "
                "180), wound or no wound.",
            ),
            Builder.power(
                "Flight",
                2,
                -14,
                "Animal",
                rtd=("Personal", "Sun", "Individual"),
                level=40,
                does="Flies, with Athletics for hard maneuvers, but cannot fight "
                "at full speed, nor fly heavily encumbered or with a passenger of "
                "its Size or more unless another faerie shares the load. ReAn 40 "
                "(Base 15, +2 Sun, +3 Size); Personal Power x2 (40 levels, -2 "
                "Might Cost).",
            ),
            Builder.power(
                "Fiery Breath",
                6,
                -26,
                "Ignem",
                rtd=("Voice", "Momentary", "Group"),
                level=40,
                does="A gout of flame: +20 damage to all in a 60-degree arc 50 "
                "paces long. CrIg 40 (Base 15, +2 Voice, +2 Size, +1 Unnatural "
                "Shape); Lesser Power x2 (40 levels, -2 Might Points).",
            ),
            Builder.power(
                "Lantern Gaze",
                5,
                -20,
                "Ignem",
                rtd=("Personal", "Sun", "Individual"),
                level=25,
                does="Blinding light shines from its eyes to light its way. CrIg "
                "25 (Base 5, +2 Sun, +2 Size); Lesser Power (25 levels).",
            ),
        ],
        vis=[BodyVis(9, "Aquam", "in the scales over its eyes")],
        appearance=(
            "A sea serpent as large as a cog or trireme, with fin-like wings, "
            "glowing yellow eyes and dark green-black scales like shields. It "
            "stinks corrosively, boils the sea with its breath and raises waves "
            "in its wake."
        ),
        notes=paragraphs(
            "Poseidon loosed it on Ethiopia's coasts when Cassiopeia boasted "
            "that she and her daughter outshone the nereids. Perseus defeated "
            "it, but Jewish tales of the Leviathan kept it alive. It hunts the "
            "Red Sea and eastern Mediterranean, flying between them as it "
            "pleases, and it feeds on sailors' fear.",
            "Wound Penalties as printed: -1 (1-15), -3 (16-30), -5 (31-45), "
            "Incapacitated (46-60), Dead (61+). Not suitable as a player "
            "character.",
        ),
    )


# -- the three covenant sites --

SIWA_SECRETS = [
    titled(
        "Siwa's resources",
        "Siwa's resources (pp. 131-133): up to four lab sites, a working "
        "covenant needing at least two: Siwa Village and any of Aghurmi, "
        "Abu Sharef or Bilad al-Rum. Income: 20 Mythic Pounds a year from "
        "dates, and 20 from caravan barter and rest fees. Few craftsmen; "
        "true specialists must be brought in.",
    ),
    titled(
        "Alexander's Camp",
        "Alexander's Camp gives 4 Herbam vis a year: cut the first fronds "
        "to sway on the Ides of February (pp. 133-134).",
    ),
    titled(
        "Alexander's Stele",
        "Alexander's Stele gives 6 Vim vis: a prism, gem or glass set "
        "atop it to catch the sunrise on the Ides of February (pp. "
        "133-134).",
    ),
    titled(
        "The Crypts of Jabal al-Mawta",
        "The Crypts of Jabal al-Mawta give 5 Corpus vis: a lone skull in "
        "the tomb with two cobra-headed pillars, on the winter solstice, "
        "ending if the tombs are emptied (pp. 133-134).",
    ),
    titled(
        "The Spring of the Sun",
        "The Spring of the Sun gives 6 Aquam or 6 Ignem vis: fill an "
        "amphora on the full moon between late October and early "
        "November, at noon for Aquam or midnight for Ignem (pp. 133-134).",
    ),
    titled(
        "Storyguide Notes",
        "Boons: Difficult Access (Minor Site); Edifices (Minor "
        "Fortification); Important Building x3, the Aghurmi temple fort "
        "and the lesser temples at Abu Sharef and Bilad al-Rum (Minor "
        "Fortification); Peasants (Free Residents); Strong Community "
        "(Minor Residents); Ungoverned (Minor External Relations). Hooks: "
        "Poverty, Multiple Sites (Minor Resources; pp. 128, 131); Road "
        "(Minor Site); Tribunal Border (Major External Relations); Unsafe "
        "(Minor External Relations). The book counts seven of each, and "
        "would give Castle and Ringworks only if the Bedouin matter to "
        "the saga. It suggests Castle, minor Natural Disaster (locusts on "
        "the dates), or a minor Regio holding a version of the temples "
        "(pp. 128-130).\n\nMultiple Sites (Major/Minor Resources Hook, p. "
        "131): facilities at several sites must go without the Aegis, "
        "share tokens or take several rituals in a day, at the cost of "
        "vis, of unguarded sanctums or of more tokens to steal. Major "
        "with five or more sites.\n\nResources: think of it as between "
        "Manor and Farm and Grand Castle (Covenants pp. 45-46). Scores in "
        "Tamazight count one less unless Siwan is the specialty.\n\nVis "
        "(pp. 133-134): Alexander's Camp, 20 points, Magic aura 2. "
        "Alexander's Stele, 30 points, Magic aura 3. Crypts of Jabal "
        "al-Mawta, 25 points, Magic aura 2. Spring of the Sun, 30 points, "
        "Magic aura 2.\n\nStory themes (pp. 134-135): exploring deserts, "
        "native traditions and lost ruins from a safe distance; scarcity "
        "and survival when isolation turns dangerous. The caravans bring "
        "the slave and salt trade and the Great Desert's adventures to "
        "the door (BS&S).",
    ),
]


def _siwa(b: Builder, p: Places) -> None:
    siwa = p["siwa"] = _site(
        b,
        "Siwa Oasis",
        aura=3,
        within="Egypt",
        summary=paragraphs(
            "A depression some 50 miles long and 5.5 to 18.5 miles wide, 500 "
            "feet below the desert plateau, a patchwork of sand, date palms and "
            "springs around sterile salt lakes, the largest being al-Zaytun. "
            "It was the oracle of Ammon, visited by Alexander, and its priests "
            "dwindled away, hastened by Justinian's decree of 532. Its people "
            "resisted the Arab conquest and took Islam only late in the twelfth "
            "century. By 1200 there remained seven families of about 200, whose "
            "forty men could not hold the old temple village and built a "
            "fortified one. Though Cairo claims it, no governor has ever come.",
            "Alexandria is eight days east by the Sikkit al-Sultan, Bahriyah "
            "twelve southeast, Awdjila 75 leagues west on the Garamantian Road "
            "through the Great Sand Sea. Caravans rest here on the way to Cairo "
            "and Alexandria, some bound for Mecca.",
            "The people grow dates, olives and wheat, keep goats and camels, "
            "and brew intoxicating lagbi from palm hearts. Men shave their "
            "heads; women wear silver and tiny braids. Outsiders rarely pass "
            "the gates, and most people speak only the Siwan dialect of "
            "Tamazight. Seven to ten sheikhs, wealthy elders, rule as a "
            "council. The thirty or so zaggalah, 'club-wielders', men of twenty "
            "to forty, sleep outside the walls and work the fields until they "
            "marry, when a new home rises on top of the walls. The khadim, "
            "drawn from them, guard the sheikhs and enforce the law, unmarried "
            "until released. Old women keep the stories, and an old firekeeper "
            "watches the gate and the fire that lights every hearth.",
        ),
        secrets=SIWA_SECRETS,
    )
    b.town(
        "Shali",
        population=220,
        place=siwa,
        summary=(
            "The walled village of Siwa, built in 1203 of salt mud that sets "
            "like cement, two or three storeys of homes forming its wall, its "
            "lanes wide enough for one laden donkey. Near it is the conical "
            "Jabal al-Mawta, the Hill of the Dead."
        ),
    )
    b.place(
        "Aghurmi",
        aura=3,
        inside=siwa,
        summary=(
            "The abandoned village three miles east of Shali, with the main "
            "oracle temple, a cut-stone fort on a very large rock, among a dozen "
            "lesser buildings, a brick watchtower, part of a wall, and "
            "Alexander's Stele, raised by Ptolemy to make up for denying Siwa "
            "the king's body. A staircase in the temple leads down to a deep "
            "well. Close by is the Spring of the Sun, coolest at noon and "
            "boiling by midnight."
        ),
    )
    b.place(
        "Abu Sharef",
        aura=3,
        inside=siwa,
        summary=(
            "A crumbling abandoned village 28 miles east of Shali, across the "
            "salt lake, the edge of Siwan land, with a lesser temple of Ammon "
            "of dressed stone, walls over a meter thick, with chambers enough "
            "for sanctum and laboratory."
        ),
    )
    b.place(
        "Bilad al-Rum",
        aura=3,
        inside=siwa,
        summary=(
            "On the western edge 13.5 miles from Shali, by abandoned Khamisah: "
            "a rectangular lesser temple of dressed stone with three grand "
            "halls, a brick outbuilding, old quarries, and rock-cut tombs in the "
            "hill."
        ),
    )
    b.faction(
        "The Zenata of Siwa",
        faction="People or tribe",
        members=55,
        place=siwa,
        summary=(
            "Berbers, who call themselves Imazighen, 'Free People', and speak "
            "Tarifit Tamazight: fifty-five warriors with two or three camels "
            "each, camped by the springs of al-Zaytun. They raid caravans and "
            "pilgrims and sell loot and slaves at market."
        ),
        wants="Goods, wives, excitement and regular spoils.",
        offers="A hardened host who know the desert, after a show of force.",
    )
    aznag = b.magus(
        "Aznag ag Tannan",
        covenant=None,
        house="",
        age=32,
        type="companion",
        summary=(
            "A famous Berber treasure hunter who guides, loots old graves and "
            "now and then turns bandit, which he finds the safest way to live "
            "well. Slick and secretive about his methods, he captains seven "
            "cousins."
        ),
    )
    b.stats(
        aznag,
        {
            "characteristics": characteristics(0, 1, 0, 1, 1, 2, 2, 1),
            "confidence": (1, 3),
            "virtues_flaws": [
                "Mercenary Captain",
                "Clear Thinker",
                "Improved Characteristics",
                "Intuition",
                "Luck",
                "Tough",
                "Warrior",
                "Well-Traveled",
                ("Enemies", {"detail": "Rival Tribe"}),
                "Greedy (Major)",
                "Infamous",
                "Missing Ear",
            ],
            "abilities": [
                ("Animal Handling", 2, "camels"),
                ("Living Language: Arabic", 3, "slang"),
                ("Area Lore: Egypt", 3, "ruins"),
                ("Area Lore: North Africa", 3, "ruins"),
                ("Athletics", 2, "running"),
                ("Awareness", 3, "spotting ambushes"),
                ("Bargain", 3, "hard sell"),
                ("Brawl", 4, "dodging"),
                ("Carouse", 2, "gambling"),
                ("Charm", 2, "guards"),
                ("Folk Ken", 2, "customers"),
                ("Guile", 2, "lying about where he has been"),
                ("Leadership", 3, "organizing attacks"),
                ("Ride", 4, "camels"),
                ("Single Weapon", 4, "long sword"),
                ("Stealth", 4, "in open desert"),
                ("Survival", 4, "finding water"),
                ("Living Language: Tamazight", 5, "Tarifit dialect"),
                ("Thrown Weapon", 3, "sling"),
            ],
            "traits": {"Greedy": 6, "Pragmatic": 3, "Stoic": 2},
            "reputations": {
                "Merciless Warrior (Deserts of Egypt and Libya)": 4,
                "Finder of Lost Treasures (Berber Tribes)": 3,
                "Hard but Fair (Siwa Oasis)": 3,
            },
            "notes": paragraphs(
                "Printed on p. 131. Combat: Dodge Init +1, Def +6; Fist Init +1, "
                "Atk +4, Def +5, Dam +1; Kick Init 0, Atk +4, Def +4, Dam +4; "
                "Bludgeon Init +1, Atk +6, Def +5, Dam +3; Sling Init -2, Atk +5, "
                "Def +5, Dam +5; Long sword Init +3, Atk +9, Def +6, Dam +7. Soak "
                "+6. Encumbrance 1 (3).",
                "Equipment: dagger, desert clothes, quilted armor, long sword, "
                "sling and stones; three camels, digging tools, desert camping "
                "gear. He wears flowing desert clothes and is never without sword "
                "and dagger.",
            ),
        },
        source=SOURCE,
    )
    gwafa = b.magus(
        "Gwafa",
        covenant=None,
        house="",
        age=23,
        type="grog",
        summary=(
            "A smiling young desert rider, imposing on his camel. He cannot "
            "learn languages, tells jokes in Tamazight regardless, and enjoys "
            "the frustration they cause."
        ),
    )
    b.stats(
        gwafa,
        {
            "characteristics": characteristics(0, 1, 0, -1, 2, 2, 1, 0),
            "virtues_flaws": [
                "Covenfolk",
                "Tough",
                "Warrior",
                "Well-Traveled",
                ("Ability Block", {"detail": "Languages"}),
                "Reckless (Minor)",
                (
                    "Social Handicap",
                    {"detail": "Inconsiderate of language difficulties"},
                ),
            ],
            "abilities": [
                ("Animal Handling", 2, "camels"),
                ("Area Lore: Egypt", 3, "oases"),
                ("Area Lore: North Africa", 3, "trade routes"),
                ("Athletics", 2, "running"),
                ("Awareness", 3, "standing on guard"),
                ("Brawl", 4, "kicking"),
                ("Carouse", 2, "remaining sober"),
                ("Ride", 4, "camels"),
                ("Single Weapon", 4, "long sword"),
                ("Stealth", 4, "in open desert"),
                ("Survival", 4, "finding water"),
                ("Living Language: Tamazight", 5, "Tarifit dialect"),
                ("Thrown Weapon", 3, "sling"),
            ],
            "traits": {"Brave": 3, "Reckless": 3, "Loyal": 2, "Subtle": -2},
            "notes": paragraphs(
                "Printed on p. 133. Combat: Dodge Init 0, Def +4; Fist Init 0, Atk "
                "+5, Def +4, Dam +2; Kick Init -1, Atk +6, Def +4, Dam +5; Sling "
                "Init -3, Atk +5, Def +3, Dam +6; Long sword Init +2, Atk +12, Def "
                "+6, Dam +8. Soak +3. Encumbrance 0 (3).",
                "Equipment: dagger, desert clothes, quilted armor, long sword, "
                "sling and stones; three camels, desert camping gear.",
            ),
        },
        source=SOURCE,
    )
    for character in (aznag, gwafa):
        b.link(character, "places", siwa, "Lives by the oasis")


IKHMINDI_SECRETS = [
    titled(
        "Ikhmindi's resources",
        "Ikhmindi's resources (pp. 137-139): up to three labs with living "
        "space in the two churches and the catacombs, or six without. "
        "Income only from fees and barter with spring and late autumn "
        "caravans, or Tapara's ventures. Few specialists and no teachers; "
        "a hermit might teach, and training can be had at Faras or Qasr "
        "Ibrim. A basketweaver, fishermen, herdsmen, potters and a smith "
        "would serve.",
    ),
    titled(
        "The Abandoned Copper Mine",
        "The Abandoned Copper Mine gives 4 Rego and 3 Terram vis a year: "
        "it gathers in copper nuggets or tools left against the seam, 25 "
        "leagues east on the Wadi Allaqi route, and stops for good if "
        "Hathor's statue at the door is taken (pp. 139-140).",
    ),
    titled(
        "The Black Sandbar of the Nile",
        "The Black Sandbar of the Nile gives 4 Creo vis twice a year: "
        "rich black silt filling two amphorae as the flood rises in June "
        "and falls in October, two leagues north of the fishing camp (pp. "
        "139-140).",
    ),
    titled(
        "The Temple Kiosk of Qertassi",
        "The Temple Kiosk of Qertassi gives 7 Imaginem vis a year: "
        "haboobs leave it in the sand at the Hathor columns, 25 leagues "
        "northeast; it stops if the capitals are harmed and returns when "
        "they are mended (pp. 139-140).",
    ),
    titled(
        "Storyguide Notes",
        "Hooks: Castle (Major Fortification); Fragile Vis Sources (Major "
        "Resources; two sites, the mine unrepairable); Poverty (Minor "
        "Resources); Ringworks (Free Fortification Choice); Road (Minor "
        "Site); Unsafe (Minor External Relations). Boons: Edifices (Minor "
        "Fortification); Difficult Access (Minor Site); Healthy Feature "
        "(Minor Site; the well, +1 to Aging Rolls for those who drink "
        "from it most of the year); Missile Weapons (Minor Residents); "
        "Important Building x2, the two churches (Minor Fortifications); "
        "Peasants (Free Residents). The book counts six Boons and eight "
        "Hooks (pp. 136-137).\n\nSuggested: minor Contested Resources; "
        "minor Hermit, a Sufi or Gnostic mystic opposed to the use of the "
        "churches; major Beholden to regional inspectors; minor Rival, a "
        "Bedouin tribe. Boons: minor Hidden Resources, from a lost Nubian "
        "tomb or the ruins of walled Sabagura 5 leagues north; major "
        "Autocephelous, which spares the inspectors but may mean worse "
        "raiders (p. 137).\n\nFragile Vis Sources (Major/Minor Resources "
        "Hook, p. 134): a source of four or more pawns stops if a feature "
        "of the site is damaged, resuming if repaired. Major for three or "
        "more fragile sites; one that cannot be repaired counts as two. "
        "It may be unknown to the covenant.\n\nVis (pp. 139-140): Abandoned "
        "Copper Mine, 35 points in all, Magic aura 3. Black Sandbar of "
        "the Nile, 40 points, no aura. Temple Kiosk of Qertassi, 35 "
        "points, Magic aura 3.\n\nStory themes (p. 140): survival in a "
        "harsh land, exploration for treasure-filled tombs, lost magics, "
        "Bedouin adversity, and a great legacy.",
    ),
]


def _ikhmindi(b: Builder, p: Places) -> None:
    ikhmindi = p["ikhmindi"] = _site(
        b,
        "Ikhmindi",
        aura=3,
        within="Nubia",
        summary=paragraphs(
            "A walled refuge above the Nile in Nobatia, seven leagues south of "
            "the first Cataract and Philae, where the routes of the Great "
            "Desert, a splinter of the Darb al-Arba'in and the Red Sea road "
            "meet. Greek missionaries built it in the mid-sixth century, to "
            "shelter farmers and spread the faith. It stood mostly empty as a "
            "caravan halt until escaped slaves moved in ten years ago, joined "
            "by local families. Its people, from all over Africa, the "
            "Slavelands and even Europe, stay because no one governs them.",
            "It measures about 360 feet by 300, on a hill between two ravines, "
            "with ten-foot walls, two towers a side and one at each corner. "
            "The main gate faces southwest to the caravan trail; the "
            "Fishermen's Gate leads northeast down to huts by the river, "
            "flooded each year. About a hundred two-storey family houses pack "
            "the five-foot alleys, half of them occupied, and an open space "
            "fifteen feet wide surrounds the central cut-stone church with its "
            "catacombs. The southern church is built into the wall. Livestock "
            "sleep in stables by the gate. The central well runs cool and "
            "fresh and seems to invigorate all who drink.",
            "Women, children and the old work inside, boys help the fishermen, "
            "and the men farm thin fields along the streams, together for "
            "safety. Nothing is wasted, even dried dung. The men are bowmen, "
            "like all the 'Archers of the Eye'.",
        ),
        secrets=IKHMINDI_SECRETS,
    )
    tapara = b.magus(
        "Tapara",
        covenant=None,
        house="",
        age=33,
        type="companion",
        summary=(
            "A Nobatian caravan leader and guide whose family lives safe in "
            "Ikhmindi. Away in spring and autumn, he plans through summer and "
            "does as little as he can all winter with his wife and children. "
            "He has trafficked in slaves without quite being a slaver."
        ),
    )
    b.stats(
        tapara,
        {
            "characteristics": characteristics(0, 1, 2, 1, 1, 2, 0, 1),
            "confidence": (1, 3),
            "virtues_flaws": [
                "Mercenary Captain",
                "Enduring Constitution",
                "Gossip",
                "Improved Characteristics",
                "Premonitions",
                "Tough",
                "Warrior",
                "Well-Traveled",
                "Ambitious (Major)",
                ("Enemies", {"detail": "Local Raiding Tribe"}),
                ("Fear", {"detail": "hyenas"}),
                "Infamous",
            ],
            "abilities": [
                ("Animal Handling", 2, "camels"),
                ("Living Language: Arabic", 3, "slang"),
                ("Area Lore: Egypt", 3, "oases"),
                ("Area Lore: Great Desert", 2, "oases"),
                ("Area Lore: Nubia", 3, "oases"),
                ("Athletics", 2, "running"),
                ("Awareness", 2, "spotting ambushes"),
                ("Bargain", 3, "hard sell"),
                ("Bows", 3, "shortbow"),
                ("Brawl", 4, "dodging"),
                ("Charm", 2, "guards"),
                ("Folk Ken", 2, "customers"),
                ("Guile", 2, "lying about where he has been"),
                ("Leadership", 3, "organizing caravans"),
                ("Living Language: Nubian", 5, "Mahasi Dialect"),
                ("Premonitions", 2, "sensing ambushes"),
                ("Ride", 4, "camels"),
                ("Single Weapon", 4, "long sword"),
                ("Stealth", 4, "in open desert"),
                ("Survival", 4, "finding water"),
                ("Living Language: Tamazight", 2, "Siwan"),
            ],
            "traits": {"Ambitious": 6, "Pragmatic": 3, "Stoic": 2},
            "reputations": {
                "Slaver (Nubian freeholds)": 4,
                "Capable Merchant (Great Desert and Nubia)": 3,
                "Good Provider (Ikhmindi)": 3,
            },
            "notes": paragraphs(
                "Printed on p. 136. Combat: Dodge Init +1, Def +6; Fist Init +1, "
                "Atk +4, Def +5, Dam +1; Kick Init -2, Atk +4, Def +4, Dam +4; "
                "Bludgeon Init +1, Atk +6, Def +5, Dam +3; Long sword Init +3, Atk "
                "+9, Def +6, Dam +8; Shortbow Init 0, Atk +6, Def +4, Dam +7. Soak "
                "+6. Encumbrance 1 (3).",
                "Equipment: dagger, desert clothes, quilted armor, long sword, "
                "shortbow and 20 arrows; three camels, desert camping gear. He "
                "dresses as a desert nomad and always carries a scimitar and "
                "dagger.",
            ),
        },
        source=SOURCE,
    )
    petros = b.magus(
        "Petros",
        covenant=None,
        house="",
        age=23,
        type="grog",
        summary=(
            "A hard-working third son, always looking for a wife. He loves "
            "Ikhmindi, is sure Egyptian slavers will destroy it, and poaches "
            "or steals from caravans without much thought for the consequences."
        ),
    )
    b.stats(
        petros,
        {
            "characteristics": characteristics(0, 2, -1, 0, 1, 1, 2, 0),
            "virtues_flaws": [
                "Covenfolk",
                vf_puissant("Bows"),
                "Tough",
                "Pessimistic",
                ("Social Handicap", {"detail": "Pagan"}),
            ],
            "abilities": [
                ("Living Language: Arabic", 3, "slang"),
                ("Area Lore: Nubia", 2, "springs"),
                ("Athletics", 2, "hiking"),
                ("Awareness", 2, "standing guard"),
                ("Bargain", 2, "bartering"),
                ("Bows", 5, "short bow"),
                ("Brawl", 2, "dodging"),
                ("Carouse", 2, "gambling"),
                ("Folk Ken", 2, "determining intent"),
                ("Hunt", 3, "small game"),
                ("Living Language: Nubian", 5, "Mahasi Dialect"),
                ("Profession: Farmer", 3, "terrace farming"),
                ("Stealth", 2, "in the hills"),
                ("Survival", 3, "finding water"),
            ],
            "traits": {"Hard-working": 2, "Steadfast": 2},
            "notes": paragraphs(
                "Printed on p. 136. Bows is 5+2 with his Puissant Virtue. Combat: "
                "Dodge Init 0, Def +3; Fist Init 0, Atk +4, Def +2, Dam +1; Kick "
                "Init -1, Atk +4, Def +1, Dam +4; Bow Init -1, Atk +13, Def +8, "
                "Dam +7; Dagger Init 0, Atk +6, Def +2, Dam +7. Soak +4. "
                "Encumbrance 0 (2).",
                "Equipment: dagger, peasant clothes, bow and 20 arrows; hill "
                "camping gear. He wears light trousers, a loose cotton smock, "
                "copper bangles on wrists and ankles, a necklace of cowries and "
                "a diamond of green-brown glass, and carries his family's horn "
                "bow, his only inheritance.",
            ),
        },
        source=SOURCE,
    )
    for character in (tapara, petros):
        b.link(character, "places", ikhmindi, "Lives here")


ADULIS_SECRETS = [
    titled(
        "The village's resources",
        "The village's resources (pp. 143-144): the lighthouse can hold "
        "four labs and sanctums, but then cannot serve as a lighthouse. "
        "Two Typical Quality sources give 100 Mythic Pounds each: myrrh "
        "grove and pearl fishery, on unclaimed islands. Any force over "
        "twenty grogs draws notice. An ex-ship captain might be autocrat; "
        "potters make hard white brick with crushed coral.",
    ),
    titled(
        "The fire coral and the fish",
        "The Fire Coral Beds give 6 Vim a year and the Magical School of "
        "Fish 6 Animal a year; both yield 1 pawn every two months or 6 "
        "each year, and a second early harvest in a year cuts both to 3 "
        "until left alone for a year (p. 144).",
    ),
    titled(
        "The storm flotsam",
        "Storm Flotsam gives 3 Perdo vis twice a year with the first "
        "spring and first autumn storm, in the wreckage under the docks "
        "(p. 144).",
    ),
    titled(
        "The sultan of Dahlek",
        "The sultan of Dahlek would blackmail the magi into helping seize "
        "Adulis, but might sell safe passage of the Bab-el-Mandeb for an "
        "elephant and regular fodder (p. 144).",
    ),
    titled(
        "The bishop and the governor",
        "The bishop may urge the governor to attack; with the bishop "
        "discredited or replaced, the governor may accept them for aid in "
        "need and regular gifts, which other magi might frown on (p. "
        "144).",
    ),
    titled(
        "Storyguide Notes",
        "Hooks: Dwindling Resources (Minor Resources; pearl beds poached "
        "by fishermen of Adulis or Dahlek, or a jinn who finds them "
        "delicious); Linked Vis Sources (Minor Resources); Poorly "
        "Defensible (Minor Site); Regio (Minor Site); Road (Minor Site); "
        "Tribunal Border (Major External Relations); Urban (Minor Site). "
        "Boons: Healthy Feature (Minor Site; harbor breezes, +1 to Aging "
        "Rolls for residents most of the year); Important Building (Minor "
        "Fortification; the lighthouse); Secondary Income (Minor "
        "Resources; myrrh); Unwitting Defenders (Minor External "
        "Relations); Sailors (Free Resident). The book counts four Boons "
        "and nine Hooks (pp. 141-142). It suggests minor Uncontrolled "
        "Portal, or major Monster, Ceto bursting up through the docks in "
        "storms (p. 142).\n\nLinked Vis Site (Major/Minor Resources Hook, "
        "pp. 142-143): two or more sources of four pawns or more depend "
        "on one condition. If it fails their rates halve in the first "
        "year, quarter in the second and then stop; a story restarts "
        "them, over three years. The book's example is bees of 6 Animal "
        "and wildflowers of 4 Herbam in Iberia. Major links four sites; "
        "permanent damage counts as two.\n\nUnwitting Defenders "
        "(Major/Minor Resources Boon, p. 143; listed as External "
        "Relations on p. 142): a force unaware of the covenant keeps "
        "bandits and pirates off. Revealing the covenant turns it into "
        "Local or Powerful Ally, or Rival or Unsafe. Major means a force "
        "that can stand a siege, paid for in taxes.\n\nResources: magical "
        "light in the lighthouse costs -5 to lab work unless the magus is "
        "Blind, until a story or project cures it.\n\nVis (p. 144): Fire "
        "Coral Beds, 30 points; Magical School of Fish, 30 points; Storm "
        "Flotsam, 30 points.\n\nStory themes (p. 144): discovery and "
        "exploration from a base open to Egypt, Ethiopia, the Levant "
        "Tribunal and Arabia, and more distantly the Great Desert, Nubia "
        "and Soqotra, by way of Yemeni merchants. Christian magi may "
        "struggle to get books; Muslim magi are nearer the Levant and "
        "Arabia.",
    ),
]


def _adulis(b: Builder, p: Places) -> None:
    site = p["adulis_site"] = b.place(
        "The Village South of Adulis",
        aura=3,
        inside=p["adulis_town"],
        summary=paragraphs(
            "A fishing village on the open shore south of Adulis, rebuilt "
            "after the dragon Ceto destroyed it in antiquity. Its people are "
            "sailors and fishermen, handy with simple weapons, and go to "
            "church in town. Cool harbor breezes keep off sickness, and the "
            "country is dry but pleasant, with room for a few goats and camels "
            "and sloops at the docks.",
            "An old stone lighthouse stands at the village's edge, overlooking "
            "the small deep harbor. The villagers have kept quiet about a "
            "hidden copse of myrrh on a nearby island's slopes and pearl beds "
            "in the cove of another.",
        ),
        secrets=ADULIS_SECRETS,
    )
    p["cetos_well"] = b.place(
        "Ceto's Well",
        inside=site,
        status="Rumoured",
        known="Locally",
        tethers="Opens on the anniversary of the dragon's attack and in great storms.",
        levels=[
            Builder.level(f"Level {n}", 0, notes="The book prints no aura here.")
            for n in (1, 2)
        ]
        + [
            Builder.level(
                "Level 3",
                0,
                notes="The book prints no aura here. It leads to a part of the "
                "Magic Realm much like the Ionian Sea.",
            )
        ],
        summary=(
            "The deep harbor where the great sea monster dived and destroyed "
            "the old village. A ridge of ruby-red fire coral grows on its "
            "northeast rim, among fish twice the common size, and fishermen "
            "of Adulis eye both in hard times."
        ),
        secrets=[
            titled(
                "What lies in Ceto's Well",
                "Ceto's Well is a three-level regio opening to the Magic Realm, "
                "likely tied to the myth of Perseus and Andromeda, and outside a "
                "likely Aegis (pp. 141-142).",
            ),
        ],
    )
    b.link(p["ethiopia"], "places", p["cetos_well"], "Ceto's old hunting ground")
    captain = b.magus(
        "Zerezghi Senai",
        covenant=None,
        house="",
        age=35,
        type="companion",
        summary=(
            "A wiry, one-eyed ship captain of a long line, dour and oddly "
            "alluring, in fine cloth and with a good axe, barefoot aboard. He "
            "dreams of passing the Bab-el-Mandeb to see the sights his "
            "grandfather described, has a taste for Yemeni qat, and leaves "
            "pining lovers and jealous husbands in every port. Nobody doubts "
            "his skill, but strange superstitions bind him."
        ),
    )
    b.stats(
        captain,
        {
            "characteristics": characteristics(2, 1, 1, 2, 1, 2, 1, 0),
            "confidence": (1, 3),
            "virtues_flaws": [
                "Merchant",
                ("Ways of the {land}", {"land": "Sea"}),
                "Improved Characteristics",
                "Improved Characteristics",
                "Inspirational",
                "Warrior",
                "Well-Traveled",
                "Curse of Venus",
                ("Driven (Major)", {"detail": "Going beyond Bab-el-Mandeb"}),
                ("Delusion", {"detail": "Sailor's Superstitions"}),
                "Missing Eye",
            ],
            "abilities": [
                ("Living Language: Amharic", 5, "Tigray"),
                ("Living Language: Arabic", 4, "Yemeni"),
                ("Area Lore: Red Sea", 2, "ports"),
                ("Athletics", 2, "climbing"),
                ("Awareness", 3, "detecting ambushes"),
                ("Bargain", 3, "negotiating sales"),
                ("Brawl", 3, "dodge"),
                ("Carouse", 2, "gambling"),
                ("Charm", 3, "first impressions"),
                ("Dead Language: Ge'ez", 1, "liturgy"),
                ("Folk Ken", 3, "magi"),
                ("Guile", 3, "lying to authority"),
                ("Leadership", 4, "directing crews"),
                ("Legerdemain", 3, "tying knots"),
                ("Music", 2, "working songs"),
                ("Profession: Navigator", 4, "fishing vessels"),
                ("Profession: Sailor", 4, "fishing vessels"),
                ("Organization Lore: Covenant of the Adulis", 1, "personalities"),
                ("Single Weapon", 4, "axe"),
                ("Stealth", 1, "at night"),
                ("Survival", 3, "finding drinking water"),
                ("Swim", 3, "underwater diving"),
            ],
            "traits": {"Outgoing": 3, "Superstitious": 3, "Brave": 2},
            "reputations": {
                "Capable Captain (Adulis)": 3,
                "A handsome scoundrel (Red Sea Ports)": 2,
            },
            "notes": paragraphs(
                "Printed on p. 141. Combat: Dodge Init 0, Def +4; Fist Init 0, Atk "
                "+4, Def +3, Dam +1; Kick Init -1, Atk +4, Def +2, Dam +4; "
                "Bludgeon Init 0, Atk +4, Def +3, Dam +4; Axe Init +1, Atk +10, Def "
                "+5, Dam +7. Soak +4. Encumbrance 1 (4).",
                "Equipment: navigator's tools, pack, leather armor, axe. His ship "
                "is quick and well kept.",
            ),
        },
        source=SOURCE,
    )
    sailor = b.magus(
        "Ammanuel Alazar",
        covenant=None,
        house="",
        age=22,
        type="grog",
        summary=(
            "A well-travelled young fishing crewman, quick to smile, in light "
            "linen with a leather breastplate and a heavy boarding axe, his "
            "hair wrapped. He is no veteran, but he can fight and is loyal to "
            "his crewmates. He could pass in a Yemeni port; further north his "
            "dark skin stands out."
        ),
    )
    b.stats(
        sailor,
        {
            "characteristics": characteristics(0, 1, 0, 0, 1, 1, 2, 1),
            "virtues_flaws": [
                "Covenfolk",
                "Warrior",
                "Well-Traveled",
                ("Delusion", {"detail": "Sailor's Superstitions"}),
                "Temperate",
            ],
            "abilities": [
                ("Living Language: Amharic", 5, "Tigray"),
                ("Living Language: Arabic", 4, "Yemeni"),
                ("Area Lore: Red Sea", 2, "ports"),
                ("Athletics", 3, "climbing"),
                ("Awareness", 2, "on watch"),
                ("Bargain", 2, "negotiating pay"),
                ("Brawl", 3, "dodge"),
                ("Carouse", 1, "gambling"),
                ("Charm", 2, "young women"),
                ("Legerdemain", 3, "tying knots"),
                ("Profession: Sailor", 4, "fishing vessels"),
                ("Folk Ken", 2, "magi"),
                ("Guile", 2, "lying to fathers"),
                ("Music", 2, "working songs"),
                ("Single Weapon", 4, "axe"),
                ("Stealth", 2, "at night"),
                ("Swim", 3, "underwater diving"),
                ("Survival", 1, "at sea"),
            ],
            "traits": {"Loyal": 2, "Superstitious": 2},
            "notes": paragraphs(
                "Printed on p. 142. The book gives his Flaw as Delusion or Fear "
                "(Sailor's Superstitions). Combat: Dodge Init +1, Def +5; Fist "
                "Init +1, Atk +5, Def +4, Dam +1; Kick Init 0, Atk +5, Def +4, Dam "
                "+4; Axe Init +2, Atk +11, Def +6, Dam +7. Soak +4. Encumbrance 1 "
                "(4).",
                "Equipment: pack, leather armor, axe.",
            ),
        },
        source=SOURCE,
    )
    for character in (captain, sailor):
        b.link(character, "places", site, "Sails from here")


# -- stories --


def _ethiopian_stories(b: Builder, p: Places) -> None:
    _seed(
        b,
        "The Great Sea Serpent",
        p["cetos_well"],
        "Ceto breaks ships that skip the sailors' sacrifices, near shore and "
        "among merchants, so that survivors spread its legend. Magi who bloody "
        "its nose become the rival it has wanted.",
        antagonist="The Dragon Ceto, playing the great rival",
        realm="Faerie",
        stages=[
            S(
                "It takes offence",
                at=1,
                clues="The magi save a ship or drive it off.",
                ignored="It hunts their allied ships and spares their own, "
                "earning them an unlucky name in every port.",
            ),
            S(
                "The rival revealed",
                at=2,
                clues="It hides its flight until the moment is best.",
                ignored="It may even defend the covenant's waters: only it may "
                "choose when the magi are destroyed.",
            ),
            S(
                "The last battle",
                at=3,
                clues="They begin to treat it as a mere hazard.",
                ignored="It forces a fight in which it 'dies' or destroys them.",
            ),
        ],
    )
    _seed(
        b,
        "The Trees Listen",
        p["ethiopia"],
        "If the Divine aura lives in the church forests, can it be moved with "
        "the trees? What of their wood, carved into items, or used to imprison "
        "demons or stunt a magus? Might such trees exist for other Realms?",
    )
    _seed(
        b,
        "The Birthright of Solomon",
        p["tana"],
        "Menelik gave the Ark into the care of the Kahens, priests of the "
        "firstborn, and they kept his ring, one of Solomon's, with a seal. Its "
        "hiding place was lost among Tana's islands and monasteries. Finding it "
        "could fill the years of any magus curious about Theurgy or Ars Notoria.",
        secrets=[
            titled(
                "The Kahen's ghost",
                "If Solomon's ring lies with an unburied Kahen, the ghost could "
                "speak of the Ark's powers against unbelievers and of old sites "
                "in Ethiopia, to one who has Ge'ez or Hebrew at 4 (p. 112).",
            ),
        ],
    )
    _seed(
        b,
        "The Devil's in the Trees",
        p["red_sea_stands"],
        "A lesser false god demon raises or transplants myrrh stands near the "
        "covenant and shows them to villagers, merchants, nobles and covenfolk "
        "alike, feeding greed and murder, then works its way among the grogs "
        "toward the magi. Bloodshed brings inquiries, tangles with local rulers "
        "and perhaps a Quaesitor, above all if a Levant covenant is in the "
        "myrrh trade.",
        antagonist="A lesser false god demon",
        realm="Infernal",
    )
    _seed(
        b,
        "Discarded Directive",
        p["zeila"],
        "When 'Amr ibn al-'As came for Ruqayyah's party, Jafar's Qur'an moved "
        "Armah to tears and the emperor refused to give them up. At his death "
        "the Prophet told his people to leave the Abyssinians in peace unless "
        "they attacked, and the sultanates have kept to that. A cabal of demons "
        "could wear away the sultans' respect for those words while goading "
        "the Ethiopian lords to aggression.",
        antagonist="A cabal of demons",
        realm="Infernal",
    )
    _seed(
        b,
        "On a Wing",
        p["ethiopia"],
        "A covenant might grow rich on bridges or short-flight items, drawing "
        "rivals who seize a bridge for tolls or ambush its agent for the "
        "device, while word of the magi's methods spreads.",
    )
    _seed(
        b,
        "Serpents of Unknown Provenance",
        p["ethiopia"],
        "An ambitious magus seeks an elephant-eating serpent as a familiar, "
        "seeing magic in the Order's snakes. They may be fallen sacred snakes of "
        "the pharaohs, spawn of Jormungandr, or children of Eden's serpent. "
        "Missing cattle or grogs might start it, for they eat more than "
        "elephants.",
    )
    _seed(
        b,
        "The Lost Temple",
        p["tana"],
        "The ruin on Tana Qirqos can show where the Holy of Holies lay at Jerusalem.",
        secrets=[
            titled(
                "The nephilim's regio",
                "Where the Holy of Holies lay may lead to a Divine regio made by "
                "Solomon and peopled by nephilim, or the temple on Tana Qirqos "
                "may be another door to it, joining Ethiopia and the Levant (p. "
                "119).",
            ),
            titled(
                "The nephilim",
                "The nephilim knew the Ark, may have studied Ars Notoria or "
                "Kabbalah with Solomon, and might help recover the Ark or fight "
                "demons (p. 119).",
            ),
            titled(
                "Storyguide Notes",
                "Students of Hermetic Architecture may want the ruins too (p. 119).",
            ),
        ],
    )
    _seed(
        b,
        "Beyond the Sultanates",
        p["mountains_of_the_moon"],
        "South past the sultanates, through heat, poison and pagans, hyenas, "
        "lions and elephant-eating serpents, stand the Mountains of the Moon. "
        "Beyond may be the rim of Creation described by Diogenes, Eden, or a way "
        "to Arcadia or Paradise.",
    )
    _seed(
        b,
        "The Nascent Saint",
        p["shewa"],
        "Pagan raiders from beyond the Jamma carry off the mother of young "
        "Takle Haymanot to wed one of their lords. Her return will prove the "
        "archangel's care.",
        secrets=[
            titled(
                "The young man",
                "A young man attends the sleeping Takle Haymanot, calls magi by "
                "their birth names, ignores the Aegis and vanishes: Michael (p. "
                "121).",
            ),
            titled(
                "Storyguide Notes",
                "A devout magus, or one with a Divine Ghostly Warder or Guardian "
                "Angel, may act as his instrument (p. 121).",
            ),
        ],
    )


def _roha_stories(b: Builder, p: Places) -> None:
    _seed(
        b,
        "A Temple in Africa",
        p["roha"],
        "A few Knights Templar in Cairo came home with Lalibela in 1187, hoping "
        "for a second base against the Levant. They fought for him against "
        "Kedus Harbe, and are now his secret allies, gathering knights in his "
        "cavalry and influence at his court.",
        secrets=[
            titled(
                "What the Templars may do",
                "Finding a covenant, the Templars may seek alliance, destroy it, "
                "or steer it (p. 118).",
            ),
            titled(
                "Storyguide Notes",
                "The storyguide sets whether the Order is Divine, Infernal or "
                "mundane (p. 118).",
            ),
        ],
        antagonist="The Templars of Ethiopia",
    )
    _seed(
        b,
        "The Angel's Share",
        p["maryam_tsion"],
        "The Ark would make the Templars independent of the pope, perhaps a "
        "nation. Letters come with the patriarch's couriers, and in 1219 one "
        "told of the Fifth Crusade at Damietta. The knights are near sixty, "
        "their sergeants near fifty. It is now or never.",
        antagonist="The Templars of Ethiopia",
        moves="Fixed dates",
        stages=[
            S(
                "The knights move",
                year=1220,
                clues="They trick or enlist the magi, or arrange a double-cross.",
                ignored="They take the Ark from Maryam Tsion.",
                stopped="The magi might swap in a replica, an elaborate heist "
                "with no blood spilled.",
            ),
            S(
                "The race north",
                clues="A long overland chase to the crusaders at Damietta.",
                ignored="The Ark reaches the army.",
            ),
            S(
                "The march on Cairo",
                year=1221,
                season="Summer",
                clues="The crusaders advance in July.",
                ignored="With the Ark the attack may not fail.",
            ),
        ],
    )
    _seed(
        b,
        "How Many Angels Dance",
        p["roha"],
        "Angels may still keep Roha's niches and gates, and appear to those at "
        "prayer or walk in human form, asking favours of the faithful, from "
        "feeding a senile anchorite to recovering captives from pagans. They do "
        "not always know the greater purpose.",
        secrets=[
            titled(
                "The angels and the Ark",
                "If the Templars go for the Ark, the angels may guide the magi to "
                "help or stop them: God let it leave Jerusalem once, and may want "
                "it moved, or kept (p. 118).",
            ),
        ],
        realm=DIVINE,
    )
    _seed(
        b,
        "For the Love of...",
        p["roha"],
        "One of Roha's angels has fallen in love with a mortal worshipper. "
        "Fearing the sin of the nephilim, the others will not act themselves, "
        "but press the characters to take the mortal far away, even on a "
        "dangerous mission to Egypt or across the Great Desert.",
        secrets=[
            titled(
                "The angel's desperation",
                "Desperate, the angel may urge a grog to kill the mortal (p. 118).",
            ),
            titled(
                "Storyguide Notes", "It may all be a test of the characters (p. 118)."
            ),
        ],
        realm=DIVINE,
    )


def _succession_stories(b: Builder, p: Places) -> None:
    _seed(
        b,
        "The Zagwe Succession",
        p["roha"],
        "Who follows Lalibela, his cousin Na'akueto La'ab or his son Yetbarak?",
        antagonist="Na'akueto La'ab",
        moves="Fixed dates",
        stages=[
            S(
                "Lalibela abdicates",
                year=1229,
                clues="If history holds, he yields to Na'akueto La'ab to retire "
                "as a monk at Roha.",
                ignored="War comes between Na'akueto La'ab and Yetbarak.",
            ),
            S(
                "Yetbarak's victory",
                clues="Lalibela returns to help his son win.",
            ),
            S(
                "The Solomonic overthrow",
                year=1270,
                clues="The Solomonic dynasty overthrows Yetbarak.",
            ),
        ],
    )
    _seed(
        b,
        "The Vacant Throne of Alexandria",
        p["ethiopia"],
        "The patriarchate stands empty, Cyril ibn Laqlaq and his foes at "
        "deadlock, with Abuna Yeshaq the Church's only head in Ethiopia.",
        moves="Fixed dates",
        stages=[
            S("Abuna Yeshaq dies", year=1225, clues="If history holds."),
            S(
                "A patriarch and an abuna",
                year=1235,
                clues="If history holds, ibn Laqlaq becomes Cyril III and "
                "Giyorgis II becomes abuna, serving until 1284.",
            ),
            S(
                "Takle Haymanot",
                year=1284,
                clues="If history holds, the saint becomes abuna at 69.",
            ),
        ],
    )


def _site_stories(b: Builder, p: Places) -> None:
    siwa, ikhmindi = p["siwa"], p["ikhmindi"]
    for name, place, text, hidden in (
        (
            "Sometime Lords of Siwa",
            siwa,
            "Bedouin raiders carry off villagers as the magi arrive, and the "
            "elders offer a bargain for their kin's return and future "
            "protection. These raiders have a patron, a sahir or a bloodthirsty "
            "demon, and the captives must be found before it claims them. It "
            "need not die, and may trouble the covenant for years.",
            "",
        ),
        (
            "Locating Laboratories",
            siwa,
            "Old ghosts, desert spirits or bound jinn hold the rooms once used "
            "by hierophants and sahirs, and want some service, such as finding "
            "a lost idol or restoring a rite, before they accept a new tenant. "
            "Left unharmed they may augment a lab, guard it or assist in it.",
            "",
        ),
        (
            "A Turb From Without",
            siwa,
            "To spare the zaggalah, the magi hire Zenata tribesmen, who must be "
            "paid and kept busy. Bored, they raid caravans, and that draws "
            "Cairo's eye. Most such stories start with their reckless members "
            "in trouble.",
            "",
        ),
        (
            "Filling the Coffers",
            siwa,
            "The elders know the oasis's tales of strange places, and hence its "
            "vis, but the magi must earn them, by Mentem trickery, bartered "
            "luxuries from Cairo or proof they respect Siwan ways. Finding the "
            "sites alone takes seasons and teaches the land, but wins no friends.",
            "",
        ),
        (
            "The Turb From Within",
            siwa,
            "The zaggalah know outsiders and want adventure. Stories, a shared "
            "retributive raid or the chance to come home rich might win them, "
            "with proof of power and of real care for them. Many of them keep "
            "open same-sex partnerships alongside marriage, so a death abroad "
            "can drive a lover to despair or wild courage.",
            "",
        ),
        (
            "The Crusaders Come Calling",
            siwa,
            "In a saga where the Fifth Crusade will not sit in Damietta until "
            "1221, it sends a force to Siwa for supplies and a new front against "
            "Sultan Al-Kamil. Its size, cunning and Divine protection decide "
            "whether this is one rout or a long struggle for the covenant.",
            "",
        ),
        (
            "Getting Slaves",
            ikhmindi,
            "Buying grogs makes the covenant look rich, bringing raiders, "
            "bandits and tax demands. Freeing slaves from Nubian, Berber or "
            "Bedouin slavers is riskier: many flee, some serve in thanks, and "
            "frequent attacks bring better armed expeditions, perhaps with "
            "supernatural aid.",
            "",
        ),
        (
            "New Landlords",
            ikhmindi,
            "The eparch of Nobatia owes the sultan under the Baqt. Arriving with "
            "his tax collectors, the magi might take on the town's debt and "
            "deliver it, and be made its governors in return for gold or "
            "slaves. A visiting Quaesitor may be less forgiving.",
            [
                titled(
                    "The eparch's protection",
                    "The eparch ranks as a metropolitan and likely has strong Magic "
                    "Resistance from Commanding Presence (RoP:D p. 42) or a relic, "
                    "and Divine agents (p. 134).",
                ),
            ],
        ),
        (
            "The Past of a Slave",
            ikhmindi,
            "A lot of slaves hides a general or tribal prince, who may rebel, or "
            "lead the magi on an adventure if they take him home. Or it holds "
            "cutthroats waiting to signal friends to the gates.",
            "",
        ),
        (
            "The Bedouin Storm",
            ikhmindi,
            "Two strong Bedouin tribes demand surrender and tribute. They know "
            "about the well, and want water, then camp fees, word of weak "
            "caravans, wives or slaves. Each competes with the other, so neither "
            "will take less than submission.",
            "",
        ),
        (
            "Lost Tombs and Treasures",
            ikhmindi,
            "A saga of unsealing the pharaohs' caches along the Nile, against "
            "tomb guardians, spirits and bound beasts, rival groups and eremites "
            "or expeditions of magi, with races out of closing tomb-regiones, "
            "fights for shelter from storms, and trips to Mythic Europe to sell "
            "the prizes.",
            "",
        ),
    ):
        _seed(b, name, place, text, secrets=hidden)


def _adulis_stories(b: Builder, p: Places) -> None:
    site = p["adulis_site"]
    for name, place, text, hidden in (
        (
            "Any Port...",
            site,
            "After a terrible storm the magi find the village wrecked, with only "
            "the lighthouse standing. Perhaps a greedy merchant or zealous "
            "missionary wants it finished off. The elders offer service, sailors "
            "and the lighthouse in return for help. The lighthouse is rumoured "
            "unsound, and the magi must keep up the lie or win legal title from "
            "the governor.",
            "",
        ),
        (
            "Free at Last",
            p["adulis_town"],
            "European crusaders taken in Egypt are for sale here, and a merchant "
            "means to set them to work on the mosques at Massawa. Outbidding him "
            "draws the bishop's eye and his hopes of tithes. Stealing them means "
            "facing the mosque's Divine aura and devout guards. Those freed may "
            "join the covenant.",
            "",
        ),
        (
            "Shipwreck of a Different Color",
            site,
            "A wreck limps to the docks at dawn. It might carry crusaders with "
            "vengeful pursuers close behind; faerie sailors eager to act out a "
            "rescue, for a price; or a dying envoy seeking contact between the "
            "abuna and Mediterranean Christians, with his message intact and his "
            "guards stranded.",
            "",
        ),
        (
            "Vis from Beyond",
            p["cetos_well"],
            "A local Christian woman died saving the village from Ceto. Her "
            "bones lie unspoiled in the fire coral, venerated but unrecognized by "
            "the Church.",
            [
                titled(
                    "The bones and the vis",
                    "The woman's bones hold a Faith point, and no vis can be gathered "
                    "while they lie there (p. 139).",
                ),
                titled(
                    "Moving the bones",
                    "Whoever moves the woman's bones has dreams, and her spirit "
                    "promises the vis sites' secrets once they reach the bishop in "
                    "Adulis, if the magi can manage that unnoticed (p. 139).",
                ),
            ],
        ),
    ):
        _seed(b, name, place, text, secrets=hidden)
