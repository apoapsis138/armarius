"""A tradition chapter's forms: the character's effects and items of the
tradition (TraditionEffect), the beings bound to them (BoundBeing), and
the points in the tradition's pools."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from ..commands import Form, SectionOps, delete
from ..form_spec import DialogField
from ..markup import escape
from ..models import (
    TRADITION_EFFECT_KINDS,
    TRADITION_ITEM_KINDS,
    BoundBeing,
    Character,
    Saga,
    TraditionDef,
    TraditionEffect,
)
from ..rules import galdor
from ..rules import hedge_casting as hc
from ..rules import hedge_effects as he
from ..rules import hedge_warping as hw

#: How many Arts, Abilities or runes an effect names: a Technique and a
#: Form, or a rune script's runes.
USES = 3


def effect_fields(
    tradition: TraditionDef, existing: TraditionEffect | None
) -> list[DialogField]:
    """An effect or item of the tradition: what it is, the casting rule
    and Arts it uses, its level, and an item's charges."""
    uses = existing.uses if existing else []
    names = [(escape(n), n) for n in tradition.abilities]
    fields = [
        DialogField(
            "name",
            "Name",
            "text",
            existing.name if existing else "",
            required=True,
        ),
        DialogField(
            "kind",
            "Kind",
            "select",
            existing.kind if existing else TRADITION_EFFECT_KINDS[0],
            options=[(k.capitalize(), k) for k in TRADITION_EFFECT_KINDS]
            + [(f"{k.capitalize()} (an item)", k) for k in TRADITION_ITEM_KINDS],
            required=True,
        ),
        DialogField(
            "rule",
            "Cast or made by",
            "select",
            (existing.rule if existing else "")
            or (tradition.casting[0].name if tradition.casting else None),
            options=[(escape(r.name), r.name) for r in tradition.casting],
            allow_blank=True,
            hint="One of the tradition's ways of casting, or its Lab Total.",
        ),
    ]
    for n in range(1, USES + 1):
        fields.append(
            DialogField(
                f"use_{n}",
                "Uses" if n == 1 else f"...and ({n})",
                "select",
                uses[n - 1] if len(uses) >= n else None,
                options=names,
                allow_blank=True,
                hint="A Technique, then a Form; or the Ability; or the script's runes."
                if n == 1
                else "",
            )
        )
    fields += guideline_fields(tradition, existing)
    fields += [
        DialogField(
            "level",
            "Level",
            "int",
            existing.level if existing else 0,
            show_if=lambda values: not _built(tradition, values),
            hint="Or its Ease Factor; worked out instead from a guideline.",
        ),
        DialogField(
            "parameters",
            "What it does",
            "text",
            existing.parameters if existing else "",
            hint="Range, Duration and Target in the book's words, or what it does.",
        ),
        DialogField(
            "charges",
            "Charges or doses left",
            "optint",
            existing.charges if existing and existing.charges else None,
            show_if=lambda values: values.get("kind") in TRADITION_ITEM_KINDS,
        ),
        DialogField("notes", "Notes", "area", existing.notes if existing else ""),
    ]
    return fields


#: The parameters an effect built on a guideline names.
_KINDS = (("range", "Range"), ("duration", "Duration"), ("target", "Target"))


def _built(tradition: TraditionDef, values: dict[str, Any]) -> bool:
    """Whether the form's guideline sets the level (one with a base)."""
    key = values.get("guideline")
    return any(
        he.guideline_key(g) == key and not g.general for g in tradition.guidelines
    )


def guideline_fields(
    tradition: TraditionDef, existing: TraditionEffect | None
) -> list[DialogField]:
    """The guideline an effect is built on, its Range, Duration and Target
    (the tradition's own, or the Hermetic ones), and further magnitudes:
    none for a tradition with no guideline table."""
    if not tradition.guidelines:
        return []
    chosen = he.guideline_of(tradition, existing) if existing else None
    fields = [
        DialogField(
            "guideline",
            "Guideline",
            "select",
            he.guideline_key(chosen) if chosen else None,
            options=[
                (
                    escape(
                        f"{' '.join(hc.short_name(a) for a in g.arts)} "
                        f"{'General' if g.general else g.level}: {g.name}"
                    ),
                    he.guideline_key(g),
                )
                for g in tradition.guidelines
            ],
            allow_blank=True,
            hint="Its level is the guideline's, plus its parameters' magnitudes.",
        )
    ]
    for kind, label in _KINDS:
        names = he.parameter_names(tradition, kind)
        if not names:
            continue
        fields.append(
            DialogField(
                kind,
                label,
                "select",
                (getattr(existing, kind) if existing else "") or None,
                options=[(escape(n), n) for n in names],
                allow_blank=True,
                show_if=lambda values: _built(tradition, values),
            )
        )
    fields.append(
        DialogField(
            "magnitudes",
            "Further magnitudes",
            "int",
            existing.magnitudes if existing else 0,
            show_if=lambda values: _built(tradition, values),
            hint="Size, complexity, or a modifier the guideline names.",
        )
    )
    return fields


