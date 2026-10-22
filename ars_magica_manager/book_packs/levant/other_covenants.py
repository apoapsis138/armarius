"""The eight lesser covenants and their magi (B&S ch08), as sketches
(L8), not played.

Keys: covenants["urbs_rubra"] (Urbs Rubra, at Petra, places["petra"];
Winter; 802; Magic 3, listed), ["urania"] (Urania, on the cliffs of
places["urania_cliffs"] in the Alan lands; Autumn; 806; Magic 3,
listed), ["para_belli"] (Para Belli, in places["para_belli_fortress"]
in Sinai; Summer; 1099; Magic 3, listed; arms gules, a lion or, L26),
["al_arama"] (Al-Arama, on places["al_arama_crag"] in the Taurus,
Lesser Armenia; Autumn; 1073; Magic 3, listed; "vis-rich", with
suggested sources, L10), ["venti_rosa"] (Venti Rosa, a Mercere caravan
with no place; Summer; 1101; its route and twice-yearly visits in the
summary), ["pyramids_i"] (The Pyramids (I), a camp by the Great Pyramid
at Giza, places["giza"]; Summer; 1148; Magic 5), ["pyramids_ii"] (The
Pyramids (II), on Giza's regio level of the temple, Magic 6; Winter,
listed; 1178), each Pyramids summary saying the book offers them as
alternatives or both at once, and ["true_cross"] (The True Cross, in
world["damietta"]; Spring; 1219; Divine 1, none at night). The
renewal motion names "Para Belli" and "The True Cross": keep them
exactly. Each summary opens with its stance (L4). Devices other than
Para Belli's are in the summaries. A covenant whose site is another
part's (Petra, Giza, Damietta) is put there in build if it is made
already, or in finish.

Magi, as sketches, keyed by first name, lower case: magi["fade"] and
["wraith"] (Urbs Rubra; their fate in secrets=); ["selene"],
["gagik"], ["xerxes"], ["theodore"] (Theodore Styppiotes; Urania);
["tiberius"], ["leo"], ["torchere"], ["hector"], ["aramis"] (Para
Belli); ["hergar"], ["hildegard"], ["ezra"], ["elaine"], ["barnabas"]
(al-Arama); ["thomasin"], ["ibrahim"], ["simon"], ["sarah"],
["khayzuran"] (Venti Rosa; only Simon Gifted); ["ruth"], ["pariah"]
(the Pyramids (I)); ["heliobus"] (Heliobus Magister, the Pyramids (II))
with the eleven priests under their names' slugs (PRIESTS), sketches
with no stats (L16); ["david"], ["xydas"] (the True Cross). Generated
stats in stats() for all but the priests (L16), the four unGifted
Redcaps with gifted=False, each at an age from rank, as the book gives
none."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...arms import Arms
from ..builder import paragraphs
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Covenant, Neighbour, Tribunal
    from ..builder import Builder
    from . import Levant

BONISAGUS = "house_bonisagus"
BJORNAER = "house_bjornaer"
CRIAMON = "house_criamon"
EX_MISCELLANEA = "house_ex_miscellanea"
FLAMBEAU = "house_flambeau"
JERBITON = "house_jerbiton"
MERCERE = "house_mercere"
MERINITA = "house_merinita"
TREMERE = "house_tremere"
TYTALUS = "house_tytalus"
VERDITIUS = "house_verditius"

KNOWN_TRIBUNAL: dict[str, Any] = {"status": "Known", "known": "In the Tribunal"}

#: The one blazon the book gives (L26).
PARA_BELLI_ARMS = Arms("Gules", charge="Lion", charge_tincture="Or")

#: Each covenant site this part makes, by key, with its region's key.
SITES: dict[str, str] = {
    "urania_cliffs": "alan_lands",
    "para_belli_fortress": "sinai",
    "al_arama_crag": "lesser_armenia",
}

#: Each covenant whose site another part makes: (covenant key, the
#: site's key).
ELSEWHERE: tuple[tuple[str, str], ...] = (
    ("urbs_rubra", "petra"),
    ("pyramids_i", "giza"),
    ("pyramids_ii", "giza"),
    ("true_cross", "damietta"),
)

#: The priests and priestesses of Thoth and Anubis in the second
#: Pyramids, by key, as the book lists them.
PRIESTS: dict[str, str] = {
    "sehotep_ib_inepu": "Sehotep ib Inepu",
    "djehuti_hotep": "Djehuti Hotep",
    "djehuti_cheperuw": "Djehuti Cheperuw",
    "sat_djehuti": "Sat Djehuti",
    "meret_djehuti": "Meret Djehuti",
    "djehuti_aha": "Djehuti Aha",
    "cheper_baw_inepu": "Cheper Baw Inepu",
    "nebet_en_medw_necher": "Nebet en Medw Necher",
    "inet_en_inepu": "Inet en Inepu",
    "hekait_inepu": "Hekait Inepu",
    "tepher_hem_necher_inepu": "Tepher Hem-necher Inepu",
}


def _lines(*lines: str) -> str:
    """The lines as one text, one entry a line."""
    return "\n".join(lines)


def _tribunal(levant: Levant) -> Tribunal | None:
    if levant.tribunal is not None:
        return levant.tribunal
    return next(iter(levant.b.saga.tribunals), None)


def _site(levant: Levant, key: str, name: str, **kw: Any) -> Neighbour:
    """A covenant's site, inside its region when that is made already."""
    place = levant.b.place(name, inside=levant.places.get(SITES[key]), **kw)
    levant.places[key] = place
    return place


