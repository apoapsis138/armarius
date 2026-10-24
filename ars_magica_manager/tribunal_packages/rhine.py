"""The Rhine Tribunal's customs (Guardians of the Forests: The Rhine
Tribunal): its covenants band together in gilds, each with its dues.
Notice of a case is due a season before the meeting, as under the core
rules: the book sets no other period.

A gild is kept in the package's data as {"name", "members" (covenant
ids), "dues"}: the roster gains a Gild column, and the sheet a Gilds
list."""

from __future__ import annotations

import re
from typing import Any

from .. import tribunals
from ..commands import Command, Confirm, Form, SectionOps
from ..form_spec import DialogField
from ..grids import Grid
from ..markup import escape
from ..models import Covenant, Saga, Tribunal
from ..sections import GILDS_SECTION
from . import (
    PackageList,
    PackageTab,
    RosterColumn,
    TribunalPackage,
    entries,
    register,
)

KEY = "rhine"


def gilds(tribunal: Tribunal) -> list[dict[str, Any]]:
    """The Tribunal's gilds, in the order entered."""
    return entries(tribunal, KEY, "gilds")


#: The trees the Rhine's gilds are named for, each with its symbol.
GILD_TREES = ("Oak", "Hawthorn", "Ash", "Elder", "Linden", "Apple")


def gild_tree(name: str) -> str | None:
    """The tree a gild's name names ("Oak Gild (Eichengilde)": "Oak"),
    whose symbol it bears; None for a name naming none, or several."""
    words = set(re.findall(r"[a-z]+", name.lower()))
    found = [tree for tree in GILD_TREES if tree.lower() in words]
    return found[0] if len(found) == 1 else None


def gilds_of(tribunal: Tribunal, covenant: Covenant) -> list[str]:
    """The names of the gilds `covenant` belongs to."""
    return [g["name"] for g in gilds(tribunal) if covenant.id in g.get("members", [])]


def _members(saga: Saga, gild: dict[str, Any]) -> list[str]:
    names = []
    for ident in gild.get("members", []):
        covenant = saga.covenant(ident)
        if covenant is not None:
            names.append(covenant.name)
    return names


def gilds_title(_saga: Saga, tribunal: Tribunal) -> str:
    return f"Gilds ({len(gilds(tribunal))})"


def gilds_grid(saga: Saga, tribunal: Tribunal) -> Grid:
    """Each gild: its member covenants and its dues."""
    rows = [
        [g["name"], ", ".join(_members(saga, g)), g.get("dues", "")]
        for g in gilds(tribunal)
    ]
    return Grid(
        ["Gild", "Members", "Dues"],
        rows,
        list(range(len(rows))),
        "No gilds yet: the Rhine's covenants band together in gilds, each "
        "with its dues.",
        caps=[18, 40, 0],
        stretch=1,
    )


def covenant_gild_fields(
    _saga: Saga, tribunal: Tribunal, covenant: Covenant | None
) -> list[DialogField]:
    """A covenant's own form: a tick for each of the Tribunal's gilds,
    on for those it belongs to."""
    ident = covenant.id if covenant is not None else None
    return [
        DialogField(
            f"gild_{index}",
            escape(gild["name"]),
            "check",
            ident in gild.get("members", []),
            hint="The gilds it belongs to." if index == 0 else "",
        )
        for index, gild in enumerate(gilds(tribunal))
    ]


def save_covenant_gilds(tribunal: Tribunal, ident: str, values: dict[str, Any]) -> None:
    """Keep a covenant's gild ticks: it joins the gilds ticked and
    leaves the others."""
    for index, gild in enumerate(gilds(tribunal)):
        key = f"gild_{index}"
        if key not in values:
            continue
        members = gild.setdefault("members", [])
        if values[key] and ident not in members:
            members.append(ident)
        elif not values[key] and ident in members:
            members.remove(ident)


def gild_fields(
    saga: Saga, tribunal: Tribunal, gild: dict[str, Any] | None
) -> list[DialogField]:
    """A gild: its name, its dues, and a tick for each covenant of the
    Tribunal that belongs to it."""
    members = set(gild.get("members", [])) if gild is not None else set()
    fields = [
        DialogField(
            "name",
            "Gild",
            "text",
            gild["name"] if gild is not None else "",
            required=True,
            placeholder="e.g. Hermetic",
        ),
        DialogField(
            "dues",
            "Dues",
            "text",
            gild.get("dues", "") if gild is not None else "",
            placeholder="e.g. 2 pawns of vis a year",
        ),
    ]
    fields += [
        DialogField(f"member_{c.id}", escape(c.name), "check", c.id in members)
        for c in tribunals.covenants_of(saga, tribunal)
    ]
    return fields


def _gild_from(
    saga: Saga, tribunal: Tribunal, values: dict[str, Any], gild: dict[str, Any]
) -> None:
    gild["name"] = values["name"]
    gild["dues"] = values.get("dues", "")
    shown = {c.id for c in tribunals.covenants_of(saga, tribunal)}
    # Members no longer in the Tribunal stay, unseen, as the form can't
    # show them.
    kept = [m for m in gild.get("members", []) if m not in shown]
    gild["members"] = kept + [
        ident for ident in sorted(shown) if values.get(f"member_{ident}")
    ]


def gild_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    def form(gild: dict[str, Any] | None) -> Form:
        def apply(values: dict[str, Any]) -> None:
            target = gild if gild is not None else {}
            _gild_from(saga, tribunal, values, target)
            if gild is None:
                gilds(tribunal).append(target)

        return Form(
            "Add a Gild" if gild is None else "Edit a Gild",
            lambda: gild_fields(saga, tribunal, gild),
            apply,
            save_label="Add" if gild is None else "Save",
        )

    def remove(index: int) -> Command:
        gild = gilds(tribunal)[index]

        def apply() -> None:
            gilds(tribunal).remove(gild)

        return Confirm(f"Delete the gild {escape(gild['name'])}?", apply)

    return SectionOps(
        add=lambda: form(None),
        edit=lambda index: form(gilds(tribunal)[index]),
        remove=remove,
        rows=lambda: [g["name"] for g in gilds(tribunal)],
    )


RHINE = TribunalPackage(
    KEY,
    "Rhine",
    customs="Gilds",
    book="GotF",
    skips_grand_tribunal=True,
    columns=(
        RosterColumn(
            "Gild",
            lambda _saga, tribunal, covenant: ", ".join(gilds_of(tribunal, covenant)),
            20,
        ),
    ),
    tabs=(
        PackageTab(
            "Gilds",
            "tab-trib-gilds",
            (PackageList(GILDS_SECTION, gilds_title, gilds_grid, gild_ops),),
        ),
    ),
    about="Its covenants band together in gilds, with dues.",
    covenant_fields=covenant_gild_fields,
    save_covenant=save_covenant_gilds,
)

register(RHINE)
