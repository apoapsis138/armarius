"""The Mysteries Revised Edition's alchemy (Chapter Five, pp. 39-46) and
its Great and Consummate Talismans (Chapter Ten, pp. 89-90), as plain rule
functions. Hermetic Alchemy's own extraction (Shape and Material bonuses
up to Magic Theory, Form vis at a twentieth) is rules.lab_virtues'.

Philosophic Alchemy (Minor or Major Mystery Virtue, pp. 40-41; needs
Hermetic Alchemy):

- The magus settles an alchemical extraction to digest by itself: the same
  Lab Total, bonuses and yield as Hermetic Alchemy's, while he does other
  work. The digestion is a seven-day distraction to that other work only;
  his days away count against both. More than 20 days away in a season
  spoils the digestion (DE p. 265's limit), as does experimenting while it
  digests. Only one extraction at a time, of any kind, in one laboratory.
- The Minor Virtue takes four continuous seasons and yields by the lowest
  of the four seasons' Lab Totals; the Major one season. Initiating the
  Major replaces the Minor, its loss an Ordeal (loss of a Virtue).
- Instead of vis, a Creo Vim digestion opens a device: as many spaces as
  the pawns of Vim vis it would have given. The magus chooses (p. 41):
  they count as pawns already opened (the device is ready for
  enchantment, and opening it normally costs that many fewer pawns), or
  as extra room on top of what the device could normally hold (its
  capacity rises by that many spaces, already open; opening the rest
  costs its normal capacity).

The Lesser Elixir (Minor Mystery Virtue, pp. 42-43; needs Hermetic
Alchemy): each season reinventing it adds a special ingredient, its Shape
and Material bonus in Elixir Points (doubled for one the alchemist devised
by Vulgar Alchemy; no ingredient above Magic Theory). The Elixir Level is
worked out from the points as an Art's score from experience, at most
Magic Theory when devised, and adds to his own Longevity Ritual's modifier
while a dose of the Elixir is in force. An Aging Crisis ends it.

The Great Elixir (Major Mystery Virtue, pp. 43-44; needs Unaging and the
Lesser Elixir): a consumable invested device whose Lesser Elixir dose
takes (Longevity Ritual level / 10) spaces, with Become a Being of Magic
(MuCo(Vi) 50) and Grant Might (Might = half of its level less 20). Drunk,
it is tested with a simple die + Stamina + Lesser Elixir Level + 1 for each
earlier attempt (at most Magic Theory) against age / 10, rounded up; an
immortal's Ease Factor stays at the age he transformed. Success makes him
a being of the Magic realm with Grant Might's Magic Might: he no longer
ages nor gains Warping (p. 44); a later, better potion raises his Might
to its own, the attempts' bonus counting afresh. A failure wastes the
potion: the next one, with new effects, adds 1 more. The errata to p.
133 (Errata p. 51): an immortal's talisman is no longer limited by his
highest Technique and Form.

Great Talisman (Minor Hermetic Mystery Virtue, pp. 89-90): the magus opens
one attunement a season merely by using his talisman, without working on
it (still one a season), and may craft new components into it each time
he reopens it, no Craft roll, up to Magic Theory components in all (the
DE's limit for any compound device, p. 255). Consummate Talisman (Major,
p. 90; needs Great Talisman or Inscription on the Soul): Personal Muto Vim
effects in the talisman work on his Formulaic spells, and Names of Power
in it on any spell (their bonus at most Magic Theory, the errata to pp.
77-78 adding "combined"), at the cost of Deleterious Circumstances (when
not touching talisman), a Minor Ordeal -- or Necessary Condition (must
wield talisman), a Major one, for a magus with similar Circumstances
already; one with his talisman as a Condition or Restriction needs no new
Flaw. The errata's p. 70 insert (Errata p. 50): Inscription on the Soul
alone does not attune bonuses without work on the talisman.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..models import (
    DIGEST_SPACES,
    SEASONS,
    Alchemy,
    Character,
    Digestion,
    ElixirIngredient,
    EnchantedDevice,
    InstilledEffect,
    next_season,
)
from . import lab, lab_virtues
from . import xp as xp_rules
from .breakdown import Breakdown, Line
from .rounding import round_down, round_up

_CH5 = "The Mysteries Revised Edition, Chapter Five: Hermetic Alchemy, {}, {}"
SOURCE = "The Mysteries Revised Edition, Chapter Five: Hermetic Alchemy, pp. 39-46"
HERMETIC_SOURCE = _CH5.format("Hermetic Alchemy", "pp. 39-40")
PHILOSOPHIC_SOURCE = _CH5.format("Philosophic Alchemy", "pp. 40-41")
LESSER_SOURCE = _CH5.format("The Lesser Elixir", "pp. 42-43")
GREAT_SOURCE = _CH5.format("The Great Elixir", "pp. 43-44")
COCKEREL_SOURCE = _CH5.format("The Order of the Green Cockerel", "pp. 44-46")
_CH10 = "The Mysteries Revised Edition, Chapter Ten: The Great Talisman, {}, {}"
TALISMAN_SOURCE = _CH10.format("Great Talisman", "pp. 89-90")
CONSUMMATE_SOURCE = _CH10.format("Consummate Talisman", "p. 90")
DISTRACTION_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Distractions from Lab "
    "Work, p. 265"
)
IMMORTAL_ERRATA = (
    "Errata (Ars Magica 5th Edition), The Mysteries Revised Edition, Immortal "
    "Beings and Permanent Change (p. 133), Errata p. 51"
)
INSCRIPTION_ERRATA = (
    "Errata (Ars Magica 5th Edition), The Mysteries Revised Edition, The Great or "
    "Consummate Talisman (p. 70), Errata p. 50"
)

HERMETIC_ALCHEMY = lab_virtues.ALCHEMY
PHILOSOPHIC_MINOR = "vf_philosophic_alchemy"
PHILOSOPHIC_MAJOR = "vf_philosophic_alchemy_major"
LESSER_ELIXIR = "vf_the_lesser_elixir"
GREAT_ELIXIR = "vf_the_great_elixir"
UNAGING = "vf_unaging"
VULGAR_ALCHEMY = "vf_vulgar_alchemy"
GREAT_TALISMAN = "vf_great_talisman"
CONSUMMATE_TALISMAN = "vf_consummate_talisman"
INSCRIPTION = "vf_inscription_on_the_soul"
DELETERIOUS = "vf_deleterious_circumstances"
NECESSARY_CONDITION = "vf_necessary_condition"
RESTRICTION = "vf_restriction"

MINOR, MAJOR = "Minor", "Major"
#: Seasons a digestion takes, by the Philosophic Alchemy Virtue's tier.
DIGESTION_SEASONS: dict[str, int] = {MINOR: 4, MAJOR: 1}
#: Tending a digestion: days of distraction to the season's other work.
TENDING_DAYS = 7
#: More days away than this in a season spoil a digestion.
MOST_DAYS_AWAY = 20
#: The Great Elixir's own effects.
BECOME_A_BEING_OF_MAGIC = 50
GRANT_MIGHT_FLOOR = 20
#: The circumstance Consummate Talisman's Flaw names.
TALISMAN_CIRCUMSTANCE = "when not touching talisman"


def _has(magus: Character, vf_id: str) -> bool:
    return lab_virtues.has(magus, vf_id)


def magic_theory(magus: Character) -> int:
    """Magic Theory with its bonuses, which every limit here is."""
    return sum(lab.ability_score(magus, "Magic Theory"))


# -- Philosophic Alchemy -------------------------------------------------------


def philosophic_tier(magus: Character) -> str:
    """ "Major", "Minor", or "" without Philosophic Alchemy."""
    if _has(magus, PHILOSOPHIC_MAJOR):
        return MAJOR
    return MINOR if _has(magus, PHILOSOPHIC_MINOR) else ""


def digestion_seasons(magus: Character) -> int:
    """The seasons the magus's digestion takes (0 without the Virtue)."""
    return DIGESTION_SEASONS.get(philosophic_tier(magus), 0)