def _temple_level(levant: Levant) -> int:
    """The number of Giza's regio level that holds the temple of Thoth
    and Anubis, or 0 while the places part has not made it."""
    giza = levant.places.get("giza")
    levels = giza.details.get("levels", []) if giza is not None else []
    for number, level in enumerate(levels, start=1):
        if "temple" in level.get("name", "").lower():
            return number
    return len(levels) if levels else 0


def build(levant: Levant) -> None:
    tribunal = _tribunal(levant)
    if tribunal is None:
        return
    b = levant.b
    _sites(levant)
    _urbs_rubra(levant, b, tribunal)
    _urania(levant, b, tribunal)
    _para_belli(levant, b, tribunal)
    _al_arama(levant, b, tribunal)
    _venti_rosa(levant, b, tribunal)
    _pyramids_i(levant, b, tribunal)
    _pyramids_ii(levant, b, tribunal)
    _true_cross(levant, b, tribunal)


def _sites(levant: Levant) -> None:
    _site(
        levant,
        "urania_cliffs",
        "The Cliffs of Urania",
        aura=3,
        summary=(
            "Two pale, sun-bleached cliffs meeting deep in the Alan lands "
            "north-east of the Black Sea, with a network of caves some "
            "fifty feet up where they join: the covenant of Urania. Its "
            "remoteness has kept it safe through every war in the region. "
            "A people of faeries, the Genjii, live near by; they are much "
            "like the jinn. Magic aura 3 (assumed; the book gives none)."
        ),
        **KNOWN_TRIBUNAL,
    )
    _site(
        levant,
        "para_belli_fortress",
        "The Fortress of the Lions",
        aura=3,
        summary=(
            "A fortress hidden in the Sinai desert, the covenant of Para "
            "Belli, guarded by two lion statues brought to life by magic. "
            "Magic aura 3 (assumed; the book gives none)."
        ),
        **KNOWN_TRIBUNAL,
    )
    _site(
        levant,
        "al_arama_crag",
        "The Crag of al-Arama",
        aura=3,
        summary=(
            "A mountain crag in the Taurus, in Lesser Armenia, remote and "
            "rich in vis, where the covenant of al-Arama stands. Magic "
            "aura 3 (assumed; the book gives none)."
        ),
        **KNOWN_TRIBUNAL,
    )


# ------------------------------------------------------------ Urbs Rubra


def _urbs_rubra(levant: Levant, b: Builder, tribunal: Tribunal) -> None:
    covenant = b.covenant(
        "Urbs Rubra",
        tribunal=tribunal,
        founded=802,
        place=levant.places.get("petra"),
        aura=3,
        season="Winter",
        summary=paragraphs(
            "Aloof: its two magi take no part in Tribunal business at all.",
            "The Red City, the Tribunal's oldest covenant, founded in 802 "
            "by the caliph Harun al-Rashid's leave, in the ancient city of "
            "Petra, from which it takes its name. A deep gorge opens onto "
            "a meeting of valleys full of caves, rooms and buildings cut "
            "or raised over the centuries by the Nabataeans, the Romans "
            "and the Byzantines; last came the Crusaders, who built a "
            "castle on a hill deep inside and left it soon after Hattin. "
            "The covenant is now mostly left alone. Its device is three "
            "red houses; it is affiliated with House Criamon.",
            "Its magi are Fade and Wraith of Criamon, husband and wife, "
            "the eldest in the Tribunal. A band of jinn living in great "
            "blocks of stone in the entrance gorge serves and guards "
            "them, and has grown so protective of its failing masters "
            "that it turns every visitor away; some of these jinn are "
            "too strong for any Hermetic magus to force a way past. No "
            "one has seen the pair for years, which is why the "
            "quaesitores ruled Tau the eldest in 1207.",
        ),
        what_matters=_lines(
            "Stance: aloof",
            "Aura: Magic 3 (assumed; the book gives none)",
            "Guardians: the jinn of the entrance gorge, who let no one in",
            "Library and vis: the book gives none",
        ),
        secrets=paragraphs(
            "Most magi believe Fade and Wraith are dead, killed by their "
            "own servants, who keep up the appearance that they live for "
            "reasons of their own; nobody knows. If they live, both are "
            "nearly senile and close to Final Twilight, and pay the "
            "Tribunal no mind.",
        ),
    )
    levant.covenants["urbs_rubra"] = covenant
    m = levant.magi
    m["fade"] = b.magus(
        "Fade",
        covenant=covenant,
        house=CRIAMON,
        age=None,
        summary=(
            "Fade of Criamon, filius La, of Urbs Rubra, Wraith's husband "
            "and with her the eldest magus of the Tribunal. He has not "
            "been seen for years; the jinn who serve the covenant turn "
            "all visitors away."
        ),
        secrets=(
            "He may be dead, killed by the jinn who now pretend he lives; "
            "if he lives, he is mostly senile and near Final Twilight."
        ),
    )
    m["wraith"] = b.magus(
        "Wraith",
        covenant=covenant,
        house=CRIAMON,
        age=None,
        summary=(
            "Wraith of Criamon, filia Vox, of Urbs Rubra, Fade's wife, "
            "and by the book the elder of the two, so that by right the "
            "office of Praeco would be hers; the book gives no reason why "
            "it is she and not her husband. She has not been seen for "
            "years."
        ),
        secrets=(
            "She may be dead, killed by the jinn who now pretend she "
            "lives; if she lives, she is mostly senile and near Final "
            "Twilight."
        ),
    )


