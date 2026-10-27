"""A covenant's ships, independent of how they are drawn: Add / Edit
Ship, and the Ships list's More: Stress Check and Ship Combat. The rules
are rules.ships' (Hermetic Projects pp. 53-54, 63; City & Guild pp. 77,
84-87); what each list row and panel shows is ships.py's.

Add / Edit Ship fills a ship from Hermetic Projects' table ("Like", p.
54) and says in its inspector what she can take and carry. Stress Check
rolls her stress die against 15 and takes the damage levels she loses;
Ship Combat rolls the two captains against each other and says what
winning does: boarding sets up a Fight for the two crews (DE pp.
395-396). Both write to the covenant's Diary.

Pattern: each is a commands.Form over the ship's record, so the
terminal's More menu and the desktop's buttons run the same code.
"""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import fields as dataclass_fields
from typing import Any

from .. import diaries, storage
from .. import ships as ship_text
from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField, attr, description_field, pairs
from ..markup import escape
from ..models import Covenant, Fight, FightSide, Possession, Saga
from ..models.ships import SHIP_QUALITIES, SUNK, TAKEN, Ship
from ..rules import dice, equipment
from ..rules import ships as rules

STRESS_TITLE = "Stress Check"
COMBAT_TITLE = "Ship Combat"
#: Both More forms' help page: the Ships list's own.
SHIPS_HELP = "section-pos-ship"
TYPED = "typed"
#: The Ship's own keys a form sets.
SHIP_KEYS = tuple(f.name for f in dataclass_fields(Ship))

AIMS: dict[str, str] = {
    "board": "Close and board",
    "ram": "Ram (a galley; a sailing ship stays entangled)",
    "shear": "Shear their oars (a galley)",
    "escape": "Slip away",
}


def _int(values: dict[str, Any], key: str, default: int = 0) -> int:
    """A number field's value as the user has it so far (0 while it
    doesn't parse)."""
    try:
        return int(values.get(key) or default)
    except TypeError, ValueError:
        return default


def _float(values: dict[str, Any], key: str) -> float:
    try:
        return float(values.get(key) or 0)
    except TypeError, ValueError:
        return 0.0


def ship_from(values: dict[str, Any], base: Ship | None = None) -> Ship:
    """The ship a form's values describe (its other figures from `base`)."""
    start = base or Ship()
    return Ship(
        ship_type=values.get("ship_type") or "",
        kind_name=values.get("kind_name") or "",
        size=_int(values, "size", start.size),
        tons=_int(values, "tons"),
        crew=_int(values, "crew"),
        lateen=bool(values.get("lateen")),
        galley=bool(values.get("galley")),
        quality=values.get("quality") or start.quality,
        excellent_bonus=_int(values, "excellent_bonus", start.excellent_bonus),
        damage_lost=_int(values, "damage_lost"),
        repaired=start.repaired,
        magnitudes=_int(values, "magnitudes"),
        captain_id=values.get("captain_id") or None,
        ballistae=_int(values, "ballistae"),
        catapults=_int(values, "catapults"),
        fighters_tons=_float(values, "fighters_tons"),
        close_to_home=bool(values.get("close_to_home")),
        home_port=values.get("home_port") or "",
    )


def captain_options(saga: Saga, covenant: Covenant) -> list[tuple[str, str]]:
    """The saga's characters, the covenant's own first."""
    people = [c for c in saga.characters if c.animal is None]
    people.sort(key=lambda c: (c.covenant_id != covenant.id, c.name))
    return [(escape(c.name), c.id) for c in people]


# -- Add / Edit Ship --


