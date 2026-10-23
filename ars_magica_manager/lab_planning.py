"""The laboratory's Lab Totals tab: the owner's Lab Total for every
Technique + Form pair, and what goes into them (rules.lab). Three
sections: the grid, the Base Lab Total every total shares, and
what each activity adds. Like the other domain modules it returns markup."""

from __future__ import annotations

import re

from . import catalog
from .arts import ART_ABBREVIATIONS, FORMS, TECHNIQUES
from .markup import escape
from .models import Character, Laboratory, Saga
from .rules import effects, scores
from .rules import lab as lab_rules
from .rules.lab_stats import specialization_scores

#: The terms every total shares, drawn from the breakdown's first lines.
_SHARED_FROM = 2  # after the Technique and Form lines
#: The grid's columns.
_ROW_LABEL_WIDTH = 12
_CELL_WIDTH = 5
#: Characteristics as the Base Lab Total lists them (
#: "Int +5, Magic Theory +7, Aura (Magic) +5").
_SHORT = {
    "Intelligence": "Int",
    "Perception": "Per",
    "Strength": "Str",
    "Stamina": "Sta",
    "Presence": "Pre",
    "Communication": "Com",
    "Dexterity": "Dex",
    "Quickness": "Qik",
}


def _no_totals(magus: Character | None) -> str | None:
    """Why there are no Lab Totals to show, or None."""
    if magus is None:
        return (
            "[dim]Lab Totals are worked out for the magus who works here: "
            "give the laboratory an owner to see them.[/]"
        )
    if magus.type != "magus":
        return f"[dim]{escape(magus.name)} isn't a magus, so has no Lab Totals.[/]"
    return None


def signed(value: float) -> str:
    """A signed amount, coloured by theme: + in $text-success, - in
    $text-error, zero plain."""
    text = f"{value:+g}"
    if value > 0:
        return f"[$text-success]{text}[/]"
    if value < 0:
        return f"[$text-error]{text}[/]"
    return text


def _columns(rows: list[tuple[str, str]], *, bold: bool = False) -> list[str]:
    """(plain label, markup value) rows with the values lined up."""
    if not rows:
        return []
    width = max(len(label) for label, _ in rows) + 2
    return [
        (f"[b]{escape(label)}[/]" if bold else escape(label))
        + " " * (width - len(label))
        + value
        for label, value in rows
    ]


def lab_totals_grid_text(saga: Saga, lab: Laboratory, magus: Character | None) -> str:
    """The Lab Total for every Technique (rows) and Form (columns)."""
    if (reason := _no_totals(magus)) is not None:
        return reason
    assert magus is not None
    header = " " * _ROW_LABEL_WIDTH + "".join(
        f"{ART_ABBREVIATIONS[f]:>{_CELL_WIDTH}}" for f in FORMS
    )
    lines = [
        f"[dim]{escape(magus.name)} working here: Technique + Form + the Base "
        "Lab Total below.[/]",
        "",
        f"[b]{header}[/]",
    ]
    for technique in TECHNIQUES:
        totals = [
            int(lab_rules.lab_total(saga, magus, technique, form, lab).total)
            for form in FORMS
        ]
        lines.append(
            f"[b]{technique:<{_ROW_LABEL_WIDTH}}[/]"
            + "".join(f"{t:>{_CELL_WIDTH}}" for t in totals)
        )
    return "\n".join(lines)


def _base_label(label: str) -> str:
    label = _SHORT.get(label, label)
    return re.sub(r"^Aura \((\w+) -?\d+\)$", r"Aura (\1)", label)


