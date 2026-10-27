"""House Criamon's Mystery: the paths, their stations and avenues, and
the stigmata (Houses of Hermes: Mystery Cults pp. 50-51, 58-73; the
Definitive Edition's Enigma, pp. 235-236, reprints the Path of the Body's
first station and agrees with it; Errata p. 55 corrects the Path of
Strife's fourth Target to 18).

The paths (pp. 58-60):

- A path has five stations, each a Major Mystery Virtue reached by
  following its avenue: an Initiation whose Script the book prints. The
  Scripts are the tradition catalog's "trad_criamon_mysteries", read by the
  Initiation season like any Mystery Cult's (PATHS names each station's).
- The guide's numbers are a Mystagogue's (p. 59): Presence + House
  Criamon Lore + the Script, against the Major Virtue's 21, less a past
  Ordeal's reduction. The printed Scripts assume a guide with Presence +
  Lore 6, and the House always provides one, so an avenue planned with no
  guide named is guided at that total; a ghostly Primus at the Cave of
  Twisting Shadows sometimes guides, with Lore 9 and the Presence he had
  in life (p. 60). A guide is anyone who knows House Criamon Lore, the
  Lore the Initiation uses (DE p. 387; p. 59); one not of the House is
  unusual, and warned of, not refused.
- The magus needs House Criamon Lore of at least the station's place on
  the path + 1, so 6 for the fifth (p. 60).
- One path at a time: a magus who steps onto another keeps only his
  Enigmatic Wisdom; rejoining, he regains its stations (p. 58). Only the
  Primus follows the Path of the Mirror (pp. 57, 59, 73), keeping his old
  paths' stations on it (p. 58); its own stations aren't printed. The app
  knows the Primus by his Hermetic background's Primus naming himself.
- Some stations also give catalogue Virtues beside the station's own:
  Differentiation of Seeming gives Clear Thinker, Common Sense and Keen
  Vision (another sense may replace Keen Vision, p. 64); Service to
  Harmony the Gentle Gift, or lifts the Blatant Gift to an ordinary Gift
  (p. 70); Expression gives Free Expression and Inspirational (p. 71).
- Every follower of a path ends Disfigured, with Vow or Pious (p. 60).

The stigmata (pp. 50-51, 60): a new mark for a station reached, a rise in
Enigmatic Wisdom, an Inner Mystery, an apprentice begun or finished, a
familiar sought or bound, a great work of the Art; the first usually with
the Riddle of the Magus, loops on the wrists after Twilight. No
mechanical cause, and no removing them, even by magic. Another Criamon
reads what one marks with Intelligence + Enigmatic Wisdom against 6.
Head binding in infancy (the cone suits the Path of Seeming, the
double-lobed skull the Path of the Body), or castration, broken bones or
severed joints, gives an aptitude for one path: +3 to the Script of that
path's first station only (p. 51).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from ..models import Character, Saga, VirtueFlawInstance
from ..models.criamon import GHOST_GUIDE, HOUSE_GUIDE
from .scores import ability_level

MC = "Houses of Hermes: Mystery Cults"
SOURCE = f"{MC}, House Criamon, The Paths, pp. 58-73; Errata p. 55"
PATHS_SOURCE = f"{MC} pp. 58-60"
STIGMATA_SOURCE = f"{MC}, Stigmata, pp. 50-51, 60"

#: The tradition catalog's entry holding the avenues' Scripts.
CULT_TRADITION = "trad_criamon_mysteries"
#: The House's Outer Mystery (DE p. 235), which makes a magus one of it.
THE_ENIGMA = "vf_the_enigma"
HOUSE = "house_criamon"
#: The cult's Lore, as the Ability catalog names it; the book's name and
#: a shorter one count too.
CULT_LORE = "Mystery Cult Lore: Criamon"
LORE_NAMES = (CULT_LORE, "House Criamon Lore", "Criamon Lore")
WISDOM = "Enigmatic Wisdom"
#: The Lore a ghostly Primus guides with (p. 60), and the guide's
#: Presence + Lore the printed Scripts assume: the House's guide's total.
GHOST_LORE = 9
ASSUMED_GUIDE = 6
#: A station's Target: a Major Virtue the guide knows (DE p. 387).
STATION_TARGET = 21
#: Head binding in infancy, or a like modification: +3 to the first
#: station of the one path it suits (p. 51).
HEAD_BINDING = 3
#: Reading what another's stigma marks: Int + Enigmatic Wisdom against 6
#: (p. 60).
READ_STIGMA_EASE = 6
NUMERALS = ("I", "II", "III", "IV", "V")

VOW, PIOUS = "vf_vow", "vf_pious_major"
DISFIGURED = "vf_disfigured"
BLATANT_GIFT = "vf_blatant_gift"
GENTLE_GIFT = "vf_gentle_gift"
SERVICE_TO_HARMONY = "vf_station_of_service_to_harmony"
HIGHER_PURPOSE = "vf_higher_purpose"


@dataclass(frozen=True)
class Station:
    """One station of a path and the avenue to it: its Virtue, what it
    gives, the Script (its components and bonus, as printed), the Target
    the book prints (with the Ordeal reductions it assumes), the Ordeal's
    size and the Flaws it brings: those gained (Virtue/Flaw catalog ids,
    with what they name), the Minor Flaw a Major one replaces, and those
    only described ("the equivalent of a Supernatural Nuisance"), which
    the troupe adds by hand. `grants` are the catalogue Virtues reaching
    the station gives beside its own. `printed_reduction` is the Target's
    reduction as the book prints it (its words and amount), where that is
    kept rather than worked out from the Ordeals' sizes. `story` is the
    avenue's, in a few words."""

    name: str
    avenue: str
    virtue_id: str
    gives: str
    components: tuple[tuple[str, int], ...]
    printed_target: int
    page: int
    story: str
    ordeal: str = ""
    gains: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = ()
    replaces: tuple[str, str] | None = None
    by_hand: str = ""
    grants: tuple[str, ...] = ()
    printed_reduction: tuple[str, int] | None = None

    @property
    def bonus(self) -> int:
        return sum(bonus for _, bonus in self.components)

    @property
    def flaw_ids(self) -> tuple[str, ...]:
        found = [vf for vf, _ in self.gains]
        if self.replaces is not None:
            found.append(self.replaces[1])
        return tuple(found)