def ship_fields(
    saga: Saga, covenant: Covenant, record: Possession | None
) -> list[DialogField]:
    ship = record.ship if record is not None and record.ship is not None else None

    def fills(values: dict[str, Any]) -> dict[str, Any]:
        return rules.type_fills(
            values.get("ship_type") or "", values.get("kind_name") or ""
        )

    return [
        DialogField("name", "Name", "text", attr(record, "name", ""), required=True),
        DialogField(
            "ship_type",
            "Like",
            "select",
            attr(ship, "ship_type", "") or None,
            options=rules.type_options(),
            allow_blank=True,
            placeholder="(typed in)",
            fills=fills,
            hint="The book's table fills size, cargo and crew (HP p. 54); "
            "change any of them.",
        ),
        DialogField("kind_name", "Kind", "text", attr(ship, "kind_name", "")),
        DialogField("size", "Size", "int", attr(ship, "size", 5)),
        DialogField("tons", "Cargo (tons)", "int", attr(ship, "tons", 20)),
        DialogField("crew", "Crew", "int", attr(ship, "crew", 8)),
        DialogField(
            "lateen",
            "Lateen-rigged (half again the crew)",
            "check",
            attr(ship, "lateen", False),
        ),
        DialogField(
            "galley",
            "A galley (oars; can ram and shear oars)",
            "check",
            attr(ship, "galley", False),
        ),
        DialogField(
            "quality",
            "Quality",
            "select",
            attr(ship, "quality", "Standard"),
            options=pairs(SHIP_QUALITIES),
            hint="Supernatural: a wondrous ship (C&G p. 70).",
        ),
        DialogField(
            "excellent_bonus",
            "Excellent bonus",
            "int",
            attr(ship, "excellent_bonus", equipment.EXCELLENT_LEAST),
            show_if=lambda v: v.get("quality") == equipment.EXCELLENT,
            hint="+1 for every 3 her builder beat the Craft Level by (C&G p. 69).",
        ),
        DialogField(
            "damage_lost", "Damage levels lost", "int", attr(ship, "damage_lost", 0)
        ),
        DialogField(
            "magnitudes",
            "Magnitudes of invested effects",
            "int",
            attr(ship, "magnitudes", 0),
            hint="The magnitude of the total levels invested in her (all her "
            "effects' levels added together), added to her stress checks "
            "(C&G p. 77; HP p. 53).",
        ),
        DialogField(
            "captain_id",
            "Captain",
            "select",
            attr(ship, "captain_id", None),
            options=captain_options(saga, covenant),
            allow_blank=True,
            placeholder="(none)",
        ),
        DialogField("ballistae", "Ballistae", "int", attr(ship, "ballistae", 0)),
        DialogField("catapults", "Light catapults", "int", attr(ship, "catapults", 0)),
        DialogField(
            "fighters_tons",
            "Cargo given to fighting men (tons)",
            "optfloat",
            attr(ship, "fighters_tons", 0.0) or None,
        ),
        DialogField(
            "close_to_home",
            "Raiding close to home (16 men a quarter ton)",
            "check",
            attr(ship, "close_to_home", False),
        ),
        DialogField("home_port", "Home port", "text", attr(ship, "home_port", "")),
        description_field(attr(record, "description", "")),
    ]


def ship_live(values: dict[str, Any]) -> str:
    """The Ship inspector: damage levels, crew, cargo left, artillery,
    stress checks and worth."""
    ship = ship_from(values)
    if ship.quality not in rules.BASE_DAMAGE_LEVELS:
        return ""
    whole = rules.damage_levels(ship)
    most = rules.artillery_limit(ship)
    pieces = rules.artillery(ship)
    rate = (
        "16 a quarter ton close to home"
        if ship.close_to_home
        else "8 a ton of cargo on a long voyage"
    )
    lines = [
        f"[b]Damage levels:[/] {rules.damage_left(ship)} of {whole} ({ship.quality} "
        f"{rules.BASE_DAMAGE_LEVELS[ship.quality]} x "
        f"{rules.damage_modifier(ship.size)} for size {ship.size:+d})",
        f"[b]Crew:[/] {rules.crew(ship)}"
        + (" (lateen: half again)" if ship.lateen else "")
        + (
            f" + {rules.fighting_men(ship)} fighting men ({rate})"
            if ship.fighters_tons
            else ""
        ),
        f"[b]Cargo left:[/] {rules.cargo_left(ship):g} of {ship.tons} tons",
        f"[b]Artillery:[/] {pieces} of at most {most} (one per 20 tons, a quarter "
        "ton each)" + (" [$text-error]too many[/]" if pieces > most else ""),
        f"[b]Stress checks:[/] {rules.QUALITY_STRESS[ship.quality]:+d} quality, "
        f"+{ship.magnitudes} enchantment, + the captain's Profession",
    ]
    bonus = rules.quality_bonus(ship)
    enchanting = rules.enchanting_modifier(ship)
    lines.append(
        f"[b]Quality:[/] +{bonus} to navigation and ship-handling; "
        f"{enchanting:+d} to Lab Totals enchanting her (C&G p. 70)"
    )
    cost = rules.book_cost(ship)
    worth = f"about {rules.guild_worth(ship)} pounds (" + (
        "a galley, 25 a ton, C&G p. 84)"
        if ship.galley
        else "4 pounds per 10 tons, C&G p. 85)"
    )
    if cost is not None:
        worth = f"{cost:g} pounds by HP's table (p. 54); {worth}"
    lines.append(f"[b]Worth:[/] {worth}")
    if ship.galley:
        lines.append("A galley: she can ram and back away, and shear oars.")
    return "\n".join(lines)


