"""The covenant sheet's Build tab: what the covenant's Build
Points went on, row by row, as it started (Initial) and as it stands now
(Current). Build Points are spent at covenant creation and don't matter in
play, so this tab is the one place they show; it keeps a covenant's value
on record (for an exported covenant, say).

- In Creation: the two columns are the same, and Current is checked
  against the storyguide's Build Points on the Creation Worksheet.
- Moving to In Play keeps the Initial figures (Covenant.
  initial_build_points); Current goes on following what the covenant owns,
  counting every laboratory, not just its starting ones.
"""

from __future__ import annotations

from .markup import escape, fit
from .models import Covenant, Saga
from .rules import creation_covenant as cov

_NAME, _NUMBER = 20, 9


def current_costs(saga: Saga, covenant: Covenant) -> list[cov.Cost]:
    """What the covenant's resources are worth now (in play: every
    laboratory counts, not just the starting ones)."""
    return cov.costs(saga, covenant, every_lab=not covenant.in_creation)


def title(saga: Saga, covenant: Covenant) -> str:
    """The section's title: "Build Points (296 of 600)" In Creation, else
    its current value."""
    total = sum(c.points for c in current_costs(saga, covenant))
    budget = covenant.build_points_budget
    if covenant.in_creation and budget is not None:
        return f"Build Points ({total} of {budget})"
    return f"Build Points ({total})"


def summary(saga: Saga, covenant: Covenant) -> str:
    """ "296/600" (or "296") for the covenant's top panel In Creation; kept
    short, as the panel's columns are narrow at 120 wide."""
    total = sum(c.points for c in current_costs(saga, covenant))
    budget = covenant.build_points_budget
    return f"{total}/{budget}" if budget is not None else f"{total}"


def _row(name: str, initial: str, current: str) -> str:
    return f"{fit(name, _NAME)}{initial:>{_NUMBER}}{current:>{_NUMBER}}"


def table_text(saga: Saga, covenant: Covenant) -> str:
    """The Build tab's table (markup): a row per kind of resource, a total,
    then the Power Level and the storyguide's Build Points."""
    current = cov.category_totals(current_costs(saga, covenant))
    initial = current if covenant.in_creation else covenant.initial_build_points
    lines = [f"[b]{_row('', 'Initial', 'Current')}[/]"]
    for name in cov.CATEGORIES:
        first = "-" if initial is None else str(initial.get(name, 0))
        lines.append(_row(name, first, str(current[name])))
    total = "-" if initial is None else str(sum(initial.values()))
    lines.append(f"[b]{_row('Total', total, str(sum(current.values())))}[/]")
    lines.append("")
    power = cov.POWER_BY_NAME.get(covenant.power_level)
    budget = covenant.build_points_budget
    lines.append(
        "Power Level: "
        + (f"{power.name} ({cov.band(power)} Build Points)" if power else "(not set)")
    )
    lines.append(
        "Storyguide's Build Points: "
        + (str(budget) if budget is not None else "(not set)")
    )
    if covenant.in_creation:
        lines.append(
            "[dim]In Creation: Initial follows Current until the covenant moves "
            "to In Play.[/]"
        )
    elif initial is None:
        lines.append(
            "[dim]Initial wasn't recorded: this covenant was in play before "
            "Build Points were tracked.[/]"
        )
    return "\n".join(lines)


#: What a line's label starts with that its row's heading already says.
_PREFIXES = (
    "Art Summa: ",
    "Ability Summa: ",
    "Tractatus: ",
    "Lab Text: ",
    "Casting Tablet: ",
    "Vis source: ",
    "Vis stock: ",
    "Enchanted: ",
    "Laboratory: ",
    "Specialist: ",
)


def _short(label: str) -> str:
    for prefix in _PREFIXES:
        if label.startswith(prefix):
            return label.removeprefix(prefix)
    return label


def items_text(saga: Saga, covenant: Covenant) -> str:
    """Every priced resource under its row's name (markup)."""
    found = current_costs(saga, covenant)
    if not found:
        return "[dim](nothing priced yet)[/]"
    lines = []
    for name in cov.CATEGORIES:
        rows = [c for c in found if c.category == name]
        if not rows:
            continue
        lines.append(f"[b]{name}[/]")
        lines += [f"  {escape(_short(c.label))}: {c.points}" for c in rows]
    return "\n".join(lines)
