"""The noble hunt, hawking, and Area Lore's use in finding things: plain
rule functions, without a front-end. forms/hunting.py words them.

SOURCE: Lords of Men, The Hunt (pp. 48-49), Hounds and the hunting dogs'
statistics (pp. 49-51), Hunting with Hounds (pp. 51-53, with the Terrain
Bonus insert, p. 53), The Prey (p. 54), Hawking and Some Typical Prey
Animals (pp. 57-58), Hawks and Falcons (p. 59) and The Kennels (p. 60);
City & Guild, Area Lore: The Hinterland as a Resource and the Area Lore
Ease Factors (pp. 82-83); the Definitive Edition's (Area) Lore (p. 159),
Hunt (p. 166), the dice (pp. 7-8) and the Gift's social penalty
(p. 204). The Errata (Ars Magica 5th Edition) corrects none of these
pages (its Lords of Men entries, p. 74, change the gyrfalcon's
Communication on p. 59, which no roll here uses, and the Stables table;
its City & Guild entries, pp. 56-57, touch neither p. 82 nor p. 83).

- **The quest** (p. 52): each huntsman rolls Perception + the lower of
  his own and his lymer's Hunt against 9 to track a fit beast to its
  lair, Presence + Animal Handling against 9 to keep the lymer quiet,
  and Intelligence + Hunt against 9 to judge its age and condition. At
  **the assembly** the guests read the droppings: Perception + Hunt
  against 12. The book calls none of these stress, so all are simple.
- **The chase** (p. 52): a round is an hour. Each hunter rolls Dexterity
  + Ride (stress) against 6 to keep the hounds in sight; the hounds and
  the prey each lose a Fatigue level a round unless a simple Stamina +
  Athletics roll makes 12; every three rounds a hunter makes a simple
  Stamina + Ride roll against 9 or loses a Long-Term Fatigue level. The
  hounds' Pursuit Total (the best dog's Perception + Hunt + stress die -
  the pack's Fatigue penalty) meets the prey's Evasion Total (Dexterity
  + Athletics + Terrain Bonus + stress die - its Fatigue penalty): the
  higher wins the round, a tie neither. Four rounds won, not necessarily
  in a row, corner the prey; four lost, or darkness, and it escapes.
- **The Terrain Bonus** (p. 53) starts at +6 for a beast native to the
  ground. Each round, each huntsman who laid the relay rolls Intelligence
  + Hunt + 6 (stress) against the Evasion Total: a success brings fresh
  dogs (the pack's Fatigue penalty is 0 next round), and that huntsman
  may roll Intelligence + Area Lore (stress) against it to take 1 off the
  bonus
  for the rest of the hunt (the relay at most 1 a round). Each hunter
  still with the pack rolls Perception + Area Lore (stress) against it:
  any success takes 1 more off.
- **The prey** (p. 54) and its seasons: the hart in spring and summer,
  the boar from midsummer through autumn, the bear in any season but
  spring, the hare in spring and summer, the otter in summer and autumn;
  the wolf and fox at any time.
- **Hawking** (p. 58): Presence + Animal Handling (the Gift's penalty
  applies) read on the book's table, from a Loyalty check and a lost bird
  at 0 or less to a +5 attack that goes on launching further attacks
  after the first at 21+ (the book sets no limit). The prey's
  figures are p. 58's table, the birds' p. 59.
- **The kennels** (p. 60): a hunt needs a dozen running dogs and a lymer
  at least.
- **Area Lore** (C&G pp. 82-83): Intelligence + Area Lore against the
  table's Ease Factors finds people, places and things in a city or its
  hinterland; one who lives in the city subtracts 3 seeking in the
  hinterland, and one who lives in the hinterland 3 seeking in the city.
  A hunting or fishing spot is Ease Factor 6.

The app's readings, where the books leave a gap (forms/hunting.py and
the notes say each with its page):
- a roll the book calls neither stress nor simple is a simple roll, since
  the book names a stress die wherever it wants one: the quest, the
  assembly, the hawker's Presence + Animal Handling, a lost hawk's
  Loyalty check against 6 (as p. 51's training test) and Area Lore's
  knowledge (C&G p. 83). The hawk's attack and the prey's defense are
  combat rolls, on stress dice;
- the hound's own "+2 to all Hunt rolls" (p. 50) adds to its Pursuit
  Total; a running dog's or greyhound's "+3 to all running rolls" to its
  Stamina + Athletics roll against tiring;
- a huntsman whose lymer is not quiet loses the beast he found;
- the chase ends on four rounds won by either side or on nightfall, as
  the book has it; a prey or pack spent beyond its last Fatigue level,
  which the book leaves open (it counts Fatigue only as a penalty to
  each total), is the app's gap-fill: the prey cornered, or the pack
  giving up;
- a hunter who falls behind stops rolling and tiring;
- a botched Dexterity + Ride roll throws the hunter, the harm left to the
  troupe;
- the hours of daylight bound the chase (the book gives no figure);
- a hawk's single attack is its Attack + the table's bonus + a stress die
  against the prey's Defense + a stress die, the damage its Damage + the
  advantage less the prey's Soak, and an Incapacitating or Dead wound a
  kill; at 21+ the book has it go on attacking after the first strike,
  with no limit, and the app stops it on a kill or, by its own limit
  (not the book's), after five strikes.
"""

