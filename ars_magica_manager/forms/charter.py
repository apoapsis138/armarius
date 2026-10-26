"""The forms of a covenant's Charter of Covenant (covenant_charter.py
says what the charter is and how it is shown): Edit Charter, Add and
Edit Clause, Break a Clause and Seal the Charter, and the Charter and
Clauses sections' Add, Edit and Delete. Both front-ends draw them.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from .. import covenant_charter as cc
from ..commands import Command, Form, Refuse, SectionOps, delete
from ..form_spec import DialogField, pairs
from ..markup import escape
from ..models import (
    CHARTER_SECTIONS,
    CLAUSE_AMENDED,
    CLAUSE_BROKEN,
    CLAUSE_IN_FORCE,
    CLAUSE_STATUSES,
    SEASONS,
    CharterClause,
    CharterSeal,
    Covenant,
    Saga,
)
from ..sections import CHARTER_SECTION, CLAUSES_SECTION

COV = cc.COV


# -- Edit Charter --


def charter_fields(covenant: Covenant) -> list[DialogField]:
    charter = cc.charter_of(covenant)
    return [
        DialogField(
            "name",
            "Name",
            "text",
            charter.name,
            required=True,
            placeholder="e.g. The Founders' Covenant Accord",
        ),
        DialogField(
            "season",
            "Sworn in",
            "select",
            charter.season or None,
            options=pairs(SEASONS),
            allow_blank=True,
        ),
        DialogField("year", "Year", "optint", charter.year),
        DialogField(
            "preamble",
            "Preamble",
            "area",
            charter.preamble,
            hint="The oath the members swear, or what the charter is for "
            f"({COV} p. 33).",
        ),
        DialogField(
            "ratified",
            "Ratified by a Quaesitor",
            "check",
            charter.ratified,
            hint=f"Then breaking it can be charged as a Low Crime ({COV} p. 36).",
        ),
    ]


def charter_form(covenant: Covenant) -> Form:
    charter = cc.charter_of(covenant)

    def apply(values: dict[str, Any]) -> None:
        charter.name = values.get("name") or ""
        charter.season = values.get("season") or ""
        charter.year = values.get("year")
        charter.preamble = values.get("preamble") or ""
        charter.ratified = bool(values.get("ratified"))

    return Form(
        "Edit Charter",
        lambda: charter_fields(covenant),
        apply,
        help_id=CHARTER_SECTION,
    )


# -- Seal the Charter --


def _sealed_key(character_id: str) -> str:
    return f"sealed_{character_id}"


def seal_fields(saga: Saga, covenant: Covenant) -> list[DialogField]:
    """A tick, a season and a year for each of the covenant's magi (and
    any who sealed it and have left since)."""
    charter = cc.charter_of(covenant)
    found: list[DialogField] = [
        DialogField(
            "about",
            "Seals",
            "info",
            "Each member's seal or signature is affixed to the charter, "
            f"to show he agrees to it ({COV} p. 33).",
        )
    ]
    for shown in cc.seals(saga, covenant):
        cid = shown.character.id
        seal = shown.seal
        key = _sealed_key(cid)

        def ticked(values: dict[str, Any], key: str = key) -> bool:
            return bool(values.get(key))

        found += [
            DialogField(key, shown.character.name, "check", seal is not None),
            DialogField(
                f"season_{cid}",
                "Sealed in",
                "select",
                (seal.season if seal else "") or None,
                options=pairs(SEASONS),
                allow_blank=True,
                show_if=ticked,
            ),
            DialogField(
                f"year_{cid}",
                "Year",
                "optint",
                seal.year if seal else charter.year,
                show_if=ticked,
            ),
        ]
    if len(found) == 1:
        found.append(
            DialogField(
                "none",
                "Magi",
                "info",
                "The covenant has no magi yet to seal it.",
            )
        )
    return found


def seal_live(saga: Saga, covenant: Covenant) -> Any:
    """The form's inspector: who will have sealed it, and who not."""

    def inspect(values: dict[str, Any]) -> str:
        done: list[str] = []
        waiting: list[str] = []
        for shown in cc.seals(saga, covenant):
            cid = shown.character.id
            name = escape(shown.character.name)
            if values.get(_sealed_key(cid)):
                at = cc.when(
                    values.get(f"year_{cid}"), values.get(f"season_{cid}") or ""
                )
                done.append(name + ("" if at == "—" else f" [dim]({escape(at)})[/]"))
            else:
                waiting.append(name)
        lines = [
            f"[b]{escape(cc.charter_title(cc.charter_of(covenant)))}[/]",
            f"[$label]Sealed by:[/] {', '.join(done) or '[dim]no one yet[/]'}",
        ]
        if waiting:
            lines.append(f"[$label]Not yet sworn:[/] {', '.join(waiting)}")
        return "\n".join(lines)

    return inspect