@dataclass(frozen=True)
class Path:
    """A path: its name ("of Seeming"), its five stations in order, its
    page, and the place its stigmata first appear (its symbolism)."""

    key: str
    name: str
    stations: tuple[Station, ...]
    page: int
    stigmata: str = ""

    @property
    def title(self) -> str:
        return f"The Path {self.name}"


def _plain(*ids: str) -> tuple[tuple[str, tuple[tuple[str, str], ...]], ...]:
    return tuple((vf, ()) for vf in ids)


PLACE = ("Special time and place", 3)
MYSTAGOGUE = ("The guide's time", 3)

BODY = Path(
    "body",
    "of the Body",
    (
        Station(
            "the Perfect Tool",
            "The Avenue of Subduing the Meat",
            "vf_station_of_the_perfect_tool",
            "Minor Potency in an aspect of Corpus; Enigmatic Wisdom for "
            "Medicine and Chirurgy",
            (
                ("Major Ordeal: Vow, Deleterious Circumstances, Disfigured", 9),
                ("Sympathy: a year's cycle as a plant, or the like", 3),
                ("Special time and place: a symbolic rebirth", 3),
            ),
            21,
            61,
            "a year of mortifications or exertions, ended by a guide as "
            "midwife to a symbolic rebirth",
            "Major",
            (
                (VOW, ()),
                ("vf_deleterious_circumstances", (("circumstance", "while ill"),)),
                (DISFIGURED, ()),
            ),
        ),
        Station(
            "Spiritual Nourishment",
            "The Avenue of Drinking the Winds of Inspiration",
            "vf_station_of_spiritual_nourishment",
            "need not eat, drink or sleep in high auras; replaces a longevity ritual",
            (("Quest: psychodramatic visions, or securing a site", 3), PLACE),
            12,
            61,
            "fasting and labyrinth meditations in a Magic aura of 7 or more, "
            "from the first day of Virgo",
        ),
        Station(
            "Perfect Economy of Movement",
            "The Avenue of the Tiniest Seed",
            "vf_station_of_perfect_economy_of_movement",
            "once a day, a Dexterity roll of 21 or less succeeds",
            (("Ordeal: Pious (Major) replaces Vow", 6), MYSTAGOGUE),
            15,
            61,
            "a season's training in focus and movement from his guide",
            "Medium",
            replaces=(VOW, PIOUS),
        ),
        Station(
            "the Microcosm",
            "The Avenue of the Spherical Mirror",
            "vf_station_of_the_microcosm",
            "casts as if holding an Arcane Connection to places and things he recalls",
            (("Quest: psychodramatic", 3), MYSTAGOGUE, PLACE),
            15,
            61,
            "a season sealed in quartz or glass, in darkness",
        ),
        Station(
            "Corporeal Repose",
            "The Avenue of Repose in the Body",
            "vf_threshold_of_corporeal_repose",
            "purified of mortal frailties",
            (("Three Quests to legendary places", 9), PLACE),
            17,
            61,
            "the four humors, three of them found by Quests, consumed where "
            "body and universe meet",
        ),
    ),
    61,
    "first on the back, over the lungs",
)

