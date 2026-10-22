"""The Bestiary (ch06, ch07, SiS): the Levant's creatures, converted from
the Fourth Edition (L15).

Four stat blocks: Amirat al-Jabal, the marida of the northern Syrian
mountains (Magic 60, Size +4), 'Abd al-Misbah, the marid of the lamp
(Magic 15, once 80), al-Qatil, the ghul mercenary (Infernal 20), and the
naddaha of the wells (Infernal 20: The Cradle and the Crescent counts
naddahas among the spirits that are not jinn and gives them no realm of
its own, so the book's stands). Then Luigi, Amber's cat (Magic Might 13,
3 pawns of Animal vis), whose Familiar record stats_magi.py binds to her
(L14). Last, Wardat al-Quds's five Familiarities, given a Might and
nothing more and marked "Might only": the ghost 'Aziza, the airy fire
spirit Hiss, the demon Lucius, and the jinn al-Manqa'i and Sharif, whom
stats_magi.py makes her bound jinn (Q1).

Keys: creatures["amirat_al_jabal"], ["abd_al_misbah"], ["al_qatil"],
["naddaha"], ["luigi"], ["aziza"], ["hiss"], ["lucius"], ["al_manqai"]
and ["sharif"]. Al-Khidr is east.py's shared creatures["al_khidr"], not
remade here.

The conversion: Might as printed; Characteristics, Abilities (renamed to
the Definitive Edition's) and personality as printed; combat worked out
again from the Definitive Edition's weapons (Init Qik + weapon, Attack
Dex + Ability + weapon, Defense Qik + Ability + weapon, Damage Str +
weapon), Soak as Stamina plus the protection the old Soak gave beyond
Stamina and Size. Each power is priced in Might points: a rated power
becomes an effect at a Definitive Edition level (the old rating x 5
where the book gave that rule, a guideline's level elsewhere) costing its
magnitude in Might, or 1 point a magnitude for the elemental controls,
as The Cradle and the Crescent prices its jinn's; a power's Init is the
creature's Quickness less its cost. The old rule that a jinni's work
ends at dawn unless it spends Might for good becomes paying the effect's
cost a second time to make it last. The jinn's blocks leave out TC&TC's
Jinni Virtue, which the catalog lacks, and give their nature in the
notes; Ways of the Desert and Magical Air, which the book gives every
jinni, are on their sheets.

Each creature is set at its place in `finish`, once the places exist:
the most fitting place a part made (Wardat's spirits and Luigi at Aedes
Veritatis's site), else the region, else the Levant, and the place
links to it. The beings named without stats (al-Abyad, the Genjii, the
Pyramids' spirits and the rest) are a sentence at their places, written
by the parts that make those places; al-Abyad is in Wardat's
biography."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...models import BodyVis
from ..builder import paragraphs

if TYPE_CHECKING:
    from ...models import Creature, CreaturePower, Neighbour
    from . import Levant

#: A person's Fatigue levels; Size changes the wound ranges, not these.
FATIGUE = "OK, 0, -1, -3, -5, Unconscious"
SIS = "SiS"
MIGHT_ONLY = "Might only:"

#: The jinni's nature, as the book gives it for every jinni.
JINN_NATURE = (
    "A jinni, made of smokeless flame. Its nature, from the book (TC&TC's "
    "Jinni Virtue is not in the catalog, so it is written here): it heals "
    "a wound level a day for each point of a Magic aura it rests in; "
    "magical fire cannot hurt it and mundane fire does half its harm, but "
    "cold does double; it sees in darkness as by day, and has Second "
    "Sight and Magic Sensitivity of at least 2; it neither ages nor "
    "sickens and dies only by violence; and it must keep any promise it "
    "makes, so it gives its word sparingly."
)
#: The dawn rule, as converted.
DAWN = (
    "Its powers' effects end at the next dawn or call to prayer; to make "
    "one last, it pays the effect's Might cost a second time."
)

#: The places each creature lives: the place keys a part may have made,
#: in order, then words a place's name may hold, then the region to fall
#: back on.
HOMES: dict[str, tuple[tuple[str, ...], tuple[str, ...], str]] = {
    "amirat_al_jabal": (
        ("northern_syria", "jabal_ansariya", "jabal_al_ansariyya"),
        ("Northern Syria", "Ansariyya", "Nusayri Mountains"),
        "syria",
    ),
    "abd_al_misbah": ((), (), "levant"),
    "al_qatil": ((), (), "syria"),
    "naddaha": (("upper_egypt",), ("Upper Egypt",), "egypt"),
}
#: Wardat's spirits and Amber's cat live where their mistresses do.
AT_AEDES = ("luigi", "aziza", "hiss", "lucius", "al_manqai", "sharif")

#: The note on each place's link to its creature.
ROLE = {
    "amirat_al_jabal": "the marida who watches over the mountains' jinn",
    "abd_al_misbah": "the marid of the lamp, wherever the lamp has gone",
    "al_qatil": "the ghul who sells his sword to any army",
    "naddaha": "the spiked crone who lurks by wells",
    "luigi": "Amber's familiar",
    "aziza": "a ghost who answers Wardat's summons",
    "hiss": "an airy fire spirit who answers Wardat's summons",
    "lucius": "a demon Wardat can summon but not command",
    "al_manqai": "a jinni bound to Wardat's service",
    "sharif": "a jinni bound to Wardat's service",
}

#: The creatures this part makes, by key, for `finish`.
_MADE: dict[str, Creature] = {}


def _chars(
    int_: int, per: int, pre: int, com: int, str_: int, sta: int, dex: int, qik: int
) -> dict[str, int]:
    """Characteristics in the Definitive Edition's order (Int, Per, Pre,
    Com, Str, Sta, Dex, Qik); the book prints them in another."""
    return {
        "intelligence": int_,
        "perception": per,
        "presence": pre,
        "communication": com,
        "strength": str_,
        "stamina": sta,
        "dexterity": dex,
        "quickness": qik,
    }


def _wounds(size: int) -> str:
    step = 5 + size
    return (
        f"Wound ranges: Light 1-{step}, Medium to {2 * step}, Heavy to "
        f"{3 * step}, Incapacitated to {4 * step}, Dead from {4 * step + 1}."
    )


def _control(levant: Levant, form: str, rating: int, qik: int) -> CreaturePower:
    """A jinni's command of an element, the book's Control power: any
    non-Ritual effect of that Form up to the old rating x 5."""
    b = levant.b
    level = rating * 5
    return b.power(
        f"Command of {form}",
        1,
        qik - 1,
        form,
        level=level,
        does=f"Works any non-Ritual {form} effect up to level {level} (the "
        f"book's rating of {rating}), at 1 Might point a magnitude. "
        + (
            "Creo Ignem effects reach a magnitude higher and Perdo Ignem ones "
            "a magnitude lower, as befits a creature of fire."
            if form == "Ignem"
            else "The book has jinn work these with the Islamic Ranges, "
            "Durations and Targets."
        ),
    )


def _summon(
    levant: Levant, rating: int, might: int, qik: int, whose: str
) -> CreaturePower:
    """The book's Summon: lesser jinn at half the summoner's Might."""
    return levant.b.power(
        "Call the Lesser Jinn",
        2,
        qik - 2,
        "Vim",
        does=f"Calls {whose} up to {rating} lesser jinn of Might up to "
        f"{might // 2} each and no more than {rating * 10} in all, who come "
        f"within {20 - rating} minutes. They serve as well as they can but "
        "shun needless danger, and may turn on a master who mistreats them. "
        "The call is Momentary: they make their own way home.",
    )


def _travel(levant: Levant, rating: int, might: int, qik: int) -> CreaturePower:
    """The book's Travel, as a Leap of Homecoming."""
    return levant.b.power(
        "The Jinni's Road",
        7,
        qik - 7,
        "Corpus",
        rtd=("Personal", "Momentary", "Individual"),
        level=35,
        does="Is at once in any place it has been before. A place it has "
        f"only heard described, or holds an Arcane Connection to, it reaches "
        f"if no more than {rating} miles off, on Int + {rating} + a stress "
        "die against 15 (easier with a map or the Connection, harder with a "
        f"vague account). It may take up to {might // 5} people along. As "
        "the Leap of Homecoming, ReCo 35.",
    )


