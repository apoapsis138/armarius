"""A character's Church tab and its forms -- no UI in here: Holy Orders
(his grade, the ladder of grades, what stands between him and the
priesthood), his Ordinations, his Petitions to the Church and his cases in
the Canon Court, with Petition the Church, Add Canon Case, Edit Holy Orders
and Perform an Exorcism, and the Ordination season's fields in the
planner. The rules and their pages are rules.clergy's (The Church pp.
33-38, 46-48).

Pattern: each list is the selectable list + details panel, its keys from
SectionOps; the grades and the petition's modifiers are tables the forms
and the totals both read."""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import Any

from .. import catalog
from ..commands import Command, Form, Refuse, SectionOps, delete, notes
from ..form_spec import ChoiceReads, DialogField, pairs
from ..markup import escape, fit
from ..models import (
    SEASONS,
    CanonCase,
    Character,
    ChurchCareer,
    Ordination,
    Petition,
    Saga,
    SeasonPlan,
    character_age,
)
from ..models.clergy import (
    ACCUSED,
    ACCUSER,
    AUDIENCE,
    GOOD_STANDING,
    GUILTY,
    IRREGULAR,
    PENDING,
    STANDINGS,
    VERDICTS,
    WRITTEN,
)
from ..rules import clergy as cl
from ..rules import dice
from ..sections import (
    CANON_SECTION,
    ORDERS_SECTION,
    ORDINATIONS_SECTION,
    PETITIONS_SECTION,
)

TC = "The Church"
ORDINATION = "ordination"
#: The help pages of the forms that have their own.
PETITION_HELP = "petition-church"
CANON_HELP = "canon-case"
EXORCISM_HELP = "perform-exorcism"
ORDERS_HELP = "edit-holy-orders"

EXAMINERS = ("The bishop", "The archdeacon", "The dean")

ActivityIs = Callable[..., Callable[[dict[str, Any]], bool]]


def ok(words: str) -> str:
    return f"[$text-success]{words}[/]"


def warn(words: str) -> str:
    return f"[$text-warning]{words}[/]"


def bad(words: str) -> str:
    return f"[$text-error]{words}[/]"


def _col(words: str, width: int) -> str:
    """A column of a list's row: `words` fitted short of `width`, so a
    space always parts it from the next, escaped."""
    return escape(fit(words, width - 1)) + " "


def _when(season: str, year: int | None) -> str:
    if not season and year is None:
        return ""
    return f"{season} {year}".strip() if year is not None else season


def _age(saga: Saga, character: Character) -> int | None:
    return character_age(character.background.year_born, saga.current_year)


# -- Holy Orders --


def grade_words(career: ChurchCareer) -> str:
    if not cl.in_orders(career):
        return "None (a layman)"
    return f"{career.grade} ({cl.orders_words(career.grade)})"


def standing_words(career: ChurchCareer) -> str:
    standing = cl.case_standing(career)
    label = cl.STANDING_LABELS.get(standing, standing)
    if standing == GOOD_STANDING:
        return ok(label)
    if standing == IRREGULAR:
        return warn(f"{label}: no Faith Points until he confesses")
    return bad(label)


def social_status_words(character: Character) -> str:
    from_catalog = cl.social_statuses(character)
    if not from_catalog:
        return "(none)"
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    return ", ".join(
        escape(getattr(by_id.get(vf.vf_id), "name", vf.vf_id)) for vf in from_catalog
    )


def orders_facts(character: Character) -> list[tuple[str, str]]:
    """The Holy Orders section's facts: (label, markup)."""
    career = character.church
    law = "Canon, not secular" if cl.in_orders(career) else "Secular"
    return [
        ("Grade", grade_words(career)),
        ("Social Status", social_status_words(character)),
        ("Birth diocese", escape(career.diocese) or "[dim](not set)[/]"),
        ("Faith Points from orders", str(cl.faith_points_from_orders(career))),
        ("Standing", standing_words(career)),
        ("Law", law),
    ]


def ladder(career: ChurchCareer, *, ticks: bool = True) -> str:
    """The grades: those held in green (ticked, for the terminal), the
    next one marked, the rest dim."""
    held = cl.rank(career.grade)
    parts = []
    for n, grade in enumerate(cl.GRADES):
        if n <= held:
            parts.append(ok(f"✓ {grade.name}" if ticks else grade.name))
        elif n == held + 1:
            parts.append(f"[b]→ {grade.name}[/]")
        else:
            parts.append(f"[dim]{grade.name}[/]")
    return ("  " if ticks else "  ·  ").join(parts)


def next_line(saga: Saga, character: Character) -> str:
    career = character.church
    if career.barred:
        return bad(
            "Barred: his last examination botched; a petition (EF 9) must let "
            f"him sit again ({TC} p. 34)."
        )
    grade = cl.next_grade(career)
    if grade is None:
        return f"[$label]Next:[/] a bishop is elected, not examined ({TC} p. 33)."
    terms = cl.exam_terms(character, grade)
    line = (
        f"[$label]Next:[/] {grade.name}: Intelligence {terms.intelligence:+d} + "
        f"{grade.ability} {terms.score} + stress die against {grade.ease}, a "
        f"season's work (Plan a Season: Ordination).  [dim]({TC} pp. 33-35)[/]"
    )
    age = _age(saga, character)
    if grade.name == "Acolyte" and age is not None and age < 20:
        line += " " + warn(f"An acolyte is usually past twenty; he is {age}.")
    return line


def priest_line(saga: Saga, character: Character, *, ticks: bool = True) -> str:
    """What stands between him and the priesthood (only before it); each
    met is ticked for the terminal."""
    if cl.rank(character.church.grade) >= cl.rank(cl.PRIEST):
        return ""
    parts = []
    for req in cl.priest_requirements(saga, character, _age(saga, character)):
        label = req.label + (f" ({req.why})" if req.why else "")
        if req.met is True:
            parts.append(f"{label} ✓" if ticks else label)
        elif req.met is None:
            parts.append(f"{label}?")
        else:
            parts.append(warn(f"{label}: a dispensation, Petition EF {cl.APPEAL_EASE}"))
    return "[$label]Toward Priest:[/] " + ", ".join(parts) + f"  [dim]({TC} p. 35)[/]"