SEEMING = Path(
    "seeming",
    "of Seeming",
    (
        Station(
            "Differentiation of Seeming",
            "The Avenue of Gruel, Water and Starlight",
            "vf_station_of_differentiation_of_seeming",
            "Clear Thinker, Common Sense, Keen Vision",
            (
                ("Minor Ordeal: Disfigured", 3),
                MYSTAGOGUE,
                ("Quest: psychodramatic, subduing the senses", 3),
                ("Special time and place: a cave, at the dark of the moon", 3),
                ("Sympathy: deprivation", 3),
            ),
            21,
            64,
            "labyrinth meditations on gruel and water, then investitures in "
            "a series of caves that tune his senses",
            "Minor",
            _plain(DISFIGURED),
            grants=("vf_clear_thinker", "vf_common_sense", "vf_keen_vision"),
        ),
        Station(
            "True Sight",
            "The Avenue that Assaults the Modesty of the Universe",
            "vf_station_of_true_sight",
            "Enigmatic Wisdom as Second Sight and Magic Sensitivity",
            (
                ("Ordeal: Vow", 3),
                ("Quest: insane wanderings", 3),
                PLACE,
                MYSTAGOGUE,
            ),
            18,
            64,
            "a season wandering in madness, defended by his companions and "
            "at last his guide",
            "Minor",
            _plain(VOW),
        ),
        Station(
            "Vivid Memories from Objects",
            "The Avenue of the Unexpected Pages",
            "vf_station_of_vivid_memories_from_objects",
            "reads the memories of objects",
            (
                ("Ordeal: Pious (Major) replaces Vow", 6),
                ("Special time and place (or the loss of his talisman)", 3),
                ("Quest: psychodramatic", 3),
            ),
            18,
            64,
            "he falls into the memories of the objects around him and must "
            "play them through to where he acquired the object, which "
            "becomes his talisman",
            "Medium",
            replaces=(VOW, PIOUS),
        ),
        Station(
            "Passing through Seeming",
            "The Avenue that is a Crossroad",
            "vf_station_of_passing_through_seeming",
            "spirit travelling",
            (MYSTAGOGUE, PLACE, ("Sympathy", 3), ("Quest", 3)),
            15,
            64,
            "his spirit drawn to the four Edges of the World, each to escape",
        ),
        Station(
            "From Which to Ignore the Real",
            "The Avenue that Leads to Transcendence",
            "vf_station_from_which_to_ignore_the_real",
            "may briefly ignore mundane objects",
            (("Major Ordeal: Twilight Prone", 9), MYSTAGOGUE),
            17,
            64,
            "investiture at the Axis Magica on New Year's Eve",
            "Major",
            _plain("vf_twilight_prone"),
        ),
    ),
    64,
    "first on the bridge of the nose",
)

