"""Forms for a covenant's records: its inhabitants, possessions, vis and
income sources, Improve Income, and the covenant's own details."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Label, Select, Static

from ... import catalog
from ... import economics as eco
from ... import inhabitants as inh
from ... import possessions as pos
from ... import sheet_text as st
from ...arts import ARTS
from ...markup import escape
from ...models import (
    COVENANT_ROLES,
    CRAFT_FIELDS,
    GEAR_QUALITIES,
    GEAR_QUALITY_DEFAULT,
    GEAR_TYPES_BY_KIND,
    GIFT_CHOICES,
    INCOME_EFFECTS,
    OTHER_COVENFOLK_ROLES,
    REALMS,
    SANCTUM_USAGE_DEFAULT,
    SANCTUM_USAGES,
    SEASONS,
    Ability,
    Character,
    Covenant,
    IncomeSource,
)
from ..fields import (
    DialogField,
    FieldsDialog,
    ModalDialog,
    _attr,
    _description_field,
    _pairs,
    _year_born_field,
)
from ..pickers import AbilityPickerScreen
from ..prompts import ConfirmScreen


def _inhabitant_fields(
    kind: str,
    entry: inh.InhabitantEntry | None,
    grog: Character | None,
) -> list[DialogField]:
    """The add/edit form for one kind of inhabitant. For a person listed from a
    character sheet, name/house/year are shown read-only (edit them on the
    sheet) and only the covenant-side fields are editable."""
    character = entry.character if entry is not None else grog
    fields = _inhabitant_identity_fields(kind, entry, grog)
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
                options=_pairs(OTHER_COVENFOLK_ROLES),
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
    fields.append(_description_field(entry.description if entry else ""))
    return fields


def _inhabitant_identity_fields(
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
    fields.append(_year_born_field(year_born))
    if kind == "magus":
        fields.append(
            DialogField(
                "gift",
                "Gift",
                "select",
                entry.record.gift if entry and entry.record else "",
                options=_pairs(GIFT_CHOICES),
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
            options=_pairs(COVENANT_ROLES),
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
            options=_pairs(CRAFT_FIELDS),
        ),
        DialogField("rare", "Rare", "check", entry.rare if entry else False),
    ]
    abilities = inh.ability_names(character)
    current = entry.linked_ability if entry else ""
    if character is not None:
        options = _pairs(abilities)
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


def _possession_dialog(
    title: str,
    kind: str,
    entry: pos.PossessionEntry | None,
    *,
    natural: bool = False,
    places: Sequence[tuple[str, str]] = (),
    place: str = "",
) -> FieldsDialog[dict[str, Any]]:
    """The add/edit form for one kind of possession (a covenant's, a
    character's Personal Gear, or -- `natural` -- a familiar's Natural
    Weapons). A weapon or armor form shows the chosen book entry in its live
    line. A Raw Vis Store's asks where it is kept: one of `places`
    (vis.location_options), `place` to start with."""
    return FieldsDialog(
        title,
        _possession_fields(kind, entry, natural=natural, places=places, place=place),
        validate=pos.form_problem,
        live=(
            (lambda values: pos.book_text(kind, values.get("gear_id")))
            if kind in GEAR_TYPES_BY_KIND
            else None
        ),
    )


def _possession_fields(
    kind: str,
    entry: pos.PossessionEntry | None,
    *,
    natural: bool = False,
    places: Sequence[tuple[str, str]] = (),
    place: str = "",
) -> list[DialogField]:
    """The add/edit form for one kind of possession. For a laboratory listed as
    a sanctum, name/owner/location/build points are shown read-only (edit them
    on the laboratory) and only the covenant-side fields are editable."""
    auto = entry is not None and entry.auto
    fields = (
        _sanctum_from_lab_fields(kind, entry)
        if auto and entry is not None
        else [
            DialogField("name", "Name", "text", _attr(entry, "name", ""), required=True)
        ]
    )
    if kind == "property":
        fields += _property_fields(entry)
    elif kind == "sanctum":
        fields += _sanctum_fields(entry, auto)
    elif kind in pos.QUANTITY_KINDS:
        fields += _quantity_possession_fields(kind, entry, natural=natural)
    elif kind in ("vis_source", "vis_store"):
        fields += _vis_possession_fields(kind, entry, places, place)

    if kind != "vis_store":
        fields.append(_description_field(_attr(entry, "description", "")))
    return fields


def _sanctum_from_lab_fields(
    kind: str, entry: pos.PossessionEntry
) -> list[DialogField]:
    """The read-only fields of a possession listed from a laboratory."""
    note = " (from the laboratory)"
    fields = [
        DialogField("_n", "Name", "info", entry.name + note),
        DialogField("_o", "Owner", "info", (entry.owner or "(none)") + note),
        DialogField("_l", "Location", "info", entry.location or "(not set)"),
        DialogField(
            "_b",
            "Build Points",
            "info",
            "(not set)" if entry.build_points is None else entry.build_points,
        ),
    ]
    if kind == "sanctum":
        fields.append(DialogField("_q", "Quality", "info", str(entry.quality) + note))
        fields.append(
            DialogField("_u", "Upkeep (Points)", "info", str(entry.upkeep) + note)
        )
    return fields


def _property_fields(entry: pos.PossessionEntry | None) -> list[DialogField]:
    return [
        DialogField("location", "Location", "text", _attr(entry, "location", "")),
        DialogField("dimensions", "Dimensions", "text", _attr(entry, "dimensions", "")),
        DialogField(
            "inhabitants", "Inhabitants", "text", _attr(entry, "inhabitants", "")
        ),
    ]


def _sanctum_fields(entry: pos.PossessionEntry | None, auto: bool) -> list[DialogField]:
    """A sanctum's covenant-side fields; one listed from a laboratory keeps
    only Usage editable."""
    fields: list[DialogField] = []
    if not auto:
        fields += [
            # Unowned sanctums are "Free": narratively, visitors can use them.
            DialogField("owner", "Owner", "text", _attr(entry, "owner", "Free")),
            DialogField("location", "Location", "text", _attr(entry, "location", "")),
            DialogField("quality", "Quality", "optint", _attr(entry, "quality", None)),
            DialogField(
                "upkeep", "Upkeep (Points)", "optint", _attr(entry, "upkeep", None)
            ),
            DialogField(
                "build_points",
                "Build Points",
                "optint",
                _attr(entry, "build_points", None),
            ),
        ]
    fields.append(
        DialogField(
            "usage",
            "Usage",
            "select",
            _attr(entry, "usage", SANCTUM_USAGE_DEFAULT),
            options=_pairs(SANCTUM_USAGES),
        )
    )
    return fields


def _gear_book_field(
    kind: str, entry: pos.PossessionEntry | None, natural: bool
) -> DialogField:
    """The weapon's or armor Material's book entry: choosing one fills in
    the book's figures (see possessions.weapon_fills/armor_fills)."""
    if kind == "weapon":
        tables = pos.NATURAL_WEAPON_TABLES if natural else pos.GEAR_WEAPON_TABLES
        weapons = {w.id: w for w in catalog.load_weapon_catalog(tables=tables)}
        options = [
            (escape(w.name if natural else f"{w.name} ({w.ability})"), w.id)
            for w in weapons.values()
        ]
        label = "Natural Weapon" if natural else "Weapon"

        def fills(values: dict[str, Any]) -> dict[str, Any]:
            return pos.weapon_fills(values, weapons)

    else:
        armors = {a.id: a for a in catalog.load_armor_catalog()}
        options = [
            (
                escape(a.name + (" (partial only)" if a.figures(True) is None else "")),
                a.id,
            )
            for a in armors.values()
        ]
        label = "Material"

        def fills(values: dict[str, Any]) -> dict[str, Any]:
            return pos.armor_fills(values, armors)

    return DialogField(
        "gear_id",
        label,
        "select",
        _attr(entry, "gear_id", None),
        options=options,
        allow_blank=True,
        placeholder="(custom)",
        fills=fills,
    )


