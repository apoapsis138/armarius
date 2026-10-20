"""Planning a character's season, independent of how it is drawn: the
Plan Season form (its fields, the plan its values describe, and what
refuses it), a grog's Yearly Update, and the Plan and Clear steps of the
character sheet's This Season and the covenant's Seasons lists
(commands.SectionOps).

Each field of the Plan Season form shows only for the activities that use
it. The form's Virtue and Flaw fields (an Initiation's) are "picker"
fields: the front-end's own chooser when it gives one (`VfPicker`, the
terminal's catalog picker), else the core's searchable list.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .. import book_kinds, catalog, seasons, sourcebooks
from .. import books as bk
from .. import lab_texts as lt
from .. import spells as spl
from ..commands import Command, Confirm, Form, Refuse, SectionOps
from ..form_spec import EMPHASIS_HINT, ChoiceReads, DialogField, attr, read_for_choice
from ..markup import escape
from ..models import (
    Character,
    Covenant,
    GrogYear,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
    XpAllocation,
)
from ..rules import activities as season_rules
from ..rules import (
    apprentice_seasons,
    book_seasons,
    experiment,
    laboratory_seasons,
    supplement_seasons,
)
from ..rules import supplement_work as sw
from ..seasons import plans as season_plans_text
from . import activity as activity_forms
from . import virtue as virtue_forms

#: A front-end's Virtue/Flaw chooser for the form: (saga, character, side)
#: -> the "picker" field's chooser (form_spec.DialogField.picker).
VfPicker = Callable[[Saga, Character, str], Callable[[Any], Any]]

ShowIf = Callable[[dict[str, Any]], bool]


def season_plan_from(
    saga: Saga,
    character: Character,
    values: dict[str, Any],
    existing: SeasonPlan | None = None,
) -> SeasonPlan:
    """The plan the season form's values describe (hidden fields are
    missing from `values`, so everything is read with a default);
    `existing`, the plan being changed, keeps what its Virtue and Flaw
    name when a drop-down chose the same entry."""
    values = _with_instances(values, existing)
    activity = values.get("activity") or ""
    allocations = [
        XpAllocation(values[f"subject_{n}"], values.get(f"points_{n}") or 0)
        for n in range(1, season_rules.MAX_SUBJECTS + 1)
        if values.get(f"subject_{n}")
    ]
    plan = SeasonPlan(
        character_id=character.id,
        year=saga.current_year,
        season=saga.current_season,
        activity=activity,
        allocations=allocations,
        source_quality=values.get("source_quality"),
        months_lost=values.get("months_lost") or 0,
        details=values.get("details") or "",
        correspondence=values.get("correspondence") or "",
        research_kind=values.get("research_kind") or "Minor",
        **{
            # A supplement activity's title and level, unless the activity
            # reads its own.
            "title": _supplement_title(activity, values),
            "book_level": _supplement_level(activity, values),
            **read_for_choice(activity, values, _SEASON_READS),
        },
    )
    for key, value in _supplement_plan_values(character, activity, values).items():
        setattr(plan, key, value)
    return plan


#: The season form's fields that only some activities read, and the plan's
#: fields they set (Strategy, as a table); a plan's field no activity here
#: reads keeps its default.
_SEASON_READS: ChoiceReads = (
    (
        (season_rules.READ,),
        lambda v: {"book_id": v.get("book_id"), "gloss": bool(v.get("gloss"))},
    ),
    (
        (book_seasons.COPY_BOOK, book_seasons.TRANSLATE_BOOK),
        lambda v: {"book_id": v.get("copy_book_id")},
    ),
    ((book_seasons.COPY_TEXTS,), lambda v: {"book_id": v.get("text_id")}),
    ((book_seasons.WRITE_TABLET,), lambda v: {"spell_id": v.get("tablet_spell_id")}),
    (
        (
            book_seasons.WRITE_SUMMA,
            book_seasons.WRITE_TRACTATUS,
            book_seasons.EDIT_FLORILEGIUM,
        ),
        lambda v: {"title": v.get("title") or ""},
    ),
    ((laboratory_seasons.NEW,), lambda v: {"title": v.get("lab_name") or ""}),
    ((book_seasons.WRITE_SUMMA,), lambda v: {"book_level": v.get("book_level")}),
    (
        (
            book_seasons.WRITE_SUMMA,
            book_seasons.WRITE_TRACTATUS,
            book_seasons.TRANSLATE_BOOK,
        ),
        lambda v: {"language": v.get("language") or ""},
    ),
    (
        (book_seasons.EDIT_FLORILEGIUM,),
        lambda v: {"florilegium_subject": v.get("florilegium_subject") or ""},
    ),
    ((book_seasons.COPY_BOOK,), lambda v: {"quick": bool(v.get("quick"))}),
    (
        (
            book_seasons.TEACH_ABBREVIATIONS,
            apprentice_seasons.OPEN_ARTS,
            apprentice_seasons.TEACH_VIRTUE,
            season_rules.OPEN_TRADITION,
        ),
        lambda v: {"subject_id": v.get("student_id")},
    ),
    ((experiment.INTEGRATE,), lambda v: {"research": v.get("research") or ""}),
    (
        (apprentice_seasons.TEACH_VIRTUE,),
        lambda v: {"effect_id": v.get("virtue_id")},
    ),
    (
        ("undergo_initiation",),
        lambda v: {"effect_id": _vf_id(v.get("mystery_virtue"))},
    ),
    (
        (
            season_rules.TAUGHT,
            season_rules.TRAINED,
            laboratory_seasons.ASSIST,
            "undergo_initiation",
            "record_lectures",
        ),
        lambda v: {"teacher_id": v.get("teacher_id")},
    ),
    (
        (season_rules.VIS_STUDY,),
        lambda v: {"vis_from": v.get("vis_from") or "character"},
    ),
    (
        (
            season_rules.VIS_STUDY,
            apprentice_seasons.SEARCH,
            experiment.INTEGRATE,
            "search_lacuna",
        ),
        lambda v: {"die": v.get("die")},
    ),
)


#: The supplement activities that give experience.
_SUPPLEMENT_XP: tuple[str, ...] = tuple(
    a.key for a in supplement_seasons.ACTIVITIES if not a.no_xp
)


_LP_ACTIVITIES = (
    "working_season",
    "workshop_production",
    "make_excellent_item",
    "tournament",
    "apothecary",
    "create_art",
)


_CHARACTERISTICS = (
    "intelligence",
    "perception",
    "strength",
    "stamina",
    "presence",
    "communication",
    "dexterity",
    "quickness",
)


_THEMES = (
    "Loyalty",
    "Calmness",
    "Kindness",
    "Bravery",
    "Wisdom",
    "Strength",
    "Justice",
)


#: Plan field -> (dialog key, activities) for the supplements' extra values.
_LEVEL_KEYS = {
    "craft_level": ("workshop_production", "make_excellent_item"),
    "might": ("tame_animal",),
    "target_level": ("pilgrimage",),
    "product_level": ("produce_remedies",),
    "score_written": ("inspeximus",),
}


_BONUS_KEYS = {
    "workshop_bonus": ("workshop_production", "make_excellent_item", "create_art"),
    "venture_lp": ("merchant_venture",),
    "elements": ("pilgrimage",),
    "script_bonus": ("undergo_initiation",),
}


_TITLE_KEYS = {
    "work_name": (
        "pilgrimage",
        "tame_animal",
        "create_art",
        "research_formula",
        "make_excellent_item",
        "record_lectures",
    ),
    "improve": ("improve_workshop",),
    "exam": ("attend_university",),
    "theme": ("care_of_souls",),
    "lore": ("undergo_initiation",),
}


def _pick(activity: str, values: dict[str, Any], keys: dict[str, tuple[str, ...]]):
    for key, activities in keys.items():
        if activity in activities:
            return values.get(key)
    return None


def _supplement_level(activity: str, values: dict[str, Any]) -> int | None:
    value = _pick(activity, values, _LEVEL_KEYS)
    if isinstance(value, str):
        return int(value) if value.isdigit() else None
    return value


def _supplement_title(activity: str, values: dict[str, Any]) -> str:
    return _pick(activity, values, _TITLE_KEYS) or ""


def _supplement_plan_values(
    character: Character, activity: str, values: dict[str, Any]
) -> dict[str, Any]:
    """The rest of a supplement season's plan (decision 38)."""
    found: dict[str, Any] = {
        "other_modifier": _pick(activity, values, _BONUS_KEYS) or 0,
        "characteristic": (
            values.get("characteristic") or "" if activity in _LP_ACTIVITIES else ""
        ),
    }
    if activity == "workshop_production":
        found["quick"] = bool(values.get("manual"))
        found["experimenting"] = bool(values.get("exert"))
    if activity == "produce_remedies":
        found["extra_vis"] = values.get("doses") or 1
    if activity == "undergo_initiation":
        virtue = values.get("mystery_virtue")
        found["effect_params"] = dict(virtue.params) if virtue else {}
        kind = values.get("ordeal_kind") or ""
        found["ordeal_kind"] = kind
        flaw = (
            values.get("ordeal_flaw") if kind in (sw.GAIN_FLAW, sw.RAISE_FLAW) else None
        )
        found["device_id"] = flaw.vf_id if flaw else None
        found["ordeal_params"] = dict(flaw.params) if flaw else {}
        lost = _own_vf(
            character,
            values.get("ordeal_lost_virtue")
            if kind == sw.LOSE_VIRTUE
            else values.get("ordeal_raised_flaw")
            if kind == sw.RAISE_FLAW
            else None,
        )
        found["ordeal_lost_id"] = lost.vf_id if lost else None
        found["ordeal_lost_params"] = dict(lost.params) if lost else {}
    if activity == "inspeximus":
        found["book_id"] = values.get("summa_id")
    return found


