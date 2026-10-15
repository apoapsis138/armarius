"""The forms for a Tribunal (New and Edit Tribunal), the choice of
Tribunal a covenant's forms share, and its sheet's lists: the proxies on
its roster, its cases, its Peripheral Code, its treasury and its Diary,
each with its Add, Edit and Delete (commands.SectionOps). Each form is a
list of form_spec.DialogFields inside a commands step, so either
front-end draws it."""

from __future__ import annotations

from dataclasses import replace as dataclass_replace
from typing import Any

from . import meeting, tribunal_packages, tribunal_sheet, tribunals
from .arts import ARTS
from .commands import (
    Choice,
    Choose,
    Command,
    Confirm,
    Form,
    Refuse,
    SectionOps,
    delete,
)
from .form_spec import DialogField, attr, pairs
from .markup import escape
from .models import (
    CASE_KINDS,
    CASE_OPEN,
    CASE_STATUSES,
    CASE_WITHDRAWN,
    SEASONS,
    TREASURY_KINDS,
    Case,
    Covenant,
    Ruling,
    Saga,
    TreasuryEntry,
    Tribunal,
    TribunalDiaryEntry,
)
from .sections import (
    CASES_SECTION,
    CODE_SECTION,
    PAST_CASES_SECTION,
    ROSTER_SECTION,
    TREASURY_SECTION,
    TRIB_DIARY_SECTION,
    TRIBUNAL_INFO_SECTION,
)


def tribunal_field(saga: Saga, tribunal_id: str | None) -> DialogField:
    """A covenant's choice of Tribunal, from the saga's."""
    return DialogField(
        "tribunal_id",
        "Tribunal",
        "select",
        tribunal_id,
        options=[(escape(label), ident) for label, ident in tribunals.options(saga)],
        allow_blank=True,
        placeholder="(no Tribunal)",
        hint="New Tribunal, in the New menu, adds one to choose."
        if not saga.tribunals
        else "",
    )


def package_fields(saga: Saga, covenant: Covenant | None) -> list[DialogField]:
    """What each Tribunal's customs add to a covenant's own form (the
    Rhine's gilds), each shown only while that Tribunal is chosen."""
    fields = []
    for tribunal in saga.tribunals:
        package = tribunal_packages.of(tribunal)
        if package.covenant_fields is None:
            continue
        for field in package.covenant_fields(saga, tribunal, covenant):
            fields.append(
                dataclass_replace(
                    field,
                    key=f"package_{tribunal.id}_{field.key}",
                    show_if=lambda values, ident=tribunal.id: (
                        values.get("tribunal_id") == ident
                    ),
                )
            )
    return fields


def save_package_fields(saga: Saga, covenant: Covenant, values: dict[str, Any]) -> None:
    """Take package_fields()' values out of `values` and keep them with
    the covenant's Tribunal."""
    for tribunal in saga.tribunals:
        prefix = f"package_{tribunal.id}_"
        own = {
            k[len(prefix) :]: values.pop(k)
            for k in list(values)
            if k.startswith(prefix)
        }
        package = tribunal_packages.of(tribunal)
        if (
            own
            and package.save_covenant is not None
            and tribunal.id == covenant.tribunal_id
        ):
            package.save_covenant(tribunal, covenant.id, own)


def _character_options(saga: Saga) -> list[tuple[str, str]]:
    return [(escape(c.name), c.id) for c in saga.characters]


def tribunal_fields(saga: Saga, tribunal: Tribunal | None) -> list[DialogField]:
    """New or Edit Tribunal: its name, when and where it next meets, its
    officers and how big it really is."""
    t = tribunal or Tribunal(id="", name="")
    officer = {"allow_blank": True, "placeholder": "(none chosen)"}
    return [
        DialogField("name", "Name", "text", t.name, required=True),
        DialogField(
            "package",
            "Customs",
            "select",
            t.package,
            options=[
                (escape(tribunal_packages.label(p)), p.key)
                for p in tribunal_packages.offered(saga, t.package)
            ],
            hint="Core rules, or a region's customs from a book in play. "
            "Switching keeps the other customs' records, hidden.",
        ),
        DialogField(
            "summary",
            "In the Saga",
            "area",
            t.summary,
            hint="A sentence or a paragraph: what the Tribunal is like.",
        ),
        DialogField(
            "history",
            "History",
            "area",
            t.history,
            hint="How it came to be, era by era: shown in its own History tab.",
        ),
        DialogField(
            "meets_every",
            "Meets every (years)",
            "int",
            t.meets_every,
        ),
        DialogField("next_year", "Next meeting (year)", "optint", t.next_year),
        DialogField(
            "next_season",
            "Next meeting (season)",
            "select",
            t.next_season,
            options=pairs(SEASONS),
        ),
        DialogField("meeting_place", "Meeting place", "text", t.meeting_place),
        DialogField(
            "praeco_id",
            "Praeco",
            "select",
            t.praeco_id,
            options=_character_options(saga),
            **officer,
        ),
        DialogField(
            "quaesitor_id",
            "Presiding Quaesitor",
            "select",
            t.quaesitor_id,
            options=_character_options(saga),
            **officer,
        ),
        DialogField(
            "covenants_total",
            "Covenants in all",
            "optint",
            t.covenants_total,
            hint="Most are never written down; blank counts only those that are.",
        ),
        DialogField("magi_total", "Magi in all", "optint", t.magi_total),
    ]