def seal_form(saga: Saga, covenant: Covenant) -> Form | Refuse:
    """More's Seal the Charter: which of the covenant's magi have sealed
    it, and when."""
    if not cc.seals(saga, covenant):
        return Refuse(
            "Seal the Charter", "The covenant has no magi yet to seal its charter."
        )
    charter = cc.charter_of(covenant)

    def apply(values: dict[str, Any]) -> None:
        kept: list[CharterSeal] = []
        for shown in cc.seals(saga, covenant):
            cid = shown.character.id
            if values.get(_sealed_key(cid)):
                kept.append(
                    CharterSeal(
                        cid,
                        values.get(f"year_{cid}"),
                        values.get(f"season_{cid}") or "",
                    )
                )
        # Seals of characters no longer in the saga stay as they were.
        known = {c.id for c in saga.characters}
        kept += [s for s in charter.seals if s.character_id not in known]
        charter.seals = kept

    return Form(
        "Seal the Charter",
        lambda: seal_fields(saga, covenant),
        apply,
        live=seal_live(saga, covenant),
        inspector="The Seals",
        help_id=CHARTER_SECTION,
    )


def charter_ops(saga: Saga, covenant: Covenant) -> dict[str, SectionOps]:
    """The Charter section's Edit, and the Clauses section's Add, Edit
    and Delete, by section id (as a sheet's core_ops keeps them)."""
    return {
        CHARTER_SECTION: SectionOps(
            edit=lambda _row: charter_form(covenant),
            rows=lambda: [cc.charter_title(cc.charter_of(covenant))],
        ),
        CLAUSES_SECTION: clause_ops(saga, covenant),
    }


# -- Add / Edit Clause --


def _amended_or_broken(values: dict[str, Any]) -> bool:
    return values.get("status") in (CLAUSE_AMENDED, CLAUSE_BROKEN)


def clause_fields(
    existing: CharterClause | None, default_year: int | None, default_season: str
) -> list[DialogField]:
    c = existing or CharterClause("", year=default_year, season=default_season)
    return [
        DialogField(
            "number",
            "Number or title",
            "text",
            c.number,
            required=True,
            placeholder="8, or a title such as Apprentices",
        ),
        DialogField(
            "section",
            "Section",
            "select",
            c.section or None,
            options=pairs(CHARTER_SECTIONS),
            allow_blank=True,
            hint=f"The part of the charter it belongs to ({COV} pp. 33-35); "
            "the list groups clauses by it.",
        ),
        DialogField("text", "Text", "area", c.text, required=True),
        DialogField(
            "season",
            "Agreed in",
            "select",
            c.season or None,
            options=pairs(SEASONS),
            allow_blank=True,
        ),
        DialogField("year", "Year", "optint", c.year),
        DialogField(
            "status", "Status", "select", c.status, options=pairs(CLAUSE_STATUSES)
        ),
        DialogField(
            "since_season",
            "Since",
            "select",
            c.since_season or None,
            options=pairs(SEASONS),
            allow_blank=True,
            show_if=_amended_or_broken,
        ),
        DialogField(
            "since_year", "Year", "optint", c.since_year, show_if=_amended_or_broken
        ),
        DialogField(
            "note",
            "How",
            "area",
            c.note,
            show_if=_amended_or_broken,
            hint="How it was broken, or what the amendment changed.",
        ),
    ]


def _made(values: dict[str, Any], existing: CharterClause | None) -> CharterClause:
    status = values.get("status") or CLAUSE_IN_FORCE
    keeps = status in (CLAUSE_AMENDED, CLAUSE_BROKEN)
    return replace(
        existing or CharterClause(""),
        number=values.get("number") or "",
        section=values.get("section") or "",
        text=values.get("text") or "",
        season=values.get("season") or "",
        year=values.get("year"),
        status=status,
        since_season=(values.get("since_season") or "") if keeps else "",
        since_year=values.get("since_year") if keeps else None,
        note=(values.get("note") or "") if keeps else "",
    )


