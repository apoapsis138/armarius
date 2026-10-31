"""Galerius of House Guernicus (Ant pp. 67-79): a Quaesitor who treats every
slip as a danger to the Order, with Ingrid of Tremere his bodyguard, his
familiar Nightwing, the magi of his past cases, and the investigation as a
dormant story. Stat blocks are the book's; the rest is a summary, not its
words.

The Tribunal is the troupe's own, so nobody here is tied to one. The book's
own list of spells prints some differently from their source; each such
spell is named in the magus's notes."""

from __future__ import annotations

from ... import storage
from ...models import (
    BodyVis,
    BondPower,
    Character,
    EnchantedDevice,
    Familiar,
    InstilledEffect,
    Possession,
    ScoredTrait,
    ShapeMaterialBonus,
)
from ..builder import (
    Builder,
    StatBlock,
    ability_from_block,
    arts_from,
    characteristics,
    dormant,
    paragraphs,
    vf_ability,
    vf_art,
    vf_focus,
    vf_great,
    virtue_flaw_from_block,
)

S = Builder.stage

GUERNICUS = "house_guernicus"
TREMERE = "house_tremere"
FATIGUE = "OK, 0, -1, -3, -5, Unconscious"
HUMAN_WOUNDS = "-1 (1-5), -3 (6-10), -5 (11-15), Incapacitated (16-20), Dead (21+)"
#: The xp past score 6 in the book's "Magic Theory 6 (12)".
MAGIC_THEORY_XP = 12

_GALERIUS: StatBlock = {
    "characteristics": characteristics(4, 2, 1, 2, -2, 1, -1, 0),
    "apparent_age": 47,
    "warping": (2, 5),
    "confidence": (1, 3),
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Flexible Formulaic Magic",
        vf_art("Affinity with {art}", "Intellego"),
        vf_great("Intelligence"),
        "Hermetic Prestige",
        "Improved Characteristics",
        "Skilled Parens",
        (
            "Driven (Major)",
            {"detail": "protect the Order of Hermes from internal threats"},
        ),
        ("Restriction", {"detail": "cannot cast under a cloudless sky"}),
        ("Ability Block", {"abilities": "Martial Abilities"}),
        ("Obsessed (Minor)", {"detail": "finding evidence of criminality"}),
        "Unimaginative Learner",
    ],
    "traits": {
        "Driven to Protect the Order": 6,
        "Loyal to Nightwing": 3,
        "Suspicious": 3,
        "Fastidious": 1,
        "Forgiving": -2,
    },
    "reputations": {"Aggressive Investigator (Hermetic)": 3},
    "abilities": [
        ("Artes Liberales", 2, "logic"),
        ("Awareness", 3, "searching"),
        ("Brawl", 1, "dodging"),
        ("Civil and Canon Law", 2, "laws and customs of Lorraine"),
        ("Code of Hermes", 5, "mundane relations"),
        ("Concentration", 2, "spell concentration"),
        ("Finesse", 2, "fine control"),
        ("Folk Ken", 3, "mundanes"),
        ("Guile", 3, "impersonating mundanes"),
        ("Living Language: High German", 5, "expansive vocabulary"),
        ("Intrigue", 3, "rumormongering"),
        ("Dead Language: Latin", 5, "Hermetic usage"),
        ("Organization Lore: Order of Hermes", 3, "politics"),
        ("Magic Theory", 6, "Intellego"),
        ("Parma Magica", 3, "Mentem"),
        ("Penetration", 3, "Intellego"),
        ("Teaching", 1, "Magic Theory"),
    ],
    "arts": arts_from(
        "Cr 7, In 13, Mu 5, Pe 6, Re 5, "
        "An 5, Aq 0, Au 0, Co 9, He 5, Ig 0, Im 7, Me 10, Te 0, Vi 10"
    ),
    "spells": [
        ("The Inexorable Search", "InCo", 20, 0),
        ("Sight of the Molting Magus", "InCo", 25, 0),
        ("Whispers Through the Black Gate", "InCo(Me)", 15, 0),
        ("The Whole from the Part", "InCo", 15, 0),
        ("Tangle of Wood and Thorns", "ReHe", 15, 0),
        ("The Ear for Distant Voices", "InIm", 20, 0),
        ("Summoning the Distant Image", "InIm", 25, 0),
        ("Aura of Beguiling Appearance", "MuIm", 10, 0),
        ("Disguise of the Transformed Image", "MuIm", 10, 0),
        ("By His Works", "CrMe", 5, 0),
        ("Words of the Unbroken Silence", "CrMe", 10, 0),
        ("The Good Witness", "CrMe", 25, 0),
        ("Frosty Breath of the Spoken Lie", "InMe", 20, 0),
        ("Posing the Silent Question", "InMe", 20, 2),
        ("Thoughts Within Babble", "InMe", 25, 0),
        ("Aura of Rightful Authority", "ReMe", 20, 0),
        ("Trust Me", "ReMe", 20, 0),
        ("Invisible Sling of Vilano", "ReTe", 10, 0),
        ("Bitter Taste of Betrayal", "InVi", 15, 0),
        ("Sense of the Lingering Magic", "InVi", 30, 0),
        ("Maintaining the Demanding Spell", "ReVi", 20, 0),
    ],
    "masteries": {"Posing the Silent Question": ["Quiet Casting", "Still Casting"]},
    "notes": paragraphs(
        "Combat: dodge Init 0, Attack n/a, Defense +2, Damage n/a; dagger Init "
        "0, Attack +2, Defense +1, Damage +1. Soak +1. Fatigue levels "
        f"{FATIGUE}. Wounds {HUMAN_WOUNDS}.",
        "Equipment: opal ring talisman, wizardly robes, two-minute hourglass, "
        "dagger. Encumbrance 0.",
        "Appearance: tall, thin and austere, with the manner of a man used to "
        "being obeyed and little patience for talk. He wears robes of good "
        "wool worked with gold thread.",
        "His Magic Theory is printed 6 (12): score 6 with 12 experience "
        "toward 7. The book asks the troupe to change his native tongue and "
        "his Civil and Canon Law specialty to suit the saga (p. 68).",
        "Spells as this block prints them (p. 68): The Whole from the Part at "
        "level 15 (its source, level 20); Disguise of the Transformed Image "
        "at level 10 (the Definitive Edition, level 15); Maintaining the "
        "Demanding Spell at level 20, a general spell. 'Aura of Beguiling "
        "Presence', cited to Houses of Hermes: Societates p. 96, is that "
        "page's Aura of Beguiling Appearance; 'Words of Unbroken Silence' is "
        "Words of the Unbroken Silence.",
    ),
}

