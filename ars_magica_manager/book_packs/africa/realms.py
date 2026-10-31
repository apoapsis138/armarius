"""The Realms of North Africa and the mundane bestiary (Between Sand and Sea
pp. 90-143), in paraphrase.

The rules this chapter prints live elsewhere and are cited, not repeated:
the Settuten, Imhergi, Inenden, Bouda and Murabitin are entries of
data/tradition_catalog.json, their Virtues of data/virtue_flaw_catalog.json,
and the monstrous races and the jnun's Sihr are rules/africa.py's. This part
adds the named people, spirits, creatures, places and stories.

A being the book describes without numbers is a Bestiary record whose notes
say so. A Virtue, Flaw or Quality the catalog lacks is left off the block and
named in the creature's notes: Crushing Jaws, Smell Water and Survive Without
Water, and the Inenden status of Merin ag Gwafa. Thick Feathers, Thick Skin
and Thick Scales are the catalog's Thick Fur/Thick Scales. By the errata
(p. 86) the waral's Cunning, Communication, Soak and Survival are corrected,
the camel's powers are New Qualities, and "Transvestite" reads "Gender
Nonconforming"; the Hyena Pelt's calculation is corrected too (p. 13).
Books and vis belong to no covenant here and stand in words on their place
or person. The Pact of 1225, the Great Hunger and the Hope are hunger.py's."""

from __future__ import annotations

from typing import Any

from ...models import BodyVis, CreaturePower
from ..builder import (
    Builder,
    characteristics,
    dormant,
    paragraphs,
    vf_great,
    vf_minor,
    vf_puissant,
)

S = Builder.stage

#: The Fatigue levels the blocks print.
FATIGUE = "OK, 0, -1, -3, -5, Unconscious"
ONE_EXTRA_FATIGUE = "OK, 0/0, -1, -3, -5, Unconscious"
LONG_FATIGUE = "OK, 0/0, -1/-1, -3/-3, -5, Unconscious"

NO_NUMBERS = "The book prints no statistics for it."
AMADAGH_LEADS = "Faerie, one of the lowhush of the amadagh"

RUMOURED: dict[str, Any] = {"status": "Rumoured", "known": "In the region"}

WAYS = ("Ways of the {land}", {"land": "Desert"})
ANCHORED = ("Anchored to the {land}", {"land": "Desert"})
VOICE = ("Voice of the {land}", {"land": "Desert"})
NETWORK = ("{land} Regio Network", {"land": "Desert"})
THICK = "Thick Fur/Thick Scales"


def _times(entry: Any, count: int) -> list[Any]:
    """A Virtue or Quality the block takes `count` times."""
    return [entry] * count


def _major_virtue(virtue: str) -> tuple[str, dict[str, str]]:
    return ("Major Virtue", {"virtue": virtue})


def _major_flaw(flaw: str) -> tuple[str, dict[str, str]]:
    return ("Major Flaw", {"flaw": flaw})


def _minor_flaw(flaw: str) -> tuple[str, dict[str, str]]:
    return ("Minor Flaw", {"flaw": flaw})


def _strength(entry: str) -> tuple[str, dict[str, str]]:
    return (entry, {"characteristic": "Strength"})


def build(b: Builder) -> None:
    _winds(b)
    _sun_and_moon(b)
    _dead(b)
    _settuten(b)
    _minor_traditions(b)
    _inenden(b)
    _blue_men(b)
    _bouda(b)
    _monstrous_races(b)
    _jnun(b)
    _lowhush(b)
    _divine(b)
    _carthage(b)
    _beasts(b)
    _stories(b)


# -- the winds of the desert --


def _wind(b: Builder, name: str, appearance: str, notes: str) -> None:
    b.creature(
        name,
        page="pp. 90-91",
        realm="Magic",
        appearance=appearance,
        notes=paragraphs(notes, f"One of the Council of Winds. {NO_NUMBERS}"),
    )


def _winds(b: Builder) -> None:
    kaf_ajnoun = b.place(
        "Kaf Ajnoun",
        realm="Magic",
        aura=7,
        summary=paragraphs(
            "The Hall of Spirits, a high and citadel-shaped mountain standing "
            "out of the sands of the Fezzan, near the Tasili n Ajjer. The "
            "people round about keep away: it is fiercely hot, no wadi runs "
            "near, and its slopes betray the foot.",
            "The Tuareg say the lights and drums of the feasts on its summit "
            "carry for leagues. Jinn come there to meet the Winds and to deal "
            "in slaves, trinkets and vis.",
        ),
        levels=[
            b.level(
                "The Palace of the Winds",
                7,
                see="A sumptuous palace on the summit.",
                notes=paragraphs(
                    "Lesser zephyr spirits wait on the Winds here. The book "
                    "gives the mountain's aura and no separate one for this "
                    "regio.",
                ),
            )
        ],
    )
    b.faction(
        "The Council of Winds",
        realm="Magic",
        place=kaf_ajnoun,
        members=7,
        summary=paragraphs(
            "Most of the old spirits of the Maghreb faded when Islam came. "
            "The desert winds did not: they wander, are tied to no one sacred "
            "place, and hold the region their own whatever its people "
            "believe. Seven genii loci and daimons sit in council: the "
            "Chergui, the Gregale, the Haboob, the Harmattan, the Khamsin, "
            "the Simoon and the Sirocco.",
            "All of them roam, to the Levant and the East, and now and then "
            "to their peers in Iberia, Provence and the North, gathering the "
            "world's news. When Africa is the matter they meet at Kaf "
            "Ajnoun. They have lately argued over the Crusade at Damietta and "
            "what to do if it spreads west; before that, the Maghreb's "
            "pirates, the Romans and Garamantians, and the many caravans of "
            "the Great Desert.",
        ),
        wants=(
            "To keep the Great Desert dangerous and wild: they favour the "
            "deeds and the people that serve this."
        ),
    )
    _wind(
        b,
        "The Chergui",
        "An Arab traveller, quick to anger and dryly funny.",
        "The hot, dry east wind.",
    )
    _wind(
        b,
        "The Gregale",
        "A silent, muscular Arab or Greek sailor.",
        "A strong, cool wind, felt mostly south of Malta. It stands apart "
        "from most of what happens in Africa, yet will not miss a gathering "
        "of the spirits.",
    )
    _wind(
        b,
        "The Haboob",
        "A pack of wild painted dogs who take turns to speak in one voice, "
        "even within a sentence.",
        "The howling dust storm. It is famed for tearing apart the lost army "
        "of Cambyses II near Siwa in antiquity.",
    )
    _wind(
        b,
        "The Harmattan",
        "A listless Berber caravaner, often leading a weary, thirsty camel.",
        "The dry, dusty western trade wind, blowing out of the south across "
        "the Western Desert.",
    )
    _wind(
        b,
        "The Khamsin",
        "A spiteful, belligerent Egyptian warrior who ages quickly over the "
        "fifty days he rages along Africa's northern coast.",
        "A hot, dry and dusty wind that usually blows out of the south for "
        "fifty days, from after Easter until Pentecost. It carries dust, sand "
        "and terrible plagues, and spreads them gladly.",
    )
    _wind(
        b,
        "The Simoon",
        "A barely veiled woman who loves to dance: passionate, capricious and "
        "cruel without thinking of it.",
        'The desert cyclone, searing and dry, which the locals call "the poison wind."',
    )
    b.creature(
        "Sirocco, the Howling Thirst of the Maghreb",
        page="p. 91",
        realm="Magic",
        might=35,
        form="Auram",
        season="Winter",
        confidence=(2, 5),
        place=kaf_ajnoun,
        block={
            "characteristics": characteristics(2, 0, 1, -1, 1, 2, 2, 2),
            "virtues_flaws": [
                "Magic Spirit",
                "Magical Master",
                WAYS,
                "Homing Instinct",
                *_times("Improved Characteristics", 2),
                "Piercing Gaze",
                "Second Sight",
                "Self-Confident",
                "Wilderness Sense",
                ("Hunger for {form} Magic", {"form": "Auram"}),
                "Magical Air",
                "Proud (Major)",
                "Wanderlust",
                ANCHORED,
                *_times("Focus Power", 2),
                *_times("Greater Power", 3),
                _major_virtue("Magical Master"),
                *_times("Improved Abilities", 4),
                *_times("Improved Might", 5),
                "Improved Powers",
                "Lesser Power",
            ],
            "abilities": [
                ("Animal Ken", 3, "detecting fear"),
                ("Area Lore: Maghreb", 6, "caves"),
                ("Area Lore: Great Desert", 6, "ergs"),
                ("Athletics", 4, "charging"),
                ("Awareness", 4, "travelers"),
                ("Bargain", 3, "setting terms"),
                ("Brawl", 6, "dodge"),
                ("Concentration", 3, "Auram effects"),
                ("Dead Language: Latin", 5, "conversation"),
                ("Dead Language: Punic", 5, "conversation"),
                ("Etiquette", 4, "jinn"),
                ("Folk Ken", 4, "first impressions"),
                ("Guile", 5, "misleading"),
                ("Living Language: Arabic", 5, "warnings"),
                ("Living Language: Berber", 5, "warnings"),
                ("Living Language: French", 3, "warnings"),
                ("Living Language: Italian", 3, "bargaining"),
                ("Living Language: Catalan", 3, "bargaining"),
                ("Organization Lore: Berber Tribes", 5, "travel routes"),
                ("Penetration", 2, "Auram effects"),
                ("Second Sight", 4, "invisible things"),
                ("Single Weapon", 5, "falchion"),
                ("Stealth", 5, "stalking"),
                ("Wilderness Sense", 4, "finding oases"),
            ],
            "traits": {"Proud": 6, "Unyielding": 3, "Fierce": 3, "Wind": 3},
            "reputations": {"Awesome Force of Nature (local)": 5},
        },
        attacks=[
            b.attack("Dodge", 2, None, 9, None),
            b.attack("Falchion", 3, 12, 9, 5),
            b.attack("Fist", 2, 8, 8, 2),
        ],
        soak=2,
        fatigue_levels="None",
        tires=False,
        powers=[
            b.power(
                "Presence",
                0,
                0,
                "Imaginem",
                rtd=("Arc", "Sun", "Ind"),
                level=35,
                does="A Constant effect. With a few moments' concentration he "
                "learns anything that happens within the bounds of the Great "
                "Desert.",
            ),
            b.power(
                "Donning the Corporeal Veil",
                0,
                1,
                "Corpus",
                level=25,
                does="Takes on a material form (Cr(Re)Co).",
            ),
            b.power(
                "Eidolon",
                0,
                2,
                "Imaginem",
                rtd=("Touch", "Conc", "Ind"),
                level=15,
                does="An illusory form material beings can see and hear. It "
                "moves and speaks as he directs and lasts until he has no use "
                "for it.",
            ),
            b.power(
                "Master of Sandstorms",
                7,
                0,
                "Auram",
                does="Up to 7 points, a point a magnitude: any non-ritual "
                "Creo, Muto or Rego Auram effect up to 7th magnitude, with "
                "Terram or Ignem prerequisites as he likes.",
            ),
            b.power(
                "Master of Thirst",
                0,
                -8,
                "Aquam",
                rtd=("Voice", "Mom", "Part"),
                level=25,
                does="Draws most of the water out of any object (PeAq(Co)).",
            ),
        ],
        vis=[BodyVis(7, "Auram", "in the dust on his clothes or in his cyclone")],
        appearance=(
            "A Tuareg warrior, robed and veiled, a falchion at his side and "
            "sand swirling round his feet; or a whirling cyclone of dust and "
            "sand."
        ),
        notes=paragraphs(
            "The hot, dust-laden wind out of the south-east, which often "
            "reaches hurricane speed. In Africa it prefers its Arabic name, "
            "the Ghibli, and grudgingly owns that Europeans know Sirocco "
            "better. It appears most often as a veiled Tuareg raider, and "
            "always as some sort of warrior, short-tempered and with a biting "
            "falchion.",
            "Proud and Wind are its Essential Traits. Its Qualities are "
            "printed as Focus Power: Auram x2, Greater Power (Donning the "
            "Corporeal Veil, Eidolon, Presence), Major Virtue (Magical "
            "Master), Improved Abilities x4, Improved Might x5, Improved "
            "Powers (Focus Power, Master of Thirst) and Lesser Power (Master "
            "of Thirst). The block gives three Greater Powers for the three "
            "named.",
        ),
    )


# -- the Sun and the Moon --


def _sun_and_moon(b: Builder) -> None:
    b.faction(
        "The Cult of the Sun and Moon",
        realm="Magic",
        summary=paragraphs(
            "In antiquity the Sun and Moon were worshipped with fanatical "
            "devotion from small shrines all over the Tell, and with animal "
            "sacrifice; the historians record it again and again as central "
            "to Ancient Libyan life. In a few places the sun was Sol Invictus, "
            "but in most she was the goddess Tafuyt, and the Moon was the god "
            "Ayyur. St. Augustine and Samuel the Confessor both tell of "
            "pagans trying to make them sacrifice to the Sun Goddess.",
            "The legacy is in how Berbers sort magic: any power not of the "
            "Divine is the sun's if a man works it and the moon's if a woman "
            "does.",
            "The sun here is no nurse but a harsh mistress, the tool of "
            "hardship. Awettuf the Ant taught sun magic, so it is believed, "
            "to protect against the world's evil: an impersonal, scholarly "
            "art that turns harm aside and bends natural forces to human good, "
            "and has charge of healing, creation and summoning. Sun magicians "
            "are the imhergi (singular amherg). Sahirs and elementalists have "
            "their own name, asehhar, the Tamazight form of sahir, and count "
            "as sun magicians even when female. Berbers would call much of "
            "Hermetic magic sun magic.",
            "Moon magic is passionate and visceral, often destructive, or "
            "turning destruction to good use. Ayyur, god of the moon and of "
            "sacrifices, taught it to the settuten, priestesses of the First "
            "Mother of the World, who made the world and all the evil that "
            "plagues it.",
        ),
        rules=(
            "Berber magicians very often have the Cyclic Magic Virtue or Flaw, "
            "tied to the fitting body (p. 92). Sahirs: The Cradle and the "
            "Crescent ch. 3; elementalists: Hedge Magic Revised Edition ch. 2."
        ),
    )
    b.faction(
        "The Imhergi and Ngagef",
        realm="Magic",
        faction="Hedge coven",
        tradition="trad_imhergi",
        summary=paragraphs(
            "Most imhergi are learned tattoo magicians, much like Cunning Folk. "
            "Among Berber women the ngagef (singular neggafa) are cosmeticians "
            "who specialise in the same sun magic although they are women.",
            "They draw no spoken charms. They paint passing tattoos called "
            "tawzayt, or mark like signs on the ground or chalk them on "
            "buildings; an amherg's lasting work is a permanent tattoo, an "
            "ahadjam, or an inscription, which wakes when uncovered and fades "
            "when its charges or its time run out.",
        ),
        rules=(
            "Tradition Imhergi and Ngagef (pp. 93-94). The traditional "
            "symbols and Design & Inscription Bonuses are on p. 95; the "
            "fifteen symbols are the Beak, Lion's Paw, Fingers, Barley, "
            "Partridge Eyes, Gameboard, Frog, Seeds, Eye, Saw, Snake, Afous "
            "(the hamsa, Africa's commonest protective amulet), Sun, Moon and "
            "Ship."
        ),
    )


# -- the cult of the dead --


