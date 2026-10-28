"""The forms of a covenant's Charter of Covenant (covenant_charter.py
says what the charter is and how it is shown): Edit Charter, Seal the
Charter, End Membership, the templates' Use, Save and Forget, Add and
Edit Clause, Break a Clause, Censure and Charge at Tribunal, and the
Charter and Clauses sections' Add, Edit and Delete. Both front-ends draw
them.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from typing import Any

from .. import charter_templates
from .. import covenant_charter as cc
from .. import tribunal_packages as tp
from ..commands import Command, Confirm, Form, Refuse, SectionOps, Then, delete
from ..form_spec import DialogField, pairs
from ..markup import escape
from ..models import (
    CENSURE_EXPELLED,
    CENSURE_LOWERED,
    CENSURE_WITHHELD,
    CENSURES,
    CHARTER_SECTIONS,
    CLAUSE_AMENDED,
    CLAUSE_BROKEN,
    CLAUSE_IN_FORCE,
    CLAUSE_STATUSES,
    PRIVILEGES,
    SEASONS,
    STANDING_ASSOCIATE,
    STANDING_EXPELLED,
    STANDING_FULL,
    STANDING_GUEST,
    STANDING_PROBATION,
    STANDINGS,
    Case,
    Censure,
    Character,
    CharterClause,
    CharterSeal,
    Covenant,
    CovenantDiaryEntry,
    Saga,
)
from ..sections import CHARTER_SECTION, CLAUSES_SECTION
from .grogs import leave_covenant

COV = cc.COV

#: More's titles, as both front-ends' buttons and menus name them.
USE_TEMPLATE = "Use a Template"
SAVE_TEMPLATE = "Save as Template"
FORGET_TEMPLATE = "Forget a Template"
END_MEMBERSHIP = "End Membership"
CENSURE = "Censure"
CHARGE = "Charge at Tribunal"


# -- Edit Charter --


def _notarized(values: dict[str, Any]) -> bool:
    return bool(values.get("ratified"))


def charter_fields(saga: Saga, covenant: Covenant) -> list[DialogField]:
    charter = cc.charter_of(covenant)
    found = [
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
            "probation_seasons",
            "Probation (seasons)",
            "optint",
            charter.probation_seasons,
            hint="How long a probationary member serves before full "
            "membership; blank if the charter sets no term (the Charter of "
            "Arae Flaviae's is 7).",
        ),
        DialogField(
            "ratified",
            "Notarized by a Quaesitor",
            "check",
            charter.ratified,
            hint="The Official Seal: then it is enforceable under the "
            f"Peripheral Code, and breaking it a Low Crime ({COV} pp. 32, 36).",
        ),
        DialogField(
            "notarized_by",
            "Quaesitor",
            "text",
            charter.notarized_by,
            show_if=_notarized,
            placeholder="who notarized it",
        ),
        DialogField(
            "notarized_season",
            "Notarized in",
            "select",
            charter.notarized_season or None,
            options=pairs(SEASONS),
            allow_blank=True,
            show_if=_notarized,
        ),
        DialogField(
            "notarized_year",
            "Year",
            "optint",
            charter.notarized_year,
            show_if=_notarized,
        ),
    ]
    custom = cc.custom(saga, covenant)
    if custom is not None and custom.reviewed_by:
        found.append(
            DialogField(
                "reviewed",
                f"Reviewed by {custom.reviewed_by}",
                "check",
                charter.reviewed,
                hint=custom.note,
            )
        )
    return found


def _charter_problem(values: dict[str, Any]) -> str | None:
    probation = values.get("probation_seasons")
    if probation is not None and probation < 1:
        return "A probation lasts at least a season, or leave it blank."
    return None


def charter_form(saga: Saga, covenant: Covenant) -> Form:
    charter = cc.charter_of(covenant)

    def apply(values: dict[str, Any]) -> None:
        charter.name = values.get("name") or ""
        charter.season = values.get("season") or ""
        charter.year = values.get("year")
        charter.preamble = values.get("preamble") or ""
        charter.probation_seasons = values.get("probation_seasons")
        charter.ratified = bool(values.get("ratified"))
        keep = charter.ratified
        charter.notarized_by = (values.get("notarized_by") or "") if keep else ""
        charter.notarized_season = (
            (values.get("notarized_season") or "") if keep else ""
        )
        charter.notarized_year = values.get("notarized_year") if keep else None
        if "reviewed" in values:
            charter.reviewed = bool(values.get("reviewed"))

    return Form(
        "Edit Charter",
        lambda: charter_fields(saga, covenant),
        apply,
        validate=_charter_problem,
        help_id=CHARTER_SECTION,
    )


# -- Seal the Charter --


def _sealed_key(character_id: str) -> str:
    return f"sealed_{character_id}"


def _until_label(standing: str | None) -> str:
    return "Expelled in" if standing == STANDING_EXPELLED else "Probation ends"


def seal_fields(saga: Saga, covenant: Covenant) -> list[DialogField]:
    """A tick, a season, a year and a standing for each of the covenant's
    magi (and any who sealed it and have left since); a probationary
    member's end of probation, an expelled one's expulsion."""
    charter = cc.charter_of(covenant)
    found: list[DialogField] = [
        DialogField(
            "about",
            "Seals",
            "info",
            "Each member's seal or signature is affixed to the charter, to "
            "show he agrees to it. A charter may have full and associate "
            f"members, and a probation before full membership ({COV} p. 33).",
        )
    ]
    for shown in cc.seals(saga, covenant):
        cid = shown.character.id
        seal = shown.seal
        key = _sealed_key(cid)

        def ticked(values: dict[str, Any], key: str = key) -> bool:
            return bool(values.get(key))

        def dated(values: dict[str, Any], key: str = key, cid: str = cid) -> bool:
            return bool(values.get(key)) and values.get(f"standing_{cid}") in (
                STANDING_PROBATION,
                STANDING_EXPELLED,
            )

        until_year, until_season = (
            (seal.until_year, seal.until_season) if seal else (None, "")
        )
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
            DialogField(
                f"standing_{cid}",
                "Standing",
                "select",
                seal.standing if seal else STANDING_FULL,
                options=pairs(STANDINGS),
                show_if=ticked,
            ),
            DialogField(
                f"until_season_{cid}",
                "Until",
                "select",
                until_season or None,
                options=pairs(SEASONS),
                allow_blank=True,
                show_if=dated,
                hint="A probation's end (blank: the charter's term from his "
                "sealing), or when he was expelled.",
            ),
            DialogField(
                f"until_year_{cid}", "Year", "optint", until_year, show_if=dated
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


def _seal_from(
    covenant: Covenant, cid: str, values: dict[str, Any]
) -> CharterSeal | None:
    """The seal the form's values give the magus (None: not sealed)."""
    if not values.get(_sealed_key(cid)):
        return None
    charter = cc.charter_of(covenant)
    year = values.get(f"year_{cid}")
    season = values.get(f"season_{cid}") or ""
    standing = values.get(f"standing_{cid}") or STANDING_FULL
    until_year, until_season = None, ""
    if standing in (STANDING_PROBATION, STANDING_EXPELLED):
        until_year = values.get(f"until_year_{cid}")
        until_season = values.get(f"until_season_{cid}") or ""
        if standing == STANDING_PROBATION and until_year is None:
            until_year, until_season = cc.probation_end(charter, year, season)
    return CharterSeal(cid, year, season, standing, until_year, until_season)


