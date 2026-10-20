"""A familiar's forms, independent of how they are drawn: the fields each
asks for (form_spec.DialogField lists) and what saving one does to the
familiar, as commands.Form steps and commands.SectionOps.

Its single-record Edits (the familiar's details, its Binding & Cords, its
Characteristics, Wounds and Fatigue) are `edits`; its lists (Natural
Weapons, Abilities, Bond Powers) have `natural_weapon_ops`,
`ability_ops` and `bond_power_ops`. Its Personality Traits and
Reputations are trait_forms.trait_ops'.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from .. import catalog, sourcebooks, storage
from .. import familiars as fam
from .. import possessions as pos
from .. import sheet_text as st
from ..arts import FORMS, TECHNIQUES
from ..commands import Choice, Choose, Command, Form, SectionOps, delete, not_offered
from ..form_spec import DialogField, attr, description_field, pairs
from ..markup import escape
from ..models import (
    CORD_SCORE_COSTS,
    GEAR_QUALITIES,
    GEAR_QUALITY_DEFAULT,
    GEAR_TYPES_BY_KIND,
    SEASONS,
    Ability,
    AbilityDef,
    BondPower,
    Creature,
    Familiar,
    Possession,
    Saga,
    VirtueFlawInstance,
    Wounds,
)
from ..rules import creation_access as access
from ..rules import scores
from .character import (
    characteristics_fields,
    characteristics_from,
    fatigue_fields,
    wounds_fields,
)

# -- the familiar's details, Binding & Cords and Characteristics --


def info_fields(familiar: Familiar) -> list[DialogField]:
    f = familiar
    return [
        DialogField("name", "Name", "text", f.name, required=True),
        DialogField("species", "Species / Description", "text", f.species),
        DialogField(
            "season_bound",
            "Season Bound",
            "select",
            f.season_bound or None,
            options=pairs(SEASONS),
            allow_blank=True,
            placeholder="(not set)",
        ),
        DialogField("year_bound", "Year Bound", "optint", f.year_bound),
        DialogField("magic_might", "Magic Might Score", "int", f.magic_might),
        DialogField("might_pool", "Current Might Pool", "optint", f.might_pool),
        DialogField("size", "Size", "int", f.size),
        DialogField("wound_multiplier", "Wound Multiplier", "int", f.wound_multiplier),
    ]


def apply_info(familiar: Familiar, values: dict[str, Any]) -> None:
    values = dict(values)
    values["season_bound"] = values["season_bound"] or ""
    for key, value in values.items():
        setattr(familiar, key, value)


def binding_fields(familiar: Familiar) -> list[DialogField]:
    """A Familiar's Initial Binding details and its three Cords (each
    option shows its point cost)."""
    cord_options = [
        (f"+{score} ({fam.cord_cost(score)} pts)", str(score))
        for score in CORD_SCORE_COSTS
    ]
    return [
        DialogField(
            "binding_technique",
            "Binding Technique",
            "select",
            familiar.binding_technique or None,
            options=pairs(TECHNIQUES),
            allow_blank=True,
            placeholder="(not set)",
        ),
        DialogField(
            "binding_form",
            "Binding Form",
            "select",
            familiar.binding_form or None,
            options=pairs(FORMS),
            allow_blank=True,
            placeholder="(not set)",
        ),
        DialogField(
            "binding_lab_total",
            "Initial Binding Lab Total",
            "int",
            familiar.binding_lab_total,
        ),
        DialogField(
            "target_binding_level",
            "Target Binding Level",
            "int",
            familiar.target_binding_level,
        ),
        DialogField(
            "vis_spent_binding",
            "Cumulative Vis Spent (pawns)",
            "int",
            familiar.vis_spent_binding,
        ),
        *(
            DialogField(
                attribute,
                label,
                "select",
                str(getattr(familiar, attribute)),
                options=cord_options,
            )
            for attribute, label, _blurb in fam.CORDS
        ),
    ]


def binding_values(values: dict[str, Any]) -> dict[str, object]:
    """The Binding & Cords form's values as the familiar's fields: a Cord
    as its score, a blank Technique or Form as ""."""
    cords = {attribute for attribute, _label, _blurb in fam.CORDS}
    return {
        key: int(value) if key in cords else ("" if value is None else value)
        for key, value in values.items()
    }


def apply_binding(familiar: Familiar, values: dict[str, Any]) -> None:
    for key, value in binding_values(values).items():
        setattr(familiar, key, value)


def familiar_characteristics_fields(familiar: Familiar) -> list[DialogField]:
    return characteristics_fields(familiar.characteristics) + [
        DialogField("base_soak", "Base Soak", "int", familiar.base_soak),
        DialogField(
            "magic_resistance", "Magic Resistance", "int", familiar.magic_resistance
        ),
    ]


def apply_characteristics(familiar: Familiar, values: dict[str, Any]) -> None:
    familiar.characteristics = characteristics_from(values)
    familiar.base_soak = values["base_soak"]
    familiar.magic_resistance = values["magic_resistance"]


def edits(familiar: Familiar) -> dict[str, Form]:
    """The familiar's single-record Edit forms, by what they edit."""
    f = familiar

    def set_wounds(values: dict[str, Any]) -> None:
        f.wounds = Wounds(soak=f.wounds.soak, **values)

    def set_fatigue(values: dict[str, Any]) -> None:
        f.fatigue_level = values["level"]

    return {
        "Familiar": Form(
            "Edit Familiar", lambda: info_fields(f), lambda v: apply_info(f, v)
        ),
        "Binding & Cords": Form(
            "Edit Binding & Cords",
            lambda: binding_fields(f),
            lambda v: apply_binding(f, v),
        ),
        "Characteristics": Form(
            "Edit Characteristics",
            lambda: familiar_characteristics_fields(f),
            lambda v: apply_characteristics(f, v),
        ),
        "Wounds": Form(
            "Edit Wounds", lambda: wounds_fields(f.wounds, soak=False), set_wounds
        ),
        "Fatigue": Form(
            "Edit Fatigue Level", lambda: fatigue_fields(f.fatigue_level), set_fatigue
        ),
    }


