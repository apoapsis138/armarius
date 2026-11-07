"""The four major covenants and their magi (B&S ch08, SiS), rebuilt in
Definitive Edition terms (L8): full covenant records with the book's
site, season, founding, aura, members, Aegis, library sizes and summae,
vis stores and yearly vis, income, and allies, enemies and contacts;
Boons and Hooks chosen from the catalog as text lines in what_matters;
the Fourth Edition point totals dropped.

Keys: covenants["aedes_veritatis"] (Aedes Veritatis, Bayt al-Haqq, on
its mountain east of Damascus; Summer; 1112; Magic 4; Aegis 35; "Size:
4 magi" with three named, so one unnamed), covenants["domus_pacis"]
(Domus Pacis, Dar al-Salam, the khan north of Jerusalem; Summer; 1169;
Magic 1; Aegis 30; one unnamed; the Tribunal's meeting place, its tents
and ring of chairs in its summary, L5), covenants["foothold"] (Foothold,
on its hill between Acre and Tyre; Spring; 1188; Magic 2; Aegis 15) and
covenants["embassy"] (The Hermetic Embassy, in al-Qurayya in Baghdad;
Spring; 1193; Divine 2; Aegis 35; affiliated with Guernicus through
Magvillus with no Guernicus member, L27; the Suhhar distrusts it, L3).
Each summary opens with its stance (L4). Their sites are places
["aedes_veritatis_mountain"] (in places["syria"]),
["dar_al_salam_khan"] (in places["syria"]), ["foothold_hill"] (in
places["jerusalem_kingdom"]) and ["al_qurayya"] (in world["baghdad"]),
each set inside its region in finish if the region was not yet made.

The named summae are Book records of their covenants (L9): nine at
Aedes Veritatis, eight at Domus Pacis, five at Foothold, with the
Qur'an at Aedes Veritatis as an Ability Summa on Theology: Islam (level
and quality blank, an authority). Allies, enemies and contacts between
the covenants are links with a note, made in finish (L8); the unnamed
spring covenants are in what_matters only. Suggested vis sources (not
in the book) are in each covenant's notes (L10).

Magi (sketches; the eight printed blocks are stats_magi.py's):
magi["umar"] (Sharaf al-Din 'Umar), ["amber"] (Amber the Golden),
["wardat"] (Wardat al-Quds) at Aedes Veritatis; ["tau"] (the Praeco),
["felix"], ["esther"] at Domus Pacis; ["guillaume"] (Guillaume de
Bourne), ["rufus"] (Rufus de Clary) at Foothold; ["aurora"] (Aurora
Borealis; her apprentice Macha named in her summary only, L2),
["spiral"] at the Embassy. The eight printed magi are given their
printed ages, as are Tau and Aurora (L16), who
are given generated stats here in stats(). Secrets in secrets= ('Umar's
service to the Ayyubids, Esther's sales and her vis source, Rufus's
hoard and his fear, the spies in Domus Pacis, the scrying devices in
Foothold, the secret war on Foothold)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...models.world import FULL
from ..builder import joined_lines, paragraphs, titled
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Covenant, Neighbour, Tribunal
    from ..builder import Builder
    from . import Levant

JERBITON = "house_jerbiton"
TREMERE = "house_tremere"
EX_MISCELLANEA = "house_ex_miscellanea"
FLAMBEAU = "house_flambeau"
GUERNICUS = "house_guernicus"
VERDITIUS = "house_verditius"
TYTALUS = "house_tytalus"
CRIAMON = "house_criamon"

KNOWN_ORDER: dict[str, Any] = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL: dict[str, Any] = {"status": "Known", "known": "In the Tribunal"}

#: Each covenant site this part makes, by key, with the key of the
#: region (or town) it stands in.
SITES: dict[str, str] = {
    "aedes_veritatis_mountain": "syria",
    "dar_al_salam_khan": "syria",
    "foothold_hill": "jerusalem_kingdom",
    "al_qurayya": "baghdad",
}

#: Links between covenants (from, to, note): the allies, enemies and
#: contacts the book names, made in finish.
COVENANT_LINKS: tuple[tuple[str, str, str], ...] = (
    ("aedes_veritatis", "foothold", "Enemy: its secret war"),
    ("aedes_veritatis", "embassy", "Enemy: political attacks"),
    ("foothold", "aedes_veritatis", "Enemy: the counter-Crusade's leader"),
    ("foothold", "embassy", "Enemy: political attacks"),
    ("domus_pacis", "embassy", "Ally"),
    ("embassy", "domus_pacis", "Contact"),
    ("embassy", "foothold", "Enemy"),
    ("embassy", "aedes_veritatis", "Enemy"),
)


def _tribunal(levant: Levant) -> Tribunal | None:
    if levant.tribunal is not None:
        return levant.tribunal
    return next(iter(levant.b.saga.tribunals), None)


def _region(levant: Levant, key: str) -> Neighbour | None:
    return levant.places.get(key) or levant.world.get(key)


def _site(levant: Levant, key: str, name: str, **kw: Any) -> Neighbour:
    """A covenant's site, inside its region when that is made already."""
    place = levant.b.place(name, inside=_region(levant, SITES[key]), **kw)
    levant.places[key] = place
    return place


def build(levant: Levant) -> None:
    tribunal = _tribunal(levant)
    if tribunal is None:
        # The Tribunal part makes the Tribunal first; without it there is
        # nothing for a covenant to belong to.
        return
    b = levant.b
    _sites(levant)
    _aedes_veritatis(levant, b, tribunal)
    _domus_pacis(levant, b, tribunal)
    _foothold(levant, b, tribunal)
    _embassy(levant, b, tribunal)


# ------------------------------------------------------------------ sites