def seal_live(saga: Saga, covenant: Covenant) -> Callable[[dict[str, Any]], str]:
    """The form's inspector: who will have sealed it, and who not."""

    def inspect(values: dict[str, Any]) -> str:
        done: list[str] = []
        waiting: list[str] = []
        out: list[str] = []
        for shown in cc.seals(saga, covenant):
            cid = shown.character.id
            name = escape(shown.character.name)
            seal = _seal_from(covenant, cid, values)
            if seal is None:
                waiting.append(name)
                continue
            notes = [cc.when(seal.year, seal.season)]
            notes = [n for n in notes if n != "—"]
            if words := cc.standing_words(seal):
                notes.append(words)
            shown_name = name + (
                f" [dim]({escape(', '.join(notes))})[/]" if notes else ""
            )
            (out if seal.standing == STANDING_EXPELLED else done).append(shown_name)
        lines = [
            f"[b]{escape(cc.charter_title(cc.charter_of(covenant)))}[/]",
            f"[$label]Sealed by:[/] {', '.join(done) or '[dim]no one yet[/]'}",
        ]
        if waiting:
            lines.append(f"[$label]Not yet sworn:[/] {', '.join(waiting)}")
        if out:
            lines.append(f"[$label]Expelled:[/] {', '.join(out)}")
        return "\n".join(lines)

    return inspect