def _vf_id(instance: VirtueFlawInstance | None) -> str | None:
    return instance.vf_id if instance else None


def _vf_field(
    key: str,
    label: str,
    saga: Saga,
    character: Character,
    side: str,
    value: VirtueFlawInstance | None,
    show_if: ShowIf,
    vf_picker: VfPicker | None,
) -> DialogField:
    """A field choosing a Virtue or Flaw (`side`) for `character`, asking
    for anything the entry names (Delete clears it): the front-end's own
    catalog picker when it gives one, else the core's searchable list
    (virtue_forms.choose_virtue_flaw)."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()

    def display(instance: VirtueFlawInstance) -> str:
        definition = by_id.get(instance.vf_id)
        tier = f" ({definition.tier})" if definition else ""
        return catalog.describe_virtue_flaw(instance, by_id) + tier

    return DialogField(
        key,
        label,
        "picker",
        value,
        allow_blank=True,
        placeholder=f"(choose the {side}...)",
        picker=vf_picker(saga, character, side) if vf_picker is not None else None,
        choose=lambda _current: virtue_forms.choose_virtue_flaw(saga, character, side),
        display=display,
        show_if=show_if,
    )


def _with_instances(
    values: dict[str, Any], existing: SeasonPlan | None
) -> dict[str, Any]:
    """`values` with the Initiation's Virtue and Flaw as instances."""
    kept = {
        "mystery_virtue": VirtueFlawInstance(
            existing.effect_id, dict(existing.effect_params)
        )
        if existing and existing.effect_id
        else None,
        "ordeal_flaw": VirtueFlawInstance(
            existing.device_id, dict(existing.ordeal_params)
        )
        if existing and existing.device_id
        else None,
    }
    found = dict(values)
    for key, plan_own in kept.items():
        if key in found:
            found[key] = _vf_of(found[key], plan_own)
    return found


