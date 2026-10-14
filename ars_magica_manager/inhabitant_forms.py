"""A covenant's Inhabitants forms, independent of how they are drawn: the
form for one inhabitant of each kind and its Add, Edit and Delete
(commands.SectionOps), and the Loyalty, Inhabitants (population) and
Miscellaneous edits.

Adding a specialist, craftsperson, turb member or other covenfolk first
offers the covenant's unassigned grogs (or a new person), then the form.
"""

from __future__ import annotations

from typing import Any

from . import catalog, covenant_diary
from . import inhabitants as inh
from .commands import Choice, Choose, Confirm, Form, SectionOps
from .form_spec import DialogField, description_field, pairs, year_born_field
from .markup import escape
from .models import (
    COVENANT_ROLES,
    CRAFT_FIELDS,
    GIFT_CHOICES,
    LOYALTY_EQUIPMENT,
    LOYALTY_MONEY,
    OTHER_COVENFOLK_ROLES,
    Character,
    Covenant,
    Saga,
)

#: The grog chooser's first entry: someone with no character sheet.
NEW_PERSON = "(New person -- not from a character sheet)"


def inhabitant_fields(
    kind: str,
    entry: inh.InhabitantEntry | None,
    grog: Character | None,
) -> list[DialogField]:
    """The add/edit form for one kind of inhabitant. For a person listed from a
    character sheet, name/house/year are shown read-only (edit them on the
    sheet) and only the covenant-side fields are editable."""
    character = entry.character if entry is not None else grog
    fields = _identity_fields(kind, entry, grog)
    if kind in ("companion", "specialist", "craftsperson", "turb", "inhabitant"):
        fields.append(
            DialogField(
                "responsibility",
                "Responsibility",
                "text",
                entry.responsibility if entry else "",
            )
        )
    if kind in ("companion", "specialist"):
        fields += _covenant_role_fields(entry)
    if kind == "inhabitant":
        fields.append(
            DialogField(
                "role",
                "Covenant Role",
                "select",
                entry.role if entry else "",
                options=pairs(OTHER_COVENFOLK_ROLES),
                required=True,
                allow_blank=True,
                placeholder="(choose a Covenant Role)",
            )
        )
    if kind == "craftsperson":
        fields += _craftsperson_fields(entry, character)
    if kind not in inh.AUTO_KINDS:
        fields.append(
            DialogField("quantity", "Quantity", "int", entry.quantity if entry else 1)
        )
    fields.append(description_field(entry.description if entry else ""))
    return fields


def _identity_fields(
    kind: str,
    entry: inh.InhabitantEntry | None,
    grog: Character | None,
) -> list[DialogField]:
    """Name, Year Born, and House and Gift for a magus: read-only for a
    person listed from a character sheet, else editable (a new grog's
    defaults come from its character)."""
    fields: list[DialogField] = []
    if entry is not None and entry.auto:
        fields.append(
            DialogField(
                "_n", "Name", "info", f"{entry.name} (from the character sheet)"
            )
        )
        if kind == "magus":
            fields.append(
                DialogField(
                    "_h", "House", "info", inh.house_name(entry.house_id) or "Unknown"
                )
            )
        year = entry.year_born
        fields.append(
            DialogField("_y", "Year Born", "info", "Unknown" if year is None else year)
        )
        if kind == "magus":
            fields.append(DialogField("_g", "Gift", "info", entry.gift))
        return fields

    houses = [(h.name, h.id) for h in catalog.load_house_catalog()]
    name = entry.name if entry is not None else (grog.name if grog else "")
    year_born = (
        entry.year_born
        if entry is not None
        else (grog.background.year_born if grog else None)
    )
    fields.append(DialogField("name", "Name", "text", name, required=True))
    if kind == "magus":
        fields.append(
            DialogField(
                "house",
                "House",
                "select",
                entry.house_id if entry else None,
                options=houses,
                allow_blank=True,
                placeholder="Unknown",
            )
        )
    fields.append(year_born_field(year_born))
    if kind == "magus":
        fields.append(
            DialogField(
                "gift",
                "Gift",
                "select",
                entry.record.gift if entry and entry.record else "",
                options=pairs(GIFT_CHOICES),
                allow_blank=True,
                placeholder="Unknown (assumed The Gift)",
            )
        )
    return fields