def _sites(levant: Levant) -> None:
    _site(
        levant,
        "aedes_veritatis_mountain",
        "The Mountain of Aedes Veritatis",
        aura=4,
        summary=(
            "A steep peak some five miles east of Damascus, climbed by a "
            "single winding track on its western face, crowned by the "
            "sandstone fortress of Aedes Veritatis. A quarry near by gives "
            "the covenant its stone. The mountain air is clean and keeps "
            "those who live there hale. Magic aura 4."
        ),
        **KNOWN_TRIBUNAL,
    )
    _site(
        levant,
        "dar_al_salam_khan",
        "The Khan of Dar al-Salam",
        aura=1,
        summary=(
            "A roadside inn for merchants under a cliff about eleven miles "
            "north of Jerusalem, on one of the quieter trade roads: a "
            "walled courtyard ringed by two storeys of rooms, a smithy and "
            "stores, with caves hidden beneath it. It is the covenant of "
            "Domus Pacis and the meeting place of the Levant Tribunal. "
            "Magic aura 1."
        ),
        **KNOWN_ORDER,
    )
    _site(
        levant,
        "foothold_hill",
        "Foothold's Hill",
        aura=2,
        summary=(
            "A hill about ten miles inland, between Acre to the south-west "
            "and Tyre to the north-east. Three of its sides are steep and "
            "dangerous; the eastern slope is gentle and wooded, and the "
            "covenant has only half-heartedly begun to clear it. Magic "
            "aura 2."
        ),
        **KNOWN_TRIBUNAL,
    )
    _site(
        levant,
        "al_qurayya",
        "Al-Qurayya",
        realm="Divine",
        aura=2,
        summary=(
            "A quarter of Baghdad near the caliph's palace, where the "
            "Hermetic Embassy keeps its house. The Dominion lies over it "
            "at 2, as over most of the city's quarters."
        ),
        **KNOWN_ORDER,
    )


# ------------------------------------------------------- Aedes Veritatis


def _aedes_veritatis(levant: Levant, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "Counter-Crusader: the leader of the magi who would fight the "
        "Crusader covenants for the Muslims' sake.",
        "Bayt al-Haqq in Arabic, the House of Truth, a name that also "
        "means the house of what is right. A sandstone fortress on a "
        "mountain top east of Damascus, founded in 1112 by Maryam "
        "al-Dimashqiyya, a young Jerbiton maga of that city, as a "
        "stronghold for the magi who had taken the Muslims' side against "
        "their Hermetic brothers. Good management and quick work on its "
        "walls and its friendships made it the bastion of the "
        "counter-Crusade. Maryam fell at Hattin in 1187, with most of the "
        "covenant's magi, and her filius Sharaf al-Din 'Umar has led it "
        "since. Its device is a stylised house holding the Arabic word "
        "haqq.",
        "The fortress was built for war: thick stone walls with arrow "
        "slits and battlements, a watchtower jutting from the north-west "
        "corner that also houses the magi, and a great hall in the middle "
        "where the grogs train more often than anyone feasts. Its "
        "neighbours take it for the seat of some reclusive emir, a part "
        "'Umar plays when he must. Its income is stone from a quarry near "
        "by, sold in Damascus, where it buys most of what it needs; some "
        "covenants asked whether stone for walls was help in the war, and "
        "the quaesitores ruled the trade lawful.",
        "Magi: 'Umar, Amber the Golden of Tremere and the sahira Wardat "
        "al-Quds; the book counts four, and names no fourth.",
    )
    what_matters = joined_lines(
        "Stance: counter-Crusader",
        "Vis stores: 150 pawns of every Art (Creo 12, Intellego 7, Muto 13, Perdo 6, Rego 10, Animal 12, Aquam 10, Auram 11, Corpus 14, Herbam 5, Ignem 15, Imaginem 5, Mentem 5, Terram 11, Vim 14)",
        "Vis: about 40 pawns a year (Animal 6, Aquam 6, Auram 3, Corpus 8, Ignem 7, Terram 4, Vim 6), from sources the book does not place",
        "Library: 1800 levels of spells, strongest in Animal and Corpus (written in Latin) and the four elements (written in Arabic)",
        "Library: Hermetic books worth 630 points, nine summae among them (see the library records), the rest in Latin and Arabic; mundane books worth 300 points, with a Qur'an and works on Islam and on the region's geography and history",
        "Income: the quarry's stone, sold in Damascus; a surplus of about 50 pounds of silver a year, with some 500 pounds' worth in store",
        "Covenfolk: 20 specialists and 150 grogs (40 servants, 110 men-at-arms)",
        "Enchantments: five swords holding a constant Edge of the Razor (level 20) for favoured grogs, and other devices worth about 100 levels",
        "Laboratories: four, all well equipped",
        "Allies: two emirs of middling power in Damascus, and two spring covenants the book does not name",
        "Enemies: Foothold above all; two spring covenants and one of middle age, unnamed",
        "Contacts: a minor emir in Jerusalem, and a merchant",
        "Boon: Natural Fortress (a peak reached by one track from the west)",
        "Boon: Healthy Feature (the clean mountain air; +1 on aging rolls)",
        "Boon: Veteran Fighters (110 men-at-arms)",
        "Boon: Local Ally (the emirs of Damascus)",
        "Boon: Secondary Income (the quarry)",
        "Hook: Infamous (a danger to the peace, in the quaesitores' eyes)",
        "Hook: Rival (Foothold and the Crusader covenants)",
        "Hook: Hermetic Politics (the counter-Crusade, and the Treaty's renewal)",
        "Hook: Dark Secret (see Secrets)",
    )
    notes = paragraphs(
        "Its people. The magi are three: 'Umar, the leader; Amber, his "
        "friend and second; and Wardat, the youngest, whom 'Umar "
        "sponsored into the Order. Of the twenty specialists and 150 "
        "grogs, most are men-at-arms, and the covenant has the air of a "
        "garrison.",
        "Suggested vis sources (not in the book), for the storyguide to "
        "use, change or ignore: the cinders of a thorn bush on the summit "
        "that lightning strikes each summer (Ignem, 4 pawns); a seam of "
        "red stone in the quarry that a mason's chisel rings on like a "
        "bell (Terram, 3 pawns); and the bones of the eagles that nest on "
        "the cliff below the tower, gathered when they die (Animal, 2 "
        "pawns).",
    )
    hidden = [
        titled(
            "The secret war",
            "Since the Treaty of Baghdad, 'Umar, his sodales and their allies "
            "inside and outside the Order have kept up a secret war on the "
            "Crusader covenants, on Foothold above all. The quaesitores have "
            "not found them out.",
        ),
        titled(
            "'Umar's double loyalty",
            "'Umar serves the Ayyubid sultans as well as the Order, a thing "
            "even Amber and Wardat do not know. If it came out, the trade "
            "ruling would be the least of Aedes Veritatis's worries: he "
            "would likely be Renounced.",
        ),
        titled(
            "Spies in Domus Pacis",
            "Aedes Veritatis keeps spies in Domus Pacis, who report "
            "everything that passes there.",
        ),
    ]
    covenant = b.covenant(
        "Aedes Veritatis",
        tribunal=tribunal,
        founded=1112,
        place=levant.places["aedes_veritatis_mountain"],
        aura=4,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        secrets=hidden,
        unnamed_magi=1,
        detail=FULL,
        season="Summer",
        aegis=35,
    )
    levant.covenants["aedes_veritatis"] = covenant
    for art, level, quality, language in (
        ("Creo", 20, 10, "Latin"),
        ("Muto", 15, 8, "Latin"),
        ("Rego", 21, 9, "Latin"),
        ("Corpus", 22, 10, "Latin"),
        ("Animal", 18, 11, "Latin"),
        ("Aquam", 14, 7, "Arabic"),
        ("Auram", 13, 6, "Arabic"),
        ("Terram", 15, 6, "Arabic"),
        ("Ignem", 16, 7, "Arabic"),
    ):
        _summa(b, covenant, "Aedes Veritatis", art, level, quality, language)
    b.book(
        covenant,
        "The Qur'an of Aedes Veritatis",
        "Ability Summa",
        ability="Theology: Islam",
        language="Arabic",
        description=(
            "A copy of the Qur'an, which the book makes an authority on "
            "Islamic theology and Islamic law; no level or quality is "
            "given, as for a holy book."
        ),
    )
    _aedes_magi(levant, b, covenant)


