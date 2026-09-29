"""The laboratory's Lab Totals tab: the owner's Lab Total for every
Technique + Form pair, and what goes into them (rules.lab, STORY-801; moved
off the Planning tab and the magus's own sheet by STORY-925). Like the other
domain modules it returns markup."""

from __future__ import annotations

from . import catalog
from .arts import ART_ABBREVIATIONS, FORMS, TECHNIQUES
from .laboratories import specialization_scores
from .markup import escape
from .models import Character, Laboratory, Saga
from .rules import effects, scores
from .rules import lab as lab_rules

#: The terms every total shares, drawn from the breakdown's first lines.
_SHARED_FROM = 2  # after the Technique and Form lines


def _grid(saga: Saga, magus: Character, lab: Laboratory) -> list[str]:
    header = " " * 12 + "".join(f"{ART_ABBREVIATIONS[f]:>5}" for f in FORMS)
    rows = [header]
    for technique in TECHNIQUES:
        totals = [
            int(lab_rules.lab_total(saga, magus, technique, form, lab).total)
            for form in FORMS
        ]
        rows.append(f"{technique:<12}" + "".join(f"{t:>5}" for t in totals))
    return rows


def lab_totals_text(saga: Saga, lab: Laboratory, magus: Character | None) -> str:
    """The Lab Total grid for `magus` working in `lab`, then the terms every
    total shares and the activity Specializations that add only sometimes."""
    if magus is None:
        return (
            "[dim]Lab Totals are worked out for the magus who works here: "
            "give the laboratory an owner to see them.[/]"
        )
    if magus.type != "magus":
        return f"[dim]{escape(magus.name)} isn't a magus, so has no Lab Totals.[/]"
    sample = lab_rules.lab_total(saga, magus, TECHNIQUES[0], FORMS[0], lab)
    shared = [
        f"{escape(line.label)} {line.amount:+g}"
        for line in sample.lines[_SHARED_FROM:]
        if line.amount is not None and "Specialization" not in line.label
    ]
    lines = [
        f"[b]Lab Totals for {escape(magus.name)}[/] (Technique + Form + the rest):",
        "",
        *_grid(saga, magus, lab),
        "",
        "Every total adds: " + ", ".join(shared) + ".",
    ]
    counted = [s for s in specialization_scores(lab) if s.counts]
    art_specs = [s for s in counted if s.name in (*TECHNIQUES, *FORMS)]
    if art_specs:
        lines.append(
            "Art Specializations, in totals using that Art: "
            + ", ".join(f"{s.name} {s.points:+d}" for s in art_specs)
            + "."
        )
    activity_specs = [s for s in counted if s not in art_specs]
    if activity_specs:
        lines.append(
            "Activity Specializations, only for that activity: "
            + ", ".join(f"{s.name} {s.points:+d}" for s in activity_specs)
            + "."
        )
    multiplied = [
        e
        for e in effects.collect(
            [scores.character_source(magus.virtues_flaws)], "lab_total"
        )
        if e.modifier.multiplier is not None and e.modifier.activity is None
    ]
    if multiplied:
        names = catalog.load_virtue_flaw_catalog_by_id()
        lines.append(
            "Multiplied (already in the grid): "
            + ", ".join(
                f"{escape(catalog.describe_virtue_flaw(e.instance, names))} "
                f"x{e.modifier.multiplier:g}"
                for e in multiplied
            )
            + "."
        )
    lines += [
        "",
        "[b]By activity[/] (on top of the grid):",
        *_activity_lines(saga, magus, lab),
    ]
    return "\n".join(lines)


#: The activities the Planning tab summarises, with a sample Art pair for
#: the ones that always use the same Arts.
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
            terms.append(f"{escape(line.label)} {line.amount:+g}")
        elif line.multiplier is not None:
            terms.append(f"{escape(line.label)} x{line.multiplier:g}")
    return terms


def _activity_lines(saga: Saga, magus: Character, lab: Laboratory) -> list[str]:
    lines = []
    for activity, label, pair in _ACTIVITIES:
        technique, form = pair or (TECHNIQUES[0], FORMS[0])
        generic = lab_rules.lab_total(saga, magus, technique, form, lab)
        specific = lab_rules.lab_total(
            saga, magus, technique, form, lab, activity=activity
        )
        terms = _extra_terms(generic, specific) or ["nothing extra"]
        text = f"{label}: {', '.join(terms)}"
        if activity == "longevity_ritual":
            total = int(specific.total)
            text += (
                f" (Creo Corpus {total}: aging rolls "
                f"-{lab_rules.longevity_modifier(total)})"
            )
        elif activity == "extract_vis":
            total = int(specific.total)
            text += f" (Creo Vim {total}: {lab_rules.vis_extracted(total)} pawns)"
        lines.append(text + ".")
    generic = lab_rules.lab_total(saga, magus, TECHNIQUES[0], FORMS[0], lab)
    experimenting = lab_rules.lab_total(
        saga, magus, TECHNIQUES[0], FORMS[0], lab, experimenting=True
    )
    terms = _extra_terms(generic, experimenting)
    lines.append(
        "Experimenting: + a simple die"
        + (f", {', '.join(terms)}" if terms else "")
        + "."
    )
    lines.append(
        f"Raw vis in one season: up to {lab_rules.vis_limit(magus)} pawns; "
        f"shape and material bonuses up to +{lab_rules.shape_material_cap(magus)} "
        "(both from Magic Theory)."
    )
    return lines
