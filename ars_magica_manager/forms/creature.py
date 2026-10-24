"""The Bestiary's forms, independent of how they are drawn: New Creature,
Edit Creature, and Add, Edit and Delete for the Bestiary's list and each
list on a creature's sheet (commands.SectionOps), for either front-end.

Every section of a creature's sheet is in `creature_ops`, so a front-end
that draws a section under its id (sections.py) gets its a / e / d.
Pattern: the sheet's `_section_ops` table, as a neighbour's; Abilities,
Virtues and Flaws and traits reuse the familiar's and character's ops."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .. import creatures, places
from ..arts import ARTS, FORMS
from ..commands import Confirm, Form, SectionOps, delete
from ..form_spec import EMPHASIS_HINT, DialogField, attr, pairs
from ..markup import escape
from ..models import (
    DETAIL_LEVELS,
    REALMS,
    SEASONS,
    BodyVis,
    Creature,
    CreatureAttack,
    CreaturePower,
    Saga,
)
from ..rules import creature_build
from ..sections import (
    BESTIARY_SECTION,
    CREATURE_ABILITIES_SECTION,
    CREATURE_ATTACKS_SECTION,
    CREATURE_CHARACTERISTICS_SECTION,
    CREATURE_DESCRIPTION_SECTION,
    CREATURE_HEALTH_SECTION,
    CREATURE_INFO_SECTION,
    CREATURE_POWERS_SECTION,
    CREATURE_REPUTATIONS_SECTION,
    CREATURE_TRAITS_SECTION,
    CREATURE_VF_SECTION,
    CREATURE_VIS_SECTION,
    LINKS_SECTION,
)
from . import familiar as ff
from . import trait as trait_forms
from . import virtue as virtue_forms
from . import world as world_forms
from .character import (
    characteristics_fields,
    characteristics_from,
    fatigue_fields,
    wounds_fields,
)
from .secrets import secrets_ops

# -- the creature itself --


def _has_realm(values: dict[str, Any]) -> bool:
    return bool(values.get("realm"))


def _many(values: dict[str, Any]) -> bool:
    return bool(values.get("many"))


def _infernal(values: dict[str, Any]) -> bool:
    return values.get("realm") == "Infernal"


#: What only an Infernal creature has (Realms of Power: The Infernal).
INFERNAL_FIELDS = {"order": "", "hierarchy": None, "weakness": ""}


def _creature_identity_fields(c: Creature | None) -> list[DialogField]:
    """Its name, and whether the stat block is for many of a kind."""
    return [
        DialogField("name", "Name", "text", attr(c, "name", ""), required=True),
        DialogField(
            "many",
            "Many of a kind",
            "check",
            attr(c, "many", False),
            hint="One stat block for many: a pack of wolves, a swarm of mice.",
        ),
        DialogField(
            "how_many",
            "How many",
            "text",
            attr(c, "how_many", ""),
            placeholder="e.g. A dozen in the marsh",
            show_if=_many,
        ),
    ]


def _creature_realm_fields(c: Creature | None) -> list[DialogField]:
    """Its realm, and its Might, Might Form and Might Pool when it has one."""
    return [
        DialogField(
            "realm",
            "Realm",
            "select",
            attr(c, "realm", "") or None,
            options=pairs(REALMS),
            allow_blank=True,
            placeholder="(none: a mundane beast)",
        ),
        DialogField(
            "might", "Might Score", "int", attr(c, "might", 0), show_if=_has_realm
        ),
        DialogField(
            "might_form",
            "Might Form",
            "select",
            attr(c, "might_form", "") or None,
            options=pairs(FORMS),
            allow_blank=True,
            placeholder="(none)",
            show_if=_has_realm,
        ),
        DialogField(
            "might_pool",
            "Might Pool now (blank = not tracked)",
            "optint",
            attr(c, "might_pool", None),
            show_if=_has_realm,
        ),
    ]


def _infernal_fields(c: Creature | None) -> list[DialogField]:
    """A demon's Order, Hierarchy and Weakness (INFERNAL_FIELDS)."""
    return [
        DialogField(
            "order",
            "Order",
            "text",
            attr(c, "order", ""),
            placeholder="e.g. Prince of the False Gods",
            show_if=_infernal,
        ),
        DialogField(
            "hierarchy",
            "Hierarchy (blank = not given)",
            "optint",
            attr(c, "hierarchy", None),
            show_if=_infernal,
        ),
        DialogField(
            "weakness",
            "Weakness",
            "text",
            attr(c, "weakness", ""),
            placeholder="e.g. Running water",
            show_if=_infernal,
        ),
    ]


