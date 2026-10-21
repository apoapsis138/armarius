"""Planning a laboratory's seasons, independent of how they are drawn: the
lab work form (the plan its values describe, what refuses it, and the
Lab Total and when the work is done, worked out as it is filled in), and
the laboratory's Planning list's New Spell, Plan and Clear
(commands.SectionOps).

One form plans every kind of lab work, each field shown only for the
work that uses it: inventing a spell (from any spell as its template,
the magus's own known spells first, or a blank design), learning one from a Lab Text, decoding a text, extracting
vis, fixing an Arcane Connection, a Longevity Ritual, enchanting, binding
and empowering a familiar, taming, moving the lab and the rest. The
terminal draws this same form on its own full screen (InventSpellScreen),
which needs more than one field per row.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any

from .. import books, seasons
from .. import enchanted_devices as ed
from .. import lab_texts as lt
from .. import spells as spl
from ..arts import ARTS, FORMS, TECHNIQUES
from ..commands import (
    Choice,
    Choose,
    Command,
    Confirm,
    Form,
    Picked,
    Refuse,
    SectionOps,
    notes,
)
from ..familiars import familiar_of
from ..form_spec import ChoiceReads, DialogField, pairs, read_for_choice
from ..markup import escape, todo
from ..models import (
    Book,
    Character,
    Laboratory,
    Saga,
    SeasonPlan,
    Spell,
    SpellDesign,
    next_season,
)
from ..rules import activities as season_rules
from ..rules import book_seasons as bs
from ..rules import enchant_seasons as es
from ..rules import experiment as ex
from ..rules import familiar_seasons as fs
from ..rules import lab_seasons, spell_levels
from ..rules import laboratory_seasons as ls
from ..seasons import pairs as paired_plans
from ..seasons.projection import as_then
from . import activity as activity_forms
from . import spell as spell_forms

#: The Range/Duration/Target choice for one the app doesn't list.
OTHER = "__other__"
#: The design's Range, Duration and Target, and the steps each lists.
KINDS: tuple[str, ...] = ("range", "duration", "target")
_STANDARD = {
    "range": spell_levels.RANGE_STEPS,
    "duration": spell_levels.DURATION_STEPS,
    "target": spell_levels.TARGET_STEPS,
}
#: A new design's Range, Duration and Target.
FIRST_STEPS = {"range": "Personal", "duration": "Momentary", "target": "Individual"}

#: The desktop's names for the Planning list's buttons.
NOUNS = ("New Spell", "Plan", "Clear")

#: The last line of most lab work's results.
EXPOSURE = "Every lab season also gives 2 xp Exposure in Magic Theory."

NO_OWNER = "Give the laboratory a magus as its owner to plan lab work."

ShowIf = Callable[[dict[str, Any]], bool]


def _doing(*keys: str) -> ShowIf:
    """A field's show_if: shown while the lab work is one of `keys`."""
    return lambda values: values.get("activity") in keys


def _chosen(values: dict[str, Any]) -> bool:
    return bool(values.get("activity"))


def _vis_from_shown(values: dict[str, Any]) -> bool:
    activity = values.get("activity")
    return bool(activity) and activity not in (
        *lab_seasons.SPELL_ACTIVITIES,
        bs.DECODE_TEXT,
        es.CHARGED_WORK,
        es.ATTUNE,
        es.INVESTIGATE,
        lab_seasons.EXTRACT,
        *ls.ACTIVITIES,
    )


def design_from(spell: Spell) -> SpellDesign:
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


#: The template list's filter, and its value for each kind of spell.
FROM = "From"
OTHER_SPELLS = "Every other spell"
#: The template list's entry for a blank design.
BLANK = Choice("A new spell (a blank design)", None, search="new blank")


def known_heading(magus: Character) -> str:
    return f"Known to {magus.name}"


def _with_from(choice: Choice, kind: str) -> Choice:
    return Choice(
        choice.label, choice.value, choice.detail, choice.search, ((FROM, kind),)
    )


def choose_template(
    saga: Saga,
    magus: Character,
    current: str | None = None,
    apply: Callable[[Any], Any] = Picked,
) -> Choose:
    """The spell a new design starts from: a blank design, then every spell
    there is, the magus's own known spells first (a variant of one they
    know), each copied into the design to change as they like."""
    known_ids = {k.spell_id for k in magus.spells_known}

    def choices() -> list[Choice]:
        every = spell_forms.spell_choices(saga, set())
        known = [
            _with_from(c, known_heading(magus)) for c in every if c.value in known_ids
        ]
        rest = [_with_from(c, OTHER_SPELLS) for c in every if c.value not in known_ids]
        return [BLANK, *known, *rest]

    return Choose(
        f"Start {escape(magus.name)}'s spell from...",
        choices,
        apply,
        empty="No spells to start from.",
        others=lambda: [
            _with_from(c, OTHER_SPELLS)
            for c in spell_forms.spell_choices(saga, set(), in_play=False)
        ],
        help_id="invent-spell-start",
        filters=(FROM,),
    )


def template_label(saga: Saga, spell_id: str | None) -> str:
    """How the Start from field shows the spell a design started from."""
    source = spl.find_spell(saga, spell_id)
    if source is None:
        return "(a new spell)"
    level = "Gen" if source.level is None else source.level
    return f"{source.name}  {spl.shorthand(source)}  (level {level})"


