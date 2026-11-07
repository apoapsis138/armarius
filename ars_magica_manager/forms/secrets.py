"""A record's Secrets: what only the storyguide should know about a
covenant, a character, a Tribunal, a neighbour or a creature, as a list.
Each secret has a short title and its words, and the season it was
revealed to the troupe, if it has been. Every one of their sheets shows
the list in a Secrets chapter of its own, under the one section id, so
the same forms edit it everywhere.

The storyguide sees every secret, each marked revealed or not in words;
anyone else (a player, or Player view: viewing.py) sees only the revealed
ones, in the record's Known section. Revealing one is the same Reveal as a
record's (forms/reveal.py), given the secret. Split breaks a secret of
several paragraphs into one secret each, after showing the parts: an
older save's Secrets come in as one untitled secret.

Pattern: the selectable list (commands.SectionOps) with a FieldsDialog
for each secret."""

from __future__ import annotations

import re
from typing import Any

from .. import viewing, world
from ..commands import Confirm, Form, Refuse, SectionOps, delete, notes
from ..form_spec import EMPHASIS_HINT, DialogField
from ..markup import escape, fit, markdown_text
from ..models import Secret
from ..sections import SECRETS_SECTION

#: What a Secrets chapter says while nothing is written in it.
NONE_YET = "No secrets yet: add what only you should know, one secret at a time."
#: What a Known section says while nothing has been revealed.
NONE_KNOWN = "Nothing revealed yet."
SPLIT_TITLE = "Split by Paragraph"

_TITLE_WIDTH = 34
_PARAGRAPH = re.compile(r"\n[ \t]*\n")


def title_of(secret: Secret) -> str:
    """The secret's title, or for an untitled one its first words."""
    if secret.title.strip():
        return secret.title.strip()
    first = " ".join(secret.text.split())
    return fit(first, _TITLE_WIDTH) if first else "(untitled)"


def state_text(secret: Secret) -> str:
    """ "Revealed Spring 1221", or "Not revealed"."""
    if not secret.revealed:
        return "Not revealed"
    return f"Revealed {world.when_text(secret.revealed_year, secret.revealed_season)}"


def revealed(record: Any) -> list[Secret]:
    return [s for s in record.secrets if s.revealed]


def storyguides(record: Any) -> bool:
    """Whether whoever is looking reads every secret (the storyguide), not
    just the revealed ones."""
    return viewing.reads(part=SECRETS_SECTION)


def shown(record: Any) -> bool:
    """Whether the record's Secrets tab or chapter shows: always to the
    storyguide (titled Secrets), to anyone else (titled Known) once a
    secret is revealed."""
    return storyguides(record) or bool(revealed(record))


def tab_title(record: Any) -> str:
    return "Secrets" if storyguides(record) else "Known"


# -- the form --


def secret_fields(secret: Secret | None) -> list[DialogField]:
    return [
        DialogField(
            "title",
            "Title",
            "text",
            secret.title if secret is not None else "",
            hint="A few words: what the list shows.",
        ),
        DialogField(
            "text",
            "Secret",
            "area",
            secret.text if secret is not None else "",
            required=True,
            hint="Only the storyguide reads this until it is revealed. "
            + EMPHASIS_HINT,
        ),
    ]


def secret_form(record: Any, secret: Secret | None) -> Form:
    def apply(values: dict[str, Any]) -> None:
        if secret is None:
            record.secrets.append(Secret(values["title"], values["text"]))
        else:
            secret.title, secret.text = values["title"], values["text"]

    verb = "New Secret" if secret is None else "Edit Secret"
    return Form(
        f"{verb} of {escape(record.name)}",
        lambda: secret_fields(secret),
        apply,
        help_id=SECRETS_SECTION,
    )


def secrets_ops(record: Any) -> dict[str, SectionOps]:
    """The Secrets list's Add, Edit and Delete, by its section id."""
    return {
        SECRETS_SECTION: SectionOps(
            add=lambda: secret_form(record, None),
            edit=lambda row: secret_form(record, record.secrets[row]),
            remove=lambda row: delete(
                record.secrets, row, title_of(record.secrets[row])
            ),
            rows=lambda: [title_of(s) for s in record.secrets],
        )
    }


# -- what a sheet shows --


def secret_rows(record: Any) -> list[tuple[int | None, str]]:
    """The storyguide's list: each secret's title and whether it is
    revealed, in words."""
    return [
        (
            i,
            f"{escape(fit(title_of(s), _TITLE_WIDTH)):<{_TITLE_WIDTH}}  {state_text(s)}",
        )
        for i, s in enumerate(record.secrets)
    ]


def secret_text(secret: Secret) -> str:
    """One secret in full (markup)."""
    head = f"[b]{escape(title_of(secret))}[/]  [$label]{state_text(secret)}[/]"
    words = secret.text.strip()
    return f"{head}\n{markdown_text(words)}" if words else head


def secrets_text(record: Any) -> str:
    """Every secret in full (markup), or a line saying there are none."""
    if not record.secrets:
        return f"[$label]{NONE_YET}[/]"
    return "\n\n".join(secret_text(s) for s in record.secrets)


def known_text(record: Any) -> str:
    """The revealed secrets in full (markup), for the Known section."""
    shown = revealed(record)
    if not shown:
        return f"[$label]{NONE_KNOWN}[/]"
    return "\n\n".join(
        f"[b]{escape(title_of(s))}[/]  [$label]{state_text(s)}[/]\n"
        + markdown_text(s.text.strip())
        for s in shown
    )


# -- Split --


def parts(secret: Secret) -> list[str]:
    """The secret's paragraphs."""
    return [p.strip() for p in _PARAGRAPH.split(secret.text) if p.strip()]


def splits(record: Any, row: int | None) -> bool:
    """Whether Split applies to the secret at `row`: it has paragraphs."""
    return (
        row is not None
        and 0 <= row < len(record.secrets)
        and (len(parts(record.secrets[row])) > 1)
    )


def split(record: Any, row: int) -> Confirm | Refuse:
    """Split by Paragraph: the secret at `row` becomes one secret for each
    of its paragraphs, each revealed as it was; the parts are shown first."""
    if not splits(record, row):
        return Refuse(
            SPLIT_TITLE, "That secret is one paragraph: there is nothing to split."
        )
    secret = record.secrets[row]
    found = parts(secret)

    def apply() -> list[str]:
        made = [
            Secret(
                secret.title if i == 0 else "",
                words,
                secret.revealed_year,
                secret.revealed_season,
            )
            for i, words in enumerate(found)
        ]
        record.secrets[row : row + 1] = made
        return notes(f"Split into {len(made)} secrets: give each a title with Edit.")

    preview = "\n".join(
        f"{i}. {escape(fit(' '.join(words.split()), 60))}"
        for i, words in enumerate(found, start=1)
    )
    return Confirm(
        f"Split {escape(title_of(secret))} into {len(found)} secrets, one for "
        f"each paragraph?\n\n{preview}",
        apply,
        yes_label="Split",
        title=SPLIT_TITLE,
    )