def seal_form(saga: Saga, covenant: Covenant) -> Form | Refuse:
    """More's Seal the Charter: which of the covenant's magi have sealed
    it, when, and in what standing."""
    if not cc.seals(saga, covenant):
        return Refuse(
            "Seal the Charter", "The covenant has no magi yet to seal its charter."
        )
    charter = cc.charter_of(covenant)

    def apply(values: dict[str, Any]) -> None:
        kept: list[CharterSeal] = []
        for shown in cc.seals(saga, covenant):
            if (seal := _seal_from(covenant, shown.character.id, values)) is not None:
                kept.append(seal)
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


# -- End Membership: the expelled who are still of the covenant --


def _membership_entry(
    saga: Saga, covenant: Covenant, character: Character, why: str
) -> None:
    covenant.diary.append(
        CovenantDiaryEntry(
            saga.current_year,
            saga.current_season,
            name=f"{character.name} left the covenant",
            details=f"{why[:1].upper()}{why[1:]}.",
            category="Membership",
        )
    )


def end_membership(saga: Saga, covenant: Covenant, character: Character) -> None:
    """Take the expelled magus off the covenant's lists and out of it,
    with a line in its Diary. His seal stays on the charter, struck."""
    leave_covenant(saga, character)
    _membership_entry(saga, covenant, character, "expelled under its charter")


def membership_fields(saga: Saga, covenants: list[Covenant]) -> list[DialogField]:
    found = [
        DialogField(
            "about",
            "",
            "info",
            "Expelled under the charter, but still of the covenant here. Tick "
            "those to take off its lists now; leave one unticked to do your "
            "own bookkeeping first (you'll be asked again when the next "
            "season is played).",
        )
    ]
    for covenant in covenants:
        for magus in cc.still_resident(saga, covenant):
            found.append(
                DialogField(
                    f"end_{covenant.id}_{magus.id}",
                    f"{magus.name} ({covenant.name})",
                    "check",
                    True,
                )
            )
    return found


def membership_form(
    saga: Saga, covenants: list[Covenant], then: Callable[[], Any] | None = None
) -> Form:
    """End Membership for the expelled magi of `covenants` still among
    their magi; `then` runs after (the season played out)."""

    def apply(values: dict[str, Any]) -> Any:
        for covenant in covenants:
            for magus in cc.still_resident(saga, covenant):
                if values.get(f"end_{covenant.id}_{magus.id}"):
                    end_membership(saga, covenant, magus)
        return then() if then is not None else None

    return Form(
        END_MEMBERSHIP,
        lambda: membership_fields(saga, covenants),
        apply,
        save_label="Continue" if then is not None else "End Membership",
        help_id=CHARTER_SECTION,
    )


def can_end_membership(saga: Saga, covenant: Covenant) -> bool:
    return bool(cc.still_resident(saga, covenant))