def _vf_of(value: Any, kept: VirtueFlawInstance | None) -> VirtueFlawInstance | None:
    """A Virtue/Flaw field's value as an instance: a picker's is one, a
    drop-down's is the entry's id (keeping what `kept`, the plan's own,
    names when it is the same entry)."""
    if not isinstance(value, str):
        return value
    if not value:
        return None
    if kept is not None and kept.vf_id == value:
        return kept
    return VirtueFlawInstance(value, {})


def _own_vf(character: Character, index: str | None) -> VirtueFlawInstance | None:
    """The character's Virtue or Flaw an "own_vf_options" choice names."""
    if (
        index is None
        or not index.isdigit()
        or int(index) >= len(character.virtues_flaws)
    ):
        return None
    return character.virtues_flaws[int(index)]


def _own_vf_options(
    character: Character, side: str, tiers: tuple[str, ...]
) -> list[tuple[str, str]]:
    """The character's own Virtues or Flaws (`side`) of `tiers`, as select
    options keyed by their place in the list."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    return [
        (escape(f"{catalog.describe_virtue_flaw(vf, by_id)} ({entry.tier})"), str(i))
        for i, vf in enumerate(character.virtues_flaws)
        if (entry := by_id.get(vf.vf_id)) is not None
        and entry.side == side
        and entry.tier in tiers
    ]


def _own_vf_value(character: Character, vf_id: str | None, params: dict) -> str | None:
    """The select value of the character's Virtue or Flaw `vf_id`."""
    wanted = VirtueFlawInstance(vf_id or "", dict(params))
    return next(
        (str(i) for i, vf in enumerate(character.virtues_flaws) if vf == wanted), None
    )


def _ordeal_is(
    activity_is: Callable[..., Callable[[dict[str, Any]], bool]], *kinds: str
) -> Callable[[dict[str, Any]], bool]:
    initiation = activity_is("undergo_initiation")
    return lambda values: initiation(values) and values.get("ordeal_kind") in kinds


#: What makes a field's show_if from activity keys (`_activity_is`).
ActivityIs = Callable[..., Callable[[dict[str, Any]], bool]]


def _supplement_total_fields(
    plan: SeasonPlan | None, activity_is: ActivityIs
) -> list[DialogField]:
    """What a supplement season's total uses or aims at: the Characteristic,
    the level of the craft, the animal, the pilgrimage or the remedy, and
    the remedy's doses."""
    level = plan.book_level if plan else None
    return [
        DialogField(
            "characteristic",
            "Characteristic",
            "select",
            (plan.characteristic if plan else "") or None,
            options=[(c.title(), c) for c in _CHARACTERISTICS],
            allow_blank=True,
            placeholder="(the usual one)",
            show_if=activity_is(*_LP_ACTIVITIES),
        ),
        DialogField(
            "craft_level",
            "Craft Level",
            "optint",
            level,
            show_if=activity_is(*_LEVEL_KEYS["craft_level"]),
            hint="Blank: 6 (15 for an excellent item).",
        ),
        DialogField(
            "might",
            "Animal's Might",
            "optint",
            level,
            show_if=activity_is("tame_animal"),
        ),
        DialogField(
            "target_level",
            "Target Level",
            "select",
            str(level) if level in (18, 30) else "18",
            options=[("18 (minor pilgrimage)", "18"), ("30 (major pilgrimage)", "30")],
            show_if=activity_is("pilgrimage"),
        ),
        DialogField(
            "product_level",
            "Product level",
            "optint",
            level,
            show_if=activity_is("produce_remedies"),
        ),
        DialogField(
            "doses",
            "Doses",
            "int",
            (plan.extra_vis if plan else 0) or 1,
            show_if=activity_is("produce_remedies"),
        ),
    ]


def _inspeximus_fields(
    saga: Saga,
    character: Character,
    plan: SeasonPlan | None,
    activity_is: ActivityIs,
) -> list[DialogField]:
    """An Inspeximus: the summa of the character's own it confirms, and
    their score when they wrote it."""
    return [
        DialogField(
            "score_written",
            "Score when written",
            "optint",
            plan.book_level if plan else None,
            show_if=activity_is("inspeximus"),
            hint="Blank: twice the summa's Level.",
        ),
        DialogField(
            "summa_id",
            "Summa",
            "select",
            plan.book_id if plan else None,
            options=[
                (escape(b.name), b.id)
                for b in saga.books
                if b.type in ("Art Summa", "Ability Summa")
                and b.author == character.name
            ],
            allow_blank=True,
            show_if=activity_is("inspeximus"),
        ),
    ]


