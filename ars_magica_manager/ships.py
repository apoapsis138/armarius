"""Logic behind the Ships list on a covenant's Possessions -- no UI in
here: each ship's row, her details and her card. The rules are
rules.ships' (Hermetic Projects pp. 53-54, 63; City & Guild pp. 77,
84-87); the forms are forms.ships'.
"""

from __future__ import annotations

from dataclasses import dataclass

from .markup import escape, fit
from .models import Possession, Saga
from .models.ships import Ship
from .rules import equipment, journeys
from .rules import ships as rules

_NAME = 18
_KIND = 22
_CARGO = 8
_CREW = 6
_QUALITY = 12
_DAMAGE = 10

#: The colour of her damage, by rules.condition.
TONES: dict[str, str] = {
    "whole": "text-success",
    "damaged": "text-warning",
    "badly": "text-error",
}
#: The river types, which keep to a barge's speed.
RIVER_TYPES = ("ferry", "lighter", "river_barge")
NO_CAPTAIN = "(none)"


def kind_words(ship: Ship) -> str:
    """ "Large merchant cog +7": what she is, and her size."""
    return f"{ship.kind_name or 'Ship'} {ship.size:+d}"


def captain_name(saga: Saga | None, ship: Ship) -> str:
    found = rules.captain(saga, ship) if saga is not None else None
    return found.name if found is not None else NO_CAPTAIN


def damage_words(ship: Ship) -> str:
    """ "7 of 9": damage levels left of whole."""
    return f"{rules.damage_left(ship)} of {rules.damage_levels(ship)}"


def damage_markup(ship: Ship) -> str:
    return f"[${TONES[rules.condition(ship)]}]{damage_words(ship)}[/]"


def crew_words(ship: Ship) -> str:
    """ "18 + 48 fighting men"."""
    men = rules.fighting_men(ship)
    return f"{rules.crew(ship)}" + (f" + {men} fighting men" if men else "")


def table_header() -> str:
    """The Ships list's column titles (after the selector marker)."""
    return (
        f"  {'Ship':<{_NAME}}{'Kind':<{_KIND}}{'Cargo':<{_CARGO}}"
        f"{'Crew':<{_CREW}}{'Quality':<{_QUALITY}}{'Damage':<{_DAMAGE}}Captain"
    )


def row_label(record: Possession, saga: Saga | None) -> str:
    """One row of the Ships list (markup), lined up with table_header."""
    ship = rules.ship_of(record)
    damage = damage_words(ship)
    padding = " " * max(0, _DAMAGE - len(damage))
    return (
        f"{escape(fit(record.name or '(unnamed)', _NAME))}"
        f"{escape(fit(kind_words(ship), _KIND))}"
        f"{fit(f'{ship.tons} t', _CARGO)}"
        f"{fit(str(rules.crew(ship)), _CREW)}"
        f"{fit(ship.quality, _QUALITY)}"
        f"{damage_markup(ship)}{padding}"
        f"{escape(captain_name(saga, ship))}"
    ).rstrip()


def _line(label: str, value: str) -> str:
    """A labelled line; `value` is markup already."""
    return f"[b]{label}:[/] {value}"


def _quarter(tons: float) -> str:
    return f"{tons:g}"


def detail_lines(record: Possession, saga: Saga | None) -> list[str]:
    """Her details panel / inspector, after her name: kind and quality,
    cargo, crew and captain, damage levels, what her cargo carries, her
    enchantment, quality bonus and speed, and the stress check."""
    ship = rules.ship_of(record)
    lines = [
        f"{escape(ship.kind_name or 'Ship')}, size {ship.size:+d}  ·  {ship.quality}"
        + ("  ·  a galley" if ship.galley else "")
        + ("  ·  lateen-rigged" if ship.lateen else ""),
        f"{_line('Cargo', f'{ship.tons} tons')}  ·  "
        f"{_line('Crew', crew_words(ship))}  ·  "
        f"{_line('Captain', escape(captain_name(saga, ship)))}",
        _line(
            "Damage levels",
            f"{damage_markup(ship)} ({ship.quality} "
            f"{rules.BASE_DAMAGE_LEVELS[ship.quality]} x size "
            f"{rules.damage_modifier(ship.size)})"
            + (", repaired before" if ship.repaired else ""),
        ),
    ]
    if rules.wrecked(ship):
        lines.append(
            "[$text-error]Wrecked: every damage level lost, and any enchantment "
            "in her with them (HP p. 65).[/]"
        )
    taken = _taken_from_cargo(ship)
    if taken:
        lines.append(_line("Taken from cargo", taken))
    if ship.magnitudes:
        lines.append(
            _line(
                "Enchanted",
                f"{ship.magnitudes} magnitudes invested: +{ship.magnitudes} to "
                "stress checks.",
            )
        )
    bonus = rules.quality_bonus(ship)
    if bonus:
        extra = (
            ", and to Lab Totals enchanting her"
            if ship.quality == equipment.EXCELLENT
            else ""
        )
        lines.append(
            _line(
                "Quality",
                f"+{bonus} to navigation and ship-handling rolls{extra} (HP p. 63).",
            )
        )
    lines.append(_line("Speed", _speed(ship)))
    if ship.home_port:
        lines.append(_line("Home port", escape(ship.home_port)))
    return lines


