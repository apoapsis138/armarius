"""Form builders for the records (DialogField lists for FieldsDialog) and the
bespoke forms that aren't FieldsDialogs: Arts, Spell Mastery, Binding & Cords,
Improve Income and the import screens. Enchanted devices and their effects
are at the end."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import replace
from pathlib import Path
from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Input,
    Label,
    ListItem,
    ListView,
    OptionList,
    Select,
    Static,
)
from textual.widgets.option_list import Option

from .. import books as bk
from .. import catalog, faith, seasons, sourcebooks, storage
from .. import economics as eco
from .. import enchanted_devices as ed
from .. import familiars as fam
from .. import inhabitants as inh
from .. import lab_texts as lt
from .. import laboratories as lab_rules
from .. import possessions as pos
from .. import spells as spl
from ..arts import ART_ABBREVIATIONS, ARTS, FORMS, TECHNIQUES
from ..markup import escape
from ..models import (
    BOOK_TYPES,
    CHARGED,
    COMPANION_TYPES,
    CORD_SCORE_COSTS,
    COVENANT_ROLES,
    CRAFT_FIELDS,
    DEVICE_PAYMENTS,
    DEVICE_TYPES,
    EFFECT_EXPIRIES,
    EFFECT_FREQUENCIES,
    ENCHANT_MATERIALS,
    ENCHANT_SIZES,
    FATIGUE_LEVELS,
    FEATURE_VIRTUE_POINTS,
    GEAR_QUALITIES,
    GEAR_QUALITY_DEFAULT,
    GEAR_TYPES_BY_KIND,
    GIFT_CHOICES,
    INCOME_EFFECTS,
    INVESTED,
    LAB_CHARACTERISTICS,
    LAB_TEXT_KINDS,
    LESSER,
    MATERIAL_SIZE_CITATION,
    OTHER_COVENFOLK_ROLES,
    REALMS,
    SANCTUM_USAGE_DEFAULT,
    SANCTUM_USAGES,
    SEASONS,
    SPELL_DURATIONS,
    SPELL_RANGES,
    SPELL_TARGETS,
    TEXT_ENCHANTMENT,
    TEXT_LONGEVITY,
    TEXT_OTHER,
    TEXT_SPELL,
    TRACTATUS_SUBJECTS,
    Aging,
    ArtScore,
    Background,
    BondPower,
    Book,
    Breakthrough,
    Character,
    Characteristics,
    Covenant,
    Description,
    DeviceComponent,
    EnchantedDevice,
    Familiar,
    GrogYear,
    HermeticBackground,
    IncomeSource,
    InstilledEffect,
    KnownSpell,
    LabCharacteristics,
    LabFeature,
    Laboratory,
    MasteryAbility,
    Saga,
    SeasonPlan,
    ShapeMaterialBonus,
    Spell,
    Wounds,
    XpAllocation,
    new_instance_id,
)
from ..rules import (
    apprentice_seasons,
    book_seasons,
    creation_characteristics,
    experiment,
    laboratory_seasons,
    spell_levels,
    supplement_seasons,
)
from ..rules import options as rule_options
from ..rules import seasons as season_rules
from .fields import (
    _EMPHASIS_HINT,
    DialogField,
    FieldsDialog,
    ModalDialog,
    _attr,
    _covenant_options,
    _description_field,
    _pairs,
    _year_born_field,
)
from .pickers import (
    ShapeMaterialPickerScreen,
    SourcebookPickerScreen,
    SpellChooserScreen,
)
from .prompts import ConfirmScreen, ListFieldScreen, _mastery_ability_dialog


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
    """A vis or income source's Contested / Dwindling Resource Hooks
    (STORY-906)."""
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
            "Dwindling Resource (-10% a year)",
            "check",
            bool(_attr(entry, "dwindling", False)),
        ),
    ]


def _saga_fields(saga: Saga | None) -> list[DialogField]:
    """The Create Saga form (with the starting date) or, given a saga, its
    Edit Saga form."""
    fields = [
        DialogField(
            "name",
            "Name",
            "text",
            _attr(saga, "name", ""),
            required=True,
            placeholder="e.g. Dammerstein",
        ),
        DialogField(
            "storyguide",
            "Storyguide",
            "text",
            _attr(saga, "storyguide", ""),
            required=True,
            placeholder="e.g. Alex",
        ),
    ]
    if saga is None:
        fields += [
            DialogField("year", "Start Year", "int", 1220),
            DialogField(
                "season", "Start Season", "select", SEASONS[0], options=_pairs(SEASONS)
            ),
        ]
    fields.append(
        DialogField(
            "description",
            "Description",
            "text",
            _attr(saga, "description", ""),
            placeholder="A one-line premise for the saga",
        )
    )
    if saga is not None:
        fields.append(
            DialogField(
                "keep_season_records",
                "Keep season records",
                "check",
                saga.keep_season_records,
                hint="A record of each season as it is applied, listed under Seasons in the tree. Off: only the Diaries keep them.",
            )
        )
        fields.append(
            DialogField(
                "books_in_play",
                "Books in play",
                "picker",
                saga.books_in_play,
                placeholder=sourcebooks.summary(None),
                picker=SourcebookPickerScreen,
                display=sourcebooks.summary,
                hint="Catalog pickers hide entries from books not in play.",
            )
        )
        fields += [
            DialogField(
                RULE_OPTION_PREFIX + option.key,
                option.label,
                "check",
                rule_options.is_on(saga, option.key),
                hint=f"Optional rule, off by default. {option.effect}",
            )
            for option in rule_options.OPTIONS
        ]
    return fields


#: Saga-form keys for the optional rules: the prefix plus the option's key.
RULE_OPTION_PREFIX = "rule_option__"


def saga_rule_options(values: dict[str, Any]) -> dict[str, bool]:
    """The optional rules chosen on the saga form, taken out of `values` (so
    what's left are plain Saga fields)."""
    chosen = {
        key.removeprefix(RULE_OPTION_PREFIX): bool(values.pop(key))
        for key in list(values)
        if key.startswith(RULE_OPTION_PREFIX)
    }
    return rule_options.normalized(chosen)


def _covenant_create_fields() -> list[DialogField]:
    return [
        DialogField(
            "name", "Name", "text", "", required=True, placeholder="e.g. Fengheld"
        ),
        DialogField(
            "notes",
            "Notes",
            "text",
            "",
            placeholder="A one-line note about the covenant",
        ),
    ]


#: The kinds of character, as Select options.
_CHARACTER_TYPES: list[tuple[str, str]] = [
    ("Magus", "magus"),
    ("Companion", "companion"),
    ("Mythic Companion", "mythic companion"),
    ("Grog", "grog"),
]


def _covenant_field(saga: Saga, covenant_id: str | None) -> DialogField:
    """An optional choice of covenant."""
    return DialogField(
        "covenant_id",
        "Covenant",
        "select",
        covenant_id,
        options=_covenant_options(saga),
        allow_blank=True,
        placeholder="(no covenant)",
    )


def _character_create_fields(saga: Saga, covenant_id: str | None) -> list[DialogField]:
    return [
        DialogField(
            "name", "Name", "text", "", required=True, placeholder="e.g. Leandro"
        ),
        DialogField("type", "Type", "select", "magus", options=_CHARACTER_TYPES),
        _covenant_field(saga, covenant_id),
    ]


def _laboratory_create_fields(saga: Saga, covenant_id: str | None) -> list[DialogField]:
    return [
        DialogField(
            "name",
            "Name",
            "text",
            "",
            required=True,
            placeholder="e.g. The Alchemical Tower",
        ),
        DialogField("size", "Size", "int", 0),
        _covenant_field(saga, covenant_id),
        DialogField(
            "starting",
            "One of the covenant's starting labs",
            "check",
            _covenant_in_creation(saga, covenant_id),
            hint="Paid for from the covenant's Build Points (one free per magus).",
        ),
    ]


def _covenant_in_creation(saga: Saga, covenant_id: str | None) -> bool:
    covenant = saga.covenant(covenant_id)
    return covenant is not None and covenant.in_creation


def _familiar_create_fields(saga: Saga, magus_id: str | None) -> list[DialogField]:
    """Name the Familiar and choose its magus (one with no Familiar yet)."""
    return [
        DialogField(
            "name", "Name", "text", "", required=True, placeholder="e.g. Ashwing"
        ),
        DialogField(
            "character_id",
            "Magus Partner",
            "select",
            magus_id,
            options=[(escape(c.name), c.id) for c in fam.unbonded_magi(saga)],
            required=True,
            allow_blank=True,
            placeholder="(choose a magus)",
        ),
    ]


#: The eight Characteristics as (label, attribute), in the book's order.
_CHARACTERISTIC_FIELDS: list[tuple[str, str]] = [
    ("Intelligence (Int)", "intelligence"),
    ("Perception (Per)", "perception"),
    ("Presence (Pre)", "presence"),
    ("Communication (Com)", "communication"),
    ("Strength (Str)", "strength"),
    ("Stamina (Sta)", "stamina"),
    ("Dexterity (Dex)", "dexterity"),
    ("Quickness (Qik)", "quickness"),
]


def _characteristics_fields(characteristics: Characteristics) -> list[DialogField]:
    return [
        DialogField(attribute, label, "int", getattr(characteristics, attribute))
        for label, attribute in _CHARACTERISTIC_FIELDS
    ]


def _characteristics_dialog(
    saga: Saga, character: Character
) -> FieldsDialog[dict[str, Any]]:
    """Edit Characteristics. While the character is In Creation the form
    shows the points spent and left as each score is typed (STORY-1316)."""
    return FieldsDialog(
        "Edit Characteristics",
        _characteristics_fields(character.characteristics),
        live=(
            (
                lambda values: creation_characteristics.points_text(
                    saga, character, values
                )
            )
            if character.in_creation
            else None
        ),
    )


def _characteristics_from(values: dict[str, Any]) -> Characteristics:
    return Characteristics(
        **{attribute: values[attribute] for _, attribute in _CHARACTERISTIC_FIELDS}
    )


def _character_info_fields(saga: Saga, character: Character) -> list[DialogField]:
    """The top panel's Edit form: name, a companion's type (Companion or
    Mythic Companion), covenant, a magus's laboratory, and the Background
    figures shown there."""
    b = character.background
    fields = [
        DialogField("name", "Name", "text", character.name, required=True),
    ]
    if character.type in COMPANION_TYPES:
        fields.append(
            DialogField(
                "type",
                "Type",
                "select",
                character.type,
                options=[t for t in _CHARACTER_TYPES if t[1] in COMPANION_TYPES],
            )
        )
    fields += [
        DialogField(
            "covenant_id",
            "Covenant",
            "select",
            character.covenant_id,
            options=_covenant_options(saga),
            allow_blank=True,
            placeholder="(unassigned)",
        ),
    ]
    if character.type == "magus":
        fields.append(
            DialogField(
                "laboratory_id",
                "Assigned Laboratory",
                "select",
                character.assigned_lab_id,
                options=[(escape(lab.name), lab.id) for lab in saga.laboratories],
                allow_blank=True,
                placeholder="(unassigned)",
            )
        )
    return fields + [
        DialogField("setting", "Setting", "text", b.setting),
        DialogField("confidence_score", "Confidence Score", "int", b.confidence_score),
        DialogField(
            "confidence_points", "Confidence Points", "int", b.confidence_points
        ),
        DialogField(
            "true_faith_score",
            "True Faith Score",
            "int",
            b.true_faith_score,
            hint="Only with the True Faith Virtue; 2+ is a Mythic Companion.",
        ),
        DialogField("faith_points", "Faith Points", "int", b.faith_points),
        DialogField("size", "Size", "int", b.size),
    ]


def _character_info_dialog(saga: Saga, character: Character) -> FieldsDialog:
    """Edit Character Info, warning (not refusing) as the True Faith Score
    is typed if the character can't have it (faith.faith_warnings)."""

    def live(values: dict[str, Any]) -> str:
        score = values.get("true_faith_score") or 0
        kind = values.get("type") or character.type
        warnings = faith.faith_warnings(character, score, kind)
        return "\n".join(f"[$text-error]{escape(w)}[/]" for w in warnings)

    return FieldsDialog(
        "Edit Character Info", _character_info_fields(saga, character), live=live
    )


_HANDEDNESS_OPTIONS: list[tuple[str, str]] = [
    ("Right", "right"),
    ("Left", "left"),
    ("Ambidextrous", "ambidextrous"),
]


#: Biographical Detail's free-text Background fields, as (label, attribute).
_BIOGRAPHY_TEXT_FIELDS: list[tuple[str, str]] = [
    ("Player", "player"),
    ("Birth Name", "birth_name"),
]


_BIOGRAPHY_TEXT_FIELDS_AFTER_YEAR: list[tuple[str, str]] = [
    ("Race/Nationality", "race_nationality"),
    ("Place of Origin", "place_of_origin"),
    ("Religion", "religion"),
    ("Title/Profession", "title_profession"),
]


def _biographical_fields(
    background: Background, description: Description
) -> list[DialogField]:
    """The Background fields not in the top panel, then every Description
    field."""
    d = description
    return [
        *(
            DialogField(attribute, label, "text", getattr(background, attribute))
            for label, attribute in _BIOGRAPHY_TEXT_FIELDS
        ),
        _year_born_field(background.year_born),
        *(
            DialogField(attribute, label, "text", getattr(background, attribute))
            for label, attribute in _BIOGRAPHY_TEXT_FIELDS_AFTER_YEAR
        ),
        DialogField("height", "Height", "optfloat", d.height),
        DialogField("weight", "Weight", "optfloat", d.weight),
        DialogField("hair", "Hair", "text", d.hair),
        DialogField("eyes", "Eyes", "text", d.eyes),
        DialogField(
            "handedness",
            "Handedness",
            "select",
            d.handedness,
            options=_HANDEDNESS_OPTIONS,
        ),
        DialogField(
            "physical_description",
            "Physical Description",
            "text",
            d.physical_description,
        ),
        DialogField("biography", "Biography", "area", d.biography, hint=_EMPHASIS_HINT),
    ]


def _aging_fields(aging: Aging) -> list[DialogField]:
    return [
        DialogField("decrepitude", "Decrepitude", "int", aging.decrepitude),
        DialogField("effects", "Effects of Aging", "text", aging.effects),
        DialogField("warping_score", "Warping Score", "int", aging.warping_score),
        DialogField("warping_points", "Warping Points", "int", aging.warping_points),
        DialogField(
            "gain_warping",
            "Gain Warping Points now",
            "int",
            0,
            hint="From one event (a powerful effect, a botch...): 2 or more "
            "take a magus to the edge of Wizard's Twilight, rolled at once.",
        ),
    ]


def _wounds_fields(wounds: Wounds, *, soak: bool = True) -> list[DialogField]:
    """Wound counts and Incapacitated/Dead; a character's Soak too (a
    Familiar's lives with its Characteristics instead)."""
    fields = (
        [
            DialogField(
                "soak",
                "Soak adjustment",
                "int",
                wounds.soak,
                hint="Added to the Soak worked out from Stamina, armour and Virtues.",
            )
        ]
        if soak
        else []
    )
    return fields + [
        DialogField("light", "Light Wounds (-1 each)", "int", wounds.light),
        DialogField("medium", "Medium Wounds (-3 each)", "int", wounds.medium),
        DialogField("heavy", "Heavy Wounds (-5 each)", "int", wounds.heavy),
        DialogField("incapacitated", "Incapacitated", "check", wounds.incapacitated),
        DialogField("dead", "Dead", "check", wounds.dead),
    ]


def _fatigue_fields(level: str) -> list[DialogField]:
    return [
        DialogField(
            "level",
            "Level",
            "select",
            level,
            options=[(level.title(), level) for level in FATIGUE_LEVELS],
        )
    ]


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
        title=(
            values.get("title") or ""
            if activity in (book_seasons.WRITE_SUMMA, book_seasons.WRITE_TRACTATUS)
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
            else values.get("mystery_virtue")
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
    for key, value in _supplement_plan_values(activity, values).items():
        setattr(plan, key, value)
    return plan


#: The supplement activities that give experience (STORY-913, 918-923).
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


def _supplement_plan_values(activity: str, values: dict[str, Any]) -> dict[str, Any]:
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
        found["device_id"] = values.get("ordeal_flaw")
        found["research_kind"] = values.get("ordeal_size") or "Minor"
    if activity == "inspeximus":
        found["book_id"] = values.get("summa_id")
    return found


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
    catalog_vfs = catalog.load_virtue_flaw_catalog()
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
        DialogField(
            "mystery_virtue",
            "Virtue initiated",
            "select",
            plan.effect_id if plan else None,
            options=[(escape(e.name), e.id) for e in catalog_vfs if e.type == "Virtue"],
            allow_blank=True,
            show_if=activity_is("undergo_initiation"),
        ),
        DialogField(
            "ordeal_flaw",
            "Ordeal Flaw (if any)",
            "select",
            plan.device_id if plan else None,
            options=[(escape(e.name), e.id) for e in catalog_vfs if e.type == "Flaw"],
            allow_blank=True,
            show_if=activity_is("undergo_initiation"),
        ),
        DialogField(
            "ordeal_size",
            "Ordeal size",
            "select",
            (plan.research_kind if plan else "") or "Minor",
            options=[(o, o) for o in ("Minor", "Medium", "Major")],
            show_if=activity_is("undergo_initiation"),
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
    """A grog's yearly update (STORY-924, Grogs Ch. 5): what the training,
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

    return FieldsDialog(
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


#: What reaching a research goal grants (Breakthrough.grant_kind).
GRANT_KINDS = [
    ("An Ability (the points become its xp)", "Ability"),
    ("A Virtue", "Virtue"),
    ("A new parameter (the troupe records it)", "Parameter"),
]


def _breakthrough_dialog(existing: Breakthrough | None) -> FieldsDialog[Breakthrough]:
    """A magus's original research goal (STORY-916; Hedda 2026-09-30): what it
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


def _season_plan_dialog(
    saga: Saga, character: Character, existing: SeasonPlan | None
) -> FieldsDialog[SeasonPlan]:
    """Plan `character`'s current season (STORY-903): the activity, what
    its experience goes into, and notes. The line above Save shows what the
    season will give, worked out as the form is filled in."""
    activities = season_rules.activities_for(character)
    options = seasons.subject_options(saga, character)
    shares = existing.allocations if existing else []

    def activity_is(*keys: str) -> Callable[[dict[str, Any]], bool]:
        return lambda values: values.get("activity") in keys

    def share(n: int) -> XpAllocation | None:
        return shares[n - 1] if len(shares) >= n else None

    subject_fields: list[DialogField] = []
    for n in range(1, season_rules.MAX_SUBJECTS + 1):
        allocation = share(n)
        if n == 1:
            shown = activity_is(
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
            shown = activity_is(season_rules.EXPOSURE, season_rules.ADVENTURE)
        else:
            shown = activity_is(season_rules.ADVENTURE)
        subject_fields.append(
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
        subject_fields.append(
            DialogField(
                f"points_{n}",
                f"Source Quality to ({n})",
                "optint",
                allocation.points if allocation and allocation.points else None,
                show_if=activity_is(season_rules.ADVENTURE),
            )
        )
    fields = [
        DialogField(
            "activity",
            "Activity",
            "select",
            existing.activity if existing else None,
            options=[(a.label, a.key) for a in activities],
            required=True,
            hint="The line above Save shows what the season will give.",
        ),
        DialogField(
            "source_quality",
            "Source Quality",
            "optint",
            existing.source_quality if existing else None,
            show_if=activity_is(
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
            existing.book_id if existing else None,
            options=[
                (escape(seasons.book_label(b)), b.id)
                for b in bk.studyable_books(saga, character)
            ],
            allow_blank=True,
            show_if=activity_is(season_rules.READ),
            hint="The covenant's library and the character's own books.",
        ),
        DialogField(
            "teacher_id",
            "Teacher / master",
            "select",
            existing.teacher_id if existing else None,
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
            show_if=activity_is(
                season_rules.TAUGHT,
                season_rules.TRAINED,
                laboratory_seasons.ASSIST,
                "undergo_initiation",
                "record_lectures",
            ),
            hint="A teacher plans Teach for the same season; the magus you "
            "assist plans lab work.",
        ),
        *subject_fields,
        DialogField(
            "title",
            "Title",
            "text",
            existing.title if existing else "",
            placeholder="blank: named for its subject",
            show_if=activity_is(book_seasons.WRITE_SUMMA, book_seasons.WRITE_TRACTATUS),
        ),
        DialogField(
            "book_level",
            "Summa Level (blank: the most)",
            "optint",
            existing.book_level if existing else None,
            show_if=activity_is(book_seasons.WRITE_SUMMA),
            hint="Each Level below the most adds Quality (+1, +3 for an Ability).",
        ),
        DialogField(
            "language",
            "Language",
            "text",
            (existing.language if existing else "") or "Latin",
            show_if=activity_is(
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
            existing.book_id if existing else None,
            options=[
                (escape(seasons.book_label(b)), b.id)
                for b in bk.studyable_books(saga, character)
            ],
            allow_blank=True,
            show_if=activity_is(book_seasons.COPY_BOOK, book_seasons.TRANSLATE_BOOK),
        ),
        DialogField(
            "quick",
            "Quick copy (x3, Quality -1)",
            "check",
            existing.quick if existing else False,
            show_if=activity_is(book_seasons.COPY_BOOK),
        ),
        DialogField(
            "text_id",
            "Lab Text",
            "select",
            existing.book_id if existing else None,
            # Every text he can get at: one he can't read yet says so, and
            # the season refuses it with the reason (STORY-508).
            options=[
                (escape(b.name + lt.cant_read_tag(saga, character, b)), b.id)
                for b in saga.books
                if b.type == "Lab Text" and bk.can_read(saga, character, b)
            ],
            allow_blank=True,
            show_if=activity_is(book_seasons.COPY_TEXTS),
        ),
        DialogField(
            "student_id",
            "Student",
            "select",
            existing.subject_id if existing else None,
            options=[
                (escape(c.name), c.id)
                for c in saga.characters
                if c.id != character.id and c.type != "grog"
            ],
            allow_blank=True,
            show_if=activity_is(
                book_seasons.TEACH_ABBREVIATIONS,
                apprentice_seasons.OPEN_ARTS,
                apprentice_seasons.TEACH_VIRTUE,
            ),
        ),
        DialogField(
            "research",
            "Research goal",
            "text",
            existing.research if existing else "",
            show_if=activity_is(experiment.INTEGRATE),
        ),
        DialogField(
            "research_kind",
            "Breakthrough",
            "select",
            (existing.research_kind if existing else "") or "Minor",
            options=[(k, k) for k in experiment.KINDS],
            show_if=activity_is(experiment.INTEGRATE),
        ),
        *_supplement_fields(saga, character, existing, activity_is),
        DialogField(
            "virtue_id",
            "Hermetic Virtue",
            "select",
            existing.effect_id if existing else None,
            options=apprentice_seasons.teachable_virtues(character),
            allow_blank=True,
            show_if=activity_is(apprentice_seasons.TEACH_VIRTUE),
        ),
        DialogField(
            "vis_from",
            "Vis from",
            "select",
            (existing.vis_from if existing else "") or "character",
            options=[
                ("Their own raw vis", "character"),
                ("Their laboratory's raw vis", "laboratory"),
                ("Their covenant's vis stores", "covenant"),
            ],
            show_if=activity_is(season_rules.VIS_STUDY),
        ),
        DialogField(
            "die",
            "Stress die (blank: rolled)",
            "optint",
            existing.die if existing else None,
            show_if=activity_is(
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
            existing.months_lost if existing else 0,
            show_if=activity_is(
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
            existing.details if existing else "",
            hint=_EMPHASIS_HINT,
        ),
    ]

    def problem(values: dict[str, Any]) -> str | None:
        plan = _season_plan_from(saga, character, values)
        found = season_rules.problems(character, plan, saga)
        if not found and plan.activity == season_rules.OTHER and not plan.details:
            return "Say in Notes what the season is spent on."
        return found[0] if found else None

    return FieldsDialog(
        f"Plan {escape(character.name)}'s Season "
        f"({saga.current_season} {saga.current_year})",
        fields,
        validate=problem,
        live=lambda values: seasons.live_text(
            saga, character, _season_plan_from(saga, character, values)
        ),
        build=lambda values: _season_plan_from(saga, character, values),
    )


def _hermetic_fields(hermetic: HermeticBackground) -> list[DialogField]:
    h = hermetic
    return [
        DialogField(
            "house",
            "House",
            "select",
            h.house,
            options=[(house.name, house.id) for house in catalog.load_house_catalog()],
            allow_blank=True,
            placeholder="(none selected)",
        ),
        DialogField("domus_magna", "Domus Magna", "text", h.domus_magna),
        DialogField("primus", "Primus", "text", h.primus),
        DialogField("parens", "Parens", "text", h.parens),
        DialogField(
            "covenant_of_apprenticeship",
            "Covenant of Apprenticeship",
            "text",
            h.covenant_of_apprenticeship,
        ),
        DialogField(
            "age_of_apprenticeship",
            "Age of Apprenticeship",
            "optint",
            h.age_of_apprenticeship,
        ),
        DialogField("wizards_sigil", "Wizard's Sigil", "area", h.wizards_sigil),
    ]


def _familiar_characteristics_fields(familiar: Familiar) -> list[DialogField]:
    return _characteristics_fields(familiar.characteristics) + [
        DialogField("base_soak", "Base Soak", "int", familiar.base_soak),
        DialogField(
            "magic_resistance", "Magic Resistance", "int", familiar.magic_resistance
        ),
    ]


def _familiar_info_fields(familiar: Familiar) -> list[DialogField]:
    f = familiar
    return [
        DialogField("name", "Name", "text", f.name, required=True),
        DialogField("species", "Species / Description", "text", f.species),
        DialogField(
            "season_bound",
            "Season Bound",
            "select",
            f.season_bound or None,
            options=_pairs(SEASONS),
            allow_blank=True,
            placeholder="(not set)",
        ),
        DialogField("year_bound", "Year Bound", "optint", f.year_bound),
        DialogField("magic_might", "Magic Might Score", "int", f.magic_might),
        DialogField("might_pool", "Current Might Pool", "optint", f.might_pool),
        DialogField("size", "Size", "int", f.size),
        DialogField("wound_multiplier", "Wound Multiplier", "int", f.wound_multiplier),
    ]


def _lab_identity_fields(saga: Saga, lab: Laboratory) -> list[DialogField]:
    return [
        DialogField("name", "Name", "text", lab.name, required=True),
        DialogField("location", "Location", "text", lab.location),
        DialogField("aura_modifier", "Aura modifier", "int", lab.aura_modifier),
        DialogField(
            "sanctum_marked",
            "Sanctum marked",
            "check",
            lab.sanctum_marked,
            hint="Its boundary is marked (a circle within a square).",
        ),
        DialogField(
            "covenant_id",
            "Covenant",
            "select",
            lab.covenant_id,
            options=_covenant_options(saga),
            allow_blank=True,
            placeholder="(unassigned)",
        ),
        DialogField(
            "owner_id",
            "Owner",
            "select",
            lab.owner_id,
            options=_lab_owner_options(saga, lab.owner_id),
            allow_blank=True,
            placeholder="(unassigned)",
        ),
    ]


def _lab_owner_options(saga: Saga, owner_id: str | None) -> list[tuple[str, str]]:
    """The magi, plus the current owner if they aren't one (any more): they
    stay the owner unless changed."""
    options = [(escape(c.name), c.id) for c in saga.characters if c.type == "magus"]
    owner = saga.character(owner_id)
    if owner is not None and owner.type != "magus":
        options.append((f"{escape(owner.name)} ({owner.type})", owner.id))
    return options


def _lab_characteristics_fields(
    characteristics: LabCharacteristics,
) -> list[DialogField]:
    return [
        DialogField(
            name,
            name.replace("_", " ").title(),
            "int",
            getattr(characteristics, name),
        )
        for name in LAB_CHARACTERISTICS
    ]


#: The Feature form's Virtue choice for adding a new Feature Virtue along
#: with the Feature: this prefix, then the Virtue's catalog id.
NEW_FEATURE_VIRTUE = "new:"


def _feature_virtue_options(
    lab: Laboratory, feature: LabFeature | None
) -> list[tuple[str, str]]:
    """The Feature Virtues a Feature can be built on (the free ones, "#2"
    telling apart two of a kind, the one it's on marked "(current)"), then
    adding a new Lesser or Greater one."""
    free = lab_rules.free_feature_virtues(lab, feature)
    options = []
    for vf in free:
        same = [other for other in free if other.vf_id == vf.vf_id]
        number = f" #{same.index(vf) + 1}" if len(same) > 1 else ""
        current = " (current)" if feature and vf.id == feature.virtue_id else ""
        options.append(
            (f"{lab_rules.tier_word(vf.vf_id)} Feature{number}{current}", vf.id)
        )
    for vf_id, points in FEATURE_VIRTUE_POINTS.items():
        options.append(
            (
                f"New {lab_rules.tier_word(vf_id)} Feature Virtue "
                f"({points} {'point' if points == 1 else 'points'})",
                NEW_FEATURE_VIRTUE + vf_id,
            )
        )
    return options


def _lab_feature_type_dialog(
    lab: Laboratory, feature: LabFeature | None = None
) -> FieldsDialog[tuple[str | None, str]]:
    """First step of adding or editing a Feature: which Feature it is (from
    the catalog, or Custom) and the Feature Virtue it's built on. Gives
    (catalog id or None for Custom, a VirtueFlawInstance id or
    NEW_FEATURE_VIRTUE + a catalog id)."""
    virtue_options = _feature_virtue_options(lab, feature)
    if feature is not None:
        feature_type = feature.feature_id or "custom"
        virtue = feature.virtue_id
    else:
        feature_type = None
        virtue = virtue_options[0][1]  # a free one if there is one
    return FieldsDialog(
        "Add a Feature" if feature is None else "Edit a Feature",
        [
            DialogField(
                "feature_type",
                "Feature",
                "select",
                feature_type,
                options=[(f.name, f.id) for f in catalog.load_lab_feature_catalog()]
                + [("Custom (any Activity or Art)", "custom")],
                required=True,
                allow_blank=True,
                placeholder="(choose a Feature)",
            ),
            DialogField(
                "virtue",
                "Built on",
                "select",
                virtue,
                options=virtue_options,
                required=True,
                allow_blank=True,
                placeholder="(choose a Feature Virtue)",
                hint="A Lesser Feature gives 1 point, a Greater Feature 3.",
            ),
        ],
        save_label="Next",
        build=lambda values: (
            None if values["feature_type"] == "custom" else values["feature_type"],
            values["virtue"],
        ),
    )


def _lab_feature_dialog(
    lab: Laboratory,
    feature_id: str | None,
    virtue_vf_id: str,
    feature: LabFeature | None = None,
) -> FieldsDialog[dict[str, Any]]:
    """Second step: the Feature's name, one Specialization per point its
    Virtue gives (the same one twice for 2 points), and -- when the lab has
    a matching Focus Flaw no other Feature holds -- whether it's the Focus,
    with a Specialization per Focus point. Every point must be placed, and
    only on the Specializations the Feature offers."""
    options = _pairs(lab_rules.feature_options(feature_id))
    offered = {value for _, value in options}
    definition = catalog.load_lab_feature_catalog_by_id().get(feature_id or "")
    budget = FEATURE_VIRTUE_POINTS[virtue_vf_id]
    tier = lab_rules.tier_word(virtue_vf_id)

    def placed(grants: list[Any], count: int) -> list[str | None]:
        points = [p for p in lab_rules.points_from_grants(grants) if p in offered]
        return [*points[:count], *[None] * (count - len(points))]

    def point_fields(
        key: str, label: str, values: list[str | None], **extra: Any
    ) -> list[DialogField]:
        return [
            DialogField(
                f"{key}{n}",
                f"{label} {n + 1}" if len(values) > 1 else label,
                "select",
                value,
                options=options,
                required=True,
                allow_blank=True,
                placeholder="(choose a Specialization)",
                **extra,
            )
            for n, value in enumerate(values)
        ]

    fields = [
        DialogField(
            "name",
            "Name",
            "text",
            feature.name if feature else (definition.name if definition else ""),
            required=True,
            placeholder="e.g. Large Brass Cauldron",
        ),
        DialogField(
            "_type",
            "Feature",
            "info",
            f"{definition.name if definition else 'Custom'} ({tier} Feature, "
            f"{budget} {'point' if budget == 1 else 'points'})",
        ),
        *point_fields(
            "point", "Point", placed(feature.allocations if feature else [], budget)
        ),
    ]
    focus_count = 0
    if lab_rules.can_focus(lab, feature, virtue_vf_id):
        focus_count = lab_rules.focus_points(virtue_vf_id)
        was_focus = feature is not None and feature.focus
        fields.append(
            DialogField(
                "focus",
                "Focus",
                "check",
                was_focus,
                hint=(
                    f"The lab's {tier} Focus is built around it: {focus_count} "
                    f"more points, -{1 if tier == 'Lesser' else 2} General "
                    "Quality on activities it doesn't aid."
                ),
            )
        )
        fields += point_fields(
            "focus_point",
            "Focus point",
            placed(
                feature.focus_allocations if was_focus and feature else [], focus_count
            ),
            show_if=lambda values: bool(values.get("focus")),
        )

    def build(values: dict[str, Any]) -> dict[str, Any]:
        focus = bool(values.get("focus"))
        return {
            "name": values["name"],
            "allocations": lab_rules.grants_from_points(
                values[f"point{n}"] for n in range(budget)
            ),
            "focus": focus,
            "focus_allocations": lab_rules.grants_from_points(
                values[f"focus_point{n}"] for n in range(focus_count)
            )
            if focus
            else [],
        }

    return FieldsDialog(
        "Add a Feature" if feature is None else "Edit a Feature",
        fields,
        save_label="Add" if feature is None else "Save",
        build=build,
    )


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


def _bond_power_fields(power: BondPower | None) -> list[DialogField]:
    """The add/edit form for one Empowered Bond Power -- all typed-in, no
    Lab Total formula computed (see BondPower's docstring)."""

    return [
        DialogField(
            "name", "Power Name", "text", _attr(power, "name", ""), required=True
        ),
        DialogField("level", "Level", "int", _attr(power, "level", 0)),
        DialogField(
            "technique",
            "Technique",
            "select",
            _attr(power, "technique", ""),
            options=_pairs(TECHNIQUES),
            allow_blank=True,
            placeholder="(none)",
        ),
        DialogField(
            "form",
            "Form",
            "select",
            _attr(power, "form", ""),
            options=_pairs(FORMS),
            allow_blank=True,
            placeholder="(none)",
        ),
        DialogField(
            "target_controller",
            "Target & Controller",
            "text",
            _attr(power, "target_controller", ""),
            placeholder="e.g. Magus (controlled by Familiar)",
        ),
        DialogField("uses_per_day", "Uses/Day", "int", _attr(power, "uses_per_day", 0)),
        DialogField(
            "penetration", "Penetration", "int", _attr(power, "penetration", 0)
        ),
        DialogField("vis_spent", "Vis Spent", "int", _attr(power, "vis_spent", 0)),
        DialogField(
            "cosmetic_trait",
            "Cosmetic Trait Manifested",
            "text",
            _attr(power, "cosmetic_trait", ""),
        ),
        DialogField(
            "instilling_progress",
            "Instilling (blank = finished)",
            "optint",
            _attr(power, "instilling_progress", None),
            hint="0 to instil it as lab work (the lab's Planning tab).",
        ),
    ]


def _ability_template_prefix(name: str) -> str | None:
    """ "Area Lore: " for a templated catalog name like "Area Lore: {region}"."""
    return name.split("{", 1)[0] if "{" in name else None


def _book_ability_choice(ability: str, names: list[str]) -> tuple[str, str]:
    """(Ability select value, Ability detail) for a book's stored ability: a
    catalog name as is, or a templated family plus the filled-in blank."""
    if not ability or ability in names:
        return ability, ""
    for name in names:
        prefix = _ability_template_prefix(name)
        if prefix and ability.startswith(prefix):
            return name, ability[len(prefix) :]
    return ability, ""  # not in the catalog: kept as its own option


def _book_fields(
    saga: Saga, book: Book | None, default_owner: str, default_type: str = ""
) -> list[DialogField]:
    """The add/edit form for a book. Which of Art/Ability/Spell, Level and
    Quality are shown follows the Type (and a Tractatus's Subject) live; a
    Lab Text's follow its Kind too (STORY-508): a spell's text names the
    spell, any other its own Technique, Form and Level, with an
    enchantment's effect and device or a Longevity Ritual's subject. A new
    book starts as `default_type` (the Lab Texts list adds Lab Texts)."""

    ability_names = [a.name for a in catalog.load_ability_catalog()]
    ability, ability_detail = _book_ability_choice(
        _attr(book, "ability", ""), ability_names
    )
    ability_options = _pairs(ability_names)
    if ability and ability not in ability_names:
        ability_options.insert(0, (ability, ability))

    def book_type(values: dict[str, Any]) -> str:
        return values.get("type") or ""

    def art_book(values: dict[str, Any]) -> bool:
        return bk.is_art_book(book_type(values), values.get("subject_kind") or "")

    def ability_book(values: dict[str, Any]) -> bool:
        return bk.is_ability_book(book_type(values), values.get("subject_kind") or "")

    def templated(values: dict[str, Any]) -> bool:
        return ability_book(values) and "{" in (values.get("ability") or "")

    # A Lab Text / Casting Tablet takes its spell's Level; only a General (or
    # not yet chosen) spell needs the book's own.
    linked = bk.book_spell(saga, book) if book is not None else None
    spell_id = linked.id if linked is not None else None

    def spell_display(chosen_id: str) -> str:
        spell = spl.find_spell(saga, chosen_id)
        if spell is None:
            return chosen_id
        return f"{spell.name}  ({spl.shorthand(spell)})"

    def lab_text(values: dict[str, Any]) -> bool:
        return book_type(values) == "Lab Text"

    def text_kind(values: dict[str, Any]) -> str:
        return (values.get("text_kind") or TEXT_SPELL) if lab_text(values) else ""

    def of_spell(values: dict[str, Any]) -> bool:
        return bk.records_spell(book_type(values), text_kind(values))

    def needs_level(values: dict[str, Any]) -> bool:
        kind = book_type(values)
        if kind not in bk.SPELL_TYPES:
            return bk.has_level(kind)
        if not of_spell(values):
            return True  # an enchantment's, a ritual's: the text's own
        spell = spl.find_spell(saga, values.get("spell_id"))
        if spell is None:
            # No spell chosen: ask for the spell first -- unless this is a book
            # whose typed spell is unknown, which keeps its own Level.
            return bool(_attr(book, "spell_name", ""))
        return spell.level is None

    if book is None:
        owner = default_owner
    elif bk.is_unassigned(saga, book):
        owner = ""
    else:
        owner = bk.owner_value(book.owner_kind, book.owner_id)
    return [
        DialogField("name", "Name", "text", _attr(book, "name", ""), required=True),
        DialogField(
            "type",
            "Type",
            "select",
            _attr(book, "type", default_type),
            options=_pairs(BOOK_TYPES),
            required=True,
            allow_blank=True,
            placeholder="(choose a Type)",
        ),
        DialogField(
            "text_kind",
            "Kind",
            "select",
            _attr(book, "text_kind", "") or TEXT_SPELL,
            options=_pairs(LAB_TEXT_KINDS),
            show_if=lab_text,
        ),
        DialogField(
            "subject_kind",
            "Subject",
            "select",
            _attr(book, "subject_kind", ""),
            options=_pairs(TRACTATUS_SUBJECTS),
            required=True,
            allow_blank=True,
            placeholder="(Art or Ability)",
            show_if=lambda v: book_type(v) == "Tractatus",
        ),
        DialogField(
            "art",
            "Art",
            "select",
            _attr(book, "art", ""),
            options=_pairs(ARTS),
            required=True,
            allow_blank=True,
            placeholder="(choose an Art)",
            show_if=art_book,
        ),
        DialogField(
            "ability",
            "Ability",
            "select",
            ability,
            options=ability_options,
            required=True,
            allow_blank=True,
            placeholder="(choose an Ability)",
            show_if=ability_book,
        ),
        DialogField(
            "ability_detail",
            "Ability detail",
            "text",
            ability_detail,
            placeholder="fills the {blank}, e.g. Rhine Tribunal",
            show_if=templated,
        ),
        DialogField(
            "spell_id",
            "Spell",
            "picker",
            spell_id,
            placeholder=(
                f"Unknown: {_attr(book, 'spell_name', '')} -- choose the spell..."
                if spell_id is None and _attr(book, "spell_name", "")
                else "(choose the spell...)"
            ),
            picker=lambda _current: SpellChooserScreen(saga),
            display=spell_display,
            show_if=of_spell,
        ),
        DialogField(
            "technique",
            "Technique",
            "select",
            _attr(book, "technique", ""),
            options=_pairs(TECHNIQUES),
            allow_blank=True,
            placeholder="(not recorded)",
            show_if=lambda v: text_kind(v) in (TEXT_ENCHANTMENT, TEXT_OTHER),
        ),
        DialogField(
            "form",
            "Form",
            "select",
            _attr(book, "form", ""),
            options=_pairs(FORMS),
            allow_blank=True,
            placeholder="(not recorded)",
            show_if=lambda v: text_kind(v) in (TEXT_ENCHANTMENT, TEXT_OTHER),
        ),
        DialogField(
            "level",
            "Level",
            "optint",
            _attr(book, "level", None),
            required=True,
            hint="",
            show_if=needs_level,
        ),
        DialogField(
            "quality",
            "Quality",
            "optint",
            _attr(book, "quality", None),
            required=True,
            show_if=lambda v: bk.has_quality(book_type(v)),
        ),
        DialogField(
            "effect_rdt",
            "Range / Duration / Target",
            "text",
            _attr(book, "effect_rdt", ""),
            placeholder="Touch / Sun / Individual",
            show_if=lambda v: text_kind(v) == TEXT_ENCHANTMENT,
        ),
        DialogField(
            "device_type",
            "Device",
            "select",
            _attr(book, "device_type", ""),
            options=_pairs((*DEVICE_TYPES, "Talisman")),
            allow_blank=True,
            placeholder="(not recorded)",
            show_if=lambda v: text_kind(v) == TEXT_ENCHANTMENT,
        ),
        DialogField(
            "shape_material",
            "Shape and material",
            "text",
            _attr(book, "shape_material", ""),
            show_if=lambda v: text_kind(v) == TEXT_ENCHANTMENT,
        ),
        DialogField(
            "ritual_subject",
            "Ritual's subject",
            "text",
            _attr(book, "ritual_subject", ""),
            show_if=lambda v: text_kind(v) == TEXT_LONGEVITY,
        ),
        DialogField(
            "ritual_extra_vis",
            "Extra vis (each time)",
            "int",
            _attr(book, "ritual_extra_vis", 0),
            hint="Pawns beyond age / 5 the ritual was first made with: spent "
            "again whenever it is performed.",
            show_if=lambda v: text_kind(v) == TEXT_LONGEVITY,
        ),
        DialogField("language", "Language", "text", _attr(book, "language", "Latin")),
        DialogField("author", "Author", "text", _attr(book, "author", "")),
        DialogField(
            "author_id",
            "Author's sheet",
            "select",
            _attr(book, "author_id", None),
            options=[(c.name, c.id) for c in saga.characters if c.type == "magus"],
            allow_blank=True,
            placeholder="(not a magus of this saga)",
            hint="Links the text to its author: the Sigil shown, and whose "
            "texts a reader has decoded.",
            show_if=lab_text,
        ),
        DialogField(
            "raw",
            "Raw (author's shorthand)",
            "check",
            bool(_attr(book, "raw", False)),
            hint="Only the author, and whoever has decoded his texts, can use "
            "it until he rewrites it.",
            show_if=lab_text,
        ),
        DialogField(
            "year_published",
            "Year Published",
            "optint",
            _attr(book, "year_published", None),
        ),
        DialogField("owner", "Owner", "select", owner, options=bk.owner_options(saga)),
        _description_field(_attr(book, "description", "")),
    ]


def _book_from_values(book: Book, values: dict[str, Any], saga: Saga) -> None:
    """Write a book form's result onto `book`. Fields the chosen Type doesn't
    use (hidden in the form, so absent from `values`) are cleared."""
    book.name = values["name"]
    book.type = values["type"]
    book.language = values.get("language", "")
    book.author = values.get("author", "")
    book.year_published = values.get("year_published")
    book.description = values.get("description", "")
    book.owner_kind, book.owner_id = bk.parse_owner_value(values.get("owner"))
    book.subject_kind = values.get("subject_kind") or ""
    book.art = values.get("art") or ""
    ability = values.get("ability") or ""
    prefix = _ability_template_prefix(ability)
    if prefix is not None:
        ability = prefix + values.get("ability_detail", "")
    book.ability = ability
    lab_text = book.type == "Lab Text"
    book.text_kind = (values.get("text_kind") or TEXT_SPELL) if lab_text else ""
    of_spell = bk.needs_spell(book)
    book.spell_id = values.get("spell_id") if of_spell else None
    if not of_spell:
        book.spell_name = ""
    book.technique = values.get("technique") or ""
    book.form = values.get("form") or ""
    if book.text_kind == TEXT_LONGEVITY:
        # A Longevity Ritual is always Creo Corpus.
        book.technique, book.form = "Creo", "Corpus"
    book.effect_rdt = values.get("effect_rdt") or ""
    book.device_type = values.get("device_type") or ""
    book.shape_material = values.get("shape_material") or ""
    book.ritual_subject = values.get("ritual_subject") or ""
    book.ritual_extra_vis = max(0, values.get("ritual_extra_vis") or 0)
    book.author_id = (values.get("author_id") or None) if lab_text else None
    book.raw = bool(values.get("raw")) if lab_text else False
    author = saga.character(book.author_id)
    if author is not None and not book.author:
        book.author = author.name
    book.level = values.get("level")
    spell = spl.find_spell(saga, book.spell_id)
    if spell is not None:
        # A copy for display without the saga; level_of() reads the spell.
        book.spell_name = spell.name
        if spell.level is not None:
            book.level = spell.level
    book.quality = values.get("quality")


def _book_live(values: dict[str, Any], saga: Saga) -> str:
    """The form's live line. For a covenant still In Creation: the Build
    Point cost (a Lab Text's or Casting Tablet's from its spell's level) and
    any covenant-creation limit the values go over (a warning, not an
    error). Otherwise Build Points don't matter (STORY-1314): only the
    Level a spell gives the book."""
    owner_kind, owner_id = bk.parse_owner_value(values.get("owner"))
    probe = Book(
        id="",
        name="",
        type=values.get("type") or "Other",
        owner_kind=owner_kind,
        owner_id=owner_id,
    )
    probe.text_kind = values.get("text_kind") or ""
    probe.spell_id = values.get("spell_id") if bk.needs_spell(probe) else None
    spell = spl.find_spell(saga, probe.spell_id)
    from_spell = (
        f"Level {spell.level}, from the spell"
        if spell is not None and spell.level is not None
        else ""
    )
    if not bk.priced(saga, probe):
        return f"[dim]{from_spell}[/]" if from_spell else ""
    if not values.get("type"):
        return "[dim]Cost: choose a Type.[/]"
    probe.level = values.get("level") if bk.has_level(probe.type) else None
    probe.quality = values.get("quality") if bk.has_quality(probe.type) else None
    lines = [f"[b]Cost:[/] {bk.cost(probe, saga)} Build Points"]
    if from_spell:
        lines[0] += f"  [dim]({from_spell})[/]"
    lines += [f"[$text-error]{escape(w)}[/]" for w in bk.limit_warnings(probe)]
    return "\n".join(lines)


#: The choice in a Range/Duration/Target select that opens a free-text box.
_OTHER = "__other__"


def _rdt_field(
    key: str,
    label: str,
    standard: tuple[str, ...],
    value: str,
    fills: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> list[DialogField]:
    """A Range/Duration/Target select of the standard values plus "Other...",
    which shows a text box for a supplement's own value."""
    other = bool(value) and value not in standard
    return [
        DialogField(
            key,
            label,
            "select",
            _OTHER if other else value,
            options=_pairs(standard) + [("Other...", _OTHER)],
            required=True,
            allow_blank=True,
            placeholder=f"(choose a {label})",
            fills=fills,
        ),
        DialogField(
            f"{key}_other",
            f"{label} (other)",
            "text",
            value if other else "",
            placeholder="e.g. Road, Special",
            show_if=lambda v, k=key: v.get(k) == _OTHER,
        ),
    ]


def _spell_fields(spell: Spell | None) -> list[DialogField]:
    return [
        DialogField("name", "Name", "text", _attr(spell, "name", ""), required=True),
        DialogField(
            "technique",
            "Technique",
            "select",
            _attr(spell, "technique", ""),
            options=_pairs(TECHNIQUES),
            required=True,
            allow_blank=True,
            placeholder="(choose a Technique)",
        ),
        DialogField(
            "form",
            "Form",
            "select",
            _attr(spell, "form", ""),
            options=_pairs(FORMS),
            required=True,
            allow_blank=True,
            placeholder="(choose a Form)",
        ),
        DialogField(
            "level",
            "Level",
            "optint",
            _attr(spell, "level", None),
            hint="Leave blank for a General spell (cast at any level).",
        ),
        DialogField(
            "requisites",
            "Requisites",
            "text",
            ", ".join(_attr(spell, "requisites", [])),
            placeholder="e.g. Rego, Corpus",
        ),
        *_rdt_field(
            "range", "Range", SPELL_RANGES, _attr(spell, "range", ""), _level_fill
        ),
        *_rdt_field(
            "duration",
            "Duration",
            SPELL_DURATIONS,
            _attr(spell, "duration", ""),
            _level_fill,
        ),
        *_rdt_field(
            "target", "Target", SPELL_TARGETS, _attr(spell, "target", ""), _level_fill
        ),
        DialogField("ritual", "Ritual", "check", _attr(spell, "ritual", False)),
        DialogField(
            "base_level",
            "Base level",
            "optint",
            _attr(spell, "base_level", None),
            hint="The guideline's level; with Range, Duration and Target it "
            "fills in Level (add any size or requisite magnitudes yourself).",
            fills=_level_fill,
        ),
        DialogField(
            "source",
            "Source",
            "text",
            _attr(spell, "source", ""),
            placeholder="e.g. a house rule, or a book",
        ),
        DialogField(
            "description", "Description", "area", _attr(spell, "description", "")
        ),
    ]


def _level_fill(values: dict[str, Any]) -> dict[str, Any]:
    """Level worked out from the base and Range/Duration/Target
    (rules.spell_levels), once they are all standard and given."""
    base = values.get("base_level")
    if base is None:
        return {}
    design = spell_levels.spell_level(
        base,
        _spell_rdt(values, "range"),
        _spell_rdt(values, "duration"),
        _spell_rdt(values, "target"),
        ritual=bool(values.get("ritual")),
    )
    return {} if design is None else {"level": design.level}


def _spell_rdt(values: dict[str, Any], key: str) -> str:
    chosen = values.get(key) or ""
    return values.get(f"{key}_other", "").strip() if chosen == _OTHER else chosen


def _spell_from_values(spell: Spell, values: dict[str, Any]) -> None:
    spell.name = values["name"]
    spell.technique = values["technique"]
    spell.form = values["form"]
    spell.level = values.get("level")
    spell.requisites = spl.parse_requisites(values.get("requisites", ""))
    spell.range = _spell_rdt(values, "range")
    spell.duration = _spell_rdt(values, "duration")
    spell.target = _spell_rdt(values, "target")
    spell.ritual = bool(values.get("ritual"))
    spell.base_level = values.get("base_level")
    spell.source = values.get("source", "")
    spell.description = values.get("description", "")
    spell.details_missing = False


def _spell_problem(values: dict[str, Any]) -> str | None:
    if values.get("level") is not None and values["level"] < 1:
        return "Level must be at least 1 (or blank for a General spell)."
    for key, label in (
        ("range", "Range"),
        ("duration", "Duration"),
        ("target", "Target"),
    ):
        if values.get(key) == _OTHER and not values.get(f"{key}_other", "").strip():
            return f"Type the {label}, or choose one of the standard ones."
    unknown = spl.unknown_requisites(values.get("requisites", ""))
    if unknown:
        return f"Requisites must be Arts (e.g. Rego, Corpus), not {', '.join(unknown)}."
    return None


def _spell_live(values: dict[str, Any]) -> str:
    """The form's live line: the spell's shorthand and magnitude."""
    if not values.get("technique") or not values.get("form"):
        return "[dim]Choose a Technique and a Form.[/]"
    probe = Spell(
        id="",
        name="",
        technique=values["technique"],
        form=values["form"],
        level=values.get("level"),
        requisites=spl.parse_requisites(values.get("requisites", "")),
        ritual=bool(values.get("ritual")),
    )
    mag = spl.magnitude(probe)
    text = f"[b]{escape(spl.shorthand(probe))}[/]"
    text += "  General level" if mag is None else f"  magnitude {mag}"
    if probe.ritual and mag is not None:
        text += f"  ({spl.vis_cost(probe)} pawns, {spl.casting_time(probe)})"
    return text


class EditArtsScreen(ModalDialog[dict[str, ArtScore] | None]):
    """Edits all 15 Hermetic Arts at once -- a fixed grid, not an addable
    list. Two side-by-side columns (Techniques, Forms), mirroring the sheet's
    own two-column Magical Arts display -- sized to fit every row without a
    scrollbar (Forms, the taller column, is only 10 rows). Each Art shows a
    Level / XP pair. Dismisses with a dict of every art's lowercase name ->
    ArtScore, or None if cancelled.
    """

    DEFAULT_CSS = """
    EditArtsScreen {
        align: center middle;
    }

    #arts-dialog {
        width: auto;
        height: auto;
        max-height: 100%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #arts-subtitle {
        color: $text-muted;
        margin-bottom: 1;
    }

    #arts-columns {
        width: auto;
        height: auto;
    }

    #arts-techniques-col {
        width: auto;
        height: auto;
        margin-right: 3;
    }

    #arts-forms-col {
        width: auto;
        height: auto;
    }

    .column-heading {
        text-style: bold;
        margin-bottom: 1;
    }

    .art-row {
        width: auto;
        height: auto;
    }

    .art-row Label {
        width: 16;
        content-align: right middle;
        padding-right: 1;
    }

    .art-row .art-score {
        width: 10;
        content-align: left middle;
        padding-left: 1;
        color: $text-muted;
    }

    .art-row Input {
        width: 5;
    }

    #arts-buttons {
        width: auto;
        height: auto;
    }

    #arts-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, arts: dict[str, ArtScore]) -> None:
        super().__init__()
        self.arts = arts

    def compose(self) -> ComposeResult:
        def row(art_name: str):
            key = art_name.lower()
            score = self.arts.get(key, ArtScore())
            yield Label(f"{art_name} ({ART_ABBREVIATIONS[art_name]})")
            yield Input(
                value=str(score.xp),
                type="integer",
                id=f"input-art-{key}-xp",
                compact=True,
            )
            yield Label(
                self._score_label(score.xp),
                id=f"art-score-{key}",
                classes="art-score",
            )

        with Vertical(id="arts-dialog"):
            yield Label("Edit Arts", id="arts-title")
            yield Label(
                "Enter each Art's total XP; its score follows", id="arts-subtitle"
            )
            with Horizontal(id="arts-columns"):
                with Vertical(id="arts-techniques-col"):
                    yield Label("Techniques", classes="column-heading")
                    for technique in TECHNIQUES:
                        with Horizontal(classes="art-row"):
                            yield from row(technique)
                with Vertical(id="arts-forms-col"):
                    yield Label("Forms", classes="column-heading")
                    for form in FORMS:
                        with Horizontal(classes="art-row"):
                            yield from row(form)
            yield Static("", id="arts-error")
            with Horizontal(id="arts-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.action_cancel()
        elif event.button.id == "btn-save":
            self._try_save()

    @staticmethod
    def _score_label(xp: int | None) -> str:
        if xp is None or xp < 0:
            return "Score ?"
        return f"Score {ArtScore(xp=xp).level}"

    def on_input_changed(self, event: Input.Changed) -> None:
        """Keep each Art's score beside its XP as the user types."""
        input_id = event.input.id or ""
        if not (input_id.startswith("input-art-") and input_id.endswith("-xp")):
            return
        key = input_id.removeprefix("input-art-").removesuffix("-xp")
        try:
            xp: int | None = int(event.value.strip())
        except ValueError:
            xp = None
        self.query_one(f"#art-score-{key}", Label).update(self._score_label(xp))

    def _try_save(self) -> None:
        error = self.query_one("#arts-error", Static)
        result: dict[str, ArtScore] = {}
        for art_name in ARTS:
            key = art_name.lower()
            xp_raw = self.query_one(f"#input-art-{key}-xp", Input).value.strip()
            try:
                xp = int(xp_raw)
            except ValueError:
                error.update(f"{art_name} needs a whole number of XP.")
                return
            if xp < 0:
                error.update(f"{art_name}'s XP can't be negative.")
                return
            result[key] = ArtScore(xp=xp)
        self.dismiss(result)


class MasteryEditScreen(ModalDialog[KnownSpell | None]):
    """Edits a known spell's Mastery: score, xp, and its Mastery Abilities
    (each with its own name/level/xp -- see MasteryAbility). Abilities are
    added/removed here and only committed to the character on Save.
    Dismisses with the finished KnownSpell, or None if cancelled."""

    DEFAULT_CSS = """
    MasteryEditScreen {
        align: center middle;
    }

    #mastery-dialog {
        width: 70;
        height: auto;
        max-height: 30;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #mastery-abilities-list {
        height: auto;
        max-height: 8;
        border: solid $accent;
    }

    #mastery-error {
        color: $error;
        height: auto;
        margin-top: 1;
    }

    #mastery-ability-row-buttons {
        width: 100%;
        height: auto;
    }

    #mastery-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, spell_name: str, existing: KnownSpell) -> None:
        super().__init__()
        self.spell_name = spell_name
        self.spell_id = existing.spell_id
        self.mastery_score = existing.mastery_score
        self.mastery_xp = existing.mastery_xp
        #: A working copy -- only becomes real on Save.
        self._abilities: list[MasteryAbility] = list(existing.mastery_abilities)

    def compose(self) -> ComposeResult:
        with Vertical(id="mastery-dialog"):
            yield Label(f"Mastery: {escape(self.spell_name)}", id="mastery-title")
            yield Label("Score")
            yield Input(
                value=str(self.mastery_score), type="integer", id="input-mastery-score"
            )
            yield Label("XP")
            yield Input(
                value=str(self.mastery_xp), type="integer", id="input-mastery-xp"
            )
            yield Label("Mastery Abilities")
            yield ListView(id="mastery-abilities-list")
            with Horizontal(id="mastery-ability-row-buttons"):
                yield Button("Add Ability", id="btn-add-ability", compact=True)
                yield Button("Remove Ability", id="btn-remove-ability", compact=True)
            yield Static("", id="mastery-error")
            with Horizontal(id="mastery-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def on_mount(self) -> None:
        self._render_abilities()

    def _render_abilities(self) -> None:
        list_view = self.query_one("#mastery-abilities-list", ListView)
        list_view.clear()
        if not self._abilities:
            list_view.append(ListItem(Label("[dim](none)[/]")))
            return
        for ability in self._abilities:
            list_view.append(
                ListItem(Label(f"{escape(ability.name)} {ability.level}/{ability.xp}"))
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.action_cancel()
        elif event.button.id == "btn-save":
            self._try_save()
        elif event.button.id == "btn-add-ability":
            self._add_ability()
        elif event.button.id == "btn-remove-ability":
            self._remove_ability()

    def _add_ability(self) -> None:
        def handle_result(ability: MasteryAbility | None) -> None:
            if ability is not None:
                self._abilities.append(ability)
                self._render_abilities()

        self.app.push_screen(
            _mastery_ability_dialog("Add a Mastery Ability"), handle_result
        )

    def _remove_ability(self) -> None:
        if not self._abilities:
            return
        list_view = self.query_one("#mastery-abilities-list", ListView)
        index = list_view.index
        if index is None or index >= len(self._abilities):
            return

        def handle_confirmed(confirmed: bool | None) -> None:
            if confirmed:
                del self._abilities[index]
                self._render_abilities()

        self.app.push_screen(
            ConfirmScreen(f"Delete {escape(self._abilities[index].name)}?"),
            handle_confirmed,
        )

    def _try_save(self) -> None:
        error = self.query_one("#mastery-error", Static)
        try:
            score = int(self.query_one("#input-mastery-score", Input).value)
            xp = int(self.query_one("#input-mastery-xp", Input).value)
        except ValueError:
            error.update("Score and XP must be whole numbers.")
            return
        self.dismiss(
            KnownSpell(
                spell_id=self.spell_id,
                mastery_score=score,
                mastery_xp=xp,
                mastery_abilities=self._abilities,
            )
        )


class EditFamiliarBindingScreen(ModalDialog[dict[str, object] | None]):
    """Edits a Familiar's Initial Binding details and the three Cords.
    Dismisses with a dict of field values, or None if cancelled."""

    DEFAULT_CSS = """
    EditFamiliarBindingScreen {
        align: center middle;
    }

    #fam-binding-dialog {
        width: 70;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    .fambindingedit-row {
        width: 100%;
        height: 1;
    }

    .fambindingedit-row Label {
        width: 28;
    }

    .fambindingedit-row Input, .fambindingedit-row Select {
        width: 1fr;
    }

    .fambindingedit-cost {
        width: auto;
        color: $text-muted;
        padding-left: 1;
    }

    #fam-binding-error {
        color: $error;
        height: auto;
    }

    #fam-binding-buttons {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, familiar: Familiar) -> None:
        super().__init__()
        self.familiar = familiar

    def compose(self) -> ComposeResult:
        f = self.familiar
        with Vertical(id="fam-binding-dialog"):
            yield Label("Edit Binding & Cords")
            with Horizontal(classes="fambindingedit-row"):
                yield Label("Binding Technique")
                yield Select(
                    _pairs(TECHNIQUES),
                    value=f.binding_technique or Select.NULL,
                    allow_blank=True,
                    prompt="(not set)",
                    id="select-fam-technique",
                    compact=True,
                )
            with Horizontal(classes="fambindingedit-row"):
                yield Label("Binding Form")
                yield Select(
                    _pairs(FORMS),
                    value=f.binding_form or Select.NULL,
                    allow_blank=True,
                    prompt="(not set)",
                    id="select-fam-form",
                    compact=True,
                )
            with Horizontal(classes="fambindingedit-row"):
                yield Label("Initial Binding Lab Total")
                yield Input(
                    value=str(f.binding_lab_total),
                    type="integer",
                    id="input-fam-lab-total",
                    compact=True,
                )
            with Horizontal(classes="fambindingedit-row"):
                yield Label("Target Binding Level")
                yield Input(
                    value=str(f.target_binding_level),
                    type="integer",
                    id="input-fam-target-level",
                    compact=True,
                )
            with Horizontal(classes="fambindingedit-row"):
                yield Label("Cumulative Vis Spent (pawns)")
                yield Input(
                    value=str(f.vis_spent_binding),
                    type="integer",
                    id="input-fam-vis-spent",
                    compact=True,
                )
            for attribute, label, _blurb in fam.CORDS:
                with Horizontal(classes="fambindingedit-row"):
                    yield Label(label)
                    yield Select(
                        [(f"+{score}", score) for score in CORD_SCORE_COSTS],
                        value=getattr(f, attribute),
                        allow_blank=False,
                        id=f"select-fam-{attribute}",
                        compact=True,
                    )
                    yield Static(
                        f"{fam.cord_cost(getattr(f, attribute))} pts",
                        id=f"cost-fam-{attribute}",
                        classes="fambindingedit-cost",
                    )
            yield Static("", id="fam-binding-error")
            with Horizontal(id="fam-binding-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.action_cancel()
        elif event.button.id == "btn-save":
            self._try_save()

    def on_select_changed(self, event: Select.Changed) -> None:
        select_id = event.select.id or ""
        if not select_id.startswith("select-fam-"):
            return
        attribute = select_id.removeprefix("select-fam-")
        if attribute not in {a for a, _, _ in fam.CORDS}:
            return
        score = event.value
        if isinstance(score, int):
            self.query_one(f"#cost-fam-{attribute}", Static).update(
                f"{fam.cord_cost(score)} pts"
            )

    def _try_save(self) -> None:
        error = self.query_one("#fam-binding-error", Static)

        technique_value = self.query_one("#select-fam-technique", Select).value
        form_value = self.query_one("#select-fam-form", Select).value
        result: dict[str, object] = {
            "binding_technique": technique_value
            if isinstance(technique_value, str)
            else "",
            "binding_form": form_value if isinstance(form_value, str) else "",
        }

        for field_name, key, label in (
            ("input-fam-lab-total", "binding_lab_total", "Initial Binding Lab Total"),
            ("input-fam-target-level", "target_binding_level", "Target Binding Level"),
            ("input-fam-vis-spent", "vis_spent_binding", "Cumulative Vis Spent"),
        ):
            raw = self.query_one(f"#{field_name}", Input).value.strip()
            try:
                result[key] = int(raw)
            except ValueError:
                error.update(f"{label} must be a whole number.")
                return

        for attribute, _label, _blurb in fam.CORDS:
            result[attribute] = self.query_one(f"#select-fam-{attribute}", Select).value

        self.dismiss(result)


#: What the saga's Import Data dialog offers: (key, label, works yet?). The
#: ones that don't work yet are listed greyed out, as what's planned.
IMPORT_KINDS: tuple[tuple[str, str, bool], ...] = (
    # An export made from More on its sheet (STORY-109): one entry per kind.
    ("characters", "Characters", True),
    ("covenants", "Covenants", True),
    ("laboratories", "Laboratories", True),
    ("books", "Books", True),
    ("spells", "Spells", True),
)
#: The kind the dialog opens on.
IMPORT_DEFAULT = "books"


class ImportScreen(ModalDialog[str | None]):
    """Choose what to import into the saga. Kinds that can't be imported yet
    are shown greyed out and can't be chosen. Dismisses with the chosen
    IMPORT_KINDS key, or None if cancelled."""

    DEFAULT_CSS = """
    ImportScreen {
        align: center middle;
    }

    #import-dialog {
        width: 50;
        max-width: 100%;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #import-hint {
        color: $text-muted;
        height: auto;
        margin-bottom: 1;
    }

    #import-list {
        height: auto;
    }

    #import-buttons {
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="import-dialog"):
            yield Label("Import Data", id="import-title")
            yield Static("What would you like to import?", id="import-hint")
            yield OptionList(id="import-list", compact=True)
            with Horizontal(id="import-buttons"):
                yield Button("Cancel", id="btn-import-cancel")

    def on_mount(self) -> None:
        options = self.query_one("#import-list", OptionList)
        options.add_options(
            Option(label, id=key)
            if works
            else Option(f"{label}  (not available yet)", id=key, disabled=True)
            for key, label, works in IMPORT_KINDS
        )
        options.highlighted = next(
            i for i, k in enumerate(IMPORT_KINDS) if k[0] == IMPORT_DEFAULT
        )
        options.focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        event.stop()
        self.dismiss(event.option.id)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(None)


class DuplicateBookScreen(ModalScreen[str]):
    """Asked during an import for a book whose name is already taken.
    Dismisses with "duplicate", "duplicate_all", "skip" or "skip_all" (the
    "_all" answers apply to every later duplicate of the same import). Skip
    is focused, and Escape skips, so a stray key never adds a copy."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("escape", "choose('skip')", "Skip"),
        ("d", "choose('duplicate')", "Duplicate"),
        ("D", "choose('duplicate_all')", "Duplicate All"),
        ("s", "choose('skip')", "Skip"),
        ("S", "choose('skip_all')", "Skip All"),
    ]

    DEFAULT_CSS = """
    DuplicateBookScreen {
        align: center middle;
    }

    #duplicate-dialog {
        width: 72;
        max-width: 100%;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #duplicate-message {
        height: auto;
        margin-bottom: 1;
    }

    #duplicate-buttons {
        width: 100%;
        height: auto;
    }

    #duplicate-buttons Button {
        margin-right: 1;
    }
    """

    #: (answer, button label), in button order.
    CHOICES: ClassVar[tuple[tuple[str, str], ...]] = (
        ("duplicate", "Duplicate"),
        ("duplicate_all", "Duplicate All"),
        ("skip", "Skip"),
        ("skip_all", "Skip All"),
    )

    def __init__(self, name: str, remaining: int, *, noun: str = "book") -> None:
        super().__init__()
        self.book_name = name
        self.remaining = remaining
        self.noun = noun

    def compose(self) -> ComposeResult:
        more = (
            f"\n[dim]{self.remaining} more duplicate(s) after this one.[/]"
            if self.remaining
            else ""
        )
        with Vertical(id="duplicate-dialog"):
            yield Static(
                f"A {self.noun} named [b]{escape(self.book_name)}[/] is already "
                f"in the saga. Add this one as well?{more}",
                id="duplicate-message",
            )
            with Horizontal(id="duplicate-buttons"):
                for answer, label in self.CHOICES:
                    yield Button(label, id=f"btn-{answer.replace('_', '-')}")

    def on_mount(self) -> None:
        self.query_one("#btn-skip", Button).focus()

    def action_choose(self, answer: str) -> None:
        self.dismiss(answer)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        self.dismiss((event.button.id or "btn-skip")[len("btn-") :].replace("-", "_"))


class SpellImportHelperScreen(ModalDialog[str | None]):
    """What a spell CSV looks like, with a way to save an example to start
    from. Dismisses with "choose" to go on to picking the file, or None."""

    DEFAULT_CSS = """
    SpellImportHelperScreen {
        align: center middle;
    }

    #spell-import-dialog {
        width: 96;
        max-width: 100%;
        height: auto;
        max-height: 100%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #spell-import-body {
        height: auto;
        max-height: 30;
    }

    #spell-import-status {
        height: auto;
        margin-top: 1;
    }

    #spell-import-buttons {
        width: 100%;
        height: auto;
        margin-top: 1;
    }

    #spell-import-buttons Button {
        margin-right: 1;
    }
    """

    def __init__(self, folder: Path) -> None:
        super().__init__()
        self.folder = folder

    def compose(self) -> ComposeResult:
        columns = "\n".join(
            f"  [b]{name}[/]: {escape(meaning)}"
            for name, meaning in spl.CSV_COLUMN_HELP
        )
        example = escape(spl.EXAMPLE_CSV.splitlines()[1])
        with Vertical(id="spell-import-dialog"):
            yield Label("Import Spells", id="spell-import-title")
            with VerticalScroll(id="spell-import-body"):
                yield Static(
                    "Spells are imported from a CSV file with a header row into the "
                    "saga's own spells. Columns, in any order and any case:\n\n"
                    f"{columns}\n\n[b]An example row:[/]\n  [dim]{example}[/]",
                    id="spell-import-help",
                )
            yield Static("", id="spell-import-status")
            with Horizontal(id="spell-import-buttons"):
                yield Button(
                    "Choose CSV file...",
                    id="btn-spell-import-choose",
                    variant="success",
                )
                yield Button("Save example CSV", id="btn-spell-import-example")
                yield Button("Cancel", id="btn-spell-import-cancel")

    def on_mount(self) -> None:
        self._fit()
        self.query_one("#btn-spell-import-choose", Button).focus()

    def on_resize(self) -> None:
        self._fit()

    def _fit(self) -> None:
        """The help scrolls, so the buttons stay on screen however short the
        terminal is."""
        self.query_one("#spell-import-body").styles.max_height = max(
            4, min(30, self.size.height - 12)
        )

    def _save_example(self) -> None:
        target = self.folder / "spells_example.csv"
        n = 2
        while target.exists():
            target = self.folder / f"spells_example_{n}.csv"
            n += 1
        status = self.query_one("#spell-import-status", Static)
        try:
            target.write_text(spl.EXAMPLE_CSV, encoding="utf-8")
        except OSError as problem:
            status.update(
                f"[$text-error]Couldn't save the example: {escape(str(problem))}[/]"
            )
            return
        status.update(
            f"Saved [b]{escape(target.name)}[/] in {escape(str(self.folder))}. "
            "Edit it, then choose it to import."
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if event.button.id == "btn-spell-import-choose":
            self.dismiss("choose")
        elif event.button.id == "btn-spell-import-example":
            self._save_example()
        else:
            self.dismiss(None)


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
        border: round $accent;
        padding: 1 2;
        background: $surface;
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
        with Vertical(id="improve-dialog"):
            yield Label(
                f"Improve {source.name or 'this source of income'}", id="improve-title"
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


# -- Enchanted Devices & Talismans (STORY-305) --

#: The Maker select's value for a maker who isn't one of the saga's
#: characters (their name is typed).
_OTHER_MAKER = "_other"


def _component_dialog(
    component: DeviceComponent | None,
) -> FieldsDialog[DeviceComponent]:
    """One component of an item: what it is, its Material and its Size."""

    def capacity(values: dict[str, Any]) -> str:
        c = DeviceComponent("", values.get("material") or "", values.get("size") or "")
        return f"Capacity: {ed.component_capacity(c)} pawns"

    return FieldsDialog(
        "Add a component" if component is None else "Edit a component",
        [
            DialogField(
                "description",
                "Description",
                "text",
                _attr(component, "description", ""),
                placeholder="e.g. oak staff",
            ),
            DialogField(
                "material",
                "Material",
                "select",
                _attr(component, "material", "wood"),
                options=[
                    (f"{name} ({base})", name)
                    for name, base in ENCHANT_MATERIALS.items()
                ],
            ),
            DialogField(
                "size",
                "Size",
                "select",
                _attr(component, "size", "small"),
                options=[(f"{name} (x{n})", name) for name, n in ENCHANT_SIZES.items()],
                hint=f"From the {MATERIAL_SIZE_CITATION}.",
            ),
        ],
        live=capacity,
        build=lambda values: DeviceComponent(
            values["description"], values["material"], values["size"]
        ),
    )


def _bonus_fields(
    bonus: ShapeMaterialBonus | None, *, attunement: bool, year: int, season: str
) -> list[DialogField]:
    fields = [
        DialogField(
            "catalog",
            "From DE's table",
            "picker",
            None,
            placeholder="(choose a shape or material...)",
            picker=lambda _current: ShapeMaterialPickerScreen(),
            display=lambda b: f"{b.shape}: {b.bonus:+d} {b.applies_to}",
            fills=lambda values: (
                {
                    "bonus": values["catalog"].bonus,
                    "applies_to": values["catalog"].applies_to,
                    "shape": values["catalog"].shape,
                }
                if values.get("catalog") is not None
                else {}
            ),
        ),
        DialogField("bonus", "Bonus", "int", _attr(bonus, "bonus", 0)),
        DialogField(
            "applies_to",
            "Applies to",
            "text",
            _attr(bonus, "applies_to", ""),
            required=True,
            placeholder="e.g. project bolt or other missile",
        ),
        DialogField(
            "shape",
            "Shape or material",
            "text",
            _attr(bonus, "shape", ""),
            placeholder="e.g. Wand/Staff",
        ),
    ]
    if attunement:
        fields += [
            DialogField(
                "season",
                "Season gained",
                "select",
                _attr(bonus, "season", season) or season,
                options=_pairs(SEASONS),
            ),
            DialogField("year", "Year gained", "optint", _attr(bonus, "year", year)),
        ]
    return fields


def _bonus_dialog(
    bonus: ShapeMaterialBonus | None,
    *,
    attunement: bool = False,
    year: int = 1220,
    season: str = "Spring",
) -> FieldsDialog[ShapeMaterialBonus]:
    """A Shape & Material bonus, picked from DE's table or typed; for an
    attunement, also the season and year it was gained."""
    noun = "an attunement" if attunement else "a Shape & Material bonus"
    return FieldsDialog(
        f"Add {noun}" if bonus is None else f"Edit {noun}",
        _bonus_fields(bonus, attunement=attunement, year=year, season=season),
        build=lambda values: ShapeMaterialBonus(
            values["bonus"],
            values["applies_to"],
            values["shape"],
            values.get("year") if attunement else None,
            values.get("season") or "" if attunement else "",
        ),
    )


def _list_display(label: Callable[[Any], str]) -> Callable[[Any], str]:
    """A list field's button text (plain): its entries, or "(none)"."""

    def display(items: list[Any]) -> str:
        if not items:
            return "(none: press to add)"
        return "; ".join(label(item) for item in items)

    return display


def _holder_options(saga: Saga) -> list[tuple[str, str]]:
    """Every character, laboratory and covenant, as "kind:id" values."""
    return [
        *(
            (f"{escape(c.name)} (character)", f"character:{c.id}")
            for c in saga.characters
        ),
        *(
            (f"{escape(lab.name)} (laboratory)", f"laboratory:{lab.id}")
            for lab in saga.laboratories
        ),
        *((f"{escape(c.name)} (covenant)", f"covenant:{c.id}") for c in saga.covenants),
    ]


def _device_from_values(
    saga: Saga, device: EnchantedDevice, values: dict[str, Any]
) -> EnchantedDevice:
    """A copy of `device` with the form's `values` (a hidden field keeps the
    device's own value)."""
    copy = replace(device, effects=list(device.effects))
    holder = values.get("holder") or ""
    kind, _, holder_id = holder.partition(":")
    maker_choice = values.get("maker")
    typed = values.get("type") or device.type
    copy.name = values.get("name", device.name) or ""
    copy.type = typed
    copy.talisman = typed == INVESTED and bool(values.get("talisman", device.talisman))
    copy.holder_kind, copy.holder_id = (kind, holder_id) if holder else (None, None)
    copy.maker_id = (
        maker_choice if maker_choice and maker_choice != _OTHER_MAKER else None
    )
    copy.maker_name = (
        values.get("maker_name") or "" if maker_choice == _OTHER_MAKER else ""
    )
    for key in (
        "components",
        "payment",
        "capacity_override",
        "pawns_opened",
        "bonuses",
        "lab_total",
        "charges_made",
        "charges_left",
        "objects",
        "attunements",
        "description",
    ):
        if key in values:
            setattr(copy, key, values[key])
    if copy.components is None:
        copy.components = []
    return copy


def _device_live(saga: Saga, device: EnchantedDevice, values: dict[str, Any]) -> str:
    """The form's live line: the capacity (or charges) as the fields stand,
    and any warning."""
    draft = _device_from_values(saga, device, values)
    if draft.type == CHARGED:
        most = ed.max_charges(draft)
        text = (
            f"Charges: at most {most} from its Lab Total"
            if most is not None
            else "Charges: worked out once it has a Lab Total and its effect"
        )
    else:
        text = f"Capacity: {ed.capacity_text(saga, draft)}"
        if draft.effects:
            text += f"; its effects use {ed.pawns_used(draft)}"
    problems = ed.warnings(saga, draft)
    if problems:
        text += "\n" + "\n".join(f"[$text-error]{line}[/]" for line in problems)
    return text


def _device_problem(device: EnchantedDevice, values: dict[str, Any]) -> str | None:
    kind = values["type"]
    if kind in (LESSER, CHARGED) and len(device.effects) > 1:
        return (
            f"A {kind} has exactly one effect: remove the others before changing "
            "its type."
        )
    for key, label in (
        ("pawns_opened", "Pawns opened"),
        ("capacity_override", "Capacity"),
        ("lab_total", "Lab Total"),
        ("charges_made", "Charges made"),
        ("charges_left", "Charges left"),
    ):
        value = values.get(key)
        if value is not None and value < 0:
            return f"{label} can't be negative."
    if values.get("objects") is not None and values["objects"] < 1:
        return "Objects must be at least 1."
    made, left = values.get("charges_made"), values.get("charges_left")
    if made is not None and left is not None and left > made:
        return "Charges left can't be more than charges made."
    return None


def _enchanted_device_dialog(
    saga: Saga,
    device: EnchantedDevice | None,
    *,
    holder: str | None = None,
) -> FieldsDialog[EnchantedDevice]:
    """Add or edit an enchanted device (DE ch. 8): its type decides which
    fields show. Components, Shape & Material bonuses and a talisman's
    attunements are lists edited in a sub-dialog. `holder` ("kind:id") is a
    new device's default holder. Dismisses with the finished device (a new
    one, or a copy of `device` to put in its place)."""
    base = device or EnchantedDevice(id="", name="")
    maker_options = [(escape(c.name), c.id) for c in saga.characters] + [
        ("Someone else (type the name)", _OTHER_MAKER)
    ]
    if device is None:
        maker_value: str | None = None
        holder_value = holder
    else:
        maker_value = device.maker_id or (_OTHER_MAKER if device.maker_name else None)
        holder_value = (
            f"{device.holder_kind}:{device.holder_id}" if device.holder_kind else None
        )

    def is_type(*kinds: str) -> Callable[[dict[str, Any]], bool]:
        return lambda values: values.get("type") in kinds

    def list_field(
        key: str,
        label: str,
        items: list[Any],
        title: str,
        row: Callable[[Any], str],
        dialog: Callable[[Any], FieldsDialog[Any]],
        **extra: Any,
    ) -> DialogField:
        return DialogField(
            key,
            label,
            "picker",
            list(items),
            picker=lambda current: ListFieldScreen(
                title, current or [], lambda item: escape(row(item)), dialog
            ),
            display=_list_display(row),
            **extra,
        )

    fields = [
        DialogField(
            "name",
            "Name",
            "text",
            base.name,
            required=True,
            placeholder="e.g. Wand of Flames",
        ),
        DialogField("type", "Type", "select", base.type, options=_pairs(DEVICE_TYPES)),
        DialogField(
            "talisman",
            "Talisman",
            "check",
            base.talisman,
            show_if=is_type(INVESTED),
            hint=ed.TALISMAN_HINT,
        ),
        DialogField(
            "holder",
            "Holder",
            "select",
            holder_value,
            options=_holder_options(saga),
            required=True,
            allow_blank=True,
            placeholder="(choose who holds it)",
        ),
        DialogField(
            "maker",
            "Maker",
            "select",
            maker_value,
            options=maker_options,
            allow_blank=True,
            placeholder="(unknown: found or bought)",
        ),
        DialogField(
            "maker_name",
            "Maker's name",
            "text",
            base.maker_name,
            show_if=lambda values: values.get("maker") == _OTHER_MAKER,
        ),
        list_field(
            "components",
            "Components",
            base.components,
            "Components (Material and Size)",
            ed.component_text,
            _component_dialog,
            show_if=is_type(INVESTED, LESSER),
            hint="Normally one; at most the maker's Magic Theory.",
        ),
        DialogField(
            "payment",
            "Opening paid for",
            "select",
            base.payment,
            options=_pairs(DEVICE_PAYMENTS),
            show_if=lambda values: (
                values.get("type") == INVESTED
                and len(values.get("components") or []) > 1
            ),
            hint="A one-time choice when it is opened.",
        ),
        DialogField(
            "capacity_override",
            "Capacity (blank = worked out)",
            "optint",
            base.capacity_override,
            show_if=is_type(INVESTED, LESSER),
        ),
        DialogField(
            "pawns_opened",
            "Pawns opened",
            "int",
            base.pawns_opened,
            show_if=is_type(INVESTED),
            hint="Only a talisman can be opened a few pawns at a time.",
        ),
        list_field(
            "bonuses",
            "Shape & Material",
            base.bonuses,
            "Shape & Material bonuses",
            ed.bonus_text,
            lambda b: _bonus_dialog(b),
            hint=ed.BONUS_HINT,
        ),
        list_field(
            "attunements",
            "Attunements",
            base.attunements,
            "Talisman attunements",
            lambda b: ed.bonus_text(b, when=True),
            lambda b: _bonus_dialog(
                b,
                attunement=True,
                year=saga.current_year,
                season=saga.current_season,
            ),
            show_if=lambda values: (
                values.get("type") == INVESTED and bool(values.get("talisman"))
            ),
            hint="One each time it is opened or given an effect.",
        ),
        DialogField(
            "lab_total",
            "Lab Total",
            "optint",
            base.lab_total,
            show_if=is_type(CHARGED),
        ),
        DialogField(
            "charges_made",
            "Charges made (blank = most)",
            "optint",
            base.charges_made,
            show_if=is_type(CHARGED),
        ),
        DialogField(
            "charges_left",
            "Charges left (blank = all)",
            "optint",
            base.charges_left,
            show_if=is_type(CHARGED),
        ),
        DialogField(
            "objects",
            "Objects sharing the charges",
            "int",
            base.objects,
            show_if=is_type(CHARGED),
            hint="e.g. 5 arrows or potions.",
        ),
        _description_field(base.description),
    ]

    def build(values: dict[str, Any]) -> EnchantedDevice:
        built = _device_from_values(saga, base, values)
        if device is None:
            built.id = storage.generate_unique_id(
                built.name, [d.id for d in saga.enchanted_devices]
            )
        return built

    return FieldsDialog(
        "Add an Enchanted Device" if device is None else "Edit an Enchanted Device",
        fields,
        validate=lambda values: _device_problem(base, values),
        live=lambda values: _device_live(saga, base, values),
        save_label="Add" if device is None else "Save",
        build=build,
    )


def _effect_from_values(
    effect: InstilledEffect, values: dict[str, Any]
) -> InstilledEffect:
    """A copy of `effect` with the form's `values` (a hidden field keeps the
    effect's own value, except the ones a checkbox turned off)."""
    copy = replace(effect)
    for key, value in values.items():
        if not hasattr(copy, key):
            continue
        setattr(copy, key, "" if value is None and key in _EFFECT_TEXT else value)
    if not copy.restricted_use:
        copy.restricted_to = ""
    if not copy.linked_trigger:
        copy.linked_to = ""
    if copy.expiry == "None":
        copy.first_use_year = None
    return copy


#: The effect's text fields a blank select leaves "" (not None).
_EFFECT_TEXT = frozenset({"technique", "form", "linked_to", "uses_per_day", "expiry"})


def _effect_live(
    device: EnchantedDevice, effect: InstilledEffect, values: dict[str, Any]
) -> str:
    """The form's live line: the modified level with its breakdown, the vis,
    and how full the device would be."""
    draft = _effect_from_values(effect, values)
    others = [e for e in device.effects if e.id != effect.id]
    trial = replace(device, effects=[*others, draft])
    level = ed.modified_level(trial, draft)
    parts = ed.level_breakdown(trial, draft)
    breakdown = " + ".join(
        [str(parts[0][1]), *(f"{n} ({label})" for label, n in parts[1:])]
    )
    text = f"Modified level: {level}" + (
        f" = {breakdown}"
        if len(parts) > 1 and draft.modified_level_override is None
        else ""
    )
    if device.type == CHARGED:
        return text
    used = ed.pawns_used(trial)
    text += f"; vis {ed.vis_cost(trial, draft)}; the device's effects would use {used}"
    room = device.pawns_opened if device.type == INVESTED else None
    if room is not None and used > room:
        text += f"\n[$text-error]More than the {room} pawns opened.[/]"
    return text


def _effect_problem(values: dict[str, Any]) -> str | None:
    penetration = values.get("penetration")
    if penetration is not None and (penetration < 0 or penetration % 2):
        return "Penetration must be a whole even number (+1 level per 2 points)."
    for key, label in (
        ("level", "Effect level"),
        ("instilling_progress", "Instilling progress"),
        ("modified_level_override", "Modified level"),
        ("vis_override", "Vis"),
    ):
        value = values.get(key)
        if value is not None and value < 0:
            return f"{label} can't be negative."
    return None


def _instilled_effect_dialog(
    device: EnchantedDevice, effect: InstilledEffect | None
) -> FieldsDialog[InstilledEffect]:
    """Add ("Instill Effect") or edit one of `device`'s effects (DE ch. 8,
    Designing the Effect and Effect Modifications). Uses per day, Effect
    Expiry and instilling progress only show on the types that have them.
    Dismisses with the finished effect."""
    base = effect or InstilledEffect(id=new_instance_id())
    invested = device.type == INVESTED
    linked_options = [
        (escape(ed.effect_name(e)) or "(unnamed)", e.id)
        for e in device.effects
        if e.id != base.id
    ]

    def check(key: str, label: str, **extra: Any) -> DialogField:
        return DialogField(key, label, "check", getattr(base, key), **extra)

    fields = [
        DialogField(
            "name",
            "Name",
            "text",
            base.name,
            required=True,
            placeholder="e.g. Pilum of Fire",
        ),
        DialogField(
            "technique",
            "Technique",
            "select",
            base.technique,
            options=_pairs(TECHNIQUES),
            allow_blank=True,
            placeholder="(none)",
        ),
        DialogField(
            "form",
            "Form",
            "select",
            base.form,
            options=_pairs(FORMS),
            allow_blank=True,
            placeholder="(none)",
        ),
        DialogField(
            "requisites",
            "Requisites",
            "text",
            base.requisites,
            placeholder="e.g. Rego",
        ),
        DialogField("range", "Range", "text", base.range, placeholder="e.g. Voice"),
        DialogField(
            "duration", "Duration", "text", base.duration, placeholder="e.g. Mom"
        ),
        DialogField("target", "Target", "text", base.target, placeholder="e.g. Ind"),
        DialogField("level", "Effect level", "int", base.level, hint=ed.LEVEL_HINT),
    ]
    if device.type != CHARGED:
        fields.append(
            DialogField(
                "uses_per_day",
                "Uses per day",
                "select",
                base.uses_per_day,
                options=[
                    (f"{ed.uses_text(uses)} (+{added})", uses)
                    for uses, added in EFFECT_FREQUENCIES.items()
                ],
            )
        )
    fields += [
        DialogField(
            "penetration",
            "Penetration",
            "int",
            base.penetration,
            hint="+1 level per 2 points.",
        ),
        check("maintains_concentration", "Maintains concentration (+5)"),
        check("restricted_use", "Restricted use (+3)"),
        DialogField(
            "restricted_to",
            "Restricted to",
            "text",
            base.restricted_to,
            placeholder="who may use it",
            show_if=lambda values: bool(values.get("restricted_use")),
        ),
        check("environmental_trigger", "Environmental trigger (+3)"),
        check("fast_trigger", "Fast trigger (+5)"),
        check("linked_trigger", "Linked trigger (+3)"),
        DialogField(
            "linked_to",
            "Triggered by",
            "select",
            base.linked_to or None,
            options=linked_options,
            allow_blank=True,
            placeholder="(choose the effect)",
            show_if=lambda values: bool(values.get("linked_trigger")),
        ),
        DialogField(
            "trigger",
            "Trigger",
            "text",
            base.trigger,
            placeholder="the word, gesture or condition",
        ),
    ]
    if invested:
        fields += [
            DialogField(
                "expiry",
                "Effect Expiry",
                "select",
                base.expiry,
                options=_pairs(EFFECT_EXPIRIES),
            ),
            DialogField(
                "first_use_year",
                "Year of first use",
                "optint",
                base.first_use_year,
                show_if=lambda values: values.get("expiry") not in (None, "None"),
            ),
        ]
    fields.append(
        check(
            "known", "Known", hint="Untick for a power not yet found by Investigation."
        )
    )
    if invested:
        fields.append(
            DialogField(
                "instilling_progress",
                "Instilling (blank = finished)",
                "optint",
                base.instilling_progress,
            )
        )
    fields.append(
        DialogField(
            "modified_level_override",
            "Modified level (blank = auto)",
            "optint",
            base.modified_level_override,
        )
    )
    if device.type != CHARGED:
        fields.append(
            DialogField(
                "vis_override",
                "Vis (blank = worked out)",
                "optint",
                base.vis_override,
            )
        )
    fields.append(_description_field(base.description))
    return FieldsDialog(
        f"Instill an Effect in {escape(device.name)}"
        if effect is None
        else f"Edit an Effect of {escape(device.name)}",
        fields,
        validate=_effect_problem,
        live=lambda values: _effect_live(device, base, values),
        save_label="Add" if effect is None else "Save",
        build=lambda values: _effect_from_values(base, values),
    )