# ---------------------------------------------------------------- Urania


def _urania(levant: Levant, b: Builder, tribunal: Tribunal) -> None:
    covenant = b.covenant(
        "Urania",
        tribunal=tribunal,
        founded=806,
        place=levant.places["urania_cliffs"],
        aura=3,
        season="Autumn",
        summary=paragraphs(
            "Aloof: so remote that most of the Tribunal's quarrels never reach it.",
            "The second covenant of the Tribunal, founded in 806, a "
            "network of caves high in two bleached cliffs in the Alan "
            "lands, which has outlasted the region's wars by being out "
            "of the way. Its device is a mountain with two peaks.",
            "Its magi study a people of faeries near by, the Genjii, who "
            "are so like the jinn that the covenant's leader, Selene of "
            "Merinita, thinks the two have a common ancestor. She cannot "
            "yet prove it, and a pact with the Genjii that forbids her "
            "to pry too far into their secrets may mean she never will.",
            "The book describes it as it was before the adventure The "
            "Sorcerer's Slave, set late in the thirteenth century, which "
            "has other magi and more of its layout and its dealings with "
            "the Genjii.",
        ),
        what_matters=_lines(
            "Stance: aloof",
            "Aura: Magic 3 (assumed; the book gives none)",
            "Pact: with the Genjii, limiting what Selene may learn of them",
            "Library and vis: the book gives none",
        ),
        secrets=(
            "The book's guess at its end: when the Mongols overrun the "
            "Alan lands in 1238, their shamans destroy Urania, leaving no "
            "survivors or witnesses and hiding their work from scrying."
        ),
    )
    levant.covenants["urania"] = covenant
    m = levant.magi
    m["selene"] = b.magus(
        "Selene",
        covenant=covenant,
        house=MERINITA,
        age=None,
        summary=(
            "Selene of Merinita, filia Myrtle, Urania's leader, who "
            "studies the Genjii and believes they and the jinn share an "
            "ancestor. Her pact with the Genjii bars her from searching "
            "out their secrets too closely."
        ),
    )
    m["gagik"] = b.magus(
        "Gagik",
        covenant=covenant,
        house=CRIAMON,
        age=None,
        summary=(
            "Gagik of Criamon, filius Matthias, of Urania. The book gives "
            "no more of him."
        ),
    )
    m["xerxes"] = b.magus(
        "Xerxes",
        covenant=covenant,
        house=TREMERE,
        age=None,
        summary=(
            "Xerxes of Tremere, filius Alix, of Urania. The book gives no more of him."
        ),
    )
    m["theodore"] = b.magus(
        "Theodore Styppiotes",
        covenant=covenant,
        house=JERBITON,
        age=None,
        summary=(
            "Theodore Styppiotes of Jerbiton, filius Reynald, of Urania. "
            "The book gives no more of him."
        ),
    )


# ------------------------------------------------------------- Para Belli


def _para_belli(levant: Levant, b: Builder, tribunal: Tribunal) -> None:
    covenant = b.covenant(
        "Para Belli",
        tribunal=tribunal,
        founded=1099,
        place=levant.places["para_belli_fortress"],
        aura=3,
        season="Summer",
        arms=PARA_BELLI_ARMS,
        summary=paragraphs(
            "Crusader: it backs Foothold's call to fight on against the "
            "Muslims, and otherwise keeps to itself.",
            "For War, also called the Covenant of Lions: a fortress "
            "hidden in the Sinai desert, set up in 1099 as soon as the "
            "First Crusade was won, to shelter Hermetic magi and to "
            "train House Flambeau's young fighters; it is affiliated "
            "with that House. Its device is a gold lion rampant on "
            "red.",
            "Two firm friends lead it, Tiberius of Flambeau and Leo of "
            "Bjornaer. It owes its other name to lions: Leo's heartbeast "
            "is one and he keeps several as companions, Tiberius's "
            "familiar is a lion called Atlas, and two magically animated "
            "lion statues guard the fortress. The two seniors are glad to "
            "spread so noble a picture. It cares little for the "
            "Tribunal's politics. The quaesitores suspect its magi, as "
            "they do Foothold's, of fighting in the Crusaders' battles, "
            "but have proved nothing.",
        ),
        what_matters=_lines(
            "Stance: Crusader",
            "Aura: Magic 3 (assumed; the book gives none)",
            "Guardians: two animated lion statues",
            "Reputation: suspected by the quaesitores of crusading",
            "Library and vis: the book gives none",
        ),
    )
    levant.covenants["para_belli"] = covenant
    m = levant.magi
    m["tiberius"] = b.magus(
        "Tiberius",
        covenant=covenant,
        house=FLAMBEAU,
        age=None,
        summary=(
            "Tiberius of Flambeau, filius Lucius, who leads Para Belli "
            "with his friend Leo. His familiar is a lion, Atlas."
        ),
    )
    m["leo"] = b.magus(
        "Leo",
        covenant=covenant,
        house=BJORNAER,
        age=None,
        summary=(
            "Leo of Bjornaer, filius Hecate, who leads Para Belli with "
            "his friend Tiberius. His heartbeast is the lion, and lions "
            "keep him company."
        ),
    )
    for key, name, parens in (
        ("torchere", "Torchere", "Flamberge"),
        ("hector", "Hector", "Ajax"),
        ("aramis", "Aramis", "Caius Magnus"),
    ):
        m[key] = b.magus(
            name,
            covenant=covenant,
            house=FLAMBEAU,
            age=None,
            summary=(
                f"{name} of Flambeau, filius {parens}, of Para Belli. The "
                "book gives no more of him."
            ),
        )


