"""Lab work planned ahead: the laboratory's queue and its text, scheduling
lab work, and the Lab Texts, effects and spells it produces."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field, replace

from .. import catalog
from .. import spells as spl
from ..markup import escape, problem, todo
from ..models import (
    SEASONS,
    TEXT_ENCHANTMENT,
    TEXT_LONGEVITY,
    TEXT_SPELL,
    Book,
    Character,
    EnchantedDevice,
    ExperimentalEffect,
    InstilledEffect,
    Laboratory,
    Saga,
    SeasonPlan,
    Spell,
    SpellDesign,
    new_instance_id,
    next_season,
)
from ..rules import activities as rules
from ..rules import book_seasons as bs
from ..rules import enchant_seasons as es
from ..rules import enchantment, experiment, lab_seasons
from ..rules import familiar_seasons as fs
from ..rules import laboratory_seasons as ls
from ..tables import Table
from . import pairs
from .plans import plan_for, plan_summary, schedule, set_plan, work_text
from .projection import projection

#: How many seasons the laboratory's Planning tab shows, the current first.
QUEUE_LENGTH = 4


def upcoming(saga: Saga, count: int = QUEUE_LENGTH) -> list[tuple[str, int]]:
    """The current season and the ones after it."""
    seasons_: list[tuple[str, int]] = [(saga.current_season, saga.current_year)]
    while len(seasons_) < count:
        seasons_.append(next_season(*seasons_[-1]))
    return seasons_


#: How far ahead the Planning tab looks for scheduled lab work.
QUEUE_HORIZON = 40


@dataclass
class QueueRow:
    """One row of the laboratory's Planning tab: a scheduled activity and
    the seasons it spans (or a season with nothing planned). For inventing,
    the work is where it stands at its last season."""

    season: str
    year: int
    plan: SeasonPlan | None
    end_season: str = ""
    end_year: int = 0
    work: lab_seasons.LabWork | None = None
    problems: list[str] = field(default_factory=list)

    @property
    def span(self) -> str:
        first = _season_label(self.season, self.year)
        if not self.end_season or (self.end_season, self.end_year) == (
            self.season,
            self.year,
        ):
            return first
        return f"{first} - {_season_label(self.end_season, self.end_year)}"


def lab_queue(saga: Saga, lab: Laboratory) -> list[QueueRow]:
    """The owner's scheduled activities from this season on, one row each
    with the seasons it spans; seasons with nothing planned in between,
    and the first free season after the last. Each row's work is worked
    out from the saga as the seasons before it leave it (projection.py):
    an invention's points carry on, and a higher Art raises the Lab
    Total."""
    owner = saga.character(lab.owner_id)
    if owner is None:
        return [QueueRow(saga.current_season, saga.current_year, None)]
    seasons_ = upcoming(saga, QUEUE_HORIZON)
    last = max(
        (
            i
            for i, (season, year) in enumerate(seasons_)
            if plan_for(saga, owner, season, year) is not None
        ),
        default=-1,
    )
    rows: list[QueueRow] = []
    ahead = projection(saga)
    for season, year in seasons_[: last + 2]:
        plan = plan_for(saga, owner, season, year)
        work = None
        found: list[str] = []
        if plan is not None and plan.lab_id:
            found, work = ahead.work(owner.id, season, year) or lab_seasons.work(
                saga, owner, plan
            )
        previous = rows[-1] if rows else None
        if (
            previous is not None
            and plan is not None
            and previous.plan is not None
            and plan.lab_id
            and previous.plan.lab_id
            and plan.activity == previous.plan.activity
            and plan.activity in lab_seasons.MULTI_SEASON
            and project_key(plan) == project_key(previous.plan)
            and not found
            and not previous.problems
        ):
            previous.end_season, previous.end_year = season, year
            previous.work = work
            continue
        rows.append(QueueRow(season, year, plan, season, year, work, found))
    return rows


def _season_label(season: str, year: int) -> str:
    return f"{season} {year}"


def _progress(work: lab_seasons.LabWork, plan: SeasonPlan) -> str:
    """A queue row's short progress: "8/15 points", "invented"."""
    progress = _PROGRESS.get(plan.activity)
    if progress is not None:
        shown = progress(work, plan)
        if shown is not None:
            return shown
    if work.finished:
        learned = (lab_seasons.LAB_TEXT, lab_seasons.TAUGHT_SPELLS)
        return "learned" if plan.activity in learned else "invented"
    return f"{work.points_after}/{work.level} points"