class LabPlanForm:
    """The lab work form for `magus` in `lab`, `season` `year`: `existing`
    the season's lab plan being changed (None: a new one), `design` the
    spell design it starts from and `activity` what a new plan starts as."""

    def __init__(
        self,
        saga: Saga,
        magus: Character,
        lab: Laboratory,
        season: str,
        year: int,
        existing: SeasonPlan | None,
        *,
        design: SpellDesign | None = None,
        activity: str | None = None,
    ) -> None:
        self.saga, self.magus, self.lab = saga, magus, lab
        self.season, self.year = season, year
        plan = existing if existing is not None and existing.lab_id else None
        self.existing = plan
        self.activity = plan.activity if plan else activity
        if design is None and plan is not None:
            design = plan.design
            if design is None and plan.spell_id:
                spell = spl.find_spell(saga, plan.spell_id)
                design = design_from(spell) if spell else None
        self.design = design
        self.key = design.key if design and design.key else uuid.uuid4().hex[:12]
        vf_ids = {vf.vf_id for vf in magus.virtues_flaws}
        self.parameter_options = {
            kind: [(name, name) for name in _STANDARD[kind]]
            + [
                (escape(f"{e.name} (as {e.costs_as})"), e.name)
                for e in spell_levels.extra_parameters(kind, vf_ids)
            ]
            + [("Other...", OTHER)]
            for kind in KINDS
        }

    # -- the fields ----------------------------------------------------------

    def title(self) -> str:
        return (
            f"Lab Work: {escape(self.magus.name)} in {escape(self.lab.name)}, "
            f"{self.season} {self.year}"
        )

    def fields(self) -> list[DialogField]:
        return [
            DialogField(
                "activity",
                "Lab work",
                "picker",
                self.activity,
                allow_blank=True,
                placeholder="(choose the lab work...)",
                choose=lambda current: activity_forms.choose_activity(
                    self.saga, self.magus, current, lab=True
                ),
                display=activity_forms.activity_label,
                hint="The line above Schedule shows the Lab Total and when "
                "it will be done.",
            ),
            *self._design_fields(),
            *self._text_fields(),
            *self._target_fields(),
            *self._other_work_fields(),
            *self._common_fields(),
        ]

    def _design_fields(self) -> list[DialogField]:
        """The spell's design: its name and effect, its Arts, Range /
        Duration / Target and its level."""
        design, inventing = self.design, _doing(lab_seasons.INVENT)
        found = [
            DialogField(
                "start_from",
                "Start from",
                "picker",
                design.source_spell_id if design else None,
                allow_blank=True,
                placeholder="(a new spell)",
                choose=lambda current: choose_template(self.saga, self.magus, current),
                display=lambda spell_id: template_label(self.saga, spell_id),
                show_if=inventing,
                fills=self.design_values,
                hint="Any spell, the magus's own known spells first: its "
                "figures fill the design in, to change as you like.",
            ),
            DialogField(
                "name",
                "Spell name",
                "text",
                design.name if design else "",
                show_if=inventing,
                hint=self._start_hint(),
            ),
            DialogField(
                "description",
                "Effect",
                "area",
                design.description if design else "",
                show_if=inventing,
            ),
            DialogField(
                "technique",
                "Technique",
                "select",
                (design.technique if design else "") or None,
                options=pairs(TECHNIQUES),
                allow_blank=True,
                placeholder="(choose)",
                show_if=inventing,
            ),
            DialogField(
                "form",
                "Form",
                "select",
                (design.form if design else "") or None,
                options=pairs(FORMS),
                allow_blank=True,
                placeholder="(choose)",
                show_if=inventing,
            ),
            DialogField(
                "requisites",
                "Requisites",
                "text",
                ", ".join(design.requisites) if design else "",
                placeholder="e.g. Rego",
                show_if=inventing,
            ),
            DialogField(
                "base_level",
                "Base level",
                "optint",
                design.base_level if design else None,
                show_if=inventing,
                hint="The level is worked out from it.",
            ),
            DialogField(
                "ritual",
                "Ritual",
                "check",
                bool(design and design.ritual),
                show_if=inventing,
            ),
        ]
        for kind in KINDS:
            current = getattr(design, kind) if design else FIRST_STEPS[kind]
            values = [v for _, v in self.parameter_options[kind]]
            steps = design.custom_steps.get(kind) if design else None
            other = _other_is(kind)
            found += [
                DialogField(
                    kind,
                    kind.title(),
                    "select",
                    current if current in values else OTHER,
                    options=self.parameter_options[kind],
                    show_if=inventing,
                ),
                DialogField(
                    f"{kind}_name",
                    f"Other {kind}",
                    "text",
                    current if current not in values else "",
                    placeholder="name",
                    show_if=other,
                ),
                DialogField(
                    f"{kind}_steps",
                    f"Other {kind}'s magnitudes",
                    "optint",
                    steps,
                    placeholder="+n",
                    show_if=other,
                ),
            ]
        found += [
            DialogField(
                "extra_magnitudes",
                "Size / extra magnitudes",
                "int",
                design.extra_magnitudes if design else 0,
                show_if=inventing,
            ),
            DialogField(
                "base_effect",
                "Base effect",
                "text",
                design.base_effect if design else "",
                placeholder="the guideline used",
                show_if=inventing,
            ),
        ]
        return found

    def design_values(self, values: dict[str, Any]) -> dict[str, Any]:
        """The design fields' values from the spell Start from names (all
        blank for a new spell)."""
        spell = spl.find_spell(self.saga, values.get("start_from"))
        design = design_from(spell) if spell is not None else None
        found: dict[str, Any] = {
            "name": design.name if design else "",
            "description": design.description if design else "",
            "technique": (design.technique if design else "") or None,
            "form": (design.form if design else "") or None,
            "requisites": ", ".join(design.requisites) if design else "",
            "base_level": design.base_level if design else None,
            "ritual": bool(design and design.ritual),
            "extra_magnitudes": design.extra_magnitudes if design else 0,
            "base_effect": "",
        }
        for kind in KINDS:
            current = getattr(design, kind) if design else FIRST_STEPS[kind]
            listed = [v for _, v in self.parameter_options[kind]]
            found[kind] = current if current in listed else OTHER
            found[f"{kind}_name"] = current if current not in listed else ""
            found[f"{kind}_steps"] = None
        return found

    def _start_hint(self) -> str:
        source = spl.find_spell(
            self.saga, self.design.source_spell_id if self.design else None
        )
        if source is None:
            return "A new spell."
        level = "Gen" if source.level is None else source.level
        return f"Started from {source.name} {spl.shorthand(source)} (level {level})."

    def _text_fields(self) -> list[DialogField]:
        """The Lab Text to invent from, and the raw text to decode."""
        plan = self.existing
        undecoded = self.undecoded()
        return [
            DialogField(
                "lab_text",
                "Lab Text",
                "select",
                plan.book_id
                if plan and plan.activity == lab_seasons.LAB_TEXT
                else None,
                options=[
                    (escape(b.name + lt.cant_read_tag(self.saga, self.magus, b)), b.id)
                    for b in lab_seasons.lab_texts_at_hand(self.saga, self.magus)
                ],
                allow_blank=True,
                placeholder="(choose the Lab Text)",
                show_if=_doing(lab_seasons.LAB_TEXT),
            ),
            DialogField(
                "decode",
                "Lab Text to decode",
                "select",
                plan.book_id
                if plan
                and plan.activity == bs.DECODE_TEXT
                and plan.book_id in [b.id for b in undecoded]
                else None,
                options=[
                    (f"{escape(b.name)} ({escape(bs.author_name(self.saga, b))})", b.id)
                    for b in undecoded
                ],
                allow_blank=True,
                placeholder="(a raw text by another magus)",
                show_if=_doing(bs.DECODE_TEXT),
            ),
        ]

    def _target_fields(self) -> list[DialogField]:
        """What lab work other than inventing acts on: an Arcane Connection,
        the person a Longevity Ritual is for, a device and its effects."""
        plan = self.existing
        connections = self.connections()
        devices = self.devices()
        effects = self._effects()
        texts = self._effect_texts()
        enchanting = _doing(*es.ACTIVITIES)
        on_effect = _doing(*es.EFFECT_ACTIVITIES)
        return [
            DialogField(
                "connection",
                "Connection to",
                "select",
                _kept(plan.connection_id if plan else None, connections),
                options=connections,
                allow_blank=True,
                placeholder="(choose; add them on the Stores chapter)",
                show_if=_doing(lab_seasons.FIX_AC),
            ),
            DialogField(
                "subject",
                "For",
                "select",
                plan.subject_id if plan and plan.subject_id else self.magus.id,
                options=self.subjects(),
                show_if=_doing(lab_seasons.LONGEVITY),
            ),
            DialogField(
                "longevity_vis",
                "Vis",
                "select",
                plan.vis_art
                if plan and plan.vis_art in lab_seasons.LONGEVITY_VIS_ARTS
                else "Creo",
                options=pairs(lab_seasons.LONGEVITY_VIS_ARTS),
                show_if=_doing(lab_seasons.LONGEVITY),
            ),
            DialogField(
                "extra_vis",
                "Extra pawns",
                "int",
                plan.extra_vis if plan else 0,
                show_if=_doing(lab_seasons.LONGEVITY),
            ),
            DialogField(
                "device",
                "Device",
                "select",
                _kept(plan.device_id if plan else None, devices),
                options=devices,
                allow_blank=True,
                placeholder="(choose; they're kept on the Inventory chapters)",
                show_if=enchanting,
            ),
            DialogField(
                "shape",
                "Shape & material",
                "int",
                plan.shape_bonus if plan else 0,
                show_if=enchanting,
            ),
            DialogField(
                "effect",
                "Effect",
                "select",
                _kept(plan.effect_id if plan else None, effects),
                options=effects,
                allow_blank=True,
                placeholder="(choose)",
                show_if=on_effect,
                hint="Choosing an effect chooses its device.",
                fills=self._device_of_effect,
            ),
            DialogField(
                "effect_text",
                "From Lab Text",
                "select",
                _kept(plan.book_id if plan else None, texts),
                options=texts,
                allow_blank=True,
                placeholder="(none: instil it the long way)",
                show_if=on_effect,
            ),
        ]

    def _other_work_fields(self) -> list[DialogField]:
        """The rest of the lab work: binding a familiar and its powers,
        taming a creature, moving the lab, a die, and where vis comes from."""
        return [
            *self._binding_fields(),
            *self._power_vis_fields(),
            *self._taming_and_moving_fields(),
            *self._die_and_vis_fields(),
        ]

    def _binding_fields(self) -> list[DialogField]:
        """Binding a familiar: the Technique and Form, and its cords."""
        plan = self.existing
        binding = _doing(fs.BIND)
        found = [
            DialogField(
                "bind_technique",
                "Technique",
                "select",
                (plan.technique if plan else "") or None,
                options=pairs(TECHNIQUES),
                allow_blank=True,
                placeholder="(choose)",
                show_if=binding,
            ),
            DialogField(
                "bind_form",
                "Form",
                "select",
                (plan.form if plan and plan.activity == fs.BIND else "") or None,
                options=pairs(FORMS),
                allow_blank=True,
                placeholder="(choose)",
                show_if=binding,
            ),
        ]
        for cord in ("golden", "silver", "bronze"):
            found.append(
                DialogField(
                    f"{cord}_cord",
                    f"{cord.title()} cord",
                    "int",
                    getattr(plan, f"{cord}_cord") if plan else 0,
                    show_if=binding,
                )
            )
        return found

    def _power_vis_fields(self) -> list[DialogField]:
        """The bond power a familiar is empowered with, and the Art whose
        vis an effect, a binding or a power spends."""
        plan = self.existing
        powers = self.powers()
        return [
            DialogField(
                "power",
                "Bond power",
                "select",
                _kept(plan.effect_id if plan else None, powers),
                options=powers,
                allow_blank=True,
                placeholder="(choose; add it on the familiar's page)",
                show_if=_doing(fs.EMPOWER),
            ),
            DialogField(
                "effect_vis",
                "Vis of",
                "select",
                (plan.vis_art if plan else "") or None,
                options=pairs(ARTS),
                allow_blank=True,
                placeholder="(the work's Technique)",
                show_if=_doing(es.INSTIL, es.LESSER_WORK, fs.BIND, fs.EMPOWER),
                hint="The Art whose vis is spent: the effect's or power's "
                "Technique or Form.",
            ),
        ]

    def _taming_and_moving_fields(self) -> list[DialogField]:
        """Taming a creature (its name, Form and Might), and moving the lab
        (where to, and whether by spell)."""
        plan = self.existing
        taming = _doing(lab_seasons.TAMING)
        tamed = plan if plan and plan.activity == lab_seasons.TAMING else None
        moving = _doing(ls.MOVE)
        return [
            DialogField(
                "creature",
                "Creature",
                "text",
                tamed.title if tamed else "",
                placeholder="its name",
                show_if=taming,
            ),
            DialogField(
                "creature_form",
                "Its Form",
                "select",
                (tamed.form if tamed else "") or None,
                options=pairs(FORMS),
                allow_blank=True,
                placeholder="(choose)",
                show_if=taming,
            ),
            DialogField(
                "might",
                "Its Might",
                "optint",
                tamed.book_level if tamed else None,
                show_if=taming,
            ),
            DialogField(
                "move_to",
                "Moving to",
                "text",
                plan.title if plan and plan.activity == ls.MOVE else "",
                placeholder="the new location",
                show_if=moving,
            ),
            DialogField(
                "by_spell",
                "By spell",
                "check",
                bool(plan and plan.by_spell),
                show_if=moving,
            ),
        ]

    def _die_and_vis_fields(self) -> list[DialogField]:
        """A typed die, and where extracted vis goes or spent vis comes
        from."""
        plan = self.existing
        vis_place = plan.vis_from if plan and plan.vis_from else "laboratory"
        return [
            DialogField(
                "die",
                "Die (blank: rolled)",
                "optint",
                plan.die if plan else None,
                show_if=_doing(es.INVESTIGATE, *ls.ROLLED),
                hint="Blank: rolled when the season is played; a typed die "
                "is used for one roll.",
            ),
            DialogField(
                "vis_to",
                "Vis goes to",
                "select",
                vis_place,
                options=self.vis_places(),
                show_if=_doing(lab_seasons.EXTRACT),
            ),
            DialogField(
                "vis_from",
                "Vis from",
                "select",
                vis_place,
                options=self.vis_places(),
                show_if=_vis_from_shown,
            ),
        ]

    def _common_fields(self) -> list[DialogField]:
        """What every kind of lab work shares: experimenting, a similar
        spell, Focus and specialty, days away, other modifiers and notes."""
        plan = self.existing
        known = [
            (escape(spell.name), spell.id)
            for k in self.magus.spells_known
            if (spell := spl.find_spell(self.saga, k.spell_id)) is not None
        ]
        experimental = _doing(*lab_seasons.EXPERIMENTAL)
        researching = _doing(*lab_seasons.EXPERIMENTAL, ex.STABILIZE)
        found = [
            DialogField(
                "experimenting",
                "Experiment",
                "check",
                bool(plan and plan.experimenting),
                show_if=experimental,
            ),
            DialogField(
                "risk",
                "Risk +",
                "int",
                plan.risk if plan else 0,
                show_if=researching,
            ),
            DialogField(
                "research",
                "Research goal",
                "text",
                plan.research if plan else "",
                placeholder="(optional)",
                show_if=researching,
            ),
            DialogField(
                "research_kind",
                "Breakthrough",
                "select",
                (plan.research_kind if plan else "Minor") or "Minor",
                options=pairs(ex.KINDS),
                show_if=researching,
            ),
            DialogField(
                "similar",
                "Similar spell known",
                "select",
                _kept(plan.similar_spell_id if plan else None, known),
                options=known,
                allow_blank=True,
                placeholder="(none)",
                show_if=_doing(lab_seasons.INVENT),
            ),
        ]
        if lab_seasons.has_focus(self.magus):
            found.append(
                DialogField(
                    "focus",
                    "Magical Focus",
                    "check",
                    bool(plan and plan.focus),
                    show_if=_chosen,
                )
            )
        specialty = lab_seasons.theory_specialty(self.magus)
        if specialty:
            found.append(
                DialogField(
                    "specialty",
                    f"Magic Theory ({escape(specialty)})",
                    "check",
                    bool(plan and plan.theory_specialty),
                    show_if=_chosen,
                )
            )
        found += [
            DialogField(
                "days_away",
                "Days away",
                "int",
                plan.days_away if plan else 0,
                show_if=_chosen,
                hint="10 cost nothing, 11-20 lower the Lab Total, more rule it out.",
            ),
            DialogField(
                "other_modifier",
                "Other modifiers",
                "int",
                plan.other_modifier if plan else 0,
                show_if=_chosen,
            ),
            DialogField(
                "assistant",
                "Assistant",
                "select",
                _kept(self.assistant_of(plan), self.helpers()),
                options=self.helpers(),
                allow_blank=True,
                placeholder="(none)",
                show_if=_chosen,
                hint="Their season is planned as Assist in a laboratory with "
                "it: + their Intelligence and Magic Theory.",
            ),
            DialogField(
                "details",
                "Notes",
                "text",
                plan.details if plan else "",
                show_if=_chosen,
            ),
        ]
        return found

    # -- the choices --------------------------------------------------------

    def helpers(self) -> list[tuple[str, str]]:
        """Who could assist: anyone else with The Gift and Magic Theory."""
        return [
            (escape(c.name), c.id)
            for c in self.saga.characters
            if c is not self.magus and ls.can_assist(c)
        ]

    def assistant_of(self, plan: SeasonPlan | None) -> str | None:
        """The assistant named on the plan, or one already assisting."""
        if plan is None:
            return None
        if plan.assistant_ids:
            return plan.assistant_ids[0]
        helpers = ls.assistants(self.saga, self.magus, plan)
        return helpers[0].id if helpers else None

    def vis_places(self) -> list[tuple[str, str]]:
        return [
            ("the laboratory's raw vis", "laboratory"),
            (f"{escape(self.magus.name)}'s raw vis", "character"),
            ("the covenant's vis stores", "covenant"),
        ]

    def connections(self) -> list[tuple[str, str]]:
        """The lab's Arcane Connections not yet fixed (and the plan's own)."""
        mine = self.existing.connection_id if self.existing else None
        return [
            (escape(c.to), c.id)
            for c in self.lab.arcane_connections
            if not c.fixed or c.id == mine
        ]

    def devices(self) -> list[tuple[str, str]]:
        """The enchanted devices the magus can work on here."""
        return [
            (f"{escape(d.name)} ({d.type})", d.id)
            for d in es.devices_for(self.saga, self.magus, self.lab)
        ]

    def _effects(self) -> list[tuple[str, str]]:
        """Every effect of those devices, named with its device."""
        return [
            (
                f"{escape(d.name)}: {escape(ed.effect_name(e))} "
                f"(level {ed.modified_level(d, e)})",
                e.id,
            )
            for d in es.devices_for(self.saga, self.magus, self.lab)
            for e in d.effects
        ]

    def _device_of_effect(self, values: dict[str, Any]) -> dict[str, Any]:
        """Choosing an effect chooses the device it is in."""
        for device in es.devices_for(self.saga, self.magus, self.lab):
            if any(e.id == values.get("effect") for e in device.effects):
                return {"device": device.id}
        return {}

    def _effect_texts(self) -> list[tuple[str, str]]:
        """The enchantment Lab Texts the magus could instil an effect of
        these devices from, named with the effect."""
        found: list[tuple[str, str]] = []
        seen: set[str] = set()
        for device in es.devices_for(self.saga, self.magus, self.lab):
            for effect in device.effects:
                for text in es.effect_texts(self.saga, self.magus, device, effect):
                    if text.id in seen:
                        continue
                    seen.add(text.id)
                    found.append(
                        (
                            f"{escape(text.name)} "
                            f"({escape(bs.author_name(self.saga, text))})",
                            text.id,
                        )
                    )
        return found

    def undecoded(self) -> list[Book]:
        """Raw Lab Texts by other magi that the magus can get at but not
        read yet."""
        return [
            b
            for b in self.saga.books
            if b.type == "Lab Text"
            and b.raw
            and books.can_read(self.saga, self.magus, b)
            and not bs.can_use_lab_text(self.magus, b)
        ]

    def powers(self) -> list[tuple[str, str]]:
        familiar = familiar_of(self.saga, self.magus.id)
        if familiar is None:
            return []
        return [
            (f"{escape(p.name) or '(unnamed)'} (level {p.level})", p.id)
            for p in familiar.bond_powers
        ]

    def subjects(self) -> list[tuple[str, str]]:
        """Who a Longevity Ritual can be for: the magus first, then everyone
        else in the saga."""
        others = sorted(
            (c for c in self.saga.characters if c.id != self.magus.id),
            key=lambda c: c.name.lower(),
        )
        return [(f"{escape(self.magus.name)} (own)", self.magus.id)] + [
            (f"{escape(c.name)} ({c.type})", c.id) for c in others
        ]

    def work_arts(self, plan: SeasonPlan) -> list[str]:
        """The Technique and Form of what `plan` works on, whose vis it may
        spend."""
        if plan.activity == fs.BIND:
            return [a for a in (plan.technique, plan.form) if a]
        if plan.activity == fs.EMPOWER:
            familiar = familiar_of(self.saga, self.magus.id)
            power = fs.power_of(familiar, plan) if familiar is not None else None
            return [a for a in (power.technique, power.form) if a] if power else []
        device = es.device_of(self.saga, plan)
        effect = es.effect_of(device, plan) if device is not None else None
        if effect is None:
            return []
        return [a for a in (effect.technique, effect.form) if a]

    # -- the plan -----------------------------------------------------------

    def design_of(self, values: dict[str, Any]) -> SpellDesign:
        custom: dict[str, int] = {}
        chosen: dict[str, str] = {}
        for kind in KINDS:
            value = values.get(kind) or ""
            if value == OTHER:
                chosen[kind] = (values.get(f"{kind}_name") or "").strip() or "Other"
                steps = values.get(f"{kind}_steps")
                if steps is not None:
                    custom[kind] = steps
            else:
                chosen[kind] = value
        design = self.design
        if "start_from" in values:
            # The spell Start from names now, and its level as printed when
            # it records no base level.
            source = spl.find_spell(self.saga, values.get("start_from"))
            design = design_from(source) if source is not None else None
        return SpellDesign(
            key=self.key,
            name=values.get("name") or "",
            technique=values.get("technique") or "",
            form=values.get("form") or "",
            requisites=spl.parse_requisites(values.get("requisites") or ""),
            base_level=values.get("base_level"),
            range=chosen["range"],
            duration=chosen["duration"],
            target=chosen["target"],
            custom_steps=custom,
            extra_magnitudes=values.get("extra_magnitudes") or 0,
            ritual=bool(values.get("ritual")),
            description=values.get("description") or "",
            base_effect=values.get("base_effect") or "",
            source_spell_id=design.source_spell_id if design else None,
            printed_level=design.printed_level if design else None,
        )

    def plan_of(self, values: dict[str, Any]) -> SeasonPlan:
        """The plan the form's values describe (hidden fields are missing
        from `values`, so everything is read with a default)."""
        activity = values.get("activity") or ""
        plan = SeasonPlan(
            character_id=self.magus.id,
            year=self.year,
            season=self.season,
            activity=activity,
            lab_id=self.lab.id,
            days_away=values.get("days_away") or 0,
            focus=bool(values.get("focus")),
            theory_specialty=bool(values.get("specialty")),
            other_modifier=values.get("other_modifier") or 0,
            details=values.get("details") or "",
            assistant_ids=[values["assistant"]] if values.get("assistant") else [],
            vis_from=self._vis_from(activity, values),
            risk=values.get("risk") or 0,
            research=values.get("research") or "",
            research_kind=values.get("research_kind") or "Minor",
            **read_for_choice(activity, values, self._reads()),
        )
        if activity in (*es.ACTIVITIES, *fs.ACTIVITIES):
            # The vis is of the work's Technique unless its Form is chosen.
            arts = self.work_arts(plan)
            chosen = values.get("effect_vis")
            plan.vis_art = chosen if chosen in arts else (arts[0] if arts else "")
        return plan

    def _reads(self) -> ChoiceReads:
        """The form's fields that only some lab work reads, and the plan's
        fields they set (Strategy, as a table); a plan's field no work here
        reads keeps its default."""

        def longevity(v: dict[str, Any]) -> dict[str, Any]:
            subject = v.get("subject")
            return {
                "subject_id": (
                    subject if subject and subject != self.magus.id else None
                ),
                "vis_art": v.get("longevity_vis") or "",
                "extra_vis": v.get("extra_vis") or 0,
            }

        return (
            (
                (lab_seasons.INVENT,),
                lambda v: {
                    "design": self.design_of(v),
                    "similar_spell_id": v.get("similar"),
                },
            ),
            ((lab_seasons.LAB_TEXT,), lambda v: {"book_id": v.get("lab_text")}),
            ((bs.DECODE_TEXT,), lambda v: {"book_id": v.get("decode")}),
            (
                es.EFFECT_ACTIVITIES,
                lambda v: {
                    "book_id": v.get("effect_text"),
                    "effect_id": v.get("effect"),
                },
            ),
            ((fs.EMPOWER,), lambda v: {"effect_id": v.get("power")}),
            ((lab_seasons.LONGEVITY,), longevity),
            (
                es.ACTIVITIES,
                lambda v: {
                    "device_id": v.get("device"),
                    "shape_bonus": v.get("shape") or 0,
                },
            ),
            (
                lab_seasons.EXPERIMENTAL,
                lambda v: {"experimenting": bool(v.get("experimenting"))},
            ),
            (
                (ls.MOVE,),
                lambda v: {
                    "title": v.get("move_to") or "",
                    "by_spell": bool(v.get("by_spell")),
                },
            ),
            (
                (lab_seasons.TAMING,),
                lambda v: {
                    "title": v.get("creature") or "",
                    "book_level": v.get("might"),
                    "form": v.get("creature_form") or "",
                },
            ),
            (
                (fs.BIND,),
                lambda v: {
                    "technique": v.get("bind_technique") or "",
                    "form": v.get("bind_form") or "",
                    "golden_cord": v.get("golden_cord") or 0,
                    "silver_cord": v.get("silver_cord") or 0,
                    "bronze_cord": v.get("bronze_cord") or 0,
                },
            ),
            ((es.INVESTIGATE, *ls.ROLLED), lambda v: {"die": v.get("die")}),
            ((lab_seasons.FIX_AC,), lambda v: {"connection_id": v.get("connection")}),
        )

    def _vis_from(self, activity: str, values: dict[str, Any]) -> str:
        """Where the work's vis comes from (or, extracting, goes to): none
        for inventing a spell; the laboratory's unless another is chosen."""
        if activity in lab_seasons.SPELL_ACTIVITIES:
            return ""
        key = "vis_to" if activity == lab_seasons.EXTRACT else "vis_from"
        kept = self.existing.vis_from if self.existing else ""
        return values.get(key) or kept or "laboratory"

    def problem(self, values: dict[str, Any]) -> str | None:
        """Why the lab work can't be scheduled, or None."""
        plan = self.plan_of(values)
        if not plan.activity:
            return "Choose the lab work."
        if plan.activity in es.EFFECT_ACTIVITIES and plan.effect_id:
            device = es.device_of(self.saga, plan)
            if device is None or es.effect_of(device, plan) is None:
                return "Choose an effect of the chosen device."
        paired = paired_plans.pair_problem(self.saga, self.magus, plan)
        if paired is not None:
            return paired
        with paired_plans.in_place(self.saga, self.magus, plan):
            found = season_rules.problems(self.magus, plan, self.saga)
        return found[0] if found else None

    # -- the line above Schedule ------------------------------------------

    def live(self, values: dict[str, Any]) -> str:
        """The design's level, the Lab Total and when the work is done,
        for a season ahead from the magus and laboratory as the seasons
        planned before it leave them."""
        plan = self.plan_of(values)
        then, magus = as_then(self.saga, self.magus, plan.season, plan.year)
        with paired_plans.in_place(then, magus, plan):
            return self._live(then, magus, plan)

    def work_of(self, plan: SeasonPlan) -> lab_seasons.LabWork | None:
        """What the plan does (its Lab Total and progress), for a season
        ahead from the magus as the seasons planned before it leave them."""
        then, magus = as_then(self.saga, self.magus, plan.season, plan.year)
        with paired_plans.in_place(then, magus, plan):
            return lab_seasons.work(then, magus, plan)[1]

    def _live(self, saga: Saga, magus: Character, plan: SeasonPlan) -> str:
        if not plan.activity:
            return "[dim]Choose the lab work.[/]"
        parts: list[str] = []
        if plan.design is not None:
            parts.append(level_text(plan.design))
        _, work = lab_seasons.work(saga, magus, plan)
        if work is None:
            parts.append("[b]Lab Total[/] [dim]--[/]")
        elif not work.lab_total.lines:
            parts.append("[b]Lab Total[/] [dim]none needed[/]")
            parts.append(" ".join(self.when_lines(plan, work)))
        else:
            terms = []
            for line in work.lab_total.lines:
                if line.amount is not None:
                    terms.append(f"{escape(line.label)} {line.amount:+g}")
                elif line.multiplier is not None:
                    terms.append(f"{escape(line.label)} x{line.multiplier:g}")
            parts.append(
                f"[b]Lab Total {int(work.lab_total.total)}[/]  "
                f"[dim]({', '.join(terms)})[/]"
            )
            parts.append(" ".join(self.when_lines(plan, work)))
        problems = season_rules.problems(magus, plan, saga)
        if problems:
            parts.append(f"[$text-error]{escape(problems[0])}[/]")
        return "\n".join(p for p in parts if p)

    def when_lines(self, plan: SeasonPlan, work: lab_seasons.LabWork) -> list[str]:
        """When the work is done and what it gives, a sentence a line
        (markup); EXPOSURE last when the season gives it."""
        season, year = self.season, self.year
        lab_total = int(work.lab_total.total)
        if plan.activity == lab_seasons.EXTRACT:
            return [
                f"Lab Total {lab_total}: {work.vis_gained} pawn(s) of Vim vis "
                f"this season, {season} {year}.",
                EXPOSURE,
            ]
        if plan.activity == lab_seasons.FIX_AC:
            return [
                f"Fixed this season, {season} {year}, for 1 pawn of Vim vis.",
                EXPOSURE,
            ]
        if plan.activity == lab_seasons.LONGEVITY:
            name = work.subject.name if work.subject is not None else "?"
            paid = ", ".join(f"{n} pawn(s) of {a}" for a, n in work.vis_cost.items())
            return [
                f"This season, {season} {year}: aging rolls -{work.longevity} "
                f"for {escape(name)}.",
                f"Vis: {paid}.",
                EXPOSURE,
            ]
        if plan.activity == ex.STABILIZE:
            return [
                f"This season, {season} {year}: stabilizing the Discovery "
                f"(magnitude {work.research_magnitude}) toward "
                f"{escape(plan.research)}.",
                "The Extraordinary Results chart is rolled when it's played.",
                EXPOSURE,
            ]
        if plan.activity == bs.DECODE_TEXT:
            return [f"{escape(seasons.work_text(work, plan))}.", EXPOSURE]
        if plan.activity == lab_seasons.LAB_TEXT:
            return [
                f"Level {work.level}, Lab Total {lab_total}: learned this season, "
                f"{season} {year}."
            ]
        if (
            plan.activity in (*es.ACTIVITIES, *ls.ACTIVITIES)
            or plan.activity == fs.BIND
        ) and plan.activity != es.INSTIL:
            return [
                f"This season, {season} {year}: "
                f"{escape(seasons.work_text(work, plan))}.",
                EXPOSURE,
            ]
        for _ in range(lab_seasons.seasons_left(work)):
            season, year = next_season(season, year)
        needed = lab_seasons.seasons_left(work) + 1
        done = "Invented" if plan.activity == lab_seasons.INVENT else "Instilled"
        return [
            f"Level {work.level}, Lab Total {lab_total}: {work.points_gained} "
            f"points a season, {work.points_before} of {work.level} so far.",
            f"{done} {season} {year} (projected: {needed} "
            f"season{'s' if needed != 1 else ''}).",
            EXPOSURE,
        ]

    # -- the step -----------------------------------------------------------

    def form(self) -> Form:
        def apply(values: dict[str, Any]) -> list[str]:
            added = seasons.plan_lab_work(self.saga, self.plan_of(values))
            if not added:
                return []
            last = added[-1]
            return notes(f"Planned through {last.season} {last.year} to finish it.")

        return Form(
            self.title(),
            self.fields,
            apply,
            validate=self.problem,
            live=self.live,
            save_label="Schedule",
        )


