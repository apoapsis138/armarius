"""A covenant's own forms, independent of how they are drawn: Edit
Covenant and its Description, the Boons and Hooks (add from the catalog,
edit, delete), and the Treasury's Wealth, Sources of Income and the
Yearly Expenditure and Cost Savings rows.

Inhabitants are in inhabitant_forms.py, possessions in
possession_forms.py, the library's books in library_forms.py and the
Diary in diary_forms.py.
"""

from __future__ import annotations

from typing import Any

from . import boon_hook_text, catalog, sourcebooks
from . import covenants as cov_rules
from . import economics as eco
from .commands import Choice, Choose, Confirm, Form, SectionOps, notes
from .covenants import boon_hook_is_unknown
from .form_spec import EMPHASIS_HINT, DialogField, description_field, pairs
from .markup import escape
from .models import (
    BOON_HOOK_DESCRIPTION,
    BOON_HOOK_DETAIL,
    BOON_HOOK_RESOURCE,
    INCOME_TYPE_DEFAULTS,
    INCOME_TYPES,
    REALMS,
    SEASONS,
    Covenant,
    CovenantBoonHookDef,
    IncomeSource,
    Saga,
    VirtueFlawInstance,
    boon_hook_params,
    new_instance_id,
)
from .possession_forms import contested_fields

# Edit Covenant and its Description

#: Edit Covenant's whole-number fields after Year Founded, as (attribute,
#: label).
_COVENANT_INT_FIELDS: tuple[tuple[str, str], ...] = (
    ("aegis_of_the_hearth", "Aegis of the Hearth"),
    ("aegis_penetration", "Aegis' Penetration"),
    ("living_conditions_magi", "Living Conditions (Magi)"),
    ("living_conditions_mundane", "Living Conditions (Mundane)"),
    ("aura", "Aura"),
)


def covenant_fields(covenant: Covenant) -> list[DialogField]:
    """Edit Covenant: its name, Tribunal, founding, Aegis, living
    conditions, aura and season."""
    cov = covenant
    return [
        DialogField("name", "Name", "text", cov.name, required=True),
        DialogField("tribunal", "Tribunal", "text", cov.tribunal),
        DialogField("year_founded", "Year Founded", "optint", cov.year_founded),
        *(
            DialogField(
                attribute,
                label,
                "int",
                getattr(cov, attribute),
                hint=(
                    "The base aura of every laboratory in this covenant."
                    if attribute == "aura"
                    else ""
                ),
            )
            for attribute, label in _COVENANT_INT_FIELDS
        ),
        DialogField(
            "aura_realm",
            "Aura Realm",
            "select",
            cov.aura_realm,
            options=pairs(REALMS),
            hint="Hermetic magic gains the full aura only in a Magic aura.",
        ),
        DialogField(
            "covenant_season",
            "Covenant Season",
            "select",
            cov.covenant_season,
            options=pairs(SEASONS),
        ),
        DialogField(
            "played",
            "Played by the troupe",
            "check",
            cov.played,
            hint="A player covenant: other records' attitudes point at it.",
        ),
    ]


def apply_covenant(covenant: Covenant, values: dict[str, Any]) -> None:
    for attribute, value in values.items():
        setattr(covenant, attribute, value)


def covenant_form(covenant: Covenant) -> Form:
    return Form(
        "Edit Covenant",
        lambda: covenant_fields(covenant),
        lambda values: apply_covenant(covenant, values),
    )


def description_fields(covenant: Covenant) -> list[DialogField]:
    return [
        DialogField("notes", "Description", "area", covenant.notes, hint=EMPHASIS_HINT)
    ]


def description_form(covenant: Covenant) -> Form:
    def apply(values: dict[str, Any]) -> None:
        covenant.notes = values["notes"]

    return Form(
        "Edit Covenant Description", lambda: description_fields(covenant), apply
    )


# Boons and Hooks