def _strength(levant: Levant, rating: int, qik: int, note: str = "") -> CreaturePower:
    return levant.b.power(
        "Strength Beyond Nature",
        1,
        qik - 1,
        "Corpus",
        does=f"Adds {rating} to Strength for one roll.{note}",
    )


def build(levant: Levant) -> None:
    _MADE.clear()
    _jinn(levant)
    _naddaha(levant)
    _luigi(levant)
    _familiarities(levant)
    levant.creatures.update(_MADE)


# -- chapter 7: the jinn --


def _jinn(levant: Levant) -> None:
    b = levant.b
    _MADE["amirat_al_jabal"] = b.creature(
        "Amirat al-Jabal, Lady Emir of the Mountain",
        page="p. 88",
        realm="Magic",
        might=60,
        form="Terram",
        size=4,
        block={
            "characteristics": _chars(1, 0, 4, 0, 10, 10, 0, -3),
            "virtues_flaws": [
                "Reserves of Strength",
                ("Ways of the {land}", {"land": "Desert"}),
                "Magical Air",
            ],
            "abilities": [
                ("Brawl", 5, "fist"),
                ("Magic Sensitivity", 3, "jinn"),
                ("Area Lore: Northern Syria", 6, "jinn strongholds"),
                ("Second Sight", 6, "jinn"),
                ("Living Language: Arabic", 5, "northern Syrian speech"),
            ],
            "traits": {"Patient": 6, "Brave": 6, "Motherly": 3, "Distracted": 3},
        },
        attacks=[b.attack("Stony fist", -3, 5, 2, 10)],
        soak=31,
        fatigue_levels=FATIGUE,
        powers=[
            _control(levant, "Terram", 10, -3),
            b.power(
                "Dread of the Heights",
                6,
                -9,
                "Mentem",
                rtd=("Voice", "Diameter", "Group"),
                level=30,
                does="Fills a crowd with terror, so that it flees or cowers; "
                "one person she may merely make wary. CrMe 30 (Base 5, +2 "
                "Voice, +1 Diameter, +2 Group), for the book's Fear 10.",
            ),
            b.power(
                "Shape of the Crag",
                6,
                -9,
                "Corpus",
                rtd=("Touch", "Sun", "Individual"),
                level=30,
                does="Turns her, or someone she touches, into any lifeless "
                "thing, from a pebble to a cliff, up to 14 steps of Size from "
                "the true one; she still sees and speaks in that shape, a "
                "victim does not. An unwilling victim resists on a Stamina "
                "stress roll of 9+. Others notice the disguise only if their "
                "Per + Awareness beats her Int + 14. MuCo(Te) 30, for the "
                "book's Shapechange to Object 14.",
            ),
            _strength(levant, 6, -3),
            _summon(levant, 10, 60, -3, "from her mountains"),
            _travel(levant, 10, 60, -3),
        ],
        vis=[
            BodyVis(10, "Terram", "in her body"),
            BodyVis(10, "Ignem", "in her body"),
        ],
        appearance=(
            "A marida fifteen feet tall and nearly as wide, a rough, hairless "
            "human shape with skin like sandy brown stone; strangers take "
            "her for part of the mountainside. Her voice is a deep rumble."
        ),
        notes=paragraphs(
            "A marida of the Marid tribe in the mountains of northern Syria. "
            "Mortal business barely interests her: she spends her care on "
            "the lesser jinn of the heights, many of whom treat her as a "
            "grandmother. She is kind to whoever shows her respect and "
            "fearsome to whoever harms her or those she shelters. A Muslim "
            "in name, she keeps the faith fitfully, always being drawn off "
            "by her charges' troubles. Talking is wiser than fighting her.",
            JINN_NATURE,
            DAWN + " " + _wounds(4),
        ),
    )
    _MADE["abd_al_misbah"] = b.creature(
        "'Abd al-Misbah, the Servant of the Lamp",
        page="p. 95",
        realm="Magic",
        might=15,
        form="Ignem",
        size=3,
        block={
            "characteristics": _chars(0, 2, -2, 0, 7, 7, 3, 4),
            "virtues_flaws": [
                "Reserves of Strength",
                ("Ways of the {land}", {"land": "Desert"}),
                "Magical Air",
            ],
            "abilities": [
                ("Area Lore: Arabia", 6, "magical sites"),
                ("Brawl", 8, "fist"),
                ("Area Lore: China", 6, "people of note"),
                ("Area Lore: Egypt", 6, "magical sites"),
                ("Folk Ken", 4, "jinn"),
                ("Guile", 4, "elaborate lies"),
                ("Area Lore: Holy Land", 6, "holy sites"),
                ("Intrigue", 4, "plotting"),
                ("Area Lore: Iraq", 6, "treasures"),
                ("Leadership", 5, "intimidation"),
                ("Magic Lore", 6, "jinn"),
                ("Magic Sensitivity", 3, "jinn"),
                ("Area Lore: Persia", 6, "people of note"),
                ("Second Sight", 6, "jinn"),
                ("Living Language: Arabic", 5, "colourful phrases"),
                ("Living Language: Chinese", 4, "court speech"),
                ("Living Language: Persian", 4, "colourful phrases"),
                ("Stealth", 4, "sneaking"),
            ],
            "traits": {"Bitter": 6, "Miserable": 5, "Brave": 5},
        },
        attacks=[b.attack("Fist", 4, 11, 12, 7)],
        soak=11,
        fatigue_levels=FATIGUE,
        powers=[
            _control(levant, "Aquam", 10, 4),
            _control(levant, "Auram", 10, 4),
            _control(levant, "Ignem", 10, 4),
            _control(levant, "Terram", 12, 4),
            b.power(
                "Unseen",
                4,
                0,
                "Imaginem",
                rtd=("Personal", "Sun", "Individual"),
                level=20,
                does="No mortal sense can find him; he may show himself and "
                "vanish again at will while it lasts. Second Sight, angels "
                "and demons see through it, and magic can find him. As the "
                "Veil of Invisibility, PeIm 20, for the book's Invisibility 6.",
            ),
            _strength(
                levant, 2, 4, " Once it was 8: his strength has drained with his Might."
            ),
            _summon(levant, 12, 15, 4, "to his side"),
            _travel(levant, 12, 15, 4),
        ],
        vis=[BodyVis(15, "Ignem", "in his body")],
        appearance=(
            "About twelve feet tall and very broad in the shoulder, with "
            "jet-black skin and curled ram's horns, in loose white trousers "
            "and a white sash, his face fixed in gloom."
        ),
        notes=paragraphs(
            "The marid bound to the copper lamp of A'la al-Din, the tailor's "
            "son from China whose tale the Arabian Nights may have gained "
            "late (the book lets a storyguide who wants history strict leave "
            "the lamp out). Whoever rubs the lamp calls him and whoever holds "
            "it commands him, with as many orders as the holder likes from "
            "chapter 6's list of services a bound jinni gives; the three "
            "wishes came later. The lamp has passed down A'la al-Din's line, "
            "each heir spending his Might, which stood at 80 and is now 15. "
            "Old, worn and resentful, he still has all his skill, if little "
            "of his raw power. The book places neither the lamp nor its "
            "owner.",
            JINN_NATURE,
            DAWN + " " + _wounds(3),
        ),
        secrets=(
            "Someone who meets the conditions of his release can free him "
            "from the lamp, and only he knows what they are; the book leaves "
            "them to the storyguide, and says they are hard. Freed, he could "
            "be a lasting friend; refused, he makes his holders' lives a "
            "misery."
        ),
    )
    _MADE["al_qatil"] = b.creature(
        "Al-Qatil, the Slayer",
        page="p. 89",
        realm="Infernal",
        might=20,
        form="Vim",
        block={
            "characteristics": _chars(0, 0, -2, -3, 5, 4, 5, 4),
            "virtues_flaws": [
                "Lightning Reflexes",
                "Weakness",
                ("Ways of the {land}", {"land": "Desert"}),
                "Magical Air",
            ],
            "abilities": [
                ("Brawl", 4, "fist"),
                ("Living Language: Arabic", 5, "peasants' speech"),
                ("Second Sight", 3, "jinn"),
                ("Magic Sensitivity", 3, "jinn"),
                ("Single Weapon", 6, "long sword"),
            ],
            "traits": {"Murderous": 6, "Brave": 5, "Evil": 5},
        },
        attacks=[
            b.attack("Fist", 4, 9, 8, 5),
            b.attack("Long sword", 6, 15, 11, 11),
            b.attack("Long sword and round shield", 6, 15, 13, 11),
        ],
        soak=10,
        fatigue_levels=FATIGUE,
        equipment="Long sword, round shield, partial chain mail.",
        powers=[
            b.power(
                "Kindle the Rage",
                1,
                3,
                "Mentem",
                does="Stirs anger in someone near him, adding 1 to rolls on a "
                "trait of anger; he may hold the power for several passions. "
                "The book's Psychomachia (Anger) 3.",
            ),
            b.power(
                "Beast Shape",
                4,
                0,
                "Corpus",
                rtd=("Personal", "Sun", "Individual"),
                level=20,
                does="Takes the shape of any living thing, a man among them, "
                "within 4 steps of his own Size, keeping his speech; to see "
                "through a human disguise others must beat his Int + 4 with "
                "Per + Awareness. MuCo(An) 20 (Base 10, +2 Sun), for the "
                "book's Shapechange to Animal 4; worked on another (Touch, "
                "+5 levels and 1 more Might) it allows a Stamina stress roll "
                "of 9+.",
            ),
            b.power(
                "Ghul's Quickness",
                1,
                3,
                "Corpus",
                does="Adds 2 to Dexterity or 1 to Quickness for one roll.",
            ),
            b.power(
                "The Second Blow",
                2,
                2,
                "Corpus",
                does="His own power, the ghul's legend made real: after he "
                "calls on it, the next blow that wounds him undoes, instead, "
                "the wounds of the last blow that struck him. It lasts for "
                "that one blow. The book allowed it twice a day; now each use "
                "costs its Might.",
            ),
        ],
        vis=[
            BodyVis(3, "Ignem", "in his body"),
            BodyVis(2, "Terram", "in his sword"),
            BodyVis(2, "Herbam", "in his shield"),
        ],
        appearance=(
            "In his own shape a squat, red-skinned man in chain mail with a "
            "sword and shield; he usually hides it under another."
        ),
        notes=paragraphs(
            "An Infernal jinni of the Ghul tribe who hires himself out to "
            "whoever pays. Other jinn shun him. He likes mortal armies best, "
            "for the fighting and slaughter, and for the chance to feed on "
            "those he cuts down while the battle keeps everyone busy; his "
            "Weakness is for human flesh. He changes his looks to slip into "
            "the ranks.",
            JINN_NATURE,
            DAWN + " " + _wounds(0),
        ),
        secrets=(
            "He can pass as an ordinary soldier among a covenant's grogs, "
            "where he sows quarrels until they are ripe for mutiny."
        ),
    )


