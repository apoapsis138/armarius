"""Planning a season: the Plan Season form and the plan it builds, the
supplement activities' fields, a grog's year and breakthroughs."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from functools import partial
from typing import Any

from .... import book_kinds, catalog, seasons, sourcebooks
from .... import books as bk
from .... import lab_texts as lt
from .... import spells as spl
from ....form_spec import EMPHASIS_HINT, DialogField, attr
from ....markup import escape
from ....models import (
    Breakthrough,
    Character,
    GrogYear,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
    XpAllocation,
)
from ....rules import activities as season_rules
from ....rules import (
    apprentice_seasons,
    book_seasons,
    creation_characteristics,
    experiment,
    laboratory_seasons,
    supplement_seasons,
)
from ....rules import supplement_work as sw
from ....seasons import plans as season_plans_text
from ..fields import FieldsDialog
from ..pickers import VirtueFlawPickerScreen


def _season_plan_from(
    saga: Saga, character: Character, values: dict[str, Any]
) -> SeasonPlan:
    """The plan the season dialog's values describe (hidden fields are
    missing from `values`, so everything is read with a default)."""
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
        book_id=(
            values.get("book_id")
            if activity == season_rules.READ
            else values.get("copy_book_id")
            if activity in (book_seasons.COPY_BOOK, book_seasons.TRANSLATE_BOOK)
            else values.get("text_id")
            if activity == book_seasons.COPY_TEXTS
            else None
        ),
        spell_id=(
            values.get("tablet_spell_id")
            if activity == book_seasons.WRITE_TABLET
            else None
        ),
        title=(
            values.get("title") or ""
            if activity
            in (
                book_seasons.WRITE_SUMMA,
                book_seasons.WRITE_TRACTATUS,
                book_seasons.EDIT_FLORILEGIUM,
            )
            else _supplement_title(activity, values)
        ),
        book_level=(
            values.get("book_level")
            if activity == book_seasons.WRITE_SUMMA
            else _supplement_level(activity, values)
        ),
        language=(
            values.get("language") or ""
            if activity
            in (
                book_seasons.WRITE_SUMMA,
                book_seasons.WRITE_TRACTATUS,
                book_seasons.TRANSLATE_BOOK,
            )
            else ""
        ),
        correspondence=values.get("correspondence") or "",
        gloss=bool(values.get("gloss")) if activity == season_rules.READ else False,
        florilegium_subject=(
            values.get("florilegium_subject") or ""
            if activity == book_seasons.EDIT_FLORILEGIUM
            else ""
        ),
        quick=bool(values.get("quick"))
        if activity == book_seasons.COPY_BOOK
        else False,
        subject_id=(
            values.get("student_id")
            if activity
            in (
                book_seasons.TEACH_ABBREVIATIONS,
                apprentice_seasons.OPEN_ARTS,
                apprentice_seasons.TEACH_VIRTUE,
            )
            else None
        ),
        research=(
            values.get("research") or "" if activity == experiment.INTEGRATE else ""
        ),
        research_kind=values.get("research_kind") or "Minor",
        effect_id=(
            values.get("virtue_id")
            if activity == apprentice_seasons.TEACH_VIRTUE
            else _vf_id(values.get("mystery_virtue"))
            if activity == "undergo_initiation"
            else None
        ),
        teacher_id=(
            values.get("teacher_id")
            if activity
            in (
                season_rules.TAUGHT,
                season_rules.TRAINED,
                laboratory_seasons.ASSIST,
                "undergo_initiation",
                "record_lectures",
            )
            else None
        ),
        vis_from=(
            values.get("vis_from") or "character"
            if activity == season_rules.VIS_STUDY
            else ""
        ),
        die=(
            values.get("die")
            if activity
            in (
                season_rules.VIS_STUDY,
                apprentice_seasons.SEARCH,
                experiment.INTEGRATE,
                "search_lacuna",
            )
            else None
        ),
    )
    for key, value in _supplement_plan_values(character, activity, values).items():
        setattr(plan, key, value)
    return plan


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


def _vf_picker_field(
    key: str,
    label: str,
    saga: Saga,
    character: Character,
    side: str,
    value: VirtueFlawInstance | None,
    show_if: Callable[[dict[str, Any]], bool],
) -> DialogField:
    """A field choosing a Virtue or Flaw (`side`) for `character` from the
    catalog picker, which asks for anything it names; Delete clears it."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()

    def display(instance: VirtueFlawInstance) -> str:
        definition = by_id.get(instance.vf_id)
        tier = f" ({definition.tier})" if definition else ""
        return catalog.describe_virtue_flaw(instance, by_id) + tier

    def picker(_current: Any) -> VirtueFlawPickerScreen:
        books = sourcebooks.saga_books(saga)
        return VirtueFlawPickerScreen(
            character.virtues_flaws,
            side=side,
            chooser=catalog.VirtueFlawChooser.for_character(character, books),
            own_abilities=[a.name for a in character.abilities],
            refusal=partial(creation_characteristics.virtue_refusal, saga, character),
        )

    return DialogField(
        key,
        label,
        "picker",
        value,
        allow_blank=True,
        placeholder=f"(choose the {side}...)",
        picker=picker,
        display=display,
        show_if=show_if,
    )


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