def _supplement_bonus_fields(
    plan: SeasonPlan | None, activity_is: ActivityIs
) -> list[DialogField]:
    """What a supplement season adds to its total: a workshop's other
    bonuses, a venture's Labor Points, a pilgrimage's elements overcome and
    an Initiation Script's bonus."""
    bonus = plan.other_modifier if plan else 0
    return [
        DialogField(
            "workshop_bonus",
            "Other bonuses",
            "int",
            bonus,
            show_if=activity_is(*_BONUS_KEYS["workshop_bonus"]),
            hint="Assistants, a craft manual, a specialty...",
        ),
        DialogField(
            "venture_lp",
            "Labor Points gained",
            "int",
            bonus,
            show_if=activity_is("merchant_venture"),
        ),
        DialogField(
            "elements",
            "Elements overcome",
            "int",
            bonus,
            show_if=activity_is("pilgrimage"),
            hint="+3 a season is added for you; add the rest (+3 to +12 each).",
        ),
        DialogField(
            "script_bonus",
            "Script bonus",
            "int",
            bonus,
            show_if=activity_is("undergo_initiation"),
        ),
    ]


def _supplement_title_fields(
    plan: SeasonPlan | None, activity_is: ActivityIs
) -> list[DialogField]:
    """What a supplement season names: the work, the workshop's
    improvement, the exam, the sermon's theme or the Mystagogue's Lore."""
    title = plan.title if plan else ""
    return [
        DialogField(
            "work_name",
            "Name",
            "text",
            title,
            placeholder="the pilgrimage, animal, work, formula or item",
            show_if=activity_is(*_TITLE_KEYS["work_name"]),
        ),
        DialogField(
            "improve",
            "Improve",
            "select",
            title or None,
            options=[("Innovation", "innovation"), ("Raw Materials", "raw materials")],
            allow_blank=True,
            show_if=activity_is("improve_workshop"),
        ),
        DialogField(
            "exam",
            "Exam",
            "select",
            title or None,
            options=[(e.title(), e) for e in ("baccalaureus", "magister", "doctor")],
            allow_blank=True,
            placeholder="(none)",
            show_if=activity_is("attend_university"),
        ),
        DialogField(
            "theme",
            "Sermon theme",
            "select",
            title or None,
            options=[(t, t) for t in _THEMES],
            allow_blank=True,
            show_if=activity_is("care_of_souls"),
        ),
        DialogField(
            "lore",
            "Mystagogue's Lore",
            "text",
            title,
            placeholder="e.g. Mercere Lore",
            show_if=activity_is("undergo_initiation"),
        ),
    ]


def _initiation_fields(
    saga: Saga,
    character: Character,
    plan: SeasonPlan | None,
    activity_is: ActivityIs,
    vf_picker: VfPicker | None,
) -> list[DialogField]:
    """An Initiation: the Virtue initiated, and the kind of Ordeal."""
    return [
        _vf_field(
            "mystery_virtue",
            "Virtue initiated",
            saga,
            character,
            "Virtue",
            VirtueFlawInstance(plan.effect_id, dict(plan.effect_params))
            if plan and plan.effect_id
            else None,
            show_if=activity_is("undergo_initiation"),
            vf_picker=vf_picker,
        ),
        DialogField(
            "ordeal_kind",
            "Ordeal",
            "select",
            (sw.ordeal_kind(plan) if plan else "") or None,
            options=[(label, kind) for kind, label in sw.ORDEAL_KINDS.items()],
            allow_blank=True,
            placeholder="(none)",
            show_if=activity_is("undergo_initiation"),
        ),
    ]


def _ordeal_fields(
    saga: Saga,
    character: Character,
    plan: SeasonPlan | None,
    activity_is: ActivityIs,
    vf_picker: VfPicker | None,
) -> list[DialogField]:
    """An Initiation's Ordeal: the Flaw it gains or raises, or the Virtue
    it loses."""
    lost = (
        _own_vf_value(character, plan.ordeal_lost_id, plan.ordeal_lost_params)
        if plan
        else None
    )
    return [
        _vf_field(
            "ordeal_flaw",
            "Flaw gained",
            saga,
            character,
            "Flaw",
            VirtueFlawInstance(plan.device_id, dict(plan.ordeal_params))
            if plan and plan.device_id
            else None,
            show_if=_ordeal_is(activity_is, sw.GAIN_FLAW, sw.RAISE_FLAW),
            vf_picker=vf_picker,
        ),
        DialogField(
            "ordeal_lost_virtue",
            "Virtue lost",
            "select",
            lost,
            options=_own_vf_options(character, "Virtue", ("Minor", "Major")),
            allow_blank=True,
            placeholder="(choose one of their Virtues)",
            show_if=_ordeal_is(activity_is, sw.LOSE_VIRTUE),
        ),
        DialogField(
            "ordeal_raised_flaw",
            "Minor Flaw raised",
            "select",
            lost,
            options=_own_vf_options(character, "Flaw", ("Minor",)),
            allow_blank=True,
            placeholder="(choose one of their Minor Flaws)",
            show_if=_ordeal_is(activity_is, sw.RAISE_FLAW),
        ),
    ]


