"""The saga the book offers (LFI chs 7-9, pp. 62-87), for the storyguide.

Six dormant threats: the two arcs, "Fire and Song" and "Spider in the
Ice", with a stage at each year of the book's timeline (p. 76) and each
later chapter by its title; "Blood of Innocence", the opening adventure,
stage by stage; the seeds "The Dragon's Bane" and "An Eye on the North";
and "The Toframanna Saga", which holds the chapter's advice. The book says
its saga is not official history (p. 67), so all of it waits to be begun.

Also the people and places of the opening adventure: the covenant of
Wormhout and its four sketched magi, De Panne, the Red Lion, Exeter, Lord
Peter's manor, Carnac; Lord Peter and the child Brighde as converted
characters; the printed creature blocks (the Serpent of Thoth, Whisper,
Lord Peter's men, the walking corpses, the thingmen); and three groups.
Chapters 7 to 18 are for storyguides, so a record's summary says only what
any traveller could learn, and the rest is in its secrets.

Creature blocks follow the pack's readings (see the package docstring):
Might, Characteristics, combat totals and Might costs as printed,
Abilities renamed, Init its owner's Quickness less the cost. Nothing in
these blocks supports a Form for their Mights, so none is set.
The Icelandic ranks (pp. 65-66) have no Virtues in the catalog and stand
in words on their own record."""

from __future__ import annotations

from typing import Any

from ...models import BodyVis
from ...models.world import Neighbour
from ..builder import (
    Builder,
    StatBlock,
    characteristics,
    dormant,
    paragraphs,
    secrets,
)
from ..fourth import Fourth, convert

S = Builder.stage
DATED = "Fixed dates"
TRACK = "A track"
BONISAGUS = "house_bonisagus"
EX_MISCELLANEA = "house_ex_miscellanea"
GUERNICUS = "house_guernicus"
TYTALUS = "house_tytalus"
VERDITIUS = "house_verditius"
#: A person's Fatigue levels, as these blocks print them.
FATIGUE = "OK, 0, -1, -3, -5, Unconscious"
#: The Definitive Edition's Confidence for an important creature.
CONFIDENCE = (1, 3)
#: The book's warning, which every record of its saga carries.
NOT_HISTORY = (
    "The book offers this as one saga, not as official Mythic history (p. 67)."
)


def build(b: Builder) -> None:
    wormhout = _wormhout(b)
    de_panne = _low_countries(b)
    manor = _england(b)
    _carnac(b)
    _characters(b, de_panne)
    _creatures(b, manor)
    _groups(b)
    _arcs(b)
    _blood_of_innocence(b, wormhout)
    _seeds(b, de_panne)
    _advice(b)


def _found(b: Builder, part: str) -> Neighbour | None:
    """The first place another part made whose name holds `part`."""
    return next(
        (n for n in b.saga.neighbours if n.kind == "place" and part in n.name), None
    )


def _without(stat: StatBlock, *names: str) -> StatBlock:
    """`stat` without the entries convert gives every magus, for a person
    who is not one."""
    kept: list[Any] = [v for v in stat.get("virtues_flaws", []) if v not in names]
    stat["virtues_flaws"] = kept
    return stat


# -- Wormhout --


def _wormhout(b: Builder) -> Any:
    site = b.place(
        "The Wormhout Regio",
        summary=(
            "A stretch of forest a mile outside the town of Wormhout, reached "
            "by a clear path that passes between two worn stone pillars."
        ),
        secrets=paragraphs(
            "A two-tier magical regio, with the mundane level guarded by a "
            "powerful Mentem spell (pp. 77, 79). Markus's parens designed its "
            "gates and seals, the covenant's main defence (p. 78).",
            "The town lies about 42 miles east of Calais and 16 miles southwest "
            "of De Panne (p. 77).",
        ),
        levels=[
            b.level(
                "The Manor Level",
                3,
                notes=secrets(
                    "",
                    "A manor house among grogs' quarters, stables, a smithy and "
                    "a meeting hall, entered between the two stone pillars in the "
                    "forest. Hermetic visitors are lodged in the manor house. "
                    "Steps at the far end of its main hall rise to a mosaic floor "
                    "(p. 79).",
                ),
            ),
            b.level(
                "The Tower Level",
                5,
                notes=secrets(
                    "",
                    "A huge tower of sanctums, library and council chamber, "
                    "entered between two carved pillars on the mosaic in the "
                    "manor hall; only the covenant's magi and consortes may pass "
                    "(p. 79).",
                ),
            ),
        ],
    )
    b.town(
        "Town of Wormhout",
        summary=(
            "A town beside a forest, which has grown greatly in trade "
            "and people over the last three centuries."
        ),
        secrets="The covenant of Wormhout lies in the forest just outside (p. 77).",
    )
    covenant = b.covenant(
        "Wormhout",
        founded=886,
        place=site,
        level=2,
        summary=(
            "A covenant of the Normandy Tribunal, in a forest outside the town "
            "of the same name."
        ),
        secrets=paragraphs(
            "The book sets it in the Normandy Tribunal (p. 77). This pack holds "
            "no Tribunal, so it stands on no roster here. Its magi are given "
            "only brief statistics; the book suggests about 1200 xp in Arts and "
            "120 in Abilities for a storyguide who fleshes them out (p. 78).",
            "Four members, most in middle age, none near final Twilight. It "
            "was built on its founders' cooperation, and its vis sources and "
            "its mundane and magical security are excellent (p. 79).",
            "Founded in 886 with Vindolanda's sponsorship, and bound to it by a "
            "treaty with no time limit, invoked by agreed tokens (pp. 77, 80). "
            "Vindolanda was reported destroyed 331 years before the saga opens.",
            "The book's saga opens here: the new magi are lodged and fed and "
            "given some study time in exchange for scribing, and are waiting "
            "for an invitation from any covenant at all (p. 77). Vera and "
            "Iphimedeia are away on an investigation when Donncadh arrives "
            "(p. 80). Magi who refuse the mission are told to leave. Markus "
            "and Cornelius offer two seasons of study rights for it and may "
            "be pressed to four.",
            "After the first adventure Iphimedeia investigates Vindolanda's "
            "survival, is reassured, and agrees to register it in the Normandy "
            "Tribunal; Wormhout honours its debt and stays an ally. Its library "
            "is open to the magi at its standard fee of 2 pawns of vis a season "
            "(p. 75). The book leaves the library's contents to the storyguide.",
        ),
    )
    _wormhout_magi(b, covenant)
    return covenant


