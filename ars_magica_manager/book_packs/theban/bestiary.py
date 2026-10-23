"""The Bestiary: the creatures The Sundered Eagle gives a stat block, from
the little envy demon of the evil eye to the vampires of the Greek
countryside, plus the six great beings it gives only a Might, whose
powers are told in the notes. The patrons of the covenants are not here:
they belong to their covenants' notes.

Numbers are the book's; what powers do, how a creature looks and the
notes are a summary in the pack's own words. Each creature is set at its
place in `finish`, once every region has built its places: the nearest
place a region part made, or else the region itself."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...models import BodyVis
from ..builder import characteristics, vf_great, vf_minor

if TYPE_CHECKING:
    from ...models import Creature, Neighbour
    from . import Theban

#: A person's Fatigue levels, as the book's stat blocks print them.
FATIGUE = "OK, 0, -1, -3, -5, Unconscious"

#: Where each creature lives: its slug, then the place keys a region part
#: may have made (most likely first), words a place's name may hold, and
#: the region to fall back on.
HOMES: dict[str, tuple[tuple[str, ...], tuple[str, ...], str]] = {
    "baskanos": ((), (), "greece"),
    "arge": (("delos",), ("Delos",), "islands"),
    "opis": (("delos",), ("Delos",), "islands"),
    "loxo": (("delos",), ("Delos",), "islands"),
    "demon_of_nicaea": (("nicaea",), ("Nicaea",), "anatolia"),
    "anima": (("smyrna", "alexandria"), ("Smyrna",), "anatolia"),
    "sibyl": (("erythrae",), ("Erythrae",), "anatolia"),
    "stoicheion": ((), (), "greece"),
    "vrykolakas": ((), (), "greece"),
    "smerdaki": ((), (), "greece"),
    "gorgona": (("thessaloniki",), ("Thessaloniki",), "greece"),
    "talos": (("candia", "crete", "knossos"), ("Candia", "Crete"), "islands"),
    "klymene": (
        ("great_altar", "pergamos", "pergamon"),
        ("Great Altar", "Pergamos", "Pergamon"),
        "anatolia",
    ),
    "belisarius": (
        ("serpent_column", "hippodrome"),
        ("Serpent Column", "Hippodrome"),
        "constantinople",
    ),
    "akgah": (("akgah_lair", "akgah"), ("Akgah",), "constantinople"),
    "druj": (
        ("vantage_point_of_xerxes", "xerxes_hill", "abydos", "hellespont"),
        ("Xerxes", "Abydos", "Hellespont"),
        "anatolia",
    ),
}

#: Where the creature sits within a place whose name says it is a regio
#: (Belisarius lives in the regio above the column, not at the column).
IN_REGIO = {"belisarius"}


def _improved(characteristic: str) -> tuple[str, dict[str, str]]:
    return ("Improved {characteristic}", {"characteristic": characteristic})


def _resistance(form: str) -> tuple[str, dict[str, str]]:
    return ("{form} Resistance", {"form": form})


#: The creatures this part makes, by slug, for `finish`.
_MADE: dict[str, Creature] = {}


def build(theban: Theban) -> None:
    _MADE.clear()
    _culture(theban)
    _delos(theban)
    _anatolia(theban)
    _realms(theban)
    _infernal(theban)
    _might_only(theban)


def finish(theban: Theban) -> None:
    """Set each creature at its place, and list it among the place's
    creatures."""
    for slug, creature in _MADE.items():
        keys, words, region = HOMES[slug]
        place = _home(theban, keys, words, region)
        if place is None:
            continue
        creature.place_id = place.id
        if slug in IN_REGIO and place.details.get("levels"):
            creature.place_level = 1
        theban.b.link(place, "creatures", creature, _ROLE.get(slug, ""))
    alexandria = theban.covenants.get("alexandria")
    if alexandria is not None and "anima" in _MADE:
        theban.b.link(
            alexandria, "creatures", _MADE["anima"], "one of its two artifacts"
        )


#: The note on each place's link to its creature.
_ROLE = {
    "baskanos": "the demon behind the evil eye",
    "arge": "a guardian of the shrines",
    "opis": "a guardian of the shrines",
    "loxo": "a guardian of the shrines",
    "demon_of_nicaea": "seven demon dogs on the roads outside the walls",
    "anima": "Alexandria's glass submarine, chained to a ship at Smyrna",
    "sibyl": "the sibyls of Ionia, Phrygia and the Hellespont",
    "stoicheion": "the guardian spirits of villages",
    "vrykolakas": "the vampire of Greek folklore",
    "smerdaki": "the demons that plague shepherds",
    "gorgona": "the mermaid of the northern Aegean",
    "talos": "the bronze protector of Candia",
    "klymene": "the titan bound under the great altar",
    "belisarius": "the faerie of the Serpent Column's regio",
    "akgah": "the demon of the Fourth Crusade, laired outside the city",
    "druj": "the demon bound beneath Xerxes's hill",
}


def _home(
    theban: Theban, keys: tuple[str, ...], words: tuple[str, ...], region: str
) -> Neighbour | None:
    """The first of `keys` a region part made, else a place whose name
    holds one of `words`, else the region itself."""
    for key in keys:
        if key in theban.places:
            return theban.places[key]
    places = [n for n in theban.b.saga.neighbours if n.kind == "place"]
    for word in words:
        found = next((p for p in places if word.casefold() in p.name.casefold()), None)
        if found is not None:
            return found
    return theban.places.get(region)


def _culture(theban: Theban) -> None:
    """Chapter 4's demon of the evil eye."""
    b = theban.b
    _MADE["baskanos"] = b.creature(
        "Baskanos",
        page="ch. 4",
        realm="Infernal",
        might=5,
        form="Vim",
        size=-7,
        how_many="swarms, unseen in the air wherever envy breeds",
        order="Tempters",
        weakness="Abhorrent Material (an amulet against the evil eye)",
        block={
            "characteristics": characteristics(2, 5, -5, -2, -2, 1, 1, 3),
            "virtues_flaws": ["Hex", "Sharp Ears", "Restriction", "Weak-Willed"],
            "abilities": [
                ("Awareness", 4, "compliments"),
                ("Folk Ken", 4, "envy"),
                ("Hex", 10, "destroy prosperity"),
                ("Penetration", 5, "Hex"),
            ],
            "traits": {"Envious": 6, "Selfish": 5, "Petulant": 3},
        },
        soak=1,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Coagulation",
                1,
                -1,
                "Corpus",
                does="Takes on a solid body, which it can let dissolve whenever "
                "it likes.",
            ),
            b.power(
                "Obsession",
                1,
                -5,
                "Vim",
                does="Costs 1 to 3 points: plants the Obsession Trait Envy in "
                "its victim, as Realms of Power: The Infernal describes.",
            ),
        ],
        vis=[BodyVis(1, "Vim", "in its eye")],
        appearance=(
            "A shrivelled little man the size of a rat whose head is nothing "
            "but one huge, unblinking, lidless eye."
        ),
        notes=(
            "A kakodaemon, as the Greeks call this kind of demon. Baskanoi "
            "hover like clouds of flies, waiting for a chance to sour good "
            "fortune into resentment; most cases of the evil eye are their "
            "work, though some people cast it themselves by Folk Magic or "
            "the Hex Ability. Their Restriction is that the Hex reaches only "
            "someone who has been praised or envied, so they use Obsession "
            "to make such targets. Wound ranges: Light 1, Medium 2, Heavy 3, Incapacitated at 4, Dead from 5.\n"
            "The surest ward is a blue glass amulet with an eye painted on "
            "it, worn on the neck or wrist or hung over a cradle or a byre; "
            "the few who can make them are much sought after. A horned sign "
            "made with the left hand after careless praise wards only for "
            "a moment."
        ),
    )


