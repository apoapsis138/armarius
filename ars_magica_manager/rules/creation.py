"""Creation checks: the public face of rules.creation_base
(Check, the step lists and registries, checks(), can_move_to_play()),
with every step's checks registered. Import this, not the step modules.
"""

from __future__ import annotations

from . import (  # noqa: F401 -- each registers its step's checks
    creation_animal,
    creation_character,
    creation_characteristics,
    creation_companion,
    creation_covenant,
    creation_finish,
    creation_later,
    creation_magus,
    creation_packages,
    creation_tradition,
    creation_virtues,
    creation_xp,
)
from .creation_base import (
    CHARACTER_CHECKS,
    CHARACTER_STEPS,
    COVENANT_CHECKS,
    COVENANT_STEPS,
    LABORATORY_CHECKS,
    LABORATORY_STEPS,
    SOURCE,
    Check,
    CheckFn,
    Record,
    Status,
    Step,
    StepStatus,
    broken_musts,
    can_move_to_play,
    check,
    checks,
    step_status,
    steps_for,
    strict,
    summary,
)

__all__ = [
    "CHARACTER_CHECKS",
    "CHARACTER_STEPS",
    "COVENANT_CHECKS",
    "COVENANT_STEPS",
    "LABORATORY_CHECKS",
    "LABORATORY_STEPS",
    "SOURCE",
    "Check",
    "CheckFn",
    "Record",
    "Status",
    "Step",
    "StepStatus",
    "broken_musts",
    "can_move_to_play",
    "check",
    "checks",
    "step_status",
    "steps_for",
    "strict",
    "summary",
]