# -- Natural Weapons --


def natural_weapon_fields(weapon: Possession | None) -> list[DialogField]:
    """One Natural Weapon: its book entry (choosing one fills in the
    book's figures), Type, Quality, Quantity, combat figures and
    Description -- the fields of a weapon possession, without Load."""
    weapons = {
        w.id: w for w in catalog.load_weapon_catalog(tables=pos.NATURAL_WEAPON_TABLES)
    }
    types = GEAR_TYPES_BY_KIND["weapon"]
    return [
        DialogField("name", "Name", "text", attr(weapon, "name", ""), required=True),
        DialogField(
            "gear_id",
            "Natural Weapon",
            "select",
            attr(weapon, "gear_id", None),
            options=[(escape(w.name), w.id) for w in weapons.values()],
            allow_blank=True,
            placeholder="(custom)",
            fills=lambda values: pos.weapon_fills(values, weapons),
        ),
        DialogField(
            "gear_type",
            "Type",
            "select",
            attr(weapon, "gear_type", types[0]) or types[0],
            options=pairs(types),
        ),
        DialogField(
            "gear_quality",
            "Quality",
            "select",
            attr(weapon, "gear_quality", GEAR_QUALITY_DEFAULT),
            options=pairs(GEAR_QUALITIES),
        ),
        DialogField("quantity", "Quantity", "int", attr(weapon, "quantity", 1)),
        DialogField("weapon_init", "Init", "int", attr(weapon, "weapon_init", 0)),
        DialogField(
            "weapon_attack",
            "Attack (blank = n/a)",
            "optint",
            attr(weapon, "weapon_attack", 0),
        ),
        DialogField(
            "weapon_defense", "Defense", "int", attr(weapon, "weapon_defense", 0)
        ),
        DialogField(
            "weapon_damage",
            "Damage (blank = n/a)",
            "optint",
            attr(weapon, "weapon_damage", 0),
        ),
        description_field(attr(weapon, "description", "")),
    ]