def _covenant_role_fields(entry: inh.InhabitantEntry | None) -> list[DialogField]:
    """A companion's or specialist's Covenant Role, and the inputs of the
    Loyalty bonus that role earns."""
    fields = [
        DialogField(
            "role",
            "Covenant Role",
            "select",
            entry.role if entry else "",
            options=pairs(COVENANT_ROLES),
            allow_blank=True,
        )
    ]
    # Steward/Chamberlain/Turb Captain/Autocrat earn the covenant a
    # Loyalty bonus (Presence + a specific Ability). The role has to be
    # chosen and saved first -- editing again then shows this.
    if entry is None or entry.role not in inh.ROLE_ABILITY_MAP:
        return fields
    ability_label = " + ".join(inh.ROLE_ABILITY_MAP[entry.role])
    if entry.character is not None:
        fields.append(
            DialogField(
                "_rb",
                "Loyalty Bonus",
                "info",
                f"{entry.role_bonus} (Presence {entry.role_presence:+d}, "
                f"{ability_label} {entry.role_ability_total}, from the "
                "character sheet)",
            )
        )
    else:
        fields += [
            DialogField(
                "presence",
                "Presence (for the Loyalty Bonus)",
                "int",
                entry.record.presence if entry.record else 0,
            ),
            DialogField(
                "skill_value",
                f"{ability_label} (for the Loyalty Bonus)",
                "int",
                entry.record.skill_value if entry.record else 0,
            ),
        ]
    return fields


def _craftsperson_fields(
    entry: inh.InhabitantEntry | None, character: Character | None
) -> list[DialogField]:
    """A craftsperson's skill value, Field of Work, Rare and Linked Ability
    (chosen from their character's Abilities, when they have a sheet)."""
    fields: list[DialogField] = []
    from_ability = entry.skill_from_ability if entry is not None else None
    if from_ability is not None and entry is not None:
        # Tied to a sheet's Ability: the score is that Ability's Level.
        fields.append(
            DialogField(
                "_s",
                "Value of Crafting Skill",
                "info",
                f"{from_ability} (Level of {entry.linked_ability})",
            )
        )
    else:
        fields.append(
            DialogField(
                "skill_value",
                "Value of Crafting Skill",
                "int",
                entry.record.skill_value if entry and entry.record else 0,
            )
        )
    fields += [
        DialogField(
            "field_of_work",
            "Field of Work",
            "select",
            entry.field_of_work if entry else "None",
            options=pairs(CRAFT_FIELDS),
        ),
        DialogField("rare", "Rare", "check", entry.rare if entry else False),
    ]
    abilities = inh.ability_names(character)
    current = entry.linked_ability if entry else ""
    if character is not None:
        options = pairs(abilities)
        if current and current not in abilities:
            options.append((current, current))
        fields.append(
            DialogField(
                "linked_ability",
                "Linked Ability",
                "select",
                current,
                options=options,
                allow_blank=True,
            )
        )
    else:
        fields.append(DialogField("linked_ability", "Linked Ability", "text", current))
    return fields


# Add, Edit and Delete


def form_title(kind: str, entry: inh.InhabitantEntry | None) -> str:
    """ "Add a Magus", or "Edit <their name>"."""
    singular = inh.KIND_SINGULAR[kind]
    if entry is None:
        return f"Add a {singular}"
    return f"Edit {escape(entry.name or 'this ' + singular.lower())}"


def inhabitant_form(
    covenant: Covenant,
    kind: str,
    entry: inh.InhabitantEntry | None,
    grog: Character | None = None,
) -> Form:
    """Add (`entry` None; for `grog`, if one was chosen) or edit one
    inhabitant."""

    def apply(values: dict[str, Any]) -> None:
        inh.save_entry(covenant, kind, entry, values, grog)

    return Form(
        form_title(kind, entry),
        lambda: inhabitant_fields(kind, entry, grog),
        apply,
        validate=inh.form_problem,
    )


def grog_label(grog: Character) -> str:
    """A grog as the chooser lists them: name, and the year born if known."""
    return escape(grog.name) + (
        f"  (born {grog.background.year_born})" if grog.background.year_born else ""
    )


