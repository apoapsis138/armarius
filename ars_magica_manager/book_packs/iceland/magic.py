"""Iceland's magicians (LFI pp. 27-29 and 45-61), in paraphrase.

Records: the factions Galdramen Hreppur, sitting at the land part's
Eldborg, Icelandic Magicians (what the traditions share: the bars on
Virtues, and the Supernatural Virtues of pp. 54-61), Traditional
Galdramen, Schooled Galdramen, Trollsynir, Vitkir of Iceland, Volur,
Visindamen, Seithkonur and The Order of Odin, a name other packs share. Dormant stories hold the book's seeds for these
people.

The powers are described, not built: the rules text of each record gives
Fourth Edition mechanics as printed, cited by page, for a later story to
convert. No Virtue, Ability or spell is entered, so nothing here depends
on the catalogs."""

from __future__ import annotations

from ...models import Neighbour
from ..builder import Builder, dormant, joined_lines, paragraphs

#: Heads the rules of every record that gives printed mechanics.
UNCONVERTED = (
    "Fourth Edition rules as printed, described and not converted: ArM4 "
    "page references are the book's own."
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
        faction="Other",
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
        faction="Other",
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
            UNCONVERTED,
            "This record gathers the limits and Supernatural Virtues the book "
            "gives Iceland's wizards in common (pp. 45, 54-61); those peculiar "
            "to Norse magic are for Norse characters, at the storyguide's "
            "careful choice.",
            "Limits (p. 45): no Virtue or Flaw tied to a Hermetic Art, the "
            "Order of Hermes or another magical tradition. Trollsynir also "
            "have no other shapeshifting power (Skinchanger, Lycanthrope, "
            "Heartbeast, Will Over Form) and nothing of a realm at odds with "
            "theirs (Faerie Magic, Faerie Blood, True Faith).",
            "Mighty Fylgja, variable (pp. 54-55): Premonitions already "
            "brings a fylgja of Magic Might 10. Each point adds 10 Might and "
            "a power in order: Phantom (seen and heard as an apparition, an "
            "hour per point of Might spent), Spirit Voice (speaks, any "
            "language at 3, may carry Curses at no more than the Hamfarir "
            "score), Corporeality (physical form as a Beast of Virtue, 5 "
            "Might an hour). Each works only during Hamfarir. Size is -3 at "
            "most; +1 buys up to Size +0, then one point per Size. A bear "
            "(Size +2) of Might 40, corporeal, costs +6.",
            "Etin Bride, +2 (p. 55): the trollsynir's Gentle Gift, for women only.",
            "Hamfarir, +2 (pp. 55-56): needs Premonitions; gives the Talent "
            "at 1. Int + Hamfarir of 9+ sends the mind out in the fylgja's "
            "body while the flesh lies in trance: unseen, immaterial, up to "
            "a day's travel an hour (nine times its animal's speed), slower "
            "to see the world, understanding speech as at 3 but not writing. "
            "Int + Hamfarir against the sleeper's Sta + 3 enters a dream. "
            "Second Sight, Magic Sensitivity and Intellego can find it; Vim "
            "and Mentem affect it. It lasts Hamfarir hours, then the body "
            "loses a Fatigue level each 20 minutes; collapse returns the "
            "spirit at the cost of a point of Stamina, curable only by "
            "magic, leaving the fylgja where it was. A trapped fylgja means "
            "no Hamfarir or Premonitions until freed. The trance counts as "
            "effeminate; men do it in private.",
            "Potency, +2 (p. 56): a Talent from 1, raised by story "
            "experience, automatic for trollsynir, trolls and giants. It "
            "invokes a magical language (Speak Jotunn or Scribe Runes, the "
            "only two in Iceland) and may not exceed that language's score. "
            "It aids Curse, Gift, Jotunn Affinity, Shapeshift, Svonhverfing "
            "and Transform.",
            "Jotunn Affinity, +4 (pp. 56-57): a Talent from 1; at most one; "
            "Large at least, Giant Blood advised. Stress die + Com + Affinity "
            "+ Speak Jotunn + Potency + Aura against the Hermetic level, in "
            "one round, limited as a spontaneous spell. A ritual effect needs "
            "a site strong in the force, 15 minutes a magnitude, a botch die "
            "a magnitude and a Fatigue roll an hour. No vis ever; base "
            "ranges; durations past Moon are ritual. Sea (Aquam, weather at "
            "sea, fog), Storms (violent Auram and Aquam weather), Frost "
            "(cold in Auram, Aquam or Ignem), Fire (Ignem or Auram fire, "
            "smoke, heat), Earth (Terram over earth, sand, clay and stone, "
            "not metal or gems).",
            "Gift, +4 (pp. 57-58): a Talent from 1 granting abilities, traits "
            "or Virtues to oneself or others, each lost on a set prohibition. "
            "Stress die + Int + Gift + Speak Jotunn or Scribe Runes + Potency, "
            "beating an Ease Factor of 3, and the recipient's Magic Resistance "
            "(Vim Parma) counts even if willing. Add 7 a Characteristic point, 3 an "
            "Ability point, 7 a Virtue or Flaw point; prohibition +3 specific, "
            "+0 general, -3 sweeping; poetic justice 14 either way. A 0 zeroes "
            "the total. Failing by 7 or more lets the storyguide lay a Curse "
            "on the caster at that Ease Factor. Speech needs the target "
            "present; runes need only reach him. Knacks in Arcane Abilities "
            "and self-improvement are warned off; the storyguide may veto "
            "(p. 57).",
            "Curse, +4 (pp. 57-59): a Talent from 1 lowering scores or Virtues "
            "or laying Flaws, always with a condition that ends it, even by "
            "chance. Same roll, Ease Factor 7, plus 3 to cap an Ability, 14 "
            "zero rolls, 21 always botch, 28 sicken slowly, 35 sicken fast; 7 "
            "a Characteristic point, Flaw point or Virtue point; condition "
            "+14 specific, +7 general, +0 sweeping; Magic Resistance; poetic "
            "justice. Gifts and Curses cannot counter each other. Spoken, "
            "within earshot; written, on an object near the victim. A failure "
            "by 7 or more may rebound.",
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
            "Svonhverfing, +4 (pp. 59-60): illusion, mainly sight, a Talent "
            "from 1; Personal, Concentration, Individual as a base. Stress "
            "die + Int + Svonhverfing + language + Potency + Aura, Ease Factor "
            "12: Size above -3 +1 a point; complex +3; moving +3, directed "
            "+6; sound +3 or +6; blur +3; invisibility +6 to +12, never "
            "truly hidden; Touch +3, Reach +6, Near +9. Speech takes 1-3 "
            "rounds; runes a minute or more, with +6 to hold it. Jotunn "
            "Affinity with Fire gives +3.",
            "Galdor Conjuring and Galdor Enchantment, +5 each (pp. 59-60): "
            "free to galdramen; others may buy them with the storyguide's "
            "leave, as partial training, and then initiate only Song Talents.",
            "Shapeshift and Transform, +5, +4 to trollsynir (pp. 60-61): "
            "separate Talents, not the narrower +3 Shapeshift of Ultima "
            "Thule. Stress die + Int + Talent + language + Potency + Aura. "
            "Shapeshift has Ease Factor 6 and alters oneself; failure bars "
            "that form until dawn; a return to one's own needs 3+. Transform "
            "has 10, plus Magic Resistance (Corpus Parma), and holds the victim "
            "until magic "
            "frees him, by level 20 from animal, 30 from plant, 35 from "
            "inanimate. No angelic, demonic, faerie or specific forms. Add "
            "for Size difference +1, +3, +6, +10, +15, +21; Reptile +1, Fish "
            "or Bird +3, Insect or Wood +6, Stone +10, Metal +15; man-made "
            "+6, complex +15; supernatural + Might; all equipment +6. A "
            "shifter keeps as many sure forms as his score, for those he "
            "beats without a roll. Second Sight and Sight of the True Form "
            "see through them. Clothing and small metal change with the "
            "target, larger metal falls away, and armour bursts on two Sizes' "
            "growth, +5 damage in scale, +10 in chain. Inanimate forms keep "
            "only touch and hearing.",
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
            UNCONVERTED,
            "A player's galdraman fills a magus slot and pays for Virtues as "
            "one (pp. 45-50, 54).",
            "Free Virtues (p. 46): Free Expression, Second Sight, "
            "Premonitions, Galdor Conjuring, Galdor Enchantment. Flaw: Major "
            "Deleterious Circumstances touching the ground. The Gift's "
            "social penalties apply; Gentle Gift or Blatant Gift may be "
            "taken.",
            "Starting Abilities: Galdor Wisdom 4, Premonitions 1, Singing 4, "
            "Speak West Norse 5, Second Sight 2, Legend Lore 2, two Song "
            "Talents of choice at 4 and 2, Bargain 2. Experience: Age + 10.",
            "Galdor Wisdom (pp. 46, 54): an Arcane Knowledge of the "
            "landvaettir, needing Galdor Conjuring or Enchanting. In a new "
            "country it falls to zero, returning a level a season. "
            "Specialties: Enchantment, Conjuring. Their magic takes auras as "
            "the landvaettir do (p. 32).",
            "Song Talents (p. 46): one for each kind of spirit; raised only "
            "by practice or experience, capped at Galdor Wisdom. A season of "
            "galdor gives 1 experience in Sing, Galdor Wisdom or that Song.",
            "The songs (p. 47): Yfel-galdor, curses, ill luck and wounds. "
            "Mal-galdor, persuasive or commanding speech. Hug-galdor, "
            "emotions and reading minds. Sig-galdor, battle, from keen "
            "weapons to courage. Lim-galdor, wounds and bones. Biarg-galdor, "
            "disease, guarding people, beasts and crops, and age. "
            "Orlog-galdor, future, past, far places, and hiding from such "
            "sight. Svart-galdor, the dead questioned or raised. Ol-galdor, "
            "driving off hostile beings, and protection from Curses. "
            "Brun-galdor, weather. Others may exist.",
            "Galdor Conjuring (pp. 46-48): set the level by Hermetic "
            "guidelines (the storyguide has the last word), duration "
            "Momentary or Concentration, no magnitude above the Song Talent. "
            "Non-ritual: 1 minute a magnitude. Ritual: 15 minutes and 1 pawn "
            "a magnitude to the spirit. No vis to boost. Stress die + Com + "
            "Sing + Galdor Wisdom + Song Talent + Aura must beat the level; "
            "halved on the ground. The result is the spirit's Might and "
            "Penetration. Concentration holds while he sings: Sta + Singing "
            "hourly, Ease Factor 6 + hours; a miss by up to 3 loses Fatigue, "
            "worse ends the song. Distractions use Int + Singing, +3 on the "
            "ground. Twice the level means a quality die of hours' work after "
            "the song ends.",
            "Bargaining (p. 48): longer durations are won from a landvaettir "
            "lord in the wilds with praise-songs, vis and service, a day a "
            "magnitude or up to a season. Reckon the level at D: Sun. Past a "
            "year it asks yearly vis, about double the magnitude, which good "
            "bargaining lowers. The conjuring roll is then made on the spot "
            "and the spirit fed. A missed tithe breaks the deal. Worked "
            "example: a level 30 path ward, 12 pawns bargained to 9, a yearly "
            "tithe and a favour owed.",
            "Health (pp. 48-49): no Instant effects. Lim- and biarg-galdor "
            "spirits add the magnitude to recovery rolls, attending at least "
            "12 hours in 24; a ritual conjuring with vis can rival Hermetic "
            "cures.",
            "Galdor Enchantment (p. 49): after a bargain, a spirit is bound "
            "while the item is made, with no lab. For life: as lesser "
            "enchanted items, low-Might spirits, Momentary or Concentration, "
            "+5 for Constant Use, no tithe, vis about as for the Hermetic item, total at double "
            "the level plus frequency. For one service: as a potion, lasting "
            "a year and a day, total at the level. Total: stress die + Com + "
            "Sing + Galdor Wisdom + Song Talent + Form and Effect Bonuses + "
            "Aura. The Craft score limits Galdor Wisdom and Song Talent; "
            "Scribe Runes may stand as Craft, on ready-made items too, but "
            "adds nothing. The Song Talent must equal the magnitude; no lab is "
            "needed, only the time to make the item, though a lifetime bargain "
            "usually takes two or three months, and the spirit, paid first, may "
            "set elaborate terms for the item's care and use.",
            "Longevity (pp. 49-50): with biarg-galdor, a lord grants it for "
            "a service besides vis, by anyone's hand. He then drinks mead "
            "with a pawn per decade of age and conjures a biarg spirit by "
            "ritual: a longevity potion of the conjuring total. Yearly mead "
            "renews it; it never fails, even on an aging result. Typical "
            "services: pull down a Christian shrine on magical ground, free a "
            "captive spirit, drive out a diabolist who tortures spirits, make "
            "a charm to clean a stream.",
            "Galdor Initiation (p. 50): learned from a lord through quests: "
            "Ars Notoria (at +3, Galdor Wisdom for Hermetic Theurgy), Curse, "
            "Enchanting Music, Galdor Songs (+2), Gift, Healer, Hamfarir, "
            "Potency, Svonhverfing. Needs Galdor Wisdom 3 per Virtue point "
            "(a supporter's will serve) and story experience of the Virtue's "
            "pyramid cost, 3 for a Song, 10 for Svonhverfing. Gained at 1.",
            "Twilight (p. 50): points as Hermetic magi, from longevity "
            "bargains and on magic botches. Stress dice send galdramen on the "
            "Long Hamfaring, Final Twilight, sooner than most magi.",
            "Hermetic Potential (p. 51): one who joins the Order learns "
            "Parma Magica but no Arts. Optionally, with the Mysteries, a "
            "crippled theurgic magic may be shared with a Hermetic theurgist.",
        ),
    )