def tribunal_problem(values: dict[str, Any]) -> str | None:
    """Why the Tribunal's values can't be saved, if they can't."""
    if values.get("meets_every", 1) < 1:
        return "A Tribunal meets every year at the most often."
    for key, words in (("covenants_total", "Covenants"), ("magi_total", "Magi")):
        if (values.get(key) or 0) < 0:
            return f"{words} in all can't be fewer than none."
    return None


def _apply(tribunal: Tribunal, values: dict[str, Any]) -> None:
    for key, value in values.items():
        setattr(tribunal, key, value)
    tribunal.next_season = tribunal.next_season or "Summer"


def new_tribunal_form(saga: Saga) -> Form:
    def apply(values: dict[str, Any]) -> None:
        _apply(tribunals.add(saga, values["name"]), values)

    return Form(
        "Create a New Tribunal",
        lambda: tribunal_fields(saga, None),
        apply,
        validate=tribunal_problem,
        save_label="Create",
    )


def edit_tribunal_form(saga: Saga, tribunal: Tribunal) -> Form:
    return Form(
        "Edit Tribunal",
        lambda: tribunal_fields(saga, tribunal),
        lambda values: _apply(tribunal, values),
        validate=tribunal_problem,
    )


# -- the roster's proxies --


def _proxies_problem(values: dict[str, Any]) -> str | None:
    if (values.get("proxies") or 0) < 0:
        return "A covenant can't hold fewer than no proxies."
    return None


def roster_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    """The roster's Edit: the proxies the chosen covenant carries to the
    next meeting, and whatever the Tribunal's customs enter for it (its
    privilege class, in Transylvania). The unrecorded covenants' row
    holds none."""

    def edit(index: int) -> Command:
        members = tribunals.covenants_of(saga, tribunal)
        if index >= len(members):
            return Refuse(
                "Unnamed covenants",
                "Proxies are entered on a recorded covenant: record it to give "
                "it some.",
            )
        covenant = members[index]
        entered = [
            c for c in tribunal_packages.of(tribunal).columns if c.field is not None
        ]

        def fields() -> list[DialogField]:
            shown = [
                DialogField(
                    "proxies",
                    "Proxies held",
                    "int",
                    tribunal_sheet.proxies(tribunal, covenant),
                    hint="The sigils it carries for absent magi at the next "
                    "meeting: each is a vote.",
                )
            ]
            return shown + [
                c.field(saga, tribunal, covenant) for c in entered if c.field
            ]

        def apply(values: dict[str, Any]) -> None:
            held = values.get("proxies") or 0
            if held:
                tribunal.proxies[covenant.id] = held
            else:
                tribunal.proxies.pop(covenant.id, None)
            for column in entered:
                if column.field is not None and column.save is not None:
                    key = column.field(saga, tribunal, covenant).key
                    column.save(tribunal, covenant, values.get(key))

        name = escape(covenant.name)
        return Form(
            f"{name} at the Tribunal" if entered else f"Proxies held by {name}",
            fields,
            apply,
            validate=_proxies_problem,
        )

    return SectionOps(
        edit=edit, rows=lambda: tribunal_sheet.roster_names(saga, tribunal)
    )


# -- cases --