def add_inhabitant(saga: Saga, covenant: Covenant, kind: str) -> Form | Choose:
    """Add one. A grog-derived kind first offers the covenant's unassigned
    grogs (or a new person) when it has any; Magi and Companions offer the
    saga's characters of that kind who aren't on the list (or someone with
    no sheet); animals go straight to the form."""
    if kind in inh.AUTO_KINDS:
        return _add_from_sheets(saga, covenant, kind)
    grogs = inh.available_grogs(saga, covenant) if kind in inh.GROG_KINDS else []
    if not grogs:
        return inhabitant_form(covenant, kind, None)
    return Choose(
        f"Add a {inh.KIND_SINGULAR[kind]}",
        lambda: (
            [Choice(NEW_PERSON, None)]
            + [Choice(grog_label(g), g, search=g.name) for g in grogs]
        ),
        lambda grog: inhabitant_form(covenant, kind, None, grog),
    )


def _add_from_sheets(saga: Saga, covenant: Covenant, kind: str) -> Form | Choose:
    """Magi or Companions: a character of the saga who isn't on the list
    joins it (and the covenant), or a new entry with no sheet."""
    people = inh.addable_characters(saga, covenant, kind)
    if not people:
        return inhabitant_form(covenant, kind, None)

    def label(character: Character) -> str:
        home = saga.covenant(character.covenant_id)
        if home is covenant:
            return f"{escape(character.name)}  (taken off the list)"
        if home is not None:
            return f"{escape(character.name)}  (of {escape(home.name)})"
        return escape(character.name)

    def chosen(character: Character | None) -> Form | Confirm | None:
        if character is None:
            return inhabitant_form(covenant, kind, None)
        home = saga.covenant(character.covenant_id)
        if home is not None and home is not covenant:
            return Confirm(
                f"Move {escape(character.name)} from {escape(home.name)} to "
                f"{escape(covenant.name)}?",
                lambda: inh.take_in(covenant, kind, character),
                yes_label="Move",
            )
        inh.take_in(covenant, kind, character)
        return None

    return Choose(
        f"Add a {inh.KIND_SINGULAR[kind]}",
        lambda: (
            [Choice(NEW_PERSON, None)]
            + [Choice(label(c), c, search=c.name) for c in people]
        ),
        chosen,
    )


def remove_inhabitant(
    covenant: Covenant, kind: str, entry: inh.InhabitantEntry
) -> Confirm:
    """Delete one, after confirming. Someone listed from a character sheet
    is not deleted: they stop counting as an inhabitant, still in the
    covenant on their sheet."""
    name = escape(entry.name or "this entry")
    if entry.auto and entry.character is not None:
        return Confirm(
            f"Remove {name} from the {inh.KIND_TITLES[kind]} list?\n\n"
            "They stay in the covenant on their character sheet, but "
            "will no longer count as an inhabitant.",
            lambda: inh.mark_departed(covenant, kind, entry),
            yes_label="Remove",
        )

    def apply() -> None:
        if entry.record in covenant.inhabitants:
            covenant.inhabitants.remove(entry.record)

    return Confirm(f"Delete {name}?", apply)


def inhabitant_ops(saga: Saga, covenant: Covenant, kind: str) -> SectionOps:
    """The Inhabitants section of `kind`: Add, Edit and Delete, by the
    row's index in the section's list (inhabitants.entries_for_kind)."""

    def entries() -> list[inh.InhabitantEntry]:
        return inh.entries_for_kind(saga, covenant, kind)

    return SectionOps(
        add=lambda: add_inhabitant(saga, covenant, kind),
        edit=lambda index: inhabitant_form(covenant, kind, entries()[index]),
        remove=lambda index: remove_inhabitant(covenant, kind, entries()[index]),
        rows=lambda: [e.name or "(unnamed)" for e in entries()],
    )


# Loyalty, the household's numbers and Miscellaneous


