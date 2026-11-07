"""The Flying Castle of Thomae, in paraphrase of Legends of Hermes, chapter
six (pp. 121-138), with the book's Timeline of the Order (p. 139) in the
legend's biography: Thomae of Tytalus, the wreck of his castle and its
treasures, Santa Lucia and its people, the griffons and their nest, the
story Flights of Fancy, and what the book leaves open about his secret.

The wreck lies in the Alps in the book's telling, but it says to move
Santa Lucia to suit the saga, and it prints no aura for any of these
sites, so a place here has no aura and no realm. Griffons are entered as
Magic, the book's "Magic (Faerie?) Might" being a question it leaves
open. Stat blocks are the book's; the rest is a summary, not its words."""

from __future__ import annotations

from typing import Any

from ...models import BodyVis, Neighbour
from ..builder import (
    Builder,
    StatBlock,
    characteristics,
    dormant,
    joined_lines,
    paragraphs,
    titled,
    vf_minor,
    vf_ward,
    wound_ranges,
)

TYTALUS = "house_tytalus"
VERDITIUS = "house_verditius"
LOCALLY = "Locally"
RUMOURED = "Rumoured"

WOUNDS_NOTE = "Wound ranges are as the block prints them. "

FEROCITY = (
    "Ferocity",
    {"detail": "may use Confidence points only when home is threatened"},
)
HOMING = ("Homing Instinct", {"detail": "always knows where home lies from it"})

NESTS_OF_GOLD = (
    "A catch-all: griffons find, dig out and work gold with it, and it is "
    "what let them hole the side of the tower."
)
GRAPPLE_NOTE = (
    "Grapple does no damage of its own, but on later rounds the griffon may "
    "add its Grapple Strength to the Attack Roll of its beak."
)
COM_NOTE = "The book prints no Communication ('Com -')."
FEMALE_LOOK = (
    "Head, forequarters and forelimbs of an eagle, and the torso, hind legs "
    "and tail of a lion, with feathered wings. It flies with startling speed "
    "and skill for its bulk, and is strong despite the bird's slight bones "
    "of its front half."
)
MALE_LOOK = (
    "Head, forequarters and forelimbs of an eagle, and the torso, hind legs "
    "and tail of a lion, but more heavily muscled than the female, above all "
    "in the forequarters. It has no wings."
)
MALE_SPINES = (
    "Defensive horns and spines stand out from the body, thickest at the neck."
)


def _times(entry: str | tuple[str, dict[str, str]], count: int) -> list[Any]:
    return [entry] * count


def _griffon_block(
    *,
    cha: dict[str, int],
    qualities: list[Any],
    abilities: list[tuple[str, int, str]],
) -> StatBlock:
    return {
        "characteristics": cha,
        "virtues_flaws": [
            "Magical Monster",
            FEROCITY,
            HOMING,
            "Keen Vision",
            *qualities,
        ],
        "abilities": abilities,
        "traits": {"Defends home": 5, "Brave": 3},
    }


def _griffon_abilities(
    *,
    animal_handling: int,
    home_lore: int,
    gold_lore: int,
    athletics: tuple[int, str],
    awareness: int,
    brawl: tuple[int, str],
    hunt: int,
    second_sight: int,
    survival: int,
) -> list[tuple[str, int, str]]:
    found = [
        ("Area Lore", home_lore, "home territory"),
        ("Athletics", athletics[0], athletics[1]),
        ("Awareness", awareness, "prey"),
        ("Brawl", brawl[0], brawl[1]),
        ("Hunt", hunt, "horses"),
        ("Second Sight", second_sight, "Illusions"),
        ("Survival", survival, "home terrain"),
    ]
    if gold_lore:
        found.insert(1, ("Area Lore", gold_lore, "gold rich territory"))
    if animal_handling:
        found.insert(0, ("Animal Handling", animal_handling, "griffons"))
    return found


