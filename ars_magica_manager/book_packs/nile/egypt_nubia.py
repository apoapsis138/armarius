"""Egypt and Nubia as of 1220: Lands of the Nile chapters VI and VII (pp. 57-102), including the Cult of Dedun's people and places. A summary of the book, not its words.

Names shared with The Cradle and the Crescent and Blood and Sand are kept exactly so that they match on import: "Egypt", "Cairo", "Alexandria", "Damietta", "The Coptic Church", "The Papal Legate", "Ayyubid Sultan of Egypt" and "The Fifth Crusade". The Great Hunger and the Hope are book_packs.hunger's; along the Nile they are the Red and the Black, and they are named here in words. The rules for the Cult of Dedun, Corpse Magic, Kassalan Exorcism, Soban Alchemy and the Blemmyae are the tradition catalog's and rules/africa.py's, cited by page."""

from __future__ import annotations

from typing import Any

from ...models import Neighbour
from ...rules import egyptian_tombs as et
from ...tombs import TombCurse, TombTrap, TombWard
from ..builder import (
    Builder,
    characteristics,
    dormant,
    paragraphs,
    vf_ability,
    vf_minor,
)

World = dict[str, Neighbour]

REGION = "In the region"
LOCAL = "Locally"
#: A place people talk about but cannot find.
RUMOUR: dict[str, Any] = {"status": "Rumoured", "known": REGION}
MONASTERY = "Monastery or nunnery"
SEE = "Bishop's cathedral"
MOSQUE = "Large urban church"
SAHIRS = "trad_sahirs"
LEARNED = "trad_learned_magicians"
DEDUN = "trad_cult_of_dedun"
EXORCISTS = "trad_kassalan_exorcists"
ALCHEMISTS = "trad_soban_alchemists"
DATED = "Fixed dates"


def build(b: Builder) -> None:
    w: World = {}
    _egypt(b, w)
    _cairo(b, w)
    _cairo_buildings(b, w)
    _gizeh(b, w)
    _alexandria(b, w)
    _crusade(b, w)
    _south_of_cairo(b, w)
    _egypt_seeds(b, w)
    _gizeh_seeds(b, w)
    _crusade_seeds(b, w)
    _upper_egypt_seeds(b, w)
    _nubia(b, w)
    _nubian_powers(b, w)
    _nobatia(b, w)
    _nobatian_towns(b, w)
    _makuria(b, w)
    _dju_waab(b, w)
    _dongola(b, w)
    _darfur(b, w)
    _alodia(b, w)
    _alodian_kingdoms(b, w)
    _meroe(b, w)
    _soba(b, w)
    _blemmyae(b, w)
    _cult_of_dedun(b, w)
    _artanyeszame(b, w)
    _pyramid(b, w)
    _hamad(b, w)
    _ababdah(b, w)
    _scorpion_fish(b, w)
    _nubia_seeds(b, w)
    _dedun_seeds(b, w)


def _place(b: Builder, name: str, **kw: Any) -> Neighbour:
    """A place known across the region unless `known` says otherwise."""
    kw.setdefault("known", REGION)
    return b.place(name, **kw)


def _seed(
    b: Builder,
    name: str,
    *parts: str,
    where: Neighbour,
    secrets: str = "",
    antagonist: str = "",
    realm: str = "",
    stages: list[dict[str, Any]] | None = None,
) -> Neighbour:
    """A story seed: a threat that waits until the storyguide begins it."""
    return dormant(
        b.threat(
            name,
            summary=paragraphs(*parts),
            secrets=secrets,
            antagonist=antagonist,
            realm=realm,
            place=where,
            stages=stages,
        )
    )


# -- Egypt --


def _egypt(b: Builder, w: World) -> None:
    w["egypt"] = _place(
        b,
        "Egypt",
        summary=paragraphs(
            "An old land whose great cities are young: Cairo, Damietta and Qus "
            "have held their present size and standing for only a few decades. "
            "Ancient landmarks stand among new suburbs, and a nobleman of "
            "today may have been a street thief or hired sword in his youth.",
            "Most Egyptians live along the Nile and live by farming it. Under "
            "the iqta' the sultan parcels out his land by contract to powerful "
            "supporters, who owe him soldiers and taxes for the right to its "
            "produce. The grants are not hereditary, so that no noble can "
            "build a regional power: the whole class of landholders (muqta's) "
            "used to be moved on a timetable, until the rich threatened "
            "revolt, and now a family moves when its head dies. Each year "
            "after the flood a muqta's servant visits every village, measures "
            "how high the water came, grades the land, and gives out fields by "
            "witnessed written contract, usually with a loan of seed, tools or "
            "money and a stated return at harvest. Most contracts go to "
            "settled farmers; itinerant ones get land the flood does not "
            "usually reach, or work a new crop such as sugar cane. Village "
            "headmen answer for the contracts. The nobles move and the farmers "
            "have no tie to one piece of land, so a European covenant's "
            "familiar tricks, such as a tame nobleman, serve poorly here (pp. "
            "69-70).",
            "The farming year, in European months (p. 70). September: quince, "
            "winter grapes and dates picked, citrus begins, balsam tapped, "
            "canals opened, loan seed given out. October: rice harvested, "
            "trefoil and turnips planted, myrtle and nenuphar pressed for oil, "
            "the Nile at its height. November: wallflower, violet, narcissus "
            "and horseradish harvested, flax fields drained and sown. "
            "December: second-year cane cut and pressed, with narcissus, "
            "carrots, citrus, green broad beans and white leeks; trefoil sown. "
            "January: young cane cut, trees moved, cane waterwheels set up, "
            "fields weeded and ploughed, dykes breached. February: almonds, "
            "grapes, lotus fruit and turnips harvested, more ploughing, summer "
            "crops planted. March: broad beans, lentils and flax bought, "
            "African ships sail for the Mediterranean ports, summer crops "
            "tended, cane planted in long-fallow fields. April: broad beans, "
            "barley, cereals, cucumbers and roses harvested, flax seed "
            "threshed. May: balsam, sesame and rice sown, crops threshed. "
            "June: figs, peaches, pears, prunes, mulberries, dates and sour "
            "grapes harvested, flax soaked, indigo planted (ready in a hundred "
            "days), honey gathered; on the 18th the Festival of Saint Michael, "
            "when the Nile begins to rise. July: flax drained and dried. "
            "August: unripe dates harvested.",
            "Trade from every quarter brings new crops, which are quickly "
            "taken up. Summer crops: cabbage, caraway, cotton, cumin, "
            "eggplant, green beans, indigo, lettuce, melons, Nile sesame, "
            "onion, radishes, sesame, sugar cane, taro and turnips. Winter "
            "crops: barley, broad beans, chickpeas, flax, garlic, grass peas, "
            "lentils, lupine, onions, trefoil and wheat.",
            "Sugar cane is new here and still rare. It needs long-fallow land "
            "and great quantities of water and is hard to press, but Europeans "
            "pay fortunes for it, treating it as a spice, and if history holds "
            "it will spread across parts of the south (p. 69).",
            "Auras (p. 57). Dominion: up to 10 at the holiest places and "
            "pilgrim sites; usually 4 at places of worship, 3 at the "
            "cemeteries and homes of People of the Book, 2 where monotheists "
            "work, and 1 where the call to prayer carries. Faerie: the Might "
            "of the area's strongest faerie divided by 5, or higher where two "
            "contest it; that faerie need not be the strongest the characters "
            "meet. Magic: at awesome natural places and tethered to human "
            "works, many old tombs among them (Tomb Creation, chapter 4). "
            "Infernal: usually small pockets the Dominion wears away, but "
            "places given over to sin can hold strong and seemingly permanent "
            "ones, such as the old customs house at 'Aydhab.",
        ),
    )
    w["nile"] = _place(
        b,
        "The Nile",
        inside=w["egypt"],
        summary=paragraphs(
            "Mythic Earth's greatest river. It rises in the Atlas, runs south "
            "through the desert to the edge of the habitable world, turns east "
            "through the lands of the Plinian races, and turns north again "
            "near Africa's east coast, through the lands of gold and black "
            "men. It floods Egypt yearly, leaving soil of almost magical "
            "fertility, and falls into the Mediterranean.",
            "Even small European creeks may have elementals; the Nile's spirit "
            "is so vast it must make avatars or invest emissaries for people "
            "to understand it at all. The Copts call it Kheme, the Black, "
            "their word also for the colour and for Egypt. Elsewhere it is "
            "called the Hope. It is not Isis, the river's faerie goddess, "
            "though she perhaps served it and fed on its vitality. The "
            "Blemmyae of Philae, once her worshippers, often act for it; in "
            "the west of Africa a tribe of seven-headed rain serpents serves "
            "it, their shape perhaps mirroring its seven-mouthed delta; in "
            "Egypt it calls up horus-beasts, the ascended dead, Coptic "
            "alchemists, jinn and faeries for its endless war with the Red.",
            "The Red, the Great Hunger, is desiccation and sterility, "
            "strongest at the heart of the Sahara; the Nile's encircling arm "
            "keeps its appetite from eating Africa. Its servants, detailed in "
            "Between Sand and Sea, include hedge magi fed by the decay of the "
            "land, set beasts, tribes of werehyenas and great afrits of "
            "smokeless flame. Some say every lie adds a grain to the Sahara "
            "and every liar serves the Red; others that no one who would "
            "escape the Black's notice should ever drink its water.",
            "The Seven Heads (p. 57). Pliny lists seven mouths, not all of "
            "which can be found in 1220: some are silted, some are not where "
            "he says. The main one is the Phatmetic Mouth at Damietta, in the "
            "eastern Delta, for decades Egypt's chief port for Nile trade. The "
            "Delta itself is called so after Herodotus, for the letter it "
            "resembles on some maps; the Copts call it Ta-Mehu, Land of the "
            "Papyrus, a name close to the Field of Reeds in Duat (chapter 4), "
            "and many gates to Faerie and the Magic Realm are hidden there (p. "
            "58).",
        ),
        secrets=(
            "The Black has withdrawn some of the silted or missing mouths from "
            "the mortal world; others are coiled back as reflections of wounds "
            "taken from the Red. One, the Pelusiac Mouth, it has hidden as a "
            "safe base for its servants."
        ),
    )
    w["sultan"] = b.lord(
        "Ayyubid Sultan of Egypt",
        title="duke",
        wealth="Wealthy",
        seat="Cairo",
        ruler="al-Kamil Muhammad",
        place=w["egypt"],
        summary=paragraphs(
            "Al-Kamil, vizier of Egypt until the old sultan died soon after "
            "the crusaders landed in 1218, and sultan since. He wants the "
            "Crusade out of Egypt so that he can settle his hold on his own "
            "lands, and has twice offered Jerusalem to be rid of it (see The "
            "Fifth Crusade). After Damietta fell he drew back twenty miles "
            "south to Mansourah, and through the winter of 1219 he has thrown "
            "up defences there and waited for an assault that has not yet come.",
            "So long as the Nile is high the sultan's ability to pay for "
            "things seems all but magical: the House, the Maristans, the tombs "
            "of Qarafah and Alexandria's mosques and bread all rest on it. He "
            "is legally entitled to his land taxes and tributes in any year "
            "the flood reaches full water. It failed in 1219, and with it his "
            "money (pp. 61, 66). Some suspect old Nile magic behind that "
            "purse; the Coptic monks say a failed harvest is explanation "
            "enough.",
        ),
    )
    b.faction(
        "The Mamluks",
        faction="Estate or rank",
        place=w["egypt"],
        summary=(
            "Slave soldiers. Copts may not carry arms, which the rulers "
            "enforce hard: a hadith calls Egyptians the finest soldiers in the "
            "world, and if that means a natural gift for war, an Egyptian "
            "peasant mob is far more dangerous than rebels elsewhere. Coptic "
            "revolts have been put down only with difficulty, so the sultans "
            "take Egyptian children from their Christian parents and raise "
            "them as Muslims and as slave soldiers (p. 59)."
        ),
    )
    b.faction(
        "The Hirranian Sabeans",
        faction="Faith or sect",
        place=w["egypt"],
        summary=(
            "A people the sultan treats as People of the Book, perhaps through "
            "confusion with the Sabians. They say the great statue at Gizeh "
            "shows the god Horon and is the tomb of one of the three great "
            "scholars called Hermes, whom they equate with the Prophet Idris "
            "(Enoch). They bury their dead in urns around it and sacrifice "
            "white roosters to it (p. 64)."
        ),
    )
    b.church(
        "The Coptic Church",
        church="Archbishop's cathedral",
        place=w["egypt"],
        ruler="Vacant since 1216",
        summary=paragraphs(
            "Egypt's Christians fare better than those in most Muslim lands. "
            "Egypt surrendered rather than falling by force, making the Copts "
            "dhimmi and limiting what a ruler may lawfully take; hadiths call "
            "them the Muslims' instruments and help; Ismail's mother and one "
            "of the Prophet's wives were Copts; and the Fatimids were largely "
            "tolerant, as the present dynasty has been. Alexandrian Copts pay "
            "no tax but a compulsory charity for the poor. New churches, "
            "forbidden elsewhere, are often built, the jurists reasoning that "
            "they merely continue old ones. Copts may not ride, but here they "
            "often do, dismounting past the houses of Muslim nobles and legal "
            "officers. They remain third in standing, behind Muslims and new "
            "converts, and may not bear arms (pp. 58-59).",
            "The Coptic Patriarch of Alexandria leads them in a moral sense. "
            "Since the capital moved it has suited him to live in Old Cairo "
            "rather than in his official see. He counts himself custodian of "
            "all Africa's Christians, but distance leaves the Churches in "
            "communion with him very independent, and a Greek rival for the "
            "See of Mark still lives in Alexandria. The finest alchemists in "
            "Egypt, the sultan's household perhaps excepted, are Coptic monks, "
            "and a suspicious number of old monks keep nilometers (pp. 59-60).",
            "The see has been empty since 1216: one priest, Cyril ibn Laqlaq, "
            "has so much wealth and influence that no one else can be elected, "
            "and a core of opponents will not have him (p. 58). If this Mythic "
            "Europe follows history he will be ordained Cyril III in 1235, a "
            "notorious simoniac. The lack of a head weakens the Copts.",
        ),
    )


def _cairo(b: Builder, w: World) -> None:
    w["cairo"] = b.town(
        "Cairo",
        charter="Noble lord",
        ruler="Sultan al-Kamil",
        answers_to=w["sultan"],
        place=w["egypt"],
        summary=paragraphs(
            "The capital of Egypt for just over fifty years, a new and "
            "wonderful city that pilgrims from everywhere praise. Many locals "
            "call it Misr, the Arabic name for all Egypt, held to be the name "
            "of a son of Noah who was the land's first king after the Flood "
            "and whose sons founded its great cities.",
            "Under Saladin and his first successors Fustat and Cairo were "
            "ringed by one wall, which is still being built by countless "
            "Christian slaves, Byzantines for choice, since Egyptians think "
            "them the best builders alive (p. 60).",
            "Plot hook, printed without a name just before the Mosque of Ibn "
            "Tulun: one Cairo mosque stands where Moses duelled Pharaoh's "
            "magicians. See Ancient Works of Magic or Trickery?",
        ),
    )
    w["coptic_cairo"] = _place(
        b,
        "Coptic Cairo",
        inside=w["egypt"],
        summary=(
            "The older quarter around Babylon Fortress, home to a large and "
            "prosperous Coptic community and, for convenience since the "
            "capital moved, to the Patriarch of Alexandria (pp. 58-59)."
        ),
    )
    w["babylon"] = _place(
        b,
        "Babylon Fortress",
        inside=w["coptic_cairo"],
        summary=(
            "A Roman strongpoint in Old Cairo. From here, it can be argued, "
            "the Empire left Egypt and handed the land and the Copts into "
            "Islam's keeping (p. 59)."
        ),
    )
    b.church(
        "The Hanging Church",
        church="Archbishop's cathedral",
        place=w["babylon"],
        summary=(
            "The Patriarch of Alexandria's cathedral, set above the gatehouse "
            "of Babylon Fortress (p. 59)."
        ),
    )
    w["fustat"] = _place(
        b,
        "Fustat",
        inside=w["egypt"],
        summary=paragraphs(
            "Egypt's capital until 1168, and one of Mythic Africa's largest "
            "and richest cities. The vizier Shawar had kept Syria and the "
            "Christians at bay by setting them against each other, but when "
            "Amalric of Jerusalem invaded he ordered Fustat emptied and "
            "burned, so that it could not serve as the invaders' base. His men "
            "spent 20,000 naphtha pots and 10,000 lighting bombs on it. The "
            "invasion stalled, and the Syrians then swept in and took Egypt "
            "for themselves (pp. 59-60).",
            "The citizens could not carry away their goods. Many nobles buried "
            "their wealth, or stayed and died in the fire. The hoards still "
            "turn up for treasure hunters, and faeries and demons use them to "
            "tempt and reward people. The single wall has made Fustat part of "
            "the capital, but it was never properly rebuilt: it is where "
            "noxious trades are carried on and waste is dumped (p. 60).",
            "Naphtha pots (p. 59). A pot is a ceramic grenade of petroleum "
            "held in gel. An incendiary pot is a thrown weapon: thick gel "
            "burns for minutes at +10 to what it touches; runnier fuel spreads "
            "a pool at +5 to everything flammable; plain liquid makes a "
            "one-round fireball, +5 less 1 per pace from the pot. An explosive "
            "pot does +10 on a hit, less 1 per foot, mostly by burning, and is "
            "often shaped for siege engines. A lighting bomb is a pot used as "
            "a fuse or to fire thatch, crops and furniture. A poison pot gives "
            "off toxic smoke and bursts only when it hits, good for sabotage "
            "and assassination, and handy against tomb spirits that incense "
            "repels. Veteran Egyptians do not panic at naphtha; untrained "
            "troops, foreign mercenaries and horses may break, and a Brave "
            "roll against 5 stands firm. Metal jackets and fierce blasts are "
            "beyond a bazaar alchemist, and are special items in stories.",
            "Naphtha by magic (p. 59): a processed natural liquid, so Creo "
            "Aquam base 3, the Base Individual a pool a foot across and six "
            "inches deep (about a gallon and a half) whatever the viscosity. "
            "Made outside a container it lights at once.",
        ),
    )


def _cairo_buildings(b: Builder, w: World) -> None:
    w["maristans"] = b.church(
        "The Maristans",
        church=MOSQUE,
        place=w["egypt"],
        answers_to=w["sultan"],
        ruler="The sultan, who pays for them",
        summary=paragraphs(
            "The Cairo Hospital, among the world's finest, a place of "
            "treatment, research and teaching to which students come from far "
            "away. A royal palace given to the sick as charity houses it; the "
            "palace opposite became the women's hospital, and a third building "
            "was raised for the insane (p. 60).",
            "It is a fine place to recover after hard events: besides its "
            "cures it has bath-houses, an excellent library and free lectures "
            "through which patients can improve their Medicine. Alchemists in "
            "the sultan's pay give out basic remedies and pass patients on to "
            "specialists.",
        ),
    )
    b.church(
        "Mosque of Ibn Tulun",
        church=MOSQUE,
        place=w["egypt"],
        summary=(
            "Cairo's oldest mosque and among its finest, built as a private "
            "mosque beside the palace of the governor Ibn Tulun. His capital, "
            "Al-Qatta'i, has been razed, and only this stands while later "
            "capitals grew round it. Over four tons of gold from one "
            "excavation are said to have paid for it. It is kept, on a subsidy "
            "from the sultan, for the free use of students and travellers from "
            "the Maghreb (p. 60)."
        ),
    )
    _place(
        b,
        "The Nilometer of Cairo",
        inside=w["egypt"],
        summary=paragraphs(
            "A white octagonal marble column in a square well near the city, "
            "marked in 22 cubits called fingers: the legally official measure "
            "of the flood, though many keep their own. So many old Coptic "
            "monks keep nilometers that those who think they hold on to "
            "ancient magic call them ritual objects; the monks gently mock the "
            "idea.",
            "At 16 cubits, 'full water', a festival begins and runs for "
            "several days; people are doused with Nile water for luck, a "
            "pharaonic custom oddly like Europe's Feast of Fools. The usual "
            "height is 17. Short of full water, perhaps one year in twenty, "
            "the sultan's purse begins to fail, and sometimes the flood fails "
            "for years on end, with famine in which, as ibn-Jabyr has it, God "
            "is the only hope (pp. 60-61).",
        ),
    )
    w["citadel"] = _place(
        b,
        "Saladin's Citadel",
        inside=w["egypt"],
        summary=paragraphs(
            "The strong point at the centre of Saladin's wall round Old and "
            "New Cairo. Unfinished in 1220, it has been the seat of government "
            "for decades, and the bureaucracy keeps gathering into it. The "
            "sultan lives here (p. 64).",
            "His library is among his countless treasures. Its last great "
            "census, under the Fatimids, counted 600,000 books, 18,000 of them "
            "on magic, astrology and alchemy.",
        ),
    )
    b.faction(
        "The House",
        faction="Council or assembly",
        decides="Its leader",
        place=w["citadel"],
        rules=(
            "Teachers take a Major Personality Flaw of loyalty to the House's "
            "goals, which is not loyalty to the sultan or to its present head. "
            "Children of the House take the Code of Honor Major Flaw."
        ),
        offers="Intense teaching, and agents for the sultan's service.",
        summary=paragraphs(
            "A school, said to lie in the citadel's grounds, that prepares "
            "agents for the sultan's service. It seems to take few students, "
            "perhaps twelve at a time, and no one outside is sure what they "
            "learn. Egypt's finest smith is trained here and kept on to teach "
            "his successor; so is an alchemist, though some Coptic monks might "
            "contest his claim to be the greatest; so are diplomats and, it is "
            "rumoured, assassins. Some think the teaching changes with the "
            "troubles the sultan's advisers foresee (p. 61). It is in effect a "
            "machine for intense teaching, which also trains specialists in "
            "how to teach.",
            "Teacher of the House (Mystery Initiation path, p. 61). The "
            "mystagogue needs Lore of the House, an Organization Lore; its "
            "Ability also covers the House's history, students, missions and "
            "resources. Gifted initiates may have faster paths; most use "
            "these. Good Teacher: Presence + Lore of the House 6, a ritual "
            "Ordeal with items from the ancient House, the Flaw of loyalty; "
            "script +9 for the total of 15. Affinity with Teaching: Presence + "
            "Lore 8; a pilgrimage to find a great and charismatic teacher and "
            "a hard task spreading his message; script +7 (place and time +3, "
            "quest +3, loss of time +1). Improved or Great Communication: "
            "Presence + Lore 8; a rite at an ancient library invoking the "
            "goddess Seshat, whom the initiate must persuade with "
            "Communication + Charm against 12. Failure means being Spirited "
            "Away to keep her library in Faerie until the next solar eclipse "
            "in Egypt, which astrologers can foretell. Success, or escape, "
            "gives 3 Characteristic points for Communication, or the Great "
            "Characteristic Virtue if it is already 3; script +7. Errata p. "
            "14: this path is for the unGifted, who must take an Ordeal at "
            "every Initiation, yet two of these have none; the errata leave it "
            "to the troupe.",
            "Its pupils and agents take the Virtues Child of the House and "
            "Agent of the Sultan (p. 61).",
        ),
        secrets=(
            "Some suggest the House's leaders have undergone, or at least "
            "know, further Initiations meant for the priesthood they descend "
            "from."
        ),
    )
    _place(
        b,
        "Tombs of Qarafah",
        inside=w["egypt"],
        summary=(
            "A wide cemetery of the tombs of the Prophet's relatives and "
            "companions, with four great congregational mosques and many "
            "smaller mosques and theological colleges. The poor, scholars and "
            "travellers are welcome in the smaller mosques, and the sultan "
            "spends a couple of thousand dinars a month on upkeep and on "
            "keeping many of the residents, which pilgrims think a marvel. "
            "Magi count as scholars or travellers, and can live here at his "
            "expense if they like (p. 64)."
        ),
    )