def orders_text(saga: Saga, character: Character) -> str:
    """The terminal's Holy Orders: the facts on two lines, the ladder, the
    next grade and the priesthood's requirements."""
    facts = orders_facts(character)
    line = "  ·  ".join
    lines = [
        line(f"[$label]{k}:[/] {v}" for k, v in facts[:3]),
        line(f"[$label]{k}:[/] {v}" for k, v in facts[3:]),
        "",
        ladder(character.church),
        "",
        next_line(saga, character),
    ]
    if extra := priest_line(saga, character):
        lines.append(extra)
    if character.church.notes.strip():
        lines += ["", escape(character.church.notes.strip())]
    return "\n".join(lines)


def orders_desk_text(saga: Saga, character: Character) -> str:
    """The desktop's text under the facts: the ladder, next, priesthood."""
    lines = [ladder(character.church, ticks=False), "", next_line(saga, character)]
    if extra := priest_line(saga, character, ticks=False):
        lines.append(extra)
    return "\n".join(lines)


def orders_fields(character: Character) -> list[DialogField]:
    career = character.church
    return [
        DialogField(
            "grade",
            "Grade",
            "select",
            career.grade,
            options=[("None (a layman)", ""), *pairs(cl.NAMES)],
            hint="Set here a grade he held before play; a season's Ordination "
            "examines him for the next.",
        ),
        DialogField("diocese", "Birth diocese", "text", career.diocese),
        DialogField(
            "standing",
            "Standing",
            "select",
            career.standing,
            options=[(cl.STANDING_LABELS[s], s) for s in STANDINGS],
            hint=f"Irregular: no Faith Points until he confesses ({TC} p. 37).",
        ),
        DialogField(
            "benefice",
            "Benefice or office",
            "text",
            career.benefice,
            hint="A priest needs a benefice, chaplaincy or curacy free to be "
            f"ordained ({TC} p. 35).",
        ),
        DialogField(
            "barred",
            "Barred from examination until a petition succeeds",
            "check",
            career.barred,
        ),
        DialogField("notes", "Notes", "area", career.notes),
    ]


def holy_orders_form(saga: Saga, character: Character) -> Form:
    """Edit Holy Orders: his grade, birth diocese, standing, benefice."""

    def apply(values: dict[str, Any]) -> None:
        career = character.church
        career.grade = values.get("grade") or ""
        career.diocese = values.get("diocese") or ""
        career.standing = values.get("standing") or GOOD_STANDING
        career.benefice = values.get("benefice") or ""
        career.barred = bool(values.get("barred"))
        career.notes = values.get("notes") or ""

    return Form(
        "Edit Holy Orders",
        lambda: orders_fields(character),
        apply,
        help_id=ORDERS_HELP,
    )


def orders_ops(saga: Saga, character: Character) -> SectionOps:
    return SectionOps(
        edit=lambda _row: holy_orders_form(saga, character),
        rows=lambda: ["Holy Orders"],
    )


# -- an entry, as both front-ends draw it --


@dataclass(frozen=True)
class Entry:
    """One row of a list: the terminal's row, and the desktop's ledger
    entry (margin mark, heading, italic line, badge, words and a note)."""

    row: str
    title: str
    subtitle: str
    rubric: str
    meta: str
    badge: tuple[str, str]
    body: str
    note: str
    info: str


NUMERALS = ("I", "II", "III", "IV", "V", "VI", "VII", "VIII")


# -- Ordinations --

W_GRADE, W_WHEN, W_EXAM = 13, 14, 22


def _tone(result: str) -> str:
    if result in (cl.FAILED, cl.BOTCHED):
        return "text-error"
    if result == cl.IGNORANT:
        return "text-warning"
    return "text-success"


def _coloured(tone: str, words: str) -> str:
    return f"[${tone}]{escape(words)}[/]"


def exam_sum(o: Ordination) -> str:
    if o.result in (cl.ELECTED, cl.RECORDED) and not o.ability:
        return result_words(o)
    die = "botch" if o.botched else str(o.die)
    return (
        f"Intelligence {o.intelligence:+d} + {escape(o.ability)} {o.score} + "
        f"stress die {die} = [b]{o.total}[/] against {o.ease}"
    )


def result_words(o: Ordination) -> str:
    return cl.result_label(o.result)


ORDINATION_RULE = (
    "[dim]Ordained: the grade's Social Status and a Faith Point. More than "
    "double the Ease Factor: a Reputation of 1 for knowing the Ability; "
    "missing it by 6 or less still passes, with a Reputation for ignorance; "
    f"missing by 7 or more is not ordained, and may be appealed (Petition EF "
    f"{cl.APPEAL_EASE}) or tried again another season; a botch may be tried "
    f"again only by petition ({TC} p. 34).[/]"
)


def ordination_entry(o: Ordination) -> Entry:
    tone = _tone(o.result)
    when = _when(o.season, o.year)
    exam = f"{o.total} vs {o.ease} ({o.ability.split()[0]})" if o.ability else "—"
    extras = []
    if o.examiner:
        extras.append(f"Examined by {o.examiner.lower()}")
    if o.elsewhere:
        extras.append("outside his birth diocese")
    note = "; ".join(extras + ([o.note] if o.note else []))
    return Entry(
        row=_col(o.grade, W_GRADE)
        + _col(when, W_WHEN)
        + _col(exam, W_EXAM)
        + _coloured(tone, result_words(o)),
        title=o.grade,
        subtitle=f"{result_words(o)}  ·  {when}" if when else result_words(o),
        rubric=NUMERALS[cl.rank(o.grade)] if o.grade in cl.BY_NAME else "§",
        meta=when,
        badge=(result_words(o), tone),
        body=exam_sum(o),
        note=f"[i]{escape(note)}[/]" if note else "",
        info="\n".join(
            [
                f"[b]{escape(o.grade)}[/]  ·  {escape(when)}  ·  "
                + _coloured(tone, result_words(o)),
                exam_sum(o),
                *([f"[i]{escape(note)}[/]"] if note else []),
                "",
                ORDINATION_RULE,
            ]
        ),
    )