def _other_is(kind: str) -> ShowIf:
    return lambda values: (
        values.get("activity") == lab_seasons.INVENT and values.get(kind) == OTHER
    )


def _kept(value: str | None, options: list[tuple[str, str]]) -> str | None:
    """`value` when the options still offer it, else nothing chosen."""
    return value if value in {v for _, v in options} else None


def level_text(design: SpellDesign) -> str:
    """The design's level, worked out from its base level (markup)."""
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
        return todo(
            "An Other parameter needs its magnitudes typed (+n) to work out the level."
        )
    found = "".join(f"  {todo(escape(n))}" for n in worked.notes)
    return (
        f"[b]Level {worked.level}[/]  {escape(worked.design_line(design.base_level))}"
        + found
    )


# -- the Planning list's steps ----------------------------------------------------


def lab_owner(saga: Saga, lab: Laboratory) -> Character | None:
    """The magus who plans lab work here, or None."""
    owner = saga.character(lab.owner_id)
    return owner if owner is not None and owner.type == "magus" else None


def queue_season(saga: Saga, lab: Laboratory, index: int | None) -> tuple[str, int]:
    """The first season of the Planning list's row `index` (the current
    season with none chosen)."""
    rows = seasons.lab_queue(saga, lab)
    if not rows:
        return saga.current_season, saga.current_year
    row = rows[min(index or 0, len(rows) - 1)]
    return row.season, row.year