def _when_finished(
    word: str,
) -> Callable[[lab_seasons.LabWork, SeasonPlan], str | None]:
    """`word` once the work is finished; until then, its points."""
    return lambda work, plan: word if work.finished else None


#: A queue row's progress for each kind of lab work (Strategy, as a table);
#: None, or work not listed, shows its points until it is finished.
_PROGRESS: dict[str, Callable[[lab_seasons.LabWork, SeasonPlan], str | None]] = {
    lab_seasons.EXTRACT: lambda work, plan: f"+{work.vis_gained} {work.vis_gained_art}",
    lab_seasons.FIX_AC: lambda work, plan: "fixed",
    lab_seasons.LONGEVITY: lambda work, plan: f"aging -{work.longevity}",
    bs.DECODE_TEXT: _when_finished("decoded"),
    lab_seasons.TAMING: _when_finished("tamed"),
    ls.MOVE: lambda work, plan: "moved" if plan.by_spell or work.finished else "moving",
    ls.BUILD: lambda work, plan: "finished" if work.second_season else "set up (Basic)",
    ls.REFINE: lambda work, plan: f"Refinement {work.refinement}",
    ls.TAKE_OVER: lambda work, plan: f"Refinement {work.refinement}",
    fs.BIND: lambda work, plan: "bound",
    fs.EMPOWER: _when_finished("instilled"),
    es.OPEN: lambda work, plan: "opened",
    es.ATTUNE: lambda work, plan: "attuned",
    es.INVESTIGATE: lambda work, plan: f"against level {work.level}",
    es.CHARGED_WORK: lambda work, plan: f"{work.charges} charge(s)",
    es.LESSER_WORK: lambda work, plan: "made",
    es.INSTIL: _when_finished("instilled"),
}


def _queue_cells(saga: Saga, lab: Laboratory) -> list[tuple[str, str]]:
    """Each coming season's span and what its owner has planned (markup)."""
    owner = saga.character(lab.owner_id)
    cells = []
    for row in lab_queue(saga, lab):
        if owner is None:
            what = "[dim]no owner[/]"
        elif row.plan is None:
            what = todo("nothing planned")
        else:
            what = escape(plan_summary(saga, owner, row.plan))
            if not row.plan.lab_id:
                what += f" [dim](on {escape(owner.name)}'s sheet)[/]"
            elif row.problems:
                what += f"  {problem("can't be done (see below)")}"
            elif row.work is not None:
                what += f"  [dim]{escape(_progress(row.work, row.plan))}[/]"
        cells.append((row.span, what))
    return cells


def lab_queue_rows(saga: Saga, lab: Laboratory) -> list[tuple[int, str]]:
    """The laboratory Planning tab's rows: each coming season and what its
    owner has planned."""
    return [
        (index, f"{when.ljust(27)}{what}")
        for index, (when, what) in enumerate(_queue_cells(saga, lab))
    ]


def lab_queue_table(saga: Saga, lab: Laboratory) -> Table:
    """lab_queue_rows as a table (markup): the seasons, and the plan."""
    return Table(
        ["Seasons", "Plan"],
        [[escape(when), what] for when, what in _queue_cells(saga, lab)],
        markup=True,
        stretch=1,
    )


def lab_queue_info(
    saga: Saga, lab: Laboratory, index: int | None, *, plan_hint: str = "Press e"
) -> str:
    """The Planning tab's details panel: the chosen season's plan and its
    Lab Total, line by line. `plan_hint` says how to plan a free season
    ("Press e" on the terminal, "Click Plan" on the desktop)."""
    if index is None:
        return (
            "[dim]Select an activity to see its plan and Lab Total; e plans a "
            "free season.[/]"
        )
    rows = lab_queue(saga, lab)
    if index >= len(rows):
        return ""
    row = rows[index]
    owner = saga.character(lab.owner_id)
    head = f"[b]{row.span}[/]"
    if owner is None:
        return head + "\n[dim]Give the laboratory an owner to plan its seasons.[/]"
    if row.plan is None:
        return head + f"\n[dim]Nothing planned. {plan_hint} to plan lab work.[/]"
    lines = [head, f"[b]{escape(plan_summary(saga, owner, row.plan))}[/]"]
    if not row.plan.lab_id:
        lines.append(
            f"[dim]Planned on {escape(owner.name)}'s sheet. Planning lab work "
            "here replaces it.[/]"
        )
        return "\n".join(lines)
    lines += [problem(escape(p)) for p in row.problems]
    if row.work is not None:
        lines.append(escape(work_text(row.work, row.plan)))
        for line in row.work.lab_total.lines:
            if line.amount is not None:
                lines.append(f"  {escape(line.label)} {line.amount:+g}")
            elif line.multiplier is not None:
                lines.append(f"  {escape(line.label)} x{line.multiplier:g}")
    if row.plan.days_away:
        lines.append(f"{row.plan.days_away} days away from the laboratory.")
    return "\n".join(lines)