def _gizeh(b: Builder, w: World) -> None:
    w["gizeh"] = _place(
        b,
        "The Gizeh Necropolis",
        inside=w["egypt"],
        summary=paragraphs(
            "Three great pyramids and a colossal lion with a man's head, a "
            "day's travel south of Cairo. Most Egyptians take little interest "
            "in the mastabas and pyramids here, thinking the plateau unusually "
            "dangerous even for a necropolis, and haunted, above all by night "
            "(pp. 62, 64).",
            "Beliefs differ widely. Aristotle lies under one pyramid; the "
            "largest was made for Alexander, who was buried in secret "
            "elsewhere; a pharaoh raised them to save his people's wisdom from "
            "Noah's Flood; Allah, or a false god such as Hermes, made them by "
            "miracle. Saladin's son tried to pull down the pyramid nearest the "
            "statue, and it still shows the damage: he believed, as most do, "
            "that treasure lies everywhere, even where others have already "
            "taken it.",
            "Herodotus and Manetho, widely read in Egypt, give each pyramid "
            "its own occupant. Cheops closed the temples, set all Egypt to "
            "work for ten years, and when money ran short prostituted his "
            "daughter; his brother Chephren ruled the same way. Cheops's son "
            "Mykerinos reopened the temples, judged fairly, and let people go "
            "home to their trades. As Egypt had been cursed to 150 years of "
            "suffering he was working against the gods, who took his only "
            "child and cut his life short. Told he had six years left, he set "
            "about making magical items to slow time (p. 62).",
            "On the highest ground stand statues of marble crocodiles that "
            "keep real crocodiles out of their sight, guarding three miles of "
            "river either way. Some say the Third Hermes himself made them. No "
            "Hermetic magus has assessed them in a laboratory, so what exactly "
            "they do is unknown (p. 62).",
            "Pilgrims widely report that the plateau's sand, the Sand of "
            "Hermes, raises Intelligence if carried as a talisman (p. 62).",
        ),
        secrets=paragraphs(
            "The plateau's greatest guardian is the Lady of the Tombs. "
            "Alexander of Jerbiton's few accounts suggest a potent faerie once "
            "worshipped as Isis, changed as her story has changed. She can "
            "call every faerie in the area and, worst of all, rouse a faerie "
            "variant of the Father of Dread (p. 62).",
            "The effect of the sand may be faeries using Grant Virtue to give "
            "scholars at the tombs Improved Characteristics. They take the "
            "gift back when a scholar stops studying the ruins, so that the "
            "weak can be led to spend their lives on one confected tomb after "
            "another, feeding the faeries' need for attention.",
            "Some say Mykerinos succeeded: his lamps make a room-sized Faerie "
            "regio where time runs slower. No one knows where they are.",
        ),
    )
    _place(
        b,
        "Abu 'l-Ahwa, the Father of Dread",
        inside=w["gizeh"],
        summary=(
            "Abu 'l-Ahwa, the Father of Dread, is the colossal lion with a "
            "man's head. The Greeks call it the "
            "strangler, or sphinx, after the winged female monster of the "
            "Theban Tribunal that strangled those who failed its riddle. Some "
            "think it a solar god. It appeared to Menkheperure (Thutmose IV) "
            "to ask that its statue be dug from the sand, according to a stela "
            "said to stand between its paws. Some call it the grave of the "
            "Prophet Idris, or of Thoth, or both. If it were dug out and rites "
            "could again be held between its paws, answers might come (p. 62)."
        ),
    )
    _place(
        b,
        "The Tomb of Aristotle",
        inside=w["gizeh"],
        summary=(
            "A pilgrimage site for scholars from across what remains of "
            "Alexander's empire. Only about a third of Aristotle's known works "
            "reach Mythic Europe, and those seem to be mostly esoterica: "
            "private musings, lecture notes and letters rather than the "
            "exoteric books meant for publication. Copies of the missing books "
            "may have been buried with him, and it is tempting to dig into the "
            "side of the pyramid; fear of its defences has so far been "
            "stronger (p. 62)."
        ),
        secrets=(
            "A complete recovered set gives great Insight across many projects "
            "and rescales many Abilities: all readers gain +3 on all Artes "
            "Liberales rolls, and others as the books' subjects dictate. "
            "Incomplete sets still give Insight, and serve as books of very "
            "high level in their Abilities."
        ),
    )
    _place(
        b,
        "The Isle of Gold at Gizeh",
        inside=w["gizeh"],
        **RUMOUR,
        summary=(
            "God sank the throne of the pharaoh who abused Moses deep in the "
            "Nile. It is still there, showing in famine years when the river "
            "runs low, and oddly no one has ever tried to raise it (p. 62)."
        ),
    )


def _alexandria(b: Builder, w: World) -> None:
    w["alexandria"] = b.town(
        "Alexandria",
        charter="Noble lord",
        ruler="Sultan al-Kamil, through his governor",
        answers_to=w["sultan"],
        place=w["egypt"],
        summary=paragraphs(
            "An ancient city long faded and now reviving. Since Rome's rule "
            "ended its wealth and prestige have drained to Fustat and Cairo. "
            "Walls rebuilt in the ninth century took in only about half the "
            "old city, and it went on shrinking until Saladin refortified it "
            "in 1181 and founded new suburbs east and south of the walls (p. "
            "65).",
            "The loss of Damietta last year has made it the court's chief port "
            "and the sultan's main fleet base. Pilgrims avoiding Christian "
            "pillage land here and cross to the Nile, and it does not link "
            "directly to the river, so it is the less handy port despite its "
            "fine harbour (pp. 57, 65). The city is full of money and of the "
            "sharp, ambitious and well connected.",
            "Its people pay nothing but the awqaf, a small poll tax, and yet "
            "the sultan pours riches through it. Between 8,000 and 12,000 "
            "mosques are said to stand here, more than in any city on earth, "
            "each with an imam on a 5 dinar stipend. Saladin's custom gives "
            "away 2,000 loaves a day: those who crossed the desert must take "
            "bread, even carrying their weight in gold, and many pass it on to "
            "the poor. While the Nile is high and he is rich, unlikely things "
            "happen in the sultan's name; a storyguide who needs a reason for "
            "almost any practice can say he pays for it (p. 65).",
            "Alexandrians are as busy by night as by day. The port unloads "
            "without stopping, those who feed the workers keep late hours, and "
            "so do their suppliers, until the city barely slows down (p. 63).",
            "It is one of the easier places for outsiders to reach, open to "
            "Iberian and North African pilgrims and to French and Italian "
            "traders, and so a good place to hire eastern-speaking servants "
            "and learn the roads east. Rich people of classical education "
            "wander its ruins with Diodorus or Arrian in hand and a guide at "
            "their elbow; the Jerbiton Itinerarium does not usually come this "
            "far south, but a skilled Jerbiton might bring apprentices (p. 63).",
        ),
        secrets=(
            "No one has noticed that the city's nights make no economic sense. "
            "Lamp oil is why other ports sleep, and there is no satisfactory "
            "explanation for the cheap oil here. Pilgrims think it one of the "
            "sultan's bounties; his servants assume nearby farms make it "
            "cheaply, and do not look, since a tax-free city could grow "
            "diamonds on trees for all the law cares. Across the Mediterranean "
            "the Quaesitores would be looking for a magus making it with Creo. "
            "If a covenant settles in Alexandria they will ask for a full "
            "investigation, and if unsatisfied send Quaesitores and hoplites, "
            "a plain message that Hermetic law now reaches North Africa (p. "
            "63)."
        ),
    )
    w["pharos"] = _place(
        b,
        "The Pharos of Alexandria",
        inside=w["egypt"],
        summary=paragraphs(
            "The Lighthouse, one of the remaining wonders of the world, much "
            "damaged and rebuilt, its tower now short and capped with a "
            "mosque. Some magi claim a strong aura over the whole island; "
            "others say they tested and found none (p. 63).",
            "Its mirror of Serican iron has long been gone. A man staring into "
            "it could pick out ships hours before the naked eye; by night its "
            "fire showed for miles; in war it could burn ships in the harbour. "
            "A Byzantine spy spread tales of treasure in the Pharos, stole the "
            "mirror in the riot that followed and, unable to destroy it, had "
            "it thrown in the sea. Some magi guess that a potent spirit of "
            "artifice defends it.",
            "An inscription to the architect appeared on the side of the tower "
            "only centuries after his death: the masons had carved a "
            "flattering dedication to the king in thin lime plaster over it, "
            "which cracked away.",
        ),
    )
    _place(
        b,
        "The Library of Alexander",
        inside=w["egypt"],
        **RUMOUR,
        summary=(
            "Burned by so many hands that the tales conflict, but many local "
            "tales agree part of it survived. Egyptians remember Cleopatra not "
            "as Rome's seductress but as a scholar and alchemist who took wise "
            "precautions when her kingdom was threatened, and many think her "
            "unfound grave may lead to a secret store of its books. Others say "
            "the land it stood on slid into the sea, and since Egyptians write "
            "by carving stone, magi with suitable spells might read any walls "
            "still standing on the seabed (p. 63)."
        ),
    )
    w["damietta"] = b.town(
        "Damietta",
        charter="Noble lord",
        ruler="The Crusade's leaders, in dispute",
        place=w["egypt"],
        summary=paragraphs(
            "A port in ancient times that lost its trade to Alexandria, kept "
            "some standing as an Arab naval base, and rose again as Fustat "
            "grew, until by the thirteenth century it was the Nile's chief "
            "port (p. 65). Water and a stout chain across the navigable "
            "channel, running from the walls to a small island tower, guarded "
            "its approaches.",
            "Of the 80,000 inside when the siege began in February 1219 only "
            "3,000 were alive when it fell that November, and only 100 of "
            "those healthy (p. 66). The looted city came to the Christians "
            "with its defences whole, and the crusaders hold the sea.",
            "In January 1220 the victors are falling apart. John of Brienne "
            "assumed it would join the Kingdom of Jerusalem; Pelagius says "
            "not, without saying whose it is, and has somehow offended both "
            "crusading orders, who now back John. Crusaders go about in squads "
            "of countrymen for safety, and in the last month some have fought "
            "to the death in the streets. The Italians pushed to force all "
            "Frenchmen out; the orders, who had stayed above what they took "
            "for a squabble over booty, routed the Italians (p. 67).",
        ),
    )
    w["mansourah"] = b.town(
        "Mansourah",
        charter="Noble lord",
        ruler="Sultan al-Kamil",
        answers_to=w["sultan"],
        place=w["egypt"],
        summary=(
            "A military city that has grown up twenty miles south of Damietta "
            "behind a tributary of the Nile, where al-Kamil has retired with "
            "his demoralised army. If it and the army fall, nothing stands "
            "between the crusaders and Cairo (pp. 66-67)."
        ),
    )


def _crusade(b: Builder, w: World) -> None:
    b.church(
        "The Papal Legate",
        church=SEE,
        ruler="Cardinal Pelagius of Albano",
        place=w["damietta"],
        summary=(
            "Cardinal Pelagius, the Pope's representative, de facto leader of "
            "the Fifth Crusade since he took the credit for the sack of the "
            "Egyptian camp in 1219. He is no noble and has little experience "
            "of command in the field. He has twice turned down al-Kamil's "
            "offers, is waiting for Frederick II, and was raised up in part by "
            "a prophecy found in Damietta (pp. 65-67)."
        ),
    )
    w["crusade"] = b.threat(
        "The Fifth Crusade",
        place=w["damietta"],
        antagonist="The crusaders at Damietta, and the papal legate Pelagius",
        moves=DATED,
        summary=paragraphs(
            "After the Fourth Crusade's disaster Innocent III preached a new "
            "armed pilgrimage led by the Church, not by kings, who were asked "
            "to come but control nothing. They were cool, and crusades against "
            "the Cathars and the Moors were nearer and looked richer. Honorius "
            "III at last mustered an army of mostly lesser nobles, with a "
            "fleet from Frisia. It gathered in Italy in 1217, the fleet was "
            "late, and in 1218 part of it landed at Acre. Told Jerusalem could "
            "not be held while Egypt stood, the crusaders sailed again and "
            "landed near Damietta, to take it as a base against Cairo. Some "
            "history-minded troupes start a few years before 1220 to play this "
            "through (pp. 64-65).",
            "A relief force under al-Kamil, then vizier, held them on the "
            "defensive for six months to February 1219; the old sultan died "
            "soon after the landing and al-Kamil took his place. The "
            "Christians beat the relief force only through a strange chance "
            "(The Defeat of the Kurds), and the sack of its camp made Pelagius "
            "the real leader. Al-Kamil offered Jerusalem and all around it "
            "save two castles, and a thirty-year truce, for their immediate "
            "departure. John of Brienne, titular King of Jerusalem, and the "
            "Outremer barons wanted to accept; Pelagius, the Italians, and the "
            "masters of the Templars and Hospitallers, leading the French, "
            "refused, and refused again when 30,000 bezants were added.",
            "In August 1219 the massed Christians drove at the sultan's "
            "fortified position; he fell back, they lost cohesion in pursuit "
            "and looting, and he struck. John and the military orders "
            "prevented a rout, but the defeat was heavy. Al-Kamil offered "
            "again: the truce, the land, the bezants, the True Cross, money to "
            "rebuild Jerusalem's walls (which his brother had pulled down in "
            "January) and his fresh prisoners. John favoured it; the Italians "
            "and French, believing the Emperor was about to come, did not. In "
            "November a few crusaders saw an ungarrisoned tower, climbed an "
            "unguarded wall and opened a gate, and the city fell. Al-Kamil, "
            "unable to assault or besiege it, withdrew to Mansourah, with the "
            "1219 flood failed and his purse with it, and braced for the end.",
            "The bezant here is the Italian word for a gold coin; these were "
            "probably dinars, which by law weigh 72 grains of barley but in "
            "practice vary. The sultan having 30,000 to hand shows what a raid "
            "on his treasury might bring: friends of the Crusade could help it "
            "hugely by finding them and making off with them (p. 64).",
        ),
        stages=[
            b.stage(
                "The spoils are redivided",
                year=1220,
                clues=(
                    "In February the factions agree to share out the sack of Damietta "
                    "again."
                ),
                ignored=(
                    "The soldiers make peace, though their leaders still cannot stand "
                    "one another. The Pope lets John of Brienne leave to claim the "
                    "throne of Armenia, and Pelagius, in sole charge, waits for "
                    "Frederick II."
                ),
            ),
            b.stage(
                "Louis of Bavaria arrives",
                year=1221,
                season="Spring",
                clues=(
                    "Frederick does not come; in May 25,000 of his soldiers do, under "
                    "Louis of Bavaria, who urges an immediate attack."
                ),
                ignored=(
                    "Preparations begin. John of Brienne returns in July and counsels "
                    "against it, and again cannot move Pelagius."
                ),
            ),
            b.stage(
                "The march on Mansourah",
                year=1221,
                season="Summer",
                clues=(
                    "The Egyptians, who have spent a year wondering at the gift of "
                    "time to rearm, march out, take fright at the host and fall back "
                    "behind the tributary at Mansourah. The Christians follow and "
                    "fortify opposite, at Sharimshah."
                ),
                ignored=(
                    "In August the Nile rises and a dry canal they crossed begins to "
                    "fill. Egyptian ships enter it and cut their retreat and supply, "
                    "and Pelagius orders a return to Damietta."
                ),
            ),
            b.stage(
                "The retreat",
                year=1221,
                season="Summer",
                clues=(
                    "The Teutonic Knights burn most of the supplies; the wine will not "
                    "burn, so to keep it from Muslims many crusaders get drunk. The "
                    "burning camp warns the Egyptians."
                ),
                ignored=(
                    "Al-Kamil has the canal wall smashed and the road turns to deep "
                    "mud. At nightfall the Egyptians attack from firm ground. The "
                    "Christians rally on John and the masters and get back to a camp "
                    "with no food, to surrender or starve. Pelagius runs the blockade "
                    "by boat."
                ),
            ),
            b.stage(
                "Damietta is handed back",
                year=1221,
                season="Autumn",
                clues=(
                    "Pelagius accepts the sultan's terms: Damietta returned, the "
                    "Christians out of Egypt for at least eight years, all prisoners "
                    "freed, the True Cross promised."
                ),
                ignored=(
                    "On 8 September 1221 the Egyptians re-enter Damietta. Oddly, the "
                    "sultan's servants cannot find the True Cross: it has been stolen."
                ),
            ),
        ],
        secrets=(
            "This is the real world's course and need not be Mythic Africa's: "
            "at any point the characters can change it, sometimes by very "
            "small acts (p. 67). If this Mythic Europe follows history, the "
            "Egyptians then pull Damietta down and build a new city of that "
            "name a mile and a half away (see Pulling it All Down)."
        ),
    )


