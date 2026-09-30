"""The Invent Spell screen (STORY-901, laid out with Hedda 2026-09-29): a
season of lab work planned on the laboratory's Planning tab. Start from a
spell (or a blank design), change anything -- name, effect, Arts,
requisites, base level, Range, Duration, Target -- and see the level, the
Lab Total and when the spell will be invented, all worked out as you type.

The other lab work of a season is planned here too (STORY-907):
extracting vis, fixing an Arcane Connection and Longevity Rituals, each
with its own few fields in place of the spell design.

A full screen rather than a FieldsDialog: it has too many fields for one
field per row at 120 x 45 (agreed with Hedda)."""

from __future__ import annotations

import uuid
from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Checkbox, Input, Label, Select, Static, TextArea

from .. import spells as spl
from ..arts import FORMS, TECHNIQUES
from ..markup import escape
from ..models import (
    Character,
    Laboratory,
    Saga,
    SeasonPlan,
    Spell,
    SpellDesign,
    next_season,
)
from ..rules import lab_seasons, spell_levels
from ..rules import seasons as season_rules
from .fields import ModalDialog
from .pickers import SpellChooserScreen

#: The drop-down choice for a Range/Duration/Target the app doesn't list.
OTHER = "__other__"
#: The design Range/Duration/Target select ids, by kind.
_KINDS: tuple[str, ...] = ("range", "duration", "target")
_STANDARD = {
    "range": spell_levels.RANGE_STEPS,
    "duration": spell_levels.DURATION_STEPS,
    "target": spell_levels.TARGET_STEPS,
}


def _int(text: str) -> int | None:
    try:
        return int(text.strip())
    except ValueError:
        return None