def _griffons(b: Builder, nest: Neighbour) -> None:
    gilded = b.power("Nests of Gold", 5, -2, "Terram", does=NESTS_OF_GOLD)
    juvenile_cha = characteristics(0, 3, 2, 0, 4, 1, 1, 3)
    adult_cha = characteristics(0, 3, 2, 0, 7, 1, 1, 2)
    hatchling_cha = characteristics(0, 3, 2, 0, 2, 0, 1, 4)
    magic_note = (
        "Printed as Magic (Faerie?) Might: whether griffons are of Magic or "
        "Faerie is left open. "
    )
    juvenile_notes = paragraphs(
        magic_note + COM_NOTE + " " + GRAPPLE_NOTE,
        "Griffons may raise young together, as lions and some birds do, the "
        "elder helping guard, feed and teach the younger. A flock of "
        "juveniles snatches what it wants and flees, and does not fight to "
        "the death. " + wound_ranges(2) + " As printed.",
    )

    b.creature(
        "Griffon, Female Hatchling",
        page="p. 136",
        realm="Magic",
        might=5,
        form="Animal",
        size=1,
        cunning=True,
        confidence=(1, 3),
        place=nest,
        block=_griffon_block(
            cha=hatchling_cha,
            qualities=[
                "Improved Abilities",
                vf_minor("Long-Winded"),
                vf_minor("Puissant Athletics"),
                vf_minor("Second Sight"),
                vf_minor("Strong-Willed"),
            ],
            abilities=_griffon_abilities(
                animal_handling=0,
                home_lore=3,
                gold_lore=0,
                athletics=(3, "flight"),
                awareness=4,
                brawl=(2, "claws"),
                hunt=2,
                second_sight=1,
                survival=3,
            ),
        ),
        attacks=[
            b.attack("Beak", 4, 3, 6, 3),
            b.attack("Grapple", 0, 2, 7, None),
            b.attack("Large Claws", 4, 9, 10, 6),
        ],
        soak=1,
        fatigue_levels="OK, 0, -1, -3, -5, Unconscious",
        vis=[BodyVis(1, "Animal", "heart")],
        appearance="About the size of a human, much of it wing. " + FEMALE_LOOK,
        notes=paragraphs(
            magic_note + COM_NOTE + " " + GRAPPLE_NOTE,
            "Athletics is 3 and +2 from Puissant. The book misprints the -3 "
            "wound range as 7-2; the entry follows the pattern of the block, "
            "7-12. " + wound_ranges(1),
            "Found in the lair, or hatched from an intact egg, as the "
            "storyguide decides. The book's words on size disagree: "
            "human-sized here (p. 133), but young griffons raised at a "
            "covenant stay little bigger than dogs for decades (p. 126).",
        ),
    )
    b.creature(
        "Griffon, Female Juvenile",
        page="p. 134",
        realm="Magic",
        might=15,
        form="Animal",
        size=2,
        cunning=True,
        confidence=(1, 3),
        how_many="a flock",
        place=nest,
        block=_griffon_block(
            cha=juvenile_cha,
            qualities=[
                ("Focus Power", {"focus": "Nests of Gold"}),
                "Improved Abilities",
                ("Improved Attack", {"detail": "beak"}),
                ("Improved Attack", {"detail": "claws"}),
                ("Improved Damage", {"detail": "beak"}),
                ("Improved Damage", {"detail": "claws"}),
                *_times("Improved Soak", 2),
                vf_minor("Improved Characteristics"),
                vf_minor("Long-Winded"),
                vf_minor("Puissant Athletics"),
                vf_minor("Second Sight"),
                vf_minor("Strong-Willed"),
            ],
            abilities=_griffon_abilities(
                animal_handling=1,
                home_lore=4,
                gold_lore=1,
                athletics=(5, "flight"),
                awareness=5,
                brawl=(5, "claws"),
                hunt=4,
                second_sight=3,
                survival=4,
            ),
        ),
        attacks=[
            b.attack("Beak", 3, 12, 10, 8),
            b.attack("Grapple", 3, 7, 9, None),
            b.attack("Large Claws", 3, 14, 12, 8),
        ],
        soak=7,
        fatigue_levels="OK, 0, -1, -3, -5, Unconscious",
        powers=[gilded],
        vis=[BodyVis(3, "Animal", "heart")],
        appearance="The size of a small horse. " + FEMALE_LOOK,
        notes=juvenile_notes
        + " Athletics is 5 and +2 from Puissant, included in the printed "
        "figures. High fantasy sagas might use them as flying mounts for "
        "magi, and faeries may model their own mounts on them.",
    )
    b.creature(
        "Griffon, Female Adult",
        page="p. 134",
        realm="Magic",
        might=30,
        form="Animal",
        size=3,
        cunning=True,
        confidence=(2, 5),
        place=nest,
        block=_griffon_block(
            cha=adult_cha,
            qualities=[
                ("Focus Power", {"focus": "Nests of Gold"}),
                "Improved Abilities",
                ("Improved Attack", {"detail": "beak"}),
                ("Improved Attack", {"detail": "claws"}),
                ("Improved Attack", {"detail": "grapple"}),
                "Improved Confidence",
                ("Improved Damage", {"detail": "beak"}),
                *_times(("Improved Damage", {"detail": "claws"}), 3),
                ("Improved Defense", {"detail": "beak"}),
                ("Improved Defense", {"detail": "claws"}),
                *_times("Improved Fatigue", 2),
                ("Improved Initiative", {"detail": "beak"}),
                ("Improved Initiative", {"detail": "claws"}),
                *_times(("Improved Initiative", {"detail": "grapple"}), 2),
                *_times("Improved Soak", 4),
                *_times(vf_minor("Improved Characteristics"), 2),
                vf_minor("Long-Winded"),
                vf_minor("Puissant Athletics"),
                vf_minor("Second Sight"),
                vf_minor("Strong-Willed"),
            ],
            abilities=_griffon_abilities(
                animal_handling=5,
                home_lore=5,
                gold_lore=3,
                athletics=(7, "flight"),
                awareness=5,
                brawl=(8, "claws"),
                hunt=4,
                second_sight=5,
                survival=5,
            ),
        ),
        attacks=[
            b.attack("Beak", 5, 15, 14, 11),
            b.attack("Grapple", 8, 12, 11, None),
            b.attack("Large Claws", 5, 17, 16, 20),
        ],
        soak=11,
        fatigue_levels="OK, 0, -1, -3, -5, Unconscious",
        powers=[gilded],
        vis=[BodyVis(6, "Animal", "heart")],
        appearance="The size of a small horse. " + FEMALE_LOOK,
        notes=paragraphs(
            magic_note + COM_NOTE + " " + GRAPPLE_NOTE,
            "Athletics is 7 and +2 from Puissant. Fiercely territorial: only "
            "one should appear in any one scenario.",
            WOUNDS_NOTE + "Light 1-8, Medium 9-16, Heavy 17-24 at -4 (the "
            "book prints -4 here, where the usual penalty is -5), "
            "Incapacitated 25-32, Dead from 33.",
        ),
    )
    b.creature(
        "Griffon, Male Hatchling",
        page="p. 137",
        realm="Magic",
        might=5,
        form="Animal",
        size=1,
        cunning=True,
        confidence=(1, 3),
        place=nest,
        block=_griffon_block(
            cha=hatchling_cha,
            qualities=[
                "Improved Abilities",
                vf_minor("Long-Winded"),
                vf_minor("Puissant Brawl"),
                vf_minor("Second Sight"),
                vf_minor("Strong-Willed"),
            ],
            abilities=_griffon_abilities(
                animal_handling=0,
                home_lore=3,
                gold_lore=0,
                athletics=(3, "running"),
                awareness=4,
                brawl=(2, "claws"),
                hunt=2,
                second_sight=1,
                survival=3,
            ),
        ),
        attacks=[
            b.attack("Beak", 4, 5, 8, 3),
            b.attack("Grapple", 0, 4, 9, None),
            b.attack("Large Claws", 4, 11, 12, 6),
        ],
        soak=3,
        fatigue_levels="OK, 0, -1, -3, -5, Unconscious",
        vis=[BodyVis(1, "Animal", "heart")],
        appearance="About the size of a human. "
        + MALE_LOOK
        + " The horns and spikes of an adult have not yet come.",
        notes=paragraphs(
            magic_note + COM_NOTE + " " + GRAPPLE_NOTE,
            "Brawl is 2 and +2 from Puissant. The book misprints the -3 "
            "wound range as 7-2; the entry follows the pattern of the block, "
            "7-12. " + wound_ranges(1),
        ),
    )
    male_nature = (
        "Horns come at adolescence, a straight pair from the forehead on most, "
        "with spikes from many joints, worst in the ruff, a ring of them "
        "guarding the throat and widest on the breast and between the "
        "shoulders; they are deadly to prey struggling in the griffon's "
        "grasp. Magi dispute what males are: the old texts do not mention "
        "them, though heraldry now and then does, and some suspect a faerie "
        "species living with the magical griffon, since they are found by "
        "nests they cannot fly to."
    )
    b.creature(
        "Griffon, Male Juvenile",
        page="p. 135",
        realm="Magic",
        might=15,
        form="Animal",
        size=2,
        cunning=True,
        confidence=(1, 3),
        how_many="a flock, or wandering alone",
        place=nest,
        block=_griffon_block(
            cha=juvenile_cha,
            qualities=[
                ("Focus Power", {"focus": "Nests of Gold"}),
                "Improved Abilities",
                ("Improved Attack", {"detail": "beak"}),
                ("Improved Attack", {"detail": "claws"}),
                ("Improved Damage", {"detail": "beak"}),
                ("Improved Damage", {"detail": "claws"}),
                *_times("Improved Soak", 2),
                vf_minor("Improved Characteristics"),
                vf_minor("Long-Winded"),
                vf_minor("Puissant Brawl"),
                vf_minor("Second Sight"),
                vf_minor("Strong-Willed"),
            ],
            abilities=_griffon_abilities(
                animal_handling=1,
                home_lore=4,
                gold_lore=1,
                athletics=(5, "running"),
                awareness=5,
                brawl=(5, "claws"),
                hunt=4,
                second_sight=3,
                survival=4,
            ),
        ),
        attacks=[
            b.attack("Beak", 3, 12, 10, 8),
            b.attack("Grapple", 3, 9, 11, None),
            b.attack("Large Claws", 3, 16, 14, 8),
        ],
        soak=9,
        fatigue_levels="OK, 0, -1, -3, -5, Unconscious",
        powers=[gilded],
        vis=[BodyVis(3, "Animal", "heart")],
        appearance="The size of a small horse. " + MALE_LOOK + " " + MALE_SPINES,
        notes=paragraphs(
            juvenile_notes,
            "Spikes: joint spikes do +5 damage to anyone who lands a melee "
            "attack on it, grappling included. Brawl is 5 and +2 from Puissant.",
            "The storyguide may instead have young males driven from the "
            "pride, as lions are, to roam looking for gold. One that finds "
            "enough heaps it up roughly to draw a female, and the two make a "
            "nest and a territory; a rich covenant might draw one in. " + male_nature,
        ),
    )
    b.creature(
        "Griffon, Male Adult",
        page="p. 135",
        realm="Magic",
        might=30,
        form="Animal",
        size=3,
        cunning=True,
        confidence=(2, 5),
        place=nest,
        block=_griffon_block(
            cha=adult_cha,
            qualities=[
                ("Focus Power", {"focus": "Nests of Gold"}),
                "Improved Abilities",
                ("Improved Attack", {"detail": "horns"}),
                *_times(("Improved Attack", {"detail": "grapple"}), 2),
                "Improved Confidence",
                *_times(("Improved Damage", {"detail": "horns"}), 2),
                ("Improved Damage", {"detail": "spikes"}),
                ("Improved Defense", {"detail": "horns"}),
                ("Improved Defense", {"detail": "grapple"}),
                *_times("Improved Fatigue", 2),
                *_times(("Improved Initiative", {"detail": "horns"}), 2),
                *_times(("Improved Initiative", {"detail": "grapple"}), 3),
                *_times("Improved Soak", 4),
                *_times(vf_minor("Improved Characteristics"), 2),
                vf_minor("Long-Winded"),
                vf_minor("Puissant Brawl"),
                vf_minor("Second Sight"),
                vf_minor("Strong-Willed"),
            ],
            abilities=_griffon_abilities(
                animal_handling=5,
                home_lore=5,
                gold_lore=3,
                athletics=(7, "running"),
                awareness=5,
                brawl=(8, "horns"),
                hunt=4,
                second_sight=5,
                survival=5,
            ),
        ),
        attacks=[
            b.attack("Beak", 2, 14, 13, 8),
            b.attack("Grapple", 11, 15, 15, None),
            b.attack("Large Claws", 2, 16, 15, 11),
            b.attack("Large Horns", 10, 17, 18, 16),
        ],
        soak=15,
        fatigue_levels="OK, 0, -1, -3, -5, Unconscious",
        powers=[gilded],
        vis=[BodyVis(6, "Animal", "heart")],
        appearance="The size of a small horse. " + MALE_LOOK + " " + MALE_SPINES,
        notes=paragraphs(
            magic_note + COM_NOTE + " " + GRAPPLE_NOTE,
            "Spikes: joint spikes do +8 damage to anyone who lands a melee "
            "attack on it, grappling included. Brawl is 8 and +2 from "
            "Puissant, included in the printed figures. Fiercely territorial: "
            "only one should appear in any one scenario.",
            WOUNDS_NOTE + "Light 1-8, Medium 9-16, Heavy 17-24 at -4 (the "
            "book prints -4 here, where the usual penalty is -5), "
            "Incapacitated 25-32, Dead from 33.",
            male_nature,
        ),
    )