# --------------------------------------------------------------- al-Arama


def _al_arama(levant: Levant, b: Builder, tribunal: Tribunal) -> None:
    covenant = b.covenant(
        "Al-Arama",
        tribunal=tribunal,
        founded=1073,
        place=levant.places["al_arama_crag"],
        aura=3,
        season="Autumn",
        summary=paragraphs(
            "Trader: its business is commerce with the Roman Tribunal.",
            "A covenant on a mountain crag in the Taurus of Lesser "
            "Armenia, one of the few founded between the Tribunal's first "
            "foundation and its second, affiliated with House Jerbiton. "
            "Its device is a white tower with a black roof and pennant. "
            "It trades with several covenants of the Roman Tribunal "
            "(Tribunals of Hermes: Rome has them).",
            "It once had the whole of the Levant's trade to itself, until "
            "Esther of Verditius at Domus Pacis broke its hold, and her "
            "name is a curse word here. Being far more remote than Domus "
            "Pacis, and on far richer vis, it still has all the vis trade "
            "with Rome, but it wants its old supremacy back. It bears the "
            "other magi of Domus Pacis no grudge, but would help anyone "
            "hostile to Esther if it thought it could get away with it.",
        ),
        what_matters=_lines(
            "Stance: trader",
            "Aura: Magic 3 (assumed; the book gives none)",
            "Vis: rich in vis, with the Levant's whole vis trade to Rome; the book gives no figures and places no source (suggestions in the notes)",
            "Trade: with covenants of the Roman Tribunal",
            "Enemy: Esther of Domus Pacis",
            "Library: the book gives none",
        ),
        notes=(
            "Suggested vis sources (not in the book), for the storyguide "
            "to use, change or ignore: snow from the crag's shaded north "
            "face that never melts, even in August (Aquam, 4 pawns); the "
            "first spring flowers of a meadow below the covenant, which "
            "bloom overnight (Herbam, 4 pawns); and a vein of white "
            "crystal in the rock that hums in a storm (Terram, 3 pawns)."
        ),
    )
    levant.covenants["al_arama"] = covenant
    m = levant.magi
    for key, name, house, parens, sex in (
        ("hergar", "Hergar", JERBITON, "Alfred", "filius"),
        ("hildegard", "Hildegard", VERDITIUS, "Mario de la Rosa", "filia"),
        ("ezra", "Ezra", TYTALUS, "Zachariah", "filius"),
        ("elaine", "Elaine", JERBITON, "Hergar", "filia"),
        ("barnabas", "Barnabas", VERDITIUS, "Hildegard", "filius"),
    ):
        house_name = house.removeprefix("house_").capitalize()
        pronoun = "her" if sex == "filia" else "him"
        m[key] = b.magus(
            name,
            covenant=covenant,
            house=house,
            age=None,
            summary=(
                f"{name} of {house_name}, {sex} {parens}, of al-Arama, "
                "which hates Esther of Domus Pacis for breaking its hold "
                f"on the Levant's trade. The book gives no more of {pronoun}."
            ),
        )


# ------------------------------------------------------------- Venti Rosa


