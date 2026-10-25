"""The Rhine Tribunal's customs (Guardians of the Forests: The Rhine
Tribunal): its magi band together in gilds, political factions that
cut across House and covenant (pp. 27-29). A magus belongs to one gild
at most, joins freely and publicly, and may not join a gild he has the
(Gild) Enmity Flaw for (p. 22); a gild has a leader or leaders and an
agenda, and the book gives it no dues. Notice of a case is due a season
before the meeting, as under the core rules: the book sets no other
period.

A gild is kept in the package's data as {"name", "agenda", "leader_ids"
(character ids), "magi" (its members' character ids), "members" (the
covenants most of whose magi belong to it)}: the roster gains a Gild
column, the sheet a Gilds list, a covenant's form a gild for each of its
magi, and a magus's sheet his gild. Saves made before the agenda had
its name kept it as "dues".

The Tremere of the Rhine have given their sigils to the House's two
exarchs, Stentorius and Severicus, who cast them (pp. 84, 109); the
package's "sigil_held_by" ({character id: holder's id}) says whose
sigil another casts, so its owner casts no vote of his own."""

from __future__ import annotations

import re
from typing import Any

from .. import tribunals, world
from ..commands import Command, Confirm, Form, SectionOps
from ..form_spec import DialogField
from ..grids import Grid
from ..markup import escape
from ..models import Character, Covenant, Saga, Tribunal
from ..sections import GILDS_SECTION
from . import (
    PackageList,
    PackageTab,
    RosterColumn,
    TribunalPackage,
    data,
    entries,
    register,
)

KEY = "rhine"


def gilds(tribunal: Tribunal) -> list[dict[str, Any]]:
    """The Tribunal's gilds, in the order entered."""
    found = entries(tribunal, KEY, "gilds")
    for gild in found:
        if "dues" in gild:
            gild.setdefault("agenda", gild.pop("dues"))
    return found


#: A gild's leaders at most (the Apple Gild's triumvirate, p. 29).
LEADERS = 3


def gild_of(tribunal: Tribunal, character_id: str) -> dict[str, Any] | None:
    """The gild the magus belongs to, or None: a magus may belong to one
    gild only (Guardians of the Forests p. 28)."""
    return next((g for g in gilds(tribunal) if character_id in g.get("magi", [])), None)


def join(tribunal: Tribunal, character_id: str, gild: dict[str, Any] | None) -> None:
    """The magus leaves any gild he is in and joins `gild` (None: none)."""
    for each in gilds(tribunal):
        magi = each.get("magi", [])
        if character_id in magi:
            magi.remove(character_id)
    if gild is not None:
        gild.setdefault("magi", []).append(character_id)


def enmities(character: Character) -> set[str]:
    """The trees of the gilds the magus has the (Gild) Enmity Flaw for:
    he may not join them (p. 22)."""
    found = set()
    for vf in character.virtues_flaws:
        if vf.vf_id == ENMITY:
            tree = gild_tree(vf.params.get("gild", ""))
            if tree is not None:
                found.add(tree)
    return found


def may_join(character: Character, gild: dict[str, Any]) -> bool:
    return gild_tree(gild.get("name", "")) not in enmities(character)


def sigil_held_by(tribunal: Tribunal) -> dict[str, str]:
    """Whose sigil another magus casts, by the owner's character id."""
    found = data(tribunal, KEY).setdefault("sigil_held_by", {})
    if not isinstance(found, dict):
        raise ValueError(f"The sigils held should be a mapping, not {found!r}.")
    return found


def casts_no_vote(_saga: Saga, tribunal: Tribunal, magus: Character) -> bool:
    """A magus whose sigil another casts has no vote of his own."""
    return magus.id in sigil_held_by(tribunal)


#: The trees the Rhine's gilds are named for, each with its symbol.
GILD_TREES = ("Oak", "Hawthorn", "Ash", "Elder", "Linden", "Apple")


def gild_tree(name: str) -> str | None:
    """The tree a gild's name names ("Oak Gild (Eichengilde)": "Oak"),
    whose symbol it bears; None for a name naming none, or several."""
    words = set(re.findall(r"[a-z]+", name.lower()))
    found = [tree for tree in GILD_TREES if tree.lower() in words]
    return found[0] if len(found) == 1 else None


#: The (Gild) Enmity Flaw.
ENMITY = "vf_gild_enmity"


def gilds_of(tribunal: Tribunal, covenant: Covenant) -> list[str]:
    """The names of the gilds most of `covenant`'s magi belong to."""
    return [g["name"] for g in gilds(tribunal) if covenant.id in g.get("members", [])]


def roster_gilds(saga: Saga, tribunal: Tribunal, covenant: Covenant) -> str:
    """The roster's Gild: the gilds most of its magi belong to, then any
    other gild one of its magi has joined."""
    names = gilds_of(tribunal, covenant)
    for magus in world.covenant_magi(saga, covenant):
        gild = gild_of(tribunal, magus.id)
        if gild is not None and gild["name"] not in names:
            names.append(gild["name"])
    return ", ".join(names)


def _members(saga: Saga, gild: dict[str, Any]) -> list[str]:
    names = []
    for ident in gild.get("members", []):
        covenant = saga.covenant(ident)
        if covenant is not None:
            names.append(covenant.name)
    return names


def gilds_title(_saga: Saga, tribunal: Tribunal) -> str:
    return f"Gilds ({len(gilds(tribunal))})"