def ordinations_title(career: ChurchCareer) -> str:
    return f"Ordinations ({len(career.ordinations)})"


def ordinations_header() -> str:
    return (
        "  "
        + fit("Grade", W_GRADE)
        + fit("Season", W_WHEN)
        + fit("Examination", W_EXAM)
        + "Result"
    )


def ordination_rows(character: Character) -> list[tuple[int | None, str]]:
    found = character.church.ordinations
    if not found:
        return [
            (
                None,
                "[dim]None yet: an Ordination season examines him for the next "
                "grade.[/]",
            )
        ]
    return [(n, ordination_entry(o).row) for n, o in enumerate(found)]


def ordination_info(character: Character, index: int | None) -> str:
    found = character.church.ordinations
    if index is None or not 0 <= index < len(found):
        return EMPTY_PANEL
    return ordination_entry(found[index]).info


def ordination_fields(existing: Ordination | None, saga: Saga) -> list[DialogField]:
    o = existing or Ordination("Doorkeeper", season=saga.current_season)
    return [
        DialogField(
            "grade", "Grade", "select", o.grade, options=pairs(cl.NAMES), required=True
        ),
        DialogField(
            "season",
            "Season",
            "select",
            o.season or None,
            options=pairs(SEASONS),
            allow_blank=True,
        ),
        DialogField(
            "year", "Year", "optint", o.year if existing else saga.current_year
        ),
        DialogField(
            "result",
            "Result",
            "select",
            o.result or cl.RECORDED,
            options=[(label, key) for key, (label, _o, _r) in cl.EXAM_RESULTS.items()],
            hint="An Ordination season sets it from the examination; record one "
            "from before play here.",
        ),
        DialogField("intelligence", "Intelligence then", "int", o.intelligence),
        DialogField("score", "His score in the Ability examined", "int", o.score),
        DialogField("die", "Stress die", "int", o.die),
        DialogField("examiner", "Examined by", "text", o.examiner),
        DialogField("note", "Note", "text", o.note),
    ]


def _ordination_from(values: dict[str, Any], existing: Ordination | None) -> Ordination:
    grade = cl.BY_NAME.get(values.get("grade") or "", cl.GRADES[0])
    result = values.get("result") or cl.RECORDED
    return replace(
        existing or Ordination(grade.name),
        grade=grade.name,
        season=values.get("season") or "",
        year=values.get("year"),
        ability=grade.ability,
        ease=grade.ease,
        result=result,
        intelligence=int(values.get("intelligence") or 0),
        score=int(values.get("score") or 0),
        die=max(0, int(values.get("die") or 0)),
        botched=result == cl.BOTCHED,
        examiner=values.get("examiner") or "",
        note=values.get("note") or "",
    )


def ordination_ops(saga: Saga, character: Character) -> SectionOps:
    """Add, Edit and Delete an ordination's record. Adding one doesn't
    change his grade: Edit Holy Orders does, as an Ordination season does."""
    career = character.church

    def form(index: int | None) -> Form:
        existing = career.ordinations[index] if index is not None else None

        def apply(values: dict[str, Any]) -> None:
            made = _ordination_from(values, existing)
            if index is None:
                career.ordinations.append(made)
            else:
                career.ordinations[index] = made

        return Form(
            "Add Ordination" if index is None else "Edit Ordination",
            lambda: ordination_fields(existing, saga),
            apply,
            live=lambda values: ORDINATION_RULE,
            save_label="Add" if index is None else "Save",
            help_id=ORDINATIONS_SECTION,
        )

    return SectionOps(
        add=lambda: form(None),
        edit=form,
        remove=lambda index: delete(
            career.ordinations,
            index,
            f"the ordination as {career.ordinations[index].grade}",
        ),
        rows=lambda: [o.grade for o in career.ordinations],
    )


# -- the Ordination season, in the planner --


def season_fields(
    character: Character, plan: SeasonPlan | None, activity_is: ActivityIs
) -> list[DialogField]:
    """Plan a Season: Ordination's own fields: the grade sought, who
    examines him, ordained outside his birth diocese, and the die if it is
    rolled at the table."""
    ours = plan is not None and plan.activity == ORDINATION
    shown = activity_is(ORDINATION)
    grades = cl.examinable(character.church)
    sought = plan.title if plan is not None and ours else ""
    if sought not in {g.name for g in grades}:
        sought = grades[0].name if grades else ""
    diocese = character.church.diocese or "his birth diocese"
    return [
        DialogField(
            "ordination_grade",
            "Grade sought",
            "select",
            sought,
            options=[(f"{g.name} ({g.ability}, EF {g.ease})", g.name) for g in grades],
            show_if=shown,
            hint="One grade a season; several at once only on election as "
            f"bishop ({TC} p. 34).",
        ),
        DialogField(
            "ordination_examiner",
            "Examined by",
            "select",
            (plan.examiner if plan is not None and ours else "") or EXAMINERS[1],
            options=pairs(EXAMINERS),
            show_if=shown,
        ),
        DialogField(
            "ordination_elsewhere",
            "Ordained outside his birth diocese",
            "check",
            bool(plan.ordained_elsewhere) if plan is not None and ours else False,
            show_if=shown,
            hint=f"Needs the leave of the bishop of {escape(diocese)} ({TC} p. 33).",
        ),
        DialogField(
            "ordination_swap",
            "Swap his Social Status for the clergy's",
            "check",
            plan.swap_status if plan is not None and ours else True,
            show_if=shown,
            hint="A character has one Social Status: the grade's replaces his "
            f"own (Clerk, then Priest; {TC} pp. 25, 34; DE p. 63). Untick to "
            "leave it for the troupe to change on Virtues & Flaws.",
        ),
        DialogField(
            "ordination_die",
            "Stress die, if rolled at the table",
            "optint",
            plan.die if plan is not None and ours else None,
            placeholder="(rolled when the season is applied)",
            show_if=shown,
        ),
    ]