def _dead(b: Builder) -> None:
    b.faction(
        "The Cult of the Dead",
        realm="Magic",
        summary=paragraphs(
            "Among the Berbers the dead stay part of the living people. "
            "Elders and marabouts speak with them through dreams, and so a "
            "whole cult keeps up the tombs and reads the dreams the spirits "
            "send, asking those beyond the grave what they see coming. The "
            "dead keep the reach they had alive: a dead ruler watches over "
            "his entire people. Though it isn't strictly needed, an ancestor "
            "is best consulted in his own tomb.",
            "For this the pyramid tomb complexes hold sleeping niches called "
            "dream houses, set in a courtyard that is square but for an "
            "extension in the middle of its east side. In the larger ones, "
            "that extension holds a small copy of the main pyramid.",
        ),
        rules=(
            "Sleeping in a dream house gives +3 to Dream Interpretation "
            "rolls on the dreams had there (p. 92; the Ability is in Realms "
            "of Power: The Divine p. 137 and pp. 128-130 here)."
        ),
    )
    b.place(
        "The Tomb of Juba II",
        realm="",
        summary=(
            "The tomb of the former king of Mauretania. Dream interpreters "
            "still go there."
        ),
    )
    b.place(
        "The Royal Tombs South of Tahert",
        realm="Magic",
        aura=3,
        summary=paragraphs(
            "The largest of the dream-house tomb complexes, on two hills in "
            "Mauretania south of Tahert. Berber kings, high priests and "
            "famous ancestors lie there. The Imazighen regularly send their "
            "best dream interpreters to divine what threatens the region and "
            "the people. Many other ghosts haunt the hills too.",
        ),
    )
    tomb = b.place(
        "The Tomb of Tin Hinan",
        realm="Magic",
        aura=5,
        summary=paragraphs(
            "Tin Hinan, Queen of the Berber and mother of the Tuareg, rests at "
            "Abalessa in the Ahaggar, in Tilfilalt, ten days south of Fes. "
            "The tomb, set into the mountainside, is all that is left of her "
            "many-chambered palace on its hill. The Ahaggar matter deeply to "
            "the settuten, being the centre of the Great Desert and perhaps a "
            "haunt of Lazz, the Great Hunger.",
            "The queen lies in state on a leather-covered bed, seven gold "
            "bracelets on her right arm and eight silver on her left. The "
            "Tuareg tribes take turns at the honour of guarding the tomb and "
            "defend it fiercely from outsiders, yet they stop no settut, "
            "wherever she comes from. Those who rest in the entryway with a "
            "token of Corpus or Creo vis often rise healed.",
            "The inscriptions, for one who reads the Libyan script and "
            "language, are summae on each settut Supernatural Ability and on "
            "Divination, Level and Quality between 6 and 12 by subject (pp. "
            "92, 97). She is consulted by the Divination Ability, and "
            "necromancy on her body gives +10 on events touching the Imazighen "
            "as a whole (p. 102). The grand convocation of the settuten meets "
            "here (p. 106).",
        ),
        secrets=(
            "The healing sleep is the work of Tin Hinan's ghost; few guess "
            "their good fortune comes from her."
        ),
    )
    b.creature(
        "Tin Hinan the Shade",
        page="p. 93",
        realm="Magic",
        might=35,
        form="Mentem",
        season="Autumn",
        confidence=(1, 3),
        encumbrance="0 (0)",
        place=tomb,
        block={
            "characteristics": characteristics(2, 1, 5, 2, -2, 2, -3, 0),
            "virtues_flaws": [
                "Magic Spirit",
                "Magical Master",
                NETWORK,
                ("Extractor of {form} Vis", {"form": "Corpus"}),
                *_times(vf_great("Presence"), 2),
                "Intuition",
                VOICE,
                "Wise One",
                "Crippled",
                "Driven (Major)",
                "Magical Air",
                ("Ability Block", {"abilities": "Martial"}),
                ANCHORED,
                ("Baneful Circumstances", {"circumstance": "day"}),
                "Visions",
                *_times("Focus Power", 4),
                *_times("Ritual Power", 2),
                "Vis Mastery",
                "Improved Abilities",
                *_times("Improved Might", 5),
                "Improved Powers",
                *_times("Lesser Power", 2),
            ],
            "abilities": [
                ("Awareness", 2, "the living"),
                ("Area Lore: Western Sahara", 4, "oases"),
                ("Area Lore: Central Sahara", 4, "Tuareg Settlements"),
                ("Bargain", 2, "setting terms"),
                ("Charm", 2, "seduction"),
                ("Dead Language: Latin", 4, "commands"),
                ("Etiquette", 4, "nobles"),
                ("Faerie Lore", 5, "Jinn"),
                ("Folk Ken", 3, "discerning motivation"),
                ("Guile", 1, "concealing intent"),
                ("Intrigue", 2, "spotting conspiracy"),
                ("Leadership", 5, "maintaining alliances"),
                ("Living Language: Arabic", 4, "conversation"),
                ("Living Language: Berber", 5, "commands"),
                ("Magic Lore", 4, "Sahir powers"),
                ("Organization Lore: Tuareg Tribes", 4, "Traditions"),
                ("Penetration", 4, "Corpus"),
                ("Teaching", 4, "single student"),
            ],
            "traits": {"Driven": 3, "Reclusive": 3, "Nurturing": 2},
            "reputations": {
                "Great and Powerful leader (local)": 5,
                "Potent Sorceress (Maghreb)": 3,
            },
        },
        attacks=[b.attack("Fist", 0, 0, -3, -2)],
        soak=2,
        fatigue_levels="None",
        tires=False,
        powers=[
            b.power(
                "Donning the Corporeal Veil",
                0,
                -2,
                "Corpus",
                does="Takes on a material form (Lesser Power, -5 Might cost).",
            ),
            b.power(
                "Focus Power (Divination)",
                7,
                0,
                "Intellego",
                does="Up to 7 points: Intellego Corpus, Imaginem or Vim effects "
                "up to 7th magnitude. Its Initiative is the magnitude - 3.",
            ),
            b.power(
                "Focus Power (Destruction)",
                7,
                0,
                "Perdo",
                does="Up to 7 points: Perdo Animal, Corpus or Terram effects "
                "up to 7th magnitude. Its Initiative is the magnitude - 3.",
            ),
            b.power(
                "Invisibility",
                0,
                -1,
                "Imaginem",
                rtd=("Touch", "Conc", "Ind"),
                level=15,
                does="She, or someone she touches, turns invisible at will, "
                "though Second Sight still sees her. The effect is PeIm 15; "
                "the book also says the Lesser Power's 25 levels.",
            ),
            b.power(
                "Ritual Focus Power (Healing)",
                7,
                0,
                "Corpus",
                does="Up to 7 points: Creo Corpus ritual effects up to 7th "
                "magnitude, paid for with any fitting vis she holds. Its "
                "Initiative is (2 x magnitude) - 3.",
            ),
        ],
        vis=[BodyVis(7, "Mentem", "in her bracelets")],
        appearance=(
            "A breathtaking, raven-haired Berber woman of noble bearing, "
            "sitting cross-legged with her legs covered, in white and blue "
            "robes, her lips and eyelids blue."
        ),
        notes=paragraphs(
            "Tin Hinan rose in the Atlas, and a prophetic dream sent her "
            "across the desert on a white camel laden with millet and dates, "
            "her servant Takama with her. She found the land empty and made "
            "her seat at Abalessa, where she bore three daughters, Tinhert "
            "(antelope), Temerwelt (hare) and Tahenkot (gazelle), who founded "
            "the royal tribes of the Imazighen and Tuareg. From Takama came "
            "the servile caste.",
            "Even death did not part her from her people: her shade is bound "
            "to the desert, answers the Brides of Ayyur, and will stay as "
            "long as the tribes seek her out. Her one great aim is to help "
            "and protect the Imazighen. She crosses vast distances by night "
            "through the Magic regiones of the Great Desert, and keeps some "
            "of her old destructive powers, no longer needing amulets for them.",
            "Her Driven is to protect and perpetuate the Tuareg, printed as "
            "her first Flaw. While her body lies undisturbed she uses "
            "Extractor of Corpus Vis to draw 5 Corpus pawns a season from the "
            "aura, her tomb serving as her laboratory, and may hold up to 20 "
            "for her Ritual Focus Power.",
        ),
    )


# -- the settuten --


def _settuten(b: Builder) -> None:
    b.faction(
        "The Brides of Ayyur",
        realm="Magic",
        faction="Hedge coven",
        tradition="trad_settuten_berber",
        summary=paragraphs(
            "The settuten (singular settut) are the witches of the Berbers; "
            "any woman who works magic is called one, but the name belongs "
            "first to this tradition of sorceresses, whose poetic title, "
            "Tisliten n Ayyur, weds them to the Moon. Since the old gods "
            "declined they have kept the old religion, priestesses of every "
            "Berber god, devotees of Yemma-t n Dunnit, the First Mother of "
            "the World. Most have The Gift and must live apart from their "
            "tribes, often in an old tomb or a marabout's. The few men among "
            "them live and are treated as women in everything.",
            "A settut wears an indigo shawl stitched with moons and other "
            "signs, and blue on her lips and round her eyes; on business, "
            "whether with a client, her peers or a ceremony, she stains her "
            "forehead with yellow ochre and saffron. She does not marry, "
            "which mildly scandalises the Berbers, and takes herbs against "
            "pregnancy in imitation of her sterile goddess.",
            "They heal, set bones, keep the midwife's and apothecary's trades "
            "and teach women to read. The tala, the women's court, sometimes "
            "seeks their advice, never forgetting that their goddess gives "
            "evil counsel. Even in Muslim districts they bless births and "
            "bury the dead, and watch closely for Gifted children at these "
            "rites: a boy is usually 'cured' by a year of Disjunction, a girl "
            "may be taken as an apprentice when she is old enough. Some, "
            "mostly the unGifted, turn to prostitution as a quick road to "
            "wealth.",
            "A tribe tolerates its settut while she serves it; only the "
            "particularly pious risk angering her, and a wronged settut is a "
            "true curse. To them sahirs, the asehharen, are Arabs and blood "
            "enemies. They will band together to hunt one out of Berber "
            "lands, dismissing his spirits and disjuncting his magic before "
            "setting a war band on him, though they seldom mean to kill. "
            "With this power, it is said, they set the Umayyad summoners at "
            "war with their servile jinn.",
        ),
        decides=(
            "The tineqiqqiten (singular tineqiqqit), seeresses with the "
            "Divination Virtue, are their only leaders and call the local "
            "convocations, which meet irregularly."
        ),
        rules=paragraphs(
            "Tradition Settuten (Berber); the Settut, Dust Devil and Settut "
            "Divination Virtues (pp. 95-106). Amulets and their Potency pp. "
            "96-98, Durations and the moon p. 98, the Abilities pp. 99-103, "
            "dispelling with the jedwel pp. 103-104, the Tamzawit Curse pp. "
            "104-105. Male settut must take Gender Nonconforming (p. 96, by "
            "the errata).",
            "A local convocation swaps news and knowledge, hears divinations, "
            "reports sightings of asehharen, and votes to blacklist a person "
            "or town or lift a ban: the blacklisted get no help from any "
            "settut and are fair game for curses. Everyone Disjuncts her own "
            "Gift on arriving, the tineqiqqiten last, after they have Opened "
            "new members' Gifts and Initiated the unGifted; the stronger give "
            "amulets to those who cannot do it themselves.",
            "The grand convocation meets at the Tomb of Tin Hinan every "
            "nineteen years, when the full moon returns to Cassiopeia on the "
            "shortest day. The book leaves its date to the storyguide. All "
            "the tineqiqqiten must attend; first they divine the fortunes of "
            "the settuten together until they agree, and the strongest or "
            "fiercest usually wins, The Gift being still on them. Exotic "
            "sorceresses and now and then supernatural guests attend too.",
        ),
        offers="Healing, advice, exorcism, midwifery and the old rites.",
    )
    b.faction(
        "The Tuareg Settuten",
        realm="Magic",
        faction="Hedge coven",
        tradition="trad_settuten_tuareg",
        summary=paragraphs(
            "The Tuareg have settuten of their own. Both peoples own the same "
            "origin for their powers, but neither counts the other as of its "
            "tradition, and they rarely work together. They go by no poetic "
            "name.",
            "Usually one settut rides with each band, carrying it over the "
            "vast spaces and making lightning raids on caravans and villages; "
            "many go disguised as men in the litham veil. When bands meet "
            "they may trade their settut, and she has little say. It spares "
            "her the resentment of The Gift, for no one has time to tire of "
            "her, though it also keeps anyone from growing used to her. A "
            "wronged settut being so dangerous, she is seldom treated as a "
            "possession.",
            "Their rare seeresses are the appointed guardians of Tin Hinan's "
            "shrine at Abalessa and speak for the southern settuten.",
            "Tuareg parents have no Disjunction to quench a Gifted boy. Found "
            "early, he is raised a girl and made a settut, sold north as a "
            "slave, or left in the southern deserts for the jnun of the Kel "
            "Asouf or for death. Some of these are taken in by the Blue Men, "
            "the outcast inenden, or a wandering sahir or Hermetic magus.",
            "Some men long in the deep desert, and some Blue Men, have "
            "Dislocation by Mystery or as a gift of the spirits. They carve "
            "its amulets from cypress or metal with ancient Libyan runes, and "
            "keep it hidden from settuten and comrades for fear of being "
            "called witches.",
        ),
        rules=paragraphs(
            "Tradition Settuten (Tuareg) (p. 106): Dislocation in place of "
            "Disjunction, Dismay in place of Dissidence, a waral lizard in "
            "place of the dust-devil under the curse, Skinchanger (waral "
            "lizard) in place of Dust Devil, usually adept at Geomancy. They "
            "cannot suppress their Gift. Those who live as men may take "
            "Gender Nonconforming (pp. 105-106, by the errata). A man with "
            "Dislocation gets no magical defences unless raised a true settut "
            "(p. 105).",
            "No local convocations: bands share what they know when they "
            "meet. At the grand convocation they keep aloof, sneer, speak "
            "only to the tineqiqqiten and only in their own Tamazight, and "
            "must accept Disjunction or stay out; raiders mostly stay away, "
            "for fear of being called asehharen.",
        ),
    )


# -- minor traditions --


def _minor_traditions(b: Builder) -> None:
    b.faction(
        "The Daughters of Four Fathers",
        summary=paragraphs(
            "A small, close family of shapeshifting women who say they all "
            "descend from one mother. Four friends on a long journey, the "
            "story goes, were missing the company of women. The carpenter, "
            "on first watch, carved a perfect woman from wood; the tailor, "
            "on second, dressed her in beautiful clothes; the magician, on "
            "third, gave her life. They always stop before saying what the "
            "thief did.",
            "Each can take a dove's shape at will and sends messages by a "
            "single feather, which flies free, writes as a quill and returns. "
            "In human form each is supernaturally beautiful, wise, widely "
            "read and watchful. Children of a wildly successful thief, they "
            "were raised like the daughters of a rich merchant or minor "
            "noble. They flock together, and almost always live in groups.",
            "In the city where they are active they hide spare feather pins "
            "in places like the baths; a few swallow an engraved stone "
            "feather, which lodges in the dove's crop and comes up at need.",
        ),
        rules=(
            "Every Daughter has Skinchanger (dove) in a Major form, Feather "
            "Messenger (Minor), Wealthy and Close Family Ties (Minor), on p. "
            "107: a prepared feather, or any picture of one, serves as the "
            "cloak, her clothes and gear become feathers, and in dove form "
            "she has a common dove's statistics with +3 Soak. Some are "
            "Well-Traveled, and some chroniclers give them Venus's Blessing. "
            "Their learning leads some to think them faeries who made up "
            "their own stories."
        ),
    )
    b.faction(
        "The Inducers",
        summary=paragraphs(
            "The scholars of the Maghreb count three kinds of magician, and "
            "these are the least: they cannot change the world, only make a "
            "victim's mind believe it has changed. This is not illusion as "
            "magi know it, for no species are touched. The diamond necklace "
            "an inducer conjures is seen by the victim alone, and not even by "
            "the inducer.",
        ),
        rules=(
            "The Induction Virtue, pp. 107-108, with the box on Entrancement "
            "and Induction, p. 106."
        ),
    )
    b.faction(
        "The Potteresses",
        summary=paragraphs(
            "Several lineages of magical potteresses work in Africa; these are "
            "the weaker ones. Many keep customs over the clay: some sacrifice "
            "chickens or rice before gathering it, others will not gather on "
            "a Monday or Friday. Most press their clay over forms, and among "
            "some tribes those forms must come from men whose first wives "
            "have died. A form from a man whose wife lives will curse a "
            "potteress, and may kill her.",
            "They gather every year for sacrifices of animals or cowrie shells, "
            "for dancing and the handing down of lore, and to bring young women "
            "into adulthood, often by genital excision. There the eldest show "
            "their power: they slap the earth and water rises for the dancers "
            "to wash in, lead trees about on bridles of string, gather mounds "
            "of earth to make the dancing ground, rule the weather and breathe "
            "fire. Their magic often seems to come from the mouth, not the "
            "hands.",
        ),
        rules=(
            "Maker of Water Vessels and Maker of Textured Vessels (p. 108). "
            "Each vessel costs a Long Term Fatigue level; one without the "
            "gifts, training and blood who tries it suffers Enfeebled for "
            "life. The senior potters are an oral tradition of Elementalists "
            "(Hedge Magic Revised Edition pp. 17-33)."
        ),
    )
    b.faction(
        "The Leather-Workers",
        summary=paragraphs(
            "Leather is the male twin of the female art of pottery in Desert "
            "Africa: the same tradition in another stuff. The worker's highest "
            "calling is saddlery. Saddles often help the rider, bridles the "
            "horse's stamina and resistance to pests, halters and hobbles the "
            "groom. North African tack has far more tassels than European, "
            "and bridles often have a headband crossing above the eyes, which "
            "keeps off flies and is often enchanted to protect or strengthen "
            "horse or rider.",
        ),
        rules=(
            "The potteresses' two Virtues in leather; each Virtue covers clay "
            "or leather, not both (p. 109)."
        ),
    )
    b.faction(
        "The Rippers",
        summary=paragraphs(
            "Minor magicians, thickest round Tunis but reported as far as the "
            "Muslim settlements of Iberia and Sicily. A ripper can tear things "
            "open with his mind, but not people, so most of them work the big "
            "markets as standover men: every cloth merchant or livestock "
            "dealer pays a little, regularly, so that his cloth stays whole "
            "and his beasts keep their bellies.",
            "Rippers can pass the talent to their children. Scholars think "
            "variously that they are one bloodline, that the family knows an "
            "Initiatory Ordeal, that they are a murabit's acolytes, or that "
            "there are many kinds who each come by it differently.",
        ),
        rules="Ripper, Fabric Ripper and Leather Ripper (pp. 109-110).",
    )
    b.faction(
        "The Geomancers",
        summary=paragraphs(
            "Geomancy, ilm al-raml, the science of the sand, reads rows of "
            "seemingly random marks scratched in earth. One Muslim legend has "
            "the angel Jibril teach it to Idris before Islam. Another credits "
            "an apocryphal easterner, Tumtum al-Hindi, whose book passed "
            "through the pre-Islamic prophets to Khalaf al-Barbar of Medina, "
            "an early convert.",
            "It stays popular with the Tuareg, the half-literate Arabic and "
            "Berber hedge magicians of the Maghreb, and some Andalusian "
            "Ex-Miscellanea lines. Most magi think it cruder than astrology, "
            "and the scholarly hedge traditions look down on it.",
            "Some inenden carve cypress dice marked with its figures, and an "
            "alchemist in Syria is said to have built a many-dialled brass "
            "instrument that casts them.",
        ),
        rules=paragraphs(
            "The Geomancy Ability and its Virtues (Geomancy, Lesser Geomancy, "
            "Skilled Geomancer, Astrological Geomancy), pp. 110-112; stylus "
            "bonuses p. 111. Astrological Geomancy is unknown in Africa and "
            "Mythic Europe.",
            "Books, p. 111. Kitab al-Raml, thought a translation of Tumtum "
            "al-Hindi's book: summa, Level 4, Quality 10; poor Arabic copies "
            "and mistranslations Quality 5 to 8 are common, and occasional "
            "good Berber, Persian or Greek texts Quality 9. Experimentarius, a "
            "flawed Latin verse translation by Bernard Silvestris, in northern "
            "libraries since the 12th century: tractatus, Quality 8. A copy "
            "of its Arabic original: tractatus, Quality 9, from a Maghrebi "
            "bookseller or an Andalusian library.",
        ),
    )