def _delos(theban: Theban) -> None:
    """Chapter 6's three Hyperborean nymphs: one block, a power each."""
    b = theban.b
    block = {
        "characteristics": characteristics(1, 2, 2, -1, 1, 2, 6, 3),
        "virtues_flaws": [
            "Daimon",
            "Magic Spirit",
            vf_great("Dexterity"),
            vf_great("Dexterity"),
            "Improved Characteristics",
            "Improved Characteristics",
            ("Puissant {ability}", {"ability": "Bows"}),
            "Self-Confident",
            "Driven (Minor)",
            "Fury",
            "Magical Air",
            "Greater Power",
            "Greater Power",
            "Greater Power",
            _improved("Dexterity"),
            ("Major Virtue", {"virtue": "Essential Virtue"}),
            "Improved Attack",
            "Improved Confidence",
            "Improved Damage",
            "Improved Damage",
            "Improved Defense",
            "Improved Initiative",
            _resistance("Mentem"),
            vf_minor("Keen Vision"),
            *[vf_minor("Improved Characteristics")] * 4,
            vf_minor("Inoffensive to Animals"),
            vf_minor("Tethered Magic"),
            vf_minor("Voice of the Island"),
        ],
        "abilities": [
            ("Dead Language: Classical Greek", 4, "sacred hymns"),
            ("Athletics", 5, "running"),
            ("Awareness", 5, "vandals"),
            ("Bows", 12, "short bow"),
            ("Brawl", 4, "dodge"),
            ("Area Lore: Delos", 5, "birds"),
            ("Hunt", 6, "quail spirits"),
            ("Dead Language: Hyperborean", 5, "warriors"),
            ("Area Lore: Hyperborea", 3, "archers"),
            ("Leadership", 4, "intimidation"),
            ("Magic Lore", 4, "wizards"),
            ("Mentem Resistance", 5, "deception"),
            ("Penetration", 4, "Strike of the Cornered Game"),
            ("Swim", 4, "coastal waters"),
        ],
        "traits": {"Archer": 6, "Wrathful": 3, "Dutybound": 3},
        "reputations": {"Guardian of the Shrines (Local)": 3},
    }
    shared = [
        b.power(
            "Donning the Corporeal Veil",
            0,
            2,
            "Corpus",
            does="Makes herself a body with these statistics and lets it go "
            "at will. If the body is killed it leaves the vis behind, but "
            "only this Aspect dies, not the spirit.",
        ),
        b.power(
            "Strike of the Cornered Game",
            2,
            4,
            "Corpus",
            level=25,
            does="Anyone her arrow hits is held paralysed until she lifts "
            "the power or the sun next rises or sets (ReCo 25: base 5, "
            "+1 Touch, +2 Sun, +1 ended at will; Greater Power, -1 Might "
            "cost, +4 Init).",
        ),
    ]
    own = {
        "Arge": (
            "distance",
            b.power(
                "Outstanding Distance",
                3,
                5,
                "Herbam",
                level=25,
                does="Her arrow can reach a target as far as seven leagues off "
                "with no penalty for range, on a normal missile Attack, so "
                "long as she can see it with nothing in the way (ReHe 25: "
                "base 3, +1 Touch, +4 magnitudes for the distance; Greater "
                "Power, +5 Init).",
            ),
        ),
        "Opis": (
            "aim",
            b.power(
                "Unequaled Aim",
                1,
                9,
                "Corpus",
                level=15,
                does="An arrow that hits strikes the body part she chooses: "
                "normal damage, and the part is useless, giving a Minor Flaw "
                "(Lame, Missing Eye or Missing Hand, say) until the wound "
                "heals. A struck hand lets go of what it held. A Greater "
                "Power, +7 Init, matching PeCo 15 (+1 Part, +1 Touch, base "
                "5).",
            ),
        ),
        "Loxo": (
            "trajectory",
            b.power(
                "Peerless Trajectory",
                0,
                10,
                "Herbam",
                level=5,
                does="Her arrow bends round corners, walls and shields: if she "
                "knows where the target is, cover doesn't stop a normal "
                "missile Attack, range counts along the arrow's real path, "
                "and the target's Defense leaves out any shield. A Greater "
                "Power, -1 Might cost and +8 Init, matching ReHe 5 (+1 "
                "complexity, +1 Touch, base 3).",
            ),
        ),
    }
    for name, (art, power) in own.items():
        _MADE[name.casefold()] = b.creature(
            f"{name}, Nymph of Delos",
            page="ch. 6",
            realm="Magic",
            might=30,
            form="Corpus",
            size=0,
            season="Winter",
            confidence=(3, 8),
            block=block,
            attacks=[
                b.attack("Short Bow", 5, 25, 0, 14),
                b.attack("Dodge", 3, None, 11, None),
            ],
            soak=5,
            fatigue_levels=FATIGUE,
            powers=[*shared, power],
            vis=[BodyVis(6, "Rego", "in her bow")],
            equipment="Short bow of ivory, full heavy leather armor.",
            appearance=(
                "One of three severe young women with their hair pulled "
                "tightly back, in leather armor with ivory bows, plainly "
                "displeased; the three are hard to tell apart."
            ),
            notes=(
                f"One of the three Hyperborean nymphs who came to Delos with "
                f"Apollon and Artemis and now keep its shrines; each embodies "
                f"part of archery, and {name} rules its {art}. Their "
                f"sisters Hyperoche and Laodice left Delos for home with "
                f"sacred gifts and were never heard of again, and the three "
                f"long for news of them. They appear when someone damages "
                f"the island's ruins or relics, and give the culprit a few "
                f"breaths to explain before they start shooting; their "
                f"victims are mortally hurt but do not die until they have "
                f"left Delos. Their bow gives Defense as not applicable. "
                f"Wound ranges: the usual ones for Size 0, Light 1-5 to Dead from 21. Their Personality Traits are Essential "
                f"Traits. Tethered Magic (Houses of Hermes: True Lineages) "
                f"lets them carry their powers on their arrows.\n"
                f"They are Aspects of Daimons of the Magic Realm: one slain "
                f"forms again a day later. They keep to the shrines where the "
                f"aura is strongest, so Acclimation does not wear down their "
                f"Might. They speak Hyperborean and could tell a seeker of "
                f"Hyperborean magic much, but they are unfriendly and want "
                f"proof of worth first."
            ),
        )