def _road_creatures(b: Builder) -> None:
    b.creature(
        "Elemental Blizzard",
        page="p. 129",
        realm="Magic",
        might=20,
        form="Aquam",
        size=3,
        cunning=True,
        block={
            "characteristics": characteristics(2, 2, 0, -6, 6, 5, -5, 1),
            "virtues_flaws": [
                "Magic Thing",
                ("Ways of the {land}", {"land": "Mountains"}),
                "Poor Memory",
                "Short Attention Span",
                "Simple-Minded",
                ("Greater Power", {"detail": "Drown"}),
                ("Greater Power", {"detail": "Chill Touch"}),
                ("Greater Power", {"detail": "Charge of the Angry Winds"}),
                ("Major Virtue", {"virtue": "Greater Immunity to Fire"}),
                *_times("Improved Abilities", 4),
                (
                    "Improved Powers",
                    {
                        "detail": "Chill Touch cost -2, Charge of the Angry "
                        "Winds cost -1 and Init +2, Drown Init +5"
                    },
                ),
                vf_minor("Lightning Reflexes"),
                vf_minor("Tough"),
            ],
            "abilities": [
                ("Area Lore", 4, "local"),
                ("Athletics", 4, "flight"),
                ("Awareness", 4, "animals"),
                ("Brawl", 4, "suffocate"),
                ("Hunt", 2, "animals"),
                ("Penetration", 6, "Chill Touch power"),
            ],
            "traits": {"Storm": 5},
        },
        soak=11,
        powers=[
            b.power(
                "Chill Touch",
                0,
                5,
                "Ignem",
                does="Its freezing touch does +10 damage, and metal armor "
                "gives no benefit against it.",
            ),
            b.power(
                "Charge of the Angry Winds",
                0,
                7,
                "Auram",
                does="As the spell of that name, adding the elemental's "
                "Strength to every Ease Factor for acting within the wind.",
            ),
            b.power(
                "Drown",
                0,
                5,
                "Auram",
                does="It wraps a victim and fills her lungs with ice, forcing "
                "a Deprivation roll (ArM5 pp. 180-181). She may break free by "
                "the Grappling rules (ArM5 p. 174).",
            ),
        ],
        vis=[BodyVis(4, "Auram", "body")],
        appearance="A menacing grey fog with shapes of men and animals in it.",
        notes=paragraphs(
            "An encounter for parties on the way to the crash site, built as "
            "a water elemental by Realms of Power: Magic. It has no self to "
            "speak of: it attacks because it is a blizzard's rage, not from "
            "hatred or to guard anything. It may attack up to its Size in "
            "enemies a round. Its immunity to fire and its disregard for much "
            "armor make it hard on groups weak in combat magic.",
            "Injured, it loses Might equal to the wound's penalty. Large "
            "pieces broken off in combat hold part of its vis; it always "
            "knows where they are and tries to rejoin them. "
            + wound_ranges(3)
            + " As printed.",
        ),
    )
    b.creature(
        "Despair Demon",
        page="p. 130",
        realm="Infernal",
        might=10,
        form="Aquam",
        size=1,
        confidence=(1, 3),
        how_many="a kind, in the Alps",
        order="Accusers (variant)",
        weakness="Protected Group: truly penitent people.",
        block={
            "characteristics": characteristics(1, 1, 0, 1, 2, 2, 2, 1),
            "virtues_flaws": ["Weak-Willed"],
            "abilities": [("Brawl", 6, "trample")],
            "traits": {"Doubt": 3},
        },
        attacks=[b.attack("Rolling Ball of Spikes (trample)", 8, 16, 14, 13)],
        soak=7,
        fatigue_levels="OK, 0, -1, -3, -5, Unconscious",
        powers=[
            b.power(
                "Coagulation",
                1,
                -1,
                "Aquam",
                does="Gives it a body, a spiked ball of icicles a yard wide. "
                "Forming takes a round; it can shed the body almost at once.",
            ),
            b.power(
                "Elemental Control of Air",
                0,
                1,
                "Auram",
                does="Any Creo, Muto or Rego Auram effect at 1 Might a "
                "magnitude (variable cost), minor effects only, of level no "
                "more than its Might Score. It hides paths, wipes footprints, "
                "cuts visibility and smothers cries for help to part "
                "stragglers from a group.",
            ),
            b.power(
                "Envisioning",
                1,
                0,
                "Mentem",
                does="Small changes to a victim's dreams, making them darker "
                "and more ominous.",
            ),
            b.power(
                "Obsession",
                3,
                -5,
                "Vim",
                does="When a human commits a venial sin and the demon spends "
                "Might in reply, it may force spiritual doubt. At the next "
                "crisis of worthiness the storyguide rolls a simple die +3, "
                "the player a simple die + a suitable Personality Trait, with "
                "adjustments for a harsh environment. If the demon's total is "
                "higher the character gains Doubt +1. Acting on that score "
                "puts him in a state of sin, and the demon coagulates and "
                "kills him.",
            ),
        ],
        vis=[BodyVis(2, "", "body")],
        appearance="A ball of icicles a yard across.",
        notes=paragraphs(
            "These prey on travelers in the Alps, confusing and separating "
            "them. Worn by privation and the fear of death, a victim may lose "
            "faith in the Lord, and the demon then kills him before he can "
            "repent. Best used on those who leave the group, like scouts or "
            "foragers. Built by Realms of Power: The Infernal. The book "
            "prints no Art for its vis. " + wound_ranges(1) + " As printed.",
        ),
    )


THOMAE_SUMMARY = paragraphs(
    "Thomae of Tytalus, c. 1122 to 1198, a showman and adventurer who made "
    "the boldest enchantment the Order has seen, a castle that flies, and a "
    "host of lesser magic items. He cared nothing for the wrangling his "
    "House loves. His challenge to himself was a boy's dream of living in a "
    "floating castle, and he paid for it by killing monsters and by hiring "
    "out to covenants at Wizard's War.",
    "In 1191 he dropped from sight and came back with the castle. The alarm "
    "was great. After a tense tribunal he agreed to take it, high up and by "
    "night, to a range of mountains and stay there, where no mundane would "
    "see it and be provoked, and elder magi would not have to think of "
    "Wizard's War. He soon tired of that. By 1195 it was plain he was "
    "slipping out to sea in the dark and visiting desolate places in other "
    "Tribunals, and a tribunal met again; his politics saw him through, as "
    "no accuser could show that the Order had come to harm. In 1198, 22 "
    "years ago, he and the castle vanished. Some say he went to Transylvania "
    "to build weapons platforms for the Tremere, some that he is exploring, "
    "some that the Devil claimed him and the castle went to dust and ash in "
    "mid-air. Search has found nothing, and most magi expect some hint of "
    "him to surface.",
    "Many want the castle and would pay well for it: the Hermetic Architects "
    "to study it for breakthroughs, the militant Houses as a weapons platform, "
    "supply engine or movable command post, House Mercere as a post for "
    "exchanging messages. His lesser items are rumored to carry folk between "
    "castle and ground, govern the weather and hurl gouts of fire. It is "
    "said they could defend the castle from any attack and let his whole "
    "turb fly, and his riches, taken from the far places of Europe and "
    "Africa, may be more folklore than fact.",
)