_INGRID: StatBlock = {
    "characteristics": characteristics(2, 0, 0, 0, 0, 2, 0, 1),
    "warping": (0, 1),
    "confidence": (1, 3),
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Flawless Magic",
        vf_ability("Affinity with {ability}", "Penetration"),
        vf_focus("Minor Magical Focus", "certamen"),
        "Skilled Parens",
        "Strong-Willed",
        ("Favors", {"detail": "to House Guernicus"}),
        ("Deficient Form", {"form": "Mentem"}),
        "Difficult Spontaneous Magic",
        ("Oversensitive (Minor)", {"detail": "to magi flaunting their power"}),
    ],
    "traits": {"Ambitious": 2, "Brave": 2, "Stubborn": 1},
    "abilities": [
        ("Artes Liberales", 2, "astronomy"),
        ("Athletics", 3, "acrobatics"),
        ("Awareness", 2, "bodyguarding"),
        ("Brawl", 2, "dagger"),
        ("Code of Hermes", 1, "Tribunal procedure"),
        ("Concentration", 3, "spell concentration"),
        ("Finesse", 3, "targeting"),
        ("Living Language: High German", 5, "storytelling"),
        ("Dead Language: Latin", 5, "Hermetic usage"),
        ("Leadership", 1, "in combat"),
        ("Magic Theory", 4, "Rego"),
        ("Parma Magica", 4, "Ignem"),
        ("Penetration", 5, "Rego"),
    ],
    "arts": arts_from(
        "Cr 5, In 0, Mu 5, Pe 10, Re 9, "
        "An 0, Aq 0, Au 0, Co 10, He 0, Ig 0, Im 0, Me 0, Te 9, Vi 0"
    ),
    "spells": [
        ("Bind Wound", "CrCo", 10, 1),
        ("Gift of the Bear's Fortitude", "MuCo", 25, 1),
        ("Grip of the Choking Hand", "PeCo", 25, 3),
        ("Invocation of Weariness", "PeCo", 20, 1),
        ("Endurance of the Berserkers (Duration: Diameter)", "ReCo", 15, 1),
        ("Wizard's Leap", "ReCo", 15, 1),
        ("The Crystal Dart", "MuTe(Re)", 10, 1),
        ("Pit of the Gaping Earth", "PeTe", 15, 1),
        ("Stone to Falling Dust", "PeTe", 20, 1),
        ("Invisible Sling of Vilano", "ReTe", 10, 1),
        ("Ominous Levitation of the Weighty Stone", "ReTe", 15, 1),
        ("Trackless Step", "ReTe", 10, 1),
        ("The Unseen Porter", "ReTe", 10, 1),
    ],
    "masteries": {
        "Bind Wound": ["Penetration"],
        "Gift of the Bear's Fortitude": ["Still Casting"],
        "Grip of the Choking Hand": [
            "Penetration",
            "Imperturbable Casting",
            "Multiple Casting",
        ],
        "Invocation of Weariness": ["Penetration"],
        "Endurance of the Berserkers (Duration: Diameter)": ["Imperturbable Casting"],
        "Wizard's Leap": ["Fast Casting"],
        "The Crystal Dart": ["Penetration"],
        "Pit of the Gaping Earth": ["Precise Casting"],
        "Stone to Falling Dust": ["Penetration"],
        "Invisible Sling of Vilano": ["Precise Casting"],
        "Ominous Levitation of the Weighty Stone": ["Precise Casting"],
        "Trackless Step": ["Quiet Casting"],
        "The Unseen Porter": ["Multiple Casting"],
    },
    "notes": paragraphs(
        "Combat: dagger Init +1, Attack +5, Defense +4, Damage +3. Soak +2. "
        f"Fatigue levels {FATIGUE}. Wounds {HUMAN_WOUNDS}.",
        "Equipment: unassuming dress, Ash Wand talisman, dagger. Encumbrance 0.",
        "Appearance: when she travels with Galerius she passes as his wife or "
        "daughter, quiet and watchful, in good plain clothes with hardly any "
        "jewelry. A second look finds her wiry and athletic, too much so for "
        "almost any woman of any rank. She keeps her talisman up her sleeve "
        "and has a habit of fingering it.",
        "Her Endurance of the Berserkers is the book's variant, Duration "
        "Diameter in place of Concentration (p. 74).",
    ),
}


