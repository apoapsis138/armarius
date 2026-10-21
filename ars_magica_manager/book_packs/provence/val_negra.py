"""The Lost Covenant of Val-Negra (Chapter Nine, with its history and fall
from Chapters Two and Three), in paraphrase: one ruined covenant place,
the Black Vale on Mount Perditu, with its three regio levels down to the
fortress at aura 8. The dungeon's rooms are in its summary rather than
places of their own; its Living Ghost (Abaddon of Tytalus), the Aerie
Clan and the thing behind the Iron Door (the Adulteration of Flambeau)
are described there too, as the app has no creature record yet, with
what players should not know under Secrets.

The Grand Library and Inirelte's books are one unowned library record,
and the Mercurian scroll Priamitus is believed to have hidden here a
second, both linked from the place. The Quaesitors' ban on rebuilding
is tribunal.py's ruling, and the Adulteration as a dormant threat is
stories.py's.

`finish` sets the place inside the Pyrenees (Mount Perditu, when the
Pyrenees part made it) and links it to the two covenants that claim its
legacy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ... import storage
from ...models import Book
from ..builder import paragraphs

if TYPE_CHECKING:
    from . import Provence


def build(provence: Provence) -> None:
    b = provence.b
    site = b.place(
        "Val-Negra",
        ruined=True,
        summary=_summary(),
        secrets=_hidden(),
        realm="Magic",
        aura=4,
        status="Rumoured",
        known="In the Order",
        levels=[
            b.level(
                "The Labyrinthine Caverns",
                6,
                enter=(
                    "Follow the gorge on past Perdut: the regio begins where "
                    "the trail starts to wander."
                ),
                notes=(
                    "The gorge forks and turns back on itself, and its path "
                    "never runs the same way twice. Cave mouths open all "
                    "along it into shifting mazes of dark tunnels that join "
                    "the regiones running under the Pyrenees. Beasts lost in "
                    "the maze, or lairing near its mouths, prey on "
                    "travellers: man-eating ogres, poisonous drakes, warped "
                    "animals and serpents of fire."
                ),
            ),
            b.level(
                "The Valley of Mists",
                7,
                enter=(
                    "Only while mist climbs out of the Tessier, at night and "
                    "just after dawn."
                ),
                notes=(
                    "A silent, choking fog, scalding in one place and icy a "
                    "few steps on; little that lives moves here. Second "
                    "Sight shows it crowded with spirits: the ghosts of lost "
                    "travellers, spiteful imps, river sprites and wretched "
                    "spirits that no longer recall what they were. Getting "
                    "out is as easy as finding a gap in the fog (Auram magic "
                    "makes it trivial); going on to Val-Negra means finding "
                    "the Circle of Light."
                ),
            ),
            b.level(
                "The Fortress of Val-Negra",
                8,
                see=(
                    "Only from inside the Circle of Light: an hour's search, "
                    "Per + Awareness against 12, and another hour for each "
                    "failure; then a regio perception roll shows the bridge."
                ),
                enter=(
                    "Cross the great stone bridge over the chasm from the "
                    "Circle of Light."
                ),
                notes=(
                    "The Circle of Light is an enchantment on the boundary "
                    "(MuVi with Perdo and Terram requisites, level 79, "
                    "constant, Penetration 0, built with the Mystery of "
                    "Hermetic Architecture and Closed Privacy of the "
                    "Enchanted Regio) that narrows the way into this level "
                    "to a lit circle ten paces across; no one outside it can "
                    "see in. Beyond the bridge stands the fortress, under an "
                    "Aegis of the Hearth of level 50 (Penetration 25). Its "
                    "rooms are described in the place's summary."
                ),
            ),
        ],
    )
    provence.places["val_negra"] = site
    for book in _library(provence):
        b.link(site, "books", book, "Kept, lost or hidden in Val-Negra")


def _summary() -> str:
    return paragraphs(
        "Founded 774, fallen 1012. Once domus magna of House Flambeau, home "
        "of the Founder himself and seat of the first Tribunal of the "
        "region; at its height, with 33 members, the largest covenant the "
        "Order has ever had, and as mighty as Durenmar. Its device is a "
        "cartwheel whose seven spokes are swords. Every magus knows the "
        "legend, yet almost no one knows where it lies or how to get in. "
        "Some say it still lives, shut away from the Order by choice; others "
        "that the regio of Mount Perditu is slowly turning it into a myth, "
        "or that the Magic Realm has swallowed it; a few think bold magi "
        "could find it and bring it back.",
        "History. The stronghold first belonged to Delendar the Destroyer, "
        "an old Mercurian wizard who took it from a cabal of sahirs who had "
        "enslaved the Aerie Clan, the strange folk native to the vale. "
        "Flambeau came to recruit him after the Founding, but Delendar had "
        "died first, having foreseen Flambeau's coming in a last vision and "
        "left the place to him; his one apprentice, Delendos, joined House "
        "Flambeau. The covenant was settled straight after the First "
        "Tribunal, but Flambeau would not accept a charter unless he held "
        "suzerainty over every covenant Val-Negra helped to found, and "
        "Guernicus's objections led the Second Grand Tribunal to lay down how "
        "regional Tribunals are made and run. Val-Negra was recognised a "
        "year later, in 774, and a Tribunal grew up around it.",
        "Flambeau was the only Founder to live here, and Trianoma and "
        "Mercere visited often; Gelon of Verditius spent decades here, and "
        "the Founder trained and housed his army of wizards here for his war "
        "on the Moors. Apromor, a Basque and Flambeau's first apprentice, "
        "became the first Primus in 820 and spread "
        "outposts across the Pyrenees; with his support Priamitus of Mercere "
        "raised a temple to Mercury nearby and revived the Cult of Mercury "
        "here, its heyday the early 900s. In 865 Val-Negra was placed in the "
        "Iberian Tribunal. Most of its golden age is unrecorded, and what "
        "tales survive disagree, so each troupe may write its own.",
        "The fall. Just before the Schism War, many of its Flambeau left "
        "after one of them had a vision, and founded Aedes Mercurii from its "
        "outlying halls and temple. Those who stayed had long distrusted "
        "House Diedne and pressed hard for war. Primus Entisimon roused the "
        "House with a speech, the vaults were thrown open to pour out vis "
        "and silver, and magi rode out to strike first; it cost them dearly. "
        "Lucien the Fat of Flambeau was ambushed and killed; Leo Augustus of "
        "Flambeau and Vegetius of Tremere fell attacking Askelarre; Delendez "
        "of Flambeau, victorious against the Diedne of Galicia and Navarre, "
        "was lost to Twilight in battle; seven magi of several Houses died in "
        "the Final Victory over Llewellyn; and Iarna of Flambeau left at the "
        "war's end to hunt the last Diedne wherever they had fled and never "
        "returned (an Ex Miscellanea prophecy says she will, if the Diedne "
        "ever do). Of 25 magi when the war began, 4 lived to see it end, and "
        "much of the covenant's lore died with the rest.",
        "Meanwhile five Diedne archmagi struck the home its magi had left "
        "lightly guarded, slipped past its traps and wards, and fought their "
        "way to the Iron Door. They killed three of the five magi defending "
        "it, and were themselves destroyed. The Quaesitors kept what "
        "happened quiet and ruled that Val-Negra must never rise again; the "
        "domus magna moved to Castra Solis, and the survivors went to Aedes "
        "Mercurii, which has claimed ever since that Val-Negra is gone and "
        "its legacy theirs. Castra Solis disputes the claim. Only a few old, "
        "powerful magi still alive have been there; they warn others off, "
        "though they like telling tales of its glory, and a careful player "
        "may coax facts out of them.",
        "The Black Vale. A gorge of the Tessier on the south side of Mount "
        "Perditu, cut so deep that the sun reaches the bottom only around "
        "midday, and then through the mist off the river: hence the name. "
        "It is the mountain's magical heart; most of its wilds have a Magic "
        "aura of 1 to 4, by place and season.",
        "Perdut (Magic aura 6). A hamlet of about thirty at the gorge's "
        "mouth, five houses and one shared field. The aura has left its "
        "people looking very old or very young; no outsider has come in "
        "generations, and they fear and revere unseen 'watchers' whom their "
        "tales say strangers once came to meet. The Gift seems not to touch "
        "them. They keep up an empty manor on a hill, once the covenant's "
        "guest house, and gladly lodge and feed visitors there. A ruined "
        "stone hut on the edge of the village held a Mercere Portal to an "
        "unknown destination, wrecked on purpose long ago by a Disenchant "
        "ritual. Aedes Mercurii's own portal here was abandoned at the start "
        "of the Schism War.",
        "The way in. Past Perdut the gorge is a regio of three levels: the "
        "Labyrinthine Caverns (aura 6), the Valley of Mists (aura 7) and the "
        "fortress (aura 8), reached only through the Circle of Light (see "
        "the levels). Redcaps once carried enchanted lanterns whose coloured "
        "light showed a safe path all the way; Harco keeps one in its vault "
        "and Primus Garus has another, but asking to borrow either will "
        "draw questions.",
        "The fortress. Across the chasm the crumbling but still splendid "
        "fortress climbs the mountain face under the great Black Tower. The "
        "outer walls hold and several towers stand; most buildings inside "
        "have fallen. Pits scattered about drop into caves and tunnels "
        "beneath, and the Black Guard of the Aerie Clan still keeps watch. "
        "Astella of Jerbiton's garden of magical plants, gone wild since "
        "she fled early in the Schism War, has overgrown most of the ruin: "
        "its creepers are rooted so deep in the walls that killing them "
        "would bring much of the place down. Some rooms hold vis-bearing "
        "plants, plants with powers like spells, and a few that kill. Her "
        "own garden is still kept in order by old enchantments; studying it "
        "and the wild growth counts as a Significato in Herbam, gaining a "
        "stress die + 8 experience.",
        "The Guardian's Tower. The path to the main gate runs beneath a "
        "bridge joining this tower, over the chasm on the right, to the "
        "Black Tower on the left; neither opens onto the path. It is entered "
        "only over the bridge from the Black Tower (magic can lift a magus "
        "to the bridge, if it penetrates the Aegis). At least two Aerie "
        "guards are always posted, one at the top and one at the bottom; "
        "they admit anyone who proves to be a Hermetic magus and hand out "
        "tokens for the Aegis. A bell at its centre rings whenever someone "
        "crosses into the regio. Its middle floor is at the covenant's "
        "ground level, and its lowest is cut into the cliff, with wide "
        "windows over the drop.",
        "The Black Tower. Built by Delendos as Apromor's seat as Primus, and "
        "the Primi's sanctum until the domus magna moved; half of it is sunk "
        "into the mountain. The second floor, jutting from the rock, holds "
        "the barracks and the only outside door, onto the bridge; a spiral "
        "stair leads up to the third, the great hall of banquets and "
        "meetings, now bare and deep in dust. The Grand Stair climbs from "
        "the third to the sixth floor. The fourth and fifth hold meeting "
        "rooms, a conference hall, a scriptorium and two wrecked guest "
        "laboratories, and on the fourth the Memorial, a cobwebbed hall to "
        "fallen heroes with an unfinished tapestry of the magi lost in the "
        "Schism War. The sixth was the Primus's reception floor: a small "
        "dining hall, a spare laboratory still in fair order, and rooms for "
        "six guests. The seventh has no door, window or stair and is reached "
        "only by magic: the Primus's quarters, a tiny library, the main "
        "laboratory reshaped by Primus after Primus, and Apromor's Perdo "
        "laboratory, the Dissolution Chamber.",
        "Below the Black Tower. Behind a blocked door on the second floor a "
        "stair runs down to a ground floor and a basement, both stuffed with "
        "stores and forgotten long ago. Under the junk in the basement are "
        "two trap doors. The wooden one opens on a cellar of laboratory "
        "ingredients, mostly rotten, where odd magical effects linger. The "
        "stone one needs a combined Strength of +3 or magic to lift; under "
        "it a stone spiral stair passes the Catacombs into the Dungeon "
        "(whose passages lead back up to the Catacombs), then stops dead "
        "against rock flecked with jade spirals, a sigil, not stone, that "
        "seals the way. Any Aerie nearby raises the alarm and fights anyone "
        "trying to get past it, with grim warnings of what lies below. "
        "Beyond, a narrow shaft ends in a round, damp room ten paces across, "
        "its walls carved with old battles that may hold clues to House "
        "Flambeau's past. Set in the floor is an iron disc five paces wide "
        "engraved with the seven-sworded wheel; it sounds solid but hollow "
        "beneath. It baffles any divination of level 40 or less (a constant "
        "PeVi 40 effect over the room). This is the Iron Door. It has been "
        "here from the start, no one knows who made it, and tampering with "
        "it has been forbidden since Apromor's day.",
        "The Grand Library. A great hall of charred oak tables. Many of its "
        "books burned in the Diedne assault, when one of the attackers set "
        "herself alight here; restoring the ashes might give back rare and "
        "potent texts, but most of what survived was carried off when the "
        "survivors left.",
        "Inirelte's Tower. The third tallest, built by Prima Inirelte and "
        "left empty of laboratories after her death. It was enchanted as her "
        "talisman through the Mystery of Hermetic Geometry. On its top floor "
        "of three, her sanctum still holds a few old Hermetic "
        "texts, kept intact by strong magic and guarded by stronger "
        "traps.",
        "The Catacombs. A wide warren of caves under the covenant: "
        "specialist laboratories, small libraries, rooms for arcane uses and "
        "stranger chambers, and the tombs of the covenant's magi and several "
        "Primi of Flambeau, their bodies mummified by the dry air. Some of "
        "their ghosts walk here, keys to the covenant's past, though death "
        "has blurred and twisted what they remember.",
        "The Shrine of the Aerie. Deep in the Catacombs, the clan's holiest "
        "place: a cavern of crystal seams flashing with colour, a waterfall "
        "roaring at one end, and carvings made over many generations. Its "
        "calm tempts visitors to sit and forget their troubles (a "
        "Personality Trait roll, perhaps; it is not magic).",
        "The Aerie Clan. Magic humans who lived here before any wizard; "
        "their tales tell of beating off Roman wizards and Carthaginian "
        "sorcerers before the sahirs enslaved them. Delendar freed them, "
        "and they have served him and his heirs, the Primi of Flambeau, "
        "ever since; they wait for a living magus to come and claim the "
        "inheritance. They know no life but that of covenfolk and go on as "
        "if Val-Negra still thrived. They look drab and almost alike, have "
        "classical Latin names and write in Latin. They hold that each "
        "generation is reborn from its elders, though nothing proves it. "
        "Each adult has Magic Might 10 (Mentem; companions 20), speaks mind "
        "to mind with any other Aerie (Silent Speech), and turns invisible "
        "when standing still and silent; a typical Black Guard fights with "
        "long sword and round shield (Attack +12, Defence +11, Damage +8, "
        "Soak +7). They are led by twins always named Romulus, Autocrat of "
        "the Interior, who wants Val-Negra kept closed, and Remus, Autocrat "
        "of the Exterior, who wants to reach out (Might 33 and 32, each "
        "with an Aura of Rightful Authority).",
        "Abaddon of Tytalus. A Living Ghost (Magic Might 50, Mentem), the "
        "last magus of Val-Negra, whom the Aerie serve devotedly; one of the "
        "most feared necromancers in the Order. His haunt is the whole "
        "covenant, and he likes to conjure and possess a strong young body "
        "to pass for a living man. He is wary of strangers at first but can "
        "come to trust them, give them casting tokens for the Aegis, and ask "
        "for help with neglected work or a stronger Aegis; he could anchor a "
        "saga of restoring Val-Negra. A true Tytalus, he enjoys puzzling and "
        "provoking his guests. Personality: Obsessed +3, Ruthless +2, "
        "Eclectic +5; reputed a Necromancer 3 (Hermetic), with Hermetic "
        "Prestige 4.",
        "Vis: each Aerie's brain holds 2 pawns of Mentem vis; some of the "
        "wild plants in the ruin bear vis, and Astella's garden once yielded "
        "vis and herbs of virtue. Unclaimed.",
    )


def _hidden() -> str:
    return paragraphs(
        "The Iron Door holds the Adulteration of Flambeau: the magical "
        "residue of the Founder's Twilights, built from his mistakes, base "
        "desires and failings (an Adulteration as Houses of Hermes: Mystery "
        "Cults describes them; House Criamon knows of such things). It is "
        "not Flambeau, who is long dead or gone into Final Twilight, but it "
        "believes it is, and does not understand why it cannot leave. Loose, "
        "it would lay the country waste in mad rage. It is a Malignancy of "
        "Magic Might 65 (Ignem), Wrathful +5, Proud +3, Hard-Hearted +2, "
        "with the Founder's fire spells as powers (Pilum of Fire, Ball of "
        "Abysmal Flame, Arc of Fiery Ribbons, a burning aura, any non-ritual "
        "Ignem effect up to level 50), flight, a body until sunrise or "
        "sunset as a bald, sun-darkened man of nearly sixty in a coarse "
        "brown robe, rituals that curse a victim with Deficient Form "
        "(Ignem) or Incompatible Arts, and awareness of everything in the "
        "fortress's level. It cannot act beyond the door while the ward "
        "holds. It hates Moors and sahirs and attacks them on sight. Its "
        "full stat block is the book's.",
        "The Diedne archmagi of 1012 broke the door's ancient seal, made by "
        "a lost Rite of Fenicil that kept it forever, and released the "
        "Adulteration, which destroyed them. The two surviving defenders, "
        "both archmagi, overpowered it and closed the door again, but the "
        "seal was gone; the round Hermetic ward they cast in its place holds "
        "it in, yet breaks if anyone simply opens the door, which is "
        "physically easy. This is why the Quaesitors hid the truth and "
        "barred the covenant's return. The door probably dates from after "
        "Delendos built the Black Tower, by him or another magus; the "
        "legend that it is as old as the Aerie, and holds demons, is wrong.",
        "Abaddon was one of the two who resealed the door. He gave up his "
        "life to guard it and the covenant forever, watches the ward, and "
        "stands ready to recast it. He keeps the Aegis up through the "
        "Mystery of Hermetic Empowerment, often by binding the ghosts of "
        "former members, who volunteer; hidden laboratories in the "
        "Catacombs let him make each Aegis item from lab texts in a season, "
        "and his spirits power it two or three times before release. "
        "Val-Negra's old wealth, and supplies from the Haruspex, keep him in "
        "vis for centuries. His talisman stores many useful spells, and he "
        "may know unique Mysteries of spirit magic.",
        "The 'watchers' of Perdut are Aerie who still walk unseen among the "
        "villagers now and then. Romulus and Remus are renewed when twins "
        "are born: old and young pairs hold a secret rite at the Shrine, and "
        "the young emerge with the elders' minds and memories while the "
        "elders vanish; Remus holds secret knowledge. Priamitus may have "
        "hidden the original scroll of a lost Mercurian ritual somewhere in "
        "the covenant.",
    )


def _library(provence: Provence) -> list[Book]:
    """The libraries the book names, with no covenant to own them: they
    file under the saga, linked from the place."""
    saga = provence.b.saga
    made: list[Book] = []
    for name, description in (
        (
            "The libraries of Val-Negra",
            "What is left of the largest covenant library of its age. The "
            "Grand Library's books mostly burned in the Diedne assault of "
            "1012, and the best of the rest left with the survivors; its "
            "ashes, if magic can restore them, might yield rare and powerful "
            "texts. Inirelte's sanctum, atop her tower, keeps a handful "
            "of old Hermetic texts, kept intact by strong magic "
            "and guarded by stronger traps. The Primus's sealed seventh "
            "floor of the Black Tower has a tiny private library, and the "
            "Catacombs several small ones, with Abaddon's lab texts. The "
            "book names no titles or levels.",
        ),
        (
            "Priamitus's scroll of Set the Stones of the Via",
            "Priamitus of Mercere, founder of the Hermetic Cult of Mercury, "
            "is thought to have hidden somewhere in Val-Negra the original "
            "scroll of this lost Mercurian ritual, one of the 37 Great "
            "Rites, which binds consecrated milestones into a Via Mercuria. "
            "A text of the ritual gives Insight for bringing True "
            "Mercurian Road Magic within Hermetic theory (+6 to the "
            "Intelligence stress roll, and +1 for each point above 4 in the "
            "ritual's Arcane Ability, to +3). Aedes Mercurii keeps casting "
            "notes of it, and a full copy may lie in Magvillus's Library of "
            "Fenicil.",
        ),
    ):
        book = Book(
            id=storage.generate_unique_id(name, [x.id for x in saga.books]),
            name=name,
            type="Other",
            description=description,
        )
        saga.books.append(book)
        made.append(book)
    return made


def finish(provence: Provence) -> None:
    site = provence.places.get("val_negra")
    if site is None:
        return
    mountain = next(
        (p for p in provence.places.values() if "Perditu" in p.name),
        provence.places.get("pyrenees"),
    )
    if mountain is not None and site.place_id is None:
        site.place_id = mountain.id
    for name, note in (
        ("Aedes Mercurii", "Founded by magi who left it; claims its legacy"),
        ("Castra Solis", "Took its place as domus magna of House Flambeau"),
    ):
        try:
            covenant = provence.covenant_named(name)
        except KeyError:
            continue
        provence.b.link(site, "covenants", covenant, note)