def end_membership_step(saga: Saga, covenant: Covenant) -> Command:
    """More's End Membership on the charter."""
    if not can_end_membership(saga, covenant):
        return Refuse(
            END_MEMBERSHIP,
            "No magus expelled under the charter is still of the covenant.",
        )
    return membership_form(saga, [covenant])


def season_reminder(saga: Saga, then: Callable[[], Any]) -> Any:
    """When a season is played: End Membership for every covenant's
    expelled magi still among its magi, then `then()`; just `then()` when
    there are none."""
    found = [c for c in saga.covenants if cc.still_resident(saga, c)]
    if not found:
        return then()
    return membership_form(saga, found, then)


# -- the templates: Use, Save and Forget --


def _template_label(saga: Saga, covenant: Covenant, template_id: str) -> str:
    template = charter_templates.find(saga, template_id)
    if template is None:
        return template_id
    key = charter_templates.tribunal_key(saga, covenant)
    if template.tribunal:
        whose = tp.PACKAGES.get(template.tribunal)
        where = whose.name if whose is not None else template.tribunal
        mark = "" if template.tribunal == key else ", another Tribunal's"
        return f"{template.name} ({where}{mark})"
    return f"{template.name} (any Tribunal)"


def use_fields(saga: Saga, covenant: Covenant) -> list[DialogField]:
    charter = cc.charter_of(covenant)
    offered = charter_templates.offered(saga, covenant)
    found = [
        DialogField(
            "template",
            "Template",
            "select",
            offered[0].id if offered else None,
            options=[(_template_label(saga, covenant, t.id), t.id) for t in offered],
            required=True,
        ),
        DialogField(
            "year",
            "Sworn in the year",
            "optint",
            charter.year if charter.year is not None else saga.current_year,
        ),
    ]
    if charter.clauses or charter.preamble.strip():
        found.append(
            DialogField(
                "_replaces",
                "",
                "info",
                f"The charter's preamble and its {len(charter.clauses)} clauses are "
                "replaced by the template's; its seals and Official Seal stay.",
            )
        )
    return found


def use_live(saga: Saga, covenant: Covenant) -> Callable[[dict[str, Any]], str]:
    def inspect(values: dict[str, Any]) -> str:
        template = charter_templates.find(saga, values.get("template") or "")
        if template is None:
            return "[dim]Choose a template.[/]"
        made = charter_templates.drawn(saga, covenant, template, values.get("year"))
        sections = [name for name, _found in cc.grouped(made) if name]
        lines = [
            f"[b]{escape(made.name)}[/]"
            + (f"  [dim]{escape(template.source)}[/]" if template.source else ""),
            f"{len(made.clauses)} clauses"
            + (f" under {', '.join(sections)}" if sections else ""),
        ]
        if template.probation_seasons is not None:
            lines.append(f"Probation: {template.probation_seasons} seasons.")
        if template.ratified_unaltered:
            lines.append(
                "[dim]Quaesitores ratify it at once while it is used unaltered "
                f"({COV} p. 33); an amended or broken clause ends that.[/]"
            )
        if made.preamble.strip():
            lines.append(f"[i]{escape(made.preamble.strip()[:240])}…[/]")
        return "\n".join(lines)

    return inspect


def use_template(saga: Saga, covenant: Covenant) -> Form:
    """More's Use a Template: draw the covenant's charter from one."""

    def apply(values: dict[str, Any]) -> None:
        template = charter_templates.find(saga, values.get("template") or "")
        if template is None:
            raise ValueError("That template is no longer in the saga.")
        charter_templates.use(saga, covenant, template, values.get("year"))

    return Form(
        USE_TEMPLATE,
        lambda: use_fields(saga, covenant),
        apply,
        live=use_live(saga, covenant),
        inspector="The Template",
        save_label="Use",
        help_id=CHARTER_SECTION,
    )


ANY_TRIBUNAL = "any"