# -- chapter 7: the naddaha --


def _naddaha(levant: Levant) -> None:
    b = levant.b
    _MADE["naddaha"] = b.creature(
        "Naddaha",
        page="p. 90",
        realm="Infernal",
        might=20,
        form="Mentem",
        how_many="a lone creature at a well or oasis, most often in Upper Egypt",
        block={
            "characteristics": _chars(0, 0, 1, 0, 5, 4, 3, 3),
            "abilities": [
                ("Brawl", 5, "grapple"),
                ("Living Language: Arabic", 5, "Egyptian speech"),
            ],
            "traits": {"Cruel": 5},
        },
        attacks=[
            b.attack("Fist", 3, 8, 8, 5),
            b.attack("Grapple (the spiked embrace)", 3, 8, 8, None),
        ],
        soak=8,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Plea at the Well",
                2,
                1,
                "Mentem",
                rtd=("Voice", "Momentary", "Individual"),
                level=30,
                does="Each time she asks something of her victim, he must "
                "make a Stamina roll of 12+ or do it unquestioning; a cynic "
                "may add to the roll and a kindly soul take away. She asks "
                "for a drink first, and then to be held. ReMe 30 at 2 Might "
                "points, as the book prices it.",
            ),
        ],
        vis=[BodyVis(2, "Mentem", "in her larynx")],
        appearance=(
            "An old woman muffled in a black milaya. Under her clothes her "
            "body is covered in long spikes as sharp as razors; unclothed "
            "her Presence is -5."
        ),
        notes=paragraphs(
            "One of the deadliest things in the Levant. She haunts wells "
            "and oases, calling a lone traveller over with a plea for water "
            "or some other likely excuse, and likes handsome victims best, "
            "perhaps from spite at her own ugliness. When he is close she "
            "crushes him against her spikes. She hides when more than one "
            "person comes. TC&TC counts naddahas among the spirits that are "
            "not true jinn, so Sihr has no special hold on her.",
            "She nearly always grapples. Once she holds a victim he is "
            "immobilised and takes a wound level each round, starting with "
            "the round she seizes him, until her hold is broken. " + _wounds(0),
        ),
        secrets=(
            "She throws what is left of her victims into the nearest river, "
            "so the bodies drift downstream from her well."
        ),
    )


