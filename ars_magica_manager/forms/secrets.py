"""A record's Secrets: what only the storyguide should read about a
covenant, a character, a Tribunal, a neighbour or a creature. Every one
of their sheets shows it in a Secrets chapter of its own, under the one
section id, so the same form edits it everywhere; a player signed in to
a hosted copy never sees it."""

from __future__ import annotations

from typing import Any

from ..commands import Form, SectionOps
from ..form_spec import EMPHASIS_HINT, DialogField
from ..markup import escape, markdown_text
from ..sections import SECRETS_SECTION

#: What a Secrets chapter says while nothing is written in it.
NONE_YET = "Nothing secret written yet: edit it to add what only you should know."


def secrets_fields(record: Any) -> list[DialogField]:
    return [
        DialogField(
            "secrets",
            "Secrets",
            "area",
            record.secrets,
            hint="Only the storyguide sees these: players signed in to a "
            f"hosted copy don't. {EMPHASIS_HINT}",
        )
    ]


def secrets_form(record: Any) -> Form:
    def apply(values: dict[str, Any]) -> None:
        record.secrets = values["secrets"]

    return Form(
        f"Secrets of {escape(record.name)}", lambda: secrets_fields(record), apply
    )


def secrets_ops(record: Any) -> dict[str, SectionOps]:
    """The Secrets section's Edit, by its section id."""
    return {SECRETS_SECTION: SectionOps(edit=lambda _row: secrets_form(record))}


def secrets_text(record: Any) -> str:
    """The record's secrets as markup, or a line saying there are none."""
    hidden = record.secrets.strip()
    return markdown_text(hidden) if hidden else f"[$label]{NONE_YET}[/]"