def _anatolia(theban: Theban) -> None:
    """Chapter 8's Demon of Nicaea and Alexandria's iron dolphin."""
    b = theban.b
    _MADE["demon_of_nicaea"] = b.creature(
        "Demon of Nicaea",
        page="ch. 8",
        realm="Infernal",
        might=20,
        form="Animal",
        size=0,
        confidence=(1, 3),
        how_many="seven, prowling the highways round Nicaea",
        order="Furies",
        hierarchy=1,
        weakness="Abhorrent Circumstance: a sunny day",
        block={
            "characteristics": characteristics(-1, 3, -1, 1, 3, 3, 3, 2),
            "virtues_flaws": ["Berserk", "Tough"],
            "abilities": [
                ("Athletics", 4, "pursuit"),
                ("Awareness", 3, "stragglers"),
                ("Brawl", 5, "teeth"),
                ("Leadership", 6, "demons of Nicaea"),
            ],
            "traits": {"Wrathful": 6, "Savage": 4},
            "reputations": {"Harrower of Saints (Infernal)": 2},
        },
        attacks=[b.attack("Teeth", 2, 12, 9, 4)],
        soak=5,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Coagulation",
                2,
                -1,
                "Corpus",
                does="Takes a solid body (Realms of Power: The Infernal).",
            ),
            b.power(
                "Endurance of the Enraged",
                0,
                0,
                "Corpus",
                does="The Furies' power to fight on in a rage (Realms of "
                "Power: The Infernal).",
            ),
            b.power(
                "Obsession",
                1,
                -5,
                "Vim",
                does="Costs 1 to 3 points: imposes the Obsession Trait Wrath.",
            ),
        ],
        vis=[BodyVis(4, "Animal", "one in each paw")],
        appearance=(
            "A big, wild-coated, savage dog with drool on its snarling jaws, "
            "always slinking low as if on the hunt, ears flat and growling; "
            "its glowing red eyes terrify its prey."
        ),
        notes=(
            "Long ago the people of Nicaea begged Saint Andrew to rid them "
            "of seven demons killing travellers outside the city; he drove "
            "them off, and they came to him as slavering dogs. Days later "
            "they killed a young man in his bed in another town, and the "
            "apostle prayed him back to life. The seven still haunt the "
            "roads but may not enter Nicaea. They strike at dusk or just "
            "after, mostly at lone travellers (a solitary Redcap is just "
            "their prey), about once a month; most townsfolk blame bandits "
            "or skirmishers. They can speak but seldom do, fight as a "
            "trained pack, and will run from a stronger group or a "
            "formidable foe. Wound ranges: the usual ones for Size 0, Light 1-5 to Dead from 21."
        ),
    )
    _MADE["anima"] = b.creature(
        "Anima, the Glass Submarine",
        page="ch. 8",
        realm="Magic",
        might=12,
        form="Terram",
        size=4,
        cunning=True,
        block={
            "characteristics": characteristics(-3, -2, -5, -6, 7, 1, 3, -3),
            "virtues_flaws": ["Lightning Reflexes", "Poor Eyesight"],
            "abilities": [
                ("Awareness", 2, "food"),
                ("Brawl", 2, "dodging"),
                ("Survival", 3, "Aegean Sea"),
                ("Swim", 5, "Bay of Smyrna"),
            ],
            "traits": {"Playful": 3, "Loyal": 1},
        },
        attacks=[b.attack("Dodge", 0, None, 0, None)],
        soak=8,
        fatigue_levels="N/A",
        powers=[
            b.power(
                "Supple as a Fish",
                0,
                0,
                "Terram",
                level=34,
                does="An instilled effect that lets the iron body swim as "
                "easily as a fish: ReTe 34 (+2 Sun, +2 metal, +3 Size, base "
                "3, +1 complexity, +1 for two uses a day, +3 for a sunrise "
                "and sunset trigger).",
            ),
            b.power(
                "Transparent Skin",
                0,
                0,
                "Terram",
                level=24,
                does="Makes its hide almost clear, so it is hard to see and its "
                "riders can look out (MuTe 24: base 1, +2 metal, +3 Size, +2 "
                "Sun, +1 for two uses a day, +3 for a sunrise and sunset "
                "trigger).",
            ),
            b.power(
                "Habitable Bowels",
                0,
                0,
                "Auram",
                level=19,
                does="Keeps a light breeze moving inside it, so the riders can "
                "breathe in some comfort: CrAu 19 (+3 Structure, +1 Touch, "
                "base 1, +2 Sun, +1 for two uses a day, +3 for a sunrise "
                "and sunset trigger).",
            ),
        ],
        appearance="An enormous dolphin wrought of iron.",
        notes=(
            "Legend calls Alexander's undersea vessel a glass bell hung "
            "from a ship; in truth it is an awakened simulacrum, a thinking "
            "mechanica of iron shaped like a dolphin as big as an elephant, "
            "made long before Alexander found it. It thinks and feels like "
            "a dolphin, and its powers were instilled in it, so they cost no "
            "Might. Up to five people of Size 0 ride inside (a tight fit) "
            "through a sealed hatch where a blowhole would be. Alexandria "
            "keeps it chained, on six hundred feet of iron chain, to one of "
            "its merchant ships at Smyrna, under guard and sailed as often "
            "as the others; the chain comes off when it carries riders. "
            "Like the flying device, it may be lent to a magus whose tokens "
            "outnumber his shards, for a deposit and a pawn of vis a week.\n"
            "Being iron, it has no Wound Penalties but 15 Damage Levels "
            "(City & Guild): when damage beats its Soak it rolls Stamina "
            "plus a stress die against the excess, losing a level on a "
            "failure and one more per botch, with no penalty until the last "
            "goes and it bursts apart. Only someone with Mechanica or "
            "Automata can repair it, that score in levels a season; Catella "
            "has neither, but a few Verditius in the Tribunal know "
            "Automata. Nine of its twelve vis slots are used, so a "
            "mechanician could add more; studying it gives each "
            "investigator three Insights toward integrating its craft."
        ),
    )