STRIFE = Path(
    "strife",
    "of Strife",
    (
        Station(
            "the Eater of Sin",
            "The Avenue of Faith in Strife",
            "vf_station_of_the_eater_of_sin",
            "Enigmatic Wisdom as Magic Sensitivity and as a weapon's Ability",
            (
                ("Major Ordeal: the Blatant Gift", 9),
                PLACE,
                ("Sympathy: transgressions (meat, sex, profanities)", 3),
            ),
            21,
            67,
            "the Labyrinth of Strife, escaped only by violating the House's "
            "tenets, before the Keeper of the Path",
            "Major",
            _plain(BLATANT_GIFT),
        ),
        Station(
            "Blood and Bronze",
            "The Avenue that Splinters",
            "vf_station_of_blood_and_bronze",
            "destroys things by meditating round them; strikes at four times "
            "the Attack Total",
            (("Minor Ordeal: Higher Purpose (to eat sin for the House)", 3), PLACE),
            12,
            67,
            "investiture at a place saturated with strife, on the anniversary "
            "of its greatest slaughter",
            "Minor",
            _plain(HIGHER_PURPOSE),
        ),
        Station(
            "That Repels and Attracts Elements",
            "The Avenue of Charm and Scorn",
            "vf_station_that_repels_and_attracts_elements",
            "attracts or repels one element at a time",
            (("Quest: seek a lover", 3), PLACE, ("Sympathy: marriage", 3)),
            15,
            67,
            "a mystical marriage to a lover who is his perfect complement",
        ),
        Station(
            "That Charms the Elements",
            "The Avenue of Befriending the Silent",
            "vf_station_that_charms_the_elements",
            "speaks to elementally pure objects",
            (
                ("Ordeal: Pious (Major) replaces Higher Purpose", 6),
                ("Ordeal: the equivalent of a Supernatural Nuisance", 3),
                ("Ordeal: Disfigured", 3),
                MYSTAGOGUE,
            ),
            18,
            67,
            "the symbolic language of elemental spirits, taught by the guide",
            "Medium",
            _plain(DISFIGURED),
            (HIGHER_PURPOSE, PIOUS),
            "a minor Supernatural Nuisance",
        ),
        Station(
            "Golden Cider",
            "The Avenue of Death",
            "vf_station_of_golden_cider",
            "makes some mystical things mundane",
            (("Ordeal: four pairs of Incompatible Arts", 12),),
            15,
            67,
            "a private ritual under the path's most senior magus: Creo is "
            "lost but with Corpus and Vim",
            "Medium",
            by_hand="Incompatible Arts four times: Creo with each Form but "
            "Corpus and Vim",
        ),
    ),
    67,
    "first on the hands",
)

WALKING = Path(
    "walking_backwards",
    "of Walking Backwards",
    (
        Station(
            "Service to Harmony",
            "The Avenue of Surrender",
            "vf_station_of_service_to_harmony",
            "the Gentle Gift, or the Blatant Gift lifted to an ordinary Gift",
            (("Major Ordeal: Pious", 9), PLACE, MYSTAGOGUE),
            21,
            71,
            "his destructive past forsworn, a pilgrimage and rites of "
            "purification, then a season's training",
            "Major",
            _plain(PIOUS),
        ),
        Station(
            "Rice and Honey",
            "The Avenue of Healing",
            "vf_station_of_rice_and_honey",
            "dances damaged things to wholeness",
            (
                ("Ordeal: Noncombatant", 3),
                ("Ordeal: the equivalent of a Vow to help the injured", 3),
            ),
            12,
            71,
            "he becomes a healer who cannot choose to harm",
            "Minor",
            _plain("vf_noncombatant", VOW),
        ),
        Station(
            "Expression",
            "The Avenue of Adulation",
            "vf_station_of_expression",
            "Free Expression, Inspirational, Enigmatic Wisdom for an art",
            (MYSTAGOGUE, ("Quest: a place of unspeakable beauty", 3), PLACE),
            15,
            71,
            "a place of unimaginable profoundness, then the guide coaxes him "
            "into expressing it",
            grants=("vf_free_expression", "vf_inspirational"),
        ),
        Station(
            "Exaltation",
            "The Avenue of a Thousand Beautiful Faces",
            "vf_station_of_exaltation",
            "draws a single positive property out of an object",
            (("Ordeal: four pairs of Incompatible Arts", 12),),
            18,
            71,
            "he gives up Perdo but with Vim and Imaginem",
            "Medium",
            by_hand="Incompatible Arts four times: Perdo with each Form but "
            "Vim and Imaginem",
        ),
        Station(
            "Immortal Ascension",
            "The Avenue of Silencing Discordant Whispers",
            "vf_immortal_ascension_as_repose",
            "chooses his age and sex; the threshold of repose",
            (MYSTAGOGUE, ("Quests: the psychic residue", 3), PLACE),
            15,
            71,
            "spiritual obstacles: temptations of power, comfort, the senses "
            "and eternal life",
            # The reduction as printed (p. 71), not worked out from the
            # fourth station's Ordeal size.
            printed_reduction=("second Initiation since a Major Ordeal", 6),
        ),
    ),
    70,
    "first on the soles of the feet",
)

