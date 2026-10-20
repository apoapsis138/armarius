"""The covenants of the Eastern Marches and Bohemia (Guardians of the
Forests, chapters 9 and 10), in paraphrase: Heorot on Zealand, Crintera
on Rügen (the domus magna of House Bjornaer), Irencillia in the Bohemian
Forest (the domus magna of House Merinita) and Roznov in Moravia, with
their magi, their notable covenfolk and what is known of their
libraries. The defunct covenants Rethra and Sirmium get no record of
their own; the live covenants' summaries mention them where the book
connects them."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..builder import paragraphs, secrets

if TYPE_CHECKING:
    from ...models import Tribunal
    from . import Rhine


def _lines(*lines: str) -> str:
    """The hooks or secrets, one a line."""
    return "\n".join(lines)


def build(rhine: Rhine) -> None:
    tribunal = rhine.tribunal
    assert tribunal is not None
    _heorot(rhine, tribunal)
    _crintera(rhine, tribunal)
    _irencillia(rhine, tribunal)
    _roznov(rhine, tribunal)


# -- Heorot --


def _heorot(rhine: Rhine, tribunal: Tribunal) -> None:
    b = rhine.b
    heorot = b.covenant(
        "Heorot",
        tribunal=tribunal,
        founded=1215,
        place=rhine.places.get("heorot_site"),
        season="Spring",
        summary=_heorot_summary(),
        what_matters=_lines(
            "Membership: not yet a member of the Rhine Tribunal; applies at the "
            "Tribunal of 1221, and the Novgorod Tribunal, whose territory Zealand "
            "nominally is, has not been told",
            "Border dispute: many Rhine magi enjoy the thought of taking ground "
            "from Novgorod, and the Tribunal would like to push its claim east",
            "Opposition: Crintera, close by on Rügen, fears a rival "
            "for the region's vis sources and objects to the admission",
            "Support: Oculus Septentrionalis sponsors the covenant; Waddenzee "
            "does not object, since Heorot will bring it more victims and "
            "serves the Ash Gild's chief interest",
            "Purpose: to learn about the Order of Odin, the aim Oculus "
            "Septentrionalis once held, and this time with the skills to pursue it",
            "Trolls: the kin of Grendel still haunt Zealand's bogs and attack the "
            "covenant; Signum Irruptus's study of them has already cost fourteen "
            "grogs and his own left arm",
            "Vis: no sources recorded",
            "Mundane relations: not recorded; Zealand is Danish, under King "
            "Valdemar II",
        ),
        notes=secrets(
            "",
            "Oculus Septentrionalis has very likely struck some private bargain "
            "with Heorot as the price of its sponsorship.",
        ),
    )
    rhine.covenants["heorot"] = heorot

    rhine.magi["signum_irruptus"] = b.magus(
        "Signum Irruptus",
        covenant=heorot,
        house="house_criamon",
        age=53,
        summary=paragraphs(
            "Master of House Criamon and leader of Heorot, whose magi serve the "
            "Ash Gild's chief interest.",
            "He is consumed by the trolls of Zealand, which he holds to be the "
            "degenerate descendants of old gods, and his study of them has cost "
            "the covenant fourteen grogs and him his left arm. He carries on "
            "regardless.",
        ),
        traits={"Brave": 3, "Obsessed": 3, "Mindful of Danger": -2},
    )
    rhine.magi["theoderich"] = b.magus(
        "Theoderich of Augsburg",
        covenant=heorot,
        house="house_jerbiton",
        age=37,
        summary=paragraphs(
            "Journeyman of House Jerbiton, formerly of Oculus Septentrionalis, "
            "and Heorot's historian.",
            "A necromancer by method, he raises the ghosts of the dead and "
            "questions them about the past. It frustrates him that he has not "
            "yet found the remains of Hrothgar or of Beowulf, on whose ground "
            "the covenant is said to stand.",
        ),
        traits={"Morbid": 3, "Inquisitive": 2, "Laconic": 1},
    )
    rhine.magi["pancrestis"] = b.magus(
        "Pancrestis filius Occultes",
        covenant=heorot,
        house="house_bonisagus",
        age=28,
        summary=paragraphs(
            "Journeyman of House Bonisagus at Heorot, who means to meet a Norse "
            "wizard and learn that magic for the Order.",
            "His parens Occultes is famous and his mentor, the Archmage "
            "Philippus Niger of Durenmar, has impressed on him how urgently the "
            "Order needs those secrets revealed. Yet a deep dread of the "
            "wilderness has so far kept him from setting foot in pagan "
            "Scandinavia.",
        ),
        traits={"Ambitious": 3, "Fearful of Wilderness": 2, "Decisive": -2},
    )


def _heorot_summary() -> str:
    return paragraphs(
        "A newly founded covenant on the Danish island of Zealand, raised on "
        "the site of the hall of Hrothgar, the Danish king of legend whom "
        "Beowulf rid of Grendel. It is not yet a member of the Rhine Tribunal "
        "and hopes to be admitted at the Tribunal of 1221.",
        "Zealand is by tradition Novgorod territory, but no covenant of the "
        "Order has ever lasted long enough in the Norse lands to attend a "
        "Tribunal, the Order of Odin being thought too great a danger, so "
        "whose ground it is remains a grey area. All Heorot's magi come from "
        "the Rhine, and their declared purpose is the one Oculus "
        "Septentrionalis was founded for and never pursued: to learn about "
        "the Order of Odin. Unlike that covenant, they have the skills for it.",
        "Oculus Septentrionalis sponsors the application; Crintera, close by "
        "on Rügen, opposes it. Meanwhile the kin of Grendel, trolls of the "
        "island's bogs, harass the covenant.",
    )


# -- Crintera --


def _crintera(rhine: Rhine, tribunal: Tribunal) -> None:
    b = rhine.b
    crintera = b.covenant(
        "Crintera",
        tribunal=tribunal,
        founded=773,
        place=rhine.places.get("crintera_site"),
        season="Winter",
        summary=paragraphs(
            "The domus magna of House Bjornaer, deep in the Stubnitz Forest on "
            "the Jasmund peninsula of Rügen, inside a Magic regio of four levels "
            "whose auras run 1, 3, 5 and 8. Its only members are the six Elders "
            "of the Bjornaer council, who govern the House from here. It was "
            "founded by the followers of Bjornaer in the Order's first days and "
            "has stood ever since.",
            "Once a quiet and powerful force in the Tribunal, Crintera has been "
            "in turmoil since the Danish conquest of Rügen in 1168 and has spent "
            "the fifty years since in Winter, as new churches and a Cistercian "
            "monastery push the Dominion towards it and a Christian island "
            "yields fewer recruits for the turb. The council is divided between "
            "Harmonists, who would live alongside mundanes who leave the wild "
            "alone, and Wilderists, who would defend the wilderness against all "
            "men.",
            "Religion of every kind is forbidden inside the regio in honour of "
            "the Animal Powers, who held the forest before the Bjornaer came; "
            "it is among the covenant's oldest laws. Every twelve years the whole "
            "House meets here for the Gathering of Twelve Years, which the "
            "islanders call the Devil's Year.",
            "Crossing each boundary of the regio works a Corpus effect that "
            "draws the crosser's heartbeast forward, a personality trait at the "
            "first and small bodily changes at the others, so that someone who "
            "has crossed all four looks a quarter or a third animal. The Parma "
            "usually resists this, but resisting is thought rude; Bjornaer can "
            "shrug the changes off with their Heartbeast. Visitors reach it by "
            "the Watching Path, the one route through Stubnitz, marked at its "
            "start by two mossy, crumbling stones in a glade near the forest's "
            "edge and known to Redcaps and Bjornaer; covenfolk and animal allies "
            "watch everyone who walks it.",
            "The covenant of Rethra in Pomerania, once a sister community of "
            "Slavic magus-priests, fell silent and was declared abolished by the "
            "Tribunal of 1207, leaving Crintera the Order's only presence in the "
            "Marches.",
        ),
        what_matters=_lines(
            "Factions: Harmonists against Wilderists on the council, with "
            "Urgen's Wilderists gaining ground as the occupation drags on; the "
            "next Gathering, in 1227, is expected to be explosive",
            "Heorot: Crintera opposes its admission in 1221, fearing competition "
            "for vis near Rügen",
            "Oculus Septentrionalis: a feud since 1179, when Urgen accused them "
            "of helping the Danish invasion and slew their leader in Wizard "
            "War; lately the guest Caprea blinded the familiar of their peace "
            "envoy Carolus by accident, and relations are worse than ever",
            "The Danes: King Valdemar II's occupation, the churches of Bergen "
            "and Altenkirchen, a Cistercian monastery, monks farming Mönchgut "
            "and a church planned at Sagard, five miles away; the turb shrinks "
            "as recruits grow scarce",
            "Vis: Creo vis every year from Zora, priestess of Hertha, in return "
            "for protection of her priesthood and a promise that no victim is "
            "taken from Crintera's covenfolk; other sources not recorded, "
            "though the invasion is said to have damaged them while leaving "
            "them largely intact",
            "The Baltic thaw: each early spring Falke casts Appease the Queen "
            "of Winter at Arkona, where Svantovit's lingering presence gives "
            "the ritual a bonus, to break the sea ice and reopen shipping",
            "Faerie trod: the volkhvy of the Forest Brothers alone can open the "
            "gate in the Ziegensteine barrow, and often let Bjornaer use it; it "
            "leads one way to Pripet Major in the Novgorod Tribunal",
            "Pagan allies: friendly with the volkhvy of the Forest Brothers and "
            "the priestesses of Hertha; the Svantovit priests of Arkona helped "
            "Falke learn her ritual",
            "Mundane relations: hostile or wary towards the Danish crown and "
            "the island's churches; islanders shun Stubnitz and tell of animal "
            "attacks, shadow-monsters and witches, which suits the covenant",
            "The Gathering of Twelve Years: all Bjornaer come every twelve "
            "years (last 1203, next 1227), fifty to a hundred magi, for lineage "
            "rites, remembrance of the dead, most Mystery initiations under the "
            "Swan Elder, Ardea's re-enactments of old legends, visions of the "
            "Animal Powers and House politics; nothing is confirmed or denied "
            "to outsiders",
            "The council: Wolf (the Primus), Bear (Senior Elder, always a bear "
            "heartbeast, casting vote), Horse (keeps track of all Bjornaer), "
            "Stag (protector), Eagle (watches the Order), Swan (leads rituals, "
            "long held by a line of heron-heartbeast seers); a bear Primus "
            "merges Wolf and Bear and a Seat of the Fox fills the sixth place",
            "Succession: a dead or Twilit Elder waits for the next Gathering, "
            "when the rest choose by an ancient divination (once a Great Beast "
            "pointed out the heir); the whole House elects the Primus from the "
            "council's candidates",
            "Guests: visiting Bjornaer may raise a temporary sanctum on the "
            "third regio level and stay for years",
        ),
        notes=secrets(
            "",
            _lines(
                "Urgen is widely suspected of driving mundanes from the wild "
                "with covert animal attacks, and is stepping them up now that "
                "the Primacy no longer restrains him.",
                "Stubnitz only looks untouched: the forest hides many "
                "settlements of covenfolk, concealed by magic.",
                "The fetishes of the Animal Powers on the fourth level (a "
                "wooden squirrel on a stump, a stone otter among cattails, a "
                "rush-woven snake in a hollow boulder, a clay wolf with shell "
                "teeth, stone birds in willow saplings hung with feathered "
                "thongs, and one for every other beast, only a few visible "
                "from any spot) are truly ancient and said to hold primordial "
                "nature spirits. Touching one's own brings a deep sense of "
                "connection; anyone who resisted the regio's changes, or "
                "nears another's fetish, feels compelled to leave it alone. "
                "Covenfolk leave offerings at the fetish of their heartbeast.",
                "Bjornaer the Founder was a Pomeranian shapeshifter-witch; the "
                "werewolves of Pomerania count her a traitor who sold their "
                "secrets to the Roman priests.",
            ),
        ),
    )
    rhine.covenants["crintera"] = crintera

    rhine.magi["urgen"] = b.magus(
        "Urgen",
        covenant=crintera,
        house="house_bjornaer",
        age=114,
        summary=paragraphs(
            "Archmagus of House Bjornaer, Senior Elder in the Seat of the Bear, "
            "leader of the Hawthorn Gild and Primus of the House from 1165 to "
            "1203, through the Danish invasion. His heartbeast is a bear.",
            "He is the most influential of the Wilderists, holding that the "
            "Order must check the swelling mundane population and that Bjornaer "
            "must enter Hermetic politics to do so. Twice in fifty years he has "
            "torn a powerful magus apart in Wizard War, and his age and his "
            "victories earn him respect; support for him grows the longer the "
            "occupation of Rügen lasts.",
        ),
        traits={"Quick-Tempered": 5, "Authoritarian": 4, "Peaceful": -4},
    )
    rhine.magi["falke"] = b.magus(
        "Falke",
        covenant=crintera,
        house="house_bjornaer",
        age=49,
        summary=paragraphs(
            "Master of House Bjornaer, Linden Gild trained, and its Prima in the "
            "Seat of the Wolf since 1203. Her heartbeast is a silver-grey falcon "
            "with white-banded wings; she looks about 45 and passed her Gauntlet "
            "at 23.",
            "Raised at Fengheld, she rose to prominence with an impassioned plea "
            "at the Tribunal of 1194 to let Crintera resist the Danes. She leans "
            "Harmonist without declaring it and governs by patience and "
            "seclusion, working to win back the trust of the Quaesitors and the "
            "Order. She has just become a Master and taken her first apprentice, "
            "and each spring casts the ritual at Arkona that thaws the Baltic.",
            "Her magic centres on bodies of water, Aquam above all, and a "
            "Twilight scar keeps her feet always wet, leaving a puddle wherever "
            "she stands still. She is small and lithe, plain but commanding, "
            "with silky uniform grey hair, simply dressed and always barefoot to "
            "show her talisman, a silver anklet patterned in watery crystal and "
            "amber. Not suited to play as a player character.",
        ),
        traits={"Committed to an Ideal": 3, "Cheerful": 2, "Humble": 1},
    )
    rhine.magi["jon_arnsson"] = b.magus(
        "Jon Arnsson",
        covenant=crintera,
        house="house_bjornaer",
        age=98,
        summary=paragraphs(
            "Master of House Bjornaer and protector of Crintera in the Seat of "
            "the Stag since the Gathering of 1167, a year before the invasion. "
            "His heartbeast is a lion.",
            "A devout Christian who regards Valdemar's Church-backed conquest as "
            "righteous, yet fiercely loyal to Crintera, he is a man of divided "
            "and conflicted loyalties whose theology any other Christian would "
            "call heresy. Gentle and hating violence, he accepts its necessity "
            "and, as protector, joins Wizard's Marches against Bjornaer when he "
            "can. The second eldest after Urgen, he is a fervent Harmonist.",
        ),
        traits={"Pious": 3},
    )
    rhine.magi["phyllia"] = b.magus(
        "Phyllia",
        covenant=crintera,
        house="house_bjornaer",
        age=58,
        summary=paragraphs(
            "Master of House Bjornaer in the Seat of the Eagle, who keeps the "
            "council informed about the Order. Her heartbeast is a polecat.",
            "She travels widely and has contacts across the Tribunal and "
            "beyond, but is a notorious gossip, quite unable to keep a secret. "
            "A Harmonist.",
        ),
        traits={"Curious": 3, "Restless": 1, "Discreet": -3},
    )
    rhine.magi["ardea"] = b.magus(
        "Ardea",
        covenant=crintera,
        house="house_bjornaer",
        age=83,
        summary=paragraphs(
            "Master of House Bjornaer and leader of its rituals in the Seat of "
            "the Swan. Her heartbeast is a heron.",
            "Quiet and contemplative, a famous seer and diviner with a hunger "
            "for magical knowledge worthy of a Bonisagus, she keeps her political "
            "opinions to herself because her word carries such weight, and sides "
            "with neither faction. She stages the re-enactments of old legends "
            "at the Gathering.",
        ),
        traits={"Neutral": 2, "Serene": 2, "Hungry for Knowledge": 1},
    )
    rhine.magi["istvan_padas"] = b.magus(
        "Istvan Padas",
        covenant=crintera,
        house="house_bjornaer",
        age=48,
        summary=paragraphs(
            "Master of House Bjornaer in the Seat of the Horse, which keeps "
            "track of Crintera's magi and of every Bjornaer. His heartbeast is a "
            "magnificent stallion.",
            "The youngest and most wilful Elder, a man of action, he descends "
            "from a line of horse-shaped Bjornaer taken into the House from the "
            "invading Magyars in the Order's early days. A Wilderist, strongly "
            "backed by his lover Zora, priestess of Hertha. His predecessor in "
            "the Seat died trying to climb the Königstuhl.",
        ),
        traits={"Hot-Headed": 3, "Brave": 2, "Subtle": -2},
    )
    rhine.magi["caprea"] = b.magus(
        "Caprea",
        covenant=crintera,
        house="house_bjornaer",
        age=None,
        summary=paragraphs(
            "Maga of House Bjornaer, at present a guest of Crintera; her rank "
            "and age are not recorded.",
            "She is using the covenant's library to finish a bestiary she means "
            "to present at the Tribunal of 1221. By accident she blinded the "
            "familiar of Carolus of Oculus Septentrionalis, who had come as a "
            "peace envoy, and so deepened the feud between the covenants.",
        ),
    )

    b.magus(
        "Dietrich",
        covenant=crintera,
        house="",
        age=None,
        type="grog",
        summary=paragraphs(
            "Leader of the Bear Clan, the biggest men of Crintera's turb, who "
            "fight with maces and bare hands.",
            "A huge man in a bearskin cape that carries the power of "
            "transformation; legend wrongly says it is the Founder's own skin. "
            "He has an uncanny knack for spotting shapechangers, which works in "
            "part even on Bjornaer magi.",
        ),
    )
    b.magus(
        "Janis",
        covenant=crintera,
        house="",
        age=None,
        type="companion",
        summary=paragraphs(
            "Volkhv of the Forest Brothers and leader of the Swan Clan, "
            "Crintera's crafters and companions with powers other than "
            "shapeshifting.",
            "He is the covenant's go-between with Rügen's pagans and is "
            "consulted on the island and its supernatural inhabitants, but may "
            "not practise his religion inside Crintera.",
        ),
    )

    b.book(
        crintera,
        "Crintera's library",
        "Other",
        description=(
            "The book gives no titles or numbers. Crintera has a library in "
            "use: the guest maga Caprea is drawing on it to finish a bestiary "
            "for the Tribunal of 1221."
        ),
    )
    b.book(
        crintera,
        "Appease the Queen of Winter",
        "Lab Text",
        art="Aquam",
        level=60,
        description=(
            "A laboratory text for the Muto Aquam ritual of the sixtieth level "
            "that thaws the Baltic each early spring by propitiating the Queen "
            "of Winter. Falke learned the ritual from it, with the help of the "
            "volkhvy of Arkona; cast at Arkona it gains a bonus of ten to the "
            "casting total, because the sun-god Svantovit opposes the Queen."
        ),
    )


# -- Irencillia --


def _irencillia(rhine: Rhine, tribunal: Tribunal) -> None:
    b = rhine.b
    irencillia = b.covenant(
        "Irencillia",
        tribunal=tribunal,
        founded=792,
        place=rhine.places.get("irencillia_site"),
        realm="Faerie",
        season="Autumn",
        unnamed_magi=3,
        summary=paragraphs(
            "The domus magna of House Merinita, hidden in faerie woodland where "
            "the northern Bohemian Forest meets the plain, among beech and oak "
            "full of fallow deer, boar, lynx and bears. Quendalon, the second "
            "Primus, built it after his return from Arcadia, when he turned the "
            "House towards the fae, so it dates from the late eighth or ninth "
            "century. The land about it is kept wild by the covenant's meddling.",
            "An Autumn covenant, now larger than ever as human encroachment on "
            "faerie lands drives Merinita magi home to it; three further magi "
            "beyond those named live here, left to the storyguide. It holds "
            "aloof from the politics of region and Tribunal alike, prizing its "
            "seclusion.",
            "Its Faerie aura is patchy: at least 1 everywhere within the "
            "boundary, up to 6 where the sancta stand, with odd high spots such "
            "as a covered walk to the kitchens at 4 along its length. Many of "
            "the stronger patches, most sancta among them, lie in fragmented "
            "regiones whose entrances bear symbols (a badger's head, a crescent "
            "moon) that outsiders cannot read. The theory is that all this is "
            "the wreckage of the vast magical war between Quendalon and Myanar.",
            "The covenant shows itself to each visitor as expectation shapes it: "
            "a castle of living wood with courtiers, a hamlet of foresters in "
            "green and brown, a wooded hill with a trilithon over a labyrinth, a "
            "gully of caves peopled by twisted folk; those who do not know it is "
            "there see open woodland and wander through unaware, avoided by its "
            "people. Every view shares an enclosing boundary (palisade, drystone "
            "wall or thorn hedge), a single gateway, and over it an inscription "
            "said to be Merinita's last words before she vanished in 785, to the "
            "effect that the spirits of old endure unchanged in the depths of "
            "rivers and the endless twilight of forests.",
            "The glamour is lived, not merely seen: materials, covenfolk's looks "
            "and even a plucked leaf differ from one observer to another, and "
            "anything carried out of the aura turns to dust and dry twigs at "
            "sunrise or sunset. No usable map can be drawn; only the sancta "
            "(each magus's firm notion of his own, as castle, town house, garden "
            "or barrow) and to a lesser degree the shared library, council "
            "chamber and dining hall reach a consensus. No magus's Magic "
            "Resistance has ever stopped the effect, and nobody knows whether it "
            "is a spell, a faerie power or something else. Every magus who stays "
            "more than a season gains a caricature, a faerie double.",
        ),
        what_matters=_lines(
            "House politics: Handri outmanoeuvred Vinaria and took the Primacy "
            "from her; she went into what is called Faerie Twilight and came "
            "back after seven years apparently unchanged",
            "The God of Truth: a dualist faith reverencing the wild and its "
            "faerie angels has sprung up in the villages near the forest over "
            "the last ten years, wherever the Prophet Iacob and his white crow "
            "are seen",
            "Handri's diplomacy: long private embassies into faerie lands, and "
            "rumours that he has met survivors of House Diedne",
            "Caricatures: every resident magus gains a faerie double (a Faerie "
            "Friend for the stay); a double can serve as an Arcane Connection, "
            "may be kidnapped to strike at its magus, or be sent to Tribunal in "
            "a busy magus's place",
            "The lost domus magna: Merinita was the last Roman priestess of "
            "Diana, drawn into the Order only by Trianoma's persuasion as her "
            "cult died under Charlemagne's Christianisation; Irencillia was "
            "never her home, and the House has forgotten where her temple stood "
            "or what it was called",
            "Maddenhofen Woods: the covenant closely guards the nearby woods "
            "where Tytalus vanished in 807 and a powerful faerie grants a "
            "Heart's Desire for a task never yet completed, yet seems to take "
            "no vis from them",
            "Two societies: human and fae live side by side; the Primus's "
            "caricature is always the monarch of the Faerie Court, at present "
            "Queen Rosmert, though whether one shapeshifting ruler or a new one "
            "with each Primus is unknown",
            "Gild: the Elder Gild, which Iacob leads",
            "Vis: no sources recorded",
            "Mundane relations: deliberately none; wanderers are shunned, and "
            "the only indirect tie is the God of Truth in the nearby villages",
        ),
        notes=secrets(
            "",
            _lines(
                "Irencillia was not Merinita's home; the true first domus "
                "magna, her temple of Diana, is lost and its name forgotten.",
                "A caricature's Might grows over time to a cap set by its "
                "magus's standing at Irencillia, in politics or in faerie "
                "understanding rather than raw power; a magus who takes on "
                "his caricature's manner grows hard to tell from it, and the "
                "two become Arcane Connections to each other.",
                "The Prophet Iacob of the God of Truth is Iacob filius "
                "Handri, carrying out the Primus's secret plan to found a "
                "religion in the name of the fae; the Quaesitors would be "
                "appalled.",
            ),
        ),
    )
    rhine.covenants["irencillia"] = irencillia

    rhine.magi["handri"] = b.magus(
        "Handri",
        covenant=irencillia,
        house="house_merinita",
        age=81,
        summary=secrets(
            paragraphs(
                "Master of House Merinita and its Primus, who shares his plans "
                "with only a few trusted advisers.",
                "Where his predecessor Vinaria talked politics with the other "
                "Primi, he gives himself to long private embassies into faerie "
                "lands, and is rumoured to have met survivors of House Diedne. "
                "Nobody admits to seeing him cast anything but the signature "
                "spell that earned him his Mastery; a magus for some sixty "
                "years, he trained Iacob and Beechleaf of Fengheld and seems "
                "never to have sought Archmage status. His caricature is "
                "Rosmert, the imperious Queen of Irencillia's fae.",
            ),
            "He conceived the scheme for a faerie religion on becoming Primus. "
            "He is secretly afraid of Vinaria and lets her do as she pleases.",
        ),
        traits={"Obsessively Secretive": 6, "Indecisive": 1, "Secure in Position": -2},
    )
    rhine.magi["ioannes_acer"] = b.magus(
        "Ioannes Acer",
        covenant=irencillia,
        house="house_merinita",
        age=23,
        summary=paragraphs(
            "Journeyman of House Merinita, Elder Gild trained, the youngest "
            "apprentice of the Archmaga Vinaria and only just past his "
            "Gauntlet.",
            "An idealist steeped in romantic chivalry that will serve him poorly "
            "beyond Irencillia, he was knighted by a Faerie Court and keeps a vow "
            "of chivalry; secular lords accept the knighthood so long as they do "
            "not ask after his liege. His magic runs to Herbam and Rego, flawless "
            "but short-lived, and he fights with greatsword and lance. A robust, "
            "golden-haired, sunburnt youth in mirror-bright ornate bronze scale, "
            "never a helm, bearing a green sycamore leaf on white, he rides and "
            "jousts from his caricature Kervus, a stag huge enough to carry him. "
            "A suitable player character.",
        ),
        traits={"Brave": 3, "Honorable": 3, "Deep Thinker": -2},
    )
    rhine.magi["vinaria"] = b.magus(
        "Vinaria",
        covenant=irencillia,
        house="house_merinita",
        age=97,
        summary=secrets(
            paragraphs(
                "Archmaga of House Merinita and its former Prima, who stepped "
                "down after Handri outmanoeuvred her.",
                "She is said to have entered Faerie Twilight and returned seven "
                "years later apparently unchanged. Politically formidable through "
                "long councils with the other Primi, whose contacts she uses "
                "skilfully, she is strongest in the raw elemental Arts and always "
                "dressed in beautiful glamour. Her old caricature, the faerie "
                "king, passed to Handri, and mysteriously she has acquired no new "
                "one since her return.",
            ),
            "Handri senses a new inner strength in her, fears her and avoids her "
            "entirely.",
        ),
        traits={"Enigmatic": 3, "Self-Assured": 3, "Hostile": -3},
    )
    rhine.magi["glesig"] = b.magus(
        "Glesig",
        covenant=irencillia,
        house="house_merinita",
        age=62,
        summary=paragraphs(
            "Master of House Merinita and the House's foremost expert on the "
            "fae beneath the earth, a Terram specialist.",
            "Big-boned and plain, her hair turned by Twilight into threads of "
            "shining copper. Her caricature Humnel, an immense troll, has become "
            "her faerie familiar; he is protective and hates to hear her "
            "insulted.",
        ),
        traits={"Impatient": 2, "Friendly": 1, "Tolerant of Fools": -2},
    )
    rhine.magi["iacob"] = b.magus(
        "Iacob filius Handri",
        covenant=irencillia,
        house="house_merinita",
        age=43,
        summary=secrets(
            paragraphs(
                "Master of House Merinita, leader of the Elder Gild and, after "
                "Vinaria, the covenant's most politically active magus.",
                "A Master of Mentem unusually young, he invents spells that plant "
                "thoughts and ideas in their targets. Tall, looking barely into "
                "his thirties, he charms with an almost hypnotic voice. His "
                "caricature Nestor, a white crow, travels with him.",
            ),
            "He runs Handri's secret project to found a religion in the fae's "
            "name: he is the Prophet Iacob of the God of Truth, known by his "
            "albino crow. He never shows magic to mundanes, and the Quaesitors "
            "would be deeply unhappy to learn of it.",
        ),
        traits={"Independent": 2, "Suspicious": 1, "Talkative": -2},
    )
    rhine.magi["gravis"] = b.magus(
        "Gravis",
        covenant=irencillia,
        house="house_bonisagus",
        age=33,
        summary=paragraphs(
            "Journeyman of House Bonisagus, come to Irencillia to pursue a "
            "lifelong fascination with the fae.",
            "Though his Faerie Lore outstrips many a Merinita's, he cannot grasp "
            "even the rudiments of Faerie Magic, which frustrates him without "
            "making him bitter; he keeps trying. Chubby and sunny, his caricature "
            "Danket is a grumpy, stick-thin, scowling dwarf.",
        ),
        traits={"Cheerful": 2, "Driven": 2, "Sensitive": 1},
    )
    rhine.magi["richenda_spinosa"] = b.magus(
        "Richenda Spinosa",
        covenant=irencillia,
        house="house_flambeau",
        age=28,
        summary=paragraphs(
            "Journeyman of House Flambeau, a Pole, and an atypical member of "
            "her House.",
            "As an apprentice she showed a gift for fire that her master "
            "Indulius of Fengheld never knew came from a secret faerie heritage, "
            "for she descends from Kupala, a faerie lord who guards the Fire "
            "Flower in the Slavic lands. His bungling, as she sees it, scarred "
            "her Gift so that fire magic now comes very hard, and her natural "
            "Herbam talent and faerie blood made her a laughing-stock in her "
            "House. Angry, with a bent for thorn spells, she has sworn vengeance "
            "on her master and is not yet reconciled to her fae side. Her "
            "caricature Jennis is a male version of herself, from whom she "
            "learns.",
        ),
        traits={"Bitter": 3, "Prickly": 2, "Fae": -2},
    )

    b.book(
        irencillia,
        "Irencillia's library",
        "Other",
        description=(
            "The book gives no titles or numbers. The library is one of the "
            "few communal spaces that every visitor sees much alike, and its "
            "faerie librarian summons books with a gesture."
        ),
    )


# -- Roznov --


def _roznov(rhine: Rhine, tribunal: Tribunal) -> None:
    b = rhine.b
    roznov = b.covenant(
        "Roznov",
        tribunal=tribunal,
        founded=1067,
        place=rhine.places.get("roznov_site"),
        season="Autumn",
        unnamed_magi=5,
        summary=paragraphs(
            "An Autumn covenant in a valley at the edge of the Carpathians on "
            "Mount Radhost, in the far east of Moravia on the Hungarian border, "
            "founded in 1067 by three Ex Miscellanea magi and admitted to the "
            "Rhine Tribunal in 1074. A Magic aura of 4 covers the whole valley, "
            "rising to 6 at the crude stone temple on the summit.",
            "It joins two strong and utterly different traditions. One half is "
            "the pagan priesthood of the old Slavic god Radegast, Ex Miscellanea "
            "magi in Roznov Castle; the other an arch-conservative stronghold of "
            "House Tremere in Roznov Fort. The two act independently, their "
            "political aims often coinciding, yet one half commonly hears of the "
            "other's schemes only from third parties. Seven magi live here in "
            "all: Igor Rastvan and his two former apprentices, the three Ex "
            "Miscellanea of the Castle; Severicus and two more Tremere, the "
            "three of the Fort; and a follower of Tytalus.",
            "Its allegiance looks split between the Rhine, whose Tribunals it "
            "attends, and the Tremere-run Transylvanian Tribunal, with which it "
            "is thought to keep regular contact, so most Rhine magi distrust it; "
            "even so it has grown into a significant political force in the "
            "Tribunal. Radegast's worship once centred on his Oracle at Rethra in "
            "Pomerania, a covenant of Slavic magus-priests that the Tribunal "
            "declared abolished in 1207, but Mount Radhost was always his sacred "
            "place.",
        ),
        what_matters=_lines(
            "Founding suspicion: Roznov could have joined Novgorod or "
            "Transylvania but took Durenmar's and Crintera's richer offer; two "
            "Transylvanian Tremere joined almost at once in 1074, and some Rhine "
            "magi think the whole affair a Tremere ploy for a foothold, with "
            "the Ex Miscellanea as dupes",
            "Vis: dozens of pawns gathered every summer solstice at the "
            "Radegast festival in the summit temple, and Corpus vis from blood",
            "The festival: if Severicus and his filii learned what really "
            "happens at the solstice they would be horrified, with charges of "
            "diabolism, a pre-emptive March or Wizard War to follow in both "
            "Tribunals; unless the Tremere already know, and keep silent for a "
            "very good hidden reason",
            "Kingdom of the Slavs: three young companions each believe "
            "themselves the rightful heir of a Slavic kingdom and dream of "
            "uniting their people against German dominance; the magi encourage "
            "all three to spur them on, and Igor has no favourite so long as "
            "the kingdom is Radegast's",
            "The slave trade: Ladislaus, a companion of the covenant, buys at "
            "the Prague slave market, where the Knights of the Sword sell their "
            "Pomeranian captives",
            "Sigils: Severicus holds his own, one of only two Rhine Tremere to "
            "do so (the other is Stentorius of Fengheld), and controls about "
            "two-fifths of the other Tremere sigils, his two filii's and "
            "Hygwald Veritas's of Waddenzee among them",
            "Gilds: every magus belongs to the Ash or the Oak Gild",
            "Mundane relations: the village below the Fort, whose folk guard "
            "the only trail up, and the Prague slave market; otherwise not "
            "recorded",
            "Covenfolk: about a score of servants and soldiers at the Castle and "
            "four times as many at the Fort, rotated continually; many are "
            "devotees of Radegast and many bought slaves, who work feverishly "
            "hoping a summons uphill means merit rather than expendability; "
            "some earn freedom and a place in the turb by a blood oath",
            "Transylvania: the Tremere of the Transylvanian Tribunal across the "
            "Hungarian border make their influence felt here",
        ),
        notes=secrets(
            "",
            _lines(
                "Every summer solstice the whole covenant and village "
                "celebrate Radegast at the summit temple with orgiastic "
                "drinking and debauchery, and a few celebrants, usually "
                "slaves, are quietly seized and sacrificed inside the temple, "
                "seen only by Igor's most loyal servants. It is never spoken "
                "of, though most covenfolk guess why people vanish each "
                "summer. The victims' blood yields Corpus vis and feeds the "
                "harvest of dozens of pawns. Some supernatural agency seems "
                "to keep the sacrifices secret.",
                "The Tremere of the Fort know nothing of the festival's true "
                "nature and, unusually for their House, neither discourage "
                "nor disapprove of the paganism; or, at the storyguide's "
                "choice, they know and hold their tongues for a hidden "
                "reason.",
                "Roznov Castle, a small twin-towered castle inside a curtain "
                "wall two-thirds of the way up Mount Radhost and visible only "
                "from its own valley, and Roznov Fort, the fort and village "
                "at the foot that command the single pass, are joined by "
                "tunnels through the mountain.",
                "Ladislaus uses Magic Sensitivity at the Prague market to pick "
                "out Gifted children among the slaves, who go to Coeris, the "
                "Tremere domus magna in Transylvania; the rest are traded or "
                "put to work at Roznov.",
            ),
        ),
    )
    rhine.covenants["roznov"] = roznov

    rhine.magi["igor_rastvan"] = b.magus(
        "Igor Rastvan",
        covenant=roznov,
        house="house_ex_miscellanea",
        age=101,
        summary=paragraphs(
            "Archmagus of House Ex Miscellanea, of the Ash or Oak Gild like all "
            "Roznov's magi, high priest of Radegast and leader of Roznov Castle "
            "and its covenfolk.",
            "Some eighty years past his Gauntlet and still hale, with black "
            "curly hair and a waist-length beard barely touched with grey, he "
            "always wears embroidered robes showing scenes of myth and his "
            "priestly rank. The filius of a founder and perhaps the only "
            "Archmage of his House, he draws on Slavic cursing traditions and is "
            "feared for killing from afar; many of his spells carry a "
            "non-Hermetic ritual element fed by the pagan ceremonies he leads, "
            "so that more worshippers mean more power. His ambition is dominion "
            "over all the Slavic lands united under Radegast, an obsession now "
            "so strong his filii fear Twilight has unhinged him.",
        ),
        traits={"Devoted to Radegast": 6, "Overconfident": 2, "Peaceful": -2},
    )
    rhine.magi["severicus"] = b.magus(
        "Severicus",
        covenant=roznov,
        house="house_tremere",
        age=77,
        summary=paragraphs(
            "Master of House Tremere, of the Ash or Oak Gild like all Roznov's "
            "magi, and leader of Roznov Fort.",
            "Very tall and thin, wholly bald with a neat greying beard, a noted "
            "master of Terram who detests change of every kind. He holds his own "
            "sigil, as only he and Stentorius of Fengheld do among the Rhine's "
            "Tremere, and controls about two-fifths of the others.",
        ),
        traits={"Unyielding": 3, "Obsessive": 2, "Sympathetic": -2},
    )

    b.magus(
        "Ladislaus",
        covenant=roznov,
        house="",
        age=None,
        type="companion",
        summary=secrets(
            paragraphs(
                "A trusted companion of Roznov and its buyer at the Prague slave "
                "market, where he passes for a shady-looking dealer.",
                "He has Magic Sensitivity.",
            ),
            "He uses it to pick out Gifted children among the slaves, who are "
            "sent to Coeris, the domus magna of House Tremere in the "
            "Transylvanian Tribunal; the other slaves he buys are traded or put "
            "to work by Roznov.",
        ),
    )
