"""The Invent Spell screen: a
season of lab work planned on the laboratory's Planning tab. Start from a
spell (or a blank design), change anything -- name, effect, Arts,
requisites, base level, Range, Duration, Target -- and see the level, the
Lab Total and when the spell will be invented, all worked out as you type.

The other lab work of a season is planned here too:
extracting vis, fixing an Arcane Connection and Longevity Rituals, each
with its own few fields in place of the spell design.

It is the core's lab work form (lab_plan_forms.LabPlanForm) drawn on a
full screen rather than a FieldsDialog, since it has too many fields for
one field per row at 120 x 45: its choices, the plan its values describe,
what refuses it and the level and When text are the core's; this screen
lays the fields out several to a row and reads them back as the form's
values."""

from __future__ import annotations

import uuid
from collections.abc import Callable, Sequence
from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Checkbox, Input, Label, Select, Static, TextArea

from ... import catalog, form_spec
from ... import lab_texts as lt
from ... import spells as spl
from ...arts import FORMS, TECHNIQUES
from ...commands import Picked
from ...form_spec import DialogField
from ...forms import activity as activity_forms
from ...forms import lab_plan as lpf
from ...forms import spell_guideline as guideline_forms
from ...forms.lab_plan import (
    KINDS,
    OTHER,
    LabPlanForm,
    choose_template,
    design_from,
    level_text,
)
from ...markup import escape
from ...models import (
    Character,
    Laboratory,
    Saga,
    SeasonPlan,
    SpellDesign,
)
from ...rules import activities as season_rules
from ...rules import book_seasons as bs
from ...rules import enchant_seasons as es
from ...rules import enchantment, lab_seasons
from ...rules import experiment as ex
from ...rules import familiar_seasons as fs
from ...rules import laboratory_seasons as ls
from .fields import ModalDialog
from .prompts import terminal_fields
from .steps import run_steps

#: The Exposure line, as the When column wraps it.
_EXPOSURE_LINES = ("Every lab season also gives 2 xp", "Exposure in Magic Theory.")

#: The widget drawing each field of the core's form (LabPlanForm.fields),
#: by its key.
#: The rows the lab Virtue options are drawn in, by their fields' keys.
VIRTUE_ROWS = (
    ("potent", "cycle_bonus", "cycle_penalty", "condition"),
    ("horoscope", "horoscope_die"),
    ("extract_form", "extract_shape"),
)

_WIDGET_OF: dict[str, str] = {
    "activity": "inv-activity",
    "name": "inv-name",
    "description": "inv-description",
    "technique": "inv-technique",
    "form": "inv-form",
    "requisites": "inv-requisites",
    "base_level": "inv-base",
    "ritual": "inv-ritual",
    "lasting": "inv-lasting",
    "attunement": "inv-attunement",
    "recreating_theory": "inv-recreating",
    "project_stage": "inv-stage",
    **{kind: f"inv-{kind}" for kind in KINDS},
    **{f"{kind}_name": f"inv-{kind}-name" for kind in KINDS},
    **{f"{kind}_steps": f"inv-{kind}-steps" for kind in KINDS},
    "extra_magnitudes": "inv-extra",
    "recurring": "inv-recurring",
    "base_effect": "inv-base-effect",
    "guideline": "inv-guideline",
    "lab_text": "inv-lab-text",
    "more_texts": "inv-more-texts",
    "teacher": "inv-teacher",
    "taught_spells": "inv-taught",
    "decode": "inv-decode",
    "connection": "inv-connection",
    "subject": "inv-subject",
    "longevity_vis": "inv-vis-art",
    "extra_vis": "inv-extra-vis",
    "fertile_text": "inv-fertile",
    "device": "inv-device",
    "shape": "inv-shape",
    "effect": "inv-effect",
    "effect_text": "inv-effect-text",
    "bind_technique": "inv-bind-t",
    "bind_form": "inv-bind-f",
    "golden_cord": "inv-golden",
    "silver_cord": "inv-silver",
    "bronze_cord": "inv-bronze",
    "power": "inv-power",
    "effect_vis": "inv-effect-vis",
    "other_vis": "inv-other-vis",
    "creature": "inv-creature",
    "creature_form": "inv-creature-form",
    "might": "inv-creature-might",
    "move_to": "inv-move-to",
    "by_spell": "inv-by-spell",
    "die": "inv-die",
    # One drop-down says where vis comes from, or goes to when extracting.
    "vis_to": "inv-vis-from",
    "vis_from": "inv-vis-from",
    "experimenting": "inv-experimenting",
    "risk": "inv-risk",
    "research": "inv-research",
    "research_kind": "inv-research-kind",
    "similar": "inv-similar",
    "focus": "inv-focus",
    "specialty": "inv-specialty",
    "days_away": "inv-days",
    "other_modifier": "inv-other",
    "details": "inv-notes",
    "assistant": "inv-assistant",
    # The magus's own lab Virtues and Flaws (LabPlanForm.virtue_fields).
    **{key: f"inv-v-{key}" for keys in VIRTUE_ROWS for key in keys},
}


