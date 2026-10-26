"""The saints and their miracles, as the books give them: each saint's
Divine Might, what he or she is patron of, feast day and powers, and each
power's Might cost, Initiative and Form, summarized.

- Realms of Power: The Divine pp. 88-91: the powers and curses saints
  use, the four ranks of saint (the Blessed Virgin, Might 100; greater
  saints 75; area saints 50; local saints 25), five sample saints and a
  list of others by rank. A saint's powers should cost no more in all
  than a fifth of its Might (a rule of thumb, p. 89).
- The Sundered Eagle pp. 136-137: the powers Greek saints favour (six new
  ones, and five of RoP: The Divine's), and the Greek saints by rank.
- The Contested Isle pp. 134-138: Ireland's saints, with their feasts and
  powers, and eighteen new powers and curses for Irish saints. Anyone of
  Irish birth may call on Saints Patrick, Brigid and Columba as patrons
  (p. 134).

Two books give a "Tame the Wild Beast": The Sundered Eagle's sends a beast
away in peace (2 points), The Contested Isle's gives a divine animal
companion (3 points); each saint has its own book's. The Contested Isle's
"Dysentric Infliction" is RoP: The Divine's Dysenteric Infliction.

The errata change nothing here. Pattern: a catalog as plain tables (dicts
of frozen records), filtered by the books in play."""

from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass

from .. import sourcebooks

SOURCE = (
    "Realms of Power: The Divine pp. 88-91; The Sundered Eagle pp. 136-137; "
    "The Contested Isle pp. 134-138"
)
ROPD = "RoP:D"
TSE = "TSE"
TCI = "TCI"

#: The ranks of saint and each one's Divine Might (RoP: The Divine p. 89).
MARY_MIGHT = 100
RANKS: dict[str, int] = {"greater": 75, "area": 50, "local": 25}


@dataclass(frozen=True)
class Power:
    """A saint's miracle or curse: its Might cost, Initiative, Form and
    what it does, in a line."""

    name: str
    points: int
    init: int
    form: str
    does: str
    book: str
    page: int
    curse: bool = False

    @property
    def cited(self) -> str:
        return f"{sourcebooks.SOURCEBOOKS.get(self.book, self.book)} p. {self.page}"

    @property
    def line(self) -> str:
        """ "Expel Demons, 1 point, Init +15, Vim": the book's heading."""
        noun = "point" if self.points == 1 else "points"
        return f"{self.name}, {self.points} {noun}, Init {self.init:+d}, {self.form}"


def _p(
    key: str,
    name: str,
    points: int,
    init: int,
    form: str,
    does: str,
    book: str,
    page: int,
    curse: bool = False,
) -> tuple[str, Power]:
    return key, Power(name, points, init, form, does, book, page, curse)