def _realms(theban: Theban) -> None:
    """The character guides of chapters 9 and 10: a sibyl and a
    stoicheion."""
    b = theban.b
    _MADE["sibyl"] = b.creature(
        "A Sibyl",
        page="ch. 9",
        realm="Magic",
        might=25,
        form="Mentem",
        size=0,
        season="Winter",
        age="n/a (varies)",
        confidence=(2, 6),
        how_many="a character guide for any of the ten sibyls, half of them "
        "in the Tribunal",
        block={
            "characteristics": characteristics(5, 6, 0, 1, -1, 0, -1, -1),
            "virtues_flaws": [
                "Magic Human",
                "Magical Master",
                "Famous",
                "Self-Confident",
                "Meddler (Major)",
                ("Ability Block", {"abilities": "Martial Abilities"}),
                "Visions",
                ("Divination and Augury", {"method": "varies"}),
                _improved("Perception"),
                "Natural Appearance",
                *["Improved Abilities"] * 3,
                _resistance("Mentem"),
                *[vf_minor("Additional Divination Method")] * 5,
                *[vf_minor("Great Intelligence")] * 2,
                *[vf_minor("Great Perception")] * 2,
                vf_minor("Improved Characteristics"),
                vf_minor("Premonitions"),
                vf_minor("Puissant Divination"),
            ],
            "abilities": [
                ("Dead Language: Classical Greek", 5, "prophetic pronouncement"),
                ("Area Lore: (her own land)", 5, "varies"),
                ("Area Lore: (a second land)", 5, "varies"),
                ("Area Lore: (a third land)", 5, "varies"),
                ("Artes Liberales", 4, "scribing riddles"),
                ("Divination", 10, "varies"),
                ("Faerie Lore", 4, "prophecy"),
                ("Guile", 1, "under duress"),
                ("Intrigue", 3, "local politics"),
                ("Dead Language: Latin", 5, "declamations"),
                ("Living Language: (local dialect)", 4, ""),
                ("Magic Lore", 5, "prophecy"),
                ("Mentem Resistance", 5, "mind-reading"),
                ("Organization Lore: (a first body)", 5, "varies"),
                ("Organization Lore: (a second body)", 5, "varies"),
                ("Penetration", 5, "Divination"),
                ("Philosophiae", 4, "natural philosophy"),
                ("Premonitions", 5, "nations"),
                ("Teaching", 3, "Area Lore"),
            ],
            "traits": {"Enigmatic": 6, "Meddlesome": 3, "Brave": 1},
            "reputations": {"Prophetess (Local)": 4},
        },
        attacks=[b.attack("Unarmed Defense", -1, None, -1, None)],
        soak=0,
        fatigue_levels=FATIGUE,
        vis=[BodyVis(5, "Mentem", "in her tools of divination")],
        appearance=(
            "A woman of the land she lives in, a girl or a withered old "
            "woman, her face behind a thin veil or a blindfold."
        ),
        notes=(
            "The book prints Magic Might 25+; most sibyls have more, which "
            "leaves room for openly magical powers beside their Divination "
            "(The Mysteries Revised Edition), Premonitions and learning. "
            "Divination is 10+2 with Puissant Divination. The Area and "
            "Organization Lores are the storyguide's to choose. Her Virtues "
            "and Flaws come to only 5 points, so there is room to tailor "
            "her; some sibyls are Transformed Humans instead. Enigmatic is "
            "an Essential Trait: magic to make her speak plainly simply "
            "fails. Wound ranges: the usual ones for Size 0, Light 1-5 to Dead from 21.\n"
            "The sibyls are ageless magic humans with true sight, each bound "
            "to a strong Magic aura or regio she cannot leave without losing "
            "her gift to Acclimation, and seldom without guardians. Those in "
            "the Tribunal: Demophile the Erythraean at Erythrae, across from "
            "Chios, who speaks in acrostics; Herophile the Delphic, who is "
            "not the Pythia and answers only those of royal blood, however "
            "thin; Phyto the Samian in her cave, who wants questions in "
            "rhyme but answers plainly; Amalthea the Hellespontine at "
            "Dardania on Mount Ida, who will not prophesy of Troy; and Lamia "
            "the Phrygian, who must be overpowered before she speaks and is "
            "terribly strong. Their daughters, the sibyllides, are magic kin "
            "with powers of sight who come home every ten years to report "
            "on the world."
        ),
    )
    _MADE["stoicheion"] = b.creature(
        "A Stoicheion",
        page="ch. 10",
        realm="Faerie",
        might=10,
        form="Animal",
        size=2,
        how_many="a character guide: every village and landmark has one",
        block={
            "characteristics": characteristics(0, 1, 2, -1, 1, 2, 0, 0),
            "virtues_flaws": [
                "Faerie Beast",
                "Focus Power",
                "Ritual Power",
                "Faerie Sight",
                "Feast of the Fae",
                "Improved Powers",
                "Increased Faerie Might (Minor)",
                "Lesser Power",
                "Personal Power",
                "Reputation as Confidence",
                "Time or Place of Power",
                "Narrowly Cognizant",
                "Overconfident (Minor)",
                "Intangible Flesh",
                ("Traditional Ward", {"ward": "varies"}),
            ],
            "abilities": [
                ("Area Lore: (its village)", 4, "local spirits"),
                ("Awareness", 3, "faeries"),
                ("Brawl", 6, "varies by animal"),
                ("Living Language: Greek", 4, "those it protects"),
                ("Faerie Lore", 2, "weaknesses of enemies"),
                ("Hunt", 3, "enemies"),
                ("Penetration", 4, "Guardian of the Bounds"),
            ],
            "traits": {"Fiercely Protective": 6, "Brave": 3, "Loyal": 3},
            "reputations": {"Defender (Local)": 4},
        },
        attacks=[
            b.attack("Teeth", 2, 14, 10, 5),
            b.attack("Claws", 2, 15, 12, 6),
            b.attack("Horns", 4, 13, 11, 5),
        ],
        soak=8,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Extended Glamour",
                0,
                0,
                "Mentem",
                does="Always on: it knows all that happens within the domain "
                "it has chosen, being one with that place; Might 10 covers a "
                "room, more Might a wider land. The domain yields Might/10 "
                "pawns of Animal vis a year as objects, which may be taken "
                "without harm if bargained for.",
            ),
            b.power(
                "Guardian of the Bounds",
                1,
                -5,
                "varies",
                does="Costs 1 to 5 points, 1 per 5 levels of the matching "
                "spell: walking the village's bounds and drawing a circle, it "
                "raises a ward like Ward against Faeries of the Water, of the "
                "Realm and Form it picks each time (Faeries of the Wood "
                "against crop blight, Demons of the Mind against the evil "
                "eye). Wards are kept low to penetrate; at Might 20 a level 10 "
                "ward costs 2 points and has Penetration 15.",
            ),
            b.power(
                "Loosely Material",
                3,
                -10,
                "Animal",
                does="Over a round it puts on glamoured flesh: Size +2 with the "
                "physical scores in the notes, the only form in which it can "
                "attack, kept as long as it likes. Slain, the body leaves the "
                "vis. Going back to spirit takes an unbroken round and returns "
                "the Might spent; a new body starts unwounded.",
            ),
            b.power(
                "Strike Dumb",
                5,
                -20,
                "Vim",
                does="Gives the victim the Mute Flaw. Made permanent, it costs "
                "Might score as well as Might Pool; temporary, the points come "
                "back only when it is lifted. Improved Powers has been "
                "applied.",
            ),
        ],
        vis=[BodyVis(3, "Animal", "in its bones")],
        appearance=(
            "Mostly unseen; to Second Sight, an outsized beast of the kind "
            "it has taken."
        ),
        notes=(
            "Might 20 in its own village, where its warding is stronger. "
            "In material form: Str +2, Sta +3, Dex +3, Qik +2. Pick the one "
            "attack that suits its beast. Its Focus Power is Guardian of the "
            "Bounds, its Ritual Power Strike Dumb, its Lesser Power Loosely "
            "Material and its Personal Power Extended Glamour. Wound ranges: Size +2, steps of 7, Light 1-7 to Dead from 29. With 15 points of Virtues and 7 of Flaws it is too "
            "strong for a player unless taken at a magus's level, but it "
            "makes a good covenant ally or guardian bought as a Boon; it may "
            "take up to 3 more points of Flaws for 2 Virtue points each. Its "
            "usual Traditional Ward is that it dies if it leaves the land or "
            "people it guards; slain, it comes back in time, a little "
            "changed.\n"
            "Stoicheia are spirits of places. In the wilds every odd boulder, "
            "lone tree, river and mountain has one, a genius loci; near "
            "people, faeries take the part, guarding the community for "
            "offerings of eggs, figs, milk and honey, and may desert or turn "
            "on a village that slights them. Kinds: the koukouvaounes, huge "
            "white owls with red eyes that fight evil faeries and demons, "
            "drink the milk left out for them, and may turn strong villagers "
            "into rams, oxen, horses or bulls to help; church stoicheia as a "
            "white calf, a red horse or a black cock; the basiliskos, a "
            "snake-shaped house spirit tied to a family, often with a Focus "
            "Power for housework; the pergalio, a black child with blue eyes "
            "bound to one building and given to jealousy; and the "
            "kalotyches of trees, which turn to murderous vengeance when "
            "their tree is felled, unless a stone is set in the cut."
        ),
    )