def _number(value: str, widget_id: str, *, placeholder: str = "") -> Input:
    """A short box for a number."""
    return Input(
        value, placeholder=placeholder, id=widget_id, classes="inv-num", compact=True
    )


def _art_select(arts: Sequence[str], value: str | None, widget_id: str) -> Select[str]:
    """A Technique or Form choice, with nothing chosen while `value` is empty."""
    return Select(
        [(art, art) for art in arts],
        value=value or Select.NULL,
        prompt="(choose)",
        id=widget_id,
        classes="inv-art",
        compact=True,
    )


#: Lab work a similar spell helps (DE pp. 251, 258, 267).
_SIMILAR = (
    lab_seasons.INVENT,
    lab_seasons.LAB_TEXT,
    es.INSTIL,
    es.LESSER_WORK,
    es.CHARGED_WORK,
    fs.EMPOWER,
)
#: The fields holding a list, edited on a list screen of their own.
_LISTS = ("more_texts", "taught_spells")

#: Lab work whose vis is of the work's Technique or Form, as chosen.
_BY_ART = (es.INSTIL, es.LESSER_WORK, fs.BIND, fs.EMPOWER)

#: Which rows of the form show for the chosen activity ("" when none is
#: chosen yet), one rule per row (Strategy, as a table).
_ROWS_SHOWN: dict[str, Callable[[str], bool]] = {
    "inv-common": bool,
    "inv-design": lambda a: a == lab_seasons.INVENT,
    "inv-labtext": lambda a: a == lab_seasons.LAB_TEXT,
    "inv-more-texts-row": lambda a: a == lab_seasons.LAB_TEXT,
    "inv-taught-row": lambda a: a == lab_seasons.TAUGHT_SPELLS,
    "inv-decode-row": lambda a: a == bs.DECODE_TEXT,
    "inv-work": lambda a: (
        bool(a) and a not in (*lab_seasons.SPELL_ACTIVITIES, bs.DECODE_TEXT)
    ),
    "inv-connection-row": lambda a: a == lab_seasons.FIX_AC,
    "inv-subject-row": lambda a: a == lab_seasons.LONGEVITY,
    "inv-device-row": lambda a: a in es.ACTIVITIES,
    "inv-effect-row": lambda a: a in es.EFFECT_ACTIVITIES,
    "inv-effect-text-row": lambda a: a in es.EFFECT_ACTIVITIES,
    "inv-effect-vis": lambda a: a in _BY_ART,
    "inv-effect-vis-label": lambda a: a in _BY_ART,
    "inv-other-vis": lambda a: a in _BY_ART,
    "inv-other-vis-label": lambda a: a in _BY_ART,
    "inv-bind-row": lambda a: a == fs.BIND,
    "inv-move-row": lambda a: a == ls.MOVE,
    "inv-taming-row": lambda a: a == lab_seasons.TAMING,
    "inv-experiment-row": lambda a: a in lab_seasons.EXPERIMENTAL or a == ex.STABILIZE,
    "inv-experimenting": lambda a: a in lab_seasons.EXPERIMENTAL,
    "inv-experimenting-label": lambda a: a in lab_seasons.EXPERIMENTAL,
    "inv-power-row": lambda a: a == fs.EMPOWER,
    "inv-die-row": lambda a: a in (es.INVESTIGATE, *ls.ROLLED),
    "inv-vis-from-row": lambda a: (
        a
        not in (
            es.CHARGED_WORK,
            es.ATTUNE,
            es.INVESTIGATE,
            *ls.ACTIVITIES,
        )
    ),
}