def _venti_rosa(levant: Levant, b: Builder, tribunal: Tribunal) -> None:
    covenant = b.covenant(
        "Venti Rosa",
        tribunal=tribunal,
        founded=1101,
        season="Summer",
        summary=paragraphs(
            "Messengers: the Tribunal's Redcaps, who take no side.",
            "A covenant on the move: a caravan of House Mercere, with "
            "which it is affiliated, going from covenant to covenant "
            "across the Tribunal and calling on each about twice a year. "
            "It is no train of carts in the western way, which are rare "
            "in these lands, but a long string of camels, horses and "
            "asses laden with tents, rugs and camping gear and with the "
            "belongings of the Redcaps and their grogs, travelling by day "
            "and camping at night. Its device is a scroll under House "
            "Mercere's seal.",
            "Of its five Redcaps only Simon is Gifted. He usually stays "
            "with the caravan, making magic items to help his fellows on "
            "the road; he has become expert at setting up a working "
            "laboratory in the unlikeliest places, and a howdah on one of "
            "his camels serves as the place for work that must be left to "
            "stand. The caravan's beasts are trained not to shy at magic. "
            "His twin sister Sarah, who guards him too closely, also "
            "keeps to the caravan; the other three are mostly away, "
            "carrying messages that cannot wait for the next visit.",
        ),
        what_matters=_lines(
            "Stance: messengers",
            "Site: none; the caravan visits each covenant about twice a year",
            "Laboratory: Simon's, wherever the caravan camps, with a howdah for long work",
            "Boon and Hook: the book gives none; it is Constantly Mobile by nature",
        ),
    )
    levant.covenants["venti_rosa"] = covenant
    m = levant.magi
    for key, name, parens, sex, said in (
        (
            "thomasin",
            "Thomasin",
            "Hengest",
            "filius",
            "An un-Gifted Redcap, usually away with urgent messages.",
        ),
        (
            "ibrahim",
            "Ibrahim",
            "Mahmud",
            "filius",
            "An un-Gifted Redcap, usually away with urgent messages.",
        ),
        (
            "simon",
            "Simon",
            "Dora",
            "filius",
            "The caravan's one Gifted magus, who stays with it, makes "
            "magic items for his fellow Redcaps and can set up a working "
            "laboratory almost anywhere, using a howdah on a camel for "
            "work that must be left to stand. His twin sister Sarah "
            "watches over him.",
        ),
        (
            "sarah",
            "Sarah",
            "Dora",
            "filia",
            "An un-Gifted Redcap, Simon's twin, who stays with the "
            "caravan to look after him, more closely than he needs.",
        ),
        (
            "khayzuran",
            "Khayzuran",
            "Nur al-Din 'Ali",
            "filia",
            "An un-Gifted Redcap, usually away with urgent messages.",
        ),
    ):
        m[key] = b.magus(
            name,
            covenant=covenant,
            house=MERCERE,
            age=None,
            summary=f"{name} of Mercere, {sex} {parens}, of Venti Rosa. {said}",
        )


# ------------------------------------------------------------ the Pyramids


def _pyramids_i(levant: Levant, b: Builder, tribunal: Tribunal) -> None:
    covenant = b.covenant(
        "The Pyramids (I)",
        tribunal=tribunal,
        founded=1148,
        place=levant.places.get("giza"),
        aura=5,
        season="Summer",
        summary=paragraphs(
            "Aloof: its magi care for nothing but the pyramids.",
            "The first of the book's two covenants at the pyramids of "
            "Giza, which it offers as alternatives, or, for the bold, "
            "both at once, since the second lies in a regio: the troupe "
            "chooses. This one is a camp of tents near the Great Pyramid, "
            "where Ruth of Bonisagus and Pariah of Criamon live with "
            "their grogs. Its device is a pyramid.",
            "Both magi are obsessed with the pyramids. They have mastered "
            "the restless spirits of the place and use them to learn the "
            "pyramids' history and to keep intruders off; they are trying "
            "to read the hieroglyphs on the walls of the burial chamber "
            "of the greatest pyramid and to find a way into the others, "
            "hoping for the hidden wisdom of the ancients and a way past "
            "the limits of Hermetic magic. Their single-mindedness "
            "unsettles other magi, and no one knows how far they will go, "
            "or what they might let loose if another pyramid opens.",
        ),
        what_matters=_lines(
            "Stance: aloof",
            "Aura: Magic 5, and 6 beside the great pyramids and the Sphinx",
            "Servants: the spirits of the place, bound to the magi",
            "Alternative: the book offers this and The Pyramids (II) as two choices, or both together",
            "Library and vis: the book gives none",
        ),
    )
    levant.covenants["pyramids_i"] = covenant
    m = levant.magi
    m["ruth"] = b.magus(
        "Ruth",
        covenant=covenant,
        house=BONISAGUS,
        age=None,
        summary=(
            "Ruth of Bonisagus, filia Orestes, of the Pyramids (I), "
            "obsessed like Pariah with the pyramids' secrets, and with "
            "him master of the spirits of Giza."
        ),
    )
    m["pariah"] = b.magus(
        "Pariah",
        covenant=covenant,
        house=CRIAMON,
        age=None,
        summary=(
            "Pariah of Criamon, filius Celeriter, of the Pyramids (I), "
            "who with Ruth commands the spirits of Giza and is trying to "
            "read the hieroglyphs of the Great Pyramid's burial chamber."
        ),
    )


