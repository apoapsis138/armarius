"""The recurring characters of Land of Fire & Ice, ch18 (pp. 133-142), in
paraphrase, converted from the Fourth Edition.

Characters, through `fourth.convert`: Iain the Scot and his wife Eleanor,
Donncadh Scot and his wife Mari, Victor filius Pralix, Einar Gamlisson,
Thord Sturluson and Vifil Halldorson. Iain and Victor are of Vindolanda,
found by name. Victor is a Hermetic magus with no Arts printed; only he
keeps the Gift and Hermetic Magus that `convert` gives every block, and
his Might and powers are in words, as a character has no Might.

Creatures: Hetep the Corrupter, Pan Caudarax and Bard Snaefellsass have a
Might; Liam the Shapeless and Damhan-allaidh, gruagachs long past human,
have a printed Magic Resistance and no Might, so they are Magic creatures
at Might 0 with the figure in their notes. Their Characteristics,
Virtues, Abilities and traits go through `convert` too where the book
prints them. Combat, powers, Confidence and Might Forms follow the pack's
readings (see the package docstring).

An Ability with no catalog counterpart is not kept under its printed name:
its experience is spent on catalog Abilities (DE p. 538), or, for an
arcane power no catalog Ability fits, it is named in the notes instead.

The book gives no Might Form, so each is this pack's reading: Hetep's is
Vim, the vis in his heart; Pan Caudarax's Ignem, his breath; Bard's Aquam,
for his frost.

The whole chapter is for storyguides: a summary holds what anyone may
see, and histories, plans and powers are in secrets."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace

from ...models import BodyVis, Character, Covenant, Creature, Neighbour
from ...rules.sites import PLACE
from ...rules.xp import ABILITY_FACTOR, ability_xp, score_from_xp
from ..builder import Builder, StatBlock, characteristics, paragraphs
from ..fourth import Fourth, convert

#: The Area Lore that takes a block's Legend Lore.
AREA = "Iceland"
#: A person's Fatigue and Body levels, as the blocks print them.
FATIGUE = "OK, 0, -1, -3, -5, Unconscious"
BODY = "OK, 0, -1, -3, -5, Incapacitated"
#: The Definitive Edition's Confidence for an important creature.
CONFIDENCE = (1, 3)
#: Printed Abilities fourth.py's table lacks, and the catalog's name.
ABILITY_NAMES = {
    "Craft Toys": "Craft: Toys",
    "Enchanting Music": "Enchanting: Music",
    "European Area Lore": "Area Lore: Europe",
    "Farming": "Profession: Farmer",
    "Fantastic Beast Lore": "Magic Lore",
    "Hermes History": "Organization Lore: Order of Hermes",
    "Icelandic Law": "Common Law",
    "Mediterranean Area Lore": "Area Lore: Mediterranean",
    "Norse Theology": "Theology: Pagan",
    "North Sea Lore": "Area Lore: North Sea",
    "Sense Holiness & Unholiness": "Sense Holiness and Unholiness",
    "Shapechange": "Shapeshifter",
    "Shapeshift": "Shapeshifter",
}
#: Printed Abilities with no catalog counterpart, and the catalog Ability
#: their whole experience is spent on, as the appendix spreads a removed
#: Ability's experience (DE p. 538). The catalog's Empathy is a Faerie
#: Method, not the Fourth Edition Talent.
SPENT_ON = {
    "Alchemy": "Philosophiae",
    "Compose Poetry": "Profession: Poet",
    "Contortions": "Athletics",
    "Diplomacy": "Etiquette",
    "Direction Sense": "Area Lore: Scottish Highlands",
    "Empathy": "Folk Ken",
    "Gruagach Lore": "Organization Lore: Gruagachan",
    "Mimicry": "Guile",
    "Weather Sense": "Wilderness Sense",
}
#: Printed arcane powers no catalog Ability fits: named in the notes and
#: left off the Abilities list.
POWERS = {
    "Decay",
    "Enthrall",
    "Galdor Wisdom",
    "Geasa",
    "Gift",
    "Gruagach Wisdom",
    "Hamfarir",
    "Hamfaring",
    "Incinerate",
    "Jotunn Affinity with Frost",
    "Potency",
    "Sacrifice",
    "Shatter",
    "Transform",
}
#: A combat line of a character's block: name, Init, Attack, Defense,
#: Damage, Fatigue.
Combat = tuple[str, int, int, int, int, int]


def _combat(lines: list[Combat], soak: str) -> str:
    """A character's printed Combat, for the biography: the sheet has no
    place for Fourth Edition totals."""
    shown = "; ".join(
        f"{name}: Init {i:+d}, Attack {a:+d}, Defense {d:+d}, Damage {g:+d}, "
        f"Fatigue {f:+d}"
        for name, i, a, d, g, f in lines
    )
    return f"Combat as printed (Fourth Edition): {shown}. Soak {soak}."


def _spend(stat: StatBlock, printed: Sequence[tuple[str, int, str]]) -> list[str]:
    """Spends each `SPENT_ON` Ability's whole experience on its catalog
    Ability, a new one taking the printed specialty, and says so. What
    buys no further score joins the block's "spare_xp"."""
    entries = {name: (score, spec) for name, score, spec in stat["abilities"]}
    spare: dict[str, int] = dict(stat["spare_xp"])
    said: list[str] = []
    for name, score, specialty in printed:
        new = SPENT_ON.get(name)
        if new is None:
            continue
        xp = ability_xp(score)
        held, own = entries.get(new, (0, specialty))
        total = ability_xp(held) + spare.get(new, 0) + xp
        reached = score_from_xp(total, ABILITY_FACTOR)
        entries[new] = (reached, own)
        spare[new] = total - ability_xp(reached)
        owner = f"{name}'" if name.endswith("s") else f"{name}'s"
        said.append(f"{owner} {xp} xp spent on {new}")
    stat["abilities"] = [(n, s, spec) for n, (s, spec) in entries.items()]
    stat["spare_xp"] = spare
    return said


def _top_up(record: Character | Creature, stat: StatBlock) -> None:
    """Adds to a built record's Abilities the experience `_spend` left
    over its scores."""
    for ability in record.abilities:
        ability.xp += stat["spare_xp"].get(ability.name, 0)