def _talisman(
    b: Builder,
    holder: Character,
    name: str,
    words: str,
    effects: list[InstilledEffect],
    attunements: list[ShapeMaterialBonus],
) -> EnchantedDevice:
    """A magus's talisman, held by the magus: no covenant holds it."""
    device = EnchantedDevice(
        id=storage.generate_unique_id(name, [d.id for d in b.saga.enchanted_devices]),
        name=name,
        description=words,
        talisman=True,
        holder_kind="character",
        holder_id=holder.id,
        bonuses=attunements,
    )
    for number, effect in enumerate(effects, 1):
        effect.id = f"{device.id}-{number}"
        device.effects.append(effect)
    b.saga.enchanted_devices.append(device)
    return device


def _galerius(b: Builder) -> Character:
    galerius = b.magus(
        "Galerius of House Guernicus",
        covenant=None,
        house=GUERNICUS,
        age=54,
        summary=paragraphs(
            "A respected Quaesitor of middle rank in the local Tribunal, "
            "known for his unflagging work against wrongdoers and as an "
            "expert on dealings with mundanes. People say that everyone he "
            "has ever looked into turned out guilty of something.",
            "He was the pupil of the great Paulinus, a Quaesitor remembered "
            "for his legal opinions and his gift for making peace, whom a "
            "mob hanged as a witch while he travelled alone. Galerius traced "
            "the careless magus whose public spells had stirred up that town "
            "and had him convicted, and has spent the twenty years and more "
            "since prosecuting magi he thinks endanger the Order.",
            "He has won cases at several meetings of the Tribunal and has "
            "never lost a magus he charged. Many applaud him and privately "
            "fear him; he has no known friends but Ingrid of Tremere, and "
            "perhaps his own covenant.",
        ),
        secrets=paragraphs(
            "He believes reckless conduct will bring the Order down, imagines "
            "how any small incident could become a disaster, and assumes magi "
            "are always scheming round the Code. He cares for the harm a deed "
            "might do, not the harm it did, and thinks it better to risk "
            "punishing the innocent than to let the guilty go (pp. 67-69).",
            "Under it lies guilt. He worships Paulinus's memory so highly he "
            "can never match it, and he has moved the blame for the death "
            "onto the Tribunal and his fellow Quaesitors, whose laxity he "
            "condemns. His motives are sincere: brought to see that his zeal "
            "has made a travesty of justice, he is crushed and tries to make "
            "amends (p. 69).",
            "He is seldom seen in his true shape. He favours Disguise of the "
            "Transformed Image: a beggar, a leper, a pilgrim, a street "
            "urchin, a tradesman's boy on an errand, a peddler, a labourer, "
            "any villager he has seen going the other way; a woman if he must. "
            "He may change several times a day. His sigil is the colour grey, "
            "so every guise has some grey hair or clothing, which can give him "
            "away (pp. 68, 71).",
            "His talisman's Invisibility he saves for getting out of trouble, "
            "though a major suspect may tempt him. With mundanes he confirms "
            "a witness with Posing the Silent Question, casts Trust Me to talk "
            "past his Gift, bribes if that fails, and prefers to watch faces "
            "as they answer. He lies freely about who he is, and only admits "
            "to being a magus hunting 'outlaw wizards' to someone who has "
            "already seen magic. The mundanes' distrust of magi seeps into "
            "him, and he comes away thinking his suspects rogues (pp. 72-73).",
            "Nightwing keeps watch on crime scenes and scouts for him. Using "
            "the raven so, using a disguise to learn about a magus, and "
            "walking behind one invisible all count as scrying. His "
            "investigation immunity covers only a reasonable suspicion, and "
            "he stretches it to gather background on suspects, which the "
            "player magi can charge him with if they prove it. He stops short "
            "of hard rules: he never turns Intellego Mentem on a magus or a "
            "magus's servant without leave (pp. 71-73).",
        ),
    )
    b.stats(galerius, _GALERIUS, source="Ant")
    magic_theory = next(a for a in galerius.abilities if a.name == "Magic Theory")
    magic_theory.xp += MAGIC_THEORY_XP
    _talisman(
        b,
        galerius,
        "Opal Ring of Galerius",
        "Galerius's talisman, an opal ring. Attunements: Opal +2 images, Opal "
        "+4 memory, Jewelry +4 protect self. Casting totals in his spell list "
        "marked as his talisman's include these (p. 68).",
        [
            InstilledEffect(
                "",
                name="Invisibility",
                technique="Perdo",
                form="Imaginem",
                duration="Concentration",
                level=15,
                uses_per_day="3",
                maintains_concentration=True,
                description="Makes him invisible. Level as printed: Base 4, +1 "
                "Concentration, +1 moving image, +5 levels because the item "
                "maintains concentration.",
            ),
            InstilledEffect(
                "",
                name="Posing the Silent Question",
                technique="Intellego",
                form="Mentem",
                level=20,
                uses_per_day="Unlimited",
                description="As the spell. He uses it to test what a witness "
                "saw, or quietly during an interrogation.",
            ),
            InstilledEffect(
                "",
                name="Loss of But a Moment's Memory",
                technique="Perdo",
                form="Mentem",
                level=15,
                uses_per_day="6",
                description="As the spell.",
            ),
        ],
        [
            ShapeMaterialBonus(2, "images", "Opal"),
            ShapeMaterialBonus(4, "memory", "Opal"),
            ShapeMaterialBonus(4, "protect self", "Jewelry"),
        ],
    )
    return galerius