# -- the inenden --


def _inenden(b: Builder) -> None:
    b.faction(
        "The Inenden",
        realm="Magic",
        faction="Hedge coven",
        tradition="trad_inenden",
        summary=paragraphs(
            "A low caste of pariah craftsmen outside the Tuareg's drum groups, "
            "speaking their own dialect of Tamazight, Tenet. They are feared "
            "as magicians belonging to neither Sun nor Moon. None has The "
            "Gift, yet many have its effect on others. Their role looks like "
            "the bouda's of Morocco, but they cannot change shape.",
            "The men work metal or carve wood, the famous Tuareg saddles among "
            "it; the women make ornate jewellery of metal and glass, with "
            "magic in it. Their superior pieces lend a small bonus to one "
            "roll and can be sold to anyone; excellent pieces, rarer, help "
            "several rolls but only the man they were made for.",
        ),
        rules=paragraphs(
            "Tradition Inenden; Inenden Crafter, Touched by (Realm), Mythic "
            "(Craft), Crafter's Eye (the catalog's Eye of Hephaestus) on pp. "
            "112-114. Outcast; many have Offensive to Animals or Magical Air. "
            "Wondrous items pp. 114-116; rare Gifted inenden p. 112.",
            "Common wondrous items of Africa (p. 114): the Ettebel of the "
            "Chief (a chief's drum, Craft Level 14), Odili of Soothing (a "
            "sorghum-wood flute that holds an animal still, 15), Saddle of the "
            "Temperate Camel (17), Jar of Potable Water (takes the salt from "
            "water, 15), Bukar of Clear Sight (a black turban, 17), Boots of "
            "the Tahr (+3 to climb, 13), and the Hyena Pelt (a mantle and hood "
            "that make the wearer a hyena until sunrise or sunset, 17; Muto "
            "Corpus (Animal) base 10, +1 Touch, +2 Sun, requisite free, by "
            "the errata).",
        ),
    )
    merin = b.magus(
        "Merin ag Gwafa",
        covenant=None,
        house="",
        age=33,
        type="companion",
        traditions=["trad_inenden"],
        summary=paragraphs(
            "A Tuareg inenden saddle-maker who wanders the Ahaggar, his pariah "
            "birth barring him from the lasting protection of any drum group, "
            "though the nobles he serves prize his work. Mortally afraid of "
            "the desert spirits, he trades much of what he makes for charms "
            "against magic, most of which do nothing. He is worn in the face, "
            "in a tattered light veil and a dirty white robe, and hung all "
            "over with small metal amulets and glass.",
            "His saddles are made for one rider and give +3 to riding or a "
            "Ride score of 8 on camels, or carry small Animal enchantments: "
            "they calm an animal, or let it go longer without water, or "
            "speed it across shifting sand.",
        ),
        secrets=(
            "Only two of his amulets do anything: a minor relic and an imerghi "
            "Vulnero Magicam charm."
        ),
    )
    b.stats(
        merin,
        {
            "characteristics": characteristics(1, 1, -2, 1, 2, 2, 2, -2),
            "size": 0,
            "apparent_age": 33,
            "decrepitude": (0, 0),
            "warping": (2, 2),
            "confidence": (1, 3),
            "virtues_flaws": [
                "Arcane Lore",
                "Gossip",
                "Herbalism",
                "Relic",
                ("Mythic {craft}", {"craft": "Saddle-Maker"}),
                vf_puissant("Craft: Woodcarver"),
                "Rapid Convalescence",
                "Outsider (Major)",
                "Poor",
                "Fear",
                "Vow (Minor)",
                "Disfigured",
                "Short Attention Span",
            ],
            "abilities": [
                ("Animal Handling", 2, "camels"),
                ("Living Language: Arabic", 2, "trade goods"),
                ("Area Lore: Ahaggar", 2, "markets"),
                ("Bargain", 3, "raw materials"),
                ("Brawl", 2, "fists"),
                ("Chirurgy", 3, "bind wounds"),
                ("Concentration", 2, "craft work"),
                ("Craft: Blacksmith", 4, "tools"),
                ("Craft: Woodcarver", 6, "saddles"),
                ("Faerie Lore", 2, "jnun"),
                ("Folk Ken", 3, "customers"),
                ("Herbalism", 3, "antidotes"),
                ("Inenden Lore", 3, "traditions"),
                ("Infernal Lore", 3, "jnun"),
                ("Magic Lore", 3, "items"),
                ("Profession: Apothecary", 2, "raw materials"),
                ("Survival", 2, "deserts"),
                ("Living Language: Tamazight", 5, "Tenet"),
                ("Teaching", 2, "wood carving"),
            ],
            "traits": {"Cowardly": 2, "Touchy": 2, "Sly": 1},
            "reputations": {"Pariah (Tuareg)": 2},
            "effects": [
                Builder.effect(
                    "Brave the Sandstorm",
                    kind="wondrous item",
                    level=25,
                    parameters="R: Personal, D: Sun, 2 uses per day",
                    notes="ReAu, Init 0, enchanted into his indigo litham veil. "
                    "It keeps sandstorms off the wearer by turning aside the "
                    "breeze that carries the dust.",
                )
            ],
            "notes": paragraphs(
                "BS&S p. 113. A Companion, balanced as a starting character, "
                "his minor craft magic aligned to Magic. Faith 1 (1), from the "
                "relic he carries. The book's Inenden social status is not in "
                "the Virtue catalog. His Disfigured (indigo skin) and Short "
                "Attention Span come of Warping from always wearing the "
                "magical veil. Fear is of the Kel Asuf; his Vow is to wear "
                "the litham always; his Herbalism acts as Medicine (Art & "
                "Academe pp. 55-56).",
                "Fist: Init -2, Attack +2, Defense -2, Damage +2. Soak +2. "
                "Fatigue OK, 0, -1, -3, -5, Unconscious. Encumbrance 0 (0).",
                "Equipment: litham veil, woodcarving and blacksmith tools, "
                "various amulets. Of those only two work: a minor relic (1 "
                "Faith point and Magic Resistance 10) and an imerghi Vulnero "
                "Magicam charm with 2 charges left, against Faerie creatures "
                "of Might under 15.",
                "To make him a Mythic Companion, choose 11 more points of "
                "Virtue, such as Geomancy, Mythic Herbalism, Leather Ripper, "
                "Premonitions or Touched by (Realm); or remake him as a "
                "Cunning-Man or Elementalist at magus level with Hedge Magic "
                "Revised Edition.",
            ),
        },
    )


# -- the Blue Men --


def _blue_men(b: Builder) -> None:
    b.faction(
        "The Blue Men of the Desert",
        realm="Magic",
        summary=paragraphs(
            "Some Tuareg of the deep desert are changed over time by its "
            "strong Magic auras and by forever wearing enchanted litham veils, "
            "until they become Magic Humans. Nominally of the great spirit "
            "called the Black, these wanderers stand guard against the worse "
            "things that rise from the deepest sands or cross where the "
            "boundaries between the mundane and the Supernatural run thin.",
            "Those fully changed are bigger and more magical than their human "
            "kin. There also seem to be lesser Blue Men, born to it in the "
            "deep desert, Magic-kin with no Might and no monstrous look.",
        ),
        rules=paragraphs(
            "The fully changed have Transformed by Magic and commonly Large or "
            "Giant Blood; built by Realms of Power: Magic ch. 4 (p. 116). "
            "Magic-kin suit grogs and companions, or an Ex Miscellanea magus, "
            "or a Mythic Companion as Spirit Votary of the Black.",
            "Inherited Virtues: Dislocation, Geomancy, Greater Immunity "
            "(Deprivation), Lesser Geomancy, Lesser Immunity (Thirst), Personal "
            "Power: Aura of Rightful Authority, Desert Regio Network, "
            "Skinchanger (waral lizard), Ways of the Desert, Voice of the "
            "Desert. Required Flaw: Vow (always wear the litham). Inherited "
            "Flaws: Anchored to the Desert, Delusion (Tuareg superiority), "
            "Disfigured (blue dyed skin), Dutybound, Feral Scent, Obsessed "
            "(camels or racial purity), Overconfident, Oversensitive "
            "(appearance), Poor Concentration, Proud, Social Handicap (poor "
            "hygiene), Short Attention Span, Wanderlust, Weak Senses (Cold "
            "Sensitivity).",
        ),
    )
    b.faction(
        "The Desiccated Men",
        realm="Magic",
        summary=paragraphs(
            "Far into the Tanezrouft, the Land of Thirst, wander the darker "
            "kin of the Blue Men. They are Tuareg who, dying of thirst and "
            "heat, were bound by a pact to the desert Daimon called the Hunger "
            "or the Red, and brought back to a semblance of life as its "
            "servants. They have lost much of their humanity. Free and proud "
            "no longer, they name themselves Ag Lazz or ibn al-Ju' to show "
            "whom they serve.",
            "Their magic runs on thirst and the drying of water; some can also "
            "command heat, raise sandstorms or call up swarms of desert "
            "creatures.",
        ),
        rules=(
            "Variants of the Drowned Men (Realms of Power: Magic pp. 96-97): "
            "Transformed Human and the Major Story Flaw Servant of the Desert "
            "(p. 115). They seem aligned to Aquam in a negative sense."
        ),
    )


# -- the shapeshifters --


def _bouda(b: Builder) -> None:
    bite = "Bite of the hybrid form: Init 0, Attack +3, Defense +1, Damage +4."
    b.creature(
        "Magical Bouda",
        page="pp. 116-118",
        realm="Magic",
        how_many="Packs led by women; rumour tells of whole villages",
        block={
            "virtues_flaws": [
                ("Personal Power", {"power": "Deceitful Tongue"}),
                ("Lesser Power", {"power": "Trembling Fear of the Predator's Gaze"}),
                "Wilderness Sense",
            ],
        },
        powers=[
            b.power(
                "Deceitful Tongue",
                0,
                3,
                "Imaginem",
                rtd=("Per", "Sun", "Ind"),
                level=3,
                does="Its Initiative is Qik + 3. Any voice of man or creature, "
                "in any language it knows, in any shape (MuIm).",
            ),
            b.power(
                "Trembling Fear of the Predator's Gaze",
                0,
                -2,
                "Mentem",
                rtd=("Eye", "Conc", "Ind"),
                level=5,
                does="Its Initiative is Qik - 2. While it holds his eye the "
                "target cannot run or dodge, though he can use his hands or "
                "call out; he loses his Quickness from Defense and takes -3 "
                "(ReCo).",
            ),
            b.power(
                "Rending Fangs",
                0,
                -3,
                "variable",
                rtd=("Touch", "Mom", "Ind"),
                level=30,
                does="A common power. Its Initiative is Qik - 3. Its bite "
                "destroys leather, bone, wood, cloth, stone or metal it can "
                "get its teeth round. With an attack it takes a point of "
                "Protection off armour, or instead of one it breaks a weapon "
                "or shield if it beats Defense by 3 or more, doing no damage; "
                "not together with Ripping Jaws (PeTe(An, He)).",
            ),
            b.power(
                "Ripping Jaws",
                0,
                -2,
                "Corpus",
                rtd=("Touch", "Mom", "Ind"),
                level=20,
                does="A common power. Its Initiative is Qik - 2. The victim "
                "takes -3 to all recovery rolls until fully healed, for any "
                "wound; Incapacitating Wounds leave scars that never fade "
                "(PeCo).",
            ),
            b.power(
                "The Beast Between",
                3,
                -2,
                "Corpus",
                rtd=("Per", "Sun", "Part"),
                level=25,
                does="A common power. 3 points or Fatigue; Initiative Qik - 2. "
                "A hyena's head, claws, fur and tail on a man's upright frame, "
                "human mental Characteristics and a hyena's physical ones, "
                f"usable hands, Protection +2. {bite} Ended early by changing "
                "shape (MuCo, free Animal requisite).",
            ),
        ],
        appearance=(
            "Often red-tinged eyes, a very hairy body, a nasal voice and "
            "foul breath. In human form it casts a hyena's shadow. Tame "
            "animals hate it and will not be touched."
        ),
        notes=paragraphs(
            "Shapeshifting hyena-men of the Maghreb and the Tell who love to "
            "prey on children, a magical kin of Animal and Corpus (Realms of "
            "Power: Magic p. 89). They live and hunt easily as men or hyenas, "
            "most changing only at night and returning at dawn; the strongest "
            "take a hybrid shape. Even as hyenas they speak with human voices, "
            "and so draw the unwary in. A pack can keep a district in constant "
            "fear for anyone outdoors, and secret lovers often fall to them.",
            "Inherited Virtues: Deceitful Tongue, Trembling Fear, Skinchanger "
            "(needing no item, hyena only and at night only), Wilderness "
            "Sense. Common Virtues: Rending Fangs, Ripping Jaws, The Beast "
            "Between. Common Flaws: Driven (terrorizing communities, Major), "
            "Dark Secret, Offensive to Animals. No Characteristics or Might "
            "are printed.",
            "Folklore's werehyena is at least Size +1 (Large), hairy and "
            "hunch-backed, its hind legs shorter than its forelegs, with "
            "glowing red eyes (p. 118). Many North African jinn, Faerie and "
            "Infernal, also take the hyena's shape and are mistaken for bouda.",
        ),
    )
    b.creature(
        "Faerie Bouda (Werehyena)",
        page="p. 117",
        realm="Faerie",
        might=15,
        size=0,
        confidence=(0, 0),
        how_many="From Morocco to the Sudan, living among the villages",
        block={
            "characteristics": characteristics(0, 2, -4, -1, 1, 2, 1, 2),
            "virtues_flaws": [
                "Crafter's Healing",
                ("Faerie Beast", {"animal": "hyena"}),
                "Faerie Speech",
                "Greater Power",
                "Improved Characteristics",
                *_times("Increased Faerie Might", 2),
                "Keen Vision",
                "Narrowly Cognizant",
                "Passes for Human",
                ("Personal Power", {"power": "Transform into Human"}),
                vf_puissant("Craft: Blacksmith"),
                "Feral Scent",
                ("Restricted Power", {"power": "Transform into Human"}),
                "Role Requires Suffering",
                "Slow Might Recovery",
                "Susceptible to Deprivation",
                "Crafty",
                "Keen Eyesight",
                "Large Teeth",
                "Mimicry",
                "Pursuit Predator",
                THICK,
            ],
            "abilities": [
                ("Athletics", 3, "running"),
                ("Awareness", 3, "food"),
                ("Brawl", 3, "bite"),
                ("Craft: Blacksmith", 4, ""),
                ("Guile", 1, "feign death"),
                ("Hunt", 4, "tracking"),
                ("Single Weapon", 2, "hammer"),
                ("Survival", 3, "desert"),
            ],
            "traits": {"Untrustworthy": 3},
        },
        attacks=[
            b.attack("Hammer", 3, 7, 5, 9),
            b.attack("Bite", 2, 9, 7, 8),
        ],
        soak=3,
        fatigue_levels=ONE_EXTRA_FATIGUE,
        powers=[
            b.power(
                "Blacksmithing",
                1,
                0,
                "Terram",
                does="Or Crafter's Healing, below. 1 point a magnitude, "
                "Initiative variable: any non-Ritual Creo, Muto, Rego or Perdo "
                "Terram spell, within its motif as a blacksmith.",
            ),
            b.power(
                "Crafter's Healing",
                0,
                0,
                "",
                does="In place of Blacksmithing, as the Major Supernatural "
                "Virtue (City & Guild p. 71).",
            ),
            b.power(
                "Looked at Thrice",
                0,
                0,
                "",
                does="As Trembling Fear of the Predator's Gaze.",
            ),
            b.power(
                "The Shadow Stays the Hound",
                0,
                0,
                "",
                does="Paralyzes a dog the werehyena's shadow falls on (Base 5, "
                "+2 Sight, +1 Conc).",
            ),
            b.power(
                "Transform into Human",
                1,
                -1,
                "Animal",
                level=20,
                does="Human form for Duration: Sun, and only at sunrise "
                "(Personal, MuAn(Co)).",
            ),
        ],
        equipment="Blacksmith tools, apron.",
        vis=[BodyVis(3, "Terram", "in its tools")],
        appearance="As a man: a disturbing smell, a nasal voice, an ugly hairy body.",
        notes=paragraphs(
            "A dark faerie that wears a human shape by day, as blacksmith, "
            "healer or wizard, and goes back to the hyena by night to rob "
            "graves. Though only narrowly cognizant it is clever, and grows "
            "Pretenses to fit the villages it secretly plagues, copying the "
            "magical bouda. Unlike most faeries it feels pain, fatigue and "
            "hunger as its neighbours do. Its Abilities are Pretenses.",
            "Built as a strong companion or weak magus, with 6 points of "
            "Virtues and 3 of Flaws unassigned. Lesser kinds lack some powers; "
            "greater ones have Entrancement, more smithing magic such as "
            "Touched by the Faerie Realm, and other mind-control or "
            "shapeshifting powers. Its block lists Crafter's Healing or Focus "
            "Power (Blacksmithing) as alternatives; Crafter's Healing stands "
            "here. A hyena's bite is Init 0, Atk +4, Def +1, Dam +3.",
            "Bouda Blood (p. 117), the Faerie Blood of its descendants: +1 to "
            "Strength or Intelligence, to no more than +3; Legacy +1, to +4; "
            "Sympathies Wastelands, Cruelty, Mimicry; other Virtues and Flaws "
            "Entrancement, Puissant Guile, Skinchanger (hyena), Disfigured, "
            "Feral Scent; hairless but for the back, hunch-backed, always "
            "red-eyed.",
        ),
    )
    b.faction(
        "The Folk Witch Bouda",
        realm="Faerie",
        faction="Hedge coven",
        tradition="trad_bouda",
        summary=paragraphs(
            "Some human bouda of Morocco claim a legendary clan or tribe, and "
            "their magic is thought to come down from their parents. They are "
            "mostly men, though their way of changing sex confuses the count, "
            "and most have The Gift. Besides ruling their hyena shape and "
            "their minds of others, they work smith's or woodcarver's magic, "
            "typically Muto Terram or Muto Herbam.",
            "As they warp they turn slowly into inhuman faerie bouda, as a "
            "gruagach turns troll.",
        ),
        rules=(
            "Tradition Bouda (folk witches), pp. 118-119: Folk Witch, Gender "
            "Shift, Theriomorph and Touched by Faerie Realm; Judged Unfairly, "
            "Short-Ranged Curses and Primitive Tradition; Sex Shift, as the "
            "book first names it, is the catalog's Gender Shift. Warping "
            "replaces the Witch's Moon. Ordeal Flaws run to the hyena's "
            "unsavoury qualities: Feral Scent, Disfigured, Hunchback, Tainted "
            "by Evil, Repellent."
        ),
    )