def _summa(
    b: Builder,
    covenant: Covenant,
    owner: str,
    art: str,
    level: int,
    quality: int,
    language: str,
) -> None:
    b.book(
        covenant,
        f"{owner}'s summa on {art}",
        "Art Summa",
        art=art,
        level=level,
        quality=quality,
        language=language,
        description=f"A summa of {owner}'s library, as the book lists it.",
    )


def _aedes_magi(levant: Levant, b: Builder, covenant: Covenant) -> None:
    m = levant.magi
    m["umar"] = b.magus(
        "Sharaf al-Din 'Umar",
        covenant=covenant,
        house=JERBITON,
        age=72,
        summary=paragraphs(
            "Head of Aedes Veritatis, filius of its founder Maryam "
            "al-Dimashqiyya. Hattin was a Muslim victory, but it killed "
            "most of the covenant's magi; the one left, Heloise of "
            "Criamon, honoured Maryam's wish and let the young 'Umar take "
            "charge, and later went her own way, saying only that her time "
            "had come, and has not been seen since. Wild and hot-headed "
            "once, he has grown into a careful, wise leader, though the "
            "counter-Crusade still obsesses him and the old wildness "
            "breaks out now and then.",
            "To look at he is nobody special, neither tall nor short, "
            "black-haired and fully bearded, until he speaks: then people "
            "listen. He wears black robes with a white sash and a white "
            "turban, and never goes without his staff, enchanted to carry "
            "him from place to place in an instant and to turn weapons "
            "aside. Like his mater he is an elementalist and a devout "
            "Sunni, and of the Islamic Tradition. His elements have made "
            "other Arts hard for him, Vim most of all: the second time he "
            "renewed his longevity potion he could make it strong enough "
            "only with rare ingredients, and hunting such things has "
            "become his own quest.",
        ),
        traits={"Brave": 3, "Calm": 3, "Careful": 3, "Pious": 3, "Wild": 1},
        secrets=[
            titled(
                "'Umar's double loyalty",
                "'Umar is a servant of the Ayyubid sultans as well as a magus "
                "of the Order, and not even his sodales know it. If the Order "
                "learnt of it he would probably be Renounced; but he is "
                "powerful and would call on the Muslims' own mages for help, "
                "so a Renunciation might not end in his death.",
            ),
        ],
    )
    m["amber"] = b.magus(
        "Amber the Golden",
        covenant=covenant,
        house=TREMERE,
        age=54,
        summary=paragraphs(
            "Amber of Tremere, filia Catullus, came to Aedes Veritatis in "
            "1188, soon after Hattin and the Muslims' retaking of "
            "Jerusalem, because she would not bow to her House's backing "
            "of the Crusades. She is now the covenant's second magus and "
            "'Umar's close friend. Fiercely independent, she is tied all "
            "the same to 'Umar, to her cat familiar Luigi, and to her "
            "parens Catullus of Coeris, who treats her as his protégée and "
            "has so far kept the House's elders from disciplining her. "
            "Catullus is drifting toward Final Twilight, and she will soon "
            "need other friends in the House.",
            "A mistake with two reagents during her apprenticeship blew up "
            "in her face, threw her into Twilight for a while and left her "
            "skin, hair and eyes the colour of gold; the bond with Luigi "
            "has slit her pupils like a cat's. She is short and lithe, "
            "catlike in her manner, with a gift for magic touching "
            "felines. She wears a loose red robe that comes off easily, "
            "for she often changes shape, into a cat or a leopard, by "
            "spells she made herself. Luigi is a cat of ordinary size "
            "whose white fur ends in gold; he picked her as much as she "
            "picked him.",
        ),
        traits={
            "Curious": 4,
            "Independent": 3,
            "Cat": 3,
            "Cruel to enemies": 1,
            "Brave": 1,
        },
    )
    m["wardat"] = b.magus(
        "Wardat al-Quds",
        covenant=covenant,
        house=EX_MISCELLANEA,
        age=33,
        summary=paragraphs(
            "The Rose of Jerusalem, a sahira, the youngest magus of Aedes "
            "Veritatis and one of the few of the land's own sahirs to "
            "join the Order. A staunch Sunni sworn to the counter-Crusade, "
            "she joined only to be protected from the Crusader magi, with "
            "'Umar as her sponsor. Her magic is Sihr: she summons and "
            "bargains with spirits, ghosts, jinn and a demon, and calls on "
            "the planets.",
            "Tall and strongly made, she goes wrapped in a black milaya "
            "that shows only her sharp face and her bare feet; her black "
            "eyes hold whoever meets them, and spirits trail after her "
            "awaiting her orders. She knows she frightens people and uses "
            "it, with her power over minds, to be left alone at her "
            "studies. When she chooses to talk she is lucid and good "
            "company, which is seldom. Since childhood the jinni al-Abyad, "
            "the White, has tormented her; she spends her time looking for "
            "a way to beat him, and comes out of her rooms only when she "
            "is needed against the Crusaders. A faint smell of roses "
            "marks her magic.",
        ),
        traits={"Reclusive": 3, "Determined": 3, "Pious": 3, "Brave": 1},
    )