def digest_problem(magus: Character) -> str:
    """Why the magus can't settle a digestion ("" when he can)."""
    if not philosophic_tier(magus):
        return f"{magus.name} hasn't Philosophic Alchemy ({PHILOSOPHIC_SOURCE})."
    if not _has(magus, HERMETIC_ALCHEMY):
        return (
            f"Philosophic Alchemy builds on Hermetic Alchemy, which {magus.name} "
            f"hasn't ({PHILOSOPHIC_SOURCE})."
        )
    if magus.alchemy is not None and magus.alchemy.digestion is not None:
        return f"{magus.name} already has a digestion running: one at a time."
    return ""


def season_list(digestion: Digestion) -> list[tuple[str, int]]:
    """The seasons a digestion runs, first to last."""
    found: list[tuple[str, int]] = []
    season, year = digestion.season, digestion.year
    if season not in SEASONS:
        return found
    for _ in range(max(1, digestion.seasons)):
        found.append((season, year))
        season, year = next_season(season, year)
    return found


def digestion_in(magus: Character, season: str, year: int) -> Digestion | None:
    """The digestion the magus tends in that season, if one runs then."""
    digestion = magus.alchemy.digestion if magus.alchemy is not None else None
    if digestion is None or (season, year) not in season_list(digestion):
        return None
    return digestion


