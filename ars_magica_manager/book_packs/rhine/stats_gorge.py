"""Full stats for the people of the Rhine Gorge story Guardians of the Forests prints stat blocks for."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Rhine


def build(rhine: Rhine) -> None:
    b = rhine.b
    magi = rhine.magi

    b.stats(
        magi["hilda"],
        {
            "characteristics": {
                "intelligence": 0,
                "perception": 0,
                "presence": -1,
                "communication": 1,
                "strength": 4,
                "stamina": 2,
                "dexterity": 1,
                "quickness": -2,
            },
            "size": 1,
            "decrepitude": (0, 0),
            "virtues_flaws": [
                "Custos",
                ("Great {characteristic}", {"characteristic": "strength"}),
                ("Puissant {ability}", {"ability": "single weapon"}),
                "Covenant Upbringing",
                "Obese",
                ("Oversensitive (Minor)", {}),
            ],
            "abilities": [
                ("Athletics", 2, "endurance"),
                ("Awareness", 3, "ambushes"),
                ("Bows", 2, "short bow"),
                ("Brawl", 4, "grappling"),
                ("Carouse", 1, "drinking quantity"),
                ("Folk Ken", 2, "peasants"),
                ("Living Language: High German", 5, "orders"),
                ("Great Weapon", 2, "pole axe"),
                ("Dead Language: Latin", 3, "making reports"),
                ("Leadership", 5, "grogs"),
                ("Music", 1, "singing loudly"),
                ("Organization Lore: Order of Hermes", 2, "Fengheld"),
                ("Single Weapon", 6, "mace and heater shield"),
                ("Teaching", 2, "Martial Abilities"),
            ],
            "traits": {"Brave": 3, "Loyal to Magi": 3, "Tolerant": -3},
            "notes": (
                "Age 28. Oversensitive to disrespect. A stout, strong custos "
                "raised at a covenant, who leads its grogs and drills them.\n"
                "Mace and heater shield: Init -1, Atk +13, Def +10, Dam +12. "
                "Mace: Init -1, Atk +12, Def +6, Dam +12. "
                "Short bow: Init -3, Atk +7, Def +1, Dam +10. "
                "Pole axe: Init -1, Atk +9, Def +1, Dam +15. "
                "Dagger: Init -2, Atk +7, Def +2, Dam +7. "
                "Fist: Init -2, Atk +5, Def +2, Dam +4. "
                "Grapple: Init -2, Atk +6, Def +3, Dam n/a. "
                "Soak +9; Encumbrance 0 (4). Wounds: -1 (1-6), -3 (7-12), "
                "-5 (13-18), Incapacitated (19-24).\n"
                "Equipment: full metal scale armour, mace, heater shield, "
                "pole axe, short bow, a traveller's kit of tools."
            ),
        },
    )

    b.stats(
        magi["byrek"],
        {
            "characteristics": {
                "intelligence": 0,
                "perception": -2,
                "presence": 0,
                "communication": 0,
                "strength": 0,
                "stamina": 2,
                "dexterity": 1,
                "quickness": 3,
            },
            "size": 0,
            "decrepitude": (0, 0),
            "virtues_flaws": [
                "Covenfolk",
                ("Affinity with {ability}", {"ability": "athletics"}),
                "Enduring Constitution",
                "Long-Winded",
                "Clumsy",
                "Depressed",
                "Simple-Minded",
            ],
            "abilities": [
                ("Athletics", 7, "running"),
                ("Awareness", 2, "obstacles"),
                ("Brawl", 2, "fist"),
                ("Carouse", 1, "solitary drinking"),
                ("Craft: Whittling", 2, "figurines"),
                ("Folk Ken", 2, "emotions"),
                ("Area Lore: Germany", 2, "Pomerania"),
                ("Great Weapon", 5, "long spear"),
                ("Hunt", 2, "birds"),
                ("Leadership", 1, "revolt"),
                ("Living Language: Low German", 2, "Pomeranian"),
                ("Ride", 3, "at speed"),
                ("Single Weapon", 2, "axe and round shield"),
                ("Survival", 3, "heathland"),
                ("Living Language: East Norse", 2, "Danish curses"),
                ("Living Language: West Slavonic", 5, "Sorbian"),
            ],
            "traits": {"Demoralized": 3, "Morose": 2},
            "notes": (
                "Age 27. A tall, unkempt runner sent away from Crintera, "
                "where his mother is a Horse Clan witch. He wears a horse-bone "
                "amulet she gave him and credits it with his speed and "
                "stamina; his Affinity with Athletics, Enduring Constitution "
                "and Long-Winded may come from it. He feels rejected and "
                "gloomy until given a real job.\n"
                "Long spear: Init +5, Atk +10, Def +10, Dam +7. "
                "Axe and round shield: Init +3, Atk +8, Def +8, Dam +6. "
                "Axe: Init +3, Atk +7, Def +5, Dam +6. "
                "Fist: Init +2, Atk +4, Def +6, Dam 0. "
                "Soak +4; Encumbrance 3 (3); Fatigue OK, 0, 0, -2, -4, "
                "Unconscious.\n"
                "Equipment: long spear, axe, round shield, heavy leather "
                "hauberk (taken off to run)."
            ),
        },
    )

    b.stats(
        magi["robert_schonburg"],
        {
            "characteristics": {
                "intelligence": 3,
                "perception": -1,
                "presence": 2,
                "communication": 1,
                "strength": 0,
                "stamina": 0,
                "dexterity": -1,
                "quickness": -1,
            },
            "size": 0,
            "confidence": (1, 3),
            "decrepitude": (0, 0),
            "virtues_flaws": [
                "Gentleman/woman",
                "Entrancement",
                "Arcane Lore",
                "Educated",
                "Premonitions",
                "Privileged Upbringing",
                ("Avaricious (Major)", {}),
                "Black Sheep",
                "Nocturnal",
                "Tainted with Evil",
            ],
            "abilities": [
                ("Artes Liberales", 2, "accounts"),
                ("Athletics", 2, "jumping"),
                ("Awareness", 1, "light sleeper"),
                ("Bargain", 1, "gaining advantage"),
                ("Brawl", 2, "dirty fighting"),
                ("Charm", 4, "women"),
                ("Chirurgy", 2, "burn wounds"),
                ("Civil and Canon Law", 2, "tolls"),
                ("Concentration", 1, "Entrancement"),
                ("Entrancement", 5, "women"),
                ("Etiquette", 2, "subtle insults"),
                ("Faerie Lore", 1, "Loreley"),
                ("Folk Ken", 2, "soldiers"),
                ("Living Language: High German", 5, "fine speech"),
                ("Guile", 3, "to affronted husbands"),
                ("Hunt", 2, "from horseback"),
                ("Infernal Lore", 4, "pacts"),
                ("Intrigue", 2, "nobility"),
                ("Dead Language: Latin", 3, "incantation"),
                ("Leadership", 2, "ruffians"),
                ("Magic Lore", 3, "occult properties"),
                ("Philosophiae", 3, "natural magic"),
                ("Premonitions", 3, "expeditious retreats"),
                ("Ride", 2, "while hunting"),
                ("Area Lore: Rhine", 3, "nobles"),
                ("Stealth", 1, "eavesdropping"),
                ("Theology: Christian", 1, "mortal sin"),
            ],
            "traits": {"Arrogant": 3, "Greedy": 3, "Scheming": 2},
            "reputations": {"Little More than a Thug": 2},
            "notes": (
                "Age 29. The baron of Schönburg's bastard, schooled in "
                "Cologne, where a mentor drew him into the Dark Arts. He "
                "serves the Devil for gain, bewitches people into obeying "
                "him, senses when he is about to be exposed, and works small "
                "natural magics: Intelligence + Infernal Lore + aura + stress "
                "die, cast like a Ritual (time and vis), with Shape and "
                "Material bonuses from stones and the like. A villain, not a "
                "player character.\n"
                "Fist: Init -1, Atk +1, Def +1, Dam 0. Soak 0; Encumbrance "
                "0 (0).\n"
                "Equipment: fine clothes, a sword he cannot use, pouches of "
                "herbs, odd stones and animal parts; about 10 pawns of mixed "
                "vis."
            ),
        },
    )

    b.stats(
        magi["wolkan"],
        {
            "characteristics": {
                "intelligence": 1,
                "perception": 1,
                "presence": -1,
                "communication": 1,
                "strength": 1,
                "stamina": 1,
                "dexterity": 2,
                "quickness": 2,
            },
            "size": 0,
            "decrepitude": (0, 0),
            "virtues_flaws": [
                "Branded Criminal",
                "Improved Characteristics",
                "Social Contacts",
                ("Ambitious (Minor)", {}),
            ],
            "abilities": [
                ("Athletics", 1, "escaping"),
                ("Awareness", 1, "being watched"),
                ("Brawl", 2, "dagger"),
                ("Carouse", 1, "putting at ease"),
                ("Charm", 2, "getting out of trouble"),
                ("Folk Ken", 2, "criminals"),
                ("Living Language: High German", 5, "criminal cant"),
                ("Guile", 2, "to authorities"),
                ("Intrigue", 3, "outlaws"),
                ("Leadership", 1, "thieves"),
                ("Legerdemain", 3, "filching"),
                ("Profession: Boatman", 2, "rowing"),
                ("Area Lore: Rhine", 3, "criminal types"),
                ("Single Weapon", 4, "short sword"),
                ("Stealth", 3, "in towns"),
                ("Survival", 2, "in towns"),
                ("Swim", 1, "holding breath"),
                ("Thrown Weapon", 3, "knife"),
            ],
            "traits": {"Self-Interest": 3, "Loyal": 0, "Brave": -1},
            "notes": (
                "Age 23. A thief branded on the cheek, let out of the Pfalz "
                "jail to collect Lord Robert's tolls, unaware they are unjust. "
                "He knows the toll trade and the dripstone sales, and has "
                "criminal contacts along the Rhine he hopes to lead.\n"
                "Short sword: Init +3, Atk +10, Def +8, Dam +6. "
                "Thrown knife: Init +2, Atk +7, Def +6, Dam +3. "
                "Dagger: Init +2, Atk +7, Def +5, Dam +4. "
                "Fist: Init +2, Atk +4, Def +4, Dam +1. "
                "Soak +1; Encumbrance 0 (1).\n"
                "Equipment: 2 daggers, short sword, change of clothes."
            ),
        },
    )

    b.stats(
        magi["torven"],
        {
            "characteristics": {
                "intelligence": 0,
                "perception": 1,
                "presence": -1,
                "communication": -1,
                "strength": 0,
                "stamina": 1,
                "dexterity": 3,
                "quickness": 1,
            },
            "size": 0,
            "confidence": (1, 3),
            "decrepitude": (0, 0),
            "virtues_flaws": [
                "Wise One",
                "Animal Ken",
                "Intuition",
                "Latent Magic Ability",
                "Wilderness Sense",
                "Magical Air",
                ("Magical {being} Companion", {"being": "animal"}),
                "Reclusive",
            ],
            "abilities": [
                ("Animal Ken", 3, "wolves"),
                ("Animal Handling", 3, "pigs"),
                ("Athletics", 2, "in forest"),
                ("Awareness", 2, "while hunting"),
                ("Bows", 2, "short bow"),
                ("Brawl", 2, "breaking holds"),
                ("Charm", 1, "peasants"),
                ("Chirurgy", 1, "animals"),
                ("Faerie Lore", 2, "Bright Winter"),
                ("Forest Lore", 3, "Westerwald"),
                ("Living Language: High German", 5, "Franconian"),
                ("Hunt", 3, "roe deer"),
                ("Leadership", 1, "Waldheim"),
                ("Magic Lore", 2, "herbs"),
                ("Stealth", 3, "in forests"),
                ("Survival", 3, "forests"),
                ("Swim", 2, "rivers"),
                ("Teaching", 2, "wilderness skills"),
                ("Wilderness Sense", 3, "forest"),
            ],
            "traits": {"Brave": 2, "Loner": 2, "Loyal to Waldheim": 2},
            "reputations": {"Wise One": 1},
            "notes": (
                "Age 24. Son of Waldheim's elder and its reluctant leader, "
                "happier with animals than people. His companion Red-Hame is "
                "a faerie wolf (Faerie Might 12), the Winter Court's "
                "messenger. His Latent Magic Ability, which he cannot "
                "control, sometimes brings wolf packs to his aid.\n"
                "Short bow: Init 0, Atk +9, Def +4, Dam +6. "
                "Knife: Init +1, Atk +6, Def +3, Dam +2. "
                "Fist: Init +1, Atk +5, Def +3, Dam 0. "
                "Soak +2; Encumbrance 2 (2).\n"
                "Equipment: plain brown clothes, wolf-fur jerkin, bow."
            ),
        },
    )

    b.stats(
        magi["david_ben_david"],
        {
            "characteristics": {
                "intelligence": 2,
                "perception": 0,
                "presence": 0,
                "communication": 2,
                "strength": 0,
                "stamina": 1,
                "dexterity": 0,
                "quickness": 0,
            },
            "size": 0,
            "confidence": (1, 3),
            "decrepitude": (0, 0),
            "apparent_age": 30,
            "virtues_flaws": [
                "Merchant",
                "Wealthy",
                "Educated",
                ("Puissant {ability}", {"ability": "bargain"}),
                "Social Contacts",
                "Well-Traveled",
                ("Pious (Major)", {}),
                ("Outsider (Major)", {}),
                "Judged Unfairly",
            ],
            "abilities": [
                ("Dead Language: Aramaic", 3, "Torah"),
                ("Animal Handling", 2, "horses"),
                ("Artes Liberales", 3, "accounts"),
                ("Awareness", 2, "faulty goods"),
                ("Bargain", 5, "luxuries"),
                ("Area Lore: Bavaria", 2, "towns"),
                ("Carouse", 2, "amongst Jews"),
                ("Charm", 2, "gaining trust"),
                ("Civil and Canon Law", 3, "regarding merchants"),
                ("Etiquette", 2, "gentlemen"),
                ("Folk Ken", 3, "empathizing"),
                ("Living Language: French", 2, "trading"),
                ("Guile", 2, "perceiving cheats"),
                ("Living Language: High German", 6, "Yiddish"),
                ("Intrigue", 3, "merchants"),
                ("Living Language: Italian", 2, "trading"),
                ("Dead Language: Latin", 3, "bargaining"),
                ("Leadership", 1, "amongst Jews"),
                ("Living Language: Low German", 2, "trading"),
                ("Medicine", 2, "infected wounds"),
                ("Philosophiae", 2, "debate"),
                ("Profession: Merchant", 4, "luxury goods"),
                ("Profession: Ship's Captain", 2, "on the Rhine"),
                ("Area Lore: Rhine", 3, "towns"),
                ("Ride", 1, "good roads"),
                ("Area Lore: Swabia", 2, "towns"),
                ("Swim", 2, "rivers"),
                ("Teaching", 2, "Academic Abilities"),
                ("Theology: Judaism", 3, "duties"),
            ],
            "traits": {
                "Devout Jew": 3,
                "Honest": 2,
                "Insensitive to Insults": 2,
            },
            "reputations": {"Jew": 3},
            "notes": (
                "Age 30. A rich Jewish merchant of Trier trading between "
                "Trier, Koblenz, Bingen and Mainz, schooled at the Jewish "
                "academy in Mainz; married to Sophie, no children. He will not "
                "bend his faith for an easier life, and may soon be asked to "
                "become a rabbi. His nephew Isaac runs the wine shop above "
                "Treverorum for him.\n"
                "Dodge: Init 0, Def 0. Soak +1; Encumbrance 0 (0).\n"
                "Equipment: plain merchant's clothes with the Jewish badge, "
                "skull cap."
            ),
        },
    )
