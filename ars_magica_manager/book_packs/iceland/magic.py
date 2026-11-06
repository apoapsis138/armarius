"""Iceland's magicians (LFI pp. 27-29 and 45-61), in paraphrase.

Records: the factions Galdramen Hreppur, sitting at the land part's
Eldborg, Icelandic Magicians (what the traditions share: the bars on
Virtues, and the Supernatural Virtues of pp. 54-61), Traditional
Galdramen, Schooled Galdramen, Trollsynir, Vitkir of Iceland, Volur,
Visindamen, Seithkonur and The Order of Odin, a name other packs share. Dormant stories hold the book's seeds for these
people.

The rules are the catalog's: Traditional Galdramen and Trollsynir are
traditions, with the Virtues and Abilities their book gives, and each
record here points to them. What remains in words is what has no place
on a sheet: the hreppur's laws, nidstong and the lifting of Curses."""

from __future__ import annotations

from ...models import Neighbour
from ..builder import Builder, dormant, joined_lines, paragraphs

#: Where a record's magic is now.
RULES_ARE_THE_CATALOGS = (
    "The rules are on the sheet of anyone who belongs to the tradition; "
    "Help has How to play a galdraman."
)


def build(b: Builder) -> None:
    eldborg = _eldborg(b)
    hreppur = _hreppur(b, eldborg)
    shared = _icelandic_magicians(b)
    traditional = _traditional_galdramen(b)
    schooled = _schooled_galdramen(b)
    trollsynir = _trollsynir(b)
    vitkir = _vitkir(b)
    volur = _volur(b)
    visindamen = _visindamen(b)
    seithkonur = _seithkonur(b)
    for group in (traditional, schooled, trollsynir, vitkir, seithkonur):
        b.link(group, "places", hreppur, "Sits in the hreppur at Eldborg")
    for group in (volur, visindamen):
        b.link(group, "places", hreppur, "Admitted in the Interdiction")
    for group in (traditional, schooled, trollsynir):
        b.link(group, "places", shared, "The Virtues and limits they share")
    b.link(traditional, "places", volur, "Its women are galdrakona")
    b.link(seithkonur, "places", volur, "Among the women called volur")
    b.link(schooled, "places", traditional, "Their model and their rivals")
    for school in ("Holar Cathedral School", "Skalholt Cathedral School"):
        found = _named(b, school)
        if found is not None:
            b.link(schooled, "places", found, "Trains schooled galdramen")
    odin = _order_of_odin(b)
    b.link(odin, "places", hreppur, "What the Order would mistake for it")
    _stories(b, eldborg)


def _named(b: Builder, name: str) -> Neighbour | None:
    """The record of that name, or none: another part may have made it."""
    return next((n for n in b.saga.neighbours if n.name == name), None)


def _eldborg(b: Builder) -> Neighbour:
    found = _named(b, "Eldborg")
    if found is None:
        raise LookupError("The land part, which runs first, makes Eldborg")
    return found