#: The plan's fields the Ordination season sets from the form.
READS: ChoiceReads = (
    (
        (ORDINATION,),
        lambda v: {
            "title": v.get("ordination_grade") or "",
            "examiner": v.get("ordination_examiner") or "",
            "ordained_elsewhere": bool(v.get("ordination_elsewhere")),
            "swap_status": bool(v.get("ordination_swap", True)),
            "die": v.get("ordination_die"),
        },
    ),
)


def examination_text(saga: Saga, character: Character, grade_name: str) -> str:
    """The Examination: the total and what each band of result does, the
    priesthood's dispensations and a major order's celibacy."""
    grade = cl.BY_NAME.get(grade_name) or cl.next_grade(character.church)
    if grade is None or not grade.ease:
        return "A bishop is elected, not examined."
    terms = cl.exam_terms(character, grade)
    ease = grade.ease
    lines = [
        f"[b]{grade.name}[/]: Intelligence {terms.intelligence:+d} + "
        f"{grade.ability} {terms.score} + stress die = {terms.base} + die, "
        f"against [b]{ease}[/]",
        "",
        f"  {ok(f'{2 * ease + 1}+')}  ordained, and a Reputation of 1, "
        f"learned in {grade.ability}",
        f"  {ok(f'{ease}+')}  ordained: a Faith Point and the Social Status",
        f"  {warn(f'{ease - cl.PASSING_MISS} to {ease - 1}')}  passed, with a "
        "Reputation of 1 for ignorance",
        f"  {bad(f'{ease - cl.PASSING_MISS - 1} or less')}  not ordained; appeal "
        f"by petition (EF {cl.APPEAL_EASE}), or try again next season",
        f"  {bad('botch')}  only a petition lets him try again",
        "",
        f"[dim]The season is also study: Source Quality 2 in {grade.ability} "
        f"({TC} pp. 33-34).[/]",
    ]
    change = cl.status_change(character, grade.name)
    if change.swaps:
        old, new = cl.swap_names(change)
        lines.append(
            f"Social Status: {escape(new)} in place of {escape(old)}, one "
            f"status only ({TC} pp. 25, 34; DE p. 63)."
        )
    if change.warning:
        lines.append(warn(escape(change.warning)))
    if grade.name == cl.PRIEST:
        for req in cl.priest_requirements(saga, character, _age(saga, character)):
            if req.met is False:
                lines.append(
                    warn(
                        f"Not {req.label}"
                        + (f" ({escape(req.why)})" if req.why else "")
                        + f": a dispensation is needed (Petition EF {cl.APPEAL_EASE})."
                    )
                )
    if not grade.minor:
        lines.append(f"[dim]A major order: celibate from now on ({TC} p. 35).[/]")
    return "\n".join(lines)


# -- Petitions --

W_ASK, W_HOW, W_SEASON, W_PT = 44, 10, 13, 10


def _result_tone(result: str) -> str:
    if result in (cl.GRANTED, cl.OVERTURNED):
        return "text-success"
    if result == cl.COMPROMISE:
        return "text-warning"
    if result == cl.NOT_MADE:
        return "label"
    return "text-error"


def petition_sum(p: Petition) -> str:
    terms = cl.petition_terms(p)
    words = " + ".join(
        f"{escape(name)} {value}" if n < 2 else f"{escape(name)} {value:+d}"
        for n, (name, value) in enumerate(terms)
    )
    if not p.made:
        return f"{words}; Ease Factor {cl.petition_ease(p)}"
    return f"{words} = [b]{cl.petition_total(p)}[/] against {cl.petition_ease(p)}"


def _arguments_line(p: Petition) -> str:
    parts = []
    for ability in cl.ARGUMENTS:
        bonus = p.arguments.get(ability, 0)
        if not bonus:
            continue
        if ability in p.argument_botches:
            parts.append(f"{ability} +{bonus}: botched, a penalty")
        elif (rolled := p.argument_rolls.get(ability)) is not None:
            verdict = "counts" if rolled >= cl.ARGUMENT_EASE else "fails"
            parts.append(
                f"{ability} +{bonus}: rolled {rolled} vs {cl.ARGUMENT_EASE}, {verdict}"
            )
        else:
            parts.append(f"{ability} +{bonus}: not yet rolled")
    return "; ".join(parts)


PETITION_RULE = (
    "[dim]No die is rolled. An argument's bonus counts only if Intelligence + "
    "the Ability + a stress die reaches 9; a botch takes it away instead. A "
    f"priest may grant up to {cl.PRIEST_GRANTS}, a bishop up to "
    f"{cl.BISHOP_GRANTS}; the rest go to the papal curia ({TC} pp. 46-48).[/]"
)


def petition_entry(p: Petition) -> Entry:
    result = cl.petition_result(p)
    tone = _result_tone(result)
    how = "Audience" if p.method == AUDIENCE else "Written"
    ease = cl.petition_ease(p)
    to = cl.decider(ease)
    when = _when(p.season, p.year) if p.made else "planned"
    total = f"{cl.petition_total(p)} vs {ease}" if p.made else f"– vs {ease}"
    args = _arguments_line(p)
    note = "; ".join(x for x in (args, p.note) if x)
    return Entry(
        row=_col(p.ask or "(unnamed)", W_ASK)
        + _col(how, W_HOW)
        + _col(when, W_SEASON)
        + _col(total, W_PT)
        + _coloured(tone, result),
        title=p.ask or "(unnamed)",
        subtitle=f"{how} petition to {to}",
        rubric="§",
        meta=f"{how}, to {to}, {when}",
        badge=(result, tone),
        body=petition_sum(p),
        note=f"[i]{escape(note)}[/]" if note else "",
        info="\n".join(
            [
                f"[b]{escape(p.ask or '(unnamed)')}[/]",
                f"{how} petition to {to}  ·  {escape(when)}  ·  "
                + _coloured(tone, result),
                "",
                petition_sum(p),
                *([escape(args)] if args else []),
                *([f"[i]{escape(p.note)}[/]"] if p.note else []),
                *(
                    [
                        f"An appeal: overturns at {p.original + cl.APPEAL_MARGIN}; a "
                        f"compromise above {p.original - cl.APPEAL_MARGIN}."
                    ]
                    if p.appeal and p.original is not None
                    else []
                ),
                "",
                PETITION_RULE,
            ]
        ),
    )