def _quantity_possession_fields(
    kind: str, entry: pos.PossessionEntry | None, *, natural: bool = False
) -> list[DialogField]:
    """The book entry, Type and Quality (gear kinds), Quantity, and a
    weapon's or armor's combat figures."""
    fields: list[DialogField] = []
    if kind in GEAR_TYPES_BY_KIND:
        types = GEAR_TYPES_BY_KIND[kind]
        book = _gear_book_field(kind, entry, natural)
        fields += [
            book,
            DialogField(
                "gear_type",
                "Type",
                "select",
                _attr(entry, "gear_type", types[0]) or types[0],
                options=_pairs(types),
                # Partial or full armor changes the book's figures.
                fills=book.fills if kind == "armor" else None,
            ),
            DialogField(
                "gear_quality",
                "Quality",
                "select",
                _attr(entry, "gear_quality", GEAR_QUALITY_DEFAULT),
                options=_pairs(GEAR_QUALITIES),
            ),
        ]
    fields.append(
        DialogField("quantity", "Quantity", "int", _attr(entry, "quantity", 1))
    )
    if kind == "weapon":
        fields += [
            DialogField("weapon_init", "Init", "int", _attr(entry, "weapon_init", 0)),
            DialogField(
                "weapon_attack",
                "Attack (blank = n/a)",
                "optint",
                _attr(entry, "weapon_attack", 0),
            ),
            DialogField(
                "weapon_defense", "Defense", "int", _attr(entry, "weapon_defense", 0)
            ),
            DialogField(
                "weapon_damage",
                "Damage (blank = n/a)",
                "optint",
                _attr(entry, "weapon_damage", 0),
            ),
        ]
    elif kind == "armor":
        fields.append(
            DialogField(
                "armor_protection",
                "Protection",
                "int",
                _attr(entry, "armor_protection", 0),
            )
        )
    if kind in GEAR_TYPES_BY_KIND and not natural:
        fields.append(DialogField("load", "Load", "int", _attr(entry, "load", 0)))
    return fields