def boon_hook_fields(
    detail: str = "",
    description: str = "",
    *,
    can_be_unknown: bool = False,
    unknown: bool = False,
    sources: list[tuple[str, str]] | None = None,
    source: str = "",
) -> list[DialogField]:
    """A covenant Boon's or Hook's own Detail (shown in the list) and
    Description (shown ahead of the rules text); both optional. A Minor
    Hook that may be Unknown also gets an Unknown checkbox, and a Resource
    Hook (`sources` given: (label, id) pairs) the vis or income source it is
    about, `source` now."""
    source_fields = (
        [
            DialogField(
                "resource",
                "About which source",
                "select",
                source or None,
                options=list(sources),
                allow_blank=True,
                placeholder="(not yet)",
                hint="Marks that source Contested or Dwindling. It can wait "
                "until the source exists."
                if sources
                else "Add the vis or income source first, then choose it here.",
            )
        ]
        if sources is not None
        else []
    )
    unknown_fields = (
        [
            DialogField(
                "unknown",
                "Unknown",
                "check",
                unknown,
                hint="Only the player who storyguides it knows it; "
                "counts 3 points, as a Major Hook.",
            )
        ]
        if can_be_unknown
        else []
    )
    return (
        unknown_fields
        + source_fields
        + [
            DialogField(
                "detail",
                "Detail",
                "text",
                detail,
                placeholder="e.g. the specific building or resource",
            ),
            DialogField(
                "description", "Description", "area", description, hint=EMPHASIS_HINT
            ),
        ]
    )


#: Each kind's section id.
BOON_HOOK_SECTIONS: dict[str, str] = {
    "Boon": "section-cov-boons",
    "Hook": "section-cov-hooks",
}


def attached(covenant: Covenant, kind: str) -> list[int]:
    """The indexes into covenant.boons_hooks of its Boons or Hooks (`kind`),
    in the order attached (as the section lists them)."""
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    return [
        index
        for index, bh in enumerate(covenant.boons_hooks)
        if bh.vf_id in by_id and by_id[bh.vf_id].type == kind
    ]


def boon_hook_choice_label(entry: CovenantBoonHookDef, taken: int) -> str:
    """A catalog Boon or Hook as Add lists it: its name, type, tier and
    cost, what it needs or rules out, and how often it is taken already."""
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    facts = [entry.category] if entry.category else []
    facts.append(entry.tier)
    if entry.cost:
        facts.append(f"{abs(entry.cost):g} pt")
    label = f"{entry.name}  \\[{', '.join(facts)}]"
    if entry.requires:
        label += (
            f"  (requires: {boon_hook_text.boon_hook_names(entry.requires, by_id)})"
        )
    if entry.requires_any:
        names = boon_hook_text.boon_hook_names(entry.requires_any, by_id)
        label += f"  (requires one of: {names})"
    if entry.excludes:
        label += (
            f"  (not with: {boon_hook_text.boon_hook_names(entry.excludes, by_id)})"
        )
    if entry.unknown:
        label += "  (may be Unknown)"
    if taken:
        label += f"  (taken x{taken})"
    return label


def boon_hook_choices(saga: Saga, covenant: Covenant, kind: str) -> list[Choice]:
    """The catalog's Boons or Hooks from books in play (and not hidden), in
    the book's order. One already attached can be taken again."""
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    books = sourcebooks.saga_books(saga)
    taken = [bh.vf_id for bh in covenant.boons_hooks]
    entries = sorted(
        (
            e
            for e in by_id.values()
            if e.type == kind
            and sourcebooks.in_play(e.source, books)
            and not catalog.hidden(e)
        ),
        key=catalog.boon_hook_sort_key,
    )
    return [
        Choice(
            boon_hook_choice_label(e, taken.count(e.id)),
            e,
            boon_hook_text.boon_hook_entry_text(e, by_id),
            f"{e.name} {e.category} {e.tier} {e.description}",
        )
        for e in entries
    ]


def add_boon_hook(saga: Saga, covenant: Covenant, kind: str) -> Choose:
    """Choose a Boon or Hook from the catalog, then name what it applies to."""

    def details(entry: CovenantBoonHookDef) -> Form:
        def apply(values: dict[str, Any]) -> list[str]:
            params = boon_hook_params(
                values["detail"],
                values["description"],
                unknown=values.get("unknown", False),
            )
            covenant.boons_hooks.append(
                VirtueFlawInstance(vf_id=entry.id, params=params, id=new_instance_id())
            )
            return notes(
                "Link this Hook to the vis or income source it is about "
                "(Edit on it, under Boons & Hooks), once that source exists."
                if entry.id in cov_rules.RESOURCE_HOOKS
                else ""
            )

        return Form(
            f"{kind}: {escape(entry.name)}",
            lambda: boon_hook_fields(can_be_unknown=entry.unknown),
            apply,
        )

    return Choose(
        f"Add a {kind}",
        lambda: boon_hook_choices(saga, covenant, kind),
        details,
        empty=f"(no more {kind}s available)",
    )


