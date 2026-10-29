"""The nine active covenants of Heirs to Merlin (ch10), their magi, the
Redcaps and Mercer House, the natural magicians, and the ruins of the
fallen covenants whose sites are known (S6-S13).

The book prints no statistics (p. 5), so each covenant is a sketch with
what the text gives, its season where the book states one (Ungulus
Winter, Voluntas Summer turning Autumn, Libellus and Nigrasaxa Spring)
and inferred elsewhere (S6). Cad Gadu follows Houses of Hermes:
Societates (S7): Ebroin is Primus and a member, Immanola entered Final
Twilight in 1216 and is in the Diary, Gwrhyr is extremely old and sits
on the Council of Four, and the regio's top level has Magic 8. Libellus
and Nigrasaxa have no place record, their region in their summaries (S8).

Keys: places["england"], ["wales"], and the sites
places["blackthorn_caves"], ["burnham_castle"], ["cad_gadu_island"],
["schola_hall"], ["ungulus_tower"], ["wilton"], ["mercer_house"];
covenants["blackthorn"], ["burnham"], ["cad_gadu"], ["libellus"],
["nigrasaxa"], ["schola"], ["semitae"], ["ungulus"], ["voluntas"]; the
ruins places["sursum"], ["stellasper"], ["castrum_antiquum"],
["magnantrum"] and ["nameless"]. Magi under their names' keys
(magi["talion"], ["iudicium"], ...); the Redcaps and natural magicians
are companions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..builder import joined_lines, paragraphs
from ..records import KNOWN_ORDER, KNOWN_TRIBUNAL

if TYPE_CHECKING:
    from ...models import Covenant, Neighbour, Tribunal
    from ..records import Records

EX_MISC = "house_ex_miscellanea"
FLAMBEAU = "house_flambeau"
GUERNICUS = "house_guernicus"
TYTALUS = "house_tytalus"
TREMERE = "house_tremere"
MERINITA = "house_merinita"
JERBITON = "house_jerbiton"
BJORNAER = "house_bjornaer"
BONISAGUS = "house_bonisagus"
VERDITIUS = "house_verditius"
CRIAMON = "house_criamon"
MERCERE = "house_mercere"

#: (key, name, House, age, summary) for each covenant's magi.
Magus = tuple[str, str, str, int, str]


def build(records: Records) -> None:
    tribunal = records.tribunal
    if tribunal is None:
        return
    _lands(records)
    _sites(records)
    for builder in (
        _blackthorn,
        _burnham,
        _cad_gadu,
        _libellus,
        _nigrasaxa,
        _schola,
        _semitae,
        _ungulus,
        _voluntas,
    ):
        builder(records, tribunal)
    _redcaps(records)
    _natural_magicians(records)
    _ruins(records)
    records.magi["gwrhyr"].traditions = ["trad_columbae"]
    records.b.link(
        records.covenants["voluntas"],
        "places",
        records.places["wilton"],
        "Its village",
    )


def _place(records: Records, key: str, name: str, region: str, **kw: Any) -> Neighbour:
    place = records.b.place(name, inside=records.places.get(region), **kw)
    records.places[key] = place
    return place


def _magi(records: Records, covenant: Covenant | None, magi: tuple[Magus, ...]) -> None:
    for key, name, house, age, summary in magi:
        records.magi[key] = records.b.magus(
            name, covenant=covenant, house=house, age=age, summary=summary
        )


# -- the lands --


def _lands(records: Records) -> None:
    b = records.b
    records.places["england"] = b.place(
        "England",
        known="In the Order",
        summary=paragraphs(
            "The kingdom of the boy king Henry III, at peace in 1220 after "
            "the civil war: perhaps 9,500 parishes, rich towns, great abbeys "
            "and a dense web of royal officials, sheriffs and courts, with "
            "royal authority weak while the king is a minor. Its only title "
            "of nobility is earl. Wheat-lands, royal forests and moors; tin "
            "in Devon and Cornwall under the Warden of the Stannaries, lead, "
            "iron in the Forest of Dean and coal on Tyneside. Every magus here "
            "lives near the mundane world.",
        ),
    )
    records.places["wales"] = b.place(
        "Wales",
        known="In the Order",
        summary=paragraphs(
            "The principalities of Gwynedd, Powys and Deheubarth under their "
            "own laws (Hywel Dda's), with land divided among all a man's sons "
            "and blood-price for killing; most of it under Llywelyn ab "
            "Iorwerth the Great, Prince of Gwynedd, while Anglo-Norman Marcher "
            "lords hold the south and east. The Welsh Church keeps its clas "
            "churches of hereditary clergy.",
        ),
    )


def _sites(records: Records) -> None:
    b = records.b
    _place(
        records,
        "blackthorn_caves",
        "The Caves of Blackthorn",
        "wales",
        aura=3,
        summary="A warren of caves under the Black Mountains of south Wales, "
        "some natural, most dug by Blackthorn and Tagelyn over two centuries, "
        "their passages smoothed and their ceilings raised. The door, at the "
        "back of a large cave, is hidden by an illusion of rock that fools even "
        "the touch and is guarded from inside; nothing but working along the "
        "wall with an axe would find it. The book gives no aura; Magic 3 is "
        "inferred.",
        **KNOWN_TRIBUNAL,
    )
    _place(
        records,
        "burnham_castle",
        "Burnham Castle",
        "england",
        aura=3,
        summary="A stone motte-and-bailey castle in the far north-east, both "
        "parts ringed by a moat from a diverted river, wall and keep of "
        "seemingly mundane build; magi are sometimes seen at rituals on the "
        "keep's crenellated top. The book gives no aura; Magic 3 is inferred.",
        **KNOWN_TRIBUNAL,
    )
    _place(
        records,
        "cad_gadu_island",
        "The Isle of Cad Gadu",
        "wales",
        levels=[
            b.level(
                "The covenant",
                3,
                enter="Between the first pair of white pillars on the white "
                "stone path.",
                notes="The two U-shaped buildings and the trilithons; the lake "
                "is still seen, though mist hides the shore. The book gives no "
                "aura; Magic 3 is inferred.",
            ),
            b.level(
                "The ridge",
                5,
                enter="Between the second pair of pillars.",
                notes="A ridge path between sheer drops, with caves for the "
                "sancta. Magic 5 is inferred.",
            ),
            b.level(
                "The highest level",
                8,
                notes="Visitors tell of a tiny island in a stormy sea, or an "
                "endless meadow; there are likely several levels, some unknown "
                "to the magi. The top level has a Magic aura of 8 (Houses of "
                "Hermes: Societates p. 101).",
            ),
        ],
        summary=paragraphs(
            "An island in a lake among the mountains of Snowdonia, edged with "
            "twenty-foot cliffs, landed on only at a guarded wooden jetty. On "
            "the mundane level are three stone cottages for visitors, built "
            "into the ruins of the first covenant, and a path of white stone "
            "edged with larger white stones that leads between the regio's "
            "levels; stray from it, and the mists may keep you for ever. The "
            "island was a camp of the Columbae, Welsh ward-makers, where Pralix "
            "fought her last battle with Damhan-Allaidh; its name, the "
            "forsaken army, honours those who died.",
            "In Welsh law the island belongs to Gwrhyr of the Columbae, whose "
            "kindred will not let it pass to his adopted filius (Houses of "
            "Hermes: Societates p. 112).",
        ),
        **KNOWN_ORDER,
    )
    _place(
        records,
        "schola_hall",
        "The School of Pythagoras",
        "england",
        realm="Divine",
        aura=3,
        summary="A large stone hall near the river at Cambridge, known in the "
        "town as the School of Pythagoras: the library and great hall of "
        "Schola Pythagoranis, where the warden lives. The other magi keep "
        "houses in the town, sanctum-marked, and the covenant has a "
        "laboratory building on the edge of a faerie forest outside town, "
        "whose aura is better than the town's Dominion; it is looking for a "
        "magic aura. Divine 3, a town (DE p. 418).",
        **KNOWN_TRIBUNAL,
    )
    _place(
        records,
        "ungulus_tower",
        "The Tower of Ungulus",
        "england",
        aura=5,
        summary="A single round tower many floors high on a ridge in the Lake "
        "District, its outside covered in carvings: scenes, snatches of Latin "
        "and other tongues, writing no one can read and abstract patterns, "
        "whose meaning, if any, no one has found. Its covenfolk are inbred in a "
        "strong magic aura; the book gives no number, and Magic 5 is inferred.",
        **KNOWN_TRIBUNAL,
    )
    _place(
        records,
        "wilton",
        "Wilton",
        "england",
        realm="Divine",
        aura=2,
        summary="A village of stone houses, unusual in the area, fifteen "
        "minutes' walk from Voluntas, which serves as part of the covenant: "
        "its craftsmen live here and its inn lodges visiting magi. Its "
        "peasants, free and serf, have good houses and magical help in need, "
        "and an enchanted birthing chair keeps nearly every mother and child "
        "alive. Divine 2, a village (DE p. 418).",
        **KNOWN_TRIBUNAL,
    )
    _place(
        records,
        "mercer_house",
        "Mercer House",
        "england",
        aura=1,
        summary="A substantial house a little way outside Coventry, home of "
        "the Tribunal's unGifted Redcaps, built in a weak magic aura (Magic 1 "
        "is inferred). Its Hermes Portal reaches Harco, House Mercere's domus "
        "magna in the Roman Tribunal. Each Redcap's device returns him and his "
        "horse to its courtyard once a day, from anywhere in the Tribunal. "
        "Perceval's wife Lucy and their children live here.",
        **KNOWN_ORDER,
    )


# -- the covenants --


def _covenant(
    records: Records,
    tribunal: Tribunal,
    key: str,
    name: str,
    *,
    founded: int | None,
    season: str,
    summary: str,
    what_matters: str = "",
    place: str = "",
    level: int = 0,
    aura: int = 0,
    realm: str = "Magic",
    secrets: str = "",
) -> Covenant:
    covenant = records.b.covenant(
        name,
        tribunal=tribunal,
        founded=founded,
        place=records.places.get(place) if place else None,
        level=level,
        aura=aura,
        realm=realm,
        summary=summary,
        what_matters=what_matters,
        season=season,
        secrets=secrets,
    )
    records.covenants[key] = covenant
    return covenant


def _blackthorn(records: Records, tribunal: Tribunal) -> None:
    covenant = _covenant(
        records,
        tribunal,
        "blackthorn",
        "Blackthorn",
        founded=818,
        season="Autumn",
        place="blackthorn_caves",
        aura=3,
        summary=paragraphs(
            "Founded by Tremere magi in 818, and until lately the master of "
            "the Tribunal: few meetings were quorate, so it could not be called "
            "to account, and it held most of the votes at those that were. In "
            "the last twenty years that has changed, and its magi are "
            "scrambling. It hosts every meeting: a great hall soars into the "
            "rock, magically lit, its walls painted with Blackthorn's glories "
            "(the Capture of the Wild Hunt among them), with a platform for the "
            "Praeco and presiding Quaesitor and a dozen guest suites round it, "
            "each with a barred guardroom, common room, kitchen, dormitory and "
            "four bedrooms. Delegations may stay a month after a meeting.",
            "Unexpected visitors, even mundanes, are held in the entrance cave "
            "until a magus decides; reaching the common areas means crossing a "
            "magus's sanctum, which no magus of the Tribunal would risk. Its "
            "covenfolk, nearly all born there, see as well in darkness as in "
            "daylight, so the caves are unlit; guards wear mail, the public "
            "staff dark green, the general staff black, and each magus's own "
            "servants dark red with his badge, rotated so that no one sees the "
            "same faces two meetings running. Its hierarchy is believed strict "
            "and is unknown outside.",
        ),
        what_matters=joined_lines(
            "Covenfolk: dozens at least, born in the caves, who see in the dark",
            "Allies: none among the established covenants, who are wary of it",
            "Enemies: Voluntas, a feud of a century; Ashenrise in Hibernia, founded by Tagelyn's survivors",
            "Boon: Hidden Resources (the caves, never mapped by outsiders)",
            "Hook: Rival (Voluntas)",
            "Hook: Hermetic Politics (its lost hold on the Tribunal)",
            "Hook: Dark Secret (the old charges of diabolism)",
        ),
        secrets="The Wild Hunt is sealed in iron-bound caves near Blackthorn, "
        "where Flumen of Tremere led it in 1154; its cries went on for weeks "
        "and have stopped, and no one has seen it since.",
    )
    _magi(records, covenant, BLACKTHORN)


BLACKTHORN: tuple[Magus, ...] = (
    (
        "talion",
        "Talion",
        FLAMBEAU,
        150,
        "Praeco of the Tribunal, its eldest magus now that Immanola is gone. An ancient magus who has weathered age and Twilight remarkably, still in full possession of his faculties and, as far as anyone knows, his magic, but very careful now about casting. Once renowned for his mastery of Perdo; he favours elaborate robes of deep green and blue. The book makes him of Flambeau at a Tremere covenant and says no more of it.",
    ),
    (
        "iudicium",
        "Iudicium",
        GUERNICUS,
        140,
        "The senior quaesitor of the Tribunal, who presides at its meetings: with the Praeco, the hold that let Blackthorn keep its grip. A solid lawyer, competent wizard and capable politician, unremarkable in looks but for a writhing scarlet serpent tattooed on his left cheek by a long-ago Twilight; an ancient magus with his House's interest in Intellego and Mentem.",
    ),
    (
        "golias",
        "Golias",
        TYTALUS,
        100,
        "An old magus who keeps the illusion of one just out of apprenticeship, with unkempt brown hair and innocent blue eyes. No one is fooled, and everyone is kept off balance wondering why. Blackthorn's best political dealer, the more so as no one knows what he is about; his magical interests are unknown.",
    ),
    (
        "goliard",
        "Goliard",
        TREMERE,
        90,
        "Filia Flumen, the most vigorous maga at Blackthorn and its leader in all but name, perhaps born there; she took her parens's place when he passed into Final Twilight in 1187. Nearly ninety, she looks in her early forties, black hair streaked grey and bloodshot brown eyes, plainly dressed in undyed white but for the jewelled purple and crimson robes she wears for the meeting's ceremonies. She restored an ancient binding on an elemental spirit that was taking revenge on humanity with rockslides, and controls it still; decades later she led an expedition into the Atlantic and was found four years on, battered and unconscious, on the sands at Chester. Anyone who deals with Blackthorn deals with her: an effective negotiator who keeps her word, keen for friends among the covenants, who are wary.",
    ),
    (
        "fornax",
        "Fornax",
        TREMERE,
        60,
        "Goliard's filia, whose parens still holds her sigil: a mature maga who looks in her mid thirties, plain, with lank hair and a scarred face, and never known to be polite. She is said to work Rego and Mentem, to make people entertain her.",
    ),
    (
        "prelum",
        "Prelum",
        TREMERE,
        33,
        "Goliard's filia, her sigil held by her parens, a maga less than ten years: good-looking, with long red hair and good teeth, always polite and usually pleasant, though she can insult within every rule of courtesy. She has a remarkable talent for Vim.",
    ),
)


def _burnham(records: Records, tribunal: Tribunal) -> None:
    covenant = _covenant(
        records,
        tribunal,
        "burnham",
        "Burnham",
        founded=1141,
        season="Summer",
        place="burnham_castle",
        aura=3,
        summary=paragraphs(
            "A covenant in the far north-east that keeps to itself. It has "
            "only lately begun sending anyone to meetings, and its envoys "
            "abstain from most votes. It holds its castle under a grant of "
            "immunity won from King Stephen in the civil war and confirmed by "
            "Henry II, owing nothing in return, or nothing obvious. Its magi may "
            "be careful mediocrities or have great and deep plans.",
            "It does not welcome visitors: the Redcaps are treated well enough, "
            "but never asked to stay, uninvited magi are turned away, and a "
            "magus with urgent news might at best be heard in the bailey. The "
            "keep holds the sancta, the library and the council chamber, and "
            "only some servants may enter it. Its covenfolk do not talk to "
            "outsiders; they are well dressed and equipped, and recruited from "
            "outside the Tribunal as well as nearby.",
        ),
        what_matters=joined_lines(
            "Boon: Right (King Stephen's grant of immunity, confirmed by Henry II)",
            "Boon: Seclusion (no visitors)",
            "Hook: Dark Secret (no one knows what it is doing)",
        ),
    )
    _magi(records, covenant, BURNHAM)


BURNHAM: tuple[Magus, ...] = (
    (
        "aindread",
        "Aindread",
        EX_MISC,
        70,
        "A mature magus who came to Burnham soon after his apprentice's Gauntlet and has left only once since, to present Caitlin at the meeting. He answers no letters and writes none; his magical interests are unknown.",
    ),
    (
        "caitlin",
        "Caitlin",
        EX_MISC,
        30,
        "Aindread's filia, a young maga who sometimes represents Burnham at the meeting: heavily freckled, with one blue eye and one brown, smartly but plainly dressed, polite to all, and unmoved by the most tempting offers. She has voted Sachiko's sigil since 1201.",
    ),
    (
        "focus",
        "Focus",
        FLAMBEAU,
        50,
        "Scintilla's filius; nothing else is generally known of him.",
    ),
    (
        "scintilla",
        "Scintilla",
        FLAMBEAU,
        90,
        "Came to Burnham from eastern Europe at the end of the twelfth century, bringing Focus. She is said to be a powerful fire maga, but has done nothing of note in Stonehenge.",
    ),
    (
        "sachiko",
        "Sachiko",
        MERINITA,
        60,
        "Probably female. The Tribunal first knew of her when Caitlin voted her sigil in 1201; it has appeared at every meeting since.",
    ),
    (
        "trutina",
        "Trutina",
        GUERNICUS,
        60,
        "A quaesitor who joined Burnham in 1195 and has attended every meeting since, as custom demands. She says little, usually has her Redcap proxy vote with Iudicium, and pleads quaesitorial neutrality to avoid conversation. Very beautiful, long-haired and dark-robed, with a silver pendant of her House's badge; a mature maga of unknown interests.",
    ),
)


def _cad_gadu(records: Records, tribunal: Tribunal) -> None:
    covenant = _covenant(
        records,
        tribunal,
        "cad_gadu",
        "Cad Gadu",
        founded=815,
        season="Winter",
        place="cad_gadu_island",
        level=3,
        aura=8,
        summary=paragraphs(
            "The domus magna of House Ex Miscellanea, where Pralix founded "
            "the Ordo Miscellanea in 815. Most magi of the House neither know "
            "nor care where it is, so it counts for little in the Tribunal, and "
            "keeps to itself. Its common buildings stand on the regio's first "
            "level: to the right of the path the guest quarters, council "
            "chamber and library, which guests may not enter and whose wards "
            "only talismans pass; to the left the servants' quarters, kitchens "
            "and great hall, with a roped-off yard for the grogs. Past them the "
            "path forks through two trilithons, the left one sanctum-marked. "
            "Children are kept on a leash until, about eleven, a parent cuts "
            "the rope: that is the coming of age, so its turb has some very "
            "young grogs.",
            "Its council keeps a seat for Pralix, and every council opens, "
            'even before visitors, with the chairman saying, "Well, it looks '
            "like Pralix isn't coming\"; most think she went into the regio's "
            "higher levels. Uninvited visitors are turned back at the jetty; a "
            "useful trade or great service may earn an invitation.",
            "Since 1216 its Primus is Ebroin, elected when Immanola, who sat "
            "twelve years gazing into a pool, was declared in Final Twilight; "
            "he has restored the Council of Four. The covenfolk dreaded the day "
            "one of the other magi would take over from her. Gwydyon, a large "
            "man in his fifties gone to fat, is both librarian and autocrat, "
            "and lets the library slide; Branwen, in her twenties, is the only "
            "one acting against the decay, building up its resources and "
            "defences and hoping, without the authority, to recruit magi who "
            "will drag it out of its slump. She is a good liar.",
        ),
        what_matters=joined_lines(
            "Boon: Regio (Major) (an island regio whose top level has Magic 8)",
            "Boon: Difficult Access (one jetty, and mist off the path)",
            "Hook: House Covenant (House Ex Miscellanea)",
            "Hook: Seat of Power (the Primus and the Robes of Dusty Dawn)",
            "Hook: Alienable Land (Gwrhyr's kindred will claim the island when he dies)",
            "Hook: Crumbling (a decaying covenant)",
        ),
        secrets="The Robes of Dusty Dawn, the Columbae's gift to Pralix and "
        "the sign of the Primacy, lie mostly crumpled on the floor or over a "
        "chair: Ebroin finds them stifling. He is an orbus, and may still be "
        "loyal to the Primus of his former House (Houses of Hermes: "
        "Societates p. 103).",
    )
    _magi(records, covenant, CAD_GADU)


CAD_GADU: tuple[Magus, ...] = (
    (
        "ebroin",
        "Ebroin",
        EX_MISC,
        35,
        "Primus of House Ex Miscellanea since 1216, young and vibrant, elected when Immanola was declared in Final Twilight. He has restored the Council of Four, giving each member nominal charge of three Tribunals and keeping Stonehenge for himself, and called a census of the House. His Council is ill chosen, its members respecting neither one another nor him, and those who meet him often take him for a bumbling fool, wrongly (DE p. 22; Houses of Hermes: Societates pp. 102-103).",
    ),
    (
        "gharad",
        "Gharad",
        EX_MISC,
        130,
        "The second eldest maga of Cad Gadu, worn harder by time than Immanola: nearly blind, and left by repeated Twilights seeing things that are not there; her delusions never harm her but can endanger others. She seldom leaves her sanctum.",
    ),
    (
        "gwrhyr",
        "Gwrhyr",
        EX_MISC,
        140,
        "A blustering incompetent of the Columbae, the Welsh ward-makers, extremely old though he looks about fifty, with pepper-and-salt hair and beard and robes embroidered with mystic symbols. Not bright nor powerful, he demands \"proper respect\" but knows his limits; his best magic is Rego. By his age and standing he sits on Ebroin's Council of Four. He owns Cad Gadu's island in Welsh law (Houses of Hermes: Societates p. 112).",
    ),
    (
        "culhwch",
        "Culhwch",
        EX_MISC,
        60,
        "Gwrhyr's filius, not his blood, who suffered his master's insecurities and grew into a bully fond of taking it out on mundanes; more talented than his pater, he looks forward to surpassing him. Small and thin, simply dressed, smelling of burning, and skilled with Ignem.",
    ),
    (
        "findabair",
        "Findabair",
        EX_MISC,
        30,
        "A young maga, stunningly beautiful, long-haired and blue-eyed, who uses magic to eat and drink all she likes without losing her looks and dresses to seduce. She sees how fallen the covenant is and whines about it to anyone who will listen, too wrapped in her pleasures to act; the young men of the covenfolk hang about her.",
    ),
)


def _libellus(records: Records, tribunal: Tribunal) -> None:
    covenant = _covenant(
        records,
        tribunal,
        "libellus",
        "Libellus",
        founded=1210,
        season="Spring",
        summary=paragraphs(
            "The newest covenant in the Tribunal and one of the largest, an "
            "unknown quantity in its politics. A dozen stone buildings, most "
            "thatched, inside a plain stone wall with no crenellations: each "
            "magus has one as a sanctum, and the council chamber, library and "
            "Stephen Eruditus's sanctum are tiled. It lies in the same small "
            "region as Schola Pythagoranis, around Cambridge, but the book "
            "gives no site. Visitors are welcome but cannot stay long; Stephen "
            "meets them, the others having little to do with the outside world. "
            "Its covenfolk have served magi for years, but have seen few kinds.",
            "The free Jump Start Kit Promises, Promises tells more of it, and "
            "the pack does not use it.",
        ),
    )
    _magi(records, covenant, LIBELLUS)


LIBELLUS: tuple[Magus, ...] = (
    (
        "stephen_eruditus",
        "Stephen Eruditus",
        JERBITON,
        70,
        "Founder and leader of Libellus, about seventy though his longevity potion holds him at a look of thirty-five; trained in the Rhine Tribunal, a known taker of risks who has always come out ahead, and founding a covenant is the largest risk yet.",
    ),
    (
        "meles",
        "Meles",
        BJORNAER,
        30,
        "A young magus of Libellus, newly arrived in the Tribunal.",
    ),
    (
        "gregorius",
        "Gregorius",
        BONISAGUS,
        30,
        "A young magus of Libellus, newly arrived in the Tribunal.",
    ),
    (
        "lucidia",
        "Lucidia",
        FLAMBEAU,
        30,
        "A young maga of Libellus, newly arrived in the Tribunal.",
    ),
    (
        "jonaquil",
        "Jonaquil",
        MERINITA,
        30,
        "A young magus of Libellus, newly arrived in the Tribunal.",
    ),
    (
        "justin",
        "Justin",
        TREMERE,
        30,
        "A young magus of Libellus, newly arrived in the Tribunal.",
    ),
    (
        "fabricor",
        "Fabricor",
        VERDITIUS,
        30,
        "A young magus of Libellus, newly arrived in the Tribunal.",
    ),
)


def _nigrasaxa(records: Records, tribunal: Tribunal) -> None:
    covenant = _covenant(
        records,
        tribunal,
        "nigrasaxa",
        "Nigrasaxa",
        founded=1201,
        season="Spring",
        summary=paragraphs(
            "Two tall towers of shining black conjured rock, smooth but for "
            "their windows, joined by a low bridge for the covenfolk and a high "
            "one for the magi; only the first has a door. The public tower holds "
            "the guest rooms, largely unfurnished, and at its top the council "
            "chamber, where visitors meet the magi; the second holds the "
            "barracks and sancta, and visitors may not cross. It lies in the "
            "same small region as Schola Pythagoranis, but the book gives no "
            "site. Its founding was what revived the Tribunal's politics, and "
            "it is one of the larger covenants.",
            "William of Thanet, autocrat since the founding, is very good at "
            "his work but ageing, with no clear successor. The turb's captain, "
            "Eleanor Sworder, has led it five years and means to be a knight; "
            "an ugly scar on her left cheek breeds rumours.",
            "The free mini-saga Nigrasaxa tells more of it, and the pack does "
            "not use it.",
        ),
    )
    _magi(records, covenant, NIGRASAXA)


NIGRASAXA: tuple[Magus, ...] = (
    (
        "maximianus",
        "Maximianus",
        BONISAGUS,
        150,
        "Founder of Nigrasaxa, a widely respected master of Corpus whose many important texts are mostly in its library: a theoretical Bonisagus who these last twenty years has turned to the Order's politics. Julia of Voluntas asked him to help, and he came to Stonehenge and founded a covenant to break the cycle of invalid meetings, recruiting young magi to strengthen it. Ancient, and thought close to Final Twilight.",
    ),
    ("siffed", "Siffed", CRIAMON, 30, "A young magus of Nigrasaxa."),
    ("ariel", "Ariel", FLAMBEAU, 30, "A young magus of Nigrasaxa."),
    ("morlen", "Morlen", MERINITA, 30, "A young magus of Nigrasaxa."),
    ("caltis", "Caltis", TREMERE, 30, "A young magus of Nigrasaxa."),
    ("herrit", "Herrit", TYTALUS, 30, "A young magus of Nigrasaxa."),
    ("thamik", "Thamik", VERDITIUS, 30, "A young magus of Nigrasaxa."),
)


def _schola(records: Records, tribunal: Tribunal) -> None:
    covenant = _covenant(
        records,
        tribunal,
        "schola",
        "Schola Pythagoranis",
        founded=1182,
        season="Summer",
        place="schola_hall",
        aura=3,
        realm="Divine",
        summary=paragraphs(
            "A Jerbiton covenant scattered through Cambridge, whose university "
            "it largely made: its magi drew scholars there when Oxford's "
            "dispersed in 1209 and kept them after 1215. Its magi are scholars "
            "first and magi second, and stay out of the Tribunal's politics; "
            "scholars among the covenfolk are the magi's peers in its "
            "administration. It admits only magi and apprentices with the "
            "Gentle Gift, who can live among mundanes. Archmage Milo of "
            "Bonisagus lived here while preparing his contest, and left for "
            "Durenmar after winning.",
            "Visitors are lodged at its expense in the town's inns, those with "
            "a normal or Blatant Gift encouraged to be brief; the whole council "
            "meets only at the end of a season. It has few grogs, who would "
            "cause more trouble than they solved in a town. Its scholars come "
            "and go with the university, but two have stayed: Amabel the "
            "Learned and Richard Rufus the Deacon.",
        ),
        what_matters=joined_lines(
            "Boon: Literate Covenfolk (its scholars)",
            "Hook: Urban (Minor) (scattered through Cambridge)",
            "Hook: Mundane Politics (Major) (deep in mundane affairs, perhaps beyond the Code)",
            "Hook: Contested Resource (vis, against Libellus and Nigrasaxa)",
        ),
    )
    _magi(records, covenant, SCHOLA)


SCHOLA: tuple[Magus, ...] = (
    (
        "edward_of_milton",
        "Edward of Milton",
        JERBITON,
        110,
        "The covenant's warden and its eldest magus, a great teacher who loves to lecture and dispute, weak for his age since he studies mundane learning too. He looks in his late fifties and is vigorous with an eager student. He has trained five apprentices, an unheard-of number. He dresses as a cleric and is in minor orders as an exorcist; his magic is chiefly Mentem, so he is very good at it.",
    ),
    (
        "astrolabe",
        "Astrolabe",
        JERBITON,
        95,
        "Probably the most brilliant magus in the Tribunal, perhaps the Order, who would be an archmage if he gave himself to magic; his passion is natural philosophy, and he has begun applying it to magic theory, which he says rests on shoddy physics. Edward's first apprentice, now old, he looks in his late thirties and is usually unkempt, but dresses well for company. He works closely with Amabel the Learned.",
    ),
    (
        "lumen",
        "Lumen",
        JERBITON,
        32,
        "A young maga and obsessive bibliophile who keeps the library and wants every text she can get, classical authors and the Order's early magi above all, copying them herself or trading more useful books for them. She searches monasteries' libraries wearing a ring that makes her look a man, and carries it off well. Homely, short and gangly, practically dressed.",
    ),
    (
        "fredegisa",
        "Fredegisa",
        GUERNICUS,
        32,
        "A quaesitor and reforming idealist, a brilliant young student of civil, canon, common and Hermetic law, who devises new structures of Hermetic law and dreams of an age of justice for all magi. Smart, severe and attractive, she makes a good impression until her talk turns to her reforms.",
    ),
)


def _semitae(records: Records, tribunal: Tribunal) -> None:
    covenant = _covenant(
        records,
        tribunal,
        "semitae",
        "Semitae",
        founded=None,
        season="Autumn",
        summary=paragraphs(
            "The wandering covenant: about six wagons, three of them large and "
            "of iron so that they can hold laboratories, enchanted to be lighter "
            "and to firm the ground under them, drawn by six horses each, the "
            "wooden ones by four. It camps each night with guards, keeps away "
            "from towns and other covenants, and has never stayed anywhere "
            "longer than four nights, following a route Gerfallon maps that no "
            "one else can follow: it once circled London for two years at "
            "fifteen miles. The Redcaps fix the next meeting place each visit; "
            "the only ways to find it are to ride with one or to arrange a "
            "meeting. It may be almost as old as the Tribunal; its first sure "
            "record is 1151.",
            "Travellers may ride along under its guards, and visitors bring "
            "their own food and shelter. It breeds horses unafraid of magi, "
            "traded for books or vis, a line no one else can make breed true. "
            "Its magi work by night and sleep by day in the moving wagons, "
            "except when studying books. Its covenfolk are vagrants who join "
            "for a while, wholly loyal while they stay, perhaps by magic that "
            "Gerfallon lifts when they go, and leave on good terms.",
        ),
        what_matters=joined_lines(
            "Hook: Constantly Mobile (a train of wagons)",
            "Hook: Itinerants (its vagrant covenfolk)",
        ),
    )
    _magi(records, covenant, SEMITAE)


SEMITAE: tuple[Magus, ...] = (
    (
        "gerfallon",
        "Gerfallon",
        CRIAMON,
        130,
        "Leader of Semitae since its first record in 1151, unaged since, of no fixed age or sex: tattooed all over, the hair shaved for more room, under a deep hood and long sleeves; his appearance may change in mid-conversation, or hold for a whole meeting. He will not speak of his past or purpose, which, he says, no one can understand who has not glimpsed the Enigma. Some forty years ago magi of Cad Gadu found him etching designs into a Snowdonian mountainside by magic; months later they were finished, a map of no one knows what.",
    ),
    (
        "vanasalus",
        "Vanasalus",
        CRIAMON,
        30,
        "A young maga with no tattoos on face or hands, dressed as a noblewoman in clothes embroidered with mystic symbols, good-looking and always friendly. She believes magic reflects the heart, so that malice brings vicious Twilights and good deeds good ones, and means to live magic, following Gerfallon about the country, until she understands the Enigma.",
    ),
    (
        "junius",
        "Junius",
        VERDITIUS,
        100,
        "An old magus at the height of his powers, dressed as a craftsman, clean-shaven, face and hands spotted with tiny burn scars; he looks puny, and his enchanted tools make his smithing surprising. He builds the covenant's wagons, but spends most of his time on a secret project he will not speak of. The Tribunal and his House are curious.",
    ),
    (
        "edward_the_white",
        "Edward the White",
        JERBITON,
        60,
        "A member of Semitae in name, gone to explore distant lands with his sigil, so the covenant has not his vote; no one expects to see him again. The Fourth Edition's The Mythic Seas tells more.",
    ),
)


def _ungulus(records: Records, tribunal: Tribunal) -> None:
    covenant = _covenant(
        records,
        tribunal,
        "ungulus",
        "Ungulus",
        founded=984,
        season="Winter",
        place="ungulus_tower",
        aura=5,
        summary=paragraphs(
            "The classic winter covenant, living on past glories and full of "
            "mad magi. Founded by House Flambeau in 984, it was for two "
            "centuries home to a great line of Verditius magi, until a dragon "
            "killed the last young one, Parsirus, and the old master died "
            "alone. Most of the Tribunal expects it to fall soon, and its "
            "treasures to bring on a feeding frenzy. William Fireheart of "
            "Flambeau, its most infamous member, made much trouble in northern "
            "France, was fined in Normandy in 1194, and lost a Wizard's War to a "
            "magus of Fudarus this year, ending its Flambeau line.",
            "Inside it is packed with wealth, magical and mundane: guests are "
            "kept to rooms of gilded furniture, rich tapestries and magical "
            "light and heat, with more devices in each guest bedroom than most "
            "covenants own. The magi may take days to answer a guest, and those "
            "who wander meet the magical defences. Its servants keep countless "
            "rituals before doors and stairs, some disarming locks and traps, "
            "some invented, and no one dares find out which. Much of the work is "
            "done by magical constructs, brooms, knives, pans and warning bells, "
            "and by invisible bound spirits who obey anyone in the covenant; no "
            "one alive admits to knowing who bound them, and the Quaesitores "
            "found no diabolism. Its human covenfolk, all born there, are a "
            "little strange.",
        ),
        what_matters=joined_lines(
            "Enchantments: more devices than any other covenant of the Tribunal",
            "Boon: Wealth (Major) (the Verditius line's treasures)",
            "Boon: Inhuman Residents (constructs and bound spirits)",
            "Hook: Distorted Covenfolk (inbred in a strong aura)",
            "Hook: Monster (Major) (the dragon that killed Parsirus)",
            "Hook: Rival (Voluntas, encroaching on its lands)",
        ),
    )
    _magi(records, covenant, UNGULUS)


UNGULUS: tuple[Magus, ...] = (
    (
        "flavius",
        "Flavius",
        EX_MISC,
        100,
        "Ungulus's leader, trained there in its glory, who remembers its Verditius magi. He knows it is falling apart and cannot abandon it nor save it, and means to hold on until the others die or pass into Twilight and then rebuild with magi who are not fresh from apprenticeship; he is already courting the Tribunal's younger magi. Long a frequent, frustrated attender of meetings, often the only one not of Blackthorn, a passable politician sidelined in the revival. He looks late middle-aged, stout, balding and brown-bearded, in magnificent robes with powerful devices, to remind people of what Ungulus owns.",
    ),
    (
        "aquila",
        "Aquila",
        BJORNAER,
        150,
        "An ancient maga who spends most of her time as an eagle on the Lake District's thermals and seldom attends council; Flavius holds her sigil for good. She will likely pass into Final Twilight soon, staying in her heartbeast, and no one knows how the covenant would tell, or whether it already has.",
    ),
    (
        "sinead",
        "Sinead",
        EX_MISC,
        140,
        "An ancient maga who loved Parsirus and burns to avenge him on the dragon: anyone who wants something of Ungulus, membership included, she asks to kill it. She has tried twice herself and barely lived; the second time she fell into Twilight, and now a magical force pushes her away from her enemy. She looks an old woman in rich, worn robes, her magic bent on fighting magical beasts.",
    ),
    (
        "viator",
        "Viator",
        MERCERE,
        95,
        "The only Gifted Redcap in the Tribunal, retired to Ungulus for the resources to make a way for covenants to talk by magic without weakening their defences against one another, and fiercely against new members until it is done. Weather-beaten and nearly bald, he dresses opulently to meet people, if not as richly as Ungulus could.",
    ),
    (
        "espera",
        "Espera",
        MERINITA,
        70,
        "Offended a faerie lord long ago, and has lived to survive him since: she never leaves the Aegis, presses for it to be strengthened, and will let no one join lest they be faeries seeking a place in its ritual. She wears enchanted iron against faeries and often changes her looks by Muto Corpus to confuse her enemy.",
    ),
)


def _voluntas(records: Records, tribunal: Tribunal) -> None:
    covenant = _covenant(
        records,
        tribunal,
        "voluntas",
        "Voluntas",
        founded=1083,
        season="Summer",
        aura=3,
        summary=paragraphs(
            "One of the most vigorous covenants of the Tribunal and the heart of "
            "the opposition to Blackthorn, nearly since its founding by Norman "
            "magi in 1083; its long summer may be sliding into autumn now that "
            "Blackthorn's hold is broken. A large stone manor house of three "
            "wings closed by a wall with a cart gate, its rear corners held by "
            "two square towers for the sancta; the council chamber and library "
            "are in the back wing. The village of Wilton, a quarter hour's walk "
            "off, is part of it.",
            "Every magus swears on joining not to let the Tribunal suffer "
            "tyrannical rule, once plainly aimed at Blackthorn; the Quaesitores "
            "have reminded its magi that the Oath forbids meddling in the "
            "Tribunal's mundane affairs. Its library is one of the best in the "
            "Tribunal and the best open to others: study is traded for texts or "
            "vis, generously, as a way of making friends, but never to "
            "Blackthorn, and copying costs a book as good as the one copied. It "
            "runs its lands as a manor, and its neighbours think it one: "
            "Ethelwald, seneschal and autocrat, plays the lord and has avoided "
            "knighthood to avoid service; his son Edward is set on being a "
            "knight, and the magi doubt he will make a seneschal.",
            "Founded by Normans, it is hostile to Horsingas, a Saxon covenant of "
            "the Loch Leglean Tribunal, a grudge from the Conquest that has not "
            "come to blows for decades.",
        ),
        what_matters=joined_lines(
            "Boon: Exceptional Book (its library, lent by negotiation)",
            "Boon: Strong Community (Wilton)",
            "Hook: Rival (Blackthorn)",
            "Hook: Hermetic Politics (its oath against tyranny in the Tribunal)",
        ),
    )
    _magi(records, covenant, VOLUNTAS)


VOLUNTAS: tuple[Magus, ...] = (
    (
        "julia",
        "Julia",
        JERBITON,
        90,
        "Voluntas's leader in all but name, who decides its dealings with the world. Tall, long black hair, pale skin and a fine low voice, in deep blue robes embroidered with silver; a mature maga of Corpus and Mentem. She came to Stonehenge in the civil war to study its shifting alliances, turned to the Order's politics as Henry II brought peace, and spent years persuading magi to stand against Blackthorn, staying away from meetings so that it could force nothing through; that led to the fiasco of 1194. She wrote to friends outside the Tribunal, Maximianus among them, and the quorate meeting of 1201 was her masterstroke. Her try to move the meeting from Blackthorn was out-manoeuvred, and she is still all but obsessed with weakening it.",
    ),
    (
        "corvus",
        "Corvus",
        BJORNAER,
        60,
        "A mature magus with a raven heartbeast and a gift for Intellego, who always seems to know things before he is told, so that he is suspected of scrying on the Order; nothing is proved, and he says it is often an act. Black-haired and dark-eyed, he stares, and rarely troubles to dress after changing back; when dressed, he wears black.",
    ),
    (
        "kirist",
        "Kirist",
        FLAMBEAU,
        30,
        "A young Flambeau in red robes with a fiery temper and Ignem magic, but committed to the good of the whole Order and aware that burning people is not always it: he argues for conciliation when he thinks it right, unless someone angers him.",
    ),
    (
        "phessallia",
        "Phessallia",
        MERINITA,
        100,
        "Disliked by most magi of the Tribunal: close to the faeries of winter and as cold to everyone, often away in the north, studying, she says, the fay of the frozen lands, with faerie items of the kind only given as gifts. She always wears white, her skin covered in a fine net of scars; an old maga thought skilled in Perdo.",
    ),
    (
        "desiderius",
        "Desiderius",
        VERDITIUS,
        100,
        "A necromancer in plain brown robes trailing the smell of rotting flesh, who long cared nothing for the living but lately has come out of his shell and tries, without the skill, to be sociable; people are too frightened to be rude to him.",
    ),
)


# -- the Redcaps and natural magicians --

REDCAPS: tuple[tuple[str, str, int, str], ...] = (
    (
        "jocelin",
        "Jocelin",
        28,
        "An unGifted Redcap in his late twenties, brown-haired and green-eyed, fond of new covenants, often the only Redcap one sees for years; he rides his horses a little hard. He has a ring of magic resistance and an enchanted shield.",
    ),
    (
        "perceval",
        "Perceval",
        48,
        "An unGifted Redcap in his late forties, thinking of retiring, tall, thin and balding, who never takes off his unenchanted red cap. His wife Lucy and their children live at Mercer House; Guy is ten, and Lucy thinks two-year-old Maud has the Gift. He helps any covenant in a crisis, but thinks people should manage daily life themselves. A brooch makes him and his horse invisible.",
    ),
    (
        "great_william",
        "Great William",
        35,
        "An unGifted Redcap of giants' blood, just under eight feet, broad, with long blond hair and beard, in his mid thirties; quick-minded, widely read and keen on magic theory. He has boots that make him walk faster and a big axe enchanted for accuracy, as he is no great fighter.",
    ),
    (
        "little_william",
        "Little William",
        38,
        "An unGifted Redcap, little only beside Great William: well over six feet and more solidly built, in his late thirties. He got a longevity potion from one of the Tribunal's magi and will not say whom or why. The only Redcap who wears armour as a habit, enchanted mail made lighter, and a skilled, proud fighter with sword and shield.",
    ),
    (
        "edgar",
        "Edgar",
        22,
        "The newest Redcap, in his early twenties, good-looking, light brown hair and grey eyes, with a way with women; he has no magical items yet.",
    ),
)


def _redcaps(records: Records) -> None:
    for key, name, age, summary in REDCAPS:
        records.magi[key] = records.b.magus(
            name,
            covenant=None,
            house=MERCERE,
            age=age,
            summary=paragraphs(
                summary,
                "Like each of the Tribunal's Redcaps, he has a device that "
                "brings him and his horse back to Mercer House from anywhere "
                "in the Tribunal, once a day.",
            ),
            type="companion",
        )


NATURAL_MAGICIANS: tuple[tuple[str, str, str | None, int | None, str], ...] = (
    (
        "amabel",
        "Amabel the Learned",
        "schola",
        None,
        "A natural magician among Schola Pythagoranis's scholars, nearly as brilliant as Astrolabe, with whom she works closely; perhaps as powerful as most of its magi, having studied her magic with greater focus. Magi who know her treat her as one of the Order, and many would be surprised to learn she has never joined.",
    ),
    (
        "richard_rufus",
        "Richard Rufus the Deacon",
        "schola",
        None,
        "A theologian among Schola Pythagoranis's scholars, friendly with the magi and sure of their good intentions, who writes tracts justifying magic used for virtuous ends; they bring him trouble with the Church, though he has not been charged with heresy, and some highly placed churchmen are said to find them convincing and to employ natural magicians.",
    ),
    (
        "grosseteste",
        "Robert Grosseteste",
        None,
        50,
        "Master Robert Grosseteste, born about 1170, an official of Hugh Foliot, bishop of Hereford: a deacon with no benefice, and an unGifted natural magician learned at Schola Pythagoranis, well disposed to magi.",
    ),
    (
        "berechiah",
        "Berechiah ben Natronai haNakdan",
        None,
        58,
        "A Jewish natural magician of Oxford, born 1162, who may approach the Order.",
    ),
)


def _natural_magicians(records: Records) -> None:
    for key, name, covenant_key, age, summary in NATURAL_MAGICIANS:
        records.magi[key] = records.b.magus(
            name,
            covenant=records.covenants.get(covenant_key) if covenant_key else None,
            house="",
            age=age,
            summary=summary,
            type="companion",
        )


# -- the ruins --

RUINS: tuple[tuple[str, str, str, str], ...] = (
    (
        "sursum",
        "The Ruins of Sursum",
        "england",
        "The site in north Cornwall of Sursum (875-931), where Tytalus diabolism was found and King Athelstan destroyed the covenant.",
    ),
    (
        "stellasper",
        "The Ruins of Stellasper",
        "england",
        "The site on the Isles of Scilly of Stellasper (1025-1163), a Criamon covenant destroyed in a storm.",
    ),
    (
        "castrum_antiquum",
        "Castrum Antiquum",
        "england",
        "The Roman fort on Hadrian's Wall that held the covenant Castrum Antiquum (852-1030 or 1031), which vanished without trace, and its farmer magus Agricola of Tytalus with it.",
    ),
    (
        "magnantrum",
        "The Cave of Magnantrum",
        "england",
        "The cave under Salisbury Plain where Magnantrum (1111-1187) disintegrated.",
    ),
    (
        "nameless",
        "The Nameless Covenant",
        "wales",
        "The razed site on Anglesey of the Diedne covenant (817-1011) whose name is struck from the records.",
    ),
)


def _ruins(records: Records) -> None:
    for key, name, region, summary in RUINS:
        _place(
            records, key, name, region, ruined=True, summary=summary, **KNOWN_TRIBUNAL
        )