def _infernal(theban: Theban) -> None:
    """Chapter 12's two Theban demons."""
    b = theban.b
    _MADE["vrykolakas"] = b.creature(
        "Vrykolakas",
        page="ch. 12",
        realm="Infernal",
        might=20,
        form="Corpus",
        size=0,
        confidence=(1, 3),
        how_many="a kind, feared all over Greece",
        order="Vessels of Iniquity",
        weakness="Protected Group (those born on a Saturday)",
        block={
            "characteristics": characteristics(0, 0, 0, 0, 4, 4, 0, 2),
            "virtues_flaws": [
                "Shapeshifter",
                "Improved Characteristics",
                "Lightning Reflexes",
            ],
            "abilities": [
                ("Athletics", 10, "leaping"),
                ("Brawl", 5, "grapple"),
                ("Folk Ken", 3, "passing for human"),
                ("Shapeshifter", 3, "at night"),
                ("Thrown Weapon", 5, "spittle"),
            ],
            "traits": {"Hateful": 6, "Depraved": 6},
        },
        attacks=[
            b.attack("Grapple", 2, 6, 7, 4),
            b.attack("Teeth", 2, 10, 8, 7),
            b.attack("Spittle", 2, 6, 0, 10),
        ],
        soak=14,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Form of Wickedness",
                2,
                0,
                "Mentem",
                does="Shows its true, dreadful shape to spread panic "
                "(Realms of Power: The Infernal).",
            ),
            b.power(
                "Form of Man",
                0,
                0,
                "Corpus",
                does="Wears the dead man's likeness (Realms of Power: The Infernal).",
            ),
            b.power(
                "Contagious Obsession",
                1,
                0,
                "Mentem",
                does="One point for each victim (Realms of Power: The Infernal).",
            ),
            b.power(
                "Obsession",
                1,
                -5,
                "Vim",
                does="Costs 1 to 3 points: imposes the Obsession Trait Fear.",
            ),
            b.power(
                "Burning Spittle",
                0,
                2,
                "Ignem",
                does="Spits liquid fire up to five paces for +10 damage; "
                "anything that parries it is eaten through and ruined. A "
                "natural attack, which Magic Resistance does not stop.",
            ),
        ],
        vis=[BodyVis(4, "Corpus", "in its teeth")],
        appearance=(
            "Looks like anyone else until it shows its powers and its true "
            "shape: a hunchback with black hands and long nails, a peeling "
            "blood-red face, the teeth of a cat or wolf, and wild hair and "
            "beard, its skin glossy black or glowing in the dark. In Thrace "
            "it is worse still: goat-skinned, with an elephant's trunk and "
            "one enormous eye. As a shapeshifter it is mostly a cat, a goat "
            "or an owl."
        ),
        notes=(
            "The Greek vampire, also called timpanios, alitos or "
            "katakhanas in some regions. Greeks dig up their dead after "
            "three years to box the bones; if the flesh has not rotted, a "
            "demon has eaten the corpse and taken its shape, and it bursts "
            "out in its Form of Wickedness. Those likeliest to rise are "
            "people who died alone, had a cat leap over the body, ate mutton "
            "from a wolf's kill, or were cursed as they died (some wicked "
            "folk curse themselves). It settles in a village where no one "
            "knows it, preys first on the dead man's kin, then further "
            "afield, on beasts and people by night, and the district "
            "sickens. It likes to take a lone victim, grapple and bite, and "
            "may keep someone alive for nightly feeding with scuffle damage. "
            "Its Spittle has Defense not applicable. Wound ranges: the usual ones for Size 0, Light 1-5 to Dead from 21.\n"
            "Holy symbols drive it off, but its true foes are the "
            "alaphroiskiotoi, the Saturday-born: it cannot hurt them, and "
            "those of them with Second Sight always know it in human or "
            "spirit shape."
        ),
    )
    _MADE["smerdaki"] = b.creature(
        "Smerdaki",
        page="ch. 12",
        realm="Infernal",
        might=10,
        form="Animal",
        size=-2,
        how_many="many, each haunting its own pasture or ruin",
        order="Tempters / Evil Spirits",
        weakness="Compulsiveness",
        block={
            "characteristics": characteristics(0, 0, 0, 2, 1, 0, 3, 2),
            "virtues_flaws": ["Hex", "Weak-Willed"],
            "abilities": [
                ("Animal Handling", 5, "inducing stampede"),
                ("Athletics", 3, "giving chase"),
                ("Brawl", 3, "evasion"),
                ("Folk Ken", 3, "shepherds"),
                ("Hex", 2, "abortions"),
            ],
            "traits": {"Selfish": 5},
        },
        attacks=[b.attack("Dodge", 2, None, 5, None)],
        soak=5,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Coagulation",
                1,
                -1,
                "Corpus",
                does="Takes a solid body, but only from its illusory or physical form.",
            ),
            b.power(
                "Obsession",
                1,
                -5,
                "Vim",
                does="Costs 1 to 3 points: imposes the Obsession Trait Terror.",
            ),
            b.power(
                "Illusionary Form",
                1,
                1,
                "Imaginem",
                does="Makes a moving image of its body that it steers; it must "
                "be in this form or a real body to use Coagulation.",
            ),
            b.power(
                "Shout of Pan",
                1,
                1,
                "Animal",
                does="Up to ten animals bolt in terror, and the fear runs "
                "through the rest of a herd; enough goats or sheep make a "
                "deadly stampede.",
            ),
        ],
        vis=[BodyVis(2, "Animal", "in its eyes")],
        appearance=(
            "A man shaggy with hair from head to foot, a ram with black "
            "marks on its brow, or a red-skinned child with a cat's eyes."
        ),
        notes=(
            "Smerdos is the Greek word for anything foul or unclean, from "
            "spoiled wine and rotten meat to the unbaptised, children of "
            "mixed birth and bastards; the polluted may gain the evil eye "
            "or become masters of maleficia, but the belief that they "
            "become smerdaki is only peasant talk. The demons haunt pens, "
            "hedges, ruined houses and the places where flocks rest, "
            "scattering the beasts, causing miscarriages and maiming prized "
            "studs. Shepherds say nothing can harm them; that is because "
            "they so seldom leave their illusory form for a real body. "
            "Since each keeps to its haunt, shepherds move pasture and "
            "silence their bells so the demon doesn't notice. Wound ranges: Size -2, steps of 3, Light 1-3 to Dead from 13."
        ),
    )