def _creature_trait_fields(c: Creature | None) -> list[DialogField]:
    """Its Size, age, Confidence and season."""
    return [
        DialogField("size", "Size", "int", attr(c, "size", 0)),
        DialogField(
            "age",
            "Age",
            "text",
            attr(c, "age", ""),
            placeholder="e.g. 200 (40), or n/a",
            hint="As the book prints it, the apparent age in brackets.",
        ),
        DialogField(
            "confidence_score",
            "Confidence Score (blank = none)",
            "optint",
            attr(c, "confidence_score", None),
        ),
        DialogField(
            "confidence_points",
            "Confidence Points",
            "int",
            attr(c, "confidence_points", 0),
            show_if=lambda values: values.get("confidence_score") is not None,
        ),
        DialogField(
            "season",
            "Season",
            "select",
            attr(c, "season", "") or None,
            options=pairs(SEASONS),
            allow_blank=True,
            placeholder="(none)",
            hint="A magical creature's season.",
        ),
    ]


def _creature_record_fields(saga: Saga, c: Creature | None) -> list[DialogField]:
    """How much of it is written down, where it is found and where it is
    printed."""
    return [
        DialogField(
            "detail",
            "Detail",
            "select",
            attr(c, "detail", "Sketch"),
            options=pairs(DETAIL_LEVELS),
            hint="A line, a sketch, or written in full.",
        ),
        places.where_field(saga, c, "Found at"),
        DialogField(
            "source",
            "Source",
            "text",
            attr(c, "source", ""),
            placeholder="e.g. Guardians of the Forests p. 34",
        ),
    ]


def info_fields(saga: Saga, creature: Creature | None) -> list[DialogField]:
    """What a creature is: its name, whether the stat block is for one or
    many, its realm and Might, Size and season, how much is written down,
    where it is found and where it is printed. Only the name is
    required; a creature with no realm is a mundane beast."""
    c = creature
    return [
        *_creature_identity_fields(c),
        *_creature_realm_fields(c),
        *_infernal_fields(c),
        *_creature_trait_fields(c),
        *_creature_record_fields(saga, c),
    ]


def apply_info(saga: Saga, creature: Creature, values: dict[str, Any]) -> None:
    values = dict(values)
    places.put(creature, values.pop("where", None))
    for key in ("realm", "might_form", "season"):
        values[key] = values.get(key) or ""
    if not values["realm"]:
        values.update(might=0, might_form="", might_pool=None)
    if values["realm"] != "Infernal":
        values.update(INFERNAL_FIELDS)
    if values.get("confidence_score") is None:
        values["confidence_points"] = 0
    if not values.get("many"):
        values["how_many"] = ""
    for key, value in values.items():
        setattr(creature, key, value)
    places.sync(saga)


def new_creature_form(saga: Saga) -> Form:
    def apply(values: dict[str, Any]) -> None:
        apply_info(saga, creatures.add(saga, values["name"]), values)

    return Form(
        "New Creature",
        lambda: info_fields(saga, None),
        apply,
        save_label="Create",
        help_id="bestiary",
    )


def edit_creature_form(saga: Saga, creature: Creature) -> Form:
    return Form(
        f"Edit {escape(creature.name)}",
        lambda: info_fields(saga, creature),
        lambda values: apply_info(saga, creature, values),
    )


def characteristics_form(creature: Creature) -> Form:
    """Its eight Characteristics (its Intelligence a Cunning score for an
    animal mind), its Soak, whether it tires and can be wounded, its
    Fatigue levels as the book prints them, and its Encumbrance."""

    def fields() -> list[DialogField]:
        return characteristics_fields(creature.characteristics) + [
            DialogField(
                "cunning",
                "Cunning, not Intelligence",
                "check",
                creature.cunning,
                hint="An animal mind: its Intelligence shows as Cun.",
            ),
            DialogField(
                "soak",
                "Soak",
                "int",
                creature.soak,
                hint="As the book prints it.",
            ),
            DialogField("tires", "Can tire", "check", creature.tires),
            DialogField(
                "fatigue_levels",
                "Fatigue levels",
                "text",
                creature.fatigue_levels,
                placeholder="e.g. OK, 0, -1, -3, -5, Unconscious",
                hint="Blank: a person's.",
                show_if=lambda values: bool(values.get("tires")),
            ),
            DialogField(
                "can_be_wounded", "Can be wounded", "check", creature.can_be_wounded
            ),
            DialogField(
                "encumbrance",
                "Encumbrance",
                "text",
                creature.encumbrance,
                placeholder="e.g. 0 (0)",
                hint="Its Burden in brackets.",
            ),
        ]

    def apply(values: dict[str, Any]) -> None:
        creature.characteristics = characteristics_from(values)
        for key in (
            "cunning",
            "soak",
            "fatigue_levels",
            "tires",
            "can_be_wounded",
            "encumbrance",
        ):
            if key in values:
                setattr(creature, key, values[key])

    return Form("Edit Characteristics", fields, apply)