def effect_from(
    tradition: TraditionDef, existing: TraditionEffect | None, values: dict[str, Any]
) -> TraditionEffect:
    made = replace(existing) if existing else TraditionEffect(name="")
    made.name = values["name"]
    made.tradition = tradition.id
    made.kind = values["kind"]
    made.rule = values.get("rule") or ""
    made.uses = [
        values[f"use_{n}"] for n in range(1, USES + 1) if values.get(f"use_{n}")
    ]
    made.level = values.get("level") or 0
    made.parameters = values.get("parameters") or ""
    made.charges = (
        (values.get("charges") or 0) if made.kind in TRADITION_ITEM_KINDS else 0
    )
    made.notes = values.get("notes") or ""
    made.guideline = values.get("guideline") or ""
    built = _built(tradition, values)
    made.range = (values.get("range") or "") if built else ""
    made.duration = (values.get("duration") or "") if built else ""
    made.target = (values.get("target") or "") if built else ""
    made.magnitudes = (values.get("magnitudes") or 0) if built else 0
    design = he.effect_design(tradition, made)
    if design is not None:
        made.level = design.level
    return made


def effect_problem(values: dict[str, Any]) -> str | None:
    if (values.get("level") or 0) < 0:
        return "The level can't be negative."
    if (values.get("charges") or 0) < 0:
        return "The charges can't be negative."
    chosen = [values.get(f"use_{n}") for n in range(1, USES + 1)]
    chosen = [c for c in chosen if c]
    if len(set(chosen)) < len(chosen):
        return "The same Art is named twice."
    return None


def design_problem(tradition: TraditionDef, values: dict[str, Any]) -> str | None:
    """A guideline the Arts chosen don't use, or a parameter the
    tradition doesn't allow the effect."""
    if not _built(tradition, values):
        return effect_problem(values)
    made = effect_from(tradition, None, {"name": "", **values})
    guideline = he.guideline_of(tradition, made)
    if (
        guideline is not None
        and made.uses
        and not set(guideline.arts) <= set(made.uses)
    ):
        return f"The guideline is for {' and '.join(guideline.arts)}."
    design = he.effect_design(tradition, made)
    if design is not None and design.problems:
        return design.problems[0]
    return effect_problem(values)


def effect_ops(character: Character, tradition: TraditionDef) -> SectionOps:
    """Add, Edit and Delete for the tradition's effects and items; a row
    is the effect's position among the tradition's."""
    effects = character.tradition_effects

    def index_of(position: int) -> int:
        return he.of_tradition(character, tradition.id)[position][0]

    def form(position: int | None) -> Form:
        index = index_of(position) if position is not None else None
        existing = effects[index] if index is not None else None

        def apply(values: dict[str, Any]) -> None:
            made = effect_from(tradition, existing, values)
            if index is None:
                effects.append(made)
            else:
                effects[index] = made

        return Form(
            "Add Effect or Item" if index is None else "Edit Effect or Item",
            lambda: effect_fields(tradition, existing),
            apply,
            validate=lambda values: design_problem(tradition, values),
            save_label="Add" if index is None else "Save",
        )

    def remove(position: int) -> Any:
        index = index_of(position)
        return delete(effects, index, effects[index].name)

    return SectionOps(
        add=lambda: form(None),
        edit=form,
        remove=remove,
        rows=lambda: [e.name for _, e in he.of_tradition(character, tradition.id)],
    )


#: What a bond's bonus adds to, as the form offers it.
_APPLIES = [
    ("Its casting totals", "casting"),
    ("Its Lab Totals", "lab"),
    ("Nothing the app works out", "none"),
]


