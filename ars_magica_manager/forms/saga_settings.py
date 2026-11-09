"""What Saga Settings' cards do: a switch flips its setting at once, as a
book's does on Books in Play, and a setting chosen from a list asks.
"""

from __future__ import annotations

from typing import Any

from .. import medallions, ruling_templates
from ..commands import Act, Form
from ..form_spec import DialogField
from ..models import Saga
from ..rules import options as rule_options
from ..seasons import defaults
from ..sheets import saga_settings as sss


def toggle_setting(saga: Saga, key: str) -> Act:
    """Turn a saga flag or an optional rule on or off."""

    def apply() -> None:
        if key in sss.SAGA_FLAGS:
            setattr(saga, key, not getattr(saga, key))
        else:
            saga.rule_options = rule_options.normalized(
                {**saga.rule_options, key: not saga.rule_options.get(key, False)}
            )

    return Act(apply)


def _setter(saga: Saga, key: str) -> Any:
    return lambda values: setattr(saga, key, values[key])


def choice_form(saga: Saga, key: str) -> Form:
    """The form that changes a setting chosen from a list."""
    if key == sss.RULING_TEMPLATES:
        return Form(
            "Ruling Templates",
            lambda: [ruling_templates.saga_field(saga)],
            _setter(saga, key),
        )
    if key == sss.STORY_FLAW_YEARS:
        return Form(
            "Story Flaw Spotlight",
            lambda: [
                DialogField(
                    key,
                    "Years",
                    "int",
                    saga.story_flaw_years,
                    hint="How long a Story or Major Personality Flaw may wait for "
                    "a story before Needs You names it; 0 turns it off.",
                )
            ],
            _setter(saga, key),
            validate=lambda values: (
                "The span is 0 or more years." if (values.get(key) or 0) < 0 else None
            ),
        )
    if key == sss.MEDALLIONS:
        title, value, options = (
            "Medallion Style",
            medallions.chosen(saga),
            medallions.options(),
        )
    else:
        title = dict(sss.UNPLANNED)[key]
        value, options = getattr(saga, key), defaults.OPTIONS
    return Form(
        title,
        lambda: [DialogField(key, title, "select", value, options=options)],
        _setter(saga, key),
    )
