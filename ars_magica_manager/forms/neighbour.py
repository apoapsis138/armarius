"""New Neighbour and Edit Neighbour, and the Region's lists' Add, Edit
and Delete (commands.SectionOps), for either front-end.

New Neighbour asks for the kind first, offering only the kinds whose
book is in play, then a plain form: a name is all it needs. Pattern:
the kinds' registry (neighbours.KINDS) is the Strategy; New's choice of
form per kind reduces to looking the kind up there."""

from __future__ import annotations

from typing import Any

from .. import neighbour_filter, neighbours, places, sourcebooks
from ..commands import Choice, Choose, Command, Confirm, Form, SectionOps, not_offered
from ..form_spec import DialogField, pairs
from ..markup import escape
from ..models import DETAIL_LEVELS, REALMS, Neighbour, Saga
from ..neighbour_lists import KindList
from ..sections import NEIGHBOUR_INFO_SECTION
from . import world as world_forms


def neighbour_fields(
    saga: Saga, neighbour: Neighbour | None, kind: str
) -> list[DialogField]:
    """A neighbour's common fields, with its kind's after the name, less
    those its kind hides: only the name is required."""
    n = neighbour or Neighbour(id="", name="", kind=kind)
    known = neighbours.KINDS.get(kind)
    own = known.fields if known is not None else None
    hides = known.hides if known is not None else frozenset()
    liege = [
        (escape(other.name), other.id)
        for other in saga.neighbours
        if other is not neighbour
    ]
    fields = [
        DialogField("name", "Name", "text", n.name, required=True),
    ]
    if neighbour is not None:
        kinds = [
            k
            for k in neighbours.KINDS.values()
            if k.key == n.kind or neighbours.in_play(saga, k)
        ]
        fields.append(
            DialogField(
                "kind",
                "Kind",
                "select",
                n.kind,
                options=[(k.name, k.key) for k in kinds],
                required=True,
            )
        )
    if own is not None:
        fields += own(saga, neighbour)
    fields += [
        DialogField(
            "summary",
            "Summary",
            "area",
            n.summary,
            hint="A paragraph: who they are and what they want.",
        ),
        DialogField(
            "detail",
            "Detail",
            "select",
            n.detail,
            options=pairs(DETAIL_LEVELS),
            hint="A line, a sketch, or written in full.",
        ),
        DialogField(
            "ruler",
            "Ruler or leader",
            "text",
            n.ruler,
            placeholder="e.g. Count Gottfried",
        ),
        DialogField(
            "answers_to",
            "Answers to",
            "select",
            n.answers_to,
            options=liege,
            allow_blank=True,
            placeholder="(no one)",
            hint="Its liege, bishop or master among the neighbours.",
        ),
        DialogField(
            "realm",
            "Realm",
            "select",
            n.realm or None,
            options=pairs(REALMS),
            allow_blank=True,
            placeholder="(none)",
        ),
    ]
    if kind == places.PLACE:
        mine = {n.id, *places.within(saga, n)} if neighbour is not None else set()
        fields.insert(
            len(fields) - 1,
            places.where_field(
                saga,
                n,
                "Inside",
                "The place it is part of: a regio inside a forest inside a county.",
                mine,
            ),
        )
    else:
        fields.append(places.where_field(saga, n, "Place"))
    return [f for f in fields if f.key not in hides]


def _kind_keys(saga: Saga, kind: str) -> set[str]:
    """The keys of the fields `kind` adds, kept in the details."""
    own = neighbours.KINDS[kind].fields if kind in neighbours.KINDS else None
    return {f.key for f in own(saga, None)} if own is not None else set()


def _apply(saga: Saga, neighbour: Neighbour, values: dict[str, Any]) -> None:
    detailed = _kind_keys(saga, neighbour.kind)
    values = dict(values)
    if "where" in values:
        places.put(neighbour, values.pop("where"))
    for key, value in values.items():
        if key in detailed:
            neighbour.details[key] = value
        else:
            setattr(neighbour, key, value)
    neighbour.answers_to = values.get("answers_to") or None
    neighbour.realm = values.get("realm") or ""
    places.sync(saga)


def new_neighbour_form(saga: Saga, kind: str) -> Form:
    name = neighbours.KINDS[kind].name

    def apply(values: dict[str, Any]) -> None:
        _apply(saga, neighbours.add(saga, kind, values["name"]), values)

    return Form(
        f"New {name}",
        lambda: neighbour_fields(saga, None, kind),
        apply,
        validate=neighbours.KINDS[kind].problem,
        save_label="Create",
    )


def edit_neighbour_form(saga: Saga, neighbour: Neighbour) -> Form:
    return Form(
        f"Edit {escape(neighbour.name)}",
        lambda: neighbour_fields(saga, neighbour, neighbour.kind),
        lambda values: _apply(saga, neighbour, values),
        validate=neighbours.kind_of(neighbour).problem,
    )


