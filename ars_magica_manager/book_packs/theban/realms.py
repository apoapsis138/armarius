"""The four realms of the Theban Tribunal, as of 1220, in paraphrase of
The Sundered Eagle chapters nine to twelve (the Magical, Faerie, Divine
and Infernal landscapes), with chapter four for the folk beliefs and
the Church: the sites those chapters describe that the region chapters
do not (the sibyls' homes, Akgah's battlefield, the monasteries of the
Greek saints); the Hermetic leagues and the titan factions; the hedge,
holy and infernal traditions and the cults; Kristophoros of Bonisagus
and Evantia of Moero's Garden; and the saints and relics, written into
the notes of the places that hold them.

The places the region parts own (Delphi, Samos, Mykonos, Mount Athos,
Hagia Sophia, the Venetian Quarter, the Studion, Patmos and the rest)
are looked up by name in `finish`, after every part has built; a relic
or saint whose place is missing goes into its region's place instead.
Creatures are the Bestiary's: Akgah, the vrykolakas, the smerdaki, the
sibyl and the stoicheion are named in their places' summaries only.
Keys: the sites are places["erythrae"], ["samian_sibyl"], ["dardania"],
["phrygian_sibyl"] and ["akgah_battlefield"]; the factions are in
world, by a short key (world["league_of_constantine"] and so on)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...places import PLACE
from ..builder import Builder, paragraphs, secrets
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Character, Neighbour
    from . import Theban

BONISAGUS = "house_bonisagus"
JERBITON = "house_jerbiton"

KNOWN_ORDER: dict[str, Any] = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL: dict[str, Any] = {"status": "Known", "known": "In the Tribunal"}
KNOWN_REGION: dict[str, Any] = {"status": "Known", "known": "In the region"}
KNOWN_LOCALLY: dict[str, Any] = {"status": "Known", "known": "Locally"}
RUMOURED: dict[str, Any] = {"status": "Rumoured", "known": "Locally"}

#: Each record whose place is another part's, with the names that place
#: may go by and the region to fall back on: settled in build when the
#: place is there already, else in finish.
_PENDING: list[tuple[Neighbour, tuple[str, ...], str]] = []


# ---------------------------------------------------------------- lookups


def _key(name: str) -> str:
    name = name.casefold().replace("’", "'").strip()
    return name.removeprefix("the ")


def _find(theban: Theban, *names: str, kinds: tuple[str, ...] = ()) -> Neighbour | None:
    """The record another part made under one of `names` (exactly, or
    a name that starts with it), the first name first."""
    records = [n for n in theban.b.saga.neighbours if not kinds or n.kind in kinds]
    for wanted in names:
        key = _key(wanted)
        for record in records:
            if _key(record.name) == key:
                return record
        for record in records:
            if _key(record.name).startswith(key):
                return record
    return None


def _settle(
    theban: Theban, record: Neighbour, names: tuple[str, ...], region: str
) -> None:
    """Put `record` in the first of `names` there is, else in `region`;
    try again in finish if neither exists yet."""
    found = _find(theban, *names, kinds=(PLACE,)) if names else None
    found = found or theban.places.get(region)
    if found is not None and found is not record:
        record.place_id, record.place_level = found.id, 0
    else:
        _PENDING.append((record, names, region))


def _add(
    theban: Theban,
    key: str,
    name: str,
    region: str,
    *,
    within: tuple[str, ...] = (),
    **kw: Any,
) -> Neighbour:
    """Make a place, store it under `key` and put it in its region."""
    place = theban.b.place(name, **kw)
    theban.places[key] = place
    _settle(theban, place, within, region)
    return place


def _append(record: Neighbour, text: str) -> None:
    """Add a paragraph to a record's summary, ahead of its secrets."""
    marker = "\n\nSecrets\n"
    summary = record.summary.rstrip()
    if marker in summary:
        head, tail = summary.split(marker, 1)
        record.summary = f"{head.rstrip()}\n\n{text}{marker}{tail}"
    else:
        record.summary = paragraphs(summary, text)


def build(theban: Theban) -> None:
    _PENDING.clear()
    _magical_sites(theban)
    _infernal_sites(theban)
    _holy_houses(theban)
    _magi(theban)
    _leagues(theban)
    _titan_factions(theban)
    _traditions(theban)
    _holy_and_heretic(theban)


# ------------------------------------------------- the sibyls' dwellings