def _wormhout_magi(b: Builder, covenant: Any) -> None:
    markus = b.magus(
        "Markus of Verditius",
        covenant=covenant,
        house=VERDITIUS,
        age=97,
        traits={"Cautious": 5, "Meticulous": 4, "Brave": -1},
        summary=(
            "The leader of Wormhout: a thickset man of average height, dark "
            "brown hair and green eyes, an expert in sacred architecture."
        ),
        secrets=paragraphs(
            "Looks 35. Size 0, Confidence 3, Twilight Points 9. Reputations: "
            "Contemptibly Cautious 3 with Flambeau and Tytalus magi; Promising "
            "Theoretician 2 with Verditius and Bonisagus magi (p. 78).",
            "A Vim specialist who has so far escaped temporary Twilight by "
            "caution and luck, though the last brush nearly took him. He knows "
            "few spells and invests a device with any effect he wants. He "
            "commissioned his longevity potion from the Order's foremost "
            "Verditius alchemist. He dreads casting the Aegis, which his "
            "enduring magic lets last up to ten years, and is researching a way "
            "to master rituals and cast them safely.",
        ),
    )
    markus.aging.apparent_age = 35
    vera = b.magus(
        "Vera of Bonisagus",
        covenant=covenant,
        house=BONISAGUS,
        age=92,
        traits={"Clear Thinking": 3, "Considered": 2, "Uncompromising": 1},
        summary=(
            "A thin, tiny woman with greying blond hair and blue eyes, and an "
            "important powerbroker in the Normandy Tribunal."
        ),
        secrets=paragraphs(
            "Looks 50. Size -1, Confidence 3, Twilight Points 15. Reputation: "
            "Formidable 3 with the Normandy Tribunal (p. 78).",
            "Her high ideals have made her enemies, even among quaesitores. Her "
            "law, certamen and, rarely for a Bonisagus, Wizard's War impress "
            "even Flambeau and Tytalus. She specialises in deception and "
            "illusion, which her master taught as the proof that truth is hard "
            "won, and uses them to expose lies. She often goes with Iphimedeia "
            "on investigations.",
        ),
    )
    vera.aging.apparent_age = 50
    iphimedeia = b.magus(
        "Iphimedeia of Guernicus",
        covenant=covenant,
        house=GUERNICUS,
        age=89,
        traits={"Dedicated": 3, "Judgmental": 3, "Brave": 2},
        summary=(
            "A quaesitor: a tall, strongly built woman with light brown hair "
            "and brown eyes, often called on to look into Hermetic crimes."
        ),
        secrets=paragraphs(
            "Looks 40. Size 0, Confidence 3, Twilight Points 17. Reputations: "
            "Impartial 3 with the Normandy Tribunal; Dangerous 3 with guilty "
            "magi (p. 78). The book calls her a quaesitor on p. 75.",
            "Respected, with powerful enemies made by her impartial justice. An "
            "Intellego specialist, sharpened by her rivalry with Vera. Few in "
            "Normandy doubt she can find a sigil on illegal magic however old, "
            "and several Marched magi have found illusion and masking useless "
            "before her (pp. 78-79).",
        ),
    )
    iphimedeia.aging.apparent_age = 40
    cornelius = b.magus(
        "Cornelius of Verditius",
        covenant=covenant,
        house=VERDITIUS,
        age=81,
        traits={"Obsessive": 3, "Patient": -2, "Practical": -1},
        summary=(
            "The youngest magus of Wormhout: a lean, shortish man with black "
            "hair and green eyes, a maker of automata."
        ),
        secrets=paragraphs(
            "Looks 32. Size 0, Confidence 3, Twilight Points 10. Reputations: "
            "Apolitical 2 and Maker of Automata 3, both with the Normandy "
            "Tribunal (p. 79).",
            "He wants an automaton that truly learns, which no Hermetic maga "
            "has made; his best play chess and work puzzles. They watch the "
            "covenant's vis sources, with magic from Vera and Iphimedeia that "
            "stays hidden and pierces concealment, on covenant land only and "
            "against concealments only. Some call that scrying; Iphimedeia "
            "would argue that entering under concealment is itself magical "
            "spying. No test case has been brought.",
        ),
    )
    cornelius.aging.apparent_age = 32


# -- Flanders --


def _low_countries(b: Builder) -> Neighbour:
    de_panne = b.town(
        "De Panne",
        population=5000,
        summary=(
            "A large Flemish port town of about five thousand souls, half a "
            "mile from its beach and docks, smelling of soot and fish. Fishing "
            "huts line the shore and old docks run far out over the shallows."
        ),
        secrets=paragraphs(
            "The book's suggested mainland base for Spider in the Ice; it may "
            "be moved anywhere in Mythic Europe, and a second storyguide could "
            "run stories here (p. 70). Earthen banks replace the land near the "
            "waterfront (p. 80).",
            "Pan Caudarax keeps a hoard here, and has promised to raze the town "
            "only if that hoard is robbed (p. 63). Once the saga is under way "
            "Redcaps deliver and collect at Iain's house and may not tell other "
            "magi where it is (p. 75). The local Redcap trades vis on the magi's "
            "behalf: a year for each exchange, at most 9 pawns at a time, and a "
            "pawn charged for every three.",
        ),
    )
    b.place(
        "The Red Lion",
        inside=de_panne,
        realm="",
        summary=(
            "A cheerful inn of three joined buildings in De Panne, kept by a "
            "grey-bearded man named Pol and his wife Richilda. Rooms are "
            "affordable."
        ),
        secrets=(
            "Redcaps often stay here and the keeper is especially friendly with "
            "the Order. Asked politely, Pol and Richilda say they heard the "
            "Englishmen talk of going back to Exeter (pp. 80-81)."
        ),
    )
    b.place(
        "Iain Scot's House",
        inside=de_panne,
        realm="",
        summary=(
            "A merchant's townhouse facing the square of De Panne, its back to "
            "the docks."
        ),
        secrets=(
            "Headquarters of Iain's large trading company, whose ship waits in "
            "port. Burned in Lord Peter's raid; as the magi arrive the smoke is "
            "still rising, and Donncadh blames threats from overseas debtors "
            "(p. 80)."
        ),
    )
    return de_panne


# -- England --


def _england(b: Builder) -> Neighbour:
    b.town(
        "Exeter",
        summary=(
            "A busy trading port on the river Exe, two days' sail from De Panne, "
            "with a quay for seagoing ships."
        ),
        secrets=(
            "The ship that fled De Panne lies here, and its captain fears Lord "
            "Peter. Quiet approaches and money get answers; public quarrels get "
            "only angry words. The crew were hired for a raid, and were shocked "
            "at its being in the middle of the town, and at the fire. Commoners "
            "and merchants here think little of Lord Peter (p. 81)."
        ),
    )
    coombe = b.place(
        "Coombe",
        realm="",
        summary="A village at the edge of Dartmoor, in hilly country.",
        secrets=(
            "Its people avoid the manor nearby, and the servants' families have "
            "heard nothing of them for months (p. 81)."
        ),
    )
    return b.place(
        "Lord Peter's Manor",
        inside=coombe,
        realm="",
        summary=(
            "A manor house on the edge of Dartmoor near Coombe, cut off by the hills."
        ),
        secrets=paragraphs(
            "Lightly guarded: six men remain when the magi come, in and around "
            "the house, and the servants are locked in their sleeping chambers. "
            "Set free they are grateful, and wish only to run home to their "
            "villages (pp. 81-82).",
            "Lord Peter's private chambers hold what serves a diabolist as a "
            "laboratory. In the middle is a stone archway capped with the "
            "stolen gatestone, which opens to Scartaris when the keystone is "
            "touched and a phrase spoken, and stays open under concentration. "
            "Ugly rumours tie him to disappearances among moorland farmers.",
        ),
    )