THOMAE_SECRETS = [
    titled(
        "How the castle fell",
        "His true end (p. 122): crossing the Alps, the castle overflew a "
        "griffon nesting site. With no Aegis, it could be attacked directly. A "
        "griffon clawed through the base of the High Tower to get at his "
        "treasury, and the castle listed and fell.",
    ),
    titled(
        "How Thomae died",
        "He wore an item that kept him from falling, so as the castle dropped "
        "he was dashed against the navigation room's ceiling. His remains are "
        "scattered through the wreck.",
    ),
    titled(
        "Thomae's ghost",
        "He died by violence without rites, so his ghost can be reached and is "
        "probably deranged (p. 123), though the Faerie Dealings story supposes "
        "he left none (p. 138).",
    ),
    titled(
        "Thomae's great deceit",
        "His great deceit (pp. 122-123): he gave out that a team of skilled "
        "helpers had made the castle by strange rituals and rare components, "
        "with mighty wards and weapons. In truth it is a bronze building on a "
        "lesser enchanted device made in one season, and his missing years "
        "were spent fitting out a laboratory big and secret enough for the "
        "Verditius he hired, and raising that magus's fee and silence.",
    ),
    titled(
        "A life that does not add up",
        "His life does not add up: too much is fitted in, and his notes show "
        "more ancillary items than he could have made or paid for (p. 138).",
    ),
    titled(
        "What all know of Thomae",
        joined_lines(
            "Ease Factor 0, Known to All:",
            "- A magus of House Tytalus, active late last century.",
            "- He built a flying castle.",
            "- He had trouble at law.",
            "- He vanished about 20 years ago.",
        ),
    ),
    titled(
        "What is widely known of Thomae",
        joined_lines(
            "Ease Factor 6, Widely Known:",
            "- He vanished young for a magus, and many think he lives, tyrannizing "
            "natives somewhere remote in Africa or Asia.",
            "- Politics bored him; flight was his obsession.",
            "- His castle was of bronze.",
            "- He was known as a slayer of magical beasts and a magical mercenary.",
            "- He was charged with provoking mundanes by showing off his castle.",
            "- He ranged far after vis to pay for it, long in the Holy Land and Africa.",
            "- He settled his case by promising not to fly over civilized lands, "
            "though it was doubted he kept to it.",
        ),
    ),
    titled(
        "Uncommon knowledge of Thomae",
        joined_lines(
            "Ease Factor 12, Uncommon Knowledge:",
            "- He told his tribunal that many of his magic items were bought, not made.",
            "- The castle's costly safety gear for his servants won their loyalty.",
            "- He claimed to be a Hermetic Architect, of one of the Order's least "
            "secret mystery societies.",
            "- Quaesitores examined the castle during his case, but it was held to "
            "be his sanctum, so not even fellow Architects went aboard.",
        ),
    ),
    titled(
        "Thomae's lost secrets",
        joined_lines(
            "Ease Factor 18, Lost Secrets:",
            "- His timeline is wrong: he seems to have fitted in more than he "
            "could, so he probably lied about what he did and when.",
            "- He was probably no Hermetic Architect, though he said so.",
        ),
    ),
    titled(
        "What Hermetic Architects know of Thomae",
        joined_lines(
            "Ease Factor 12, Hermetic Architects only:",
            "- Many effects he called integral to the castle were impossible "
            "without a breakthrough in Hermetic Architecture.",
        ),
    ),
    titled(
        "Storyguide Notes",
        paragraphs(
            "The wreck's record has how the castle fell. See the stories of "
            "Thomae's Secret. How deep the deceit goes is the storyguide's.",
            "What the Order Remembers (p. 122; roll Intelligence + Order of "
            "Hermes Lore, pp. 10-11; +3 for a character with some reason to "
            "care about his works or his legal case; the recollections may be "
            "false).",
        ),
    ),
]

TIMELINE = joined_lines(
    "Timeline of the Order (p. 139)",
    "767: The Order of Hermes is founded at Durenmar.",
    "c. 857: Hérisson born.",
    "867: Hérisson joins House Bjornaer at the Gathering of Twelve Years.",
    "881: Hérisson passes his Gauntlet, a magus of the Normandy Tribunal.",
    "c. 885: Conciatta born.",
    "895: Baltasar hears of a Gifted child and buys her from her father; "
    "Conciatta's apprenticeship begins.",
    "900-990: Hérisson develops his research on creating vis.",
    "910: Conciatta passes her Gauntlet.",
    "915: Conciatta founds a covenant in Saraqusta with Currito.",
    "923: Conciatta publishes The Application of Vim to the Supernatural "
    "Humors; her experiments leave her Gift damaged.",
    "925: Baltasar of Bonisagus marched for Infernal corruption.",
    "933: Conciatta studies the Dominion in Toledo.",
    "937: Conciatta submits her last papers and withdraws from the Order.",
    "c. 940: Hermanus born.",
    "952: Hérisson moves his laboratory and sanctum to his garden.",
    "961: Evidence of infernal corruption in House Tytalus comes to light.",
    "965: Hermanus of Tremere completes his Gauntlet and joins the Order.",
    "980: Currito leaves Saraqusta and Conciatta.",
    "986: Fortunata born, daughter of the Prince of Milan.",
    "987: At the Gathering of Twelve Years Hérisson argues with the Primus "
    "of Bjornaer; the House has no interest in talk of peace.",
    "990: Hérisson submits a thesis on his original research to the Library "
    "of Durenmar.",
    "996: Fortunata apprenticed to Apollo of Jerbiton.",
    "999: Conciatta's last breakthrough.",
    "1000: Her Gift overcoming her, Conciatta takes sanctuary in Toledo.",
    "1001: Hérisson meets the primus of House Diedne to ease the hostilities.",
    "1002: Gypaetus of Bjornaer kills Hérisson in a Wizard's War.",
    "1004: The Schism War begins.",
    "1007: Conciatta enters Final Twilight and her spirit fractures.",
    "1011: Fortunata passes her Gauntlet and takes her Hermetic name.",
    "1013: The Vexillation of the Adamant Rook is formed.",
    "1015: Fortunata frees Lucida from the cleft tree.",
    "1017: Fortunata joins the summer covenant of Cupressa Nigra and begins "
    "publishing translations from ancient tongues.",
    "1019: House Bjornaer leaves hiding with a Harmonist agenda drawn from "
    "Hérisson's philosophy.",
    "1048: Fortunata acquitted of diabolism.",
    "1055: Fortunata acquitted of spying by spirit magic.",
    "1061: Fortunata, senior maga of Cupressa Nigra, leaves it for a remote "
    "island, but opens her house in Venice to the Redcaps.",
    "1067-1123: Cupressa Nigra is abandoned as its junior magi move on. "
    "Fortunata goes on translating, writes Hermetic texts on spirit lore, "
    "circulates a few on Principles Lore, and gains a name as a powerful "
    "eccentric.",
    "1070: The Vexillation of the Adamant Rook is dissolved.",
    "1098: Hermanus and the wing of Coeris holding his laboratory disappear, "
    "assumed a Twilight brought on by a magical botch. The Vexillation of "
    "the Unbarred Gateway is formed.",
    "1104: The Vexillation of the Unbarred Gateway is dissolved.",
    "1110: Amarantha of Tremere disappears.",
    "1115: Velius sets his archmagus challenge.",
    "1120: Velius succumbs to Final Twilight.",
    "c. 1122: Thomae born.",
    "1123: Last contact with Fortunata before Twilight takes her.",
    "1198: Thomae and his castle vanish.",
)

WRECK_SUMMARY = paragraphs(
    "A castle of bronze lies broken on the side of a snowy peak, its courtyard "
    "a single bronze sheet, its finials cast as dogs, its bells hanging silent "
    "from their chains. The foot of the High Tower is torn open by huge claws.",
)