from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass, field

from ..models import Character, Creature, Saga
from . import combat, derived, dice, scores
from .study import gift_social_penalty

SOURCE = (
    "Lords of Men, The Hunt, Hounds, Hunting with Hounds, The Terrain Bonus, The "
    "Prey, Hawking, Hawks and Falcons and The Kennels, pp. 48-60; City & Guild, Area "
    "Lore: The Hinterland as a Resource and Area Lore Ease Factors, pp. 82-83; "
    "Definitive Edition, (Area) Lore p. 159, Hunt p. 166"
)
LOM = "LoM"
CG = "C&G"

HUNT = "Hunt"
RIDE = "Ride"
ATHLETICS = "Athletics"
ANIMAL_HANDLING = "Animal Handling"
AREA_LORE = "Area Lore"

# -- the quest and the assembly (p. 52) --

TRACK_EASE = 9
QUIET_EASE = 9
JUDGE_EASE = 9
ASSEMBLY_EASE = 12

# -- the chase (pp. 52-53) --

RIDE_EASE = 6
TIRING_EASE = 12
RIDE_STAMINA_EASE = 9
#: Every so many rounds a hunter rolls Stamina + Ride.
RIDE_STAMINA_EVERY = 3
TERRAIN_BONUS = 6
RELAY_BONUS = 6
ROUNDS_TO_WIN = 4
#: Said where a chase ends on spent Fatigue, which the book leaves open.
GAP_FILL = (
    "the app's reading: the book ends a chase only on four rounds won or nightfall"
)
#: The app's reading: the hours of daylight a chase has, by season.
DAYLIGHT = {"Spring": 12, "Summer": 15, "Autumn": 11, "Winter": 8}

# -- hawking (p. 58) and the Loyalty check (p. 51) --

LOYALTY_EASE = 6
#: The most strikes a hawk makes at 21+: the app's own limit, as the book
#: sets none (p. 58).
MOST_STRIKES = 5

#: A person's Fatigue penalties, after Fresh (DE p. 403).
PERSON_FATIGUE = (0, -1, -3, -5)


def fatigue_penalties(levels: str) -> tuple[int, ...]:
    """A creature's Fatigue levels as the book prints them ("OK, 0/0,
    -1/-1, -3, -5, Unconscious") as the penalty of each level after OK;
    a person's for none."""
    found: list[int] = []
    for part in levels.replace(";", ",").split(","):
        word = part.strip()
        if not word or word.casefold() in ("ok", "fresh"):
            continue
        if word.casefold().startswith("unc"):
            break
        for piece in word.split("/"):
            piece = piece.strip().replace("–", "-").replace("−", "-")
            try:
                found.append(int(piece))
            except ValueError as error:
                raise ValueError(f"A Fatigue level {piece!r} in {levels!r}.") from error
    return tuple(found) or PERSON_FATIGUE


def penalty(levels: Sequence[int], lost: int) -> int:
    """The Fatigue penalty after losing `lost` levels (0 when fresh)."""
    if lost <= 0:
        return 0
    return levels[min(lost, len(levels)) - 1]


def spent(levels: Sequence[int], lost: int) -> bool:
    """Whether `lost` levels go past the last: unconscious, or spent."""
    return lost > len(levels)


# -- the hounds (pp. 49-51) --