# -- Secrets in Sand: Amber's cat --


def _luigi(levant: Levant) -> None:
    b = levant.b
    _MADE["luigi"] = b.creature(
        "Luigi",
        page="p. 7",
        source=SIS,
        realm="Magic",
        might=13,
        form="Animal",
        size=-3,
        block={
            "characteristics": _chars(1, 3, 0, 0, -3, 0, 3, 3),
            "virtues_flaws": ["Magic Animal", "Lightning Reflexes", "Piercing Gaze"],
            "abilities": [
                ("Awareness", 2, "sounds"),
                ("Stealth", 6, "hunting"),
            ],
            "traits": {"Curious": 4, "Independent": 2, "Cruel to enemies": 1},
        },
        attacks=[b.attack("Claws and teeth", 2, 5, 6, -1)],
        soak=1,
        fatigue_levels=FATIGUE,
        vis=[
            BodyVis(1, "Animal", "in his left eye"),
            BodyVis(1, "Animal", "in his right eye"),
            BodyVis(1, "Animal", "in his brain"),
        ],
        appearance="An ordinary-sized cat whose white fur is tipped with gold.",
        notes=paragraphs(
            "Amber the Golden's familiar (her sheet has the bond). The choosing "
            "was mutual, and each leaves the other room "
            "to be themselves. He loves the leopard's shape Amber's From Cat "
            "to Cat gives him. Presence and Communication n/a as printed.",
            "Combat from the Definitive Edition's claws (Init Qik + -1, "
            "Attack Dex + 2, Defense Qik + 3, Damage Str + 2), with no Brawl "
            "score printed. " + _wounds(-3),
        ),
    )


