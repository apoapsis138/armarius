"""The Bestiary (TC&TC, every chapter), in paraphrase.

Every creature the book gives a stat block (C19): the 24 with a Might,
the mundane beasts, the short Arabian templates of ch06, and the two
human kinds of the Mongol host. Keys:

- the jinn and other spirits: creatures["kharrat"] (Kharrat the
  Braggart, Infernal 10; order.py binds him to 'Arkhaman in its stats
  step, so the key stays), ["jumayl"] (Faerie 15), ["bali_al_ard"] (the
  racehorse the text calls Hesaan, Faerie 5; C19), ["abd_al_qininna"]
  (the 'afrit of the Bottle, Faerie 30), ["ghula"] (Faerie 20),
  ["baghl"] (Magic 15), ["zawbaa"] (Magic 18), ["ighraq"] (Magic 40;
  8 Aquam in his body, and the 2 Aquam a year his gorge gives, which
  is the gorge's), ["buran"] (Infernal 25, in the Yenghissar sword),
  ["infernal_ghul"] (Infernal, up to 20), ["qareen"] (Infernal 15),
  ["azi_dahak"] (Infernal 40);
- the other beings with a Might: ["aladlammu"] (one block for the bull
  pair, Faerie 30), ["simurgh"] (Faerie 50), ["heavenly_horse"] (Faerie
  5), ["nisnas"] (Magic 10), ["giant_of_ad"] (Magic 20),
  ["girtablullu"] (Magic 17), ["mushhushshu"] (Magic 25), ["nasu"]
  (Magic 5), ["hyrcanian_tiger"] (Magic 10), ["olghoi_khorkhoi"] (Magic
  14), ["ruq"] (Magic 14), ["steppe_spirits"] (Magic 30 to 45, a
  template);
- the beasts: ["gazelle"], ["bactrian_camel"] (with its pack, wild and
  war variants), ["elephant"] (with the bull and the war elephant),
  ["steppe_pony"], and ch06's templates built on other books' beasts:
  ["saluqi"], ["saqr"], ["shahin"], ["dromedary"], ["arabian_horse"]
  and ["flying_serpent"] (no numbers printed);
- the people: ["mongol_trooper"] (the orlock general's changes in its
  notes) and ["spirit_shaman"].

Every jinni takes the Jinni Free Virtue. Might, Characteristics,
Virtues, Abilities (a faerie's Pretenses), combat and powers as printed,
each power at the book's Might cost and Initiative; vis in a creature's
body is its Bestiary vis (C17). Kharrat's Envisioning costs 1 point for
a dream and 5 for a waking vision (C24). A Virtue the catalog lacks is
left out and named in the creature's notes (Gluttonous, Positive
Reputation, Thick Skin), or given as its nearest entry (Pass as Human
as Passes for Human, Tough Feathers as Thick Fur/Thick Scales, Water
Lore as Nature Lore).

Each creature is set at its place in `finish`, once every part has
built: the first of its place keys a region part made, else a place
whose name holds one of its words, else its region; the place links to
it. The qareen and the 'afrit of the Bottle haunt no one place and are
left unplaced. East.py's shared creatures["al_khidr"] is not remade:
finish puts him at the Rock of Moses (or Shamakhi, or Shirvan) when he
has no place. Each jinni is linked from east.py's world["jinn"]. The 45
lesser demons stay in the book (checklist 4), and the beings named
without stats (Iblis, the anqa, Lukman's falcons, the peris and the
rest) are sentences at their places, written by the parts that make
those places."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...models import BodyVis
from ..builder import (
    characteristics,
    paragraphs,
    titled,
    vf_great,
    vf_minor,
    vf_puissant,
)

if TYPE_CHECKING:
    from ...models import Creature, Neighbour
    from ..builder import Builder
    from . import Cradle

#: A person's Fatigue levels, printed in most blocks.
FATIGUE = "OK, 0, -1, -3, -5, Unconscious"
#: A herd beast's, with its extra levels.
BEAST_FATIGUE = "OK, 0/0, -1/-1, -3/-3, -5, Unconscious"
JINNI = "Jinni"
BISMILLAH = "the Bismillah invocation"
PRETENSES = "Its Abilities are the book's Pretenses."

#: Where each creature lives: the keys a part may have made (in
#: cradle.places or cradle.world), then words a place's name may hold,
#: then the region to fall back on ("" for a creature with no one home).
HOMES: dict[str, tuple[tuple[str, ...], tuple[str, ...], str]] = {
    "kharrat": (("sanaa",), ("Sana'a",), "arabia"),
    "jumayl": (("al_mushaqqar", "bahrayn"), ("Mushaqqar", "Bahrayn"), "arabia"),
    "bali_al_ard": (("najd",), (), "arabia"),
    "abd_al_qininna": ((), (), ""),
    "ghula": ((), (), "arabia"),
    "baghl": (("elburz", "alborz", "mazandaran"), ("Elburz", "Alborz"), "persia"),
    "zawbaa": (("nefud", "dahna"), ("Nefud",), "arabia"),
    "ighraq": (("ighraq_gorge",), ("Ighraq", "Lesser Zab"), "mesopotamia"),
    "buran": (("taklimakan", "yenghissar"), ("Taklimakan", "Taklamakan"), "silk_road"),
    "infernal_ghul": ((), (), "arabia"),
    "qareen": ((), (), ""),
    "azi_dahak": (("damavand", "mount_damavand"), ("Damavand",), "persia"),
    "aladlammu": (("babylon",), ("Babylon",), "mesopotamia"),
    "simurgh": (("damavand", "mount_damavand"), ("Damavand",), "persia"),
    "heavenly_horse": (("farghana",), ("Farghana",), "silk_road"),
    "nisnas": (("hadramawt",), ("Hadramawt",), "arabia"),
    "giant_of_ad": (("ubar", "uman"), ("Ubar", "Iram"), "arabia"),
    "girtablullu": (("jazira",), (), "mesopotamia"),
    "mushhushshu": (("assyria", "jazira"), ("Assyria",), "mesopotamia"),
    "nasu": ((), (), "persia"),
    "hyrcanian_tiger": (("mazandaran", "great_desert"), ("Hyrcania",), "persia"),
    "olghoi_khorkhoi": (("great_desert", "kyzylkum"), ("Kyzylkum",), "persia"),
    "ruq": (("roof_of_the_world", "badakhshan"), ("Roof of the World",), "silk_road"),
    "steppe_spirits": (("transoxiana",), (), "silk_road"),
    "gazelle": (("great_desert",), ("Dasht-i Kavir",), "persia"),
    "bactrian_camel": ((), (), "silk_road"),
    "elephant": (("khwarazm",), (), "silk_road"),
    "steppe_pony": (("transoxiana",), (), "silk_road"),
    "saluqi": (("najd",), (), "arabia"),
    "saqr": (("najd",), (), "arabia"),
    "shahin": (("najd",), (), "arabia"),
    "dromedary": ((), (), "arabia"),
    "arabian_horse": (("najd",), (), "arabia"),
    "flying_serpent": (("hadramawt",), ("Hadramawt",), "arabia"),
    "mongol_trooper": (("transoxiana",), (), "silk_road"),
    "spirit_shaman": (("transoxiana",), (), "silk_road"),
}
#: Where al-Khidr (east.py's) is set when he has no place: the rock
#: where Moses met him.
KHIDR_HOME = (("rock_of_moses", "shamakhi", "shirvan"), ("Rock of Moses",))

#: The note on each place's link to its creature.
ROLE = {
    "kharrat": "the Infernal jinni bound to Sana'a's young vizier",
    "jumayl": "a jann caravan guard who drinks in its markets",
    "bali_al_ard": "a jinni racehorse of the Bedouin races",
    "ghula": "the faerie ghulas who marry and feed on men",
    "baghl": "the earth jinni of a quarried cave",
    "zawbaa": "the whirlwind jinn of the sands",
    "ighraq": "the drowning flood of the gorge",
    "buran": "the storm demon bound in the Yenghissar sword",
    "infernal_ghul": "the Infernal ghuls of its graveyards and slums",
    "azi_dahak": "the demon who makes a Zahhak of a ruler",
    "aladlammu": "the winged bull guardians against demons",
    "simurgh": "the great bird of the mountain",
    "heavenly_horse": "the blood-sweating horses of the valley",
    "nisnas": "the half-men of the forests",
    "giant_of_ad": "the giants of 'Ad in the deep desert",
    "girtablullu": "the scorpion-men who guard the old ruins",
    "mushhushshu": "the snake-dragons of old Assyria",
    "nasu": "the corpse-flies of the nasu spirit",
    "hyrcanian_tiger": "the swift tigers that hunt its gazelles",
    "olghoi_khorkhoi": "the death worm under the sand",
    "ruq": "the giant eagles of the high valleys",
    "steppe_spirits": "the genii loci of the steppe",
    "gazelle": "the Persian gazelle",
    "bactrian_camel": "the two-humped camels of the caravans",
    "elephant": "the elephants of the eastern armies",
    "steppe_pony": "the nomads' hardy ponies",
    "saluqi": "the Bedouin's prized hunting hounds",
    "saqr": "the falconers' saqr",
    "shahin": "the falconers' shahin",
    "dromedary": "the one-humped camel",
    "arabian_horse": "the Arabian racehorse",
    "flying_serpent": "the winged serpents of the incense trees",
    "mongol_trooper": "the Mongol horsemen",
    "spirit_shaman": "the shamans who ride with the Mongols",
}

#: The jinn among them, linked from east.py's world["jinn"], with the
#: people each belongs to.
JINN = {
    "kharrat": "a shaitan, bound to a sahir",
    "jumayl": "one of the jann",
    "bali_al_ard": "a faerie jinni in a horse's shape",
    "abd_al_qininna": "an 'afrit of the Bottles of Suleiman",
    "ghula": "the dark faerie jinn of the desert",
    "baghl": "a Magic jinni of the earth",
    "zawbaa": "a Magic jinni of whirling sand",
    "ighraq": "a pagan jinni of the river",
    "buran": "a storm demon reckoned among the corrupt jinn",
    "infernal_ghul": "the degenerate Infernal jinn",
    "qareen": "the companion spirit every person has",
}

#: The creatures this part makes, by key, for `finish`.
_MADE: dict[str, Creature] = {}


def _times(entry: Any, count: int) -> list[Any]:
    """A Virtue or Quality the block takes `count` times."""
    return [entry] * count


def _ways(land: str) -> tuple[str, dict[str, str]]:
    return ("Ways of the {land}", {"land": land})


def _ward(kind: str, against: str = BISMILLAH) -> tuple[str, dict[str, str]]:
    return (kind, {"ward": against})


def _immune(hazard: str) -> tuple[str, dict[str, str]]:
    return ("Greater Immunity", {"hazard": hazard})


def _major(virtue: str) -> tuple[str, dict[str, str]]:
    return ("Major Virtue", {"virtue": virtue})


def build(cradle: Cradle) -> None:
    _MADE.clear()
    _infernal_jinn(cradle)
    _faerie_jinn(cradle)
    _magic_jinn(cradle)
    _arabia(cradle)
    _mesopotamia(cradle)
    _persia(cradle)
    _silk_road(cradle)
    _arabian_templates(cradle)
    _mongols(cradle)
    cradle.creatures.update(_MADE)


# -- ch03 and ch04: the Infernal jinn --


def _infernal_jinn(cradle: Cradle) -> None:
    b = cradle.b
    _MADE["kharrat"] = b.creature(
        "Kharrat the Braggart",
        page="p. 35",
        realm="Infernal",
        might=10,
        form="Ignem",
        order="Tempter (Shaitan)",
        hierarchy=1,
        confidence=(1, 3),
        weakness=(
            "Protected Group: a victim who rejects him wholly and willingly, "
            "spending a Confidence Point on it; and anyone who speaks the "
            "Bismillah."
        ),
        block={
            "characteristics": characteristics(0, 1, 3, 0, 2, 2, 2, 1),
            "virtues_flaws": [JINNI, "Greater Malediction", "Weak-Willed"],
            "abilities": [
                ("Living Language: Arabic", 5, "threats"),
                ("Brawl", 6, "fist"),
                ("Charm", 6, "bragging"),
                ("Concentration", 2, "maintaining spells"),
                ("Folk Ken", 3, "temptation"),
                ("Penetration", 3, "Vim"),
                ("Theology: Islam", 1, "jinn"),
            ],
            "traits": {"Selfish": 5, "Proud": 3, "Cruel": 3},
        },
        attacks=[b.attack("Fist", 1, 9, 8, 2)],
        soak=10,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Apparition",
                1,
                0,
                "Imaginem",
                does="Takes an illusory shape that only his chosen victim, "
                "'Arkhaman, can see; to him it seems a living person in every "
                "way.",
            ),
            b.power(
                "Protection of the Close Friend",
                0,
                3,
                "Mentem",
                does="His chosen victim cannot move against him unless sorely "
                "provoked, as a son could not strike his mother. The victim may "
                "rage at him freely, but each fresh attempt to oppose him in "
                "deed takes a great effort of will.",
            ),
            b.power(
                "Control Human",
                2,
                1,
                "Mentem",
                does="If it penetrates, he commands his companion, who obeys "
                "as well as he can; the victim may try to throw off the control "
                "each time he is told to act against his faith. Its Initiative "
                "is his Quickness.",
            ),
            b.power(
                "Envisioning",
                1,
                2,
                "Mentem",
                does="Enters his companion's dreams for 1 point, slowly "
                "darkening them and speaking through any figure in them; or, "
                "for 5 points, forces a waking vision of whatever he likes. A "
                "vision can stun for a round, and the victim needs a Brave roll "
                "of 9+ to avoid retching, fits or terror. The text gives the "
                "cost once as 1 or 2; the pack follows the power's own account "
                "and the qareen's (1 or 5).",
            ),
            b.power(
                "Coagulation",
                2,
                -1,
                "Corpus",
                does="Forms a body, as Realms of Power: The Infernal p. 31 describes.",
            ),
            b.power(
                "Obsession",
                1,
                -5,
                "Vim",
                does="Stirs the trait Overconfident in a victim, for 1 to 3 "
                "points, as Realms of Power: The Infernal p. 31 describes.",
            ),
        ],
        vis=[BodyVis(2, "Ignem", "in his eyes")],
        appearance=(
            "A pale man whose eyes are wholly black and smoke like embers. "
            "Most of the time he stays in spirit form, unseen."
        ),
        notes=paragraphs(
            "A vain, haughty shaitan whom the young sahir 'Arkhaman of "
            "Sana'a summoned as his first spirit, believing him to be his "
            "father. Kharrat thinks the boy is wholly his and that the "
            "longing to please a father will lead him into evil. So far "
            "'Arkhaman has kept him in hand with vis, as his elders warned "
            "him to. Reputations: none.",
        ),
        secrets=[
            titled(
                "Kharrat's aim",
                "His aim is to bind 'Arkhaman by an accepted duty and send "
                "him to find his mother, the imam's niece who hid his birth: "
                "the shame his coming would bring her is what the demon "
                "relishes.",
            ),
        ],
    )
    _MADE["buran"] = b.creature(
        "The Buran of Yenghissar",
        page="p. 70",
        realm="Infernal",
        might=25,
        form="Auram",
        size=4,
        order="Aerial Powers (Buran)",
        hierarchy=3,
        confidence=(1, 3),
        weakness="Protected Group: anyone who speaks the Bismillah.",
        tires=False,
        can_be_wounded=False,
        block={
            "characteristics": characteristics(-5, 0, 3, -2, 0, 0, 3, 6),
            "virtues_flaws": [
                JINNI,
                "Berserk",
                "Strong-Willed",
                "Wilderness Sense",
                "Fury",
                "Greater Malediction",
                "Mute",
            ],
            "abilities": [
                ("Living Language: Arabic", 5, "understanding"),
                ("Folk Ken", 3, "travellers"),
                ("Theology: Islam", 3, "jinn"),
                ("Survival", 5, "desert"),
                ("Area Lore: Taklamakan", 5, "legends"),
                ("Wilderness Sense", 2, "weather"),
            ],
            "traits": {"Untameable": 5},
            "reputations": {"Scourge of Yenghissar (local)": 2},
        },
        powers=[
            b.power(
                "Delusion of the Desert",
                1,
                3,
                "Imaginem",
                does="Shows a lost traveller his missing friends or a "
                "welcoming oasis before it falls on him, or shows itself as a "
                "sandstorm in a man's shape with burning eyes to terrify. An "
                "image of one thing costs 1 point, one filling a room 5. Every "
                "such image has some flaw: a wrong smell, or only one person "
                "sees it.",
            ),
            b.power(
                "Elemental Control of Wind",
                1,
                1,
                "Auram",
                does="Any Creo, Muto or Rego Auram effect, at 1 Might point a "
                "magnitude (so its cost varies), up to a level no higher than "
                "its Might and never a Ritual.",
            ),
            b.power(
                "Recalcitrance",
                0,
                0,
                "Vim",
                does="Always active. Any supernatural attempt to control it, "
                "though not to destroy it, treats its Might as half again as "
                "high, or raises the Ease Factor by half: a Circular Ward "
                "Against Demons must be of level 38 to hold it back.",
            ),
        ],
        vis=[
            BodyVis(5, "Auram", "vis prava, left as black sand when it is dispersed"),
        ],
        appearance=(
            "A huge formless whirl of raging black sand; Second Sight makes "
            "out a giant shadow in a man's shape inside it."
        ),
        notes=paragraphs(
            "A wild storm spirit of the desert that once fell on the village "
            "of Yenghissar, on the road to Khashgar, every seventh year, "
            "ruining its crops and herds. A careless sahir of Infernal bent "
            "has bound it into his family's sword with the Goetic Art of "
            "Binding (Realms of Power: The Infernal p. 117), and it rages to "
            "be free, stirring up the elements around him. It is mute: its "
            "Arabic is how much it understands.",
            "It has no body and cannot touch the world but by its powers, so "
            "it has no combat, Soak or wounds, and lacks the Coagulation and "
            "Obsession most demons have. Storm spirits like it haunt the "
            "Taklamakan, weaker and stronger; a Magic one is much the same "
            "without Recalcitrance or the malice.",
        ),
    )
    _MADE["infernal_ghul"] = b.creature(
        "Ghul (Infernal)",
        page="p. 73",
        realm="Infernal",
        might=20,
        form="Corpus",
        order="Furies",
        how_many=(
            "solitary, in graveyards, refuse pits and slums; Might usually "
            "no more than 20"
        ),
        weakness=(
            "Protected Group: anyone who speaks the Bismillah; Vulnerability (iron)."
        ),
        block={
            "virtues_flaws": [JINNI],
            "abilities": [
                ("Living Language: Arabic", 5, "deception"),
                ("Brawl", 6, "claws"),
                ("Charm", 4, "trust"),
                ("Stealth", 4, "urban areas"),
                ("Theology: Islam", 1, "jinn"),
            ],
        },
        powers=[
            b.power(
                "Berserker Rage",
                1,
                0,
                "Mentem",
                does="Gives someone, most often itself or its beasts, the "
                "Berserk Virtue until they calm down.",
            ),
            b.power(
                "Change Form",
                0,
                0,
                "Corpus",
                does="Reshapes its own flesh at will into a human or animal "
                "form (Corpus or Animal), most ghuls into one kind only, within "
                "the natural Size of that kind. It is no spell, so Magic "
                "Resistance does nothing against a changed ghul's blows.",
            ),
            b.power(
                "Endurance of the Enraged",
                0,
                0,
                "Corpus",
                does="Wound penalties do not touch it, except on Defense.",
            ),
            b.power(
                "Restoration",
                10,
                0,
                "Corpus",
                does="The next blow that strikes it heals, instead, the wound "
                "it took the last time it was hurt; one blow each use.",
            ),
        ],
        appearance=(
            "A tall, stooped, wild thing with long arms and iron claws, in "
            "rags and torn robes filthy with marrow, blood and grave dirt. "
            "Cleverer ones look nearly human, but sharp-featured, with "
            "pointed or saw-edged teeth and long hooked nails."
        ),
        notes=paragraphs(
            "A degenerate jinni of a debased tribe given to the Infernal, a "
            "cannibal of the night that preys on the weak or eats carrion. "
            "It goes in heavy robes as a lost traveller, a woman in need or "
            "a kindly dervish, and every ghul can take the shape of at least "
            "one local scavenger: dog, hyena, jackal or vulture. It scorns "
            "weapons for nails and teeth. Folk say a ghul wounded but not "
            "slain at one stroke is healed by a second, so lone travellers "
            "fear them.",
            "A guide rather than a full block: no Characteristics or combat "
            "are printed, and other Abilities differ from ghul to ghul. A "
            "true terrestrial demon of the Furies, it cannot become "
            "incorporeal and has no Coagulation; this one lacks Envisioning "
            "and Obsession too. Exceptional ghuls command rock or flesh, "
            "illusions, possession or human magics, and the most feared "
            "summon other jinn by Sihr, the Arts Fabulosa or the Goetic "
            "Arts. It is not the female faerie ghula, whatever the two "
            "share. Its Form, Corpus, is from the book's errata.",
        ),
    )
    _MADE["qareen"] = b.creature(
        "Qareen",
        page="p. 74",
        realm="Infernal",
        might=15,
        form="Vim",
        order="Tempters (Shaitan / Qareen)",
        how_many="one for each person, as the hadith says; this is a typical one",
        weakness=(
            "Protected Group: a victim who rejects it wholly and willingly, "
            "spending a Faith Point on it; and the jinn's usual weaknesses."
        ),
        tires=False,
        can_be_wounded=False,
        block={
            "characteristics": characteristics(1, 1, 2, 3, 0, 0, 0, 2),
            "virtues_flaws": [JINNI],
        },
        powers=[
            b.power(
                "Apparition",
                1,
                0,
                "Imaginem",
                does="Takes an illusory shape only its companion sees, who "
                "takes it for a real person.",
            ),
            b.power(
                "Control Human",
                2,
                2,
                "Mentem",
                does="If it penetrates, the qareen commands its companion, who "
                "may fight free each time an order goes against his faith.",
            ),
            b.power(
                "Envisioning",
                1,
                2,
                "Mentem",
                does="Haunts its companion's dreams for 1 point, twisting them "
                "darker little by little and speaking through any figure in "
                "them; or, for 5 points, forces a waking vision that can stun "
                "him for a round, after which a Brave roll of 9+ is needed to "
                "keep from retching, fits or terror. Its favourite way of "
                "speaking to him.",
            ),
            b.power(
                "Protection of the Appointed Companion",
                0,
                2,
                "Mentem",
                does="Its companion can no more move against it than against "
                "his own mother: he may be furious with it, but to oppose it "
                "in deed takes great will and a Confidence point, each time.",
            ),
        ],
        appearance=(
            "An incorporeal spirit, a wan reflection of its companion to "
            "anyone with Second Sight; to the companion it looks lovely or "
            "dreadful as its schemes require."
        ),
        notes=paragraphs(
            "The companion spirit Islamic tradition gives every person, a "
            "private tempter. This block is for a person burdened with "
            "Plagued by a Supernatural Entity (Qareen), a Major Story Flaw, "
            "who sees and knows his qareen; quieter ones, behind the Impious Friend or "
            "Manufactured Ignorance Flaws, have a Might of 5 to 10. Its "
            "whispers seem to come from the victim's own mind, and the "
            "storyguide gives them as advice, never naming a demon.",
            "Strength, Stamina and Dexterity are n/a (it has no body, and no "
            "Coagulation); the Communication printed has no label and is "
            "taken as +3. Its Abilities vary: up to 300 experience points' "
            "worth, often matching its companion's, used to help or hinder "
            "him.",
        ),
    )
    _MADE["azi_dahak"] = b.creature(
        "Azi Dahak, Duke of the Spirits of Deceit",
        page="p. 143",
        realm="Infernal",
        might=40,
        form="Mentem",
        size=4,
        order="Duke of the Spirits of Deceit",
        hierarchy=7,
        confidence=(3, 9),
        weakness="Abhorrent Material: flame from a Mazdean fire temple.",
        block={
            "characteristics": characteristics(2, 2, 0, 1, 12, 4, 5, -1),
            "virtues_flaws": [
                "Ablating",
                "Binding",
                "Commanding",
                "Summoning",
                "Inspirational",
            ],
            "abilities": [
                ("Athletics", 5, "flying"),
                ("Brawl", 8, "bite"),
                ("Guile", 8, "promises of power"),
                ("Intrigue", 5, "nobles"),
                ("Leadership", 4, "own heads"),
                ("Organization Lore: Suhhar Sulayman", 4, "viziers"),
                ("Penetration", 4, "Possession"),
                ("Teaching", 5, "Goetic Arts"),
                ("Ablating", 12, ""),
                ("Binding", 8, ""),
                ("Commanding", 8, ""),
                ("Summoning", 10, ""),
            ],
            "traits": {"Deceitful": 6, "Hatred of Persia": 5, "Trustworthy": -5},
            "reputations": {"Legendary Tyrant King (Infernal)": 7},
        },
        attacks=[b.attack("Bite (three heads)", 1, 15, 10, 20)],
        soak=15,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Coagulation",
                4,
                -1,
                "Animal",
                does="Forms a body, and lets it go when he likes.",
            ),
            b.power(
                "Obsession",
                1,
                -5,
                "Vim",
                does="Stirs the trait Power Hungry, for 1 to 3 points (Realms "
                "of Power: The Infernal p. 31).",
            ),
            b.power(
                "Envisioning",
                1,
                0,
                "Mentem",
                does="Appears in someone's dreams.",
            ),
            b.power(
                "Possession",
                0,
                2,
                "Mentem",
                does="Costs what he puts into it, and he usually puts in his "
                "whole Might Pool, ruling his victim's acts. He regains no Might "
                "while he possesses, so he must leave now and then; meanwhile "
                "the victim dreams of his own death and damnation and may try "
                "to bar the demon's return (Realms of Power: The Infernal "
                "p. 32).",
            ),
            b.power(
                "Trust of the Innocent",
                1,
                -1,
                "Mentem",
                does="The target believes one plausible lie until shown "
                "otherwise; Intelligence against 6 resists.",
            ),
            b.power(
                "Forked Tongue of the Serpent",
                3,
                -1,
                "Mentem",
                does="The target believes any lie, however absurd, until he "
                "repeats it to someone and hears how foolish it is. An "
                "Intelligence roll of 9+ also sees through it, the first an "
                "hour after and then once an hour.",
            ),
            b.power(
                "The Serpent's Oracle",
                2,
                -3,
                "Vim",
                does="Works any Intellego effect, or foresees the nearest "
                "consequences of one chosen act.",
            ),
            b.power(
                "Empower the Possessed",
                0,
                0,
                "Vim",
                does="A victim he possesses who wilfully uses a Goetic Art adds "
                "Azi Dahak's own score in it, and may use the demon's Hierarchy "
                "in place of his own.",
            ),
        ],
        vis=[BodyVis(8, "Mentem", "vis prava, in his eyes")],
        appearance=(
            "Seldom seen in the flesh: a vast winged serpent with three heads, "
            "each with two eyes and three pairs of fangs. Snakes and scorpions "
            "pour from his wounds. He bites three foes a round, acting as a "
            "Trained Group of three."
        ),
        notes=paragraphs(
            "The demon whose host becomes Zahhak. The first Zahhak, the "
            "tyrant of Persia's heroic age, ruled a thousand years from "
            "Ctesiphon after sawing Jamshid in half, until Feridun ended his "
            "reign; since then a Zahhak has risen from time to time and "
            "Persian sahirs have fought him, never again so mighty. The last "
            "was the Shansabani sultan Muhammad of Ghur, beaten fourteen "
            "years ago. A possessed man grows a black snake from each "
            "shoulder that grows back when cut and hungers for human brains; "
            "only ending the possession cures it.",
            "At first the demon makes his host do evil, and slowly his "
            "promises corrupt the host himself; none has yet held out. Once "
            "the host embraces evil the demon teaches him the Goetic Arts, "
            "Ablating above all, to lengthen his life, gain Magic Resistance "
            "and steal the powers of other spirits. His Goetic Arts are "
            "entered as Abilities.",
        ),
        secrets=[
            titled(
                "Genghis Khan and the Zahhak",
                "Some Persian sahirs suspect that Genghis Khan is a Zahhak, "
                "or takes counsel from one, since he turns on Persia the way "
                "Azi Dahak's hosts do.",
            ),
            titled(
                "The first Zahhak",
                "The first Zahhak was never slain: an angel helped Feridun "
                "chain him beneath Mount Damavand, where he lives yet, freed "
                "of the demon Azi Dahak and kept from death by holy bonds.",
            ),
            titled(
                "Storyguide Notes",
                "Whether Genghis Khan is a Zahhak is the storyguide's choice.",
            ),
        ],
    )


# -- ch04: the Faerie jinn --


def _faerie_jinn(cradle: Cradle) -> None:
    b = cradle.b
    _MADE["jumayl"] = b.creature(
        "Jumayl, a Jinni Guide",
        page="p. 64",
        realm="Faerie",
        might=15,
        form="Vim",
        age="n/a (looks 25)",
        confidence=(1, 3),
        tires=False,
        block={
            "characteristics": characteristics(-1, 2, 0, 0, 2, 0, 2, 3),
            "virtues_flaws": [
                JINNI,
                "Passes for Human",
                *_times("Greater Power", 2),
                "Ostentatious",
                "Faerie Speech",
                "Highly Cognizant",
                "Humanoid Faerie",
                *_times("Increased Faerie Might (Minor)", 2),
                "Improved Characteristics",
                "Reputation as Confidence",
                "Second Sight",
                "Skinchanger",
                "Warrior",
                "Well-Traveled",
                "Wilderness Sense",
                "Greater Malediction",
                "Might Recovery Requires Vitality",
                "Carefree",
                "Dutybound",
                _ward("Traditional Ward"),
                "Vulnerable to Folk Tradition",
            ],
            "abilities": [
                ("Animal Handling", 3, "camels"),
                ("Athletics", 3, "running"),
                ("Area Lore: Mythic Middle East", 4, "trade routes"),
                ("Awareness", 3, "alertness"),
                ("Brawl", 3, "dagger"),
                ("Bows", 5, "short bow"),
                ("Carouse", 2, "power drinking"),
                ("Faerie Speech", 5, ""),
                ("Area Lore: al-Mushaqqar", 2, "drinking establishments"),
                ("Faerie Lore", 3, "jinn"),
                ("Folk Ken", 4, "mercenaries"),
                ("Leadership", 4, "battle"),
                ("Ride", 3, "camels"),
                ("Second Sight", 3, "jinn"),
                ("Single Weapon", 7, "long sword"),
                ("Survival", 2, "deserts"),
                ("Theology: Islam", 1, "jinn"),
                ("Wilderness Sense", 3, "find water"),
            ],
            "traits": {"Impulsive": 3, "Cheerful": 3, "Impious": -1},
            "reputations": {"Skilled caravan guard (Mythic Middle East)": 2},
        },
        attacks=[b.attack("Long sword", 5, 14, 9, 8)],
        soak=3,
        powers=[
            b.power(
                "Cuirass of the Zephyr",
                1,
                3,
                "Auram",
                does="As Circling Winds of Protection, lasting for as long as "
                "he goes on reciting verses of the Qur'an (the Duration of "
                "Recitation, much like Concentration).",
            ),
            b.power(
                "Blinding Light of the Pious",
                1,
                3,
                "Ignem",
                does="As Flash of the Scarlet Flames.",
            ),
            b.power(
                "Tay al-Ard (Travel)",
                4,
                1,
                "Corpus",
                rtd=("Touch", "Momentary", "Group"),
                level=45,
                does="Takes him, and two people whose hands he holds, at once "
                "to any place he has visited or holds an Arcane Connection to, "
                "however far. As the Leap of Homecoming at Touch and Group; one "
                "Intricacy point lowers its cost.",
            ),
        ],
        vis=[BodyVis(3, "Vim", "in a camel's tooth")],
        equipment=(
            "A fine Damascus steel long sword, a caravan guard's leather scale "
            "armour, showy jewellery."
        ),
        appearance=(
            "A handsome, supple man of no clear Eastern people, with skin "
            "like alabaster and white hair, one eye an iridescent green and "
            "the other the blue of the sea. He wears swirling robes of deep "
            "blue over light leather, set off with gold. His name means "
            "little camel."
        ),
        notes=paragraphs(
            "One of the jann: a mercenary guide condemned, for a crime his "
            "brother did, to wander the caravanserais of the trade routes "
            "from the Levant to Transoxiana and further. A fine swordsman and "
            "woodsman, he is known to Muslim merchants and even the Levant's "
            "Redcaps for his good humour and his daring against raiders. Any "
            "great city of the region may hold him, but he likes best the "
            "markets by the fortress of al-Mushaqqar in Bahrayn, for the "
            "well-paid work and the cheap drink. Like most faerie jinn he can "
            "take a beast's shape, in his case a white wild Bactrian camel "
            "(Skinchanger). " + PRETENSES,
            "He never tires, yet ordinary wine undoes him easily. Spent Might "
            "comes back only after a full night's rest and a meal among "
            "fellow travellers in a human settlement, with their rations or "
            "an inn's food, drink men have brewed, and their songs and tales "
            "of the road: each eight hours restores Might equal to the aura, "
            "as adjusted for his realm, or 1 at least. He need not truly eat. "
            "He guards his True Name and leaves no Arcane Connections about. "
            "Made as a magus-level character by Realms of Power: Faerie; to "
            "make him a plain companion, drop Ostentatious, Highly Cognizant "
            "and the two Increased Might Virtues, make his powers Lesser, and "
            "trade his Might Recovery Flaw for three Minor Flaws.",
        ),
    )
    _MADE["bali_al_ard"] = b.creature(
        "Bali' al-Ard, the Swallower of the Ground",
        page="p. 65",
        realm="Faerie",
        might=5,
        form="Animal",
        size=2,
        confidence=(1, 3),
        tires=False,
        block={
            "characteristics": characteristics(-2, 0, 2, -4, 4, 3, 1, 5),
            "virtues_flaws": [
                JINNI,
                "Faerie Beast",
                "Greater Power",
                *_times(vf_great("Quickness"), 2),
                "Improved Characteristics",
                ("Mythic {characteristic}", {"characteristic": "Quickness"}),
                *_times("Personal Power", 2),
                "Reputation as Confidence",
                "Curse of Venus",
                "Greater Malediction",
                "Proud (Minor)",
                "Incognizant",
                _ward("Traditional Ward"),
                ("Tragic {characteristic}", {"characteristic": "Intelligence"}),
                "Domesticated",
                "Fast Runner",
                "Herd Animal",
                *_times("Imposing Appearance", 3),
            ],
            "abilities": [
                ("Living Language: Arabic", 5, "horses"),
                ("Athletics", 6, "racing"),
                ("Awareness", 3, "bad footing"),
                ("Theology: Islam", 1, "jinn"),
            ],
            "traits": {"Proud": 3, "Loyal": 2, "Brave": 1},
            "reputations": {"Magnificent racehorse (local)": 3},
        },
        attacks=[b.attack("Hooves", 6, 3, 4, 5)],
        soak=3,
        powers=[
            b.power(
                "Drinker of the Wind",
                1,
                1,
                "Animal",
                level=30,
                does="Carries him at once to any place within seven leagues "
                "that he can see or holds an Arcane Connection to. As Seven "
                "League Stride, but not being Hermetic it takes his rider too. "
                "Four Intricacy points speed it and cheapen it.",
            ),
            b.power(
                "Immateriality",
                3,
                2,
                "Imaginem",
                rtd=("Personal", "Sun", "Individual"),
                level=40,
                does="Makes him immaterial until the next sunrise or nightfall.",
            ),
        ],
        vis=[BodyVis(1, "Animal", "in a copper horseshoe")],
        equipment="Tack and harness of rare quality, horseshoes of coppery gold.",
        appearance="A splendid Arabian stallion, of the breed famed even in Europe.",
        notes=paragraphs(
            "The jinni racehorse of a young Bedouin sahir, Salih al-Kamil, "
            "who loves him dearly. (The text calls the example horse Hesaan, "
            "which only means horse; the block names him Bali' al-Ard, and "
            "the pack does too.) He never tires and can travel by magic, so "
            "in the dust and muddle of a long desert race he cheats, winning "
            "his master glory that feeds the horse's need for vitality. "
            "Breeders hound the sahir to put mares to him, not knowing that "
            "stud work takes the horse from his master's side and can never "
            "get a foal. He can take no shape but a horse's, though he can "
            "become immaterial.",
            "His Quickness specialty is racing (Mythic Quickness, allowed "
            "though Heroic, since it makes the racehorse); like any horse he "
            "has +3 to running. He is a fit khadim, a servant spirit, for a "
            "new unGifted sahir with small Solomonic scores; built on a "
            "courser and not balanced as a player's character. " + PRETENSES,
        ),
    )
    _MADE["abd_al_qininna"] = b.creature(
        "'Abd al-Qininna, Servant of the Bottle",
        page="p. 66",
        realm="Faerie",
        might=30,
        form="Imaginem",
        size=3,
        confidence=(1, 3),
        tires=False,
        block={
            "characteristics": characteristics(0, 2, 2, 0, 4, 2, 1, 1),
            "virtues_flaws": [
                JINNI,
                "Monstrous Appearance",
                "External Vis (Major)",
                *_times("Greater Power", 2),
                *_times("Ritual Power", 4),
                "Faerie Speech",
                *_times("Improved Powers", 2),
                *_times("Lesser Power", 4),
                "Narrowly Cognizant",
                "Reputation as Confidence",
                "Intangible Flesh",
                _ward("Sovereign Ward"),
            ],
            "abilities": [
                ("Penetration", 6, ""),
                ("Theology: Islam", 1, "jinn"),
            ],
            "traits": {"Proud": 3, "Sly": 3, "Cruel": 2},
            "reputations": {"Terrifyingly magical": 3},
        },
        powers=[
            b.power(
                "Binding Oath",
                5,
                -19,
                "Vim",
                rtd=("Voice", "", ""),
                level=50,
                penetration_bonus=15,
                does="A Ritual Power. Whoever frees the seemingly captive "
                "'afrit may bargain for three wishes, or for a span of "
                "conditional service as its nature dictates, if he swears to "
                "destroy the bottle and set the jinni free for ever. Five "
                "Intricacy points cheapen it.",
            ),
            b.power(
                "Eidolon",
                2,
                -2,
                "Imaginem",
                level=20,
                does="Taken twice: its glamour shows both as the copper bottle "
                "that seems to hold it and as a towering column of smoke in a "
                "man's shape rising from the bottle's mouth.",
            ),
            b.power(
                "Illusionary Home",
                4,
                -4,
                "Imaginem",
                level=40,
                does="Raises a sumptuous phantom palace for whoever holds the bottle.",
            ),
            b.power(
                "Flight",
                3,
                0,
                "Auram",
                rtd=("Touch", "", ""),
                level=30,
                does="Always active: as Wings of the Soaring Wind.",
            ),
            b.power(
                "Loosely Material",
                0,
                -5,
                "Corpus",
                level=25,
                does="At a cost that varies, gives a would-be master a plain "
                "bottle to handle, or gives its 'afrit form enough substance to "
                "carry loads, use Touch powers or fight when its master bids.",
            ),
            b.power(
                "Tay al-Ard (Travel)",
                4,
                1,
                "Corpus",
                rtd=("Touch", "Momentary", "Group"),
                level=50,
                does="Bears the 'afrit and whatever it carries at once to any "
                "place the bottle's holder has visited or holds an Arcane "
                "Connection to, at any distance; as the Leap of Homecoming. "
                "One Intricacy point cheapens it.",
            ),
            b.power(
                "Serendipitous Wealth",
                10,
                -9,
                "Terram",
                level=50,
                does="A Ritual Power that seems to grant the Wealthy Virtue, "
                "but, like the False Gods' Wealth of Nations, fetches the "
                "treasure from somewhere else (Realms of Power: The Infernal "
                "p. 37). Five Intricacy points cheapen it.",
            ),
        ],
        vis=[BodyVis(6, "Imaginem", "gathered in its bottle")],
        appearance=(
            "At first a solid copper flask shaped like a gourd, stoppered "
            "with lead stamped with Suleiman's seal. Disturb the seal and it "
            "becomes a pillar of smoke topped by a vast torso, red or "
            "sometimes blue or green, with a monstrous horned or jag-toothed "
            "face. The novice takes that for the faerie; the jinni is still "
            "a bodiless spirit under the glamour."
        ),
        notes=paragraphs(
            "One of the Bottles of Suleiman, a kind of faerie jinni grown "
            "from the folk tales of poor fishermen who net a sealed copper "
            "flask, a cucurbite, and free a grateful or furious jinni from "
            "it. These jinn take the shape of the bottle itself and play out "
            "stories of riches and humbling (Realms of Power: Faerie p. 79) "
            "on any shore of the Islamic lands, near fishing villages. This "
            "one is servile. Its External Vis is the copper bottle, which "
            "grants Self-Confident. Intelligence is n/a as printed (taken "
            "as 0); no combat is printed. " + PRETENSES,
            "Too strong and too tied to its story to be a player's "
            "character; only a very experienced sahir could bind it as a "
            "khadim, though weaker bottles might suit younger ones. Drawn from "
            "two tales of the Nights, The City of Brass and The Fisherman and "
            "the Jinni. It is left "
            "unplaced: such bottles wash up anywhere along the coasts.",
        ),
    )
    _MADE["ghula"] = b.creature(
        "Ghula (Faerie)",
        page="p. 72",
        realm="Faerie",
        might=20,
        form="Corpus",
        how_many="in the cities and deserts, each in her chosen household",
        tires=False,
        block={
            "characteristics": characteristics(0, 0, 5, 1, 1, 0, 0, 1),
            "virtues_flaws": [
                JINNI,
                *_times("Greater Power", 2),
                "Infiltrator (Major)",
                _ways("Desert"),
                "Faerie Sight",
                "Faerie Speech",
                "Feast of the Dead",
                "Humanoid Faerie",
                *_times("Increased Faerie Might (Minor)", 3),
                "Personal Power",
                "Narrowly Cognizant",
                "Greater Malediction",
                "Restricted Might (Major)",
                _ward("Traditional Ward"),
            ],
            "abilities": [
                ("Living Language: Arabic", 5, "seduction"),
                ("Charm", 6, "men"),
                ("Brawl", 6, "in dark areas"),
                ("Stealth", 9, "urban areas"),
                ("Theology: Islam", 1, "jinn"),
            ],
            "traits": {"Demure/Ravenous": 3},
        },
        attacks=[
            b.attack("Claws", 0, 11, 10, 5),
            b.attack("Fangs", 1, 10, 8, 4),
        ],
        soak=0,
        powers=[
            b.power(
                "Cause Drowsiness",
                2,
                -2,
                "Corpus",
                rtd=("Touch", "Until", "Individual"),
                level=25,
                does="Puts a person she touches to sleep. ReCo (Base 4, +1 "
                "Touch, +4 Until); one Intricacy point cheapens it.",
            ),
            b.power(
                "Illusionary Home",
                0,
                -3,
                "Imaginem",
                rtd=("Touch", "Sun", "Structure"),
                level=40,
                does="Always active: a glamour that makes a place look, sound, "
                "smell, feel and even taste like the home her role calls for. "
                "MuIm (Base 5, +3 Structure, +2 Sun, +1 Touch, +1 constant); "
                "four Intricacy points cheapen it.",
            ),
            b.power(
                "Transform Into Human",
                0,
                0,
                "Animal",
                rtd=("Personal", "Sun", "Individual"),
                level=25,
                does="A Personal Power that turns her between her human shape "
                "and her feeding shape. MuCo(An) (Base 10, +2 Sun, +1 Size); "
                "five Intricacy points cheapen it and speed it.",
            ),
        ],
        vis=[BodyVis(4, "Imaginem", "in rats' skulls")],
        equipment="Perfume and a wardrobe.",
        appearance=(
            "Usually a beautiful woman posing as a rich widow or an orphan of "
            "good family who needs a husband, often one driven from her home "
            "by war, which makes the tale ring true. The eyes and the inside "
            "of the mouth of an Arab ghula are always green."
        ),
        notes=paragraphs(
            "A dark faerie jinniyya of the desert, risen from, or wearing "
            "the face of, those who die of thirst there. She weds a strong, "
            "rich man and drinks his blood as he sleeps; with vitality enough "
            "she bears a child that looks like its father but is a ghula too, "
            "born with teeth. By night the ghulas of a city slip out to "
            "feast and drain the dead in the graveyards. In the usual tale "
            "the husband finds them out and destroys the nest but spares his "
            "child, who grows up to lord it over the city and drive him out; "
            "the broken old man then haunts the outskirts warning travellers "
            "of his part in the ruin, and his telling feeds the ghuls' fame. "
            "Another tale makes them the ghosts of harlots given flesh, who "
            "lure weak-willed men to lonely places, put them to sleep and "
            "crush their heads with stones. Male faerie ghuls exist but only "
            "serve the ghulas.",
            "Restricted in daylight; locked into a body though a spirit; not "
            "meant as a player's character. First given in Realms of Power: "
            "Faerie p. 72; this one is the Arab jinniyya, not the European "
            "lamia. The book prints her Might with no Form; its errata "
            "give Corpus. " + PRETENSES,
        ),
    )


# -- ch04 and ch06: the Magic jinn --


def _magic_jinn(cradle: Cradle) -> None:
    b = cradle.b
    _MADE["baghl"] = b.creature(
        "Baghl, the Earth Jinni",
        page="p. 69",
        realm="Magic",
        might=15,
        form="Terram",
        size=2,
        season="Spring",
        confidence=(1, 3),
        tires=False,
        block={
            "characteristics": characteristics(-2, 2, 1, -1, 3, 3, 1, -1),
            "virtues_flaws": [
                "Magic Spirit",
                JINNI,
                _immune("fire"),
                _ways("Mountains"),
                "Second Sight",
                "Skinchanger",
                "Strong-Willed",
                "Tough",
                "Greater Malediction",
                "Magical Air",
                ("Vulnerable Magic", {"condition": "the muezzin's call"}),
                "Reclusive",
                "Focus Power",
                *_times("Greater Power", 2),
                *_times("Improved Abilities", 3),
                *_times("Lesser Power", 2),
                vf_minor("Improved Characteristics"),
            ],
            "abilities": [
                ("Living Language: Arabic", 5, "stone"),
                ("Athletics", 3, "climbing"),
                ("Great Weapon", 4, "maul"),
                ("Profession: Miner", 3, "gemstones"),
                ("Second Sight", 4, "jinn"),
                ("Theology: Islam", 3, "jinn"),
            ],
            "traits": {"Reclusive": 5, "Immutable": 3, "Proud": 2},
        },
        attacks=[b.attack("Maul (warhammer)", -1, 11, 3, 15)],
        soak=10,
        powers=[
            b.power(
                "Flesh to Stone",
                2,
                -4,
                "Terram",
                rtd=("Touch", "Sun", "Individual"),
                level=35,
                does="Turns a person he touches to stone until sunrise or the "
                "dawn call to prayer (Base 20, +1 Touch, +2 Sun); three Mastery "
                "points cheapen it.",
            ),
            b.power(
                "Ruler of Earth",
                1,
                0,
                "Terram",
                level=15,
                does="His Focus Power: any non-Ritual Perdo or Rego Terram "
                "effect up to level 15, at 1 Might point a magnitude (1 to 3).",
            ),
            b.power(
                "Incorporeal",
                0,
                0,
                "Mentem",
                does="Always active: by nature unseen and untouchable, beyond "
                "the reach of the physical world. Magic can aim at him only if "
                "the caster can sense him. In this state he has no physical "
                "scores, and uses his physical Characteristics only against "
                "other bodiless beings.",
            ),
            b.power(
                "Donning the Corporeal Veil",
                2,
                1,
                "Corpus",
                does="Makes the body described under Appearance, with its "
                "arms and armour, its Size, combat scores and wounds. It never "
                "tires and lasts until he lets it go; killing it does not kill "
                "him.",
            ),
            b.power(
                "Presence",
                0,
                0,
                "Mentem",
                does="Always active: he knows everything that happens in his "
                "haunt. It must penetrate to sense anyone with Magic "
                "Resistance.",
            ),
        ],
        vis=[BodyVis(3, "Terram", "in his body, if he is slain in the flesh")],
        appearance=(
            "A fat man with a mule's head, eyes like pupilless jet and limbs "
            "seamed with quartz, swinging a huge maul. In the flesh he can "
            "also take the shape of a big black mule."
        ),
        notes=paragraphs(
            "The jinni of a dark cave in the Elburz mountains, quarried once "
            "until he drove the miners away. Leaving him to admire his fine "
            "rock formations mostly keeps him calm, and now and then he will "
            "talk with scholars of theology. He knows Islam fairly well and "
            "may feign the faerie jinn's weakness to folk rites, though only "
            "the muezzin's call truly harms him. His haunt is an Arcane "
            "Connection to him (+1 to the Penetration multiplier); better "
            "ones come only from his body. His cave gives 1 pawn of Terram "
            "vis a year, a quartz-crusted stalactite at its back (the cave's "
            "vis, not his).",
        ),
    )
    _MADE["zawbaa"] = b.creature(
        "Zawba'a, Whirlwind of the Desert",
        page="p. 103",
        realm="Magic",
        might=18,
        form="Terram",
        season="Summer",
        confidence=(1, 3),
        tires=False,
        how_many="one whirlwind to a stretch of desert",
        block={
            "characteristics": characteristics(-2, -1, -3, -1, 3, 3, 2, 2),
            "virtues_flaws": [
                "Magic Spirit",
                JINNI,
                _immune("heat"),
                _ways("Desert"),
                "Berserk",
                "Keen Vision",
                "Second Sight",
                "Wilderness Sense",
                "Blatant Magical Air",
                "Driven (Major)",
                "Greater Malediction",
                "Magical Air",
                ("Baneful Circumstances", {"circumstance": "touching iron"}),
                *_times("Greater Power", 3),
                "No Fatigue",
                *_times("Improved Attack", 2),
                *_times("Improved Initiative", 2),
                *_times("Improved Soak", 2),
            ],
            "abilities": [
                ("Living Language: Arabic", 5, "abuse"),
                ("Athletics", 2, "sprint"),
                ("Awareness", 2, "potential victims"),
                ("Bargain", 1, "magical bargains"),
                ("Brawl", 5, "clawing wind"),
                ("Area Lore: Desert", 3, "trade routes"),
                ("Folk Ken", 1, "wizards"),
                ("Hunt", 3, "tracking"),
                ("Penetration", 3, "Corpus"),
                ("Second Sight", 4, "invisible things"),
                ("Survival", 3, "deserts"),
                ("Theology: Islam", 1, "jinn"),
                ("Wilderness Sense", 3, "deserts"),
            ],
            "traits": {
                "Angry": 2,
                "Vicious": 3,
                "Merciless": 2,
                "Bloodthirsty (Strength)": 3,
            },
        },
        attacks=[b.attack("Clawing wind", 8, 12, 8, 6)],
        soak=7,
        powers=[
            b.power(
                "Donning the Corporeal Veil",
                0,
                1,
                "Terram",
                does="Takes a body (Size +1) so it can strike foes; a Greater "
                "Power (Realms of Power: Magic p. 102).",
            ),
            b.power(
                "Flay",
                0,
                1,
                "Corpus",
                rtd=("Touch", "Momentary", "Individual"),
                level=20,
                does="Its touch tears the skin half off a foe, who takes a "
                "Heavy Wound. A Greater Power, its Mastery points spent on "
                "cost, speed and Penetration.",
            ),
            b.power(
                "Presence",
                0,
                0,
                "Imaginem",
                does="Always active: it knows all that passes in its haunt, "
                "which may be as large as a Structure (Realms of Power: Magic "
                "p. 103).",
            ),
        ],
        vis=[
            BodyVis(3, "Terram", "in the little whirl of black sand it leaves"),
            BodyVis(1, "Auram", "in the little whirl of black sand it leaves"),
        ],
        appearance=(
            "In the flesh, a pillar of sand some eight feet tall spinning "
            "fast, with a spiteful, bloodthirsty face chuckling at its heart."
        ),
        notes=paragraphs(
            "A jinni of the Arabian sands that loves to kill whoever crosses "
            "its path. It knows only the head-on charge, so it is easily "
            "outwitted. Its Bloodthirsty trait is Essential and is counted in "
            "its attack; Flay adds to the harm. Some seasoned sahirs strike "
            "bargains with zawba'a and bind them as khadims, riding them "
            "across the land as whirling sandstorms, a sight that awes even "
            "great princes.",
        ),
    )
    _MADE["ighraq"] = b.creature(
        "Ighraq al-Siq, the Drowning Flood of the Gorge",
        page="p. 130",
        realm="Magic",
        might=40,
        form="Aquam",
        size=5,
        season="Autumn",
        confidence=(1, 3),
        tires=False,
        block={
            "characteristics": characteristics(1, 2, 2, 0, 9, 2, 1, -3),
            "virtues_flaws": [
                "Magic Spirit",
                JINNI,
                "Magical Monster",
                _ways("River"),
                *_times("Improved Characteristics", 2),
                "Large",
                "Second Sight",
                ("Nature Lore", {"nature": "Water"}),
                "Wrathful (Major)",
                "Infamous",
                "Poor Memory",
                "Focus Power",
                *_times("Greater Power", 5),
                *_times("Lesser Power", 2),
                *_times("Ritual Power", 3),
                *_times("Huge", 3),
                *_times("Improved Might", 5),
                *_times("Improved Powers", 5),
                "Blatant Magical Air",
                "Limited Movement",
                "Restriction",
                ("Baneful Circumstances", {"circumstance": "not touching water"}),
                ("Restricted Power", {"power": "Drown, in floodwave form only"}),
                (
                    "Restricted Power",
                    {"power": "Grant Wilding, only to those with Water Lore"},
                ),
                ("Slow Power", {"power": "Transform into Floodwave"}),
                ("Slow Power", {"power": "Donning the Corporeal Veil"}),
            ],
            "abilities": [
                ("Living Language: Arabic", 2, "water"),
                ("Living Language: Aramaic", 5, "water"),
                ("Area Lore: Tigris", 5, "floods"),
                ("Area Lore: Zab", 6, "history"),
                ("Brawl", 6, "bludgeon"),
                ("Great Weapon", 3, "lance"),
                ("Penetration", 4, "wards"),
                ("Second Sight", 4, "jinn"),
                ("Swim", 6, "leaping out of the water"),
                ("Theology: Islam", 2, "jinn"),
                ("Water Lore", 6, "rivers"),
            ],
            "traits": {"Wrathful": 5, "Proud": 3, "Fickle": 2, "Flood": 3},
            "reputations": {"Mad river (local)": 4},
        },
        attacks=[
            b.attack("Bludgeon (floodwave form)", -3, 8, 2, 11),
            b.attack("Lance", 0, 8, 2, 16),
        ],
        soak=6,
        powers=[
            b.power(
                "Crafter of Water",
                1,
                0,
                "Aquam",
                level=40,
                does="His Focus Power: any non-Ritual Creo or Rego Aquam "
                "effect up to level 40, at 1 Might point a magnitude (1 to 8). "
                "He may use a Range of the waterway (as Sight) and a Target of "
                "the body of water (as Structure), reaching anyone on or in his "
                "reach of the river, or the whole Zab (Realms of Power: Magic "
                "p. 43). Three Mastery points raise its level by 15.",
            ),
            b.power(
                "Drown",
                0,
                -2,
                "Aquam",
                level=30,
                does="In floodwave form only: after a melee blow lands he "
                "swallows a foe smaller than himself, who must roll against "
                "deprivation (ArM5 pp. 180-181) and may struggle free each "
                "round by the grappling rules (ArM5 p. 174).",
            ),
            b.power(
                "Donning the Corporeal Veil",
                2,
                1,
                "Corpus",
                level=35,
                does="Takes the body under Appearance, with its arms, armour, "
                "combat scores and wounds; it never tires and lasts until he "
                "lets it go, and killing it does not kill him. Slow: it needs "
                "an extra round to prepare.",
            ),
            b.power(
                "Grant Water Lore",
                5,
                -13,
                "Vim",
                does="Gives someone the Minor Mystery Virtue Water Lore, for a "
                "while or for good (Houses of Hermes: Mystery Cults "
                "pp. 103-104). His canyon is a source of Quality 4; a magus who "
                "talks the spiteful jinni into teaching him learns as from a "
                "teacher, at Quality 9.",
            ),
            b.power(
                "Grant Wilding",
                10,
                -23,
                "Vim",
                does="Gives the Major Mystery Virtue Wilding to someone who "
                "already has a Water Lore score, for a while or for good "
                "(Houses of Hermes: Mystery Cults pp. 105-106).",
            ),
            b.power(
                "Presence",
                0,
                0,
                "Mentem",
                level=35,
                does="Always active once he is loose: he knows all that "
                "happens in his haunt; it must penetrate to sense anyone with "
                "Magic Resistance.",
            ),
            b.power(
                "Transform into Floodwave",
                4,
                -4,
                "Aquam",
                level=45,
                does="Becomes a flood that seems to draw on the river's own "
                "water. Slow: it needs an extra round to prepare.",
            ),
        ],
        vis=[BodyVis(8, "Aquam", "in smooth stones of many hues, if he is slain")],
        appearance=(
            "A lean giant with blue-green skin and lank green-black hair "
            "like river weed, bearing a great spear and a vest of "
            "water-worn stones. Once manifest he can break into his favourite "
            "shape, a flood full of hurtling stones that runs up or down the "
            "watercourse. A Deluge of Rushing and Dashing in that narrow "
            "gorge is terrible."
        ),
        notes=paragraphs(
            "An old pagan spirit of the Tigris, once free along its length "
            "and now held to one stretch of the Lesser Zab, the Siq "
            "al-Majnun or Jinni's Gorge, where his spring floods burst "
            "through the narrow canyon (a Magic aura of 6). He shrinks from "
            "even setting foot on the banks. He is sealed in a carved stone "
            "block at the gorge, as some lost cities' gates are guarded: "
            "while sealed he can do nothing and is hidden in the native "
            "rock, which takes his Magic Resistance; the ground about it is "
            "an Arcane Connection to him (+1 to the Penetration multiplier, "
            "+3 to someone touching the block barefoot). His gorge gives 2 "
            "pawns of Aquam a year, rainwater gathering in a niche of that "
            "block (the gorge's vis).",
            "Built as an Autumn character by Realms of Power: Magic, from a "
            "base Might of 35 raised to 40 by Improved Might, and not meant "
            "to be balanced. He has a True Name like any jinni but no Daimon "
            "Virtue. His Flood trait is Essential; Water Lore is his Nature "
            "Lore Virtue. The block gives his Might no Form: the pack takes "
            "Aquam. A Faerie or Infernal version, or one of Auram or Terram "
            "with a Might of 20 to 25, can be made from him.",
        ),
    )


# -- ch06: Arabia --


def _arabia(cradle: Cradle) -> None:
    b = cradle.b
    _MADE["nisnas"] = b.creature(
        "Nisnas",
        page="p. 116",
        realm="Magic",
        might=10,
        form="Corpus",
        size=-1,
        season="Summer",
        confidence=(1, 3),
        how_many="many, in the forests of Yemen and Hadramawt",
        block={
            "characteristics": characteristics(0, 1, -3, 0, 0, 2, 2, 3),
            "virtues_flaws": [
                "Magic Human",
                "Magical Monster",
                ("Essential Virtue (Major)", {"trait": "Fast (Leaping)"}),
                _ways("Forests"),
                "Keen Vision",
                "Long-Winded",
                "Sharp Ears",
                ("Voice of the {land}", {"land": "Forest"}),
                "Wilderness Sense",
                "Enemies",
                "Compulsion (Minor)",
                "Missing Eye",
                "Missing Hand",
                "Small Frame",
                "Greater Power",
                *_times("Improved Defense", 2),
                *_times("Improved Fatigue", 2),
                *_times("Improved Initiative", 2),
                *_times("Improved Soak", 2),
                "Monstrous Appearance",
                "Susceptible to Deprivation",
            ],
            "abilities": [
                ("Living Language: Arabic", 4, "listening in"),
                ("Athletics", 5, "leaping"),
                ("Awareness", 3, "ambushes"),
                ("Brawl", 3, "fist"),
                ("Concentration", 2, "jumping"),
                ("Folk Ken", 2, "peasants"),
                ("Area Lore: Hadramawt", 3, "forests"),
                ("Hunt", 3, "tracking"),
                ("Stealth", 3, "sneak"),
                ("Survival", 3, "forests"),
                ("Wilderness Sense", 3, "forests"),
            ],
            "traits": {
                "Cautious": 1,
                "Curious": 3,
                "Skittish": 2,
                "Fast (Leaping)": 6,
            },
        },
        attacks=[b.attack("Fist", 6, 2, 8, -3)],
        soak=6,
        powers=[
            b.power(
                "Hop like the Wind",
                0,
                5,
                "Corpus",
                rtd=("Personal", "Sun", "Individual"),
                level=20,
                does="Huge bounds that carry it swiftly over the ground, like "
                "the Gift of the Frog's Legs but with a great leap every "
                "round. A Greater Power, cheapened and speeded.",
            ),
        ],
        vis=[BodyVis(2, "Corpus", "in its foot")],
        appearance=(
            "A small man split down the middle: a faceless half head, one "
            "side of a body with a single arm and leg, a sheep's tail, and "
            "half a face sunk into its chest."
        ),
        notes=paragraphs(
            "A shy, harmless wild thing that seems to come from Hadramawt, "
            "whose people find its flesh sweet and hunt it for the pot; its "
            "Enemies Flaw is theirs. It can talk, and stories tell of "
            "nisnases who pleaded for their lives before they were killed. "
            "Its curiosity is a Compulsion; Fast (Leaping) is its Essential "
            "Trait.",
        ),
    )
    _MADE["giant_of_ad"] = b.creature(
        "Giant of 'Ad",
        page="p. 119",
        realm="Magic",
        might=20,
        form="Corpus",
        size=7,
        season="Autumn",
        confidence=(1, 3),
        how_many="a people, in regiones deep in the deserts of 'Uman",
        block={
            "characteristics": characteristics(0, 2, -1, -1, 13, 0, 1, -4),
            "virtues_flaws": [
                "Magic Human",
                "Improved Characteristics",
                "Magical Champion",
                _ways("Desert"),
                "Pagan (Major)",
                ("Anchored to the {land}", {"land": "Desert"}),
                "Animal Companion",
                ("Offensive to {being}", {"being": "spirits"}),
                *_times("Gigantic", 6),
                "Focus Power",
                "Monstrous Appearance",
                "Acclimation Prone",
                "Susceptible to Deprivation",
            ],
            "abilities": [
                ("Animal Handling", 2, "falconry"),
                ("Area Lore: Arabia", 6, "cities"),
                ("Dead Language: 'Adid", 5, "ancient"),
                ("Bargain", 3, "payment for services"),
                ("Brawl", 2, "stomp"),
                ("Craft: Stonemason", 6, ""),
                ("Magic Lore", 4, "Arabia"),
                ("Survival", 3, "desert"),
            ],
            "traits": {"Proud": 2, "Focused": -1},
        },
        attacks=[
            b.attack("Chisel (as knife)", -4, 3, -2, 15),
            b.attack("Stomp (kick)", -5, 4, -1, 16),
        ],
        soak=3,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Stonesmith",
                1,
                -4,
                "Terram",
                level=20,
                does="His Focus Power: any non-Ritual Creo, Intellego or Muto "
                "Terram effect on stone up to level 20, at 1 Might point a "
                "magnitude (1 to 4).",
            ),
        ],
        vis=[
            BodyVis(1, "Corpus", "in his heart"),
            BodyVis(1, "Terram", "in his left hand"),
            BodyVis(1, "Terram", "in his right hand"),
        ],
        equipment="Mason's tools, Bedouin robes the colour of sand.",
        appearance=(
            "Over thirty feet tall, yet far more civilised than Europe's "
            "rough giants. Giants of 'Ad love falcons and other hawks, and "
            "one usually nests in a giant's long hair or beard."
        ),
        notes=paragraphs(
            "The giants of southern Arabia, of the line of great 'Ad and of "
            "Noah's third son: huge magical beings older than Islam who have "
            "kept to Magic regiones in the deep desert since they lost their "
            "masterpiece, the City of a Thousand Pillars. They are not "
            "deathless, and weaken if they stay long away from strong "
            "desert Magic auras (Anchored to the Desert). Now and then one "
            "comes out to sell his building craft to sorcerers and emirs, "
            "asking in return for hints of how to live for ever.",
            "Balanced as a powerful starting companion: 295 experience "
            "points for Abilities and 5 free Virtue points, matched by 5 of "
            "Flaws. His falcon (his Animal Companion) may be mundane or "
            "magical, scaled up as far as Size +3.",
        ),
    )


# -- ch07: Mesopotamia --


def _mesopotamia(cradle: Cradle) -> None:
    b = cradle.b
    _MADE["aladlammu"] = b.creature(
        "Aladlammu and Apsasu",
        page="p. 120",
        realm="Faerie",
        might=30,
        form="Animal",
        size=4,
        confidence=(1, 3),
        tires=False,
        how_many="a pair: the male aladlammu and the female apsasu",
        block={
            "characteristics": characteristics(1, 1, 1, 1, 8, 2, 2, -2),
            "virtues_flaws": [
                *_times("Huge", 3),
                "Greater Power",
                "Increased Faerie Might (Major)",
                _major("Greater Immunity to Disease"),
                "Ritual Power",
                "Faerie Speech",
                *_times("Improved Characteristics", 2),
                "Improved Damage",
                *_times("Improved Soak", 3),
                *_times("Increased Faerie Might (Minor)", 2),
                "Hybrid Form",
                "Lesser Power",
                "Positive Folktales",
                "Second Sight",
                "Compassionate (Major)",
                _ward("Sovereign Ward", "a special amulet"),
                "Supernatural Nuisance",
                "Incognizant",
            ],
            "abilities": [
                ("Awareness", 3, "alertness"),
                ("Brawl", 7, "hooves"),
                ("Chirurgy", 2, "heatstroke"),
                ("Folk Ken", 4, "spotting the possessed"),
                ("Infernal Lore", 4, "disease spirits"),
                ("Second Sight", 5, "demons"),
            ],
            "traits": {"Hatred for demons": 3, "Helpful": 2},
            "reputations": {"Foe of Demons (local)": 2},
        },
        attacks=[b.attack("Trample", 0, 12, 8, 14)],
        soak=8,
        powers=[
            b.power(
                "Burn the Filthy Spirit",
                0,
                -5,
                "Vim",
                rtd=("Eye", "", ""),
                level=10,
                does="Meeting a demon's eye, by sight or Second Sight, strips "
                "it of 15 Might. PeVi (Base 5, +1 Eye); a Lesser Power, "
                "cheapened and speeded.",
            ),
            b.power(
                "Repel the Nightstalking Spirit",
                1,
                -4,
                "Vim",
                level=30,
                does="Makes a room or a patch of clear ground safe: if the "
                "power penetrates, no demon of Infernal Might 25 or less can "
                "enter. Where no boundary exists the beast must mark an "
                "unbroken line, which need not be a circle. ReVi (Base 25, +1 "
                "for the unusual Target); a Greater Power, cheapened, with 10 "
                "experience points of Penetration.",
            ),
            b.power(
                "Restoration of the Defiled Body",
                3,
                -11,
                "Corpus",
                rtd=("Touch", "", ""),
                level=25,
                does="As the spell of that name (ArM5 p. 129). A Ritual Power, "
                "so it costs a permanent point of Might Score as well as Might "
                "points. CrCo (Base 20, +1 Touch), with 15 experience points "
                "of Penetration.",
            ),
        ],
        vis=[BodyVis(6, "Animal", "in its hooves")],
        appearance=(
            "A mighty bull with vast wings and a bearded man's head; the "
            "apsasu has a woman's head. Sparks fly when their hooves strike "
            "a foe."
        ),
        notes=paragraphs(
            "Guardians made by the old gods, male and female, sworn enemies "
            "of harmful spirits and above all the galla, the disease "
            "demons that plague them (their Supernatural Nuisance). The same "
            "beings with winged human bodies to match their heads are the "
            "shedu (male) and lamassu (female). Huge statues of them stand "
            "in many great ruins, and a district lucky enough to have one "
            "can call on the faerie when disease or demons strike. Someone "
            "with the right Area Lore and Faerie Lore can make the amulet "
            "that is their Sovereign Ward (Realms of Power: Faerie p. 52). "
            "Not meant as player characters. " + PRETENSES,
        ),
    )
    _MADE["girtablullu"] = b.creature(
        "Girtablullu, the Scorpion-Man",
        page="p. 122",
        realm="Magic",
        might=17,
        form="Animal",
        size=1,
        season="Summer",
        confidence=(1, 3),
        encumbrance="0 (3)",
        how_many="small bands, each a Trained Group, at old ruins",
        block={
            "characteristics": characteristics(-1, 1, 0, -2, 3, 2, 3, 4),
            "virtues_flaws": [
                "Magic Human",
                _ways("Desert"),
                vf_great("Quickness"),
                "Greater Malediction",
                "Dutybound",
                "Improved Abilities",
                *_times("Improved Attack", 2),
                *_times("Improved Characteristics", 4),
                "Improved Damage",
                *_times("Improved Might", 2),
                "Improved Powers",
                *_times("Improved Soak", 2),
                "Lesser Power",
                vf_minor("Large"),
            ],
            "abilities": [
                ("Living Language: Arabic", 1, "Maslawi"),
                ("Athletics", 4, "over sand"),
                ("Awareness", 3, "interlopers"),
                ("Dead Language: Babylonian", 5, "orders"),
                ("Brawl", 5, "sting"),
                ("Bows", 5, "longbow"),
                ("Hunt", 2, "thieves"),
                ("Leadership", 3, "scorpion-men"),
                ("Area Lore: Local", 1, "hiding places"),
                ("Penetration", 3, "Venom power"),
                ("Stealth", 3, "ruins"),
            ],
            "traits": {"Fiercely Protective": 3},
        },
        attacks=[
            b.attack("Bow", 5, 20, 13, 11),
            b.attack("Sting", 9, 15, 15, 9),
        ],
        soak=12,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Venom",
                0,
                0,
                "Corpus",
                rtd=("Touch", "", ""),
                level=20,
                does="The tail's sting: anyone struck needs a Stamina roll of "
                "9+ or takes a Heavy Wound. The sting is a weapon, so the power "
                "has no Initiative of its own. PeCo (Base 15, +1 Touch); a "
                "Lesser Power, cheapened, with 10 experience points of "
                "Penetration.",
            ),
        ],
        vis=[BodyVis(3, "Perdo", "in its sting")],
        equipment=(
            "A bow with eleven arrows in the quiver; lamellar armour, as full "
            "metal-reinforced leather."
        ),
        appearance=(
            "A warrior above the waist, long-haired, with a plaited beard; "
            "below, the glossy black shell of a scorpion with its long, "
            "stinging tail, standing on two clawed legs like a bird's. It "
            "carries a bow. Some have wings like a bird's."
        ),
        notes=paragraphs(
            "One of the eleven monster-races Tiamat bore to destroy the young "
            "gods, taken into the gods' service after Marduk slew her. The "
            "gods made the scorpion-men guardians of monuments and holy "
            "places, and they belong above all to Shamash the sun god, so "
            "explorers of old ruins meet them. Their totals include +3 from "
            "Ways of the Desert; Fiercely Protective is an Essential Trait. "
            "They are strongest by day: at night they suffer Poor Eyesight, "
            "No Sense of Direction and Clumsy (their Greater Malediction).",
        ),
    )
    _MADE["mushhushshu"] = b.creature(
        "Mushhushshu, the Snake-Dragon",
        page="p. 123",
        realm="Magic",
        might=25,
        form="Animal",
        size=3,
        season="Summer",
        confidence=(1, 3),
        cunning=False,
        block={
            "characteristics": characteristics(2, 0, 2, 0, 6, 2, 1, -1),
            "virtues_flaws": [
                "Magic Animal",
                "Arcane Lore",
                "Clear Thinker",
                "Keen Vision",
                "Lightning Reflexes",
                "Piercing Gaze",
                "Strong-Willed",
                "Tough",
                "Proud (Major)",
                "Wanderlust",
                "Infamous",
                "Gigantic",
                _major("Greater Immunity to Poison"),
                "Greater Power",
                "Gift of Speech",
                *_times("Improved Abilities", 2),
                *_times("Improved Attack", 2),
                *_times("Improved Powers", 2),
                *_times("Improved Soak", 2),
                *_times("Lesser Power", 2),
                vf_minor("Desert Regio Network"),
                vf_minor("Large"),
                vf_minor("Lesser Immunity to Arrows"),
                vf_minor("Puissant Brawl"),
                vf_minor("Second Sight"),
            ],
            "abilities": [
                ("Living Language: Arabic", 4, "Maslawi"),
                ("Area Lore: Assyria", 4, "magical places"),
                ("Awareness", 3, "invaders"),
                ("Dead Language: Babylonian", 5, "Assyrian"),
                ("Brawl", 6, "bite"),
                ("Concentration", 3, "Eye of the Serpent"),
                ("Hunt", 4, "interlopers"),
                ("Infernal Lore", 3, "local demons"),
                ("Intrigue", 3, "politics"),
                ("Faerie Lore", 2, "servants of deities"),
                ("Magic Lore", 4, "local spirits"),
                ("Area Lore: Mesopotamia", 4, "Old Babylonia"),
                ("Penetration", 4, "Voice of Regal Authority"),
                ("Second Sight", 4, "spirits"),
            ],
            "traits": {"Vain": 6, "Aloof": 2, "Thirst for Knowledge": 2},
            "reputations": {"Violent against Foreigners (local)": 2},
        },
        attacks=[
            b.attack("Bite", -1, 18, 9, 9),
            b.attack("Claws", -1, 14, 10, 10),
        ],
        soak=15,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Assessing Gaze",
                1,
                -10,
                "Corpus",
                rtd=("Eye", "", "Group"),
                level=25,
                does="Picks out which of a band of people threatens it most, "
                "usually the best fighter; it also notices that magic is "
                "present, though not how strong. InCo(Vi) (Base 5, +1 Eye, +2 "
                "Group, +1 requisite); a Lesser Power, cheapened and speeded.",
            ),
            b.power(
                "Voice of Regal Authority",
                1,
                0,
                "Mentem",
                rtd=("", "Sun", "Sound"),
                level=35,
                does="Always active: whoever hears its voice feels a strong "
                "urge to do as it says. ReMe (Base 5, +2 Sun, +3 Sound, +1 "
                "constant); a Greater Power, cheapened.",
            ),
            b.power(
                "Eye of the Serpent",
                1,
                -6,
                "Corpus",
                rtd=("Eye", "Concentration", "Individual"),
                level=15,
                does="Holds a person rooted by a look. ReCo (Base 5, +1 Eye, "
                "+1 Concentration); a Lesser Power, cheapened and speeded.",
            ),
        ],
        vis=[BodyVis(5, "Vim", "in its horns")],
        appearance=(
            "A long snake's body on four legs like a dragon's, the front "
            "pair a lion's and the hind pair an eagle's; its head bears horns "
            "and a fine crest."
        ),
        notes=paragraphs(
            "One of Tiamat's monster-races, given after her death to "
            "Ashshur, Assyria's god, whose priests could call and command "
            "them; yatus of Harran may still know how. Uncalled, they wander "
            "the hills and desert edges of old Assyria from one Magic aura "
            "or regio to the next (Desert Regio Network, Realms of Power: "
            "Magic p. 45). One will attack armed foreigners within Assyria's "
            "old borders, but news or knowledge worth hearing can stay it. "
            "Before a fight it uses Assessing Gaze to choose whom to fix "
            "with Eye of the Serpent; its sinuous body lets it bite and claw "
            "in one round. Brawl 6 gains +2 from Puissant Brawl.",
        ),
    )


# -- ch08: Persia --


def _persia(cradle: Cradle) -> None:
    b = cradle.b
    _MADE["nasu"] = b.creature(
        "Nasu Spirit",
        page="p. 142",
        realm="Magic",
        might=5,
        form="Animal",
        size=-12,
        season="Spring",
        cunning=True,
        how_many="a swarm, as large as the corpses it has fed on",
        block={
            "characteristics": characteristics(0, 1, 0, 0, -20, 0, 3, 10),
            "virtues_flaws": [
                "Magic Spirit",
                "Magic Sensitivity",
                *_times("Greater Power", 2),
                "Ritual Power",
                *_times("Improved Damage", 10),
                "Improved Powers",
                *_times("Miniature", 5),
            ],
            "abilities": [
                ("Athletics", 3, "flying"),
                ("Awareness", 3, "corpses"),
                ("Brawl", 3, "biting"),
                ("Magic Sensitivity", 3, "wizards"),
            ],
            "traits": {"Hungry": 6},
        },
        attacks=[b.attack("Swarm bite", 10, 7, 0, 10)],
        soak=0,
        powers=[
            b.power(
                "Donning the Corporeal Veil",
                0,
                9,
                "Animal",
                rtd=("Touch", "Sun", ""),
                level=25,
                does="Takes a body, which it may drop at any time; a nasu "
                "seldom leaves the world while there are corpses left to eat. "
                "Cr(Re)An (Base 5, +1 Touch, +2 Sun, +1 requisite); a Greater "
                "Power, cheapened and speeded.",
            ),
            b.power(
                "Corpse-Feeding",
                3,
                8,
                "Animal",
                rtd=("Touch", "", "Group"),
                level=25,
                does="A Ritual Power. A nasu that crawls into an opening of a "
                "corpse comes out three rounds later as ten, each its double "
                "with this power too, though a swarm of any size holds only "
                "one pawn of vis. Every three rounds a swarm can grow by 3 "
                "Size, as far as the corpses allow; growing, it attacks the "
                "living and makes more corpses. CrAn(Vi) (Base 5, +1 Touch, +2 "
                "Group, +1 requisite).",
            ),
            b.power(
                "Swarm Form",
                0,
                0,
                "Animal",
                does="A Greater Power with no Hermetic match. A nasu fights "
                "only as a swarm, which must be the Size of its foe or more: "
                "a hundred thousand (Size +3) can take on an ordinary group of "
                "people. Weapons cannot kill it; only area effects such as "
                "fire or smoke, each fifth of the swarm caught costing it 1 "
                "Might point.",
            ),
        ],
        vis=[BodyVis(1, "Animal", "in its body (one pawn for a whole swarm)")],
        appearance=(
            "A fly three inches long with a red and yellow striped belly, "
            "buzzing horribly in flight."
        ),
        notes=paragraphs(
            "A Persian magical spirit, not a jinni, drawn to fresh corpses, "
            "most of all those of magical beasts and sorcerers. It seldom "
            "takes flesh unless called, and is so slight that any apprentice "
            "can call one, which is why masters warn never to: with enough "
            "fresh meat, one nasu becomes millions within minutes. Sihr "
            "cannot call it, though (Spirit) Summoning can. Its swarm cannot "
            "be parried, only dodged (its Defense is n/a, entered as 0). "
            "Gluttonous, which the catalog lacks, is left out; Hungry is its "
            "Essential Trait. Its wound ranges "
            "are 1, 2, 3, 4 and 5 or more.",
        ),
    )
    _MADE["hyrcanian_tiger"] = b.creature(
        "Hyrcanian Tiger",
        page="p. 153",
        realm="Magic",
        might=10,
        form="Animal",
        season="Spring",
        cunning=True,
        confidence=(1, 3),
        tires=False,
        how_many="lone hunters of Mazandaran and Persia's northern desert",
        block={
            "characteristics": characteristics(1, 0, -2, -5, 0, 1, 2, 5),
            "virtues_flaws": [
                "Magic Animal",
                ("Affinity with {ability}", {"ability": "Athletics"}),
                "Improved Characteristics",
                vf_puissant("Athletics"),
                "Proud (Minor)",
                "No Fatigue",
                *_times("Improved Abilities", 3),
                "Improved Attack",
                *_times(vf_minor("Great Quickness"), 2),
                "Personal Power",
                "Crafty",
                "Fast Runner",
                "Pursuit Predator",
                "Tireless",
            ],
            "abilities": [
                ("Athletics", 6, "running"),
                ("Awareness", 3, "gazelle"),
                ("Brawl", 5, "bite"),
                ("Area Lore: Dasht-i Kavir", 2, "oases"),
                ("Hunt", 4, "gazelle"),
                ("Survival", 3, "semi-desert"),
            ],
            "traits": {"Vain": 5, "Swift": 3, "Brave": 1},
        },
        attacks=[
            b.attack("Bite", 5, 11, 12, 1),
            b.attack("Trip", 4, 11, 13, None),
        ],
        soak=2,
        powers=[
            b.power(
                "Swiftness of Thought",
                1,
                4,
                "Animal",
                level=20,
                does="It is fast by nature, but for a Might point it covers "
                "500 paces more in one round. ReAn (Base 20, as for ReCo); a "
                "Personal Power, cheapened.",
            ),
        ],
        vis=[BodyVis(2, "Animal", "in its feet")],
        appearance=(
            "A long-legged tawny cat some seven feet long with its three-foot "
            "tail, weighing about 150 pounds. Mythic Europe's tigers are "
            "spotted, not striped, though a saga may have stripes."
        ),
        notes=paragraphs(
            "Named for its arrow-swift running, it lends its name to the "
            "Tigris. Persia's old kings kept these tigers as pets, and nobles "
            "still pay hunters to steal cubs for training; a pursuing "
            "tigress can be fooled with glass balls, taking her reflection "
            "for her cub. It eats its prey, mostly gazelle, from its nature "
            "though as a magic beast it need not.",
            "It has +3 to every roll for running; Athletics 6 gains +2 from "
            "Puissant Athletics, and Swift is an Essential Trait. A Trip "
            "that beats the foe's Defense by 3 knocks him down. More than "
            "twice as fast as the swiftest horse even unaided, it keeps that "
            "pace only a round or two and cannot turn sharply at speed, so "
            "prey escapes by dodging and weaving. For a mundane tiger, drop "
            "the Might, Magical Qualities, powers and vis; it then tires "
            "(Tireless).",
        ),
    )
    _MADE["simurgh"] = b.creature(
        "The Simurgh",
        page="p. 154",
        realm="Faerie",
        might=50,
        form="Animal",
        size=9,
        tires=False,
        block={
            "characteristics": characteristics(1, 2, 0, 1, 15, 3, 1, 0),
            "virtues_flaws": [
                "External Vis (Major)",
                *_times("Huge", 8),
                "Faerie Beast",
                "Faerie Sight",
                "Faerie Speech",
                "Focus Power",
                _immune("bludgeoning weapons"),
                _immune("slashing weapons"),
                _immune("piercing weapons"),
                *_times("Improved Characteristics", 9),
                *_times("Improved Powers", 6),
                "Positive Folktales",
                "Reputation as Confidence",
                *_times("Ritual Power", 3),
                "Compassionate (Major)",
                "Incognizant",
                "Traditional Ward",
            ],
            "abilities": [
                ("Area Lore: Arabia", 5, "wars"),
                ("Area Lore: Persia", 8, "legendary figures"),
                ("Area Lore: Transoxiana", 5, "peoples"),
                ("Artes Liberales", 8, "Persian literature"),
                ("Athletics", 5, "flying"),
                ("Awareness", 4, "wrongdoers"),
                ("Brawl", 5, "claws"),
                ("Philosophiae", 8, "natural sciences"),
                ("Survival", 6, "mountains"),
                ("Teaching", 5, "Area Lore"),
            ],
            "traits": {"Kind": 6, "Curious": 3},
            "reputations": {"Bird of God (local)": 5},
        },
        attacks=[b.attack("Claws", 0, 12, 8, 19)],
        soak=12,
        powers=[
            b.power(
                "Heart of the Whirlwind",
                1,
                -1,
                "Auram",
                level=50,
                does="Her Focus Power: any non-Ritual effect of the winds up "
                "to level 50, at 1 Might point a magnitude (1 to 10); its "
                "Initiative is minus its cost.",
            ),
            b.power(
                "Grant Fertility",
                2,
                -22,
                "Herbam",
                rtd=("Sight", "Year", "Boundary"),
                level=55,
                does="A Ritual Power worked as she flies over the fields: "
                "like The Bountiful Feast, but over ten times the area, and "
                "making beasts fruitful as well as crops. CrHe(An) (Base 1, +3 "
                "Sight, +4 Year, +4 Boundary, +2 Size, +1 Animal requisite), "
                "cheapened by 9 in all.",
            ),
        ],
        vis=[BodyVis(15, "Animal", "in her breast feathers")],
        appearance=(
            "Big enough to carry off an elephant: an eagle with a dog's head "
            "and a lion's claws, her feathers the colour of bright-polished "
            "copper and her peacock's tail patterned in thirty colours."
        ),
        notes=paragraphs(
            "The vast bird of Mount Damavand, who ranges all over Persia; "
            "most Persians have seen her, and her presence strangely "
            "reassures them, for she brings fertility and is the pride of "
            "the nation. She says she has watched the world destroyed three "
            "times, and her long life has made her a sage of many subjects. "
            "In her best-known tale she raised the white-haired Zal, "
            "Rostam's father, left to die in the Alborz by his own father, "
            "and gave him three feathers to summon her when he needed her.",
            "Ordinary weapons barely touch her: only magic weapons or spells "
            "wound her. By her External Vis she may give a worthy person one "
            "of her breast feathers, holding five pawns of Animal vis; each "
            "is an Arcane Connection to her and, thrown into a fire, calls "
            "her in great need. Not designed as a player's character. " + PRETENSES,
        ),
    )
    _MADE["gazelle"] = b.creature(
        "Persian Gazelle",
        page="p. 155",
        size=-1,
        cunning=True,
        how_many="herds, led by a male",
        block={
            "characteristics": characteristics(-2, 1, -4, -4, -2, 3, 1, 3),
            "virtues_flaws": [
                "Improved Abilities",
                "Long-Winded",
                "Well-Traveled",
                "Compassionate (Minor)",
                "Defensive Fighter",
                "Fast Runner",
                "Pack/Herd Leader",
                "Keen Eyesight",
                "Large Horns/Antlers",
                "Herd Animal",
                "Tireless",
            ],
            "abilities": [
                ("Area Lore: Dasht-i Kavir", 4, "finding water"),
                ("Athletics", 4, "running"),
                ("Awareness", 3, "predators"),
                ("Brawl", 4, "dodging"),
                ("Leadership", 5, "gazelles"),
                ("Survival", 3, "semi-desert"),
            ],
            "traits": {"Gentle": 3},
        },
        attacks=[
            b.attack("Horns", 5, 8, 9, 1),
            b.attack("Dodge", 3, None, 10, None),
        ],
        soak=4,
        fatigue_levels=BEAST_FATIGUE,
        appearance=(
            "A small, delicate antelope with a fawn hide and a dark stripe "
            "along each flank; the male's horns are his defence."
        ),
        notes=paragraphs(
            "The ghazal, the dorcas of Western bestiaries, common in Persia's "
            "Dasht-i Kavir. It sees very keenly (+3 to rolls of sight) and "
            "runs fast (+3 to running). Only males have the herd leader's "
            "Quality, the large horns and Leadership, and only a male "
            "fights; when forced to he gains Ferocity for the while, with 3 "
            "temporary Confidence Points.",
        ),
    )
    _MADE["olghoi_khorkhoi"] = b.creature(
        "Olghoi Khorkhoi, the Death Worm",
        page="p. 159",
        realm="Magic",
        might=14,
        form="Animal",
        season="Spring",
        cunning=True,
        how_many="lone worms under the northern deserts of Persia and Transoxiana",
        block={
            "characteristics": characteristics(-1, 1, 0, -5, 2, 3, 3, 1),
            "virtues_flaws": [
                "Magic Animal",
                _ways("Desert"),
                "Improved Characteristics",
                vf_puissant("Stealth"),
                "Tough",
                ("Offensive to {being}", {"being": "animals"}),
                *_times(
                    ("Poor {characteristic}", {"characteristic": "Communication"}), 2
                ),
                "Greater Power",
                _major("Greater Immunity to Fire"),
                "Improved Abilities",
                *_times("Improved Might", 4),
                "Improved Powers",
                *_times("Personal Power", 2),
                "Monstrous Appearance",
                ("Minor Flaw", {"flaw": "Restricted Power"}),
            ],
            "abilities": [
                ("Brawl", 4, "bludgeon"),
                ("Area Lore: Desert", 2, "trails"),
                ("Stealth", 4, "under sand"),
                ("Thrown Weapon", 4, "fiery venom"),
            ],
            "traits": {"Hungry": 6},
            "reputations": {"Death Worm (local)": 2},
        },
        attacks=[
            b.attack("Fiery venom", 6, 11, 9, 30),
            b.attack("Bludgeon (and +10 fire)", 5, 15, 10, 9),
        ],
        soak=10,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Spit Fire",
                1,
                3,
                "Ignem",
                rtd=("Voice", "", ""),
                level=35,
                does="Spits burning venom up to 15 paces on a Thrown Weapon "
                "attack, at -2 beyond 5 paces and -4 beyond 10. Only a shield "
                "parries it, else it must be dodged with Brawl; a hit does +30 "
                "damage. Not usable from June to November (its Restricted "
                "Power). CrIg (Base 25, +2 Voice); a Greater Power, cheapened "
                "and speeded.",
            ),
            b.power(
                "Fiery Touch",
                0,
                0,
                "Ignem",
                rtd=("Touch", "Sun", ""),
                level=30,
                does="Always active: its burning slime adds +10 damage to its "
                "bludgeon and eats metal, so a foe's armour loses a point of "
                "Protection even if he soaks it all. CrIg (Base 5, +1 Touch, "
                "+2 Sun, +1 corrosive, +1 constant); a Personal Power taken "
                "twice, cheapened.",
            ),
        ],
        vis=[BodyVis(3, "Ignem", "in its body")],
        appearance=(
            "A worm five feet long and a foot thick, with no head or tail to "
            "be seen, blood-red mottled with black."
        ),
        notes=paragraphs(
            "The grown form of the worm that causes rishtah, which the Ghuzz "
            "cure by burying the sick limb in hot sand from dawn to dusk "
            "until the worm leaves it; sometimes the worm lives on in the "
            "sand and grows to five feet or more, and the Ghuzz say it falls "
            "on travellers and herds with fiery venom. It moves freely under "
            "the ground and, though blind, feels every tremor. If its Dex + "
            "Stealth beats a victim's Per + Awareness it bursts up beside "
            "him with +3 to Attack in the first round, before Initiative is "
            "rolled. Beasts shy from it by instinct, and horses' alarm is "
            "often the first warning.",
            "Its totals include +3 from Ways of the Desert; Stealth 4 gains "
            "+2 from Puissant Stealth. Gluttonous, which the catalog lacks, "
            "is left out.",
        ),
    )


# -- ch09: the Silk Road --


def _silk_road(cradle: Cradle) -> None:
    b = cradle.b
    _MADE["bactrian_camel"] = b.creature(
        "Bactrian Camel",
        page="p. 170",
        size=2,
        cunning=True,
        confidence=(0, 0),
        how_many="strings of them in every caravan",
        block={
            "characteristics": characteristics(-2, -1, -4, -5, 3, 4, -1, -2),
            "virtues_flaws": ["Long-Winded", "Feral Scent", "Hardy", "Herd Animal"],
            "abilities": [
                ("Athletics", 4, "running"),
                ("Awareness", 3, "predators"),
                ("Brawl", 2, "dodging"),
                ("Survival", 5, "home terrain"),
            ],
            "reputations": {"Ill-tempered beast (Mythic Middle East)": 3},
        },
        attacks=[b.attack("Kick (hooves)", 0, 3, 2, 4)],
        soak=4,
        fatigue_levels=BEAST_FATIGUE,
        powers=[
            b.power(
                "Smell Water",
                0,
                0,
                "Animal",
                does="Scents water fit to drink up to two miles off.",
            ),
            b.power(
                "Survive Without Water",
                0,
                0,
                "Animal",
                does="Lasts up to two weeks without drinking.",
            ),
        ],
        appearance=(
            "The common two-humped riding camel: stubborn, tough and rank, "
            "placid most of the year but quick to turn savage in the rutting "
            "season. Going weeks without water and finding it underground "
            "make it the beast of choice for crossing deserts."
        ),
        notes=paragraphs(
            "The camel of the wider Middle East, beside the one-humped "
            "dromedary of North Africa, Egypt, Arabia and the Levant. Wild "
            "ones are rare and live only in the far east. Its humour is "
            "melancholic with a choleric streak; a few Bjornaer born on "
            "Europe's south-eastern edge have a camel heartbeast.",
            "Variants. The pack camel, most of a caravan's: add Domesticated "
            "and the Minor Heroic Virtue Great Bearer (Houses of Hermes: True "
            "Lineages p. 105: twice the load before it is burdened, and twice "
            "the distance before a journey tires it), and drop Survival. The "
            "wild camel: add Wilderness Sense and Greater Immunity to "
            "thirst, Communication -6, the Defensive Fighter (with its extra "
            "Fatigue level), Fast Runner and Herd Animal Qualities, Brawl "
            "(dodging) 4 and Wilderness Sense (sense sandstorms) 3; kick "
            "Init +0, Atk +5, Dfn +3, Dam +4. The war camel (from "
            "a Bactrian or a dromedary): add Aggressive, Pack Animal and "
            "Ferocity (when ridden into battle), Brawl (hooves) 5; kick "
            "Init +0, Atk +4, Dfn +3, Dam +0; trained, it fights in a "
            "Trained Group with its rider.",
        ),
    )
    _MADE["elephant"] = b.creature(
        "Asian Elephant",
        page="p. 173",
        size=4,
        cunning=True,
        confidence=(0, 0),
        how_many="a few, kept by nobles or the Khwarazmian army",
        block={
            "characteristics": characteristics(0, 1, -4, -5, 10, 3, 0, -2),
            "virtues_flaws": [
                *_times("Improved Characteristics", 3),
                "Tough",
                "Fear",
                "Amphibious",
                "Crafty",
                "Defensive Fighter",
                "Grapple",
                "Herd Animal",
                "Sharp Ears",
                "Tough Hide",
            ],
            "abilities": [
                ("Athletics", 3, "running"),
                ("Awareness", 3, "food"),
                ("Brawl", 4, "dodge"),
                ("Survival", 3, "forests or plains"),
                ("Swim", 4, "rivers"),
            ],
            "traits": {"Lustful": -3, "Wise": 2},
        },
        attacks=[
            b.attack("Stomp", -2, 4, 2, 13),
            b.attack("Trunk (grapple)", -1, 4, 2, None),
        ],
        soak=9,
        fatigue_levels="OK, 0/0, -1, -3, -5, Unconscious",
        powers=[
            b.power(
                "Trunk",
                0,
                0,
                "Animal",
                does="Always active: the trunk handles things like a hand, "
                "though work needing two hands is at -3.",
            ),
        ],
        appearance=(
            "The Asian elephant: up to ten feet high and twenty long, "
            "weighing as much as 8,000 pounds. This block is the usual tamed "
            "cow; only bulls carry tusks worth fighting with."
        ),
        notes=paragraphs(
            "Persia's ancient armies prized war elephants, and a few remain "
            "in the east, curiosities for nobles and shock troops for the "
            "Khwarazmian army. Elephants are famed foes of dragons and "
            "charge serpents without fear, but the squeal of a pig or boar "
            "terrifies them (their Fear) and they bolt unless held. They "
            "hear superbly and feel tremors through the trunk (+3 to "
            "hearing). Each Improved Characteristics gives a Size +4 beast "
            "12 points. Its natural stomp is Init -1, Attack 0, Defense -1, "
            "Damage +3, and the trunk only grapples; one dropped from a "
            "height on a man does +15 damage. Thick Skin, which the catalog "
            "lacks, is left out; Tough Hide is kept.",
            "Variants. The bull: add Aggressive, Extra Natural Weapons, "
            "Imposing Appearance twice, Large Horns (tusks), Herd Leader and "
            "Ferocity (defending the herd), Presence +1 and Communication -4, "
            "Brawl (tusks) 5 and Leadership (elephants) 5; tusks Init +1, "
            "Attack +9, Defense +5, Damage +13. The war elephant: add "
            "Aggressive and Pack Animal, Brawl (stomp) 5; stomp Init -2, "
            "Attack +6, Defense +3, Damage +13. Persian ones wear the like "
            "of leather or metal scale (3 or more to Soak) and carry a howdah "
            "for up to six soldiers with javelins, polearms or bows, fighting "
            "as a Trained Group with them under the mahout.",
        ),
    )
    _MADE["heavenly_horse"] = b.creature(
        "The Heavenly Horse of Farghana",
        page="p. 174",
        realm="Faerie",
        might=5,
        form="Animal",
        size=2,
        cunning=True,
        confidence=(0, 0),
        tires=False,
        how_many="herds in the valley of Farghana",
        block={
            "characteristics": characteristics(-2, 0, 2, -4, 5, 4, 1, 3),
            "virtues_flaws": [
                "External Vis (Minor)",
                "Faerie Beast",
                "Ferocity",
                "Long-Winded",
                *_times("Improved Characteristics", 3),
                "Unaffected by The Gift",
                "Incognizant",
                "Proud (Minor)",
                "Susceptible to Deprivation",
                "Amphibious",
                "Domesticated",
                "Fast Runner",
                "Good Jumper",
                "Herd Animal",
                *_times("Imposing Appearance", 3),
                "Tireless",
            ],
            "abilities": [
                ("Athletics", 4, "long-distance running"),
                ("Awareness", 3, "noises"),
                ("Brawl", 2, "hooves"),
                ("Swim", 4, "rivers"),
            ],
            "traits": {"Spirited": 3, "Loyal": 2},
            "reputations": {"Dragon-steed (local)": 2},
        },
        attacks=[b.attack("Hooves", 4, 2, 6, 6)],
        soak=4,
        powers=[
            b.power(
                "Heavenly Hooves",
                2,
                0,
                "Animal",
                rtd=("", "Sun", ""),
                level=25,
                does="Always active: it runs at full speed whatever the "
                "ground, up to thirty miles a day, even over open water or "
                "chasms without slowing. ReAn (Base 10, +2 Sun, +1 constant); "
                "a Personal Power.",
            ),
        ],
        vis=[
            BodyVis(
                1,
                "Animal",
                "a year, faerie-tainted, in the bloody sweat gathered from it",
            ),
        ],
        appearance=(
            "Like other middling chargers, a little under sixteen hands "
            "high, but finer-boned than the best mundane horse; even a "
            "skilled trainer struggles to tell its breeding."
        ),
        notes=paragraphs(
            "The horses of the headwaters of the Jaxartes, famous since "
            "ancient times, said to be foals of mortal mares by river "
            "dragons or other heavenly steeds; they look much like the "
            "Arab-bred horses of Europe's nobles, if a little larger. Magi "
            "and Gifted sahirs want them because neither The Gift nor "
            "Magical Air troubles them, not even a Blatant Gift, and tales "
            "tell of envoys from Serica travelling vast distances for one.",
            "They sweat blood after any hard effort, without harm; a year's "
            "sweat, properly gathered, is a vis source of 1 pawn of "
            "faerie-tainted Animal vis (its External Vis). As a faerie it "
            "neither tires nor ages, but suffers as usual without air, food "
            "and water in its role. Like any horse it has +3 to running and "
            "jumping. Positive Reputation, which the catalog lacks, is left "
            "out. Not balanced as a player's character. " + PRETENSES,
        ),
    )
    _MADE["ruq"] = b.creature(
        "Ruq",
        page="p. 176",
        realm="Magic",
        might=14,
        form="Animal",
        size=6,
        season="Autumn",
        cunning=True,
        confidence=(1, 3),
        how_many="roosting in the diamond-strewn valleys of the Roof of the World",
        block={
            "characteristics": characteristics(0, 3, 2, 0, 13, 3, 1, -4),
            "virtues_flaws": [
                "Magic Animal",
                "Ferocity",
                "Keen Vision",
                ("{land} Regio Network", {"land": "Cloud"}),
                "Unaffected by The Gift",
                "Magical Monster",
                ("Offensive to {being}", {"being": "animals"}),
                *_times("Gigantic", 5),
                *_times("Improved Initiative", 5),
                *_times("Lesser Power", 2),
                ("Major Flaw", {"flaw": "Age Quickly"}),
                *_times("Reduced Might", 3),
                "Susceptible to Deprivation",
                "Accomplished Flyer",
                "Aggressive",
                "Extra Natural Weapons",
                "Fast Flyer",
                "Grapple",
                *_times("Imposing Appearance", 3),
                "Keen Eyesight",
                "Pursuit Predator",
                "Thick Fur/Thick Scales",
            ],
            "abilities": [
                ("Area Lore: Persia", 6, "mountains"),
                ("Area Lore: Transoxiana", 6, "mountains"),
                ("Athletics", 5, "flight"),
                ("Awareness", 4, "prey"),
                ("Brawl", 5, "grapple"),
                ("Hunt", 4, "find prey"),
                ("Survival", 3, "mountains"),
            ],
            "traits": {"Fierce": 3, "Raptor": 3},
            "reputations": {"Stealer of livestock (Transoxiana)": 3},
        },
        attacks=[
            b.attack("Beak", 5, 7, 6, 14),
            b.attack("Talons", -1, 11, 3, 13),
            b.attack("Grapple", -1, 6, 1, None),
        ],
        soak=5,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Clasp",
                2,
                -8,
                "Corpus",
                rtd=("Eye", "Sun", "Individual"),
                level=10,
                does="Weakens the arms of someone held in its talons after a "
                "Grapple, so he cannot struggle free by opposing the Grapple; a "
                "Lesser Power, ReCo (Base 3, +2 Sun, +1 Eye).",
            ),
            b.power(
                "Paralyzing Stare",
                1,
                -9,
                "Corpus",
                rtd=("Eye", "Concentration", "Individual"),
                level=15,
                does="Holds fast any target of human size who meets its "
                "terrible stare. ReCo (Base 5, +1 Eye, +1 Concentration); a "
                "Lesser Power, cheapened.",
            ),
        ],
        vis=[BodyVis(3, "Animal", "in its wingtip feathers")],
        appearance=(
            "A gigantic eagle with eyes bright as steel and cruel hooked "
            "talons. This is one of the smaller ones, a little over 25 feet "
            "tall with a wingspan over 40; bigger ruqs (Size +8) have been "
            "seen bearing off elephants and even giants."
        ),
        notes=paragraphs(
            "The roc, which lifts a man in one claw like a mouse and carries "
            "off livestock, horses and people. Splendid, but no Beast of "
            "Virtue, and not meant as a player's character: built on a big "
            "falcon or eagle (Size -2) of base Might 15, raised to giant "
            "size. Tough Feathers, which the catalog lacks, is entered as "
            "Thick Fur/Thick Scales. The Turks and Mongols of the steppe hunt "
            "foxes, and even wolves, with the burkit, a golden eagle of "
            "Size -2.",
        ),
    )
    _MADE["steppe_pony"] = b.creature(
        "Steppe Pony",
        page="p. 179",
        size=1,
        cunning=True,
        confidence=(0, 0),
        how_many="the nomads' herds; most horses of the eastern provinces",
        block={
            "characteristics": characteristics(-2, 0, 0, -4, 2, 4, -2, 3),
            "virtues_flaws": [
                "Enduring Constitution",
                "Long-Winded",
                "Improved Characteristics",
                "Simple-Minded",
            ],
            "abilities": [
                ("Athletics", 4, "long-distance running"),
                ("Survival", 3, "steppe"),
            ],
            "traits": {"Brave": 2},
            "reputations": {"Hardy (local)": 1},
        },
        attacks=[b.attack("Kick", 5, 0, 5, 3)],
        soak=4,
        fatigue_levels="OK, 0/0, -1/-1, -3, -5, Unconscious",
        appearance=(
            "A little smaller than Europe's horses, light grey to dappled "
            "brown, and very hardy."
        ),
        notes=paragraphs(
            "The tarpan of the steppe, bred from its wild horses by every "
            "nomad tribe, and unlike the bigger breeds of Europe, Arabia and "
            "southern Persia (the Book of Mundane Beasts; Lords of Men, ch. "
            "5). The nomads value most the ponies that have Great Bearer and "
            "Sure Traveler, Minor Heroic Virtues (Houses of Hermes: True Lineages pp. "
            "105-107). Like all light horses it has +3 to running and "
            "jumping.",
        ),
    )
    _MADE["steppe_spirits"] = b.creature(
        "Lesser Steppe Spirit",
        page="p. 181",
        realm="Magic",
        might=30,
        form="Auram",
        how_many=(
            "one genius loci for each stretch of steppe, from a small valley "
            "to a land the size of a kingdom"
        ),
        block={"virtues_flaws": [_ways("Steppe")]},
        notes=paragraphs(
            "A template, not a full block. Might 30 to 45, of Auram or "
            "Terram, or now and then Aquam or Herbam; the pack enters the "
            "lowest, in Auram. Each is the genius loci of its own steppe, "
            "and all have Ways of the Steppe. Their usual powers are Creator "
            "of Winds or of Earth, Guide, Manifestation, Presence, and Ruler "
            "of Winds or of Earth, and some can give Major Supernatural "
            "Virtues to messengers they choose.",
            "They are fragments of Great Tengri, the sky god the steppe "
            "peoples call their common forefather: to Hermetic eyes an Elder "
            "Daimon, a Kosmokrator of steppe and sky drawing on the Magic "
            "realm, much as the old spirit of the Hercynian Forest does in "
            "the west. Where farmers and the Dominion press on the steppe's "
            "fringes, Tengri has spent some of its own power to make these "
            "lesser spirits. Each meets one of three ends: it holds out, "
            "keeping a magical steppe (the plains by the Sea of Azov, the "
            "Dzungarian basin, Mongolia's far east); it fades away, leaving "
            "mundane grassland, as in Pannonia and the Hungarian plain; or "
            "another being takes its place, most often making a faerie "
            "steppe.",
        ),
    )


# -- ch06: the short Arabian templates --


def _arabian_templates(cradle: Cradle) -> None:
    b = cradle.b
    templates = (
        (
            "saluqi",
            "Saluqi",
            "p. 104",
            "packs, or one hunting beside a falcon",
            "The noble greyhound-like hound of the Bedouin. Dogs are unclean "
            "to most Muslims outside the Maliki school, but saluqis are "
            "treasured, sleep in their owners' tents and are mourned in "
            "verse, prized for beauty and hunting alike as coursers in fast "
            "packs or as bird dogs working with falcons (Lords of Men, ch. 5, "
            "on hunting with hounds).",
            "No block of its own: take the greyhound (Realms of Power: Magic "
            "p. 143, or the Book of Mundane Beasts), add Grapple, Imposing "
            "Appearance twice and Keen Eyesight, drop Keen Sense of Smell, "
            "add Endurance and another Improved Characteristics, raise "
            "Presence to +1 and Stamina to +3, and make it Hunt 4 (track by "
            "sight). Exceptional ones have Puissant Hunt and powers like the "
            "Faerie Hounds of Realms of Power: Faerie pp. 88-89.",
        ),
        (
            "saqr",
            "Saqr",
            "p. 106",
            "kept by falconers across Arabia",
            "The Arab falconers' usual bird, like the gyrfalcon and prized "
            "for stamina more than speed; the falconers fly it at houbara, "
            "stone curlew and hare in the winter. A fine bird, especially a "
            "female, marks a tribal leader's standing.",
            "No block of its own: take the gyrfalcon of the Book of Mundane "
            "Beasts (Realms of Power: Magic p. 142, or Lords of Men p. 59) and "
            "add Tireless and Long-Winded. Exceptional saqrs, the nomad "
            "sheikhs' pride, have Puissant Hunt and Imposing Appearance "
            "twice.",
        ),
        (
            "shahin",
            "Shahin",
            "p. 106",
            "kept by falconers across Arabia",
            "The peregrine falcon, sometimes preferred to the saqr: the "
            "fastest falcon, but with far less stamina, best at taking small "
            "birds on the wing and less fit for hawking in the desert.",
            "No block of its own: take the falcon of the Book of Mundane "
            "Beasts at Size -4, with Quickness +1 and Strength -2, Ambush "
            "Predator, Stealth 3 (ambush prey) and Flight 3 (climbing "
            "flight), its combat worked out again to match.",
        ),
        (
            "dromedary",
            "Dromedary",
            "p. 104",
            "in every Bedouin camp and Arabian caravan",
            "The one-humped camel the Bedouin use in war and trade, commoner "
            "than the Bactrian in North Africa, Egypt, Arabia and the Levant. "
            "Magi of Hermes pp. 10-11 gives it in full.",
            "No block of its own: take the Bactrian camel and lower Strength "
            "to +1 and Stamina to +3, raise Dexterity to 0, drop Long-Winded, "
            "Feral Scent and Hardy and one Fatigue level, make its Reputation "
            "Cranky +1 (much of Arabia), its kick Init 0, Atk +4, "
            "Dfn +2, Dam +2, its Soak +3, and its Survival 3 (home "
            "terrain).",
        ),
        (
            "arabian_horse",
            "Arabian Racehorse",
            "p. 104",
            "bred by the Bedouin",
            "The Bedouin's famous horses, revered only below the camel. The "
            "jinn among them may ride stranger mounts: giant ostriches, "
            "leopards, or worse.",
            "No block of its own: take the courser of the Book of Mundane "
            "Beasts (Realms of Power: Magic, or the Atlas Games website), "
            "add Imposing Appearance twice and Great Quickness, with Presence "
            "+1 and Quickness +3. Arabian steeds for war or other work start "
            "from the destrier or the charger with the same changes.",
        ),
        (
            "flying_serpent",
            "Flying Serpent (Iaculus)",
            "p. 117",
            "flocks, in the incense trees of Hadramawt and on Soqotra",
            "The syrenii of Pliny, called iaculi by magi and javelin-snakes or "
            "darters by most people: white snakes with bat's wings, some with "
            "a pair of stubby legs, that perch in the incense trees and dart "
            "down on whatever passes. They guard the resin trees, and "
            "harvesters drive them off with the smoke of storax brought from "
            "Anatolia. Each year flocks try to cross into Egypt and are "
            "killed by the ibis, their natural enemy; since the ibis is "
            "Thoth's and so Hermes', most magi think them ill-omened, though "
            "one Quaesitor uses them in his inquiries.",
            "The book prints no statistics. Exceptional ones are said to "
            "slip past wards to deliver their venom, a claim no magus has "
            "tested. They are less sociable than the magical Olibanum "
            "Serpents of Soqotra (Rival Magic p. 110) and resist taming "
            "without magic; which came first is unknown.",
        ),
    )
    for key, name, page, many, about, rules in templates:
        _MADE[key] = b.creature(
            name,
            page=page,
            cunning=True,
            how_many=many,
            notes=paragraphs(about, rules),
        )


# -- ch09: the Mongols --


def _mongols(cradle: Cradle) -> None:
    b = cradle.b
    _MADE["mongol_trooper"] = b.creature(
        "Mongol Trooper",
        page="p. 180",
        age="30",
        encumbrance="2 (3)",
        how_many="the horde's vanguard, scouts and guards",
        block={
            "characteristics": characteristics(-1, 1, 0, -1, 1, 2, 1, 2),
            "virtues_flaws": [
                vf_puissant("Ride"),
                vf_puissant("Bows"),
                "Warrior",
                "Reckless (Minor)",
                "Disfigured",
                "Infamous",
            ],
            "abilities": [
                ("Animal Handling", 3, "horses"),
                ("Area Lore: Mythic Steppe", 3, "geography"),
                ("Area Lore: Persia", 2, "geography"),
                ("Area Lore: Transoxiana", 2, "geography"),
                ("Athletics", 3, "running"),
                ("Awareness", 2, "in combat"),
                ("Bargain", 2, "livestock"),
                ("Bows", 5, "composite"),
                ("Brawl", 3, "dagger"),
                ("Craft: Bows", 3, ""),
                ("Hunt", 3, "tracking"),
                ("Living Language: Mongolian", 5, "military communication"),
                ("Ride", 3, "battle"),
                ("Single Weapon", 5, "saber"),
                ("Survival", 3, "steppe"),
            ],
            "traits": {"Brave": 3, "Reckless": 3, "Loyal": 3},
            "reputations": {"Murderous (local)": 4},
        },
        attacks=[
            b.attack("Dagger", 0, 7, 6, 4),
            b.attack("Composite bow (mounted)", 0, 16, 13, 8),
            b.attack("Composite bow (on foot)", -2, 13, 10, 8),
            b.attack("Saber (mounted)", 4, 14, 12, 7),
            b.attack("Saber (on foot)", 2, 11, 9, 7),
            b.attack("Spear (mounted)", 4, 11, 10, 6),
            b.attack("Spear (on foot)", 2, 8, 7, 6),
        ],
        soak=4,
        fatigue_levels=FATIGUE,
        equipment=(
            "Composite bow (Load 2), half-armour of metal-reinforced leather "
            "(Load 2), saber (Load 1), daggers, spear (Load 1)."
        ),
        appearance=(
            "A fierce horseman of the east, his chest lightly armoured in "
            "fur-lined leather under an acorn-shaped iron helmet trimmed with "
            "fur, a bow in a saddle quiver, a saber and a short spear with a "
            "little hook below the blade."
        ),
        notes=paragraphs(
            "A mundane Mongol of the host now in Transoxiana and eastern "
            "Persia, as his victims see him (first given in another form in "
            "Ancient Magic pp. 15-18). Younger men ride too; this is the best "
            "the characters are likely to meet, a vanguard fighter, or a lone "
            "scout or sentry. Bows 5 and Ride 3 each gain +2 from Puissant; "
            "Soak is his armour and Stamina. No Confidence is printed. "
            "Mongol generals are chiefly brilliant soldiers, not the khan's "
            "kin, masters of reading a field and of the feigned retreat that "
            "draws a foe into a long, tiring chase before they turn on him.",
            "The orlock (a general): an older companion built from this "
            "template, about 40, with Intelligence 0, Perception +1, "
            "Presence +2, Communication +1, Strength 0, Stamina +2, "
            "Dexterity +1, Quickness 0 (from Improved Characteristics); adding "
            "Affinity with Leadership, Clear Thinker, Improved "
            "Characteristics, Inspirational, Puissant Leadership, "
            "Self-Confident and Strong-Willed, with Enemies (Mythic Middle "
            "East), Outsider and Vow (loyalty to Genghis Khan); without "
            "Puissant Bows or Reckless. Confidence 2 (5); Resolute +3, "
            "Ruthless +5, Cunning +4; add Leadership 6+2 (battlefield), "
            "Intrigue 3 (alliances), Guile 3 (elaborate lies), Folk Ken 2 "
            "(nobles), Persian 3 (negotiations), Craft: Siege Equipment 3 "
            "(catapults or mangonels) and Artes Liberales 1 (military "
            "communication); no Bargain, and Bows only 5. Soak, Fatigue, "
            "wounds, equipment and Encumbrance stay; combat is worked out "
            "again.",
        ),
    )
    _MADE["spirit_shaman"] = b.creature(
        "Mongol Spirit Shaman",
        page="p. 181",
        age="55",
        confidence=(1, 3),
        encumbrance="3 (3)",
        how_many="a few among the horde",
        block={
            "characteristics": characteristics(1, -1, 2, 1, -2, 2, -1, 1),
            "virtues_flaws": [
                "Wise One",
                "Summoning",
                "Ghostly Warder",
                vf_puissant("Ride"),
                "Warrior",
                "Enemies",
                "Outsider (Major)",
                "Disfigured",
                "Infamous",
                "Vow (Minor)",
            ],
            "abilities": [
                ("Animal Handling", 3, "horses"),
                ("Area Lore: Mythic Steppe", 3, "geography"),
                ("Area Lore: Persia", 2, "geography"),
                ("Area Lore: Transoxiana", 2, "geography"),
                ("Athletics", 3, "running"),
                ("Awareness", 3, "in combat"),
                ("Bargain", 3, "spirits"),
                ("Bows", 5, "composite"),
                ("Craft: Bows", 2, "composite"),
                ("Brawl", 2, "dagger"),
                ("Faerie Lore", 2, "spirits"),
                ("Guile", 2, "elaborate lies"),
                ("Hunt", 2, "tracking"),
                ("Infernal Lore", 3, "spirits"),
                ("Leadership", 2, "battlefield"),
                ("Magic Lore", 3, "spirits"),
                ("Living Language: Mongolian", 5, "negotiations"),
                ("Penetration", 4, "spirits"),
                ("Living Language: Persian", 3, "negotiations"),
                ("Ride", 3, "in battle"),
                ("Single Weapon", 3, "saber"),
                ("Survival", 3, "steppe"),
                ("Summoning", 22, ""),
            ],
            "traits": {"Resolute": 3, "Ruthless": 5, "Discerning": 4},
            "reputations": {"Murderous (local)": 4, "Spirit-worshiper (Infernal)": 3},
        },
        attacks=[
            b.attack("Dagger", 1, 4, 4, 1),
            b.attack("Composite bow (mounted)", -1, 12, 10, 5),
            b.attack("Composite bow (on foot)", -3, 9, 7, 5),
            b.attack("Saber (mounted)", 3, 10, 9, 4),
            b.attack("Saber (on foot)", 1, 7, 6, 4),
            b.attack("Spear (mounted)", 3, 7, 7, 3),
            b.attack("Spear (on foot)", 1, 4, 4, 3),
        ],
        soak=4,
        fatigue_levels=FATIGUE,
        equipment=(
            "Composite bow (Load 2), half-armour of metal-reinforced leather "
            "(Load 2), saber (Load 1), daggers, spear (Load 1)."
        ),
        appearance=(
            "An easterner in a jumble of tattered cloth, feathers and beads, "
            "with a ritual drum and stick; look closely and his clothes are "
            "on inside out."
        ),
        notes=paragraphs(
            "One of the few tribal shamans of Great Tengri, the Mongols' sky "
            "god, who ride with the army. Skilled in the spirit world, they "
            "call spirits to scout, to fight supernatural foes and to spy, "
            "and use whatever kind serves, demons included: a spirit may "
            "agree to be bound into a weapon, as a kind of enchanted device, "
            "or be set a task. For simplicity, assume he can readily call "
            "any suitable spirit, Faerie, Magic or Infernal, up to Might 30, "
            "and strike a bargain for its help; the Solomonic summoning rules of ch03 "
            "can guide play, and Realms of Power: The Infernal pp. 114-115 "
            "has fuller ones. Summoning is the Goetic Art (score 22, an Art).",
            "Every shaman has a familiar spirit much like a qareen, usually "
            "an ancestor of his homeland that follows and helps him (his "
            "Ghostly Warder; The Mysteries: Revised Edition or Realms of "
            "Power: Magic give examples). Each Characteristic except "
            "Communication carries 1 aging point; Decrepitude 1 (5). Unlike "
            "the shamans of Ancient Magic p. 18.",
        ),
    )


# -- finish: homes and links --


def finish(cradle: Cradle) -> None:
    """Set each creature at its place, link the place and the jinn to it,
    and put east.py's al-Khidr at the rock where Moses met him."""
    b = cradle.b
    for key, creature in _MADE.items():
        keys, words, region = HOMES[key]
        place = _home(cradle, keys, words)
        if place is None and region:
            place = cradle.places.get(region)
        if place is not None:
            if creature.place_id is None:
                creature.place_id = place.id
            _link(b, place, creature, ROLE.get(key, ""))
    jinn = cradle.world.get("jinn")
    if jinn is not None:
        for key, note in JINN.items():
            if key in _MADE:
                _link(b, jinn, _MADE[key], note)
    khidr = cradle.creatures.get("al_khidr")
    if khidr is not None and khidr.place_id is None:
        place = _home(cradle, *KHIDR_HOME) or cradle.places.get("mesopotamia")
        if place is not None:
            khidr.place_id = place.id


def _link(b: Builder, record: Neighbour, creature: Creature, note: str) -> None:
    if not any(link.target_id == creature.id for link in record.links):
        b.link(record, "creatures", creature, note)


def _home(cradle: Cradle, keys: tuple[str, ...], words: tuple[str, ...]) -> Any:
    """The first of `keys` a part made, else a place whose name holds one
    of `words`."""
    for key in keys:
        found = cradle.places.get(key) or cradle.world.get(key)
        if found is not None:
            return found
    places = [n for n in cradle.b.saga.neighbours if n.kind == "place"]
    for word in words:
        found = next((p for p in places if word.casefold() in p.name.casefold()), None)
        if found is not None:
            return found
    return None