def save_fields(saga: Saga, covenant: Covenant) -> list[DialogField]:
    key = charter_templates.tribunal_key(saga, covenant)
    # The core rules have no customs of their own to suit.
    key = "" if key == tp.CORE.key else key
    return [
        DialogField(
            "name",
            "Name",
            "text",
            f"{cc.charter_title(cc.charter_of(covenant))}",
            required=True,
            hint="A template of the same name is replaced.",
        ),
        DialogField(
            "tribunal",
            "Suits",
            "select",
            key or ANY_TRIBUNAL,
            options=[("Any Tribunal", ANY_TRIBUNAL)]
            + [
                (p.name, p.key)
                for p in tp.offered(saga, key or None)
                if p.key != "core"
            ],
            required=True,
            hint="A covenant of that Tribunal's customs sees it first.",
        ),
        DialogField(
            "_about",
            "",
            "info",
            f"Its {len(cc.charter_of(covenant).clauses)} clauses and preamble are "
            "kept with the saga; the covenant's and its Tribunal's names become "
            "blanks, filled in when another covenant uses it.",
        ),
    ]


def save_template(saga: Saga, covenant: Covenant) -> Form | Refuse:
    """More's Save as Template: keep the charter to start others from."""
    charter = cc.charter_of(covenant)
    if not charter.clauses and not charter.preamble.strip():
        return Refuse(SAVE_TEMPLATE, "The charter has no preamble or clauses to keep.")

    def apply(values: dict[str, Any]) -> list[str]:
        tribunal = values.get("tribunal") or ANY_TRIBUNAL
        made = charter_templates.save_as(
            saga,
            covenant,
            (values.get("name") or "").strip(),
            "" if tribunal == ANY_TRIBUNAL else tribunal,
        )
        return [f"Saved {made.name} as a charter template."]

    return Form(
        SAVE_TEMPLATE,
        lambda: save_fields(saga, covenant),
        apply,
        save_label="Save",
        help_id=CHARTER_SECTION,
    )


def forget_template(saga: Saga) -> Form | Refuse:
    """More's Forget a Template: drop one the troupe saved."""
    if not saga.charter_templates:
        return Refuse(
            FORGET_TEMPLATE, "The saga keeps no charter templates of its own."
        )

    def apply(values: dict[str, Any]) -> None:
        charter_templates.forget(saga, values.get("template") or "")

    return Form(
        FORGET_TEMPLATE,
        lambda: [
            DialogField(
                "template",
                "Template",
                "select",
                saga.charter_templates[0].id,
                options=[(t.name, t.id) for t in saga.charter_templates],
                required=True,
                hint="Charters drawn from it keep their clauses.",
            )
        ],
        apply,
        save_label="Forget",
        help_id=CHARTER_SECTION,
    )


def charter_ops(saga: Saga, covenant: Covenant) -> dict[str, SectionOps]:
    """The Charter section's Edit, and the Clauses section's Add, Edit
    and Delete, by section id (as a sheet's core_ops keeps them)."""
    return {
        CHARTER_SECTION: SectionOps(
            edit=lambda _row: charter_form(saga, covenant),
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
        censure=(existing.censure if existing else None)
        if status == CLAUSE_BROKEN
        else None,
    )


def clause_live(
    saga: Saga, covenant: Covenant, index: int | None
) -> Callable[[dict[str, Any]], str]:
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
        if glossed := cc.gloss(draft, cc.binding(saga, covenant)):
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


def _clause(covenant: Covenant, index: int | None) -> CharterClause | None:
    clauses = cc.charter_of(covenant).clauses
    return clauses[index] if index is not None and 0 <= index < len(clauses) else None


def can_break(covenant: Covenant, index: int | None) -> bool:
    """Whether Break a Clause is offered: on a clause not broken yet."""
    clause = _clause(covenant, index)
    return clause is not None and clause.status != CLAUSE_BROKEN


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


def break_live(
    saga: Saga, covenant: Covenant, clause: CharterClause
) -> Callable[[dict[str, Any]], str]:
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
                "[dim]It stays in the charter, struck through. More's "
                "Censure then says what the covenant does about it.[/]",
                cc.gloss(draft, cc.binding(saga, covenant)),
            ]
        )

    return inspect