def case_fields(saga: Saga, case: Case | None) -> list[DialogField]:
    """A case on the docket. Status and outcome are a past case's, so
    only Edit offers them."""
    fields = [
        DialogField(
            "title",
            "Case",
            "text",
            attr(case, "title", ""),
            required=True,
            placeholder="e.g. Fengheld v. Arnhaven",
        ),
        DialogField(
            "kind",
            "Kind",
            "select",
            attr(case, "kind", "charge"),
            options=[(k.title(), k) for k in CASE_KINDS],
        ),
        DialogField("brought_by", "Brought by", "text", attr(case, "brought_by", "")),
        DialogField(
            "against",
            "Against",
            "text",
            attr(case, "against", ""),
            hint="A covenant or a magus; a case naming one of yours is flagged.",
        ),
        DialogField(
            "charge",
            "Charge",
            "area",
            attr(case, "charge", ""),
            placeholder="e.g. Depriving a magus of magical power (the Code)",
        ),
        DialogField(
            "filed_year",
            "Filed (year)",
            "optint",
            case.filed_year if case is not None else saga.current_year,
        ),
        DialogField(
            "filed_season",
            "Filed (season)",
            "select",
            (case.filed_season if case is not None else saga.current_season) or None,
            options=pairs(SEASONS),
            allow_blank=True,
        ),
        DialogField(
            "notice_given",
            "Notice given",
            "check",
            attr(case, "notice_given", False),
        ),
        DialogField(
            "penalty",
            "Sought",
            "text",
            attr(case, "penalty", ""),
            hint="What it asks the Tribunal to do: a penalty or a ruling.",
        ),
        DialogField(
            "evidence",
            "Evidence",
            "area",
            attr(case, "evidence", ""),
            hint="One piece a line.",
        ),
        DialogField("prosecutor", "Prosecutor", "text", attr(case, "prosecutor", "")),
        DialogField("defender", "Defender", "text", attr(case, "defender", "")),
    ]
    if case is not None:
        fields += [
            DialogField(
                "status",
                "Status",
                "select",
                case.status,
                options=pairs(CASE_STATUSES),
                hint="A decided or withdrawn case moves to the Rulings of Past "
                "Tribunals.",
            ),
            DialogField(
                "outcome",
                "Outcome",
                "text",
                case.outcome,
                show_if=lambda values: values.get("status") != CASE_OPEN,
            ),
        ]
    return fields


def _set_case(case: Case, values: dict[str, Any]) -> None:
    for key, value in values.items():
        setattr(case, key, value)
    case.filed_season = case.filed_season or ""


def _case_form(saga: Saga, tribunal: Tribunal, case: Case | None) -> Form:
    def apply(values: dict[str, Any]) -> None:
        if case is None:
            fresh = Case(values["title"])
            _set_case(fresh, values)
            tribunal.cases.append(fresh)
        else:
            _set_case(case, values)

    return Form(
        "Add a Case" if case is None else f"Edit {escape(case.title)}",
        lambda: case_fields(saga, case),
        apply,
        save_label="Add" if case is None else "Save",
    )


def _remove_case(tribunal: Tribunal, case: Case) -> Command:
    def apply() -> None:
        tribunal.cases.remove(case)
        for ruling in tribunal.rulings:
            if ruling.case_id == case.id:
                ruling.case_id = ""

    return Confirm(f"Delete the case {escape(case.title)}?", apply)


def case_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    """The cases still to be heard."""

    def cases() -> list[Case]:
        return tribunal_sheet.open_cases(tribunal)

    return SectionOps(
        add=lambda: _case_form(saga, tribunal, None),
        edit=lambda index: _case_form(saga, tribunal, cases()[index]),
        remove=lambda index: _remove_case(tribunal, cases()[index]),
        rows=lambda: [c.title for c in cases()],
    )


def past_case_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    """The cases decided or withdrawn: Edit (to correct one, or reopen it)
    and Delete."""

    def cases() -> list[Case]:
        return tribunal_sheet.closed_cases(tribunal)

    return SectionOps(
        edit=lambda index: _case_form(saga, tribunal, cases()[index]),
        remove=lambda index: _remove_case(tribunal, cases()[index]),
        rows=lambda: [c.title for c in cases()],
    )


def withdraw_case(tribunal: Tribunal, index: int) -> Command:
    """More's Withdraw on the chosen case: it leaves the docket, kept
    among the past rulings as withdrawn."""
    pending = tribunal_sheet.open_cases(tribunal)
    if index >= len(pending):
        return Refuse("Withdraw", "Choose a case on the docket first.")
    case = pending[index]

    def apply() -> None:
        case.status = CASE_WITHDRAWN

    return Confirm(
        f"Withdraw {escape(case.title)}? It leaves the docket and is kept "
        "among the Rulings of Past Tribunals as withdrawn.",
        apply,
        yes_label="Withdraw",
        title="Withdraw a Case",
    )