def _sheet(key: str, block: Fourth, *, hermetic: bool = False) -> StatBlock:
    """The converted block. Only a Hermetic magus keeps the Gift and
    Hermetic Magus that `convert` gives every block; the clauses about
    Twilight and a printed Confidence go where the book has neither."""
    moved = [
        f"{name} {score} to {ABILITY_NAMES[name]}"
        for name, score, _ in block.abilities
        if ABILITY_NAMES.get(name, name) != name
    ]
    powers = [
        f"{name} {score}" + (f" ({specialty})" if specialty else "")
        for name, score, specialty in block.abilities
        if name in POWERS
    ]
    renamed = replace(
        block,
        abilities=[
            (ABILITY_NAMES.get(name, name), score, specialty)
            for name, score, specialty in block.abilities
            if name not in POWERS and name not in SPENT_ON
        ],
    )
    stat, _ = convert(key, renamed, area=AREA)
    spent = _spend(stat, block.abilities)
    if not hermetic:
        stat["virtues_flaws"] = stat["virtues_flaws"][2:]
    notes = stat["notes"].replace("Twilight Points 0 / 3 = Warping 0; ", "")
    notes = notes.replace(", not the old 0", "")
    stat["notes"] = paragraphs(
        notes,
        f"Abilities renamed: {'; '.join(moved)}." if moved else "",
        f"Abilities with no counterpart: {'; '.join(spent)}." if spent else "",
        f"Powers with no Ability now, as printed: {'; '.join(powers)}."
        if powers
        else "",
    )
    return stat


def _creature_sheet(key: str, block: Fourth) -> StatBlock:
    """A converted block for a creature: its notes lose the line on age,
    Twilight and Confidence, which a Bestiary record shows itself."""
    stat = _sheet(key, block)
    stat["notes"] = "\n".join(
        line
        for line in stat["notes"].split("\n")
        if not line.startswith("Converted from")
    )
    return stat


def _vindolanda(b: Builder) -> Covenant | None:
    return next((c for c in b.saga.covenants if c.name == "Vindolanda"), None)


def _place(b: Builder, *names: str) -> Neighbour | None:
    """The first place whose name holds one of `names`, in their order."""
    for name in names:
        for record in b.saga.neighbours:
            if record.kind == PLACE and name in record.name:
                return record
    return None


def _person(
    b: Builder,
    key: str,
    name: str,
    block: Fourth,
    *,
    summary: str,
    secrets: str,
    covenant: Covenant | None = None,
    born: int | None = None,
) -> Character:
    """A companion of the book, with no House; `born` where the block's
    age is not the age in the pack's year."""
    person = b.magus(
        name,
        covenant=covenant,
        house="",
        age=block.age if born is None else b.year - born,
        summary=summary,
        type="companion",
        secrets=secrets,
    )
    stat = _sheet(key, block)
    return b.stats(person, stat, source="LFI")


def build(b: Builder) -> None:
    _scots(b)
    _victor(b)
    _liam(b)
    _hetep(b)
    _damhan_allaidh(b)
    _einar(b)
    _pan_caudarax(b)
    _bard(b)
    _thord(b)
    _vifil(b)