# -- chapter 6: Wardat's Familiarities --


def _familiarities(levant: Levant) -> None:
    b = levant.b
    for key, name, realm, form, what in (
        (
            "aziza",
            "'Aziza",
            "Magic",
            "Mentem",
            "The ghost of Wardat al-Quds's grandmother.",
        ),
        (
            "hiss",
            "Hiss",
            "Magic",
            "Ignem",
            "An airy spirit of fire.",
        ),
        (
            "lucius",
            "Lucius",
            "Infernal",
            "Vim",
            "A demon. A sahir may summon a demon but never command one.",
        ),
        (
            "al_manqai",
            "Al-Manqa'i, the Bog-Dweller",
            "Magic",
            "Vim",
            "A jinni of the Ghul tribe, though not a corrupt one: its Might "
            "is Magic. Bound to Wardat's service.",
        ),
        (
            "sharif",
            "Sharif, the Noble",
            "Magic",
            "Vim",
            "A jinni of the Marid tribe. Bound to Wardat's service.",
        ),
    ):
        _MADE[key] = b.creature(
            name,
            page="p. 67",
            realm=realm,
            might=15,
            form=form,
            notes=paragraphs(
                what,
                f"{MIGHT_ONLY} the book names it among Wardat's Familiarities "
                f"with a Might of 15 and gives no stat block; its Form ({form}) "
                "is the pack's choice. The storyguide builds the rest if it is "
                "needed.",
            ),
        )