#: The Path of the Mirror, for the Primi only: they keep their stations on
#: their old paths, and its own aren't printed (pp. 58-59).
MIRROR = Path("mirror", "of the Mirror", (), 58, "")

PATHS: dict[str, Path] = {p.key: p for p in (BODY, SEEMING, STRIFE, WALKING, MIRROR)}
#: Every station's Virtue -> (its path, its place on the path, 1 to 5).
STATION_OF: dict[str, tuple[Path, int]] = {
    station.virtue_id: (path, n)
    for path in PATHS.values()
    for n, station in enumerate(path.stations, start=1)
}


# -- who and what --------------------------------------------------------------


def is_criamon(magus: Character | None) -> bool:
    """Whether `magus` is of House Criamon: its magus, or one Initiated
    into the Enigma."""
    if magus is None:
        return False
    return (magus.hermetic.house or "") == HOUSE or any(
        vf.vf_id == THE_ENIGMA for vf in magus.virtues_flaws
    )


def is_primus(magus: Character) -> bool:
    """Whether `magus` is the Primus of House Criamon: a Criamon magus whose
    Hermetic background names himself as the House's Primus."""
    named = magus.hermetic.primus.strip().casefold()
    return is_criamon(magus) and bool(named) and named == magus.name.strip().casefold()


def paths_open_to(magus: Character) -> list[Path]:
    """The paths Change Path offers him: the four printed ones, and the Path
    of the Mirror only for the Primus, who alone follows it (pp. 57, 59,
    73), or for one already set on it."""
    return [
        p
        for p in PATHS.values()
        if p is not MIRROR or is_primus(magus) or magus.enigma.path == MIRROR.key
    ]


def has_enigma_tab(character: Character) -> bool:
    """Whether the sheet has The Enigma: a magus of House Criamon."""
    return character.type == "magus" and is_criamon(character)


def cult_lore(character: Character) -> int:
    """His House Criamon Lore, by the best of its names."""
    return max(ability_level(character, name) for name in LORE_NAMES)


def wisdom(character: Character) -> int:
    return ability_level(character, WISDOM)


def held(character: Character) -> set[str]:
    return {vf.vf_id for vf in character.virtues_flaws}


def stations_held(character: Character, path: Path) -> list[int]:
    """The places (1 to 5) of the path's stations he holds."""
    have = held(character)
    return [
        n
        for n, station in enumerate(path.stations, start=1)
        if station.virtue_id in have
    ]


def path_of(character: Character) -> Path | None:
    """The path he walks: the one his Enigma names, else the one most of
    his stations are on (None: the Winding Path, no path yet)."""
    named = PATHS.get(character.enigma.path)
    if named is not None:
        return named
    counts = [
        (len(stations_held(character, p)), p) for p in PATHS.values() if p.stations
    ]
    best = max(counts, key=lambda pair: pair[0], default=(0, None))
    return best[1] if best[0] else None


def station_reached(character: Character, path: Path) -> int:
    """How far along the path he is: the stations he holds in order from
    the first (a gap stops the count)."""
    have = set(stations_held(character, path))
    count = 0
    while count + 1 in have:
        count += 1
    return count


def next_station(character: Character, path: Path | None) -> tuple[int, Station] | None:
    """The station his next avenue reaches, with its place (None: no path,
    or the path's end)."""
    if path is None:
        return None
    n = station_reached(character, path) + 1
    if n > len(path.stations):
        return None
    return n, path.stations[n - 1]


def lore_needed(place: int) -> int:
    """House Criamon Lore a station needs: its place on the path + 1 (p. 60)."""
    return place + 1


def set_aside(character: Character, path: Path | None) -> list[tuple[Path, Station]]:
    """The stations he holds on other paths, of no use while he walks this
    one (p. 58); only the Primus, on the Path of the Mirror, keeps them."""
    if path is not None and path.key == MIRROR.key and is_primus(character):
        return []
    return [
        (other, other.stations[n - 1])
        for other in PATHS.values()
        if other is not path
        for n in stations_held(character, other)
    ]