def _kind_choice(kind: neighbours.NeighbourKind) -> Choice:
    book = sourcebooks.SOURCEBOOKS.get(kind.book, "") if kind.book else ""
    detail = f"{escape(kind.blurb.capitalize())}."
    if book:
        detail += f"\n[$label]From {escape(book)}.[/]"
    return Choice(f"{kind.name}  [$label]{escape(kind.blurb)}[/]", kind.key, detail)


def new_neighbour(saga: Saga, group: str | None = None) -> Command:
    """New Neighbour: the kind (of `group`, if given) whose book is in
    play, then its form. With one kind to choose, its form at once."""
    kinds = (
        neighbours.kinds_of(group)
        if group is not None
        else list(neighbours.KINDS.values())
    )
    offered = [k for k in kinds if neighbours.in_play(saga, k)]
    if group is not None and len(offered) == 1:
        return new_neighbour_form(saga, offered[0].key)

    def others() -> list[Choice]:
        return [
            not_offered(
                _kind_choice(k),
                f"add {sourcebooks.SOURCEBOOKS.get(k.book, k.book)} in Saga Content",
            )
            for k in kinds
            if not neighbours.in_play(saga, k)
        ]

    return Choose(
        "New Neighbour: what kind?",
        lambda: [_kind_choice(k) for k in offered],
        lambda key: new_neighbour_form(saga, key),
        empty="No kind of neighbour has its book in play.",
        others=others,
    )


def _delete(saga: Saga, neighbour: Neighbour) -> Confirm:
    consequences = neighbours.deletion_consequences(saga, neighbour)
    message = f"Delete {escape(neighbour.name)}?"
    if consequences:
        message += "\n\n" + "\n".join(escape(c) for c in consequences)
    return Confirm(message, lambda: neighbours.delete(saga, neighbour))


def group_ops(saga: Saga, group: str) -> SectionOps:
    """A group of the Region: Add one of its kinds, Edit or Delete the
    chosen neighbour."""

    def members() -> list[Neighbour]:
        return neighbour_filter.shown(saga, group)

    return SectionOps(
        add=lambda: new_neighbour(saga, group),
        edit=lambda index: edit_neighbour_form(saga, members()[index]),
        remove=lambda index: _delete(saga, members()[index]),
        rows=lambda: [n.name for n in members()],
    )


def filter_form(saga: Saga) -> Form:
    """Narrow the Region's lists of neighbours to a region (a place that
    sits inside no other) and a kind; both blank shows them all."""
    wanted = neighbour_filter.current(saga)

    def fields() -> list[DialogField]:
        return [
            DialogField(
                "region",
                "Region",
                "select",
                wanted.region or None,
                options=[
                    (escape(p.name), p.id) for p in neighbour_filter.regions(saga)
                ],
                allow_blank=True,
                placeholder="(any)",
                hint="A neighbour inside it at any depth, or the region itself.",
            ),
            DialogField(
                "kind",
                "Kind",
                "select",
                wanted.kind or None,
                options=[(k.name, k.key) for k in neighbour_filter.kinds(saga)],
                allow_blank=True,
                placeholder="(any)",
                hint="Blank both to show every neighbour.",
            ),
        ]

    def apply(values: dict[str, Any]) -> None:
        neighbour_filter.choose(
            saga,
            neighbour_filter.Filter(
                region=values.get("region") or "", kind=values.get("kind") or ""
            ),
        )

    return Form("Filter Neighbours", fields, apply, save_label="Filter")


def region_ops(saga: Saga) -> dict[str, SectionOps]:
    """Every list of the Region the core edits, by section id."""
    return {g.section_id: group_ops(saga, g.key) for g in neighbours.GROUPS}


def neighbour_ops(saga: Saga, neighbour: Neighbour) -> dict[str, SectionOps]:
    """A neighbour's sheet: its top panel, its attitude, favours and
    links."""
    return {
        NEIGHBOUR_INFO_SECTION: SectionOps(
            edit=lambda _row: edit_neighbour_form(saga, neighbour)
        ),
        **world_forms.record_ops(saga, neighbour),
        **{
            entry.section_id: entry.ops(saga, neighbour)
            for entry in tab_lists(neighbour)
        },
    }


def tab_lists(neighbour: Neighbour) -> tuple[KindList, ...]:
    """The lists the neighbour's kind adds to its sheet."""
    kind = neighbours.kind_of(neighbour)
    tabs = ([kind.tab] if kind.tab is not None else []) + list(kind.more)
    return tuple(entry for tab in tabs for entry in tab.lists)


def delete_neighbour(saga: Saga, neighbour: Neighbour) -> Confirm:
    return _delete(saga, neighbour)