def scheduled_with(saga: Saga, plan: SeasonPlan) -> list[SeasonPlan]:
    """`plan` and the later seasons scheduled to continue it (a plan saved
    for several seasons, or lab work on the same project), in season
    order."""
    key = project_key(plan) if plan.lab_id else None
    start = (plan.year, SEASONS.index(plan.season))
    found = [plan, *_subject_plans(saga, plan)]
    if plan.series:
        found += [
            p
            for p in saga.season_plans
            if p is not plan
            and p.character_id == plan.character_id
            and p.series == plan.series
            and (p.year, SEASONS.index(p.season)) > start
        ]
    elif key is not None:
        found += [
            p
            for p in saga.season_plans
            if p is not plan
            and p.character_id == plan.character_id
            and p.lab_id
            and project_key(p) == key
            and (p.year, SEASONS.index(p.season)) > start
        ]
    return sorted(found, key=lambda p: (p.year, SEASONS.index(p.season)))


def plan_lab_work(saga: Saga, plan: SeasonPlan) -> list[SeasonPlan]:
    """Lock in a lab plan and, for an invention that will take more seasons,
    the same plan for each season it's projected to need (where nothing else
    is planned). Returns the plans added after the first."""
    # Rescheduling replaces the seasons planned to continue it.
    start = (plan.year, SEASONS.index(plan.season))
    key = project_key(plan)
    replaced = [
        p
        for p in saga.season_plans
        if p.character_id == plan.character_id
        and p.lab_id
        and key is not None
        and project_key(p) == key
        and (p.year, SEASONS.index(p.season)) > start
    ]
    for old in replaced:
        pairs.drop_pairs(saga, old)
        saga.season_plans.remove(old)
    for old in _subject_plans(saga, plan):
        saga.season_plans.remove(old)
    set_plan(saga, plan)
    character = saga.character(plan.character_id)
    if character is not None:
        pairs.make_pairs(saga, character, plan)
    if character is not None and plan.activity == lab_seasons.LONGEVITY:
        _plan_subject(saga, character, plan)
    if character is None or plan.activity not in lab_seasons.MULTI_SEASON:
        return []
    found, work = lab_seasons.work(saga, character, plan)
    if found or work is None:
        return []
    added = schedule(saga, plan, lab_seasons.seasons_left(work))
    for each in added:
        pairs.make_pairs(saga, character, each)
    return added


def _subject_plans(saga: Saga, plan: SeasonPlan) -> list[SeasonPlan]:
    """The season planned for the subject of the magus's Longevity Ritual
    in `plan`'s season."""
    return [
        p
        for p in saga.season_plans
        if p.activity == lab_seasons.LONGEVITY_SUBJECT
        and p.subject_id == plan.character_id
        and (p.season, p.year) == (plan.season, plan.year)
    ]


def _plan_subject(saga: Saga, magus: Character, plan: SeasonPlan) -> None:
    """Plan the subject's season with the magus (when they're planned season
    by season and have nothing else planned)."""
    subject = lab_seasons.subject_of(saga, magus, plan)
    if subject is None or subject is magus or not rules.is_planned(subject):
        return
    if plan_for(saga, subject, plan.season, plan.year) is not None:
        return
    set_plan(
        saga,
        SeasonPlan(
            subject.id,
            plan.year,
            plan.season,
            lab_seasons.LONGEVITY_SUBJECT,
            details=f"The subject of {magus.name}'s Longevity Ritual.",
            subject_id=magus.id,
        ),
    )


def _lab_text_book(saga: Saga, magus: Character, lab: Laboratory, spell: Spell) -> Book:
    ids = {b.id for b in saga.books}
    base = f"labtext_{spell.id}_{magus.id}"
    book_id, n = base, 2
    while book_id in ids:
        book_id, n = f"{base}_{n}", n + 1
    return Book(
        id=book_id,
        name=f"Lab Text: {spell.name}",
        type="Lab Text",
        author=magus.name,
        owner_kind="laboratory",
        owner_id=lab.id,
        year_published=saga.current_year,
        spell_id=spell.id,
        spell_name=spell.name,
        raw=True,
        author_id=magus.id,
        text_kind=TEXT_SPELL,
    )