# -- the monstrous races --


def _race(
    b: Builder,
    name: str,
    page: str,
    entries: list[Any],
    words: str,
    *,
    powers: list[CreaturePower] | None = None,
    size: int = 0,
    secrets: str = "",
) -> None:
    """A race of Magic Humans: the rules are rules.africa's."""
    b.creature(
        name,
        page=page,
        realm="Magic",
        size=size,
        how_many="Tribes",
        block={"virtues_flaws": [*entries, "Monstrous Appearance"]},
        powers=powers,
        notes=paragraphs(
            words,
            "A Magic Human of the Plinian races: Might by the character's "
            "role, most Spring, immune to deprivation unless stated, Monstrous "
            "Appearance free, speaking its human neighbours' languages "
            "(pp. 119-120).",
        ),
        secrets=secrets,
    )


def _short_race(b: Builder, name: str, words: str) -> None:
    b.creature(
        name,
        page="p. 122",
        realm="Magic",
        how_many="Tribes",
        notes=paragraphs(words, f"One of the other monstrous races. {NO_NUMBERS}"),
    )


def _monstrous_races(b: Builder) -> None:
    age = _major_flaw("Age Quickly")
    deprived = "Susceptible to Deprivation"
    _race(
        b,
        "Anthropophagus (Man-Eater)",
        "pp. 119-120",
        [
            ("Improved Attack", {"weapon": "Bite"}),
            *_times(("Improved Damage", {"weapon": "Bite"}), 2),
            _major_flaw("Greater Malediction"),
        ],
        paragraphs(
            "A man's shape with a vast pot belly, a mouth crowded with "
            "hippopotamus tusks, small piggy eyes and sparse hair. What "
            "disgusts its neighbours, though, is the habit of eating its own "
            "dead. A member who dies by mishap is ritually consumed by friends "
            "and family, unless of a disease, and then only if it clearly "
            "touched just one organ. Drinking cups are made of the skulls of "
            "each family's most famous, and other body parts are worn. Alone "
            "of the Magic Humans they are not tolerated in human settlements, "
            "for all their protests that they want only their own.",
            "Tusks: Init 0, Attack +6, Defense +2, Damage +11.",
        ),
        secrets=paragraphs(
            "Their Greater Malediction: Magic auras do not keep off "
            "Acclimation. They must eat human flesh in a ceremony at least "
            "once a year, or lose a Magic Quality each year until they are "
            "ordinary, hideous mortals. One corpse feeds five. A family with "
            "no death to hand must make one, and those who tire of it and let "
            "themselves acclimate are usually eaten first; the last resort is "
            "the nearest human settlement.",
            "Not all are born to it. A human who shares the ceremony gains "
            "Transformed Human with the Greater Malediction. A village will "
            "sometimes spare a victim, share the secret, and send him home to "
            "get them the sacred meal each year. He gains Disfigured after five "
            "ceremonies, and after fifteen is too monstrous to stay among men.",
        ),
    )
    _race(
        b,
        "Astomus (Mouthless)",
        "pp. 120-121",
        [
            vf_minor("Enchanting Music"),
            vf_minor("Puissant Music"),
            "Personal Power",
            _minor_flaw("Fragile Constitution"),
            _minor_flaw("Warped Senses: Sensitive Smell"),
            "Reduced Fatigue",
        ],
        "The Apple-Smellers have no mouth and need neither breath, food nor "
        "drink, taking some sustenance through smell; they often carry apples. "
        "A very bad odour is said to kill them, and can certainly lay one low. "
        "Soft, silky, pale hair covers them, and they wear cloth of a soft "
        "cotton or down harvested from trees. Their voices are high and "
        "trilling, and they are superb singers. Frederick Barbarossa kept a "
        "choir of three, who soon sickened and died in the European climate.",
        powers=[
            b.power(
                "The Tongueless Voice",
                0,
                0,
                "Imaginem",
                rtd=("Per", "Sun", "Ind"),
                level=10,
                does="A constant effect, no cost. Any sound, speech, song or "
                "music comes from the head, no louder than a human could make; "
                "only suppressing the power silences it (CrIm).",
            )
        ],
    )
    _race(
        b,
        "Blemmya",
        "p. 121",
        [
            vf_minor("Puissant Bargain"),
            vf_minor("Tough"),
            _minor_flaw("Hunchback"),
            _minor_flaw("Poor Hearing"),
        ],
        "Merchants who live mostly in the deserts of Libya, with a large tribe "
        "on the upper Nile. They make little and bargain superbly, buying low "
        "and selling high, and lead camel trains on longer treks than human "
        "rivals by being immune to thirst. Their faces are on their chests, "
        "with no head or neck, the shoulders set wide and the face larger than "
        "a man's; their ears lie beneath their arms, so they hear poorly. "
        "They are hairless, go bare above the waist, and are naturally hard to "
        "hurt. Armour needs eye holes or a visor, so must be rigid, and large "
        "shields are of little use to them; their warriors tend to be mounted "
        "skirmishers with slings.",
    )
    _race(
        b,
        "Cynocephalus (Dog-Head)",
        "pp. 121-122",
        ["Gigantic", vf_minor("Sharp Ears"), age, deprived],
        "Dog-headed giants up to ten feet tall, found all along Africa's coast "
        "and commonest in Cyrenaica; some say the Canary Islands are named for "
        "ancient Dog-Heads. The Eastern Church's lore makes Saint Christopher "
        "one, born Reprobus, his fur turning white at baptism. They are "
        "covered in coarse black fur, with erect ears and long snouts full of "
        "dagger teeth, and smell exceptionally well (+3 to all rolls with "
        "scent, trails included). Many have Afflicted Tongue, though their own "
        "kind understand them. Men and women alike hunt antelope and wild goat "
        "with spears, and now and then take livestock. They eat meat raw, wear "
        "skins, and trade skins and leather for wool, pots and consumables. "
        "Most are pagan, worshipping jnun and spirits, and the Arab and Muslim "
        "dislike of dogs falls on them too.",
    )
    _race(
        b,
        "Maritimus",
        "p. 122",
        [
            *_times("Lesser Power", 2),
            vf_minor("Keen Vision"),
            vf_minor("Sense Holiness and Unholiness"),
            age,
            deprived,
        ],
        "A race with a second set of eyes above the first, keen-sighted and "
        "expert archers. One eye, it is said, looks to God to live rightly, "
        "one to the world to avoid sin, one to the Devil to flee him and one "
        "to the flesh to punish it. Nearly all have been Christian since the "
        "days of the Vandals, though not all good ones: now and then one "
        "serves as lookout on a Barbary pirate. Most live on the coasts of "
        "Mauritania, fishing and gathering shellfish.",
        powers=[
            b.power(
                "Double Sighted",
                0,
                0,
                "Imaginem",
                rtd=("Per", "Sun", "Vision"),
                level=30,
                does="A constant effect, no cost. He makes out detail at any "
                "distance as if a foot away, and judges distance to an inch or "
                "so at several miles (InIm, Personal Power x2).",
            )
        ],
    )
    _race(
        b,
        "Panotius (All-Ear)",
        "p. 122",
        [
            "Improved Abilities",
            "Improved Fatigue",
            vf_minor("Sharp Ears"),
            "Personal Power",
            age,
            deprived,
        ],
        "A timid, peaceful race, milk-white of skin, with ears that reach the "
        "ground and are looped round the arms to keep them out of the dirt. "
        "They fold them round their bodies for warmth and spread them as "
        "wings. Otherwise they look and dress like the humans about them. "
        "They grow fruit trees in secluded valleys and oases, best under high "
        "cliffs, eat no meat, work no metal, and are sought for their "
        "knowledge of legend and lore. Most have Noncombatant, and fly to a "
        "high perch from any fight.",
        powers=[
            b.power(
                "Auricular Flight",
                1,
                -2,
                "Corpus",
                rtd=("Per", "Conc", "Ind"),
                level=20,
                does="Its Initiative is Qik - 2. A short-term Fatigue level "
                "for flight as fast as a running horse. Every minute a Stamina "
                "+ Concentration roll against 6 or another Fatigue level; none "
                "when Dazed. Athletics steers (ReCo).",
            )
        ],
    )
    _race(
        b,
        "Tripithamus",
        "p. 122",
        [
            "Greater Power",
            ("{form} Resistance", {"form": "Ignem"}),
            *_times(("Improved Damage", {"weapon": "copper sword"}), 2),
            "Improved Initiative",
            "Miniature",
            age,
            _minor_flaw("Small Frame"),
        ],
        paragraphs(
            "Three spans high (27 inches), from the far south at the edge of "
            "the torrid zone; also called Pygmaei. The sun has charred their "
            "skins black, and they hold its heat and light. Instead of clothes "
            "they braid their long hair with grasses and beads. They are "
            "mostly pagan, raising shrines to fire and the sun; they grow crops "
            "and keep little cattle for milk and normal goats or ostriches to "
            "ride. Their society is matriarchal: in some tribes the men are "
            "little more than slaves, in others nearly equals. They war "
            "forever with a race of supernatural cranes who steal their grain.",
            "Warriors carry a copper sword, made by the tribe's priests, that "
            "bursts into flame when drawn and works only for a tripithamus: a "
            "short sword (ArM5 p. 176) with +3 Initiative and +6 Damage. Their "
            "Improved Damage and Initiative apply to these swords.",
        ),
        size=-3,
        powers=[
            b.power(
                "The Sun's Glance",
                0,
                0,
                "Ignem",
                rtd=("Touch", "Sun", "Ind"),
                level=15,
                does="A constant effect, no cost. The eyes shine like a lantern "
                "for five paces, without hurting sight; only closing them or a "
                "Confidence point shuts it off (CrIg; printed Greater Power, "
                "10 levels, -2 cost).",
            ),
            b.power(
                "The Sun's Breath",
                1,
                -1,
                "Ignem",
                rtd=("Touch", "Mom", "Ind"),
                level=10,
                does="Its Initiative is Qik - 1. Heats a thing no bigger than "
                "her head: metal glows red, water boils, the flammable "
                "ignites. It cools normally (CrIg).",
            ),
            b.power(
                "The Sun's Shout",
                1,
                1,
                "Ignem",
                rtd=("Voice", "Mom", "Ind"),
                level=10,
                does="Its Initiative is Qik + 1. Spits a dart of fire for +5 "
                "damage if it Penetrates (CrIg).",
            ),
        ],
    )
    _race(
        b,
        "Troglodyte (Hole-Creeper)",
        "p. 124",
        [
            _major_virtue("Greater Power"),
            *_times(vf_minor("Great Quickness"), 2),
            _major_flaw("Mute"),
            _minor_flaw("Warped Senses: Sensitive Sight"),
            _minor_flaw("Small Frame"),
        ],
        "Thin, pale cave-dwellers with tiny eyes that cannot bear bright light "
        "and huge pink ears, met when Berber clans who dig their homes broke "
        "through into caves lived in since time began. Some meetings end in "
        "harmony, the troglodytes in the depths and the Berbers near the "
        "entrance; others in a fight until one side is gone. They go naked "
        "until they meet humans, then take traded clothes or make them of "
        "pale fish skin and mangy rat pelts. None has ever been heard to make "
        "a sound. Among themselves they use touch and signs that humans do "
        "not know, and trade by simple gestures. They are very fast, as "
        "humans mostly learn when they flee the light, and they kill snakes "
        "wherever they find them.",
        powers=[
            b.power(
                "Eyes of the Bat",
                0,
                0,
                "Auram",
                rtd=("Per", "Sun", "Hearing"),
                level=30,
                does="A constant effect, no cost. Moves freely in complete "
                "darkness, as the Hermetic spell (ArM5 p. 127; InAu).",
            )
        ],
    )
    _short_race(
        b,
        "Amyctyra",
        "A lower lip that juts so far it shades them like an umbrella. They "
        "eat only raw meat and are unfriendly to outsiders.",
    )
    _short_race(
        b,
        "Androgynus (Man-Woman)",
        "Has the anatomy of both sexes, and a society that knows no gender roles.",
    )
    _short_race(
        b,
        "Artibatira",
        "Walks on all fours, with shorter legs, longer arms and a longer neck "
        "than a human, and cannot speak.",
    )
    _short_race(
        b,
        "Erythropodes (Red-Feet)",
        "Twenty-four feet tall, arms white to the shoulder, black ears, red "
        "feet, round heads and long noses. They live near the river Brixon, a "
        "tributary of the Nile.",
    )
    _short_race(
        b,
        "Gorillae",
        "Hairy humans named by Hanno the Navigator of Carthage, with six "
        "fingers on each hand and boar's teeth. In most tribes the men have "
        "tails; in some, neither sex has one.",
    )
    _short_race(
        b,
        "Hippopod (Horse-Foot)",
        "Two long toes like an ostrich's and two broad fingers like a "
        "lobster's claws. They run exceptionally fast.",
    )
    _short_race(
        b,
        "Monoculus (One-Eye)",
        "Often mistaken for a cyclops: the same single eye in the middle of "
        "the forehead, without the giant's stature.",
    )


# -- the jnun --


def _jinn(b: Builder, name: str, page: str, realm: str, words: str) -> None:
    b.creature(name, page=page, realm=realm, notes=paragraphs(words, NO_NUMBERS))


def _kel_asouf(b: Builder) -> None:
    """The Kel Asouf: pp. 123 and 126 add to the record the desert chapter
    makes, so one saga holds one of them."""
    words = paragraphs(
        "The lost tribes of the night. The northern Berbers think the Tuareg "
        "half supernatural for their strange ways, but the Tuareg have their "
        "own tales of invisible spirits in the desert's voids and dark. They "
        "fear and respect the Kel Asouf, partly for their links to eastern "
        "sahirs, and turn to amulets and charms from their tribal settuten. "
        "Gifted boys left in the south may be adopted by them.",
    )
    rules = "True jinn, which Sihr affects (p. 126); Faerie by p. 123."
    found = next((n for n in b.saga.neighbours if n.name == "The Kel Asouf"), None)
    if found is None:
        b.faction("The Kel Asouf", realm="Faerie", summary=words, rules=rules)
    else:
        found.summary = paragraphs(found.summary, words)
        found.details["rules"] = rules