#: Every power, by key.
POWERS: dict[str, Power] = dict(
    [
        # Realms of Power: The Divine p. 88: powers.
        _p(
            "acknowledgment_of_evil",
            "Acknowledgment of Evil",
            1,
            10,
            "Vim",
            "Demons within voice range declare themselves; Penetration is "
            "the saint's Might less 5 times the cost.",
            ROPD,
            88,
        ),
        _p(
            "apparition",
            "Apparition",
            0,
            20,
            "Imaginem",
            "The saint appears in person, still beyond physical harm.",
            ROPD,
            88,
        ),
        _p(
            "celestial_immunity",
            "Celestial Immunity",
            5,
            15,
            "Corpus",
            "Immune to all physical harm while the danger lasts.",
            ROPD,
            88,
        ),
        _p(
            "cure_blindness",
            "Cure Blindness",
            2,
            3,
            "Corpus",
            "Sight restored for good, whatever took it.",
            ROPD,
            88,
        ),
        _p(
            "expel_demons",
            "Expel Demons",
            1,
            15,
            "Vim",
            "A demon driven from a person or place back to Hell: the saint's "
            "Might + a stress die (no botch) against the demon's.",
            ROPD,
            88,
        ),
        _p(
            "grant_of_serenity",
            "Grant of Serenity",
            1,
            -10,
            "Mentem",
            "Calms the petitioner and ends any malign Mentem spell on him.",
            ROPD,
            88,
        ),
        _p(
            "mass_healing",
            "Mass Healing",
            5,
            0,
            "Corpus",
            "A crowd healed of every disease, wound and affliction "
            "(not Decrepitude, nor aged Characteristics).",
            ROPD,
            88,
        ),
        _p(
            "raise_the_dead",
            "Raise the Dead",
            7,
            0,
            "Corpus",
            "Life restored to a corpse whose soul is not yet in heaven.",
            ROPD,
            88,
        ),
        _p(
            "resist_temptation",
            "Resist Temptation",
            1,
            5,
            "Mentem",
            "Magic Resistance equal to the saint's Might against Infernal temptation.",
            ROPD,
            88,
        ),
        _p(
            "sanctuary_of_virginity",
            "Sanctuary of Virginity",
            4,
            10,
            "Corpus",
            "A follower's virginity protected by some miracle.",
            ROPD,
            88,
        ),
        _p(
            "scourging_of_snakes",
            "Scourging of Snakes",
            4,
            13,
            "Animal",
            "Snakes driven from an island as large as Ireland, for good.",
            ROPD,
            88,
        ),
        _p(
            "straighten_the_crippled",
            "Straighten the Crippled",
            3,
            10,
            "Corpus",
            "The lame and deformed healed (not Decrepitude or Warping).",
            ROPD,
            88,
        ),
        _p(
            "the_dutiful_shepherd",
            "The Dutiful Shepherd",
            4,
            10,
            "Imaginem",
            "The saint's image leads a lost petitioner to safety: +10 Soak "
            "and Magic Resistance 10 meanwhile.",
            ROPD,
            88,
        ),
        _p(
            "the_faithful_made_whole",
            "The Faithful Made Whole",
            4,
            15,
            "Corpus",
            "All disease cured and all wounds healed.",
            ROPD,
            88,
        ),
        _p(
            "the_incombustible_shroud",
            "The Incombustible Shroud",
            3,
            20,
            "Ignem",
            "Immune to fire, however great.",
            ROPD,
            88,
        ),
        _p(
            "the_laborers_boon",
            "The Laborer's Boon",
            1,
            10,
            "Terram",
            "A broken tool mended or a lost one replaced.",
            ROPD,
            88,
        ),
        _p(
            "the_leap_of_the_faithful",
            "The Leap of the Faithful",
            5,
            5,
            "Corpus",
            "One person carried at once to another place, however far.",
            ROPD,
            88,
        ),
        _p(
            "tomorrows_bounty",
            "Tomorrow's Bounty",
            2,
            0,
            "Herbam",
            "Food at once for a large crowd.",
            ROPD,
            88,
        ),
        # Realms of Power: The Divine p. 89: curses.
        _p(
            "blindness",
            "Blindness",
            1,
            8,
            "Corpus",
            "The target blinded until magic or miracle mends it.",
            ROPD,
            89,
            curse=True,
        ),
        _p(
            "blisters_of_humility",
            "Blisters of Humility",
            1,
            12,
            "Corpus",
            "Boils for a week: -6 to all physical actions.",
            ROPD,
            89,
            curse=True,
        ),
        _p(
            "dysenteric_infliction",
            "Dysenteric Infliction",
            5,
            9,
            "Corpus",
            "A fatal, wretched dysentery.",
            ROPD,
            89,
            curse=True,
        ),
        _p(
            "flabbergast_the_impertinent",
            "Flabbergast the Impertinent",
            2,
            3,
            "Mentem",
            "A night's snoring sleep no magic can break: two long-term "
            "Fatigue levels down by morning.",
            ROPD,
            89,
            curse=True,
        ),
        _p(
            "humility_of_caesar",
            "Humility of Caesar",
            1,
            12,
            "Animal or Corpus",
            "Thrown from his horse, or flat on his face afoot.",
            ROPD,
            89,
            curse=True,
        ),
        _p(
            "ignis_domini",
            "Ignis Domini",
            4,
            18,
            "Ignem",
            "A pillar of fire from heaven: +30 damage.",
            ROPD,
            89,
            curse=True,
        ),
        _p(
            "rebuke_the_unfaithful",
            "Rebuke the Unfaithful",
            4,
            13,
            "Mentem",
            "A vision: mend some unchristian way within thirty days, or die.",
            ROPD,
            89,
            curse=True,
        ),
        _p(
            "smiting_of_the_lord",
            "Smiting of the Lord",
            4,
            13,
            "Auram",
            "A lightning bolt from the saint's hands: +35 damage.",
            ROPD,
            89,
            curse=True,
        ),
        _p(
            "swallowed_alive",
            "Swallowed Alive and Sent to Hell",
            5,
            3,
            "Terram",
            "The earth opens under the target, straight to Hell.",
            ROPD,
            89,
            curse=True,
        ),
        _p(
            "terrify_the_unbeliever",
            "Terrify the Unbeliever",
            2,
            18,
            "Mentem",
            "Flight in terror of the saint until dawn, unless a Brave (or "
            "like) roll of 12+.",
            ROPD,
            89,
            curse=True,
        ),
        _p(
            "the_earths_riches",
            "The Earth's Riches",
            3,
            10,
            "Terram",
            "Sticks and stones turned to gold and gems, as Touch of Midas: "
            "a warning against earthly reward.",
            ROPD,
            89,
            curse=True,
        ),
        _p(
            "the_feast_of_worms",
            "The Feast of Worms",
            3,
            5,
            "Corpus",
            "Maggots: +10 damage, and a Stamina stress roll of 12 or a "
            "point of Presence lost for good.",
            ROPD,
            89,
            curse=True,
        ),
        # The Sundered Eagle p. 136: the Greek saints' powers.
        _p(
            "healing",
            "Healing",
            2,
            7,
            "Corpus",
            "Every wound healed, any disease cured, any physical impairment remedied.",
            TSE,
            136,
        ),
        _p(
            "overstepping_the_temporal_bounds",
            "Overstepping the Temporal Bounds",
            5,
            9,
            "Mentem",
            "Glimpses of past and future, in riddles: the petitioner has "
            "Premonitions or Visions for the day.",
            TSE,
            136,
        ),
        _p(
            "feed_the_hungry",
            "Feed the Hungry",
            1,
            3,
            "Herbam",
            "Nourishing food for as many as the saint sees fit.",
            TSE,
            136,
        ),
        _p(
            "relief_from_natural_disasters",
            "Relief from Natural Disasters",
            5,
            6,
            "Aquam or Terram",
            "A mundane storm, earthquake or the like halted; from a "
            "supernatural one, the petitioner carried up to a hundred miles "
            "away.",
            TSE,
            136,
        ),
        _p(
            "tame_the_wild_beast_tse",
            "Tame the Wild Beast",
            2,
            5,
            "Animal",
            "A hostile beast of any size departs in peace.",
            TSE,
            136,
        ),
        _p(
            "gift_of_endurance",
            "Gift of Endurance",
            3,
            6,
            "Corpus",
            "No need to eat or sleep, and no harm from heat or cold, for as "
            "many days as the saint's Might.",
            TSE,
            136,
        ),
        # The Contested Isle pp. 137-138: the Irish saints' powers.
        _p(
            "banish_magical_monster",
            "Banish Magical Monster",
            0,
            5,
            "Vim",
            "As Demon's Eternal Oblivion, against a magical beast: if it "
            "Penetrates, its Might falls by the saint's for good.",
            TCI,
            137,
        ),
        _p(
            "bless_the_book",
            "Bless the Book",
            2,
            2,
            "Aquam",
            "A book made proof against water forever.",
            TCI,
            137,
        ),
        _p(
            "borne_up_by_angels",
            "Borne up by Angels",
            2,
            20,
            "Corpus",
            "Angels (Divine Might 15) slow a deadly fall and set him down.",
            TCI,
            137,
        ),
        _p(
            "call_forth_the_waters",
            "Call Forth the Waters",
            4,
            1,
            "Aquam",
            "A great wave upon a shore, or a spring of fresh water.",
            TCI,
            137,
        ),
        _p(
            "counting_sheep",
            "Counting Sheep",
            3,
            5,
            "Animal",
            "A flock lost or given to the poor is whole again when counted.",
            TCI,
            137,
        ),
        _p(
            "cure_madness",
            "Cure Madness",
            4,
            0,
            "Mentem",
            "Insanity healed, the petitioner's or another's.",
            TCI,
            137,
        ),
        _p(
            "hide_fugitive",
            "Hide Fugitive",
            1,
            13,
            "Imaginem",
            "The petitioner seems a natural feature to sight, sound and touch.",
            TCI,
            137,
        ),
        _p(
            "multitude_of_fish",
            "Multitude of Fish",
            2,
            9,
            "Aquam",
            "Fish return in plenty to waters where they had failed.",
            TCI,
            137,
        ),
        _p(
            "protect_the_wild_prey",
            "Protect the Wild Prey",
            5,
            3,
            "Animal",
            "A wild beast blessed: hounds shun it and weapons fail until sunset.",
            TCI,
            137,
        ),
        _p(
            "shatter_idol",
            "Shatter Idol",
            2,
            9,
            "Terram",
            "A stone idol lately worshipped crumbles to rubble.",
            TCI,
            137,
            curse=True,
        ),
        _p(
            "still_the_waves",
            "Still the Waves",
            5,
            4,
            "Aquam",
            "Waters stand still as if frozen, or a ship has one calm voyage.",
            TCI,
            137,
        ),
        _p(
            "strange_fruit",
            "Strange Fruit",
            2,
            5,
            "Herbam",
            "A tree bears edible fruit, of any kind, in or out of season.",
            TCI,
            137,
        ),
        _p(
            "tame_the_wild_beast_tci",
            "Tame the Wild Beast",
            3,
            5,
            "Animal",
            "A divine animal companion, unageing while the petitioner lives; "
            "betraying it brings the saint's curse.",
            TCI,
            137,
        ),
        _p(
            "the_captive_made_free",
            "The Captive Made Free",
            5,
            4,
            "Terram",
            "Prison walls break, doors open and chains fall.",
            TCI,
            138,
        ),
        _p(
            "the_unquenchable_fire",
            "The Unquenchable Fire",
            2,
            6,
            "Ignem",
            "A hearth fire that never goes out.",
            TCI,
            138,
        ),
        _p(
            "the_sky_made_light",
            "The Sky Made Light",
            2,
            9,
            "Auram",
            "Storm and cloud, even magical, cleared until sunset.",
            TCI,
            138,
        ),
        _p(
            "test_of_truth",
            "Test of Truth",
            2,
            9,
            "Mentem",
            "Only truth until the questioning ends; a lie brings convulsions. "
            "Even demons cannot lie.",
            TCI,
            138,
            curse=True,
        ),
        _p(
            "walk_upon_the_waters",
            "Walk Upon the Waters",
            3,
            7,
            "Corpus",
            "Water bears him as if it were stone.",
            TCI,
            138,
        ),
    ]
)

