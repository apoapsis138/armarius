"""The Rhine Tribunal's customs (Guardians of the Forests: The Rhine
Tribunal): its covenants band together in gilds, each with its dues, and
notice of a case is wanted a year before the meeting.

A gild is kept in the package's data as {"name", "members" (covenant
ids), "dues"}: the roster gains a Gild column, and the sheet a Gilds
list."""

from __future__ import annotations

from typing import Any

from .. import tribunals
from ..commands import Command, Confirm, Form, SectionOps
from ..form_spec import DialogField
from ..grids import Grid
from ..markup import escape
from ..models import Covenant, Saga, Tribunal
from ..sections import GILDS_SECTION
from . import PackageList, RosterColumn, TribunalPackage, entries, register

KEY = "rhine"


def gilds(tribunal: Tribunal) -> list[dict[str, Any]]:
    """The Tribunal's gilds, in the order entered."""
    return entries(tribunal, KEY, "gilds")


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
    notice_seasons=4,
    notice_words="a year",
    columns=(
        RosterColumn(
            "Gild",
            lambda _saga, tribunal, covenant: ", ".join(gilds_of(tribunal, covenant)),
            20,
        ),
    ),
    lists=(
        PackageList(
            "Gilds",
            "tab-trib-gilds",
            GILDS_SECTION,
            gilds_title,
            gilds_grid,
            gild_ops,
        ),
    ),
    about="Its covenants band together in gilds, with dues; notice of a case "
    "is wanted a year before the meeting.",
)

register(RHINE)