def _ingrid(b: Builder) -> Character:
    ingrid = b.magus(
        "Ingrid of House Tremere",
        covenant=None,
        house=TREMERE,
        age=36,
        summary=paragraphs(
            "A junior maga of House Tremere who does not yet hold her voting "
            "sigil. Her superiors lend her to the Quaesitors when asked, and "
            "she often travels with Galerius as his bodyguard through "
            "dangerous country or on violent cases. She stays at his side and "
            "says little, though her Gift makes it hard to go unnoticed.",
            "She goes by her Christian name, which cannot serve as a "
            "sympathetic connection to her.",
        ),
        secrets=paragraphs(
            "Rather like a very junior Hoplite, a word she would not use. She "
            "is weak at investigation and adds little to the case itself. She "
            "deters attacks on Galerius, but if the players do fight, she is "
            "less deadly than a true Hoplite (p. 74).",
            "In a fight she opens with The Crystal Dart; if Magic Resistance "
            "stops that she turns to indirect spells such as Invisible Sling "
            "of Vilano and Pit of the Gaping Earth. Wizard's Leap, mastered, "
            "takes her out of danger at fast-cast speed. With both an Arcane "
            "and a sympathetic connection to a foe she can penetrate with her "
            "favourites, Invocation of Weariness and Grip of the Choking "
            "Hand: not lethal, so unlikely to bring a charge of a high crime "
            "even without enough cause (p. 74).",
            "If Galerius falls into disgrace, House Tremere presses her to "
            "drop him, whatever she thinks herself (p. 79).",
        ),
    )
    b.stats(ingrid, _INGRID, source="Ant")
    _talisman(
        b,
        ingrid,
        "Ash Wand of Ingrid",
        "Ingrid's talisman, an ash wand she keeps hidden in her sleeve. "
        "Attunements: Ash +2 harm people, Wand +4 destroy things at a "
        "distance (p. 74).",
        [
            InstilledEffect(
                "",
                name="The Wound that Weeps",
                technique="Perdo",
                form="Corpus",
                level=15,
                uses_per_day="12",
                description="As the spell.",
            ),
            InstilledEffect(
                "",
                name="Repel the Wooden Shafts",
                technique="Rego",
                form="Herbam",
                level=10,
                uses_per_day="6",
                fast_trigger=True,
                description="As the spell, with a Fast Trigger: +3 to Initiative.",
            ),
        ],
        [
            ShapeMaterialBonus(2, "harm people", "Ash"),
            ShapeMaterialBonus(4, "destroy things at a distance", "Wand"),
        ],
    )
    return ingrid


_NIGHTWING_CHARACTERISTICS = characteristics(1, 2, -2, 0, -7, 0, -1, 5)
_NIGHTWING_VIRTUES: list[str | tuple[str, dict[str, str]]] = [
    "Magic Animal",
    "Magical Friend",
    ("Essential Virtue (Minor)", {"detail": "understand portents"}),
    "Keen Vision",
    "Unaffected by The Gift",
    ("Compulsion (Minor)", {"detail": "steal shiny objects"}),
    "Weak Characteristics",
    "Improved Abilities",
    "Improved Abilities",
    "Improved Defense",
    "Improved Defense",
    ("Minor Virtue", {"virtue": "Premonitions"}),
    ("Minor Virtue", {"virtue": "Second Sight"}),
    "Susceptible to Deprivation (Minor)",
]
_NIGHTWING_TRAITS = {
    "Loyal to Galerius": 3,
    "Morbid": 3,
    "Nurturing": 2,
    "Raven": 3,
    "Understands Portents": 3,
}
_NIGHTWING_REPUTATIONS = {"Bad Luck (local)": 2}
_NIGHTWING_ABILITIES = [
    ("Athletics", 3, "flying"),
    ("Awareness", 3, "shiny objects"),
    ("Brawl", 3, "dodging"),
    ("Living Language: German", 5, "sarcastic remarks"),
    ("Hunt", 1, "voles"),
    ("Dead Language: Latin", 5, "Hermetic usage"),
    ("Magic Theory", 1, "enchanting familiar"),
    ("Premonitions", 4, "homicide"),
    ("Second Sight", 4, "ghosts"),
    ("Stealth", 1, "hiding in treetops"),
    ("Survival", 3, "fields"),
]