class InventSpellScreen(ModalDialog[SeasonPlan | None]):
    """Plan a season of lab work: invent a spell (from a spell or a blank
    design) or invent one from a Lab Text. Dismisses with the plan, or None
    if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    InventSpellScreen {
        align: center middle;
    }

    #inv-dialog {
        width: 118;
        max-width: 100%;
        height: auto;
        max-height: 100%;
        border: round $accent;
        padding: 0 1;
        background: $surface;
    }

    #inv-scroll {
        height: auto;
    }

    .inv-row {
        width: 100%;
        height: 1;
        margin-bottom: 1;
    }

    .inv-row Label {
        width: auto;
        padding-right: 1;
    }

    .inv-title {
        width: 100%;
        height: 1;
        text-style: bold;
        color: $text-muted;
    }

    #inv-header {
        width: 100%;
        height: 1;
        text-style: bold;
    }

    #inv-design {
        width: 100%;
        height: auto;
    }

    #inv-start {
        width: 64;
    }

    #inv-new {
        width: auto;
        margin-left: 2;
    }

    InventSpellScreen Checkbox {
        width: 5;
        min-width: 5;
    }

    #inv-name, #inv-notes, #inv-base-effect {
        width: 1fr;
    }

    #inv-description {
        height: 7;
        margin-bottom: 1;
    }

    .inv-art {
        width: 16;
    }

    .inv-rdt {
        width: 24;
    }

    .inv-num {
        width: 6;
    }

    #inv-requisites {
        width: 18;
    }

    #inv-similar, #inv-lab-text, #inv-subject {
        width: 50;
    }

    #inv-vis-from {
        width: 40;
    }

    #inv-vis-art {
        width: 14;
    }

    #inv-connection {
        width: 1fr;
    }

    #inv-work, #inv-common {
        width: 100%;
        height: auto;
    }

    .inv-other {
        width: 18;
    }

    #inv-level {
        height: auto;
        margin-bottom: 1;
    }

    #inv-results {
        width: 100%;
        height: auto;
    }

    #inv-total {
        width: 44;
        height: auto;
    }

    #inv-when {
        width: 1fr;
        height: auto;
        padding-left: 4;
    }

    #inv-error {
        color: $text-error;
        height: auto;
    }

    #inv-buttons {
        width: 100%;
        height: auto;
        align-horizontal: right;
    }
    """

    def __init__(
        self,
        saga: Saga,
        magus: Character,
        lab: Laboratory,
        season: str,
        year: int,
        existing: SeasonPlan | None,
        *,
        activity: str | None = None,
    ) -> None:
        """`activity`: what a new plan starts as (None: nothing chosen)."""
        super().__init__()
        self.saga = saga
        self.magus = magus
        self.lab = lab
        self.season = season
        self.year = year
        lab_plan = existing if existing is not None and existing.lab_id else None
        self.initial = lab_plan
        self.initial_activity = lab_plan.activity if lab_plan else activity
        design = lab_plan.design if lab_plan and lab_plan.design else None
        if design is None and lab_plan and lab_plan.spell_id:
            spell = spl.find_spell(saga, lab_plan.spell_id)
            design = self._design_from(spell) if spell else None
        self.key = design.key if design else uuid.uuid4().hex[:12]
        self.source_id = design.source_spell_id if design else None
        self.printed_level = design.printed_level if design else None
        vf_ids = {vf.vf_id for vf in magus.virtues_flaws}
        self.parameter_options = {
            kind: [(name, name) for name in _STANDARD[kind]]
            + [
                (f"{e.name} (as {e.costs_as})", e.name)
                for e in spell_levels.extra_parameters(kind, vf_ids)
            ]
            + [("Other...", OTHER)]
            for kind in _KINDS
        }
        self._design = design
        self._ready = False

    # -- layout --------------------------------------------------------------

    def compose(self) -> ComposeResult:
        plan = self.initial
        design = self._design
        known = [
            (escape(spell.name), spell.id)
            for k in self.magus.spells_known
            if (spell := spl.find_spell(self.saga, k.spell_id)) is not None
        ]
        with Vertical(id="inv-dialog"):
            yield Static(self._header(self.initial_activity or ""), id="inv-header")
            with VerticalScroll(id="inv-scroll"):
                with Horizontal(classes="inv-row"):
                    yield Label("Lab work")
                    yield Select(
                        [
                            (season_rules.ACTIVITIES[key].label, key)
                            for key in lab_seasons.LAB_ACTIVITIES
                        ],
                        value=self.initial_activity or Select.NULL,
                        prompt="(none)",
                        id="inv-activity",
                        compact=True,
                    )
                with Vertical(id="inv-design"):
                    with Horizontal(classes="inv-row"):
                        yield Label("Start from")
                        yield Button(self._start_label(), id="inv-start", compact=True)
                        yield Button("New spell", id="inv-new", compact=True)
                    with Horizontal(classes="inv-row"):
                        yield Label("Name      ")
                        yield Input(
                            design.name if design else "", id="inv-name", compact=True
                        )
                    yield Label("Effect")
                    yield TextArea(
                        design.description if design else "", id="inv-description"
                    )
                    yield Static("── Effect ─────────", classes="inv-title")
                    with Horizontal(classes="inv-row"):
                        yield Label("Technique")
                        yield Select(
                            [(t, t) for t in TECHNIQUES],
                            value=(
                                design.technique
                                if design and design.technique
                                else Select.NULL
                            ),
                            prompt="(choose)",
                            id="inv-technique",
                            classes="inv-art",
                            compact=True,
                        )
                        yield Label(" Form")
                        yield Select(
                            [(f, f) for f in FORMS],
                            value=(
                                design.form if design and design.form else Select.NULL
                            ),
                            prompt="(choose)",
                            id="inv-form",
                            classes="inv-art",
                            compact=True,
                        )
                        yield Label(" Requisites")
                        yield Input(
                            ", ".join(design.requisites) if design else "",
                            placeholder="e.g. Rego",
                            id="inv-requisites",
                            compact=True,
                        )
                        yield Label(" Base level")
                        yield Input(
                            ""
                            if not design or design.base_level is None
                            else str(design.base_level),
                            id="inv-base",
                            classes="inv-num",
                            compact=True,
                        )
                        yield Label(" Ritual")
                        yield Checkbox(
                            "",
                            value=bool(design and design.ritual),
                            id="inv-ritual",
                            compact=True,
                        )
                    with Horizontal(classes="inv-row"):
                        for kind in _KINDS:
                            yield Label(("" if kind == "range" else " ") + kind.title())
                            current = getattr(design, kind) if design else ""
                            values = [v for _, v in self.parameter_options[kind]]
                            choice = (
                                current
                                if current in values
                                else OTHER
                                if current
                                else values[0]
                            )
                            yield Select(
                                self.parameter_options[kind],
                                value=choice,
                                allow_blank=False,
                                id=f"inv-{kind}",
                                classes="inv-rdt",
                                compact=True,
                            )
                    with Horizontal(classes="inv-row", id="inv-other-row"):
                        for kind in _KINDS:
                            current = getattr(design, kind) if design else ""
                            steps = design.custom_steps.get(kind) if design else None
                            yield Label(
                                ("" if kind == "range" else " ") + f"Other {kind}"
                            )
                            yield Input(
                                current if current not in _STANDARD[kind] else "",
                                placeholder="name",
                                id=f"inv-{kind}-name",
                                classes="inv-other",
                                compact=True,
                            )
                            yield Input(
                                "" if steps is None else str(steps),
                                placeholder="+n",
                                id=f"inv-{kind}-steps",
                                classes="inv-num",
                                compact=True,
                            )
                    with Horizontal(classes="inv-row"):
                        yield Label("Size / extra magnitudes")
                        yield Input(
                            str(design.extra_magnitudes) if design else "0",
                            id="inv-extra",
                            classes="inv-num",
                            compact=True,
                        )
                        yield Label(" Base effect")
                        yield Input(
                            design.base_effect if design else "",
                            placeholder="the guideline used",
                            id="inv-base-effect",
                            compact=True,
                        )
                    yield Static("", id="inv-level")
                with Horizontal(classes="inv-row", id="inv-labtext"):
                    yield Label("Lab Text")
                    yield Select(
                        [
                            (escape(b.name), b.id)
                            for b in lab_seasons.lab_texts(self.saga, self.magus)
                        ],
                        value=(plan.book_id if plan and plan.book_id else Select.NULL),
                        prompt="(choose the Lab Text)",
                        id="inv-lab-text",
                        compact=True,
                    )
                with Vertical(id="inv-work"):
                    with Horizontal(classes="inv-row", id="inv-connection-row"):
                        yield Label("Connection to")
                        yield Select(
                            self._connections(),
                            value=self._connection_value(plan),
                            prompt="(choose; add them on the Inventory tab)",
                            id="inv-connection",
                            compact=True,
                        )
                    with Horizontal(classes="inv-row", id="inv-subject-row"):
                        yield Label("For")
                        yield Select(
                            self._subjects(),
                            value=(
                                plan.subject_id
                                if plan and plan.subject_id
                                else self.magus.id
                            ),
                            allow_blank=False,
                            id="inv-subject",
                            compact=True,
                        )
                        yield Label(" Vis")
                        yield Select(
                            [(art, art) for art in lab_seasons.LONGEVITY_VIS_ARTS],
                            value=(
                                plan.vis_art
                                if plan
                                and plan.vis_art in lab_seasons.LONGEVITY_VIS_ARTS
                                else "Creo"
                            ),
                            allow_blank=False,
                            id="inv-vis-art",
                            compact=True,
                        )
                        yield Label(" Extra pawns")
                        yield Input(
                            str(plan.extra_vis) if plan else "0",
                            id="inv-extra-vis",
                            classes="inv-num",
                            compact=True,
                        )
                    with Horizontal(classes="inv-row"):
                        yield Label("Vis", id="inv-vis-from-label")
                        yield Select(
                            [
                                ("the laboratory's raw vis", "laboratory"),
                                (
                                    f"{escape(self.magus.name)}'s raw vis",
                                    "character",
                                ),
                            ],
                            value=(
                                plan.vis_from
                                if plan and plan.vis_from
                                else "laboratory"
                            ),
                            allow_blank=False,
                            id="inv-vis-from",
                            compact=True,
                        )
                with Vertical(id="inv-common"):
                    yield Static("── Lab work ────────", classes="inv-title")
                    with Horizontal(classes="inv-row"):
                        yield Label("Similar spell known")
                        yield Select(
                            known,
                            value=(
                                plan.similar_spell_id
                                if plan
                                and plan.similar_spell_id in [v for _, v in known]
                                else Select.NULL
                            ),
                            prompt="(none)",
                            id="inv-similar",
                            compact=True,
                        )
                        if lab_seasons.has_focus(self.magus):
                            yield Label(" Magical Focus")
                            yield Checkbox(
                                "",
                                value=bool(plan and plan.focus),
                                id="inv-focus",
                                compact=True,
                            )
                        if lab_seasons.theory_specialty(self.magus):
                            yield Label(
                                f" Magic Theory ({escape(lab_seasons.theory_specialty(self.magus))})"
                            )
                            yield Checkbox(
                                "",
                                value=bool(plan and plan.theory_specialty),
                                id="inv-specialty",
                                compact=True,
                            )
                    with Horizontal(classes="inv-row"):
                        yield Label("Days away")
                        yield Input(
                            str(plan.days_away) if plan else "0",
                            id="inv-days",
                            classes="inv-num",
                            compact=True,
                        )
                        yield Label(
                            " (10 cost nothing, 11-20 lower the Lab Total, more rule it out)   Other"
                        )
                        yield Input(
                            str(plan.other_modifier) if plan else "0",
                            id="inv-other",
                            classes="inv-num",
                            compact=True,
                        )
                    with Horizontal(classes="inv-row"):
                        yield Label("Notes")
                        yield Input(
                            plan.details if plan else "", id="inv-notes", compact=True
                        )
                    with Horizontal(id="inv-results"):
                        yield Static("", id="inv-total")
                        yield Static("", id="inv-when")
            yield Static("", id="inv-error")
            with Horizontal(id="inv-buttons"):
                yield Button("Schedule", id="btn-save", variant="primary", compact=True)
                yield Button("Cancel", id="btn-cancel", compact=True)
                yield Button("Reset", id="btn-reset", compact=True)

    def on_mount(self) -> None:
        self._ready = True
        self._refresh()
        self._fit()

    def on_resize(self) -> None:
        self._fit()

    def _fit(self) -> None:
        """The dialog is as tall as its content; past the screen's height,
        the form scrolls and the buttons stay in view."""
        # Border 2, header 1, error up to 2, buttons 1.
        self.query_one("#inv-scroll").styles.max_height = max(self.size.height - 6, 8)

    # -- reading the form ------------------------------------------------------

    def _value(self, selector: str) -> str:
        return self.query_one(selector, Input).value

    def _select(self, selector: str) -> str | None:
        value = self.query_one(selector, Select).value
        return value if isinstance(value, str) else None

    def _checked(self, selector: str) -> bool:
        found = self.query(selector)
        return bool(found) and bool(found.first(Checkbox).value)

    def _current_design(self) -> SpellDesign:
        custom: dict[str, int] = {}
        chosen: dict[str, str] = {}
        for kind in _KINDS:
            value = self._select(f"#inv-{kind}") or ""
            if value == OTHER:
                name = self._value(f"#inv-{kind}-name").strip() or "Other"
                chosen[kind] = name
                steps = _int(self._value(f"#inv-{kind}-steps"))
                if steps is not None:
                    custom[kind] = steps
            else:
                chosen[kind] = value
        return SpellDesign(
            key=self.key,
            name=self._value("#inv-name").strip(),
            technique=self._select("#inv-technique") or "",
            form=self._select("#inv-form") or "",
            requisites=spl.parse_requisites(self._value("#inv-requisites")),
            base_level=_int(self._value("#inv-base")),
            range=chosen["range"],
            duration=chosen["duration"],
            target=chosen["target"],
            custom_steps=custom,
            extra_magnitudes=_int(self._value("#inv-extra")) or 0,
            ritual=self._checked("#inv-ritual"),
            description=self.query_one("#inv-description", TextArea).text.rstrip(),
            base_effect=self._value("#inv-base-effect").strip(),
            source_spell_id=self.source_id,
            printed_level=self.printed_level,
        )

    def current_plan(self) -> SeasonPlan:
        activity = self._select("#inv-activity") or ""
        inventing = activity == lab_seasons.INVENT
        spell_work = activity in lab_seasons.SPELL_ACTIVITIES
        longevity = activity == lab_seasons.LONGEVITY
        subject = self._select("#inv-subject")
        return SeasonPlan(
            character_id=self.magus.id,
            year=self.year,
            season=self.season,
            activity=activity,
            lab_id=self.lab.id,
            design=self._current_design() if inventing else None,
            book_id=(
                self._select("#inv-lab-text")
                if activity == lab_seasons.LAB_TEXT
                else None
            ),
            similar_spell_id=self._select("#inv-similar") if inventing else None,
            days_away=_int(self._value("#inv-days")) or 0,
            focus=self._checked("#inv-focus"),
            theory_specialty=self._checked("#inv-specialty"),
            other_modifier=_int(self._value("#inv-other")) or 0,
            details=self._value("#inv-notes").strip(),
            vis_from="" if spell_work else (self._select("#inv-vis-from") or ""),
            subject_id=(
                subject if longevity and subject and subject != self.magus.id else None
            ),
            vis_art=(self._select("#inv-vis-art") or "") if longevity else "",
            extra_vis=(_int(self._value("#inv-extra-vis")) or 0) if longevity else 0,
            connection_id=(
                self._select("#inv-connection")
                if activity == lab_seasons.FIX_AC
                else None
            ),
        )

    def _connections(self) -> list[tuple[str, str]]:
        """The lab's Arcane Connections not yet fixed (and the plan's own)."""
        mine = self.initial.connection_id if self.initial else None
        return [
            (escape(c.to), c.id)
            for c in self.lab.arcane_connections
            if not c.fixed or c.id == mine
        ]

    def _connection_value(self, plan: SeasonPlan | None) -> object:
        ids = [value for _, value in self._connections()]
        if plan is not None and plan.connection_id in ids:
            return plan.connection_id
        return Select.NULL

    def _subjects(self) -> list[tuple[str, str]]:
        """Who a Longevity Ritual can be for: the magus first, then everyone
        else in the saga."""
        others = sorted(
            (c for c in self.saga.characters if c.id != self.magus.id),
            key=lambda c: c.name.lower(),
        )
        return [(f"{escape(self.magus.name)} (own)", self.magus.id)] + [
            (f"{escape(c.name)} ({c.type})", c.id) for c in others
        ]

    def _header(self, activity: str) -> str:
        found = season_rules.ACTIVITIES.get(activity)
        label = found.label if found is not None else "Lab work"
        return (
            f"{label} -- {escape(self.magus.name)} in "
            f"{escape(self.lab.name)}, {self.season} {self.year}"
        )

    # -- showing the results ---------------------------------------------------

    def _start_label(self) -> str:
        source = spl.find_spell(self.saga, getattr(self, "source_id", None))
        if source is None:
            return "(New spell) -- choose a spell to start from..."
        level = "Gen" if source.level is None else source.level
        return f"{source.name}  {spl.shorthand(source)}  (level {level})"

    def _level_text(self, design: SpellDesign) -> str:
        if design.base_level is None:
            if design.printed_level is not None:
                return (
                    f"Level {design.printed_level} (as printed: type a base level "
                    "to work it out from the parameters)"
                )
            return "[dim]Type a base level: the level is worked out from it.[/]"
        worked = spell_levels.spell_level(
            design.base_level,
            design.range,
            design.duration,
            design.target,
            extra_magnitudes=design.extra_magnitudes,
            ritual=design.ritual,
            custom_steps=design.custom_steps,
        )
        if worked is None:
            return (
                "[$text-warning]An Other parameter needs its magnitudes typed "
                "(+n) to work out the level.[/]"
            )
        notes = "".join(f"  [$text-warning]{escape(n)}[/]" for n in worked.notes)
        return (
            f"[b]Level {worked.level}[/]  {escape(worked.design_line(design.base_level))}"
            + notes
        )

    def _refresh(self) -> None:
        if not self._ready:
            return
        plan = self.current_plan()
        inventing = plan.activity == lab_seasons.INVENT
        chosen = bool(plan.activity)
        self.query_one("#inv-header", Static).update(self._header(plan.activity))
        self.query_one("#inv-common").display = chosen
        self.query_one("#inv-design").display = inventing
        self.query_one("#inv-labtext").display = plan.activity == lab_seasons.LAB_TEXT
        self.query_one("#inv-work").display = chosen and (
            plan.activity not in lab_seasons.SPELL_ACTIVITIES
        )
        self.query_one("#inv-connection-row").display = (
            plan.activity == lab_seasons.FIX_AC
        )
        self.query_one("#inv-subject-row").display = (
            plan.activity == lab_seasons.LONGEVITY
        )
        self.query_one("#inv-vis-from-label", Label).update(
            "Vis goes to" if plan.activity == lab_seasons.EXTRACT else "Vis from"
        )
        self.query_one("#inv-similar").disabled = not inventing
        self.query_one("#inv-other-row").display = inventing and any(
            self._select(f"#inv-{kind}") == OTHER for kind in _KINDS
        )
        if plan.design is not None:
            self.query_one("#inv-level", Static).update(self._level_text(plan.design))
        if not chosen:
            self.query_one("#inv-error", Static).update("")
            return
        problems = season_rules.problems(self.magus, plan, self.saga)
        _, work = lab_seasons.work(self.saga, self.magus, plan)
        total, when = (
            self.query_one("#inv-total", Static),
            self.query_one("#inv-when", Static),
        )
        if work is None:
            total.update("[b]Lab Total[/]\n[dim]--[/]")
            when.update("")
        elif plan.activity == lab_seasons.FIX_AC:
            total.update("[b]Lab Total[/]\n[dim]None needed[/]")
            when.update(self._when_text(plan, work))
        else:
            lines = ["[b]Lab Total[/]"]
            for line in work.lab_total.lines:
                if line.amount is not None:
                    lines.append(f"{escape(line.label)[:30]:<30} {line.amount:+g}")
                elif line.multiplier is not None:
                    lines.append(f"{escape(line.label)[:30]:<30} x{line.multiplier:g}")
            lines.append(f"[b]{'Lab Total':<30} {int(work.lab_total.total)}[/]")
            total.update("\n".join(lines))
            when.update(self._when_text(plan, work))
        self.query_one("#inv-error", Static).update(
            escape(problems[0]) if problems else ""
        )

    def _when_text(self, plan: SeasonPlan, work: lab_seasons.LabWork) -> str:
        lab_total = int(work.lab_total.total)
        exposure = ["", "Every lab season also gives 2 xp", "Exposure in Magic Theory."]
        if plan.activity == lab_seasons.EXTRACT:
            return "\n".join(
                [
                    "[b]When[/]",
                    f"Lab Total {lab_total}: {work.vis_gained} pawn(s) of Vim vis "
                    f"this season, {self.season} {self.year}.",
                    *exposure,
                ]
            )
        if plan.activity == lab_seasons.FIX_AC:
            return "\n".join(
                [
                    "[b]When[/]",
                    f"Fixed this season, {self.season} {self.year}, for 1 pawn "
                    "of Vim vis.",
                    *exposure,
                ]
            )
        if plan.activity == lab_seasons.LONGEVITY:
            name = work.subject.name if work.subject is not None else "?"
            paid = ", ".join(f"{n} pawn(s) of {a}" for a, n in work.vis_cost.items())
            return "\n".join(
                [
                    "[b]When[/]",
                    f"This season, {self.season} {self.year}: aging rolls "
                    f"-{work.longevity} for {escape(name)}.",
                    f"Vis: {paid}.",
                    *exposure,
                ]
            )
        if plan.activity == lab_seasons.LAB_TEXT:
            return (
                f"[b]When[/]\nLevel {work.level}, Lab Total {lab_total}: learned "
                f"this season, {self.season} {self.year}."
            )
        season, year = self.season, self.year
        for _ in range(lab_seasons.seasons_left(work)):
            season, year = next_season(season, year)
        seasons_needed = lab_seasons.seasons_left(work) + 1
        return "\n".join(
            [
                "[b]When[/]",
                f"Level {work.level}, Lab Total {lab_total}: "
                f"{work.points_gained} points a season",
                f"{work.points_before} of {work.level} points so far",
                f"Invented {season} {year} (projected: {seasons_needed} "
                f"season{'s' if seasons_needed != 1 else ''})",
                "",
                "Every lab season also gives 2 xp",
                "Exposure in Magic Theory.",
            ]
        )

    # -- events ------------------------------------------------------------------

    def on_input_changed(self, _event: Input.Changed) -> None:
        self._refresh()

    def on_select_changed(self, _event: Select.Changed) -> None:
        self._refresh()

    def on_checkbox_changed(self, _event: Checkbox.Changed) -> None:
        self._refresh()

    def on_text_area_changed(self, _event: TextArea.Changed) -> None:
        self._refresh()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        button = event.button.id
        if button == "btn-cancel":
            self.dismiss(None)
        elif button == "btn-reset":
            self._fill(self._initial_design(), self.initial)
            self._reset_work(self.initial)
        elif button == "inv-new":
            self.key = uuid.uuid4().hex[:12]
            self._fill(None, None)
        elif button == "inv-start":
            self.app.push_screen(
                SpellChooserScreen(
                    self.saga,
                    exclude={k.spell_id for k in self.magus.spells_known},
                    title=f"Start {escape(self.magus.name)}'s spell from...",
                ),
                self._start_from,
            )
        elif button == "btn-save":
            plan = self.current_plan()
            if not plan.activity:
                self.query_one("#inv-error", Static).update("Choose the lab work.")
                return
            problems = season_rules.problems(self.magus, plan, self.saga)
            if problems:
                self.query_one("#inv-error", Static).update(escape(problems[0]))
                return
            self.dismiss(plan)

    def _start_from(self, spell_id: str | None) -> None:
        spell = spl.find_spell(self.saga, spell_id)
        if spell is not None:
            self._fill(self._design_from(spell), None, keep_lab_options=True)

    def _initial_design(self) -> SpellDesign | None:
        return self._design

    @staticmethod
    def _design_from(spell: Spell) -> SpellDesign:
        """A design filled in from `spell`: its level is worked out from its
        base level where it has one (the rest of its level becomes extra
        magnitudes), otherwise kept as printed."""
        extra = 0
        if spell.base_level is not None and spell.level is not None:
            found = spell_levels.extra_magnitudes(
                spell.base_level, spell.range, spell.duration, spell.target, spell.level
            )
            extra = found or 0
        return SpellDesign(
            key=uuid.uuid4().hex[:12],
            name=spell.name,
            technique=spell.technique,
            form=spell.form,
            requisites=list(spell.requisites),
            base_level=spell.base_level,
            range=spell.range or "Personal",
            duration=spell.duration or "Momentary",
            target=spell.target or "Individual",
            extra_magnitudes=extra,
            ritual=spell.ritual,
            description=spell.description,
            source_spell_id=spell.id,
            printed_level=spell.level if spell.base_level is None else None,
        )

    def _fill(
        self,
        design: SpellDesign | None,
        plan: SeasonPlan | None,
        *,
        keep_lab_options: bool = False,
    ) -> None:
        """Put `design` (None: a blank one) and, unless kept, `plan`'s lab
        options into the form."""
        self._ready = False
        self.source_id = design.source_spell_id if design else None
        self.printed_level = design.printed_level if design else None
        if design is not None and design.key:
            self.key = design.key
        self.query_one("#inv-start", Button).label = self._start_label()
        self.query_one("#inv-name", Input).value = design.name if design else ""
        self.query_one("#inv-description", TextArea).text = (
            design.description if design else ""
        )
        for selector, value in (
            ("#inv-technique", design.technique if design else ""),
            ("#inv-form", design.form if design else ""),
        ):
            self.query_one(selector, Select).value = value or Select.NULL
        self.query_one("#inv-requisites", Input).value = (
            ", ".join(design.requisites) if design else ""
        )
        self.query_one("#inv-base", Input).value = (
            "" if not design or design.base_level is None else str(design.base_level)
        )
        self.query_one("#inv-ritual", Checkbox).value = bool(design and design.ritual)
        for kind in _KINDS:
            current = getattr(design, kind) if design else _STANDARD_FIRST[kind]
            values = [v for _, v in self.parameter_options[kind]]
            self.query_one(f"#inv-{kind}", Select).value = (
                current if current in values else OTHER
            )
            self.query_one(f"#inv-{kind}-name", Input).value = (
                current if current not in values else ""
            )
            steps = design.custom_steps.get(kind) if design else None
            self.query_one(f"#inv-{kind}-steps", Input).value = (
                "" if steps is None else str(steps)
            )
        self.query_one("#inv-extra", Input).value = (
            str(design.extra_magnitudes) if design else "0"
        )
        self.query_one("#inv-base-effect", Input).value = (
            design.base_effect if design else ""
        )
        if not keep_lab_options:
            self.query_one("#inv-days", Input).value = (
                str(plan.days_away) if plan else "0"
            )
            self.query_one("#inv-other", Input).value = (
                str(plan.other_modifier) if plan else "0"
            )
            self.query_one("#inv-notes", Input).value = plan.details if plan else ""
            self.query_one("#inv-similar", Select).value = (
                plan.similar_spell_id if plan and plan.similar_spell_id else Select.NULL
            )
        self._ready = True
        self.call_after_refresh(self._refresh)

    def _reset_work(self, plan: SeasonPlan | None) -> None:
        """Put `plan`'s activity and its non-spell fields back."""
        self._ready = False
        self.query_one("#inv-activity", Select).value = (
            self.initial_activity or Select.NULL
        )
        self.query_one("#inv-connection", Select).value = self._connection_value(plan)
        self.query_one("#inv-subject", Select).value = (
            plan.subject_id if plan and plan.subject_id else self.magus.id
        )
        self.query_one("#inv-vis-art", Select).value = (
            plan.vis_art
            if plan and plan.vis_art in lab_seasons.LONGEVITY_VIS_ARTS
            else "Creo"
        )
        self.query_one("#inv-extra-vis", Input).value = (
            str(plan.extra_vis) if plan else "0"
        )
        self.query_one("#inv-vis-from", Select).value = (
            plan.vis_from if plan and plan.vis_from else "laboratory"
        )
        self._ready = True
        self.call_after_refresh(self._refresh)


_STANDARD_FIRST: dict[str, str] = {
    "range": "Personal",
    "duration": "Momentary",
    "target": "Individual",
}
