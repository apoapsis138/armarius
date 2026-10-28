"""A character's Religion chapter -- no UI in here: whether the sheet has
it, its Faith section (his religion, his patron and Devotions, a mystic
path, the saints who refused him) with Edit Religion, and which of the
Church's sections follow it (forms.church). What each faith offers and
who may take it are rules.faiths'.

Pattern: the faith registry (rules.faiths.FAITHS) is Strategy kept in a
dict, as the activity registry is: the chapter asks his Faith for its
icon, its sections and its actions, and never tests the religion
itself."""

from __future__ import annotations

from typing import Any

from .. import devotion as devotion_forms
from .. import sourcebooks
from ..commands import Form, SectionOps
from ..markup import escape
from ..models import Character, Saga
from ..models.religion import CHRISTIAN
from ..rules import clergy as cl
from ..rules import devotion as dv
from ..rules import faiths, mysticism
from ..rules.theban_customs import pious
from ..sections import FAITH_SECTION
from .character import religion_field

HELP_ID = "religion"
TITLE = "Religion"


def _books(saga: Saga) -> frozenset[str] | None:
    return sourcebooks.saga_books(saga)


def shows(saga: Saga, character: Character) -> bool:
    """Whether the sheet has the Religion chapter: a person (not an
    animal) while a book that gives the faiths their rites is in play, or
    one with a Church career already recorded."""
    if character.animal is not None:
        return False
    return devotion_forms.invokes(saga) or cl.has_church_tab(character)


def church_shown(saga: Saga, character: Character) -> bool:
    """Whether the Church's Petitions and Canon Court follow: a Christian
    while The Church is in play, or anyone with a career recorded."""
    return cl.has_church_tab(character) or (
        faiths.faith(character).church and devotion_forms.the_church(saga)
    )


def orders_shown(saga: Saga, character: Character) -> bool:
    """Whether Holy Orders and Ordinations follow: the Church's sections,
    for one who may hold orders (rules.faiths.may_hold_orders)."""
    return church_shown(saga, character) and faiths.may_hold_orders(character)


def icon(character: Character) -> str:
    """The chapter's icon: his faith's."""
    return faiths.faith(character).icon


def religion_words(character: Character) -> str:
    held = character.background.religion
    return escape(held) if held else f"{CHRISTIAN} [dim](not set)[/]"


def faith_facts(character: Character) -> list[tuple[str, str]]:
    """The Faith section's facts: (label, markup)."""
    facts = [("Religion", religion_words(character))]
    if faiths.religion(character) == CHRISTIAN:
        devotions = dv.devotions(character)
        facts += [
            ("Patron saint", escape(dv.patron(character)) or "[dim](none)[/]"),
            (
                "Devotions",
                ", ".join(escape(dv.devotion_label(p)) for p in devotions)
                or "[dim](none)[/]",
            ),
        ]
        if path := mysticism.path(character):
            facts.append(("Mystic path", escape(path)))
        if refused := dv.refused(character):
            facts.append(("Refused him", ", ".join(map(escape, refused))))
    facts.append(("Pious", f"{pious(character):+d}"))
    return facts


def faith_note(character: Character) -> str:
    return faiths.faith(character).note


def faith_text(character: Character) -> str:
    """The terminal's Faith section: the facts two to a line, then what
    his faith gives him."""
    facts = [f"[$label]{k}:[/] {v}" for k, v in faith_facts(character)]
    lines = ["  ·  ".join(facts[i : i + 2]) for i in range(0, len(facts), 2)]
    lines.append(f"[dim]{escape(faith_note(character))}[/]")
    return "\n".join(lines)


def religion_form(saga: Saga, character: Character) -> Form:
    """Edit Religion: the faith he holds (Biographical Detail's field)."""

    def apply(values: dict[str, Any]) -> None:
        character.background.religion = str(values.get("religion") or "")

    return Form(
        "Edit Religion",
        lambda: [religion_field(character.background.religion)],
        apply,
        help_id=HELP_ID,
    )


def faith_ops(saga: Saga, character: Character) -> SectionOps:
    return SectionOps(
        edit=lambda _row: religion_form(saga, character),
        rows=lambda: [TITLE],
    )


def ops(saga: Saga, character: Character) -> dict[str, SectionOps]:
    return {FAITH_SECTION: faith_ops(saga, character)}