def description_form(creature: Creature) -> Form:
    """What it looks like, what it carries, and anything else."""

    def fields() -> list[DialogField]:
        return [
            DialogField(
                "appearance",
                "Appearance",
                "area",
                creature.appearance,
                hint=EMPHASIS_HINT,
            ),
            DialogField(
                "equipment",
                "Equipment",
                "text",
                creature.equipment,
                placeholder="e.g. A tooled saddle",
            ),
            DialogField(
                "notes",
                "Notes",
                "area",
                creature.notes,
                hint=f"Its habits, its lair, the story it belongs to. {EMPHASIS_HINT}",
            ),
        ]

    def apply(values: dict[str, Any]) -> None:
        for key, value in values.items():
            setattr(creature, key, value)

    return Form("Edit Description", fields, apply)


def health_form(creature: Creature) -> Form:
    """Its wounds now, and how fatigued it is."""

    def fields() -> list[DialogField]:
        return wounds_fields(creature.wounds, soak=False) + fatigue_fields(
            creature.fatigue_level
        )

    def apply(values: dict[str, Any]) -> None:
        values = dict(values)
        creature.fatigue_level = values.pop("level")
        creature.wounds = creature.wounds.with_counts(**values)

    return Form("Edit Wounds and Fatigue", fields, apply)


# -- its lists --


def _list_ops(
    items: list[Any],
    noun: str,
    fields: Callable[[Any | None], list[DialogField]],
    make: Callable[[dict[str, Any]], Any],
    row: Callable[[Any], str],
    validate: Callable[[dict[str, Any]], str | None] | None = None,
    prepare: Callable[[dict[str, Any]], dict[str, Any]] = dict,
) -> SectionOps:
    """Add, Edit and Delete for one of the creature's lists: a form of
    `fields` whose values (`prepare`d) `make` a new entry, or set the
    chosen one's."""

    def form(index: int | None) -> Form:
        existing = items[index] if index is not None else None

        def apply(values: dict[str, Any]) -> None:
            values = prepare(values)
            if existing is None:
                items.append(make(values))
                return
            for key, value in values.items():
                setattr(existing, key, value)

        title = f"Add {noun}" if existing is None else f"Edit {escape(row(existing))}"
        return Form(title, lambda: fields(existing), apply, validate=validate)

    return SectionOps(
        add=lambda: form(None),
        edit=form,
        remove=lambda index: delete(items, index, row(items[index])),
        rows=lambda: [row(item) for item in items],
    )


def attack_fields(attack: CreatureAttack | None) -> list[DialogField]:
    """One line of its Combat, as the book prints the totals."""
    return [
        DialogField(
            "name",
            "Attack",
            "text",
            attr(attack, "name", ""),
            required=True,
            placeholder="e.g. Bite",
        ),
        DialogField("init", "Init", "int", attr(attack, "init", 0)),
        DialogField(
            "attack", "Attack (blank = n/a)", "optint", attr(attack, "attack", 0)
        ),
        DialogField("defense", "Defense", "int", attr(attack, "defense", 0)),
        DialogField(
            "damage", "Damage (blank = n/a)", "optint", attr(attack, "damage", 0)
        ),
    ]


def power_fields(power: CreaturePower | None) -> list[DialogField]:
    """One of its Powers: what it costs and does; its Penetration is
    worked out from the Might and the cost."""
    return [
        DialogField("name", "Power", "text", attr(power, "name", ""), required=True),
        DialogField(
            "might_cost", "Might Point cost", "int", attr(power, "might_cost", 0)
        ),
        DialogField("init", "Init", "int", attr(power, "init", 0)),
        DialogField(
            "form",
            "Form",
            "select",
            attr(power, "form", "") or None,
            options=pairs(FORMS),
            allow_blank=True,
            placeholder="(none)",
        ),
        DialogField(
            "range", "Range", "text", attr(power, "range", ""), placeholder="e.g. Voice"
        ),
        DialogField(
            "duration",
            "Duration",
            "text",
            attr(power, "duration", ""),
            placeholder="e.g. Sun",
        ),
        DialogField(
            "target",
            "Target",
            "text",
            attr(power, "target", ""),
            placeholder="e.g. Ind",
        ),
        DialogField(
            "level",
            "Effect level (blank = none given)",
            "optint",
            attr(power, "level", None),
        ),
        DialogField(
            "quality",
            "From Quality",
            "select",
            attr(power, "quality", "") or "",
            options=[("Typed", ""), *((q, q) for q in creature_build.POWERS)],
            hint="Suggests the cost and Initiative from the effect level (RoP: "
            "Magic p. 36): a new power's are filled in, and typed ones that "
            "differ are checked, never refused.",
        ),
        DialogField(
            "penetration_bonus",
            "Penetration bonus",
            "int",
            attr(power, "penetration_bonus", 0),
            hint="Beyond its Might: a Penetration Ability or Quality.",
        ),
        DialogField(
            "description", "What it does", "area", attr(power, "description", "")
        ),
    ]