def _scots(b: Builder) -> None:
    _person(
        b,
        "iain",
        "Iain the Scot",
        Fourth(
            age=442,
            apparent=29,
            characteristics=characteristics(2, 1, 0, 2, 1, 2, 0, 2),
            confidence=5,
            twilight=0,
            decrepitude=0,
            size=1,
            virtues=[
                ("External Soul", 4),
                ("Wealthy", 3),
                ("Merchant", 0),
                ("Large", 1),
                ("Strong-Willed", 1),
                ("Well-Traveled", 1),
                ("Magic Sensitivity", 1),
                ("Enemies", -4, "servants of Hetep"),
            ],
            abilities=[
                ("Alchemy", 5, "transformations"),
                ("Artes Liberales", 6, "logic"),
                ("Bargain", 6, "bulk"),
                ("Boating", 4, "navigation"),
                ("European Area Lore", 4, "towns"),
                ("Etiquette", 4, "merchant"),
                ("Intrigue", 6, "merchants"),
                ("Legend Lore", 6, "myths"),
                ("Magic Sensitivity", 3, "vis"),
                ("Medicine", 5, "self"),
                ("Mediterranean Area Lore", 4, "eastern ports"),
                ("Philosophiae", 4, "metaphysics"),
                ("Scribe Greek", 5, "contracts"),
                ("Speak Gaelic", 5, "archaic"),
                ("Scribe Latin", 6, "contracts"),
                ("Speak French", 5, "all dialects"),
                ("Speak German", 4, "all dialects"),
                ("Speak Greek", 5, "southern"),
                ("Speak Latin", 6, "ancient"),
                ("Speak Norse", 4, "western"),
                ("Speak Saxon", 4, "all dialects"),
            ],
            arts={},
            spells=[],
            traits={
                "Patient": 3,
                "Loyal (to Victor)": 3,
                "Devoted to Family": 2,
                "Fair-minded": 1,
            },
            reputations={
                "Fair Dealer (London, Flanders, Venice and Constantinople merchants)": 2
            },
            notes=paragraphs(
                "Magical equipment (p. 133): a dirk enchanted for +4 damage and "
                "never to break; half chain made light (load -0.5) with +2 "
                "protection; a Ring of Magic Resistance giving +50, commissioned "
                "from a Verditius in 869 AD, which works only for members of "
                "Vindolanda; several Rings of Ages that make him look other "
                "ages, at present about 50. He keeps healing potions by him: "
                "one stabilized his wounds and the fire destroyed the rest.",
                "The block's Cursed (lost his gift) -6 has no catalog entry and "
                "is kept here; Wealthy Merchant +3 is Wealthy and Merchant.",
            ),
        ),
        covenant=_vindolanda(b),
        summary="A big, well-kept merchant of De Panne in Flanders, known as a "
        "fair dealer from London to Constantinople, with light red hair and "
        "blue eyes and no scar worth the name. He says little of himself and "
        "cares most for his family.",
        secrets=paragraphs(
            "Iain the Unbowed, filius and son of Liam the Shapeless, an original "
            "member of Vindolanda, and now a natural magician. Born in 778, he "
            "looks 29 without his rings. Hetep maimed his Gift in Pralix's war "
            "and Setna alone can restore it (pp. 72, 77, 88, 129). After more "
            "than a hundred years' study he has the basics of Natural Magic. "
            "He serves Victor and his family with equal devotion, and hides his "
            "age and his past from the world (p. 133).",
            "He guarded the Scartaris gatestone from 888, settled in De Panne "
            "in 1182, and after 1220 runs Vindolanda's daily affairs for Victor "
            "(pp. 72, 77, 87).",
        ),
    )
    _person(
        b,
        "eleanor",
        "Eleanor, Iain's wife",
        Fourth(
            age=47,
            apparent=40,
            characteristics=characteristics(1, -1, 3, 1, -1, 1, 2, -1),
            confidence=0,
            twilight=0,
            decrepitude=0,
            virtues=[
                ("Faerie Blood", 2, "Sidhe"),
                ("Oversensitive", -1, "snide comments"),
                ("Soft-Hearted", -1),
            ],
            abilities=[("Craft Toys", 5, "safe ones")],
            arts={},
            spells=[],
            traits={"Devoted to Family": 3, "Insecure": 2},
            notes=paragraphs(
                "Her looks owe seven years to a longevity potion from her husband "
                "(p. 134). No Confidence is printed.",
                "The block's Empathy +1 is the Fourth Edition Talent, not the "
                "catalog's Empathy (a Major Faerie Method), and is kept here. Bad "
                "Reputation -1 has no catalog entry and prints no Reputation to "
                "keep: some women of the town hold her birth against her.",
            ),
        ),
        summary="Wife of the merchant Iain Scot of De Panne: still a striking "
        "beauty close on fifty, dressed in the newest fashion. A foundling "
        "left at St Michael's church and fostered by a carpenter through "
        "Father Galcher, she sold the toys she made at market for high "
        "prices until Iain, the town's best match, married her. Some women "
        "of the town still look down on her for her birth.",
        secrets="",
    )
    _person(
        b,
        "donncadh",
        "Donncadh Scot",
        Fourth(
            age=28,
            apparent=None,
            characteristics=characteristics(3, 0, 1, 1, 0, 0, 1, 0),
            confidence=3,
            twilight=0,
            decrepitude=0,
            size=1,
            granted=["The Gift"],
            virtues=[
                ("Wealthy", 3),
                ("Merchant", 0),
                ("Strong-Willed", 1),
                ("Well-Traveled", 1),
                ("Second Sight", 1),
                ("Faerie Blood", 2, "Sidhe"),
                ("Large", 1),
                ("Enemies", -4, "servants of Hetep"),
                ("Overconfident", -2),
                ("Dutybound", -1, "family"),
                ("Deep Sleeper", -1),
                ("Weakness", -1, "women"),
                ("Magical Air", -1),
            ],
            abilities=[
                ("Alchemy", 3, "transformations"),
                ("Artes Liberales", 3, "logic"),
                ("Awareness", 2, "markets"),
                ("Bargain", 3, "wool"),
                ("Brawl", 1, "punch"),
                ("Concentration", 3, "reading"),
                ("Etiquette", 2, "merchant"),
                ("Legend Lore", 1, "myths"),
                ("Magic Sensitivity", 2, "vis"),
                ("Medicine", 1, "salves"),
                ("Philosophiae", 5, "spellcasting"),
                ("Scribe Greek", 1, "copying"),
                ("Speak Gaelic", 2, "trading"),
                ("Scribe Latin", 2, "original"),
                ("Speak French", 4, "trading"),
                ("Speak German", 2, "trading"),
                ("Speak Greek", 2, "trading"),
                ("Speak Latin", 4, "church"),
                ("Speak Norse", 2, "western"),
                ("Speak Saxon", 3, "trading"),
                ("Single Weapon", 3, "longsword"),
            ],
            arts={},
            spells=[],
            traits={"Devoted to Family": 3, "Brave": 2},
            reputations={"Fair Trader (merchants of Flanders)": 1},
            notes=paragraphs(
                "Magical equipment (p. 134): half chain made light (load -0.5) "
                "with +2 protection; a Ring of Magic Resistance of +20, made by "
                "Iain.",
                "The block's Charm +1 has no catalog Virtue and is kept here; "
                "Wealthy Merchant +3 is Wealthy and Merchant. The book says he "
                "has the Gift (p. 87), though the block does not print it.",
            ),
        ),
        summary="Iain's son and partner at De Panne, a very tall man of 28 with "
        "light brown hair and blue eyes, known among Flemish merchants as a "
        "fair trader, with a young daughter, Brighde.",
        secrets="A natural magician with the Gift (p. 87), and consors of "
        "Vindolanda (p. 80), frantic to rescue Brighde in 1220. He knows his "
        "father's secret and has been "
        "taught by him in the Scartaris library. He tells nothing of the "
        "gateway or of Scartaris unless he must, and then the least he can. "
        "Hermetic magi make him a little nervous and their magic fascinates "
        "him. He would once have made a fine apprentice and might even now "
        "learn the Arts, but he would not take an apprentice's place (p. 134).",
    )
    _person(
        b,
        "mari",
        "Mari, Donncadh's wife",
        Fourth(
            age=22,
            apparent=None,
            characteristics=characteristics(0, 2, 1, 0, 0, 1, -2, -1),
            confidence=0,
            twilight=0,
            decrepitude=0,
            virtues=[
                ("Gossip", 2),
                ("Sharp Ears (Minor)", 1),
                ("Premonitions", 1),
                ("Meddler (Minor)", -1),
                ("Noncombatant", -3),
            ],
            abilities=[],
            arts={},
            spells=[],
            traits={"World of Her Own": 3, "Brave": -2, "Judgmental": 2},
            reputations={"Gossip (De Panne ladies)": 2},
            notes="No Confidence is printed.",
        ),
        summary="Wife of Donncadh Scot and mother of Brighde, a fairly tall "
        "woman with the blond hair and blue eyes of her Scandinavian "
        "forebears, daughter of Baldwin, who co-owns De Panne's only mill. "
        "She is delighted with her marriage, expecting a second child, a "
        "proud mother and known among the merchants' wives for her close "
        "interest in everyone's affairs, though not in the family trade.",
        secrets="She knows nothing of Iain's true past or her husband's magic; "
        "recent events, and arriving at a Hermetic covenant, have shaken her "
        "badly. Her fylgja (p. 32) is a hawk. She has never linked her little "
        "accidents to coming danger, so it spent the past week trying and "
        "failing to warn her (pp. 134-135).",
    )


def _victor(b: Builder) -> None:
    victor = b.magus(
        "Victor filius Pralix",
        covenant=_vindolanda(b),
        house="house_ex_miscellanea",
        age=438,
        summary="A follower of Pralix, given his sigil when she defeated "
        "Damhan-allaidh in 816, whom the Order has long counted among the dead.",
        secrets=paragraphs(
            "In life he could bring anyone round to any position, with an "
            "understanding of people unmatched in his day, but a demon was "
            "beyond him. Hetep overwhelmed him and shut him in a hellish "
            "dream, where he suffered for sixty years until he outwitted the "
            "demon and seized the dreamscape. Since then each has argued the "
            "other's soul in the language of dreams, over grace and its "
            "rejection; Victor now rules the dream and Hetep must endure his "
            "constant calls to renounce Hell (p. 135).",
            "Spirit and body are parted, though he is technically alive, and "
            "the body would crumble within weeks if his ward failed, so he "
            "works by possession alone. Brighde, his friend's granddaughter, "
            "comes first, but everything he does bends toward destroying the "
            "Spider, and he will draw the magi into risky schemes in return "
            "for scraps of knowledge about Damhan-allaidh or Hetep (pp. 135-136).",
            "He looks a tall man in Roman robes, frozen in the ward in his "
            "Scartaris laboratory (p. 82). Founder and Disceptator of Vindolanda, "
            "he entered the battle of wills in 888 (p. 72). Born in 782.",
            "Magic Might 50. Possession (ReMe 50, cost varies): any human in "
            "eye contact, or in sight of his body. Entry costs Might equal to "
            "the victim's Confidence + Stamina (+3 if Strong-Willed) + twice "
            "any True Faith. Parma Magica resists, using the highest of "
            "Corpus, Mentem or Vim, against his penetration of 50 + stress "
            "die; a Natural Resistance roll (Stamina + stress die) of 50 also "
            "stops it. In a Gifted host he uses his full magic without Might. "
            "He does not want a stolen body, and takes control or searches a "
            "mind only at need.",
            "Morphean Landscape (ReMe, 10 points): melds the dreams of up to "
            "twelve people into one under his control, for meetings. Mastery of "
            "the Mind (Me): any Mentem spell to level 50, including his own, "
            "and the Oneiromantic spells of The Mysteries if the troupe uses "
            "them. Mastery of the Image (Im): the same with Imaginem to level "
            "30. Mastery of the Forms: other Forms to level 15. Each costs "
            "twice the spell's magnitude in Might, with no words or gestures, "
            "only a moment's thought.",
        ),
    )
    block = Fourth(
        age=438,
        apparent=41,
        characteristics=characteristics(5, 2, -1, 1, 1, 2, 0, 1),
        confidence=6,
        twilight=0,
        decrepitude=0,
        virtues=[],
        abilities=[],
        arts={},
        spells=[],
        traits={
            "Focused": 3,
            "Otherworldly": 4,
            "Patient": 2,
            "Obsessed with destroying Damhan-allaidh": 6,
        },
        reputations={"Long Dead (the Order)": 3},
        notes="The book prints no Arts, Abilities, Virtues or Flaws: his powers, "
        "with his Magic Might of 50, are his block (p. 135).",
    )
    b.stats(victor, _sheet("victor", block, hermetic=True), source="LFI")


