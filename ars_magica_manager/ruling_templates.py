"""The outcomes a Tribunal's rulings are written from: templates with
blanks ("{party} holds {what} for {years} years, until it is debated
again"), kept with the saga and edited on Edit Saga. At a meeting's
Rulings each case can take one; its blanks are asked, and the sentence
they make is the ruling the Acta and the Tribunal's records keep. A
template with a {years} blank sets a term: the matter comes due to be
debated again (tribunal_terms).

Each template is a plain dict ({"name", "text"}) so a save holds it as it
is; a saga that has never changed them uses the app's own (DEFAULTS).
A template is a Python format string, so no pattern is needed beyond
`str.format_map`."""

from __future__ import annotations

import string
from typing import Any

from .commands import Form, picked
from .form_spec import DialogField, ListEditor
from .markup import escape
from .models import Case, Saga

#: The blank whose number sets a term in years.
YEARS = "years"

#: The app's own templates, until the saga changes them. Acquittal's
#: costs and the Quaesitor's penalty follow HoH: True Lineages
#: (Tribunal Procedures).
DEFAULTS: tuple[dict[str, str], ...] = (
    {
        "name": "Fined",
        "text": "{party} pays {amount} to {whom} by {when}.",
    },
    {
        "name": "Holds for a term",
        "text": "{party} holds {what} for {years} years, until it is debated again.",
    },
    {
        "name": "Acquitted",
        "text": "{party} is acquitted; {prosecutor} bears the defence's costs.",
    },
    {
        "name": "Convicted",
        "text": "{party} is convicted; the Presiding Quaesitor sets the "
        "penalty: {penalty}.",
    },
    {
        "name": "Settled privately",
        "text": "Settled before the Presiding Quaesitor: {terms}.",
    },
    {
        "name": "Ruled",
        "text": "The Tribunal rules: {ruling}.",
    },
    # The Code's penalties (HoH: True Lineages pp. 59-61), paid by the
    # next Tribunal.
    {
        "name": "Damages",
        "text": "{party} pays {victim} damages of {damages} in vis or "
        "enchanted devices by the next Tribunal.",
    },
    {
        "name": "Fined (shared)",
        "text": "{party} pays a fine of {amount} by the next Tribunal: a "
        "third to {prosecutor}, two thirds to the Tribunal's coffers.",
    },
    {
        "name": "Seasons of service",
        "text": "{party} serves {seasons} seasons for House Mercere or "
        "Guernicus: {service}.",
    },
    {
        "name": "Investing items",
        "text": "{party} invests {items} and delivers them to {recipient} by "
        "the next Tribunal.",
    },
    {
        "name": "Loss of an apprentice",
        "text": "{party} surrenders the apprentice {apprentice} at once; "
        "{prosecutor} has first claim.",
    },
    {
        "name": "Banished",
        "text": "{party} is banished from the Tribunal and must find another "
        "Tribunal of residence.",
    },
    {
        "name": "Loss of a familiar",
        "text": "{party}'s cords to the familiar {familiar} are cut before the "
        "next Tribunal.",
    },
    {
        "name": "Death of a familiar",
        "text": "{party}'s familiar {familiar} is put to death before the next "
        "Tribunal.",
    },
    {
        "name": "Cast out",
        "text": "{party} is cast out of the Order: {victim} takes a quarter of "
        "the estate, {prosecutor} a quarter, and the heir the rest.",
    },
)


def templates(saga: Saga) -> list[dict[str, str]]:
    """The saga's templates: its own, or the app's until it has changed
    them."""
    if saga.ruling_templates is None:
        return [dict(t) for t in DEFAULTS]
    return saga.ruling_templates


def named(saga: Saga, name: str) -> dict[str, str] | None:
    return next((t for t in templates(saga) if t.get("name") == name), None)


def blanks(text: str) -> list[str]:
    """A template's blanks, in the order they first appear."""
    found: list[str] = []
    try:
        parsed = list(string.Formatter().parse(text))
    except ValueError:
        return found
    for _literal, blank, _spec, _conversion in parsed:
        if blank and blank not in found:
            found.append(blank)
    return found


def refused(text: str) -> str | None:
    """Why `text` can't be a template (a stray brace), or None."""
    try:
        list(string.Formatter().parse(text))
    except ValueError:
        return "A blank is a word in braces, such as {party}; a lone { or } can't be filled."
    if any(not b.replace(" ", "").replace("_", "").isalnum() for b in blanks(text)):
        return "A blank is a word or two in braces, such as {vis source}."
    return None


def fill(text: str, values: dict[str, Any]) -> str:
    """The template's sentence with its blanks filled; one left empty
    stays as its name in brackets, to be seen and mended."""

    class Shown(dict[str, str]):
        def __missing__(self, key: str) -> str:
            return f"[{key}]"

    given = Shown({k: str(v) for k, v in values.items() if str(v or "").strip()})
    try:
        return text.format_map(given)
    except ValueError, IndexError, KeyError:
        return text


def suggested(case: Case, blank: str, term: int | None) -> str:
    """What a blank starts as, from the case: the accused for {party},
    who brought it for {whom}, {prosecutor} and {victim}, the term for
    {years}."""
    plain = blank.casefold()
    if plain in ("party", "accused", "defendant"):
        return case.against
    if plain in ("whom", "prosecutor", "plaintiff", "brought by", "victim"):
        return case.brought_by
    if plain == YEARS:
        return str(term) if term else ""
    if plain == "penalty":
        return case.penalty
    return ""


# -- editing them (Edit Saga) --


def row(template: dict[str, str]) -> str:
    """A template as its list shows it."""
    return f"{template.get('name') or '(unnamed)'}: {template.get('text', '')}"


def entry_form(template: dict[str, str] | None) -> Form:
    """Add or change one template: its name and its words with blanks."""
    kept = template or {"name": "", "text": ""}

    def fields() -> list[DialogField]:
        return [
            DialogField("name", "Name", "text", kept.get("name", ""), required=True),
            DialogField(
                "text",
                "Says",
                "area",
                kept.get("text", ""),
                required=True,
                hint="A blank is a word in braces, asked for when a ruling "
                "uses it: {party}, {amount}, {vis source}. A {years} blank "
                "sets a term: the matter comes due to be debated again.",
            ),
        ]

    def validate(values: dict[str, Any]) -> str | None:
        return refused(values.get("text") or "")

    return Form(
        "Ruling Template"
        if template is None
        else f"Ruling Template: {escape(kept['name'])}",
        fields,
        picked(lambda values: {"name": values["name"], "text": values["text"]}),
        validate=validate,
    )


def saga_field(saga: Saga) -> DialogField:
    """Edit Saga's list of the templates."""
    return DialogField(
        "ruling_templates",
        "Ruling templates",
        "picker",
        [dict(t) for t in templates(saga)],
        display=lambda items: f"{len(items)} template{'' if len(items) == 1 else 's'}",
        items=ListEditor(row, entry_form, "Ruling Templates"),
        hint="The outcomes a Tribunal's rulings are written from, each with "
        "blanks filled in at the meeting.",
    )