def _south_of_cairo(b: Builder, w: World) -> None:
    w["qus"] = b.town(
        "Qus",
        charter="Noble lord",
        ruler="Sultan al-Kamil",
        answers_to=w["sultan"],
        place=w["egypt"],
        summary=paragraphs(
            "The Greeks' Apollinopolis, long in decline and now in a century's "
            "rise the second city of Egypt. Three things raised it: the "
            "Crusade has pushed the pilgrim road across the Red Sea, and Qus "
            "is the last civilised place on it; a Christian rising at Qift "
            "ended with the sultan's brother putting 3,000 to the sword, so "
            "its market came here; and a gold rush at nearby Wadi Allaqi makes "
            "it the centre of mining supplies. New families have risen with "
            "trade and mining (p. 67).",
            "Merchants of Egypt meet those of Yemen, Ethiopia and beyond here, "
            "and complain of unfair taxes: goods assessed for a year's tax "
            "though not owned for a year, no allowance for exempt tools of "
            "trade, and assessors who check for smuggling by piercing bags "
            "with sharp sticks. Yet the merchants feel safe: one whose camels "
            "sicken may leave pepper or cinnamon by the road and expect to "
            "find it untouched (p. 69).",
            "The Qusian authorities are strict and the narrow valley is a "
            "choke point, so smuggling is hard, unless one can cross the "
            "desert. It is the nearest large settlement to old Thebes, its "
            "necropolis, and the temples of Luxor and Karnak (p. 68).",
        ),
    )
    w["qift"] = b.town(
        "Qift",
        charter="Noble lord",
        answers_to=w["sultan"],
        place=w["egypt"],
        summary=(
            "Once the gateway for foreign merchants into southern Egypt, now a "
            "town of Copts impoverished by their failed rising, in which the "
            "sultan's brother killed 3,000. Magi can hire grogs, "
            "Coptic-speaking companions and people with influence among the "
            "clergy here (pp. 67-68)."
        ),
    )
    w["akhmim"] = b.town(
        "Akhmim",
        place=w["egypt"],
        summary=(
            "A city on the pilgrim road south to Qus. Arab writers say wizards "
            "live in a temple here, served by moving statues or by moving "
            "reliefs on the walls, which grant their desires; yet these "
            "magicians hold no political power, even over the town around "
            "them. The town is named for a god classical writers equated with "
            "Pan (p. 68)."
        ),
        secrets=(
            "Theories abound. Some magi think their magic weak outside the "
            "temple's Faerie aura. Some Christians call them worshippers of "
            "Asmodeus, kept down by the imminent wrath of God. Some Muslims "
            "reply that they serve a Divine being and keep from the world for "
            "pious reasons."
        ),
    )
    _place(
        b,
        "Thebes, Luxor and Karnak",
        inside=w["egypt"],
        summary=(
            "The ancient capital, its necropolis and its temples, near Qus. "
            "The tombs near Thebes are cut into the rock and probably include "
            "those of the rulers who followed the strange heretic, monotheist "
            "pharaohs of lost Amarna (p. 68)."
        ),
    )
    w["allaqi"] = _place(
        b,
        "Wadi Allaqi",
        inside=w["egypt"],
        summary=(
            "The scene of a gold rush that Qus supplies (p. 67), and the reach "
            "of the north of Blemmyae territory, where some Blemmyae families "
            "mine gold and emeralds and control the flow of gold into Makuria "
            "and Egypt (p. 95). Shipping goods to the miners and carrying off "
            "untaxed gold might pay smugglers very well (p. 68)."
        ),
    )
    w["aydhab"] = b.town(
        "'Aydhab",
        place=w["egypt"],
        summary=paragraphs(
            "A seedy Red Sea port of pirates and smugglers for centuries, "
            "lately rich as the place pilgrims leave Egypt for Jiddah. Travel "
            "writers tell pilgrims to keep to trusted groups, for the locals "
            "will rob and kill for money. The desert around gives nothing: no "
            "crops, and even the water is imported. Most older buildings are "
            "woven of reeds shipped from the Nile, a few new ones plastered. "
            "On paper its wealth is trade, the pilgrim traffic and the catch; "
            "in truth its traders prey at sea, the pilgrims are its prey ashore "
            "and few fish are landed (p. 69). The port lies in land the Blemmyae claim, but in "
            "Egyptian hands (p. 96).",
            "Some pilgrims think the journey washes out sin and use it to "
            "indulge, and at a price most vices can be had here. Pilgrims are "
            "fleeced in three legal ways: famous prices for necessities, a "
            "fairly light tax of part of their food, and the hire of jilabs. A "
            "jilab is a rickety boat of planks sewn with coconut fibre, "
            "caulked with palm shavings, rigged with Theban palm-leaf sails "
            "and greased with castor or shark oil; it flexes on the reefs, so "
            "it is thought safer than a nailed hull. The hire is so high that "
            "the owner loses nothing if it sinks. Boats are often lost, "
            "crammed with pilgrims in a sea known for wrecks and sharks, and "
            "everyone in town who is not poor owns at least two.",
        ),
        secrets=(
            "Most of the city seems to be falling under the sway of evil (p. 57)."
        ),
    )
    w["torturers"] = _place(
        b,
        "The House of Torturers",
        inside=w["egypt"],
        realm="Infernal",
        known=LOCAL,
        summary=(
            "The old customs house at 'Aydhab. The Fatimids charged all who "
            "entered Egypt here seven and a half dinars, and hanged those who "
            "could not pay by the testicles, sending their names on to Qus and "
            "elsewhere, where the tax agents would do what travellers call "
            "only 'worse'. Sultans no longer charge pilgrims (pp. 57, 68)."
        ),
        secrets=(
            "It keeps an Infernal aura, the book gives no figure, and minor "
            "demons living there urge locals to rob or murder pilgrims."
        ),
    )
    w["pearl_isles"] = _place(
        b,
        "The Pearl Islands near 'Aydhab",
        inside=w["egypt"],
        summary=(
            "Islands whose seabeds teem with a silver bivalve that tastes of "
            "sea turtle, with mother-of-pearl shells. Pearls come in a brief "
            "June season from divers, about four to the ton of shellfish. Some "
            "divers black out as they surface (p. 68)."
        ),
        secrets=(
            "Those who black out seem to sate creatures that guard the pearls. "
            "If magi make diving safer, the creatures may stop slumbering."
        ),
    )
    w["red_sea"] = _place(
        b,
        "The Red Sea",
        summary=(
            "A sea of reefs, wrecks and sharks, home to immense creatures: "
            "sea-eels, sharks, whales, tremendous turtles, massive "
            "sea-centipedes and worms. They chase shoals up from the depths "
            "until the fish beach themselves in numbers or leap into boats (p. "
            "97). Its ports, 'Aydhab, Badi, Qusayr and Sawakin, are old rivals."
        ),
    )
    w["keepers"] = b.faction(
        "The Keepers of the Roads",
        faction="Faerie court",
        realm="Faerie",
        place=w["egypt"],
        summary=(
            "Faeries who guard the goods merchants leave at the roadside and "
            "enforce the road's bounds and the rule against theft. They need "
            "not attack: they confuse a thief and hide the road, and he dies "
            "of exposure or thirst (p. 68)."
        ),
    )


# -- Egypt's stories --


def _egypt_seeds(b: Builder, w: World) -> None:
    egypt, cairo, gizeh = w["egypt"], w["cairo"], w["gizeh"]
    alexandria, maristans, pharos = w["alexandria"], w["maristans"], w["pharos"]
    _seed(
        b,
        "No Papa",
        "The patriarchate has been vacant since 1216, deadlocked between "
        "Cyril ibn Laqlaq and those who oppose him. Characters who could "
        "break the deadlock might win the gratitude of the winning side "
        "(p. 58).",
        where=cairo,
        antagonist="Cyril ibn Laqlaq and his opponents",
    )
    _seed(
        b,
        "Ancient Works of Magic or Trickery?",
        "At the Cairo mosque built where Moses duelled Pharaoh's "
        "magicians, characters can call up the magicians' ghosts, given "
        "the right help or Hermetic Virtues. With no relic they must make "
        "an Arcane Connection to the dead; happily the two magicians' "
        "names are recorded, and one died in the Plague of the Death of "
        "the First Born Sons. Leadworkers (Houses of Hermes: True "
        "Lineages) and users of defixiones (Ancient Magic) can use names "
        "for this, and summon a pharaonic wizard here (p. 59).",
        where=cairo,
        secrets="Some of their magic was only trickery.",
    )
    _seed(
        b,
        "Perfect Ingredient",
        "A plague breaks out in Egypt. It was last seen three hundred "
        "years ago and a scholar cured it somehow. A student's account in "
        "the Maristan library tells of a strange talisman that sealed the "
        "illness into the pit of the last victims, and gives away clues to "
        "the pit. The head of the Maristan sends an expedition (p. 60).",
        where=maristans,
        secrets=(
            "Grave robbers have opened the pit and carried off the talismans. "
            "While they hold them they stay well but can carry the sickness. "
            "The Maristan and the Guild of Seekers combine to find them, study "
            "the talismans and copy them, and the player characters are urged "
            "to fetch a rare ingredient each one needs. Rivals who learn the "
            "plan mean to gather as much of it as they can and destroy the "
            "source, to make their stock priceless."
        ),
    )
    _seed(
        b,
        "The Magical Air",
        "In Barcelona ordinary people have begun to develop the Magical "
        "Air Flaw. Strife follows, and churchmen who see the likeness to "
        "the Gifted blame the Order. A local Criamon suggests a "
        "contaminant but cannot find or treat it. The Tribunal tries "
        "everything it can, and sends a delegation to see whether the "
        "Maristan's records hold anything similar (p. 60).",
        where=maristans,
    )
    _seed(
        b,
        "The Returnee",
        "A young woman among the Maristan's insane makes wild claims that "
        "would be ignored if they were not in archaic Latin. A Coptic monk "
        "has heard such phrases only from a member of the Order of Hermes. "
        "She says she is Lucia of the line of Trianoma, back from "
        "Twilight. Her parents swear she is their own daughter, raised "
        "from birth (p. 60).",
        where=maristans,
        secrets="How, then, does she know the Parma Magica?",
    )
    _seed(
        b,
        "Pyramidions",
        "Of the three main pyramids at Gizeh only one keeps its capstone. "
        "The other two were stolen, with great difficulty, and hidden. "
        "Pyramidions are powerful tethers that make Magic auras, yet are "
        "small enough for a spell or a cart to move. Who needs a mobile "
        "aura, and what have they used it for these few hundred years (p. "
        "62)?",
        where=gizeh,
    )
    _seed(
        b,
        "Where is Alexander?",
        "Most guides say the largest pyramid was made for Alexander, who "
        "never lay in it. By old custom whoever buried Pharaoh was the "
        "next Pharaoh, so Ptolemy stole the corpse and buried it secretly. "
        "For long a certain sarcophagus was thought his, a blind that "
        "really held the last king before the Ptolemies. Treasure hunters "
        "keep coming back to Cairo with coins, amulets and papyri that "
        "hint at his tomb (p. 62).",
        where=gizeh,
        secrets=(
            "Hermetic magi actually know Alexander was buried in Memphis and "
            "then Alexandria, and have some idea where. None of the local "
            "faeries care."
        ),
    )
    _seed(
        b,
        "The Library of Cleopatra",
        "Find the unfound grave of Cleopatra and it may lead to a hidden "
        "store of Alexandria's books; or find the walls of the library on "
        "the seabed, and read what was carved on them (p. 63).",
        where=alexandria,
    )
    _seed(
        b,
        "The Lighthouse Mirror",
        "A sedentary Verditius offers to pay the characters to find the "
        "Pharos mirror. Can they search the seabed, find ghosts who "
        "remember its casting into the sea, or get an Arcane Connection to "
        "it (p. 63)?",
        where=pharos,
    )
    _seed(
        b,
        "The Island's Aura",
        "A powerful magus planning an Alexandrian covenant has been "
        "distracted by the Christians feuding in Damietta. He pays the "
        "characters to live on the Pharos island for a year and find out "
        "why reports of its aura disagree (p. 63).",
        where=pharos,
    )
    _seed(
        b,
        "The Second Inscription",
        "Another sheet of lime plaster has fallen from the Lighthouse, "
        "showing a detailed prediction of events in the Order. Is it a "
        "hoax? If not, are other messages hidden on the building, and can "
        "whoever wrote them be trusted (p. 63)?",
        where=pharos,
    )
    _seed(
        b,
        "The Mystery of the Oil",
        "Where does the oil that lights Alexandria all night come from (p. 63)?",
        where=alexandria,
    )
    _seed(
        b,
        "The Itinerarium in Alexandria",
        "A skilled Jerbiton leads a band of apprentices to Alexandria's "
        "ruins. The players act as guards, or as rescuers when something "
        "unexpected happens (p. 63).",
        where=alexandria,
    )
    _seed(
        b,
        "Peasant Revolt",
        "Sugar needs far fewer hands than wheat or barley. Absentee nobles "
        "with no feeling for their land order as much of it grown as "
        "possible, leaving many without work, and if several in a district "
        "do so, each counting on buying a neighbour's wheat, there is "
        "famine. A horde of starving peasants threatens the magi's "
        "interests: can they turn its anger aside (p. 69)?",
        where=egypt,
    )
    _seed(
        b,
        "A Wheel for the Verditius",
        "A Verditius in the Greater Alps, curious about the waterwheels "
        "that crush cane, writes by redcap asking the characters to take "
        "apart the most efficient wheel they can find and ship it to him. "
        "Can they get it quietly, dismantle it unbroken and send it? Would "
        "it be easier to send Egypt's best wheelwright to the Alps? And if "
        "they go with it through Italy, how do they deal with nobles drawn "
        "by rumours of a Saracen siege engine (p. 69)?",
        where=egypt,
    )
    _seed(
        b,
        "The Source of the Cane",
        "Sugar cane appeared very suddenly in Egypt, and rumour says "
        "supernatural powers gave it to the first farmers. Did a demon of "
        "gluttony offer it to men? Are there really faeries that possess "
        "children who eat sugar and set them running mad (p. 69)?",
        where=egypt,
    )


def _gizeh_seeds(b: Builder, w: World) -> None:
    gizeh = w["gizeh"]
    _seed(
        b,
        "Aristotle's Lost Books",
        "Dig into the side of Aristotle's pyramid, past defences no one "
        "has yet dared, for the books meant for publication that Mythic "
        "Europe has never read (p. 62).",
        where=gizeh,
        secrets="The Tomb of Aristotle's record gives what the books do.",
    )
    _seed(
        b,
        "The Lamps of Mykerinos",
        "Where are the lamps with which Mykerinos tried to slow time, and "
        "do they still work (p. 62)?",
        where=gizeh,
    )
    _seed(
        b,
        "The Sand of Hermes",
        "A scholar who carries the plateau's sand for its gift to the mind "
        "has spent his life among the tombs and cannot be brought to leave "
        "(p. 62).",
        where=gizeh,
        realm="Faerie",
        secrets=(
            "Faeries grant the gift and take it back if he stops, feeding on "
            "the attention."
        ),
    )
    _seed(
        b,
        "The Crocodiles of Gizeh",
        "No Hermetic magus has ever assessed the marble crocodiles in a "
        "laboratory. What do they do, and could they be moved (p. 62)?",
        where=gizeh,
    )
    _seed(
        b,
        "Raising the Throne",
        "In a famine year the Isle of Gold shows above the low Nile. Why "
        "has no one ever tried to raise Pharaoh's throne (p. 62)?",
        where=gizeh,
    )
    _seed(
        b,
        "The Wizards of Akhmim",
        "Who are the wizards of the temple at Akhmim, served by moving "
        "statues yet with no power over the town around them (p. 68)?",
        where=w["akhmim"],
    )


def _crusade_seeds(b: Builder, w: World) -> None:
    damietta, sultan = w["damietta"], w["sultan"]
    _seed(
        b,
        "Breaking the Chain",
        "It took a month to break the chain at Damietta, and two groups "
        "are sure they did it. French soldiers remember assaulting the "
        "island tower from boats and rushing it with ladders, at the cost "
        "of many comrades. Dutch soldiers remember building a ship with a "
        "great saw beneath it, and ramming the chain in two; they have "
        "commissioned bells to ring the victory every year. Both carry "
        "pieces of the chain as keepsakes (p. 66).",
        where=damietta,
        secrets=(
            "Some crusade leaders believe both stories in full, each with "
            "whichever group they are talking to; confronted, they cannot see "
            "the difficulty and soon forget the conversation. Is this a "
            "miracle hidden by Divine power, or two powerful faeries "
            "contesting the crusaders' vitality?"
        ),
    )
    _seed(
        b,
        "The Defeat of the Kurds",
        "The first Egyptian army was destroyed by infighting. Hearing that "
        "the general of the Kurds, his largest contingent, planned a coup, "
        "the sultan burst into the plotters' tent at the very moment their "
        "hands lay on a Qur'an, swearing to depose him. He took them "
        "prisoner and went to Cairo to secure his position. His army woke "
        "to find him gone and its general a prisoner, and scattered (p. "
        "66).",
        where=sultan,
        secrets=(
            "Was the plot mundane, born in the army or of Christian agents? Or "
            "a contagious madness from a demon, a faerie whispering promises "
            "of rule, or a battle between puppets of the Order of Suleiman?"
        ),
    )
    _seed(
        b,
        "Pulling it All Down",
        "As Damietta's buildings come down to supply the new city a mile "
        "and a half away, treasures and secrets come to light. Ghosts are "
        "disturbed, and the hidden cesspits of servants of the Infernal "
        "lie open (p. 67).",
        where=damietta,
        secrets=(
            "If magi steer the choice of the new site, it might take in "
            "ancient tombs with Magic auras, leaving lacunae in the city's "
            "Dominion."
        ),
    )
    _seed(
        b,
        "Pelagius's Destiny",
        "A prophecy in an old Arabic book found in Damietta foretold "
        "Pelagius's victory, and helped raise him up. No one knows who "
        "wrote it or how a crusader came by it. Characters who find a "
        "clearer copy can sell it to either side for valuable concessions, "
        "or use it to work events themselves (p. 67).",
        where=damietta,
    )


def _upper_egypt_seeds(b: Builder, w: World) -> None:
    egypt, qus = w["egypt"], w["qus"]
    _seed(
        b,
        "Escort",
        "A redcap or magus who means to explore Ethiopia or Arabia asks "
        "for an escort to Qus, to meet the merchants who come there, learn "
        "the distant country's language and hear the dangers of the road "
        "(p. 68).",
        where=qus,
    )
    _seed(
        b,
        "Lost Merchants",
        "Someone asks the characters to find the bodies of merchants lost "
        "to the Keepers of the Roads, for burial; or to save a merchant "
        "who angered a keeper by theft and was lucky enough not to die of "
        "thirst (p. 68).",
        where=w["keepers"],
        antagonist="The Keepers of the Roads",
        realm="Faerie",
    )
    _seed(
        b,
        "Smuggling at Qus",
        "Magi or servants able to cross the desert could make a great deal "
        "smuggling past Qus: goods out to the gold miners of Wadi Allaqi, "
        "untaxed gold back (p. 68).",
        where=w["allaqi"],
    )
    _seed(
        b,
        "Infernal Site?",
        "Pilgrims at 'Aydhab keep being robbed and murdered, and the trail "
        "leads back to the old customs house (p. 68).",
        where=w["torturers"],
        realm="Infernal",
        secrets=(
            "Minor demons dwelling in the House of Torturers encourage the "
            "locals to it."
        ),
    )
    _seed(
        b,
        "Pearls",
        "Characters who want money quite legally might try the islands "
        "near 'Aydhab in the brief June pearling season (p. 68).",
        where=w["pearl_isles"],
        secrets=(
            "If magi make the diving safe, the guardians that are sated by "
            "drowning divers may wake."
        ),
    )
    _seed(
        b,
        "The Bujat Road",
        "Sailing back from Jiddah to 'Aydhab is dangerous: the winds blow "
        "ships south into the lands of the Bujat, the Romans' Blemmyae. "
        "Some travellers say the Bujat hire out camels and lead people "
        "north on purpose short of supplies, and then claim the goods of "
        "those who die of hunger and thirst. Their sultan lives in the "
        "mountains near Philae, and his family are said to be corrupt "
        "nudists who wear a loincloth at most. The al-Bujat once lived around "
        "Philae and worshipped Isis, and their wars made the Romans move "
        "Egypt's border north and garrison it (p. 68).",
        where=egypt,
        secrets=(
            "It is unclear whether these are the Bujat, or headless faeries "
            "who have taken their name and story."
        ),
    )


# -- Nubia --