def _might_only(theban: Theban) -> None:
    """The six the book gives a Might and no stat block; their powers are
    in the notes."""
    b = theban.b
    _MADE["gorgona"] = b.creature(
        "The Gorgona",
        page="ch. 5",
        realm="Faerie",
        might=40,
        appearance=(
            "A mermaid rising from the waves, at times in a chariot drawn "
            "by dolphins, with a lyre."
        ),
        notes=(
            "Powers (no stat block): she ranges over the whole northern "
            "Aegean, most often near Thessaloniki's harbour and at midnight "
            "in rough seas. Meeting a ship, she asks a sailor whether "
            "Alexander lives. Told he is dead, she sighs, plunges beneath "
            "the hull, swells to a monstrous size and lifts a wave with her "
            "hand to overturn the ship; told he lives and reigns, she lets "
            "it go and calms the sea with her lyre."
        ),
    )
    _MADE["talos"] = b.creature(
        "Talos, the Protector of Candia",
        page="ch. 6",
        realm="Magic",
        might=35,
        size=3,
        vis=[BodyVis(7, "Ignem", "in his ichor, if drained")],
        appearance=("A giant bronze man with a bull's head (he is not the Minotaur)."),
        notes=(
            "Powers (no stat block): Hephaistos made him for King Minos. "
            "Each day he runs three times round Crete, hundreds of miles, "
            "throwing great rocks at hostile ships; enemies who land he "
            "grips in a deadly embrace after heating himself red-hot. One "
            "vein of green ichor runs from his neck to his ankle, stopped "
            "by a bronze nail: Medea pulled it and he bled out, until a "
            "local alchemist brewed him fresh blood.\n"
            "Bound for centuries in a cellar of the ruined Labyrinth at "
            "Knossos in Byzantine times, he is free again now the old spell "
            "has failed, and he is a plague to Venetian ships; Candia's new "
            "rulers offer a fine reward for taking or killing the "
            '"demon". His true nature would fascinate House Verditius, '
            "and he could serve as the patron of a covenant on Candia."
        ),
    )
    _MADE["klymene"] = b.creature(
        "Klymene",
        page="ch. 8",
        realm="Magic",
        might=50,
        appearance="A titan-goddess, the titan of fame.",
        notes="Powers (no stat block): a Kosmokrator Spirit (Realms of Power: "
        "Magic). Neutral in the war of the titans, she was bound not in "
        "Tartaros but under the great altar at Pergamos, which is the "
        "lock of her prison; she thought the cell a kindness, shared "
        "with her sisters. A flaw in the binding lets a Hermetic magus "
        "standing on the altar cast a ritual without vis, drawing on "
        "her power; such spells risk odd side effects, and a botch is "
        "tainted as if with faerie vis.",
        secrets="The Theban magi do not know she is there. The bonds have a "
        "strength of 50, renewed each new year; every ritual cast "
        "from the altar wears them down by the pawns it would "
        "normally need. If they reach 0 within one year the altar "
        "splits and Klymene is free, and unhappy about it, with "
        "nowhere to go: she may go back to the Magic Realm, settle "
        "on a mountaintop and upset all around her, or roam the "
        "Tribunal freeing other bound titanesses. Lucian's Children "
        "of Olympus are drawn to the altar.",
    )
    _MADE["belisarius"] = b.creature(
        "Belisarius of the Serpent Column",
        page="ch. 7",
        realm="Faerie",
        might=10,
        appearance=(
            "The great general as an urban faerie plays him, at the head of "
            "his imperial guardsmen."
        ),
        notes=(
            "Powers (no stat block): an incognizant faerie who lives in a "
            "regio (Faerie aura 4) above the Serpent Column in the "
            "Hippodrome, a vision of the arena in its old glory as big as "
            "the real one, entered by walking round the column against the "
            "sun with a Roman-style sword in hand. He gives the column its "
            "Faerie aura and leads a troupe of city faeries who re-enact, "
            "over and over, the end of the Nika Riots, with Belisarius and "
            "his guard crushing the rioters: a lesson, to him, that change "
            "is bad and lawful rule and old ways are best. He needs mortals "
            "for his play, so he sends his followers into the city to lure "
            "watchers in."
        ),
    )
    _MADE["akgah"] = b.creature(
        "Akgah, the Demon of the Fourth Crusade",
        page="ch. 12",
        realm="Infernal",
        might=50,
        size=0,
        appearance=(
            "A two-headed winged leopard the size of an elephant, a mockery "
            "of the winged lion of Venice, with sweet-scented fur mottled "
            "gold and black and great golden wings."
        ),
        notes=(
            "Powers (no stat block): a prince of Hell, foe and counterpart "
            "of the Hagka, the Divine two-headed eagle. Those in its company "
            "are seized by greed, lust and battle frenzy. In spring 1204 it "
            "fought the Hagka in the Hippodrome, wrecking part of the arena, "
            "and won; the eagle fled wounded, and crusaders who saw it took "
            "it for a holy vision of Venice's lion. The fall of the empire "
            "was its design, and won it great standing among Hell's princes; "
            "now it works to keep the successor states at war, distrustful "
            "and greedy.\n"
            "Its lair is an Infernal regio about a dozen miles from "
            "Constantinople, like a blasted battlefield, where it lolls "
            "eating from reeking heaps of corpses among treasure and "
            "plundered relics, with hundreds of bodies on pikes around it."
        ),
    )
    _MADE["druj"] = b.creature(
        "The Druj of Xerxes's Hill",
        page="ch. 8",
        realm="Infernal",
        might=30,
        appearance="Unseen, bound beneath the hill.",
        notes=(
            "Powers (no stat block): Obsession (Realms of Power: The "
            "Infernal), with the Obsession Trait Doubt. Artabanos, Xerxes's "
            "sorcerer in the Persian Wars, made her raise the man-made "
            "hill near Abydos in one day, then bound her under it to "
            "sharpen the king's sight, but her malice seeped out and filled "
            "Xerxes with doubt and gloom. The marble throne is gone. Anyone "
            "on the hill (Infernal aura 3) sees the whole Hellespont as if "
            "with Keen Vision, and is open to her Obsession."
        ),
    )