def petitions_title(career: ChurchCareer) -> str:
    granted = sum(
        1
        for p in career.petitions
        if cl.petition_result(p) in (cl.GRANTED, cl.OVERTURNED)
    )
    count = len(career.petitions)
    return f"Petitions ({granted} granted of {count})" if count else "Petitions"


def petitions_header() -> str:
    return (
        "  "
        + fit("Petition", W_ASK)
        + fit("By", W_HOW)
        + fit("Season", W_SEASON)
        + fit("Total", W_PT)
        + "Result"
    )


def petition_rows(character: Character) -> list[tuple[int | None, str]]:
    found = character.church.petitions
    if not found:
        return [(None, "[dim]None yet. Petition the Church with a.[/]")]
    return [(n, petition_entry(p).row) for n, p in enumerate(found)]


def petition_info(character: Character, index: int | None) -> str:
    found = character.church.petitions
    if index is None or not 0 <= index < len(found):
        return EMPTY_PANEL
    return petition_entry(found[index]).info


_FLAGS = (
    ("testimony", f"Many testify (+{cl.TESTIMONY})"),
    ("evidence", f"Magical evidence (+{cl.EVIDENCE})"),
    ("vision", f"A holy vision (+{cl.VISION})"),
    ("miracle", f"Miracles (+{cl.MIRACLE})"),
)
_ARGUMENT_KEYS = {
    cl.CANON_LAW: "argue_law",
    "Artes Liberales": "argue_logic",
    "Intrigue": "argue_intrigue",
}
_ARGUMENT_LABELS = {
    cl.CANON_LAW: "Argument: Canon Law",
    "Artes Liberales": "Argument: Logic",
    "Intrigue": "Argument: Intrigue",
}
OTHER_EXAMPLE = ""


def petition_fields(
    saga: Saga, character: Character, p: Petition | None
) -> list[DialogField]:
    q = p or Petition("", season=saga.current_season, year=saga.current_year)
    return [
        DialogField(
            "ask",
            "Petition",
            "text",
            q.ask,
            required=True,
            placeholder="e.g. Access to the cathedral library",
        ),
        DialogField(
            "example",
            "Like",
            "select",
            q.example,
            options=[
                ("Something else (type its Ease Factor)", OTHER_EXAMPLE),
                *((f"{name} ({ease})", name) for name, ease in cl.EXAMPLES),
            ],
            hint=f"The book's examples ({TC} p. 47) set the Ease Factor.",
        ),
        DialogField(
            "ease",
            "Ease Factor",
            "optint",
            None
            if p is not None and p.example
            else (q.ease if p is not None else None),
            hint="Blank: the example's.",
        ),
        DialogField(
            "method",
            "Made by",
            "select",
            q.method,
            options=[
                ("Letter: Communication + Church Lore", WRITTEN),
                ("Audience: Presence + Church Lore (The Gift applies)", AUDIENCE),
            ],
        ),
        DialogField(
            "scribe",
            "Scribe",
            "text",
            q.scribe,
            show_if=lambda v: v.get("method") != AUDIENCE,
            hint="Who writes it for him (blank: he writes it himself); his "
            f"Communication + Church Lore is used instead ({TC} p. 48).",
        ),
        DialogField(
            "scribe_total",
            "Scribe's Com + Lore",
            "optint",
            q.scribe_total,
            show_if=lambda v: v.get("method") != AUDIENCE and bool(v.get("scribe")),
        ),
        *(DialogField(key, label, "check", getattr(q, key)) for key, label in _FLAGS),
        DialogField(
            "clergy",
            "Clergy support",
            "select",
            str(q.clergy),
            options=[(n, str(v)) for n, v in cl.CLERGY_SUPPORT],
            hint="The highest only.",
        ),
        DialogField(
            "lay",
            "Lay support",
            "select",
            str(q.lay),
            options=[(n, str(v)) for n, v in cl.LAY_SUPPORT],
            hint="The highest only.",
        ),
        DialogField("donation", "Donation (0 to +3)", "int", q.donation),
        *(
            DialogField(
                _ARGUMENT_KEYS[ability],
                _ARGUMENT_LABELS[ability],
                "int",
                q.arguments.get(ability, 0),
                hint="Each argument is rolled when the petition is made: "
                f"Intelligence + the Ability + stress die against {cl.ARGUMENT_EASE}."
                if ability == cl.CANON_LAW
                else "",
            )
            for ability in cl.ARGUMENTS
        ),
        DialogField(
            "reputation",
            "Church Reputation",
            "int",
            q.reputation,
            hint="His Reputation with the Church: a bonus, or a penalty if bad.",
        ),
        DialogField("spells", "Spells on the deciders", "int", q.spells),
        DialogField(
            "appeal",
            "An appeal",
            "check",
            q.appeal,
            hint="Against a petition granted to another (p. 48).",
        ),
        DialogField(
            "original",
            "Its Petition Total",
            "optint",
            q.original,
            show_if=lambda v: bool(v.get("appeal")),
        ),
        DialogField(
            "late",
            f"Not in the same season (-{cl.LATE_APPEAL})",
            "check",
            q.late,
            show_if=lambda v: bool(v.get("appeal")),
        ),
        DialogField(
            "made",
            "Made now",
            "check",
            q.made,
            hint="Unticked: only planned, with no total yet.",
        ),
        DialogField(
            "season",
            "Season",
            "select",
            q.season or saga.current_season,
            options=pairs(SEASONS),
        ),
        DialogField("year", "Year", "optint", q.year),
        DialogField("note", "Note", "text", q.note),
    ]


def _clamp(value: Any, low: int, high: int) -> int:
    return min(high, max(low, int(value or 0)))