def _power_values(values: dict[str, Any]) -> dict[str, Any]:
    return {
        **values,
        "form": values.get("form") or "",
        "quality": values.get("quality") or "",
    }


def fill_suggested(creature: Creature, power: CreaturePower) -> CreaturePower:
    """A power from a Quality with its cost and Initiative still blank (0)
    takes the Quality's figures, which stay editable."""
    figures = creature_build.suggested(creature, power)
    if figures is not None and power.might_cost == 0 and power.init == 0:
        power.might_cost, power.init = figures
    return power


def vis_fields(vis: BodyVis | None) -> list[DialogField]:
    """Vis in its body: how many pawns, of what Art, and where."""
    return [
        DialogField("pawns", "Pawns", "int", attr(vis, "pawns", 1)),
        DialogField(
            "art",
            "Art",
            "select",
            attr(vis, "art", "") or None,
            options=pairs(ARTS),
            required=True,
        ),
        DialogField(
            "where",
            "Where in the body",
            "text",
            attr(vis, "where", ""),
            placeholder="e.g. in its horns",
        ),
    ]


def _vis_problem(values: dict[str, Any]) -> str | None:
    return "Pawns must be at least 1." if values["pawns"] < 1 else None


def creature_ops(saga: Saga, creature: Creature) -> dict[str, SectionOps]:
    """Every section of a creature's sheet the core edits, by section id."""
    return {
        CREATURE_INFO_SECTION: SectionOps(
            edit=lambda _row: edit_creature_form(saga, creature)
        ),
        CREATURE_CHARACTERISTICS_SECTION: SectionOps(
            edit=lambda _row: characteristics_form(creature)
        ),
        CREATURE_DESCRIPTION_SECTION: SectionOps(
            edit=lambda _row: description_form(creature)
        ),
        CREATURE_HEALTH_SECTION: SectionOps(edit=lambda _row: health_form(creature)),
        CREATURE_VF_SECTION: virtue_forms.virtue_flaw_ops(saga, creature),
        CREATURE_TRAITS_SECTION: trait_forms.trait_ops(
            creature.personality_traits, CREATURE_TRAITS_SECTION
        ),
        CREATURE_REPUTATIONS_SECTION: trait_forms.trait_ops(
            creature.reputations, CREATURE_REPUTATIONS_SECTION
        ),
        CREATURE_ATTACKS_SECTION: _list_ops(
            creature.attacks,
            "an Attack",
            attack_fields,
            lambda values: CreatureAttack(**values),
            lambda a: a.name or "(unnamed)",
        ),
        CREATURE_ABILITIES_SECTION: ff.ability_ops(saga, creature),
        CREATURE_POWERS_SECTION: _list_ops(
            creature.powers,
            "a Power",
            power_fields,
            lambda values: fill_suggested(creature, CreaturePower(**values)),
            lambda p: p.name or "(unnamed)",
            prepare=_power_values,
        ),
        CREATURE_VIS_SECTION: _list_ops(
            creature.vis,
            "Vis",
            vis_fields,
            lambda values: BodyVis(**values),
            lambda v: creatures.vis_text(v),
            validate=_vis_problem,
        ),
        LINKS_SECTION: world_forms.link_ops(saga, creature),
        **secrets_ops(creature),
    }


# -- the Bestiary's list --


def delete_creature(saga: Saga, creature: Creature) -> Confirm:
    message = f"Delete {escape(creature.name)}?"
    consequences = creatures.deletion_consequences(saga, creature)
    if consequences:
        message += "\n\n" + "\n".join(escape(c) for c in consequences)
    return Confirm(message, lambda: creatures.delete(saga, creature))


def bestiary_ops(saga: Saga) -> dict[str, SectionOps]:
    """The Bestiary's list: New, Edit or Delete the chosen creature."""

    def listed() -> list[Creature]:
        return creatures.listed(saga)

    return {
        BESTIARY_SECTION: SectionOps(
            add=lambda: new_creature_form(saga),
            edit=lambda index: edit_creature_form(saga, listed()[index]),
            remove=lambda index: delete_creature(saga, listed()[index]),
            rows=lambda: [c.name for c in listed()],
        )
    }