def bond_fields(
    saga: Saga, tradition: TraditionDef, existing: BoundBeing | None
) -> list[DialogField]:
    """A being bound by the tradition: its kind of bond, the Bestiary
    creature it is, and the bonus its bond adds."""
    bonds = tradition.bonds
    feeds = "; ".join(f"{b.name}: {b.feeds}" for b in bonds if b.feeds)
    return [
        DialogField(
            "name", "Name", "text", existing.name if existing else "", required=True
        ),
        DialogField(
            "kind",
            "Bond",
            "select",
            (existing.kind if existing else "") or (bonds[0].name if bonds else None),
            options=[(escape(b.name), b.name) for b in bonds],
            allow_blank=True,
            hint="One of the tradition's bonds; blank for another kind.",
        ),
        DialogField(
            "creature_id",
            "Bestiary creature",
            "select",
            (existing.creature_id if existing else "") or None,
            options=[(escape(c.name), c.id) for c in saga.creatures],
            allow_blank=True,
        ),
        DialogField(
            "bonus",
            "Bonus",
            "int",
            existing.bonus if existing else 0,
            hint=escape(feeds),
        ),
        DialogField(
            "applies_to",
            "Bonus adds to",
            "select",
            (existing.applies_to if existing else ("lab" if bonds else "")) or "none",
            options=_APPLIES,
            required=True,
        ),
        DialogField(
            "service",
            "The service",
            "text",
            existing.service if existing else "",
            show_if=_a_deal,
        ),
        DialogField(
            "vis_yearly",
            "Vis a year",
            "int",
            existing.vis_yearly if existing else 0,
            show_if=_a_deal,
        ),
        DialogField(
            "favour",
            "Favour owed",
            "text",
            existing.favour if existing else "",
            show_if=_a_deal,
        ),
        DialogField("notes", "Notes", "area", existing.notes if existing else ""),
    ]


def _a_deal(values: dict[str, Any]) -> bool:
    """A bond that is a deal with a spirit lord."""
    return values.get("kind") == galdor.DEAL


def bond_from(
    tradition: TraditionDef, existing: BoundBeing | None, values: dict[str, Any]
) -> BoundBeing:
    made = replace(existing) if existing else BoundBeing(name="")
    made.name = values["name"]
    made.tradition = tradition.id
    made.kind = values.get("kind") or ""
    made.creature_id = values.get("creature_id") or ""
    made.bonus = values.get("bonus") or 0
    applies = values.get("applies_to") or "none"
    made.applies_to = "" if applies == "none" else applies
    made.notes = values.get("notes") or ""
    deal = _a_deal(values)
    made.service = (values.get("service") or "") if deal else ""
    made.vis_yearly = (values.get("vis_yearly") or 0) if deal else 0
    made.favour = (values.get("favour") or "") if deal else ""
    return made


def bond_problem(values: dict[str, Any]) -> str | None:
    if (values.get("bonus") or 0) and values.get("applies_to") in (None, "", "none"):
        return "Say what the bonus adds to."
    if (values.get("vis_yearly") or 0) < 0:
        return "Pawns of vis can't be fewer than 0."
    return None


def bond_ops(saga: Saga, character: Character, tradition: TraditionDef) -> SectionOps:
    """Add, Edit and Delete for the beings bound by the tradition; a row
    is the being's position among the tradition's."""
    beings = character.bound_beings

    def index_of(position: int) -> int:
        return hw.bound(character, tradition.id)[position][0]

    def form(position: int | None) -> Form:
        index = index_of(position) if position is not None else None
        existing = beings[index] if index is not None else None

        def apply(values: dict[str, Any]) -> None:
            made = bond_from(tradition, existing, values)
            if index is None:
                beings.append(made)
            else:
                beings[index] = made

        return Form(
            "Add Bound Being" if index is None else "Edit Bound Being",
            lambda: bond_fields(saga, tradition, existing),
            apply,
            validate=bond_problem,
            save_label="Add" if index is None else "Save",
        )

    def remove(position: int) -> Any:
        index = index_of(position)
        return delete(beings, index, beings[index].name)

    return SectionOps(
        add=lambda: form(None),
        edit=form,
        remove=remove,
        rows=lambda: [b.name for _, b in hw.bound(character, tradition.id)],
    )


def pool_fields(character: Character, tradition: TraditionDef) -> list[DialogField]:
    """The points in each of the tradition's pools."""
    return [
        DialogField(
            f"pool_{n}",
            pool.name,
            "int",
            hw.pool_points(character, tradition, pool.name),
            hint=escape(f"Cap: {pool.cap}") if pool.cap else "",
        )
        for n, pool in enumerate(tradition.pools)
    ]


def pool_problem(values: dict[str, Any]) -> str | None:
    if any((v or 0) < 0 for k, v in values.items() if k.startswith("pool_")):
        return "A pool can't hold fewer than 0 points."
    return None


def pool_ops(character: Character, tradition: TraditionDef) -> SectionOps:
    """Edit for the tradition's pools (one row: the section)."""

    def apply(values: dict[str, Any]) -> None:
        for n, pool in enumerate(tradition.pools):
            key = hw.pool_key(tradition, pool.name)
            points = values.get(f"pool_{n}") or 0
            if points:
                character.tradition_pools[key] = points
            else:
                character.tradition_pools.pop(key, None)

    def form(_row: int) -> Form:
        return Form(
            "Edit Pools",
            lambda: pool_fields(character, tradition),
            apply,
            validate=pool_problem,
        )

    return SectionOps(
        edit=form if tradition.pools else None,
        rows=lambda: ["Pools"] if tradition.pools else [],
    )