def path_flaws(character: Character) -> list[str]:
    """The Flaws the paths bring that he has (Virtue/Flaw catalog ids), in
    the order his sheet lists them."""
    of_paths = {
        vf
        for path in PATHS.values()
        for station in path.stations
        for vf in station.flaw_ids
    }
    found: list[str] = []
    for vf in character.virtues_flaws:
        if vf.vf_id in of_paths and vf.vf_id not in found:
            found.append(vf.vf_id)
    return found


def when_reached(character: Character, vf_id: str) -> str:
    """The season he reached the station, or "" when it isn't kept."""
    found = next((r for r in character.enigma.reached if r.vf_id == vf_id), None)
    if found is None:
        return ""
    return " ".join(str(part) for part in (found.season, found.year) if part)


# -- the guide ------------------------------------------------------------------


@dataclass(frozen=True)
class Guide:
    """A guide's name, Presence and House Criamon Lore; `house`: the guide
    the House provides, known only by his total; `outsider`: one not of
    House Criamon, which is unusual (p. 59)."""

    name: str
    presence: int
    lore: int
    ghost: bool = False
    house: bool = False
    outsider: bool = False

    @property
    def total(self) -> int:
        return self.presence + self.lore


def ghost_guide(presence: int) -> Guide:
    return Guide(
        "A ghostly Primus at the Cave of Twisting Shadows", presence, GHOST_LORE, True
    )


def house_guide() -> Guide:
    """The guide the House provides: Presence + House Criamon Lore 6, the
    total the printed Scripts assume (p. 60)."""
    return Guide("A guide the House provides", 0, ASSUMED_GUIDE, house=True)


def guide_of(saga: Saga, magus: Character, guide_id: str) -> Guide | None:
    """The guide `guide_id` names: the House's ("" or HOUSE_GUIDE), a
    ghostly Primus, a character of the saga, or None for one who is gone."""
    if not guide_id or guide_id == HOUSE_GUIDE:
        return house_guide()
    if guide_id == GHOST_GUIDE:
        return ghost_guide(magus.enigma.primus_presence)
    found = saga.character(guide_id)
    if found is None or found is magus:
        return None
    return Guide(
        found.name,
        found.characteristics.presence,
        cult_lore(found),
        outsider=not is_criamon(found),
    )


def guides(saga: Saga, magus: Character) -> list[Character]:
    """The saga's characters who could guide him: any but himself who knows
    House Criamon Lore, the Lore the Initiation uses (DE p. 387; p. 59).
    One not of the House is unusual (outsider_warning), not refused."""
    return [c for c in saga.characters if c is not magus and cult_lore(c) >= 1]


def outsider_warning(name: str) -> str:
    """The warning for a guide not of House Criamon."""
    return (
        f"{name} isn't of House Criamon: a guide from outside the House is "
        f"unusual, though he knows its Lore ({MC} p. 59)."
    )


# -- the avenue ------------------------------------------------------------------


@dataclass(frozen=True)
class Avenue:
    """The next avenue worked out: the station, the guide, the Script
    (with his aptitude for the path), the Target (21 less the Ordeal
    reduction), what stands in the way and what is unusual."""

    place: int
    station: Station
    guide: Guide | None
    script: int
    target: int
    problems: tuple[str, ...]
    warnings: tuple[str, ...] = ()

    @property
    def total(self) -> int:
        return (self.guide.total if self.guide is not None else 0) + self.script

    @property
    def enough(self) -> bool:
        return self.guide is not None and self.total >= self.target


def target(reduction: int) -> int:
    """A station's Target: 21, less a past Ordeal's reduction, never below 9
    (DE p. 388)."""
    return max(9, STATION_TARGET - reduction)


def aptitude_bonus(character: Character, path: Path, place: int) -> int:
    """+3 for the first station of the one path his head binding (or a like
    modification) suits, else 0 (p. 51)."""
    suited = character.enigma.aptitude_path == path.key
    return HEAD_BINDING if place == 1 and suited else 0


def script_extra(character: Character, key: str) -> int:
    """What the Initiation season adds to an avenue's printed Script: his
    aptitude for its path's first station (p. 51); 0 for any other Script."""
    found = station_of_script(key)
    return aptitude_bonus(character, *found) if found is not None else 0