def _magical_sites(theban: Theban) -> None:
    _add(
        theban,
        "erythrae",
        "Erythrae",
        "anatolia",
        summary=secrets(
            paragraphs(
                "A small town on the Ionian coast facing the island of "
                "Khios, home of Demophile, the Erythraean Sibyl. Of the "
                "ten sibyls she speaks most nearly as a Christian would, "
                "and so she is the best known of them; her answers come as "
                "riddles, very often acrostics, a form she is said to have "
                "devised, in which the first letters of each line spell out "
                "the meaning.",
                "Every sibyl sits in a strong Magic aura or regio (the book "
                "gives no number) and cannot go far from it without "
                "risking Acclimation and the loss of her sight; she seldom "
                "lives alone, and keeps guardians, mortal or otherwise. "
                "For the sibyl's character guide, see the Bestiary.",
            ),
            "Sibyls are magic humans, immortal and truly far-seeing, "
            "though few know it; 'sibyl' may be an office handed on rather "
            "than one woman. Their daughters by visitors, the sibyllides, "
            "are magic kin gifted in prophecy and second sight, who must "
            "come home every ten years to tell their mothers how the world "
            "goes; at least one is a magus of the Order, with a natural "
            "bent for Intellego.",
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "samian_sibyl",
        "The Cave of the Samian Sibyl",
        "islands",
        within=("Samos",),
        summary=paragraphs(
            "A cave in the hills of Samos, where Phyto, the Samian Sibyl, "
            "lives among the shepherds' grazing; she is the easiest of the "
            "sibyls to approach, and the herdsmen bring her gifts. A "
            "question put to her must be framed as a rhyming riddle, but "
            "her replies are plain spoken. She lies in a strong Magic aura "
            "(no number is given) that she cannot leave without losing her "
            "gift.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        theban,
        "dardania",
        "Dardania on Mount Ida",
        "anatolia",
        summary=paragraphs(
            "The slopes of Mount Ida in the Troad, where Amalthea, the "
            "Hellespontine Sibyl, has her seat; she came from Troy itself. "
            "Anyone born a Trojan may have a true prophecy of her, but on "
            "Troy, or the town that stands there now, she will say nothing "
            "at all, not since she foretold the war that killed so many of "
            "her people. Her home is a strong Magic aura (its number is "
            "not given).",
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "phrygian_sibyl",
        "The Haunt of the Phrygian Sibyl",
        "anatolia",
        summary=secrets(
            paragraphs(
                "Somewhere in the Phrygian uplands of the Anatolian "
                "plateau lives the sibyl called Lamia, of ill repute even "
                "if she is probably not the child-eating faerie who shares "
                "her name. She gives no prophecy freely: a questioner must "
                "wrestle her down and force the words from her, and she is "
                "far stronger than any of her sisters. The prophets of "
                "Lamites (1123 to 1127) took her as their covenant's "
                "patron and did not live long.",
            ),
            "Whether the sibyl or the faerie Lamia killed the magi of "
            "Lamites is the storyguide's to say; each had cause.",
        ),
        **RUMOURED,
    )


# --------------------------------------------------- the infernal sites


def _infernal_sites(theban: Theban) -> None:
    _add(
        theban,
        "akgah_battlefield",
        "Akgah's Battlefield",
        "constantinople",
        realm="Infernal",
        levels=[
            Builder.level(
                "The Blasted Field",
                0,
                "Infernal",
                notes=(
                    "A ruined battlefield where Akgah lolls on heaps of "
                    "rotting dead, plunder and defiled relics, feeding at "
                    "leisure; hundreds of pikes about it carry the bodies "
                    "of suicides, ravished nuns and other lost souls. The "
                    "book gives the regio no aura number."
                ),
            )
        ],
        summary=secrets(
            paragraphs(
                "Open country about twelve miles from Constantinople, "
                "where nothing marks the way into an Infernal regio, the "
                "lair of the demon prince that wrecked the Fourth Crusade "
                "(see the Bestiary). Akgah takes the shape of a "
                "two-headed leopard the size of an elephant, with golden "
                "wings and fragrant gold-and-black fur, a twisted mirror "
                "of Venice's winged lion; greed, lust and battle-madness "
                "take hold of those around it.",
                "In the spring of 1204 it fought the Hagka, the Divine "
                "two-headed eagle that guarded the city, among the statues "
                "of the Hippodrome, and broke part of the arena in the "
                "struggle. The Hagka fled wounded; crusaders who saw the "
                "fight took it for a vision of St Mark's lion winning, and "
                "fought the harder. The Hagka, Divine Might 40, now keeps "
                "to the wild mountains of Asia Minor as the protector of "
                "Nicaea, its white feathers soiled and its wounds open "
                "until the empire is made whole; it shelters any pious "
                "Greek loyal to the empire and is the enemy of every "
                "unrepentant crusader.",
            ),
            "Akgah planned the Fourth Crusade and the fall of the city, "
            "which raised it high among the princes of Hell. It now works "
            "to keep the successor states at war, feeding their greed and "
            "mistrust of one another. Before it, Andronikos Komnenos sold "
            "his soul to a demon in a woman's shape for the throne he took "
            "in 1182, and his massacre of the Latins set Venice and "
            "Montferrat against the empire; the excommunication of the "
            "crusaders after Zara let demons walk among them, and several "
            "of their lords made pacts for protection, fame or gold. Like "
            "Andronikos, most of the crusade's leaders were dead within a "
            "few years.",
        ),
        **RUMOURED,
    )


# ------------------------------------------ the monasteries of the saints


def _holy_houses(theban: Theban) -> None:
    b = theban.b
    w = theban.world
    w["karakalou"] = b.church(
        "The Karakalou Monastery",
        church="Monastery or nunnery",
        order="Orthodox monks of Mount Athos",
        summary=paragraphs(
            "One of the monasteries of the Holy Mountain. A drakos in the "
            "shape of a vast serpent once crawled out of the sea and made "
            "its home here, and the monks simply kept it as their house "
            "snake (see the Faerie landscape: many drakoi can take a "
            "serpent's form, now and then with a man's head, and some "
            "grow huge).",
        ),
    )
    _settle(theban, w["karakalou"], ("Mount Athos", "Athos"), "greece")
    w["hosios_loukas"] = b.church(
        "The Monastery of Hosios Loukas",
        church="Monastery or nunnery",
        order="Orthodox monks",
        summary=paragraphs(
            "A monastery on the slopes of Mount Helicon in Boeotia, built "
            "around the tomb of Saint Luke the hermit (Hosios Loukas), who "
            "lived here in the tenth century and is its patron, a local "
            "saint of Divine Might 25.",
        ),
    )
    _settle(
        theban, w["hosios_loukas"], ("Mount Helicon", "Boeotia", "Thebes"), "greece"
    )
    w["rufinianae"] = b.church(
        "Rufinianae",
        church="Monastery or nunnery",
        order="Orthodox monks",
        summary=paragraphs(
            "A monastic complex a few miles from Chalcedon, on the Asian "
            "shore of the Bosporus, where the imperial family often broke "
            "a journey. Its patron is Saint Hypatios, a local saint of "
            "Divine Might 25.",
        ),
    )
    _settle(theban, w["rufinianae"], ("Chalcedon",), "constantinople")


# ------------------------------------------------------------------ magi


def _magi(theban: Theban) -> None:
    b = theban.b
    m = theban.magi
    m["kristophoros"] = b.magus(
        "Kristophoros",
        covenant=None,
        house=BONISAGUS,
        age=None,
        summary=paragraphs(
            "A Bonisagus preacher who holds the First Commandment above "
            "everything. To him the pagan survivals all through the "
            "Tribunal's customs are a creeping evil, and he means to "
            "scrub every trace of idolatry out of Hermetic practice in "
            "Thebes. Oddly he has no quarrel with the titans, who ask "
            "no worship, only with the faerie gods who hunger for it. "
            "The book names no covenant for him.",
            "That makes him the rallying point of the Legion of Atlas, "
            "whose aims match his though their reasons do not; his "
            "eloquence has more than once saved magi who harmed "
            "faeries from conviction, so player magi may find him an "
            "ally at Tribunal, wanted or not.",
        ),
    )
    m["evantia"] = b.magus(
        "Evantia",
        covenant=_covenant(theban, "Moero's Garden"),
        house=JERBITON,
        age=None,
        summary=paragraphs(
            "Of Moero's Garden, and the most respected of the Seekers of "
            "the Fallen, who look for the titans' return and study Magic "
            "auras, regiones and the ways into the Magic Realm. The book "
            "gives her only that line and no House; she is entered as "
            "Jerbiton, since seven of her covenant's eight magi are.",
        ),
    )


def _covenant(theban: Theban, name: str) -> Any:
    try:
        return theban.covenant_named(name)
    except KeyError:
        return None


# ------------------------------------------------------- Hermetic leagues


def _leagues(theban: Theban) -> None:
    b = theban.b
    w = theban.world
    w["league_of_constantine"] = b.faction(
        "The League of Constantine",
        faction="Other",
        decides="A council",
        wants="A Greek emperor back on the throne of Constantinople and the Church freed of Rome; first, the lost battle standard, as a clue to the hagka",
        offers="Magi and their martial apprentices for the Nicene cause",
        summary=secrets(
            paragraphs(
                "A Hermetic league that would set the empire back on its "
                "true road: a rightful Greek emperor in Constantinople and "
                "the Church out from under the pope. Earlier conquerors of "
                "the city married into its great houses and carried on "
                "the Roman line; the Latins did neither, and they bent the "
                "Church to Rome as well. Its members are all Jerbiton, "
                "though nothing requires it, and each has an apprentice "
                "near the Gauntlet from the antigones, more warlike than "
                "their masters. It is centred at Moero's Garden, where four "
                "of the seven Jerbiton belong and the two youngest blame "
                "the city's fall on their elders' idleness.",
                "Its members have found that Infernal powers helped bring "
                "the city down, and they believe the missing hagka is the "
                "key to setting things right. The emperor's divine "
                "authority rests on three things: his battle standard (a "
                "bronze staff topped by a gold eagle, its purple silk "
                "bearing the imperial sign, last seen when Isaac Angelos's "
                "army broke before the Bulgarians in 1190; borne beside "
                "the emperor it gives his troops +3 to Discipline and "
                "Morale), his crown (made for each emperor and of no power "
                "alone, but needed to wake the others; the Latins took "
                "every old crown), and the hagka itself, a bronze "
                "two-headed eagle on a lance with an icon of the Virgin "
                "hung from it, which gives its bearer Magic Resistance 10. "
                "Together they spread that resistance to every friendly "
                "troop in sight and raise the bonus to +6. Today the "
                "Bulgarians have one, the Latins another, and the third is "
                "lost: Alexios V Doukas Mourtzouphlos left both crown and "
                "hagka behind when French knights routed him near Philia "
                "early in 1204. The league is now searching Bulgarian "
                "lands for the standard.",
            ),
            "The league is right: the city has lost Divine favour, and "
            "the hagka's return would bless a truly devout emperor, Greek "
            "or not, with Solomon's wisdom, David's strength and St Paul's "
            "mercy. But the demons have hidden from its spells; it knows "
            "the fall was Infernal work but not whose hands, and so cannot "
            "tell friend from foe. The hagka may be whole or broken, in a "
            "crusader's treasury, a Greek monastery, the burned Venetian "
            "quarter's rubble or the bed of the Bosporus.",
        ),
    )
    w["children_of_olympos"] = b.faction(
        "The Children of Olympos",
        faction="Other",
        decides="Its leader",
        ruler="Lucian the Scholar of Aegaea",
        wants="The old Greek gods as the covenants' patrons, bound by lasting pacts",
        offers="Initiation into Elysian Ecstasy, with Lucian as mystagogue",
        summary=secrets(
            paragraphs(
                "A small, odd Hermetic league gathered round Lucian the "
                "Scholar of Merinita, of Aegaea. It holds that the Order "
                "should turn from the waning Divine and Infernal to an "
                "older footing: magical beings care nothing for mortals, "
                "but faeries are drawn to the fates of men, and the Greek "
                "gods have outlasted every rival. It wants each covenant's "
                "patron to be one of the old gods. It has sympathisers but "
                "few true members, most of them Merinita; its existence is "
                "open, its methods are not.",
                "Lucian has invented two Mysteries by which a person "
                "channels a chosen god, who possesses her and lends her "
                "his Personality Trait and Sympathy Traits: Elysian "
                "Ecstasy (Minor) and the stronger, riskier Olympian Pact "
                "(Major, with a Major Personality Flaw fitting the god, "
                "and a share of the god's powers at a Warping Point a "
                "use). The initiation needs no Merinita cult lore: the "
                "initiate wins a boon from twelve mighty beings, each "
                "standing for one Olympian, then performs a rite in an "
                "Olympian's shrine as Sirius rises, taking Susceptibility "
                "to Faerie Power with the gift. Lucian has been mystagogue "
                "for every member who knows Elysian Ecstasy; he alone has "
                "the Pact.",
                "Seekers commonly match the Houses to the Olympians: "
                "Bjornaer to Poseidon, Bonisagus to Zeus, Criamon to "
                "Hestia or Dionysos, Ex Miscellanea to Demeter, Flambeau "
                "to Apollon, Guernicus to Hera, Jerbiton to Aphrodite, "
                "Mercere to Hermes, Merinita to Artemis, Tremere to "
                "Athena, Tytalus to Ares and Verditius to Hephaistos; "
                "Diedne was Demeter, later Hades. Some say Trianoma chose "
                "the Founders to fit the pattern, and that a House was "
                "bound to fall once Ex Miscellanea made thirteen.",
            ),
            "Under it lies Lucian's unspoken hope that Faerie will replace "
            "the Magic auras of the Theban covenants and bring back the "
            "worship of the gods. He believes the gods feed on their epic "
            "stories, which must be lived again, and he has cast many of "
            "the Tribunal's magi and covenants as players in his great "
            "re-enactment: his sudden, seemingly treacherous shifts at "
            "Tribunal are attempts to push them into their parts. He may be "
            "channelling impostors, faerie or Infernal; he has yet to win "
            "any god as a patron; and his Twilight Scars make him forget "
            "who he is while a god rides him. Proximios means to set "
            "Celaenea, who loves Hermes, against him, and to slip an "
            "infernalist into the league so that it calls up a False God.",
        ),
    )
    w["league_of_the_vigilant"] = b.faction(
        "The League of the Vigilant",
        faction="Other",
        decides="Its leader",
        ruler="Hydatius of Ingasia, its general",
        wants="To find any demon's servant hidden in the Order",
        offers="Funds and magical supplies (from Proximios)",
        rules="Members other than the two founders are kept secret",
        summary=secrets(
            paragraphs(
                "A new league of demon hunters. Most magi know Infernal "
                "powers rode with both Latin and Greek armies when "
                "Constantinople fell, and many fear the Order is tainted "
                "too. Hydatius of Ingasia leads it, and Proximios of "
                "Alexandria pays for it and supplies it. It is still "
                "small, with no home or meeting place; the founders want "
                "magi from outside the Tribunal, fresh eyes to spot the "
                "rot, and keep the other members' names secret while they "
                "court help openly themselves. Knowing Hermetic magic "
                "cannot find a demon, they rely on patient watching for a "
                "slip.",
                "The Tribunal tolerates it as it does every league, but "
                "doubts it will work; the cautious recall how witch hunts "
                "grow, while others think it needed. The founders' fine "
                "names keep its critics quiet.",
            ),
            "Proximios is an infernalist and founded the league as the "
            "first move of his plan to bring the Order down, starting in "
            "Thebes. He will steer it against innocents who look guilty "
            "(Caterina da Vigonovo of Polyaigos, the young magi of Erebos, "
            "and inquisitive Delfini of Aegaea), never leading in person: "
            "a demon wearing Hydatius's face will give the order to "
            "strike. As he gains ground he will use the league ever more "
            "openly as his shock troops. See the story An Enemy Within.",
        ),
    )
    w["league_against_idolatry"] = b.faction(
        "The League Against Idolatry",
        faction="Other",
        decides="A council",
        wants="An end to the Ceremony of Propitiation and to the Tribunal's recognition of patrons",
        rules="Boycotts the Propitiation on Delos",
        summary=paragraphs(
            "Magi who would strip the last pagan rites out of the Order's "
            "customs, working mainly through the Legislative Board. In "
            "1220 it is the magi of Oikos tou Eleous and Gigas, with "
            "fitful, lukewarm help from Artoud of Xylinites. Its target "
            "now is the Ceremony of Propitiation: the altars kept and the "
            "vis offered to patrons on Delos in Tribunal years go, it "
            "says, past the honour due to a being (proskynesis "
            "timetike) into worship (latreia), a mortal sin that brings "
            "God's anger on all who take part and on their sodales. The "
            "rite is ancient, the quarrel bitter and still unsettled.",
        ),
    )
    w["new_iconophiles"] = b.faction(
        "The New Iconophiles",
        faction="Other",
        decides="Its leader",
        ruler="Valnastium",
        wants="The holy art scattered by the sack of 1204 found and saved",
        summary=paragraphs(
            "Valnastium's league within House Jerbiton, heirs in spirit "
            "of the old League of Iconophiles from which the House grew "
            "(see Houses of Hermes: Societates). In Thebes its member is "
            "Syagricus of Moero's Garden, who goes to Constantinople at "
            "least once a year hunting the covenant's lost works of art.",
        ),
    )


# ---------------------------------------------------- the titan factions


def _titan_factions(theban: Theban) -> None:
    b = theban.b
    w = theban.world
    named = (
        "The name was Lucian's, coined in a sneering speech four "
        "Tribunals ago that mocked all three factions of titan scholars; "
        "it stuck, and the younger members now use it themselves. None "
        "of the three is yet a formal league."
    )
    w["seekers_of_the_fallen"] = b.faction(
        "The Seekers of the Fallen",
        faction="Other",
        decides="A vote of all",
        ruler="Evantia of Moero's Garden, most respected",
        wants="The titans restored, and with them a new age of magic",
        summary=paragraphs(
            "A loose handful of magi who think the titans, made by God "
            "before man as governors of time and nature, will bring back "
            "a golden age of magic if they are freed. To them Eden was "
            "the Magic Realm, and Adam and Eve carried shards of it out "
            "into the world, which survive as auras; so they pore over "
            "Magic auras, regiones and gates into the Magic Realm. They "
            "have repaired the lion arch at Dodona, and hunt the lost "
            "Julian Library.",
            named,
        ),
    )
    w["legion_of_atlas"] = b.faction(
        "The Legion of Atlas",
        faction="Other",
        decides="A vote of all",
        ruler="Kristophoros of Bonisagus, its rallying point",
        wants="The faerie gods undermined and the Magic Realm built anew",
        summary=paragraphs(
            "Perhaps the most radical faction in Thebes: where the "
            "Seekers would save what is left of the Magic Realm, the "
            "Atlasians would raise it again by bringing down the faerie "
            "gods, after Atlas, who led the titans' war once the gods "
            "drowned Atlantis. It is perilous work: the gods are strong, "
            "and the Oath forbids molesting the fae. Kristophoros of "
            "Bonisagus speaks for them, from his own hatred of idolatry.",
            named,
        ),
    )
    w["kampes_lovers"] = b.faction(
        "Kampe's Lovers",
        faction="Other",
        decides="A vote of all",
        ruler="Tisiphon of Hedyosmos, most prominent",
        wants="A closer bond with the imprisoned titans, and Hades' hold on their prison loosened",
        summary=secrets(
            paragraphs(
                "Magi who draw on the titans' power though the titans lie "
                "chained: some say all magic reaches men through them, and "
                "that Hermes first learned to tap it without loosening the "
                "chains. They want a closer bond with the Magic Realm's "
                "primal spirits, not the gods' fall, and are named for "
                "Kampe, the she-dragon who keeps Tartaros and has been the "
                "living chain of the gods since Zeus killed her. The faction "
                "draws Tytalus magi, for its aims echo the Titanoi's "
                "(Houses of Hermes: Societates); Tisiphon of Hedyosmos is "
                "its best-known member, and the threskeia geine of "
                "Hedyosmos is its heart.",
                named,
            ),
            "The binding magics of old (the epanankoi) are almost "
            "forgotten; some think Kampe's power fed them. Some ancient "
            "bindings still hold, and magi fear they could not mend one: "
            "the defeated giants buried under mountains and islands, the "
            "monsters of the Persian Wars sealed in objects, the oaths "
            "beneath the old leagues, and the rumoured Jar of Pandora. "
            "Delos's binding to the sea floor has already failed.",
        ),
    )


# ------------------------------------------------ the hedge traditions


def _traditions(theban: Theban) -> None:
    b = theban.b
    w = theban.world
    w["witches_of_thessaly"] = b.faction(
        "The Witches of Thessaly",
        tradition="trad_witches_of_thessaly",
        faction="Hedge coven",
        decides="Its leader",
        ruler="Destasia of Erebos",
        realm="Magic",
        wants="Their mainland grounds and vis kept from rivals",
        summary=secrets(
            paragraphs(
                "The old stygian witches of the mainland (Realms of Power: "
                "The Infernal), perhaps Trianoma's own native tradition. "
                "Those who joined the Order lead Erebos, whose head has "
                "always been one of them, of Cyra's line; others still "
                "work their binding magic outside it and quarrel with "
                "Erebos over land and vis. Binding is called the 'Stygian "
                "Art' in Thebes and is widely thought suspect, even "
                "Infernal, since goetia leads the field; Polydegmon of "
                "Hedyosmos practises a binding tradition of his own, "
                "unique until he trains an heir. Greek wizards of old "
                "hired the Witches to bind the monsters of the Persian "
                "Wars.",
            ),
            "Mainland magi call the slander rites (diabolai) witchcraft. "
            "Anyone with the right Lore and a personal tie to a being "
            "that has taken a place or a matter under its care (a "
            "village's nymph, an old shrine's god, Asklepios for a "
            "physician, a mythic forebear) can shame it into using one of "
            "its powers on a chosen target, by burning or soaking its "
            "effigy or reversing its rites: Presence + Realm Lore + "
            "modifiers + stress die against 9 + Might/5. Failure angers "
            "it for a month; a bad failure turns its power on the caller.",
        ),
    )
    w["daughters_of_erictho"] = b.faction(
        "The Daughters of Erictho",
        faction="Hedge coven",
        decides="Its leader",
        realm="Infernal",
        wants="Erebos ruined and their mountains to themselves",
        summary=paragraphs(
            "Witches of Thessaly who refused the Order and hide in the "
            "Cambunian mountains, Erebos's nearest enemies (Realms of "
            "Power: The Infernal). Some folk-witch covens have joined "
            "them, usually with the Infernal witches in charge, which is "
            "why folk witches have so bad a name in the empire.",
        ),
    )
    w["folk_witches"] = b.faction(
        "The Folk Witches of Hekate",
        tradition="trad_folk_witches",
        faction="Hedge coven",
        decides="Its leader",
        realm="Magic",
        summary=paragraphs(
            "Folk witches (Hedge Magic) of the mainland rather than the "
            "isles, many of them secret worshippers of Hekate, titaness "
            "of witchcraft, who claim an unbroken line from classical "
            "times. Some covens have allied with the Strigae or the "
            "Daughters of Erictho, mostly to their cost. The nightwalkers "
            "oppose such covens.",
            "Greek peasants also know the Folk Magic Virtue: scraps of "
            "ceremony for warding, divining, healing or the evil eye, "
            "cast through a Realm Lore at a Fatigue level each. Magi "
            "mostly think it beneath notice.",
        ),
    )
    w["nightwalkers"] = b.faction(
        "The Nightwalkers",
        tradition="trad_nightwalkers",
        faction="Hedge coven",
        decides="A vote of all",
        realm="Magic",
        wants="The fields and children kept safe from witches",
        summary=paragraphs(
            "Remnants of an ancient Greek nightwalking cult (Hedge "
            "Magic), in pockets across the empire, often cunning folk as "
            "well. They fight folk-witch covens, above all those allied "
            "to Infernal witches, and are the sworn foes of the "
            "stringles. Light-shadowed ones (alaphroiskiotoi, born on a "
            "Saturday, most with Second Sight and all with power over "
            "the vrykolakes) who sleepwalk, the parmenoi, may go with "
            "them to their night battles or be nightwalkers themselves.",
        ),
    )
    w["cunning_folk"] = b.faction(
        "The Cunning Folk",
        tradition="trad_learned_magicians",
        faction="Hedge coven",
        decides="Its leader",
        realm="Faerie",
        offers="Protection for their villages, through the local nymphs and faeries",
        summary=paragraphs(
            "The learned magicians' rural kin (Hedge Magic), as common "
            "in the countryside as the folk witches, who deal with the "
            "faeries and nymphs of their place to guard their villages. "
            "Mathematici are rare, for Byzantium has no universities, "
            "and those there are mostly came with the Venetians. "
            "Alchemists flourish in Constantinople, heirs of a great body "
            "of learning, generously paid before the fall for their work "
            "on Greek Fire and other arms.",
        ),
    )
    w["apostles_of_apollonius"] = b.faction(
        "The Apostles of Apollonius",
        faction="Hedge coven",
        decides="Its leader",
        realm="Magic",
        offers="Fair winds and calm seas, for hire",
        summary=paragraphs(
            "Elementalists (Hedge Magic) devoted to Apollonius of Tyana, "
            "scattered through the Greek islands and Asia Minor and in "
            "touch with their Arab fellows to the south and east. Command "
            "of water and wind is worth much to sea peoples, and "
            "merchants sometimes hire them for a safe voyage.",
        ),
    )
    w["makhai"] = b.faction(
        "The Makhai",
        faction="Hedge coven",
        decides="Its leader",
        realm="Magic",
        wants="Vengeance on the gods for the titans' prison",
        summary=secrets(
            paragraphs(
                "Rumoured sorcerers who serve Ekhidna and Typhon, the "
                "monsters Earth bore to avenge the titans on the faerie "
                "gods; a Greek kin of the Muspelli (Rival Magic). The "
                "storyguide may fold them into the Pelasgian wizards "
                "below, or use them in their place.",
            ),
            "A Greek version of the gruagachan could be drawn from the "
            "Pelasgians before the Hellenes: worshippers of the titans, "
            "descended from the serpent-tailed giants, with power over "
            "curses and blessings tied to what is allowed and forbidden, "
            "some goetic spirit magic in place of tattoos, and perhaps a "
            "store of Defixio Lore. Giant-blooded Greeks take Mythic Blood "
            "(Gigantes), usually with a Focus in strength or Terram and the "
            "Rebellious Flaw; Large, Snake Legs and needing to touch the "
            "ground are common. Magi also comb the islands for "
            "katadesmoi, the cursing tablets of Katadesmos (Defixio) "
            "Magic, which struck at any range and set conditional curses; "
            "it is why Leadworker turns up among hedge wizards, though "
            "among magi it is Tremere's secret.",
        ),
    )
    w["cult_of_orpheus"] = b.faction(
        "The Cult of Orpheus",
        faction="Hedge coven",
        decides="A council",
        realm="Magic",
        summary=paragraphs(
            "A native Greek tradition now within Ex Miscellanea (Houses "
            "of Hermes: Societates), with power over the bonds between "
            "people. Members live at Erebos, and Zacharias tends the "
            "cult's holy grove of Orphykia on Lesbos. They take a keen "
            "interest in adelphopoiesis, the oath-bound brotherhood rite "
            "(a True Friend Virtue or Flaw and a Sympathetic Connection), "
            "which some Jerbiton magi have sworn, even with mundanes.",
        ),
    )
    w["pharmacopoieans"] = b.faction(
        "The Pharmacopoieans",
        tradition="trad_pharmacopoeians",
        faction="Hedge coven",
        decides="A council",
        realm="Magic",
        summary=paragraphs(
            "The herbalist tradition of Ex Miscellanea (Houses of "
            "Hermes: Societates), native to Greece; its members live at "
            "Erebos, and Galla of Epidauros was trained in it.",
        ),
    )
    w["stringles"] = b.faction(
        "The Stringles",
        tradition="trad_stringla",
        faction="Hedge coven",
        decides="Its leader",
        realm="Infernal",
        rules="Covens of thirteen; each witch takes the Infernal Blessing on joining",
        wants="The Church's power and men's rule over women broken",
        summary=secrets(
            paragraphs(
                "Witches of the Byzantine lands (an Infernal tradition "
                "like the Strigae) who look like any other woman, save "
                "that in time their wrists and ankles twist, so the old "
                "ones hide them; many a husband has found after years "
                "that his wife, and usually her mother, is one. They meet "
                "in covens of thirteen in rocky clefts and echoing gorges. "
                "Mykonos is said to swarm with them, and some small "
                "islands are full of their covens; Polyaigos was a nest "
                "of them until Laskaris cleared it.",
            ),
            "Each coven has a bodiless demon, a Watcher of the Deluders, "
            "who speaks to them as a voice and teaches maleficia. A new "
            "witch takes the Infernal Blessing, and her coven's leader can "
            "give her one more power: flight on gathered winds, healing "
            "herself with another's blood, or a breath that blights "
            "crops. Witches elsewhere can call a Mykonian stringles demon "
            "for a yearly tithe of one infant.",
        ),
    )
    w["cult_of_heroes"] = b.faction(
        "The Cult of Heroes",
        faction="Other",
        decides="A council",
        summary=paragraphs(
            "House Mercere's Mystery cult of the heroes, many of whose "
            "members claim descent from a champion of the mythic age; "
            "it keeps a close eye on Greece, where the heroes' tales are "
            "still told and some heroes, in faerie form or the real "
            "thing, may still walk. Akhilles' blood brings Greater "
            "Immunity to metal and Fury; Bellerophon's, power over wild "
            "beasts and Pride; Kastor's or Polydeukes', a twin's "
            "haunting; Daidalos's, invention and Touched by Faerie; "
            "Helen's, unearthly beauty and the Curse of Venus; "
            "Odysseus's, seamanship and a supernatural plague; "
            "Perseus's, one of his gifts' powers working through a fit "
            "tool; Theseus's, warcraft and a Code of Honour.",
        ),
    )


# ------------------------------------- holy traditions, heresies, cults


def _holy_and_heretic(theban: Theban) -> None:
    b = theban.b
    w = theban.world
    w["hesychasts"] = b.faction(
        "The Hesychasts",
        faction="Other",
        decides="Its leader",
        realm="Divine",
        rules="Only monks, perhaps some nuns; no Latins",
        summary=paragraphs(
            "Orthodox mystics who repeat the Jesus Prayer without end and "
            "hold perfectly still for hours, with special breathing, "
            "drawing the mind down into the heart in search of God; they "
            "shun ecstasies and visions as dangerous counterfeits. The "
            "practice is as old as the Desert Fathers and known from St "
            "John of Sinai's Ladder of Divine Ascent, still disputed, "
            "and spreading: besides the hermits who live apart, a newer "
            "movement brings it into the monasteries' daily offices, "
            "above all on Mount Athos.",
            "As a holy tradition (Realms of Power: The Divine), the "
            "ascetics favour Meditation, Purity, Transcendence and "
            "Understanding, the monastics Ceremony, Meditation, "
            "Transcendence and Understanding; all are prone to the "
            "Divine Gloom from their first ascent.",
        ),
    )
    w["society_of_cyprian_and_justina"] = b.faction(
        "The Society of Cyprian and Justina",
        faction="Other",
        decides="A council",
        realm="Divine",
        wants="The enemies of God fought with prayer and miracle",
        summary=paragraphs(
            "A small, devout holy society (favoured Abilities Holy Magic, "
            "Invocation, Sense Holy and Unholy, and Wonders) under the "
            "patron saints of repentant magicians: Cyprian, the "
            "third-century wonder-worker of Antioch whose demons fled "
            "from the Christian Justina when he was paid to win her for "
            "a suitor, so that he burned his books and became a priest, "
            "and she a deaconess, both later martyred. Holy Magic is "
            "found among magi too, mostly Jerbiton, with Sol Invictus "
            "societies and Jewish Kabbalists, Baal Shem and Karaites.",
            "Showy magic is deadly in Greek towns: the mob may kill an "
            "amulet-wearer or a suspected sorcerer before the Church, "
            "whose laws are mild, can try him. Jerbiton magi pass as "
            "natural philosophers if they keep their spells quiet, and "
            "the Gentle Gift is precious here.",
        ),
    )
    w["paulicians"] = b.faction(
        "The Paulicians",
        faction="Other",
        decides="A council",
        realm="Infernal",
        rules="Only the inner circle knows the creed is Infernal",
        wants="Rebel armies, as in the ninth century; for now, harm to Christians and Jews",
        summary=secrets(
            paragraphs(
                "A heretic sect of the great cities, above all "
                "Constantinople, Philippopolis and Thessaloniki, free to "
                "worship since 990 and left alone by the Orthodox Church. "
                "Its Manichaean creed sets Satan and God at endless war "
                "and its folk alone as the chosen; outwardly austere and "
                "devout, it seems harmless. The holy magae of Oikos tou "
                "Eleous preach and argue against it, and most people take "
                "them for bigots.",
            ),
            "The sect is an Infernal tradition (favoured Abilities "
            "Ceremony, Debauchery, Diablerie and Malediction). Holding "
            "the world to be Satan's, its leaders hate Church and "
            "synagogue alike, slander and denounce both, and strike at "
            "them with Infernal powers when they can; a diabolist ring "
            "tied to it worked in Thessaloniki after 1185. Its "
            "communities grow, but cannot yet raise an army.",
        ),
    )
    w["eleusinian_cult"] = b.faction(
        "The Cult of Eleusis",
        faction="Other",
        decides="A council",
        realm="Faerie",
        rules="A sponsor; no barbarians, blood-guilty or harlots; secrecy on pain of death",
        offers="Freedom from the fear of death (the Lesser Mystery, Self-Confident); for some, Death Prophecy (the Greater)",
        summary=paragraphs(
            "Greece's foremost Mystery of old, still kept by a dwindling "
            "secret few at Eleusis near Athens: initiates lose their fear "
            "of death and, in its Christian dress, grow sure of Heaven, "
            "though the Church calls it heresy. Candidates gather in the "
            "Athenian agora and walk the Sacred Way through Daphni, whose "
            "monks long favoured the cult until the Cistercians took the "
            "house in 1205. At Eleusis they drink the kykeon and Hekate "
            "seems to meet them, choosing the epoptai who go on; the "
            "Lesser Mystery is held each March, the Greater every fifth "
            "year in late August. (Eleusis itself is in Greece.)",
        ),
    )
    if _find(theban, "The Christians of Serapis", kinds=("faction",)) is None:
        w["christians_of_serapis"] = b.faction(
            "The Christians of Serapis",
            faction="Other",
            decides="A council",
            realm="Infernal",
            members=200,
            ruler="A dozen priests",
            summary=secrets(
                "A heretic sect hidden beneath Sinope that worships "
                "Serapis in God's place, around a cult statue smuggled "
                "there when the sect was thought wiped out in the fourth "
                "century. Its priests dress and act like Orthodox clergy "
                "and win converts quietly; Etoumes, the Greek lord of "
                "Sinope, has just taken one as his confessor.",
                "Serapis is a False God, who hides the Infernal source of "
                "the powers he grants; few of his flock know what he is.",
            ),
        )


# ------------------------------------------------------- the relics


def finish(theban: Theban) -> None:
    """Settle the records whose places were not built yet; write the
    relics and saints into the places that hold them; tie the factions to
    their members."""
    for record, names, region in _PENDING:
        found = _find(theban, *names, kinds=(PLACE,)) if names else None
        found = found or theban.places.get(region)
        if found is not None and found is not record:
            record.place_id, record.place_level = found.id, 0
    _PENDING.clear()
    _place_factions(theban)
    _relics(theban)
    _saints(theban)
    _members(theban)
    evantia = theban.magi["evantia"]
    if evantia.covenant_id is None:
        home = _covenant(theban, "Moero's Garden")
        if home is not None:
            evantia.covenant_id = home.id


def _covenant_place(theban: Theban, name: str) -> Neighbour | None:
    covenant = _covenant(theban, name)
    if covenant is None or covenant.place_id is None:
        return None
    return next(
        (n for n in theban.b.saga.neighbours if n.id == covenant.place_id), None
    )


def _place_factions(theban: Theban) -> None:
    w = theban.world
    homes: dict[str, tuple[tuple[str, ...], tuple[str, ...], str]] = {
        # key: (covenants, places, region)
        "league_of_constantine": (("Moero's Garden",), ("Nicaea",), "anatolia"),
        "children_of_olympos": (("Aegaea",), (), "islands"),
        "league_of_the_vigilant": (("Ingasia", "Alexandria"), (), "islands"),
        "league_against_idolatry": (("Oikos tou Eleous",), ("Thessaloniki",), "greece"),
        "new_iconophiles": ((), ("Constantinople",), "constantinople"),
        "seekers_of_the_fallen": (("Moero's Garden",), (), "anatolia"),
        "legion_of_atlas": ((), (), "greece"),
        "kampes_lovers": (("Hedyosmos",), (), "greece"),
        "witches_of_thessaly": (("Erebos",), ("Thessaly",), "greece"),
        "daughters_of_erictho": (
            (),
            ("The Cambunian Mountains", "Cambunian", "Thessaly"),
            "greece",
        ),
        "folk_witches": ((), (), "greece"),
        "nightwalkers": ((), (), "greece"),
        "cunning_folk": ((), (), "greece"),
        "apostles_of_apollonius": ((), (), "islands"),
        "makhai": ((), (), "greece"),
        "cult_of_orpheus": ((), ("Orphykia",), "islands"),
        "pharmacopoieans": (("Erebos",), (), "greece"),
        "stringles": ((), ("Mykonos",), "islands"),
        "cult_of_heroes": ((), (), "greece"),
        "hesychasts": ((), ("Mount Athos", "Athos"), "greece"),
        "society_of_cyprian_and_justina": ((), (), "constantinople"),
        "paulicians": ((), ("Thessaloniki", "Constantinople"), "constantinople"),
        "eleusinian_cult": ((), ("Eleusis",), "greece"),
        "christians_of_serapis": ((), ("Sinope",), "anatolia"),
    }
    for key, (covenants, places, region) in homes.items():
        faction = w.get(key)
        if faction is None or faction.place_id is not None:
            continue
        found = next(
            (p for c in covenants if (p := _covenant_place(theban, c)) is not None),
            None,
        )
        if found is None and places:
            found = _find(theban, *places, kinds=(PLACE,))
        if found is None:
            found = theban.places.get(region)
        if found is not None:
            faction.place_id = found.id


def _note(
    theban: Theban,
    names: tuple[str, ...],
    region: str,
    text: str,
    relic: dict[str, Any] | None = None,
) -> None:
    """Write `text` into the first record of `names` there is, else into
    the region's place; a relic goes on a church's list as well."""
    target = _find(theban, *names) or theban.places.get(region)
    if target is None:
        return
    _append(target, text)
    if relic is not None and target.kind == "church":
        target.details.setdefault("relics", []).append(relic)


def _relics(theban: Theban) -> None:
    _note(
        theban,
        ("Hagia Sophia", "Haghia Sophia"),
        "constantinople",
        "Relics: fragments of the True Cross, found by St Helena near "
        "Jerusalem, were kept here in numbers; the Venetians and Latins "
        "now hold them, and the exiles carried many small ones to Nicaea. "
        "A piece as long as a man's leg has Faith 10 (Divine Might 100) "
        "and heals any wound at once; a hand-sized piece Faith 3, healing "
        "a Medium Wound; a sliver Faith 1, an ordinary relic. Tiny ones "
        "are common, worn in gold reliquaries, and the Cross never runs "
        "out of them. The Image of Edessa came here from Jerusalem in "
        "944 and the Crown of Thorns in 1063; the Mandylion, the first "
        "icon not made by hands, was stolen in the sack.",
        {"name": "Fragments of the True Cross", "saint": "Christ", "faith": 3},
    )
    _note(
        theban,
        ("Nicaea",),
        "anatolia",
        "Relics: the exiles brought many of the smaller pieces of the "
        "True Cross from Hagia Sophia (a hand-sized piece is Faith 3 and "
        "heals a Medium Wound; a sliver is an ordinary relic).",
    )
    _note(
        theban,
        ("The Venetian Quarter", "Venetian Quarter", "The Podestà"),
        "constantinople",
        "Relic: the Crown of Thorns (Faith 7; Cure Blindness, Strengthen "
        "the Cripple and Mass Healing), whose every thorn is a Minor "
        "relic. It is the Latin emperor's, but the doge holds it as "
        "pledge for a loan of 13,134 pounds, locked away here in the "
        "Venetian quarter; it is the only relic left that can raise an "
        "empyreal aura in the city.",
    )
    _note(
        theban,
        (
            "Blachernae",
            "The Great Palace",
            "Boukoleon",
            "The Imperial Palace",
            "Latin Empire",
            "The Latin Empire",
        ),
        "constantinople",
        "Relic: the Holy Lance, the pilum of the centurion Longinus, in "
        "the city since the eighth century and now in the Latin "
        "emperor's palace (Faith 3, Expel Demons; a Powerful Relic). A "
        "second, longer lance found at Antioch in 1098 seems genuine "
        "too.",
    )
    _note(
        theban,
        ("Otto de la Roche", "The Duchy of Athens", "Duchy of Athens", "Athens"),
        "greece",
        "Relic: the Image of Edessa, a napkin-sized piece of Christ's "
        "linen shroud bearing the print of His face (Faith 5, Divine "
        "Might 50; Celestial Immunity and the Leap of the Faithful), "
        "taken from Hagia Sophia and now Otto de la Roche's. Eastern "
        "churchmen resent it bitterly; a few appealed to Innocent III, "
        "for nothing.",
    )
    _note(
        theban,
        ("The Studion", "Studion", "The Monastery of Stoudios"),
        "constantinople",
        "The most exact copy of the Synaxarion, the Orthodox calendar of "
        "more than two thousand saints with a short life and readings "
        "for each, compiled in the eleventh century and kept up to date, "
        "is here beside the Church of St John the Baptist. It lists "
        "saints the West does not, among them both Justinians and the "
        "patriarchs Photios and Ignatios.",
    )


def _saints(theban: Theban) -> None:
    _note(
        theban,
        ("Thessaloniki",),
        "greece",
        "Saint: Demetrios, the city's patron and the soldiers' (an area "
        "saint, Divine Might 50). In 1207, besieged by Ioannitsa the "
        "Greek-slayer, tsar of Bulgaria, the city called on him, and he "
        "took bodily form and killed the tsar with a spear.",
    )
    _note(
        theban,
        ("Trebizond",),
        "anatolia",
        "Saint: Eugenios, the city's patron (an area saint, Divine Might 50).",
    )
    _note(
        theban,
        ("Constantinople",),
        "constantinople",
        "Saints: Euphemia, the city's first official saint and its patron "
        "(an area saint, Divine Might 50), under the Theotokos, its "
        "protector; Cosmas and Damian, the unmercenary physician twins, "
        "saints of doctors and the suburbs (local, Divine Might 25). The "
        "greater saints (Divine Might 75) most invoked are St George and "
        "St John Chrysostom, and St Nicholas of Myra (area) for sailors, "
        "merchants, students and children. Oaths are sworn by St Basil "
        "of Caesarea or Saints Theodoros and Theophanes, who may punish "
        "a notorious perjurer; islanders swear by their river, after the "
        "Styx.",
    )
    _note(
        theban,
        ("Patmos",),
        "islands",
        "Saint: Leontios, patron of the monastery of St John the "
        "Evangelist, a holy fool who was never a monk and was made a "
        "saint for his austerities alone (local, Divine Might 25).",
    )
    _note(
        theban,
        ("Caesarea", "Kayseri"),
        "anatolia",
        "Saint: Prokopios, the first martyr of Diocletian's "
        "persecution, much loved in Caesarea (local, Divine Might 25).",
    )
    _note(
        theban,
        ("Delphi",),
        "greece",
        "Herophile, the Delphic Sibyl, also lives in the sacred precinct; "
        "she is not and never was the Pythia, though the two share the "
        "place. She prophesies only for those of royal blood, however "
        "thin. See also the Erythraean, Samian, Hellespontine and "
        "Phrygian sibyls.",
    )
    _note(
        theban,
        ("Zakynthos",),
        "greece",
        "The one-eyed, fire-eyed drakoi here, great stone-throwers, are "
        "probably the kyklopes' children, who came up out of Tartaros "
        "to live by the volcanoes.",
    )


def _members(theban: Theban) -> None:
    b = theban.b
    w = theban.world
    m = theban.magi
    for key, slug, note in (
        ("children_of_olympos", "lucian", "Its leader and mystagogue"),
        ("league_of_the_vigilant", "hydatius", "Its general"),
        ("league_of_the_vigilant", "proximios", "Co-founder and paymaster"),
        ("league_against_idolatry", "artoud", "Lends it fitful support"),
        ("new_iconophiles", "syagricus", "A member"),
        ("seekers_of_the_fallen", "evantia", "Its most respected member"),
        ("legion_of_atlas", "kristophoros", "Its rallying point"),
        ("kampes_lovers", "tisiphon", "Its best-known member"),
        ("witches_of_thessaly", "destasia", "A Witch of Thessaly, leader of Erebos"),
        ("cult_of_orpheus", "zacharias", "Tends Orphykia"),
        ("pharmacopoieans", "galla", "Trained in the tradition"),
    ):
        magus: Character | None = m.get(slug)
        if magus is not None and key in w:
            b.link(w[key], "characters", magus, note)
    for key, name, note in (
        ("league_of_constantine", "Moero's Garden", "Its centre; four members"),
        ("league_against_idolatry", "Oikos tou Eleous", "Its members"),
        ("league_against_idolatry", "Gigas", "Its members"),
        ("kampes_lovers", "Hedyosmos", "Its heart"),
        ("witches_of_thessaly", "Erebos", "Led by one of them"),
        ("daughters_of_erictho", "Erebos", "Their enemy"),
        ("paulicians", "Oikos tou Eleous", "Preaches against them"),
    ):
        covenant = _covenant(theban, name)
        if covenant is not None:
            b.link(w[key], "covenants", covenant, note)


# --------------------------------------------------------------- stats

P = Profile
GREEK = "Greek"

#: Each magus the book sketches without a stat block, by character key.
PROFILES: dict[str, Profile] = {
    "kristophoros": P(
        strong="com pre int",
        arts={"Vi": 5, "Me": 4, "Pe": 3},
        abilities={
            "Artes Liberales": (4, "rhetoric"),
            "Code of Hermes": (4, "Tribunal debate"),
            "Theology": (4, "idolatry"),
            "Faerie Lore": 2,
        },
        age=80,
        native=GREEK,
    ),
    "evantia": P(
        strong="int per",
        arts={"In": 5, "Vi": 5, "Re": 3},
        abilities={
            "Magic Lore": (4, "regiones"),
            "Philosophiae": 3,
            "Etiquette": 2,
        },
        age=90,
        native=GREEK,
    ),
}


def stats(theban: Theban) -> None:
    """Generated stats for Kristophoros and Evantia, neither of whom
    has a printed stat block."""
    b = theban.b
    for key, profile in PROFILES.items():
        apply(b, theban.magi[key], profile)