def tending_line(days_away: int) -> Line:
    """What tending the digestion takes off the season's other lab work: the
    distraction of its seven days added to the days away, less what the
    days away cost alone (none until the two pass ten days)."""
    alone = lab.distraction_penalty(max(0, days_away)) or 0
    together = lab.distraction_penalty(max(0, days_away) + TENDING_DAYS)
    extra = (together if together is not None else -30) - alone
    return Line(
        f"Tending the digestion ({TENDING_DAYS} days, Philosophic Alchemy)",
        amount=extra,
        source=PHILOSOPHIC_SOURCE,
    )


def tending_problem(days_away: int) -> str:
    """Why no other lab work is possible beside the digestion this season
    ("" when it is): its seven days and the days away pass twenty."""
    days = max(0, days_away) + TENDING_DAYS
    if lab.distraction_penalty(days) is None:
        return (
            f"{max(0, days_away)} days away and {TENDING_DAYS} tending the "
            f"digestion make {days}: no other lab work is possible this season "
            f"(more than {MOST_DAYS_AWAY}; {PHILOSOPHIC_SOURCE})."
        )
    return ""


def spoils(days_away: int) -> bool:
    """More than twenty days out of the laboratory spoil the digestion."""
    return days_away > MOST_DAYS_AWAY


def pawns_from(total: int, digestion: Digestion, magus: Character) -> int:
    """What a Lab Total yields: Vim vis or open spaces at a tenth (rounded
    up), a Form's vis at its Hermetic Alchemy divisor (a twentieth, a tenth
    with its Extractor Virtue)."""
    if total <= 0:
        return 0
    if digestion.product == DIGEST_SPACES or not digestion.form:
        return round_up(total / 10)
    return round_up(total / lab_virtues.form_extraction_divisor(magus, digestion.form))


def digestion_yield(digestion: Digestion, magus: Character) -> int:
    """The finished digestion's yield: by the lowest of its seasons' Lab
    Totals (the Minor Virtue's four; the Major's one)."""
    if not digestion.totals:
        return 0
    return pawns_from(min(digestion.totals), digestion, magus)


def finished(digestion: Digestion) -> bool:
    return len(digestion.totals) >= max(1, digestion.seasons)


def opening_left(capacity: int, spaces: int) -> int:
    """Pawns still needed to open a device the digestion opened `spaces`
    of, counting them against its capacity (TMRE p. 41's example: 24 less
    8 is 16)."""
    return max(0, capacity - spaces)


def open_spaces(device: EnchantedDevice, spaces: int, extra_room: bool) -> None:
    """A finished digestion's `spaces` put into `device`: as pawns of its
    capacity already opened, or (`extra_room`) as room on top of its
    capacity, already open (p. 41 offers both)."""
    spaces = max(0, spaces)
    if extra_room:
        device.extra_spaces += spaces
    device.pawns_opened += spaces


def spaces_text(extra_room: bool) -> str:
    """How a digestion's open spaces count, for its notes."""
    if extra_room:
        return (
            "extra room on top of its capacity, already open; opening the rest "
            f"costs its normal capacity ({PHILOSOPHIC_SOURCE})"
        )
    return (
        "pawns already opened: ready for enchantment, and opening it normally "
        f"costs that many pawns fewer ({PHILOSOPHIC_SOURCE})"
    )


def replaces_minor(magus: Character) -> bool:
    """Initiating the Major Virtue replaces the Minor one, whose loss counts
    as an Ordeal (loss of a Virtue) for the Initiation."""
    return _has(magus, PHILOSOPHIC_MINOR)