WRECK_SECRETS = [
    titled(
        "Where the wreck lies",
        "Thomae's castle crashed in the Alps, on a peak beyond a range of "
        "mountains about half a day west of Santa Lucia.",
    ),
    titled(
        "The heaped bodies",
        "The bodies of Santa Lucians killed on the road lie heaped in the "
        "courtyard of Thomae's wreck, their ghosts penned there by the Dogs of "
        "the Castle.",
    ),
    titled(
        "The Flight Disk",
        "The Flight Disk (p. 123): a single flat circle of hard stone 300 paces "
        "across and just under a pace thick, in a metal jacket beneath the "
        "bronze courtyard: a lesser enchanted device, not Hermetic Architecture, "
        "of one season's work. ReTe level 33, Pen +0, constant. R: Personal, D: "
        "Diameter, T: Individual. Flies the castle at a horse's running speed, "
        "steered by colored lights. It triggers itself whenever the spell is not "
        "running, so a single PeVi cannot bring it down and the flight never "
        "jerks. Base 3, +1 Diameter, +3 size, +1 stone; unlimited use +10, "
        "environmental trigger +3.",
    ),
    titled(
        "The Control Chain",
        "The Control Chain (p. 123): a steel chain fixed to the disk's center, "
        "rising through the High Tower to the laboratory, ending in a metal bulb. "
        "Doors in its tube let it be reached from many rooms. Touch it and speak "
        "Latin commands, and the bulb shines in colors and strengths that steer "
        "the disk. CrIg level 9, Pen +0, constant. R: Personal, D: Sun, T: "
        "Individual. Base 1, +2 Sun, +2 caster's control of color; constant "
        "use +4. It has many spare patterns, called by speaking numbers, meant "
        "for later additions to the disk. A separate item from the disk.",
    ),
    titled(
        "What killed Thomae",
        "The disk's steering by light is what killed Thomae: the griffon's "
        "hole cracked the jacket, sunlight fell on the disk, and the castle "
        "listed before he could work out why.",
    ),
    titled(
        "Why the castle has no Aegis",
        "Boundary effects (p. 123): they do not move, so an Aegis of the "
        "Hearth or Boundary ward on Thomae's castle would be left behind as it "
        "flew. That is why it has no Aegis. Thomae trusted its reputation and "
        "his soldiers.",
    ),
    titled(
        "Thomae's laboratory notes",
        "Laboratory notes (pp. 123-124): his laboratory was wrecked, but his "
        "best books survive in magical storage chests. The codices have lab notes "
        "for: the flying disk; the large laboratory it was made in; the control "
        "chain (useful for triggering other items from afar, in mines or under "
        "water); the siege finials, plain mystical artillery that look like all "
        "the other finials on the walls; Thomae's anchor, a whimsical ship's "
        "anchor trailed through the air behind and below the castle that hides "
        "the castle from the ground but not itself, bought or made after his "
        "legal troubles; Thomae's whip, his talisman, a long bronze chain that "
        "moves by magic, used to work things at a distance, extend Touch range "
        "and lash in battle; the falling bells; and the medallions of flight, "
        "invisibility, safe falling, attack and espionage.",
    ),
    titled(
        "The falling bells",
        "The falling bells (p. 124): large bells in public spaces, whose sound "
        "the castle's bronze carried far. While in free fall they chime, and all "
        "who hear can fly for the rest of the day. Special winches let out one "
        "loop of chain at a time, so a bell drops a second before the slack "
        "takes it. These were for emergencies.",
    ),
    titled(
        "The training bells",
        "Training bell (p. 124): smaller bells for training, festivities and "
        "missions; servants learned to leap to a tower top and back, some to "
        "fly in earnest. ReCo level 35, Pen +0. R: Touch, D: Sun, T: Individual. "
        "Worked by holding the handle and ringing. The user flies at a brisk walk "
        "for the rest of the day. Tapped on a child as it rings it gives guided "
        "flight, and in theory it could be swung as a club to set a victim "
        "flying. Base 10, +1 Touch, +2 Sun; constant use +10.",
    ),
    titled(
        "Thomae's tender",
        "Thomae's tender (pp. 124-125): a floating metal platform for lifting "
        "stores, faster than the castle, able to scout ahead or catch up. It was "
        "meant as expedition vehicle and lifeboat but never so used, and lacks "
        "climate control, artillery or incorrupt food stores. A large moonstone "
        "powers it: moved to a like metal plate, it powers that one. Its words "
        "are plain Latin, found by patient trial, in the ruins, or in the "
        "laboratory. ReTe level 34, Pen +0, constant. R: Touch, D: Sun, T: "
        "Individual. Carries as much as can be piled on it. Base 3, +1 Touch, +2 "
        "Sun, +2 size, +2 metal; constant use +4.",
    ),
    titled(
        "Covenant goods in the wreck",
        "Covenant goods (p. 125): a laboratory, a private library, and stores "
        "to keep Thomae's servants in luxury, much destroyed by the crash and "
        "the weather since. Not enough to equip a covenant's laboratories, but "
        "there may be enchanted lab equipment, valuable books, or wealth to "
        "buy supplies.",
    ),
    titled(
        "The castle's bronze",
        "The bronze (p. 125): Thomae chose it because a skin of corrosion stops "
        "its decay. It sells at 200 to 300 Mythic Pounds a ton, or up to 1,500 "
        "reworked as fine brassware. The trouble is weight, remoteness and "
        "flooding the market, not supply.",
    ),
    titled(
        "What the griffons attack",
        "The griffons attack anything flying larger than a bird, horses and "
        "draft animals, and gold-carriers.",
    ),
    titled(
        "Storyguide Notes",
        paragraphs(
            "The book sets the crash in the Alps and leaves the place to the "
            "saga. Skilled questioning of the villagers (Presence with "
            "Leadership or Charm, Ease Factor 12) gives a closer position. No "
            "aura is printed. How badly it is damaged is the storyguide's. "
            "Mended or altered a little, it can be the start of a Spring "
            "covenant (p. 121). The griffon alternatives story offers other "
            "reasons it fell.",
            "The griffons' claw marks: Intelligence + Magic Lore against 18 "
            "shows a giant eagle made them, 12 if the site has been scoured for "
            "mixed giant eagle feathers and lion hairs. A griffon may be "
            "glimpsed far off (Perception + Awareness 18). A ghost or a "
            "befriended faerie hound may tell.",
            "No levels are printed for the items in Thomae's notes, and the "
            "book says only that the notes survive, not where the items lie.",
            "If the characters cannot fly, a medallion, the tender or a "
            "training bell may turn up here to bring the griffons' lair within "
            "reach (p. 133). Storyguides may place items from the book's other "
            "chapters here. See Flights of Fancy.",
        ),
    ),
]


