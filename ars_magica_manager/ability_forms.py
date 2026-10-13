"""Abilities, independent of how they are drawn: the form for one
Ability (its xp, with the score it buys shown live, and its Specialty)
and a list of Abilities' Add, Edit and Delete (commands.SectionOps).

Adding chooses the Ability from the catalog first, then names what a
templated one needs ("Craft: {craft}"), then asks its xp and Specialty.
A character and a familiar share them.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from . import catalog, sourcebooks
from . import sheet_text as st
from .commands import Choice, Choose, Command, Form, SectionOps, delete
from .form_spec import DialogField, attr
from .markup import escape
from .models import Ability, AbilityDef, VirtueFlawInstance
from .rules import scores
from .rules import xp as xp_rules
from .virtue_forms import param_fields, params_from


def ability_fields(ability: Ability | None) -> list[DialogField]:
    """An Ability's total xp and Specialty (its name is the form's title)."""
    return [
        DialogField("xp", "XP", "int", attr(ability, "xp", 0)),
        DialogField(
            "specialty",
            "Specialty",
            "text",
            attr(ability, "specialty", None) or "",
            placeholder="e.g. Swords",
        ),
    ]


def ability_problem(values: dict[str, Any]) -> str | None:
    if values["xp"] < 0:
        return "XP can't be negative."
    return None


def ability_from(name: str, category: str, values: dict[str, Any]) -> Ability:
    return Ability(
        name=name,
        category=category,
        xp=values["xp"],
        specialty=values["specialty"] or None,
    )


def ability_live(
    name: str, virtues_flaws: Sequence[VirtueFlawInstance] = (), note: str = ""
) -> Callable[[dict[str, Any]], str]:
    """The form's live line: the score the xp buys, with the owner's
    Puissant (from `virtues_flaws`); `note` follows it (e.g. how much xp
    the Creation Worksheet gave it)."""
    bonus, _ = scores.ability_bonus(virtues_flaws, name)

    def live(values: dict[str, Any]) -> str:
        score = st.live_score(values["xp"], xp_rules.ABILITY_FACTOR, bonus)
        line = f"{escape(name)}: {score}"
        return f"{line}\n[$text-warning]{escape(note)}[/]" if note else line

    return live


def ability_form(
    name: str,
    ability: Ability | None,
    apply: Callable[[dict[str, Any]], Any],
    virtues_flaws: Sequence[VirtueFlawInstance] = (),
    *,
    save_label: str = "Save",
    note: str = "",
) -> Form:
    """Add or edit the Ability `name`; `apply` gets the form's values
    (ability_from builds the Ability from them)."""
    return Form(
        escape(name),
        lambda: ability_fields(ability),
        apply,
        validate=ability_problem,
        live=ability_live(name, virtues_flaws, note),
        save_label=save_label,
    )


def ability_label(ability: Ability) -> str:
    """An Ability as a row names it (markup): its name, Specialty and
    score."""
    specialty = f" ({escape(ability.specialty)})" if ability.specialty else ""
    return f"{escape(ability.name)}{specialty} {st.score_text(ability.progress)}"


def ability_choice(entry: AbilityDef) -> Choice:
    """A catalog Ability as the Add list offers it."""
    needs = f"  (needs: {', '.join(entry.parameters)})" if entry.parameters else ""
    return Choice(
        escape(f"{entry.name}  [{entry.category}]{needs}"),
        entry,
        st.ability_entry_text(entry),
        entry.category,
    )


def abilities_offered(
    held: Sequence[Ability], books: frozenset[str] | None = None
) -> list[AbilityDef]:
    """The catalog Abilities an owner holding `held` may add: not one
    already held (a templated one always), from a book in play and not
    hidden in the saga."""
    return [
        entry
        for entry in catalog.abilities_to_offer({a.name for a in held})
        if sourcebooks.in_play(entry.source, books) and not catalog.hidden(entry)
    ]


def ability_ops(
    abilities: list[Ability],
    virtues_flaws: Sequence[VirtueFlawInstance] = (),
    *,
    books: frozenset[str] | None = None,
    note: Callable[[str], str] | None = None,
) -> SectionOps:
    """Add, Edit and Delete for the list `abilities`; `virtues_flaws` are
    its owner's (for Puissant in the live score), `books` the books in
    play and `note` an Ability's note in its Edit form (by its name)."""

    def details(entry: AbilityDef, name: str) -> Form:
        def apply(values: dict[str, Any]) -> None:
            abilities.append(ability_from(name, entry.category, values))

        return ability_form(name, None, apply, virtues_flaws, save_label="Confirm")

    def chosen(entry: AbilityDef) -> Command:
        if not entry.parameters:
            return details(entry, entry.name)
        return Form(
            escape(entry.name),
            lambda: param_fields(entry.parameters),
            lambda values: details(
                entry,
                catalog.resolve_ability_name(
                    entry, params_from(entry.parameters, values)
                ),
            ),
            save_label="Confirm",
        )

    def edit(index: int) -> Form:
        existing = abilities[index]

        def apply(values: dict[str, Any]) -> None:
            abilities[index] = ability_from(existing.name, existing.category, values)

        return ability_form(
            existing.name,
            existing,
            apply,
            virtues_flaws,
            note=note(existing.name) if note is not None else "",
        )

    return SectionOps(
        add=lambda: Choose(
            "Add an Ability",
            lambda: [ability_choice(e) for e in abilities_offered(abilities, books)],
            chosen,
            empty="(no more Abilities available)",
        ),
        edit=edit,
        remove=lambda index: delete(abilities, index, abilities[index].name),
        rows=lambda: [ability_label(a) for a in abilities],
    )