def edit_boon_hook(covenant: Covenant, index: int) -> Form:
    """The Boon or Hook at `index` (into covenant.boons_hooks): its detail,
    description, whether it is Unknown and, for a Resource Hook, which
    source it is about."""
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    instance = covenant.boons_hooks[index]
    definition = by_id[instance.vf_id]

    def apply(values: dict[str, Any]) -> None:
        instance.params = boon_hook_params(
            values["detail"],
            values["description"],
            instance.params,
            unknown=values.get("unknown", False),
        )
        if "resource" in values:
            cov_rules.link_resource(covenant, instance, values["resource"] or "")

    return Form(
        f"{definition.type}: {escape(definition.name)}",
        lambda: boon_hook_fields(
            instance.params.get(BOON_HOOK_DETAIL, ""),
            instance.params.get(BOON_HOOK_DESCRIPTION, ""),
            can_be_unknown=definition.unknown,
            unknown=boon_hook_is_unknown(instance, definition),
            sources=(
                cov_rules.resource_sources(covenant)
                if instance.vf_id in cov_rules.RESOURCE_HOOKS
                else None
            ),
            source=instance.params.get(BOON_HOOK_RESOURCE, ""),
        ),
        apply,
    )


def remove_boon_hook(covenant: Covenant, index: int) -> Confirm:
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    label = catalog.describe_boon_hook(covenant.boons_hooks[index], by_id)

    def apply() -> None:
        del covenant.boons_hooks[index]

    return Confirm(f"Delete {escape(label)}?", apply)


def boon_hook_ops(saga: Saga, covenant: Covenant, kind: str) -> SectionOps:
    """The Boons or Hooks section (`kind`): Add, Edit and Delete by the
    row's position among that kind's."""
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    return SectionOps(
        add=lambda: add_boon_hook(saga, covenant, kind),
        edit=lambda row: edit_boon_hook(covenant, attached(covenant, kind)[row]),
        remove=lambda row: remove_boon_hook(covenant, attached(covenant, kind)[row]),
        rows=lambda: [
            catalog.describe_boon_hook(covenant.boons_hooks[i], by_id)
            for i in attached(covenant, kind)
        ],
    )


# The Treasury


def wealth_form(covenant: Covenant) -> Form:
    economics = covenant.economics

    def apply(values: dict[str, Any]) -> None:
        economics.wealth = values["wealth"]

    return Form(
        "Edit Wealth",
        lambda: [
            DialogField("wealth", "Wealth (pounds in stores)", "int", economics.wealth)
        ],
        apply,
    )


def income_fields(source: IncomeSource | None) -> list[DialogField]:
    """A source of income: its name, type, income and description, and
    whether a Resource Hook covers it."""
    usual = ", ".join(f"{t} {n}" for t, n in INCOME_TYPE_DEFAULTS.items())
    return [
        DialogField(
            "name", "Name", "text", source.name if source else "", required=True
        ),
        DialogField(
            "type",
            "Type",
            "select",
            source.type if source else "Typical",
            options=pairs(INCOME_TYPES),
            required=True,
        ),
        DialogField(
            "income",
            "Current Income (blank = usual)",
            "optint",
            source.income if source else None,
            hint=f"Usual per year: {usual}.",
        ),
        description_field(source.description if source else ""),
        *contested_fields(source),
    ]


def income_title(source: IncomeSource | None) -> str:
    if source is None:
        return "Add a Source of Income"
    return f"Edit {escape(source.name or 'this source of income')}"


def apply_income(
    covenant: Covenant, source: IncomeSource | None, values: dict[str, Any]
) -> None:
    if source is None:
        eco.add_income_source(covenant, values)
    else:
        for key, value in values.items():
            setattr(source, key, value)


def income_form(covenant: Covenant, source: IncomeSource | None) -> Form:
    return Form(
        income_title(source),
        lambda: income_fields(source),
        lambda values: apply_income(covenant, source, values),
    )


def income_ops(covenant: Covenant) -> SectionOps:
    """Sources of Income: Add, Edit and Delete."""
    sources = covenant.economics.income_sources
    return SectionOps(
        add=lambda: income_form(covenant, None),
        edit=lambda index: income_form(covenant, sources[index]),
        remove=lambda index: Confirm(
            f"Delete {escape(sources[index].name or 'this source of income')}?",
            lambda: sources.remove(sources[index]),
        ),
        rows=lambda: [s.name or "(unnamed)" for s in sources],
    )