def _hreppur(b: Builder, eldborg: Neighbour) -> Neighbour:
    return b.faction(
        "Galdramen Hreppur",
        faction="Hedge coven",
        realm="Magic",
        place=eldborg,
        decides=(
            "A council, sitting yearly at Eldborg; it also judges disputes "
            "between members (p. 28)"
        ),
        wants=(
            "Its members left in peace by the godar, its magic discreet, "
            "its trade orderly, and no talk of it among outsiders"
        ),
        offers=(
            "Fixed fees for magical service; wards on the interior paths; "
            "a court for what cannot go to the things; a godi's defence "
            "against a charge of witchcraft"
        ),
        summary=paragraphs(
            "Iceland's magicians long ago did what its farmers do, and made "
            "a hreppur of their own: a cooperative that sets their fees, "
            "shares out common land and common duties, and settles the "
            "quarrels no thing could be asked to hear. It meets once a year "
            "at Eldborg in the Western Quarter, five days after the Althing "
            "ends, and it has a bargain with the godar: the paths across "
            "the interior are kept warded against trolls and violent "
            "spirits, and its people are not hounded.",
            "It began in the tenth century, when godar were pressing "
            "magicians to meddle in feuds. A magician who felt that pressure "
            "had the whole hreppur behind him, and the godar soon thought "
            "better of it. Charms and spells that meant no harm were sold "
            "at fixed prices to all but the blacklisted, and the hreppur "
            "came to regulate the gathering of ond, the vital force that "
            "Odin gave to man in the old tale and Latin magi call vis, which "
            "galdramen give to the spirits. Its people have also treated with "
            "giants and dragons to keep the peace. Volur and visindamen were "
            "first asked to join in the Interdiction of 1031-1041 "
            "(pp. 11-12, 14, 17, 27-29).",
        ),
        rules=joined_lines(
            "Fees (1220): a trollson, galdraman or vitkir charges one "
            "standard ounce a day or part of a day, to two standard marks "
            "(16 ounces) a season. Seithkona and witches charge half an "
            "ounce a day, to one mark (8 ounces) a season. Ond is charged "
            "at one standard mark a pawn.",
            "Discretion: magic is to be discreet, with as few witnesses as "
            "may be. A householder hiring a magician first assures him none "
            "of the household will take offence; if that fails, the magician "
            "is not answerable. Supernatural affairs are not discussed with "
            "non-members unless it cannot be helped, and the council alone "
            "decides what men of rank must be told. A member charged with "
            "witchcraft through unjustified, indiscreet magic pays the godi "
            "or storbaendur who defends him six law marks; if it was beyond "
            "his control the defence is free.",
            "Ond: a member may claim any source on his own land; on common "
            "land the first to harvest it claims it. A poacher returns the "
            "ond and pays a mark a pawn. The claims of a member dying "
            "without an heir lie open to the first harvester; abandoned "
            "sites may be claimed, and the hreppur judges any dispute.",
            "Duties: the cost and work of the path wards is split as evenly "
            "as the members allow. One who cannot contribute gives at least "
            "three pawns a year; one too poor for that pays nothing, but "
            "may not judge or sit on the council. Serving anyone on the "
            "blacklist, reviewed yearly, costs a fine of three law marks "
            "and the fee taken.",
            "Black magic: malign magic on a human forfeits the hreppur's "
            "protection; magical attacks are allowed only against outlawed "
            "magicians. A magician in a mundane conflict uses mundane means "
            "or loses that protection. Attacked at home or on an innocent "
            "journey, not on a raid, he may use magic to drive off attackers "
            "or get away, but only with his life at risk, and never to "
            "injure on purpose.",
        ),
        secrets=paragraphs(
            "Its authority is loose: no oath, no ceremony of joining, and "
            "attending Eldborg or paying the path tax is voluntary, but only "
            "those who keep its laws share the protection of its deal with "
            "the godar. Magi may be admitted on the same terms. Witchcraft "
            "cases embarrass it badly, and it works to end them fast "
            "(pp. 102, 105).",
            "The meeting in the book's saga draws 11 trollsynir, 6 vitkir, "
            "62 galdramen (11 of them schooled) and 8 seithkonur, with a "
            "council of five (p. 102).",
            "With the Guardians at its side it could stand even against "
            "Hermetic magi. Kill a prominent galdraman and many landvaettir "
            "lords are incensed; kill a trollson and his giant kin are "
            "enraged; a war could turn all of supernatural Iceland on the "
            "Order (p. 29).",
        ),
    )