def clause_live(saga: Saga, covenant: Covenant, index: int | None) -> Any:
    """The clause form's inspector: the clause as the list will show it."""

    def inspect(values: dict[str, Any]) -> str:
        charter = cc.charter_of(covenant)
        existing = charter.clauses[index] if index is not None else None
        draft = _made(values, existing)
        lines = [
            f"[b]{escape(cc.clause_name(draft))}[/]  "
            + cc.status_markup(draft)
            + (f"  [dim]{escape(draft.section)}[/]" if draft.section else ""),
            cc.clause_text(draft) or "[dim]…[/]",
        ]
        if extra := cc.note_line(draft):
            lines.append(extra)
        if glossed := cc.gloss(charter, draft):
            lines.append(glossed)
        return "\n".join(lines)

    return inspect


def clause_ops(saga: Saga, covenant: Covenant) -> SectionOps:
    """Add, Edit and Delete on the Clauses list; a row is the clause's
    index in the charter."""
    charter = cc.charter_of(covenant)

    def form(index: int | None) -> Form:
        existing = charter.clauses[index] if index is not None else None

        def apply(values: dict[str, Any]) -> None:
            made = _made(values, existing)
            if index is None:
                charter.clauses.append(made)
            else:
                charter.clauses[index] = made

        return Form(
            "Add Clause" if index is None else "Edit Clause",
            lambda: clause_fields(existing, saga.current_year, saga.current_season),
            apply,
            live=clause_live(saga, covenant, index),
            save_label="Add" if index is None else "Save",
            help_id=CLAUSES_SECTION,
            inspector="The Clause",
        )

    return SectionOps(
        add=lambda: form(None),
        edit=form,
        remove=lambda index: delete(
            charter.clauses, index, cc.clause_name(charter.clauses[index])
        ),
        rows=lambda: [cc.clause_name(c) for c in charter.clauses],
    )


# -- Break a Clause --


def can_break(covenant: Covenant, index: int | None) -> bool:
    """Whether Break a Clause is offered: on a clause not broken yet."""
    clauses = cc.charter_of(covenant).clauses
    return (
        index is not None
        and 0 <= index < len(clauses)
        and clauses[index].status != CLAUSE_BROKEN
    )


def break_fields(saga: Saga) -> list[DialogField]:
    return [
        DialogField(
            "season",
            "Season",
            "select",
            saga.current_season,
            options=pairs(SEASONS),
        ),
        DialogField("year", "Year", "int", saga.current_year),
        DialogField(
            "note",
            "How it was broken",
            "area",
            "",
            required=True,
            placeholder="Who broke it, and how",
        ),
    ]


def break_live(covenant: Covenant, clause: CharterClause) -> Any:
    """Break a Clause's inspector: the clause struck through, with the
    note as it will read."""

    def inspect(values: dict[str, Any]) -> str:
        draft = replace(
            clause,
            status=CLAUSE_BROKEN,
            since_year=values.get("year"),
            since_season=values.get("season") or "",
            note=(values.get("note") or "").strip() or "…",
        )
        return "\n".join(
            [
                f"[b]{escape(cc.clause_name(clause))}[/]",
                cc.clause_text(draft),
                cc.note_line(draft),
                "[dim]It stays in the charter, struck through.[/]",
                cc.gloss(cc.charter_of(covenant), draft),
            ]
        )

    return inspect


def break_clause(saga: Saga, covenant: Covenant, index: int | None) -> Command:
    """More's Break a Clause on the chosen clause: when, and how."""
    if not can_break(covenant, index):
        return Refuse(
            "Break a Clause", "Choose a clause of the charter that isn't broken yet."
        )
    assert index is not None
    clause = cc.charter_of(covenant).clauses[index]

    def apply(values: dict[str, Any]) -> None:
        clause.status = CLAUSE_BROKEN
        clause.since_season = values.get("season") or ""
        clause.since_year = values.get("year")
        clause.note = values.get("note") or ""

    return Form(
        f"Break a Clause: {escape(cc.clause_name(clause))}",
        lambda: break_fields(saga),
        apply,
        live=break_live(covenant, clause),
        save_label="Break",
        help_id=CLAUSES_SECTION,
        inspector="The Clause Struck",
    )