def _nightwing(b: Builder, galerius: Character) -> None:
    nightwing = b.creature(
        "Nightwing",
        page="p. 69",
        realm="Magic",
        might=9,
        size=-4,
        confidence=(1, 3),
        block={
            "characteristics": _NIGHTWING_CHARACTERISTICS,
            "virtues_flaws": _NIGHTWING_VIRTUES,
            "traits": _NIGHTWING_TRAITS,
            "reputations": _NIGHTWING_REPUTATIONS,
            "abilities": _NIGHTWING_ABILITIES,
        },
        attacks=[
            b.attack("Dodge", 5, None, 12, None),
            b.attack("Beak", 5, 7, 11, -6),
        ],
        soak=0,
        fatigue_levels=FATIGUE,
        vis=[BodyVis(2, "Intellego", "1 in each eye")],
        appearance="A raven with an unnatural intelligence shining in its eyes.",
        notes=paragraphs(
            "The Raven of Virtue, Galerius's familiar. Base statistics before "
            "the bond are in Realms of Power: Magic p. 62. Wounds -1 (1), -3 "
            "(2), -5 (3), Incapacitated (4), Dead (5+). Warping Score 1 (8).",
            "Cords: Gold 0, Silver 3, Bronze 0. Bond powers: Mental "
            "Communication (complex), the Level 15 effect of ArM5 p. 105, "
            "working for both partners; Shared Senses, the Level 30 effect of "
            "ArM5 p. 105, letting Galerius use Nightwing's senses but not the "
            "reverse.",
        ),
        secrets=(
            "Galerius sees and hears through the raven to watch places and "
            "scout, and if he learns he is being followed it serves as his "
            "lookout. The raven is also a clue to his approach: seen once, it "
            "is watched for, and ordinary ravens can keep the magi on edge "
            "(pp. 72, 75, 77)."
        ),
    )
    b.saga.familiars.append(
        Familiar(
            id=storage.generate_unique_id(
                "Nightwing", [f.id for f in b.saga.familiars]
            ),
            character_id=galerius.id,
            name="Nightwing",
            species="A raven, the Raven of Virtue",
            magic_might=9,
            size=-4,
            virtues_flaws=[virtue_flaw_from_block(v) for v in _NIGHTWING_VIRTUES],
            personality_traits=[
                ScoredTrait(n, s) for n, s in _NIGHTWING_TRAITS.items()
            ],
            reputations=[ScoredTrait(n, s) for n, s in _NIGHTWING_REPUTATIONS.items()],
            silver_cord=3,
            characteristics=nightwing.characteristics,
            base_soak=0,
            natural_weapons=[
                Possession(
                    id=storage.generate_unique_id("Dodge", []),
                    kind="weapon",
                    name="Dodge",
                    weapon_init=5,
                    weapon_attack=None,
                    weapon_defense=12,
                    weapon_damage=None,
                ),
                Possession(
                    id=storage.generate_unique_id("Beak", []),
                    kind="weapon",
                    name="Beak",
                    weapon_init=5,
                    weapon_attack=7,
                    weapon_defense=11,
                    weapon_damage=-6,
                ),
            ],
            abilities=[ability_from_block(*a) for a in _NIGHTWING_ABILITIES],
            bond_powers=[
                BondPower(
                    id=storage.generate_unique_id(name, []),
                    name=name,
                    level=level,
                    target_controller=controller,
                )
                for name, level, controller in (
                    ("Mental Communication (complex)", 15, "Magus and familiar"),
                    ("Shared Senses", 30, "Magus uses the familiar's senses"),
                )
            ],
        )
    )
    b.link(galerius, "creatures", nightwing, "His familiar")


