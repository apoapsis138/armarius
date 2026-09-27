"""Form builders for the records (DialogField lists for FieldsDialog) and the
bespoke forms that aren't FieldsDialogs: Arts, Spell Mastery, Binding & Cords,
Improve Income and the import screens."""

from __future__ import annotations

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
from .. import catalog
from .. import economics as eco
from .. import familiars as fam
from .. import inhabitants as inh
from .. import possessions as pos
from .. import spells as spl
from ..arts import ART_ABBREVIATIONS, ARTS, FORMS, TECHNIQUES
from ..markup import escape
from ..models import (
    BOOK_TYPES,
    CORD_SCORE_COSTS,
    COVENANT_ROLES,
    CRAFT_FIELDS,
    FATIGUE_LEVELS,
    GEAR_QUALITIES,
    GEAR_QUALITY_DEFAULT,
    GEAR_TYPES_BY_KIND,
    GIFT_CHOICES,
    INCOME_EFFECTS,
    LAB_CHARACTERISTICS,
    OTHER_COVENFOLK_ROLES,
    SANCTUM_USAGE_DEFAULT,
    SANCTUM_USAGES,
    SEASONS,
    SPELL_DURATIONS,
    SPELL_RANGES,
    SPELL_TARGETS,
    TRACTATUS_SUBJECTS,
    Aging,
    ArtScore,
    Background,
    BondPower,
    Book,
    Character,
    Characteristics,
    Covenant,
    Description,
    Familiar,
    HermeticBackground,
    IncomeSource,
    KnownSpell,
    LabCharacteristics,
    Laboratory,
    MasteryAbility,
    Saga,
    Spell,
    Wounds,
)
from .fields import (
    _EMPHASIS_HINT,
    DialogField,
    ModalDialog,
    _attr,
    _covenant_options,
    _description_field,
    _pairs,
    _year_born_field,
)
from .pickers import SpellChooserScreen
from .prompts import ConfirmScreen, _mastery_ability_dialog


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


def _possession_fields(
    kind: str, entry: pos.PossessionEntry | None
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
        fields += _quantity_possession_fields(kind, entry)
    elif kind in ("vis_source", "vis_store"):
        fields += _vis_possession_fields(kind, entry)

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


def _quantity_possession_fields(
    kind: str, entry: pos.PossessionEntry | None
) -> list[DialogField]:
    """Type and Quality (gear kinds), Quantity, and a weapon's combat
    statistics."""
    fields: list[DialogField] = []
    if kind in GEAR_TYPES_BY_KIND:
        types = GEAR_TYPES_BY_KIND[kind]
        fields += [
            DialogField(
                "gear_type",
                "Type",
                "select",
                _attr(entry, "gear_type", types[0]) or types[0],
                options=_pairs(types),
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
                "weapon_attack", "Attack", "int", _attr(entry, "weapon_attack", 0)
            ),
            DialogField(
                "weapon_defense", "Defense", "int", _attr(entry, "weapon_defense", 0)
            ),
            DialogField(
                "weapon_damage", "Damage", "int", _attr(entry, "weapon_damage", 0)
            ),
        ]
    return fields


def _vis_possession_fields(
    kind: str, entry: pos.PossessionEntry | None
) -> list[DialogField]:
    """Art, Season harvested (a source), Pawns, Location and Physical Form."""
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
    fields += [
        DialogField("pawns", "Pawns", "int", _attr(entry, "pawns", 1) or 1),
        DialogField("location", "Location", "text", _attr(entry, "location", "")),
        DialogField(
            "physical_form",
            "Physical Form",
            "text",
            _attr(entry, "physical_form", ""),
        ),
    ]
    return fields


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
    return fields


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
    ]


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


def _characteristics_from(values: dict[str, Any]) -> Characteristics:
    return Characteristics(
        **{attribute: values[attribute] for _, attribute in _CHARACTERISTIC_FIELDS}
    )


def _character_info_fields(saga: Saga, character: Character) -> list[DialogField]:
    """The top panel's Edit form: name, covenant, a magus's laboratory, and
    the Background figures shown there."""
    b = character.background
    fields = [
        DialogField("name", "Name", "text", character.name, required=True),
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
        DialogField("size", "Size", "int", b.size),
    ]


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
    ]