def _jnun(b: Builder) -> None:
    b.faction(
        "The Jnun of Africa",
        summary=paragraphs(
            "Few supernatural beings matter more here. People think in terms "
            "of jnun, not of realms, which confuses any magus trying to learn "
            "about them. Jnun, jnoun and jinn are near enough one word in "
            "different mouths: jnun more the further west you go, jnoun in "
            "the old Carthaginian lands, jinn in Egypt and from Arab merchants "
            "of the east.",
            "Alone in the Sahara, it is said, you can hear the whispers of "
            "thousands of invisible jinn. The wild jinn are spirits of an "
            "oasis, a mountain or a stretch of desert, true genii loci of the "
            "Magic realm, and cannot go far from their land without a bargain "
            "or coercion. Others are faeries who ape the Berber, Bedouin and "
            "Tuareg peoples beside them, and others are Infernal.",
            "Tunisian and Libyan 'jinn' are harder to master than eastern ones "
            "because many of them are not jinn at all.",
        ),
        rules=(
            "Which jnun Sihr commands: rules.africa, pp. 123-125. All true "
            "jinn have the Free Virtue Jinn, nearly all Ways of the (Land) "
            "and Greater Malediction: Bound by Bargains, and Magic ones "
            "elemental powers. Multiple animal shapes, Shapeshifter sizes and "
            "hybrid shapes pp. 123-124; building them, The Cradle and the "
            "Crescent ch. 4."
        ),
    )
    _jinn(
        b,
        "Ghola (African)",
        "p. 125",
        "Faerie",
        "A large female jinni who changes shape to hide her real form, a "
        "hairy, goat-footed ogress like the teryel. A cannibal, she lures prey "
        "with soft mimicked voices. Dark faeries like the ghula of other lands "
        "(Realms of Power: Faerie p. 71). Some ghouls have the ears and feet "
        "of a donkey and the jaws of a jackal (p. 123).",
    )
    _jinn(
        b,
        "Ghul of the Siwah Necropoli",
        "p. 125",
        "Infernal",
        "A savager creature of the same name, only in the eastern necropoli "
        "of the Siwah Oasis, closer to the creatures of Egypt and the Sinai "
        "mountains: a hulking sorcerer that takes the form of a jackal, hyena "
        "or vulture. A demonic jinni like the Infernal Ghul of The Cradle and "
        "the Crescent p. 73.",
    )
    _jinn(
        b,
        "Shayatin (The Devils)",
        "p. 125",
        "Infernal",
        "Wicked invisible spirits of graveyards, ruins, thresholds and "
        "latrines, who tempt and corrupt as European demons do. They are the "
        "shaitan of the east: corrupt Infernal jinn, equal to the mazzikim, "
        "succubi, Evil Spirits and other immaterial demons of Realms of "
        "Power: The Infernal. Sihr affects them all.",
    )
    _jinn(
        b,
        "Leriah (The Jnun of the Air)",
        "p. 125",
        "Infernal",
        "Disease Spirits, demons that infect their victims through Diseased "
        "Possession. There are seven tribes, each tormenting on its own day "
        "of the week. They are not true jinn, and Sihr does not touch them.",
    )
    b.faction(
        "The Afarta",
        summary=paragraphs(
            "The winged messengers and nobles of the jnun (singular afrit), "
            "spirits of the air kin to the leriah but outranking other jnoun, "
            "as mighty as the strongest marid of the East. Many lesser afarta "
            "take the shape of long-haired winged serpents and carry messages "
            "for the sultan of the jinn under their chief, Eblis.",
            "The greater afarta are the jnun's nobility, terrible and "
            "monstrous, many-headed serpents or beast-headed giants. Many "
            "afarta possess humans, and the possessed is called a majnun, a "
            "madman. When the Order of Suleiman talks of the untamable jinn of "
            "the Maghrib and Libya, it usually means these. Only the fabled "
            "Seal of Solomon, a lost non-Hermetic artifact, is thought able to "
            "control them with ease.",
        ),
        rules=(
            "Lesser afarta are Infernal dragons (p. 125), not true jinn and "
            "unlike the eastern 'afrit despite the name: Sihr does not touch "
            "them, and sahirs cannot summon them. The greater vary in Realm, "
            "most being Magic variants of the Aerial Powers, and can lend "
            "subjects Recalcitrance (Realms of Power: The Infernal p. 42). The "
            "strongest are Magic Daimons, manifest as Aspects, not easily "
            "controlled by non-theurgical Hermetic magic. None is a true jinn."
        ),
    )
    seventh = b.place(
        "The Seventh Depth",
        realm="Faerie",
        status="Rumoured",
        summary=(
            "A vast Faerie regio off the southern Mediterranean coast, where "
            "Sidi Moussa, sultan of the jnoun of the sea, holds court."
        ),
    )
    b.faction(
        "The Baharia",
        realm="Faerie",
        place=seventh,
        ruler="Sidi Moussa",
        summary=paragraphs(
            "The jnoun al-Bahar, found only in Africa and thickest along the "
            "coasts round the Tunisian peninsula, though they are said to "
            "live in all oceans. This strictly ranked Faerie tribe looks like "
            "mermen and tritons, a man's body to the waist and a fish's below. "
            "They are blamed for storms and tempests, and superstitious "
            "locals still offer them sacrifices and rites whatever Islam "
            "teaches.",
        ),
        rules=(
            "Mermen and tritons are in Realms of Power: Faerie pp. 90-91. Not "
            "true jinn: Sihr does not touch them (p. 125), though they may "
            "share jinn's Traditional Wards, including the authority of "
            "Islam, and other magic can summon them."
        ),
    )
    _jinn(
        b,
        "Sidi Moussa",
        "p. 125",
        "Faerie",
        "Sultan of the baharia, in the Seventh Depth. He pays homage only to "
        "the Sultan al-Hut.",
    )
    _jinn(
        b,
        "The Sultan al-Hut",
        "p. 125",
        "Faerie",
        "The Lord of Fishes, a dark and powerful pre-Islamic Faerie deity at "
        "the head of a feudal court of sea creatures.",
    )
    b.faction(
        "The Awlad al-Hut",
        realm="Faerie",
        summary=paragraphs(
            "A secret brotherhood of Tunisian fishermen, drawn from those "
            "called the Ouata, who cling to totemic beliefs older than Islam "
            "in the face of the orthodoxy of Mahdia. Fishermen of the society "
            "are initiated into a non-Hermetic Mystery Cult.",
        ),
        rules=(
            "Mostly unGifted. Some leaders may have hedge magic, as Mythic "
            "Alchemists or Water Elementalists, seemingly of Faerie and not "
            "Magic (Hedge Magic Revised Edition; p. 124)."
        ),
    )
    b.faction(
        "The Siadna",
        realm="Faerie",
        summary=paragraphs(
            "The Masters Underground: the Walad al-Ahmar, sons of the Red, "
            "and the Walad al-Akhdar, sons of the Black. They live chiefly "
            "among people, invisible or as dogs, donkeys, camels, serpents, "
            "chickens, fish and above all cats, and keep secret lairs and "
            "palaces underground, playing the roles of Europe's common "
            "faeries.",
        ),
        rules=(
            "Closest of the faeries to eastern jinn: vulnerable to the "
            "traditional wards and the sahirs' binding, built as Pious jinn "
            "(The Cradle and the Crescent ch. 4; p. 126)."
        ),
    )
    _kel_asouf(b)
    b.faction(
        "Al-Maghrebi",
        realm="Faerie",
        summary=paragraphs(
            "The evil Moroccan magician runs through the Thousand Nights and "
            "One Night like a dark thread, ruining trusting youths who become "
            "wise heroes by escaping him. These Faerie wizards mostly bear "
            "non-Arabic, usually Berber, names. In some western tellings a "
            "like figure of magian birth and Persian looks takes the villain's "
            "part: these seemingly Zoroastrian faeries are the al-Majusi.",
        ),
    )


# -- the lowhush --


def _lowhush(b: Builder) -> None:
    amadagh = b.place(
        "The Amadagh",
        realm="Faerie",
        summary=paragraphs(
            "To the Berbers any wasteland, even a forested one, is an amadagh, "
            "the outskirts of the Otherworld, part underworld and land of the "
            "dead. All is reversed there: rivers run uphill, trees lift their "
            "roots into the air, and sheep are black, with black milk. It is "
            "barren by definition and full of dire things, and there the "
            "lowhush are found.",
        ),
    )
    b.faction(
        "The Lowhush",
        place=amadagh,
        summary=paragraphs(
            "Lowhush (singular lwash) is the Berber word for monsters: it "
            "covers dangerous mundane beasts, Magic spirits and monstrous "
            "faeries alike. The jnun count too, though their forms and stories "
            "owe more to Arab and Bedouin ideas than to the old Berber "
            "beliefs.",
        ),
        rules=(
            "For statistics, see the Faerie Bestiary of Realms of Power: "
            "Faerie ch. 4 and The Cradle and the Crescent ch. 4 (p. 126)."
        ),
    )
    b.creature(
        "Toaten (Ant-Folk)",
        page="p. 126",
        realm="Magic",
        might=5,
        form="Terram",
        size=-2,
        season="Spring",
        age="15 (mature)",
        how_many="Swarms",
        place=amadagh,
        block={
            "characteristics": characteristics(1, 2, -2, -1, 1, 2, 0, 3),
            "virtues_flaws": [
                "Magic Human",
                "Improved Characteristics",
                "Warrior",
                "Magical Monster",
                ANCHORED,
                "Weakness",
                _strength("Improved {characteristic}"),
                "No Fatigue",
                *_times(vf_great("Strength"), 2),
                "Lesser Power",
                "Miniature",
                "Monstrous Appearance",
                "Susceptible to Deprivation",
            ],
            "abilities": [
                ("Athletics", 2, "climbing"),
                ("Bargain", 1, "setting prices"),
                ("Brawl", 2, "fist"),
                ("Living Language: Berber", 4, "mining terms"),
                ("Profession: Miner", 3, "tunnels"),
                ("Thrown Weapon", 4, "sling"),
            ],
            "traits": {"Industrious": 3, "Toaten": 3},
            "reputations": {
                "Amazing builders (Local)": 4,
                "Strange Creatures (Local)": 3,
            },
        },
        attacks=[
            b.attack("Dodge", 3, None, 5, None),
            b.attack("Fist", 3, 3, 6, 1),
            b.attack("Sling", 0, 6, 0, 5),
        ],
        soak=2,
        tires=False,
        powers=[
            b.power(
                "Delve the Earth",
                0,
                0,
                "Terram",
                level=10,
                does="With a touch, a tunnel a pace deep. Used over and over "
                "to build warrens, and to loosen stones for the great burial "
                "mounds (PeTe; 2 mastery points on Might cost, 1 on Initiative).",
            )
        ],
        equipment=(
            "Any small thing that caught its interest, a camel-hide loincloth, "
            "and a sling wound round the waist or worn as a sash with a stone "
            "ready."
        ),
        vis=[BodyVis(1, "Terram", "in its hands")],
        appearance=(
            "Between ant and dwarf, no taller than a young child: hairless, "
            "carapace-like ochre skin, two pairs of arms ending in rough claws, "
            "large black eyes without pupils, and two jutting lower tusks "
            "for breaking stone. Almost always filthy."
        ),
        notes=paragraphs(
            "Not quite monsters, but of the Otherworld. They call themselves "
            "helpful servants of the Dii Mauri and work tirelessly in swarms, "
            "rebuilding the mountains the lowhush keep eroding. By an ancient "
            "compact they raise and keep the sacred tombs of the Berbers. "
            "Those who barter strange goods with them can hire their labour. "
            "They love fruit and wine, but drunk toaten work badly.",
            "Individuals might have one more Virtue and Flaw. Their Weakness "
            "is Fresh Fruit or Wine.",
        ),
    )

    def lwash(name: str, page: str, words: str) -> None:
        b.creature(
            name,
            page=page,
            realm="Faerie",
            place=amadagh,
            notes=paragraphs(words, f"{AMADAGH_LEADS}. {NO_NUMBERS}"),
        )

    lwash(
        "Teryel",
        "p. 127",
        "The teryelen are primeval ogresses, daughters of the Teryel, first "
        "woman and first witch of the Berber creation. Rather like the ghul "
        "of Bedouin tales, a teryel may be a night terror many times over, "
        "and sometimes a saviour of women suffering violence. The greatest "
        "wield magic like the highest Court Faeries of Europe: African Great "
        "Lezis, landholders of the wasteland and keepers of great treasures.",
    )
    lwash(
        "Aicha Bouteliss",
        "p. 127",
        "The weaker teryel: little more than a brutish female giant of the "
        "forest, hard of hearing and short-sighted.",
    )
    lwash(
        "Loundja",
        "p. 127",
        "A beautiful teryel who lingers near village wells and has a settut's powers.",
    )
    lwash(
        "Waghzen",
        "p. 127",
        "The teryel's husband, a brute; a Faerie Giant (Realms of Power: "
        "Faerie p. 98).",
    )
    lwash(
        "Sfar Lahwa",
        "p. 127",
        "The Whistling Wind, the ogress's son, a brute; a Faerie Giant.",
    )
    lwash(
        "Ajdhoun Alkubur",
        "p. 127",
        "A somber Faerie giant of the same kind, haunting cemeteries and "
        "ancient tombs.",
    )
    lwash(
        "Moumoush Aderghal",
        "p. 127",
        "A cyclopean son of the teryel, found all through the forested hills "
        "of the Tell.",
    )
    lwash(
        "Hataf Larrais",
        "p. 127",
        "The Bride Snatcher, another son of the teryel: like the glanconer "
        "(Realms of Power: Faerie pp. 74-75), but preying on young married "
        "women, somewhere between child's terror and sexual predator.",
    )
    lwash(
        "Talafsa",
        "p. 127",
        "A giant seven-headed serpent like the Greek hydra, a water spirit in "
        "the role of nereid or nymph. It usually demands a maiden each year, "
        "and brings drought unless appeased.",
    )


# -- the Divine --


def _divine(b: Builder) -> None:
    b.faction(
        "The Murabitin",
        realm="Divine",
        faction="Hedge coven",
        tradition="trad_murabitin",
        summary=paragraphs(
            "Murabitin (singular murabit), or igurramen in Tamazight, are at "
            "once scholars, dream interpreters, religious hermits and makers "
            "of protective amulets. They mostly live in zawiyas, houses built "
            "near tombs, tending a saint's shrine and honouring him by study "
            "and prayer. Above all they are the religious authority of the "
            "Berbers round them, debating Qur'an and law and settling disputes.",
            "A murabit names no price for an amulet, but he may remark how "
            "hard it was to make, and the wearer gives something fitting, "
            "goods or livestock; now and then he asks a favour or a task "
            "instead.",
            "A brotherhood, a tariqa or Path, sometimes forms round a murabit "
            "and his line. Its members, talibs or students, swear obedience "
            "to the line as heirs of its founder's divine grace, and some "
            "believe their joined faith lets murabitin heal and grant "
            "salvation. A few zawiyas stand by pre-Islamic tombs, where "
            "dream interpretation reaches the ancestors and the scraps of "
            "memory they hold; it marks the murabitin as heirs of Berber "
            "antiquity and protectors of its shrines.",
            "The art usually passes from father to son, though a likely "
            "candidate may be adopted. They seem akin to the Jewish Ba'al "
            "Shem, as neither would admit, Jews having once lived in numbers "
            "among the Maghreb's Berbers. The Order thinks them hedge "
            "wizards unworthy of membership.",
        ),
        rules=(
            "Tradition Murabitin; Mystic Tradition: Favored Abilities Blessing, "
            "Ceremony, Craft Amulet, Dream Interpretation, Understanding; "
            "Murabit, Pious and Vow. The Murabit, Talib, Craft Amulets and "
            "Dream Interpretation Virtues and both Abilities, pp. 127-130."
        ),
    )
    b.faction(
        "The Sufis of the Maghreb",
        realm="Divine",
        summary=paragraphs(
            "Sufis take the Qur'an as speaking straight to the heart, and know "
            "the Divine as a personal, all-consuming love. Their name comes "
            "from suf, the wool of their plain clothes. They hold that their "
            "way comes from the Qur'an, breaks no law of Islam, and is needed "
            "for its fulfilment. They count Mansur al-Hallaj and Junayd "
            "Baghdadi of the early 10th century as their effective founders; "
            "Abu Nasr al-Sarraj and Abu Hamid Muhammad al-Ghazali put the "
            "theory in order, and the mystic poet Ibn-Arabi of Damascus is "
            "now the most active thinker.",
            "They helped fix Islam among the Berbers. Brotherhoods reached the "
            "Maghreb in the 12th and 13th centuries, though far stronger in "
            "the Levant, and young groups are forming in Marrakech and Fes. "
            "Tariqas gather in a convent or a saint's tomb round a senior "
            "Sufi, a shaykh, or a guide, a murshid, with his muridin; most see "
            "one another as peers. A murid becomes a shaykh by receiving the "
            "khirqa, the cloak of the silsilah, the chain back to the Prophet "
            "through which wisdom flows.",
            "Often thought heretics, they are more and more seen as models of "
            "piety. Some rulers build zawiyas, khanqahs (convents) and ribats "
            "(hospices) for them, partly to keep them under watch. Many "
            "murabitin are Sufis and the ignorant mix them up, but the two "
            "traditions are distinct. The most pious, the zahids, are said to "
            "work miracles, karamas, flying, healing with a touch and "
            "conjuring food and clothing by prayer. The most learned seem to "
            "bend the world a little: they find what they need, and events "
            "fall out their way, which they call the will of God.",
            "Renowned Sufis of the Maghreb, all dead: Abu Madyan, a popular "
            "mystic from Iberia whom many Almohads feared, who died in 1198 "
            "on his way to the Caliph at Marrakesh and lies at Tlemcen, nearly "
            "its patron saint. Ali Hirzihim, whom Abu Madyan took as his "
            "spiritual leader, who spread al-Ghazali's works and taught at "
            "the Qarawiyin in Fes, taught by an uncle who was al-Ghazali's "
            "pupil, and took his khirqa from Ibn al-Arabi. Al-Dakkak of "
            "Sijilmasa, who studied beside Abu Madyan in Fes, gave him the "
            "master's khirqa, and lies outside Bab al-Gisa in Fes. Al-Ghazali, "
            "the Persian Sufi who set Sufism within mainstream Islam, to some "
            "the most important Muslim after Muhammad, who died at Tus in "
            "1111. Ibn al-Arabi of Seville, a great judge of Islamic law, who "
            "weighed the belief that knowledge comes only by purifying the "
            "soul, and died at Fes in 1143.",
        ),
        rules=paragraphs(
            "Zahids: Realms of Power: The Divine p. 116 (p. 131 here).",
            "The Khirka of Abu Madyan (p. 129): a patched grey woollen cloak, "
            "handed from master to student, radiating calm. Faith Score 5, 5 "
            "Faith Points, Divine Might 50, with the Saint powers Celestial "
            "Immunity, Grant Serenity, Resist Temptation and The Incombustible "
            "Shroud (Realms of Power: The Divine p. 88).",
            "Books, in Arabic (p. 129). Abu Madyan: Bidayat al Mouridin, Ouns "
            "al Wahid, Tahfat al Arib and his Diwan, each a Theology tractatus, "
            "Quality 9, in private libraries of the Maghreb and al-Andalus, "
            "sometimes the Levant. Ibn Masarrah: Kitab al-i'tibar, Kitab "
            "khawass al-huruf and Tawhid al-muqinin, each a Theology tractatus, "
            "Quality 10, there too, rarely the Levant; several works they "
            "cite are lost, so his system can hardly be rebuilt. Al-Ghazali: "
            "The Revival of Religious Sciences, summa, Theology: Islam, Level "
            "5, Quality 8; Incoherence of the Philosophers, The Deliverer From "
            "Error and The Jerusalem Tract, Theology tractatus, Quality 8; in "
            "the Maghreb, al-Andalus and all the eastern Muslim world.",
        ),
    )