def _nubia(b: Builder, w: World) -> None:
    w["nubia"] = _place(
        b,
        "Nubia",
        summary=paragraphs(
            "The stretch of the Nile valley with a narrow, broken floodplain "
            "and six cataracts, the Arabs' bled es-Sudan, Land of the Blacks. "
            "Lower Nubia, around the first two cataracts, is almost rainless "
            "desert with a thin strip of river, farmed only with mule-driven "
            "waterwheels. Upper Nubia to the south has seasonal rain and much "
            "vegetation; where a river joins the Nile the land inside the "
            "confluence is rich, and people gather on these 'islands'. "
            "Savannah buffers it from the desert, and in the far south it "
            "merges into the Ethiopian Highlands. Its three kingdoms are "
            "Nobatia, Makuria and Alodia (p. 71).",
            "History (pp. 71-73). Early kingdoms at Ballana near Pakhoras and "
            "at Kerma were absorbed by Kush, ruled by qores who descended from "
            "Nubian pharaohs of Egypt, and from Cush son of Ham. Kush broke "
            "from Egypt a thousand years before Christ. Its capital was first "
            "Napata, near the fourth cataract. In 591 BC Emperor Aspelta moved "
            "his palace to Meroë, partly to escape the priests, who as "
            "arbiters of ma'at, the order that made the laws, elected the "
            "king, made him a god and could order him to kill himself. He "
            "obeyed. Around 300 BC Emperor Arqamani had the Napatan priests "
            "slaughtered and made Meroë the capital, with a new royal "
            "cemetery; emperors then truly ruled but were no longer divine. "
            "Weakened by war with Rome and Axum and by rebellion, Kush faded. "
            "In 297 Diocletian used the desert Nobatae against the Blemmyae, "
            "and they settled the valley. A fifth-century Blemmyae revival at "
            "Meroë was crushed by Axum and the Nobatae, and three kingdoms "
            "emerged. Axum held Upper Nubia as a vassal for nearly a century "
            "from the early sixth.",
            "In 540 Constantinople sent two missions, Justinian's Melkite and "
            "Theodora's Monophysite; the empress had the Melkites delayed in "
            "Egypt, and Julian spent two years in Nubia. His successor "
            "Longinus returned only in 567, when Makuria had gone orthodox, "
            "stayed six years in Nobatia, was exiled to Arabia, came back in "
            "580, and crossed the Blemmyae lands to Alodia, which he converted "
            "wholly. The Umayyads failed twice to take Makuria, in 642 and "
            "652, and the Baqt gave five centuries of accord. With the "
            "Melkites out of favour in Arab Egypt, Makuria had no Melkite "
            "bishops for over a century, and King Merkurios, the 'New "
            "Constantine', builder of Dongola, adopted Monophysitism. He also "
            "subdued Nobatia, which he suspected of dealing with Egypt's "
            "Muslims. Under the Fatimids (969 to 1171) Nubia thrived, "
            "supplying them with goods and soldiers, and gold found in the Red "
            "Sea hills paid for new ports.",
            "When the Fatimids fell in 1171 Salah ed-Din sent his brother "
            "Shams ed-Dawla Turan Shah to invade Nubia. Nobatia suffered "
            "terribly and Premnis was held for some years. An emissary sent to "
            "weigh Makuria reported it too poor to be worth conquering, a lie, "
            "for it was and is at its height, and the Ayyubids withdrew. Trade "
            "returned but trust did not: the Baqt now goes unpaid more years "
            "than not, and demands for arrears are ignored. Bedouin tribes "
            "driven out by the Ayyubids are coming south into Upper Nubia, "
            "taking land from Makuria and Alodia and setting up warring "
            "principalities, meks, east of the Nile. Nobatia's desert is too "
            "poor to tempt them.",
            "People (pp. 73-74). Nubians are black-skinned, with wavy black "
            "hair (curly hair is thought the mark of slave stock), and taller "
            "than most Europeans and Arabs. They wear light cotton trousers "
            "and loose smocks, brightly dyed in geometric patterns for church "
            "and feast days. Important people wear short tunics stiffened with "
            "reeds or ivory to flare at the waist, sometimes several layers of "
            "different lengths and colours. Both sexes wear gold and copper "
            "bangles and neck hoops, beads of ostrich eggshell, glass, cowrie "
            "and wood, and carved stone rings; parasols and walking sticks are "
            "common even among the young; hair is plaited in tresses or held "
            "in topknots with long ivory combs.",
            "Warriors (p. 73). The Arabs call Nubian archers 'pupil-smiters' "
            "and 'archers of the eyes'. They use self bows and a compound bow "
            "with a bone core, with costly iron heads that punch through thick "
            "armour, spears, and short one-edged swords, and moulded oxhide "
            "breastplates, skirts, vambraces and greaves. Cavalry ride light "
            "horses or war camels. Exarchs command divisions of the royal "
            "guard or frontier garrisons; there is a levy in war, and Makuria "
            "keeps a small river navy under two nauarchs.",
            "The dead (pp. 73-74). Nubians bury by Church rite but with no "
            "ceremony, and fear the dead deeply. A mask or plate covers the "
            "face so that death cannot infect those who see it; family and "
            "friends rarely attend, leaving it to a priest and hired "
            "pallbearers. Graves show where, not who. Houses have no windows "
            "towards a burial site, and graveyards have no roads near them. "
            "The same dread covers Kush's monuments: people who live by a "
            "pyramid avoid looking at it. Alodians will not even name a dead "
            "person or speak of his deeds.",
            "Names (p. 74). A given name with perhaps a father's or town's "
            "(Abraam son of Kosma, Dawud of Dongola); women often by marriage "
            "(Eionngoka wife of Abraam). Male: Abraam, Adama, Anastasios, "
            "Athanasios, Chael, Dauti, Dawud, Douddil, Georgios, Iakobi, "
            "Iesou, Ioannes, Ioasse, Kosma, Mashshouda, Merkourios, Orinourla, "
            "Petros, Pisroel, Tapara, Tirsakouni. Female: Anthelia, Anna, "
            "Eionngoka, Eirene, Ekkir, Genseoua, Iannia, Maria, Mariham, Mena, "
            "Petrosinta, Songoja, Sophora, Theodora. Most Nubians laugh at "
            "long Kushite names, but Meroë's upper classes still sometimes use "
            "them. Male: Amanikhabale, Aspelta, Atakhebasken, Malewiebamani, "
            "Piye, Senkamanisken, Shabaka, Taharqa, Tanwetamai. Female: "
            "Amanitore, Aqaluqa, Gerarheni, Henuttakhebit, Kasaqa, Pebatjma, "
            "Qalhata, Shanakdakhete, Tabiry, Yuterow.",
            "Economy (pp. 76-77). Several crops a year of sorghum, millet, "
            "barley and dates, with lentils, olives, sesame, vines, bananas, "
            "wheat and cotton. Sorghum makes bread and mizr, a staple beer; "
            "dates and grapes make drink; oxen drive the waterwheels. Sheep, "
            "goats, cattle and above all pigs are the livestock. Houses are of "
            "sun-dried brick. Pottery (at Pakhoras) and weaving (at Dongola) "
            "lead, with leather, metal and palm-fibre goods; gold and emeralds "
            "come from the Red Sea Hills. Cotton, and camel and goat wool, "
            "take dyes, and Nubian indigo gives light-fast blues the north "
            "envies. Exports: glass, ivory, ostrich feathers, cattle, "
            "emeralds, gold and above all slaves. Imports from Egypt: wheat, "
            "linen and wine. Downstream boats always pass; upstream, sail "
            "cannot get from Dongola to Abu Hamad against the prevailing wind, "
            "and the cataracts pass only at high water, so camels and donkeys "
            "matter.",
            "Ancient auras (p. 83). The old monuments once had Faerie auras "
            "from pagan worship, which waned as the temples emptied. Centuries "
            "as cemeteries may have left a tether to the Magic Realm: a Magic "
            "aura of 1 for each century of continuous use, more at striking "
            "natural sites, less where the monuments have decayed (Realms of "
            "Power: Magic pp. 8-10).",
        ),
    )
    w["fortified_river"] = _place(
        b,
        "The Fortified River",
        inside=w["nubia"],
        summary=(
            "Since the mid-twelfth century the kings of Makuria and Alodia "
            "have raised over fifty fortresses from Soba to Kalabsha, on "
            "nearly every lone hilltop with its own water, each big enough for "
            "the local people and with deep crypt-like stores of grain, in "
            "answer to their Muslim neighbours' growing aggression. Smaller "
            "ones have minimal garrisons and lie mostly deserted (p. 80)."
        ),
        secrets=(
            "More than one has been quietly taken over by bandits, and "
            "sometimes something more sinister lives there."
        ),
    )
    w["darb"] = _place(
        b,
        "The Darb al-Arba'in",
        inside=w["nubia"],
        summary=(
            "The road of the Arab slavers, from Asyut in Egypt by way of the "
            "remote trading town of Uri down into the Slavelands. It carries "
            "slaves past every major city on the Nile, so that Nubians can "
            "pretend the trade does not exist (pp. 77, 85)."
        ),
    )


def _nubian_powers(b: Builder, w: World) -> None:
    nubia = w["nubia"]
    b.custom(
        "The Baqt",
        place=nubia,
        rules=(
            "No war between the parties; safe conduct for each other's "
            "citizens; runaway slaves and Egyptian outlaws returned. Each year "
            "Nubia owes 365 slaves to the treasury, 40 to the emir of Egypt, "
            "20 to the governor of Aswan, 5 to the judge of Aswan and 1 to "
            "each of the twelve guarantors; Egypt owes wheat, barley, wine and "
            "fancy cloth."
        ),
        summary=paragraphs(
            "The treaty of 652 between the Umayyad governor of Egypt and the "
            "king of Makuria, after a failed invasion; the name comes from the "
            "Greek pakton, agreement. It alone among Muslim treaties freed a "
            "Christian land from invasion and forced conversion, and Egypt did "
            "not invade for over 500 years despite many lapses (p. 73).",
            "In 835, fourteen years in arrears, the caliph pressed King "
            "Zacharias of Makuria, whose son George went to Baghdad and made "
            "the slaves due every three years. The Fatimids demanded arrears "
            "too, an envoy came to Dongola, and it was renewed again. Since "
            "the invasion of 1172 it binds less, and the Baqt is more often "
            "defaulted than paid (pp. 72-73).",
            "Copies are in every city of Nobatia and Makuria; the originals of "
            "652 and 835 lie in Dongola Cathedral. A copy signed under "
            "authority from the King of Makuria and the Fatimid governor holds "
            "a pawn of Rego vis. The two originals are sources of Rego vis "
            "infused with the Divine, yielding only in years when Egypt does "
            "not attack and the tribute is not in arrears (p. 73).",
        ),
    )
    b.church(
        "The Nubian Church",
        church=SEE,
        place=nubia,
        summary=paragraphs(
            "Nubia is overwhelmingly Christian, and it is illegal for a "
            "Makurian or Alodian subject to profess any other faith. Nobatia "
            "and Alodia were first Monophysite and Makuria Melkite; as "
            "Byzantine power in Egypt sank, Makuria too came over. The Church "
            "is one with the Coptic Church under the Patriarch of Alexandria, "
            "who appoints all bishops, many of them Egyptians, but its liturgy "
            "is in Greek, not Coptic (p. 74).",
            "There are seven sees in Makuria and Nobatia (Kalabsha, Premnis, "
            "Pakhoras, Sai, Dongola, Shanqir and Kallama) and six in Alodia "
            "(Soba, Meroë, Kabushia, Kawa, Sennar and Goz Regeb). The ranks "
            "are many: bishops (papas), great priests (sorto daoul), priests "
            "(sorto or presbyteros), archimandrites, archdeacons, epideacons, "
            "deacons, liturgists and elders (gort). The typical church is a "
            "flat-roofed rectangle on timbers; larger ones are cruciform or "
            "domed. Monasticism is minor, its houses mostly founded and filled "
            "by Egyptians, and there are unrecognised communities called lawra "
            "(p. 76).",
            "The archangel Michael is everywhere in invocations, inscriptions "
            "and dedications, and the common cryptogram chi-pi-theta stands "
            "for his name in Greek by number: 689 (p. 76).",
        ),
    )
    b.faction(
        "The Kushite Gods",
        faction="Faith or sect",
        place=nubia,
        summary=paragraphs(
            "The old religion lingers in pockets, untolerated by the Church. "
            "Before creation water covered all; a mound rose, and on it Atum "
            "the first god was born and made the world from it. That mound is "
            "Dju Wa'ab (p. 76).",
            "Atum is an old man, sometimes ram-headed. Anhur and Menhit were "
            "war gods Egypt took from Kush: Anhur, patron of soldiers, a "
            "bearded man in a kilt and four-feathered headdress with a spear, "
            "honoured with mock battles; Menhit, 'she who massacres', "
            "lion-headed, who rained fiery arrows. Mandulis, the sun, wears "
            "ram's horns, cobras, plumes and sun discs, and sometimes has a "
            "hawk's body and a man's head. Dedun, god of incense, was god of "
            "prosperity, guardian of the royal dead and special patron of the "
            "priests. Apedemak, perhaps the greatest, patron of royalty and of "
            "Meroë, was a four-armed man with three lion heads, or one, or a "
            "lion killing serpents, an allegory for Arqamani's triumph over "
            "the priests of Napata; he stood for courage, truth, light and "
            "fertility. His wife Amesemi was goddess of protection and the "
            "moon.",
        ),
    )
    b.faction(
        "The Ja'alin",
        faction="Family",
        decides="Its leader",
        ruler="Hamad",
        place=nubia,
        tradition=SAHIRS,
        summary=(
            "Bedouin who have come from Arabia and Egypt over the last fifty "
            "years and now hold both banks between Abu Hamad and Berber. A "
            "dozen or so little principalities, meks, each founded by a prince "
            "exiled with Hamad, hold around a hundred human families and "
            "twenty or so jinn; each prince has an unGifted sahir of Hamad's "
            "line as vizier, who also mediates with the jinn. The jinn mostly "
            "belong to the Faerie Realm and are Muslims like their neighbours. "
            "Proud descendants of Abbas, uncle of Mohammed, men and women "
            "alike scar their faces in an H or T. They herd sheep and goats "
            "over thin pasture and sometimes fight over it, but quarrels are "
            "forbidden at Abu Hamad, which is neutral ground (p. 81)."
        ),
    )
    b.faction(
        "Banu al-Kanz",
        faction="Family",
        place=nubia,
        ruler="The Kanz al-Dawlah",
        summary=(
            "An Arab tribe that held the Aswan region under the Fatimids, one "
            "of whose rulers earned the title Kanz al-Dawlah, 'treasure of the "
            "state', which became hereditary. The Ayyubids drove them out, and "
            "they have made a semi-independent Muslim principality in northern "
            "Nobatia, including the land round Philae. Refugees from them "
            "built the island forts of the Batn al-Hajar (pp. 78, 80). The "
            "book also spells them Banu al-Kanuz."
        ),
    )
    w["slavers"] = b.custom(
        "The Nubian Slave Trade",
        place=w["darb"],
        wants="Slaves and their cattle from the Slavelands.",
        summary=paragraphs(
            "Slaves are all three kingdoms' chief export. They come from the "
            "Slavelands, the vast pasture south and west of Alodia, with its "
            "peaceful unorganised herders, trekked hundreds of miles and "
            "driven north to Egypt (p. 77). Details of those peoples are in "
            "chapter 9.",
            "The Christian kingdoms promote the trade yet abhor keeping "
            "slaves. Most bishops think it unbecoming and do nothing. The "
            "chief excuse is the Baqt, though it has weakened since 1172 and "
            "takes only a third of the slaves passing through; the rest are "
            "for profit. Promoters call the captives barely better than "
            "beasts, or say slavery is a better life than the Slavelands' wild "
            "beasts and cannibals. When the Baqt is missed it is rarely "
            "conscience, but refusal to pay the slavers' prices, no will to "
            "regulate them, and few ways to undercut them; sometimes famine or "
            "disease in the Slavelands, and rarely a whole lost expedition (p. "
            "77).",
            "Owning slaves is legal but not acceptable in any Nubian kingdom. "
            "Unlike Europe's, slave owners in Egypt and Nubia need no Virtue, "
            "and may hold what suits their wealth; a Christian owner in a "
            "Christian kingdom has a Local Reputation of 1. Slavers take "
            "Merchant if they transport or Mercenary Captain if they capture, "
            "and are likely Well-Traveled (p. 75).",
            "Playing it (p. 75): slave stories need care for modern "
            "sensibilities. A slave character takes the Favored Slave or "
            "Chattel Slave Flaw (p. 76), which differ from Guardians of the "
            "Forests' Slave (p. 102). Reasons for a lax master: an inherited "
            "slave who "
            "cannot be freed without insult, a long loyal line, a vital skill, "
            "a self-sale to avert a worse fate. Stories for a chattel slave: "
            "escaped and hunted; seeking captured family; a dead master no one "
            "knows of; crimes hidden from the master or forced by him; a "
            "favoured slave envied; a master's enemies striking through him. "
            "Those truly free of their master count as free Aithiopians.",
            "A free Aithiopian marks himself apart: Outsider if he keeps "
            "tribal ways, Outcast if he has taken local ones, in any saga "
            "outside the Slavelands. He will be taken for a slave in any Arab "
            "land, but without a Story Flaw that can usually be settled. Story "
            "Flaws may tie him here: Dependents or a True Love sold north, "
            "Close Family Ties, a former owner as Enemy, a Feud with his "
            "captor. A campaigner against slavery likely has Driven, Temporal "
            "Influence or Social Contacts, and Enemies. Abolishing the trade "
            "means renegotiating or ending the Baqt; petitioning the Church is "
            "a fine start, and what the bishops ask in return may make stories.",
        ),
    )


def _nobatia(b: Builder, w: World) -> None:
    w["nobatia"] = _place(
        b,
        "Nobatia",
        inside=w["nubia"],
        summary=paragraphs(
            "A splinter of Kush that kept Kushite gods and customs, under "
            "Makuria's suzerainty for the last four hundred years or so but "
            "culturally its own and resisting every attempt to make it a "
            "province. It runs from the first to the third cataract, mostly "
            "desert, with the Libyan Desert west and the Nubian east; its "
            "people keep to the river, and eastern-bank settlements are the "
            "more heavily fortified against Blemmyae raids (pp. 77-78).",
            "As in old Kush, inspectors collect all surplus and give it to "
            "those in need, first to those who have given before, so there is "
            "little poverty. It is a free trade zone, unlike Makuria: Egyptian "
            "coin is legal tender and Egyptians trade unhindered, but all "
            "cargo going upriver must pass to Nobatian factors. Trade with "
            "Alodia cannot cross Makuria, so caravans leave Nobatian towns "
            "across the risky desert. With the Ayyubid and Bedouin threats, "
            "people are moving from scattered settlements to walled hilltop "
            "and island towns, with stronger houses and inside stores (p. 78).",
        ),
    )
    w["eparch"] = b.lord(
        "The Eparch of Nobatia",
        title="",
        seat="Premnis",
        place=w["nobatia"],
        summary=(
            "The Lord of the Mountain, viceroy in place of a king, appointed "
            "directly by the King of Makuria, with judicial and financial "
            "control of the land. He can found churches and celebrate Mass. "
            "Each eparch is also anointed king of Dotawo, a Makurian vassal "
            "kingdom centred at Ado, which pays for him. He handles relations "
            "with Muslim Egypt, receives goods meant for the King of Makuria, "
            "and must deliver the Baqt's slaves or, more often of late, "
            "excuses. His emblem is a double-horned headdress, worn on formal "
            "occasions; his agents carry it embossed on an iron badge (p. 77)."
        ),
    )
    w["ado"] = b.town(
        "Ado",
        charter="Noble lord",
        ruler="The Eparch of Nobatia, as king of Dotawo",
        answers_to=w["eparch"],
        place=w["nobatia"],
        summary=(
            "A hilltop fortress, with Premnis and Pakhoras one of Nobatia's "
            "three chief towns, and capital of the subkingdom of Dotawo. In "
            "the invasion of 1172 the Egyptians, who call it Jabal 'Adda, "
            "searched it for the eparch and failed to take him. The book calls "
            "that invasion Abbasid here, and Ayyubid elsewhere (p. 78)."
        ),
    )
    b.church(
        "The Eparch's Church at Ado",
        church=MOSQUE,
        place=w["ado"],
        summary=(
            "The eparch's own church: no cathedral, but an impressive building "
            "with a complex geometric mosaic floor (p. 78)."
        ),
    )
    w["batn"] = _place(
        b,
        "Batn al-Hajar",
        inside=w["nobatia"],
        summary=(
            "The 'belly of stones', named by Egyptian traders: eighty miles "
            "south of the second cataract where the Nile runs between high "
            "cliffs through barren mountains, with no floodplain, in places no "
            "more than twenty paces wide, broken by rapids, outcrops and small "
            "islands, and unnavigable even at the flood. Some islands hold "
            "miniature forts, raised into rocky towers against the floods by "
            "people fleeing the Banu al-Kanz. Otherwise it is all but "
            "uninhabited. It divides Lower Nubia, where foreigners are "
            "welcome, from Upper Nubia, where foreign trade is forbidden (p. "
            "78)."
        ),
    )
    _place(
        b,
        "Dotawo",
        inside=w["nobatia"],
        summary=(
            "A vassal kingdom of Makuria inside Nobatia, centred on Ado, whose "
            "crown is given to each eparch to pay for his office (pp. 77-78)."
        ),
    )
    _place(
        b,
        "Akasha",
        inside=w["batn"],
        summary=(
            "A fortress in the Batn al-Hajar with a garrison guarding Nobatia "
            "from the Banu al-Kanz (p. 78)."
        ),
    )
    _place(
        b,
        "The Lost Temple of Ramses",
        inside=w["nobatia"],
        **RUMOUR,
        summary=(
            "Twin temples said to be carved from a mountain somewhere above "
            "Philae, under millennia of sand, which treasure hunters seek all "
            "over Lower Nubia. Pharaoh Ramses is said to have built them to "
            "intimidate his southern neighbours, claiming to have beaten them "
            "at Kadesh. The Great Temple was for Amun, Ra, Ptah and the "
            "deified pharaoh; the Small Temple for Hathor and his wife "
            "Nefertari (p. 79)."
        ),
        levels=[
            Builder.level(
                "The Temples",
                5,
                "Faerie",
                enter=(
                    "A troop of always twenty-two baboons, descended from those kept "
                    "at the temple, raise their arms each dawn to worship the sun. A "
                    "human who takes one's place in the rite sees the sun go through "
                    "the sand to light the temple's guardian statues, and may approach."
                ),
            )
        ],
        secrets=("Explorers fail because the temples lie in a Faerie regio of aura 5."),
    )
    w["menarti"] = _place(
        b,
        "Menarti",
        inside=w["nobatia"],
        summary=(
            "A small island at the foot of the second cataract, 'island of "
            "Mei', Saint Michael. It is the upriver limit of navigation from "
            "Egypt (p. 79)."
        ),
    )
    b.church(
        "Monastery of Menarti",
        church=MONASTERY,
        place=w["menarti"],
        summary="A small monastery under Saints Michael and Cosmas (p. 79).",
    )
    b.town(
        "Takoa",
        place=w["menarti"],
        answers_to=w["eparch"],
        summary=(
            "A small town on Menarti's southern tip, a customs post between "
            "Lower and Upper Nubia. No foreign merchant may pass: all cargo is "
            "given up here and goes on to the eparch (p. 79)."
        ),
    )
    _place(
        b,
        "The Tumulus Graves of Nobatia",
        inside=w["nobatia"],
        aura=1,
        summary=(
            "Massive tumuli on both banks hold kings and princes, many "
            "enclosing palaces or compounds with rich grave goods and "
            "sacrificed animals, especially dogs. Most are pre-Christian "
            "kinglets', though the earliest Nobatian kings used them too "
            "despite their faith, for continuity. Each intact tumulus has a "
            "Magic aura of 1 (p. 80)."
        ),
        secrets="A tumulus may hold a grave guardian such as a mummified dog.",
    )