def _schooled_galdramen(b: Builder) -> Neighbour:
    return b.faction(
        "Schooled Galdramen",
        faction="Hedge coven",
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
            UNCONVERTED,
            "Iceland's equivalent of Hedge Magic's Natural Magicians (pp. 45, "
            "51). Their sacred phrases are synthemata.",
            "They follow the Natural Magicians' rules (Hedge Magic, p. 40), "
            "but conjure magical spirits to make the effect. The only "
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
        faction="Other",
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
            UNCONVERTED,
            "A player's trollson fills a magus slot and pays for Virtues as "
            "one (pp. 45, 52-54).",
            "Free (p. 52): Potency, Shapeshift, Giant Blood; Sheltered "
            "Upbringing, and usually the Blatant Gift, which Etin Bride can "
            "ease, neither counting toward the Flaw total. Choose one of "
            "Curse, Gift, Transform, Jotunn Affinity or Svonhverfing. Up to "
            "10 points each of balancing Virtues and Flaws besides.",
            "Starting Abilities: Speak Jotunn 5, Shapeshift 4, a magical "
            "Talent 3, Trollson Lore 2, Trollskap Wisdom 4, Speak West Norse "
            "3, Survival 3, Potency 2. Experience: Age + 10.",
            "Trollskap (p. 52): magic of Exceptional Talents, always on stress "
            "dice, unable to touch spirits or the dead. Necromancer or "
            "Summoner may be had, but not as trollskap: only at creation or "
            "by story. Once initiated, a trollson can never learn Galdor "
            "Conjuring, Enchantment or Hermetic magic.",
            "Afflictions (pp. 52-53): botching a primary magical Talent gives "
            "a Trollskap Affliction at 0, or +1 to one, from Horns, Fangs, "
            "Claws, Blue Skin, Obsession, Rage, Icy Aura and the like; five "
            "at most, 6 at most each. So do External Soul healing botches and "
            "initiation zeroes. With five at 6, further points go to a Troll "
            "trait, and at +6 the character flees, lost. Giants are immune. "
            "Non-player trollsynir gain about a point each five years.",
            "Magic Resistance (p. 53): the sum of the primary Talents held at "
            "creation, three at most, always Shapeshift, +20 with an External "
            "Soul. Example: 17 + 18 + 16 + 20 = 71.",
            "Trollskap Initiation (p. 53): a season or more among Jotunn "
            "spirits. Stress die + Int + Trollskap Wisdom, no aura, Ease "
            "Factor 10 a Virtue point, Wisdom 3 a Virtue point. Each further "
            "season adds a stress die. Gained at 1. A zero gives an "
            "Affliction level and a botch check; a botch restarts it. "
            "Available: Curse, Divination, Dousing, Empathy, Enchanting "
            "Music, Entrancement, External Soul, Gift, Hamfarir, Healer, Hex, "
            "Jotunn Affinity (of their clan), Magic Sensitivity, Premonitions, "
            "Second Sight, Shapeshift, Svonhverfing, Transform, Visions.",
            "External Soul, +4 (pp. 53-54): initiation only. The soul goes "
            "into an object, for good; while it is whole he cannot be killed, "
            "dismembered, burned or aged, only incapacitated, but any scratch "
            "to it kills him. Recovery totals under 9 lose the next roll, a "
            "botch two and adds an Affliction. Magic Resistance +20. It hides "
            "the arcane connection: a Hermetic ritual to find it must be "
            "researched, beat his Magic Resistance and have him present.",
            "Speak Jotunn (p. 54): the giants' magical language, near to "
            "Pictish; a gruagach and a trollson converse at -1. Adds with "
            "Potency to many Talents; needs Potency to learn. Specialties: "
            "Insults, Praise.",
            "Scribe Runes (p. 54): needs Potency. The runes are cut, rubbed "
            "with blood and spoken. A magical language for Talents Potency "
            "aids, except Jotunn Affinity; slower than speech, with other "
            "advantages. Specialties: a Talent.",
            "Trollskap Wisdom (p. 54): for initiation and new Talents. "
            "Specialties: Curses, Divinations, Illusions.",
            "Trollson Lore (p. 54): knows famous trollsynir, serves as Giant "
            "Lore, and tells a clan. Specialties: jotunn, a Clan, female "
            "magicians.",
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
        faction="Other",
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
        faction="Other",
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
        realm="Magic",
        summary=paragraphs(
            "Women magicians, among the volur, each of whom can borrow her "
            "fylgja's body and go abroad in it. The hreppur allows them only "
            "half the fee of a galdraman, half an ounce a day.",
        ),
        rules="The book leaves their ways to Ultima Thule. Pp. 28, 45, 55.",
    )


def _order_of_odin(b: Builder) -> Neighbour:
    return b.faction(
        "The Order of Odin",
        faction="Other",
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
