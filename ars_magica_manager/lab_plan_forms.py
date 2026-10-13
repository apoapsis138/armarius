"""Planning a laboratory's seasons, independent of how they are drawn: the
lab work form (the plan its values describe, what refuses it, and the
Lab Total and when the work is done, worked out as it is filled in), and
the laboratory's Planning list's New Spell, Plan and Clear
(commands.SectionOps).

One form plans every kind of lab work, each field shown only for the
work that uses it: inventing a spell (from a spell chosen first, or a
blank design), learning one from a Lab Text, decoding a text, extracting
vis, fixing an Arcane Connection, a Longevity Ritual, enchanting, binding
and empowering a familiar, taming, moving the lab and the rest. The
terminal plans the same work on its own full screen (InventSpellScreen),
which needs more than one field per row; both build the same SeasonPlan
and refuse it for the same reasons (rules.activities.problems).
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any

from . import books, seasons, spell_forms
from . import enchanted_devices as ed
from . import lab_texts as lt
from . import spells as spl
from .arts import ARTS, FORMS, TECHNIQUES
from .commands import Choice, Choose, Command, Confirm, Form, Refuse, SectionOps, notes
from .familiars import familiar_of
from .form_spec import DialogField, pairs
from .markup import escape, todo
from .models import (
    Book,
    Character,
    Laboratory,
    Saga,
    SeasonPlan,
    Spell,
    SpellDesign,
    next_season,
)
from .rules import activities as season_rules
from .rules import book_seasons as bs
from .rules import enchant_seasons as es
from .rules import experiment as ex
from .rules import familiar_seasons as fs
from .rules import lab_seasons, spell_levels
from .rules import laboratory_seasons as ls

#: The Range/Duration/Target choice for one the app doesn't list.
OTHER = "__other__"
#: The design's Range, Duration and Target, and the steps each lists.
KINDS: tuple[str, ...] = ("range", "duration", "target")
_STANDARD = {
    "range": spell_levels.RANGE_STEPS,
    "duration": spell_levels.DURATION_STEPS,
    "target": spell_levels.TARGET_STEPS,
}
_STANDARD_FIRST = {"range": "Personal", "duration": "Momentary", "target": "Individual"}

#: The desktop's names for the Planning list's buttons.
NOUNS = ("New Spell", "Plan", "Clear")

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
                "select",
                self.activity,
                options=[
                    (season_rules.ACTIVITIES[key].label, key)
                    for key in lab_seasons.LAB_ACTIVITIES
                ],
                allow_blank=True,
                placeholder="(choose the lab work)",
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
            current = getattr(design, kind) if design else _STANDARD_FIRST[kind]
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
        undecoded = self._undecoded()
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
        connections = self._connections()
        devices = self._devices()
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
                options=self._subjects(),
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
        plan = self.existing
        binding = _doing(fs.BIND)
        taming = _doing(lab_seasons.TAMING)
        moving = _doing(ls.MOVE)
        powers = self._powers()
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
        found += [
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
            DialogField(
                "creature",
                "Creature",
                "text",
                plan.title if plan and plan.activity == lab_seasons.TAMING else "",
                placeholder="its name",
                show_if=taming,
            ),
            DialogField(
                "creature_form",
                "Its Form",
                "select",
                (plan.form if plan and plan.activity == lab_seasons.TAMING else "")
                or None,
                options=pairs(FORMS),
                allow_blank=True,
                placeholder="(choose)",
                show_if=taming,
            ),
            DialogField(
                "might",
                "Its Might",
                "optint",
                plan.book_level
                if plan and plan.activity == lab_seasons.TAMING
                else None,
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
                (plan.vis_from if plan and plan.vis_from else "laboratory"),
                options=self._vis_places(),
                show_if=_doing(lab_seasons.EXTRACT),
            ),
            DialogField(
                "vis_from",
                "Vis from",
                "select",
                (plan.vis_from if plan and plan.vis_from else "laboratory"),
                options=self._vis_places(),
                show_if=_vis_from_shown,
            ),
        ]
        return found

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
                "details",
                "Notes",
                "text",
                plan.details if plan else "",
                show_if=_chosen,
            ),
        ]
        return found

    # -- the choices --------------------------------------------------------

    def _vis_places(self) -> list[tuple[str, str]]:
        return [
            ("the laboratory's raw vis", "laboratory"),
            (f"{escape(self.magus.name)}'s raw vis", "character"),
            ("the covenant's vis stores", "covenant"),
        ]

    def _connections(self) -> list[tuple[str, str]]:
        """The lab's Arcane Connections not yet fixed (and the plan's own)."""
        mine = self.existing.connection_id if self.existing else None
        return [
            (escape(c.to), c.id)
            for c in self.lab.arcane_connections
            if not c.fixed or c.id == mine
        ]

    def _devices(self) -> list[tuple[str, str]]:
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

    def _undecoded(self) -> list[Book]:
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

    def _powers(self) -> list[tuple[str, str]]:
        familiar = familiar_of(self.saga, self.magus.id)
        if familiar is None:
            return []
        return [
            (f"{escape(p.name) or '(unnamed)'} (level {p.level})", p.id)
            for p in familiar.bond_powers
        ]

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

    def _work_arts(self, plan: SeasonPlan) -> list[str]:
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
        longevity = activity == lab_seasons.LONGEVITY
        binding = activity == fs.BIND
        taming = activity == lab_seasons.TAMING
        subject = values.get("subject")
        plan = SeasonPlan(
            character_id=self.magus.id,
            year=self.year,
            season=self.season,
            activity=activity,
            lab_id=self.lab.id,
            design=self.design_of(values) if activity == lab_seasons.INVENT else None,
            book_id=(
                values.get("lab_text")
                if activity == lab_seasons.LAB_TEXT
                else values.get("decode")
                if activity == bs.DECODE_TEXT
                else values.get("effect_text")
                if activity in es.EFFECT_ACTIVITIES
                else None
            ),
            similar_spell_id=values.get("similar")
            if activity == lab_seasons.INVENT
            else None,
            days_away=values.get("days_away") or 0,
            focus=bool(values.get("focus")),
            theory_specialty=bool(values.get("specialty")),
            other_modifier=values.get("other_modifier") or 0,
            details=values.get("details") or "",
            vis_from=self._vis_from(activity, values),
            subject_id=(
                subject if longevity and subject and subject != self.magus.id else None
            ),
            vis_art=values.get("longevity_vis") or "" if longevity else "",
            device_id=values.get("device") if activity in es.ACTIVITIES else None,
            effect_id=(
                values.get("effect")
                if activity in es.EFFECT_ACTIVITIES
                else values.get("power")
                if activity == fs.EMPOWER
                else None
            ),
            experimenting=bool(values.get("experimenting"))
            if activity in lab_seasons.EXPERIMENTAL
            else False,
            risk=values.get("risk") or 0,
            research=values.get("research") or "",
            research_kind=values.get("research_kind") or "Minor",
            title=(
                values.get("move_to") or ""
                if activity == ls.MOVE
                else values.get("creature") or ""
                if taming
                else ""
            ),
            book_level=values.get("might") if taming else None,
            by_spell=bool(values.get("by_spell")) if activity == ls.MOVE else False,
            technique=values.get("bind_technique") or "" if binding else "",
            form=(
                values.get("bind_form") or ""
                if binding
                else values.get("creature_form") or ""
                if taming
                else ""
            ),
            golden_cord=values.get("golden_cord") or 0 if binding else 0,
            silver_cord=values.get("silver_cord") or 0 if binding else 0,
            bronze_cord=values.get("bronze_cord") or 0 if binding else 0,
            shape_bonus=values.get("shape") or 0 if activity in es.ACTIVITIES else 0,
            die=values.get("die") if activity in (es.INVESTIGATE, *ls.ROLLED) else None,
            extra_vis=values.get("extra_vis") or 0 if longevity else 0,
            connection_id=values.get("connection")
            if activity == lab_seasons.FIX_AC
            else None,
        )
        if activity in (*es.ACTIVITIES, *fs.ACTIVITIES):
            # The vis is of the work's Technique unless its Form is chosen.
            arts = self._work_arts(plan)
            chosen = values.get("effect_vis")
            plan.vis_art = chosen if chosen in arts else (arts[0] if arts else "")
        return plan

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
        found = season_rules.problems(self.magus, plan, self.saga)
        return found[0] if found else None

    # -- the line above Schedule ------------------------------------------

    def live(self, values: dict[str, Any]) -> str:
        """The design's level, the Lab Total and when the work is done."""
        plan = self.plan_of(values)
        if not plan.activity:
            return "[dim]Choose the lab work.[/]"
        parts: list[str] = []
        if plan.design is not None:
            parts.append(level_text(plan.design))
        _, work = lab_seasons.work(self.saga, self.magus, plan)
        if work is None:
            parts.append("[b]Lab Total[/] [dim]--[/]")
        elif not work.lab_total.lines:
            parts.append("[b]Lab Total[/] [dim]none needed[/]")
            parts.append(self._when_text(plan, work))
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
            parts.append(self._when_text(plan, work))
        problems = season_rules.problems(self.magus, plan, self.saga)
        if problems:
            parts.append(f"[$text-error]{escape(problems[0])}[/]")
        return "\n".join(p for p in parts if p)

    def _when_text(self, plan: SeasonPlan, work: lab_seasons.LabWork) -> str:
        season, year = self.season, self.year
        lab_total = int(work.lab_total.total)
        exposure = "Every lab season also gives 2 xp Exposure in Magic Theory."
        if plan.activity == lab_seasons.EXTRACT:
            return (
                f"Lab Total {lab_total}: {work.vis_gained} pawn(s) of Vim vis "
                f"this season, {season} {year}. {exposure}"
            )
        if plan.activity == lab_seasons.FIX_AC:
            return (
                f"Fixed this season, {season} {year}, for 1 pawn of Vim vis. {exposure}"
            )
        if plan.activity == lab_seasons.LONGEVITY:
            name = work.subject.name if work.subject is not None else "?"
            paid = ", ".join(f"{n} pawn(s) of {a}" for a, n in work.vis_cost.items())
            return (
                f"This season, {season} {year}: aging rolls -{work.longevity} "
                f"for {escape(name)}. Vis: {paid}. {exposure}"
            )
        if plan.activity == ex.STABILIZE:
            return (
                f"This season, {season} {year}: stabilizing the Discovery "
                f"(magnitude {work.research_magnitude}) toward "
                f"{escape(plan.research)}. The Extraordinary Results chart is "
                f"rolled when it's played. {exposure}"
            )
        if plan.activity == bs.DECODE_TEXT:
            return f"{escape(seasons.work_text(work, plan))}. {exposure}"
        if plan.activity == lab_seasons.LAB_TEXT:
            return (
                f"Level {work.level}, Lab Total {lab_total}: learned this season, "
                f"{season} {year}."
            )
        if (
            plan.activity in (*es.ACTIVITIES, *ls.ACTIVITIES)
            or plan.activity == fs.BIND
        ) and plan.activity != es.INSTIL:
            return (
                f"This season, {season} {year}: "
                f"{escape(seasons.work_text(work, plan))}. {exposure}"
            )
        for _ in range(lab_seasons.seasons_left(work)):
            season, year = next_season(season, year)
        needed = lab_seasons.seasons_left(work) + 1
        done = "Invented" if plan.activity == lab_seasons.INVENT else "Instilled"
        return (
            f"Level {work.level}, Lab Total {lab_total}: {work.points_gained} "
            f"points a season, {work.points_before} of {work.level} so far. "
            f"{done} {season} {year} (projected: {needed} "
            f"season{'s' if needed != 1 else ''}). {exposure}"
        )

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
    blank = Choice("A new spell (a blank design)", None, search="new blank")

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

    return Choose(
        f"Start {escape(owner.name)}'s spell from...",
        lambda: [
            blank,
            *spell_forms.spell_choices(saga, {k.spell_id for k in owner.spells_known}),
        ],
        start,
    )


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

    def apply() -> None:
        for each in removed:
            if each in saga.season_plans:
                saga.season_plans.remove(each)

    span = (
        f"{season} {year}"
        if len(removed) == 1
        else f"{season} {year} - {removed[-1].season} {removed[-1].year}"
    )
    return Confirm(
        f"Clear {escape(owner.name)}'s plan for {span} "
        f"({escape(seasons.plan_summary(saga, owner, plan))})?",
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