# -- the Peripheral Code --


def _case_options(tribunal: Tribunal) -> list[tuple[str, str]]:
    return [(escape(c.title), c.id) for c in tribunal.cases]


def ruling_fields(
    saga: Saga, tribunal: Tribunal, ruling: Ruling | None
) -> list[DialogField]:
    return [
        DialogField(
            "title",
            "Ruling",
            "text",
            attr(ruling, "title", ""),
            required=True,
            placeholder="e.g. Gild membership",
        ),
        DialogField(
            "year",
            "Year",
            "optint",
            ruling.year if ruling is not None else saga.current_year,
        ),
        DialogField("says", "What it says", "area", attr(ruling, "says", "")),
        DialogField(
            "case_id",
            "Case",
            "select",
            attr(ruling, "case_id", "") or None,
            options=_case_options(tribunal),
            allow_blank=True,
            placeholder="(none)",
        ),
    ]


def code_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    rulings = tribunal.rulings

    def form(ruling: Ruling | None) -> Form:
        def apply(values: dict[str, Any]) -> None:
            target = ruling if ruling is not None else Ruling(values["title"])
            target.title = values["title"]
            target.year = values.get("year")
            target.says = values.get("says", "")
            target.case_id = values.get("case_id") or ""
            if ruling is None:
                rulings.append(target)

        return Form(
            "Add a Ruling" if ruling is None else "Edit a Ruling",
            lambda: ruling_fields(saga, tribunal, ruling),
            apply,
            save_label="Add" if ruling is None else "Save",
        )

    return SectionOps(
        add=lambda: form(None),
        edit=lambda index: form(rulings[index]),
        remove=lambda index: delete(rulings, index, rulings[index].title),
        rows=lambda: [r.title for r in rulings],
    )


# -- the treasury --

#: Each kind of treasury entry, as Add offers it.
TREASURY_NOUNS: dict[str, str] = {
    "vis": "Vis",
    "silver": "Silver",
    "loan": "A loan",
    "fine": "A fine",
}

_TREASURY_HELP: dict[str, str] = {
    "vis": "Pawns of an Art in the treasury (or taken out of it).",
    "silver": "Pounds of silver in the treasury (or taken out of it).",
    "loan": "Silver or vis lent out of the treasury, owed back.",
    "fine": "A fine owed to the treasury, from a case.",
}


def treasury_fields(
    tribunal: Tribunal, kind: str, entry: TreasuryEntry | None
) -> list[DialogField]:
    """A treasury entry of `kind`: vis, silver, a loan or a fine."""
    amount_label = {
        "vis": "Pawns (+ in, − out)",
        "silver": "Pounds (+ in, − out)",
    }.get(kind, "Amount")
    fields = [DialogField("kind", "Entry", "info", TREASURY_NOUNS[kind])]
    if kind in ("loan", "fine"):
        fields.append(
            DialogField(
                "who",
                "To whom" if kind == "loan" else "Owed by",
                "text",
                attr(entry, "who", ""),
                required=True,
            )
        )
    fields.append(
        DialogField("amount", amount_label, "optfloat", attr(entry, "amount", None))
    )
    if kind != "silver":
        fields.append(
            DialogField(
                "art",
                "Art",
                "select",
                attr(entry, "art", "") or None,
                options=pairs(ARTS),
                required=kind == "vis",
                allow_blank=kind != "vis",
                placeholder="(silver)",
                hint="" if kind == "vis" else "Leave blank for pounds of silver.",
            )
        )
    if kind == "loan":
        fields += [
            DialogField(
                "due_year", "Due (year)", "optint", attr(entry, "due_year", None)
            ),
            DialogField("paid", "Repaid", "check", attr(entry, "paid", False)),
        ]
    if kind == "fine":
        fields += [
            DialogField(
                "case_id",
                "From the case",
                "select",
                attr(entry, "case_id", "") or None,
                options=_case_options(tribunal),
                allow_blank=True,
                placeholder="(none)",
            ),
            DialogField("paid", "Paid", "check", attr(entry, "paid", False)),
        ]
    fields.append(DialogField("note", "Note", "text", attr(entry, "note", "")))
    return fields


def _treasury_problem(values: dict[str, Any]) -> str | None:
    if not values.get("amount"):
        return "Say how much: an amount can't be nothing."
    return None