def _pyramids_ii(levant: Levant, b: Builder, tribunal: Tribunal) -> None:
    covenant = b.covenant(
        "The Pyramids (II)",
        tribunal=tribunal,
        founded=1178,
        place=levant.places.get("giza"),
        level=_temple_level(levant),
        aura=6,
        season="Winter",
        summary=paragraphs(
            "Aloof: its priests keep their worship; its one Hermetic "
            "magus holds twelve votes and has not yet used them.",
            "The second of the book's two covenants at Giza, offered as "
            "an alternative to the first or alongside it, since it lies "
            "in a regio: the troupe chooses. Since ancient times a "
            "brotherhood of twelve priests and priestesses of Thoth and "
            "Anubis has worshipped in a temple hidden in a regio near the "
            "pyramids and the Sphinx. When one died, another Gifted soul "
            "was drawn to the temple to take the place, so they were "
            "always twelve. Its device is the hieroglyphs of the two "
            "gods; it is affiliated with House Ex Miscellanea.",
            "In 1177 a priest died and the one drawn in was a respected "
            "Hermetic scholar, Heliobus Magister of Bonisagus, just as "
            "Hermetic magi had begun raiding the temple for its magical "
            "wealth. He soon had the priesthood admitted to House Ex "
            "Miscellanea, in 1178, which put it under the Code and ended "
            "the raids, and its worship goes on in peace.",
            "So far Heliobus seems to care only for studying his "
            "fellows' rites, but the Tribunal's political covenants worry "
            "that he controls twelve votes; if he ever chose to use them "
            "he would be a power. And nobody knows what magic the temple "
            "hides.",
        ),
        what_matters=_lines(
            "Stance: aloof",
            "Aura: Magic 6, in the temple's regio (assumed; the book gives none)",
            "Season: Winter (assumed; the book wavers between spring and winter)",
            "Votes: twelve at Tribunal, Heliobus's to use if he likes",
            "Alternative: the book offers this and The Pyramids (I) as two choices, or both together",
            "Library and vis: the book gives none",
        ),
    )
    levant.covenants["pyramids_ii"] = covenant
    m = levant.magi
    m["heliobus"] = b.magus(
        "Heliobus Magister",
        covenant=covenant,
        house=BONISAGUS,
        age=None,
        summary=(
            "Heliobus Magister of Bonisagus, filius Maximus Cosinus, a "
            "respected researcher drawn to the temple of Thoth and Anubis "
            "in 1177 to take a dead priest's place, who brought the "
            "priesthood into House Ex Miscellanea in 1178. He studies "
            "their ceremonies and seems to want nothing more; with the "
            "eleven priests he controls twelve votes at Tribunal."
        ),
    )
    for key, name in PRIESTS.items():
        m[key] = b.magus(
            name,
            covenant=covenant,
            house=EX_MISCELLANEA,
            age=None,
            summary=(
                f"{name}, of the priesthood of Thoth and Anubis in the "
                "temple at Giza, admitted to House Ex Miscellanea in "
                "1178. The book names the priests and says nothing of "
                "their magic, so they are given no stats."
            ),
        )


# ---------------------------------------------------------- the True Cross


def _true_cross(levant: Levant, b: Builder, tribunal: Tribunal) -> None:
    covenant = b.covenant(
        "The True Cross",
        tribunal=tribunal,
        founded=1219,
        place=levant.world.get("damietta"),
        aura=1,
        realm="Divine",
        season="Spring",
        summary=paragraphs(
            "Crusader: treasure-hunters riding in the Crusade's wake.",
            "Founded after the Crusaders took Damietta in 1219, by two "
            "young magi who mean to plant the Order in the city. With a "
            "handful of grogs and some powerful friends among the "
            "Crusader garrison, they have set themselves two tasks: to "
            "recover the magical things from a Muslim sorcerer's estate, "
            "and to make the port a channel for magical treasures to the "
            "magi of Europe. They have called on the Order for others to "
            "join them, but few are likely to come until Damietta is "
            "safer. Its device is a cross.",
            "The Mythic Seas (Fourth Edition) says more of it. The book "
            "warns that the Treaty is most likely to break if this "
            "covenant is destroyed.",
        ),
        what_matters=_lines(
            "Stance: Crusader",
            "Aura: Divine 1, and none at night",
            "Contacts: friends of influence in the Crusader garrison",
            "Work: the dead sorcerer's estate, and the port as a road for magical treasure to Europe",
            "Call: for magi to join them",
            "Library and vis: the book gives none",
        ),
    )
    levant.covenants["true_cross"] = covenant
    m = levant.magi
    m["david"] = b.magus(
        "David",
        covenant=covenant,
        house=TREMERE,
        age=None,
        summary=(
            "David of Tremere, filius Virgil, a young magus and one of "
            "the two founders of the True Cross at Damietta."
        ),
    )
    m["xydas"] = b.magus(
        "Xydas",
        covenant=covenant,
        house=BONISAGUS,
        age=None,
        summary=(
            "Xydas of Bonisagus, filius Marcellus, a young magus and one "
            "of the two founders of the True Cross at Damietta."
        ),
    )


# -------------------------------------------- after every part has built


def finish(levant: Levant) -> None:
    """Put the sites in their regions and the covenants whose sites are
    other parts' on them, and link the covenants to their friends and
    foes. Anything not yet made is skipped."""
    b = levant.b
    for key, region_key in SITES.items():
        site, region = levant.places.get(key), levant.places.get(region_key)
        if site is not None and region is not None and site.place_id is None:
            site.place_id = region.id
    c = levant.covenants
    for covenant_key, site_key in ELSEWHERE:
        covenant, site = c.get(covenant_key), levant.find(site_key)
        if covenant is not None and site is not None and covenant.place_id is None:
            covenant.place_id = site.id
    pyramids_ii: Covenant | None = c.get("pyramids_ii")
    if pyramids_ii is not None and not pyramids_ii.place_level:
        pyramids_ii.place_level = _temple_level(levant)
    for source, target, kind, note in (
        ("para_belli", "foothold", "covenants", "Ally: backs its call for war"),
        ("al_arama", "esther", "characters", "Enemy: she broke its monopoly"),
        ("al_arama", "domus_pacis", "covenants", "Trade rival"),
        ("true_cross", "fifth_crusade", "places", "Friends in the garrison"),
        ("urania", "alans", "places", "Its neighbours"),
    ):
        record, found = c.get(source), levant.find(target)
        if record is not None and found is not None:
            b.link(record, kind, found, note)
    m = levant.magi
    for source, target, note in (
        ("tiberius", "leo", "His firm friend"),
        ("leo", "tiberius", "His firm friend"),
        ("fade", "wraith", "His wife"),
        ("wraith", "fade", "Her husband"),
        ("simon", "sarah", "His twin sister"),
        ("sarah", "simon", "Her twin brother"),
        ("elaine", "hergar", "Her parens"),
        ("barnabas", "hildegard", "His parens"),
    ):
        if source in m and target in m:
            b.link(m[source], "characters", m[target], note)