#: What the user types on a table row, by `Economics` attribute.
ECONOMICS_TYPED_LABELS: dict[str, str] = {
    "tithes": "Amount (pounds a year)",
    "inflation": "Amount (pounds a year)",
    "sundry": "Amount (pounds a year, at least 1)",
    "magic_savings": "Savings (pounds a year)",
    "emergency_savings": "Savings (pounds a year)",
}


def economics_row_fields(
    covenant: Covenant, which: str, row: eco.Row
) -> list[DialogField]:
    """A Yearly Expenditure (`which` "expenditure") or Cost Savings row:
    the figures typed rather than calculated, and its Notes."""
    economics = covenant.economics
    first = "Cost" if which == "expenditure" else "Quantity"
    fields = [DialogField("_n", "Row", "info", row.name)]
    if row.typed:
        fields += [
            DialogField(
                attribute,
                ECONOMICS_TYPED_LABELS[attribute],
                "int",
                getattr(economics, attribute),
            )
            for attribute in row.typed
        ]
    else:
        fields += [
            DialogField("_c", f"{first} (calculated)", "info", eco.money(row.first)),
            DialogField("_s", "Savings (calculated)", "info", eco.money(row.savings)),
        ]
    fields.append(
        DialogField("notes", "Notes", "text", economics.notes.get(row.key, ""))
    )
    return fields


def economics_row_form(covenant: Covenant, which: str, row: eco.Row) -> Form:
    return Form(
        f"Edit {row.name}",
        lambda: economics_row_fields(covenant, which, row),
        lambda values: eco.apply_row_edit(covenant.economics, row.key, values),
        validate=lambda values: eco.row_problem(row.key, values),
    )


#: The emergency draw's choices.
DRAW, EDIT_ROW = "draw", "edit"


def emergency_draw(covenant: Covenant, row: eco.Row, summary: eco.Summary) -> Choose:
    """With a deficit, editing Emergency Savings first offers to cover it
    from Wealth: all of it, or as much as Wealth holds; or to edit the row
    as usual."""
    deficit = -summary.surplus_deficit
    draw = eco.emergency_draw(summary)
    outcome = (
        f"This moves {draw} from Wealth into Emergency Savings."
        if draw == deficit
        else f"Wealth only covers {draw} of it: all of it is drawn, and "
        f"{deficit - draw} stays uncovered."
    )

    def apply(choice: str) -> Form | list[str]:
        if choice == EDIT_ROW:
            return economics_row_form(covenant, "savings", row)
        eco.draw_from_wealth(covenant, draw)
        return notes(f"Drew {draw} from Wealth to cover the deficit.")

    return Choose(
        "Draw from Wealth to cover the deficit?",
        lambda: [
            Choice(
                "Draw from Wealth",
                DRAW,
                f"Deficit: {deficit}    Wealth: {summary.wealth}\n{outcome}",
            ),
            Choice(
                f"Edit {row.name} instead",
                EDIT_ROW,
                "Type the savings and notes yourself.",
            ),
        ],
        apply,
    )


def edit_economics_row(saga: Saga, covenant: Covenant, which: str, index: int):
    """Edit a Yearly Expenditure or Cost Savings row (by its index in the
    table). Emergency Savings, with a deficit and Wealth to draw on, offers
    the draw first."""
    summary = eco.summarize(saga, covenant)
    rows = summary.expenditure if which == "expenditure" else summary.savings
    row = rows[index]
    if (
        row.key == "emergency_savings"
        and summary.surplus_deficit < 0
        and eco.emergency_draw(summary) > 0
    ):
        return emergency_draw(covenant, row, summary)
    return economics_row_form(covenant, which, row)


def economics_row_ops(saga: Saga, covenant: Covenant, which: str) -> SectionOps:
    """Yearly Expenditure or Cost Savings (`which`): Edit only."""

    def rows() -> list[str]:
        summary = eco.summarize(saga, covenant)
        listed = summary.expenditure if which == "expenditure" else summary.savings
        return [row.name for row in listed]

    return SectionOps(
        edit=lambda index: edit_economics_row(saga, covenant, which, index),
        rows=rows,
    )