def loyalty_fields(saga: Saga, covenant: Covenant) -> list[DialogField]:
    """The Loyalty block: what is typed or chosen, and what is worked out
    shown beside it."""
    loyalty = covenant.loyalty
    styles = inh.governance_names(covenant)
    if styles:
        governance = DialogField(
            "_g",
            "Type of Governance",
            "info",
            f"{', '.join(styles)} (from your Boons)",
        )
    else:
        governance = DialogField(
            "governance", "Type of Governance", "text", loyalty.governance
        )
    base = inh.base_loyalty(saga, covenant)
    modifiers = inh.total_modifiers(saga, covenant)
    return [
        governance,
        DialogField("_bp", "Base Loyalty Points", "info", base),
        DialogField("_tm", "Total modifiers", "info", modifiers),
        DialogField("_cp", "Current Loyalty Points", "info", base + modifiers),
        DialogField(
            "_ps",
            "Prevailing Loyalty Score",
            "info",
            inh.prevailing_loyalty_score(base + modifiers),
        ),
        DialogField(
            "_lc",
            "Living Conditions (from the covenant's Living Conditions (Mundane))",
            "info",
            inh.living_conditions_loyalty(covenant),
        ),
        DialogField(
            "equipment",
            "Equipment",
            "select",
            loyalty.equipment,
            options=pairs(LOYALTY_EQUIPMENT),
        ),
        DialogField(
            "money",
            "Money",
            "select",
            loyalty.money,
            options=pairs(LOYALTY_MONEY),
        ),
        DialogField(
            "pension",
            "  Pension? (half Wages until death)",
            "check",
            loyalty.pension,
        ),
        DialogField(
            "_sp",
            "Specialists (Presence + Ability of Steward/Chamberlain/Turb "
            "Captain/Autocrat)",
            "info",
            inh.specialists_loyalty(saga, covenant),
        ),
        DialogField("familiarity", "Familiarity", "int", loyalty.familiarity),
        DialogField(
            "_rp",
            "Reputation (-5 per point of a known bad Reputation)",
            "info",
            inh.reputation_loyalty_penalty(covenant),
        ),
        DialogField(
            "actions_and_events",
            "Actions and events (manual, on top of the Diary's "
            f"{covenant_diary.diary_loyalty(covenant):+d})",
            "int",
            loyalty.actions_and_events,
        ),
        DialogField(
            "magical_influence",
            "Magical Influence",
            "int",
            loyalty.magical_influence,
        ),
    ]


def population_fields(saga: Saga, covenant: Covenant) -> list[DialogField]:
    """The household's numbers: only Other People is typed."""
    pop = covenant.population
    return [
        DialogField(
            "_tm",
            "Number of Teamsters",
            "info",
            inh.other_covenfolk_count(saga, covenant, "Teamster"),
        ),
        DialogField(
            "_tn", "Teamsters Needed", "info", inh.minimum_teamsters(saga, covenant)
        ),
        DialogField(
            "_sv",
            "Number of Servants",
            "info",
            inh.other_covenfolk_count(saga, covenant, "Servant"),
        ),
        DialogField(
            "_sn", "Servants Needed", "info", inh.minimum_servants(saga, covenant)
        ),
        DialogField(
            "_lb",
            "Number of Laborers",
            "info",
            inh.other_covenfolk_count(saga, covenant, "Laborer"),
        ),
        DialogField("other_people", "Other People", "int", pop.other_people),
        DialogField(
            "_t",
            "Total Inhabitants",
            "info",
            f"{inh.total_inhabitants(saga, covenant)} (calculated)",
        ),
    ]


def misc_fields(covenant: Covenant) -> list[DialogField]:
    """Aging modifiers and magical help with the household's work."""
    pop = covenant.population
    return [
        DialogField("aging_magi", "Aging for Magi", "int", pop.aging_magi),
        DialogField("aging_mundane", "Aging for Mundane", "int", pop.aging_mundane),
        DialogField("magic_laborers", "Magic Laborers", "int", pop.magic_laborers),
        DialogField("magic_servants", "Magic Servants", "int", pop.magic_servants),
        DialogField("magic_teamsters", "Magic Teamsters", "int", pop.magic_teamsters),
        DialogField("magic_turbula", "Magic Turbula", "int", pop.magic_turbula),
    ]


def _set_all(record: Any) -> Any:
    def apply(values: dict[str, Any]) -> None:
        for key, value in values.items():
            setattr(record, key, value)

    return apply


def loyalty_form(saga: Saga, covenant: Covenant) -> Form:
    return Form(
        "Edit Loyalty",
        lambda: loyalty_fields(saga, covenant),
        _set_all(covenant.loyalty),
    )


def population_form(saga: Saga, covenant: Covenant) -> Form:
    return Form(
        "Edit Inhabitants",
        lambda: population_fields(saga, covenant),
        _set_all(covenant.population),
    )


def misc_form(covenant: Covenant) -> Form:
    return Form(
        "Edit Miscellaneous",
        lambda: misc_fields(covenant),
        _set_all(covenant.population),
    )