def _liam(b: Builder) -> None:
    stat = _creature_sheet(
        "liam",
        Fourth(
            age=471,
            apparent=None,
            characteristics=characteristics(3, 1, 0, 1, -5, -1, -5, -5),
            confidence=4,
            twilight=0,
            decrepitude=0,
            size=2,
            virtues=[
                ("Giant Blood", 5),
                ("External Soul", 4),
                ("Strong-Willed", 1),
                ("Monstrous Appearance", -5),
                ("Magical Memory", 2),
            ],
            abilities=[
                ("Brawl", 5, "claws"),
                ("Empathy", 2, "magicians"),
                ("Enchanting Music", 4, "dance"),
                ("Faerie Lore", 4, "Sidhe"),
                ("Fantastic Beast Lore", 4, "giants"),
                ("Folk Ken", 4, "giants"),
                ("Geasa", 3, "physical"),
                ("Curse", 3, "characteristics"),
                ("Gruagach Lore", 3, "outdated"),
                ("Gruagach Wisdom", 15, "new Talents"),
                ("Herbalism", 5, "cures"),
                ("Hermes History", 3, "Pralix"),
                ("Magic Sensitivity", 5, "faerie"),
                ("Potency", 6, "shapeshift"),
                ("Premonitions", 5, "immediate future"),
                ("Second Sight", 6, "faeries"),
                ("Speak Latin", 3, "hermetic"),
                ("Speak Gaelic", 5, "conversational"),
                ("Speak Pictish", 6, "shapeshift"),
                ("Speak Saxon", 4, "northern"),
                ("Gift", 8, "physical"),
                ("Shapeshift", 16, "land animals"),
                ("Transform", 7, "birds"),
            ],
            arts={},
            spells=[],
            traits={"Brave": 3, "Irritable": 2, "Suicidal": 3},
            reputations={"Dead (Hermetic magi)": 1},
            notes=paragraphs(
                "Magic Resistance 51 printed, and no Might. Presence n/a in the "
                "block, 0 here. Student of Brude +1 is left out: the catalog's "
                "Student of a realm is not a teacher. Soak +41 includes the +40 "
                "of his invulnerability.",
                "Effects of his Gruagach powers: Magical Aura, Blatant Gift, a "
                "wholly monstrous look, no bones (hence the Characteristics, "
                "wrecked by three centuries buried), constant pain.",
                "Shapeless Form, which he takes at will: Int +3, Per +1, Str "
                "+5, Sta +5, Dex -4, Qik -3, Size +5, Soak +50, tireless; Body "
                "levels OK, 0, 0, 0, -1, -1, -3, -3, -5, -5, Incapacitated. The "
                "Combat lines are this form's; the book gives Grapple no "
                "Defense or Damage and Smother only Damage. Each turn he may "
                "put out up to five pseudopods at one foe. If two or more "
                "strike in a round he may grapple and draw the victim in, and "
                "on success smothering starts next round, to Fatigue and then "
                "Body levels, armor no help.",
            ),
        ),
    )
    liam = b.creature(
        "Liam the Shapeless",
        page="p. 136",
        realm="Magic",
        size=2,
        block=stat,
        age="471",
        confidence=stat["confidence"],
        attacks=[
            b.attack("Strike", 10, 12, 4, 9),
            b.attack("Grapple", 10, 12, 0, None),
            b.attack("Smother", 0, None, 0, 10),
        ],
        soak=41,
        fatigue_levels="Tireless (Shapeless Form)",
        tires=False,
        secrets=paragraphs(
            "A gruagach born in 749, father of Iain, reckoned "
            "dead by the magi after three centuries buried. Once "
            "recovered he is barely human, fighting for each breath in constant "
            "pain, and moves only by shapeshifting, into the one form he can hold "
            "for long. Endurance of the Berserkers, or any Corpus or Mentem effect "
            "that quells pain, gives him respite, and with it he can help the magi "
            "hunt Damhan-allaidh; without it he can only beg to die. Even so he "
            "will ask Iain to destroy his soulstone once the Spider is gone (p. "
            "136).",
            "A fleshy thing with no shape, bones or organs, able to squeeze "
            "into small places, forever putting out and drawing in tentacles "
            "of flesh.",
            stat["notes"],
        ),
    )
    _top_up(liam, stat)