@dataclass(frozen=True)
class Hound:
    """A hunting dog's figures for the chase (p. 50): its Perception and
    Hunt, its quality's bonus to Hunt rolls, its Stamina and Athletics, a
    bonus to running rolls, and its Fatigue penalties."""

    key: str
    name: str
    perception: int
    hunt: int
    hunt_bonus: int
    stamina: int
    athletics: int
    running_bonus: int
    fatigue: tuple[int, ...]
    role: str

    @property
    def pursuit(self) -> int:
        """Its Pursuit Total before the die and Fatigue."""
        return self.perception + self.hunt + self.hunt_bonus

    @property
    def tiring(self) -> int:
        """Its Stamina + Athletics roll against tiring, before the die."""
        return self.stamina + self.athletics + self.running_bonus


HOUNDS: dict[str, Hound] = {
    h.key: h
    for h in (
        Hound(
            "running_dog",
            "Running dog",
            3,
            4,
            2,
            1,
            3,
            3,
            (0, -1, -1, -1, -3, -3, -5),
            "the pack, hunting in couples by scent",
        ),
        Hound(
            "lymer",
            "Lymer",
            3,
            4,
            2,
            1,
            3,
            0,
            (0, -1, -1, -3, -5),
            "tracks the quarry silently in the quest",
        ),
        Hound(
            "greyhound",
            "Greyhound",
            1,
            4,
            0,
            0,
            3,
            3,
            (0, -1, -1, -3, -5),
            "brings the prey down; must be slipped within sight of it",
        ),
        Hound(
            "alaunt",
            "Alaunt",
            1,
            4,
            2,
            1,
            3,
            0,
            (0, -1, -1, -3, -5),
            "held on the leash for the kill",
        ),
        Hound(
            "mastiff",
            "Mastiff",
            1,
            0,
            2,
            2,
            3,
            0,
            (0, -1, -3, -5),
            "for boar and bear, slower than a greyhound",
        ),
    )
}
RUNNING_DOG = "running_dog"
#: A lymer's Hunt, for the quest (p. 50).
LYMER_HUNT = HOUNDS["lymer"].hunt
#: The least a huntsman hunts with (p. 60).
LEAST_PACK = "a dozen good running dogs and a lymer"


# -- the quarry (p. 54) --


@dataclass(frozen=True)
class Quarry:
    """A beast to hunt: its figures for the Evasion Total and for tiring,
    the seasons it is hunted in (empty: any), and where its figures and
    words come from."""

    key: str
    name: str
    dexterity: int
    athletics: int
    stamina: int
    fatigue: tuple[int, ...]
    size: int = 0
    seasons: tuple[str, ...] = ()
    source: str = ""
    words: str = ""
    dangerous: bool = False

    @property
    def evasion(self) -> int:
        """Its Evasion Total before the Terrain Bonus, the die and Fatigue."""
        return self.dexterity + self.athletics

    @property
    def tiring(self) -> int:
        return self.stamina + self.athletics

    def in_season(self, season: str) -> bool:
        return not self.seasons or season in self.seasons


#: The quarry p. 54 names, by the Definitive Edition's stat blocks (and
#: p. 58's hare): the bestiary key, its seasons, and what the book says.
BOOK_QUARRY: tuple[tuple[str, tuple[str, ...], str, bool], ...] = (
    (
        "stag",
        ("Spring", "Summer"),
        "the hart, the object of most hunts; dangerous when it turns at bay",
        False,
    ),
    (
        "wild_boar",
        ("Summer", "Autumn"),
        "from midsummer through the autumn; dangerous, and good eating",
        True,
    ),
    (
        "bear",
        ("Summer", "Autumn", "Winter"),
        "never in spring; bear hunts may last days, and all the hunters close "
        "in together for the kill",
        True,
    ),
    (
        "wolf",
        (),
        "little honour but a good chase, and a necessity; it must be parted "
        "from its pack",
        False,
    ),
)
#: The hare, from p. 58's table: Size -6, Stamina +1, Dexterity +3.
HARE = Quarry(
    "lom:hare",
    "Hare",
    3,
    0,
    1,
    PERSON_FATIGUE,
    size=-6,
    seasons=("Spring", "Summer"),
    source=f"{LOM} pp. 54, 58",
    words="a fine runner, best chased by sighthounds; found in the peasants' "
    "fields, whose crops the chase tramples",
)


def creature_quarry(
    creature: Creature,
    key: str,
    *,
    seasons: tuple[str, ...] = (),
    source: str = "",
    words: str = "",
    dangerous: bool = False,
) -> Quarry:
    """A creature of the Bestiary as quarry, from its stat block."""
    chars = creature.characteristics
    athletics = next((a.level for a in creature.abilities if a.name == ATHLETICS), 0)
    return Quarry(
        key,
        creature.name,
        chars.dexterity,
        athletics,
        chars.stamina,
        fatigue_penalties(creature.fatigue_levels),
        size=creature.size,
        seasons=seasons,
        source=source or creature.source,
        words=words,
        dangerous=dangerous,
    )