# ------------------------------------------------------------ Domus Pacis


def _domus_pacis(levant: Levant, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "Mediator: neutral ground, and the seat of the Tribunal.",
        "Dar al-Salam to its neighbours, the Abode of Peace: a roadside "
        "khan north of Jerusalem where merchants put up for the night, "
        "paying fees that are part of the covenant's income. The grogs "
        "and covenfolk live in the rooms round the courtyard; the magi "
        "and the rest of the grogs live in caves hidden under the inn. "
        "Its device is a hand.",
        "Aurora of Jerbiton founded it in 1169, with Tau of Flambeau's "
        "help, as a place where magi of the Order and wizards of other "
        "traditions could meet and trade knowledge. She has moved on, "
        "but the covenant keeps to her purpose: Hermetic magi, raqis and "
        "other mages still come to talk over their work. Since Tau became "
        "Praeco it is also the Tribunal's meeting place. Every seven "
        "years tents go up outside the khan for the visitors, the main "
        "gate is shut and opened only for magi coming to the meeting, "
        "and inside chairs are set in a ring in the courtyard where the "
        "business is argued and decided.",
        "The warlike magi of the Tribunal think little of it, and it is "
        "poorly defended; perhaps only its enemies' contempt and their "
        "fear of its powerful friends have spared it worse. Its magi "
        "are energetic, though, and may soon set its troubles right.",
        "Magi: Tau, Felix of Guernicus and Esther of Verditius; the book "
        "counts four, and names no fourth.",
    )
    what_matters = joined_lines(
        "Stance: mediator",
        "Duty: the Tribunal meets here every seven years; the next meeting is in 1221",
        "Vis stores: 200 pawns (20 of each Technique and 10 of each Form)",
        "Vis: about 30 pawns a year (Creo 5, Intellego 2, Rego 5, Corpus 3, Ignem 4, Imaginem 4, Mentem 3, Vim 4), from sources the book does not place",
        "Library: 1500 levels of spells, strongest in Corpus, Ignem, Imaginem, Mentem and Vim",
        "Library: Hermetic books worth 630 points, eight summae among them (see the library records); mundane books worth 480 points on all manner of subjects",
        "Income: merchants' fees at the khan and Esther's trade between the Levant and Rome; a surplus of about 50 pounds of silver a year, with some 1000 pounds' worth in store",
        "Covenfolk: 10 specialists and 25 grogs (10 servants, 15 men-at-arms)",
        "Enchantments: devices worth about 75 levels, many of them lighting the caves and keeping their air fresh",
        "Allies: Magvillus, House Guernicus's domus magna, and the Hermetic Embassy",
        "Enemies: none",
        "Reputation: a haven of peace, among the quaesitores; the quaesitores' pawn, among Crusader and counter-Crusader magi",
        "Boon: Prestige (a haven of peace, and the Tribunal's meeting place)",
        "Boon: Powerful Ally (Magvillus)",
        "Boon: Wealth (Esther's trade)",
        "Hook: Road (a trade road, and merchants at the gate every week)",
        "Hook: Poorly Defensible (flat ground on three sides, a cliff over it on the east)",
        "Hook: Hermetic Politics (the Tribunal's mediators)",
        "Hook: Spies (see Secrets)",
        "Hook: Rival (al-Arama, over Esther's trade)",
    )
    notes = paragraphs(
        "The khan. A high wall closes a central courtyard, with two "
        "storeys of buildings against it: on the ground floor the smithy "
        "and the merchants' rooms and storerooms, above them most of the "
        "grogs and covenfolk. The cave system beneath, where the magi "
        "live, is lit and aired by enchanted devices.",
        "Suggested vis sources (not in the book), for the storyguide to "
        "use, change or ignore: the dew that gathers on the cliff face "
        "over the khan on the mornings after a meeting has ended (Rego, "
        "3 pawns); a spring deep in the caves whose water tastes of "
        "whatever the drinker last dreamt (Mentem, 2 pawns); and the "
        "soot of the smithy's forge on the night of the winter solstice "
        "(Ignem, 2 pawns).",
    )
    hidden = [
        titled(
            "Aedes Veritatis's spies",
            "The bellicose magi have slipped spies into Domus Pacis. Aedes "
            "Veritatis's spies learn everything that happens here.",
        ),
        titled(
            "Foothold's spies",
            "Foothold's spies in Domus Pacis know what passes in the "
            "covenant's council.",
        ),
    ]
    covenant = b.covenant(
        "Domus Pacis",
        tribunal=tribunal,
        founded=1169,
        place=levant.places["dar_al_salam_khan"],
        aura=1,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        secrets=hidden,
        unnamed_magi=1,
        detail=FULL,
        season="Summer",
        aegis=30,
    )
    levant.covenants["domus_pacis"] = covenant
    for art, level, quality in (
        ("Creo", 21, 9),
        ("Intellego", 17, 8),
        ("Rego", 17, 8),
        ("Corpus", 16, 7),
        ("Ignem", 15, 7),
        ("Imaginem", 18, 9),
        ("Mentem", 19, 11),
        ("Vim", 14, 7),
    ):
        _summa(b, covenant, "Domus Pacis", art, level, quality, "Latin")
    _domus_magi(levant, b, covenant)