#: The powers Greek saints favour (The Sundered Eagle p. 136): its six,
#: and five of RoP: The Divine's.
GREEK_POWERS: tuple[str, ...] = (
    "healing",
    "overstepping_the_temporal_bounds",
    "feed_the_hungry",
    "relief_from_natural_disasters",
    "tame_the_wild_beast_tse",
    "gift_of_endurance",
    "acknowledgment_of_evil",
    "apparition",
    "expel_demons",
    "resist_temptation",
    "sanctuary_of_virginity",
)


@dataclass(frozen=True)
class Saint:
    """A saint: name, Divine Might, patronage, feast day (if the book gives
    it), powers (keys of POWERS; none where the book lists only the name)
    and the book. `anyone`: anyone may ask her aid (the Blessed Virgin,
    The Church p. 13); `irish_patron`: anyone of Irish birth may call on
    him as a patron (The Contested Isle p. 134)."""

    name: str
    might: int
    patron_of: str
    book: str
    page: int
    powers: tuple[str, ...] = ()
    feast: str = ""
    anyone: bool = False
    irish_patron: bool = False

    @property
    def rank(self) -> str:
        if self.might >= MARY_MIGHT:
            return "the Queen of Heaven"
        return next(
            (f"{rank} saint" for rank, might in RANKS.items() if self.might >= might),
            "local saint",
        )