def _hetep(b: Builder) -> None:
    b.creature(
        "Hetep the Corrupter",
        page="pp. 137-138",
        realm="Infernal",
        might=60,
        form="Vim",
        size=-1,
        confidence=CONFIDENCE,
        block={
            "characteristics": characteristics(0, 2, -5, 3, 5, 5, 5, 6),
            "traits": {"Secretive": 6, "Capricious": 6, "Ambitious": 5},
        },
        attacks=[b.attack("Bite or Claw", 13, 14, 13, 11)],
        soak=15,
        fatigue_levels="OK, 0, -3, -5, Unconscious",
        vis=[BodyVis(18, "Vim", "in his heart, Infernally tainted")],
        powers=[
            b.power(
                "Sunder the Magician's Spirit",
                10,
                -4,
                "Vim",
                level=50,
                does="PeVi. A landed blow wounds the victim's Gift, against "
                "Magic Resistance with Vim added to Parma. Hermetic magic has "
                "no cure while he remains in the mortal realm, and elsewhere "
                "he alone can give one, as a rule for a cardinal pact.",
            ),
            b.power(
                "Shapechange",
                0,
                6,
                "Corpus",
                level=40,
                does="MuCo(An). Turns one he possesses into his natural body.",
            ),
            b.power(
                "Raise Corpse",
                1,
                5,
                "Corpus",
                level=25,
                does="ReCo. Raises anyone he kills as one of the walking dead.",
            ),
            b.power(
                "Infernal Spell",
                0,
                6,
                "Vim",
                does="Works the like of spontaneous spells to level 30, at 1 "
                "Might a magnitude.",
            ),
            b.power(
                "Possession",
                0,
                6,
                "Mentem",
                does="ReMe. Any human in line of sight. Entry costs Might equal "
                "to the victim's Confidence + Stamina (+3 if Strong-Willed) + "
                "twice any True Faith. Parma resists, using the highest of "
                "Corpus, Mentem or Vim, against his penetration of 65 + stress "
                "die; a Natural Resistance roll (Stamina + stress die) of 60 "
                "also stops it. He can stay indefinitely. Hermetic magic cannot "
                "detect him; detection and exorcism are resisted by twice his "
                "current Might.",
            ),
            b.power(
                "Corrupt Knowledge",
                1,
                5,
                "Vim",
                level=50,
                does="PeVi, 1 point a day. Slowly corrupts a written work on "
                "magic he touches: a summa takes days equal to the experience "
                "it holds (55 for a level 10 summa), a libri quaestionum or "
                "tractatus days equal to its quality, an Authority a year and "
                "a day. A reader then gains an Occult Lore experience point a "
                "season, taken out of the study total, and a Personality Trait "
                "for the dark arts at the score those points give. Only Sense "
                "Holiness and Unholiness or a like divine gift shows the "
                "change.",
            ),
        ],
        appearance="A skinless baboon: a warped, dog-like, flayed beast with "
        "long-fingered claws much like hands.",
        notes=paragraphs(
            "Body levels as printed: OK, 0, -3, -5, Incapacitated, Banished.",
            "Converted: Might, Characteristics, costs and levels as printed; "
            "Shapechange's 0 and each varying cost are entered as 0, each Init "
            "his Quickness less the cost; the Might Form, unprinted, is Vim, "
            "his vis, this pack's reading. Printed Fatigue total +11 left out.",
        ),
        secrets="Once a servant of Thoth, he betrayed his master for Hell and "
        "means to turn all magic to its service, working chiefly on "
        "magicians. His former kin kept watch: Setna caught him time and "
        "again hiding in those who came to Thoth's stelae, until "
        "Damhan-allaidh brought him into the sanctum. There he set to "
        "corrupting Thoth's own words, hoping to lay the magic realm at "
        "Hell's feet. Setna noticed before it was done and drove "
        "Damhan-allaidh out, but the corruption went on sapping Setna, and "
        "Hetep needed only time, until Pralix broke in on the Spider's "
        "preparations and in the end beat him. Victor of Vindolanda captured "
        "Hetep in 875. The two have been locked in a battle of wills ever "
        "since, beyond mortal understanding; for a century Victor has "
        "withstood all the demon can conjure. Hetep is no great thinker, and "
        "Victor has tricked him into letting slip that he was close to "
        "finishing some plot against the Order (pp. 137-138).",
    )


def _damhan_allaidh(b: Builder) -> None:
    stat = _creature_sheet(
        "damhan_allaidh",
        Fourth(
            age=650,
            apparent=None,
            characteristics=characteristics(-1, -3, 0, -5, 10, 15, 5, 8),
            confidence=5,
            twilight=0,
            decrepitude=0,
            size=1,
            granted=[
                ("Vulnerable to {substance} (Major)", {"substance": "obsidian"}),
                (
                    "Vulnerable to {substance} (Major)",
                    {"substance": "Celtic holy relics"},
                ),
            ],
            virtues=[
                ("External Soul", 4),
                ("Monstrous Appearance", -5),
                ("Hatred (Major)", -3, "the Order of Hermes"),
                ("Deleterious Circumstances", -3, "under clear skies"),
                ("Fury", -3, "when thwarted"),
                ("Weakness", -1, "strong drink"),
            ],
            abilities=[
                ("Brawl", 7, "claws"),
                ("Concentration", 5, "screams"),
                ("Contortions", 7, "escape bonds"),
                ("Direction Sense", 4, "hills"),
                ("Divination", 4, "entrails"),
                ("Dowsing", 6, "magic"),
                ("Empathy", 2, "victims"),
                ("Enchanting Music", 6, "fear"),
                ("Entrancement", 5, "willing sacrifice"),
                ("Faerie Lore", 3, "history"),
                ("Fantastic Beast Lore", 8, "giants"),
                ("Geasa", 7, "physical"),
                ("Gift", 6, "characteristics"),
                ("Gruagach Lore", 2, "outdated"),
                ("Gruagach Wisdom", 30, "new Talents"),
                ("Herbalism", 6, "poison"),
                ("Hermes History", 3, "Pralix"),
                ("Hex", 3, "fear"),
                ("Magic Sensitivity", 5, "Hermetic"),
                ("Mimicry", 5, "victim's voice"),
                ("Occult Lore", 5, "Scottish Highlands"),
                ("Potency", 6, "curse"),
                ("Premonitions", 5, "Order of Hermes"),
                ("Second Sight", 4, "faeries"),
                ("Sense Holiness & Unholiness", 7, "relics"),
                ("Speak Frankish", 3, "courtly"),
                ("Speak Latin", 3, "archaic"),
                ("Speak Pictish", 6, "Geasa"),
                ("Speak Saxon", 4, "threats"),
                ("Stealth", 5, "walk silently"),
                ("Visions", 3, "hunters"),
                ("Weather Sense", 4, "storms"),
                ("Curse", 17, "physical"),
                ("Shapeshift", 20, "monsters"),
                ("Transform", 20, "fish"),
                ("Decay", 15, "bone-breaking"),
                ("Enthrall", 10, "for sacrifice"),
                ("Incinerate", 13, "projection"),
                ("Sacrifice", 8, "human"),
                ("Shatter", 9, "explosion"),
            ],
            arts={},
            spells=[],
            traits={
                "Hate Order of Hermes": 5,
                "Insane (megalomaniac)": 5,
                "Suicidal": 5,
            },
            reputations={"Dead (Order of Hermes)": 5, "Evil": 3},
            notes=paragraphs(
                "Magic Resistance 77 printed, and no Might. Presence n/a in the "
                "block, 0 here; Intelligence and Perception are worn down by "
                "three centuries buried. Need Not Sleep +5 has no catalog "
                "entry and is kept here. Vulnerability (obsidian) and "
                "Vulnerable (Celtic holy relics) are Vulnerable to a substance.",
                "Effects of his Gruagach powers: Magical Aura, Blatant Gift, "
                "Offensive to Animals; a wholly monstrous look; clothes rot on "
                "his skin; fangs (+8 damage in Bite); a hunchback; iron-hard "
                "claws (+5 damage in Brawl); no body hair; skin crusted with "
                "old pus; swollen abdomen; open sores; constant pain. Body "
                "levels as printed: OK, 0, 0, -1, -3, -5, Incapacitated.",
                "His Special Gruagach Abilities act like Hermetic Form and "
                "Technique pairs, each a separate skill casting spontaneous "
                "Hermetic-style spells. Result level = Ability + Characteristic "
                "+ stress die if he spends a point of that Characteristic, or "
                "half that if not. A botch after spending loses the point for "
                "good; otherwise it comes back as Fatigue does. Parma or wards "
                "resist; Penetration equals the result after any halving. "
                "Incinerate: as Creo and Rego Ignem, true fire only, Presence "
                "(now only at half). Decay: as Perdo Animal and Corpus, Stamina. "
                "Enthrall: as Rego and Perdo Mentem, Intelligence. Sacrifice: "
                "as Creo Vim; each Body level drained gives a pawn of vis per "
                "10 levels of result, only at Imbolc, Beltane, Lughnasa and "
                "Samhain. Shatter: as Perdo Herbam and Terram, Strength.",
            ),
        ),
    )
    spider = b.creature(
        "Damhan-allaidh, the Spider",
        page="pp. 138-139",
        realm="Magic",
        size=1,
        block=stat,
        age="650",
        confidence=stat["confidence"],
        attacks=[
            b.attack("Bite", 15, 12, 15, 19),
            b.attack("Claw", 17, 13, 16, 16),
        ],
        soak=16,
        fatigue_levels="OK, 0, 0, -1, -3, -5, Unconscious",
        secrets=paragraphs(
            "The ancient gruagach, born in 570, whom the Order thinks dead. His "
            "name, said davan-alli, is Gaelic for the spider, and he is also "
            "called Dav'nalleous (pp. 70-71). "
            "His mind is close to ruin, and the scrap of humanity left in it "
            "longs to be free of him. Beast instinct usually rules and he obeys "
            "Hetep at a word. Brought to reflect on his state, by The Gift of "
            "Reason or fine roleplaying, he may turn on Hetep and seek God's "
            "grace. Only true remorse, unlikely as it is, would move God to "
            "undo the soul he hid away and let him rest (p. 139).",
            "No longer human at all: hairless, crusted with pus and open sores, "
            "with a beast's head of huge jaw and fangs, a back too twisted to "
            "walk upright, and long iron-hard claws for hands and feet.",
            stat["notes"],
        ),
    )
    _top_up(spider, stat)