def avenue(
    character: Character,
    path: Path,
    place: int,
    guide: Guide | None,
    reduction: int,
) -> Avenue:
    """Following the avenue to `path`'s station at `place` with `guide`;
    `reduction` is his past Ordeals' (the Initiation season's)."""
    station = path.stations[place - 1]
    script = station.bonus + aptitude_bonus(character, path, place)
    problems: list[str] = []
    needs = lore_needed(place)
    if cult_lore(character) < needs:
        problems.append(
            f"But his House Criamon Lore is {cult_lore(character)}: the "
            f"{ordinal(place)} station needs {needs}."
        )
    if guide is None:
        problems.append("Choose his guide: the one named is no longer in the saga.")
    warnings = (outsider_warning(guide.name),) if guide and guide.outsider else ()
    return Avenue(
        place, station, guide, script, target(reduction), tuple(problems), warnings
    )


def script_name(path: Path, place: int) -> str:
    """The catalog Script of the path's station at `place`."""
    station = path.stations[place - 1]
    return f"The Path {path.name}, {NUMERALS[place - 1]}: {station.avenue}"


def script_key(path: Path, place: int) -> str:
    """How a season plan names the station's Script (SeasonPlan.hedge_script)."""
    return f"{CULT_TRADITION}/{script_name(path, place)}"


def station_of_script(key: str) -> tuple[Path, int] | None:
    """The path and place a plan's Script reaches, if it is an avenue."""
    tradition, _, name = key.partition("/")
    if tradition != CULT_TRADITION:
        return None
    for path in PATHS.values():
        for place in range(1, len(path.stations) + 1):
            if script_name(path, place) == name:
                return path, place
    return None


# -- the Initiation season's hooks ---------------------------------------------------


def lore_is_enough(tradition_id: str) -> bool:
    """Whether a guide of `tradition_id`'s Initiations need only know its
    Lore, not belong to it: House Criamon's (DE p. 387; p. 59)."""
    return tradition_id == CULT_TRADITION


def knows_by_rule(key: str) -> bool:
    """The House's Scripts are followed at the Targets the book prints, as
    a Major Virtue the guide knows (p. 60)."""
    return key.startswith(f"{CULT_TRADITION}/")


def stand_in(initiate: Character, mystagogue: Character, key: str) -> Guide | None:
    """The guide of an avenue planned with no Mystagogue (p. 60): a ghostly
    Primus when his Enigma names one, else the guide the House provides
    (Presence + Lore 6); None for any other Script or a named Mystagogue."""
    if mystagogue is not initiate or station_of_script(key) is None:
        return None
    if initiate.enigma.guide_id == GHOST_GUIDE:
        return ghost_guide(initiate.enigma.primus_presence)
    return house_guide()


def avenue_problem(initiate: Character, vf_id: str, key: str) -> str:
    """What stops following an avenue ("" if nothing, or for any other
    Script): a magus of the House, the stations before it on the path,
    not one he holds already, and the Virtue the plan names its own."""
    found = station_of_script(key)
    if found is None:
        return ""
    path, place = found
    station = path.stations[place - 1]
    if not is_criamon(initiate):
        return (
            f"{initiate.name} isn't of House Criamon: the paths are its "
            f"Mystery ({PATHS_SOURCE})."
        )
    if station.virtue_id in held(initiate):
        return f"{initiate.name} has reached the Station of {station.name} already."
    if station_reached(initiate, path) < place - 1:
        return (
            f"The avenues are followed in order: {initiate.name} hasn't reached "
            f"the station before {station.name} on {path.title} ({PATHS_SOURCE})."
        )
    if vf_id and vf_id != station.virtue_id:
        return (
            f"This avenue reaches the Station of {station.name}: choose its Virtue "
            "as the one Initiated."
        )
    return ""


@dataclass
class Outcome:
    """What following an avenue does besides the station's Virtue: the
    Flaws its Ordeal adds and takes away (whenever the Ordeal is suffered),
    the catalogue Virtues the station grants and the Flaw it lifts (only
    when he is initiated), the Ordeal's size, the station reached and
    notes."""

    add: list[VirtueFlawInstance]
    remove: list[VirtueFlawInstance]
    ordeal: str
    station: str
    notes: list[str]
    granted: list[VirtueFlawInstance] = field(default_factory=list)
    lifted: list[VirtueFlawInstance] = field(default_factory=list)