def _treasury_form(tribunal: Tribunal, kind: str, entry: TreasuryEntry | None) -> Form:
    def apply(values: dict[str, Any]) -> None:
        target = entry if entry is not None else TreasuryEntry(kind)
        target.amount = values.get("amount") or 0
        target.art = values.get("art") or ""
        target.who = values.get("who", "")
        target.due_year = values.get("due_year")
        target.case_id = values.get("case_id") or ""
        target.paid = bool(values.get("paid", False))
        target.note = values.get("note", "")
        if entry is None:
            tribunal.treasury.append(target)

    noun = TREASURY_NOUNS[kind].removeprefix("A ")
    return Form(
        f"Add {noun}" if entry is None else f"Edit {noun}",
        lambda: treasury_fields(tribunal, kind, entry),
        apply,
        validate=_treasury_problem,
        save_label="Add" if entry is None else "Save",
    )


def treasury_ops(tribunal: Tribunal) -> SectionOps:
    """Add chooses the kind of entry first, then fills in its form."""
    entries = tribunal.treasury

    def add() -> Command:
        return Choose(
            "Add to the Treasury",
            lambda: [
                Choice(TREASURY_NOUNS[kind], kind, _TREASURY_HELP[kind])
                for kind in TREASURY_KINDS
            ],
            lambda kind: _treasury_form(tribunal, kind, None),
        )

    def edit(index: int) -> Command:
        entry = entries[index]
        return _treasury_form(tribunal, entry.kind, entry)

    return SectionOps(
        add=add,
        edit=edit,
        remove=lambda index: delete(
            entries, index, tribunal_sheet.amount_text(entries[index])
        ),
        rows=lambda: [
            f"{e.kind.title()} {tribunal_sheet.amount_text(e)}" for e in entries
        ],
    )


# -- the Diary --


def diary_fields(saga: Saga, entry: TribunalDiaryEntry | None) -> list[DialogField]:
    return [
        DialogField(
            "year",
            "Year",
            "int",
            entry.year if entry is not None else saga.current_year,
        ),
        DialogField(
            "season",
            "Season",
            "select",
            (entry.season if entry is not None else saga.current_season) or None,
            options=pairs(SEASONS),
            allow_blank=True,
        ),
        DialogField(
            "title",
            "Entry",
            "text",
            attr(entry, "title", ""),
            required=True,
            placeholder="e.g. The Tribunal of 1221",
        ),
        DialogField(
            "margin",
            "Numbers",
            "text",
            attr(entry, "margin", ""),
            hint='Set in the margin, e.g. "23 votes, 3 by proxy".',
        ),
        DialogField("details", "Details", "area", attr(entry, "details", "")),
    ]


def diary_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    diary = tribunal.diary

    def form(entry: TribunalDiaryEntry | None) -> Form:
        def apply(values: dict[str, Any]) -> None:
            target = entry if entry is not None else TribunalDiaryEntry(values["year"])
            target.year = values["year"]
            target.season = values.get("season") or ""
            target.title = values["title"]
            target.margin = values.get("margin", "")
            target.details = values.get("details", "")
            if entry is None:
                diary.append(target)

        return Form(
            "Add a Diary Entry" if entry is None else "Edit a Diary Entry",
            lambda: diary_fields(saga, entry),
            apply,
            save_label="Add" if entry is None else "Save",
        )

    return SectionOps(
        add=lambda: form(None),
        edit=lambda index: form(diary[index]),
        remove=lambda index: delete(diary, index, diary[index].title or "this entry"),
        rows=lambda: [e.title or "(untitled)" for e in diary],
    )


def tribunal_ops(saga: Saga, tribunal: Tribunal) -> dict[str, SectionOps]:
    """Every section of a Tribunal's sheet the core edits, by id."""
    ops: dict[str, SectionOps] = {
        TRIBUNAL_INFO_SECTION: SectionOps(
            edit=lambda _row: edit_tribunal_form(saga, tribunal)
        ),
        ROSTER_SECTION: roster_ops(saga, tribunal),
        CASES_SECTION: case_ops(saga, tribunal),
        PAST_CASES_SECTION: past_case_ops(saga, tribunal),
        CODE_SECTION: code_ops(saga, tribunal),
        TREASURY_SECTION: treasury_ops(tribunal),
        TRIB_DIARY_SECTION: diary_ops(saga, tribunal),
    }
    for extra in tribunal_packages.of(tribunal).lists:
        ops[extra.section_id] = extra.ops(saga, tribunal)
    ops.update(meeting.ops(saga, tribunal))
    return ops
