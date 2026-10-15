"""The forms for a Tribunal (New and Edit Tribunal, and deleting one),
and the choice of Tribunal a covenant's forms share. Each is a list of
form_spec.DialogFields inside a commands step, so either front-end draws
it."""

from __future__ import annotations

from typing import Any

from . import tribunals
from .commands import Form
from .form_spec import DialogField, pairs
from .markup import escape
from .models import SEASONS, Saga, Tribunal


def tribunal_field(saga: Saga, tribunal_id: str | None) -> DialogField:
    """A covenant's choice of Tribunal, from the saga's."""
    return DialogField(
        "tribunal_id",
        "Tribunal",
        "select",
        tribunal_id,
        options=[(escape(label), ident) for label, ident in tribunals.options(saga)],
        allow_blank=True,
        placeholder="(no Tribunal)",
        hint="New Tribunal, in the New menu, adds one to choose."
        if not saga.tribunals
        else "",
    )


def _character_options(saga: Saga) -> list[tuple[str, str]]:
    return [(escape(c.name), c.id) for c in saga.characters]


def tribunal_fields(saga: Saga, tribunal: Tribunal | None) -> list[DialogField]:
    """New or Edit Tribunal: its name, when and where it next meets, its
    officers and how big it really is."""
    t = tribunal or Tribunal(id="", name="")
    officer = {"allow_blank": True, "placeholder": "(none chosen)"}
    return [
        DialogField("name", "Name", "text", t.name, required=True),
        DialogField(
            "summary",
            "In the Saga",
            "area",
            t.summary,
            hint="A sentence or a paragraph: what the Tribunal is like.",
        ),
        DialogField(
            "meets_every",
            "Meets every (years)",
            "int",
            t.meets_every,
        ),
        DialogField("next_year", "Next meeting (year)", "optint", t.next_year),
        DialogField(
            "next_season",
            "Next meeting (season)",
            "select",
            t.next_season,
            options=pairs(SEASONS),
        ),
        DialogField("meeting_place", "Meeting place", "text", t.meeting_place),
        DialogField(
            "praeco_id",
            "Praeco",
            "select",
            t.praeco_id,
            options=_character_options(saga),
            **officer,
        ),
        DialogField(
            "quaesitor_id",
            "Presiding Quaesitor",
            "select",
            t.quaesitor_id,
            options=_character_options(saga),
            **officer,
        ),
        DialogField(
            "covenants_total",
            "Covenants in all",
            "optint",
            t.covenants_total,
            hint="Most are never written down; blank counts only those that are.",
        ),
        DialogField("magi_total", "Magi in all", "optint", t.magi_total),
    ]


def tribunal_problem(values: dict[str, Any]) -> str | None:
    """Why the Tribunal's values can't be saved, if they can't."""
    if values.get("meets_every", 1) < 1:
        return "A Tribunal meets every year at the most often."
    for key, words in (("covenants_total", "Covenants"), ("magi_total", "Magi")):
        if (values.get(key) or 0) < 0:
            return f"{words} in all can't be fewer than none."
    return None


def _apply(tribunal: Tribunal, values: dict[str, Any]) -> None:
    for key, value in values.items():
        setattr(tribunal, key, value)
    tribunal.next_season = tribunal.next_season or "Summer"


def new_tribunal_form(saga: Saga) -> Form:
    def apply(values: dict[str, Any]) -> None:
        _apply(tribunals.add(saga, values["name"]), values)

    return Form(
        "Create a New Tribunal",
        lambda: tribunal_fields(saga, None),
        apply,
        validate=tribunal_problem,
        save_label="Create",
    )


def edit_tribunal_form(saga: Saga, tribunal: Tribunal) -> Form:
    return Form(
        "Edit Tribunal",
        lambda: tribunal_fields(saga, tribunal),
        lambda values: _apply(tribunal, values),
        validate=tribunal_problem,
    )