def _past(b: Builder, galerius: Character) -> None:
    """Paulinus, and the magi of the cases the book gives."""
    paulinus = b.magus(
        "Paulinus of House Guernicus",
        covenant=None,
        house=GUERNICUS,
        age=None,
        summary=(
            "A dead Quaesitor of high renown, remembered for his learned legal "
            "opinions, his skill as a peacemaker and decades of selfless "
            "service. Peasants in a town frightened of witchcraft took him for "
            "a witch while he travelled alone; they hunted him through every "
            "change of shape, seized him and hanged him in the square."
        ),
    )
    b.link(galerius, "characters", paulinus, "His pater")
    rosmer = b.magus(
        "Holger Rosmer of House Jerbiton",
        covenant=None,
        house="house_jerbiton",
        age=None,
        summary=(
            "The careless magus whose spells cast in public frightened a town "
            "and set its bishop preaching against witchcraft, in the troubled "
            "days when Paulinus passed through. Galerius hunted him down and "
            "charged him with endangering the Order; after a short trial he "
            "was convicted and punished with the death of his familiar. "
            "Galerius had pressed for a Wizard's March."
        ),
    )
    b.link(galerius, "characters", rosmer, "Convicted over Paulinus's death")
    kraxia = b.magus(
        "Kraxia of House Criamon",
        covenant=None,
        house="house_criamon",
        age=None,
        summary=(
            "Accused of molesting the fae, she was shown to have been framed "
            "by a neighbour, but Galerius went on to find that she had helped "
            "a local bandit escape the mundane authorities, and she was "
            "convicted of interfering with mundanes. Her penalty came to "
            "several seasons of service."
        ),
    )
    jurgen = b.magus(
        "Jürgen of Trier",
        covenant=None,
        house="house_ex_miscellanea",
        age=None,
        summary=(
            "A magus of Ex Miscellanea who framed his neighbour Kraxia to "
            "hide a crime of his own, and whose covenant was afterwards robbed "
            "by the bandit she had helped. Galerius exposed him; his penalty "
            "came to several seasons of service."
        ),
    )
    b.link(kraxia, "characters", jurgen, "The neighbour who framed her")
    iana = b.magus(
        "Iana of House Merinita",
        covenant=None,
        house="house_merinita",
        age=None,
        summary=(
            "Accused of refusing the outcome of a certamen she lost to "
            "Claudius of Verditius. Convicted of that and of obstructing a "
            "Quaesitor's investigation, she was banished from the Tribunal, "
            "and the lab text of the spell she had used was seized and "
            "destroyed."
        ),
        secrets=(
            "With no outside witnesses, she and Claudius each swore under "
            "Frosty Breath of the Spoken Lie to having won. Galerius found she "
            "had a spell of Momentary duration made to beat truth detection, "
            "much like Clear Breath of the Consummate Liar (Guardians of the "
            "Forests p. 73), castable without voice or gesture and so brief "
            "that it did not show when she was checked for active magic before "
            "her testimony. Since then he has insisted on checks before and "
            "after any questioning (pp. 75-77)."
        ),
    )
    claudius = b.magus(
        "Claudius of House Verditius",
        covenant=None,
        house="house_verditius",
        age=None,
        summary=(
            "The magus who beat Iana of Merinita at certamen, in the case "
            "Galerius investigated when she would not honour the result."
        ),
    )
    b.link(iana, "characters", claudius, "Her opponent at certamen")
    tranio = b.magus(
        "Tranio of House Jerbiton",
        covenant=None,
        house="house_jerbiton",
        age=None,
        summary=(
            "Repeatedly accused of stealing vis. Another Quaesitor looked into "
            "him without bringing charges; Galerius convicted him."
        ),
        secrets=(
            "Galerius waited invisible at a vis source Tranio had been "
            "robbing and caught him at it. The Tribunal's records say he had "
            "mundanes watching to tell him when to set the trap; they are not "
            "named and never testified (p. 76)."
        ),
    )
    for convict, note in (
        (kraxia, "Convicted of interfering with mundanes"),
        (jurgen, "Penalized after framing Kraxia"),
        (iana, "Convicted and banished from the Tribunal"),
        (tranio, "Convicted of stealing vis"),
    ):
        b.link(galerius, "characters", convict, note)