def build(b: Builder) -> None:
    wreck = b.place(
        "The Wreck of Thomae's Castle",
        realm="",
        summary=WRECK_SUMMARY,
        secrets=WRECK_SECRETS,
        status=RUMOURED,
        known=LOCALLY,
    )
    old_village = b.place(
        "Santa Lucia",
        realm="",
        summary="A tiny mountain village of folk who speak a rough, homely "
        "Latin and are ruled by three councilors with metal badges of office. "
        "Its pasture has grown too poor for its growing numbers, and the "
        "village is packing up to move before winter.",
        secrets=[
            titled(
                "Who the Santa Lucians are",
                "Santa Lucia's people are the castle's surviving covenfolk and "
                "their children.",
            ),
            titled(
                "Skills of the old Santa Lucians",
                "Many of Santa Lucia's old ones have skills of use to magi, "
                "learned aboard Thomae's castle, and a covenant short of "
                "skilled folk could recruit them (p. 126).",
            ),
            titled(
                "The villagers' folk tale",
                "Their folk tale (p. 131): they served a wizard, Thomae, with a "
                "castle in the sky, which 'bird-cats' destroyed. He had made "
                "sure that his servants could fly a little if it fell, and they "
                "escaped into the eye of the sun, where the monsters could not "
                "follow. Intelligence + Magic Lore 12 shows the bird-cats to be "
                "griffons.",
            ),
            titled(
                "The councilors' badges",
                "The three badges of Santa Lucia's councilors were the marks of "
                "Thomae's bodyguards.",
            ),
            titled(
                "The village's last tie",
                "The councilors' badges are Santa Lucia's last symbolic tie to "
                "Thomae's castle.",
            ),
            titled(
                "Storyguide Notes",
                "The book places Santa Lucia in the Alps and tells the "
                "storyguide to change its name and place to suit the saga. "
                "Intelligence + Order of Hermes Lore 12 recognizes the badges "
                "(21 normally, lowered because the characters are looking for "
                "just this and hold a twin). If it suits, they are magical, and "
                "may pass some of Thomae's defenses. The book names one "
                "councilor, Rogerio. See Flights of Fancy.",
            ),
        ],
        status=RUMOURED,
        known=LOCALLY,
    )
    new_valley = b.place(
        "The New Valley of Santa Lucia",
        realm="",
        summary="A valley the Santa Lucians are making their own, with carts "
        "on the road, temporary bridges and fords, and a village still to "
        "build.",
        secrets=[
            titled(
                "Whose land the valley is",
                "The New Valley of Santa Lucia is an allod: land no nobleman "
                "claims, which makes a fine site for a Spring covenant.",
            ),
            titled(
                "Storyguide Notes",
                "A Spring covenant here can have the castle and the Santa "
                "Lucians as the saga's first story (p. 126). In that case the "
                "griffons are likely too much for newly Gauntleted magi, and "
                "one of the griffon alternatives should take their place. Its "
                "location is left to the saga. Santa Lucia's work there is in "
                "Flights of Fancy.",
            ),
        ],
        status=RUMOURED,
        known=LOCALLY,
    )
    nest = b.place(
        "The Griffons' Nest of Gold",
        realm="",
        summary="A nest high in some place no man can climb to, woven of gold, "
        "griffon feathers and the woods of strange trees, with eggs like "
        "great polished agates.",
        secrets=[
            titled(
                "Where the griffons lair",
                "Griffons lair where few can reach. The griffons' range "
                "overlaps the crash site of Thomae's castle.",
            ),
            titled(
                "The Nest of Gold",
                "The Nest of Gold (p. 125): a fortune in gold, and worth more as a "
                "focus: +7 to enchantments for defending a home or protecting "
                "treasure. To use it, it must reach a laboratory with its "
                "structure whole, by careful handling, skilled goldsmithing to "
                "solder it, or magic, until it can be stabilized and enchanted. "
                "An intact nest may also be needed for eggs to hatch.",
            ),
            titled(
                "Eggs of Agate",
                "Eggs of Agate (p. 125): griffon eggs are flawless agates the size "
                "of an ostrich's. Agate in the mouth is said to stop thirst, and "
                "sorcerers have used it since Rome to rule rivers and storms. "
                "Linked to Auram magic (+3), protection from storms (+5), and "
                "protection from venom (+7). Shells of hatched eggs may be "
                "enchanted the same way.",
            ),
            titled(
                "Baby griffons",
                "Baby griffons (pp. 125-126): hatched at a covenant they grow "
                "slowly, little bigger than dogs for decades, and do as they are "
                "told if they accept someone local as head of their pride. They "
                "act like flying kittens with keen sight and the strength to "
                "tear holes in things, and may suit as familiars. Magic can hasten "
                "their growth, but grown griffons are far harder to train, being "
                "notoriously impossible to coerce.",
            ),
            titled(
                "Griffons and farming",
                "Griffons prey on livestock and would ruin farming, so they "
                "belong in far mountains. The Avars' flight west in the sixth "
                "century is sometimes laid to a plague of them (p. 130).",
            ),
            titled(
                "Storyguide Notes",
                "The book gives no place for the nest, only that the griffons' "
                "range overlaps the crash site. Ways of finding it are in "
                "Flights of Fancy. Rules for training magical animals are in "
                "Realms of Power: Magic p. 81.",
            ),
        ],
        status=RUMOURED,
        known=LOCALLY,
    )
    b.place(
        "Thomae's Secret Laboratory",
        realm="",
        summary="A workshop no one has found, built to make the greatest "
        "enchantment the Order has seen.",
        secrets=[
            titled(
                "Who keeps the laboratory",
                "Thomae set his secret laboratory up to make the disk, and his "
                "Verditius collaborator has kept it (p. 138).",
            ),
            titled(
                "Notes for the laboratory",
                "Thomae's lab notes for his secret laboratory survive in the wreck.",
            ),
            titled(
                "Storyguide Notes",
                "Where it is, the book leaves open; one suggestion puts it in a "
                "small African or Asian kingdom Thomae conquered. Its stories "
                "are in Thomae's Secret: The Verditius.",
            ),
        ],
        status=RUMOURED,
        known=LOCALLY,
    )

    thomae = b.magus(
        "Thomae of Tytalus",
        covenant=None,
        house=TYTALUS,
        age=None,
        summary=THOMAE_SUMMARY,
        secrets=THOMAE_SECRETS,
    )
    thomae.description.biography = TIMELINE
    b.link(thomae, "places", wreck, "His castle, and his remains")

    andros = b.magus(
        "Andros",
        covenant=None,
        house="",
        age=None,
        type="companion",
        summary="A former mercenary in his mid-twenties, now stealing unseen "
        "from the great houses of a large town. He keeps a bronze medal of "
        "Saint Thomas and thinks it holy.",
        secrets=[
            titled(
                "Where Andros got the medal",
                "He got the medal from Roberto, whose vanishing in battle he "
                "saw, and made sure to take it when arrows killed Roberto. He "
                "thought of sending it home, but a tiny Alpine village seemed "
                "too much trouble.",
            ),
            titled(
                "Roberto's belongings",
                "He has Roberto's other belongings, which may point to Santa "
                "Lucia, and knows where Roberto lies buried.",
            ),
            titled(
                "The medallion",
                "The medallion (pp. 127-128): small bronze on a chain of the "
                "same, a man's portrait on one side and a stylized castle on "
                "the other, like a pilgrim's medal. Maker's marks at the bottom "
                "edge.",
            ),
            titled(
                "The medal's false saint",
                "Saint Thomas's marks on Andros's medal are wrong "
                "(Intelligence + Church Lore 3): the halo is a spiral and "
                "nothing else names him, though Thomas is patron of architects, "
                "so the castle could pass.",
            ),
            titled(
                "Why Andros's prayer works",
                "His garbled Latin prayer works because the triggers of two "
                "powers are 'Thomae' and the Latin for 'help'. It takes him two "
                "rounds, and he always uses both, not knowing they are "
                "separable.",
            ),
            titled(
                "What Andros does not know",
                "He knows the medal eases his landings, not that free fall does "
                "it. He does not know that blowing on it spies. Roberto did, "
                "which is why he kissed it before battle: to hear his "
                "commanders and get himself put in the reserve.",
            ),
            titled(
                "A training medallion",
                "Andros's medallion was made for training covenfolk: slower "
                "flight, far longer lasting. Scent of frying onions marks the "
                "maker's sigil while Aerial Dancer and Veil of Invisibility "
                "last.",
            ),
            titled(
                "The medallion's powers",
                joined_lines(
                    "Aerial Dancer: ReCo 35, Pen +0, unlimited/day. R: Touch, D: "
                    "Sun, T: Individual. Spoken 'Thomae'. Moves the wearer "
                    "through the air any way he likes at a running pace. Base 10, "
                    "+1 Touch, +2 Sun; unlimited +10. The other medallions fly "
                    "for two minutes at a running horse's speed (Base 15, +1 "
                    "Touch, +1 Diameter; unlimited +10).",
                    "Failure to Fall: ReCo 25, Pen +0, unlimited/day. R: Touch, D: "
                    "Diameter, T: Individual. Triggered by free fall. Lowers the "
                    "faller about a foot a second for 120 feet, then reactivates "
                    "if he is falling still, with a brief gap in the onion smell "
                    "by which covenfolk claimed to judge their drop. Base 5, +1 "
                    "Touch, +1 Diameter; unlimited +10. (The book says two "
                    "minutes and, a sentence on, three.)",
                    "Veil of Invisibility: PeIm 25, Pen +0, 24 uses/day. R: "
                    "Touch, D: Sun, T: Individual. Spoken 'help' in Latin. As the "
                    "spell (ArM5 p. 146). Base 4, +1 Touch, +2 Sun, +1 moving; 24 "
                    "uses +5.",
                    "Whispering Winds: printed ReAu 15, Pen +0, 1 use/day. R: "
                    "Sight, D: Concentration, T: Individual. Worked by blowing on "
                    "the medallion. As the spell (ArM5 p. 127, which has it as "
                    "InAu 15). Eavesdrops on a group in view. Unique.",
                ),
            ),
            titled(
                "The other medallions",
                "Thomae's three shield grogs each had a medallion, a little "
                "different from each other, and his bodyguards made a strange "
                "three-dimensional martial art of them. The others are with the "
                "leaders of the Santa Lucians (p. 124).",
            ),
            titled(
                "Storyguide Notes",
                "No threat to a band of seasoned grogs. The book gives him no "
                "statistics: choose a generic to fit what he becomes after the "
                "story (p. 127).",
            ),
        ],
    )
    roberto = b.magus(
        "Roberto",
        covenant=None,
        house="",
        age=None,
        type="grog",
        summary="A dead soldier of a mercenary company, who said he came "
        "from a tiny Alpine village called Santa Lucia and always kissed his "
        "medal before a fight.",
        secrets=[
            titled(
                "Roberto's theft",
                "Son of Rogerio, whose medallion he stole before going off to soldier.",
            ),
            titled(
                "Roberto's ghost",
                "Shot down by arrows. He died in battle and was buried anyhow, "
                "so his ghost can be summoned (p. 129).",
            ),
            titled(
                "Roberto's remains",
                "Returning Roberto's remains to Rogerio will be taken very "
                "kindly (p. 131).",
            ),
        ],
    )
    rogerio = b.magus(
        "Rogerio",
        covenant=None,
        house="",
        age=None,
        type="companion",
        summary="One of the three councilors of Santa Lucia, old now, who "
        "wears a metal badge of office.",
        secrets=[
            titled(
                "Rogerio's past",
                "A ranking servant of Thomae, perhaps one of his guard.",
            ),
            titled(
                "Rogerio's lost medallion",
                "His badge replaces the medallion his son Roberto stole, and he "
                "wants the original back. He assumes at first that the "
                "characters took it from Roberto.",
            ),
            titled(
                "Winning Rogerio over",
                "His goodwill is worth having. He would not use a combat item "
                "now as he did when young, so another offer of position may "
                "sway him.",
            ),
            titled(
                "Rogerio's reckless son",
                "Andros's story fits what he recalls of his reckless son (p. 131).",
            ),
            titled("Storyguide Notes", "The book gives no statistics."),
        ],
    )
    flavia = b.magus(
        "Flavia of Verditius",
        covenant=None,
        house=VERDITIUS,
        age=None,
        summary="A living Verditius, maker of a bronze medal bearing a spiral. "
        "Her sigil is the smell of frying onions.",
        secrets=[
            titled(
                "Flavia's Arcane Connection",
                "She holds a fixed Arcane Connection to Thomae, taken to ensure "
                "he paid, and let him believe it destroyed.",
            ),
            titled(
                "Why Flavia never used it",
                "She has never used her Arcane Connection to Thomae, thinking he "
                "has made himself a king in Africa or Asia, and that it is folly "
                "to vex a magician-king with a flying fortress.",
            ),
            titled(
                "Storyguide Notes",
                "The characters must persuade her with skill to let them use "
                "it. To go on to the search for the secret laboratory, the "
                "storyguide should send them by another lead (p. 129). The book "
                "does not say she is the castle's Verditius collaborator.",
            ),
        ],
    )
    b.link(andros, "characters", roberto, "Took his medal")
    b.link(rogerio, "characters", roberto, "His son")
    b.link(rogerio, "places", old_village, "One of its three councilors")
    b.link(
        flavia, "characters", thomae, "Made a medal for him; holds an Arcane Connection"
    )

    b.creature(
        "The Dogs of the Castle",
        page="p. 132",
        realm="Faerie",
        might=5,
        form="Animal",
        size=1,
        cunning=True,
        how_many="hunting packs",
        place=wreck,
        block={
            "characteristics": characteristics(0, 2, -4, 0, 0, 2, 1, 2),
            "virtues_flaws": [
                ("Greater Power", {"detail": "Grasp Ghost"}),
                "Faerie Beast",
                ("External Vis (Minor)", {"detail": "finial"}),
                "Faerie Sight",
                "Improved Characteristics",
                "Sharp Ears (Minor)",
                "Large",
                "Incognizant",
                "Reckless (Minor)",
                vf_ward("cannot be inside"),
            ],
            "abilities": [
                ("Athletics", 5, "distance running"),
                ("Awareness", 6, "keeping watch"),
                ("Brawl", 5, "bite"),
                ("Hunt", 6, "track by scent"),
            ],
            "traits": {"Loyal to the castle": 5},
        },
        attacks=[b.attack("Bite (small teeth)", 2, 10, 9, 1)],
        soak=7,
        powers=[
            b.power(
                "Fearful Flaming Eyes",
                2,
                -2,
                "Corpus",
                rtd=("Eye", "Concentration", ""),
                level=15,
                does="Paralyzes outright a human who meets its gaze. Base 5, "
                "+1 Eye, +1 Concentration.",
            ),
            b.power(
                "Grasp Ghosts",
                2,
                0,
                "Mentem",
                rtd=("Touch", "Sun", ""),
                level=20,
                does="Seizes a ghost and drags it to the castle, where a ring "
                "of hounds keeps it from leaving. Base 5, +1 Touch, +2 Sun.",
            ),
            b.power(
                "Hands of the Animal",
                2,
                0,
                "Animal",
                rtd=("Touch", "Sun", ""),
                level=15,
                does="Constant. Carries and handles a thing as if with human "
                "hands of Strength +5. It must concentrate to do more than "
                "carry, to drop a thing, or to take up another. Base 3 (ReTe), "
                "+1 Touch, +2 Sun, +1 constant.",
            ),
        ],
        vis=[BodyVis(1, "Terram", "in finial")],
        appearance="Cunningly jointed bronze statues of dogs, moving of "
        "themselves, clanking and howling like machines.",
        notes=paragraphs(
            "Faeries who settled into the dog-shaped finials on the castle's "
            "walls, and took their shape and manners from them. They hunt in "
            "packs, by nature and because their three powers together cost "
            "more than one dog's Might, and they fight as trained groups. "
            "Their abilities are Pretenses; soak is a naturally armored form. "
            "Greater Power is printed Greater Faerie Power. "
            + wound_ranges(1)
            + " As printed.",
            "Killing them is easy at this Might, so the storyguide may raise "
            "it to steer players toward capturing, questioning or "
            "domesticating them, or add numbers. Some finials may be magic "
            "items for the castle's defense that a dog can trigger; destroying "
            "its body then destroys the item.",
        ),
        secrets=[
            titled(
                "Why the Dogs kill",
                "They guard the line between home and away from home, and the "
                "Santa Lucians, by moving, are crossing it. So they kill those "
                "hauling goods, and drag bodies and ghosts back to be 'at home' "
                "in the courtyard.",
            ),
            titled("Storyguide Notes", "See Flights of Fancy."),
        ],
    )
    _griffons(b, nest)
    _road_creatures(b)

    dormant(
        b.threat(
            "Flights of Fancy",
            place=wreck,
            antagonist="The griffons, and the Dogs of the Castle",
            moves="A track",
            summary="An unseen thief is robbing a large town near the "
            "covenant, by a power that looks like the work of a magus.",
            secrets=[
                titled(
                    "Where the thief's medal leads",
                    "The thief's medal leads to a mountain village, its bronze "
                    "hounds, and the wreck of Thomae's castle.",
                ),
                titled(
                    "What the griffons attack",
                    "Griffons attack gold-carriers, draft animals (horses above "
                    "all, which they love) and anything flying bigger than a "
                    "bird.",
                ),
                titled(
                    "Storyguide Notes",
                    "The adventure of the chapter (pp. 126-133). The Dogs and "
                    "griffons need not be fought: each has a subtler answer "
                    "below.",
                ),
            ],
            stages=[
                b.stage(
                    "Foreshadowing",
                    at=1,
                    clues="In earlier stories, let Thomae pass by in a word: "
                    "art of his castle, a mention in a legal case. Let griffons "
                    "be seen too: a covenant's old archmage's staff tipped with "
                    "an ostrich-egg agate a griffon laid, griffons as "
                    "decoration in art.",
                ),
                b.stage(
                    "The Hidden Thief",
                    at=2,
                    clues="Crimes by an invisible man in a large town near "
                    "the covenant. Reasons to care: magically aided crime "
                    "gets blamed on magi; the thief may be a magus, and a "
                    "public worry a Hermetic crime; a charm means a magus made "
                    "it, too near the covenant; such items often come from "
                    "murdered redcaps; a robbed man or his servants ask for "
                    "help or justice; the covenant's trade is hit.",
                ),
                b.stage(
                    "To Catch the Thief",
                    at=3,
                    clues="Get to a burgled site by bribes, social rolls, "
                    "magic or housebreaking. Awareness 6: the thief flew, for "
                    "the roof shows no tool or foot marks. A second roll: he "
                    "was looking for what he could find, not one thing. Catch "
                    "him by Arcane Connections at the site, by criminal "
                    "contacts tracing the goods, or by a pattern in the "
                    "robberies that sets a trap.",
                ),
                b.stage(
                    "Recognizing the Link",
                    at=4,
                    clues="The medal, held by Andros. Order of Hermes Lore 3: "
                    "the spiral is House Tytalus's. Order of Hermes Lore 9 ties "
                    "it to Thomae's legend, +3 for knowing the prayer to Saint "
                    "Thomas, +3 for Hermetic Architects. Intelligence + Magic "
                    "Theory 3: Verditius runes and a personal mark at the "
                    "bottom edge. Order of Hermes Lore 15 knows the mark, 12 "
                    "noting the onion sigil; House Verditius Lore 6, or 3. "
                    "Redcaps and hoplites can name the magus, perhaps for a "
                    "big favor. A player who sees it needs no roll.",
                ),
                b.stage(
                    "Following the Lead",
                    at=5,
                    clues="To Santa Lucia, by: Roberto's belongings; his ghost; "
                    "other Santa Lucian lads soldiering in a nearby war, as "
                    "guides; a redcap who knows; or Flavia of Verditius and "
                    "her Arcane Connection to Thomae.",
                ),
                b.stage(
                    "The Road",
                    at=6,
                    clues="An isolated, slow journey carrying what could "
                    "normally be bought on the way. Give spotlight to those "
                    "not yet used. Monsters: the Elemental Blizzard, the "
                    "Despair Demon. Environmental puzzles for spontaneous "
                    "casters and non-fighters: a fallen rope bridge over a "
                    "ravine; a path under unstable snow where noise brings "
                    "avalanches; a river swollen by early melt; long travel "
                    "above the snowline; a blizzard needing shelter or "
                    "diverting.",
                ),
                b.stage(
                    "The Santa Lucians",
                    at=7,
                    clues="The villagers race winter to shift goods and cattle "
                    "to new pasture. Solve their problems for their help "
                    "finding the castle: dig a well three feet wide and 30 "
                    "deep; clear or pave main roads; replace temporary bridges "
                    "and fords; raise chapel, mill, granary, calving sheds, "
                    "bakery and smokehouse; clear land for orchards and "
                    "fields; fence pasture; cut hay; slaughter and preserve "
                    "beasts that cannot winter. Their tales place the castle "
                    "half a day west, with no roll.",
                ),
                b.stage(
                    "The Dogs of the Castle",
                    at=8,
                    clues="Bronze dogs attack parties hauling goods to the new "
                    "site. Destroy them, or question them with Intellego "
                    "Mentem. The cause shows only to one who can read glamor, "
                    "or who sees the guarded heap of bodies at the wreck and "
                    "makes Intelligence + Faerie Lore 6. Faerie Lore 15 shows "
                    "that castle trinkets matter. A faerie may be tracked home.",
                    ignored="They go on killing the movers and penning their "
                    "ghosts at the castle.",
                    stopped="Fight them, at the cost of more attacks if the "
                    "tie remains.",
                    turned="If the leaders give up Thomae's badges and make "
                    "new symbols for the village, the last link is cut, and "
                    "the faeries lose interest. A hound attached to the "
                    "characters' story may guide them, even to the griffons, "
                    "to see a great battle.",
                ),
                b.stage(
                    "The Crash Site",
                    at=9,
                    clues="Claws holed the highest tower. Learning griffons did "
                    "it: claw marks; a ghost; a hound; a griffon sighted; or a "
                    "flock of juvenile females snatching horses, mules, "
                    "donkeys or unwarded gold and fleeing, not fighting to the "
                    "death.",
                    turned="Sneakery, played as an environmental puzzle: work "
                    "the wreck unnoticed by tunnels, by hiding the scent of "
                    "draft animals, by flying invisibly, or whatever fits the "
                    "Arts. No fight is needed, while repairing or salvaging.",
                ),
                b.stage(
                    "The Lair of the Griffons",
                    at=10,
                    clues="Only needed for the nest of gold, or if subtlety "
                    "fails. Finding it: horsemeat as bait (Intelligence + Artes "
                    "Liberales 12 recalls how Alexander trapped four griffons "
                    "with it and drove them through the air with carcasses "
                    "dangling before them), with an Arcane Connection kept to "
                    "the meat until a chick is fed; Intellego Animal on "
                    "feathers or hairs from the wreck, which must beat Magic "
                    "Resistance; a faerie who wants to witness the battle; or "
                    "following a beaten flock home.",
                    stopped="Combat with the griffons, adult female and male "
                    "(one of each at most), juveniles and hatchlings.",
                    turned="The nest, eggs and young become the troupe's.",
                ),
            ],
        )
    )
    dormant(
        b.threat(
            "Hatching the Griffons' Eggs",
            place=nest,
            antagonist="Time and ignorance",
            summary="Agate eggs from the nest of gold lie cold. No magus knows "
            "how they hatch, or even if they die away from their nest.",
            secrets=[
                titled(
                    "Whether the eggs die",
                    "It is unknown whether griffon eggs die outside the right "
                    "environment or wait for their mystic climate.",
                ),
                titled(
                    "Storyguide Notes",
                    paragraphs(
                        "Story seed (p. 125).",
                        "It may take a story to find a way to hatch the "
                        "griffons' eggs: a favor to the covenant with a great "
                        "library; a powerful Bjornaer said to take griffon "
                        "shape; Jerbiton covenants that train magical beasts, "
                        "and a maga at remote Valnastium with potent items for "
                        "training griffons, who may never have hatched one and "
                        "may be too far to reach in time.",
                    ),
                ),
            ],
        )
    )
    dormant(
        b.threat(
            "Griffon Alternatives",
            place=wreck,
            antagonist="A demon of Pride, or a flock of magical moths",
            summary="What if something other than griffons brought down the "
            "castle? It may be waiting for the next who tries to fly.",
            secrets=[
                titled(
                    "A demon of Pride",
                    "A demon: a powerful one of an Order that punishes human "
                    "sin struck Thomae's castle down, taking flight as Pride. "
                    "The castle mends with little trouble, and the mender "
                    "becomes its target.",
                ),
                titled(
                    "Magical moths",
                    "Moths: a flock of ethereal magical moths flew through the "
                    "side of Thomae's disk to the light within. Set the chain's "
                    "orb to black and offer another mystic light, with simple "
                    "CrIm or CrIg spells of Ring duration, to lure them out of "
                    "the works.",
                ),
                titled(
                    "Storyguide Notes",
                    "Alternatives to the griffons (p. 137), which the book also "
                    "suggests for a saga's first story (p. 126). The demon may "
                    "be mixed with the griffons to give the covenant a new "
                    "Enemy. The book gives no statistics.",
                ),
            ],
        )
    )
    dormant(
        b.threat(
            "Griffons in Other Tales",
            antagonist="The griffons of old stories",
            summary="Griffons guard more than a golden nest: old Greek tales "
            "set them at the edges of the world and beside the gods' arms.",
            secrets=[
                titled(
                    "Griffons by the north wind",
                    "Aristeas's lost Arimaspea, reported by Herodotus, sets "
                    "griffons close to the north wind, their land dividing "
                    "Hyperborea from the world. Magi after Hyperborean magic "
                    "(Ancient Magic) could tame one and use its migratory sense "
                    "to seek the land of gold.",
                ),
                titled(
                    "Aristeas the Nightwalker",
                    "Aristeas was a Nightwalker. In Hedge Magic's story a "
                    "faerie Aristeas tries to turn the cult from the Lady to "
                    "Apollo, and is said to have hidden his body in the "
                    "griffons' land.",
                ),
                titled(
                    "Griffons and the Titans' weapons",
                    "In the Hesperides quest (Ancient Magic), one outcome seeks "
                    "the weapons of the old gods. A Greek poem gives Zeus "
                    "griffons as guard dogs, so they may nest on the mountain "
                    "hiding the Titans' weapons.",
                ),
                titled("Storyguide Notes", "Ties to earlier books (p. 137)."),
            ],
        )
    )
    opening = (
        "What Thomae was hiding is the troupe's to choose (p. 138). Point to "
        "it with: who or what was his 'Verditius collaborator', and where is "
        "his ghost?"
    )
    dormant(
        b.threat(
            "Thomae's Secret: The Verditius",
            antagonist="Thomae's Verditius collaborator",
            summary="Thomae had a Verditius helper who has never claimed the "
            "credit. Why would a Verditius stay so modest?",
            secrets=[
                titled(
                    "Why the Verditius hides the laboratory",
                    "Thomae's Verditius collaborator has kept the secret "
                    "laboratory and hides it for a reason: it holds prohibited "
                    "faerie or demonic elements; or it lies at the heart of a "
                    "small African or Asian kingdom Thomae conquered, probably "
                    "against the Code; or it has spent twenty years turning out "
                    "flying squares that clip together into a platform for a "
                    "flying city.",
                ),
                titled("Storyguide Notes", opening),
            ],
        )
    )
    dormant(
        b.threat(
            "Thomae's Secret: Faerie Dealings",
            antagonist="The faerie come to collect",
            summary="Time and money should have stopped Thomae. Something "
            "else paid, and may yet come for the debt.",
            secrets=[
                titled(
                    "Built in Arcadia",
                    "Thomae built the castle and items in Arcadia, solving both "
                    "limits.",
                ),
                titled(
                    "What came back from Arcadia",
                    "If Thomae died in Arcadia unknowing, what came back was a "
                    "powerful faerie, which is why there is no ghost and why "
                    "creatures perfect for his story struck him down; his "
                    "wanderings to far mountains may have been his glamor "
                    "seeking to finish its script.",
                ),
                titled(
                    "The faerie debt",
                    "Faeries trade wishes for vitality, and so large a thing as "
                    "Thomae's castle brought out of Faerie means vast vitality "
                    "given, or promised. A collector comes, or takes the castle "
                    "back: a dark faerie wanting the blood of the dead of a war "
                    "he promised to start, or a Queen of Sylphs demanding the "
                    "tears of ten thousand babies, this century's rent for her "
                    "flying throne.",
                ),
                titled("Storyguide Notes", opening),
            ],
        )
    )
    dormant(
        b.threat(
            "Thomae's Secret: The Found Object",
            antagonist="Whatever the disk held down",
            summary="The control chain is plainly Hermetic. The great disk may "
            "be something far older.",
            secrets=[
                titled(
                    "What Thomae found in Egypt",
                    "Herodotus tells of Chemiss, a floating island bearing a "
                    "temple of Apollo. Hunting vis in Egypt, Thomae found that "
                    "a stone disc held it up, worked out, perhaps with help, "
                    "that colored lights steered it, and spent his missing "
                    "years ordering the lesser items.",
                ),
                titled(
                    "The Verditius ally's silence",
                    "Thomae's Verditius ally lets others think he built the "
                    "disk, keeping the bragging rights, and exposure would "
                    "wound his standing.",
                ),
                titled(
                    "Chemiss in myth",
                    "In myth, Latona or a priestess made the island of Chemiss "
                    "float to hide Apollo (Horus) from Typhon (Set); she was "
                    "the city goddess of Buto, with an oracle there by "
                    "Herodotus, so some trace may remain. So the disc hid a "
                    "faerie from a magical being in Egypt's Titanomachy.",
                ),
                titled(
                    "What lay beneath the disc",
                    "What else lay beneath Chemiss's disc: a weapons cache's "
                    "capstone, a faerie road's door? What goes on there now "
                    "Thomae has taken this barrier away?",
                ),
                titled("Storyguide Notes", opening),
            ],
        )
    )
    b.link(old_village, "places", new_valley, "Where the village is moving")