def plan_lab_season(saga: Saga, lab: Laboratory, index: int | None) -> Command:
    """Plan the lab work of row `index`'s season, or change it."""
    owner = lab_owner(saga, lab)
    if owner is None:
        return Refuse("Plan Lab Work", NO_OWNER)
    season, year = queue_season(saga, lab, index)
    existing = seasons.plan_for(saga, owner, season, year)
    return LabPlanForm(saga, owner, lab, season, year, existing).form()


def new_spell(saga: Saga, lab: Laboratory, index: int | None) -> Command:
    """Invent a spell in row `index`'s season: choose a spell to start
    from (or a blank design), then fill in the lab work."""
    owner = lab_owner(saga, lab)
    if owner is None:
        return Refuse("Invent a Spell", NO_OWNER)
    season, year = queue_season(saga, lab, index)

    def start(spell_id: str | None) -> Form:
        spell = spl.find_spell(saga, spell_id) if spell_id else None
        return LabPlanForm(
            saga,
            owner,
            lab,
            season,
            year,
            None,
            design=design_from(spell) if spell is not None else None,
            activity=lab_seasons.INVENT,
        ).form()

    return choose_template(saga, owner, apply=start)


def clear_lab_season(saga: Saga, lab: Laboratory, index: int | None) -> Command:
    """Clear row `index`'s season and the seasons scheduled to continue
    its work, after confirming."""
    owner = lab_owner(saga, lab)
    if owner is None:
        return Refuse("Clear Lab Work", NO_OWNER)
    season, year = queue_season(saga, lab, index)
    plan = seasons.plan_for(saga, owner, season, year)
    if plan is None:
        return Refuse("Clear Lab Work", f"Nothing is planned for {season} {year}.")
    removed = seasons.scheduled_with(saga, plan)
    paired = [p for each in removed for p in paired_plans.linked(saga, each)]

    def apply() -> None:
        paired_plans.clear_with(saga, [*removed, *paired])

    span = (
        f"{season} {year}"
        if len(removed) == 1
        else f"{season} {year} - {removed[-1].season} {removed[-1].year}"
    )
    also = (
        f" {escape(paired_plans.names(saga, paired))}'s plans with it are cleared too."
        if paired
        else ""
    )
    return Confirm(
        f"Clear {escape(owner.name)}'s plan for {span} "
        f"({escape(seasons.plan_summary(saga, owner, plan))})?{also}",
        apply,
        yes_label="Clear",
    )


def planning_ops(
    saga: Saga, lab: Laboratory, chosen: Callable[[], int | None] = lambda: None
) -> SectionOps:
    """The laboratory's Planning list: New Spell (in the chosen season, or
    the current one), and Plan and Clear for the row chosen. `chosen` is
    the row the front-end has chosen, for New Spell."""
    return SectionOps(
        add=lambda: new_spell(saga, lab, chosen()),
        edit=lambda index: plan_lab_season(saga, lab, index),
        remove=lambda index: clear_lab_season(saga, lab, index),
        rows=lambda: row_names(saga, lab),
    )


def row_names(saga: Saga, lab: Laboratory) -> list[str]:
    """Each Planning row as plain text: "Spring 1220  Invent a Spell: ..."."""
    owner = saga.character(lab.owner_id)
    return [
        f"{row.span}  "
        + (
            seasons.plan_summary(saga, owner, row.plan)
            if owner is not None and row.plan is not None
            else "nothing planned"
        )
        for row in seasons.lab_queue(saga, lab)
    ]