def _vis_possession_fields(
    kind: str,
    entry: pos.PossessionEntry | None,
    places: Sequence[tuple[str, str]] = (),
    place: str = "",
) -> list[DialogField]:
    """Art, Season harvested (a source), Pawns, Kept at (a store, one of
    `places`), Location and Physical Form."""
    fields = [
        DialogField(
            "art",
            "Art",
            "select",
            _attr(entry, "art", ""),
            options=_pairs(ARTS),
            required=True,
            allow_blank=True,
            placeholder="(choose an Art)",
        )
    ]
    if kind == "vis_source":
        fields.append(
            DialogField(
                "season",
                "Season harvested",
                "select",
                _attr(entry, "season", ""),
                options=_pairs(SEASONS),
                required=True,
                allow_blank=True,
                placeholder="(choose a Season)",
            )
        )
        # The Hooks are on the record: a PossessionEntry has no such fields.
        fields += _contested_fields(entry.record if entry is not None else None)
    fields.append(DialogField("pawns", "Pawns", "int", _attr(entry, "pawns", 1) or 1))
    if kind == "vis_store" and places:
        fields.append(
            DialogField(
                "place",
                "Kept at",
                "select",
                place,
                options=list(places),
                required=True,
                hint="The covenant, one of its laboratories, or one of its "
                "characters. Location says where exactly.",
            )
        )
    fields += [
        DialogField("location", "Location", "text", _attr(entry, "location", "")),
        DialogField(
            "physical_form",
            "Physical Form",
            "text",
            _attr(entry, "physical_form", ""),
        ),
    ]
    return fields


def _contested_fields(entry: Any) -> list[DialogField]:
    """A vis or income source's Contested / Dwindling Resource Hooks."""
    return [
        DialogField(
            "contested",
            "Contested Resource",
            "check",
            bool(_attr(entry, "contested", False)),
            hint="Covered by a Contested or Indiscreet Resource Hook: advancing "
            "asks whether it was secured once its security lapses.",
        ),
        DialogField(
            "secured_until",
            "Secured through (year)",
            "optint",
            _attr(entry, "secured_until", None),
            show_if=lambda values: bool(values.get("contested")),
            hint="A story secures it for five years.",
        ),
        DialogField(
            "dwindling",
            "Dwindling Resource (gone in 10 years)",
            "check",
            bool(_attr(entry, "dwindling", False)),
        ),
    ]


#: Edit Covenant's whole-number fields after Year Founded, as (attribute,
#: label).
_COVENANT_INT_FIELDS: tuple[tuple[str, str], ...] = (
    ("aegis_of_the_hearth", "Aegis of the Hearth"),
    ("aegis_penetration", "Aegis' Penetration"),
    ("living_conditions_magi", "Living Conditions (Magi)"),
    ("living_conditions_mundane", "Living Conditions (Mundane)"),
    ("aura", "Aura"),
)


