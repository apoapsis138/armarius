"""Creation checks, the machinery: what the book asks of a covenant,
laboratory or character being created, as lines marked pass, warn (a book
"must") or advice (a book "should": what the record has too many or too
few of), each citing its source.

Checks run only while a record is In Creation. They never block an edit;
with the saga's "Enforce creation rules strictly" option on, a broken must
stops the record moving to In Play (see can_move_to_play). Advice never
blocks.

Each creation step adds its checks to the step's list below; the Creation
Worksheet shows a step's checks beside its budget.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Literal

from ..models import FULL, Character, Covenant, Laboratory, Saga
from . import options

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Detailed "
    "Character Creation Summary (https://www.redcap.org/page/Ars_Magica_"
    "Definitive_Edition,_Chapter_Three:_Characters#Detailed_Character_"
    "Creation_Summary)"
)

Status = Literal["pass", "warn", "advice"]
Record = Character | Covenant | Laboratory


@dataclass(frozen=True)
class Check:
    """One creation rule applied to a record."""

    #: The worksheet step it belongs to (a Step key).
    step: str
    #: The rule, e.g. "Virtues balance Flaws".
    label: str
    #: pass; warn (a must is broken); advice (a should is not met).
    status: Status
    #: What the record has, e.g. "3 Virtue points, 2 Flaw points".
    detail: str
    #: The rule's citation.
    source: str


@dataclass(frozen=True)
class Step:
    """A step of the Creation Worksheet."""

    key: str
    title: str
    #: Whether this record goes through the step (e.g. Apprenticeship is
    #: for magi only).
    applies: Callable[[Record], bool] = lambda record: True


def _magus(record: Record) -> bool:
    return isinstance(record, Character) and record.type == "magus"


CHARACTER_STEPS: tuple[Step, ...] = (
    Step("concept", "Concept"),
    Step("virtues_flaws", "Virtues and Flaws"),
    Step("characteristics", "Characteristics"),
    Step("childhood", "Early Childhood"),
    Step("later_life", "Later Life"),
    Step("apprenticeship", "Apprenticeship", _magus),
    Step("gauntlet", "Years past Gauntlet", _magus),
    Step("finish", "Finishing Touches"),
)
COVENANT_STEPS: tuple[Step, ...] = (
    Step("power", "Baseline"),
    Step("build_points", "Resources"),
    Step("boons_hooks", "Boons & Hooks"),
    Step("finish", "Review"),
)
LABORATORY_STEPS: tuple[Step, ...] = (
    Step("setup", "Setting Up"),
    Step("finish", "Review"),
)

CheckFn = Callable[[Saga, Record], list[Check]]

#: Each step's checks, in the order shown; each step registers its own.
CHARACTER_CHECKS: dict[str, list[CheckFn]] = {s.key: [] for s in CHARACTER_STEPS}
COVENANT_CHECKS: dict[str, list[CheckFn]] = {s.key: [] for s in COVENANT_STEPS}
LABORATORY_CHECKS: dict[str, list[CheckFn]] = {s.key: [] for s in LABORATORY_STEPS}


def check(
    step: str, registry: dict[str, list[CheckFn]]
) -> Callable[[CheckFn], CheckFn]:
    """Register a check function for `step` in `registry`."""

    def register(fn: CheckFn) -> CheckFn:
        registry[step].append(fn)
        return fn

    return register


def steps_for(record: Record) -> tuple[Step, ...]:
    """The worksheet steps this record goes through, in order."""
    if isinstance(record, Character):
        steps = CHARACTER_STEPS
    elif isinstance(record, Covenant):
        steps = COVENANT_STEPS
    else:
        steps = LABORATORY_STEPS
    return tuple(step for step in steps if step.applies(record))


def _registry(record: Record) -> dict[str, list[CheckFn]]:
    if isinstance(record, Character):
        return CHARACTER_CHECKS
    if isinstance(record, Covenant):
        return COVENANT_CHECKS
    return LABORATORY_CHECKS


def checks(saga: Saga, record: Record, step: str | None = None) -> list[Check]:
    """Every creation check for `record` (only `step`'s, if given), in
    worksheet order; none once it is In Play, nor for a sketch, which no
    budget applies to."""
    if not record.in_creation or getattr(record, "detail", FULL) != FULL:
        return []
    registry = _registry(record)
    keys = [s.key for s in steps_for(record)]
    result: list[Check] = []
    for key in keys if step is None else [step]:
        for fn in registry.get(key, ()):
            result.extend(fn(saga, record))
    return result


def broken_musts(found: Sequence[Check]) -> list[Check]:
    return [c for c in found if c.status == "warn"]


def strict(saga: Saga) -> bool:
    """Whether the saga enforces creation rules strictly."""
    return options.is_on(saga, "strict_creation")


def can_move_to_play(saga: Saga, record: Record) -> bool:
    """Whether `record` may move to In Play: always, unless the saga is
    strict and a must is broken."""
    return not (strict(saga) and broken_musts(checks(saga, record)))


def summary(found: Sequence[Check]) -> str:
    """ "2 warnings, 1 advice" -- or "all checks pass" ("no checks yet" for
    none)."""
    if not found:
        return "no checks yet"
    warns = sum(c.status == "warn" for c in found)
    advice = sum(c.status == "advice" for c in found)
    parts = []
    if warns:
        parts.append(f"{warns} warning{'s' if warns != 1 else ''}")
    if advice:
        parts.append(f"{advice} advice")
    return ", ".join(parts) or "all checks pass"


StepStatus = Literal["pass", "warn", "advice", "none"]


def step_status(found: Sequence[Check]) -> StepStatus:
    """A step's mark on the worksheet's progress list: warn if any must is
    broken, else advice if any should is unmet, else pass; "none" for a
    step with no checks."""
    if not found:
        return "none"
    if any(c.status == "warn" for c in found):
        return "warn"
    if any(c.status == "advice" for c in found):
        return "advice"
    return "pass"