def _einar(b: Builder) -> None:
    _person(
        b,
        "einar",
        "Einar Gamlisson",
        Fourth(
            age=76,
            apparent=None,
            characteristics=characteristics(1, 0, 1, 5, 0, 2, -1, -1),
            confidence=4,
            twilight=0,
            decrepitude=0,
            virtues=[
                ("Great Characteristic", 4, "Communication"),
                ("Driving Goal", -1, "revenge"),
                ("Lost Love", -1),
                ("Sense of Doom", -3),
            ],
            abilities=[
                ("Galdor Wisdom", 12, "yfel-galdor"),
                ("Second Sight", 6, "fate-spirits"),
                ("Premonitions", 6, "violence"),
                ("Brawl", 3, "fist"),
                ("Enchanting Music", 5, "rousing"),
                ("Summoning", 4, "trolls"),
                ("Hamfarir", 5, "distant travel"),
                ("Sing", 11, "long periods"),
                ("Norse Theology", 5, "Odin"),
                ("Legend Lore", 6, "fate-spirits"),
                ("Bargain", 4, "landvaettir lords"),
                ("Etiquette", 4, "landvaettir"),
                ("Weapon and Shield", 4, "axe and round shield"),
                ("Curse", 4, "infertility"),
                ("Scribe Runes", 3, "curses"),
                ("Potency", 3, "curses"),
                ("Speak West Norse", 7, "magicians"),
                ("Speak Latin", 5, "churchmen"),
                ("Speak Jotunn", 5, "trolls"),
                ("Craft: Weaving", 5, "wool"),
                ("Craft: Leather", 4, "belts"),
            ],
            arts={},
            spells=[],
            traits={
                "Obsessed with Revenge": 3,
                "Brave": 3,
                "Level Headed": -1,
            },
            reputations={"Rogue (the Eldborg Hreppur)": 3},
            notes=paragraphs(
                "The block is for 1231, when he is most likely met, aged 76; "
                "the record's birth year is the book's 1155. He looks in his "
                "late fifties.",
                "Enchanting Music, Summoning and Hamfarir came by initiation. "
                "Galdraman Songs: Yfel-galdor (curse songs) 7, Mal-galdor (speech) "
                "5, Hug-galdor (mind) 2, Sig-galdor (victory) 2, Lim-galdor "
                "(healing) 3, Biarg-galdor (birth) 10, Orlog-galdor (fate) 11, "
                "Ol-galdor (warding) 5, Brun-galdor (weather) 3.",
                _combat(
                    [
                        ("Brawl (fist)", 4, 3, 3, 0, 6),
                        ("Axe and Round Shield", 6, 6, 10, 6, 7),
                    ],
                    "12 with the magical cloak",
                ),
                f"Fatigue {FATIGUE}; Body {BODY}.",
                "Magical equipment: a Blue Cloak of warding songs (+20 magic "
                "resistance, +10 Soak); a Scarf of Red Wool, an effect like "
                "Trust of Childlike Faith at Target Group 12 times a day; a "
                "Scarf of Yellow Wool, Aura of Rightful Authority at Constant "
                "Duration; a Leather Hat that makes him invisible while he "
                "stands still. He should have many minor items, above all "
                "healing potions in the form of woven bandages (p. 139).",
                "Secret Hiding Place +1, Curse +4 and Potency +2 have no catalog "
                "entries and are kept here; Incredible Communication +4 is "
                "Great Communication, with his printed +5 kept.",
            ),
        ),
        born=1155,
        summary="A distinguished Icelander who looks in his late fifties, with "
        "straight black hair, rare among the Norse, a neat beard, a blue robe "
        "embroidered in knots and a voice like honey that talks people round.",
        secrets="A traditional galdraman and the main antagonist of the Fire and "
        "Song story arc, sworn against the dragon Pan Caudarax. In 1210 "
        "he went to Norway to help his kinsman Bjarke Odd-Karnor in a feud, "
        "and there married Yrsa and had two sons. In 1218 she sailed to join "
        "him on a ship that also carried Flambeau magi bound to destroy the "
        "Order of Odin. The landvaettir felt them, and the dragon burned the "
        "ship. Not seeing the dragon's reasons, Einar swore to destroy its "
        "family as his was destroyed (pp. 69-70). He is a great friend of the "
        "alfar and of the Norns; the Norn who became his fylgja showed him "
        "his own doom, so he hurries his revenge, and she now looks much like "
        "his dead wife (p. 140). His nidstong cursed Pan Caudarax's eggs (pp. "
        "98, 100). He fled to Glasvellir, where he took a new wife and children "
        "in the human village, and in 1230 stirred Blund Thorgilsson against "
        "the eggs; Thorodd Gamlisson of Snaefell is his brother (pp. 114-117). "
        "If he lives he teaches the Aesir faith to Geirrod's slaves (p. 127).",
    )