def _workshop_production_fields(
    plan: SeasonPlan | None, activity_is: ActivityIs
) -> list[DialogField]:
    """Workshop production's choices: writing a craft manual, and exerting."""
    return [
        DialogField(
            "manual",
            "Write a craft manual",
            "check",
            bool(plan and plan.quick),
            show_if=activity_is("workshop_production"),
            hint="Costs 1 Labor Point; needs Artes Liberales 1.",
        ),
        DialogField(
            "exert",
            "Exert",
            "check",
            bool(plan and plan.experimenting),
            show_if=activity_is("workshop_production"),
            hint="+ a simple die to the Workshop Total, and an Aging roll.",
        ),
    ]


def _supplement_fields(
    saga: Saga,
    character: Character,
    existing: SeasonPlan | None,
    activity_is: ActivityIs,
    vf_picker: VfPicker | None = None,
) -> list[DialogField]:
    """The season form's fields for the supplement sub-systems."""
    plan = existing
    return [
        *_supplement_total_fields(plan, activity_is),
        *_inspeximus_fields(saga, character, plan, activity_is),
        *_supplement_bonus_fields(plan, activity_is),
        *_supplement_title_fields(plan, activity_is),
        *_initiation_fields(saga, character, plan, activity_is, vf_picker),
        *_ordeal_fields(saga, character, plan, activity_is, vf_picker),
        *_workshop_production_fields(plan, activity_is),
    ]


def _activity_is(*keys: str) -> ShowIf:
    """A field's show_if: shown while the Activity is one of `keys`."""
    return lambda values: values.get("activity") in keys


def _book_options(saga: Saga, character: Character) -> list[tuple[str, str]]:
    return [
        (escape(seasons.book_label(b)), b.id)
        for b in bk.studyable_books(saga, character)
    ]


def study_fields(
    saga: Saga, character: Character, existing: SeasonPlan | None
) -> list[DialogField]:
    """The Activity, and the Source Quality, book or teacher it studies from."""
    books = sourcebooks.saga_books(saga)
    gloss = attr(existing, "gloss", False)
    # Glossing is Covenants': off the form with the book out of play, unless
    # the plan already glosses.
    hidden = (
        set()
        if gloss or sourcebooks.in_play(book_kinds.GLOSS.book, books)
        else {"gloss"}
    )
    fields = [
        DialogField(
            "activity",
            "Activity",
            "picker",
            attr(existing, "activity", None),
            required=True,
            placeholder="(choose the activity...)",
            choose=lambda current: activity_forms.choose_activity(
                saga, character, current
            ),
            display=activity_forms.activity_label,
            hint="Filter by Type or Book, or type to search. The line above "
            "Save shows what the season will give.",
        ),
        DialogField(
            "source_quality",
            "Source Quality",
            "optint",
            attr(existing, "source_quality", None),
            show_if=_activity_is(
                season_rules.PRACTICE, season_rules.ADVENTURE, *_SUPPLEMENT_XP
            ),
            hint=(
                "Practice: blank for 4 (5 for a spell's Mastery). Adventure: "
                "the storyguide's 5 to 10. Others: see the line above Save."
            ),
        ),
        DialogField(
            "book_id",
            "Book",
            "select",
            attr(existing, "book_id", None),
            options=_book_options(saga, character),
            allow_blank=True,
            show_if=_activity_is(season_rules.READ),
            hint="The covenant's library and the character's own books.",
        ),
        DialogField(
            "gloss",
            "Gloss it (+1 Quality)",
            "check",
            bool(gloss),
            hint="A reader at least half as skilled as its Level, with better "
            "Communication than its author, glosses it while reading: +1, once.",
            show_if=_activity_is(season_rules.READ),
        ),
        DialogField(
            "teacher_id",
            "Teacher / master",
            "select",
            attr(existing, "teacher_id", None),
            options=[
                (escape(c.name), c.id)
                for c in saga.characters
                if c.id != character.id and c.type != "grog"
            ]
            + [
                (escape(c.name), c.id)
                for c in saga.characters
                if c.id != character.id and c.type == "grog"
            ],
            allow_blank=True,
            show_if=_activity_is(
                season_rules.TAUGHT,
                season_rules.TRAINED,
                laboratory_seasons.ASSIST,
                "undergo_initiation",
                "record_lectures",
            ),
            hint="A teacher plans Teach for the same season; the magus you "
            "assist plans lab work. An Initiation's Mystagogue: none for a "
            "self-initiation.",
        ),
    ]
    return [f for f in fields if f.key not in hidden]


def _subject_fields(
    saga: Saga, character: Character, existing: SeasonPlan | None
) -> list[DialogField]:
    """Where the season's experience goes: one subject for most activities,
    two for Exposure and Adventure, more for Adventure, each with its share of
    an Adventure's Source Quality."""
    options = seasons.subject_options(saga, character)
    shares = existing.allocations if existing else []
    fields: list[DialogField] = []
    for n in range(1, season_rules.MAX_SUBJECTS + 1):
        allocation = shares[n - 1] if len(shares) >= n else None
        if n == 1:
            shown = _activity_is(
                season_rules.EXPOSURE,
                season_rules.PRACTICE,
                season_rules.ADVENTURE,
                season_rules.TAUGHT,
                season_rules.TEACH,
                season_rules.TRAINED,
                season_rules.VIS_STUDY,
                book_seasons.WRITE_SUMMA,
                book_seasons.WRITE_TRACTATUS,
                *_SUPPLEMENT_XP,
                *season_rules.TRADITION_ACTIVITIES,
            )
        elif n == 2:
            shown = _activity_is(season_rules.EXPOSURE, season_rules.ADVENTURE)
        else:
            shown = _activity_is(season_rules.ADVENTURE)
        fields.append(
            DialogField(
                f"subject_{n}",
                "Experience in" if n == 1 else f"...and in ({n})",
                "select",
                allocation.subject if allocation else None,
                options=options,
                allow_blank=True,
                show_if=shown,
                hint=(
                    "What the season's experience goes into (Teach: Teaching "
                    "or the language used)."
                    if n == 1
                    else "Exposure: 1 xp each in two. Adventure: at most 5 "
                    "points of Source Quality to each."
                    if n == 2
                    else ""
                ),
            )
        )
        fields.append(
            DialogField(
                f"points_{n}",
                f"Source Quality to ({n})",
                "optint",
                allocation.points if allocation and allocation.points else None,
                show_if=_activity_is(season_rules.ADVENTURE),
            )
        )
    return fields