def base_lab_total_text(saga: Saga, lab: Laboratory, magus: Character | None) -> str:
    """The terms every Lab Total shares, then the Specializations that add
    only to some, and any multiplier already in the grid."""
    if _no_totals(magus) is not None:
        return "[dim](no Lab Totals)[/]"
    assert magus is not None
    sample = lab_rules.lab_total(saga, magus, TECHNIQUES[0], FORMS[0], lab)
    lines = _columns(
        [
            (_base_label(line.label), signed(line.amount))
            for line in sample.lines[_SHARED_FROM:]
            if line.amount is not None and "Specialization" not in line.label
        ]
    )
    counted = [s for s in specialization_scores(saga, lab) if s.counts]
    art_specs = [s for s in counted if s.name in (*TECHNIQUES, *FORMS)]
    if art_specs:
        lines += ["", "[b]Art Specializations[/] [dim](in totals using that Art)[/]"]
        lines += _columns([(s.name, signed(s.points)) for s in art_specs])
    activity_specs = [s for s in counted if s not in art_specs]
    if activity_specs:
        lines += [
            "",
            "[b]Activity Specializations[/] [dim](only for that activity)[/]",
        ]
        lines += _columns([(s.name, signed(s.points)) for s in activity_specs])
    multiplied = [
        e
        for e in effects.collect(
            [scores.character_source(magus.virtues_flaws)], "lab_total"
        )
        if e.modifier.multiplier is not None and e.modifier.activity is None
    ]
    if multiplied:
        names = catalog.load_virtue_flaw_catalog_by_id()
        lines += ["", "[b]Multiplied[/] [dim](already in the grid)[/]"]
        lines += _columns(
            [
                (
                    catalog.describe_virtue_flaw(e.instance, names),
                    f"x{e.modifier.multiplier:g}",
                )
                for e in multiplied
            ]
        )
    return "\n".join(lines)


#: The activities the tab summarises, with a sample Art pair for the ones
#: that always use the same Arts.
_ACTIVITIES: tuple[tuple[str, str, tuple[str, str] | None], ...] = (
    ("invent_spells", "Inventing spells", None),
    ("enchant_items", "Enchanting items", None),
    ("learn_from_lab_text", "Working from a Lab Text", None),
    ("bind_familiar", "Binding a familiar", None),
    ("longevity_ritual", "Longevity Ritual", ("Creo", "Corpus")),
    ("extract_vis", "Extracting vis", ("Creo", "Vim")),
)


def _extra_terms(
    generic: lab_rules.LabTotal, specific: lab_rules.LabTotal
) -> list[str]:
    """The terms `specific` has that `generic` doesn't."""
    seen = {(line.label, line.amount, line.multiplier) for line in generic.lines}
    terms = []
    for line in specific.lines:
        if (line.label, line.amount, line.multiplier) in seen:
            continue
        if line.amount is not None:
            terms.append(f"{escape(line.label)} {signed(line.amount)}")
        elif line.multiplier is not None:
            terms.append(f"{escape(line.label)} x{line.multiplier:g}")
    return terms


def activity_totals_text(saga: Saga, lab: Laboratory, magus: Character | None) -> str:
    """What each activity adds on top of the grid, then the Longevity and
    vis results and the Magic Theory limits, each on its own line."""
    if _no_totals(magus) is not None:
        return "[dim](no Lab Totals)[/]"
    assert magus is not None
    nothing = "[dim]nothing extra[/]"
    rows: list[tuple[str, str]] = []
    results: list[tuple[str, str]] = []
    generic = lab_rules.lab_total(saga, magus, TECHNIQUES[0], FORMS[0], lab)
    for activity, label, pair in _ACTIVITIES:
        technique, form = pair or (TECHNIQUES[0], FORMS[0])
        base = lab_rules.lab_total(saga, magus, technique, form, lab)
        specific = lab_rules.lab_total(
            saga, magus, technique, form, lab, activity=activity
        )
        rows.append((label, ", ".join(_extra_terms(base, specific)) or nothing))
        total = int(specific.total)
        if activity == "longevity_ritual":
            results.append(
                (
                    "Longevity result",
                    f"Creo Corpus {total}: aging rolls "
                    f"-{lab_rules.longevity_modifier(total)}",
                )
            )
        elif activity == "extract_vis":
            results.append(
                (
                    "Vis extraction",
                    f"Creo Vim {total}: {lab_rules.vis_extracted(total)} pawns "
                    "a season",
                )
            )
    experimenting = lab_rules.lab_total(
        saga, magus, TECHNIQUES[0], FORMS[0], lab, experimenting=True
    )
    rows.append(
        (
            "Experimenting",
            ", ".join(["+ a simple die", *_extra_terms(generic, experimenting)]),
        )
    )
    results += [
        (
            "Raw vis a season",
            f"up to {lab_rules.vis_limit(magus)} pawns [dim](Magic Theory)[/]",
        ),
        (
            "Shape and material",
            f"bonuses up to +{lab_rules.shape_material_cap(magus)} "
            "[dim](Magic Theory)[/]",
        ),
    ]
    # One label column for both groups, so their values line up.
    lined = _columns(rows + results, bold=True)
    return "\n".join([*lined[: len(rows)], "", *lined[len(rows) :]])