def _domus_magi(levant: Levant, b: Builder, covenant: Covenant) -> None:
    m = levant.magi
    m["tau"] = b.magus(
        "Tau",
        covenant=covenant,
        house=FLAMBEAU,
        age=133,
        summary=paragraphs(
            "Tau of Flambeau, filius Sigma, leader of Domus Pacis and "
            "Praeco of the Tribunal since 1207, when the quaesitores ruled "
            "him its eldest. At 133 he still seems a Flambeau of the usual "
            "kind, loving fire, too sure of himself and boyish; under the "
            "roguish manner he is a kind and honest man who wants to do "
            "right by people, cleverer and of wider magical interests "
            "than his House's type, though few look past the surface.",
            "His master Sigma, a wandering Flambeau, passed into Final "
            "Twilight just before Tau's Gauntlet, on the road to a "
            "covenant in Scotland. Tau went on alone to the House of "
            "Hermes' Wisdom, whose head soon sent him to find the nearest "
            "gathering of his House for his Gauntlet. A magus at last, he "
            "lived a long while among the magi of a Greater Alps covenant, until a "
            "younger sodalis there, Aurora of Jerbiton, made plans for a "
            "covenant in the Levant; he came with her and helped her found "
            "Domus Pacis, content to stay in the background, and took it "
            "over at her urging when she left for the Embassy.",
            "Once a dashing young man, he is slower now and very hard of "
            "hearing, and looks to be in his seventies: silver curls to "
            "his collar, a goatee, laughing eyes and a friendly smile. He "
            "dresses well, in a leather tunic, breeches and polished black "
            "boots, with a shortsword at his side.",
        ),
    )
    m["felix"] = b.magus(
        "Felix",
        covenant=covenant,
        house=GUERNICUS,
        age=48,
        summary=paragraphs(
            "Felix of Guernicus, filius Raymond, a quaesitor. He was born "
            "at Dar al-Salam to one of the covenfolk and was a guard in "
            "its turb when his Gift showed itself at 28; after the usual "
            "fifteen years of apprenticeship he passed his Gauntlet only "
            "five years ago. Soon after, his parens was killed fighting a "
            "hedge wizard, in a skirmish that crippled Felix's right leg "
            "for good. He took over Raymond's standing duty of watching "
            "the dealings between House Criamon and the Levant's "
            "Kabbalists, and does it faithfully, by ordinary means first, "
            "since he knows his magic is weak and best kept in support. "
            "He is on good terms with the Kabbalists and has quickly won "
            "a name for fairness in the Order.",
            "A plump, friendly-looking man a little under middle height, "
            "with an aquiline face and brown hair greying at the temples. "
            "His twisted leg keeps him from standing quite straight. He "
            "wears plain brown robes and walks with a staff; he can fight "
            "but seldom goes armed, as his leg makes it hard and battle no "
            "longer stirs him.",
        ),
        traits={
            "Sensible": 3,
            "Diligent": 3,
            "Fair": 3,
            "Brave": 2,
            "Honest": 1,
        },
    )
    m["esther"] = b.magus(
        "Esther",
        covenant=covenant,
        house=VERDITIUS,
        age=43,
        summary=paragraphs(
            "Esther of Verditius, filia Enrico Bellini, the newest magus "
            "at Dar al-Salam, who joined in 1197 and has fast become its "
            "most valued. Her passion is the Levant's trade: through her "
            "merchant contacts she has made herself and the covenant "
            "rich, and under her the covenant is a channel for goods "
            "between the East and Europe, above all between the Levant "
            "and the Roman Tribunal. Her trade is now its main income. It "
            "has also made bitter enemies of the magi of al-Arama, whose "
            "monopoly she broke.",
            "An attractive woman of middle height and build, with short "
            "fair hair, pale skin and an unmistakably English accent. She "
            "wears simple white robes under a blue hooded cloak she has "
            "enchanted with several powers, a plain gold circlet, and "
            "tools and casting foci hanging from her belt. She is friendly "
            "and businesslike; most of her magic is made to ease her "
            "craft and her trading, and she will use a subtle spell on a "
            "mind to win the better side of a bargain.",
        ),
        traits={
            "Avaricious": 3,
            "Professional": 3,
            "Friendly": 2,
            "Subtle": 2,
            "Mercenary": 2,
        },
        secrets=[
            titled(
                "Esther's trade",
                "Esther has been enriching herself by selling powerful "
                "enchanted devices to Muslim and Latin nobles, which the "
                "Peripheral Code forbids. If the quaesitores found out, it "
                "would go hard with her and with her sodales.",
            ),
            titled(
                "Esther's own vis",
                "Esther has a vis source of her own, of Terram, which no one "
                "else knows of.",
            ),
            titled(
                "Storyguide Notes",
                "The book does not say where Esther's vis source is.",
            ),
        ],
    )


# --------------------------------------------------------------- Foothold