# -- the gods of Carthage --


def _god(b: Builder, name: str, words: str, *, mask: str) -> None:
    b.creature(
        name,
        page="p. 135",
        realm="Infernal",
        notes=paragraphs(words, NO_NUMBERS),
        secrets=mask,
    )


def _carthage(b: Builder) -> None:
    mask = (
        "Only a mask. Whatever this god once was, by the fall of Carthage "
        "the whole pantheon was one demon, Ba'al Ammon."
    )
    ruins = b.place(
        "The Ruins of Carthage",
        realm="Infernal",
        summary=paragraphs(
            "Outside Tunis, on the site of the city, the Punic and Roman works "
            "are abandoned and looted for their cut stone, and little can "
            "be recognised. Carthage was utterly destroyed in 164 BC, its "
            "enemies writing all that survives of it. Tunis is what remains of "
            "its greatness.",
        ),
        secrets=paragraphs(
            "A great mass of melted bronze lies buried here, the remains of a "
            "tophet destroyed in the razing, and with it Ba'al Ammon's urns of "
            "vis-rich ash.",
            "Every Punic colony had to build a temple to Tanit and Ba'al "
            "Ammon, its shrines beside a tophet: a great bronze god or goddess "
            "with upstretched arms and a fire within. Petitioners laid bound "
            "offerings on the sloping hands to fall into the mouth and burn. "
            "The priests buried the ashes in urns dedicated to Tanit, and the "
            "demon drew on the pits as vast stores of vis.",
        ),
    )
    b.faction(
        "The Priesthood of Carthage",
        realm="Infernal",
        place=ruins,
        summary=paragraphs(
            "Long dead. The priests of Carthage drew their tradition from the "
            "Cabieri, a circle of ancient mystics and smiths with a sanctuary "
            "on Samothrace. They ranked second only to the kings and queens, "
            "bargained with the gods for a fee, carried back the gods' "
            "demands, saw that petitioners paid, and schooled the young in the "
            "faith. Later priests hid their founder's discoveries in myth and "
            "allegory so that Greeks and Romans should not steal them.",
            "That founder was Sanchuniathon, priest of Ba'al Ammon and sorcerer "
            "of Berytus, whom Plutarch thought truthful. He mastered the "
            "mysteries of Taautus of the Cabieri, the Egyptians' Thoyth and "
            "the Alexandrians' Thoth, whom the Greeks called Hermes; he "
            "studied the secret writings of Levantine Punic priests, and "
            "joined the two. Philo of Byblos put his work into Attic Greek, "
            "and no copy now survives.",
            "Their worship stood on celebration, sacrifice and serpents. They "
            "raised standing stones, stelae, carved with the gods' signs, to "
            "win favour or give thanks, most of them Tanit's, and pillars "
            "inscribed with their myths. They burned the 'first fruits' in "
            "great bronze altars, the firstborn of prominent citizens among "
            "them, though several treaties demanded it stop; as the legions "
            "broke the defenses the nobles burned 300 high-born children. "
            "Serpents they honoured as images of rejuvenation and immortality "
            "with festivals, sexual rites and sacrifice, drawn from Taautus's "
            "mysteries.",
            "They taught that their gods had been men, kings raised to godhood "
            "by ancestor worship, and that the greatest priests and kings "
            "might rise likewise. No account of how survives.",
        ),
        secrets=paragraphs(
            "The apotheosis was a lie. The gods were a single demon who enjoyed "
            "the work, granting just enough to encourage more sin and "
            "bloodshed, and charging for things it would gladly have done "
            "anyway.",
            "Their rite was a now-lost Profane Sacrifice, joining Sacrifice and "
            "Profaning the Holy (Realms of Power: The Infernal pp. 95-96): "
            "burning an offering makes a pawn of Vim vis infesta for each +2 "
            "the offering would give, 5 pawns for an innocent human.",
            "A storyguide may instead make them Faerie hedge wizards of Faerie "
            "Bargaining (p. 130; Realms of Power: Faerie p. 131), the child "
            "sacrifices giving vitality. Later they raised slave children to "
            "offer in place of their own; such faeries, finding the trick, "
            "could withdraw their protection.",
        ),
        rules=paragraphs(
            "The Priesthood's ruins have no printed aura; Tunis is described "
            "with the coasts.",
            "Serpent amulets of shed snakeskin give long life: +3 to aging "
            "rolls and Tainted with Evil while worn (p. 134). Some pillars may "
            "carry True Names, and their remnants may give Seekers insight "
            "into lost magic (p. 132).",
            "Books. Praeparatio Evangelica by Eusebius, in Latin (p. 132): "
            "summa, Area Lore: Ancient Carthage, Level 2, Quality 5, and "
            "Theology, Level 3, Quality 5, in private libraries in the Levant "
            "and Egypt and in Constantinople; it was meant to discredit "
            "paganism and became the last map to Punic magic. One copy is "
            "papyrus scrolls on iron rods capped with brass bull's heads, in "
            "a dark cedar box with brass fittings, in a fine narrow hand in a "
            "Roman dialect. Bibliotheca Historica Book III by Diodorus "
            "Siculus, in Latin (p. 130): summa, Area Lore: Ancient Carthage, "
            "Level 2, Quality 5, same libraries; it tells of the 300 children. "
            "De Superstitiones by Plutarch, in Latin (p. 130): tractatus, "
            "Area Lore: Ancient Carthage, Quality 5, in private libraries and "
            "Constantinople; on the flutes and drums that drowned the "
            "sacrifices' cries.",
        ),
    )
    b.creature(
        "Ba'al Ammon, Lord of Carthage",
        page="pp. 133-134",
        realm="Infernal",
        might=50,
        form="Vim",
        order="Prince of False Gods",
        hierarchy=9,
        confidence=(1, 3),
        place=ruins,
        block={
            "characteristics": characteristics(2, 2, 1, 2, 4, 5, 5, 4),
            "virtues_flaws": [
                ("Greater Immunity", {"hazard": "Flame and Heat"}),
                "Improved Characteristics",
                "Overconfident",
                "Vis Mastery",
            ],
            "abilities": [
                ("Bargain", 10, "setting rates for assistance"),
                ("Brawl", 4, "dodge"),
                ("Charm", 9, "first encounters"),
                ("Dead Language: Punic", 5, "giving orders"),
                ("Folk Ken", 9, "humans"),
                ("Guile", 10, "priests"),
                ("Great Weapon", 10, "great sword"),
                ("Infernal Lore", 8, "individual demons"),
                ("Intrigue", 9, "subtly spreading doctrine"),
                ("Leadership", 15, "humans"),
                ("Philosophiae", 8, "metaphysics"),
                ("Teaching", 9, "Infernal Lore"),
            ],
            "traits": {
                "Greedy": 6,
                "Proud": 6,
                "Ruthless Ambition": 6,
                "Subtle": 5,
                "Cunning": 4,
                "Deceptive": 4,
                "False God Demon": 3,
            },
            "reputations": {
                "Demon of Carthage": 9,
                "Ba'al Saturn": 4,
                "Baalzebub": 3,
            },
        },
        attacks=[
            b.attack("Fist", 4, 9, 8, 4),
            b.attack("Great Sword", 6, 21, 17, 13),
        ],
        soak=4,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Form of Fancy",
                0,
                0,
                "Corpus or Animal",
                does="Once in a body, he shifts to any human form, even with "
                "animal parts such as curling ram's horns, and dissolves them "
                "at will. A natural change: Magic Resistance does not stop "
                "physical attacks.",
            ),
            b.power(
                "Know the Places of Men",
                10,
                0,
                "Intellego",
                does="Up to 10 points, a point a magnitude: Intellego Corpus "
                "or Imaginem effects up to 10th magnitude.",
            ),
            b.power(
                "Master of Flame",
                10,
                0,
                "Ignem",
                does="Up to 10 points, a point a magnitude: Ignem effects up "
                "to 10th magnitude.",
            ),
            b.power(
                "Summon the Herd of Destruction",
                12,
                -19,
                "Mentem",
                rtd=("Arc", "Moon", "Group"),
                does="A ritual power (ReMe 15, +4 Arc, +3 Moon, +2 Group): "
                "10 ghostly war elephants who obey him, or one he names, for "
                "Moon Duration. They understand only Punic.",
            ),
            b.power(
                "Coagulation",
                5,
                -1,
                "Corpus",
                does="Takes a material form, which he may dissolve at will.",
            ),
            b.power(
                "Envisioning",
                1,
                0,
                "Mentem",
                does="1 point to appear in a sleeper's dreams, 5 for a waking "
                "dream. So he often spoke to his worshippers.",
            ),
            b.power(
                "His Master's Voice",
                0,
                1,
                "Vim",
                does="Variable: summons demons or corrupt beasts to him, 1 "
                "point for each point of their Infernal Might, so rarely used. "
                "He has no control over what comes.",
            ),
            b.power(
                "Obsession",
                1,
                -5,
                "Vim",
                does="1 to 3 points: imposes the Obsession Traits of Greed, "
                "Merciless Ambition and Pride (Realms of Power: The Infernal "
                "pp. 31-32).",
            ),
            b.power(
                "Possession",
                0,
                2,
                "Mentem",
                does="Variable: as Realms of Power: The Infernal. Might moved "
                "into a Possession Pool stays there until the possession ends. "
                "The more Might, the more he can do and the weaker the "
                "Penetration. Each portion is an independent copy of his mind "
                "using any Power its pool can pay for. He may give the host "
                "Magic Resistance equal to the Pool, or hide within and pass "
                "wards. Forcing the host, or using its powers, draws on the "
                "pool (1 point a magnitude or Ability point, or the Might the "
                "victim spent; a questionable act must beat the host's Trait "
                "on stress die + Might spent). The possession ends at pool 0. "
                "Vim spells drain the pool but must Penetrate his full Might.",
            ),
            b.power(
                "Shroud the Stench of the Pit",
                0,
                3,
                "Vim",
                does="Variable: conceals the Infernal nature of a power or "
                "aura as Magical or Faerie, or as wholly mundane, even from "
                "Sense Holiness and Unholiness, for as long as what it masks. "
                "It costs the masked Power's cost, or its magnitude if it "
                "costs no Might.",
            ),
            b.power(
                "Wealth of Nations",
                3,
                0,
                "Terram",
                does="Summons riches of intrinsic value up to 50 pounds of "
                "gold from somewhere else, a royal treasury or the purse of "
                "the man beside you, chosen to corrupt most.",
            ),
        ],
        weakness="Protected Group: people who have sacrificed to the Punic Gods that day.",
        vis=[
            BodyVis(10, "Vim", "in his curling horns"),
            BodyVis(20, "Vim", "vis infesta, carried on long stays abroad"),
        ],
        appearance=(
            "A handsome, well and fittingly dressed man or woman, curling ram's "
            "horns at the sides of his head, eyes like cinders, and always a "
            "large, vicious sword. He takes the look and sex the summoner "
            "would find most fitting. A snake always comes with him, sometimes "
            "a small garter or viper, sometimes something larger."
        ),
        notes=paragraphs(
            "Lord of the Punic pantheon and patron of Carthage, his sign the "
            "ram's spiral horns; nominally a moon god. The Egyptians linked him "
            "to Amun, the Greeks to Kronos, who fathered the Younger Titans "
            "that so intrigued the Founder Tytalus, swallowed the first "
            "Olympians, and sacrificed his son Iarbus for victory. He answered "
            "nobles' prayers in war with ghostly elephants and soldiers, and "
            "made the fiery artillery of the living burn with Hell's hunger. "
            "He survived as the Roman Ba'al Saturn. A potent necromancer and "
            "master of flame.",
            "He delights in corrupting men, in death and destruction, and in "
            "driving societies down. By Vis Mastery he spends vis as Might, "
            "and carries several rooks of it when long manifested.",
            "The book promises the ghostly war elephants' statistics 'later' "
            "and does not print them.",
        ),
        secrets=(
            "He is one demon of Hell who played every god of the Punics, and "
            "at last revealed himself to the Goetics as Baalzebub. The vast "
            "cache of vis infesta outside Tunis is his."
        ),
    )
    _god(
        b,
        "Tanit",
        "The Queen of Blood and Fire, consort and confidante of Ba'al Ammon, "
        "goddess of war, virgin mother, nurse and sign of fertility, her "
        "shrines outnumbering his; she was thought to sway him. Most stelae "
        "bear her sign, a circle on a triangle with a line across the point, "
        "not unlike an ankh, and she sometimes has a lion's head. The "
        "Egyptians tied her to Nit of war and the hunt; the Greeks saw Juno "
        "Caelestis, the African Juno.",
        mask=mask,
    )
    _god(
        b,
        "Dagon",
        "Ruler of farming and fishing and the bounty of the land, the Greeks' "
        "Zeus Arotrios. He also guarded the underwater prison of seven titans "
        "cast into the sea.",
        mask=mask,
    )
    _god(
        b,
        "Eshmun",
        "God of healing, linked with Asclepius: eighth son of Sydyk, carrying "
        "his staff of office with a snake coiled round his other arm. His "
        "brothers were the secretive Cabieri of Samothrace.",
        mask=mask,
    )
    _god(
        b,
        "Sydyk",
        "Discoverer of the uses of salt and judge of the gods, interpreting "
        "when Ba'al Ammon was absent: harsh, unforgiving, valuing righteousness "
        "over mercy. Sanchuniathon names his father as Magos, a follower of "
        "Zoroaster who rose as a foreign god.",
        mask=mask,
    )
    _god(
        b,
        "Melkart",
        "The Tyrian Heracles, patron of Tyre and Leptis Magna, god of death and "
        "rebirth, protector of his places and his most devout. A legacy of "
        "Carthage's birth as a colony of Tyre. Hannibal followed him, "
        "Septimius Severus built him a temple in Rome, and his cult spread "
        "through the Punic colonies of Iberia.",
        mask=mask,
    )


# -- the mundane bestiary --