def petition_from(
    character: Character, values: dict[str, Any], existing: Petition | None
) -> Petition:
    """The petition the form describes, with his own figures as they are
    now; argument rolls already made are kept while their bonus stands."""
    method = values.get("method") or WRITTEN
    characteristic, lore, gift = cl.petitioner_terms(character, method)
    example = values.get("example") or OTHER_EXAMPLE
    typed = values.get("ease")
    ease = typed if typed is not None else cl.EXAMPLE_EASE.get(example, 9)
    scribe = (values.get("scribe") or "").strip() if method != AUDIENCE else ""
    arguments = {
        ability: _clamp(values.get(key), 0, cl.ARGUMENT_MAX)
        for ability, key in _ARGUMENT_KEYS.items()
        if _clamp(values.get(key), 0, cl.ARGUMENT_MAX)
    }
    old = existing or Petition("")
    return replace(
        old,
        ask=(values.get("ask") or "").strip(),
        example=example,
        ease=int(ease),
        method=method,
        scribe=scribe,
        scribe_total=values.get("scribe_total") if scribe else None,
        characteristic=characteristic,
        lore=lore,
        gift=gift,
        testimony=bool(values.get("testimony")),
        evidence=bool(values.get("evidence")),
        vision=bool(values.get("vision")),
        miracle=bool(values.get("miracle")),
        clergy=int(values.get("clergy") or 0),
        lay=int(values.get("lay") or 0),
        donation=_clamp(values.get("donation"), 0, cl.DONATION_MAX),
        arguments=arguments,
        argument_rolls={
            a: r
            for a, r in old.argument_rolls.items()
            if arguments.get(a) == old.arguments.get(a)
        },
        argument_botches=[
            a for a in old.argument_botches if arguments.get(a) == old.arguments.get(a)
        ],
        reputation=int(values.get("reputation") or 0),
        spells=int(values.get("spells") or 0),
        appeal=bool(values.get("appeal")),
        original=values.get("original") if values.get("appeal") else None,
        late=bool(values.get("late")) if values.get("appeal") else False,
        made=bool(values.get("made")),
        season=values.get("season") or "",
        year=values.get("year"),
        note=values.get("note") or "",
    )


def petition_live(
    character: Character, existing: Petition | None
) -> Callable[[dict[str, Any]], str]:
    """The Petition: the sum, granted or refused, and who decides."""

    def inspect(values: dict[str, Any]) -> str:
        draft = petition_from(character, values, existing)
        # Arguments not yet rolled are shown as if they count.
        for ability in draft.arguments:
            if (
                ability not in draft.argument_rolls
                and ability not in draft.argument_botches
            ):
                draft.argument_rolls[ability] = cl.ARGUMENT_EASE
        total, ease = cl.petition_total(draft), cl.petition_ease(draft)
        terms = " + ".join(f"{escape(n)} {v}" for n, v in cl.petition_terms(draft))
        lines = [f"{terms} = [b]{total}[/]"]
        if draft.appeal and draft.original is not None:
            lines.append(
                f"Overturns it at {draft.original + cl.APPEAL_MARGIN} (its total + "
                f"{cl.APPEAL_MARGIN}); a compromise is brokered above "
                f"{draft.original - cl.APPEAL_MARGIN}."
            )
        else:
            verdict = (
                ok("granted")
                if total >= ease
                else bad(f"refused (short by {ease - total})")
            )
            lines.append(
                f"Against [b]{ease}[/]: {verdict}. Decided by {cl.decider(ease)}."
            )
        if draft.arguments:
            lines.append(
                "[dim]Each argument counts only if its roll (Intelligence + the "
                f"Ability + stress die) reaches {cl.ARGUMENT_EASE}; rolled on saving.[/]"
            )
        if draft.method == AUDIENCE and draft.gift:
            lines.append(warn(f"An audience: The Gift's penalty, -{draft.gift}."))
        if draft.made and draft.year is not None:
            others = cl.petitions_this_season(
                character.church, draft.season, draft.year
            ) - (
                1
                if existing is not None
                and existing.made
                and existing.season == draft.season
                and existing.year == draft.year
                else 0
            )
            if others:
                lines.append(
                    warn("He has already petitioned this season: usually one a season.")
                )
        lines.append(
            "[dim]No die. One petition a season, and it takes no season unless "
            f"he travels ({TC} pp. 46-48).[/]"
        )
        return "\n".join(lines)

    return inspect


def petition_form(
    saga: Saga,
    character: Character,
    index: int | None = None,
    rng: random.Random | None = None,
) -> Command:
    """Petition the Church (or edit a petition): the arguments are rolled
    when it is made."""
    career = character.church
    if index is not None and not 0 <= index < len(career.petitions):
        return Refuse("Edit Petition", "Choose a petition first.")
    existing = career.petitions[index] if index is not None else None

    def apply(values: dict[str, Any]) -> list[str]:
        made = petition_from(character, values, existing)
        if made.made and any(
            a not in made.argument_rolls and a not in made.argument_botches
            for a in made.arguments
        ):
            cl.roll_arguments(saga, character, made, rng or random.Random())
        if index is None:
            career.petitions.append(made)
        else:
            career.petitions[index] = made
        if not made.made:
            return notes(f"Planned: {escape(made.ask)}.")
        return notes(
            f"{escape(made.ask)}: {cl.petition_total(made)} against "
            f"{cl.petition_ease(made)}, {cl.petition_result(made).lower()}.",
            escape(_arguments_line(made)),
        )

    return Form(
        "Petition the Church" if index is None else "Edit Petition",
        lambda: petition_fields(saga, character, existing),
        apply,
        validate=_petition_problem,
        live=petition_live(character, existing),
        save_label="Petition" if index is None else "Save",
        help_id=PETITION_HELP,
        inspector="The Petition",
    )


def _petition_problem(values: dict[str, Any]) -> str | None:
    if (
        not values.get("example")
        and values.get("ease") is None
        and not values.get("appeal")
    ):
        return "Choose an example like it, or type its Ease Factor."
    if values.get("appeal") and values.get("original") is None:
        return "Type the Petition Total of the petition appealed."
    return None


def petition_ops(saga: Saga, character: Character) -> SectionOps:
    career = character.church
    return SectionOps(
        add=lambda: petition_form(saga, character),
        edit=lambda index: petition_form(saga, character, index),
        remove=lambda index: delete(
            career.petitions, index, career.petitions[index].ask or "the petition"
        ),
        rows=lambda: [p.ask or "(unnamed)" for p in career.petitions],
    )


# -- the Canon Court --