def _story(b: Builder, galerius: Character, ingrid: Character) -> None:
    threat = dormant(
        b.threat(
            "The Quaesitor's Investigation",
            antagonist="Galerius of House Guernicus",
            summary=paragraphs(
                "Galerius of House Guernicus is asking questions in the "
                "covenant's neighbourhood, and to be investigated by him is "
                "known to mean real trouble.",
            ),
            secrets=paragraphs(
                "Use him when the magi have done something questionable or "
                "have something to hide, or when they are falsely accused by "
                "mistake or by design. If there is no reason to suspect them "
                "he is no real threat, and can be a short-term ally: do they "
                "notice how far he oversteps, and dare they say so? He needs "
                "some evidence, however thin, and comes either on a neighbour's "
                "complaint or on his own initiative (pp. 67, 69).",
                "What might draw him (pp. 69-70): scrying, which Tribunals "
                "punish strictly and which he alone may half excuse; dealing "
                "with demons, even unknowingly through tainted vis, for which "
                "the penalty is always a March, so give the players clues and "
                "a fair chance; deprivation of magical power, over disputed "
                "vis, a slain beast near another covenant, or a contested "
                "familiar or apprentice, and more than one or two such quarrels "
                "brand them habitual troublemakers; mundane interference, "
                "which each Tribunal reads differently (Normandy demands proof "
                "of ruin to a magus, The Lion and the Lily p. 25, though serving "
                "a mundane as a court wizard is always serious); and reckless "
                "behaviour, no crime at all, though he thinks it should be. A "
                "case with no real merit makes him a paper tiger, a good choice "
                "for a troupe new to legal stories, but a conviction can still "
                "cost Reputation.",
                "False accusations (p. 70): a disliked wandering magus or "
                "redcap vanishes near the covenant, by outlaws, a river or "
                "faeries; a neighbour's sanctum is burgled of an invested "
                "device or fine book, with the owner's Arcane Connections ended "
                "by Perdo Vim, the thief being one of the victim's own "
                "covenant; a hedge wizard turned diabolist attacks enemies he "
                "shares with the covenant; a magus of another Tribunal secretly "
                "sells enchanted items past the usual limits, and the great of "
                "the region compete for them. Solving the real crime is the "
                "way out. Other sourcebooks' story seeds with accused magi "
                "serve too.",
                "The Reputation: a stress roll of his Reputation against Ease "
                "Factor 6 (ArM5 p. 19) tells a character he prosecutes what "
                "others overlook and seeks the harshest penalty (p. 70). "
                "Tribunal records are open on a season's notice; Int + Code of "
                "Hermes, stress, Ease Factor 12, shows he wins by blackening "
                "the defendant's character with anecdotes barely tied to the "
                "case (p. 75). He investigated and prosecuted all his cases "
                "himself, which is unusual; most were settled at private "
                "hearing, so the full Tribunal never saw his methods; one or "
                "two challenges to his charging beyond the first complaint "
                "failed (pp. 75-76).",
                "The powers of a Quaesitor (p. 72; Houses of Hermes: True "
                "Lineages pp. 61-66): he carries a letter of authority from "
                "the Primus and can lose it, and his House, for abuse; he must "
                "investigate serious complaints and may begin on his own; he "
                "may ask reasonable cooperation, which never includes "
                "submitting to magical interrogation; he may use magic in an "
                "investigation, but learning a magus's innocent affairs that "
                "way is a crime, softened by investigation immunity, under "
                "which he answers only for actual harm (True Lineages p. 62); "
                "he may call a March in an extreme case, for the Tribunal to "
                "ratify; he may not arrest or detain, nor order anyone to "
                "submit to mind-reading. Failure to cooperate is a low crime "
                "(p. 75).",
                "Making him harder (p. 73): he is written with one fatal flaw, "
                "using spells on mundanes, to give the players a counter-claim. "
                "Let a grog do the legwork instead and the scrying charge goes "
                "away. Mundanes may testify in person or, more often, in "
                "writing, with magic used to see they speak freely; often "
                "Quaesitors use them only to find physical evidence (True "
                "Lineages p. 58).",
                "Allies (p. 78): if the players start to feel the law is rigged, "
                "let a sympathetic magus he once savaged offer advice at a "
                "recess, such as the right to challenge evidence and demand "
                "its source. Well-wishers may turn up after the Tribunal "
                "whatever the verdict. Have a second player, with no magus on "
                "trial, play the presiding Quaesitor, coached on how seriously "
                "scrying is taken (p. 79).",
                "Preparing the defense (p. 76): what a Quaesitor may do is "
                "mostly unwritten House tradition, and serving Quaesitors will "
                "not discuss a colleague's misconduct, so the answers may lie "
                "with experts outside the Tribunal or in distant libraries. "
                "The accused may call character witnesses, the best answer to "
                "his attacks on character. Make them easy to get: anyone the "
                "covenant has helped or lived at peace with should speak, and "
                "mundanes may too, with less weight. Reaching them opens side "
                "stories. Trial procedure is in True Lineages pp. 56-59 (p. 78).",
            ),
            stages=[
                S(
                    "A hint of wrongdoing",
                    at=1,
                    clues=(
                        "Some crime or complaint near the covenant reaches him. "
                        "If the troupe has attended Tribunal, they may have "
                        "seen him prosecute."
                    ),
                    ignored="He comes to the covenant.",
                ),
                S(
                    "The interview",
                    at=2,
                    clues=(
                        "He arrives saying plainly what incident he is looking "
                        "into and asks what they know, who lives there, and who "
                        "has visited. He calls it an interview, is cordial if "
                        "brusque, asks hospitality for a night or two, and "
                        "declines any offer of magical verification as "
                        "premature, though he remembers it."
                    ),
                    ignored=(
                        "He seems to leave, and stays nearby in disguise to "
                        "check every answer."
                    ),
                ),
                S(
                    "Strangers in the villages",
                    at=3,
                    clues=(
                        "Several odd strangers seem to have come to the "
                        "villages at once, asking about the magi and snooping "
                        "around places they use. Each wears something grey. A "
                        "raven is about. Wild rumours spread behind them. "
                        "Mundanes know a good deal about the magi's visitors "
                        "and habits, and tell it readily."
                    ),
                    ignored=(
                        "He builds his picture of the magi as deceitful rogues "
                        "and spreads to anything else suspicious he finds; he "
                        "can jump from suspicion to suspicion for a long while."
                    ),
                    stopped=(
                        "Grogs and companions, free of the Gift, can shadow "
                        "him with some comic mistakes, and question the same "
                        "mundanes. Tracking him by mundane means is lawful, and "
                        "while they do not know the stranger is a Quaesitor "
                        "they are probably justified in using magic. Unmasked "
                        "by magic, he threatens charges and later drops them."
                    ),
                ),
                S(
                    "Requests for cooperation",
                    at=4,
                    clues=(
                        "If he thinks they are tampering he asks them to stay "
                        "home for a day or two on some pretext. If confronted "
                        "he grows angry and hints that they scried on him, "
                        "though he knows that charge will not stick, and tells "
                        "them to keep out of his way."
                    ),
                    ignored=(
                        "He files any hindrance as failure to cooperate, on his "
                        "own testimony."
                    ),
                    turned=(
                        "Solving the real crime while dodging him. Strong "
                        "evidence against someone else is the one thing that "
                        "dispels his suspicion; he doubts it, then follows it, "
                        "and comes to the right answer. He repays this by "
                        "asking for help with later cases, which earns a good "
                        "Hermetic Reputation, and may become a prickly friend."
                    ),
                ),
                S(
                    "Questioning under magic",
                    at=5,
                    clues=(
                        "If they offered, he comes back to hold them to it. "
                        "Each is taken alone and kept apart, must submit to "
                        "Sense of the Lingering Magic before and after, and may "
                        "use no magic. A Quaesitor casts Frosty Breath of the "
                        "Spoken Lie, held with Maintaining the Demanding Spell "
                        "and timed by his hourglass. His questions are built "
                        "to leave no way round, and he ends by asking about "
                        "any other crime, reported or not."
                    ),
                    stopped=(
                        "The truly innocent can clear themselves in minutes. If "
                        "he checks their answers and finds nothing he closes "
                        "the case and files no charges."
                    ),
                    ignored=(
                        "Refusal is their right where a question is off the "
                        "subject, but to him it shows guilt; he threatens, "
                        "does not prosecute it, and hunts for what they hid."
                    ),
                ),
                S(
                    "The private hearing",
                    at=6,
                    clues=(
                        "Summons under the presiding Quaesitor's seal. He "
                        "arranges to prosecute himself. Before the presiding "
                        "Quaesitor he offers muck first, then circumstance, "
                        "then his hard evidence with a triumphant glare. The "
                        "characters may contest the facts and ask how he came "
                        "by them; relevance waits for the public hearing."
                    ),
                    turned=(
                        "The harder they press on his conduct the more "
                        "agitated he grows, until the presiding Quaesitor turns "
                        "on him. He may rage, argue and lose, or see what he "
                        "has done, thunderstruck and in tears. Magi who refuse "
                        "magical questioning keep the moral high ground."
                    ),
                    stopped=(
                        "If they are innocent he agrees to drop the case rather "
                        "than be disgraced in public."
                    ),
                ),
                S(
                    "Counter-claim and settlement",
                    at=7,
                    clues=(
                        "A counter-charge of scrying heard now must have been "
                        "published beforehand; otherwise it waits for the next "
                        "Tribunal."
                    ),
                    stopped=(
                        "The presiding Quaesitor presses both sides: charges "
                        "cut or dropped for counter-claims dropped. Galerius "
                        "surrenders his letter of authority, goes to Magvillus "
                        "for several seasons of 'study' and may be moved to "
                        "another Tribunal. He pays each defendant three pawns "
                        "of vis a season for their expenses and lost seasons, "
                        "within a season. He loses Ingrid."
                    ),
                    ignored=(
                        "With his credit intact the case goes to public "
                        "argument, where he has every advantage and presses "
                        "for harsh penalties. Cooler heads give a minor penalty, "
                        "a vis fine or a couple of seasons' service, but the "
                        "magi gain or raise a bad Hermetic Reputation (ArM5 p. "
                        "167)."
                    ),
                ),
                S(
                    "The rematch",
                    at=8,
                    clues=(
                        "If he won, he thinks the penalty too light and turns up "
                        "at any mischief in the region."
                    ),
                    ignored=(
                        "A later Tribunal brings new charges against them, or "
                        "theirs against him for unlawful investigation. Make it "
                        "decisive: a final confrontation beats living in dread "
                        "of one more trial."
                    ),
                ),
            ],
        )
    )
    b.link(threat, "characters", galerius, "The investigator")
    b.link(threat, "characters", ingrid, "His bodyguard")
    b.link(galerius, "characters", ingrid, "His bodyguard on dangerous cases")


def build(b: Builder) -> None:
    galerius = _galerius(b)
    ingrid = _ingrid(b)
    _nightwing(b, galerius)
    _past(b, galerius)
    _story(b, galerius, ingrid)