def natural_weapon_ops(familiar: Familiar) -> SectionOps:
    weapons = familiar.natural_weapons

    def form(index: int | None) -> Form:
        existing = weapons[index] if index is not None else None
        title = (
            "Add a Natural Weapon"
            if existing is None
            else f"Edit {escape(existing.name or 'this attack')}"
        )

        def apply(values: dict[str, Any]) -> None:
            if existing is not None:
                for key, value in values.items():
                    setattr(existing, key, value)
                return
            weapons.append(
                Possession(
                    id=storage.generate_unique_id(
                        values.get("name") or "weapon", [w.id for w in weapons]
                    ),
                    kind="weapon",
                    **values,
                )
            )

        return Form(
            title,
            lambda: natural_weapon_fields(existing),
            apply,
            validate=pos.form_problem,
            live=lambda values: pos.book_text("weapon", values.get("gear_id")),
        )

    return SectionOps(
        add=lambda: form(None),
        edit=form,
        remove=lambda index: delete(
            weapons, index, weapons[index].name or "this attack"
        ),
        rows=lambda: [w.name or "(unnamed)" for w in weapons],
    )


# -- Abilities --


def ability_fields(ability: Ability | None) -> list[DialogField]:
    """An Ability's total xp and Specialty (its name is the form's title)."""
    return [
        DialogField("xp", "XP", "int", attr(ability, "xp", 0)),
        DialogField(
            "specialty",
            "Specialty",
            "text",
            attr(ability, "specialty", None) or "",
            placeholder="e.g. Swords",
        ),
    ]


def ability_problem(values: dict[str, Any]) -> str | None:
    if values["xp"] < 0:
        return "XP can't be negative."
    return None


def ability_from(name: str, category: str, values: dict[str, Any]) -> Ability:
    return Ability(
        name=name,
        category=category,
        xp=values["xp"],
        specialty=values["specialty"] or None,
        xp_table=access.ability_xp_table(name),
    )


def ability_form(
    name: str,
    ability: Ability | None,
    virtues_flaws: Sequence[VirtueFlawInstance],
    apply: Callable[[dict[str, Any]], Any],
    *,
    save_label: str = "Save",
) -> Form:
    """An Ability's xp, with the score it buys shown live (with the
    owner's Puissant), and its Specialty; `apply` gets the values."""
    bonus, _ = scores.ability_bonus(virtues_flaws, name)
    factor = access.ability_factor(name)

    def live(values: dict[str, Any]) -> str:
        xp = values.get("xp")
        score = st.live_score(xp if isinstance(xp, int) else None, factor, bonus)
        return f"{escape(name)}: {score}"

    return Form(
        escape(name),
        lambda: ability_fields(ability),
        apply,
        validate=ability_problem,
        live=live,
        save_label=save_label,
    )


def parameter_fields(parameters: Sequence[str]) -> list[DialogField]:
    """What a templated catalog Ability ("Craft: {craft}") needs named."""
    return [
        DialogField(
            param, param.title(), "text", "", required=True, placeholder="e.g. Creo"
        )
        for param in parameters
    ]


def _ability_label(entry: AbilityDef) -> str:
    """A catalog Ability as the list of them names it, as the terminal's
    picker does: "Craft: {craft}  [General]  (needs: craft)"."""
    needs = f"  (needs: {', '.join(entry.parameters)})" if entry.parameters else ""
    return f"{entry.name}  [{entry.category}]{needs}"


def ability_choices(
    saga: Saga, held: Sequence[str], *, in_play: bool = True
) -> list[Choice]:
    """The catalog Abilities a familiar holding `held` can still take,
    from the saga's books in play and not hidden by the saga. `in_play`
    False: the others instead, marked with why (for Show everything)."""
    books = sourcebooks.saga_books(saga)
    found = []
    for entry in catalog.abilities_to_offer(held):
        why = (
            "hidden in this saga"
            if catalog.hidden(entry)
            else ""
            if sourcebooks.in_play(entry.source, books)
            else "book not in play"
        )
        if bool(why) == in_play:
            continue
        choice = Choice(
            escape(_ability_label(entry)),
            entry,
            st.ability_entry_text(entry),
            entry.category,
        )
        found.append(not_offered(choice, why) if why else choice)
    return found


