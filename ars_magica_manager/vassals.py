"""Vassal covenants: a covenant that has sworn an oath to another
(Covenant.liege_id), with the oath's duties written on it
(Covenant.oath).

The vassalage shows only while both covenants are in the same Tribunal:
an oath across Tribunals is a matter for the Tribunals, not a standing
tie. The vassal's sheet says "Vassal of" its liege and the liege's sheet
lists its vassals.

The oath is also what the covenant rules call Boons and Hooks: the
vassal is Beholden (Major Hook) to a Powerful Ally (Major Boon), and the
liege is owed Favors (Major Boon) by covenants it must protect (Minor
Hook). Swearing adds each, its detail naming the other covenant.

Pattern: an id reference, as a neighbour's answers_to, resolved when
shown, so renaming either covenant needs nothing."""

from __future__ import annotations

from typing import Any

from . import tribunal_packages
from .form_spec import DialogField
from .markup import escape
from .models import (
    BOON_HOOK_DETAIL,
    Covenant,
    Saga,
    VirtueFlawInstance,
    boon_hook_params,
    new_instance_id,
)

#: The oath's Boons and Hooks: the vassal's, then the liege's.
VASSAL_BOONS_HOOKS = ("covbh_hook_major_beholden", "covbh_boon_major_powerful_ally")
LIEGE_BOONS_HOOKS = ("covbh_boon_major_favors_owed", "covbh_hook_minor_protector")


def _covenant(saga: Saga, covenant_id: str | None) -> Covenant | None:
    return next((c for c in saga.covenants if c.id == covenant_id), None)


def liege_of(saga: Saga, covenant: Covenant) -> Covenant | None:
    """The covenant `covenant` is vassal to, while both share a
    Tribunal."""
    liege = _covenant(saga, covenant.liege_id)
    if liege is None or liege is covenant or liege.tribunal_id != covenant.tribunal_id:
        return None
    return liege


def vassals_of(saga: Saga, covenant: Covenant) -> list[Covenant]:
    """The covenants sworn to `covenant` in its Tribunal, by name."""
    return sorted(
        (c for c in saga.covenants if liege_of(saga, c) is covenant),
        key=lambda c: c.name,
    )


def rows(saga: Saga, covenant: Covenant) -> list[tuple[str, str]]:
    """The sheet's "Vassal of" and "Vassals" facts, each only when it
    has one."""
    shown = []
    liege = liege_of(saga, covenant)
    if liege is not None:
        shown.append(("Vassal of", liege.name))
    sworn = vassals_of(saga, covenant)
    if sworn:
        shown.append(("Vassals", ", ".join(c.name for c in sworn)))
    return shown


def fields(saga: Saga, covenant: Covenant) -> list[DialogField]:
    """A covenant's liege, the oath's duties, and whether to add the
    oath's Boons and Hooks."""
    sworn = lambda values: bool(values.get("liege_id"))
    return [
        DialogField(
            "liege_id",
            "Vassal of",
            "select",
            covenant.liege_id,
            options=[
                (escape(c.name), c.id)
                for c in sorted(saga.covenants, key=lambda c: c.name)
                if c is not covenant
            ],
            allow_blank=True,
            placeholder="(sworn to none)",
            hint="The covenant it has sworn an oath to; shown while both are "
            "in the same Tribunal.",
        ),
        DialogField(
            "oath",
            "The oath's duties",
            "area",
            covenant.oath,
            hint="What it owes its liege, and what the liege owes it.",
            show_if=sworn,
        ),
        DialogField(
            "oath_boons_hooks",
            "Add the oath's Boons and Hooks",
            "check",
            False,
            hint="Beholden and Powerful Ally on this covenant; Favors Owed and "
            "Protector on its liege. Ones already taken aren't added again.",
            show_if=sworn,
        ),
    ]


def _take(covenant: Covenant, vf_id: str, detail: str) -> None:
    """Add a Boon or Hook naming `detail`, unless it already has it."""
    for instance in covenant.boons_hooks:
        if instance.vf_id == vf_id and instance.params.get(BOON_HOOK_DETAIL) == detail:
            return
    covenant.boons_hooks.append(
        VirtueFlawInstance(
            vf_id=vf_id, id=new_instance_id(), params=boon_hook_params(detail, "")
        )
    )


def swear(vassal: Covenant, liege: Covenant) -> None:
    """Add the oath's Boons and Hooks to both covenants."""
    for vf_id in VASSAL_BOONS_HOOKS:
        _take(vassal, vf_id, liege.name)
    for vf_id in LIEGE_BOONS_HOOKS:
        _take(liege, vf_id, vassal.name)


def problem(saga: Saga, covenant: Covenant, values: dict[str, Any]) -> str | None:
    """Why the form's liege can't be sworn to: the Tribunal both would
    share (the one the form chooses) recognises no vassal covenants."""
    liege = _covenant(saga, values.get("liege_id"))
    tribunal_id = values.get("tribunal_id", covenant.tribunal_id)
    if liege is None or not tribunal_id or liege.tribunal_id != tribunal_id:
        return None
    tribunal = saga.tribunal(tribunal_id)
    if tribunal is None:
        return None
    return tribunal_packages.of(tribunal).no_vassals or None


def save(saga: Saga, covenant: Covenant, values: dict[str, Any]) -> None:
    """Take this module's fields out of `values` and apply them."""
    if "liege_id" not in values:
        return
    covenant.liege_id = values.pop("liege_id") or None
    covenant.oath = values.pop("oath", covenant.oath) or ""
    take = values.pop("oath_boons_hooks", False)
    liege = _covenant(saga, covenant.liege_id)
    if take and liege is not None and liege is not covenant:
        swear(covenant, liege)