def _carnac(b: Builder) -> None:
    b.place(
        "Carnac",
        summary="The great megaliths of Carnac, in France.",
        secrets=(
            "One of the lost gateways of the Cult of Thoth stands here, leading "
            "to the Kerlingarfjoll valley. Hetep led Damhan-allaidh through it, "
            "he used it again to escape to Scotland after 808, and Victor found "
            "it in 845 and took its gatestone to Vindolanda (pp. 71-72). One of "
            "Lord Peter's ancestors served Damhan-allaidh here (p. 83)."
        ),
    )


# -- people with blocks --


def _characters(b: Builder, de_panne: Neighbour) -> None:
    peter = b.magus(
        "Lord Peter",
        covenant=None,
        house="",
        age=39,
        type="companion",
        summary=(
            "A landed knight of Devon, tall and thin, with Norman features and "
            "a short black beard, who usually wears a long red cloak. His "
            "family came to England with the Conqueror."
        ),
        secrets=paragraphs(
            "An English diabolist, promised more magical power for freeing "
            "Hetep. Found his grandfather's occult books on his death; Hell has "
            "watched his family since an ancestor served Damhan-allaidh near "
            "Carnac. He blackmails Falkes de Bréauté, acting Earl of Devonshire "
            "(p. 83). The characters kill him in the opening adventure (p. 76).",
        ),
    )
    stat, _ = convert(
        "lord_peter",
        Fourth(
            age=39,
            apparent=None,
            characteristics=characteristics(2, 0, -1, 1, 1, 2, 1, 0),
            confidence=4,
            twilight=0,
            decrepitude=0,
            virtues=(
                ("Landed Noble", 5),
                ("Demonic Familiar", 4),
                ("Blackmail", 2, "Falkes de Bréauté, acting Earl of Devonshire"),
                ("Strong-Willed", 1),
                ("Educated", 1),
                ("Reckless (Minor)", 1),
                ("Susceptible to Divine Power", -4),
                ("Tainted With Evil", -2),
                ("Bad Reputation", -1, "kidnapper"),
                ("Dark Secret", -1, "diabolist"),
                ("Obligations", -1, "to Hell"),
            ),
            granted=(("Offensive to {being}", {"being": "animals"}),),
            abilities=(
                ("Awareness", 3, "ambush"),
                ("Bargain", 4, "demons"),
                ("Charm", 2, "nobles"),
                ("Common Law", 3, "Common"),
                ("Guile", 2, "activates"),
                ("Folk Ken", 1, "nobles"),
                ("Intrigue", 2, "English court"),
                ("Leadership", 3, "men-at-arms"),
                ("Occult Lore", 6, "demons"),
                ("Speak English", 5, ""),
                ("Speak French", 4, "Norman"),
                ("Speak Latin", 5, ""),
                ("Scribe Latin", 2, ""),
                ("Single Weapon", 5, "longsword"),
                ("Weapon and Shield", 5, "longsword and kite shield"),
            ),
            arts={},
            spells=(),
            traits={"Ruthless": 3, "Sadistic": 3, "Sly": 1},
            reputations={"Kidnapper (Newton Abbey)": 1, "Refined (Devon nobility)": 2},
            notes=(
                "Printed combat: Brawl (fist) Init +4 Atk +4 Dfn +3 Dam +1; "
                "Dagger +6, +5, +6, +3; Longsword +9, +8, +10, +4. Soak +15 with "
                "his magical cloak. Printed as Landed Knight, Virtues Demonic "
                "Familiar +4, Blackmail +2 and Reckless +1: the catalog has them "
                "as Landed Noble and as Minor Flaws. English Law is Common Law, "
                "and his Guile's specialty is as printed. Fatigue OK, 0, -1, -3, "
                "-5, Unconscious; Body OK, 0, -1, -3, -5, Incapacitated. LFI p. 83."
            ),
        ),
    )
    b.stats(peter, _without(stat, "The Gift", "Hermetic Magus"))
    brighde = b.magus(
        "Brighde Scot",
        covenant=None,
        house="",
        age=5,
        type="companion",
        summary=(
            "A very bright child of De Panne, daughter of Donncadh Scot and "
            "granddaughter of the merchant Iain, who already has some Latin "
            "and is learning her letters."
        ),
        secrets=paragraphs(
            "Her magical potential is plain to any magus in five minutes. Her "
            "grandfather has shown her the Scartaris sanctum, and she dreams of "
            "being a wizard like him (p. 84). She has the Gift (p. 87).",
            "Kidnapped by Lord Peter and forced to open the gate; possessed by "
            "Hetep; then host to Victor, who imprisons the demon in her and "
            "takes her as his apprentice. He hates controlling her and does so "
            "only at need. Her gauntlet is the story of 1240. A player may run "
            "her, but she does not adventure before that gauntlet (p. 87).",
        ),
    )
    stat, _ = convert(
        "brighde",
        Fourth(
            age=5,
            apparent=None,
            characteristics=characteristics(5, 2, 2, 1, -4, 0, -3, -3),
            confidence=4,
            twilight=0,
            decrepitude=0,
            virtues=(
                ("Incredible Intelligence", 4, "Intelligence"),
                ("Latent Magic Ability", 2),
                ("Strong-Willed", 1),
            ),
            abilities=(
                ("Awareness", 1, "food"),
                ("Folk Ken", 1, "parents"),
                ("Charm", 2, "parents"),
                ("Speak French", 3, "Norman; cute voice"),
                ("Speak Latin", 1, "nouns"),
                ("Scribe Latin", 1, "her name"),
                ("Disputatio", 1, "getting own way"),
            ),
            arts={},
            spells=(),
            traits={"Mischievous": 3, "Curious": 3},
            reputations={"Spoilt (wives of De Panne's merchants)": 1},
            size=-2,
            notes=(
                "Fully grown she will have Str -1, Dex -1, Qik 0 and Size 0. "
                "Soak -2. Printed Virtue Charm +1 has no catalog counterpart and "
                "is left out. Her Gift comes from p. 87; the block prints only "
                "Latent Magical Ability. Fatigue OK, -3, -5, Unconscious; Body OK, "
                "-3, -5, Incapacitated. LFI p. 84."
            ),
        ),
    )
    b.stats(brighde, _without(stat, "Hermetic Magus"))
    _founders(b)
    b.lord(
        "Sir Ivain of De Panne",
        place=de_panne,
        summary=(
            "A landed knight in Flanders, loyal to the French Crown, who carries "
            "a holy sword."
        ),
        secrets="The hero of the seed The Dragon's Bane (p. 63).",
    )