def _beasts(b: Builder) -> None:
    b.creature(
        "Camel, Dromedary (Camelus)",
        page="p. 136",
        size=2,
        cunning=True,
        confidence=(0, 0),
        how_many="Herds",
        block={
            "characteristics": characteristics(-2, 0, -4, -5, 1, 3, 0, -2),
            "virtues_flaws": ["Herd Animal"],
            "abilities": [
                ("Athletics", 4, "running"),
                ("Awareness", 3, "predators"),
                ("Brawl", 2, "dodging"),
                ("Survival", 3, "home terrain"),
            ],
            "reputations": {"Cranky (much of Africa)": 1},
        },
        attacks=[b.attack("Kick", 0, 4, 2, 2)],
        soak=3,
        fatigue_levels=FATIGUE,
        appearance="A single-humped Arabian camel.",
        notes=paragraphs(
            "The common riding dromedary (Jamal), first given under Alexander "
            "of Jerbiton in Magi of Hermes pp. 10-11. Camels smell open water "
            "by its air-after-rain scent, go long without drinking and can "
            "walk through mild sandstorms unharmed. Splayed feet carry them "
            "faster over sand than horses and tire them less.",
            "New Qualities (errata p. 86; not in the catalog). Smell Water: "
            "smells drinkable water up to two miles off. Survive Without "
            "Water: lives up to two weeks without it.",
            "Riding camel, the mehari of the lower classes' races: add Fast "
            "Runner (+3 to running) and Improved Characteristics, Quickness "
            "+0. War camel: add Aggressive, Pack Animal and Ferocity (when "
            "ridden in battle), Brawl (hooves) 5; kick Init +0, Attack +8, "
            "Defense +5, Damage +2; it can train to attack in a Trained Group "
            "with its rider. Bactrian camel: Hardy, Long-Winded and Feral "
            "Scent, fully given in The Cradle and the Crescent p. 170.",
            "The block's wound ranges stop at Incapacitated 22+.",
        ),
    )
    b.creature(
        "Camel of Virtue",
        page="pp. 136-137",
        realm="Magic",
        might=7,
        form="Animal",
        size=3,
        season="Summer",
        cunning=True,
        confidence=(0, 0),
        block={
            "characteristics": characteristics(-2, 0, -4, -5, 3, 3, 2, -1),
            "virtues_flaws": [
                "Magic Animal",
                "Magical Champion",
                NETWORK,
                "Homing Instinct",
                "Hardy",
                "Improved Abilities",
                "Unaffected by the Gift",
                VOICE,
                ("Bound to {realm}", {"realm": "Magic"}),
                "Magical Monster",
                ("Offensive to {being}", {"being": "Animals"}),
                "Greater Power",
                _major_virtue("Ways of the Desert"),
                "Improved Fatigue",
                "Improved Powers",
                "Lesser Power",
                "Personal Power",
            ],
            "abilities": [
                ("Area Lore: Great Desert", 6, "regiones"),
                ("Athletics", 4, "running"),
                ("Animal Handling", 4, "camels"),
                ("Awareness", 3, "predators"),
                ("Brawl", 2, "dodging"),
                ("Survival", 5, "home terrain"),
            ],
            "traits": {"Camel": 3},
            "reputations": {"Noble (the Desert)": 3, "Cranky (Africa)": 1},
        },
        attacks=[b.attack("Kick", -1, 8, 3, 5)],
        soak=2,
        fatigue_levels=LONG_FATIGUE,
        powers=[
            b.power(
                "Perfect Form of the Desert Ship",
                0,
                -3,
                "Animal",
                level=15,
                does="Turns it into dromedary or Bactrian form and back, "
                "changing its Characteristics and non-magical Qualities to "
                "suit (MuAn; Base 5, +2 Sun).",
            ),
            b.power(
                "Keep the Simoon at Bay",
                1,
                -3,
                "Auram",
                rtd=("Voice", "Sun", "Group"),
                level=35,
                does="Shields the camel, its herd and any riders from the "
                "simoon, the scorching wind and sandstorm of the deep desert "
                "(ReAu).",
            ),
            b.power(
                "Scent the Distant Waters of the Oasis",
                1,
                -3,
                "Aquam",
                level=20,
                does="Finds any natural water on the path it is travelling, by "
                "simple Perception rolls against 6, once a day on long "
                "journeys; invoked again if the water is more than half a day "
                "off (InAq; Base 2, +2 Road, +2 Smell, +2 Sun).",
            ),
            b.power(
                "Subtle Taste of Poison and Purity",
                0,
                -2,
                "Aquam",
                level=5,
                does="As the spell (ArM5 p. 122); poison does not harm it, a "
                "Magical Animal, so it tastes fouled water safely (InAq).",
            ),
        ],
        appearance="A huge white dromedary or Bactrian camel of noble bearing.",
        notes=paragraphs(
            "A rare master of the sands, wandering from desert to desert at the "
            "head of tribes of wild camels by way of a great Desert Regio "
            "Network linking the dry lands it calls home.",
            "Unlike most Beasts of Virtue it lacks Susceptible to Deprivation "
            "and is immune to thirst, starvation or fatigue. Voice of the Land "
            "is entered as of the Desert. Camel is its Essential Trait.",
        ),
    )
    b.creature(
        "Dog, Painted (Lycaon)",
        page="p. 137",
        size=-1,
        cunning=True,
        confidence=(0, 0),
        how_many="Packs of one sex, up to 30",
        block={
            "characteristics": characteristics(0, 0, -2, -4, -3, 2, 3, 2),
            "virtues_flaws": [
                *_times("Improved Characteristics", 2),
                vf_puissant("Brawl"),
                "Sharp Ears",
                "Infamous",
                "Pack Mentality",
                "Fast Runner",
                "Pack Animal",
                "Pack/Herd Leader",
                "Pursuit Predator",
                "Tireless",
            ],
            "abilities": [
                ("Athletics", 5, "distance running"),
                ("Awareness", 3, "smell"),
                ("Brawl", 3, "teeth"),
                ("Hunt", 4, "pursuit"),
                ("Survival", 3, "desert"),
            ],
            "traits": {"Brave": 3, "Social": 3},
            "reputations": {"Bloodthirsty (local)": 4},
        },
        attacks=[
            b.attack("Dodge", 2, None, 7, None),
            b.attack("Bite", 2, 12, 9, 1),
        ],
        soak=2,
        fatigue_levels=LONG_FATIGUE,
        appearance=(
            "A large, lean canine with long legs and oversized round ears "
            "standing up like a wolf's. Its short mottled fur of red, black, "
            "brown, white and yellow looks painted. Its cry is more a bird's "
            "chirp than a bark."
        ),
        notes=paragraphs(
            "The kalb, far more social than the small northern jackal. Packs "
            "often range near the Tuareg's desert strongholds, preying on "
            "their goats, sheep and camels, and run down gazelles and other "
            "antelope on the plains. Its habit of disembowelling prey earns "
            "its name as a killer.",
            "Its Strength is misprinted; -3 is what its bite's Damage +1 "
            "requires (teeth +1, Crushing Jaws +3). Crushing Jaws (p. 139) is "
            "not in the catalog: +3 Damage to any bite, already in the block; "
            "a Grapple can hold the jaws shut. Natural weapon: teeth Init 0, "
            "Atk +3, Def +1, Dam +1. Puissant Brawl +2 is in the block. All "
            "get +3 to running and can pursue prey long and far.",
            "Bjornaer heartbeast: choleric with a melancholic aspect.",
        ),
    )
    b.creature(
        "Fox",
        page="p. 138",
        size=-4,
        cunning=True,
        confidence=(0, 0),
        block={
            "characteristics": characteristics(1, 0, -2, -5, -6, -1, 2, 6),
            "virtues_flaws": [
                "Perfect Balance",
                "Nocturnal",
                "Ambush Predator",
                "Crafty",
                "Good Jumper",
                "Hardy",
                "Sharp Ears",
            ],
            "abilities": [
                ("Athletics", 4, "running"),
                ("Awareness", 3, "food"),
                ("Brawl", 3, "bite"),
                ("Hunt", 4, "prey"),
                ("Stealth", 4, "stalking prey"),
                ("Survival", 4, "desert"),
            ],
            "traits": {"Sly": 3},
            "reputations": {"Wily (local)": 3},
        },
        attacks=[
            b.attack("Dodge", 6, None, 8, None),
            b.attack("Bite", 6, 9, 10, -5),
        ],
        soak=-1,
        fatigue_levels=ONE_EXTRA_FATIGUE,
        appearance=(
            "Much smaller and slighter than a wolf, long in the body with a "
            "narrow head and short limbs; sandy fur and very large ears."
        ),
        notes=paragraphs(
            "The tha'lab, smaller in Africa than in Europe and no less sly. "
            "Arabic stories like those of Reynard call the fox Abu Hassan or "
            "Abu Suleiman. All foxes get +3 to jumping. Natural weapon: teeth "
            "Init 0, Atk +3, Def +1, Dam +1.",
            "The tiny fanak (fennec, Size -5, about 3 pounds) lives all over "
            "Mythic Africa and the Middle East. A larger, redder sand fox "
            "(Size -3) lives only in 'Uman: wounds adjust, combat is the same.",
            "Cleverer foxes: Crafty x2 (Cun +3) and Guile 3 (animals). Vafer "
            "the Magical Fox and Felix the Lucky Fox are in Tales of Mythic "
            "Europe p. 14 and Magi of Hermes p. 123, a Fox of Virtue in Realms "
            "of Power: Magic p. 67. Faerie and Infernal foxes are known too.",
            "Bjornaer heartbeast: choleric with a sanguine aspect.",
        ),
    )
    b.creature(
        "Goat (Capra)",
        page="p. 138",
        size=-1,
        cunning=True,
        how_many="Herds",
        block={
            "characteristics": characteristics(-1, 1, -4, -5, 0, 1, 2, 1),
            "virtues_flaws": [
                "Long-Winded",
                "Perfect Balance",
                "Lecherous (Minor)",
                "Aggressive",
                "Extra Natural Weapons",
                "Hardy",
                "Herd Animal",
                "Keen Eyesight",
                "Skilled Climber",
            ],
            "abilities": [
                ("Athletics", 4, "running"),
                ("Awareness", 3, "predators"),
                ("Brawl", 5, "horns"),
                ("Survival", 5, "hills"),
            ],
            "traits": {"Lustful": 1},
            "reputations": {"Lecherous (local)": 2},
        },
        attacks=[
            b.attack("Horns", 2, 11, 6, 2),
            b.attack("Hooves", 3, 9, 8, 1),
        ],
        soak=1,
        fatigue_levels=ONE_EXTRA_FATIGUE,
        appearance=(
            "A small wild she-goat ('anaza) such as an Arabian tahr, with short "
            "knobbly horns; males of many breeds carry larger ones."
        ),
        notes=paragraphs(
            "The ma'ez. Valued for meat, milk and hairy hides, and moved "
            "between coast and mountain pasture through the year, above all in "
            "Provence and the Maghreb. Christian tales show the Devil as a "
            "black goat over a coven, folklore turns hedge magicians into "
            "goats, and moralists call them lechers for the rut.",
            "The book's first Ability has lost its name; Athletics is entered, "
            "as every other beast's first is. Natural weapons: horns Init +1, "
            "Atk +3, Def -1, Dam +2; hooves Init +2, Atk +2, Def +2, Dam +1. "
            "All goats and sheep get +3 to climbing.",
            "Male goat (hircus): can be larger (Size 0, Strength +2, Quickness "
            "0), Lustful +3, Ferocity (romantic rival). Larger breeds to Size "
            "+1, the mouflon, the Levant's ibex, Morocco's Barbary sheep: large "
            "horns Init +2, Atk +3, Def +2, Dam +3.",
            "Sheep, wild ewe (ovis): Peaceful +3, Obedient +3, no Aggressive "
            "or Extra Natural Weapons, Cunning -1 lower, Brawl (dodge) 2, "
            "usually Size -2 (Strength 2 lower, Quickness +2), not all horned. "
            "Wild ram (aries): as a male goat with Virile +3, Violent +2. "
            "Domestic goats and sheep have no Survival and Communication -4.",
            "Bjornaer heartbeast: wild goat melancholic; wild sheep melancholic "
            "with a choleric aspect.",
        ),
    )
    b.creature(
        "Hyena (Yena)",
        page="p. 139",
        size=-1,
        cunning=True,
        confidence=(0, 0),
        block={
            "characteristics": characteristics(1, 2, -4, -1, -1, 2, 1, 2),
            "virtues_flaws": [
                "Improved Characteristics",
                "Keen Vision",
                vf_puissant("Guile"),
                "Social Handicap",
                "Nocturnal",
                "Crafty",
                "Keen Eyesight",
                "Large Teeth",
                "Mimicry",
                "Pursuit Predator",
                THICK,
            ],
            "abilities": [
                ("Athletics", 3, "running"),
                ("Awareness", 3, "food"),
                ("Brawl", 3, "bite"),
                ("Guile", 1, "feign dead"),
                ("Hunt", 4, "tracking"),
                ("Survival", 3, "desert"),
            ],
            "traits": {"Cowardly": 3, "Sly": 2},
            "reputations": {"Treacherous": 2},
        },
        attacks=[
            b.attack("Bite", 2, 9, 7, 5),
            b.attack("Dodge", 2, None, 5, None),
        ],
        soak=3,
        fatigue_levels=ONE_EXTRA_FATIGUE,
        appearance=(
            "The commoner striped hyena: a massive torso on short hind legs, "
            "so the back slopes down, and a large short-muzzled head on a long, "
            "thick, stiff neck."
        ),
        notes=paragraphs(
            "The dhubba, found through the Levant, North Africa, Iraq, Persia "
            "and beyond. Striped hyenas tame and train like dogs, even joining "
            "a pack if raised with hounds; the Egyptians used them to hunt "
            "desert game. Greater African ones (Size +1) are ridden by jinn or "
            "witches, and ghuls often take the shape.",
            "Its Social Handicap is an unpleasant odor. Crushing Jaws (p. 139), "
            "not in the catalog, adds +3 Damage to any bite and is in the "
            "block; a Grapple can hold the jaws shut. Natural weapon: bite "
            "Init 0, Atk +4, Def +1, Dam +3 (+6 with the Quality).",
        ),
    )
    b.creature(
        "Crocotta (Hyena of Virtue)",
        page="p. 139",
        realm="Magic",
        notes=paragraphs(
            "The crocotta or kynolykos (dog-wolf) of Ethiopia, thought the "
            "offspring of hyena and lion. These spotted hyenas seem to shift "
            "sex readily. They are bigger, stronger, faster and fiercer than "
            "the mundane kind, with real wits and a human-like cackle that "
            "tricks prey.",
            "Changes from the hyena, as a template: at least Size +1, Str +4, "
            "Qik +3, Int +2, Tough Hide, Aggressive; Improved Characteristics, "
            "Tough, Tainted by Evil, Gender Shift; Brawl 5; Fierce +3 in place "
            "of Cowardly; mimicry equal to Arabic 3; all have Greater Immunity: "
            "Steel; many have Entrancement. Some strike dogs dumb with their "
            "shadow, or paralyze a creature they look at thrice.",
            "A stone in its body, worn on the upper arm, wards against faeries "
            "of the desert or grants Premonitions or Visions; some cultures "
            "say the same of its eyes. By Persian sources a charm of its "
            "genitalia and anus gives Venus's Blessing. No full block is "
            "printed and its Might is not given.",
        ),
    )
    b.creature(
        "Jackal (Thos)",
        page="p. 140",
        size=-2,
        cunning=True,
        confidence=(0, 0),
        block={
            "characteristics": characteristics(0, 0, -2, -4, -3, 2, 3, 3),
            "virtues_flaws": [
                *_times("Improved Characteristics", 2),
                "Long-Winded",
                "Sharp Ears",
                "Fast Runner",
                "Keen Sense of Smell",
                "Pursuit Predator",
                "Tireless",
            ],
            "abilities": [
                ("Athletics", 5, "distance running"),
                ("Awareness", 3, "smell"),
                ("Brawl", 3, "teeth"),
                ("Hunt", 4, "track by smell"),
                ("Survival", 3, "desert"),
            ],
            "traits": {"Friendly": 3},
            "reputations": {"Scavenger (local)": 4},
        },
        attacks=[
            b.attack("Dodge", 3, None, 6, None),
            b.attack("Bite", 3, 10, 8, -2),
        ],
        soak=2,
        fatigue_levels=LONG_FATIGUE,
        appearance=(
            "Smaller and shorter-legged than a wolf, slight, long in the body "
            "and short in the tail; mostly reddish-yellow, some marked black "
            "or grey."
        ),
        notes=paragraphs(
            "The wawi or ibn 'awa, no pack animal: it hunts alone or in mated "
            "pairs or scavenges at the edge of settlements. Friendlier to man "
            "than the wolf, it can be tamed and trained as a guard, not for "
            "hunting. Black jackals are signs of Anubis, and a favoured shape "
            "of Faerie and Infernal jinn, especially ghuls, for their habit "
            "of lurking near graves.",
            "All get +3 to running and can pursue prey long and far. Natural "
            "weapon: teeth Init 0, Atk +3, Def +1, Dam +1.",
        ),
    )
    b.creature(
        "Set Animal",
        page="p. 140",
        notes=paragraphs(
            "The sha or sal'awa, a Typhonic beast of the easternmost deserts "
            "and Egypt: a jackal's body, a donkey's ears, a long curved snout "
            "and an upright forked tail. Tied to the dark Egyptian god Set, "
            "equated with Typhon, it foretells misfortune.",
            "Almost surely magical, and a unique familiar for a magus who can "
            "find and befriend one, though its loyalty to a being of "
            "destruction may give pause. It may instead be a dark Faerie "
            "hound, a hedge magician's monstrous form, or an Infernal beast "
            "trying to trap a magus into serving its forgotten master.",
            f"{NO_NUMBERS} Its realm is left to the storyguide.",
        ),
    )
    b.creature(
        "Lizard, Waral (Varanus)",
        page="p. 140",
        size=2,
        cunning=True,
        confidence=(1, 3),
        block={
            "characteristics": characteristics(1, 0, -6, -6, 5, 2, 2, -1),
            "virtues_flaws": [
                "Ferocity",
                ("Greater Immunity", {"hazard": "Poison"}),
                "Tough",
                "Depressed",
                "Poor Eyesight",
                "Aggressive",
                "Crafty",
                "Grapple",
                "Hardy",
                "Loathsome Appearance",
                "Keen Sense of Smell",
                THICK,
                "Tough Hide",
                "Venomous",
            ],
            "abilities": [
                ("Athletics", 3, "running"),
                ("Awareness", 3, "food"),
                ("Brawl", 5, "bite"),
                ("Survival", 5, "desert"),
            ],
            "traits": {"Languid": 2},
            "reputations": {"Dangerous (local)": 2},
        },
        attacks=[
            b.attack("Bite", -1, 11, 6, 9),
            b.attack("Grapple", -1, 7, 4, None),
        ],
        soak=8,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Venomous Bite",
                0,
                0,
                "",
                does="If its Attack Advantage beats the victim's armour "
                "Protection (not Soak), he suffers an exceptionally debilitating "
                "poison, Stamina against 12 or Incapacitating, whether or not "
                "the bite wounds. Boots do not stop it, and it serves well on "
                "a victim held in its locking bite.",
            )
        ],
        appearance=(
            "A large grey lizard, some over 8 feet long like this one, size "
            "and colour varying with habitat. It lashes its tail when roused. "
            "Slow of gait, its powerful jaws snap shut fast to lock on prey."
        ),
        notes=paragraphs(
            "The waran. Tuareg myth makes these desert lizards ancestors of "
            "the tribes, and to harm, kill or eat one is taboo. Other desert "
            "peoples think them sinister. They shelter in rock clefts and bask "
            "on flat outcrops throughout the desert.",
            "Cunning, Communication, Soak and Survival follow the errata (p. "
            "86). Presence is -6, or +3 for Loathsome Appearance. Ferocity "
            "defends food or a fresh kill, with Confidence 1 (3) in that only. "
            "The Bite's Damage includes +3 from Crushing Jaws (p. 139), which "
            "its Qualities do not list and the catalog does not hold.",
        ),
    )
    b.creature(
        "Ostrich (Struthio)",
        page="pp. 140-141",
        size=1,
        cunning=True,
        confidence=(0, 0),
        how_many="Great flocks",
        block={
            "characteristics": characteristics(-2, 2, -1, -2, 2, 2, 2, 3),
            "virtues_flaws": [
                "Improved Characteristics",
                "Keen Vision",
                "Perfect Balance",
                "Sharp Ears",
                "Fragile Constitution",
                "Camouflage",
                "Defensive Fighter",
                "Fast Runner",
                "Hardy",
                "Herd Animal",
                "Keen Eyesight",
                THICK,
            ],
            "abilities": [
                ("Athletics", 3, "running"),
                ("Awareness", 4, "predators"),
                ("Brawl", 4, "dodging"),
                ("Survival", 5, "home terrain"),
            ],
        },
        attacks=[
            b.attack("Dodge", 3, None, 8, None),
            b.attack("Kick (as hoof)", 5, 8, 7, 3),
        ],
        soak=3,
        fatigue_levels=FATIGUE,
        appearance=(
            "A large bird with a long neck and legs and huge eyes. Males are "
            "typically black with white tail plumes, females a discreet grey."
        ),
        notes=paragraphs(
            "The na'aam, scattered over northern Africa and commonest in Egypt; "
            "a slightly smaller kind ranges northern Arabia and the Levant. "
            "Prized for feathers and leather, less for meat, they roam the "
            "semi-arid plains in great flocks and avoid the deep desert. "
            "Hunting them is a favourite sport of nobles and rich sahirs. They "
            "cannot fly or glide, but run as fast as a gazelle (+3 to running, "
            "like horses).",
            "Natural weapon: kick Init +2, Atk +2, Def +2, Dam +1. Thick "
            "Feathers is the catalog's Thick Fur/Thick Scales.",
            "Some evil jinn keep bigger birds as mounts in place of horses, or "
            "trade them to nobles and sahirs who like an exotic mount: Size +2 "
            "or more, perhaps Great or Mythic Quickness, Perfect Balance and "
            "Unaffected by the Gift. Some jnun tribes have bred Faerie flocks "
            "with powers of travel and distance.",
        ),
    )
    b.creature(
        "Scorpion, Monstrous (Scorpio)",
        page="p. 141",
        size=-5,
        cunning=True,
        confidence=(0, 0),
        block={
            "characteristics": characteristics(-2, -2, -5, -6, -10, 2, 2, 6),
            "virtues_flaws": [
                "Lightning Reflexes",
                "Infamous",
                "Aggressive",
                "Ambush Predator",
                "Extra Natural Weapons",
                "Grapple",
                "Tough Hide",
                "Venomous",
            ],
            "abilities": [
                ("Athletics", 3, "running"),
                ("Awareness", 3, "food"),
                ("Brawl", 5, "sting"),
                ("Hunt", 4, "rodents"),
                ("Stealth", 4, "ambush"),
                ("Survival", 3, "desert"),
            ],
            "traits": {"Fierce": 3},
            "reputations": {"Deadly (local)": 5},
        },
        attacks=[
            b.attack("Pincers", 6, 10, 14, -6),
            b.attack("Grapple", 6, 7, 11, None),
            b.attack("Sting", 10, 10, 6, -9),
        ],
        soak=4,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Venomous Sting",
                0,
                0,
                "",
                does="If its Attack Advantage beats the victim's armour "
                "Protection (not Soak), he suffers an exceptionally debilitating "
                "poison, Stamina against 6 or Incapacitating, whether or not "
                "the sting wounds. High leather boots and other simple "
                "measures hinder it.",
            )
        ],
        appearance="A black creature with oversized pincers and an arched, barbed tail.",
        notes=paragraphs(
            "Al 'Aqrab, a favoured shape of evil jinn. This is the 'giant' "
            "black scorpion of the Arabian deserts, the size of a small "
            "rabbit; most are Size -8 or smaller. The book's Sting Damage has "
            "an asterisk with no note. Natural weapons: pincers Init +0, Atk "
            "+3, Def +3, Dam +4; sting Init +4, Atk +2, Def -6, Dam +1.",
            "The lighter ones are worse, for stronger venom (at least 12, "
            "Fatal), and blending with the sand: add Camouflage, drop "
            "Aggressive, Brawl 3. Venom ranges from a Medium wound to Fatal, "
            "and even small ones may reach 15.",
            "Larger kinds are rumoured in the deep desert: Size +3 or more "
            "guarding old tombs and sand-choked ruins in Egypt. Stories tell of "
            "winged Mesopotamian scorpion-men, scorpion-human centaurs "
            "guarding temples of old gods, and winged scorpions in Egypt and "
            "India.",
            "Swarms (Legends of Hermes p. 44): attack with +10 damage "
            "automatically each round, Soaked normally. A normal scorpion's "
            "sting is painful and rarely fatal; the allergy that makes it "
            "fatal may be a Minor Flaw in Africa. A jinni taking the form of "
            "a swarm would suit.",
        ),
    )
    b.creature(
        "Unicorn, Eastern (Monoceros)",
        page="p. 142",
        size=4,
        cunning=True,
        confidence=(1, 3),
        block={
            "characteristics": characteristics(-1, 0, -4, -5, 8, 1, 0, -1),
            "virtues_flaws": [
                "Ferocity",
                "Improved Characteristics",
                vf_puissant("Brawl"),
                "Tough",
                "Oversensitive",
                "Weakness",
                "Aggressive",
                "Defensive Fighter",
                "Extra Natural Weapons",
                "Hardy",
                *_times("Imposing Appearance", 3),
                "Large Horns/Antlers",
                "Shell",
                THICK,
                "Tough Hide",
            ],
            "abilities": [
                ("Athletics", 3, "running"),
                ("Awareness", 3, "opponents"),
                ("Brawl", 5, "horn"),
                ("Survival", 5, "plains"),
            ],
            "traits": {"Belligerent": 2, "Intolerant": 3},
        },
        attacks=[
            b.attack("Horn", 1, 11, 9, 11),
            b.attack("Trample", 1, 9, 8, 9),
        ],
        soak=11,
        fatigue_levels="OK, 0/0, -1/-1, -3, -5, Unconscious",
        powers=[
            b.power(
                "Charge of the Karkadann",
                0,
                0,
                "",
                does="A natural power. It spends a Fatigue level to charge over "
                "flat ground with its horn, adding its Combat Ability to its "
                "Attack roll; anything smaller it strikes is knocked prone "
                "(Lords of Men p. 123).",
            )
        ],
        appearance=(
            "A large grey beast with a thick armoured hide and a bull's body. "
            "A large conical horn juts from the nose and curves back above a "
            "finger-shaped lip."
        ),
        notes=paragraphs(
            "The karkadann, the Lord of the Desert, of the Persian deserts and "
            "the plains of North Africa, nothing like Europe's romantic beast. "
            "Famous for charging elephants in the belly and skewering them. A "
            "virgin's care soothes it, but its horn is no antidote to poison.",
            "It has -3 to fast or nimble movement, melee included, charging "
            "excepted. Weakness is maidens; Oversensitive, threats; Ferocity, "
            "defending territory. Its Thick Skin is the catalog's Thick "
            "Fur/Thick Scales. Natural weapons: Large Horn Init +2, Atk +3, "
            "Def +2, Dam +3; trample Init +2, Atk +2, Def +2, Dam +1. Puissant "
            "Brawl +2 is in the block. Wounds as printed: -1 (1-9), -3 (10-18), "
            "-5 (19-26), Incapacitated (27-34), Dead (35+).",
            "Bigger ones (Size +5) and Faerie kinds live on the southern plains "
            "and foothills at the desert's edge, and the fabled Eastern "
            "Unicorn of Virtue is said to dwell in Ethiopia. Folklore tells "
            "of jinn with its head guarding the ways to Jinnistan and marching "
            "in the armies of Suleiman and Balquis. Too large for a Bjornaer "
            "heartbeast unless the magus has Giant Blood and a good story.",
        ),
    )
    b.creature(
        "Vulture, Egyptian (Vultor)",
        page="p. 143",
        size=-4,
        cunning=True,
        confidence=(0, 0),
        block={
            "characteristics": characteristics(0, 4, -6, -2, -4, 3, 1, 4),
            "virtues_flaws": [
                ("Lesser Immunity", {"hazard": "Rotten Meat"}),
                "Long-Winded",
                "Feral Scent",
                "Infamous",
                "Accomplished Flyer",
                "Extra Natural Weapons",
                "Keen Sense of Smell",
                "Loathsome Appearance",
            ],
            "abilities": [
                ("Athletics", 5, "swift flight"),
                ("Awareness", 4, "spotting corpses"),
                ("Brawl", 2, "talons"),
                ("Survival", 3, "deserts or mountains"),
                ("Thrown Weapon", 2, "rock"),
            ],
            "traits": {"Morbid": 2, "Patient": 1},
            "reputations": {"Omen of impending death (local)": 2},
        },
        attacks=[
            b.attack("Talons", 3, 6, 10, -4),
            b.attack("Beak", 4, 6, 7, -3),
            b.attack("Stone (dropped)", 4, -1, 0, None),
            b.attack("Stone (bludgeon)", 4, 0, 6, -2),
        ],
        soak=3,
        fatigue_levels=FATIGUE,
        appearance=(
            "A large ugly raptor with a bald head and bright orange face, white "
            "plumage and black-tipped wings, often fouled with blood and "
            "carrion."
        ),
        notes=paragraphs(
            "The nasr, found all through the Levant, the Mythic Middle East "
            "and North Africa, called the Pharaoh's Chicken for its place in "
            "royal Egyptian carvings. Anciently tied to Isis, Mut and Nekhbet, "
            "and the sign of Upper Egypt, its wings spread over the pharaoh. "
            "Vultures are clever, breaking eggs with rocks and dropping stones "
            "on prey; the Greeks said one killed Aeschylus, taking his bald "
            "head for a tortoise.",
            "Presence is -6, or +3 for Loathsome Appearance. The dropped stone has "
            "no Defense (n/a in the book). It counts as No "
            "Hands, -5 with stones. A half-fist stone does +3 and +1 for every "
            "two feet dropped (ArM5 p. 181), Range 10. Natural weapons: talons "
            "Init -1, Atk +2, Def +3, Dam +2; beak Init 0, Atk +3, Def +1, Dam "
            "+1; dropped stone Init 0, Atk +1, Def 0. By Pliny, +3 to smell "
            "rolls and +2 to Hunt.",
            "Larger vultures to Size -1, slower and fiercer: Aggressive, "
            "Cunning +1, Brawl (talons) 5; they attack flamingoes and smaller "
            "creatures. Those nesting in Magic auras on remote crags warp to "
            "brilliant colours; some have Premonitions or Visions, and old "
            "females may have Divination (The Mysteries Revised Edition pp. "
            "58-62) with Divination 4 (death), +3 to Ceremonial Augury for "
            "misfortune and +5 for death. It is a common form of ghuls and "
            "Infernal hedge wizards.",
            "Bjornaer heartbeast: sanguine with a choleric aspect, almost "
            "always female.",
        ),
    )
    b.creature(
        "Vulture of Virtue",
        page="p. 143",
        realm="Magic",
        appearance="A giant black vulture of the highest mountains.",
        notes=paragraphs(
            "They personify intimidation, patience and prudence. Every one the "
            "magi have identified was female, and most are thought to live a "
            "hundred years. Many classical authorities deny there are male "
            "vultures, saying females bear identical daughters without a mate, "
            "an allegory the Church uses for the Virgin birth.",
            "The skin of the bald head holds Corpus, not Animal, vis; the "
            "amount is not printed. At least one elder Bjornaer with a vulture "
            "Heartbeast has lately passed into Final Twilight as one of these, "
            "and nobody knows what a male would become.",
            NO_NUMBERS,
        ),
    )