def start(magus: Character, digestion: Digestion, season: str, year: int) -> Digestion:
    """Settle `digestion` in `season`: it takes the seasons the magus's
    Virtue gives. Returns it."""
    digestion.season, digestion.year = season, year
    digestion.seasons = digestion_seasons(magus) or 1
    digestion.totals = []
    if magus.alchemy is None:
        magus.alchemy = Alchemy()
    magus.alchemy.digestion = digestion
    return digestion


def abandon(magus: Character) -> None:
    if magus.alchemy is not None:
        magus.alchemy.digestion = None


# -- The Lesser Elixir ---------------------------------------------------------


def ingredient_points(bonus: int, devised: bool, magic_theory: int) -> int:
    """An ingredient's Elixir Points: its bonus, doubled for one the
    alchemist devised himself, never above Magic Theory."""
    points = max(0, bonus) * (2 if devised else 1)
    return min(points, max(0, magic_theory))


def elixir_points(ingredients: Sequence[ElixirIngredient], magic_theory: int) -> int:
    return sum(ingredient_points(i.bonus, i.devised, magic_theory) for i in ingredients)


def elixir_level(points: int, magic_theory: int) -> int:
    """The Elixir Level: from Elixir Points as an Art's score from
    experience (1, 3, 6, 10...), at most Magic Theory."""
    level = xp_rules.score_from_xp(max(0, points), xp_rules.ART_FACTOR)
    return min(level, max(0, magic_theory))


def elixir_breakdown(
    ingredients: Sequence[ElixirIngredient], magic_theory: int
) -> Breakdown:
    """The Elixir Points, an ingredient a line, and the Level they give."""
    lines = [
        Line(
            f"{i.name or 'Ingredient'} (+{i.bonus}"
            + (", devised: doubled" if i.devised else "")
            + ")",
            amount=ingredient_points(i.bonus, i.devised, magic_theory),
            source=LESSER_SOURCE,
        )
        for i in ingredients
    ]
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def lesser_elixir_problem(magus: Character) -> str:
    if not _has(magus, LESSER_ELIXIR):
        return f"{magus.name} hasn't the Lesser Elixir ({LESSER_SOURCE})."
    if not _has(magus, HERMETIC_ALCHEMY):
        return f"The Lesser Elixir needs Hermetic Alchemy ({LESSER_SOURCE})."
    return ""


def add_ingredient(magus: Character, ingredient: ElixirIngredient) -> tuple[int, int]:
    """Reinvent the Lesser Elixir with one more ingredient: the formula's
    points and Level, devised now at the magus's Magic Theory. The Level
    is kept for his aging rolls, active from the dose it is made with.
    Returns (points, level)."""
    if magus.alchemy is None:
        magus.alchemy = Alchemy()
    magus.alchemy.ingredients.append(ingredient)
    theory = magic_theory(magus)
    points = elixir_points(magus.alchemy.ingredients, theory)
    magus.alchemy.elixir_level = elixir_level(points, theory)
    magus.alchemy.elixir_active = True
    return points, magus.alchemy.elixir_level


def ritual_performed(subject: Character, performer: Character) -> str:
    """A Longevity Ritual just made or performed again for `subject`: an
    alchemist performing his own adds his Lesser Elixir's ingredients to the
    dose (taking little more time, p. 43), so the Elixir is in force; any
    other dose ends it. Returns a note ("" when nothing changes)."""
    alchemy_ = subject.alchemy
    if alchemy_ is None or not alchemy_.ingredients:
        return ""
    if subject is performer and _has(subject, LESSER_ELIXIR):
        alchemy_.elixir_active = True
        return (
            f"The Lesser Elixir's ingredients are added: Elixir Level "
            f"{alchemy_.elixir_level} more to aging rolls ({LESSER_SOURCE})."
        )
    alchemy_.elixir_active = False
    return f"The Lesser Elixir is not in this dose ({LESSER_SOURCE})."


def end_elixir(magus: Character) -> None:
    """An Aging Crisis, or a new Longevity Ritual, ends the dose in force:
    the Elixir must be repeated."""
    if magus.alchemy is not None:
        magus.alchemy.elixir_active = False


def aging_lines(longevity_modifier: int, magus: Character) -> list[Line]:
    """The Aging Bonus: the Longevity Ritual's modifier, plus the Elixir
    Level while a dose of it is in force."""
    lines = [Line("Longevity Ritual", amount=longevity_modifier, source="")]
    bonus = magus.alchemy.elixir_bonus if magus.alchemy is not None else 0
    if bonus:
        lines.append(
            Line(f"Lesser Elixir (Level {bonus})", amount=bonus, source=LESSER_SOURCE)
        )
    return lines