def ship_problem(values: dict[str, Any]) -> str | None:
    return rules.problem(ship_from(values))


def save_ship(
    covenant: Covenant, record: Possession | None, values: dict[str, Any]
) -> Possession:
    """Write the form's values: her name and description on the entry, the
    rest on her Ship. Fewer damage levels lost than before marks her
    repaired (-1 to stress checks, C&G p. 77)."""
    before = record.ship if record is not None else None
    ship = ship_from(values, before)
    if before is not None and ship.damage_lost < before.damage_lost:
        ship.repaired = True
    if record is None:
        record = Possession(
            id=storage.generate_unique_id(
                values.get("name") or "ship", [r.id for r in covenant.possessions]
            ),
            kind=rules.SHIP_KIND,
        )
        covenant.possessions.append(record)
    record.name = values.get("name") or ""
    record.description = values.get("description") or ""
    record.ship = ship
    return record


def ship_form(saga: Saga, covenant: Covenant, record: Possession | None) -> Form:
    """Add (`record` None) or edit one of the covenant's ships."""
    title = (
        "Add a Ship" if record is None else f"Edit {escape(record.name or 'this ship')}"
    )
    return Form(
        title,
        lambda: ship_fields(saga, covenant, record),
        lambda values: save_ship(covenant, record, values),
        validate=ship_problem,
        live=ship_live,
        inspector="The Ship",
    )


# -- the chosen ship --


def _chosen(covenant: Covenant, index: int) -> Possession | None:
    listed = rules.ships_of(covenant)
    return listed[index] if 0 <= index < len(listed) else None


# -- Sunk or Taken --

FATE_TITLE = "Sunk or Taken"
AFLOAT = "afloat"


def fate_fields(saga: Saga, covenant: Covenant, ship: Ship) -> list[DialogField]:
    others = [(escape(c.name), c.id) for c in saga.covenants if c is not covenant]
    return [
        DialogField(
            "fate",
            "What became of her",
            "select",
            ship.fate or AFLOAT,
            options=[("Still afloat, hers", AFLOAT), ("Sunk", SUNK), ("Taken", TAKEN)],
        ),
        DialogField(
            "by",
            "Taken by",
            "text",
            ship.fate_by,
            show_if=lambda v: v.get("fate") == TAKEN,
            placeholder="e.g. Eustace the Monk's pirates",
        ),
        DialogField(
            "captor",
            "To the covenant",
            "select",
            None,
            options=others,
            allow_blank=True,
            placeholder="(none of the saga's)",
            show_if=lambda v: v.get("fate") == TAKEN,
            hint="A covenant that took her: she moves to its Possessions.",
        ),
    ]