def _foothold(levant: Levant, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "Crusader: the loudest of the covenants that want the old war on "
        "the Muslims back.",
        "Not the oldest Crusader covenant, but the one that leads them. "
        "Its founders, the Flambeau Guillaume de Bourne and the "
        "Tytalus Rufus de Clary, two Frenchmen as violent as they are unruly, came to the Levant in "
        "1188, just after Salah al-Din took Jerusalem, and set up their "
        "covenant to be the Order's lasting foothold on the coast, hence "
        "its name. Its device is a flaming sword; it is affiliated with "
        "House Flambeau.",
        "A two-storey stone keep in a yard, inside a strong wall with "
        "battlements and a parapet, on a hill inland from the coast "
        "between Acre and Tyre. Grogs and servants live on both floors, "
        "the magi on the upper one only. Two fishermen and a merchant "
        "among the specialists keep it supplied by selling fish and what "
        "timber is cut. The covenfolk are mostly French and mostly loyal "
        "to their masters and their cause, though there has been some "
        "grumbling in the ranks. The magi, lost in dreams of conquest, "
        "neglect their household, and it may take an attack to wake "
        "them.",
        "The other Crusader covenants back it and the counter-Crusaders "
        "hate it. The quaesitores see it as the chief danger to a shaky "
        "peace and suspect its magi of crusading still. If the Treaty "
        "ever fails, Foothold may well be the first to fall.",
    )
    what_matters = joined_lines(
        "Stance: Crusader",
        "Vis stores: none; it is used nearly as fast as it comes in",
        "Vis: about 15 pawns a year (Creo 3, Perdo 4, Mentem 1, Corpus 3, Ignem 4), from sources the book does not place",
        "Library: 900 levels of spells, strongest in Creo Ignem, Perdo Corpus and Perdo Mentem",
        "Library: Hermetic books worth 360 points, mostly summae, five of them named (see the library records), the rest spread evenly over the Arts; mundane books worth 180 points on the region's geography and history and on warfare",
        "Income: fish and timber; no surplus",
        "Covenfolk: 20 specialists and 50 grogs (15 servants, 35 men-at-arms)",
        "Laboratories: badly kept (-1 to Lab Totals)",
        "Allies: two spring covenants and one of middle age, the other Crusader covenants",
        "Enemies: Aedes Veritatis above all, and two spring covenants",
        "Reputation: a danger to the peace, among the quaesitores",
        "Boon: Difficult Access (steep on three sides)",
        "Boon: Tower Keep (the two-storey keep and its walled yard)",
        "Boon: Hunters or Sailors (its fishermen)",
        "Hook: Infamous (a danger to the peace, in the quaesitores' eyes)",
        "Hook: Rival (Aedes Veritatis and the counter-Crusaders)",
        "Hook: Mundane Politics (its crusading, which the quaesitores suspect)",
        "Hook: Rebellious Covenfolk (discontent among the grogs)",
        "Hook: Spies (see Secrets)",
    )
    notes = paragraphs(
        "Suggested vis sources (not in the book), for the storyguide to "
        "use, change or ignore: the ash of a beacon fire lit on the "
        "hilltop for the feast of the Holy Cross (Ignem, 2 pawns); "
        "thorns from a bramble that grows where a crusader's blood was "
        "spilled on the wooded slope (Perdo, 2 pawns); and the scales of "
        "a fish the fishermen net off Tyre once a year that never stops "
        "struggling (Corpus, 1 pawn).",
    )
    hidden = [
        titled(
            "Scrying devices in Foothold",
            "Magi in the Ayyubids' service have hidden scrying devices in "
            "Foothold, about 75 levels of them, to have warning of any sudden "
            "attack by the covenant or its allies. Its magi do not know.",
        ),
        titled(
            "Foothold's spies",
            "Foothold's own spies in Domus Pacis tell it what passes in that "
            "covenant's council.",
        ),
        titled(
            "The secret war",
            "Aedes Veritatis wages a secret war on Foothold.",
        ),
    ]
    covenant = b.covenant(
        "Foothold",
        tribunal=tribunal,
        founded=1188,
        place=levant.places["foothold_hill"],
        aura=2,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        secrets=hidden,
        detail=FULL,
        season="Spring",
        aegis=15,
    )
    levant.covenants["foothold"] = covenant
    for art, level, quality in (
        ("Creo", 10, 5),
        ("Perdo", 10, 5),
        ("Corpus", 12, 7),
        ("Ignem", 15, 5),
        ("Mentem", 10, 5),
    ):
        _summa(b, covenant, "Foothold", art, level, quality, "Latin")
    m = levant.magi
    m["guillaume"] = b.magus(
        "Guillaume de Bourne",
        covenant=covenant,
        house=FLAMBEAU,
        age=43,
        summary=paragraphs(
            "Guillaume de Bourne of Flambeau, filius Ignatia, a Flambeau "
            "of the old pattern, Ignem his strength and as much a soldier "
            "as a magus, except that he is pious and truly believes in "
            "the Crusade, and that belief has become an obsession. The "
            "Holy Land should be won from the Muslims for the Church; "
            "that the Order would gain by it is, to him, beside the "
            "point. He knows he is a warrior with no head for politics, "
            "so he lets Rufus speak for the covenant and spends nearly as "
            "much time drilling with the grogs as studying.",
            "A big, thickset man with black hair, a thin moustache and a "
            "heavy accent; a burn scar on his right cheek is the mark of "
            "a fight with a powerful Muslim magus. He wears a plain tunic "
            "and trews, a gold cross on a chain and a longsword at his "
            "left hip, and fights in nothing heavier than a reinforced "
            "leather hauberk.",
        ),
        traits={
            "Overconfident": 3,
            "Pious": 3,
            "Brave": 3,
            "Hot-tempered": 2,
        },
    )
    m["rufus"] = b.magus(
        "Rufus de Clary",
        covenant=covenant,
        house=TYTALUS,
        age=45,
        summary=paragraphs(
            "Rufus de Clary of Tytalus, filius Gilles de Clary, who "
            "speaks for Foothold at Tribunal. In debate he argues that "
            "the Crusade must go on for the Order's good, and that if the "
            "Order spreads into Muslim lands it can claim their magical "
            "riches; he means to have his share, and the end justifies "
            "the means.",
            "A handsome, slim man with a slight stoop, very fair hair and "
            "deep blue eyes, in robes of the same blue, with a silver "
            "pendant engraved with his House's sign. He is cunning and "
            "manipulative and will sacrifice others to his ends. He can "
            "work magic without words or gestures and read lips, and so "
            "has learnt many secrets; more than one magus dreads what "
            "would happen if he ever got proof of what he knows.",
        ),
        traits={
            "Power-hungry": 3,
            "Manipulative": 3,
            "Heartless": 2,
            "Vulnerable": 1,
        },
        secrets=[
            titled(
                "What drives Rufus",
                "Fear, not faith, drives him. His parents were diabolists who "
                "put him through horrors as a child until Gilles de Clary "
                "rescued him, and he still believes demons are after his "
                "soul; he hunts magical power to protect himself from them, "
                "and keeps the root of his zeal to himself.",
            ),
            titled(
                "Rufus's hoard",
                "He is gathering a hoard of other magi's secrets, and looking "
                "for the proof that would turn each one into a hold over its "
                "owner.",
            ),
        ],
    )