def ability_ops(saga: Saga, familiar: Familiar | Creature) -> SectionOps:
    """Add, Edit and Delete for a familiar's or a creature's Abilities."""
    abilities = familiar.abilities

    def details(name: str, category: str) -> Form:
        return ability_form(
            name,
            None,
            familiar.virtues_flaws,
            lambda values: abilities.append(ability_from(name, category, values)),
            save_label="Confirm",
        )

    def chosen(entry: AbilityDef) -> Command:
        if not entry.parameters:
            return details(entry.name, entry.category)
        return Form(
            escape(entry.name),
            lambda: parameter_fields(entry.parameters),
            lambda values: details(
                catalog.resolve_ability_name(
                    entry, {p: values[p].lower() for p in entry.parameters}
                ),
                entry.category,
            ),
            save_label="Confirm",
        )

    def add() -> Choose:
        return Choose(
            "Add an Ability",
            lambda: ability_choices(saga, [a.name for a in abilities]),
            chosen,
            empty="(no more Abilities available)",
            others=lambda: ability_choices(
                saga, [a.name for a in abilities], in_play=False
            ),
        )

    def edit(index: int) -> Form:
        existing = abilities[index]

        def apply(values: dict[str, Any]) -> None:
            abilities[index] = ability_from(existing.name, existing.category, values)

        return ability_form(existing.name, existing, familiar.virtues_flaws, apply)

    return SectionOps(
        add=add,
        edit=edit,
        remove=lambda index: delete(abilities, index, abilities[index].name),
        rows=lambda: [a.name for a in abilities],
    )


# -- Bond Powers --


def bond_power_fields(power: BondPower | None) -> list[DialogField]:
    """The add/edit form for one Empowered Bond Power -- all typed-in, no
    Lab Total formula computed (see BondPower's docstring)."""

    return [
        DialogField(
            "name", "Power Name", "text", attr(power, "name", ""), required=True
        ),
        DialogField("level", "Level", "int", attr(power, "level", 0)),
        DialogField(
            "technique",
            "Technique",
            "select",
            attr(power, "technique", ""),
            options=pairs(TECHNIQUES),
            allow_blank=True,
            placeholder="(none)",
        ),
        DialogField(
            "form",
            "Form",
            "select",
            attr(power, "form", ""),
            options=pairs(FORMS),
            allow_blank=True,
            placeholder="(none)",
        ),
        DialogField(
            "target_controller",
            "Target & Controller",
            "text",
            attr(power, "target_controller", ""),
            placeholder="e.g. Magus (controlled by Familiar)",
        ),
        DialogField("uses_per_day", "Uses/Day", "int", attr(power, "uses_per_day", 0)),
        DialogField("penetration", "Penetration", "int", attr(power, "penetration", 0)),
        DialogField("vis_spent", "Vis Spent", "int", attr(power, "vis_spent", 0)),
        DialogField(
            "cosmetic_trait",
            "Cosmetic Trait Manifested",
            "text",
            attr(power, "cosmetic_trait", ""),
        ),
        DialogField(
            "instilling_progress",
            "Instilling (blank = finished)",
            "optint",
            attr(power, "instilling_progress", None),
            hint="0 to instil it as lab work (the lab's Planning tab).",
        ),
    ]


def save_bond_power(
    powers: list[BondPower], existing: BondPower | None, values: dict[str, Any]
) -> None:
    """Change `existing` to the form's `values`, or add a new power."""
    values = dict(values)
    # A blank Technique or Form is "" on a BondPower, as on the binding.
    values["technique"] = values.get("technique") or ""
    values["form"] = values.get("form") or ""
    if existing is not None:
        for key, value in values.items():
            setattr(existing, key, value)
        return
    powers.append(
        BondPower(
            id=storage.generate_unique_id(
                values.get("name") or "power", [p.id for p in powers]
            ),
            **values,
        )
    )


def bond_power_ops(familiar: Familiar) -> SectionOps:
    powers = familiar.bond_powers

    def form(index: int | None) -> Form:
        existing = powers[index] if index is not None else None
        title = (
            "Add a Bond Power"
            if existing is None
            else f"Edit {escape(existing.name) or 'this Bond Power'}"
        )
        return Form(
            title,
            lambda: bond_power_fields(existing),
            lambda values: save_bond_power(powers, existing, values),
        )

    return SectionOps(
        add=lambda: form(None),
        edit=form,
        remove=lambda index: delete(
            powers, index, powers[index].name or "this Bond Power"
        ),
        rows=lambda: [p.name or "(unnamed)" for p in powers],
    )