def _leaders(saga: Saga, gild: dict[str, Any]) -> str:
    found = (saga.character(i) for i in gild.get("leader_ids", []))
    return ", ".join(c.name for c in found if c is not None)


def _magi_text(saga: Saga, gild: dict[str, Any]) -> str:
    names = [c.name for c in (saga.character(i) for i in gild.get("magi", [])) if c]
    covenants = _members(saga, gild)
    parts = [", ".join(names)] if names else []
    if covenants:
        parts.append("most of " + ", ".join(covenants))
    return "; ".join(parts)


def gilds_grid(saga: Saga, tribunal: Tribunal) -> Grid:
    """Each gild: who leads it, its magi and the covenants most of whose
    magi belong to it, and its agenda."""
    rows = [
        [g["name"], _leaders(saga, g), _magi_text(saga, g), g.get("agenda", "")]
        for g in gilds(tribunal)
    ]
    return Grid(
        ["Gild", "Led by", "Members", "Agenda"],
        rows,
        list(range(len(rows))),
        "No gilds yet: the Rhine's magi band together in gilds, political "
        "factions across House and covenant, a magus in one at most.",
        caps=[18, 20, 30, 0],
        stretch=3,
    )


def covenant_gild_fields(
    saga: Saga, tribunal: Tribunal, covenant: Covenant | None
) -> list[DialogField]:
    """A covenant's own form: a tick for each of the Tribunal's gilds, on
    for those most of its magi belong to, and each of its magi's gild."""
    ident = covenant.id if covenant is not None else None
    found = [
        DialogField(
            f"gild_{index}",
            escape(gild["name"]),
            "check",
            ident in gild.get("members", []),
            hint="The gilds most of its magi belong to." if index == 0 else "",
        )
        for index, gild in enumerate(gilds(tribunal))
    ]
    magi = world.covenant_magi(saga, covenant) if covenant is not None else []
    for magus in magi:
        mine = gild_of(tribunal, magus.id)
        found.append(
            DialogField(
                f"gild_of_{magus.id}",
                f"Gild: {escape(magus.name)}",
                "select",
                str(gilds(tribunal).index(mine)) if mine is not None else None,
                options=[
                    (escape(g["name"]), str(index))
                    for index, g in enumerate(gilds(tribunal))
                    if may_join(magus, g)
                ],
                allow_blank=True,
                placeholder="(no gild)",
                hint="One gild at most, never one he has the Enmity Flaw "
                "for (Guardians of the Forests pp. 22, 28).",
            )
        )
    return found


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
    listed = gilds(tribunal)
    for key, value in values.items():
        if not key.startswith("gild_of_"):
            continue
        chosen = listed[int(value)] if value not in (None, "") else None
        join(tribunal, key.removeprefix("gild_of_"), chosen)


def gild_fields(
    saga: Saga, tribunal: Tribunal, gild: dict[str, Any] | None
) -> list[DialogField]:
    """A gild: its name, its agenda, its leaders, and a tick for each
    covenant of the Tribunal most of whose magi belong to it."""
    members = set(gild.get("members", [])) if gild is not None else set()
    leaders = list(gild.get("leader_ids", [])) if gild is not None else []
    magi = [
        (escape(m.name), m.id)
        for c in tribunals.covenants_of(saga, tribunal)
        for m in world.covenant_magi(saga, c)
    ]
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
            "agenda",
            "Agenda",
            "text",
            gild.get("agenda", "") if gild is not None else "",
            placeholder="e.g. to restore the Tribunal's ancient glory",
            hint="What it stands for; a member is expected to vote with it.",
        ),
    ]
    fields += [
        DialogField(
            f"leader_{n}",
            "Led by" if n == 0 else "And by",
            "select",
            leaders[n] if n < len(leaders) else None,
            options=magi,
            allow_blank=True,
            placeholder="(not recorded)",
        )
        for n in range(LEADERS)
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
    gild["agenda"] = values.get("agenda", "")
    gild.pop("dues", None)
    leaders = [values.get(f"leader_{n}") for n in range(LEADERS)]
    gild["leader_ids"] = list(dict.fromkeys(i for i in leaders if i))
    gild.setdefault("magi", [])
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


def magus_facts(
    saga: Saga, tribunal: Tribunal, character: Character
) -> list[tuple[str, str]]:
    """A Rhine magus's gild, and who casts his sigil when another does."""
    found = []
    gild = gild_of(tribunal, character.id)
    if gild is not None:
        found.append(("Gild", gild["name"]))
    holder = saga.character(sigil_held_by(tribunal).get(character.id))
    if holder is not None:
        found.append(("Sigil", f"cast by {holder.name}"))
    return found


RHINE = TribunalPackage(
    KEY,
    "Rhine",
    customs="Gilds",
    book="GotF",
    skips_grand_tribunal=True,
    columns=(RosterColumn("Gild", roster_gilds, 20),),
    tabs=(
        PackageTab(
            "Gilds",
            "tab-trib-gilds",
            (PackageList(GILDS_SECTION, gilds_title, gilds_grid, gild_ops),),
        ),
    ),
    about="Its magi band together in gilds, political factions across "
    "House and covenant, one gild to a magus.",
    covenant_fields=covenant_gild_fields,
    save_covenant=save_covenant_gilds,
    magus_facts=magus_facts,
    casts_no_vote=casts_no_vote,
)

register(RHINE)