def station_gifts(
    initiate: Character, station: Station
) -> tuple[list[VirtueFlawInstance], list[VirtueFlawInstance], list[str]]:
    """The catalogue Virtues reaching `station` gives that he lacks, the
    Flaw it lifts, and notes: Clear Thinker, Common Sense and Keen Vision
    (p. 64); the Gentle Gift, or the Blatant Gift lifted to an ordinary
    Gift (p. 70); Free Expression and Inspirational (p. 71)."""
    have = held(initiate)
    granted = [VirtueFlawInstance(vf) for vf in station.grants if vf not in have]
    lifted: list[VirtueFlawInstance] = []
    notes: list[str] = []
    if "vf_keen_vision" in station.grants:
        notes.append(
            "Keen Vision may be traded for the like in another sense: change "
            f"it by hand ({MC} p. 64)."
        )
    if station.virtue_id == SERVICE_TO_HARMONY:
        if BLATANT_GIFT in have:
            lifted = [vf for vf in initiate.virtues_flaws if vf.vf_id == BLATANT_GIFT]
            notes.append(
                "The Blatant Gift is lifted to an ordinary Gift, whose "
                f"penalties remain ({MC} p. 70)."
            )
        elif GENTLE_GIFT not in have:
            granted.append(VirtueFlawInstance(GENTLE_GIFT))
    return granted, lifted, notes


def outcome(initiate: Character, key: str, *, own_ordeal: bool) -> Outcome | None:
    """Reaching the station `key`'s avenue leads to (None for any other
    Script). The Ordeal's Flaws are added unless the plan names an Ordeal
    of its own (`own_ordeal`): a Major Flaw replaces its Minor one; a
    Flaw the book only describes is noted for the troupe."""
    found = station_of_script(key)
    if found is None:
        return None
    path, place = found
    station = path.stations[place - 1]
    have = held(initiate)
    add: list[VirtueFlawInstance] = []
    remove: list[VirtueFlawInstance] = []
    granted, lifted, notes = station_gifts(initiate, station)
    if not own_ordeal:
        for vf, params in station.gains:
            if vf not in have:
                add.append(VirtueFlawInstance(vf, dict(params)))
        if station.replaces is not None:
            old, new = station.replaces
            remove += [vf for vf in initiate.virtues_flaws if vf.vf_id == old]
            if new not in have:
                add.append(VirtueFlawInstance(new))
    if station.by_hand:
        notes.append(f"Add the rest of the Ordeal by hand: {station.by_hand}.")
    notes.append(
        f"{initiate.name} reaches the Station of {station.name}, {place} of "
        f"{len(path.stations)} on {path.title}: a new stigma usually appears "
        f"(add it on The Enigma; {STIGMATA_SOURCE})."
    )
    return Outcome(
        add,
        remove,
        "" if own_ordeal else station.ordeal,
        station.virtue_id,
        notes,
        granted,
        lifted,
    )


def initiation_notes(initiate: Character, key: str) -> list[str]:
    """What the season notes before the Total: the avenue's story, and
    stepping onto another path."""
    found = station_of_script(key)
    if found is None:
        return []
    path, place = found
    station = path.stations[place - 1]
    notes = [
        f"{station.avenue}: {station.story} ({MC} p. {station.page}). A magus "
        "who fails may try again; utter failure in a psychodrama may force a "
        f"Twilight check ({MC} p. 59)."
    ]
    current = path_of(initiate)
    if current is not None and current is not path:
        notes.append(
            f"He steps from {current.title} onto {path.title}: he keeps only his "
            f"Enigmatic Wisdom of the old path's stations ({MC} p. 58)."
        )
    return notes


def ordinal(n: int) -> str:
    return {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth"}.get(
        n, f"{n}th"
    )


def reduction_words(sizes: Iterable[tuple[str, int, int]]) -> str:
    """The best past Ordeal's reduction, as the book words it ("his first
    Initiation since a Minor Ordeal"), from (size, initiations since,
    reduction); "" when none applies."""
    best = max(sizes, key=lambda found: found[2], default=None)
    if best is None or not best[2]:
        return ""
    size, since, _ = best
    return f"his {ordinal(since + 1)} Initiation since a {size} Ordeal"