W_CHARGE, W_ROLE, W_COURT, W_CW = 30, 10, 22, 13

ROLE_LABELS = {ACCUSED: "Accused", ACCUSER: "Accuser"}
VERDICT_LABELS = {PENDING: "Pending", "acquitted": "Acquitted", GUILTY: "Guilty"}

CANON_RULE = (
    "[dim]Canon courts shed no blood: no death or bodily punishment. The judge "
    "decides, with no jury; about a dozen oath-helpers swearing to the "
    "accused's good character acquit him (compurgation). No one need attend "
    f"more than two days' travel from his diocese ({TC} pp. 35-37).[/]"
)


def verdict_words(case: CanonCase) -> tuple[str, str]:
    """The verdict as shown, and its tone."""
    if case.verdict == GUILTY:
        words = f"Guilty: {case.punishment.lower()}" if case.punishment else "Guilty"
        return (
            words,
            "text-error" if case.punishment == cl.EXCOMMUNICATION else "text-warning",
        )
    if case.verdict == PENDING:
        return "Pending", "label"
    return "Acquitted", "text-success"


def case_entry(case: CanonCase) -> Entry:
    words, tone = verdict_words(case)
    role = ROLE_LABELS.get(case.role, case.role)
    when = _when(case.season, case.year)
    court = case.court or "A canon court"
    title = case.charge + (f": {case.what}" if case.what else "")
    punishment = (
        cl.PUNISHMENTS.get(case.punishment, "") if case.verdict == GUILTY else ""
    )
    extra = (
        "Compurgation: oath-helpers swore for the accused." if case.compurgation else ""
    )
    return Entry(
        row=_col(title, W_CHARGE)
        + _col(role, W_ROLE)
        + _col(court, W_COURT)
        + _col(when, W_CW)
        + (f"[dim]{escape(words)}[/]" if tone == "label" else _coloured(tone, words)),
        title=title,
        subtitle=f"{court} · {when}" if when else court,
        rubric="§",
        meta=f"{court.lower()} court, {when}" if when else f"{court.lower()} court",
        badge=(words, tone),
        body=escape(case.note)
        if case.note
        else f"{role} of {escape(case.charge.lower())}.",
        note=f"[i]{escape(extra)}[/]" if extra else "",
        info="\n".join(
            [
                f"[b]{escape(title)}[/]",
                f"{role}  ·  {escape(court)}  ·  {escape(when)}  ·  "
                + _coloured(tone, words),
                *([escape(punishment)] if punishment else []),
                *([escape(case.note)] if case.note else []),
                *([escape(extra)] if extra else []),
                "",
                CANON_RULE,
            ]
        ),
    )


def canon_title(career: ChurchCareer) -> str:
    return f"Canon Court ({len(career.cases)})"


def canon_header() -> str:
    return (
        "  "
        + fit("Charge", W_CHARGE)
        + fit("As", W_ROLE)
        + fit("Court", W_COURT)
        + fit("Season", W_CW)
        + "Verdict"
    )


def canon_rows(character: Character) -> list[tuple[int | None, str]]:
    found = character.church.cases
    if not found:
        return [(None, "[dim]None. Add a case with a.[/]")]
    return [(n, case_entry(c).row) for n, c in enumerate(found)]


def canon_info(character: Character, index: int | None) -> str:
    found = character.church.cases
    if index is None or not 0 <= index < len(found):
        return EMPTY_PANEL
    return case_entry(found[index]).info


def canon_fields(
    saga: Saga, character: Character, case: CanonCase | None
) -> list[DialogField]:
    c = case or CanonCase("Slander", season=saga.current_season, year=saga.current_year)
    name = character.name or "He"
    return [
        DialogField("charge", "Charge", "select", c.charge, options=pairs(cl.CHARGES)),
        DialogField(
            "what", "What", "text", c.what, placeholder="e.g. Ulrich the miller"
        ),
        DialogField(
            "role",
            f"{escape(name)} is",
            "select",
            c.role,
            options=[(ROLE_LABELS[r], r) for r in (ACCUSED, ACCUSER)],
        ),
        DialogField(
            "court",
            "Court",
            "select",
            c.court or cl.COURTS[0],
            options=pairs(cl.COURTS),
        ),
        DialogField(
            "season",
            "Season",
            "select",
            c.season or saga.current_season,
            options=pairs(SEASONS),
        ),
        DialogField("year", "Year", "optint", c.year),
        DialogField(
            "compurgation",
            "Compurgation",
            "check",
            c.compurgation,
        ),
        DialogField(
            "verdict",
            "Verdict",
            "select",
            c.verdict,
            options=[(VERDICT_LABELS[v], v) for v in VERDICTS],
        ),
        DialogField(
            "punishment",
            "Punishment",
            "select",
            c.punishment or "Monition",
            options=pairs(tuple(cl.PUNISHMENTS)),
            show_if=lambda v: v.get("verdict") == GUILTY,
        ),
        DialogField("note", "Note", "area", c.note),
    ]


def canon_live(values: dict[str, Any]) -> str:
    """The Case: what the punishment does, and a warning when compurgation
    and Guilty are both set."""
    lines = []
    guilty = values.get("verdict") == GUILTY
    if values.get("compurgation") and guilty:
        lines.append(
            warn(
                "Compurgation acquits when about a dozen oath-helpers swear: is Guilty right?"
            )
        )
    if guilty:
        punishment = values.get("punishment") or "Monition"
        lines.append(
            f"[b]{escape(punishment)}[/]: {escape(cl.PUNISHMENTS.get(punishment, ''))}"
        )
        if punishment == cl.EXCOMMUNICATION and values.get("role") != ACCUSER:
            lines.append("Shown on Holy Orders as his standing.")
    lines.append(CANON_RULE)
    return "\n".join(lines)


def case_from(values: dict[str, Any], existing: CanonCase | None) -> CanonCase:
    verdict = values.get("verdict") or PENDING
    return replace(
        existing or CanonCase(""),
        charge=values.get("charge") or cl.CHARGES[-1],
        what=(values.get("what") or "").strip(),
        role=values.get("role") or ACCUSED,
        court=values.get("court") or cl.COURTS[0],
        season=values.get("season") or "",
        year=values.get("year"),
        compurgation=bool(values.get("compurgation")),
        verdict=verdict,
        punishment=(values.get("punishment") or "Monition")
        if verdict == GUILTY
        else "",
        note=values.get("note") or "",
    )


