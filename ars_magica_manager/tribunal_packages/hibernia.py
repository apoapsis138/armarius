"""The Hibernian Tribunal's customs (The Contested Isle: The Hibernian
Tribunal). A covenant is represented at a meeting only while it shows its
cathach, the trophy it took when it was founded; one taken from it leaves
its magi without a vote until it is won back. A covenant being founded
must hold its land, cattle and cathach for a year before the praeco
recognises it. The supernatural factions of Ireland send ambassadors,
confirmed at the Sacred Council before each meeting, who vote as magi
do; much of its law is treaties between named parties; and the Coill
Trí owe the Order seven Gifted children at every meeting, one from each
of their túatha (the meeting's steps are in hibernia_meeting.py).

Kept in the package's data: "cathaigh", {covenant id: {"cathach" (what
it is), "taken_by" (who holds it, if taken), "taken_year", "since" (the
year a covenant being founded began holding it)}}; "ambassadors", each
{"id", "faction", "name", "confirmed"}; "treaties", each {"title",
"parties", "terms", "ends", "year", "witness"}; and "tuatha", each
{"name", "ceannaire"}, the Coill Trí's seven. The roster gains a Cathach
column, a covenant's own form its cathach, and the sheet an Ambassadors
tab with both lists."""

from __future__ import annotations

from typing import Any

from ..commands import Command, Confirm, Form, SectionOps
from ..form_spec import DialogField
from ..grids import Grid
from ..markup import escape
from ..models import Covenant, Saga, Tribunal, new_instance_id
from ..sections import AMBASSADORS_SECTION, TREATIES_SECTION
from . import (
    Envoy,
    PackageList,
    PackageTab,
    RosterColumn,
    TribunalPackage,
    data,
    entries,
    register,
)

KEY = "hibernia"

#: What the Code asks of a covenant founded in the Tribunal.
FOUNDING = (
    "Hibernia's Code: a new covenant must hold land, cattle and a cathach "
    "(a trophy it took, not made) for a year before the praeco recognises "
    "it, and its magi vote only while it shows the cathach at the meeting."
)

_FIELDS = ("cathach", "taken_by", "taken_year", "since")


def cathaigh(tribunal: Tribunal) -> dict[str, dict[str, Any]]:
    """Each covenant's cathach, by covenant id."""
    found = data(tribunal, KEY).setdefault("cathaigh", {})
    assert isinstance(found, dict)
    return found


def cathach_of(tribunal: Tribunal, covenant_id: str) -> dict[str, Any]:
    """What is recorded of the covenant's cathach ({} for nothing)."""
    return cathaigh(tribunal).get(covenant_id, {})


def recognised_in(entry: dict[str, Any]) -> int | None:
    """The year a covenant being founded is recognised: a year after it
    began holding its cathach (None for one long recognised)."""
    since = entry.get("since")
    return None if since is None else since + 1


def lacks_cathach(saga: Saga, tribunal: Tribunal, covenant: Covenant) -> str:
    """Why the covenant can't show its cathach ("" when it can): it was
    taken, or the covenant is still being founded."""
    entry = cathach_of(tribunal, covenant.id)
    holder = (entry.get("taken_by") or "").strip()
    if holder:
        year = entry.get("taken_year")
        return f"Its cathach is held by {holder}" + (f" since {year}" if year else "")
    recognised = recognised_in(entry)
    if recognised is not None and saga.current_year < recognised:
        return f"It is still being founded: recognised in {recognised}"
    return ""


def cathach_text(saga: Saga, tribunal: Tribunal, covenant: Covenant) -> str:
    """The roster's Cathach: what it is, or who has taken it, or when a
    covenant being founded is recognised."""
    entry = cathach_of(tribunal, covenant.id)
    holder = (entry.get("taken_by") or "").strip()
    if holder:
        year = entry.get("taken_year")
        return f"Taken by {holder}" + (f" ({year})" if year else "")
    recognised = recognised_in(entry)
    if recognised is not None and saga.current_year < recognised:
        return f"Founding: recognised {recognised}"
    return entry.get("cathach", "")


def covenant_fields(
    _saga: Saga, tribunal: Tribunal, covenant: Covenant | None
) -> list[DialogField]:
    """A covenant's own form: its cathach, who holds it if it was taken,
    and for one being founded the year it began holding it."""
    entry = cathach_of(tribunal, covenant.id) if covenant is not None else {}
    found = []
    if covenant is None:
        found.append(DialogField("founding", "", "info", FOUNDING))
    found += [
        DialogField(
            "cathach",
            "Cathach",
            "text",
            entry.get("cathach", ""),
            placeholder="e.g. the tusks of the Black Pig",
            hint="The trophy it shows at each meeting to be represented.",
        ),
        DialogField(
            "taken_by",
            "Cathach taken by",
            "text",
            entry.get("taken_by", ""),
            hint="Who holds it, if it was taken; blank while the covenant "
            "has it. Its magi have no vote until it is back.",
        ),
        DialogField(
            "taken_year",
            "Taken in (year)",
            "optint",
            entry.get("taken_year"),
        ),
        DialogField(
            "since",
            "Holding it since (year)",
            "optint",
            entry.get("since"),
            hint="For a covenant being founded: the year it began holding "
            "its land, cattle and cathach. It is recognised a year later.",
        ),
    ]
    return found