def _taken_from_cargo(ship: Ship) -> str:
    parts: list[str] = []
    if ship.fighters_tons:
        rate = (
            "16 a quarter ton close to home"
            if ship.close_to_home
            else "8 a ton on a long voyage"
        )
        parts.append(
            f"{_quarter(ship.fighters_tons)} tons for {rules.fighting_men(ship)} "
            f"fighting men ({rate}, C&G p. 87)"
        )
    if rules.artillery(ship):
        pieces = []
        if ship.ballistae:
            pieces.append(
                f"{ship.ballistae} ballista" + ("e" if ship.ballistae > 1 else "")
            )
        if ship.catapults:
            pieces.append(
                f"{ship.catapults} light catapult" + ("s" if ship.catapults > 1 else "")
            )
        parts.append(
            f"{' and '.join(pieces)} (a quarter ton each; up to "
            f"{rules.artillery_limit(ship)} on {ship.tons} tons, C&G p. 86)"
        )
    return "; ".join(parts) + ("." if parts else "")


def _speed(ship: Ship) -> str:
    if ship.ship_type in RIVER_TYPES:
        barge = journeys.MEANS["barge_down"]
        return f"a river barge's 8 to 10 miles a day ({barge.speed_source})."
    sea = journeys.MEANS["ship"]
    low, high = sea.speed
    slower = ", slower for her size" if ship.size >= 8 else ""
    return (
        f"{low} to {high} miles a day{slower} ({sea.speed_source}); about "
        f"{sea.guide} by the Definitive Edition (p. 408)."
    )


STRESS_NOTE = (
    "[dim]A stress check (storm, fire, combat, magic): stress die + the "
    "captain's Profession + quality + an enchanted ship's magnitudes, "
    "against 15; failure loses a damage level, a botch one more per botch "
    "(C&G p. 77; HP p. 53).[/]"
)


def detail_text(record: Possession, saga: Saga | None) -> str:
    """The whole details panel (markup): her name, details, the
    description, and how a stress check goes."""
    first, *rest = detail_lines(record, saga)
    lines = [f"[b]{escape(record.name or '(unnamed)')}[/]  ·  {first}", *rest]
    if record.description.strip():
        lines += ["", f"[i]{escape(record.description.strip())}[/]"]
    lines.append(STRESS_NOTE)
    return "\n".join(lines)


@dataclass(frozen=True)
class Card:
    """A ship as the desktop's ledger entry shows her."""

    title: str
    meta: str
    badge: str
    tone: str  # a palette key
    body: str
    note: str


def card(record: Possession, saga: Saga | None) -> Card:
    ship = rules.ship_of(record)
    return Card(
        title=record.name or "(unnamed)",
        meta=f"{ship.kind_name or 'Ship'}, size {ship.size:+d}, {ship.tons} tons",
        badge=f"{damage_words(ship)} damage",
        tone=TONES[rules.condition(ship)],
        body=(
            f"{ship.quality}; crew {crew_words(ship)}; captain "
            f"{captain_name(saga, ship)}."
        ),
        note=record.description.strip(),
    )


def subtitle(record: Possession) -> str:
    """The inspector's line under her name."""
    ship = rules.ship_of(record)
    return f"{ship.kind_name or 'Ship'}, size {ship.size:+d}  ·  {ship.quality}"


def table_cells(record: Possession, saga: Saga | None) -> list[str]:
    """Her row as plain cells after the name, for the sheet as a table."""
    ship = rules.ship_of(record)
    return [
        kind_words(ship),
        f"{ship.tons} t",
        str(rules.crew(ship)),
        ship.quality,
        damage_words(ship),
        captain_name(saga, ship),
    ]


TABLE_TITLES = ("Kind", "Cargo", "Crew", "Quality", "Damage", "Captain")