# -- the hunters --


def area_lores(character: Character) -> list[tuple[str, int]]:
    """The character's Area Lores, (name, score), best first: the
    abilities named "Area Lore: ..." (the ability catalog's family)."""
    found = [
        (a.name, a.level)
        for a in character.abilities
        if a.name.casefold().startswith(AREA_LORE.casefold())
    ]
    return sorted(found, key=lambda pair: -pair[1])


def area_lore(character: Character, name: str | None = None) -> int:
    """His score in the Area Lore named, or with none named his best."""
    if name:
        return scores.ability_level(character, name)
    found = area_lores(character)
    return found[0][1] if found else 0


@dataclass(frozen=True)
class Hunter:
    """One who rides with the hunt: the figures the chase rolls with."""

    name: str
    dexterity: int = 0
    ride: int = 0
    stamina: int = 0
    perception: int = 0
    hunt: int = 0
    area_lore: int = 0


@dataclass(frozen=True)
class Huntsman:
    """One who quests with a lymer and lays the relay."""

    name: str
    perception: int = 0
    presence: int = 0
    intelligence: int = 0
    hunt: int = 0
    animal_handling: int = 0
    area_lore: int = 0


def hunter_of(character: Character, area: str | None = None) -> Hunter:
    c = character.characteristics
    return Hunter(
        character.name,
        c.dexterity,
        scores.ability_level(character, RIDE),
        c.stamina,
        c.perception,
        scores.ability_level(character, HUNT),
        area_lore(character, area),
    )


def huntsman_of(character: Character, area: str | None = None) -> Huntsman:
    c = character.characteristics
    return Huntsman(
        character.name,
        c.perception,
        c.presence,
        c.intelligence,
        scores.ability_level(character, HUNT),
        scores.ability_level(character, ANIMAL_HANDLING),
        area_lore(character, area),
    )


def _roll(
    rng: random.Random,
    modifiers: int,
    ease: int | None,
    saga: Saga | None,
    *,
    stress: bool,
) -> dice.Roll:
    """A roll on a stress die only where the book names one; every
    unlabelled roll is simple."""
    return dice.roll(rng, modifiers, ease_factor=ease, stress=stress, saga=saga)


def said(roll: dice.Roll) -> str:
    """A roll in words: "12 against 9", "a botch against 9"."""
    shown = "a botch" if roll.die.botched else str(roll.total)
    return f"{shown} against {roll.ease_factor}"


# -- the quest and the assembly --


@dataclass
class Quest:
    """The quest's outcome: whether a fit beast was found and its worth
    judged, what the guests learned at the assembly, and the lines."""

    found: bool = False
    judged: bool = False
    read: bool = False
    lines: list[str] = field(default_factory=list)


def quest(
    huntsmen: Sequence[Huntsman],
    guests: Sequence[Hunter],
    rng: random.Random,
    saga: Saga | None = None,
    lymer_hunt: int = LYMER_HUNT,
) -> Quest:
    """Each huntsman tracks with his lymer, keeps it quiet and judges the
    beast (p. 52); at the assembly the guests read the droppings."""
    done = Quest()
    for man in huntsmen:
        track = _roll(
            rng,
            man.perception + min(man.hunt, lymer_hunt),
            TRACK_EASE,
            saga,
            stress=False,
        )
        if not track.succeeded:
            done.lines.append(f"{man.name} finds no fit beast ({said(track)}).")
            continue
        quiet = _roll(
            rng, man.presence + man.animal_handling, QUIET_EASE, saga, stress=False
        )
        if not quiet.succeeded:
            done.lines.append(
                f"{man.name} tracks a beast to its lair ({said(track)}), but his "
                f"lymer gives tongue and it is startled away ({said(quiet)})."
            )
            continue
        judge = _roll(rng, man.intelligence + man.hunt, JUDGE_EASE, saga, stress=False)
        done.found = True
        done.judged = done.judged or bool(judge.succeeded)
        done.lines.append(
            f"{man.name} tracks a beast to its lair and keeps his lymer quiet"
            + (
                f"; he judges its age and condition ({said(judge)})."
                if judge.succeeded
                else f"; he cannot vouch for its age or condition ({said(judge)})."
            )
        )
    if done.found:
        for guest in guests:
            read = _roll(
                rng, guest.perception + guest.hunt, ASSEMBLY_EASE, saga, stress=False
            )
            if read.succeeded:
                done.read = True
                done.lines.append(
                    f"At the assembly {guest.name} reads the droppings: its age, "
                    f"health and size ({said(read)})."
                )
    return done