def save_covenant(tribunal: Tribunal, ident: str, values: dict[str, Any]) -> None:
    """Keep a covenant's cathach; nothing entered forgets it."""
    entry = {
        key: values[key].strip() if isinstance(values[key], str) else values[key]
        for key in _FIELDS
        if key in values
    }
    entry = {key: value for key, value in entry.items() if value not in ("", None)}
    if entry:
        cathaigh(tribunal)[ident] = entry
    else:
        cathaigh(tribunal).pop(ident, None)


# -- the ambassadors --


def ambassadors(tribunal: Tribunal) -> list[dict[str, Any]]:
    """The factions' ambassadors, in the order entered; each is given an
    id the first time it is read."""
    found = entries(tribunal, KEY, "ambassadors")
    for entry in found:
        entry.setdefault("id", new_instance_id())
    return found


def tuatha(tribunal: Tribunal) -> list[tuple[str, str]]:
    """The Coill Trí's túatha, each (name, ceannaire), as recorded."""
    return [
        (t.get("name", ""), t.get("ceannaire", ""))
        for t in entries(tribunal, KEY, "tuatha")
    ]


def confirmed(tribunal: Tribunal, meeting: dict[str, Any]) -> list[dict[str, Any]]:
    """The ambassadors who vote at `meeting`: those its Sacred Council
    confirmed, else (before it sits) those confirmed on the list."""
    council = meeting.get("council")
    if council is not None:
        ids = set(council.get("confirmed", []))
        return [a for a in ambassadors(tribunal) if a["id"] in ids]
    return [a for a in ambassadors(tribunal) if a.get("confirmed")]


def envoys(_saga: Saga, tribunal: Tribunal, meeting: dict[str, Any]) -> list[Envoy]:
    """Each ambassador confirmed for the meeting, a vote each."""
    return [
        Envoy(f"envoy_{a['id']}", a.get("name") or a.get("faction", ""), a["faction"])
        for a in confirmed(tribunal, meeting)
    ]


def ambassadors_title(_saga: Saga, tribunal: Tribunal) -> str:
    return f"Ambassadors ({len(ambassadors(tribunal))})"


def ambassadors_grid(_saga: Saga, tribunal: Tribunal) -> Grid:
    """Each faction's ambassador, and whether they are confirmed."""
    rows = [
        [a["faction"], a.get("name", ""), "Confirmed" if a.get("confirmed") else ""]
        for a in ambassadors(tribunal)
    ]
    return Grid(
        ["Faction", "Ambassador", "Vote"],
        rows,
        list(range(len(rows))),
        "No ambassadors yet: each supernatural faction of Ireland may send "
        "one, confirmed at the Sacred Council, who votes as a magus does.",
        caps=[30, 30, 0],
    )


def ambassador_fields(entry: dict[str, Any] | None) -> list[DialogField]:
    e = entry or {}
    return [
        DialogField(
            "faction",
            "Faction",
            "text",
            e.get("faction", ""),
            required=True,
            placeholder="e.g. the Tuatha Dé of Munster",
        ),
        DialogField(
            "name",
            "Ambassador",
            "text",
            e.get("name", ""),
            placeholder="(to be named)",
        ),
        DialogField(
            "confirmed",
            "Confirmed",
            "check",
            bool(e.get("confirmed", True)),
            hint="Confirmed at the Sacred Council: they vote at the meeting.",
        ),
    ]


def ambassador_ops(_saga: Saga, tribunal: Tribunal) -> SectionOps:
    def form(entry: dict[str, Any] | None) -> Form:
        def apply(values: dict[str, Any]) -> None:
            target = entry if entry is not None else {"id": new_instance_id()}
            target.update(values)
            if entry is None:
                ambassadors(tribunal).append(target)

        return Form(
            "Add an Ambassador" if entry is None else "Edit an Ambassador",
            lambda: ambassador_fields(entry),
            apply,
            save_label="Add" if entry is None else "Save",
        )

    def remove(index: int) -> Command:
        entry = ambassadors(tribunal)[index]

        def apply() -> None:
            ambassadors(tribunal).remove(entry)

        return Confirm(f"Delete the ambassador of {escape(entry['faction'])}?", apply)

    return SectionOps(
        add=lambda: form(None),
        edit=lambda index: form(ambassadors(tribunal)[index]),
        remove=remove,
        rows=lambda: [a["faction"] for a in ambassadors(tribunal)],
    )