def _nobatian_towns(b: Builder, w: World) -> None:
    nobatia = w["nobatia"]
    w["kalabsha"] = b.town(
        "Kalabsha",
        place=nobatia,
        summary=(
            "Capital of the Blemmyae state after Kush, now the smallest of "
            "Nobatia's bishoprics. The temple the Blemmyae raised to Mandulis "
            "mostly still stands (p. 79). The northern end of the river's "
            "fortresses (p. 80)."
        ),
    )
    _place(
        b,
        "Temple of Mandulis at Kalabsha",
        inside=nobatia,
        summary=(
            "The temple the Blemmyae raised to Mandulis at their capital, "
            "mostly still standing (p. 79)."
        ),
    )
    w["pakhoras"] = b.town(
        "Pakhoras",
        charter="Church",
        place=nobatia,
        summary=paragraphs(
            "Bukharas in Arabic, sometimes called Faras: Nobatia's religious "
            "and cultural centre, though the eparch now rules from Premnis. "
            "Tons of sand blow in daily, and armies of 'sand-warriors' with "
            "buckets and spades clear the cathedral, the palace and the "
            "property of those who can pay. Dumped on the west side, the sand "
            "has silted the channel, turning the old island into a peninsula, "
            "and every few decades citizens raise their thresholds, and past "
            "generations their walls and roofs (p. 79).",
            "Most of the city is Kushite and in fine condition. The wall, ten "
            "paces high and three thick with three gates, encloses three "
            "sides, leaving the east to poor defence by the river, and is "
            "extended upwards as the sand rises. The former king's palace, the "
            "highest point, lies empty at the centre, richly set with statues "
            "of lion-headed Kushite gods. One of two ancient Egyptian temples "
            "is mostly ruin, the other a warehouse.",
            "It has a large monastery on a hill outside, a smaller one within "
            "whose pottery factories make fine vessels sold through Nubia and "
            "beyond, six churches around the cathedral, and a mosque for "
            "foreign traders, though the bishop forbids the public call to "
            "prayer. A large market sells exotic goods from Alodia and beyond. "
            "Outside the southern gate a tent city of drovers tends visitors' "
            "beasts, and escorts and mercenaries from Atbara will arrange "
            "passage over the river and south to Alodia without entering "
            "Makuria.",
            "The town stands on the Kom, a hill that was the original island (p. 79).",
        ),
        secrets=(
            "The first Nubians here slew the giant who embodied the Kom, a "
            "powerful servant of the Red. They crushed its bones and fed them "
            "to livestock, shredded its flesh for birds, fed those beasts to "
            "dogs and lions, then killed and burned those and scattered the "
            "ashes. Some believe the daily sand is the Kom, remaking its body. "
            "If so it is winning: more sand arrives than can be removed, and "
            "some claim the heaps ripple like muscles about to flex."
        ),
    )
    b.church(
        "Cathedral of Pakhoras",
        church=SEE,
        place=w["pakhoras"],
        summary=(
            "A large and imposing cathedral, kept clear of sand by the city's "
            "sand-warriors (p. 79)."
        ),
    )
    _place(
        b,
        "Serra",
        inside=nobatia,
        summary=(
            "An old pharaonic fortress across the river from Pakhoras, "
            "refortified and held by its soldiers. Pakhoras plans to evacuate "
            "here if invaded, and it keeps plenty of food and firewood (p. 80)."
        ),
    )
    w["philae"] = _place(
        b,
        "Philae",
        inside=nobatia,
        summary=paragraphs(
            "A pair of islands in the first cataract, the Pearl of Egypt. The "
            "smaller, Philae proper, was sacred to Egyptians and Nubians as a "
            "burial place of Osiris; 'The Unapproachable', it could be landed "
            "on only after the proper rites. No birds fly over it and no fish "
            "can be caught from its shores. The larger, Senmut or Beghé, bears "
            "monuments to the pharaohs and emperors who claimed Egypt (p. 80).",
            "Pharaonic and Graeco-Roman building covers most of both islands, "
            "above all the temples of Isis, Amun-Osiris, Hathor and Horus. The "
            "land around, the Dodekachoenus, was the estate of Isis and kept "
            "the priests of the Great Temple. It is now held by the Banu "
            "al-Kanz, and the few inhabitants, mostly monks and lay brothers "
            "of a small monastery, feel besieged, though the well-fortified "
            "island has not been seriously tried. One of the first Nubian "
            "bishoprics, its seat moved to Kalabsha.",
        ),
    )
    w["premnis"] = b.town(
        "Premnis",
        charter="Noble lord",
        ruler="The Eparch of Nobatia",
        answers_to=w["eparch"],
        place=nobatia,
        summary=paragraphs(
            "Pedeme to Kush, Qasr Ibrim to the Arabs: a fortified hilltop "
            "town, Nobatia's administrative centre. It began as seven temples "
            "of the Nubian pharaohs; the Ptolemies circled it with a massive "
            "wall. With Nobatia's conversion, placed here in the seventh "
            "century, the temples became churches and it grew into a true town "
            "(p. 80).",
            "Ayyubid forces took it in 1172. After their expulsion the "
            "defences were improved, secular buildings went up among the "
            "religious, irregular stone housing filled a large two-level "
            "piazza over one temple, and the eparch moved his administration "
            "here from Pakhoras. High above the valley, it need not be "
            "abandoned at the flood, though it does become an island. Foreign "
            "merchants usually pass on to Pakhoras.",
        ),
    )
    b.church(
        "Cathedral of Our Lady the Pure Virgin",
        church=SEE,
        place=w["premnis"],
        summary=(
            "The stone cathedral of Premnis, damaged in the Ayyubid invasion "
            "of 1172 (p. 80)."
        ),
    )
    w["sai"] = _place(
        b,
        "Sai Island",
        inside=nobatia,
        summary=(
            "The largest permanent island on the Nile, six miles by three. A "
            "large pharaonic brick fortress stands on its east shore, and a "
            "small town surrounds the cathedral of one of Nubia's bishops (p. "
            "80)."
        ),
    )


# -- Makuria --


def _makuria(b: Builder, w: World) -> None:
    w["makuria"] = _place(
        b,
        "Makuria",
        inside=w["nubia"],
        summary=paragraphs(
            "Perhaps the most important Nubian kingdom, from the third to the "
            "fifth cataract, covering the heart of lost Kush yet distinctly "
            "Greek in nature, with nothing Kushite left. It is peaceful and "
            "prosperous, with many towns and broad fertile fields, though "
            "people are gathering into defensible towns with stores of food, "
            "firewood and water, partly against the Bedouin who have entered "
            "the eastern desert (p. 81).",
            "Foreign trade is a royal monopoly run through Nobatia, and no "
            "money circulates. Foreign traders may not sell here on pain of "
            "losing all their goods, even if they are only passing upriver.",
        ),
    )
    w["great_king"] = b.lord(
        "The Great King of Makuria",
        title="",
        wealth="Wealthy",
        seat="Dongola",
        place=w["makuria"],
        summary=(
            "The megalobasilikos, whose ministers and court bear Byzantine "
            "titles. Each town is its own kingdom, and thirteen vassal kings, "
            "the domestikoi, pay him tribute. All of them, the great king too, "
            "are priests who say Mass for their realms, until a king takes a "
            "life and can say it no more. He can reduce any subject to a "
            "slave, guilty or not. He takes counsel from a host of ministers "
            "and a court of seven bishops. The succession is matrilinear, a "
            "king's sister's son before his own, and crises are common when no "
            "heir is clear (p. 81)."
        ),
        secrets=(
            "Five years ago his armies uprooted and burned Abu Hamad. That "
            "night a visitor came to his bedchamber, and since then he has "
            "forbidden anyone to try again."
        ),
    )
    w["eparch"].answers_to = w["great_king"].id
    w["abu_hamad"] = b.town(
        "Abu Hamad",
        charter="Rules itself",
        place=w["makuria"],
        summary=(
            "A tent city at the end of the great bend of the Nile, the only "
            "Muslim settlement in Makuria by the book's account of it (though "
            "see Samna) and a thorn in the kingdom's side. Its people are "
            "Ja'alin Bedouin, who come and go to trade, arrange marriages, "
            "hold festivals and honour their dead, and Arabic is its chief "
            "tongue. Armies of the domestikoi and the great king have tried to "
            "clear it, and it simply reforms; the last attempt was five years "
            "ago. Makurian spies see that one set of tents at the heart of the "
            "camp never moves, and they have never got inside (p. 81)."
        ),
        secrets=(
            "Those tents are the opulent home of 'Izz el-Afram Hamad, the "
            "Master of Abu Hamad."
        ),
    )
    w["atbara"] = b.town(
        "Atbara",
        charter="Rules itself",
        place=w["makuria"],
        summary=(
            "A frontier town at the meeting of the Atbara and the Nile, "
            "fiercely independent of Makuria and Alodia and rich enough to "
            "stay so. It controls river traffic for the fifth cataract, ends "
            "the Pakhoras road that takes trade round Makuria to Alodia, and "
            "ends the only safe road to Sawakin. Its guides wear green turbans "
            "(p. 81)."
        ),
        secrets=(
            "The Blemmyae spare caravans led by Atbarans, and in return their "
            "chiefs are told the route and goods of the occasional rich "
            "caravan that somehow cannot get an escort. The Atbarans have a "
            "like alliance with the Ja'alin at Abu Hamad, so that caravans for "
            "their rivals never arrive."
        ),
    )
    w["berber"] = b.town(
        "Berber",
        place=w["makuria"],
        answers_to=w["great_king"],
        summary=(
            "The last Makurian town before Alodia, given Atbara's doubtful "
            "loyalty. It used to end the Pakhoras road, but the Ja'alin now "
            "attack caravans bound for it and leave those for Atbara alone, "
            "and it has shrunk to a tenth of its people. Many think Atbara "
            "pays them to keep it poor (p. 81)."
        ),
    )
    w["kallama"] = b.town(
        "Kallama",
        charter="Church",
        place=w["makuria"],
        summary=(
            "A town grown up around Makuria's smallest cathedral, existing "
            "only to serve the bishop and the monastery attached to his see "
            "(p. 82)."
        ),
    )
    w["galu"] = _place(
        b,
        "Galu",
        inside=w["makuria"],
        summary=(
            "A Napatan fortress, ruined and half in the sand, over the Wadi "
            "Howar, once an important seasonal spring and road west. The wadi "
            "is dry, its settlements are gone, and the land is a desolate "
            "waste (p. 84)."
        ),
        secrets=(
            "Galu caused the failure. It was built on the home of the wadi's "
            "spirit after Napatan priests slew it, hoping to take over the "
            "water's flow; the effect did not last, and the fortress was left "
            "guarding a road to nowhere."
        ),
    )
    b.church(
        "Ghazali",
        church=MONASTERY,
        place=w["makuria"],
        summary=(
            "One of Nubia's largest monasteries, a large church of the Holy "
            "Trinity amid living quarters and a commemorative complex, inside "
            "a high whitewashed wall of stone faced with brick. Monks are "
            "buried in a barrel-vaulted crypt, and it has a hospice for "
            "visitors and a hospital for the sick and dying (p. 84)."
        ),
    )
    w["kerma"] = _place(
        b,
        "Kerma",
        inside=w["makuria"],
        aura=3,
        summary=paragraphs(
            "Capital of a kingdom older than Kush. The circular royal palace "
            "lies in ruins beside two deffufa, solid mud-brick towers thirty "
            "paces high; remains of a towered wall over two miles long enclose "
            "room for 10,000 (p. 85).",
            "The cemetery runs over a mile north to south, with an estimated "
            "25,000 graves: low mounds under thousands of pebbles, often "
            "clustered round a larger one, some white, some black and a few of "
            "both, for no known reason. Dozens of huge royal tumuli stand at "
            "the southern end, four over a hundred paces across. A Magic aura "
            "of 3 clings to those four, 2 to the rest of the royal cemetery "
            "and 1 to the other graves.",
        ),
    )
    b.town(
        "Negila",
        place=w["makuria"],
        answers_to=w["great_king"],
        summary=(
            "A small oasis on the Darfur caravan road, claimed by Makuria on "
            "the edge of Alodian Bayuda. It holds a Makurian outpost with a "
            "unit of Struthophagi mounted on ostriches, swift messengers and "
            "scouts (p. 85)."
        ),
    )
    w["elephants"] = _place(
        b,
        "The Valley of Elephants",
        inside=w["makuria"],
        summary=(
            "Marshes in a lush stretch of the Nile where elephants gather in "
            "great numbers for the food, above all a sweet rush they cannot "
            "get enough of. The serpents that usually hunt elephants do not "
            "come here, oddly. The herds wreck farming and have driven people "
            "to the marsh edges, where they raise what crops they can hide or "
            "protect and live in tents they can strike when sentries see "
            "elephants coming (p. 86)."
        ),
        secrets=(
            "The sweet rush is hateful to the giant serpents of the gorges "
            "round about, or so the Old Man of the Forest says."
        ),
    )


def _dju_waab(b: Builder, w: World) -> None:
    w["dju_waab"] = _place(
        b,
        "Dju Wa'ab",
        inside=w["makuria"],
        aura=3,
        summary=paragraphs(
            "'The pure mountain', Jebel Barkal to the Egyptians: a small "
            "flat-topped mountain in a bend of the Nile, only a hundred paces "
            "high but sheer above a flat land, a landmark at one of the few "
            "crossings of the river and an opening for east-west trade. To "
            "Kush it was the world's centre, where the creator stood to bring "
            "the universe into being, and a huge free pinnacle at its south "
            "corner seemed a natural statue of a god. Around it lie the steep "
            "pyramids of Nubian pharaohs, Kushite rock tombs and tumuli of "
            "pagan Makurian kings (p. 82).",
            "It has a Magic aura of 3 as a striking natural feature, and "
            "burial sites may be higher. The temples' Faerie auras may once "
            "have surpassed that, but most have gone with their worshippers.",
            "Nubian pyramids (p. 84). Unlike Egypt's they are steep, seventy "
            "degrees against about forty-five, so one thirty paces high may be "
            "twenty wide where Egypt's would be sixty. Each has a pylon gate "
            "and temple at its base. The body lay ten or more paces beneath, "
            "down steep stairs, past an antechamber for offerings like an "
            "Egyptian serdab. Otherwise tomb contents are like Egypt's.",
        ),
    )
    w["napata"] = _place(
        b,
        "Napata",
        inside=w["dju_waab"],
        summary=(
            "The first capital of Kush, at the foot of Dju Wa'ab, dominated by "
            "the priesthood, with over two dozen temples to single gods and to "
            "combinations with sacred meanings. Incense and chanting once fed "
            "the faerie gods and kept a Faerie aura. The temples are empty and "
            "the priests long dead; no aura remains, though echoes of those "
            "gods linger (p. 83)."
        ),
    )
    _place(
        b,
        "Kurru",
        inside=w["dju_waab"],
        aura=2,
        summary=(
            "The first pyramid field of the rulers of Kush, in Dju Wa'ab's "
            "shadow. Over fifty pyramids remain, fewer than half still "
            "standing; five emperors' survive, with fourteen queens', some of "
            "them renowned warriors. Two centuries of use left a Magic aura of "
            "2 (p. 83)."
        ),
    )
    _place(
        b,
        "Nuri",
        inside=w["dju_waab"],
        aura=5,
        summary=(
            "The later pyramid field, on the west bank opposite Napata, in use "
            "about five hundred years until Arqamani moved the royal cemetery "
            "to Meroë, which left a Magic aura of 5. The tombs of 21 emperors "
            "stand on two plateaus with those of 52 kings' mothers, wives and "
            "princes. The western plateau has the largest and oldest, that of "
            "Taharqa, king of Kush and pharaoh of Egypt, over fifty paces "
            "high, with the parallel lines of kings' wives' pyramids and the "
            "necropolis of the kentakes, the kings' mothers. The eastern "
            "plateau holds the other twenty emperors, each in a sarcophagus of "
            "a dozen tons or more (p. 83)."
        ),
    )


def _dongola(b: Builder, w: World) -> None:
    w["dongola"] = b.town(
        "Dongola",
        charter="Noble lord",
        ruler="The Great King of Makuria",
        answers_to=w["great_king"],
        place=w["makuria"],
        summary=paragraphs(
            "Makuria's capital, built by King Merkurios on a bluff on the east "
            "bank where the Wadi Howar meets the Nile, at the south end of the "
            "fertile Letti Basin, and commanding all movement along that bank. "
            "Within a day's journey lie about thirty villages of fine "
            "buildings, churches and monasteries, palms, vines, gardens, "
            "fields and broad pastures (p. 83).",
            "The high stone wall that first defended it is now the innermost "
            "of seven, one for each stage of growth, with a large suburb to "
            "the north. Over ten thousand are estimated to live here, in big "
            "houses often of two storeys on wide streets. It is a weaving town "
            "(p. 77). The royal palace alone is of red brick, several storeys "
            "above anything else, with domes on top.",
        ),
    )
    w["granite"] = b.church(
        "The Church of the Granite Columns",
        church=SEE,
        place=w["dongola"],
        summary=(
            "Dongola's cathedral, a square building whose sixteen polished "
            "granite columns stand in four rows, the wide nave crossed by a "
            "narthex to make a cruciform plan inside. They hold up a mighty "
            "dome, and a true master painted its vivid Biblical frescoes. "
            "Dominion aura 7 within. The originals of the Baqt of 652 and 835 "
            "are stored here (pp. 73, 83)."
        ),
    )
    b.church(
        "The Church of the Angels",
        church=MOSQUE,
        place=w["dongola"],
        summary=(
            "An impressive cruciform church in Dongola, famous for a "
            "many-coloured stone pavement that ripples like the river in the "
            "sun. Dominion aura 6 (p. 84)."
        ),
    )


def _darfur(b: Builder, w: World) -> None:
    w["darfur"] = _place(
        b,
        "Darfur",
        inside=w["makuria"],
        summary=(
            "A region far from the Nile yet firmly under Makuria, living on "
            "the slave trade. Its buildings are of distinctive red brick, "
            "built as flat-topped truncated cones up to fifty paces across at "
            "the base, twenty-five at the top and six high, each shared by "
            "several families (p. 85)."
        ),
    )
    b.faction(
        "The Tajuwa",
        faction="People or tribe",
        place=w["darfur"],
        summary=(
            "The people of Darfur. They look like the slave races they "
            "capture, with tight curly hair and scant beards, but have Nubian "
            "height, suggesting old mixing. Both sexes wear ankle-length "
            "smocks copied from the Arab djellebah, often striped linen; those "
            "who need freer clothes wear loose trousers and no shirt. Their "
            "warriors are mostly caravan guards with weapons and armour to "
            "personal taste, swords being uncommon. They are lax Christians at "
            "best: their churches, staffed by Nubian priests, stand nearly "
            "empty at the Eucharist, and they have sought no other gods (pp. "
            "85-86)."
        ),
    )
    w["uri"] = b.town(
        "Uri",
        ruler="The chief of the Tajuwa",
        answers_to=w["great_king"],
        place=w["darfur"],
        summary=(
            "The royal palace of the chief of the Tajuwa, Makuria's vassal, "
            "and a long-distance market at the crossing of the Darb al-Arba'in "
            "and the Tarik al-Sudan, the savannah route west across the Great "
            "Desert (Between Sand and Sea) (p. 85)."
        ),
    )
    b.church(
        "'Ayn Farah",
        church=MONASTERY,
        place=w["darfur"],
        summary=(
            "A red-brick monastery and church of Egyptian Copts, founded to "
            "convert the slaves. Every slave on the Darb al-Arba'in is in "
            "theory offered baptism, but slavers rarely stop, so the monks "
            "stand on the walls and shout Christ's salvation at the passing "
            "lines. The slaves seldom understand; the monks try to learn the "
            "Slavelands' many tongues but get little practice (p. 85)."
        ),
    )
    b.town(
        "Fasher",
        place=w["darfur"],
        summary=(
            "The main starting point for expeditions into the Slavelands: an "
            "oasis with few lasting buildings, a camp of slavers, caravan "
            "guards and camel and cattle drovers, with a thriving rope-making "
            "trade. Slaves from the south are penned here like the stock taken "
            "with them (pp. 85-86)."
        ),
    )
    b.town(
        "Samna",
        place=w["darfur"],
        summary=(
            "A town of Tajuwa red brick, with one of Makuria's only mosques, "
            "for the Arab slave traders (p. 86)."
        ),
    )