def _book_work_fields(
    saga: Saga, character: Character, existing: SeasonPlan | None
) -> list[DialogField]:
    """Writing, copying and translating books, and copying Lab Texts."""
    return [
        DialogField(
            "title",
            "Title",
            "text",
            attr(existing, "title", ""),
            placeholder="blank: named for its subject",
            show_if=_activity_is(
                book_seasons.WRITE_SUMMA,
                book_seasons.WRITE_TRACTATUS,
                book_seasons.EDIT_FLORILEGIUM,
            ),
        ),
        DialogField(
            "book_level",
            "Summa Level (blank: the most)",
            "optint",
            attr(existing, "book_level", None),
            show_if=_activity_is(book_seasons.WRITE_SUMMA),
            hint="Each Level below the most adds Quality (+1, +3 for an Ability).",
        ),
        DialogField(
            "language",
            "Language",
            "text",
            attr(existing, "language", "") or "Latin",
            show_if=_activity_is(
                book_seasons.WRITE_SUMMA,
                book_seasons.WRITE_TRACTATUS,
                book_seasons.TRANSLATE_BOOK,
            ),
            hint="Written in, or translated into.",
        ),
        DialogField(
            "copy_book_id",
            "Book",
            "select",
            attr(existing, "book_id", None),
            options=_book_options(saga, character),
            allow_blank=True,
            show_if=_activity_is(book_seasons.COPY_BOOK, book_seasons.TRANSLATE_BOOK),
        ),
        DialogField(
            "quick",
            "Quick copy (x3, Quality -1)",
            "check",
            attr(existing, "quick", False),
            show_if=_activity_is(book_seasons.COPY_BOOK),
        ),
        DialogField(
            "text_id",
            "Lab Text",
            "select",
            attr(existing, "book_id", None),
            # Every text he can get at: one he can't read yet says so, and
            # the season refuses it with the reason.
            options=[
                (escape(b.name + lt.cant_read_tag(saga, character, b)), b.id)
                for b in saga.books
                if b.type in ("Lab Text", "Casting Tablet")
                and bk.can_read(saga, character, b)
            ],
            allow_blank=True,
            show_if=_activity_is(book_seasons.COPY_TEXTS),
        ),
        DialogField(
            "florilegium_subject",
            "Florilegium subject",
            "select",
            attr(existing, "florilegium_subject", "") or None,
            options=_florilegium_subjects(saga, character),
            allow_blank=True,
            hint="The tractatus on it you can get at, not bound in a codex, are "
            "bound best first.",
            show_if=_activity_is(book_seasons.EDIT_FLORILEGIUM),
        ),
        DialogField(
            "tablet_spell_id",
            "Spell (mastered)",
            "select",
            attr(existing, "spell_id", None),
            options=_mastered_spells(saga, character),
            allow_blank=True,
            show_if=_activity_is(book_seasons.WRITE_TABLET),
        ),
    ]


def _new_lab_fields(
    character: Character, existing: SeasonPlan | None
) -> list[DialogField]:
    """Setting up a new laboratory: its name."""
    named = existing is not None and existing.activity == laboratory_seasons.NEW
    return [
        DialogField(
            "lab_name",
            "Laboratory's name",
            "text",
            existing.title if named and existing else "",
            placeholder=f"blank: {character.name}'s laboratory",
            show_if=_activity_is(laboratory_seasons.NEW),
            hint="Made in the magus's covenant when the season is applied.",
        )
    ]


def _florilegium_subjects(saga: Saga, character: Character) -> list[tuple[str, str]]:
    """The subjects the character can get at unbound tractatus on."""
    names = season_plans_text.spell_names(saga, character)
    found: dict[str, int] = {}
    for book in saga.books:
        subject = book_seasons.book_subject(book)
        if (
            book.type == "Tractatus"
            and subject
            and bk.codex_of(saga, book) is None
            and bk.can_read(saga, character, book)
        ):
            found[subject] = found.get(subject, 0) + 1
    return [
        (escape(f"{season_rules.subject_label(s, names)} ({n} tractatus)"), s)
        for s, n in found.items()
    ]


def _mastered_spells(saga: Saga, character: Character) -> list[tuple[str, str]]:
    """The spells the character has mastered, for writing Casting Tablets."""
    found = []
    for known in character.spells_known:
        spell = spl.find_spell(saga, known.spell_id)
        if spell is not None and known.mastery_score >= 1:
            found.append((escape(f"{spell.name} ({spl.shorthand(spell)})"), spell.id))
    return found