def canon_form(saga: Saga, character: Character, index: int | None = None) -> Command:
    """Add Canon Case (or edit one): the storyguide's record of a case; an
    excommunication shows as his standing."""
    career = character.church
    if index is not None and not 0 <= index < len(career.cases):
        return Refuse("Edit Canon Case", "Choose a case first.")
    existing = career.cases[index] if index is not None else None

    def apply(values: dict[str, Any]) -> None:
        made = case_from(values, existing)
        if index is None:
            career.cases.append(made)
        else:
            career.cases[index] = made
        career.standing = cl.case_standing(career)

    return Form(
        "Add Canon Case" if index is None else "Edit Canon Case",
        lambda: canon_fields(saga, character, existing),
        apply,
        live=canon_live,
        save_label="Add" if index is None else "Save",
        help_id=CANON_HELP,
        inspector="The Case",
    )


def canon_ops(saga: Saga, character: Character) -> SectionOps:
    career = character.church
    return SectionOps(
        add=lambda: canon_form(saga, character),
        edit=lambda index: canon_form(saga, character, index),
        remove=lambda index: delete(
            career.cases, index, career.cases[index].charge or "the case"
        ),
        rows=lambda: [c.charge for c in career.cases],
    )


# -- Perform an Exorcism --

AURA_REALMS = ("Divine", "Magic", "Faerie", "Infernal", "None")


def exorcism_fields(saga: Saga, character: Character) -> list[DialogField]:
    return [
        DialogField(
            "points",
            "Faith or Confidence Points spent",
            "int",
            1,
            hint=f"At least 1; +{cl.POINT_BONUS} each.",
        ),
        DialogField("water", f"Holy water (+{cl.HOLY_WATER})", "check", True),
        DialogField("cross", f"A crucifix (+{cl.CRUCIFIX})", "check", True),
        DialogField(
            "realm", "The aura's realm", "select", "Divine", options=pairs(AURA_REALMS)
        ),
        DialogField("aura", "Aura", "int", 0),
        DialogField(
            "might", "Might the demon invested", "int", 10, hint="The Ease Factor."
        ),
        DialogField("resistance", "The energumen's Magic Resistance", "int", 0),
    ]


def _exorcism_terms(
    character: Character, values: dict[str, Any]
) -> tuple[int, list[str]]:
    return cl.exorcism_bonus(
        character.church.grade,
        int(values.get("points") or 1),
        holy_water=bool(values.get("water")),
        crucifix=bool(values.get("cross")),
        aura_realm=values.get("realm") or "None",
        aura=int(values.get("aura") or 0),
    )


def exorcism_live(character: Character) -> Callable[[dict[str, Any]], str]:
    def inspect(values: dict[str, Any]) -> str:
        total, terms = _exorcism_terms(character, values)
        might = int(values.get("might") or 0)
        lines = [
            "stress die + "
            + " + ".join(escape(t) for t in terms)
            + f" = [b]{total} + die[/]",
            f"Against [b]{might}[/]: the die must show {max(0, might - total)} or more.",
        ]
        if int(values.get("resistance") or 0):
            lines.append(
                "The total must also Penetrate the energumen's Magic Resistance."
            )
        if not cl.may_use_faith_points(character.church):
            lines.append(
                warn("Irregular: he can't use Faith Points until he confesses.")
            )
        lines.append(
            "[dim]Any cleric may exorcise; an ordained exorcist gets +1. A Divine "
            f"power: other realms' auras don't hinder it (DE p. 411; {TC} p. 34).[/]"
        )
        return "\n".join(lines)

    return inspect


def exorcism_form(
    saga: Saga, character: Character, rng: random.Random | None = None
) -> Form:
    """Perform an Exorcism: a calculator; Roll rolls it and says what came
    of it (the Points spent are the player's to mark)."""

    def apply(values: dict[str, Any]) -> list[str]:
        total, _terms = _exorcism_terms(character, values)
        might = int(values.get("might") or 0)
        roll = dice.roll(rng or random.Random(), total, ease_factor=might, saga=saga)
        shown = "a botch" if roll.die.botched else str(roll.die.value)
        lines = [
            f"Exorcism: the die shows {shown}, total {roll.total} against {might}."
        ]
        if roll.succeeded:
            lines.append("The demon is exorcised.")
            resistance = int(values.get("resistance") or 0)
            if resistance:
                penetration = roll.total - might
                lines.append(
                    f"Penetration {penetration} against Magic Resistance {resistance}: "
                    + (
                        "it penetrates."
                        if penetration > resistance
                        else "it does not penetrate."
                    )
                )
        else:
            lines.append("The demon stays.")
        return notes(*lines)

    return Form(
        "Perform an Exorcism",
        lambda: exorcism_fields(saga, character),
        apply,
        live=exorcism_live(character),
        save_label="Roll",
        cancel_label="Close",
        help_id=EXORCISM_HELP,
        inspector="The Rite",
    )


# -- the tab as a whole --

EMPTY_PANEL = "[dim]Choose an ordination, a petition or a case to see it in full.[/]"


def ordination_entries(character: Character) -> list[Entry]:
    return [ordination_entry(o) for o in character.church.ordinations]


def petition_entries(character: Character) -> list[Entry]:
    return [petition_entry(p) for p in character.church.petitions]


def case_entries(character: Character) -> list[Entry]:
    return [case_entry(c) for c in character.church.cases]


def ops(saga: Saga, character: Character) -> dict[str, SectionOps]:
    """Each Church section's verbs."""
    return {
        ORDERS_SECTION: orders_ops(saga, character),
        ORDINATIONS_SECTION: ordination_ops(saga, character),
        PETITIONS_SECTION: petition_ops(saga, character),
        CANON_SECTION: canon_ops(saga, character),
    }


def exorcism_step(saga: Saga, character: Character) -> Command:
    """More's Perform an Exorcism."""
    return exorcism_form(saga, character)