# -- finish: homes and links --


def finish(levant: Levant) -> None:
    """Set each creature at its place and link the place to it."""
    b = levant.b
    aedes = _aedes_site(levant)
    for key, creature in _MADE.items():
        if key in AT_AEDES:
            place = aedes or levant.places.get("syria") or levant.places.get("levant")
        else:
            keys, words, region = HOMES[key]
            place = _home(levant, keys, words)
            if place is None:
                place = levant.places.get(region) or levant.places.get("levant")
        if place is None:
            continue
        creature.place_id = place.id
        if not any(link.target_id == creature.id for link in place.links):
            b.link(place, "creatures", creature, ROLE[key])


def _home(
    levant: Levant, keys: tuple[str, ...], words: tuple[str, ...]
) -> Neighbour | None:
    """The first of `keys` a part made, else a place whose name holds one
    of `words`."""
    for key in keys:
        if key in levant.places:
            return levant.places[key]
    places = [n for n in levant.b.saga.neighbours if n.kind == "place"]
    for word in words:
        found = next((p for p in places if word.casefold() in p.name.casefold()), None)
        if found is not None:
            return found
    return None


def _aedes_site(levant: Levant) -> Neighbour | None:
    aedes = levant.covenants.get("aedes_veritatis")
    if aedes is not None and aedes.place_id:
        return levant.b.saga.neighbour(aedes.place_id)
    return None