def _wounds_fields(wounds: Wounds, *, soak: bool = True) -> list[DialogField]:
    """Wound counts and Incapacitated/Dead; a character's Soak too (a
    Familiar's lives with its Characteristics instead)."""
    fields = [DialogField("soak", "Soak", "int", wounds.soak)] if soak else []
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
        DialogField("wizards_sigil", "Wizard's Sigil", "text", h.wizards_sigil),
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
        DialogField("build_points", "Points (Build Points)", "int", lab.build_points),
        DialogField("aura_modifier", "Aura modifier", "int", lab.aura_modifier),
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
            options=[
                (escape(c.name), c.id) for c in saga.characters if c.type == "magus"
            ],
            allow_blank=True,
            placeholder="(unassigned)",
        ),
    ]


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
    saga: Saga, book: Book | None, default_owner: str
) -> list[DialogField]:
    """The add/edit form for a book. Which of Art/Ability/Spell, Level and
    Quality are shown follows the Type (and a Tractatus's Subject) live."""

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

    def needs_level(values: dict[str, Any]) -> bool:
        kind = book_type(values)
        if kind not in bk.SPELL_TYPES:
            return bk.has_level(kind)
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
            _attr(book, "type", ""),
            options=_pairs(BOOK_TYPES),
            required=True,
            allow_blank=True,
            placeholder="(choose a Type)",
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
            show_if=lambda v: book_type(v) in bk.SPELL_TYPES,
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
        DialogField("language", "Language", "text", _attr(book, "language", "Latin")),
        DialogField("author", "Author", "text", _attr(book, "author", "")),
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
    book.spell_id = values.get("spell_id") if book.type in bk.SPELL_TYPES else None
    if book.type not in bk.SPELL_TYPES:
        book.spell_name = ""
    book.level = values.get("level")
    spell = spl.find_spell(saga, book.spell_id)
    if spell is not None:
        # A copy for display without the saga; level_of() reads the spell.
        book.spell_name = spell.name
        if spell.level is not None:
            book.level = spell.level
    book.quality = values.get("quality")


def _book_live(values: dict[str, Any], saga: Saga) -> str:
    """The form's live line: the Build Point cost (a Lab Text's or Casting
    Tablet's from its spell's level) and any covenant-creation limit the
    values go over (a warning, not an error)."""
    if not values.get("type"):
        return "[dim]Cost: choose a Type.[/]"
    probe = Book(id="", name="", type=values["type"])
    probe.level = values.get("level") if bk.has_level(probe.type) else None
    probe.quality = values.get("quality") if bk.has_quality(probe.type) else None
    probe.spell_id = values.get("spell_id") if probe.type in bk.SPELL_TYPES else None
    lines = [f"[b]Cost:[/] {bk.cost(probe, saga)} Build Points"]
    spell = spl.find_spell(saga, probe.spell_id)
    if spell is not None and spell.level is not None:
        lines[0] += f"  [dim](Level {spell.level}, from the spell)[/]"
    lines += [f"[red]{escape(w)}[/]" for w in bk.limit_warnings(probe)]
    return "\n".join(lines)


#: The choice in a Range/Duration/Target select that opens a free-text box.
_OTHER = "__other__"


def _rdt_field(
    key: str, label: str, standard: tuple[str, ...], value: str
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
        *_rdt_field("range", "Range", SPELL_RANGES, _attr(spell, "range", "")),
        *_rdt_field(
            "duration", "Duration", SPELL_DURATIONS, _attr(spell, "duration", "")
        ),
        *_rdt_field("target", "Target", SPELL_TARGETS, _attr(spell, "target", "")),
        DialogField("ritual", "Ritual", "check", _attr(spell, "ritual", False)),
        DialogField(
            "base_level", "Base level", "optint", _attr(spell, "base_level", None)
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
        width: 14;
        content-align: right middle;
        padding-right: 1;
    }

    .art-row .art-sep {
        width: 1;
        content-align: center middle;
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
                value=str(score.level),
                type="integer",
                id=f"input-art-{key}-level",
                compact=True,
            )
            yield Label("/", classes="art-sep")
            yield Input(
                value=str(score.xp),
                type="integer",
                id=f"input-art-{key}-xp",
                compact=True,
            )

        with Vertical(id="arts-dialog"):
            yield Label("Edit Arts", id="arts-title")
            yield Label("Each score is Level / XP", id="arts-subtitle")
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

    def _try_save(self) -> None:
        error = self.query_one("#arts-error", Static)
        result: dict[str, ArtScore] = {}
        for art_name in ARTS:
            key = art_name.lower()
            level_raw = self.query_one(f"#input-art-{key}-level", Input).value.strip()
            xp_raw = self.query_one(f"#input-art-{key}-xp", Input).value.strip()
            try:
                level = int(level_raw)
                xp = int(xp_raw)
            except ValueError:
                error.update(f"{art_name} needs whole numbers for Level and XP.")
                return
            result[key] = ArtScore(level=level, xp=xp)
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
    ("characters", "Characters", False),
    ("covenants", "Covenants", False),
    ("laboratories", "Laboratories", False),
    ("books", "Books", True),
    ("spells", "Spells", True),
)


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
        options.highlighted = next(i for i, k in enumerate(IMPORT_KINDS) if k[2])
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
            status.update(f"[red]Couldn't save the example: {escape(str(problem))}[/]")
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