def _founders(b: Builder) -> None:
    """The dead of the old war, in the book's cast list (pp. 71-72)."""
    b.magus(
        "Pralix",
        covenant=None,
        house=TYTALUS,
        age=None,
        summary=(
            "The Tytalus maga who first beat Damhan-allaidh and founded House "
            "Ex Miscellanea."
        ),
        secrets=(
            "Victor's parens. Landed in Northumbria in May 814, beat "
            "Damhan-allaidh in 816, and raised the Ordo Miscellanea from the "
            "witches, druids, beast mages and spirit masters of her army, "
            "becoming prima when it joined the Order (p. 71)."
        ),
    )
    b.magus(
        "Ealasaid, Lady of the Waters",
        covenant=None,
        house=EX_MISCELLANEA,
        age=None,
        summary="A theurgist of the old covenant of Vindolanda, long dead.",
        secrets=(
            "Her line came down from the Romano-Celtic priests of Sulis Minerva "
            "at Bath. She worked out the Carnac gate and rebuilt the gatestones "
            "as Hermetic thaumaturgy. Filia of Morwena and parens of Macomb. "
            "She fled Wales from threats by Diedne magi, reclaimed her lands "
            "with a first sanctum under Glyder Fawr, left it to Macomb, and "
            "moved to the Sea Temple beneath the sea off Devon. Damhan-allaidh "
            "killed her there in 889, and her ghost brought the dome down on him "
            "and Liam (pp. 71-73, 88, 94, 123)."
        ),
    )
    b.magus(
        "Macomb",
        covenant=None,
        house=EX_MISCELLANEA,
        age=None,
        summary="A theurgist of the old covenant of Vindolanda, long dead.",
        secrets=(
            "Ealasaid's filius and an original member, whose sanctum was Glyder "
            "Fawr in Snowdonia. Damhan-allaidh killed him there in 889 (pp. "
            "71-72, 94-95)."
        ),
    )


# -- creature blocks --


def _creatures(b: Builder, manor: Neighbour) -> None:
    b.creature(
        "Serpent of Thoth",
        page="p. 75",
        realm="Magic",
        might=40,
        size=6,
        how_many="Sixty in all",
        confidence=CONFIDENCE,
        tires=False,
        block={
            "characteristics": characteristics(0, 2, 0, 0, 8, 8, 1, 5),
            "traits": {"Determined": 3, "Touchy": 3, "Knowledgeable": 3},
        },
        powers=[
            b.power(
                "Movement",
                1,
                4,
                "",
                does="Carries itself to any point in the Mundane, Magic or "
                "Faerie Realms.",
            ),
            b.power(
                "Gateway",
                0,
                5,
                "",
                does="Bridges the mundane and magical realms, swallowing or "
                "bringing up people and things while it stays incorporeal. With "
                "a magical archway, trilithon or the like this costs nothing; "
                "without one, 5 Might.",
            ),
            b.power(
                "Knowledge of the Subterranean",
                3,
                2,
                "Terram",
                level=40,
                does="InTe 40. Sees or hears whatever happens under the earth, or "
                "knows where anything buried lies.",
            ),
            b.power(
                "Strong Willed",
                0,
                5,
                "Vim",
                does="No magic can compel it to act against its will.",
            ),
        ],
        appearance="A vast snake with a head at either end.",
        notes=(
            "Printed with Tireless Fatigue, Body levels OK, 0, 0, 0, -1, -1, -1, "
            "-3, -3, -5, -5, Banished, and no Soak. The block prints Per twice; "
            "the 0 is read as Pre."
        ),
        secrets=paragraphs(
            "Earth daemons of Thoth, each with its own name, akin to the "
            "Amphisbaena of Hedge Magic p. 76 but far greater. They dug secret "
            "tunnels and hid things in remote caves for him, and helped his "
            "priests build temples in far places; they know every place in the "
            "Magic, Faerie and Mundane Realms (pp. 73-74).",
            "The Gateways (p. 73). A true gateway is two cross-lintels cut in "
            "ritual from one stone and enchanted as bridges to the spirit realm. "
            "A serpent, bought with gifts of vis, joins them: called from before "
            "a lintel, it stretches a mouth over each gate, and travellers pass "
            "quickly through it. It can bar any gate by person or oath-sworn "
            "group, but cannot perceive motive, so coercion and magical "
            "compulsion deceive it. The lore passed from Thoth's priests through "
            "the Cult of Mercury to the Order as the Hermes Portal ritual, in a "
            "weaker form.",
            "Ealasaid rebuilt it as Hermetic thaumaturgy, in notes the magi may "
            "recover. Cut unquarried stone free in ritual, carry it to a "
            "laboratory unseen and untouched by the ritually unclean, split it, "
            "open each half as an invested device and invest a level 40 Rego Vim "
            "effect that calls the serpent and opens the bridge. Then summon a "
            "serpent. She learned 16 of the sixty names and wrote spells for "
            "three, at level 55, in her and Macomb's grimoire.",
            "Daemonic Adjuration of [Name], Serpent of Thoth (ReVi Gen, Special, "
            "Special, Individual, Ritual). The Fourth Edition printing: stress "
            "die + Com + spell level + Penetration + Aura against stress die + "
            "40; each point of margin counts toward the serpent's appearing, "
            "which it does when the points pass its Might. Repeat casts add up, "
            "but are lost at the next sunrise or sunset. It then bargains: 20 "
            "pawns, and 20 more for each gateway pair it already serves, reduced "
            "by half a roll of Com + Bargain + Theurgy + stress die. Under The "
            "Mysteries, casting from text needs Hermetic Theurgy equal to the "
            "spell's magnitude; otherwise a magus learns it and must master it "
            "first. A serpent serves any number of gates, one at a time. The "
            "joined gatestones stop being Arcane Connections to each other.",
        ),
    )
    b.creature(
        "Whisper",
        page="p. 83",
        realm="Infernal",
        might=25,
        size=-3,
        confidence=CONFIDENCE,
        place=manor,
        block={
            "characteristics": characteristics(1, 5, -1, -3, -4, 1, 1, 2),
            "abilities": [
                ("Awareness", 5, "being watched"),
                ("Stealth", 5, "secret observation"),
            ],
            "traits": {"Sly": 5, "Cowardly": 2},
        },
        attacks=[b.attack("Beak or Claw", 3, 2, 6, -5)],
        soak=-2,
        fatigue_levels="OK, -3, -5, Unconscious",
        powers=[
            b.power(
                "Swift Flight",
                0,
                2,
                "Auram",
                level=20,
                does="ReAu 20. Flies ten times as fast as a normal bird and "
                "never tires.",
            ),
            b.power(
                "Mythic Perception",
                5,
                -3,
                "Vim",
                level=40,
                does="InVi 40. Sees through any disguise or illusion, and hears "
                "talk perfectly up to a mile away.",
            ),
            b.power(
                "Eye Peck",
                5,
                -3,
                "Corpus",
                level=30,
                does="PeCo 30. A hit scratches an eye, the Might being spent after the "
                "attack lands. An infection sets in next day and lasts seven "
                "days, blinding that eye; a Medicine or Herbalism roll of 15+ "
                "saves it, or Restoration of the Defiled Body stops the infection "
                "and restores sight.",
            ),
        ],
        vis=[BodyVis(4, "Intellego", "in its eyes")],
        appearance="A crow.",
        notes=(
            "Printed Body levels OK, -3, -5, Incapacitated, Banished. It speaks "
            "by whispering in its master's ear, in a rasp no one else hears and "
            "he follows only with a Perception roll of +6. It never repeats "
            "itself."
        ),
        secrets=(
            "Lord Peter's familiar, once Damhan-allaidh's messenger. Misheard "
            "messages have undone several masters. A coward, it goes back to "
            "spirit form as soon as anyone attacks it."
        ),
    )
    b.creature(
        "Lord Peter's Men",
        page="p. 82",
        how_many="Hired men-at-arms",
        place=manor,
        block={
            "characteristics": characteristics(0, 1, 0, -1, 2, 1, 1, 1),
            "abilities": [
                ("Awareness", 2, "on watch"),
                ("Brawl", 4, "fist"),
                ("Stealth", 2, "raids"),
                ("Single Weapon", 4, "longsword and round shield"),
            ],
            "traits": {"Mercenary": 3},
        },
        attacks=[
            b.attack("Brawl (fist)", 7, 6, 6, 2),
            b.attack("Longsword and Round Shield", 8, 8, 13, 6),
        ],
        soak=3,
        fatigue_levels=FATIGUE,
        equipment="Heavy leather hauberk.",
        notes=(
            "Printed Body levels OK, 0, -1, -3, -5, Incapacitated. Weapon and "
            "Shield 4 is Single Weapon."
        ),
        secrets=(
            "Two dozen die in Scartaris and six stay behind at the manor (p. 82)."
        ),
    )
    b.creature(
        "Walking Corpses",
        page="p. 86",
        realm="Infernal",
        might=10,
        how_many="Varies",
        tires=False,
        attacks=[
            b.attack("Brawling (fist)", 1, 0, -1, -1),
            b.attack("Club", 1, 1, -1, 3),
        ],
        soak=9,
        vis=[BodyVis(1, "Corpus", "in the body; infernally tainted")],
        appearance="Horribly mutilated men, women and children.",
        notes=paragraphs(
            "Size varies from +1 to -2. Printed Body levels OK, 0, -1, -3, -5, "
            "Immobilized; they do not tire. Only cutting muscles and breaking "
            "bones hurts them.",
            "They can be immobilized, but only burning, Christian burial, "
            "laying the head at the feet, or a particular Perdo Vim spell stops "
            "them moving.",
        ),
        secrets="The slain of Snaefellsnes, raised by Hetep (pp. 86, 137).",
    )
    b.creature(
        "Thingmen",
        page="p. 86",
        how_many="A storgodi's following",
        age="14-45",
        block={
            "characteristics": characteristics(0, 0, 0, 0, 1, 1, 0, 0),
            "abilities": [
                ("Profession: Boatman", 2, "fishing"),
                ("Brawl", 3, "dagger"),
                ("Common Law", 2, "procedures"),
                ("Great Weapon", 2, "spear"),
                ("Living Language: West Norse", 4, "farming terms"),
                ("Single Weapon", 2, "longsword and round shield"),
            ],
            "traits": {"Brave": 1, "Loyal": 1},
        },
        attacks=[
            b.attack("Brawl (fist)", 4, 3, 3, 1),
            b.attack("Longsword and Round Shield", 5, 5, 10, 5),
            b.attack("Long Spear", 8, 9, 4, 7),
            b.attack("Dagger", 6, 5, 6, 4),
        ],
        soak=3,
        fatigue_levels=FATIGUE,
        equipment="Heavy leather hauberk.",
        notes=(
            "Icelandic farmers armed for a storgodi. Printed Body levels OK, 0, "
            "-1, -3, -5, Incapacitated. Longshaft Weapon is Great Weapon, Boating "
            "a Profession, Icelandic Law Common Law, and Weapon and Shield Single "
            "Weapon. Printed Confidence 3 is left out."
        ),
        secrets="Thirty ride with Thord Sturluson on Snaefellsnes (p. 86).",
    )


