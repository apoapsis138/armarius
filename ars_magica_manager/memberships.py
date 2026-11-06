"""A faction's members: the characters, covenants, creatures and other
neighbours that belong to it, each with its role ("knight of the court", "elder").

A member is kept once, on the faction, in Neighbour.details["roster"],
each entry {"who": "<kind>:<id>", "role": ...}, the kind a Ref's
(characters, covenants, creatures, neighbours), as a story's `concerns` names its
record. The way back, the factions a record is a member of, is worked
out when a page is drawn (connections.member_of), so deleting either
side never leaves the other stale: a member since deleted shows as gone.
A faction's Answers to is its liege, not its membership.

Pattern: an id reference resolved when shown, kept in a kind's list
(neighbour_lists.KindList) like a university's masters; the way back is
the derived reverse index connections.py keeps for links."""

from __future__ import annotations

from typing import Any, TypedDict, cast

from . import references
from .commands import Choice, Choose, Picked, SectionOps
from .form_spec import DialogField
from .grids import Grid
from .markup import escape
from .models import Neighbour, Saga, details_list
from .neighbour_lists import KindList, list_ops
from .references import Fact
from .rules import sites
from .sections import MEMBERS_SECTION

#: The kinds of record a faction's member can be, as a chooser heads them.
MEMBER_KINDS: tuple[tuple[str, str], ...] = (
    ("characters", "Character"),
    ("covenants", "Covenant"),
    ("creatures", "Bestiary"),
    ("neighbours", "Neighbour"),
)


class Member(TypedDict, total=False):
    """One member of a faction: who ("characters:<id>") and their role."""

    who: str
    role: str


def roster(faction: Neighbour) -> list[Member]:
    return cast(list[Member], details_list(faction, "roster"))


def who_of(record: Any) -> str:
    """The `who` value naming `record`."""
    found = references.ref(record)
    if found is None:
        raise ValueError(f"{record!r} can't be a faction's member.")
    return f"{found.kind}:{found.id}"


def record_of(saga: Saga, member: Member) -> Any | None:
    """The record a member names, or None once it is gone."""
    kind, _, record_id = (member.get("who") or "").partition(":")
    return references.find(saga, kind, record_id)


def name_of(saga: Saga, member: Member) -> str:
    found = record_of(saga, member)
    return found.name if found is not None else "(no longer in the saga)"


def _kind_word(record: Any) -> str:
    found = references.ref(record)
    kind = found.kind if found is not None else ""
    return dict(MEMBER_KINDS).get(kind, "")


def members(saga: Saga, faction: Neighbour) -> list[tuple[Any, str]]:
    """The records on a faction's roster that are still in the saga, each
    with its role."""
    return [
        (found, m.get("role") or "")
        for m in roster(faction)
        if (found := record_of(saga, m)) is not None
    ]


def factions_of(saga: Saga, record: Any) -> list[tuple[Neighbour, str]]:
    """The factions whose roster names `record`, each with its role
    there."""
    found = references.ref(record)
    if found is None:
        return []
    who = f"{found.kind}:{found.id}"
    return [
        (n, m.get("role") or "")
        for n in saga.neighbours
        if n.kind == "faction"
        for m in n.details.get("roster") or []
        if m.get("who") == who
    ]


# -- the Members list on a faction's tab --


def members_title(_saga: Saga, faction: Neighbour) -> str:
    return f"Members ({len(roster(faction))})"


def members_grid(saga: Saga, faction: Neighbour) -> Grid:
    rows = []
    for member in roster(faction):
        found = record_of(saga, member)
        rows.append(
            [
                name_of(saga, member),
                _kind_word(found) if found is not None else "",
                member.get("role") or "",
            ]
        )
    return Grid(
        ["Member", "Kind", "Role"],
        rows,
        list(range(len(rows))),
        "No members recorded: add a character, a creature or a neighbour.",
        caps=[30, 10, 0],
    )


def choose_member(saga: Saga, faction: Neighbour) -> Choose:
    """Who can be a member: any character, creature or neighbour but a
    place and the faction itself."""

    def choices() -> list[Choice]:
        found: list[Choice] = []
        for kind, heading in MEMBER_KINDS:
            for record in getattr(saga, kind):
                if record is faction or sites.is_place(record):
                    continue
                found.append(
                    Choice(
                        escape(record.name),
                        f"{kind}:{record.id}",
                        escape(heading),
                        facets=(("Kind", heading),),
                    )
                )
        return found

    return Choose(
        "Member",
        choices,
        Picked,
        empty="No characters, creatures or other neighbours yet.",
        filters=("Kind",),
        help_id="section-nb-members",
    )


def member_fields(
    saga: Saga, faction: Neighbour, member: Member | None
) -> list[DialogField]:
    m = member or {}
    return [
        DialogField(
            "who",
            "Member",
            "picker",
            m.get("who"),
            required=True,
            placeholder="(choose one)",
            hint="A character, a Bestiary creature or another neighbour.",
            choose=lambda _current: choose_member(saga, faction),
            display=lambda value: name_of(saga, {"who": value}) if value else "",
        ),
        DialogField(
            "role",
            "Role",
            "text",
            m.get("role", ""),
            placeholder="e.g. knight of the court",
        ),
    ]


def member_ops(saga: Saga, faction: Neighbour) -> SectionOps:
    return list_ops(
        saga,
        faction,
        "roster",
        "Member",
        member_fields,
        lambda m: name_of(saga, m),
    )


MEMBERS = KindList(MEMBERS_SECTION, members_title, members_grid, member_ops)


def members_fact(saga: Saga, faction: Neighbour) -> list[Fact]:
    """Its members, each linked; none while it has none."""
    found = members(saga, faction)
    if not found:
        return []
    value = ", ".join(f"{r.name} ({role})" if role else r.name for r, role in found)
    return [Fact("Members", value, references.refs(*(r for r, _ in found)))]