# ------------------------------------------------------- the Embassy


def _embassy(levant: Levant, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "Mediator: the keeper of the Treaty of Baghdad.",
        "The Order's presence in Baghdad: a house built in the Muslim "
        "manner in the quarter of al-Qurayya, near the caliph's palace, "
        "where two magi live with their bodyguards and servants and "
        "look after the Treaty and the Order's standing at the courts "
        "of the caliph and the Ayyubid sultans. Aurora of Jerbiton founded it in 1193, "
        "when she became a quaesitor, to watch over the peace she had "
        "made. Its device is a white flag with the sign of the Order.",
        "Magvillus, the domus magna of House Guernicus, pays for it, so "
        "it is affiliated with that House, though no Guernicus magus "
        "lives there. Its two magi have proved devoted to its purpose "
        "and are left to themselves.",
        "Foothold and Aedes Veritatis, the leaders of the two warring "
        "factions, harass it now and then with indirect and political "
        "attacks. None has come to violence, and none is likely to, "
        "given Aurora's standing and the quaesitores' weight; but if the "
        "Treaty were abandoned its magi would have to leave the city at "
        "once. The Suhhar Sulayman of Baghdad, who never signed the "
        "Treaty, distrust it.",
    )
    what_matters = joined_lines(
        "Stance: mediator",
        "Duty: keeping the Treaty of Baghdad, and the Order's relations with the caliph and the Ayyubids",
        "Vis stores: 50 pawns of every Art (Creo 4, Intellego 5, Muto 3, Perdo 3, Rego 5, Animal 3, Aquam 2, Auram 2, Corpus 5, Herbam 3, Ignem 2, Imaginem 4, Mentem 2, Terram 2, Vim 5)",
        "Vis: about 20 pawns a year (Creo 3, Intellego 3, Muto 1, Rego 3, Corpus 4, Imaginem 3, Vim 3), from sources the book does not place",
        "Library: 1500 levels of spells, strongest in Corpus, Imaginem and Vim",
        "Library: Hermetic books worth 450 points, spread evenly over the Arts, none named; mundane books worth 300 points on all manner of subjects",
        "Income: Magvillus pays its way",
        "Covenfolk: 20 specialists (14 servants and 6 bodyguards, all highly skilled)",
        "Allies: Magvillus, House Guernicus's domus magna",
        "Enemies: Foothold and Aedes Veritatis",
        "Contacts: Domus Pacis (Dar al-Salam)",
        "Reputation: expert peacemakers, among the quaesitores; interfering do-gooders, among Crusader and counter-Crusader magi",
        "Boon: Prestige (the Order's embassy to the caliph)",
        "Boon: Powerful Ally (Magvillus)",
        "Hook: Urban (the city of Baghdad, all round it)",
        "Hook: Poorly Defensible (overlooked by a rooftop to the south)",
        "Hook: Superiors (Magvillus, which pays for it)",
        "Hook: Hermetic Politics (both warring factions)",
        "Hook: Missing Aura (no Magic aura: the Dominion lies over it at 2)",
    )
    notes = paragraphs(
        "The house. A Muslim-style town house with a council chamber, "
        "closed in by the city on every side; a neighbour's roof looks "
        "down into it from the south.",
        "Suggested vis sources (not in the book), for the storyguide to "
        "use, change or ignore: ink scraped from a treaty the caliph's "
        "chancery has sealed and then cancelled (Rego, 2 pawns); the "
        "reflection in the house's fountain at the moment the call to "
        "prayer falls silent at sunset, caught in a glass bowl "
        "(Imaginem, 2 pawns); and the down of a pigeon from the caliph's "
        "post lofts that has flown the road from Damascus a hundred "
        "times (Corpus, 1 pawn).",
    )
    hidden = [
        titled(
            "Storyguide Notes",
            paragraphs(
                "When the Mongols take Baghdad in 1258 and put the caliph and "
                "many Muslim mages to death, the Hermetic Embassy falls with "
                "the city if it is still there; most of its people die, and "
                "Aurora, old and weak, is taken by the Mongol shamans.",
                "The Embassy's end is the book's guess.",
            ),
        ),
    ]
    covenant = b.covenant(
        "The Hermetic Embassy",
        tribunal=tribunal,
        founded=1193,
        place=levant.places["al_qurayya"],
        aura=2,
        realm="Divine",
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        secrets=hidden,
        detail=FULL,
        season="Spring",
        aegis=35,
    )
    levant.covenants["embassy"] = covenant
    b.book(
        covenant,
        "The library of the Hermetic Embassy",
        "Other",
        description=(
            "No books are named: Hermetic books worth 450 points spread "
            "evenly through the Arts, and 300 points of mundane books on "
            "many subjects."
        ),
    )
    m = levant.magi
    m["aurora"] = b.magus(
        "Aurora Borealis",
        covenant=covenant,
        house=JERBITON,
        age=102,
        summary=paragraphs(
            "Archmaga and quaesitor, Aurora of Jerbiton, filia Marianne, "
            "the oldest quaesitor in the Tribunal and the architect of "
            "the Treaty of Baghdad. A daughter of Alpine nobility, "
            "she was struck by lightning at eight, which woke her Gift "
            "and showed her how she will end: in Final Twilight, from a "
            "second strike. Her mater loved the stars; Aurora cared for "
            "earthly things and for people, took early to Corpus and "
            "studied Mentem deeply, and after her Gauntlet stayed twenty "
            "years at her mater's covenant, a favourite of the grogs and "
            "covenfolk she helped with her magic.",
            "Then she came to the Levant, founded Domus Pacis in 1169, "
            "and, watching Salah al-Din unite the Muslims, saw the danger "
            "to the Order: from 1183 she treated in Baghdad with him, the "
            "caliph and their mages, and brought the quaesitores of "
            "Magvillus a way to end the fighting. When the Treaty was "
            "forced through in 1193 she was made a quaesitor, moved to "
            "Baghdad to keep the peace, founded the Embassy, and soon "
            "became an archmaga. It was she who proposed that only a "
            "Guernicus quaesitor may preside at the Tribunal, so that she "
            "would never be accused of bias in the chair.",
            "At 102 she looks in her late sixties: slim, with long red "
            "hair streaked with grey, in bright, well-cut robes of many "
            "colours, still beautiful; many young magi have lost their "
            "hearts to her, and she has never let it go further. Age and "
            "creeping Twilight are telling on her: a hard Twilight lately "
            "damaged her Animal, she feels her hold on the world "
            "loosening, and she fears for the Levant if she goes soon, "
            "for Spiral could not carry on her diplomacy. She is looking "
            "for an answer.",
            "Her one apprentice, Macha, is now a maga in a covenant in "
            "Hibernia; she shares her mater's interests, leaning more to "
            "Mentem than Corpus.",
        ),
    )
    m["spiral"] = b.magus(
        "Spiral",
        covenant=covenant,
        house=CRIAMON,
        age=53,
        summary=paragraphs(
            "Spiral of Criamon, filius Umberto, the Embassy's second "
            "magus. He wants the peace kept, but what he cares about most "
            "is unravelling the mysteries of Islamic magic. His view of "
            "the world, and of magic above all, is so much his own that "
            "the Muslim mages he meets can hardly follow him; Baghdad's "
            "Sufis think him a wise man and understand little of what he "
            "says. That is why he could not take over the Order's "
            "diplomacy if Aurora were lost, though his enthusiasm keeps "
            "him blind to it.",
            "As a young magus he gave himself almost fanatically to "
            "Intellego and Vim, studying Corpus only enough to make a "
            "strong longevity potion and so win more years for them. He "
            "has mellowed since, seen that Mentem and Imaginem would help "
            "him understand Islamic magic, and is widening his studies.",
            "An unsettling figure: tall and thin as a skeleton, all "
            "joints, his face covered in spiral tattoos and his long fair "
            "hair wild and unwashed, in plain robes torn and ragged from "
            "neglect.",
        ),
        traits={"Enthusiastic": 3, "Naive": 3, "Obsessive": 3, "Obscure": 3},
    )