# -- the chase --


@dataclass
class Chase:
    """The chase round by round: who won, the Terrain Bonus at the end, who
    fell behind, each hunter's Long-Term Fatigue lost, and the lines."""

    cornered: bool = False
    rounds: int = 0
    hounds_won: int = 0
    prey_won: int = 0
    terrain: int = TERRAIN_BONUS
    behind: list[str] = field(default_factory=list)
    thrown: list[str] = field(default_factory=list)
    long_term: dict[str, int] = field(default_factory=dict)
    lines: list[str] = field(default_factory=list)


def _keep_up(
    done: Chase,
    riding: list[Hunter],
    round_: int,
    rng: random.Random,
    saga: Saga | None,
) -> None:
    """Each hunter still riding keeps the hounds in sight, or falls behind
    (thrown, on a botch)."""
    for hunter in list(riding):
        keep = _roll(rng, hunter.dexterity + hunter.ride, RIDE_EASE, saga, stress=True)
        if keep.succeeded:
            continue
        riding.remove(hunter)
        done.behind.append(hunter.name)
        if keep.die.botched:
            done.thrown.append(hunter.name)
            done.lines.append(
                f"Hour {round_}: {hunter.name} is thrown from the saddle."
            )
        else:
            done.lines.append(f"Hour {round_}: {hunter.name} falls behind.")


def _relay(
    relay: Sequence[Huntsman], evasion: int, rng: random.Random, saga: Saga | None
) -> tuple[bool, bool]:
    """The relay's round: whether fresh dogs join the pack, and whether a
    huntsman's Area Lore cuts the Terrain Bonus (once a round at most)."""
    fresh = cut = False
    for man in relay:
        placed = _roll(
            rng, man.intelligence + man.hunt + RELAY_BONUS, evasion, saga, stress=True
        )
        if not placed.succeeded:
            continue
        fresh = True
        if not cut:
            ground = _roll(
                rng, man.intelligence + man.area_lore, evasion, saga, stress=True
            )
            cut = bool(ground.succeeded)
    return fresh, cut


def _saddle_sore(
    done: Chase, riding: Sequence[Hunter], rng: random.Random, saga: Saga | None
) -> None:
    """Every third round, each hunter riding keeps his strength or loses a
    Long-Term Fatigue level."""
    for hunter in riding:
        held = _roll(
            rng, hunter.stamina + hunter.ride, RIDE_STAMINA_EASE, saga, stress=False
        )
        if not held.succeeded:
            done.long_term[hunter.name] = done.long_term.get(hunter.name, 0) + 1


def _tires(tiring: int, rng: random.Random, saga: Saga | None) -> bool:
    """Whether a beast loses a Fatigue level this round."""
    return not _roll(rng, tiring, TIRING_EASE, saga, stress=False).succeeded


def _ending(done: Chase, quarry: Quarry, hounds_spent: bool) -> str:
    if done.hounds_won >= ROUNDS_TO_WIN:
        return f"After {done.rounds} hours the {quarry.name.lower()} turns at bay."
    if done.prey_won >= ROUNDS_TO_WIN:
        return f"After {done.rounds} hours the quarry escapes."
    # The book ends a chase only on four rounds won or nightfall; a spent
    # prey or pack is the app's gap-fill.
    if done.cornered:
        return (
            f"After {done.rounds} hours the {quarry.name.lower()} is spent and "
            f"turns at bay ({GAP_FILL})."
        )
    if hounds_spent:
        return f"The hounds are spent: the quarry escapes ({GAP_FILL})."
    return "Darkness falls before the quarry is cornered: it escapes."