def mark_fate(saga: Saga, covenant: Covenant, index: int) -> Command:
    """More's Sunk or Taken on the chosen ship: what became of her in a
    fight or storm (Tales of Power pp. 109-110). A sunk or taken ship
    counts in no fleet; one taken by a covenant of the saga moves to its
    Possessions, afloat, and both Diaries say so."""
    record = _chosen(covenant, index)
    if record is None:
        return Refuse(FATE_TITLE, "Choose a ship first.")
    ship = rules.ship_of(record)

    def apply(values: dict[str, Any]) -> list[str]:
        fate = values.get("fate") or AFLOAT
        when = f"{saga.current_season} {saga.current_year}"
        captor = saga.covenant(values.get("captor")) if fate == TAKEN else None
        if fate == AFLOAT:
            ship.fate = ship.fate_by = ship.fate_when = ""
            record.ship = ship
            return notes(f"{escape(record.name)} is hers again.")
        if captor is not None:
            covenant.possessions.remove(record)
            captor.possessions.append(record)
            ship.fate = ship.fate_by = ship.fate_when = ""
            record.ship = ship
            text = f"{record.name} was taken by {captor.name}."
            diaries.write(
                saga.current_year,
                saga.current_season,
                record.name,
                text,
                covenants=[covenant, captor],
            )
            return notes(
                escape(text), f"She is now in {escape(captor.name)}'s Possessions."
            )
        ship.fate = fate
        ship.fate_by = (values.get("by") or "").strip() if fate == TAKEN else ""
        ship.fate_when = when
        record.ship = ship
        text = (
            f"{record.name} was {fate.lower()}"
            + (f" by {ship.fate_by}" if ship.fate_by else "")
            + "."
        )
        diaries.write(
            saga.current_year,
            saga.current_season,
            record.name,
            text,
            covenants=[covenant],
        )
        return notes(escape(text), "She counts in no fleet now.")

    return Form(
        f"{FATE_TITLE}: {escape(record.name)}",
        lambda: fate_fields(saga, covenant, ship),
        apply,
        help_id=SHIPS_HELP,
    )


# -- Stress Check --


def stress_fields(ship: Ship) -> list[DialogField]:
    return [
        DialogField(
            "event",
            "What happens",
            "select",
            "storm",
            options=[(words, key) for key, words in rules.EVENTS.items()],
        ),
        DialogField(
            "weather",
            "Weather",
            "select",
            "fair",
            options=[(words, key) for key, words in rules.WEATHER_WORDS.items()],
        ),
        DialogField("repaired", "Repaired before (-1)", "check", ship.repaired),
    ]


def stress_live(saga: Saga, record: Possession) -> Callable[[dict[str, Any]], str]:
    ship = rules.ship_of(record)
    captain = rules.captain(saga, ship)

    def live(values: dict[str, Any]) -> str:
        terms = rules.stress_terms(
            ship, captain, values.get("weather") or "fair", bool(values.get("repaired"))
        )
        total = rules.stress_total(terms)
        said = " ".join(
            f"{'+' if t.value >= 0 else '-'} {escape(t.words)} {abs(t.value)}"
            for t in terms
        )
        fails = equipment.STRESS_EASE - 1 - total
        lines = [
            f"stress die {said} = [b]{total:+d} + die[/] against "
            f"{equipment.STRESS_EASE}",
            (
                f"Fails on a die of {fails} or less: she loses a damage level "
                f"({ship_text.damage_words(ship)} now); a botch loses one more "
                "for each botch die that comes up."
                if fails >= 1
                else "Only a botch can harm her: one damage level, and one more "
                "for each botch die that comes up."
            ),
            "Her enchantments hold until every damage level is gone (HP p. 53).",
        ]
        return "\n".join(lines)

    return live


def stress_check(
    saga: Saga, covenant: Covenant, index: int, rng: random.Random | None = None
) -> Command:
    """More's Stress Check on the chosen ship."""
    record = _chosen(covenant, index)
    if record is None:
        return Refuse(STRESS_TITLE, "Choose a ship first.")
    ship = rules.ship_of(record)
    if rules.wrecked(ship):
        return Refuse(
            STRESS_TITLE,
            f"{escape(record.name)} is wrecked: she has no damage levels left.",
        )

    def apply(values: dict[str, Any]) -> list[str]:
        return roll_stress(saga, covenant, record, values, rng or random.Random())

    return Form(
        f"{STRESS_TITLE}: {escape(record.name)}",
        lambda: stress_fields(ship),
        apply,
        live=stress_live(saga, record),
        save_label="Roll",
        help_id=SHIPS_HELP,
        inspector="Weathering It",
    )