# -- groups --


def _groups(b: Builder) -> None:
    b.faction(
        "The Praeses Septentrionalis",
        summary="The Northern Guard, an old league of Hermetic covenants.",
        secrets=(
            "Vindolanda joined it to guard Scotland against Damhan-allaidh's "
            "return (p. 72). His forces attacked its covenants in 889 and "
            "destroyed them all (pp. 72, 77)."
        ),
    )
    b.faction(
        "The Thothian Watchers",
        realm="Magic",
        summary="Spirits of old Egypt, about whom almost nothing is told.",
        secrets=(
            "Thoth set them to capture and imprison Hetep, but they cannot take "
            "him while he possesses someone. He used to lose them by going back "
            "to Hell, which he now cannot do without undoing his partial "
            "corruption of the stelae. They speak to no one and wait for his "
            "mistake. The book prints no stats. Ealasaid's grimoire holds a "
            "spell to contact them, now of little use (p. 84)."
        ),
    )
    b.faction(
        "The Odd-Karnor Clan",
        summary="A Norwegian family, embroiled in a feud of its own.",
        secrets=(
            "Bjarke Odd-Karnor called in his distant kinsman Einar Gamlisson for "
            "magical help in 1210. Einar stayed seven years and married Yrsa, a "
            "young girl of the clan (p. 69). She and her two sons died in 1218. "
            "The feud is a centuries-old one with the Beogarts, a powerful "
            "family in Iceland (p. 103; see Leif Beogart)."
        ),
    )
    b.faction(
        "The Ranks of Iceland",
        summary=(
            "Who stands where in Iceland: free men, householders, landowners, "
            "great farmers and chieftains, and those with no standing."
        ),
        secrets=paragraphs(
            "The book's social-class Virtues and Flaws (pp. 65-66), with Fourth "
            "Edition points, have no entries in the catalog:",
            "Freeman +0: freeborn, no land or milk animals; must find a place "
            "in a household or as a hut-man. Bondi +1: rents land a year at a "
            "time and may choose an assembly, usually the landlord's godi. "
            "Landowner +2: also owns land, pays thing-tax, may attend the thing, "
            "and may have to ride with his godi to the Althing or pay toward it. "
            "Storbondi +3: rich and influential, with tenant farms and churches, "
            "and Temporal Influence free. Godi +4: holds a godord, appoints "
            "judges and panels, sits on the law council, and has Temporal "
            "Influence free. Storgodi +5: several godords and a riki, one of the "
            "five competing families, rich but unable to keep men-at-arms.",
            "Freedman -1: a dependant of his former owner, with Bad Reputation "
            "(Freedman) 3. Slave -2: property, outside the law. Outlaw -3 to -5: "
            "by the power of the accuser, from a bondi's to a godi's, who hunts "
            "him to the end; killing three other outlaws earns a reprieve.",
            "Every Icelander starts with Icelandic Law 2 and Legend Lore 2. The "
            "wealthy, from landowner up, are usually Educated, which they pay "
            "for (p. 66).",
            "Iceland-born characters (pp. 64-65). Magus-equivalents: Trollson, "
            "traditional galdraman. Mythic companions: seithkona (a Hedge Magic "
            "cunning-woman with a fylgja and Hamfarir instead of Visions, and "
            "Second Sight and Legend Lore instead of the faerie versions), "
            "schooled galdraman (Natural Magician), spirit master. Companions: "
            "witch, seeress or wiseman, viking (anachronistic by 1220), skald, "
            "shapeshifter, bondi, godi. Grogs: berserker (almost unknown by now), "
            "laborer, tenant farmer, thrall.",
            "The book's Fourth Edition Virtue lists (p. 65). Witch (heid), often "
            "with a Jotunn Affinity, some with Scribe Runes, Shapeshift or "
            "Transform: Bane Maker +2, Magical Animal Companion +2, Herbalism "
            "+1, Bad Reputation (pagan) -1, Tainted with Evil -2. Seeress "
            "(volva) or wiseman (visindaman): Divination +4, Visions +2, Second "
            "Sight +1, Premonitions +1. Viking: Mercenary Leader +3 or Wealthy "
            "Merchant +3, Ways of the Sea +4, Well Traveled +1, Social Contacts "
            "+1, Berserk +1, Fury -3, Judged Unfairly -1. Skald: Audio Eidetic "
            "Memory +3, Free Expression +1, Inspirational +1. Shapeshifter: "
            "Shapeshifter +5, Skinchanger +2 or Lycanthrope -3, Outcast -1. "
            "Bondi: Bondi +1, Landowner +2, Storbondi +3, Social Contacts +1, "
            "Obligations -1. Godi: Godi +4, Prestigious Family +1, Feud -1 to "
            "-4. Berserker: Berserk +1, Fury -3, Outcast -1. Laborer: Freeman "
            "or Freedman. Tenant farmer: Bondi. Thrall: Slave.",
            "Magi should come from the Order's heartlands, at first; at most one "
            "player should fill the magus slot with a native magician. One "
            "character needs Premonitions for Spider in the Ice.",
        ),
    )