# -- The Great Elixir ----------------------------------------------------------


def has_great_elixir(magus: Character) -> bool:
    return _has(magus, GREAT_ELIXIR)


def great_elixir_problem(magus: Character) -> str:
    if not _has(magus, GREAT_ELIXIR):
        return f"{magus.name} hasn't the Great Elixir ({GREAT_SOURCE})."
    missing = [
        name
        for vf_id, name in ((UNAGING, "Unaging"), (LESSER_ELIXIR, "the Lesser Elixir"))
        if not _has(magus, vf_id)
    ]
    if missing:
        return f"The Great Elixir needs {' and '.join(missing)} ({GREAT_SOURCE})."
    return ""


def elixir_spaces(longevity_level: int) -> int:
    """Spaces the Lesser Elixir dose takes in the Great Elixir device: the
    Longevity Ritual's level / 10, rounded up as an effect's are."""
    return max(0, round_up(longevity_level / 10))


def granted_might(level: int) -> int:
    """Grant Might's Magic Might: half of (its level less 20)."""
    return max(0, round_down((level - GRANT_MIGHT_FLOOR) / 2))


def great_ease(age: int) -> int:
    """The test's Ease Factor: age / 10, rounded up."""
    return max(0, round_up(age / 10))


def great_test_lines(
    stamina: int, lesser_level: int, earlier_attempts: int, magic_theory: int
) -> list[Line]:
    """What the simple die is added to: Stamina, the Lesser Elixir Level,
    and +1 for each earlier attempt, at most Magic Theory."""
    lines = [
        Line("Stamina", amount=stamina, source=GREAT_SOURCE),
        Line("Lesser Elixir Level", amount=lesser_level, source=GREAT_SOURCE),
    ]
    reroll = min(max(0, earlier_attempts), max(0, magic_theory))
    if reroll:
        lines.append(Line("Earlier attempts", amount=reroll, source=GREAT_SOURCE))
    return lines


def great_succeeds(die: int, lines: Sequence[Line], ease: int) -> bool:
    return die + sum(line.amount or 0 for line in lines) >= ease


def transformed(magus: Character) -> bool:
    """Whether the Great Elixir has made the magus a being of Magic."""
    return magus.alchemy is not None and magus.alchemy.immortal_age is not None


def great_ease_basis(magus: Character, age: int) -> int:
    """The age the test's Ease Factor is by: his age, or the age he
    transformed at once he is immortal (he no longer ages)."""
    if magus.alchemy is not None and magus.alchemy.immortal_age is not None:
        return magus.alchemy.immortal_age
    return age


def great_ease_for(magus: Character, age: int) -> int:
    """The test's Ease Factor for the magus (great_ease_basis / 10)."""
    return great_ease(great_ease_basis(magus, age))


def magus_test_lines(magus: Character) -> list[Line]:
    """The test's bonuses for the magus: his Stamina, his Lesser Elixir
    Level and his attempts since the last success."""
    alchemy_ = magus.alchemy
    return great_test_lines(
        magus.characteristics.stamina,
        alchemy_.elixir_level if alchemy_ is not None else 0,
        alchemy_.great_attempts if alchemy_ is not None else 0,
        magic_theory(magus),
    )


@dataclass(frozen=True)
class GreatTest:
    """A Great Elixir drunk and tested: the die, what it is added to, the
    Ease Factor, and the Magic Might its Grant Might gives."""

    die: int
    lines: tuple[Line, ...]
    ease: int
    might: int

    @property
    def total(self) -> int:
        return self.die + int(sum(line.amount or 0 for line in self.lines))

    @property
    def succeeds(self) -> bool:
        return self.total >= self.ease


def great_test(magus: Character, age: int, die: int, grant_level: int) -> GreatTest:
    """The test of a Great Elixir whose Grant Might is `grant_level`."""
    return GreatTest(
        die,
        tuple(magus_test_lines(magus)),
        great_ease_for(magus, age),
        granted_might(grant_level),
    )