# -- the treaties --


def treaties(tribunal: Tribunal) -> list[dict[str, Any]]:
    """The treaties in force, in the order entered."""
    return entries(tribunal, KEY, "treaties")


def treaties_title(_saga: Saga, tribunal: Tribunal) -> str:
    return f"Treaties ({len(treaties(tribunal))})"


def treaties_grid(_saga: Saga, tribunal: Tribunal) -> Grid:
    """Each treaty: its parties, the year made, its witness and how it
    ends."""
    rows = [
        [
            t["title"],
            t.get("parties", ""),
            "" if t.get("year") is None else str(t["year"]),
            t.get("witness", ""),
            t.get("ends", ""),
        ]
        for t in treaties(tribunal)
    ]
    return Grid(
        ["Treaty", "Parties", "Year", "Witness", "Ends"],
        rows,
        list(range(len(rows))),
        "No treaties yet: much of Hibernia's law is treaties between named "
        "parties, each witnessed by a Quaesitor.",
        caps=[26, 30, 4, 18, 0],
    )


def treaty_fields(entry: dict[str, Any] | None) -> list[DialogField]:
    e = entry or {}
    return [
        DialogField(
            "title",
            "Treaty",
            "text",
            e.get("title", ""),
            required=True,
            placeholder="e.g. The Treaty of the Ford",
        ),
        DialogField(
            "parties",
            "Parties",
            "text",
            e.get("parties", ""),
            hint="Who is bound by it: covenants, magi, factions.",
        ),
        DialogField("year", "Year", "optint", e.get("year")),
        DialogField(
            "witness",
            "Witnessed by",
            "text",
            e.get("witness", ""),
            hint="The Quaesitor who witnessed it.",
        ),
        DialogField(
            "ends",
            "How it ends",
            "text",
            e.get("ends", ""),
            placeholder="e.g. when either party dies",
        ),
        DialogField("terms", "Terms", "area", e.get("terms", "")),
    ]


def treaty_ops(_saga: Saga, tribunal: Tribunal) -> SectionOps:
    def form(entry: dict[str, Any] | None) -> Form:
        def apply(values: dict[str, Any]) -> None:
            target = entry if entry is not None else {}
            target.update(values)
            if entry is None:
                treaties(tribunal).append(target)

        return Form(
            "Add a Treaty" if entry is None else "Edit a Treaty",
            lambda: treaty_fields(entry),
            apply,
            save_label="Add" if entry is None else "Save",
        )

    def remove(index: int) -> Command:
        entry = treaties(tribunal)[index]

        def apply() -> None:
            treaties(tribunal).remove(entry)

        return Confirm(f"Delete {escape(entry['title'])}?", apply)

    return SectionOps(
        add=lambda: form(None),
        edit=lambda index: form(treaties(tribunal)[index]),
        remove=remove,
        rows=lambda: [t["title"] for t in treaties(tribunal)],
    )


HIBERNIA = TribunalPackage(
    KEY,
    "Hibernia",
    customs="Cathaigh and ambassadors",
    book="TCI",
    columns=(RosterColumn("Cathach", cathach_text, 24),),
    tabs=(
        PackageTab(
            "Ambassadors",
            "tab-trib-ambassadors",
            (
                PackageList(
                    AMBASSADORS_SECTION,
                    ambassadors_title,
                    ambassadors_grid,
                    ambassador_ops,
                ),
                PackageList(
                    TREATIES_SECTION, treaties_title, treaties_grid, treaty_ops
                ),
            ),
        ),
    ),
    meeting_steps=("sacred_council", "tithe"),
    envoys=envoys,
    covenant_fields=covenant_fields,
    save_covenant=save_covenant,
    credential="cathach",
    lacks_credential=lacks_cathach,
    no_vassals="Hibernia recognises no vassal covenants: each covenant "
    "answers to the Tribunal alone.",
    about="A covenant's magi vote only while it shows its cathach, the "
    "trophy it took when it was founded, and a new covenant must hold "
    "land, cattle and a cathach for a year to be recognised. The "
    "supernatural factions' ambassadors, confirmed at the Sacred Council, "
    "vote as magi do; its law is largely treaties; and the Coill Trí give "
    "the Order seven Gifted children at each meeting. It meets at the Hill "
    "of Tara, and certamen there allows no veto and no limit on who, when "
    "or how often.",
)

register(HIBERNIA)