# -- the arcs --


def _arcs(b: Builder) -> None:
    dormant(
        b.threat(
            "Fire and Song",
            antagonist="Einar Gamlisson, galdraman, against Pan Caudarax",
            moves=DATED,
            realm="Magic",
            place=_found(b, "Hekla"),
            summary=paragraphs(
                "Driven by a galdraman's grief. Einar Gamlisson has sworn to "
                "destroy the family of the dragon that killed his own, and the "
                "characters are caught between them.",
                NOT_HISTORY,
            ),
            secrets=paragraphs(
                "The first arc, before the climax with Damhan-allaidh; its "
                "purpose is to draw the characters into Iceland's daily life, "
                "where magicians live beside farmers and godar, a small picture "
                "of what the Order might achieve in Europe (pp. 67-68). Chapters "
                "11 to 14. Each story follows on the next by the years shown, "
                "but the dates are suggestions, not to be enforced, and other "
                "stories fill the time between (p. 75).",
                "In 1210 Einar went to Norway to help Bjarke Odd-Karnor, and "
                "stayed seven years; he married Yrsa and had two sons. He sailed "
                "home a year ahead of them to repair his farmstead and renew his "
                "ties with the spirits. In 1218 Yrsa and the boys took ship at "
                "Bergen. Powerful Flambeau magi were aboard, going to destroy "
                "the Order of Odin. Their presence roused the landvaettir and "
                "the First Guardian, Pan Caudarax, who burned the ship and went "
                "home to Hekla. Einar does not see that the dragon was defending "
                "Iceland (pp. 69-70).",
                "Einar is cunning and ruthless, and the characters may pity him. "
                "Pan Caudarax is a huge dragon of the Hekla crater, not native "
                "to the north, in Iceland over a thousand years. Bard "
                "Snaefellsass, a powerful trollson, wants the two reconciled and "
                "holds himself guardian of the land the covenant stands on, so "
                "he may become a strong ally (p. 70).",
                "Vis: Vindolanda soon has Rego and Vim sources; beyond that only "
                "stories (the Odadahraun among them) and aura extraction bring "
                "it. The annual Galdramen Hreppur meeting will haggle for vis, "
                "in rough terms such as fire, illusion, warding, weather (p. 75).",
                "The book's dates disagree. The eggs hatch about twenty years "
                "after the settlement of 1222 (pp. 105-106), yet are two years "
                "from hatching in 1230 (pp. 76, 114). Page 106 puts the burned "
                "ship five years back, about 1217, where p. 70 says 1218.",
            ),
            stages=[
                S(
                    "Thord's Feast",
                    year=1221,
                    clues="A local storbaendur accuses the characters of sorcery, "
                    "and they go to the district's spring thing. He suffers the "
                    "side effects of a curse laid on Pan Caudarax's eggs; one "
                    "young dragon is already dead.",
                    stopped="Lifting the curse wins them a place in Iceland, and "
                    "tells them someone holds a deep grudge against a dragon.",
                ),
                S(
                    "Meet the Dragon",
                    year=1222,
                    clues="An invitation to the magicians' meeting at Eldborg. "
                    "The dragon demands to talk to the priests of Hermes, and "
                    "threatens to lay Iceland waste.",
                    stopped="Appeasing Pan Caudarax also wins the right to "
                    "gather vis at certain sites.",
                ),
                S(
                    "Feast of Thanks",
                    year=1223,
                    clues="Bard Snaefellsass invites them to a feast of thanks "
                    "for dealing with the dragon. They learn of Iceland's "
                    "supernatural powers and are drawn into their quarrels, "
                    "above all with a clan of giants.",
                    stopped="Some allies won, some enemies defused.",
                ),
                S(
                    "The Glittering Plains",
                    year=1230,
                    clues="1230 to 1231. The eggs are near hatching and Einar "
                    "tries again to destroy them, then escapes to the Glittering "
                    "Plains, a strange realm underground, where the characters "
                    "follow him and meet its people.",
                    stopped="They may end the feud by diplomacy or violence, and "
                    "may find the Obsidian Temple.",
                ),
            ],
        )
    )
    dormant(
        b.threat(
            "Spider in the Ice",
            antagonist="Damhan-allaidh and the demon Hetep",
            moves=DATED,
            realm="Infernal",
            place=_found(b, "Kerlingarfjoll"),
            summary=paragraphs(
                "Driven by the Order's oldest feud. Damhan-allaidh, the Spider, "
                "and the demon Hetep plot from Iceland to bring the Order down, "
                "and a hidden valley temple of Thoth is the prize.",
                NOT_HISTORY,
            ),
            secrets=paragraphs(
                "The second arc: Chapter 9 brings the characters to Iceland and "
                "Chapters 15 to 17 end it, about forty years on (pp. 67-68). The "
                "fate of Damhan-allaidh, the valley temple and Vindolanda are at "
                "the storyguide's discretion. Its two seats are Iceland and De "
                "Panne, which suits a second storyguide (p. 70). Dates are "
                "suggestions (p. 75).",
                "The valley. About 2000 BC priests of Thoth under the legendary "
                "Setna followed spirits to a mist-shrouded valley at Iceland's "
                "heart, and after years broke the mist with a spell. An obsidian "
                "block carved into an arch stood there. They built a temple round "
                "it and opened a gateway; few who entered came back, but those "
                "who did had multiplied power. They made lesser gateways, and "
                "when Egypt fell the priests were scattered and the ways lost "
                "(pp. 70-71).",
                "The Spider. A Pictish magician drawn to goetia, he got a reed "
                "scroll naming Hetep in 680 and made a cardinal pact: ancient "
                "knowledge and the safest hiding place for his soul. Hetep took "
                "him by Carnac to the valley and hid inside him. Setna's spirit, "
                "for once deceived, let him study the seven stelae for four "
                "seasons while Hetep corrupted them; then Setna saw it, fought "
                "him, and he fled through the seven doors into the Glasvellir "
                "regio. He came out of the Snaefell crater in 730. The gate no "
                "longer answers him; Hetep says to wait for Setna to weaken "
                "(p. 71).",
                "The wars. He refused the Order's offer, and his blood sacrifice "
                "and demon cults brought Flambeau and Tremere against him. He "
                "beat them in 808, then left by Carnac for Scotland. Pralix of "
                "Tytalus landed in Northumbria in May 814 and in two years beat "
                "him with local wizards; he escaped. She raised the Ordo "
                "Miscellanea from her army, and Trianoma brought it in as House "
                "Ex Miscellanea (p. 71).",
                "Vindolanda. Victor, Pralix's apprentice, whose gauntlet was "
                "surviving the war, founded it on a supply fort of Hadrian's "
                "Wall with theurgists Ealasaid and Macomb and gruagachan Iain "
                "and Liam. In 845 he found the Carnac gate and brought its stone "
                "home; seven years on it was deciphered and the valley found. "
                "Ealasaid made Hermetic gatestones in three more years, and each "
                "magus built a linked sanctum: Victor's in the Scartaris peak of "
                "Snaefell, the others beneath the sea off Devon and in Snowdonia "
                "(p. 72).",
                "The battle of wills. They captured Hetep in 875 and found him a "
                "fallen spirit of Thoth. Victor designed a spell of wills to "
                "turn him, which ends only with one's defeat, and the theurgists "
                "warded him in with him. It began in 888, and Iain's party left "
                "with the Scartaris gatestone. In 889 the Spider destroyed the "
                "Northern Guard and led the attack on Vindolanda; Ealasaid and "
                "Macomb died. Liam escaped. In 890 Tremere and Flambeau routed "
                "the Spider's forces, and he and Liam were buried in Ealasaid's "
                "collapsing sanctum under 50 meters of sea, their external souls "
                "keeping them alive. His last followers fled to Shetland and "
                "some to Iceland, and Hetep's minions still hunt the sanctum "
                "(pp. 71-73).",
            ),
            stages=[
                S(
                    "Blood of Innocence",
                    year=1220,
                    clues="The characters are sent to help Iain Scot, an old ally "
                    "of their covenant. His family guards the gatestone to "
                    "Victor's sanctum; a diabolist takes it, kidnaps Brighde and "
                    "forces her to open the gate, and the characters follow him "
                    "to Iceland and find Victor and Hetep locked in battle. "
                    "Played out in the story of the same name.",
                    stopped="The diabolist dies, Brighde is possessed by Hetep, "
                    "then by Victor to bind the demon, and the characters are "
                    "invited into Vindolanda and make Iceland their base.",
                ),
                S(
                    "Brighde's Gauntlet",
                    year=1240,
                    clues="Her gauntlet is to trick Hetep into showing where "
                    "Damhan-allaidh's body lies. He makes for Old Vindolanda and "
                    "opens a hidden gatestone to Ealasaid's secret sanctum.",
                    ignored="As planned, Hetep tricks Brighde and gets away in "
                    "Damhan-allaidh's body, and Victor must sacrifice himself to "
                    "save her.",
                ),
                S(
                    "Spider Through Mist",
                    year=1256,
                    clues="Hetep and Damhan-allaidh break into the Kerlingarfjoll "
                    "valley and the Obsidian Temple.",
                    ignored="Hetep corrupts the stelae and begins to corrupt all "
                    "magical writing in the world, with Damhan-allaidh guarding "
                    "the temple.",
                    stopped="Hetep is thwarted and the magi win.",
                ),
                S(
                    "Into the Gateway",
                    year=1260,
                    clues="The magi finish Ealasaid's work on the Obsidian "
                    "Gateway ritual. As things stand, they must help defend the "
                    "stelae or break in to destroy them.",
                    stopped="A last battle with Damhan-allaidh, Hetep or both "
                    "ends the arc.",
                ),
            ],
        )
    )


