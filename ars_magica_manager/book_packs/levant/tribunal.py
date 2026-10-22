"""The Levant Tribunal itself: the record and its summary (the Tribunal
of the East and its refounding, the young and violent Order of the
Levant, its five stances, the meetings in tents at Domus Pacis, the
Guernicus chair), the Levant as the Tribunal's region with the shared
regions set inside it, the Peripheral Code with the Treaty of Baghdad,
its ten-year term and its two renewals, the docket for 1221 (the
renewal motion and Foothold's charge against 'Umar), the past meetings
in the Diary, the Islamic Tradition as a faction, and the two magi who
belong to no covenant: Scipio, the presiding quaesitor, and Arash, who
swore the Treaty of Barcelona in place of the Oath (build); then the
Praeco and the Presiding Quaesitor, the Islamic Tradition's members and
the Tribunal's totals (finish); and Scipio's and Arash's generated stats
(stats).

Keys: places["levant"]; world["islamic_tradition"]; magi["scipio"] and
magi["arash"]. The Praeco is magi["tau"] (major_covenants), and the
Islamic Tradition's members are magi["umar"] (major_covenants) and
whichever of MEMBERS the parts make."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...tribunal_packages import levant as package
from ..builder import paragraphs
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Character
    from . import Levant

NAME = "The Levant Tribunal"
#: The book's own counts: fifteen covenants and fifty-nine magi, about
#: forty-eight of them in covenants and the rest wanderers and hermits.
COVENANTS_TOTAL = 15
MAGI_TOTAL = 59
MEETING_PLACE = "Domus Pacis"

#: The covenants as the parts name them, for the motion's parties.
EMBASSY = "The Hermetic Embassy"
DOMUS_PACIS = "Domus Pacis"
AEDES_VERITATIS = "Aedes Veritatis"
FOOTHOLD = "Foothold"
PARA_BELLI = "Para Belli"
TRUE_CROSS = "The True Cross"

SUMMARY = paragraphs(
    "The Order's easternmost Tribunal, reaching from Trebizond and the "
    "Alan lands of the Caucasus through Lesser Armenia, Syria and the "
    "four Latin states to Cyprus, Egypt and Sinai, and east to Baghdad. "
    "It began as the Tribunal of the East, two covenants (Urbs Rubra at "
    "Petra in 802 and Urania in the Caucasus in 806) founded by Harun "
    "al-Rashid's leave, won through Charlemagne's embassies, and "
    "reckoned a Tribunal in 832. Magi of every House came after the "
    "First Crusade, staked out territories over the old covenants' "
    "protests, and the Grand Tribunal of 1129 recognised the refounded "
    "Tribunal under its new name.",
    "A young Tribunal in every sense. It is dangerous, so its magi are "
    "young and few live to old age; few covenants pass spring or "
    "summer, and one that reaches autumn is honoured for it. The Order's "
    "hold is slight and a magus can stay independent with ease. For most "
    "of a century magi meddled in the wars, fought the Muslims' mages, "
    "and turned on one another in Wizard Wars over the land's riches, "
    "with quaesitores as deep in it as anyone, until the Treaty of "
    "Baghdad of 1193 brought a hard peace. There are fifteen covenants "
    "and fifty-nine magi, about forty-eight of them in covenants. "
    "Flambeau, Verditius, Criamon and Jerbiton are the commonest Houses, "
    "then Tremere and Tytalus; Merinita is rarest, for want of faeries, "
    "and few of the land's own wizards join Ex Miscellanea.",
    "Its questions. Crusade and jihad first: the Treaty forbids both, "
    "the quaesitores enforce it as best they can, and others hunt for "
    "loopholes or meddle unseen. Each covenant takes a stance, which "
    "its summary gives first: Crusader (Foothold, Para Belli and their "
    "allies, who want war on the Muslims), counter-Crusader (Aedes "
    "Veritatis and its allies, who want war on Foothold), mediator (the "
    "Hermetic Embassy, Domus Pacis and the quaesitores, who keep the "
    "Treaty), trader, or aloof. Then the border with Thebes, settled "
    "on paper and quick to flare; trade with Rome and, against the "
    "quaesitores' efforts, with merchants, churchmen and lords, chiefly "
    "by Jerbiton and Verditius magi; and the old wisdom of the East, "
    "which Criamon and Jerbiton magi seek among the ruins and from the "
    "land's mages and Sufis.",
    "The meeting. Since Tau of Flambeau became Praeco the Tribunal has "
    "met every seven years at his covenant, Domus Pacis, a khan north "
    "of Jerusalem: tents go up outside for the visitors, the gate is "
    "shut to all but magi, and the business is done from a ring of "
    "chairs in the courtyard. The last meetings were in 1207 and 1214, "
    "and the next, in 1221, must vote on renewing the Treaty; the book "
    "gives no season, so summer is assumed. The chair must be a "
    "quaesitor of House Guernicus, a rule Aurora proposed so that she "
    "would never have to preside and be called partial; Scipio of "
    "Guernicus holds it now and keeps no covenant. Votes are one to a "
    "magus, which gives Heliobus of the Pyramids twelve.",
    "Playing in the Levant. The book offers the troupe a part as "
    "mediators, between the Tribunal's factions or between the Order "
    "and the caliph and the Ayyubids: whether they succeed or not, they "
    "will make friends and enemies inside the Order and out.",
)

SECRETS = paragraphs(
    "The book's own guess at what follows 1220: the Treaty fails, "
    "perhaps once the True Cross is lost, and the Tribunal joins the "
    "war; or it holds until the Mongols come, and then the Mamluks "
    "drive the Order from the mainland by 1291, leaving only Cyprus.",
    "The Praeco's office should strictly be Wraith's, of Urbs Rubra, "
    "the elder of the Tribunal's two eldest; the quaesitores ruled Tau "
    "the eldest in 1207 only because no one could reach her.",
)

#: The Peripheral Code: (year or None, title, what it says).
RULINGS: tuple[tuple[int | None, str, str], ...] = (
    (
        1193,
        "The Treaty of Baghdad",
        "Made between the Order in the Levant and the caliph's court, with "
        "Salah al-Din's mages and their Ayyubid heirs, and forced on the "
        "Levant's magi at the meeting of 1193 by quaesitores from "
        "Magvillus. No magus may take any part in Crusade or jihad, for "
        "either side; the Order's fighting with the Muslims' mages is "
        "over; and a magus found meddling in the wars is severely "
        "punished. Aurora of Jerbiton made it, treating with the caliph, "
        "Salah al-Din and their mages from 1183. The Order of Suleiman "
        "as a body never signed it.",
    ),
    (
        1193,
        "The Treaty's term",
        "Muslim law lets a truce last ten years at most, so the Treaty "
        "lapses each decade unless the Tribunal renews it, and it is "
        "debated at every meeting. Each renewal is voted at the last "
        "meeting before the Treaty lapses; the present term runs to 1223, "
        "and its renewal is before the meeting of 1221.",
    ),
    (
        1200,
        "The Treaty renewed for 1203",
        "The meeting of 1200 renewed the Treaty for ten years from 1203.",
    ),
    (
        1207,
        "The Treaty renewed for 1213",
        "The meeting of 1207 renewed the Treaty, by a narrow vote, for ten "
        "years from 1213.",
    ),
    (
        None,
        "The chair",
        "The quaesitor who presides at a meeting of the Tribunal must be "
        "of House Guernicus; a quaesitor of any other House may not. "
        "Aurora of Jerbiton proposed the rule.",
    ),
    (
        1207,
        "The Praeco",
        "Fade and Wraith of Urbs Rubra, the eldest magi, had not been seen "
        "for years and could not be reached, so the quaesitores ruled that "
        "Tau of Flambeau be held the eldest, and Praeco.",
    ),
    (
        None,
        "The stone of Aedes Veritatis",
        "Some covenants asked whether Aedes Veritatis's sale of quarry "
        "stone to Damascus aided the war, since the stone might build "
        "walls. The quaesitores ruled the trade lawful: the stone is not "
        "magical, and was not made for war.",
    ),
    (
        None,
        "Enchanted devices",
        "Selling enchanted devices to mundane lords is interference in "
        "mundane affairs, and forbidden.",
    ),
    (
        None,
        "The border with Thebes",
        "After 1204 Theban magi followed the Byzantine refugees east and "
        "Thebes claimed more of Asia Minor for them; Aurora and other "
        "quaesitores of both Tribunals settled the quarrel short of war. "
        "The Empire of Nicaea belongs to the Theban Tribunal and the "
        "Empire of Trebizond to the Levant. Both sides have agreed to "
        "differ, and many are unhappy with it.",
    ),
    (
        1178,
        "The priests of the Pyramids",
        "Heliobus Magister of Bonisagus brought the twelve priests of "
        "Thoth and Anubis in their temple at Giza into House Ex "
        "Miscellanea, under the Code's protection, which ended the "
        "Hermetic raids on their temple.",
    ),
    (
        None,
        "Sahirs in the Order",
        "A sahir may join the Order as any hedge wizard does, through "
        "House Ex Miscellanea, swearing the Oath and taking the Parma "
        "Magica.",
    ),
)


def build(levant: Levant) -> None:
    b = levant.b
    levant.tribunal = tribunal = b.tribunal(
        NAME,
        package=package.LEVANT.key,
        summary=SUMMARY,
        secrets=SECRETS,
        meets_every=7,
        next_year=1221,
        next_season="Summer",
        meeting_place=MEETING_PLACE,
        covenants_total=COVENANTS_TOTAL,
        magi_total=MAGI_TOTAL,
    )
    _region(levant)
    for year, title, says in RULINGS:
        b.ruling(tribunal, title, year, says)
    _docket(levant)
    _meetings(levant)
    _islamic_tradition(levant)
    _scipio(levant)
    _arash(levant)


# -- the region --


def _region(levant: Levant) -> None:
    b = levant.b
    levant.places["levant"] = region = b.place(
        "The Levant",
        known="In the Order",
        summary=paragraphs(
            "The lands at the eastern end of the Mediterranean and behind "
            "them, as far as the Order's Levant Tribunal reaches: the four "
            "Latin states on the coast and Cyprus, Lesser Armenia, Syria, "
            "Egypt and Sinai, Asia Minor east of Nicaea, the Alan lands "
            "of the Caucasus, Georgia, Greater Armenia and Iraq. Muslims, "
            "eastern Christians of a dozen churches, Jews and Latin "
            "settlers live side by side, and the Latin states hold only "
            "a coastal strip since Salah al-Din's victories.",
        ),
    )
    # The regions shared with The Cradle and the Crescent sit in the
    # Levant on this pack's map.
    for key in ("iraq", "georgia", "greater_armenia"):
        shared = levant.places.get(key)
        if shared is not None and shared.place_id is None:
            shared.place_id = region.id
    mosul, iraq = levant.world.get("mosul"), levant.places.get("iraq")
    if mosul is not None and iraq is not None and mosul.place_id is None:
        mosul.place_id = iraq.id


# -- the docket for 1221 --


def _docket(levant: Levant) -> None:
    b = levant.b
    tribunal = levant.tribunal
    assert tribunal is not None
    b.case(
        tribunal,
        "Renew the Treaty of Baghdad for 1223",
        kind="motion",
        brought_by=f"{EMBASSY}, {DOMUS_PACIS} and {AEDES_VERITATIS}",
        against=f"{FOOTHOLD}, {PARA_BELLI} and {TRUE_CROSS}",
        charge=paragraphs(
            "That the Tribunal renew the Treaty of Baghdad for ten years "
            "from 1223, when its present term ends. The mediators bring "
            "it; the counter-Crusaders of Aedes Veritatis back it, as the "
            "Treaty shields the Muslims. The Crusader covenants want it "
            "rejected this time so that they can help the Crusade at "
            "Damietta, and both sides are hunting for votes. The aloof "
            "covenants are undecided, and Heliobus's twelve votes may "
            "settle it.",
            "If it passes, give the ruling a term of seven years: it then "
            "ends at the meeting of 1228, the last before the Treaty "
            "lapses again in 1233, and comes back on the docket in time.",
        ),
        filed_year=1220,
        filed_season="Spring",
        notice_given=True,
        evidence="The Treaty of Baghdad and its two renewals\n"
        "The Crusade at Damietta, and the strain it puts on the peace",
    )
    b.case(
        tribunal,
        "The slaying of a Crusader magus",
        kind="charge",
        brought_by=FOOTHOLD,
        against=f"Sharaf al-Din 'Umar of {AEDES_VERITATIS}",
        charge="Early in his career 'Umar fought and killed a Crusader "
        "magus who had attacked him. He would plead self-defence, but no "
        "one else saw it, so the slaying of a sodalis may be laid against "
        "him as a High Crime. Foothold has learnt of it and asks that he "
        "be Renounced, which would cost the counter-Crusaders their "
        "leader.",
        filed_year=1220,
        filed_season="Spring",
        notice_given=False,
        evidence="None witnessed",
    )


# -- the meetings before 1221 --

#: (year, title, details): the meetings the book dates or implies.
MEETINGS: tuple[tuple[int, str, str], ...] = (
    (
        1193,
        "The Treaty of Baghdad accepted",
        "Quaesitores from Magvillus made the Tribunal accept the Treaty "
        "Aurora had negotiated, ending the Order's war with the Muslims' "
        "mages. Crusading magi could no longer excuse breaches of the "
        "Code as defence, nor counter-Crusaders as protecting the "
        "Muslims.",
    ),
    (
        1200,
        "The Treaty renewed",
        "The meeting renewed the Treaty for ten years from 1203.",
    ),
    (
        1207,
        "The Treaty renewed, and a Praeco ruled",
        "The meeting renewed the Treaty for ten years from 1213, barely. "
        "With Fade and Wraith out of reach, the quaesitores ruled Tau of "
        "Flambeau the eldest, and the Tribunal has met at Domus Pacis "
        "since.",
    ),
    (
        1214,
        "A meeting with no renewal",
        "The Treaty was not due until 1223, and is renewed only at the "
        "last meeting before it lapses, so this meeting had nothing to "
        "renew; the debate went on all the same.",
    ),
)


def _meetings(levant: Levant) -> None:
    tribunal = levant.tribunal
    assert tribunal is not None
    for year, title, details in MEETINGS:
        levant.b.event(tribunal, year, title, details, season="Summer")


# -- the Islamic Tradition --

#: The magi of the Islamic Tradition, by key, with the link's note; the
#: parts that make them are named in their keys' docstrings.
MEMBERS: tuple[tuple[str, str], ...] = (("umar", "Its leading member"),)


def _islamic_tradition(levant: Levant) -> None:
    levant.world["islamic_tradition"] = levant.b.faction(
        "The Islamic Tradition",
        faction="Other",
        summary=paragraphs(
            "Not a society but a strand running through the Order since "
            "its first settlers reached the Levant: magi of any House or "
            "faith who have worked Islamic ideas into Hermetic magic to "
            "make it more supple, chiefly by using the Islamic ranges, "
            "durations and targets. Most are Muslims and most belong to "
            "Jerbiton, Criamon or Ex Miscellanea. Its Virtues (Islamic "
            "Magic, Interfaith Magic) and Flaws (Poorly-Meshed "
            "Hermetic-Islamic Magic, The Faerie Problem) are in the "
            "catalog, from Secrets in Sand.",
            "In these times most of its magi keep their heads down, "
            "though a few work openly against the Crusade and the "
            "crusading magi. Its members are often suspected of "
            "counter-crusading, nearly always without cause. A spell may "
            "give the Islamic parameters as typed; the book's table "
            "matching them to Hermetic ones, and its rule that adapting "
            "them for other magi is a major breakthrough, stay in the "
            "book.",
        ),
    )


# -- the magi of no covenant --


def _scipio(levant: Levant) -> None:
    levant.magi["scipio"] = levant.b.magus(
        "Scipio",
        covenant=None,
        house="house_guernicus",
        age=96,
        summary=paragraphs(
            "Scipio of Guernicus, filius Rognvald, the Tribunal's senior "
            "quaesitor and so the chair of its meetings, which gives him "
            "great power. He keeps no covenant and spends his time "
            "travelling the Tribunal. Ninety-six, he looks to be in his "
            "sixties: strongly built, with short grey hair and a beard, "
            "always in robes of grey. A master of Intellego, above all "
            "Intellego Mentem, he knows most of the common Intellego "
            "spells of the other Forms too.",
            "The book leaves his character to the troupe, as three "
            "readings, none chosen here: a rigid Traditionalist who "
            "enforces the Code to the letter; a Transitionalist who lets "
            "reason come before law; or a corrupt judge in some "
            "covenant's pay.",
        ),
    )


def _arash(levant: Levant) -> None:
    levant.magi["arash"] = levant.b.magus(
        "Arash",
        covenant=None,
        house="",
        age=None,
        summary=paragraphs(
            "Once the apprentice of Rachel of Criamon, and now outside the "
            "Order. A spiritual crisis in his apprenticeship led him, at "
            "his induction in 1213, to refuse the Oath of Hermes and "
            "swear instead the Treaty of Barcelona, the pact of peace "
            "between Hermetic magi and Kabbalists. Magi threatened him, "
            "and House Criamon spirited him away to Baghdad, where he "
            "studies the Kabbalah with the city's rabbis. He finds his "
            "Hermetic and Kabbalistic gifts hard to reconcile, and his "
            "progress is uneven.",
            "Kabbalah (Fourth Edition) says more of him.",
        ),
    )


# -- after every part has built --


def finish(levant: Levant) -> None:
    b, tribunal = levant.b, levant.tribunal
    assert tribunal is not None
    saga = b.saga
    praeco: Character | None = levant.magi.get("tau")
    quaesitor: Character | None = levant.magi.get("scipio")
    tribunal.praeco_id = praeco.id if praeco is not None else None
    tribunal.quaesitor_id = quaesitor.id if quaesitor is not None else None

    tradition = levant.world["islamic_tradition"]
    for key, note in MEMBERS:
        member = levant.magi.get(key)
        if member is not None:
            b.link(tradition, "characters", member, note)

    arash, baghdad = levant.magi.get("arash"), levant.world.get("baghdad")
    if arash is not None and baghdad is not None:
        b.link(arash, "places", baghdad, "Lives among its Jews")

    resident = [c for c in saga.covenants if c.tribunal_id == tribunal.id]
    ids = {c.id for c in resident}
    named = [m for m in saga.characters if m.type == "magus" and m.covenant_id in ids]
    tribunal.covenants_total = max(COVENANTS_TOTAL, len(resident))
    tribunal.magi_total = max(
        MAGI_TOTAL, len(named) + sum(c.unnamed_magi for c in resident)
    )


# -- generated stats --

#: The two magi of no covenant, whom the book sketches without stats.
PROFILES: dict[str, Profile] = {
    "scipio": Profile(
        strong="int per",
        weak="dex qik",
        arts={"In": 10, "Me": 8, "Vi": 4, "Co": 3, "An": 2, "Te": 2},
        abilities={
            "Code of Hermes": (6, "the Peripheral Code"),
            "Folk Ken": (4, "magi"),
            "Area Lore: Levant Tribunal": (4, "covenants"),
            "Intrigue": (3, "Hermetic politics"),
            "Ride": 2,
        },
        virtues=[
            "Hermetic Prestige",
            "Clear Thinker",
            "Driven (Minor)",
        ],
        native="Italian",
    ),
    "arash": Profile(
        strong="int per",
        weak="str",
        arts={"In": 6, "Vi": 5, "Me": 5, "Cr": 3},
        abilities={
            "Enigmatic Wisdom": (4, "the Kabbalah"),
            "Concentration": (3, "study"),
            "Dead Language: Hebrew": (3, "scripture"),
            "Living Language: Arabic": 3,
        },
        virtues=["Outsider (Major)"],
        age=33,
        native="Persian",
    ),
}


def stats(levant: Levant) -> None:
    for key, profile in PROFILES.items():
        character = levant.magi.get(key)
        if character is not None:
            apply(levant.b, character, profile)