def _student_and_research_fields(
    saga: Saga, character: Character, existing: SeasonPlan | None
) -> list[DialogField]:
    """The student taught, and the goal of a research season."""
    return [
        DialogField(
            "student_id",
            "Student",
            "select",
            attr(existing, "subject_id", None),
            options=[
                (escape(c.name), c.id)
                for c in saga.characters
                if c.id != character.id and c.type != "grog"
            ],
            allow_blank=True,
            show_if=_activity_is(
                book_seasons.TEACH_ABBREVIATIONS,
                apprentice_seasons.OPEN_ARTS,
                apprentice_seasons.TEACH_VIRTUE,
                season_rules.OPEN_TRADITION,
            ),
        ),
        DialogField(
            "research",
            "Research goal",
            "text",
            attr(existing, "research", ""),
            show_if=_activity_is(experiment.INTEGRATE),
        ),
        DialogField(
            "research_kind",
            "Breakthrough",
            "select",
            attr(existing, "research_kind", "") or "Minor",
            options=[(k, k) for k in experiment.KINDS],
            show_if=_activity_is(experiment.INTEGRATE),
        ),
    ]


def _correspondence_fields(
    saga: Saga, character: Character, existing: SeasonPlan | None
) -> list[DialogField]:
    """Useful correspondence alongside the season (Covenants in play): the
    subject it is on, +1 xp in it."""
    if not sourcebooks.in_play("Covenants", sourcebooks.saga_books(saga)):
        return []
    return [
        DialogField(
            "correspondence",
            "Correspondence on",
            "select",
            attr(existing, "correspondence", "") or None,
            options=seasons.subject_options(saga, character),
            allow_blank=True,
            placeholder="(none this season)",
            hint="Useful correspondence on a theme of your research or reading, "
            "with at least one letter received: +1 xp in it (one a season).",
        )
    ]


def _closing_fields(
    character: Character, existing: SeasonPlan | None
) -> list[DialogField]:
    """The Virtue taught, where vis comes from, the die, months lost and notes."""
    return [
        DialogField(
            "virtue_id",
            "Hermetic Virtue",
            "select",
            attr(existing, "effect_id", None),
            options=apprentice_seasons.teachable_virtues(character),
            allow_blank=True,
            show_if=_activity_is(apprentice_seasons.TEACH_VIRTUE),
        ),
        DialogField(
            "vis_from",
            "Vis from",
            "select",
            attr(existing, "vis_from", "") or "character",
            options=[
                ("Their own raw vis", "character"),
                ("Their laboratory's raw vis", "laboratory"),
                ("Their covenant's vis stores", "covenant"),
            ],
            show_if=_activity_is(season_rules.VIS_STUDY),
        ),
        DialogField(
            "die",
            "Stress die (blank: rolled)",
            "optint",
            attr(existing, "die", None),
            show_if=_activity_is(
                season_rules.VIS_STUDY,
                apprentice_seasons.SEARCH,
                experiment.INTEGRATE,
                "search_lacuna",
            ),
            hint="Leave blank for the app to roll it when the season is applied.",
        ),
        DialogField(
            "months_lost",
            "Months lost (0-3)",
            "int",
            attr(existing, "months_lost", 0),
            show_if=_activity_is(
                season_rules.EXPOSURE,
                season_rules.PRACTICE,
                season_rules.READ,
                season_rules.TAUGHT,
                season_rules.TRAINED,
                season_rules.VIS_STUDY,
            ),
            hint="Each full month lost to distractions cuts the total by a third.",
        ),
        DialogField(
            "details",
            "Notes",
            "area",
            attr(existing, "details", ""),
            hint=EMPHASIS_HINT,
        ),
    ]


def season_plan_fields(
    saga: Saga,
    character: Character,
    existing: SeasonPlan | None,
    *,
    vf_picker: VfPicker | None = None,
) -> list[DialogField]:
    """The Plan Season form: the activity, what its experience goes into,
    and notes. Each field shows only for the activities that use it."""
    return [
        *study_fields(saga, character, existing),
        *_subject_fields(saga, character, existing),
        *_book_work_fields(saga, character, existing),
        *_new_lab_fields(character, existing),
        *_student_and_research_fields(saga, character, existing),
        *_supplement_fields(saga, character, existing, _activity_is, vf_picker),
        *_correspondence_fields(saga, character, existing),
        *_closing_fields(character, existing),
    ]


def season_plan_title(saga: Saga, character: Character) -> str:
    """ "Plan Tiberius's Season (Spring 1220)" (markup)."""
    return (
        f"Plan {escape(character.name)}'s Season "
        f"({saga.current_season} {saga.current_year})"
    )


def season_plan_problem(
    saga: Saga,
    character: Character,
    values: dict[str, Any],
    existing: SeasonPlan | None = None,
) -> str | None:
    """Why the season the form describes can't be planned, or None."""
    plan = season_plan_from(saga, character, values, existing)
    found = season_rules.problems(character, plan, saga)
    if not found and plan.activity == season_rules.OTHER and not plan.details:
        return "Say in Notes what the season is spent on."
    return found[0] if found else None


def season_plan_live(
    saga: Saga,
    character: Character,
    values: dict[str, Any],
    existing: SeasonPlan | None = None,
) -> str:
    """The line above Save: what the season will give, worked out as the
    form is filled in."""
    return seasons.live_text(
        saga, character, season_plan_from(saga, character, values, existing)
    )


# -- a grog's Yearly Update ----------------------------------------------------


def grog_year_title(character: Character) -> str:
    return f"{escape(character.name)}'s Yearly Update"


