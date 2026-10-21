"""The magical and faerie landscape of the Hibernian Tribunal, as of 1220,
in paraphrase of The Contested Isle chapters ten and eleven, with what
chapter four adds about the ambassadors: the druids as they were and as
the word is used now (geasa in their summary), the Coill Trí and its
seven túatha, the bards and their four great schools, the faerie bards
(the Ollamhain), the elder races (the Tuatha Dé with Mug Ruith, the Fir
Bolg with King Rudraige and Fothaid, the Fomórach with King Madán and
Ainid), the beasts of magic under the Eagle King, and the faeries of
Ireland at large, each as a faction; the five High Roads from Tara as
Faerie trods; and the Otherworld's places no province chapter has (Tír
na nÓg, Tír Tairngire, Teach Duínn, Slievanamon, Goibhniu's ale-house,
Dian Céacht's pools).

The creatures with stat blocks (the fíorláir, the dobhar-chú, Donn,
the trooping faerie, Caílte, the Head of Arastotail) are the Bestiary's;
the Treaty of Cnoc Maol Réidh's clauses and the ambassadors' list are the
Tribunal part's, which reads `hibernia.tuatha` from here. Places the
province chapters describe (Tara, Dairbhre, the Aran Isles, Tír
Fhomóraig) are their parts'; `finish` only places the factions in them
and links the people other parts made, looked up with `.get`.

Keys: world["druids"], ["coill_tri"], ["bards"], ["ollamhain"],
["tuatha_de"], ["fir_bolg"], ["fomorach"], ["beasts_of_magic"],
["faeries"], and the schools world["dromnea"], ["baile_ui_eodhasa"],
["ceall_cluaine"], ["cahir_school"]; places["slighe_assail"],
["slighe_chualann"], ["slighe_dhala"], ["slighe_mhor"],
["slighe_mhidluachra"], ["tir_na_nog"], ["tir_tairngire"],
["teach_duinn"], ["slievanamon"], ["goibhniu_ale_house"],
["dian_cecht_pools"]."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..builder import paragraphs

if TYPE_CHECKING:
    from ...models import Neighbour
    from . import Hibernia

SKETCHED = (
    "Sketched as a faction until the app models hedge magic: its powers "
    "are summarised here, and a member who needs them is played from The "
    "Contested Isle and Hedge Magic Revised Edition."
)

RUMOURED: dict[str, Any] = {"status": "Rumoured", "known": "Locally"}
TRIBUNAL_WIDE: dict[str, Any] = {"status": "Known", "known": "In the Tribunal"}

#: The Coill Trí's seven túatha in the book's order, (name, ceannaire);
#: the book leaves three for the troupe to make.
TUATHA: list[tuple[str, str]] = [
    ("Túath Buidhe", "Buidhe"),
    ("Túath hEilionora", "Eilionora inghean Ua Shuibne"),
    ("Túath Saidhbh", "Sadhbh Amhreaidh"),
    ("Túath Rónáin", "Rónán Brathair"),
]

#: Each faction's home, by its key: the place keys to try, in order.
HOMES: dict[str, tuple[str, ...]] = {
    "druids": ("ireland",),
    "coill_tri": ("connacht",),
    "bards": ("ireland",),
    "ollamhain": ("ireland",),
    "tuatha_de": ("ireland",),
    "fir_bolg": ("arainn_mhor", "aran", "aran_isles", "connacht"),
    "fomorach": ("tir_fhomoraig", "tory", "ulster"),
    "beasts_of_magic": ("ireland",),
    "faeries": ("ireland",),
}

#: Places of other parts a faction's home may be, by name, when the key
#: is not one this part knows.
HOME_NAMES: dict[str, tuple[str, ...]] = {
    "fir_bolg": ("Árainn Mhór", "The Aran Isles", "The Isles of Aran"),
    "fomorach": ("Tír Fhomóraig", "Toraigh", "Tory Island"),
    "tuatha_de": (),
}

#: Each bardic school's province, by its key.
SCHOOL_PROVINCES: dict[str, str] = {
    "dromnea": "connacht",
    "baile_ui_eodhasa": "ulster",
    "ceall_cluaine": "leinster",
    "cahir_school": "munster",
}


def build(hibernia: Hibernia) -> None:
    _druids(hibernia)
    _coill_tri(hibernia)
    _bards(hibernia)
    _schools(hibernia)
    _races(hibernia)
    _beasts(hibernia)
    _faeries(hibernia)
    _high_roads(hibernia)
    _otherworld_places(hibernia)


# ------------------------------------------------------------ the druids


def _druids(hibernia: Hibernia) -> None:
    b = hibernia.b
    hibernia.world["druids"] = b.faction(
        "The Druids (draoithe)",
        faction="Hedge coven",
        realm="Magic",
        rules=(
            "Now only a title: any Gifted wizard, or any member of a hedge "
            "tradition, is called a draoi; a hedge wizard without either is "
            "an asarlaí. Many of the Code's oaths bind only druids and "
            "magi, not the asarlaithe."
        ),
        wants="Their old lore recovered; to be let alone by the Order",
        offers="Divination, geasa, shape-changing and weather-working",
        summary=paragraphs(
            "The learned class of pagan Ireland is gone. Its druids kept "
            "the lore in memory, judged, advised kings, served the old "
            "gods, foretold and worked magic, and would not set their "
            "secrets down in writing, so what is known of them now is "
            "rumour and story. They were already failing under Saint "
            "Patrick's missions and vanished from society in the ninth "
            "century. Irish druidry was never House Diedne's, and both "
            "are now thought extinct.",
            "The word covered three callings. Every druid began with four "
            "years as a bard, the keeper of tales and maker of poems, who "
            "trained his memory in place of writing. Some went on to four "
            "years as a fáith (plural fáithi), the priest who tended a "
            "clan's gods and read their will by divination, and some of "
            "those to the draoi (plural draoithe), counsellor, lawgiver "
            "and chief magician of a clan: twenty years in all.",
            "Their magic, as the tales tell it: memory so trained it "
            "seemed uncanny, divination above all, the laying of "
            "prohibitions and curses that marked out kings and champions, "
            "changing their own shape or another's (often as a curse), "
            "illusion, and for a few, weather, which in war meant mist "
            "and storm sent against the foe. The Pictish gruagachan of "
            "Hedge Magic Revised Edition have every one of these powers "
            "but weather, and may be the other branch of the same "
            "tradition; the druids had no tattoo magic, no tie to giants "
            "and no external soul. Whether Diedne's Breton and Gaulish "
            "line was kin to them is left to each saga.",
            "Their gods were whatever was supernatural: one of the Tuatha "
            "Dé, an ancestor, a hero, a beast, a rock or an old tree, and "
            "none was god of anything in particular. Each clan had its "
            "own, placated by its fáith; the draoi dealt with every other "
            "power that the clan did not worship.",
            "Diedne first came in 793 and offered the chief druid "
            "Sechnassach a place in her House or death; he laughed her "
            "off. She came back in 797 with twenty-seven of her House, "
            "landing near Wexford, and three bands of nine hunted the "
            "druids across Ireland. Most chose death. By 816 she told the "
            "Tribunal that none were left, an overstatement, but the "
            "tradition was broken. In 806 she met Pralix on the shore of "
            "Lough Cuan, each sure the other had come to help her; the "
            "quarrel became an unlawful Wizard War, and neither ever "
            "charged the other or said who struck first.",
            "Today most Irish hedge wizards claim druid blood, mostly "
            "without cause. Connacht's wizards call themselves druids as "
            "members of the Coill Trí (see that faction); the Pact of "
            "Oireadh is Connacht's other druid circle (see Connacht).",
            "Geasa. A geas (or geis) is an enchantment that punishes a "
            "forbidden act. Druids laid them on kings and champions to set "
            "them apart and on enemies as curses; some hedge wizards can "
            "still make one, and old-fashioned faeries love them. A "
            "fortifying geas is a Minor Virtue, often with a small "
            "uncanny sign, joined to the Prohibition Flaw: break the "
            "condition and both are lost, perhaps to be won back by making "
            "amends to whoever laid it. Death Prophecy is a mighty "
            "fortifying geas that holds death off while its condition "
            "stands. A prohibition geas is the Prohibition Flaw alone; "
            "breaking it swaps it for another Minor Flaw, or for a "
            "while a Major one that heals like a Heavy Wound or with "
            "amends, after which the prohibition returns. A blight geas "
            "is set off by outside circumstance, as Baneful Circumstances "
            "and Macha's Birth-Pangs (the ces noidhen) are. A geas names "
            "a kind of person, beast, thing or place, a circumstance, and "
            "an injunction: 'never' for a prohibition, 'always' for most "
            "fortifying geasa, 'while' or 'if' for a blight. Baneful "
            "Circumstances and Lesser Malediction: Macha's Birth-Pangs "
            "are in the catalog; geasa as a system are not modelled.",
            SKETCHED,
        ),
    )


# ------------------------------------------------------------ the Coill Trí


def _coill_tri(hibernia: Hibernia) -> None:
    b = hibernia.b
    hibernia.tuatha = list(TUATHA)
    hibernia.world["coill_tri"] = b.faction(
        "The Coill Trí",
        faction="Hedge coven",
        ruler="Seven ceannairí, one for each túath",
        realm="Magic",
        rules=(
            "Every hedge wizard in Connacht is taken to be a member; those "
            "outside it wear an amulet of three hazel leaves. Each of the "
            "seven túatha must find one Gifted child every seven years for "
            "the Order. A new clause of the Treaty needs a Tribunal's vote "
            "and every ceannaire's consent, and a magus must propose it."
        ),
        wants=(
            "Freedom from the Order's bullying; relief from the tithe of "
            "children; justice at the Sacred Council"
        ),
        offers=(
            "Seven Gifted children at every Tribunal; a single party for "
            "the Order to treat with in place of hundreds of hedge wizards"
        ),
        summary=paragraphs(
            "The federation of Connacht's non-Hermetic wizards, of many "
            "traditions, all claiming to be the heirs of the scattered "
            "druid lore and all taking the druid's title. In 844 Cormacan "
            "the Learned, Chief Bard of Ireland, came to the Order on "
            "behalf of High-King Congalach Cnogba, whose hedge-wizard "
            "subjects complained of harassment; Fedelmid Ua Heirméais of "
            "House Mercere spoke for the Order. Diedne's pogrom had shown "
            "that Join or Die fails in Ireland, so the two sides made the "
            "Treaty of Cnoc Maol Réidh (see the Tribunal), binding from "
            "the Tribunal's first meeting in 898. The wizards it bound "
            "were first called the Comman Cosán Chían (roughly, a league "
            "of the old way); from its three Cs (in ogham, C is coll, "
            "the hazel) the name soon wore down to the Coill Trí, the "
            "three hazels.",
            "The Order urged, and sometimes forced, hedge wizards who "
            "fought magi over resources to move to Connacht, leaving the "
            "rest of the island to the Hermetic magi. The Coill Trí now "
            "number at least as many as the Hibernian Order and perhaps "
            "far more. It is a legal person, not a rival: it has no "
            "centre, no rules, no common aims and takes no joint action, "
            "and attempts to raise it into a native host fail on the "
            "suspicion The Gift breeds, which suits the Order. Membership "
            "is rarely a choice for a draoi.",
            "What it gives its members is the Treaty's protection. A "
            "wronged draoi may complain at Tribunal and is owed an "
            "investigation and justice, but few do, preferring a little "
            "abuse to the Order's scrutiny; more often members bring "
            "quarrels with one another or with supernatural beings to the "
            "Sacred Council, where Hermetic judges see that the weaker "
            "side is treated fairly. Its own ambassador, chosen from its "
            "ranks, speaks for every wizard in Ireland, must see the "
            "children delivered and the parties to a case brought, and is "
            "trusted by neither side; a hedge wizard can bring a case or "
            "make a treaty only with its sponsorship.",
            "The tithe of seven Gifted children chafes most. Not every "
            "draoi can see The Gift, so offered children are sometimes "
            "refused; when the tithe is late, Redcaps go into Connacht to "
            "demand it of known druids, and the red-capped stranger "
            "hunting children has become a Connacht bogey, more than once "
            "chased off by a mob. Some magi use their power to extort "
            "services from the Coill Trí, who dare not complain. The "
            "Treaty has never been tested at Tribunal, and the day is "
            "near: English magi call it a mockery of a Code made for "
            "Hermetic magi, and some Irish magi covet Connacht. Most "
            "members are Christian, if not orthodox, and some Connacht "
            "clergy notice that the bishop's court keeps finding "
            "deviants tied to an organization they know almost nothing "
            "of, and wonder if it is a nest of heretics or worse.",
            "The seven túatha. Each túath is a region, takes its name from "
            "its current ceannaire, and sends the ceannaire to Tribunal; "
            "some ceannairí carry their members' complaints, others make "
            "members speak for themselves. Most túatha exist only in name, "
            "a few are run like a chief's clan with rules and courts, and "
            "ceannairí are elected, born to it or chosen by lot. Unless "
            "said, the troupe places them; the book describes four and "
            "leaves three for the troupe.",
            "Túath Buidhe: mostly unGifted visionaries rebuilding the "
            "druid lore from its fragments into a cult on the old "
            "legends, with scores of Initiation Scripts gathered from "
            "other members and dozens more of their own making, which "
            "they will gladly use to Initiate anyone in the Coill Trí; "
            "the storyguide decides whether they like the Order or still "
            "hate it for Diedne. Their ceannaire always comes from one "
            "line of Cruithnigh wizards. Buidhe himself, a mystagogue "
            "thought mad, lives on an island off Connacht's west coast, "
            "where visitors find him naked in the rain talking to a rowan "
            "or entranced under a bull's hide; his memory holds scripts "
            "for many Supernatural Virtues, most of which he lacks, and "
            "if he can be kept attentive he usually agrees to Initiate.",
            "Túath hEilionora: every member who lives outside Connacht, "
            "so that hedge wizards elsewhere share the Treaty's "
            "protection and magi near a tradition can treat with it at "
            "law; twice the size of any other. Its ceannaire is whoever "
            "settles in a certain Magic aura (the saga chooses it) on her "
            "predecessor's appointment. Eilionora inghean Ua Shuibne, an "
            "elemental physician who learned her craft in France, is "
            "devoted to the restoration of the old lore, reads the old "
            "tales eagerly and half believes she is Macha Mhuinge Ruadh "
            "reborn, the queen who founded Ireland's first hospital at "
            "Bron Bherg (see Eamhain Mhacha, Ulster). The native "
            "traditions think her an upstart and shun her; she bears it "
            "and stays active.",
            "Túath Saidhbh: unusually many Gifted members, always, who "
            "avoid one another and share no culture; they draw lots for "
            "the hated post of ceannaire. Magi long to know why the "
            "region breeds The Gift, but the Treaty keeps them out, even "
            "those born there. Sadhbh Amhreaidh, a cold, bitter folk "
            "witch who sneers at the likes of Eilionora, claims endless "
            "generations of witches behind her; she and her grandmother "
            "alone survived a mundane attack on their coven, and no "
            "other coven will take in witches who teach Embitterment "
            "(Tales of Mythic Europe). She has no daughter yet to teach.",
            "Túath Rónáin: lately shamed when a magus, not its own "
            "people, uncovered a diabolic coven among its members. Its "
            "ceannaire now keeps three inquisitors watching the rest, and "
            "suspicion weighs hardest on its Gifted. Rónán Brathair, a "
            "Cistercian monk and a draoi who helped root the coven out, "
            "uses the Holy Powers of Intervention and Understanding by "
            "Meditation and would turn the Coill Trí toward God, knowing "
            "how large a task that is.",
            "Three further túatha: not described in the book; the troupe "
            "names them and their ceannairí as needed.",
            "Faolán of the Younger House lives among the Coill Trí in "
            "breach of the Treaty (see Connacht).",
            SKETCHED,
        ),
    )


# ------------------------------------------------------------ the bards


def _bards(hibernia: Hibernia) -> None:
    b = hibernia.b
    w = hibernia.world
    w["bards"] = b.faction(
        "The Bards (filídh)",
        faction="Other",
        decides="Its leader",
        ruler="The ard-ollamh Érenn, the Chief Bard of Ireland (vacant since 1218)",
        rules=(
            "Nine grades of learning; four years and a hard examination "
            "make a filí, twelve an ollamh, who may found a school. Only "
            "the Chief Bard may strip a bard of rank, and only a bard's "
            "son and grandson may become Chief Bard. Mixing music with "
            "bardic tales is a grave sin to the schools."
        ),
        wants="Patrons, the old tales kept, a new Chief Bard",
        offers="Lore, genealogy, praise or satire, and schooling for nobles' sons",
        summary=paragraphs(
            "Of the three druid callings only the bards lived through "
            "Christianity and Diedne, dismissed as mere poets by the "
            "one and as petty conjurers by the other, and they are "
            "little changed in 1220. They keep the old tales and "
            "Christian homilies in verse and prose and make new works "
            "for the kings who keep them, and they call themselves "
            "filídh (singular filí) rather than bards, to put their "
            "druid past further behind them.",
            "Their schools double as Ireland's grammar schools for "
            "aristocrats' sons: four years of grammar, composition, "
            "history, genealogy, geography and custom, then the "
            "examination. Those who stay grow their memories further; "
            "a senior bard knows more than two hundred stories and "
            "builds poems with many layers of meaning. The Chief "
            "Bard is the high-king's own poet and king of the bards, "
            "who settles their quarrels with outsiders and sets the "
            "fashions of verse. The last, Giolla Ernain Ua Martain, "
            "died in 1218, and no successor has been chosen.",
            "Bards inherit the old reverence for druids. Their "
            "immunity, once the high-king's guarantee, has lapsed, "
            "but their name still protects them: Irish households "
            "owe a known bard hospitality, feuding with one was long "
            "forbidden, and even robbers fear to touch one, so a bard "
            "walks the roads in safety.",
            "Bard characters: the Social Status Virtues Bard (free; a "
            "filí of the rank of Dos, Local Reputation 1, aged 20 or "
            "more), Senior Bard (Minor; a Cano or Cli after five or "
            "six years, Reputation 2, 90 extra experience points) and "
            "Master Bard (Major; an Anruth after nine years, "
            "Reputation 3, 240 extra points, two seasons a year "
            "teaching or composing for a lord), with Bardic Education "
            "(the catalog's Educated (Bardic), 50 points) for the "
            "years of study; the Protection Virtue for the respect "
            "they are owed, worth more where the English are weak; "
            "Profession: Storyteller or Poet, the lores, and the Art "
            "of Memory (or Concentration). Enchanting Storytelling "
            "is Enchanting Music told as a tale. All are in the "
            "catalog.",
            "Bards of power. A few senior bards keep the druids' "
            "magic in the making of their works rather than the "
            "telling: Máistirs whose verse is uncannily beautiful, "
            "and many of them wordsmiths, with Touched by (Realm), "
            "usually Faerie, who make wondrous tales and poems as "
            "others make wondrous items, using Communication + "
            "Profession: Storyteller or Poet, limited to Personal "
            "Range, Performance Duration and Sound Target, and usable "
            "only by the one they were made for; reciting one makes "
            "an Arcane Connection to the reciter that a magus can "
            "catch. The Uí hUiginn school has most of them, some able "
            "to work craft magic like the Rusticani. The book gives "
            "five such tales: The Youthful Exploits of Cú Chulainn "
            "(ReCo 30, listeners ignore fatigue and wounds), Fear "
            "Diadh's Last Stand (CrMe 20, +3 against fear), The "
            "Daghdha's Escape from Indech's Ráth (ReMe 20, an "
            "unbreakable sleep), Manannán Mac Lir's Chariot "
            "(MuAq(Te) 30, walking on water) and Blrrmm, Blrrmm "
            "(Mu(Re)Im 10, listeners can only babble).",
            "The new Duration Performance (as Concentration: it lasts "
            "while the caster performs, after a Communication + "
            "Ability roll against 3) and Target Sound (as Structure: "
            "everyone who hears the sound within a Voice range of it) "
            "need Performance Magic or Sensory Magic for Hermetic use; "
            "the app does not model either.",
            "The four great schools are Dromnea of the Uí Dálaigh, "
            "Baile Uí Eódhasa, Ceall Cluaine of the Uí hUiginn and "
            "Cahir of the Mac Craith (each its own record). The "
            "Ollamhain, faerie musicians who steal the ollamh's "
            "title, are their rivals (see that faction).",
            SKETCHED,
        ),
        secrets="Some senior bards still hold their druid forebears' magic, "
        "though not every bard of high grade can, and no bard will "
        "own that such magic exists.",
    )
    w["ollamhain"] = b.faction(
        "The Ollamhain",
        tradition="trad_ollamhain",
        faction="Hedge coven",
        realm="Faerie",
        rules="Faerie wizardry worked through music, outside the bardic schools",
        wants="The bardic title, and audiences to enchant",
        offers="Glamour and music stronger than any filí's",
        summary=paragraphs(
            "A small band of faerie magicians (Realms of Power: "
            "Faerie) who call themselves the masters, taking the "
            "learned grade of ollamh for a tradition that conjures "
            "glamour with music. They are stronger in magic than the "
            "Irish bards but lack their good name. The schools teach "
            "none of it: music is a lesser art to them, using it for "
            "glamour betrays the tradition, and the Ollamhain carry "
            "the title with none of its lore or duty, so they are "
            "forbidden to call themselves filídh. Some do anyway, and "
            "wordsmiths have tried to prosecute rivals before the "
            "Sacred Council. Between single bards and Ollamhain "
            "things may be respectful, each keeping to its own "
            "sphere, or a bitter feud.",
            "Story seed: the bardic schools' enmity could be turned "
            "against a covenant's rival, sparking a war of satire and "
            "rhymed slander.",
            "Faolán of the Younger House is the son in magic of a true "
            "Ollamh, and an Ollamhain singer was driven out of "
            "Roscommon (see Connacht).",
            SKETCHED,
        ),
        secrets="A 'bard' who takes the part of the covenant's rival or enemy "
        "is in truth one of the Ollamhain.",
    )


def _schools(hibernia: Hibernia) -> None:
    b = hibernia.b
    w = hibernia.world
    w["dromnea"] = b.university(
        "Dromnea, the Uí Dálaigh school",
        school="Cathedral school",
        ruler="Donnchadh Mór Ua Dálaigh",
        summary=paragraphs(
            "The school of the Uí Dálaigh, perhaps Ireland's most famous "
            "bardic family, which has given most of the Chief Bards of "
            "the last six hundred years. Its founder, Cearbhall Fionn mac "
            "Aonghus Ua Dálaigh, won the gift of poetry by drinking a "
            "faerie cow's milk; the great Cú Chonnacht Ua Dálaigh, held "
            "the best of Ireland's bards living or dead, was great-"
            "grandfather to the present head, Donnchadh Mór Ua Dálaigh. "
            "The family rule the Mhuintir Bháire peninsula, which the book "
            "puts in Connacht, as its chiefs. As political as the Mac "
            "Craith, but far quieter about it.",
            "A bardic school, entered as a cathedral school for its teaching limits.",
        ),
    )
    w["baile_ui_eodhasa"] = b.university(
        "Baile Uí Eódhasa, the Uí hEódhasa school",
        school="Cathedral school",
        summary=paragraphs(
            "The Uí hEódhasa school on the shore of lower Lough Erne in "
            "Ulster, known for epic verse of glorious battles and heroic "
            "slaughter. The taste for such poems has passed, and the "
            "school is out of fashion and short of patrons.",
            "A bardic school, entered as a cathedral school for its teaching limits.",
        ),
    )
    w["ceall_cluaine"] = b.university(
        "Ceall Cluaine, the Uí hUiginn school",
        school="Cathedral school",
        summary=paragraphs(
            "The Uí hUiginn school at Ceall Cluaine (Kilcloney) in "
            "Leinster, the smallest of the four great schools. It is "
            "famed for finely built tales that stack meaning on meaning, "
            "makes more magical tales than any other school (most of the "
            "wordsmiths are its filídh), and teaches music too, though "
            "not to its bardic standard in verse and prose. Tadg Ua "
            "Broin, seanachaidh of Lámbaird's clan, studied here.",
            "A bardic school, entered as a cathedral school for its teaching limits.",
        ),
    )
    w["cahir_school"] = b.university(
        "Cahir, the Mac Craith school",
        school="Cathedral school",
        summary=paragraphs(
            "The school of the Mac Craith, hereditary poets and "
            "chroniclers to their Uí Briain kin, who followed them into "
            "Munster. It sits inside Cahir Castle, near Waterford as the "
            "book has it, and is the most openly political of the bardic "
            "schools.",
            "A bardic school, entered as a cathedral school for its teaching limits.",
        ),
    )


# ------------------------------------------------------------ the elder races


def _races(hibernia: Hibernia) -> None:
    b = hibernia.b
    w = hibernia.world
    w["tuatha_de"] = b.faction(
        "The Tuatha Dé Danann",
        faction="Faerie court",
        realm="Faerie",
        ruler="No one leader; Bobd is king of the Munster Tuatha Dé",
        rules=(
            "Each is an individual with his own interests, not a god of "
            "anything; they were lived with and learned from, never truly "
            "worshipped. They can handle iron freely. Their ambassador is "
            "confirmed at the Sacred Council."
        ),
        wants="Their stories retold and lived again, and the vitality that brings",
        offers="Craft, enchanted treasures, healing, and a vote at Tribunal",
        summary=paragraphs(
            "Ireland's pagan gods, the children of Danu: faeries first "
            "bound to the great elemental spirit of the Danube, who "
            "took up a band of Nemed's grandson's people fleeing "
            "Ireland, dwelt with them in four mysterious cities, then "
            "led them back to conquer the Fir Bolg and later the "
            "Fomórach. For two hundred years they lived among their "
            "followers, marrying them and teaching their arts, until "
            "the Mílesians defeated them and they withdrew into "
            "cairns, tumuli and buried ráths. Many remain, kings, "
            "warriors and leaders, handsome and dressed like nobles, "
            "but they are seldom met. The Irish still honour them and "
            "remember their tales.",
            "Some of them: Aonghus mac Óg of youth, love and passion; "
            "Badhbh the war goddess, who bathes in her enemies' blood "
            "and whose sight is an evil omen; Brigid of fertility, "
            "healing and poetry, whose holy places a saint of the same "
            "name took over; Dian Céacht the physician; Donn the death "
            "god, gathering an army of spirits at Teach Duínn (see "
            "the Bestiary); Goibhniu the smith, maker of magic spears "
            "and of an ale that grants immortality, who hates Donn; "
            "Lugh of many crafts, the Tuatha Dé's saviour at the "
            "Second Battle of Moytirra; Manannán mac Lir of the sea, "
            "who drives his chariot round Ireland herding fish and "
            "whales; Oghma, who made the ogham letters; the Dagda, "
            "father of the gods as Danu is their mother, though not "
            "their leader; and Nuadha of the Silver Arm, their leader "
            "in the wars with the Fir Bolg and the Fomóir. The four "
            "treasures of the Tuatha Dé still exist.",
            "Their ambassador is Mug Ruith, a faerie in the role of a "
            "famous Munster druid who learned his craft from Simon "
            "Magus in Jerusalem, served many Munster kings as court "
            "wizard and, some say, beheaded John the Baptist, cursing "
            "the Irish with violence. He sits on the Sacred Council "
            "every seven years for Bobd, king of the Munster Tuatha "
            "Dé, flying in on the roth rámach, his oared wheel, in a "
            "bull's hide and a bird mask. He lives on Dairbhre off "
            "Desmond's west coast (see Munster) with his faerie "
            "daughter Tlachtga, a strong druid herself, who also "
            "keeps a sídhe on the Hill of Tlachtga (see Meath). His "
            "treasures, a shining chariot, a magic shield and a "
            "stone that once became a venomous eel, draw treasure "
            "seekers to the island.",
            "Their stories: comical tales they repeat for spectators "
            "who get caught in them (the Dagda once ate his way out "
            "of a pit of porridge, and may make a village dig and "
            "fill another); tales of craft and wonder (Manannán's "
            "cloaks of invisibility, Goibhniu's ale, Dian Céacht's "
            "healing pools); feuds, in which locals suffer; and "
            "tales of bloodshed that stir men to violence or warn "
            "them off it.",
            "Story seeds: an Irish rebel steals one of Manannán's "
            "cloaks to raid the English along the Leinster-Ulster "
            "border, and its faerie owner torments the next village "
            "until it is returned; thieves brew Goibhniu's ale and "
            "sell it to princes and knights, not knowing it turns to "
            "poison within the month unless he brews it, and a hedge "
            "wizard asks the magi to find the barrels; a covenfolk's "
            "contagious old Irish sickness defies Hermetic healing, "
            "and only one of Dian Céacht's pools will cure it; Donn "
            "steals Goibhniu's magic cow and hides it in a local "
            "king's ráth, and Goibhniu arms trooping faeries with "
            "enchanted spears to raid it; Lugh gathers young men, "
            "some of the macgnímartha among them, to raid the "
            "Fomóir islands again, and the magi fear the raid will "
            "bring a Fomóir invasion; a physician on his way to cure "
            "his king sees Badhbh and begs the magi to drive her off "
            "(poets say Strongbow saw her washing severed heads "
            "before his last battle).",
        ),
        secrets="Why the Tuatha Dé sided with House Diedne in the Schism War "
        "is still unknown, after two centuries of Cliffheart's "
        "questions (see Munster).",
    )
    w["fir_bolg"] = b.faction(
        "The Fir Bolg",
        faction="Family",
        realm="Magic",
        decides="Its leader",
        ruler="King Rudraige Ua Sláine, on Árainn Mhór",
        rules=(
            "Three tribes, each with a royal line free of deformity; "
            "their ambassador comes from the royal blood. A Fir Bolg "
            "has Magical Blood (Human), often Great (Characteristic) and "
            "Large, and unless royal the deformities of Fomóir blood."
        ),
        wants="Respect for their titles; their old pride restored",
        offers="Counsel to Connacht's rulers, healing and fertility, a vote at Tribunal",
        summary=paragraphs(
            "The people who came after the flood that ended the "
            "Nemedians, in three tribes: the Fir Bolg proper, the "
            "most numerous, who named the whole race, the Fir "
            "Domhnann and the Gaileoin. Landing in the south, they "
            "spread over the island and first cut it into the four "
            "provinces still used, all but Meath. In the north they "
            "met the Fomórach, bought peace with tribute and became "
            "their serfs, farming for idle Fomóir lords. Beaten by "
            "the Tuatha Dé at the First Battle of Magh Tuireadh, they "
            "were offered one province and chose Connacht; when the "
            "Fomórach came for tribute and found the Tuatha Dé there "
            "instead, those two went to war. Few remain in Connacht; "
            "most now live on the Aran Isles (see Connacht).",
            "They were once like humans but greater, taller, stronger, "
            "fairer and more skilled, peaceful farmers who could "
            "make the poorest ground bear; but Fomóir lords bred with "
            "them, and now few escape deformity but the royal line of "
            "each tribe, and the monstrous blood makes them wrathful "
            "and prone to the Ríastradh. Royalty is the Gentleman or "
            "Gentlewoman Virtue, about as much as humans grant their "
            "titles; the royal caste often has a power of healing or "
            "fertility, such as Purifying Touch or Control Fertility, "
            "and one with a Dark Secret or Black Sheep may hide or "
            "show a malformation.",
            "The Fir Bolg tribe is still the largest and leads: King "
            "Rudraige Ua Sláine, who rules the whole race, lives on "
            "Árainn Mhór with them. They are Christian, converted by "
            "Saint Grellan as this chapter has it (Connacht's chapter "
            "says Saint Patrick). The Fir Domhnann, the smallest and "
            "always closest to the Fomórach, took the Fomóir goddess "
            "Domnu as their own and keep the night as their Lady of "
            "Darkness wants; their druids have strange powers of "
            "darkness and healing that light undoes. The Gaileoin "
            "look Christian, and are a lazier, more casually sinful "
            "people than their neighbours.",
            "Their ambassador is Fothaid, one of the king's younger "
            "sons: seven feet tall, broad and brawny, graceful, a "
            "trained speaker as handsome in manner as in looks, and "
            "fiercely vain of his pure blood, raging at any hint of a "
            "flaw. He cares little for his people and uses the "
            "Tribunal to win admirers.",
            "Fir Bolg characters and battle transformations are as the "
            "Fomórach's (see that faction); Sláine, their leader, was "
            "the first high-king of Mythic Ireland.",
            SKETCHED,
        ),
        secrets="A secret circle of Gaileoin infernalists rules the tribe's "
        "king; the other tribes do not know. The meddling has left "
        "the Gaileoin royal line feeble-minded, puppets in all but "
        "name, though the tribe as a whole has been slow to fall.",
    )
    w["fomorach"] = b.faction(
        "The Fomórach",
        faction="Family",
        realm="Magic",
        decides="Its leader",
        ruler="King Madán Muinreamhair of Tír Fhomóraig",
        rules=(
            "Fewer than a hundred left, in a loose kingdom on the islands "
            "north of Ulster. A geas of the Tuatha Dé's druids weakens "
            "every Fomóir who stands on Irish soil; their ambassador comes "
            "from the royal blood."
        ),
        wants="To keep their race alive; old vengeance on the sons of Nemed",
        offers="Sea lore and sea power, a vote at Tribunal",
        summary=paragraphs(
            "The Fomórach (one is a Fomóir) say they were Ireland's first "
            "people, before Cessair's folk, whom they never met. Kin to "
            "the sea, the dark and the winter, they rode out the Flood "
            "that drowned Cessair, fought every people who came after "
            "until the Second Battle of Magh Tuireadh broke them, and "
            "withdrew to the northern islands, where they still are.",
            "Their elders were children of Domnu, goddess of the abyss. "
            "The Túatha Dé Domnu's ancient kings, Balor of the Evil Eye, "
            "Cichol the Footless and Indech, are kosmokrators (Realms of "
            "Power: Magic), spirits able to take vast elemental shapes; "
            "since the faerie gods beat them they have drawn their "
            "Aspects out of the world and take no part in it. Today's "
            "Fomórach are much diminished, trapped in huge, hideously "
            "misshapen bodies; most have given up preying on others, "
            "though a few still pirate quiet sea lanes. Their kingdom is "
            "Tír Fhomóraig, Tory and Rathlin (see Ulster).",
            "King Madán Muinreamhair, Madán Thick-neck, has no love for "
            "humans, since Nemed slew his four sons, but has come to see "
            "them as his race's hope and arranges marriages with the "
            "Cruithnigh of Rathlin, to his people's disgust. His "
            "ambassador is Ainid, chosen as the ugliest of his kin: "
            "her face all pustules, her arms badly mismatched, her bare "
            "feet clawed with horn. She flaunts her deformities, natural "
            "to her race, and enjoys the horror they cause; few know her "
            "well, but she bargains shrewdly and plays politics well, "
            "and four Fir Bolg slaves carry her on a bier so she never "
            "touches Irish soil.",
            "Fomóir characters are Magic Humans (Realms of Power: Magic) "
            "with Giant Blood, obvious deformities no two alike (Cichol "
            "had a great serpent's hindquarters; Lot had four eyes on her "
            "back and a mouth on her chest; her husband Goll had no eyes "
            "at all), often a bent for Aquam, and Baneful Circumstances "
            "on Irish soil. Their inherited Quality is the Blessing of "
            "Domnu (MuCo 15, constant): at home under water, with no "
            "penalties there, speaking and hearing normally, and "
            "recovering Might, Fatigue and wounds as on land. Common "
            "Qualities are Gigantic, Limited Gestures and Limited "
            "Movement; common Virtues Ways of the Sea, Voice of the Sea "
            "and Warped Senses.",
            "Fomóir blood runs in many humans, often hundreds of "
            "generations back: a mild monstrosity (Aquam Monstrosity, "
            "Disfigured, Hunchback, Obese) or a Monstrous Appearance, "
            "Giant Blood or Reserves of Strength, a wrathful temper, and "
            "the old heroes' battle transformations. The Ríastradh "
            "(Major Supernatural; Cú Chulainn's, from his half-Fomóir "
            "father Lugh) needs Fury or Wrathful and Fomóir descent: "
            "anger twists the hero into a Fomóir form built from three "
            "Qualities (Huge, Large, Improved Soak, Initiative or "
            "Attack), more for each Inferiority taken (a monstrous "
            "appearance, bloodlust, reduced Defense), resisted each "
            "round by Stamina + Concentration against 6 + the Angry "
            "trait, rising by one a round; it ignores Fatigue penalties "
            "and lasts until he falls unconscious. The Lúan Láith "
            "(Minor), the hero's light blazing from the brow, or the "
            "sian caurad, the hero's war cry, gives allied groups +3 "
            "and enemy groups -3 to Brave and Morale checks while he "
            "fights alone. Berserk counts as a battle transformation too. "
            "Ríastradh and Lúan Láith are in the catalog.",
            SKETCHED,
        ),
    )


def _beasts(hibernia: Hibernia) -> None:
    b = hibernia.b
    hibernia.world["beasts_of_magic"] = b.faction(
        "The beasts of magic",
        faction="Other",
        realm="Magic",
        decides="Its leader",
        ruler="The King of the Eagles",
        rules=(
            "Beasts of the Magic realm that speak and understand men's "
            "ways choose a representative among themselves, or a magus "
            "speaks for them; they make treaties only through him."
        ),
        wants="Not to be bound or enslaved by magi",
        offers="A vote at Tribunal; the favour of Ireland's magical beasts",
        summary=paragraphs(
            "Ireland's magical beasts are represented at Tribunal like "
            "any people. Until two meetings ago a fíorláir, a true "
            "mare, held the post; then an English magus clumsily "
            "asked her to be his familiar, which she took for a kind "
            "of magical bondage, and she gave it up. The King of the "
            "Eagles, who claims lordship over all Ireland's birds, now "
            "sits instead; Cliodna of Lámbaird brokered his coming.",
            "Among them: the fíorláir, sometimes born as a mare's "
            "seventh filly with no colt between, whom no ill power can "
            "touch, who keeps her rider from harm and outruns every "
            "horse. Lámbaird has tried and failed to breed one; a "
            "magus who enslaves one by magic will face the Eagle "
            "King's complaint, so she must be befriended. Where she "
            "first touched the ground grows Mary's Clover, a "
            "shamrock with four leaves, which may be enriched into a "
            "talisman: plated in silver, blessed by a priest and sung "
            "over to the Virgin daily for a season, it gives its "
            "wearer Luck. And the dobhar-chú, the king otter, white "
            "with black ears and a black cross on its back, hurt only "
            "by silver, often hunting in pairs; its killer dies of its "
            "curse within a day, but the skin with the cross, "
            "enriched by the one who killed it and survived, keeps a "
            "boat from drowning, a house from fire or a man from "
            "accident. Both are in the Bestiary.",
        ),
        secrets="Whether the Eagle King's claim to rule all Ireland's birds "
        "is true is unknown.",
    )


# ------------------------------------------------------------ the faeries


def _faeries(hibernia: Hibernia) -> None:
    b = hibernia.b
    hibernia.world["faeries"] = b.faction(
        "The faeries of Ireland (the daoine sídhe)",
        faction="Faerie court",
        realm="Faerie",
        rules=(
            "Each kind keeps its own traditions and its own wards. "
            "Any faeries besides the Tuatha Dé may name an ambassador to "
            "the Sacred Council; if they do not, House Merinita puts one "
            "forward."
        ),
        wants="Roles to play and people to play them on: vitality",
        offers="Entertainment, help, and danger, often all at once",
        summary=paragraphs(
            "Everyone in Ireland has met the Faerie realm somehow, from "
            "the peasant who glimpses a procession far off to the king "
            "who weds a faerie woman before his clan. Assemblies meet on "
            "sacred hills, mostly in Faerie auras, and faerie homes, "
            "cairns, tumuli and mounds, stud the land. Irish faeries are "
            "either merry and helpful or cruel and deadly; some steal, "
            "kill or eat people, and the kindly ones are fickle. Folk "
            "avoid the word: they say the good neighbours (daoine "
            "maithe), the people of the mound (daoine sídhe), the host "
            "of the hills (croc na gcnoc), or just Them (iad). Most are "
            "easy to recognise: some look like better-dressed, "
            "handsomer people, some like beasts (the Salmon of Wisdom, "
            "Fionn mac Cumhaill's two hounds), many like evil hybrids "
            "of man and animal.",
            "There are four kinds. The pagan gods, the Tuatha Dé, are "
            "the mightiest and rarest (their own faction). Social "
            "faeries, the hero-faeries, replay the deeds of heroes from "
            "the Ulster and Fenian cycles and every other tale, saints, "
            "devils and talking beasts included, and are the most "
            "peaceable; some magi hold that several faeries share one "
            "hero's saga, each living one episode ('Cú Chulainn Slaying "
            "Connla', 'Cú Chulainn Stealing Emer', 'Cú Chulainn Killing "
            "Cú Roí'), others that the Cú Chulainn of Ulster is one "
            "faerie, perhaps the Tribunal's strongest. Trooping faeries, "
            "the slua sí, are night gangs of destruction that copy "
            "fianna, Ostmen raiders or English knights, or look like "
            "the restless dead though they belong to neither the "
            "Infernal nor the Divine; they will not parley, and other "
            "faeries use them as the threat a protector guards against. "
            "Solitary faeries keep to one hill, river bend or bog: the "
            "three crones of Slievanamon, the old woman of the wood, the "
            "sea monster of Lough Derg, the crone of the River Barrow "
            "who drags swimmers down to keep her house, the old woman "
            "of the mountain who kills a girl who fails to finish her "
            "sewing, the banshee (bean sí) who wails before a death in "
            "her family, and Áillen mac Midgna, a three-headed magician "
            "of northern Connacht who keeps setting Tara alight by "
            "vomiting burning stones (see Meath).",
            "Famous heroes the faeries play: Cú Chulainn, who held off "
            "Connacht's army alone in the Táin Bó Cuailnge; Fionn mac "
            "Cumhaill of Leinster and the Fenian Cycle; Medb, Connacht's "
            "fierce, wise, merciless and boldly amorous queen; Sláine, "
            "first high-king, of the Fir Bolg; Saint Patrick; and the "
            "Devil, gambler, drinker and good company, so famous in Irish "
            "tales that faeries copy him. Since faeries mimic saints and "
            "demons too, a creature of another realm may be a faerie in "
            "disguise.",
            "Common powers: most have Faerie Speech and Faerie Sight and "
            "are Humanoid Faeries; Invisibility is the commonest power "
            "and Flight next. Others: Elf Shot (4 points, Init -4, "
            "Animal; darts seen by moonlight, each a Light Wound to a "
            "beast, often a cow), Faerie Stroke (5 points, Init -5, "
            "Corpus; a touch that strikes the victim dumb, like Twist of "
            "the Tongue), Thrust of the Wind (3 points, Init -3, Auram; "
            "as Charge of the Angry Winds) and Retreat to the Sídh (Corpus, 7 "
            "points, Init -7; the faerie alone goes at once to "
            "its home or anywhere it has an Arcane Connection to).",
            "Wards: holy symbols, herbs and iron stop many (but not the "
            "Tuatha Dé); a horse skull under the house or a hearth kept "
            "lit all year stops trooping faeries; fresh milk on the "
            "threshold keeps a solitary one out; a red ribbon on a cow's "
            "tail guards her from social faeries; birds' eggs and sheep "
            "bones in the walls, holy things on the west wall and hearth "
            "soot on sleeping children guard a home. A ward against one "
            "kind seldom works on another.",
            "Donn, the trooping faeries, Caílte mac Rónáin and his band "
            "of outlaws, and the Head of Arastotail are in the Bestiary.",
            "Story seeds: Fionn and his fian burst into a hillside "
            "wedding the magi attend, to take back a Leinster bride for "
            "her clan's honour; a hedge wizard swears his lord is "
            "guided by a false Saint Patrick (or a false devil); a "
            "faerie cat courts a lonely widow so as to feed on her "
            "priest's alarm; a faerie devil dices on the night roads "
            "for travellers' souls, and a covenfolk who met him wakes "
            "drained, saying Satan is abroad; a local king hears the "
            "banshee call his name, and the magi go into the Otherworld "
            "to plead with her.",
        ),
    )


# ------------------------------------------------------------ the High Roads

ROAD_COMMON = paragraphs(
    "One of the five High Roads (slíghe) found leading out of the royal "
    "fort at Tara the night Conn of the Hundred Battles came into the world; "
    "they reach every part of Ireland and are wide enough for two wagons "
    "abreast, unlike the rest of Ireland's roads, many of them mere "
    "rights of way. Each is a Faerie trod (Realms of Power: Faerie), a "
    "liminal space neither here nor there, with a Faerie aura of 2. At "
    "either end, at Tara or at the road's far terminus, its Guardian can "
    "be called: it seems to come, but in truth spirits the caller away "
    "into Faerie, where it may be won over, by beating it in its own "
    "challenge or by paying it vitality some other way, to let him "
    "travel. On the road time seems to pass as usual, but the traveller "
    "arrives having gone twenty-four times as fast, a day's journey in "
    "under half an hour, and may stop anywhere along it. One who can "
    "cross a Faerie threshold elsewhere meets the Guardian there "
    "without the Threshold's Guardian's help. Without Realms of Power: "
    "Faerie, treat each terminus as a Faerie regio boundary of 2 and "
    "the middle of the road as one of 4.",
    "Redcaps: Hibernia has no Mercere Portals, and its Redcaps use the "
    "High Roads in their place. In his Gauntlet an apprentice Redcap "
    "must beat one Guardian in its own way, then makes a pact with it, "
    "taking a geas that feeds it vitality; from then on a token victory "
    "is enough each time he takes that road. Over a career a Redcap may "
    "make such pacts with every Guardian and use the whole network.",
)

#: The five High Roads: key, name, route, Guardian.
ROADS: tuple[tuple[str, str, str, str], ...] = (
    (
        "slighe_assail",
        "Slíghe Assail",
        "Runs due west from Tara toward Lough Owel over the central "
        "plain and on to Rathcrogan (Rath Cruachain) in Connacht.",
        "Its Guardian is a middle-aged woman with a crooked staff, who "
        "some magi think looks like the descriptions of Pralix. She "
        "challenges the traveller to debate some arcane question, won by "
        "the cleverer answer rather than the deeper learning.",
    ),
    (
        "slighe_chualann",
        "Slíghe Chualann",
        "The road of Cuala: through Dublin, along the foot of the "
        "Wicklow Mountains, then down the River Barrow to Waterford.",
        "Its Guardian is Oisín son of Fionn mac Cumhaill on his faerie "
        "horse Embarr. The traveller must somehow bring him down from "
        "the saddle, and the moment he dismounts his faerie youth "
        "leaves him and he is old and shrivelled.",
    ),
    (
        "slighe_dhala",
        "Slíghe Dhála",
        "Dála's road: south-east from Tara to the Liffey, then "
        "south-west over the Bog of Allen to Limerick and the mouth of "
        "the Shannon.",
        "Its Guardian is a Black Dog, fear made flesh; the traveller "
        "must master it and his own terror.",
    ),
    (
        "slighe_mhor",
        "An tSlíghe Mhór",
        "The Great Road: south from Tara, then along the Eisgir Riadha, "
        "the line of mounds over the central plain from Dublin Bay to "
        "Galway Bay, by Durrow and Clonmacnoise.",
        "Its Guardian is Gamal mac Figal, a doorkeeper of the Tuatha Dé, "
        "who makes the traveller prove that he is unique in an Ability "
        "of his choosing.",
    ),
    (
        "slighe_mhidluachra",
        "Slíghe Mhidlúachra",
        "North from Tara through the foothills of the Mournes to Eamhain "
        "Mhacha, round the east and north shores of Lough Neagh, ending "
        "at Derry.",
        "Its owner is a faerie lord who plays the traveller at "
        "fidhceall; a loser may not arrive quite where he meant to. A "
        "Redcap who has beaten him finds a single piece left on his "
        "board.",
    ),
)


def _high_roads(hibernia: Hibernia) -> None:
    b = hibernia.b
    ireland = hibernia.places.get("ireland")
    for key, name, route, guardian in ROADS:
        hibernia.places[key] = b.place(
            name,
            realm="Faerie",
            aura=2,
            inside=ireland,
            summary=paragraphs(f"{route} {guardian}", ROAD_COMMON),
            **TRIBUNAL_WIDE,
        )


# ------------------------------------------------------------ the Otherworld


def _otherworld_places(hibernia: Hibernia) -> None:
    b = hibernia.b
    p = hibernia.places
    ireland = p.get("ireland")
    munster = p.get("munster")
    p["tir_na_nog"] = b.place(
        "Tír na nÓg, the Otherworld",
        realm="Faerie",
        inside=ireland,
        summary=paragraphs(
            "The Irish faeries' Otherworld: a lovely, uncanny mirror of "
            "the land around it, close by and yet apart. It is called Tír "
            "na nÓg (Land of the Young), Tír na mBeo (Land of the "
            "Living) or Mag Mell (Delightful Plain), and "
            "Hermetic scholars cannot tell whether they name one place "
            "or many. They do know the names point to the three faerie "
            "worlds of Realms of Power: Faerie: half of Ireland's "
            "faeries live in Elysium, the land of myth that keeps a "
            "people's history; a third in Eudokia, among the turning "
            "points of single lives, where babies are taken, wives "
            "stolen and drunkards led astray; and the fewest, though "
            "more each year, in Arcadia.",
            "It is reached from faerie homes: most often a mound "
            "(sídhe, which also names the faeries), inside either a "
            "rough dwelling of stone pillars and earth roof or a "
            "sunlit, summery mansion; also cairns, tumuli, mountaintops, "
            "lake beds, the hearts of forests and bogs. Some are only "
            "Faerie auras, but many are regiones. It is the Faerie realm "
            "itself, not a site, so it has no aura of its own here.",
            "Story seed: faeries often move house. A child makes an "
            "abandoned faerie ráth his secret den, and after a month of "
            "play vanishes; its owner, a brutish swamp-ogre, has come "
            "home. Was the boy eaten, flayed or sold to another faerie? "
            "The magi must learn which and bring him back.",
        ),
        **TRIBUNAL_WIDE,
    )
    p["tir_tairngire"] = b.place(
        "Tír Tairngire, the Land of Promise",
        realm="Faerie",
        aura=1,
        inside=ireland,
        levels=[
            b.level(
                "Tír Tairngire",
                6,
                "Faerie",
                enter=(
                    "By the tree on the Isle of Man, the only entrance the "
                    "stories know; the Sídh of Lir in Ulster is said to be "
                    "another (see Ulster)."
                ),
                notes="The aura is the pack's choice; the book gives none.",
            )
        ],
        summary=paragraphs(
            "A vast Faerie regio lying over the sea all round Mythic "
            "Ireland. By the stories its one way in is on the Isle of "
            "Man, where a magical tree joins the island to it: the tree "
            "stands on four legs of white silver set on the ocean bed, "
            "and golden apples of power grow on its boughs. Whether it "
            "touches Tír na nÓg is unknown. Ulster's tale of the Sídh of "
            "Lir names it Lir's Otherworld, where fish graze like sheep.",
        ),
        **RUMOURED,
    )
    p["teach_duinn"] = b.place(
        "Teach Duínn, the House of Donn",
        realm="Faerie",
        aura=4,
        inside=munster,
        levels=[
            b.level(
                "Donn's hall",
                7,
                "Faerie",
                notes=(
                    "A large, guarded regio; its aura is the pack's "
                    "choice, the book gives none."
                ),
            )
        ],
        summary=paragraphs(
            "A rocky island off the Munster coast, the palace of "
            "Donn, the Dark One, death god of the Tuatha Dé (see the "
            "Bestiary), where the dead gather. Like any king he has "
            "sons and cattle and raids his neighbours. In wartime his "
            "three red-haired sons ride the land spreading terror, "
            "and the slain are said to rise here and join his host; "
            "in peace he roams adding to it one man at a time, "
            "killing a sleeper so that the spirit flies here, or "
            "leaving a false corpse in a living man's place and "
            "carrying the man off. His hall holds things that "
            "command the dead, walking corpse and haunting ghost "
            "alike. He fought the Order in the Schism War beside "
            "Salmon's Eye, and helped destroy Warbler's Way; "
            "Cliffheart, close by, still watches the Tuatha Dé.",
            "Why he takes living captives no one knows: as servants, "
            "husbands for his daughters, or subjects for his druids' "
            "experiments. No one knows why he builds an army either, "
            "beyond that kings do.",
        ),
        secrets="His great regio may hide a whole army, and magi wonder if "
        "he means to invade again. Munster's endless wars may set "
        "him off, and anyone starting a war with the Order would "
        "find him a ready ally.",
        **TRIBUNAL_WIDE,
    )
    p["slievanamon"] = b.place(
        "Slievanamon",
        realm="Faerie",
        aura=3,
        inside=munster,
        summary=(
            "A mountain of Munster, home of three crones, a small band of "
            "solitary faeries tied to no larger company. What they want "
            "of those who climb it is the storyguide's to decide. The "
            "book gives no aura; the pack sets Faerie 3."
        ),
        **RUMOURED,
    )
    p["goibhniu_ale_house"] = b.place(
        "Goibhniu's ale-house",
        realm="Faerie",
        aura=4,
        inside=munster,
        summary=(
            "The smith god Goibhniu's secret ale-house, somewhere on an isle off "
            "the Munster coast, where he brews the magic ale that grants "
            "immortality. Many treasure hunters have searched for it. Ale "
            "brewed to his recipe by anyone else turns to deadly poison "
            "within a month. The book gives no aura; the pack sets "
            "Faerie 4."
        ),
        **RUMOURED,
    )
    p["dian_cecht_pools"] = b.place(
        "Dian Céacht's pools",
        realm="Faerie",
        aura=3,
        inside=ireland,
        summary=(
            "Pools of magic water made by Dian Céacht, physician of the "
            "Tuatha Dé, that cure any sickness at all, even the old Irish "
            "diseases Hermetic healing cannot touch. Where they lie is "
            "left to the storyguide. The book gives no aura; the pack "
            "sets Faerie 3."
        ),
        **RUMOURED,
    )


# ------------------------------------------------------------ finish


def _named(hibernia: Hibernia, *names: str) -> Neighbour | None:
    """The first neighbour, made by any part, with one of these names."""
    wanted = {name.casefold() for name in names}
    return next(
        (n for n in hibernia.b.saga.neighbours if n.name.casefold() in wanted),
        None,
    )


def _home(hibernia: Hibernia, key: str) -> Neighbour | None:
    found = _named(hibernia, *HOME_NAMES.get(key, ()))
    if found is not None:
        return found
    return next((hibernia.places[k] for k in HOMES[key] if k in hibernia.places), None)


def finish(hibernia: Hibernia) -> None:
    """Put each faction and school in its province, tie the High Roads to
    Tara, and link the people and covenants other parts made, skipping
    any not made yet."""
    b = hibernia.b
    w = hibernia.world
    p = hibernia.places
    for key in HOMES:
        home = _home(hibernia, key)
        if home is not None:
            w[key].place_id = home.id
    for key, province in SCHOOL_PROVINCES.items():
        place = p.get(province)
        if key == "cahir_school":
            place = _named(hibernia, "Cahir Castle", "Cahir") or place
        if place is not None:
            w[key].place_id = place.id
    ireland = p.get("ireland")
    for key in ("tir_na_nog", "tir_tairngire", "dian_cecht_pools"):
        if ireland is not None and p[key].place_id is None:
            p[key].place_id = ireland.id
    munster = p.get("munster")
    for key in ("teach_duinn", "slievanamon", "goibhniu_ale_house"):
        if munster is not None and p[key].place_id is None:
            p[key].place_id = munster.id

    tara = p.get("tara")
    for key, *_ in ROADS:
        road = p[key]
        if ireland is not None and road.place_id is None:
            road.place_id = ireland.id
        if tara is not None:
            b.link(road, "places", tara, "Its terminus at Tara")

    dairbhre = _named(hibernia, "Tech Dairbhre", "Dairbhre", "Dairbhre Isle")
    if dairbhre is not None:
        b.link(w["tuatha_de"], "places", dairbhre, "Mug Ruith's home")
    for key, note in (
        ("cliodna", "Brought the Eagle King to the Tribunal"),
        ("faolan", "Lives among the Coill Trí in breach of the Treaty"),
    ):
        magus = hibernia.magi.get(key)
        if magus is not None:
            faction = "beasts_of_magic" if key == "cliodna" else "coill_tri"
            b.link(w[faction], "characters", magus, note)
    for faction, covenant, note in (
        ("tuatha_de", "cliffheart", "Studies the Tuatha Dé"),
        ("beasts_of_magic", "lambaird", "Tried to breed a fíorláir"),
        ("coill_tri", "praesis", "May enter Connacht on three errands"),
        ("coill_tri", "qui_sonant", "A haven for all under the Treaty"),
    ):
        found = hibernia.covenants.get(covenant)
        if found is not None:
            b.link(w[faction], "covenants", found, note)
    for creature, faction in (
        ("Fíorláir", "beasts_of_magic"),
        ("Dobhar-chú", "beasts_of_magic"),
        ("Donn", "tuatha_de"),
        ("Trooping faerie", "faeries"),
        ("Caílte mac Rónáin", "faeries"),
        ("The Head of Arastotail", "faeries"),
    ):
        made = next(
            (
                c
                for c in b.saga.creatures
                if c.name.casefold().startswith(creature.casefold())
            ),
            None,
        )
        if made is not None:
            b.link(w[faction], "creatures", made, "See the Bestiary")