def roll_stress(
    saga: Saga,
    covenant: Covenant,
    record: Possession,
    values: dict[str, Any],
    rng: random.Random,
) -> list[str]:
    """Roll her stress check, take what it costs and write it in the
    covenant's Diary."""
    ship = rules.ship_of(record)
    repaired = bool(values.get("repaired"))
    ship.repaired = repaired
    terms = rules.stress_terms(
        ship, rules.captain(saga, ship), values.get("weather") or "fair", repaired
    )
    total = rules.stress_total(terms)
    die = dice.stress_die(rng, 1, saga=saga)
    lost = rules.take_damage(
        ship, rules.levels_lost(total, die.value, die.botches if die.botched else 0)
    )
    event = rules.EVENTS.get(values.get("event") or "", "A stress check")
    if die.botched:
        outcome = f"a botch ({die.botches}): she loses {lost} damage levels"
    elif lost:
        outcome = f"{total + die.value} against 15: she loses a damage level"
    else:
        outcome = f"{total + die.value} against 15: she comes through whole"
    left = ship_text.damage_words(ship)
    text = f"{event}: {outcome} ({left} left)."
    if rules.wrecked(ship):
        text += " She is wrecked, and any enchantment in her is lost."
    diaries.write(
        saga.current_year,
        saga.current_season,
        f"{STRESS_TITLE}: {record.name}",
        text,
        covenants=[covenant],
    )
    return notes(f"{STRESS_TITLE}: {escape(record.name)}.", escape(text))


# -- Ship Combat --


def _their_options(saga: Saga, record: Possession) -> list[tuple[str, str]]:
    """The saga's other ships, other covenants' first, then one typed in."""
    found = sorted(
        (
            (record in c.possessions, escape(f"{p.name} ({c.name})"), f"{c.id}/{p.id}")
            for c, p in rules.saga_ships(saga)
            if p is not record
        ),
        key=lambda option: option[0],
    )
    return [
        *((label, key) for _, label, key in found),
        ("Another: typed in below", TYPED),
    ]


def _their_ship(saga: Saga, key: str) -> tuple[Covenant, Possession] | None:
    return next(
        ((c, p) for c, p in rules.saga_ships(saga) if f"{c.id}/{p.id}" == key), None
    )


def _typed(values: dict[str, Any]) -> bool:
    return (values.get("theirs") or TYPED) == TYPED


def combat_fields(saga: Saga, record: Possession) -> list[DialogField]:
    ship = rules.ship_of(record)
    options = _their_options(saga, record)
    return [
        DialogField(
            "_ours",
            "Our ship",
            "info",
            f"{record.name} ({ship_text.captain_name(saga, ship)})",
        ),
        DialogField("theirs", "Their ship", "select", options[0][1], options=options),
        DialogField(
            "their_name",
            "Their ship's name",
            "text",
            "",
            show_if=_typed,
            placeholder="e.g. a Lübeck cog",
        ),
        DialogField("their_size", "Their size", "int", 5, show_if=_typed),
        DialogField(
            "their_captain",
            "Their captain's Int + Profession",
            "int",
            3,
            show_if=_typed,
        ),
        DialogField(
            "aim",
            "We mean to",
            "select",
            "board",
            options=[(words, key) for key, words in AIMS.items()],
        ),
        DialogField("crew_bonus", "Our crew's experience (0 to +3)", "int", 0),
        DialogField("their_bonus", "Their crew's experience (0 to +3)", "int", 0),
        DialogField(
            "conditions",
            "Weather and speed for us (+/-)",
            "int",
            0,
            hint="E.g. +1 a faster pirate ship; a fleeing merchant gets a bonus "
            "in fog (C&G p. 86).",
        ),
        DialogField(
            "rounds",
            "Rounds closing within range",
            "int",
            0,
            hint="A ballista reaches 600 yards, a light catapult 200; each "
            "reloads in ten rounds.",
        ),
    ]


class _Side:
    """One ship's side in the chase: its name, captain's modifiers and size."""

    def __init__(self, name: str, captain: str, base: int, size: int) -> None:
        self.name, self.captain, self.base, self.size = name, captain, base, size