def break_clause(saga: Saga, covenant: Covenant, index: int | None) -> Command:
    """More's Break a Clause on the chosen clause: when, and how."""
    clause = _clause(covenant, index)
    if clause is None or clause.status == CLAUSE_BROKEN:
        return Refuse(
            "Break a Clause", "Choose a clause of the charter that isn't broken yet."
        )

    def apply(values: dict[str, Any]) -> None:
        clause.status = CLAUSE_BROKEN
        clause.since_season = values.get("season") or ""
        clause.since_year = values.get("year")
        clause.note = values.get("note") or ""

    return Form(
        f"Break a Clause: {escape(cc.clause_name(clause))}",
        lambda: break_fields(saga),
        apply,
        live=break_live(saga, covenant, clause),
        save_label="Break",
        help_id=CLAUSES_SECTION,
        inspector="The Clause Struck",
    )


# -- Censure --


def can_censure(covenant: Covenant, index: int | None) -> bool:
    """Whether Censure is offered: on a broken clause."""
    clause = _clause(covenant, index)
    return clause is not None and clause.status == CLAUSE_BROKEN


def _withheld_key(privilege: str) -> str:
    return "withheld_" + privilege.lower().replace(",", "").replace(" ", "_")


def _withholds(values: dict[str, Any]) -> bool:
    return values.get("penalty") == CENSURE_WITHHELD


def _members(saga: Saga, covenant: Covenant) -> list[Character]:
    return [s.character for s in cc.seals(saga, covenant) if not s.expelled]


def censure_fields(
    saga: Saga, covenant: Covenant, clause: CharterClause
) -> list[DialogField]:
    c = clause.censure
    members = _members(saga, covenant)
    # One already censured (expelled, perhaps) stays choosable.
    if c is not None and (was := saga.character(c.character_id)) is not None:
        members += [was] if was not in members else []
    whom = c.character_id if c else (members[0].id if members else None)
    found = [
        DialogField(
            "whom",
            "Whom",
            "select",
            whom,
            options=[(m.name, m.id) for m in members],
            required=True,
        ),
        DialogField(
            "penalty",
            "Penalty",
            "select",
            c.penalty if c else CENSURE_WITHHELD,
            options=pairs(CENSURES),
            required=True,
            hint=f"Privileges the covenant holds in common, withheld until he "
            f"makes amends; his standing lowered; or expulsion ({COV} pp. 35-36).",
        ),
    ]
    found += [
        DialogField(
            _withheld_key(p),
            p,
            "check",
            bool(c and p in c.withheld),
            show_if=_withholds,
        )
        for p in PRIVILEGES
    ]
    found += [
        DialogField(
            "season",
            "Censured in",
            "select",
            (c.season if c else saga.current_season) or None,
            options=pairs(SEASONS),
            allow_blank=True,
        ),
        DialogField("year", "Year", "optint", c.year if c else saga.current_year),
        DialogField(
            "until_season",
            "Until",
            "select",
            (c.until_season if c else "") or None,
            options=pairs(SEASONS),
            allow_blank=True,
            show_if=_withholds,
            hint="Blank: until he makes amends.",
        ),
        DialogField(
            "until_year",
            "Year",
            "optint",
            c.until_year if c else None,
            show_if=_withholds,
        ),
        DialogField("note", "Note", "area", c.note if c else ""),
    ]
    return found


def _censure_from(values: dict[str, Any], before: Censure | None) -> Censure:
    penalty = values.get("penalty") or CENSURE_WITHHELD
    withholds = penalty == CENSURE_WITHHELD
    return Censure(
        values.get("whom") or "",
        penalty,
        [p for p in PRIVILEGES if values.get(_withheld_key(p))] if withholds else [],
        values.get("year"),
        values.get("season") or "",
        values.get("until_year") if withholds else None,
        (values.get("until_season") or "") if withholds else "",
        values.get("note") or "",
        before.case_id if before else "",
    )


