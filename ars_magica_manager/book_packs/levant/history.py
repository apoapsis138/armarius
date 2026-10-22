"""The Levant Tribunal's history, as the book tells it (ch02, the
appendix timeline, and the dates scattered through ch07 and ch08), as
Tribunal Diary entries from the Order's founding in 767 to the fall of
Damietta in 1219: the Tribunal of the East and its two covenants, the
long silence after Harun al-Rashid, the First Crusade and the magi who
came with it, the Grand Tribunal of 1129 that recognised the refounded
Tribunal, each covenant's founding, the cursed coins of Damascus,
Hattin, Aurora's road to the Treaty of Baghdad, the Hermetic Embassy,
the quarrel with Thebes after 1204, Arash's refusal of the Oath and the
Crusade at Damietta. Crusade history enters only where it shaped the
Tribunal (1099, 1144, 1148, 1187, 1192, 1204, 1218 and 1219); the early
caliphs and the world before Islam stay in the book.

The meetings of 1193, 1200, 1207 and 1214 are tribunal.py's, and are not
repeated here. Nothing after 1220 goes in the Diary (L22): what the book
foretells is in the lords' summaries and the stories' stages.

Where the book gives a span or only "soon after", the entry takes the
year it names first and says so; where the chapters disagree, it
follows the pack's decisions (the Tribunal of the East in 832, the
timeline's year) and gives the other reading in brackets."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..builder import secrets

if TYPE_CHECKING:
    from . import Levant

#: The order of the seasons within a year; an entry with none comes first.
SEASON_ORDER = {"": 0, "Spring": 1, "Summer": 2, "Autumn": 3, "Winter": 4}

#: (year, season, title, details, hidden): one Diary entry each.
EVENTS: tuple[tuple[int, str, str, str, str], ...] = (
    # -- The Tribunal of the East --
    (
        767,
        "",
        "The Order of Hermes founded",
        "The Order is founded in the west, far from the lands that will one "
        "day be the Levant Tribunal. At this time Baghdad, built five years "
        "before by the caliph al-Mansur, is the young capital of the "
        "'Abbasids.",
        "",
    ),
    (
        802,
        "",
        "Urbs Rubra founded at Petra",
        "Harun al-Rashid, caliph since 786, has been trading embassies with "
        "Charlemagne, a king with more friends in the Order than the "
        "quaesitores like to own. Through them the Order wins the caliph's "
        "leave for two covenants in his lands, and the first, Urbs Rubra, is "
        "raised among the rock-cut halls of Petra. Harun's reign is an age "
        "of wonders, when jinn and men in some places live side by side and "
        "trade with one another, and the caliph himself is said to take "
        "lessons in Hermetic magic.",
        "If the storyguide wants it, the rumour is true: Harun learnt the "
        "Order's magic and passed it to mages of his court, and their "
        "pupils' pupils practise it still (see the Islamic Tradition's "
        "story seeds).",
    ),
    (
        806,
        "",
        "Urania founded in the Caucasus",
        "The second covenant by Harun's leave is made in caves high on two "
        "pale cliffs in the Alan country, north-east of the Black Sea. Its "
        "remoteness will keep it alive through every war to come.",
        "",
    ),
    (
        809,
        "",
        "Harun dies, and the East forgets the Order",
        "Harun's sons fall to civil war over his throne, the Muslim world "
        "turns its eyes inward and later breaks into rival states, and the "
        "two covenants lose their friends at court. For almost three "
        "centuries the East is a quiet corner of the Order.",
        "",
    ),
    (
        817,
        "",
        "House Ex Miscellanea joins the Order",
        "The hedge wizards' House is admitted, the road by which the "
        "Levant's priests of the Pyramids and its sahirs will one day come "
        "into the Order.",
        "",
    ),
    (
        832,
        "",
        "The Tribunal of the East",
        "The lands of Urbs Rubra and Urania are counted a Tribunal of the "
        "Order and named the Tribunal of the East, since the Order has "
        "reached no further in that direction. (Ch02 says only that this "
        "came soon after the covenants were founded; 832 is the timeline's "
        "year.)",
        "",
    ),
    (
        848,
        "",
        "The Sundering of House Tremere",
        "The timeline marks the Sundering of House Tremere in the west; the "
        "East, cut off since Harun's death, plays no part.",
        "",
    ),
    (
        961,
        "",
        "Tasgillia executed",
        "The timeline records the execution of Tasgillia, an event of the "
        "Order in the west that the book does not tell.",
        "",
    ),
    (
        969,
        "",
        "The Fatimids take Egypt, with Berber wizards",
        "The Isma'ili Fatimids, caliphs at Qayrawan since 909 on the "
        "strength of the mountain Berbers, send their general Jawhar to "
        "take Fustat and found Cairo beside it. Berber wizards march with "
        "them, working a magic no Muslim mage had met before, and the mages "
        "who stand against the invasion are wiped out. No magus of the "
        "Order ever meets them, and what their magic was is still unknown.",
        "",
    ),
    (
        1003,
        "",
        "The Schism War",
        "From 1003 to 1012 the Schism War tears the Order apart. The "
        "Tribunal of the East, still a forgotten backwater, has no recorded "
        "part in it.",
        "",
    ),
    (
        1073,
        "",
        "Al-Arama founded",
        "Magi raise a covenant on a crag of the Taurus in Lesser Armenia, "
        "one of the few founded between the East's first Tribunal and its "
        "second, and it grows rich on trade with covenants of the Roman "
        "Tribunal.",
        "",
    ),
    # -- The Crusaders and their magi --
    (
        1098,
        "",
        "The Holy Lance found at Antioch",
        "With the First Crusade trapped inside Antioch, a southern French "
        "servant, Peter Bartholomew, tells its leaders that Saint Andrew has "
        "shown him in visions where the Lance that pierced Christ lies "
        "buried. They dig beneath the cathedral of St Peter, find it, carry "
        "it out against the besiegers and break the siege. It is a crusade "
        "of portents: comets, saints' ghosts at the head of the armies, "
        "visions on every side.",
        "",
    ),
    (
        1099,
        "Summer",
        "The First Crusade takes Jerusalem",
        "On 15 July the crusaders storm Jerusalem and slaughter its people, "
        "and Godfrey rules it as Defender of the Holy Sepulchre; a Fatimid "
        "army is beaten in August. The sorcerers of Jerusalem had cursed "
        "the siege engines and strengthened the walls, but the Muslims' "
        "mages are few, scattered and leaderless, and they cannot hold "
        "against the Hermetic magi who have come with the armies: "
        "Flambeau, Tremere and Tytalus above all, some for their faith, "
        "some for plunder, and some Flambeau to avenge a founder they "
        "believe Muslim wizards murdered. Arnulf, the new Latin patriarch, "
        "finds a relic of the True Cross buried at the Holy Sepulchre.",
        "Ever since, the night of 15 July has been a night of the dead in "
        "Jerusalem: an Infernal aura of 5 replaces the Divine ones, and "
        "the dead of 1099 throng the streets until dawn.",
    ),
    (
        1099,
        "Summer",
        "Para Belli founded",
        "Just after the Crusade, Flambeau magi found a fortress hidden in "
        "the Sinai as a refuge for the Order and a school of war for their "
        "House's young.",
        "",
    ),
    (
        1101,
        "",
        "The Holy Lance lost; Venti Rosa founded",
        "The crusaders carry the Lance into battle until 1101, when it is "
        "lost in Asia Minor; what became of it no one knows. The same year "
        "Redcaps found Venti Rosa, a covenant that is a caravan, carrying "
        "the Order's messages from covenant to covenant across the East.",
        "",
    ),
    (
        1112,
        "",
        "Aedes Veritatis founded",
        "Maryam al-Dimashqiyya, a young Jerbiton maga of Damascus, raises a "
        "fortress on a mountain five miles east of the city for magi who "
        "have chosen to fight their Hermetic brothers on the Muslims' side. "
        "She names it the House of Truth; in Arabic, Bayt al-Haqq, it means "
        "too the house of what is right.",
        "",
    ),
    (
        1129,
        "",
        "The Levant Tribunal recognised",
        "After the Crusade, Verditius magi come for the spoils, Criamon to "
        "sit with the East's mystics, Jerbiton for its wealth and learning, "
        "and the newcomers stake out covenants and lands over the old "
        "covenants' protests. The Grand Tribunal of 1129 recognises the "
        "refounded Tribunal and, as the Order now holds covenants across "
        "the eastern lands, names it the Levant Tribunal. Recognition "
        "brings no order. For decades magi meddle openly in the wars, clash "
        "again and again with the Muslims' mages, and fight one another in "
        "Wizard Wars over the land's riches; some, sickened by their "
        "sodales' cruelty, take the Muslims' side. Crusading magi excuse "
        "their breaches of the Code as the price of keeping the Order in "
        "the East, counter-crusaders theirs as shielding the Muslims, and "
        "the quaesitores, some of them as deep in it as anyone, cannot "
        "rule the Tribunal.",
        "",
    ),
    (
        1144,
        "Winter",
        "Edessa falls to Zangi",
        "On Christmas Eve Zangi, atabeg of Mosul, takes Edessa and ends the "
        "first of the Latin states, with Muslim magi at his side. As Zangi, "
        "Nur al-Din and Salah al-Din unite the Muslims, mages gather to "
        "their banners.",
        "",
    ),
    (
        1148,
        "Summer",
        "The cursed coins of Damascus",
        "The Second Crusade, led by Louis VII and Conrad III, turns on "
        "Damascus, Jerusalem's ally, and fails. Some Latins of the Levant "
        "sold their comrades for a chest of gold, but the city's sorcerers "
        "had enchanted the coins, and when the traitors came to spend them "
        "they were brass.",
        "",
    ),
    (
        1148,
        "Summer",
        "The Pyramids (I) founded",
        "Ruth of Bonisagus and Pariah of Criamon pitch a camp of tents by "
        "the Great Pyramid at Giza. (One of the book's two covenants at the "
        "pyramids; see the Pyramids (II), 1178.)",
        "",
    ),
    (
        1169,
        "",
        "Aurora comes to the Levant",
        "Aurora Borealis of Jerbiton arrives with Tau of Flambeau and "
        "founds Domus Pacis in a khan north of Jerusalem, where magi and "
        "the land's other wizards may meet and trade knowledge. In Egypt "
        "the Kurd Shirkuh becomes the Fatimid caliph's vizier and dies "
        "within the year, and his nephew Salah al-Din takes his place.",
        "",
    ),
    (
        1174,
        "",
        "Nur al-Din dies, or seems to",
        "Nur al-Din, the Muslims' champion in Syria since he took Damascus "
        "in 1154, dies, and Salah al-Din begins to bring the Muslim Levant "
        "under his own rule. Some say the prophet al-Khidr taught Nur "
        "al-Din words of power that won him whatever he asked and carried "
        "him great distances in an instant.",
        "Khidr may also have taught him long life and foresight: the "
        "storyguide may decide he feigned his death, foreseeing Salah "
        "al-Din's destiny, and still works unseen for Islam.",
    ),
    (
        1177,
        "",
        "Heliobus drawn to the temple",
        "One of the twelve priests of Thoth and Anubis, hidden in a regio "
        "among the pyramids and the Sphinx since ancient times, dies, and "
        "as always a Gifted stranger is drawn to take the empty place. This "
        "time it is Heliobus Magister, a respected Bonisagus researcher, "
        "who arrives as Hermetic magi begin raiding the temple for its "
        "magic.",
        "",
    ),
    (
        1178,
        "",
        "The Pyramids (II): the priests join the Order",
        "Heliobus brings the priesthood into House Ex Miscellanea and under "
        "the Code's protection, and the raids stop. (The book's second "
        "covenant at the pyramids; it may stand instead of the first, or "
        "beside it.)",
        "",
    ),
    (
        1183,
        "",
        "Aurora goes to Baghdad",
        "Seeing the danger Salah al-Din's rise means for the Order, Aurora "
        "approaches him, the caliph and their mages, travels to Baghdad to "
        "sketch a treaty, and offers it to the quaesitores of Magvillus, "
        "who seize on the chance to bring the Tribunal to heel.",
        "",
    ),
    (
        1187,
        "Summer",
        "Hattin",
        "Salah al-Din destroys the Latin army at Hattin on 4 July and takes "
        "Jerusalem and most of the Latin states. Muslim mages working with "
        "him kill many Hermetic magi on the field and later lend magical "
        "artillery against the Latin castles, and by the year's end several "
        "of the great crusading covenants are gone. The survivors accuse "
        "the counter-crusaders of helping the Muslims, but nothing is ever "
        "proved. The relic of the True Cross is lost to Salah al-Din on the "
        "field.",
        "",
    ),
    (
        1187,
        "Summer",
        "Maryam falls; 'Umar leads Aedes Veritatis",
        "Maryam al-Dimashqiyya and most of Aedes Veritatis's magi die at "
        "Hattin, though their side has won. Heloise of Criamon, the one "
        "left, defers to Maryam's wish, and her young filius Sharaf al-Din "
        "'Umar takes the covenant; Heloise later goes, saying only that it "
        "was time, and is not seen again. At Petra the crusaders abandon "
        "their castle, leaving Urbs Rubra undisturbed.",
        "",
    ),
    (
        1188,
        "",
        "Foothold founded; Amber joins Aedes Veritatis",
        "Two young magi from France, the Flambeau Guillaume de Bourne and "
        "the Tytalus Rufus de Clary, plant a covenant on a hill north-east of Acre "
        "to keep the Order a lasting foothold on the coast. Amber of "
        "Tremere, rejecting her House's support for the Crusades, joins "
        "'Umar at Aedes Veritatis. (By the book's ages Guillaume and Rufus "
        "were barely magi; the pack keeps the year.)",
        "",
    ),
    (
        1192,
        "Summer",
        "Richard's truce, and the talks in Baghdad",
        "After the Third Crusade retakes Acre and Richard I sells Cyprus to "
        "Guy of Lusignan, Richard and Salah al-Din agree on 2 September a "
        "three-year truce that leaves the coast to the Latins and Jerusalem "
        "to the Muslims. In Baghdad, Aurora's talks between the Order and "
        "the Muslims' rulers and mages draw to a close.",
        "",
    ),
    (
        1193,
        "",
        "Salah al-Din dies",
        "Salah al-Din dies at Damascus on 4 March, and his sons and brother "
        "divide his empire.",
        "",
    ),
    (
        1193,
        "Autumn",
        "The Hermetic Embassy founded",
        "With the Treaty accepted, Aurora is invited to become a "
        "quaesitor, and accepts. She moves to Baghdad to keep the Treaty "
        "and founds the Hermetic Embassy there, near the caliph's palace, "
        "paid for by Magvillus; soon afterwards she becomes an archmaga.",
        "",
    ),
    (
        1195,
        "",
        "The last Grand Tribunal",
        "The Order's most recent Grand Tribunal meets.",
        "",
    ),
    (
        1197,
        "",
        "Esther joins Domus Pacis",
        "Esther of Verditius, an Englishwoman, comes to Domus Pacis and "
        "soon makes it a channel for trade between the Levant and the "
        "Roman Tribunal, breaking al-Arama's hold on the trade.",
        "",
    ),
    (
        1203,
        "",
        "The Treaty's second term",
        "The renewal voted in 1200 takes effect: the Treaty runs another ten years.",
        "",
    ),
    (
        1204,
        "Spring",
        "Constantinople falls; quarrel with Thebes",
        "The Fourth Crusade takes Constantinople on 12 April and founds a "
        "Latin empire; few of its knights ever reach the Levant. Greek "
        "states rise at Nicaea and Trebizond, Theban magi follow the "
        "refugees east, and Thebes claims the border lands for them. War "
        "between the two Tribunals is averted by Aurora and quaesitores of "
        "both, who give Nicaea to Thebes and Trebizond to the Levant. (The "
        "book does not date the settlement.)",
        "",
    ),
    (
        1213,
        "",
        "The Treaty's third term; Arash refuses the Oath",
        "The renewal won, barely, in 1207 takes effect. At his induction "
        "into the Order, Arash, apprentice of Rachel of Criamon, refuses "
        "the Oath of Hermes after a crisis of the spirit and swears the "
        "Treaty of Barcelona instead. Magi threaten him, and House Criamon "
        "spirits him away to Baghdad.",
        "",
    ),
    (
        1215,
        "",
        "Felix passes his Gauntlet",
        "Felix, born to covenfolk at Domus Pacis, whose Gift showed itself "
        "only at twenty-eight while he was a guard there, becomes a magus "
        "of Guernicus. His parens Raymond is killed soon after in a fight "
        "with a hedge wizard that lames Felix, who takes up Raymond's watch "
        "on House Criamon and the Kabbalists. (The book says five years "
        "before 1220.)",
        "",
    ),
    (
        1218,
        "",
        "The Fifth Crusade lands in Egypt",
        "The crusaders strike at Egypt, the heart of Muslim power, and "
        "besiege Damietta. Al-Kamil offers them every old Latin land west "
        "of the Jordan and a thirty-year truce if they will leave Egypt, "
        "and they refuse. The war strains the Treaty of Baghdad as nothing "
        "has since 1193.",
        "",
    ),
    (
        1219,
        "",
        "Damietta falls; the True Cross founded",
        "Damietta falls to the Crusade. Two young magi, David of Tremere "
        "and Xydas of Bonisagus, found the True Cross in the city, with a "
        "few grogs and friends in the garrison, and call on the Order to "
        "join them. In Syria al-Mu'azzam pulls down Jerusalem's walls, so "
        "that the crusaders cannot hold the city if they take it.",
        "",
    ),
)


def build(levant: Levant) -> None:
    """Enter every event of `EVENTS` in the Tribunal's Diary, in order of
    year and season. Nothing is written when the Tribunal has not been
    made yet (the parts build in order, this one after the Tribunal's)."""
    tribunal = levant.tribunal
    if tribunal is None:
        return
    for year, season, title, details, hidden in sorted(
        EVENTS, key=lambda e: (e[0], SEASON_ORDER[e[1]])
    ):
        levant.b.event(tribunal, year, title, secrets(details, hidden), season=season)
    # The past meetings (tribunal.py's) take their places among the rest.
    tribunal.diary.sort(key=lambda e: (e.year, SEASON_ORDER.get(e.season, 0)))