def _sides(
    saga: Saga, record: Possession, values: dict[str, Any]
) -> tuple[_Side, _Side]:
    ship = rules.ship_of(record)
    captain = rules.captain(saga, ship)
    name, score = rules.profession(captain)
    intelligence = captain.characteristics.intelligence if captain else 0
    ours = _Side(
        record.name,
        f"{captain.name if captain else 'Our captain'}: Int {intelligence} + "
        f"{name} {score}",
        rules.captain_terms(
            intelligence,
            score,
            _int(values, "crew_bonus"),
            _int(values, "conditions"),
        ),
        ship.size,
    )
    found = None if _typed(values) else _their_ship(saga, values.get("theirs") or "")
    their_bonus = _int(values, "their_bonus")
    if found is None:
        typed = _int(values, "their_captain")
        theirs = _Side(
            values.get("their_name") or "Their ship",
            f"Their captain: Int + Profession {typed}",
            rules.captain_terms(0, typed, their_bonus, 0),
            _int(values, "their_size", 5),
        )
    else:
        other = rules.ship_of(found[1])
        them = rules.captain(saga, other)
        their_name, their_score = rules.profession(them)
        their_int = them.characteristics.intelligence if them else 0
        theirs = _Side(
            found[1].name,
            f"{them.name if them else 'Their captain'}: Int {their_int} + "
            f"{their_name} {their_score}",
            rules.captain_terms(their_int, their_score, their_bonus, 0),
            other.size,
        )
    return ours, theirs


def _softening(ship: Ship, rounds: int) -> str:
    shots = rules.shots(rounds)
    if not rules.artillery(ship):
        return "No artillery aboard to soften them as the ships close."
    if not shots:
        return "No rounds within range yet: give how many the ships close for."
    parts = []
    if ship.ballistae:
        parts.append(
            f"{ship.ballistae} ballista shooting {shots} time(s) each: a "
            "crewman killed a hit"
        )
    if ship.catapults:
        parts.append(
            f"{ship.catapults} light catapult shooting {shots} time(s) each: a "
            "simple die / 2 incapacitated a hit"
        )
    return "; ".join(parts) + ". Fired into a melee, it kills friend and foe alike."


def _win_words(aim: str, ship: Ship, ours: _Side, theirs: _Side) -> list[str]:
    taller = rules.taller(ours.size, theirs.size)
    height = {
        "ours": f"{escape(ours.name)}'s men get +3 Attack and Defense until boarded.",
        "theirs": f"{escape(theirs.name)}'s men get +3 Attack and Defense until "
        "boarded.",
        "": "Neither ship stands taller.",
    }[taller]
    if aim == "board":
        return [
            "[b]If we win:[/] we board. The crews fight as groups (DE pp. 395-396), "
            f"set up as a Fight; {height}",
            "[b]If they win:[/] they slip away.",
        ]
    if aim == "ram":
        lines = [
            "[b]If we win:[/] rammed soundly, she founders in 5 x a simple die minutes."
        ]
        if not ship.galley:
            lines.append(
                "[$text-warning]A sailing ship can't back away: we stay "
                "entangled, and may go down with her.[/]"
            )
        return [*lines, "[b]If they win:[/] they escape the ram."]
    if aim == "shear":
        return [
            "[b]If we win:[/] 2 x a simple die of their rowers incapacitated, and "
            "she can't make way until new oars are shipped.",
            "[b]If they win:[/] they escape it.",
        ]
    return [
        "[b]If we win:[/] we slip away.",
        f"[b]If they win:[/] they board us, set up as a Fight; {height}",
    ]


def combat_live(saga: Saga, record: Possession) -> Callable[[dict[str, Any]], str]:
    ship = rules.ship_of(record)

    def live(values: dict[str, Any]) -> str:
        ours, theirs = _sides(saga, record, values)
        aim = values.get("aim") or "board"
        return "\n".join(
            [
                f"[b]{escape(ours.name)}[/] ({escape(ours.captain)}, crew and "
                f"weather): [b]{ours.base:+d} + stress die[/]",
                f"[b]{escape(theirs.name)}[/] ({escape(theirs.captain)}, crew): "
                f"[b]{theirs.base:+d} + stress die[/]",
                "",
                f"[b]Softening:[/] {_softening(ship, _int(values, 'rounds'))}",
                *_win_words(aim, ship, ours, theirs),
                "[dim]City & Guild pp. 86-87.[/]",
            ]
        )

    return live


def combat_problem(record: Possession) -> Callable[[dict[str, Any]], str | None]:
    ship = rules.ship_of(record)

    def problem(values: dict[str, Any]) -> str | None:
        if values.get("aim") == "shear" and not ship.galley:
            return "Only a galley can shear oars (C&G p. 86)."
        for key in ("crew_bonus", "their_bonus"):
            if not 0 <= _int(values, key) <= rules.MOST_CREW_BONUS:
                return "A crew's experience is 0 to +3 (C&G p. 86)."
        if _int(values, "rounds") < 0:
            return "Rounds can't be negative."
        return None

    return problem