def grog_year_fields(
    character: Character, existing: GrogYear | None
) -> list[DialogField]:
    """A grog's yearly update (Grogs Ch. 5): what the training,
    practice and exposure go into, and the year's story awards."""
    names = sorted({a.name for a in character.abilities})
    options = [(escape(n), n) for n in names]

    def ability(key: str, label: str, hint: str = "") -> DialogField:
        value = getattr(existing, key) if existing else ""
        pairs = options + (
            [(escape(value), value)] if value and value not in names else []
        )
        return DialogField(
            key,
            label,
            "select",
            value or None,
            options=pairs,
            allow_blank=True,
            hint=hint,
        )

    return [
        ability(
            "vocational",
            "Vocational training",
            "Usually Single Weapon, from the drill sergeant.",
        ),
        DialogField(
            "vocational_xp",
            "Vocational xp",
            "int",
            existing.vocational_xp if existing else 7,
            hint="7, or the teacher's Source Quality if known.",
        ),
        ability("practice", "Practice (4 xp)"),
        ability("exposure", "Exposure (2 xp)"),
        ability("exposure_2", "Exposure (2 xp), second"),
        DialogField(
            "story_awards",
            "Story awards this year",
            "int",
            existing.story_awards if existing else 0,
            hint="Each takes a season: exposure, vocational, practice, exposure.",
        ),
    ]


def grog_year_from(values: dict[str, Any]) -> GrogYear:
    return GrogYear(
        vocational=values.get("vocational") or "",
        vocational_xp=values.get("vocational_xp") or 0,
        practice=values.get("practice") or "",
        exposure=values.get("exposure") or "",
        exposure_2=values.get("exposure_2") or "",
        story_awards=values.get("story_awards") or 0,
    )


def grog_year_form(character: Character) -> Form:
    """Set up a grog's Yearly Update."""

    def apply(values: dict[str, Any]) -> None:
        character.grog_year = grog_year_from(values)

    return Form(
        grog_year_title(character),
        lambda: grog_year_fields(character, character.grog_year),
        apply,
    )


# -- the steps: plan a season, clear it -----------------------------------------


def plan_season(
    saga: Saga, character: Character, *, vf_picker: VfPicker | None = None
) -> Form:
    """Plan `character`'s current season, or change the plan; a grog's is
    the Yearly Update instead."""
    if not season_rules.is_planned(character):
        return grog_year_form(character)
    existing = seasons.plan_for(saga, character)

    def apply(values: dict[str, Any]) -> None:
        seasons.set_plan(saga, season_plan_from(saga, character, values, existing))

    return Form(
        season_plan_title(saga, character),
        lambda: season_plan_fields(saga, character, existing, vf_picker=vf_picker),
        apply,
        validate=lambda values: season_plan_problem(saga, character, values, existing),
        live=lambda values: season_plan_live(saga, character, values, existing),
    )


def clear_season(saga: Saga, character: Character) -> Confirm | Refuse:
    """Drop `character`'s plan for the current season, after confirming."""
    plan = seasons.plan_for(saga, character)
    if plan is None:
        return Refuse(
            "Clear the Season",
            f"Nothing is planned for {escape(character.name)} this season.",
        )
    return Confirm(
        f"Clear {escape(character.name)}'s plan "
        f"({escape(seasons.plan_summary(saga, character, plan))})?",
        lambda: seasons.clear_plan(saga, character),
        yes_label="Clear",
    )


#: The desktop's names for a This Season section's three buttons.
PLAN_NOUNS = ("Plan", "Edit", "Clear")
GROG_NOUNS = ("Yearly Update", "Edit", "Clear")


def season_nouns(character: Character) -> tuple[str, str, str]:
    """What a This Season section's Add, Edit and Delete are called:
    Plan, Edit and Clear, or a grog's Yearly Update."""
    return PLAN_NOUNS if season_rules.is_planned(character) else GROG_NOUNS


def character_season_ops(saga: Saga, character: Character) -> SectionOps:
    """The character sheet's This Season: Plan while nothing is planned,
    then Edit and Clear for the plan (its one row). A grog's Plan is the
    Yearly Update, with nothing to clear."""
    if not season_rules.is_planned(character):
        return SectionOps(add=lambda: grog_year_form(character))

    def rows() -> list[str]:
        plan = seasons.plan_for(saga, character)
        return [] if plan is None else [seasons.plan_summary(saga, character, plan)]

    planned = seasons.plan_for(saga, character) is not None
    return SectionOps(
        add=None if planned else lambda: plan_season(saga, character),
        edit=lambda _index: plan_season(saga, character),
        remove=lambda _index: clear_season(saga, character),
        rows=rows,
    )


#: The desktop's names for a covenant Seasons list's buttons (it has no Add).
COVENANT_NOUNS = ("Add", "Plan", "Clear")


def covenant_season_ops(saga: Saga, covenant: Covenant, kind: str) -> SectionOps:
    """A covenant Seasons list of `kind` (seasons.SEASON_KINDS): Plan and
    Clear for the person chosen. Grogs are updated yearly, so their list
    has no Clear."""
    people = seasons.covenant_people(saga, covenant, kind)

    def plan(index: int) -> Command:
        return plan_season(saga, people[index])

    def clear(index: int) -> Command:
        return clear_season(saga, people[index])

    return SectionOps(
        edit=plan,
        remove=None if kind == "grog" else clear,
        rows=lambda: [c.name or "(unnamed)" for c in people],
    )