# -- Alodia --


def _alodia(b: Builder, w: World) -> None:
    w["alodia"] = _place(
        b,
        "Alodia",
        inside=w["nubia"],
        summary=paragraphs(
            "The most remote Nubian kingdom, from the fifth cataract to beyond "
            "the meeting of the Blue and White Niles. It is held to be "
            "stronger than Makuria: richer in gold, more fertile, larger, with "
            "a bigger and better-armed army (pp. 86-87).",
            "Its nine subkingdoms are Atbai, Bayuda, Butana, Gezira, Kabushia, "
            "Kassala, Keraba, Meroë and Soba.",
        ),
    )
    w["king_alodia"] = b.lord(
        "The Great King of Alodia",
        title="",
        wealth="Wealthy",
        seat="Soba",
        place=w["alodia"],
        summary=(
            "A great king like Makuria's, ruling nine subkingdoms from Soba. "
            "His army has a strong presence in rebellious Gezira. Royal Meroë "
            "has resented his rule through several failed coups (pp. 86, 88, "
            "90)."
        ),
    )
    w["mortuary"] = b.faction(
        "The Mortuary Society of Kassala",
        faction="Hedge coven",
        decides="A council",
        tradition=EXORCISTS,
        place=w["alodia"],
        wants="To limit the power of the Cult of Dedun.",
        summary=paragraphs(
            "The society that cares for Alodia's dead, based at Kassala with "
            "offices in every city. Its members are shunned as unlucky and "
            "respected for doing what must be done. By law they wear plain "
            "white linen smocks with a black sash; most add a black fez-like "
            "hat and a glass bell, and all carry a pouch of powder that wards "
            "off the dead (p. 88).",
            "Every Alodian pays a mandatory burial tax in gold dust, most of "
            "which pays the society. Should a foreigner die in Alodia his "
            "family or friends must pay for the body, or it is usually left to "
            "scavengers, and the unburied dead are the likelier to haunt those "
            "who did not bury them (pp. 88-89).",
            "Kassalan Exorcists (p. 89) deal with the dead who will not accept "
            "their place. Their Virtue, tradition and Kassalan Dust are the "
            "Kassalan Exorcists' chapter.",
        ),
        secrets=(
            "The society's upper ranks know of the Cult of Dedun, and much of "
            "its work is designed to limit it: church burial for everyone, in "
            "anonymous graves so the famous cannot be found, guarded "
            "mausoleums, and magic that counters the cult's sorcerers. Its "
            "assassins killed Artanyeszame's master."
        ),
    )
    w["ministry"] = b.faction(
        "The Ministry of Works",
        faction="Hedge coven",
        tradition=ALCHEMISTS,
        decides="Its leader",
        place=w["alodia"],
        offers="The wonders of Soba, and training in Soban Alchemy.",
        summary=paragraphs(
            "The department that keeps and improves Soba, employer of most of "
            "its alchemists, who wear red robes and can be seen leading "
            "building crews or restoring public works and art. State "
            "alchemists teach the next generation at the Ministry buildings. "
            "Summae and tractatus on Soban Alchemy exist in Nubian Greek, many "
            "jealously held by rich families (p. 93).",
            "Alchemist of Soba and Soban Alchemy (Virtues and Ability) are the "
            "Soban Alchemists' chapter, pp. 93-94. Alchemists tend to set up "
            "in the lacunae of the city's Dominion to spare themselves its "
            "penalties. Some believe the art is the last of the magic that "
            "raised the monuments of Egypt and Kush.",
        ),
    )
    b.lord(
        "The Qore and Kentake of Meroë",
        title="",
        seat="Taqasi",
        answers_to=w["king_alodia"],
        place=w["alodia"],
        summary=(
            "King and queen mother of the city-state of Meroë, who rule "
            "together. They have often risen against Soba and failed. They are "
            "widely believed to be pagan worshippers of Apedemak: the lion is "
            "their symbol, they sit on a lion throne and they keep lions as "
            "pets (p. 90)."
        ),
    )


def _alodian_kingdoms(b: Builder, w: World) -> None:
    alodia, king = w["alodia"], w["king_alodia"]
    atbai = _place(
        b,
        "Atbai",
        inside=alodia,
        summary=(
            "Alodia's easternmost, driest and poorest kingdom, with no "
            "minerals to trade. Its people are mostly herders, with some Red "
            "Sea fishing villages. The northern border is disputed with the "
            "Blemmyae, and its king has left the villages he cannot afford to "
            "defend to their mercy (p. 87)."
        ),
    )
    b.town(
        "Goz Regeb",
        place=atbai,
        answers_to=king,
        summary=(
            "Atbai's only town of size, seat of a bishop, with a cathedral "
            "modest for Alodia (p. 87)."
        ),
    )
    _place(
        b,
        "Taflin",
        inside=atbai,
        summary=(
            "A fertile area where Atbaik nomads bring their flocks in the "
            "rains for a month-long festival of stock trading and marriage "
            "arrangements. Ball games are discouraged, out of respect for the "
            "Dihi (p. 87)."
        ),
    )
    b.faction(
        "The Dihi",
        faction="People or tribe",
        place=atbai,
        summary=paragraphs(
            "Children of Blemmyae and humans in northern Atbai. They look like "
            "the human parent, but have Blemmyae ears on the upper torso, and "
            "at their first great shock or excitement the head falls clean off "
            "the shoulders. This does not harm them and it can be put back, if "
            "they live. After that it may fall in any strenuous effort or "
            "emotional stress. Some lions of Atbai have learned to ambush "
            "Dihi, since a headless body is easy prey. A Dihi careful enough "
            "to keep his head on before having children has normal children; "
            "an afflicted Dihi's are afflicted. Most think it a curse; a few "
            "have found uses for it (p. 86).",
            "Rules (p. 86): take Lesser Malediction. In physical or emotional "
            "stress roll a stress die: on 9 or more the head comes off, and "
            "also on any botched physical roll, when it may roll away. The "
            "head is deaf and the body blind, but a head that can see its body "
            "can shout it commands. Reattaching takes a round. Dihi often have "
            "Magical Blood (Realms of Power: Magic p. 46) to balance it.",
        ),
    )
    bayuda = _place(
        b,
        "Bayuda",
        inside=alodia,
        summary=(
            "Unlike its fellows, a kingdom of countless small villages "
            "scattered through sandy desert into the Gilif Hills, with no one "
            "city. Each village seems to have its own language, unrelated to "
            "any neighbour's or to Nubian (p. 87)."
        ),
        secrets=(
            "They all speak one language, but under a magical curse no native "
            "Bayudan can understand another speaking it. An outsider who "
            "learns it from any village is understood by all."
        ),
    )
    _place(
        b,
        "The Gilif Hills",
        inside=bayuda,
        summary=(
            "Deep ravines and jagged crags, an unforgiving land said to be "
            "haunted by leopard spirits. It does hold uncommonly many "
            "leopards, and some may have supernatural powers. For the Gilif "
            "leopards use the lion's statistics (The Book of Mundane Beasts) "
            "with Size +1, which takes 2 from Strength and adds 1 to Quickness "
            "(p. 87)."
        ),
    )
    butana = _place(
        b,
        "Butana",
        inside=alodia,
        summary=(
            "A sheltered kingdom between Keraba and Soba, Alodia's main "
            "farmland, well watered by tributaries of the Nile and the Atbara. "
            "Its people are known for hard work and helped by Soba's "
            "alchemists, who rely on Naqan glass (p. 87)."
        ),
    )
    b.town(
        "Naqa",
        place=butana,
        answers_to=king,
        summary=(
            "Capital of Butana, an old city of Meroë's age on the seasonal "
            "Wadi Awateib, where lesser wadis come down from the plateau, "
            "thirty miles from the Nile. It is a trading city on the way to "
            "Ethiopia, and many slaves from the south get their first taste of "
            "civilisation here. It is famed for glass: unusually pure sand "
            "gives a clear glass with a slight green tinge, traded north in "
            "ingots, and its glassblowers are justly respected (pp. 87-88)."
        ),
    )
    gezira = _place(
        b,
        "Gezira",
        inside=alodia,
        summary=(
            "The southernmost and newest kingdom, between the White and Blue "
            "Niles, the least Nubian, sharing blood with Ethiopians and "
            "Aithiopes, and poorer than the others. Known for rebellion, many "
            "of its people see their vassalage as conquest, and the great "
            "king's army may provoke more riots than it prevents (p. 88)."
        ),
    )
    b.town(
        "Sennar",
        place=gezira,
        ruler="The monarch of Gezira",
        answers_to=king,
        summary=(
            "Capital of Gezira, home of a dynasty of Nubian and Megabaran "
            "blood (chapter 9). Men and women are equal among the Gezirans, "
            "the monarch is as often a queen as a king, and a quarter of the "
            "army are warrior women quartered here (p. 88)."
        ),
    )
    b.town(
        "Kabushia",
        place=alodia,
        answers_to=king,
        summary=(
            "The Gates: the northernmost and among the most heavily fortified "
            "subkingdoms, its city full of warriors, its outer districts "
            "growing food for the standing army, with whole villages of smiths "
            "turning Meroë's iron into weapons. No friend of Makuria: in the "
            "Umayyad invasion the Makurian royal family, sent south for "
            "safety, were seized by its king and ransomed at an extortionate "
            "price, and it has never let its great neighbour forget it (p. 88)."
        ),
    )
    w["kassala"] = b.town(
        "Kassala",
        place=alodia,
        answers_to=king,
        summary=paragraphs(
            "Home of the Mortuary Society and a city of the dead, with more "
            "dead than living among its tombs, cemeteries and monuments. Some "
            "graves are ancient, most from Christian Alodia, belonging to "
            "those deemed worth remembering for money or fame. No trade route "
            "comes near it; one road crosses the plain from the west (p. 88).",
            "Other cities pay Kassalans to take their corpses. Porters gather "
            "the bodies for morticians to prepare, hired pallbearers carry "
            "them, and priests do little but the burial rite. Others make "
            "shrouds, death masks and incense, or work as mourners and grave "
            "guardians. With so small a congregation it has no Dominion aura, "
            "and some parts have a weak Magic aura.",
            "Embalming is rare: most are wrapped in plain shrouds, with a clay "
            "or metal mask, and the wrappings often bear protective texts of "
            "folk-magical value. For more, the flesh is taken from the bones, "
            "which is held to speed the soul to redemption, ward off ghosts "
            "and foil sorcerers.",
        ),
    )
    keraba = _place(
        b,
        "Keraba",
        inside=alodia,
        summary=(
            "A kingdom ruled from el-Hobagi when power drifted upstream after "
            "Kush, then eclipsed by Soba in the sixth century and made a "
            "vassal. It is now ruled from Sufra (p. 89)."
        ),
    )
    b.town(
        "Sufra",
        place=keraba,
        answers_to=king,
        summary="The present seat of the kings of Keraba (p. 89).",
    )
    _place(
        b,
        "El-Hobagi",
        inside=keraba,
        realm="Faerie",
        aura=3,
        summary=(
            "A huge tumulus, one of Alodia's last pagan royal burials, among "
            "other high-status tombs. It has never been entered, despite tales "
            "of wealth; if it is like others, the entrance is at the summit, "
            "with a shaft going down. Beside it a temple of ram-headed Atum is "
            "in remarkable repair, with a Faerie aura of 3, as though still "
            "used, though no one has ever been seen to enter (p. 89)."
        ),
    )
    b.town(
        "Kawa",
        place=alodia,
        answers_to=king,
        summary=(
            "One of Alodia's six episcopal sees, named only in that list (p. 76)."
        ),
    )
    b.town(
        "Shanqir",
        place=w["makuria"],
        answers_to=w["great_king"],
        summary=(
            "One of the seven episcopal sees of Makuria and Nobatia, named "
            "only in that list (p. 76)."
        ),
    )


def _meroe(b: Builder, w: World) -> None:
    w["meroe"] = b.town(
        "Meroë",
        ruler="The Qore and Kentake of Meroë",
        answers_to=w["king_alodia"],
        place=w["alodia"],
        summary=paragraphs(
            "Medewi to its builders, raised by King Aspelta of Kush six "
            "centuries before Christ as his chief palace, capital after "
            "Arqamani took the empire from the priests around 300 BC. At its "
            "height it ruled the whole Upper Nile; now it is a city-state "
            "within Alodia, and the Island of Meroë is the vast triangle "
            "between the Nile and the Atbara that it rules (p. 89).",
            "It is famed for iron and then gold. Its outskirts look almost "
            "industrial with bloomeries and blast furnaces, and Meroitic "
            "ironwork is prized far and wide. Its people have a superior air, "
            "born of their ancient heritage (pp. 89-90).",
        ),
        secrets=(
            "The Initiation Script of the Undying Ones survives only among the "
            "writings on the monuments here, a site the Mortuary Society "
            "patrols (p. 100)."
        ),
    )
    w["taqasi"] = _place(
        b,
        "Taqasi",
        inside=w["alodia"],
        summary=(
            "The chief residence of the King of Meroë, a palace of about "
            "twenty rooms on two levels round a courtyard, with a ramp to a "
            "podium, amid luxurious grounds. A pride of lions roams the "
            "manicured 'jungle', fed on live prey released within the walls, "
            "so it is unwise to come uninvited. From the podium the king and "
            "kentake receive visitors and watch the lions feed; if a meeting "
            "goes badly, the two may be combined (p. 90)."
        ),
    )
    w["begarawiyah"] = _place(
        b,
        "Begarawiyah",
        inside=w["alodia"],
        aura=5,
        summary=paragraphs(
            "The royal necropolis outside Meroë, the widest of Kush's three "
            "(with Kurru and Nuri) (p. 90).",
            "Southern cemetery: the oldest, of the same age as Nuri, with nine "
            "pyramids, four of them emperors' and five princes' and queens', "
            "and 195 unmarked tombs of commoners. Magic aura 4, from over four "
            "hundred years of royal burial.",
            "Northern cemetery: used after Arqamani moved the capital. His "
            "pyramid stands with those of 29 other kings and 27 kentakes, "
            "queens and royals, and just three non-royal tombs. Magic aura 5, "
            "from six and a half centuries.",
            "Western cemetery: 113 tombs, none royal and so no pyramids, "
            "simple and poorly preserved. No Magic aura.",
        ),
        secrets=(
            "This is the haunt of Alodia's most powerful devotees of Dedun, "
            "and some pyramids are occupied, with higher Magic auras aligned "
            "to the dead. Artanyeszame excludes all other Undying Ones from "
            "the southern cemetery. Two more dwell in the northern and a third "
            "in the western."
        ),
    )


def _soba(b: Builder, w: World) -> None:
    w["soba"] = b.town(
        "Soba",
        charter="Noble lord",
        ruler="The Great King of Alodia",
        answers_to=w["king_alodia"],
        place=w["alodia"],
        summary=paragraphs(
            "Alodia's capital, on the east bank of the Blue Nile just above "
            "its meeting with the White, spread over a gently rolling plain "
            "cut by shallow streams. People live on the mounds between them, "
            "with wide open land around. Gravel mounds hold big wooden houses "
            "coated in white clay that glitters with mica, each in a lush "
            "garden. Red-brick mounds bear seventeen churches decorated with "
            "gold leaf, chief of them the Church of Manbali, the cathedral. "
            "The Dominion is 3 near these, with many lacunae where it does not "
            "reach. Small monasteries, each of a few monks, stand around the "
            "town and on the banks. It alone in Alodia has a mosque, for a "
            "sizeable population of Muslims from Egypt and the southern "
            "sultanates (p. 93).",
            "The city is famous for its alchemists' wonders. Corner poles shed "
            "light at night to rival the moon. The streets are unusually "
            "smooth for wheels, and some Soban vehicles hover just off the "
            "ground. Streams, sometimes canalised, carry stone barges that "
            "float miraculously with grain and timber. Fountains run upwards, "
            "stone statues in gardens are tethered lest they float away, "
            "bridges are of transparent metal, and roof tiles make the city "
            "smell sweet.",
        ),
    )
    b.church(
        "Church of Manbali",
        church=SEE,
        place=w["soba"],
        summary=(
            "The most prominent and luxurious of Soba's seventeen churches, "
            "and its cathedral (p. 93)."
        ),
    )


# -- the Blemmyae --


def _blemmyae(b: Builder, w: World) -> None:
    w["hills"] = _place(
        b,
        "The Red Sea Hills",
        inside=w["nubia"],
        summary=(
            "The land between the Nile valley and the Red Sea, broadly the "
            "Blemmyae's, with the Pakhoras road to Atbara as its western "
            "border. Gold was found here under the Fatimids, and gold and "
            "emeralds are mined here. Treaties between Blemmyan and Makurian "
            "kings fix the limits but last only as long as the signatories' "
            "lives. Blemmyae and Makurians have lately found a common enemy in "
            "the Ja'alin (pp. 72, 77, 96)."
        ),
    )
    w["blemmyae"] = b.faction(
        "The Blemmyae Tribes",
        faction="Family",
        decides="Its leader",
        ruler="The King of the Blemmyae",
        place=w["hills"],
        summary=paragraphs(
            "A nomadic, warlike race of magic humans of the Red Sea Hills and "
            "the Nubian Desert, and of the Libyan Desert in the west, with no "
            "head or neck and a face on the upper chest. Libyan Blemmyae are "
            "merchants who lead camel trains. Nubian Blemmyae are aggressive "
            "and rightly feared. They herd camels for wool, leather, meat and "
            "milk, and hunt gazelle and ostrich. They raid caravans between "
            "Nobatia and Alodia for luxuries, and as their reputation means no "
            "resistance from Nubian merchants, most victims escape alive, "
            "often with their bulky goods. Bedouin get no such mercy: there is "
            "no treaty with them, and they are interlopers. Regular tribute to "
            "the Makurian and Alodian thrones is thinly veiled fines for past "
            "raids or bribes for future ones (pp. 95-96).",
            "Five tribes, named for five cities they once held: Phoinikon, "
            "Khiris, Taphis, Talmis and Prima. One king rules all, sometimes "
            "at Sawakin but more often among his family like any other "
            "Blemmya. He is respected and usually obeyed, but relies on the "
            "five phylarchs, tribal chiefs. On taking the crown he names as "
            "heir one phylarch, not his own tribe's, and cannot change it; if "
            "that phylarch dies the honour goes to his nearest male relative. "
            "Under them hypotyranni lead bands of about fifty families.",
            "Men outnumber women ten to one, but women do not age and bear for "
            "many generations, and bloodlines are watched lest a woman marry "
            "her descendants. They have resisted Christianity and Islam, "
            "worshipping the stars and Kushite gods, Mandulis above all. Their "
            "language, Beja, descends from Meroitic.",
            "Characters (p. 96). Their faces are larger than a man's between "
            "wide shoulders, their hearing is poor as their ears are under "
            "their arms, and their hairless bodies, bare above the waist, "
            "resist damage. Women have no breasts and feed children goat or "
            "camel milk. Armour needs eye holes or a visor, so must be rigid, "
            "and large shields are of little use; warriors tend to be mounted "
            "skirmishers with slings. They are Magic Humans (Realms of Power: "
            "Magic p. 32) with the inherited features the rules cite: Puissant "
            "Thrown Weapon, Tough, Hunchback and Poor Hearing, and for men Age "
            "Quickly, giving a human lifespan. They take a Social Status "
            "suited to their tribal role, or to their magical nature among "
            "humans.",
        ),
    )
    b.town(
        "Badi",
        charter="Rules itself",
        place=w["hills"],
        summary=(
            "Abandoned by honest merchants, a fetid pit of lawlessness whose "
            "long quays serve the pirates who prey on the Red Sea. Anything "
            "can be had here, and men can be hired to get what cannot be "
            "bought. The Blemmyae keep land travellers away for their own "
            "good, and few captains dare the sea: by standing order of Egypt "
            "and Arabia, ships known to have docked here forfeit the lives of "
            "captain and crew, and passengers are sold as slaves (p. 96)."
        ),
    )
    w["sawakin"] = b.town(
        "Sawakin",
        ruler="Sometimes the King of the Blemmyae",
        place=w["hills"],
        summary=paragraphs(
            "Ptolemy's Limen Evangelis, Port of Good Hope; both Sawakin and "
            "the Beja U Suk mean 'prisons'. Solomon is said to have banished "
            "his most troublesome jinn here, and as far as anyone knows they "
            "still sit in a magical jail no one can find (p. 96).",
            "A round island at the end of a long inlet, a fantastic town built "
            "wholly of bands of white, pink and red coral. Its lighthouse is "
            "so shaded from white at the base to red at the top that it can "
            "hardly be seen at dawn or dusk. Red coral has a strong sympathy "
            "with controlling demons (ArM5 p. 110), which might guide those "
            "seeking the prisons. It is the end of the only safe road from "
            "Atbara (p. 81).",
            "It rivals 'Aydhab, Badi and Qusayr, and is rising at Badi's "
            "expense on trade with Arabia, Persia and distant Hind and on "
            "passage to Mecca for the hajj. It sometimes exports coral, mostly "
            "'snake's tongue', forked twigs of rough red stone (p. 97).",
        ),
    )
    _place(
        b,
        "The Prisons of the Jinn",
        inside=w["hills"],
        **RUMOUR,
        realm="Magic",
        summary=(
            "The jail beneath Sawakin of the jinn Solomon banished, whose "
            "whereabouts no one knows (p. 96)."
        ),
        secrets=(
            "There are 111 jinn in prisons of coral beneath the town, all "
            "hostile to man. Most are petty nuisances Solomon would not free; "
            "a few are truly terrible. One is rumoured to be Ashmodai, Prince "
            "of Temptation, one of the ten mightiest demons save Satan himself "
            "(Realms of Power: the Infernal p. 27). No one knows, and any "
            "number of jinn claim to be him."
        ),
    )