def ship_combat(
    saga: Saga, covenant: Covenant, index: int, rng: random.Random | None = None
) -> Command:
    """More's Ship Combat for the chosen ship."""
    record = _chosen(covenant, index)
    if record is None:
        return Refuse(COMBAT_TITLE, "Choose a ship first.")
    if rules.wrecked(rules.ship_of(record)):
        return Refuse(
            COMBAT_TITLE, f"{escape(record.name)} is wrecked and can't give chase."
        )

    def apply(values: dict[str, Any]) -> list[str]:
        return roll_combat(saga, covenant, record, values, rng or random.Random())

    return Form(
        f"{COMBAT_TITLE}: {escape(record.name)}",
        lambda: combat_fields(saga, record),
        apply,
        validate=combat_problem(record),
        live=combat_live(saga, record),
        save_label="Roll",
        help_id=SHIPS_HELP,
        inspector="The Chase",
    )


def _total(base: int, die: dice.DieResult) -> int:
    return dice.Roll(base, die).total


def roll_combat(
    saga: Saga,
    covenant: Covenant,
    record: Possession,
    values: dict[str, Any],
    rng: random.Random,
) -> list[str]:
    """Roll the two captains against each other, say what came of it,
    set up a Fight when one crew boards the other, and write it in the
    covenant's Diary."""
    ship = rules.ship_of(record)
    ours, theirs = _sides(saga, record, values)
    aim = values.get("aim") or "board"
    our_die = dice.stress_die(rng, 1, saga=saga)
    their_die = dice.stress_die(rng, 1, saga=saga)
    our_total, their_total = _total(ours.base, our_die), _total(theirs.base, their_die)
    rolled = (
        f"{ours.name} {our_total}"
        + (" (botched)" if our_die.botched else "")
        + f" against {theirs.name} {their_total}"
        + (" (botched)" if their_die.botched else "")
    )
    lines: list[str] = []
    boarding = False
    if our_total == their_total:
        lines.append("Neither captain gains the advantage: the chase goes on.")
    elif our_total > their_total:
        if aim == "board":
            boarding = True
            lines.append(f"{ours.name} closes and boards {theirs.name}.")
        elif aim == "ram":
            minutes = rules.founder_minutes(dice.simple_die(rng))
            lines.append(
                f"{theirs.name} is rammed soundly: she founders in {minutes} minutes."
            )
            if not ship.galley:
                lines.append(f"{ours.name} can't back away: she is entangled with her.")
        elif aim == "shear":
            rowers = rules.sheared_rowers(dice.simple_die(rng))
            lines.append(
                f"{theirs.name}'s oars are sheared: {rowers} rowers incapacitated, "
                "and she makes no way until new oars are shipped."
            )
        else:
            lines.append(f"{ours.name} slips away.")
    elif aim == "escape":
        boarding = True
        lines.append(f"{theirs.name} closes and boards {ours.name}.")
    elif aim == "board":
        lines.append(f"{theirs.name} slips away.")
    else:
        lines.append(f"{theirs.name} escapes damage.")
    if boarding:
        taller = rules.taller(ours.size, theirs.size)
        fight = Fight(
            f"Boarding: {ours.name} and {theirs.name}",
            place="At sea",
            year=saga.current_year,
            season=saga.current_season,
            sides=[
                FightSide(name=f"{ours.name}'s crew", covenant_id=covenant.id),
                FightSide(name=f"{theirs.name}'s crew"),
            ],
        )
        saga.fights.append(fight)
        lines.append(
            f"A Fight, {fight.name}, is set up in Conflicts: add the two crews "
            "as groups (DE pp. 395-396)."
            + (
                f" {(ours if taller == 'ours' else theirs).name}'s men have +3 "
                "Attack and Defense until they are boarded (C&G p. 86)."
                if taller
                else ""
            )
        )
    text = f"{rolled}. " + " ".join(lines)
    diaries.write(
        saga.current_year,
        saga.current_season,
        f"{COMBAT_TITLE}: {record.name}",
        text,
        covenants=[covenant],
    )
    return notes(
        f"{COMBAT_TITLE}: {escape(record.name)}.",
        escape(rolled) + ".",
        *map(escape, lines),
    )