def _blood_of_innocence(b: Builder, wormhout: Any) -> None:
    dormant(
        b.threat(
            "Blood of Innocence",
            antagonist="Lord Peter, an English diabolist seeking Hetep's favour",
            moves=TRACK,
            realm="Infernal",
            summary=paragraphs(
                "Driven by a diabolist's bargain. A wounded merchant is carried "
                "into Wormhout, his house burned and his granddaughter stolen, "
                "and the treaty he invokes sends the covenant's young guests "
                "after her.",
                NOT_HISTORY,
            ),
            secrets=paragraphs(
                "The saga's opening adventure, of 1220 (ch. 9). During Pralix's "
                "war Hetep maimed Iain's Gift. He kept his External Soul, joined "
                "Vindolanda as a full magus, and hid with the Scartaris gatestone "
                "in 888. He searched the world for centuries, learned Natural "
                "Magic, grew rich as a merchant, and settled in De Panne in 1182, "
                "where he married. In 1219 he gave up on Victor and went to ask "
                "Cad Gadu for aid, was turned away for lack of an invitation, and "
                "a diabolist followed him home (p. 77).",
                "The oath the magi swear and the charter are on the covenant of "
                "Vindolanda's record (p. 85). Donncadh and Brighde are both "
                "Gifted and may become player characters; Donncadh could stay a "
                "Mythic Companion (p. 87).",
            ),
            stages=[
                S(
                    "Fate Lends a Hand",
                    at=1,
                    clues="A cart reaches Wormhout: Iain the Scot wounded, with "
                    "his wife Eleanor, son Donncadh and daughter-in-law Mari. "
                    "Donncadh, consors of Vindolanda, invokes the treaty of 886 "
                    "before Markus and Cornelius, who send the characters.",
                    stopped="The magi accept. Donncadh tells of the raid and of "
                    "one stolen black stone engraved with magic, and no more. He "
                    "holds an Arcane Connection to his daughter; an Intellego "
                    "Corpus spell of level 10 gives her direction, or whether she "
                    "lives, and takes him half an hour.",
                ),
                S(
                    "De Panne",
                    at=2,
                    clues="Smoke still rises from Iain's house. Dockworkers saw an "
                    "English ship leave at night, soon after the fire. At the Red "
                    "Lion they heard talk of Exeter.",
                    stopped="Iain's ship is still in port and Donncadh takes it.",
                ),
                S(
                    "Exeter",
                    at=3,
                    clues="Two days' sail up the Exe. Iain's sailors know the ship "
                    "that fled. Quiet money gets the name of Lord Peter.",
                    stopped="They get directions to his manor.",
                ),
                S(
                    "Lord Peter's Manor",
                    at=4,
                    clues="The magician has rebuilt the gateway and forced "
                    "Brighde to open it. Six guards remain, and the servants are "
                    "locked in.",
                    stopped="Donncadh opens the gate, and may have to explain "
                    "where it leads.",
                ),
                S(
                    "Scartaris Sanctum",
                    at=5,
                    clues="Two dozen corpses and broken gargoyles fill the first "
                    "chamber. In Victor's laboratory two interlocked circles hold "
                    "domes of ice: a tall man in Roman robes and a squatting "
                    "dog-like thing, frozen, joined by silver ribbons from their "
                    "eyes. Brighde is tied to a chair and Lord Peter is at a "
                    "ritual over the demon's ward, which cracks when he is "
                    "interrupted.",
                    ignored="Fighting Lord Peter and Whisper, the characters see "
                    "the host body shatter and the ribbons strike Brighde. Hetep "
                    "takes her, shifts her to his beast shape, attacks Donncadh "
                    "once and flees down a hidden tunnel that collapses behind "
                    "him. Victor's ribbons strike a magus, Penetration 50 + stress "
                    "die, and the first to fail falls in a fit, carrying him as a "
                    "ghost.",
                ),
                S(
                    "Victor Offers a Deal",
                    at=6,
                    clues="Victor puts the magi to sleep (as Rego Mentem 25, "
                    "Penetration +50) and meets them in his Morphean Landscape, at "
                    "a round marble table with armed men of about 870 along the "
                    "walls. He offers full membership and answers briefly: he made "
                    "no pact, and sought Damhan-allaidh or his soulstone.",
                    stopped="They swear the oath and wake. His host is led to a "
                    "grimoire of tunnelling spells, and they clear the tunnel in "
                    "about 12 hours, coming out halfway up Snaefell's southern "
                    "slope.",
                ),
                S(
                    "Snaefellsnes",
                    at=7,
                    clues="Farmsteads burn between them and the coast, and "
                    "mutilated dead charge from one. Thord Sturluson rides up with "
                    "thirty men; bravery and an offer to hunt the creature win "
                    "him. Over twenty Icelanders and thirty Norwegians are dead.",
                    stopped="Thord says the demon killed a Norwegian crew and put "
                    "out to sea with them, and he has another vessel.",
                ),
                S(
                    "Ocean Chase",
                    at=8,
                    clues="Hetep has about four hours' start, but his dead sail "
                    "badly. The Arcane Connection to Brighde still works with "
                    "Intellego Animal for her shape, until he notices and blocks "
                    "it; replaced planking of his ship is a connection too.",
                    stopped="Board the ghost-ship and bring Victor's host to arm's "
                    "length. Hetep may strike once before Victor passes into him; "
                    "Brighde reverts and lies in a coma for about a day. Thord and "
                    "his men are deeply impressed.",
                ),
                S(
                    "What Now?",
                    at=9,
                    clues="Both ships sail back to Snaefellsnes, and Thord wants "
                    "a tale the public will accept: monsters are not unknown, nor "
                    "are magicians hunting them. A service of thanks at the church "
                    "on his estate at Stad is followed by a feast.",
                    stopped="Brighde can open the gate back to the manor if her "
                    "father is dead, and the gatestone goes home to De Panne. "
                    "Devon will not miss Lord Peter, and De Panne's burghers will "
                    "back the magi.",
                ),
            ],
        )
    )