def _effect_text(
    saga: Saga,
    magus: Character,
    lab: Laboratory,
    device: EnchantedDevice,
    effect: InstilledEffect,
) -> Book:
    """The raw Lab Text of an effect just instilled: a snapshot
    of the effect and of the device it went into (the device may be given
    away or lost; the text is exact to that shape and material)."""
    kind = es.text_device_type(device)
    parts = [
        " ".join(p for p in (c.size, c.material, c.description) if p)
        for c in device.components
    ]
    return Book(
        id=f"labtext_effect_{magus.id}_{new_instance_id()}",
        name=f"Lab Text: {effect.name or 'an effect'} ({device.name})",
        type="Lab Text",
        author=magus.name,
        author_id=magus.id,
        raw=True,
        owner_kind="laboratory",
        owner_id=lab.id,
        year_published=saga.current_year,
        # The level it was instilled at (with its uses a day and the rest).
        level=enchantment.modified_level(device, effect),
        text_kind=TEXT_ENCHANTMENT,
        technique=effect.technique,
        form=effect.form,
        effect_rdt=" / ".join(
            part or "?" for part in (effect.range, effect.duration, effect.target)
        ),
        device_type=kind,
        shape_material="; ".join(p for p in parts if p),
        description=effect.description,
        experimental_effects=[replace(e) for e in effect.experimental_effects],
    )


def _longevity_text(
    saga: Saga,
    magus: Character,
    lab: Laboratory,
    subject: Character,
    lab_total: int,
    extra_vis: int = 0,
) -> Book:
    """The raw Lab Text of a Longevity Ritual: Creo Corpus, its
    level the ritual's Lab Total; it lets the ritual be performed again."""
    return Book(
        id=f"labtext_longevity_{magus.id}_{new_instance_id()}",
        name=f"Lab Text: Longevity Ritual for {subject.name}",
        type="Lab Text",
        author=magus.name,
        author_id=magus.id,
        raw=True,
        owner_kind="laboratory",
        owner_id=lab.id,
        year_published=saga.current_year,
        level=max(0, lab_total),
        text_kind=TEXT_LONGEVITY,
        technique="Creo",
        form="Corpus",
        ritual_subject=subject.name,
        ritual_extra_vis=max(0, extra_vis),
    )


def project_key(plan: SeasonPlan) -> str | None:
    """What ties a plan's seasons of invention together: its design, or the
    spell it invents."""
    if plan.activity == es.INSTIL:
        return f"effect:{plan.effect_id}" if plan.effect_id else None
    if plan.activity == fs.EMPOWER:
        return f"bond:{plan.effect_id}" if plan.effect_id else None
    if plan.activity == lab_seasons.TAMING:
        return f"taming:{plan.title.strip()}"
    if plan.activity == bs.DECODE_TEXT:
        return f"decode:{plan.book_id}" if plan.book_id else None
    if plan.design is not None:
        return f"design:{plan.design.key}"
    return plan.spell_id


def _with_effects(
    saga: Saga, magus: Character, spell: Spell, effects: list[ExperimentalEffect]
) -> Spell:
    """The spell as invented with its experimental effects: the magus's own
    record (a copy when it was someone else's), which anyone learning it
    learns, warts and all."""
    if not any(s is spell for s in magus.invented_spells):
        own = spl.add_invented_spell(
            saga, magus, spell.name, spell.technique, spell.form
        )
        for attribute in (
            "level",
            "description",
            "requisites",
            "range",
            "duration",
            "target",
            "ritual",
            "base_level",
        ):
            setattr(own, attribute, getattr(spell, attribute))
        own.source = "Invented"
        spell = own
    spell.experimental_effects += effects
    experiment.apply_changes(spell, effects)
    return spell


def _invented_spell(saga: Saga, magus: Character, design: SpellDesign) -> Spell:
    """The spell a finished design gives: the spell it started from when it
    wasn't changed, otherwise a new spell of the magus's own."""
    designed = lab_seasons.design_spell(design)
    source = catalog.find_spell(saga, design.source_spell_id)
    if source is not None and lab_seasons.same_spell(source, designed):
        return source
    spell = spl.add_invented_spell(
        saga, magus, designed.name, designed.technique, designed.form
    )
    for attribute in (
        "level",
        "description",
        "requisites",
        "range",
        "duration",
        "target",
        "ritual",
        "base_level",
    ):
        setattr(spell, attribute, getattr(designed, attribute))
    spell.source = "Invented"
    return spell