def _icelandic_magicians(b: Builder) -> Neighbour:
    return b.faction(
        "Icelandic Magicians",
        faction="Hedge coven",
        realm="Magic",
        summary=paragraphs(
            "The island has its own ways of magic, far from the roots of "
            "Hermes: song that calls the land's spirits, giants' "
            "blood, runes cut and reddened, shapes taken and shapes forced "
            "on others, curses set on a horse-headed pole in sight of an "
            "enemy's farm. Latin magi call their makers hedge wizards. An Icelander who sees a nidstong knocks "
            "it down on the spot.",
        ),
        rules=joined_lines(
            RULES_ARE_THE_CATALOGS,
            "Limits (p. 45): those peculiar to Norse magic are for Norse "
            "characters, at the storyguide's careful choice. Hermetic Virtues are "
            "open to the Gifted (Hedge Magic RE p. 12); trollsynir have no other "
            "shapeshifting power and nothing of a realm at odds with theirs.",
            "Virtues: Mighty Fylgja and Large Fylgja, Hamfarir, Potency, Curse, "
            "Jotunn Affinity with Earth, Galdor Conjuring, Galdor Enchantment. The "
            "book's other Talents are the gruagach Arts, or Rival Magic's Winter's "
            "Breath, Storm's Eye, Wildfire and Sjonhverfing. The book's Gift has no "
            "Ability: keep its score in notes (pp. 57-58).",
            "Nidstong (pp. 57-59): a tall rune-cut pole topped with a horse's "
            "skull, set overlooking the victims' land; it can strike groups. "
            "A casting roll daily against each target until it succeeds, "
            "with no backlash or botch while it stands; the last rolls count "
            "when it falls.",
            "Lifting a Curse (p. 59): the maker beats the first roll; or the "
            "condition is met. A Curse holder beating the total, or an "
            "Intellego Vim of the 7th magnitude, learns the condition. "
            "Intellego Vim of 20+ shows the Ease Factor, and a Perdo Vim "
            "ritual above the casting total dispels it, at the risk of "
            "catching it on a botch.",
            "Sun Duration (p. 51): in Iceland D: Sun lasts to the next "
            "sunrise or sunset, from about 23 hours at midsummer to 1, and "
            "further north longer. Optionally a full turn of the sky breaks "
            "it, at just under 24 hours.",
        ),
    )


def _traditional_galdramen(b: Builder) -> Neighbour:
    return b.faction(
        "Traditional Galdramen",
        faction="Hedge coven",
        tradition="trad_galdramen",
        realm="Magic",
        wants=(
            "Good standing with the landvaettir lords, whose servants do "
            "their work, and their old lore left unmolested"
        ),
        offers=(
            "Spirits called by song for healing, weather, sight of far "
            "places, wards on a path or a farm, and curses"
        ),
        summary=paragraphs(
            "Norse theurgists whose art is galdor, song-magic: long chants "
            "of sacred phrases, heavy with the old Aesir stories, that call "
            "the spirits of the land to serve. A galdraman spends his life "
            "learning the landvaettir of his country and composing poems in "
            "their honour, and he will sing from a wooden platform or a "
            "chair, since the magic turns sullen against the bare ground. "
            "When he stops singing, it stops. He knows his own land's "
            "spirits only, and in a strange country must begin again.",
            "They are mostly men; a woman of the tradition is a galdrakona, "
            "and few there are. The Gift marks them, with all its unease. "
            "Though they may be pagans at heart, they need no temple for "
            "their magic, and so have escaped the Church's wrath.",
            "A galdraman's fylgja leads his spirit into Twilight, and at the "
            "last does not bring it home.",
        ),
        rules=joined_lines(
            RULES_ARE_THE_CATALOGS,
            "The tradition's chapter is Galdor; its More has Conjure a Spirit, "
            "Bargain with a Lord and Bind an Item (pp. 45-50, 54).",
            "Health (pp. 48-49): no Instant effects. Lim- and biarg-galdor "
            "spirits add the magnitude to recovery rolls, attending at least "
            "12 hours in 24; a ritual conjuring with vis can rival Hermetic "
            "cures.",
            "Longevity (pp. 49-50): with biarg-galdor, a lord grants it for "
            "a service besides vis, by anyone's hand. He then drinks mead "
            "with a pawn per decade of age and conjures a biarg spirit by "
            "ritual: a longevity potion of the conjuring total. Yearly mead "
            "renews it; it never fails, even on an aging result. Typical "
            "services: pull down a Christian shrine on magical ground, free a "
            "captive spirit, drive out a diabolist who tortures spirits, make "
            "a charm to clean a stream.",
            "Hermetic Potential (p. 51): one who joins the Order learns "
            "Parma Magica but no Arts. Optionally, with the Mysteries, a "
            "crippled theurgic magic may be shared with a Hermetic theurgist.",
        ),
    )