# -- stories --


def _stories(b: Builder) -> None:
    dormant(
        b.threat(
            "The Broken Gift",
            antagonist="A cadre of veiled settuten",
            summary=(
                "A boy meant to be a magus's apprentice is carried off by "
                "veiled women to be subjected to Disjunction. Can the magus "
                "reach him before his Gift is quenched? Can he bargain with "
                "the settuten, or is magical war the only choice? (p. 104)"
            ),
        )
    )
    dormant(
        b.threat(
            "Sun Versus Moon",
            antagonist="The local settuten",
            summary=paragraphs(
                "A covenant that offends the local settuten may be blacklisted "
                "and targeted. The Aegis probably saves its buildings from "
                "Dissolution, but not its water or crops, and Dissidence could "
                "ruin the covenfolk's ties with the community (p. 104).",
                "Some will want to destroy these hedge wizards, and find "
                "themselves facing many foes and the Berbers besides. Others "
                "will seek peace, a hard road with The Gift souring every "
                "meeting.",
            ),
        )
    )
    dormant(
        b.threat(
            "Forewarned Is Forearmed",
            antagonist="A cabal of sahirs",
            summary=paragraphs(
                "As a prelude, perhaps, to an Arab push into Berber land, "
                "sahirs plot to murder the tineqiqqiten at the grand "
                "convocation. Without them no settut can Open The Gift, and "
                "some or all of the Initiation Scripts may be lost. Premonition "
                "and omen have warned the seeresses, who are seeking allies, "
                "but will not say at once why (p. 104).",
            ),
        )
    )
    dormant(
        b.threat(
            "Predators and Prey Alike",
            antagonist="A pack of bouda",
            summary=paragraphs(
                "A bouda pack hunting the countryside has come to like the "
                "taste of covenfolk. Will the magi find the killers and "
                "destroy them, or bind them to service? What if they get "
                "inside the covenant and hunt from there? And if they do "
                "serve, will their masters feed them slaves or make true "
                "scavengers of them? (p. 116)",
            ),
        )
    )
    dormant(
        b.threat(
            "Dream a Dream of Days Past",
            summary=paragraphs(
                "The characters seek out a local murabit to find a spirit, a "
                "lost site or some fragment of antiquity through the ancestors "
                "he can call. The dreaming ghosts remember as far back as Rome, "
                "not always reliably. Could his gift lead to the Ancient Magic "
                "of Canaanite Necromancy, or to Insight into an initiation of "
                "Dream Magic? How will they persuade so pious a man to share? "
                "A magus might become his adopted son by saving his firstborn "
                "from a bargain with a sahir and the appetites of an insatiable "
                "slaver jinn (p. 128).",
            ),
        )
    )
    dormant(
        b.threat(
            "A Lost Key",
            antagonist="A Goetic infernalist",
            summary=paragraphs(
                "Locals bring the magi a low pedestal, a cippus, dedicated to "
                "Melkart of Tyre as a votive, carved in Greek and strange "
                "signs. It bears the True Name of Melkart, and a native Goetic "
                "infernalist wants it: he hides among the visiting peasants, "
                "working round every precaution to steal it (p. 131).",
            ),
            secrets=(
                "The Cippus of Melqart, in Classic Greek and Punic: a tractatus "
                "of Dead Language: Punic, Quality 5, studied for a season with "
                "Dead Language: Punic or Classic Greek of 4 or more. It is a "
                "key to Phoenician."
            ),
        )
    )
    dormant(
        b.threat(
            "Undiscovered Heritage",
            antagonist="Ba'al Ammon",
            summary=paragraphs(
                "A magus finds a cache of ancient Greek manuscripts credited to "
                "the Cabieri, in the libraries of Constantinople or in ruins "
                "of the Theban Tribunal. They hint at a tie between the Punic "
                "magic of Carthage and the rites of Thoth-Hermes, and name "
                "secret cult sites in the mountains west of Carthage (p. 131).",
            ),
            secrets=(
                "Seekers who follow the trail may find the false faerie Ba'al "
                "Ammon lingering there, or easily called. He offers ancient "
                "magic, and the risk of unwitting corruption."
            ),
        )
    )
    dormant(
        b.threat(
            "Health and Long Life",
            summary=paragraphs(
                "As a gift, from ruins, or from the bazaars of the Tell, the "
                "magi come by a life-extending amulet of the Punic priests. Is "
                "it an Arcane Connection to Ba'al Ammon, a relic of Carthage, "
                "or a trap laid by Gifted sahirs of the Caliphate? Is the Aging "
                "bonus worth the risk? Would taking it apart for Insight yield "
                "a minor Breakthrough in longevity? (p. 131)",
            ),
        )
    )
    dormant(
        b.threat(
            "Wages of Carthage",
            antagonist="A Gifted sahir",
            moves="A track",
            summary=paragraphs(
                "A Gifted sahir against the magi seems to have endless Vim vis, "
                "and a stream of supernatural assassins harries them whenever "
                "they leave the covenant. Beat him, and his tainted trove "
                "remains: will they take it, and what will they do with it? "
                "How will they keep another sahir from doing the same? "
                "(p. 131)",
            ),
            secrets=("He has found Ba'al Ammon's cache of vis infesta outside Tunis."),
            stages=[
                b.stage("Faerie jinn", clues="His first servants are Faerie jinn."),
                b.stage("Infernal jinn", clues="Later foes are Infernal jinn."),
                b.stage("Full demons", clues="At last, demons outright."),
            ],
        )
    )
    dormant(
        b.threat(
            "To Resurrect the Brazen Tophet",
            summary=paragraphs(
                "In the ruins of Carthage a magus finds a huge lump of melted "
                "bronze that seems to hold several pawns of vis. Dug out and "
                "reformed, it would work again as a Tophet of Sacrifice, "
                "turning offerings into Vim vis. Such a prize might lead "
                "greedy magi deeper and deeper into depravity; and if word "
                "reaches vis-poor Tribunals or amoral, vis-hungry magi, its "
                "owners will be challenged on many fronts (p. 131).",
            ),
        )
    )