def _seeds(b: Builder, de_panne: Neighbour) -> None:
    dormant(
        b.threat(
            "The Dragon's Bane",
            antagonist="Pan Caudarax's prophecy",
            place=de_panne,
            realm="Magic",
            summary=(
                "Sir Ivain of De Panne has found a dragon's prophecy that his "
                "town will burn, and is taking ship for Iceland with his holy "
                "sword to kill the dragon first. The magi are welcome aboard."
            ),
            secrets=paragraphs(
                "A way to bring characters to Iceland without Spider in the Ice "
                "(p. 63). Pan Caudarax promised to raze the town for a past "
                "slight; the prophecy is on p. 140. Magi may want the vis of the "
                "corpse, or to guard Ivain.",
                "Their presence on the ship may be enough to rouse the Guardians "
                "(p. 7). Local magicians can tell them of the dragon's weak spot "
                "if they enlist them. Faced, Pan Caudarax asks why the knight "
                "defends thieves. He will destroy De Panne only when his hoard "
                "there is robbed; once Ivain understands, he withdraws his "
                "challenge and goes home.",
            ),
        )
    )
    dormant(
        b.threat(
            "An Eye on the North",
            antagonist="The Order's fear of the Order of Odin",
            summary=(
                "Word of Iceland's Galdramen Hreppar reaches the Order, which is "
                "intrigued, alarmed or both, and young magi are chosen to go and "
                "see."
            ),
            secrets=(
                "Heorot on Zealand (see Ultima Thule) was founded partly to watch "
                "the Order of Odin, and the Hreppar may be the nearest thing to "
                "it outside tales. The trip may be a spying mission with the "
                "quaesitores' approval, or a diplomatic one, as the characters' "
                "skills suit (pp. 63-64)."
            ),
        )
    )


def _advice(b: Builder) -> None:
    dormant(
        b.threat(
            "The Toframanna Saga",
            antagonist="Iceland itself",
            summary=(
                "A saga of foreign magicians, whom Icelanders call toframenn, "
                "learning to live in a land of neighbours."
            ),
            secrets=paragraphs(
                "Toframan, feminine tofrakona, is the Icelandic magicians' word "
                "for foreign magicians, whose power rests on no song, giant "
                "blood, runes or herbs, so the saga is the saga of the magi (p. "
                "62).",
                "Land and weather (p. 62). Volcanic ground everywhere; rugged "
                "lowlands, and an interior of trolls, giants and violent spirits "
                "that bleakly offsets the summer meadows. Stick to the paths and "
                "the ponies. A day seldom passes without rain, sleet, hail or "
                "snow, above all in the west, and sun often follows.",
                "Society (pp. 62-63). Everyone of rank knows everyone, and "
                "writes; even labourers follow the intrigues. Foreign magicians "
                "are endlessly discussed, and a magical attempt at privacy makes "
                "it worse. Secret crimes come out, for Icelanders despise those "
                "who disown their acts. Bread and ale are luxuries and a storgodi "
                "is a simple farmer, yet the freemen are proud: tenant farmers "
                "expect to be heard, abuse brings vengeance or a lawsuit, and "
                "reputations are national. If Mythic Iceland follows history the "
                "storgodi's feudal schemes fail and the Norwegian king must "
                "treat with the farmers themselves.",
                "Premises of the saga (pp. 68-69). High fantasy, with the "
                "characters as heroes. A mature Order: expansion is over, and "
                "Join or Die on the borders is a sport. The Oath is applied "
                "pragmatically, and quaesitores act when the Order is endangered. "
                "Commoners do not know of the Order; Jerbiton envoys keep the "
                "peace with Church and courts. Open magic breaks no Code but "
                "angers churchmen. Magi swear no feudal oath and strike deals "
                "with lords, but being in thing with a godi carries no feudal "
                "duty, as the characters may have to argue at Tribunal. Young "
                "magi expect hard terms from a covenant, and take them.",
                "Virtues and Flaws to refuse (p. 74): Quaesitor, Hedge Wizard, "
                "Infamous Master, Tormenting Master, Discredited Lineage, since "
                "the covenant is isolated; Secret Vis Source and Vis Obligation, "
                "since vis is scarce and shared.",
                "The feud is the theme: Order against Damhan-allaidh, Einar "
                "against the dragon, and behind them the storgodi's mundane feud "
                "(pp. 18-19, 67). The arcs are linear in places, and meant to be "
                "left to the storyguide's nudging or dropped (p. 68).",
            ),
        )
    )