def _schooled_galdramen(b: Builder) -> Neighbour:
    return b.faction(
        "Schooled Galdramen",
        faction="Hedge coven",
        tradition="trad_learned_magicians",
        realm="Magic",
        wants="To rival the traditional galdramen",
        offers="The same services, worked with Christian learning",
        summary=paragraphs(
            "Priests trained at the cathedral schools of Holar and Skalholt, "
            "who weave divine names with animals, plants, stones, images, "
            "aromatics, talismans and written letters into intricate rites, "
            "to call the spirits as the old galdramen do. The way was opened "
            "by Saemundur Sigfusson, who came home from France and put "
            "Judeo-Christian and classical phrases in place of the heathen "
            "ones. All are clergy, so none are women.",
            "Mainland scholars would call the method dangerous and the "
            "theory heresy, but Iceland is far off and a law unto itself, "
            "and no churchman of rank who has learned of it has yet made an "
            "issue of it.",
        ),
        rules=joined_lines(
            "Learned Magicians (Hedge Magic RE, Chapter 5), Iceland's Natural "
            "Magicians (pp. 45, 51), whose sacred phrases are synthemata.",
            "They conjure magical spirits to make the effect. The only "
            "differences: they use the normal magical interaction table, "
            "and they have the Gift.",
        ),
        secrets=(
            "Being Gifted, they could learn Hermetic magic; they only lack "
            "the means. Books of Hermetic theory in either school could "
            "change that, to the horror of the Order (p. 51)."
        ),
    )


def _trollsynir(b: Builder) -> Neighbour:
    return b.faction(
        "Trollsynir",
        faction="Hedge coven",
        tradition="trad_trollsynir",
        realm="Magic",
        decides="No one: they have no formal organisation (p. 54)",
        wants="Mostly to be left alone, away from men",
        offers="Rarely, and from a very few, their powers to men's benefit",
        summary=paragraphs(
            "The sons of trolls (a man is a trollson, a woman a trollsdottir): "
            "wizards whose power is their giant blood, seldom more than three "
            "generations from a giant forebear. Each belongs to a giant clan "
            "whose ways shape him. Raised by giants or by grown trollsynir, "
            "they soak up magic as other children do speech, and know little "
            "of men. Most share their elders' hostility to mankind; a rare "
            "few turn their gifts to good. They speak Jotunn, and they are "
            "the Norse cousins of Scotland's gruagachan, though not the same.",
            "Their magic costs them. Each slip brings them nearer the wild "
            "blood, with horns or fangs or blue skin, until the mind goes too "
            "and they flee to the wilderness. Many of Iceland's trolls are "
            "said to have been trollsynir. Some choose to break their own "
            "soulstones first.",
        ),
        rules=joined_lines(
            RULES_ARE_THE_CATALOGS,
            "The Fifth Edition trollsynir of Hedge Magic RE p. 76: the gruagach "
            "Arts through the Jotnar tongue, with a Trollskap chapter. No Magic "
            "Resistance (Hedge Magic RE p. 9) and no Potency, so totals fall from "
            "the book's; Afflictions are Transformation's bad results. A printed "
            "figure stays in a record's notes.",
        ),
    )


def _vitkir(b: Builder) -> Neighbour:
    return b.faction(
        "Vitkir of Iceland",
        faction="Hedge coven",
        tradition="trad_vitkir",
        realm="Magic",
        summary=paragraphs(
            "Rune-magicians who draw on the pagan Norse gods. They are rare "
            "here, for the law comes down hard on heathen ways, and a vitki "
            "in Iceland all but needs a magic or faerie regio to hide his "
            "patron's temple in. In the old days godar who wanted power "
            "mostly gave up their arts to keep it. Vitkir sit in the "
            "Galdramen Hreppur, charge its higher fee, and can ward the "
            "interior paths as galdramen do.",
        ),
        rules="The tradition is Ultima Thule's. Pp. 9, 12, 28, 45.",
    )


def _volur(b: Builder) -> Neighbour:
    return b.faction(
        "Volur",
        faction="Hedge coven",
        realm="Magic",
        summary=paragraphs(
            "The name Icelanders often give a woman who practises magic "
            "(a volva, in the singular): the witches and seeresses who came "
            "with the Norse settlers and often worked seithr, a magic of "
            "shamanic rites. A few are galdrakona, among the traditional "
            "galdramen; others are seithkonur. No woman is a schooled "
            "galdraman, for those are all clergy.",
        ),
        rules="Pp. 9, 45.",
    )


def _visindamen(b: Builder) -> Neighbour:
    return b.faction(
        "Visindamen",
        faction="Hedge coven",
        realm="Magic",
        summary="The wise men among the Norse magicians who came with the "
        "settlers, often workers of seithr as the volur are. They stood outside "
        "the hreppur until the Interdiction.",
        rules="The book gives them no rules of their own. Pp. 9, 14.",
    )


