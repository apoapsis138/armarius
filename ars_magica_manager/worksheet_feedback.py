"""What the Creation Worksheet tells you as you go, for a front-end to draw:
each step's budgets as meters (spent of how much), one ledger of the
experience every step has put into each Ability and Art with its total and
score, and the creation rules that are broken anywhere, each naming the
step that fixes it.

The ledger reads Character.creation_xp, the record every step's spending
already writes, so a stage sees what the others put in without asking them.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from . import catalog, creation
from .arts import ARTS
from .forms.worksheet import Record
from .markup import escape
from .models import Character, Covenant, Saga
from .rules import creation as rules
from .rules import creation_access as access
from .rules import creation_characteristics as cch
from .rules import creation_covenant as cov
from .rules import creation_later as later
from .rules import creation_magus as magus
from .rules import creation_tradition as ct
from .rules import creation_xp as cx
from .tables import Table
from .worksheet import ENTRY_STEPS, target_score


@dataclass(frozen=True)
class Meter:
    """A budget as a bar: what it is, how much is spent of how much."""

    label: str
    spent: int
    total: int
    unit: str = "xp"

    @property
    def left(self) -> int:
        return self.total - self.spent

    @property
    def over(self) -> bool:
        return self.spent > self.total

    def words(self) -> str:
        """ "30 of 45 xp, 15 left" (or "5 over")."""
        rest = f"{-self.left} over" if self.over else f"{self.left} left"
        return f"{self.spent} of {self.total} {self.unit}, {rest}"


def _childhood(saga: Saga, character: Character) -> list[Meter]:
    native = sum(
        x.xp for x in cx.entries(character, "childhood") if x.note == cx.NATIVE
    )
    others = cx.spent(character, "childhood") - native
    return [
        Meter("Native Language", native, cx.NATIVE_XP),
        Meter("Other childhood xp", others, cx.CHILDHOOD_XP),
    ]


def _later_life(saga: Saga, character: Character) -> list[Meter]:
    meters = [
        Meter(
            "Later Life",
            cx.spent(character, "later_life"),
            later.later_life_budget(saga, character),
        )
    ]
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    for vf_id, rule in access.virtue_xp(character).items():
        meters.append(
            Meter(by_id[vf_id].name, cx.spent(character, "virtue", note=vf_id), rule.xp)
        )
    return meters


def _apprenticeship(saga: Saga, character: Character) -> list[Meter]:
    return [
        Meter(
            "Arts and Abilities",
            cx.spent(character, "apprenticeship"),
            magus.xp_budget(character),
        ),
        Meter(
            "Spell levels",
            cx.spent(character, magus.SPELLS_STEP),
            magus.level_budget(character),
            "levels",
        ),
    ]


def _training(saga: Saga, character: Character) -> list[Meter]:
    meters = []
    if budget := ct.xp_budget(character):
        meters.append(Meter("Arts and Abilities", cx.spent(character, ct.STEP), budget))
    return meters


def _gauntlet(saga: Saga, character: Character) -> list[Meter]:
    return [
        Meter(
            "Points past Gauntlet",
            magus.gauntlet_spent(character),
            magus.gauntlet_points(saga, character),
            "points",
        )
    ]


def _characteristics(saga: Saga, character: Character) -> list[Meter]:
    spent = sum(line.cost for line in cch.lines(saga, character))
    return [Meter("Characteristic points", spent, cch.budget(character), "points")]


def _build_points(saga: Saga, covenant: Covenant) -> list[Meter]:
    budget = covenant.build_points_budget
    if budget is None:
        return []
    return [Meter("Build Points", cov.spent(saga, covenant), budget, "points")]


#: Each step's meters, by record kind and step key.
_CHARACTER_METERS: dict[str, Callable[[Saga, Character], list[Meter]]] = {
    "characteristics": _characteristics,
    "childhood": _childhood,
    "later_life": _later_life,
    "training": _training,
    "apprenticeship": _apprenticeship,
    "gauntlet": _gauntlet,
}

#: The steps whose own list spends xp: each shows the ledger.
XP_STAGES = frozenset(
    {"childhood", "later_life", "training", "apprenticeship", "gauntlet"}
)


def meters(saga: Saga, record: Record, step: str) -> list[Meter]:
    """The step's budgets, as meters (none for a step without one)."""
    if isinstance(record, Character):
        found = _CHARACTER_METERS.get(step)
        return found(saga, record) if found is not None else []
    if isinstance(record, Covenant) and step == "build_points":
        return _build_points(saga, record)
    return []


def _ledger_order(character: Character, target: str) -> tuple[int, int, str]:
    """Abilities by name, then the Arts in the book's order."""
    if target in ARTS:
        return (1, ARTS.index(target), target)
    return (0, 0, target)


def ledger(character: Character, step: str) -> Table:
    """Every Ability and Art the worksheet has put xp into: a column of
    the xp each stage put in (this `step`'s first and in bold), then the
    total it came to and the score it buys."""
    entries = [x for x in character.creation_xp if x.step in ENTRY_STEPS]
    used = [s for s in ENTRY_STEPS if any(x.step == s for x in entries)]
    stages = ([step] if step in used else []) + [s for s in used if s != step]
    targets = sorted(
        {x.target for x in entries}, key=lambda t: _ledger_order(character, t)
    )
    rows = []
    for target in targets:
        cells = [escape(target)]
        for stage in stages:
            xp = sum(
                creation.gained_xp(x)
                for x in entries
                if x.target == target and x.step == stage
            )
            text = str(xp) if xp else ""
            cells.append(f"[b]{text}[/]" if stage == step and text else text)
        progress, _specialty = target_score(character, target)
        cells += [str(progress.total), str(progress.score)]
        rows.append(cells)
    columns = ["Ability or Art", *(ENTRY_STEPS[s] for s in stages), "Total xp", "Score"]
    return Table(columns, rows, markup=True)


def shows_ledger(record: Record, step: str) -> bool:
    return isinstance(record, Character) and step in XP_STAGES


@dataclass(frozen=True)
class Broken:
    """A creation rule that must hold and doesn't, with the step to fix it
    on."""

    step: str
    step_title: str
    label: str
    detail: str

    def words(self) -> str:
        return f"{self.step_title}: {self.label} ({self.detail})"


def broken(saga: Saga, record: Record) -> list[Broken]:
    """Every rule broken anywhere on the worksheet, in step order (the
    shoulds that are only advice are left to their steps)."""
    titles = {s.key: s.title for s in rules.steps_for(record)}
    return [
        Broken(c.step, titles.get(c.step, c.step), c.label, c.detail)
        for c in rules.checks(saga, record)
        if c.status == "warn"
    ]