# -- the Cult of Dedun --


def _cult_of_dedun(b: Builder, w: World) -> None:
    w["dedun"] = b.faction(
        "The Cult of Dedun",
        faction="Hedge coven",
        decides="A council",
        tradition=DEDUN,
        realm="Magic",
        place=w["nubia"],
        wants="Bodily immortality, and the return of its temporal power.",
        summary=paragraphs(
            "Dedun, the Egyptians' Dedwen and god of incense, was to the "
            "Kushite priests lord of what is gathered in this life for the "
            "next: prosperity, as the dead were buried with their goods; fame "
            "and reputation; the patron of priests who kept the dead's memory; "
            "guardian of the dead and lord of the fields of prosperity; god of "
            "salt, natron, naphtha and all that preserves. His chief centre "
            "was Napata. The struggle of priests and kings is often shown as "
            "the uraeus, his sign, fighting the lion of Apedemak (p. 97).",
            "Under this cult the pyramids of Napata and Meroë rose and the "
            "fields of the dead were tended. By holding the dead it ruled the "
            "living, until Arqamani, with the priests of Apedemak, stormed "
            "Napata, killed the priests and took the royal dead (p. 97). Few "
            "in Nubia now suspect it survives.",
        ),
        secrets=paragraphs(
            "The priesthood of Kush included Canaanite necromancers (Ancient "
            "Magic, chapter 2), some come with the Tribe of Dan, others after "
            "Saul's purge of Canaan's priests. Those seeking that Mystery may "
            "find clues leading here. Holding the royal dead, the priests held "
            "their living relatives, by the threat of wracking their spirits "
            "after death (p. 97).",
            "The cult lurks in graveyards and forgotten tombs. It now cares "
            "less for keeping the dead than for power over them, and the Red's "
            "subtle influence has made it, knowingly or not, a corrupting "
            "force serving oblivion. It is a Mystery Cult in informal "
            "districts, each worshipping at a grave site under a temple "
            "priest; those priests meet every few years. Most members above "
            "adherent seek magical power, not worship; its Mysteries are of "
            "the Magic realm, not Faerie. Some priests are fanatics, but none "
            "deceive themselves: it is a way to eternal life, once offered "
            "after death as an akh (chapter 4), and now as lordship over one's "
            "own decaying flesh (pp. 97-98).",
            "Adherents come from every walk of life, some from families loyal "
            "for centuries, some wooed by friends in the priesthood, some "
            "through curiosity about Kush's graves or research into long life "
            "or necromancy. They attend night rites at the local temple, "
            "usually four times a year, favour each other in daily life, and "
            "help when a temple priest asks. Altar priests assist the temple "
            "priest, keep the temple and the discipline, and silently kill an "
            "adherent who endangers secrecy; there are rarely more than four "
            "to a temple. A temple priest usually leaves family and normal "
            "life to live in squalor in his temple on what can be scrounged, "
            "sometimes on the bodies he steals, and gathers a court of noted "
            "corpses, each prepared by his own rite and bearing his name in "
            "Meroitic, which makes each a permanent Arcane Connection to him. "
            "There are currently a dozen Undying Ones along the Nile (pp. "
            "98-100).",
            "The cult teaches no magic of its own, but draws the unsavoury. "
            "Sorcerers among it are often Learned Magicians, or have Corpse "
            "Magic, the Goetic Arts (Summoning and Commanding, in a version "
            "that reaches ghosts and bears an Infernal taint), or curse magic "
            "such as Hex, Cursing, the Vulnero Art or Malediction (p. 102).",
            "The ranks, Initiation Scripts, Virtues, court strength, the loss "
            "of the Gift, the common powers of the Undying Ones and Corpse "
            "Magic are the Cult of Dedun's chapter and rules/africa.py (pp. "
            "98-102). The errata (p. 87) correct the temple priest's script: "
            "she will not necessarily become bedridden and die of old age at "
            "Decrepitude 5.",
            "Under the Empire of Kush a body was embalmed, coated in molten "
            "glass and set on a pillar, visible for all to see, and by some "
            "magic not burned. After the priesthood of Dedun fell that secret "
            "was lost, and the body was first put in a hollow statue of its "
            "likeness, gold for royalty, silver for princes and the rich, "
            "earthenware even for the poor, and then in glass (p. 88).",
        ),
    )


def _artanyeszame(b: Builder, w: World) -> None:
    artanyeszame = b.magus(
        "Artanyeszame",
        covenant=None,
        house="",
        age=None,
        type="mythic companion",
        traditions=[LEARNED, DEDUN],
        summary=(
            "A withered, bent old Nubian in an Egyptian priest's robes and a "
            "headdress of ostrich feathers, the flesh gone from his left cheek "
            "to show teeth and bone. He carries a sceptre, and uses it as a "
            "club if he must. He lives in the southern necropolis of "
            "Begarawiyah (pp. 90-92)."
        ),
        secrets=paragraphs(
            "An Undying One. Born nearly two centuries ago, a beggar named "
            "Georgiu of Atbara, he was apprenticed to a learned magician, from "
            "whom he heard of the Cult of Dedun. Assassins of the Mortuary "
            "Society killed his master, and he has hated them ever since. With "
            "his master's resources he built up his power and took the "
            "transformation. He heads a chapter of the cult, with agents far "
            "along the Nile, chosen for their skills or contacts.",
            "He wants an intact Book of Thoth (chapter 5), believing like so "
            "many before him that he is strong enough to read it unconsumed. "
            "Until then he gathers power and destroys those who might "
            "interfere. He lets lesser sorcerers be, but tries to rule or "
            "remove any strong one, which sets him against 'Izz el-Afram "
            "Hamad; that feud may catch the characters, courted by one if they "
            "have crossed the other, and robbed of magical resources if they "
            "have crossed neither. It will likely end in stalemate. He could "
            "be an enemy, or for a while a mentor. Compared to a magus he is "
            "not powerful, but versatile and cunning.",
            "He ignores those who seek the Undying Ones' Script unless they "
            "annoy him, when he steers them to a fake he made a century ago, "
            "which inflicts the Ordeal but grants nothing.",
        ),
    )
    block: dict[str, Any] = {
        "characteristics": characteristics(1, -1, -2, 2, -3, 0, -2, -3),
        "aging_points": {
            "perception": 1,
            "presence": 1,
            "dexterity": 1,
            "quickness": 2,
        },
        "size": 0,
        "decrepitude": (3, 2),
        "confidence": (2, 5),
        "traditions": [LEARNED, DEDUN],
        "virtues_flaws": [
            "Learned Magician",
            "Transformed Human",
            "Corpse Magic",
            "Strong Verbal Charms",
            "Unnatural Vitality",
            "Animal Ken",
            "Harnessed Magic",
            "Dedun's Blessing",
            "Self-Confident",
            "Charm Magician",
            "Enemies",
            "Enfeebled",
            "Ambitious (Minor)",
            "No Chartae Making",
            "Tainted With Evil",
            "Vow (Minor)",
            "Focus Power",
            "Focus Power",
            "Greater Power",
            "Greater Power",
            ("{form} Resistance", {"form": "Corpus"}),
            "Improved Abilities",
            *["Improved Might"] * 9,
            "Improved Powers",
            "Lesser Power",
        ],
        "abilities": [
            ("Animal Ken", 3, "hyenas"),
            ("Area Lore: Meroë", 3, "pyramids"),
            ("Area Lore: Nubia", 3, "history"),
            ("Artes Liberales", 4, "astronomy"),
            ("Corpse Magic", 5, "interrogation"),
            ("Concentration", 4, "powers"),
            ("Corpus Resistance", 4, "resisting control"),
            ("Dead Language: Meroitic", 4, "royalty"),
            ("Folk Ken", 1, "magicians"),
            ("Guile", 2, "Nubians"),
            ("Leadership", 4, "bouda"),
            ("Living Language: Romaic Greek", 3, "Nubian"),
            ("Living Language: Nubian", 5, "Alwa"),
            ("Magic Lore", 4, "the dead"),
            ("Medicine", 2, "dry maladies"),
            ("Organization Lore: Cult of Dedun", 6, "Initiation"),
            ("Penetration", 4, "Salutem"),
            ("Philosophiae", 3, "natural philosophy"),
            ("Profession: Scribe", 2, "hieroglyphs"),
            ("Single Weapon", 2, "mace"),
            ("Tueor", 4, ""),
            ("Succuro", 5, ""),
            ("Vulnero", 7, ""),
            ("Fortunam", 6, ""),
            ("Magicam", 8, ""),
            ("Salutem", 12, ""),
        ],
        "traits": {"Remorseless": 3, "Scheming": 3, "Obsessive": 3, "Amoral": 2},
        "reputations": {"Ruthless (Local)": 3},
        "effects": [
            Builder.effect(
                name,
                rule="Known charm",
                uses=[technique, form],
                level=level,
                parameters=does,
                notes=f"Casting total +{total}, with the +9 of Unnatural Vitality. {design}",
            )
            for name, technique, form, level, total, does, design in CHARMS
        ],
        "notes": paragraphs(
            "Magic Might 25 (Corpus). Season: Winter. Magic Human: Transformed "
            "Human. Characteristics before aging: Int +2, Per +1, Pre -1, Com "
            "+2, Str 0, Sta +1, Dex +1, Qik -1. His court bought him Might 16; "
            "the nine Improved Might came by consuming vis (Realms of Power: "
            "Magic p. 52).",
            "Harnessed Magic is a Hermetic Virtue lost with the Gift. "
            "Transformed Human, Unnatural Vitality, Dedun's Blessing, "
            "Enfeebled and his Vow came by Initiation. His Enemies are the "
            "Mortuary Society of Kassala.",
            "Combat: Scepter (mace) Init -2, Attack +4, Defense 0, Damage +5. "
            "Soak 0. Fatigue OK, 0, -1, -3, -5, Unconscious. Wounds -1 (1-5), "
            "-3 (6-10), -5 (11-15), Incapacitated (16-20), Dead (21+). "
            "Encumbrance 1 (1). Equipment: robes, sceptre.",
            "Powers. Chariot of the Winds: 1 point, Init -2, Auram. A wind "
            "carries him where he likes at up to 40 miles an hour; hovering "
            "takes Concentration rolls. Cr(Re)Au 30 (Base 5, +1 Touch, +1 "
            "Conc, +2 highly unnatural, +1 requisite); Greater Power (30 "
            "levels, -2 cost, +2 Init).",
            "Lord of the Incorporeal: variable points, Init minus (Might cost "
            "+ 1), Mentem. Any non-Ritual spell of level 50 or less to do with "
            "ghosts, at 1 Might a magnitude: often Whispers Through the Black "
            "Gate (3 points, ArM5 p. 130), Vision of the Haunting Spirit (8, "
            "p. 150), Lay to Rest the Haunting Spirit (1-5, p. 150) and Coerce "
            "the Spirit of the Night (4, p. 152), and more exotic uses such as "
            "restoring a ghost's memories or giving it a passing body. Focus "
            "Power x2, with Improved Powers to raise the limit.",
            "Restore the Faded Tapestry of Youth: 4 points, Init -6, Corpus. "
            "The Dungeon Master: 1 point, Init -4, Imaginem. Both as the "
            "Undying Ones' common powers (p. 101): the first sheds his aging "
            "points for about an hour, with one Characteristic one above his "
            "best (Cr(Mu)Co(Me) 45); the second lets him see and hear anything "
            "in a structure he touches (InIm 15). The printed Inits use his "
            "Qik before aging.",
            "He casts charms as Hermetic Formulaic spells (Communication + "
            "Technique + Form + aura) through Strong Verbal Charms. His "
            "formularies hold many hundreds of spells, castable as Spontaneous "
            "spells at (Casting Score + stress die) / 2 after tens of minutes "
            "finding the right charm (Hedge Magic Revised Edition, chapter 5).",
            "Vis: sources of seven pawns a year, and usually ten pawns on him. "
            "His corpse holds 5 pawns of Vim in his withered heart.",
        ),
    }
    b.stats(artanyeszame, block, source="LotN")
    b.magus(
        "Queen Weteriken",
        covenant=None,
        house="",
        age=None,
        type="mythic companion",
        traditions=[DEDUN],
        summary=(
            "A ghost of a Kushite queen in the Pyramid of Arrakkamani, mother "
            "of its king, and a powerful necromancer: Communication 1, Corpse "
            "Magic 10, Teaching 4 (p. 92)."
        ),
        secrets=(
            "The ally and tutor of Artanyeszame, and part of his court of the "
            "dead. The Sovereign Ward Against Wandering Shadows has trapped "
            "her; she claims she enchanted it into the walls herself."
        ),
    )
    b.magus(
        "The Bouda Sisters of Begarawiyah",
        covenant=None,
        house="",
        age=None,
        type="mythic companion",
        summary=(
            "Three sisters, hyena skinchangers and witches (Hex 5), who live in "
            "the antechamber of the Pyramid of Arrakkamani and lead a dozen "
            "magical hyenas. Bouda are described in chapter 8 (p. 92)."
        ),
        secrets=("Friends of Artanyeszame; the hyenas serve as his covenfolk."),
    )


CHARMS: list[tuple[str, str, str, int, int, str, str]] = [
    (
        "Safeguard the Necromantic Spell",
        "Tueor",
        "Fortunam",
        15,
        21,
        "Takes two botch dice from any use of Corpse Magic.",
        "Base 10, +1 Diam.",
    ),
    (
        "Gift of Atum",
        "Succuro",
        "Fortunam",
        25,
        22,
        "Gives the target the Tough Virtue.",
        "Base 10, +1 Touch, +2 Sun.",
    ),
    (
        "Gift of Anhur",
        "Succuro",
        "Fortunam",
        25,
        22,
        "Gives the target the Puissant Single Weapon Virtue.",
        "Base 10, +1 Touch, +2 Sun.",
    ),
    (
        "Gift of Menhit",
        "Succuro",
        "Fortunam",
        25,
        22,
        "Gives the target the Puissant Bows Virtue.",
        "Base 10, +1 Touch, +2 Sun.",
    ),
    (
        "Gift of Apedemak",
        "Succuro",
        "Fortunam",
        25,
        22,
        "Gives the target the Inspirational Virtue.",
        "Base 10, +1 Touch, +2 Sun.",
    ),
    (
        "Sweet Incense of Dedun",
        "Succuro",
        "Magicam",
        5,
        24,
        "Shows vis within Range.",
        "Base 1, +2 Voice, +2 Sun.",
    ),
    (
        "Gift of Dedun",
        "Succuro",
        "Magicam",
        20,
        24,
        "Gives the caster Second Sight at score 4.",
        "Base 10, +2 Sun.",
    ),
    (
        "Sharpen the Magician's Knife",
        "Succuro",
        "Magicam",
        15,
        24,
        "+3 to the caster's next use of Vulnero.",
        "Base 10, +1 Diam.",
    ),
    (
        "Strengthen the Magician's Shield",
        "Succuro",
        "Magicam",
        15,
        24,
        "+3 to the caster's next use of Tueor.",
        "Base 10, +1 Diam.",
    ),
    (
        "Fortify the Magician's Balm",
        "Succuro",
        "Magicam",
        15,
        24,
        "+3 to the caster's next use of Succuro.",
        "Base 10, +1 Diam.",
    ),
    (
        "Charm of Alacritous Fortune Against Earth",
        "Tueor",
        "Magicam",
        15,
        23,
        ("+8 to the caster's Defense Total against magical earth or stone attacks."),
        "Base 10, +1 Diam.",
    ),
    (
        "Charm of Magical Fortitude Against Fire",
        "Tueor",
        "Magicam",
        13,
        23,
        "+16 to the caster's Soak Total against magical fire.",
        "Base 8, +1 Diam.",
    ),
    (
        "Sever the Binding Constraints",
        "Vulnero",
        "Magicam",
        20,
        26,
        (
            "Hastens the end of a spell meant to restrain or hinder its "
            "target: if 35 + stress die is at least double its level, its "
            "Duration falls one magnitude (Sun to Diam, Diam to Mom)."
        ),
        "Level 20, +1 Touch.",
    ),
    (
        "Charm of Protection Against the Fae",
        "Vulnero",
        "Magicam",
        20,
        26,
        (
            "Creatures of Faerie Might 20 or less cannot affect the target "
            "while the charm Penetrates."
        ),
        "Base effect.",
    ),
    (
        "Charm of Protection Against Spirits",
        "Vulnero",
        "Magicam",
        20,
        26,
        (
            "Creatures of Magic Might 20 or less, not only spirits, cannot "
            "affect the target while the charm Penetrates."
        ),
        "Base effect.",
    ),
    (
        "Ward the Sword's Edge",
        "Tueor",
        "Salutem",
        16,
        27,
        "+12 to the caster's Soak against slashing melee weapons.",
        "Base 6, +2 Sun.",
    ),
    (
        "Ward the Spear's Thrust",
        "Tueor",
        "Salutem",
        20,
        27,
        "Piercing melee weapons cannot harm the caster.",
        "Base 10, +2 Sun.",
    ),
    (
        "Ward the Club's Blow",
        "Tueor",
        "Salutem",
        20,
        27,
        "Bludgeoning melee weapons cannot harm the caster.",
        "Base 10, +2 Sun.",
    ),
    (
        "Curse of the Ruptured Ears",
        "Vulnero",
        "Salutem",
        35,
        30,
        (
            "A stab of pain strikes one person deaf and incapacitates for a "
            "round. Heals as a Heavy Wound."
        ),
        "Base 20, +2 Voice, +1 pain.",
    ),
    (
        "Curse of the Milky Eyes",
        "Vulnero",
        "Salutem",
        30,
        30,
        "Blinds the target. Heals as a Heavy Wound.",
        "Base 20, +2 Voice.",
    ),
    (
        "Curse of the Dumb Beast",
        "Vulnero",
        "Salutem",
        25,
        30,
        "Destroys the victim's tongue. Heals as a Medium Wound.",
        "Base 15, +2 Voice.",
    ),
]