def _covenant_fields(covenant: Covenant) -> list[DialogField]:
    cov = covenant
    return [
        DialogField("name", "Name", "text", cov.name, required=True),
        DialogField("tribunal", "Tribunal", "text", cov.tribunal),
        DialogField("year_founded", "Year Founded", "optint", cov.year_founded),
        *(
            DialogField(
                attribute,
                label,
                "int",
                getattr(cov, attribute),
                hint=(
                    "The base aura of every laboratory in this covenant."
                    if attribute == "aura"
                    else ""
                ),
            )
            for attribute, label in _COVENANT_INT_FIELDS
        ),
        DialogField(
            "aura_realm",
            "Aura Realm",
            "select",
            cov.aura_realm,
            options=_pairs(REALMS),
            hint="Hermetic magic gains the full aura only in a Magic aura.",
        ),
        DialogField(
            "covenant_season",
            "Covenant Season",
            "select",
            cov.covenant_season,
            options=_pairs(SEASONS),
        ),
    ]


class ImproveIncomeScreen(ModalDialog[tuple[int, str] | None]):
    """Manually simulates a year's Income Modification (ArM5's automated/
    yearly advancement isn't built yet -- this is a deliberate stand-in for
    it). Choosing an Effect updates the Multiplier and Projected Income live;
    Commit confirms via ConfirmScreen, then dismisses with (new income, the
    Note to record), or None if cancelled."""

    DEFAULT_CSS = """
    ImproveIncomeScreen {
        align: center middle;
    }

    #improve-dialog {
        width: 70;
        height: auto;
        padding: 1 2;
    }

    .improve-row {
        width: 100%;
        height: 1;
    }

    .improve-label {
        width: 26;
    }

    .improve-value {
        width: 1fr;
        color: $text-muted;
    }

    #improve-effect {
        width: 1fr;
    }

    #improve-note-label {
        margin-top: 1;
        height: 1;
    }

    #improve-note {
        color: $text-muted;
        height: auto;
    }

    #improve-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #improve-buttons {
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, source: IncomeSource, current_year: int) -> None:
        super().__init__()
        self.source = source
        self.current_year = current_year

    def compose(self) -> ComposeResult:
        source = self.source
        with Vertical(id="improve-dialog", classes="dialog-box"):
            yield Label(
                f"Improve {source.name or 'this source of income'}",
                id="improve-title",
                classes="dialog-title",
            )
            with Horizontal(classes="improve-row"):
                yield Label("Name", classes="improve-label")
                yield Static(
                    escape(source.name or "(unnamed)"), classes="improve-value"
                )
            with Horizontal(classes="improve-row"):
                yield Label("Current Income", classes="improve-label")
                yield Static(str(source.current_income), classes="improve-value")
            with Horizontal(classes="improve-row"):
                yield Label("Annual Improvement Effect", classes="improve-label")
                yield Select(
                    _pairs(INCOME_EFFECTS),
                    value="Status Quo",
                    id="improve-effect",
                    compact=True,
                )
            with Horizontal(classes="improve-row"):
                yield Label("Income Multiplier", classes="improve-label")
                yield Static(
                    eco.income_multiplier_text("Status Quo"),
                    classes="improve-value",
                    id="improve-multiplier",
                )
            with Horizontal(classes="improve-row"):
                yield Label("Projected Income", classes="improve-label")
                yield Static(
                    str(source.current_income),
                    classes="improve-value",
                    id="improve-projected",
                )
            yield Label("Note", id="improve-note-label")
            yield Static(
                escape(source.note.strip()) if source.note.strip() else "(none)",
                id="improve-note",
            )
            yield Static("", id="improve-error")
            with Horizontal(id="improve-buttons"):
                yield Button("Commit", id="btn-commit", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.action_cancel()
        elif event.button.id == "btn-commit":
            self._try_commit()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id != "improve-effect" or not isinstance(event.value, str):
            return
        effect = event.value
        self.query_one("#improve-multiplier", Static).update(
            eco.income_multiplier_text(effect)
        )
        self.query_one("#improve-projected", Static).update(
            str(eco.projected_income(self.source.current_income, effect))
        )

    def _try_commit(self) -> None:
        effect = self.query_one("#improve-effect", Select).value
        if not isinstance(effect, str):
            self.query_one("#improve-error", Static).update("Choose an Effect.")
            return
        current = self.source.current_income
        projected = eco.projected_income(current, effect)
        note = eco.improvement_note(
            self.current_year, self.source.name, effect, current, projected
        )
        name = escape(self.source.name or "this source of income")

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                self.dismiss((projected, note))

        self.app.push_screen(
            ConfirmScreen(
                f"Update {name}'s income from {current} to {projected}?",
                yes_label="Update",
            ),
            handle_confirmed,
        )


def _bought_ability(value: Any) -> tuple[str, str]:
    """The (name, category) of a Buy a Specialist form's Ability: an
    Ability from the picker, or a name."""
    if isinstance(value, Ability):
        return value.name, value.category
    name = str(value or "")
    definition = st.ability_definition(name)
    return name, definition.category if definition else ""


def _buy_specialist_dialog(
    books: frozenset[str] | None = None,
) -> FieldsDialog[tuple[str, dict[str, Any]]]:
    """Someone bought with Build Points for a new covenant: an NPC defined
    by the Ability they serve with, from the Ability picker. A teacher costs
    Communication + Teaching + the highest Ability taught; anyone else their
    score. Which covenfolk category they join follows from the Ability
    (inhabitants.bought_kind): a Craft makes a craftsperson, a Martial
    Ability the turb. Builds (kind, an Inhabitant's fields)."""

    def teacher(values: dict[str, Any]) -> bool:
        return bool(values.get("teacher"))

    def kind(values: dict[str, Any]) -> str:
        name, category = _bought_ability(values.get("linked_ability"))
        return inh.bought_kind(name, category, teacher=teacher(values))

    def cost(values: dict[str, Any]) -> int:
        total = values.get("specialist_score") or 0
        if teacher(values):
            total += (values.get("teacher_communication") or 0) + (
                values.get("teacher_teaching") or 0
            )
        return total

    def live(values: dict[str, Any]) -> str:
        if not values.get("linked_ability"):
            return f"Costs {cost(values)} Build Points"
        return (
            f"Joins the {inh.KIND_TITLES[kind(values)]}. "
            f"Costs {cost(values)} Build Points"
        )

    def problem(values: dict[str, Any]) -> str | None:
        if not values.get("linked_ability"):
            return "Choose the Ability they serve the covenant with."
        if values["specialist_score"] < 0:
            return "The score can't be negative."
        return None

    def build(values: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        which = kind(values)
        name, _ = _bought_ability(values["linked_ability"])
        is_teacher = values.pop("teacher")
        rare = values.pop("rare", False)
        field = values.pop("field_of_work", None) or "None"
        values["linked_ability"] = name
        if not is_teacher:
            values["teacher_communication"] = None
            values["teacher_teaching"] = None
        else:
            values["role"] = "Teacher"
        if which == "craftsperson":
            values["rare"] = bool(rare)
            values["field_of_work"] = field
            values["skill_value"] = values["specialist_score"]
        return which, values

    def craft(values: dict[str, Any]) -> bool:
        return kind(values) == "craftsperson"

    def picker(current: Any) -> AbilityPickerScreen:
        return AbilityPickerScreen(books=books, ask_details=False)

    return FieldsDialog(
        "Buy a Specialist",
        [
            DialogField("name", "Name", "text", "", required=True),
            DialogField("teacher", "A teacher", "check", False),
            DialogField(
                "linked_ability",
                "Ability used for the covenant",
                "picker",
                None,
                placeholder="(choose an Ability)",
                picker=picker,
                display=lambda value: _bought_ability(value)[0],
                hint="A teacher: the highest Ability taught.",
            ),
            DialogField("specialist_score", "Its score", "int", 1),
            DialogField("rare", "A rare craft", "check", False, show_if=craft),
            DialogField(
                "field_of_work",
                "Saves money on",
                "select",
                "None",
                options=_pairs(CRAFT_FIELDS),
                show_if=craft,
            ),
            DialogField(
                "teacher_communication", "Communication", "int", 0, show_if=teacher
            ),
            DialogField("teacher_teaching", "Teaching", "int", 1, show_if=teacher),
            DialogField("year_born", "Year Born", "optint", None),
        ],
        validate=problem,
        live=live,
        save_label="Buy",
        build=build,
    )
