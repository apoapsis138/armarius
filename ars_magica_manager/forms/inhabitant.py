"""A covenant's Inhabitants forms, independent of how they are drawn: the
form for one inhabitant of each kind and its Add, Edit and Delete
(commands.SectionOps), and the Loyalty, Inhabitants (population) and
Miscellaneous edits.

Adding a specialist, craftsperson, turb member or other covenfolk first
offers the covenant's unassigned grogs (or a new person), then the form.
"""

from __future__ import annotations

from typing import Any

from .. import catalog, covenant_diary
from .. import inhabitants as inh
from ..commands import Choice, Choose, Confirm, Form, SectionOps, notes
from ..form_spec import DialogField, description_field, pairs, year_born_field
from ..markup import escape
from ..models import (
    COVENANT_ROLES,
    CRAFT_FIELDS,
    GIFT_CHOICES,
    LOYALTY_EQUIPMENT,
    LOYALTY_MONEY,
    OTHER_COVENFOLK_ROLES,
    Arrival,
    Character,
    Covenant,
    CovenantDiaryEntry,
    Inhabitant,
    Saga,
)
from ..rules import covenfolk, derived

#: The grog chooser's first entry: someone with no character sheet.
NEW_PERSON = "(New person -- not from a character sheet)"
NEW_ANIMAL = "(New animal -- not from a character sheet)"


def new_entry_label(kind: str) -> str:
    return NEW_ANIMAL if kind in inh.ANIMAL_KINDS else NEW_PERSON