def _pan_caudarax(b: Builder) -> None:
    b.creature(
        "Pan Caudarax, Dragon of Hekla",
        page="p. 140",
        realm="Magic",
        might=70,
        form="Ignem",
        size=6,
        place=_place(b, "Hekla"),
        age="Many thousands of years",
        confidence=CONFIDENCE,
        block={
            "characteristics": characteristics(5, 4, 0, 0, 20, 10, 0, 0),
            "abilities": [
                ("Shapeshifter", 23, "fantastic beasts"),
            ],
            "traits": {"Honorable": 3, "Brave": 6, "Cunning": 3},
            "reputations": {
                "Guardian (Icelandic magicians)": 3,
                "Harbinger of Doom (De Panne)": 1,
            },
        },
        attacks=[
            b.attack("Breath", 12, 8, 0, 40),
            b.attack("Bite", 15, 15, 10, 36),
            b.attack("1st Claw", 17, 18, 12, 32),
            b.attack("2nd Claw", 17, 18, 12, 32),
        ],
        soak=30,
        fatigue_levels="OK, 0, 0, -1, -1, -3, -3, -5, -5, Unconscious",
        powers=[
            b.power(
                "Fiery Breath",
                5,
                -5,
                "Ignem",
                level=50,
                does="CrIg. A gout of fire over an area 10 paces wide and 30 "
                "long: intensely hot but with little force, so any cover "
                "blocks it.",
            ),
            b.power(
                "Spellcasting",
                0,
                0,
                "Vim",
                does="Casts a range of spells as if he had the Arts Creo 20, "
                "Rego 10, Animal 20 and Imaginem 10.",
            ),
        ],
        equipment="Dragon Amulet (CrVi 40): white marble, worn on the chest in "
        "a harness of fine gold chains. Once a day it gives the vis to make "
        "one healing spell Instant. The spell must be designed for the "
        "amulet, so the amulet must first be investigated.",
        appearance="An enormous beast who takes the shape of the dragons of "
        "the land he is in: in Iceland usually a lindorm, a Norse serpent "
        "dragon; in western Europe golden-red scales and vast wings hiding a "
        "serpent body and thin, sinewy arms.",
        notes=paragraphs(
            "Body levels as printed: OK, 0, 0, -1, -1, -3, -3, -5, -5, "
            "Incapacitated. Bite and Claws are Furious Attacks, usable on "
            "several foes in a round with no penalty; Breath has no Defense "
            "(n/a).",
            "Converted: Might, Characteristics (Presence and Communication "
            "unprinted, 0 here) as printed; the Fatigue totals are left out "
            "(Breath +10, the rest +20); the Might Form, unprinted, is Ignem, "
            "his breath, this pack's reading.",
            "Powers with no Ability now, as printed: Curse 31 (thieves); Geas "
            "34 (deals); Gift 28 (one time bonus); Transform 29 (tasty).",
        ),
        secrets=paragraphs(
            "He has a weak spot beneath his left ear, where the scales never "
            "quite grew. Anyone who knows may aim for it at -3 to Attack, and "
            "there his Soak is only +5.",
            "First Guardian of Iceland, he came back to Hekla in 108 after "
            "nearly a thousand years in Flanders, where he took priests of "
            "Mercury and Apollo to teach him their magic and built up a hoard. "
            "He has lairs across the world.",
            "The prophecy of De Panne: leaving Flanders as too crowded, he "
            "declared that he went by choice, not wishing to live among men "
            "or to wipe them out, that he remembered the treasure he left "
            "there, and that anyone who robbed it would bring him back in a "
            "vengeance feared for centuries. He has not yet had to keep the "
            "oath (p. 140), and will raze the town only if the hoard is "
            "robbed (p. 63).",
        ),
    )


def _bard(b: Builder) -> None:
    stat = _creature_sheet(
        "bard",
        Fourth(
            age=260,
            apparent=None,
            characteristics=characteristics(0, 0, 3, 0, 6, 5, -1, -1),
            confidence=0,
            twilight=0,
            decrepitude=0,
            size=2,
            granted=["External Soul"],
            virtues=[],
            abilities=[
                ("Jotunn Affinity with Frost", 17, "stopping snowfall"),
                ("Shapeshift", 18, "gaining size"),
                ("Transform", 16, "dog"),
                ("Gift", 5, "virtues"),
                ("Divination", 3, "danger"),
                ("Survival", 8, "mountains"),
                ("Climb", 6, "mountains"),
                ("Great Weapon", 8, "quarterstaff"),
                ("Speak Jotunn", 10, "Clan of Hrym"),
                ("Potency", 10, "Transform"),
            ],
            arts={},
            spells=[],
            traits={"Friend of Man": 4, "Unworldly": 3, "Boastful": -2},
            reputations={
                "Guardian Spirit (men of Snaefellsnes)": 4,
                "Dangerous to cross (trolls)": 4,
                "Leader (giants of Iceland)": 8,
            },
            notes="External Soul is printed among his Abilities with no score. "
            "The book prints no Combat, Soak or levels for him. His natural "
            "Size is +3; the block's +2 is the eight-foot shape he has worn "
            "so long it is second nature, and he often goes smaller among "
            "men. The Might Form, unprinted, is Aquam, for his frost, this "
            "pack's reading.",
        ),
    )
    b.creature(
        "Bard Snaefellsass Dumbson",
        page="p. 141",
        realm="Magic",
        might=71,
        form="Aquam",
        size=2,
        block=stat,
        age="260",
        confidence=CONFIDENCE,
        place=_place(b, "The Singing Cave", "Snaefellsnes"),
        appearance="Very handsome, with blond hair going silver-gray, blue "
        "eyes, broad shoulders and a guileless smile. He wears a plain tunic "
        "and leggings with a walrus-hide belt, a cowled gray fur cloak "
        "outdoors, and often carries an iron-shod staff, with a huge gray dog, "
        "Snati, at his side.",
        notes=stat["notes"],
        secrets="Born in 960 in Helluland, the giants' realm beyond Greenland, "
        "son of King Dumb, half giant and half troll, and of Mjoll, daughter "
        "of the frost giant Snaer the Old; fostered by giants in Iceland, he "
        "settled in Norway. A trollson in Ars Magica's terms, more human than "
        "giant after so long among men. He left Norway with so many others "
        "when Harald Finehair took the crown, came to Iceland with his nine "
        "daughters, named Snaefellsnes and made his home at Songhellir, the "
        "Singing Cave. His brother Thorkel settled with him; their families "
        "feuded and made peace. Having guarded the people there against the "
        "trolls that swarm in those parts, he is held their guardian spirit. "
        "He leads all Iceland's giants and is one of the land's Guardians "
        "(p. 141). He wants peace between the dragon and Einar, and counts "
        "himself guardian of the land where the characters' covenant stands "
        "(p. 70). The book's dates disagree: born in 960, he leaves Norway at "
        "the accession of a Harald who reigns 890-930 (pp. 17, 141).",
    )