# -------------------------------------------- after every part has built


def finish(levant: Levant) -> None:
    """Set the covenants' sites inside their regions where the places
    part made them after this one, and link the covenants to each other
    and to the people and places their summaries name. Anything not yet
    made is skipped."""
    b = levant.b
    for key, region_key in SITES.items():
        site, region = levant.places.get(key), _region(levant, region_key)
        if site is not None and region is not None and site.place_id is None:
            site.place_id = region.id
    c = levant.covenants
    for source, target, note in COVENANT_LINKS:
        if source in c and target in c:
            b.link(c[source], "covenants", c[target], note)
    for covenant_key, place_key, note in (
        ("aedes_veritatis", "damascus", "Buys its supplies and sells its stone here"),
        ("domus_pacis", "jerusalem", "Eleven miles to the south"),
        ("foothold", "acre", "Ten miles to the south-west"),
        ("embassy", "caliph", "Keeps the Treaty with his court"),
        ("embassy", "al_kamil", "Keeps the Treaty with the Ayyubids"),
        ("embassy", "order", "The Suhhar distrusts the Embassy"),
    ):
        covenant, target = c.get(covenant_key), levant.find(place_key)
        if covenant is not None and target is not None:
            b.link(covenant, "places", target, note)
    m = levant.magi
    for magus_key, target_key, kind, note in (
        ("esther", "al_arama", "covenants", "Enemies: she broke its monopoly"),
        ("amber", "umar", "characters", "Her close friend"),
        ("tau", "aurora", "characters", "Came to the Levant with her"),
    ):
        magus, target = m.get(magus_key), levant.find(target_key)
        if magus is not None and target is not None:
            b.link(magus, kind, target, note)


# --------------------------------------------------------- generated stats

#: Tau and Aurora, whom Secrets in Sand leaves unstatted ("powerful
#: enough"); generated at the book's ages (L16).
PROFILES: dict[str, Profile] = {
    "tau": Profile(
        strong="int pre sta",
        weak="per",
        arts={"Ig": 9, "Cr": 6, "Pe": 5, "Re": 5, "In": 4, "Me": 3},
        abilities={
            "Leadership": (5, "the Tribunal"),
            "Code of Hermes": (4, "the Peripheral Code"),
            "Area Lore: Levant Tribunal": (4, "covenants"),
            "Single Weapon": (3, "shortsword"),
            "Living Language: Arabic": 3,
            "Charm": 2,
        },
        virtues=[
            "Hermetic Prestige",
            "Poor Hearing",
            "Overconfident (Minor)",
        ],
        native="French",
    ),
    "aurora": Profile(
        strong="com pre int",
        weak="str",
        arts={"Co": 9, "Me": 9, "Cr": 6, "Re": 6, "In": 5, "An": 2},
        abilities={
            "Intrigue": (6, "the Treaty"),
            "Etiquette": (5, "the caliph's court"),
            "Code of Hermes": (5, "the Peripheral Code"),
            "Charm": (4, "envoys"),
            "Living Language: Arabic": 5,
            "Folk Ken": (4, "rulers"),
            "Islamic Law": 2,
        },
        virtues=[
            "Hermetic Prestige",
            "Visions (Minor)",
            "Twilight Prone",
        ],
        native="High German",
    ),
}


def stats(levant: Levant) -> None:
    """Generated stats for Tau and Aurora; the other eight magi here have
    printed blocks, which stats_magi.py enters."""
    b = levant.b
    for key, profile in PROFILES.items():
        character = levant.magi.get(key)
        if character is not None:
            apply(b, character, profile)