class InventSpellScreen(ModalDialog[SeasonPlan | None]):
    """Plan a season of lab work: invent a spell (from a spell or a blank
    design) or invent one from a Lab Text. Dismisses with the plan, or None
    if cancelled."""

    help_id = "invent-spell"

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
        padding: 0 1;
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

    #inv-similar, #inv-lab-text, #inv-subject, #inv-decode {
        width: 50;
    }

    #inv-vis-from {
        width: 40;
    }

    #inv-creature {
        width: 24;
    }

    #inv-move-to {
        width: 40;
    }

    #inv-research {
        width: 30;
    }

    #inv-research-kind {
        width: 14;
    }

    #inv-vis-art, #inv-effect-vis {
        width: 14;
    }

    #inv-device, #inv-effect, #inv-power, #inv-effect-text {
        width: 50;
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
        self.form = LabPlanForm(
            saga, magus, lab, season, year, existing, activity=activity
        )
        self.initial = self.form.existing
        self.initial_activity = self.form.activity
        #: The lab work chosen (the Lab work button's value).
        self.activity = self.initial_activity
        self._design = self.form.design
        #: The catalog guideline the design is based on (the Guideline
        #: button's value).
        self._guideline = guideline_forms.design_guideline(self._design)
        self.parameter_options = self.form.parameter_options
        #: The core form's fields, each drawn by its widget (_WIDGET_OF).
        self._fields = self.form.fields()
        #: The list fields' entries as they stand.
        self._lists: dict[str, list[str]] = {
            spec.key: list(spec.value) if isinstance(spec.value, list) else []
            for spec in self._fields
            if spec.key in _LISTS
        }
        self._ready = False

    # -- layout --------------------------------------------------------------

    def compose(self) -> ComposeResult:
        plan = self.initial
        with Vertical(id="inv-dialog", classes="dialog-box"):
            yield Static(self._header(self.initial_activity or ""), id="inv-header")
            with VerticalScroll(id="inv-scroll"):
                with Horizontal(classes="inv-row"):
                    yield Label("Lab work")
                    yield Button(
                        self._activity_label(self.initial_activity),
                        id="inv-activity",
                        compact=True,
                    )
                with Vertical(id="inv-design"):
                    yield from self._compose_design(self._design)
                yield from self._compose_lab_texts(plan)
                with Vertical(id="inv-work"):
                    yield from self._compose_targets(plan)
                    yield from self._compose_other_work(plan)
                with Vertical(id="inv-common"):
                    yield from self._compose_common(plan)
            yield Static("", id="inv-error")
            with Horizontal(id="inv-buttons"):
                yield Button("Schedule", id="btn-save", variant="primary", compact=True)
                yield Button("Cancel", id="btn-cancel", compact=True)
                yield Button("Reset", id="btn-reset", compact=True)

    def _compose_design(self, design: SpellDesign | None) -> ComposeResult:
        """The spell's design: where it starts from, its name and effect, its
        Arts, Range / Duration / Target, and its level."""
        with Horizontal(classes="inv-row"):
            yield Label("Start from")
            yield Button(self._start_label(), id="inv-start", compact=True)
            yield Button("New spell", id="inv-new", compact=True)
        with Horizontal(classes="inv-row"):
            yield Label("Name      ")
            yield Input(design.name if design else "", id="inv-name", compact=True)
        yield Label("Effect")
        yield TextArea(design.description if design else "", id="inv-description")
        yield Static("── Effect ─────────", classes="inv-title")
        with Horizontal(classes="inv-row"):
            yield Label("Guideline")
            yield Button(self._guideline_label(), id="inv-guideline", compact=True)
        with Horizontal(classes="inv-row"):
            yield Label("Technique")
            yield _art_select(
                TECHNIQUES, design.technique if design else None, "inv-technique"
            )
            yield Label(" Form")
            yield _art_select(FORMS, design.form if design else None, "inv-form")
            yield Label(" Requisites")
            yield Input(
                ", ".join(design.requisites) if design else "",
                placeholder="e.g. Rego",
                id="inv-requisites",
                compact=True,
            )
            yield Label(" Base level")
            yield _number(
                ""
                if not design or design.base_level is None
                else str(design.base_level),
                "inv-base",
            )
            yield Label(" Ritual")
            yield Checkbox(
                "",
                value=bool(design and design.ritual),
                id="inv-ritual",
                compact=True,
            )
            yield Label(" Lasting")
            yield Checkbox(
                "",
                value=bool(design and design.lasting),
                id="inv-lasting",
                compact=True,
            )
        with Horizontal(classes="inv-row"):
            for kind in KINDS:
                yield Label(("" if kind == "range" else " ") + kind.title())
                current = getattr(design, kind) if design else ""
                values = [v for _, v in self.parameter_options[kind]]
                choice = (
                    self.form.parameter_choice(kind, current)[0]
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
            for kind in KINDS:
                current = getattr(design, kind) if design else ""
                steps = design.custom_steps.get(kind) if design else None
                yield Label(("" if kind == "range" else " ") + f"Other {kind}")
                yield Input(
                    self.form.parameter_choice(kind, current)[1] if current else "",
                    placeholder="name",
                    id=f"inv-{kind}-name",
                    classes="inv-other",
                    compact=True,
                )
                yield _number(
                    "" if steps is None else str(steps),
                    f"inv-{kind}-steps",
                    placeholder="+n",
                )
        with Horizontal(classes="inv-row"):
            yield Label("Size / extra magnitudes")
            yield _number(str(design.extra_magnitudes) if design else "0", "inv-extra")
            yield Label(" Base effect")
            yield Input(
                design.base_effect if design else "",
                placeholder="the guideline used",
                id="inv-base-effect",
                compact=True,
            )
            recurring = next((f for f in self._fields if f.key == "recurring"), None)
            if recurring is not None:
                yield Label(" Recurs each")
                yield Select(
                    recurring.options,
                    value=recurring.value or Select.NULL,
                    prompt=recurring.placeholder,
                    id="inv-recurring",
                    compact=True,
                    tooltip=recurring.hint or None,
                )
        yield Static("", id="inv-level")

    def _compose_lab_texts(self, plan: SeasonPlan | None) -> ComposeResult:
        """The Lab Text to invent from, and the raw text to decode."""
        with Horizontal(classes="inv-row", id="inv-labtext"):
            yield Label("Lab Text")
            yield Select(
                [
                    (escape(b.name + lt.cant_read_tag(self.saga, self.magus, b)), b.id)
                    for b in lab_seasons.lab_texts_at_hand(self.saga, self.magus)
                ],
                value=(plan.book_id if plan and plan.book_id else Select.NULL),
                prompt="(choose the Lab Text)",
                id="inv-lab-text",
                compact=True,
            )
        with Horizontal(classes="inv-row", id="inv-more-texts-row"):
            yield Label("More Lab Texts")
            yield Button(
                self._list_label("more_texts"), id="inv-more-texts", compact=True
            )
        with Horizontal(classes="inv-row", id="inv-taught-row"):
            yield Label("Teacher")
            teachers = self.form.teachers()
            yield Select(
                teachers,
                value=(
                    plan.teacher_id
                    if plan
                    and plan.activity == lab_seasons.TAUGHT_SPELLS
                    and plan.teacher_id in [v for _, v in teachers]
                    else Select.NULL
                ),
                prompt="(choose the magus who teaches)",
                id="inv-teacher",
                compact=True,
            )
            yield Label(" Spells taught")
            yield Button(
                self._list_label("taught_spells"), id="inv-taught", compact=True
            )
        with Horizontal(classes="inv-row", id="inv-decode-row"):
            yield Label("Lab Text")
            yield Select(
                [
                    (f"{escape(b.name)} ({escape(bs.author_name(self.saga, b))})", b.id)
                    for b in self.form.undecoded()
                ],
                value=(
                    plan.book_id
                    if plan
                    and plan.activity == bs.DECODE_TEXT
                    and plan.book_id in [b.id for b in self.form.undecoded()]
                    else Select.NULL
                ),
                prompt="(a raw text by another magus)",
                id="inv-decode",
                compact=True,
            )

    def _compose_targets(self, plan: SeasonPlan | None) -> ComposeResult:
        """What lab work other than inventing acts on: an Arcane Connection,
        the person a Longevity Ritual is for, a device and its effects."""
        with Horizontal(classes="inv-row", id="inv-connection-row"):
            yield Label("Connection to")
            yield Select(
                self.form.connections(),
                value=self._connection_value(plan),
                prompt="(choose; add them on the Inventory tab)",
                id="inv-connection",
                compact=True,
            )
        with Horizontal(classes="inv-row", id="inv-subject-row"):
            yield Label("For")
            yield Select(
                self.form.subjects(),
                value=(plan.subject_id if plan and plan.subject_id else self.magus.id),
                allow_blank=False,
                id="inv-subject",
                compact=True,
            )
            yield Label(" Vis")
            yield Select(
                [(art, art) for art in lab_seasons.LONGEVITY_VIS_ARTS],
                value=(
                    plan.vis_art
                    if plan and plan.vis_art in lab_seasons.LONGEVITY_VIS_ARTS
                    else "Creo"
                ),
                allow_blank=False,
                id="inv-vis-art",
                compact=True,
            )
            yield Label(" Extra pawns")
            yield _number(str(plan.extra_vis) if plan else "0", "inv-extra-vis")
            # From a Lab Text using the Fertile Longevity Ritual breakthrough,
            # offered only to a magus who hasn't reached it himself.
            fertile = next(
                (f for f in self.form.fields() if f.key == "fertile_text"), None
            )
            if fertile is not None:
                yield Label(" Fertile")
                yield Checkbox(
                    "",
                    value=bool(fertile.value),
                    id="inv-fertile",
                    compact=True,
                    tooltip=fertile.hint or None,
                )
        with Horizontal(classes="inv-row", id="inv-device-row"):
            yield Label("Device")
            yield Select(
                self.form.devices(),
                value=self._device_value(plan),
                prompt="(choose; they're kept on the Inventory tabs)",
                id="inv-device",
                compact=True,
            )
            yield Label(" Shape & material")
            yield _number(str(plan.shape_bonus) if plan else "0", "inv-shape")
            attunements = self._spec_options("attunement")
            if attunements:
                yield Label(" Attune to")
                yield Select(
                    attunements,
                    value=self._spec_value("attunement"),
                    prompt="(none this season)",
                    id="inv-attunement",
                    compact=True,
                )
        with Horizontal(classes="inv-row", id="inv-effect-row"):
            yield Label("Effect")
            yield Select(
                self._effects(plan.device_id if plan else None),
                value=self._effect_value(plan),
                prompt="(choose)",
                id="inv-effect",
                compact=True,
            )
        with Horizontal(classes="inv-row", id="inv-effect-text-row"):
            yield Label("From Lab Text")
            yield Select(
                self._effect_texts(plan),
                value=self._effect_text_value(plan),
                prompt="(none: instil it the long way)",
                id="inv-effect-text",
                compact=True,
            )

    def _compose_other_work(self, plan: SeasonPlan | None) -> ComposeResult:
        """The rest of the lab work: binding a familiar and its powers, taming
        a creature, moving the lab, a die, and where vis comes from."""
        with Horizontal(classes="inv-row", id="inv-bind-row"):
            yield Label("Technique")
            yield _art_select(
                TECHNIQUES, plan.technique if plan else None, "inv-bind-t"
            )
            yield Label(" Form")
            yield _art_select(FORMS, plan.form if plan else None, "inv-bind-f")
            for cord in ("golden", "silver", "bronze"):
                yield Label(f" {cord.title()} cord")
                yield _number(
                    str(getattr(plan, f"{cord}_cord")) if plan else "0", f"inv-{cord}"
                )
        with Horizontal(classes="inv-row", id="inv-power-row"):
            yield Label("Bond power")
            yield Select(
                self.form.powers(),
                value=self._power_value(plan),
                prompt="(choose; add it on the familiar's sheet)",
                id="inv-power",
                compact=True,
            )
        with Horizontal(classes="inv-row", id="inv-taming-row"):
            yield Label("Creature")
            yield Input(
                plan.title if plan else "",
                placeholder="its name",
                id="inv-creature",
                compact=True,
            )
            yield Label(" Form")
            yield _art_select(FORMS, plan.form if plan else None, "inv-creature-form")
            yield Label(" Might")
            yield _number(
                "" if plan is None or plan.book_level is None else str(plan.book_level),
                "inv-creature-might",
            )
        with Horizontal(classes="inv-row", id="inv-move-row"):
            yield Label("Moving to")
            yield Input(
                plan.title if plan else "",
                placeholder="the new location",
                id="inv-move-to",
                compact=True,
            )
            yield Label(" By spell")
            yield Checkbox(
                "",
                value=bool(plan and plan.by_spell),
                id="inv-by-spell",
                compact=True,
            )
        with Horizontal(classes="inv-row", id="inv-die-row"):
            yield Label("Die")
            yield _number(
                "" if plan is None or plan.die is None else str(plan.die),
                "inv-die",
                placeholder="rolled",
            )
            yield Label(
                " (blank: rolled when the season is played; a typed die "
                "is used for one roll)"
            )
        with Horizontal(classes="inv-row", id="inv-vis-from-row"):
            yield Label("Vis", id="inv-vis-from-label")
            yield Select(
                self.form.vis_places(),
                value=(plan.vis_from if plan and plan.vis_from else "laboratory"),
                allow_blank=False,
                id="inv-vis-from",
                compact=True,
            )
            yield Label(" Art", id="inv-effect-vis-label")
            yield Select(
                self._effect_arts(plan),
                value=self._effect_art_value(plan),
                prompt="(Art)",
                id="inv-effect-vis",
                compact=True,
            )
            yield Label(" Of the other Art", id="inv-other-vis-label")
            yield _number(str(plan.other_vis) if plan else "0", "inv-other-vis")

    def _compose_common(self, plan: SeasonPlan | None) -> ComposeResult:
        """What every kind of lab work shares: experimenting, a similar spell,
        Focus and specialty, days away, other modifiers, notes, an assistant and the
        results."""
        known = [
            (escape(spell.name), spell.id)
            for k in self.magus.spells_known
            if (spell := catalog.find_spell(self.saga, k.spell_id)) is not None
        ]
        yield Static("── Lab work ────────", classes="inv-title")
        with Horizontal(classes="inv-row", id="inv-experiment-row"):
            yield Label("Experiment", id="inv-experimenting-label")
            yield Checkbox(
                "",
                value=bool(plan and plan.experimenting),
                id="inv-experimenting",
                compact=True,
            )
            yield Label(" Risk +")
            yield _number(str(plan.risk) if plan else "0", "inv-risk")
            yield Label(" Research goal")
            yield Input(
                plan.research if plan else "",
                placeholder="(optional)",
                id="inv-research",
                compact=True,
            )
            yield Label(" ")
            yield Select(
                [(k, k) for k in ex.KINDS],
                value=(plan.research_kind if plan else "Minor") or "Minor",
                allow_blank=False,
                id="inv-research-kind",
                compact=True,
            )
        with Horizontal(classes="inv-row"):
            yield Label("Similar spell known")
            yield Select(
                known,
                value=(
                    plan.similar_spell_id
                    if plan and plan.similar_spell_id in [v for _, v in known]
                    else Select.NULL
                ),
                prompt="(none)",
                id="inv-similar",
                compact=True,
            )
            if lab_seasons.has_focus(self.magus):
                yield Label(" Magical Focus")
                focus = self._spec_options("focus")
                if focus:
                    yield Select(
                        focus,
                        value=self._spec_value("focus"),
                        allow_blank=False,
                        id="inv-focus",
                        compact=True,
                    )
                else:
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
        yield from self._compose_virtues(plan)
        with Horizontal(classes="inv-row"):
            yield Label("Days away")
            yield _number(str(plan.days_away) if plan else "0", "inv-days")
            yield Label(
                " (10 cost nothing, 11-20 lower the Lab Total, more rule it out)   Other"
            )
            yield _number(str(plan.other_modifier) if plan else "0", "inv-other")
            yield Label(" Recreating (Magic Theory then)")
            yield _number(
                str(plan.recreating_theory) if plan else "0", "inv-recreating"
            )
        stages = self._spec_options("project_stage")
        if stages:
            with Horizontal(classes="inv-row"):
                yield Label("Spent on a project's stage")
                yield Select(
                    stages,
                    value=self._spec_value("project_stage"),
                    prompt="(none)",
                    id="inv-stage",
                    compact=True,
                )
        with Horizontal(classes="inv-row"):
            yield Label("Notes")
            yield Input(plan.details if plan else "", id="inv-notes", compact=True)
            helpers = self.form.helpers()
            if helpers:
                chosen = self.form.assistant_of(plan)
                yield Label(" Assistant")
                yield Select(
                    helpers,
                    value=chosen if chosen in [v for _, v in helpers] else Select.NULL,
                    prompt="(none)",
                    id="inv-assistant",
                    compact=True,
                )
        with Horizontal(id="inv-results"):
            yield Static("", id="inv-total")
            yield Static("", id="inv-when")

    def _compose_virtues(self, plan: SeasonPlan | None) -> ComposeResult:
        """The options the magus's lab Virtues and Flaws give, a row of
        each kind (only the magus's own)."""
        specs = {spec.key: spec for spec in self.form.virtue_fields(plan)}
        for keys in VIRTUE_ROWS:
            shown = [specs[key] for key in keys if key in specs]
            if not shown:
                continue
            with Horizontal(classes="inv-row"):
                for position, spec in enumerate(shown):
                    widget_id = _WIDGET_OF[spec.key]
                    yield Label(
                        (" " if position else "") + spec.label,
                        id=f"{widget_id}-label",
                    )
                    if spec.kind == "check":
                        yield Checkbox(
                            "",
                            value=bool(spec.value),
                            id=widget_id,
                            compact=True,
                            tooltip=spec.hint or None,
                        )
                    elif spec.kind == "select":
                        yield Select(
                            spec.options,
                            value=spec.value if spec.value else Select.NULL,
                            prompt=spec.placeholder or "(none)",
                            id=widget_id,
                            compact=True,
                            tooltip=spec.hint or None,
                        )
                    else:
                        value = "" if spec.value is None else str(spec.value)
                        number = _number(value, widget_id)
                        number.tooltip = spec.hint or None
                        yield number

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

    def _spec(self, key: str) -> DialogField | None:
        return next((f for f in self._fields if f.key == key), None)

    def _spec_options(self, key: str) -> list[tuple[str, str]]:
        """A core field's choices, when the core form offers it as one."""
        spec = self._spec(key)
        return list(spec.options) if spec is not None and spec.kind == "select" else []

    def _spec_value(self, key: str) -> object:
        spec = self._spec(key)
        value = spec.value if spec is not None else None
        return value if isinstance(value, str) and value else Select.NULL

    def _select(self, selector: str) -> str | None:
        value = self.query_one(selector, Select).value
        return value if isinstance(value, str) else None

    def _read(self, spec: DialogField) -> Any:
        """What the widget for one of the core form's fields holds."""
        if spec.key == "activity":
            return self.activity
        if spec.key in self._lists:
            return list(self._lists[spec.key])
        if spec.key == "start_from":
            design = self.form.design
            return design.source_spell_id if design else None
        if spec.key == "guideline":
            return self._guideline
        found = self.query(f"#{_WIDGET_OF[spec.key]}")
        if not found:
            return None
        widget = found.first()
        if isinstance(widget, Select):
            return widget.value if isinstance(widget.value, str) else None
        if isinstance(widget, Checkbox):
            return bool(widget.value)
        if isinstance(widget, TextArea):
            return widget.text.rstrip()
        return widget.value.strip() if isinstance(widget, Input) else None

    def values(self) -> dict[str, Any]:
        """The form's values as they stand, as the core's form holds them
        (a number not typed yet is None; hidden fields are left out)."""
        current = form_spec.current_values(self._fields, self._read)
        return {
            spec.key: current[spec.key]
            for spec in self._fields
            if spec.key in current and form_spec.shown(spec, current)
        }

    def current_plan(self) -> SeasonPlan:
        return self.form.plan_of(self.values())

    def _connection_value(self, plan: SeasonPlan | None) -> object:
        ids = [value for _, value in self.form.connections()]
        if plan is not None and plan.connection_id in ids:
            return plan.connection_id
        return Select.NULL

    def _device_value(self, plan: SeasonPlan | None) -> object:
        ids = [value for _, value in self.form.devices()]
        if plan is not None and plan.device_id in ids:
            return plan.device_id
        return Select.NULL

    def _effects(self, device_id: str | None) -> list[tuple[str, str]]:
        """The chosen device's effects (the core's form lists every
        device's; here the device is chosen first)."""
        device = next(
            (d for d in self.saga.enchanted_devices if d.id == device_id), None
        )
        if device is None:
            return []
        return [
            (
                f"{escape(enchantment.effect_name(e))} (level {enchantment.modified_level(device, e)})",
                e.id,
            )
            for e in device.effects
        ]

    def _effect_texts(self, plan: SeasonPlan | None) -> list[tuple[str, str]]:
        """The Lab Texts the plan's effect could be instilled from: enchantment texts of
        the same Arts, level and kind of device that the magus can read."""
        device = es.device_of(self.saga, plan) if plan is not None else None
        effect = es.effect_of(device, plan) if device and plan else None
        if device is None or effect is None:
            return []
        return [
            (
                f"{escape(b.name)} ({escape(bs.author_name(self.saga, b))})",
                b.id,
            )
            for b in es.effect_texts(self.saga, self.magus, device, effect)
        ]

    def _effect_text_value(self, plan: SeasonPlan | None) -> object:
        ids = [value for _, value in self._effect_texts(plan)]
        return plan.book_id if plan and plan.book_id in ids else Select.NULL

    def _effect_value(self, plan: SeasonPlan | None) -> object:
        if plan is None:
            return Select.NULL
        ids = [value for _, value in self._effects(plan.device_id)]
        return plan.effect_id if plan.effect_id in ids else Select.NULL

    def _power_value(self, plan: SeasonPlan | None) -> object:
        ids = [value for _, value in self.form.powers()]
        if plan is not None and plan.effect_id in ids:
            return plan.effect_id
        return Select.NULL

    def _effect_arts(self, plan: SeasonPlan | None) -> list[tuple[str, str]]:
        """The Technique and Form whose vis the work may spend."""
        if plan is None:
            return []
        return [(art, art) for art in self.form.work_arts(plan)]

    def _effect_art_value(self, plan: SeasonPlan | None) -> object:
        arts = [value for _, value in self._effect_arts(plan)]
        if plan is not None and plan.vis_art in arts:
            return plan.vis_art
        return arts[0] if arts else Select.NULL

    def _header(self, activity: str) -> str:
        found = season_rules.ACTIVITIES.get(activity)
        label = found.label if found is not None else "Lab work"
        return (
            f"{label} -- {escape(self.magus.name)} in "
            f"{escape(self.lab.name)}, {self.season} {self.year}"
        )

    # -- showing the results ---------------------------------------------------

    def _start_label(self) -> str:
        design = self.form.design
        source = catalog.find_spell(
            self.saga, design.source_spell_id if design else None
        )
        if source is None:
            return "(New spell) -- choose a spell to start from..."
        level = "Gen" if source.level is None else source.level
        return f"{source.name}  {spl.shorthand(source)}  (level {level})"

    def _refresh(self) -> None:
        if not self._ready:
            return
        values = self.values()
        plan = self.form.plan_of(values)
        inventing = plan.activity == lab_seasons.INVENT
        self.query_one("#inv-header", Static).update(self._header(plan.activity))
        for row, shown in _ROWS_SHOWN.items():
            self.query_one(f"#{row}").display = shown(plan.activity)
        for spec in self.form.virtue_fields(plan):
            visible = spec.show_if is None or bool(spec.show_if(values))
            widget_id = _WIDGET_OF[spec.key]
            for found in self.query(f"#{widget_id}, #{widget_id}-label"):
                found.display = visible
        self.query_one("#inv-vis-from-label", Label).update(
            "Vis goes to" if plan.activity == lab_seasons.EXTRACT else "Vis from"
        )
        self.query_one("#inv-similar").disabled = plan.activity not in _SIMILAR
        self.query_one("#inv-other-row").display = inventing and any(
            self._select(f"#inv-{kind}") == OTHER for kind in KINDS
        )
        if plan.design is not None:
            self.query_one("#inv-level", Static).update(level_text(plan.design))
        if not plan.activity:
            self.query_one("#inv-error", Static).update("")
            return
        problem = self.form.problem(values)
        self._show_lab_total(plan)
        self.query_one("#inv-error", Static).update(escape(problem or ""))

    def _show_lab_total(self, plan: SeasonPlan) -> None:
        """The work's Lab Total, line by line, and when it is done."""
        work = self.form.work_of(plan)
        total, when = (
            self.query_one("#inv-total", Static),
            self.query_one("#inv-when", Static),
        )
        if work is None:
            total.update("[b]Lab Total[/]\n[dim]--[/]")
            when.update("")
        elif not work.lab_total.lines:
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

    def _when_text(self, plan: SeasonPlan, work: lab_seasons.LabWork) -> str:
        """The core's When lines, one to a line, the Exposure apart."""
        lines = ["[b]When[/]"]
        for line in self.form.when_lines(plan, work):
            lines += ["", *_EXPOSURE_LINES] if line == lpf.EXPOSURE else [line]
        return "\n".join(lines)

    # -- events ------------------------------------------------------------------

    def on_input_changed(self, _event: Input.Changed) -> None:
        self._refresh()

    def on_select_changed(self, event: Select.Changed) -> None:
        if self._ready and event.select.id in (
            "inv-device",
            "inv-effect",
            "inv-power",
            "inv-bind-t",
            "inv-bind-f",
        ):
            self._work_changed(event.select.id)
        self._refresh()

    @staticmethod
    def _activity_label(activity: str | None) -> str:
        return escape(activity_forms.activity_label(activity) or "(none)")

    def set_activity(self, activity: str | None) -> None:
        """Choose the lab work, as the Lab work picker does."""
        self.activity = activity
        self.query_one("#inv-activity", Button).label = self._activity_label(activity)
        if self._ready:
            self._work_changed("inv-activity")
        self._refresh()

    def _choose_activity(self) -> None:
        def chosen(end: object) -> None:
            if isinstance(end, Picked):
                self.set_activity(end.value)

        run_steps(
            self.app,
            activity_forms.choose_activity(
                self.saga, self.magus, self.activity, lab=True
            ),
            chosen,
        )

    def _work_changed(self, widget_id: str | None) -> None:
        """A different device offers its own effects, and an effect (or
        lab work) its own Lab Texts and Technique and Form to pay vis
        with."""
        self._ready = False
        if widget_id == "inv-device":
            effects = self._effects(self._select("#inv-device"))
            self.query_one("#inv-effect", Select).set_options(effects)
        plan = self.current_plan()
        self.query_one("#inv-effect-text", Select).set_options(self._effect_texts(plan))
        arts = self._effect_arts(plan)
        vis = self.query_one("#inv-effect-vis", Select)
        vis.set_options(arts)
        if arts:
            vis.value = arts[0][1]
        self._ready = True

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
        elif button == "inv-activity":
            self._choose_activity()
        elif button == "inv-new":
            self._fill(None, None)
        elif button == "inv-start":
            self._choose_start()
        elif button == "inv-guideline":
            self._choose_guideline()
        elif button in ("inv-more-texts", "inv-taught"):
            self._edit_list(
                "more_texts" if button == "inv-more-texts" else "taught_spells"
            )
        elif button == "btn-save":
            try:
                values = form_spec.result(self._fields, self._read)
            except form_spec.FieldError as error:
                self.query_one("#inv-error", Static).update(escape(str(error)))
                return
            problem = self.form.problem(values)
            if problem:
                self.query_one("#inv-error", Static).update(escape(problem))
                return
            self.dismiss(self.form.plan_of(values))

    def _list_label(self, key: str) -> str:
        spec = next(s for s in self._fields if s.key == key)
        assert spec.display is not None
        return escape(spec.display(self._lists.get(key, [])))

    def _edit_list(self, key: str) -> None:
        """Edit a list field on its own screen (prompts.terminal_fields)."""
        spec = next(s for s in self._fields if s.key == key)
        [screen_spec] = terminal_fields([spec])
        assert screen_spec.picker is not None

        def done(chosen: Any) -> None:
            if chosen is None:
                return
            self._lists[key] = list(chosen)
            widget = "#inv-more-texts" if key == "more_texts" else "#inv-taught"
            self.query_one(widget, Button).label = self._list_label(key)
            self._refresh()

        self.app.push_screen(screen_spec.picker(self._lists.get(key, [])), done)

    def _choose_start(self) -> None:
        """Choose the spell the design starts from (any spell, the magus's
        known ones first) or a blank design."""

        def chosen(end: object) -> None:
            if isinstance(end, Picked):
                self._start_from(end.value)

        design = self.form.design
        run_steps(
            self.app,
            choose_template(
                self.saga, self.magus, design.source_spell_id if design else None
            ),
            chosen,
        )

    def _guideline_label(self) -> str:
        return escape(guideline_forms.guideline_label(self._guideline))

    def _choose_guideline(self) -> None:
        """Choose the supplement guideline the spell is based on: it fills
        in the Arts, base level and Base effect, as the core's field does."""

        def chosen(end: object) -> None:
            if isinstance(end, Picked):
                self._use_guideline(end.value)

        run_steps(
            self.app,
            guideline_forms.choose_guideline(self.saga, self._guideline),
            chosen,
        )

    def _use_guideline(self, guideline_id: str | None) -> None:
        self._guideline = guideline_id
        self.query_one("#inv-guideline", Button).label = self._guideline_label()
        filled = guideline_forms.guideline_values({"guideline": guideline_id})
        for key in ("technique", "form", "target"):
            if key in filled:
                self.query_one(f"#{_WIDGET_OF[key]}", Select).value = filled[key]
        for key in ("base_level", "base_effect"):
            if key in filled:
                self.query_one(f"#{_WIDGET_OF[key]}", Input).value = str(filled[key])
        self._refresh()

    def _start_from(self, spell_id: str | None) -> None:
        spell = catalog.find_spell(self.saga, spell_id)
        self._fill(
            design_from(spell) if spell is not None else None,
            None,
            keep_lab_options=True,
        )

    def _initial_design(self) -> SpellDesign | None:
        return self._design

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
        self.form.design = design
        self.form.key = design.key if design and design.key else uuid.uuid4().hex[:12]
        self.query_one("#inv-start", Button).label = self._start_label()
        self._guideline = guideline_forms.design_guideline(design)
        self.query_one("#inv-guideline", Button).label = self._guideline_label()
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
        self.query_one("#inv-lasting", Checkbox).value = bool(design and design.lasting)
        for kind in KINDS:
            current = getattr(design, kind) if design else lpf.FIRST_STEPS[kind]
            chosen, other_name = self.form.parameter_choice(kind, current)
            self.query_one(f"#inv-{kind}", Select).value = chosen
            self.query_one(f"#inv-{kind}-name", Input).value = other_name
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
        for recurs in self.query("#inv-recurring").results(Select):
            recurs.value = (design.recurring if design else "") or Select.NULL
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
        self.activity = self.initial_activity
        self.query_one("#inv-activity", Button).label = self._activity_label(
            self.activity
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
        self.query_one("#inv-other-vis", Input).value = (
            str(plan.other_vis) if plan else "0"
        )
        self.query_one("#inv-vis-from", Select).value = (
            plan.vis_from if plan and plan.vis_from else "laboratory"
        )
        self._ready = True
        self.call_after_refresh(self._refresh)