def _thord(b: Builder) -> None:
    _person(
        b,
        "thord",
        "Thord Sturluson",
        Fourth(
            age=55,
            apparent=None,
            characteristics=characteristics(2, 0, 0, 2, 2, 3, 0, -1),
            confidence=4,
            twilight=0,
            decrepitude=0,
            virtues=[
                ("Tough", 1),
                ("Premonitions", 1),
                ("Enemies", -4, "various"),
            ],
            abilities=[
                ("Athletics", 2, "running"),
                ("Awareness", 2, "on watch"),
                ("Brawl", 3, "dagger"),
                ("Compose Poetry", 2, "praise poems"),
                ("Diplomacy", 4, "family"),
                ("Farming", 4, "animals"),
                ("Leadership", 4, "thingmen"),
                ("Longshaft Weapon", 4, "long spear"),
                ("Icelandic Law", 5, "compensation"),
                ("Intrigue", 4, "assemblies"),
                ("North Sea Lore", 2, "towns"),
                ("Premonitions", 3, "doom"),
                ("Speak West Norse", 5, "commands"),
                ("Swim", 3, "rivers"),
                ("Stealth", 3, "raids"),
                ("Speak Latin", 3, "Church"),
                ("Survival", 2, "mountains"),
                ("Weapon and Shield", 4, "longsword and round shield"),
            ],
            arts={},
            spells=[],
            traits={"Calculating": 2, "Ambitious": 3, "Conciliatory": 2},
            reputations={"Fair (thingmen)": 2, "Ambitious (Icelanders)": 3},
            notes=paragraphs(
                "Aging Afflictions: Poor Hearing -1, Painful Joints -1.",
                _combat(
                    [
                        ("Brawl (fist)", 3, 3, 2, 2, 6),
                        ("Longsword and Round Shield", 6, 7, 12, 5, 8),
                        ("Long Spear", 9, 11, 5, 7, 8),
                        ("Dagger", 5, 5, 5, 4, 7),
                    ],
                    "+14 (Half Chain Mail)",
                ),
                f"Fatigue {FATIGUE}; Body {BODY}.",
                "Storgodi +4 has no catalog entry and is kept here.",
            ),
        ),
        summary="A storgodi and the eldest legitimate son of Hvamm-Sturla and "
        "Gudny Bodvarsdottir of the Myramen. Marriage to Helga Arisdottir won "
        "him the estate of Stad at Snaefellsnes and half the Thorsnes godord; "
        "the priest Thorgils Snorrason gave him the other half. In 1220 he is "
        "the strongest man in southern Iceland, his brother Sighvat holds a "
        "like place in the north, and his youngest brother is Snorri Sturluson. "
        "He is known as fair by his thingmen, and as ambitious by everyone.",
        secrets="He rides against Hetep's dead on Snaefellsnes with thirty men, "
        "takes ship with the magi, and gives out a tale the public can accept "
        "(pp. 86-87). He wants the foreign magi under his influence: he offers "
        "them law and his support as thingmen, sells Dagverdara, and lends them "
        "Vifil, who watches them for him (pp. 98-99).",
    )


def _vifil(b: Builder) -> None:
    _person(
        b,
        "vifil",
        "Vifil Halldorson",
        Fourth(
            age=45,
            apparent=None,
            characteristics=characteristics(2, 0, 1, 3, 0, 2, 1, -2),
            confidence=3,
            twilight=0,
            decrepitude=0,
            virtues=[
                ("Close Family Ties", 1),
                ("Social Contacts", 1, "Galdramen"),
                ("Lame", -2),
                ("Favors", -1),
                ("Poor Hearing", -1),
            ],
            abilities=[
                ("Awareness", 2, "sheep"),
                ("Brawl", 1, "dagger"),
                ("Craft: Jewelry-making", 4, "silver"),
                ("Craft: Blacksmith", 5, "tools"),
                ("Craft: Weapon-smithing", 2, "spearheads"),
                ("Farming", 3, "animals"),
                ("Galdor Wisdom", 5, "conjuring"),
                ("Hamfaring", 3, ""),
                ("Legend Lore", 3, ""),
                ("Longshaft Weapon", 2, "long spear"),
                ("Occult Lore", 2, ""),
                ("Icelandic Law", 2, "procedures"),
                ("Premonitions", 2, "weather"),
                ("Ride", 2, "rough ground"),
                ("Survival", 2, "mountains"),
                ("Sing", 5, "conjuring"),
                ("Second Sight", 3, ""),
                ("Speak Latin", 4, "Church Latin"),
                ("Speak West Norse", 5, "casual"),
                ("Weapon and Shield", 2, "longsword and round shield"),
            ],
            arts={},
            spells=[],
            traits={"Generous": 3, "Brave": 2, "Honorable": 1},
            reputations={"Generous (people of Snaefellsnes)": 2},
            notes=paragraphs(
                "Galdraman Songs: Biarg-galdor 4, Lim-galdor 3, Ol-galdor 5, "
                "Brun-galdor 4.",
                _combat(
                    [
                        ("Brawl (fist)", 0, 2, -1, 0, 3),
                        ("Long Spear", 6, 10, 2, 6, 5),
                        ("Longsword and Round Shield", 3, 6, 8, 4, 5),
                    ],
                    "+8 with armor",
                ),
                f"Fatigue {FATIGUE}; Body {BODY}.",
                "Magical equipment: a Bracelet of Magic Resistance, +15 (p. 142).",
                "Bondi +1 and Cursed (magic used for personal gain has double "
                "botch risk) -2 have no catalog entries and are kept here. "
                "Close Family Ties, a +1 Virtue here, is a Flaw in the catalog.",
            ),
        ),
        summary="A tall, thin, affable farmer and smith of Snaefellsnes with "
        "light brown hair, brown eyes and a clubfoot that keeps him from much "
        "farm work. His smithy makes tools and now and then weapons, and "
        "earns him well. His son runs the farm and its three laborers, and "
        "he is known for his generosity to neighbors in hard times.",
        secrets="A moderately powerful traditional galdraman who quietly sells "
        "his services around the region. With the farm in his son's hands he "
        "means to work on his magic (p. 142). Thord asks him to guide the "
        "foreign magi, and to watch and report on them, which he admits only "
        "if asked; he has no Gentle Gift, so they may guess (p. 99). He can "
        "tell them about Pan Caudarax (p. 101), brings them to the hreppur, "
        "and shares the vis if he found the nidstong himself (pp. 102, 106).",
    )