def inhabitant_fields(
    kind: str,
    entry: covenfolk.InhabitantEntry | None,
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
        fields.append(
            DialogField(
                "on_council",
                "On the council, with a full vote",
                "check",
                entry.on_council if entry else False,
                hint="An unGifted council member counts 0 in Base Loyalty's "
                "average; a token seat doesn't count (Covenants p. 38).",
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
    if kind in covenfolk.ANIMAL_POINT_KINDS:
        fields += _animal_fields(kind, entry, character)
    if kind not in covenfolk.AUTO_KINDS:
        fields.append(
            DialogField("quantity", "Quantity", "int", entry.quantity if entry else 1)
        )
    fields.append(description_field(entry.description if entry else ""))
    return fields


def _identity_fields(
    kind: str,
    entry: covenfolk.InhabitantEntry | None,
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


def _animal_fields(
    kind: str,
    entry: covenfolk.InhabitantEntry | None,
    character: Character | None,
) -> list[DialogField]:
    """An animal's Size and whether it is a carnivore, for its Points of
    Inhabitants: an animal grog's Size is its sheet's and its kind says
    whether it eats meat, so both are shown, not asked."""
    usual_size, usual_carnivore = covenfolk.ANIMAL_DEFAULTS[kind]
    if character is not None:
        size = int(derived.size(character).total)
        return [
            DialogField(
                "_sz",
                "Size",
                "info",
                f"{size:+d} (from the character sheet)"
                + (", a carnivore" if usual_carnivore else ""),
            )
        ]
    record = entry.record if entry is not None else None
    size = record.size if record is not None else None
    carnivore = record.carnivore if record is not None else None
    return [
        DialogField(
            "size",
            "Size",
            "optint",
            usual_size if size is None else size,
            required=True,
            hint="A Size +3 horse counts 1 point; each Size smaller halves "
            "it, each larger doubles it (Hermetic Projects p. 123).",
        ),
        DialogField(
            "carnivore",
            "Carnivore",
            "check",
            usual_carnivore if carnivore is None else carnivore,
            hint="A meat-eater (a hound, a cat, a hawk) counts double.",
        ),
    ]


def _covenant_role_fields(entry: covenfolk.InhabitantEntry | None) -> list[DialogField]:
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
    if entry is None or entry.role not in covenfolk.ROLE_ABILITY_MAP:
        return fields
    ability_label = " + ".join(covenfolk.ROLE_ABILITY_MAP[entry.role])
    if entry.character is not None:
        fields.append(
            DialogField(
                "_rb",
                "Loyalty Bonus",
                "info",
                f"{entry.role_bonus} (Presence {entry.role_presence:+d}"
                + (" twice" if len(covenfolk.ROLE_TASKS[entry.role]) > 1 else "")
                + f", {ability_label} {entry.role_ability_total}, from the "
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
    entry: covenfolk.InhabitantEntry | None, character: Character | None
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


def form_title(kind: str, entry: covenfolk.InhabitantEntry | None) -> str:
    """ "Add a Magus", or "Edit <their name>"."""
    singular = inh.KIND_SINGULAR[kind]
    if entry is None:
        return f"Add a {singular}"
    return f"Edit {escape(entry.name or 'this ' + singular.lower())}"


def inhabitant_form(
    covenant: Covenant,
    kind: str,
    entry: covenfolk.InhabitantEntry | None,
    grog: Character | None = None,
    year: int | None = None,
) -> Form:
    """Add (`entry` None; for `grog`, if one was chosen) or edit one
    inhabitant. A new one arrives in `year` (the saga's year, as a rule)
    unless the form says otherwise; a covenant still being created starts
    its people as here since the founding."""
    arriving = entry is None and year is not None and kind in inh.ARRIVING_KINDS

    dated = entry is not None and (
        (entry.record is not None and kind in inh.FAMILIARITY_KINDS)
        or kind in covenfolk.AUTO_KINDS
    )

    def fields() -> list[DialogField]:
        found = inhabitant_fields(kind, entry, grog)
        if dated and entry is not None:
            found += arrival_fields(covenant, entry)
        if arriving:
            found.append(
                DialogField(
                    f"{ARRIVED}new",
                    "Year arrived",
                    "optint",
                    None if covenant.in_creation else year,
                    hint="Blank: here since the covenant's founding"
                    + (f" ({covenant.year_founded})" if covenant.year_founded else "")
                    + ".",
                )
            )
        return found

    def apply(values: dict[str, Any]) -> None:
        years = {k: values.pop(k) for k in list(values) if k.startswith(ARRIVED)}
        created = entry is not None and entry.record is None
        inh.save_entry(covenant, kind, entry, values, grog)
        if arriving:
            inh.set_arrival(
                covenant, covenant.inhabitants[-1], years.get(f"{ARRIVED}new")
            )
        if dated and entry is not None:
            # A character listed from a sheet gets its record on first edit.
            record = covenant.inhabitants[-1] if created else entry.record
            if record is not None:
                redate(covenant, record, years)

    def problem(values: dict[str, Any]) -> str | None:
        arrived = sum(a.count for a in entry.arrivals) if entry is not None else 0
        if values.get("quantity", 1) < arrived:
            return (
                f"{arrived} of them are recorded as arriving later: take people "
                "away with Depart instead."
            )
        return inh.form_problem(values)

    return Form(
        form_title(kind, entry),
        fields,
        apply,
        validate=problem,
    )


#: The key that opens each arrival's year field in an edit form.
ARRIVED = "arrived_"


def arrival_fields(
    covenant: Covenant, entry: covenfolk.InhabitantEntry
) -> list[DialogField]:
    """A year for each group of a line: those here since the founding
    (blank) and each later arrival, so a group can be re-dated."""
    founded = covenant.year_founded
    if entry.kind in covenfolk.AUTO_KINDS:
        came = entry.arrivals[0].year if entry.arrivals else None
        return [
            DialogField(
                f"{ARRIVED}founding" if came is None else f"{ARRIVED}0",
                "Year arrived",
                "optint",
                came,
                hint="Blank: here since the covenant's founding"
                + (f" ({founded})" if founded else "")
                + ".",
            )
        ]
    arrived = sum(a.count for a in entry.arrivals)
    fields = []
    if entry.quantity > arrived:
        fields.append(
            DialogField(
                f"{ARRIVED}founding",
                f"Year {entry.quantity - arrived} came (here since the founding)",
                "optint",
                None,
                hint="Blank: here since the covenant's founding"
                + (f" ({founded})" if founded else "")
                + ". Type a year to date them as newcomers.",
            )
        )
    fields += [
        DialogField(
            f"{ARRIVED}{i}",
            f"Year {a.count} came",
            "optint",
            a.year,
            hint="Blank or the founding year: here since the founding.",
        )
        for i, a in enumerate(entry.arrivals)
    ]
    return fields


def redate(covenant: Covenant, record: Inhabitant, years: dict[str, Any]) -> None:
    """Re-date a line's groups from the edit form's years: a group dated at
    or before the founding (or blank) is counted as here since then, and
    groups of the same year merge. Its people stay as many."""
    founded = covenant.year_founded or 0
    groups: list[tuple[int, int | None]] = []
    arrived = sum(a.count for a in record.arrivals)
    if record.quantity > arrived:
        groups.append((record.quantity - arrived, years.get(f"{ARRIVED}founding")))
    groups += [
        (a.count, years.get(f"{ARRIVED}{i}", a.year))
        for i, a in enumerate(record.arrivals)
    ]
    by_year: dict[int, int] = {}
    for count, year in groups:
        if year is not None and year > founded:
            by_year[year] = by_year.get(year, 0) + count
    record.arrivals = [Arrival(count, year) for year, count in sorted(by_year.items())]


def recruit_form(
    saga: Saga, covenant: Covenant, entry: covenfolk.InhabitantEntry
) -> Form:
    """More people join a line: how many, and when. They dilute Familiarity
    until they grow used to the Gift (Covenants pp. 37, 40)."""
    record = entry.record
    assert record is not None  # the covenfolk lists hold only records
    name = entry.name or inh.KIND_SINGULAR[entry.kind]

    def apply(values: dict[str, Any]) -> list[str]:
        count, year = values["count"], values["year"]
        record.quantity += count
        same = next((a for a in record.arrivals if a.year == year), None)
        if same is not None:
            same.count += count
        else:
            record.arrivals.append(Arrival(count, year))
        covenant.diary.append(
            CovenantDiaryEntry(
                year,
                saga.current_season,
                f"{count} joined {name}",
                values["note"],
                category="Inhabitants",
            )
        )
        return notes(f"{count} joined {escape(name)}: now {record.quantity}.")

    return Form(
        f"Recruit to {escape(name)}",
        lambda: [
            DialogField("count", "How many joined", "int", 1, required=True),
            DialogField(
                "year", "Year they came", "int", saga.current_year, required=True
            ),
            DialogField("note", "Note", "text", ""),
        ],
        apply,
        validate=lambda values: None if values["count"] >= 1 else "At least one joins.",
        save_label="Recruit",
    )


def depart_form(
    saga: Saga, covenant: Covenant, entry: covenfolk.InhabitantEntry
) -> Form:
    """Some of a line leave: you choose which arrival they came with, how
    many, and why."""
    record = entry.record
    assert record is not None  # the covenfolk lists hold only records
    name = entry.name or inh.KIND_SINGULAR[entry.kind]
    founded = covenant.year_founded or saga.current_year
    arrived = sum(a.count for a in record.arrivals)
    groups: list[tuple[str, str, int]] = []
    if record.quantity > arrived:
        groups.append(
            (
                "founding",
                f"Here since the founding ({record.quantity - arrived})",
                record.quantity - arrived,
            )
        )
    groups += [
        (str(i), f"Joined {max(founded, a.year)} ({a.count})", a.count)
        for i, a in enumerate(record.arrivals)
    ]
    sizes = {key: size for key, _label, size in groups}

    def problem(values: dict[str, Any]) -> str | None:
        count = values["count"]
        if count < 1:
            return "At least one leaves."
        if count > sizes[values["group"]]:
            return f"That group has only {sizes[values['group']]}."
        return None

    def apply(values: dict[str, Any]) -> list[str]:
        count, group = values["count"], values["group"]
        if group != "founding":
            arrival = record.arrivals[int(group)]
            arrival.count -= count
            if not arrival.count:
                record.arrivals.remove(arrival)
        record.quantity -= count
        covenant.diary.append(
            CovenantDiaryEntry(
                saga.current_year,
                saga.current_season,
                f"{count} left {name}",
                values["why"],
                category="Inhabitants",
            )
        )
        if not record.quantity:
            covenant.inhabitants.remove(record)
            return notes(f"Everyone in {escape(name)} has gone: the line is removed.")
        return notes(f"{count} left {escape(name)}: now {record.quantity}.")

    return Form(
        f"Depart from {escape(name)}",
        lambda: [
            DialogField(
                "group",
                "Who leaves",
                "select",
                groups[0][0],
                options=[(label, key) for key, label, _size in groups],
                required=True,
            ),
            DialogField("count", "How many", "int", 1, required=True),
            DialogField(
                "why", "Why", "text", "", hint="Died of old age, dismissed, ran off..."
            ),
        ],
        apply,
        validate=problem,
        save_label="Depart",
    )


def grog_label(grog: Character) -> str:
    """A grog as the chooser lists them: name, and the year born if known."""
    return escape(grog.name) + (
        f"  (born {grog.background.year_born})" if grog.background.year_born else ""
    )


def add_inhabitant(saga: Saga, covenant: Covenant, kind: str) -> Form | Choose:
    """Add one. A grog-derived kind first offers the covenant's unassigned
    grogs (or a new person) when it has any, Horses and Hounds its animal
    grogs; Magi and Companions offer the saga's characters of that kind
    who aren't on the list (or someone with no sheet); Livestock go
    straight to the form."""
    if kind in covenfolk.AUTO_KINDS:
        return _add_from_sheets(saga, covenant, kind)
    grogs = inh.available_grogs(saga, covenant, kind) if inh.takes_grogs(kind) else []
    if not grogs:
        return inhabitant_form(covenant, kind, None, year=saga.current_year)
    return Choose(
        f"Add a {inh.KIND_SINGULAR[kind]}",
        lambda: (
            [Choice(new_entry_label(kind), None)]
            + [Choice(grog_label(g), g, search=g.name) for g in grogs]
        ),
        lambda grog: inhabitant_form(
            covenant, kind, None, grog, year=saga.current_year
        ),
    )


def _add_from_sheets(saga: Saga, covenant: Covenant, kind: str) -> Form | Choose:
    """Magi or Companions: a character of the saga who isn't on the list
    joins it (and the covenant), or a new entry with no sheet."""
    people = inh.addable_characters(saga, covenant, kind)
    if not people:
        return inhabitant_form(covenant, kind, None, year=saga.current_year)

    def label(character: Character) -> str:
        home = saga.covenant(character.covenant_id)
        if home is covenant:
            return f"{escape(character.name)}  (taken off the list)"
        if home is not None:
            return f"{escape(character.name)}  (of {escape(home.name)})"
        return escape(character.name)

    # Someone taken in now arrives now, unless the covenant is being made.
    arrival = None if covenant.in_creation else saga.current_year

    def chosen(character: Character | None) -> Form | Confirm | None:
        if character is None:
            return inhabitant_form(covenant, kind, None, year=saga.current_year)
        home = saga.covenant(character.covenant_id)
        if home is not None and home is not covenant:
            return Confirm(
                f"Move {escape(character.name)} from {escape(home.name)} to "
                f"{escape(covenant.name)}?",
                lambda: inh.take_in(covenant, kind, character, arrival),
                yes_label="Move",
            )
        inh.take_in(covenant, kind, character, arrival)
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
    covenant: Covenant, kind: str, entry: covenfolk.InhabitantEntry
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
    row's index in the section's list (covenfolk.entries_for_kind)."""

    def entries() -> list[covenfolk.InhabitantEntry]:
        return covenfolk.entries_for_kind(saga, covenant, kind)

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
            "pensioners",
            "  Pensioners (each costs half Wages)",
            "int",
            loyalty.pensioners,
            show_if=lambda v: bool(v.get("pension")),
        ),
        DialogField(
            "_sp",
            "Specialists (Presence + Ability of Steward/Chamberlain/Turb "
            "Captain/Autocrat)",
            "info",
            inh.specialists_loyalty(saga, covenant),
        ),
        DialogField(
            "familiarity",
            "Familiarity adjustment",
            "int",
            loyalty.familiarity,
            hint=f"Worked out: {inh.familiarity(saga, covenant) - loyalty.familiarity} "
            "(2 a year since the covenant's founding, at most what the Gift "
            "takes, DE p. 186); this adjusts it, e.g. for new covenfolk.",
        ),
        DialogField(
            "_rp",
            "Reputation (-5 per point of a known bad Reputation)",
            "info",
            inh.reputation_loyalty(covenant),
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
            covenfolk.other_covenfolk_count(saga, covenant, "Teamster"),
        ),
        DialogField(
            "_tn",
            "Teamsters Needed",
            "info",
            covenfolk.minimum_teamsters(saga, covenant),
        ),
        DialogField(
            "_sv",
            "Number of Servants",
            "info",
            covenfolk.other_covenfolk_count(saga, covenant, "Servant"),
        ),
        DialogField(
            "_sn", "Servants Needed", "info", covenfolk.minimum_servants(saga, covenant)
        ),
        DialogField(
            "_lb",
            "Number of Laborers",
            "info",
            covenfolk.other_covenfolk_count(saga, covenant, "Laborer"),
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