#: A lowered standing: a full member to probation, any other to a
#: Protected Guest (the Charter of Arae Flaviae's censure, Covenants p. 128).
LOWERED = {
    STANDING_FULL: STANDING_PROBATION,
    STANDING_ASSOCIATE: STANDING_GUEST,
    STANDING_PROBATION: STANDING_GUEST,
    STANDING_GUEST: STANDING_GUEST,
}


def _standing_change(
    saga: Saga, covenant: Covenant, censure: Censure
) -> tuple[str, str] | None:
    """The standing the censure gives the magus's seal, from what it is
    ((before, after)); None when it changes nothing."""
    seal = cc.seal_of(cc.charter_of(covenant), censure.character_id)
    before = seal.standing if seal else STANDING_FULL
    if censure.penalty == CENSURE_EXPELLED:
        after = STANDING_EXPELLED
    elif censure.penalty == CENSURE_LOWERED:
        after = LOWERED.get(before, before)
    else:
        return None
    return None if after == before else (before, after)


def censure_live(
    saga: Saga, covenant: Covenant, clause: CharterClause
) -> Callable[[dict[str, Any]], str]:
    def inspect(values: dict[str, Any]) -> str:
        if not values.get("whom"):
            return "[dim]Choose whom the covenant censures.[/]"
        censure = _censure_from(values, clause.censure)
        lines = [
            f"[b]{escape(cc.clause_name(clause))}[/]",
            escape(cc.censure_words(saga, censure)),
        ]
        if change := _standing_change(saga, covenant, censure):
            lines.append(f"His seal: {escape(change[0])} → {escape(change[1])}.")
        if warning := cc.personal_warning(censure.withheld):
            lines.append(f"[$text-warning]{escape(warning)}[/]")
        if censure.penalty == CENSURE_EXPELLED:
            lines.append(
                "[dim]Expulsion is the gravest censure: in most covenants only "
                f"a magus who betrays the charter is expelled ({COV} p. 35). You "
                "will be asked whether to take him off the covenant's lists now.[/]"
            )
        return "\n".join(lines)

    return inspect


def _restanding(saga: Saga, covenant: Covenant, censure: Censure) -> None:
    """Give the magus's seal the standing the censure leaves him in."""
    change = _standing_change(saga, covenant, censure)
    if change is None:
        return
    charter = cc.charter_of(covenant)
    seal = cc.seal_of(charter, censure.character_id)
    if seal is None:
        seal = CharterSeal(censure.character_id)
        charter.seals.append(seal)
    seal.standing = change[1]
    if seal.standing == STANDING_EXPELLED:
        seal.until_year, seal.until_season = censure.year, censure.season
    elif seal.standing == STANDING_PROBATION:
        seal.until_year, seal.until_season = cc.probation_end(
            charter, censure.year, censure.season
        )
    else:
        seal.until_year, seal.until_season = None, ""


def censure_clause(saga: Saga, covenant: Covenant, index: int | None) -> Command:
    """More's Censure on a broken clause: whom the covenant censured, and
    how. Expelling a magus still of the covenant then asks whether to end
    his membership now."""
    clause = _clause(covenant, index)
    if clause is None or clause.status != CLAUSE_BROKEN:
        return Refuse(CENSURE, "Choose a broken clause: only a breach is censured.")
    if not _members(saga, covenant):
        return Refuse(CENSURE, "The charter has no members to censure.")

    def apply(values: dict[str, Any]) -> Any:
        censure = _censure_from(values, clause.censure)
        clause.censure = censure
        _restanding(saga, covenant, censure)
        magus = saga.character(censure.character_id)
        if (
            censure.penalty == CENSURE_EXPELLED
            and magus is not None
            and magus.covenant_id == covenant.id
        ):
            return Then(
                Confirm(
                    f"{escape(magus.name)} is expelled. Take him off "
                    f"{escape(covenant.name)}'s lists now? Choose No to do it "
                    "yourself; you'll be asked again when the next season is "
                    "played while he is still of the covenant.",
                    lambda: end_membership(saga, covenant, magus),
                    yes_label="Remove",
                    title=END_MEMBERSHIP,
                )
            )
        return None

    return Form(
        f"{CENSURE}: {escape(cc.clause_name(clause))}",
        lambda: censure_fields(saga, covenant, clause),
        apply,
        live=censure_live(saga, covenant, clause),
        inspector="The Censure",
        save_label="Censure",
        help_id=CLAUSES_SECTION,
    )