# --------------------------------------------------------- generated stats

P = Profile
LORE = "Area Lore: Levant Tribunal"

#: Every magus here but the priests, none of whom the book gives a block
#: or an age: each age is chosen from rank and standing (listed on the
#: assumptions page).
PROFILES: dict[str, Profile] = {
    "fade": P(
        strong="int per",
        weak="qik dex",
        arts={"Vi": 7, "In": 6, "Me": 6, "Re": 4, "Ig": 3},
        abilities={
            "Enigmatic Wisdom": (7, "the Enigma"),
            "Magic Lore": (5, "jinn"),
            "Living Language: Arabic": 4,
        },
        virtues=["Twilight Prone"],
        age=150,
        native="Greek",
    ),
    "wraith": P(
        strong="int sta",
        weak="qik str",
        arts={"Vi": 7, "In": 6, "Mu": 5, "Im": 5, "Ig": 3},
        abilities={
            "Enigmatic Wisdom": (7, "the Enigma"),
            "Magic Lore": (5, "jinn"),
            "Living Language: Arabic": 4,
        },
        virtues=["Twilight Prone"],
        age=155,
        native="Greek",
    ),
    "selene": P(
        strong="int pre per",
        arts={"In": 7, "Mu": 6, "Im": 5, "An": 4, "He": 4},
        abilities={
            "Faerie Lore": (6, "the Genjii"),
            "Magic Lore": (4, "jinn"),
            "Leadership": 3,
            "Living Language: Alan": 3,
        },
        virtues=["Vow (Minor)"],
        age=95,
        native="Greek",
    ),
    "gagik": P(
        arts={"In": 5, "Vi": 5, "Me": 5, "Te": 3},
        abilities={"Enigmatic Wisdom": (4, "the Enigma"), "Faerie Lore": 2},
        age=70,
        native="Armenian",
    ),
    "xerxes": P(
        strong="int sta pre",
        arts={"Re": 5, "Pe": 5, "Co": 4, "Me": 4},
        abilities={"Leadership": 3, "Survival": (2, "mountains")},
        age=55,
        native="Persian",
    ),
    "theodore": P(
        strong="com pre int",
        arts={"Cr": 5, "Im": 5, "Me": 4, "Te": 3},
        abilities={"Etiquette": 3, "Faerie Lore": 2},
        age=45,
        native="Greek",
    ),
    "tiberius": P(
        strong="sta str pre",
        weak="com",
        arts={"Ig": 8, "Pe": 6, "Cr": 5, "An": 4, "Re": 3},
        abilities={
            "Leadership": (5, "young warriors"),
            "Single Weapon": (4, "sword"),
            "Animal Ken": (3, "lions"),
            "Survival": (3, "desert"),
        },
        virtues=["Warrior", "Driven (Minor)"],
        age=90,
        native="Italian",
    ),
    "leo": P(
        strong="sta str per",
        weak="com",
        arts={"An": 8, "Mu": 6, "Co": 5, "Re": 4},
        abilities={
            "Heartbeast": (6, "the lion"),
            "Animal Ken": (4, "lions"),
            "Survival": (3, "desert"),
        },
        virtues=["Animal Companion", "Reclusive"],
        age=85,
        native="Italian",
    ),
    "torchere": P(
        strong="sta str qik",
        arts={"Ig": 7, "Pe": 5, "Cr": 4},
        abilities={"Single Weapon": (3, "sword"), "Brawl": 2},
        age=40,
        native="French",
    ),
    "hector": P(
        strong="str sta dex",
        arts={"Ig": 6, "Pe": 5, "Re": 4, "Te": 3},
        abilities={"Single Weapon": (3, "sword"), "Ride": 2},
        age=33,
        native="French",
    ),
    "aramis": P(
        strong="qik dex sta",
        arts={"Ig": 6, "Cr": 5, "Au": 4},
        abilities={"Single Weapon": (3, "rapier-like blades"), "Athletics": 2},
        age=29,
        native="French",
    ),
    "hergar": P(
        strong="com pre int",
        arts={"Cr": 6, "Te": 6, "Re": 5, "Me": 4, "Im": 3},
        abilities={
            "Bargain": (6, "vis"),
            "Etiquette": (4, "magi"),
            "Living Language: Italian": 4,
            "Leadership": 3,
        },
        virtues=["Ambitious (Minor)"],
        age=120,
        native="High German",
    ),
    "hildegard": P(
        strong="int dex",
        arts={"Re": 6, "Te": 6, "Vi": 5, "Ig": 4},
        abilities={
            "Craft: Goldsmith": (5, "settings"),
            "Bargain": (4, "enchantments"),
            "Living Language: Italian": 3,
        },
        age=115,
        native="High German",
    ),
    "ezra": P(
        strong="int com",
        arts={"Me": 6, "Re": 5, "Im": 4, "In": 3},
        abilities={
            "Intrigue": (5, "trade"),
            "Guile": (4, "rivals"),
            "Bargain": 3,
        },
        virtues=["Hatred (Minor)"],
        age=75,
        native="Armenian",
    ),
    "elaine": P(
        strong="com pre",
        arts={"Cr": 5, "Te": 5, "Me": 4, "Im": 3},
        abilities={
            "Bargain": (4, "vis"),
            "Etiquette": 3,
            "Living Language: Italian": 3,
        },
        age=60,
        native="Armenian",
    ),
    "barnabas": P(
        strong="int dex",
        arts={"Re": 5, "Te": 5, "Ig": 4, "Vi": 3},
        abilities={"Craft: Goldsmith": (4, "settings"), "Bargain": 2},
        age=50,
        native="Armenian",
    ),
    "thomasin": P(
        gifted=False,
        strong="sta per qik",
        abilities={
            "Ride": (5, "long journeys"),
            LORE: (5, "roads"),
            "Survival": (4, "desert"),
            "Living Language: Arabic": 4,
            "Organization Lore: Order of Hermes": 3,
        },
        virtues=["Redcap", "Wanderlust"],
        age=60,
        native="English",
    ),
    "ibrahim": P(
        gifted=False,
        strong="sta per com",
        abilities={
            "Ride": (5, "camels"),
            LORE: (5, "roads"),
            "Survival": (4, "desert"),
            "Animal Handling": (3, "camels"),
            "Living Language: Latin": 3,
        },
        virtues=["Redcap", "Wanderlust"],
        age=48,
        native="Arabic",
    ),
    "simon": P(
        strong="int dex sta",
        arts={"Re": 7, "Cr": 5, "Te": 5, "Vi": 5, "An": 3},
        abilities={
            "Magic Theory": (6, "enchanting items"),
            "Animal Handling": (3, "camels"),
            "Ride": 2,
            LORE: 3,
        },
        virtues=["Close Family Ties"],
        age=42,
        native="Greek",
    ),
    "sarah": P(
        gifted=False,
        strong="per sta pre",
        abilities={
            "Awareness": (5, "danger to her brother"),
            "Single Weapon": (3, "knife"),
            "Ride": 3,
            LORE: 4,
            "Animal Handling": 3,
        },
        virtues=["Redcap", "Close Family Ties", "Busybody", "Dutybound"],
        age=42,
        native="Greek",
    ),
    "khayzuran": P(
        gifted=False,
        strong="qik per com",
        abilities={
            "Ride": (4, "horses"),
            LORE: (4, "roads"),
            "Survival": (3, "desert"),
            "Living Language: Latin": 3,
        },
        virtues=["Redcap", "Wanderlust"],
        age=32,
        native="Arabic",
    ),
    "ruth": P(
        strong="int per",
        arts={"Re": 6, "Me": 6, "In": 5, "Te": 4, "Vi": 4},
        abilities={
            "Magic Lore": (5, "ghosts"),
            "Magic Theory": (5, "inventions"),
            "Dead Language: Ancient Egyptian": (2, "hieroglyphs"),
        },
        virtues=["Obsessed (Minor)"],
        age=75,
        native="Italian",
    ),
    "pariah": P(
        strong="int per",
        arts={"In": 6, "Me": 6, "Re": 5, "Te": 4, "Vi": 4},
        abilities={
            "Enigmatic Wisdom": (5, "the Enigma"),
            "Magic Lore": (4, "ghosts"),
            "Dead Language: Ancient Egyptian": (3, "hieroglyphs"),
        },
        virtues=["Obsessed (Minor)"],
        age=70,
        native="Greek",
    ),
    "heliobus": P(
        strong="int per",
        arts={"In": 8, "Vi": 7, "Re": 6, "Me": 5, "Cr": 4},
        abilities={
            "Magic Theory": (7, "inventions"),
            "Magic Lore": (5, "the temple's rites"),
            "Dead Language: Ancient Egyptian": (4, "rites"),
        },
        virtues=["Hermetic Prestige", "Obsessed (Minor)"],
        age=110,
        native="Italian",
    ),
    "david": P(
        strong="pre sta int",
        arts={"Re": 5, "Pe": 4, "Me": 4, "Co": 3},
        abilities={"Leadership": (3, "grogs"), "Single Weapon": 2},
        age=30,
        native="French",
    ),
    "xydas": P(
        strong="int per",
        arts={"In": 5, "Vi": 5, "Re": 3},
        abilities={"Magic Theory": (4, "enchanted items"), "Magic Lore": 2},
        age=28,
        native="Greek",
    ),
}


def stats(levant: Levant) -> None:
    """Generated stats for the lesser covenants' magi and Redcaps; the
    priests of the second Pyramids are left as sketches (L16)."""
    b = levant.b
    for key, profile in PROFILES.items():
        character = levant.magi.get(key)
        if character is not None:
            apply(b, character, profile)