def _seithkonur(b: Builder) -> Neighbour:
    return b.faction(
        "Seithkonur",
        faction="Hedge coven",
        tradition="trad_folk_witches",
        realm="Magic",
        summary=paragraphs(
            "Women magicians, among the volur, each of whom can borrow her "
            "fylgja's body and go abroad in it. The hreppur allows them only "
            "half the fee of a galdraman, half an ounce a day.",
        ),
        rules="Folk Witches (Hedge Magic RE, Chapter 3), each with a fylgja and "
        "Hamfarir, Second Sight and Legend Lore instead of Visions and the "
        "faerie versions. Pp. 28, 45, 55, 65.",
    )


def _order_of_odin(b: Builder) -> Neighbour:
    return b.faction(
        "The Order of Odin",
        faction="Hedge coven",
        summary=paragraphs(
            "The band of Norse wizards that senior magi of the Order of "
            "Hermes fear, on very little evidence, and fear the more for "
            "having so little.",
        ),
        rules="P. 29.",
        secrets=(
            "Whether it exists is for each storyguide to decide. On the "
            "surface the Galdramen Hreppur looks like this Order, but it "
            "grew up here, shaped by local custom and local wants, and owes "
            "nothing to anyone abroad. Icelanders mentioned the name will only be "
            "confused (pp. 29, 105). That hedge wizards can resist Hermetics "
            "at all would still confirm the Order's fears."
        ),
    )


def _stories(b: Builder, eldborg: Neighbour) -> None:
    dormant(
        b.threat(
            "The Order against the Hreppur",
            place=eldborg,
            antagonist="Hermetic magi who take the hreppur for the Order of Odin",
            summary=paragraphs(
                "Fearful magi take Iceland's magicians for the Order of Odin "
                "and move against them, and the deaths draw landvaettir "
                "lords, giant kin and the Guardians into the quarrel. The "
                "characters may stand on either side.",
                "Notes: p. 29.",
            ),
        )
    )
    dormant(
        b.threat(
            "A Friend's Longevity Bargain",
            antagonist="A rival magician, and the winter",
            summary=paragraphs(
                "A galdraman the characters respect asks them to settle some "
                "matter touching the landvaettir, and does not say it is the "
                "service his longevity deal demands. A rival magician works "
                "against them, and without knowing it they decide whether "
                "the old man sees out the winter.",
                "Notes: p. 49.",
            ),
        )
    )
    dormant(
        b.threat(
            "The Lord's Quest",
            antagonist="A landvaettir lord who sets the price of teaching",
            summary=paragraphs(
                "A galdraman seeking a new power is set quests by a lord of "
                "the landvaettir, and must earn the story experience to pay "
                "for it. The book's examples: make peace between the men of "
                "Vapnafjord and the trolls of the Eastern Quarter; bring the "
                "magic spear of the rune-magician Viga-Glum out of the middle "
                "of the Odadahraun; find the soul-stone of the giantess Mjoll, "
                "so she may die in peace; or persuade the men of Kirkadale to "
                "leave their farms for the lowlands.",
                "Notes: p. 50.",
            ),
        )
    )
    dormant(
        b.threat(
            "Hermetic Theory at the Schools",
            antagonist="The schooled galdramen of Holar and Skalholt",
            summary=paragraphs(
                "Books on Hermetic theory reach Holar or Skalholt, whose "
                "Gifted priests lack only that to learn the Order's magic. "
                "A merchant bound for Skalholt is blown off course to "
                "Snaefellsnes with Hermetic books for the bishop's school "
                "among his cargo, and the magi there must choose what to do. "
                "Trade with the schools and monasteries may equally build a "
                "library, for books on Philosophiae hold something each side "
                "could learn from.",
                "Notes: pp. 27, 51.",
            ),
        )
    )
    dormant(
        b.threat(
            "The Walrus Hunt",
            antagonist="A shapechanged trollson or giant",
            summary=paragraphs(
                "Walrus crowd the western and northern coasts in winter, on "
                "the ice floes. They are dangerous to hunt, and rich: ivory, "
                "hide, blubber and meat. Not every walrus is a walrus.",
                "Notes: p. 27.",
            ),
        )
    )