def drink_great_elixir(magus: Character, age: int, test: GreatTest) -> str:
    """Apply a tested Great Elixir: on success the magus becomes a being of
    Magic at this age (once) with its Magic Might, and the attempts' bonus
    starts afresh; on a failure the potion is wasted and the next attempt
    gets 1 more. Returns what happened."""
    if magus.alchemy is None:
        magus.alchemy = Alchemy()
    alchemy_ = magus.alchemy
    was_immortal = alchemy_.immortal_age is not None
    if not test.succeeds:
        alchemy_.great_attempts += 1
        if was_immortal:
            return (
                "Failed: the new Great Elixir is wasted, with no other ill effect; "
                f"his Magic Might stays {magus.magic_might} ({GREAT_SOURCE})."
            )
        return (
            "Failed: the Become a Being of Magic and Grant Might effects of this "
            "potion did not work for him; a new dose of the Lesser Elixir and new "
            f"effects make the next potion ({GREAT_SOURCE})."
        )
    alchemy_.great_attempts = 0
    if was_immortal:
        before = magus.magic_might
        magus.magic_might = max(before, test.might)
        return (
            f"Success: his Magic Might is now {magus.magic_might} (was {before}) "
            f"({GREAT_SOURCE})."
        )
    alchemy_.immortal_age = age
    magus.magic_might = test.might
    return (
        f"Success: at {age} he becomes an immortal being of the Magic realm, with "
        f"Magic Might {test.might}. He no longer ages nor gains Warping, and "
        f"later potions are tested against the Ease Factor of this age "
        f"({GREAT_SOURCE})."
    )


# -- Great and Consummate Talismans --------------------------------------------


def component_limit(magus: Character) -> int:
    """The most components a compound device of the magus's may have:
    his Magic Theory (DE p. 255; a great talisman's too, TMRE p. 90). The
    device panel warns of more (enchanted_devices.warnings)."""
    return magic_theory(magus)


def great_talisman(magus: Character) -> bool:
    return _has(magus, GREAT_TALISMAN)


def talisman_notes(magus: Character) -> list[str]:
    """What the magus's Talisman Virtues let him do with his talisman."""
    found: list[str] = []
    theory = component_limit(magus)
    if great_talisman(magus):
        found.append(
            "Great Talisman: an attunement each season merely by using it, "
            "without working on it (still one a season); reopening it may "
            f"craft in new components, no Craft roll, up to {theory} in all "
            f"(Magic Theory) ({TALISMAN_SOURCE})."
        )
    if _has(magus, CONSUMMATE_TALISMAN):
        found.append(
            "Consummate Talisman: its Personal Muto Vim effects work on his "
            "Formulaic spells, its Names of Power on any spell he casts (spoken "
            f"aloud), their bonus at most Magic Theory ({theory}) "
            f"({CONSUMMATE_SOURCE})."
        )
    if _has(magus, INSCRIPTION) and not great_talisman(magus):
        found.append(
            "Inscription on the Soul alone attunes no bonus without work on the "
            f"talisman ({INSCRIPTION_ERRATA})."
        )
    return found


def consummate_effects(effects: Sequence[InstilledEffect]) -> list[InstilledEffect]:
    """The talisman's effects a Consummate Talisman turns on its magus's
    own casting: Muto Vim at Personal Range."""
    return [
        e
        for e in effects
        if e.technique == "Muto" and e.form == "Vim" and e.range == "Personal"
    ]


def consummate_problem(magus: Character) -> str:
    if not (great_talisman(magus) or _has(magus, INSCRIPTION)):
        return (
            "Consummate Talisman needs Great Talisman or Inscription on the Soul "
            f"({CONSUMMATE_SOURCE})."
        )
    return ""


def _talisman_flaw(magus: Character, vf_id: str) -> bool:
    return any(
        vf.vf_id == vf_id and "talisman" in " ".join(vf.params.values()).lower()
        for vf in magus.virtues_flaws
    )


def consummate_ordeal(magus: Character) -> tuple[str, str, str]:
    """Consummate Talisman's Ordeal: (Flaw id, its circumstance, the Ordeal's
    tier). Deleterious Circumstances (when not touching talisman), a Minor
    Ordeal; Necessary Condition (must wield talisman), a Major one, for a
    magus with Deleterious Circumstances already; none for one whose
    talisman is already his Necessary Condition or Restriction (it still
    counts as an Ordeal for this Initiation)."""
    if _talisman_flaw(magus, NECESSARY_CONDITION) or _talisman_flaw(magus, RESTRICTION):
        return "", "", ""
    if _has(magus, DELETERIOUS):
        return NECESSARY_CONDITION, "must wield talisman", MAJOR
    return DELETERIOUS, TALISMAN_CIRCUMSTANCE, MINOR