def chase(
    hound: Hound,
    quarry: Quarry,
    hunters: Sequence[Hunter],
    relay: Sequence[Huntsman],
    rng: random.Random,
    *,
    native: bool = True,
    hours: int = 12,
    saga: Saga | None = None,
) -> Chase:
    """Run the chase (pp. 52-53) an hour a round until four rounds are won
    either way, not necessarily in a row (a tie counts for neither), or
    darkness falls. A prey or pack spent past its last Fatigue level also
    ends it: the book leaves that case open, and this is the app's
    gap-fill."""
    done = Chase(terrain=TERRAIN_BONUS if native else 0)
    riding = list(hunters)
    hounds_lost = prey_lost = 0
    for round_ in range(1, max(hours, 1) + 1):
        done.rounds = round_
        _keep_up(done, riding, round_, rng, saga)
        pursuit = _roll(
            rng,
            hound.pursuit + penalty(hound.fatigue, hounds_lost),
            None,
            saga,
            stress=True,
        ).total
        evasion = _roll(
            rng,
            quarry.evasion + done.terrain + penalty(quarry.fatigue, prey_lost),
            None,
            saga,
            stress=True,
        ).total
        fresh, relay_cut = _relay(relay, evasion, rng, saga)
        hunters_cut = any(
            _roll(rng, h.perception + h.area_lore, evasion, saga, stress=True).succeeded
            for h in riding
        )
        if pursuit != evasion:
            gained = pursuit > evasion
            done.hounds_won += gained
            done.prey_won += not gained
            outcome = "the hounds gain" if gained else "the quarry gains"
        else:
            outcome = "neither gains"
        said_more = ["fresh dogs from the relay"] if fresh else []
        cut = int(relay_cut) + int(hunters_cut)
        if cut:
            done.terrain -= cut
            said_more.append(f"Terrain Bonus now {done.terrain:+d}")
        done.lines.append(
            f"Hour {round_}: Pursuit {pursuit} against Evasion {evasion}: {outcome}"
            + (f" ({'; '.join(said_more)})" if said_more else "")
            + "."
        )
        hounds_lost = 0 if fresh else hounds_lost + _tires(hound.tiring, rng, saga)
        prey_lost += _tires(quarry.tiring, rng, saga)
        if round_ % RIDE_STAMINA_EVERY == 0:
            _saddle_sore(done, riding, rng, saga)
        # Four rounds won is the book's ending; a prey spent past its last
        # Fatigue level is the app's gap-fill for a case the book leaves open.
        done.cornered = done.hounds_won >= ROUNDS_TO_WIN or spent(
            quarry.fatigue, prey_lost
        )
        if (
            done.cornered
            or done.prey_won >= ROUNDS_TO_WIN
            or spent(hound.fatigue, hounds_lost)
        ):
            break
    done.lines.append(_ending(done, quarry, spent(hound.fatigue, hounds_lost)))
    return done


def still_riding(hunters: Sequence[Hunter], done: Chase) -> list[Hunter]:
    return [h for h in hunters if h.name not in done.behind]


# -- hawking (pp. 57-59) --


@dataclass(frozen=True)
class Bird:
    """A hawk or falcon (p. 59): its best attack, Size, and the largest
    prey it will take untrained (None: any)."""

    key: str
    name: str
    attack: int
    damage: int
    init: int
    size: int
    largest: int | None = None
    words: str = ""


BIRDS: dict[str, Bird] = {
    b.key: b
    for b in (
        Bird(
            "gyrfalcon",
            "Gyrfalcon",
            6,
            -4,
            8,
            -3,
            words="the largest and most prized falcon; talons",
        ),
        Bird(
            "peregrine",
            "Peregrine falcon",
            6,
            -6,
            7,
            -4,
            words="an ambush predator: +3 to attack unsuspecting prey from "
            "hiding, not counted here",
        ),
        Bird(
            "goshawk",
            "Goshawk",
            9,
            -4,
            5,
            -3,
            largest=-2,
            words="flown from the fist; Aggressive, +3 to attack; no prey above "
            "Size -2 unless trained to it",
        ),
        Bird(
            "merlin",
            "Merlin",
            6,
            -9,
            11,
            -5,
            largest=-5,
            words="small and very fast; prey up to partridge size",
        ),
        Bird(
            "lanner_pair",
            "Pair of lanners",
            12,
            -6,
            7,
            -4,
            words="taught to hunt as a trained pair",
        ),
        Bird(
            "sparrowhawk",
            "Sparrowhawk",
            6,
            -7,
            8,
            -4,
            words="the most common hawk, and notoriously fragile",
        ),
    )
}


@dataclass(frozen=True)
class Prey:
    """A beast or bird from p. 58's Some Typical Prey Animals (None for
    the table's n/a)."""

    name: str
    size: int
    dexterity: int
    defense: int
    soak: int