def _supplement_fields(
    saga: Saga,
    character: Character,
    existing: SeasonPlan | None,
    activity_is: Callable[..., Callable[[dict[str, Any]], bool]],
) -> list[DialogField]:
    """The season form's fields for the supplement sub-systems."""
    plan = existing
    level = plan.book_level if plan else None
    bonus = plan.other_modifier if plan else 0
    title = plan.title if plan else ""
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
        DialogField(
            "score_written",
            "Score when written",
            "optint",
            level,
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
        _vf_picker_field(
            "mystery_virtue",
            "Virtue initiated",
            saga,
            character,
            "Virtue",
            VirtueFlawInstance(plan.effect_id, dict(plan.effect_params))
            if plan and plan.effect_id
            else None,
            show_if=activity_is("undergo_initiation"),
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
        _vf_picker_field(
            "ordeal_flaw",
            "Flaw gained",
            saga,
            character,
            "Flaw",
            VirtueFlawInstance(plan.device_id, dict(plan.ordeal_params))
            if plan and plan.device_id
            else None,
            show_if=_ordeal_is(activity_is, sw.GAIN_FLAW, sw.RAISE_FLAW),
        ),
        DialogField(
            "ordeal_lost_virtue",
            "Virtue lost",
            "select",
            _own_vf_value(character, plan.ordeal_lost_id, plan.ordeal_lost_params)
            if plan
            else None,
            options=_own_vf_options(character, "Virtue", ("Minor", "Major")),
            allow_blank=True,
            placeholder="(choose one of their Virtues)",
            show_if=_ordeal_is(activity_is, sw.LOSE_VIRTUE),
        ),
        DialogField(
            "ordeal_raised_flaw",
            "Minor Flaw raised",
            "select",
            _own_vf_value(character, plan.ordeal_lost_id, plan.ordeal_lost_params)
            if plan
            else None,
            options=_own_vf_options(character, "Flaw", ("Minor",)),
            allow_blank=True,
            placeholder="(choose one of their Minor Flaws)",
            show_if=_ordeal_is(activity_is, sw.RAISE_FLAW),
        ),
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


def _grog_year_dialog(
    character: Character, existing: GrogYear | None
) -> FieldsDialog[GrogYear]:
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

    dialog = FieldsDialog(
        f"{escape(character.name)}'s Yearly Update",
        [
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
        ],
        build=lambda values: GrogYear(
            vocational=values.get("vocational") or "",
            vocational_xp=values.get("vocational_xp") or 0,
            practice=values.get("practice") or "",
            exposure=values.get("exposure") or "",
            exposure_2=values.get("exposure_2") or "",
            story_awards=values.get("story_awards") or 0,
        ),
    )
    dialog.help_id = "grog-year"
    return dialog


#: What reaching a research goal grants (Breakthrough.grant_kind).
GRANT_KINDS = [
    ("An Ability (the points become its xp)", "Ability"),
    ("A Virtue", "Virtue"),
    ("A new parameter (the troupe records it)", "Parameter"),
]


def _breakthrough_dialog(existing: Breakthrough | None) -> FieldsDialog[Breakthrough]:
    """A magus's original research goal: what it
    is, the kind of Breakthrough sought (Minor, Major, Hermetic; its target
    follows, and the storyguide may type a secret one), and what reaching it
    grants."""
    virtues = sorted(
        (d for d in catalog.load_virtue_flaw_catalog() if d.type == "Virtue"),
        key=lambda d: d.name,
    )
    grant_kind = existing.grant_kind if existing else ""

    def grant(kind: str) -> str:
        return existing.grant if existing and grant_kind == kind else ""

    def build(values: dict[str, Any]) -> Breakthrough:
        kind = values.get("grant_kind") or ""
        made = replace(existing) if existing else Breakthrough(name="")
        made.name = values["name"]
        made.description = values.get("description") or ""
        made.kind = values["kind"]
        made.target = values["target"]
        made.points = values.get("points") or 0
        made.grant_kind = kind
        made.grant = values.get(f"grant_{kind.lower()}") or "" if kind else ""
        made.reached = made.reached and made.points >= made.target
        return made

    def problem(values: dict[str, Any]) -> str | None:
        if (values.get("target") or 0) < 1:
            return "The target is at least 1 point."
        if (values.get("points") or 0) < 0:
            return "The points gained can't be negative."
        return None

    return FieldsDialog(
        "Add Research Goal" if existing is None else "Edit Research Goal",
        [
            DialogField(
                "name",
                "Goal",
                "text",
                existing.name if existing else "",
                required=True,
                placeholder="e.g. Penetrating the Aegis",
            ),
            DialogField(
                "description",
                "What it is",
                "area",
                existing.description if existing else "",
            ),
            DialogField(
                "kind",
                "Breakthrough",
                "select",
                existing.kind if existing else "Minor",
                options=[
                    (f"{kind} ({points} points)", kind)
                    for kind, points in experiment.KINDS.items()
                ],
                required=True,
                fills=lambda values: {
                    "target": experiment.KINDS.get(values.get("kind") or "", 30)
                },
            ),
            DialogField(
                "target",
                "Target",
                "int",
                existing.target if existing else experiment.KINDS["Minor"],
                hint="The storyguide may set a secret target.",
            ),
            DialogField(
                "points",
                "Points so far",
                "int",
                existing.points if existing else 0,
            ),
            DialogField(
                "grant_kind",
                "Reaching it grants",
                "select",
                grant_kind or None,
                options=GRANT_KINDS,
                allow_blank=True,
                placeholder="(the troupe decides)",
            ),
            DialogField(
                "grant_ability",
                "Ability",
                "text",
                grant("Ability"),
                show_if=lambda values: values.get("grant_kind") == "Ability",
            ),
            DialogField(
                "grant_virtue",
                "Virtue",
                "select",
                grant("Virtue") or None,
                options=[(escape(d.name), d.id) for d in virtues],
                allow_blank=True,
                show_if=lambda values: values.get("grant_kind") == "Virtue",
            ),
            DialogField(
                "grant_parameter",
                "Parameter",
                "text",
                grant("Parameter"),
                show_if=lambda values: values.get("grant_kind") == "Parameter",
            ),
        ],
        save_label="Add" if existing is None else "Save",
        build=build,
        validate=problem,
    )


ShowIf = Callable[[dict[str, Any]], bool]


def _activity_is(*keys: str) -> ShowIf:
    """A field's show_if: shown while the Activity is one of `keys`."""
    return lambda values: values.get("activity") in keys


def _book_options(saga: Saga, character: Character) -> list[tuple[str, str]]:
    return [
        (escape(seasons.book_label(b)), b.id)
        for b in bk.studyable_books(saga, character)
    ]


def _study_fields(
    saga: Saga, character: Character, existing: SeasonPlan | None
) -> list[DialogField]:
    """The Activity, and the Source Quality, book or teacher it studies from."""
    books = sourcebooks.saga_books(saga)
    activities = season_rules.activities_for(
        character, books=books, keep=attr(existing, "activity", "")
    )
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
            "select",
            attr(existing, "activity", None),
            options=[(a.label, a.key) for a in activities],
            required=True,
            hint="The line above Save shows what the season will give.",
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


def _season_plan_dialog(
    saga: Saga, character: Character, existing: SeasonPlan | None
) -> FieldsDialog[SeasonPlan]:
    """Plan `character`'s current season: the activity, what
    its experience goes into, and notes. The line above Save shows what the
    season will give, worked out as the form is filled in. Each field shows
    only for the activities that use it."""
    fields = [
        *_study_fields(saga, character, existing),
        *_subject_fields(saga, character, existing),
        *_book_work_fields(saga, character, existing),
        *_student_and_research_fields(saga, character, existing),
        *_supplement_fields(saga, character, existing, _activity_is),
        *_correspondence_fields(saga, character, existing),
        *_closing_fields(character, existing),
    ]

    def problem(values: dict[str, Any]) -> str | None:
        plan = _season_plan_from(saga, character, values)
        found = season_rules.problems(character, plan, saga)
        if not found and plan.activity == season_rules.OTHER and not plan.details:
            return "Say in Notes what the season is spent on."
        return found[0] if found else None

    dialog = FieldsDialog(
        f"Plan {escape(character.name)}'s Season "
        f"({saga.current_season} {saga.current_year})",
        fields,
        validate=problem,
        live=lambda values: seasons.live_text(
            saga, character, _season_plan_from(saga, character, values)
        ),
        build=lambda values: _season_plan_from(saga, character, values),
    )
    dialog.help_id = "plan-season"
    return dialog