_GREATER, _AREA, _LOCAL = RANKS["greater"], RANKS["area"], RANKS["local"]

#: Every saint the books describe, by key. A saint in two books (Patrick
#: and Kevin in RoP: The Divine's list and The Contested Isle) is the
#: fuller book's.
SAINTS: dict[str, Saint] = {
    # Realms of Power: The Divine pp. 90-91.
    "mary": Saint(
        "The Blessed Virgin Mary",
        MARY_MIGHT,
        "the laity; women, virgins, nuns; protection against epidemics and disasters",
        ROPD,
        90,
        (
            "apparition",
            "celestial_immunity",
            "cure_blindness",
            "grant_of_serenity",
            "the_incombustible_shroud",
            "the_leap_of_the_faithful",
            "rebuke_the_unfaithful",
            "resist_temptation",
            "straighten_the_crippled",
            "the_dutiful_shepherd",
        ),
        anyone=True,
    ),
    "peter": Saint(
        "Saint Peter",
        _GREATER,
        "the Church, popes and fishermen",
        ROPD,
        90,
        (
            "acknowledgment_of_evil",
            "apparition",
            "celestial_immunity",
            "cure_blindness",
            "expel_demons",
            "mass_healing",
            "raise_the_dead",
            "sanctuary_of_virginity",
            "terrify_the_unbeliever",
            "the_laborers_boon",
            "tomorrows_bounty",
        ),
    ),
    "martin_of_tours": Saint(
        "Saint Martin of Tours",
        _AREA,
        "soldiers, horses, riders and beggars",
        ROPD,
        90,
        (
            "acknowledgment_of_evil",
            "apparition",
            "celestial_immunity",
            "expel_demons",
            "grant_of_serenity",
            "terrify_the_unbeliever",
            "the_laborers_boon",
        ),
    ),
    "guinefort": Saint(
        "Saint Guinefort",
        _LOCAL,
        "protecting local children",
        ROPD,
        91,
        (
            "blisters_of_humility",
            "grant_of_serenity",
            "resist_temptation",
            "straighten_the_crippled",
            "the_faithful_made_whole",
        ),
    ),
    "nerius": Saint(
        "Saint Nerius",
        _AREA,
        "Christian magi",
        ROPD,
        91,
        (
            "apparition",
            "celestial_immunity",
            "ignis_domini",
            "the_incombustible_shroud",
            "the_leap_of_the_faithful",
        ),
    ),
    "paul": Saint("Saint Paul", _GREATER, "Greece", ROPD, 91),
    "andrew": Saint("Saint Andrew", _GREATER, "Scotland, fishermen, sailors", ROPD, 91),
    "james_the_great": Saint(
        "Saint James the Great", _GREATER, "Spain, pilgrims, laborers", ROPD, 91
    ),
    "john_the_evangelist": Saint(
        "Saint John the Evangelist",
        _GREATER,
        "Asia Minor, friendship, writers",
        ROPD,
        91,
    ),
    "matthew": Saint(
        "Saint Matthew", _GREATER, "tax collectors, bookkeepers, bankers", ROPD, 91
    ),
    "thomas": Saint("Saint Thomas", _GREATER, "India, architects, surveyors", ROPD, 91),
    "jude": Saint("Saint Jude", _GREATER, "lost causes", ROPD, 91),
    "ambrose": Saint("Saint Ambrose", _GREATER, "bishops, learning, bees", ROPD, 91),
    "jerome": Saint("Saint Jerome", _GREATER, "scholars", ROPD, 91),
    "edward_the_confessor": Saint(
        "Saint Edward the Confessor", _AREA, "England", ROPD, 91
    ),
    "benedict": Saint(
        "Saint Benedict of Nursia", _AREA, "Europe, monks, farm workers", ROPD, 91
    ),
    "thomas_becket": Saint("Saint Thomas a Becket", _AREA, "Canterbury", ROPD, 91),
    "denis": Saint("Saint Denis", _AREA, "Paris", ROPD, 91),
    "boniface": Saint("Saint Boniface", _AREA, "Germany, brewers, tailors", ROPD, 91),
    "wenceslaus": Saint("Saint Wenceslaus", _AREA, "Bohemia", ROPD, 91),
    "finnbarr": Saint("Saint Finnbarr", _LOCAL, "Cork", ROPD, 91),
    "gilbert": Saint("Saint Gilbert", _LOCAL, "Sempringham", ROPD, 91),
    "godric": Saint("Saint Godric", _LOCAL, "Durham and Finchale", ROPD, 91),
    "david_of_thessalonike": Saint(
        "Saint David of Thessalonike", _LOCAL, "Thessalonike", ROPD, 91
    ),
    "eulogius": Saint("Saint Eulogius", _LOCAL, "Cordoba", ROPD, 91),
    "irene": Saint("Saint Irene", _LOCAL, "Thessalonica", ROPD, 91),
    "gotthard": Saint("Saint Gotthard", _LOCAL, "Hildesheim", ROPD, 91),
    "adalbert": Saint("Saint Adalbert", _LOCAL, "Prague", ROPD, 91),
    # The Sundered Eagle p. 137: the Greek saints (powers as p. 136 has
    # them: GREEK_POWERS).
    "john_chrysostom": Saint("Saint John Chrysostom", _GREATER, "preachers", TSE, 137),
    "george": Saint("Saint George", _GREATER, "soldiers", TSE, 137),
    "demetrios": Saint("Saint Demetrios", _AREA, "Thessaloniki and soldiers", TSE, 137),
    "eugenios": Saint("Saint Eugenios", _AREA, "Trebizond", TSE, 137),
    "euphemia": Saint("Saint Euphemia", _AREA, "Constantinople", TSE, 137),
    "nicholas_of_myra": Saint(
        "Saint Nicholas of Myra",
        _AREA,
        "sailors, merchants, students and children",
        TSE,
        137,
    ),
    "symeon_stylites": Saint("Saint Symeon Stylites", _AREA, "Antioch", TSE, 137),
    "hosios_loukas": Saint(
        "Saint Hosios Loukas", _LOCAL, "his monastery on Mount Helicon", TSE, 137
    ),
    "hypatios": Saint("Saint Hypatios", _LOCAL, "Rufinianae", TSE, 137),
    "leontios": Saint(
        "Saint Leontios",
        _LOCAL,
        "the monastery of St. John the Evangelist on Patmos",
        TSE,
        137,
    ),
    "prokopios": Saint("Saint Prokopios", _LOCAL, "Caesarea", TSE, 137),
    "cosmas_and_damian": Saint(
        "Saints Cosmas and Damian",
        _LOCAL,
        "physicians and suburban Constantinople",
        TSE,
        137,
    ),
    # The Contested Isle pp. 134-137: Ireland's saints.
    "patrick": Saint(
        "Saint Patrick",
        _AREA,
        "Ireland",
        TCI,
        134,
        (
            "apparition",
            "expel_demons",
            "resist_temptation",
            "scourging_of_snakes",
            "shatter_idol",
            "the_faithful_made_whole",
            "the_captive_made_free",
            "the_unquenchable_fire",
            "the_sky_made_light",
        ),
        feast="17 March",
        irish_patron=True,
    ),
    "brigid": Saint(
        "Saint Brigid of Kildare",
        _AREA,
        "Ireland",
        TCI,
        135,
        (
            "apparition",
            "call_forth_the_waters",
            "counting_sheep",
            "cure_blindness",
            "expel_demons",
            "resist_temptation",
            "sanctuary_of_virginity",
            "the_faithful_made_whole",
            "test_of_truth",
            "tomorrows_bounty",
        ),
        feast="1 February",
        irish_patron=True,
    ),
    "columba": Saint(
        "Saint Columba",
        _AREA,
        "Ireland, Derry, warriors, exiles, Scotland and Iona",
        TCI,
        135,
        (
            "acknowledgment_of_evil",
            "apparition",
            "banish_magical_monster",
            "borne_up_by_angels",
            "dysenteric_infliction",
            "expel_demons",
            "multitude_of_fish",
            "raise_the_dead",
            "resist_temptation",
            "the_dutiful_shepherd",
            "walk_upon_the_waters",
        ),
        feast="9 June",
        irish_patron=True,
    ),
    "abban": Saint(
        "Saint Abbán",
        _LOCAL,
        "the Irish Church's independence",
        TCI,
        135,
        (
            "apparition",
            "banish_magical_monster",
            "counting_sheep",
            "the_captive_made_free",
            "still_the_waves",
            "walk_upon_the_waters",
        ),
        feast="16 March",
    ),
    "kevin": Saint(
        "Saint Kevin of Glendalough",
        _LOCAL,
        "Dublin, Glendalough and crows",
        TCI,
        135,
        (
            "apparition",
            "counting_sheep",
            "protect_the_wild_prey",
            "raise_the_dead",
            "strange_fruit",
            "tame_the_wild_beast_tci",
        ),
        feast="3 June",
    ),
    "ciaran": Saint(
        "Saint Ciarán of Clonmacnoise",
        _LOCAL,
        "herdsmen and cattle",
        TCI,
        135,
        (
            "apparition",
            "bless_the_book",
            "resist_temptation",
            "tame_the_wild_beast_tci",
            "the_faithful_made_whole",
        ),
        feast="9 September",
    ),
    "malachy": Saint(
        "Saint Malachy",
        _LOCAL,
        "Armagh, visionaries and fisherfolk",
        TCI,
        136,
        (
            "apparition",
            "expel_demons",
            "multitude_of_fish",
            "the_faithful_made_whole",
            "rebuke_the_unfaithful",
        ),
        feast="3 November",
    ),
    "dympna": Saint(
        "Saint Dympna",
        _LOCAL,
        "Ghent, Tydavnet, the insane and the anxious",
        TCI,
        136,
        (
            "apparition",
            "cure_madness",
            "grant_of_serenity",
            "sanctuary_of_virginity",
            "test_of_truth",
        ),
        feast="15 May",
    ),
    "brendan": Saint(
        "Saint Brendan the Navigator",
        _LOCAL,
        "explorers, navigators, Clonfert and Ardfert",
        TCI,
        136,
        (
            "apparition",
            "expel_demons",
            "hide_fugitive",
            "raise_the_dead",
            "still_the_waves",
            "tame_the_wild_beast_tci",
        ),
        feast="16 May",
    ),
    "grellan": Saint(
        "Saint Grellan",
        _LOCAL,
        "the betrayed, those menaced by the Fir Bolg, Ballinasloe",
        TCI,
        136,
        (
            "apparition",
            "raise_the_dead",
            "swallowed_alive",
            "protect_the_wild_prey",
            "grant_of_serenity",
        ),
        feast="29 September",
    ),
    "senan": Saint(
        "Saint Senan mac Geirrcinn",
        _LOCAL,
        "Scattery Island, the Corco Baiscinn and the Uí Fhidgeinte",
        TCI,
        137,
        (
            "acknowledgment_of_evil",
            "apparition",
            "banish_magical_monster",
            "call_forth_the_waters",
            "dysenteric_infliction",
        ),
        feast="8 March",
    ),
    "cronan": Saint(
        "Saint Cronan of Tipperary",
        _LOCAL,
        "the diocese of Roscrea",
        TCI,
        137,
        (
            "apparition",
            "walk_upon_the_waters",
            "raise_the_dead",
            "tame_the_wild_beast_tci",
            "celestial_immunity",
            "bless_the_book",
            "the_sky_made_light",
        ),
        feast="28 April",
    ),
}


def in_play(books: Collection[str] | None) -> dict[str, Saint]:
    """The saints of the books in play (None: every book)."""
    return {
        key: saint
        for key, saint in SAINTS.items()
        if sourcebooks.in_play(saint.book, books)
    }


def powers_of(saint: Saint) -> tuple[Power, ...]:
    """A saint's powers: its own, or for a Greek saint the book lists by
    name only, the powers Greek saints favour."""
    keys = saint.powers or (GREEK_POWERS if saint.book == TSE else ())
    return tuple(POWERS[k] for k in keys)


def powers_in_play(books: Collection[str] | None) -> dict[str, Power]:
    return {
        key: power
        for key, power in POWERS.items()
        if sourcebooks.in_play(power.book, books)
    }