PREY: dict[str, Prey] = {
    p.name.lower(): p
    for p in (
        Prey("Partridge", -5, 3, 9, 0),
        Prey("Hare", -6, 3, 4, 1),
        Prey("Duck", -3, 3, 7, 0),
        Prey("Goose", -2, 3, 6, 1),
        Prey("Pheasant", -2, 3, 7, 0),
        Prey("Heron", -2, 4, 7, -1),
        Prey("Crane", -1, 3, 5, 0),
    )
}


@dataclass(frozen=True)
class Flight:
    """What the hawking table (p. 58) makes of a total."""

    attacks: bool
    bonus: int = 0
    init_bonus: int = 0
    again: bool = False
    loyalty_check: bool = False
    words: str = ""


def flight(total: int) -> Flight:
    """The hawking table's result for a Presence + Animal Handling total."""
    if total <= 0:
        return Flight(
            False,
            loyalty_check=True,
            words="A Loyalty check for the bird: on a failure it leaves, never "
            "to be seen again.",
        )
    if total <= 3:
        return Flight(
            False,
            words="The hawk flies off to a nearby tree and looks back quizzically.",
        )
    if total <= 6:
        return Flight(
            False, words="The hawk ignores its quarry, circles, and comes back."
        )
    if total <= 9:
        return Flight(True, words="The hawk makes a single attack on its prey.")
    if total <= 12:
        return Flight(True, 1, words="The hawk attacks, +1 to its attack.")
    if total <= 15:
        return Flight(True, 2, words="The hawk attacks, +2 to its attack.")
    if total <= 20:
        return Flight(True, 3, words="The hawk attacks, +3 to its attack.")
    return Flight(
        True,
        5,
        5,
        again=True,
        words="The hawk attacks, +5 to attack and Initiative, and keeps on striking.",
    )


def hawker_total(character: Character) -> int:
    """Presence + Animal Handling, less the Gift's social penalty (p. 58;
    DE p. 204)."""
    return (
        character.characteristics.presence
        + scores.ability_level(character, ANIMAL_HANDLING)
        - gift_social_penalty(character)
    )


@dataclass
class Hawking:
    """A hawking flight: the roll, what the table makes of it, each strike,
    whether the prey was killed, whether the bird was lost, and the lines."""

    total: int = 0
    result: Flight = field(default_factory=lambda: flight(0))
    killed: bool = False
    lost: bool = False
    lines: list[str] = field(default_factory=list)


def will_stoop(bird: Bird, prey: Prey, trained: bool) -> bool:
    """Whether the bird will attack prey this size (p. 59)."""
    return bird.largest is None or prey.size <= bird.largest or trained


def hawk(
    modifiers: int,
    bird: Bird,
    prey: Prey,
    rng: random.Random,
    *,
    loyal: int = 0,
    trained: bool = False,
    saga: Saga | None = None,
) -> Hawking:
    """Fly the bird at the prey: the hawker's roll (a simple die: the book
    names none) on p. 58's table, then the bird's strikes. At 21+ it goes
    on attacking after the first, miss or hit, with no limit in the book;
    the app stops it on a kill or, by its own limit, after MOST_STRIKES."""
    roll = _roll(rng, modifiers, None, saga, stress=False)
    done = Hawking(total=roll.total)
    done.result = flight(roll.total)
    shown = "a botch" if roll.die.botched else str(roll.total)
    done.lines.append(f"Presence + Animal Handling: {shown}. {done.result.words}")
    if done.result.loyalty_check:
        check = _roll(rng, loyal, LOYALTY_EASE, saga, stress=False)
        done.lost = not check.succeeded
        done.lines.append(
            f"Loyalty check {said(check)}: "
            + ("the bird is gone for good." if done.lost else "the bird comes back.")
        )
        return done
    if not done.result.attacks:
        return done
    if not will_stoop(bird, prey, trained):
        done.lines.append(
            f"The {bird.name.lower()} will not stoop at prey as large as a "
            f"{prey.name.lower()} unless trained to it."
        )
        return done
    strikes = MOST_STRIKES if done.result.again else 1
    for strike in range(1, strikes + 1):
        attack = _roll(
            rng, bird.attack + done.result.bonus, None, saga, stress=True
        ).total
        defense = _roll(rng, prey.defense, None, saga, stress=True).total
        if not combat.hits(attack, defense):
            done.lines.append(
                f"Strike {strike}: Attack {attack} against Defense {defense}: a miss."
            )
            continue
        excess = combat.damage_dealt(bird.damage, attack, defense) - prey.soak
        wound = derived.wound_for(excess, prey.size)
        done.killed = wound in ("Incapacitating", "Dead")
        done.lines.append(
            f"Strike {strike}: Attack {attack} against Defense {defense}: "
            + (
                f"a {wound} wound" + (": a kill." if done.killed else ".")
                if wound
                else "a hit that does no harm."
            )
        )
        if done.killed:
            break
    else:
        if strikes > 1:
            done.lines.append(
                f"The app stops the hawk after {strikes} strikes; the book sets "
                "no limit (p. 58)."
            )
    return done


