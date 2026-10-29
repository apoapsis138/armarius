"""The Tribunal's lands and places (ch01, ch02, ch04, ch05): the regions,
the four covenants' sites, the two fallen covenants of the first
settlement, and the places of Slavic legend the book names.

Auras the book numbers are kept: Three Lakes Magic 4, Leczyca Magic 4,
Pripet Maior Magic 6 and the Valley of a Thousand Caves Slavic Faerie 6
(N7). A Slavic faerie aura is a Faerie aura where the Volkhvy and
domestic magic are strong (p. 82); it is Faerie here, with the
difference in the summary. Places of legend the book gives no number
take Faerie 3 (the convention the Alps and Stonehenge packs follow).
Slavic Arcadia is a Rumoured place of its own, not an aura.

Keys: places["russia"], ["novgorod_lands"], ["pripet_marsh"], ["urals"],
["poland"], ["baltic"], ["steppe"], the covenant sites
["three_lakes_site"], ["thousand_caves_site"], ["pripet_island"],
["leczyca_ridge"], the ruins ["rodnya"] and ["grand_silesia"], and
["lake_strukhalis"], ["tatras"], ["wawel_hill"], ["slavic_arcadia"]."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..builder import Builder, paragraphs

if TYPE_CHECKING:
    from ..records import Records

SLAVIC_AURA = (
    "A Slavic faerie aura: to most people and magic no different from any "
    "Faerie aura, but the Volkhvy draw twice its strength in their rites "
    "there, and pagans with Pagan Belief can work domestic magic in it. "
    "The Volkhvy keep such auras Slavic; without them they turn neutral."
)


def build(records: Records) -> None:
    b, p = records.b, records.places
    p["russia"] = b.place(
        "The Russian Principalities",
        aura=0,
        summary=paragraphs(
            "The lands of the House of Rurik: Novgorod, Suzdalia, Ryazan, "
            "Smolensk, Polotsk, Chernigov, Kiev, Pereyaslavl, Pinsk-Turov, "
            "Volinia and Galicia, each ruled by its prince and his boyars "
            "and druzhina, at war with one another as often as not. Forest "
            "in the north, the open steppe in the south; rivers are the "
            "roads, timber, furs, wax, honey and slaves the trade. Pagan "
            "villages linger in the forests and the Volkhvy with them.",
        ),
        known="In the Order",
    )
    p["novgorod_lands"] = b.place(
        "The Lands of Lord Novgorod the Great",
        inside=p["russia"],
        aura=0,
        summary="The vast northern lands of the city on the Volkhov, from "
        "Lake Ilmen to the White Sea: forest, lakes and fur-trapping "
        "country, with Ladoga and Beloozero its other towns.",
        known="In the Order",
    )
    p["pripet_marsh"] = b.place(
        "The Great Pripet Marsh",
        inside=p["russia"],
        realm="Faerie",
        aura=3,
        summary=paragraphs(
            "Two hundred miles by a hundred and fifty of reed, channel, "
            "bog and stilt-village between Turov and Pinsk, rich in bog "
            "iron, fish and fowl, with salt basins beginning to be mined at "
            "its edge. Settlers are being brought in to drain and work it, "
            "and Pripet Maior answers them with raids and hauntings.",
            "The marsh's heart is a wilderness few enter; Stolitzya the "
            "Swimmer is said to brood there.",
        ),
        status="Known",
        known="In the Order",
    )
    p["urals"] = b.place(
        "The Western Urals",
        aura=0,
        summary="Endless forest rising to the mountains in the east, above "
        "the headwaters of the Kama. Three Lakes' explorers reached it in "
        "the 1150s; its Slavic tribes are quietly pagan and live with "
        "little iron.",
        known="In the Tribunal",
    )
    p["poland"] = b.place(
        "The Kingdom of Poland",
        aura=0,
        summary=paragraphs(
            "The lands of the Piast dukes, divided since 1138 into "
            "duchies: Krakow and Sandomierz under the Grand Duke Leszek the "
            "White, Silesia, Greater Poland, Mazovia and Kujavia, and "
            "Pomerania on the sea. German settlers pour into Silesia, the "
            "Prussians raid from the north, and the Rhine Tribunal covets "
            "the land, which it calls vacant.",
        ),
        known="In the Order",
    )
    p["baltic"] = b.place(
        "The Baltic Coast",
        aura=0,
        summary="The pagan peoples' shore: Prussians, Lithuanians, "
        "Samogithians, Curs, Semgallians, Livonians, Letts and Estonians, "
        "with the crusading orders, the Bishop of Riga and the Danes "
        "pressing in. Where the old gods are still the law, the Volkhvy "
        "are priests of whole peoples.",
        known="In the Order",
    )
    p["steppe"] = b.place(
        "The Southern Steppe",
        aura=0,
        summary="The open grassland south of Kiev and Pereyaslavl, the "
        "Cumans' range for a century, where nomads have come and gone for "
        "millennia. Rodnya stood at its edge.",
        known="In the Order",
    )
    _sites(records)
    _legend(records)


def _sites(records: Records) -> None:
    b, p = records.b, records.places
    p["three_lakes_site"] = b.place(
        "The Valley of Three Lakes",
        inside=p["novgorod_lands"],
        aura=4,
        summary="A fertile lowland valley ringed by dense woods at the "
        "centre of the triangle of lakes Onega, Beloe and Ilmen, much of "
        "its floor a wide, placid lake; its walls and some of the floor "
        "are cleared for pasture. The covenant's stockade climbs from the "
        "Trade Yard to the High House and the stone Keep in a pass of the "
        "valley wall.",
        known="In the Tribunal",
    )
    p["thousand_caves_site"] = b.place(
        "The Valley of a Thousand Caves",
        inside=p["urals"],
        realm="Faerie",
        aura=6,
        summary=paragraphs(
            "A long, twisting gorge running down from the western face of "
            "the Urals above the Kama's headwaters, its cliffs pocked with "
            "hundreds of dry, roomy caves joined by ledges. At its mouth "
            "rears the Earth Crown, the covenant's watchpost; below it the "
            "Great Cavern, as large as a cathedral, is the only fortified "
            "part. The valley floor is farmed. Georgi Yurivich found and "
            "named it more than forty years ago.",
            SLAVIC_AURA,
        ),
        known="In the Tribunal",
    )
    p["pripet_island"] = b.place(
        "Pripet Maior's Island",
        inside=p["pripet_marsh"],
        aura=6,
        summary="A middling island twenty miles inside the southern edge "
        "of the marsh, reached by one narrow path from the south and then "
        "a deep channel crossed by an enchanted causeway, which the Aegis "
        "raises for covenfolk and invited guests (and which sticks up or "
        "down when the Aegis is late). Its reed palaces, living tree "
        "houses and flower arbours were once a baroque marvel; now they "
        "rot, and quicksand lies among them.",
        known="In the Tribunal",
    )
    p["leczyca_ridge"] = b.place(
        "Leczyca's Ridge",
        inside=p["poland"],
        aura=4,
        summary="A ridge in gentle hill country between the Vistula and "
        "the Warta, about fifty miles east of Sieradz. The east and west "
        "approaches are rough, the south tedious; an easy track climbs "
        "from the north, from Leczyca town.",
        known="In the Tribunal",
    )
    p["rodnya"] = b.place(
        "Rodnya",
        inside=p["steppe"],
        aura=0,
        summary="The Theban covenant founded near the town of Rodnya on "
        "the Dnieper, eighty miles south of Kiev, in 992; Patrick of "
        "Dunderry's home, abandoned in 1009 under Theban and "
        "Transylvanian attack.",
        known="In the Tribunal",
        ruined=True,
    )
    p["grand_silesia"] = b.place(
        "Grand Silesia",
        inside=p["poland"],
        aura=0,
        summary="The Rhine's covenant of 993, in a secluded valley of the "
        "hills between the Oder and the Warta, halfway between Poznan and "
        "Wroclaw; damaged in 1009, resettled in 1013 and destroyed by "
        "anti-pagan knights in 1039.",
        known="In the Tribunal",
        ruined=True,
    )


def _legend(records: Records) -> None:
    b, p = records.b, records.places
    p["lake_strukhalis"] = b.place(
        "Lake Strukhalis",
        inside=p["poland"],
        realm="Faerie",
        aura=3,
        summary="The Polish lake where belief in Strukis the Great Pike, "
        "king of fish and lord of the water faeries, is strongest. His "
        "palace lies beneath it; whoever enters stands a good chance of "
        "being seized as his slave.",
        status="Rumoured",
        known="Locally",
    )
    p["tatras"] = b.place(
        "The Tatra Mountains",
        inside=p["poland"],
        realm="Faerie",
        aura=3,
        summary="The north-western Carpathians on Poland's southern border, "
        "where most of the Slavic monsters lair: dragons, ogres and giants "
        "(dziwozony), and lesser horrors that raid the borderland.",
        known="Locally",
    )
    p["wawel_hill"] = b.place(
        "Wawel Hill",
        inside=p["poland"],
        aura=0,
        summary="Krakow's citadel hill, where the hero Krakus slew a "
        "marauding dragon by an alchemical trick he could not manage by "
        "arms; the city grew on the site. The cave beneath is still shown.",
        known="Locally",
    )
    p["slavic_arcadia"] = b.place(
        "Slavic Arcadia",
        realm="Faerie",
        aura=0,
        summary=paragraphs(
            "The part of Arcadia ruled by the faerie powers the Slavs call "
            "gods: firmer and more logical than the west's, a land of "
            "fairy tale where kindness to an overladen tree is rewarded "
            "and giants come in threes. The World Tree holds it together: "
            "Slavic Heaven in its branches, Slavic Earth (thirty "
            "princedoms, half of the Gold Court and half of the White) "
            "about its trunk, and Slavic Hell among its roots, where the "
            "Nameless God of Demons is bound and the Fates watch, and "
            "where the dead live in the autumn garden of Slavic Elysium "
            "with the Isle of Boyan, home of the Volkhvy's dead.",
            "Visitors are drawn at once into its stories; those who play "
            "them too well stay happily ever after. Every foray should "
            "cost something. Since 1206 Mongol spirits, wingless thunder "
            "wyrms, have raided it in the Onslaught, laying three "
            "princedoms waste.",
        ),
        status="Rumoured",
        known="In the Order",
        levels=[
            Builder.level(
                "Slavic Earth",
                0,
                "Faerie",
                notes="An idealized Russia of princedoms and cities about "
                "the World Tree's mountain; its borders with the 'German' "
                "faeries are the way into western Arcadia.",
            ),
            Builder.level(
                "Slavic Heaven",
                0,
                "Faerie",
                notes="The gods' world in the Tree's branches, of blinding "
                "Summer; only the strongest Volkhvy go, and few return.",
            ),
            Builder.level(
                "Slavic Hell and Elysium",
                0,
                "Faerie",
                notes="Dim courts of winter and toil, the dark gods' realm "
                "where the Fates keep the Nameless, and the gentle Elysium "
                "of the pagan dead with the Isle of Boyan.",
            ),
        ],
    )