# -- Charge at Tribunal --


def can_charge(saga: Saga, covenant: Covenant, index: int | None) -> bool:
    """Whether Charge at Tribunal is offered: on a broken clause of a
    charter that binds under the Peripheral Code, of a covenant in a
    Tribunal, not charged yet."""
    clause = _clause(covenant, index)
    return (
        clause is not None
        and clause.status == CLAUSE_BROKEN
        and not (clause.censure and clause.censure.case_id)
        and saga.tribunal(covenant.tribunal_id) is not None
        and cc.binding(saga, covenant)
    )


def charge_fields(
    saga: Saga, covenant: Covenant, clause: CharterClause
) -> list[DialogField]:
    c = clause.censure
    magi = [s.character for s in cc.seals(saga, covenant)]
    return [
        DialogField(
            "against",
            "Against",
            "select",
            c.character_id if c else (magi[0].id if magi else None),
            options=[(m.name, m.id) for m in magi],
            required=True,
        ),
        DialogField(
            "title",
            "Case",
            "text",
            f"{covenant.name}'s charter: {cc.clause_name(clause)}",
            required=True,
        ),
        DialogField(
            "charge",
            "Charge",
            "area",
            f"Breaking the charter of {covenant.name}, a Low Crime: "
            f"{clause.text.strip()}",
            required=True,
        ),
        DialogField(
            "evidence",
            "Evidence",
            "area",
            clause.note.strip(),
            hint="One short entry a line.",
        ),
    ]


def charge(saga: Saga, covenant: Covenant, index: int | None) -> Command:
    """More's Charge at Tribunal on a broken clause: a charge on the
    covenant's Tribunal's docket, brought by the covenant."""
    clause = _clause(covenant, index)
    if clause is None or not can_charge(saga, covenant, index):
        return Refuse(
            CHARGE,
            "Choose a broken clause of a charter that binds under the Peripheral "
            "Code (notarized, or sworn where the Tribunal makes it law), of a "
            "covenant in a Tribunal, not charged yet.",
        )
    tribunal = saga.tribunal(covenant.tribunal_id)
    assert tribunal is not None

    def apply(values: dict[str, Any]) -> list[str]:
        magus = saga.character(values.get("against") or "")
        case = Case(
            values.get("title") or "",
            kind="charge",
            brought_by=covenant.name,
            against=magus.name if magus is not None else "",
            charge=values.get("charge") or "",
            filed_year=saga.current_year,
            filed_season=saga.current_season,
            evidence=values.get("evidence") or "",
        )
        tribunal.cases.append(case)
        if clause.censure is None and magus is not None:
            clause.censure = Censure(
                magus.id,
                CENSURE_WITHHELD,
                year=saga.current_year,
                season=saga.current_season,
            )
        if clause.censure is not None:
            clause.censure.case_id = case.id
        return [f"{case.title} is on the docket of {tribunal.name}."]

    return Form(
        f"{CHARGE}: {escape(cc.clause_name(clause))}",
        lambda: charge_fields(saga, covenant, clause),
        apply,
        live=lambda _values: (
            f"[dim]{escape(cc.law_line(saga, covenant))} The case goes on "
            f"{escape(tribunal.name)}'s docket, to be heard at its next meeting.[/]"
        ),
        save_label="Charge",
        help_id=CLAUSES_SECTION,
    )