# -- Area Lore (C&G pp. 82-83) --


@dataclass(frozen=True)
class Sought:
    """One line of the Area Lore Ease Factors table, in the app's words."""

    key: str
    ease: int
    words: str


SOUGHT: tuple[Sought, ...] = (
    Sought("common_shop", 6, "a shop selling what everyone wants"),
    Sought("free_goods", 6, "a hunting or fishing spot, where goods are free"),
    Sought("major_road", 6, "a major road, ferry, ford, pass or bridge"),
    Sought("major_hazard", 6, "a major hazard on the main route"),
    Sought("major_inn", 6, "a major inn"),
    Sought("festival", 6, "how to behave as a minor guest at a festival"),
    Sought("section_shop", 9, "a shop for one part of society (farrier, cooper)"),
    Sought("hedge_magician", 9, "most hedge magicians"),
    Sought("small_road", 9, "the smaller gravel or paved roads"),
    Sought("regional_hazard", 9, "hazards off the main roads and rivers"),
    Sought("village_inn", 9, "the largest inn or hospice near each village"),
    Sought("reputation_6", 9, "people with Reputations of 6 or more"),
    Sought("customs_illegal", 9, "local customs it is illegal or despised to ignore"),
    Sought("narrow_shop", 12, "a shop for a narrow few (books, cosmetics, silks)"),
    Sought("any_road", 12, "the road to any mundane place in the region"),
    Sought("town_danger", 12, "a town's hazardous quarters, and how to pass them"),
    Sought("route_inns", 12, "small inns on the route, and where to camp"),
    Sought("reputation_3", 12, "people with Reputations of 3 or more"),
    Sought("customs_reputation", 12, "laws or customs that slowly cost Reputation"),
    Sought("illegal_trade", 15, "one selling an illegal, repressed service"),
    Sought("minor_tracks", 15, "minor tracks, or roads to deserted settlements"),
    Sought("ill_repute", 15, "persons or places of ill repute on the route"),
    Sought("best_room", 15, "the best room in each season, and shelter in storms"),
    Sought("community", 15, "anyone publicly part of a community on the route"),
    Sought("alliances", 15, "the public alliances and marriages of notable people"),
    Sought("real_power", 15, "who is really in charge, and how to meet them"),
    Sought("heinous", 18, "one selling heinous services: murder for hire"),
    Sought("supernatural_road", 18, "roads under supernatural sway (faerie trods)"),
    Sought("brief_hazards", 18, "brief hazards: charged nights, the bailiffs' rounds"),
    Sought("hidden_people", 18, "the deliberately hidden: smugglers or bandits"),
)
SOUGHT_BY_KEY = {s.key: s for s in SOUGHT}
OTHER = "other"
FREE_GOODS = SOUGHT_BY_KEY["free_goods"]

#: Where the character lives against where he seeks (p. 82).
AT_HOME = "home"
TOWNSMAN_ABROAD = "townsman"
COUNTRYMAN_IN_TOWN = "countryman"
AWAY_PENALTY = 3
AWAY: dict[str, str] = {
    AT_HOME: "Where he spends his time",
    TOWNSMAN_ABROAD: "A townsman in the hinterland (-3)",
    COUNTRYMAN_IN_TOWN: "A countryman in the city (-3)",
}


def away_penalty(where: str) -> int:
    return 0 if where == AT_HOME else -AWAY_PENALTY


def area_lore_roll(
    intelligence: int,
    score: int,
    ease: int,
    rng: random.Random,
    *,
    where: str = AT_HOME,
    saga: Saga | None = None,
) -> dice.Roll:
    """Intelligence + Area Lore (simple die, the app's reading) against the
    table's Ease Factor, 3 off for one seeking away from his own ground."""
    return _roll(
        rng, intelligence + score + away_penalty(where), ease, saga, stress=False
    )
