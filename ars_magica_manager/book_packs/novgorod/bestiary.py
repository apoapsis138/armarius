"""The Bestiary (ch04, ch05): the Slavic faeries, monsters and the
vampire, and Stolitzya the Swimmer, converted from the Fourth Edition
(N13).

The conversion: Might as printed (where the book gives a range, its
lower end, the range in the notes); Characteristics as printed (a
"varies" entered as 0); Size as printed. Combat is worked out again from
the Definitive Edition's weapons (Storyguide Screen p. 4; DE pp.
172-176): Init Qik + weapon, Attack Dex + Ability + weapon, Defense Qik
+ Ability + weapon, Damage Str + weapon, the Ability at the score that
gives the printed Attack with the new weapon (at least 1, at most 10);
Soak is Stamina plus the protection the old Soak gave beyond Stamina and
Size. The faeries have no Confidence (RoP:F p. 54).

Each printed Faerie Power becomes a Realms of Power: Faerie power (pp.
54-61): one with an exemplar there takes it (Bless as Grant (Minor
Virtue), Curse as Grant (Minor Flaw), or Major at a rating of 10 or more
for a faerie of Might 30 or more; Elfshot as Cause Sickness; Fear and
Infatuation as Enthralling Sound; Possession as Enthrallment;
Shapechange Other to Animal as Transform Victim into (Animal); Brew
Faerie Potions and Enchant Objects as Craft Magical Trinket); the
Control, Glamour and Healing powers are Focus Powers over their Form,
up to the old rating x 5 and never above the Might (p. 54); the
shape-changes, invisibility and insubstantiality are Personal Powers at
the level of the matching spell; Prophecy and Travel are Greater
Powers. Might costs and Init follow the Faerie Power Virtue table (p.
55). Powers the book prints with Hermetic levels (the dragons' breath,
the vampire's, Stolitzya's) keep their level; a faerie's is priced as a
Greater Power, the vampire's and Stolitzya's keep the book's Might cost,
each with Init Qik less its cost.

The Slavic gods have no statistics (p. 83) and are notes on the
Volkhvy (world.py); the Faerie Lord, the totem bear and the dragons are
examples of their kinds. The animal princes, dziadys, zluidni and
dziwozony have no blocks and are in the notes of the nearest kin.

Keys: creatures["faerie_lord"], ["leshy"], ["polevik"], ["vodyanoi"],
["rusalka"], ["domovoi"], ["dvorovoi"], ["bannik"], ["ovinnik"],
["zaltys"], ["totem_bear"], ["strukis"], ["firebird"], ["semargl"],
["poludnica"], ["strzyga"], ["marauding_dragon"], ["sorcerous_dragon"],
["three_headed_giant"], ["vampire"], ["onslaught_dragon"] and
["stolitzya"]."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ...models import BodyVis
from ..builder import Builder, characteristics, paragraphs, wound_ranges

if TYPE_CHECKING:
    from ...models import CreatureAttack, CreaturePower
    from ..records import Records

#: The Definitive Edition's weapons: (Ability, Init, Attack, Defense,
#: Damage), Storyguide Screen p. 4.
WEAPONS: dict[str, tuple[str, int, int, int, int]] = {
    "Fist": ("Brawl", 0, 0, 0, 0),
    "Teeth": ("Brawl", 0, 3, 1, 1),
    "Large teeth": ("Brawl", 0, 4, 1, 3),
    "Claws": ("Brawl", -1, 2, 3, 2),
    "Large claws": ("Brawl", 0, 5, 3, 4),
    "Large horns": ("Brawl", 2, 3, 2, 3),
    "Club": ("Single Weapon", 1, 2, 1, 3),
    "Great sword": ("Great Weapon", 2, 5, 2, 9),
    "Long sword and round shield": ("Single Weapon", 2, 4, 3, 6),
    "Lance": ("Single Weapon", 2, 4, 0, 5),
    "Composite bow": ("Bows", -2, 4, 0, 7),
}
#: The most and least an Ability worked back from a printed Attack is.
SKILL = (1, 10)
FATIGUE = "OK, 0, -1, -3, -5, Unconscious"
LARGE_FATIGUE = "OK, 0/0, -1/-1, -3/-3, -5, Unconscious"
SMALL_FATIGUE = "OK, -1, -3, -5, Unconscious"
TINY_FATIGUE = "OK, -3, -5, Unconscious"


@dataclass(frozen=True)
class Kind:
    """A creature as the book prints it, in its own numbers."""

    key: str
    name: str
    page: str
    might: int
    form: str
    size: int
    chars: tuple[int, int, int, int, int, int, int, int]
    #: (weapon from WEAPONS, the book's name for the attack, printed Atk).
    attacks: tuple[tuple[str, str, int], ...]
    old_soak: int
    fatigue: str
    #: (Faerie Power, rating) as printed.
    powers: tuple[tuple[str, int], ...]
    vis: tuple[tuple[int, str], ...]
    traits: dict[str, int]
    appearance: str
    notes: str
    weakness: str = "Vulnerable to iron"
    place: str = "russia"
    how_many: str = "Many"
    realm: str = "Faerie"
    might_range: str = ""
    cunning: bool = False
    extra: tuple[str, ...] = field(default_factory=tuple)


def _combat(
    b: Builder, kind: Kind
) -> tuple[list[CreatureAttack], list[tuple[str, int, str]], int]:
    """The attacks, the Abilities they use and the Soak, worked out again."""
    _int, _per, _pre, _com, strength, stamina, dex, qik = kind.chars
    attacks: list[CreatureAttack] = []
    skills: dict[str, int] = {}
    for weapon, label, printed in kind.attacks:
        ability, init, atk, dfn, dam = WEAPONS[weapon]
        score = max(SKILL[0], min(SKILL[1], printed - dex - atk))
        score = max(score, skills.get(ability, 0))
        skills[ability] = score
        attacks.append(
            b.attack(
                label,
                qik + init,
                dex + score + atk,
                qik + score + dfn,
                strength + dam,
            )
        )
    soak = stamina + max(0, kind.old_soak - stamina - kind.size)
    abilities = [(name, score, "") for name, score in skills.items()]
    return attacks, abilities, soak


# -- the faerie powers, by Realms of Power: Faerie --

FOCUS_TECHNIQUES = {
    "Control Element": "any non-Ritual Creo, Muto, Perdo or Rego {form} effect",
    "Control Animals": "any non-Ritual Rego Animal effect",
    "Control Person": "any non-Ritual Rego Mentem effect on people",
    "Control Fertility": "any Creo effect on the fertility of fields, beasts "
    "and people (Herbam, Animal or Corpus)",
    "Glamour": "any non-Ritual Imaginem effect",
    "Healing": "any non-Ritual Creo Corpus effect that heals",
    "Communicate": "any Intellego effect that speaks with {form}",
}
FOCUS_FORMS = {
    "Control Animals": "Animal",
    "Control Person": "Mentem",
    "Control Fertility": "Herbam",
    "Glamour": "Imaginem",
    "Healing": "Corpus",
}


def _focus(
    b: Builder, label: str, power: str, form: str, rating: int, might: int, qik: int
) -> CreaturePower:
    level = min(rating * 5, might)
    magnitude = max(1, level // 5)
    words = FOCUS_TECHNIQUES[power].format(form=form)
    return b.power(
        label,
        magnitude,
        qik - magnitude,
        form,
        level=level,
        does=f"A Focus Power: {words} up to level {level} (the book's rating "
        f"of {rating}), at 1 Might point a magnitude; the cost shown is the "
        "most it can be. RoP:F p. 54.",
    )


def _power(b: Builder, name: str, rating: int, might: int, qik: int) -> CreaturePower:
    """One printed Faerie Power, as Realms of Power: Faerie prices it."""
    if name.startswith("Control Element"):
        form = name.split(": ")[1]
        return _focus(
            b, f"Control of {form}", "Control Element", form, rating, might, qik
        )
    if name in FOCUS_FORMS:
        return _focus(b, name, name, FOCUS_FORMS[name], rating, might, qik)
    if name.startswith("Communicate"):
        form = name.split(" with ")[1]
        return _focus(b, f"Speech with {form}", "Communicate", form, rating, might, qik)
    exemplar = EXEMPLARS.get(name)
    if name == "Curse" and rating >= 10 and might >= 30:
        exemplar = EXEMPLARS["Great Curse"]
    if exemplar is None:
        raise KeyError(f"No conversion for the Faerie Power {name!r}")
    label, cost, init, form, rtd, level, does = exemplar
    return b.power(
        label,
        cost,
        qik + init,
        form,
        rtd=rtd,
        level=level,
        does=f"{does} (the book's {name} {rating})",
    )


PERSONAL = ("Personal", "Sun", "Individual")
#: Each Faerie Power with an exemplar: (name, Might cost, Init modifier,
#: Form, Range/Duration/Target, level, what it does and where).
EXEMPLARS: dict[
    str, tuple[str, int, int, str, tuple[str, str, str], int | None, str]
] = {
    "Bless": (
        "Blessing",
        5,
        -10,
        "Vim",
        ("Touch", "Momentary", "Individual"),
        None,
        "Grant (Minor Virtue): bestows a Minor Virtue the faerie's nature "
        "suits, for as long as it chooses or until a condition is broken; "
        "the Might returns when it is withdrawn. RoP:F pp. 56-57",
    ),
    "Curse": (
        "Curse",
        5,
        -10,
        "Vim",
        ("Touch", "Momentary", "Individual"),
        None,
        "Grant (Minor Flaw): lays a Minor Flaw on a victim, now or when a "
        "taboo is broken; 5 levels and 1 Might more to curse a family or "
        "household. RoP:F p. 57",
    ),
    "Great Curse": (
        "Curse",
        10,
        -20,
        "Vim",
        ("Touch", "Momentary", "Individual"),
        None,
        "Grant (Major Flaw): lays a Major Flaw on a victim; 5 levels and "
        "1 Might more to curse a family or household. It cannot kill "
        "outright. RoP:F p. 57",
    ),
    "Elfshot": (
        "Elfshot",
        3,
        -3,
        "Corpus",
        ("Touch", "Momentary", "Individual"),
        25,
        "Cause Sickness: an unseen dart that strikes a serious illness "
        "into its victim. RoP:F p. 58",
    ),
    "Fear": (
        "Dread",
        3,
        -3,
        "Mentem",
        ("Voice", "Sun", "Group"),
        30,
        "Enthralling Sound: fills everyone who hears it with fear, or "
        "deepens a fear they have; a Personality roll of 9+ throws it off. "
        "RoP:F p. 58",
    ),
    "Infatuation": (
        "Infatuation",
        3,
        -3,
        "Mentem",
        ("Voice", "Sun", "Group"),
        30,
        "Enthralling Sound: fills those who hear it with desire for the "
        "faerie; a Personality roll of 9+ throws it off. RoP:F p. 58",
    ),
    "Possession": (
        "Possession",
        4,
        -4,
        "Mentem",
        ("Eye", "Sun", "Individual"),
        40,
        "Enthrallment: takes complete control of a person for a day by "
        "meeting his eye. RoP:F p. 58",
    ),
    "Shapechange Other to Animal": (
        "Transform Victim into an Animal",
        3,
        -3,
        "Animal",
        ("Voice", "Sun", "Individual"),
        30,
        "Turns one who hears it into a land animal, chosen when the faerie "
        "was made. RoP:F p. 60",
    ),
    "Brew Faerie Potions": (
        "Brew Faerie Potions",
        10,
        0,
        "Vim",
        ("Touch", "Momentary", "Individual"),
        None,
        "Craft Magical Trinket: a potion of glamour that lets its drinker "
        "use a Minor Virtue once; 15 Might for a Major one. RoP:F p. 58",
    ),
    "Enchant Objects": (
        "Enchant Objects",
        10,
        0,
        "Vim",
        ("Touch", "Momentary", "Individual"),
        None,
        "Craft Magical Trinket: a trinket of glamour that lets its holder "
        "use a Minor Virtue once; 15 Might for a Major one. RoP:F p. 58",
    ),
    "Change Size": (
        "Change of Size",
        1,
        -1,
        "Corpus",
        PERSONAL,
        5,
        "A Personal Power: grows or shrinks by steps of Size (Base 3, +2 "
        "Sun). RoP:F p. 60",
    ),
    "Shapechange to Animal": (
        "Shapechange to Animal",
        2,
        -2,
        "Animal",
        PERSONAL,
        15,
        "A Personal Power: takes a beast's shape, as the Shape of the "
        "Woodland Prowler (MuCo(An) 15)",
    ),
    "Shapechange to Object": (
        "Shapechange to Object",
        4,
        -4,
        "Terram",
        PERSONAL,
        35,
        "A Personal Power: becomes a thing, a gatepost, a stone or a log "
        "(Base 25, +2 Sun)",
    ),
    "Shapechange to Human": (
        "Human Shape",
        2,
        -2,
        "Corpus",
        PERSONAL,
        20,
        "A Personal Power: takes a human shape (Base 10, +2 Sun)",
    ),
    "Invisibility": (
        "Unseen",
        2,
        -2,
        "Imaginem",
        PERSONAL,
        20,
        "A Personal Power: as the Veil of Invisibility (PeIm 20)",
    ),
    "Insubstantial Form": (
        "Insubstantial Form",
        3,
        -3,
        "Corpus",
        PERSONAL,
        25,
        "A Personal Power: becomes a thing of air that blades pass through "
        "(MuCo(Au), Base 15, +2 Sun)",
    ),
    "Prophecy": (
        "Prophecy",
        3,
        -3,
        "Mentem",
        ("Voice", "Momentary", "Individual"),
        30,
        "A Greater Power with no Hermetic equivalent, as Hermetic magic "
        "cannot see the future: a glimpse of what is to come, given in its "
        "own way",
    ),
    "Travel": (
        "Faerie Road",
        4,
        -4,
        "Corpus",
        ("Personal", "Momentary", "Individual"),
        35,
        "A Greater Power: is at once in any place it knows, as the Leap of "
        "Homecoming (ReCo 35)",
    ),
    "Communication with Humans": (
        "Human Speech",
        0,
        0,
        "Mentem",
        PERSONAL,
        5,
        "A Personal Power: speaks and understands the tongues of men; its "
        "spare levels made it cost nothing. RoP:F p. 61",
    ),
}


def _kind(b: Builder, records: Records, kind: Kind) -> None:
    attacks, abilities, soak = _combat(b, kind)
    qik = kind.chars[7]
    powers = [_power(b, name, rating, kind.might, qik) for name, rating in kind.powers]
    for line in kind.extra:
        powers.append(EXTRA[line](b, qik))
    records.creatures[kind.key] = b.creature(
        kind.name,
        page=kind.page,
        realm=kind.realm,
        might=kind.might,
        form=kind.form,
        size=kind.size,
        cunning=kind.cunning,
        block={
            "characteristics": characteristics(*kind.chars),
            "abilities": abilities,
            "traits": kind.traits,
        },
        attacks=attacks,
        soak=soak,
        fatigue_levels=kind.fatigue,
        powers=powers,
        vis=[BodyVis(pawns, art, "in its body") for pawns, art in kind.vis],
        appearance=kind.appearance,
        notes=paragraphs(
            kind.notes,
            (
                f"Might {kind.might_range} in the book; the lowest is entered. "
                if kind.might_range
                else ""
            )
            + "Slavic faeries wax and wane with the seasons, by as much as a "
            "quarter: the Gold Court's in summer, the White Court's in "
            "winter. " + wound_ranges(kind.size),
        ),
        how_many=kind.how_many,
        place=records.places.get(kind.place),
        weakness=kind.weakness,
        tires=bool(kind.fatigue),
    )


def _breath(b: Builder, qik: int) -> CreaturePower:
    return b.power(
        "Fiery Breath",
        4,
        qik - 4,
        "Ignem",
        rtd=("Voice", "Momentary", "Group"),
        level=35,
        does="A cone of fire thirty to forty paces long and five wide at "
        "its end: +35 damage to all within it, which metal armour does not "
        "stop. The book's CrIg 35, priced as a Greater Power.",
    )


EXTRA = {"breath": _breath}


KINDS: tuple[Kind, ...] = (
    Kind(
        "faerie_lord",
        "Slavic Faerie Lord",
        "p. 84",
        30,
        "Auram",
        1,
        (3, 3, 2, 0, 2, 2, 1, 2),
        (
            ("Long sword and round shield", "Faerie sword and shield", 10),
            ("Lance", "Faerie lance", 10),
            ("Composite bow", "Faerie bow", 9),
        ),
        15,
        FATIGUE,
        (
            ("Bless", 10),
            ("Change Size", 5),
            ("Control Element: Auram", 6),
            ("Control Element: Aquam", 6),
            ("Curse", 10),
            ("Elfshot", 10),
            ("Glamour", 12),
            ("Healing", 6),
            ("Shapechange to Animal", 10),
        ),
        (),
        {"Abrupt": 4, "Valiant": 3},
        "A knight of a faerie court, in full faerie mail (Protection 9 "
        "here, the book's 13) with weapons of glamour better than any "
        "smith's.",
        "The book's example lord, sworn to Stribog, god of the winds; Might "
        "30 to 35. Faerie Lords are the Slavic Seelie and Unseelie, each "
        "with a pagan god for patron, living in courts that mirror a "
        "prince's: the Gold Court of the sun and summer, the White Court of "
        "winter and decay, whose lords are beautiful as snowflakes and "
        "appallingly lethal. Courts come in opposed pairs (a sun court on a "
        "peak, a winter court in a gorge), with auras of 6 to 8 and a gate "
        "to Arcadia near. Animal princes are lords of this kind.",
        weakness="Discomfort from iron",
        how_many="",
        might_range="30-35",
    ),
    Kind(
        "leshy",
        "Leshy",
        "p. 85",
        30,
        "Herbam",
        0,
        (2, 1, 0, 1, 0, 3, 1, 0),
        (("Club", "Club", 5),),
        5,
        FATIGUE,
        (
            ("Bless", 6),
            ("Change Size", 4),
            ("Control Animals", 4),
            ("Control Fertility", 12),
            ("Curse", 6),
            ("Glamour", 8),
            ("Shapechange to Animal", 7),
            ("Shapechange Other to Animal", 7),
        ),
        ((15, "Herbam"),),
        {"Prankster": 4},
        "A small, balding man with a long beard, bushy brows, emerald eyes "
        "and cheeks blue from his azure blood; his size changes to match "
        "the trees about him, from Size -4 to +4.",
        "Forest guardians, often mighty, each with a carefully kept "
        "territory: masters of size and shape, not malicious but "
        "mischievous, fond of leading travellers astray and of bargains, "
        "and respectful of those who see through their tricks. Presence, "
        "Strength and Quickness vary with his size; the club's damage too.",
    ),
    Kind(
        "polevik",
        "Polevik",
        "p. 85",
        20,
        "Herbam",
        0,
        (1, 1, 1, -1, 2, 1, 1, 3),
        (("Fist", "Grapple and strangle", 5),),
        3,
        FATIGUE,
        (
            ("Bless", 8),
            ("Control Element: Herbam", 5),
            ("Control Fertility", 16),
            ("Curse", 8),
            ("Healing", 4),
        ),
        ((7, "Herbam"),),
        {"Solemn": 3, "Vicious": 2},
        "Most are women, more or less human by season: bright green in "
        "spring, deep green in summer, auburn or gold in autumn, white or "
        "grey in winter; grass may grow for hair, the skin may be fresh "
        "earth and the eyes glittering stones.",
        "Field spirits, asked for their blessing at every sowing, "
        "capricious and dangerous if offended; in south Russia some are "
        "worshipped as minor gods. Once a polevik's grip draws blood she "
        "keeps it and the initiative until a round in which she wounds no "
        "one and is wounded, her Attack +5 to +10 the while. In a "
        "blossoming field she heals a wound level a round. Iron does not "
        "trouble her: the plough and sickle have accustomed her to it.",
        weakness="",
        might_range="20 and more",
    ),
    Kind(
        "vodyanoi",
        "Vodyanoi",
        "p. 86",
        15,
        "Aquam",
        0,
        (0, 1, 0, 1, 3, 3, 1, 2),
        (("Fist", "Grapple", 7),),
        5,
        FATIGUE,
        (
            ("Control Person", 4),
            ("Control Element: Aquam", 10),
            ("Curse", 10),
            ("Fear", 5),
            ("Glamour", 5),
            ("Infatuation", 5),
            ("Shapechange to Animal", 5),
        ),
        ((6, "Aquam"), (4, "Perdo")),
        {"Murderous": 4},
        "Bloated, unkempt men or women with mossy, dripping hair and green "
        "skin; or beguiling beauties; or dog-headed, horned and tailed.",
        "Water spirits, the most vicious of the common faeries, faerie "
        "born or risen from the drowned; known in Poland as topielec. Any "
        "water deep enough to drown in may hold one. It grapples to "
        "immobilize, then drags its victim under in a contest of Strength; "
        "its combat totals fall by 1 for every ten paces from its home "
        "water, where it heals a wound and a Fatigue level a round. Many "
        "keep palaces in a regio, served by the drowned.",
        might_range="15-25",
    ),
    Kind(
        "rusalka",
        "Rusalka",
        "p. 87",
        10,
        "Aquam",
        0,
        (0, 0, 1, 1, 1, 1, 0, 1),
        (("Fist", "Grapple", 5),),
        5,
        FATIGUE,
        (
            ("Control Element: Aquam", 7),
            ("Control Fertility", 5),
            ("Curse", 6),
            ("Fear", 3),
            ("Infatuation", 4),
        ),
        ((4, "Aquam"), (3, "Perdo")),
        {"Willful": 4, "Unreliable": 4},
        "Always a woman, bloated and distorted or a comely maiden.",
        "Nymphs and dryads of water and wood, capricious and "
        "untrustworthy, some risen from drowned pagans; barren women seek "
        "their blessing. Each is bound to a water or a corner of wood, even "
        "a single tree (her Control is of Herbam then, and her vis), heals "
        "a wound and a Fatigue level a round there, and in water attacks "
        "as a vodyanoi does.",
        might_range="10-15",
    ),
    Kind(
        "domovoi",
        "Domovoi",
        "p. 87",
        10,
        "Mentem",
        -1,
        (-1, 1, -1, -2, 0, 1, 2, 3),
        (("Claws", "Claws", 4),),
        3,
        SMALL_FATIGUE,
        (
            ("Bless", 5),
            ("Change Size", 2),
            ("Curse", 5),
            ("Invisibility", 5),
            ("Insubstantial Form", 5),
            ("Prophecy", 5),
            ("Shapechange to Object", 6),
        ),
        (),
        {"Loyal": 4, "Secretive": 4},
        "A small, graceful man or woman covered in fine, glossy brown hair, "
        "even on palms and soles, sometimes with horns or a tail. Rarely "
        "seen, often heard; it is bad luck to see one.",
        "House spirits under the stove or in the cellar, who keep the home "
        "and its luck for courtesy and a share of food and milk, warn of "
        "danger and opportunity, and grow fierce in a family feud. A good "
        "domovoi is more than a match for any number of zluidni, the "
        "small, spiteful, misshapen dark faeries that curse, glamour and "
        "possess in petty malice. Iron does not trouble it.",
        weakness="",
        might_range="10-15",
    ),
    Kind(
        "dvorovoi",
        "Dvorovoi",
        "p. 88",
        8,
        "Animal",
        -1,
        (-1, 2, 0, -2, 2, 2, 1, 2),
        (("Fist", "Brawl", 4),),
        4,
        SMALL_FATIGUE,
        (
            ("Bless", 5),
            ("Change Size", 2),
            ("Communicate with Animal", 5),
            ("Control Fertility", 5),
            ("Curse", 5),
            ("Infatuation", 6),
            ("Shapechange to Animal", 4),
            ("Shapechange to Object", 4),
        ),
        (),
        {"Diligent": 4, "Demanding": 4},
        "A small, gnarled man or woman, often strikingly disfigured, a nose "
        "to the chin; or half beast, like the animals it guards; or a "
        "gatepost.",
        "Spirits of courtyard, farmyard and pasture, good guardians of "
        "sheep and cattle but less tractable than the domovoi, and lusty, "
        "prone to seducing mortals; the Slavs fool them with dolls and "
        "scarecrows.",
        weakness="Discomfort from iron",
        might_range="8-12",
    ),
    Kind(
        "bannik",
        "Bannik",
        "p. 88",
        5,
        "Aquam",
        -2,
        (-2, 0, -3, -3, 0, 1, 2, 3),
        (("Claws", "Claw", 4),),
        2,
        TINY_FATIGUE,
        (
            ("Control Element: Aquam", 5),
            ("Insubstantial Form", 5),
            ("Invisibility", 4),
            ("Prophecy", 5),
        ),
        (),
        {"Diligent": 4, "Easily offended": 4},
        "Small and seldom seen.",
        "Spirits of the bath-house (in the north, the sauna), who keep the "
        "fire lit and the cistern full, caulk the walls and fetch wood, "
        "but insist on their turn: every fourth bath is theirs, and an "
        "intruder is cruelly clawed. They prophesy, vaguely.",
        might_range="5-10",
    ),
    Kind(
        "ovinnik",
        "Ovinnik",
        "p. 89",
        8,
        "Ignem",
        -3,
        (0, 1, -2, -3, 0, 1, 2, 2),
        (("Claws", "Claws", 4),),
        3,
        "OK, -5, Unconscious",
        (
            ("Control Element: Ignem", 5),
            ("Curse", 5),
            ("Elfshot", 5),
            ("Shapechange to Animal", 4),
        ),
        ((3, "Ignem"),),
        {"Malicious": 4, "Lazy": 4},
        "A large, mangy, lazy black cat lounging about the barn.",
        "Barn guardians, the most dangerous of the house spirits: angered, "
        "they can burn down the barns they keep. Their scratches fester: "
        "twice the usual wound penalty to Chirurgy and recovery rolls.",
        weakness="Discomfort from iron",
        might_range="8-12",
    ),
    Kind(
        "zaltys",
        "Zaltys",
        "p. 89",
        5,
        "Ignem",
        -4,
        (2, 2, -2, 0, -2, -2, 0, -1),
        (),
        0,
        "OK, Unconscious",
        (
            ("Bless", 5),
            ("Control Element: Ignem", 4),
            ("Control Fertility", 5),
            ("Curse", 5),
            ("Prophecy", 5),
        ),
        ((3, "Intellego"),),
        {"Lazy": 5, "Benevolent": 4},
        "A small, brightly coloured snake basking on the warm stones by the hearth.",
        "Lithuanian house snakes, sacred to the sun goddess Saule, found "
        "only in Lithuanian auras and regiones. They do no housework but "
        "are prized for their wisdom and luck; keeping one pleases Saule. "
        "Ill-treated, or if the house turns from the old gods, it leaves "
        "and takes the family's luck. Iron does not trouble it. (The "
        "book's Strength is missing; -2 is taken.)",
        weakness="",
        place="baltic",
        might_range="5-10",
    ),
    Kind(
        "totem_bear",
        "Totem Bear",
        "p. 90",
        15,
        "Animal",
        3,
        (1, 3, 2, -3, 6, 7, 1, 1),
        (("Large claws", "Maul", 13), ("Fist", "Tackle (knocks down)", 7)),
        30,
        LARGE_FATIGUE,
        (
            ("Bless", 10),
            ("Control Animals", 6),
            ("Control Element: Herbam", 6),
            ("Control Fertility", 8),
            ("Curse", 10),
            ("Prophecy", 10),
            ("Shapechange to Object", 6),
        ),
        ((8, "Animal"), (3, "Vim")),
        {"Dignified": 3, "Aggressive": 3},
        "A bear larger than any mundane one, that speaks plainly if not eloquently.",
        "The book's example of a clan's totem beast: every clan has its "
        "animal mascots, and most pagan villages one or more such beasts, "
        "intelligent and able to speak, whom the villagers consult, honour "
        "and may worship; their coming is an omen. A tackle that wounds "
        "knocks its target down.",
        might_range="15-20",
        how_many="",
    ),
    Kind(
        "strukis",
        "Strukis, the Great Pike",
        "p. 90",
        40,
        "Aquam",
        3,
        (4, 3, 2, 2, 3, 2, 1, 0),
        (("Large teeth", "Bite", 8),),
        9,
        LARGE_FATIGUE,
        (
            ("Bless", 10),
            ("Brew Faerie Potions", 5),
            ("Change Size", 6),
            ("Communication with Humans", 10),
            ("Control Animals", 6),
            ("Control Person", 10),
            ("Control Element: Aquam", 10),
            ("Curse", 10),
            ("Enchant Objects", 5),
            ("Glamour", 10),
            ("Prophecy", 10),
            ("Shapechange to Human", 5),
        ),
        ((15, "Aquam"), (5, "Mentem"), (5, "Intellego")),
        {"Domineering": 4, "Greedy": 4},
        "A vast pike that can take the shape of a great faerie lord.",
        "King of fish and lord of the water faeries, worshipped most near "
        "Lake Strukhalis in Poland: a magical faerie beast that can be a "
        "lord, not a lord that can be a beast. His rule over the world's "
        "fish fails for one hour a year, when he sleeps and dreams "
        "prophecies. Knowledge flows to him down every Slavic stream and "
        "lake, but he is a miser greedy for slaves, and whoever enters his "
        "palace is likely to be kept. Immersed, he heals two wound and "
        "Fatigue levels a round.",
        weakness="Discomfort from iron",
        place="lake_strukhalis",
        how_many="",
    ),
    Kind(
        "firebird",
        "Zhar-Ptitsa, the Firebird",
        "p. 91",
        50,
        "Ignem",
        -2,
        (4, 3, 0, 0, 1, 3, 3, 5),
        (("Claws", "Talons", 10),),
        5,
        TINY_FATIGUE,
        (
            ("Bless", 10),
            ("Control Element: Ignem", 15),
            ("Curse", 10),
            ("Travel", 21),
        ),
        ((30, "Ignem"),),
        {"Curious": 3, "Thief": 3},
        "A cassowary of fire; one feather from its wing lights a feast hall "
        "brighter than the sun, yet hurts no one who looks at it.",
        "The most famous, most potent and most elusive of the legendary "
        "Slavic beasts, dwelling in the garden of the sun in the uttermost "
        "East and eating golden apples and fruits bright as gems. It shows "
        "no true intelligence but is a cunning thief of bright, sweet "
        "things, found only in strong regiones near Arcadia, and so "
        "powerful it can open a gate to Arcadia at need, which makes it "
        "hard to catch and harder to keep. Nastassia Baramov's obsession; "
        "sacred to Dazhdbog.",
        weakness="Discomfort from iron",
        place="slavic_arcadia",
        how_many="",
        cunning=True,
    ),
    Kind(
        "semargl",
        "Semargl",
        "p. 91",
        30,
        "Animal",
        1,
        (2, 3, 0, 0, 3, 4, 2, 2),
        (("Teeth", "Bite", 7),),
        7,
        FATIGUE,
        (
            ("Bless", 10),
            ("Communicate with Animal", 10),
            ("Control Element: Auram", 10),
            ("Curse", 10),
            ("Fear", 10),
            ("Insubstantial Form", 5),
            ("Travel", 28),
        ),
        ((10, "Animal"), (10, "Auram")),
        {"Hungry": 3},
        "A dog with an eagle's wings and tail, feathered from head to tail.",
        "The strangest of the chimaeric beasts: swift, voracious and "
        "cunning, a servant of the gods whose duty is a mystery, perhaps "
        "their messenger, as Hermes was.",
        place="slavic_arcadia",
        how_many="",
        cunning=True,
    ),
    Kind(
        "poludnica",
        "Poludnica",
        "p. 92",
        5,
        "Mentem",
        0,
        (0, -2, -3, -5, 0, 0, 0, 0),
        (),
        0,
        "",
        (("Fear", 2), ("Prophecy", 3)),
        (),
        {"Disturbed": 2},
        "No body at all.",
        "Revenants common in Poland: pagan souls that never reached "
        "Arcadia, or Christians badly buried or killed by evil faeries. "
        "They seldom speak clearly, but send their kin prophetic or "
        "maddening dreams, or warnings of coming tragedy. The pagan dead, "
        "the dziadys, are ritually feasted four times a year.",
        weakness="",
        place="poland",
        might_range="5-15",
    ),
    Kind(
        "strzyga",
        "Strzyga",
        "p. 92",
        10,
        "Corpus",
        1,
        (1, 1, 0, -1, 2, 2, 1, 1),
        (("Fist", "Strangle", 6),),
        5,
        FATIGUE,
        (
            ("Control Person", 8),
            ("Curse", 5),
            ("Fear", 8),
            ("Glamour", 6),
            ("Possession", 10),
        ),
        ((3, "Perdo"), (2, "Vim")),
        {"Malicious": 3},
        "Looks human; born with two full sets of teeth.",
        "A Polish changeling with two spirits, human and faerie; baptism "
        "touches only the human one. It may live and die a normal life; "
        "then, the soul gone to judgement, the faerie spirit sends the "
        "body out as a strangler at the crossroads, gaining Might from "
        "its victims' last breaths. It has two hearts: killed or "
        "incapacitated, it rises at once, whole, and must be killed again.",
        place="poland",
        might_range="10-15",
    ),
    Kind(
        "marauding_dragon",
        "Marauding Dragon",
        "p. 93",
        40,
        "Ignem",
        5,
        (-1, 2, 0, 0, 8, 8, -2, -3),
        (("Large claws", "Claw and bite", 15),),
        20,
        "OK/OK, 0/0, -1/-1, -3/-3, -5/-5, Unconscious",
        (("Fear", 20),),
        ((10, "Animal"), (10, "Ignem"), (10, "Perdo"), (5, "Vim")),
        {"Ravenous": 5},
        "A four-limbed, fire-breathing serpent with bat wings, Size +5 or more.",
        "The dragons of the northern Carpathians are the worst monsters of "
        "the Slavic lands, faerie, unlike most of Europe's, which are of "
        "Magic; magi burn to know whether the two are kin. This kind is "
        "strong, hungry and resilient, but not clever: the one Krakus "
        "killed at Krakow, by an alchemical trick, as arms could not.",
        place="tatras",
        how_many="",
        cunning=True,
        extra=("breath",),
    ),
    Kind(
        "sorcerous_dragon",
        "Sorcerous Dragon",
        "p. 93",
        50,
        "Vim",
        4,
        (2, 3, 2, 1, 6, 6, -1, -2),
        (("Large claws", "Claw and bite", 15),),
        15,
        "OK, 0/0, -1/-1, -3/-3, -5/-5, Unconscious",
        (
            ("Brew Faerie Potions", 5),
            ("Change Size", 6),
            ("Control Person", 10),
            ("Control Element: Ignem", 10),
            ("Control Element: Auram", 10),
            ("Fear", 10),
            ("Glamour", 12),
            ("Infatuation", 10),
            ("Invisibility", 5),
            ("Shapechange to Human", 6),
            ("Shapechange to Object", 6),
        ),
        ((5, "Ignem"), (15, "Perdo"), (15, "Vim")),
        {"Devious": 4, "Murderous": 3},
        "A four-limbed, fire-breathing serpent with bat wings, Size +4 or "
        "less, often in a man's shape.",
        "The subtler kind of Slavic dragon: still dangerous in body, but "
        "intelligent, magically gifted and vicious. Its size changes never "
        "take it above +4.",
        place="tatras",
        how_many="",
        extra=("breath",),
    ),
    Kind(
        "three_headed_giant",
        "Three-Headed Giant",
        "p. 94",
        15,
        "Terram",
        3,
        (-1, 4, -3, -3, 4, 4, -1, -2),
        (("Great sword", "Greatsword", 12),),
        10,
        LARGE_FATIGUE,
        (
            ("Communicate with Herbam", 6),
            ("Control Element: Terram", 8),
            ("Fear", 8),
            ("Shapechange to Object", 6),
        ),
        ((6, "Terram"), (4, "Perdo")),
        {"Greedy": 3, "Murderous": 4},
        "A huge, three-headed brute.",
        "The book's example of the ogres and giants the Poles call "
        "dziwozony and the Russians norka: huge, very strong, dim, and "
        "vulnerable to Christian rites and relics, not much troubled by "
        "iron. Many rule earth, are proof against weapons, melt into rock, "
        "earth, water or mud and move through it, and can smell a mortal's "
        "nationality. They come as siblings with ever more heads, three, "
        "six, nine, about five Might a head. In its own terrain it heals a "
        "wound and a Fatigue level a round, even when slain.",
        weakness="Discomfort from iron; vulnerable to Christian rites and relics",
        place="tatras",
    ),
    Kind(
        "onslaught_dragon",
        "Onslaught Dragon",
        "p. 100",
        40,
        "Auram",
        5,
        (2, 3, 3, 1, 7, 8, 0, 0),
        (("Large teeth", "Bite (swallows)", 12), ("Large claws", "Claws", 12)),
        20,
        "OK/OK, 0/0, -1/-1, -3/-3, -5/-5, Unconscious",
        (
            ("Communicate with Animal", 10),
            ("Control Element: Auram", 15),
            ("Control Element: Aquam", 15),
            ("Fear", 12),
            ("Glamour", 10),
        ),
        ((10, "Auram"), (10, "Aquam"), (10, "Perdo"), (10, "Vim")),
        {"Destructive": 6},
        "A wingless serpent that flies, with massive jaws, mane and horns, "
        "gold, silver or ebony, four limbs and terrible claws; it brings "
        "thunder and lightning, not flame.",
        "The spirits of the Mongols, come since 1206 to ravage the dreams "
        "of the Slavs: they swarm through Slavic Earth and the clan lands "
        "of Slavic Hell, have laid three princedoms waste, and gnaw at the "
        "roots of the World Tree. Whoever its bite wounds must roll a die "
        "+ Size of 6+ or be swallowed, to cut his way out of the throat "
        "(Soak 12) or the stomach (Soak 15), whose acids do 20 a round. It "
        "also speaks with plants and people.",
        place="slavic_arcadia",
    ),
)


def build(records: Records) -> None:
    b = records.b
    for kind in KINDS:
        _kind(b, records, kind)
    _vampire(records)
    _stolitzya(records)


def _vampire(records: Records) -> None:
    b = records.b
    chars = (1, 1, -3, 1, 2, 2, 1, 2)
    kind = Kind(
        "vampire",
        "Upiór (Vampire)",
        "p. 95",
        10,
        "Corpus",
        0,
        chars,
        (("Teeth", "Bite", 4), ("Fist", "Strangle", 5)),
        5,
        "",
        (),
        (),
        {},
        "",
        "",
    )
    attacks, abilities, soak = _combat(b, kind)
    qik = chars[7]

    def power(name: str, cost: int, form: str, level: int, does: str) -> CreaturePower:
        return b.power(name, cost, qik - cost, form, level=level, does=does)

    records.creatures["vampire"] = b.creature(
        "Upiór (Vampire)",
        page="p. 95",
        realm="Infernal",
        might=10,
        form="Corpus",
        block={
            "characteristics": characteristics(*chars),
            "abilities": abilities,
            "traits": {"Murderous": 5},
        },
        attacks=attacks,
        soak=soak,
        fatigue_levels="OK, 0, -1, -3, -5, falls to dust",
        powers=[
            power(
                "Confusion of the Numb Will",
                2,
                "Mentem",
                15,
                "As the spell (ReMe 15).",
            ),
            power(
                "Shape of the Furred Slinker",
                3,
                "Corpus",
                25,
                "Becomes a rat (MuCo 25).",
            ),
            power("Broom of the Winds", 2, "Auram", 15, "As the spell (ReAu 15)."),
            power(
                "The Iron Grasp",
                2,
                "Corpus",
                15,
                "+3 to its grip: Strength, and the strangle's Attack and "
                "Damage (MuCo 15).",
            ),
        ],
        vis=[
            BodyVis(1, "Perdo", "diabolically tainted"),
            BodyVis(1, "Vim", "diabolically tainted"),
            BodyVis(1, "Corpus", "diabolically tainted"),
        ],
        how_many="Many",
        place=records.places.get("russia"),
        weakness=(
            "Sunlight drains 3 Might a round, then a wound a round until it "
            "is dust; bright light 1 Might a round a magnitude past the first "
            "(a strong lantern as level 10, a bonfire as 15); it cannot "
            "enter holy ground; on a road it needs a Might point more and "
            "attacks at -3, at a crossroads' centre three more and -6; and a "
            "loving vigil kept three nights over the body, if buried in holy "
            "ground, stops it ever rising."
        ),
        notes=paragraphs(
            "Called zmory, upiory or martwiec in Poland, oboroten in "
            "Russia: not made by biting but by an Infernal pact, giving up "
            "the soul for a semblance of undeath; the damned rises a few "
            "nights after burial to hunt. It kills by strangling more than "
            "by biting. A bite or strangle that wounds keeps its grip (a "
            "Strength contest to break), taking a wound a round, while it "
            "uses its powers. Infernal Might 10 to 15 when new, more for "
            "the old, who trade Might to their patrons for better gifts.",
            "Spent Might returns after a day's rest in its sanctuary. Its "
            "permanent Might rises a point of experience for each mortal it "
            "kills and falls one for each night it does not; at zero its "
            "soul goes to Hell. Beaten to no wound levels it falls to grave "
            "dust and rises at the next dusk unless the dust is thrown in "
            "water or otherwise scattered, when it takes a stress die x 10 "
            "days to come back, losing Might the while. Perdo Vim made for "
            "the purpose destroys its Might outright.",
            "Converted: the powers keep the book's levels and Might costs, "
            "Init Qik less the cost.",
        ),
    )


def _stolitzya(records: Records) -> None:
    b = records.b
    chars = (5, 2, 4, -5, 7, 3, -3, -3)

    def power(
        name: str,
        cost: int,
        form: str,
        rtd: tuple[str, str, str],
        level: int | None,
        does: str,
    ) -> CreaturePower:
        return b.power(name, cost, -3 - cost, form, rtd=rtd, level=level, does=does)

    records.creatures["stolitzya"] = b.creature(
        "Stolitzya the Swimmer",
        page="p. 136",
        realm="Magic",
        might=45,
        form="Animal",
        size=4,
        cunning=True,
        confidence=(1, 3),
        age="About 200",
        place=records.places.get("pripet_marsh"),
        block={
            "characteristics": characteristics(*chars),
            "abilities": [("Brawl", 10, "")],
            "traits": {"Lazy": 4, "Irritable": 2},
            "reputations": {
                "Monster (local peasants)": 3,
                "Dead (Novgorod Tribunal)": 2,
                "Legendary (House Bjornaer)": 2,
            },
        },
        attacks=[b.attack("Bite (swallows)", -3, 11, 8, 10)],
        soak=31,
        fatigue_levels="OK, 0/0, -1/-1, -3/-3, -5/-5, Unconscious",
        powers=[
            power(
                "Man into Sprat",
                7,
                "Corpus",
                ("Sight", "Sun", "Individual"),
                35,
                "Turns a man as far off as she can see into a fish of about "
                "Size -3. The book's MuCo 35, Penetration 30.",
            ),
            power(
                "Steel Shell",
                8,
                "Animal",
                ("Personal", "Sun", "Individual"),
                40,
                "Her last defence: her shell becomes a gleaming steel dome "
                "(+15 Soak), her head drawn in under her horny forelimbs, "
                "and she sinks into deep water. The book's MuAn 40.",
            ),
            power(
                "Dominion of the Swamp",
                8,
                "Herbam",
                ("Voice", "Diameter", "Structure"),
                40,
                "Whips plants and water within 300 yards into a maelstrom: "
                "+5 damage to everyone in it who fails a stress die + Dex + "
                "Swim or Athletics of 6+, and the same roll to do anything "
                "but hold position. The book's ReHe(Aq) 40.",
            ),
            power(
                "Speech",
                1,
                "Animal",
                ("Personal", "Concentration", "Individual"),
                5,
                "She can still speak human tongues at will, though her "
                "attention is hard to hold. The book's ReAn 5.",
            ),
        ],
        appearance="A great black-backed turtle grown so vast her shell "
        "looks like a sunken island, her encrusted beak and head as big as "
        "a house.",
        notes=paragraphs(
            "Pripet Maior's founder, a near-legendary Bjornaer who went into "
            "Final Twilight over forty years ago (the book also says thirty) "
            "and stayed in her heart-beast, augmented by Muto and steeped in "
            "magic by a century and a half of longevity potions; most of "
            "Pripet's magi were her apprentices and believe her queen of the "
            "marsh's heart. Susan of Wicklow says she saw her about fifteen "
            "years ago; whether she lives is the troupe's to decide.",
            "Her bite swallows a man of Size 0 or less who takes a wound "
            "unless he rolls Size against 6+, one higher for each wound past "
            "the first: a round dazed in her throat (Soak 12) unless he makes "
            "a stress die + Int of 9+, then +30 damage a round from the "
            "stones in her stomach (Soak 20). Given a hundred feet of open "
            "water she rams people, banks or floating islands, her bow wave "
            "swamping all near, as Mighty Torrent of Water; surfacing under "
            "a foe she can shatter a boat or tear an island apart, and is "
            "very hard to hurt.",
            "Her last Arts, for resistance only: Cr 24, In 29, Mu 37, Pe 26, "
            "Re 29, An 34, Aq 30, Au 16, Co 33, He 24, Ig 6, Im 13, Me 19, "
            "Te 26, Vi 31.",
            "Converted: the book prints totals of Attack +20 to +25 and "
            "Damage +30 to +45 on its old scale; here Brawl 10 with her "
            "jaws (Large teeth) gives the totals shown, and her Soak is her "
            "Stamina and the old Soak beyond Stamina and Size. Her powers "
            "keep the book's levels at a magnitude a Might point, Init Qik "
            "less the cost (the Alps pack's reading for the Magic realm). "
            + wound_ranges(4),
        ),
    )