def _pyramid(b: Builder, w: World) -> None:
    w["arrakkamani"] = _place(
        b,
        "The Pyramid of Arrakkamani",
        inside=w["begarawiyah"],
        aura=6,
        known=LOCAL,
        summary=(
            "A royal pyramid in the southern necropolis of Begarawiyah. A "
            "curse in Meroitic is written at the tomb's entrance (p. 92)."
        ),
        secrets=paragraphs(
            "Artanyeszame's home. His court of the dead, of strength 181 over "
            "four dozen corpses, among them King Arrakkamani and his mother "
            "Weteriken, is posed in a chamber as if at audience, paying homage "
            "to the central throne where he broods. Magic aura 6, aligned to "
            "the dead. The book scores the lair as a covenant site, for 259 "
            "Build Points overall (p. 92); the Tomb tab holds its curse, "
            "enchantments and traps.",
            "Covenfolk: the three bouda sisters and a dozen magical hyenas, "
            "some with Magic Sensitivity, who can find Corpus vis in the "
            "necropolis's long-buried dead, and are prone to bouts of madness.",
            "Library (45 Build Points): Inscription on Petitioning the Dead, a "
            "summa on Corpse Magic, Level 8, Quality 6; Initiation Script for "
            "Corpse Magic, Script Bonus +15. Specialists (56): two altar "
            "priests (Magic Lore 5), four grave guardians (Single Weapon 4), "
            "the ghost of Queen Weteriken, the three bouda. Vis (35): 2 pawns "
            "of Vim a year (paint flecks from magical texts), 4 of Corpus "
            "(bodies robbed by hyenas), 1 of Ignem (glass exposed to the dawn "
            "sun on the rising of Sirius).",
        ),
    )
    b.tomb(
        w["arrakkamani"],
        kind="major_monarch",
        boons="Aura x2 (Site, Minor), Seclusion (Site, Minor)",
        hooks="Evil Custom (Site, Minor), Inhuman Covenfolk (Residents, Minor), "
        "Seed of Madness (Residents, Minor)",
        hook_points=3,
        other="library 45, specialists 56, vis sources 35",
        other_bp=136,
        curses=[
            TombCurse(
                name="Those That Enter My Tomb in Their Impurity",
                kind=et.GREATER,
                art="PeCo",
                level=45,
                rdt="Touch, Special, Room",
                uses=1,
                condition="Those that enter the tomb in their impurity",
                excoriation="Their flesh shall decay and their bones perish: the "
                "Enfeebled Major Flaw. Written in Meroitic on the entrance. "
                "Artanyeszame's Might makes him immune, and his purification rite "
                "protects his servants. (Base 30, +1 Touch, +2 Room.)",
            ),
        ],
        wards=[
            TombWard(
                name="Shroud of Sands",
                art="ReTe",
                level=25,
                uses="24/day",
                effect="A cloak of sandstone disks on twine, moving up to ten "
                "thousand cubic paces of sand, enough to bury the pyramid or dig "
                "out the tunnel to the burial chamber; slow, and a threat only to "
                "the immobile (Base 1, +2 Voice, +1 Conc, +1 Part, +3 Size; +5 24 "
                "uses/day).",
            ),
            TombWard(
                name="Glory of the Royal Lion",
                art="ReCo",
                level=40,
                penetration=12,
                uses="12/day",
                effect="A statue of Apedemak whose lit eyes hold one looker a "
                "round, until its uses end, motionless save to keep facing it, "
                "even out of sight; they starve unless released (Base 5, +1 Eye, "
                "+3 Moon, +1 release; +4 12/day, +6 Pen 12).",
                deactivation="A command word in Meroitic releases those held",
            ),
            TombWard(
                name="Sovereign Ward Against Wandering Shadows",
                kind=et.WARD,
                art="ReMe",
                level=57,
                penetration=26,
                uses="constant",
                ease=24,
                effect="No spirit of Might 25 or less enters or leaves the pyramid "
                "if it Penetrates. Queen Weteriken, trapped by it, claims to have "
                "enchanted it herself; Artanyeszame gained his Might inside and is "
                "immune (Base 25, +0 Touch, +0 Sun, +3 Structure; +1 2/day, +3 "
                "environmental trigger, +13 Pen 26).",
            ),
        ],
        traps=[
            TombTrap(
                name="The Receding Steps",
                harm="fatal",
                ease=9,
                roll="Str + Athletics - Encumbrance",
                text="The steps to the burial chamber recede into a smooth 20 pace "
                "ramp ending on a hard floor, +30 damage; the roll catches the "
                "sides.",
            ),
            TombTrap(
                name="The False Burial Chamber",
                harm="scare",
                ease=9,
                roll="Per + Bargain",
                text="Filled with fake treasure, and good for an ambush; the roll "
                "sees through it from outside.",
            ),
            TombTrap(
                name="The Rain of Poisoned Darts",
                harm="minor",
                further_bp=2 * et.HARMS["minor"].build_points,
                ease=6,
                roll="Sta",
                text="Each person is struck by 1-6 darts, each a Light Wound "
                "unless the roll is made (average 3 Light Wounds).",
            ),
            TombTrap(
                name="The Falling Slab",
                harm="serious",
                ease=12,
                roll="Qik + Athletics - Encumbrance",
                text="A massive stone slab, +15 damage, which traps people on the "
                "wrong side; the roll dives clear.",
            ),
        ],
    )


def _hamad(b: Builder, w: World) -> None:
    b.magus(
        "'Izz el-Afram Hamad",
        covenant=None,
        house="",
        age=None,
        type="mythic companion",
        traditions=[SAHIRS],
        summary=(
            "A Bedouin prince of the Ja'alin, the Master of Abu Hamad, "
            "charming, inquisitive and sinister in equal measure (p. 82)."
        ),
        secrets=paragraphs(
            "A powerful Gifted sahir, driven from his home by the Ayyubids to "
            "the southern Nubian Desert with his Ja'alin and a host of jinni. "
            "Now over eighty and feeling it despite magic that has lengthened "
            "his life, he has heard from his apprentices of the Cult of Dedun, "
            "and hopes to learn its trick of immortality. He suffers no "
            "threat: he tries to remove other Gifted magicians, trains no "
            "Gifted apprentices lest he raise a rival, and has several "
            "unGifted ones.",
            "A particularly powerful jinn serves as ally and servant, chafing "
            "at bonds it cannot break. His eyes are said to be everywhere, his "
            "agents mostly Egyptians in administrative posts. The nature of "
            "his pacts with the jinni, and which realm they belong to, is left "
            "to the storyguide. The book prints no statistics for him. He "
            "suits a recurring villain, out of reach of new characters, "
            "growing as they do.",
        ),
    )
    _seed(
        b,
        "The Master of Abu Hamad",
        "A merchant friend of the characters is being ruined by a rival "
        "with an endless supply of their trade goods, from a magic reed "
        "basket that seems to create them permanently without vis. The "
        "trail leads to Abu Hamad (p. 82).",
        where=w["abu_hamad"],
        antagonist="'Izz el-Afram Hamad",
        secrets=(
            "Hamad arranged this to meet and weigh the characters. He insists "
            "they keep the basket as compensation. It works by a bound jinn, "
            "which fetches the goods from elsewhere, and a power makes it read "
            "to Hermetic Investigation as a normal enchantment, like a Shell "
            "of False Determination. Other clashes with the Ja'alin and his "
            "minions should fill out the arc."
        ),
        stages=[
            Builder.stage(
                "The Magical Basket",
                at=1,
                clues="A rival's endless goods; a reed basket; the trail to Abu Hamad.",
                ignored="The merchant is ruined, and the characters are left a mystery.",
            ),
            Builder.stage(
                "Attempted Regicide",
                at=2,
                clues=(
                    "Having met Hamad and lived, the characters interest the Great "
                    "King of Makuria, as Hamad makes sure. They are summoned to "
                    "Dongola with the basket, and run into court politics stirred by "
                    "his agents."
                ),
                ignored=(
                    "Before the king the basket's true purpose shows: a fearsome jinn "
                    "comes out and attacks him. Even if it is beaten, the characters "
                    "may be blamed for endangering him and lose any favour they had."
                ),
            ),
            Builder.stage(
                "The Demons of Sawakin",
                at=3,
                clues=(
                    "Hamad seeks to master the jinni imprisoned at Sawakin, creatures "
                    "Solomon himself thought too dangerous."
                ),
                ignored=(
                    "With them he could smash any Aegis of the Hearth and defeat even "
                    "Hermetic magi. The characters must race to the Coral City for a "
                    "showdown of Hermetic and Solomonic magic."
                ),
            ),
        ],
    )
    _seed(
        b,
        "The Siege of Berber",
        "The characters are hired to break the blockade of Berber, or "
        "something they need is trapped inside. Three Ja'alin meks hold "
        "the three landward approaches, each with two score warriors and a "
        "dozen jinni; given notice, three more lie a day away and six more "
        "within three (p. 83).",
        where=w["berber"],
        antagonist="The Ja'alin",
        secrets=(
            "The characters are the first outsiders here in three years. The "
            "people are enslaved to Ja'alin overlords and set to digging under "
            "the town. For what, and for whom? 'Izz el-Afram Hamad is the "
            "obvious mastermind, but by no means the only possibility."
        ),
    )


def _ababdah(b: Builder, w: World) -> None:
    ababdah = b.magus(
        "Ababdah",
        covenant=None,
        house="",
        age=30,
        type="mythic companion",
        summary=(
            "A stocky Blemmya miner of the Phoinikon tribe in leather on his "
            "forearms and upper arms and a skirt of leather strips, with a "
            "pick and a camel laden with gear. His finds of gold seams have "
            "made his tribe rich. He gets lost in the dunes, so a younger "
            "cousin often shadows him (p. 95)."
        ),
    )
    b.stats(
        ababdah,
        {
            "characteristics": characteristics(0, 1, 0, -1, 5, 2, 2, 1),
            "size": 0,
            "apparent_age": 30,
            "confidence": (1, 3),
            "virtues_flaws": [
                "Magic Human",
                "Craftsman",
                vf_ability("Affinity with {ability}", "Profession: Miner"),
                "Long-Winded",
                "Warrior",
                (
                    "Essential Flaw (Minor)",
                    {"trait": "Excessively Generous (Communication)"},
                ),
                "Generous (Minor)",
                "No Sense of Direction",
                "Improved Abilities",
                "Improved Abilities",
                "Lesser Power",
                vf_minor("Great Strength"),
                vf_minor("Great Strength"),
                vf_minor("Improved Characteristics"),
                vf_minor("Improved Characteristics"),
                vf_minor("Puissant Thrown Weapon"),
                vf_minor("Tough"),
                "Personal Power",
                ("Major Flaw", {"flaw": "Age Quickly"}),
                "Monstrous Appearance",
                ("Minor Flaw", {"flaw": "Hunchback"}),
                ("Minor Flaw", {"flaw": "Poor Hearing"}),
            ],
            "abilities": [
                ("Animal Handling", 3, "camels"),
                ("Area Lore: Nobatia", 1, "Pakhoras"),
                ("Area Lore: Red Sea Hills", 3, "ore-bearing areas"),
                ("Bargain", 4, "evaluating value"),
                ("Folk Ken", 1, "gold merchants"),
                ("Leadership", 2, "miners"),
                ("Living Language: Beja", 5, "Phoinikon"),
                ("Living Language: Nubian", 3, "Dongolawi"),
                ("Organization Lore: Phoinikon Tribe", 2, "gold merchants"),
                ("Profession: Miner", 6, "gold"),
                ("Ride", 3, "camels"),
                ("Single Weapon", 5, "pick"),
                ("Thrown Weapons", 5, "sling"),
            ],
            "traits": {
                "Charitable": 3,
                "Diligent": 2,
                "Brave": 1,
                "Excessively Generous (Communication)": -3,
            },
            "notes": paragraphs(
                "Magic Might 5 (Corpus). Season: Summer. Monstrous Appearance "
                "comes free with Magic Human. Beja is his native language. Thrown "
                "Weapons is printed 5+2 with Puissant, and Profession: Miner 6 "
                "(8). In human society he would most likely have Magical Covenfolk "
                "as his Social Status.",
                "Combat: Pick (as mace) Init +2, Attack +11, Defense +7, Damage "
                "+13. Sling Init -2, Attack +11, Defense +7, Damage +10. Soak +6. "
                "Fatigue OK, 0, -1, -3, -5, Unconscious. Wounds -1 (1-5), -3 "
                "(6-10), -5 (11-15), Incapacitated (16-20), Dead (21+). "
                "Encumbrance 0 (Burden 0). Equipment: miner's tools, partial "
                "leather armour.",
                "Powers. Ease the Labor of Ten Miners: 2 points, Init -2, Terram. "
                "Weakens rock over ten paces by ten and up to ten deep, for easy "
                "digging. PeTe 15 (Base 2, +1 Touch, +1 stone, +3 size); Lesser "
                "Power (15 levels, -1 Might cost). Gold-Miner's Keen Eye: 1 point, "
                "Init -1, Terram. Sees gold through up to three paces of matter "
                "and judges its purity and quantity. InTe 20 (Base 2, +1 Conc, +4 "
                "Vision, +1 through matter); Personal Power (20 levels, -1 Might "
                "cost).",
                "Vis: 1 pawn of Terram, in his eyes.",
            ),
        },
        source="LotN",
    )


def _scorpion_fish(b: Builder, w: World) -> None:
    b.creature(
        "Scorpion Fish (Scorpaena)",
        page="p. 97",
        size=5,
        cunning=True,
        confidence=(1, 3),
        block={
            "characteristics": characteristics(-2, -2, -5, -6, 10, 3, 1, 0),
            "virtues_flaws": [
                "Improved Characteristics",
                "Ferocity",
                "Tough",
                "Greedy (Major)",
                "Aggressive",
                "Aquatic",
                "Large Teeth",
                "Pursuit Predator",
                "Swallow Whole",
                "Thick Fur/Thick Scales",
                "Tough Hide",
            ],
            "abilities": [
                ("Awareness", 2, "prey"),
                ("Brawl", 5, "teeth"),
                ("Hunt", 4, "large fish"),
                ("Survival", 3, "Red Sea"),
                ("Swim", 5, "deep water"),
            ],
            "traits": {"Hungry": 6},
            "reputations": {"Killer (Local)": 2},
        },
        attacks=[b.attack("Bite", 0, 11, 7, 13)],
        soak=10,
        fatigue_levels="OK, 0/0, -1, -3, -5, Unconscious",
        appearance=(
            "A hideous red fish over six paces long, with a toad's mouth full "
            "of razor teeth and a body covered in rough nodules and long "
            "spines."
        ),
        place=w["red_sea"],
        notes=paragraphs(
            "Ferocity applies in shallow water. Wound ranges: -1 (1-10), -3 "
            "(11-20), -5 (21-30), Incapacitated (31-40), Dead (41+).",
            "Swallow Whole is a Quality by the errata (p. 87); the book prints "
            "it under Powers. It takes any creature of Size 0 or less, which "
            "can struggle only with Brawl. The arithmetic is in "
            "rules/africa.py.",
            "Small ones, two feet or so, sometimes turn up in fishermen's "
            "nets; these are the figures for a twenty-foot horror. With the "
            "Fast Swimmer Quality the block serves for the Red Sea's giant "
            "sharks.",
            "Giant eels use the elephant-eating serpent (p. 23) with the "
            "Aquatic Quality and the Slippery Quality twice: Swim 5, "
            "water-breathing and +9 to Defense Totals in a grapple.",
        ),
    )


# -- Nubia's stories --


def _nubia_seeds(b: Builder, w: World) -> None:
    nubia, dju_waab = w["nubia"], w["dju_waab"]
    _seed(
        b,
        "Theft by the Dead",
        "Robbers, probably foreigners, exploit the Nubian horror of the "
        "dead by faking their deaths and going about as their own walking "
        "corpses. No one reports them, and no one follows them to their "
        "graveyard haunt (p. 73).",
        where=nubia,
        secrets=(
            "Their work has drawn faeries or demons, who take the look of real "
            "corpses and copy the crimes. The characters are drawn in when one "
            "robs them in the shape of someone they know to be dead."
        ),
    )
    _seed(
        b,
        "Six Hundred and Eighty Nine",
        "A crazed old man has for years sold clay amulets marked "
        "chi-pi-theta and spent the money on used swords, over six hundred "
        "now, fixed to his outer walls. His house is a local landmark. One "
        "day the swords are gone (p. 74).",
        where=nubia,
        secrets=(
            "He is hiding them across the city, muttering in Aramaic, "
            "believing that with all 689 in their exact places he will summon "
            "Michael, archangel of the sword, to cast out the city's evil. "
            "Will it work? Will it bring an archangel? Will Michael define "
            "evil as men do? Sodom and Gomorrah were the last cities he "
            "cleansed."
        ),
    )
    _seed(
        b,
        "Freedom Fortress",
        "The characters stop for help at a small fortress of the river (p. 80).",
        where=w["fortified_river"],
        secrets=(
            "Its garrison are escaped slaves posing as soldiers. Some would "
            "kill the characters if they guess the truth; another faction "
            "warns them and may want to leave with them or use them to take "
            "the fort. The characters could gain useful allies."
        ),
    )
    _seed(
        b,
        "The Soul Exchange",
        "Seeking something rare, the characters visit a fortress famed for "
        "its black market, and find it a den of every vice (p. 82).",
        where=w["fortified_river"],
        realm="Infernal",
        secrets=(
            "Its people are ghosts, trapped by the demon that killed them. "
            "Each is promised freedom for winning a soul for Hell, but the "
            "demon just consumes the ghost and traps its victim instead. Only "
            "slaying the demon in the caverns beneath the fort frees them."
        ),
    )
    _seed(
        b,
        "The Blind God's Eyes",
        "Treasure hunters have long searched Napata for the Kushite "
        "priests' lost wealth, and legend says the missing statues of the "
        "gods show the way. The priests' last act was to wipe the paint "
        "from the statues' eyes, making them mere stone (p. 84).",
        where=w["napata"],
        secrets=(
            "Wind has uncovered one, and a merchant's daughter, waiting for "
            "her father at the well, idly coloured in its eyes with kohl. The "
            "faerie that lived in it has returned, and it now walks slowly and "
            "inexorably to its destination. There is a town in the way."
        ),
    )
    _seed(
        b,
        "The Hawk That Thought It Was A God",
        "A desert hawk circles Dju Wa'ab crying, and lands on a temple "
        "roof every day at noon (p. 84).",
        where=dju_waab,
        secrets=(
            "A faerie animal with the merest scrap of Might, once emissary of "
            "Mandulis. If characters are near at midday it takes them for the "
            "old priests and gives his last message, that Anhur's Spear lies "
            "where the sun meets the sea and the waves lie still. What does it "
            "mean?"
        ),
    )
    _seed(
        b,
        "Thirty Centuries",
        "A character is visited, by vision, Second Sight or vivid dream, "
        "by the ghost of an ancient warrior in a black tabard. His unit is "
        "surrounded and needs help. He can lead the characters to Kerma, "
        "where the battle can be seen on the night of a new moon (p. 84).",
        where=w["kerma"],
        antagonist="A temple priest of Dedun",
        secrets=(
            "Kerma died in a civil war, and the stones mark each side's "
            "fallen. Every new moon the ghosts fight again; a black soldier "
            "killed joins the white, and vice versa, and his grave's stones "
            "change colour over the year, making the mixed graves. If one side "
            "stands unopposed the army will unite under one commander, free to "
            "leave. White holds most graves now and gains yearly, the work of "
            "a temple priest of Dedun. What will he do with 25,000 ghostly "
            "warriors?"
        ),
    )
    _seed(
        b,
        "Valley of Elephants",
        "An Old Man of the Forest, a magical elephant and guardian of the "
        "valley, appears before the characters. A local king plans to "
        "drain the marshes for farming and drive off the herds. The sweet "
        "rush, he says, is hateful to the giant serpents of the gorges; "
        "without it men and elephants alike will feed them. The king will "
        "be hard to convince. Is it true? Can there be a compromise (p. "
        "86)?",
        where=w["elephants"],
    )
    _seed(
        b,
        "Black Coral",
        "Someone comes to Sawakin for coral, to trade or to enchant, and "
        "buys stone that draws evil spirits instead of warding them off "
        "(p. 96).",
        where=w["sawakin"],
        antagonist="The cult of 'Ashmodai'",
        realm="Infernal",
        secrets=(
            "An earthquake cracked the coral under a warehouse, and an "
            "Infernal jinn reached a labourer clearing the rubble, who now "
            "leads a cult of 'Ashmodai'. The cult corrupts the coral and "
            "tracks its buyers, and recruits the demons they attract, once the "
            "buyer is dead or corrupted."
        ),
    )
    _seed(
        b,
        "Grandmother Lion",
        "The characters meet an Aithiops slave escaped from Taqasi, with "
        "poor Nubian, who begs them to free her grandmother from the king "
        "(p. 96).",
        where=w["taqasi"],
        secrets=(
            "The 'grandmother' is a magical lioness of Taqasi, the lion's "
            "equal of a sorceress, with powers including human shape. The king "
            "found her out and holds her cub to ensure her behaviour. She has "
            "the Gift, so some pet lions distrust her and may betray her. If "
            "she and her son go free, she might let the cub become a "
            "character's familiar or companion."
        ),
    )


def _dedun_seeds(b: Builder, w: World) -> None:
    dedun, pyramid = w["dedun"], w["arrakkamani"]
    _seed(
        b,
        "The Green Stone Hand",
        "The characters come by a hand of green stone (p. 90).",
        where=pyramid,
        antagonist="Artanyeszame",
        secrets=(
            "It is the missing part of the Djet in Cleopatra's Tomb. An agent "
            "snooping in their things tells Artanyeszame, who realises the "
            "Djet can show him the Book of Thoth. He has only to trick them "
            "into wanting to find the tomb."
        ),
    )
    _seed(
        b,
        "The Queen's Ghost",
        "A junior member of the Mortuary Society asks the characters to "
        "help free the ghost of a Kushite queen and lay her soul to rest "
        "(p. 90).",
        where=pyramid,
        antagonist="The Mortuary Society",
        secrets=(
            "He omits that Queen Weteriken is Artanyeszame's ally and tutor, "
            "in his pyramid. The society hopes the characters will weaken or "
            "destroy him for them."
        ),
    )
    _seed(
        b,
        "Theft of the Dead",
        "A vis source of the characters is being raided by a man plainly "
        "not taking it for himself. This may be their first sight of the "
        "Cult of Dedun (p. 102).",
        where=dedun,
        antagonist="The Cult of Dedun",
        secrets=(
            "He is an adherent. His Prohibition stops him naming his master or "
            "leading them to his temple if he suspects he is watched, and "
            "forcing him triggers it."
        ),
    )
    _seed(
        b,
        "Help from the Black",
        "Soon after a clash with the cult, a potential ally approaches the "
        "characters. She has been fighting its corruption, and asks help "
        "to free a friend captured by an Undying One (p. 102).",
        where=dedun,
        antagonist="The Cult of Dedun",
        secrets=(
            "She is secretly a knowing servant of the Black, and her friend is "
            "an akh (chapter 4), who could be another strong ally."
        ),
    )
    _seed(
        b,
        "If You Can't Beat Them, Join Them",
        "The characters' ally seems ever better informed about the cult's "
        "rivals, and steers them against those rivals (p. 102).",
        where=dedun,
        antagonist="The Cult of Dedun",
        secrets=(
            "She has joined in secret. She tells herself she is bringing it "
            "down from within, but immortality has seduced her, and she hopes "
            "the characters will find where the Initiation Script for the "
            "transformation lies."
        ),
    )
